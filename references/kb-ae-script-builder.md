# kb-ae-script-builder — toàn văn tài liệu của nguồn `ae-script-builder`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/ae-script-builder/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: ae-script-builder/SKILL.md ===== -->

---
name: ae-script-builder
description: >-
  Dựng mới hoàn toàn dự án Adobe After Effects (.aep) từ con số 0 bằng mã ExtendScript (.jsx) chạy ngầm không cần mở giao diện (AfterFX.exe -noui -m -s). Bao gồm kiến trúc dự án chuẩn (templates/du-an-ae), thư viện hàm lõi lib.jsx (bezier easing, expression, 3D layer, shape vector, camera), 10 quy tắc Text Animator tiếng Việt không cắt dấu (R1–R10), xuất MP4 chuẩn màu BT.709 (1-1-1) và hệ thống kiểm định hình ảnh tự động (qa_chu.py, metrics.py, to_contact.py). Kích hoạt khi người dùng yêu cầu viết code .jsx tạo project After Effects mới, làm motion graphics bằng script AE, sửa lỗi chữ tiếng Việt trong AE, hoặc render/kiểm tra chất lượng video AE bằng dòng lệnh.
---

# AE Script Builder — Dựng Mới Dự Án After Effects Bằng Mã ExtendScript (`.jsx`)

Skill này cung cấp toàn bộ quy trình, thư viện hàm lõi (`lib.jsx`), bộ khung dự án mẫu (`templates/du-an-ae`), ví dụ thực chiến (`examples/opa-agent`) và công cụ kiểm định tự động để **dựng mới hoàn toàn file `.aep` từ con số 0** bằng dòng lệnh mà không cần thao tác tay trên giao diện After Effects.

---

## Chạy trên máy Linux này

- Python: `~/.venvs/video-skills/bin/python` (máy không có lệnh `python`/`py`; venv có numpy, scipy, matplotlib, opencv, scikit-image, Pillow, fontTools, resvg-py, faster-whisper). Lệnh `python …` trong tài liệu chạy bằng đường dẫn này.
- ffmpeg/ffprobe 8.1 ở `~/.local/bin` (libx264, FFV1, ProRes 4444, loudnorm, ebur128).
- Đường dẫn Windows trong tài liệu đã đổi sang Linux: `F:\` → `/media/vmiz/Over Powers/`, `D:\` → `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/` (bản sao lưu ổ D ngày 2026-10-28). Ổ USB `Over Powers` phải đang gắn. `E:\` không có trên máy; tài nguyên thay thế ở `/home/vmiz/Thanh/Media/TNEDIT/` (`02_SFX`, `08_Nhac_Nen`, `01_Font`, `06_B-Roll`…).
- Trên Linux dùng **EffectCraft 0.17** (`~/.local/bin/effectcraft`) thay After Effects: chạy ExtendScript theo mô hình đối tượng AE (`app.version` báo `26.0`), ScriptUI, `$.evalFile`; `app.run(id, params)` gọi mọi lệnh của app. Chạy script: File > Scripts > Run Script File… (script đặt trong `~/.config/effectcraft/Scripts/` hiện ở File > Scripts). Script ghi file cần bật Settings > Scripting > Allow Scripts to Write Files (máy này đang tắt). EffectCraft **không mở được `.aep`** (chỉ `.ecproj`); không có `aerender`/headless.
- Đã chạy thử 2026-10-29: `templates/du-an-ae` và `examples/opa-agent` (46 comp, 31 lớp chữ, 388 expression, 0 lỗi) dựng đúng trên EffectCraft, chữ tiếng Việt đủ dấu. Cách chạy: `python tools/ec.py` → chạy `build/_bundle_ec.jsx` trong project trống; project lưu `project/<tên>.ecproj`, báo cáo `build/_report.json`. `lib.jsx` đọc cả tên nhóm Advanced của EffectCraft (`advanced`/`basedOn`/`shape`). Script `references/template-audit/` cần `1.aep` nên chỉ chạy trên AE.
- `tools/ae.py` gọi `AfterFX.exe`/`aerender` nên chỉ chạy trên Windows; trên Linux dùng `tools/ec.py`. Font contact sheet (`to_contact.py`, `to_khung.py`): `/home/vmiz/Thanh/Media/TNEDIT/01_Font/Google_Fonts_PR/BeVietnamPro-Bold.ttf` (máy không có bản SemiBold).

---

## 1. Cấu Trúc Thư Mục Trong Skill

- **`templates/du-an-ae/`** — Khung dự án khởi tạo nhanh cho mọi phim After Effects mới:
  - `build/lib.jsx`: Thư viện hàm dùng chung (`makeComp`, `addSolid`, `addShapeRect`, `addText`, `ease`, `expOut`, `backOut`, `addAnimatorFadeUp`, `applyWiggle`, `applyOvershoot`, `addCamera`, `enableMotionBlur`).
  - `build/main.jsx`: Điểm vào chạy `AfterFX.exe -r`, tự động nạp `seed/empty-ae26.aep`, ghép từng cảnh vào `00_MASTER`, lưu `.aep`.
  - `build/scenes/s1_mau.jsx`: Cảnh mẫu có sẵn nền, hạt trôi (floating dots), tiêu đề bay lên từng từ và thẻ nhịp đập.
  - `tools/ae.py`: Wrapper Python gọi `AfterFX.exe -noui -m -s`, `aerender.exe` và `ffmpeg` (kèm cờ màu BT.709).
  - `tools/qa_chu.py`: Cổng kiểm tra tự động phát hiện chữ đè nhau, tràn lề an toàn hoặc bị cắt dấu tiếng Việt.
  - `tools/to_contact.py`: Xuất bảng ảnh contact sheet để duyệt nhanh bằng mắt.
- **`examples/opa-agent/`** — Dự án mẫu hoàn chỉnh 5 cảnh (30 giây, `1920x1080`, `30 fps`, nhân vật + linh vật Bò OPA + Text Animator + âm thanh đồng bộ):
  - `build/scenes/s1_mo_dau.jsx` → `s5_cta.jsx`, `art_nhan_vat.jsx`, `art_icon_mascot.jsx`, `am_thanh.jsx`.
  - `tools/svg_to_ae.py`, `tools/build_accent_font.py`, `tools/do_dung_yen.py`.
- **`scripts/v2w/`** — Bộ đo lường chuyển động trên video đầu ra (`metrics.py`, `metrics_core.py`, `scan_video.py`, `contact.py`).
- **`references/`** — Sổ tay tra cứu chuyên sâu:
  - `references/SO-TAY-AFTER-EFFECTS.md`: Sổ tay toàn diện về kiến trúc ExtendScript, bảng 11 đường cong Easing, 6 mẫu Expression, quy tắc màu BT.709 và xử lý lỗi.
  - `references/template-audit/`: Báo cáo giải phẫu kỹ thuật từ 3 dự án `.aep` thương mại (`BANG-TEXT-VA-KEYFRAME.md`, `BAO-CAO-PHAN-TICH.md`, `MOTION-PRESETS.json`, `PROMPT-HOAN-CHINH-OPUS.md` và bộ 7 script thăm dò `.jsx`).
  - `references/01-PHUONG-AN-TRIEN-KHAI-OPA-AGENT.md` & `references/00_BANG-HUONG-DAN-DUNG-TOAN-BO.md`.

---

## 2. Quy Trình 5 Bước Khởi Tạo & Dựng Dự Án Mới

### Bước 1: Sao chép khung dự án chuẩn
Copy thư mục `templates/du-an-ae/` sang thư mục làm việc mới của dự án. Chỉnh sửa cấu hình trong `tools/ae.py`:
- `W`, `H`, `FPS`, `DUR` (mặc định `1920x1080`, `30 fps`).
- Đường dẫn `AE_DIR` trỏ tới bộ cài Adobe After Effects trên máy (ví dụ: `C:\Program Files\Adobe\Adobe After Effects 2026\Support Files`).

### Bước 2: Thiết kế từng phân cảnh trong `build/scenes/`
Mỗi cảnh tách thành một hàm độc lập `buildSceneN(proj, folder)` trả về một `CompItem`:
- Dùng `makeComp(proj, "S1_MoDau", W, H, FPS, dur, folder)` để tạo comp cảnh.
- Dùng `addShapeRect`, `addText`, `addCamera`, `enableMotionBlur` từ `build/lib.jsx`.
- Ghép các comp cảnh nối tiếp nhau trong `00_MASTER` tại `build/main.jsx`.

### Bước 3: Áp dụng 10 Quy Tắc Vàng Khi Làm Chữ Tiếng Việt (R1–R10)

> [!IMPORTANT]
> Tiếng Việt có hệ thống dấu thanh chồng lên nguyên âm मũ (`Ấ`, `Ể`, `Ự`, `Ẵ`). Nếu dùng `Track Matte` hoặc hộp cắt sát thân chữ kiểu tiếng Anh, dấu tiếng Việt sẽ bị chém mất đầu!

| Mã | Quy tắc bắt buộc |
|---|---|
| **R1** | **Ưu tiên đơn vị `Words` (`ADBE TextIndexUnits = 2`):** Đi theo từng từ với `Offset: -30% -> 100%`, `Shape = Ramp Up`, `Ease Low = 85%` để chữ lướt mượt không vụn. |
| **R2** | **Đơn vị `Characters` (`Units = 1`):** Chỉ dùng cho заголовки ngắn (≤ 4 từ), bắt buộc kèm `Position.Y + Scale` hoặc `Rotation.Z`. |
| **R3** | **Đơn vị `Lines` (`Units = 3`):** Dùng cho phụ đề nhiều dòng hoặc danh sách gạch đầu dòng. |
| **R4** | **Tránh bật 3D Per-Character (`ADBE Vec3D Chars`) trừ khi thật sự xoay trục X/Y:** Giúp giữ tốc độ render nhanh và chống lỗi răng cưa dấu tiếng Việt. |
| **R5** | **Khoảng thời gian Reveal chuẩn:** `0.45s – 0.90s` (`14 – 27 frames` ở `30fps`). |
| **R6** | **Cấm cắt dấu tiếng Việt:** Không dùng `Track Matte` cắt sát chữ cho các dòng có dấu chồng (`Ấ, Ể, Ộ, Ự`). Dùng `Opacity + Position Y` trong Text Animator, và đặt `leading ≥ fontSize × 1.28`. |
| **R10** | **Kiểm tra hộp bao bằng `sourceRectAtTime(t, false)`:** Đo chính xác chiều rộng/cao thực tế của chữ sau khi gắn font để căn lề và kiểm tra tràn khung. |

### Bước 4: Chạy Build `.aep`, Kiểm Định Chữ (`qa_chu.py`) và Render MP4

Chạy lần lượt các lệnh từ thư mục dự án:

```bash
# 1. Sinh file dự án .aep bằng AfterFX.exe chạy ngầm (-noui -m -s)
python tools/ae.py build

# 2. Kiểm tra tự động lỗi đè chữ, tràn khung an toàn, cắt dấu tiếng Việt
python tools/qa_chu.py

# 3. Xuất các khung hình kiểm tra và ghép bảng contact sheet
python tools/ae.py frames
python tools/to_contact.py

# 4. Render bản video MP4 hoàn chỉnh (aerender -> ProRes/AVI -> ffmpeg H.264 BT.709)
python tools/ae.py mp4
```

> [!CAUTION]
> **Quy tắc màu sắc BT.709 (`1-1-1`):** Khi nén từ `aerender` sang `H.264 MP4` bằng `ffmpeg`, bắt buộc truyền đủ bộ cờ `-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv`. Thiếu các cờ này trình phát sẽ đọc nhầm ma trận màu khiến màu nền và thương hiệu bị lệch.

### Bước 5: Kiểm Định Chuyển Động (`scripts/v2w/metrics.py`)

Sau khi xuất `.mp4`, chạy bộ đo lường chuyển động để đảm bảo không có khung hình chết (`dead frames`):

```bash
python scripts/v2w/metrics.py duong_dan_video.mp4
```

- **Tiêu chuẩn vượt cổng QA:** `dead_frame_pct = 0.0%`, không có lỗi trong `qa_chu.py`, màu sắc đồng nhất chuẩn `BT.709`.

<!-- ===== /file: ae-script-builder/SKILL.md ===== -->

<!-- ===== file: ae-script-builder/examples/opa-agent/KHUNG-DUNG.md ===== -->

# Khung dựng — OPA Agent × Pancake (After Effects native)

21/10/2026 · 16:9, 1920×1080, 30 fps, 36 s (1.080 khung, khung đầu là 0)
Trạng thái: **bản giao v10 (23/10/2026)**: `out/review/OPA-Agent-Pancake_v10.mp4` = hình v08 + URL thật trên nút CTA + âm v09 (68 SFX theo chuyển động, nhạc tự tổng hợp; quanh lời bỏ 4 SFX, chỉnh 7, còn 64) + giọng đọc `VOICE/1023.MP3`, master −16,0 LUFS, đỉnh thật −3,5 dBTP; đã tự kiểm và rà chéo âm bằng agent (mục 6c). Hình v08 và âm v09 bạn đã duyệt ngày 22/10. Còn chờ: bạn duyệt v10 (lưu ý câu 5 đọc "Oping"), Hùng duyệt đăng. Bản cũ nằm ở `out/review/_ban-cu`.

## 1. Brief đã chốt

- **Mục tiêu:** giới thiệu OPA Agent — AI bán hàng cho shop dùng Pancake, đi từ quá tải tin nhắn đến tự động hóa và giải phóng thời gian.
- **Người xem:** chủ shop online, người quản lý nhiều trang, nhân viên trực page đang dùng Pancake/Pancake POS.
- **Thông điệp:** "OPA lo phần trả lời, shop lo phần bán!" (trong lời đọc cảnh 5).
- **Đã khóa:** trình tự Hook → Nỗi đau → Giải pháp → Giải phóng → CTA; chữ và lời theo kịch bản; tên OPA Agent, Pancake/Pancake POS; hoạt hình 2D, mascot Bò OPA, đi từ tối sang sáng; cảnh cuối nền xanh thương hiệu.
- **Bạn chốt 21/10:**
  - Cài Fraunces Italic 800 đúng bản V2 đã render, tên `Fraunces OPA ExtraBold Italic`.
  - "OPING" là chỗ chờ URL: nút CTA hiện `[URL]`, sửa ở comp `TXT_S5_URL`.
  - Mốc cảnh 2→3 dời sang **13,5 s**; mốc: 0–5 / 5–13,5 / 13,5–22 / 22–30 / 30–36 s.
  - Giọng đọc bạn gửi file sau; project có lớp giữ chỗ kèm marker từng câu; MP4 duyệt chỉ có SFX.
  - Duyệt gu đoạn mẫu, giao dựng hoàn thiện cảnh 2–5 và các điểm nối.
- **Bạn chốt 22/10:** duyệt bản hoàn thiện v08; giao chọn SFX theo từng chuyển động từ kho `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx`, chọn nhạc nền, đặt mức theo research decibel (bản v09, mục 6b); **duyệt phần âm v09** (nhạc nền tự tổng hợp, `assets/music/nhac-nen-opa-agent.wav`, MD5 01881e83…, dựng lại từ `tools/audio/score_agent.py` ra đúng từng bit).
- **Bạn gửi 23/10:** giọng đọc `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/VOICE/1023.MP3` (36,0 s, khớp lời kịch bản; câu 5 đọc "ngay tại Oping") và URL `https://chat.overpowers.agency/` (nút CTA hiện `chat.overpowers.agency`).

### Giả định và lựa chọn đảo ngược được

| Chỗ | Đã chọn | Lý do |
|---|---|---|
| fps | 30 fps theo brief | BRAND-SPEC ghi 16:9 = 60 fps (chốt 19/10); brief mới ghi 30. Đổi 60 fps trong AE giữ nguyên giây, không phải dựng lại. |
| Màu | Đêm #003C99 (cảnh 1–2) → trắng (3–4) → xanh #0068FF (5) | Tối → sáng như brief; nền phẳng kiểu V2 |
| Nhân vật chủ shop | Vẽ phẳng bằng đúng 5 màu OPA: da #E6F0FF, tóc đen, áo trắng, ghế xanh | Palette OPA không có màu da; kiểu đơn sắc giữ thương hiệu |
| ✅ 👉 • | Icon vector: tích xanh OPA, mũi tên, dấu "!" đỏ ALERT | Emoji trong AE không ổn định; palette không có xanh lá; ALERT chỉ cho dấu cảnh báo nhỏ |
| Dấu "—" cảnh 5 | Xuống dòng "OPA Agent" / "AI bán hàng cho shop dùng Pancake" | Chữ giữ nguyên, chỉ đổi cách trình bày |
| Glass, glow, đổ bóng, CC Cylinder của mẫu (R7, R8, R9) | Không dùng; nhãn kính R9 thành chip phẳng | Video OPA: phẳng, không bóng đổ, không 3D |
| Luật "7–9 chữ mỗi khung" | Giữ chữ khóa, cho vào từng dòng; cuối cảnh 3 có khoảng 45 chữ trên hình | Kịch bản khóa dài hơn luật; cần bạn xem có chấp nhận không |
| Nhãn giao diện | "24H", "POS", "99+", "Pancake POS"; dữ liệu UI giả | Luật Minh: dòng bắt đầu bằng số thì viết hoa chữ ngay sau; không dùng giao diện thật |
| SFX | 68 cue theo từng chuyển động, 29 file từ kho `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx` (CC0/MIT, không theSOUNDS) chép WAV vào `assets/sfx`; logo âm thanh giữ bản của bộ OPA | Bảng cue kèm lý do và mức: `audio/BANG-CUE-AM-THANH.md`. Âm có cao độ chọn trong giọng La trưởng của nhạc (đo cao độ từng file) |
| Nhạc nền | Tự tổng hợp 36 s, 120 BPM, La trưởng, theo 5 cảnh (`tools/audio/score_agent.py`, bộ nhạc cụ V2/V3); −31 LUFS khi phát | Kho sfx không có bài nhạc nào đủ dài (file dài nhất là bản nghe thử gộp SFX của Kenney); BRAND-SPEC OPA: không nhạc có bản quyền, tự tổng hợp như V2/V3. Dự phòng nếu bạn muốn: 4 bài Mixkit ở kho nhạc mặc định |
| URL trên nút CTA | `chat.overpowers.agency` (bỏ `https://` và `/` cuối), chữ thường; nút giãn theo chữ (742 px), con trỏ bấm sau chữ | Gọn trên nút; URL/tên miền giữ chữ thường như luật tên file (08/10), `tools/qa_chu.py` miễn viết hoa cho dòng là URL |
| Giọng đọc | Dùng nguyên file của bạn, đặt từ 0 s, gain +2,6 dB (giọng ở −16,3 LUFS trong bản trộn) | File đã khớp nhịp 5 cảnh; không cắt ghép câu |
| Khối trang trí nền | Màu đặc theo V2 (`src/v2w/world/tones.ts`): nền đêm dùng khối #0068FF, khung và nền xanh dùng khối #003C99, nền trắng dùng khối #E6F0FF | Bản trước pha độ mờ ra màu ngoài bảng (#0042A9, #1776FD, #005BE1). Muốn khối chìm hơn: sửa fill trong layer `DECO …` của từng cảnh |

## 2. Phương án hình và chuyển động

Ngôn ngữ chung: nền phẳng kiểu V2, khối trang trí màu đặc; máy quay ảo (null `CAM`) trôi **một đường chậm và đều** suốt từng cảnh, hướng trôi chọn để khối chính luôn cách lề; chữ và giao diện gắn vào máy quay; chuyển cảnh liền mạch, không cắt cứng.

- **Cảnh 1 · 0–5 s · Hook (đêm):** chủ shop chau mày gõ phím, đồng hồ quay 3 vòng/5 s tích tắc, 6 tin nhắn bật dồn dập có chấm đỏ, điện thoại rung. Cột chữ: headline theo từ → phụ theo dòng → cụm nhấn "Mỗi ngày?" có khối trắng quét. Máy quay lao vào chồng tin nhắn.
- **Nối 1→2 (4,5–5,3 s):** một tin nhắn trắng giữa chồng tin nở về phía ống kính, phủ kín khung đúng khung cuối cảnh 1; cảnh 2 tan ra từ màn trắng trong 10 khung, máy quay tiếp tục chiều đẩy vào (80 % → 100 %).
- **Cảnh 2 · 5–13,5 s · Nỗi đau (đêm):**
  - Nhịp 1 (5,8 s): hộp thư cuộn liên tục, mỗi tin mới đẩy danh sách lên một ô, "99+" nảy, chấm đỏ chưa đọc → "Hàng chục cuộc chat bỏ dở".
  - Nhịp 2 (8,2 s): câu hỏi lặp lại, câu trả lời giống hệt nhau bật ra, chấm đỏ của câu vừa trả lời tắt → "Trả lời lặp đi lặp lại".
  - Nhịp 3 (10,6 s): phiếu POS mở bằng mask (R10), viền xanh chạy theo mép khối mở; chip số điện thoại, chip địa chỉ bay vào ô; vạch gõ dài ra; con trỏ bấm lưu → "Lên đơn POS thủ công".
  - Cuối cảnh: hộp thư và phiếu rung quá tải.
- **Nối 2→3 (12,9–13,5 s):** Bò OPA trắng lao vào (cúi đầu, dừng có rung tắt dần); đĩa sáng đi cùng Bò, bật sau lưng Bò (Bò chuyển xanh đúng khung đó) rồi nở đều trong 11 khung, phủ kín đúng khung cuối cảnh. Sang cảnh 3, Bò cất cánh từ tốc độ 0, bay vào đầu bảng; đầu bảng hoá xanh từ chỗ Bò đáp.
- **Cảnh 3 · 13,5–22 s · Giải pháp (ngày):**
  - Bảng OPA Agent mở bằng mask (R10) từ góc trên-trái; Bò bay vào đầu bảng và hoá trắng trên nền xanh của đầu bảng.
  - Chip "Pancake POS" cắm vào kèm vòng tỏa lặp lại (1 kết nối).
  - 5 hàng minh họa bật đúng nhịp 5 tính năng: trả lời kèm kho hàng; đơn vào Pancake POS có tích; ảnh chuyển khoản có vạch quét rồi tích; chuông nhắc 24H rung; nút gạt chuyển từ Bò sang nhân viên.
  - Cột chữ: "Chỉ 1 kết nối —" (khối xanh) → headline → 5 tính năng → "Và nhiều hơn thế nữa!".
- **Nối 3→4 (21,2–22 s):** cột chữ thoát R6 (thu nhỏ cả khối); khung bảng hoá xanh ngay tại chỗ, giao diện tắt dưới nó, rồi khung dời đều về đúng khung xanh của cảnh 4.
- **Cảnh 4 · 22–30 s · Giải phóng:** chủ shop trồi lên từ mép dưới khung xanh rồi ngả lưng, hai tay sau gáy, mắt cười; cà phê bốc hơi; tích xanh bay lên từ laptop. Ba dòng "Không cần…" có icon tích.
- **Nối 4→5 (29,1–30 s):** chữ rút, nhân vật trượt xuống, khung xanh nở tăng tốc phủ kín khung đúng khung cuối.
- **Cảnh 5 · 30–36 s · CTA (xanh):**
  - Bò trắng hiện kiểu V2: mõm bật lên theo lò xo, sừng mọc từ gốc, hai vòng tỏa theo sonic logo, rồi thở 1,00–1,03.
  - Chữ: "OPA Agent" theo ký tự → câu định vị → nhãn CTA.
  - Nút `[URL]` bật lò xo, con trỏ bấm, gợn bấm; một gợn nhắc lại và nút thở nhẹ tới hết phim.

## 3. Công thức dùng (từ MOTION-PRESETS.json)

Đại lượng pixel của mẫu đổi theo **em (cỡ chữ)** để giữ đúng tỉ lệ chuyển động (mẫu R1: Position 300 trên chữ 300 px = 1,0 em). Influence giữ nguyên số gốc.

| Mã | Dùng cho | Thông số | Chọn theo | Easing gốc |
|---|---|---|---|---|
| R1 | Headline cảnh 1, 3 | Position [0, 1,0 em], Opacity 0, Blur 0,427 em | Từ | Start 0→100 trong 30 khung; Out 75,217 % / In 75,121 % |
| R2 | Phụ, cụm nhấn, định vị, nhãn CTA | [0, 0,667 em], Opacity 0, Blur 0,667 em | Dòng | 75,322 % / 75,664 % |
| R3 | "Và nhiều hơn thế nữa!", "OPA Agent", "[URL]" | [0, 0,711 em], Opacity 0, Blur 0,356 em | Ký tự | Vào 75,217 % / 75,603 % |
| R5 | Gạch đầu dòng cảnh 2, tính năng cảnh 3, "Không cần…" cảnh 4 | [2,0 em, 0], Opacity 0, Blur 1,0 em | Dòng | 60,752 % / 60,174 % |
| R6 | Cột chữ cảnh 3 thoát | Scale cấp Scene 100 → 86 → 0 | — | Out 0,01 % / In 100 % rồi Out 100 % / In 15,133 % |
| R10 | Mở phiếu POS (cảnh 2), mở bảng OPA Agent (cảnh 3) | Size khối matte 0 → đủ, track matte alpha | — | Out 15,236 % / In 100 % |
| Khối nhấn | "Mỗi ngày?", "Chỉ 1 kết nối —" | Quét từ trái 8 khung; đệm trái 0,12 em, phải 0,22 em, cao 1,26 em; chữ trên khối là bản sao + Fill + track matte | — | EASE_IN_SCENE (0,2; 0,8; 0,2; 1) |
| Lò xo OPA | Icon, tin nhắn, nút, mõm và sừng Bò | Damping 12, stiffness 100: vọt khoảng 9,5 %, đỉnh 0,39 s | — | Không áp vào chữ |

- Transform Opacity của mọi text layer giữ 100; độ mờ 0 nằm ở Animator, đúng như mẫu.
- Blur của chữ là Text Animator Blur; motion blur theo màn trập chỉ bật cho layer chuyển động nhanh.

## 4. Bảng theo cảnh

| Cảnh | Chữ chính xác | Vai trò | Font, cỡ hiệu dụng | Selector, transform | Matte, effect | Quan hệ với hình |
|---|---|---|---|---|---|---|
| 1 | BẠN MẤT / BAO NHIÊU / THỜI GIAN | Headline (tiêu điểm) | Be Vietnam Pro ExtraBold 126 px, dòng 166 | R1 theo từ, ra Start 100→0 | Không | Cột phải x 1010; máy quay đẩy làm bay khỏi khung |
| 1 | Để trả lời khách và lên đơn / Trên Pancake | Phụ | Medium 56 px | R2 theo dòng | Không | Dưới headline 46 px |
| 1 | Mỗi ngày? | Cụm nhấn | Fraunces OPA ExtraBold Italic 80 px | R2 + khối trắng quét, chữ xanh trên khối | Track matte alpha theo khối | Chốt câu hỏi, cùng nhịp đồng hồ |
| 2 | Hàng chục cuộc chat bỏ dở · Trả lời lặp đi lặp lại · Lên đơn POS thủ công | Ba mục song song | SemiBold 50 px, trắng | R5 từ phải; icon "!" lò xo | Không | Mỗi mục khớp một nhịp UI: hộp thư cuộn, câu trả lời lặp, phiếu POS |
| 2 | Còn size M không shop? · Giá bao nhiêu? · Check bill giúp em | Chữ trong UI | Medium 32 px | Dòng tin trượt vào, danh sách cuộn | Mask chữ nhật cắt vùng danh sách | Comp `DONG_TIN_1–3`: sửa một lần đổi mọi lần lặp |
| 3 | Chỉ 1 kết nối — | Cụm nhấn | Fraunces 80 px | R2 + khối xanh, chữ trắng | Track matte | Cùng lúc chip "Pancake POS" cắm vào |
| 3 | OPA tự động hóa toàn bộ / Quy trình bán hàng / Trên Pancake: | Headline | ExtraBold 56 px, dòng 74 | R1 theo từ | Không | Dưới cụm nhấn 34 px |
| 3 | 5 tính năng (nguyên văn) | Mục song song | Medium 40 px, icon tròn xanh 52 px | R5 + icon lò xo | Không | Mỗi dòng ứng một hàng minh họa trong bảng OPA Agent |
| 3 | Và nhiều hơn thế nữa! | Câu chốt | ExtraBold 44 px, xanh | R3 theo ký tự | Không | Cả cột thoát R6 |
| 4 | Không cần tạo App / Facebook phức tạp · Không cần gõ lại một câu hỏi / Hàng trăm lần · Không cần copy-paste từng / Số điện thoại, địa chỉ vào POS | Ba mục song song | Medium 48 px, dòng 64, icon tích 70 px | R5 + icon lò xo | Không | Khớp lời đọc từng vế; bên trái tích bay lên |
| 5 | OPA Agent | Tên (display) | ExtraBold 128 px, trắng | R3 theo ký tự | Không | Cạnh Bò trắng |
| 5 | AI bán hàng cho shop dùng Pancake | Định vị | Medium 46 px | R2 | Không | — |
| 5 | Thử miễn phí ngay tại: + [URL] | CTA | SemiBold 40 px; nút ExtraBold 48 px | R2, R3, lò xo, con trỏ, gợn | Không | Link thật điền vào `TXT_S5_URL` |

<!-- BANG-TU-DONG:BAT-DAU (sinh bởi tools/bang_khung.py từ build/_report.json, không sửa tay) -->
### Bảng thời gian chữ theo khung master

| Text comp | Công thức | Cỡ chữ | Bắt đầu vào | Hiện đủ | Bắt đầu ra | Hết |
|---|---|---:|---|---|---|---|
| TXT_S1_HEADLINE | R1 theo từ | 126 px | f4 (0,13 s) | f34 (1,13 s) | f122 (4,07 s) | f150 (5,00 s) |
| TXT_S1_PHU | R2 theo dòng | 56 px | f28 (0,93 s) | f58 (1,93 s) | f120 (4,00 s) | f146 (4,87 s) |
| TXT_S1_NHAN | R2 theo dòng | 80 px | f52 (1,73 s) | f82 (2,73 s) | f120 (4,00 s) | f146 (4,87 s) |
| TXT_S2_Y1 | R5 dòng từ phải | 50 px | f174 (5,80 s) | f204 (6,80 s) | f370 (12,33 s) | f396 (13,20 s) |
| TXT_S2_Y2 | R5 dòng từ phải | 50 px | f246 (8,20 s) | f276 (9,20 s) | f370 (12,33 s) | f396 (13,20 s) |
| TXT_S2_Y3 | R5 dòng từ phải | 50 px | f318 (10,60 s) | f348 (11,60 s) | f370 (12,33 s) | f396 (13,20 s) |
| TXT_S3_NHAN | R2 theo dòng | 80 px | f413 (13,77 s) | f443 (14,77 s) | theo chuyển cảnh | — |
| TXT_S3_HEADLINE | R1 theo từ | 56 px | f425 (14,17 s) | f455 (15,17 s) | theo chuyển cảnh | — |
| TXT_S3_TINH_NANG_1 | R5 dòng từ phải | 40 px | f449 (14,97 s) | f479 (15,97 s) | theo chuyển cảnh | — |
| TXT_S3_TINH_NANG_2 | R5 dòng từ phải | 40 px | f477 (15,90 s) | f507 (16,90 s) | theo chuyển cảnh | — |
| TXT_S3_TINH_NANG_3 | R5 dòng từ phải | 40 px | f505 (16,83 s) | f535 (17,83 s) | theo chuyển cảnh | — |
| TXT_S3_TINH_NANG_4 | R5 dòng từ phải | 40 px | f533 (17,77 s) | f563 (18,77 s) | theo chuyển cảnh | — |
| TXT_S3_TINH_NANG_5 | R5 dòng từ phải | 40 px | f561 (18,70 s) | f591 (19,70 s) | theo chuyển cảnh | — |
| TXT_S3_CHOT | R3 theo ký tự | 44 px | f585 (19,50 s) | f615 (20,50 s) | theo chuyển cảnh | — |
| TXT_S4_Y1 | R5 dòng từ phải | 48 px | f672 (22,40 s) | f702 (23,40 s) | f856 (28,53 s) | f882 (29,40 s) |
| TXT_S4_Y2 | R5 dòng từ phải | 48 px | f720 (24,00 s) | f750 (25,00 s) | f856 (28,53 s) | f882 (29,40 s) |
| TXT_S4_Y3 | R5 dòng từ phải | 48 px | f766 (25,53 s) | f796 (26,53 s) | f856 (28,53 s) | f882 (29,40 s) |
| TXT_S5_TEN | R3 theo ký tự | 128 px | f912 (30,40 s) | f942 (31,40 s) | theo chuyển cảnh | — |
| TXT_S5_DINH_VI | R2 theo dòng | 46 px | f934 (31,13 s) | f964 (32,13 s) | theo chuyển cảnh | — |
| TXT_S5_NHAN_CTA | R2 theo dòng | 40 px | f956 (31,87 s) | f986 (32,87 s) | theo chuyển cảnh | — |
| TXT_S5_URL | R3 theo ký tự | 48 px | f972 (32,40 s) | f996 (33,20 s) | theo chuyển cảnh | — |

Bản dựng: 46 comp, 388 expression, lỗi expression: 0, lỗi dựng: 0.

### SFX theo chuyển động (chưa có giọng đọc; bảng đầy đủ kèm lý do: `audio/BANG-CUE-AM-THANH.md`)

| Âm | Đỉnh (khung master) | Mức |
|---|---|---:|
| Tin nhan bat 1 | f2 (0,07 s) | -11 dB |
| Tin nhan bat 2 | f12 (0,40 s) | -11 dB |
| Dong ho tac 15 | f15 (0,50 s) | -11.1 dB |
| Tin nhan bat 3 | f21 (0,70 s) | -11 dB |
| Tin nhan bat 4 | f29 (0,97 s) | -11 dB |
| Tin nhan bat 5 | f36 (1,20 s) | -11 dB |
| Tin nhan bat 6 | f42 (1,40 s) | -11 dB |
| Dong ho tac 45 | f45 (1,50 s) | -11.1 dB |
| Dong ho tich 60 | f60 (2,00 s) | -11.1 dB |
| Dong ho tac 75 | f75 (2,50 s) | -11.1 dB |
| Khoi nhan quet (Moi ngay) | f79 (2,63 s) | -13.1 dB |
| Dong ho tich 90 | f90 (3,00 s) | -11.1 dB |
| Dong ho tac 105 | f105 (3,50 s) | -11.1 dB |
| Dong ho tich 120 | f120 (4,00 s) | -11.1 dB |
| Dong ho tac 135 | f135 (4,50 s) | -11.1 dB |
| Tin moi 1 | f171 (5,70 s) | -14.2 dB |
| Canh bao 1 | f176 (5,87 s) | -13.9 dB |
| Tin moi 2 | f189 (6,30 s) | -14.2 dB |
| Tin moi 3 | f213 (7,10 s) | -14.2 dB |
| Tin moi 4 | f237 (7,90 s) | -14.2 dB |
| Canh bao 2 | f248 (8,27 s) | -13.9 dB |
| Tra loi lap 1 | f252 (8,40 s) | -11 dB |
| Tin moi 5 | f263 (8,77 s) | -14.2 dB |
| Tra loi lap 2 | f274 (9,13 s) | -11 dB |
| Tin moi 6 | f285 (9,50 s) | -14.2 dB |
| Tra loi lap 3 | f296 (9,87 s) | -11 dB |
| Tin moi 7 | f307 (10,23 s) | -14.2 dB |
| Canh bao 3 | f320 (10,67 s) | -13.9 dB |
| Tin moi 8 | f335 (11,17 s) | -14.2 dB |
| Go phim 1 | f346 (11,53 s) | -2.6 dB |
| Go phim 2 | f349 (11,63 s) | -3.6 dB |
| Go phim 3 | f352 (11,73 s) | -2.6 dB |
| Tin moi 9 | f355 (11,83 s) | -14.2 dB |
| Go phim 4 | f367 (12,23 s) | -3.6 dB |
| Go phim 5 | f370 (12,33 s) | -2.6 dB |
| Tin moi 10 | f373 (12,43 s) | -14.2 dB |
| Go phim 6 | f376 (12,53 s) | -3.6 dB |
| Bam luu (than) | f381 (12,70 s) | -8 dB |
| Bam luu (tach) | f381 (12,70 s) | -19.9 dB |
| Bam luu (nha) | f385 (12,83 s) | -11.6 dB |
| Bo OPA lao vao | f388 (12,93 s) | -19.8 dB |
| Dia sang bat | f393 (13,10 s) | -11.8 dB |
| Swell sang ngay | f404 (13,47 s) | -15.9 dB |
| Bang OPA mo | f415 (13,83 s) | -12.2 dB |
| Khoi nhan quet (1 ket noi) | f436 (14,53 s) | -13.1 dB |
| Bo dap dau bang | f441 (14,70 s) | -11.9 dB |
| Tinh nang 1 | f451 (15,03 s) | -12.5 dB |
| Ket noi Pancake POS | f457 (15,23 s) | -18.7 dB |
| Tinh nang 2 | f479 (15,97 s) | -12.5 dB |
| Tinh nang 3 | f507 (16,90 s) | -12.5 dB |
| Tinh nang 4 | f535 (17,83 s) | -12.5 dB |
| Tinh nang 5 | f563 (18,77 s) | -12.5 dB |
| Nut gat tiep quan | f574 (19,13 s) | -11.5 dB |
| Cot chu thu R6 | f639 (21,30 s) | -16.8 dB |
| Nhan vat troi len | f669 (22,30 s) | -18.2 dB |
| Dau tich 1 | f674 (22,47 s) | -15.1 dB |
| Dau tich 2 | f722 (24,07 s) | -15.1 dB |
| Dau tich 3 | f768 (25,60 s) | -15.1 dB |
| Khung xanh no tran | f898 (29,93 s) | -15.9 dB |
| Sonic logo OPA | f904 (30,13 s) | -15.4 dB |
| Nut CTA bat | f966 (32,20 s) | -11.7 dB |
| Bam nut CTA (than) | f1025 (34,17 s) | -10.4 dB |
| Bam nut CTA (tach) | f1025 (34,17 s) | -15.1 dB |
| Bam nut CTA (nha) | f1030 (34,33 s) | -10.6 dB |
<!-- BANG-TU-DONG:KET-THUC -->

## 5. Cấu trúc project (`project/OPA-Agent-Pancake_v01.aep`)

```
00_MASTER/                     OPA_AGENT_MASTER_16x9: 5 cảnh nối tiếp, GIONG DOC (1023.MP3, +2,6 dB), MARKER CAU THOAI, AM THANH (SFX + nhạc)
01_CANH (scene)/               S1_MO_DAU, S2_NOI_DAU, S3_GIAI_PHAP, S4_GIAI_PHONG, S5_CTA — mỗi cảnh có null CAM
02_TITLE (thiet ke chu)/       TITLE_S1…S5: vị trí, offset thời gian, khối nhấn, icon đi kèm chữ
03_EDIT_CHU (sua chu o day)/   TXT_*: mỗi comp một layer "TEXT" có Text Animator; DONG_TIN_1–3: câu hỏi trong hộp thư
04_HINH/                       ART_CHU_SHOP_*, ART_MASCOT_BO_OPA(_HIEN), UI_* (hộp thư, danh sách tin, phiếu POS, bảng OPA Agent)
05_CONTROL (mau)/              CONTROL: null BRAND, 6 Color Control; mọi màu shape nối bằng expression
06_AM_THANH/                   AM_THANH_SFX_NHAC: nhạc nền (dưới cùng) + 68 layer SFX + file WAV (assets/sfx, assets/music)
```

- **Đổi chữ:** mở `03_EDIT_CHU` → comp `TXT_…` → sửa layer `TEXT`. Khối nhấn và bong bóng tin nhắn tự giãn theo chữ (`sourceRectAtTime`). Chữ trong UI minh họa khác (chip, nhãn) nằm trong comp `UI_…`.
- **Đổi màu:** sửa Color Control trong `CONTROL > BRAND`; màu chữ đặt trực tiếp trên layer chữ.
- **Giọng đọc:** layer `GIONG DOC (1023.MP3 cua ban)` trong master, từ 0 s, gain +2,6 dB; thay giọng: chạy lại `tools/am_thanh_cues.py` với file mới (tham số thứ hai) rồi dựng lại; marker từng câu ở layer `MARKER CAU THOAI`.
- **Đổi âm:** sửa cue (âm, khung, mức đích) trong `tools/am_thanh_cues.py` → `python -I tools/am_thanh_cues.py "/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx"` (chép file, tính gain, sinh `build/data/am_thanh_cues.jsxinc` và bảng cue) → dựng lại. Nhạc nền: `python tools/audio/score_agent.py ae/opa-agent/assets/music/nhac-nen-opa-agent.wav` (chạy trong thư mục gốc OPA). Khi có giọng đọc: kéo vào master, căn theo marker, giữ nhạc như cũ, rồi chuẩn hoá cả bản về −16 LUFS, đỉnh thật ≤ −2 dBTP.
- **Dựng lại từ đầu:** `python -I tools/ae.py build` (JSX trong `build/`, chạy trong phiên AE headless riêng, không đụng AE đang mở). Render: `python -I tools/ae.py render --comp OPA_AGENT_MASTER_16x9 --start 0 --end 1079 --out …`.
- **Font cần cài:** Be Vietnam Pro (ExtraBold, SemiBold, Bold, Medium) và `assets/fonts/FrauncesOPA-ExtraBoldItalic.ttf` (Fraunces Italic wght 800, Google Fonts v38, OFL).
- **Plugin:** không dùng plugin ngoài; chỉ effect gốc của AE (Fill, Color Control).

<!-- KIEM:BAT-DAU -->
## 6. Tự kiểm và rà chéo (bản v08 = b13, 21/10/2026)

File: `out/review/_ban-cu/OPA-Agent-Pancake_v08.mp4` (H.264 1920×1080, 30 fps, 1.080 khung, gắn nhãn BT.709; AAC 48 kHz chỉ có SFX bộ cũ; hình dùng tiếp ở v09). Ảnh: `KHUNG-HIEN-DU_v08.png` (5 khung đã hiện đủ), `TO-KHUNG-1s_v08.png` (1 khung mỗi giây).

| Nấc | Cách kiểm | Kết quả |
|---|---|---|
| 1. Dựng | `tools/ae.py build`, buộc tính mọi expression rồi gom lỗi | 0 lỗi dựng, 0 lỗi expression · 46 comp · 388 expression |
| 2. Khung đã hiện đủ | 5 khung 3,5 / 12,0 / 20,6 / 28,4 / 35,6 s, xem bằng mắt | Đạt |
| 3. Tờ khung, điểm nối | Tờ 1 khung/giây; dải khung gốc ở 4 điểm nối (140–165, 386–412, 630–670, 880–915), Bò đáp đầu bảng (405–442), phiếu POS (316–356), hơi cà phê | Đạt sau 4 vòng dựng (b10 → b13) |
| 4. Chữ | `tools/qa_chu.py` trên chữ trong project: viết hoa đầu dòng, cỡ ≥ 28 px, font trong bộ, Fraunces chỉ ở cụm nhấn, mục song song cùng kiểu, không font thay thế | Đạt · 31 layer · 39 dòng |
| 5. Màu | Giải mã BT.709, lấy mẫu nền và khối trang trí cả 5 cảnh | Đúng bảng OPA, lệch ≤ 3 mức do mã hoá (#003998 ≈ #003C99, #0067FF ≈ #0068FF) |
| 6. Chuyển động | `tools/v2w/metrics.py --no-flow` (thước đo của V2) | Tĩnh B 0,46 % · Tĩnh A 0 · chuỗi đứng yên dài nhất 2 khung · cắt cứng 0 → **đạt** |
| 7. Âm thanh (chỉ SFX) | ebur128, true peak, đỉnh tức thời; lệch đỉnh SFX so với khung hình | −28,0 LUFS · −8,8 dBTP · M lớn nhất −20,9 LUFS · mọi đỉnh trễ đều +0,63 khung (21 ms, độ trễ mồi AAC của AE) |
| Rà chéo | Agent Q hình–chữ trên b7 (14 mục), Q5 âm thanh trên b7, Q hình–chữ lần 2 trên b11, lần 3 trên b13 | Lần 2: 10/12 lỗi cũ đã hết; tìm thêm Bò mất 1 khung ở 441 (có từ b8), đĩa sáng còn khựng, Bò cất cánh giật, hơi cà phê pha độ mờ → sửa ở b13. Điểm lần 2: chuyển động 7,5 · chữ 8,5 · thương hiệu 8 · kể chuyện 8,5. Lần 3: cả 4 chỗ đạt (đĩa phủ đều 33→98 % qua 393–404, phủ kín đúng 404; Bò cất cánh 1→19→44→63 px/khung), không lỗi cần sửa |

**Sửa trong vòng hoàn thiện (theo rà chéo b7, b11 và tự kiểm b10–b13):**
- Nối 1→2: tin nhắn trắng nở phủ kín khung cuối cảnh 1, cảnh 2 tan ra từ trắng (hết cắt cứng 149→150).
- Đĩa sáng 2→3 đi cùng Bò, bật che trọn Bò rồi nở đều 11 khung thay vì loé 3 khung; Bò đổi xanh đúng khung đĩa bật.
- Bò cảnh 3 giữ xanh tới khung đáp (hết mất Bò ở 441), cất cánh từ tốc độ 0; hơi cà phê thành nét trắng đặc chạy bằng trim.
- Nối 3→4: khung bảng hoá xanh tại chỗ rồi dời về khung cảnh 4 (hết chồng lệch, hết mép bảng ló ra); nhân vật cảnh 4 trồi từ mép dưới khung.
- Máy quay cảnh 2, 3, 4 đổi hướng trôi để khối chính cách lề (mép phải chữ cảnh 4 ≤ x 1788, lề phải ≥ 131 px); cột chữ cảnh 3 hạ 40 px.
- Nhịp chữ: tính năng cảnh 3 cách 28 khung (hàng minh hoạ bật cùng nhịp), mục 3 cảnh 4 vào sớm 24 khung, "OPA Agent" vào ở 30,4 s.
- Phiếu POS có viền xanh ngay khi mở; khối trang trí màu đặc; ping chip "Pancake POS" tách khỏi tick tính năng 1.
- Thư viện dựng: keyframe "LINEAR" trước đây bị AE làm êm hai đầu (trôi máy quay, kim đồng hồ chậm dần ở đầu, cuối); nay chạy đều đúng ý.

**Ghi nhận, để nguyên:** "Lên đơn POS thủ công" (cảnh 2) đọc trọn ~1,4 s, ngắn nhất phim, vì đĩa sáng 2→3 phủ cột chữ từ 393; viền phiếu POS chạm nút lưu ở 326–333 (chỉ thấy khi soi từng khung); khung 404–405 gần trùng (Bò lấy đà, 1 khung).

**Chưa kiểm:** chưa nghe bằng tai (chỉ đo); chưa mở project trong AE có giao diện (project dựng và render bằng phiên AE riêng, không đụng AE đang mở của bạn); chưa có giọng đọc nên chưa trộn master −16 LUFS.

### 6b. Âm thanh v09 (SFX theo chuyển động + nhạc nền, 22/10/2026)

File: `out/review/OPA-Agent-Pancake_v09.mp4` (= b18). Hình trùng v08 (PSNR trung bình 104 dB, thấp nhất 78 dB), chỉ thay âm. Bảng cue đầy đủ kèm lý do, mức và nguồn research: `audio/BANG-CUE-AM-THANH.md`.

| Nấc | Cách kiểm | Kết quả |
|---|---|---|
| Kho, chọn âm | Đo cả 2.982 file (`tools/phan_tich_sfx.py` → `audio/kho_sfx_do.csv`): thời lượng, đỉnh, đỉnh thật, M, độ to tích hợp, độ sáng; đo cao độ các âm có nốt | 68 cue, 30 file; âm có cao độ đều trong giọng La trưởng (3 file dịch cao độ); kho không có bài nhạc nào đủ dài |
| Đồng bộ | Đỉnh từng file đặt vào khung chuyển động; đo lại trên MP4 | Mọi cue trễ đều 0,64 khung (độ trễ AAC của AE), không cue nào lệch riêng |
| Mức | ebur128 trên MP4 (chưa có giọng) | Nhạc riêng −31,1 LUFS khi phát (đích −31); SFX + nhạc −28,0 LUFS, LRA 4,9 LU; độ to ngắn hạn lớn nhất −25,0 LUFS (+3,0 LU so với tích hợp; EBU R 128 s1 cho tới +5) |
| Đỉnh | Đỉnh thật cả bản; dựng lại stem SFX, đo ±40 ms quanh mỗi cue (tính cả âm chồng) | Cả bản −10,9 dBTP; stem SFX ≤ −12,0 dBTP ở mọi cue |
| Nhô trên nhạc | M 400 ms và RMS 50 ms của cue so với nhạc tại chỗ | Mọi cue nhô ≥ +2,6 dB ở cửa sổ 50 ms (Q5 đo b17) |
| Nhạc nền | `tools/audio/score_agent.py`: LRA, lọc 100 Hz, −3 dB ở 2 kHz, vào 1 s, tắt 1,5 s, lặng tuyệt đối 13,1–13,5 s và 29,93–30,4 s | Đạt (Q5 dựng lại trùng từng bit; không click ở chỗ lặng) |
| Rà chéo Q5 | b17: 68 cue đúng khung, nhạc đạt; 4 lỗi cần sửa (2 cú bấm chồng lớp vượt trần đỉnh, giấy POS trễ 7–9 khung, chuông "xong" là Sol trưởng, glass lệch ¼ cung) và 5 nên sửa → sửa hết ở b18 | b18: cả 5 nhóm đã hết, không lỗi mới cần sửa; stem SFX lớn nhất −11,95 dBTP; chuông "xong" thành A4–C#5–E5 (lệch ≤ 2 cent), glass thành A–C#–F# (≤ 8 cent); không cặp âm nào cách dưới 3 khung; SFX lớn nhất −24,2 LUFS (8,2 LU dưới giọng). Điểm: an toàn đỉnh 8 (từ 5), hợp giọng 8 (từ 6). Ghi nhận: nốt đầu chuông "xong" vào trước icon 7 khung (đỉnh đúng icon); riser sớm 2 khung so với khung trắng để chừa đầu câu 2; press/typing/release lệch khoảng 35 cent (tiếng ngắn) |

**Khi lồng giọng đọc (bắt buộc):**
- Đặt giọng khoảng −16,3 LUFS: SFX + nhạc cộng thêm khoảng 0,3 LU để bản cuối ra đúng −16.
- Master cuối qua limiter đỉnh thật −2 dBTP: trần −12 dBTP mỗi cue không đủ nếu đỉnh giọng −3 dBTP trùng pha với SFX (Q5 tính trường hợp xấu nhất).
- Câu 2 bắt đầu từ 5,04 s trở đi (riser đỉnh ở 4,9 s); câu 5 vào sau logo âm thanh khoảng 0,3 s.
- Nghe lại cụm 12,6–13,4 s (bấm lưu, whoosh Bò, thịch, swell): M −24 LUFS, gần ngưỡng 8 LU dưới giọng.

### 6c. Giọng đọc, URL và bản giao v10 (23/10/2026)

File: `out/review/OPA-Agent-Pancake_v10.mp4` (bản dựng b23, master theo A.10 bằng `master.py`). Ảnh: `KHUNG-HIEN-DU_v10.png`, `TO-KHUNG-1s_v10.png`; bản nghe thử nhẹ `OPA-Agent-Pancake_v10_nghe-thu-720p.mp4` (âm giữ nguyên).

| Nấc | Cách kiểm | Kết quả |
|---|---|---|
| Lời so kịch bản | whisper large-v3 (`audio/giong/whisper.json`) so lời khóa | Khớp; whisper nghe nhầm "size" → "Sai", "tồn" → "tuần", "POS" → "Post". Câu 5 đọc "ngay tại Oping" (kịch bản: "[URL]") |
| Mốc câu | Năng lượng sau khoảng nghỉ | 0,10 / 4,38 / 14,09 / 22,62 / 30,33 s. Câu 2 dài 9,4 s nên vào trước cảnh 2 0,6 s (lời đi trước hình); "Giờ đây" vào sau cú đáp nhạc cảnh 3 0,6 s |
| SFX quanh lời | Mỗi cue: rơi lúc nói hay nghỉ, dưới giọng bao nhiêu LU (cột Lời, Dưới giọng trong bảng cue) | 43/64 cue rơi lúc nói, thấp hơn giọng ≥ 9,7 LU. Bỏ riser 4,9 s và tiếng giấy POS (đè "tưởng tượng", "size"); hạ khối nhấn, whoosh Bò, swell, collapse; dời whoosh nhân vật và logo âm thanh vào khoảng nghỉ. Sau rà chéo: bỏ 2 tiếng chip bay, hạ lớp tách của cú bấm lưu 6 dB (dòng Rà chéo Q5) |
| Nhạc dưới giọng | Cửa sổ 3 s và 400 ms trên từng lớp | 3 s: thấp nhất 11,7 LU, trung vị 14,9 LU. Cửa sổ 400 ms dưới 10 LU chỉ ở chỗ vắt qua khoảng nghỉ |
| Rõ lời | whisper trên bản giao so với giọng riêng | Cùng 152 từ, khớp 99,3 %, độ tin cậy trung bình 0,975 so 0,976 (b20 và b23 như nhau; whisper không nhạy với SFX đè phụ âm, phần đó đo ở dòng Rà chéo Q5). Chữ khóa: giọng trên (nhạc + SFX) từ 10,7 LU ("Giờ đây") tới 17,3 LU ("OPA") |
| Đồng bộ | Tương quan chéo giọng gốc với bản giao | Trễ 21,3 ms (0,64 khung) như mọi SFX: độ trễ AAC của AE, dưới ngưỡng nghe lệch |
| Master | `master.py` (loudnorm hai lượt, chỉ nhận tuyến tính), đích −16,1 như ca B8 | Tuyến tính; file giao −16,0 LUFS, đỉnh thật −3,5 dBTP, LRA 1,2 LU; ngắn hạn lớn nhất cao hơn tích hợp 1,4 LU |
| Hình | Đo chuyển động V2; dải khung cảnh 5 | Đạt (Tĩnh B 0,46 %, Tĩnh A 0, cắt cứng 0). Nút giãn theo URL (742 px), con trỏ bấm sau chữ, không đè URL |
| Rà chéo Q5 | Agent soát bản v10 đầu (dựng b20): rõ lời, cân mức, đồng bộ, đỉnh; đo dải 2–8 kHz quanh đầu âm tiết | Điểm: rõ lời 8, cân mức 9, đồng bộ 8, an toàn đỉnh 10. **Cần sửa:** 2 tiếng chip bay (11,30 / 11,97 s) đè đầu âm tiết "rồi" và /t/ của "từng". **Nên sửa:** lớp tách của cú bấm lưu (12,70 s) chỉ thấp hơn /s/ của "sẽ" 3,6 dB. **Đã sửa ở b23 (bản giao này):** bỏ 2 chip (dời sang khung 336/356 thì chỉ cách ping tin mới 1 khung, nghe thành tiếng đúp); hạ lớp tách 6 dB. Đo lại dải 2–8 kHz: chỗ chip không còn SFX (trước đó chip 2 to hơn phụ âm 15,5 dB); lớp tách thấp hơn /s/ 8,8 dB. Âm b23 chỉ khác b20 ở đúng 3 chỗ đó, còn lại trùng từng mẫu; hình trùng b22 (khung 84–130 lệch nhiễu mã hóa, PSNR ≥ 78 dB). **Ghi nhận, giữ:** whoosh nhân vật (22,3 s) trễ hình 5–7 khung để đuôi chữ "Agent" sạch |

**Đã thử rồi bỏ:** dìm nhạc −4 dB dưới "OPA Agent" cuối câu 3 vì whisper tin chữ "Agent" giảm 0,80 → 0,58. Dìm xong vẫn 0,56, và giọng đã cao hơn nhạc + SFX 15,9 LU ở đó, nên đây là dao động của whisper với từ tiếng Anh; giữ nhạc đúng bản đã duyệt.
<!-- KIEM:KET-THUC -->

<!-- ===== /file: ae-script-builder/examples/opa-agent/KHUNG-DUNG.md ===== -->

<!-- ===== file: ae-script-builder/examples/opa-agent/README.md ===== -->

# Ca mẫu nhánh A: "OPA Agent × Pancake" (bản chụp ngày 26/10/2026)

Video giải thích 2D, 16:9, 1920×1080, 30 fps, 36 s, 5 cảnh, dựng hoàn toàn bằng JSX trong phiên AE riêng.
- Minh duyệt hình bản v08 và âm bản v09 ngày 22/10.
- Bản v10 (23/10) có giọng đọc và URL thật. Đã tự kiểm và rà chéo âm. Còn chờ Minh tạo lại giọng câu 5 (đang đọc "Oping"), và chờ Hùng duyệt hình.

Đây là bản chụp code và tài liệu để agent mới đọc, chép. Dự án sống nằm ở `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/OPA-Motion-graphic-mascot/ae/opa-agent`.

| Có trong gói | Không có trong gói (lấy ở dự án sống) |
|---|---|
| `build/` (lib, main, 7 cảnh, dữ liệu sinh) | `assets/sfx` (2,6 MB), `assets/music` (6,6 MB), `assets/voice` (9,9 MB) |
| `tools/*.py`, `tools/seed/empty-ae26.aep` | `project/*.aep`, `out/` (MP4, ảnh) |
| `assets/fonts/FrauncesOPA-ExtraBoldItalic.ttf` (OFL) | `audio/kho_sfx_do.csv` nằm ở `data/` của skill |
| `KHUNG-DUNG.md`: brief, phương án, bảng cảnh, cấu trúc project, cách sửa, kết quả kiểm | |
| `audio/BANG-CUE-AM-THANH.md`: 64 cue, mức, lý do, nguồn research | |

- Dựng lại từ bản chụp này cần chép thêm thư mục `assets/` từ dự án sống, vì `main.jsx` dừng khi thiếu file giọng đọc.
- `tools/ae.py` đã vá ngày 26/10: lệnh `stills` render vào thư mục tạm không dấu cách. Lý do: aerender không ghi được chuỗi ảnh vào đường dẫn có dấu cách.
- `tools/run_ae.ps1` của dự án sống không chép vào đây: nó dùng `-m -r`, cách này không chạy được.

Đọc theo thứ tự: `KHUNG-DUNG.md` mục 1–5 → `build/lib.jsx` → `build/main.jsx` → một cảnh (`build/scenes/s5_cta.jsx` ngắn nhất) → `tools/am_thanh_cues.py` → `audio/BANG-CUE-AM-THANH.md`.

<!-- ===== /file: ae-script-builder/examples/opa-agent/README.md ===== -->

<!-- ===== file: ae-script-builder/examples/opa-agent/audio/BANG-CUE-AM-THANH.md ===== -->

# Bảng cue âm thanh — OPA Agent × Pancake

Sinh bởi `tools/am_thanh_cues.py` (không sửa tay; sửa cue trong file đó rồi chạy lại và dựng lại AE).
Kho SFX: `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx` (CC0 / MIT). Logo âm thanh: bộ âm OPA. Nhạc nền: tự tổng hợp (`tools/audio/score_agent.py`).

**Cột:** khung = khung master (30 fps) mà **đỉnh** âm rơi vào; M đích = độ to tức thời 400 ms muốn có trong bản trộn (LUFS); M = độ to thực sau gain (thấp hơn đích khi bị trần đỉnh thật −12 dBTP giữ lại: âm cực ngắn, đỉnh nhọn); gain = chỉnh trên layer AE; TP = đỉnh thật của toàn bộ SFX trong ±40 ms quanh đỉnh cue (dựng lại stem, đã tính các âm chồng nhau; vượt trần thì cả nhóm cùng khung bị hạ).

**Nhạc nền:** `nhac-nen-opa-agent.wav` · đo −20,5 LUFS → gain −10,50 dB → tích hợp −31 LUFS (15 LU dưới giọng −16 LUFS). Cột **Nhô** = M của cue trừ độ to tức thời của nhạc quanh khung đó (âm ngắn, sáng vẫn nghe rõ khi Nhô hơi âm vì thang 400 ms tính thấp âm cực ngắn).

**Giọng đọc:** `1023.MP3` → `assets/voice/giong-doc-1023.wav` · đo −18,9 LUFS → gain +2,60 dB → −16,3 LUFS. Cột **Lời** = cue rơi lúc đang nói hay khoảng nghỉ; **Dưới giọng** = độ to tức thời của giọng trừ M của cue (chỉ tính lúc đang nói).

## Thang mức (research decibel, 22/10/2026)

| Lớp | Mức trong bản trộn | Căn cứ |
|---|---|---|
| Giọng đọc | −16,3 LUFS trong bản trộn (bản giao chuẩn hoá −16 LUFS, đỉnh thật ≤ −2 dBTP) | Chuẩn Minh chốt; AES TD1008: nhạc −16, lời −18 LUFS; YouTube chuẩn hoá về khoảng −14 LUFS và không kéo bản nhỏ lên |
| Nhạc nền | −31 LUFS tích hợp (15 LU dưới giọng), dải độ to ≤ 5 LU | Quy trình nền 1.2.3 Minh duyệt (giọng luôn cao hơn nền ≥ 10 LU); hướng dẫn trộn phổ biến: nhạc dưới lời 15–25 dB; WCAG 1.4.7 (AAA): nền dưới lời ≥ 20 dB |
| SFX chuyển cảnh, logo | M −24,5 … −27 | Rơi vào khoảng nghỉ giữa các câu; vẫn dưới giọng ≥ 8 LU |
| SFX sự kiện giao diện | M −27 … −31 | Nhô trên nền nhạc tại chỗ 0–4 LU |
| Tiếng nhỏ (đồng hồ, gõ phím, click) | M −33 … −38 | Âm cực ngắn, sáng: nghe rõ dù M thấp |
| Mỗi cue | Đỉnh thật ≤ −12 dBTP | Âm trùng đỉnh giọng đẩy bản trộn quá trần (bài học B8 trong master prompt) |
| Cả bản ngắn (nội dung quảng cáo) | Độ to ngắn hạn 3 s không vượt mức tích hợp quá 5 LU; đỉnh thật ≤ −1 dBTP | EBU R 128 s1 (nội dung ngắn); đo theo ITU-R BS.1770 / EBU Tech 3341 |

Nguồn: [EBU R 128 s1](https://tech.ebu.ch/docs/r/r128s1.pdf) · [EBU R 128](https://en.wikipedia.org/wiki/EBU_R_128) · [AES TD1008 (Production Advice)](https://productionadvice.co.uk/td1008/) · [Telos: loudness cho streaming](https://docs.telosalliance.com/docs/understanding-loudness-for-streaming-audio) · [WCAG 1.4.7](https://www.disabilityworld.org/toolkit/standards/wcag/1-4-7-low-or-no-background-audio/) · [Vidpros: nhạc nền quá to](https://vidpros.com/fix-background-music-too-loud-video/).

## Cảnh 1 · Hook (0–5 s)

| Giây | Khung | Chuyển động | Âm (file trong kho) | M đích | M | Nhô | Lời | Dưới giọng | Gain | TP | Lý do |
|---:|---:|---|---|---:|---:|---:|---|---:|---:|---:|---|
| 0,07 | 2 | Tin nhắn 1 bật lò xo | `03-pops-snaps-elastic/pop-bubble-low-A4.wav` | −28 | −30,1 | +20,5 | nghỉ | — | −11,0 | −12 | Pop A4–C#5–E5 đi lên theo hợp âm La trưởng của nhạc: dồn dập mà vẫn hợp giọng |
| 0,40 | 12 | Tin nhắn 2 bật lò xo | `03-pops-snaps-elastic/pop-bubble-mid-C#5.wav` | −27,5 | −30,7 | +12,0 | nghỉ | — | −11,0 | −12 | Pop A4–C#5–E5 đi lên theo hợp âm La trưởng của nhạc: dồn dập mà vẫn hợp giọng |
| 0,50 | 15 | Đồng hồ nảy mỗi 0,5 s | `04-ui-tech-hud/ui-tick-crisp-E6.wav` | −32 | −33,2 | +6,5 | đang nói | 19,1 | −11,1 | −12,1 | Tích A6 / tắc E6 xen kẽ, ngang nền nhạc: nhịp thời gian trôi, không đè lời |
| 0,70 | 21 | Tin nhắn 3 bật lò xo | `03-pops-snaps-elastic/pop-bubble-high-E5.wav` | −27 | −30,7 | +4,5 | đang nói | 17,0 | −11,0 | −12 | Pop A4–C#5–E5 đi lên theo hợp âm La trưởng của nhạc: dồn dập mà vẫn hợp giọng |
| 0,97 | 29 | Tin nhắn 4 bật lò xo | `03-pops-snaps-elastic/pop-bubble-low-A4.wav` | −26,5 | −30,1 | +3,7 | đang nói | 15,0 | −11,0 | −12 | Pop A4–C#5–E5 đi lên theo hợp âm La trưởng của nhạc: dồn dập mà vẫn hợp giọng |
| 1,20 | 36 | Tin nhắn 5 bật lò xo | `03-pops-snaps-elastic/pop-bubble-mid-C#5.wav` | −26,5 | −30,7 | +3,4 | đang nói | 15,6 | −11,0 | −12 | Pop A4–C#5–E5 đi lên theo hợp âm La trưởng của nhạc: dồn dập mà vẫn hợp giọng |
| 1,40 | 42 | Tin nhắn 6 bật lò xo | `03-pops-snaps-elastic/pop-bubble-high-E5.wav` | −26,5 | −30,7 | +2,6 | đang nói | 14,7 | −11,0 | −12 | Pop A4–C#5–E5 đi lên theo hợp âm La trưởng của nhạc: dồn dập mà vẫn hợp giọng |
| 1,50 | 45 | Đồng hồ nảy mỗi 0,5 s | `04-ui-tech-hud/ui-tick-crisp-E6.wav` | −32 | −33,2 | −0,2 | đang nói | 17,7 | −11,1 | −12 | Tích A6 / tắc E6 xen kẽ, ngang nền nhạc: nhịp thời gian trôi, không đè lời |
| 2,00 | 60 | Đồng hồ nảy mỗi 0,5 s | `04-ui-tech-hud/ui-tick-crisp-A6.wav` | −32 | −33,3 | +0,9 | đang nói | 18,1 | −11,1 | −12 | Tích A6 / tắc E6 xen kẽ, ngang nền nhạc: nhịp thời gian trôi, không đè lời |
| 2,50 | 75 | Đồng hồ nảy mỗi 0,5 s | `04-ui-tech-hud/ui-tick-crisp-E6.wav` | −32 | −33,2 | +1,7 | đang nói | 18,1 | −11,1 | −12 | Tích A6 / tắc E6 xen kẽ, ngang nền nhạc: nhịp thời gian trôi, không đè lời |
| 2,63 | 79 | Khối nhấn trắng quét "Mỗi ngày?" | `04-ui-tech-hud/ui-swish-accent-tick.wav` | −32 | −32 | +3,0 | đang nói | 17,4 | −13,1 | −14,1 | Swish ngắn đúng nhịp quét 8 khung; nằm dưới câu 1 nên hạ còn −32; cùng âm, cùng mức khối nhấn cảnh 3 |
| 3,00 | 90 | Đồng hồ nảy mỗi 0,5 s | `04-ui-tech-hud/ui-tick-crisp-A6.wav` | −32 | −33,3 | +1,2 | đang nói | 17,7 | −11,1 | −12 | Tích A6 / tắc E6 xen kẽ, ngang nền nhạc: nhịp thời gian trôi, không đè lời |
| 3,50 | 105 | Đồng hồ nảy mỗi 0,5 s | `04-ui-tech-hud/ui-tick-crisp-E6.wav` | −32 | −33,2 | +1,7 | đang nói | 15,8 | −11,1 | −12 | Tích A6 / tắc E6 xen kẽ, ngang nền nhạc: nhịp thời gian trôi, không đè lời |
| 4,00 | 120 | Đồng hồ nảy mỗi 0,5 s | `04-ui-tech-hud/ui-tick-crisp-A6.wav` | −32 | −33,3 | +0,9 | nghỉ | — | −11,1 | −12 | Tích A6 / tắc E6 xen kẽ, ngang nền nhạc: nhịp thời gian trôi, không đè lời |
| 4,50 | 135 | Đồng hồ nảy mỗi 0,5 s | `04-ui-tech-hud/ui-tick-crisp-E6.wav` | −32 | −33,2 | +0,5 | nghỉ | — | −11,1 | −12 | Tích A6 / tắc E6 xen kẽ, ngang nền nhạc: nhịp thời gian trôi, không đè lời |

## Cảnh 2 · Nỗi đau (5–13,5 s)

| Giây | Khung | Chuyển động | Âm (file trong kho) | M đích | M | Nhô | Lời | Dưới giọng | Gain | TP | Lý do |
|---:|---:|---|---|---:|---:|---:|---|---:|---:|---:|---|
| 5,70 | 171 | Tin khách mới trượt vào hộp thư | `04-ui-tech-hud/ui-soft-ping-night.wav` | −29,5 | −29,5 | +3,6 | đang nói | 14,2 | −14,2 | −15,2 | Ping A3 trầm "night" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s |
| 5,87 | 176 | Icon "!" của gạch đầu dòng 1 bật | `04-ui-tech-hud/ui-alert-soft-low.wav` | −28,5 | −28,5 | +4,3 | đang nói | 13,1 | −13,9 | −14,8 | Cảnh báo mềm (Rê5, trong giọng La); ba mục song song cùng một âm, cùng mức |
| 6,30 | 189 | Tin khách mới trượt vào hộp thư | `04-ui-tech-hud/ui-soft-ping-night.wav` | −29,5 | −29,5 | +4,3 | đang nói | 12,3 | −14,2 | −15,2 | Ping A3 trầm "night" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s |
| 7,10 | 213 | Tin khách mới trượt vào hộp thư | `04-ui-tech-hud/ui-soft-ping-night.wav` | −29,5 | −29,5 | +3,7 | đang nói | 13,1 | −14,2 | −15,2 | Ping A3 trầm "night" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s |
| 7,90 | 237 | Tin khách mới trượt vào hộp thư | `04-ui-tech-hud/ui-soft-ping-night.wav` | −29,5 | −29,5 | +3,7 | đang nói | 13,6 | −14,2 | −15,2 | Ping A3 trầm "night" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s |
| 8,27 | 248 | Icon "!" của gạch đầu dòng 2 bật | `04-ui-tech-hud/ui-alert-soft-low.wav` | −28,5 | −28,5 | +5,6 | đang nói | 12,9 | −13,9 | −14,9 | Cảnh báo mềm (Rê5, trong giọng La); ba mục song song cùng một âm, cùng mức |
| 8,40 | 252 | Câu trả lời y hệt lần 1 gửi đi | `04-ui-tech-hud/ui-card-snap-dock.wav` | −32 | −33,7 | −0,8 | nghỉ | — | −11,0 | −12,1 | Cùng một tiếng "snap" mỗi lần: nghe ra sự lặp; lần 4 (316) bỏ vì trùng cảnh báo 3 và phiếu POS |
| 8,77 | 263 | Tin khách mới trượt vào hộp thư | `04-ui-tech-hud/ui-soft-ping-night.wav` | −29,5 | −29,5 | +1,5 | nghỉ | — | −14,2 | −15,2 | Ping A3 trầm "night" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s |
| 9,13 | 274 | Câu trả lời y hệt lần 2 gửi đi | `04-ui-tech-hud/ui-card-snap-dock.wav` | −32 | −33,7 | −1,4 | đang nói | 18,0 | −11,0 | −12 | Cùng một tiếng "snap" mỗi lần: nghe ra sự lặp; lần 4 (316) bỏ vì trùng cảnh báo 3 và phiếu POS |
| 9,50 | 285 | Tin khách mới trượt vào hộp thư | `04-ui-tech-hud/ui-soft-ping-night.wav` | −29,5 | −29,5 | +1,9 | nghỉ | — | −14,2 | −15,2 | Ping A3 trầm "night" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s |
| 9,87 | 296 | Câu trả lời y hệt lần 3 gửi đi | `04-ui-tech-hud/ui-card-snap-dock.wav` | −32 | −33,7 | −3,1 | đang nói | 16,5 | −11,0 | −12 | Cùng một tiếng "snap" mỗi lần: nghe ra sự lặp; lần 4 (316) bỏ vì trùng cảnh báo 3 và phiếu POS |
| 10,23 | 307 | Tin khách mới trượt vào hộp thư | `04-ui-tech-hud/ui-soft-ping-night.wav` | −29,5 | −29,5 | +3,3 | đang nói | 12,5 | −14,2 | −15,2 | Ping A3 trầm "night" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s |
| 10,67 | 320 | Icon "!" của gạch đầu dòng 3 bật | `04-ui-tech-hud/ui-alert-soft-low.wav` | −28,5 | −28,5 | +3,0 | nghỉ | — | −13,9 | −14,9 | Cảnh báo mềm (Rê5, trong giọng La); ba mục song song cùng một âm, cùng mức |
| 11,17 | 335 | Tin khách mới trượt vào hộp thư | `04-ui-tech-hud/ui-soft-ping-night.wav` | −29,5 | −29,5 | +1,5 | nghỉ | — | −14,2 | −15,2 | Ping A3 trầm "night" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s |
| 11,53 | 346 | Vạch gõ dài ra trong ô | `04-ui-tech-hud/uisfx-minimal-typing.mp3` | −34 | −34 | −2,9 | đang nói | 20,6 | −2,6 | −14 | Gõ phím rất nhỏ, xen mức ±1 dB; cách ping tin mới (355, 373) ít nhất 3 khung |
| 11,63 | 349 | Vạch gõ dài ra trong ô | `04-ui-tech-hud/uisfx-minimal-typing.mp3` | −35 | −35 | −3,8 | đang nói | 21,9 | −3,6 | −15 | Gõ phím rất nhỏ, xen mức ±1 dB; cách ping tin mới (355, 373) ít nhất 3 khung |
| 11,73 | 352 | Vạch gõ dài ra trong ô | `04-ui-tech-hud/uisfx-minimal-typing.mp3` | −34 | −34 | −2,8 | nghỉ | — | −2,6 | −14 | Gõ phím rất nhỏ, xen mức ±1 dB; cách ping tin mới (355, 373) ít nhất 3 khung |
| 11,83 | 355 | Tin khách mới trượt vào hộp thư | `04-ui-tech-hud/ui-soft-ping-night.wav` | −29,5 | −29,5 | +1,0 | đang nói | 12,9 | −14,2 | −15,2 | Ping A3 trầm "night" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s |
| 12,23 | 367 | Vạch gõ dài ra trong ô | `04-ui-tech-hud/uisfx-minimal-typing.mp3` | −35 | −35 | −4,0 | đang nói | 19,6 | −3,6 | −15 | Gõ phím rất nhỏ, xen mức ±1 dB; cách ping tin mới (355, 373) ít nhất 3 khung |
| 12,33 | 370 | Vạch gõ dài ra trong ô | `04-ui-tech-hud/uisfx-minimal-typing.mp3` | −34 | −34 | −3,4 | đang nói | 17,8 | −2,6 | −14 | Gõ phím rất nhỏ, xen mức ±1 dB; cách ping tin mới (355, 373) ít nhất 3 khung |
| 12,43 | 373 | Tin khách mới trượt vào hộp thư | `04-ui-tech-hud/ui-soft-ping-night.wav` | −29,5 | −29,5 | +1,5 | đang nói | 12,6 | −14,2 | −15,2 | Ping A3 trầm "night" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s |
| 12,53 | 376 | Vạch gõ dài ra trong ô | `04-ui-tech-hud/uisfx-minimal-typing.mp3` | −35 | −35 | −3,8 | đang nói | 18,3 | −3,6 | −14,6 | Gõ phím rất nhỏ, xen mức ±1 dB; cách ping tin mới (355, 373) ít nhất 3 khung |
| 12,70 | 381 | Con trỏ bấm lưu: lớp thân | `04-ui-tech-hud/uisfx-minimal-press.mp3` | −29,5 | −29,5 | +1,8 | đang nói | 13,1 | −8,0 | −13 | Press của bộ minimal (đỉnh không nhọn nên đứng trên nhạc mà vẫn dưới trần đỉnh) |
| 12,70 | 381 | Con trỏ bấm lưu: lớp tách | `04-ui-tech-hud/kenney-mouseclick1.wav` | −46 | −46 | −14,7 | đang nói | 29,6 | −19,9 | −13 | Click chuột Kenney cùng khung, nhập với lớp thân thành một cú bấm; trùng âm /s/ của "sẽ" nên rất nhỏ (Q5 v10) |
| 12,83 | 385 | Con trỏ nhả | `packs/uisfx-themes/minimal/release.mp3` | −32,5 | −32,5 | −0,7 | đang nói | 15,8 | −11,6 | −16,8 | Release của bộ minimal, nhỏ hơn lúc bấm |
| 12,93 | 388 | Bò trắng lao vào từ phải | `01-whooshes-transitions/whoosh-deep-windup.wav` | −31 | −31 | +1,7 | đang nói | 15,3 | −19,8 | −20,7 | Whoosh trầm, đỉnh lúc Bò vừa lọt vào hình và nhanh nhất; nằm dưới "mệt mỏi như thế nào" nên hạ còn −31 |
| 13,10 | 393 | Đĩa sáng bật sau lưng Bò, Bò hoá xanh | `02-impacts-hits/thump-body-punch.wav` | −28 | −30,4 | +5,7 | đang nói | 14,1 | −11,8 | −12 | Tiếng thịch thân trầm cho cú va: rơi đúng khoảng lặng của nhạc |
| 13,47 | 404 | Đĩa nở phủ kín khung (393–404) | `05-risers-builders/swell-tonal-brass-1.0s.wav` | −28 | −28 | +5,8 | nghỉ | — | −15,9 | −16,9 | Swell hợp âm (giọng La) dâng tới khung trắng cuối, nhạc đáp cảnh 3 ngay sau; dưới chữ cuối câu 2 nên −28 |

## Cảnh 3 · Giải pháp (13,5–22 s)

| Giây | Khung | Chuyển động | Âm (file trong kho) | M đích | M | Nhô | Lời | Dưới giọng | Gain | TP | Lý do |
|---:|---:|---|---|---:|---:|---:|---|---:|---:|---:|---|
| 13,83 | 415 | Bảng OPA Agent mở bằng mask | `01-whooshes-transitions/uisfx-glass-expand.mp3` (+155 cent) | −28 | −28 | −0,2 | nghỉ | — | −12,2 | −20,1 | Expand mềm, đỉnh lúc mask mở nhanh nhất; dịch +155 cent về La–Đô♯–Fa♯ cho hợp giọng |
| 14,53 | 436 | Khối nhấn xanh quét "Chỉ 1 kết nối —" | `04-ui-tech-hud/ui-swish-accent-tick.wav` | −32 | −32 | −3,9 | nghỉ | — | −13,1 | −14,1 | Cùng âm, cùng mức khối nhấn cảnh 1; rơi vào khoảng nghỉ 14,46–14,75 s |
| 14,70 | 441 | Bò đáp vào đầu bảng, màu xanh lan ra | `03-pops-snaps-elastic/catch-bright-ring.wav` | −28,5 | −28,5 | −0,2 | nghỉ | — | −11,9 | −12,9 | "Catch" sáng E5: Bò về đúng chỗ |
| 15,03 | 451 | Icon tính năng 1 bật | `04-ui-tech-hud/ui-wood-marimba-tick.wav` | −28 | −28 | +1,0 | đang nói | 13,3 | −12,5 | −13,5 | Marimba A5 ấm, hợp giọng; năm mục song song cùng âm, cùng mức |
| 15,23 | 457 | Chip "Pancake POS" cắm vào, vòng tỏa | `04-ui-tech-hud/ui-chime-question-bell.wav` | −27 | −27 | +1,8 | đang nói | 10,8 | −18,7 | −19,8 | Chuông hai tông sáng (E6–A5) = đã kết nối; âm dày, đỉnh thấp nên nổi trên nhạc thân đầy mà không vượt trần đỉnh (tiếng chốt khóa bị trần giữ, chìm dưới nhạc 3,8 LU); cách tick tính năng 1 sáu khung |
| 15,97 | 479 | Icon tính năng 2 bật | `04-ui-tech-hud/ui-wood-marimba-tick.wav` | −28 | −28 | +1,2 | nghỉ | — | −12,5 | −13,6 | Marimba A5 ấm, hợp giọng; năm mục song song cùng âm, cùng mức |
| 16,90 | 507 | Icon tính năng 3 bật | `04-ui-tech-hud/ui-wood-marimba-tick.wav` | −28 | −28 | +0,6 | đang nói | 12,1 | −12,5 | −13,5 | Marimba A5 ấm, hợp giọng; năm mục song song cùng âm, cùng mức |
| 17,83 | 535 | Icon tính năng 4 bật | `04-ui-tech-hud/ui-wood-marimba-tick.wav` | −28 | −28 | +0,5 | đang nói | 12,5 | −12,5 | −13,5 | Marimba A5 ấm, hợp giọng; năm mục song song cùng âm, cùng mức |
| 18,77 | 563 | Icon tính năng 5 bật | `04-ui-tech-hud/ui-wood-marimba-tick.wav` | −28 | −28 | +1,3 | đang nói | 11,5 | −12,5 | −13,5 | Marimba A5 ấm, hợp giọng; năm mục song song cùng âm, cùng mức |
| 19,13 | 574 | Nút gạt chạy từ Bò sang nhân viên | `04-ui-tech-hud/uisfx-minimal-toggle-on.mp3` | −29,5 | −29,5 | −0,7 | đang nói | 12,6 | −11,5 | −19,3 | Toggle-on lúc nút gạt gần tới đích (đã đi 77 % ở 574) |
| 21,30 | 639 | Cột chữ thu R6, bảng hoá xanh | `01-whooshes-transitions/uisfx-glass-collapse.mp3` (+155 cent) | −34 | −34 | −4,2 | đang nói | 18,0 | −16,8 | −24,8 | Collapse mềm cùng cú thu đầu của R6, dịch +155 cent như expand; nằm dưới chữ "OPA Agent" cuối câu 3 nên hạ còn −34 |
| 22,30 | 669 | Chủ shop trồi lên trong khung xanh | `01-whooshes-transitions/whoosh-light-airy.wav` | −29 | −29 | +2,9 | nghỉ | — | −18,2 | −17,5 | Whoosh nhẹ đi lên, đỉnh trong khoảng nghỉ 22,19–22,62 s, trước câu 4 hơn 0,3 s (âm nhiều 2–8 kHz) |

## Cảnh 4 · Giải phóng (22–30 s)

| Giây | Khung | Chuyển động | Âm (file trong kho) | M đích | M | Nhô | Lời | Dưới giọng | Gain | TP | Lý do |
|---:|---:|---|---|---:|---:|---:|---|---:|---:|---:|---|
| 22,47 | 674 | Icon tích mục 1 bật | `04-ui-tech-hud/uisfx-minimal-success.mp3` (+200 cent) | −29 | −29 | +1,8 | nghỉ | — | −15,1 | −23 | Chuông "xong" ba nốt đi lên, dịch +2 cung thành La–Đô♯–Mi (hợp âm chủ của nhạc); nốt cuối, cũng là đỉnh, rơi đúng lúc icon tích bật; ba mục cùng âm, cùng mức |
| 24,07 | 722 | Icon tích mục 2 bật | `04-ui-tech-hud/uisfx-minimal-success.mp3` (+200 cent) | −29 | −29 | +2,9 | đang nói | 9,7 | −15,1 | −23 | Chuông "xong" ba nốt đi lên, dịch +2 cung thành La–Đô♯–Mi (hợp âm chủ của nhạc); nốt cuối, cũng là đỉnh, rơi đúng lúc icon tích bật; ba mục cùng âm, cùng mức |
| 25,60 | 768 | Icon tích mục 3 bật | `04-ui-tech-hud/uisfx-minimal-success.mp3` (+200 cent) | −29 | −29 | +1,9 | đang nói | 13,5 | −15,1 | −23 | Chuông "xong" ba nốt đi lên, dịch +2 cung thành La–Đô♯–Mi (hợp âm chủ của nhạc); nốt cuối, cũng là đỉnh, rơi đúng lúc icon tích bật; ba mục cùng âm, cùng mức |
| 29,93 | 898 | Khung xanh nở tràn khung sang cảnh 5 | `01-whooshes-transitions/whoosh-cut-medium.wav` | −26 | −26 | +9,8 | nghỉ | — | −15,9 | −16,9 | Whoosh đỉnh trước cắt 0,03 s (luật whoosh vào cảnh mới) |

## Cảnh 5 · CTA (30–36 s)

| Giây | Khung | Chuyển động | Âm (file trong kho) | M đích | M | Nhô | Lời | Dưới giọng | Gain | TP | Lý do |
|---:|---:|---|---|---:|---:|---:|---|---:|---:|---:|---|
| 30,13 | 904 | Bò hiện, vòng tỏa đầu tiên | `opa-sonic-logo-c.wav` | −27 | −27 | +59,2 | nghỉ | — | −15,4 | −16,4 | Logo âm thanh OPA (giọng La, đã dùng ở V2/V3); đỉnh trong khoảng nghỉ trước "OPA Agent" câu 5 (30,33 s), đuôi nằm dưới lời nên −27 |
| 32,20 | 966 | Nút URL bật lò xo | `03-pops-snaps-elastic/catch-bounce-dry.wav` | −29 | −29 | +2,4 | đang nói | 13,5 | −11,7 | −12,7 | Bounce A4: về chủ âm, kết ý |
| 34,17 | 1025 | Con trỏ bấm nút CTA: lớp thân | `04-ui-tech-hud/uisfx-minimal-press.mp3` | −28,5 | −31,9 | +1,1 | nghỉ | — | −10,4 | −12,1 | Cùng cú bấm cảnh 2, to hơn 1 dB vì là hành động chốt |
| 34,17 | 1025 | Con trỏ bấm nút CTA: lớp tách | `04-ui-tech-hud/kenney-mouseclick1.wav` | −29 | −41,2 | −8,2 | nghỉ | — | −15,1 | −12,1 | Lớp tách sáng như cảnh 2 |
| 34,33 | 1030 | Con trỏ nhả | `packs/uisfx-themes/minimal/release.mp3` | −31,5 | −31,5 | +1,3 | đang nói | 16,1 | −10,6 | −18,5 | Release của bộ minimal |

## Chuyển động cố ý không gắn âm

- Chữ vào/ra (R1–R6): lời đọc sẽ đọc đúng chữ đó, thêm âm sẽ che lời.
- Điện thoại rung lần 7–11 (56–112): nhịp 14 khung lệch nhịp đồng hồ 15 khung, chồng lên nhau thành lộn xộn dưới lời cảnh 1; sáu lần rung đầu trùng tin nhắn bật nên đã có âm.
- Tin mới thứ 2, 4, 6 (178, 200, 224) và chấm đỏ, "99+" nảy: cách tin trước dưới 0,5 s (nghe thành tiếng đúp), đã có ping của tin kề.
- Trả lời lặp lần 4 (316): trùng cảnh báo 3 và phiếu POS mở.
- Rung quá tải (375–389): nhạc dâng hats và whoosh Bò lao vào đảm nhận.
- Hàng minh họa cảnh 3 (hộp kho, tích, vạch quét, giỏ hàng, người) và chuông 24H: lời cảnh 3 dày, tick tính năng đã đánh dấu từng hàng.
- Tích bay lên cảnh 4 (684–814), hơi cà phê, Bò thở, nút CTA thở: chuyển động nền liên tục, giữ cảnh 4 thư thả.
- Vòng tỏa thứ hai (916) và con trỏ CTA đi vào (992–1022): logo âm thanh đã phủ; chỉ gắn âm lúc bấm.
- Riser vào màn trắng (4,9 s) và tiếng giấy phiếu POS (10,77 s): bỏ khi lồng giọng 23/10. Riser nằm đè "tưởng tượng" đầu câu 2, tiếng giấy đè đúng chữ "size"; cả hai nhiều năng lượng 2–8 kHz, che phụ âm.
- Chip số điện thoại, địa chỉ bay vào ô (338–348, 358–368): bỏ sau rà chéo v10, vì tiếng swish đè đầu âm tiết "rồi", "từng" lúc lời đang đọc đúng "nhập tay từng đơn hàng"; dời đi thì chỉ cách ping tin mới 1 khung.

<!-- ===== /file: ae-script-builder/examples/opa-agent/audio/BANG-CUE-AM-THANH.md ===== -->

<!-- ===== file: ae-script-builder/references/00_BANG-HUONG-DAN-DUNG-TOAN-BO.md ===== -->

# BẢNG HƯỚNG DẪN DỰNG TOÀN BỘ VIDEO OPA TRÊN AFTER EFFECTS

> Làm theo thứ tự từ trên xuống. Không chuyển bước khi cột **Kết quả phải thấy** chưa đạt.

## A. Chuẩn bị project — 20 đến 30 phút

| STT | Bạn phải làm | Thao tác chính xác | File sử dụng | Kết quả phải thấy |
|---:|---|---|---|---|
| 1 | Mở After Effects | Khởi động AE → `New Project` | — | Project trắng, không báo lỗi. |
| 2 | Chạy script tạo project | `File > Scripts > Run Script File…` → chọn `06_AFTER_EFFECTS/OPA_SETUP_PROJECT.jsx` | `OPA_SETUP_PROJECT.jsx` | Project có folder `00_MASTER` đến `06_RENDER`, comp `OPA_MASTER_60S` và 8 scene. |
| 3 | Lưu project ngay | `File > Save As` → đặt tên `OPA_BrandFilm_v01.aep` | — | File AEP nằm trong thư mục dự án của bạn. |
| 4 | Chọn 16 bpc | Nhấn chữ `8 bpc` dưới Project panel → chọn `16 bpc` | — | Góc dưới Project panel hiển thị `16 bpc`. |
| 5 | Đặt màu làm việc | `File > Project Settings > Color > Working Space > Rec.709 Gamma 2.4` | — | Project sử dụng Rec.709 Gamma 2.4. |
| 6 | Import logo | `File > Import > File…` | `01_BRAND/opa-logo-official.png` | Logo OPA xuất hiện trong Project panel. |
| 7 | Import storyboard | Chọn toàn bộ 8 PNG trong folder | `03_STORYBOARD_PNG/*.png` | Có đủ S01 đến S08. |
| 8 | Import icon | Chọn toàn bộ 12 PNG trong folder | `05_ICONS_PNG/*.png` | Có 12 icon nền trong suốt. |
| 9 | Import animatic | `File > Import > File…` | `08_REFERENCE/OPA_ANIMATIC_REFERENCE_60S.mp4` | Có video reference đúng 60 giây. |
| 10 | Đưa animatic vào master | Kéo animatic vào `OPA_MASTER_60S`; đặt ở dưới cùng; giảm Opacity 20%; bật Shy | Animatic MP4 | Có thể bật/tắt animatic để so timing. |
| 11 | Bật autosave | `Edit > Preferences > Auto-Save` → 5 phút, 20 phiên bản | — | AE tự lưu dự phòng. |
| 12 | Tạo guide | Trong comp chính: `View > Show Rulers`; kéo guide cách mép trái/phải 120 px | — | Chữ và CTA không vượt vùng an toàn. |

## B. Quy tắc layer áp dụng cho tất cả các scene

| Loại layer | Tên phải dùng | Màu label | Ghi chú |
|---|---|---|---|
| Nền | `BG_White`, `BG_Gradient` | Brown | Luôn đặt cuối timeline. |
| Text | `TXT_Headline`, `TXT_Body`, `TXT_Label` | Yellow | Dùng DM Sans nếu đã cài. |
| Shape/card | `SHP_Card_*` | Blue | Dựng bằng Shape Layer để sửa được. |
| Icon | `ICO_*` | Cyan | Có thể dùng PNG hoặc vẽ lại từ SVG. |
| Null điều khiển | `CTRL_*` | Red | Dùng để parent nhiều layer. |
| Matte | `MAT_*` | Purple | Tắt biểu tượng mắt nếu matte không cần nhìn thấy. |
| Adjustment | `ADJ_*` | Orange | Blur, glow hoặc grade toàn cảnh. |
| Audio | `VO_*`, `MUSIC_*`, `SFX_*` | Green | Voice luôn ở trên music trong timeline. |

## C. Công thức keyframe dùng xuyên suốt

| Hiệu ứng | Frame 0 | Frame giữa | Frame cuối | Tổng thời gian | Graph Editor |
|---|---:|---:|---:|---:|---|
| Card xuất hiện | Position Y +40; Scale 96%; Opacity 0 | Scale 102% | Position chuẩn; Scale 100%; Opacity 100 | 14–16 frame | Đầu 30%, cuối 75–85% Influence |
| Text body xuất hiện | Y +18; Opacity 0 | — | Y 0; Opacity 100 | 10–14 frame | Ease Out |
| Headline mạnh | Scale 112%; Opacity 0 | Scale 97% | Scale 100%; Opacity 100 | 16–20 frame | Hãm mạnh ở cuối |
| Icon pop | Scale 0; Rotation -8° | Scale 112% | Scale 100%; Rotation 0° | 10–12 frame | Overshoot nhẹ |
| Button CTA | Y +24; Scale 98%; Opacity 0 | Scale 103% | Y 0; Scale 100%; Opacity 100 | 14–18 frame | Ease Out |
| Đường vẽ | Trim Paths End 0% | — | End 100% | 18–40 frame | Tăng nhanh rồi hãm |
| Checkmark | Trim Paths End 0% | — | End 100% | 6–8 frame | Ease Out |

**Cách đặt keyframe:** chọn layer → nhấn `P` cho Position, `S` cho Scale, `T` cho Opacity, `R` cho Rotation → nhấn Stopwatch → di chuyển playhead → đổi giá trị. Chọn keyframe và nhấn `F9` để Easy Ease.

---

# D. DỰNG TỪNG SCENE

## Scene 01 — Chaos — 00:00 đến 00:04

| Bước | Việc làm | Thao tác và thông số | Asset | Kết quả phải thấy |
|---:|---|---|---|---|
| 1 | Mở scene | Double-click `S01_CHAOS` | `S01_CHAOS.png` làm reference | Comp dài 4 giây. |
| 2 | Đặt reference | Kéo PNG vào comp; Opacity 30%; khóa layer | Storyboard S01 | Có hình mẫu để canh bố cục. |
| 3 | Tạo headline | Text: `Quá Nhiều Công Cụ. Quá Nhiều Thao Tác.`; DM Sans Bold 72 px | — | Headline nằm phía trên, giữa khung. |
| 4 | Tạo card mẫu | Rounded Rectangle 500×190; Roundness 30; Fill trắng; Stroke 2 px; Shadow 12% | Icon spreadsheet | Một card giống storyboard. |
| 5 | Pre-compose card | Chọn shape, icon, text → `Ctrl+Shift+C` → `COMP_CARD_SPREADSHEET` | — | Card thành một pre-comp. |
| 6 | Nhân thành 4 card | Duplicate và đổi thành Email, CRM, Calendar | 4 icon tương ứng | Bốn card nằm quanh tâm. |
| 7 | Animate card 1 | Dùng công thức Card xuất hiện; bắt đầu frame 5 | — | Card vào nhanh, dừng mềm. |
| 8 | Stagger card | Card 2 trễ 3 frame; card 3 trễ 6; card 4 trễ 9 | — | Card xuất hiện liên tiếp. |
| 9 | Tạo chiều sâu | Card gần Scale 105%; card xa Scale 92–96%; giảm opacity card xa | — | Cảnh có foreground/background. |
| 10 | Tạo camera | New Camera 35 mm + Null `CTRL_Camera`; parent camera vào null | — | Có thể zoom toàn cảnh. |
| 11 | Animate camera | 2 giây cuối: zoom out 10–15% | — | Cuối cảnh hé lộ toàn bộ sự hỗn loạn. |
| 12 | Bật motion blur | Bật biểu tượng Motion Blur cho card và comp | — | Card mượt khi đi nhanh, nét khi dừng. |

**Đạt khi:** xem ở Full Resolution, headline đọc rõ; bốn card không che nhau; không có card nào chạy linear.

## Scene 02 — 10 bước thủ công — 00:04 đến 00:12

| Bước | Việc làm | Thao tác và thông số | Kết quả phải thấy |
|---:|---|---|---|
| 1 | Đặt storyboard S02 | Opacity 30%, khóa layer | Có mẫu pipeline ngang. |
| 2 | Vẽ đường chính | Pen Tool → Shape Layer → Stroke đỏ/cam 5 px → `Add > Trim Paths` | Một đường ngang từ trái sang phải. |
| 3 | Animate đường | End 0% ở frame 0 → 100% tại 2,5 giây | Đường được vẽ dần. |
| 4 | Tạo node mẫu | Circle 76 px; Fill trắng; Stroke đỏ 5 px; số `01` ở giữa | Một node rõ và cân. |
| 5 | Nhân 10 node | Căn đều bằng `Window > Align` | Mười node có khoảng cách đều. |
| 6 | Thêm label | Tạo lead, Tìm email, Soạn nội dung, Gửi, Chờ, Follow-up, Đánh giá, Đặt lịch, CRM, Meeting | Mỗi label tối đa hai từ hoặc rất ngắn. |
| 7 | Animate node | Scale 0 → 115 → 100 khi đầu Trim Path đi tới | Node nảy nhẹ đúng thời điểm. |
| 8 | Stagger label | Label vào sau node 2 frame; Y +14 → 0; Opacity 0 → 100 | Label không xuất hiện quá sớm. |
| 9 | Tạo token | Circle 28 px màu đỏ; copy Path pipeline và paste vào Position | Token chạy dọc pipeline. |
| 10 | Camera pan | Pan nhẹ từ node 1 sang node 10 | Người xem cảm nhận quy trình dài. |

**Đạt khi:** khán giả hiểu “nhiều bước” dù không đọc đủ mười label; token không chạy vượt trước đường vẽ.

## Scene 03 — Freeze và logo — 00:12 đến 00:21

| Bước | Việc làm | Thao tác và thông số | Asset/Kết quả |
|---:|---|---|---|
| 1 | Đặt pipeline mờ | Dùng frame cuối S02 hoặc pre-compose pipeline; Opacity 15–25% | Nền gợi lại cảnh trước. |
| 2 | Tạo dòng nhỏ | `Mất Quá Nhiều Thời Gian Cho`; 36 px; Slate | Hiện trước headline. |
| 3 | Tạo headline | `10 Bước Thủ Công`; 100 px; Bold; đỏ/cam | Là điểm nhìn chính. |
| 4 | Animate headline | Scale 125 → 96 → 100; Opacity 0 → 100 trong 17 frame | Cảm giác bị đóng dấu. |
| 5 | Tạo underline | Rectangle cao 10 px; Anchor Point về trái; Scale X 0 → 100 | Gạch chân mở từ trái sang phải. |
| 6 | Hút card vào tâm | Card Position về tâm; Scale → 0; Rotation 8–20°; stagger 2 frame | Vấn đề bị thu gọn. |
| 7 | Đặt logo chuẩn | Import `opa-logo-official.png`; đặt chính giữa | Dùng logo thật, không gõ chữ OPA. |
| 8 | Reveal logo không plugin | Scale 92 → 103 → 100; Opacity 0 → 100 | Logo xuất hiện sạch. |
| 9 | Saber tùy chọn | Solid → Saber → Layer Masks; End Offset 0 → 100; fade Saber về 0 | Glow chỉ tồn tại lúc vẽ. |
| 10 | Giữ logo | Logo dừng hoàn toàn ít nhất 12 frame | Người xem nhận diện được thương hiệu. |

## Scene 04 — Ba trụ cột — 00:21 đến 00:27

| Bước | Việc làm | Thao tác | Kết quả |
|---:|---|---|---|
| 1 | Tạo ba card | Marketing, Công Nghệ, AI; 470×210; Roundness 30 | Ba card cùng hệ thiết kế. |
| 2 | Thêm icon | Target/marketing, technology, ai | Icon nằm trong circle màu nhạt. |
| 3 | Animate card trái | X -80 → 0; Scale 96 → 102 → 100 | Marketing vào từ trái. |
| 4 | Animate card phải | X +80 → 0 | AI hoặc Công nghệ vào từ phải. |
| 5 | Animate card giữa | Y +60 → 0 | Card giữa vào sau 3–4 frame. |
| 6 | Vẽ đường nối | Trim Paths từ card về core giữa | Ba năng lực hội tụ. |
| 7 | Tạo headline cuối | `Marketing × Công Nghệ × AI` | Headline gradient xanh–tím. |
| 8 | Chuẩn bị match cut | Đường cuối scene nằm đúng vị trí đường đầu S05 | Hai scene nối liền không nhảy. |

## Scene 05 — AI Pipeline — 00:27 đến 00:39

| Bước | Việc làm | Thao tác và thông số | Kết quả |
|---:|---|---|---|
| 1 | Tạo component node | Card 380×220; icon, title, description, status dot | Một node hoàn chỉnh. |
| 2 | Nhân 4 node | Kết nối CRM; AI Chấm Điểm Lead; Follow-Up Tự Động; Meeting Booked | Bốn node căn đều. |
| 3 | Tạo trạng thái Idle | Opacity 40%; border xám | Node chưa hoạt động mờ. |
| 4 | Tạo trạng thái Active | Opacity 100%; border xanh; Scale 104% | Chỉ một node active. |
| 5 | Tạo trạng thái Complete | Nền xanh rất nhạt; icon check | Node đã xử lý dịu lại. |
| 6 | Vẽ pipeline | Shape Stroke 8–10 px chạy sau card | Một tuyến dữ liệu liên tục. |
| 7 | Tạo token | Circle 30 px gradient xanh–tím | Token là chủ thể chuyển động chính. |
| 8 | Cho token chạy | Copy path vào Position; dừng 8–12 frame tại mỗi node | Token đi lần lượt 1→4. |
| 9 | Node 1 micro-motion | Icon link hoặc database pulse | Hiểu CRM đã kết nối. |
| 10 | Node 2 counter | Slider Control 0 → 92; Source Text `Math.round(effect("Score")("Slider"))+"/100"` | Hiện `92/100`. |
| 11 | Node 3 email | Flap Rotation mở; arrow Position đi ra | Hiểu follow-up đã gửi. |
| 12 | Node 4 check | Trim Paths dấu check 0 → 100 trong 8 frame | Meeting booked hoàn thành. |
| 13 | Giữ kết quả | Hold node cuối ít nhất 20 frame | Khán giả đọc được kết quả. |
| 14 | Thêm SFX | Một click nhẹ tại từng node; chime rõ nhất ở node 4 | Hình và âm khớp đúng frame. |

**Đạt khi:** tắt voice-over vẫn hiểu quy trình; chỉ token và node active thu hút mắt; không có bốn node cùng glow.

## Scene 06 — Hệ sinh thái dịch vụ — 00:39 đến 00:47

| Bước | Việc làm | Thao tác | Kết quả |
|---:|---|---|---|
| 1 | Tạo card lớn | Marketing Đa Nền Tảng; nền xanh nhạt | Card chiếm khoảng 45% chiều ngang. |
| 2 | Tạo hai card phụ | Giải Pháp Công Nghệ; Ứng Dụng AI | Xếp dọc bên phải. |
| 3 | Thêm tag | Mỗi card tối đa 3–4 tag | Text không quá dày. |
| 4 | Tạo matte reveal | Rectangle Scale Y 0 → 100; card Y +24 → 0 | Card mở ra sạch. |
| 5 | Stagger card | Card lớn vào trước; card phụ trễ 5 frame | Có hierarchy. |
| 6 | Animate tag | Trễ nhau 2 frame | Tag hiện lần lượt, không đồng loạt. |

## Scene 07 — Kết quả — 00:47 đến 00:54

| Bước | Việc làm | Thao tác | Kết quả |
|---:|---|---|---|
| 1 | Xác minh số liệu | Chỉ dùng 3×, 10K+, 95% khi OPA duyệt | Không xuất bản claim chưa xác nhận. |
| 2 | Tạo ba stat card | Cùng kích thước, cùng spacing | Ba cột cân bằng. |
| 3 | Tạo counter 3× | Slider 0 → 3; thêm `×` trong expression | Số dừng ở 3×. |
| 4 | Tạo counter 10K+ | Slider 0 → 10; thêm `K+` | Số dừng ở 10K+. |
| 5 | Tạo counter 95% | Slider 0 → 95; thêm `%` | Số dừng ở 95%. |
| 6 | Stagger | Counter sau trễ hơn counter trước 5 frame | Số chạy lần lượt. |
| 7 | Settle | Khi đạt số cuối: Scale 100 → 104 → 100 | Kết quả có điểm kết thúc. |
| 8 | Hold | Giữ toàn bộ số ổn định ít nhất 1,2 giây | Khán giả đọc đủ. |

## Scene 08 — CTA — 00:54 đến 01:00

| Bước | Việc làm | Thao tác | Kết quả |
|---:|---|---|---|
| 1 | Đặt logo chuẩn | Chính giữa, hơi cao hơn tâm | Logo có khoảng thở. |
| 2 | Tạo tagline | `Tăng Trưởng Thông Minh.` và `Mở Rộng Nhanh Hơn.` | Dòng hai dùng gradient. |
| 3 | Mask reveal tagline | Text Y +24 → 0 trong matte | Hai dòng vào cách nhau 4 frame. |
| 4 | Tạo CTA | Rounded Rectangle xanh; text `Đăng Ký Tư Vấn Miễn Phí` | Button rõ, không quá lớn. |
| 5 | Animate CTA | Y +24 → 0; Scale 98 → 103 → 100 | CTA vào mềm. |
| 6 | Light sweep | CC Light Sweep chạy một lần | Không loop ánh sáng. |
| 7 | Thêm website | `opa.business` dưới CTA | Đọc rõ ở màn hình nhỏ. |
| 8 | Hold cuối | Giữ toàn bộ frame tĩnh ít nhất 1,5 giây | Video kết thúc chắc chắn. |

---

# E. ÂM THANH VÀ NHỊP

| Track | Mức tham khảo | Việc phải làm |
|---|---:|---|
| Voice-over | Peak -6 đến -3 dB | Đặt trước, cắt scene theo câu thoại. |
| Music | Khoảng -24 đến -18 dB dưới voice | Hạ nhạc khi giọng đọc dày. |
| Whoosh | Khoảng -18 đến -10 dB | Chỉ dùng ở chuyển cảnh lớn. |
| UI click | Khoảng -24 đến -16 dB | Khớp frame node active. |
| Final chime | Khoảng -16 đến -10 dB | Dùng ở Meeting Booked hoặc CTA. |
| Master | Không vượt -1 dB | Không được clipping. |

## Điểm đặt SFX

| Timecode | SFX |
|---:|---|
| 00:00–00:04 | Card pop nhỏ, paper/UI movement |
| 00:04 | Pipeline start whoosh |
| 00:12 | Impact ngắn khi freeze |
| 00:16–00:21 | Energy rise/logo chime |
| 00:27 | Digital whoosh mở AI pipeline |
| Mỗi node S05 | Soft click |
| Node Meeting Booked | Confirmation chime |
| 00:47 | Statistic rise nhẹ |
| 00:54 | Brand resolve/chime |

---

# F. KIỂM TRA TRƯỚC KHI RENDER

| STT | Kiểm tra | Đạt khi |
|---:|---|---|
| 1 | Xem không âm thanh | Vẫn hiểu vấn đề → giải pháp → kết quả → CTA. |
| 2 | Chỉ nghe âm thanh | Voice rõ, music không lấn, SFX không quá nhiều. |
| 3 | Xem Full Resolution | Không có layer nhảy, matte hở hoặc chữ rung. |
| 4 | Kiểm tra chữ | Mỗi dòng bắt đầu bằng chữ hoa; dấu tiếng Việt không bị cắt. |
| 5 | Kiểm tra Graph Editor | Không có chuyển động linear ngoài progress/token chủ ý. |
| 6 | Kiểm tra logo | Dùng đúng `opa-logo-official.png`, không méo tỷ lệ. |
| 7 | Kiểm tra claim | Số liệu đã được OPA xác nhận. |
| 8 | Kiểm tra CTA | Giữ đủ 1,5 giây và đọc được khi thu nhỏ preview 50%. |
| 9 | Kiểm tra mobile | Xem thử video trên màn hình điện thoại. |
| 10 | Xem file render lại | Không chỉ xem RAM Preview trong After Effects. |

# G. RENDER

| Bản | Thiết lập |
|---|---|
| Master | QuickTime → Apple ProRes 422 HQ → 1920×1080 → 30 fps → PCM 48 kHz |
| Web/Social | H.264 High Profile → VBR 2 Pass → Target 16–20 Mbps → Max 24–30 Mbps → AAC 320 kbps |
| Tên file | `OPA_BrandFilm_60s_16x9_Web_v01.mp4` |

## Thứ tự làm thực tế

1. Hoàn thành S01 và render thử 4 giây.
2. Hoàn thành S02–S03 và kiểm tra transition.
3. Hoàn thành S04–S05; đây là phần quan trọng nhất.
4. Hoàn thành S06–S08.
5. Ghép voice-over.
6. Thêm music và SFX.
7. Xem ba vòng QA.
8. Render master trước, H.264 sau.

Không dựng cả tám scene cùng lúc. Hoàn thiện chuyển động của một card và một node trước; sau đó nhân hệ thống đó cho toàn bộ video.

<!-- ===== /file: ae-script-builder/references/00_BANG-HUONG-DAN-DUNG-TOAN-BO.md ===== -->

<!-- ===== file: ae-script-builder/references/01-PHUONG-AN-TRIEN-KHAI-OPA-AGENT.md ===== -->

# OPA Agent — Ads 01: phương án dựng After Effects

Nguồn kịch bản: [Video 01 — Tổng quan OPA Agent](https://opa-agent-video-roadmap-pitch.vercel.app/#video-01), đọc ngày 21/10/2026. Bản dựng giữ 5 nhịp **0–5 / 5–11 / 11–22 / 22–30 / 30–36 giây**. Ưu tiên 1920 × 1080; có bản 1080 × 1920 được sắp lại bố cục. Cả hai 30 fps, 36 giây, pixel vuông.

## Hướng mỹ thuật

Một chủ shop, hai trạng thái: đầu video bị tin nhắn bao vây; sau kết nối OPA, công việc đi vào luồng rõ ràng. Minh họa phẳng 2D, nền trắng xanh, chữ lớn, giao diện dạng thẻ; phần nỗi đau chuyển sang xanh đêm. Xanh OPA lấy từ logo gốc, gần #0068FF. Cam dành cho quá tải, xanh lá cho thao tác hoàn tất. Không dùng số liệu tăng doanh thu hay chứng thực chưa có trong kịch bản.

Headline dùng Montserrat Bold / ExtraBold; phần giải thích và UI dùng Arial để giữ dấu tiếng Việt. Cụm nhấn `THỜI GIAN?`, `OPA tự động hóa`, `OPA lo việc lặp lại` tách text layer, đổi font và có hiệu ứng riêng. Dòng hiển thị bắt đầu bằng chữ hoa. Dấu xuống dòng là chủ đích bố cục, sửa câu dài cần kiểm tra lại hình.

## Storyboard và cách dựng

| Đoạn | Bản 16:9 | Chuyển động / layer AE | Bản 9:16 |
|---|---|---|---|
| 0–5s — Hook | Chủ shop quay lưng bên trái; headline bên phải; đồng hồ ở trên; 3 tin nhắn xuất hiện quanh bàn | Nhân vật gồm đầu, tóc, cổ, áo, tay, laptop, ghế, bàn, chậu cây; null điều khiển nhịp người. Kim đồng hồ quay bằng expression. Bubble scale 82 → 104 → 100%, opacity và position có easing. Cụm `THỜI GIAN?` trượt lên cùng gạch chân mở ngang. | Headline ở trên, nhân vật ở giữa/dưới; bubble phân bố quanh nhân vật. Giữ phần chữ quan trọng trong x=90–900. |
| 5–11s — Pain | Màn hình inbox nhiều trang bên trái, ba thẻ nỗi đau bên phải; nền tối dần | `UI_01_INBOX_OVERLOAD` dựng lại bằng shape/text. Trạng thái chờ nhấp nháy, từng hàng hội thoại vào lệch nhịp. Nền tối thêm nhẹ, ba pain card trượt lên lần lượt. | Inbox nằm dưới headline, ba thẻ nỗi đau xếp dọc phía dưới. |
| 11–22s — Solution | Giao diện chat → POS bên trái; headline và 5 pill bên phải; mascot xuất hiện nhỏ | Vòng tròn xanh phủ khung hình quanh mốc 11s rồi tan. Tin hỏi ở 0.4s của cảnh, AI trả lời ở 1.4s, yêu cầu lên đơn ở 3.2s, xác nhận ở 5.4s, thẻ POS vào ở 6.4s. Năm pill lần lượt vào theo nhịp: tồn kho, chốt đơn, xác minh ảnh, nhắc giỏ, tiếp quản. Icon là shape, dấu check dùng Trim Paths. | Headline → UI → năm pill xếp dọc; cùng nội dung, bố cục riêng. Không crop nguyên bản ngang. |
| 22–30s — Relief | Chủ shop thư giãn bên trái; ba check card bên phải | Rig chủ shop riêng với tay dang, mắt, miệng cười. Ba check card vào cách nhau 1.85s; check vẽ bằng Trim Paths. Giữ cảnh kết để người xem đọc. | Nhân vật thu gọn dưới headline; ba check card xếp dọc phía dưới. |
| 30–36s — CTA | Mascot bên trái; logo, lời hứa, nút CTA và URL bên phải | Logo gốc giữ PNG trong precomp đúng vùng alpha. Mascot 2D gồm các shape riêng. CTA pop-in; con trỏ vào và click; vòng click lan ra. Kết thúc có hold để đọc domain. | Logo ở trên, mascot ở giữa, lời hứa và CTA ở dưới. URL giữ một dòng trong vùng an toàn. |

Chuyển cảnh dùng cut ở mốc 5, 22 và 30s; vòng tròn xanh tại 11s tạo điểm đổi trạng thái. Native Motion Blur bật, shutter angle 180°. Không cần Saber, FX Console hay plugin trả phí để mở project.

## Cấu trúc chỉnh sửa

| Thư mục trong Project panel | Nội dung |
|---|---|
| `00_EXPORT — Open MASTER here` | Hai master theo tỷ lệ, marker 5 cảnh, audio VO/BGM/SFX riêng |
| `01_SCENES_16x9 — Edit text + motion` | H_S01_HOOK đến H_S05_CTA |
| `02_SCENES_9x16 — Reflowed layout` | V_S01_HOOK đến V_S05_CTA |
| `03_UI_COMPONENTS — Shared demo interface` | Inbox quá tải và chat tự động → POS; chỉnh một lần cập nhật cả hai tỷ lệ |
| `04_CHARACTERS + LOGO — Native rigs` | Chủ shop bận, chủ shop thư giãn, mascot 2D, đồng hồ, logo |
| `05_FOOTAGE — Replace brand / voice` | Logo gốc, ảnh mascot tham chiếu, VO placeholder, BGM và SFX |
| `99_README + QA` | Hướng dẫn ngay trong AE, color controller, báo cáo cấu trúc |

`TXT_` là chữ sửa được; `CARD_`, `PILL_`, `ICON_`, `BG_` là shape; `CTRL_` là null/controller. `GUIDE_SAFE` là guide layer tắt sẵn và không xuất vào video. Khi chỉnh text riêng từng tỷ lệ, vào đúng thư mục H hoặc V.

Text/shape trực tiếp có thể Ctrl+D rồi sửa độc lập. Nhân bản một **precomp layer** vẫn dùng chung source: để tạo phiên bản nội dung độc lập, nhân bản composition trong Project panel rồi thay source layer. Các UI/rig dùng chung là chủ đích để sửa đồng thời hai tỷ lệ.

## Âm thanh và lời bình

- `SFX-36s-original.wav`: tiếng tích tắc và tin nhắn trong đoạn đầu, whoosh ở mốc chuyển, tick khi hoàn tất, click CTA và âm logo.
- `BGM-36s-original-guide.wav`: nhạc điện tử tối giản 120 BPM bắt đầu ở đoạn giải pháp; là nhạc guide tự tổng hợp để dựng nhịp, có thể thay bằng bài đã cấp phép.
- `VO-REPLACE-36s-silent.wav`: track im lặng có chủ đích, đặt sẵn trong cả hai master; **chưa phải giọng đọc**.
- Lời bình gốc và bản rút gọn đề xuất nằm ở `03-LOI-BINH.md`. Đoạn pain gốc dài nhất so với 6 giây được cấp. Thu lời bình rồi chỉnh nhịp theo câu thật; không ép tốc độ đọc nếu nghe gấp.

## Những lựa chọn cần chốt ở khâu cuối

1. Thay VO bằng bản thu thật và căn lại điểm vào/ra theo marker.
2. Duyệt câu chữ, tính năng và ưu đãi dùng thử; URL `chat.overpowers.agency` được giữ theo nguồn kịch bản, chưa kiểm tra đăng nhập hoặc ưu đãi ở runtime.
3. Duyệt mascot: bản 2D trong video là diễn giải dựng riêng từ hướng bò xanh, chưa được coi là mascot thương hiệu đã duyệt. Ảnh mascot gốc trên máy được kèm làm tham chiếu.
4. Nếu cần UI chính xác từng pixel, thay minh họa bằng quay màn hình OPA/Pancake POS đã xác nhận. UI hiện tại thể hiện câu chuyện, không phải bằng chứng sản phẩm đang vận hành.
5. Nghe và cân nhạc/SFX với VO; kiểm tra lại cả hai tỷ lệ khi đổi câu dài.

Kịch bản nguồn nhắc SMIT Ads Check Pro. Bản này triển khai cấu trúc và timing trong bảng nguồn; không khẳng định đã tái tạo chính xác khung hình hoặc animation của video SMIT.

<!-- ===== /file: ae-script-builder/references/01-PHUONG-AN-TRIEN-KHAI-OPA-AGENT.md ===== -->

<!-- ===== file: ae-script-builder/references/SO-TAY-AFTER-EFFECTS.md ===== -->

# Sổ tay After Effects: dựng và sửa project bằng script

Bản cuối v3, ngày 26/10/2026. Nguồn:
- **ca mẫu nhánh A** "OPA Agent × Pancake": bản v07–v10, 21–23/10;
- **bộ phân tích template AE** ngày 21/10;
- **ca mẫu nhánh B** sửa "template 5.aep", do một phiên agent khác làm (23–26/10);
- các bài học đã ghi trong memory.

Mọi con số đều đo trên máy của Minh, trừ chỗ ghi "nguồn web" hoặc "chưa đo".

Đọc nhanh: mục 2 (chọn nhánh), 3 (chạy AE), 5 (keyframe), 6 (chữ), 9 (âm), 11 (kiểm).

Ký hiệu đường dẫn:

| Ký hiệu | Đường dẫn |
|---|---|
| `<SKILL>` | thư mục của skill này (chứa `SKILL.md`) |
| `<VD-A>` | `<SKILL>\examples\opa-agent`: bản chụp code ca mẫu nhánh A |
| `<VD-B>` | `<SKILL>\examples\template-5`: script ca mẫu nhánh B |
| `<KHUNG>` | `<SKILL>\templates\du-an-ae`: bộ khung dự án mới, đã thử |
| `<AE>` | `C:\Program Files\Adobe\Adobe After Effects 2026\Support Files` |
| `<SFX>` | `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx`: kho SFX của Minh |
| `<OPA>` | `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/OPA-Motion-graphic-mascot`: dự án OPA sống |

Máy khác thì đổi các đường dẫn này theo mục 17.

## Mục lục

1. Từ ngữ
2. Bức tranh chung: hai nhánh
3. Chạy AE mà không đụng phiên của Minh
4. Cấu trúc project
5. Keyframe và easing
6. Chữ
7. Hình: shape, matte, parent, expression, máy quay, nhân vật, giao diện
8. Chuyển động và nhịp
9. Âm thanh
10. Render và xuất file
11. Thang kiểm trước khi giao
12. Học từ template AE có sẵn
13. Nhánh B: sửa template mua về
14. Bàn giao và cách sửa
15. Nhánh A: bắt đầu dự án mới
16. Lỗi hay gặp
17. Cấu hình máy, cài skill, phụ thuộc
18. Nguồn

## 1. Từ ngữ

| Từ | Nghĩa |
|---|---|
| Comp (composition) | Một khung dựng có kích thước, fps, thời lượng. Comp đặt trong comp khác gọi là pre-comp |
| Layer | Một lớp trong comp: chữ, hình vẽ (shape), ảnh, âm, null, comp con |
| Null | Layer vô hình làm tay cầm. Gắn layer khác vào để di chuyển chung, ví dụ máy quay ảo |
| Parent | Layer cha. Con đi theo vị trí, tỉ lệ, góc xoay của cha, nhưng không theo độ mờ |
| Khung (frame) | Một hình. 30 fps là 30 khung mỗi giây. Đánh số từ 0 |
| Keyframe (key) | Mốc giá trị tại một khung. AE tự tính giá trị giữa hai key |
| Nội suy | Cách đi giữa hai key: Linear (đều), Bezier (tăng, giảm tốc), Hold (đứng yên rồi nhảy) |
| Easing | Đường tăng tốc, giảm tốc giữa hai key |
| Speed, Influence | Hai số của mỗi tay nắm ease: tốc độ tại key và độ dài tay nắm (% của đoạn). Speed 0 với influence lớn là chậm lâu ở hai đầu |
| Temporal, spatial | Temporal: tốc độ theo thời gian. Spatial: hình dạng đường đi của Position. Hai thứ khác nhau |
| cubic-bezier | Cách viết easing trên web. Đổi qua lại được với speed, influence (mục 5.1) |
| Text Animator | Bộ tạo chuyển động cho chữ theo ký tự, từ hoặc dòng, nằm ngay trong layer chữ |
| Range Selector | Phần của Text Animator chọn chữ nào bị tác động. Cho Start chạy 0→100 thì chữ lần lượt hiện |
| em | Cỡ chữ dùng làm đơn vị. Chữ 126 px thì 1 em = 126 px |
| Track matte | Lấy độ trong suốt (alpha) của một layer làm khuôn cho layer khác |
| Mask | Đường cắt vẽ ngay trên layer |
| Expression | Đoạn JavaScript nhỏ gắn vào thuộc tính, tính lại giá trị mỗi khung |
| matchName | Tên cố định của thuộc tính dùng trong script (ví dụ `ADBE Opacity`). Không đổi theo ngôn ngữ giao diện |
| JSX, ExtendScript | Ngôn ngữ script của AE (JavaScript đời cũ, ES3) |
| Headless | Chạy AE không mở giao diện, trong một phiên riêng |
| aerender | Chương trình render của AE, chạy bằng dòng lệnh |
| Seed | File .aep trống dùng làm gốc để lưu project mới |
| Holder (comp giữ chỗ) | Comp trong template để người dùng thả logo, ảnh, video, nhạc của mình vào |
| .aepx | Project AE dạng XML (đọc được bằng chữ), cùng nội dung với .aep |
| BT.709 | Chuẩn màu video HD. MP4 phải gắn thẻ này thì máy phát mới hiện đúng màu |
| LUFS, LU | Độ to cảm nhận theo chuẩn ITU-R BS.1770. LU là chênh lệch giữa hai mức LUFS |
| M, S, I | Độ to tức thời (cửa sổ 400 ms), ngắn hạn (3 s), tích hợp (cả bài) |
| dBTP | Đỉnh thật: tính cả đỉnh nằm giữa hai mẫu số |
| LRA | Dải độ to: phần to và phần nhỏ của bài chênh nhau bao nhiêu LU |
| SFX, cue | SFX là hiệu ứng âm. Mỗi lần đặt một SFX vào timeline là một cue |
| Master âm | Bước cuối: chỉnh cả bản về đúng độ to và chừa khoảng trống cho đỉnh |
| Tĩnh A, Tĩnh B | Số đo khung đứng của `metrics.py`. Tĩnh B: khung gần như không đổi so với khung trước (≤ 0,5 % điểm ảnh đổi). Tĩnh A: khung đứng hẳn (≤ 0,04 %) |
| Q, Q5 | Agent rà chéo mới, chưa đọc gì của dự án. Q soát hình và chữ, Q5 soát âm (mục 11.1) |
| B8 | Ca cũ của pipeline video: bản trộn vượt trần đỉnh vì tiếng tick trùng đỉnh giọng. Từ đó có trần −12 dBTP mỗi cue và master ở −16,1 |

## 2. Bức tranh chung: hai nhánh

| | Nhánh A: dựng mới bằng script | Nhánh B: sửa template mua về |
|---|---|---|
| Khi nào | Không có template; cần .aep sạch, phân tầng rõ, dựng lại được | Có sẵn template .aep (Envato…) gần đúng ý |
| Đầu vào | kịch bản khóa, bảng cảnh | template .aep, kịch bản, logo, ảnh, giao diện, nhạc |
| Cách làm | JSX tạo mọi comp, layer, key từ đầu (mục 15) | đọc cấu trúc template, thay chữ, màu, tài nguyên, gắn SFX bằng script (mục 13) |
| Ca mẫu | `<VD-A>` (OPA Agent, đã qua thang kiểm) | `<VD-B>` (template 5, chưa kiểm lại khi đóng gói) |
| Phần dùng chung | chạy AE (3), keyframe (5), chữ (6), âm (9), render (10), thang kiểm (11), bàn giao (14) | như bên trái |

Lý do dựng bằng script thay vì bấm tay:
1. Đầu ra là .aep thật: có layer chữ, layer shape, keyframe gốc. Minh mở ra sửa được.
2. Dựng lại từ đầu chỉ mất khoảng 5–17 s. Sửa bao nhiêu vòng cũng không lệch.
3. Agent không phải bấm chuột vào AE của Minh.

Quy trình nhánh A:

```
kịch bản khóa ─► bảng cảnh (KHUNG-DUNG.md)
 ─► JSX: lib.jsx + scenes/*.jsx + main.jsx (+ dữ liệu sinh: path, cue âm)
 ─► AE headless (tools/ae.py build) ─► project .aep + báo cáo build/_report.json
 ─► aerender (tools/ae.py render) ─► MP4 ─► gắn thẻ BT.709
 ─► âm: SFX theo chuyển động + nhạc nền + giọng (tools/am_thanh_cues.py) ─► dựng lại
 ─► master âm (master.py) ─► thang kiểm + rà chéo ─► giao
```

## 3. Chạy AE mà không đụng phiên của Minh

Minh thường để AE mở sẵn, và có khi một agent khác cũng đang chạy script trong phiên đó. Vì vậy:
- không gửi script vào phiên ấy;
- không điều khiển AE bằng chuột (computer-use);
- không dùng mẹo đổi tiến trình cha (parent PID) để đẩy script vào phiên đang mở;
- mọi việc chạy trong một phiên AE riêng.

Nếu Minh muốn chạy script trong phiên AE đang mở của Minh:
- agent chỉ soạn file JSX;
- Minh lưu project của mình trước, rồi tự chạy bằng menu File › Scripts › Run Script File…;
- script không đóng project, không bỏ thay đổi chưa lưu, và lưu kết quả ra file mới.

### 3.1 Lệnh

```bash
cd "<thư mục dự án AE>"
python -I tools/ae.py build          # dựng project từ build/*.jsx
python -I tools/ae.py render --comp <COMP> --start 0 --end <khung cuối> --out out/review/_lam/bNN.mp4
python -I tools/ae.py stills --comp <COMP> --frames 20,60,100 --outdir out/stills
```

`tools/ae.py build` làm 5 việc:
1. Gộp các file theo thứ tự trong `BUNDLE_ORDER` thành `build/_bundle.jsx`: `lib.jsx`, `data/*.jsxinc`, `scenes/*.jsx`, `main.jsx`.
2. Đổi tên project cũ thành `*.bak-<giờ>.aep`, rồi chép seed trống `tools/seed/empty-ae26.aep` ra đường dẫn đích.
3. Mở phiên AE riêng: `AfterFX.exe -noui -m -s "<loader>"`.
4. Chờ tối đa 600 s. Quá giờ thì dừng đúng tiến trình đó.
5. Đọc `build/_report.json` và in lỗi.

### 3.2 Loader

```js
if (!(app.project && (app.project.file || app.project.numItems))) {
  var OPA_ARGS = {target: 'D:/.../project/X.aep', report: 'D:/.../build/_report.json', sfx: 'D:/.../assets/sfx'};
  var f = new File('D:/.../build/_bundle.jsx'); f.encoding = 'UTF-8'; f.open('r'); var s = f.read(); f.close(); eval(s);
}
```

- Loader là **một dòng**: `tools/ae.py` ghép sẵn thành một chuỗi rồi truyền làm một tham số. Bản trên xuống dòng chỉ để dễ đọc.
- Ý nghĩa các cờ:
  - `-noui`: chạy không giao diện;
  - `-m`: mở một phiên AE mới, riêng, không trao script cho phiên đang mở;
  - `-s`: chạy chuỗi script đi kèm.
- Loader chỉ đọc file bundle rồi `eval`. Không nhét cả script vào tham số `-s`.
- Trong loader không có `$` và không có dấu `"`, vì dòng lệnh Windows làm hỏng chúng. Đường dẫn viết bằng `/`.
- Dòng đầu là chốt an toàn: nếu phiên đã có project thì không chạy gì.
- Mấy cách sau không chạy được:
  - `-m -r file.jsx`: phiên mới tự thoát sau khoảng 6 s;
  - `$.evalFile` đặt trong `-s`.
- Phiên mở bằng `-s` tự thoát khi script chạy xong.
- Chạy một JSX bất kỳ (ví dụ script trích template, mục 12) cũng theo cách này: loader đọc file JSX rồi `eval`. Script phải tự ghi kết quả ra file.

### 3.3 Lưu .aep

- Phiên headless không lưu được project mới: `app.project.save(new File(...))` trả `false`.
- Cách làm: chép seed trống ra đường dẫn đích → `app.open(file)` → dựng → `app.project.save()` để lưu đè lên chính nó.
- Sửa một project có sẵn (nhánh B): chép project ra bản sao → mở bản sao → sửa → `save()`. Không mở file gốc.
- Template do bản AE cũ lưu cũng mở ra thành "converted", và phiên headless không lưu được nó. Nhờ Minh mở template bằng AE 2026 rồi File › Save As ra một file mới, một lần. Từ đó làm trên bản sao của file mới.
- Seed phải do chính AE 2026 lưu. Seed của bản AE cũ mở ra sẽ thành project "converted", khi đó `save()` đòi Save As.
- Mất seed, hoặc AE lên bản mới:
  - còn một file .aep do đúng bản AE hiện tại lưu: chép nó ra, mở bằng phiên headless, xóa mọi item (`app.project.item(i).remove()`, đi từ cuối về đầu), rồi `save()`. File đó thành seed mới;
  - AE vừa lên bản, chưa có file nào của bản mới: nhờ Minh mở AE, tạo project trống, File › Save As một lần.
- `main.jsx` kiểm project vừa mở có 0 item. Không đúng thì dừng.
- Đầu script gọi `app.beginSuppressDialogs()`, cuối script gọi `app.endSuppressDialogs(false)`.
- Đặt `project.expressionEngine = 'javascript-1.0'` và `project.bitsPerChannel = 8`.
- Hàm cần giao diện như `comp.openInViewer()` không dùng trong phiên headless.

### 3.4 Báo cáo

- Kênh kết quả duy nhất là file JSON do script ghi (`O.writeFile`). `app.exitCode` không truyền ra mã thoát.
- Mọi lỗi phải được ghi vào báo cáo. Không có khối `catch` rỗng.
- Báo cáo của ca mẫu nhánh A gồm:
  - `errors`, `warnings`;
  - `expressionErrors`: đã buộc tính mọi expression trước khi gom lỗi;
  - `textDump`: mọi layer chữ, kèm chữ, font, cỡ, `substitute`;
  - `comps`, `placements`, `texts` (công thức, mốc), `measures`;
  - `sfx`, `music`, `voice`, `saved`, `seconds`.

### 3.5 Treo, quá giờ

- Chỉ dừng đúng PID mình mở.
- Phiên bị buộc tắt thì lần mở sau hiện hộp "Crash Repair Options". Gửi phím Enter vào đúng cửa sổ của phiên mình (PostMessage theo PID) để chọn Continue.

## 4. Cấu trúc project

### 4.1 Phân tầng của template chuyên nghiệp

Template "Corporate Opener" (đọc bằng script ngày 21/10) phân tầng như sau:

`Master → Scene → Title (thiết kế chữ) → Text (nội dung) → layer chữ → Text Animator → Range Selector`

Mỗi tầng làm một việc:
- **Text:** nội dung, font, chuyển động theo từ, dòng hoặc ký tự.
- **Title:** gói text lại, để đổi chữ mà vẫn giữ cách dựng.
- **Scene:** vị trí, tỉ lệ, thời gian vào ra của cả khối, quan hệ với hình.
- **CONTROL:** màu, kích thước, vật liệu, điều khiển qua effect và expression.
- **Master:** thứ tự cảnh và các điểm nối.

Chất lượng của template đến từ cách phối các tầng này, không đến từ một hiệu ứng "chữ bay lên, mờ dần".

### 4.2 Cấu trúc ca mẫu nhánh A

```
00_MASTER/                     OPA_AGENT_MASTER_16x9: 5 cảnh, giọng đọc, marker câu thoại, comp âm
01_CANH (scene)/               S1_MO_DAU … S5_CTA; mỗi cảnh có null CAM
02_TITLE (thiet ke chu)/       TITLE_S1…S5: vị trí, offset thời gian, khối nhấn, icon đi kèm chữ
03_EDIT_CHU (sua chu o day)/   TXT_*: mỗi comp một layer "TEXT" có Text Animator
04_HINH/                       ART_* (nhân vật, mascot), UI_* (giao diện minh họa)
05_CONTROL (mau)/              CONTROL: null BRAND + Color Control; mọi màu shape nối bằng expression
06_AM_THANH/                   AM_THANH_SFX_NHAC: nhạc nền + các layer SFX; file WAV
```

- Tên comp và tên layer viết không dấu, để gọi `aerender -comp` và viết expression không lỗi mã hóa. Chữ hiển thị thì đủ dấu.
- `comp.comment` ghi mốc thời gian và cách sửa cho người mở project.
- Marker câu thoại nằm trên một null dẫn hướng (`guideLayer = true`, `enabled = false`), mỗi câu một marker tại giây bắt đầu.

### 4.3 Đặt comp con và đổi khung

- `O.place(cha, con)` đặt anchor bằng tâm comp con và position bằng tâm comp cha. Hai comp cùng kích thước thì toạ độ đi qua 1:1.
- Key trong comp con là khung **cục bộ**:
  - giây trên master = `sceneLayer.startTime + subLayer.startTime + … + giây của key` (cộng hết các tầng);
  - layer có stretch (`layer.stretch`, 100 = bình thường): giây trên comp cha = `startTime + giây cục bộ × stretch / 100`;
  - layer có time remap: không có công thức gọn. Tra bằng `timeRemap.valueAtTime(t)` trên comp cha để biết giây t của cha đang chiếu giây nào của con;
  - khung = `round(giây × fps)`.
- Ví dụ template: key f30 của Text 1 hiện ở f57 của Scene 1, vì Title 1 bắt đầu ở f27.
- `tools/bang_khung.py` (ca mẫu A) tự tính bảng mốc chữ theo khung master. `<VD-B>\parse_aep_timings.py` tính giây toàn cục cho mọi cảnh, comp con của template.

### 4.4 CONTROL màu

- Comp `CONTROL` có một null `BRAND`. Mỗi màu là một effect Color Control trên null đó.
- Màu của shape: đặt giá trị rồi gắn expression `comp("CONTROL").layer("BRAND").effect("blue")(1)`. Đổi một màu ở CONTROL thì cả phim đổi theo.
- Đổi màu tại một giây t: `var a = …, b = …; time < t ? a : b` (`O.fxColorSwitch`).

### 4.5 Cấu trúc template thương mại (ví dụ template 5)

- Comp tổng: `Final_4k (3840 x 2160)` và `Full_HD (1920 x 1080)`, chứa `01_Scene` … `13_Scene` nối nhau.
- Comp giữ chỗ (Holder) nằm trong thư mục Edit:
  - `Logo_Holder` (1000×1000);
  - `01_Person_Holder` … `08_Person_Holder` cho chân dung;
  - `06_Scene_Avatar01`, `06_Scene_Avatar02` cho avatar khung chat;
  - `Music_Holder` cho nhạc.
- Màu điều khiển tập trung ở các layer `Text Colors`, `Background Colors`, `Icons, Buttons & UI Colors` trong comp tổng. Vài comp còn màu gán cứng, ví dụ `Color_Flash` dùng `ADBE 4ColorGradient`, và Glow trên một số icon.
- Tên comp có thể trùng giữa các nhánh template. Nhận diện bằng ID kèm chuỗi sử dụng.

## 5. Keyframe và easing

### 5.1 Kiến thức nền

- Mỗi key có tay nắm vào (in) và tay nắm ra (out). Mỗi tay nắm là `KeyframeEase(speed, influence)`.
- **speed:** tốc độ tại key, đo bằng đơn vị của thuộc tính mỗi giây. 0 là đứng yên ở key.
- **influence:** tay nắm dài bao nhiêu % của đoạn, từ 0,1 đến 100. Càng lớn càng chậm lâu ở key.
- Easy Ease (phím F9) = speed 0, influence 33,33 %. Template chuyên nghiệp không dùng F9: chữ dùng khoảng 75 %.
- Sổ tay ghi preset dạng `{o: [k_o, inf_o], i: [k_i, inf_i]}`:
  - `o` là tay nắm ra của key đầu, `i` là tay nắm vào của key sau;
  - `k` là hệ số tốc độ: speed thật = k × tốc độ trung bình của đoạn.
- Đổi sang cubic-bezier của web:
  `cubic-bezier(inf_o/100, k_o × inf_o/100, 1 − inf_i/100, 1 − k_i × inf_i/100)`.

### 5.2 Bảng preset

Các preset nằm trong `O.EASE` của `lib.jsx`. Số trong ngoặc vuông là [hệ số tốc độ; influence %].

| Preset | o | i | cubic-bezier | Dùng cho | Nguồn |
|---|---|---|---|---|---|
| R1_IN | [0; 75,217] | [0; 75,121] | (0.752, 0, 0.249, 1) | Headline vào | template, đo native |
| R1_OUT | [0; 75,121] | [0; 75,217] | (0.751, 0, 0.248, 1) | Headline ra | template |
| R2_IN | [0; 75,322] | [0; 75,664] | (0.753, 0, 0.243, 1) | Nhãn phụ theo dòng (ra: đảo hai số) | template |
| R3_IN | [0; 75,217] | [0; 75,603] | (0.752, 0, 0.244, 1) | Display theo ký tự | template |
| R3_OUT | [0; 100] | [0; 20,993] | (1, 0, 0.79, 1) | Display ra | template |
| R4_IN | [0; 70,636] | [0; 70,540] | (0.706, 0, 0.295, 1) | Heading nhiều dòng | template |
| R5_IN | [0; 60,752] | [0; 60,174] | (0.608, 0, 0.398, 1) | Body theo dòng từ phải (ra: đảo hai số) | template |
| MASK (R10) | [0; 15,236] | [0; 100] | (0.152, 0, 0, 1) | Mở khung bằng matte: nhanh lúc đầu, đuôi dài | template |
| R6A, rồi R6B | [0; 0,01] → [0; 100] | [0; 100] → [0; 15,133] | | Thu cả khối chữ ở cấp Scene: 100 → 86 → 0 | template (Scene 5) |
| BRAND | [4; 20] | [0; 80] | (0.2, 0.8, 0.2, 1) | Vật vào cảnh | V2 (EASE_IN_SCENE) |
| EXIT | [0; 60] | [4; 20] | (0.6, 0, 0.8, 0.2) | Vật ra cảnh | V2 |
| SOFT | [0; 50] | [0; 50] | (0.5, 0, 0.5, 1) | Máy quay trôi, đoạn giữ | ca mẫu A |
| PUSH | [0; 85] | [2,2; 30] | (0.85, 0, 0.7, 0.34) | Máy quay lao vào điểm cắt | ca mẫu A |
| LIFT | [0; 15] | [0; 80] | (0.15, 0, 0.2, 1) | Vật cất cánh từ tốc độ 0 | ca mẫu A |
| LINEAR | — | — | đều | Nền trôi, kim đồng hồ | |
| HOLD | — | — | nhảy | Bật, tắt tức thì | |

- Mỗi vai trò một đường ease: chữ, mask, máy quay, vật khác nhau.
- Đừng tự thêm nảy (bounce) hay lò xo cho chữ khi công thức không có.

### 5.3 Đặt key bằng script

Hàm của ca mẫu: `O.anim(prop, [[khung, giá trị], [khung, giá trị, 'PRESET'], ...])`. Preset ghi ở key k là đường ease của đoạn từ key k−1 tới key k.

Thứ tự gọi bắt buộc:
1. `prop.setValueAtTime(t, v)` cho mọi key.
2. Lấy chỉ số key bằng `prop.nearestKeyIndex(t)`.
3. `prop.setTemporalEaseAtKey(k, inEase[], outEase[])`.
4. **Sau cùng** mới gọi `prop.setInterpolationTypeAtKey(k, inType, outType)`.

Lý do: `setTemporalEaseAtKey` đổi luôn phía LINEAR của key thành Bezier. Ca mẫu từng dính lỗi này: nền trôi "LINEAR" vẫn chậm dần ở hai đầu.

```js
// a, b: giá trị hai key liền nhau (1 chiều); dt: số giây giữa hai key; P = {o:[ko, io], i:[ki, ii]}
var avg = (b - a) / dt;
var outE = [new KeyframeEase(P.o[0] * avg, P.o[1])];
var inE  = [new KeyframeEase(P.i[0] * avg, P.i[1])];
prop.setTemporalEaseAtKey(k0, prop.keyInTemporalEase(k0), outE);
prop.setTemporalEaseAtKey(k1, inE, prop.keyOutTemporalEase(k1));
prop.setInterpolationTypeAtKey(k0, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER); // gọi sau ease
```

- Số phần tử của mảng ease bằng số chiều của thuộc tính:
  - Opacity: 1;
  - Scale: 3, kể cả layer 2D;
  - Audio Levels: 2;
  - Position là thuộc tính spatial nên chỉ 1 phần tử, là tốc độ dọc đường đi: speed = hệ số × (khoảng cách giữa hai key / số giây giữa hai key).
- Position đi thẳng: tắt `setSpatialAutoBezierAtKey` và `setSpatialContinuousAtKey`, rồi đặt `setSpatialTangentsAtKey(k, [0,0], [0,0])`. Không làm thì AE tự uốn cong đường đi.
- Đoạn giữ 100 → 100 nằm giữa pha vào và pha ra: dùng Bezier phẳng (SOFT) như template. Không cần HOLD.

### 5.4 Lò xo

- Lò xo OPA (SPRING_POP của V2): damping 12, stiffness 100, mass 1. Kết quả: vọt khoảng 9,5 %, đỉnh lúc 0,39 s.
- Trong AE, tính nghiệm lò xo y(t) = 1 − e^(−6t)·(cos 8t + 0,75·sin 8t) ra 4 key (`O.springKeys`, `O.popScale`). Ví dụ nút bật từ 0 lên 100 % ở 30 fps, bắt đầu tại khung `at`:

| Key | Khung | Scale (%) | Ease của đoạn đi tới key này |
|---|---|---|---|
| 1 | at | 0 | — |
| 2 | at + 12 (0,39 s) | 109,5 | BRAND |
| 3 | at + 24 (0,79 s) | 99,1 | SOFT |
| 4 | at + 39 (1,18 s + 4 khung) | 100 | SOFT |

- Key 4 là key cuối. Sau đó nút đứng ở 100 %, hoặc thở bằng expression.
- Số khung làm tròn bằng `Math.round(giây × fps)`. Ở 60 fps thì tính lại theo giây.
- Dùng key thay vì expression lò xo, để mở .aep ra vẫn thấy key.
- Lò xo dùng cho icon, nút, tin nhắn, mascot. Không dùng cho chữ: chữ đi bằng Text Animator.

### 5.5 Đổi fps

Giữ nguyên số giây, đổi số khung: khung ở 60 fps = khung ở 30 fps × 2. Influence giữ nguyên.

### 5.6 Đọc key từ project có sẵn

- Các hàm: `prop.numKeys`, `prop.keyTime(k)`, `prop.keyValue(k)`, `prop.keyInInterpolationType(k)`, `prop.keyInTemporalEase(k)[d].speed` và `.influence`, `keyTemporalAutoBezier`, `keyInSpatialTangent`.
- Script mẫu: `<SKILL>\references\template-audit\scripts\export-projects.jsx`.
- Giá trị enum: BEZIER = 6613, LINEAR = 6612, HOLD = 6614.
- Muốn lấy đường cong thật: đọc `prop.valueAtTime(f/fps, false)` mỗi 0,25 khung (`sample-and-render.jsx`).

## 6. Chữ

### 6.1 Text Animator hoạt động thế nào

- Animator chứa các giá trị lệch: Position [0, 1 em], Opacity 0, Blur. Range Selector chọn phần chữ chịu các giá trị lệch đó.
- Pha vào: keyframe `Start` từ 0 lên 100. Phần được chọn co dần, chữ lần lượt về đúng chỗ, rõ nét và hiện đủ. Pha ra: Start từ 100 về 0.
- Opacity 0 là độ mờ của phần đang được chọn. **Transform Opacity của layer chữ giữ ở 100.**
- Chỉ đặt key cho Position hay Opacity của cả layer thì không tạo được kiểu hiện theo từ, dòng, ký tự.
- **Một animator cho cả câu.** Đặt `Based On` = Từ thì AE tự chia từng từ. Không cần mỗi từ một animator.

| Phần | matchName |
|---|---|
| Animator | `ADBE Text Properties` › `ADBE Text Animators` › `ADBE Text Animator` |
| Giá trị lệch | `ADBE Text Animator Properties` › `ADBE Text Position 3D`, `ADBE Text Opacity`, `ADBE Text Blur` |
| Selector, Start | `ADBE Text Selectors` › `ADBE Text Selector` › `ADBE Text Percent Start` |
| Based On | `ADBE Text Range Advanced` › `ADBE Text Range Type2`: 1 = ký tự, 2 = ký tự trừ khoảng trắng, 3 = từ, 4 = dòng |
| Shape | `ADBE Text Range Advanced` › `ADBE Text Range Shape` = 1 (vuông) |

### 6.2 Công thức

Template đo trên chữ rất to (300 px, khổ 2160). Ca mẫu đổi sang em để giữ đúng tỉ lệ chuyển động.

| Mã | Dùng cho | Based On | Position | Blur | Ease |
|---|---|---|---|---|---|
| R1 | Headline | Từ (3) | [0; 1,0 em] | 0,427 em | R1_IN, R1_OUT |
| R2 | Nhãn phụ, cụm nhấn, câu định vị, nhãn CTA | Dòng (4) | [0; 0,667 em] | 0,667 em | R2 |
| R3 | Display, tên, URL, câu chốt | Ký tự (1) | [0; 0,711 em] | 0,356 em | R3 |
| R4 | Heading nhiều dòng, vào ra riêng | Dòng (4) | vào [0; −0,5 em], ra [0; +0,5 em] | 0,5 em | R4 |
| R5 | Body, mục danh sách | Dòng (4) | [2,0 em; 0] (từ phải) | 1,0 em | R5 |
| R6 | Cả khối chữ thoát | Không dùng animator: Scale của layer Title ở cấp Scene | 100 → 86 → 0 | | R6A, R6B |
| R10 | Mở khung, bảng | Không dùng animator: Size của khối matte từ 0 tới đủ | | | MASK |

- Mọi công thức chữ có Opacity 0 trên animator.
- Position của animator là `ADBE Text Position 3D`: nhập 3 số [x; y; 0]. Bảng ghi x; y. Blur nhập 2 số bằng nhau [b; b]. Bảng ghi b.
- R4 cần 2 animator: một animator vào (Start 0→100), một animator ra (End 0→100).
- Thời lượng mặc định: vào 30 khung, ra 30 khung. Ca mẫu: R6 thu 12 khung rồi 9 khung; R10 mở trong 28 khung.
- Gọi trong ca mẫu: `O.textAnim(layer, 'R1', {em: 126, inAt: 4, inDur: 30, outAt: 122, outDur: 28})`.
- Nhịp của template:
  - chữ chính vào trước, nhãn phụ vào trễ 28 khung (0,93 s);
  - hai nhóm rút ra cùng lúc;
  - nhờ vậy có thứ bậc khi vào và gom nhóm khi ra.

### 6.3 Đặt chữ theo hộp đo

- `layer.sourceRectAtTime(t, false)` trả {left, top, width, height} của phần chữ thật.
- Đặt mép trên-trái khối chữ tại (x, top): position = [x − left, top − rect.top] (`O.placeTop`).
- Co chữ cho vừa bề rộng, nhưng không nhỏ hơn 28 px (`O.fitWidth`).
- Khối nền, bong bóng giãn theo chữ: expression đọc `sourceRectAtTime` của layer chữ. Ví dụ: nút CTA của ca mẫu rộng 742 px theo URL.
- Text layer có anchor [0,0] gắn với baseline. Đó là bình thường, không phải lỗi.

### 6.4 Font

- Đặt font bằng tên PostScript, ví dụ `td.font = 'BeVietnamPro-ExtraBold'`.
- Sau `setValue(td)` thì đọc lại để kiểm:
  - `td.font` phải bằng tên đã đặt;
  - `td.fontObject.isSubstitute` phải là false;
  - toàn project: `app.fonts.missingOrSubstitutedFonts` phải rỗng.
- Chế độ headless không hiện hộp thoại báo thiếu font. Phải tự kiểm và ghi vào báo cáo.
- Cài font mới cho AE thấy:
  1. Chép file font vào `%LOCALAPPDATA%\Microsoft\Windows\Fonts` và ghi khóa HKCU `...\CurrentVersion\Fonts`, để font còn sau khi khởi động lại. Riêng bước này thì AE chưa thấy.
  2. Gọi `AddFontResourceW` và phát `WM_FONTCHANGE`:

```powershell
Add-Type @"
using System; using System.Runtime.InteropServices;
public class FontReg {
 [DllImport("gdi32.dll", CharSet=CharSet.Unicode)] public static extern int AddFontResourceW(string file);
 [DllImport("user32.dll", SetLastError=true)] public static extern IntPtr SendMessageTimeout(IntPtr h, uint msg, IntPtr w, IntPtr l, uint flags, uint timeout, out IntPtr res);
}
"@
$file = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Fonts\<Font>.ttf'
[FontReg]::AddFontResourceW($file)
$res = [IntPtr]::Zero
[void][FontReg]::SendMessageTimeout([IntPtr]0xffff, 0x001D, [IntPtr]::Zero, [IntPtr]::Zero, 0x0002, 3000, [ref]$res)
```

  3. Mở phiên AE mới, vì AE quét font lúc khởi động.
- Font biến thiên (variable font, chỉ có trục wght): AE cần file tĩnh. Cố định giá trị wght rồi ghép đủ bộ Latin và tiếng Việt. Ví dụ: `<VD-A>\tools\build_accent_font.py` làm Fraunces wght 800.
- Font của bộ OPA: Be Vietnam Pro (ExtraBold, SemiBold, Bold, Medium) và `<VD-A>\assets\fonts\FrauncesOPA-ExtraBoldItalic.ttf` (OFL).

### 6.5 Luật chữ của Minh

- Viết hoa chữ cái đầu mọi dòng hiển thị, kể cả mục danh sách. Dòng mở đầu bằng số thì viết hoa chữ cái đầu tiên sau số. Tên file và URL giữ chữ thường.
- Cỡ chữ nhỏ nhất 28 px (khung cao 1080). Ở khung 4K (cao 2160) là 56 px. Tính theo cỡ hiệu dụng: cỡ font × tích scale của các tầng cha. Ví dụ font 300 trong Title scale 75 % là 225 px.
- Cụm nhấn: dùng font khác thân bài, kèm hiệu ứng có nghĩa. Cách làm ở video OPA:
  - font Fraunces Italic 800;
  - khối đánh dấu quét từ trái trong 8 khung: đệm trái 0,12 em, đệm phải 0,22 em, cao 1,26 em;
  - chữ nằm trên khối là bản sao + effect Fill + track matte theo khối (`O.accentBlock`).
- Mục song song: cùng font, cùng cỡ, cùng công thức, cùng âm.
- Chữ lấy đúng kịch bản khóa. Không đoán tên riêng, số liệu, CTA.
- Soát tự động: `python -I tools/qa_chu.py` (đọc `textDump` trong báo cáo dựng).

### 6.6 Thay chữ trong template

- **Giữ tên layer.** Nhiều template dùng tên layer chữ trong expression, ví dụ để đo `sourceRectAtTime()` cho hộp nền. Layer chưa đặt tên riêng thì AE lấy chính nội dung chữ làm tên, nên đổi chữ là đổi luôn tên và gãy expression. Cách làm:
  1. lưu `var origName = layer.name;`;
  2. gán chữ mới bằng `setValue(textDocument)`;
  3. trả lại `layer.name = origName;`.
- **Câu tiếng Việt dài hơn câu mẫu.** Câu tiếng Việt thường nhiều từ hơn câu tiếng Anh gốc. Ca mẫu B thấy Text Animator theo từ dừng khi chưa hiện hết, chữ cuối còn mờ; nguyên nhân cụ thể chưa ghi lại. Cách ca mẫu B sửa (`fixTextAnimator` trong `<VD-B>\customize_template_assets.jsx`):
  - đặt `ADBE Text Levels Max Ease` = 0;
  - đặt lại 2 key của `ADBE Text Percent Start`: 0 % → 100 % trong 0,20–1,05 s (thẻ lật nhanh: 0–0,45 s). Đây là giây cục bộ của comp chữ.
- Hàm đó xóa mọi key Start của mọi animator và không đặt ease, nên mất luôn pha ra và đường ease của template. Làm đúng hơn:
  - chỉ đặt lại 2 key pha vào của animator vào;
  - giữ nguyên pha ra;
  - đặt ease theo vai trò (mục 5.2).
- Sau khi thay: đo `sourceRectAtTime` để chắc chữ không tràn khung, rồi chạy soát chữ.

## 7. Hình: shape, matte, parent, expression, máy quay, nhân vật, giao diện

### 7.1 Shape layer

- AE vẽ nhóm **đứng đầu danh sách lên trên cùng**. Muốn phần tử đầu mảng nằm dưới thì thêm nhóm theo thứ tự ngược (`O.shape`).
- Trong một layer, tên các nhóm phải khác nhau, vì hàm tìm nhóm theo tên.
- matchName hay dùng:
  - `ADBE Root Vectors Group` › `ADBE Vector Group` › `ADBE Vectors Group`;
  - hình chữ nhật: `ADBE Vector Shape - Rect` (`ADBE Vector Rect Size`, `ADBE Vector Rect Roundness`);
  - elip: `ADBE Vector Shape - Ellipse`; đường path: `ADBE Vector Shape - Group`;
  - tô và viền: `ADBE Vector Graphic - Fill`, `ADBE Vector Graphic - Stroke`;
  - vẽ nét dần: `ADBE Vector Filter - Trim`;
  - transform của nhóm: `ADBE Vector Transform Group`.
- Path trong AE gồm đỉnh và tiếp tuyến tương đối (vertices, inTangents, outTangents).
- Đổi SVG sang path AE: `<VD-A>\tools\svg_to_ae.py`. Cung A được đổi sang Bézier, mỗi đoạn ≤ 90°, sai số dưới 0,03 px.

### 7.2 Track matte, mask

- Gắn matte: `layer.setTrackMatte(matteLayer, TrackMatteType.ALPHA)`.
- Matte chỉ làm khuôn thì đặt `matte.enabled = false`. Matte vừa làm khuôn vừa phải hiện, như khối nhấn, thì để `enabled = true`.
- Mở khung kiểu R10: animate Size của khối matte từ 0 tới đủ với ease MASK. Thêm một viền chạy theo mép khối, để không lộ lỗ trống.
- Mask chữ nhật trên layer: `ADBE Mask Parade` › `ADBE Mask Atom` › `ADBE Mask Shape` (`O.rectMask`).

### 7.3 Parent

- Parent truyền vị trí, tỉ lệ, góc xoay. **Parent không truyền opacity.** Con cần mờ theo cha thì gắn expression `thisComp.layer("Cha").transform.opacity` (`O.followOpacity`).
- Position của layer có parent là toạ độ cục bộ. Muốn toạ độ thật trên khung thì dùng `toComp()` trong expression.

### 7.4 Expression hay dùng

- Engine là `javascript-1.0`.
- Thở (co giãn nhẹ, 100–103 % như Bò OPA): `var s = 100 + 1.5 * (1 - Math.cos(time * 2 * Math.PI * 0.5)); [s, s]`.
- Lắc nhẹ: `Math.sin(time * 2 * Math.PI * 0.9) * 2`.
- Con trỏ gõ chữ nhấp nháy: `Math.floor(time * 30 / 8) % 2 ? 0 : 100`.
- Kích thước theo chữ: đọc `comp("TXT_…").layer("TEXT").sourceRectAtTime(t, false)`.
- Sau khi dựng, buộc tính mọi expression bằng `valueAtTime`, rồi gom `expressionError` vào báo cáo. Ca mẫu A: 388 expression, 0 lỗi.
- Template mua về có thể có sẵn expression lỗi, ví dụ gọi một thuộc tính không tồn tại. Đừng chép lỗi đó sang bản mới.

### 7.5 Máy quay ảo, motion blur

- Mỗi cảnh có một null `CAM`. Mọi layer chính gắn parent vào CAM.
- CAM trôi Scale và Position một đường chậm, đều suốt cảnh. Ví dụ cảnh 5: 100 → 106 % trong 6 s, ease LINEAR.
- Motion blur phải bật ở hai chỗ: comp (`comp.motionBlur = true`) và layer (`layer.motionBlur = true`). Chỉ bật cho layer chuyển động nhanh.
- Blur trong công thức chữ là Text Animator Blur, khác motion blur.

### 7.6 Effect: số thô khác số trên giao diện

Script đọc số thô, không phải con số hiện trong bảng Effect Controls:

| Thuộc tính | Số thô | Trên giao diện |
|---|---|---|
| Drop Shadow Opacity | 76,5 (thang 0–255) | 30 % |
| Glow Threshold | 153 (thang 0–255) | 60 % |
| Fill Opacity | 1 (thang 0–1) | 100 % |

- Đọc `unitsText`, `minValue`, `maxValue` trước khi chép số.
- Kiểm effect hoặc layer style có đang bật không (`enabled`, `active`). API vẫn đọc được giá trị của style đang tắt.

### 7.7 Mẫu: con trỏ bấm nút (cảnh 5 ca mẫu A)

Khung ở đây là khung cục bộ của comp `TITLE_S5`. Cộng 900 ra khung master.

| Vật | Thuộc tính | Key |
|---|---|---|
| Con trỏ | Position | f92 ngoài khung [1880; 1040] → f122 tới điểm bấm (BRAND) → f128 lún thêm [−4; +4] px (SOFT) → f136 về điểm bấm (SOFT) |
| Con trỏ | Opacity | f92 = 0 → f96 = 100 (LINEAR) |
| Nút | Scale | f124 = 100 → f128 = 94 (BRAND) → f136 = 100 (BRAND) |
| Gợn bấm | Scale | f126 = 100 → f150 = [118; 150] (BRAND) |
| Gợn bấm | Opacity | f124 = 0 → f126 = 90 (LINEAR) → f150 = 0 (EXIT) |
| Nút thở | Scale, expression | từ f140: `var t = time - 140 / 30; var k = t > 0 ? 2.5 * Math.sin(t * 2 * Math.PI / 1.2) : 0; [value[0] + k, value[1] + k]` |

- Điểm bấm đặt ngay sau chữ URL, để con trỏ không che chữ.
- Âm: lớp press + lớp click có đỉnh ở f125, lúc nút vừa lún; tiếng release có đỉnh ở f130.
- Bật motion blur cho con trỏ.

### 7.8 Nhân vật, mascot tách bộ phận

Kỹ thuật rig (tách bộ phận để diễn trong AE), học từ dự án Motion Omi:
- Bộ tấm thiết kế nhân vật:
  - CS01: xoay 4 góc;
  - CS02: biểu cảm;
  - CS03: tách bộ phận trên nền phẳng để cắt PNG, SVG;
  - CS04: tư thế hành động;
  - CS05: bản đồ tâm xoay.
- Đặt anchor đúng chỗ khớp:
  - thân: anchor ở chân đế, để nhún nảy mà chân vẫn bám sàn;
  - sừng, tay: parent vào thân, anchor ở gốc khớp, để xoay không rời khớp;
  - bong bóng chat: anchor ở đuôi nhọn, để bung ra từ người gửi.

**Bò OPA theo `<OPA>\BRAND-SPEC.md`:**
- không mắt, miệng, tay chân; chỉ 5 màu;
- không bóp méo: chỉ co giãn đều mọi trục, nên không squash & stretch kiểu [108; 92] → [95; 106].

Bản mascot của Motion Omi có mắt LED, sừng tia sét vàng #FFD400, thân nam châm chữ U. Bản này trái các luật trên, và chưa có ghi nhận Minh duyệt. Chỉ dùng khi brief nêu rõ, hoặc Minh duyệt.

### 7.9 Đưa giao diện UI vào AE

- Ảnh UI sinh bằng AI dùng prompt 7 phần: loại màn hình + ngành hàng + danh sách thành phần + mã màu + font + phong cách + "4K UI mockup". Bản đầy đủ (cấu trúc 7 phần, prompt mẫu, bảng màu ngành hàng, lệnh xuất SVG tách lớp và bộ tấm nhân vật `CS01..CS05`) nằm ngay trong gói tại `<SKILL>\references\sketch-to-ui-va-nhan-vat.md`.
- Ba cách đưa vào AE:
  1. **Phác thảo hóa thật:** bản vẽ tay ở dưới, bản UI thật ở trên, quét bằng Linear Wipe hoặc mask.
  2. **Màn hình nghiêng có chiều sâu:** bật 3D Layer, nghiêng màn hình, đẩy các thẻ nổi lên trục Z −20 … −50 px để máy quay lia qua thấy chiều sâu.
  3. **SVG → Illustrator → AE:** SVG chia nhóm `<g id>` → Illustrator "Release to Layers" → lưu .ai → nhập vào AE kiểu "Composition - Retain Layer Sizes", để diễn từng thẻ riêng.
- Video OPA theo BRAND-SPEC: nền phẳng, 5 màu; không gradient, glow, bóng đổ, 3D bóng loáng (phim 3D trong `film3d/` là ngoại lệ riêng).
  - 5 màu OPA: xanh #0068FF, xanh đêm #003C99, xanh nhạt #E6F0FF, đen #0A0A0A, trắng #FFFFFF.
  - Đỏ cảnh báo #E5484D chỉ dùng cho dấu cảnh báo nhỏ.
  - Turbulent Displace và Glow ở cách 1, lớp 3D ở cách 2, bảng màu #0A2540 / #0052FF / #00E5FF / #FFD400 của ca Motion Omi chỉ dùng cho video không theo BRAND-SPEC OPA, hoặc khi Minh duyệt.
- Template có sẵn glow, kính mờ, gradient, 3D mà video là của OPA: mặc định làm phẳng theo BRAND-SPEC. Muốn giữ hiệu ứng của template thì Minh quyết ở G0.

### 7.10 Ảnh, logo, nút có chữ

- Nhập ảnh, logo PNG: `var it = app.project.importFile(new ImportOptions(new File(path)));` → `var L = comp.layers.add(it);` → đặt bằng `O.setT`. Ảnh nhập xong cho vào thư mục `04_HINH` (`it.parentFolder`).
- Logo là vật, không phải chữ. Cho vào bằng Scale và Opacity với ease BRAND, hoặc lò xo (mục 5.4). Logo khách giữ đúng tỉ lệ, không bóp méo.
- Nút có chữ (ca mẫu A, cảnh 5):
  1. nút là shape, bật lò xo ở khung f66;
  2. chữ trên nút là layer chữ riêng trong comp `TXT_…`, vào bằng R3 từ khung f72, tức sau khi nút đã bật;
  3. đặt layer chữ nằm trên nút (`moveBefore`);
  4. nút rộng theo chữ: đo `sourceRectAtTime` của chữ rồi tính bề rộng nút.
- Lò xo áp cho nút, không áp cho chữ trên nút.

## 8. Chuyển động và nhịp (gu của Minh)

- Mặc định: mượt, giàu chuyển động, chuyên nghiệp. Hai lời chê đã có:
  - V2 bản đầu "nhàm": 70 % khung gần như đứng yên;
  - phim 3D bản 1 "lúc nhanh lúc chậm".
- Nhịp phải đều:
  - máy quay trôi một đường chậm suốt cảnh;
  - hành động rơi đúng phách nhạc (120 BPM: mỗi phách 0,5 s = 15 khung ở 30 fps);
  - không lia máy gấp.
- Chuyển cảnh không cắt cứng. Một vật nở ra phủ kín khung đúng ở khung cuối cảnh trước; cảnh sau tan ra từ đó trong khoảng 10 khung. Ví dụ ca mẫu A:
  - nối 1→2: tin nhắn trắng nở ra;
  - nối 2→3: đĩa sáng nở đều trong 11 khung;
  - nối 4→5: khung xanh nở ra.
- So le đều: các mục song song cách nhau đều nhau (ca mẫu A: 28 khung).
- Chữ chạy suốt phim, mỗi nhịp một câu, đủ thời gian đọc.
- Đo bằng `python -X utf8 "<SKILL>/scripts/v2w/metrics.py" <mp4> --no-flow`. Đạt khi:
  - mỗi ô 2 s có ≤ 15 % khung gần đứng yên (Tĩnh B);
  - Tĩnh A = 0;
  - 0 cắt cứng.
  Đoạn giữ logo sau khi logo đã hiện xong được miễn đo (`--exempt`, Minh chốt 24/10).
- Video OPA theo BRAND-SPEC: 5 màu, nền phẳng; không gradient, glow, bóng đổ, 3D bóng loáng; mascot đúng hình. Góp ý "tiết chế" của agent không phải luật.

## 9. Âm thanh

### 9.1 Thang mức trong bản trộn (trước master)

| Lớp | Mức | Căn cứ |
|---|---|---|
| Giọng đọc | −16,3 LUFS. SFX và nhạc cộng thêm khoảng 0,3 LU, nên cả bản ra −16 | chuẩn của Minh; AES TD1008 (lời −18, nhạc −16) |
| Nhạc nền (có giọng) | −31 LUFS tích hợp, tức 15 LU dưới giọng (±1); LRA ≤ 5 LU | quy trình nền 1.2.3 Minh duyệt |
| SFX chuyển cảnh, logo | M −24,5 … −27 | đặt vào khoảng nghỉ giữa các câu |
| SFX sự kiện giao diện | M −27 … −33 | nhô trên nhạc tại chỗ 0–4 LU |
| Tiếng nhỏ (đồng hồ, gõ phím, click) | M −33 … −38; lớp tách của cú bấm xuống tới −46 khi trùng lời | âm ngắn và sáng nên vẫn nghe rõ dù M thấp |
| Mọi SFX lúc đang nói | thấp hơn giọng ≥ 8 LU | |
| Mỗi cue | đỉnh thật ≤ −12 dBTP, tính cả âm chồng cùng khung | âm trùng đỉnh giọng sẽ đẩy bản trộn quá trần (bài học B8) |
| Cả bản ngắn | độ to ngắn hạn lớn nhất ≤ tích hợp + 5 LU | EBU R 128 s1 |

- M đích là độ to tức thời lớn nhất (cửa sổ 400 ms) của riêng cue đó khi phát trong bản trộn.
- Mức cú bấm ở ca mẫu A (M đích):

| Lớp | Cảnh 2, trùng lời | CTA, trong khoảng nghỉ |
|---|---|---|
| Thân (press) | −29,5 | −28,5 |
| Tách (click) | −46 | −29; trần đỉnh giữ lại còn −41 |
| Nhả (release) | −32,5 | −31,5 |

- WCAG 1.4.7 (nền dưới lời ≥ 20 dB) là mức AAA cho người nghe kém, chỉ để tham khảo. Chuẩn Minh duyệt: nhạc 15 LU dưới giọng; lúc đang nói, giọng cao hơn nền ≥ 10 LU.
- EBU R 128 s1 cho phép đỉnh thật −1 dBTP. Chuẩn của Minh chặt hơn: file giao ≤ −2 dBTP. Bảng mức trong `<VD-A>\audio\BANG-CUE-AM-THANH.md` ghi tiếng giao diện −27 … −31; thực tế ca mẫu A dùng tới −33.
- Video không có giọng đọc: xem mục 9.10.

Đường link nguồn web nằm trong `<VD-A>\audio\BANG-CUE-AM-THANH.md`. Bản nghiên cứu đầy đủ: `<SKILL>\references\nghien-cuu-decibel.md`.

### 9.2 Đo cho đúng

- Độ to tính theo ITU-R BS.1770-4:
  - lọc K ở 48 kHz;
  - M dùng cửa sổ 400 ms;
  - I có cổng −70 LUFS và −10 LU;
  - đỉnh thật lấy mẫu ×4.
- **File mono:** AE phát ra cả 2 kênh với nguyên mức (L = R = file × gain). Vì vậy nghe to hơn số đo trên file mono 3 LU.
  - Đo đúng: nhân đôi kênh nguyên mức, bằng numpy `repeat` hoặc ffmpeg `pan=stereo|c0=c0|c1=c0`.
  - Không dùng `-ac 2` hay `aformat` của ffmpeg: chúng chia −3 dB mỗi kênh. Ca mẫu A từng vì vậy làm nhạc to hơn đích 3 LU.
- Âm ngắn hơn 400 ms: đệm im lặng tới 400 ms rồi mới đo M. Click, tick đo thêm trong dải tần ở cửa sổ ngắn, vì thước 400 ms đánh giá thấp chúng.
- Công cụ: `python -I tools/phan_tich_sfx.py "<kho>" out.csv` (có trong `<VD-A>\tools`). Các cột: dur, eff, onset, **peak_s**, peak_dbfs, tp_dbtp, m_max, i_lufs, centroid.
- Kho SFX của Minh đã đo sẵn: `<SKILL>\data\kho_sfx_do.csv` (2.982 file, đo ngày 22/10 sau khi sửa cách đọc file mono).
  - CSV chỉ dùng để chọn âm. Gain luôn được tính lại trên file WAV đã chép, trong `am_thanh_cues.py`.

### 9.3 Chọn SFX

- Kho: `<SFX>` (CC0, MIT), chia 7 nhóm theo chuyển động, cộng thư mục packs (`uisfx-themes` 12 chủ đề, Kenney, Remotion).
- Không dùng theSOUNDS. Kho không có nhạc nền dài.
- Chọn theo chuyển động:

| Chuyển động | Loại âm |
|---|---|
| Vật bật lò xo | pop, bounce |
| Icon bật | tick, marimba |
| Vật bay, chuyển cảnh | whoosh |
| Dẫn vào cao trào | swell, riser |
| Va chạm | thump |
| Cú bấm | press + click + release |
| Logo | sonic logo |

- Chọn bộ âm theo gu của video:
  - explainer vui, nhân vật (ca mẫu A): pop có nốt, marimba, tick. Minh đã duyệt bộ này ở v09;
  - quảng cáo SaaS, công nghệ sang (ca mẫu B): `packs/uisfx-themes/{studio, glass, minimal, scifi, soft, cinematic, zen}`, âm ấm, gọn; tránh âm hoạt hình, còi chói, whoosh nhiễu gắt;
  - video có cả nhân vật lẫn giao diện: chọn theo từng khoảnh khắc. Nhân vật nảy, bật dùng pop, bounce; thao tác giao diện dùng bộ uisfx. Mỗi loại khoảnh khắc giữ một họ âm. Gu cuối cùng do Minh chốt khi nghe đoạn mẫu.
- Âm có nốt phải hợp giọng của nhạc (ca mẫu A ở La trưởng). Đo cao độ bằng `python -X utf8 "<SKILL>/scripts/cao_do.py" <file1> <file2> …` (in 3–4 đỉnh phổ mạnh nhất kèm tên nốt). Lệch thì dịch bằng `aresample=48000,asetrate=48000*2^(c/1200),aresample=48000`. Âm sẽ ngắn lại theo cùng tỉ lệ. Ca mẫu A đã dịch success +200 cent, glass expand và collapse +155 cent.
- Mục song song dùng cùng âm, cùng mức. Một âm lặp lại nhiều lần (tin nhắn mới) thì lấy cách một, để hai lần cách nhau ≥ 0,5 s.
- Không đặt hai âm gần giống nhau cách nhau dưới 3 khung: tai nghe thành tiếng đúp.
- Chép sang WAV 48 kHz trước khi đưa vào AE. AE không đọc OGG; MP3 bị lệch giờ do độ trễ của bộ mã.
  - `am_thanh_cues.py` tự đổi cả SFX lẫn giọng.
  - Đổi tay: `ffmpeg -y -i vao.mp3 -ar 48000 -c:a pcm_s24le ra.wav`.
  - Tùy chọn cho tiếng UI êm hơn (ca mẫu B): thêm `lowpass=f=11000`. Lọc này đổi chất âm, nên nghe thử trước khi áp cả bộ.

### 9.4 Đặt SFX theo chuyển động

- **Căn đỉnh âm, không căn đầu file:** `layer.startTime = khung_hình / fps − peak_s`. peak_s là số giây từ đầu file tới lúc biên độ lớn nhất.
  - SFX đặt trong comp cảnh (nhánh B): `layer.startTime = (giây_toàn_cục − giây_bắt_đầu_cảnh) − peak_s`.
- Đỉnh rơi đúng khung chạm, hoặc khung vật chuyển động nhanh nhất. Không bao giờ sớm hơn hình; trễ tới 1 khung thì chấp nhận được.
- Whoosh chuyển cảnh: đỉnh ngay trước điểm cắt khoảng 1 khung, lúc vật nở nhanh nhất.
- Cú bấm gồm 2 lớp cùng khung (thân press + tách click), cộng tiếng nhả sau 4–5 khung.
- Gain = M đích − M đo được của file. Sau đó hạ thêm nếu đỉnh thật vượt −12 dBTP.
- Dựng lại stem SFX để đo đỉnh trong ±40 ms quanh mỗi cue, tính cả âm chồng. Nhóm cue nào vượt trần thì hạ cả nhóm.
- Ghi lại các chuyển động cố ý không gắn âm, kèm lý do. Ví dụ: chữ vào ra đã có lời đọc lo; chuyển động nền chạy liên tục.
- Công cụ của ca mẫu A: `<VD-A>\tools\am_thanh_cues.py`.
  - Sinh `build/data/am_thanh_cues.jsxinc`, mỗi cue gồm file, khung đỉnh, gain, tên layer.
  - Sinh bảng đọc được `audio/BANG-CUE-AM-THANH.md`.
- **Chống phát đúp:** ca mẫu B đặt SFX ở hai nơi: comp SFX riêng (`00_OPA_SFX_Master`) và trong từng comp cảnh. Khi đó, trong comp chính để render (`Final_4k`, `Full_HD`), đặt `audioEnabled = false` cho các layer cảnh. Không làm vậy thì mỗi tiếng phát hai lần, to thêm 6 dB.
  - Nếu nhạc hay âm nào khác nằm trong comp cảnh, tắt âm layer cảnh sẽ tắt luôn chúng. Khi đó chuyển nhạc ra comp SFX riêng, hoặc bỏ bản SFX trong comp cảnh.
  - Cách gọn nhất: mỗi tiếng chỉ đặt ở một nơi.

### 9.5 Khi có giọng đọc

- Dùng nguyên file Minh gửi. Chép sang WAV 48 kHz 24-bit, đặt gain để giọng ở −16,3 LUFS khi phát.
- Đặt marker cho từng câu theo chỗ năng lượng tăng lại sau khoảng nghỉ.
- Chữ lấy từ kịch bản; whisper chỉ dùng để căn giờ. Mốc từ của whisper thường sớm 0,1–0,4 s.
- Câu đọc dài hơn cảnh: cho lời vào trước hình (J-cut), không cắt câu.
- SFX trong lúc đang nói:
  - âm nhiều năng lượng ở 2–8 kHz (swish, whoosh, riser, giấy): đặt vào khoảng nghỉ, đỉnh sớm hơn đầu từ kế tiếp ≥ 0,07 s, hoặc bỏ;
  - kiểm che phụ âm: lọc dải 2–8 kHz, RMS 10 ms, xét **cả cửa sổ quanh cue**. SFX phải thấp hơn phụ âm ≥ 8 dB;
  - ví dụ ca mẫu A: tiếng chip to hơn phụ âm 15,5 dB (cần sửa: bỏ); lớp tách chỉ thấp hơn 3,6 dB (nên sửa: hạ 6 dB);
  - nếu chỉ xét giọng tại khung đỉnh thì sẽ bỏ sót đuôi âm chạy vào âm tiết sau;
  - whisper không nhạy với lỗi này (độ tin cậy vẫn 1,0), nên phải đo bằng dải tần.
- Đo che phụ âm bằng code dưới đây. Stem SFX dựng lại bằng `am_thanh_cues.sfx_stem(rows, peaks)` từ `build/data/am_thanh_cues.jsxinc`; giọng là file WAV nhân gain.

```python
# v = giọng (đã nhân gain), s = stem SFX: cùng 48 kHz, mảng numpy (n, 2); t = giây của cue
import numpy as np
from scipy.signal import butter, sosfilt

def band_db(x, sr=48000, w=480):  # dải 2–8 kHz, RMS 10 ms, ra dB
    y = sosfilt(butter(4, [2000, 8000], btype="bandpass", fs=sr, output="sos"), x, axis=0)
    n = len(y) // w
    return 10 * np.log10((y[:n * w] ** 2).reshape(n, w, -1).mean(axis=(1, 2)) + 1e-20)

bv, bs = band_db(v), band_db(s)
i, j = int((t - 0.10) * 100), int((t + 0.15) * 100)  # cửa sổ quanh cue
act = bv[i:j] > bv[i:j].max() - 20                   # khung giọng đang có phụ âm
print("SFX trừ giọng:", (bs[i:j][act] - bv[i:j][act]).max(), "dB")  # đạt khi ≤ −8
```

- Nhạc dưới giọng: lúc đang nói, giọng cao hơn nhạc + SFX ≥ 10 LU, đo theo cửa sổ 3 s. Ca mẫu A thấp nhất 11,7 LU.
- Dìm nhạc (duck) chỉ khi đo thấy cần. Ca mẫu A đã thử dìm −4 dB, không đổi gì nên bỏ.
- Kiểm rõ lời: chạy whisper trên bản trộn rồi so với giọng riêng. Ca mẫu A khớp 99,3 %.
- Kiểm đồng bộ: tương quan chéo giọng gốc với bản xuất.
- AAC của AE trễ đều khoảng 21 ms (1024 mẫu, 0,64 khung ở 30 fps). Mức này dưới ngưỡng nghe ra lệch, không cần bù.

### 9.6 Nhạc nền

- Video OPA: không dùng nhạc có bản quyền mà tự tổng hợp. Ca mẫu A dùng `<OPA>\tools\audio\score_agent.py`:
  - 36 s, 120 BPM, La trưởng, chia theo 5 cảnh;
  - mỗi cảnh có phách 1 riêng, để cú "đáp" rơi đúng mốc cảnh;
  - dựng lại ra đúng từng bit.
- Xử lý nền:
  - lọc bỏ dưới 100 Hz, giảm 3 dB ở 2 kHz;
  - vào dần 1 s, tắt dần 1,5 s;
  - LRA ≤ 5 LU;
  - mức tuyệt đối đặt bằng gain của layer trong AE.
- Để một khoảng lặng ngắn trước cú đáp cho SFX swell, whoosh, logo lấp vào. Ca mẫu A: 13,1–13,5 s và 29,93–30,4 s.
- Video không phải OPA: chỉ dùng nhạc có quyền dùng, do khách hoặc Minh đưa (có giấy phép). Chưa có thì hỏi Minh. Kho mặc định trên máy Minh nằm ở mục A.8 của `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/AI Video/prompts/MASTER_VIDEO_EDITOR_VI.md`.
- File nhạc gốc (hoặc nhạc đã duyệt) giữ nguyên, kiểm bằng MD5. Mọi xử lý làm trên một file WAV dẫn xuất, rồi đưa file đó vào `assets/music/` cho AE:

```bash
# cắt đúng thời lượng video (ví dụ 10 s), vào dần 1 s, tắt dần 1,5 s, lọc dưới 100 Hz, WAV 48 kHz
ffmpeg -y -i nhac-goc.mp3 -t 10 -af "highpass=f=100,afade=t=in:d=1,afade=t=out:st=8.5:d=1.5" -ar 48000 -c:a pcm_s24le assets/music/nhac-nen.wav
# có giọng đọc thì thêm vào chuỗi lọc: equalizer=f=2000:t=q:w=1:g=-3 (giảm 3 dB ở 2 kHz cho lời rõ)
```

- Cắt nhạc ở chỗ hết câu nhạc thì nghe tự nhiên hơn cắt giữa câu. Nghe thử điểm cắt trước khi chốt.

### 9.7 Đưa âm vào AE

- Dựng một comp âm riêng (ca mẫu A: `AM_THANH_SFX_NHAC`; ca mẫu B: `00_OPA_SFX_Master`). Thêm nhạc trước để nằm dưới cùng, rồi tới các SFX. Đặt comp này vào master.
- Mức của layer: `layer.property('ADBE Audio Group').property('ADBE Audio Levels').setValue([dB, dB])`.
- Giọng đọc là một layer riêng trong master, bắt đầu từ 0 s.
- Ghi marker tại giây của mỗi cue để người mở project tìm nhanh.

### 9.8 Master file giao

```bash
python -X utf8 "<SKILL>/scripts/master.py" out/review/_lam/bNN_709.mp4 out/review/<TEN>_vNN.mp4 --I -16.1 --TP -2.5 --voice assets/voice/<giong>.wav
```

- Công cụ chạy loudnorm hai lượt và **chỉ nhận chế độ tuyến tính** (không nén).
  - Không đạt vì đỉnh quá cao: công cụ in 8 điểm đỉnh thật cao nhất rồi thoát mã 2 mà không ghi file.
  - Khi đó hạ SFX hoặc nhạc ở các điểm ấy rồi dựng lại. Không để loudnorm tự nén.
- Đích −16,1, vì AAC làm lệch khoảng +0,1; file giao sẽ đo ra −16,0. TP đặt −2,5 để sau AAC vẫn ≤ −2 dBTP.
- Số của ca mẫu A: −16,0 LUFS, −3,5 dBTP, LRA 1,2 LU.
- Hình chép nguyên (`-c:v copy`), nên thẻ BT.709 vẫn còn. Âm mã hóa AAC 256k, 48 kHz.
- `--voice` là file giọng riêng (tùy chọn). Khi không đạt tuyến tính, công cụ in thêm đỉnh của giọng ở cùng cửa sổ, để biết đỉnh đến từ SFX, nhạc hay từ giọng. Video không giọng thì bỏ tham số này.
- Bản −14 LUFS để đăng mạng xã hội: chỉ làm khi Minh yêu cầu. Minh đã chốt bản này cho phim 3D; với video AE thì hỏi lại.

### 9.9 Lệnh âm (ca mẫu A)

```bash
cd "<thư mục dự án AE>"
python -X utf8 -I tools/am_thanh_cues.py "/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx" "/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/VOICE/<giong>.MP3"
#   tự chép SFX và giọng sang WAV 48 kHz, tính gain, sinh cue cho AE và bảng cue
python -I tools/ae.py build                                        # đưa cue mới vào project
ffmpeg -v info -i <mp4> -map 0:a -af ebur128=peak=true -f null -   # I, LRA, đỉnh thật
ffmpeg -y -i <mp4> -vn -ac 1 -ar 16000 giong16k.wav
PYTHONIOENCODING=utf-8 python "<SKILL>/scripts/transcribe.py" giong16k.wav whisper.json
```

Lệnh trích âm cho whisper dùng `-ac 1` cũng được, vì whisper không cần mức chuẩn.

### 9.10 Video không có giọng đọc (nhạc dẫn, thường gặp ở nhánh B)

- Không có chuẩn có nguồn cho số dB giữa nhạc và SFX (`<SKILL>\references\nghien-cuu-decibel.md` mục 3). Nhạc và các SFX chủ chốt cùng là lớp tiền cảnh.
- **Mức nhạc** (đề xuất, chưa đo trên ca thật nào): nhạc là lớp chính. Đặt nhạc khoảng −17 LUFS tích hợp trong bản trộn, để cả bản (nhạc + SFX) gần −16 trước master. Nhờ vậy master chỉ nâng hạ dưới 1–2 dB và trần đỉnh mỗi cue vẫn giữ được.
  - Đừng giữ −31 LUFS của video có giọng: master sẽ phải nâng khoảng 15 dB, đỉnh vượt trần và `master.py` dừng.
  - Trong `am_thanh_cues.py`, đổi hằng `MUSIC_LUFS` từ −31 sang khoảng −17.
- **So từng cú, không so cả bài:**
  - đo M (400 ms) của cue so với M của nhạc ngay tại chỗ, hoặc RMS trong dải tần của tiếng;
  - cột "Nhô" mà `am_thanh_cues.py` ghi vào bảng cue chính là số này;
  - tiếng giao diện nhỏ nhô 0–4 LU;
  - tiếng chủ chốt (mở màn, chốt đơn, logo, CTA) nhô +4 … +10 LU, tốt nhất đặt vào chỗ nhạc lặng hoặc cú đáp;
  - vẫn giữ trần đỉnh thật −12 dBTP mỗi cue (master nâng thêm X dB thì trần trước master là −12 − X).
- Không có lời đọc lo phần chữ, nên chữ chính vào có thể gắn tiếng nhẹ (tick, swish nhỏ) cho nhịp rõ. Mục song song dùng cùng âm. Có giọng thì thường bỏ.
- Số đặt của ca mẫu B (chưa đo trên bản xuất; dùng làm điểm xuất phát rồi đo):
  - file SFX hạ −4,5 dB trước (`volume=-4.5dB`), lọc `lowpass=f=11000`;
  - gain layer theo nhóm:

| Nhóm chuyển động | Ví dụ âm (uisfx-themes) | Gain layer |
|---|---|---|
| Điểm nhấn mở màn, chốt đơn, CTA | `cinematic/wake`, `glass/checkout`, `cinematic/complete` | −6 … −6,5 dB |
| Chuyển cảnh máy quay, nút bấm chính | `cinematic/expand`, `glass/send`, `studio/press`, `glass/toggle-on` | −7 … −7,5 dB |
| Thẻ trượt, tiêu đề, cảnh báo nhẹ | `studio/swipe`, `soft/warning`, `studio/connect` | −8 … −8,5 dB |
| Chuyển động nhỏ, avatar, gõ phím, quét AI | `studio/focus`, `minimal/progress-step`, `studio/typing`, `studio/scanning` | −9 … −9,5 dB |

  - nhạc trong `Music_Holder`: gain −8 dB.
- Gain layer chỉ có nghĩa khi biết file to bao nhiêu. Đổi bộ âm hay đổi nhạc thì đo lại, không chép số.
- Master như mục 9.8.

## 10. Render và xuất file

### 10.1 MP4

```bash
"<AE>\aerender.exe" -project <aep> -comp <COMP> -s 0 -e 1079 -RStemplate "Best Settings" -OMtemplate "H.264 - Match Render Settings - 40 Mbps" -output <mp4>
```

- `tools/ae.py render` gọi đúng lệnh này, ghi log `.aerender.log` và báo các dòng ERROR.
- aerender luôn mở engine riêng, không đụng phiên của Minh. Không dùng `-reuse`.
- Ca mẫu A: video 36 s, 1080p, 30 fps render khoảng 55 s.
- Render một project khác (nhánh B, bản sao template): thêm `--project`, ví dụ
  `python -I tools/ae.py render --project "<bản sao>.aep" --comp "Full_HD (1920 x 1080)" --start 0 --end <khung cuối> --out out/review/_lam/b01.mp4`.
  - Giao 1080p thì render comp Full HD của template; giao 4K thì render comp 4K.
  - Giữ fps của template. Đổi fps của template làm lệch mọi mốc thời gian đã dựng.

### 10.2 Gắn thẻ màu

H.264 xuất bằng template "Match Render Settings" được mã hóa theo BT.709 dải TV, nhưng không gắn thẻ. Máy phát vì vậy đoán sai màu. Gắn thẻ mà không mã hóa lại:

```bash
ffmpeg -y -i bNN.mp4 -c copy -bsf:v h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0 bNN_709.mp4
```

Khi đo màu phải giải mã theo bt709: #0068FF ra (0,104,255). Lệch ≤ 3 mức là do mã hóa.

### 10.3 Ảnh tĩnh

- `tools/ae.py stills`: dùng aerender với `-OMtemplate "TIFF Sequence with Alpha"` cho từng khung, rồi ffmpeg đổi ra PNG.
- aerender không ghi được chuỗi ảnh vào đường dẫn có dấu cách (đo 26/10, lỗi "Directory does not exist" với "Minh\ PC"). `ae.py` bản trong skill render TIFF vào thư mục tạm không dấu cách (`%PUBLIC%`), rồi mới đổi ra PNG ở thư mục đích.
- `comp.saveFrameToPng` không ghi được ảnh trong lần thử 21/10. Đừng dùng làm bằng chứng.
- RenderQueue trong script có thể trả `ERR_STOPPED` dù đã ghi TIFF. Mở file ra kiểm.
- Cách khác: trích khung từ MP4 bằng ffmpeg.
  - Tờ khung 1 khung mỗi giây: `tools/to_contact.py` (có trong `<KHUNG>` và `<VD-A>`).
  - Tờ khung đã hiện đủ: `<VD-A>\tools\to_khung.py`.

### 10.4 So hai bản

- Âm: `ffmpeg -v error -i a.mp4 -map 0:a -f md5 -`. Muốn biết khác ở đâu: giải mã hai bản ra f32, trừ cho nhau, gom vùng lệch theo cửa sổ 10 ms.
- Hình: `ffmpeg -i a.mp4 -i b.mp4 -lavfi "[0:v][1:v]psnr=stats_file=psnr.log" -f null -`. Vài khung có PSNR ≥ 78 dB là nhiễu mã hóa, hình không đổi.
- Dùng để chứng minh lần sửa chỉ đổi đúng chỗ cần đổi.

### 10.5 Bản nghe thử nhẹ

```bash
ffmpeg -y -i ban_giao.mp4 -vf scale=1280:720:flags=lanczos -c:v libx264 -preset slow -crf 28 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -c:a copy -movflags +faststart ban_nghe-thu-720p.mp4
```

`-c:a copy` giữ âm trùng từng byte với bản giao. Video 36 s ra khoảng 3 MB.

## 11. Thang kiểm trước khi giao

| Nấc | Kiểm | Lệnh, cách làm | Đạt khi |
|---|---|---|---|
| 1 | Dựng | `tools/ae.py build` (nhánh B: báo cáo của script sửa template) | 0 lỗi dựng, 0 lỗi expression, không có font thay thế |
| 2 | Khung đã hiện đủ | ảnh mỗi cảnh lúc chữ và hình đã vào đủ | xem bằng mắt: không đè, không tràn, đúng màu |
| 3 | Tờ khung, điểm nối | tờ 1 khung/giây; dải 5 khung quanh mọi điểm nối và cú chạm | không cắt cứng, không mất vật, không giật |
| 4 | Chữ | `tools/qa_chu.py` | đúng luật chữ mục 6.5; mục song song cùng kiểu |
| 5 | Màu | giải mã bt709, lấy mẫu nền và các khối | đúng bảng màu, lệch ≤ 3 mức |
| 6 | Chuyển động | `<SKILL>/scripts/v2w/metrics.py --no-flow` | Tĩnh B ≤ 15 % mỗi ô 2 s, Tĩnh A 0, 0 cắt cứng |
| 7 | Âm | ebur128; lệch đỉnh SFX so với khung; có giọng: nhạc dưới giọng, che phụ âm 2–8 kHz, whisper; không giọng: cột "Nhô" của từng cue so với nhạc | đúng mức mục 9; đỉnh SFX trễ ≤ 1 khung, không sớm |
| 8 | Rà chéo | agent mới: Q (hình, chữ) và Q5 (âm). Chỉ đưa file và số đo, không đưa kết luận tự kiểm | không còn "Cần sửa"; "Nên sửa" đã sửa hoặc ghi lý do để ngỏ |
| 9 | File giao | master; ffprobe; đo lại I, TP trên file giao; bản nghe thử 720p | −16,0 LUFS, ≤ −2 dBTP, h264 gắn thẻ bt709, đúng độ dài |

- Chỉ báo "xong" sau khi đã mở hoặc giải mã file ra và xem. Không suy từ việc lệnh đã chạy xong.
- Nấc nào không làm được thì ghi "chưa kiểm". Còn lỗi "Cần sửa" hoặc nấc "chưa kiểm" thì giao dưới tên **bản nháp**.
- Ở ca mẫu A, rà chéo âm bắt được 2 tiếng chip đè phụ âm mà tự kiểm, kể cả whisper, đã bỏ sót. Đừng bỏ nấc 8.
- Agent chỉ đo, không nghe được bằng tai. Ghi rõ điều đó và nhờ Minh nghe.
- Nhánh B: script sửa template phải xuất `textDump` vào báo cáo (chép hàm `dumpTexts` trong `<KHUNG>\build\main.jsx`), thì nấc 4 mới chạy được `qa_chu.py`.

### 11.1 Rà chéo: Q và Q5

- Mỗi agent rà là một agent mới, chưa đọc gì của dự án. Không đưa kết luận tự kiểm cho agent đó, để nó nhìn bằng mắt mới.
- Đầu vào: MP4 giao, tờ khung 1 giây, dải khung ở các điểm nối, bảng số đo, brief và kịch bản (`KHUNG-DUNG.md`). Q5 cần thêm bảng cue và file giọng riêng nếu có.
- Yêu cầu trả về:
  - danh sách lỗi, mỗi lỗi có giây hoặc khung, xếp ba mức "Cần sửa", "Nên sửa", "Ghi nhận";
  - điểm từng mặt. Q chấm chuyển động, chữ, thương hiệu, kể chuyện. Q5 chấm rõ lời, cân mức, đồng bộ, an toàn đỉnh.
- Sửa xong thì gửi lại đúng agent đó cho vòng 2: soát lại từng lỗi đã nêu và tìm lỗi mới.

## 12. Học từ template AE có sẵn

### 12.1 Xem trước khi có file (Envato)

Trang mẫu `app.envato.com/.../video-templates/<id>` không cần đăng nhập.
- Tab "Inside the file" → bấm "Expand all": hiện cây project thật (thư mục, tên comp, asset; tối đa 20 mục mỗi thư mục). Đọc bằng `document.body.innerText`.
- Video hướng dẫn thường quay màn hình AE. Cắt cận khung thì đọc được Effect Controls và lớp điều khiển.
- Lấy khung hình preview:
  1. tạo một `<video>` mới cùng `src`;
  2. seek tới thời điểm cần;
  3. chờ `requestVideoFrameCallback`;
  4. `drawImage` lên canvas rồi chụp màn hình.
- File .aep thì Minh phải tự tải bằng tài khoản của Minh.

### 12.2 Khi đã có .aep

- Mở **bản sao** trong phiên riêng, chỉ đọc, không lưu.
- Script trích nằm ở `<SKILL>\references\template-audit\scripts\`. Sửa đường dẫn cứng `/media/vmiz/Over Powers/video AE/...` trước khi chạy.
  - `export-projects.jsx`: cả cây comp, layer, thuộc tính, key, ease, tangent, expression → JSON.
  - `sample-and-render.jsx`: tìm font thiếu; lấy mẫu `valueAtTime` mỗi 0,25 khung.
  - `render-frames.jsx`: render vài khung TIFF để xem.
  - `property-units.jsx`: đối chiếu số thô với số trên giao diện.
- Kết quả của lần trích 21/10, nằm ở `<SKILL>\references\template-audit\`:
  - `BAO-CAO-PHAN-TICH.md`: đọc trước;
  - `MOTION-PRESETS.json`: 10 công thức;
  - `BANG-TEXT-VA-KEYFRAME.md`;
  - prompt giao việc: `PROMPT-HOAN-CHINH-OPUS.md`.
- Ca mẫu B tính giây toàn cục của mọi cảnh, comp con bằng `<VD-B>\parse_aep_timings.py`.
  - Script này đọc một báo cáo dạng chữ phân tab (`COMP`, `LAYER`, `TEXT_VAL`…), không đọc JSON của `export-projects.jsx`. Hai bước chưa nối được với nhau.
  - Có JSON của `export-projects.jsx` thì tự cộng `startTime` các tầng theo mục 4.3. Muốn dùng `parse_aep_timings.py` thì phải ghi báo cáo đúng dạng chữ đó.
  - Trong phiên riêng, cứ ghi báo cáo thẳng ra file. Không cần mẹo giấu báo cáo vào file .aepx.

### 12.3 Bẫy khi đọc template

- Font thiếu: Manrope bị thay bằng Times trong lần trích 21/10. Ảnh render khi ấy không đại diện cho font gốc.
- Expression lỗi có sẵn trong template (Bevel Angle gọi `Angle Glow` không tồn tại). Đừng chép.
- Tên comp trùng giữa hai nhánh template. Nhận diện bằng ID kèm chuỗi sử dụng.
- Key là khung cục bộ: phải cộng offset của các tầng (mục 4.3).
- Số thô khác số trên giao diện (mục 7.6). Style đang tắt vẫn đọc được giá trị.
- Pixel của template theo khổ gốc (ví dụ 2160×3840). Đổi khổ thì nhân q = bề rộng mới / bề rộng gốc cho các đại lượng pixel, giữ nguyên % và góc. Hoặc đổi theo em như ca mẫu A.
- Music comp của template có thể rỗng.

## 13. Nhánh B: sửa template mua về

Các bước. Ca mẫu: `<VD-B>` (đọc `README.md` trong đó trước):
1. **Kịch bản và brief:** chốt chữ, CTA, logo, ảnh, nhạc, khổ (G0). Template 4K (3840×2160) thì cỡ chữ nhỏ nhất 56 px.
2. **Đọc cấu trúc template** (mục 12.2, 4.5):
   - lập bảng cảnh: giây vào ra toàn cục của mỗi cảnh và comp con (mục 4.3);
   - lập danh sách comp giữ chỗ, layer chữ, layer màu điều khiển.
3. **Chuẩn bị tài nguyên:**
   - chân dung, logo, thẻ giao diện, avatar: đúng kích thước comp giữ chỗ (ví dụ logo 1000×1000);
   - thay footage vào comp giữ chỗ thì kéo dài thời lượng của comp giữ chỗ lẫn comp bao ngoài cho đủ cảnh, để hình không tắt sớm;
   - avatar khung chat: giữ layer Background của template, đặt avatar mới lên trên cùng (`moveToBeginning()`).
4. **Sửa bằng script, trên bản sao, trong phiên riêng:**
   - thay chữ theo mục 6.6;
   - đổi màu ở các layer điều khiển (mục 4.5), rồi tìm màu gán cứng còn sót;
   - không để `catch` rỗng; mọi lỗi ghi ra báo cáo.
5. **Âm** (mục 9.3, 9.4, 9.10): chọn bộ âm theo gu, căn đỉnh theo giây toàn cục, chống phát đúp, đo, rồi master.
6. **Render, thang kiểm, bàn giao** (mục 10, 11, 14).

Luật thương hiệu vẫn áp: video OPA theo BRAND-SPEC (5 màu, phẳng, mascot không mắt), dù template gốc có glow, kính, 3D. Mặc định làm phẳng; muốn giữ hiệu ứng của template trái BRAND-SPEC thì Minh quyết ở G0.

**Công cụ nhánh B còn thiếu trong gói** (chưa làm vì chưa thử được trên AE):
- Chưa có lệnh chạy một JSX lên bản sao template. `tools/ae.py build` luôn chép seed trống đè lên file đích, nên không dùng cho nhánh B.
- Cách làm tạm:
  1. viết JSX tự mở bản sao (`app.open(new File(...))`), sửa, `save()`, rồi ghi báo cáo JSON;
  2. chạy bằng loader như mục 3.2, đổi đường dẫn bundle thành file JSX đó;
  3. lần đầu chạy, đọc báo cáo và mở bản sao ra xem trước khi làm tiếp.
- Render, xuất khung của bản sao: `tools/ae.py render` hoặc `stills` với `--project` (mục 10.1).
- Bốn script của `<VD-B>` có nhiều chỗ làm trái luật của skill. Đọc mục "Chỗ làm trái luật" trong `README.md` của nó trước khi dùng.

## 14. Bàn giao và cách sửa

**Giao những gì:**
- project `.aep` cùng thư mục assets;
- script dựng lại hoặc script sửa template (`build/`, `tools/`);
- MP4 giao đã master và gắn thẻ bt709;
- bản nghe thử 720p;
- ảnh khung đã hiện đủ và tờ khung 1 giây;
- `KHUNG-DUNG.md`: brief đã chốt, giả định, phương án chuyển động, công thức, bảng theo cảnh, bảng mốc chữ, bảng SFX, cấu trúc project, cách sửa, kết quả từng nấc kiểm. Mẫu: `<VD-A>\KHUNG-DUNG.md`;
- bảng cue âm: cue, mức, lý do, nguồn research. Mẫu: `<VD-A>\audio\BANG-CUE-AM-THANH.md`.

**Cách sửa (ghi lại cho Minh), ví dụ nhánh A:**
- Đổi chữ: `03_EDIT_CHU` → comp `TXT_…` → layer `TEXT`.
- Đổi màu: `CONTROL` → `BRAND` → Color Control.
- Đổi giọng: chạy lại `am_thanh_cues.py` với file giọng mới, rồi dựng lại.
- Đổi âm: sửa `cues()` trong `am_thanh_cues.py`, chạy lại, dựng lại.
- Dựng lại từ đầu: `python -I tools/ae.py build`.
- Ghi rõ font cần cài. Không dùng plugin ngoài, chỉ effect gốc của AE.

**Báo cáo:** đã kiểm gì; tự kiểm hay rà chéo bằng agent; chưa kiểm gì; điểm chờ duyệt.
- Video OPA: Minh duyệt lời; Hùng duyệt hình trước khi đăng (BRAND-SPEC mục 7).
- Video làm cho khách khác: Minh quyết ai duyệt.

## 15. Nhánh A: bắt đầu dự án mới

1. Chép `<KHUNG>` thành `<dự án>\ae\<tên>\`. Bộ khung đã thử ngày 26/10 trên AE 2026: dựng, xuất khung, soát chữ đều đạt.
2. Sửa:

| File | Sửa gì |
|---|---|
| `build\lib.jsx` | `O.COLORS`, `O.FONT` (mặc định OPA); `O.W`, `O.H`, `O.FPS` nếu khác 1920×1080, 30 fps. Giữ `O.EASE`, `O.anim`, `O.textAnim`. `O.makeControl` ghi cứng 6 tên màu (`blue`, `blueDark`, `blueLight`, `black`, `white`, `alert`): giữ nguyên 6 tên và chỉ đổi giá trị RGB; thêm tên mới thì thêm cả vào danh sách trong `O.makeControl` |
| `build\main.jsx` | thời lượng master, danh sách cảnh `plan` |
| `build\scenes\*.jsx` | viết các cảnh `OPA.buildSx`; xóa cảnh mẫu `s1_mau.jsx` |
| `tools\qa_chu.py` | bộ font được duyệt |
| `tools\ae.py` | `AE_DIR` nếu AE cài chỗ khác |

3. Thêm âm: chép từ `<VD-A>` các file `build\scenes\am_thanh.jsx`, `tools\am_thanh_cues.py`, `tools\phan_tich_sfx.py`. Rồi sửa đủ các chỗ sau, vì chúng ghi cứng cho ca OPA Agent 36 s:

| Chỗ | Sửa gì |
|---|---|
| `build\main.jsx` của bộ khung | thêm đoạn gắn comp âm vào master và đoạn giọng đọc. Chép từ `<VD-A>\build\main.jsx`: khối `if (O.buildAudio && A.sfx)` và khối `if (O.VOICE && A.sfx)` |
| `build\scenes\am_thanh.jsx` | thời lượng comp âm đang là 1080 khung (36 s): đổi bằng thời lượng master |
| `am_thanh_cues.py`: `MUSIC` | đường dẫn file nhạc. Nhạc phải là WAV 48 kHz sẵn trong `assets\music\`, vì script không tự đổi nhạc (mục 9.6) |
| `am_thanh_cues.py`: `MUSIC_LUFS` | −31 khi có giọng; khoảng −17 khi không giọng (mục 9.10) |
| `am_thanh_cues.py`: `SND`, `SHIFT`, `cues()` | bộ âm, độ dịch cao độ, danh sách cue của video mới |
| `am_thanh_cues.py`: `OPA_KIT` | logo âm thanh OPA; video khác bỏ hoặc thay |
| `am_thanh_cues.py`: `write_md`, `LEVELS` | tiêu đề 5 cảnh và chú thích của ca OPA: viết lại theo video mới |
4. Đi qua các cổng:
   1. brief: hỏi gộp một lần;
   2. đoạn mẫu 3–5 s và khung đã hiện đủ, để Minh duyệt gu;
   3. dựng đủ, tự kiểm;
   4. âm, Minh nghe;
   5. lồng giọng, master;
   6. rà chéo;
   7. giao.

Ca mẫu A đã đi: v07 (mẫu gu) → v08 (đủ 5 cảnh, Minh duyệt) → v09 (SFX và nhạc, Minh duyệt âm) → v10 (giọng đọc và URL).

## 16. Lỗi hay gặp

| Dấu hiệu | Làm đúng |
|---|---|
| Gửi script vào AE bằng `-r`, đổi tiến trình cha để chui vào phiên đang mở, hoặc điều khiển AE bằng chuột | `AfterFX.exe -noui -m -s "<loader>"` trong phiên riêng |
| `-m -r file.jsx` tự thoát sau khoảng 6 s; `$.evalFile` không chạy | loader `File.read()` rồi `eval` |
| `app.project.save(new File())` trả false | chép seed trống (hoặc bản sao template) → open → save() |
| Script lưu đè lên template gốc | làm trên bản sao |
| `openInViewer()` trong phiên headless | bỏ; hàm này cần giao diện |
| `catch (err) {}` rỗng | ghi lỗi vào báo cáo |
| Nền "LINEAR" vẫn chậm dần ở hai đầu | đặt kiểu nội suy SAU `setTemporalEaseAtKey` |
| Dùng Easy Ease 33 % cho mọi thứ | preset theo vai trò (mục 5.2) |
| Mỗi từ một animator; key Opacity cho cả layer | một animator, Based On = Từ, Start 0→100 |
| Đổi chữ trong template làm gãy expression | giữ `layer.name` (mục 6.6) |
| Câu tiếng Việt dài, chữ cuối không hiện | Max Ease = 0, đặt lại Start 0→100 (mục 6.6) |
| Shape đứng đầu mảng lại nằm trên cùng | thêm nhóm theo thứ tự ngược |
| Layer con không mờ theo cha | expression theo opacity của cha |
| Squash & stretch, mắt, màu ngoài bảng cho Bò OPA | BRAND-SPEC: chỉ co giãn đều, không mắt, 5 màu (mục 7.8) |
| Chữ ra Times hoặc sai dáng | kiểm `isSubstitute`; AddFontResourceW + WM_FONTCHANGE; mở phiên mới |
| Màu MP4 lệch | gắn thẻ BT.709 bằng `h264_metadata` |
| `ae.py stills` báo "Directory does not exist" | đường dẫn có dấu cách; dùng `ae.py` bản trong skill (render qua thư mục tạm) |
| Nhạc to hơn đích 3 LU | file mono: đo bằng cách nhân đôi kênh, không dùng `-ac 2` |
| SFX lệch giờ | MP3 → WAV 48 kHz; căn ĐỈNH: `startTime = t − peak_s` |
| Đặt cứng gain −5 … −10 dB mà không đo | gain = M đích − M đo; số của ca mẫu B chỉ là điểm xuất phát (mục 9.10) |
| Mỗi tiếng SFX phát hai lần, to thêm 6 dB | tắt `audioEnabled` của layer cảnh trong comp tổng (mục 9.4) |
| Bản trộn vượt −2 dBTP | trần −12 dBTP mỗi cue, kiểm âm chồng; master tuyến tính |
| SFX đè phụ âm mà whisper vẫn báo ổn | đo dải 2–8 kHz trên cả cửa sổ cue |
| Âm có nốt lạc giọng nhạc | đo cao độ, dịch theo cent |
| Hai âm giống nhau cách dưới 3 khung | dời hoặc bỏ một âm |
| Báo "render xong" khi chưa mở file | giải mã, xem khung, đo âm rồi mới báo |
| Hộp "Crash Repair Options" sau khi buộc tắt | gửi Enter vào đúng cửa sổ của phiên mình |
| Lệnh `ffmpeg` không ghi file mà vẫn trả mã 0 | luôn thêm `-y` |
| Python in tiếng Việt bị lỗi | `python -X utf8` hoặc `PYTHONIOENCODING=utf-8` |
| Lệnh hỏng mà `\| tail` vẫn báo exit 0 | đọc kết quả thật |
| Template ghi opacity bóng 76,5 | đó là số thô thang 0–255, bằng 30 % trên giao diện |
| Template do bản AE cũ lưu, phiên headless không lưu được | nhờ Minh mở bằng AE 2026 và Save As một lần (mục 3.3) |
| Sửa Range Selector của template xong thì mất pha ra | chỉ đặt lại key pha vào, giữ pha ra, đặt ease theo vai trò (mục 6.6) |
| Tắt âm layer cảnh để chống phát đúp, nhạc cũng tắt theo | mỗi tiếng chỉ đặt ở một nơi; nhạc nằm ngoài comp cảnh (mục 9.4) |
| Video không giọng mà giữ nhạc −31 LUFS | nhạc khoảng −17 LUFS; đổi `MUSIC_LUFS` (mục 9.10) |
| Đổi fps của template | giữ fps của template |

## 17. Cấu hình máy, cài skill, phụ thuộc

**Đường dẫn theo máy của Minh** (máy khác thì đổi):

| Thứ | Đường dẫn | Ở đâu trong code |
|---|---|---|
| After Effects 2026 | `C:\Program Files\Adobe\Adobe After Effects 2026\Support Files` | `AE_DIR` trong `tools/ae.py` |
| Kho SFX | `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx` | tham số đầu của `am_thanh_cues.py` |
| Giọng đọc Minh gửi | `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/VOICE` | tham số thứ hai của `am_thanh_cues.py` |
| Dự án OPA sống | `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/OPA-Motion-graphic-mascot` | BRAND-SPEC, nhạc tự tổng hợp |
| Template nhánh B | `/media/vmiz/Over Powers/video AE/template intro/video edit teamplate` | đầu các script `<VD-B>` |

**Phụ thuộc:** Python 3.12 + numpy, scipy; ffmpeg, ffprobe trong PATH; After Effects 2026. Whisper cần thêm `faster-whisper` và model large-v3 tải sẵn. Thiếu thư viện thì hỏi Minh trước khi cài.

**Cài skill:**
- Claude Code: chép thư mục `after-effects` vào `C:\Users\<tên>\.claude\skills\`. Trên máy Minh, thư mục đó là junction trỏ về bản gốc `/media/vmiz/Over Powers/THÀNH V/Skill/after-effects`.
- Agent đọc `.agents\skills` (Codex, Gemini CLI, Antigravity…): chép thư mục vào `.agents\skills\` của agent đó, hoặc vào `C:\Users\<tên>\.agents\skills\`.
- claude.ai: tải file `after-effects.zip` lên mục Skills.
- Cập nhật: sửa bản gốc ở `/media/vmiz/Over Powers/THÀNH V/Skill/after-effects`. Bản chép ở chỗ khác (hiện có `/media/vmiz/Over Powers/THÀNH V/Motion Omi/.agents/skills/after-effects`) phải chép lại, rồi đóng lại file zip.

## 18. Nguồn

**Trong gói skill:**
- Ca mẫu A: `<VD-A>\KHUNG-DUNG.md`, `<VD-A>\audio\BANG-CUE-AM-THANH.md`, `<VD-A>\build\*`, `<VD-A>\tools\*.py`.
- Ca mẫu B: `<VD-B>\*`.
- Phân tích template: `<SKILL>\references\template-audit\` (`BAO-CAO-PHAN-TICH.md`, `MOTION-PRESETS.json`, `PROMPT-HOAN-CHINH-OPUS.md`, `BANG-TEXT-VA-KEYFRAME.md`, `scripts\*.jsx`).
- Thiết kế UI từ phác thảo (Sketch-to-UI) & Nhân vật 2D–3D tách lớp: `<SKILL>\references\sketch-to-ui-va-nhan-vat.md`.
- Âm: `<SKILL>\references\nghien-cuu-decibel.md`; `<SKILL>\scripts\master.py`, `transcribe.py`, `cao_do.py`; số đo kho SFX `<SKILL>\data\kho_sfx_do.csv`.
- Đo chuyển động: `<SKILL>\scripts\v2w\` (`metrics.py`, `metrics_core.py`, `scan_video.py`, `contact.py`).

**Trên máy Minh:**
- Luật: `<OPA>\BRAND-SPEC.md`; `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/AI Video/EDITORIAL_RULES.md`; skill `master-video-edit`.
- Dữ liệu trích template đầy đủ (khoảng 200 MB): `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/research/ae-text-audit-2026-10-21`.
- Motion Omi (UI, nhân vật, prompt Omni Flash): `/media/vmiz/Over Powers/THÀNH V/Motion Omi`.
- Nhạc tự tổng hợp của OPA: `<OPA>\tools\audio\score_agent.py`. Không có trong gói, vì cần bộ nhạc cụ của dự án OPA.

**Web:**
- Adobe, Scripts in After Effects: https://helpx.adobe.com/after-effects/using/scripts.html
- After Effects Scripting Guide (property, keyframe, ease): https://ae-scripting.docsforadobe.dev/
- Fonts object: https://ae-scripting.docsforadobe.dev/text/fontsobject/
- EBU R 128 s1: https://tech.ebu.ch/docs/r/r128s1.pdf

<!-- ===== /file: ae-script-builder/references/SO-TAY-AFTER-EFFECTS.md ===== -->

<!-- ===== file: ae-script-builder/references/TONG-HOP-SKILL-AFTER-EFFECTS.md ===== -->

# Hồ Sơ Tổng Hợp & Đóng Gói Skill Duy Nhất: `after-effects`

- **Tên gọi chính thức của Skill:** `after-effects`
- **Đường dẫn lưu trữ gốc (Master Source):** `/media/vmiz/Over Powers/THÀNH V/Skill/after-effects`
- **File đóng gói đầu ra (Archive):** `/media/vmiz/Over Powers/THÀNH V/Skill/after-effects.zip` (và bản sao tại `/media/vmiz/Over Powers/THÀNH V/Skill/after-effects/after-effects.zip`)
- **Ngày hoàn tất hợp nhất:** 27/10/2026

---

## 1. Kết quả kiểm tra đối chiếu: Bản cài hiện tại và Bản cài trước có trùng nhau không?

Qua rà soát toàn bộ các thư mục trong `/media/vmiz/Over Powers/THÀNH V/Skill/`, `/media/vmiz/Over Powers/THÀNH V/Skill/_ban-cu/` và `/media/vmiz/Over Powers/THÀNH V/Motion Omi/.agents/skills/`, kết quả cụ thể như sau:

| Thành phần kiểm tra | Trạng thái trước khi gộp | Kết quả xử lý hợp nhất |
|---|---|---|
| **1. `after-effects` (v1/v2) vs `after-effects` (v3 hiện tại)** | **Trùng lặp ~90% nội dung cốt lõi**: 16 mục gốc của `SO-TAY-AFTER-EFFECTS.md` và 2 mục mới (Research/Sửa template `.aep` + Gắn High-Tech SFX `-6.0` đến `-9.5 dB`) đã được biên tập gộp vào mục `4.5`, `6.6`, `7.8`, `7.9`, `9.3`, `9.4`, `9.10`, `12.2`, `13` của bản v3. | Giữ **1 bản chính duy nhất** tại `/media/vmiz/Over Powers/THÀNH V/Skill/after-effects`. Bản v2 trước lúc gộp đã được lưu trữ an toàn trong `/media/vmiz/Over Powers/THÀNH V/Skill/_ban-cu/2026-10-26_truoc-gop/`. |
| **2. `ae-template-motion-sfx` vs `after-effects`** | **Trùng 100% chức năng với Nhánh B của `after-effects`**: 4 script (`parse_aep_timings.py`, `customize_template_assets.jsx`, `prepare_sfx_pro.py`, `generate_ae_sfx_jsx.py`) và quy trình 4 bước đều đã nằm trong `after-effects\examples\template-5\` và Mục 13 của sổ tay. | Đã **hợp nhất hoàn toàn vào `after-effects`**, xóa bỏ Junction trùng `ae-template-motion-sfx` trong `.gemini\config\skills\` và cất bản cũ vào `/media/vmiz/Over Powers/THÀNH V/Skill/_ban-cu/`. |
| **3. `sketch-to-mobile-ui` vs `after-effects`** | **Trùng một phần (Mục 7.8 & 7.9)** nhưng phần chi tiết Prompt 7 phần, bảng màu 5 ngành hàng, lệnh xuất SVG tách lớp `<g id="...">` và bảng `CS01..CS05` vẫn đang nằm rời ở thư mục `/media/vmiz/Over Powers/THÀNH V/Skill/sketch-to-mobile-ui`. | Đã **gộp toàn bộ nội dung chi tiết** vào thẳng `/media/vmiz/Over Powers/THÀNH V/Skill/after-effects/references/sketch-to-ui-va-nhan-vat.md` và cất thư mục rời `sketch-to-mobile-ui` vào `/media/vmiz/Over Powers/THÀNH V/Skill/_ban-cu/`. |

---

## 2. Cấu trúc Tất Cả Trong Một (All-in-One) của Skill `after-effects`

Toàn bộ kiến thức, bộ khung dựng mới (Nhánh A), bộ công cụ sửa template `.aep` có sẵn (Nhánh B), thiết kế nhân vật 2D–3D & UI từ phác thảo, cùng kho số đo 2.982 file SFX đều nằm gọn trong **một thư mục duy nhất** `/media/vmiz/Over Powers/THÀNH V/Skill/after-effects`:

```text
/media/vmiz/Over Powers/THÀNH V/Skill/after-effects/
├─ SKILL.md                              # Lối vào chính thức của skill "after-effects"
├─ SO-TAY-AFTER-EFFECTS.md               # Sổ tay đầy đủ 18 mục (Nhánh A + Nhánh B + Âm thanh + QA)
├─ TONG-HOP-SKILL-AFTER-EFFECTS.md       # File báo cáo tổng hợp & hướng dẫn đầu ra (file này)
├─ after-effects.zip                     # Gói nén đầu ra hoàn chỉnh để mang sang máy/agent khác
│
├─ templates\du-an-ae\                   # [Nhánh A] Bộ khung dự án mới (đã test trên AE 2026)
│  ├─ README.md
│  ├─ build\lib.jsx, main.jsx, scenes\s1_mau.jsx
│  └─ tools\ae.py, qa_chu.py, to_contact.py, seed\empty-ae26.aep
│
├─ examples\opa-agent\                   # [Ca mẫu Nhánh A] Dựng mới hoàn toàn từ code (36s, 5 cảnh)
│  ├─ KHUNG-DUNG.md, README.md
│  ├─ audio\BANG-CUE-AM-THANH.md
│  ├─ assets\fonts\FrauncesOPA-ExtraBoldItalic.ttf
│  ├─ build\lib.jsx, main.jsx, data\*, scenes\*
│  └─ tools\ae.py, am_thanh_cues.py, bang_khung.py, phan_tich_sfx.py, qa_chu.py, svg_to_ae.py...
│
├─ examples\template-5\                  # [Ca mẫu Nhánh B] Research & sửa template .aep 13 cảnh + SFX
│  ├─ README.md                          # Lưu ý bắt buộc trước khi tái sử dụng cho dự án khác
│  ├─ parse_aep_timings.py               # Giải mã thời gian toàn cục (Global IN/OUT & Frame)
│  ├─ customize_template_assets.jsx      # Thay nhân vật 2D/3D, chân dung, logo, UI, chữ Việt & Range Selector
│  ├─ prepare_sfx_pro.py                 # Chọn High-Tech SFX (uisfx-themes), lọc 11kHz, căn đỉnh peak_s
│  └─ generate_ae_sfx_jsx.py             # Sinh JSX gắn SFX (-6.0..-9.5 dB) vào 00_OPA_SFX_Master & 13 cảnh
│
├─ scripts\                              # Bộ công cụ Python dùng chung cho cả 2 nhánh
│  ├─ master.py                          # Master âm tuyến tính chuẩn BS.1770 (-16.0 LUFS, <= -2 dBTP)
│  ├─ transcribe.py                      # Chạy faster-whisper kiểm độ rõ lời & căn mốc thoại
│  ├─ cao_do.py                          # Đo cao độ (pitch/note) của SFX để dịch cent khớp giọng nhạc
│  └─ v2w\metrics.py, metrics_core.py, scan_video.py, contact.py
│
├─ data\
│  └─ kho_sfx_do.csv                     # Bảng đo kiểm định lượng 2.982 file SFX (dur, peak_s, tp_dbtp, m_max, centroid)
│
└─ references\                           # Tài liệu nghiên cứu & quy chuẩn tham chiếu
   ├─ nghien-cuu-decibel.md              # Nghiên cứu chuẩn âm lượng EBU R128 / ITU-R BS.1770-4
   ├─ sketch-to-ui-va-nhan-vat.md        # Quy trình Sketch-to-UI (Prompt 7 phần, SVG tách lớp) & Nhân vật CS01..CS05
   └─ template-audit\                    # Bộ phân tích preset chuyển động R1..R10 & script trích xuất .aep
      ├─ BAO-CAO-PHAN-TICH.md, BANG-TEXT-VA-KEYFRAME.md, MOTION-PRESETS.json, PROMPT-HOAN-CHINH-OPUS.md
      └─ scripts\export-projects.jsx, sample-and-render.jsx, render-frames.jsx, property-units.jsx...
```

---

## 3. Trạng thái Liên kết (Junction & Bản chép) trên Máy Minh

Tất cả các công cụ AI trên máy đều đã trỏ về đúng **1 skill duy nhất tên `after-effects`**:

1. **Bản gốc (Master):** `/media/vmiz/Over Powers/THÀNH V/Skill/after-effects`
2. **Claude Code Junction:** `C:\Users\Minh PC\.claude\skills\after-effects` $\rightarrow$ trỏ thẳng về `/media/vmiz/Over Powers/THÀNH V/Skill/after-effects`.
3. **Antigravity / Gemini Config Junction:** `C:\Users\Minh PC\.gemini\config\skills\after-effects` $\rightarrow$ trỏ thẳng về `/media/vmiz/Over Powers/THÀNH V/Skill/after-effects` (đã xóa junction thừa `ae-template-motion-sfx`).
4. **Workspace `Motion Omi`:** `/media/vmiz/Over Powers/THÀNH V/Motion Omi/.agents/skills/after-effects` (đã đồng bộ bản mới nhất).
5. **Thư mục lưu trữ bản cũ:** `/media/vmiz/Over Powers/THÀNH V/Skill/_ban-cu/` (giữ lịch sử các bản nháp trước khi gộp để không mất dữ liệu).

<!-- ===== /file: ae-script-builder/references/TONG-HOP-SKILL-AFTER-EFFECTS.md ===== -->

<!-- ===== file: ae-script-builder/references/template-audit/BANG-TEXT-VA-KEYFRAME.md ===== -->

# Bảng chữ và keyframe theo scene

Nguồn: `/media/vmiz/Over Powers/video AE/save/1.aep`, nhánh `Corporate Opener Mobile copy 23.x.aep`, master `!Corporate Opener` ID 3. Có 26 text layer nguồn đi vào master này; thư viện trong file có tổng 130 text layer vì nhập hai bộ template.

Frame trong các bảng dưới là frame cục bộ của comp chứa thuộc tính, bắt đầu từ 0. 30 fps. Để đổi sang master, đọc offset và chuỗi usage trong TEXT-RECIPES.json.

## Scene 1 / Text 1 / ID 141

Chữ: **Visual Graphics**

Font yêu cầu: `Manrope-Bold`, cỡ nguồn 300 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100 → f153: 100 → f183: 0.
- Đơn vị Range Selector: Từ.
- `/Text/Animators/Animator 1/Properties/Position`: [0, 300, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [128, 128].
- Chuỗi pre-comp: !Corporate Opener / layer 11 Scene 1 → Scene 1 / layer 11 Title 1 → Title 1 / layer 1 Text 1. Offset master: 27.000 frame; hệ số thời gian: 1.

## Scene 1 / Text 2 / ID 154

Chữ: **Motion Design**

Font yêu cầu: `Manrope-Regular`, cỡ nguồn 96 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100 → f125: 100 → f155: 0.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 1/Properties/Position`: [0, 64, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [64, 64].
- Chuỗi pre-comp: !Corporate Opener / layer 11 Scene 1 → Scene 1 / layer 7 Title 2 → Title 2 / layer 1 Text 2. Offset master: 55.000 frame; hệ số thời gian: 1.

## Scene 2 / Text 3 / ID 430

Chữ: **Minimalist**

Font yêu cầu: `Manrope-Bold`, cỡ nguồn 360 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100 → f152: 100 → f182: 0.
- Đơn vị Range Selector: Ký tự.
- `/Text/Animators/Animator 1/Properties/Position`: [0, 256, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [128, 128].
- Chuỗi pre-comp: !Corporate Opener / layer 10 Scene 2 → Scene 2 / layer 11 Title 3 → Title 3 / layer 1 Text 3. Offset master: 233.000 frame; hệ số thời gian: 1.

## Scene 3 / Text 2 / ID 605

Chữ: **Minimal Graphic**

Font yêu cầu: `Manrope-Regular`, cỡ nguồn 96 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100 → f110: 100 → f140: 0.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 1/Properties/Position`: [0, 64, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [64, 64].
- Chuỗi pre-comp: !Corporate Opener / layer 9 Scene 3 → Scene 3 / layer 2 Title 2 → Title 2 / layer 1 Text 2. Offset master: 471.000 frame; hệ số thời gian: 1.

## Scene 3 / Text 4 / ID 631

Chữ: **Brand Promo / By Tortoha**

Font yêu cầu: `Manrope-Bold`, cỡ nguồn 256 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 1/Properties/Position`: [0, -128, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [128, 128].
- `/Text/Animators/Animator 2/Selectors/Range Selector 1/End`: f172: 0 → f202: 100.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 2/Properties/Position`: [0, 128, 0].
- `/Text/Animators/Animator 2/Properties/Opacity`: 0.
- `/Text/Animators/Animator 2/Properties/Blur`: [128, 128].
- Chuỗi pre-comp: !Corporate Opener / layer 9 Scene 3 → Scene 3 / layer 7 Title 4 → Title 4 / layer 1 Text 4. Offset master: 416.000 frame; hệ số thời gian: 1.

## Scene 3 / Text 5 / ID 644

Chữ: **Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean / ultricies placerat velit, sed vulputate neque sollicitudin et.**

Font yêu cầu: `Manrope-Regular`, cỡ nguồn 64 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100 → f135: 100 → f165: 0.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 1/Properties/Position`: [128, 0, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [64, 64].
- Chuỗi pre-comp: !Corporate Opener / layer 9 Scene 3 → Scene 3 / layer 6 Title 5 → Title 5 / layer 1 Text 5. Offset master: 446.000 frame; hệ số thời gian: 1.

## Scene 4 / Text 2 / ID 914

Chữ: **Visual Design**

Font yêu cầu: `Manrope-Regular`, cỡ nguồn 96 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100 → f125: 100 → f155: 0.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 1/Properties/Position`: [0, 64, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [64, 64].
- Chuỗi pre-comp: !Corporate Opener / layer 8 Scene 4 → Scene 4 / layer 2 Title 2 → Title 2 / layer 1 Text 2. Offset master: 674.000 frame; hệ số thời gian: 1.

## Scene 4 / Text 4 / ID 940

Chữ: **Glow Design / Opener**

Font yêu cầu: `Manrope-Bold`, cỡ nguồn 256 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 1/Properties/Position`: [0, -128, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [128, 128].
- `/Text/Animators/Animator 2/Selectors/Range Selector 1/End`: f172: 0 → f202: 100.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 2/Properties/Position`: [0, 128, 0].
- `/Text/Animators/Animator 2/Properties/Opacity`: 0.
- `/Text/Animators/Animator 2/Properties/Blur`: [128, 128].
- Chuỗi pre-comp: !Corporate Opener / layer 8 Scene 4 → Scene 4 / layer 7 Title 4 → Title 4 / layer 1 Text 4. Offset master: 619.000 frame; hệ số thời gian: 1.

## Scene 4 / Text 5 / ID 953

Chữ: **Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut / tincidunt nisi sit amet vestibulum ornare. Aliquam porta / lacus pretium dapibus dapibus. Ut nibh sapien, viverra sed / quam a, venenatis dapibus nunc.**

Font yêu cầu: `Manrope-Regular`, cỡ nguồn 64 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100 → f135: 100 → f165: 0.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 1/Properties/Position`: [128, 0, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [64, 64].
- Chuỗi pre-comp: !Corporate Opener / layer 8 Scene 4 → Scene 4 / layer 6 Title 5 → Title 5 / layer 1 Text 5. Offset master: 649.000 frame; hệ số thời gian: 1.

## Scene 5 / Text 1 / ID 1200

Chữ: **Corporate Template**

Font yêu cầu: `Manrope-Bold`, cỡ nguồn 300 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100 → f154: 100 → f184: 0.
- Đơn vị Range Selector: Từ.
- `/Text/Animators/Animator 1/Properties/Position`: [0, 300, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [128, 128].
- Chuỗi pre-comp: !Corporate Opener / layer 7 Scene 5 → Scene 5 / layer 6 Title 1 → Title 1 / layer 1 Text 1. Offset master: 840.000 frame; hệ số thời gian: 1.

## Scene 5 / Text 3 / ID 1226

Chữ: **Graphic Design**

Font yêu cầu: `Manrope-Regular`, cỡ nguồn 300 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100 → f106: 100 → f136: 0.
- Đơn vị Range Selector: Ký tự.
- `/Text/Animators/Animator 1/Properties/Position`: [0, 256, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [128, 128].
- Chuỗi pre-comp: !Corporate Opener / layer 7 Scene 5 → Scene 5 / layer 5 Title 3 → Title 3 / layer 1 Text 3. Offset master: 873.000 frame; hệ số thời gian: 1.

## Scene 5 / Text 6 / ID 1265

Chữ: **Ultimate Visuals**

Font yêu cầu: `Manrope-Bold`, cỡ nguồn 300 px. Font render hiện tại bị thay thế: True.

- Chuỗi pre-comp: !Corporate Opener / layer 7 Scene 5 → Scene 5 / layer 3 Title 6 → Title 6 / layer 1 Text 6. Offset master: 919.000 frame; hệ số thời gian: 1.

## Scene 6 / Text 2 / ID 1455

Chữ: **Motion Graphics**

Font yêu cầu: `Manrope-Regular`, cỡ nguồn 96 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100 → f125: 100 → f155: 0.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 1/Properties/Position`: [0, 64, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [64, 64].
- Chuỗi pre-comp: !Corporate Opener / layer 6 Scene 6 → Scene 6 / layer 2 Title 2 → Title 2 / layer 1 Text 2. Offset master: 1080.000 frame; hệ số thời gian: 1.

## Scene 6 / Text 4 / ID 1481

Chữ: **Corporate / Opener**

Font yêu cầu: `Manrope-Bold`, cỡ nguồn 256 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 1/Properties/Position`: [0, -128, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [128, 128].
- `/Text/Animators/Animator 2/Selectors/Range Selector 1/End`: f130: 0 → f160: 100.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 2/Properties/Position`: [0, 128, 0].
- `/Text/Animators/Animator 2/Properties/Opacity`: 0.
- `/Text/Animators/Animator 2/Properties/Blur`: [128, 128].
- Chuỗi pre-comp: !Corporate Opener / layer 6 Scene 6 → Scene 6 / layer 7 Title 4 → Title 4 / layer 1 Text 4. Offset master: 1066.000 frame; hệ số thời gian: 1.

## Scene 6 / Text 5 / ID 1494

Chữ: **Lorem ipsum dolor sit amet, consectetur / adipiscing elit. Ut tincidunt nisi sit amet / vestibulum ornare. Aliquam porta lacus / pretium dapibus dapibus.**

Font yêu cầu: `Manrope-Regular`, cỡ nguồn 64 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100 → f117: 100 → f147: 0.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 1/Properties/Position`: [128, 0, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [64, 64].
- Chuỗi pre-comp: !Corporate Opener / layer 6 Scene 6 → Scene 6 / layer 6 Title 5 → Title 5 / layer 1 Text 5. Offset master: 1073.000 frame; hệ số thời gian: 1.

## Scene 6 / Text 7 / ID 1520

Chữ: **Corporate Opener Template**

Font yêu cầu: `Manrope-Bold`, cỡ nguồn 216 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100 → f147: 100 → f177: 0.
- Đơn vị Range Selector: Ký tự.
- `/Text/Animators/Animator 1/Properties/Position`: [0, 128, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [128, 128].
- Chuỗi pre-comp: !Corporate Opener / layer 6 Scene 6 → Scene 6 / layer 11 Title 7 → Title 7 / layer 1 Text 7. Offset master: 1043.000 frame; hệ số thời gian: 1.
- Chuỗi pre-comp: !Corporate Opener / layer 6 Scene 6 → Scene 6 / layer 11 Title 7 → Title 7 / layer 2 Text 7. Offset master: 1043.000 frame; hệ số thời gian: 1.
- Chuỗi pre-comp: !Corporate Opener / layer 6 Scene 6 → Scene 6 / layer 13 Title 7 → Title 7 / layer 1 Text 7. Offset master: 1043.000 frame; hệ số thời gian: 1.
- Chuỗi pre-comp: !Corporate Opener / layer 6 Scene 6 → Scene 6 / layer 13 Title 7 → Title 7 / layer 2 Text 7. Offset master: 1043.000 frame; hệ số thời gian: 1.

## Scene 7 / Text 1 / ID 1805

Chữ: **Ultimate Design**

Font yêu cầu: `Manrope-Bold`, cỡ nguồn 300 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100 → f172: 100 → f202: 0.
- Đơn vị Range Selector: Từ.
- `/Text/Animators/Animator 1/Properties/Position`: [0, 300, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [128, 128].
- Chuỗi pre-comp: !Corporate Opener / layer 5 Scene 7 → Scene 7 / layer 6 Title 1 → Title 1 / layer 1 Text 1. Offset master: 1227.000 frame; hệ số thời gian: 1.

## Scene 7 / Text 2 / ID 1818

Chữ: **Trendy Motion**

Font yêu cầu: `Manrope-Regular`, cỡ nguồn 96 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100 → f157: 100 → f187: 0.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 1/Properties/Position`: [0, 64, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [64, 64].
- Chuỗi pre-comp: !Corporate Opener / layer 5 Scene 7 → Scene 7 / layer 2 Title 2 → Title 2 / layer 1 Text 2. Offset master: 1242.000 frame; hệ số thời gian: 1.

## Scene 8 / Text 2 / ID 2185

Chữ: **Glow Design**

Font yêu cầu: `Manrope-Regular`, cỡ nguồn 96 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100 → f157: 100 → f187: 0.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 1/Properties/Position`: [0, 64, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [64, 64].
- Chuỗi pre-comp: !Corporate Opener / layer 4 Scene 8 → Scene 8 / layer 2 Title 2 → Title 2 / layer 1 Text 2. Offset master: 1444.000 frame; hệ số thời gian: 1.

## Scene 8 / Text 4 / ID 2211

Chữ: **Template / By Tortoha**

Font yêu cầu: `Manrope-Bold`, cỡ nguồn 256 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 1/Properties/Position`: [0, -128, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [128, 128].
- `/Text/Animators/Animator 2/Selectors/Range Selector 1/End`: f171: 0 → f201: 100.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 2/Properties/Position`: [0, 128, 0].
- `/Text/Animators/Animator 2/Properties/Opacity`: 0.
- `/Text/Animators/Animator 2/Properties/Blur`: [128, 128].
- Chuỗi pre-comp: !Corporate Opener / layer 4 Scene 8 → Scene 8 / layer 7 Title 4 → Title 4 / layer 1 Text 4. Offset master: 1430.000 frame; hệ số thời gian: 1.

## Scene 8 / Text 5 / ID 2224

Chữ: **Lorem ipsum dolor sit amet, consectetur / adipiscing elit. Ut tincidunt nisi sit amet / vestibulum ornare. Aliquam porta lacus / pretium dapibus dapibus.**

Font yêu cầu: `Manrope-Regular`, cỡ nguồn 64 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100 → f164: 100 → f194: 0.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 1/Properties/Position`: [128, 0, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [64, 64].
- Chuỗi pre-comp: !Corporate Opener / layer 4 Scene 8 → Scene 8 / layer 6 Title 5 → Title 5 / layer 1 Text 5. Offset master: 1437.000 frame; hệ số thời gian: 1.

## Scene 9 / Text 2 / ID 2501

Chữ: **Collage**

Font yêu cầu: `Manrope-Regular`, cỡ nguồn 96 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100 → f135: 100 → f165: 0.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 1/Properties/Position`: [0, 64, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [64, 64].
- Chuỗi pre-comp: !Corporate Opener / layer 3 Scene 9 → Scene 9 / layer 2 Title 2 → Title 2 / layer 1 Text 2. Offset master: 1662.000 frame; hệ số thời gian: 1.

## Scene 9 / Text 3 / ID 2514

Chữ: **Minimal Opener**

Font yêu cầu: `Manrope-Bold`, cỡ nguồn 360 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100 → f150: 100 → f180: 0.
- Đơn vị Range Selector: Ký tự.
- `/Text/Animators/Animator 1/Properties/Position`: [0, 256, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [128, 128].
- Chuỗi pre-comp: !Corporate Opener / layer 3 Scene 9 → Scene 9 / layer 6 Title 3 → Title 3 / layer 1 Text 3. Offset master: 1647.000 frame; hệ số thời gian: 1.

## Scene 10 / Text 4.1 / ID 2852

Chữ: **Corporate / Motion Design**

Font yêu cầu: `Manrope-Bold`, cỡ nguồn 256 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 1/Properties/Position`: [0, 128, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [128, 128].
- `/Text/Animators/Animator 2/Selectors/Range Selector 1/End`: f156: 0 → f186: 100.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 2/Properties/Position`: [0, -128, 0].
- `/Text/Animators/Animator 2/Properties/Opacity`: 0.
- `/Text/Animators/Animator 2/Properties/Blur`: [128, 128].
- Chuỗi pre-comp: !Corporate Opener / layer 2 Scene 10 → Scene 10 / layer 3 Title 4.1 → Title 4.1 / layer 1 Text 4.1. Offset master: 1851.000 frame; hệ số thời gian: 1.

## Scene 10 / Text 4.2 / ID 2865

Chữ: **Ultimate Visual / Graphics**

Font yêu cầu: `Manrope-Bold`, cỡ nguồn 256 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 1/Properties/Position`: [0, -128, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [128, 128].
- `/Text/Animators/Animator 2/Selectors/Range Selector 1/End`: f156: 0 → f186: 100.
- Đơn vị Range Selector: Dòng.
- `/Text/Animators/Animator 2/Properties/Position`: [0, 128, 0].
- `/Text/Animators/Animator 2/Properties/Opacity`: 0.
- `/Text/Animators/Animator 2/Properties/Blur`: [128, 128].
- Chuỗi pre-comp: !Corporate Opener / layer 2 Scene 10 → Scene 10 / layer 2 Title 4.2 → Title 4.2 / layer 1 Text 4.2. Offset master: 1851.000 frame; hệ số thời gian: 1.

## Scene 11 / Text 3 / ID 3087

Chữ: **Envato**

Font yêu cầu: `Manrope-Bold`, cỡ nguồn 360 px. Font render hiện tại bị thay thế: True.

- `/Text/Animators/Animator 1/Selectors/Range Selector 1/Start`: f0: 0 → f30: 100 → f61: 100 → f91: 0.
- Đơn vị Range Selector: Ký tự.
- `/Text/Animators/Animator 1/Properties/Position`: [0, 256, 0].
- `/Text/Animators/Animator 1/Properties/Opacity`: 0.
- `/Text/Animators/Animator 1/Properties/Blur`: [128, 128].
- Chuỗi pre-comp: !Corporate Opener / layer 1 Scene 11 → Scene 11 / layer 2 Title 3 → Title 3 / layer 1 Text 3. Offset master: 2038.000 frame; hệ số thời gian: 1.

<!-- ===== /file: ae-script-builder/references/template-audit/BANG-TEXT-VA-KEYFRAME.md ===== -->

<!-- ===== file: ae-script-builder/references/template-audit/BAO-CAO-PHAN-TICH.md ===== -->

# Phân tích chữ và chuyển động từ project After Effects thực tế

Ngày đọc: 21/10/2026. Công cụ trích: After Effects 26.3x87, ExtendScript chạy trong phiên riêng. Nguồn gốc được mở để đọc, không lưu thay đổi. Số liệu trong tài liệu là dữ liệu lấy từ AE, trừ chỗ ghi rõ là đề xuất hoặc quy đổi gần đúng.

## Kết quả cần dùng ngay

Chữ trong mẫu chủ yếu được dựng bằng **Text Animator + Range Selector**, kết hợp Position, Opacity và Blur trên từng từ, dòng hoặc ký tự. Transform của text thường đứng yên. Cảm giác hoàn chỉnh còn đến từ cấp pre-comp Title, layer Scene, parent, mask, adjustment layer và controller.

Chất lượng của mẫu nằm ở cách phối hợp các cấp này. Một prompt chỉ yêu cầu “chữ bay lên, opacity 0–100, thêm shadow” sẽ bỏ mất phần lớn cơ chế thật.

Đọc `MOTION-PRESETS.json` để lấy 10 công thức gọn, `BANG-TEXT-VA-KEYFRAME.md` để xem từng chữ đang dùng trong master, và `PROMPT-HOAN-CHINH-OPUS.md` để giao việc cho AI.

## 1. Phạm vi đã đọc và trạng thái thực tế

| File | Comp | Layer | Text layer trong thư viện | Tổng keyframe lưu trong file |
|---|---:|---:|---:|---:|
| Corporate Opener Mobile.aep | 224 | 435 | 65 | 773 |
| Corporate Opener Mobile copy 23.x.aep | 224 | 435 | 65 | 773 |
| save/1.aep | 449 | 872 | 130 | 1.556 |
| save/Untitled Project.aep | 0 | 0 | 0 | 0 |
| Auto-Save/Untitled Project auto-save 1.aep | 449 | 872 | 130 | 1.556 |
| Auto-Save/Untitled Project auto-save 2.aep | 449 | 872 | 130 | 1.556 |

- File đang mở khi bắt đầu là `/media/vmiz/Over Powers/video AE/save/1.aep`, 589 project item, chưa có thay đổi chưa lưu tại thời điểm đọc trạng thái.
- File 1.aep nhập **hai bộ template**, một nhánh copy 23.x và một nhánh bản hiện hành. Vì vậy 130 text layer là hai thư viện 65 lớp, không phải 130 đoạn chữ khác nhau đang xuất hiện trong video.
- Master chính được phân tích là `!Corporate Opener`, ID 3, thuộc nhánh `Corporate Opener Mobile copy 23.x.aep`; nó được bọc bởi `!Corporate Opener 2`, ID 6386.
- Từ master ID 3 lần theo các source comp của layer đang bật: 145 comp liên quan, **26 text layer nguồn thực sự được sử dụng**. Một nguồn có thể được dùng qua nhiều lớp, như chữ vòng ở Scene 6.
- Hai phiên bản template có cùng keyframe chữ/chuyển động được trích. So sánh native phát hiện 431 khác biệt ở alpha của Material Options / Shadow Color; đây không phải 431 thay đổi thiết kế hay 431 lỗi motion.
- Nhánh thứ hai trong 1.aep giữ các tham số tĩnh/keyframe được so sánh với template hiện hành. Nhánh đầu có thay đổi màu/controller của Scene 1 và thêm một layer nền trong Glow Elements; phần lớn cấu trúc chữ vẫn từ mẫu.
- Các thư mục được cung cấp không chứa MP4/MOV, JSX/JSXBIN, FFX hay AEPX độc lập. Các biểu thức điều khiển nằm bên trong AEP: working có 544 expression lưu trong hai bộ.
- Music comp trong cả hai nhánh đều rỗng. Chưa có âm thanh để phân tích nhịp dựng theo nhạc.
- Đã đọc trang HELP.pdf. Tài liệu mô tả controller theo scene, thư mục Edit/Texts, placeholder và font Manrope. Các chỉ dẫn đó được dùng như tài liệu mô tả mẫu, không phải lệnh thay đổi project.

### Những điểm ảnh hưởng chất lượng

1. **Thiếu font thực tế.** Native `fontObject.isSubstitute=true` cho Manrope-Bold và Manrope-Regular; cả hai đang trỏ `C:\Windows\Fonts\times.ttf`. Vì thế chữ serif trong ảnh đang thấy là font thay thế. Không nên dùng hình serif này làm chuẩn của Manrope.
2. **Có expression lỗi sẵn trong nguồn.** Mỗi bộ template có ba lỗi ở Scene 3, 6, 8: Bevel and Emboss / Angle gọi `CONTROL → Title 2 → Angle Glow`, trong khi thuộc tính tên đó không tồn tại. Working nhập hai bộ nên ghi nhận sáu lỗi. Chưa sửa nguồn trong nhiệm vụ phân tích này.
3. **Ảnh/video còn là placeholder.** Các frame có mũi tên tải xuống đúng như source hiện có. Chưa thể kết luận chất lượng bố cục với footage thật.

## 2. Định dạng, thời gian và phân cấp

Master gốc: **2160 × 3840, 30 fps, 71 giây**. Scene 1–10 dài 8 giây; Scene 11 dài 3,0667 giây. Các scene chồng thời gian trên master.

| Scene | Bắt đầu trên master | Frame master, từ 0 |
|---|---:|---:|
| 1 | 0,0000 s | 0 |
| 2 | 7,0667 s | 212 |
| 3 | 13,8667 s | 416 |
| 4 | 20,6333 s | 619 |
| 5 | 27,4000 s | 822 |
| 6 | 34,1667 s | 1025 |
| 7 | 40,9000 s | 1227 |
| 8 | 47,6667 s | 1430 |
| 9 | 54,4000 s | 1632 |
| 10 | 61,2000 s | 1836 |
| 11 | 67,9333 s | 2038 |

Chuỗi dựng điển hình:

`Master → Scene → Designs/Title → Edits/Texts/Text → Text layer → Animator → Range Selector`.

Mỗi cấp làm một nhiệm vụ:

- **Text source:** nội dung, font, căn chữ, vũ đạo theo từ/dòng/ký tự.
- **Title design:** đóng gói text source để thay nội dung mà giữ cách dựng.
- **Scene:** vị trí, tỷ lệ, thời gian vào/ra của cả khối chữ; Fill, Shadow, Cylinder và quan hệ với hình.
- **Glass/Mask/Adjustment:** vật liệu và vùng tác động, không phải thuộc tính font.
- **CONTROL:** đổi màu, kính, độ sáng, bóng qua pseudo effect và expression.
- **Master:** thứ tự, điểm nối và thời gian chồng các scene.

Tên comp bị trùng giữa hai nhánh. Khi tự động hóa phải nhận diện bằng ID kèm đường dẫn thư mục/chuỗi sử dụng, không chỉ gọi tên `Text 1` hay `Scene 1`.

## 3. Các công thức text chính

Tất cả frame ở bảng này là **frame cục bộ của comp Text**, bắt đầu từ 0, tại 30 fps. Những tham số pixel thuộc khổ nguồn, chưa nhân tỷ lệ của layer cha.

| Công thức | Ví dụ nguồn | Font/cỡ nguồn | Chọn theo | Giá trị Animator | Keyframe điều khiển |
|---|---|---|---|---|---|
| R1 Tiêu đề chính | Scene 1 / Text 1 / Visual Graphics | Manrope Bold 300 | Từ | Position [0,300,0]; Opacity 0; Blur [128,128] | Start: f0=0 → f30=100 → f153=100 → f183=0 |
| R2 Nhãn phụ | Scene 1 / Text 2 / Motion Design | Manrope Regular 96 | Dòng | Position [0,64,0]; Opacity 0; Blur [64,64] | Start: f0=0 → f30=100 → f125=100 → f155=0 |
| R3 Display | Scene 2 / Text 3 / Minimalist | Manrope Bold 360 | Ký tự | Position [0,256,0]; Opacity 0; Blur [128,128] | Start: f0=0 → f30=100 → f152=100 → f182=0 |
| R4 Heading hai chiều | Scene 3 / Text 4 / Brand Promo / By Tortoha | Manrope Bold 256 | Dòng | Animator 1: Y=-128; Animator 2: Y=+128; cả hai Opacity 0, Blur 128 | Animator 1 Start f0=0 → f30=100; Animator 2 End f172=0 → f202=100 |
| R5 Body | Scene 3 / Text 5 / Lorem ipsum… | Manrope Regular 64 | Dòng | Position [128,0,0]; Opacity 0; Blur [64,64] | Start f0=0 → f30=100 → f135=100 → f165=0 |

### Vì sao Opacity Animator bằng 0 nhưng chữ vẫn hiện?

Giá trị 0 là độ mờ của **nhóm ký tự đang được selector chọn**. Khi Start chạy từ 0 lên 100, từng phần thoát khỏi phạm vi bị đẩy/ẩn/làm mờ và trở về hình thức gốc. Transform / Opacity của layer vẫn 100.

Đây là chuyển động kết hợp có thứ tự: chữ đang bị dịch và mờ → selector đi qua → chữ về đúng chỗ, sắc nét và hiện đủ. Chỉ keyframe Transform / Opacity của cả layer sẽ không tái tạo được cách dựng theo từ/dòng/ký tự.

Các thời gian cuối có biến thể giữa scene. Ví dụ Heading R4 ở Scene 6 thoát bằng End từ f130 đến f160, không phải lúc nào cũng f172–202. Bảng chi tiết 26 text nằm trong `BANG-TEXT-VA-KEYFRAME.md`.

## 4. Keyframe ở đâu: ví dụ Scene 1

Đường đọc trong AE:

- Mở nhánh template copy 23.x → Scene 1 → Edits → Texts → Text 1.
- Text layer → Text → Animator 1 → Range Selector 1 → Start.
- Chuyển động riêng của từng từ nằm ở đây; Transform của text source không có keyframe.
- Trở lại Scene 1 để xem layer Title 1, Title 2 và các lớp kính.

| Thành phần | Offset của pre-comp trong Scene 1 | Mốc trên timeline Scene 1 |
|---|---:|---|
| Visual Graphics | f27 | Bắt đầu f27; hiện đủ f57; bắt đầu rút f180; hết f210 |
| Motion Design | f55 | Bắt đầu f55; hiện đủ f85; bắt đầu rút f180; hết f210 |
| Glass Stroke / Glass Effects của nhãn | f55 | Opacity f55=0 → f85=100 → f180=100 → f210=0 |
| Glass Mask 2 của ảnh | f60 | Size f60=[0,0] → f90=[2500,4180] → f165=[2500,4180] → f195=[0,1024] |
| Image Scene 1 | f67 | Layer ảnh bắt đầu ở f67; kết quả hiện hình còn phụ thuộc mask và pre-comp |

Ví dụ: keyframe f30 trong Text 1 không phải frame 30 của Scene 1. Vì Title 1 bắt đầu f27 và source bên trong bắt đầu f0, key đó xuất hiện ở f57 của Scene 1. Với scene khác còn phải cộng offset của Scene trên master và xử lý stretch/time remap nếu có.

Nhịp vào của chữ chính và nhãn phụ lệch **28 frame = 0,9333 giây**. Nhịp ra của hai nhóm lại đồng bộ ở f180–210. Cách dàn thời gian này tạo thứ bậc khi vào, rồi gom nhóm khi kết cảnh.

## 5. Position, Scale, Rotation, Anchor Point và Opacity

### Text source và pre-comp không dùng cùng hệ tọa độ

- Scene dọc: 2160×3840, tâm [1080,1920].
- Nhiều Text/Title pre-comp nằm ngang: 3840×2160, tâm [1920,1080].
- Text layer thật trong Text source có Anchor Point [0,0,0], gắn với hệ gốc/baseline chữ; không phải tâm của Scene.
- Parent biến đổi tiếp vị trí/tỷ lệ của con. Một Position của con có parent là tọa độ local, không thể đọc thẳng thành vị trí cuối trên khung hình.

### Ví dụ chính xác của Scene 1

| Layer | Anchor Point | Position | Scale | Rotation | Opacity Transform |
|---|---|---|---|---:|---:|
| Text layer thật của Text 1 | [0,0,0] | [1925,2499;1154,25;0] | [100,100,100] | 0 | 100 |
| Title 1 trong Scene 1 | [1920,1080,0] | [1080,2952,0] | [75,75,100] | 0 | 100 |
| Text layer thật của Text 2 | [0,0,0] | [1919,5199;1102,56;0] | [100,100,100] | 0 | 100 |
| Title 2 trong Scene 1 | [1920,1080,0] | [1080,3340,0] | [100,100,100] | 0 | 100 |

Các giá trị này là tĩnh. Trong Scene 1, cảm giác chữ trồi lên đến từ Text Animator, không phải keyframe Position của các hàng trong bảng.

Font chính 300×75%=225 px hiệu dụng trong output rộng 2160. Nếu xuất cùng bố cục ở 1080×1920, nó tương đương khoảng **112,5 px**. Nhãn phụ 96 px với scale 100% tương đương **48 px** ở khổ rộng 1080. Bởi vậy không thể lấy trực tiếp font 300 rồi dùng trên khung 1080.

### Những trường hợp Transform thực sự có keyframe

- **Scene 2 / Title 3 / Position:** f60 [1080,1920,0] → f90 [1080,410,0]. Cả tiêu đề đổi vị trí sau giai đoạn reveal bên trong source.
- **Scene 5 / Title 6 / Scale:** f97 [100,100,100] → f172 [60,60,100] → f202 [0,0,100]. Text source “Ultimate Visuals” không có Animator riêng; hiệu ứng thu chữ nằm ở cấp Scene.
- **Scene 6 / Title 7 / CC Cylinder / Rotation Y:** f18=0° → f318=360°. Đây là rotation của effect, không phải Transform / Rotation của text. Scene dài 8 giây nên chỉ dùng một phần khoảng quay 10 giây đã định nghĩa.
- Anchor Point của text trong các ví dụ trên là tĩnh; không có căn cứ để yêu cầu AI phải animate Anchor Point cho mọi chữ.

## 6. Làm mượt: đây là Bézier đã chỉnh, không chỉ F9

Native xác nhận enum BEZIER=6613, LINEAR=6612, HOLD=6614. Các keyframe reveal điển hình là Bézier, Temporal Auto Bezier=false, Temporal Continuous=false; tay nắm được chỉnh riêng.

**R1 / Start / đoạn f0–30:**

- Key f0, Out: Speed ≈0,00000705; Influence **75,2169715%**.
- Key f30, In: Speed ≈−0,00001077; Influence **75,1205431%**.
- Những speed rất nhỏ gần 0 là dữ liệu số gốc; không phải một lần đi lùi có chủ đích.
- Đường chuẩn hóa gần đúng: `cubic-bezier(0.75217,0,0.24879,1)`.
- Cảm giác: đầu chậm → tăng tốc mạnh ở giữa → giảm tốc về điểm dừng. Không phải spring và không có overshoot đáng kể từ công thức này.

**Mask ảnh / Size / đoạn f60–90:**

- Out Influence khoảng **15,2362572%**, In Influence **100%**; speed đầu/cuối gần 0.
- Chuẩn hóa gần đúng: `cubic-bezier(0.15236,0,0,1)`.
- Mask mở nhanh sớm rồi kéo đuôi giảm tốc dài, khác đường cong của chữ.

`EASING-THUC-TE.png` được vẽ từ **valueAtTime native mỗi 0,25 frame**, không phải đồ thị tự ước lượng. File mẫu nằm ở `raw/native-samples.json`. Hai cubic-bezier nêu trên là cách chuyển gần đúng khi dựng bằng code; nếu dùng AE hãy giữ Speed/Influence gốc.

Temporal easing điều khiển tốc độ theo thời gian. Spatial tangent điều khiển hình dạng đường đi của Position 2D/3D. Hai loại không thay thế cho nhau; dữ liệu tangent đã được giữ trong CSV/JSON khi thuộc tính hỗ trợ.

## 7. Đổ bóng: thông số UI và dữ liệu raw khác nhau

Bóng chữ rõ ràng được áp ở **Scene 5 / Title 1, Title 3, Title 6**, bằng `ADBE Drop Shadow`, nối controller `Text Shadow`.

| Tham số | Giá trị đúng để hiểu/dựng |
|---|---|
| Shadow Color | Đen [0,0,0] |
| Opacity trên UI/controller | **30%** |
| Opacity raw đọc bằng scripting | **76,5 trên thang 0–255** |
| Direction | 135° |
| Distance | 8 px nguồn |
| Softness | 128 px nguồn |
| Shadow Only | Tắt |

Điểm rất dễ sai: nhìn raw 76,5 rồi viết “Opacity 76,5%”. Native đã kiểm controller=30, max của effect=255. Khi làm bằng code cần chuyển opacity về 0,30. Khi xuất 1080 từ hệ nguồn 2160, khoảng cách tương đương 4 px và độ mềm theo hệ nguồn tương đương 64 px; không coi tham số Softness AE là Gaussian sigma CSS có thể chép một-một mà không render đối chiếu.

Tương tự, Glow Threshold raw=153 trên thang 0–255 tương ứng UI=60%; Fill Opacity raw=1 trên thang 0–1 tương ứng UI=100%. Mỗi effect có miền giá trị riêng.

Không phải mọi chữ đều có Drop Shadow. Nhiều giá trị Layer Styles mặc định vẫn đọc được qua API dù group đang tắt. Báo cáo chỉ coi style/effect có nhánh đang bật là đang áp dụng.

## 8. Kính, glow và blur

Nhãn “Motion Design” ở Scene 1 là một tổ hợp:

1. Title 2 chứa text.
2. Glass Stroke: shape viền, parent vào Title 2.
3. Glass Effects: adjustment layer, parent vào Title 2.
4. Glass Mask: alpha matte giới hạn vùng adjustment.
5. CONTROL điều khiển kích thước, bo góc, màu, tint và blur bằng expression.

Thông số nhãn Scene 1:

- Rectangle Size [1024,256], Roundness 128.
- Tint Amount 6%; Gaussian Blur (Legacy) 128.
- Stroke dùng **Bevel and Emboss đang bật**: size 5, angle 90°, altitude 30°, highlight opacity 75%, shadow opacity 50%.
- **Drop Shadow của stroke đang tắt.** Bóng trong Bevel and Emboss không phải Drop Shadow rời đã phân tích ở Scene 5.
- Glass Stroke và Glass Effects có opacity keyframe đồng bộ f55–85–180–210.

Không cần suy diễn đây là mô phỏng khúc xạ kính vật lý. Cấu trúc thật dùng blur nền, tint, matte, viền và bevel.

Blur của chữ là **Text Animator Blur**. Motion Blur cấp comp/layer trong các Scene đã kiểm đang tắt. Gaussian Blur của kính, Glow Radius và CC Radial Blur của nền là các cơ chế khác nữa. Prompt phải gọi đúng loại blur đang cần.

## 9. Chữ cuốn quanh ảnh: Scene 6

- Source strip `Title 7` rộng 6000×2160, anchor [3000,1080,0].
- Hai lớp Title 7 nằm trước và sau lớp ảnh, dùng hai giá trị Render của CC Cylinder là 2 và 3 để xử lý hai phần mặt.
- Radius 100%; Rotation X=19°, Rotation Z=31°.
- Rotation Y ở lớp chính có keyframe f18=0°, f318=360°; lớp phụ phụ thuộc cấu trúc parent.
- Layer chính scale [210,210,100].
- Ambient=200, Diffuse=0, Specular=0; Glow Radius=64, Intensity=1, Threshold UI=60%.

Kết quả là chữ có chiều sâu và bị ảnh che ở phần phía sau. Chỉ xoay Z một dòng chữ phẳng sẽ không có cùng kết quả.

## 10. Phân cấp thị giác và cách chuyển thành prompt

Quan sát source và 22 frame native cho thấy các vai trò chữ được tách rõ:

- Headline lớn, thường 1–2 dòng, chịu trách nhiệm thông điệp chính.
- Display/keyword chọn theo ký tự để tạo nhịp riêng, có thể đổi vị trí ở cấp Scene.
- Heading nhiều dòng có animator vào và ra riêng.
- Body nhỏ, reveal theo dòng từ bên phải, không dùng vũ đạo cỡ lớn của headline.
- Nhãn phụ nằm trong pill kính, vào trễ hơn headline.
- Chữ vòng làm lớp không gian phụ, kết hợp front/back của hình.

Đây là các công thức lấy từ mẫu, không phải quy tắc bất biến cho mọi thương hiệu. Khi đổi nội dung, giữ vai trò và nhịp nhưng phải kiểm chiều dài dòng, thời gian đọc và vùng an toàn. Không đưa nguyên Lorem ipsum, Envato, By Tortoha hoặc chữ mẫu vào video mới khi brief không yêu cầu.

## 11. Cách dùng bộ giao cho Opus

1. Đọc báo cáo này và `MOTION-PRESETS.json` trước. File preset khoảng 40 KB, đủ để bắt đầu, không cần nạp toàn bộ raw gần 200 MB.
2. Khi cần đúng một text/scene, đọc mục tương ứng trong `BANG-TEXT-VA-KEYFRAME.md` hoặc `TEXT-RECIPES.json`.
3. Khi cần đối chiếu keyframe đầy đủ, đọc `analysis/working-1/keyframes.csv` (1.556 hàng dữ liệu). Frame trong CSV là local của comp, không phải master mặc định.
4. Dùng `PROMPT-HOAN-CHINH-OPUS.md` và điền brief. Nếu cần .aep chỉnh layer được, chọn AE native. Nếu chọn Remotion/Three.js phải diễn dịch effect có kiểm chứng, không coi import MP4 là có layer AE gốc.
5. Tạo bài thử nhỏ: headline + pill kính + 1 khung ảnh, rồi render để khóa gu trước khi dựng toàn bộ.

## 12. Đã kiểm và giới hạn

- Đã mở và trích đủ sáu file AEP bằng AE, không dùng suy đoán từ tên file để điền thông số.
- Đã trích text, hierarchy, keyframes, temporal easing, spatial tangent, expression và trạng thái effect/style.
- Đã kiểm missing font bằng API native, đồng thời xác nhận font thay thế qua ảnh render.
- Đã render và giải mã được **22 frame native 540×960**: 12 mốc của Scene 1 và một mốc cho mỗi Scene 2–11. `SCENE-01-CONTACT.jpg` và `SCENE-OVERVIEW.jpg` là ảnh ghép các frame đó.
- RenderQueue trả trạng thái `ERR_STOPPED` 3019 dù ghi ra TIFF; từng TIFF đã được mở/giải mã thành công. Các ảnh là bằng chứng still native, không phải bằng chứng pipeline render toàn video đã đạt. `saveFrameToPng` trước đó không ghi được ảnh nên không dùng làm bằng chứng.
- Chưa render/phát toàn bộ 71 giây, chưa kiểm motion blur ở mọi comp không dùng, chưa nghe nhạc vì Music comp rỗng.
- Font thiếu và expression lỗi được báo lại, chưa sửa file nguồn.
- Hash nguồn trước/sau và kiểm tính toàn vẹn của bộ giao nằm trong `VERIFICATION.json`.

### Tài liệu API dùng để xác định cách đọc

- Adobe Scripts: https://helpx.adobe.com/after-effects/using/scripts.html
- Property / keyframe easing: https://ae-scripting.docsforadobe.dev/property/property/
- Font substitution: https://ae-scripting.docsforadobe.dev/text/fontsobject/

Các tài liệu web giải thích API. Các con số của template trong báo cáo lấy từ dữ liệu native tại máy, không lấy từ một bài hướng dẫn chung trên mạng.

<!-- ===== /file: ae-script-builder/references/template-audit/BAO-CAO-PHAN-TICH.md ===== -->

<!-- ===== file: ae-script-builder/references/template-audit/PROMPT-HOAN-CHINH-OPUS.md ===== -->

# Prompt dựng motion graphic theo ngôn ngữ của project AE đã phân tích

Sao chép khối dưới, điền phần BRIEF. Các con số kỹ thuật là tham chiếu có nguồn; thời lượng và nội dung phim mới do brief quyết định.

```text
Bạn là đạo diễn motion graphics và người dựng After Effects. Hãy chuyển brief của tôi thành một video có phân cấp chữ rõ, nhịp mượt và nguồn chỉnh sửa được, học đúng kỹ thuật của template đã phân tích.

NGUỒN THAM CHIẾU
- Mẫu:
  /media/vmiz/Over Powers/video AE/video/vertical-corporate-opener-2026-09-24-08-52-22-utc
- Project đang triển khai:
  /media/vmiz/Over Powers/video AE/save/1.aep
- Bộ phân tích native:
  /media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/research/ae-text-audit-2026-10-21

Đọc BAO-CAO-PHAN-TICH.md và MOTION-PRESETS.json trong bộ phân tích trước. Chỉ đọc thêm BANG-TEXT-VA-KEYFRAME.md, TEXT-RECIPES.json hoặc CSV khi cần đúng text/scene đó. Không nạp toàn bộ raw vào ngữ cảnh nếu không cần.

BRIEF
- Mục tiêu video: [...]
- Đối tượng xem và nơi đăng: [...]
- Thông điệp duy nhất cần nhớ: [...]
- Kịch bản/chữ chính xác: [...]
- Logo, ảnh, footage, font, nhạc được dùng: [...]
- CTA chính xác: [...]
- Khổ / fps / thời lượng: [...]
- Engine và file nguồn: [After Effects native .aep / Remotion / Three.js]
- Tính chất công việc: [dựng video mới / sửa một bản sao của project]
- Phạm vi tự sáng tạo và phần đã khóa: [...]

NGUYÊN TẮC LÀM VIỆC
1. Kiểm tra công cụ thực sự khả dụng. Nếu giao .aep phải dựng bằng AE native hoặc script JSX thực thi trong AE. Không gọi một MP4 import vào AE là project có layer text/shape/keyframe gốc.
2. Giữ nguồn tham chiếu; làm trong project mới hoặc bản sao ở thư mục đầu ra riêng. Giữ cấu trúc phân tầng để tôi chỉnh tiếp.
3. Dùng nội dung của brief. Không bê chữ Lorem ipsum, Envato, By Tortoha hay CTA mẫu sang video mới. Không đoán tên riêng hoặc số liệu.
4. Tự quyết các chi tiết triển khai đã nằm trong brief. Hỏi gộp một lần nếu còn thiếu nội dung bắt buộc, font hoặc dữ liệu thật. Tuân thủ các cổng duyệt của dự án.
5. Các luật OPA chỉ áp dụng khi đây là video OPA. Nếu brief chọn glass/glow như mẫu, đối chiếu phạm vi thương hiệu trước khi áp một lệnh cấm mặc định.

KIẾN TRÚC DỰNG
- Master: thời gian và điểm nối scene.
- Scene: bố cục tổng, vị trí/tỷ lệ của khối chữ, hình và camera.
- Title/Design pre-comp: đóng gói hình thức.
- Text/Edit pre-comp: nội dung, font và Text Animator.
- CONTROL: màu, kích thước, vật liệu, shadow, blur và glow.
- Glass Stroke, Glass Effects, Glass Mask: tách riêng, parent và matte đúng quan hệ.
- Nhận diện comp bằng đường dẫn và ID/chuỗi sử dụng khi tên trùng. Không sửa nhầm nhánh template thứ hai.

PHÂN CẤP CHỮ
- Một tiêu điểm chính tại mỗi nhịp.
- Headline để truyền thông điệp chính; display/keyword để tạo điểm nhấn.
- Body dễ đọc, chuyển động nhẹ hơn headline.
- Nhãn phụ/pill vào trễ theo thứ bậc, không tranh mắt với headline.
- Viết hoa chữ cái đầu mỗi dòng tiếng Việt; tên riêng giữ đúng.
- Cụm nhấn phải có lý do thiết kế, xử lý tương đương giữa các mục song song.
- Xác định thời gian đọc từ nội dung mới; không chép máy móc thời gian của câu ngắn sang đoạn dài.

CÔNG THỨC THAM CHIẾU THỰC TẾ
Các số dưới thuộc hệ nguồn 2160×3840, 30 fps, frame bắt đầu từ 0. Chúng là preset học từ mẫu, không phải nội dung/kịch bản bắt buộc của phim mới.

R1 — Headline theo từ:
- Text Animator Position [0,300,0], Opacity 0, Blur [128,128].
- Based On = Words.
- Range Selector Start: f0=0, f30=100, f153=100, f183=0.
- Giữ Transform Opacity của text layer ở 100. Opacity 0 là của phạm vi Animator được chọn.

R2 — Nhãn phụ theo dòng:
- Position [0,64,0], Opacity 0, Blur [64,64].
- Based On = Lines.
- Start: f0=0, f30=100, f125=100, f155=0.

R3 — Display theo ký tự:
- Position [0,256,0], Opacity 0, Blur [128,128].
- Based On = Characters.
- Ví dụ Start f0=0, f30=100, f152=100, f182=0.

R4 — Heading nhiều dòng có animator vào/ra riêng:
- Animator vào: Position [0,-128,0], Opacity 0, Blur 128;
  Start f0=0 → f30=100.
- Animator ra: Position [0,+128,0], Opacity 0, Blur 128;
  ví dụ End f172=0 → f202=100.
- Chọn mốc ra theo scene và thời gian đọc; biến thể có trong preset.

R5 — Body theo dòng từ bên phải:
- Position [128,0,0], Opacity 0, Blur [64,64].
- Based On = Lines.
- Ví dụ Start f0=0, f30=100, f135=100, f165=0.

R6 — Scale cả khối ở cấp Scene:
- Ví dụ Scene 5 / Title 6: f97=[100,100,100],
  f172=[60,60,100], f202=[0,0,100].
- Hiệu ứng này nằm trên layer pre-comp, không ép thêm Text Animator vào source khi không cần.

R7 — Chữ cuốn quanh ảnh:
- Strip Title rộng 6000×2160, anchor [3000,1080,0].
- Dùng CC Cylinder và hai lớp để xử lý phần chữ trước/sau ảnh.
- Radius 100%, Rotation X 19°, Rotation Z 31°.
- Rotation Y tham chiếu: 0° ở f18 → 360° ở f318.
- Scene mẫu dài 8 giây nên không hiểu rằng cả vòng 10 giây đều được chiếu.
- Học đúng layer order, parent và Render mode 2/3 từ preset.

EASING
- Không chỉ nhấn F9 rồi coi là khớp mẫu.
- Reveal headline điển hình dùng Bézier, Speed hai đầu gần 0,
  Out Influence khoảng 75,21697%, In Influence khoảng 75,12054%.
- Nếu chuyển sang code, cubic-bezier chuẩn hóa gần đúng:
  (0.75217,0,0.24879,1).
- Mask mở ảnh có đường riêng: Out Influence khoảng 15,23626%,
  In Influence 100%; gần đúng (0.15236,0,0,1).
- Không dùng cùng một easing cho text, mask, camera và mọi hiệu ứng.
- Muốn khớp chính xác, đọc inEase/outEase và native-samples.json.
- Temporal easing quyết định tốc độ; spatial tangent quyết định đường đi.
- Không tự thêm bounce/spring khi preset không có.

PHỐI HỢP THỜI GIAN
- Scene 1 tham chiếu: headline offset f27, nhãn phụ offset f55.
- Headline hiện đủ f57; nhãn hiện đủ f85; cả hai rút f180–210.
- Keyframe local của pre-comp phải được đổi về timeline Scene/Master.
- Khi đổi sang 60 fps, giữ thời gian giây và đổi số frame tương ứng.
- Với scene mới, thiết kế bảng vào → hiện đủ → giữ đọc → ra cho từng vai trò chữ.

TỌA ĐỘ VÀ TỶ LỆ
- Scene dọc gốc có tâm [1080,1920].
- Nhiều Title pre-comp nằm ngang 3840×2160, anchor [1920,1080].
- Text source có anchor [0,0,0]; không tự coi đó là lỗi.
- Position của con có parent là local; kiểm toàn bộ chuỗi transform.
- Nếu đổi output rộng 2160 sang 1080, q=0,5 cho đại lượng pixel.
  Giữ nguyên phần trăm scale, opacity và góc; không scale hai lần.
- Ví dụ font 300 với Title scale 75% cho cỡ hiệu dụng 225 ở khổ gốc,
  tương đương 112,5 ở output 1080; font phụ 96 tương đương 48.
- Đổi nội dung/font thì đo lại sourceRect và bố cục trước khi chốt anchor.

BÓNG VÀ VẬT LIỆU
- Bóng chữ Scene 5 tham chiếu:
  đen, Opacity UI 30%, Direction 135°, Distance 8, Softness 128,
  Shadow Only tắt.
- Raw Opacity effect là 76,5/255, không phải 76,5%.
- Glow Threshold raw 153/255 tương ứng UI 60%.
- Fill Opacity raw 1/1 tương ứng UI 100%.
- Không gán shadow cho mọi chữ chỉ vì API đọc được giá trị mặc định.
  Kiểm enabled của effect/group/style trước.
- Pill kính Scene 1: Size [1024,256], Roundness 128,
  adjustment Gaussian Blur 128, Tint 6%, alpha matte riêng.
- Stroke kính dùng Bevel and Emboss; Drop Shadow của stroke đang tắt.
- Phân biệt Text Animator Blur, Gaussian Blur, Glow, Radial Blur
  và Motion Blur theo màn trập. Không gọi chung chúng là motion blur.

KIỂM TRA NGUỒN TRƯỚC KHI DỰNG
- Manrope Bold/Regular đang bị thay bằng times.ttf trong phiên audit.
  Kiểm font thật trước khi dùng hình làm chuẩn typography;
  không âm thầm coi font thay thế là gu thiết kế đã duyệt.
- Ba lỗi expression mỗi bộ ở Scene 3,6,8 gọi Angle Glow không tồn tại.
  Khi dựng bản mới, nối đúng controller/property hoặc dựng tương đương
  có kiểm chứng; không sao chép nguyên lỗi vào nguồn mới.
- Music comp mẫu rỗng. Chỉ dựng nhạc/SFX từ tài nguyên và phạm vi brief.

QUY TRÌNH ĐẦU RA
1. Tóm tắt brief, điểm đã khóa, phương án hình ảnh và công thức dự định dùng.
2. Lập bảng theo scene: thời gian, chữ chính xác, vai trò thị giác,
   font/cỡ hiệu dụng, điểm vào/hiện đủ/ra, transform, selector, easing,
   shadow, matte, hiệu ứng và quan hệ với hình.
3. Dựng khung đã hiện đủ và đoạn mẫu 3–5 giây để duyệt gu.
4. Sau khi duyệt, tự dựng phần còn lại và tự sửa trong phạm vi đã chốt.
5. Render và mở frame để xem tại đầu/giữa/cuối pha vào, pha đọc và pha ra.
   Kiểm thêm các điểm nối và phát video ở tốc độ thật.
6. Kiểm font, dấu tiếng Việt, sourceRect, vùng an toàn, clipping,
   phân cấp, thời gian đọc, mặt trước/sau và expression.
7. Giao source chỉnh sửa được, script dựng lại nếu có, MP4 và ảnh contact.
   Báo chính xác những gì đã đo/xem/nghe và phần chưa kiểm.
8. Chỉ báo render thành công sau khi file được mở/giải mã và kiểm tra;
   không suy từ lệnh đã chạy hay file chỉ vừa xuất hiện.
```

<!-- ===== /file: ae-script-builder/references/template-audit/PROMPT-HOAN-CHINH-OPUS.md ===== -->

<!-- ===== file: ae-script-builder/templates/du-an-ae/README.md ===== -->

# Bộ khung dự án After Effects (nhánh A: dựng mới bằng script)

Chép cả thư mục này thành `<dự án>\ae\<tên>\`. Tên thư mục là tên file project: `project\<tên>.aep`.

Đã thử ngày 26/10/2026 trên AE 2026 (26.3): dựng 6 comp, 2 expression, 0 lỗi; xuất 2 khung đúng chữ tiếng Việt; soát chữ đạt.

| File | Việc |
|---|---|
| `tools/ae.py` | dựng (`build`), render MP4 (`render`), xuất khung tĩnh (`stills`) trong phiên AE riêng |
| `tools/seed/empty-ae26.aep` | project trống do AE 2026 lưu; dùng làm gốc mỗi lần dựng |
| `build/lib.jsx` | thư viện: comp, shape, chữ, Text Animator R1–R5, ease, lò xo, CONTROL màu. Mặc định theo thương hiệu OPA: dự án khác sửa `O.COLORS`, `O.FONT` |
| `build/main.jsx` | mở seed, tạo thư mục, master, đặt cảnh, quét expression, xuất chữ, lưu, ghi báo cáo |
| `build/scenes/s1_mau.jsx` | cảnh mẫu 5 s: headline R1, nhãn phụ R2, nút lò xo, máy quay trôi |
| `tools/qa_chu.py` | soát chữ từ báo cáo dựng (viết hoa đầu dòng, cỡ ≥ 28 px, font trong bộ) |
| `tools/to_contact.py` | tờ khung có nhãn giờ từ MP4 |

```bash
python -I tools/ae.py build
python -I tools/ae.py stills --comp MASTER_16x9 --frames 45,100 --outdir out/stills
python -I tools/ae.py render --comp MASTER_16x9 --start 0 --end 149 --out out/review/_lam/b01.mp4
python -X utf8 -I tools/qa_chu.py
```

- Thêm cảnh: viết `OPA.buildS2` trong `build/scenes/`, thêm một dòng vào `plan` trong `main.jsx`.
- Thêm âm: chép `scenes/am_thanh.jsx` và `tools/am_thanh_cues.py`, `tools/phan_tich_sfx.py` từ `examples/opa-agent`, rồi sửa đủ các chỗ ghi cứng theo bảng ở sổ tay mục 15 bước 3. Cách đặt mức: sổ tay mục 9.
- Font: máy mới phải cài Be Vietnam Pro và `examples/opa-agent/assets/fonts/FrauncesOPA-ExtraBoldItalic.ttf` (sổ tay mục 6.4). Thiếu font thì báo cáo dựng ghi lỗi FONT.
- Đường dẫn AE nằm ở đầu `tools/ae.py` (`AE_DIR`).

<!-- ===== /file: ae-script-builder/templates/du-an-ae/README.md ===== -->
