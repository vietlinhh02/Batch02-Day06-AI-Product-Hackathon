# Discord Class Bot - Mockup

## Bot Interaction Mockup

### Scenario 1: Happy Path - Tìm bài tập

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Discord Server - #general                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  👤 Nguyễn Viết Linh                                              20:30     │
│     @ClassBot tối qua có bài tập gì không?                                 │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  🤖 ClassBot                                                         20:30   │
│     ┌─────────────────────────────────────────────────────────────────┐     │
│     │ 📚 Câu trả lời:                                                 │     │
│     │                                                                  │     │
│     │ Tối qua thầy giao bài tập về CNN (Convolutional Neural Network):│     │
│     │ • Implement CNN cơ bản trên MNIST                               │     │
│     │ • Deadline: Thứ 6 (07/06/2026)                                  │     │
│     │ • Nộp qua Google Classroom                                     │     │
│     │                                                                  │     │
│     │ 📎 Nguồn tham khảo:                                             │     │
│     │ • Thầy Nguyễn (20:15) → [Xem tin nhắn](link)                   │     │
│     │ • Thảo luận nhóm (20:45) → [Xem tin nhắn](link)                │     │
│     │                                                                  │     │
│     │ ⚠️ Kiểm tra lại bằng link bên dưới để đảm bảo chính xác.       │     │
│     └─────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Scenario 2: Low Confidence - Tìm kiếm mơ hồ

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Discord Server - #general                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  👤 Đặng Minh Chức                                                 21:00    │
│     @ClassBot thầy nói gì về overfitting?                                  │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  🤔 ClassBot                                                         21:00   │
│     ┌─────────────────────────────────────────────────────────────────┐     │
│     │ ⚠️ Tìm thấy ít thông tin về chủ đề này:                        │     │
│     │                                                                  │     │
│     │ Thầy có đề cập ngắn gọn: "Overfitting thì thêm dropout hoặc    │     │
│     │ regularization" trong lúc trả lời câu hỏi.                     │     │
│     │                                                                  │     │
│     │ 📎 Nguồn:                                                       │     │
│     │ • Thầy Nguyễn (19:30) → [Xem tin nhắn](link)                   │     │
│     │                                                                  │     │
│     │ 💡 Bạn có muốn tôi:                                             │     │
│     │ • Tìm thêm context về regularization?                          │     │
│     │ • Hỏi trực tiếp thầy để được giải thích kỹ hơn?               │     │
│     └─────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Scenario 3: Failure - Không tìm thấy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Discord Server - #general                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  👤 Bùi Hoàng Linh                                                21:30     │
│     @ClassBot deadline môn này là khi nào?                                 │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ❓ ClassBot                                                         21:30   │
│     ┌─────────────────────────────────────────────────────────────────┐     │
│     │ 🔍 Không tìm thấy thông tin về deadline trong lịch sử chat.    │     │
│     │                                                                  │     │
│     │ Gợi ý:                                                         │     │
│     │ • Thử hỏi trực tiếp giảng viên                                 │     │
│     │ • Kiểm tra kênh #announcements                                  │     │
│     │ • Hỏi lại bằng câu khác: "khi nào nộp bài tập CNN?"           │     │
│     └─────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Scenario 4: Correction - Sửa lỗi

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Discord Server - #general                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  👤 Hoàng Trung Quân                                               21:45    │
│     @ClassBot bài tập CNN nộp khi nào?                                     │
│                                                                              │
│  🤖 ClassBot                                                         21:45   │
│     ┌─────────────────────────────────────────────────────────────────┐     │
│     │ 📚 Bài tập CNN deadline thứ 6 (07/06). [Xem nguồn](link)       │     │
│     └─────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  👤 Hoàng Trung Quân                                               21:46    │
│     @ClassBot Sai, đó là deadline tuần trước. Tuần này là thứ 4.           │
│                                                                              │
│  🔄 ClassBot                                                         21:46   │
│     ┌─────────────────────────────────────────────────────────────────┐     │
│     │ ✅ Đã ghi nhận correction. Cảm ơn bạn!                         │     │
│     │                                                                  │     │
│     │ Thông tin đã cập nhật:                                          │     │
│     │ • Bài tập CNN deadline: Thứ 4 (05/06)                           │     │
│     │ • Người sửa: Hoàng Trung Quân                                   │     │
│     │ • Thời gian: 21:46                                              │     │
│     └─────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Bot Commands

| Command | Mô tả | Ví dụ |
|---------|--------|-------|
| `@ClassBot <câu hỏi>` | Hỏi bot về nội dung học | `@ClassBot bài tập CNN là gì?` |
| `@ClassBot help` | Hiển thị hướng dẫn sử dụng | `@ClassBot help` |
| `@ClassBot status` | Kiểm tra trạng thái bot | `@ClassBot status` |

## Error States

### Bot không có quyền
```
🤖 ClassBot: Tôi không có quyền đọc tin nhắn trong kênh này. 
   Hãy nhờ admin cấp quyền "Read Message History" cho tôi.
```

### Bot quá tải
```
🤖 ClassBot: Xin lỗi, tôi đang xử lý nhiều câu hỏi. 
   Thử lại sau 30 giây nhé!
```

### Lỗi API
```
🤖 ClassBot: Có lỗi xảy ra khi xử lý câu hỏi. 
   Vui lòng thử lại hoặc báo admin.
```
