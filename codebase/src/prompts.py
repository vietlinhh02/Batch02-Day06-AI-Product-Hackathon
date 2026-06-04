"""
Prompts for Discord Class Bot - Personal queries, RAG, and unrelated detection
"""

SYSTEM_PROMPT = """Bạn là ClassBot - trợ lý AI trong server Discord.

VAI TRÒ: Giúp mọi người tìm lại thông tin đã thảo luận trong chat.

CÁCH TRẢ LỜI:
1. Đọc TẤT CẢ tin nhắn được cung cấp trong context
2. Trả lời ngắn gọn, đúng trọng tâm, bằng tiếng Việt
3. LUÔN LUÔN kèm link tin nhắn gốc (📎) khi trích dẫn thông tin
4. KHÔNG bịa thêm thông tin ngoài context
5. Nếu không có đủ thông tin để trả lời → nói rõ điều đó
6. Nếu tin nhắn ở kênh khác, ghi rõ tên kênh (ví dụ: "trong #announcements, ...")

FORMAT TRẢ LỜI:
- Câu trả lời chính
- 📎 Nguồn: link1, link2, ..."""

PERSONAL_SYSTEM_PROMPT = """Bạn là ClassBot - trợ lý AI trong server Discord.

NHIỆM VỤ: Người dùng muốn biết họ (hoặc ai đó) đã chat những gì. Bạn được cung cấp danh sách tin nhắn của người đó.

QUAN TRỌNG - MỖI TIN NHẮN ĐỀU CÓ LINK:
Trong context, mỗi tin nhắn đều có dòng "📎 Link: <url>". BẮT BUỘC phải kèm link này khi nhắc đến tin nhắn đó.

CÁCH TRẢ LỜI:
1. Liệt kê TỪNG tin nhắn theo thứ tự thời gian (cũ nhất → mới nhất)
2. Mỗi tin nhắn viết dưới dạng: [thời gian] tóm tắt nội dung → link
3. Nếu người dùng yêu cầu tóm tắt, hãy gộp các tin nhắn cùng chủ đề
4. Trả lời bằng tiếng Việt, thân thiện
5. KHÔNG bỏ sót link nào đã được cung cấp

FORMAT:
**Tin nhắn của [tên]:**
- [HH:MM DD/MM] Nội dung tóm tắt → [link]
- [HH:MM DD/MM] Nội dung tóm tắt → [link]
..."""

UNRELATED_RESPONSE = "Không tìm thấy thông tin trong lịch sử chat. Gợi ý: `@ClassBot thử tìm <từ khoá>` để mình tìm lại nhé."

NO_PERSONAL_RESPONSE = "Không tìm thấy tin nhắn nào của bạn trong lịch sử chat. Hãy chat thêm để mình ghi nhớ nhé!"

NO_CONTEXT_RESPONSE = "Không tìm thấy thông tin liên quan trong lịch sử chat."

IDENTITY_SYSTEM_PROMPT = """Bạn là ClassBot - trợ lý AI trong server Discord.

NHIỆM VỤ: Người dùng muốn biết một người trong server là ai. Bạn được cung cấp các tin nhắn của người đó.

CÁCH TRẢ LỜI - BẮT BUỘC LÀM THEO:
1. Dòng đầu: "**[Tên]** là người dùng trong kênh chat. 3 tin nhắn gần nhất:"
2. Liệt kê CHÍNH XÁC từng tin nhắn được cung cấp, theo thứ tự thời gian, mỗi tin một dòng
3. Mỗi dòng phải có: thời gian + NGUYÊN VĂN tóm gọn nội dung + LINK GỐC
4. KHÔNG được tóm tắt chung, KHÔNG được gộp nhiều tin nhắn thành một
5. Nếu có ít hơn 3 tin nhắn thì liệt kê hết những gì có

FORMAT MẪU (cứng):
**[Duy]** là người dùng trong kênh chat. 3 tin nhắn gần nhất:
- [14:20 04/06] "cho em hỏi bài tập..." → https://discord.com/channels/...
- [14:15 04/06] "có ai biết deadline..." → https://discord.com/channels/...
- [14:10 04/06] "em cảm ơn ạ" → https://discord.com/channels/..."""


def build_context_prompt(question: str, context_chunks: list, scores: list, user_id: str = None, current_channel: str = "") -> str:
    """Build prompt with RAG context and message links."""
    if not context_chunks:
        return ""

    sorted_chunks = sorted(context_chunks, key=lambda x: x.get('timestamp', ''))

    context_parts = []
    has_other_channels = False
    for chunk in sorted_chunks:
        link = chunk.get('message_link', '')
        user_name = chunk.get('author', 'Unknown')
        channel = chunk.get('channel', '')
        timestamp = chunk.get('timestamp', '')[:16].replace('T', ' ')

        citation = f"{user_name} ({timestamp})"
        if channel:
            citation += f" trong #{channel}"
            if current_channel and channel != current_channel:
                has_other_channels = True
        if link:
            citation += f" → {link}"

        context_parts.append(f"{chunk['content']}\n📎 Tin nhắn: {citation}")

    context = "\n\n---\n\n".join(context_parts)

    channel_note = ""
    if has_other_channels:
        channel_note = "\n(Lưu ý: một số tin nhắn ở kênh khác, hãy ghi rõ tên kênh khi trả lời.)"

    return f"""=== TIN NHẮN LIÊN QUAN ===
{context}
=== HẾT ===
{channel_note}
Câu hỏi: "{question}"

Hãy trả lời dựa trên các tin nhắn trên. Nhớ kèm link nguồn (📎) cho mỗi thông tin trích dẫn.
Nếu có tin nhắn từ kênh khác, hãy ghi rõ tên kênh (ví dụ: "trong #general, ...")."""


def build_personal_context_prompt(question: str, user_messages: list, user_name: str) -> str:
    """Build prompt for personal queries with user's own messages."""
    if not user_messages:
        return ""

    sorted_msgs = sorted(user_messages, key=lambda x: x.get('timestamp', ''))

    context_parts = []
    for msg in sorted_msgs:
        link = msg.get('message_link', '')
        channel = msg.get('channel', '')
        timestamp = msg.get('timestamp', '')[:16].replace('T', ' ')
        content = msg.get('content', '')

        line = f"[{timestamp}] #{channel}: {content}"
        if link:
            line += f"\n🔗 LINK GỐC: {link}"

        context_parts.append(line)

    context = "\n\n---\n\n".join(context_parts)

    return f"""=== {len(sorted_msgs)} TIN NHẮN CỦA {user_name} (có link gốc + tên kênh) ===
{context}
=== HẾT ({len(sorted_msgs)} tin) ===

{user_name} hỏi: "{question}"

QUAN TRỌNG: Liệt kê CHÍNH XÁC {len(sorted_msgs)} tin nhắn ở trên. Mỗi tin một dòng, kèm LINK GỐC.
Định dạng mỗi dòng: - [HH:MM DD/MM] #{kênh}: nội dung → LINK"""


def _is_personal_query(question: str) -> bool:
    """Check if question is asking about someone's messages (self or others)."""
    action_patterns = [
        'vừa chat', 'vừa nói', 'vừa làm', 'vừa hỏi', 'vừa nhắn',
        'đã chat', 'đã nói', 'đã làm', 'đã hỏi', 'đã nhắn',
        'chat gì', 'nói gì', 'làm gì', 'hỏi gì', 'nhắn gì',
        'chat những gì', 'nói những gì', 'làm những gì',
    ]
    question_lower = question.lower()
    if any(kw in question_lower for kw in action_patterns):
        return True

    # "bạn biết tôi/duy là ai không"
    if 'là ai' in question_lower or 'ai là' in question_lower:
        if not _is_bot_question(question):
            return True

    # "tóm tắt/liệt kê tin nhắn của tôi/mình/..." or "@name"
    summary_patterns = ['tin nhắn', 'message', 'tóm tắt', 'liệt kê', 'tổng hợp', 'tổng kết', 'kể lại']
    if any(kw in question_lower for kw in summary_patterns):
        if _is_self_reference(question):
            return True
        # Check for any person reference (name or @mention)
        if 'của ' in question_lower or '@' in question:
            return True
        # Check for third person: "tóm tắt những gì Linh đã nói" etc.
        if any(kw in question_lower for kw in action_patterns):
            return True

    return False


def _is_self_reference(question: str) -> bool:
    """Check if question is about the asker themselves."""
    self_keywords = ['tôi', 'mình', 'tớ', 'em', 'tui', 'ta']
    question_lower = question.lower()
    words = question_lower.split()
    for kw in self_keywords:
        if kw in words:
            return True
        # Also check as part of "của tôi", "cho tôi", etc.
        if f'của {kw}' in question_lower or f'cho {kw}' in question_lower:
            return True
    return False


def _is_bot_question(question: str) -> bool:
    """Check if question is about the bot itself or its capabilities."""
    bot_keywords = [
        'bạn có thể', 'mày có thể', 'bot có thể', 'có thể đọc',
        'bạn làm được', 'mày làm được',
        'chức năng', 'tính năng',
        'bạn là ai', 'mày là ai', 'ai là',
        'cách dùng', 'hướng dẫn', 'cách sử dụng', 'làm sao để dùng',
        'giúp', 'giúp đỡ',
        'có thể xem', 'có thể lấy', 'có thể truy cập',
        'đọc được kênh', 'xem được kênh', 'kênh khác', 'server khác',
        'hoạt động như thế nào', 'làm gì được', 'làm được gì',
    ]
    question_lower = question.lower()
    return any(kw in question_lower for kw in bot_keywords)


def build_correction_prompt(user_message: str, original_answer: str) -> dict:
    return {
        "is_correction": True,
        "user_message": user_message,
        "original_answer": original_answer,
        "response": "Đã ghi nhận. Cảm ơn bạn!"
    }


CONFIDENCE_THRESHOLDS = {
    "high": 0.5,
    "medium": 0.35,
    "low": 0.25,
    "none": 0.0
}

RESPONSE_TEMPLATES = {
    "happy": {"prefix": "", "suffix": ""},
    "low_confidence": {"prefix": "", "suffix": ""},
    "failure": {"prefix": "", "suffix": ""},
    "correction": {"prefix": "", "suffix": ""}
}
