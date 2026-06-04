# Evidence Pack — Discord Class Bot

## 1. Nhóm và track

**Tên nhóm:** (điền tên nhóm)
**Thành viên:** Mai Ngọc Duy - 2A202600736, Hoàng Trung Quân - 2A202600720, Đặng Minh Chức - 2A20260061, Bùi Hoàng Linh - 2A202600804, Nguyễn Viết Linh - 2A202600719 *
**Track:** A — Learning OS (Vin AI Thực Chiến)
**Product/app đã chọn:** Discord lớp học
**Build slice đang nghĩ:** AI bot đọc toàn bộ message history trong server/channel, trả lời câu hỏi của học viên về nội dung đã trao đổi.

## 2. Self-use evidence

Nhóm tự dùng Discord lớp Vin AI và ghi lại điểm gãy.

| Observation | Path liên quan | Điều học được |
|---|---|---|
| Vào Discord muộn 30 phút, scroll không kịp 200+ tin nhắn. Hỏi lại thì không ai rep vì ai cũng đang theo dòng mới | Happy + Failure | Học viên cần cách tra cứu nhanh nội dung đã nói, không phụ thuộc vào người khác |
| Hỏi "có bài tập không" trong group → người rep trước nói "có", người rep sau nói "không có gì đâu" → không biết ai đúng | Low-confidence | Thông tin trong chat bị phân mảnh, cần nguồn duy nhất để xác nhận |
| Cuối buổi giảng viên tổng kết dài 1 đoạn, hôm sau không ai nhớ đủ. Phải scroll lại tìm | Happy | Cần bot tóm tắt hoặc trả lời chính xác vào 1 lần hỏi |
| Có người reply tin nhắn từ hôm trước, context bị đứt | Failure | Bot cần theo dõi reply chain về message gốc để không mất context |

## 3. User / review / social evidence

| Quote / review / observation | Nguồn | User là ai? | Pain/failure mode |
|---|---|---|---|
| "I kept forgetting to check it regularly!" | ResearchGate (2024) — Examining Benefits and Challenges of Using Discord in Online Higher Education | Sinh viên đại học | Không theo kịp tin nhắn, bỏ lỡ thông tin quan trọng |
| "Read Message History must be enabled or students will not see most of their colleagues' posts (or yours)!" | Ryan Cordell (2021) — Tips for Classroom Discord | Giảng viên dùng Discord dạy học | Học viên không xem được lịch sử, post lặp lại vì không biết đã có người hỏi |
| "The undergroundness of Discord is part of its appeal... students use it to ask logistical questions about class too embarrassed to ask the professor" | EdSurge (2023) — How Students Use Unofficial Online Backchannels | Sinh viên dùng Discord ngoài giờ học | Hỏi trong group, không ai rep hoặc rep sai |
| Over half of new-to-Discord participants found it "confusing, complicated, or strange" | Arifianto et al. (2021), cited in ResearchGate | Sinh viên mới dùng Discord | Không biết cách tìm lại thông tin cũ, không dùng được thread/search |
| Students "need scaffolds and support to practice communication online" | EdWeek (2025) — Can Messaging Apps Like Discord Facilitate Student Learning? | Giáo viên quan sát học sinh | Tin nhắn nhanh + nhiều người nói → lộn xộn → không extract được kiến thức |

## 4. Competitor / analog evidence

| App / mô hình tham khảo | Họ xử lý task này thế nào? | Pattern học được | Có áp dụng trong 1 ngày không? |
|---|---|---|---|
| **discord-rag** (antoinelrnld) | Bot đọc toàn bộ message → embed vào vector store → `/ask` trả về RAG answer | Semantic chunking + RAG, dùng ChromaDB/PGVector | Có. Embed + RAG là pattern chuẩn |
| **mAIcro** (MicroClub-USTHB) | Hybrid search (vector + BM25 + RRF), sync real-time từ Discord Gateway, temporal intelligence | Real-time sync, hybrid search, question normalization | Có. Chunk context window đơn giản hơn hybrid search |
| **team-memory-bot** (rkarwankar) | Mem0 AI cho memory, vector semantic search, phân loại knowledge type | Phân loại knowledge để tăng accuracy khi retrieve | Một phần. Có thể bỏ classification để đơn giản hóa |
| **DiscordSam** (helix4u) | LLM local + ChromaDB + distilled summaries + reply chain context | Phát hiện reply chain để giữ context, distill summaries | Có. Reply chain là key insight cho chat bị nhão |
| **js-llmcord** (stanley2058) | Conversation threading từ reply chain + thread, RAG với pgvector, multiple LLM providers | Max 25 messages context, reply chain reconstruction | Có. Đơn giản, chỉ cần reply chain + chunk context |

## 5. Evidence -> Insight

```text
Evidence nổi bật nhất:
- Học viên Discord lớp AI thường xuyên hỏi lại câu đã có người trả lời (self-use)
- Nghiên cứu chỉ ra sinh viên "forget to check" và bị overwhelmed bởi volume tin nhắn (ResearchGate)
- Giảng viên phải bật Read Message History vì sinh viên không xem được tin cũ (Cordell)
- Open-source community đã xây dựng 5+ dự án RAG bot cho Discord (competitor)

Insight:
User không chỉ cần đọc lại chat history.
Thật ra họ cần một cách hỏi nhanh bằng ngôn ngữ tự nhiên và nhận câu trả lời tổng hợp từ toàn bộ lịch sử chat, không cần scroll hay biết từ khóa chính xác.

Opportunity:
AI có thể giúp bằng cách đọc toàn bộ message history → embed → RAG retrieval → trả lời câu hỏi kèm trích dẫn message gốc. Học viên chỉ cần @bot "có bài tập không", bot tự tìm và trả lời.
```

## 6. Evidence đổi SPEC như thế nào?

- [x] Đổi user chính: từ "học viên vắng mặt" → bổ sung cả "học viên có mặt nhưng không theo kịp"
- [x] Đổi failure mode: từ "transcript sai" (voice) → "context quá rộng/nhão" (text chat)
- [x] Đổi build slice: từ voice-meeting bot → text-history bot
- [ ] Đổi Auto/Aug decision.
- [ ] Đổi 4 paths.
- [x] Đổi owner/test plan.
- [ ] Đổi pain statement.

Ghi rõ 1-2 thay đổi quan trọng:

```text
Trước evidence, nhóm định làm voice bot (STT + summary) cho Zoom meeting.
Sau evidence, nhóm đổi thành text-history bot (RAG trên message history) cho Discord.
Lý do: (1) Voice STT tiếng Việt có độ trễ và sai số cao, không demo được trong 1 ngày. (2) Discord là môi trường thật của Vin AI, học viên tương tác chính qua text. (3) Pain point "scroll mỏi tay + hỏi lại không ai rep" là real pain có evidence cả trong nhóm lẫn research.
```
