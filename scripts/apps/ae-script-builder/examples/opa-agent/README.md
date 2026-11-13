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
