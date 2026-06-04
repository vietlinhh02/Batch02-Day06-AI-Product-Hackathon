# Discord Class Bot - Vin AI Thực Chiến

Bot trợ lý AI cho lớp học Discord, sử dụng RAG (Retrieval-Augmented Generation) để trả lời câu hỏi dựa trên lịch sử chat.

## Tính năng chính

- 🤖 Trả lời câu hỏi bằng tiếng Việt dựa trên lịch sử chat
- 📎 Trích dẫn nguồn (tên người nói + link message gốc)
- ⚠️ Xử lý low-confidence và failure cases
- 🔄 Correction mode - học viên có thể sửa thông tin sai
- 🔍 Semantic search với embedding

## Tech Stack

| Component | Technology |
|-----------|------------|
| Discord Bot | discord.py v2.3+ |
| LLM | GPT-4o-mini (via OpenRouter) |
| Embedding | text-embedding-3-small (via OpenRouter) |
| Vector DB | ChromaDB |
| Language | Python 3.9+ |

## Cài đặt

### 1. Clone repo

```bash
git clone <repo-url>
cd codebase
```

### 2. Tạo virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

### 3. Cài dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup environment variables

```bash
cp .env.example .env
```

Edit `.env` với thông tin của bạn:

```env
DISCORD_TOKEN=your_discord_bot_token
OPENAI_API_KEY=sk-or-v1-your_openrouter_key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
```

### 5. Tạo Discord Bot

1. Vào [Discord Developer Portal](https://discord.com/developers/applications)
2. Tạo Application mới → Bot
3. Copy token vào `.env`
4. Enable intents: Message Content Intent, Server Members Intent
5. Invite bot vào server với quyền: Send Messages, Read Message History, Embed Links

### 6. Chạy bot

```bash
python src/bot.py
```

## Sử dụng

### Commands

| Command | Mô tả |
|---------|--------|
| `@ClassBot <câu hỏi>` | Hỏi bot về nội dung học |
| `@ClassBot help` | Hiển thị hướng dẫn |
| `@ClassBot status` | Kiểm tra trạng thái |

### Ví dụ

```
@ClassBot bài tập CNN là gì?
@ClassBot thầy nói gì về overfitting?
@ClassBot deadline khi nào?
```

## Architecture

```
User Question
     │
     ▼
┌─────────────┐
│ Embed Query │ ← text-embedding-3-small (OpenRouter)
└─────────────┘
     │
     ▼
┌─────────────┐
│ Vector Search│ ← ChromaDB (cosine similarity)
└─────────────┘
     │
     ▼
┌─────────────┐
│ Build Context│ ← Top-k chunks + citations
└─────────────┘
     │
     ▼
┌─────────────┐
│ LLM Generate │ ← GPT-4o-mini (OpenRouter) + system prompt
└─────────────┘
     │
     ▼
┌─────────────┐
│ Post-process │ ← Add disclaimer, format
└─────────────┘
     │
     ▼
Discord Response
```

## File Structure

```
codebase/
├── src/
│   ├── bot.py           # Discord bot chính
│   ├── rag_pipeline.py  # RAG pipeline (chunk, embed, retrieve)
│   ├── prompts.py       # Optimized prompts
│   └── config.py        # Configuration
├── data/
│   └── sample_messages.json  # Sample data cho testing
├── docs/
│   ├── flow-diagram.md  # Flow diagram
│   └── mockup.md        # Mockup các scenarios
├── requirements.txt
├── .env.example
└── README.md
```

## Demo Scenarios

### 1. Happy Path ✅
```
User: "Tối qua có bài tập gì không?"
Bot: "Tối qua thầy giao bài tập CNN, deadline thứ 6. [Link]"
```

### 2. Low Confidence ⚠️
```
User: "Thầy nói gì về overfitting?"
Bot: "Chỉ tìm thấy 1 đề cập ngắn. [Link]. Bạn muốn tôi hỏi thêm?"
```

### 3. Failure ❌
```
User: "Deadline môn này là khi nào?"
Bot: "Không tìm thấy thông tin. Thử hỏi giảng viên nhé."
```

### 4. Correction 🔄
```
User: "Sai, đó là deadline tuần trước"
Bot: "Đã ghi nhận. Cảm ơn bạn!"
```

## Phân công nhóm

| Thành viên | Vai trò |
|------------|---------|
| Mai Ngọc Duy | Research / Evidence |
| Hoàng Trung Quân | SPEC |
| Nguyễn Viết Linh | Prototype (Discord bot + RAG) |
| Đặng Minh Chức | Test / Failure paths |
| Bùi Hoàng Linh | Demo script / Repo |

## License

MIT
