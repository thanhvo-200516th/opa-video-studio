# kb-ae-template-customizer — toàn văn tài liệu của nguồn `ae-template-customizer`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/ae-template-customizer/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: ae-template-customizer/SKILL.md ===== -->

---
name: ae-template-customizer
description: >-
  Phân tích, bóc tách cấu trúc và tùy biến sâu các dự án After Effects thương mại (.aep từ Envato Elements / VideoHive nhiều phân cảnh). Tự động quét cây thư mục comp/layer và mốc thời gian toàn cục (parse_aep_timings.py), thay thế đồng loạt nhân vật 2D/3D, ảnh chân dung, bảng giao diện UI đa tầng và sửa lỗi mất dấu tiếng Việt do Range Selector (customize_template_assets.jsx), chuẩn hóa âm thanh SFX High-Tech SaaS UI 48kHz 24-bit lọc lowpass 11kHz (prepare_sfx_pro.py), và tự động chèn SFX khớp chính xác keyframe ở ngưỡng -6.0 đến -9.5 dB (generate_ae_sfx_jsx.py). Kích hoạt khi người dùng muốn chỉnh sửa template .aep có sẵn, thay thế asset/nhân vật/UI/text tiếng Việt trong template AE, hoặc gắn SFX tự động theo keyframe của file .aep.
---

# AE Template Customizer — Tùy Biến Sâu Template `.aep` Thương Mại & Tự Động Hóa SFX

Skill này chuyên xử lý **Nhánh B (Khai thác & Tùy biến file `.aep` có sẵn từ Envato / VideoHive)** với hàng chục precomp lồng nhau, giúp tự động hóa hoàn toàn việc khảo sát cấu trúc, thay thế nhân vật/giao diện/chữ tiếng Việt và chèn hiệu ứng âm thanh (SFX) khớp từng nhịp chuyển động.

---

## Chạy trên máy Linux này

- Python: `~/.venvs/video-skills/bin/python` (máy không có lệnh `python`/`py`; venv có numpy, scipy, matplotlib, opencv, scikit-image, Pillow, fontTools, resvg-py, faster-whisper). Lệnh `python …` trong tài liệu chạy bằng đường dẫn này.
- ffmpeg/ffprobe 8.1 ở `~/.local/bin` (libx264, FFV1, ProRes 4444, loudnorm, ebur128).
- Đường dẫn Windows trong tài liệu đã đổi sang Linux: `F:\` → `/media/vmiz/Over Powers/`, `D:\` → `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/` (bản sao lưu ổ D ngày 2026-10-28). Ổ USB `Over Powers` phải đang gắn. `E:\` không có trên máy; tài nguyên thay thế ở `/home/vmiz/Thanh/Media/TNEDIT/` (`02_SFX`, `08_Nhac_Nen`, `01_Font`, `06_B-Roll`…).
- Skill này sửa template `.aep` thương mại nên **chỉ chạy trên After Effects (Windows)**: EffectCraft 0.17 trên máy này không mở được `.aep`. Trên Linux chỉ chạy được phần Python (`parse_aep_timings.py`, `prepare_sfx_pro.py`, `generate_ae_sfx_jsx.py`). Đường dẫn bên trong `.jsx` sinh ra giữ dạng Windows.
- `prepare_sfx_pro.py` đọc kho SFX ở bản sao lưu ổ D. `generate_ae_sfx_jsx.py` ghi ra `/media/vmiz/Over Powers/add_sfx_t5.jsx` (chính là `F:\add_sfx_t5.jsx` trên Windows); đường dẫn bên trong file `.jsx` sinh ra vẫn là Windows.

---

## 1. Cấu Trúc Thư Mục Trong Skill

- **`scripts/parse_aep_timings.py`** — Công cụ đọc file nhị phân `.aep` hoặc dữ liệu trích xuất để tính toán mốc thời gian toàn cục (`Global Timing`) của từng phân cảnh (`Scene 01..13`), xác định chính xác từng layer bắt đầu ở giây thứ mấy trên timeline tổng.
- **`scripts/customize_template_assets.jsx`** — Script ExtendScript chạy ngầm trong After Effects thực hiện:
  1. Thay thế các bộ phận nhân vật 2D/3D (`Head`, `Body`, `Hand`, `Arm`, `Character Precomp`) bằng asset thương hiệu mới.
  2. Thay thế ảnh chân dung (Portrait Avatars) và vẽ mới/thay thế các bảng giao diện UI (`Dashboard`, `Card`, `Chart`, `Toggle`) đa tầng.
  3. Chuyển đổi font chữ sang font hỗ trợ tiếng Việt, tắt `All Caps`, nới `Leading` và sửa lỗi **Range Selector** làm rụng/mất chữ cuối câu khi dịch sang tiếng Việt dài hơn câu gốc tiếng Anh.
- **`scripts/prepare_sfx_pro.py`** — Công cụ xử lý hậu kỳ âm thanh bằng `ffmpeg`:
  - Chuyển đổi toàn bộ SFX sang chuẩn **WAV 48.000 Hz, 24-bit (`pcm_s24le`), Stereo**.
  - Áp bộ lọc **Low-pass `11.000 Hz`** cho các tiếng *Whoosh / Swish* để tạo chất âm **Warm High-Tech SaaS UI** (ấm, sang, không chói gắt tai).
  - Cắt gọn khoảng lặng đầu file để đỉnh xung (`Transient Peak`) nổ đúng frame hình.
- **`scripts/generate_ae_sfx_jsx.py`** — Tự động sinh mã `.jsx` chèn toàn bộ các lớp âm thanh SFX vào đúng comp và đúng mốc thời gian keyframe, tự động đặt mức `Audio Levels` chuẩn công nghiệp (`-6.0 dB` đến `-9.5 dB`).
- **`data/kho_sfx_do.csv`** — Bảng dữ liệu đo đạc thông số kỹ thuật (`duration`, `sample_rate`, `max_dBFS`, `mean_dBFS`, `peak_offset_ms`) của toàn bộ kho SFX dùng để tính toán bù trễ (`pre-roll offset`).
- **`references/README-template-5.md`** — Tài liệu hướng dẫn chi tiết quy trình thực chiến trên dự án 13 cảnh (`template 5.aep`).

---

## 2. Quy Trình 4 Bước Tùy Biến Template `.aep` Thương Mại

### Bước 1: Quét Cấu Trúc & Tính Thời Gian Toàn Cục (`parse_aep_timings.py`)
Các template Envato thường lồng 4–6 tầng precomp (`Main Comp -> Scene Comp -> Content Comp -> Asset Comp`). Trước khi sửa, chạy:

```bash
python scripts/parse_aep_timings.py
```

Script sẽ lập bản đồ toàn bộ các `CompItem`, tính toán `Global Start Time = Parent startTime + Child startTime` và xuất danh sách tọa độ thời gian của từng cảnh, từng hiệu ứng chuyển cảnh và từng cụm chữ.

### Bước 2: Thay Thế Nhân Vật, UI & Chữ Tiếng Việt (`customize_template_assets.jsx`)
Khi thay nội dung tiếng Việt và asset thương hiệu vào template:
1. **Sửa lỗi mất chữ cuối câu do Range Selector:** Nhiều template Envato đặt `Range Selector -> Mode = Index` (theo số ký tự cố định của câu tiếng Anh gốc). Khi thay bằng câu tiếng Việt dài hơn, các chữ vượt quá chỉ số `End` sẽ bị tàng hình! Script tự động chuyển `Units` sang `Percentage (100%)` hoặc cập nhật lại `End` bằng đúng `text.length`.
2. **Thay thế Asset bảo toàn Keyframe:** Sử dụng `layer.replaceSource(newFootageItem, false)` hoặc vẽ đè `ShapeLayer` bên trong precomp lá (`leaf precomp`) để giữ nguyên 100% keyframe `Position`, `Scale`, `Rotation`, `Puppet Pin` và `Null Parent` của tác giả template.
3. Chạy script tự động qua dòng lệnh:

```powershell
& "C:\Program Files\Adobe\Adobe After Effects 2026\Support Files\AfterFX.exe" -noui -m -s "$.evalFile('F:/SKILL/ae-template-customizer/scripts/customize_template_assets.jsx')"
```

### Bước 3: Chuẩn Hóa Kho SFX Phong Cách High-Tech SaaS UI (`prepare_sfx_pro.py`)
Chạy script chuẩn hóa âm thanh trước khi đưa vào After Effects:

```bash
python scripts/prepare_sfx_pro.py
```

- Mọi file SFX được đồng bộ về `48kHz / 24-bit Stereo`.
- Các âm chuyển cảnh (*Whoosh / Swoop*) được lọc cắt tần số rít trên `11kHz` và fade-out mượt mà, không bị cụt đuôi.

### Bước 4: Sinh Mã & Bơm Tự Động SFX Khớp Keyframe (`generate_ae_sfx_jsx.py`)
1. Chạy `python scripts/generate_ae_sfx_jsx.py` để sinh script `.jsx` gắn âm thanh.
2. Quy tắc đặt mức âm lượng (`Audio Levels` trong AE):
   - **Chuyển cảnh chính (Scene Transition Whoosh):** `-6.0 dB` đến `-7.0 dB` (đặt sớm trước điểm cắt cảnh `80ms – 150ms` dựa theo `peak_offset_ms` trong `data/kho_sfx_do.csv` để đỉnh gió trùng khít frame chuyển cảnh).
   - **Thẻ UI / Hình khối bật lên (UI Pop / Card Appear):** `-7.5 dB` đến `-8.5 dB`.
   - **Chữ gõ / Nút bấm / Vi tương tác (Text Tick / Click / Chime):** `-8.5 dB` đến `-9.5 dB`.
3. Mật độ vàng: **2.5 – 3.5 SFX / giây** (chỉ gắn vào chuyển động chính có trọng lượng thị giác, không gắn tràn lan vào mọi hạt bụi phụ gây rác tai).

<!-- ===== /file: ae-template-customizer/SKILL.md ===== -->

<!-- ===== file: ae-template-customizer/references/README-template-5.md ===== -->

# Ca mẫu nhánh B: sửa template mua về "template 5.aep"

Bốn script do một phiên agent khác viết (23–26/10/2026) khi sửa template thương mại 13 cảnh `template 5.aep` thành video quảng cáo OPA Agent. Kết quả là `OPA_Agent_Promo_2026.aep`.
- Gói giữ **nguyên nội dung** bốn script để tham khảo.
- Script chưa được chạy lại để kiểm khi đóng gói.
- Chưa có ghi nhận Minh đã duyệt video của ca này.

| Script | Việc | Đầu vào cứng trong code |
|---|---|---|
| `parse_aep_timings.py` | đọc báo cáo cấu trúc template, tính giây và khung toàn cục của mọi cảnh, comp con | `C:\Users\Public\OPA-AE-20261021\T5-REPORT-DECODED.txt` |
| `customize_template_assets.jsx` | nạp chân dung, logo, thẻ UI, nhạc; đổi bảng màu; thay chữ tiếng Việt; sửa Range Selector | `/media/vmiz/Over Powers/video AE/template intro/video edit teamplate/template 5.aep`, thư mục `OPA_T5_Assets`, file nhạc trên ổ F |
| `prepare_sfx_pro.py` | chọn 78 cue SFX bộ uisfx-themes, đổi WAV 48 kHz 24-bit, `volume=-4.5dB,lowpass=11000`, tính startTime căn đỉnh | danh sách cue và mốc cảnh của template 5, kho SFX ổ D, thư mục ra ổ F |
| `generate_ae_sfx_jsx.py` | sinh JSX đưa SFX vào comp `00_OPA_SFX_Master` và từng cảnh, gain −6 … −9,5 dB | JSON cue của bước trên, đường dẫn template 5 |

## Phải sửa trước khi dùng cho dự án khác

1. **Đường dẫn cứng** ở đầu mỗi script: đổi sang dự án mới.
2. **Chạy trên bản sao, trong phiên AE riêng** (sổ tay mục 3). Hai file JSX được viết để chạy trong phiên AE đang mở:
   - lưu đè lên chính `template 5.aep`;
   - JSX sinh ra gọi `openInViewer()` trước bước lưu. Hàm này cần giao diện, nên xóa nó khi chạy headless.
3. **`customize_template_assets.jsx` bỏ qua lỗi im lặng** (`catch (err) {}`). Thêm dòng ghi lỗi ra file báo cáo trước khi dùng.
4. **Báo cáo cấu trúc** mà `parse_aep_timings.py` đọc do hai file không có trong gói tạo ra: `inspect_t5_aepx.jsx` và `decode_aepx.py`, cùng ở `C:\Users\Public\OPA-AE-20261021`.
   - Hai file này giấu báo cáo vào comment của file .aepx, vì phiên chạy của họ không ghi file được.
   - Trong phiên riêng thì ghi thẳng ra file JSON, như `references/template-audit/scripts/export-projects.jsx`.
5. **Mức âm** (−4,5 dB trước, gain −6 … −9,5 dB, nhạc −8 dB) là số đặt cho riêng bộ âm của ca này, chưa đo trên bản xuất. Dùng làm điểm xuất phát, rồi đo và master theo sổ tay mục 9.
6. **Không dùng `run_ae_script.py` của ca này.** File đó đẩy script vào phiên AE đang mở bằng cách đổi tiến trình cha (parent PID), trái với luật không chạy vào phiên AE của Minh.
7. **Lưu:** đổi `app.project.save(projFile)` thành `app.project.save()` trên bản sao đã mở.
8. **Viết lại phần riêng của template 5:** tên comp, vòng lặp 13 cảnh, `SCENE_STARTS`, danh sách 78 cue, thông số 3840×2160 / 30 fps / 55,5 s.

## Chỗ làm trái luật của skill (sửa trước khi dùng lại)

| Chỗ | Trái luật nào | Sửa |
|---|---|---|
| `customize_template_assets.jsx` nhập thẳng file MP3 nhạc ngoài (`atlasaudio-upbeat-corporate-617614.mp3`) | sổ tay 9.3, 9.6: nhạc phải là WAV 48 kHz; video OPA tự tổng hợp nhạc | đổi sang WAV; video OPA dùng nhạc tự tổng hợp hoặc hỏi Minh |
| Font `BeVietnamPro-Black` | ngoài bộ font duyệt của OPA | dùng ExtraBold, hoặc hỏi Minh thêm font vào bộ |
| Vài dòng chữ mở đầu bằng chữ thường | luật viết hoa chữ cái đầu mọi dòng (URL được miễn) | viết hoa chữ cái đầu |
| Màu #00E0FF, #05122E và giữ `Buttons_Glow_Color` | 5 màu OPA, không glow | đổi về 5 màu OPA, tắt glow, trừ khi Minh duyệt giữ |
| `prepare_sfx_pro.py` đổi WAV bằng `-ac 2` | sổ tay 9.2: `-ac 2` hạ mỗi kênh 3 dB | giữ số kênh gốc, hoặc nhân đôi kênh nguyên mức |
| `prepare_sfx_pro.py` lấy M từ CSV thay vì đo lại file WAV đã xử lý | gain phải tính trên file thật đưa vào AE (sổ tay 9.2) | đo lại sau khi đổi WAV và lọc |
| Nhiều khối `catch` rỗng, cả trong JSX được sinh ra | mọi lỗi phải ghi vào báo cáo (sổ tay 3.4) | ghi lỗi ra file |

<!-- ===== /file: ae-template-customizer/references/README-template-5.md ===== -->
