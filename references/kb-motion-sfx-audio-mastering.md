# kb-motion-sfx-audio-mastering — toàn văn tài liệu của nguồn `motion-sfx-audio-mastering`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/motion-sfx-audio-mastering/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: motion-sfx-audio-mastering/SKILL.md ===== -->

---
name: motion-sfx-audio-mastering
description: >-
  Thiết kế âm thanh (Sound Design), chọn lọc SFX từ kho 2.990+ file (7 nhóm 01-whooshes..07-textures, uisfx-themes, kenney, remotion-sfx), dàn dựng đa rãnh A1–A4 trên Premiere Pro / After Effects, tổng hợp và trộn âm thanh bằng mã Python (dsp.py, synth.py, mixbus.py), dò & dịch cao độ đồng âm giọng La trưởng (cao_do.py), kiểm định chất lượng âm thanh tự động (qa_audio.py) và chuẩn hóa âm lượng EBU R128 / ITU-R BS.1770 (master.py, -16 LUFS / -14 LUFS, -1.5 dBTP). Kích hoạt khi người dùng muốn thiết kế âm thanh cho video motion graphics/quảng cáo, chọn nhạc nền Envato & SFX, chạy script mix/master audio chuẩn LUFS, hoặc kiểm tra lỗi âm thanh.
---

# Motion SFX & Audio Mastering — Thiết Kế Âm Thanh, Phối Trộn Đa Rãnh & Chuẩn Hóa Âm Lượng LUFS

Skill này kết hợp toàn bộ kiến thức **Thiết kế âm thanh (Sound Design)** trên Premiere Pro / After Effects với **Hệ thống xử lý tín hiệu số & Mastering tự động bằng Python (`DSP / Mixbus / EBU R128`)** để tạo ra bản âm thanh trong trẻo, giàu năng lượng và đạt chuẩn phát sóng quốc tế.

---

## Chạy trên máy Linux này

- Python: `~/.venvs/video-skills/bin/python` (máy không có lệnh `python`/`py`; venv có numpy, scipy, matplotlib, opencv, scikit-image, Pillow, fontTools, resvg-py, faster-whisper). Lệnh `python …` trong tài liệu chạy bằng đường dẫn này.
- ffmpeg/ffprobe 8.1 ở `~/.local/bin` (libx264, FFV1, ProRes 4444, loudnorm, ebur128).
- Đường dẫn Windows trong tài liệu đã đổi sang Linux: `F:\` → `/media/vmiz/Over Powers/`, `D:\` → `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/` (bản sao lưu ổ D ngày 2026-10-28). Ổ USB `Over Powers` phải đang gắn. `E:\` không có trên máy; tài nguyên thay thế ở `/home/vmiz/Thanh/Media/TNEDIT/` (`02_SFX`, `08_Nhac_Nen`, `01_Font`, `06_B-Roll`…).
- Kho 2.995 SFX (gốc của đường dẫn tương đối trong `data/kho_sfx_do.csv`): `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx`. `master.py` đã chạy thử ra đúng −16,0 LUFS (2026-10-29). `transcribe.py` chạy faster-whisper bằng CPU.

---

## 1. Cấu Trúc Thư Mục Trong Skill

- **`references/`** — Sổ tay hướng dẫn đặt âm thanh và nghiên cứu kỹ thuật:
  - `references/HUONG-DAN-DAT-AM-THANH.md`: Quy trình dàn dựng đa rãnh (`A1..A4`), cách căn đỉnh sóng âm (*Waveform Peak Alignment*) khớp với khung hình chuyển động.
  - `references/NHAC-NEN-ENVATO-VA-SFX.md`: Hướng dẫn chọn nhạc nền thương mại (Envato Elements) theo tâm trạng kịch bản, cách cắt nối nhạc theo khuông nhịp (*Beat Grid*) và xử lý Ducking khi có giọng đọc.
  - `references/HUONG-DAN-UI-POP.md`: Cẩm nang sử dụng bộ âm thanh giao diện **UI Pop / Click / Tick / Chime / Notification** cho các cảnh thao tác phần mềm, khung chat và bảng điều khiển.
  - `references/README-KHO-SFX-2990.md`: Bản đồ phân loại kho **2.990+ file SFX** (chia thành 7 nhóm `01-whooshes` đến `07-textures`, `uisfx-themes`, `kenney`, `remotion-sfx`) kèm quy tắc chọn nhanh 20 file tủ.
  - `references/nghien-cuu-decibel.md`: Nghiên cứu chuyên sâu về tiêu chuẩn âm lượng quốc tế **ITU-R BS.1770 / EBU R128**, lý giải sự khác biệt giữa `dBFS`, `True Peak (dBTP)` và `Integrated Loudness (LUFS)`.
- **`data/kho_sfx_do.csv`** — Bảng thông số đo đạc (`max_dBFS`, `mean_dBFS`, `peak_offset_ms`, `duration`) của kho SFX.
- **`scripts/`** — Công cụ đo cao độ, bóc băng và chuẩn hóa âm lượng tổng:
  - `scripts/master.py`: Chuẩn hóa âm lượng cuối cùng bằng bộ lọc `ffmpeg loudnorm` hai lượt (*Two-pass EBU R128*) về đúng **`-16.0 LUFS`** (hoặc `-14.0 LUFS`), giới hạn đỉnh thực **`-1.5 dBTP`**.
  - `scripts/cao_do.py`: Phân tích tần số cơ bản (`f0` bằng biến đổi tự tương quan / FFT) của từng mẫu âm thanh và dịch cao độ (`pitch shift`) về đúng các bậc hợp âm **La trưởng (`A Major`: `A - C# - E`)** để các tiếng chuông/pop vang lên hòa quyện như một bản nhạc.
  - `scripts/transcribe.py`: Bóc băng giọng đọc lấy mốc thời gian từng từ (`word-level timestamps`) để đặt hiệu ứng hình ảnh và SFX khớp miệng người nói.
- **`scripts/audio/`** — Bộ công cụ DSP & Mixbus lập trình bằng Python (`dsp.py`, `dsp_loud.py`, `dsp_sweep.py`, `synth.py`, `mixbus.py`, `mux.py`, `sonic_logo.py`, `sfx_catalog.py`, `qa_audio.py`, `qa_audio_checks.py`, `score_agent.py`, `score_v2.py`, `score_v3.py`, `score_thumon_build.py`).

---

## 2. Bản Đồ 7 Nhóm Âm Thanh SFX & Quy Tắc Chọn File Chuẩn

Khi lấy âm thanh từ kho SFX (`references/README-KHO-SFX-2990.md`), phân bổ đúng vai trò cho từng nhóm:
1. **`01-whooshes` (Gió lướt / Chuyển cảnh):** Dùng cho lia máy quay nhanh (*Whip-pan*), thẻ lớn bay vào/ra. Lưu ý đặt sớm **`80ms – 150ms` trước frame cắt cảnh** để đỉnh sóng gió rơi đúng vào điểm chuyển hình.
2. **`02-pops-clicks` (Bật nảy / Nhấp chuột):** Dùng cho nút bấm, huy hiệu bật lên (*Scale Pop*), con trỏ chuột click.
3. **`03-chimes-bells` (Chuông sáng / Thành công):** Dùng khi hoàn thành tác vụ, hiện dấu tích xanh (`Success`), hoặc khóa logo cuối bài (*Sonic Logo*).
4. **`04-risers-drops` (Tụ lực / Bùng nổ):** Dùng ở cuối đoạn dẫn nhập (trước khi giải pháp xuất hiện) để đẩy cảm xúc lên cao trào.
5. **`05-impacts-booms` (Va chạm trầm):** Dùng cho nhịp dậm chân của linh vật 3D hoặc chữ tiêu đề lớn đập xuống mặt sàn.
6. **`06-typing-data` (Gõ phím / Dữ liệu chạy):** Dùng khi dòng chữ đang gõ trong ô chat hoặc con số đang nhảy tăng trưởng.
7. **`07-textures-ambience` (Không gian nền):** Lớp âm thanh phòng nhẹ nhàng tạo chiều sâu không gian.

---

## 3. Phân Tầng Âm Lượng Chuẩn Công Nghiệp (`Mix Hierarchy`)

Để bản phối trong trẻo, giọng đọc rõ từng chữ và hiệu ứng SFX không đè lấp nội dung, tuân thủ nghiêm ngặt tháp âm lượng sau:

| Tầng âm thanh | Mức mục tiêu (Target Level) | Xử lý EQ / Dynamics bắt buộc |
|---|---|---|
| **1. Giọng đọc chính (Voiceover - `A1`)** | **`-14 LUFS` đến `-16 LUFS`** (Đỉnh `-3 dBTP`) | Cắt tần số ù dưới `85 Hz` (*High-pass*), nén nhẹ tỷ lệ `3:1`, khử âm xuýt (*De-esser* tại `6–8 kHz`). |
| **2. SFX Điểm nhấn chính (Transition / Hero Pop - `A2`)** | **`-12 dBFS` đến `-16 dBFS`** (hoặc `-6.5 dB` đến `-8.0 dB` trong AE khi chưa có Voice) | Lọc mềm dải cao chói trên `11 kHz` cho tiếng Whoosh; giữ nguyên 100% đuôi vang tự nhiên. |
| **3. SFX Vi tương tác (UI Click / Typing - `A3`)** | **`-18 dBFS` đến `-24 dBFS`** | Đặt lệch kênh trái/phải nhẹ (`Pan ±15%`) theo vị trí vật thể trên màn hình. |
| **4. Nhạc nền (Background Music - `A4`)** | **`-18 LUFS`** (khi không có giọng đọc) / Hạ xuống **`-26 dBFS` đến `-28 dBFS`** (khi có giọng đọc) | Sidechain Ducking tự động hạ `8–10 dB` mỗi khi có giọng nói và cắt nhẹ vùng tần số `1.5 kHz – 3.5 kHz` để nhường chỗ cho giọng người. |

---

## 4. Quy Trình Phối Trộn, Kiểm Định (`qa_audio.py`) & Mastering Tự Động (`master.py`)

```bash
# 1. Dò và đồng bộ cao độ SFX về giọng chuẩn (nếu cần phối theo hợp âm thương hiệu)
python scripts/cao_do.py

# 2. Chạy chuẩn hóa âm lượng tổng 2 lượt (Two-pass EBU R128 Loudnorm)
python scripts/master.py input_raw.wav output_mastered.wav --lufs -16.0 --tp -1.5

# 3. Kiểm định tự động bản âm thanh (kiểm tra clipping, khoảng lặng chết, lệch pha, sai chuẩn LUFS)
python scripts/audio/qa_audio.py output_mastered.wav
```

<!-- ===== /file: motion-sfx-audio-mastering/SKILL.md ===== -->

<!-- ===== file: motion-sfx-audio-mastering/references/HUONG-DAN-DAT-AM-THANH.md ===== -->

# Hướng dẫn SFX cho OPA Intro

Video chuẩn: 25 giây, 25 FPS.

## Cách nhanh nhất

Import `00_ALL-SFX-SYNCED_25s.wav` vào Premiere, kéo xuống track A2 và đặt đầu file đúng tại `00:00:00:00`.

File này đã ghép và canh sẵn toàn bộ SFX theo video. Sau đó đặt nhạc nền trên A1. Nếu SFX hơi lớn, giảm toàn bộ clip xuống khoảng `-3 dB` đến `-6 dB`.

## Các file riêng để tự chỉnh

| Số | Tên file | Đặt đầu file tại | Điểm animation chính | Công dụng |
|---:|---|---:|---:|---|
| 01 | `01_01.32_logo-chime.mp3` | 1.15s | 1.32s | Thanh thương hiệu/logo hiện lên |
| 02 | `02_03.76_title-whoosh.mp3` | 3.55s | 3.76s | Dòng tiêu đề xuất hiện |
| 03 | `03_05.16_cards-whoosh.mp3` | 4.92s | 5.16s | Các thẻ giao diện bay vào |
| 04 | `04_05.16_cards-pop.mp3` | 5.12s | 5.16s | Nhấn lúc các thẻ dừng lại |
| 05 | `05_07.52_star-chime.mp3` | 7.35s | 7.52s | Biểu tượng sao xuất hiện |
| 06 | `06_09.60_main-ui-impact.mp3` | 9.00s | 9.60s | Giao diện chính vào giữa màn hình |
| 07 | `07_11.60_gallery-whoosh.mp3` | 11.35s | 11.60s | Cụm giao diện di chuyển |
| 08 | `08_13.20_ai-network-impact.mp3` | 12.60s | 13.20s | Mạng AI OPA xuất hiện |
| 09 | `09_16.88_transition-build.mp3` | 11.34s | 16.88s | Build dài dẫn tới chuyển cảnh |
| 10 | `10_18.12_ai-network-impact.mp3` | 17.50s | 18.12s | Mạng AI xuất hiện lần hai |
| 11 | `11_20.16_grid-whoosh.mp3` | 19.92s | 20.16s | Lưới giao diện bay vào |
| 12 | `12_20.16_grid-pop.mp3` | 20.12s | 20.16s | Nhấn khi lưới giao diện dừng |
| 13 | `13_23.48_ending-chime.mp3` | 23.30s | 23.48s | Câu kết xuất hiện |

## Bố trí track

- A1: nhạc nền.
- A2: file `00_ALL-SFX-SYNCED_25s.wav`, hoặc các whoosh.
- A3: impact và pop nếu dùng file riêng.
- A4: chime nếu dùng file riêng.

Không dùng đồng thời file `00_ALL-SFX-SYNCED_25s.wav` và cả 13 file riêng, vì âm thanh sẽ bị nhân đôi.

<!-- ===== /file: motion-sfx-audio-mastering/references/HUONG-DAN-DAT-AM-THANH.md ===== -->

<!-- ===== file: motion-sfx-audio-mastering/references/HUONG-DAN-UI-POP.md ===== -->

# UI Pop Pack cho OPA Intro

Import toàn bộ 9 file MP3 trong thư mục này vào Premiere và nghe thử bằng cách nhấp đúp từng file trong Project panel.

| Số | File | Dùng cho | Mốc phù hợp trong OPA Intro |
|---:|---|---|---|
| 01 | `01-quick-pop.mp3` | Card, badge hoặc UI bật lên | 5.16s hoặc 20.16s |
| 02 | `02-crisp-ui-click.mp3` | Nút, toggle, icon được chọn | Đặt đúng frame của hành động nhỏ |
| 03 | `03-soft-ui-click.mp3` | Click nhẹ cho nhiều card liên tiếp | Các chuyển động phụ quanh 9.60-11.60s |
| 04 | `04-key-press.mp3` | Text/terminal hoặc ký tự xuất hiện | Quanh 3.76s nếu muốn nhấn dòng chữ |
| 05 | `05-electronic-ping.mp3` | Điểm dữ liệu hoặc icon quan trọng | 7.52s |
| 06 | `06-notification-ui.mp3` | Toast, thông báo, khung UI hiện lên | 9.60s, để âm lượng nhỏ |
| 07 | `07-soft-chime.mp3` | Xác nhận thành công hoặc đoạn kết | 23.48s |
| 08 | `08-sparkle-ui.mp3` | Logo, ánh sáng hoặc biểu tượng sao | 1.32s hoặc 7.52s |
| 09 | `09-digital-glitch-ui.mp3` | Chuyển cảnh công nghệ mạnh | 13.20s hoặc 18.12s |

## Gợi ý tối giản

Đừng dùng cả 9 âm thanh cùng lúc. Bản phối sạch cho video 25 giây chỉ cần:

- 08 tại 1.32s.
- 01 tại 5.16s.
- 05 tại 7.52s.
- 06 hoặc 01 tại 9.60s.
- 09 tại 13.20s.
- 07 tại 23.48s.

Đặt mỗi file trên A3 hoặc A4. Mức âm lượng khởi đầu: `-14 dB` đến `-9 dB`; riêng glitch khoảng `-16 dB` đến `-12 dB` để không lấn nhạc nền.

Các file nguồn được giải quyết từ thư viện media-use chỉ dùng CC0/CC BY. Không có `CREDITS.md` được tạo cho lần lấy này, nên không có mục CC BY riêng cần chép thêm vào phần mô tả video.

<!-- ===== /file: motion-sfx-audio-mastering/references/HUONG-DAN-UI-POP.md ===== -->

<!-- ===== file: motion-sfx-audio-mastering/references/NHAC-NEN-ENVATO-VA-SFX.md ===== -->

# OPA Intro - Music và SFX cho Premiere Pro

## Nhạc nền đề xuất

Lựa chọn chính: **AI Technology Promo Corporate** của SERGMARU trên Envato Elements.

- Link: https://elements.envato.com/ai-technology-promo-corporate-YUZX46A
- Tải phiên bản `AI_Technology_Promo_Corporate_short` dài 0:30.
- Ưu tiên file WAV; MP3 320 kbps cũng dùng được.
- Cắt còn 25 giây và fade-out từ khoảng 24:00 tới 25:00.
- Mức âm lượng khởi đầu: -18 dB đến -14 dB.
- Khi tải, đăng ký giấy phép Envato cho dự án OPA và giữ file license.

Lựa chọn thay thế: **Futuristic Technology Presentation - Inspiring AI Innovation Digital Background**.

- Link: https://elements.envato.com/futuristic-technology-presentation-inspiring-ai-in-GJPMM7L
- Có sẵn bản 30 giây, không có vocal.

## SFX đã chuẩn bị sẵn

Import toàn bộ thư mục `SFX-PREMIERE` vào Premiere:

1. `01-short-ui-whoosh.mp3` - chuyển động nhanh, thẻ giao diện bay vào.
2. `02-ui-pop-click.mp3` - nút, icon hoặc UI bật lên.
3. `03-tech-bass-impact.mp3` - cảnh chính xuất hiện hoặc chuyển cảnh lớn.
4. `04-cinematic-whoosh-build.mp3` - đoạn build/chuyển cảnh dài.
5. `05-digital-sparkle-chime.mp3` - logo, ngôi sao hoặc câu kết.

Các file này được lấy từ thư viện SFX đi kèm quy trình media-use. Nguồn resolver chỉ sử dụng CC0/CC BY; không có file `CREDITS.md` được tạo cho bộ này, nghĩa là không có mục CC BY cần chép thêm từ lần resolve này.

## Bảng đặt âm thanh

| Mốc | Track | File | Cách đặt |
|---|---|---|---|
| 00:00:01:08 | A4 | 05-digital-sparkle-chime.mp3 | Đỉnh chime trùng lúc thanh thương hiệu hiện rõ |
| 00:00:03:19 | A2 | 01-short-ui-whoosh.mp3 | Bắt đầu trước chữ khoảng 3-4 frame |
| 00:00:05:04 | A2 + A3 | 01-short-ui-whoosh.mp3 + 02-ui-pop-click.mp3 | Whoosh dẫn vào, pop trùng lúc thẻ dừng |
| 00:00:07:13 | A4 | 05-digital-sparkle-chime.mp3 | Để nhỏ, chỉ nhấn biểu tượng sao |
| 00:00:09:15 | A3 | 03-tech-bass-impact.mp3 | Đỉnh bass trùng lúc giao diện chính vào giữa |
| 00:00:11:15 | A2 | 01-short-ui-whoosh.mp3 | Canh theo hướng di chuyển của cụm giao diện |
| 00:00:13:05 | A3 | 03-tech-bass-impact.mp3 | Đỉnh hit trùng lúc mạng AI OPA hiện hoàn chỉnh |
| 00:00:16:22 | A2 | 04-cinematic-whoosh-build.mp3 | Cắt bớt đầu; đặt đỉnh swell tại Marker |
| 00:00:18:03 | A3 | 03-tech-bass-impact.mp3 | Bản sao nhỏ hơn khoảng 3 dB |
| 00:00:20:04 | A2 + A3 | 01-short-ui-whoosh.mp3 + 02-ui-pop-click.mp3 | Whoosh cho lưới; pop cho thời điểm dừng |
| 00:00:23:12 | A4 | 05-digital-sparkle-chime.mp3 | Ending chime, fade tự nhiên tới cuối |

## Bố trí track trong Premiere

- A1: nhạc nền.
- A2: whoosh và riser.
- A3: impact, bass hit và UI pop.
- A4: sparkle/chime.

Không nhất thiết phải dùng đủ mọi cue. Nếu video nghe quá dày, giữ các cue chính tại 01:08, 05:04, 09:15, 13:05, 18:03 và 23:12.

Mức âm lượng gợi ý: whoosh/pop -12 đến -8 dB, impact -10 đến -6 dB, sparkle -14 đến -10 dB. Master không vượt quá -1 dB.

<!-- ===== /file: motion-sfx-audio-mastering/references/NHAC-NEN-ENVATO-VA-SFX.md ===== -->

<!-- ===== file: motion-sfx-audio-mastering/references/README-KHO-SFX-2990.md ===== -->

# Thư Viện Sound Effects (SFX) cho Animation & Motion Graphics

Thư mục này chứa **2.990+ file âm thanh** (`.wav`, `.mp3`, `.ogg`) hoàn toàn miễn phí bản quyền (CC0 / MIT / Studio Synth 48kHz), đã được phân loại sẵn theo **7 nhóm chuyển động cốt lõi** và **4 bộ Pack gốc**.

---

## 1. Các Thư Mục Phân Loại Nhanh (Dùng Ngay Theo Chuyển Động)

| Thư mục | Số file | Công dụng & Các file tiêu biểu |
| :--- | :---: | :--- |
| [`01-whooshes-transitions/`](./01-whooshes-transitions/) | **30** | **Chuyển động & Chuyển cảnh:** `whoosh-cut-fast.wav`, `whoosh-cut-medium.wav`, `whoosh-light-airy.wav`, `whoosh-deep-windup.wav`, `paper-slide-transition.wav`, `card-flap-swish.wav`, `fast-forward-whirr-sweep.wav`, `remotion-whoosh.wav`, `remotion-whip.wav`, cùng các bộ `swipe`, `expand`, `collapse` đa chất liệu. |
| [`02-impacts-hits/`](./02-impacts-hits/) | **34** | **Va chạm, Điểm dừng & Logo Slam:** `impact-cinematic-accent.wav`, `impact-deep-logo.wav`, `sub-drop-heavy.wav`, `sub-drop-clean-logo.wav`, `thump-body-punch.wav`, `heavy-thock-chime-save.wav`, `heavy-slam-combo.wav`, `remotion-vine-boom.wav`, và các tiếng va chạm chất liệu từ Kenney/UISFX. |
| [`03-pops-snaps-elastic/`](./03-pops-snaps-elastic/) | **73** | **2D Explainer, Nảy (Bounce) & Co giãn:** `pop-bubble-low-A4.wav`, `pop-bubble-mid-C#5.wav`, `pop-bubble-high-E5.wav`, `pop-eject-block.wav`, `catch-bounce-dry.wav`, `catch-hollow-tock.wav`, `catch-bright-ring.wav`, `elastic-boing-low.wav`, `elastic-boing-high.wav`, cùng các tiếng `snap`, `pluck`, `bong`, `drop`. |
| [`04-ui-tech-hud/`](./04-ui-tech-hud/) | **88** | **Giao diện UI, App Promo & Infographic:** `ui-tick-crisp-E6.wav`, `ui-card-snap-dock.wav`, `ui-row-scroll-tick.wav`, `ui-lock-latch-fix.wav`, `ui-wood-marimba-tick.wav`, `ui-swish-accent-tick.wav`, `ui-chime-question-bell.wav`, `hud-data-scan-1.2s.wav`, `remotion-mouse-click.wav`, `remotion-ui-switch.wav`, `remotion-ding.wav`... |
| [`05-risers-builders/`](./05-risers-builders/) | **27** | **Dẫn dắt & Cao trào (Tension / Build-up):** `riser-noise-short-0.6s.wav`, `riser-noise-medium-1.2s.wav`, `riser-noise-long-2.0s.wav`, `swell-tonal-brass-1.0s.wav`, `swell-tonal-brass-1.6s.wav`, `downlifter-sub-sweep-1.5s.wav`, cùng các hiệu ứng `level-up`, `achievement`, `wake`. |
| [`06-glitch-scifi/`](./06-glitch-scifi/) | **53** | **Nhiễu kỹ thuật số & Sci-Fi / Cyber:** `glitch-digital-stutter-1.wav`, `glitch-digital-stutter-2.wav`, `glitch-micro-artifact.wav`, `remotion-loading-lag.wav`, `remotion-record-scratch.wav`, cùng bộ `scanning`, `processing`, `forceField`, `laser`, `computerNoise`. |
| [`07-textures-drones-foley/`](./07-textures-drones-foley/) | **26** | **Âm nền (Drone), Chất liệu & Foley:** `drone-cinematic-dark-4s.wav`, `texture-vinyl-crackle-3s.wav`, `sonic-logo-brass-chord.wav`, `sonic-logo-fifth-interval.wav`, `remotion-page-turn.wav`, `remotion-shutter-modern.wav`, `remotion-shutter-old.wav`, tiếng giấy/vải/kim loại (`book`, `cloth`, `metal`). |

---

## 2. Các Bộ Thư Viện Gốc Đầy Đủ Trong [`packs/`](./packs/)

Nếu bạn muốn duyệt toàn bộ các biến thể đồng bộ theo từng phong cách (Theme/Style), hãy mở thư mục [`packs/`](./packs/):

1. **[`packs/remotion-sfx/`](./packs/remotion-sfx/) (32 file WAV)**
   * Bộ âm thanh chính thức của `@remotion/sfx` (`whoosh.wav`, `whip.wav`, `page-turn.wav`, `switch.wav`, `mouse-click.wav`, `shutter-modern.wav`, `ding.wav`, v.v.).
2. **[`packs/uisfx-themes/`](./packs/uisfx-themes/) (1.872 file MP3 & OGG — MIT License)**
   * Gồm **12 chủ đề âm thanh đồng nhất**: `cinematic`, `minimal`, `rubber`, `glass`, `mechanical`, `organic`, `scifi`, `soft`, `studio`, `dreamy`, `zen`, `arcade`.
   * Mỗi chủ đề có đủ **78 hành động chuyển động**: `swipe`, `snap`, `drop`, `drag-start`, `expand`, `collapse`, `hover`, `press`, `release`, `toggle-on`, `toggle-off`, `scanning`, `processing`, `notification`, `success`, `error`, `typing`, `unlock`, v.v.
3. **[`packs/kenney-ui-wav/`](./packs/kenney-ui-wav/) (51 file WAV — CC0 Public Domain)**
   * Toàn bộ gói Kenney UI Audio chất lượng gốc `.wav` (`click1..5`, `mouseclick1`, `mouserelease1`, `rollover1..6`, `switch1..38`).
4. **[`packs/kenney-complete/`](./packs/kenney-complete/) (700+ file OGG — CC0 Public Domain)**
   * 9 gói âm thanh chuyên biệt từ Kenney:
     * `kenney_interface-sounds` (UI clicks, plucks, toggles, glitches, confirmations)
     * `kenney_impact-sounds` (va chạm vật lý: kim loại, gỗ, kính, bước chân, cú đấm)
     * `kenney_digital-audio` (chuyển động điện tử, zap, phase jump, powerup)
     * `kenney_sci-fi-sounds` (công nghệ tương lai, laser, thruster, force field)
     * `kenney_rpg-audio` (foley tự nhiên: lật sách, vải sột soạt, kim loại, cửa gỗ)
     * `kenney_casino-audio` (tiếng chia bài, trượt thẻ `card-fan`, `card-place`, `card-shove` — cực hợp cho UI Card animation)
     * `kenney_music-jingles` & `kenney_voiceover-pack`

<!-- ===== /file: motion-sfx-audio-mastering/references/README-KHO-SFX-2990.md ===== -->

<!-- ===== file: motion-sfx-audio-mastering/references/nghien-cuu-decibel.md ===== -->

Ngày 22/10/2026 · Nghiên cứu mức decibel cho âm thanh phim 3D "Thủ môn" (21 s, 16:9, 60 fps, không lời) · Soạn: Claude Code (Opus 5.5)

Phạm vi: chỉ tra cứu và tổng hợp, không sửa file nào khác. Số "hiện tại" của phim lấy từ `docs/film3d/g6-am-thanh.md` (bản 2) và từ một lần đo lại chỉ đọc ngày 22/10 trên `out/thu-mon-3d-16x9-ban2/thu-mon-3d_16x9_ban2.mp4` (ffmpeg `ebur128=peak=true`).

**Nhãn nguồn dùng trong báo cáo**

- **[CT]** tài liệu chính thức: ITU, EBU, ATSC, trang trợ giúp của nền tảng, datasheet, bằng sáng chế.
- **[NC]** bài nghiên cứu khoa học.
- **[TC]** nguồn thứ cấp: bài của kỹ sư uy tín, hoặc bản tóm tắt tài liệu AES. Trang aes.org chặn truy cập tự động (lỗi 403), nên tôi không mở được bản gốc TD1004, TD1008.
- **[ĐO]** đo thực nghiệm của bên thứ ba, không phải tài liệu chính thức.
- **[TÍNH]** tôi tự tính từ công thức hoặc hệ số trong nguồn.
- **[SL]** suy luận của tôi, chưa có nguồn chuẩn. Đây là điểm xuất phát để nghe thử, không phải số chuẩn.
- **"chưa tìm được nguồn"**: đã tìm nhưng không thấy nguồn đáng tin.

---

## 0. Bảng số chính

| Mục | Số | Nguồn |
|---|---|---|
| EBU R 128 (phát sóng) | Đích −23,0 LUFS. Dung sai ±1,0 LU khi không đạt được, ví dụ chương trình trực tiếp; ±0,2 LU cho sai số đo ở khâu QC. True peak ≤ −1 dBTP (sai số đo ±0,3 dB). Đo cả chương trình, không đo riêng lời, nhạc hay SFX | [CT] [R 128 v5.0, 2023](https://tech.ebu.ch/files/live/sites/tech/files/shared/r/r128v5_0.pdf) |
| EBU R 128: LRA | Không khuyên dùng LRA cho chương trình ngắn hơn 1 phút | [CT] như trên, chú thích 2 |
| EBU R 128 s1 (quảng cáo, promo, tối đa khoảng 2 phút) | −23,0 LUFS. Max Short-term ≤ −18,0 LUFS (+5,0 LU so với đích). TP ≤ −1 dBTP. LRA không áp dụng | [CT] [R 128 s1, 2020](https://tech.ebu.ch/docs/r/r128s1.pdf) |
| EBU R 128 s2 (streaming) | Phát nguyên −23 LUFS. Nếu không dùng metadata, mức phát tạm thời là −20 đến −16 LUFS | [CT] [R 128 s2 v3.0, 2023](https://tech.ebu.ch/files/live/sites/tech/files/shared/r/r128s2v3_0.pdf) |
| EBU Tech 3343 / 3344 (codec nén) | Codec MPEG-1 L2, AC-3: TP ≤ −2 dBTP. Đặt limiter −2 dBTP trước encoder, hạ thấp hơn nếu bitrate thấp | [CT] [Tech 3343](https://tech.ebu.ch/docs/tech/tech3343.pdf), [Tech 3344](https://tech.ebu.ch/docs/tech/tech3344.pdf) |
| ATSC A/85:2013 (truyền hình Mỹ) | Đích −24 LKFS. Chênh khoảng ±2 dB do sai số đo là chấp nhận được. TP < −2 dBTP | [CT] [A/85:2013](https://www.atsc.org/wp-content/uploads/2025/06/A85-2013-with-Corrigendum-No-1.pdf) |
| AES TD1004 (2015) | Cửa sổ −16 đến −20 LUFS, TP −1 dBTP | [TC] [Production Expert](https://www.production-expert.com/home-page/2015/11/17/aes-release-recommendations-for-loudness-of-audio-streaming-and-network-file-playback) |
| AES TD1008 (2021, thay TD1004) | Nhạc −16 LUFS. Lời và nội dung hỗn hợp −18 LUFS. Quảng cáo, trailer −18 LUFS. TP ≤ −1 dBTP ở đầu vào codec. Không dành cho âm kèm hình | [TC] [Production Advice](https://productionadvice.co.uk/td1008/), [Production Expert](https://www.production-expert.com/production-expert-1/aes-update-loudness-recommendations-for-audio-only-streaming), [trích §4, §7B](https://raw.githubusercontent.com/M-Igashi/baken/main/docs/true-peak-ceiling.md) |
| Spotify | Normal −14, Loud −11, Quiet −19 LUFS. Chuẩn hóa cả lên lẫn xuống. Khuyên master −14 LUFS, TP ≤ −1 dBTP; master to hơn −14 thì TP ≤ −2 dBTP | [CT] [Spotify for Artists](https://support.spotify.com/us/artists/article/loudness-normalization/) |
| YouTube | Mốc khoảng −14 LUFS từ 2019. Chỉ hạ bản to, không nâng bản nhỏ | [ĐO] [Ian Shepherd, MeterPlugs 2019](https://www.meterplugs.com/blog/2019/09/18/youtube-changes-loudness-reference-to-14-lufs.html) |
| YouTube "Stable volume" | Bật mặc định. Liên tục chỉnh mức để thu hẹp chênh lệch to nhỏ | [CT] [YouTube Help](https://support.google.com/youtube/answer/14106294?hl=en) |
| Facebook, Instagram (Reels, Stories) | Chuẩn hóa ở app bằng metadata xHE-AAC (MPEG-D DRC). App tự đặt đích theo ngữ cảnh. Meta không công bố số LUFS | [CT] [Meta Engineering 2023](https://engineering.fb.com/2023/04/11/video-engineering/high-quality-audio-xhe-aac-codec-meta/) |
| TikTok | chưa tìm được nguồn chính thức. Blog bên thứ ba ghi −13 đến −14 LUFS, không kèm phép đo | — |
| Đồng bộ: ITU-R BT.1359 | Ngưỡng nhận ra: âm sớm 45 ms, âm trễ 125 ms. Ngưỡng chấp nhận: sớm 90 ms, trễ 185 ms. Chuỗi phát sóng: sớm ≤ 22,5 ms, trễ ≤ 30 ms | [CT] [BT.1359](https://itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.1359-0-199802-S!!PDF-E.pdf) |
| Đồng bộ: EBU R37 | Mỗi khâu: âm sớm ≤ 5 ms, trễ ≤ 15 ms. Từ đầu đến cuối: sớm ≤ 40 ms, trễ ≤ 60 ms | [CT] [R37-2007](https://tech.ebu.ch/docs/r/r037.pdf) |
| Đồng bộ: ATSC IS-191 | Đầu vào encoder: âm sớm ≤ 15 ms, trễ ≤ 45 ms | [TC] [TV Technology 2004](https://tvtechnology.com/opinions/atsc-recommends-av-sync-rules) |
| Đồng bộ: tiếng va kiểu clapperboard | Điểm nghe như trùng nhau: âm trễ 32–39 ms. Không nhận ra lệch khi âm trễ từ 1,7 đến 75,8 ms. Khuyên âm trễ 0–80 ms, không để âm sớm | [NC] [Heide & Maempel, Tonmeistertagung 2010](https://www.simpk.de/fileadmin/user_upload_sim/Dokumente/Forschung/Themen/Abteilung_III/Publikationen/Heide_Maempel_2011_Die_Wahrnehmung_audiovisueller_Synchronitaet_in_elektronischen_Medien.pdf) |
| Loa điện thoại | Loa linh kiện 11×15 mm cho smartphone cộng hưởng ở 800 Hz ±10 % (hộp sau 1 cm³) | [CT] [Datasheet Knowles](https://cdn.eicom.ru/media/PDF/440124.pdf) |

---

## 1. Đơn vị

### 1.1 Các đơn vị đo

| Đơn vị | Nghĩa | Cần nhớ | Nguồn |
|---|---|---|---|
| **dBFS** | Mức số so với mức lớn nhất máy số ghi được. 0 dBFS là mức tối đa; nửa biên độ khoảng −6 dBFS | Đồng hồ đỉnh mẫu (sample peak) bỏ sót đỉnh nằm giữa hai mẫu | [CT] [Wikipedia: DBFS](https://en.wikipedia.org/wiki/DBFS), [BS.1770-5 Annex 2](https://www.itu.int/dms_pubrec/itu-r/rec/bs/R-REC-BS.1770-5-202311-I!!PDF-E.pdf) |
| **dBTP** | Đỉnh thật (true peak): đỉnh của sóng liên tục, ước bằng nội suy ×4 (48 kHz → 192 kHz) | Đồng hồ ×4 có thể đọc thiếu khoảng 0,5 dB, vì thế trần sản xuất là −1 dBTP | [CT] [BS.1770-5](https://www.itu.int/dms_pubrec/itu-r/rec/bs/R-REC-BS.1770-5-202311-I!!PDF-E.pdf), [Tech 3343](https://tech.ebu.ch/docs/tech/tech3343.pdf) |
| **LUFS = LKFS** | Độ to theo trọng số K, so với full scale. Tín hiệu tăng 1 dB thì số đo tăng 1 LUFS. Sine 997 Hz ở 0 dBFS vào một kênh đo được −3,01 LKFS | EBU gọi là LUFS, ITU gọi là LKFS, hai tên cùng một đại lượng | [CT] [BS.1770-5](https://www.itu.int/rec/R-REC-BS.1770-5-202311-I/en), [R 128](https://tech.ebu.ch/files/live/sites/tech/files/shared/r/r128v5_0.pdf) |
| **LU** | Đơn vị tương đối, 1 LU = 1 dB | Dùng cho chênh lệch, LRA, thang tương đối | [CT] [Tech 3341](https://tech.ebu.ch/docs/tech/tech3341.pdf) |
| **M / S / I** | Momentary: cửa sổ 400 ms. Short-term: 3 s. Hai loại này không có cổng lọc. Integrated: cả bài, chia khối 400 ms chồng 75 %, bỏ khối dưới −70 LUFS rồi bỏ khối thấp hơn 10 LU | Max M và Max S dùng để soi đoạn to nhất | [CT] [Tech 3341](https://tech.ebu.ch/docs/tech/tech3341.pdf), [BS.1770-5](https://www.itu.int/rec/R-REC-BS.1770-5-202311-I/en) |
| **LRA** | Khoảng giữa phân vị 10 % và 95 % của các giá trị Short-term (3 s). Bỏ phần dưới −70 LUFS và phần thấp hơn 20 LU | Không dùng cho bài ngắn hơn 1 phút | [CT] [Tech 3342](https://tech.ebu.ch/docs/tech/tech3342.pdf), [R 128](https://tech.ebu.ch/files/live/sites/tech/files/shared/r/r128v5_0.pdf) |
| **RMS** | Căn bậc hai của trung bình bình phương. Có hai quy ước: AES17 coi sine đầy thang là 0 dBFS RMS; quy ước toán học cho cùng sine đó −3,01 dB | Phải biết máy đo dùng quy ước nào | [CT] [Wikipedia: DBFS](https://en.wikipedia.org/wiki/DBFS) |
| **Crest factor** | Đỉnh chia RMS. Sine: 1,414, tức 3,01 dB | Đo trên dạng sóng, không có trọng số K | [CT] [Wikipedia: Crest factor](https://en.wikipedia.org/wiki/Crest_factor) |
| **PLR** | True peak lớn nhất trừ độ to chương trình (LUFS). Đo độ động ở quy mô nhỏ ("vi động") | PLR cao: âm nhiều gai, đỉnh nhọn | [CT] [R 128 s2](https://tech.ebu.ch/files/live/sites/tech/files/shared/r/r128s2v3_0.pdf) |

### 1.2 Cộng trừ dB

| Phép | Kết quả | Nguồn |
|---|---|---|
| Gấp đôi biên độ (điện áp, áp suất) | +6,02 dB (20·log₁₀2) | [CT] [sengpielaudio](https://sengpielaudio.com/calculator-loudness.htm) |
| Gấp đôi công suất | +3,01 dB | như trên |
| Hai nguồn bằng nhau, không tương quan (hai tiếng khác nhau) | +3 dB | [CT] [sengpielaudio: coherent sources](https://sengpielaudio.com/calculator-coherentsources.htm) |
| Hai nguồn bằng nhau, cùng pha (hai lớp cùng mẫu đặt trùng) | +6 dB. Đây là cách đỉnh cộng dồn khi chồng lớp | như trên |
| 0 dB cộng −6 dB, không tương quan | +0,97 dB | [TÍNH] 10·log₁₀(1 + 10^−0,6) |
| Hai mức chênh nhau 10 dB | Tổng chỉ tăng 0,41 dB | [TÍNH] 10·log₁₀(1,1) |
| Tăng 10 dB | Nghe to khoảng gấp đôi. Đây là quy tắc ước lượng: số sone gấp đôi khi tăng 10 phon (trên 40 phon). Tăng 3 dB **không** nghe to gấp đôi | [CT] [sengpielaudio](https://sengpielaudio.com/calculator-loudness.htm), [Wikipedia: Sone](https://en.wikipedia.org/wiki/Sone) |

### 1.3 Đường cong Fletcher–Munson / ISO 226: nghe nhỏ thì mất trầm

ISO 226:2023 là bản hiện hành của đường cong đồng mức to. Bảng dưới tính bằng công thức và hệ số của ISO 226:2003, lấy từ [mã của Jeff Tackett](https://dsprelated.com/showcode/174.php). Bản 2023 chỉnh lại một ít, nên dùng số này để thấy xu hướng, đừng coi là số chính xác. Đơn vị là dB SPL: mức cần để tone ở tần số đó nghe to bằng 1 kHz. [TÍNH]

| Tần số | 40 phon (nghe nhỏ) | 60 phon | 80 phon (nghe to) |
|---|---|---|---|
| 50 Hz | 77,8 | 90,0 | 101,7 |
| 100 Hz | 64,4 | 78,7 | 92,5 |
| 200 Hz | 53,4 | 69,9 | 85,9 |
| 500 Hz | 43,1 | 62,1 | 80,9 |
| 1 kHz | 40,0 | 60,0 | 80,0 |
| 3,15 kHz | 35,6 | 56,4 | 77,1 |

- Nghe nhỏ (40 phon): 50 Hz phải mạnh hơn 1 kHz 37,8 dB. Nghe to (80 phon): chỉ cần 21,7 dB. Vậy khi vặn nhỏ, tiếng 50 Hz yếu đi thêm khoảng 16 dB so với dải trung. Ở 100 Hz con số này khoảng 12 dB, ở 200 Hz khoảng 7,5 dB.
- Tai nhạy nhất ở 2–5 kHz ([Wikipedia: Equal-loudness contour](https://en.wikipedia.org/wiki/Equal-loudness_contour)).
- Trên điện thoại vặn nhỏ, loa nhỏ đã thiếu trầm (mục 5), tai lại kém nhạy trầm thêm. Kết quả: tick, pop ở 1–5 kHz vẫn rõ, còn sub drop gần như biến mất.

### 1.4 Trọng số K của đồng hồ LUFS

Tôi tính từ hệ số bộ lọc trong BS.1770-5 (48 kHz). Số là mức so với 997 Hz. [TÍNH]

| 40 Hz | 50 Hz | 100 Hz | 200 Hz | 1 kHz | 2 kHz | 4 kHz | 8 kHz |
|---|---|---|---|---|---|---|---|
| −6,3 dB | −4,6 dB | −1,8 dB | −1,0 dB | 0 | +2,4 dB | +3,3 dB | +3,4 dB |

Cùng một mức đỉnh, sub 40–50 Hz được đồng hồ LUFS tính nhỏ hơn 1 kHz 5–6 dB, còn tiếng sáng trên 2 kHz được tính to hơn 2–3 dB. Sub tốn chỗ đỉnh mà góp ít LUFS. Tiếng sáng góp nhiều LUFS.

---

## 2. Mức độ to mục tiêu và true peak theo nền tảng

### 2.1 Bảng nền tảng

| Nền tảng | Mức chuẩn hóa | Chiều | True peak | Nguồn |
|---|---|---|---|---|
| YouTube | Khoảng −14 LUFS | Chỉ hạ bản to, không nâng bản nhỏ | Chưa tìm được nguồn chính thức. Bên thứ ba thường khuyên ≤ −1 dBTP | [ĐO] [MeterPlugs 2019](https://www.meterplugs.com/blog/2019/09/18/youtube-changes-loudness-reference-to-14-lufs.html) |
| YouTube "Stable volume" | Liên tục chỉnh mức khi phát. Không áp cho YouTube Music và MV chính thức | Nén độ động khi phát | — | [CT] [YouTube Help](https://support.google.com/youtube/answer/14106294?hl=en) |
| YouTube: file tải lên | AAC-LC hoặc Opus, stereo, 48 kHz, 384 kbps | — | — | [CT] [YouTube Help](https://support.google.com/youtube/answer/1722171?hl=en) |
| Spotify | −14 (Normal), −11 (Loud), −19 (Quiet) | Cả hai chiều. Khi nâng bản nhỏ vẫn chừa 1 dB cho codec nén. Chế độ Loud có limiter ở −1 dB (đỉnh mẫu), attack 5 ms, release 100 ms | ≤ −1 dBTP; ≤ −2 dBTP nếu master to hơn −14 LUFS | [CT] [Spotify](https://support.spotify.com/us/artists/article/loudness-normalization/) |
| Facebook, Instagram | Đích do app đặt theo ngữ cảnh (loa máy, tai nghe, tiếng ồn). Meta không công bố số | Meta nói đưa "độ to trung bình mọi phiên về cùng đích". Chưa tìm được nguồn nói rõ có nâng bản nhỏ không | Chưa tìm được nguồn | [CT] [Meta Engineering](https://engineering.fb.com/2023/04/11/video-engineering/high-quality-audio-xhe-aac-codec-meta/) |
| TikTok | Chưa tìm được nguồn | Chưa tìm được nguồn | Chưa tìm được nguồn | Một bài tổng hợp năm 2026 cũng ghi Meta và TikTok không công bố số: [Fora Soft](https://www.forasoft.com/learn/audio-for-video/articles-audio/lufs-targets-per-platform-2026) |
| EBU R 128 (phát sóng) | −23,0 LUFS | Bắt buộc với bên sản xuất | ≤ −1 dBTP; codec nén −2 dBTP | [CT] mục 0 |
| AES (streaming âm thanh) | TD1004: −16 đến −20 LUFS. TD1008: nhạc −16, lời −18 LUFS | Khuyến nghị cho bên phân phối, không phải mức để master | ≤ −1 dBTP ở đầu vào codec. TD1008 §7B: codec 256 kbps có thể chịu −0,5 dBTP; bitrate thấp cần hạ dưới −1 | [TC] mục 0 |
| Game (IESD 2015, để tham khảo) | Console −24 LUFS ±2. Mobile −16 LUFS ±2, LRA 10–15 LU | — | Console ≤ −1 dBTP | [TC] [IESD](https://www.audiogang.org/wp-content/uploads/2015/04/IESD-Mix-Ref-Levels-v03.02.pdf) |

### 2.2 Video ngắn trên mạng xã hội nên master bao nhiêu

Chưa tìm được chuẩn chính thức riêng cho video ngắn mạng xã hội. Lập luận:

1. YouTube đo được ở khoảng −14 LUFS và chỉ hạ, không nâng [ĐO]. Bản thấp hơn −14 sẽ phát nhỏ hơn video khác đúng bằng phần thiếu.
2. Spotify chính thức dùng −14 LUFS [CT]. Đây không phải nền tảng video, nhưng là mốc chung của nhiều dịch vụ.
3. Meta chuẩn hóa ở app, không công bố số [CT]. Trên app bản mới, master ở mức nào cũng bị đưa về đích của app. TikTok chưa rõ.
4. Các khuyến nghị −16 đến −20 của AES và EBU s2 dành cho dòng âm thanh và đài phát sóng. TD1008 ghi rõ không dành cho âm kèm hình.

→ **Đề xuất: −14 LUFS integrated, đo trên file stereo cuối cùng. True peak ≤ −1 dBTP là trần cứng, nên ≤ −2 dBTP.** Lý do của mức −2: nền tảng sẽ nén lại file. EBU Tech 3344 đặt limiter −2 dBTP trước encoder, Spotify yêu cầu ≤ −2 với master to hơn −14, ATSC dùng −2. [SL dựa trên các nguồn trên]

### 2.3 So sánh −16 và −14 LUFS

| | −16 LUFS (đang dùng) | −14 LUFS |
|---|---|---|
| YouTube | Phát nhỏ hơn video −14 khoảng 2 dB, không được bù | Không bị hạ, không bị nâng |
| Dịch vụ nâng cả bản nhỏ (kiểu Spotify) | Được nâng lên nếu còn chỗ đỉnh | Giữ nguyên |
| App Meta bản mới | App tự đưa về đích, khác biệt nhỏ | Như bên trái |
| Chỗ cho đỉnh | Với TP −1: PLR tối đa 15 dB | Với TP −1: PLR tối đa 13 dB; với TP −2: 12 dB |
| Khớp chuẩn | Mép trên của AES TD1004 (−16 đến −20) và của EBU s2 | Khớp mốc YouTube và Spotify |
| Với phim này | PLR của MP4 là 10,8 dB | Chỉ cần +2 dB. TP thành −3,2 dBTP, không phải ép thêm |

Lợi của −16: còn nhiều chỗ cho đỉnh, hợp với mix nhiều gai nhọn. Hại: thua 2 dB trên YouTube và trên mọi nền tảng không chuẩn hóa. Lợi của −14: ngang mặt bằng chung. Hại: phim có PLR trên 13 dB sẽ phải ép limiter. Phim này chỉ có PLR 10,8 dB nên lên −14 không mất gì. [SL]

---

## 3. Cân bằng nhạc nền và SFX khi không có lời đọc

### 3.1 Nhạc nên thấp hơn SFX bao nhiêu

**Chưa tìm được nguồn chuẩn** cho số dB hay LU cụ thể. Những gì có nguồn:

- EBU R 128 đo cả chương trình, không đo riêng lời, nhạc hay SFX [CT].
- EBU Tech 3343 ([link](https://tech.ebu.ch/docs/tech/tech3343.pdf)) nói mức của từng thành phần là quyết định nghệ thuật [CT]. Cảm giác to do "âm tiền cảnh" quyết định: giọng, nhạc tiêu đề, **SFX chủ chốt**.
- Cũng theo Tech 3343: tiếng cụng ly có đỉnh cao mà độ to thấp (PLR cao). Một đoạn guitar nén có độ to gần bằng đỉnh. Hai tiếng có cùng đỉnh thì guitar to hơn nhiều. Vì vậy không so SFX với nhạc bằng đỉnh. [CT]
- Blog của Krotos (hãng làm công cụ âm thanh, 2025) đưa quy tắc ước lượng: nhạc khoảng −20 dB; tiếng hit, crack từ −20 đến −10 dB. Bài không ghi đơn vị đo. [TC, độ tin thấp] [link](https://krotos.studio/blog/how-to-balance-music-and-sound-effects)

Hệ quả cho cách đo [SL]: so integrated của bus nhạc (liên tục) với bus SFX (thưa, gai) sẽ ra chênh lệch lớn mà không phản ánh tai nghe. Nên so theo từng cú: Momentary 400 ms, hoặc RMS trong dải tần của tiếng, như QA ping của dự án đang làm.

### 3.2 Ducking (hạ nhạc khi SFX nổ)

**Chưa tìm được nguồn cho ducking theo SFX.** Các nguồn dưới đây đều cho trường hợp hạ nhạc dưới lời nói:

| Nguồn | Mức hạ | Attack | Release / fade |
|---|---|---|---|
| [Audacity Auto Duck](https://manual.audacityteam.org/man/auto_duck.html), mặc định [CT] | −12 dB, ngưỡng −30 dB RMS | fade xuống 0,5 s | fade lên 0,5 s, giữ tối thiểu 1 s |
| [Vindral Composer](https://composer-docs.vindral.com/operators/operators-sidechain-ducking.html) [CT, tài liệu hãng] | −6 đến −12 dB là hạ nhẹ; từ −30 dB trở xuống thì nhạc gần như mất | 1–10 ms: hạ tức thì. 50–200 ms: mềm hơn nhưng lọt đầu tiếng | 50–200 ms: hồi nhanh nhưng dễ nghe "bơm". 500–1500 ms: giữ nhạc thấp qua các khoảng nghỉ |
| [Sound On Sound 2010](https://www.soundonsound.com/node/4908058) (Len Sasso) [TC] | ratio vô cực cho ducking dưới lời | — | khoảng 100 ms ở cuối clip |

### 3.3 LRA cho video ngắn xem trên điện thoại

- EBU không khuyên dùng LRA cho bài ngắn hơn 1 phút, vì LRA dựa trên cửa sổ 3 s nên có quá ít điểm dữ liệu ([R 128](https://tech.ebu.ch/files/live/sites/tech/files/shared/r/r128v5_0.pdf), [R 128 s1](https://tech.ebu.ch/docs/r/r128s1.pdf)) [CT]. Thay vào đó, R 128 s1 giới hạn **Max Short-term ≤ đích + 5 LU**.
- EBU R 128 s2 xếp điện thoại vào nhóm "ít chỗ khuếch đại, tiếng ồn nền cao" [CT]. Tech 3343 nói nền tảng như vậy có thể cần LRA thấp hơn, nhưng không cho số [CT].
- IESD khuyên game mobile LRA 10–15 LU [TC]. Số này dành cho phiên chơi dài, không áp cho phim 21 s.
- → **Chưa tìm được nguồn** cho số LRA của video ngắn hơn 1 phút trên điện thoại.

---

## 4. Mức theo loại SFX

| Loại | Số dB có nguồn | Nguyên tắc có nguồn |
|---|---|---|
| Tick, click giao diện | chưa tìm được nguồn | PLR cao (Tech 3343). Năng lượng ở 1–5 kHz, nơi tai nhạy nhất (ISO 226). Trọng số K cộng thêm 2–3 dB (mục 1.4) |
| Pop | chưa tìm được nguồn | như trên |
| Whoosh | chưa tìm được nguồn | — |
| Va chạm nhẹ | chưa tìm được nguồn | — |
| Impact lớn | chưa tìm được nguồn | Giới hạn chung: Max Short-term ≤ đích + 5 LU (R 128 s1), TP ≤ −1 dBTP |
| Riser | chưa tìm được nguồn | — |
| Logo sting, sub drop | chưa tìm được nguồn | Sub được đồng hồ LUFS tính nhỏ đi 5–6 dB (mục 1.4). Ở 40 phon, 50 Hz phải mạnh hơn 1 kHz 38 dB mới nghe to bằng (mục 1.3) |

**Nhóm nào nên nổi rõ nhất.** Tech 3343 nói "âm tiền cảnh" (giọng, nhạc tiêu đề, SFX chủ chốt) quyết định cảm giác to [CT]. Phim không lời thì SFX mang ý chính đóng vai tiền cảnh. Chọn tiếng nào là quyết định nội dung, không phải quyết định kỹ thuật.

**Giữ chỗ đỉnh cho tiếng trầm (sub):**

- Sub tốn chỗ đỉnh mà góp ít LUFS: 50 Hz bị trọng số K tính nhỏ đi 4,6 dB [TÍNH].
- Lớp cùng pha cộng biên độ, tới +6 dB ([sengpielaudio](https://sengpielaudio.com/calculator-coherentsources.htm)). Sub drop, kick và bass đạt đỉnh cùng lúc là chỗ dễ vượt trần nhất.
- Codec nén làm đỉnh vượt lên, bitrate càng thấp càng vượt nhiều (TD1008 §7B, [TC]). EBU Tech 3344 đặt limiter −2 dBTP trước encoder [CT].
- [Sound On Sound 1998](https://www.soundonsound.com/reviews/waves-maxxbass) (Paul White, bài review Waves MaxxBass) [TC]: hạ phần trầm gốc khoảng 3 dB, rồi thêm hài cao hơn khoảng một quãng tám để bù cảm giác trầm.
- [SL]:
  - lọc bỏ dưới khoảng 30 Hz, vì trọng số K tính nhỏ đi 9 dB ở 30 Hz và loa nhỏ không phát được;
  - không để đỉnh sub trùng đỉnh kick;
  - đo TP trên file AAC đã giải mã, không đo trên WAV.

---

## 5. Loa điện thoại và lớp trung cho tiếng trầm

| Dữ kiện | Nguồn |
|---|---|
| Loa Knowles "Donau Slim" 11×15×3 mm cho smartphone: cộng hưởng 800 Hz ±10 % trong hộp sau 1 cm³, nhà sản xuất gọi là "thấp nhất". Phép thử độ bền dùng lọc cắt trầm 12 dB/oct ở 800 Hz | [CT] [datasheet](https://cdn.eicom.ru/media/PDF/440124.pdf) |
| Bằng sáng chế của Dolby: với thiết bị cầm tay, "tần số thấp nhất" của nội dung là 100–500 Hz, cần ống dẫn âm để bù | [CT] [US10536769B2](https://patents.google.com/patent/US10536769B2/en) |
| Larsen & Aarts (JAES, 2002): dùng hài để tạo ảo giác trầm qua loa nhỏ ("virtual bass") | [NC] [TU/e](https://research.tue.nl/en/publications/reproducing-low-pitched-signals-through-small-loudspeakers/) |
| MaxxBass tạo hài cao hơn khoảng một quãng tám. Hài cho cảm giác trầm nhưng không cho cảm giác rung vật lý | [TC] [Sound On Sound](https://www.soundonsound.com/reviews/waves-maxxbass) |

- **Mốc "~200 Hz": chưa tìm được nguồn đo** cho điện thoại đời mới. Dữ liệu loa linh kiện ở trên cho thấy mốc thực có thể cao hơn: vài trăm Hz, tới khoảng 800 Hz ở loa nhỏ.
- **Lớp trung 300 Hz–2 kHz: chưa có nguồn cho dải cụ thể này, nhưng hướng làm có nguồn** (hài, virtual bass). [SL]: dồn năng lượng lớp trung vào 400 Hz–2,5 kHz, cho tiếng "cắc" đầu cú lên tới khoảng 4 kHz. Dự án đang có:
  - `phone_layer` dải 250–2500 Hz;
  - lớp phone của cú accent dải 400–4000 Hz;
  - QA giả lập loa điện thoại bằng lọc dải 400–8000 Hz.

  Các dải này nhất quán với dữ liệu trên.

---

## 6. Đồng bộ âm và hình

| Nguồn | Âm sớm (trước hình) | Âm trễ (sau hình) | Ghi chú |
|---|---|---|---|
| ITU-R BT.1359 (1998), ngưỡng nhận ra [CT] | 45 ms | 125 ms | Thử ở Nhật, Thụy Sĩ, Úc trên tư liệu truyền hình NTSC và PAL |
| ITU-R BT.1359, ngưỡng chấp nhận [CT] | 90 ms | 185 ms | |
| ITU-R BT.1359, chuỗi phát sóng [CT] | 22,5 ms | 30 ms | |
| EBU R37-2007, mỗi khâu [CT] | 5 ms | 15 ms | |
| EBU R37-2007, đầu đến cuối [CT] | 40 ms | 60 ms | Ngưỡng 50 % người xem nhận ra lệch khẩu hình |
| ATSC IS-191 (2003), đầu vào encoder [TC] | 15 ms | 45 ms | Bài TV Technology ghi cả chuỗi là sớm 30 ms, trễ 90 ms |
| Dixon & Spitz 1980, búa đóng (trích qua Heide & Maempel) [NC] | 75 ms | 188 ms | |
| Heide & Maempel 2010, tiếng clapperboard [NC] | Âm trễ ít hơn 1,7 ms, kể cả trùng khung, đã bị nhận ra là lệch | 75,8 ms | Nghe như trùng nhau khi âm trễ 32,4–38,7 ms. Mức người nghe thích: âm trễ 47,5 ms. Khuyên âm trễ 0–80 ms, không để âm sớm. 105 người nghe (51 người làm dựng phim, âm thanh), màn CRT, mức lệch thử theo bước 40 ms |

- Âm sớm bị nhận ra nhanh hơn âm trễ. Lý do tự nhiên: ngoài đời ánh sáng luôn tới trước âm thanh.
- Hoffner (TV Technology, 2004): trong chuỗi phát, hình thường bị trễ nhiều hơn tiếng, nên tiếng hay bị **sớm** [TC]. Máy chiếu và TV ở hội thảo cũng là một khâu trong chuỗi phát.
- Ở 60 fps: 1 khung = 16,7 ms = 800 mẫu ở 48 kHz.
  - Trễ 1 khung: nằm trong mọi chuẩn.
  - Sớm 1 khung: đã vượt mức sớm 15 ms của ATSC và ngưỡng của Heide & Maempel.
- → **Đặt tiếng va chạm trễ 1 khung, không đặt trùng khung.** Theo dữ liệu tiếng va của Heide & Maempel, đặt trùng khung là đã ở vùng tai nghe "âm hơi sớm". [NC + SL]

---

## 7. Áp dụng cho phim 21 s này

### 7.1 Hiện trạng

Đo lại ngày 22/10, chỉ đọc, trên MP4 giao bản 2.

| I | TP | LRA | Max S | Max M | PLR | Định dạng |
|---|---|---|---|---|---|---|
| −16,0 LUFS | −5,2 dBTP | 6,4 LU | −14,0 LUFS (khoảng 16,0 s) | −12,6 LUFS (khoảng 15,1 s, tràn xanh) | 10,8 dB | AAC stereo 48 kHz, L = R |

MP4 là master mono tách ra hai kênh, mỗi kênh −3 dB. Vì vậy MP4 đo stereo vẫn ra −16,0 LUFS như WAV mono, còn TP thấp hơn WAV 3 dB (WAV: −2,2 dBTP).

### 7.2 Master (file giao)

| Thông số | Đặt | Căn cứ |
|---|---|---|
| Integrated | **−14,0 LUFS**, đo trên MP4 stereo cuối, sai số ±0,5 LU | Mục 2.2 |
| True peak | **≤ −2,0 dBTP** trên MP4. Trần cứng −1,0 | EBU Tech 3344, Spotify, ATSC |
| Max Short-term | **≤ I + 5 LU = −9 LUFS** | Quy tắc +5 LU của R 128 s1, áp sang đích −14 [SL] |
| LRA | Chỉ ghi lại, không chấm đạt hay trượt. Mục "LRA 5–8 LU" của lane A nên thay bằng Max Short-term | R 128 và R 128 s1 không dùng LRA cho bài ngắn hơn 1 phút |
| Kênh | Stereo L = R, 48 kHz, AAC-LC, 320–384 kbps | YouTube khuyên AAC-LC stereo 48 kHz 384 kbps |
| Cách lên −14 | Cộng **+2,0 dB ở bước stereo, sau limiter**, không thêm limiter. Ví dụ khi mux, dùng hệ số 0,891 (−1 dB) mỗi kênh thay cho 0,708 (−3 dB). Hoặc master thẳng ở miền stereo như lane A đề xuất | [TÍNH] |
| Kết quả dự kiến | I −14,0 · TP −3,2 dBTP · Max S −12,0 · Max M −10,6 · PLR 10,8 dB. Limiter không ép thêm (ép tối đa vẫn 4,66 dB ở logo) | [TÍNH] |
| Chú ý | Không nâng WAV mono +2 dB rồi dùng như file giao: WAV sẽ có TP −0,2 dBTP, vượt trần −1 | [TÍNH] |
| Chiếu ở hội thảo | Dùng file stereo. WAV mono phát ra hai loa ở cùng mức sẽ to hơn khoảng 3 LU | [CT] [Tech 3344 §6.16](https://tech.ebu.ch/docs/tech/tech3344.pdf), [Auphonic](https://auphonic.com/blog/2020/06/09/loudness-normalization-mono-productions/) |
| Phát sóng truyền hình (nếu cần) | Làm bản riêng. EBU: −23 LUFS (bớt 9 dB từ bản −14), TP ≤ −1. ATSC: −24 LKFS, TP ≤ −2 | [CT] |

### 7.3 Từng nhóm âm

Cột "Hiện tại" lấy từ `g6-am-thanh.md` bản 2, đã được Minh duyệt. **Mọi số trong cột "Đích" là [SL]**: các chuẩn không quy định mức dB cho từng loại SFX. Cộng +2 dB ở bước master giữ nguyên mọi chênh lệch dưới đây.

| Nhóm | Vai trò | Đích đề xuất | Hiện tại |
|---|---|---|---|
| Ping báo tin | Ý chính của phim | Trong dải của ping: ≥ +3 dB so với nhạc (sàn +2 dB) | +3,0…+3,4 dB (b1 +7,2) |
| Tick hứng | Nhịp chính, tiền cảnh | ≥ +6 dB so với nhạc trong dải 0,8–6 kHz. Không nâng thêm: dải này tai nhạy nhất, dễ chói khi vặn to | +8…+14 dB |
| Tick thẻ CRM, tick dòng, tick nút CTA | Phụ | Thấp hơn tick hứng 3–6 dB trong cùng dải | Chưa đo riêng |
| "Bụp" tin bay ra (pop) | Phụ | Khoảng như ping: ≥ +2 dB trong dải của nó, thấp hơn tick hứng | Chưa đo riêng |
| Whoosh, riser, swell | Nối cảnh | Momentary của tiếng (solo) không vượt Momentary của nhạc tại đó. Riser kết hoặc đạt đỉnh đúng khung cú chính, không to hơn cú chính | PLR bus chuyển cảnh 18,4 dB (bản 1) |
| Va chạm nhẹ (đáp nhỏ, tok sừng, nảy) | Vật lý | Nghe được qua giả lập loa điện thoại 400–8000 Hz. Không cần nổi hơn nhạc | — |
| Impact lớn (đáp sau nhảy, tràn xanh) | Cao trào | Limiter ép (RMS 300 ms) ≤ 3 dB, theo lane A. Max S toàn phim ≤ I + 5 LU | Ép 1,30 dB ở cú đáp; Max M = I + 3,4 LU |
| Logo sting + sub drop | Kết, tiền cảnh | Qua giả lập loa điện thoại, logo ≥ thân đoạn đuổi (0 dB trở lên). Nếu thiếu, nâng lớp phone của hit và sub drop khoảng +2 dB trước khi hạ nhạc. Sub: lọc dưới khoảng 30 Hz, không trùng đỉnh kick, TP sau AAC ≤ −2 dBTP | Qua giả lập: −1,1 dB (WARN) |
| Nhạc nền | Thảm | Chấm theo từng cú như các dòng trên, không chấm "nhạc − SFX (integrated của bus) ≤ 2 LU". Nếu cần ducking cho cú lớn: hạ 2–4 dB, attack ≤ 10 ms, release 150–250 ms (không quá nửa phách ở 120 BPM) | Bus nhạc to hơn bus SFX 5,2 LU |

**Nhóm nổi rõ nhất:** ping báo tin, tick hứng, logo. Ping là ý chính theo điều phối 21/10, và đúng vai "SFX chủ chốt" trong Tech 3343.

### 7.4 Đồng bộ (60 fps)

- **Va chạm:** giữ đỉnh **trễ 1 khung (16,7 ms)** sau hình như đang làm. Vật nặng có thể trễ tới 2 khung (33 ms), vẫn sát điểm "nghe trùng" 32–39 ms. **Không bao giờ để âm sớm.**
- **Whoosh, riser:** kết hoặc đạt đỉnh đúng khung sự kiện (giữ quy ước hiện tại). Căn theo đỉnh tiếng, không theo đầu file.
- **Hit logo, cắt nhạc:** hiện đặt đúng khung. [SL] Có thể dời hit logo trễ 1 khung cho cùng cảm giác với các cú va chạm.

### 7.5 Kiểm trước khi giao

- Đo trên MP4 cuối, không đo trên WAV:
  - I, LRA, TP: `ffmpeg -i <mp4> -af ebur128=peak=true -f null -`
  - Max S, Max M: thêm `-v verbose` và `framelog=verbose`.
- Nghe trên điện thoại thật, ở khoảng 1/3 âm lượng rồi ở mức to. Mục 1.3 cho thấy nghe nhỏ thì mất trầm nhiều nhất.
- Sau khi đăng YouTube: mở "Stats for nerds". Bản −14 sẽ hiện mức chỉnh khoảng 0 dB.

---

## 8. Chưa tìm được nguồn hoặc chưa chắc

- Mức đích và cách chuẩn hóa của TikTok. Số LUFS của Meta. Tài liệu chính thức của YouTube về −14 LUFS (hiện chỉ có số đo của bên thứ ba).
- Bản gốc AES TD1004, TD1008, AES71 (video OTT), AES77 (streaming): aes.org chặn truy cập. Số AES trong báo cáo lấy qua nguồn thứ cấp.
- ATSC A/85 đã sửa đổi tháng 7/2026, có thêm phụ lục streaming ([SVG](https://www.sportsvideo.org/2026/07/16/atsc-releases-first-major-revision-to-a-85-audio-loudness-recommended-practice-since-2013/)). Tôi chưa xem được số mới; số trong báo cáo là bản 2013.
- Mức dB cho từng loại SFX, mức nhạc so với SFX, ducking theo SFX: không có nguồn chuẩn. Mọi số ở mục 7.3 là [SL].
- LRA cho video ngắn hơn 1 phút trên điện thoại.
- Đáp tuyến loa của điện thoại đời mới (mốc ~200 Hz). Bảng ISO 226 tính theo hệ số bản 2003, bản 2023 chỉnh nhẹ.

## 9. Danh mục nguồn

| # | Nguồn | Link |
|---|---|---|
| 1 | ITU-R BS.1770-5 (11/2023) | https://www.itu.int/rec/R-REC-BS.1770-5-202311-I/en |
| 2 | EBU R 128 v5.0 (2023) | https://tech.ebu.ch/files/live/sites/tech/files/shared/r/r128v5_0.pdf |
| 3 | EBU R 128 s1 (2020) | https://tech.ebu.ch/docs/r/r128s1.pdf |
| 4 | EBU R 128 s2 v3.0 (2023) | https://tech.ebu.ch/files/live/sites/tech/files/shared/r/r128s2v3_0.pdf |
| 5 | EBU Tech 3341, 3342, 3343 (2023) | https://tech.ebu.ch/docs/tech/tech3341.pdf · https://tech.ebu.ch/docs/tech/tech3342.pdf · https://tech.ebu.ch/docs/tech/tech3343.pdf |
| 6 | EBU Tech 3344 v2.1 (2016) | https://tech.ebu.ch/docs/tech/tech3344.pdf |
| 7 | EBU R37-2007 | https://tech.ebu.ch/docs/r/r037.pdf |
| 8 | ITU-R BT.1359 (1998) | https://itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.1359-0-199802-S!!PDF-E.pdf |
| 9 | ATSC A/85:2013 | https://www.atsc.org/wp-content/uploads/2025/06/A85-2013-with-Corrigendum-No-1.pdf |
| 10 | ATSC IS-191 (R. Hoffner, TV Technology 2004) | https://tvtechnology.com/opinions/atsc-recommends-av-sync-rules |
| 11 | AES TD1004 (qua Production Expert) | https://www.production-expert.com/home-page/2015/11/17/aes-release-recommendations-for-loudness-of-audio-streaming-and-network-file-playback |
| 12 | AES TD1008 (qua Ian Shepherd, M. Thornton, trích §4 và §7B) | https://productionadvice.co.uk/td1008/ · https://www.production-expert.com/production-expert-1/aes-update-loudness-recommendations-for-audio-only-streaming · https://raw.githubusercontent.com/M-Igashi/baken/main/docs/true-peak-ceiling.md |
| 13 | Spotify for Artists | https://support.spotify.com/us/artists/article/loudness-normalization/ |
| 14 | YouTube −14 LUFS (Ian Shepherd) | https://www.meterplugs.com/blog/2019/09/18/youtube-changes-loudness-reference-to-14-lufs.html |
| 15 | YouTube Help: Stable volume; thông số tải lên | https://support.google.com/youtube/answer/14106294?hl=en · https://support.google.com/youtube/answer/1722171?hl=en |
| 16 | Meta Engineering: xHE-AAC | https://engineering.fb.com/2023/04/11/video-engineering/high-quality-audio-xhe-aac-codec-meta/ |
| 17 | Fora Soft: mức LUFS theo nền tảng (2026) | https://www.forasoft.com/learn/audio-for-video/articles-audio/lufs-targets-per-platform-2026 |
| 18 | sengpielaudio | https://sengpielaudio.com/calculator-loudness.htm · https://sengpielaudio.com/calculator-coherentsources.htm |
| 19 | Wikipedia: Sone, Equal-loudness contour, DBFS, Crest factor | https://en.wikipedia.org/wiki/Sone · https://en.wikipedia.org/wiki/Equal-loudness_contour · https://en.wikipedia.org/wiki/DBFS · https://en.wikipedia.org/wiki/Crest_factor |
| 20 | Hệ số ISO 226:2003 (mã J. Tackett) | https://dsprelated.com/showcode/174.php |
| 21 | Datasheet Knowles Donau Slim | https://cdn.eicom.ru/media/PDF/440124.pdf |
| 22 | Dolby US10536769B2 | https://patents.google.com/patent/US10536769B2/en |
| 23 | Larsen & Aarts, JAES 2002 | https://research.tue.nl/en/publications/reproducing-low-pitched-signals-through-small-loudspeakers/ |
| 24 | Sound On Sound: Waves MaxxBass (1998); Live Side-chain Compression (2010) | https://www.soundonsound.com/reviews/waves-maxxbass · https://www.soundonsound.com/node/4908058 |
| 25 | Heide & Maempel, Tonmeistertagung 2010 | https://www.simpk.de/fileadmin/user_upload_sim/Dokumente/Forschung/Themen/Abteilung_III/Publikationen/Heide_Maempel_2011_Die_Wahrnehmung_audiovisueller_Synchronitaet_in_elektronischen_Medien.pdf |
| 26 | Auphonic: mono và dual mono | https://auphonic.com/blog/2020/06/09/loudness-normalization-mono-productions/ |
| 27 | Audacity Auto Duck; Vindral Composer ducking | https://manual.audacityteam.org/man/auto_duck.html · https://composer-docs.vindral.com/operators/operators-sidechain-ducking.html |
| 28 | Krotos blog (2025) | https://krotos.studio/blog/how-to-balance-music-and-sound-effects |
| 29 | IESD Mix Ref Levels v03.02 (2015) | https://www.audiogang.org/wp-content/uploads/2015/04/IESD-Mix-Ref-Levels-v03.02.pdf |

<!-- ===== /file: motion-sfx-audio-mastering/references/nghien-cuu-decibel.md ===== -->
