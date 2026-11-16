# Phân Tích Chuyên Sâu: Text, Typography, Text Motion & Slow Text của `@__dviet` (Cập Nhật Tháng 11/2026)

> Nghiên cứu đối chiếu **2 video mới nhất tháng 11/2026** (`7706183278461570356` ngày 2026-11-09, `7707653827016674580` ngày 2026-11-13) với **2 video tháng 08/2026** (`7669054598971133204` ngày 2026-08-01, `7672413018575146261` ngày 2026-08-10) và **hồ sơ cũ `dviet-style.json`** (17 video 20/07–05/10/2026).
> Toàn bộ timestamp, kích thước pixel, màu sắc, tốc độ nói (WPM) và độ dài chuyển động được đo trực tiếp từ sheet 2 fps, strip 12 fps (`83 ms/frame`), full-res PNG và transcript Whisper `large-v3-turbo`.

---

## 1. Bảng Dữ Liệu Tổng Hợp 4 Video Đối Chứng

| Video ID | Ngày | Tỉ lệ & FPS | Thời lượng | Số shot / Trung vị shot | Cuts/10s | LUFS | Tổng từ / WPM (nói) | Phong cách chính |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `7669054598971133204` | 2026-08-01 | `1080×1920` (9:16), `60 fps` | `27.75 s` | `6` / `1.75 s` | `2.52` | `-11.4` | `125` từ / `275.7 WPM` | Classic tutorial (3 font, chữ chồng lớp) |
| `7672413018575146261` | 2026-08-10 | `1080×1920` (9:16), `60 fps` | `65.16 s` | `7` / `1.72 s` (`max 52.0 s`) | `1.84` | `-12.1` | `287` từ / `275.3 WPM` | Classic tutorial (flash biến mất, 3 font) |
| `7706183278461570356` | 2026-11-09 | **`1440×1080` (4:3), `24 fps`** | `61.14 s` | `15` / **`3.21 s`** (`max 15.71 s`) | `2.29` | `-11.3` | `283` từ / `279.2 WPM` | **Cinematic Storytelling + Slow Text** |
| `7707653827016674580` | 2026-11-13 | **`1440×1080` (4:3), `30 fps`** | `57.21 s` | `31` / `1.20 s` (`max 5.83 s`) | `5.94` | **`-16.7`** | `282` từ / `297.2 WPM` | **Editorial Motion Graphics + Optical Glow** |

> **Phát hiện cốt lõi về nhịp điệu:** Ở video `7706183278461570356` (09/11/2026), tốc độ nói của `@__dviet` thực chất **không chậm đi** (`279.2 WPM` so với `275 WPM` cũ và `287 WPM` trung vị hồ sơ cũ). Cảm giác "chậm, sâu, điện ảnh" (**Slow Text**) đến từ 4 đòn bẩy thị giác: (1) chuyển sang khung **4:3 @ 24 fps**, (2) tăng gấp đôi độ dài shot (`3.21 s` vs `1.72 s`), (3) **gom text thành cụm câu giữ lâu `1.5–2.7 s`** thay vì bật-tắt từng 1–3 từ ở giữa ngực, và (4) dùng **opacity ramp chậm (`0.33–0.45 s`), staggered letter reveal (`0.25–0.42 s`) & cross-dissolve swap (`0.25–0.50 s`)** thay cho `hard swap`.

---

## 2. Text & Typography (Bước Nhảy Từ 3-Font Mix Sang 1-Family Discipline)

### 2.1. Hệ font mới (Tháng 11/2026)
- **Loại bỏ hoàn toàn Serif nghiêng (`Playfair Display Bold Italic`) và Script (`Great Vibes` / `Whisper`)**: Trên toàn bộ cả 2 video mới (`7706183278461570356` và `7707653827016674580`), **100% chữ trên khung hình sử dụng duy nhất hệ Sans-Serif hẹp/nén ngang** (chỉ trừ logo thương hiệu `MagentX` ở `t=44.2 s` của `7706183`).
- **Đặc điểm hình thái chữ (đo từ full-res `1440×1080`):**
  - Chữ thường **100% chữ thường (`lowercase`)** cho cả dòng dẫn và từ khóa nhấn (giống nguyên tắc cũ, ngay cả cụm nhấn như `"chán"`, `"sức mạnh"`, `"hard cut,"`, `"tập trung"`).
  - **Nén ngang (`scaleX ≈ 0.78–0.85`) + tracking âm chặt (`-45` đến `-70`)**: Tạo dáng chữ cao, thon, hiện đại kiểu editorial poster (gần với `SF Pro Display Condensed` / `SVN-Gilroy` nén ngang hoặc `Be Vietnam Pro` nén ngang `80%`).
  - Ở `7706183278461570356`: Chữ talking head và storytelling dùng nét chữ tròn hình học (`a` 1 tầng trong `"chán"`, `"đang"`, `"tia"`, `"đã"`, `"mình chỉ chắc"`), độ dày `Medium/SemiBold` cho từ khóa và `Regular` cho dòng phụ.
  - Ở `7707653827016674580`: Talking head dùng sans-serif nén ngang bo nhẹ có glow (`"bạn nghĩ"`, `"sức mạnh"`, `"âm thanh"`), còn các **thẻ motion graphics minh họa** (`t=9.8–10.8 s`, `t=33.2–37.4 s`) dùng sans-serif nét đều hình thái `grotesque` (`a` 2 tầng trong `"hard cut,"`, `"đơn giản nhất là"`).

### 2.2. Phân tầng kích thước (Đo trực tiếp trên canvas `1440×1080`)
- **Chữ dẫn / ngữ cảnh (`context_small`)**:
  - `7706183` (`t=3.8 s`): `"mình đang..."` cao `74 px` (`~6.9% H`), `"công việc"` cao `79 px` (`~7.3% H`).
  - `7707653` (`t=4.2 s`): `"bạn nghĩ"` cao `61 px` (`~5.6% H`); (`t=10.2 s`): `"đơn giản nhất là"` cao `67 px` (`~6.2% H`).
- **Từ khóa nhấn (`keyword_sans_glow`)**:
  - `7706183` (`t=3.8 s`): `"chán"` cao `140 px` (`~13.0% H`) -> **tỉ lệ nhấn ~`1.8–1.9×`** chữ dẫn.
  - `7707653` (`t=4.2 s`): `"sức mạnh"` lõi chữ `108 px` (`~10.0% H`) -> **tỉ lệ nhấn ~`1.8×`** chữ dẫn.
  - `7707653` (`t=10.2 s` motion-graphic card): `"hard cut,"` cao `212 px` (`~19.6% H`) -> **tỉ lệ nhấn ~`3.2×`** chữ dẫn.
- **Tầng nền chìm (`watermark_bg` — MỚI hoàn toàn ở `7707653`)**:
  - Chữ tiếng Việt cỡ đại (`~280–360 px`, chiếm gần hết chiều ngang khung) đặt làm nền ở **opacity `5–10%`**, làm mờ nhẹ (`blur ~4–8 px`): `"cắt"` (`t=7.2–8.8 s`), `"cắt cứng"` (`t=9.8–10.8 s`), `"âm thanh"` (`t=25.8–26.8 s`), `"khớp"` (`t=28.8–29.2 s`), `"khớp hình"` (`t=33.2–37.8 s`), `"hành"` (`t=38.2–38.8 s`), `"dựng phim"` (`t=46.2–49.8 s`).

### 2.3. Màu sắc, Ánh sáng & Optical Halation (Thay Drop Shadow Đen Bằng Bloom)
- **Không còn viền/bóng đen cứng (`#000000`)** trên chữ talking head như tháng 08/2026 (`opacity 50%, blur 10, dist 4`).
- Thay bằng **Optical Halation / Soft Glow** hòa vào ánh sáng phim:
  - **`7706183` (Tone ấm điện ảnh)**:
    - Cảnh tối: vàng hổ phách **`#E7BC11`** kèm quầng sáng mềm.
    - Cảnh có nắng / ngoài trời (`t=27.0 s`, `t=53.5 s`): vàng rực **`#FAE616`** / vàng nắng **`#F5CE88`**, đến cả chữ trắng cũng có **quầng halation trắng rất nhẹ** (như quay qua filter Black Pro-Mist).
  - **`7707653` (Tone Emerald / Tech Editorial)**:
    - Chữ nhấn trên nền tối & sofa: xanh mint-neon **`#3EED9C` – `#45EDA0`** (dịu mắt và sang hơn hẳn `#04AC04` cũ), glow bán kính mềm `14–22 px`.
    - Thẻ motion-graphic nền sáng (Light Card): nền kem xanh **`#E6ECD6`**, chữ xanh rừng đậm **`#347A53`** (kèm viền sắc sai RGB nhẹ ở mép chữ tạo cảm giác ống kính vintage).
    - Thẻ motion-graphic nền tối (Dark Card): xanh rêu thẫm chuyển sắc (`#072816` → `#0E3B22`) với chữ trắng & xanh neon.
- **Làm mờ viền ống kính (`peripheral_lens_blur`)**: Cả hai video tháng 11/2026 đều áp dụng hiệu ứng mờ xuyên tâm / mờ 4 góc rất mạnh (`radial/lens blur` từ ~`55%` tâm ra ngoài) + vignette tối 4 góc, khiến chữ đặt ở vùng mờ cũng mang nhẹ chất quang học của ống kính.

### 2.4. Bố cục không gian & Tương tác chiều sâu
- **Thoát khỏi vùng ngực giữa (`y=45–65%`)**: Trên các cảnh talking head tháng 11/2026, chữ được dời sang **khoảng trống âm (negative space)** bên trái hoặc bên phải khuôn mặt (`x ≈ 12–42%` hoặc `x ≈ 58–88%`, `y ≈ 22–52%`), không còn đè ngang ngực áo gây rối như `7669054` và `7672413`.
- **Chữ uốn cong / quỹ đạo quanh đầu (`curved_orbit` & `3d_ring`)**:
  - `7707653` `t=0.8–3.2 s`: Vòng cung kép ôm quanh đầu (`"bốn cách để cắt video"` ngoài, `"mà mọi editor nên"` trong).
  - `7706183` `t=17.2–19.3 s`: Cụm 3 đoạn chữ uốn tròn ôm theo hình đầu & vai (`"những luồng idea"` + `"dần biến thành"` + `"cơn nhức đầu"`).
  - `7707653` `t=43.0–43.7 s`: **Vòng chữ 3D xoay quanh đỉnh đầu** (`"quay đầu • quay đầu •"`) mô phỏng đúng động tác nói.
- **Rotoscoping / Che chữ sau tiền cảnh (`depth_masking`)**:
  - `7706183` `t=13.9–15.8 s`: `"thích thú"` & `"mình tạo ra"` nằm hoàn toàn **sau lưng & đầu chủ thể** (chủ thể tách nền đè lên trên, chữ dẫn nhỏ `"với những sản phẩm"` đặt ở lớp trước ngực).
  - `7706183` `t=35.4–36.2 s`: `"cái hộp"` & `"giữ mình lại"` bị **thân cây tiền cảnh quét ngang che khuất** theo chuyển động lia máy (motion-tracked occlusion).

---

## 3. Chuyển Động Của Chữ (Text Motion — Các Kiểu Mới Tháng 11/2026)

Đo từng khung ở `12 fps` (`83 ms/frame`) cho thấy sự đa dạng vượt trội so với 4 kiểu cũ (`blur_in`, `fade`, `slide_up_blur`, `whip_in`):

| Kiểu chuyển động | Thời lượng vào / ra | Cơ chế quan sát trực tiếp (Timestamp) | Khác biệt so với trước 10/2026 |
| :--- | :--- | :--- | :--- |
| **1. Slow Opacity Ramp + Bloom** | Vào **`0.33–0.42 s`** | `7706183`: `"chán"` (`t=3.17–3.58 s`, `0.42 s` từ 15%→100% + bloom); `"tia hy vọng"` (`t=25.63–25.97 s`, `0.33 s` ăn khớp vệt nắng); `"cái hộp"` (`t=35.25–35.58 s`, `0.33 s`). | Chậm gấp ~2× `blur_in` cũ (`0.17 s`), gần như không trượt vị trí (`slide_px = 0`). |
| **2. Random Per-Letter Staggered Fade/Blur** | Vào **`0.25–0.42 s`** | `7706183` `t=52.00–53.67 s`: `"mình chỉ chắc"` (`0.25 s`: chữ cái hiện ngẫu nhiên `ì h ắ` → đủ câu), `"một điều"` (`0.33 s`), `"từ giờ"` (`0.42 s` hiện từng chữ cái rất từ tốn). | Mới hoàn toàn; thay vì hiện từng từ rời rạc, cả cụm hiện mềm theo ký tự ngẫu nhiên. |
| **3. Cross-Dissolve Text Swap** | Chồng **`0.25–0.42 s`** | `7706183` `t=4.17–4.42 s`: `"mơ ước"` fade-in đè lên `"chán"` đang fade-out; `t=54.00–54.25 s`: `"mình chỉ chắc"` + `"một điều"` mờ dần `0.25 s` trong khi `"mình sẽ làm ra"` hiện lên. | Xoá bỏ `out_default: hard swap` cũ, tạo cảm giác chữ "tan" vào nhau. |
| **4. Typewriter + Glitch/Decoder Cursor (`\|`)** | Vào **`0.50 s`** (hoặc `0.20 s` ngắn) | `7707653` `t=22.88–23.38 s`: `"âm thanh"` chạy ký tự giải mã (`?#` → `â= \|` → `âm th\|` → `âm thanh\|`, `0.50 s`) với con trỏ xanh nhấp nháy tới `t=24.05 s`. Nhanh hơn ở `"effect"` (`t=5.10–5.30 s`, `0.20 s`). | Mới hoàn toàn (mang chất tech/UI editor). |
| **5. Vertical Echo Stack (`chồng lên`)** | `0.25 s` slide + `0.75 s` echo | `7707653` `t=24.13–25.22 s`: `"chồng lên"` trượt ngang kèm motion blur (`0.25 s`), sau đó nhân bản xếp chồng 3–4 lớp lên phía trên (`t=24.55–25.22 s`) để minh họa nghĩa đen của từ. | Minh họa trực tiếp ý nghĩa từ khóa bằng hành vi chữ. |
| **6. Ghost Background Hold & Fade** | Ra **`0.50 s`** | `7707653` `t=7.80–8.30 s`: `"không."` giữ `0.58 s` rồi lùi về nền mờ dần trong `0.50 s` ngay dưới câu `"thực ra nó nằm ở những"`. | Thay cho cắt cụt, giữ dư âm thị giác của câu phủ định. |
| **7. Soft Blur-Out / Particle Shatter** | Ra **`0.17–0.42 s`** | `7707653`: `"bạn nghĩ sức mạnh"` blur-out trong `0.17 s` (`t=4.43–4.60 s`); `"góc máy"` blur-out `0.17 s` (`t=44.80–44.97 s`); hook `"mà mọi editor nên thành thạo"` **tan thành hạt (particle shatter)** `0.42 s` (`t=2.83–3.25 s`). | Rất ít `hard cut` chữ đột ngột trên talking head như hồi tháng 08/2026. |

---

## 4. Giải Mã Kỹ Thuật "Slow Text" (Chữ Chậm & Nhịp Thở Mới)

Phân tích đối chiếu `7706183278461570356` (09/11/2026) và `7707653827016674580` (13/11/2026) cho thấy `@__dviet` định nghĩa lại "Slow Text" không phải bằng cách **nói chậm**, mà bằng **6 quy tắc tách nhịp chữ khỏi nhịp nói**:

1. **Giữ cụm câu lâu trên màn hình (`1.5–2.7 s` liên tục vs `1.3 s` cũ):**
   - Trong `7706183`, mỗi ý được thiết kế thành **1 cụm bố cục hoàn chỉnh (2–3 tầng)** và giữ nguyên vị trí trong **`1.5–2.7 s`**:
     - `t=13.08–15.75 s` (**`2.67 s`**): `"mình không còn cảm giác"` → `"thích thú"` (sau lưng) → `"với những sản phẩm mình tạo ra"`.
     - `t=17.08–19.33 s` (**`2.25 s`**): `"những luồng idea"` → `"dần biến thành"` → `"cơn nhức đầu"`.
     - `t=25.63–27.47 s` (**`1.84 s`**): `"tia hy vọng"` → `"đã chiếu tới..."`.
     - `t=49.20–51.80 s` (**`~2.60 s`**): `"mình cũng không chắc sẽ giỏi lên bao nhiêu"`.
     - `t=52.00–54.25 s` (**`2.25 s`**): `"mình chỉ chắc"` → `"một điều"` → `"từ giờ"`.
   - Mắt người xem được **nghỉ tại 1 điểm neo**, không phải đảo mắt liên tục theo 1–2 từ nhấp nháy ở tốc độ `280 WPM`.
2. **Làm chậm pha vào (`0.33–0.45 s`) & pha ra (`0.25–0.50 s`):**
   - Thay `fade 0.08–0.10 s` và `blur_in 0.17 s` bằng đường cong ease mượt (`cubic-bezier(0.22, 1, 0.36, 1)` hoặc `easeInOutSine`) trong **`0.33–0.45 s`**.
   - Đặc biệt hiệu quả khi kết hợp **Opacity `0% → 100%` + Gaussian Blur `16px → 0px` + Glow Bloom `0% → 100%`**.
3. **Chữ đi trước hoặc đồng bộ theo ánh sáng/cảnh, không giật theo từng âm tiết:**
   - Ví dụ `t=25.63 s` (`"tia hy vọng"`): chữ không bật theo nhịp trống, mà **sáng dần theo tốc độ vệt nắng quét qua mặt Việt**.
4. **Xuyên cắt (`Cross-Cut Persistence`):**
   - Giữ cụm chữ sống xuyên qua điểm cắt cảnh (`"cơn nhức đầu"` xuyên cắt `t=19.33 s`; `"những sản phẩm"` xuyên cắt từ cảnh cận máy ảnh sang cảnh toàn hoàng hôn `t=54.83–55.80 s`; `"cái hộp"` xuyên cắt pan cây `t=35.4–36.2 s`). Việc này triệt tiêu cảm giác "cắt gắt" dù vẫn giữ nhịp dựng mạch lạc.
5. **Tách rời hoặc loại bỏ phụ đề `caption` nhấp nháy:**
   - Trong `7706183`, **không có dải caption 1–3 từ bật từng nhịp** ở giữa màn hình; chính **cụm slow text đóng vai trò phụ đề nghệ thuật duy nhất**.
   - Trong `7707653`, tốc độ nói nhanh hơn (`297.2 WPM`) nhưng chữ được đặt cố định ở 1 vùng bên phải/trên card và dùng giải mã mềm / blur-in-out (`0.17–0.50 s`) nên vẫn sạch mắt, không loạn nhịp.
6. **Cân bằng âm lượng dịu hơn ở video hướng dẫn mới (`7707653`):**
   - Trong khi `7706183` giữ `-11.3 LUFS` để đẩy cao trào cảm xúc, `7707653` hạ xuống **`-16.7 LUFS`** (`LRA 2.0 LU`, `True Peak -3.1 dBFS`) — nhẹ tai, ít nén gắt hơn hẳn chuẩn `-10.7..-13.8 LUFS` trước tháng 10/2026.

---

## 5. Đối Chiếu Nhanh: Giữ Nguyên vs Tiến Hóa (Trước 10/2026 → Tháng 11/2026)

| Hạng mục | Hồ sơ cũ (`dviet-style.json`, 17 video T7–T10/2026) | Cập nhật Tháng 11/2026 (`7706183` & `7707653`) | Kết luận |
| :--- | :--- | :--- | :--- |
| **Khung hình & FPS** | `1080×1920` (9:16), `60 fps` | **`1440×1080` (4:3)**, **`24 fps`** (story) / **`30 fps`** (motion graphic) | **Tiến hóa lớn** |
| **Hệ Font** | 3 font: `SF Pro Display` + `Playfair Bold Italic` + `Great Vibes` | **100% Sans-Serif nén ngang** (`scaleX ~0.8`), bỏ Serif & Script | **Tiến hóa lớn** |
| **Kiểu chữ (Case)** | Chữ thường (`lower`) là chủ đạo | **Giữ nguyên 100% `lower`**, tracking âm sâu (`-45..-70`) | **Giữ nguyên & siết chặt** |
| **Bảng màu nhấn** | 1 màu nhấn/video: vàng `#F4C40C`, xanh `#04AC04` | Giữ luật 1 màu nhấn/video; cập nhật **vàng `#E7BC11 / #FAE616`**, **mint-neon `#3EED9C`**, thêm bộ **Light Card `#E6ECD6` + `#347A53`** | **Mở rộng & tinh chỉnh** |
| **Bóng & Ánh sáng** | Drop shadow đen (`#000`, `50%`, `blur 10`) | **Bỏ bóng đen**, chuyển sang **Optical Glow / Halation** + **mờ 4 góc ống kính** | **Tiến hóa lớn** |
| **Vị trí chữ** | Chính giữa ngực (`y=45–65%`) | **Vùng trống âm (trái/phải mặt)**, vòng cung/3D quanh đầu, và **sau chủ thể/vật thể** | **Tiến hóa lớn** |
| **Nhịp chữ & Motion** | `blur_in 0.17 s`, `fade 0.10 s`, `hard swap`, giữ chữ `1.3 s` | **Slow Text**: vào `0.33–0.45 s` (ramp/staggered letter), **giữ `1.5–2.7 s`**, **cross-dissolve/blur-out `0.17–0.50 s`**, xuyên cắt | **Tiến hóa lớn** |
| **Tốc độ nói (WPM)** | Trung vị `287 WPM` | `279 WPM` (`7706183`) / `297 WPM` (`7707653`) | **Giữ nguyên** |
| **Cấu trúc Hook & CTA** | Minh họa trực tiếp kỹ thuật bằng hiệu ứng; CTA cuối rõ | Tiếp tục minh họa ngay hiệu ứng đang nói (`"chồng lên"` xếp lớp, `"vết cắt"` có đường cắt ngang, `"cut"` ở outro) | **Giữ nguyên DNA** |

---

## 6. Bảng Công Thức Tái Tạo (FilmCraft / HyperFrames / CapCut)

### 6.1. Công thức 1 — **Cinematic Slow Text (Kiểu `7706183` — 09/11/2026)**
Dùng cho video kể chuyện, chia sẻ góc nhìn, intro/outro sâu lắng.

| Thành phần | Thông số chuẩn | FilmCraft (`.fcproj`) | HyperFrames (`HTML/CSS/GSAP`) | CapCut |
| :--- | :--- | :--- | :--- | :--- |
| **Canvas & FPS** | `1440×1080` (4:3) hoặc `1080×1920`, **`24 fps`** | Project `1440x1080 @ 24fps` | `<hf-composition width="1440" height="1080" fps="24">` | Tỷ lệ `4:3`, Xuất `24fps` |
| **Font & Tracking** | Sans-serif hình học nén ngang `82%`, tracking `-50`, chữ thường | Font `SF Pro Display` / `Be Vietnam Pro`, `Scale X = 82%`, `Tracking = -50` | `font-family: 'Be Vietnam Pro', sans-serif; transform: scaleX(0.82); letter-spacing: -0.05em; text-transform: lowercase;` | Font tròn/nén (hoặc `Gilroy`/`SVN-Gilroy`), Khoảng cách chữ `-4` đến `-6`, Co ngang |
| **Tỷ lệ 2 tầng** | Dẫn `68–76 px` (`#FFFFFF`), Nhấn `130–145 px` (`#FAE616` / `#E7BC11`) | 2 Text Clips lệch trục (chữ dẫn `72px`, từ khóa `138px`) | `.ctx { font-size: 70px; }` / `.kw { font-size: 138px; color: #FAE616; }` | Cỡ chữ phụ `6–7% H`, từ khóa `12–13% H` |
| **Glow / Halation** | Không drop-shadow đen; Glow cùng màu chữ | `Wonder Glow`: `radius 20`, `intensity 35–45`, `color #FAE616` (chữ trắng: `intensity 15`) | `text-shadow: 0 0 24px rgba(250,230,22,0.55), 0 0 48px rgba(231,188,17,0.28);` | Phát sáng (Glow): Cường độ `25–35`, Phạm vi `35–45` |
| **Slow In (Ramp)** | `0.33–0.42 s`, opacity `0→1`, blur `14px→0` | Keyframe `Opacity 0→100%` + `Gaussian Blur 14→0` trong `8–10 frames` (`0.33–0.42 s`), Ease-out | `gsap.from(el, { opacity: 0, filter: 'blur(14px)', duration: 0.38, ease: 'power2.out' })` | Hoạt ảnh Vào: `Rõ dần (Fade In)` hoặc `Mờ dần vào`, thời lượng **`0.4s`** |
| **Staggered Letter** | `0.30–0.42 s` từng ký tự ngẫu nhiên | Text Animator / tách chữ con lệch `0.025 s/ký tự` | `SplitText` chars + `gsap.from(chars, { opacity: 0, filter: 'blur(8px)', stagger: { each: 0.025, from: 'random' }, duration: 0.25 })` | Hoạt ảnh Vào: `Ngẫu nhiên` / `Xuất hiện từng chữ` đặt `0.4s` |
| **Slow Out / Cross** | Giữ cụm **`1.5–2.7 s`**, ra `0.25–0.35 s` (chồng lên cụm sau) | Chồng đuôi clip cũ `6–8 frames` lên đầu clip mới, keyframe `Opacity 100→0%` + `Blur 0→10` | `gsap.to(prevEl, { opacity: 0, filter: 'blur(10px)', duration: 0.30, ease: 'power1.in' })` | Hoạt ảnh Ra: `Mờ dần (Fade Out)` **`0.3s`**, đặt gối đầu giữa 2 layer |
| **Depth Masking** | Chủ thể/tiền cảnh đè lên từ khóa | `V1` nền gốc → `V2` Text nhấn → `V3` chủ thể tách nền (Matte) → `V4` chữ dẫn nhỏ | CSS `z-index`: `1` bg video, `2` `.kw`, `3` masked foreground `<video>`, `4` `.ctx` | Nhân đôi video gốc lên lớp phủ → `Xóa nền tự động` đè lên layer text nhấn |

### 6.2. Công thức 2 — **Editorial Glow & Motion Cards (Kiểu `7707653` — 13/11/2026)**
Dùng cho video hướng dẫn, giải thích kỹ thuật, giữ chất điện ảnh nhưng nhịp thông tin nhanh hơn (`30 fps`).

| Thành phần | Thông số chuẩn | FilmCraft (`.fcproj`) | HyperFrames (`HTML/CSS/GSAP`) | CapCut |
| :--- | :--- | :--- | :--- | :--- |
| **Bảng màu 2 chế độ** | **Dark**: nền `#072816`, chữ trắng + nhấn `#3EED9C`<br>**Light**: nền `#E6ECD6`, chữ `#347A53` | Solid/Gradient BG + Adjustment Layer Glow (`#3EED9C`) | CSS variables `--bg-dark: #072816; --accent: #3EED9C; --bg-light: #E6ECD6; --ink-light: #347A53;` | Nền gradient xanh rêu thẫm / kem nhạt; chữ xanh mint neon + Phát sáng `30–40` |
| **Watermark Nền Chìm** | Chữ tiếng Việt `280–360 px`, opacity `6–10%`, blur `6 px` | Text Layer sát nền (`V1.5`), `Opacity 8%`, `Gaussian Blur 6px` | `.wm { font-size: 320px; opacity: 0.08; filter: blur(6px); pointer-events: none; }` | Layer chữ lớn sát nền, Độ mờ `8%`, thêm hiệu ứng `Làm mờ 10` |
| **Typewriter Glitch** | `0.50 s` giải mã ký tự + con trỏ `\|` nhấp nháy | Biểu thức/keyframe hiện từng ký tự + shape thanh `\|` nhấp nháy `6Hz` | JS scramble-to-target text over `0.50 s` + CSS blinking cursor `\|` (`#3EED9C`) | Hoạt ảnh Vào: `Máy đánh chữ` / `Giải mã` `0.5s` |
| **Blur-Out Sạch** | Ra `0.17 s` (thay hard cut) | `Gaussian Blur 0→20` + `Opacity 100→0%` trong `5 frames` (`0.17 s` @ 30fps) | `gsap.to(el, { opacity: 0, filter: 'blur(18px)', duration: 0.17 })` | Hoạt ảnh Ra: `Làm mờ` `0.2s` |
| **Peripheral Lens Blur** | Tâm nét `55%`, mờ 4 góc + vignette tối | Adjustment Layer trên cùng: `Radial/Gaussian Blur 18px` + `Inverted Ellipse Mask` (feather `35%`) | `.lens-blur { backdrop-filter: blur(12px); mask-image: radial-gradient(circle at 50% 50%, transparent 45%, black 85%); }` | Hiệu ứng: `Làm mờ viền / Radial Blur` cường độ `25–35`, Mặt nạ tròn đảo ngược làm mờ viền `50` |
