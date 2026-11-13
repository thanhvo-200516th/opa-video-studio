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
