# OPA Design System — Context for Claude Code

Hệ thống thiết kế và quy chuẩn logo chính thức của OverPowers Agency (OPA).

## Tài nguyên có sẵn
- `assets/svg/`: Vector SVG chuẩn (`opa-mascot-blue.svg`, `opa-mascot-white.svg`, `opa-mascot-parts.svg`).
- `assets/png/`: Bản render 2000x2000px trong suốt (`OPA-V4-A-Core-*.png`).
- `assets/pdf/`: Master vector PDF (`OPA — Biểu tượng 2D V4.pdf`).
- `tokens.ts` & `tokens.json`: Hằng số màu sắc, typography, radii, motion.
- `theme.css`: CSS Variables chuẩn OPA.
- `tailwind.preset.js`: Preset sẵn cho dự án dùng Tailwind CSS.
- `DESIGN-SYSTEM.md`: Tài liệu hướng dẫn nhận diện chi tiết.

## Quy tắc bắt buộc khi code giao diện
1. **Màu sắc**:
   - Xanh chủ đạo: `#0068FF`.
   - Nền tối: `#0A0A0A`. Nền sáng: `#FFFFFF`. Nền phụ/bubble: `#E6F0FF`.
   - Phối màu tương phản: Logo/chữ trắng trên nền xanh hoặc nền tối; logo/chữ đen hoặc xanh trên nền sáng.
   - Không dùng gradient màu mè hoặc hiệu ứng 3D.
2. **Typography**:
   - Font chính: `Be Vietnam Pro` (tiêu đề 800, body 500).
   - Font nhấn cụm từ: `Fraunces` Italic 800.
3. **Mascot**:
   - Biểu tượng Bò OPA: hình học phẳng, vững chãi, dứt khoát.
   - Khi cần animate các bộ phận, dùng `assets/svg/opa-mascot-parts.svg` với 4 ID: `c-muzzle`, `a-horn-left`, `b-horn-right`, `d-nostril-gap`.
