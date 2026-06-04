"""
Discord Bot for Class Bot RAG System
Handles Discord events and integrates with RAG pipeline
"""
import asyncio
import logging
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import discord
from discord.ext import commands

from config import (
    DISCORD_TOKEN, DISCORD_BOT_PREFIX,
    OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL,
    ALLOWED_CHANNELS, RATE_LIMIT_PER_USER, RATE_LIMIT_WINDOW,
    MAX_RESPONSE_TOKENS, TEMPERATURE, BOT_LANGUAGE
)
from rag_pipeline import RAGPipeline
from prompts import (
    SYSTEM_PROMPT, PERSONAL_SYSTEM_PROMPT, IDENTITY_SYSTEM_PROMPT,
    build_context_prompt, build_personal_context_prompt,
    build_correction_prompt,
    UNRELATED_RESPONSE, NO_PERSONAL_RESPONSE, NO_CONTEXT_RESPONSE,
    _is_personal_query, _is_self_reference, _is_bot_question,
    CONFIDENCE_THRESHOLDS, RESPONSE_TEMPLATES
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ClassBot(commands.Bot):
    """Discord bot with RAG capabilities."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=DISCORD_BOT_PREFIX,
            intents=intents,
            help_command=commands.DefaultHelpCommand()
        )

        self.rag_pipeline = RAGPipeline()
        self.openai_client = None
        self.rate_limits = {}
        self.conversation_state = {}  # {user_id: {target_user_id, target_name, loaded_count, limit}}

        self._load_openai()

    def _load_openai(self):
        """Load OpenAI client via OpenRouter."""
        try:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
            logger.info("OpenRouter client loaded")
        except Exception as e:
            logger.error(f"Failed to load OpenRouter: {e}")

    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        logger.info('Đang tải lịch sử chat...')

        for guild in self.guilds:
            total = 0
            for channel in guild.text_channels:
                try:
                    n = await self._ingest_channel_history(channel, limit=None)
                    total += n
                    logger.info(f'  #{channel.name}: {n} chunks')
                except Exception as e:
                    logger.warning(f'  #{channel.name}: skip ({e})')
            logger.info(f'Tải xong {total} tin nhắn từ {guild.name}')

        logger.info('Bot sẵn sàng!')

    async def on_message(self, message: discord.Message):
        """Handle incoming messages."""
        if message.author == self.user:
            return

        if message.content.startswith(DISCORD_BOT_PREFIX):
            await self.process_commands(message)
            return

        if self.user in message.mentions:
            await self.handle_question(message)
            return

        await self.process_commands(message)

        # Only store normal chat messages (not commands, not @mentions to bot)
        await self._store_message(message)

    async def _store_message(self, message: discord.Message):
        """Store a single message to vector store in real-time."""
        try:
            if not message.content or message.author.bot:
                return
            if message.content.startswith(DISCORD_BOT_PREFIX):
                return
            if self.user in message.mentions:
                return

            msg_data = {
                "id": str(message.id),
                "author": message.author.display_name,
                "user_id": str(message.author.id),
                "role": "member",
                "content": message.content,
                "timestamp": message.created_at.isoformat(),
                "channel": message.channel.name,
                "message_link": message.jump_url
            }

            from rag_pipeline import TextChunker, EmbeddingEngine
            chunker = TextChunker()
            embedder = EmbeddingEngine()

            chunks = chunker.chunk_message(msg_data)
            for chunk in chunks:
                embedding = embedder.embed_text(chunk["content"])
                self.rag_pipeline.vector_store.add_documents([chunk], [embedding])

        except Exception as e:
            logger.error(f"Failed to store message: {e}")

    def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user is rate limited."""
        now = datetime.now().timestamp()

        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []

        self.rate_limits[user_id] = [
            ts for ts in self.rate_limits[user_id]
            if now - ts < RATE_LIMIT_WINDOW
        ]

        if len(self.rate_limits[user_id]) >= RATE_LIMIT_PER_USER:
            return False

        self.rate_limits[user_id].append(now)
        return True

    async def handle_question(self, message: discord.Message):
        """Route question to appropriate handler."""
        question = message.content
        for mention in message.mentions:
            question = question.replace(f'<@{mention.id}>', '').replace(f'<@!{mention.id}>', '')
        question = question.strip()

        if not question:
            await message.reply("Bạn muốn hỏi gì? Ví dụ: @ClassBot bài tập tuần này là gì?")
            return

        greetings = ['xin chào', 'hello', 'hi', 'chào', 'hey', 'yo', 'hola']
        if question.lower() in greetings:
            await self.send_greeting(message)
            return

        if question.lower() in ['help', 'giúp', 'hướng dẫn']:
            await self.send_help(message)
            return

        if question.lower() in ['status', 'trạng thái']:
            await self.send_status(message)
            return

        if _is_bot_question(question):
            await self.send_help(message)
            return

        if not self._check_rate_limit(str(message.author.id)):
            await message.reply("Bạn hỏi quá nhanh! Thử lại sau 30 giây nhé.")
            return

        if self._is_correction(question):
            await self.handle_correction(message, question)
            return

        if _is_personal_query(question):
            if _is_self_reference(question):
                target_user = message.author
            else:
                target_user = self._extract_mentioned_user(message)
                if target_user is None:
                    target_user = self._find_user_by_name(message.guild, question)
                if target_user is None:
                    await self.handle_rag_query(message, question, message.channel.name)
                    return
            await self.handle_personal_query(message, question, target_user)
            return

        if self._is_load_more(question):
            await self._handle_load_more(message)
            return

        if self._is_refinement_instruction(question):
            hint = self._extract_search_hint(question)
            if hint:
                await self.handle_rag_query(message, hint, message.channel.name)
                return

        await self.handle_rag_query(message, question, message.channel.name)

    async def handle_personal_query(self, message: discord.Message, question: str, target_user: discord.Member = None):
        """Handle personal queries about user's own messages or another user."""
        if target_user is None:
            target_user = message.author

        user_id = str(target_user.id)
        user_name = target_user.display_name

        is_identity = 'là ai' in question.lower() or 'ai là' in question.lower()
        limit = 3 if is_identity else 30
        system_prompt = IDENTITY_SYSTEM_PROMPT if is_identity else PERSONAL_SYSTEM_PROMPT

        user_messages = self.rag_pipeline.query_user_messages(user_id, limit=limit)

        if not user_messages:
            await message.reply(NO_PERSONAL_RESPONSE)
            return

        context_prompt = build_personal_context_prompt(question, user_messages, user_name)
        if not context_prompt:
            await message.reply(NO_PERSONAL_RESPONSE)
            return

        async with message.channel.typing():
            try:
                response = self.openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": context_prompt}
                    ],
                    temperature=TEMPERATURE,
                    max_tokens=MAX_RESPONSE_TOKENS
                )
                answer = response.choices[0].message.content
                await message.reply(answer)
            except Exception as e:
                logger.error(f"LLM error on personal query: {e}")
                fallback = self._build_personal_fallback(user_messages, user_name)
                await message.reply(fallback)

    async def handle_rag_query(self, message: discord.Message, question: str, current_channel: str = ""):
        """Handle general questions using RAG."""
        async with message.channel.typing():
            try:
                result = self.rag_pipeline.query(question)

                if result["type"] == "failure" or not result["documents"]:
                    if _is_bot_question(question):
                        await self.send_help(message)
                    else:
                        await message.reply(UNRELATED_RESPONSE)
                    return

                # Show current channel only if it has strong matches, else all channels
                docs = self._filter_by_channel(result["documents"], result["scores"], current_channel)

                context_prompt = build_context_prompt(
                    question, docs, result["scores"],
                    str(message.author.id), current_channel
                )

                if not context_prompt:
                    await message.reply(UNRELATED_RESPONSE)
                    return

                response = self.openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": context_prompt}
                    ],
                    temperature=TEMPERATURE,
                    max_tokens=MAX_RESPONSE_TOKENS
                )
                answer = response.choices[0].message.content
                await message.reply(answer)

            except Exception as e:
                logger.error(f"Error processing RAG query: {e}")
                await message.reply("Có lỗi xảy ra khi xử lý câu hỏi. Vui lòng thử lại.")

    def _is_correction(self, text: str) -> bool:
        """Check if message is a correction."""
        correction_keywords = [
            'sai', 'không đúng', 'nhầm', 'correction',
            'thực ra', 'thật ra', 'chỉnh sửa'
        ]
        return any(keyword in text.lower() for keyword in correction_keywords)

    def _is_load_more(self, question: str) -> bool:
        """Check if user wants to load more messages."""
        keywords = [
            'xem thêm', 'tìm thêm', 'thêm nữa', 'nữa đi', 'nữa nhé',
            'tiếp tục', 'tiếp đi', 'cho thêm', 'nữa', 'more',
            'xem tiếp', 'tìm tiếp',
        ]
        q = question.lower()
        return any(k in q for k in keywords)

    async def _handle_load_more(self, message: discord.Message):
        """Load more messages for the previous my_messages/user_messages query."""
        user_id = str(message.author.id)
        state = self.conversation_state.get(user_id)

        if not state:
            await message.reply("Bạn muốn xem tin nhắn của ai? Ví dụ: `!my_messages 10` hoặc `!user_messages @nguoi 10`")
            return

        target_user_id = state["target_user_id"]
        loaded = state["loaded_count"]

        custom_limit = self._extract_number(message.content)
        limit = custom_limit if custom_limit else state["limit"]

        messages = self.rag_pipeline.query_user_messages(target_user_id, limit, loaded)

        if not messages:
            await message.reply("Không còn tin nhắn nào nữa.")
            return

        target_name = state.get("target_name", "người dùng")
        response = self._format_messages_response(target_name, messages, loaded)
        await message.reply(response)

        self.conversation_state[user_id]["loaded_count"] = loaded + len(messages)

    def _format_messages_response(self, target_name: str, messages: list, offset: int = 0) -> str:
        """Format messages into a Discord response string."""
        response = f"**Tin nhắn của {target_name} (từ #{offset + 1}):**\n\n"
        for i, msg in enumerate(messages, 1):
            num = offset + i
            timestamp = (msg.get('timestamp', '')[:16] or '').replace('T', ' ')
            channel = msg.get('channel', '')
            response += f"{num}. [{timestamp}] #{channel}: {msg.get('content', '')[:100]}..."
            if msg.get('message_link'):
                response += f"\n   {msg['message_link']}"
            response += "\n"
        return response

    def _extract_number(self, text: str) -> int:
        """Extract the last number from a string. Returns 0 if no number found."""
        import re
        numbers = re.findall(r'\d+', text)
        return int(numbers[-1]) if numbers else 0

    def _filter_by_channel(self, documents: list, scores: list, current_channel: str) -> list:
        """Only show current channel if it has good matches, otherwise show all channels."""
        if not current_channel or not documents:
            return documents

        in_channel = [(d, s) for d, s in zip(documents, scores) if d.get('channel', '') == current_channel]

        # Only restrict to current channel if it has at least one solid match (>= 0.4)
        if in_channel and max(s for _, s in in_channel) >= 0.4:
            return [d for d, _ in in_channel]

        # Current channel has only weak/no matches → show all channels
        return documents

    def _is_refinement_instruction(self, question: str) -> bool:
        """Check if user is giving search instructions to the bot."""
        keywords = [
            'thử tìm', 'tìm lại', 'tìm thêm', 'tìm với',
            'search', 'tìm kiếm', 'xem lại', 'xem thêm',
            'kiểm tra', 'thử lại', 'tra cứu', 'thử hỏi',
        ]
        q = question.lower()
        return any(k in q for k in keywords)

    def _extract_search_hint(self, question: str) -> str:
        """Extract the actual search hint from an instruction message."""
        prefixes = [
            'thử tìm', 'tìm lại', 'tìm thêm', 'tìm với',
            'search', 'tìm kiếm', 'xem lại', 'xem thêm',
            'kiểm tra', 'thử lại', 'tra cứu', 'thử hỏi',
        ]
        hint = question
        for p in prefixes:
            idx = hint.lower().find(p)
            if idx >= 0:
                hint = hint[idx + len(p):].strip()
                break

        connectors = ['về', 'với', 'từ khoá', 'từ khóa', 'theo', 'bằng']
        for c in connectors:
            if hint.lower().startswith(c + ' '):
                hint = hint[len(c):].strip()
                break

        return hint.strip() if hint.strip() else question

    async def handle_correction(self, message: discord.Message, correction_text: str):
        """Handle user correction."""
        logger.info(f"Correction from {message.author}: {correction_text}")

        response = "Đã ghi nhận correction. Cảm ơn bạn!\n\n"
        response += f"Thông tin đã cập nhật:\n"
        response += f"- {correction_text}\n"
        response += f"- Người sửa: {message.author.display_name}\n"
        response += f"- Thời gian: {datetime.now().strftime('%H:%M')}"

        await message.reply(response)

    def _build_personal_fallback(self, user_messages: list, user_name: str) -> str:
        """Build fallback response for personal queries without LLM."""
        if not user_messages:
            return NO_PERSONAL_RESPONSE

        response = f"Tin nhắn gần đây của {user_name}:\n\n"
        for i, msg in enumerate(user_messages[:10], 1):
            content = msg.get('content', '')[:150]
            timestamp = (msg.get('timestamp', '')[:16] or '').replace('T', ' ')
            channel = msg.get('channel', '')
            link = msg.get('message_link', '')
            response += f"{i}. [{timestamp}] #{channel}: {content}"
            if link:
                response += f"\n   {link}"
            response += "\n\n"

        return response

    async def send_help(self, message: discord.Message):
        """Send help message."""
        help_text = (
            "**ClassBot - Hướng dẫn sử dụng**\n\n"
            "**Hỏi về nội dung đã chat:**\n"
            "`@ClassBot bài tập tuần này là gì?`\n"
            "`@ClassBot ai nói gì về CNN?`\n\n"
            "**Hỏi về bản thân:**\n"
            "`@ClassBot tôi vừa chat gì?`\n\n"
            "**Hỏi về người khác:**\n"
            "`@ClassBot @Linh vừa chat gì?`\n"
            "`@ClassBot Linh đã nói gì?`\n\n"
            "**Lệnh:**\n"
            "`!my_messages 10` - Xem tin nhắn của bạn\n"
            "`!user_messages @người 10` - Xem tin nhắn của người khác\n"
            "`@ClassBot xem thêm` - Tải thêm tin nhắn (sau khi dùng lệnh trên)\n\n"
            "*Bot tự động tải toàn bộ lịch sử chat khi khởi động và học từ tin nhắn mới.*"
        )
        await message.reply(help_text)

    async def send_greeting(self, message: discord.Message):
        """Send greeting response."""
        greetings = [
            f"Xin chào {message.author.display_name}! Mình là ClassBot. Bạn muốn hỏi gì về nội dung đã chat?",
            f"Chào {message.author.display_name}! Mình giúp bạn tìm lại thông tin trong chat. Thử hỏi: @ClassBot bài tập tuần này là gì?",
            f"Hey {message.author.display_name}! Hỏi mình bất cứ điều gì đã thảo luận trong server nhé!",
        ]
        await message.reply(random.choice(greetings))

    async def send_status(self, message: discord.Message):
        """Send bot status."""
        stats = self.rag_pipeline.get_stats()
        status_text = (
            f"**ClassBot Status**\n\n"
            f"**Vector Store:**\n"
            f"- Documents: {stats['vector_store']['total_documents']}\n"
            f"- Collection: {stats['vector_store']['collection_name']}\n\n"
            f"**Configuration:**\n"
            f"- Chunk size: {stats['config']['chunk_size']}\n"
            f"- Top-k: {stats['config']['top_k']}\n"
            f"- Threshold: {stats['config']['similarity_threshold']}\n\n"
            f"**LLM:** {OPENAI_MODEL} (via OpenRouter)\n"
            f"**Embedding:** openai/text-embedding-3-small (via OpenRouter)"
        )
        await message.reply(status_text)

    async def _ingest_channel_history(self, channel, limit=None) -> int:
        """Ingest message history from a Discord channel into vector store.
        limit=None means no limit - fetch all messages."""
        messages = []
        async for msg in channel.history(limit=limit):
            if msg.content and not msg.author.bot and self.user not in msg.mentions:
                messages.append({
                    "id": str(msg.id),
                    "author": msg.author.display_name,
                    "user_id": str(msg.author.id),
                    "role": "member",
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat(),
                    "channel": channel.name,
                    "message_link": msg.jump_url
                })

        if not messages:
            return 0

        from rag_pipeline import TextChunker, EmbeddingEngine
        chunker = TextChunker()
        embedder = EmbeddingEngine()
        chunks = chunker.chunk_messages(messages)
        texts = [c["content"] for c in chunks]
        embeddings = embedder.embed_batch(texts)
        self.rag_pipeline.vector_store.add_documents(chunks, embeddings)
        return len(chunks)

    def _extract_mentioned_user(self, message: discord.Message) -> Optional[discord.Member]:
        """Extract the first non-bot mentioned user from a message."""
        for mention in message.mentions:
            if mention.id != self.user.id:
                return mention
        return None

    def _find_user_by_name(self, guild: discord.Guild, question: str) -> Optional[discord.Member]:
        """Try to find a user in the guild by name from the question text."""
        if not guild:
            return None
        question_lower = question.lower()
        for member in guild.members:
            if not member.bot:
                display_name_lower = member.display_name.lower()
                name_lower = member.name.lower()
                if display_name_lower in question_lower or name_lower in question_lower:
                    return member
        return None

def main():
    """Run the bot."""
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not set!")
        print("Error: Please set DISCORD_TOKEN environment variable")
        print("Copy .env.example to .env and fill in your Discord bot token")
        sys.exit(1)

    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not set!")
        print("Error: Please set OPENAI_API_KEY environment variable (OpenRouter key)")
        print("Get your key from: https://openrouter.ai/keys")
        sys.exit(1)

    bot = ClassBot()

    @bot.command(name='my_messages')
    async def my_messages_command(ctx, limit: int = 10):
        """Show your recent messages in the store.
        Usage: !my_messages 10 | Then: @ClassBot xem thêm
        """
        user_id = str(ctx.author.id)
        messages = bot.rag_pipeline.query_user_messages(user_id, limit, 0)

        if not messages:
            await ctx.send("Không tìm thấy tin nhắn nào của bạn trong store.")
            return

        response = bot._format_messages_response(ctx.author.display_name, messages, 0)
        await ctx.send(response)

        # Save state for load more
        bot.conversation_state[user_id] = {
            "target_user_id": user_id,
            "target_name": ctx.author.display_name,
            "loaded_count": len(messages),
            "limit": limit,
        }

    @bot.command(name='user_messages')
    async def user_messages_command(ctx, user: discord.Member = None, limit: int = 10):
        """Show recent messages from a specific user.
        Usage: !user_messages @someone 10 | Then: @ClassBot xem thêm
        """
        if user is None:
            await ctx.send("Vui lòng tag người dùng. Ví dụ: `!user_messages @Linh 10`")
            return

        user_id = str(user.id)
        messages = bot.rag_pipeline.query_user_messages(user_id, limit, 0)

        if not messages:
            await ctx.send(f"Không tìm thấy tin nhắn nào của {user.display_name} trong store.")
            return

        response = bot._format_messages_response(user.display_name, messages, 0)
        await ctx.send(response)

        # Save state for load more (keyed by caller, not target)
        caller_id = str(ctx.author.id)
        bot.conversation_state[caller_id] = {
            "target_user_id": user_id,
            "target_name": user.display_name,
            "loaded_count": len(messages),
            "limit": limit,
        }

    logger.info("Starting ClassBot...")
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
