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
