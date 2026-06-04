# Discord Class Bot - RAG Pipeline Flow

## Main Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DISCORD CLASS BOT                                  │
│                            RAG Pipeline Flow                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   DATA INGESTION │     │   EMBEDDING      │     │   VECTOR STORE   │
│                  │     │                  │     │                  │
│ Discord Messages │────▶│ Text Chunking    │────▶│ ChromaDB         │
│ • Channel msgs   │     │ • 512 tokens     │     │ • Persistent     │
│ • Threads        │     │ • Overlap 50     │     │ • Cosine sim     │
│ • Reactions      │     │ • Metadata       │     │ • HNSW index     │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                                            │
                                                            │ Embeddings
                                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER QUERY FLOW                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ User @bot hỏi    │     │ Query Embedding  │     │ Semantic Search  │
│                  │────▶│                  │────▶│                  │
│ "Tối qua có      │     │ text-embedding-  │     │ Top-k=5 results  │
│  bài tập gì?"   │     │ 3-small          │     │ Score > 0.3      │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                                            │
                                                            │ Retrieved chunks
                                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RETRIEVAL & FILTERING                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ Score Check      │     │ Context Builder  │     │ Prompt Assembly  │
│                  │────▶│                  │────▶│                  │
│ • score >= 0.3   │     │ • Merge chunks   │     │ System prompt    │
│ • No results?    │     │ • Add metadata   │     │ + Context        │
│   → Fallback     │     │ • Add links      │     │ + User query     │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                                            │
                                                            │ Assembled prompt
                                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              LLM GENERATION                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ GPT-4o-mini      │     │ Response         │     │ Post-processing  │
│                  │────▶│ Generation       │────▶│                  │
│ • Vietnamese     │     │ • Answer         │     │ • Add citations  │
│ • Temperature 0.3│     │ • Confidence     │     │ • Add disclaimer │
│ • Max tokens 500 │     │ • Citations      │     │ • Format output  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                                            │
                                                            │ Final response
                                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             DISCORD OUTPUT                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  🤖 Câu trả lời:                                                            │
│                                                                              │
│  Tối qua thầy giao bài tập về CNN, deadline thứ 6.                         │
│                                                                              │
│  📎 Nguồn:                                                                   │
│  • [Thầy Nguyễn - 20:15](discord.com/channels/...)                         │
│  • [Thảo luận](discord.com/channels/...)                                   │
│                                                                              │
│  ⚠️ Kiểm tra lại bằng link bên dưới để đảm bảo chính xác.                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Four Paths Flow

### 1. Happy Path ✅
```
User: "Tối qua có bài tập gì không?"
  │
  ├─▶ Embed query
  ├─▶ Search vector store
  ├─▶ Found 3 results (score > 0.5)
  ├─▶ Build context with citations
  ├─▶ Generate answer
  └─▶ Return: "Bài tập CNN, deadline T6. [Link]"
```

### 2. Low Confidence Path ⚠️
```
User: "Thầy nói gì về overfitting?"
  │
  ├─▶ Embed query
  ├─▶ Search vector store
  ├─▶ Found 1 result (score = 0.35)
  ├─▶ Flag as low-confidence
  └─▶ Return: "Chỉ tìm thấy 1 đề cập ngắn. [Link]. Bạn muốn tôi hỏi thêm?"
```

### 3. Failure Path ❌
```
User: "Deadline môn này là khi nào?"
  │
  ├─▶ Embed query
  ├─▶ Search vector store
  ├─▶ No results (score < 0.3)
  └─▶ Return: "Không tìm thấy thông tin. Thử hỏi giảng viên nhé."
```

### 4. Correction Path 🔄
```
User: "Sai, đó là deadline tuần trước"
  │
  ├─▶ Detect correction intent
  ├─▶ Log correction to database
  ├─▶ Update message metadata
  └─▶ Return: "Đã ghi nhận. Cảm ơn bạn!"
```

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     TECHNICAL STACK                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  Discord.py  │    │  OpenRouter │    │  ChromaDB   │         │
│  │  v2.3+      │    │  GPT-4o-mini│    │  v0.4+      │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                  │                  │                  │
│         └──────────────────┼──────────────────┘                  │
│                            │                                     │
│                     ┌──────▼──────┐                              │
│                     │   Main Bot  │                              │
│                     │   Pipeline  │                              │
│                     └─────────────┘                              │
│                                                                  │
│  Embedding Model: text-embedding-3-small (1536 dims) via OpenRouter │
│  Chunk Size: 512 tokens, 50 overlap                             │
│  Similarity: Cosine, threshold 0.3                              │
│  Top-k: 5 results                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```
