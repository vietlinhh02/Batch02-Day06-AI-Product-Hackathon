# Evidence Pack — Discord Class Bot

---

## 1. Pain Point Summary

Học viên trong lớp học online qua Discord thường gặp khó khăn khi cần tra cứu lại nội dung đã trao đổi trước đó. Vấn đề xuất hiện rõ khi số lượng tin nhắn trong một buổi học tăng nhanh, thông tin bị phân mảnh ở nhiều channel hoặc reply chain, và học viên không online đúng thời điểm để theo dõi toàn bộ cuộc trò chuyện.

Pain point chính:

> Học viên dễ bỏ lỡ bài tập, deadline, nội dung giảng viên đã dặn hoặc câu trả lời quan trọng trong Discord vì chat volume cao, thông tin trôi nhanh và search thủ công không đủ tiện cho người học.

---

## 2. Self-use Evidence của nhóm

| Evidence | Nguồn | User/pain nói lên điều gì? | SPEC implication |
|---|---|---|---|
| Nhóm vào Discord muộn khoảng 30 phút, phải scroll lại hơn 200 tin nhắn nhưng vẫn khó tìm đúng thông tin cần thiết | Self-use | Chat volume cao làm học viên mất thời gian tra cứu và dễ bỏ sót thông tin | Bot phải truy vấn được message history và trả lời kèm link message gốc |
| Khi hỏi “có bài tập không”, có nhiều người trả lời khác nhau, dẫn đến thông tin mâu thuẫn | Self-use | Discord thiếu single source of truth; học viên không biết nên tin câu trả lời nào | Bot phải cite nguồn gốc, ưu tiên message của giảng viên hoặc mentor |
| Giảng viên tổng kết nội dung cuối buổi nhưng hôm sau nhiều người không nhớ chính xác | Self-use | Nội dung quan trọng dễ bị trôi sau buổi học | Bot cần hỗ trợ hỏi lại nội dung buổi học bằng tiếng Việt tự nhiên |
| Học viên hỏi lại trong channel nhưng câu hỏi bị loãng giữa các dòng chat mới | Self-use | Hỏi lại thủ công không đảm bảo có người trả lời | Bot cần hoạt động async, user có thể hỏi lại bất cứ lúc nào |

---

## 3. External Evidence

### Source 1 — Lauricella & Kay: Discord trong lớp học đại học online

**Nguồn:**  
Lauricella, S., & Kay, R. — *Examining the Benefits and Challenges of Using Discord in Online Higher Education Classrooms*  

**Links:**  
- https://journalofeducationalinformatics.ca/index.php/JEI/article/view/225  
- https://www.researchgate.net/publication/377107344_Examining_the_Benefits_and_Challenges_of_Using_Discord_in_Online_Higher_Education_Classrooms

**Nội dung liên quan:**  
Nghiên cứu khảo sát trải nghiệm sinh viên khi dùng Discord trong các lớp đại học online. Discord được đánh giá là có lợi cho việc kết nối, trao đổi và chia sẻ thông tin lớp học, nhưng cũng có các thách thức như khó điều hướng với người mới, cần hướng dẫn sử dụng, và có sinh viên quên kiểm tra Discord thường xuyên.

**Liên hệ với pain point của nhóm:**  
Nguồn này chứng minh rằng vấn đề không chỉ xảy ra trong nhóm mình. Khi Discord được dùng như môi trường học tập, sinh viên có thể bỏ lỡ thông tin hoặc gặp khó khăn trong việc theo dõi nếu không quen nền tảng.

**SPEC implication:**  
Discord Class Bot nên hỗ trợ:

- Hỏi lại nội dung lớp bằng ngôn ngữ tự nhiên.
- Không bắt học viên phải nhớ chính xác keyword, channel hoặc thời điểm gửi tin.
- Trả lời async, tức là học viên có thể hỏi lại sau buổi học.
- Có citation/link message gốc để học viên tự kiểm chứng.

---

### Source 2 — Arifianto & Izzudin, 2021: Students’ Acceptance of Discord as an Alternative Online Learning Media

**Nguồn:**  
Arifianto, M. L., & Izzudin, I. F. — *Students’ Acceptance of Discord as an Alternative Online Learning Media*  

**Links:**  
- https://online-journals.org/index.php/i-jet/article/view/22917  
- https://www.researchgate.net/publication/355589562_Students%27_Acceptance_of_Discord_as_an_Alternative_Online_Learning_Media

**Nội dung liên quan:**  
Bài nghiên cứu khảo sát mức độ chấp nhận Discord như một nền tảng hỗ trợ dạy và học online. Discord có nhiều tính năng hữu ích cho giao tiếp học tập, nhưng các nghiên cứu sau trích lại rằng nhiều người mới dùng Discord có thể thấy nền tảng này khó hiểu, phức tạp hoặc lạ.

**Liên hệ với pain point của nhóm:**  
Nếu học viên mới không quen với Discord, họ sẽ khó tận dụng search, thread, channel hoặc reply chain. Điều này làm tăng khả năng bỏ lỡ nội dung quan trọng.

**SPEC implication:**  
Bot không nên yêu cầu học viên học cú pháp Discord search. Thay vào đó, bot cần hỗ trợ câu hỏi tự nhiên như:

```text
@bot hôm qua thầy giao bài gì?
@bot deadline bài lab là khi nào?
@bot thầy nói gì về RAG?
```

---

### Source 3 — Discord Help Center: How to Use Search on Discord

**Nguồn:**  
Discord Help Center — *How to Use Search on Discord*  

**Link:**  
https://support.discord.com/hc/en-us/articles/115000468588-How-to-Use-Search-on-Discord

**Nội dung liên quan:**  
Tài liệu chính thức của Discord cho thấy Discord Search có nhiều filter như:

- `from:` tìm theo người gửi
- `in:` tìm trong channel
- `mentions:` tìm tin nhắn có nhắc tới ai đó
- `has:` tìm tin nhắn có link, file, embed
- `before:`, `after:`, `during:` tìm theo thời gian

**Liên hệ với pain point của nhóm:**  
Các filter này mạnh, nhưng yêu cầu user phải nhớ khá nhiều thông tin: ai gửi, gửi ở channel nào, khoảng thời gian nào, hoặc keyword cụ thể là gì. Trong bối cảnh học viên vào muộn hoặc bỏ lỡ 200+ tin nhắn, search thủ công không phải cách tối ưu.

**SPEC implication:**  
Bot cần đóng vai trò semantic search layer bên trên Discord history. User chỉ cần hỏi bằng tiếng Việt, bot tự tìm message liên quan.

Ví dụ:

```text
User: Hôm qua có bài tập gì không?
Bot: Có. Giảng viên giao bài lab về RAG, deadline là thứ Sáu. Nguồn: [link message gốc]
```

---

### Source 4 — GitHub: antoinelrnld/discord-rag

**Nguồn:**  
GitHub — `antoinelrnld/discord-rag`  

**Link:**  
https://github.com/antoinelrnld/discord-rag

**Nội dung liên quan:**  
Repo này xây dựng ứng dụng RAG dựa trên Discord messages. Mục tiêu là cho phép hệ thống đọc lịch sử tin nhắn Discord, tạo embedding, retrieve context liên quan và dùng LLM để trả lời.

**Liên hệ với pain point của nhóm:**  
Đây là bằng chứng kỹ thuật cho thấy hướng “Discord message history + RAG + chatbot” đã có tiền lệ. Nhóm không cần build một app quá lớn ngay từ đầu, mà có thể làm prototype hẹp dựa trên pattern có sẵn.

**SPEC implication:**  
Prototype nên tập trung vào pipeline:

```text
Collect Discord messages
→ Clean messages
→ Embed messages
→ Retrieve relevant messages
→ Generate answer
→ Return answer with citation link
```

---

### Source 5 — Vectara Ragtime: RAG Bot for Slack and Discord

**Nguồn:**  
Vectara — *RAGTime: A RAG-Powered Bot for Slack and Discord*  

**Links:**  
- https://www.vectara.com/blog/ragtime-a-rag-powered-bot-for-slack-and-discord  
- https://github.com/vectara/ragtime

**Nội dung liên quan:**  
RAGTime là một bot open-source cho Slack và Discord, cho phép người dùng hỏi đáp dựa trên knowledge corpus. Repo cũng mô tả việc bot lưu message IDs và thread IDs để trả lời theo ngữ cảnh.

**Liên hệ với pain point của nhóm:**  
Điểm này rất quan trọng với Discord Class Bot vì nhóm cần bot trả lời kèm citation/link gốc. Nếu không có link gốc, bot dễ trở thành một hệ thống “nói nghe có vẻ đúng” nhưng không kiểm chứng được.

**SPEC implication:**  
Discord Class Bot nên lưu các trường sau trong dataset:

```json
{
  "message_id": "m001",
  "channel_name": "thảo-luận-lớp-học",
  "author_name": "GV. A",
  "author_role": "teacher",
  "content": "Deadline bài lab là thứ Sáu.",
  "created_at": "2026-06-03T20:15:00",
  "jump_url": "https://discord.com/channels/demo/channel/message"
}
```

Các trường quan trọng nhất cho citation:

- `message_id`
- `channel_name`
- `author_role`
- `created_at`
- `jump_url`

---

## 4. Evidence Table

| Evidence | Nguồn | User/pain nói lên điều gì? | SPEC phải đổi gì? |
|---|---|---|---|
| Nhóm vào Discord muộn 30 phút, phải scroll hơn 200 tin nhắn | Self-use | Chat volume cao làm học viên bỏ lỡ thông tin | Bot phải truy vấn message history và trả lời có citation |
| Hỏi “có bài tập không” nhưng nhận câu trả lời mâu thuẫn | Self-use | Thông tin phân mảnh, không có single source of truth | Bot phải cite message gốc, ưu tiên giảng viên/mentor |
| Giảng viên tổng kết cuối buổi nhưng hôm sau nhiều người không nhớ rõ | Self-use | Nội dung quan trọng dễ bị trôi | Bot cần hỗ trợ hỏi lại nội dung buổi học |
| Sinh viên dùng Discord trong lớp online có thể gặp khó khăn vì cần hướng dẫn, khó điều hướng, hoặc quên kiểm tra thường xuyên | Lauricella & Kay | Discord có ích nhưng không tự động đảm bảo học viên nắm được thông tin | Bot cần async Q&A và natural language query |
| Người mới dùng Discord có thể thấy nền tảng khó hiểu hoặc phức tạp | Arifianto & Izzudin | Không phải học viên nào cũng biết dùng search/thread/channel hiệu quả | Bot nên che bớt độ phức tạp của Discord |
| Discord Search có nhiều filter như from, in, has, before, after, during | Discord Help Center | Search thủ công yêu cầu user nhớ đúng keyword, người gửi, channel hoặc thời gian | Bot cần semantic retrieval thay vì chỉ keyword search |
| Có open-source project xây dựng RAG trên Discord messages | GitHub discord-rag | Hướng Discord + RAG đã có tiền lệ kỹ thuật | Prototype nên dùng RAG pipeline |
| RAGTime hỗ trợ Slack/Discord bot và lưu message/thread IDs | Vectara Ragtime | Trả lời có context và link nguồn là khả thi | Bot cần lưu message_id/thread_id/jump_url để cite nguồn |

---

## 5. Synthesis: Bằng chứng nói gì sâu hơn về user?

Các bằng chứng cho thấy pain point không chỉ là “Discord có nhiều tin nhắn”. Vấn đề sâu hơn là:

1. **Thông tin học tập bị phân mảnh**  
   Một phần nằm trong thông báo, một phần nằm trong thảo luận, một phần nằm trong reply chain.

2. **Học viên không luôn online đúng thời điểm**  
   Khi vào muộn, user phải scroll lại nhiều tin nhắn và rất dễ bỏ sót nội dung quan trọng.

3. **Search thủ công phụ thuộc vào trí nhớ của user**  
   Nếu user không nhớ ai gửi, gửi lúc nào, ở channel nào, hoặc dùng keyword gì, search truyền thống sẽ kém hiệu quả.

4. **Câu trả lời không có nguồn sẽ không đáng tin**  
   Nếu bot chỉ trả lời mà không đưa link message gốc, user vẫn phải tự đi kiểm tra lại. Điều này làm mất giá trị của bot.

Vì vậy, Discord Class Bot nên được thiết kế như một RAG assistant hẹp, không phải một chatbot nói chuyện chung chung.

---

## 6. Opportunity Statement

Học viên trong Discord lớp học cần một cách nhanh hơn để hỏi lại nội dung đã xuất hiện trong lịch sử chat mà không phải tự scroll, tự search, hoặc hỏi lại người khác.

Cơ hội sản phẩm:

> Xây dựng Discord Class Bot giúp học viên hỏi lại nội dung buổi học bằng tiếng Việt tự nhiên, nhận câu trả lời ngắn gọn kèm link message gốc để kiểm chứng.

Đây là việc đáng sửa vì:

- Giảm thời gian tìm lại thông tin.
- Giảm số lần hỏi lại trong channel.
- Giảm rủi ro bỏ lỡ deadline/bài tập.
- Giúp học viên vào muộn vẫn theo kịp lớp.
- Giúp nhóm có một prototype rõ ràng, hẹp và demo được.

---

## 7. Build Slice đề xuất

### Một user

Học viên lớp online qua Discord, đặc biệt là người vào muộn hoặc bỏ lỡ đoạn chat.

### Một task

Hỏi lại nội dung quan trọng đã xuất hiện trong lịch sử chat.

Ví dụ:

```text
@bot tối qua có bài tập gì không?
```

### Một AI decision

AI quyết định message nào trong lịch sử chat là evidence liên quan nhất để trả lời câu hỏi.

### Một output

Bot trả lời bằng tiếng Việt, kèm link message gốc.

Ví dụ:

```text
Có. Tối qua GV. An giao bài lab về RAG, deadline là thứ Sáu 23:59.

Nguồn:
1. Message của GV. An trong #bài-học lúc 20:45: [link]
2. Message nhắc lại của mentor trong #hỏi-đáp lúc 21:10: [link]
```

---

## 8. Auto/Aug Decision

### Chọn hướng: Conditional Automation

Bot được phép tự trả lời trong phạm vi hẹp: tra cứu lại nội dung đã có trong lịch sử Discord.

Tuy nhiên, bot không được tự bịa khi không có evidence đủ mạnh.

### Human giữ quyền ở đâu?

User giữ quyền kiểm chứng bằng cách click link message gốc.

Nếu bot không chắc, bot phải nói rõ:

```text
Mình chỉ tìm thấy một message liên quan nhưng chưa đủ chắc. Đây là nguồn gốc để bạn kiểm tra lại: [link]
```

### Nguyên tắc truyền thống nên giữ

Thông tin chính thức vẫn nên ưu tiên từ:

1. Giảng viên
2. Mentor
3. Thông báo lớp học
4. Message của học viên chỉ dùng làm nguồn phụ

---

## 9. Four Paths

| Path | Mô tả | Bot cần làm gì? |
|---|---|---|
| Happy path | User hỏi “tối qua có bài tập gì không?” và trong chat có message rõ ràng từ giảng viên | Trả lời đúng bài tập + deadline + link message gốc |
| Low-confidence path | User hỏi “thầy nói gì về overfitting?” nhưng chat chỉ có một đoạn nhắc mơ hồ | Báo rằng evidence yếu, đưa link message liên quan, không kết luận quá chắc |
| Failure path | User hỏi deadline nhưng trong lịch sử chat không có thông tin deadline | Nói “không tìm thấy”, đề xuất hỏi giảng viên/mentor |
| Correction path | Bot nhầm deadline tuần trước thành tuần này | User sửa, bot ghi nhận correction và cập nhật answer trong demo |

---

## 10. Failure Mode nguy hiểm nhất

Failure mode nguy hiểm nhất là bot trả lời sai nhưng nghe có vẻ tự tin.

Ví dụ:

```text
User: Deadline bài lab là khi nào?
Bot sai: Deadline là tối nay.
```

Trong thực tế, nếu deadline thật là tuần sau hoặc chưa được công bố, học viên có thể làm sai kế hoạch, nộp nhầm hoặc mất niềm tin vào bot.

### Cách prototype xử lý

Prototype cần có 3 cơ chế:

1. **Always cite source**  
   Mọi câu trả lời phải kèm link message gốc.

2. **Low-confidence fallback**  
   Nếu retrieval score thấp hoặc evidence không rõ, bot không được trả lời chắc chắn.

3. **No-evidence answer**  
   Nếu không tìm thấy bằng chứng, bot phải nói không tìm thấy thay vì tự suy đoán.

Mẫu fallback:

```text
Mình chưa tìm thấy thông tin deadline trong lịch sử chat hiện có.
Bạn nên hỏi trực tiếp giảng viên hoặc mentor để xác nhận.
```

---

## 11. Source List

### Academic / Education Sources

1. Lauricella, S., & Kay, R.  
   *Examining the Benefits and Challenges of Using Discord in Online Higher Education Classrooms*  
   https://journalofeducationalinformatics.ca/index.php/JEI/article/view/225

2. Lauricella, S., & Kay, R. — ResearchGate version  
   https://www.researchgate.net/publication/377107344_Examining_the_Benefits_and_Challenges_of_Using_Discord_in_Online_Higher_Education_Classrooms

3. Arifianto, M. L., & Izzudin, I. F.  
   *Students’ Acceptance of Discord as an Alternative Online Learning Media*  
   https://online-journals.org/index.php/i-jet/article/view/22917

4. Arifianto & Izzudin — ResearchGate version  
   https://www.researchgate.net/publication/355589562_Students%27_Acceptance_of_Discord_as_an_Alternative_Online_Learning_Media

### Product / Technical Sources

5. Discord Help Center  
   *How to Use Search on Discord*  
   https://support.discord.com/hc/en-us/articles/115000468588-How-to-Use-Search-on-Discord

6. GitHub — discord-rag  
   https://github.com/antoinelrnld/discord-rag

7. Vectara Blog — RAGTime: A RAG-Powered Bot for Slack and Discord  
   https://www.vectara.com/blog/ragtime-a-rag-powered-bot-for-slack-and-discord

8. GitHub — Vectara Ragtime  
   https://github.com/vectara/ragtime

---

## 12. Research Conclusion

Dựa trên self-use của nhóm và nguồn ngoài nhóm, pain point “học viên bị mất thông tin trong Discord lớp học” là có thật. Vấn đề không chỉ nằm ở việc có nhiều tin nhắn, mà còn nằm ở việc thông tin bị phân mảnh, khó tra cứu, khó xác minh và dễ bị trôi khi học viên không online đúng thời điểm.

Vì vậy, hướng build hợp lý nhất cho Discord Class Bot là:

```text
Discord message history
→ RAG retrieval
→ Answer in Vietnamese
→ Citation link to original Discord message
```

Prototype không nên build thành một app lớn. Build slice hẹp nên là:

> Học viên hỏi lại nội dung buổi học đã qua, bot trả lời dựa trên message history và luôn kèm link message gốc để kiểm chứng.

Đây là scope đủ nhỏ để demo trong Day 06, nhưng vẫn chứng minh được giá trị cốt lõi của sản phẩm.
