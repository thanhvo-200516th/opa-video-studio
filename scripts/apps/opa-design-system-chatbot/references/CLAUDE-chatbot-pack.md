# OPA Chatbot Agent — Claude Code Context

## Dự án
Gói giao diện và linh hồn cho Chatbot Agent của OPA (OverPowers Agency) — đối tác vận hành AI cho đội ngũ bán hàng và marketing của doanh nghiệp vừa và nhỏ Việt Nam.

## Cấu trúc thư mục
- `assets/`: Các file vector chuẩn của mascot Bò OPA (`opa-mascot-blue.svg`, `opa-mascot-parts.svg`).
- `tokens.ts` / `tokens.json`: Bảng màu, typography, khoảng cách, easing chuyển động chuẩn.
- `MascotAvatar.tsx`: Component avatar linh vật Bò OPA hỗ trợ 5 trạng thái động (`idle`, `thinking`, `responding`, `success`, `alert`).
- `ChatWidget.tsx`: Drop-in floating widget hoàn chỉnh theo chuẩn giao diện OPA.
- `preview.html`: Trang demo tương tác thử nghiệm nhanh trạng thái mascot và khung chat.
- `PROMPT.md`: Các bộ prompt mẫu cho AI Engineer và LLM Runtime.

## Nguyên tắc thiết kế (Design System Rules)
1. **Màu sắc**:
   - Chủ đạo: `#0068FF` (Xanh OPA).
   - Nền tối: `#0A0A0A`. Nền sáng: `#FFFFFF`.
   - Nền phụ / bong bóng chat agent: `#E6F0FF`.
   - Màu chữ: Trên nền xanh dùng trắng `#FFFFFF`. Trên nền trắng dùng `#0A0A0A`.
2. **Typography**:
   - Font: `Be Vietnam Pro` (hỗ trợ đầy đủ dấu tiếng Việt không bị cắt mũ).
   - Tiêu đề: ExtraBold (700-800). Nội dung: Medium (500).
3. **Mascot Bò OPA**:
   - Hình học phẳng, tối giản, dứt khoát.
   - Không tự ý thêm mắt, mũi, miệng hoặc làm 3D bóng bẩy.
   - Chuyển động có tính lực: vào cảnh dứt khoát (`cubic-bezier(0.2, 0.8, 0.2, 1)`), nảy spring nhẹ (`damping: 12`).

## Tính cách & Tone giọng Agent
- **Tính cách**: Khỏe khoắn, tin cậy, chủ động, thẳng thắn, hướng tới hiệu quả thực tế. Không cợt nhả, không trẻ con.
- **Xưng hô**: Xưng "OPA" (hoặc "tôi"), gọi người dùng là "anh/chị".
- **Cách nói**: Câu ngắn gọn (mỗi câu tối đa 7-10 chữ khi hiển thị giao diện), đi thẳng vào việc, không vòng vo.
- **Biên giới hứa hẹn**: Không bịa đặt số liệu tăng trưởng của khách hàng. Không hứa hẹn tính năng hoặc mức giảm giá vượt thẩm quyền.
