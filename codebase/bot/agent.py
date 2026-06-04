from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from bot.config import Settings
from bot.corrections import Correction, CorrectionStore
from bot.llm import call_llm
from bot.rag import RAGStore

log = logging.getLogger(__name__)


# ── tool definitions (OpenAI function-calling schema) ───────────────────────

TOOL_SEARCH_HISTORY = {
    "type": "function",
    "function": {
        "name": "search_history",
        "description": (
            "Tìm kiếm trong lịch sử chat của kênh Discord lớp học. "
            "Dùng khi cần tìm thông tin về bài tập, deadline, nội dung bài giảng, "
            "hoặc bất kỳ chủ đề nào đã được thảo luận."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Câu truy vấn tìm kiếm (tiếng Việt hoặc tiếng Anh)",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Số lượng kết quả tối đa (mặc định 5)",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
}

TOOL_SUMMARIZE_TOPIC = {
    "type": "function",
    "function": {
        "name": "summarize_topic",
        "description": (
            "Lấy nhiều context chunks về một chủ đề để tổng hợp/tóm tắt. "
            "Dùng khi user yêu cầu tóm tắt nội dung buổi học hoặc một chủ đề cụ thể."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Chủ đề cần tóm tắt",
                },
                "num_chunks": {
                    "type": "integer",
                    "description": "Số chunks cần lấy (mặc định 15)",
                    "default": 15,
                },
            },
            "required": ["topic"],
        },
    },
}

TOOL_GET_MESSAGE_CONTEXT = {
    "type": "function",
    "function": {
        "name": "get_message_context",
        "description": (
            "Lấy các tin nhắn xung quanh một message cụ thể (trước và sau). "
            "Dùng khi cần hiểu rõ context của một tin nhắn được trích dẫn."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "ID của tin nhắn cần xem context",
                },
                "window": {
                    "type": "integer",
                    "description": "Số tin nhắn trước/sau (mặc định 3)",
                    "default": 3,
                },
            },
            "required": ["message_id"],
        },
    },
}

TOOL_SUBMIT_CORRECTION = {
    "type": "function",
    "function": {
        "name": "submit_correction",
        "description": (
            "Ghi nhận một sửa lỗi từ người dùng. "
            "Dùng khi user chỉ ra rằng thông tin trước đó sai."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "original_claim": {
                    "type": "string",
                    "description": "Thông tin sai ban đầu",
                },
                "correct_info": {
                    "type": "string",
                    "description": "Thông tin đúng",
                },
            },
            "required": ["original_claim", "correct_info"],
        },
    },
}

ALL_TOOLS = [
    TOOL_SEARCH_HISTORY,
    TOOL_SUMMARIZE_TOPIC,
    TOOL_GET_MESSAGE_CONTEXT,
    TOOL_SUBMIT_CORRECTION,
]


# ── system prompt ──────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
Bạn là trợ lý AI cho lớp học Discord. Bạn tìm kiếm lịch sử chat để trả lời, KHÔNG dùng kiến thức riêng.

Quy tắc:
1. LUÔN gọi `search_history` trước khi trả lời.
2. Phân biệt nguồn: giảng viên (is_instructor=true) → tin cậy cao; học viên → cần kiểm chứng.
3. Khi trích dẫn: [text](https://discord.com/channels/{guild_id}/{channel_id}/{message_id})
4. Không tìm thấy → nói rõ & gợi ý hỏi giảng viên. Mâu thuẫn → chỉ ra cả 2 nguồn.
5. Trả lời ngắn gọn, tiếng Việt. KHÔNG bịa thông tin.
6. Kết thúc: "🔬 Cao" / "🧐 Trung bình" / "🌫️ Thấp" (theo mức tin cậy).
"""


# ── agent response ─────────────────────────────────────────────────────────


@dataclass
class AgentResponse:
    answer: str
    confidence: str  # "high" | "medium" | "low"
    sources: list[dict] = field(default_factory=list)
    correction_submitted: bool = False


# ── agent loop ─────────────────────────────────────────────────────────────


async def run_agent(
    settings: Settings,
    question: str,
    rag: RAGStore,
    corrections: CorrectionStore,
    guild_id: str,
    corrected_by: str = "",
) -> AgentResponse:
    """Run the tool-calling agent loop and return the final response."""

    system = _SYSTEM_PROMPT.replace("{guild_id}", guild_id or "0")

    # Inject known corrections into system prompt
    correction_block = corrections.to_prompt_block(question)
    if correction_block:
        system += "\n\n" + correction_block

    messages: list[dict] = [
        {"role": "system", "content": system},
        {"role": "user", "content": question},
    ]

    collected_sources: list[dict] = []
    seen_source_ids: set[str] = set()
    correction_submitted = False

    for step in range(settings.agent_max_steps):
        log.debug("Agent step %d/%d", step + 1, settings.agent_max_steps)

        try:
            msg = await call_llm(settings, messages, tools=ALL_TOOLS)
        except Exception:
            log.exception("LLM call failed at step %d", step + 1)
            return AgentResponse(
                answer="Xin lỗi, AI đang gặp lỗi kết nối. Vui lòng thử lại sau.",
                confidence="low",
            )

        finish_reason = "stop"
        # Determine finish reason from the message structure
        tool_calls = msg.get("tool_calls")
        if tool_calls:
            finish_reason = "tool_calls"

        if finish_reason != "tool_calls" or not tool_calls:
            # Final answer
            content = msg.get("content", "")
            if not content:
                content = (
                    "Xin lỗi, mình chưa tìm thấy thông tin phù hợp trong lịch sử chat để trả lời câu hỏi này. "
                    "Bạn thử hỏi cụ thể hơn nhé!"
                )
            return AgentResponse(
                answer=content,
                confidence=_infer_confidence(content),
                sources=collected_sources,
                correction_submitted=correction_submitted,
            )

        # Append assistant message with tool_calls
        messages.append(msg)

        # Execute each tool call
        for tc in tool_calls:
            fn_name = tc["function"]["name"]
            try:
                fn_args = json.loads(tc["function"]["arguments"])
            except json.JSONDecodeError:
                fn_args = {}

            result = await _execute_tool(
                fn_name, fn_args, rag, corrections,
                guild_id, corrected_by,
            )

            if fn_name == "submit_correction":
                correction_submitted = True

            # Collect sources from search results (dedup by link)
            if fn_name in ("search_history", "summarize_topic"):
                if isinstance(result, dict) and "results" in result:
                    for r in result["results"]:
                        link = r.get("link", "")
                        if link and link not in seen_source_ids:
                            seen_source_ids.add(link)
                            collected_sources.append(r)

            # Append tool result
            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": json.dumps(result, ensure_ascii=False),
            })

    # Max steps reached — force a final answer
    messages.append({
        "role": "user",
        "content": "Hãy đưa ra câu trả lời cuối cùng dựa trên thông tin đã thu thập.",
    })
    try:
        msg = await call_llm(settings, messages)
        content = msg.get("content", "")
    except Exception:
        content = ""

    if not content:
        content = (
            "Xin lỗi, mình chưa tìm thấy thông tin phù hợp trong lịch sử chat để trả lời câu hỏi này. "
            "Bạn thử hỏi cụ thể hơn nhé!"
        )

    return AgentResponse(
        answer=content,
        confidence="low",
        sources=collected_sources,
        correction_submitted=correction_submitted,
    )


# ── tool execution ────────────────────────────────────────────────────────


async def _execute_tool(
    name: str,
    args: dict,
    rag: RAGStore,
    corrections: CorrectionStore,
    guild_id: str,
    corrected_by: str,
) -> dict:
    """Execute a single tool and return its result."""

    if name == "search_history":
        query = args.get("query", "")
        top_k = args.get("top_k", 5)
        results = rag.search(query, top_k=top_k, threshold=0.0)
        return {
            "results": _format_search_results(results, guild_id),
            "count": len(results),
        }

    if name == "summarize_topic":
        topic = args.get("topic", "")
        num_chunks = args.get("num_chunks", 15)
        results = rag.search(topic, top_k=num_chunks, threshold=0.0)
        return {
            "results": _format_search_results(results, guild_id),
            "count": len(results),
        }

    if name == "get_message_context":
        message_id = args.get("message_id", "")
        window = args.get("window", 3)
        context = rag.get_context_around(message_id, window=window)
        return {
            "context": context,
            "found": len(context) > 0,
        }

    if name == "submit_correction":
        original = args.get("original_claim", "")
        correct = args.get("correct_info", "")
        correction = Correction(
            original_claim=original,
            correct_info=correct,
            corrected_by=corrected_by or "unknown",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        corrections.add(correction)
        return {
            "status": "ok",
            "message": f"Đã ghi nhận sửa lỗi: '{original}' → '{correct}'",
        }

    return {"error": f"Unknown tool: {name}"}


def _format_search_results(results: list[dict], guild_id: str) -> list[dict]:
    """Format search results for LLM consumption — truncated, minimal fields."""
    formatted = []
    for r in results:
        gid = r.get("guild_id") or guild_id or "0"
        link = f"https://discord.com/channels/{gid}/{r['channel_id']}/{r['message_id']}"
        content = r.get("content", "")
        # Truncate content — LLM only needs the gist, not full 1500-char chunks
        if len(content) > 400:
            content = content[:400] + "…"
        formatted.append({
            "content": content,
            "author": r["author"],
            "is_instructor": r.get("is_instructor", False),
            "link": link,
            "timestamp": r.get("timestamp", "")[:19],
            "score": round(r.get("score", 0), 3),
        })
    return formatted


def _infer_confidence(text: str) -> str:
    """Infer confidence level from the answer text."""
    low_signals = ["không tìm thấy", "không rõ", "cần được kiểm chứng", "thấp", "🌫️"]
    mid_signals = ["trung bình", "có thể", "một học viên", "🧐"]
    high_signals = ["giảng viên", "chắc chắn", "cao", "🔬"]

    text_lower = text.lower()
    if any(s in text_lower for s in low_signals):
        return "low"
    if any(s in text_lower for s in high_signals):
        return "high"
    if any(s in text_lower for s in mid_signals):
        return "medium"
    return "medium"
