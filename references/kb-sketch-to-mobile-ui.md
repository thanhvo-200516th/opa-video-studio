# kb-sketch-to-mobile-ui — toàn văn tài liệu của nguồn `sketch-to-mobile-ui`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/sketch-to-mobile-ui/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: sketch-to-mobile-ui/SKILL.md ===== -->

---
name: sketch-to-mobile-ui
description: >-
  Chuyển đổi ảnh phác thảo tay (wireframe/sketch vẽ trên giấy, iPad hoặc bảng trắng) thành thiết kế giao diện Mobile App & SaaS UI hoàn chỉnh và bảng tách lớp nhân vật 2D/3D (CS01..CS05). Bao gồm cấu trúc Prompt 7 phần, bộ preset màu/typography theo ngành nghề, và quy trình xuất file vector .svg có định danh từng nhóm <g id="..."> qua Adobe Illustrator (Release to Layers) để đưa vào After Effects diễn hoạt độc lập từng nút bấm, thẻ UI và khớp xương nhân vật. Kích hoạt khi người dùng muốn biến ảnh vẽ tay/wireframe thành UI chuyên nghiệp, viết prompt tạo giao diện từ sketch, hoặc tách lớp UI/nhân vật từ SVG sang After Effects.
---

# Sketch to Mobile UI & Character Rigging — Từ Phác Thảo Tay Sang Giao Diện & Nhân Vật Chuyển Động

Skill này giúp chuyển hóa các bản vẽ phác thảo tay (wireframe trên giấy, sổ tay, bảng trắng) thành giao diện ứng dụng Mobile/Web sắc nét và nhân vật 2D/3D tách rời từng bộ phận, sẵn sàng đưa thẳng vào **Adobe Illustrator -> After Effects** để làm hoạt họa (Motion Graphics).

---

## Chạy trên máy Linux này

- Trên Linux dùng EffectCraft 0.17 (`~/.local/bin/effectcraft`) thay After Effects và bỏ được bước Illustrator: import thẳng file `.svg` (vào dạng footage) → Layer > Create Shapes from Vector Layer; mỗi `<g id>` thành một nhóm shape cùng tên (đã thử với `opa-mascot-parts.svg` ngày 2026-10-29: `mascot` › `a-horn-left`, `b-horn-right`, `c-muzzle`, `d-nostril-gap`).

---

## 1. Cấu Trúc Thư Mục Trong Skill

- **`SKILL.md`** — Tài liệu hướng dẫn công thức Prompt 7 phần chuyển đổi Sketch sang Mobile UI, bảng Preset theo ngành nghề và quy trình xử lý các tình huống đặc biệt.
- **`references/sketch-to-ui-va-nhan-vat.md`** — Quy trình kỹ thuật chi tiết nối tiếp từ thiết kế sang chuyển động:
  - Chuẩn bị cấu trúc thẻ `<g id="ten_layer">` trong file `.svg`.
  - Quy trình **Adobe Illustrator (`Release to Layers (Sequence)`) -> Lưu `.ai` -> Import vào After Effects (`Composition - Retain Layer Sizes`) -> `Create Shapes from Vector Layer`**.
  - Bộ 5 bản thiết kế nhân vật (`CS01..CS05`) phục vụ tách khớp Rigging 2D (`Puppet Pin` / `Null Parent`) và dựng khối 3D.

---

## 2. Công Thức Prompt 7 Phần (Biến Bản Vẽ Tay Thành Mobile UI)

Khi người dùng cung cấp ảnh chụp bản vẽ tay (sketch/wireframe), luôn xây dựng Prompt tạo ảnh UI theo đúng **7 khối tuần tự** sau:

1. **Tuyên bố chuyển đổi (Transformation Statement):**
   - Nêu rõ loại ứng dụng và mục tiêu: *"Transform this hand-drawn wireframe sketch into a high-craft, production-ready [Loại App] mobile UI design..."*
2. **Tuân thủ bố cục gốc (Layout Fidelity):**
   - Giữ đúng vị trí, thứ tự từ trên xuống dưới, tỷ lệ các ô và luồng điều hướng như trong bản vẽ tay; tự động căn thẳng lưới (`8px grid`), cân đối khoảng trắng (`padding/margin`) chuẩn hệ điều hành.
3. **Thẩm mỹ & Ngôn ngữ thiết kế (Design Aesthetic & Platform):**
   - Chỉ định rõ nền tảng (**iOS 18 Human Interface Guidelines** hoặc **Material Design 3**), chế độ sáng/tối (**Light Mode** tinh khiết hoặc **Dark Mode** chiều sâu), độ bo góc (`border-radius: 16px–24px`), đổ bóng mềm đa tầng.
4. **Bảng màu chủ đạo (Color Palette):**
   - Khai báo mã HEX cụ thể cho: *Background Surface*, *Elevated Card*, *Primary Brand Accent*, *Secondary Accent*, *Text Primary*, *Text Muted*, và *Semantic Status (Success/Warning/Danger)*.
5. **Hệ thống chữ (Typography Hierarchy):**
   - Định nghĩa rõ: * Font không chân hiện đại* (`SF Pro Display`, `Plus Jakarta Sans`, `Be Vietnam Pro`, `Inter`), phân cấp rõ *Header*, *Section Title*, *Card Metric*, *Body* và *Caption*.
6. **Chi tiết hóa từng thành phần (Component Detailing):**
   - Biến các nét gạch/ô vuông nguệch ngoạc trong bản vẽ thành linh kiện thật:
     - Hình tròn có chữ X → Avatar người dùng thật hoặc linh vật 3D.
     - Đường zích zắc → Biểu đồ đường mượt có vùng phủ gradient bên dưới.
     - Các dòng gạch ngang → Văn bản có nội dung thực tế, có nghĩa (không dùng chữ giả vô nghĩa).
     - Ô vuông nhỏ → Bộ icon đồng bộ nét (`2px stroke` hoặc `duotone`).
7. **Quy cách hiển thị đầu ra (Presentation Format):**
   - Xuất dạng **Flat UI Screen** thẳng góc (nếu cần cắt lớp đưa vào After Effects) hoặc đặt trong khung **iPhone 16 Pro Titanium Mockup** trên nền studio tối giản (nếu dùng để trình chiếu).

---

## 3. Bảng Preset Thẩm Mỹ Theo Ngành Nghề

| Ngành / Loại App | Chế độ nền | Màu chủ đạo (HEX) | Phong cách đặc trưng |
|---|---|---|---|
| **AI SaaS / Chatbot (OPA)** | Light / Dark | `#1B6EF3`, `#4DC4FF`, `#F5F3EE` | Bề mặt kem ấm hoặc xanh đen sâu, thẻ bo tròn `20px`, viền mảnh `1px`, linh vật Bò xanh |
| **Fintech / Ngân hàng số** | Dark / Clean Light | `#0A2540`, `#00D4B2`, `#635BFF` | Số liệu tài chính rõ nét, biểu đồ tăng trưởng phát sáng nhẹ, cảm giác bảo mật cao |
| **E-Commerce / Mua sắm** | Light Mode | `#FF4D2D`, `#111827`, `#F9FAFB` | Ảnh sản phẩm nổi bật, thẻ giá rõ ràng, nút CTA độ tương phản cao |
| **Health & Fitness** | Light / Dark | `#10B981`, `#3B82F6`, `#F3F4F6` | Vòng tròn tiến độ (Activity Rings), màu sắc tươi mới năng lượng |
| **EdTech / Học tập** | Warm Light | `#6366F1`, `#F59E0B`, `#FFFBEB` | Thân thiện, có tiến trình bài học, huy hiệu gamification và linh vật đồng hành |

---

## 4. Quy Trình Tách Lớp Vector (`.svg` -> `.ai` -> After Effects)

Khi cần đưa giao diện hoặc nhân vật vào **After Effects** để diễn hoạt từng phần tử (xem chi tiết tại `references/sketch-to-ui-va-nhan-vat.md`):

1. **Định danh từng nhóm trong SVG:**
   - Mọi thành phần cần chuyển động độc lập phải nằm trong một thẻ `<g id="...">` riêng biệt (ví dụ: `<g id="ui_header">`, `<g id="card_revenue">`, `<g id="btn_cta">`, hoặc với nhân vật: `<g id="dau">`, `<g id="mat_trai">`, `<g id="canh_tay_phai">`, `<g id="ban_tay_phai">`).
2. **Tách lớp trong Adobe Illustrator:**
   - Mở file `.svg` bằng Illustrator → Mở bảng **Layers** → Chọn layer tổng → Nhấn biểu tượng menu góc phải bảng Layers → Chọn **`Release to Layers (Sequence)`**.
   - Kéo các sub-layer vừa tách ra ngoài thành **Top-level Layers** và đặt lại tên đúng chuẩn → Lưu thành file **`.ai` (Adobe Illustrator)**.
3. **Đưa vào After Effects & Chuyển thành Shape Layer:**
   - Trong After Effects: `File -> Import -> File...` → Chọn file `.ai` → Ở mục **Import Kind**, bắt buộc chọn **`Composition - Retain Layer Sizes`**.
   - Mở comp vừa tạo → Chọn các layer vector `.ai` cần uốn/biến hình → Chuột phải chọn **`Create -> Create Shapes from Vector Layer`**.
   - Đặt lại **Anchor Point** về đúng khớp xoay (vai, khuỷu tay, cổ tay cho nhân vật; hoặc tâm thẻ cho UI) và gắn dây cha–con (`Parent & Link`).

<!-- ===== /file: sketch-to-mobile-ui/SKILL.md ===== -->

<!-- ===== file: sketch-to-mobile-ui/references/sketch-to-ui-va-nhan-vat.md ===== -->

# Thiết kế Giao diện UI (Sketch-to-UI) & Nhân vật 2D–3D Đưa Vào After Effects

Tài liệu tham chiếu này hợp nhất toàn bộ quy trình từ skill `sketch-to-mobile-ui` và hệ thống thiết kế nhân vật / thành phần `Motion Omi` vào chung gói skill **`after-effects`**.

---

## Phần A — Chuyển bản vẽ phác thảo (Sketch / Wireframe) thành Giao diện UI & Đưa vào AE

### 1. Giải phẫu cấu trúc Prompt 7 phần (Role – Task – Constraint)

| Phần | Tên mục | Tác dụng chính |
|---|---|---|
| **Mở đầu** | **Role Prompting** | Định vị AI là nhà thiết kế UI/UX & Product Designer chuyên nghiệp để áp dụng phân cấp thị giác, khoảng trắng và bố cục chuẩn. |
| **Mục 1** | **Understand the Sketch** | Khóa bố cục: dùng bản vẽ tay làm khung tham chiếu chính (*primary structural reference*), giữ nguyên ý đồ và vị trí các phần tử. |
| **Mục 2** | **Visual Design Style** | Định nghĩa **Design System**: màu nền, màu thẻ, màu nhấn, bo góc, đổ bóng mềm (hoặc phẳng theo BRAND-SPEC) và phong cách ảnh minh họa. |
| **Mục 3** | **Transform Sketches into UI Components** | Ánh xạ nét vẽ thô thành Component chuẩn: nút bấm hình viên thuốc (pill-shaped), thẻ thông tin, biểu đồ, bộ chọn, nút CTA chính. Kèm câu khóa *"Only include components that are relevant to the uploaded sketch"* để cấm AI tự bịa thêm phần tử. |
| **Mục 4** | **Layout and Composition** | Quy định khung hình đầu ra: đặt trong màn hình nhìn thẳng (*straight-on mockup*) hoặc bảng giao diện SaaS / POS theo đúng tỷ lệ cần dựng. |
| **Mục 5** | **Product Accuracy and Text** | **Negative Prompt chống lỗi AI**: cấm viết chữ vô nghĩa (*random letters*), cấm làm méo nút (*distorted buttons*), ép dùng số liệu hợp lý và icon đồng bộ. |
| **Mục 6 & Kết** | **Final Quality & Core Rule** | Đảm bảo chất lượng đầu ra đạt chuẩn Figma / Portfolio chuyên nghiệp, giữ nguyên ý tưởng gốc của bản phác thảo. |

### 2. Prompt Template Đa Năng (Tùy biến cho mọi ngành hàng & SaaS/App)

```text
Act as a world-class UI/UX designer and product designer. Transform my uploaded hand-drawn wireframe or rough app sketch into a polished, premium, production-quality UI design.

1. Understand the Sketch
Carefully analyze the uploaded sketch and understand its layout, components, labels, buttons, and intended functionality. Use the sketch as the primary structural reference. Preserve its original concept and layout while upgrading the visual design.

2. Visual Design Style
- Create a modern, premium [NGÀNH NGHỀ APP: e.g., SaaS AI Sales Chat & Pancake POS / Fintech banking / E-commerce fashion] interface.
- Use a [MÀU NỀN: e.g., clean flat background (#FFFFFF or #0A0A0A) / sleek dark-mode background (#0F172A)] with [MÀU THẺ: e.g., clean structured cards] and [MÀU NHẤN: e.g., electric blue (#0068FF)].
- Apply rounded corners, elegant sans-serif typography (Be Vietnam Pro / Inter), and balanced spacing.
- Use [HÌNH ẢNH MINH HỌA: e.g., clean product cards, order status badges, or studio product shots].
- Maintain a professional Figma-quality aesthetic with clear visual hierarchy.

3. Transform Sketches into UI Components
Convert the rough wireframe elements into polished interface components, including:
- Interactive-looking buttons, tabs, and pill-shaped controls.
- [THÀNH PHẦN ĐẶC THÙ 1: e.g., Live customer chat bubbles & AI instant reply cards]
- [THÀNH PHẦN ĐẶC THÙ 2: e.g., Real-time inventory stock badges & bank transfer bill verification [OK]]
- [THÀNH PHẦN ĐẶC THÙ 3: e.g., Automated POS order creation card (#PK8921)]
- A prominent primary action button, such as “[NÚT HÀNH ĐỘNG CHÍNH: e.g., Kết nối Pancake ngay / Confirm Order].”
Only include components that are relevant to the uploaded sketch. Do not force every component into every screen.

4. Layout and Composition
Present the finished UI in a clean, straight-on screen mockup. Keep the interface readable, aligned, visually balanced, and consistent.

5. Product Accuracy and Text
Preserve the purpose and meaning of the original sketch. Use legible interface text, realistic numbers/metrics, consistent icons, and correctly aligned elements. Do not generate random letters, distorted buttons, unnecessary labels, or unrelated UI components.

6. Final Quality
The final result must look like a premium product concept designed by an experienced UI/UX designer: clean, modern, visually impressive, realistic, and ready for motion graphics production.
```

### 3. Bảng Presets Thay Nhanh Theo Ngành

| Ngành (Category) | Màu nền & Thẻ (Style) | Màu nhấn (Accent) | Các Component đặc thù (Mục 3) |
|---|---|---|---|
| **OPA SaaS / Pancake POS (theo BRAND-SPEC)** | Nền phẳng 5 màu (`#FFFFFF`, `#E6F0FF`, `#0A0A0A`), không glow/gradient | Xanh OPA (`#0068FF`), Xanh đêm (`#003C99`), Đỏ cảnh báo nhỏ (`#E5484D`) | Bong bóng chat khách & AI, thẻ tồn kho POS, thẻ xác minh bill `[OK]`, mã đơn `#PK8921`. |
| **Fintech / Crypto** | Dark mode (`#0B0F19`), thẻ Glassmorphism mờ | Xanh Neon (`#10B981`) hoặc Tím (`#6366F1`) | Thẻ số dư (Balance card), biểu đồ đường (Line chart), lịch sử giao dịch, nút *Send / Receive*. |
| **Fitness / Health** | Nền tối hoặc trắng xám sạch, thẻ bo tròn lớn | Cam năng động (`#F97316`) hoặc Xanh lá | Vòng tròn tiến độ (Activity rings), biểu đồ nhịp tim/calo, danh sách bài tập, nút *Start Workout*. |
| **E-Commerce / Thời trang** | Nền trắng tinh (`#FFFFFF`), thẻ xám nhạt (`#F8FAFC`) | Đen sang trọng (`#111827`) hoặc Vàng đồng | Lưới sản phẩm (Product grid), bộ chọn màu/size, giỏ hàng, đánh giá sao, nút *Add to Cart*. |
| **Booking / Du lịch** | Nền trắng kem ấm, thẻ ảnh tràn viền | Xanh biển (`#0EA5E9`) hoặc Đỏ san hô | Thanh tìm kiếm ngày/địa điểm, thẻ khách sạn kèm giá/đánh giá, bản đồ vị trí, nút *Book Now*. |

### 4. Ba cách đưa Giao diện UI vào After Effects

1. **Cách 1 — Biến hình từ nét vẽ tay thành App thật (`Sketch-to-Real Transition`)**:
   - Đưa cả **Layer Ảnh Vẽ Tay** (nằm dưới) và **Layer Ảnh UI Hoàn Thiện** (nằm trên) vào chung một Comp trong After Effects, căn chồng khít nhau.
   - Dùng `Linear Wipe` hoặc `Mask Path` quét từ trên xuống để nét vẽ chì biến thành giao diện thật, hoặc tách từng cụm (`Header`, `Card`, `Button`) bật lên bằng lò xo (`O.popScale`).
2. **Cách 2 — Gắn giao diện vào Màn hình / Thẻ nổi (`Screen Placeholder & Z-Depth`)**:
   - Đưa các màn hình đã sinh đồng bộ vào comp giữ chỗ (`Screen_Placeholder`, `06_Scene` chat cards).
   - Với video không bị giới hạn phẳng bởi BRAND-SPEC, có thể bật `3D Layer`, xoay nghiêng màn hình và đẩy các thẻ con (`Card`, `Badge`, `Button`) lên trục `Z = -20px … -50px` để tạo chiều sâu Parallax khi máy quay lia qua.
3. **Cách 3 — Xuất SVG tách lớp → Illustrator → After Effects (`SVG Release to Layers`)**:
   - Khi sinh giao diện bằng AI (Claude / ChatGPT / Gemini), nối thêm đoạn lệnh sau vào cuối prompt:
     ```text
     AFTER EFFECTS LAYER EXPORT INSTRUCTION:
     In addition to the visual design, generate a clean, production-ready SVG code (viewBox="0 0 390 844" or "0 0 1920 1080") of this UI screen so I can animate it in Adobe After Effects.
     - Group every distinct UI component into separate, clearly named <g id="..."> groups (e.g., id="header_bar", id="address_card", id="product_card_1", id="cta_button").
     - Separate button backgrounds and text into distinct elements so they can be keyframed independently.
     - Use clean vector paths, standard rounded rectangles (<rect rx="...">), and system fonts.
     ```
   - Mở file `.svg` trong **Adobe Illustrator** → bảng **Layers** → chọn **Release to Layers (Sequence)** → lưu thành `.ai`.
   - Trong After Effects: `File > Import > File...` → chọn file `.ai` với `Import Kind = Composition` và `Footage Dimensions = Layer Size` (hoặc dùng `<VD-A>\tools\svg_to_ae.py` để đổi trực tiếp đường path SVG sang Shape Layer của AE).

---

## Phần B — Thiết kế Nhân vật 2D–3D, Chân dung & Bộ phận Tách Lớp (Motion Omi)

> **Lưu ý luật thương hiệu (Sổ tay mục 7.8):**
> - Với **Video OPA chính thức theo `BRAND-SPEC.md`**: Bò OPA không mắt, không miệng, không tay chân, chỉ dùng 5 màu OPA và chỉ co giãn đều (không squash & stretch bóp méo).
> - Quy trình `CS01..CS05` dưới đây áp dụng cho các dự án nhân vật 2D–3D có mắt/biểu cảm/sừng rời (như bản thử nghiệm Motion Omi) hoặc khi Minh duyệt rõ ở cổng G0.

### 1. Bộ 5 Tấm Character Sheet (`CS01` – `CS05`) chuẩn Rigging AE

| Mã tấm | Tên tấm | Nội dung & Mục đích trong After Effects |
|---|---|---|
| **CS01** | **Character Turnaround Sheet (4 góc)** | 4 góc nhìn chuẩn (`Front 0°`, `Three-Quarter Left 3/4`, `Side Profile 90°`, `Back View 180°`) đứng thẳng hàng ngang, đồng nhất 100% tỷ lệ để làm mẫu gốc (*Master Identity Reference*). |
| **CS02** | **Facial Expression & Emotion Sheet** | 6 trạng thái biểu cảm (`Happy`, `Focused Scanning`, `Friendly Wink`, `Surprised Alert`, `Proud Success [OK]`, `Thinking Processing`) để chuyển đổi trạng thái mặt theo tình huống kịch bản. |
| **CS03** | **Separated Rigging Parts / Sprite Sheet** | Tách rời từng bộ phận có khoảng cách rõ ràng trên nền phẳng tương phản cao để cắt PNG/SVG đưa vào AE: Thân chính (`PART_1_BODY`), Sừng/Tay trái (`PART_2_LEFT`), Sừng/Tay phải (`PART_3_RIGHT`), và các bộ biểu cảm rời (`PART_4A..4D`). |
| **CS04** | **Action Pose Library (4 tư thế)** | 4 tư thế diễn xuất chính tương ứng với kịch bản: (1) Đón tin nhắn, (2) Quét tồn kho & bảng giá, (3) Xác nhận đơn hàng thành công, (4) Chào kết màn CTA. |
| **CS05** | **Anchor Point & Proportion Blueprint** | Bản vẽ kỹ thuật đánh dấu chính xác vị trí đặt tâm xoay (`Anchor Point`) cho từng bộ phận khi gắn parent trong After Effects. |

### 2. Quy tắc đặt Tâm Xoay (`Anchor Point`) khi Rig nhân vật & UI trong AE

1. **Thân nhân vật (`Body`)**: Đặt `Anchor Point` tại **Chân Đế (`[50%, 100%]`)** để khi phóng to/thu nhỏ hoặc nhún từ mặt sàn lên, chân đế không bị trượt khỏi mặt đất.
2. **Sừng / Cánh tay / Tai rời (`Horn_L`, `Horn_R`)**: Gắn `Parent` vào layer `Body`, đặt `Anchor Point` ngay tại **Gốc Khớp tiếp giáp với thân** (ví dụ `[22.6%, 42.1%]` và `[77.4%, 42.1%]`) để khi xoay `Rotation ±12°` không bị hở khớp.
3. **Bong bóng Chat (`Chat_Bubble`)**: Đặt `Anchor Point` tại **Đầu nhọn đuôi bong bóng** để khi bung tỉ lệ `Scale 0% → 109.5% → 100%` (lò xo mục 5.4), bong bóng mọc ra tự nhiên từ phía avatar người gửi.
4. **Chân dung 3D trong các comp giữ chỗ (`01_Person_Holder` … `08_Person_Holder`)**:
   - Tạo bộ chân dung đồng nhất về ánh sáng studio và kích thước vuông (`1000×1000 px`).
   - Khi thay vào comp giữ chỗ của template bằng script, luôn đặt `comp.duration = 10.0` và `layer.outPoint = 10.0` cho cả comp `Holder` lẫn comp `Person` bao ngoài để ảnh không bị tắt sớm giữa cảnh.

<!-- ===== /file: sketch-to-mobile-ui/references/sketch-to-ui-va-nhan-vat.md ===== -->
