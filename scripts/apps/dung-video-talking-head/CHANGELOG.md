# Changelog

Định dạng tự do (không theo Keep a Changelog), mốc theo `metadata.version` của `SKILL.md`.

## [1.2.3] — 2026-09-26

Sửa sau lô b05 (spec `docs/specs/2026-09-26-talking-head-1.2.3-design.md`).

- F1 (R221, lô b05 video 30/40/45/46): BUILD tự áp hero thì ghi dòng PLAN vào STATE.md rồi dừng sớm, agent chạy lại đúng lệnh BUILD — hết bị terminal cắt ở 420 s và _require_rows chặn lần chạy lại; giới hạn 2 vòng tính qua các lần chạy lại.
- F2: BANNED thêm từ sinh chữ trên giấy ghi chú / checklist / màn hình chat (note, checklist, checkbox, written, bullet, handwritten, chat, message, texting…).

## [1.2.2] — 2026-09-26

Sửa sau lô b04 (spec `docs/specs/2026-09-26-talking-head-1.2.2-design.md`).

- F1: FACE_ROOM mà mọi lớp đều có hero một hàng qua PLAN --check ⇒ BUILD tự gộp vào plan.json (bản cũ ở out/safe/plan_before_autohero.json), ghi lại edit.json và dựng lại từ planner (tối đa 2 vòng); còn lại FAIL như cũ (b04: 8/10 video phải mở lại PLAN chỉ để dán dòng GỘP SẴN).
- F2: BANNED thêm từ sinh nhãn/chữ, số liệu giả, logo, nhân vật có bản quyền (side-by-side, split screen, graph, metrics, youtube, game character…); «Sửa:» của BROLL_PROMPT chỉ cách viết thay; §B/PLAN.md: cùng sản phẩm tả cả dáng + màu.
- F3: ảnh B-roll có viền đều (trắng/đen, chuyển đột ngột) được cắt trước khi phủ khung (b04 v12 B4).
- F4: render_video.py in GỢI Ý thiếu RAM khi Remotion báo «No frame found at position».

## [1.2.1] — 2026-09-24

Sửa sau lô b03 (spec `docs/specs/2026-09-24-talking-head-1.2.1-design.md`).

- F1: face_safe dùng ảnh dò không hook (`face_png`) cho lớp hiện lúc tít hook còn trên hình — trước đây tít hook bị tính là chữ của thẻ đầu ⇒ FACE_ROOM giả; b03 video 6/12/13 phải bỏ hook (R208/R210).
- F2: `broll_plan.recommend` dưới sàn độ phủ ⇒ lấy bộ gom theo thời gian (b03 video 11: 22 % → 26 %); §B in sàn/trần/số ô/khoảng cách thật và phủ của đề xuất.
- F3: `broll.style_suffix` thêm «unbranded generic products and devices»; §B + PLAN.md: cùng sản phẩm ⇒ chép nguyên một cụm mô tả vào mọi prompt, không tên hãng.
- F4: assets.json có `fallback_reason`; VERIFY ghi lý do clip rơi về ảnh (vd 403 spending-limit của xAI).
- R217 (2026-09-26, lô b04 video 22): dò lại cue trên mix/final bằng tương quan chéo chuẩn hoá (`audio.match_at`, dùng ở `mux.cue_offset_f` và L11 `lint_post._cue_offset_f`) — tương quan thô bị giọng to kéo lệch, báo lệch giả +8,72 f cho whoosh −28 dB trong khoảng lặng trước giọng −19 dB.

## [1.2.0] — 2026-09-23

- R209 (2026-09-24, lô b03 video 6/12): Subtitle.tsx — dòng cuối của thẻ rơi từ trên xuống (trượt từ dưới lên làm chữ + quầng nhoè chui qua đáy vùng an toàn, text_safe FAIL khi khung dò trùng lúc từ đang hiện); HERO_ROW_FIT 0,98 → 0,95 (quầng nhoè ngang + advance đo hụt).

- R207 (2026-09-24, lô b03 video 4): build._plan_passes chép thêm meta.json vào thư mục tạm — thiếu nó thì plan có B-roll trượt BROLL_FORBIDDEN khi chạy thử, mọi gợi ý FACE_ROOM bị bỏ («không có gợi ý tự động»).

- R206 (2026-09-24, lô b03): PREP.md §4 — mặc định `broll_class` `light` cho lô dựng bằng 1.2.0; `none` chỉ khi user ghi rõ; ví dụ khuôn có một video light. OPERATOR.md: ví dụ lệnh intake dùng `--rules 1.2.0`.

B-roll AI cắt cảnh toàn màn hình (D-B1–D-B7): bổ sung ô B-roll tại PLAN và PLAN-SHEET (§B) với prompt tiếng Anh; bước BUILD `broll_assets` tự động sinh ảnh tĩnh (`ag/nano-banana`) kèm hiệu ứng đẩy nhẹ hoặc tối đa 1 video clip (`xai/grok-imagine-video`) qua 9router (cổng R0b); component Remotion `Broll.tsx` dựng B-roll đè toàn màn hình dưới phụ đề; âm thanh `broll_in` (B11) kích hoạt tại mốc chuyển cảnh; kiểm định V8 trong `verify.py` xác thực hiển thị B-roll thực tế tại khung hình giữa slot và chống phẳng ảnh; bộ luật mới `broll.*` cùng `sfx.sync_frame.broll_in`; các phán quyết Ruling R200–R203; cổng đo R0b đạt chuẩn; nâng cấp hợp đồng kế hoạch sang `plan/2` (tương thích ngược hoàn toàn với `plan/1`).

### Phán quyết đáng chú ý

- **B-roll AI cắt cảnh toàn màn hình (D-B1, D-B2, Ruling R202)**: B-roll dựng đè toàn bộ khung hình người nói (full coverage) trong khoảng 2–4 s mỗi slot; tiếng avatar và phụ đề vẫn chạy liên tục xuyên suốt; hỗ trợ ảnh tĩnh AI tạo bởi `ag/nano-banana` kết hợp hiệu ứng đẩy (push) nhẹ hoặc tối đa 1 clip động `xai/grok-imagine-video` cho mỗi video; sinh asset hoàn toàn tự động trong bước BUILD `broll_assets` mà không phát sinh thêm card kanban.
- **B-roll AI không bao giờ là bằng chứng (Ruling R200, B16)**: B-roll AI chỉ dùng cho mục đích minh hoạ hoặc bối cảnh không gian; các video nhóm `heavy` bắt buộc đặt `claim_gate: true` và báo cáo chỉ rõ các cảnh quay thực tế còn thiếu.
- **Không in nhãn AI trực tiếp lên khung hình (Ruling R201, B17)**: Giữ nhất quán với bản dựng avatar không nhãn của 1.1.1; công bố nhãn AI qua tính năng gắn nhãn của nền tảng khi đăng tải, được tự động nhắc nhở trong `EDITOR-REPORT.md`.
- **Giới hạn độ phủ B-roll tối đa 40% (Ruling R203, B04)**: Khống chế tổng thời lượng B-roll trong khoảng 25–40% tổng độ dài video (dưới 45–60 s) để bảo đảm không làm lu mờ gương mặt người nói; trần 40% là cổng kiểm tra cứng bắt lỗi `BROLL_COVER_OVER`.
- **Cổng đo R0b đạt chuẩn (2026-09-23)**: Thử nghiệm thực tế với 9router xác nhận tích hợp thành công model ảnh `ag/nano-banana` và video `xai/grok-imagine-video` (chi phí ~0,35 USD/clip, thời gian phản hồi ~40 s).
- **Âm thanh và hình ảnh đồng bộ (B11, V8)**: Tiếng động chuyển cảnh `broll_in` bám dính cue và xuất hiện cùng frame chuyển cảnh B-roll; khâu kiểm định V8 bảo đảm B-roll thực sự hiển thị trên video render cuối cùng và kiểm tra độ lệch chuẩn ánh sáng chống khung hình phẳng.
- **Nâng cấp schema kế hoạch sang `plan/2`**: Bổ sung trường `broll` vào schema kế hoạch; hỗ trợ trích xuất và kiểm tra độc lập; tương thích ngược hoàn chỉnh với các kế hoạch chuẩn `plan/1`.

## [1.1.1] — 2026-09-16

Bản sửa lỗi canary toàn diện sau đợt dựng thử nghiệm video 16: giải quyết triệt để 5 khuyết điểm nhìn thấy (D1–D5), 2 lỗi luồng agent (G11-1, G11-3), và các lỗi tiềm ẩn P1–P13 phát hiện trong quy trình. Bổ sung bước BUILD `face_safe` đảm bảo chữ không đè miệng người nói (D1, P2), sửa lỗi móc chữ ư bị cắt khi render qua paint pad + `ink.ts` (D2), chuẩn hoá ngắt câu/ngoặc kép qua textmarks (D3), chống xé từ ghép tiếng Việt và giữ dấu câu nội tại qua lexicon (D4, P6), chống cụt từ cuối và trôi từ dính (D5), thay thế hoàn toàn cơ chế agent tự sinh script nháp bằng hợp đồng kế hoạch tất định qua `plan.json` và chặn `PLAN_DRIFT` (G11-1, G11-3, P1), tự động hoá đề xuất thẻ liệt kê bước qua candidate S (P3), khoá từ dính `glue` tránh rớt dòng chữ hoa/CTA (P5), triệt tiêu frame đen đầu video và đuôi video bị cụt (P7, P8), cắt cảnh đúng điểm lặng qua `CUT_SNAP` (P9), hồi phục SFX cho CTA (P10), lọc trùng whoosh và bảo đảm âm thanh gắn liền sự kiện hình ảnh (P11), chọn offset BGM theo độ dải động tối thiểu tránh tăng âm đột ngột (P12), hoãn cân chỉnh SFX ngoài dải giọng sang R1 (P13), và chỉ thêm chi phí mềm `side_char_over` cho dòng nhỏ dài (P4 — không có cổng chặn, để vòng hiệu chỉnh R1).

**Ghi chú khoá version (phán quyết R50):** 1.1.1 thêm luật và thêm một bước BUILD (`face_safe`) — theo đúng quy ước ghi trong mục `[1.1.0]` thì đó là mức **minor**. Nhưng user đã quyết định gọi là **"1.1.1 sửa lỗi canary"** (phán quyết R50), vì mọi thay đổi đều nhằm sửa các khuyết điểm của lần dựng canary video 16 và schema `edit/1.1` chỉ đổi ba chỗ tương thích (`shots[].y ≤ 0`, hai trường tuỳ chọn `words[].glue` và `steps.rows`).

### Phán quyết đáng chú ý

- **Hợp đồng PLAN mới (`plan.json` + `PLAN-SHEET.md`)**: Giải quyết tận gốc G11-1, G11-3 và P1. Agent không viết file nháp ngoài quy trình hay tự sửa `edit.json` mà chỉ điền 5 quyết định vào `plan.json` (`hook/emphasis/steps/cta/hero`) từ các ứng viên sinh tự động; code dựng (`compose`) tự động ráp `edit.json`; `verify.py` kiểm tra ráp lại độc lập và bắt lỗi `PLAN_DRIFT` nếu có can thiệp tay. `PLAN-SHEET.md` là tài liệu duy nhất agent cần đọc ở khâu PLAN.
- **Đóng lỗi G11-1 bằng số đo**: `compose(recommended_plan)` đạt 0 lỗi trên 12/12 video thật (v2, v16 và 10 fixture thật), số ghi chú chỉ 0–5 mỗi video. Hàm `editschema.propose` cũ của 1.1.0 (nguồn gốc khiến agent lạc lối sinh script nháp) đã bị xoá hoàn toàn cùng 135 dòng mã phụ trợ, có test chặn tái phát.
- **Đối chuẩn canary trên video 2**: Bản dựng 1.1.0 của video 2 lộ đúng 8 lỗi dưới bộ luật 1.1.1: 6 lỗi `TIERS` (hero 3 tầng 10–23 ký tự vượt trần 8 ký tự), 1 lỗi `STEPS_SHOT` (thẻ liệt kê nằm trên cảnh cỡ 1,04 — thẻ liệt kê phải nằm trong cảnh cận, cỡ ≥ 1,14), 1 lỗi `BLOCK_LEN` (thẻ cuối 1,35 s trên hình) — khớp chính xác các khuyết điểm đã ghi nhận từ canary.
- **Bảo vệ khuôn mặt (`face_safe` — D1, P2)**: Thêm bước BUILD `face_safe` với thuật toán FACE_FIT (nâng trục y, kẹp trần s1, đẩy rộng s0) và cổng kiểm tra FACE_ROOM / `facesafe.check`, bảo đảm phụ đề không chạm vùng miệng người nói tại các block có nguy cơ (b12, b13, b19 trên v16).
- **Phục hồi dấu tiếng Việt và chữ dính (`ink.ts`, lexicon — D2, D4, P5)**: Bổ sung khoảng đệm vẽ (paint pad) trong `Subtitle.tsx` và vùng dành cho nét chữ `ink.ts` (sinh tự động) để móc chữ ư không bị cắt (như "tính từ" thành "tính tù" ở D2); tích hợp bộ từ điển ghép tiếng Việt giữ dấu câu nội tại (`COMPOUND_SPLIT`, `DISPLAY_PUNCT`), khoá trường `glue` theo cặp từ trong lexicon, chuỗi chữ hoa và từ khoá CTA để chống rớt dòng ("UGC THOẠI", "tự nhiên").
- **Nhận diện số và chuẩn hoá từ khoá CTA**: Phép thử "từ là số" loại trừ «một», «không», «thứ N» để tránh sinh nhầm hook «KHÔNG» ở giây 1,5 của v16; từ khoá CTA chỉ ép làm hero trong vùng CTA (ngoài vùng là điều kiện loại S20), chuẩn hoá cách đọc số («7 NGÀY» ↔ «bảy ngày»), hỗ trợ động từ CTA hai từ («bình luận») và mở rộng cụm từ khoá đơn («Bình luận BRIEF»); nếu từ khoá gây lỗi 3 tầng TIERS thì ngắt thẻ ngay sau từ khoá.
- **Giữ trần hero một dòng `text.hero_one_row_chars` = 8**: Đo lường thực tế bằng PIL trên Subtitle.fitSize chứng minh nới trần sẽ làm lỗi tràn biên P4 quay lại; bác bỏ đề xuất phạt "hero hai dòng" vì đo đạc thực nghiệm trên v16 cho thấy hero bị hạ xuống các từ phụ không mong muốn («NHÂN VẬT», «ĐANG KỂ»).
- **Khử trùng lỗi và chuẩn hoá cấu hình**: Lỗi trùng lặp từ hai nguồn được gộp theo cặp `(mã, vị trí)` và ưu tiên giữ câu thông báo có hướng dẫn sửa lỗi; chuẩn hoá `plan.emphasis_min_video_s` = 30 khớp chính xác tài liệu thiết kế §11.
- **Sửa sau lần dựng lại canary video 16 (2026-09-17)**: cổng `face_safe` kiểm thật các lớp chữ (trước đó khoá mặt nạ sai nên kiểm 0 lớp) và kiểm mỗi khung theo đúng shot `Footage.tsx` vẽ ở mốc cắt lẻ khung; vòng FACE_ROOM cộng dồn — BUILD lưu `out/safe/face_room_plan.json`, PLAN nạp sẵn plan đó vào `plan.json` (mục §0b).
- **Hero một hàng (`hero_row`, `text.hero_row_max_chars` = 16 — lô b01 nới từ 14 cho từ khoá CTA)**: hero ghi đè (`plan.hero`) dài 9–16 ký tự dựng MỘT hàng, cỡ co theo bề rộng glyph thật (`ink.ts` ADV do `tools/make_ink_table.py` sinh) — giữ cụm có nghĩa («kể trải nghiệm», «dễ hình dung») thay vì đổi sang từ nối ≤ 8 ký tự («đang kể», «Nó khiến»). Gợi ý FACE_ROOM ưu tiên hero một hàng và chỉ in phương án đã chạy thử qua PLAN `--check`. Trần 8 ký tự của hero ba tầng thường giữ nguyên.
- **Ngưỡng giọng S28 `voice.tilt_min_db` −8,5 → −9,5 dB (2026-09-17, lô b01)**: đo 58 video HeyGen cùng giọng — trung bình −8,11 dB, lệch chuẩn 0,40, thấp nhất −8,91; ngưỡng cũ chặn 8/58 (có canary 21) dù không có cụm giọng hỏng riêng. User nghe A/B rồi duyệt.

## [1.1.0] — 2026-09-12

Tái cấu trúc lớn: rules-as-data (`rules.json` + `rules.schema.json`), planner
SFX/BGM tất định theo khoảng ngắt (S01–S29), một trục âm thanh duy nhất (stem +
mux ffmpeg), ánh xạ video↔kịch bản theo nội dung (không dán tay), stage PREP,
pipeline 4 card/video trên Hermes kanban, và `verify.py` (V1–V7) tất định.

**Ngoại lệ khoá version (spec §4.3):** 1.0.0 → 1.1.0 là lần **duy nhất** một
bản minor được phép đổi cả schema (`edit.json` 1.0 → `edit/1.1`, chỉ số từ thay
vì giây) và thứ tự pipeline trong một lần. Từ bản này trở đi: patch = đổi số
luật hoặc sửa lint; minor = thêm luật/stage; major = đổi schema hoặc thứ tự
pipeline.

### Phán quyết đáng chú ý

- **R9** — khâu đỉnh giọng (`thlib/voice.py`): chain gain tuyến tính → `alimiter`
  (ngưỡng = trần TP đích − 0,5 dB, `level=false`, `latency=true`) → loudnorm
  tuyến tính hai lượt; `vo_clear` raise khi ffmpeg báo lượt phi tuyến. Lý do:
  giọng HeyGen có PLR 13,9–16,3 dB nên đạt −16 LUFS với TP ≤ −2 dBTP không thể
  chỉ bằng gain tuyến tính; limiter look-ahead là thực hành R128 chuẩn, đo tốn
  ≤ 0,08 LU và giữ xcorr ở −0,08 ms.
- **R19 / R35** — khâu đỉnh cho final/nobgm/social (`thlib/mix.py`): R19 áp lại
  đúng pattern R9 cho mix cuối; R35 tinh chỉnh riêng cho **file social giao
  cho user**: loudnorm tuyến tính hai lượt trên `mix.wav` (lossless, chưa
  encode) qua limiter true-peak (ngưỡng = trần đích − 0,5 dB) rồi mới encode
  AAC, đo lại TP như L11 và hạ trần thêm đúng phần vượt + 0,1 dB, tối đa 3 lần
  thử — vì bộ limiter theo mẫu của R19 áp trực tiếp lên AAC fail TP sau khi
  encode lần hai (cộng thêm 0,09–3,2 dB không đoán trước được) trên 6/6 project
  thật; cách của R35 đạt 6/6, 5/6 ngay lần thử đầu ở −2,0 dBTP.
- **R26 / R29** — probe text-safe (`check_text_safe.py`, `Subtitle.tsx`): R26
  giữ nguyên nghĩa đen "alpha > 0 ngoài hộp là FAIL" của B14, nhưng probe render
  `TextOnly` **tắt trang trí** (glow, drop/text/box-shadow, backdrop-blur) —
  chỉ đo glyph và nền/viền thẻ, pill; R29 giữ nguyên bốn loại tắt của R26
  nhưng vẫn đo blur/opacity chuyển động, và thêm quy tắc
  `steps.out = min(item cuối.e + 0,15; block sau.show đầu tiên − 0,10)` để thẻ
  liệt kê tắt trước khi block sau hiện. Lý do: đo `alpha > 0` trên hiệu ứng mềm
  từng ép layout che miệng người nói ở Task 11; ý B14 là chữ không đè lên UI
  nền tảng, không phải cấm mọi hiệu ứng mềm.
- **R30 / R31** — từ cuối mỗi block đọc được (`thlib/picture.py`,
  `Subtitle.tsx`): R30 bắt từ cuối mỗi block đậm ≥ 90 % trong ≥ 3 frame liền
  trước khi tắt, dùng chuyển nhanh 2 khung khi thoát thường 6 khung sẽ cắt mất
  nó; R31, khi vẫn không đủ, dời mốc hiện (`display_shift_s`) ≤ 0,15 s mỗi từ
  (từ bị lùi ≤ 0,10 s sau onset thật, sự kiện đã đồng bộ không bao giờ dời) —
  còn lại thì gắn cảnh báo `LAST_WORD_TIGHT` (CONCERN, không FAIL). Lý do:
  7/17 block của video 02 cắt mất từ cuối ở bản 1.0.0 — một lỗi phụ đề thấy
  được; sau R30–R31 cả 17/17 block đọc được.

### Thêm

- `thlib` (pure functions, unit test riêng) + CLI mỏng trên `stage.py`:
  P0 (`intake.py`, `make_cards.py`) → PREP → APPROVE-PREP → INTAKE → PLAN →
  BUILD → VERIFY → APPROVE-CANARY (spec §9, §10).
- `rules.json` + `rules.schema.json`: mọi số nằm trong dữ liệu, khoá qua
  `rules.lock` + `releases/1.1.0/MANIFEST.sha256` (spec §4.3).
- `verify.py` (V1–V7) tất định; `check_prep.py`, `check_text_safe.py`.
- `releases/1.1.0/stages/OPERATOR.md` cho opa-operator (Ruling R15); `collect_kpi.py`
  gom `out/verify/kpi.json` vào `_batches/<b>/kpi.jsonl`, in danh sách video gửi user
  duyệt (D5) và xoá `node_modules` khi đóng lô.
- `tools/check_drift.py` (M0, chỉ đọc; 9 mục, gồm con trỏ SOUL.md của operator/
  editor/verifier và board `vm-heygen-1` + card `t_81a309b2` đã archive — spec
  §13.1 mục 2 và 4 — và thư mục skill đang dùng sạch theo git) và `tools/make_manifest.py` — công cụ dev, để ở `tools/` vì
  Hermes không liệt kê thư mục này cho worker.

### Đổi

- Schema `edit.json`: 1.0 (giây) → `edit/1.1` (index từ trong `words.json`).
- Trục âm thanh: một stem duy nhất render bằng Python + mux ffmpeg, thay chuỗi
  ghép tay nhiều lớp của 1.0.0.
- `SKILL.md`: từ quy trình đầy đủ (agent tự viết `edit.json`, tự build/render)
  thành router ≤ 40 dòng trỏ vào `stage.py` + `stages/PREP.md` / `PLAN.md` —
  bản 1.0.0 vẫn xem được qua `git show v1.0.0:SKILL.md`.
- **R36** — bố cục gốc skill: `references/`, `scripts/` (`new_project.py`),
  `assets/` (pack SFX 1.0.0), `template/`, `examples/` của 1.0.0 chuyển vào
  `legacy/1.0.0/` (giữ nguyên cấu trúc bên trong, `new_project.py` vẫn chạy tại
  chỗ). Lý do: Hermes đưa `references/`, `templates/`, `assets/`, `scripts/` ở
  gốc skill vào prompt của mọi worker như "supporting files" — tài liệu 1.0.0
  (schema tính bằng giây) ở đó mở lại kênh trôi "chép từ bản trước" (spec §4.3).
  Tag `v1.0.0` giữ bố cục gốc.
