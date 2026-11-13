# kb-ae-logo-intro-reveal — toàn văn tài liệu của nguồn `ae-logo-intro-reveal`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/ae-logo-intro-reveal/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: ae-logo-intro-reveal/SKILL.md ===== -->

---
name: ae-logo-intro-reveal
description: >-
  Thay thế logo thương hiệu, đồng bộ bảng màu nhận diện (Brand Colors), tinh chỉnh bộ điều khiển (Control Panel / Essential Graphics / Slider / Checkbox) và kết xuất video Tech Logo Intro / Brand Reveal (10s–16s) trên Adobe After Effects từ các bộ template công nghệ Envato (Abstract Techno, Sci-Fi HUD, Digital Coding, Blueprint Logo Reveal, NH2GY3D, Futuristic Hi-Tech A7XZTEC). Kích hoạt khi người dùng muốn làm video intro logo công nghệ trên AE, thay logo/đổi màu thương hiệu trong template intro AE, hoặc chạy script tự động hóa Blueprint/Hi-Tech Logo Reveal.
---

# AE Logo Intro Reveal — Sản Xuất & Tùy Biến Intro Logo Công Nghệ Trên After Effects

Skill này tổng hợp toàn bộ quy trình chuẩn, hồ sơ kỹ thuật của các mẫu Intro Logo công nghệ hàng đầu từ Envato và bộ công cụ script tự động hóa (`.jsx` + `.py`) để biến đổi bất kỳ template Logo Reveal nào thành sản phẩm mang nhận diện thương hiệu riêng (như OPA `#1B6EF3`).

---

## Chạy trên máy Linux này

- Python: `~/.venvs/video-skills/bin/python` (máy không có lệnh `python`/`py`; venv có numpy, scipy, matplotlib, opencv, scikit-image, Pillow, fontTools, resvg-py, faster-whisper). Lệnh `python …` trong tài liệu chạy bằng đường dẫn này.
- Đường dẫn Windows trong tài liệu đã đổi sang Linux: `F:\` → `/media/vmiz/Over Powers/`, `D:\` → `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/` (bản sao lưu ổ D ngày 2026-10-28). Ổ USB `Over Powers` phải đang gắn. `E:\` không có trên máy; tài nguyên thay thế ở `/home/vmiz/Thanh/Media/TNEDIT/` (`02_SFX`, `08_Nhac_Nen`, `01_Font`, `06_B-Roll`…).
- Trên Linux dùng **EffectCraft 0.17** (`~/.local/bin/effectcraft`) thay After Effects: chạy ExtendScript theo mô hình đối tượng AE (`app.version` báo `26.0`), ScriptUI, `$.evalFile`; `app.run(id, params)` gọi mọi lệnh của app. Chạy script: File > Scripts > Run Script File… (script đặt trong `~/.config/effectcraft/Scripts/` hiện ở File > Scripts). Script ghi file cần bật Settings > Scripting > Allow Scripts to Write Files (máy này đang tắt). EffectCraft **không mở được `.aep`** (chỉ `.ecproj`); không có `aerender`/headless.
- Template Envato (`.aep`: Blueprint, NH2GY3D, HUD…) và các script sửa chúng (`ADAPT_*`, `FINAL_POLISH*`, `INSPECT_*`, `LOAD_*`, `RESET_*`, `RUN_*`, `TEST_COLOR`, `TRACE_NATIVE_COLOR`) chỉ dùng được trên After Effects. `Create_Futuristic_HiTech_Logo_A7XZTEC.jsx` dựng từ đầu nên chạy được trên EffectCraft (đã cài vào File > Scripts; lấy `Logoweb.png` từ USB, lưu `.ecproj` cạnh logo). Lưu ý: camera gắn vào null đang xoay ở giây 0 nên khung cuối bị nghiêng, khác video mẫu (EffectCraft bù parent giống AE).

---

## 1. Cấu Trúc Thư Mục Trong Skill

- **`references/`** — Hệ thống tài liệu hướng dẫn chi tiết từng dòng template:
  - `references/HUONG-DAN-3-TEMPLATES-OPA.md`: Hướng dẫn hoàn chỉnh cho 3 mẫu chủ lực:
    1. **Template 1 — Abstract Techno Logo Reveal** (`1920x1080`, `29.97 fps`, `11s`, Không cần plugin ngoài, hỗ trợ xuất nền trong suốt Alpha).
    2. **Template 2 — Sci-Fi HUD Logo Reveal** (`1920x1080`, `29.97 fps`, `10s`, hiệu ứng vòng xoay HUD tương lai + tia sáng Saber).
    3. **Template 3 — Digital Coding Logo** (`3840x2160` 4K & Full HD, `30 fps`, `12s`, ma trận mã lệnh số hóa hội tụ thành logo).
  - `references/HUONG-DAN-BLUEPRINT-OPA.md` & `references/PHAN-TICH-VIDEO-VA-KICH-BAN-BLUEPRINT.md`: Quy trình tùy biến mẫu **Blueprint Logo Reveal** (bản vẽ kỹ thuật 3D lưới trục tọa độ, thước đo kỹ thuật, đổi toàn bộ dải màu sang Xanh OPA `#1B6EF3` / `#0A1931`).
  - `references/HUONG-DAN-OPA-NH2GY3D.md`: Hướng dẫn tùy biến mẫu **NH2GY3D Tech Logo** từ bước thay logo vector đến bước render.
  - `references/NGHIEN-CUU-OPA-TECH.md` & `references/templates.json`: Báo cáo nghiên cứu, chấm điểm và phân loại các mẫu Intro công nghệ theo phong cách (HUD, Particle, Blueprint, Circuit, Clean Corporate).
  - `references/README-THAY-PLACEHOLDER-16S.md`: Quy trình thay nhanh 8 Placeholder cho kịch bản **Brand Film 16 giây** (`1920x1080` & `1080x1920`).
- **`scripts/`** — Bộ công cụ tự động hóa bằng ExtendScript & Python:
  - `scripts/ADAPT_BLUEPRINT_OPA.jsx` & `scripts/ADAPT_BLUEPRINT_OPA.template.jsx`: Tự động nạp logo, đổi câu tagline và cập nhật màu toàn bộ hệ thống lưới Blueprint.
  - `scripts/TRACE_NATIVE_COLOR.jsx` & `scripts/TEST_COLOR.jsx`: Dò tìm mọi thuộc tính màu (`Fill`, `Stroke`, `Ramp`, `Tint`, `Tritone`, `Glow`, `CC Toner`) nằm ẩn sâu trong các precomp của template.
  - `scripts/apply_brand_colors.py`: Script Python đồng bộ mã màu thương hiệu vào script AE.
  - `scripts/FINAL_POLISH.jsx`, `scripts/INSPECT_CURRENT_TEMPLATE.jsx`, `scripts/LOAD_BRAND_AND_SAVE.jsx`, `scripts/RESET_WORKING_AND_TEST.jsx`, `scripts/RUN_ADAPT_FRESH.jsx`.
  - `scripts/Create_Futuristic_HiTech_Logo_A7XZTEC.jsx`: Script dựng mới hoàn toàn hiệu ứng **Futuristic Hi-Tech Logo Reveal** bằng code thuần trong After Effects.

---

## 2. Quy Trình 4 Bước Chuẩn Hóa Logo Intro Thương Hiệu

### Bước 1: Chuẩn Bị File Logo Đầu Vào
1. Luôn ưu tiên định dạng **SVG / AI (Vector)** hoặc **PNG nền trong suốt (`RGBA`)** có kích thước tối thiểu `2000 × 2000 px`.
2. Khi đưa vào comp `Logo Placeholder` / `Your Logo Here`:
   - Căn giữa tâm comp (`Position = [comp.width/2, comp.height/2]`).
   - Giữ biên độ an toàn: chiều rộng hoặc chiều cao logo chiếm **45% – 65%** kích thước comp placeholder (không để sát mép vì hiệu ứng Glow/Saber/Extrude 3D sẽ bị cắt cụt).
   - Bật cờ **Continuously Rasterize (`collapseTransformation = true`)** nếu là file vector `.ai` / `.eps`.

### Bước 2: Dò Tìm & Đồng Bộ Bảng Màu Thương Hiệu (`TRACE_NATIVE_COLOR.jsx`)
Nhiều template công nghệ đặt một lớp `Control` ở ngoài nhưng vẫn còn các lớp `Solid`, `Gradient Ramp` hoặc `Tint` khóa cứng màu gốc ở các precomp sâu bên trong:
1. Chạy `scripts/INSPECT_CURRENT_TEMPLATE.jsx` và `scripts/TRACE_NATIVE_COLOR.jsx` để liệt kê toàn bộ các hiệu ứng màu đang hoạt động trong toàn dự án.
2. Áp bảng màu chuẩn thương hiệu (ví dụ bộ màu OPA):
   - **Primary Accent (Đường nét / Tia sáng / HUD chính):** `#1B6EF3` (`RGB: 27, 110, 243`)
   - **Secondary Cyan / Highlight (Điểm nổ sáng / Giao điểm lưới):** `#4DC4FF` (`RGB: 77, 196, 255`)
   - **Deep Tech Background (Nền tối kỹ thuật):** `#081226` đến `#0D1F40`
   - **Pure White (Logo & Tagline khi khóa nét cuối cảnh):** `#FFFFFF`

### Bước 3: Tinh Chỉnh Thước Đo, Lưới Kỹ Thuật & Tagline (`ADAPT_BLUEPRINT_OPA.jsx`)
- Với dòng **Blueprint / HUD**: tắt hoặc giảm `Opacity` của các chữ số ngẫu nhiên rườm rà nếu gây rối mắt tại thời điểm logo khóa nét (`final lockup` từ giây `07.0s – 10.0s`).
- Thay nội dung `Tagline / Website` bằng font không chân hiện đại (`Be Vietnam Pro` hoặc `Plus Jakarta Sans`, `Tracking: +80` đến `+150`).

### Bước 4: Xuất File Chuẩn Nền Đen Hoặc Nền Trong Suốt (Alpha)
- **Bản đầy đủ (Full Render):** Xuất `H.264 MP4` (`1920x1080`, chuẩn màu `BT.709`, âm thanh `AAC 320 kbps`).
- **Bản phủ trong suốt (Alpha Overlay để chèn lên đầu/cuối video khác):**
  - Mở comp điều khiển (`Control`), tích chọn `Transparent Background / Alpha = ON` (hoặc tắt mắt layer `Background`).
  - Xuất định dạng **QuickTime ProRes 4444** với `Channels = RGB + Alpha`, `Color = Straight (Unmatted)`.

<!-- ===== /file: ae-logo-intro-reveal/SKILL.md ===== -->

<!-- ===== file: ae-logo-intro-reveal/references/HUONG-DAN-3-TEMPLATES-OPA.md ===== -->

# Hướng dẫn dựng intro logo OPA từ 3 template

**Dành cho After Effects trên Windows · Kiểm tra file ngày 21/10/2026 · AE 2026 / 26.3**

## 1. Nên bắt đầu từ mẫu nào?

**Dùng template 1 - Abstract Techno Logo Reveal làm bản chính.** Nét sáng, các lớp chiều sâu, camera và vệt highlight của mẫu này phù hợp nhất với phần logo có khối trong video tham chiếu. Dùng template 3 khi muốn nhấn vào công nghệ/AI bằng lớp mã và lưới. Template 2 phù hợp với một phiên bản HUD, có vòng và hình lục giác bao quanh logo.

Hướng dẫn này có ba phần thực hành thay logo riêng và một cách dựng video OPA dài 16 giây. Bạn nên hoàn tất template 1 trước, sau đó dựng các cảnh nhận diện ở mục 9. Mục 7 và 8 giúp làm thêm hai phương án khác.

| Bộ trong thư mục của bạn | File nên mở trên AE 2026 | Comp kết quả đã kiểm tra | Thông số gốc | Vai trò đề xuất |
|---|---|---|---|---|
| Template 1 / Abstract Techno Logo Reveal | `Abstract Techno Logo Reveal 25.x.aep` | `## RENDER THIS` | 3840×2160, 30 fps, 10s | Intro chính: nét, chiều sâu, highlight |
| Template 2 / Sci-fi Logo | `Sci-fi Logo.aep` | `_MAIN COMP` | 1920×1080, 29,97 fps, khoảng 12,012s | Phương án HUD / vòng công nghệ |
| Template 3 / FRA - Digital Sci-fi Coding Logo Reveal | `FRA - Digital Coding Logo Reveal (Universalized Expression).aep` | `Digital Code Logo Reveal - Render HD (1920x1080)` | HD, 30 fps, 10,033s; có bản 4096×2160 | Phương án lớp mã / camera / lưới |

Ba file 18.x, 23.x, 25.x trong template 1 là các bản tương thích của cùng bộ, không phải ba mẫu khác nhau. Cả ba có 44 project item và 23 comp. Template 3 có bản thường và bản Universalized Expression; bản Universalized dùng các tham chiếu expression thuận tiện hơn khi khác ngôn ngữ giao diện. Không import đồng thời cả hai phiên bản của cùng một bộ.

### Nguồn đã đọc

Thư mục gốc: `/media/vmiz/Over Powers/video AE/template intro/template giải nén`.

Đã kiểm tra 6 file `.aep` bằng After Effects, 2 PDF của template 1, video hướng dẫn của template 2 và 3, các readme và các file ảnh/vector đi kèm. Readme của template 3 đang trống. Các footage đang được tham chiếu trong ba bộ đều có file tại thư mục đã giải nén.

Các tên bên dưới lấy từ project thật. Những con số trong bảng **preset OPA đề xuất** là điểm bắt đầu để dựng; không phải thông số trong bộ nhận diện chính thức.

## 2. Video Download.mp4 thực sự đang làm gì?

Nguồn: `/media/vmiz/Over Powers/THÀNH V/Download.mp4`. Video có hình 576×1024, 30 fps, **478 frame**, phần hình dài 15,933s. Đây là video quay màn hình đang chạy motion logo Framer. Khung dọc còn chứa màn hình AE, phối cảnh máy quay, phản chiếu đèn và watermark; phần logo bên trong màn hình mới là tham chiếu chuyển động.

Đã xem lại toàn bộ 478 frame. Frame được đánh số từ 0; các mốc chuyển động mềm có sai số quan sát khoảng 1-2 frame. Các mốc cắt rõ như frame 50, 214, 244, 259, 304, 334, 349, 379 và 439 có thể mở lại trong thư mục `Images/Reference`.

| Mốc trong nguồn | Frame | Hình ảnh / dạng motion | Áp dụng vào OPA |
|---|---|---|---|
| 0-1,633s | 0-49 | Điểm, đoạn thẳng dựng dần icon trên nền xanh | Lấy cách vẽ contour; cần artwork O/P/A của OPA |
| 1,667-3,100s | 50-93 | Cắt sang nền tối, logo sáng có cảm giác khối | Template 1: camera và các lớp extrusion/gloss |
| 3,133-4,100s | 94-123 | Một phần logo xanh, xuất hiện đường và nhãn | Chọn bảng xanh OPA; giữ lớp phụ vừa phải |
| 4,133-5,600s | 124-168 | Vệt sáng, góc nghiêng, bloom/flash; đỉnh sáng khoảng 4,7s | Template 1 có highlight và chiều sâu; giảm cường độ nếu mất khoảng rỗng O/P |
| 5,633-6,600s | 169-198 | Glow xanh bùng lên rồi giảm thành contour | Giữ một nhịp sáng rõ, sau đó trả logo về màu đọc được |
| 6,633-7,100s | 199-213 | Icon thu nhỏ về giữa, settle | Giảm chuyển động trước đoạn nhận diện |
| 7,133-9,100s | 214-273 | Wordmark trên nền sáng, xanh nhạt, tối rồi xanh đậm | Dựng 4 biến thể nền, mỗi biến thể khoảng 0,5s |
| 9,133-10,100s | 274-303 | Typography phóng lớn, trượt ngang, chồng nhiều lớp | Dùng chính artwork OPA phóng lớn và trượt; giữ nguyên tỉ lệ |
| 10,133-11,100s | 304-333 | Các thẻ màu | Dựng shape card Blue / White / Ink |
| 11,133-11,600s | 334-348 | Icon phẳng trên nền sáng | Dùng chữ O từ artwork, căn giữa |
| 11,633-12,600s | 349-378 | Icon quang học, viền màu trên nền xanh | Có thể dùng một vệt sáng ngắn; màu OPA vẫn là màu chính |
| 12,633-14,600s | 379-438 | Badge tròn biến dạng thành một chiếc mũ | Bản OPA hướng dẫn ở đây dùng badge O; phần mũ cần thêm asset/mockup 3D riêng |
| 14,633-15,433s | 439-463 | Đổi nền xanh, vật thể xoay/rời khung | Kết bằng wordmark OPA trắng trên nền xanh |
| 15,467-15,900s | 464-477 | Quay lại điểm/nét đầu để loop | Tùy mục đích, giữ logo cuối để ghép nội dung hoặc làm loop riêng |

Ba template mới cung cấp engine reveal và các lớp kỹ thuật. Các cảnh biến thể nền, chữ lớn, thẻ màu, badge và cảnh kết được dựng thêm bằng shape/text/pre-comp trong AE. Riêng phép biến dạng thành mũ trong nguồn là một hạng mục asset/3D khác.

![Bảng mốc tham chiếu](Images/reference-keyframes.jpg)

## 3. Chuẩn bị đúng logo OPA

### 3.1. Dùng file nào?

Bộ hướng dẫn có các PNG trong suốt được căn gọn từ artwork OPA đã cung cấp, giữ nguyên hình O/P/A:

| File trong `Assets` | Dùng khi nào |
|---|---|
| `OPA-blue-1500x500.png` | Thay logo trong cả ba template; nền sáng hoặc hiệu ứng giữ màu nguồn |
| `OPA-white-1500x500.png` | Logo trắng trên nền xanh/tối và cảnh kết |
| `OPA-ink-1500x500.png` | Logo tối trên nền trắng/xanh nhạt |
| `OPA-O-white-512x512.png` | Icon O trắng trong badge |

PNG gốc có canvas 3082×1751 nhưng vùng artwork thực chỉ khoảng **732×221**, tại bounding box `(1175,765)-(1907,986)`. Template 1 tự fit theo kích thước canvas, vì vậy dùng nguyên PNG gốc sẽ làm logo nhìn rất bé. Các PNG 1500×500 trong bộ này có artwork rộng khoảng 1440 px, còn một ít khoảng trống để không sát mép.

PNG được xuất qua AE để giữ alpha. Đây là artwork raster được căn lại, không phải vector AI/SVG gốc. Khi có vector thương hiệu chính thức, có thể thay source tương ứng và kiểm tra lại độ dày nét.

### 3.2. Màu và chữ dùng cho bản dựng

| Thành phần | Giá trị đề xuất |
|---|---|
| Xanh OPA | `#0068FF` |
| Trắng | `#FFFFFF` |
| Nền tối cho reveal | `#04060D` hoặc `#0B1220` |
| Nền sáng | `#F7F9FC` |
| Highlight xanh nhạt | `#59BFFF` |
| Tagline bản dựng | `Marketing × Công nghệ × AI` |
| Font tagline dễ dùng | Arial Regular, có dấu tiếng Việt |

Wordmark OPA luôn dùng file artwork. Không gõ chữ OPA bằng font thay thế. Tagline trên là phương án cho video, bạn có thể đổi theo câu được doanh nghiệp duyệt.

### 3.3. Tạo bản làm việc

1. Tạo thư mục `/media/vmiz/Over Powers/video AE/OPA-INTRO-WORK` và các folder `Assets`, `Projects`, `Exports`.
2. Copy các PNG OPA cần dùng vào `Assets`.
3. Khi mở từng template, dùng **File → Save As → Save As…** để lưu bản làm việc vào `Projects`, ví dụ `OPA_T1_Abstract.aep`, `OPA_T2_HUD.aep`, `OPA_T3_Digital.aep`.
4. Nếu AE hỏi chuyển phiên bản project, mở và lưu thành bản làm việc nói trên.
5. Mở comp kết quả, chọn **Fit** - Vừa khung và **Half/Quarter** - Một nửa/Một phần tư khi chỉnh; xuất ở Full.

**Điểm kiểm tra:** file đang chỉnh có tên OPA trong `Projects`; nguồn template và thư mục Footage vẫn còn nguyên.

## 4. Những thao tác AE cần hiểu trước

| Nhãn / phím | Nghĩa và tác dụng |
|---|---|
| Project | Bảng danh sách file và composition |
| Composition / comp | Khung hình và timeline của một cảnh |
| Pre-comp | Một comp được đặt làm layer trong comp khác |
| Effect Controls / F3 | Bảng điều khiển hiệu ứng của layer đang chọn |
| S / P / T / R | Scale - Tỷ lệ / Position - Vị trí / Opacity - Độ hiện / Rotation - Góc xoay |
| U / UU | Hiện thuộc tính có keyframe / hiện các thuộc tính đã thay đổi |
| Stopwatch | Đồng hồ bật/tắt keyframe của một thuộc tính |
| F9 / Easy Ease | Làm chuyển động tăng/giảm tốc mềm ở keyframe đã chọn |
| Ctrl+I | Import - Nhập file, kể cả một project `.aep` khác |
| Ctrl+N / Ctrl+K | Tạo comp mới / mở thông số comp hiện tại |
| Ctrl+T | Horizontal Type Tool - Công cụ chữ ngang |
| Ctrl+M | Add to Render Queue - Thêm comp vào hàng đợi xuất |

**Layer trực tiếp và pre-comp khác nhau thế nào?** Khi Ctrl+D một layer PNG/shape/text, mỗi bản có transform hoặc nội dung layer riêng. Khi Ctrl+D một layer pre-comp trong timeline, các bản vẫn cùng đọc một comp nguồn. Sửa bên trong nguồn sẽ đổi cả hai. Muốn một cảnh khác nội dung, duplicate comp trong bảng Project rồi dùng comp mới. Nếu comp mới còn chứa các pre-comp con dùng chung thì các phần con đó vẫn liên kết.

Các tên gốc như `## RENDER THIS`, `SOURCE`, `Digital Code Logo Reveal` được expression tham chiếu. Đặt tên OPA cho master mới hoặc folder bao ngoài; giữ các tên nội bộ của template.

## 5. Template 1 - Dựng bản OPA chính

### 5.1. Mở đúng file và comp

Đường dẫn: `/media/vmiz/Over Powers/video AE/template intro/template giải nén/template 1/Abstract Techno Logo Reveal/Abstract Techno Logo Reveal 25.x.aep`.

1. Nhấn Ctrl+O, mở file trên; lưu bản OPA bằng Save As.
2. Trong bảng Project, double-click **`## RENDER THIS`**.
3. Kéo playhead đến khoảng 4-5s để thấy đoạn reveal; đến 8-9s để xem logo gần hoàn thiện.

**Điểm kiểm tra:** comp 3840×2160, 30 fps, 10 giây. Trong timeline có layer `Settings` và `MAIN `.

### 5.2. Thay logo ở đúng chỗ

1. Trong bảng Project tìm **`## LOGO REPLACE`**. Đây là **footage ảnh**, không phải comp.
2. Right-click nó → **Replace Footage → File…** - Thay file nguồn.
3. Chọn `OPA-blue-1500x500.png` trong Assets.
4. Quay lại `## RENDER THIS` ở 8-9s.

Template dùng comp `SOURCE` 3840×3840 để auto fit; expression fit theo chiều rộng/chiều cao của file nguồn. Không thêm một PNG OPA nằm đè lên comp kết quả: cách đó chỉ tạo logo phẳng ở trên, các lớp chiều sâu bên dưới vẫn lấy logo demo.

**Điểm kiểm tra:** silhouette trong các lớp nét và khối đều là O/P/A; không còn hình AP của demo.

### 5.3. Chỉnh kích thước và bảng màu

1. Trong `## RENDER THIS`, chọn layer **`Settings`**, nhấn **F3**.
2. Chỉnh theo bảng này. Đây là preset đã được lưu thử để kiểm tra hướng dẫn; có thể tinh chỉnh sau khi xem chuyển động.

| Tên control chính xác | Giá trị bắt đầu cho OPA | Cách dùng |
|---|---|---|
| `Logo Scale` | 150 | Nếu logo quá lớn lúc camera đến gần, giảm từng bước 10; giữ hai chiều đồng đều |
| `Line Thickness` | 7 | Tăng lên 8-10 nếu nét bị mất ở Full HD; giảm nếu lỗ O/P bị bít |
| `Dropdown Menu Control` | 1 - Custom Color | 1 dùng màu custom; 2 lấy màu từ nguồn |
| `Color 1` | `#0068FF` | Màu chính của các lớp hiệu ứng |
| `Color 2` | `#59BFFF` | Màu highlight, giữ sáng hơn màu chính |
| `Floor Colour` | `#04060D` | Màu sàn/nền tối của hiệu ứng |
| `Text Position` | Bắt đầu từ `[1500,600]` | Điều khiển trong comp chữ; xem trực tiếp trước khi đổi |

Bạn cũng có thể dùng panel **Essential Graphics** khi có trong giao diện: chọn primary comp `## RENDER THIS`, sẽ thấy LOGO SCALE, LOGO REPLACE, TEXT REPLACE và nhóm Settings. PDF gốc có hình minh họa panel đồ họa; đường `Settings → F3` ở trên là cách chỉnh trực tiếp đã đối chiếu với file `.aep`.

Chỉ chọn menu/màu ở control gốc; không cần vào comp `3D ` với hơn 100 lớp FX để đổi từng lớp.

### 5.4. Sửa tagline và font

1. Mở comp **`TEXT`** trong bảng Project.
2. Chọn layer **`Lorem Ipsum 3`**.
3. Dùng Ctrl+T để thay thành `Marketing × Công nghệ × AI`.
4. Chọn font **Arial Regular**, cỡ bắt đầu **60** trong comp TEXT.
5. Mở lại `## RENDER THIS`, xem ở 8-9s. Nếu dài quá, giảm font size; điều chỉnh vị trí bằng `Settings → Text Position`.

Font gốc của câu demo là `Between1-Medium`; không cần cài font này để giữ logo OPA vì wordmark là artwork. PDF gốc cũng ghi nhạc preview được tải riêng, không có trong bộ này.

### 5.5. Kiểm tra trước khi dựng tiếp

- 2s: đã bắt đầu nhìn ra contour OPA.
- 4-5s: hình vẫn còn khoảng rỗng ở O/P, highlight không làm logo thành một mảng trắng.
- 7s: các lớp khối và camera không cắt mất đầu/cuối wordmark.
- 9s: logo và tagline đọc được, không còn Lorem Ipsum.

Nếu viền đỏ/xanh lá của demo quá mạnh: mở `MAIN ` → chọn `Adjustment Layer 8` → F3 → tắt riêng hiệu ứng **`3D Glasses`** bằng nút fx cạnh hiệu ứng, rồi so sánh lại. Control màu ở Settings không loại bỏ hoàn toàn hiệu ứng tách kênh này. Giữ hoặc giảm tùy phong cách bạn muốn.

![Template 1 - khung kiểm tra OPA](Images/T1-OPA-preview.png)

Ảnh trên là một frame kiểm tra setup, không đại diện cho toàn bộ 10 giây chuyển động.

## 6. Cách dùng bản template 1 trong video hoàn chỉnh

**Bản intro đơn:** giữ nguyên 10s của `## RENDER THIS`. Tạo comp mới `OPA_INTRO_T1_HD`, 1920×1080, 30 fps, 10s. Kéo `## RENDER THIS` vào và đặt Scale **50%**, Position `[960,540]`. Đặt audio ở comp mới này.

**Bản nhận diện 16s giống nhịp tham chiếu hơn:** dùng engine 10s làm phần đầu 7,2s, rồi thêm biến thể màu, chữ lớn, thẻ màu và badge. Cách dựng nằm ở mục 9. Đây là lựa chọn dựng nhịp, không sửa trực tiếp tốc độ của từng camera trong template.

Nếu cần xem lại video tutorial của hai bộ còn lại, mốc hướng dẫn tương ứng được liệt kê trong phần của từng bộ. Đó là thời gian trong video **hướng dẫn thao tác**, không phải thời gian của animation đầu ra.

## 7. Template 3 - Phương án Digital / AI

### 7.1. Mở và nhận diện các comp

Đường dẫn: `/media/vmiz/Over Powers/video AE/template intro/template giải nén/template 3/FRA - Digital Sci-fi Coding Logo Reveal/FRA - Digital Coding Logo Reveal (Universalized Expression).aep`.

| Tên comp/layer | Việc cần làm |
|---|---|
| `Your Logo` | Thay artwork và câu `envato.com` |
| `Digital Code Logo Reveal → Color Control` | Đổi màu các thành phần được nối với control |
| `Digital Code Logo Reveal - Render 4K (4096x2160) → CC` | Màu nền/ánh sáng phụ và Curves |
| `Digital Code Logo Reveal - Render HD (1920x1080)` | Comp HD để preview/xuất |
| `Overlay Codes`, `Overlay Codes 2` | Các dòng mã và hình kỹ thuật |
| `glass texture` | Texture kính; cần giữ file DirtWindowStains… đi kèm |

### 7.2. Thay logo mà không giữ nhầm Scale của EPS demo

1. Lưu bản làm việc OPA.
2. Mở **`Your Logo`**, canvas 4096×2160.
3. Ctrl+I nhập `OPA-blue-1500x500.png`; kéo file vào comp.
4. Đặt Position **`[2048,1080]`**, Scale **112,5%** ở cả hai chiều. Artwork rộng khoảng 1620 px là điểm bắt đầu phù hợp với khung logo demo.
5. Đặt layer mới chạy hết comp Your Logo, khoảng 16,44s.
6. Tắt mắt layer **`EnvatoLogoLight.eps`**.
7. Giữ `SAFE AREA` làm guide; guide không xuất ra video. Layer `Shape Layer 1` của bản gốc đang tắt.

EPS demo đang có Scale khoảng **575,44%** vì kích thước nguồn EPS nhỏ. Nếu Alt-kéo một PNG lớn vào đúng layer EPS rồi giữ Scale ấy, logo mới sẽ phóng quá mức. Cách thêm layer mới và đặt số ở trên tránh lỗi đó.

**Điểm kiểm tra:** logo vừa vùng SAFE AREA, đúng tỉ lệ; trong comp `Digital Code Logo Reveal` các lớp bóng, contour và khối đều lấy OPA từ cùng pre-comp `Your Logo`.

### 7.3. Đổi chữ và màu

1. Trong `Your Logo`, sửa layer **`envato.com`** thành tagline; bắt đầu với Arial Regular, cỡ **90** trong comp gốc.
2. Giữ animation Anchor Point/Opacity vốn có của layer chữ. Chọn layer, nhấn U để xem trước khi thay transform.
3. Mở `Digital Code Logo Reveal`, chọn **`Color Control`** → F3.
4. Đặt **`Color Control 1`** thành `#0068FF`.
5. Mở comp render 4K, chọn **`CC`** → F3. Đổi năm màu nền theo tông xanh tối để bỏ mảng cam/tím demo.

| Control của CC | Preset OPA đề xuất |
|---|---|
| `Background Color 01` | `#081F40` |
| `Background Color 02` | `#05142E` |
| `Background Color 03` | `#04060D` |
| `Background Color 04` | `#0A2E59` |
| `Background Color 05` | `#051A42` |

`Curves` trong CC có keyframe sẵn, vì vậy trước tiên giữ nguyên. Nếu hình tối quá, tăng dần nền hoặc chỉnh Curves sau khi nhìn cả đoạn, tránh đổi toàn bộ nền thành xanh sáng cùng lúc làm mất nét logo.

### 7.4. Làm bớt rối cho thương hiệu doanh nghiệp

Trong `Digital Code Logo Reveal`, các layer `Overlay Codes` và `Overlay Codes 2` có thể giảm Opacity hoặc tắt từng layer để so sánh. Để giữ cảm giác AI mà logo vẫn nổi, bắt đầu với 40-60% ở các lớp mã đang hiện. Đây là mức đề xuất về thiết kế, không phải slider tổng có sẵn trong template.

Mở comp render HD ở khoảng 5s và 9s để kiểm tra camera, logo, tagline và nền. Nguồn 4K là **4096×2160**, khác 3840×2160. Wrapper HD có Scale 50%, nghĩa là hình nguồn rộng 2048 và được cắt nhẹ hai bên trong canvas 1920. Giữ chữ/logo trong SAFE AREA khi dùng bản HD.

Các comp logo/background gốc có cả 25 fps; comp render là 30 fps. Giữ cấu trúc này khi sửa nguồn, không đổi hàng loạt mọi pre-comp sang 30 fps.

![Template 3 - khung kiểm tra OPA](Images/T3-OPA-preview.png)

Mốc trong `help.mp4`: 20-60s thay logo/chữ; 80-110s xem màu/nét; 120-170s chỉnh nền/Curves; 180-220s chuyển sang comp render và xuất. Xem lại các ảnh hướng dẫn trong `Images/Tutorials/T3-sheet-1.jpg` và `T3-sheet-2.jpg`.

## 8. Template 2 - Phương án HUD

Đường dẫn: `/media/vmiz/Over Powers/video AE/template intro/template giải nén/template 2/Sci-fi Logo/Sci-fi Logo.aep`.

### 8.1. Thay logo

1. Mở file và Save As bản OPA.
2. Mở **`EDIT YOUR LOGO HERE`**, canvas 1000×1000.
3. Import/kéo `OPA-blue-1500x500.png` vào comp.
4. Đặt Position **`[500,500]`**, Scale **60%**. Canvas ảnh rộng 900 px; artwork thực rộng khoảng 864 px.
5. Cho layer chạy hết comp, khoảng 10,01s. Layer `Instructions` vốn đang tắt, giữ tắt.
6. Mở `_MAIN COMP` và xem lúc camera nghiêng khoảng 3-5s, sau đó lúc kết 9-11s.

Nếu dùng icon O thay vì cả wordmark trong HUD, dùng icon nguồn riêng và chỉnh lại Scale để vừa vòng. Với bản OPA doanh nghiệp, wordmark đầy đủ giúp người xem nhận tên thương hiệu ngay.

### 8.2. Chỉnh đúng CONTROLLERS

Trong **`_MAIN COMP`**, chọn layer **`CONTROLLERS`** → F3.

| Control đúng tên | Giá trị / thao tác cho OPA |
|---|---|
| `Use Logo Original Color` | Bật khi dùng PNG OPA xanh; lúc này nguồn quyết định màu logo |
| `Logo Color` | `#0068FF`; muốn control này tô lại logo thì tắt Use Logo Original Color |
| `Disable URL` | Để tắt nếu dùng tagline trong template; bật nếu muốn bỏ hẳn dòng phụ |
| `Disable Lights` | Bắt đầu tắt; bật nếu cần xem phiên bản ít ánh sáng |
| `Lights Color` | `#59BFFF` |
| `Lines Color` | `#0068FF` |
| `Background Grid` | `#0F2647` |
| `Background Dots 01` | `#0F2647` |
| `Background Dots 02` | `#0068FF` |

Không phải đổi `Logo Color` là chắc chắn đổi logo: checkbox giữ màu gốc là điểm quyết định. Video tutorial minh họa đúng việc chuyển màu logo ở vùng 140-170s.

### 8.3. Sửa dòng URL thành tagline

1. Mở **`EDIT YOUR URL HERE`**, canvas 1000×100.
2. Sửa layer **`www.yourwebsite.com`** thành `Marketing × Công nghệ × AI`.
3. Chọn Arial Regular, cỡ bắt đầu **27**; giữ câu nằm trong chiều ngang 1000 px và chiều cao 100 px.
4. Giữ `Instructions` tắt.
5. Quay về `_MAIN COMP`, xem ở đoạn cuối nơi URL được hiển thị.

Font HUD nhỏ trong bản gốc là `BebasNeueBook`, câu URL là `CenturyGothic`. Nếu báo thiếu font, có thể thay text phụ bằng Arial/Arial Narrow đang có trên máy và kiểm tra tràn dòng. Hình logo OPA vẫn lấy từ PNG, không phụ thuộc font này.

Template 2 dùng **29,97 fps**, khoảng **12,012s**. Giữ nguyên comp gốc khi chỉnh. Nếu đưa vào master 30 fps, AE lấy mẫu theo timeline master; không cần đổi trực tiếp toàn bộ engine HUD.

![Template 2 - khung kiểm tra OPA](Images/T2-OPA-preview.png)

Mốc trong `How to use this template.mp4`: 30-90s nhập và đặt logo; 100-130s sửa URL; 130-180s các controller; 180-221s thử logo/URL ở đoạn kết. Readme cũng chỉ rõ ba comp cần sửa: `_MAIN COMP`, `EDIT YOUR LOGO HERE`, `EDIT YOUR URL HERE`.

## 9. Dựng video nhận diện OPA 16 giây theo nhịp tham chiếu

Đây là kịch bản thực hành hoàn chỉnh bằng template 1 và các cảnh native AE. Template 2 hoặc 3 có thể thay phần reveal khi bạn muốn một phong cách khác. Nếu muốn dùng cả ba, xem cách ghép tùy chọn ở mục 10.

### 9.1. Tạo master và đặt nhịp

1. Sau khi sửa xong template 1, tạo comp mới **`OPA_MASTER_16S`** bằng Ctrl+N.
2. Đặt Width 1920, Height 1080, Pixel Aspect Square Pixels, Frame Rate 30, Duration 16 giây.
3. Kéo `## RENDER THIS` vào master, Scale 50%, Position `[960,540]`.
4. Right-click layer đó → **Time → Time Stretch…** - Co giãn thời gian. Đặt Stretch Factor **72%**, giữ đầu layer ở 0. Engine 10s sẽ chạy trong 7,2s.
5. Đặt tên layer ngoài là `01_REVEAL_T1`. Giữ tên comp nguồn như cũ.

| Timeline master | Frame 30 fps, mốc cuối không tính | Cảnh | Nguồn |
|---|---|---|---|
| 0-7,2s | 0-215 | Nét, khối, highlight, camera rồi settle | Template 1, Time Stretch 72% |
| 7,2-9,2s | 216-275 | 4 biến thể logo/nền, mỗi biến thể 0,5s | Comp `OPA_COLOR_VARIANTS` |
| 9,2-10,2s | 276-305 | Artwork lớn trượt ngang, một nhịp chuyển mạnh | Comp `OPA_KINETIC` |
| 10,2-11,6s | 306-347 | 3 thẻ màu | Comp `OPA_PALETTE` |
| 11,6-13,6s | 348-407 | Icon O trên badge | Comp `OPA_BADGE` |
| 13,6-16s | 408-479 | Logo trắng trên xanh, tagline và giữ cảnh kết | Comp `OPA_FINAL` |

Tạo mỗi comp cảnh mới ở 1920×1080/30 fps với đúng thời lượng của cảnh. Trong master, kéo từng comp vào, đưa playhead đến mốc bắt đầu và nhấn **`[`** để đưa đầu layer tới đó. `[` di chuyển layer; **Alt+`[` / Alt+`]`** cắt đầu/cuối layer. Nhấn U để kiểm tra keyframe trước khi dùng phím cắt.

Vì phần reveal đã được tăng tốc, hãy RAM Preview cả đoạn 0-7,2s. Nếu muốn chuyển động chậm và sang hơn, dùng bản reveal đủ 10s và kéo dài master; thứ tự các cảnh nhận diện giữ nguyên.

### 9.2. Cảnh 4 biến thể nền, 2 giây

1. Tạo `OPA_COLOR_VARIANTS`, dài 2s.
2. Tạo 4 cặp layer background + PNG logo. Mỗi cặp xuất hiện trong 0,5s liên tiếp: 0-0,5; 0,5-1; 1-1,5; 1,5-2.
3. Các nền dùng solid bằng **Layer → New → Solid…**. Các logo là PNG riêng, đặt giữa `[960,540]`, Scale khoảng **60%**; artwork rộng khoảng 864 px.
4. Cặp 1: nền trắng, logo xanh. Cặp 2: nền `#EAF3FF`, logo tối. Cặp 3: nền `#0B1220`, logo trắng. Cặp 4: nền `#0068FF`, logo trắng.
5. Dùng hard cut giữa các cặp để giữ nhịp nhanh. Không thêm 4 transition dài làm mềm hết cảm giác đổi biến thể.

**Điểm kiểm tra:** cả 4 logo nằm đúng cùng tâm và có cùng bề rộng. Không co một bản theo chiều ngang chỉ để vừa câu chữ.

### 9.3. Cảnh artwork lớn trượt ngang, 1 giây

1. Tạo `OPA_KINETIC`, nền xanh OPA, dài 1s.
2. Thêm PNG OPA trắng, Scale **160%** để artwork rộng khoảng 2304 px, lớn hơn khung.
3. Bật stopwatch Position. Đặt ba keyframe: **0s `[2500,540]`**, **0,2s `[960,540]`**, **1s `[-1500,540]`**.
4. Chọn các keyframe → F9. Preview; tăng tốc ra khung nếu thấy logo dừng lâu.
5. Ctrl+D layer hai lần. Lùi hai bản sau lần lượt **2 frame và 4 frame**, giảm Opacity còn **25% và 12%** để có cảm giác chồng lớp; bật Motion Blur của layer và của comp.

Đây là chuyển động artwork, không phải gõ chữ OPA bằng font. Nếu quá rối, giữ một layer chính và một bản trễ.

### 9.4. Cảnh bảng màu, 1,4 giây

1. Tạo `OPA_PALETTE`, nền `#F7F9FC`, dài 1,4s.
2. Bỏ chọn mọi layer rồi dùng Rounded Rectangle Tool để tạo 3 **shape layer** riêng. Nếu đang chọn PNG, công cụ vẽ có thể tạo mask thay vì shape.
3. Mỗi card khoảng **300×440**, bo góc **18**; tâm ở **`[620,500]`, `[960,500]`, `[1300,500]`**. Màu lần lượt Blue, White, Ink.
4. Tạo text Arial 24 dưới card ở y=790: `OPA Blue`, `OPA White`, `OPA Ink`. Card trắng có thể thêm stroke `#DDE5EF`, 2 px để tách khỏi nền.
5. Với mỗi card và nhãn, animate Position từ y=650 tới y=500 và Opacity 0→100 trong **0,25s**. Cho card 2 trễ **3 frame**, card 3 trễ **6 frame**.
6. Giữ đủ tới khoảng 1,1s; trong 0,3s cuối kéo lên thêm 50 px và fade out.

**Điểm kiểm tra:** thứ tự xanh-trắng-tối rõ ràng; text không dính vào cạnh card. Căn các nhãn theo tâm card, không căn theo bề rộng chữ.

### 9.5. Badge O, 2 giây

1. Tạo `OPA_BADGE`, nền sáng, dài 2s.
2. Vẽ ellipse **420×420**, Fill `#0068FF`, Position `[960,540]`.
3. Thêm icon `OPA-O-white-512x512.png`, đặt tâm `[960,540]`; bắt đầu Scale **60%**. Chỉnh nhỏ hơn nếu khoảng xanh quanh O bị hẹp.
4. Nếu chỉ có wordmark, dùng mask để chỉ giữ chữ O trong một pre-comp riêng, sau đó căn lại Anchor Point vào giữa O trước khi animate Scale.
5. Pre-compose circle và icon thành `OPA_BADGE_GROUP`, chọn **Move all attributes into the new composition** - Chuyển thuộc tính vào comp mới.
6. Animate Scale nhóm ở local 0s=70%, 0,35s=100%, 1,6s=100%, 2s=130%; Opacity 0→100 trong 0,2s, giữ, rồi fade trong 0,2s cuối. Dùng F9.

Giữ cả circle và O trong cùng nhóm để khi scale, hai phần đi cùng nhau. Đây là ứng dụng nhận diện dạng badge, thay cho cảnh biến dạng thành mũ trong video nguồn.

### 9.6. Cảnh kết xanh, 2,4 giây

1. Tạo `OPA_FINAL`, dài 2,4s, nền `#0068FF`.
2. Đặt wordmark OPA trắng tại **`[960,460]`**, Scale **60%**; bề rộng artwork khoảng 864 px.
3. Tạo tagline Arial Regular **36 px**, trắng, center tại khoảng **`[960,680]`**.
4. Trong 0,3s đầu, logo đi từ y=480→460, Opacity 0→100. Tagline trễ 4 frame, từ y=700→680 và fade 0→100 trong 0,3s.
5. Giữ logo/tagline đứng yên phần còn lại. Đừng fade ra đen ở cuối nếu sẽ ghép ngay sang video doanh nghiệp; quyết định điểm cắt theo nội dung phía sau.

**Điểm kiểm tra:** từ khoảng 14,3s của master đến hết, người xem đọc được đầy đủ OPA và tagline.

## 10. Nếu muốn kết hợp cả 3 template trong một video

Hãy làm từng bản thay logo trước rồi import các `.aep` làm việc vào một master bằng Ctrl+I. AE đưa project được import vào folder; giữ tên comp con để expression tiếp tục đúng. Ba engine cùng chạy dễ nặng, nên dựng và kiểm tra từng cảnh trước khi bật preview cả master.

Cách ghép đề xuất: **0-1,8s template 3** lấy contour/lưới đang hình thành → **1,8-6,2s template 1** lấy phần có khối/highlight → **6,2-7,2s template 2** lấy một nhịp HUD → **7,2-16s** dùng các cảnh nhận diện ở mục 9.

Đây là **phương án biên tập**: chọn đoạn nguồn bằng mắt sau khi thay logo, không lấy mặc định 1,8s đầu của mọi template vì có thể chỉ có nền. Dùng ba frame kiểm tra đã render để định hướng, rồi RAM Preview để chọn mốc in/out thực tế. Cắt theo mức sáng, vị trí và độ lớn logo; dùng hard cut hoặc dissolve tối đa khoảng 3-5 frame khi cần nối.

Để thống nhất hình: cùng tông nền tối, xanh OPA làm chính, giảm HUD/codes nếu lấn wordmark. Mỗi đoạn chỉ có một lớp logo chính. Nếu nhịp HUD quá khác, dùng template 2 thành một phiên bản intro riêng và giữ bản 16s đi theo template 1.

## 11. Audio và nhịp cắt

Trong ba bộ đã giải nén không có file nhạc riêng dạng WAV/MP3; các MP4 help là video hướng dẫn. Template 1 dẫn tới nhạc preview bán riêng trong PDF. Bạn có thể đặt nhạc/sound design đã có quyền sử dụng ở master.

| Mốc master 16s | Âm thanh gợi ý |
|---|---|
| 0-2s | Một texture điện tử nhẹ, không che tiếng nếu có voice-over |
| 3-6s | Một whoosh/sweep đi cùng highlight hoặc chuyển góc |
| 7,2s | Một nhịp chốt khi bắt đầu bản nhận diện phẳng |
| 9,2s | Whoosh ngắn theo cảnh artwork trượt |
| 10,2s | 2-3 click nhẹ theo thẻ màu |
| 11,6s | Pop mềm cho badge |
| 13,6s | Một âm chốt thương hiệu và đuôi reverb ngắn |

Trong AE nhấn **L** trên layer audio để mở Audio Levels. Bắt đầu ở mức nhỏ, preview với tai nghe, giảm nếu nhiều effect cộng lại bị gắt. Giữ peak dưới 0 dBFS; có thể chừa khoảng 1 dB ở bản xuất. Không cần đặt whoosh cho mọi layer chuyển động.

## 12. Xuất file và gom project để chuyển máy

### Xuất video

1. Mở `OPA_MASTER_16S` hoặc comp intro HD bạn đã tạo.
2. Ctrl+M để đưa comp vào Render Queue.
3. Render Settings: **Best Settings**, Resolution **Full**, 30 fps ở master.
4. Output Module trên AE hiện tại có preset **`H.264 - Match Render Settings - 15 Mbps`**; chọn preset này để có MP4 xem/gửi.
5. Output To: chọn thư mục Exports, đặt tên rõ `OPA_Intro_T1_10s_HD.mp4` hoặc `OPA_BrandFilm_16s_HD.mp4`.
6. Render, sau đó mở MP4 kiểm tra từ đầu tới cuối. RAM Preview ở Half/Quarter không phản ánh chính xác độ nét xuất Full.

Để xuất UHD 3840×2160, tạo master riêng kích thước đó, scale vị trí/shape/text tương ứng. Template 1 có engine đúng 3840×2160. Template 2 chỉ HD; phóng nó lên không tạo thêm chi tiết thật. Template 3 có bản 4096×2160, cần quyết định crop/fit khi đưa vào UHD.

### Chuyển cả project và footage

Trong bản làm việc, chọn **File → Dependencies → Collect Files…** - Gom file phụ thuộc. Chọn thu thập cho project/các comp cần bàn giao, kiểm tra đủ ảnh và audio, rồi chọn thư mục đích mới. Đây là thao tác Adobe hướng dẫn để gom project cùng nguồn; xem [tài liệu Adobe về nhập và gom project](https://helpx.adobe.com/after-effects/desktop/work-with-other-applications/work-with-adobe-premiere/importing-effects-premiere-pro.html).

Giữ PNG logo và texture cạnh bản làm việc hoặc dùng Collect Files. Nếu bị missing footage, right-click footage đó trong Project → **Replace Footage → File…**, chọn file cùng tên trong thư mục đã giải nén. Thay file texture của template 3 ở item `DirtWindowStains005_COL_6K.jpg`; không thay vào layer logo.

## 13. Lỗi thường gặp và cách xử lý

| Triệu chứng | Kiểm tra và sửa |
|---|---|
| Logo OPA rất bé | PNG gốc có nhiều khoảng trong suốt; dùng PNG 1500×500 đi kèm, rồi chỉnh control hoặc Scale đúng chỗ |
| Template 1 vẫn hiện logo AP trong khối | Đã đè logo ở comp kết quả; thay footage `## LOGO REPLACE` để mọi pre-comp đọc cùng nguồn |
| Template 3 logo quá to | Layer EPS demo có Scale khoảng 575%; thêm PNG mới, đặt Scale 112,5% và tắt EPS |
| Template 2 đổi Logo Color mà hình không đổi | `Use Logo Original Color` đang bật; tắt nó để dùng Logo Color, hoặc giữ bật và sửa artwork nguồn |
| Logo có hình chữ nhật đen | Kiểm tra alpha/checkerboard trong viewer; dùng PNG trong suốt, không dùng JPG logo có nền |
| Viền O/P bị lấp | Giảm Line Thickness/glow, kiểm tra tại Full; giữ màu highlight có chi tiết |
| Tagline mất dấu | Dùng Arial hỗ trợ tiếng Việt, kiểm tra chữ trong Character và trên frame xuất |
| Chữ bị cắt | Xem canvas TEXT / URL HERE, giảm font size hoặc đặt lại vị trí; không chỉ kéo rộng layer theo X |
| Sửa một bản làm bản khác đổi theo | Hai layer pre-comp đang dùng chung nguồn; duplicate comp trong Project nếu cần nội dung độc lập |
| Expression đỏ sau khi đổi tên | Khôi phục tên comp gốc hoặc sửa tham chiếu; ưu tiên đặt tên OPA cho wrapper/master |
| Render chậm | Preview Quarter, chỉ preview Work Area cần xem; ba engine đều có nhiều lớp/comp lớn, nhất là T1 |
| Lệch màu/nét khi ghép 3 mẫu | Thống nhất bảng xanh-tối, kiểm tra frame giao nhau, giảm lớp HUD/codes và độ sáng phụ |
| Đoạn màu/badge có frame trống | Kiểm tra in/out của layer cảnh theo bảng frame master; mốc cuối là exclusive, cảnh sau bắt đầu ngay mốc đó |

## 14. Checklist hoàn tất

- Đúng silhouette O/P/A và khoảng rỗng, không gõ lại wordmark bằng font.
- Logo, contour và các lớp khối đều đọc nguồn OPA.
- Không còn AP, Envato, `envato.com`, `www.yourwebsite.com` hoặc Lorem Ipsum của demo.
- Nền tối/sáng và logo có đủ tương phản; highlight không lấn hình.
- Tagline viết hoa đầu dòng, đủ dấu, nằm trong khung.
- Không nhầm mốc thời gian của tutorial 3 phút với mốc của intro 10-12 giây.
- Xem đủ phần giữa và cảnh kết; không chỉ kiểm tra frame đầu/cuối.
- Đã xem MP4 xuất Full, có audio đúng mức và đúng tỉ lệ hình.
- Có bản Collect Files khi chuyển máy.

## 15. Bằng chứng và các file mở lại

| File/thư mục trong bộ hướng dẫn | Nội dung |
|---|---|
| `Evidence/source-inventory.json` | Danh sách và SHA256 các file nguồn trước khi đọc |
| `Evidence/Download-probe.json` | Thông số đúng video Download.mp4, 478 frame và checksum |
| `Native/*-inspection.json` | Comp, layer, effect và giá trị control đọc trực tiếp trong AE |
| `Images/Reference/all-frames-1.jpg` đến `all-frames-6.jpg` | Bảng hình bao phủ toàn bộ video tham chiếu |
| `Images/Tutorials/T2-sheet-*.jpg`, `T3-sheet-*.jpg` | Bảng mốc của hai video hướng dẫn |
| `Images/PDF/AE-Help-*.png`, `Script-*.png` | Trang PDF của template 1 đã render để đọc hình và chữ |
| `Examples/OPA_T1_SETUP.aep`, T2/T3 tương ứng | Bản setup OPA để thực hành; đã thay logo/màu/chữ và kiểm tra một frame mỗi bộ |
| `QA` | Log render các frame kiểm tra và báo cáo xác minh bộ hướng dẫn |

Phần cấu trúc và control đã được đọc từ file thật trên AE 26.3; các bản setup dùng logo OPA để render frame kiểm tra. Kịch bản 16 giây ở mục 9 là hướng dẫn triển khai tiếp, với thông số dựng được đề xuất rõ ràng. Bản Blueprint OPA ở lượt trước nằm riêng tại `/media/vmiz/Over Powers/video AE/OPA-Blueprint-OPA`, không dùng nhầm làm nguồn của ba template mới.

Các project trong Examples đi cùng Assets. Mở một bản để đối chiếu ngay các control đã đặt, hoặc tự làm lại từ file gốc theo từng bước trong tài liệu. Texture/EPS của template 3 được copy vào `Assets/T3-Footage` cho các bản setup này.

<!-- ===== /file: ae-logo-intro-reveal/references/HUONG-DAN-3-TEMPLATES-OPA.md ===== -->

<!-- ===== file: ae-logo-intro-reveal/references/HUONG-DAN-BLUEPRINT-OPA.md ===== -->

# Hướng dẫn dựng OPA từ Blueprint Logo Reveal

Project làm việc: `/media/vmiz/Over Powers/video AE/OPA-Blueprint-OPA/OPA-Blueprint-OPA.aep`.

Giữ nguyên thư mục Assets bên cạnh project. File gốc của PixelTruck vẫn nằm tại `/media/vmiz/Over Powers/video AE/video/mẫu intro logo/Blueprint Logo Reveal`.

## 1. Mở đúng bản dựng

1. Trong After Effects, chọn **File → Open Project…** — Mở project; phím tắt **Ctrl+O**.
2. Chọn `OPA-Blueprint-OPA.aep` trong thư mục bàn giao.
3. Trong bảng **Project**, mở folder **00_OPA_EXPORTS**.
4. Double-click `OPA_10s_16x9_1920x1080` để xem intro 10 giây. Để xem bản có bảng màu và badge, mở `OPA_16s_BRAND_FILM_1920x1080`.
5. Chọn độ phóng đại **Fit** — Vừa khung. Khi chỉnh, có thể chọn độ phân giải **Half** — Một nửa; khi xuất chọn Full.

**Điểm kiểm tra:** có đúng chữ OPA, phần rỗng của O/P còn nguyên và không có sọc màu báo thiếu footage.

## 2. Hiểu cấu trúc trước khi sửa

| Comp/layer | Công dụng |
|---|---|
| `MAIN COMP` | Engine Blueprint 4K của template, 3840×2160 / 30 fps / 10s |
| `MAIN COMP → CONTROL` | Nét logo, echo, grid, rulers, màu, blur và vị trí chữ |
| `MAIN COMP → AUXILIARY GEOMETRY ` | Hướng và cường độ các hình học phụ |
| `MAIN COMP → CC` | Nhiễu và chỉnh hình tổng |
| `MAIN COMP → MOTION BLUR` | Pixel Motion Blur của tác giả; đã tắt trong bản OPA để nét rõ và render nhẹ hơn |
| `YOUR LOGO` | Artwork logo dùng chung cho các comp của template |
| `YOUR TEXT ` | Dòng tagline; tên comp gốc có khoảng trắng cuối |
| `ALL RULERS` | Các thước của tác giả và bộ đường `OPA_RULER_*` đã thêm |
| `OPA_10s_16x9_1920x1080` | Bản Full HD chứa `MAIN COMP` ở Scale 50% và audio riêng |
| `OPA_16s_BRAND_FILM_1920x1080` | Intro dùng chung, sau đó là thẻ màu, badge O và cảnh kết xanh |

Một **pre-comp** là một composition được đặt làm layer trong composition khác. Hai layer cùng dùng một pre-comp sẽ cập nhật cùng nhau. Vì vậy sửa `YOUR LOGO` sẽ cập nhật các vị trí dùng logo trong phần Blueprint. Các thẻ màu và hình O ở đoạn mở rộng là shape layer riêng.

Không đổi tên các comp gốc như `MAIN COMP`, `YOUR LOGO`, `YOUR TEXT `: expression của tác giả tham chiếu các tên đó.

## 3. Chỉnh artwork OPA

1. Mở `YOUR LOGO`.
2. Tìm ba layer `OPA_VECTOR_O`, `OPA_VECTOR_P`, `OPA_VECTOR_A`.
3. Mỗi layer là **Shape Layer** — Layer hình dạng. Mở **Contents → … path → Path** để chỉnh các điểm của chữ đó.
4. Khi chỉ muốn đổi kích thước toàn bộ logo, chọn cả ba layer và chỉnh cùng mức **Scale** — Tỷ lệ; không kéo riêng chiều ngang hoặc dọc. Nếu giữ hiệu ứng vệt sáng, chọn thêm ba layer `OPA_LIGHT_PASS_O/P/A` để chúng đổi cùng tỉ lệ, hoặc tắt mắt ba layer vệt sáng.
5. Layer `OPA_PNG_REFERENCE / Disabled` là ảnh gốc để đối chiếu. Có thể bật tạm để so sánh, rồi tắt trước khi xuất để tránh chồng hai phiên bản.

Các layer `OPA_LIGHT_PASS_O/P/A` tạo vệt sáng lướt ở khoảng 6–7,3s. Chọn một layer, nhấn U để xem keyframe opacity và mask. Tắt mắt cả ba layer nếu muốn logo giữ màu xanh phẳng trong suốt đoạn reveal.

Các đường shape được trace từ alpha của ảnh OPA đã cung cấp, không phải bộ vector AI/SVG chính thức. Artwork trong PNG gốc có vùng vẽ thực 732×221 px trên canvas 3082×1751. Bộ trace đã được đối chiếu theo mask trước khi đưa vào AE; khi cần hiệu chỉnh nhận diện ở mức brand guideline, dùng vector gốc được duyệt.

Nếu thay bằng logo khác: import ảnh/vector trong suốt bằng Ctrl+I, thêm vào `YOUR LOGO`, căn giữa canvas 1500×1500 và giữ tỉ lệ. Tắt ba layer OPA vector đang có. Cần chỉnh lại rulers và cảnh O icon ở đoạn mở rộng cho logo mới.

**Điểm kiểm tra:** riêng trong `YOUR LOGO`, OPA nằm giữa canvas; bề rộng bố cục khoảng 1360 trên canvas 1500, còn khoảng trống ở hai bên.

## 4. Sửa tagline

1. Mở `YOUR TEXT `.
2. Chọn layer `OPA_TAGLINE / Edit this text`.
3. Dùng công cụ **Horizontal Type Tool** — Công cụ chữ ngang, phím **Ctrl+T**; double-click dòng chữ rồi thay nội dung.
4. Bản hiện tại dùng “Marketing × Công nghệ × AI”, font Arial để có dấu tiếng Việt.
5. Nếu câu dài hơn, giảm **Font Size** — Cỡ chữ trong bảng Character; giữ nguyên tỉ lệ layer.
6. Mở lại `MAIN COMP` tại khoảng 8–9 giây và kiểm tra khoảng cách giữa logo với chữ.

Cảnh kết của brand film lấy nội dung chữ từ `YOUR TEXT ` bằng expression; phần style của dòng cuối được đặt riêng để dùng chữ trắng trên nền xanh.

## 5. Chỉnh màu và mức hiệu ứng của Blueprint

1. Mở `MAIN COMP`.
2. Chọn layer `CONTROL`, nhấn **F3** để mở **Effect Controls** — Bảng điều khiển hiệu ứng.
3. Kéo playhead đến marker tương ứng: **Setups 1**, **Setups 2**, **Setups 3**. Các marker là ghi chú mốc chỉnh của tác giả.

| Điều khiển | Ý nghĩa | Hướng chỉnh cho OPA |
|---|---|---|
| `RGB split ` | Tách kênh màu | Tắt để giữ nét rõ |
| `Camera lens blur` | Độ mờ ống kính | Giảm nếu cần logo rõ sớm hơn |
| `Logo line width ` | Bề dày nét vẽ | Điều chỉnh vừa đủ đọc ở Full HD |
| `Logo line color` | Màu contour | OPA Blue `#0068FF` |
| `Logo line_echo intensity ` | Cường độ vệt nét | Giữ thấp để không rối hình O/P/A |
| `Logo line_echo quantity` | Số lớp vệt | 2 là điểm bắt đầu của bản này |
| `Rulers intensity` | Cường độ đường đo | Có keyframe giảm dần trước cảnh kết |
| `Auxiliary lines intensity` | Đường phụ | Có keyframe giảm dần |
| `Grid intensity ` | Lưới | Có keyframe giảm về 0 để cảnh kết thoáng |
| `Text intensity` | Độ hiện của chữ | 100 khi dùng tagline |
| `Text color` | Màu tagline | Màu tối trên nền sáng |
| `Text position ` | Vị trí tagline | Xem trực tiếp ở 8–9s rồi kéo điểm điều khiển |
| `Background color` | Hai màu ánh xạ nền | Hai tông sáng, thiên xanh rất nhẹ |

Một số tên hiệu ứng có khoảng trắng cuối do file gốc; giao diện nhìn gần như giống nhau. Khi sửa bằng tay, chọn theo nhãn trong Effect Controls.

Các slider có stopwatch xanh đã có keyframe. Để đổi mức cho cả đoạn, chọn các keyframe liên quan; thay một giá trị tại một thời điểm có thể chỉ tạo/sửa một keyframe.

## 6. Chỉnh đường dựng theo hình OPA

1. Mở `ALL RULERS`.
2. Các layer `RULER`, `RULER 2`, `RULER (PROTRACTOR)…`, `RULER (RADIUS)…` của logo demo đã được tắt mắt.
3. Các layer `OPA_RULER_1` đến `OPA_RULER_6` là đường dựng mới. Mở **Contents → Editable path → Path** để sửa đầu mút.
4. `OPA_LABEL_W` và `OPA_LABEL_H` là nhãn chữ có thể sửa.
5. Mở `MAIN COMP` ở khoảng 3–4s để xem đường dựng cùng góc camera thực tế.

Nếu muốn dùng lại bộ thước gốc của tác giả: bật mắt thước cần dùng trong `ALL RULERS`, mở comp `RULER…` tương ứng, chọn `CONTROL ` và nhấn F3. Chỉnh `Ruler_position`, `Ruler_rotation`, các `Auxiliary lines_position_*` và độ dài. Chỉnh ở cuối phần animation của thước như PDF của tác giả hướng dẫn. Không bật tất cả thước cùng lúc nếu chưa căn lại theo OPA.

## 7. Chỉnh bản brand film 16 giây

Mở `OPA_16s_BRAND_FILM_1920x1080` và dùng các marker trên timeline:

1. **0–10s:** layer `01_BLUEPRINT_10s / Shared source` dùng chung nguồn intro. Sửa engine và tagline ở các comp gốc.
2. **10–12,3s:** sửa màu trong `CARD_OPA Blue`, `CARD_OPA White`, `CARD_OPA Ink`; sửa tên màu trong các layer `LABEL_…`.
3. **12,3–13,5s:** `O_ICON_BADGE` là nền tròn; `OPA_O_ICON` là chữ O dạng shape.
4. **13,5–16s:** `BG_FINAL_BLUE`, ba layer `FINAL_OPA_*` và `TXT_FINAL_TAGLINE` là cảnh kết.
5. Nhấn **U** trên layer để hiện các thuộc tính có keyframe; nhấn **UU** để xem các thuộc tính đã thay đổi.

Đoạn bảng màu/badge/cảnh kết lấy nhịp và ý tưởng triển khai nhận diện từ video tham chiếu. Phần đầu vẫn giữ engine Blueprint của file người dùng cung cấp.

## 8. Audio và xuất video

Audio nằm ở các layer `SFX / …` và trong Assets. Đây là sound-design hướng dẫn tự tạo. Có thể tắt biểu tượng loa để thay bằng audio khác.

1. Mở comp cần xuất.
2. Nhấn **Ctrl+M** — Add to Render Queue, thêm vào hàng đợi xuất.
3. Chọn **Best Settings**, **Resolution: Full**, 30 fps.
4. Chọn **H.264 - Match Render Settings - 15 Mbps** trong Output Module trên AE hiện tại.
5. Chọn file đích trong `Exports`, nhấn **Render**.

Với bản 4K, xuất `MAIN COMP` thay vì comp Full HD. Nếu muốn audio đi cùng bản 4K, thêm audio vào một wrapper 3840×2160 hoặc ghép audio sau khi xuất; `MAIN COMP` gốc là engine hình.

## 9. Kiểm tra nhanh trước khi dùng

- Không có color bars hoặc báo thiếu footage.
- OPA giữ đúng tỉ lệ, khoảng rỗng O/P không bị lấp.
- Tagline đủ dấu tiếng Việt và không cắt chữ.
- Không có đoạn đen giữa các cảnh 10s, 12,3s và 13,5s của bản dài.
- Giữ cảnh kết đủ lâu để đọc; dùng bản 10s khi cần mở đầu, bản 16s khi trình bày nhận diện.
- Chỉ chuyển cả thư mục project cùng Assets; không chuyển mỗi file `.aep` sang máy khác.

Chi tiết đối chiếu video gốc nằm trong `PHAN-TICH-VIDEO-VA-KICH-BAN.md`.

<!-- ===== /file: ae-logo-intro-reveal/references/HUONG-DAN-BLUEPRINT-OPA.md ===== -->

<!-- ===== file: ae-logo-intro-reveal/references/HUONG-DAN-OPA-NH2GY3D.md ===== -->

# OPA × Hi-Tech Logo Reveal — Manum-FX / NH2GY3D

## Trạng thái và mục tiêu

Người dùng xác nhận chưa tải template. Tài liệu này hoàn thành kịch bản và quy trình chỉnh sửa; chưa phải hướng dẫn đã kiểm chứng trên AEP của NH2GY3D. Các tên `OPA_MASTER`, `OPA_END_BG`, `OPA_WORDMARK` dưới đây là tên hướng dẫn bạn tự tạo, không phải tên layer được tác giả cung cấp.

Trang đã đối chiếu: https://elements.envato.com/hi-tech-logo-reveal-NH2GY3D . Thuộc tính hiện niêm yết After Effects CC, 1920×1080, 10 giây, không yêu cầu plugin bổ sung. Cần mở AEP để xác nhận fps, thời lượng comp thực tế, tên controller và cấu trúc layer. Video preview có thể khác một chút về thời lượng so với comp xuất.

Mục tiêu sáng tạo: một hệ thống công nghệ khởi động, nhận diện chữ O bằng vòng quét, sau đó trình bày đầy đủ OPA rõ ràng. Chữ O dùng trong cảnh reveal là đề xuất chuyển động; dấu hiệu nhận diện cuối vẫn là nguyên logo OPA.

## 1. Kịch bản đề xuất

Bản chính khoảng 12 giây: khoảng 10 giây template và khoảng 2 giây kết thương hiệu. Các mốc trong đoạn HUD là định hướng cảm giác, không phải keyframe gốc đã đo từ AEP.

| Thời gian dự kiến | Hình ảnh | Cảm giác / âm thanh đề xuất |
|---|---|---|
| 0–2s | Nền xanh đen, grid và các điểm dữ liệu xuất hiện | Hệ thống khởi động, tiếng điện tử nhẹ |
| 2–5s | Các vòng HUD tách lớp, xoay và tiến về tâm theo chuyển động mẫu | Quét và tập hợp thông tin, một tiếng sweep |
| 5–8s | Vòng ổn định dần, chữ O trắng của OPA hiện ở tâm | Nhận diện được kích hoạt, một điểm nhấn âm thanh |
| 8–9,6s | Giữ chữ O trong HUD, các chi tiết phụ lắng lại theo mẫu | Cho người xem kịp nhận hình |
| 9,6–10,3s | Nền xanh đen phủ dần lên HUD; đầy đủ OPA xanh xuất hiện | Chuyển êm, âm thanh giảm dần |
| 10,3–12s | Logo OPA nguyên bản đứng rõ trên nền sạch | Giữ thương hiệu, kết gọn |

Không thêm tagline hay địa chỉ web vào bản chính vì chưa có nội dung được chốt. Không dùng font gõ lại chữ OPA để thay cho file logo.

### Màu và bố cục đề xuất

- Xanh thương hiệu: `#0068FF`.
- Nền cảnh kết: `#071526` — màu nền đề xuất, không phải màu nền gốc đã đo.
- HUD: giữ nhiều nét trắng/xanh nhạt; dùng xanh thương hiệu làm điểm nhấn.
- Logo trong vòng: `OPA-O-white-512x512.png`, giữ đúng hình và khoảng hở của O.
- Logo cảnh kết: `OPA-blue-1500x500.png`, đặt giữa khung.
- Logo đầy đủ ngang khoảng 3,3:1, vì vậy không ép nó thành hình vuông để vừa vòng HUD.

## 2. Chuẩn bị thư mục và tải đúng gói

Thư mục hướng dẫn và asset đã chuẩn bị:

```text
/media/vmiz/Over Powers/video AE/OPA-NH2GY3D-Guide/
    HUONG-DAN-OPA-NH2GY3D.md
    Assets\
        OPA-O-white-512x512.png
        OPA-blue-1500x500.png
        OPA-white-1500x500.png
```

Khi tải về, bạn tự tạo thêm các thư mục sau:

```text
Source\      gói NH2GY3D giải nén, giữ đầy đủ cây thư mục
Project\     bản .aep chỉnh cho OPA
Render\      video xuất thử và bản cuối
```

1. Mở trang NH2GY3D, kiểm tra tác giả là **Manum-FX**.
2. Đăng nhập tài khoản có quyền tải và tải gói template. Nút **Download preview** chỉ lấy video mẫu, không phải project chỉnh sửa.
3. Giải nén đầy đủ vào `Source`. Giữ nguyên vị trí tương đối của AEP và thư mục footage đi kèm.
4. Đọc file Help/Tutorial trong gói nếu có để tìm comp thay logo và color controls.

**Điểm kiểm tra:** trong gói phải có project `.aep` hoặc project AE tương ứng, không chỉ có `.mp4`.

## 3. Mở và lưu bản OPA

1. Mở After Effects, chọn **File > Open Project** và mở AEP vừa giải nén.
2. Nếu AE chuyển đổi project phiên bản cũ, lưu thành bản mới.
3. Chọn **File > Save As > Save As**, lưu tại:
   `/media/vmiz/Over Powers/video AE/OPA-NH2GY3D-Guide/Project/OPA-NH2GY3D-v01.aep`.
4. Nếu có Missing Footage, chọn một footage bị thiếu ở Project panel, dùng **Replace Footage > File** và trỏ đúng file trong thư mục giải nén.
5. Nếu có Missing Font, kiểm tra tutorial và layer text tương ứng. Bản chính không cần tagline nên không tự thay font của logo.

**Điểm kiểm tra:** chạy preview bản gốc trong project đã Save As trước khi sửa. Nếu bản gốc chưa giống preview, xử lý tài nguyên thiếu trước.

## 4. Nhận diện comp chính và comp thay logo

**Composition / comp** là một cảnh có timeline. **Pre-comp** là một comp nằm như một layer trong comp khác. Chỉnh nội dung pre-comp có thể thay đổi tất cả nơi đang dùng nó.

1. Trong **Project panel** — bảng chứa tài nguyên, tìm comp có đầy đủ nền, vòng HUD và logo.
2. Mở comp và đưa playhead đến gần cuối. Đối chiếu với video mẫu để nhận ra comp xuất chính.
3. Nhấn **Ctrl+K** mở Composition Settings. Ghi lại kích thước, fps và duration thực tế; giữ nguyên fps của mẫu.
4. Tạm gọi comp đó là **comp HUD chính** trong hướng dẫn; không cần đổi tên comp tác giả vì expressions có thể tham chiếu tên cũ.
5. Xem tutorial để tìm comp thay logo. Các từ như Logo, Replace, Edit là từ khóa gợi ý, không phải tên đã xác nhận của NH2GY3D.
6. Nếu chưa thấy, trong comp HUD chính, mở dần layer pre-comp có chứa hình logo cho đến khi thấy ảnh logo mẫu.

**Điểm kiểm tra:** bạn tìm được nơi thay ảnh logo, nhưng các vòng HUD/camera vẫn nằm trong phần animation của mẫu. Không đặt ảnh OPA đè thẳng lên cảnh chính nếu muốn nó hưởng hiệu ứng reveal.

Lưu ý: Ctrl+D một comp chính không tự nhân bản toàn bộ pre-comp con. Bản Save As ở bước 3 giúp giữ project nguồn gốc riêng.

## 5. Import và thay chữ O vào vị trí logo

1. Nhấn **Ctrl+I** — Import File.
2. Import ba PNG trong thư mục `Assets` của hướng dẫn.
3. Mở comp thay logo, bật biểu tượng ô bàn cờ trong Composition viewer để kiểm tra nền trong suốt.
4. Nếu ảnh logo mẫu chỉ là một layer tĩnh bên trong comp thay logo: kéo `OPA-O-white-512x512.png` vào comp đó; tắt mắt layer ảnh mẫu, giữ lại các layer matte/effect liên quan.
5. Chọn layer O vừa thêm, nhấn **S** — Scale. Giữ hai chiều liên kết, chỉnh để vừa vùng logo mẫu. Không mặc định Scale phải bằng 100%.
6. Nhấn **P** — Position, đưa O vào giữa comp thay logo. Nếu comp có kích thước W×H, tâm hình học thường là `[W/2, H/2]`; kiểm tra bằng mắt ở comp chính sau đó.
7. Quay lại comp HUD chính để xem O có đi cùng vòng, ánh sáng và reveal hay không.

**Nếu layer logo mẫu có animation riêng:** nhấn **U** để xem keyframes trước khi thay. Khi cần giữ nguyên animation của layer đó, tạo một comp chứa O với kích thước bằng source logo cũ; sau đó giữ **Alt** và kéo comp mới từ Project panel thả lên đúng layer logo cũ trong Timeline. Cách này giữ thuộc tính layer; vẫn phải kiểm tra căn tâm và kích thước vì source mới có thể khác source cũ.

**Điểm kiểm tra:** logo mẫu đã biến mất, O đúng hình, không có hộp nền đen, không bị méo và không bị che mất khoảng hở.

## 6. Xử lý dòng chữ mặc định

1. Tìm layer text đang hiển thị URL hoặc chữ mẫu trong cảnh.
2. Nếu layer text nằm trong một comp riêng, mở đến layer chữ có biểu tượng T.
3. Với bản chính không tagline, tắt mắt đúng layer chữ mẫu. Giữ lại các layer điều khiển, matte hoặc thành phần HUD khác.
4. Quay lại comp HUD chính và chạy qua cả đoạn reveal.

Nếu chữ đã nằm trong footage dựng sẵn, không thể sửa bằng Type Tool; cần kiểm tra AEP trước khi quyết định cách che/thay. Không đoán rằng mọi chữ trên preview đều là text editable.

**Điểm kiểm tra:** không còn tên, logo hay URL mặc định của mẫu trong khung hình.

## 7. Chỉnh màu cho OPA

1. Mở comp chính và chọn layer điều khiển màu được tutorial tác giả chỉ định, nếu có.
2. Vào **Window > Effect Controls** — bảng chỉnh hiệu ứng của layer đang chọn.
3. Nếu có các ô màu cho HUD/accent/background, chỉnh từng ô một rồi xem lại ảnh. Tên các ô thực tế cần xác nhận từ AEP.
4. Đặt điểm nhấn năng lượng về `#0068FF`, giữ các vạch nhỏ trắng hoặc xanh nhạt để rõ chi tiết.
5. Chỉ chỉnh màu nền qua control của tác giả nếu có. Cảnh kết riêng ở bước sau sẽ dùng `#071526`.
6. Nếu không có controller, cần xác định đúng layer sinh màu của HUD trước; không áp Fill lên toàn bộ cảnh vì sẽ làm mất các sắc độ/chi tiết.

**Điểm kiểm tra:** cảnh có tông xanh OPA, O vẫn rõ, các nét HUD không cháy trắng hoặc bít vào nhau. Chưa cần thay keyframe camera, xoay vòng hay tốc độ của mẫu.

## 8. Tạo comp xuất mới để thêm cảnh kết

Giữ nguyên animation trong comp HUD chính. Tạo một comp bao ngoài để thêm đủ logo OPA cuối video.

1. Trong Project panel, kéo comp HUD chính vào nút **New Composition**. AE tạo comp mới bao chứa nó và kế thừa thông số.
2. Chọn comp mới, nhấn **Ctrl+K**, đặt tên `OPA_MASTER`.
3. Gọi thời lượng comp HUD chính là **T**. Đặt duration comp mới thành **T + 2 giây**, giữ nguyên fps. Nếu T=10s thì comp xuất là 12s.
4. Kiểm tra layer HUD bắt đầu ở giây 0 và kết thúc đúng T. Không bật Time Remapping hoặc Time Stretch cho bản đầu.

Thứ tự layer trong `OPA_MASTER` sau khi làm xong, từ trên xuống:

```text
OPA_WORDMARK    PNG logo đầy đủ, 2D
OPA_END_BG      solid xanh đen, 2D
Comp HUD chính pre-comp gốc đã thay O và màu
Audio          nếu có dùng âm thanh riêng
```

Các layer cảnh kết không parent với camera hoặc null của template. Cảnh kết dùng vị trí màn hình cố định.

## 9. Tạo nền cảnh kết

1. Trong `OPA_MASTER`, đưa playhead về giây 0, chọn **Layer > New > Solid** hoặc nhấn **Ctrl+Y**.
2. Đặt tên `OPA_END_BG`, màu `#071526`, bấm **Make Comp Size**.
3. Đặt solid ở trên layer HUD. Giữ layer 2D, Mode Normal.
4. Đưa playhead tới **T − 0,4 giây**, chọn solid rồi nhấn **T** — Opacity.
5. Bấm đồng hồ Opacity, đặt **0%**.
6. Đưa playhead tới **T**, đặt Opacity **100%**.
7. Kéo out-point solid phủ đến cuối `OPA_MASTER` nếu layer chưa đủ dài.

Ví dụ nếu T=10s: nền có Opacity 0% ở 9,6s và 100% ở 10,0s. Ở fps không biểu diễn được đúng 9,6s, chọn frame gần nhất.

**Điểm kiểm tra:** trước đoạn chuyển, HUD vẫn rõ. Khi comp HUD kết thúc, nền mới đã kín khung và không có frame đen/trong suốt ngoài ý muốn.

## 10. Thêm đầy đủ OPA và tạo keyframe

1. Đưa playhead về giây 0 rồi kéo `OPA-blue-1500x500.png` vào `OPA_MASTER`, đặt trên `OPA_END_BG`. Kiểm tra in-point của layer không nằm sau thời điểm bắt đầu fade.
2. Đổi tên layer thành `OPA_WORDMARK`, giữ layer 2D.
3. Nhấn **P**, đặt Position `[960, 540]` nếu comp là 1920×1080.
4. Nhấn **S**, đặt Scale khởi điểm khoảng **50%**, giữ liên kết hai chiều. Đây là điểm bắt đầu để chỉnh bằng mắt; không phải giá trị logo placeholder gốc.
5. Đưa playhead tới **T − 0,2s**, nhấn **T**, bấm đồng hồ và đặt Opacity **0%**.
6. Tới **T + 0,3s**, đặt Opacity **100%**.
7. Nhấn **S**. Tại **T − 0,2s**, tạo keyframe Scale **48%**. Tại **T + 0,3s**, tạo keyframe **50%**.
8. Chọn hai keyframe Scale, nhấn **F9** — Easy Ease để chuyển động mềm.
9. Giữ logo đứng yên, Opacity 100% đến cuối. Không thêm nhấp nháy hoặc glitch ở đoạn giữ cuối.
10. Kiểm tra layer PNG kéo dài đến cuối comp.

Ví dụ T=10s:

| Layer / thuộc tính | Mốc đầu | Mốc sau |
|---|---|---|
| OPA_END_BG / Opacity | 9,6s → 0% | 10,0s → 100% |
| OPA_WORDMARK / Opacity | 9,8s → 0% | 10,3s → 100% |
| OPA_WORDMARK / Scale | 9,8s → 48% | 10,3s → 50% |

Phím T vừa là chữ viết tắt biến thời lượng trong tài liệu, vừa là phím AE mở Opacity khi một layer đang chọn; hai ý này khác nhau.

**Điểm kiểm tra:** sau chuyển cảnh, người xem nhìn thấy đủ O/P/A đúng tỷ lệ, ở giữa khung, nền sạch. Vòng HUD không đè lên wordmark ở cảnh cuối.

## 11. Phương án đơn giản hơn: dùng cả logo ngay trong HUD

Nếu không muốn dùng riêng chữ O, ở bước 5 thay bằng `OPA-white-1500x500.png`. Giữ đúng tỷ lệ và thu nhỏ để toàn bộ wordmark nằm trong vùng trống của vòng.

Kiểm tra ở Composition viewer 100% và cả khi xem nhỏ như trên điện thoại. Nếu logo ngang bị nhỏ khó đọc hoặc cắt P/A, ưu tiên bản O → đầy đủ OPA ở trên. Không kéo giãn logo hoặc thay đổi kích thước của comp placeholder tùy tiện vì có thể ảnh hưởng matte/effect.

## 12. Âm thanh, xem thử và xuất

### Âm thanh

Trang mẫu liên kết một track âm thanh riêng, nên cần kiểm tra gói tải có audio hay không. Không mặc định nhạc preview đã nằm trong AEP. Nếu thêm âm thanh, đặt sweep theo vòng quét, impact theo lúc O hiện rõ; để đuôi âm thanh giảm mềm trong cảnh kết. Không nhân đôi audio nếu comp gốc đã có track.

### Xem thử

1. Preview toàn bộ `OPA_MASTER`, trước tiên ở Half resolution để xem nhịp.
2. Kiểm tra lại các frame O vừa xuất hiện, trước/sau nền phủ HUD và frame logo cuối ở Full resolution / 100%.
3. Xác nhận không còn logo/URL mẫu, không méo OPA, không còn matte cắt logo, không thiếu footage/font/effect.
4. Xác nhận đoạn giữ logo cuối đủ dài và không cắt mất đuôi âm thanh.
5. Save project bằng Ctrl+S.

### Xuất MP4 xem thử

1. Mở đúng `OPA_MASTER`.
2. Chọn **Composition > Add to Render Queue**.
3. Render Settings: Best Settings, phạm vi toàn comp. Nếu Work Area chưa phủ toàn clip, sửa Time Span về toàn bộ comp trước khi render.
4. Output Module: chọn H.264 nếu bản AE đang dùng có hỗ trợ. Với Full HD, có thể bắt đầu khoảng 15–20 Mbps để xem thử chất lượng; đây là đề xuất xuất, không phải thiết lập gốc template.
5. Output To: `/media/vmiz/Over Powers/video AE/OPA-NH2GY3D-Guide/Render/OPA-NH2GY3D-v01.mp4`.
6. Nếu bản AE không có H.264 trong Render Queue, dùng **Composition > Add to Adobe Media Encoder Queue**, chọn H.264 / Match Source và kiểm tra lại kích thước, fps, phạm vi xuất.
7. Render rồi mở chính MP4 vừa xuất để xem từ đầu đến cuối. Render xong không đồng nghĩa đã kiểm tra chất lượng.

Sau khi hoàn thiện có thể dùng **File > Dependencies > Collect Files** để gom project và footage cho việc lưu trữ/chuyển máy. Tài liệu hướng dẫn không phải một AEP đã dựng sẵn.

## 13. Lỗi thường gặp

| Hiện tượng | Kiểm tra trước |
|---|---|
| OPA quá nhỏ trong vòng | Logo ngang cần vùng rộng; dùng O trong HUD và wordmark cuối |
| PNG hiện nền đen | Bật checkerboard, kiểm tra alpha và đúng PNG; màu đen viewer chưa chắc là nền trong ảnh |
| Thay PNG nhưng không thấy reveal | Có thể đang đặt ảnh ở sai cấp; cần thay bên trong comp logo mà animation tham chiếu |
| Thay source làm lệch tâm | Kiểm tra source dimensions, Anchor Point, Position, Scale; tạo comp insert cùng kích thước source cũ |
| P/A bị cắt | Kiểm tra mask/matte và vùng trống của placeholder, không kéo méo logo |
| Chỉnh màu không tác dụng | Xác định đúng controller / đúng comp; màu có thể do expression điều khiển |
| Cảnh cuối không thấy logo | Logo phải trên solid, Opacity có keyframe 100%, layer đủ dài và không parent vào camera |
| Cuối video xuất bị cắt | Kiểm tra duration OPA_MASTER, layer out-point và Time Span trong Render Queue |

## Nguồn đối chiếu

- Template: https://elements.envato.com/hi-tech-logo-reveal-NH2GY3D
- Adobe — pre-comp và comp lồng: https://helpx.adobe.com/after-effects/desktop/work-with-compositions/precomposing-and-nesting/precomposing-nesting-pre-rendering.html
- Adobe — xuất H.264 trực tiếp: https://helpx.adobe.com/after-effects/desktop/render-and-export/export-h-264-from-the-after-effects/exporting-h264-from-the-after-effects-render-queue.html
- Adobe — render/export và Collect Files: https://helpx.adobe.com/after-effects/desktop/render-and-export/basics-of-rendering-and-exporting/basics-rendering-exporting.html

Khi có AEP thật, phần cần cập nhật là: tên comp chính, tên comp logo, tên layer text/controller, fps và duration T. Kịch bản, asset OPA và cách thêm cảnh kết bao ngoài vẫn là cơ sở để triển khai.

<!-- ===== /file: ae-logo-intro-reveal/references/HUONG-DAN-OPA-NH2GY3D.md ===== -->

<!-- ===== file: ae-logo-intro-reveal/references/NGHIEN-CUU-OPA-TECH.md ===== -->

# OPA — nghiên cứu intro logo công nghệ

Kiểm tra ngày 21/10/2026: đọc danh sách 48 kết quả ở trang 2, đối chiếu bốn mẫu tham chiếu và các trang sản phẩm được chọn; xem preview trực tiếp trong trình duyệt. Đây là nghiên cứu trang giới thiệu/preview, chưa tải và kiểm thử các AEP mới. Thời lượng dưới đây lấy ở Attributes, không lấy độ dài video quảng cáo có thể chứa nhiều phiên bản. Đánh giá độ phù hợp và cách sửa là đề xuất riêng cho OPA.


## Chọn nhanh

1. Gần mẫu V5GE8LJ nhất: NH2GY3D — Manum-FX.

2. Gọn, ưu tiên nhận diện OPA: KM97AC2 — Chernu.

3. Dữ liệu/AI, cân nhắc logo ngang: LJEF57R — RwTemplates.


## Logo OPA và tiêu chí chọn

OPA là wordmark ngang khoảng 3,3:1. Giữ đúng tỷ lệ và khoảng hở chữ O, lòng P, dáng A. Đề xuất dùng #0068FF cho đường năng lượng; nền xanh đen, logo trắng hoặc xanh có đủ tương phản. Mẫu vòng tròn cần mở vùng logo hoặc có đoạn kết đủ OPA; chỉ dùng chữ O như một phương án chuyển động được đề xuất.


## 8 ứng viên mới


### 1. Hi-Tech Logo Reveal — Manum-FX / NH2GY3D

https://elements.envato.com/hi-tech-logo-reveal-NH2GY3D

After Effects CC · 10 giây · 1920 × 1080 · 41.8 MB · None required — theo trang Envato

- Hình ảnh: Vòng HUD chia vạch, lưới không gian, camera nghiêng rồi trả về logo ở giữa.

- Đánh giá OPA: Ưu tiên 1 theo gu V5GE8LJ. Vòng tròn hợp chữ O; cả wordmark OPA sẽ nhỏ nếu giữ nguyên khung.

- Cách áp dụng đề xuất: Đề xuất O ở giữa vòng quét, sau đó kết bằng đủ OPA; hoặc mở vòng đủ rộng để đặt cả logo, giữ đúng tỷ lệ.


### 2. Hi-Tech Logo Reveal — Chernu / KM97AC2

https://elements.envato.com/hi-tech-logo-reveal-KM97AC2

After Effects CC · 10 giây · Resizable — theo trang sản phẩm · 20 MB · None required — theo trang Envato

- Hình ảnh: Đường sáng và nét kỹ thuật trên nền tối; kết logo/tagline gọn.

- Đánh giá OPA: Ưu tiên 2 cho OPA dùng thường xuyên. Ít chi tiết cạnh tranh với khoảng hở O và lòng chữ P.

- Cách áp dụng đề xuất: Thay toàn bộ placeholder bằng OPA ngang, chỉnh đường sáng về xanh thương hiệu; kiểm tra khoảng trống của placeholder sau khi tải.


### 3. Digital And Technology Logo Reveal — RwTemplates / LJEF57R

https://elements.envato.com/digital-and-technology-logo-reveal-LJEF57R

After Effects CC · 17 giây · 3840 × 2160 · 594 MB · None required — theo trang Envato

- Hình ảnh: Không gian đường dữ liệu, lưới và các bảng thông tin trên nền xanh đen.

- Đánh giá OPA: Ưu tiên 3 cho hướng AI, hệ thống và kết nối. Preview có bố cục chữ ngang; phù hợp để cân nhắc OPA đầy đủ.

- Cách áp dụng đề xuất: Chuyển năng lượng về #0068FF, giản bớt chữ trang trí; nếu cần intro ngắn thì dựng bản cắt riêng, không tăng tốc toàn bộ 17 giây.


### 4. Future Technology Logo Reveal — Chernu / 9WWCV6G

https://elements.envato.com/future-technology-logo-reveal-9WWCV6G

After Effects CC · 10 giây · Resizable — theo trang sản phẩm · 143 MB · None required — theo trang Envato

- Hình ảnh: Nét phát sáng dựng hình học và grid, kết logo trên nền tối.

- Đánh giá OPA: Lựa chọn thay thế KM97AC2, thiên về nét hình học. Preview có phần quảng bá nhiều tỷ lệ khung hình.

- Cách áp dụng đề xuất: Chọn bản ngang cho cả OPA, hạn chế glow làm bít lòng chữ. Resizable không đồng nghĩa mọi thành phần đều vector.


### 5. Tech Sci-fi Logo Reveal — bjarfx / RTGZ8K3

https://elements.envato.com/tech-sci-fi-logo-reveal-RTGZ8K3

After Effects CC · 8 giây · 1920 × 1080 · 301 MB · None required — theo trang Envato

- Hình ảnh: Khối hình học đen, mạch dữ liệu và module kính ở trung tâm.

- Đánh giá OPA: Đáng cân nhắc nếu muốn OPA trông như một hệ thống công nghệ được kích hoạt. Khác kiểu vòng HUD của mẫu cuối.

- Cách áp dụng đề xuất: Đặt OPA trong module, dùng điểm nhấn xanh. Cần xem AEP để biết phần 3D nào là footage dựng sẵn, phần nào chỉnh được.


### 6. Digital Technology Logo Reveal — ProMotionSquad-1 / UZ7WQFS

https://elements.envato.com/digital-technology-logo-reveal-UZ7WQFS

After Effects CC · 15 giây · 1920 × 1080 · 522 MB · None required — theo trang Envato

- Hình ảnh: Các bảng mạch và interface dày đặc, chuyển camera, logo hiện giữa vùng tối với glitch.

- Đánh giá OPA: Hợp video giới thiệu sản phẩm mạnh về công nghệ. Ít gần vòng quét hơn NH2GY3D và dễ rối nếu để nguyên đa màu.

- Cách áp dụng đề xuất: Giảm đỏ/xanh lá, gom về xanh OPA và trắng. Giảm glitch ở đoạn cuối để người xem đọc rõ ba chữ.


### 7. Business Tech Logo Reveal — StalkerMotionGraphics / B38RMXJ

https://elements.envato.com/business-tech-logo-reveal-B38RMXJ

After Effects CC · 12 giây · 1920 × 1080 · 116 MB · None required — theo trang Envato

- Hình ảnh: Các khung nội dung trên grid hội tụ vào logo; không gian lưới phía sau.

- Đánh giá OPA: Hợp intro doanh nghiệp hoặc có hình ảnh sản phẩm đi kèm. Không phải lựa chọn gần V5GE8LJ nhất.

- Cách áp dụng đề xuất: Đổi khung và grid sang xanh OPA, kết đủ wordmark. Chỉ dùng nếu muốn kể thêm về doanh nghiệp trước logo.


### 8. Clean Tech Logo Reveal — pxlzero / GCQQ36X

https://elements.envato.com/clean-tech-logo-reveal-GCQQ36X

After Effects CC · 7 giây · 3840 × 2160 · 287 MB · None required — theo trang Envato

- Hình ảnh: Logo có cảm giác nổi khối, nền sáng với chi tiết hình học; bố cục chữ ngang rộng.

- Đánh giá OPA: Hợp hướng OPA doanh nghiệp sáng, sạch. Ít giống mẫu cuối nền tối, đưa vào như phương án mở rộng.

- Cách áp dụng đề xuất: Giữ logo OPA xanh trên nền sáng, giảm độ dày/bóng nếu làm biến dạng hình gốc. Không đổi màu là thành kiểu HUD.


## Bốn mẫu tham chiếu

- V5GE8LJ — Hi-Tech Logo Reveal / bma-prod: Vòng HUD, hạt sáng và glitch; đây là chuẩn ưu tiên của người dùng.

- PC862BB — Advanced Technology Logo / rlg_r2: Mạch điện, dữ liệu, nền tối; thiên về mạng kết nối.

- EEPLMKP — Abstract Techno Logo Reveal / TranSMaxX2: Nét neon, glitch; ít thiên về vòng HUD.

- VYBCH3Q — Hi Tech Logo Reveal / ReflectionMotion: Bệ lục giác, đường mạch sáng; có cảm giác vật thể/platform.


## Không ưu tiên / có điều kiện

- [Hi-Tech Logo Reveal — hgungor](https://elements.envato.com/hi-tech-logo-reveal-VE7TLPX): Trang yêu cầu Trapcode Form và Trapcode 3DStroke; không xếp nhóm dễ dựng.

- [Hi-Tech Logo Reveal — RwTemplates](https://elements.envato.com/hi-tech-logo-reveal-W29WBLB): Trang yêu cầu Trapcode Form, Superluminal Stardust, Video Copilot Element 3D. Khác LJEF57R không yêu cầu plugin.

- [Hi-Tech Logo Reveal — ProMotionSquad-1](https://elements.envato.com/hi-tech-logo-reveal-CGVYM3N): Không yêu cầu plugin nhưng preview nhiều vòng cơ khí và chi tiết nhọn; đánh giá là lấn logo OPA hơn nhóm đầu.

- [Hi Tech Logo Opener — StrokeVorkz](https://elements.envato.com/hi-tech-logo-opener-VFNXRP5): Thiên về gallery ảnh doanh nghiệp, xa gu vòng HUD của mẫu cuối.

- [Elegant Tech Logo Reveal — easygraphics](https://elements.envato.com/elegant-tech-logo-reveal-MYF7GT8): Bệ vuông và nền sáng, thiên về logo icon; không ưu tiên cho wordmark ngang OPA.

- [Futuristic High Tech Logo Reveal — Camotion](https://elements.envato.com/futuristic-high-tech-logo-reveal-4V62A8T): Glitch mạnh và preview thiên gaming/esports; ít phù hợp định hướng doanh nghiệp so với nhóm đầu.


## Hướng dựng đề xuất, không phải timing gốc template

0–2 giây: nền dữ liệu khởi động. 2–4 giây: vòng quét hoặc đường sáng hội tụ. 4–6 giây: OPA xuất hiện, glitch nhẹ và ngắn. 6–8 giây: tắt bớt HUD, giữ đủ wordmark rõ, ổn định. Khi tải AEP phải kiểm tra comp logo, vùng alpha, keyframe và footage trước khi quyết định sửa timing.


## Trạng thái bằng chứng

Không suy ra không-plugin nghĩa là tất cả 3D đều sửa được. Không suy ra Resizable nghĩa là vector hay vô hạn độ phân giải. Không xác nhận nhạc preview đi kèm gói template. Các ảnh trong bảng HTML là ảnh đại diện Envato, cần internet; không phải bản ghép thử logo OPA.

<!-- ===== /file: ae-logo-intro-reveal/references/NGHIEN-CUU-OPA-TECH.md ===== -->

<!-- ===== file: ae-logo-intro-reveal/references/PHAN-TICH-VIDEO-VA-KICH-BAN-BLUEPRINT.md ===== -->

# OPA — Blueprint Logo Reveal và video tham chiếu

## Nguồn đã đối chiếu

- Video người dùng: `/media/vmiz/Over Powers/THÀNH V/Download.mp4`.
- SHA256: `816bf634df21cc6da2634ce541900520e5b00d133d9e0dc30bf5e7488d079c7f`.
- Hình: 576 × 1024, 30 fps, giải mã đủ 478 frame, thời lượng hình 15,933 giây. Audio dài khoảng 15,953 giây.
- Đây là video quay màn hình một bài motion logo Framer; khung dọc còn có màn hình AE, phối cảnh, phản chiếu và watermark. Phần motion trong màn hình được dùng làm tham chiếu.
- Template người dùng cung cấp: `/media/vmiz/Over Powers/video AE/video/mẫu intro logo/Blueprint Logo Reveal/Blueprint Logo Reveal.aep`.
- File gốc có SHA256 `4d1296a63d87e2a088ad68dc6bb458782e29be760aed4702ac1727cc0da1ed31`.
- MAIN COMP của template: 3840 × 2160, 30 fps, 10 giây; file được AE hiện tại chuyển từ phiên bản 18.4.1.

## Bảng chuyển động theo video gốc

Frame đánh số từ 0. Các mốc dưới đây là mốc quan sát trên file được cung cấp, có thể lệch 1–2 frame ở đoạn có blur hoặc chuyển cảnh liên tục.

| Video gốc | Frame | Điều nhìn thấy | Cách áp dụng vào OPA |
|---|---|---|---|
| 0,000–1,633s | 0–49 | Nền xanh; điểm và đoạn thẳng lần lượt dựng silhouette Framer | Giữ cách dựng theo nét. Template dùng contour của OPA và camera/lưới có sẵn |
| 1,667–3,100s | 50–93 | Cắt sang nền tối; khối logo sáng rõ dần | Dùng quá trình outline → logo màu trong template; giữ hình OPA đúng artwork |
| 3,133–4,100s | 94–123 | Một phần logo chuyển xanh; đường chéo và nhãn nhỏ xuất hiện | Chuyển bảng màu về OPA Blue; đường phụ ưu tiên trục ngang/dọc của wordmark |
| 4,133–5,600s | 124–168 | Vệt sáng kéo dài; cảm giác khối nghiêng/xoay, chớp sáng | Lấy nhịp chuyển nét thành khối và chuyển động chiều sâu làm tham chiếu; dùng camera/echo của template |
| 5,633–6,600s | 169–198 | Glow xanh bùng lên rồi giảm, để lại outline | Giảm echo về mức vừa phải, giữ nét và logo còn đọc được |
| 6,633–7,100s | 199–213 | Logo nhỏ, cô đọng ở trung tâm | Có một giai đoạn settle trước cảnh nhận diện cuối |
| 7,133–9,100s | 214–273 | Wordmark Framer trên nền sáng → xanh nhạt → đen → xanh đậm; mỗi biến thể khoảng 0,5s | Bản intro 10s dừng ổn định; bản brand film bổ sung đoạn bảng màu và nền xanh |
| 9,133–10,100s | 274–303 | Typography phóng lớn, trượt ngang, các lớp chữ lệch nhau | Không kéo giãn wordmark OPA; giữ hình học chính xác và dùng chuyển động layer/card |
| 10,133–11,600s | 304–348 | Các thẻ màu, sau đó trở về icon trên nền trắng | Đoạn 10–12,3s trong brand film: ba thẻ OPA Blue / White / Ink |
| 11,633–12,600s | 349–378 | Logo có viền màu quang học trên nền xanh | Dùng giới hạn xanh–trắng của OPA; RGB split của template được tắt để nét gọn |
| 12,633–14,600s | 379–438 | Icon trên hình tròn rồi biến dạng thành vật thể dạng mũ | Đoạn ứng dụng icon O trên badge tròn; không cần thêm hình mũ chưa có trong bộ thương hiệu |
| 14,633–15,433s | 439–463 | Đổi nền xanh; vật thể xoay/rời khung | Chuyển về nền OPA Blue và wordmark trắng ở cảnh kết |
| 15,467–15,900s | 464–477 | Quay lại đoạn điểm/nét ban đầu, tạo cảm giác loop | Intro OPA giữ cảnh kết đủ lâu để ghép vào video doanh nghiệp |

## Kịch bản bản intro 10 giây

| Thời gian | Hình ảnh và chuyển động | Mục đích |
|---|---|---|
| 0–3s | Camera và các lớp nét của Blueprint tạo cấu trúc OPA | Giới thiệu hình học của thương hiệu |
| 3–5,2s | Contour O/P/A hoàn thiện, xuất hiện đường dựng và nhãn W/H | Gợi cảm giác thiết kế chính xác |
| 5,2–7,2s | Chuyển sang logo xanh, giảm các chi tiết kỹ thuật | Tập trung vào dấu hiệu nhận diện |
| 7,2–10s | Logo OPA và dòng “Marketing × Công nghệ × AI” | Giữ đủ thời gian đọc trước nội dung chính |

## Kịch bản bản brand film 16 giây

| Thời gian | Nội dung |
|---|---|
| 0–10s | Bản intro Blueprint dùng chung nguồn chỉnh sửa |
| 10–12,3s | Ba thẻ OPA Blue / OPA White / OPA Ink trượt vào và rời khung |
| 12,3–13,5s | Icon O từ artwork gốc xuất hiện trên badge tròn |
| 13,5–16s | Nền xanh, wordmark OPA trắng, tagline xuất hiện nhẹ và giữ đến cuối |

## Các quyết định về thiết kế

- Wordmark lấy từ artwork OPA đã cung cấp; O/P/A là shape path riêng, không gõ lại bằng font.
- Bảng màu cốt lõi: OPA Blue `#0068FF`, trắng và màu chữ tối.
- Các thước đo góc/bán kính của logo demo được tắt. Các đường `OPA_RULER_*` được dựng theo bounding box của wordmark OPA. W/H là ký hiệu chiều rộng/chiều cao, không phải tuyên bố tỷ lệ vàng hay số đo kỹ thuật được thương hiệu phê duyệt.
- Cảnh bảng màu và badge dùng shape/text gốc của AE, có thể chỉnh trong timeline.
- Audio là sound-design hướng dẫn tự tạo trong bộ asset; không lấy nhạc của video Framer hoặc nhạc bán riêng của template.
- Câu tagline đang dùng là phương án dựng cho bản này và có thể sửa ở `YOUR TEXT `.

## Nguồn để mở lại

- [Blueprint Logo Reveal — PixelTruck](https://elements.envato.com/blueprint-logo-reveal-KPBZ8GD).
- PDF hướng dẫn nằm trong thư mục `Tutorial and links` của bộ template người dùng cung cấp.
- Bảng khung hình và dữ liệu đo nằm trong bộ `Reference` của lượt phân tích trước.

<!-- ===== /file: ae-logo-intro-reveal/references/PHAN-TICH-VIDEO-VA-KICH-BAN-BLUEPRINT.md ===== -->

<!-- ===== file: ae-logo-intro-reveal/references/README-THAY-PLACEHOLDER-16S.md ===== -->

# Bộ ảnh OPA cho video SaaS Promo

## Thông số mẫu Envato

- Project: `SaaS Promo - Ai Website Promo Teaser`
- Kích thước: 1920 x 1080
- Tốc độ khung hình: 25 FPS
- Thời lượng: 25 giây
- After Effects: CC 2024 trở lên
- Không yêu cầu plugin
- Font trong hướng dẫn: Archivo và Gilroy

## Thứ tự thay vào Placeholder

| Placeholder | Ảnh đề xuất | Nội dung |
|---|---|---|
| Placeholder_01 | 01-opa-home-hero.png | Mở đầu thương hiệu OPA |
| Placeholder_02 | 02-opa-services.png | Hệ sinh thái dịch vụ |
| Placeholder_03 | 03-opa-prompt-ai.png | Prompt AI |
| Placeholder_04 | 04-opa-media-ai.png | Media AI |
| Placeholder_05 | 05-opa-ai-courses.png | Đào tạo AI |
| Placeholder_06 | 06-opa-data-api.png | Data API |
| Placeholder_07 | 08-opa-workflow-automation.png | Cách cũ và cách OPA |
| Placeholder_08 | 09-opa-ai-agents.png | AI Agents vận hành quy trình |
| Placeholder_09 | 07-opa-about.png | Kết thúc/giới thiệu OPA |

## Ba ảnh công nghệ bổ sung

- `10-opa-ai-agent-network-1920x1080.png`: dùng cho cảnh tổng quan AI Agent.
- `11-opa-business-automation-1920x1080.png`: dùng cho cảnh chuyển đổi quy trình thủ công sang tự động hóa.
- `12-opa-data-intelligence-1920x1080.png`: dùng cho cảnh Data/API/Analytics.

Ba ảnh này là hình minh họa được tạo riêng cho intro, không phải ảnh chụp sản phẩm đang chạy.

## Cách thay trong After Effects

1. Vào `File > Import > File...` hoặc nhấn `Ctrl+I`, chọn toàn bộ ảnh trong thư mục này.
2. Mở `Placeholder_01` trong Project, kéo ảnh tương ứng vào composition đó.
3. Chọn layer ảnh và nhấn `Ctrl+Alt+F` để vừa khung 1920 x 1080.
4. Nếu Placeholder đang có ảnh mẫu, giữ `Alt` rồi kéo ảnh mới từ Project thả lên layer cũ để giữ nguyên animation, scale và mask.
5. Lặp lại với Placeholder_02 đến Placeholder_09, sau đó mở composition `Main` để xem toàn bộ video.

## Nội dung chữ gợi ý

- Mở đầu: `Marketing x Công Nghệ x AI`
- Thông điệp chính: `Tổ chức toàn bộ quy trình với AI`
- Thông điệp phụ: `Giải pháp thực chiến cho doanh nghiệp Việt`
- Kết: `OPA — Tăng tốc vận hành. Tăng trưởng bền vững.`

<!-- ===== /file: ae-logo-intro-reveal/references/README-THAY-PLACEHOLDER-16S.md ===== -->
