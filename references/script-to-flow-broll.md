# Quy trình chuẩn hoá: Video / Kịch bản → 3 Agent hiểu kịch bản → Prompt 5 tầng H5 → Google Flow (MCP hoặc trình duyệt Cindy)

Tài liệu này chuẩn hoá toàn bộ quy trình từ đầu vào thô (**Video Talking Head chưa có kịch bản** hoặc **Kịch bản văn bản `SPEC.md` / JSON**) đi qua **Quy trình 3 Agent** đến khi xuất bản xong bộ B-Roll đời thực chân thực, không nhựa/AI, đạt chuẩn **1080×1920, 30 fps, không tiếng, sạch chữ/logo** bằng Google Flow (MCP `google-flow` hoặc trình duyệt Cindy, chọn theo phiên — xem `references/flow-broll.md`).

> **Kiến trúc Prompt nền tảng:** Xem thêm [`references/master-video-prompt-architecture.md`](master-video-prompt-architecture.md) (đặc biệt **Mục 5b: Công thức 5 Tầng T2V Anti-Plastic cho Flow B-roll**) để nắm nguyên lý *Positional Bias*, *Anti-Slop*, *Frozen Descriptor*, *4-Axis I2V Motion* và bảng thuật ngữ *DOP Cinematography Lexicon*.

> **Luật cứng áp dụng xuyên suốt:**
> - **D15 (Nguồn B-roll mặc định 100 % Google Flow):** Mục tiêu **100 %** thời lượng B-roll tạo bằng **Google Flow (MCP hoặc trình duyệt Cindy)** (tối thiểu **≥ 95 %**); footage thật / stock (`auto-footage`, kho D5) chỉ là ngoại lệ tối đa **2–5 %** (trần cứng `≤ 5 %`). Muse local chỉ là dự phòng khẩn khi Google Flow không khả dụng và người dùng đồng ý (D3).
> - **D9 (Nghĩa đen đời thực, cấm ẩn dụ CGI trừu tượng):** B-roll phải minh hoạ **đúng nghĩa đen đời thực** của từng câu thoại `tts_text` qua **Quy trình 3 Agent**. CẤM các ẩn dụ CGI trừu tượng xa rời lời nói (như khối lập phương hổ phách phát sáng trên giàn kim loại, hai thanh ray thép trượt hộp đèn, lăng kính, bánh răng, lõi năng lượng, các nút phát sáng trôi nổi).
> - **D8 (Giới hạn lặp B-roll):** Mỗi cảnh / clip B-roll tối đa **2 lần trong 1 video** và qua tối đa **2 video khác nhau** (`scripts/media_reuse.py audit` + `scripts/edit_rules.py`).
> - **D1 (Nhịp hình):** Không để đoạn A-Roll nói trơ kéo dài quá **8 giây** (`MAX_AROLL_ONLY_S = 8.0`), cảnh chèn B-Roll phải đạt **≥ 25 %** tổng thời lượng video (`MIN_BROLL_SHARE = 0.25`), đoạn nói liền `> 4 s` ưu tiên chèn hoặc zoom.
> - **E2 (Nỗi đau):** Câu nói chứa từ khoá nỗi đau (`edit_rules.PAIN_LEXICON`) ưu tiên chèn B-Roll minh hoạ đúng hoàn cảnh đời thực của nỗi đau đó.
> - **D3 (Tín dụng & công cụ):** Google Flow là mặc định, chạy bằng MCP khi phiên có tool `flow_*`, bằng trình duyệt Cindy khi không có (cả hai đều chính thức; Muse chỉ dự phòng khẩn khi Flow hỏng và có đồng ý). Luôn tính trước giây và tín dụng Flow (`flow_seconds` / `flow_credits`) và kiểm tra số dư qua `flow_inspect_account` (đường MCP) hoặc bảng tài khoản Flow (đường trình duyệt). Thiếu tín dụng → báo người dùng và dừng; không tự nâng cấp/mua thêm.
> - **Chọn bên thực thi theo phiên (D-a):** Phiên có tool `flow_*` → MCP `google-flow`; phiên không có (Claude Code / Cindy mặc định) → trình duyệt Cindy theo `references/flow-broll.md` mục 0–5. Không chạy hai đường song song cho cùng một cảnh.

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
  - Nếu `voice_len > 7.5 s` (hoặc chứa 2 vế đối lập) hoặc `voice_len + 0.3 > 15.0 s`: tách thành 2 sub-beats / 2 slot B-Roll nối tiếp (Agent 1 xử lý ở Bước 4).
  - `flow_credits` (gói Pro/Ultra, 720p):
    - `3 tín dụng / giây` cho phần `≤ 10 s`, và `6 tín dụng / giây` cho phần `11–15 s`.
    - Nâng 1080p bản được chọn: miễn phí `≤ 10 s`, `1 tín dụng / giây` cho phần vượt `10 s`.
    - Mặc định tạo `outputs = 2` bản ở 720p để chọn bằng mắt, rồi chỉ nâng 1080p **1 bản tốt nhất**:
      `credits_x2 = 2 * (min(secs, 10) * 3 + max(0, secs - 10) * 6) + max(0, secs - 10)`.

### Bước 4: Quy trình 3 Agent hiểu kịch bản & viết Prompt 5 tầng Anti-Plastic (chuẩn H5)

Tuyệt đối **không** dịch thô `visual_direction` hoặc bịa ẩn dụ trừu tượng rồi gửi thẳng vào Google Flow. Mọi B-Roll đều phải đi qua **3 Agent chuyên trách** dưới đây (áp dụng cho cả Nhánh 1 từ video và Nhánh 2 từ kịch bản):

#### Agent 1 — Script Semantic Analyst (Phân tích ngữ nghĩa & tách nhịp đời thực)
- **Đầu vào:** Đọc **toàn bộ `tts_text` của cả video** (`00_storyboard_manifest.json` hoặc `broll_plan.json`) để hiểu trọn mạch câu chuyện, nhân vật chính và bối cảnh ngành nghề.
- **Tách nhịp (`Sub-beat Split`):** Bất kỳ đoạn B-Roll nào **dài `> 7,5 s`** hoặc **chứa 2 vế đối lập / 2 hành động tách biệt** (vd: *"trước đây loay hoay thủ công, giờ đội ngũ bấm chạy đồng đều"*) **phải tách thành 2 sub-beats** rõ ràng (mỗi sub-beat là 1 clip liền mạch, không nhồi 2 cảnh vào 1 clip).
- **Chuyển nghĩa thành `script_beat_vi`:** Với từng beat, viết 1 câu tiếng Việt mô tả **cảnh đời thực cụ thể (người + đồ vật + hành động nhìn thấy được bằng mắt)** chứng minh đúng `anchor_quote`:
  - **ĐÚNG (Nghĩa đen đời thực):** *"Nữ nhân viên văn phòng người Việt đang ngồi trước bàn gỗ mở một tệp ảnh mẫu in trên bàn và đặt cạnh hộp sản phẩm mẫu"* hoặc *"Góc qua vai người trẻ Việt Nam kéo dây sạc hoặc gõ bàn phím laptop mờ hoàn toàn, đồng nghiệp bên cạnh cùng bấm chuột đồng loạt."*
  - **CẤM TUYỆT ĐỐI (Ẩn dụ CGI trừu tượng):** khối lập phương hổ phách phát sáng (`glowing amber cube`), giàn kim loại, hai thanh ray thép trượt hộp đèn (`metal pipeline rails`), lăng kính (`glowing prism`), bánh răng (`gears`), lõi năng lượng (`energy core`), các nút trôi nổi (`floating nodes`), `hologram`, `sci-fi`, `neon circuit`.

#### Agent 2 — 5-Layer Anti-Plastic Prompt Architect (Kiến trúc sư Prompt 5 tầng cho Google Flow Omni Flash)
Từ `script_beat_vi` và `anchor_quote`, viết cấu trúc **`layers` 5 tầng** tối ưu cho bộ mã hoá **T5-XXL / Gemma**, rồi ghép thành chuỗi `prompt` tiếng Anh **`18–95` từ** đạt chuẩn **H5**:

1. **Tầng 1 — `l1_shot_subject` (Primacy Zone — Trọng số đầu câu cao nhất):**
   - Cấu trúc: `[Shot Size] + [Camera Angle] + Vietnamese + [Faceless Lock nếu là founder/chủ/speaker/narrator/host] + [Ngoại hình & trang phục đời thực có chất liệu vải tự nhiên]`.
   - Ví dụ: `Over-the-shoulder medium shot of a young Vietnamese designer in a slightly wrinkled olive-green cotton shirt,`
   - *Frozen Descriptor:* Nếu cùng 1 nhân vật xuất hiện ở ≥ 2 slot B-Roll trong cùng video, **copy-paste nguyên văn** cùng một cụm mô tả ngoại hình & trang phục ở mọi slot.
2. **Tầng 2 — `l2_action_script` (Literal Action — Hành động nghĩa đen `State A → Verb → State B`):**
   - Diễn tả ĐÚNG ý nghĩa `anchor_quote` bằng hành động con người & đồ vật đời thường thật, kết hợp vật lý phụ tự nhiên (nếp áo co duỗi, hơi nước bốc nhẹ, tay đặt tự nhiên cỡ trung).
   - Ví dụ: `steadily arranging plain unbranded product sample cards from left to right on a wooden desk while a Vietnamese colleague beside her clicks a plain mouse at the same moment,`
3. **Tầng 3 — `l3_environment` (Lived-in Grounding — Bối cảnh Việt Nam có chiều sâu đời thực):**
   - Bối cảnh công sở / xưởng / quán / căn hộ Việt Nam sống động vừa đủ (cây xanh, ly gốm trơn, ánh nắng cửa sổ, đồ dùng đời thường vừa phải).
   - **Ràng buộc màn hình / giấy / bảng:** Nếu có `screen`, `monitor`, `laptop`, `phone`, `tablet`, `whiteboard`, `paper`, `notebook`, `document`, **BẮT BUỘC** ghi rõ `completely out of focus`, `blurred`, `defocused`, `blank`, hoặc `out of frame`. Đồ vật luôn `unbranded` / `plain`.
   - Ví dụ: `in a lived-in Saigon studio office with laptop screens completely out of focus in the background and a plain ceramic mug beside a blank unbranded notebook,`
4. **Tầng 4 — `l4_optics_realism` (Anti-Plastic Optics & Physics — Chống nhựa, chống lộ AI):**
   - Thay thế mọi tính từ sáo rỗng bằng thông số ống kính tài liệu, ánh sáng tự nhiên hỗn hợp, hạt phim và chi tiết da/vải thật:
     - Gợi ý chuẩn: `shot on 35mm documentary lens f/2.8, subtle natural handheld camera feel, soft overcast window light mixing with warm desk lamp, subtle 35mm film grain, unretouched skin texture, natural fabric creases,` (hoặc `50mm documentary lens f/2.0`).
   - **CẤM Anti-Slop:** `stunning`, `breathtaking`, `hyper-detailed`, `hyperdetailed`, `8k`, `4k masterpiece`, `masterpiece`, `magical`, `very realistic`, `ultra realistic`, `photorealistic masterpiece`, `award-winning`, `best quality`.
   - **CẤM từ nhựa/CGI & ánh sáng giả:** `glossy skin`, `porcelain skin`, `airbrushed`, `plastic sheen`, `cyberpunk neon`, `unreal engine`, `octane render`, `cgi`, `3d render`, chuyển động gimbal trơn tuột siêu thực (`hyper-smooth gimbal`).
   - **CẤM cú pháp trọng số CLIP:** `(keyword:1.3)` hay `keyword::2`.
5. **Tầng 5 — `l5_camera_motion` (Kinetic & Clean Tail — 1 chuyển động máy + khẳng định sạch khung):**
   - Chọn **ĐÚNG 1** chuyển động máy nhẹ nhàng tự nhiên (`slow gentle push-in`, `subtle handheld drift`, `slow lateral tracking shot`, `gentle static tripod framing`) + đuôi khẳng định sạch khung: `unbranded blank surfaces, clean frame.`
   - **KHÔNG** nối đuôi phủ định `no text, no logos, no subtitles` (Flow không có negative prompt box; nối đuôi phủ định dễ khiến AI vẽ ngược ra chữ/logo).

#### Agent 3 — Prompt & Visual Critic (Kiểm định mã nguồn + Kiểm định mắt 720p)
- **Cổng 1 (Code Lint):** Chạy `broll_fix.py lint` (hoặc `broll_from_video.py check-prompts`) kiểm tra chặt **cấu trúc `layers` 5 tầng**, độ dài **`18–95` từ tiếng Anh**, từ cấm `BANNED_RE`, nhãn `Vietnamese`, faceless lock, màn hình mờ/trống, chính sách **anti-plastic & anti-abstract-CGI**.
- **Cổng 2 (Visual Critic trên 2 bản 720p & `qa/broll_check_sheet.jpg`):**
  - Bắt buộc mở xem bằng mắt **cả 2 bản 720p** do Flow trả về và lưới ảnh `qa/broll_check_sheet.jpg`.
  - **Loại ngay lập tức** nếu dính bất kỳ lỗi nào:
    1. Da sáp láng mịn, bóng nhựa, ánh sáng neon giả tạo / nhìn lộ rõ AI/CGI;
    2. Ngón tay méo, bàn tay thừa ngón, đồ vật phi vật lý (ly xuyên bàn, chuột biến dạng);
    3. Chữ, số, logo hãng (trên lưng laptop, cốc, áo, biển hiệu) hoặc màn hình/giấy hiện giao diện đọc được;
    4. Người nói/founder lộ mặt lạ;
    5. Cắt cảnh ngầm / chuyển cảnh giữa clip / người xuất hiện hoặc biến mất đột ngột;
    6. **Lệch nghĩa `anchor_quote`** (hình không chứng minh đúng câu thoại tiếng Việt).
  - Nếu cả 2 bản đều hỏng → Agent 2 sửa `layers` theo đúng lỗi nhìn thấy (không giữ ẩn dụ cũ), `lint` lại và tạo lại tối đa 1 lần.

**Các luật cứng từ `scripts/broll_fix.py` (vi phạm sẽ bị `lint` chặn):**
1. **Độ dài, cấu trúc 5 tầng & ngôn ngữ:** Lõi `prompt` **18–95 từ tiếng Anh** (kèm object `layers` đủ `l1_shot_subject`..`l5_camera_motion`), tuyệt đối không có dấu tiếng Việt, không phải mã clip thư viện.
2. **Không dùng từ cấm (`BANNED_RE`) & Anti-Plastic / Anti-CGI:** Cấm từ vẽ chữ/UI/số liệu giả (`text, caption, subtitle, sign, logo, number, chart, dashboard, ui, chat, app, label, poster, brand, note, notes, checklist, checkbox, written, bullet, handwritten, handwriting, chatting, message, messaging, texting, side-by-side, comparison, graph, metrics, analytics, statistics, engagement, writing on paper`), tên hãng/nền tảng (`youtube, tiktok, facebook, instagram, iphone, macbook, apple, samsung, google`), cùng danh sách từ nhựa/slop và ẩn dụ CGI trừu tượng trong `rules.json › params.broll.anti_plastic_policy`.
3. **Bắt buộc quốc tịch Việt Nam:** Nếu khung hình có người (`PERSON_RE`), **phải có từ `Vietnamese`** (không ghi AI dễ sinh người phương Tây).
4. **Người nói / Founder / CEO phải giấu mặt:** Nếu nhắc tới `founder, ceo, narrator, speaker, presenter, host`, bắt buộc dùng góc giấu mặt (`from behind, back view, over the shoulder, silhouette, hands only, face out of frame`).
5. **Màn hình / giấy tờ / bảng trắng:** Chỉ được xuất hiện khi ghi rõ **`out of frame`**, **`out of focus`**, **`blurred`**, **`defocused`** hoặc **`blank`**. (Các cụm mơ hồ như `"angled away"` hoặc `"soft glow"` KHÔNG đủ — Flow vẫn vẽ logo/giao diện).
6. **Một clip — một cảnh liền mạch (`MULTI_SHOT_RE`):** Cấm `transition from/to, cut to, montage, split-screen, before-and-after, picture-in-picture, pip, overlay`. Một hành động, một bối cảnh, một chuyển động máy.
7. **KHÔNG nối đuôi `NO text...` khi gửi Google Flow:** Chỉ gửi lõi `prompt` sạch. Flow không có negative prompt box; thêm `"no text, no logo"` dễ bị mô hình hiểu ngược và vẽ ra chữ/logo.

### Bước 5: Kiểm `check-prompts` → Tạo qua Google Flow (MCP hoặc trình duyệt) → Agent 3 duyệt → Chuẩn hoá
1. Lưu danh sách prompt theo schema 3 Agent ra `prompts.json`:
   ```json
   [
     {
       "slot_id": 2,
       "anchor_quote": "đoạn nguyên văn nằm trong lời thoại slot 2",
       "script_beat_vi": "Cảnh đời thực cụ thể chứng minh câu thoại (không ẩn dụ CGI)",
       "layers": {
         "l1_shot_subject": "Over-the-shoulder medium shot of a young Vietnamese designer in a wrinkled dark cotton polo,",
         "l2_action_script": "steadily sliding plain sample swatches across a wooden desk to match a printed cardboard moodboard out of focus,",
         "l3_environment": "in a lived-in Hanoi studio office with blurred monitors in the background and a blank unbranded notebook beside a ceramic cup,",
         "l4_optics_realism": "shot on 35mm documentary lens f/2.8, subtle natural handheld camera feel, soft overcast window light mixing with desk lamp, subtle 35mm film grain, unretouched skin texture, natural fabric creases,",
         "l5_camera_motion": "slow gentle push-in, unbranded blank surfaces, clean frame."
       },
       "prompt": "Over-the-shoulder medium shot of a young Vietnamese designer in a wrinkled dark cotton polo, steadily sliding plain sample swatches across a wooden desk to match a printed cardboard moodboard out of focus, in a lived-in Hanoi studio office with blurred monitors in the background and a blank unbranded notebook beside a ceramic cup, shot on 35mm documentary lens f/2.8, subtle natural handheld camera feel, soft overcast window light mixing with desk lamp, subtle 35mm film grain, unretouched skin texture, natural fabric creases, slow gentle push-in, unbranded blank surfaces, clean frame."
     }
   ]
   ```
2. Kiểm tra H5 (strict layers & anti-plastic) và xuất kế hoạch tín dụng cuối cùng bằng `broll_from_video.py check-prompts`:
   ```bash
   $PY scripts/broll_from_video.py check-prompts \
     --plan /path/to/work_dir/broll_plan.json \
     --prompts /path/to/work_dir/prompts.json \
     --out /path/to/work_dir/flow_ready.json
   ```
   Phải đạt `[H5 OK]` (0 lỗi, mã thoát `0`) trước khi gọi Flow.
3. Thực thi tạo qua Google Flow — chọn theo phiên (D-a; chi tiết `references/flow-broll.md`). Phiên **không có** tool `flow_*` → làm theo đường trình duyệt Cindy (mục 0–5 của `flow-broll.md`), bỏ qua phần MCP dưới đây. Phiên **có** `flow_*` thì:
   - `flow_list_accounts` → lấy `defaultAccountId` nếu `readyForGeneration=true` (chưa kết nối → `flow_begin_account_connection`, chờ người dùng bấm *Connect Flow* → `flow_complete_account_connection`).
   - `flow_inspect_account` (bắt buộc, lưu ra `inspect.json`) → kiểm tra `models`, `aspectRatios`, `visibleDurations`, số bản video, `upscales`, và **số dư tín dụng** (`balance >= total_credits`, thiếu thì dừng và báo người dùng).
   - Dựng đối số từng job bằng `$PY scripts/broll_fix.py mcp-jobs <thư_mục_video> --inspect inspect.json [--speed 1.10]` (in một danh sách JSON các object đối số `flow_generate_video`, mỗi cảnh một object), rồi gọi `flow_generate_video` cho từng object. Quy tắc (D-b):
     - `prompt`: prompt sạch đã qua lint; `outputDirectory`: `<work_dir>/_google_raw`; `fileName`: `<seq_prefix>_b-roll-<M>_raw`
     - `model` và `aspectRatio`: đúng id `flow_inspect_account` trả (ví dụ `omni-1-2-flash`, `9:16`), không gõ cứng
     - `durationSeconds`: `duration_seconds` từ `flow_ready.json`, chỉ truyền khi nằm trong `visibleDurations`
     - `outputs`: chỉ truyền khi số bản đó được inspect liệt kê; cần 2 bản mà `outputs: 2` không có → 2 job riêng, mỗi job `outputs: 1`
     - `upscale`: `"1080p"` khi inspect liệt kê (không thì `highest_available`); không lấy bản 720p làm clip cuối
     - `download`: `true`, `referenceFiles`: `[]`, `confirmCreditSpend`: `true`
   - Nếu trả `status="processing"`: poll `flow_job_status(jobId, waitSeconds=10)` với đúng `jobId` đó; cấm gọi lại `flow_generate_video` cho cảnh đó khi job còn `processing`.
   - **Agent 3 xem chọn bản đúng nhất bằng mắt:** Loại ngay bản da nhựa, ngón tay méo, đồ vật phi vật lý, dính chữ/logo, màn hình lộ nội dung, mặt người lạ khi đang quay founder, cắt cảnh ngầm, hoặc lệch `anchor_quote`.
   - Chưa có bản 1080p (upscale không áp trong lúc tạo) → `flow_upscale_video(jobId, factor="1080p", confirmCreditSpend=true)` → poll `flow_job_status` → `flow_download_job(jobId)`.
   - Agent UI của Flow có thể viết lại prompt: báo cáo ghi prompt thực sự đã gửi; Visual Critic chấm theo `anchor_quote`, không theo prompt (D-d).
   - Sau khi tải, `broll_fix.py verify` FAIL clip ngắn hơn lời − 0,3 s: nếu MCP không đặt được `durationSeconds` → tạo lại cảnh bằng đường trình duyệt đúng số giây, hoặc tách câu thành 2 beat; ghi báo cáo (D-c).
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

### Bước 2: Chạy Quy trình 3 Agent → Prompt 5 tầng H5 → Tạo qua Google Flow (MCP hoặc trình duyệt)
1. **Agent 1 (Script Semantic Analyst)** đọc trọn `tts_text` trong `00_storyboard_manifest.json`, tách đoạn `> 7,5 s` hoặc có 2 vế đối lập thành sub-beats và viết `script_beat_vi` (nghĩa đen đời thực, **CẤM ẩn dụ CGI trừu tượng**).
2. **Agent 2 (5-Layer Anti-Plastic Prompt Architect)** viết `broll_new_prompts.json` cho mọi phân đoạn `"type": "b-roll"` (mỗi phần tử gồm `seq`, `anchor_quote` trích nguyên văn từ `tts_text`, `script_beat_vi`, `layers` 5 tầng `l1_shot_subject`..`l5_camera_motion`, và `prompt` ghép `18–95` từ tiếng Anh đạt H5).
3. **Agent 3 (Cổng 1 — Lint)** kiểm tra luật H5 (strict layers & anti-plastic) & lập kế hoạch tín dụng:
   ```bash
   $PY scripts/broll_fix.py lint /path/to/script_dir --prompts broll_new_prompts.json
   $PY scripts/broll_fix.py prepare /path/to/script_dir --prompts broll_new_prompts.json --source flow
   $PY scripts/broll_fix.py plan /path/to/script_dir --engine flow --outputs 2
   ```
   Báo tổng giây và tổng tín dụng Flow cho người dùng xác nhận trước khi tiêu tín dụng (D3).
4. Tạo qua Google Flow, chọn theo phiên (D-a): phiên không có `flow_*` → đường trình duyệt Cindy (`references/flow-broll.md` mục 0–5). Phiên có `flow_*` → gọi MCP `google-flow` theo thứ tự:
   `flow_list_accounts` → `flow_inspect_account` (lưu `inspect.json`) → `$PY scripts/broll_fix.py mcp-jobs <script_dir> --inspect inspect.json [--speed 1.10]` dựng đối số → `flow_generate_video` → `flow_job_status` (cùng `jobId`, không gọi lại khi đang `processing`) → **Agent 3 (Cổng 2 — Visual Critic)** xem chọn bản đúng nhất (loại ngay bản da nhựa, ngón tay méo, đồ vật phi vật lý, cắt cảnh ngầm hoặc lệch `anchor_quote`) → `flow_upscale_video(factor="1080p")` nếu chưa có bản 1080p → `flow_download_job`. Tham số chỉ truyền khi inspect cho phép (D-b); không có `outputs: 2` thì 2 job `outputs: 1`; ghi prompt thực sự đã gửi (D-d).
5. Chuẩn hoá & xác minh hàng loạt:
   ```bash
   $PY scripts/broll_fix.py normalize <raw_1080p.mp4> <script_dir>/<STT>_b-roll-<M>.mp4 [--mark flow]
   $PY scripts/broll_fix.py verify <script_dir> --scenes <danh_sách_seq>
   ```
   `verify` FAIL clip ngắn hơn lời − 0,3 s → tạo lại cảnh bằng đường trình duyệt đúng số giây hoặc tách câu thành 2 beat (D-c).
   Mở `qa/broll_check_sheet.jpg` kiểm tra bằng mắt từng cảnh (không da nhựa/CGI, không chữ/logo, đúng nghĩa đen `anchor_quote`), sau đó chạy `scripts/scene_check.py` (0 FAIL).

---

## Bảng chuyển đổi nhanh: Ý tưởng tiếng Việt → Prompt 5 tầng H5 Anti-Plastic cho Google Flow

| Ý tưởng / Lời thoại tiếng Việt | Lỗi cũ dễ mắc (Ẩn dụ CGI / Nhựa / Vẽ chữ) | Prompt tiếng Anh 5 tầng H5 Anti-Plastic (`18–95` từ, ghép từ `l1`–`l5`) |
|---|---|---|
| *"Bảng luồng kéo thả nối từ ý tưởng tiếng Việt sang ảnh 4K xuất video"* | Vẽ khối lập phương hổ phách phát sáng trên giàn kim loại, hoặc dùng `UI, workflow chart` gây chữ giả | `Over-the-shoulder medium shot of a young Vietnamese creator in a wrinkled dark cotton t-shirt sitting at a wooden desk, steadily moving plain matte photo cards along a row of blank unbranded paper cards from left to right, in a lived-in Saigon studio with monitors completely out of focus in the background, shot on 35mm documentary lens f/2.8, subtle natural handheld camera feel, soft overcast window light mixing with warm desk lamp, subtle 35mm film grain, unretouched skin texture, natural fabric creases, slow gentle push-in, unbranded blank surfaces, clean frame.` |
| *"Đội ngũ bấm chạy đồng đều"* | Vẽ 2 thanh ray thép trượt hộp đèn CGI, thiếu `Vietnamese` | `Medium wide shot of three Vietnamese office teammates in casual wrinkled linen and cotton shirts seated side by side along a wooden table, pressing their plain wireless mice and tapping their spacebars in unison as they lean slightly forward, in an authentic lived-in office with blurred out-of-focus monitors in the foreground, shot on 35mm documentary lens f/2.8, subtle natural handheld camera feel, soft overcast daylight from a glass window, subtle 35mm film grain, unretouched skin texture, natural fabric creases, slow lateral tracking shot, unbranded blank surfaces, clean frame.` |
| *"Báo cáo doanh thu / chỉ số tăng trưởng vọt"* | Dùng `chart, graph, metrics, analytics, dashboard` → vẽ số liệu giả, chữ sai chính tả | `Over-the-shoulder medium shot of a young Vietnamese entrepreneur in a plain navy cotton polo typing calmly at a wooden desk, reaching over to pick up a plain ceramic mug with a relaxed smile, in a lived-in office with an unbranded laptop screen blurred out of focus, shot on 35mm documentary lens f/2.8, subtle natural handheld camera feel, soft overcast morning window light, subtle 35mm film grain, unretouched skin texture, natural fabric creases, slow gentle dolly-in, unbranded blank surfaces, clean frame.` |
| *"Quá tải công việc, lạc lối giữa đống việc không tên"* | Dùng `checklist, notes, handwritten` hoặc da bóng nhựa CGI | `Back view medium shot of a tired Vietnamese office worker in a creased white cotton shirt sitting alone at a wooden desk stacked with plain blank folders, slowly lowering both hands to rub his temples, in a dimly lit Saigon apartment office at dusk, shot on 35mm documentary lens f/2.8, subtle natural handheld camera feel, warm desk lamp light mixing with cool twilight window light, subtle 35mm film grain, natural hair strands and fabric creases, slow gentle push-in, unbranded blank surfaces, clean frame.` |
| *"Khách nhắn tin mà ngâm tin nhắn 5 phút là mất đơn"* | Dùng `chatting, message, iphone, app` → hiện logo Apple/tin nhắn chữ lỗi | `Over-the-shoulder close-up from behind of a Vietnamese shop owner in a natural beige linen apron holding a blank unbranded phone completely out of focus, glancing up toward an empty glass boutique doorway as evening street traffic blurs outside, shot on 50mm documentary lens f/2.0, subtle natural handheld camera feel, soft warm indoor tungsten lamp mixing with overcast dusk light, subtle 35mm film grain, natural fabric creases, gentle handheld drift, unbranded blank surfaces, clean frame.` |
| *"Ngồi nói chay 8 giây không có cảnh chèn khiến người xem lướt qua"* | Dùng `speaker face, tiktok, swipe` → AI vẽ mặt người lạ hoặc giao diện TikTok | `Side profile silhouette of a Vietnamese creator in a matte dark cotton hoodie speaking calmly toward an unbranded studio microphone on a desk, gesturing naturally with one hand at chest height, in a quiet lived-in home studio with out-of-focus shelving behind, shot on 35mm documentary lens f/2.8, subtle natural handheld camera feel, soft warm window rim light mixing with dim room fill, subtle 35mm film grain, natural fabric creases, slow gentle push-in, unbranded blank surfaces, clean frame.` |
