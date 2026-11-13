# kb-dviet-viral-text-audio-edit — toàn văn tài liệu của nguồn `dviet-viral-text-audio-edit`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/dviet-viral-text-audio-edit/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: dviet-viral-text-audio-edit/SKILL.md ===== -->

---
name: dviet-viral-text-audio-edit
description: >-
  Thiết kế Text Effects nghệ thuật theo phong cách kênh TikTok @__dviet ("Việt Mỏi Lưng":
  Multi-Font Overlapping Calligraphy + Sans-Serif, Slide Text Reveal, Overlapping Stroke Text,
  Blend Modes Difference/Overlay, Text Behind Subject + Backlight Halo, Flash Out, Flicker,
  Clone Visual Hook, 3D Fanned Cards) kết hợp chuỗi lọc tạp âm, khử vang và chuẩn hóa giọng nói
  mã nguồn mở (DeepFilterNet, VxStudio, ClearerVoice, Resemble Enhance, Master_Me -14 LUFS)
  trên FilmCraft (.fcproj), EffectCraft (.ecproj) và Premiere Pro / Remotion.
---

# DViet Viral Text Effects & Open-Source Audio Polish — FilmCraft, EffectCraft & Premiere

## 1. Mục tiêu & Quy tắc Bàn giao Bắt buộc

Skill này kết hợp **2 trụ cột nâng cao trình độ dựng video ngắn (9:16, 60fps)**:
1. **Hệ thống Text Effects & Visual Hooks chuẩn `@__dviet` ("Việt Mỏi Lưng") + Editorial 2-Tier Typography:** Biến các đoạn talking-head thông thường thành video có chiều sâu thị giác cao thông qua phối chữ đa tầng (Calligraphy Script đè lên Geometric Sans-Serif Bold), mặt nạ trượt (`Slide Text`), chữ đan xen (`Overlapping Text`), hòa trộn màu (`Blend Modes`), đặt chữ sau đầu người nói (`Text Behind Subject` kèm quầng sáng `Backlight Halo`) và hiệu ứng kết thúc (`Flash Out` / `Flicker` / `Radial Blur`).
2. **Hệ thống Lọc & Tinh chỉnh Âm thanh Mã nguồn mở (Open-Source Dialogue Chain):** Làm sạch tạp âm nền, khử vang phòng, cắt âm xuýt (De-Esser), cắt tần số đục (`235Hz`), nâng độ rõ giọng (`3.4kHz`) và chuẩn hóa độ lớn đạt **`-14 LUFS` (`-1.5 dBTP`)** kết hợp đi SFX giữ nguyên 100% đuôi âm tự nhiên.

> **QUY TẮC BẮT BUỘC KHI DỰNG TRÊN FILMCRAFT / PREMIERE:**
> Sau khi triển khai edit xong trên timeline, **TUYỆT ĐỐI KHÔNG tự động xuất/render ra file video (`.mp4`, `.mov`)** trừ khi người dùng yêu cầu rõ ràng. Luôn lưu và giữ nguyên trạng thái project (`.fcproj`, `.ecproj` hoặc `.prproj`) cùng timeline làm việc đa rãnh (`V1..V6`, `A1..A4`, `C1`) để người dùng trực tiếp kiểm tra, tinh chỉnh và duyệt cuối cùng.

---

## 2. Cấu trúc Timeline 60fps Chuẩn `@__dviet` (Giải phẫu từ `timeline Breakdown`)

Khi dựng sequence dọc `1080×1920` (`60fps`), phân bổ các tầng track như sau:

| Tầng Track | Nội dung trên Track | Kỹ thuật & Preset áp dụng |
| :--- | :--- | :--- |
| **`V6` (Text Layer Top)** | Chữ nhấn bằng **Font Calligraphy Script** (`Great Vibes`, `Pinyon Script`, `Alex Brush`, `Instrument Serif Italic`) | Đặt lệch lên trên `45px–65px`, đè một phần xuống dòng chữ ở `V5`. Áp dụng preset `[DViet] Slide Up Text Reveal + Motion Blur` hoặc `Deep Glow`. |
| **`V5` (Text Layer Main)** | Chữ chính bằng **Font Sans-Serif Bold** (`Plus Jakarta Sans Bold`, `Be Vietnam Pro ExtraBold`, `Anton`) | Ép sát khoảng cách chữ (`tracking: -35` đến `-45`), trượt lên chậm hơn `V6` khoảng `0.06s–0.08s` (staggered reveal). |
| **`V4` (Text Echo / Icons / Cards)** | Lớp chữ viền rỗng (`Overlapping Stroke`), **3D Glass Badges**, hoặc thẻ **UI Glassmorphism** | Dùng asset từ `/home/vmiz/Thanh/Media/TNEDIT/` kết hợp `[MisterHorse] Smooth Pop-In Elastic` hoặc `[DViet] Flash Out & Radial Blur Finisher`. |
| **`V3` (Foreground Subject Cutout / Overlays)** | Lớp người nói đã tách nền (khi làm **Text Behind Subject**) hoặc Overlay `OVL_Flash_Out_Burst_60fps.mp4` (`Screen` blend mode) | Khi làm *Text Behind Subject*: đặt video gốc ở `V1`, đặt `Halo_Purple_Cyber_Backlight.png` + Text ở `V2`, và đặt lớp người tách nền (Alpha Matte) ở `V3`. |
| **`V2` (B-Roll / Vignette / Halos)** | B-roll từ `/home/vmiz/Thanh/Media/TNEDIT/06_B-Roll/Stock_Theo_Chu_De_PR`, hoặc `Overlay_Bottom_Dark_Vignette_9x16.png` | Lớp phủ tối 1/3 dưới khung hình giúp chữ trắng/vàng luôn nổi bật trên áo sáng màu mà không cần viền đen thô. |
| **`V1` (Main A-Roll)** | Video người nói chính (Talking Head) | Punch-in/out `105%–115%` tại từ khóa; gắn LUT điện ảnh (`Dehancer Kodak Vision3 2383` hoặc `FilmConvert Fuji Eterna 250D` ở mức `65%–80%`). |
| **`A1` (Dialogue / Voice)** | Giọng nói chính đã lọc tạp âm & chuẩn hóa | Gắn preset **`[OpenAudio] DeepFilterNet + VxStudio Dialogue Polish`** hoặc chạy `scripts/clean_and_master_voice.py`. |
| **`A2`, `A3` (SFX Tracks)** | Các lớp Sound Effects xếp so le từ `/home/vmiz/Thanh/Media/TNEDIT/02_SFX/Thu_Vien_SFX_PR` | Mỗi lần cụm chữ `Slide Text` / `Icon` / `Card` xuất hiện đều có SFX (`Whoosh`, `Swoosh`, `UI_Click`, `Pop`, `Camera`, `Glitch`) đặt đúng frame đầu, **giữ nguyên 100% đuôi âm**. |
| **`A4` (BGM Music)** | Nhạc nền từ `/home/vmiz/Thanh/Media/TNEDIT/08_Nhac_Nen/BGM_Thu_Vien_PR` | Gắn `[AutoDuck] Smart BGM Ducking Under Voice` (hoặc hạ nền `-22` đến `-25 dB`). |

---

## 3. Bộ Công Cụ Đã Cài Sẵn Trong FilmCraft (`0.13.0`) & EffectCraft (`0.17`)

### 3.1. Trong FilmCraft (`/home/vmiz/.local/share/filmcraft/`)
1. **5 Motion Graphics Templates (`.fcgt`) mới trong bảng `Graphics Templates`:**
   * **`[DViet] Dual-Font Calligraphy + Sans Title`** (`dviet-dual-font-script-title.fcgt`): Phối chữ *Great Vibes* đè lên *Plus Jakarta Sans Bold* (`tracking -45`) đúng chuẩn 16/17 video của `@__dviet` (*Slide text effect*, *first Reel*, *Flicker effect*, *Just do it.*).
   * **`[DViet] Giant Number + 2-Tier Hook (3 Effects)`** (`dviet-giant-number-list-hook.fcgt`): Con số khổng lồ (`3`) bên trái + chữ Script (*Effects* / *Website*) ở tầng trên bên phải + chữ Sans (*for editors*) ở tầng dưới bên phải.
   * **`[DViet] Overlapping Solid + Hollow Stroke Text`** (`dviet-overlapping-stroke-text.fcgt`): 3 lớp chữ đan xen (chữ viền rỗng `stroke` + chữ đặc `solid` + chữ `script` phía dưới) như video *overlapping text* (161.2K views).
   * **`[DViet] Text Behind Subject Header (ep.2)`** (`dviet-behind-head-title.fcgt`): Cụm tiêu đề cỡ lớn đặt ở 1/3 trên khung hình kèm bóng phát sáng tím/xanh để đặt sau đầu người nói.
   * **`[Editorial] 2-Tier Chest Caption (White + Yellow Impact)`** (`mkq-dual-stack-chest-caption.fcgt`): Caption 2 tầng đặt vùng ngực áo (dòng dẫn màu trắng `Be Vietnam Pro Medium` + dòng nhấn IN HOA màu vàng `#FFD600` font `Anton`).
2. **6 Effect Presets mới trong bảng `Effects > Presets` (`effect-presets.json`):**
   * **`[DViet] Slide Up Text Reveal + Motion Blur`**: Trượt chữ từ dưới lên kèm nhòe chuyển động (`Motion Blur 75%`).
   * **`[DViet] Flash Out & Radial Blur Finisher`**: Chớp sáng `Wonder Glow` cường độ cao + `Directional Blur` + thu nhỏ nhẹ khi đóng chữ/cảnh.
   * **`[DViet] Flicker Strobe Visual Hook`**: Tạo hiệu ứng nhấp nháy ánh sáng + tách nhẹ kênh màu RGB (`4.5px`) khi mở đầu.
   * **`[DViet] Floating Rounded Card Frame (PiP)`**: Bo góc video người nói (`Radius 44px`), viền trắng mảnh và đổ bóng sâu (như Pinned Video #1 của `@__dviet`).
   * **`[OpenAudio] DeepFilterNet + VxStudio Dialogue Polish`**: Chuỗi 8 mắt xích xử lý giọng nói dựa trên kiến trúc mã nguồn mở (`Speech Enhance` → `DeNoise` → `DeReverb` → `DeClicker` → `DeEsser 6.4kHz` → `Parametric EQ` cắt 85Hz/235Hz, nâng 3.4kHz/10.5kHz → `Single-band Compressor` → `Hard Limiter -1.5dB`).
   * **`[OpenAudio] Master_Me -14 LUFS Podcast Leveler`**: Tự động giữ đều độ lớn giọng nói theo chuẩn `master_me` (`Tube Compressor` + `Mastering` + `Hard Limiter -1.5dB`).

### 3.2. Trong EffectCraft (`/home/vmiz/.config/effectcraft/`)
* Mở bảng **Window > `DViet & Viral Text VFX Suite.jsx`** (hoặc **File > Scripts > `DViet & Viral Text VFX Suite.jsx`**):
  * **`+ Dual-Font Title`**: Tự động tạo 2 layer chữ (*Great Vibes* + *Plus Jakarta Sans* âm tracking) kèm chuyển động trượt lệch pha (`0.08s`) và `Deep Glow`.
  * **`+ Giant #3 Hook`**: Tạo bố cục 3 layer số lớn + chữ 2 tầng.
  * **`+ Overlapping Echo`**: Tạo cặp chữ chạy ngược chiều đan xen nhau.
  * **`+ Behind Head Rig`**: Tạo cụm chữ tiêu đề phía trên cho kỹ thuật *Text Behind Subject*.
  * **`⬆️ Slide Reveal` / `⚡ Flash Out` / `✨ Flicker Hook`**: Gắn keyframe hiệu ứng chỉ với 1 cú nhấp chuột vào bất kỳ layer nào đang chọn.

---

## 4. Kho Tài Nguyên Mở Rộng Tại `/home/vmiz/Thanh/Media/TNEDIT/`

| Thư mục tài nguyên | Đường dẫn | Chi tiết các Asset mới đã bổ sung |
| :--- | :--- | :--- |
| **1. Bộ Font Calligraphy & Sans-Serif (58 TTF)** | `/home/vmiz/Thanh/Media/TNEDIT/01_Font/Google_Fonts_PR/` + `/home/vmiz/Thanh/Media/TNEDIT/01_Font/Google_Fonts_Style_DViet/` *(và `~/.local/share/fonts/`)* | Đã bổ sung 8 font Script/Calligraphy chuẩn `@__dviet` (**`GreatVibes-Regular.ttf`**, **`PinyonScript-Regular.ttf`**, **`AlexBrush-Regular.ttf`**, **`Allura-Regular.ttf`**, **`DancingScript-Variable.ttf`**, **`Parisienne-Regular.ttf`**, **`Satisfy-Regular.ttf`**, **`Sacramento-Regular.ttf`**) + trọn bộ **`BeVietnamPro`** (`Regular`, `Medium`, `SemiBold`, `Bold`, `ExtraBold`, `Italic`). |
| **2. Bộ Icon Vector & 3D Glass Badges (72 files)** | `/home/vmiz/Thanh/Media/TNEDIT/07_Assets/Icon_Lucide_Glass_Badge/` | • `svg/`: 24 file vector SVG gốc từ Lucide/Unicons (nhập thẳng vào EffectCraft giữ nguyên layer).<br>• `glass_badges_512/`: 24 huy hiệu kính mờ 3D (`BADGE_AI_Sparkles.png`, `BADGE_Chart_Growth.png`, `BADGE_Rocket_Startup.png`, `BADGE_Headphones_SFX.png`...).<br>• `png_512/`: 24 icon trắng phát sáng trên nền trong suốt. |
| **3. Bộ Thẻ UI Glassmorphism & Khung `@__dviet`** | `/home/vmiz/Thanh/Media/TNEDIT/07_Assets/UI_Card_Glassmorphism/` | • `Card_DViet_3D_Fanned_Pocket.png`: Ví kính mờ đựng 3 thẻ xòe quạt (`-8° / 0° / +10°` giống hệt video #13 của `@__dviet`).<br>• `Card_DViet_Floating_Frame_Mask_9x16.png`: Khung nền trắng khoét lỗ bo góc kèm glow tím/xanh (giống Pinned Video #1).<br>• `Overlay_Bottom_Dark_Vignette_9x16.png`: Lớp phủ tối mượt 1/3 dưới khung hình.<br>• `Card_AI_Prompt_Input_Glass.png`, `Card_Before_After_Split_Line.png`, `Card_Social_Comment_Bubble.png`. |
| **4. Quầng Sáng Backlight Halo & Flash 60fps** | `/home/vmiz/Thanh/Media/TNEDIT/03_VFX/Halo_Backlight_Flash/` | • `Halo_Purple_Cyber_Backlight.png`, `Halo_Cyan_Teal_Backlight.png`, `Halo_Warm_Gold_Backlight.png`: Đặt sau lưng người nói khi làm *Text Behind Subject*.<br>• `OVL_Flash_Out_Burst_60fps.mp4`: Video overlay chớp sáng 60fps (hòa trộn `Screen` / `Add`). |

---

## 5. Quy Trình Lọc & Chuẩn Hóa Âm Thanh Bằng Script Tự Động

Trước khi đưa file voice hoặc video gốc vào timeline (hoặc khi cần cứu file thu âm bị ồn, vang, nhỏ tiếng), chạy script đi kèm trong skill:

```bash
python3 ~/.gemini/config/skills/dviet-viral-text-audio-edit/scripts/clean_and_master_voice.py \
  --input "/duong/dan/video_hoac_audio_goc.mp4" \
  --output "/duong/dan/voice_cleaned_14lufs.wav" \
  --mode studio
```

Script này kết hợp chuỗi lọc DSP của `ffmpeg` (Highpass `85Hz` → Spectral Denoise `afftdn` → Mud Cut `235Hz` → De-Esser `6.4kHz` → Presence Lift `3.4kHz` → Air Boost `10.5kHz` → Dynamic Compressor `acompressor` → Chuẩn hóa âm lượng 2-pass **EBU R128 `-14.0 LUFS` / `-1.5 dBTP`**). Ở `--mode studio` / `heavy`, script tự chạy DeepFilterNet trước (`deep-filter` đã cài ở `~/.local/bin`); `--mode light` chỉ dùng bộ lọc `ffmpeg`.

### 5.1. Công cụ mã nguồn mở thật đã cài trên máy (đã chạy thử 2026-10-29)

Đo trên giọng thật trộn ồn hồng + ù 50 Hz (tỉ lệ giọng / ồn trong khoảng nghỉ, càng cao càng sạch): bản ồn 12,6 dB · chỉ bộ lọc `ffmpeg` 12,3 dB · DeepFilterNet 45,2 dB · script trên `--mode studio` 47,0 dB · resemble-enhance `--denoise_only` 44,0 dB · ClearerVoice 55,5 dB.

| Việc | Lệnh | Ghi chú |
| :--- | :--- | :--- |
| Khử ồn AI nhanh (DeepFilterNet3, CPU) | `deep-filter -D voice.wav -o out_dir/` | 20 s âm thanh ≈ 2 s. Đầu vào WAV 48 kHz: `ffmpeg -i in.mp4 -vn -ac 1 -ar 48000 voice.wav`. Ra `out_dir/voice.wav`. |
| Khử ồn + khử vang sạch nhất (ClearerVoice MossFormer2_SE_48K, GPU) | `clearvoice-enhance in.wav out.wav` | 20 s ≈ 30 s. Model cố định ở `~/.local/share/video-ai/clearvoice`. |
| Phục hồi giọng thu kém (resemble-enhance) | `resemble-enhance in_dir/ out_dir/ --device cpu` (thêm `--denoise_only` để chỉ khử ồn) | Bản đầy đủ tổng hợp lại giọng, ra 44,1 kHz; cần > 4,6 GB GPU trống, khi FilmCraft/EffectCraft đang mở thì dùng `--device cpu` (20 s ≈ 100 s). Nghe lại trước khi dùng. |
| Tách giọng khỏi nhạc / SFX (BS-RoFormer, GPU) | `audio-separator in.wav --output_dir out/ --output_format WAV --model_file_dir ~/.cache/audio-separator-models` | 36 s ≈ 27 s; giọng tách ra so với giọng gốc: SNR 11,9 → 23,4 dB. Ra 2 file `(Vocals)` và `(Instrumental)`. |
| Chuẩn hóa −14 LUFS | `ffmpeg-normalize in.wav -nt ebu -t -14 -tp -1.5 -ar 48000 -c:a pcm_s24le -o out.wav` | Tự chuyển sang chế độ động nếu đỉnh vượt −1,5 dBTP (có cảnh báo). |
| Tự cắt khoảng lặng → timeline FilmCraft | `auto-editor in.MP4 --edit audio:threshold=10% --margin 0.15sec --export premiere -o cut.xml --no-open`, rồi mở `cut.xml` bằng FilmCraft | Máy quay ồn nền cao: ngưỡng mặc định 4% không cắt gì → tăng ngưỡng hoặc khử ồn trước. `pr/Soucre/Video/C0009`, `C0010` không có tiếng. |

Chuỗi khuyên dùng cho track `A1`: (tách giọng nếu lẫn nhạc) → `deep-filter` hoặc `clearvoice-enhance` → `ffmpeg-normalize` −14 LUFS → đưa vào FilmCraft.

### 5.2. Text Behind Subject (tách nền người nói)

* `rvm-matte in.mp4 nguoi_alpha.mov` — RobustVideoMatting (GPU) → ProRes 4444 có alpha, đặt trên track chữ trong FilmCraft / EffectCraft. 9 s 1080×1920 ≈ 25 s. Tham số 3 là downsample (0,25 cho 1080p, 0,125 cho 4K).
* Skill `facecammaxxing` (`fcm.py track` rồi `fcm.py render`) dựng sẵn hiệu ứng `text-behind`, `kinetic-caption`, `backdrop-word`… bằng Remotion.
* Footage `pr/Soucre/Video/C00xx.MP4` quay nghiêng (3840×2160, không có thông tin xoay): xoay trước `ffmpeg -i in.MP4 -vf "transpose=1,scale=1080:1920" -c:v libx264 -crf 16 -c:a aac out.mp4`.

<!-- ===== /file: dviet-viral-text-audio-edit/SKILL.md ===== -->
