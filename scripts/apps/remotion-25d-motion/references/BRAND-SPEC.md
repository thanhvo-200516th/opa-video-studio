Ngày tạo: 06/10/2026 · Dựng bằng Claude Code (Opus 5.5) + Remotion 4.0.533
Trạng thái: chờ Hùng duyệt mascot SVG và sting 6 s

# BRAND-SPEC: video motion graphic OPA

Mọi video OPA **import** màu, chữ, chuyển động và mascot từ code dùng chung bên dưới. Không định nghĩa lại màu hay easing trong từng video. Muốn đổi thì đổi ở đây và ở file nguồn tương ứng, rồi render lại.

## 1. Màu

Chỉ dùng các màu này (nguồn: `src/brand/tokens.ts` → `COLORS`, riêng đỏ cảnh báo là hằng `ALERT`).

| Tên trong code | Mã | Dùng cho |
|---|---|---|
| `blue` | #0068FF | Xanh OPA, chủ đạo |
| `black` | #0A0A0A | Nền tối |
| `white` | #FFFFFF | Nền sáng, chữ trên nền xanh hoặc tối |
| `blueLight` | #E6F0FF | Nền phụ rất nhạt |
| `blueDark` | #003C99 | Nền phụ đậm, vật nhỏ (chấm, bong bóng tin nhắn) |
| `ALERT` (hằng riêng) | #E5484D | **Chỉ** cho dấu cảnh báo nhỏ: chỗ "rò khách", lỗi trong quy trình (Minh chốt 11/10/2026, dùng từ V3). Không làm nền lớn, không tô chữ, không tô mascot. |

- **Màu chữ theo nền** (`TEXT_ON`): trên nền xanh dùng chữ trắng. Trên nền trắng dùng chữ đen (hoặc xanh cho dòng nhấn).
- **Màu mascot theo nền** (`MASCOT_ON`): bản xanh trên nền sáng. **Bản trắng chỉ đặt trên nền xanh hoặc nền tối.**
- **Phong cách:** phẳng, khối hình học, nhiều khoảng trắng, chuyển cảnh dứt khoát. Không gradient cầu vồng, không 3D bóng loáng, không ảnh stock người. (Ngoại lệ có giới hạn: phim 3D Bò OPA, xem mục 9.)

## 2. Chữ

- **Font:** "Be Vietnam Pro" (Google Fonts, `src/brand/fonts.ts`), có đủ bộ dấu tiếng Việt. Tiêu đề **ExtraBold 800**, nội dung **Medium 500**.
- **Font cụm nhấn** (Minh chốt 09/10/2026): "Fraunces" **Italic 800** (`ACCENT_FONT` trong `src/brand/fonts.ts`), đủ dấu tiếng Việt. Chỉ dùng cho cụm nhấn. Cụm nhấn luôn đi kèm hiệu ứng có nghĩa, không chỉ đổi màu:
  - khối "đánh dấu" màu nhấn quét dưới chữ từ trái sang, như một hàng CRM vừa được ghi nhận;
  - chữ đổi màu đúng chỗ khối phủ;
  - bản 16:9 làm bằng `src/v2w/text/accentMark.tsx`.
  - Mọi cụm nhấn song song xử lý như nhau.
- **Viết hoa** chữ cái đầu mọi dòng hiển thị, kể cả dòng 2 của câu bị ngắt ("Khách nhắn / Tối qua…") (Minh chốt 09/10/2026).
- **Cỡ chữ** (`TYPE`, cho khung 1080 px chiều ngang):

  | Loại | Cỡ |
  |---|---|
  | display | 150 |
  | title | 88 |
  | body | 48 |
  | caption | 38 |

- **Line-height 1,32.** Đã kiểm tra trên `type-test` (ảnh `out/review/type-test.png`): dấu chồng (Ầ Ổ Ữ), dấu nặng và đ không bị cắt, không chạm dòng trên.
- **Component chữ:** dùng `<TextLine>` (`src/components/Text.tsx`). Nó đã gắn sẵn font, line-height và kiểu vào cảnh trượt lên + hiện dần.
- **Giọng chữ:** tiếng Việt, xưng "OPA", gọi khách là "anh chị". Câu ngắn, mỗi khung tối đa 7–9 chữ.

## 3. Khung hình và vùng an toàn

| Tỉ lệ | Kích thước | fps | Composition |
|---|---|---|---|
| 9:16 (mặc định: TikTok, Reels, Facebook) | 1080 × 1920 | 30 | `mascot-sting` |
| 1:1 (khi được yêu cầu) | 1080 × 1080 | 30 | `mascot-sting-1x1` |
| 16:9 (khi được yêu cầu) | 1920 × 1080 | 60 | `v2-khong-bo-sot-khach-16x9`, `v3-ai-audit-16x9`, phim 3D (`film3d/`, mục 9). Sting cũ `mascot-sting-16x9` vẫn 30 fps (Minh chốt 60 fps cho 16:9 ngày 19/10/2026) |

- **Vùng an toàn 9:16:** chừa **250 px trên, 420 px dưới, 120 px bên phải** (`safeInsets`).
- **Vùng an toàn 1:1 và 16:9:** spec chưa quy định, tạm dùng lề đều 6 % cạnh ngắn. *(Đề xuất, chờ Hùng duyệt.)*
- **Lề chữ trái** tối thiểu `TEXT_GUTTER` = 72 px.
- **Soát nhanh vùng an toàn:** render với `--props='{"showGuides":true}'`. Vùng bị giao diện nền tảng che sẽ hiện màu đỏ nhạt.
- **Màu xuất video:** H.264, `yuv420p`, dải TV, bt709 (`remotion.config.ts`). Đo trên MP4, xanh #0068FF ra (0,103,255).

## 4. Mascot "Bò OPA"

- **Tính cách:** khỏe, chắc, đáng tin, chủ động lao vào việc. Không hề, không dễ thương kiểu trẻ con.
- **Không** thêm mắt, miệng hay chi tiết mới. **Không** đổi tỉ lệ.

### File vector

- **Bản gốc:** `logo/OPA-V4-A-Core-*-2000.png` và thông số dựng trong `logo/OPA — Biểu tượng 2D V4.pdf`.
- **Script dựng:** `tools/mascot/build_mascot.py` (chạy `npm run mascot:build`). Script sinh ra:

| File | Nội dung |
|---|---|
| `mascot/opa-mascot-blue.svg` | Một path liền, bản xanh, dùng tĩnh |
| `mascot/opa-mascot-black.svg` | Một path liền, bản đen, dùng tĩnh |
| `mascot/opa-mascot-white.svg` | Một path liền, bản trắng, dùng tĩnh |
| `mascot/opa-mascot-parts.svg` | 4 phần tách để animate |
| `mascot/opa-mascot-parts-preview.png` | Ảnh tô màu từng phần để duyệt |
| `src/mascot/geometry.json` | Toạ độ cho component (không sửa tay) |

### 4 phần tách

| Mã | id trong SVG | Phần |
|---|---|---|
| (a) | `a-horn-left` | Sừng trái. Có "chân sừng" chìm trong thân để khi nghiêng ±2° không hở đường nối |
| (b) | `b-horn-right` | Sừng phải (ảnh gương của sừng trái) |
| (c) | `c-muzzle` | Khối mõm chữ U bo tròn, gồm thân, trán và lòng O |
| (d) | `d-nostril-gap` | Khe trán giữa đỉnh mõm. Là vùng trống, không tô. Hai mép khe là 2 "lỗ mũi", điểm phát hạt khi thở phì |

### Cách dựng hình

- **Thân, trán, khe:** đúng số trong PDF.

  | Đại lượng | Giá trị |
  |---|---|
  | W | 520 u |
  | t | 99,311 u |
  | g = W/φ³ | 122,755 u |
  | b = t/φ | 61,378 u |
  | Bo góc | R = 2t, r = t, đồng tâm |

  PNG 2000 px = **2 px/u**, không lệch gốc, nên viewBox SVG 0 0 2000 2000 trùng PNG.
- **Sừng:** PDF chỉ ghi "mỗi cạnh một Bézier bậc 3". Script lần viền dưới pixel từ PNG rồi khớp mỗi cạnh bằng đúng một cubic (tối ưu sai số lớn nhất). Kết quả:
  - Tiếp tuyến tại chỗ nối trán nằm ngang.
  - Khía vai ra **125,0°**, khớp PDF.
  - Mũi rộng 49,4 u, PDF ghi 0,5t = 49,7 u.

### Độ khớp với PNG gốc

Chi tiết trong `mascot/verify/report.md`.

| Vùng | Lệch lớn nhất | P99 |
|---|---|---|
| Sừng | 0,76 px | 0,45 px |
| Thân / mõm / khe | 0,48 px | 0,28 px |

- Yêu cầu là ≤ 2 px. Không điểm viền nào lệch quá 1 px.
- Đường nối giữa các phần khi ghép lại: chênh alpha tối đa 0,008, không thấy bằng mắt.

### Thư viện chuyển động

Code ở `src/mascot/`. Mỗi chuyển động là hàm thuần của frame, gộp bằng `combine()`.

| # | Tên | API | Mô tả |
|---|---|---|---|
| 1 | reveal | `reveal(frame, fps, start)` | Mõm chữ U bật lên từ dưới (spring damping 12, nảy một lần), viền rồi đổ màu xanh từ dưới lên 0,4 s, hai sừng vẽ dần từ gốc lên ngọn 0,6 s. Tổng `revealFrames(fps)` = 32 frame |
| 2 | idle | `idle(frame, fps, start, {amplitude, hornDegrees, periodSeconds})` | Thở: scale 1,00 → 1,03 → 1,00, chu kỳ 2,4 s. Sừng nghiêng ±2° đối xứng |
| 3 | charge | `charge(frame, start, {direction, tiltDegrees, back, lunge})` | Cúi 8°, lùi 20 px, lao tới 60 px kèm motion blur ngang ngắn, dừng có rung tắt dần. Đứng lại ở vị trí đã lao. 24 frame. Dùng khi chuyển sang lời giải |
| 4 | snort | `snortPuff(...)` + `<SnortParticles start color>` | Phồng nhẹ một nhịp, 2 cụm hạt bay lên từ hai mép khe (d), 0,4 s. Dùng để nhấn mạnh |
| 5 | catch | `<CatchItems {...} kind="dot" \| "message">` + `catchPulse()` + `catchSchedule()` | Mọi vật rơi hội tụ vào khe, xuống đáy lòng U rồi tan; không vật nào rơi ra ngoài. `catchSchedule()` trả frame chạm đáy để đồng bộ hiệu ứng khác (ví dụ dòng CRM ở V2) |
| 6 | badge | `badgePlacement()`, `toBadge()` | Watermark góc dưới trái, cao 96 px, độ mờ 90 %, nằm trên vùng 420 px dưới |
| 7 | outro | `<Outro background price cta mascotFrom>` | 2,5 s: mascot giữa khung + "OPA" + "Đối tác vận hành AI / cho đội bán hàng" + CTA (mặc định `opa.business`), thêm dòng giá nếu truyền `price` |

- **Easing chủ đạo** (`src/brand/tokens.ts`):
  - Vào cảnh: `EASE_IN_SCENE` = cubic-bezier(0.2, 0.8, 0.2, 1).
  - Bật nảy: `SPRING_POP` = spring damping 12.
- **Vị trí:** `heroPlacement()` đặt mascot lớn giữa vùng an toàn. Placement gồm tâm và chiều cao dấu, tính bằng px khung video.
- **Xem cả 7 động tác:** `out/mascot-motions-preview.mp4` (composition `mascot-motions`).

## 5. Âm thanh

- Mỗi video có 1 track nhạc nền **trống** (`<BgmPlaceholder />`, file `public/audio/bgm-placeholder.wav`) và SFX gợi ý tại charge, snort, catch (`<Sfx cue at />`).
- Mọi file hiện là âm thanh im lặng để giữ chỗ. Thay bằng file cùng tên, xem `public/sfx/README.md`.
- **Không dùng nhạc có bản quyền.**

## 6. Giá và link

- **`prices.json`:** `SHOW_PRICE=false` và mọi giá để trống.
  - Khung giá dùng `priceLine(keys, format)` (`src/brand/content.ts`).
  - Khi `SHOW_PRICE=false`, luôn hiện "**Nhắn OPA để nhận báo giá**".
  - Khi `SHOW_PRICE=true` mà còn giá trống, render **dừng với lỗi** để tránh đăng video giá rỗng.
- **`links.json`:** `WEBSITE = opa.business`. Fanpage, link đăng ký và link tải còn là chỗ `{{...}}` chờ điền.

## 7. Quy tắc nội dung (mọi video)

- **Không đưa con số kết quả** (%, số đơn, doanh thu tăng…) nếu không có câu chuyện khách hàng thật đi kèm. Chỉ nói lợi ích định tính: không bỏ sót khách, phản hồi nhanh, có báo cáo, đội tự dùng được AI.
- **Không dùng tên, logo, ảnh chụp màn hình hay dữ liệu thật của khách.** Giao diện minh hoạ dùng dữ liệu giả, tên giả rõ ràng.
- **Không nhắc** khoá kiếm tiền online, trợ lý AI kế toán hay pháp chế.
- **Duyệt trước khi đăng:** mọi video qua Hùng (hình) và Minh (lời, giá).

## 8. Lệnh thường dùng

```bash
npm run dev            # mở Remotion Studio để xem và tua
npm run render:sting   # render out/mascot-sting.mp4
npm run mascot:build   # dựng lại SVG mascot + báo cáo so khớp
```

**Lưu ý trên máy này:** một hook có thể viết lại lệnh `npx remotion …`. Nếu lệnh lỗi "Missing script", gọi thẳng `./node_modules/.bin/remotion …`.

## 9. Phim 3D Bò OPA (ngoại lệ, Minh duyệt 19/10/2026)

Mục 1 ghi "không 3D bóng loáng". Phim 3D mascot là ngoại lệ có giới hạn, áp **chỉ** cho dòng phim dựng bằng three.js trong `film3d/` (skill `mascot-film-3d`). Mọi video 2D vẫn theo mục 1. Minh duyệt kiểu 3D và báo Hùng; Hùng vẫn duyệt hình trước khi đăng (mục 7).

- **Hình Bò:**
  - đùn từ dấu trong `src/mascot/geometry.json` (sinh qua `film3d/brand-opa/export.ts`, không chép tay);
  - dày t = 198,62 px logo, bằng nét chữ U;
  - cạnh vát bo tròn 0,08 t;
  - mặt trước khớp logo: IoU ≥ 0,999, lệch viền ≤ 1 px;
  - như mục 4: không mắt, miệng, tay chân; không bóp méo: thở và hơi phì chỉ co giãn đều mọi trục (biên độ không giới hạn thêm; phim "Thủ môn" thở 1,00–1,03, mỗi cú phì phồng thêm tới 3,5 %); sừng xoay quanh chân sừng.
- **Look "C2":**
  - mặt trước và mặt sau tô phẳng đúng #0068FF. Đo trên MP4 theo mặt nạ: lệch CIEDE2000 ≤ 2 (phim "Thủ môn" đo ra (0,103,255), lệch 0,34);
  - thành bên nhận sáng từ #003C99 tới gần #0068FF;
  - viền sáng mảnh chạy theo cạnh vát;
  - không kim loại, không gương, không bóng loáng (mục 1), không gradient cầu vồng.
- **Luật nền (luật đêm):**
  - Bò xanh chỉ đứng trước nền sáng ngay sau lưng. Đo bằng độ sáng vòng nền 6–20 px quanh bóng Bò.
  - Cảnh đêm được phép khi màn hình sáng nằm ngay sau Bò xanh.
  - Bò trắng chỉ trên nền xanh hoặc tối, như mục 1.
- **Diễn:**
  - bằng tư thế, sừng, nhịp thở;
  - hơi thở phì là hạt xanh #0068FF bật ra từ hai mép khe trán;
  - cận cảnh được cắt thân Bò khi storyboard ghi rõ, nhưng ngọn sừng luôn cách mép khung ≥ 24 px.
- **Khung hình và xuất:** 16:9, 1920 × 1080, 60 fps; H.264, `yuv420p`, dải TV, bt709. Render 16 mẫu mỗi điểm ảnh để không răng cưa và có nhòe chuyển động thật.
- **Chữ:**
  - lớp phủ Remotion trong suốt, theo mục 2;
  - vùng chữ là nền trơn, tương phản với nền 3D ≥ 4,5 : 1;
  - máy quay không lia ngang qua cột chữ khi chữ còn trên hình.
- **Màn kết:** chương "trạm OPA" 16:9 của V2. Bò 3D chuyển trắng, dẹt thành dấu 2D và khóa đúng vị trí Bò 2D của màn kết (lệch ≤ 2 px).
- **Âm** (Minh chốt 23/10/2026):
  - master −16 LUFS như V2, V3; bản đăng mạng xã hội −14 LUFS (cộng +2 dB ở bước stereo sau limiter, đỉnh thật ≤ −2 dBTP). Nguồn số liệu: `docs/film3d/am-thu-vien/nghien-cuu-decibel.md`;
  - nhạc nền tự tổng hợp; SFX tự tổng hợp hoặc lấy từ thư viện miễn bản quyền `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx` (danh mục đo: `docs/film3d/am-thu-vien/danh-muc-sfx.csv`), âm có nốt phải khớp giọng nhạc; không dùng nhạc có bản quyền;
  - Bò "nói" bằng hơi mũi phì, sừng gõ "tok" và thân đáp trầm; không tiếng bò kêu.
- **Nguồn đo và lệnh:** `film3d/films/<phim>/FOLLOWUPS.md` (thang kiểm 8 nấc), `tools/film3d/qa.py`, `tools/v2w/metrics.py`. Phim mẫu: `out/thu-mon-3d-16x9-ban2/` (bản 2, Minh duyệt 21/10/2026; âm thư viện chọn 22/10/2026).
