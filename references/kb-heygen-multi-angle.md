# HeyGen nhiều góc quay (look) và ngân hàng A-roll dùng lại

Mục đích: mỗi video có 2-4 góc của cùng một người dẫn (cho nhịp A-roll bớt đơn điệu), và câu thoại lặp giữa nhiều video chỉ phải render một lần.
Script: `scripts/heygen_looks.py` (liệt kê/chia look), `scripts/render_heygen_aroll.py` (render, ước lượng, bank, link).

## 1. Khái niệm (HeyGen API v3)
- Một nhân vật là một "group"; mỗi trang phục/tư thế/góc là một "look" của group đó.
- `avatar_id` khi tạo video phải là LOOK id, không phải group id.
- `GET /v3/avatars/looks?group_id=...` trả `id`, `name`, `preview_image_url`, `supported_api_engines`.
- `POST /v3/videos`: `{type:"avatar", avatar_id, voice_id, script, aspect_ratio:"9:16", background?, engine?}`; theo dõi bằng `GET /v3/videos/{id}`.
- Look không hỗ trợ engine đang chọn sẽ báo `invalid_parameter`. Vì vậy script chỉ gửi `engine` khi look hỗ trợ, nếu không thì chọn engine đầu tiên look hỗ trợ.
- Chưa có tài liệu chọn "góc" theo tham số: các góc phải là look có sẵn (tạo trong HeyGen hoặc tải ảnh lên thành look của cùng group).

## 2. Khoá API
- CHỈ lấy từ biến môi trường `HEYGEN_API_KEY` hoặc `--key-file <file>` người dùng đưa lúc chạy.
- Không ghi khoá vào file, log, báo cáo, prompts. `looks.json`, `heygen_render_log.json` không chứa khoá.
- Không có khoá: chỉ chạy được DRY-RUN, `--estimate`, `pick`, `link`.

## 3. Quy trình một video
1. Liệt kê look của người dẫn, lưu `looks.json`:
   `python scripts/heygen_looks.py list --group <group_id> --out looks.json --key-file ~/k.txt`
   (hoặc `--all` cho mọi look của tài khoản). In ra: id, tên, URL ảnh xem trước, engine hỗ trợ.
2. Xem ảnh xem trước, giữ 2-4 look hợp video (cùng người, khác góc).
3. Chia look cho shot A-roll (không để 2 shot A-roll liền nhau cùng look):
   `python scripts/heygen_looks.py pick --looks looks.json --videos KB08=4 --angles 3`
   Hoặc để render tự chia: `--looks looks.json --assign auto --angles 3`.
4. Hoặc đặt tay trong `prompts_heygen_aroll.json`: thêm `"avatar_id": "<look_id>"` (cũng nhận `look_id`) cho từng shot; thêm `"background"` nếu cần nền riêng.
   Thứ tự ưu tiên: `avatar_id` trong shot > `--assign auto` > `--avatar-id` mặc định.
5. Xem trước và ước lượng (không tốn credit):
   `python scripts/render_heygen_aroll.py <thư mục video> --looks looks.json --assign auto --estimate --usd-per-min <giá>`
6. Render thật (tốn credit): thêm `--yes` (và `--key-file`). Có thể thêm `--engine <tên>`, `--background <màu/URL>`.

## 4. Nhiều video (lô)
- Trỏ vào thư mục tổng chứa các thư mục video: `python scripts/render_heygen_aroll.py <thư mục tổng> --looks looks.json --assign auto --angles 3`
- Số lần dùng mỗi look được cân bằng trên cả lô (chênh nhau tối đa 1 shot); kết quả cố định giữa các lần chạy, kể cả khi resume.
- Chia look tính trên MỌI shot A-roll (kể cả shot đã render), nên chạy lại không làm đổi look của shot còn lại.

## 5. Ngân hàng A-roll dùng lại
`bank.json` (do planner sinh): `[{"bank_id":"B01","text":"...","look_id":"<look>","used_in":["KB08","KB09"]}]`
(tuỳ chọn `duration_hint_sec`). Trong `prompts_heygen_aroll.json` của mỗi video, shot dùng lại mang `"bank_id":"B01"`.
1. Render mỗi câu đúng một lần vào `bank/<bank_id>.mp4` (cạnh bank.json, hoặc `--bank-dir`):
   `python scripts/render_heygen_aroll.py --bank bank.json --yes --key-file ~/k.txt`
2. Đưa vào từng video đúng tên `<STT>_a-roll-<N>.mp4` theo `bank_id` trong prompts:
   `python scripts/render_heygen_aroll.py link bank.json <thư mục tổng> [--symlink] [--force]`
- `link` chỉ chép vào video có tên chứa một mã trong `used_in` (nếu `used_in` có giá trị); video khác bị báo `skip`.
- File đích đã có thì bỏ qua (dùng `--force` để ghi đè). Thiếu file bank hoặc `bank_id` lạ: báo `missing-...`, mã thoát 1.

## 6. An toàn chi phí và chạy lại
- Mặc định DRY-RUN: in từng shot, look, engine, câu thoại; không gọi API.
- `--yes` mới gọi thật. File `.mp4` đã có (> 10 KB) được bỏ qua, trừ `--force`. Lỗi một shot thì dừng, chạy lại sẽ tiếp từ shot còn thiếu.
- `--estimate`: bảng shot và tổng giây theo look; chỉ có cột tiền khi truyền `--usd-per-min` / `--credits-per-min` (đơn giá mặc định chưa biết, hãy kiểm trên trang giá chính thức của HeyGen trước khi dự toán).
- Câu thoại còn chữ số, `%`, `/` bị cảnh báo (đọc sai tiếng Việt): sửa trước khi `--yes`.

## 7. Giới hạn đã biết
- Chưa có lệnh tạo look từ ảnh (`POST /v3/avatars` kiểu photo); hiện tạo look trong HeyGen rồi `list`.
- Định dạng giá trị `background` theo tài liệu HeyGen hiện hành; script chuyển nguyên chuỗi (hoặc object trong JSON của shot).
- Giữ nhất quán giọng: dùng cùng `--voice-id` cho mọi look của một người dẫn.
