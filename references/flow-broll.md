# Tạo B-roll bằng Google Flow (D3, D15) — quy trình mặc định từng bước

**Công cụ tạo B-roll mặc định chính (D3, D15):** mục tiêu **100 %** thời lượng B-roll (tối thiểu **≥ 95 %**; footage thật / stock ngoại lệ tối đa **2–5 %**, trần cứng ≤ 5 %); tuân giới hạn lặp **D8 (`≤ 2 lần / video, ≤ 2 video`)**. Trình duyệt Cindy là kênh phụ khi MCP `google-flow` lỗi; Muse local chỉ là dự phòng khẩn nếu Google Flow không khả dụng và người dùng đồng ý. Số đo ngày 2026-11-14 trên 2 tài khoản (PRO và ULTRA; chạy thử 3 cảnh OPA05 song song); giao diện tiếng Việt. Tên tài khoản có thể hiện đảo thứ tự họ / tên ở hai chỗ. Flow đổi giao diện thường xuyên: nhãn khác thì `snapshot` lại và tìm nút cùng nghĩa, không đoán toạ độ.

Có **2 nhánh thực thi Google Flow**:
- **Nhánh 1 (Mặc định ưu tiên khi có MCP `google-flow` — gọi qua `call_mcp_tool` với `ServerName="google-flow"`):** Khi dùng MCP `google-flow`, mọi tương tác đi qua các tool `flow_*`, không mở `labs.google/fx/tools/flow` bằng trình duyệt khác.
  - **Bước 0 (3-Agent chuẩn bị Prompt & Kiểm tra tài khoản):**
    1. Chạy **Agent 1 (Script Semantic Analyst)** đọc toàn bộ `tts_text`, tách đoạn `> 7,5 s` hoặc 2 vế đối lập thành sub-beats, viết `script_beat_vi` đời thực (CẤM ẩn dụ CGI trừu tượng).
    2. Chạy **Agent 2 (5-Layer Anti-Plastic Prompt Architect)** viết `layers` (`l1_shot_subject`..`l5_camera_motion`) ghép thành `prompt` `18–95` từ đạt H5.
    3. Chạy **Agent 3 (Cổng 1 — Lint)** + `$PY scripts/broll_fix.py plan --engine flow`, `lint` (strict layers & anti-plastic) và `prepare --source flow`.
    4. Gọi `flow_list_accounts` (`readyForGeneration=true` → lấy `defaultAccountId`; chưa kết nối → `flow_begin_account_connection` → dừng chờ người dùng bấm *Connect Flow* trên Chromium hiện *"Session sent"* → `flow_complete_account_connection`) → `flow_inspect_account` (kiểm tra `models`, `aspectRatios`, `visibleDurations`, `outputs`, `upscales`, số dư tín dụng; số dư < tổng tín dụng ở `plan` → báo, dừng, D3).
  - **Bước 1–2 (Tạo video 720p x2):** Gọi `flow_generate_video` với `prompt` lõi đã qua `broll_fix.py lint` (không nối đuôi câu cấm), `outputDirectory: "<thư_mục_video>/_google_raw"`, `fileName: "<STT>_b-roll-<M>_raw"`, `model: "omni-flash"`, `aspectRatio: "9:16"`, `durationSeconds` (theo `plan`), `outputs: 2`, `upscale: "none"`, `download: true`, `referenceFiles: []`, `confirmCreditSpend: true`. Giữ `jobId`; nếu `status="processing"` thì poll `flow_job_status(jobId, waitSeconds=10)` cho tới khi xong (cấm gọi lại `flow_generate_video` khi đang `processing`).
  - **Bước 3 (Agent 3 — Visual Critic trên 2 bản 720p):** Kiểm tra **cả 2 bản 720p** tải về theo bảng tiêu chí loại trừ Anti-Plastic & Khớp kịch bản ở Mục 3 bên dưới.
  - **Bước 4 (Nâng 1080p, tải & chuẩn hoá):** Gọi `flow_upscale_video(jobId, factor="1080p", confirmCreditSpend=true)` → poll `flow_job_status` nếu cần → `flow_download_job(jobId)` lưu về `<thư_mục_video>/_google_raw/` → chạy `$PY scripts/broll_fix.py normalize <thư mục video>/_google_raw/<file> <thư mục video>/<STT>_b-roll-<M>.mp4 [--mark flow]`, rồi sang Mục 5 (`verify`).
- **Nhánh 2 (Kênh phụ qua trình duyệt Cindy `mcp__cindy_browser` khi MCP `google-flow` lỗi hoặc không khả dụng):** Thực hiện theo hướng dẫn bấm UI chi tiết ở các mục 0–5 dưới đây.

## 0. Trước khi bấm gì
1. `$PY scripts/broll_fix.py plan <thư mục video> --engine flow [--speed 1.10]` → mỗi cảnh: giây cần đặt, tín dụng (mặc định x2), tổng tín dụng.
2. Prompt từng cảnh đã qua `broll_fix.py lint` (0 lỗi) và `prepare --source flow` (sao lưu clip cũ, ghi nguồn `flow`). Gõ vào Flow đúng `prompt_core` — KHÔNG nối đuôi "NO text…" của Muse, không thêm câu cấm ("no text, no logos"): Flow không có ô loại trừ, câu cấm hay bị bỏ qua hoặc gợi ra chính thứ bị cấm.
3. Tài khoản: dùng trình duyệt Cindy (Linux: người dùng tự đăng nhập trong cửa sổ Chrome của Cindy — `request_input_handoff` chỉ có trên macOS) (`mcp__cindy_browser`, chế độ hiện tại). Mở `https://labs.google/fx/tools/flow`, bấm nút "Thông tin về tài khoản" để xem tên tài khoản, nhãn gói (PRO) và số "tín dụng Google Flow". Báo người dùng tên tài khoản đang dùng. Muốn dùng đúng Chrome của người dùng thì cần chế độ "Trình duyệt của tôi" (`setBackend user-browser`) — chỉ chạy được khi Chrome đã cài và bật tiện ích Cindy; chưa có thì báo người dùng, không tự cài, không chép cookie.
4. Số dư < tổng tín dụng ở bước 1 → báo, dừng. Không mua thêm, không bật dùng thử, không bấm "Nâng cấp" (D3). Gặp trang đăng nhập → `request_input_handoff`, không tự gõ mật khẩu.

## 1. Cài đặt (mỗi cảnh kiểm lại, Flow nhớ lựa chọn cũ)
Mở một dự án (hoặc "Dự án mới"), bấm nút cài đặt cạnh ô nhập ("Điều kiện kích hoạt cài đặt", hiện dạng `Video · 720p · N giây ▯ xN`):

| Mục | Chọn | Ghi chú |
|---|---|---|
| Loại | **Video** | |
| Chế độ | **Thành phần**, KHÔNG đính kèm ảnh | đính ảnh khuôn mặt người nói = đưa nguồn lên Google → cần người dùng đồng ý riêng cho video đó (A4) |
| Khung | **9:16** | |
| Mô hình ("Chọn nhóm mô hình") | **Omni 1.2 Flash** | Omni 1.1 Flash, Veo 3.1 Fast / Quality ngừng 2026-12-05; Veo 3.1 Quality 8 s = 100 tín dụng / bản |
| Độ phân giải | **720p** | 360p chỉ để thử nhanh |
| Độ dài (thanh trượt 3–15 s) | số giây `plan` in | `input[type=range]` giá trị = giây − 3 |
| Số bản | **x2** | chọn bản đúng hơn; cả 2 hỏng → làm lại 1 lần với prompt đã sửa |

Giá (720p): 3 tín dụng / s đến 10 s, 6 tín dụng / s cho phần 11–15 s; nâng 1080p miễn phí đến 10 s, 1 tín dụng / s phần vượt. Dòng "Quá trình tạo sẽ tốn N tín dụng" đổi theo mô hình → đọc lại SAU khi chọn mô hình, phải khớp `plan` trước khi bấm tạo. Nút "Bắt đầu tạo" nằm sát nút cài đặt: bấm theo ref / nhãn, không theo toạ độ.

Cài đặt: "Trả về video không có âm thanh" (nút bánh răng của dự án) để BẬT. "Hình mờ có thể nhìn thấy" (bảng tài khoản): tuỳ tài khoản — PRO ở Việt Nam bị khoá BẬT ("Khu vực của bạn yêu cầu…") → `normalize --mark flow`; ULTRA cho tắt (2026-11-14: tắt sẵn) → để TẮT, normalize KHÔNG `--mark` (xoá dấu khi không có dấu chỉ làm nhoè một ô). Ghi trạng thái vào báo cáo.

## 2. Tạo
1. Bấm ô "Bạn muốn tạo những gì?", gõ `prompt_core`, bấm "Bắt đầu tạo".
2. Chờ: mỗi lệnh `wait` tối đa 30 s; một bản 6–10 s mất khoảng 1–3 phút. Có thể gửi cảnh sau trong lúc cảnh trước đang tạo.
3. Bản xong hiện thành thẻ trong lưới dự án. Thẻ (và nút "Dự án mới") thường KHÔNG có ref trong snapshot → bấm bằng `act` `evaluate` (tìm phần tử theo nhãn / ảnh) hoặc `clickCoords` lấy từ snapshot `labels`. Trang chỉnh sửa (`/project/<id>/edit/<id>`) có 2 ảnh nhỏ ở đầu = 2 bản x2; mỗi bản xem và tải riêng.
4. Nhiều cảnh cùng lúc: mỗi tab một "Dự án mới" riêng; KHÔNG quá 2–3 tab tự động cùng tạo trên một tài khoản — 2026-11-14 chạy 5 tab song song thì Flow báo "hoạt động bất thường", mọi thẻ "Không thành công". Bị chặn → mở "Dự án mới" (đã gỡ được); vẫn chặn → nghỉ 5 phút, gửi tối đa 2 cảnh một lúc.
5. Tiết kiệm: xem 2 bản ở 720p trên trang chỉnh sửa, chỉ tải 1080p bản được chọn (bản loại không cần nâng).

## 3. Chọn bản (Agent 3 — Visual Critic bắt buộc, bằng mắt, cho TỪNG bản 720p)
Chụp màn hình trang chỉnh sửa hoặc tải 2 bản 720p về rồi xem `qa/broll_check_sheet.jpg`. **Loại ngay bản** nếu có BẤT KỲ lỗi nào sau đây:
- **Nhựa / Lộ AI / CGI:** da sáp láng mịn mất lỗ chân lông, ánh sáng neon/cyberpunk gắt, vật thể phát sáng trừu tượng (khối lập phương/lăng kính/thanh ray thép CGI), chuyển động gimbal trơn tuột siêu thực;
- **Giải phẫu & Vật lý lỗi:** ngón tay méo/thừa ngón, mặt biến dạng, đồ vật phi vật lý (ly xuyên bàn, chuột méo), người xuất hiện hoặc biến mất đột ngột;
- **Chữ / Logo / Giao diện:** chữ, số, logo hãng (cả trên viền / lưng màn hình, laptop, cốc, áo), biển hiệu; màn hình / tivi / máy tính bảng / bảng trắng hiện rõ nội dung (dashboard, giao diện, bản vẽ, bảng tính); giấy in biểu đồ đọc được;
- **Sai nhân vật:** người được gọi là "mình", "anh", founder, CEO lộ rõ mặt (AI vẽ người lạ, không phải người nói);
- **Chuyển cảnh ngầm:** cắt cảnh hoặc chuyển cảnh giữa clip;
- **Lệch nghĩa `anchor_quote`:** hình không minh hoạ đúng nghĩa đen đời thực câu nói của cảnh đó.
Ghi vào báo cáo: cảnh, bản chọn, lý do loại bản còn lại. Cả 2 bản đều hỏng → Agent 2 sửa `layers` theo lỗi thấy được (vd đưa màn hình ra khỏi khung, bỏ từ nhựa, đổi sang hành động đời thực khác), `lint` lại, tạo lại tối đa 1 lần; vẫn hỏng → báo người dùng, giữ CẢNH BÁO D1.

## 4. Tải về và chuẩn hoá
1. Trang chỉnh sửa → nút tải xuống → **"1080p Đã tăng độ phân giải"** (không chọn "720p Kích thước gốc", GIF, 4K). Nâng 1080p ≤ 10 s miễn phí (11 s: 1 tín dụng); Flow nâng mất 1–2,5 phút rồi file mới xuất hiện. Bản 1080p là 1080×1920, 24 fps, vẫn có rãnh tiếng (normalize bỏ).
2. Trình duyệt Cindy lưu vào `/tmp/openclaw/downloads/` (tên `<uuid>-<Tiêu_đề>_<mã>.mp4`), thư mục DÙNG CHUNG: ghi `ls` trước khi bấm tải, lấy đúng file MỚI xuất hiện sau đó (không dùng `ls -t | head` khi có cảnh khác đang tải), chép sang `<thư mục video>/_google_raw/<STT>_b-roll-<M>_v<1|2>.mp4`.
3. `$PY scripts/broll_fix.py normalize <thư mục video>/_google_raw/<file> <thư mục video>/<STT>_b-roll-<M>.mp4 [--mark flow]` → 1080×1920, 30 fps (Flow ra 24 fps), không tiếng; `--mark flow` (chỉ khi bản tải về CÓ dấu ngôi sao góc dưới phải) xoá dấu. In CẢNH BÁO < 1080 → tải lại bản 1080p.
4. Xem góc dưới phải của 1 khung sau chuẩn hoá (crop `x 680–1080, y 1520–1920`): còn dấu → báo, không giao.

## 5. Kiểm sau
Đã tạo lại cảnh với prompt khác lượt đầu → ghi prompt cuối: `$PY scripts/broll_fix.py prepare <thư mục video> --prompts <file prompt cuối> --source flow --keep-clips` (không chuyển clip; manifest khớp clip thật, `scene_check` hết cảnh báo sai).

`$PY scripts/broll_fix.py verify <thư mục video> --scenes … [--speed 1.10]` (0 FAIL) → mở `qa/broll_check_sheet.jpg`, áp lại bảng ở mục 3 → `scene_check` (0 FAIL). Báo cáo ghi: tài khoản, mô hình, giây, số bản, tín dụng đã dùng, số dư còn lại, bản chọn.

## Viết prompt cho Flow (Quy trình 3 Agent + 5 Tầng Anti-Plastic H5)
Xem đặc tả đầy đủ tại [`references/master-video-prompt-architecture.md`](master-video-prompt-architecture.md) (Mục 5b) và hướng dẫn chuyển đổi kịch bản qua 3 Agent tại [`references/script-to-flow-broll.md`](script-to-flow-broll.md). Các quy tắc thực chiến bắt buộc cho Google Flow (`omni-flash`, T5-XXL/Gemma):
- **Quy trình 3 Agent trước khi gọi Flow:**
  1. **Agent 1 (Script Semantic Analyst):** Đọc toàn bộ `tts_text`, tách đoạn `> 7,5 s` hoặc có 2 vế đối lập thành sub-beats, viết `script_beat_vi` mô tả **cảnh đời thực cụ thể chứng minh câu nói** — CẤM ẩn dụ CGI trừu tượng (khối phát sáng, lăng kính, bánh răng, lõi năng lượng, thanh ray thép trượt hộp đèn).
  2. **Agent 2 (5-Layer Anti-Plastic Prompt Architect):** Viết đủ 5 tầng `layers` (`l1_shot_subject`, `l2_action_script`, `l3_environment`, `l4_optics_realism`, `l5_camera_motion`) → ghép thành `prompt` `18–95` từ tiếng Anh đạt H5.
  3. **Agent 3 (Prompt & Visual Critic):** Chạy `broll_fix.py lint` (strict layers & anti-plastic) + kiểm định mắt cả 2 bản 720p & `qa/broll_check_sheet.jpg`.
- **Cấu trúc 5 Tầng (`l1`–`l5`) chống nhựa & tối ưu T5-XXL/Gemma:**
  - `l1_shot_subject` (Primacy Zone): `[Shot Size + Camera Angle + Vietnamese + Faceless Lock nếu founder/speaker + trang phục/vải tự nhiên]` (Frozen Descriptor copy-paste nguyên văn nếu nhân vật lặp ở ≥ 2 cảnh).
  - `l2_action_script` (Literal Action): `State A → Verb → State B` diễn tả đúng nghĩa đen `anchor_quote` bằng người & đồ vật đời thường thật.
  - `l3_environment` (Lived-in Grounding): Bối cảnh công sở/đời thực Việt Nam sống động vừa đủ + màn hình/giấy/bảng **luôn** `out of frame`, `out of focus`, `blurred`, `defocused` hoặc `blank`; đồ vật `unbranded`/`plain` (`"angled away"`, `"soft glow"` KHÔNG đủ — Flow vẫn vẽ logo DELL và dashboard).
  - `l4_optics_realism` (Anti-Plastic Optics & Physics): Thông số tài liệu (`shot on 35mm documentary lens f/2.8`, `subtle natural handheld camera feel`, `soft overcast window light mixing with desk lamp`, `subtle 35mm film grain`, `unretouched skin texture`, `natural fabric creases`). **CẤM** Anti-Slop (`stunning`, `breathtaking`, `hyper-detailed`, `8k masterpiece`, `magical`, `very realistic`), **CẤM** từ nhựa/CGI (`glossy skin`, `porcelain skin`, `airbrushed`, `cyberpunk neon`, `unreal engine`, `octane render`), **CẤM** cú pháp trọng số CLIP `(keyword:1.3)` / `keyword::2`.
  - `l5_camera_motion` (Kinetic & Clean Tail): Đúng **1 chuyển động máy nhẹ tự nhiên** (`slow gentle push-in`, `slow lateral tracking shot`, `gentle handheld drift`, `static tripod`) + khẳng định sạch khung (`unbranded blank surfaces, clean frame`) — **KHÔNG** nối đuôi `"no text, no logos"`.
- **T2V (Flow text-only mặc định) vs I2V (khi có Keyframe đầu/cuối):** T2V phải tự đủ cả 5 tầng trên; I2V thì bỏ lặp mô tả tĩnh đã có trong ảnh và viết theo **4 Trục Động lực học**.
- Người nói ("mình", "anh", founder, CEO): không lộ mặt — `from behind`, `back view`, `over the shoulder`, `close-up of hands`, `silhouette`. Khách hàng, đồng nghiệp lộ mặt được.
- Người xuất hiện trong khung luôn ghi `Vietnamese` (kênh Việt, khán giả Việt): không ghi thì Flow ra người phương Tây (KB06 2026-11-14: 4 / 8 cảnh). `broll_fix.py lint` chặn.
- Đồ có chữ / số / logo sẵn (đồng hồ bấm giờ, đồng hồ số, máy quay, chân máy, đèn studio, bàn phím cận) → thay hoặc để ngoài khung. Nói rõ trên bàn/tường có gì (`a clean wooden desk with a plain ceramic mug`) để mô hình không tự bịa giấy tờ/biểu đồ.
- Một clip một cảnh liền: không `transition from … to …`, `cut to`, `montage`, `before and after`, `PiP`, `overlay`; không hiệu ứng hậu kỳ (bản đồ tự bật, khoanh vùng phát sáng, bảng thông số). Tay giữ cỡ trung, ít động; cận vật thay vì cận tay để tránh méo ngón.
