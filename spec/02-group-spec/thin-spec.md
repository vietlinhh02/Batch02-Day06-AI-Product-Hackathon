# Thin SPEC — Discord Class Bot (Day 05)

## 1. Track, product/app và user

**Track:** A — Learning OS (Vin AI Thực Chiến)
**Product/app thật:** Discord server lớp học
**User cụ thể:** Học viên tham gia lớp online qua Discord, đặc biệt là người vào muộn, người bỏ lỡ đoạn chat, hoặc người có mặt nhưng không theo kịp tốc độ tin nhắn.
**Nhóm có phải user thật không? Nếu không, khác ở đâu?** Có. Cả nhóm đều là học viên trong Discord lớp Vin AI, đã trải qua pain point thật: scroll 200+ tin để tìm câu trả lời, hỏi lại nhưng bị loãng giữa dòng chat mới.

## 2. Evidence summary

| Evidence | Nguồn | User/pain nói lên điều gì? | SPEC phải đổi gì? |
|---|---|---|---|
| Nhóm vào Discord muộn 30ph, scroll không kịp 200+ tin, hỏi lại không ai rep | Self-use | Chat volume cao → mất thông tin → không có cách tra cứu nhanh | Bot phải trả lời kèm link message gốc để verify |
| Hỏi "có bài tập không", 2 người rep mâu thuẫn | Self-use | Thông tin phân mảnh, không có single source of truth | Bot phải cite nguồn để user tự kiểm chứng |
| Giảng viên tổng kết cuối buổi, hôm sau không ai nhớ | Self-use | Cần bot tổng hợp và trả lời chính xác một lượt | Bot phải giữ được context xuyên suốt buổi học |
| "I kept forgetting to check it regularly" | ResearchGate 2024 | Sinh viên bỏ lỡ tin vì volume quá lớn | Bot phải hoạt động async, không cần user online |
| Sinh viên thấy Discord "confusing, complicated" | Arifianto et al. 2021 | Người mới không biết dùng search/thread của Discord | Bot dùng natural language, không cần học syntax |
| 5+ open-source RAG bot cho Discord đã tồn tại | GitHub (discord-rag, mAIcro, team-memory-bot) | Nhu cầu này là thật, pattern RAG đã được validate | Dùng RAG + context window, không reinvent |

## 3. Pain statement

```text
Học viên lớp Discord đang gặp khó ở bước tra cứu lại nội dung đã trao đổi,
vì chat volume cao (200-500 tin/buổi) + tin nhắn phân mảnh + reply chain phức tạp,
dẫn tới bỏ lỡ bài tập, deadline, kiến thức quan trọng, hoặc phải hỏi lại nhiều lần.
Bằng chứng chính là trải nghiệm của cả nhóm trên chính Discord Vin AI.
```

## 4. Build slice

```text
Cho học viên đang cần tra cứu nội dung buổi học đã qua,
prototype sẽ dùng AI để đọc toàn bộ message history → embed → RAG retrieval → trả lời câu hỏi bằng tiếng Việt,
tạo ra câu trả lời kèm link message gốc (citation),
và xử lý failure mode "câu hỏi không có trong lịch sử chat" bằng fallback: "Không tìm thấy, thử hỏi cách khác hoặc ping giảng viên".
```

## 5. Auto/Aug decision

- [ ] **Augmentation:** AI gợi ý/draft/phân loại, user quyết cuối.
- [ ] **Conditional automation:** AI tự làm trong case hẹp; case mơ hồ/rủi ro chuyển người.
- [x] **Automation:** AI tự quyết và tự hành động.

**Lý do chọn:** Bot trả lời câu hỏi trực tiếp, không có human-in-the-loop vì đây là tra cứu thông tin (không phải quyết định y tế/tài chính). User luôn có thể verify bằng cách click link message gốc.

**Human role:** reviewer (click link message gốc để kiểm chứng câu trả lời)

## 6. Four paths

| Path | Prototype phải thể hiện gì? |
|---|---|
| Happy | User @bot "tối qua có bài tập gì không?" → Bot trả về câu trả lời chính xác + link message gốc của giảng viên |
| Low-confidence | User @bot "thầy nói gì về overfitting?" nhưng chat chỉ có 1 tin mơ hồ → Bot trả lời "Chỉ tìm thấy 1 đề cập ngắn, đây là nội dung gốc [link]. Bạn có muốn tôi hỏi thêm context không?" |
| Failure | User @bot "deadline môn này là khi nào?" nhưng chưa ai nói về deadline trong chat → Bot: "Không tìm thấy thông tin về deadline trong lịch sử chat. Bạn thử hỏi trực tiếp giảng viên nhé." |
| Correction | User phát hiện bot trả lời sai (nhầm deadline của tuần trước thành tuần này) → User reply "Sai, đó là deadline tuần trước" → Bot ghi nhận và cập nhật (manual correction trigger) |

## 7. Failure mode nguy hiểm nhất

```text
Nếu user hỏi một câu mà bot tự tin trả lời sai (hallucination từ LLM),
AI có thể đưa ra thông tin sai về deadline, bài tập, hoặc nội dung học,
hậu quả là học viên làm sai bài, nộp muộn, hoặc hiểu sai kiến thức.
Prototype sẽ xử lý bằng (1) luôn kèm link message gốc để user verify, (2) low-confidence flag khi relevance score < threshold, (3) disclaimer "Kiểm tra lại bằng link bên dưới".
Owner kiểm thử path này là (điền tên thành viên).
```

## 8. Owner plan cho sáng Day 06

| Thành viên | Việc phụ trách | Bằng chứng cần có trong repo |
|---|---|---|
| Mai Ngọc Duy | Research / evidence | Evidence pack + link nguồn |
| Hoàng Trung Quân | SPEC | Thin SPEC + 4 paths documented |
| Nguyễn Viết Linh | Prototype (Discord bot + RAG pipeline) | Code bot + instruction chạy được |
| Đặng Minh Chức | Test / failure path | Screenshot/recording test happy + failure + correction |
| Bùi Hoàng Linh | Demo script / repo | Script demo 3 phút + repo cá nhân đủ file |
