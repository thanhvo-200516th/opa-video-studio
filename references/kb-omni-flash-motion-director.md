# kb-omni-flash-motion-director — toàn văn tài liệu của nguồn `omni-flash-motion-director`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/omni-flash-motion-director/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: omni-flash-motion-director/SKILL.md ===== -->

---
name: omni-flash-motion-director
description: >-
  Đạo diễn và kiểm soát chuyển động 2D/2.5D Motion Graphics trên Google Flow (Gemini Omni Flash 1.1 / Veo) bằng phương pháp khóa ảnh đầu–cuối (First Frame + Last Frame K00..K07), ảnh linh kiện rời (Component Ingredients C01..C04), cấu trúc Prompt 10 khối điều khiển theo phong cách After Effects Keyframe, rào chắn Invisible Data Guard (ngăn AI vẽ nhầm tên biến/số giây/tọa độ lên màn hình), quy trình Hybrid (xuất Clean Motion Plate từ Omni Flash kết hợp chữ tiếng Việt trong After Effects), và 21 công thức nhịp điệu H01–H21. Kích hoạt khi người dùng muốn viết prompt tạo video motion graphics trên Google Flow / Omni Flash, tạo các frame neo K00..K07 từ Python, hoặc điều khiển chuyển động AI mượt chuẩn After Effects.
---

# Omni Flash Motion Director — Đạo Diễn Chuyển Động 2D/2.5D Trên Google Flow (Omni Flash 1.1)

Skill này đóng gói toàn bộ phương pháp điều khiển mô hình tạo video **Google Flow (Gemini Omni Flash 1.1)** hoạt động chính xác như một phần mềm diễn hoạt keyframe (**After Effects Motion Control**), giải quyết triệt để lỗi biến dạng hình khối, lỗi sai chính tả tiếng Việt và lỗi AI tự ý vẽ thông số kỹ thuật lên màn hình.

---

## Chạy trên máy Linux này

- Python: `~/.venvs/video-skills/bin/python` (máy không có lệnh `python`/`py`; venv có numpy, scipy, matplotlib, opencv, scikit-image, Pillow, fontTools, resvg-py, faster-whisper). Lệnh `python …` trong tài liệu chạy bằng đường dẫn này.
- ffmpeg/ffprobe 8.1 ở `~/.local/bin` (libx264, FFV1, ProRes 4444, loudnorm, ebur128).
- Đường dẫn Windows trong tài liệu đã đổi sang Linux: `F:\` → `/media/vmiz/Over Powers/`, `D:\` → `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/` (bản sao lưu ổ D ngày 2026-10-28). Ổ USB `Over Powers` phải đang gắn. `E:\` không có trên máy; tài nguyên thay thế ở `/home/vmiz/Thanh/Media/TNEDIT/` (`02_SFX`, `08_Nhac_Nen`, `01_Font`, `06_B-Roll`…).
- Font Arial trong script đã đổi sang Liberation Sans (`/usr/share/fonts/truetype/liberation/`, cùng metric).
- Phần chữ tiếng Việt và keyframe đặt lên clean plate (bước AE) làm được trong EffectCraft 0.17 (`~/.local/bin/effectcraft`): Text Animator, expression, chữ tiếng Việt đủ dấu đã chạy thử đúng ngày 2026-10-29; EffectCraft không mở `.aep`.

---

## 1. Cấu Trúc Thư Mục Trong Skill

- **`references/`** — Bộ tài liệu kịch bản, prompt pack và công thức chuyển động:
  - `references/PROMPT-OMNI-FLASH-KICH-BAN-01-AE-MOTION-CONTROL.md`: Bộ Prompt điều khiển chuyển động theo chuẩn **10 khối After Effects Keyframe** kèm cơ chế **Invisible Data Guard**.
  - `references/QUY-TRINH-SAN-XUAT-VA-PROMPT-TU-ANH-OMNI-FLASH.md`: Quy trình sản xuất đồng bộ từ **Bộ Ảnh Khóa (`Frames`) + Ảnh Linh Kiện (`Components`) -> Google Flow (Omni Flash 1.1)**.
  - `references/PROMPT-PACK-OMNI-FLASH.md`: Bộ Prompt hoàn chỉnh 7 phân cảnh (`S1..S7`, tổng `35 giây`) cho phim Motion Graphics linh vật Bò OPA, bao gồm cả **Chế độ A (Frames to Video)** và **Chế độ B (Ingredients to Video)** cùng giải pháp **Hybrid (Omni Flash + After Effects)**.
  - `references/KICH-BAN-OMNI-FLASH.md` & `references/KICH-BAN-PROMO-CHATBOT-OPA.md`: Kịch bản chi tiết từng giây, góc máy và bảng phân cảnh.
  - `references/PHAN-TICH-3-MAU-ENVATO-H01-H21.md`: Bóc tách 3 mẫu quảng cáo AI/Chatbot hạng nặng từ Envato thành **21 công thức học tập (`H01..H21`)** về nhịp điệu, con trỏ chuột, gõ chữ trực tiếp và nối cảnh.
- **`scripts/`** — Công cụ sinh ảnh khóa và kiểm định clip đầu ra:
  - `scripts/build_all_frames.py`: Tự động dựng toàn bộ các khung hình neo chuẩn xác từng pixel (`1920x1080`) và bảng linh kiện (`Components`) bằng Python PIL/Cairo.
  - `scripts/build_khung.py`: Sinh bộ 8 ảnh khóa chuyển tiếp (`K00..K07`) và 4 ảnh linh kiện (`C01..C04`).
  - `scripts/do_clip.py` & `scripts/tach_pdf.py`: Đo kiểm thông số các đoạn clip xuất về từ Google Flow.

---

## 2. Hai Chế Độ Điều Khiển Trên Google Flow (Omni Flash 1.1)

### Chế độ A: Frames to Video (`First Frame + Last Frame` — Khuyên dùng để nối cảnh mượt 100%)
Để ghép 7 đoạn video (`S1..S7`) thành một bộ phim liền mạch không bị giật tại điểm cắt:
- **Quy tắc bắt cầu (`Bridge Keyframes`):** Khung hình cuối (`Last Frame`) của Cảnh `N` chính là Khung hình đầu (`First Frame`) của Cảnh `N+1`:
  - `S1`: `K00` (Đầu) → `K01` (Cuối)
  - `S2`: `K01` (Đầu) → `K02` (Cuối)
  - `S3`: `K02` (Đầu) → `K03` (Cuối)
  - ... tiếp tục cho tới `K07`.
- Chạy `python scripts/build_khung.py` hoặc `python scripts/build_all_frames.py` để xuất bộ ảnh khóa `K00..K07` trước khi tải lên Google Flow.

### Chế độ B: Ingredients to Video (`Tham chiếu linh kiện C01..C04`)
Khi muốn Omni Flash tự do sáng tạo góc máy nhưng vẫn giữ đúng 100% thiết kế thương hiệu, tải lên tối đa 3 ảnh linh kiện cho mỗi cảnh:
- `C01_mascot_bo_opa.png`: Linh vật Bò OPA chuẩn 4 góc độ.
- `C02_khung_chat_ui.png`: Giao diện khung chat / bảng điều khiển sạch.
- `C03_icon_mang_xa_hoi.png` / `C04_bang_gia_cta.png`: Các cụm huy hiệu và thẻ giá.

---

## 3. Cấu Trúc Prompt 10 Khối Chuẩn After Effects & Rào Chắn "Invisible Data Guard"

> [!CAUTION]
> **Rào chắn bắt buộc (Invisible Data Guard):** Nếu viết các ký hiệu như `Layer_1`, `[960, 540]`, `100% -> 120%`, `0.0s - 1.5s`, `cubic-bezier(0.22, 1, 0.36, 1)` trực tiếp như văn bản thường, mô hình AI tạo video sẽ **vẽ luôn các con số và tên biến đó thành chữ nổi trên màn hình video**!
> **Cách khắc phục:** Luôn mở đầu Prompt bằng khối `[INVISIBLE DIRECTOR INSTRUCTIONS — DO NOT RENDER ANY TECHNICAL LABELS, NUMBERS, TIMECODES, HEX CODES, OR LAYER NAMES AS ON-SCREEN TEXT]` và mô tả quỹ đạo bằng ngôn từ thị giác tự nhiên kèm cảm giác vật lý (*spring overshoot, whip-pan with directional motion blur, staggered cascade*).

### 10 Khối Điều Khiển Chuyển Động Trong Mỗi Prompt:
1. **Invisible Data Guard (Khối khóa chống in chữ kỹ thuật).**
2. **Global Comp & Aesthetic Specs:** Tỷ lệ `16:9` hoặc `9:16`, `60fps smooth motion feel`, phong cách `2.5D Isometric SaaS UI + Tactile Clay/Vector Mascot`, bảng màu mô tả bằng tên màu chuẩn xác.
3. **First-Frame Exact Lock (`0.0s`):** Mô tả trạng thái đứng yên/khởi đầu khớp 100% với ảnh `First Frame` đã nạp.
4. **Camera Choreography (Quỹ đạo máy quay 2.5D):** Ví dụ: *Slow dolly-in combined with a gentle 8-degree isometric orbit to the right, creating strong parallax between the foreground UI badges and the background grid*.
5. **Primary Subject / Mascot Action (Diễn xuất nhân vật/linh vật):** Mô tả rõ nhịp lấy đà (*anticipation*), hành động chính (*main action*) và nhịp nảy đàn hồi (*settle with soft secondary bounce on the ears and horns*).
6. **UI Layer Choreography & Stagger (Biên đạo giao diện lệch pha):** Các thẻ UI bay vào cách nhau một nhịp ngắn (*cascading stagger from top to bottom*), có con trỏ chuột di chuyển theo đường cong tự nhiên và nhấn nút (*cursor glides in, clicks button with a crisp tactile press-down and ripple*).
7. **Lighting & Depth Dynamics:** Ánh sáng viền (*rim light*), bóng đổ mềm dưới chân vật thể (*ambient contact shadow*) và độ mờ trường ảnh nhẹ ở tiền cảnh/hậu cảnh.
8. **Transition Out (`4.2s – 5.0s`):** Đưa toàn bộ bố cục về khớp hoàn toàn với ảnh `Last Frame` để nối sang cảnh tiếp theo không lộ vết cắt.
9. **Clean Text / Plate Policy (Quy tắc xử lý chữ):** Xem mục 4 bên dưới.
10. **Negative Constraints:** *No morphing faces, no extra limbs, no garbled pseudo-text, no watermarks, no HUD timecode overlays, no sudden jump cuts*.

---

## 4. Quy Trình Hybrid (Omni Flash + After Effects) Để Chữ Tiếng Việt Sắc Nét 100%

Các mô hình tạo video AI thường làm nhòe hoặc sai dấu tiếng Việt (`Ấ, Ể, Ộ, Ự`) khi thẻ UI đang bay nhanh. Quy trình chuẩn công nghiệp là **Phương án Hybrid**:
1. **Bước 1 — Xuất ảnh khóa không chữ (`Clean Plates`):** Chạy `build_khung.py --no-text` để tạo các ảnh khung cảnh, linh vật và thẻ UI trắng (chưa điền chữ tiếng Việt).
2. **Bước 2 — Tạo video nền chuyển động trên Google Flow:** Dùng Omni Flash 1.1 diễn hoạt linh vật 3D/2.5D, ánh sáng, camera parallax và các khung thẻ UI bay nhảy mượt mà.
3. **Bước 3 — Ghép chữ Vector tiếng Việt trong After Effects:** Đưa các clip MP4 từ Omni Flash vào After Effects (kết hợp skill `ae-script-builder`), đặt lớp chữ tiếng Việt vector chuẩn font `Be Vietnam Pro` / `Fraunces` kèm Text Animator bám theo chuyển động thẻ UI. Kết quả vừa có chuyển động 3D/2.5D sống động của AI, vừa có chữ tiếng Việt sắc nét tuyệt đối ở độ phân giải Full HD / 4K.

<!-- ===== /file: omni-flash-motion-director/SKILL.md ===== -->

<!-- ===== file: omni-flash-motion-director/references/KICH-BAN-OMNI-FLASH.md ===== -->

Ngày tạo: 23/10/2026 · Logo: `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Cowork Minh/OPA/OPA — Biểu tượng 2D V4.pdf`, biến thể **A · O Core** (đầu bò chữ O, #0068FF)
Trạng thái: kịch bản để Minh thử trên Google Flow. Chưa clip nào được tạo; hình và lời phải qua duyệt như BRAND-SPEC mục 7.

# Kịch bản motion graphic logo OPA với Gemini Omni Flash (Google Flow)

## 0. Dùng file này thế nào

1. Đọc mục 2 (khung neo) và mục 3 (từ điển After Effects). Hai mục này là cách nghĩ cho mọi kịch bản.
2. Chọn một kịch bản ở mục 6. Mới làm thì bắt đầu với **KB1** và **KB2**.
3. Trong Flow: tải **khung đầu** và **khung cuối** ghi trong kịch bản (thư mục `flow-omni/khung/`), dán prompt trong ô xám, tạo 2–4 bản.
4. Sửa bằng các câu ở mục "Sửa bằng hội thoại", mỗi lượt sửa một chỗ.
5. Đưa clip vào After Effects để khóa logo, chỉnh màu, thêm chữ tiếng Việt (mục 8), rồi soát theo mục 10.

**File liên quan:**
- `KICH-BAN-PROMO-CHATBOT-OPA.md`: promo 32 s ghép After Effects với Omni Flash, dùng các hiệu ứng học từ 3 mẫu Envato.
- `PROMPT-PACK-OMNI-FLASH.md` (bản 2): 15 prompt có thông số kiểu AE (lớp, điểm neo, keyframe, ease, tỷ lệ nhịp) kèm luật màu, VFX, SFX, ảnh tham chiếu, khóa định dạng và khóa nền; prompt khởi tạo Agent; prompt sửa có số.
- Bản phân tích 3 mẫu: `research/envato-chatbot-2026-10-23/PHAN-TICH-3-MAU.md`.

## 1. Omni Flash là gì

- "Omi Flash" là **Gemini Omni Flash**, model video của Google, ra mắt ngày 19/05/2026. Model này có trong Google Flow (`labs.google/flow`) với gói Google AI Plus, Pro hoặc Ultra.
- Bản **Omni 1.1 Flash** (cuối 08/2026) thêm **khung đầu + khung cuối**: bạn đưa ảnh mở và ảnh đóng, model tự dựng chuyển động ở giữa. Cả bộ kịch bản này dựa vào tính năng đó.
- Mỗi lần tạo được 3–10 giây, tỉ lệ 16:9 hoặc 9:16, có âm thanh đi kèm. Bản nháp độ phân giải thấp; bản chốt nâng lên 1080p hoặc 4K. Clip nối dài được theo từng bước 10 giây, tối đa 40 giây.
- Có hai cách đưa ảnh vào:
  - **Khung đầu / khung cuối:** ảnh trở thành đúng khung hình mở và đóng của clip.
  - **Ảnh tham chiếu:** model giữ nhận diện của vật nhưng không ghim vị trí.
  - Theo tài liệu API, hai cách này không dùng chung trong một lần tạo.
- Sửa bằng hội thoại: mỗi lượt sửa một thứ và nói rõ cái gì giữ nguyên.
- **Điểm yếu là chữ trong hình.** Chữ lớn còn giữ được, chữ nhỏ dễ hỏng, tiếng Việt có dấu càng dễ hỏng. Vì vậy chữ "OPA" luôn đến từ khung cuối, còn chữ tiếng Việt thêm trong After Effects.

> Chưa kiểm trên giao diện Flow của bạn. Tên nút, thời lượng và độ phân giải có thể khác theo gói tài khoản và theo đợt cập nhật. Các số trên lấy từ blog Google và tài liệu bên thứ ba, nguồn ở cuối file.

## 2. Tư duy chính: khung neo chính là keyframe

Trong After Effects, bạn đặt keyframe ở đầu và cuối, rồi chỉnh đường cong tốc độ ở giữa. Với Omni Flash cũng vậy:

```
After Effects :  ◆──────── đường cong tốc độ (Graph Editor) ────────◆
                 0 s                                                 5 s

Omni Flash    :  [Khung đầu]── prompt tả đường đi + mốc giữa ──[Khung cuối]
                 K00 nền trắng   [0.5-1.25s] ... [1.5-2.0s] ...    K01 logo chuẩn
```

- **Khung đầu, khung cuối** = keyframe đầu và cuối. Đó là ảnh logo chuẩn đã dựng sẵn (mục 4).
- **Prompt** = đường nội suy: tả vật đi đường nào, nhanh chậm ra sao.
- **Mốc thời gian trong prompt** (`[1.0-1.5s]`) = các keyframe ở giữa.

Cách này có hai lợi ích:

1. **Logo ở khung cuối luôn đúng hình**, vì AI chỉ vẽ đoạn giữa.
2. **Ghép nhiều clip liền mạch.** Khung cuối clip trước trùng khung đầu clip sau, nên cắt cứng mà không giật (KB9).

## 3. Từ điển After Effects → câu viết trong prompt

Prompt viết bằng tiếng Anh, vì thuật ngữ chuyển động tiếng Anh cho kết quả ổn định hơn. Phần giải thích vẫn bằng tiếng Việt.

| Kỹ năng After Effects | Hiểu nôm na | Viết trong prompt |
|---|---|---|
| **Keyframe** | Mốc giá trị tại một thời điểm | Khung đầu/cuối + mốc `[0.5-1.0s]` |
| **Position** (phím P) | Vị trí | `slides up from below the bottom edge into place`, `glides to the left, about a fifth of the frame width` |
| **Scale** (S) | Co giãn | `scales up from a single point to full size`, `shrinks evenly by about 4%` |
| **Rotation** (R) | Xoay | `tilts back about 8 degrees`, `swings up into place` |
| **Anchor Point** (A) | Điểm làm trục khi xoay hoặc co giãn | `pivoting on its bottom center`, `each horn rotates around its root`, `scales up from the center of its inner opening` |
| **Opacity** (T) | Độ hiện | `fades in` (ít dùng; logo OPA nên hiện bằng chuyển động) |
| **Easy Ease** (F9) | Vào êm, ra êm | `smooth ease-in-out` |
| Ease out mạnh | Nhanh rồi đáp nhẹ | `fast start, soft landing`, `snappy ease-out` |
| Ease in mạnh (Graph Editor) | Chậm rồi nhanh dần | `slowly at first, then accelerating hard` |
| **Overshoot** (vượt đà) | Quá đích một chút rồi về | `overshoots a few degrees, then settles` |
| Dao động tắt dần | Lắc qua lại nhỏ dần | `rocks back and forth in a quickly fading wobble` |
| **Hold keyframe** | Đứng yên | `holds perfectly still` (dùng ít, tránh khung chết) |
| **Motion Blur** | Nhòe khi chạy nhanh | `light motion blur only on the fastest part` |
| **Offset / Sequence Layers** | Lệch nhịp giữa các lớp | `the left horn leads; the right horn follows two frames later` |
| **Parenting + Null** | Lớp cha kéo theo lớp con | `the horns are attached to the head and move with it` |
| Null làm "máy quay" | Đẩy cả khung vào chậm | `a very slow, steady push-in of about 3%` |
| **Track Matte / Mask** | Lộ ra từ sau một mép vô hình | `slide out from behind the head, as if hidden behind it` |
| **Trim Paths** | Nét tự vẽ | `a thin outline draws itself along the silhouette` |
| **Linear Wipe** | Đổ màu theo hướng | `fills with solid blue, a clean flat wipe rising from bottom to top` |
| **Path morph** | Hình này biến thành hình kia | `the bubble's outline smoothly morphs into the U-shaped head` |
| **Motion Path + Auto-Orient** | Bay theo đường cong, mũi quay theo hướng bay | `flies in on a smooth curved arc` |
| **Camera** | Máy quay | `camera locked, no camera movement` hoặc `the camera dives into ...` |
| **loopOut("cycle")** | Lặp liền mạch | Khung đầu = khung cuối + `seamless loop` |
| **Time-Reverse Layer** (Ctrl+Alt+R) | Chạy ngược clip | Không viết vào prompt; làm sau trong AE (mục 7) |

Ba nguyên lý diễn hay dùng cho logo:

- **Lấy đà** (anticipation): lùi hoặc co lại trước khi lao tới.
- **Dư âm** (follow-through): dừng rồi còn lắc nhẹ.
- **Lệch nhịp** (overlap): phần phụ như sừng chạy trễ thân 1–2 khung.

> Luật thương hiệu: logo **chỉ co giãn đều mọi trục**. Không dùng "squash & stretch" (bóp dẹt, kéo dài) như hoạt hình thường.

## 4. Bộ ảnh đầu vào đã dựng sẵn

Dựng bằng `python tools/flow-omni/build_khung.py`. Xem nhanh cả bộ ở `flow-omni/tong-quan-khung.png`.

- Dấu đầu bò lấy từ `logo/OPA-V4-A-Core-*-2000.png`. Đo trên trang 3 của PDF: trùng hình dấu trong PDF, IoU 0,9964; phần lệch là viền nhòe JPEG.
- Chữ "OPA" và khoảng cách giữa dấu với chữ tách thẳng từ trang 3 PDF (`flow-omni/nguon/`).

**Khung neo** (mỗi khung có bản `khung/16x9/` 1920 × 1080 và `khung/9x16/` 1080 × 1920):

| File | Nội dung | Dùng trong |
|---|---|---|
| `K00_nen-trang.png` | Nền trắng trống | Khung đầu KB1, KB3, KB4 |
| `K01_dau-bo_nen-trang.png` | Dấu đầu bò xanh, giữa khung | Khung cuối KB1, KB4, KB5, KB7; cả hai đầu KB2, KB8 |
| `K02_dau-bo-trang_nen-xanh.png` | Dấu trắng trên nền #0068FF | Khung đầu KB6; bản nền xanh của KB2 |
| `K03_nen-xanh.png` | Nền #0068FF trống | Khung cuối KB6 |
| `K04_logo-chu_nen-trang.png` | Dấu + chữ OPA (cụm logo trong PDF) | Khung cuối KB3, KB9 cảnh C |
| `K05_bong-bong-chat_nen-trang.png` | Bong bóng chat xanh ba chấm | Khung đầu KB5 |
| `K06_dau-bo-lech_nen-trang.png` | Dấu đầu bò lệch trái (bản 9:16: lệch xuống dưới) | Khung đầu KB7 |
| `K07_mang-luoi-kenh_nen-xanh.png` | Dấu trắng giữa sáu nút kênh nối bằng đường thẳng, nền xanh; chừa dải dưới cho chữ | Khung cuối cảnh C4 của promo chatbot |

Bản 9:16 đặt tâm giữa vùng an toàn (chừa 250 px trên, 420 px dưới).

**Ảnh tham chiếu** (`flow-omni/tham-chieu/`) dùng khi tạo bằng chế độ tham chiếu hoặc nói chuyện với Agent của Flow: `T01` dấu xanh nền trắng, `T02` cụm logo nền trắng, `T03` dấu trắng nền xanh, `T04` bảng phong cách (màu và mẫu giao diện phẳng, không chữ). Các ảnh đều có nền đặc, vì PNG trong suốt có thể bị hiểu là nền đen.

**Điểm neo (Anchor Point)** trên PNG logo 2000 × 2000 px, dùng khi tự dựng lại trong AE. Bản tách sừng có trong `mascot/opa-mascot-parts.svg`.

| Điểm | Tọa độ (px) | Dùng cho |
|---|---|---|
| Đáy giữa chữ U | (1000, 1633) | Bật nảy, thở, lấy đà, lao tới |
| Gốc sừng trái / phải | (620, 900) / (1380, 900) | Xoay sừng |
| Tâm lòng chữ O | (1000, 1186) | Chui qua lòng O (KB6) |
| Khe trán | (1000, 876) | Hứng tin nhắn, hạt phì ra (KB8) |
| Tâm khung bao | (1000, 1000) | Mặc định của AE. Lệch tâm lòng O 186 px, nên KB6 phải dời điểm neo |

## 5. Khung prompt 6 khối

Mọi prompt trong file theo đúng thứ tự này. Muốn tự viết kịch bản mới thì điền vào khung:

```text
[KIỂU]      Flat 2D vector logo animation, clean motion graphics, {N} seconds. Plain solid {white/#0068FF} background.
[KHUNG]     Start exactly on the first frame ({mô tả}) and end exactly on the last frame ({mô tả}).
[DÒNG THỜI GIAN]
            [a-b s] {một hành động chính, viết bằng từ điển mục 3}
            [c-d s] ...
            [0-N s] A very slow, steady push-in of about 3%, landing exactly on the last frame.
                    (chỉ khi khung đầu trống; khung đầu có hình thì thay bằng
                    "The logo takes one slow, even breath, landing exactly on the last frame.")
[MÁY QUAY]  Camera locked except for the slow push-in.
[ÂM THANH]  {tiếng gắn với từng hành động}. No music, no voice, no animal sounds.
[KHÓA LOGO] Keep the logo identical to the last frame — same silhouette, proportions and horn shape,
            flat solid #0068FF, crisp vector edges. It is a flat logo, not a character: no eyes, no mouth,
            no face, no extra details. No gradients, glow, shadows, 3D, texture or text.
            Uniform scaling only, never squash or stretch.
```

Năm luật khi viết prompt:

1. **Mỗi mốc thời gian một hành động chính.** Đặt mốc trên lưới 0,25 s (nửa phách nhạc 120 BPM) để sau này dễ khớp nhạc.
2. **Luôn có chuyển động nền chậm** để không có đoạn đứng chết. V2 bản đầu bị chê "nhàm" chính vì nhiều khung đứng yên.
   - Khung đầu trống (K00, K03): đẩy máy vào 3–6 % suốt clip, đáp đúng khung cuối.
   - Khung đầu có hình: cho logo thở nhẹ ở đoạn cuối. Không đẩy máy, vì khung đầu và khung cuối đều phải đúng cỡ 100 %; đẩy máy sẽ làm khung đầu lệch cỡ.
3. **Nhịp đều.** Không xen đoạn đứng im với đoạn dồn dập. Đó là lỗi của phim 3D bản 1 ("lúc nhanh lúc chậm").
4. **Luôn có khối KHÓA LOGO.** Thiếu khối này, AI hay thêm mắt, bóng, ánh sáng 3D.
5. **Âm thanh viết theo hành động.** Bò "nói" bằng hơi mũi phì và tiếng sừng gõ "tok", không bao giờ kêu "ò".

## 6. Chín kịch bản

| # | Tên | Độ khó | Kỹ năng After Effects chính | Dài | Khung đầu → cuối |
|---|---|---|---|---|---|
| KB1 | Bật nảy | Cơ bản | Anchor Point, Scale vượt đà, Rotation quanh gốc, lệch nhịp | 5 s | K00 → K01 |
| KB2 | Thở (vòng lặp) | Cơ bản | Easy Ease dạng sóng, loopOut, xoay đối xứng | 5 s | K01 → K01 |
| KB3 | Lắp ráp + hiện chữ | Trung bình | Position, follow-through, Track Matte, Sequence Layers | 6 s | K00 → K04 |
| KB4 | Vẽ nét rồi đổ màu | Trung bình | Trim Paths, Linear Wipe, Null máy quay | 5 s | K00 → K01 |
| KB5 | Bong bóng chat hóa đầu bò | Trung bình | Path morph, lấy đà, sóng lệch nhịp | 6 s | K05 → K01 |
| KB6 | Chui qua lòng chữ O | Nâng cao | Anchor Point vào lòng O, Ease in hàm mũ, Motion Blur | 4 s | K02 → K03 |
| KB7 | Lao tới | Nâng cao | Lấy đà, hành động, dư âm, overlap | 4 s | K06 → K01 |
| KB8 | Hứng tin nhắn | Nâng cao | Motion Path, Auto-Orient, nhịp đập theo phách, hạt | 8 s | K01 → K01 |
| KB9 | Phim 20 s ghép 3 cảnh | Nâng cao | Nối khung neo, ghép, chữ tiếng Việt trong AE | 20 s | K05 → K01 → K01 → K04 |

Cách đọc bảng keyframe trong từng kịch bản:

- Cột "Giây" ghi mốc giá trị, ví dụ `0,5 → 0,9` nghĩa là giá trị đổi trong khoảng 0,5 đến 0,9 giây.
- Bảng vừa để bạn hiểu prompt đang tả gì, vừa là công thức nếu muốn tự dựng lại trong After Effects.
- Bản 9:16: dùng file cùng tên trong `khung/9x16/` và giữ nguyên prompt, trừ chỗ ghi riêng.

---

### KB1 · Bật nảy

**Dùng cho:** mở hoặc đóng video, sting logo 5 s.
**Thông số:** 16:9 · 5 s · khung đầu `K00_nen-trang` · khung cuối `K01_dau-bo_nen-trang`

| Giây | Lớp | Thuộc tính | Giá trị | Nội suy |
|---|---|---|---|---|
| 0 → 0,5 | — | — | Nền trắng, chưa có gì | — |
| 0,5 → 0,9 | Đầu chữ U | Scale, Anchor ở đáy giữa | 0 % → 112 % | Ease out mạnh |
| 0,9 → 1,1 → 1,25 | Đầu chữ U | Scale | 112 → 95 → 100 % | Easy Ease |
| 0,75 → 1,25 → 1,4 | Sừng trái | Rotation, Anchor ở gốc sừng | −40° → +6° → 0° | Ease out, vượt đà |
| 0,82 → 1,32 → 1,47 | Sừng phải | Rotation | +40° → −6° → 0° | Trễ sừng trái 2 khung |
| 0 → 5,0 | Null "máy quay" (cha của cả logo) | Scale | 97 → 100 % | Tuyến tính, chậm đều |
| suốt clip | Mọi lớp | Motion Blur | Bật | — |

```text
Flat 2D vector logo animation, clean motion graphics, 5 seconds. Plain solid white background. Start exactly on the first frame (empty white) and end exactly on the last frame (the OPA bull-head logo).

[0.0-0.5s] Empty white canvas.
[0.5-1.25s] The U-shaped head pops up from a single point at its bottom center: it scales up quickly to about 112%, dips to 95%, then settles at full size. Snappy ease-out, light motion blur only on the fastest part.
[0.75-1.5s] The two horns sprout from their roots where they join the head, growing outward to the tips. Each horn swings up into place around its root, overshoots by a few degrees, then settles. The left horn leads; the right horn follows two frames later.
[0-5.0s] The whole time, a very slow, steady push-in of about 3%, so the frame never feels frozen. It lands exactly on the last frame.

Camera: locked and centered, only the slow push-in.
Audio: a soft pop when the head appears, two crisp wooden "tok" clicks as the horns lock, a faint airy whoosh. No music, no voice, no animal sounds.
Brand lock: keep the logo identical to the last frame — same silhouette, proportions and horn shape, flat solid #0068FF, crisp vector edges. It is a flat logo, not a character: no eyes, no mouth, no face, no extra details. No gradients, glow, shadows, 3D, texture or text. Uniform scaling only, never squash or stretch.
```

**Ý prompt:** đầu chữ U bật lên từ đáy và vượt đà một nhịp. Hai sừng mọc từ gốc, lệch nhau 2 khung. Máy đẩy vào chậm suốt clip để không có khung chết.

**Sửa bằng hội thoại:**
- `Keep everything else exactly the same. Only make the bounce of the head smaller and softer.`
- `Keep everything else exactly the same. Only make the horns start 0.25 seconds earlier.`

**Lỗi hay gặp:** sừng mọc từ ngọn xuống, hoặc bay từ ngoài vào. Sửa bằng câu `the horns grow from the root at the head outward to the tip, never from outside the frame`.

---

### KB2 · Thở (vòng lặp)

**Dùng cho:** logo nền chờ, avatar động, màn kết đứng lâu, logo góc màn hình.
**Thông số:** 16:9 hoặc 9:16 · 5 s · khung đầu = khung cuối = `K01_dau-bo_nen-trang` (bản nền xanh: `K02`, đổi "white" thành "#0068FF" và logo thành "white")

| Giây | Lớp | Thuộc tính | Giá trị | Nội suy |
|---|---|---|---|---|
| 0 → 1,25 → 2,5 | Cả logo | Scale, Anchor ở đáy giữa | 100 → 103 → 100 % | Easy Ease (dạng sóng sin) |
| 0 → 1,25 → 2,5 | Sừng trái / phải | Rotation quanh gốc | 0 → −2° / +2° → 0 | Cùng nhịp, đối xứng gương |
| 2,5 → 5,0 | Mọi lớp | — | Lặp lại y hệt | `loopOut("cycle")` |

Nhịp thở 2,5 s, sát nhịp "idle" 2,4 s của BRAND-SPEC; làm tròn để hai nhịp khớp đúng 5 s.

```text
Flat 2D vector logo animation, seamless loop, 5 seconds. Plain solid white background. The first and last frames are the same centered OPA bull-head logo, so the clip must loop perfectly.

The logo breathes calmly, two identical breaths of 2.5 seconds each: it scales up evenly to about 103% from its bottom center, then back to 100%, with smooth ease-in-out like a sine wave. On each inhale the two horns tilt outward by about 2 degrees around their roots, mirrored left and right, then return.
The motion is continuous and even: it never stops and never speeds up.

Camera: locked, no camera movement; the logo stays exactly centered.
Audio: a very soft, low breath of air on each inhale. No music, no voice, no animal sounds.
Brand lock: keep the logo identical to the first and last frame — same silhouette, proportions and horn shape, flat solid #0068FF, crisp vector edges. It is a flat logo, not a character: no eyes, no mouth, no face, no extra details. No gradients, glow, shadows, 3D, texture or text. Uniform scaling only, never squash or stretch.
```

**Ý prompt:** thở hai nhịp đều, sừng nghiêng ra đối xứng. Khung đầu trùng khung cuối nên clip tự lặp.

**Sửa bằng hội thoại:** `Keep everything else exactly the same. Only make the breathing slightly stronger, about 4%.`

**Kiểm vòng lặp:** trong AE đặt clip hai lần nối nhau rồi xem chỗ nối. Nếu giật, cắt bớt 2–4 khung cuối hoặc hòa hai đầu 4 khung.

---

### KB3 · Lắp ráp + hiện chữ OPA

**Dùng cho:** intro video thương hiệu.
**Thông số:** 16:9 · 6 s · khung đầu `K00_nen-trang` · khung cuối `K04_logo-chu_nen-trang`

| Giây | Lớp | Thuộc tính | Giá trị | Nội suy |
|---|---|---|---|---|
| 0 → 0,5 | — | — | Nền trắng | — |
| 0,5 → 1,0 | Đầu chữ U | Position Y | Từ dưới mép khung lên đúng chỗ | Ease out mạnh + Motion Blur |
| 1,0 → 1,5 | Hai sừng | Position Y + Rotation quanh gốc | Rơi từ trên xuống, xoay 20° → 0° | Ease in (rơi nhanh dần), chạm thì dừng gắt |
| 1,5 → 1,75 | Đầu chữ U | Scale, Anchor ở đáy | 100 → 97 → 100 % | Nhún khi sừng chạm (follow-through) |
| 1,75 → 2,75 | Chữ O, P, A | Position X + Track Matte | Trượt ra phải từ sau đầu bò, mỗi chữ trễ 3 khung | Ease out |
| 0 → 6,0 | Null máy quay | Scale | 96 → 100 % | Tuyến tính |

```text
Flat 2D vector logo animation, clean motion graphics, 6 seconds. Plain solid white background. Start exactly on the first frame (empty white) and end exactly on the last frame: the OPA bull-head mark on the left and the "OPA" wordmark on the right.

[0.0-0.5s] Empty white.
[0.5-1.0s] The U-shaped head slides up from below the bottom edge into its final place: fast start, soft landing, light vertical motion blur.
[1.0-1.5s] The two horns drop in from above the top edge, turning about 20 degrees as they fall, and snap onto the top of the head with a firm stop.
[1.5-1.75s] The head reacts to the impact with one tiny dip and recovery.
[1.75-2.75s] The letters O, P, A slide out to the right from behind the head, as if they were hidden behind it, one after another with a short stagger, each easing to a stop in its final position. The letters only slide; they never change shape.
[0-6.0s] A very slow, steady push-in of about 4% for the whole clip, landing exactly on the last frame.

Camera: locked except for the slow push-in.
Audio: a quick swoosh as the head rises, two wooden "tok" clicks as the horns lock, a soft low thump on the dip, three light ticks as the letters arrive. No music, no voice, no animal sounds.
Brand lock: keep the mark and the wordmark identical to the last frame — same shapes, spacing and proportions, flat solid #0068FF, crisp vector edges. No other text or letters. It is a flat logo, not a character: no eyes, no face, no extra details. No gradients, glow, shadows, 3D or texture. Uniform scaling only.
```

**Ý prompt:** đầu bò trồi lên, sừng rơi xuống khớp, đầu nhún một cái, chữ OPA trượt ra từ sau lưng đầu bò.

**Sửa bằng hội thoại:**
- `Keep everything else exactly the same. Only make the letters arrive faster, finishing by 2.5 seconds.`
- `Keep everything else exactly the same. Only remove the dip of the head.`

**Lỗi hay gặp:** chữ méo hoặc sai nét giữa clip. Nếu khung cuối đúng thì chấp nhận được, vì chữ chỉ lướt qua. Nếu chữ méo lâu, chuyển sang cách khóa logo ở mục 8, hoặc cho chữ hiện muộn hơn và nhanh hơn.

---

### KB4 · Vẽ nét rồi đổ màu

**Dùng cho:** video kiểu "bản vẽ thiết kế", giới thiệu nhận diện, mở bài giảng.
**Thông số:** 16:9 · 5 s · khung đầu `K00_nen-trang` · khung cuối `K01_dau-bo_nen-trang`

| Giây | Lớp | Thuộc tính | Giá trị | Nội suy |
|---|---|---|---|---|
| 0,25 → 1,5 | Viền xanh (Stroke 6 px) | Trim Paths Start / End | 50 / 50 % → 0 / 100 % (vẽ từ đáy giữa tỏa hai bên) | Easy Ease |
| 1,25 → 2,0 | Đầu chữ U | Linear Wipe, từ dưới lên | 100 % → 0 % | Ease in-out |
| 1,75 → 2,5 | Hai sừng | Linear Wipe dọc theo sừng | Từ gốc → ngọn | Ease out |
| 2,5 | Viền | — | Nhập vào khối màu | — |
| 0 → 5,0 | Null máy quay | Scale | 94 → 100 % | Tuyến tính |

```text
Flat 2D vector logo animation, "draw-on" style, 5 seconds. Plain solid white background. Start exactly on the first frame (empty white) and end exactly on the last frame (the OPA bull-head logo).

[0.25-1.5s] A thin, clean #0068FF outline draws itself along the logo's silhouette, starting at the bottom center of the U and growing in both directions at the same speed until the outline is complete, including both horns.
[1.25-2.0s] The U-shaped head fills with solid #0068FF, a clean flat wipe rising from the bottom to the top.
[1.75-2.5s] Each horn fills from its root to its tip.
[2.5s] The outline merges into the solid shape; nothing else changes.
[0-5.0s] Throughout the clip, a slow and steady push-in of about 6%, landing exactly on the last frame.

Camera: locked except for the push-in.
Audio: a light pencil-like scratching while the outline draws, a soft rising whoosh during the fill, one clean wooden "tok" when the horns are full. No music, no voice, no animal sounds.
Brand lock: keep the logo identical to the last frame — same silhouette, proportions and horn shape, flat solid #0068FF, crisp vector edges. It is a flat logo, not a character: no eyes, no mouth, no face, no extra details. No gradients, glow, shadows, 3D, texture or text. Uniform scaling only, never squash or stretch.
```

**Ý prompt:** nét viền tự vẽ quanh logo, rồi màu xanh đổ từ dưới lên, sừng đổ từ gốc ra ngọn. Đây đúng là động tác "reveal" trong BRAND-SPEC mục 4.

**Sửa bằng hội thoại:** `Keep everything else exactly the same. Only make the outline thinner and draw it more slowly.`

**Lỗi hay gặp:** màu đổ ra kiểu chất lỏng, có sóng và bọt. Đừng dùng chữ "liquid" hay "pour"; chỉ viết "a clean flat wipe".

---

### KB5 · Bong bóng chat hóa đầu bò

**Dùng cho:** mở video bán hàng. Câu chuyện: một tin nhắn của khách trở thành OPA.
**Thông số:** 16:9 · 6 s · khung đầu `K05_bong-bong-chat_nen-trang` · khung cuối `K01_dau-bo_nen-trang`

| Giây | Lớp | Thuộc tính | Giá trị | Nội suy |
|---|---|---|---|---|
| 0 → 1,0 | Ba chấm | Position Y | Nhún lên xuống dạng sóng, mỗi chấm trễ 3 khung | Easy Ease |
| 1,0 → 1,25 | Bong bóng | Scale | 100 → 92 % | Lấy đà |
| 1,25 → 2,5 | Bong bóng → đầu chữ U | Path (biến hình) | Khung bo tròn → chữ U, đuôi thu vào | Easy Ease |
| 1,25 → 1,75 | Ba chấm | Position + Scale | Gom vào giữa, rơi xuống lòng U rồi tan | Ease in |
| 2,25 → 3,0 | Hai sừng | Scale + Rotation quanh gốc | 0 → 100 %; −30° → +5° → 0° | Ease out vượt đà |
| 3,0 → 6,0 | Cả logo, Anchor ở đáy | Scale | 100 → 102 → 100 %, hai nhịp | Easy Ease, đáp đúng khung cuối |

```text
Flat 2D vector motion graphics, 6 seconds: a chat message turns into the OPA logo. Plain solid white background. Start exactly on the first frame (a blue chat bubble with three white dots) and end exactly on the last frame (the OPA bull-head logo).

[0.0-1.0s] The three white dots inside the bubble bounce like a "typing" indicator, one after another in a smooth wave.
[1.0-1.25s] The bubble gathers itself: it shrinks evenly by a few percent, a small anticipation.
[1.25-2.5s] The bubble's outline smoothly morphs into the U-shaped head of the logo, and the little tail retracts into the shape. The three dots slide together into the middle and drop into the hollow of the U, where they disappear.
[2.25-3.0s] The two horns grow out of the top corners of the head, each swinging up around its root with a slight overshoot before settling.
[3.0-6.0s] The logo breathes twice, slowly and evenly (about 2% bigger and back, from its bottom center), landing exactly on the last frame.

Camera: locked, no camera movement.
Audio: three soft typing "blips", a smooth airy whoosh during the morph, two wooden "tok" clicks as the horns lock. No music, no voice, no animal sounds.
Brand lock: the final logo must be identical to the last frame — same silhouette, proportions and horn shape, flat solid #0068FF, crisp vector edges. It is a flat logo, not a character: no eyes, no mouth, no face, no extra details. No gradients, glow, shadows, 3D, texture or text. Uniform scaling only.
```

**Ý prompt:** ba chấm "đang gõ", bong bóng co lại lấy đà, biến hình thành chữ U, ba chấm rơi vào lòng U, sừng mọc ra.

**Sửa bằng hội thoại:** `Keep everything else exactly the same. Only make the morph slower and smoother, from 1.25 to 2.75 seconds.`

**Lỗi hay gặp:** AI cho bong bóng "nổ" rồi logo hiện ra (cắt cảnh), không biến hình. Thêm câu `one continuous shape the whole time, no cut, no flash, no dissolve`.

---

### KB6 · Chui qua lòng chữ O (chuyển cảnh)

**Dùng cho:** nối từ logo sang nội dung. Chạy ngược thì thành intro "kéo ra khỏi lòng O".
**Thông số:** 16:9 · 4 s · khung đầu `K02_dau-bo-trang_nen-xanh` · khung cuối `K03_nen-xanh`

**Bài học Anchor Point:** muốn "chui qua lòng O" thì điểm neo phải nằm ở **tâm lòng O**, tức (1000, 1186) trên PNG 2000 px. Nếu để điểm neo mặc định ở tâm khung bao (1000, 1000), máy sẽ lao vào trán bò, không vào lỗ. Trong prompt, câu `scales up from the center of its inner opening` làm việc của điểm neo.

| Giây | Lớp | Thuộc tính | Giá trị | Nội suy |
|---|---|---|---|---|
| 0 → 0,75 | Logo trắng | Scale, Anchor ở tâm lòng O | 100 → 95 % | Easy Ease (lùi lấy đà) |
| 0,75 → 3,0 | Logo trắng | Scale | 95 → 2500 % | Ease in rất mạnh (đường cong hàm mũ trong Graph Editor) |
| 0,75 → 3,0 | Logo trắng | Motion Blur | Bật, shutter angle cao | — |
| 3,0 → 4,0 | — | — | Toàn màn hình #0068FF | Cắt sang cảnh sau ở mốc này |

```text
Flat 2D vector motion graphics transition, 4 seconds. Solid #0068FF background with the white OPA bull-head logo in the center. Start exactly on the first frame and end on a completely plain #0068FF frame.

[0.0-0.75s] The logo eases back slightly, shrinking evenly by about 5%, like taking a breath before a dive.
[0.75-3.0s] The camera dives straight into the hollow center of the U-shaped head: the logo scales up from the center of its inner opening, slowly at first, then accelerating hard, so the white walls of the U rush past the edges of the frame with strong zoom motion blur, until only the blue inside the hollow fills the whole screen.
[3.0-4.0s] Plain solid #0068FF.

Audio: a rising airy whoosh that accelerates with the zoom, ending in a soft low "whump" when the screen turns fully blue. No music, no voice, no animal sounds.
Brand lock: a flat solid white logo on a flat solid #0068FF background, crisp edges, the same silhouette in every frame until it leaves the screen. It is a flat logo, not a character: no eyes, no face, no extra details. No gradients, glow, shadows, 3D, texture or text. Uniform scaling only.
```

**Ý prompt:** logo lùi lấy đà rồi máy lao thẳng vào lòng chữ O, nhanh dần, đến khi màn hình toàn xanh.

**Sửa bằng hội thoại:** `Keep everything else exactly the same. Only make the dive start later, at 1.0 second, and be even faster at the end.`

**Dùng ngược:** trong AE chọn lớp clip, nhấn **Ctrl + Alt + R** (Time-Reverse Layer). Clip thành: màn xanh → máy lùi ra khỏi lòng O → logo hiện đủ. Âm chạy ngược nghe lạ, nên tắt âm clip và gắn SFX khác.

---

### KB7 · Lao tới

**Dùng cho:** chuyển từ "vấn đề" sang "lời giải", nối với động tác "charge" trong BRAND-SPEC.
**Thông số:** 16:9 · 4 s · khung đầu `K06_dau-bo-lech_nen-trang` · khung cuối `K01_dau-bo_nen-trang`

| Giây | Lớp | Thuộc tính | Giá trị | Nội suy |
|---|---|---|---|---|
| 0 → 0,5 | Cả logo | Scale | 100 → 101,5 → 100 % | Thở nhẹ |
| 0,5 → 1,0 | Cả logo, Anchor ở đáy giữa | Rotation, Position X, Scale | −8° (ngả ra sau), lùi 2 % bề ngang, 100 → 96 % | Ease in-out (lấy đà) |
| 1,0 → 1,4 | Cả logo | Position X, Rotation, Scale | Lao về giữa khung, +6° (chúi tới), 96 → 100 % | Ease out gắt + Motion Blur ngang mạnh |
| 1,4 → 2,25 | Cả logo | Rotation | +6 → −3 → +1 → 0° | Dao động tắt dần (dư âm) |
| 1,47 → 2,32 | Hai sừng | Rotation quanh gốc | Như thân, trễ 2 khung | Overlap |
| 2,25 → 4,0 | Cả logo | Scale | 100 → 102 → 100 % | Thở một nhịp, đáp đúng khung cuối |

```text
Flat 2D vector motion graphics, 4 seconds. The OPA bull-head logo acts like a determined bull, using only its pose — no face. Plain solid white background. Start exactly on the first frame (logo on the left) and end exactly on the last frame (logo centered).

[0.0-0.5s] The logo breathes once, calm and ready.
[0.5-1.0s] Anticipation: pivoting on its bottom center, it leans back about 8 degrees, draws back a little to the left and shrinks evenly by about 4%, horns lowered, gathering power.
[1.0-1.4s] Charge: it dashes to the center of the frame, tipping forward about 6 degrees, with strong horizontal motion blur.
[1.4-2.25s] It stops hard at the center, and the momentum rocks it back and forth around its bottom center in a quickly fading wobble. The horns follow the body a couple of frames late.
[2.25-4.0s] It stands firm with one small, even breath, landing exactly on the last frame.

Camera: locked, no camera movement.
Audio: a short puff of breath through the nose on the anticipation, a fast whoosh on the charge, a deep soft thump on the stop, a light wooden "tok" from the horns. No music, no voice, no mooing or other animal sounds.
Brand lock: keep the logo identical to the last frame — same silhouette, proportions and horn shape, flat solid #0068FF, crisp vector edges. It is a flat logo, not a character: no eyes, no mouth, no face, no legs, no extra details. No gradients, glow, shadows, 3D, texture or text. Uniform scaling only, never squash or stretch.
```

**Ý prompt:** ba nhịp diễn: lấy đà (ngả sau, co lại) → lao tới (chúi trước, nhòe ngang) → dư âm (lắc nhỏ dần, sừng trễ nhịp).

**Bản 9:16:** khung đầu `khung/9x16/K06` đặt logo thấp. Thay `draws back a little to the left` bằng `crouches down a little`, `dashes to the center of the frame` bằng `dashes upward to the center of the frame`, và `horizontal motion blur` bằng `vertical motion blur`.

**Lỗi hay gặp:** AI mọc chân hoặc thêm mặt cho "con bò". Câu `using only its pose — no face` và `no legs` trong khối khóa là để chặn lỗi này. Nếu vẫn bị, bỏ câu `acts like a determined bull`.

---

### KB8 · Hứng tin nhắn

**Dùng cho:** cảnh kể chuyện "OPA không bỏ sót tin nhắn nào", giống ý phim "Thủ môn".
**Thông số:** 16:9 · 8 s · khung đầu = khung cuối = `K01_dau-bo_nen-trang`

| Giây | Lớp | Thuộc tính | Giá trị | Nội suy |
|---|---|---|---|---|
| 0 → 1,0 | Logo | Scale | 100 → 102 → 100 % | Easy Ease |
| 1,0 → 6,0 | 5 bong bóng nhỏ #003C99 | Position theo đường cong (Motion Path) + Auto-Orient | Bay từ 5 hướng mép khung, rơi qua khe trán vào lòng U; mỗi chiếc cách 1,0 s (đúng phách) | Ease in khi rơi |
| Mỗi lần hứng | Logo, Anchor ở đáy | Scale | 100 → 104 → 100 % trong 6 khung | Ease out |
| Mỗi lần hứng | Hai sừng | Rotation | ±3° → 0 | Tắt dần |
| 6,0 → 7,0 | Hạt xanh #0068FF | Particle (CC Particle World) | 2 chùm bật lên từ hai mép khe trán, tan trong 0,4 s | — |
| 7,0 → 8,0 | Logo | Scale | Thở một nhịp chậm | Đáp đúng khung cuối |

```text
Flat 2D vector motion graphics, 8 seconds, a story beat: the OPA bull catches every incoming message. Plain solid white background. The first and last frames are the same centered OPA bull-head logo.

[0.0-1.0s] The logo breathes calmly once.
[1.0-6.0s] Five small, simple chat-bubble icons (flat #003C99, a rounded bubble with a little tail, no text inside) fly in one by one from different edges of the frame, one per second, each on a smooth curved arc. Each bubble falls neatly through the gap at the top of the head, between the horns, into the hollow of the U, sinks to the bottom and dissolves. Every catch makes the head give a quick, small pulse (about 4% bigger and back) and the horns tick slightly. No bubble ever misses or lands outside.
[6.0-7.0s] After the last catch, two small puffs of #0068FF dots burst upward from the two edges of the gap at the top of the head, like a satisfied snort, and fade quickly.
[7.0-8.0s] One slow, calm breath, landing exactly on the last frame.

Camera: locked, no camera movement.
Audio: a soft whoosh for each flying bubble, a gentle pop on each catch, each pop slightly higher in pitch, a short airy nose puff on the snort. No music, no voice, no animal sounds.
Brand lock: keep the logo identical to the first and last frame — same silhouette, proportions and horn shape, flat solid #0068FF, crisp vector edges. It is a flat logo, not a character: no eyes, no mouth, no face, no extra details. No gradients, glow, shadows, 3D or text. Only the small bubbles and dots may be added, and they stay flat and simple. Uniform scaling only.
```

**Ý prompt:** 5 tin nhắn bay tới đều mỗi giây và rơi đúng vào khe trán. Mỗi lần hứng, đầu bò đập một nhịp. Cuối cảnh bò "phì" hơi xanh.

**Sửa bằng hội thoại:**
- `Keep everything else exactly the same. Only make the bubbles fly in on wider, slower arcs.`
- `Keep everything else exactly the same. Only change the number of bubbles to three, one every 1.5 seconds.`

**Lỗi hay gặp:** bong bóng có chữ bên trong (thường là chữ vô nghĩa). Giữ câu `no text inside`. Nếu vẫn có chữ, đổi thành `a plain rounded shape with a tail, completely empty`.

---

### KB9 · Phim 20 s ghép 3 cảnh

**Dùng cho:** video ngắn mạng xã hội "không bỏ sót khách". Ba clip nối nhau bằng khung neo nên cắt cứng mà liền.

```
Cảnh A (KB5, 6 s)   K05 bong bóng ──────────► K01 đầu bò
Cảnh B (KB8, 8 s)                             K01 đầu bò ──────────► K01 đầu bò
Cảnh C (mới, 6 s)                                                    K01 đầu bò ──► K04 logo + chữ
                    0 s                  6 s                    14 s           20 s
```

Cảnh A dùng nguyên prompt KB5, cảnh B dùng nguyên prompt KB8. Cảnh C "đóng logo" như sau.

**Cảnh C · thông số:** 16:9 · 6 s · khung đầu `K01_dau-bo_nen-trang` · khung cuối `K04_logo-chu_nen-trang`

| Giây | Lớp | Thuộc tính | Giá trị | Nội suy |
|---|---|---|---|---|
| 0 → 0,5 | Đầu bò | Scale | 100 → 102 → 100 % | Thở |
| 0,5 → 1,5 | Đầu bò | Position X + Scale | Sang trái 398 px (≈ 1/5 bề ngang), thu còn 65 % | Easy Ease + Motion Blur |
| 1,25 → 2,25 | Chữ O, P, A | Position X + Track Matte | Trượt ra từ sau đầu bò, mỗi chữ trễ 3 khung | Ease out |
| 2,25 → 6,0 | Cả cụm logo | Scale | 100 → 102 → 100 %, hai nhịp | Easy Ease, đáp đúng khung cuối |

```text
Flat 2D vector logo animation, 6 seconds. Plain solid white background. Start exactly on the first frame (the OPA bull-head logo, centered) and end exactly on the last frame (the bull-head on the left with the "OPA" wordmark on the right).

[0.0-0.5s] The logo breathes once.
[0.5-1.5s] The bull-head glides to the left, about a fifth of the frame width, while shrinking evenly to about two-thirds of its size, with smooth ease-in-out and light motion blur, settling into its place in the final lockup.
[1.25-2.25s] The letters O, P, A slide out to the right from behind the bull-head, as if hidden behind it, one after another with a short stagger, each easing to a stop. The letters only slide; they never change shape.
[2.25-6.0s] The whole lockup breathes twice, slowly and evenly (about 2% bigger and back), landing exactly on the last frame.

Camera: locked, no camera movement.
Audio: a smooth glide whoosh, three light ticks as the letters land, one warm low wooden "tok" at the end. No music, no voice, no animal sounds.
Brand lock: the mark and the wordmark must match the last frame exactly — same shapes, spacing and proportions, flat solid #0068FF, crisp vector edges. No other text. It is a flat logo, not a character: no eyes, no face, no extra details. No gradients, glow, shadows, 3D or texture. Uniform scaling only.
```

**Cảnh C bản 9:16:** cụm logo trong khung dọc nhỏ hơn. Thay `about a fifth of the frame width` bằng `about a quarter of the frame width`, và `to about two-thirds of its size` bằng `to a little less than half of its size` (đo: dịch 298 px, còn 43 %).

**Ghép trong After Effects:**

1. Tạo comp 1920 × 1080 dài 20 s. Đặt fps theo clip Flow (xem trong Interpret Footage).
2. Đặt A ở 0 s, B ở 6 s, C ở 14 s, nối đuôi nhau, cắt cứng.
3. Soát chỗ nối: khung cuối clip trước và khung đầu clip sau phải giống nhau. Nếu màu lệch nhẹ giữa hai clip, chỉnh Curves cho clip sau khớp clip trước.
4. Thêm chữ tiếng Việt bằng font Be Vietnam Pro 800, cụm nhấn Fraunces Italic 800, viết hoa đầu dòng, tối đa 7–9 chữ mỗi khung (BRAND-SPEC mục 2). Gợi ý lời, **chờ Minh duyệt**:
   - Cảnh A (0–6 s): "Khách nhắn lúc nửa đêm?"
   - Cảnh B (6–14 s): "OPA hứng trọn từng tin nhắn"
   - Cảnh C (14–20 s): "Không bỏ sót khách nào" + `opa.business`
5. Âm: tắt âm ba clip Flow, vì mỗi clip tự tạo âm riêng nên ghép lại sẽ lệch nhau. Dựng lại SFX từ thư viện `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx`, rồi master −16 LUFS và bản đăng mạng xã hội −14 LUFS (BRAND-SPEC mục 9).

## 7. Quy trình làm trong Flow

Tên nút dưới đây theo mô tả của các bài hướng dẫn; giao diện thật có thể khác.

1. Vào `labs.google/flow`, tạo **project mới** (ví dụ "OPA logo motion").
2. Chọn model **Omni Flash**, bản 1.1 nếu có. Chọn tỉ lệ 16:9 hoặc 9:16 và thời lượng theo kịch bản.
3. Bật chế độ **khung đầu / khung cuối**. Tải ảnh từ `flow-omni/khung/16x9/` (hoặc `9x16/`) đúng tên ghi trong kịch bản.
4. Dán prompt trong ô xám, tạo **2–4 bản**.
5. Chọn bản gần ý nhất, rồi sửa bằng hội thoại. Mỗi lượt một thay đổi, luôn mở đầu bằng `Keep everything else exactly the same. Only ...`.
6. Khi ưng: nâng lên **1080p** rồi tải MP4.
7. Chỉ dùng Agent của Flow khi muốn hỏi ý tưởng hoặc tạo hàng loạt biến thể. Khi cần đúng logo, dùng chế độ khung như trên.

**Nếu Flow của bạn chỉ cho khung đầu, không cho khung cuối:**

1. Làm ngược. Ví dụ KB1: lấy `K01` (logo) làm khung đầu và viết prompt cho logo "rút vào": sừng thu về gốc, đầu U co về một điểm ở đáy, còn nền trắng.
2. Trong AE nhấn **Ctrl + Alt + R** để đảo clip. Logo sẽ đúng hình ở cuối, vì khung đầu gốc giờ thành khung cuối.
3. Tắt âm clip đảo và gắn SFX mới.

## 8. Hậu kỳ trong After Effects

**Khóa logo ở khung cuối** (khi AI làm logo lệch nhẹ ở đoạn đứng):

1. Kéo đúng file khung cuối (ví dụ `K01_dau-bo_nen-trang.png`) lên lớp trên cùng, đặt ở 0,5 s cuối clip.
2. Đổi blend mode lớp đó sang **Difference**. Chỗ nào ra đen tuyền là trùng; viền sáng là chỗ lệch.
3. Đổi blend mode về **Normal**. Cho Opacity 0 → 100 % trong 3–4 khung để logo chuẩn "đè" lên mà mắt không thấy.

**Màu:**
- Dùng bảng **Info** để đo màu logo. Phải ra ≈ (0, 104, 255).
- Nếu lệch, dùng **Effect → Color Correction → Change to Color** hoặc **Curves**.
- Nền trắng phải đúng (255, 255, 255). AI hay cho nền ngà hoặc xám nhẹ.

**Khung hình:** giữ fps gốc của clip Flow. Đừng bật Frame Blending hay Pixel Motion để nội suy khung, vì dễ làm nhòe viền logo.

**Chữ và âm:** theo bước 4–5 của KB9.

**Xuất:** H.264 qua Media Encoder. Đo lại màu xanh trên MP4. Nếu lệch, gắn thẻ màu bt709 như đã làm với video "OPA Agent × Pancake".

## 9. Lỗi hay gặp và câu sửa

| Hiện tượng | Câu thêm vào prompt hoặc lượt sửa |
|---|---|
| Logo méo ở giữa clip | `Keep the exact silhouette in every frame; only move, rotate and scale it as a rigid shape.` Rút ngắn chuyển động, giảm góc xoay |
| Thêm mắt, miệng, mặt, chân | `It is a flat logo, not a character: no eyes, no mouth, no face, no legs.` Bỏ các từ như "cute", "alive", "character" |
| Có bóng, ánh sáng, 3D, gradient | `Flat vector, no lighting, no shading, no depth.` |
| Máy quay tự trôi, lắc | `Camera locked, no camera movement.` |
| Xuất hiện chữ lạ | `No text anywhere in the frame.` |
| Chữ OPA méo | Cho chữ hiện muộn và nhanh; khóa bằng khung cuối (mục 8) |
| Nhịp không đúng mốc | Sửa một mốc mỗi lượt: `Only make the horns lock at 1.25 seconds instead.` |
| Đứng yên quá lâu, "nhàm" | `The motion never fully stops; keep a slow, steady push-in until the end.` (khung đầu trống) hoặc `keep breathing gently until the end.` (khung đầu có hình) |
| Nhạc lạ, tiếng bò kêu | `No music, no voice, no mooing or other animal sounds.` |
| Không ra đúng khung cuối | Kiểm lại đã chọn chế độ khung chưa; hoặc làm ngược + Time-Reverse (mục 7) |

## 10. Checklist trước khi gửi duyệt

- [ ] Khung cuối trùng logo chuẩn: lớp Difference ra đen (mục 8).
- [ ] Màu đo ra ≈ (0, 104, 255); nền trắng (255, 255, 255) hoặc xanh đúng.
- [ ] Không mắt, miệng, mặt, chân; không chi tiết lạ.
- [ ] Không gradient, glow, bóng đổ, 3D bóng loáng (BRAND-SPEC mục 1).
- [ ] Không méo: chỉ co giãn đều.
- [ ] Ngọn sừng cách mép khung ít nhất 24 px.
- [ ] Không chữ lạ; chữ "OPA" đúng nét; chữ tiếng Việt thêm bằng AE.
- [ ] Nhịp đều, không đoạn đứng chết dài.
- [ ] Âm: không tiếng bò kêu, không nhạc có bản quyền; master −16 LUFS, bản mạng xã hội −14 LUFS.
- [ ] Hùng duyệt hình, Minh duyệt lời trước khi đăng (BRAND-SPEC mục 7).

## Nguồn

- Google, "Introducing Gemini Omni" (ra mắt 19/05/2026, đầu vào, sửa bằng hội thoại, SynthID): https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-omni/
- Google, cập nhật Flow với Gemini Omni (Agent, công cụ Flow): https://blog.google/innovation-and-ai/models-and-research/google-labs/flow-updates/
- Atlas Cloud, tóm tắt hướng dẫn prompt Gemini Omni của Google DeepMind (5 khía cạnh, mỗi lượt sửa một chỗ; bên thứ ba): https://www.atlascloud.ai/vi/blog/guides/gemini-omni-prompt-guide
- Segmind, so sánh Omni Flash 1.0 và 1.1 (3–10 s, 16:9 / 9:16, khung đầu-cuối, mốc `[0-3s]`, chữ còn yếu; bên thứ ba): https://blog.segmind.com/gemini-omni-1-1-flash-features-examples-and-1-0-compared/
- Runware, tài liệu khung đầu-cuối và ảnh tham chiếu của Omni 1.1 (khung không dùng chung với tham chiếu; bên thứ ba): https://runware.ai/docs/models/google-gemini-omni-flash-1-1/guides/first-and-last-frame · https://runware.ai/docs/models/google-gemini-omni-flash-1-1/guides/reference-driven-video
- Android Authority, Flow nhận Omni 1.1 Flash với khung đầu-cuối, nối dài tới 40 s (28/08/2026; trang chặn truy cập trực tiếp, nội dung đọc qua kết quả tìm kiếm): https://androidauthority.com/google-flow-gemini-omni-1-1-flash-video-update-3704288
- Atlabs, cấu trúc prompt Omni Flash (bên thứ ba): https://www.atlabs.ai/blog/ultimate-gemini-omni-flash-prompting-guide-2026

<!-- ===== /file: omni-flash-motion-director/references/KICH-BAN-OMNI-FLASH.md ===== -->

<!-- ===== file: omni-flash-motion-director/references/KICH-BAN-PROMO-CHATBOT-OPA.md ===== -->

Ngày tạo: 23/10/2026 · Dựa trên phân tích 3 mẫu Envato: `research/envato-chatbot-2026-10-23/PHAN-TICH-3-MAU.md` (mã hiệu ứng H01–H21)
Trạng thái: kịch bản, chưa dựng.
- Toàn bộ chữ trên màn hình là **gợi ý, chờ Minh duyệt lời**.
- Cảnh 3 có một chỗ **hỏi Hùng** (khung chat nghiêng 2.5D).

# Promo 32 s "OPA trực chat cho đội bán hàng"

## 0. Mạch truyện

Khách nhắn khắp nơi → một khách hỏi → OPA trả lời ngay và ghi vào CRM → một OPA trực mọi kênh → không bỏ sót khách nào → logo và lời mời.

Mạch này lấy khung kể chuyện của mẫu 2 (vấn đề → giới thiệu → tính năng → kết), giao diện chat của mẫu 1 và mẫu 3, và chuyển động logo của bộ KB1–KB9.

## 1. Phân công công cụ

Chia việc theo một luật: **cảnh nào có chữ tiếng Việt phải đúng thì làm bằng After Effects; chuyển động hình khối thì giao Omni Flash.**

| Cảnh | Giây | Công cụ | Nội dung | Hiệu ứng | Khung đầu → cuối (Omni) |
|---|---|---|---|---|---|
| C1 | 0–4 | After Effects | Tin nhắn dồn, huy hiệu đỏ đếm số | H18, H11, H02, H01 | — |
| C2 | 4–8 | After Effects | Khách gõ câu hỏi, máy bám theo chữ | H07, H06, H08 | — |
| C3 | 8–14 | After Effects | OPA trả lời, ghi CRM, tiêu đề đổi từ | H17, H12, H06, H04, H21 | — |
| C4 | 14–20 | **Omni Flash** + chữ AE | Một OPA trực mọi kênh (mạng lưới) | H10, H01 | `K02` → `K07` |
| C5 | 20–26 | **Omni Flash** + chữ AE | Hứng tin nhắn, không bỏ sót | KB8 rút gọn, H03 | `K01` → `K01` |
| C6 | 26–32 | **Omni Flash** + chữ AE | Đóng logo, khẩu hiệu, nút CTA | KB9 cảnh C, H07 | `K01` → `K04` |

**Khung hình:** 16:9, 1920 × 1080, comp 30 fps như video "OPA Agent × Pancake" đã duyệt. Clip Omni đặt thẳng vào comp; soát giật ở đoạn chạy nhanh, vì fps của clip Omni có thể khác 30.

**Nhịp:**
- 120 BPM, một phách = 0,5 s, mọi mốc nằm trên lưới 0,25 s.
- Cảnh dài 4 hoặc 6 s.
- Chữ có mặt ở mọi cảnh, mỗi nhịp một câu.
- Không đoạn nào đứng yên quá 0,5 s.

## 2. Từng cảnh

### C1 · 0–4 s · "Tin nhắn dồn" (After Effects, nền trắng)

**Chữ (gợi ý):** "Khách nhắn khắp nơi" — tiêu đề Be Vietnam Pro 800, 88 px, góc trên trái, lề 72 px.

| Giây | Lớp | Thuộc tính | Giá trị | Nội suy / hiệu ứng |
|---|---|---|---|---|
| 0,25 / 0,75 / 1,25 | 3 bong bóng khách (nền #E6F0FF, chữ #0A0A0A, 38 px) | Scale, Anchor ở góc đuôi | 0 → 105 → 100 % trong 8 khung | H18, lệch nhau 0,5 s |
| 0,5 → 2,0 | Tiêu đề | Text Animator theo ký tự; trong animator: Opacity 0 %, Position X +40, Blur 12 | Range Start 0 → 100 % | H02, Ease out |
| 1,25 → 3,0 | 3 huy hiệu đỏ `ALERT #E5484D` | Slider "So" | 1 → 12 · 1 → 27 · 1 → 99 (hiện "99+") | H11, Ease in; huy hiệu nảy 100 → 115 → 100 % mỗi lần tăng chục |
| 2,5 → 3,5 | 3 bong bóng nhỏ thêm | Scale | Bật dày hơn, lệch 0,25 s | Tạo cảm giác "dồn dập" |
| 0 → 3,75 | Null máy quay | Scale | 100 → 104 % | Tuyến tính |
| 3,75 → 4,25 | Khối #0068FF phủ kín | Position X | Quét từ trái sang, che rồi để lại nền xanh | H01, Ease in-out |

Câu chữ trong bong bóng (giả, chung chung): "Còn hàng không shop?", "Ship Hà Nội mấy ngày ạ?", "Giá sỉ thế nào ạ?".

### C2 · 4–8 s · "Khách hỏi" (After Effects, nền xanh #0068FF)

**Chữ:** câu khách gõ "Shop còn size M không ạ?" (gợi ý), Be Vietnam Pro 500, 48 px, chữ đen trong ô trắng.

| Giây | Lớp | Thuộc tính | Giá trị | Nội suy / hiệu ứng |
|---|---|---|---|---|
| 4,25 → 4,5 | Nút "+" tròn trắng | Scale | 0 → 110 → 100 % | Bật, Ease out |
| 4,5 → 4,9 | Ô nhập trắng | Rectangle Size, Roundness = cao/2, Anchor mép trái | [96, 96] → [1100, 96] | H07, Ease out mạnh |
| 4,9 → 6,9 | Chữ câu hỏi | Source Text gõ dần (expression mục 4) | 0 → 24 ký tự | H06 |
| 4,9 → 6,9 | Null máy quay | Scale 150 %, Position X bám mép phải chữ | Trôi đều sang phải | H08 |
| 6,9 → 7,25 | Nút gửi: tròn trắng, dấu đầu bò xanh nhỏ ở giữa | Scale | 0 → 110 → 100 % | Bật |
| 7,25 → 8,0 | Null máy quay | Scale, Anchor ở tâm nút gửi | 150 → 900 % | Ease in mạnh; nút trắng phủ kín màn hình → nối sang C3 |

### C3 · 8–14 s · "OPA trả lời" (After Effects, nền trắng)

**Chữ (gợi ý):**
- **Tiêu đề đổi từ (H04):** "OPA *trả lời ngay*" → "OPA *ghi vào CRM*" → "OPA *có báo cáo*". Cụm nhấn dùng Fraunces Italic 800 kèm khối đánh dấu quét dưới chữ (BRAND-SPEC mục 2).
- **Bong bóng OPA:** "Dạ còn ạ! Anh chị cho OPA xin số điện thoại để giữ hàng nhé."
- **Chip:** "✓ Đã ghi vào CRM".

| Giây | Lớp | Thuộc tính | Giá trị | Nội suy / hiệu ứng |
|---|---|---|---|---|
| 8,0 → 9,0 | Khung chat (thẻ trắng, viền 2 px #0068FF, bo 32 px); avatar OPA ở đầu khung | Scale, Anchor ở tâm avatar | 900 → 100 % | H17 zoom ra: hóa ra nút gửi là avatar OPA |
| 8,0 → 9,0 | Khung chat | Y Rotation (lớp 3D) | 20° → 0° | H12 không glow. **Hỏi Hùng**; nếu không duyệt thì bỏ dòng này |
| 9,0 → 9,5 | Bong bóng khách (câu C2) | Position Y + Scale từ góc đuôi | Trượt vào khung | H18 |
| 9,5 → 10,25 | Ba chấm "đang gõ" của OPA | Position Y (expression sóng) | Nhún lệch pha | H06 |
| 10,25 → 11,75 | Bong bóng OPA (nền #0068FF, chữ trắng 38 px) | Source Text gõ dần + Size theo chữ | Bong bóng giãn theo chữ. Dùng chữ dạng khung (paragraph text) rộng ~620 px để câu tự xuống dòng | H06 |
| 11,75 → 12,25 | Chip "Đã ghi vào CRM" (viền xanh, dấu tích xanh) | Scale | 0 → 110 → 100 % | H21 |
| 8,5 → 13,5 | Tiêu đề | Đổi từ ở 9,0 · 11,75 · 12,75 s | Từ cũ nhòe bay lên, từ mới nhòe đi vào trong 8 khung | H04; lần đổi 11,75 s trùng lúc chip bật |
| 13,75 → 14,25 | Khối #0068FF | Position X | Quét che, lộ cảnh C4 | H01 |

### C4 · 14–20 s · "Mọi kênh" (Omni Flash 6 s: `K02` → `K07`, chữ thêm bằng AE)

**Chữ (gợi ý, AE, dải dưới y 900–1015):** "Một OPA trực mọi kênh". Chữ trắng, 48 px, hiện từ nhòe (H03) ở 15,5 s.

```text
Flat 2D vector motion graphics, 6 seconds. Plain solid #0068FF background. Start exactly on the first frame (the large white OPA bull-head logo, centered) and end exactly on the last frame (a smaller white logo in the middle of a network of six white round icons joined by thin white lines).

[0.0-1.0s] The logo takes one calm breath.
[1.0-2.5s] The camera pulls back smoothly: the logo shrinks evenly to about 60% of its size and rises slightly, staying centered horizontally.
[1.5-3.0s] Six white round icon buttons burst outward from behind the logo one after another, clockwise, each flying along a straight line with light motion blur and settling into its place on a ring around the logo with a small overshoot.
[2.5-4.0s] Thin straight white lines draw themselves from the logo out to each icon, then around the ring from icon to icon.
[4.0-6.0s] The icons pulse gently one by one, clockwise, like messages arriving, and everything lands exactly on the last frame.

Camera: only the smooth pull-back, no rotation.
Audio: a soft whoosh for the pull-back, six light pops as the icons arrive, a gentle rising shimmer while the lines draw. No music, no voice, no animal sounds.
Brand lock: flat solid white shapes on a flat solid #0068FF background, crisp vector edges. The logo keeps the exact silhouette of the first and last frames. Icons stay simple and identical to the last frame; no photos, no faces, no text. No gradients, glow, shadows, 3D or texture. Uniform scaling only.
```

**Vì sao giao Omni:** sáu nút bay ra, đường nối tự vẽ, máy lùi là chuyển động hình khối hữu cơ, Omni làm mượt mà không cần dựng từng đường. Khung cuối `K07` ghim đúng vị trí cuối, nên mạng lưới luôn gọn. Mẫu 2 cũng không vẽ đường nối trực tiếp mà dùng video dựng sẵn (`02_Scene_Lines.mov`).

**Nối sang C5:** ở 19,75 → 20,25 s, một khối trắng quét từ trái sang (H01 bản trắng) che chỗ nối từ nền xanh sang nền trắng.

### C5 · 20–26 s · "Không bỏ sót" (Omni Flash 6 s: `K01` → `K01`, chữ thêm bằng AE)

**Chữ (gợi ý, AE, góc trên):** "Không bỏ sót *khách nào*". Hiện từ nhòe (H03) ở 20,5 s; cụm nhấn dùng Fraunces + khối đánh dấu.

Đây là KB8 rút còn 6 s và 3 bong bóng. Bong bóng chỉ bay từ trái, phải và dưới, để vùng trên trống cho chữ.

```text
Flat 2D vector motion graphics, 6 seconds: the OPA bull catches every incoming message. Plain solid white background. The first and last frames are the same centered OPA bull-head logo.

[0.0-0.75s] The logo breathes calmly once.
[0.75-4.5s] Three small, simple chat-bubble icons (flat #003C99, a rounded bubble with a little tail, no text inside) fly in one by one, one every 1.25 seconds, from the left edge, the right edge and the bottom edge, never from the top. Each flies on a smooth curved arc and falls neatly through the gap at the top of the head, between the horns, into the hollow of the U, sinks to the bottom and dissolves. Every catch makes the head give a quick, small pulse (about 4% bigger and back) and the horns tick slightly. No bubble ever misses.
[4.5-5.25s] Two small puffs of #0068FF dots burst upward from the two edges of the gap at the top of the head, like a satisfied snort, and fade quickly.
[5.25-6.0s] One calm breath, landing exactly on the last frame.

Camera: locked, no camera movement.
Audio: a soft whoosh for each bubble, a gentle pop on each catch, each pop slightly higher in pitch, a short airy nose puff on the snort. No music, no voice, no animal sounds.
Brand lock: keep the logo identical to the first and last frame — same silhouette, proportions and horn shape, flat solid #0068FF, crisp vector edges. It is a flat logo, not a character: no eyes, no mouth, no face, no extra details. No gradients, glow, shadows, 3D or text. Only the small bubbles and dots may be added, and they stay flat and simple. Uniform scaling only.
```

**Nối sang C6:** khung cuối C5 trùng khung đầu C6 (`K01`), nên cắt cứng.

### C6 · 26–32 s · "Đóng" (Omni Flash 6 s: `K01` → `K04`, chữ và nút thêm bằng AE)

Dùng nguyên prompt **KB9 cảnh C** trong `KICH-BAN-OMNI-FLASH.md`.

**Phần AE thêm dưới cụm logo:**
- 29,0 s: dòng "Đối tác vận hành AI cho đội bán hàng" (chữ đã có trong màn kết BRAND-SPEC mục 4), 48 px, đen, hiện từ nhòe (H03), tâm y ≈ 790.
- 30,0 → 30,5 s: nút CTA, chấm tròn #0068FF kéo thành viên thuốc (H07), chữ trắng "opa.business" (`links.json`), tâm y ≈ 900.
- 30,5 → 32 s: nút thở nhẹ 100 → 102 → 100 % cùng nhịp cụm logo.

## 3. Cách dựng project After Effects (học từ mẫu 1 và 2)

```
PROMO_OPA_32s (1920×1080, 30 fps, marker C1…C6)
├─ 00_DIEU_KHIEN   Null có 6 Color Control: XANH #0068FF · DEN #0A0A0A · TRANG #FFFFFF
│                  · XANH_NHAT #E6F0FF · XANH_DAM #003C99 · ALERT #E5484D
├─ 01_HOLDER       Logo_Holder (PNG logo/OPA-V4-A-Core-*-2000.png), Omni_C4, Omni_C5, Omni_C6
├─ 02_UI           PRE_BongBong_Khach, PRE_BongBong_OPA, PRE_O_Nhap, PRE_Chip, PRE_HuyHieu, PRE_NutCTA
└─ 03_CANH         C1_TinNhanDon, C2_KhachHoi, C3_OPATraLoi, C4_MoiKenh, C5_KhongBoSot, C6_Dong
```

- **Màu:** mọi Fill lấy từ lớp điều khiển, ví dụ `comp("PROMO_OPA_32s").layer("00_DIEU_KHIEN").effect("XANH")("Color")`. Đổi một chỗ là cả phim đổi, như lớp `Background Colors` của mẫu 2.
- **Font:** Be Vietnam Pro (800 tiêu đề, 500 nội dung), "Fraunces OPA" Italic 800 cho cụm nhấn. Font này đã cài trên máy theo video "OPA Agent × Pancake".
- **Mỗi thành phần giao diện là một precomp tái dùng,** như `PRE_xx_Button` của mẫu 1.

## 4. Ba expression cần dùng

**Bong bóng giãn theo chữ đang gõ (H06).** Đặt trên Source Text của lớp chữ:

```js
txt = "Dạ còn ạ! Anh chị cho OPA xin số điện thoại để giữ hàng nhé.";
n = Math.floor(linear(time, inPoint, inPoint + 1.5, 0, txt.length));
txt.substr(0, n)
```

Đặt trên Size của Rectangle Path trong lớp bong bóng:

```js
r = thisComp.layer("Chu_OPA").sourceRectAtTime(time, false);
[r.width + 64, r.height + 40]
```

Đặt trên Position của Rectangle Path, để bong bóng giãn theo đúng phía chữ chạy:

```js
r = thisComp.layer("Chu_OPA").sourceRectAtTime(time, false);
[r.left + r.width / 2, r.top + r.height / 2]
```

Lớp bong bóng phải cùng Position và Anchor Point với lớp chữ. Cách gọn nhất: parent bong bóng vào lớp chữ, rồi đặt Position của bong bóng về [0, 0].

Gõ câu bằng Unicode dựng sẵn (NFC). Nếu dấu tiếng Việt nằm thành ký tự riêng, mỗi bước gõ sẽ hiện dấu rời khỏi chữ.

**Huy hiệu đếm số (H11).** Slider Control "So" trên lớp huy hiệu; Source Text:

```js
v = Math.round(effect("So")("Slider"));
v >= 99 ? "99+" : String(v)
```

**Ba chấm "đang gõ" (H06).** Position của từng chấm; đổi `pha` thành 0, 1, 2 cho từng chấm:

```js
pha = 0;
value + [0, -6 * Math.max(0, Math.sin((time - pha * 0.12) * 10))]
```

## 5. Âm thanh

- Tắt âm của cả ba clip Omni, vì âm từng clip không khớp nhau và không khớp phần AE.
- Gắn SFX theo hành động từ thư viện `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx`:
  - bật bong bóng: pop nhẹ;
  - huy hiệu tăng: tick;
  - quét màu: whoosh;
  - gõ chữ: phím mềm;
  - sừng: "tok";
  - hơi phì: luồng hơi.
- Nhạc nền tự tổng hợp 120 BPM.
- Master −16 LUFS; bản đăng mạng xã hội −14 LUFS (BRAND-SPEC mục 9).

## 6. Việc còn chờ

- [ ] Minh duyệt lời của 6 cảnh (mục 2).
- [ ] Hùng duyệt có cho khung chat nghiêng 2.5D (C3) không.
- [ ] Tạo 3 clip Omni (C4, C5, C6) và soát theo checklist mục 10 của `KICH-BAN-OMNI-FLASH.md`.
- [ ] Nếu muốn khớp đúng easing của mẫu Envato: tải file .aep về để đọc dữ liệu thật (mục 5 của bản phân tích).

<!-- ===== /file: omni-flash-motion-director/references/KICH-BAN-PROMO-CHATBOT-OPA.md ===== -->

<!-- ===== file: omni-flash-motion-director/references/PHAN-TICH-3-MAU-ENVATO-H01-H21.md ===== -->

Ngày đọc: 23/10/2026 · Nguồn: 3 mẫu Envato tìm bằng từ khóa "ai chatbot promo"
Trạng thái: phân tích từ video preview, cây project Envato công bố và video hướng dẫn. **Chưa mở file .aep**: trên máy không có bản tải của 3 mẫu này (đã quét `Downloads`, `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/`, `/media/vmiz/Over Powers/video AE`).

# Phân tích hiệu ứng 3 mẫu "AI chatbot promo"

## 0. Đọc nhanh

- **Mẫu 1** (Ae_Rocket): bộ 30 cảnh giao diện chatbot sáng màu, kiểu "UI pack". Học được: bong bóng chat tự giãn theo chữ, chấm tròn kéo thành ô nhập, danh sách chọn kiểu bánh xe, con trỏ bấm nút.
- **Mẫu 2** (refinality): promo kể chuyện nền tím tối. Học được: mạng lưới bung ra từ logo, huy hiệu thông báo đếm số, khung chat nghiêng vào, câu hỏi kèm nút chọn, từ cuối câu đổi liên tục, chớp màu chuyển cảnh.
- **Mẫu 3** (Yura_Kobitovich): bản MOGRT cho Premiere, nền đen tối giản. Học được: máy bám theo chữ đang gõ, zoom ra lộ thiết bị, điện thoại trồi lên với tin nhắn.
- **21 hiệu ứng** ở mục 4 đã quy về công thức After Effects, câu prompt Omni Flash và mức hợp thương hiệu OPA.
- **Các hiệu ứng đã được đem dùng** trong kịch bản promo 32 s: `OPA-Motion-graphic-mascot/flow-omni/KICH-BAN-PROMO-CHATBOT-OPA.md`.

> Cột "Cách dựng trong AE" là **suy từ hình**, chưa phải dữ liệu đọc từ file. Tên comp, thư mục và lớp điều khiển là **dữ liệu thật**, lấy từ mục "Inside the file" của Envato và video hướng dẫn. Muốn có keyframe, easing và expression thật như bộ phân tích ngày 21/10 thì phải có file .aep (mục 5).

## 1. Thông tin 3 mẫu

| | Mẫu 1 | Mẫu 2 | Mẫu 3 |
|---|---|---|---|
| Tên | AI Chatbot Promo Agent Builder UI Pack | AI Chat Agent Promo | AI Chatbot Promo for Premiere Pro |
| Tác giả | Ae_Rocket | refinality | Yura_Kobitovich |
| Link | [envato](https://app.envato.com/search/all/video-templates/659edcd0-f195-4f38-9f15-11f0660d07ac) | [envato](https://app.envato.com/search/all/video-templates/b67cac33-0451-4281-a7c8-1bf97c483e2a) | [envato](https://app.envato.com/search/all/video-templates/41a7034d-8ff7-4f2e-a0df-874ba5ef7385) |
| Phần mềm | After Effects CC | After Effects CC | **Premiere Pro** (MOGRT) |
| Khung | 1920 × 1080 | Co giãn được (comp 4K và Full HD) | 3840 × 2160 |
| fps · dài | 24 fps · 124 s | 30 fps · 56 s | 30 fps · 30 s |
| Plugin | Không cần | Không cần | Không cần |
| Gói tải | 10 MB: aep, mp4, pdf, txt | 155 MB: aep, mov, mp4, png, txt | 32,4 MB: mogrt, mp4, txt |
| Tông màu | Sáng, pastel, nền khối màu nhòe | Tím tối, viền phát sáng hồng tím | Đen, xám, chữ trắng |
| Nhạc | Không ghi | "Future Technology Industrial" (bán riêng) | "Emotional Background Electronica" (bán riêng) |

Mẫu 3 có bản After Effects riêng cùng tác giả, tên "AI Chatbot Promo". Envato liệt kê bản này trong mục "Similar by Yura_Kobitovich"; tôi chưa mở trang đó.

## 2. Cấu trúc project (dữ liệu thật từ Envato)

### Mẫu 1 · `AI Chatbot Promo Agent Builder UI Pack.aep` (369 mục, 68 comp)

| Thư mục | Số mục | Nội dung thấy được (Envato chỉ hiện 20 mục đầu mỗi thư mục) |
|---|---:|---|
| `01_MAIN_COMPS` | 30 | 30 cảnh tên thương hiệu giả "LUMORA": `_01_Bot_From_Prompt`, `_02_Support_Flow`, `_03_Support_Chat`, `_04_Agent_Setup`, `_05_Shop_Widget`, `_06_Template_Gallery`, `_07_Sales_Agent`, `_08_Lead_Router_Flow`, `_09_Demo_Booking_Chat`, `_10_Sales_Agent_Setup`, … `_20_Screening_Flow`, +10 |
| `02_PRECOMPS` | 36 | `PRE_01_Button` … `PRE_20_Button`, +16: nút bấm tách thành precomp riêng để tái dùng |
| `03_ASSETS` | 298 | Mỗi cảnh ("SLD" = slide) có bộ riêng: `SLD_01_BG_Gradient`, `SLD_01B_BTN_Base`, `SLD_01B_BTN_Shine`, `SLD_01_CARD_Result_0x_Tile`, `SLD_01_CARD_Result_03_ChannelOn_0x`, `SLD_01_DECOR_Avatar_0x_Disc`, `SLD_02_NODE_0x_Tile`… |
| Gốc | 2 | `PREVIEW` (lưới 2 × 2 bốn cảnh), `PROMO_AI` (đoạn promo 0–30 s) |

**Cách tổ chức:** mỗi cảnh là một comp độc lập. Tài sản đặt tên theo `SLD_<số cảnh>_<loại>_<tên>`. Nút bấm gồm hai lớp: `BTN_Base` (thân nút) và `BTN_Shine` (vệt sáng chạy qua).

### Mẫu 2 · `AI Chat Agent Promo.aep` (115 mục, 114 comp)

| Thư mục | Nội dung |
|---|---|
| `01. Edit Comps` (37) | `-> Edit Logo/Logo_Holder`, `-> Edit Music/Music_Holder`; mỗi cảnh có comp chữ `0x_Scene_Text01/02`; cảnh 2 có `Edit_Icons/Icon_Holder_01…06` và `Edit_Persons_Avatar/01…08_Person_Holder` |
| `02. Final Render` (2) | `Final_4k (3840 x 2160)`, `Full_HD (1920 x 1080)` |
| `03. Other/1) Scene Comps` (46) | `01_Scene` + `01_Scene_Color_Flash`; `02_Scene` + `02_Scene_EdgeGlow`, `Avatar_Comps`, `Icon_Comps`; `04_Scene_AlertComp`, `Notification_Comps`, `04_Scene_Counter01/02`, `Number_Counter/Numbers_Comp01/02`; `05_Scene_Button`, `05_Scene_Color_Flash`… |
| `03. Other/2) Assets` (12) | `Icons/01…09_Icon.png`; `Pre_Render/02_Scene_Lines.mov` |
| `03. Other/3) Controls` (7) | `Background Colors`, `Camera_Control`, `Guide_Layer`, `Icons, Buttons & UI Colors`, `Num_Control`, +2 |
| `03. Other/4) Solids` (3) | `Background`, `Edge_Glow`, `Flash` |

**Đọc từ video hướng dẫn (5:40):**
- Lớp `Background Colors` có `BG_Color_01…04` (Color Control) và `Flash_Transition` (Checkbox Control, bật/tắt chớp chuyển cảnh).
- Comp `Final_4k` 30 fps có ba lớp điều khiển ở trên cùng: `Text Colors`, `Background Colors`, `Icons, Buttons & UI Colors`. Marker comp chia cảnh `01_Scene` … `06_Scene`.
- Đổi màu một lần là cả phim đổi theo, vì mọi lớp lấy màu từ đây bằng expression. Ở phút 4–5 video hướng dẫn đổi cả mẫu sang tông xanh dương.
- **Đường nối của mạng lưới là video dựng sẵn** (`02_Scene_Lines.mov`), không phải shape động. Mẹo này giảm thời gian render.

### Mẫu 3 · MOGRT

`AI_Chatbot_Promo_MOGRT/MOGRT Files/AI Chatbot Promo.mogrt` (912,7 KB), `Font/Fonts Link.txt`, `Help/Help.mp4`. Không có file .aep. Sửa chữ trong bảng Essential Graphics của Premiere. File MOGRT xuất từ AE thường gói project AE bên trong, nhưng phải mở mới biết bản này có hay không.

## 3. Dòng thời gian từng mẫu

Đọc bằng cách lấy khung hình mỗi 0,25–0,75 s ngay trong trình duyệt. Tờ khung hình lưu ở `khung-xem/` (ảnh nhỏ, chỉ để tra cứu nội bộ).

### Mẫu 1 · đoạn `PROMO_AI` (0–30 s), sau đó là lưới 30 cảnh

| Giây | Cảnh | Hiệu ứng (mã ở mục 4) |
|---|---|---|
| 0–2 | Bong bóng khách gõ "Can you make my AI chatbot look amazing?" | H06 bong bóng giãn theo chữ |
| 2–4 | Avatar bot, ba chấm "đang gõ", trả lời "Absolutely. Meet AI Chatbot Promo." + chip gợi ý bật lần lượt | H06, chip bật so le |
| 4,5 | Khối màu xanh lá quét kín màn hình | H01 chớp/quét màu |
| 5–8,5 | Bức tường thẻ UI nghiêng, máy trôi; thẻ trắng ở giữa đếm "3 → 20 → 30 chatbot & agent scenes" | H13, H14 |
| 9 | Vệt chéo xanh quét | H01 |
| 9,5–14 | Cột chữ "Chat apps / Website widgets / Agent builder / Setup wizards / Template gallery" cuộn lên từng mục; mục đang chọn đậm, có vạch dọc; thẻ UI bên phải đổi theo | H05 |
| 14,5 | Quét màu chéo xanh dương → xanh lá | H01 |
| 15–20 | "Your brand. Every bubble." hiện từ nhòe; thẻ chat đổi tông màu bằng vạch quét dọc | H03, H16 |
| 20,5–24,5 | "Type a message. The bubble follows." Chấm tròn kéo thành ô nhập, bong bóng câu hỏi, ba nút có nhãn trượt vào so le | H03, H07, H06 |
| 25 | Quét màu xanh lá | H01 |
| 25,5–29,5 | Thẻ trắng phóng ra, "AI Chatbot Pack" gõ chữ (chữ 2 màu nhấn), hàng chip có dấu tích | H21 |
| 30–124 | Lưới 2 × 2: mỗi nhóm bốn cảnh chạy ~2,5 s rồi tan vào nền khối màu nhòe ~2 s | H20 |
| 31,6–34,8 (trong lưới) | "Describe your bot. Lumora builds it.": chữ gõ trong ô prompt có con trỏ nhấp nháy, chuột di tới nút "Generate" rồi bấm | H09 |

### Mẫu 2 · 56 s, 30 fps

| Giây | Cảnh | Hiệu ứng |
|---|---|---|
| 0–0,3 | Chớp màu hồng tím | H01 (`01_Scene_Color_Flash`) |
| 0,45–3 | "Building a strong community / is real success": chữ chạy từ trái sang kèm nhòe ngang; dòng 2 màu nhấn; ra bằng nhòe ngang | H02 |
| 3,2–6,5 | Logo AI lớn → máy lùi; avatar bay vào có nhòe chuyển động; đường nối tự vẽ từ tâm; nút icon bật; vòng ngoài mở rộng | H10 |
| 7–9 | "But managing it all / that's the challenge" | H02 |
| 9,5–12 | Hai avatar có huy hiệu đỏ đếm số tăng nhanh, "Endless notifications" | H11 |
| 12,5 | Chớp màu | H01 |
| 13–15 | "Presenting / AI Agents" + nút "Chat Agent" bật | H03 |
| 15,5–21,5 | Khung chat nghiêng 3D quay vào, viền phát sáng; tin khách → bot gõ → trả lời | H12, H06 |
| 22–26,5 | Tiêu đề đổi từ cuối: "Ready to answer questions" → "Ready to support members" | H04 |
| 27–31,5 | Máy lùi ra thành bức tường thẻ chat, trôi ngang; viên thuốc "Ready to control all processes" | H13 |
| 32–34 | "Build your own AI-powered Agent" | H02 |
| 34,5–42,75 | "How should the agent answer?" / "…sound?": nút lựa chọn bật so le, vệt chọn nhảy giữa các nút | H15 |
| 43,5–47,25 | "Teach your agents with custom data → community content → knowledge sources" | H04 |
| 48–50,25 | Mạng lưới lần hai, lùi xa hơn | H10 |
| 51 | Chớp màu | H01 |
| 51,75–55,5 | "Scale your business with AI Agents" + URL nhỏ | H03 |

### Mẫu 3 · 30 s, 30 fps

| Giây | Cảnh | Hiệu ứng |
|---|---|---|
| 0,6–1,5 | "Turn AI into your workflow" hiện từ nhòe | H03 |
| 1,7–4,6 | Nút "+" bật, ô tìm kiếm kéo dài sang phải; "Work smarter at every step" gõ ra, mép chữ mới mờ dần; máy bám theo chữ sang phải; dừng ở nút ✦ | H07, H08 |
| 4,6–6 | Nút ✦ đứng giữa → zoom ra: hóa ra nó nằm trong dock của máy tính bảng | H17 |
| 6,6–8,4 | "Save hours every single day" | H03 |
| 9–12 | Điện thoại trồi lên, tin nhắn xanh/xám bật lần lượt | H18 |
| 12,6–16,8 | "Stay ahead of the competition" → bong bóng chat trôi khắp màn hình (lớp xa gần) | H13 |
| 17,4–22,8 | Cửa sổ ứng dụng (code + khung chat) trượt vào rồi trôi chậm, tin nhắn hiện dần | H19 |
| 23,4–30 | Chuỗi câu "From request to result", "Designed for every task", "Ready for anything", "my-AI-chatbot.com" | H03 |

## 4. Thư viện 21 hiệu ứng

Cột "OPA" so với BRAND-SPEC:
- ✅ dùng được nguyên;
- ✏️ dùng được nếu chỉnh (đã ghi cách chỉnh);
- ❌ trái luật thương hiệu.

| Mã | Hiệu ứng | Thấy ở | Cách dựng trong AE (suy từ hình) | Viết cho Omni Flash | OPA |
|---|---|---|---|---|---|
| H01 | Chớp / quét màu chuyển cảnh | M2 0,3 · 12,5 · 51 s; M1 4,5 · 9 · 14,5 · 25 s | Solid `Flash` hoặc shape phủ kín. M2: Opacity 0 → 100 → 0 trong ~8 khung, bật tắt bằng checkbox `Flash_Transition`. M1: shape quét chéo, Position đi ngang khung | `a flat #0068FF panel sweeps across the frame from left to right and clears` | ✏️ Bỏ gradient hồng tím; dùng khối #0068FF phẳng quét |
| H02 | Chữ chạy từ trái kèm nhòe ngang | M2 0,45–3 · 7–9 · 32–34 s | Text Animator, Range Selector theo ký tự, Start 0 → 100 %; trong animator: Opacity 0, Position X +40, Blur ngang (hoặc Scale X 150 %); Ease out | Không giao cho Omni (chữ tiếng Việt hỏng) | ✅ Làm trong AE |
| H03 | Chữ hiện từ nhòe theo từ | M1 15 · 20,5 s; M3 nhiều câu | Animator theo Words: Blur 20 → 0, Opacity 0 → 100, Tracking −20 → 0; offset từng từ 2 khung | Không giao cho Omni | ✅ AE |
| H04 | Đổi từ cuối câu | M2 22 · 43,5–47 s | Phần đầu câu giữ nguyên; từ cuối là layer riêng (hoặc Source Text keyframe); từ cũ nhòe bay lên, từ mới nhòe đi vào; chu kỳ ~1,5 s | Không giao cho Omni | ✅ AE: "OPA **trả lời** / **ghi CRM** / **báo cáo**" |
| H05 | Danh sách cuộn kiểu bánh xe chọn | M1 9,5–14 s | Các dòng chữ con của một Null; Position Y của Null nhảy mỗi ~0,9 s (Easy Ease); Opacity từng dòng bằng expression theo khoảng cách tới dòng giữa; vạch dọc đánh dấu đứng yên | Không giao cho Omni | ✅ AE |
| H06 | Bong bóng chat giãn theo chữ + gõ chữ | M1 0–4 · 22–24,5 s; M2 16–26 s | Text Animator kiểu máy đánh chữ (Range Start theo khung). Rectangle của bong bóng lấy Size từ `sourceRectAtTime()` của chữ + lề. Ba chấm "đang gõ" nhún bằng expression sóng sin lệch pha. Chip bật Scale 0 → 110 → 100 lệch 3 khung | Chỉ bong bóng không chữ: `a simple flat chat bubble with three dots pops in` | ✅ AE (chữ tiếng Việt phải đúng) |
| H07 | Chấm tròn kéo thành ô nhập (thanh dài) | M1 20,75–22 s; M3 1,7–2,6 s | Rectangle Size [w, h] từ [h, h] → [w, h], Roundness = h/2, Anchor ở mép trái; Ease out mạnh; M3 có nút "+" bật trước | `a small dot stretches sideways into a long rounded input bar` | ✅ |
| H08 | Máy bám theo chữ đang gõ | M3 2,2–4,6 s | Null "máy quay" làm cha nhóm ô nhập; Position X = −(mép phải chữ) bằng `sourceRectAtTime`, Scale 160 %; khi gõ xong máy dừng ở nút | `the camera stays close and glides right, following the text as it is typed` | ✅ AE |
| H09 | Con trỏ chuột di và bấm nút | M1 31,6–34,8 s | Lớp con trỏ PNG có Position theo đường cong; nút Scale 100 → 94 → 100 trong 6 khung khi bấm; vệt sáng (`BTN_Shine`) chạy qua | `a mouse cursor glides to the button and clicks it; the button presses in briefly` | ✅ |
| H10 | Mạng lưới bung từ logo | M2 3,2–6,5 · 48–50 s | Máy lùi (3D camera hoặc Scale 140 → 100 %); avatar bay từ ngoài vào với Motion Blur; đường nối là `02_Scene_Lines.mov` dựng sẵn; icon bật Scale; viền glow từ comp `EdgeGlow` | `small flat icons burst outward from the logo and settle in a ring; thin straight lines draw themselves from the logo to each icon` | ✏️ **Không dùng ảnh người** (BRAND mục 1) → thay bằng biểu tượng kênh; bỏ glow; nét phẳng |
| H11 | Huy hiệu thông báo đếm số | M2 9,5–12 s | Slider Control trên lớp `Num_Control`; Source Text = `Math.round(slider)`; huy hiệu tròn đỏ co giãn nhẹ mỗi lần tăng | Không giao cho Omni (số phải đúng) | ✏️ Đỏ chỉ dùng `ALERT #E5484D` cho dấu nhỏ, đúng ý "tin bị bỏ sót" |
| H12 | Khung chat nghiêng 3D quay vào | M2 15,5–16,5 s | Lớp 3D: Y Rotation 35° → 0, Z lùi → 0, Ease out; viền phát sáng bằng comp `EdgeGlow` (Glow) | `a flat chat window swings in from a slight angle and faces the camera` | ✏️ Bỏ glow, viền phẳng 2 px #0068FF. Nghiêng 2.5D phẳng chưa có trong BRAND-SPEC → **hỏi Hùng** |
| H13 | Bức tường thẻ + máy lùi trôi | M1 5,5–8,5 s; M2 27–31,5 s; M3 14,4–16,8 s | Lưới precomp trên lớp 3D, khác độ sâu Z; máy lùi + trôi ngang chậm (parallax); thẻ gần chạy nhanh hơn thẻ xa | `the camera pulls back to reveal a wall of chat cards drifting slowly sideways` | ✅ Thẻ trắng viền xanh trên nền phẳng |
| H14 | Bộ đếm số lớn | M1 6,5–7,5 s | Slider 0 → 30, Ease out, Source Text làm tròn | Không giao cho Omni | ✏️ Chỉ đếm thứ có thật (số kênh, số bước). **Không** đếm số kết quả (BRAND mục 7) |
| H15 | Câu hỏi + nút lựa chọn | M2 34,5–42,75 s | Nút viên thuốc bật so le; khối chọn trượt sang nút được chọn (Position, Ease in-out) | Không giao cho Omni | ✏️ Nút được chọn: nền #0068FF chữ trắng; nút khác: viền xanh. Bỏ glow |
| H16 | Đổi tông màu bằng vạch quét | M1 15,5–20 s | Hai bản màu chồng nhau; Linear Wipe hoặc Track Matte theo một vạch dọc chạy ngang | `a thin vertical line sweeps across and the card switches from white to blue behind it` | ✏️ Chỉ đổi trắng ↔ xanh OPA |
| H17 | Zoom ra lộ thiết bị (nối cảnh bằng zoom) | M3 4,6–5 s | Đối tượng giữa khung ở Scale 400 % → 100 %, đồng thời lộ khung thiết bị; Ease in-out | `the camera pulls back and reveals the icon is the avatar inside a chat window` | ✅ Logo OPA → hóa ra là avatar bot trong khung chat |
| H18 | Điện thoại trồi lên, tin nhắn bật | M3 9–12 s | Điện thoại: Position Y từ dưới lên, Ease out; mỗi tin: Anchor ở góc đuôi bong bóng, Scale 0 → 105 → 100; danh sách tự đẩy lên | `a phone rises from the bottom; message bubbles pop in one by one from their tails` | ✅ |
| H19 | Cửa sổ ứng dụng trôi chậm | M3 17,4–22,8 s | Precomp cửa sổ; Position + Scale tuyến tính rất chậm suốt cảnh | `the app window drifts very slowly to the left` | ✅ |
| H20 | Nền khối màu nhòe trôi | M1 0–4 s, giữa các lưới | Hình elip màu + Gaussian Blur lớn, `wiggle()` trên Position | — | ❌ Gradient, nhòe màu trái BRAND mục 1 → dùng nền phẳng |
| H21 | Thẻ tiêu đề + chip có dấu tích | M1 25,5–29,5 s | Thẻ trắng Scale 90 → 100 %, chữ gõ ra (từ thứ hai màu nhấn), chip bật so le 3 khung | — | ✏️ Bỏ kính mờ, bóng đổ; thẻ phẳng viền xanh |

**Cách tổ chức đáng học** (áp cho project AE của OPA):

1. **Một lớp điều khiển màu duy nhất.** Mọi màu lấy từ Color Control bằng expression, như mẫu 2. Với OPA, gắn sẵn năm màu BRAND-SPEC; sau này đổi màu không phải sửa từng lớp.
2. **Comp "Holder" cho thứ khách thay:** `Logo_Holder`, `Icon_Holder_xx`, `Music_Holder`.
3. **Dựng sẵn phần nặng** (`02_Scene_Lines.mov`) để render nhanh.
4. **Marker comp đặt tên theo cảnh** để nhảy nhanh khi sửa.
5. **Mỗi cảnh một comp độc lập**, tài sản đặt tên theo cảnh (`SLD_<số>_<loại>_<tên>`), như mẫu 1.

## 5. Muốn có dữ liệu .aep thật

Bộ phân tích ngày 21/10 (`research/ae-text-audit-2026-10-21`) đã có script đọc .aep bằng ExtendScript chạy nền: `scripts/export-projects.jsx`, `analyze.py`, `build_presets.py`. Script xuất từng layer, hiệu ứng, keyframe, easing và expression. Để chạy cho bộ này:

1. Bạn tải 2 mẫu AE (10 MB và 155 MB) và file MOGRT (32,4 MB) bằng tài khoản Envato của bạn. Envato yêu cầu đăng ký tên dự án cho mỗi lần tải để cấp giấy phép, nên tôi không tải thay được.
2. Giải nén vào `research/envato-chatbot-2026-10-23/nguon/`.
3. Tôi chạy lại các script trên. Kết quả: danh sách effect thật từng layer, đồ thị easing, expression của lớp điều khiển, file `MOTION-PRESETS.json` cho bộ chatbot.

**Lưu ý giấy phép:** không đưa video preview hay file của mẫu Envato vào Google Flow làm tham chiếu chuyển động. Muốn Omni bắt chước một chuyển động, hãy dựng lại chuyển động đó bằng AE với hình OPA rồi dùng bản của mình.

<!-- ===== /file: omni-flash-motion-director/references/PHAN-TICH-3-MAU-ENVATO-H01-H21.md ===== -->

<!-- ===== file: omni-flash-motion-director/references/PROMPT-OMNI-FLASH-KICH-BAN-01-AE-MOTION-CONTROL.md ===== -->

# BỘ PROMPT GOOGLE OMNI FLASH & MOTION CONTROL (AFTER EFFECTS) — KỊCH BẢN SỐ 1 (ADS #1)

> **Dự án**: OPA Agent — AI Bán Hàng Cho Shop Dùng Pancake  
> **Kịch bản gốc**: `VIDEO 01 · Ads #1 (Flagship - 36s)` từ `https://opa-agent-video-roadmap-pitch.vercel.app/`  
> **Project After Effects tham chiếu**: `/media/vmiz/Over Powers/video AE/template intro/video edit teamplate/template 5.aep` (`Final_4k (3840 x 2160)`)  
> **Sản phẩm render mẫu**: `/media/vmiz/Over Powers/EDIT ADOBE/videointro/Final_4k (3840 x 2160)\o ping.mp4` (`3840×2160`, `30 fps`, `55.5s`)  
> **Kiến trúc Motion Control kế thừa**: `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude` (`PROMPT-PACK-OMNI-FLASH.md`, `KICH-BAN-OMNI-FLASH.md`, `PHAN-TICH-3-MAU.md`, `BAO-CAO-PHAN-TICH.md`, `PROMPT-HOAN-CHINH-OPUS.md`, `KET-LUAN-VA-PROMPT-SUA.md`, `KHUNG-DUNG.md`)

---

## PHẦN 1: GIẢI MÃ KIẾN TRÚC AFTER EFFECTS TỪ ẢNH CHỤP (`template 5.aep`) & VIDEO MẪU (`o ping.mp4`)

### 1.1. Cấu trúc cây Pre-comp trong `template 5.aep` (`Final_4k (3840 x 2160)`)
Trên ảnh chụp màn hình tại timecode `0:00:19:03` và file render mẫu `o ping.mp4`, project After Effects được tổ chức theo **Pre-comp lồng 4 tầng (Nested Pre-compositions)** kết hợp **Global Control Layers**:

```text
Final_4k (3840 x 2160) [3840×2160 | 30 fps | Anchor: 1920.0, 1080.0 | Pos: 1920.0, 1080.0 | Scale: 100%, 100% | Rot: 0x+0.0°]
 ├── # Global Controllers (Adjustment / Guide / Null Layers đầu timeline):
 │    ├── 1. Text Colors                   (Expression Control đổi màu chữ toàn cục)
 │    ├── 2. Background Colors             (Màu nền #0A142E / #FFFFFF / Gradient Blue)
 │    ├── 3. Icons, Buttons & UI Colors    (Màu pill, viền sáng EdgeGlow #2690FF / #1E40FF)
 │    ├── 4. Camera_Control                (Master Null 3D điều khiển Zoom/Pan/Parallax toàn cảnh)
 │    └── 5. Num_Control                   (Slider Control đếm số tự động: 268, 311, 159.000đ)
 │
 └── # Scene Pre-comps (Cắt theo nhịp 120 BPM = 15 frames/beat @ 30fps):
      └── 05_Scene (00:15:00 – 00:26:15)   [Cảnh khung chat 3D nghiêng đang mở trên ảnh chụp]
           ├── 05_Scene_Text01             (Header trên: "Tự trả lời khách theo tồn kho" -> H04 Word/Line Swap)
           ├── 05_Scene_Button02           (Pre-comp khung thẻ UI / Pill / Bubble)
           │    └── 05_Scene_Text02        (Layer chữ bên trong nút/bong bóng chat)
           ├── Chat_Card_3D                (3D Layer: Y Rotation +35° -> 0°, Z Position đẩy lùi, viền EdgeGlow)
           └── BG_Glow_Grid                (Lưới sáng mờ + Radial Glow chuyển động chậm)
```

### 1.2. Nguyên lý Vật lý & 5 Thông số Transform cốt lõi từ `Motion Claude` áp vào `Kịch bản số 1`

Để Google Omni Flash (hoặc After Effects) tạo ra chuyển động **mượt như sản phẩm mẫu `o ping.mp4`** và không bị "đơ hình" (47.8% khung tĩnh ở bản cũ), mọi chuyển động phải tuân thủ **5 thông số Transform + Đồ thị vận tốc (Graph Editor)**:

| Thông số AE | Quy chuẩn trong `Final_4k (3840×2160)` (Pixel) | Quy chuẩn trong Prompt Omni Flash (`%` & Ngôn ngữ tự nhiên) | Quy tắc Vật lý & Easing bắt buộc |
| :--- | :--- | :--- | :--- |
| **1. Anchor Point (Điểm neo `A`)** | • Comp / Card trung tâm: `[1920, 1080]`<br>• Bong bóng chat khách (trái): Góc dưới-trái `[0, H]`<br>• Bong bóng chat OPA (phải): Góc dưới-phải `[W, H]`<br>• Đầu Bò OPA (`U_HEAD`): Đáy giữa `[50%, 100%]`<br>• Gốc sừng trái/phải: `[22.6%, 42.1%]` & `[77.4%, 42.1%]`<br>• Form/Card bung mở: Đỉnh-trái `[0, 0]` hoặc Tâm `[W/2, H/2]` | • Luôn khóa điểm neo trước khi Scale/Rotate.<br>• Trong prompt Omni Flash: Mô tả bằng vị trí vật lý (*"from its bottom-left tail corner"*, *"from a single point at its bottom-center"*, *"around each horn's root where it joins the head"*) để AI không vẽ số tọa độ lên hình. | **Sai lầm phổ biến nhất**: Để Anchor Point ở giữa `[50%, 50%]` khi bung bong bóng chat hoặc xoay sừng làm hình bị trượt (floating pivot). |
| **2. Position (Vị trí `P`)** | • Tách X/Y (`Separate Dimensions`) hoặc 3D `[X, Y, Z]`<br>• Bước cuộn tin nhắn (Step-scroll): `ΔY = -210 px` (4K) mỗi khi có tin mới.<br>• Text Reveal (R1/H02): Trượt ngang hoặc trượt dọc qua `Alpha Track Matte` (`ΔY = +120 px -> 0 px`). | • Hệ tọa độ `(x%, y%)` với `(0%, 0%)` là góc trên-trái, `(50%, 50%)` là tâm khung hình.<br>• Tách bạch **Local Position** (vật thể tự trượt) và **Camera Null (`CAM`) Position** (khung hình đẩy tới). | **Rule R1 (Text Slide)**: `Out Influence 75.2% / In Influence 75.1%` (`cubic-bezier(0.75, 0, 0.25, 1)`).<br>**Rule R10 (Card/Mask Wipe)**: `Out Influence 15.2% / In Influence 100%` (`cubic-bezier(0.15, 0, 0, 1)` — vọt nhanh đầu, đáp cực êm). |
| **3. Scale (Tỷ lệ `S`)** | • Logo / Mascot: **Đồng nhất 2 trục** `[S%, S%]` (Tuyệt đối không Squash & Stretch méo logo).<br>• UI Pop-in: `0% -> 108% -> 100%` (trong `10–12 frames`).<br>• Mascot Reveal: `0% -> 112% -> 95% -> 100%` (`22 frames`).<br>• Camera (`CAM` Null): Push-in liên tục `96% -> 100%` suốt cảnh. | • Ghi rõ chuỗi **3-keyframe hoặc 4-keyframe spring**: `0% -> 108% -> 100%` (overshoot nhẹ 6–8%) hoặc `0% -> 112% -> 95% -> 100%`.<br>• Nút CTA / Thanh Input: Dùng `Rectangle Size [h, h] -> [w, h]` (nở từ hình tròn thành viên thuốc) thay vì kéo giãn `Scale X` làm méo bo góc (`Roundness`). | **Lò xo chuẩn (`SPRING_POP`)**: $\omega = 16, \zeta = 0.67$ (~6–8% overshoot, tắt hẳn sau 1 chu kỳ). Không bao giờ dùng Linear hoặc chỉ 2 keyframe `0% -> 100%`. |
| **4. Rotation (Góc xoay `R`)** | • Quy ước chiều kim đồng hồ = Dương (`+°`).<br>• Kim đồng hồ (Scene 1): Kim phút `0° -> +1080°` (3 vòng), kim giờ `0° -> +90°`.<br>• Bò OPA húc (`Charge` - Scene 3): Lấy đà `-8°` (ngả sau) -> `+6°` (húc tới) -> `-3° -> +1° -> 0°`.<br>• Hai sừng (`HORN_L/R`): Cụm vào `-40° -> +6° -> 0°` (lệch pha 2 frames = `0.08s`).<br>• Card 3D (`05_Scene`): `Y Rotation +35° -> 0°`, `X Rotation +8° -> 0°`. | • Chỉ định rõ tâm xoay (Anchor) + chiều xoay (`counter-clockwise` = `-°`, `clockwise` = `+°`) + biên độ giảm chấn (damped oscillation). | Xoay luôn đi kèm **Overlap / Follow-through**: Sừng trễ hơn đầu `0.08s` (2–3 frames); đuôi trỏ chuột hoặc icon trong pill trễ hơn khung pill `0.05s` (1–2 frames). |
| **5. Keyframe & Timing Grid** | • Khung chuẩn: `30 fps` (`1 frame = 0.0333s`) hoặc `60 fps`.<br>• Nhịp nhạc: `120 BPM` = `0.50s / beat` (`15 frames @ 30fps`).<br>• Mọi điểm nổ (Pop-in, Cut, Click) phải khóa vào lưới `0.25s` (`7–8 frames`). | • Trong Omni Flash (giới hạn 3s–10s mỗi clip): Chia Kịch bản 36s thành **6 Clip chuẩn (5s – 6s – 5s – 6s – 8s – 6s)**, khóa `First Frame` + `Last Frame`. | **Tỷ lệ vàng**: `70% thời lượng` cho chuyển động (Action + Settle), tối đa `30% thời lượng` giữ tĩnh cuối clip (trong lúc giữ tĩnh, `CAM` vẫn trôi chậm `2–4%` để khung hình luôn "sống"). |

---

## PHẦN 2: BẢNG THÔNG SỐ KỸ THUẬT AFTER EFFECTS (`Final_4k 3840x2160 @ 30fps`) CHO KỊCH BẢN SỐ 1

Dưới đây là bảng thông số Keyframe chuẩn xác để dựng hoặc hậu kỳ 5 cảnh của **Kịch bản số 1 (Ads #1 - 36s)** trên After Effects (tương thích 100% cấu trúc `template 5.aep`):

| Scene & Timecode | Tên Pre-comp & Layer (Chuẩn `template 5.aep`) | Anchor Point `[X, Y]` (4K px & %) | Position `[X, Y, (Z)]` | Scale `[X%, Y%]` | Rotation `R / Rx,Ry,Rz` | Easing (Speed Graph) & Expression |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SCENE 1**<br>`00:00 – 00:05`<br>*(Hook: Chủ shop quá tải & Đồng hồ quay)* | `01_Scene` > `CAM_Null` | `[1920, 1080]` (`50%, 50%`) | `[1920, 1080] -> [1980, 1040]` | `100% -> 106%` (`f0 -> f150`) | `0°` | Linear Push-in liên tục hướng về laptop & đồng hồ |
| | `01_Scene_Clock_Hands` | Tâm trục đồng hồ `[2880, 520]` (`75%, 24%`) | `[2880, 520]` | `[100%, 100%]` | Kim phút: `0° -> +1080°`<br>Kim giờ: `0° -> +90°` | `In 40% / Out 85%` (Tăng tốc vù vù tạo cảm giác trôi giờ) |
| | `01_Scene_ShopOwner_Head` | Đáy cổ `[1820, 1380]` (`47%, 64%`) | `[1820, 1380]` | `[100%, 100%]` | `0° -> -5° -> +4° -> -3° -> 0°` | Nghiêng đầu thở dài + Rung nhẹ `wiggle(6, 8)` khi tin nhắn nổ dồn dập |
| | `01_Scene_MsgBubble_01..08` | Góc đuôi bong bóng (`[0%, 100%]` hoặc `[100%, 100%]`) | Xếp chồng quanh laptop (Stagger `6 frames` = `0.20s`/tin) | `0% -> 108% -> 100%` (`10 frames` mỗi bubble) | `-6° -> +2° -> 0°` | **Spring Pop**: `Out 15.2% / In 100%` + Overshoot `108%` tại `f7` |
| | `01_Scene_Text01` *(TOS Hook)* | Đáy dòng chữ `[1920, 320]` (`50%, 15%`) | `[1920, 440] -> [1920, 320]` (Qua `Alpha Matte`) | `[100%, 100%]` | `0°` | **Rule R1**: `Out 75.2% / In 75.1%` trong `16 frames` (`0.53s`) |
| **SCENE 2**<br>`00:05 – 00:11`<br>*(Xoáy sâu nỗi đau: Hàng chục chat bỏ dở & Lên đơn tay)* | `02_Scene` > `ChatList_Scroll_Null` | `[960, 1080]` (`25%, 50%`) | `Y: 1080 -> 870 -> 660 -> 450` (Nhảy bậc mỗi `0.50s`) | `[100%, 100%]` | `0°` | Step-scroll theo nhịp beat: `Out 20% / In 90%` (`12 frames` trượt, `3 frames` nghỉ) |
| | `02_Scene_Badge_99Plus` | Tâm huy hiệu đỏ `[1420, 310]` (`37%, 14%`) | `[1420, 310]` | `0% -> 115% -> 95% -> 100%` (Nhịp lặp `100% -> 108% -> 100%`) | `0° -> -8° -> +8° -> 0°` | `Slider Control` đếm số `12 -> 99+` (`Math.round(slider)`) |
| | `02_Scene_POS_ManualCard` | Đỉnh-trái `[2100, 360]` (`55%, 17%`) | `[2100, 360]` | Mask Wipe `0% -> 100%` (`18 frames`) | `0°` | **Rule R10**: `Out 15.2% / In 100%` + 3 bullet nỗi đau trượt vào cách nhau `0.35s` |
| | `02_Scene_DarkVignette` | `[1920, 1080]` | `[1920, 1080]` | `[100%, 100%]` | `0°` | `Opacity: 0% -> 65%` (`f0 -> f180`) tạo áp lực trực đêm quá tải |
| **SCENE 3**<br>`00:11 – 00:22`<br>*(Giải pháp: Mascot Bò OPA + Split-Screen Chat & 5 Pills)* | `05_Scene` > `Mascot_Bull_OPA` | Đáy giữa đầu bò `[50%, 100%]` | `[960, 540]` (`25%, 25%`) | `0% -> 112% -> 95% -> 100%` (`22 frames`) | `-8°` (lấy đà `f0–f6`) -> `+6°` (húc `f12`) -> `-3° -> 0°` | **Cú húc thương hiệu (Bull Charge)** quét sạch màn tối bằng `Whoosh Glow Sweep` |
| | `05_Scene_ChatCard_Left` *(Giống hệt ảnh `00:19:03`)* | Tâm thẻ trái `[1020, 1180]` (`26.5%, 54.6%`) | `[1020, 1180, +300] -> [1020, 1180, 0]` | `88% -> 100%` | `Y Rot: +28° -> 0°`<br>`X Rot: +6° -> 0°` (`24 frames`) | Card 3D xoay phẳng về phía camera + viền `EdgeGlow` xanh `#1E40FF` chạy quanh mép (`Trim Paths`) |
| | `05_Scene_Button02` *(5 Feature Pills cột phải)* | Cạnh trái mỗi Pill `[2040, Y_i]` (`53%, Y_i%`) | `X: 2240 -> 2040`<br>`Y_1..5`: `620, 820, 1020, 1220, 1420` | `0% -> 108% -> 100%` (Stagger `15 frames` = `0.50s` đúng nhịp 120 BPM) | `0°` | Kích thước Pill tự co giãn theo chữ bằng `sourceRectAtTime()` + Khung sáng `Selection_Frame` (H15) trượt qua từng Pill |
| **SCENE 4**<br>`00:22 – 00:30`<br>*(Giải phóng sức lao động: Chủ shop thảnh thơi & 3 Tích xanh)* | `04_Relief_ShopOwner` | Đáy lưng ghế `[1920, 1520]` (`50%, 70%`) | `[1920, 1520]` | `95% -> 100%` | Ngả lưng thư giãn `0° -> -4°`, hai tay mở rộng `+15°` | Chuyển động thở êm (`Math.sin(time*2)*1.5`) |
| | `04_Relief_StrikeCard_01..03` | Tâm từng thẻ `[920, 580]`, `[2920, 580]`, `[1920, 360]` | Giữ nguyên theo vòng cung quanh chủ shop | `0% -> 106% -> 100%` (Stagger `0.60s`) | `0°` | Đường gạch bỏ đỏ (`Trim Paths End: 0% -> 100%` trong `10 frames`) -> Thay bằng Icon Check xanh ✅ (`Scale 0% -> 115% -> 100%`) |
| **SCENE 5**<br>`00:30 – 00:36`<br>*(Outro & CTA: Logo Lockup + Click `chat.overpowers.agency`)* | `13_Scene` > `OPA_Mascot_Master` | Đáy giữa `U_HEAD` `[50%, 100%]` | `[1920, 920]` (`50%, 42.6%`) -> Trượt sang `[1320, 920]` (`34.4%, 42.6%`) tại `01.50s` | `0% -> 112% -> 95% -> 100%` -> Thu về `72%` khi nhường chỗ cho chữ `OPA AGENT` | Sừng `HORN_L/R`: `-40° -> +6° -> 0°` quanh gốc sừng `[22.6%, 42.1%]` | Chuẩn tuyệt đối từ `KET-LUAN-VA-PROMPT-SUA.md` (Không thêm mắt/mũi, giữ đúng lỗ trắng hình chữ O ở `[50%, 64.7%]`) |
| | `13_Scene_CTA_Pill` | Tâm nút `[1920, 1560]` (`50%, 72.2%`) | `[1920, 1560]` | `Rectangle Size: [140, 140] -> [1480, 140]` (`16 frames`)<br>Khi Click (`03.50s`): `Scale 100% -> 94% -> 102% -> 100%` (`8 frames`) | `0°` | Nở từ vòng tròn thành nút Pill (`Out 15.2% / In 100%`) + Sóng `Click Ripple` (`Scale 80% -> 150%`, `Opacity 60% -> 0%`) |
| | `13_Scene_MouseCursor` | Đỉnh mũi tên `[0, 0]` | Đường cong Bézier từ `[2950, 1950]` -> `[2180, 1580]` (`02.50s -> 03.45s`) | `100% -> 88% -> 100%` tại `03.50s` | `-15° -> 0°` | Trỏ chuột lướt đường cong tự nhiên, nhấn xuống đúng nhịp âm thanh `Click` |

---

## PHẦN 3: QUY TẮC SỐNG CÒN KHI VIẾT PROMPT CHO GOOGLE OMNI FLASH (TỪ THỰC NGHIỆM `MOTION CLAUDE`)

Qua quá trình kiểm thử thực tế trong `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/OPA-Motion-graphic-mascot/flow-omni`, có **4 quy tắc bắt buộc** quyết định 100% chất lượng đầu ra trên Google Omni Flash:

1. **Chốt chặn "Invisible Data Guard" (Chống lỗi AI vẽ thông số lên màn hình)**:
   - Trong lần chạy P01 (`KET-LUAN-VA-PROMPT-SUA.md`), khi đưa các tên biến (`HORN_L`, `22.6%`, `C#`, mũi tên kích thước) vào prompt mà không rào chắn, **Omni Flash đã vẽ luôn chữ `HORN_L`, `22.6%` và đường gióng kỹ thuật lên video!**
   - **Giải pháp bắt buộc**: Mọi prompt Motion Control phải có câu khóa ở đầu:
     > `"Everything below is invisible animation and camera control data. Never draw any of it on screen: no labels, layer names, numbers, percentages, coordinates, arrows, guides, dimension lines, bounding boxes, or any text."`
2. **Chiến lược Hybrid "Clean Motion Plates + AE Typography"**:
   - Các mô hình tạo video (Omni Flash / Veo / Kling) xử lý **Vật lý chuyển động, Mascot 2D/2.5D, Khung thẻ UI 3D, Ánh sáng Glow, Chuyển cảnh Whoosh** cực đẹp, nhưng **luôn làm nhòe hoặc sai dấu tiếng Việt cỡ nhỏ**.
   - Vì vậy, với mỗi cảnh bên dưới, bộ tài liệu cung cấp **2 phiên bản Prompt**:
     - **Bản A — `Clean Plate Mode` (Khuyên dùng cho quy trình chuyên nghiệp với AE)**: Yêu cầu Omni Flash dựng toàn bộ nhân vật, khung thẻ UI, bong bóng chat, thanh skeleton, hiệu ứng sáng và chuyển động camera (không vẽ chữ tiếng Việt), sau đó thả vào `template 5.aep` để gắn lớp chữ tiếng Việt sắc nét 4K.
     - **Bản B — `Full Visual + Motion Control Mode`**: Dành cho trường hợp muốn xem bản nháp đầy đủ bố cục ngay trên Google Omni Flash.
3. **Khóa `First Frame` + `Last Frame` (Omni 1.1 Flash) hoặc `Style Reference`**:
   - Google Omni Flash chỉ giữ chuẩn hình học thương hiệu (đặc biệt là Mascot Bò OPA và giao diện thẻ chat `05_Scene`) khi đính kèm **Ảnh tham chiếu (Reference Image)** hoặc cặp **First Frame + Last Frame**.
4. **Prompt bằng Tiếng Anh chuyên ngành Motion Graphics**:
   - Toàn bộ thuật ngữ điều khiển (`anchor point`, `overshoot spring`, `staggered pop-in`, `3D Y-rotation swing`, `track-matte slide`, `damped oscillation`) phải viết bằng **tiếng Anh** để khớp 100% với không gian huấn luyện của Google Omni Flash.

---

## PHẦN 4: PROMPT KHỞI TẠO HỆ THỐNG (SYSTEM / SESSION INIT PROMPT CHO GOOGLE OMNI FLASH)

Copy đoạn prompt dưới đây gửi vào đầu phiên làm việc với **Google Omni Flash Agent** để thiết lập tư duy **After Effects Motion Control Director**:

```markdown
You are a Senior After Effects Motion Graphics Director and Google Omni Flash Motion-Control Specialist creating a 36-second flagship 2D/2.5D SaaS commercial ("VIDEO 01 - Ads #1: OPA Agent for Pancake POS") inspired by the "AI Chat Agent Promo" After Effects template (`Final_4k 3840x2160 @ 30fps`) and SMIT - Ads Check Pro pacing.

STRICT VISUAL & MOTION CONTROL RULES FOR ALL SHOTS:
1. INVISIBLE DATA GUARD: All technical parameters (timestamps, percentages, degrees, anchor points, easing curves, layer names) are INVISIBLE animation instructions. NEVER render any labels, coordinates, numbers, percentages, dimension lines, arrows, or technical HUD overlays onto the video frames.
2. FORMAT & RHYTHM LOCK:
   - Resolution & Aspect Ratio: 16:9 widescreen (3840x2160 4K aesthetic), 30 fps (or 60 fps smooth interpolation).
   - Tempo Grid: 120 BPM (1 beat = 0.50s = 15 frames @ 30fps; half-beat = 0.25s). Every pop-in, scroll step, and camera cut locks to this 0.25s grid.
   - Zero Dead Frames: The master camera (`CAM_Null`) must maintain a continuous, subtle push-in (`Scale 96% -> 100%`) or gentle parallax drift throughout every shot so no frame is ever frozen.
3. AFTER EFFECTS TRANSFORM & EASING DISCIPLINE:
   - ANCHOR POINT LOCK: Every element scales and rotates strictly from its functional mechanical pivot:
     * Chat bubbles: pivot from the bottom-left (incoming) or bottom-right (outgoing) tail corner.
     * UI cards & modals: expand from their top-left corner or center with fast-out, long-settle easing (`cubic-bezier(0.15, 0, 0, 1)`, AE Out Influence 15.2% / In Influence 100%).
     * OPA Bull Mascot head: pivots from its bottom-center base (`[50%, 100%]`); left and right horns pivot from their respective horn roots (`[22.6%, 42.1%]` and `[77.4%, 42.1%]`) with a 0.08s overlap delay.
     * CTA & Feature Pills: expand horizontally from a circle into a rounded pill (`Rectangle Size [h, h] -> [w, h]`) so corner roundness never distorts.
   - SCALE & SPRING PHYSICS: Never use linear 2-keyframe scaling (`0% -> 100%`). Always use a 3- or 4-keyframe spring curve (`0% -> 108% -> 100%` for UI pills/bubbles; `0% -> 112% -> 95% -> 100%` for hero mascot/checkmarks).
   - 2.5D CARD PERSPECTIVE (Template `05_Scene` Style): Hero UI panels enter with a subtle 3D perspective swing (`Y-Rotation +28° -> 0°`, `X-Rotation +6° -> 0°`) accompanied by a traveling cobalt-blue edge glow (`#1E40FF` to `#2690FF`) and soft multi-layered drop shadows (`opacity 12%, blur 40px, Y-offset +18px`).
4. BRAND PALETTE & MASCOT IDENTITY LOCK:
   - Primary Brand Blue: `#1E40FF` (Electric Cobalt) | Deep Navy Background: `#0A142E` | Clean Daylight Surface: `#F4F7FF` to `#FFFFFF`.
   - Alert / Pain-Point Accent: `#FF3B30` (Coral Red) | Success / Relief Accent: `#10B981` (Emerald Green) & `#2690FF` (Cyan-Blue Glow).
   - OPA Bull Mascot: Minimalist flat geometric royal-blue bull head (`#1E40FF`) composed of a U-shaped head, two curved crescent horns on top, and a single solid white circular O-ring cutout in the lower center of the face. NO eyes, NO nostrils, NO mouth, NO ears, NO 3D shading on the mascot.
```

---

## PHẦN 5: BỘ PROMPT CHI TIẾT TỪNG CẢNH CHO KỊCH BẢN SỐ 1 TRÊN GOOGLE OMNI FLASH (6 CLIPS = 36 GIÂY)

> **Lưu ý vận hành trên Google Flow / Omni Flash**: Vì Scene 3 dài `11 giây` (`00:11 – 00:22`), vượt quá ngưỡng tối ưu 5s–8s của 1 clip đơn trên Omni Flash, chúng ta tách **Scene 3** thành **Clip 3A (5s — Cú húc chuyển cảnh & Khung Chat 3D `05_Scene` tự chốt đơn)** và **Clip 3B (6s — Split-Screen & 5 Feature Pills nảy theo nhịp 120 BPM)**. Tổng cộng **6 Clips = 36 giây** khớp 100% kịch bản gốc trên web.

---

### 🎬 CLIP 1 — SCENE 1 (`00:00 – 00:05` | Thời lượng: `5.0s`): HOOK — CHỦ SHOP QUÁ TẢI & ĐỒNG HỒ QUAY VÙ VÙ

* **Bối cảnh Kịch bản số 1**: Hoạt hình 2D/2.5D: Chủ shop ngồi quay lưng trước laptop, đồng hồ treo tường bên phải quay vù vù. Hàng loạt icon tin nhắn Messenger/Pancake nảy lên liên tục kèm tiếng *"Ting! Ting! Ting!"* dồn dập.
* **Text hậu kỳ trong AE (`01_Scene_Text01`)**:
  `BẠN MẤT BAO NHIÊU THỜI GIAN`  
  `để trả lời khách và lên đơn trên Pancake mỗi ngày?`

#### 🔹 Prompt 1A — Motion Control Chi Tiết (Chuẩn After Effects Keyframe + Invisible Guard)
```text
Everything below is invisible animation and camera control data. Never draw any of it on screen: no labels, layer names, numbers, percentages, coordinates, arrows, guides, dimension lines, or any text.

[INPUT & STYLE LOCK]
High-end 2D/2.5D vector motion graphics animation in 16:9 widescreen (4K 3840x2160 aesthetic, 30 fps). Clean modern SaaS commercial style matching SMIT Ads Check Pro and Envato AI Chat Promo.

[BACKGROUND & LIGHTING LOCK]
A cozy e-commerce shop office room seen from behind a young shop owner sitting at a desk in front of a glowing laptop at center-bottom `(50%, 68%)`. Warm indoor desk lamp gradually cools into stressed slate-blue twilight (`#162238`). On the upper-right wall at `(76%, 26%)` hangs a minimalist circular wall clock.

[LAYERS & MECHANICAL ANCHOR POINTS]
- `CAM_NULL` (Master Camera): Anchor at canvas center `(50%, 50%)`.
- `SHOP_OWNER`: Viewed from behind at `(50%, 68%)`, upper torso and head pivoting from the base of the neck `(50%, 62%)`.
- `WALL_CLOCK`: Circular dial at `(76%, 26%)`; minute hand and hour hand both pivot strictly from the center pin of the clock face `(76%, 26%)`.
- `MSG_BUBBLES_01_TO_08`: Eight glossy blue and orange chat notification bubbles with circular avatar dots and skeleton message bars (no readable words), each pivoting strictly from its bottom-left or bottom-right speech-tail corner.

[KEYFRAMES & TRANSFORM TIMELINE (0.00s to 5.00s @ 120 BPM)]
- `[0.00s -> 5.00s]` `CAM_NULL`: Continuous slow push-in from Scale `96%` to `104%`, drifting slightly toward the laptop and clock so the frame feels alive and increasingly claustrophobic.
- `[0.00s -> 4.50s]` `WALL_CLOCK` Rotation: The minute hand spins clockwise rapidly through three full revolutions (`Rotation 0 deg -> +1080 deg`, accelerating with ease-in `40%` and ease-out `85%`), while the hour hand advances `0 deg -> +90 deg`, visually showing hours flying by.
- `[0.25s -> 4.25s]` `MSG_BUBBLES_01_TO_08` Staggered Pop-In: Every `0.25s` (half-beat), a new chat notification bubble pops out around the laptop screen in a rising arc from `(32%, 58%)` to `(68%, 34%)`. Each bubble scales from its tail-corner anchor using a crisp 3-keyframe spring (`Scale 0% -> 108% -> 100%` over `0.30s`, `Rotation -6 deg -> +2 deg -> 0 deg`).
- `[1.00s -> 4.50s]` `SHOP_OWNER` Reaction: As the bubbles pile up around the laptop, the shop owner's shoulders slump and their head tilts from `0 deg -> -5 deg -> +4 deg` with a subtle stressed tremor, hands frantically hovering over the keyboard.
- `[0.00s -> 5.00s]` Top 22% of the frame `(y: 0% to 22%)` is kept clean and uncluttered dark-slate space reserved for the After Effects headline overlay.

[VFX & SFX CUES]
Subtle radial screen glow from the laptop monitor reflecting on the shop owner's silhouette; soft motion blur on the spinning clock hands and popping bubbles. Audio cues: fast rhythmic clock ticking accelerating under rapid-fire "Ting! Ting! Ting!" message chime pops.
```

#### 🔹 Prompt 1B — Bản Ngôn Ngữ Tự Nhiên Thuần Khiết (An toàn 100% không lo AI vẽ thông số)
```text
A crisp 2D/2.5D vector motion-graphics animation in 16:9 widescreen, styled like a modern SaaS tech commercial. We see a young online shop owner from behind, sitting at a desk in front of a glowing laptop in the lower center of the frame, while the top fifth of the composition stays clean dark navy-slate negative space for a title header. On the upper-right wall hangs a clean minimalist round clock whose hands spin rapidly clockwise, showing hours flying past in seconds. Starting immediately and building to a frantic rhythm, glossy blue and orange chat notification bubbles with tiny bell and message icons pop out one after another around the laptop screen, each springing cleanly from its pointed tail corner with a lively bounce and a soft glow. As dozens of unread chat bubbles stack up around the monitor, the room lighting dims into a stressed late-night blue glow and the shop owner's shoulders slump with exhaustion while the camera pushes slowly inward. No text, no letters, and no numbers appear anywhere on screen.
```

---

### 🎬 CLIP 2 — SCENE 2 (`00:05 – 00:11` | Thời lượng: `6.0s`): XOÁY SÂU NỖI ĐAU — MÀN HÌNH QUÁ TẢI HỘI THOẠI & NHẬP ĐƠN POS THỦ CÔNG

* **Bối cảnh Kịch bản số 1**: Góc nhìn chuyển sang màn hình máy tính mở hàng chục hội thoại Pancake đang nhấp nháy chờ rep (*"Còn size M không shop?"*, *"Giá bao nhiêu?"*, *"Check bill giúp em"*). Không gian xung quanh tối dần (trực page đêm muộn, quá tải).
* **Text hậu kỳ trong AE (`02_Scene_Text01..03`)**:
  `• Hàng chục cuộc chat bỏ dở`  
  `• Trả lời lặp đi lặp lại`  
  `• Lên đơn POS thủ công`

#### 🔹 Prompt 2A — Motion Control Chi Tiết (Chuẩn After Effects Keyframe + Invisible Guard)
```text
Everything below is invisible animation and camera control data. Never draw any of it on screen: no labels, layer names, numbers, percentages, coordinates, arrows, guides, dimension lines, or any text.

[INPUT & STYLE LOCK]
2.5D UI motion graphics in 16:9 widescreen (4K 3840x2160 aesthetic, 30 fps), matching the dark-mode UI card aesthetic of Envato AI Chat Agent Promo (`04_Scene` & `05_Scene`).

[BACKGROUND & LIGHTING LOCK]
Deep midnight navy workspace background (`#081024`) with a darkening vignette around the edges to evoke late-night burnout. A soft coral-red warning ambient glow (`#FF3B30` at 15% opacity) pulses gently behind the overloaded inbox panel.

[LAYERS & MECHANICAL ANCHOR POINTS]
- `CAM_NULL`: Anchor at `(50%, 50%)`, slight 2.5D perspective tilt.
- `INBOX_PANEL_LEFT`: A sleek multi-channel chat inbox window occupying the left half of the screen `(28%, 54%)`, tilted slightly in 3D space (`Y-Rotation +12 deg`). Inside is a vertical stack of incoming customer chat rows.
- `ALERT_BADGE_RED`: A glossy coral-red notification counter pill anchored at the top-right corner of the inbox window `(44%, 20%)`, pivoting from its center.
- `MANUAL_POS_FORM_RIGHT`: A manual order-entry spreadsheet/POS form card on the right `(72%, 62%)`, anchored at its top-left corner `(54%, 38%)`, while the upper-right area `(54%, 15% to 35%)` holds three clean horizontal glass pill slots for bullet points.

[KEYFRAMES & TRANSFORM TIMELINE (0.00s to 6.00s @ 120 BPM)]
- `[0.00s -> 0.50s]` `INBOX_PANEL_LEFT` Entrance: Swings in from `Scale 88% -> 100%` and `Y-Rotation +24 deg -> +12 deg` with fast-out, long-settle easing (`Out Influence 15.2%, In Influence 100%`).
- `[0.50s -> 4.50s]` Vertical Step-Scroll on Beat: Every `0.50s` (on each 120 BPM beat), the stack of chat rows inside `INBOX_PANEL_LEFT` shifts downward by one row height as a new urgent incoming message row pops in at the top from its left avatar anchor (`Scale 0% -> 108% -> 100%`), flashing an unread red dot and skeleton question bars.
- `[0.75s -> 5.00s]` `ALERT_BADGE_RED`: Pops in (`Scale 0% -> 115% -> 95% -> 100%`) and pulses rhythmically (`Scale 100% -> 108% -> 100%` + subtle shake `Rotation -6 deg -> +6 deg -> 0 deg`) as unread alerts accumulate.
- `[1.25s -> 3.00s]` `MANUAL_POS_FORM_RIGHT`: Wipes open diagonally from its top-left anchor `(54%, 38%)` (`Mask Scale 0% -> 100%`, `cubic-bezier(0.15, 0, 0, 1)`), showing a blinking cursor tediously copying and pasting skeleton bars from the chat window into manual phone and address input boxes.
- `[1.50s, 2.25s, 3.00s]` Three dark-glass bullet pill containers slide in horizontally at the upper right `(72%, 20%)`, `(72%, 28%)`, and `(72%, 36%)` with a `0.75s` stagger (`Position X +8% -> 0%`, `Opacity 0% -> 100%`), ready for After Effects Vietnamese bullet text.
- `[4.00s -> 6.00s]` `CAM_NULL`: Pushes in from `Scale 100% -> 106%` as the surrounding ambient light dims further, emphasizing overload just before the hero transition.

[VFX & SFX CUES]
Crisp glassmorphism borders, subtle coral-red edge pulse on unread rows, shallow depth-of-field blur on background grid.
```

#### 🔹 Prompt 2B — Bản Ngôn Ngữ Tự Nhiên Thuần Khiết
```text
A sleek 2.5D dark-mode UI motion-graphics scene in 16:9 widescreen. On the left side of the frame, a slightly angled multi-channel chat inbox window is flooded with incoming customer message rows that step-scroll downward on every beat as new unread rows pop in at the top with glowing red alert dots and pulsing notification badges. On the lower-right side, a manual order-entry form wipes open from its top-left corner, showing a blinking cursor struggling to copy and paste bars of customer data from the chat into form fields one by one. Above the form on the upper right, three sleek translucent glass pill banners slide smoothly into place one after another, left clean and blank for text overlay. As the inbox continues flashing with unanswered messages, the surrounding midnight-blue workspace darkens around the edges while the camera pushes slowly inward. Render all UI cards with clean geometric bars and icons only—no letters, words, or numbers on screen.
```

---

### 🎬 CLIP 3A — SCENE 3 PHẦN ĐẦU (`00:11 – 00:16` | Thời lượng: `5.0s`): CHUYỂN CẢNH BỪNG SÁNG, MASCOT BÒ OPA XUẤT HIỆN & KHUNG CHAT 3D (`05_Scene`) TỰ CHỐT ĐƠN POS

* **Bối cảnh Kịch bản số 1 + Khớp 100% ảnh chụp `template 5.aep` (`00:19:03`)**:
  - Chuyển cảnh bừng sáng (`Whoosh Transition`): Mascot Bò OPA xuất hiện, giao diện OPA Agent bung ra mượt mà bên trái màn hình.
  - Khung chat OPA tự động tư vấn size M giá 159.000đ và tự đẩy đơn sang bảng Pancake POS (dựa trên đúng cơ chế `05_Scene` trong ảnh chụp: thẻ trắng 3D có viền xanh `EdgeGlow` xoay về phía camera).

#### 🔹 Prompt 3A — Motion Control Chi Tiết (Chuẩn `05_Scene` trong `template 5.aep` + Mascot Charge)
```text
Everything below is invisible animation and camera control data. Never draw any of it on screen: no labels, layer names, numbers, percentages, coordinates, arrows, guides, dimension lines, or any text.

[INPUT & STYLE LOCK]
Use the attached OPA Bull Mascot reference image (`T01`) and `05_Scene` UI layout (`T03`). 2.5D SaaS UI & Mascot motion graphics in 16:9 widescreen (4K 3840x2160, 30 fps).

[BACKGROUND & TRANSITION LOCK]
At `[0.00s -> 0.50s]`, a brilliant royal-blue and cyan light-sweep wave (`#1E40FF` to `#2690FF`) wipes across the dark screen from left to right, transforming the canvas into a vibrant, high-tech cobalt-and-daylight blue studio environment (`#0D1B3E` with a bright radial glow `#1E40FF` on the left).

[LAYERS & MECHANICAL ANCHOR POINTS]
- `MASCOT_OPA_BULL`: Minimalist flat royal-blue geometric bull head (`#1E40FF`) with two curved crescent horns and a single solid white circular O-ring cutout in the lower center of the face (strictly no eyes, no nostrils, no mouth). Anchored at its bottom-center base `(50%, 100%)`, positioned at the top-left of the chat panel `(16%, 22%)`.
- `CHAT_CARD_05_LEFT`: A crisp white rounded UI chat card (`#FFFFFF`, corner radius `28px`) with a glowing cobalt-blue outer rim (`EdgeGlow #2690FF`), occupying the left column `(28%, 56%)`, pivoting from its center in 3D space.
- `BUBBLE_CUSTOMER`: Incoming light-gray chat bubble at upper-left inside the card, anchored at its bottom-left tail corner.
- `BUBBLE_OPA_REPLY`: Outgoing royal-blue (`#1E40FF`) AI reply bubble on the right side of the card, anchored at its bottom-right tail corner, containing a mini product thumbnail and a green POS order-confirmed badge.

[KEYFRAMES & TRANSFORM TIMELINE (0.00s to 5.00s @ 120 BPM)]
- `[0.00s -> 0.75s]` `MASCOT_OPA_BULL` Hero Charge & Pop: Springs up from its bottom-center anchor (`Scale 0% -> 112% -> 95% -> 100%`). It performs a signature energetic bull-charge tilt: leans back `-8 deg` in anticipation (`0.15s`), lunges forward `+6 deg` (`0.35s`), and settles `0 deg` (`0.75s`), while both crescent horns swing outward from their roots with a `0.08s` overlap (`-35 deg -> +5 deg -> 0 deg`).
- `[0.40s -> 1.40s]` `CHAT_CARD_05_LEFT` 3D Swing-In (exact `template 5.aep` `05_Scene` motion): Enters on the left half of the screen, rotating smoothly in 3D from an angled perspective (`Y-Rotation +32 deg -> +4 deg`, `X-Rotation +6 deg -> 0 deg`, `Scale 86% -> 100%`, `cubic-bezier(0.15, 0, 0, 1)`) as a bright blue streak traces around its border (`Trim Paths 0% -> 100%`).
- `[1.50s -> 2.00s]` `BUBBLE_CUSTOMER`: Pops out from its bottom-left tail corner (`Scale 0% -> 108% -> 100%`).
- `[2.10s -> 2.60s]` Instant AI Typing Indicator: A tiny blue pill appears at the bottom-right with three white dots bouncing in a sine-wave sequence (`phase offset 0.08s`).
- `[2.60s -> 3.40s]` `BUBBLE_OPA_REPLY`: Morphs from the typing pill into a full royal-blue reply bubble from its bottom-right anchor (`Scale 0% -> 108% -> 100%`).
- `[3.50s -> 4.75s]` Automated POS Order Sync Card: Immediately below the AI reply, a sleek emerald-green & blue POS order confirmation card slides down (`Mask Wipe Out 15.2% / In 100%`) and stamps a glowing green checkmark (`Scale 0% -> 115% -> 100%`), while the right half of the screen `(x: 52% to 94%)` remains clean open studio space ready for the 5 Feature Pills in Shot 3B.

[VFX & SFX CUES]
Energetic "Whoosh!" light sweep at `0.00s`, crisp UI pop chimes on each bubble, and a bright confirmation chime at `3.60s`.
```

---

### 🎬 CLIP 3B — SCENE 3 PHẦN SAU (`00:16 – 00:22` | Thời lượng: `6.0s`): BỐ CỤC SPLIT-SCREEN & 5 PILL TÍNH NĂNG NẢY RA THEO NHỊP NHẠC (`05_Scene_Button02` + `H15`)

* **Bối cảnh Kịch bản số 1**:
  - Bên trái: Khung chat OPA + Mascot Bò OPA vẫn hoạt động mượt mà, tự động đẩy đơn sang bảng Pancake POS.
  - Bên phải: Tiêu đề lớn phía trên + **5 Pill tính năng (Icon + Text)** lần lượt nảy ra (`Pop-in`) theo nhịp nhạc 120 BPM, kèm khung sáng chọn chạy dọc (`H15 Option Pill Selector` từ `o ping.mp4` cảnh `09_Scene`).
* **Text hậu kỳ trong AE (`05_Scene_Text01` & `05_Scene_Button01..05`)**:
  - Header: `Chỉ 1 kết nối — OPA tự động hóa toàn bộ quy trình bán hàng trên Pancake:`
  - Pill 1: `💬 Tự trả lời đúng tồn kho POS`
  - Pill 2: `📦 Tự chốt đơn vào Pancake POS`
  - Pill 3: `🧾 Xác minh chuyển khoản bằng ảnh`
  - Pill 4: `⏰ Nhắc khách bỏ giỏ trong 24h`
  - Pill 5: `🤝 Nhân viên tiếp quản bất cứ lúc nào`
  - Footer: `Và nhiều hơn thế nữa!`

#### 🔹 Prompt 3B — Motion Control Chi Tiết (Split-Screen + 5 Staggered Feature Pills trên lưới 0.50s)
```text
Everything below is invisible animation and camera control data. Never draw any of it on screen: no labels, layer names, numbers, percentages, coordinates, arrows, guides, dimension lines, or any text.

[INPUT & CONTINUITY LOCK]
Use the last frame of Clip 3A as First Frame lock. 2.5D Split-Screen SaaS UI motion graphics in 16:9 widescreen (4K 3840x2160, 30 fps).

[BACKGROUND & SPLIT-SCREEN LAYOUT]
Left column `(x: 6% to 48%)` keeps the active white 3D-angled OPA Chat & Pancake POS sync card with the royal-blue OPA Bull Mascot perched at its top-left corner. Right column `(x: 52% to 94%)` is dedicated to a vertical stack of five sleek rounded feature-pill buttons (`05_Scene_Button` style) beneath a clean header zone at `(y: 12% to 22%)`.

[LAYERS & MECHANICAL ANCHOR POINTS]
- `LEFT_CHAT_POS_GROUP`: Gently floating in 2.5D space (`Y-Rotation +4 deg`), showing live order sync pulses flowing from the chat bubble into a compact POS order table at the bottom of the card.
- `FEATURE_PILLS_01_TO_05`: Five horizontal white-and-glass rounded pill cards stacked vertically in the right column at `y = 28%, 40%, 52%, 64%, 76%`. Each pill is anchored at its left circular icon badge `(x = 54%)` and features a distinct minimalist 2D vector icon on the left:
  1. Pill 1 (`y=28%`): Blue chat bubble + inventory box icon.
  2. Pill 2 (`y=40%`): Package box + lightning POS arrow icon.
  3. Pill 3 (`y=52%`): Receipt bill + green verification shield icon.
  4. Pill 4 (`y=64%`): Clock + shopping cart bell icon.
  5. Pill 5 (`y=76%`): Handshake / human headset takeover icon.
- `GLOW_SELECTOR_FRAME`: A luminous cobalt-cyan border highlight (`#2690FF`) that glides vertically from Pill 1 down to Pill 5 (`H15` selector mechanic).

[KEYFRAMES & TRANSFORM TIMELINE (0.00s to 6.00s @ 120 BPM)]
- `[0.00s -> 6.00s]` `CAM_NULL`: Smooth continuous push-in `Scale 100% -> 104%`.
- Staggered 5-Pill Pop-In on Exact 120 BPM Beats (`0.50s` interval):
  * `[0.50s -> 0.90s]` `FEATURE_PILL_01`: Springs open from its left icon anchor (`Scale 0% -> 108% -> 100%`, `Position X +4% -> 0%`, `Out Influence 15.2% / In Influence 100%`); its icon pops `0.06s` later (`Scale 0% -> 115% -> 100%`).
  * `[1.00s -> 1.40s]` `FEATURE_PILL_02`: Same crisp spring pop-in at `y = 40%`.
  * `[1.50s -> 1.90s]` `FEATURE_PILL_03`: Same crisp spring pop-in at `y = 52%`.
  * `[2.00s -> 2.40s]` `FEATURE_PILL_04`: Same crisp spring pop-in at `y = 64%`.
  * `[2.50s -> 2.90s]` `FEATURE_PILL_05`: Same crisp spring pop-in at `y = 76%`.
- `[3.00s -> 5.20s]` `GLOW_SELECTOR_FRAME` Cascade: A bright electric-blue selection border sweeps smoothly down across all five pills (`Out Influence 75% / In Influence 75%`), lighting up each pill's icon with a subtle scale pulse (`100% -> 104% -> 100%`) while the left chat panel shows a matching green order-synced pulse.
- `[0.00s -> 6.00s]` Inside each pill to the right of the icon, leave clean uncluttered white pill surface (or ultra-subtle skeleton bars) so Vietnamese typography can be composited cleanly in After Effects.

[VFX & SFX CUES]
Five rhythmic, ascending melodic synth-marimba pop notes synced to `0.50s, 1.00s, 1.50s, 2.00s, 2.50s`.
```

---

### 🎬 CLIP 4 — SCENE 4 (`00:22 – 00:30` | Thời lượng: `8.0s`): GIẢI PHÓNG SỨC LAO ĐỘNG (RELIEF) — CHỦ SHOP THẢNH THƠI & GẠCH BỎ 3 NỖI ĐAU KÈM TÍCH XANH ✅

* **Bối cảnh Kịch bản số 1**: Quay lại nhân vật chủ shop 2D ngồi trước laptop nhưng giờ mỉm cười thảnh thơi, hai tay dang rộng thoải mái (hoặc đan sau gáy thư giãn). Xung quanh nhân vật lần lượt nảy lên 3 khung thoại gạch bỏ các thao tác cực nhọc, kèm dấu tích xanh ✅.
* **Text hậu kỳ trong AE (`04_Relief_Text01..03`)**:
  `✅ Không cần tạo App Facebook phức tạp`  
  `✅ Không cần gõ lại một câu hỏi hàng trăm lần`  
  `✅ Không cần copy-paste từng số điện thoại, địa chỉ vào POS`

#### 🔹 Prompt 4A — Motion Control Chi Tiết (Chuẩn After Effects Keyframe + Invisible Guard)
```text
Everything below is invisible animation and camera control data. Never draw any of it on screen: no labels, layer names, numbers, percentages, coordinates, arrows, guides, dimension lines, or any text.

[INPUT & STYLE LOCK]
2D/2.5D vector character & UI motion graphics in 16:9 widescreen (4K 3840x2160 aesthetic, 30 fps), matching the character style of Shot 1 but now in bright, airy daylight.

[BACKGROUND & LIGHTING LOCK]
Bright, sunlit modern shop studio (`#F4F7FF` to `#FFFFFF`) with warm morning sunlight streaming in and soft floating royal-blue ambient particles. The oppressive dark mood of Shot 1 is completely gone.

[LAYERS & MECHANICAL ANCHOR POINTS]
- `SHOP_OWNER_RELAXED`: Centered in the lower-middle frame `(50%, 66%)` behind the laptop, facing three-quarters toward camera with a calm, relieved smile. Upper body pivots from the lower spine `(50%, 74%)`; arms pivot from the shoulders.
- `LAPTOP_SCREEN`: Shows a tiny blue OPA Bull Mascot icon smoothly handling chats automatically on its own.
- `RELIEF_CARDS_01_TO_03`: Three wide rounded floating white UI banners arranged in a clean arc above and around the shop owner at `(26%, 36%)`, `(74%, 36%)`, and `(50%, 18%)`. Each card is anchored at its center and has a circular badge slot on its left edge.

[KEYFRAMES & TRANSFORM TIMELINE (0.00s to 8.00s @ 120 BPM)]
- `[0.00s -> 1.50s]` `SHOP_OWNER_RELAXED` Motion: Leans back comfortably into the chair (`Rotation 0 deg -> -4 deg`, `Out Influence 80%`) and stretches both arms wide open in a relaxed, carefree posture (`Shoulder Rotation 0 deg -> +18 deg`), followed by a gentle breathing loop (`Scale Y 100% <-> 101.5%`).
- `[1.25s -> 2.50s]` `RELIEF_CARD_01` (Left `(26%, 36%)`):
  * Pops in from its center (`Scale 0% -> 108% -> 100%` over `0.35s`) initially showing a faded gray gear/code icon with a red diagonal strike-through line drawing across it (`Trim Paths 0% -> 100%` in `0.25s`).
  * At `1.85s`, a vibrant emerald-green checkmark badge (`#10B981`) springs over the left badge slot (`Scale 0% -> 115% -> 95% -> 100%`) as the card border glows clean blue (`#1E40FF`).
- `[2.75s -> 4.00s]` `RELIEF_CARD_02` (Right `(74%, 36%)`):
  * Pops in (`Scale 0% -> 108% -> 100%`), crosses out a repetitive keyboard-typing icon (`Trim Paths 0% -> 100%`), and snaps into a glowing green checkmark badge (`Scale 0% -> 115% -> 95% -> 100%`) at `3.35s`.
- `[4.25s -> 5.50s]` `RELIEF_CARD_03` (Top-Center `(50%, 18%)`):
  * Pops in (`Scale 0% -> 108% -> 100%`), crosses out a manual copy-paste clipboard icon (`Trim Paths 0% -> 100%`), and snaps into a glowing green checkmark badge (`Scale 0% -> 115% -> 95% -> 100%`) at `4.85s`.
- `[5.50s -> 8.00s]` All three cards float gently in zero-gravity (`vertical sine drift +-6px`) while the camera performs a slow celebratory pull-back (`Scale 103% -> 98%`). Keep the interior right side of all three cards clean white space for the After Effects Vietnamese text lines.

[VFX & SFX CUES]
Three crisp "slash -> ding!" sound pairs synced to the strikethrough and green checkmark pops at `1.85s`, `3.35s`, and `4.85s`.
```

#### 🔹 Prompt 4B — Bản Ngôn Ngữ Tự Nhiên Thuần Khiết
```text
A bright, uplifting 2D/2.5D vector motion-graphics scene in 16:9 widescreen. In a sunlit, airy studio workspace, the young shop owner sits in front of the laptop smiling peacefully, leaning back and stretching both arms out wide in complete relief while the laptop screen quietly runs automated blue chat bubbles on its own. Around the shop owner in the upper half of the frame, three sleek floating white rounded banners pop in one by one in a balanced arc—first on the left, then on the right, and finally at top-center. On each banner, a small gray icon representing tedious manual work is swiftly crossed out by a red line and immediately replaced by a vibrant emerald-green checkmark badge that springs in with a joyful bounce. The interior of each banner stays clean white space reserved for post-production text, while the camera glides slowly back. No words, letters, or numbers appear on screen.
```

---

### 🎬 CLIP 5 — SCENE 5 (`00:30 – 00:36` | Thời lượng: `6.0s`): OUTRO & CTA — MASCOT BÒ OPA + LOGO LOCKUP & CLICK `chat.overpowers.agency`

* **Bối cảnh Kịch bản số 1 + Quy chuẩn Logo Animation từ `KET-LUAN-VA-PROMPT-SUA.md`**:
  - Chuyển cảnh nền trắng/xanh thương hiệu tinh gọn. Mascot Bò OPA + Logo OPA Agent hiện lớn ở chính giữa màn hình.
  - Bên dưới là nút CTA nổi bật kèm hiệu ứng trỏ chuột click vào.
* **Text hậu kỳ trong AE (`13_Scene_Text01..02`)**:
  `OPA Agent — AI bán hàng cho shop dùng Pancake`  
  `👉 Thử miễn phí ngay tại: chat.overpowers.agency`

#### 🔹 Prompt 5A — Motion Control Chi Tiết (Chuẩn Logo OPA `KET-LUAN-VA-PROMPT-SUA.md` + CTA Pill Click)
```text
Everything below is invisible animation and camera control data. Never draw any of it on screen: no labels, layer names, numbers, percentages, coordinates, arrows, guides, dimension lines, or any text.

[INPUT & BRAND LOCK]
Attach First Frame (`K00` clean white-blue studio canvas) and Reference Image (`T01` OPA Bull Mascot & Lockup). 16:9 widescreen (4K 3840x2160, 30 fps).
Strict Mascot Geometry Lock: Flat royal-blue (`#1E40FF`) U-shaped bull head, two curved crescent horns on top, and a single solid white circular O-ring cutout inside the lower center of the head. Never add eyes, pupils, nostrils, mouth, ears, or gradients to the bull head.

[BACKGROUND LOCK]
Minimalist pure white and soft daylight-blue studio background (`#F8FAFF` to `#FFFFFF`) with a subtle royal-blue ambient halo in the center.

[LAYERS & MECHANICAL ANCHOR POINTS]
- `OPA_BULL_MARK`: Positioned initially at `(50%, 40%)`. The U-shaped head scales and rotates strictly from its bottom-center point `(50%, 100% of the head)`. Left and right crescent horns pivot from their respective horn roots where they meet the head. The inner white circle expands from its center.
- `CTA_PILL_BUTTON`: Centered below at `(50%, 74%)`, anchored at its center `(50%, 74%)`, filled with vibrant royal-blue (`#1E40FF`) and a soft outer glow.
- `MOUSE_CURSOR`: A crisp white-and-navy vector pointer arrow starting from the bottom-right corner `(82%, 92%)`, pivoting from its arrow tip.

[KEYFRAMES & TRANSFORM TIMELINE (0.00s to 6.00s @ 120 BPM)]
- `[0.25s -> 1.00s]` `OPA_BULL_MARK` Signature Spring Reveal:
  * The royal-blue U-head pops up from its bottom-center point using the exact 4-keyframe spring (`Scale 0% -> 112% -> 95% -> 100%` over `0.60s`), accompanied by a damped tilt (`Rotation -8 deg -> +5 deg -> -2 deg -> 0 deg`).
  * Delayed by `0.10s`, the inner white circle pops open from its center (`Scale 0% -> 110% -> 100%`).
  * Delayed by `0.15s`, the left horn (`0.40s`) and right horn (`0.48s`, `0.08s` stagger) swing outward from their roots (`Rotation -40 deg -> +6 deg -> 0 deg`) and lock into the exact reference silhouette.
- `[1.25s -> 2.00s]` Horizontal Lockup Slide: The completed bull mark glides smoothly left from `x = 50%` to `x = 34%` while scaling uniformly to `72%` (`Out Influence 75% / In Influence 75%`), leaving clean horizontal space on the right `(x: 42% to 72%, y: 40%)` for the `OPA AGENT` wordmark and subtitle in After Effects.
- `[1.75s -> 2.40s]` `CTA_PILL_BUTTON` Morph Expand: Starts as a royal-blue circle at `(50%, 74%)` and stretches horizontally from its center into a wide rounded CTA pill button (`Rectangle Size [h, h] -> [w, h]`, `Out Influence 15.2% / In Influence 100%`), keeping semi-circular end caps perfectly round.
- `[2.50s -> 3.45s]` `MOUSE_CURSOR` Arc & Click: Glides along a smooth curved Bézier arc from `(82%, 92%)` to `(58%, 75%)` over the CTA pill (`Out Influence 80%`).
- `[3.50s -> 3.85s]` The Click Impact: Cursor tip presses down (`Scale 100% -> 88% -> 100%`) as the entire `CTA_PILL_BUTTON` compresses and rebounds (`Scale 100% -> 94% -> 103% -> 100%` in `0.25s`), emitting two concentric royal-blue ripple rings (`Scale 95% -> 135%`, `Opacity 60% -> 0%`).
- `[3.85s -> 6.00s]` Final Hold with Subtle Life: The logo lockup and glowing CTA button hold steady while `CAM_NULL` continues a gentle `100% -> 102%` drift to the end of the 6-second clip.

[VFX & SFX CUES]
Playful 3-note rising synth chime on the bull reveal (`0.25s–0.90s`), crisp mechanical mouse click at `3.50s`, and a warm resolving major chord logo tail (`3.50s–6.00s`).
```

#### 🔹 Prompt 5B — Bản Ngôn Ngữ Tự Nhiên Thuần Khiết (Kèm First Frame + Last Frame Lock)
```text
Create a 6-second 2D minimalist vector outro animation in 16:9 widescreen on a clean white-and-daylight-blue background, using the attached OPA Bull Mascot reference image. In the first second, the flat royal-blue U-shaped bull head springs up from its bottom-center point with a lively bounce and a slight playful tilt; a split-second later, the solid white circular ring opens inside the lower center of the head and both curved crescent horns swing smoothly outward from their roots to lock into the exact mascot silhouette, with no eyes, nostrils, or mouth. In the second second, the bull mark glides smoothly to the left of center to make room for a headline beside it, while below it a royal-blue circle stretches horizontally into a sleek rounded call-to-action pill button. A crisp vector mouse cursor glides in along a smooth curved path from the bottom right, lands on the blue pill button at 3.5 seconds, and clicks it—causing the button to press down and spring back with a glowing blue ripple ring before holding steady to the end. Do not draw any text, letters, or numbers on screen.
```

---

## PHẦN 6: BỘ PROMPT ĐIỀU KHIỂN HỘI THOẠI (FOLLOW-UP CONVERSATIONAL CONTROL TRÊN GOOGLE OMNI FLASH)

Khi làm việc với **Google Omni Flash**, nếu sau lần render đầu tiên bạn muốn chỉnh sửa **đúng 1 thông số After Effects** (ví dụ: chỉnh lại độ nảy `Scale`, đổi tâm xoay `Anchor Point`, chỉnh góc nghiêng 3D `Rotation`, hay xóa chữ lạ do AI tự vẽ), hãy áp dụng quy tắc **"1 Lượt = 1 Thay Đổi + Khóa Phần Còn Lại"** từ `KICH-BAN-OMNI-FLASH.md`:

### 1. Sửa lỗi AI tự ý vẽ chữ / số / nhãn kỹ thuật lên video
```text
Keep the exact same camera motion, layout, colors, and animation timing. Remove all text, letters, numbers, labels, and technical lines from the screen so every UI card, pill, and chat bubble contains only clean geometric shapes, icons, and solid skeleton bars.
```

### 2. Chỉnh lại độ nảy `Scale` (Overshoot Spring) theo chuẩn After Effects (`0% -> 108% -> 100%`)
```text
Keep everything else in the scene identical. Only refine the scale pop-in of the [chat bubbles / 5 feature pills / CTA button]: make each element spring crisply from 0% to a slight 108% overshoot and settle smoothly back to 100% over 0.30 seconds, instead of scaling linearly.
```

### 3. Sửa lỗi sai `Anchor Point` (Tâm neo bị trượt khi phóng to hoặc xoay)
```text
Keep the background, colors, and timing unchanged. Only fix the pivot point (anchor point) of the [chat bubbles / bull horns / UI card]:
- For incoming chat bubbles: make them scale and pop strictly from their bottom-left tail corner.
- For the OPA bull head: make it scale and tilt strictly from its bottom-center base so the bottom edge stays planted.
- For the two horns: make each horn rotate strictly around its root where it connects to the head.
```

### 4. Chỉnh góc xoay 3D (`Y-Rotation` / `X-Rotation`) của khung Chat `05_Scene` giống hệt ảnh chụp `template 5.aep`
```text
Keep the exact same chat bubble animation inside the card. Only adjust the 3D perspective of the main white chat panel on the left: start the card angled at roughly 30 degrees toward the center, then smoothly rotate it flatter toward the camera (around a 4-degree subtle angle) over 0.8 seconds with a glowing royal-blue border tracing its outer edge.
```

### 5. Đồng bộ lại nhịp `Stagger` (Độ trễ giữa 5 Pill tính năng ở Scene 3B theo đúng nhịp 120 BPM)
```text
Keep the split-screen layout and left chat panel unchanged. Only adjust the timing of the five feature pills on the right column: make them pop in sequentially from top to bottom at strict 0.50-second intervals (at 0.5s, 1.0s, 1.5s, 2.0s, and 2.5s), with each pill expanding from its left icon badge.
```

---

## PHẦN 7: QUY TRÌNH RÁP HẬU KỲ TRONG AFTER EFFECTS (`template 5.aep` / `Final_4k 3840x2160`)

Để sản phẩm cuối cùng đạt độ sắc nét **4K chuẩn thương mại như `o ping.mp4`** mà không bị lỗi dấu tiếng Việt của AI:

1. **Bước 1 — Xuất Clean Plates từ Google Omni Flash**:
   - Render 6 clips (`Clip 1`, `Clip 2`, `Clip 3A`, `Clip 3B`, `Clip 4`, `Clip 5`) bằng các **Prompt Bản A (Clean Plate Mode)** ở trên.
   - Upscale hoặc đưa trực tiếp vào comp `Final_4k (3840 x 2160)` (`30 fps`) trong `template 5.aep`.
2. **Bước 2 — Gắn lớp Text Tiếng Việt chuẩn `Inter` / `Plus Jakarta Sans` (`SemiBold` & `Bold`)**:
   - Áp dụng **Expression tự co giãn khung Pill (`sourceRectAtTime`)** từ `BAO-CAO-PHAN-TICH.md` lên các layer `05_Scene_Button02` để khung tự ôm khít độ dài chữ tiếng Việt:
     ```javascript
     // Gắn vào thuộc tính Size của Rectangle Path trong Shape Layer (Pill):
     const s = thisComp.layer("05_Scene_Text02");
     const r = s.sourceRectAtTime(time, false);
     const padX = 80; // Padding ngang (4K)
     const padY = 44; // Padding dọc (4K)
     [r.width + padX * 2, r.height + padY * 2];
     ```
   - Áp dụng **Expression đếm số tự động (`Slider Control`)** cho huy hiệu tin nhắn quá tải (Scene 2) và giá tiền/mã đơn `#PK8921` (Scene 3):
     ```javascript
     // Gắn vào Source Text của Badge_Counter:
     Math.round(effect("Slider Control")("Slider")) + "+"
     ```
3. **Bước 3 — Khóa Easing trong Graph Editor (Speed Graph)**:
   - Chọn toàn bộ keyframe `Position` của chữ tiêu đề (`TOS`): Mở `Keyframe Velocity` (`Ctrl + Shift + K`) -> Đặt **Outgoing Influence = `75.2%`**, **Incoming Influence = `75.1%`** (Rule R1).
   - Chọn toàn bộ keyframe `Scale` / `Mask Expansion` của khung thẻ UI: Đặt **Outgoing Influence = `15.2%`**, **Incoming Influence = `100%`** (Rule R10).
4. **Bước 4 — Đồng bộ Voice-Over (VO) & Sound Effects (SFX 48kHz)**:
   - Đặt marker tại đúng các mốc `00:00`, `00:05`, `00:11`, `00:16`, `00:22`, `00:30`, `00:36` và khớp tiếng *Ting! Ting!* (Scene 1), *Whoosh!* (Scene 3A `00:11`), *5 tiếng Pop Marimba* (Scene 3B `00:16.5 – 00:19.0`), *3 tiếng Ding!* (Scene 4) và *Mouse Click + Logo Chime* (Scene 5 `00:33.5`).

<!-- ===== /file: omni-flash-motion-director/references/PROMPT-OMNI-FLASH-KICH-BAN-01-AE-MOTION-CONTROL.md ===== -->

<!-- ===== file: omni-flash-motion-director/references/PROMPT-PACK-OMNI-FLASH.md ===== -->

Ngày tạo: 23/10/2026 · **Bản 2.2**: P01 dời nhịp sớm 0,3 s, 24/10 (bản 1: `.ban1.md`; bản 2: `.ban2.md`; bản 2.1: `.ban2-1.md`)
Dùng cùng `KICH-BAN-OMNI-FLASH.md` (KB1–KB9), `KICH-BAN-PROMO-CHATBOT-OPA.md` (C1–C6) và bản phân tích 3 mẫu Envato (mã hiệu ứng H01–H21).
Trạng thái: bộ prompt sẵn để dán vào Google Flow. Chưa chạy thử trên Omni Flash; số trong prompt chưa được đo trên clip thật.

# Bộ prompt Omni Flash có thông số motion graphic · bản 2

## 0. Bản 2 thêm gì

Mỗi prompt nay có đủ **mười khối**, theo đúng thứ tự:

| Khối | Giữ cái gì | Mới ở bản 2 |
|---|---|---|
| `INPUT` | Dùng ảnh nào, theo chế độ nào (khung hay tham chiếu) | ✅ |
| `FORMAT LOCK` | Tỉ lệ, khung hình, thời lượng, một cảnh liền | ✅ |
| `BACKGROUND LOCK` | Nền đúng một màu phẳng suốt clip | ✅ |
| `COLOR` | Màu nào cho vật nào, cấm chỉnh màu | ✅ |
| `UNITS` · `LAYERS & ANCHOR POINTS` · `KEYFRAMES` | Thông số chuyển động kiểu After Effects | như bản 1 |
| `VFX` | Hiệu ứng được dùng kèm thông số; mọi thứ khác bị cấm | ✅ |
| `TIMING RATIO` · `DIRECTOR NOTE` | Tỷ lệ nhịp và ý định | như bản 1 |
| `SFX` | Danh sách âm theo mốc giây, cao độ, mức to, hướng | ✅ thay dòng AUDIO |
| `LOGO LOCK` | Hình logo không đổi | tách từ BRAND LOCK |

Thêm ảnh tham chiếu mới **T04 bảng phong cách** (`tham-chieu/T04_bang-phong-cach.png`): bảng màu và mẫu giao diện phẳng, không chữ, dùng cho các prompt dựng nền giao diện (P12, P13, P15).

> **Omni hiểu số như "lực kéo", không như lệnh chính xác.** Khung đầu và khung cuối mới ghim đúng tuyệt đối. Cách làm: tạo 2–4 bản → đo (mục 10) → sửa bằng prompt sửa có số (mục 9).

**Bài học lần chạy đầu (P01, 23/10)** — đo ở `do/OPA_logo_animation_rules_20261023170017/`:

1. **Omni vẽ chữ của prompt lên hình**: tên lớp ("HORN_L"), con số ("22.6%"), tên nốt ("C#"), đường đo kích thước. Bản 2.1 thêm vào mọi prompt câu "Everything below is invisible animation data. Never draw any of it…", và P01 đổi tên lớp sang lời thường. Nếu vẫn hiện chữ, dùng kiểu B (chỉ ý định) của P01.
2. **Omni tự thêm chữ OPA** khi prompt nói "OPA logo". Mọi prompt không cần chữ nay ghi `the bull-head mark only — no "OPA" letters`.
3. **Thời lượng do cài đặt của Flow quyết định**, không do chữ "exactly N seconds". Đặt đúng thời lượng trong Flow trước khi tạo.
4. **Khung cuối chỉ khớp khi bật chế độ khung đầu/cuối.** Lần chạy đầu, khung cuối chỉ trùng 61 %.
5. **Màu logo lệch** (18, 110, 234) và âm vỡ (+0,4 dBFS): sửa ở hậu kỳ (mục 10), đừng trông vào prompt.

**Độ dài:** mỗi prompt bản 2.1 dài 1.700–3.050 ký tự (đã đo). Nếu Flow báo quá dài, bỏ dần theo thứ tự:
1. DIRECTOR NOTE;
2. TIMING RATIO;
3. UNITS (chỉ bỏ khi đã gửi prompt khởi tạo ở mục 7).

**Không bao giờ bỏ:** INPUT, FORMAT LOCK, BACKGROUND LOCK, COLOR, KEYFRAMES, SFX, LOGO LOCK.

## 1. Quy ước thông số

### 1.1 Đơn vị

| Thuộc tính | Đơn vị trong prompt | Ghi chú |
|---|---|---|
| Thời gian | giây, `0.50s` | Mốc trên lưới 0,25 s (nửa phách 120 BPM) |
| Position | % khung, `(x%, y%)`, gốc (0, 0) góc trên trái | Không dùng px |
| Scale | % so với cỡ ở khung cuối | 100 % = đúng cỡ khung cuối |
| Rotation | độ, **dương = chiều kim đồng hồ** | Như After Effects |
| Anchor Point | tên + `(x%, y%)` của khung bao dấu | Bảng 1.2 |
| Lệch nhịp | giây, `+0.08s` | ≈ 2 khung ở 24 fps |

### 1.2 Điểm neo trên dấu đầu bò

Đo từ `logo/OPA-V4-A-Core-blue-2000.png`, theo % khung bao của dấu.

| Tên | Vị trí | Dùng cho |
|---|---|---|
| `bottom-center` | (50 %, 100 %) | Bật nảy, thở, lấy đà, lao tới |
| `horn-root-L` / `horn-root-R` | (22,6 %, 42,1 %) / (77,4 %, 42,1 %) | Xoay sừng |
| `inner-opening-center` | (50 %, 64,7 %) | Chui qua lòng O |
| `top-gap-center` | (50 %, 40,2 %) | Hứng tin nhắn |
| `top-gap-edges` | (41,1 %, 40,2 %) và (58,9 %, 40,2 %) | Hạt phì ra |

### 1.3 Vị trí dấu trong khung neo

| Khung | 16:9 | 9:16 |
|---|---|---|
| `K01`, `K02` | tâm (50 %, 50 %), cao 46,2 % H | tâm (50 %, 45,6 %), rộng 57,3 % W |
| `K04` | dấu (29,3 %, 50 %) = 64,6 % cỡ K01; cụm rộng 59,7 % W | dấu (22,5 %, 45,6 %) = 42,8 % cỡ K01; cụm rộng 79,4 % W |
| `K06` | (28 %, 50 %) | (50 %, 63,1 %) |
| `K05` | bong bóng (50 %, 50 %), rộng 21,9 % W | (50 %, 45,5 %), rộng 44,4 % W |
| `K07` | dấu (50 %, 46,3 %) = 60 % cỡ K02; vòng nút 27,1 % W × 27,8 % H | dấu (50 %, 42,7 %) = 46 % cỡ K02; vòng 33,3 % W × 24,5 % H |
| Tâm lòng O | (50 %, 56,8 %) | (50 %, 49,9 %) |
| Hai mép khe trán | (47,5 %, 45,5 %), (52,5 %, 45,5 %) | — |

### 1.4 Bảng ease

| Tên | Nghĩa trong After Effects | Cảm giác |
|---|---|---|
| `[linear]` | Không ease | Đều tuyệt đối |
| `[ease-in-out]` | Easy Ease (F9) | Vào êm, ra êm |
| `[ease-out 80%]` | Ease out, influence 80 % | Nhanh rồi đáp rất nhẹ |
| `[pop]` | Spring damping 12 (`SPRING_POP`) | Vượt ~10–12 % một nhịp rồi đứng |
| `[ease-in 90%]` | Ease in 90 % | Chậm rồi nhanh dần rất gắt |
| `[sine]` | Easy Ease liên tục | Thở, đung đưa |
| `[decay]` | Mỗi nhịp lắc = −0,5 lần nhịp trước | Lắc tắt dần |

### 1.5 Tỷ lệ chuẩn của OPA

| Động tác | Scale | Rotation | Thời lượng |
|---|---|---|---|
| Thở | 100 → 103 → 100 % | Sừng ±2° | Chu kỳ 2,5 s |
| Nhịp đập khi hứng | 100 → 104 → 100 % | Sừng ±3° | 0,25 s |
| Bật vào | 0 → 112 → 95 → 100 % | — | 0,75 s |
| Lấy đà | 100 → 96 % | −8° | 0,5 s |
| Lao tới | 96 → 100 % | +6° | 0,4 s |
| Dư âm | — | +6 → −3 → +1 → 0° | 0,85 s |
| Máy đẩy vào | 94–97 → 100 % | — | Suốt clip |

**Luật nhịp:**
- Đoạn đứng yên hoàn toàn không quá 10 % clip.
- Khung đầu trống thì đẩy máy vào suốt clip. Khung đầu có hình thì không đẩy máy, mà cho logo thở.
- **Khung chốt logo** (Minh chốt 24/10/2026): đoạn giữ logo sau khi logo đã hiện xong được miễn đo đứng yên, như khung CTA cuối của V2. P01 bản 2.2 miễn từ 1,20 s, lúc sừng vừa đứng (`do/P01.json`, khóa `exempt`). Đoạn mở đầu không được để nền trống quá 0,2 s.
- **Đo đứng yên trên clip chỉ có logo:** thước V2 tính cả các khung đổi chiều của ease (đỉnh vượt đà, đáy hụt) là "đứng", vì logo chỉ chiếm ~7 % khung. Clip giả làm đúng nhịp vẫn ra 35–49 % ở đoạn bật nảy. Với logo, xem thêm **chuỗi đứng yên dài nhất** (ngưỡng V2: ≤ 0,2 s, tức 5 khung ở 24 fps).

## 2. Luật màu

### 2.1 Bảng màu và vai trò

Chỉ dùng các màu trong BRAND-SPEC mục 1. Prompt luôn ghi **mã hex**, không ghi tên màu chung chung như "blue".

| Mã | Vai trò được phép | Không được dùng cho |
|---|---|---|
| `#0068FF` | Logo trên nền sáng; nền chính của cảnh xanh; bong bóng OPA; nút; viền 2 px của thẻ | — |
| `#FFFFFF` | Nền sáng; logo trên nền xanh; thẻ, ô nhập, nút tròn | Logo trên nền trắng |
| `#E6F0FF` | Bong bóng khách; vạch giữ chỗ; mảng phụ nhạt | Logo |
| `#003C99` | Vật nhỏ: bong bóng tin đang bay, chấm | Nền lớn, logo |
| `#0A0A0A` | Chữ (thêm trong AE); nền tối khi được yêu cầu | Logo xanh |
| `#E5484D` | **Chỉ** chấm cảnh báo nhỏ (≤ 3 % chiều cao khung) | Nền, chữ, logo, mảng lớn |

### 2.2 Luật phối

1. **Logo xanh chỉ trên nền trắng hoặc `#E6F0FF`. Logo trắng chỉ trên `#0068FF`, `#003C99` hoặc `#0A0A0A`.** Không bao giờ để logo xanh trên nền xanh.
2. **Mỗi cảnh tối đa 1 màu nền + 1 màu chính + 2 màu phụ.** Mỗi prompt liệt kê đủ trong khối COLOR; màu nào không có tên trong khối là không được xuất hiện.
3. **Không chỉnh màu:** không color grading, không phủ tông, không đổi độ sáng hay độ bão hòa, không để màu trôi dần giữa các khung. Trắng phải là trắng tuyệt đối.
4. **Không gradient, không màu chuyển.** Đổi màu chỉ bằng mép cứng (khối quét, track matte), như P11.

**Câu chuẩn trong prompt:**

```text
COLOR: <vật> #0068FF; <vật> #FFFFFF; … Only these colors. No color grading, tint, exposure change or color drift between frames; whites stay pure #FFFFFF.
```

## 3. Luật VFX

Motion graphic của OPA là **phẳng**. VFX chỉ được dùng để chuyển động dễ đọc hơn, không để trang trí.

### 3.1 Được dùng (phải ghi rõ mốc và mức)

| VFX | Thông số | Dùng ở |
|---|---|---|
| Motion blur theo hướng | Chỉ trong đoạn nhanh đã ghi mốc; shutter 180°; không có trên khung đứng | P01, P03, P07, P09, P10 |
| Zoom blur | Chỉ ở 0,8 s cuối của cú zoom xuyên; tâm blur = điểm neo zoom | P06 |
| Vẽ nét (Trim Paths) | Nét đều, đầu nét tròn, không phát sáng | P04, P10 |
| Quét phẳng (Linear Wipe) | Mép cứng, không mờ mép | P04, P11 |
| Lộ ra sau mép (Track Matte) | Mép cứng | P03, P09 |
| Biến hình (Path morph) | Một hình liền, không tan, không chớp | P05 |
| Hạt phẳng | Chấm tròn đặc `#0068FF` hoặc `#003C99`, tối đa 10 hạt mỗi cụm, tan trong 0,4 s | P08 |
| Lệch tầng (parallax) | Ba lớp xa gần chạy khác tốc độ, không mờ | P14 |

### 3.2 Bị cấm (luôn ghi trong khối VFX)

Glow, bloom, lens flare, light leak, tia sáng, chromatic aberration, film grain, nhiễu, glitch, tách RGB, bokeh, depth of field, khói, sương, lấp lánh, vệt sáng chạy qua nút (như `BTN_Shine` của mẫu 1), bóng đổ, bevel, phản chiếu, khối 3D, rung máy, vignette.

**Câu chuẩn:**

```text
VFX: allowed only — <danh sách kèm mốc>. Forbidden: glow, bloom, lens flares, light leaks, sparkles, shine sweeps, grain, noise, glitch, chromatic aberration, depth of field, smoke, shadows, bevel, reflections, 3D, camera shake, vignette.
```

## 4. Luật SFX

Omni tạo âm cùng lúc với hình. Âm phải **bám chuyển động**, đúng như cách các video OPA đã duyệt dùng âm.

### 4.1 Mười luật

1. **Mỗi âm gắn với một keyframe.** Điểm đánh của âm rơi đúng mốc giây trong KEYFRAMES, lệch tối đa 1 khung.
2. **Âm có nốt nằm trong hợp âm A trưởng (A, C#, E)**, khớp bộ SFX đã duyệt. Ví dụ: `pop-bubble-low-A4`, `pop-bubble-mid-C#5`, `pop-bubble-high-E5`, `tick-catch-a4`, `ping-a3`.
3. **Chuỗi âm lặp thì nốt đi lên:** A4 → C#5 → E5 → A5…, như tiếng hứng tin của phim "Thủ môn".
4. **Ba mức to:** strong (0 dB, âm chính), medium (−6 dB, âm phụ), soft (−12 dB, âm nền). Mỗi thời điểm chỉ một âm strong.
5. **Hướng âm theo vị trí vật:** vật bên trái kêu bên trái, vật chạy ngang thì âm chạy theo.
6. **Whoosh dài đúng bằng cú di chuyển** và to nhất lúc vật nhanh nhất.
7. **Giữa các âm là im lặng:** không tiếng ù, không tiếng phòng, không đuôi vang dài quá 0,5 s.
8. **Bò "nói" bằng:** hơi mũi phì, sừng gõ "tok" (gỗ khô), thân đáp trầm. **Không** tiếng bò kêu.
9. **Cấm:** nhạc, giọng nói, tiếng người, tiếng động vật, tiếng còi, tiếng glitch hay nhiễu số, nhạc có bản quyền.
10. **Âm của Omni là bản nháp.** Khi đưa vào phim, thay bằng file thư viện (bảng 4.2) rồi master −16 LUFS; bản đăng mạng xã hội −14 LUFS (BRAND-SPEC mục 9).

### 4.2 Từ điển âm → file đã duyệt

| Loại âm (viết trong prompt) | Khi nào | File thay trong After Effects |
|---|---|---|
| `soft bubbly pop` (có nốt) | Bong bóng, nút, nút mạng lưới bật | `ae/opa-agent/assets/sfx/pop-bubble-low-A4.wav`, `pop-bubble-mid-C#5.wav`, `pop-bubble-high-E5.wav` |
| `dry wooden tok` (có nốt) | Sừng khớp, chữ cái đáp | `ae/opa-agent/assets/sfx/ui-wood-marimba-tick.wav` |
| `bright catch pop` (có nốt) | Tin lọt khe | `sfx/03-pops-snaps-elastic/catch-bright-ring.wav` (đổi cao độ theo A trưởng), `ae/opa-agent/assets/sfx/tick-catch-a4.wav` |
| `soft low thump` | Thân đáp, dừng gắt | `ae/opa-agent/assets/sfx/thump-body-punch.wav` |
| `airy whoosh` | Di chuyển, quét màu | `ae/opa-agent/assets/sfx/whoosh-cut-light.wav`, `whoosh-cut-medium.wav`, `whoosh-light-airy.wav` |
| `deep wind-up whoosh` | Lấy đà, hít vào | `ae/opa-agent/assets/sfx/whoosh-deep-windup.wav` |
| `airy nose puff` | Bò phì hơi | `sfx/07-textures-drones-foley/foley-snort-puff.wav` |
| `tiny UI tick` (có nốt) | Huy hiệu, nhịp đập, con trỏ | `ae/opa-agent/assets/sfx/ui-tick-crisp-A6.wav`, `ui-tick-crisp-E6.wav` |
| `soft expand swipe` | Ô nhập kéo dài, biến hình | `ae/opa-agent/assets/sfx/uisfx-glass-expand+155c.wav` |
| `soft typing blips` | Gõ chữ, ba chấm | `ae/opa-agent/assets/sfx/uisfx-minimal-typing.wav` |
| `soft notification ping` | Tin tới | `ae/opa-agent/assets/sfx/ping-a3.wav`, `ping-e4.wav` |
| `soft low whump` | Kết cú zoom xuyên | `sfx/02-impacts-hits/impact-deep-logo.wav` (mức medium) |

Các file trong `ae/opa-agent/assets/sfx/` là bộ đã dùng trong video "OPA Agent × Pancake" v09, Minh duyệt âm ngày 22/10/2026. Các file trong `sfx/` lấy từ cue sheet âm thư viện của phim "Thủ môn" bản 2.

**Mẫu khối SFX:**

```text
SFX (each sound lands exactly on its keyframe; pitched sounds in A major — A, C#, E; levels: strong 0 dB, medium −6 dB, soft −12 dB; silence between cues; no music, voice, animal sounds or long reverb):
- 0.50s soft bubbly pop, A4, strong, center
- …
```

## 5. Ảnh tham chiếu và chế độ đầu vào

### 5.1 Ba chế độ

| Chế độ | Đưa vào | Khi nào dùng | Giới hạn |
|---|---|---|---|
| **A · Khung đầu + cuối** | 2 ảnh `K0x` | Logo phải đúng ở đầu và cuối (hiện logo, chuyển cảnh, nối clip) | Theo tài liệu API, không kèm được ảnh tham chiếu |
| **A1 · Chỉ khung đầu** | 1 ảnh `K0x` | Bắt đầu từ logo đúng, kết mở | Như trên |
| **B · Ảnh tham chiếu** | 1–3 ảnh `T0x` | Cảnh tự do không có khung cuối nhưng cần đúng logo hoặc đúng phong cách | Không ghim bố cục; nền và khung giữ bằng chữ |

Bản API của Omni 1.1 không cho dùng khung và ảnh tham chiếu trong cùng một lần tạo. Giao diện Flow có thể khác; nếu Flow cho đưa cả hai, vẫn ưu tiên chế độ A cho cảnh logo.

### 5.2 Ảnh tham chiếu có sẵn

| File | Nội dung | Gọi trong prompt là |
|---|---|---|
| `T01_dau-bo-xanh_nen-trang.png` | Dấu xanh trên nền trắng | `reference image N — the OPA bull-head logo (blue on white)` |
| `T02_logo-chu-xanh_nen-trang.png` | Dấu + chữ OPA | `reference image N — the OPA lockup` |
| `T03_dau-bo-trang_nen-xanh.png` | Dấu trắng trên nền xanh | `reference image N — the OPA bull-head logo (white on blue)` |
| `T04_bang-phong-cach.png` | Bảng màu + bong bóng, thẻ, nút, ô nhập phẳng | `reference image N — the OPA style board` |

### 5.3 Năm luật dùng tham chiếu

1. **Đưa ảnh theo đúng thứ tự gọi trong prompt.** Thứ tự ảnh là tín hiệu model đọc.
2. **Nói rõ vai trò từng ảnh:**
   - ảnh logo: `keep it identical wherever it appears`;
   - ảnh phong cách: `match its colors, outline weight, corner roundness and flat shapes; do not copy its layout`.
3. **Kết bằng câu ghim:** `Keep the logo identical to reference image 1.`
4. **Không đưa ảnh có chữ** ngoài T02. Không đưa ảnh hoặc video của mẫu Envato (giấy phép).
5. Nếu Flow hiện thẻ tên cho ảnh (ví dụ `@image1`), thay chữ `reference image 1` bằng thẻ đó.

## 6. Giữ nguyên định dạng và giữ nguyên nền

### 6.1 FORMAT LOCK

Giữ đúng tỉ lệ đã chọn trong Flow, tràn khung. Cấm:
- viền đen, letterbox, khung viền, góc bo;
- chia đôi màn hình, cảnh lồng cảnh;
- chữ, phụ đề, watermark, giao diện máy;
- cắt cảnh, chuyển cảnh lạ;
- quay chậm, tăng giảm tốc, dừng hình (trừ khi KEYFRAMES ghi);
- phóng hay cắt mép của khung đầu, khung cuối (bố cục hai khung đó phải trùng từng vị trí).

```text
FORMAT LOCK: <16:9 | 9:16>, full frame, exactly <N> seconds, one continuous shot. Keep the exact framing of the given frames — no crop, reframing, black bars, borders, split screen, captions, watermark, cuts, slow motion, speed ramps or freeze frames.
```

### 6.2 BACKGROUND LOCK

Nền là **một màu phẳng đúng mã hex, suốt mọi khung**. Cấm:
- gradient, hoa văn, chất liệu, nhiễu, vignette;
- ánh sáng thay đổi, bóng đổ lên nền;
- sàn, đường chân trời, tường, phòng, bầu trời;
- vật trang trí hay hạt bay ở nền;
- máy di chuyển làm lộ nền mới.

Chỉ được đổi màu nền khi KEYFRAMES ghi rõ (P06 kết bằng màu nền cũ; P11 đổi bằng khối quét).

```text
BACKGROUND LOCK: solid <#FFFFFF | #0068FF> in every frame — no gradient, texture, noise, vignette, light change, shadows, floor, horizon, room, sky, decoration or background particles. Camera moves never reveal anything new behind.
```

**Khi sửa bằng hội thoại**, câu mở đầu luôn nhắc giữ cả hai:

```text
Keep everything else exactly the same — same format and framing, same background, same colors, same timing and same sound. Only …
```

## 7. Prompt khởi tạo phiên (Agent của Flow)

Dán một lần khi mở project. Các prompt sau vẫn giữ đủ khối khóa, vì chưa kiểm được Agent nhớ quy ước qua nhiều lượt.

```text
You are my motion designer for OPA logo animations in this project. Apply these rules to every request.

UNITS: seconds; positions in % of the frame, (0%,0%) = top-left; scale in % of the last-frame size; rotation in degrees, positive = clockwise.
ANCHORS on the OPA bull-head (in % of its bounding box): bottom-center (50%,100%); horn roots (22.6%,42.1%) and (77.4%,42.1%); inner opening center (50%,64.7%); top gap center (50%,40.2%).
EASING: linear; ease-in-out; ease-out 80%; pop (one ~12% overshoot); ease-in 90%; sine; decay (each swing half the previous).
COLOR: only #0068FF, #FFFFFF, #E6F0FF, #003C99, #0A0A0A, and #E5484D for tiny alert dots only. Blue logo only on white or #E6F0FF; white logo only on #0068FF, #003C99 or #0A0A0A. No gradients, grading, tint or color drift.
FORMAT: keep the chosen aspect ratio, full frame, one continuous shot; no crop, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND: one flat solid color in every frame; nothing appears behind; no light change.
VFX: only motion blur, zoom blur, line draw, hard-edged wipes, track-matte reveals, shape morphs and flat dot particles when I list them. Never glow, flares, sparkles, shine sweeps, grain, glitch, depth of field, smoke, shadows, 3D or camera shake.
SFX: every sound lands on a keyframe; pitched sounds in A major (A, C#, E), rising when repeated; levels strong 0 dB / medium −6 dB / soft −12 dB; silence between cues; the bull speaks only with nose puffs, wooden "tok" horn clicks and soft low thumps. Never music, voice, animal sounds or long reverb.
REFERENCES: when I attach reference images, keep any logo identical to them and use the style board only for look, not layout.
NEVER DRAW THE DATA: my prompts contain timings, names, numbers and notes as invisible instructions; never show labels, numbers, guides, diagrams or any text on screen unless I ask for on-screen text.
LOGO: the bull-head is a flat logo, not a character — never add eyes, mouth, face, limbs or details; uniform scaling only.
PRIORITY when something conflicts: 1) logo, color and background locks, 2) exact first and last frames, 3) timing and sound sync, 4) exact values.

Reply only "OK" and wait for my first shot.
```

## 8. Mười lăm prompt

| # | Tên | Chế độ | Đầu vào | Nền | Dài |
|---|---|---|---|---|---|
| P01 | Bật nảy | A | K00 → K01 | trắng | 5 s |
| P02 | Thở lặp | A | K01 → K01 | trắng | 5 s |
| P03 | Lắp ráp + chữ | A | K00 → K04 | trắng | 6 s |
| P04 | Vẽ nét, đổ màu | A | K00 → K01 | trắng | 5 s |
| P05 | Bong bóng hóa đầu bò | A | K05 → K01 | trắng | 6 s |
| P06 | Chui qua lòng O | A | K02 → K03 | xanh | 4 s |
| P07 | Lao tới | A | K06 → K01 | trắng | 4 s |
| P08 | Hứng tin nhắn | A | K01 → K01 | trắng | 8 s |
| P09 | Đóng logo | A | K01 → K04 | trắng | 6 s |
| P10 | Mạng lưới kênh | A | K02 → K07 | xanh | 6 s |
| P11 | Quét màu đảo nền | A | K01 → K02 | trắng → xanh | 3 s |
| P12 | Thông báo dồn (nền cho AE) | B | T04 | trắng | 5 s |
| P13 | Ô nhập kéo dài (nền cho AE) | B | T04 | xanh | 4 s |
| P14 | Zoom ra thành tường thẻ chat | A1 | K01 | trắng | 6 s |
| P15 | Điện thoại trồi lên | B | T03 + T04 | xanh | 5 s |

Prompt viết cho 16:9. Làm bản 9:16 thì đổi `16:9` trong FORMAT LOCK và thay vị trí theo cột 9:16 của bảng 1.3.

---

### P01 · Bật nảy · A · K00 → K01 · 5 s · bản 2.2

Bản 2.2 (Minh chốt 24/10): **dời cả nhịp sớm 0,3 s**. Đầu bò bật từ 0,20 s, bỏ 0,5 s nền trắng chết ở đầu. Khung chốt bắt đầu lúc sừng phải vừa đứng (1,20 s).

Bản 2.1 (23/10, sau lần chạy đầu): Omni vẽ cả tên lớp, con số, tên nốt lên hình; tự thêm chữ OPA; diễn thêm sau 6 s. Đo và kết luận: `do/OPA_logo_animation_rules_20261023170017/KET-LUAN-VA-PROMPT-SUA.md`.

Trong Flow:
- đặt thời lượng **5 s** trong phần cài đặt;
- bật chế độ khung đầu `K00`, khung cuối `K01`;
- không gắn ảnh tham chiếu.

Thử kiểu A trước; nếu vẫn hiện chữ thì dùng kiểu B.

**Kiểu A: có thông số**

```text
OPA logo animation — flat 2D vector motion graphics.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first frame = empty white (given); last frame = the OPA bull-head mark alone, centered (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 5 seconds, one continuous shot. Keep the exact framing of the given frames — no crop, reframing, bars, borders, captions, watermark, cuts, slow motion or speed ramps.
BACKGROUND LOCK: solid #FFFFFF in every frame — no gradient, texture, vignette, light change, shadows, faint text, scribbles, ghost shapes, ripples or background objects.
COLOR: the mark is solid #0068FF, exactly as in the last frame. No grading, tint or color drift.
MOTION (seconds; scale in % of the last-frame size; rotation positive = clockwise):
- The head starts popping almost immediately, from a single point at its bottom-center: 0.20s 0% → 0.60s 112% (fast ease-out) → 0.80s 95% → 0.95s 100%. Its bottom edge stays planted.
- The left horn grows from its root where it joins the head and swings up: 0.45s −40° → 0.95s +6° → 1.10s 0°. The right horn mirrors it, 0.08s later.
- The whole frame pushes in very slowly and steadily: 0.00s 97% → 5.00s 100%.
- After 1.20s nothing else animates: no second pop, no pulse, no ripple, no re-scaling — only the slow push continues.
VFX: light motion blur only during the fast pop (0.20–0.60s) and the horn swing (0.45–0.95s). Nothing else: no glow, flares, sparkles, grain, glitch, shadows, 3D or camera shake.
SOUND (audio only, never shown): exactly three sounds and silence everywhere else — a soft bubbly pop at 0.20s; a dry wooden click at 0.95s; a second, slightly higher wooden click at 1.03s. Both clicks tuned to an A major chord. Gentle levels, no clipping, no music, no voice, no animal sounds, no extra hits or swells.
LOGO LOCK: the bull-head mark only — no "OPA" letters, no wordmark, no text. Identical to the last frame: same silhouette, proportions and horn shape, crisp edges. A flat logo, not a character: no eyes, mouth or face. Uniform scaling only.
```

**Kiểu B: chỉ ý định**

```text
A clean, premium flat 2D logo reveal on a plain pure white background, 5 seconds, one continuous shot, 16:9. Start on the given empty white frame and end exactly on the given last frame: the blue OPA bull-head mark alone in the center.
Almost immediately — a fifth of a second in — the U-shaped head pops up from a tiny point at its base, overshoots a little and settles with one tight bounce, its base staying planted. Right after, the two horns sprout from their roots and swing up into place, the left one a moment before the right, each with a small overshoot. Then the frame keeps a very slow, steady push-in until the end; nothing else moves.
Flat solid #0068FF on pure white. No text, letters, numbers, labels, guides or diagrams anywhere; no "OPA" wordmark. No gradients, glow, shadows, sparkles, ripples, ghost shapes or 3D. Never squash or stretch the mark; it is a flat logo, not a character.
Sound: one soft bubbly pop when the head appears, then two dry wooden clicks as the horns lock, the second slightly higher; silence otherwise. No music, voice or animal sounds.
```

**Đọc nhanh:** đầu chữ U bật từ điểm đáy ngay từ 0,2 s (đáy đứng yên), vượt 112 % rồi hụt 95 % rồi đứng lúc 0,95 s. Sừng xoay quanh gốc từ −40° về 0°, sừng phải trễ 0,08 s, đứng hẳn lúc 1,18 s. Từ 1,2 s chỉ còn máy đẩy chậm. Đúng ba âm: 0,20 · 0,95 · 1,03 s.

**Khung chốt:** từ 1,20 s đến hết là khung chốt logo, miễn đo đứng yên (Minh chốt 24/10/2026). Thông số đo ở `do/P01.json`. Thử trên clip giả đúng nhịp này: ngoài khung chốt, chuỗi đứng dài nhất 5 khung (0,21 s), đạt ngưỡng V2.

**Tỷ lệ nhịp:** chờ 4 % · bật nảy và sừng 20 % · khung chốt 76 %.

---

### P02 · Thở lặp · A · K01 → K01 · 5 s

```text
OPA logo animation — seamless loop, flat 2D vector motion graphics.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first and last frames = the same OPA bull-head logo centered at (50%,50%) (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 5 seconds, one continuous shot that loops perfectly. No crop, reframing, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #FFFFFF in every frame — no gradient, texture, vignette, light change, shadows or background objects.
COLOR: logo #0068FF only. No grading, tint or color drift.
UNITS: seconds; scale in % of the last-frame size; rotation in degrees, positive = clockwise.
LAYERS & ANCHOR POINTS: LOGO = whole bull-head, anchor bottom-center (50%,100% of its box). HORN_L, HORN_R, anchor at each horn's root.
KEYFRAMES:
- LOGO scale: 0.00s 100% → 1.25s 103% → 2.50s 100% → 3.75s 103% → 5.00s 100% [sine].
- HORN_L rotation: 0° → 1.25s −2° → 2.50s 0° → 3.75s −2° → 5.00s 0° [sine]; HORN_R mirrored (+2°).
- Camera locked.
VFX: none. Forbidden: glow, flares, sparkles, grain, glitch, depth of field, shadows, 3D, camera shake, vignette.
TIMING RATIO: inhale 50% · exhale 50%, two identical cycles; nothing ever stops.
DIRECTOR NOTE: A calm, strong breath — the logo swells gently from its base and the horns open slightly on each inhale, even like a resting heartbeat.
SFX (no music, voice or animal sounds; the sound at 5.00s matches 0.00s so the loop is seamless):
- 0.00–1.25s and 2.50–3.75s very soft low inhale of air, soft, center
- 1.25–2.50s and 3.75–5.00s near silence
LOGO LOCK: the bull-head mark only — no "OPA" letters, no wordmark, no text. Identical to the first and last frame — same silhouette, proportions and horn shape. A flat logo, not a character: no eyes, mouth, face or extra details. Uniform scaling only.
```

---

### P03 · Lắp ráp + chữ OPA · A · K00 → K04 · 6 s

```text
OPA logo animation — flat 2D vector motion graphics.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first frame = empty white (given); last frame = the OPA lockup: bull-head mark centered at (29.3%,50%) with the "OPA" wordmark to its right (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 6 seconds, one continuous shot. Keep the exact framing of the last frame — no crop, reframing, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #FFFFFF in every frame — no gradient, texture, vignette, light change, shadows or background objects.
COLOR: mark and wordmark #0068FF only. No grading, tint or color drift.
UNITS: seconds; positions in % of frame; scale in % of the last-frame size; rotation in degrees, positive = clockwise.
LAYERS & ANCHOR POINTS: HEAD = U-shaped head of the mark, anchor bottom-center. HORNS = both horns, anchor at each root. LETTER_O, LETTER_P, LETTER_A = wordmark letters, hidden behind an invisible vertical edge at the right side of the mark (track matte). CAMERA = whole frame.
KEYFRAMES:
- HEAD position y: 0.50s below the frame (y 120%) → 1.00s final place [ease-out 80%].
- HORNS position y: 1.00s above the frame (y −20%) → 1.50s final place [ease-in, hard stop]; rotation 1.00s ±20° → 1.50s 0°.
- HEAD scale: 1.50s 100% → 1.62s 97% → 1.75s 100% (impact dip).
- LETTER_O x: 1.75s hidden → 2.25s final [ease-out 80%]; LETTER_P +0.12s; LETTER_A +0.25s. Letters only slide, never change shape.
- CAMERA scale: 0.00s 96% → 6.00s 100% [linear].
VFX: allowed only — vertical motion blur on HEAD 0.50–1.00s and HORNS 1.00–1.50s; hard-edged track-matte reveal for the letters. Forbidden: glow, flares, sparkles, shine sweeps, grain, glitch, depth of field, smoke, shadows, 3D, camera shake, vignette.
TIMING RATIO: wait 8% · build 17% · letters 17% · slow push 58%.
DIRECTOR NOTE: Parts snapping together — the head rises, the horns drop and lock with a firm click, the head absorbs the impact, then the letters glide out from behind the mark.
SFX (each sound on its keyframe; pitched sounds in A major; strong 0 dB, medium −6 dB, soft −12 dB; silence between cues; no music, voice or animal sounds):
- 0.50–1.00s quick rising swoosh, medium, bottom to center
- 1.50s dry wooden tok (both horns together), A4, strong, center-left
- 1.55s soft low thump, medium
- 2.25s, 2.37s, 2.50s tiny UI ticks for O, P, A, notes A5, C#6, E6, soft, panning left to right
LOGO LOCK: mark and wordmark identical to the last frame — same shapes, spacing and proportions. No other text or letters. No eyes, face or extra details. Uniform scaling only.
```

---

### P04 · Vẽ nét rồi đổ màu · A · K00 → K01 · 5 s

```text
OPA logo animation — "draw-on" style, flat 2D vector motion graphics.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first frame = empty white (given); last frame = the OPA bull-head logo centered at (50%,50%) (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 5 seconds, one continuous shot. No crop, reframing, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #FFFFFF in every frame — no paper texture, gradient, vignette, light change, shadows or background objects.
COLOR: outline and fills #0068FF only. No grading, tint or color drift.
UNITS: seconds; scale in % of the last-frame size.
LAYERS & ANCHOR POINTS: OUTLINE = thin stroke along the logo silhouette, 0.8% of the frame height thick, starting at the bottom-center. HEAD_FILL = fill of the U-shaped head, wiped bottom to top. HORN_FILL = fill of each horn, wiped root to tip. CAMERA = whole frame.
KEYFRAMES:
- OUTLINE trim: 0.25s 0% → 1.50s 100%, growing from the bottom-center in both directions at the same speed [ease-in-out].
- HEAD_FILL wipe: 1.25s 0% → 2.00s 100% [ease-in-out].
- HORN_FILL wipe: 1.75s 0% → 2.50s 100% [ease-out 80%].
- OUTLINE merges into the fill at 2.50s.
- CAMERA scale: 0.00s 94% → 5.00s 100% [linear].
VFX: allowed only — line draw (round caps, even width) and hard-edged flat wipes. Forbidden: glow, liquid, paint texture, brush strokes, sparkles, grain, glitch, depth of field, shadows, 3D, camera shake, vignette.
TIMING RATIO: wait 5% · draw 25% · fill 20% · slow push 50%.
DIRECTOR NOTE: A designer drawing the mark live — a clean line traces the shape, flat blue fills it from the bottom up, the horns fill last.
SFX (each sound on its keyframe; pitched sounds in A major; strong 0 dB, medium −6 dB, soft −12 dB; silence between cues; no music, voice or animal sounds):
- 0.25–1.50s light pencil-like scratch following the line, soft, panning with the line
- 1.25–2.00s soft rising whoosh, medium
- 2.50s dry wooden tok, A4, strong, center
LOGO LOCK: the bull-head mark only — no "OPA" letters, no wordmark, no text. Identical to the last frame — same silhouette, proportions and horn shape, crisp edges. A flat logo, not a character: no eyes, mouth, face or extra details.
```

---

### P05 · Bong bóng chat hóa đầu bò · A · K05 → K01 · 6 s

```text
OPA logo animation — flat 2D vector motion graphics: a chat message becomes the logo.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first frame = a #0068FF chat bubble with three white dots, centered (given); last frame = the OPA bull-head logo, centered (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 6 seconds, one continuous shot. No crop, reframing, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #FFFFFF in every frame — no gradient, texture, vignette, light change, shadows or background objects.
COLOR: bubble, head and horns #0068FF; dots #FFFFFF. Only these colors. No grading, tint or color drift.
UNITS: seconds; positions in % of frame; scale in % of the last-frame size; rotation in degrees, positive = clockwise.
LAYERS & ANCHOR POINTS: DOT_1–3, anchor each dot's center. BUBBLE = bubble with its tail, anchor bubble center. HEAD = U-shaped head the bubble becomes, anchor bottom-center. HORN_L, HORN_R, anchor at each root.
KEYFRAMES:
- DOTS y: 0.00–1.00s each bounces up 1.5% of the frame height and back, in a wave, 0.12s apart [sine].
- BUBBLE scale: 1.00s 100% → 1.25s 92% [ease-in-out] (anticipation).
- BUBBLE → HEAD morph: 1.25s → 2.50s, one continuous shape, the tail retracts [ease-in-out].
- DOTS: 1.25s slide to the center → 1.75s drop into the hollow of the U and vanish [ease-in].
- HORN_L: 2.25s scale 0%, rotation −30° → 2.75s +5° → 3.00s 0° [pop]; HORN_R mirrored.
- LOGO scale: 3.00s 100% → 3.75s 102% → 4.50s 100% → 5.25s 102% → 6.00s 100% [sine], anchor bottom-center.
- Camera locked.
VFX: allowed only — one continuous shape morph (no cut, flash or dissolve) and light motion blur on the horns 2.25–2.75s. Forbidden: glow, sparkles, particles, grain, glitch, depth of field, shadows, 3D, camera shake, vignette.
TIMING RATIO: typing 17% · anticipation 4% · morph 29% · settle with breaths 50%.
DIRECTOR NOTE: The typing dots bounce, the bubble gathers itself, then reshapes into the bull's head and sprouts its horns — a customer message turning into OPA.
SFX (each sound on its keyframe; pitched sounds in A major; strong 0 dB, medium −6 dB, soft −12 dB; silence between cues; no music, voice or animal sounds):
- 0.00–1.00s soft typing blips on each dot bounce, A5, C#6, E6, soft
- 1.00s small deep wind-up whoosh, soft
- 1.25–2.50s soft expand swipe following the morph, medium
- 1.75s tiny drop pop as the dots fall in, A4, soft
- 2.75s dry wooden tok, E5, strong, center
LOGO LOCK: the bull-head mark only — no "OPA" letters, no wordmark, no text. The final logo identical to the last frame — same silhouette, proportions and horn shape, crisp edges. A flat logo, not a character: no eyes, mouth, face or extra details. Uniform scaling only.
```

---

### P06 · Chui qua lòng chữ O · A · K02 → K03 · 4 s

```text
OPA logo transition — flat 2D vector motion graphics.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first frame = the white OPA bull-head logo centered on #0068FF (given); last frame = completely plain #0068FF (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 4 seconds, one continuous shot. No crop of the first frame, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #0068FF in every frame, including the final second — no gradient, vignette, light change, flash or background objects.
COLOR: logo #FFFFFF on #0068FF. Only these two colors. No grading, tint or color drift.
UNITS: seconds; scale in % of the first-frame size.
LAYERS & ANCHOR POINTS: LOGO = the white bull-head. ANCHOR = the center of its inner opening (the hollow inside the U), (50%,64.7%) of the logo box = (50%,56.8%) of the frame. All scaling happens around this point, so the camera dives into the hollow, not into the forehead.
KEYFRAMES:
- LOGO scale: 0.00s 100% → 0.75s 95% [ease-in-out] (pull back).
- LOGO scale: 0.75s 95% → 3.00s 2500% [ease-in 90%: slow, then sharply accelerating].
- 3.00–4.00s plain #0068FF, perfectly still.
VFX: allowed only — zoom blur centered on the anchor from 2.20s to 3.00s. Forbidden: glow, white flash, flares, sparkles, grain, glitch, depth of field, shadows, 3D, camera shake, vignette.
TIMING RATIO: breath 19% · dive 56% · blue 25%.
DIRECTOR NOTE: A short breath back, then a dive straight through the hollow of the U; the white walls rush past the frame edges until only the blue inside remains.
SFX (each sound on its keyframe; strong 0 dB, medium −6 dB, soft −12 dB; silence between cues; no music, voice or animal sounds):
- 0.00–0.75s deep wind-up whoosh, soft
- 0.75–3.00s airy whoosh rising with the zoom from soft to strong, center
- 3.00s soft low whump, medium
- 3.00–4.00s silence
LOGO LOCK: the bull-head mark only — no "OPA" letters, no wordmark, no text. The same silhouette in every frame until it leaves the screen. A flat logo, not a character: no eyes, face or extra details. Uniform scaling only.
```

---

### P07 · Lao tới · A · K06 → K01 · 4 s

```text
OPA logo animation — flat 2D vector motion graphics; the logo acts with posture only.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first frame = the logo at (28%,50%) (given); last frame = the same logo centered at (50%,50%), same size (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 4 seconds, one continuous shot. Camera locked; no crop, reframing, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #FFFFFF in every frame — no floor, ground line, dust, shadows, gradient, vignette or background objects.
COLOR: logo #0068FF only. No grading, tint or color drift.
UNITS: seconds; positions in % of frame; scale in % of the last-frame size; rotation in degrees, positive = clockwise.
LAYERS & ANCHOR POINTS: LOGO = whole bull-head, anchor bottom-center (50%,100% of its box); all rotation pivots here. HORNS, anchor at each root; they follow the LOGO 0.08s late (overlap).
KEYFRAMES:
- LOGO scale: 0.00s 100% → 0.25s 101.5% → 0.50s 100% [sine].
- ANTICIPATION 0.50s → 1.00s [ease-in-out]: rotation 0° → −8°; position x 28% → 26%; scale 100% → 96%.
- CHARGE 1.00s → 1.40s [ease-out 80%]: position x 26% → 50%; rotation −8° → +6°; scale 96% → 100%.
- FOLLOW-THROUGH 1.40s → 2.25s [decay]: rotation +6° → −3° (1.60s) → +1° (1.80s) → 0° (2.25s).
- SETTLE: scale 2.25s 100% → 3.10s 102% → 4.00s 100% [sine].
VFX: allowed only — strong horizontal motion blur 1.00–1.40s. Forbidden: speed lines, dust, impact flash, glow, sparkles, grain, glitch, depth of field, shadows, 3D, camera shake, vignette.
TIMING RATIO: breath 12% · anticipation 13% · charge 10% · follow-through 21% · settle 44%.
DIRECTOR NOTE: A determined bull told only through posture — it leans back gathering power, dashes to the center, stops hard, rocks twice and stands firm.
SFX (each sound on its keyframe; pitched sounds in A major; strong 0 dB, medium −6 dB, soft −12 dB; silence between cues; no music, voice, mooing or other animal sounds):
- 0.50s airy nose puff, medium, left
- 0.50–1.00s deep wind-up whoosh, soft, left
- 1.00–1.40s fast whoosh, strong, panning left to center
- 1.40s soft low thump, strong, center
- 1.48s dry wooden tok, A4, medium, center
LOGO LOCK: the bull-head mark only — no "OPA" letters, no wordmark, no text. Identical to the last frame — same silhouette, proportions and horn shape. A flat logo, not a character: no eyes, mouth, face, legs or extra details. Uniform scaling only, never squash or stretch.
```

**Bản 9:16:** dấu từ (50 %, 63,1 %) lao lên (50 %, 45,6 %). Đổi `position x 28% → 26%` thành `position y 63.1% → 64.5%`, `position x 26% → 50%` thành `position y 64.5% → 45.6%`, `horizontal` thành `vertical`, `left` thành `bottom` trong SFX.

---

### P08 · Hứng tin nhắn · A · K01 → K01 · 8 s

```text
OPA logo animation — flat 2D vector motion graphics: the bull catches every message.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first and last frames = the same OPA bull-head logo centered at (50%,50%) (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 8 seconds, one continuous shot. Camera locked; no crop, reframing, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #FFFFFF in every frame — no gradient, texture, vignette, light change, shadows or background objects; only the listed bubbles and dots move.
COLOR: logo #0068FF; bubbles #003C99; puff dots #0068FF. Only these colors. No grading, tint or color drift.
UNITS: seconds; positions in % of frame; scale in % of the last-frame size; rotation in degrees, positive = clockwise.
LAYERS & ANCHOR POINTS: LOGO, anchor bottom-center. HORNS, anchor at each root. BUBBLE_1–5 = small flat chat-bubble icons (rounded, with a tail, no text), 4% of the frame width, auto-oriented along their paths. GAP = top gap between the horns at (50%,45.5%). PUFFS = dots from the gap edges (47.5%,45.5%) and (52.5%,45.5%).
KEYFRAMES:
- LOGO scale: 0.00s 100% → 0.50s 102% → 1.00s 100% [sine].
- BUBBLE_n launch at 1.00s, 2.00s, 3.00s, 4.00s, 5.00s from the left, right, bottom, left and right edges, each on a curved arc, reaching GAP 0.75s after launch [ease-in], then sinking into the hollow and dissolving.
- Each catch (1.75s, 2.75s, 3.75s, 4.75s, 5.75s): LOGO scale 100% → 104% → 100% in 0.25s [pop]; HORNS ±3° → 0° [decay].
- PUFFS: 6.00s two puffs rise 5% of the frame height, gone by 6.40s.
- LOGO scale: 7.00s 100% → 7.50s 102% → 8.00s 100% [sine].
VFX: allowed only — light motion blur on the flying bubbles; flat solid dot particles for PUFFS (at most 10 dots per puff, no glow). Forbidden: glow, sparkles, stars, trails, grain, glitch, depth of field, shadows, 3D, camera shake, vignette.
TIMING RATIO: breath 12% · five catches on the beat 63% · snort 12% · breath 13%.
DIRECTOR NOTE: Messages arrive one per second like a steady beat and every one lands inside the bull's head — none is missed. The snort at the end says "done".
SFX (each sound on its keyframe; pitched sounds in A major, rising; strong 0 dB, medium −6 dB, soft −12 dB; silence between cues; no music, voice or animal sounds):
- each launch: soft airy whoosh, soft, panned from the bubble's side
- catches 1.75s, 2.75s, 3.75s, 4.75s, 5.75s: bright catch pop on A4, C#5, E5, A5, C#6, medium, center
- 6.00s airy nose puff, strong, center
LOGO LOCK: the bull-head mark only — no "OPA" letters, no wordmark, no text. Identical to the first and last frame — same silhouette, proportions and horn shape. A flat logo, not a character: no eyes, mouth, face or extra details. Uniform scaling only.
```

**Bản 6 s cho promo C5:** 3 bong bóng phóng ở 0,75 s · 2,0 s · 3,25 s, chỉ từ trái, phải, dưới; hứng ở 1,5 s · 2,75 s · 4,0 s (A4, C#5, E5); PUFFS ở 4,5 s; thở 5,25–6,0 s.

---

### P09 · Đóng logo · A · K01 → K04 · 6 s

```text
OPA logo animation — flat 2D vector motion graphics.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first frame = the bull-head mark centered at (50%,50%), 46% of the frame height (given); last frame = the OPA lockup: the mark at (29.3%,50%) at 64.6% of its first size, with the "OPA" wordmark to its right (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 6 seconds, one continuous shot. Keep the exact framing of both given frames — no crop, reframing, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #FFFFFF in every frame — no gradient, texture, vignette, light change, shadows or background objects.
COLOR: mark and wordmark #0068FF only. No grading, tint or color drift.
UNITS: seconds; positions in % of frame; scale in % of the first-frame mark size.
LAYERS & ANCHOR POINTS: MARK = bull-head, anchor its box center. LETTER_O, LETTER_P, LETTER_A, hidden behind an invisible vertical edge at the right side of the mark (track matte). LOCKUP = mark + wordmark, anchor lockup center.
KEYFRAMES:
- MARK scale: 0.00s 100% → 0.25s 101.5% → 0.50s 100% [sine].
- MARK position: 0.50s (50%,50%) → 1.50s (29.3%,50%) [ease-in-out]; scale 0.50s 100% → 1.50s 64.6% [ease-in-out].
- LETTER_O x: 1.25s hidden → 1.75s final [ease-out 80%]; LETTER_P +0.12s; LETTER_A +0.25s. Letters only slide.
- LOCKUP scale: 2.25s 100% → 3.15s 102% → 4.10s 100% → 5.05s 102% → 6.00s 100% [sine].
VFX: allowed only — light horizontal motion blur on MARK 0.50–1.50s; hard-edged track-matte reveal for the letters. Forbidden: glow, flares, sparkles, shine sweeps, grain, glitch, depth of field, shadows, 3D, camera shake, vignette.
TIMING RATIO: breath 8% · glide 17% · letters 13% · breathing hold 62%.
DIRECTOR NOTE: The mark glides into its place in the lockup while the letters slide out from behind it, then the whole signature breathes calmly.
SFX (each sound on its keyframe; pitched sounds in A major; strong 0 dB, medium −6 dB, soft −12 dB; silence between cues; no music, voice or animal sounds):
- 0.50–1.50s smooth glide whoosh, medium, panning center to left
- 1.75s, 1.87s, 2.00s tiny UI ticks for O, P, A, notes A5, C#6, E6, soft, panning left to right
- 2.25s warm low wooden tok, A3, strong, center
LOGO LOCK: mark and wordmark identical to the last frame — same shapes, spacing and proportions. No other text. No eyes, face or extra details. Uniform scaling only.
```

**Bản 9:16:** MARK từ (50 %, 45,6 %) tới (22,5 %, 45,6 %), scale 42,8 %.

---

### P10 · Mạng lưới kênh · A · K02 → K07 · 6 s

```text
OPA motion graphics — flat 2D vector: one OPA, every channel.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first frame = the white bull-head logo centered on #0068FF (given); last frame = the logo at (50%,46.3%) at 60% of its first size, ringed by six white round icon buttons joined by thin white lines (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 6 seconds, one continuous shot. Keep the exact framing of both given frames — no crop, reframing, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #0068FF in every frame — no gradient, glow, grid, stars, vignette, light change or background objects.
COLOR: logo, buttons and lines #FFFFFF; icon glyphs inside the buttons #0068FF. Only these two colors. No grading, tint or color drift.
UNITS: seconds; positions in % of frame; scale in % of the first-frame logo size.
LAYERS & ANCHOR POINTS: LOGO, anchor box center. NODE_1–6 = round icon buttons clockwise from the top: globe, phone, chat bubble, envelope, person icon, shopping bag, on an ellipse 27% of the frame width × 28% of the frame height around the logo, each 11% of the frame height. SPOKES = lines from just outside the logo to each node. RING = thinner lines between neighbouring nodes.
KEYFRAMES:
- LOGO scale: 0.00s 100% → 0.50s 102% → 1.00s 100% [sine].
- LOGO: 1.00s → 2.50s scale 100% → 60%, position (50%,50%) → (50%,46.3%) [ease-in-out].
- NODE_n: launch from behind the logo at 1.50s + 0.25s × (n−1), fly straight to its ring position, scale 0% → 110% → 100% [pop].
- SPOKES trim 2.50s → 3.25s (from the logo outward) [ease-out 80%]; RING trim 3.25s → 4.00s.
- NODE_n pulse at 4.00s + 0.33s × (n−1): scale 100% → 108% → 100% in 0.25s [pop].
VFX: allowed only — light motion blur on nodes while flying (1.50–3.00s); line draw with even width. Forbidden: glow on lines or nodes, sparkles, data particles, grain, glitch, depth of field, shadows, 3D, camera shake, vignette.
TIMING RATIO: breath 17% · pull-back and burst 25% · lines 25% · pulses 33%.
DIRECTOR NOTE: The camera pulls back as six channels burst out of OPA and get wired together — one assistant on every channel, each blinking as a message arrives.
SFX (each sound on its keyframe; pitched sounds in A major, rising; strong 0 dB, medium −6 dB, soft −12 dB; silence between cues; no music, voice or animal sounds):
- 1.00–2.50s soft airy whoosh for the pull-back, medium
- node landings around 1.75s, 2.00s, 2.25s, 2.50s, 2.75s, 3.00s: soft bubbly pops A4, C#5, E5, A5, C#6, E6, medium, panned to each node's side
- 2.50–4.00s gentle rising shimmer with no melody, soft
- pulses from 4.00s: tiny UI ticks, soft, panned to each node
LOGO LOCK: the bull-head mark only — no "OPA" letters, no wordmark, no text. The logo keeps its exact silhouette; icons simple and identical to the last frame — no photos, faces or text. Uniform scaling only.
```

---

### P11 · Quét màu đảo nền · A · K01 → K02 · 3 s

```text
OPA motion graphics transition — flat 2D vector.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first frame = blue OPA bull-head logo centered on white (given); last frame = the same logo in white, centered on solid #0068FF (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 3 seconds, one continuous shot. Camera locked; no crop, reframing, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #FFFFFF until the panel passes, then solid #0068FF — the panel is the only thing that changes the background; no gradient between them.
COLOR: #0068FF and #FFFFFF only. Wherever the panel covers the logo, the logo becomes #FFFFFF (track matte); the flip travels exactly with the panel edge. No grading, tint or color drift.
UNITS: seconds; positions in % of frame.
LAYERS & ANCHOR POINTS: PANEL = flat #0068FF panel as tall as the frame with a straight vertical leading edge, anchor at that edge. LOGO = bull-head, same size and place in both frames, anchor bottom-center.
KEYFRAMES:
- LOGO scale: 0.00s 100% → 0.50s 101.5% → 0.75s 100% [sine].
- PANEL leading edge x: 0.75s 0% → 1.75s 100% [ease-in-out].
- LOGO scale: 1.75s 100% → 2.40s 102% → 3.00s 100% [sine].
VFX: allowed only — one hard-edged wipe (no feather, no blur on the edge). Forbidden: motion blur on the panel, glow, flash, sparkles, grain, glitch, shadows, 3D, camera shake, vignette.
TIMING RATIO: breath 25% · sweep 33% · breath 42%.
DIRECTOR NOTE: A clean blue sweep crosses the frame and inverts the colors as it passes — the logo turns white exactly at the moving edge.
SFX (no music, voice or animal sounds; silence before and after):
- 0.75–1.75s clean airy whoosh, medium, panning left to right
LOGO LOCK: the bull-head mark only — no "OPA" letters, no wordmark, no text. Same silhouette and size in every frame. A flat logo, not a character: no eyes, face or extra details.
```

---

### P12 · Thông báo dồn (nền cho AE) · B · T04 · 5 s

```text
Flat 2D vector motion graphics plate for compositing.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: reference image 1 = the OPA style board — match its colors, outline weight, corner roundness and flat shapes; do not copy its layout. No first or last frame.
FORMAT LOCK: 16:9, full frame, exactly 5 seconds, one continuous shot. No bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #FFFFFF in every frame — no gradient, texture, vignette, light change, shadows or background objects.
COLOR: bubbles #E6F0FF; alert dots #E5484D, only as small dots (at most 3% of the frame height). Nothing else colored. No grading, tint or color drift.
UNITS: seconds; positions in % of frame; scale in %.
LAYERS & ANCHOR POINTS: BUBBLE_1 at (22%,30%), BUBBLE_2 at (70%,38%), BUBBLE_3 at (35%,68%) = empty rounded chat bubbles with a tail, 20% of the frame width, anchor at the tip of each tail. BADGE_n = small empty #E5484D dot at the top-right corner of each bubble, anchor its center. SMALL_BUBBLES = three more at half size. CAMERA = whole frame.
KEYFRAMES:
- BUBBLE_1/2/3 scale 0% → 105% → 100% in 0.33s [pop], at 0.25s, 0.75s, 1.25s.
- BADGE_n scale 0% → 120% → 100% [pop], 0.25s after its bubble; then pulses 100% → 115% → 100% three times, each gap shorter (0.60s, 0.45s, 0.30s).
- SMALL_BUBBLES scale 0% → 105% → 100% [pop] at 2.50s, 2.75s, 3.00s, filling empty areas.
- CAMERA scale 0.00s 100% → 5.00s 104% [linear].
- 4.00–5.00s: layout stays put (only the slow push continues) so text can be added on top.
VFX: none besides the pops. Forbidden: glow, sparkles, shine, grain, glitch, depth of field, shadows, 3D, camera shake, vignette.
TIMING RATIO: bubbles 30% · badges 30% · crowding 20% · steady 20%.
DIRECTOR NOTE: Customer messages keep popping up and the red dots keep pulsing faster — an inbox overflowing.
SFX (each sound on its keyframe; pitched sounds in A major; strong 0 dB, medium −6 dB, soft −12 dB; no music, voice or animal sounds):
- 0.25s, 0.75s, 1.25s soft notification pings A3, C#4, E4, medium, panned left, right, left
- each badge pop and pulse: tiny UI tick, E6, soft, getting busier
- 2.50s, 2.75s, 3.00s lighter bubbly pops, soft
LOCK: no text, numbers, letters, logos, faces or photos anywhere — bubbles and dots stay empty.
```

Sau đó trong AE: đặt chữ câu hỏi của khách vào trong bong bóng, số đếm lên chấm đỏ (expression ở mục 4 của kịch bản promo).

---

### P13 · Ô nhập kéo dài (nền cho AE) · B · T04 · 4 s

```text
Flat 2D vector UI motion plate for compositing.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: reference image 1 = the OPA style board — match its input bar, round button, outline weight and corner roundness; do not copy its layout. No first or last frame.
FORMAT LOCK: 16:9, full frame, exactly 4 seconds, one continuous shot. Camera locked; no bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #0068FF in every frame — no gradient, texture, vignette, light change, shadows or background objects.
COLOR: plus button, bar and send button #FFFFFF; plus sign and cursor #0068FF. Only these two colors. No grading, tint or color drift.
UNITS: seconds; positions and sizes in % of frame.
LAYERS & ANCHOR POINTS: PLUS = white circle with a thin plus sign, 9% of the frame height, at (22%,50%), anchor its center. BAR = white fully rounded input bar, 9% of the frame height tall, anchor its LEFT edge at the right side of PLUS. CURSOR = thin vertical cursor near the bar's left end. SEND = white circle, 9% of the frame height.
KEYFRAMES:
- PLUS scale: 0.25s 0% → 0.40s 110% → 0.50s 100% [pop].
- BAR width: 0.50s 9% → 0.90s 57% of the frame width, growing to the right only [ease-out 80%]; corners stay fully round.
- CURSOR: blinks every 0.50s from 0.90s to 4.00s, on the beat.
- SEND scale: 3.40s 0% → 3.55s 110% → 3.65s 100% [pop] at (82%,50%).
- From 0.90s, PLUS and BAR stay perfectly still (no drift) so text can be placed later.
VFX: none. Forbidden: glow, shine sweeps, sparkles, grain, glitch, depth of field, shadows, 3D, camera shake, vignette.
TIMING RATIO: build 22% · steady bar 63% · send button 15%.
DIRECTOR NOTE: A clean chat input appears — the plus pops, the bar stretches out from it, the cursor waits for a customer's question, and a send button arrives.
SFX (each sound on its keyframe; pitched sounds in A major; strong 0 dB, medium −6 dB, soft −12 dB; no music, voice or animal sounds):
- 0.25s soft bubbly pop, A5, medium, left
- 0.50–0.90s soft expand swipe, medium, left to center
- 3.40s soft bubbly pop, E5, medium, right
LOCK: no text, letters, numbers or logos anywhere.
```

Sau đó trong AE: gõ "Shop còn size M không ạ?" bằng expression gõ chữ, 0,9–3,4 s, đặt vào thanh. Thanh đứng yên nên không cần tracking.

---

### P14 · Zoom ra thành tường thẻ chat · A1 · K01 · 6 s

```text
Flat 2D vector motion graphics.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first frame only = the blue OPA bull-head logo centered on white (given). No last frame, no reference images.
FORMAT LOCK: 16:9, full frame, exactly 6 seconds, one continuous shot. No bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #FFFFFF in every frame — the pull-back reveals only the cards, never a room, desk, floor, gradient or shadows.
COLOR: cards #FFFFFF with 2px #0068FF outlines; placeholder bars #E6F0FF; avatar logo #0068FF. Only these colors. No grading, tint or color drift.
UNITS: seconds; positions in % of frame; scale in % of the first-frame size.
LAYERS & ANCHOR POINTS: LOGO = the bull-head; it turns out to be the small avatar at the top-left of CARD_MAIN; zoom anchor = LOGO center. CARD_MAIN = white rounded chat card with placeholder bars. WALL = about 20 similar cards in a loose grid on three depth layers.
KEYFRAMES:
- CAMERA scale (zoom-out around LOGO): 0.00s 100% → 1.50s 18% [ease-in-out]; CARD_MAIN appears around the logo as it shrinks.
- WALL: 1.00s → 2.00s cards appear from the edges, 0.05s apart.
- CAMERA pan 1.50s → 6.00s, constant leftward drift: near cards 6%, mid 4%, far 2% of the frame width [linear].
VFX: allowed only — parallax between the three layers. Forbidden: blur on far cards, depth of field, 3D tilt, glow, shine, grain, glitch, shadows, camera shake, vignette.
TIMING RATIO: zoom-out 25% · reveal 8% · parallax drift 67%.
DIRECTOR NOTE: What looked like a logo is OPA's avatar inside one chat; pulling back reveals a whole wall of conversations OPA handles at once, drifting calmly.
SFX (pitched sounds in A major; strong 0 dB, medium −6 dB, soft −12 dB; no music, voice or animal sounds):
- 0.00–1.50s soft airy whoosh, medium, center
- 1.00–2.00s faint layered card slides, soft, spread left and right
- 2.00–6.00s near silence
LOGO LOCK: the bull-head mark only — no "OPA" letters, no wordmark, no text. The avatar logo keeps the exact silhouette of the first frame at every size. No readable text, faces or photos.
```

---

### P15 · Điện thoại trồi lên · B · T03 + T04 · 5 s

```text
Flat 2D vector UI motion plate.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: reference image 1 = the OPA bull-head logo, white on blue — keep it identical wherever it appears; reference image 2 = the OPA style board — match its bubbles, outline weight and corner roundness; do not copy its layout. No first or last frame.
FORMAT LOCK: 16:9, full frame, exactly 5 seconds, one continuous shot. No bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #0068FF in every frame — no gradient, glow, vignette, light change, shadows or background objects.
COLOR: phone body and screen #FFFFFF; customer bubbles #E6F0FF; OPA bubbles #0068FF with a tiny #FFFFFF bull-head avatar. Only these colors. No grading, tint or color drift.
UNITS: seconds; positions in % of frame; scale in %.
LAYERS & ANCHOR POINTS: PHONE = flat white phone outline, 70% of the frame height, final center (50%,52%), anchor bottom-center. MSG_1–4 = empty chat bubbles inside the screen: customer on the left, OPA on the right; anchor at the tip of each tail.
KEYFRAMES:
- PHONE position y: 0.25s y 130% → 1.00s 52% [ease-out 80%]; rotation 0.25s −4° → 1.00s 0°.
- MSG_1 (customer) 1.25s, MSG_2 (OPA) 2.00s, MSG_3 (customer) 2.75s, MSG_4 (OPA) 3.50s: scale 0% → 105% → 100% in 0.30s [pop]; older messages slide up [ease-in-out].
- PHONE stays perfectly still from 3.50s to 5.00s.
VFX: allowed only — light vertical motion blur on PHONE 0.25–1.00s. Forbidden: screen glare, glow, reflections, shadows, 3D tilt, depth of field, grain, glitch, camera shake, vignette.
TIMING RATIO: rise 15% · conversation 55% · steady 30%.
DIRECTOR NOTE: A phone rises and a quick chat plays out — a customer asks, OPA answers right away, twice, on an even rhythm.
SFX (each sound on its keyframe; pitched sounds in A major; strong 0 dB, medium −6 dB, soft −12 dB; no music, voice or animal sounds):
- 0.25–1.00s soft rising swoosh, medium, bottom to center
- 1.25s and 2.75s soft notification ping, A3, medium, left (customer)
- 2.00s and 3.50s soft bubbly pop, E5, medium, right (OPA)
LOGO LOCK: the tiny avatar identical to reference image 1. No readable text, faces, photos or other brand logos.
```

## 9. Prompt sửa có số

Mỗi lượt chỉ đổi **một** thứ. Câu luôn mở đầu bằng:

```text
Keep everything else exactly the same — same format and framing, same background, same colors, same timing and same sound. Only …
```

| Lỗi | Phần sau chữ "Only" |
|---|---|
| Vượt đà quá mạnh | `change HEAD overshoot from 112% to 106%, settling by 1.15s.` |
| Sừng vào trễ | `shift all HORN keyframes 0.25s earlier.` |
| Xoay quanh tâm thay vì đáy | `move the rotation anchor of LOGO to its bottom-center (50%,100% of its box).` |
| Zoom vào sai chỗ | `move the zoom anchor to the center of the inner opening, (50%,56.8%) of the frame.` |
| Logo lệch màu | `fix the logo color to exactly #0068FF in every frame; no tint or grading.` |
| Nền ngả xám, có vignette hay gradient | `fix the background to solid #FFFFFF in every frame; no vignette, gradient or shading.` |
| Nền xuất hiện sàn, phòng, đồ vật | `remove everything behind the logo; the background is plain #FFFFFF only.` |
| Có viền đen hoặc khung bị cắt | `fix the format: full 16:9 frame, no black bars, borders or crop.` |
| Có glow, lấp lánh, bóng đổ | `remove the glow, sparkles and shadows; keep every shape flat.` |
| Motion blur quá nhiều | `reduce motion blur to a light trail during the fastest 0.2s only.` |
| Âm lệch nhịp | `move the wooden tok so it lands exactly at 1.25s, on the horn lock.` |
| Có nhạc hoặc giọng nói | `remove the music and any voice; keep the sound effects.` |
| Âm chói, không cùng giọng | `retune the pops to the notes A4, C#5, E5 (A major).` |
| Logo sai khi dùng ảnh tham chiếu | `make the logo identical to reference image 1: same silhouette, flat color.` |
| Đoạn cuối đứng chết | `add one slow breath on LOGO (100% → 102% → 100%, [sine]) in the last 1.5s.` |

## 10. Kiểm clip ra

Đưa clip vào After Effects. Bật **Info** (Ctrl + 2) và **Rulers** (Ctrl + R).

| Kiểm | Cách | Ngưỡng đạt |
|---|---|---|
| Thời gian | Tua từng khung tới các mốc KEYFRAMES | Lệch ≤ 0,2 s |
| Scale, góc | Solid mỏng làm thước; guide theo bảng 1.3 | Scale ≤ 3 %, góc ≤ 2° |
| Khung đầu, cuối | Đặt khung neo lên trên, blend mode Difference | Đen tuyền |
| Màu logo | Bảng Info, đo ở giữa thân logo | ≈ (0, 104, 255), lệch ≤ 3 mỗi kênh |
| Nền | Đo 4 góc ở 0 s, giữa clip và cuối clip | Đúng một giá trị (255, 255, 255) hoặc (0, 104, 255), không trôi |
| Định dạng | Xem mép khung, đặc biệt khung cuối | Không viền đen, không bị cắt |
| VFX | Tua chậm các đoạn nhanh | Chỉ có VFX trong danh sách được dùng |
| SFX | Bật waveform âm (phím L L), so điểm đánh với mốc keyframe | Lệch ≤ 1 khung; không nhạc, không giọng |

Lệch quá ngưỡng thì dùng đúng một câu ở mục 9 rồi tạo lại. Âm Omni dù đạt vẫn thay bằng file thư viện (bảng 4.2) khi dựng phim.

## 11. Ghép thành promo

| Promo | Prompt |
|---|---|
| C1 (0–4 s) | P12 làm nền + chữ, số AE |
| C2 (4–8 s) | P13 làm nền + chữ AE |
| C3 (8–14 s) | AE hoàn toàn; P15 làm nền thay thế |
| C4 (14–20 s) | P10 |
| C5 (20–26 s) | P08 bản 6 s |
| C6 (26–32 s) | P09 + chữ, nút CTA AE |
| Nối nền trắng ↔ xanh | P11 hoặc khối quét làm bằng AE |

<!-- ===== /file: omni-flash-motion-director/references/PROMPT-PACK-OMNI-FLASH.md ===== -->

<!-- ===== file: omni-flash-motion-director/references/QUY-TRINH-SAN-XUAT-VA-PROMPT-TU-ANH-OMNI-FLASH.md ===== -->

# QUY TRÌNH SẢN XUẤT VIDEO MOTION GRAPHICS & BỘ PROMPT NHẬN DIỆN ẢNH TRÊN GOOGLE OMNI FLASH (KỊCH BẢN SỐ 1 - ADS #1)

> **Dự án**: `VIDEO 01 · Ads #1 (Flagship 36s)` — **TỔNG QUAN OPA AGENT: TỰ TRẢ LỜI KHÁCH, CHỐT ĐƠN THẲNG VÀO PANCAKE POS**  
> **Thư mục Hình ảnh & Storyboard**: [/media/vmiz/Over Powers/THÀNH V/Motion Omi/ẢNH](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH)  
> **Thư mục Tài nguyên (SFX, BGM, Fonts, Mascot Gốc)**: [/media/vmiz/Over Powers/THÀNH V/Motion Omi/ASSETS](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS)  
> **Bảng Storyboard Tương Tác (Mở trên trình duyệt)**: [STORYBOARD-SAN-XUAT-VIDEO-01.html](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/STORYBOARD-SAN-XUAT-VIDEO-01.html)

---

## BƯỚC 1: TIẾP NHẬN Ý TƯỞNG, BRIEF & PHÂN RÃ KỊCH BẢN CHI TIẾT THEO BLOCK 5 GIÂY

### 1.1. Tóm tắt Brief & Mục tiêu Chuyển đổi
* **Nỗi đau cốt lõi (Pain Point)**: Chủ shop dùng Pancake quản lý nhiều trang bán hàng, mỗi ngày mất hàng tiếng đồng hồ để trả lời lặp đi lặp lại các câu hỏi giống nhau (*giá, size, tồn kho*) và phải copy-paste từng số điện thoại, địa chỉ để nhập tay đơn hàng vào Pancake POS.
* **Thông điệp anh hùng (Hero Message)**: *"OPA lo phần trả lời, shop lo phần bán"* — Kết nối thẳng vào Pancake & Pancake POS chỉ trong 1 lần bấm, không cần tạo App Facebook phức tạp.
* **Nhịp điệu & Phong cách (Pacing & Look)**:
  * Nhịp chuẩn: **120 BPM** (`1 phách = 0.50s = 15 frames @ 30fps`; `nửa phách = 0.25s`).
  * Phong cách kết hợp: **2D Vector Character** (Chủ shop ở Cảnh 1 & Cảnh 4 giống cấu trúc *SMIT - Ads Check Pro*) + **2.5D SaaS UI Motion & Mascot Bò OPA** (Cảnh 2, 3A, 3B, 5 giống project After Effects `template 5.aep` / `Final_4k (3840 x 2160)` và [o ping.mp4](file:///media/vmiz/Over%20Powers/EDIT%20ADOBE/videointro/Final_4k%20(3840%20x%202160)/o%20ping.mp4)).

### 1.2. Chia 36 Giây Kịch Bản Số 1 thành 6 Đoạn Timeline (Mỗi đoạn 1 Bộ Ảnh 5s = 5 Nhịp Motion + 4 Ảnh Thành Phần)

| Mã Đoạn | Timecode | Thời lượng | Vai trò Kịch bản | Thư mục Ảnh tương ứng trong `/media/vmiz/Over Powers/THÀNH V/Motion Omi/ẢNH` |
| :--- | :--- | :--- | :--- | :--- |
| **Đoạn 01** | `00:00 – 00:05` | `5.0s` | **Hook**: Chủ shop ngồi quay lưng quá tải, đồng hồ quay vù vù 3 vòng, 8 bong bóng tin nhắn nổ dồn dập | [SCENE_01_00s-05s_HOOK_QUA_TAI](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_01_00s-05s_HOOK_QUA_TAI) |
| **Đoạn 02** | `00:05 – 00:11` | `6.0s` *(Block 5s)* | **Xoáy sâu nỗi đau**: Hộp thư Pancake nhấp nháy chờ rep (`99+`), 3 nỗi đau trượt ra, nhập tay POS thủ công | [SCENE_02_05s-11s_XOAY_SAU_NOI_DAU](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_02_05s-11s_XOAY_SAU_NOI_DAU) |
| **Đoạn 03A** | `00:11 – 00:16` | `5.0s` | **Giải pháp Phần 1**: Chuyển cảnh bừng sáng (`Whoosh`), Bò OPA húc mở màn, Khung Chat 3D (`05_Scene`) xoay phẳng & tự chốt đơn POS `#PK8921` | [SCENE_03A_11s-16s_BO_OPA_VA_CHAT_3D](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_03A_11s-16s_BO_OPA_VA_CHAT_3D) |
| **Đoạn 03B** | `00:16 – 00:22` | `6.0s` *(Block 5s)* | **Giải pháp Phần 2 (Split-Screen)**: Trái giữ khung Chat + POS; Phải nảy 5 Pill tính năng (`05_Scene_Button02`) theo nhịp 120 BPM + Khung sáng `H15` quét dọc | [SCENE_03B_16s-22s_SPLIT_SCREEN_5_PILLS](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_03B_16s-22s_SPLIT_SCREEN_5_PILLS) |
| **Đoạn 04** | `00:22 – 00:30` | `8.0s` *(Block 5s)* | **Giải phóng sức lao động (Relief)**: Chủ shop mỉm cười thảnh thơi dang rộng 2 tay; 3 khung thoại gạch bỏ thao tác cực nhọc -> nổ 3 dấu tích xanh ✅ | [SCENE_04_22s-30s_GIAI_PHONG_SUC_LAO_DONG](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_04_22s-30s_GIAI_PHONG_SUC_LAO_DONG) |
| **Đoạn 05** | `00:30 – 00:36` | `6.0s` *(Block 5s)* | **Outro & CTA**: Bò OPA bung mở từ đáy `U_HEAD` -> trượt sang trái ghép chữ `OPA`, nút CTA xanh nở ngang + chuột lướt tới Click tạo sóng Ripple | [SCENE_05_30s-36s_OUTRO_CTA_LOCKUP](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_05_30s-36s_OUTRO_CTA_LOCKUP) |

---

## BƯỚC 2: HỆ THỐNG SFX, NHẠC NỀN (BGM), FONT TEXT & TEXT VFX ĐÃ TUYỂN CHỌN VÀO `ASSETS`

Toàn bộ 57 file âm thanh, font chữ và vector gốc đã được lọc và chép vào [/media/vmiz/Over Powers/THÀNH V/Motion Omi/ASSETS](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS):

### 2.1. Hệ thống Font chữ & Text VFX (Chuẩn `BRAND-SPEC.md` & `template 5.aep`)
1. **Font Tiêu đề & UI chính**: [BeVietnamPro-ExtraBold.ttf](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/FONTS/BeVietnamPro-ExtraBold.ttf) (`ExtraBold 800`) — Hiển thị sắc nét dấu chồng tiếng Việt (`Ầ, Ổ, Ữ, Đ`), line-height `1.32`.
2. **Font Nội dung Chat & POS**: [BeVietnamPro-Medium.ttf](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/FONTS/BeVietnamPro-Medium.ttf) (`Medium 500`).
3. **Font Cụm Nhấn Thương Hiệu**: [FrauncesOPA-ExtraBoldItalic.ttf](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/FONTS/FrauncesOPA-ExtraBoldItalic.ttf) (`Fraunces Italic 800`) — Đi kèm hiệu ứng **Khối đánh dấu quét ngang dưới chữ (`Accent Mark Sweep`)**.
4. **4 Hiệu ứng Text VFX đưa vào After Effects & Prompt**:
   * **Text VFX #1 — `Alpha Track-Matte Slide Up` (Rule R1)**: Chữ trượt từ dưới hộp mặt nạ vô hình lên (`ΔY = +120px -> 0px`, `16 frames`), đồ thị vận tốc `Out Influence 75.2% / In Influence 75.1%`.
   * **Text VFX #2 — `Horizontal Motion-Blur Word Swap` (H02/H04 từ `o ping.mp4`)**: Dòng chữ tiêu đề trượt ngang tốc độ cao kèm `Directional Blur` rồi phanh gấp êm ái.
   * **Text VFX #3 — `Auto-Width Dynamic Pill` (`sourceRectAtTime`)**: Khung viên thuốc `05_Scene_Button02` tự động nở rộng khớp chiều dài câu tiếng Việt với `Out Influence 15.2% / In Influence 100%` (Rule R10).
   * **Text VFX #4 — `Number Counter Roll` (`Slider Control`)**: Huy hiệu đỏ đếm tăng tốc từ `12+ -> 99+` (Scene 2) và giá tiền `159.000đ` / mã đơn `#PK8921` (Scene 3A).

### 2.2. Nhạc nền (BGM) & Bảng Cue Sheet SFX (48kHz, Chuẩn `-14 LUFS` Mạng Xã Hội)
* **Nhạc nền 120 BPM (`0.50s / beat`)**:
  * [nhac-nen-opa-agent.wav](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/BGM/nhac-nen-opa-agent.wav)
  * [bgm-120bpm-opa-v2.wav](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/BGM/bgm-120bpm-opa-v2.wav)
* **Bảng Gắn SFX Theo Từng Mốc Chuyển Động (Trễ `+1 frame` = `16.7ms` sau điểm va chạm hình ảnh)**:

| Cảnh & Mốc Giây | Chuyển động trên hình | File SFX trong `/media/vmiz/Over Powers/THÀNH V/Motion Omi/ASSETS/SFX` | Cao độ / Mức âm chuẩn |
| :--- | :--- | :--- | :--- |
| **Scene 1** (`00:00–00:05`) | Kim đồng hồ quay vù vù 3 vòng (`0° -> +1080°`) | [fast-forward-whirr-sweep.wav](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/SFX/fast-forward-whirr-sweep.wav) | `-2 LU` so với nhạc nền |
| **Scene 1** (`00:25–04:25`) | 8 bong bóng tin nhắn nổ liên hoàn mỗi `0.25s` | [pop-bubble-low-A4.wav](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/SFX/pop-bubble-low-A4.wav) -> [pop-bubble-mid-C#5.wav](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/SFX/pop-bubble-mid-C%235.wav) -> [pop-bubble-high-E5.wav](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/SFX/pop-bubble-high-E5.wav) | Tăng dần cao độ `A4 -> C#5 -> E5` tạo cảm giác dồn dập |
| **Scene 2** (`05:00–11:00`) | Dòng chat mới nhảy bậc mỗi `0.50s` + Huy hiệu đỏ `99+` | [ui-soft-ping-night.wav](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/SFX/ui-soft-ping-night.wav) + [ui-alert-soft-low.wav](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/SFX/ui-alert-soft-low.wav) | `+3 dB` trong dải `150–2000 Hz` |
| **Scene 2** (`06:25–10:00`) | Gõ phím copy-paste thủ công vào bảng POS | [uisfx-minimal-typing.wav](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/SFX/uisfx-minimal-typing.wav) | `-4 LU` so với nhạc nền |
| **Scene 3A** (`11:00–11:75`) | Chuyển cảnh Whoosh sáng xanh + Bò OPA húc (`Charge`) | [whoosh-cut-fast.wav](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/SFX/whoosh-cut-fast.wav) + [foley-snort-puff.wav](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/SFX/foley-snort-puff.wav) | `+0 LU` ngang nhạc nền |
| **Scene 3A** (`11:40–15:50`) | Khung Chat 3D `05_Scene` xoay khớp vị trí & Đẩy đơn POS `#PK8921` | [ui-card-snap-dock.wav](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/SFX/ui-card-snap-dock.wav) + [uisfx-minimal-success+200c.wav](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/SFX/uisfx-minimal-success%2B200c.wav) | `+4 dB` trong dải `800–6000 Hz` |
| **Scene 3B** (`16:50–19:00`) | 5 Pill tính năng nảy ra cách nhau `0.50s` + Khung sáng `H15` quét | [ui-wood-marimba-tick.wav](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/SFX/ui-wood-marimba-tick.wav) + [ui-swish-accent-tick.wav](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/SFX/ui-swish-accent-tick.wav) | Chuỗi nốt `A5 -> C#6 -> E6` |
| **Scene 4** (`23:25–27:50`) | Gạch bỏ 3 thao tác thủ công -> Nổ 3 dấu tích xanh ✅ | [catch-bright-ring.wav](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/SFX/catch-bright-ring.wav) + [uisfx-glass-expand+155c.wav](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/SFX/uisfx-glass-expand%2B155c.wav) | `+2 dB` trong dải `800–6000 Hz` |
| **Scene 5** (`30:25–36:00`) | Bò OPA bung mở -> Trỏ chuột Click nút CTA -> Âm kết Logo | [click-chuot.wav](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/SFX/click-chuot.wav) + [opa-sonic-logo-c.wav](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/SFX/opa-sonic-logo-c.wav) + [sonic-logo-brass-chord.wav](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ASSETS/SFX/sonic-logo-brass-chord.wav) | Sonic Logo `+2 dB` để nổi rõ trên loa điện thoại |

---

## BƯỚC 3: QUY TRÌNH TẠO CHARACTER & RIG SHEET ĐỂ MODEL AI ĐỌC THÔNG TIN ẢNH

Toàn bộ các bảng Character & Rig Sheet đã được xuất vào [/media/vmiz/Over Powers/THÀNH V/Motion Omi/ẢNH/00_CHARACTER_SHEET_BO_OPA](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/00_CHARACTER_SHEET_BO_OPA):

1. **[CS01_BO_OPA_CHARACTER_RIG_SHEET.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/00_CHARACTER_SHEET_BO_OPA/CS01_BO_OPA_CHARACTER_RIG_SHEET.png)**:
   * **Mục đích**: Dành cho Đạo diễn, Editor After Effects và Model AI hiểu rõ cấu tạo cơ học 4 phần của **Bò OPA (`V4 · A · O Core`)**:
     * `(a) a-horn-left`: Sừng trái — xoay quanh điểm neo **A2 `[22.6%, 42.1%]`** (`[569.16, 901.07]` trên hệ 2000px).
     * `(b) b-horn-right`: Sừng phải — xoay quanh điểm neo **A3 `[77.4%, 42.1%]`** (`[1430.84, 901.07]`).
     * `(c) c-muzzle`: Thân chữ U bo tròn đồng tâm (`R = 2t, r = t`) — phóng to và nghiêng quanh điểm neo **A1 `[50%, 100%]`** (đáy giữa chữ U).
     * `(d) d-nostril-gap`: Khe trán rộng `g = 122.755u` — điểm phát 2 cụm hạt xanh khi thở phì (`Snort Puff`).
   * **5 Key Poses chuẩn hóa**: `Pose 1: Reveal Spring Pop` -> `Pose 2: Idle Breathing` -> `Pose 3: Charge Anticipation (-8°)` -> `Pose 4: Charge Lunge (+6°)` -> `Pose 5: Lockup & Snort Puff`.
2. **[CS02_REF_BO_OPA_XANH_NEN_TRANG.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/00_CHARACTER_SHEET_BO_OPA/CS02_REF_BO_OPA_XANH_NEN_TRANG.png)** & **[CS03_REF_BO_OPA_TRANG_NEN_XANH.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/00_CHARACTER_SHEET_BO_OPA/CS03_REF_BO_OPA_TRANG_NEN_XANH.png)**:
   * Hai ảnh tham chiếu sạch tuyệt đối (không chữ, không đường gióng) để đính kèm vào ô **Style / Character Reference** trên Google Omni Flash.
3. **[CS04_COMPONENT_3_BO_PHAN_BO_OPA_SACH.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/00_CHARACTER_SHEET_BO_OPA/CS04_COMPONENT_3_BO_PHAN_BO_OPA_SACH.png)**:
   * Ảnh tách rời 3 thành phần (`Sừng trái` + `Thân chữ U` + `Sừng phải`) để AI nhận diện các khớp nối khi tạo chuyển động bung logo.
4. **[CS05_CHU_SHOP_CHARACTER_SHEET.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/00_CHARACTER_SHEET_BO_OPA/CS05_CHU_SHOP_CHARACTER_SHEET.png)**:
   * Bảng đối chiếu sự đồng nhất của nhân vật Chủ Shop giữa **Scene 1 (Đêm muộn quá tải)** và **Scene 4 (Ban ngày thảnh thơi dang rộng 2 tay)**.

---

## BƯỚC 4: HỆ THỐNG STORYBOARD SẢN XUẤT & CẤU TRÚC ẢNH TRONG MỖI ĐOẠN 5 GIÂY

### 4.1. Bộ Storyboard Đạo Diễn (`00_STORYBOARD_SAN_XUAT`)
Tại thư mục [/media/vmiz/Over Powers/THÀNH V/Motion Omi/ẢNH/00_STORYBOARD_SAN_XUAT](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/00_STORYBOARD_SAN_XUAT), hệ thống đã tạo 4 bảng Storyboard lớn:
* **[SB00_MASTER_DIRECTOR_STORYBOARD_30_FRAMES.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/00_STORYBOARD_SAN_XUAT/SB00_MASTER_DIRECTOR_STORYBOARD_30_FRAMES.png)**: Bảng tổng覽 toàn bộ **30 khung hình chuyển động (6 phân cảnh × 5 bước motion)** từ `00:00` đến `00:36`, kèm cột kịch bản `VO`, `TOS`, `SFX`, `Camera & AE Keyframes`.
* **[SB01_STORYBOARD_PHAN_1_HOOK_VA_NOI_DAU.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/00_STORYBOARD_SAN_XUAT/SB01_STORYBOARD_PHAN_1_HOOK_VA_NOI_DAU.png)**: Storyboard chi tiết **Scene 01 & Scene 02** có vẽ trực tiếp **Mũi tên Vector Chuyển động (`Motion Arrows`)** và danh sách **Ảnh Thành Phần (`Components`)**.
* **[SB02_STORYBOARD_PHAN_2_GIAI_PHAP_BO_OPA_CHAT_3D_5_PILLS.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/00_STORYBOARD_SAN_XUAT/SB02_STORYBOARD_PHAN_2_GIAI_PHAP_BO_OPA_CHAT_3D_5_PILLS.png)**: Storyboard chi tiết **Scene 03A & Scene 03B**.
* **[SB03_STORYBOARD_PHAN_3_GIAI_PHONG_VA_OUTRO_CTA.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/00_STORYBOARD_SAN_XUAT/SB03_STORYBOARD_PHAN_3_GIAI_PHONG_VA_OUTRO_CTA.png)**: Storyboard chi tiết **Scene 04 & Scene 05**.

### 4.2. Quy ước Đánh Dấu & Phân Loại 11 File Ảnh trong MỖI Thư Mục Đoạn 5 Giây
Trong mỗi thư mục phân cảnh (`SCENE_01` đến `SCENE_05`), có đúng **11 file ảnh** được chuẩn hóa mã tên để cả người dựng lẫn Model AI phân biệt rõ **Ảnh Bao Quát**, **Frame Đầu**, **Bước Motion Trung Gian**, **Ảnh Thành Phần** và **Frame Cuối**:

| Mã File trong từng thư mục Scene | Phân loại Vai trò | Công dụng khi đưa vào Google Omni Flash & After Effects |
| :--- | :--- | :--- |
| `00_MASTER_BAO_QUAT_5s.png` | **[ẢNH BAO QUÁT 5 GIÂY]** | Tấm ảnh tổng hợp toàn bộ 5 nhịp chuyển động trong 5s (`F01 -> M02 -> M03 -> M04 -> F05`) + 4 ảnh thành phần + bảng thông số Keyframe AE. |
| `F01_FIRST_FRAME_t0.0s.png` | **[FRAME ĐẦU — 0.00s]** | Ảnh 16:9 sạch ở giây `0.00s` -> Nạp vào ô **First Frame (Khung hình đầu)** trên Google Omni Flash. |
| `M02_MOTION_STEP_t1.25s.png` | **[BƯỚC MOTION 2/5 — 1.25s]** | Thể hiện trạng thái chuyển động ở giây `1.25s` (bắt đầu gia tốc/nảy). |
| `M03_MOTION_STEP_t2.50s.png` | **[BƯỚC MOTION 3/5 — 2.50s]** | Thể hiện trạng thái chuyển động ở giữa clip `2.50s` (cao trào chuyển động). |
| `M04_MOTION_STEP_t3.75s.png` | **[BƯỚC MOTION 4/5 — 3.75s]** | Thể hiện trạng thái chuyển động ở giây `3.75s` (giảm chấn lò xo / gần hoàn tất). |
| `F05_LAST_FRAME_t5.0s.png` | **[FRAME CUỐI / ẢNH ĐÍCH — 5.00s]** | Ảnh 16:9 sạch hoàn chỉnh ở giây `5.00s` -> Nạp vào ô **Last Frame (Khung hình cuối)** trên Google Omni Flash để khóa bố cục đích. |
| `F05_LAST_FRAME_CO_CHU_AE.png` | **[BẢN ĐỐI CHIẾU CHỮ AE 4K]** | Ảnh Frame cuối đã gắn đầy đủ chữ tiếng Việt chuẩn `Be Vietnam Pro` để Editor căn vị trí chữ trong After Effects. |
| `C01_COMPONENT_*.png` .. `C04_COMPONENT_*.png` | **[4 ẢNH THÀNH PHẦN TÁCH LẺ]** | Tách riêng từng vật thể con trong ảnh bao quát (Đồng hồ, Bong bóng chat, Huy hiệu đỏ, Bò OPA, Khung Chat 3D, 5 Pills, Nút CTA, Trỏ chuột) -> Nạp vào ô **Ingredients / Reference Images** trên Omni Flash. |

---

## BƯỚC 5: BỘ PROMPT CHUYỂN ĐỘNG TẠO VIDEO CHO TỪNG ĐOẠN 5 GIÂY TRÊN GOOGLE OMNI FLASH (CÓ NHẬN DIỆN `FIRST FRAME`, `COMPONENTS`, `MOTION STEPS`, `LAST FRAME`)

> **Cách thao tác trên Google Omni Flash (Google Flow)**:
> Với mỗi đoạn 5 giây bên dưới:
> 1. Đính kèm **`F01_FIRST_FRAME_t0.0s.png`** làm **First Frame (Ảnh #1 / Start Frame)**.
> 2. Đính kèm **`F05_LAST_FRAME_t5.0s.png`** làm **Last Frame (Ảnh #2 / End Frame — đồng thời là Ảnh Bao Quát Đích)**.
> 3. Đính kèm các ảnh **`C01..C04_COMPONENT_*.png`** (hoặc `00_MASTER_BAO_QUAT_5s.png` nếu dùng chế độ Multi-Image Reference) làm **Component Ingredients (Ảnh thành phần)**.
> 4. Dán **Prompt Chuyển Động** tương ứng bên dưới (prompt đã được thiết kế để AI nhận diện rõ đâu là Frame đầu, đâu là các Ảnh thành phần, và cách các Ảnh thành phần di chuyển qua các bước `M02 -> M03 -> M04` để hội tụ thành Frame cuối `F05`).

---

### 🎬 ĐOẠN 01 (`00:00 – 00:05` | 5.0s): HOOK — CHỦ SHOP QUÁ TẢI & ĐỒNG HỒ QUAY + BÃO TIN NHẮN

* **Thư mục ảnh**: [/media/vmiz/Over Powers/THÀNH V/Motion Omi/ẢNH/SCENE_01_00s-05s_HOOK_QUA_TAI](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_01_00s-05s_HOOK_QUA_TAI)
* **Khai báo Ảnh nạp vào Omni Flash**:
  * **First Frame (Ảnh mở đầu `0.0s`)**: [F01_FIRST_FRAME_t0.0s.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_01_00s-05s_HOOK_QUA_TAI/F01_FIRST_FRAME_t0.0s.png)
  * **Last Frame / Ảnh Bao Quát Đích (`5.0s`)**: [F05_LAST_FRAME_t5.0s.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_01_00s-05s_HOOK_QUA_TAI/F05_LAST_FRAME_t5.0s.png)
  * **Các Ảnh Thành Phần (`Components`)**:
    * `Component 1`: [C01_COMPONENT_DONG_HO_QUAY_NHANH.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_01_00s-05s_HOOK_QUA_TAI/C01_COMPONENT_DONG_HO_QUAY_NHANH.png) (Đồng hồ treo tường)
    * `Component 2`: [C02_COMPONENT_BONG_BONG_MESSENGER.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_01_00s-05s_HOOK_QUA_TAI/C02_COMPONENT_BONG_BONG_MESSENGER.png) (Bong bóng chat xanh đuôi trái)
    * `Component 3`: [C03_COMPONENT_BONG_BONG_PANCAKE.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_01_00s-05s_HOOK_QUA_TAI/C03_COMPONENT_BONG_BONG_PANCAKE.png) (Bong bóng chat cam đuôi phải)
    * `Component 4`: [C04_COMPONENT_HUY_HIEU_CANH_BAO_DO.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_01_00s-05s_HOOK_QUA_TAI/C04_COMPONENT_HUY_HIEU_CANH_BAO_DO.png) (Huy hiệu cảnh báo đỏ)

#### 📋 Prompt Chuyển Động Đoạn 01 (Copy dán vào Google Omni Flash):
```text
Everything below is invisible camera and animation control data. Never draw any labels, numbers, percentages, coordinates, arrows, or text onto the video frames.

[IMAGE REFERENCE & FRAME IDENTIFICATION]
- FIRST FRAME LOCK (`t = 0.00s`): Use `F01_FIRST_FRAME_t0.0s.png` as the exact starting frame (the shop owner sitting from behind at the laptop desk at night, wall clock at upper-right `(76%, 26%)` at 12:10, zero chat bubbles around the laptop).
- LAST FRAME / MASTER TARGET LOCK (`t = 5.00s`): Use `F05_LAST_FRAME_t5.0s.png` as the exact ending composition (all 8 blue and orange chat bubbles and the red alert badge surrounding the laptop, glowing red-rimmed wall clock, slightly closer camera framing).
- COMPONENT INGREDIENTS IDENTIFICATION:
  * Component `C01` (Wall Clock): Located at `(76%, 26%)`. Its minute and hour hands pivot strictly around the center pin of the clock dial.
  * Component `C02` (Blue Messenger Bubble) & Component `C03` (Orange Pancake Bubble): Individual notification bubbles that must pop in sequentially around the laptop, each scaling from its bottom speech-tail corner.
  * Component `C04` (Red Alert Pill Badge): Pops in above the laptop screen at `(56%, 51%)` from its center anchor.

[5-SECOND MOTION PROGRESSION (FROM FIRST FRAME TO LAST FRAME)]
- Step 1 (`0.00s -> 1.25s`, matching `F01 -> M02`):
  The master camera begins a continuous slow push-in (`Scale 100% -> 106%` over 5s). On the upper-right wall clock (`C01`), the minute hand accelerates clockwise (`Rotation 0 deg -> +270 deg`) while the first 2 chat bubbles (`C02` on the left, `C03` on the right) spring out from their tail-corner anchor points (`Scale 0% -> 108% overshoot -> 100%`, `Rotation -6 deg -> +2 deg -> 0 deg`).
- Step 2 (`1.25s -> 2.50s`, matching `M02 -> M03`):
  The clock hands spin faster (`+270 deg -> +540 deg`) and the clock rim begins pulsing with a stressed red glow. Bubbles #3 and #4 pop in on the half-beat (`0.25s` stagger) above the first pair with the same crisp `0% -> 108% -> 100%` spring.
- Step 3 (`2.50s -> 3.75s`, matching `M03 -> M04`):
  The clock completes another revolution (`+540 deg -> +810 deg`). Bubbles #5 and #6 pop in higher around the monitor, and the red alert badge (`C04`) springs open right above the laptop (`Scale 0% -> 115% -> 95% -> 100%`). The shop owner's head tilts slightly (`-5 deg -> +4 deg`) with exhausted shoulder slump as the room ambient light darkens.
- Step 4 (`3.75s -> 5.00s`, matching `M04 -> F05_LAST_FRAME`):
  The final bubbles #7 and #8 pop into place, completing the exact 8-bubble cluster and clock position of `F05_LAST_FRAME_t5.0s.png`. Keep the top 20% header zone completely clean dark-slate space. No text or numbers on screen.
```

---

### 🎬 ĐOẠN 02 (`00:05 – 00:11` | 6.0s / Block 5s): XOÁY SÂU NỖI ĐAU — HỘP THƯ QUÁ TẢI & NHẬP POS TAY

* **Thư mục ảnh**: [/media/vmiz/Over Powers/THÀNH V/Motion Omi/ẢNH/SCENE_02_05s-11s_XOAY_SAU_NOI_DAU](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_02_05s-11s_XOAY_SAU_NOI_DAU)
* **Khai báo Ảnh nạp vào Omni Flash**:
  * **First Frame (`0.0s`)**: [F01_FIRST_FRAME_t0.0s.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_02_05s-11s_XOAY_SAU_NOI_DAU/F01_FIRST_FRAME_t0.0s.png)
  * **Last Frame / Ảnh Bao Quát Đích (`5.0s`)**: [F05_LAST_FRAME_t5.0s.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_02_05s-11s_XOAY_SAU_NOI_DAU/F05_LAST_FRAME_t5.0s.png)
  * **Các Ảnh Thành Phần (`Components`)**:
    * `Component 1`: [C01_COMPONENT_HANG_TIN_NHAN_CHO_REP.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_02_05s-11s_XOAY_SAU_NOI_DAU/C01_COMPONENT_HANG_TIN_NHAN_CHO_REP.png) (Dòng hội thoại khách chờ rep)
    * `Component 2`: [C02_COMPONENT_HUY_HIEU_99_PLUS.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_02_05s-11s_XOAY_SAU_NOI_DAU/C02_COMPONENT_HUY_HIEU_99_PLUS.png) (Huy hiệu cảnh báo đỏ góc hộp thư)
    * `Component 3`: [C03_COMPONENT_BANG_NHAP_POS_THU_CONG.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_02_05s-11s_XOAY_SAU_NOI_DAU/C03_COMPONENT_BANG_NHAP_POS_THU_CONG.png) (Bảng nhập đơn POS thủ công)
    * `Component 4`: [C04_COMPONENT_THANH_NOI_DAU_GLASS.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_02_05s-11s_XOAY_SAU_NOI_DAU/C04_COMPONENT_THANH_NOI_DAU_GLASS.png) (Thanh Glass Pill nỗi đau)

#### 📋 Prompt Chuyển Động Đoạn 02 (Copy dán vào Google Omni Flash):
```text
Everything below is invisible camera and animation control data. Never draw any labels, numbers, percentages, coordinates, arrows, or text onto the video frames.

[IMAGE REFERENCE & FRAME IDENTIFICATION]
- FIRST FRAME LOCK (`t = 0.00s`): Use `F01_FIRST_FRAME_t0.0s.png` as the starting frame (left dark-mode inbox window with only 3 chat rows, right column empty).
- LAST FRAME / MASTER TARGET LOCK (`t = 5.00s`): Use `F05_LAST_FRAME_t5.0s.png` as the final target frame (left inbox filled with 6 urgent unread chat rows + glowing red alert badge at top-right of inbox; right column showing 3 stacked dark-glass pain-point pills on top and the manual POS entry form with a blinking red cursor below, surrounded by a darkened late-night vignette).
- COMPONENT INGREDIENTS IDENTIFICATION:
  * Component `C01` (Unread Chat Row): Stacks vertically inside the left inbox panel (`x: 5% to 45%`), step-scrolling downward as new rows pop in from their left avatar anchor.
  * Component `C02` (Red Notification Badge): Anchored at the top-right corner of the left inbox window `(43%, 13%)`.
  * Component `C03` (Manual POS Form Card): Anchored at its top-left corner `(54%, 43%)` in the lower-right quadrant.
  * Component `C04` (Dark-Glass Pain Pill): Three horizontal pill banners that slide into the upper-right quadrant at `y = 16%, 25%, 34%`.

[5-SECOND MOTION PROGRESSION (FROM FIRST FRAME TO LAST FRAME)]
- Step 1 (`0.00s -> 1.25s`, matching `F01 -> M02`):
  Inside the left inbox window, the existing rows step-scroll down by one row height (`cubic-bezier(0.2, 0, 0.1, 1)`) as a 4th unread chat row (`C01`) pops in at the top (`Scale 0% -> 108% -> 100%`). Simultaneously, the red notification badge (`C02`) springs open at the top-right corner of the inbox (`Scale 0% -> 115% -> 95% -> 100%`), the first dark-glass pill (`C04`) slides in at upper-right (`Position X +8% -> 0%`), and the manual POS form (`C03`) begins wiping open diagonally from its top-left anchor to 45% size.
- Step 2 (`1.25s -> 2.50s`, matching `M02 -> M03`):
  A 5th unread chat row (`C01`) step-scrolls into the left inbox, the second dark-glass pill (`C04`) slides into place at `y = 25%`, and the manual POS form (`C03`) finishes expanding to 85%–100% with fast-out, long-settle easing (`Out Influence 15.2%, In Influence 100%`).
- Step 3 (`2.50s -> 3.75s`, matching `M03 -> M04`):
  A 6th unread chat row (`C01`) fills the left inbox while the red badge (`C02`) shakes (`Rotation -6 deg -> +6 deg -> 0 deg`). The third dark-glass pill (`C04`) locks into `y = 34%`, and inside the manual POS form (`C03`), a red bar and blinking cursor tediously type inside the third input field.
- Step 4 (`3.75s -> 5.00s`, matching `M04 -> F05_LAST_FRAME`):
  The surrounding midnight-blue workspace darkens around the edges (vignette opacity `0% -> 65%`) while all elements settle into the exact layout of `F05_LAST_FRAME_t5.0s.png`. Render clean geometric UI shapes and bars only—no text or numbers.
```

---

### 🎬 ĐOẠN 03A (`00:11 – 00:16` | 5.0s): GIẢI PHÁP PHẦN 1 — BÒ OPA HÚC MỞ MÀN & KHUNG CHAT 3D (`05_Scene`) TỰ CHỐT ĐƠN

* **Thư mục ảnh**: [/media/vmiz/Over Powers/THÀNH V/Motion Omi/ẢNH/SCENE_03A_11s-16s_BO_OPA_VA_CHAT_3D](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_03A_11s-16s_BO_OPA_VA_CHAT_3D)
* **Khai báo Ảnh nạp vào Omni Flash**:
  * **First Frame (`0.0s`)**: [F01_FIRST_FRAME_t0.0s.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_03A_11s-16s_BO_OPA_VA_CHAT_3D/F01_FIRST_FRAME_t0.0s.png)
  * **Last Frame / Ảnh Bao Quát Đích (`5.0s`)**: [F05_LAST_FRAME_t5.0s.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_03A_11s-16s_BO_OPA_VA_CHAT_3D/F05_LAST_FRAME_t5.0s.png)
  * **Các Ảnh Thành Phần (`Components`)**:
    * `Component 1`: [C01_COMPONENT_BO_OPA_CHARGE.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_03A_11s-16s_BO_OPA_VA_CHAT_3D/C01_COMPONENT_BO_OPA_CHARGE.png) (Bò OPA tư thế húc Charge)
    * `Component 2`: [C02_COMPONENT_KHUNG_CHAT_3D_05_SCENE.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_03A_11s-16s_BO_OPA_VA_CHAT_3D/C02_COMPONENT_KHUNG_CHAT_3D_05_SCENE.png) (Khung thẻ trắng 3D `05_Scene` có viền xanh `EdgeGlow`)
    * `Component 3`: [C03_COMPONENT_BA_CHAM_TYPING.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_03A_11s-16s_BO_OPA_VA_CHAT_3D/C03_COMPONENT_BA_CHAM_TYPING.png) (Bong bóng 3 chấm Typing)
    * `Component 4`: [C04_COMPONENT_THE_CHOT_DON_POS_XANH.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_03A_11s-16s_BO_OPA_VA_CHAT_3D/C04_COMPONENT_THE_CHOT_DON_POS_XANH.png) (Thẻ tự động tạo đơn Pancake POS màu xanh lá)

#### 📋 Prompt Chuyển Động Đoạn 03A (Copy dán vào Google Omni Flash):
```text
Everything below is invisible camera and animation control data. Never draw any labels, numbers, percentages, coordinates, arrows, or text onto the video frames.

[IMAGE REFERENCE & FRAME IDENTIFICATION]
- FIRST FRAME LOCK (`t = 0.00s`): Use `F01_FIRST_FRAME_t0.0s.png` as the starting frame (a bright royal-blue light-sweep wave across the left half of the screen with the flat white geometric OPA Bull Mark tilting back `-8 deg` in anticipation).
- LAST FRAME / MASTER TARGET LOCK (`t = 5.00s`): Use `F05_LAST_FRAME_t5.0s.png` as the exact ending frame (the white OPA Bull Mark perched at top-left `(9%, 15%)` above the large white rounded `05_Scene` chat card on the left half of the screen, containing the light-blue customer bubble, the royal-blue OPA reply bubble, and the emerald-green POS order confirmation card at the bottom).
- COMPONENT INGREDIENTS IDENTIFICATION:
  * Component `C01` (OPA Bull Mark): Flat geometric U-shaped head with two crescent horns and one circular O-ring cutout in the lower center (strictly NO eyes, NO nostrils, NO mouth). Scales and tilts from its bottom-center base `[50%, 100%]`.
  * Component `C02` (`05_Scene` White 3D Chat Card): Rounded white UI panel with a glowing cobalt-blue outer rim (`EdgeGlow #2690FF`), pivoting in 2.5D space around its center at `(28%, 52%)`.
  * Component `C03` (Three-Dot Typing Bubble): Royal-blue pill with three white dots bouncing in a sine wave, anchored at its bottom-right tail corner.
  * Component `C04` (Green POS Order Confirmation Card): Emerald-green bordered order box with a white-and-green checkmark badge inside the bottom half of `C02`.

[5-SECOND MOTION PROGRESSION (FROM FIRST FRAME TO LAST FRAME)]
- Step 1 (`0.00s -> 1.25s`, matching `F01 -> M02`):
  From `F01`, the OPA Bull Mark (`C01`) lunges forward (`Rotation -8 deg -> +6 deg`) and glides up to perch at `(9%, 15%)` as the large white `05_Scene` chat card (`C02`) swings in on the left half of the screen from an angled 3D perspective (`Y-Rotation +32 deg -> +14 deg`, `Scale 86% -> 95%`, `cubic-bezier(0.15, 0, 0, 1)`) with a bright cyan-blue light streak tracing around its border.
- Step 2 (`1.25s -> 2.50s`, matching `M02 -> M03`):
  The white chat card (`C02`) rotates flatter toward the camera (`Y-Rotation +14 deg -> +4 deg`) as the incoming light-blue customer chat bubble pops out at upper-left inside the card from its bottom-left tail corner (`Scale 0% -> 108% -> 100%`).
- Step 3 (`2.50s -> 3.75s`, matching `M03 -> M04`):
  On the right side of the chat card, the royal-blue typing indicator bubble (`C03`) pops in from its bottom-right tail corner and its three white dots bounce in a smooth wave (`0.08s` phase offset).
- Step 4 (`3.75s -> 5.00s`, matching `M04 -> F05_LAST_FRAME`):
  The typing bubble (`C03`) morphs into the full royal-blue AI reply bubble (`Scale 0% -> 108% -> 100%`), and immediately beneath it the emerald-green POS order confirmation card (`C04`) wipes open downward (`Out Influence 15.2%, In Influence 100%`) and stamps its green checkmark badge, locking into the exact composition of `F05_LAST_FRAME_t5.0s.png`. No text or numbers on screen.
```

---

### 🎬 ĐOẠN 03B (`00:16 – 00:22` | 6.0s / Block 5s): GIẢI PHÁP PHẦN 2 — SPLIT-SCREEN & 5 PILL TÍNH NĂNG NẢY THEO NHỊP 120 BPM

* **Thư mục ảnh**: [/media/vmiz/Over Powers/THÀNH V/Motion Omi/ẢNH/SCENE_03B_16s-22s_SPLIT_SCREEN_5_PILLS](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_03B_16s-22s_SPLIT_SCREEN_5_PILLS)
* **Khai báo Ảnh nạp vào Omni Flash**:
  * **First Frame (`0.0s`)**: [F01_FIRST_FRAME_t0.0s.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_03B_16s-22s_SPLIT_SCREEN_5_PILLS/F01_FIRST_FRAME_t0.0s.png)
  * **Last Frame / Ảnh Bao Quát Đích (`5.0s`)**: [F05_LAST_FRAME_t5.0s.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_03B_16s-22s_SPLIT_SCREEN_5_PILLS/F05_LAST_FRAME_t5.0s.png)
  * **Các Ảnh Thành Phần (`Components`)**:
    * `Component 1`: [C01_COMPONENT_PILL_01_TON_KHO.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_03B_16s-22s_SPLIT_SCREEN_5_PILLS/C01_COMPONENT_PILL_01_TON_KHO.png) (Pill 1: Icon Chat tồn kho)
    * `Component 2`: [C02_COMPONENT_PILL_02_CHOT_DON_GLOW.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_03B_16s-22s_SPLIT_SCREEN_5_PILLS/C02_COMPONENT_PILL_02_CHOT_DON_GLOW.png) (Pill 2: Icon Hộp hàng POS + Viền sáng `H15`)
    * `Component 3`: [C03_COMPONENT_PILL_03_CHECK_BILL.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_03B_16s-22s_SPLIT_SCREEN_5_PILLS/C03_COMPONENT_PILL_03_CHECK_BILL.png) (Pill 3: Icon Hóa đơn tích xanh)
    * `Component 4`: [C04_COMPONENT_PILL_05_TIEP_QUAN.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_03B_16s-22s_SPLIT_SCREEN_5_PILLS/C04_COMPONENT_PILL_05_TIEP_QUAN.png) (Pill 5: Icon Tai nghe nhân viên tiếp quản)

#### 📋 Prompt Chuyển Động Đoạn 03B (Copy dán vào Google Omni Flash):
```text
Everything below is invisible camera and animation control data. Never draw any labels, numbers, percentages, coordinates, arrows, or text onto the video frames.

[IMAGE REFERENCE & FRAME IDENTIFICATION]
- FIRST FRAME LOCK (`t = 0.00s`): Use `F01_FIRST_FRAME_t0.0s.png` as the starting frame (split-screen layout: left half holds the completed white `05_Scene` chat & POS card with the white OPA Bull Mark at top-left; right half shows the top header bars and the 1st rounded white feature pill `C01` popping in at `y = 24%`).
- LAST FRAME / MASTER TARGET LOCK (`t = 5.00s`): Use `F05_LAST_FRAME_t5.0s.png` as the exact ending composition (all 5 rounded white feature pills stacked evenly in the right column from `y = 24%` to `y = 74%`, with a bright cyan-blue selection glow highlighting Pills #2 and #3).
- COMPONENT INGREDIENTS IDENTIFICATION:
  * Components `C01`, `C02`, `C03`, `C04` (Feature Pill Buttons `05_Scene_Button02`): Wide white rounded pill cards with a blue circular icon badge on the left and a gray skeleton bar inside. Every pill is anchored at the center of its left circular icon badge `(x = 54%)`.

[5-SECOND MOTION PROGRESSION (FROM FIRST FRAME TO LAST FRAME)]
- Step 1 (`0.00s -> 1.25s`, matching `F01 -> M02`):
  While the left chat card floats gently in 2.5D space, Pill #1 (`C01` at `y = 24%`) settles from `106% -> 100%` scale, and on the next beat Pill #2 (`C02` at `y = 36.5%`, package box icon) springs open from its left circular icon anchor (`Scale 0% -> 108% -> 100%`, `Position X +4% -> 0%`, `cubic-bezier(0.15, 0, 0, 1)`).
- Step 2 (`1.25s -> 2.50s`, matching `M02 -> M03`):
  Following the strict `0.50s` (120 BPM) stagger grid, Pill #3 (`C03` at `y = 49%`, receipt checkmark icon) and Pill #4 (`y = 61.5%`, clock icon) pop in one after another from their left icon anchors (`Scale 0% -> 108% -> 100%`).
- Step 3 (`2.50s -> 3.75s`, matching `M03 -> M04`):
  Pill #5 (`C04` at `y = 74%`, headset icon) springs open at the bottom of the right stack (`Scale 0% -> 108% -> 100%`), completing all 5 feature pills.
- Step 4 (`3.75s -> 5.00s`, matching `M04 -> F05_LAST_FRAME`):
  A luminous cyan-blue outer border highlight (`Glow Selector Frame H15`) sweeps smoothly down the stack of 5 pills (`Out Influence 75%, In Influence 75%`), illuminating Pills #2 and #3 with green confirmation dots on their right edges, matching `F05_LAST_FRAME_t5.0s.png` exactly. No text or numbers on screen.
```

---

### 🎬 ĐOẠN 04 (`00:22 – 00:30` | 8.0s / Block 5s): GIẢI PHÓNG SỨC LAO ĐỘNG — CHỦ SHOP THẢNH THƠI & 3 TÍCH XANH ✅

* **Thư mục ảnh**: [/media/vmiz/Over Powers/THÀNH V/Motion Omi/ẢNH/SCENE_04_22s-30s_GIAI_PHONG_SUC_LAO_DONG](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_04_22s-30s_GIAI_PHONG_SUC_LAO_DONG)
* **Khai báo Ảnh nạp vào Omni Flash**:
  * **First Frame (`0.0s`)**: [F01_FIRST_FRAME_t0.0s.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_04_22s-30s_GIAI_PHONG_SUC_LAO_DONG/F01_FIRST_FRAME_t0.0s.png)
  * **Last Frame / Ảnh Bao Quát Đích (`5.0s`)**: [F05_LAST_FRAME_t5.0s.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_04_22s-30s_GIAI_PHONG_SUC_LAO_DONG/F05_LAST_FRAME_t5.0s.png)
  * **Các Ảnh Thành Phần (`Components`)**:
    * `Component 1`: [C01_COMPONENT_THE_GACH_BO_THAO_TAC_CU.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_04_22s-30s_GIAI_PHONG_SUC_LAO_DONG/C01_COMPONENT_THE_GACH_BO_THAO_TAC_CU.png) (Thẻ đang gạch chéo đỏ thao tác cực nhọc)
    * `Component 2`: [C02_COMPONENT_THE_TICH_XANH_01.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_04_22s-30s_GIAI_PHONG_SUC_LAO_DONG/C02_COMPONENT_THE_TICH_XANH_01.png) (Thẻ Tích xanh #1 bên trái)
    * `Component 3`: [C03_COMPONENT_THE_TICH_XANH_02.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_04_22s-30s_GIAI_PHONG_SUC_LAO_DONG/C03_COMPONENT_THE_TICH_XANH_02.png) (Thẻ Tích xanh #2 bên phải)
    * `Component 4`: [C04_COMPONENT_THE_TICH_XANH_03.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_04_22s-30s_GIAI_PHONG_SUC_LAO_DONG/C04_COMPONENT_THE_TICH_XANH_03.png) (Thẻ Tích xanh #3 phía trên giữa)

#### 📋 Prompt Chuyển Động Đoạn 04 (Copy dán vào Google Omni Flash):
```text
Everything below is invisible camera and animation control data. Never draw any labels, numbers, percentages, coordinates, arrows, or text onto the video frames.

[IMAGE REFERENCE & FRAME IDENTIFICATION]
- FIRST FRAME LOCK (`t = 0.00s`): Use `F01_FIRST_FRAME_t0.0s.png` as the starting frame (bright sunlit daylight studio, the young shop owner smiling peacefully behind the laptop with both arms stretched wide open in relief, a small blue OPA Bull Mark icon on the laptop screen, no floating banners yet).
- LAST FRAME / MASTER TARGET LOCK (`t = 5.00s`): Use `F05_LAST_FRAME_t5.0s.png` as the exact ending composition (three wide white rounded banners floating in a balanced arc around the smiling shop owner at `(23%, 30%)`, `(77%, 30%)`, and `(50%, 13%)`, each displaying a glowing emerald-green checkmark circle on the left and clean light-blue skeleton bars on the right).
- COMPONENT INGREDIENTS IDENTIFICATION:
  * Component `C01` (Red Strikethrough Banner State): The intermediate state where a red diagonal line crosses out the gray manual-task icon and bar.
  * Components `C02`, `C03`, `C04` (Emerald-Green Checkmark Banners): The resolved state of the three floating cards after the red strikethrough transforms into a green checkmark badge (`#10B981`). Each banner pivots from its center anchor, while the green checkmark badge springs from the left circular slot.

[5-SECOND MOTION PROGRESSION (FROM FIRST FRAME TO LAST FRAME)]
- Step 1 (`0.00s -> 1.25s`, matching `F01 -> M02`):
  The relaxed shop owner breathes gently and leans back comfortably (`Rotation 0 deg -> -2 deg`). On the left at `(23%, 30%)`, Banner #1 pops in from its center (`Scale 0% -> 108% -> 100%`), flashes the red strikethrough (`C01`), and immediately springs into the glowing emerald-green checkmark card `C02` (`Checkmark Scale 0% -> 115% -> 95% -> 100%`).
- Step 2 (`1.25s -> 2.50s`, matching `M02 -> M03`):
  On the right at `(77%, 30%)`, Banner #2 pops in from its center (`Scale 0% -> 108% -> 100%`), crosses out the old icon (`C01`), and snaps into the emerald-green checkmark card `C03`.
- Step 3 (`2.50s -> 3.75s`, matching `M03 -> M04`):
  At top-center `(50%, 13%)`, Banner #3 pops in (`Scale 0% -> 106%`) in the red strikethrough state `C01`, drawing the red diagonal slash across the gray icon (`Trim Paths 0% -> 100%`).
- Step 4 (`3.75s -> 5.00s`, matching `M04 -> F05_LAST_FRAME`):
  Banner #3 at top-center transforms from `C01` into the emerald-green checkmark card `C04` (`Scale 0% -> 115% -> 100%`), and all three green-checked banners float gently in place matching `F05_LAST_FRAME_t5.0s.png` exactly. No text or letters on screen.
```

---

### 🎬 ĐOẠN 05 (`00:30 – 00:36` | 6.0s / Block 5s): OUTRO & CTA — BÒ OPA + LOGO LOCKUP & CLICK `chat.overpowers.agency`

* **Thư mục ảnh**: [/media/vmiz/Over Powers/THÀNH V/Motion Omi/ẢNH/SCENE_05_30s-36s_OUTRO_CTA_LOCKUP](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_05_30s-36s_OUTRO_CTA_LOCKUP)
* **Khai báo Ảnh nạp vào Omni Flash**:
  * **First Frame (`0.0s`)**: [F01_FIRST_FRAME_t0.0s.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_05_30s-36s_OUTRO_CTA_LOCKUP/F01_FIRST_FRAME_t0.0s.png)
  * **Last Frame / Ảnh Bao Quát Đích (`5.0s`)**: [F05_LAST_FRAME_t5.0s.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_05_30s-36s_OUTRO_CTA_LOCKUP/F05_LAST_FRAME_t5.0s.png)
  * **Các Ảnh Thành Phần (`Components`)**:
    * `Component 1`: [C01_COMPONENT_BO_OPA_OUTRO.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_05_30s-36s_OUTRO_CTA_LOCKUP/C01_COMPONENT_BO_OPA_OUTRO.png) (Bò OPA xanh chuẩn V4)
    * `Component 2`: [C02_COMPONENT_CHU_OPA_WORDMARK.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_05_30s-36s_OUTRO_CTA_LOCKUP/C02_COMPONENT_CHU_OPA_WORDMARK.png) (Cụm chữ `OPA` xanh nguyên bản trang 3 PDF)
    * `Component 3`: [C03_COMPONENT_NUT_CTA_PILL.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_05_30s-36s_OUTRO_CTA_LOCKUP/C03_COMPONENT_NUT_CTA_PILL.png) (Nút CTA Pill xanh dương)
    * `Component 4`: [C04_COMPONENT_TRO_CHUOT_CLICK.png](file:///media/vmiz/Over%20Powers/THÀNH%20V/Motion%20Omi/ẢNH/SCENE_05_30s-36s_OUTRO_CTA_LOCKUP/C04_COMPONENT_TRO_CHUOT_CLICK.png) (Con trỏ chuột Vector)

#### 📋 Prompt Chuyển Động Đoạn 05 (Copy dán vào Google Omni Flash):
```text
Everything below is invisible camera and animation control data. Never draw any labels, numbers, percentages, coordinates, arrows, guides, or extra text onto the video frames.

[IMAGE REFERENCE & FRAME IDENTIFICATION]
- FIRST FRAME LOCK (`t = 0.00s`): Use `F01_FIRST_FRAME_t0.0s.png` as the starting frame (clean white-and-sky-blue daylight canvas with the royal-blue OPA Bull Mark springing up at center `(50%, 41%)`, head tilted `-5 deg` and crescent horns folded inward `-28 deg`).
- LAST FRAME / MASTER TARGET LOCK (`t = 5.00s`): Use `F05_LAST_FRAME_t5.0s.png` as the exact ending composition (the OPA Bull Mark `C01` positioned at left-of-center `(34%, 35%)` beside the bold geometric blue `OPA` wordmark `C02` at `(59%, 36%)`, a subtitle skeleton bar below, and the wide royal-blue CTA pill button `C03` at `(50%, 73%)` with concentric blue click ripple rings and the vector mouse cursor `C04` resting at `(61%, 77%)`).
- COMPONENT INGREDIENTS IDENTIFICATION:
  * Component `C01` (OPA Bull Mark): Flat royal-blue (`#0068FF`) U-shaped head with two crescent horns and one solid white circular O-ring cutout in the lower center (strictly NO eyes, NO nostrils, NO mouth). Head pivots from its bottom-center base `[50%, 100%]`; horns pivot from their roots `[22.6%, 42.1%]` and `[77.4%, 42.1%]`.
  * Component `C02` (`OPA` Geometric Wordmark): Slides out horizontally from behind `C01` via an invisible vertical track-matte.
  * Component `C03` (Royal-Blue CTA Pill Button): Centered at `(50%, 73%)`, morphing from a small circle into a wide rounded pill (`Rectangle Size [116, 116] -> [920, 116]`).
  * Component `C04` (Vector Mouse Pointer): Glides in from bottom-right `(77%, 87%)` along a smooth curved Bézier arc, pivoting at its arrow tip.

[5-SECOND MOTION PROGRESSION (FROM FIRST FRAME TO LAST FRAME)]
- Step 1 (`0.00s -> 1.25s`, matching `F01 -> M02`):
  At center `(50%, 41%)`, the OPA Bull Mark (`C01`) settles from its `112% -> 95% -> 100%` spring pop (`Rotation -5 deg -> 0 deg`) as both crescent horns swing outward from their roots (`Rotation -28 deg -> +6 deg -> 0 deg` with a `0.08s` stagger) to lock into the exact upright silhouette of `M02`.
- Step 2 (`1.25s -> 2.50s`, matching `M02 -> M03`):
  The bull mark (`C01`) glides smoothly left from `x = 50%` to `x = 34%` while scaling uniformly to `72%` (`Out Influence 75%, In Influence 75%`), revealing the blue `OPA` wordmark (`C02`) sliding into `(59%, 36%)`. Below at `(50%, 73%)`, the CTA pill button (`C03`) begins stretching horizontally outward from its center (`width 116px -> 320px`) as the mouse cursor (`C04`) enters at bottom-right `(77%, 87%)`.
- Step 3 (`2.50s -> 3.75s`, matching `M03 -> M04`):
  The CTA pill (`C03`) finishes expanding to its full width (`920px`, `cubic-bezier(0.15, 0, 0, 1)`). The mouse cursor (`C04`) arcs smoothly up to `(60%, 76%)` and clicks the button at `3.50s`: the cursor tip presses down (`Scale 100% -> 88%`) and the entire CTA pill compresses to `Scale 94%` while emitting two expanding concentric blue ripple rings.
- Step 4 (`3.75s -> 5.00s`, matching `M04 -> F05_LAST_FRAME`):
  The CTA pill (`C03`) rebounds crisply (`Scale 94% -> 103% -> 100%`) and holds steady in the exact final lockup of `F05_LAST_FRAME_t5.0s.png`.
```

<!-- ===== /file: omni-flash-motion-director/references/QUY-TRINH-SAN-XUAT-VA-PROMPT-TU-ANH-OMNI-FLASH.md ===== -->
