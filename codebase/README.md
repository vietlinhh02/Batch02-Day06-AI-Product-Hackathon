# Discord Class Bot — RAG Q&A over Message History

Discord bot dùng RAG trên message history để trả lời câu hỏi của học viên bằng tiếng Việt.

## Tech Stack

| Thành phần | Công nghệ |
|---|---|
| Bot framework | discord.py 2.x |
| LLM | DeepSeek V4 Flash (`deepseek-v4-flash`) |
| API endpoint | `https://opencode.ai/zen/go/v1/chat/completions` |
| Retrieval | TF-IDF + cosine similarity (scikit-learn) |
| HTTP client | httpx |
| Runtime | Python 3.11+ |

## Cài đặt

```bash
cd codebase

# Tạo virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Cài dependencies
pip install -e .
```

## Cấu hình

```bash
cp .env.example .env
# Chỉnh sửa .env với giá trị thật:
#   DISCORD_TOKEN        - Token của Discord bot
#   DEEPSEEK_API_KEY     - API key cho DeepSeek
#   TARGET_CHANNEL_ID    - ID kênh Discord cần index (để trống = dùng kênh hiện tại)
```

### Lấy Discord Bot Token

1. Vào https://discord.com/developers/applications
2. Tạo application → Bot → Copy token
3. Bot cần quyền: `Send Messages`, `Read Message History`, `Use Slash Commands`
4. Invite bot với scope `bot` + `applications.commands`

## Chạy

```bash
python -m bot.main
```

## Slash Commands

| Command | Mô tả |
|---|---|
| `/ask <câu hỏi>` | Hỏi về nội dung đã trao đổi trong kênh |
| `/reload` | Tải lại lịch sử chat từ kênh |

## Cấu trúc

```
codebase/
├── pyproject.toml        ← Dependencies
├── .env.example          ← Biến môi trường mẫu
└── bot/
    ├── __init__.py
    ├── main.py           ← Entry point, Discord client
    ├── config.py         ← Settings từ env vars
    ├── llm.py            ← DeepSeek V4 Flash integration
    ├── rag.py            ← TF-IDF retrieval + chunking
    └── cog_qa.py         ← Slash commands (/ask, /reload)
```

## Flow

1. Bot khởi động → sync slash commands
2. User `/ask "tối qua có bài tập gì không?"`
3. Bot fetch 2000 tin nhắn gần nhất từ channel → chunk → build TF-IDF index
4. TF-IDF cosine search tìm top-k chunks liên quan
5. Gửi context + câu hỏi đến DeepSeek V4 Flash
6. Trả lời embed với citation link message gốc
7. Nếu không tìm thấy → fallback message
