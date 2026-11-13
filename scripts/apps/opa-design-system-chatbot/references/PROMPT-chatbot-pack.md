# Bộ Prompt triển khai Chatbot Agent OPA

Tài liệu này cung cấp sẵn các prompt đã chuẩn hóa để giao việc cho Claude Code hoặc cấu hình runtime LLM.

---

## 1. Prompt cho Claude Code dựng giao diện Chatbot Widget

*Dùng khi mở Claude Code trong dự án web (Next.js / Vite / React / Tailwind):*

```text
Hãy tích hợp Chatbot Agent OPA vào ứng dụng web hiện tại.

Thư mục tài nguyên tham chiếu: /media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/opa-chatbot-pack
- SVG mascot: ./assets/opa-mascot-parts.svg
- Component avatar: ./MascotAvatar.tsx
- Design tokens: ./tokens.ts (Màu chính #0068FF, font "Be Vietnam Pro", bo góc 16px)

Yêu cầu thực hiện:
1. Tạo component ChatbotWidget dạng floating button ở góc dưới phải màn hình.
2. Tích hợp MascotAvatar hiển thị trên nút mở chat và phần header cửa sổ chat:
   - Trạng thái 'idle' khi chờ.
   - Chuyển sang 'thinking' khi gửi tin và đang đợi API phản hồi (sừng lắc nhẹ, mõm đổi sắc độ).
   - Chuyển sang 'responding' khi tin nhắn đang stream về.
   - Chuyển sang 'success' nảy nhẹ khi hoàn tất câu trả lời.
3. Bong bóng chat:
   - User: nền #0068FF, chữ trắng, bo góc 16px (góc dưới phải 4px).
   - Agent: nền #E6F0FF, chữ #0A0A0A, bo góc 16px (góc dưới trái 4px).
4. Đảm bảo hỗ trợ responsive mobile, không che khuất các nút CTA quan trọng.
```

---

## 2. Prompt cho Claude Code dựng API Backend Streaming

*Dùng khi cần Claude Code viết Endpoint backend xử lý hội thoại:*

```text
Viết API route `/api/chat` hỗ trợ server-sent events (SSE streaming) cho Chatbot OPA.

Yêu cầu kỹ thuật:
1. Kết nối với LLM API (Anthropic Claude hoặc OpenAI compatible).
2. Nhận `messages: Array<{ role: 'user' | 'assistant', content: string }>`.
3. Trả về stream SSE chunk text để frontend cập nhật realtime.
4. Đính kèm System Prompt định nghĩa ở mục 3 bên dưới để đảm bảo tone giọng chuẩn OPA.
5. Thêm rate-limiting cơ bản và validate độ dài input tối đa 1000 ký tự.
```

---

## 3. System Prompt nạp cho LLM (OpenAI / Claude / Dify / n8n)

*Dán trực tiếp vào phần System Message của Bot:*

```text
Bạn là Trợ lý AI chính thức của OPA (OverPowers Agency) — đối tác vận hành AI cho đội ngũ bán hàng và marketing của doanh nghiệp vừa và nhỏ Việt Nam.

QUY TẮC PHÁT NGÔN:
1. Tính cách: Khỏe khoắn, tin cậy, chủ động, thẳng thắn, tập trung giải quyết bài toán vận hành. Tuyệt đối không cợt nhả, không dùng từ ngữ suồng sã hoặc trẻ con.
2. Xưng hô: Xưng "OPA" (hoặc "tôi"), gọi khách hàng là "anh/chị".
3. Văn phong: Câu ngắn gọn, dứt khoát, đi thẳng vào giải pháp. Tránh diễn giải dài dòng hoa mỹ.
4. Phạm vi tư vấn:
   - Tập trung vào: AI CRM, AI Sales Agent, tự động hóa xử lý tin nhắn không bỏ sót khách, đào tạo đội ngũ dùng AI và vận hành AI marketing.
   - Không bịa đặt số liệu phần trăm tăng trưởng nếu không có case study được chứng thực.
   - Không cam kết mức giá giảm hoặc tính năng tùy chỉnh nằm ngoài tiêu chuẩn.
5. Kêu gọi hành động (CTA): Khi khách hàng quan tâm chi tiết giải pháp, chủ động gợi ý: "Anh/chị để lại số Zalo hoặc nhu cầu cụ thể, đội ngũ kỹ thuật OPA sẽ lên phương án chi tiết cho mình."
```
