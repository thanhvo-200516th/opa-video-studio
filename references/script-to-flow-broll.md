# Quy trình chuẩn hoá: Video / Kịch bản → Xác định B-Roll → Prompt chuẩn H5 → Google Flow MCP

Tài liệu này chuẩn hoá toàn bộ quy trình từ đầu vào thô (**Video Talking Head chưa có kịch bản** hoặc **Kịch bản văn bản `SPEC.md` / JSON**) đến khi xuất bản xong bộ B-Roll đạt chuẩn **1080×1920, 30 fps, không tiếng, sạch chữ/logo** bằng MCP `google-flow`.

> **Luật cứng áp dụng xuyên suốt:**
> - **D1 (Nhịp hình):** Không để đoạn A-Roll nói trơ kéo dài quá **8 giây** (`MAX_AROLL_ONLY_S = 8.0`), cảnh chèn B-Roll phải đạt **≥ 25 %** tổng thời lượng video (`MIN_BROLL_SHARE = 0.25`), đoạn nói liền `> 4 s` ưu tiên chèn hoặc zoom.
> - **E2 (Nỗi đau):** Câu nói chứa từ khoá nỗi đau (`edit_rules.PAIN_LEXICON`) ưu tiên chèn B-Roll minh hoạ đúng nỗi đau đó.
> - **D3 (Tín dụng & công cụ):** Luôn tính trước giây và tín dụng Flow (`flow_seconds` / `flow_credits`) và kiểm tra số dư qua `flow_inspect_account`. Thiếu tín dụng → báo người dùng và dừng; không tự nâng cấp/mua thêm.
> - **MCP-first:** Mọi thao tác Google Flow đi qua MCP `google-flow` (`flow_*`), tuyệt đối không mở `labs.google/fx/tools/flow` bằng trình duyệt ngoài.

---

## Nhánh 1 — Đầu vào là Video (Talking Head / A-Roll thô chưa có kịch bản)

Áp dụng khi người dùng đưa một file video người nói (`.mp4`, `.mov`) cần tự tìm điểm chèn B-Roll và tạo clip B-Roll mới khớp lời.

### Bước 1: Bóc lời thoại có word timestamps & đọc nội dung
Chạy `scripts/broll_from_video.py analyze` trực tiếp trên video gốc (hoặc trên file transcript JSON đã bóc trước bằng `scripts/transcribe.py` / `faster-whisper`):

```bash
PY=~/.venvs/video-skills/bin/python

# Cách A: Bóc băng + phân tích tự động từ video thô
$PY scripts/broll_from_video.py analyze \
  --video /path/to/aroll_raw.mp4 \
  --out /path/to/work_dir

# Cách B: Phân tích từ transcript Scribe/Whisper JSON có sẵn
$PY scripts/broll_from_video.py analyze \
  --transcript /path/to/transcript.json \
  --out /path/to/work_dir
```

Script tự gom các từ liên tiếp thành các block ý nghĩa (`3.0–10.0 s`, tách tại dấu ngắt câu `. ? !` hoặc khoảng lặng `> 0.45 s`), đọc hết câu chuyện và xuất `work_dir/broll_plan.json` + `work_dir/broll_plan.md`.

### Bước 2: Quy tắc xác định chỗ cần chèn B-Roll trên timeline
Kiểm tra lại danh sách `slots[]` trong `broll_plan.md` dựa theo 3 tiêu chí:
1. **Chặn nói trơ > 4–8 s (Luật D1):** Bất kỳ đoạn A-Roll liên tiếp nào vượt `8.0 s` bắt buộc phải ngắt bằng ít nhất 1 slot `B-ROLL`. Tổng thời lượng `B-ROLL` đạt **≥ 25 %** tổng video.
2. **Câu chứa từ khoá nỗi đau / vấn đề (Luật E2):** Các câu chứa từ khoá trong `PAIN_LEXICON` (vd: *mất khách, quá tải, tốn thời gian, đốt tiền, ngồi nói chay, quy trình rác...*) được ưu tiên chuyển thành `B-ROLL` minh hoạ đúng hoàn cảnh đó.
3. **Câu mô tả bối cảnh, hành động, ví dụ thực tế, kết quả:** Ưu tiên cắt sang `B-ROLL` để tăng tính trực quan. **Tránh** cắt sang B-Roll ở:
   - Câu **hook mặt người 0–3 s đầu** (giữ slot đầu là `A-ROLL` để bắt giữ ánh nhìn).
   - Câu **chốt CTA cuối video** (trừ khi kịch bản thuộc dạng `broll_heavy`).

### Bước 3: Trích `anchor_quote`, tính `flow_seconds` & `flow_credits`
Với từng slot `B-ROLL`:
- Giữ nguyên văn đoạn lời thoại thuộc slot đó làm `anchor_quote` (hoặc cụm từ cốt lõi nằm gọn bên trong lời thoại của slot).
- Lấy `voice_len = end - start` (giây).
- Công thức chuẩn hoá thời lượng & tín dụng trên Google Flow (đồng bộ với `scripts/broll_fix.py`):
  - `flow_seconds = clamp(ceil(voice_len + 0.3), 3, 15)` (thanh trượt Omni 1.2 Flash chạy từ 3–15 s; cộng thêm `0.3 s` đệm tránh hụt đuôi).
  - Nếu `voice_len + 0.3 > 15.0 s`: tách thành 2 slot B-Roll nối tiếp.
  - `flow_credits` (gói Pro/Ultra, 720p):
    - `3 tín dụng / giây` cho phần `≤ 10 s`, và `6 tín dụng / giây` cho phần `11–15 s`.
    - Nâng 1080p bản được chọn: miễn phí `≤ 10 s`, `1 tín dụng / giây` cho phần vượt `10 s`.
    - Mặc định tạo `outputs = 2` bản ở 720p để chọn bằng mắt, rồi chỉ nâng 1080p **1 bản tốt nhất**:
      `credits_x2 = 2 * (min(secs, 10) * 3 + max(0, secs - 10) * 6) + max(0, secs - 10)`.

### Bước 4: Viết câu Prompt tiếng Anh chuẩn H5 bám sát 100% `anchor_quote`
Mỗi slot `B-ROLL` viết một câu prompt tiếng Anh theo **khung 5 phần H5**:

```text
[1. Chủ thể người Việt / đôi tay giấu mặt]
+ [2. Hành động cụ thể minh hoạ đúng anchor_quote]
+ [3. Bối cảnh thật & đồ vật trên mặt bàn/tường nói rõ]
+ [4. Ánh sáng / không khí / ống kính]
+ [5. 1 chuyển động máy mượt duy nhất]
```

**Các luật cứng từ `scripts/broll_fix.py` (vi phạm sẽ bị `lint` chặn):**
1. **Độ dài & ngôn ngữ:** **8–60 từ tiếng Anh**, tuyệt đối không có dấu tiếng Việt, không phải mã clip thư viện.
2. **Không dùng từ cấm (`BANNED_RE`):** Cấm mọi từ dễ khiến AI vẽ chữ/UI/số liệu giả như:
   `text, caption, subtitle, sign, logo, number, chart, dashboard, ui, chat, app, label, poster, brand, note, notes, checklist, checkbox, written, bullet, handwritten, handwriting, chatting, message, messaging, texting, side-by-side, comparison, graph, graphs, metrics, analytics, statistics, engagement, writing on paper` và tên hãng/nền tảng (`youtube, tiktok, facebook, instagram, iphone, macbook, apple, samsung, google`).
3. **Bắt buộc quốc tịch Việt Nam:** Nếu khung hình có người (`PERSON_RE`), **phải có từ `Vietnamese`** (không ghi AI dễ sinh người phương Tây).
4. **Người nói / Founder / CEO phải giấu mặt:** Nếu nhắc tới `founder, ceo, narrator, speaker, presenter, host`, bắt buộc dùng góc giấu mặt (`from behind, back view, over the shoulder, silhouette, hands only, face out of frame`).
5. **Màn hình / giấy tờ / bảng trắng:** Chỉ được xuất hiện khi ghi rõ **`out of frame`**, **`out of focus`**, **`blurred`**, **`defocused`** hoặc **`blank`**. (Các cụm mơ hồ như `"angled away"` hoặc `"soft glow"` KHÔNG đủ — Flow vẫn vẽ logo/giao diện).
6. **Một clip — một cảnh liền mạch (`MULTI_SHOT_RE`):** Cấm `transition from/to, cut to, montage, split-screen, before-and-after, picture-in-picture, pip, overlay`. Một hành động, một bối cảnh, một chuyển động máy.
7. **KHÔNG nối đuôi `NO text...` khi gửi Google Flow:** Chỉ gửi lõi `prompt` sạch. Flow không có negative prompt box; thêm `"no text, no logo"` dễ bị mô hình hiểu ngược và vẽ ra chữ/logo.

### Bước 5: Kiểm `check-prompts` → Tạo qua MCP `google-flow` → Chuẩn hoá
1. Lưu danh sách prompt ra `prompts.json` dạng:
   ```json
   [
     {
       "slot_id": 2,
       "anchor_quote": "đoạn nguyên văn nằm trong lời thoại slot 2",
       "prompt": "Over-the-shoulder shot of a young Vietnamese office worker..."
     }
   ]
   ```
2. Kiểm tra H5 và xuất kế hoạch tín dụng cuối cùng bằng `broll_from_video.py check-prompts`:
   ```bash
   $PY scripts/broll_from_video.py check-prompts \
     --plan /path/to/work_dir/broll_plan.json \
     --prompts /path/to/work_dir/prompts.json \
     --out /path/to/work_dir/flow_ready.json
   ```
   Phải đạt `[H5 OK]` (0 lỗi, mã thoát `0`) trước khi gọi Flow.
3. Thực thi tạo qua **MCP `google-flow`** (xem thêm chi tiết trong `references/flow-broll.md`):
   - `flow_list_accounts` → lấy `defaultAccountId` nếu `readyForGeneration=true` (chưa kết nối → `flow_begin_account_connection`, chờ người dùng bấm *Connect Flow* → `flow_complete_account_connection`).
   - `flow_inspect_account` → kiểm tra `models`, `aspectRatios`, `visibleDurations`, `upscales`, và **số dư tín dụng** (`balance >= total_credits`, thiếu thì dừng và báo người dùng).
   - Với từng job trong `flow_ready.json`, gọi `flow_generate_video`:
     - `prompt`: prompt sạch đã qua lint
     - `outputDirectory`: `<work_dir>/_google_raw`
     - `fileName`: `<seq_prefix>_b-roll-<M>_raw`
     - `model`: `"omni-flash"` (theo `flow_inspect_account`)
     - `aspectRatio`: `"9:16"`
     - `durationSeconds`: giá trị `duration_seconds` từ `flow_ready.json`
     - `outputs`: `2`, `upscale`: `"none"`, `download`: `true`, `referenceFiles`: `[]`, `confirmCreditSpend`: `true`
   - Nếu trả `status="processing"`: poll `flow_job_status(jobId, waitSeconds=10)` với đúng `jobId` đó (tuyệt đối không gọi `flow_generate_video` lại).
   - **Xem chọn 1 trong 2 bản 720p bằng mắt:** Loại ngay bản dính chữ/logo, màn hình lộ nội dung, mặt người lạ khi đang quay founder, tay/mặt méo, nhảy cảnh, hoặc lệch `anchor_quote`.
   - Nâng 1080p bản đã chọn & tải về: `flow_upscale_video(jobId, factor="1080p", confirmCreditSpend=true)` → poll `flow_job_status` nếu cần → `flow_download_job(jobId)`.
4. Chuẩn hoá clip về chuẩn dựng `1080×1920, 30 fps, không tiếng, BT.709` bằng `broll_fix.py normalize`:
   ```bash
   $PY scripts/broll_fix.py normalize \
     /path/to/work_dir/_google_raw/<file_1080p>.mp4 \
     /path/to/work_dir/<seq_prefix>_b-roll-<M>.mp4 \
     --mark flow
   ```
   *(Chỉ thêm `--mark flow` nếu bản tải về có dấu ngôi sao góc dưới phải; nếu tài khoản Ultra đã tắt watermark thì bỏ `--mark flow`.)*

---

## Nhánh 2 — Đầu vào là Kịch bản văn bản (`SPEC.md` / text / JSON)

Áp dụng khi sản xuất từ kịch bản văn bản có sẵn để tạo cả gói thư mục dự án (`00_storyboard_manifest.json`, `00_BANG_PHAN_CANH.md`, `prompts_muse_veo_broll.json`).

### Bước 1: Tách cảnh A-Roll vs B-Roll theo 3 chế độ tỷ lệ
Dùng `scripts/analyze_and_scaffold.py` để phân tích kịch bản và chia cảnh theo 3 mức tỷ lệ:
- **`balanced_credit_saver` (Mặc định khuyên dùng — A-Roll 30–38%):** Giữ A-Roll mặt người ở Hook mở đầu, các câu chuyển ý cốt lõi, dẫn chứng cá nhân và chốt CTA; các đoạn giải thích, bối cảnh và nỗi đau giao cho B-Roll.
- **`aroll_heavy` (A-Roll 50–70%):** Ưu tiên độ tin cậy mặt người nói (phỏng vấn/chia sẻ chuyên sâu), B-Roll chỉ chèn ở đoạn > 8 s hoặc từ khoá nỗi đau nặng.
- **`broll_heavy` (A-Roll 15–28%):** Giọng đọc dẫn chuyện xuyên suốt trên chuỗi B-Roll điện ảnh, chỉ lộ mặt ở Hook ngắn hoặc câu kết.

```bash
$PY scripts/analyze_and_scaffold.py --spec /path/to/SPEC.md --out /path/to/output_root
```

### Bước 2: Chuyển hoá cảnh B-Roll → Prompt chuẩn H5 → Tạo qua Google Flow MCP
1. Với mọi phân đoạn `"type": "b-roll"` trong `00_storyboard_manifest.json`, chuyển `visual_direction` + `tts_text` thành file `broll_new_prompts.json` (mỗi phần tử gồm `seq`, `prompt` chuẩn H5, `anchor_quote` trích nguyên văn từ `tts_text`).
2. Kiểm tra luật H5 & lập kế hoạch tín dụng:
   ```bash
   $PY scripts/broll_fix.py lint /path/to/script_dir --prompts broll_new_prompts.json
   $PY scripts/broll_fix.py prepare /path/to/script_dir --prompts broll_new_prompts.json --source flow
   $PY scripts/broll_fix.py plan /path/to/script_dir --engine flow --outputs 2
   ```
   Báo tổng giây và tổng tín dụng Flow cho người dùng xác nhận trước khi tiêu tín dụng (D3).
3. Gọi MCP `google-flow` theo đúng thứ tự:
   `flow_list_accounts` → `flow_inspect_account` → `flow_generate_video` → `flow_job_status` → xem chọn bản → `flow_upscale_video(factor="1080p")` → `flow_download_job`.
4. Chuẩn hoá & xác minh hàng loạt:
   ```bash
   $PY scripts/broll_fix.py normalize <raw_1080p.mp4> <script_dir>/<STT>_b-roll-<M>.mp4 [--mark flow]
   $PY scripts/broll_fix.py verify <script_dir> --scenes <danh_sách_seq>
   ```
   Mở `qa/broll_check_sheet.jpg` kiểm tra bằng mắt từng cảnh (không chữ/logo, đúng `anchor_quote`), sau đó chạy `scripts/scene_check.py` (0 FAIL).

---

## Bảng chuyển đổi nhanh: Ý tưởng tiếng Việt → Prompt H5 an toàn cho Google Flow

| Ý tưởng / Lời thoại tiếng Việt | Lỗi dễ mắc khiến AI vẽ chữ / hỏng cảnh | Prompt tiếng Anh chuẩn H5 an toàn (đã đạt `lint_prompt`) |
|---|---|---|
| *"Báo cáo doanh thu / chỉ số tăng trưởng vọt"* | Dùng `chart, graph, metrics, analytics, dashboard` → vẽ số liệu giả, chữ sai chính tả | `Over-the-shoulder shot of a young Vietnamese entrepreneur typing calmly at a clean wooden desk with an unbranded laptop screen blurred out of focus, warm morning window light, slow dolly-in.` |
| *"Quá tải công việc, lạc lối giữa đống việc không tên"* | Dùng `checklist, notes, handwritten, cluttered text` → vẽ giấy chi chít chữ méo | `Back view of a tired Vietnamese office worker sitting alone at a dimly lit wooden desk stacked with plain blank folders, rubbing temples slowly, warm desk lamp glow, slow push-in.` |
| *"Khách nhắn tin mà ngâm tin nhắn 5 phút là mất đơn"* | Dùng `chatting, message, iphone, app, notification` → hiện logo Apple/tin nhắn chữ lỗi | `Close-up from behind of a Vietnamese shop owner holding a blank phone out of focus in a cozy boutique at dusk, looking toward an empty doorway, warm ambient light, subtle handheld motion.` |
| *"Quy trình rối rắm, phần mềm rời rạc tốn cả ngày"* | Dùng `UI, transition from chaos to clean, split-screen` → tách đôi khung hình hoặc vẽ giao diện | `Medium shot of two Vietnamese teammates standing apart in a busy office looking puzzled over scattered blank boxes on a long table, cool fluorescent overhead light, slow lateral tracking shot.` |
| *"Đội ngũ kỹ thuật tập trung rèn giũa sản phẩm"* | Quên ghi `Vietnamese`, lộ màn hình code/logo hãng | `Slow push-in on a young Vietnamese engineering team in a bright modern office, three colleagues shoulder to shoulder with monitors blurred out of focus in foreground, warm daylight, shallow depth of field.` |
| *"Đóng gói sản phẩm chuẩn chỉ trước khi giao khách"* | Dùng từ `brand, label, poster` → AI tự bịa tên thương hiệu lên hộp | `Medium close-up of a Vietnamese warehouse staff member carefully taping a plain unbranded cardboard box on a clean wooden packing table, soft natural daylight, smooth orbit camera movement.` |
| *"Ngồi nói chay 8 giây không có cảnh chèn khiến người xem lướt qua"* | Dùng `speaker face, tiktok, swipe` → AI vẽ mặt người lạ hoặc giao diện TikTok | `Side profile silhouette of a Vietnamese creator speaking into a clean studio microphone against a dark warm backdrop, soft rim light, slow push-in.` |
