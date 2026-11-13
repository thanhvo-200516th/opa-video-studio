# kb-opa-design-system-chatbot — toàn văn tài liệu của nguồn `opa-design-system-chatbot`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/opa-design-system-chatbot/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: opa-design-system-chatbot/SKILL.md ===== -->

---
name: opa-design-system-chatbot
description: >-
  Hệ thống nhận diện thiết kế thương hiệu OPA (Design System tokens.ts, tokens.json, theme.css, tailwind.preset.js), giải phẫu linh vật Bò OPA 4 lớp SVG tách rời (opa-mascot-parts.svg), component hoạt ảnh React <MascotAvatar> 5 trạng thái cảm xúc (idle, thinking, responding, success, alert), giao diện khung chat <ChatWidget> hỗ trợ SSE streaming và bộ System Prompt chuẩn giọng điệu trợ lý AI OPA. Kích hoạt khi người dùng muốn xây dựng giao diện web/app/chatbot mang thương hiệu OPA, nhúng linh vật Bò OPA chuyển động vào React/HTML, hoặc cấu hình giọng điệu trả lời cho AI Chatbot OPA.
---

# OPA Design System & Chatbot Pack — Hệ Thống Thiết Kế, Linh Vật Bò SVG & Giao Diện Chatbot AI OPA

Skill này đóng gói toàn bộ **Design Tokens**, **Bộ Vector Linh Vật Bò OPA tách lớp**, **Các React Components (`MascotAvatar.tsx`, `ChatWidget.tsx`)** và **Hồ sơ nhân cách AI (`PROMPT.md`)** để triển khai nhất quán nhận diện thương hiệu OPA trên mọi sản phẩm Web, SaaS Dashboard, Landing Page và Chatbot.

---

## 1. Cấu Trúc Thư Mục Trong Skill

- **`tokens/`** — Bộ biến thiết kế chuẩn hóa đa nền tảng:
  - `tokens/tokens.ts` & `tokens/tokens.json`: Định nghĩa mã màu, thang chữ, khoảng cách, độ bo góc, bóng đổ và thông số lò xo chuyển động.
  - `tokens/theme.css`: Biến CSS gốc (`--opa-blue`, `--opa-navy`, `--opa-cream`, ...) kèm các lớp `@keyframes` diễn hoạt linh vật.
  - `tokens/tailwind.preset.js`: Cấu hình mở rộng cắm trực tiếp vào `tailwind.config.js`.
- **`assets/svg/`** — Bộ tài nguyên Vector chuẩn của Linh vật Bò OPA:
  - `assets/svg/opa-mascot-parts.svg`: File SVG tách riêng **4 nhóm giải phẫu độc lập** (`#sung-trai`, `#sung-phai`, `#tai-trai`, `#tai-phai`, `#dau-mat`, `#vong-mui`) để điều khiển hoạt ảnh từng bộ phận bằng CSS hoặc GSAP/Framer Motion.
  - `assets/svg/opa-mascot-blue.svg`, `opa-mascot-white.svg`, `opa-mascot-black.svg`: Các phiên bản đơn sắc và đầy đủ dùng cho nền sáng/tối.
- **`components/`** — Bộ linh kiện giao diện React / HTML dùng ngay:
  - `components/MascotAvatar.tsx`: Component hiển thị linh vật Bò OPA với **5 trạng thái cảm xúc sống động** (`idle`, `thinking`, `responding`, `success`, `alert`).
  - `components/ChatWidget.tsx`: Giao diện cửa sổ Chatbot hoàn chỉnh (nút nổi góc màn hình, khung hội thoại, bong bóng tin nhắn, hiệu ứng gõ chữ trực tiếp SSE streaming, nút gợi ý nhanh).
  - `components/preview.html`: Trang chạy thử trực tiếp trên trình duyệt không cần cài đặt bundler, cho phép bấm chuyển đổi từng trạng thái của linh vật và khung chat.
- **`references/`** — Tài liệu đặc tả kỹ thuật và System Prompt:
  - `references/DESIGN-SYSTEM.md` & `references/CLAUDE-design-system.md`: Quy chuẩn toàn diện về bảng màu, hệ thống chữ `Fraunces` + `Be Vietnam Pro` + `JetBrains Mono` và quy tắc không gian.
  - `references/CLAUDE-chatbot-pack.md` & `references/PROMPT-chatbot-pack.md`: Hướng dẫn tích hợp API hội thoại streaming và toàn văn **System Prompt** định hình giọng văn thông minh, thực chiến, gần gũi của trợ lý AI OPA.

---

## 2. Bảng Màu & Hệ Thống Chữ Cốt Lõi Của OPA (`tokens/tokens.ts`)

### Bảng màu thương hiệu (Brand Palette):
- **OPA Primary Blue (`#1B6EF3`):** Màu chủ đạo cho linh vật, nút hành động chính (Primary CTA), đường viền kích hoạt.
- **OPA Deep Navy (`#0B1F4D` / `#081226`):** Màu nền tối sâu và màu chữ tiêu đề độ tương phản cao.
- **OPA Electric Cyan (`#4DC4FF`):** Màu nhấn phụ cho hiệu ứng tia sáng AI, trạng thái đang suy nghĩ (`thinking`) và huy hiệu công nghệ.
- **OPA Warm Cream (`#F5F3EE` / `#FAF8F5`):** Màu nền sáng đặc trưng ấm áp, chống mỏi mắt và tạo sự khác biệt với nền trắng lạnh thông thường.
- **Semantic Colors:** Thành công `#10B981` (Emerald), Cảnh báo `#F59E0B` (Amber), Lỗi/Khẩn cấp `#EF4444` (Coral Red).

### Hệ thống Font chữ (Typography):
1. **Tiêu đề Điểm Nhấn (Display / Accent Serif):** `Fraunces` (ExtraBold Italic `800i`) — tạo cá tính biên tập sang trọng khi kết hợp cùng chữ không chân.
2. **Tiêu đề & Nội dung chính (Sans-serif UI):** `Be Vietnam Pro` hoặc `Plus Jakarta Sans` (`400`, `500`, `600`, `700`, `800`) — tối ưu hoàn hảo cho dấu tiếng Việt.
3. **Số liệu & Mã lệnh (Monospace):** `JetBrains Mono` (`500`, `700`).

---

## 3. Năm Trạng Thái Hoạt Ảnh Của `<MascotAvatar />`

Khi tích hợp `components/MascotAvatar.tsx` vào ứng dụng hoặc Chatbot, truyền prop `state` tương ứng với luồng xử lý của AI:
1. **`state="idle"` (Đứng chờ tự nhiên):** Đầu nhấp nhô nhẹ theo nhịp thở (`3.2s/chu kỳ`), chớp mắt ngẫu nhiên mỗi `3.5–5s`, tai khẽ cử động nhẹ.
2. **`state="thinking"` (Đang phân tích dữ liệu):** Đầu nghiêng nhẹ `6°`, hai sừng phát sáng nhịp xung xanh `#4DC4FF`, mắt nhìn lên hướng suy tư, tai vểnh nhịp nhàng.
3. **`state="responding"` (Đang trả lời người dùng):** Linh vật gật nhẹ theo nhịp chữ chảy ra (`streaming tokens`), vòng mũi ánh sáng nhấp nháy đồng bộ.
4. **`state="success"` (Hoàn thành xuất sắc):** Nhảy bật nhẹ lên cao (`bounce overshoot`), hai tai vẫy vui vẻ, viền hào quang xanh ngọc `#10B981`.
5. **`state="alert"` (Cảnh báo / Phát hiện vấn đề):** Rung lắc ngang ngắn (`shake`), sừng chuyển sắc cam/đỏ cảnh báo để thu hút sự chú ý ngay lập tức.

---

## 4. Tích Hợp Nhanh Vào Dự Án React / Next.js

1. Sao chép thư mục `tokens/`, `assets/svg/` và `components/` vào `src/` của dự án.
2. Nhúng `tokens/theme.css` vào `app/layout.tsx` (hoặc `main.tsx`) và thêm `tokens/tailwind.preset.js` vào mảng `presets` trong `tailwind.config.js`.
3. Khởi tạo `<ChatWidget />` và kết nối endpoint streaming theo mẫu hướng dẫn trong `references/CLAUDE-chatbot-pack.md` cùng System Prompt trong `references/PROMPT-chatbot-pack.md`.

<!-- ===== /file: opa-design-system-chatbot/SKILL.md ===== -->

<!-- ===== file: opa-design-system-chatbot/references/CLAUDE-chatbot-pack.md ===== -->

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

<!-- ===== /file: opa-design-system-chatbot/references/CLAUDE-chatbot-pack.md ===== -->

<!-- ===== file: opa-design-system-chatbot/references/CLAUDE-design-system.md ===== -->

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

<!-- ===== /file: opa-design-system-chatbot/references/CLAUDE-design-system.md ===== -->

<!-- ===== file: opa-design-system-chatbot/references/DESIGN-SYSTEM.md ===== -->

# OPA Brand & Design System Guidelines

Nguồn sự thật duy nhất cho nhận diện thương hiệu, hệ thống thiết kế và tài nguyên logo của **OverPowers Agency (OPA)**.

---

## 1. Đóng gói tài nguyên Logo & Mascot

Tất cả tài nguyên đã được chuẩn hóa trong thư mục `./assets/`:

```text
assets/
├── svg/
│   ├── opa-mascot-blue.svg        # Bản chính màu xanh (#0068FF), viewBox 2000x2000
│   ├── opa-mascot-white.svg       # Bản trắng (#FFFFFF) dùng trên nền xanh hoặc nền tối
│   ├── opa-mascot-black.svg       # Bản đen (#0A0A0A) dùng cho in ấn đơn sắc hoặc nền sáng
│   └── opa-mascot-parts.svg       # Bản tách 4 phần vector (sừng L, sừng R, mõm chữ U, khe trán)
├── png/
│   ├── OPA-V4-A-Core-blue-2000.png   # PNG trong suốt 2000x2000 (#0068FF)
│   ├── OPA-V4-A-Core-white-2000.png  # PNG trong suốt 2000x2000 (#FFFFFF)
│   └── OPA-V4-A-Core-black-2000.png  # PNG trong suốt 2000x2000 (#0A0A0A)
└── pdf/
    └── OPA — Biểu tượng 2D V4.pdf    # Master vector PDF gốc
```

### Cấu trúc hình học (Mascot Anatomy)
- **Kích thước gốc**: `viewBox="0 0 2000 2000"`, Bounding Box `[306.31, 367.33, 1693.69, 1632.8]`.
- **4 thành phần vector (`opa-mascot-parts.svg`)**:
  1. `c-muzzle`: Khối mõm bo tròn hình chữ U (tượng trưng cho cái phễu hứng mọi cơ hội, không bỏ sót khách).
  2. `a-horn-left`: Sừng trái (tâm xoay pivot: `569.16, 901.07`).
  3. `b-horn-right`: Sừng phải (tâm xoay pivot: `1430.84, 901.07`).
  4. `d-nostril-gap`: Khe trán / 2 lỗ thở giữa đỉnh mõm.

---

## 2. Quy tắc màu sắc (Color Tokens)

| Tên màu | Mã Hex | Mục đích sử dụng |
|---|---|---|
| **OPA Blue (Chủ đạo)** | `#0068FF` | Màu nhận diện chính, nút bấm chính, điểm nhấn |
| **OPA Blue Dark** | `#003C99` | Trạng thái hover, đường viền đậm, nền phụ tối |
| **OPA Blue Light** | `#E6F0FF` | Nền thẻ phụ, bong bóng tin nhắn, highlight dịu |
| **Neutral Black** | `#0A0A0A` | Nền tối (dark mode), chữ tiêu đề trên nền sáng |
| **Neutral White** | `#FFFFFF` | Nền sáng, chữ trên nền xanh hoặc nền tối |
| **Neutral Border** | `#E2E8F0` | Đường kẻ, viền card, ngăn cách nội dung |
| **Neutral Surface** | `#F8FAFC` | Nền khối xám nhẹ cho UI/Dashboard |

### Quy tắc tương phản bắt buộc:
- Mascot trắng **chỉ** xuất hiện trên nền xanh `#0068FF` hoặc nền tối `#0A0A0A`.
- Mascot xanh `#0068FF` xuất hiện trên nền trắng hoặc nền nhạt `#E6F0FF`.
- Chữ trên nền xanh luôn là màu trắng `#FFFFFF`.
- Tuyệt đối **không** dùng gradient cầu vồng, không đổ bóng blur lòe loẹt, không 3D kim loại bóng bẩy.

---

## 3. Kiểu chữ (Typography)

1. **Font chính (Primary Font)**: `"Be Vietnam Pro"` (Google Fonts).
   - Đảm bảo hiển thị chuẩn các ký tự tiếng Việt có dấu (`ầ, ổ, ữ, đ...`) không bị xén mũ.
   - Tiêu đề (Headings/Display): ExtraBold (800) hoặc Bold (700).
   - Nội dung (Body/UI): Medium (500) hoặc Regular (400).
2. **Font nhấn (Accent Font)**: `"Fraunces"` Italic 800.
   - Dùng độc quyền cho cụm từ khóa quan trọng cần nhấn mạnh (ví dụ: *không bỏ sót khách*, *vận hành AI*).

---

## 4. Chuyển động (Motion Principles)

- **Đặc trưng**: Dứt khoát, chắc nịch, có lực đẩy (charge) và độ bật nảy cơ học.
- **Easing vào cảnh**: `cubic-bezier(0.2, 0.8, 0.2, 1)`.
- **Easing ra cảnh**: `cubic-bezier(0.6, 0, 0.8, 0.2)`.
- **Bật nảy (Spring Pop)**: Damping `12`, stiffness `100`, mass `1` (nảy rõ 1 nhịp rồi đứng vững, không bồng bềnh).

---

## 5. Quy tắc cấm kỵ (Don'ts)

1. Không bóp méo tỷ lệ width/height của logo/mascot.
2. Không vẽ thêm mắt, miệng cười hay chi tiết cute hoạt hình vào Bò OPA.
3. Không tự ý đổi mã màu xanh `#0068FF` sang xanh cyan hoặc xanh tím.

<!-- ===== /file: opa-design-system-chatbot/references/DESIGN-SYSTEM.md ===== -->

<!-- ===== file: opa-design-system-chatbot/references/PROMPT-chatbot-pack.md ===== -->

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

<!-- ===== /file: opa-design-system-chatbot/references/PROMPT-chatbot-pack.md ===== -->
