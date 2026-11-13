# Preset render talking head — Kênh AI Doanh Nghiệp (anh Huy)

Chốt ngày 26/10/2026: dùng **bản B — photo avatar sân golf** làm chuẩn cho toàn bộ 30 kịch bản.

## Thông số đã khóa

| Mục | Giá trị |
|-----|---------|
| Avatar look | `761364fad106369de1c3ada3994aee9c` — "AHuy - Golf Cart CEO" |
| Avatar group | `d2ca30ee30804228ada59ec6a0f596e3` — nhóm "AHuy" (chung với digital twin cũ) |
| Voice | `09bed03ed2984542836268ac73ffc18c` — voice clone AHuy, tiếng Việt, nam |
| Khung hình | 9:16, 1080p, fit `cover` |
| Engine | Avatar IV (mặc định) |
| Expressiveness | `medium` |
| Motion prompt | executive nói thẳng camera, quay đầu tự nhiên, giữ eye contact |

API: `POST https://api.heygen.com/v3/videos`, header `X-Api-Key`.

## Cách render một bài

```powershell
$env:HEYGEN_KEY = "<api key>"
python render.py 5                 # chỉ in lời thoại, KHÔNG tốn credit
python render.py 5 --yes           # render thật + tự tải về folder này
```

Luôn chạy lần 1 không có `--yes` để đọc lại lời thoại. Script tự bóc markdown,
nhưng **không tự sửa** ba thứ sau — phải tự tay chỉnh rồi render bằng `--text`:

1. **Ký tự `%`** — viết thành chữ. `90%` → "chín mươi phần trăm".
2. **Từ khóa comment viết liền** — `TUDUYAI` → "TƯ DUY AI", `HUANLUYEN` → "HUẤN LUYỆN".
3. **Chữ số nhạy cảm** — nghe lại đoạn có số, giọng đọc đôi khi đọc sai.

Quy trình khi cần sửa tay:

```powershell
python render.py 5 > bai05-huanluyen-loi-thoai.txt   # rồi mở file ra sửa
python render.py 5 --text bai05-huanluyen-loi-thoai.txt --yes
```

## Chi phí thực tế

Đo trên 2 video đầu, mỗi video 1 phút 40 giây ở 1080p:

- **~130 plan credit + ~$6.6 ví** cho mỗi video.
- Số dư sau bài #03: **243 credit, $12.15** — chỉ đủ thêm khoảng 2 bài.

Cách giảm nếu chạy hết 30 bài:

- Hạ `RESOLUTION` xuống `"720p"` trong `render.py`.
- Chỉ render phần talking head (00:00–00:25 và 00:55–01:15). Đoạn giữa 00:25–00:55
  là screen demo, bị che 70–80% khung hình theo brief kênh — render mặt ở đó là phí tiền.

## Phần API không làm được

- **Phụ đề**: HeyGen không trả `.srt` cho preset này. Phải tự làm bằng CapCut/Premiere.
- **Screen demo**: đoạn 00:25–00:55 phải tự quay màn hình rồi ghép picture-in-picture.
  Quy chuẩn kênh: zoom 150–200%, khoanh đỏ các con số tài chính / thời gian.

## File trong folder

- `render.py` — script render, đọc preset ở đầu file.
- `kich-ban-30-bai.json` — trọn bộ 30 kịch bản lấy từ trang dashboard.
- `bai03-tuduyai-B-photo-golf.mp4` — bản chuẩn đã duyệt.
- `bai03-tuduyai-A-digital-twin.mp4` — bản so sánh, dùng digital twin cũ (đã loại).
