# Nguồn footage — API, giới hạn, giấy phép

Kiểm 2026-11-01. Mã nguồn tham khảo cho phần Pexels / Pixabay: `harry0703/MoneyPrinterTurbo` (MIT, `app/services/material.py`).

| Nguồn | Cách gọi | Key | Giới hạn | Giấy phép |
|---|---|---|---|---|
| Kho TNEDIT | chỉ mục CLIP `06_B-Roll/.footage_index/` (`index.json` + `index.npz`, 3 khung / clip) | — | — | theo `_nguon.json` / README danh mục từng thư mục |
| Pexels | `GET https://api.pexels.com/videos/search?query=&orientation=portrait&per_page=15`, header `Authorization: <key>` → `videos[].video_files[] {width, height, link}`, `image` (ảnh xem trước), `duration`, `user.name` | `PEXELS_API_KEY` (miễn phí, pexels.com/api) | 200 yêu cầu / giờ, 20.000 / tháng | Pexels License: miễn phí, dùng thương mại, không bắt ghi nguồn; không bán lại nguyên clip |
| Pixabay | `GET https://pixabay.com/api/videos/?key=&q=&per_page=20&safesearch=true` → `hits[].videos.{large,medium,small,tiny} {url, width, height, thumbnail}`, `duration`, `tags`, `user`, `pageURL` | `PIXABAY_API_KEY` (miễn phí, pixabay.com/api/docs) | 100 yêu cầu / 60 s; giữ kết quả 24 h | Pixabay Content License: miễn phí, dùng thương mại, không bắt ghi nguồn |
| Pexels ảnh | `GET https://api.pexels.com/v1/search?query=&orientation=portrait&per_page=15` → `photos[] {id, width, height, alt, photographer, src.{original, medium}}`; tải `original?auto=compress&cs=tinysrgb&h=2560` | `PEXELS_API_KEY` | như trên | Pexels License — **chưa chạy thật** (máy chưa có key; parser kiểm bằng dữ liệu mẫu) |
| Pixabay ảnh | `GET https://pixabay.com/api/?key=&q=&image_type=photo&orientation=vertical&per_page=20&safesearch=true` → `hits[] {webformatURL (640), largeImageURL (1280), imageWidth, imageHeight}` | `PIXABAY_API_KEY` | như trên | Pixabay Content License — **chưa chạy thật** |
| Mixkit | không có API: trang `https://mixkit.co/free-stock-video/<từ>/` (24 clip, chỉ 1 từ; trang tìm nhiều từ tải bằng JS nên không đọc được). Clip: `https://assets.mixkit.co/videos/<id>/<id>-1080.mp4` (hoặc `-720.mp4`), ảnh xem trước `<id>-thumb-360-0.jpg` | — | đọc ít (1–2 trang / cảnh); giao diện đổi → nguồn lỗi, bị bỏ qua | Mixkit Stock Video Free License: dùng thương mại, không bắt ghi nguồn |
| Muse | muse2api local `http://127.0.0.1:18610/v1` (khoá `~/.config/muse/env`): `POST /images/generations {model: muse-image, size: 9:16, async}` → `POST /videos {model: muse-video, seconds: 1–60, image: <data URL khung đầu>}`; hỏi tiến độ `GET …/<id>` | `MUSE_API_KEY` (đã có) | 2 tài khoản → chạy 2 việc / lần; ảnh ~30 s, video 5 s ~1–2 phút, 10 s ~2,3 phút, 30 s ~4,8 phút, 60 s ~7,5 phút (đo 2026-11-02); ra 720×1280 hoặc 704×1248 24fps có tiếng (skill bỏ tiếng, đổi 30fps; đặt lên timeline 1080×1920 cần phóng ~150%); ≥ 30 s bối cảnh trôi (đạo cụ / góc máy đổi dần); **video trả lại kết quả cũ khi prompt + độ dài trùng, kể cả khác ảnh khung đầu** (đo 2026-11-02: đoạn 6 trùng từng byte đoạn 2) → skill gắn `(shot <sha1 ảnh>)`; đôi khi không bám ảnh khung đầu (lệch 45/255) → kiểm + tạo lại | tạo bằng AI — xem kỹ trước khi dùng |

Ghi chú:
- Điểm CLIP ViT-B-32 (đã cộng thưởng hướng khung / kho) giữa câu tả và ảnh thường 0,20–0,37: kết quả đúng nghĩa đo được ≥ 0,28, lạc nghĩa ~0,24–0,25 → ngưỡng Muse 0,27 (đo 2026-11-01 trên THCN04).
- Ảnh xem trước Pexels / Pixabay là khung đại diện, có thể khác phần còn lại của clip: xem `sheet.jpg` (khung giữa clip đã tải).
- Lỗi tải không in URL có key (Pixabay đặt key trong URL): `media.http_get` chỉ báo phần trước `?`.
