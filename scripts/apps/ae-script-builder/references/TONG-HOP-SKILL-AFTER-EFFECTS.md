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
