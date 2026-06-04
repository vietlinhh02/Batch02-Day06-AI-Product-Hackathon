# Synthesis & Decide — Discord Class Bot

Dùng sau khi nhóm đã có evidence. Mục tiêu là chốt một build slice đủ nhỏ cho Day 06.

## 1. Gom evidence thành cụm

Gom theo **workflow/pain**, không gom theo tên feature.

- "Scroll không kịp, hỏi lại không ai rep"
- "Thông tin phân mảnh, 2 người rep mâu thuẫn"
- "Không nhớ nội dung buổi trước, không biết cách tra lại"
- "Người mới dùng Discord không biết search/thread"
- "Chat volume cao (200-500 tin/buổi) → quá tải"

## 2. Viết insight

```text
Học viên lớp Discord không chỉ cần đọc lại chat history.
Họ thật ra cần một cách tra cứu nhanh bằng ngôn ngữ tự nhiên, không cần scroll hay biết từ khóa,
vì evidence cho thấy (1) chat volume quá lớn để đọc tuần tự, (2) thông tin bị phân mảnh qua nhiều tin nhắn và reply chain, (3) người dùng không có thời gian hoặc kỹ năng dùng search Discord.
```

## 3. Viết opportunity

```text
Cơ hội là dùng AI để tự động trả lời câu hỏi từ toàn bộ lịch sử chat (RAG over message history),
giúp user nhận câu trả lời chính xác kèm link message gốc trong vài giây,
trong khi vẫn kiểm soát hallucination bằng citation + low-confidence flag.
```

## 4. Chọn build slice

Build slice tốt phải qua 5 câu hỏi:

| Câu hỏi | Đạt khi | Đánh giá |
|---|---|---|
| User cụ thể chưa? | Nói được ai dùng, trong bối cảnh nào. | Đạt. Học viên Vin AI Discord, vào muộn hoặc cần tra cứu lại. |
| Task đủ hẹp chưa? | Demo được trong 3-5 phút. | Đạt. Demo: 1 user @bot 1 câu → bot trả lời + cite link. |
| AI decision rõ chưa? | AI gợi ý/tự làm một việc cụ thể. | Đạt. AI retrieve + generate answer từ message history. |
| Failure path rõ chưa? | Có một case AI không chắc hoặc sai để test. | Đạt. 3 failure paths: không tìm thấy, low-confidence, hallucination. |
| Có evidence không? | Có bằng chứng từ self-use/review/user/competitor. | Đạt. Self-use team + ResearchGate paper + 5 competitor repos. |

## 5. Quyết định: giữ, giảm scope, hay đổi hướng?

| Tình huống | Quyết định |
|---|---|
| Evidence yếu, user mơ hồ | — (không áp dụng, evidence đủ mạnh) |
| Ý tưởng quá rộng | Giảm scope: từ "giải thích + tóm tắt + Q&A" → chỉ "Q&A kèm citation". Tóm tắt để backlog. |
| AI không cần thiết | — (cần RAG, không thể làm bằng rule) |
| Rủi ro cao | Chọn automation nhưng luôn kèm citation link để user verify. |
| Không demo được trong 1 ngày | Đưa real-time sync + hybrid search vào backlog. Day 06 chỉ làm: fetch history 1 kênh → embed → `/ask` trả lời. |

## 6. Câu chốt cuối

Điền câu này trước khi rời lớp:

```text
Dựa trên self-use (nhóm scroll Discord mỏi tay + hỏi lại không ai rep) và research (ResearchGate + 5 open-source RAG bots),
nhóm sẽ build một Discord bot dùng RAG trên message history,
cho học viên lớp Vin AI Discord,
để giải quyết pain "không tra cứu được nội dung cũ vì chat quá nhiều và phân mảnh",
bằng cách AI tự động retrieve + generate câu trả lời kèm link message gốc,
và sẽ test failure path "bot tự tin trả lời sai" bằng cách cố tình hỏi câu không có trong chat để xem bot có hallucinate không.
```

## 7. Backlog

Những thứ **không build trong Day 06**:

- Real-time sync (bot chỉ fetch history 1 lần, không listen message mới)
- Hybrid search (chỉ dùng vector similarity, không BM25 + RRF)
- Tóm tắt buổi học (chỉ Q&A, không auto-summarize)
- Multi-channel support (chỉ 1 channel)
- Phân biệt người nói (giảng viên vs học viên) trong câu trả lời
- Voice transcription (bỏ hoàn toàn)
