# SPEC sản phẩm — Discord Class Bot

## 1. Bằng chứng

Nỗi đau: Học viên lớp Discord đang gặp khó ở bước tra cứu lại nội dung đã trao đổi, vì chat volume cao (200-500 tin/buổi), tin nhắn phân mảnh, reply chain phức tạp.
Dẫn tới: Bỏ lỡ bài tập, deadline, kiến thức quan trọng, hoặc phải hỏi lại nhiều lần.

**Trải nghiệm trực tiếp (Self-use):**
- Nhóm vào Discord muộn 30 phút, scroll không kịp 200+ tin, hỏi lại không ai rep.
- Hỏi "có bài tập không", 2 người rep mâu thuẫn (không có single source of truth).
- Giảng viên tổng kết cuối buổi, hôm sau không ai nhớ.

**Nguồn bên ngoài nhóm (Evidence Pack chốt):**

Nhóm xác định nguồn mạnh nhất chứng minh cho pain point là **Lauricella & Kay 2023**, vì nó chỉ ra trực tiếp vấn đề "khó điều hướng, cần cấu trúc hơn" trong môi trường lớp học online. Các nguồn GitHub chỉ đóng vai trò chứng minh tính khả thi về mặt kỹ thuật.

| Evidence | Nguồn | User/pain nói lên điều gì? | SPEC phải đổi gì? |
|---|---|---|---|
| Sinh viên dùng Discord trong lớp online gặp khó khăn vì cần tutorial, khó điều hướng channel, phải check thêm một app nữa | [Lauricella & Kay 2023](https://journalofeducationalinformatics.ca/index.php/JEI/article/download/225/203/1413) | Discord có ích nhưng dễ gây mất thông tin nếu user không theo dõi thường xuyên | Bot cần async Q&A, hỏi lại được sau buổi học |
| Hơn một nửa người mới dùng Discord trong nghiên cứu Arifianto et al. thấy Discord confusing/complicated/strange | [Arifianto & Izzudin 2021](https://online-journals.org/index.php/i-jet/article/view/22917), cited in Lauricella & Kay 2023 | Người mới không nhất thiết biết dùng Discord search/thread hiệu quả | Bot dùng natural language, không yêu cầu học syntax |
| Discord search chính thức có nhiều filter như from, in, mentions, has, before, after | [Discord Help Center](https://support.discord.com/hc/en-us/articles/115000468588-How-to-Use-Search-on-Discord) | Search thủ công yêu cầu user nhớ đúng người gửi, channel, ngày hoặc keyword | Bot cần tự retrieve từ message history |
| Repo discord-rag cho phép tạo RAG app dựa trên Discord messages | [GitHub discord-rag](https://github.com/antoinelrnld/discord-rag) | Pattern hỏi đáp trên lịch sử Discord đã có tiền lệ kỹ thuật | Dùng RAG pipeline: collect messages → embed → retrieve → answer |
| Ragtime là open-source RAG bot cho Slack/Discord, có lưu message/thread IDs để trả lời theo context | [Vectara Ragtime](https://github.com/vectara/ragtime) | Citation/message link là hướng khả thi | Bot cần trả lời kèm link message gốc để verify |

## 2. Lát cắt để build

Cho học viên đang cần tra cứu nội dung buổi học đã qua, prototype sẽ dùng AI để đọc toàn bộ message history → embed → RAG retrieval → trả lời câu hỏi bằng tiếng Việt.
Bot tạo ra câu trả lời **luôn kèm link message gốc** (citation) để verify, và có khả năng xử lý fallback khi "câu hỏi không có trong lịch sử chat" hoặc "nguồn thông tin không đáng tin cậy".

## 3. AI Product Canvas

| Ô | Nội dung giải quyết |
|---|---------------------|
| **Value** | Dành cho học viên học online qua Discord. Giải quyết nỗi đau quá tải thông tin, trôi tin nhắn. AI giúp truy xuất thông tin tức thì bằng ngôn ngữ tự nhiên thay vì tự cuộn (scroll) tìm kiếm thủ công. |
| **Trust** | AI luôn đính kèm link message gốc để người dùng tự click vào kiểm chứng (verify). Có cơ chế cảnh báo "Độ tin cậy: Thấp/Trung bình" nếu thông tin lấy từ học viên thay vì giảng viên. |
| **Feasibility** | Khả thi cao để build. Chi phí thấp do lượng text mỗi buổi học không quá lớn (context window có thể bao quát được). Dữ liệu có sẵn từ lịch sử chat Discord. Rủi ro Hallucination có thể mitigate bằng Prompting và JSON schema. |
| **Tín hiệu học** | Khi user phản hồi bot sai (ví dụ đính chính "deadline là tuần trước"), dữ liệu lỗi này giúp nhóm tinh chỉnh lại system prompt (Few-shot prompting) để bot phân biệt context tốt hơn ở lần sau. |

## 4. Tăng năng lực hay tự động hóa

**Lựa chọn:** Tự động hóa (Automation)
**Lý do:** Bot sẽ tự quyết và tự hành động trả lời trực tiếp cho người dùng. Vì đây là hành vi tra cứu thông tin thông thường (không phải quyết định y tế, tài chính hay điều hướng hệ thống nguy hiểm). 
Người dùng đóng vai trò **Reviewer** - tự verify tính đúng đắn qua link gốc do bot cung cấp. Nếu sai thì hậu quả là hiểu lầm thông tin nhưng dễ dàng hoàn tác bằng việc hỏi lại hoặc tra link.

## 5. Bốn đường đi của trải nghiệm

| Đường đi | Tình huống | Cách prototype xử lý |
|----------|---------|------------------|
| **Đường thuận (Happy)** | User @bot "Tổng hợp lại deadline tuần này" | Bot trả về các deadline chính xác kèm link message gốc (citation) để verify. |
| **Khi AI không chắc (Low-confidence)** | User @bot hỏi về thông tin chưa được giảng viên xác nhận (VD: "Deadline tuần này là..." nhưng chỉ học viên nói) | Bot trả lời kèm cảnh báo "Độ tin cậy: Thấp/Trung bình" và khuyên check lại với giảng viên. |
| **Khi AI sai (Failure/Fallback)** | User @bot hỏi thông tin không hề có trong chat (VD: "ai tạo ra bot này") | Bot trả lời "Không tìm thấy thông tin trong lịch sử chat. Bạn thử hỏi trực tiếp giảng viên nhé." |
| **Khi người dùng sửa (Correction)** | Xử lý lỗi "ảo tưởng" (hallucination) khi gọi hàm. Bot trả lời sai tham số. | Người dùng đính chính (VD: "Tôi nhớ có lịch trình lúc 13h"). Tín hiệu này dùng để áp dụng Few-shot Prompting và JSON schema chuẩn ép bot nhận diện ngữ cảnh đúng. |

## 6. Những kiểu lỗi đáng lo nhất

**Lỗi Hallucination (Ảo tưởng thông tin từ LLM):**
- **Khi nào xảy ra:** Khi đầu vào mơ hồ, hoặc khi dùng Tool Calling thiếu mô tả JSON Schema chặt chẽ, khiến AI tự "bịa" ra tham số thay vì trích xuất từ lịch sử.
- **Hậu quả:** AI đưa ra thông tin sai về deadline, bài tập. Học viên làm sai bài, nộp muộn, hoặc hiểu sai kiến thức (rất nguy hiểm).
- **Cách xử lý của prototype:** 
  1. Luôn kèm link message gốc để user verify.
  2. Đánh giá độ tin cậy "Cao/Trung bình/Thấp" dựa trên nguồn thông tin.
  3. Có disclaimer: "AI có thể sai — kiểm tra bằng link bên trên".

## 7. Kế hoạch kiểm thử và bằng chứng demo

**Kịch bản test:**
- **Đầu vào bình thường (Happy path):** Nhập "Tổng hợp lại deadline tuần này" -> Kì vọng bot list ra đủ 2 deadline từ chat kèm link gốc.
- **Đầu vào khó/nhiễu (Low-confidence & Correction):** Nhập "Tôi nhớ có lịch trình check point lúc 13h cơ" -> Kì vọng bot nhận diện thông tin này chưa được giảng viên confirm và trả lời "Mức tin cậy: Thấp".
- Bằng chứng lưu lại: Screenshot hội thoại thực tế giữa bot và nhóm trên server Discord. (Đã ghi nhận trong log).

## 8. Phân công

| Thành viên | Việc phụ trách | Bằng chứng cần có trong repo |
|---|---|---|
| **Mai Ngọc Duy** | Research / evidence | Evidence pack + link nguồn |
| **Hoàng Trung Quân** | SPEC | File `spec/spec.md` chuẩn hóa theo form |
| **Nguyễn Viết Linh** | Prototype (Discord bot + RAG) | Code bot + instruction chạy được |
| **Đặng Minh Chức** | Test / failure path | Screenshot test 4 paths, xử lý Hallucination |
| **Bùi Hoàng Linh** | Demo script / repo | Script demo 3 phút + tổng hợp repo |
