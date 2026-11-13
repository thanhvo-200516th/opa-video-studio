# Hướng Dẫn Sử Dụng Skill Dựng Video Talking-Head (Bản 1.2.3)

Tài liệu dành cho chủ kênh vận hành hệ thống dựng video ngắn tự động (TikTok, Reels, Shorts) từ video người nói HeyGen hoặc quay điện thoại.

---

## 1. Skill Này Làm Gì

Skill tự động hóa toàn bộ khâu hậu kỳ dựng video ngắn chuẩn 9:16 từ video avatar thô, đảm bảo chất lượng phát hành đồng đều mà không cần dựng thủ công.

### 1.1 Đầu Vào
- Video avatar nói: file `D:/MMO/Van Minh AI/Vid Heygen/<n>/<n>.mp4` hoặc file lẻ `<n>.mp4`.
- Kịch bản chuẩn: kịch bản biên tập từ tài liệu «60 kịch bản HeyGen v3».

### 1.2 Đầu Ra
Mỗi video được xuất tại thư mục `D:/MMO/Van Minh AI/Vid Heygen/<n>/edit-r1.2.3/out/`:
- `final.mp4`: video thành phẩm hoàn chỉnh (đầy đủ phụ đề, âm thanh, nhạc nền, B-roll).
- `final-nobgm.mp4`: video thành phẩm không nhạc nền (để tự thêm nhạc trên TikTok/Reels).
- `final-social.mp4`: video tối ưu chuẩn nền tảng xã hội (xử lý âm lượng hai lượt).
- `out/verify/VERDICT.md`: biên bản kiểm định chất lượng tự động đạt chuẩn phát hành.
- `out/verify/contact_sheet.png`: ảnh tổng hợp 12 khung hình đại diện (lưới 4×3) để kiểm tra nhanh bằng mắt.

### 1.3 Bốn Lớp Dựng
1. **Phụ đề động (Kinetic Subtitles)**: phụ đề 3 tầng (dòng nhỏ trên, chữ đập hero ở giữa, dòng nhỏ dưới), tự động ngắt nhịp theo giọng nói và bảo vệ vùng mặt người nói.
2. **B-roll AI**: tự động chèn hình ảnh hoặc video clip minh họa toàn màn hình đè dưới phụ đề ở những câu phù hợp, tổng cộng khoảng 25–40% thời lượng.
3. **Hiệu ứng âm thanh (SFX)**: tự động chèn tiếng whoosh, pop, click, impact chuẩn theo chuyển động chữ và cảnh cắt.
4. **Nhạc nền (BGM)**: tự động căn chỉnh âm lượng nhạc dìm dưới giọng nói, tránh đè giọng avatar.

### 1.4 Tám Mục Kiểm Định Chất Lượng (V1–V8)
Trước khi bàn giao, hệ thống tự động kiểm tra nghiêm ngặt 8 tiêu chí:
- **V1 (Khóa phiên bản)**: quy tắc dựng khớp đúng bản release đã đóng băng và đúng cấu hình card.
- **V2 (Kiểm tra dựng)**: phụ đề, hiệu ứng âm thanh và vùng an toàn chữ không lỗi kỹ thuật.
- **V3 (Đồng bộ âm thanh)**: khớp pha âm thanh, độ lệch từng tiếng động so với giọng dưới ngưỡng cho phép.
- **V4 (Âm lượng chuẩn)**: `final.mp4` và `final-nobgm.mp4` ở −16 LUFS, `final-social.mp4` ở −14 LUFS (sai số ±0,5), kèm trần đỉnh True-Peak.
- **V5 (Tính toàn vẹn dữ liệu)**: mọi file trung gian khớp nhật ký trạng thái STATE.md theo chuỗi nguồn gốc.
- **V6 (Báo cáo biên tập)**: đầy đủ báo cáo biên tập và không có bản vá tạm ngoài luồng.
- **V7 (Kiểm tra thị giác)**: ghép lưới 12 khung hình đại diện để người kiểm duyệt xem xét trực quan.
- **V8 (Kiểm định B-roll)**: B-roll thực sự hiển thị trên video render cuối, không phẳng hình và khớp danh mục tài nguyên.

---

## 2. Chuẩn Bị Máy

Hệ thống vận hành thông qua nền tảng Hermes Agent với các vai trò chuyên biệt.

### 2.1 Các Profile Cần Dùng
- **`opa-operator`**: điều phối viên chạy lệnh điều hành, theo dõi tiến độ lô và nhận lệnh duyệt từ chủ kênh.
- **`opa-editor`**: chuyên viên dựng video phụ trách lập kế hoạch (PLAN) và xử lý kỹ thuật (BUILD).
- **`opa-verifier`**: chuyên viên kiểm định độc lập chấm điểm V1–V8 và xem xét thị giác (VERIFY).

### 2.2 Gateway Gốc Duy Nhất
Mọi việc điều phối Kanban yêu cầu đúng một dịch vụ Gateway chạy ở profile mặc định.
- **Kiểm tra trạng thái gateway**:
  Chạy lệnh chỉ đọc:
  ```bash
  hermes gateway list
  ```
  Dòng `default` bắt buộc có dấu `✓` kèm `PID …`. Mọi dòng profile phụ `opa-*` phải là `✗ … not running`.
  *Ghi chú (kiểm 2026-09-27):* bản Hermes hiện tại cho gateway gốc phục vụ luôn các profile, nên dòng `opa-*` có thể hiện `✓` mà **không có PID**. Như vậy vẫn đúng (chỉ một dispatcher). Chỉ sai khi một dòng `opa-*` có `PID` riêng, tức một gateway thứ hai đang chạy.
- **Khởi động gateway gốc khi chưa chạy**:
  Khởi động qua tác vụ Windows (gõ trong Git Bash):
  ```bash
  MSYS_NO_PATHCONV=1 schtasks /run /tn Hermes_Gateway
  ```
  *Lưu ý:* Tuyệt đối không gõ `hermes gateway run` trong terminal của agent hoặc operator vì sẽ kích hoạt sai profile.

### 2.3 Biến Môi Trường
- `NINEROUTER_API_KEY`: biến môi trường bắt buộc cấu hình trên máy để cấp quyền sinh ảnh và video B-roll qua cổng 9router. Chỉ khai báo tên biến trong cấu hình môi trường, không ghi hay in giá trị khóa ra màn hình hoặc tài liệu.

### 2.4 Phần Mềm Nền Tảng Yêu Cầu
Theo đúng đặc tả của skill:
- **Python**: phiên bản 3.10+ (cần thư viện `faster-whisper`, `numpy`).
- **Node.js**: phiên bản 18+.
- **ffmpeg**: công cụ xử lý âm thanh và video đa phương tiện.
- **Bộ font chữ**: Cinematic fonts pack đặt tại `D:/MMO/Font/Cinematic fonts pack`.

---

## 3. Thư Mục Và File

Cấu trúc lưu trữ dữ liệu và theo dõi sản xuất được tổ chức quy củ:

### 3.1 Thư Mục Gốc
- `VID_ROOT = D:/MMO/Van Minh AI/Vid Heygen`: thư mục chứa toàn bộ video gốc HeyGen và các dự án sản xuất.

### 3.2 Thư Mục Quản Lý Lô Sản Xuất (`_batches/<bNN>/`)
Mỗi đợt sản xuất quản lý trong thư mục `D:/MMO/Van Minh AI/Vid Heygen/_batches/<bNN>/` (ví dụ `b01`):
- `batch_manifest.json`: hồ sơ danh mục các video thuộc lô, phân loại mẫu và trạng thái khởi tạo.
- `mapping.csv`: bảng đối chiếu tự động giữa file video avatar và mục kịch bản chuẩn v3.
- `PREP-SHEET.md`: bảng tổng hợp phiếu chuẩn bị (trạng thái video, nhu cầu B-roll, cảnh báo rủi ro).
- `APPROVALS.md`: nhật ký ghi nhận nguyên văn mọi lời phê duyệt từ chủ kênh theo từng mốc.
- `cards.json`: danh sách ánh xạ các card Kanban của lô kèm mã định danh card (`t_…`).
- `kpi.jsonl`: nhật ký tổng hợp chỉ số kỹ thuật và chất lượng sau khi hoàn tất kiểm định.

### 3.3 Thư Mục Dự Án Dựng Của Từng Video (`<n>/edit-r1.2.3/`)
Nằm tại `D:/MMO/Van Minh AI/Vid Heygen/<n>/edit-r1.2.3/`:
- `STATE.md`: nhật ký bất biến ghi nhận mọi thay đổi và mã băm sha8 của từng tệp dữ liệu trung gian.
- `plan.json`: bản kế hoạch dựng (hook, điểm nhấn, liệt kê, CTA, B-roll) do agent lập.
- `edit.json`: cấu trúc kỹ thuật chi tiết tự động ráp từ `plan.json`, tuyệt đối không sửa tay.
- `out/`: thư mục chứa video xuất xưởng (`final.mp4`, `final-social.mp4`, `final-nobgm.mp4`, `QA.json`, `EDITOR-REPORT.md`, `verify/VERDICT.md`, `verify/contact_sheet.png`).

### 3.4 Bảng Kanban Điều Phối
- Board `vm-heygen-<bNN>` (ví dụ `vm-heygen-b01`): bảng theo dõi điều phối tiến độ toàn bộ các card công việc của lô qua hệ thống Hermes Kanban.

---

## 4. Luồng Một Lô Từ Đầu Tới Cuối

Quy trình sản xuất gồm 8 bước tuần tự được thực thi chính xác:

```text
[P0: Lập lô] 
    ↓
[PREP] → [APPROVE-PREP] 
    ↓
[Phase videos] 
    ↓
[Canary: INTAKE → PLAN → BUILD → VERIFY] 
    ↓
[APPROVE-CANARY] 
    ↓
[Các video còn lại: INTAKE → PLAN → BUILD → VERIFY] 
    ↓
[KPI & Gửi user duyệt] 
    ↓
[Đóng lô]
```

### Bước 1: P0 — Lập Lô
- **Ai làm**: `opa-operator` tương tác với chủ kênh.
- **Lệnh thực thi**:
  1. Tạo board Kanban cho lô:
     ```bash
     hermes kanban boards create vm-heygen-b01 --name "Van Minh AI · HeyGen b01"
     ```
  2. Nạp dữ liệu và kiểm tra ban đầu:
     ```bash
     PYTHONIOENCODING=utf-8 python "C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/scripts/intake.py" --batch b01 --videos 16,21,27,51,53,59,60 --transcriber whisper --preset standard --rules 1.2.3
     PYTHONIOENCODING=utf-8 python "C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/scripts/make_cards.py" --batch b01 --board vm-heygen-b01 --check
     PYTHONIOENCODING=utf-8 python "C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/scripts/make_cards.py" --batch b01 --board vm-heygen-b01
     ```
- **User cần làm**: cung cấp danh sách video muốn dựng trong lô (tối đa 10 video).

### Bước 2: PREP → APPROVE-PREP-<k>
- **Ai làm**: `opa-editor` lập phiếu `prep-<k>.json` và dựng `PREP-SHEET.md`. Sau đó `opa-operator` chuyển thông tin tới chủ kênh.
- **Lệnh thực thi**:
  Khi chủ kênh duyệt, operator ghi nhận lời duyệt vào comment và `APPROVALS.md`, rồi chạy:
  ```bash
  hermes kanban --board vm-heygen-b01 complete <id APPROVE-PREP-<k>>
  ```
- **User cần làm**: đọc `PREP-SHEET.md`, xác nhận trạng thái các video, gắn cờ `claim_gate` nếu cần thử nghiệm thực tế hoặc loại bỏ video lỗi đọc kịch bản.

### Bước 3: Khởi Tạo Pha Video (Phase videos)
- **Ai làm**: `opa-operator` (chỉ chạy sau khi toàn bộ card `APPROVE-PREP-<k>` đã hoàn tất).
- **Lệnh thực thi**:
  ```bash
  PYTHONIOENCODING=utf-8 python "C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/scripts/make_cards.py" --batch b01 --board vm-heygen-b01 --phase videos --check
  PYTHONIOENCODING=utf-8 python "C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/scripts/make_cards.py" --batch b01 --board vm-heygen-b01 --phase videos
  ```
- **User cần làm**: không cần can thiệp, hệ thống tự động sinh chuỗi dựng cho video canary và các video còn lại.

### Bước 4: Dựng Video Canary Thử Nghiệm
- **Ai làm**: các agent chạy chuỗi INTAKE → PLAN → BUILD → VERIFY hoàn toàn tự động cho riêng 1 video canary đầu tiên để nghiệm thu trước chất lượng.
- **User cần làm**: chờ video canary hoàn tất quá trình kiểm định tự động.

### Bước 5: APPROVE-CANARY (Duyệt Video Mẫu Đầu Tiên)
- **Ai làm**: `opa-operator` gửi video canary và phiếu kiểm định cho chủ kênh.
- **Lệnh thực thi**:
  Sau khi chủ kênh đồng ý chất lượng, operator ghi nhận lời duyệt vào comment và `APPROVALS.md`, rồi chạy:
  ```bash
  hermes kanban --board vm-heygen-b01 complete <id APPROVE-CANARY>
  ```
- **User cần làm**: nghe và xem kỹ video canary (xem hình ảnh, kiểm tra chữ phụ đề, B-roll, âm thanh); đưa ra quyết định duyệt hoặc yêu cầu chỉnh sửa chi tiết kèm mốc thời gian.

### Bước 6: Dựng Các Video Còn Lại Của Lô
- **Ai làm**: các worker xử lý tuần tự từng video qua 4 bước INTAKE → PLAN → BUILD → VERIFY.
  - `opa-editor` xử lý từng card một (giới hạn 1 card song song để tránh xung đột tài nguyên máy).
  - Khâu render video và phiên âm Whisper xếp hàng tự động qua khóa phần cứng `_batches/.heavy.lock`.
- **User cần làm**: theo dõi tiến độ tổng thể, không cần thao tác thủ công.

### Bước 7: Thu Thập KPI Và Gửi Video Duyệt
- **Ai làm**: `opa-operator` chạy định kỳ sau mỗi video xong khâu VERIFY hoặc khi hoàn tất toàn bộ lô:
  ```bash
  PYTHONIOENCODING=utf-8 python "C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/scripts/collect_kpi.py" --batch b01
  ```
- **User cần làm**: nhận các video được đánh dấu `GỬI USER: …` (gồm canary, video mẫu 1/5, video có cảnh báo CONCERN hoặc có cờ `claim_gate`), xem kiểm tra và phản hồi duyệt hoặc nhận xét.

### Bước 8: Đóng Lô Sản Xuất
- **Ai làm**: `opa-operator` thực hiện sau khi chủ kênh đã duyệt toàn bộ video xuất bản.
- **Lệnh thực thi**:
  ```bash
  PYTHONIOENCODING=utf-8 python "C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/scripts/collect_kpi.py" --batch b01 --prune-node-modules
  ```
  Lệnh này dọn dẹp các thư mục `node_modules` tạm của các video đã hoàn thành tốt (`VERIFIED` / `DONE_WITH_CONCERNS`), giải phóng dung lượng ổ đĩa.
- **User cần làm**: xác nhận đã nhận đủ video và hoàn tất đợt duyệt.

---

## 5. Việc Của Anh (User) Ở Mỗi Mốc Duyệt

Vai trò của chủ kênh là chốt duyệt chất lượng tại các mốc then chốt để đảm bảo nội dung chính xác.

### 5.1 Duyệt Phiếu PREP (`APPROVE-PREP-<k>`)
Khi operator gửi bảng tổng hợp `PREP-SHEET.md`:
- Xem xét trạng thái từng video: video nào ghi `needs_rerender` (HeyGen đọc lỗi chữ giữ chỗ) thì tạm bỏ qua chờ quay lại; video nào ghi `needs_input` thì phản hồi quyết định.
- Gắn cờ `claim_gate: true` cho các video có câu nói cần thử nghiệm thực tế (ví dụ so sánh bản miễn phí vs trả phí), case study học viên, số liệu chưa kiểm chứng nguồn hoặc tin tức thiếu ngày phát hành. Các video này vẫn dựng bình thường nhưng bắt buộc không đăng tải trước khi xác nhận thực tế.
- Trả lời duyệt: trả lời ngắn gọn, nêu rõ các yêu cầu điều chỉnh nếu có.

### 5.2 Trường Hợp Muốn Sửa Phiếu PREP
Nếu chưa đồng ý phiếu chuẩn bị:
- **Tuyệt đối không complete card**: operator không được đóng card `APPROVE-PREP-<k>`.
- Gửi yêu cầu sửa rõ ràng từng video (ví dụ: video 16 để needs_input chờ quay màn hình, video 21 ghép mục kịch bản số 12).
- Operator sẽ ghi nhận nguyên văn yêu cầu vào comment card và `_batches/<b>/APPROVALS.md` dưới dạng:
  ```markdown
  - APPROVE-PREP-1 — 2026-09-20 — sửa phiếu: "Sửa mấy chỗ:
  - video 16 để needs_input, chờ tôi quay màn hình
  - video 21 ghép mục v3 số 12"
  ```
- Operator chạy lại quy trình thử lại:
  ```bash
  PYTHONIOENCODING=utf-8 python "C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/scripts/make_cards.py" --batch b01 --board vm-heygen-b01 --retry PREP-1
  ```
  Agent sẽ đọc lại đúng lời dặn này để xuất bản `PREP-SHEET.md` mới xin duyệt lại.

### 5.3 Duyệt Video Canary (`APPROVE-CANARY`)
Canary là video đầu tiên xuất xưởng của lô để nghiệm thu toàn diện chất lượng:
- **Cách xem và nghe chuẩn**:
  - Mở `out/final.mp4` và đọc `out/verify/VERDICT.md` kèm theo.
  - Nghe bằng loa điện thoại ở mức nửa âm lượng, sau đó nghe lại bằng tai nghe.
  - Nghe ở môi trường yên tĩnh rồi thử ở môi trường có tiếng ồn.
  - Nghe trọn một lượt không nhìn thanh timeline để cảm nhận nhịp điệu, sau đó mới ghi mốc phút:giây (`mm:ss`) nếu thấy điểm chưa ưng ý.
  - Kiểm tra B-roll AI: hình ảnh minh họa có phù hợp không, có xuất hiện chữ/logo rác không.
- Phản hồi duyệt:
  - Đồng ý: `"Duyệt canary video N của lô bNN."`
  - Chưa duyệt: `"Chưa duyệt canary video N: <lỗi thấy được + mốc giây>. Sửa rồi dựng lại."`

### 5.4 Duyệt Cả Lô Và Các Video Cần Xem
Sau khi các video hoàn tất, operator gửi các video thuộc diện `GỬI USER`:
- Duyệt trọn lô hoặc duyệt có điều kiện:
  - `"Duyệt cả lô bNN."`
  - `"Duyệt lô bNN trừ video X: <lỗi + mốc giây>. Làm lại riêng video đó."`
- Lời chê của chủ kênh sẽ được ghi vào `_batches/<b>/FEEDBACK.jsonl` để làm căn cứ cải tiến bộ quy tắc cho các lô kế tiếp.

### 5.5 Nguyên Tắc Ghi Lời Duyệt Bất Biến
Mọi câu trả lời của chủ kênh đều được operator chép **nguyên văn, không diễn giải, không tóm tắt**:
1. Dán y nguyên vào comment của card Kanban tương ứng.
2. Dán thành một mục mới vào cuối file `_batches/<b>/APPROVALS.md` dưới mục `## Lời duyệt` với cấu trúc:
   `- APPROVE-<TÊN> — YYYY-MM-DD: <lời user nguyên văn>`
3. Chỉ sau khi ghi nhận đầy đủ hai nơi trên, operator mới được bấm complete card.

---

## 6. Khi Có Sự Cố

Bảng tra cứu nguyên nhân và hướng xử lý nhanh khi gặp sự cố trong quá trình sản xuất:

| Triệu chứng | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| Card bị block `needs_input` ở bước INTAKE | Độ khớp kịch bản và giọng nói < 0,80 hoặc số thứ tự kịch bản bị lệch | Chủ kênh kiểm tra lại kịch bản chuẩn; operator chạy `intake.py --update` nếu cần, rồi chạy `--retry <n>:INTAKE`. |
| Card bị block `transient` hoặc có run `timed_out` | Quá thời gian quy định (render, npm, ffmpeg treo) hoặc process con chạy nền chiếm khóa `.stage.lock` / `.heavy.lock` | Operator chạy PowerShell diệt sạch tiến trình con sót lại, rồi dùng `--retry <n>:<STAGE>` (xem chi tiết bên dưới). Tuyệt đối không unblock thủ công. |
| Card bị block `capability` | Lỗi kỹ thuật hệ thống (lỗi lint_sfx, lệch pha xcorr, lỗi dò mặt) | Chuyển cho dev xử lý mã nguồn skill; video tạm dừng chờ bản vá. |
| Card PLAN bị block `needs_input` sau 3 vòng | Bản kế hoạch `plan.json` kiểm tra `--check` thất bại sau 3 vòng lặp | Operator mở lần thử thứ hai (`a2`) giao cho model mạnh hơn; `a2` kế thừa `plan.json` có sẵn để tinh chỉnh tiếp. |
| Cảnh báo `STRAY_SCRIPT` | Agent tự tiện viết script lạ bên ngoài vào thư mục dự án | Lệnh `--check` tự động bắt lỗi; agent hoặc operator xóa sạch các file script lạ đó rồi chạy lại. |
| Lỗi `FACE_ROOM` ở bước BUILD | Chữ phụ đề đè lên miệng hoặc mắt người nói | Bản 1.2.3 tự động áp hero một hàng (tối đa 2 vòng), ghi dòng PLAN vào `STATE.md` rồi dừng sớm để tránh cắt 420s; agent chỉ cần chạy lại lệnh BUILD. Nếu vẫn lỗi, operator mở lại PLAN với phương án `breaks` hoặc `hero` gợi ý. |
| Render lỗi «No frame found at position» | Máy thiếu RAM khi Remotion render (script in dòng «GỢI Ý: Remotion thiếu bộ đệm khung…») | Kiểm RAM còn trống và NonPaged pool; NonPaged pool cao thì khởi động lại máy, rồi dựng lại bằng `--retry <n>:BUILD`. Không phải lỗi dữ liệu. |
| Clip B-roll động rơi về ảnh tĩnh (V8 concern) | Lỗi 403 spending-limit của xAI qua 9router hoặc mạng chập chờn | Hệ thống tự động chuyển mượt sang ảnh tĩnh AI (`ag/nano-banana`), video vẫn hoàn thành đạt chuẩn `DONE_WITH_CONCERNS`. Kiểm tra lại hạn mức tài khoản 9router. |
| Ảnh B-roll có chữ tiếng Anh hoặc logo | Prompt B-roll vô tình chứa từ nhạy cảm hoặc model ảnh tự sinh chữ | Operator mở lại bước PLAN bằng `--retry <n>:PLAN`, agent tăng trường `"v"` lên 1 và viết lại prompt tả cảnh thuần túy không chứa chữ. |
| Video trạng thái `needs_rerender` | Kịch bản HeyGen còn sót chữ giữ chỗ `[CÔNG CỤ]`, `[TIN MỚI]` hoặc đọc chỉ dẫn chuyển động | Đưa video vào danh sách quay lại trên HeyGen; không đưa vào lô hiện tại mà gom vào các lô tiếp theo sau khi đã có file chuẩn. |
| Lỗi `PLAN_DRIFT` ở bước VERIFY | Có người sửa tay trực tiếp vào file `edit.json` | Operator mở lại PLAN mới; nguyên tắc bất di bất dịch: **agent ghi `plan.json`, hệ thống tự ráp `edit.json`**. |

### Quy Tắc Vàng: Không Bao Giờ Unblock Lần Hai
Theo luật của Hermes Kanban, card đã block tuyệt đối không được gõ lệnh unblock thủ công. Mọi quy trình khắc phục sự cố phải thực hiện qua cơ chế `--retry`:
```bash
PYTHONIOENCODING=utf-8 python "C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/scripts/make_cards.py" --batch b01 --board vm-heygen-b01 --retry <n>:<STAGE>
```
Script sẽ tự động tạo lần thử mới `a<k+1>` và in rõ các lệnh cập nhật liên kết (`link` card mới với card duyệt, `unlink` card cũ, và `archive` card cũ). Làm đúng theo thứ tự được in ra.

### Xử Lý Tiến Trình Con Chạy Sót Sau `timed_out`
Khi Hermes báo run kết thúc dạng `timed_out`, các tiến trình con `python`, `node`, `ffmpeg` có thể vẫn đang chạy ngầm và giữ khóa máy. Trước khi chạy lệnh `--retry`, operator phải chạy hai lệnh PowerShell sau (ví dụ xử lý cho video 16, card cũ `t_abc12345`):
1. Liệt kê các tiến trình sót:
   ```powershell
   MSYS_NO_PATHCONV=1 powershell -NoProfile -Command 'Get-CimInstance Win32_Process | Where-Object { $_.Name -match "^(python|node|ffmpeg)" -and ($_.CommandLine -like "*Vid Heygen?16?edit-r1.2.3*" -or $_.CommandLine -like "*stage.py*t_abc12345*") } | Select-Object ProcessId,Name,CommandLine | Format-List'
   ```
2. Buộc dừng toàn bộ cây tiến trình:
   ```powershell
   MSYS_NO_PATHCONV=1 powershell -NoProfile -Command 'Get-CimInstance Win32_Process | Where-Object { $_.Name -match "^(python|node|ffmpeg)" -and ($_.CommandLine -like "*Vid Heygen?16?edit-r1.2.3*" -or $_.CommandLine -like "*stage.py*t_abc12345*") } | ForEach-Object { taskkill /F /T /PID $_.ProcessId }'
   ```
Sau khi chạy lại lệnh 1 thấy trống hoàn toàn, mới thực hiện lệnh `--retry`.

---

## 7. B-Roll AI

Quy chuẩn dựng B-roll cắt cảnh toàn màn hình bằng trí tuệ nhân tạo (spec 1.2.0–1.2.3):

### 7.1 Nguyên Tắc Vận Hành
- **Loại tài nguyên**: sinh tự động trong bước BUILD `broll_assets`. Dùng ảnh tĩnh sinh bằng model `ag/nano-banana` kết hợp hiệu ứng đẩy nhẹ (push) hoặc tối đa 1 video clip chuyển động sinh bằng `xai/grok-imagine-video` cho mỗi video (chi phí clip khoảng 0,35 USD/video).
- **Vị trí và thời lượng**: B-roll dựng đè toàn bộ khung hình người nói (full coverage) trong khoảng 2–4 giây mỗi slot, âm thanh giọng nói và phụ đề vẫn chạy liên tục. Tổng thời lượng B-roll nằm trong khoảng 25–40% tổng độ dài video để không làm lu mờ gương mặt người nói (cổng kiểm tra B04/BROLL_COVER_OVER).
- **Ruling R200**: B-roll AI chỉ đóng vai trò minh họa bối cảnh/ví dụ, không bao giờ được coi là bằng chứng kết quả thật. Video thuộc nhóm `heavy` bắt buộc gắn cờ `claim_gate: true`.
- **Ruling R201**: Không in nhãn AI trực tiếp lên video; việc công bố nhãn AI sẽ được thực hiện qua tính năng gắn nhãn của nền tảng mạng xã hội khi đăng bài.

### 7.2 Quy Chuẩn Viết Prompt B-Roll
- Prompt viết bằng **tiếng Anh**, độ dài từ **8 đến 60 từ**.
- Tập trung tả cảnh vật, bối cảnh, hành động cụ thể minh họa trực tiếp câu đang nói.
- Ứng dụng hoặc trang web phải mô tả chung: «a generic unbranded app» hoặc «an unbranded interface».
- Kết quả công việc tả bằng cảm xúc, nét mặt hoặc hành động thực tế, không vẽ biểu đồ số liệu.
- Nhân vật nếu có phải nhất quán về độ tuổi, trang phục, mái tóc. Cùng một sản phẩm xuất hiện ở nhiều ô B-roll phải chép nguyên văn cụm mô tả chi tiết cả kiểu dáng và màu sắc, không nhắc tên thương hiệu.

### 7.3 Danh Sách Từ Cấm Trong Prompt B-Roll (`BANNED`)
Để ngăn ngừa model ảnh sinh ra nhãn rác, văn bản lỗi hoặc vi phạm bản quyền, cấm triệt để các từ sau trong prompt (chép nguyên văn từ biến `BANNED` trong `releases/1.2.3/scripts/thlib/broll_plan.py`):

`logo`, `watermark`, `text`, `subtitle`, `side-by-side`, `split screen`, `comparison`, `label`, `labels`, `caption`, `captions`, `annotation`, `annotations`, `notes`, `graph`, `chart`, `metrics`, `analytics`, `statistics`, `engagement`, `youtube`, `tiktok`, `facebook`, `instagram`, `iphone`, `macbook`, `apple`, `samsung`, `google`, `game character`, `note`, `checklist`, `checklists`, `checkbox`, `checkboxes`, `written`, `bullet`, `bullets`, `handwritten`, `handwriting`, `chat`, `chatting`, `message`, `messages`, `messaging`, `texting`.

---

## 8. Những Điều Không Bao Giờ Làm

Các điều cấm kỵ tuyệt đối trong quá trình vận hành hệ thống (OPERATOR.md §8, spec §10.1):

1. **Không tự viết `edit.json` hay tự build/render thủ công**: agent chỉ ghi `plan.json`, hệ thống tự ráp `edit.json`.
2. **Không tự dán số vào card, comment, hay summary**: mọi số liệu (thời lượng, dB, ms, mã băm sha…) chỉ lấy từ kết quả script in ra.
3. **Không ghi file vào `<n>/edit*`**: khu vực này chỉ dành cho các worker INTAKE/PLAN/BUILD/VERIFY xử lý (ngoại lệ duy nhất là lệnh dọn dẹp `collect_kpi.py --prune-node-modules` khi đóng lô).
4. **Không bao giờ unblock card lần thứ hai**: khi card bị block, luôn dùng cơ chế `--retry` để tạo lần thử mới `a<k+1>` và lưu trữ (archive) card cũ.
5. **Không chạy code ngoài luồng**: không dùng `python -c`, `node -e`, `execute_code`, hay viết script tạm ngoài thư mục release. Chỉ chạy qua các script chính quy trong thư mục `releases/<ver>/scripts/`.
6. **Không complete card `APPROVE-*` trước khi chủ kênh duyệt**: card phê duyệt chỉ được đóng sau khi đã có phản hồi chính thức từ chủ kênh và đã chép nguyên văn vào `APPROVALS.md`.
7. **Không tiết lộ khóa bí mật**: tuyệt đối không in hoặc lưu giá trị `NINEROUTER_API_KEY`.

---

## 9. Cập Nhật Skill Lên Bản Mới

Quy trình nâng cấp phiên bản đảm bảo hệ thống bất biến và không xung đột giữa các đợt dựng:

### 9.1 Phát Triển Và Đóng Băng Bản Phát Hành
- Toàn bộ công việc phát triển và kiểm thử phiên bản mới được thực hiện tại repository:
  `D:/Vibe Coding/AI Video/th-skill-1.1` trên nhánh tính năng tương ứng `rulebook-x.y.z`.
- Các bản phát hành cũ bắt buộc phải đóng băng bất biến (kiểm tra tự động qua bộ test `test_release_frozen.py`), đảm bảo các dự án cũ có thể tái lập kết quả chính xác bất kỳ lúc nào.

### 9.2 Đồng Bộ Vào Thư Mục Skill Thật
Sau khi toàn bộ bài kiểm tra vượt qua:
- Đưa mã nguồn lên thư mục skill thật đang dùng của Hermes Agent:
  `C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head`
  trên nhánh `main` và đánh dấu tag phiên bản `vx.y.z`.
- Đẩy kho lưu trữ lên máy chủ GitHub cá nhân:
  `github.com/minhnv0807/dung-video-talking-head` (chế độ riêng tư - private).

### 9.3 Cập Nhật Con Trỏ SOUL.md Của opa-operator
Cập nhật đúng dòng trỏ phiên bản trong file cấu hình `SOUL.md` của profile điều phối (OPERATOR.md mục M0):
```text
dung-video-talking-head@1.1 — lô vm-heygen-*: chỉ làm theo C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/stages/OPERATOR.md; task packet và quy trình riêng trong SOUL này KHÔNG áp dụng cho các lô đó.
```

### 9.4 Nguyên Tắc An Toàn Khi Triển Khai
Chỉ được phép triển khai phiên bản mới khi **không có card nào đang chạy trên hệ thống**. Việc thay đổi file `MANIFEST.sha256` hoặc mã nguồn giữa chừng khi một lô đang sản xuất sẽ làm các video đang dựng bị lệch mã khóa kiểm tra `rules.lock` và dẫn đến đánh rớt kiểm định V1 (`REJECTED`).

---

## 10. Prompt Mẫu

Chép nguyên văn các mẫu câu lệnh dưới đây để tương tác điều phối và vận hành hệ thống:

### 10.1 Dán vào Claude Code (Claude làm điều phối, giao việc cho agent OPA Hermes)

Mở lô mới:
  Mở lô sản xuất bNN của skill dung-video-talking-head bản 1.2.3 cho các video <danh sách số, tối đa 10>.
  Giao việc cho các agent OPA Hermes qua hermes kanban (không dùng subagent Claude). Giám sát kĩ: xem đủ mọi ảnh B-roll
  theo picture_lock, xem contact sheet từng video, ghi nguyên văn lời duyệt vào APPROVALS.md. Báo tôi khi cần duyệt PREP,
  canary và cả lô.

Hỏi tiến độ:
  Lô bNN đang tới đâu? Liệt kê card đang chạy, card bị khoá kèm lý do, và video nào đã VERIFY xong.

Duyệt phiếu PREP:
  Tôi duyệt phiếu PREP lô bNN. (Thêm nếu cần: gắn claim_gate cho video X vì cần thử thật trước khi đăng; bỏ qua video Y, chờ render lại.)

Duyệt canary:
  Duyệt canary video N của lô bNN.
  — hoặc — Chưa duyệt canary video N: <lỗi thấy được + mốc giây>. Sửa rồi dựng lại.

Duyệt cả lô:
  Duyệt cả lô bNN.
  — hoặc — Duyệt lô bNN trừ video X: <lỗi + mốc giây>. Làm lại riêng video đó.

Card bị khoá:
  Card <id> trên board vm-heygen-bNN bị khoá. Đọc log worker, tìm nguyên nhân gốc, xử lý bằng --retry (không unblock),
  chỉ hỏi tôi khi cần quyết định.

Ảnh B-roll có chữ / sai nội dung:
  Video N lô bNN, ảnh <Bk> ở giây <t> có chữ tiếng Anh (hoặc: không khớp câu đang nói). Thay prompt không chữ rồi dựng lại video đó.

Sửa skill sau một lô:
  Tổng hợp các lỗi lặp lại của lô bNN thành spec bản 1.2.x. Giao OPA làm (tối đa 3 card), test nhanh và test chậm xanh
  thì triển khai vào skill thật, push lên GitHub, rồi mở lô sau.

Đóng lô:
  Đóng lô bNN: chạy collect_kpi với --prune-node-modules sau khi tôi đã trả lời mọi video.

Video đã render lại trên HeyGen:
  Video N đã render lại trên HeyGen (file <đường dẫn>). Kiểm khớp kịch bản rồi đưa vào lô tiếp theo.

### 10.2 Dán vào chat opa-operator (Hermes) khi không dùng Claude Code

  Làm theo C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/stages/OPERATOR.md:
  mở lô bNN với các video <danh sách>, preset standard. Dừng ở mỗi card APPROVE và chờ tôi duyệt; chép nguyên văn lời duyệt
  vào _batches/bNN/APPROVALS.md trước khi complete card.
