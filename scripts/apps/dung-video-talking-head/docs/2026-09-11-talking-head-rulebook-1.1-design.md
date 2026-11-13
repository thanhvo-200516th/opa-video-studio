# Bộ luật dựng talking-head 1.1 + dây chuyền giao việc OPA — Thiết kế

- **Ngày:** 2026-09-11 (bản 2: đã sửa theo 2 vòng soát chéo độc lập và whisper kiểm lại)
- **Trạng thái:** chờ user duyệt spec, sau đó lập kế hoạch triển khai.
- **Phạm vi:** skill Hermes `dung-video-talking-head` (1.0.0 → 1.1.x cho A-roll, SFX, nhạc nền, PREP; 1.2.0 cho B-roll), cùng quy trình opa-operator / opa-editor / opa-verifier cho khoảng 60 video HeyGen.
- **Bằng chứng:** `2026-09-11-rulebook-evidence/`
  - `audit/`: đo video 2; bảng ghép video ↔ kịch bản.
  - `prototype/`: planner đã chạy thật trên video 2.
  - `research/`: nghiên cứu có nguồn, phản biện, bản chốt workflow.

---

## 0. Tóm tắt

**Chẩn đoán.** Video 2 nghe bị "chồng" vì SFX **gắn theo chữ trên hình, không gắn theo hơi thở của giọng**:
- 25 cue trong 43 s; 23/25 đỉnh rơi vào lúc đang nói.
- Khoảng 9–12 s SFX đè lên lời.
- File bass gần như câm trên loa điện thoại.
- Track âm thanh trễ 42,7 ms.

Luật chỉ nằm trong văn xuôi, số bị dán vào brief, nên lỗi trôi từ video này sang video khác.

**Thiết kế (hướng B đầy đủ).** Luật thành **dữ liệu có version**, cộng **code tất định** tự đặt tiếng, **lint** chặn sai, **4 card mỗi video**. Agent chỉ phán đoán ở **ba chỗ**: PREP (phiếu chuẩn bị), PLAN (chữ, hook, CTA), B1 (kế hoạch B-roll).

**Chạy thử planner trên dữ liệu thật video 2:** 25 → **8 cue**, 8/8 trong khoảng ngắt, 0 ms đè lời, tối đa 2 cue/5 s. Hook nghe rõ trên loa điện thoại (−6 dB phone-A so với giọng; trước là −36 dB). **Chưa ai nghe bản này**, mọi mức hiệu chỉnh ở R1.

**Hai phát hiện khi soát spec (đã kiểm bằng whisper):**
1. Folder `Vid Heygen/<n>` đi theo số của **file HeyGen v3**. File đánh giá và file đạo diễn **lệch số từ mục 06**, nên mọi phép ghép phải theo **nội dung**, không theo số.
2. Một số mp4 **đọc nguyên placeholder** (31, 33, 37) hoặc **đọc cả chỉ dẫn motion** (38). Những video này phải **render lại trên HeyGen** trước khi dựng (§7.1).

### 10 luật vàng (bản 1 trang cho người)

1. **Lời nói là neo.** Sự kiện hình chỉ là *ứng viên* để có tiếng.
2. **SFX chỉ nằm trọn trong khoảng ngắt thật** của giọng (đo bằng năng lượng; ≥ 250 ms, riêng tầng C ≥ 210 ms), tắt trước từ kế tiếp 60 ms. Không tiếng nào đè lời.
3. **Mỗi lúc chỉ có giọng + nhạc nền + tối đa 1 SFX.** Mỗi khoảng ngắt tối đa 1 cue.
4. **Nhịp (standard):**
   - đỉnh cách nhau ≥ 1 s;
   - ≤ 2 cue/5 s, ≤ 3 cue/10 s, cả video ≤ ceil(2,5 × giây/10);
   - tầng A ≤ 4 và cách nhau ≥ 6 s;
   - không để quá 8 s im nếu còn chỗ đặt.
5. **Mỗi giai đoạn một họ tiếng:** hook/chữ đập = impact đơn (không dùng bass), chuyển ý = whoosh mềm, thẻ = slide, CTA = sparkle. Hero script, cắt nhảy, mục liệt kê: không tiếng.
6. **Mức theo tầng so với giọng, đo như loa điện thoại:** A −3, B −8, C −12 dB. Không bao giờ to hơn giọng. Nhạc nền tĩnh, thấp hơn giọng 15 LU.
7. **Khớp frame:** đỉnh tiếng rơi đúng frame chữ đạt 90% chuyển động. Giọng, SFX và nhạc chung một trục mẫu.
8. **Hook hai lớp:** tít có từ giây 0 và không có tiếng; cú đập gắn với từ reveal trong 3,5 s đầu.
9. **CTA chỉ một tiếng**, trong ±1 s quanh nó không có tiếng khác.
10. **Không ai đặt số tay.** Planner sinh, lint chặn, verifier đo lại. Đổi luật chỉ qua version mới.

---

## 1. Bối cảnh, mục tiêu, tiêu chí thành công

**Bối cảnh:**
- Khoảng 60 video HeyGen dọc (nguồn 2160×3840 @25fps, tiếng Việt, 40–60 s).
- **Composition và bản xuất: 1080×1920 @30fps.** Mọi frame trong luật tính ở 30 fps (`rules.json → fps`); nguồn 25 fps chỉ là đầu vào.
- Tài liệu (§6):
  - lời chuẩn: `60 kịch bản HeyGen v3 — phiên bản 45–60 giây.md`;
  - kịch bản đạo diễn: `60-kich-ban-video-ngan-ai-vm-dabest.md`;
  - phân loại: `60-kich-ban-heygen-talking-head.md`.
- Người thực thi là agent Hermes:
  - opa-operator: grok-4.6, dispatcher;
  - opa-editor: **gemini-3.8-flash**, 60 lượt gọi model mỗi lượt chạy;
  - opa-verifier.

**Mục tiêu:**
1. Luật SFX và nhạc nền rõ ràng, có số, có căn cứ, chống chồng lớp, tôn trọng ngắt nghỉ.
2. Dây chuyền cố định, giao việc khoa học, giữ "tư duy dựng" khi nhiều agent làm và khi thêm B-roll sau.
3. Sản xuất hàng loạt mà không trôi luật.

**Tiêu chí thành công (đo được):**
- 100% video qua `verify.py`, lint L1–L14 PASS.
- 0 ms SFX đè lời; mật độ nằm trong ngân sách preset.
- Loudness final −16 ±0,5 và social −14 ±0,5 LUFS; TP ≤ −1,5 dBTP.
- **Âm thanh:** xcorr(final, mix) ≤ 2 ms. **Tiếng so với hình:** đỉnh cue lệch frame đồng bộ trong −1/+2 f.
- Ngân sách lượt theo stage đúng bảng §9 (INTAKE ≤ 15, PLAN ≤ 25, BUILD ≤ 15, VERIFY ≤ 20, PREP ≤ 25, B1 ≤ 20); không card nào chạm trần 60 — đo sau lượt chạy (ghi chú dưới bảng §9).
- Không card nào chứa số kỹ thuật.
- Sau R1: user nghe video mốc và không còn chê "chồng" hay "bé".

---

## 2. Quyết định đã chốt

| # | Quyết định | Nguồn |
|---|---|---|
| D1 | Âm hưởng **vừa phải** → preset `standard` là mặc định của kênh. calm và punchy vẫn nằm trong rules.json cho A/B ở R1 và cho F1. | User |
| D2 | **Có nhạc nền** rất nhỏ, dùng bài cố định cho cả series, lấy từ **thư viện free có license rõ**. User nghe và chọn **1–3 bài**. Chọn 1 bài thì mọi video dùng bài đó; chọn nhiều thì xoay tất định. | User |
| D3 | Nguồn B-roll: **ảnh/clip AI** (Grok qua 9router), **quay màn hình** (user), **stock có license**. | User |
| D3a | *Đề xuất, chờ user xác nhận:* stock chỉ dùng cho bối cảnh, không bao giờ làm "bằng chứng" (B16). | Nghiên cứu/pháp lý |
| D4 | **Bước 0 đọc kịch bản**, phân loại nhu cầu B-roll và báo user chuẩn bị trước (PREP, §7). | User |
| D5 | Duyệt: **video canary mỗi đợt duyệt kỹ** (gồm cả kế hoạch B-roll của nó, nếu có), sau đó ngẫu nhiên 1/5, cộng mọi `DONE_WITH_CONCERNS` và mọi video có claim_gate. | User |
| D6 | B-roll vào **tuỳ kịch bản**: `none` / `light` (agent làm) / `heavy` (chờ asset của user; **không tự bỏ**). | User |
| D7 | Hướng **B đầy đủ**: luật là dữ liệu, planner tất định, stem âm thanh, lint, 4 card/video, verify.py, chuỗi provenance. | User |
| D8 | Luật và code nằm trong **git ngay trong** `shared-skills/video/dung-video-talking-head/`, có `releases/<ver>/` và tag. | User |
| D9 | M0 đổi cấu hình Hermes: **mọi thứ trừ `auto_decompose`**. | User |
| D10 | Lời chuẩn = VIDEO SCRIPT trong file HeyGen v3. Đối chiếu: 01 khớp 94,5%, 02 khớp 98,1%. | User + đo |
| D11 | **Chỉ làm video chưa dựng.** Video 1–2 giữ bản đã giao; dữ liệu video 2 chỉ dùng làm fixture kiểm thử. | User |
| D12 | Không ghi API key vào file nào. Code dùng biến `NINEROUTER_API_KEY` và base_url trong config Hermes. | Bảo mật |
| D13 | *Phát hiện, chờ user xác nhận cách xử lý:*<br>• video ghép với kịch bản **theo nội dung**;<br>• video đọc placeholder hoặc chỉ dẫn motion → trạng thái `needs_rerender`, user render lại trên HeyGen. | Soát chéo + whisper |

---

## 3. Chẩn đoán hiện trạng (chi tiết: `audit/`, `research/final_diagnosis_markdown.txt`)

| Chỉ số (video 2) | Hiện tại | Planner 1.1 (mô phỏng thật, standard) |
|---|---|---|
| Số cue / cue mỗi 10 s | 25 / 5,8 | **8 / 1,85** |
| Nhiều nhất trong 5 s / trong 2 s | 6 / 4 | **2 / 1** |
| Khoảng cách đỉnh–đỉnh nhỏ nhất / median | 124 / 1263 ms | **2767 / 4967 ms** |
| Đỉnh cue nằm trong khoảng ngắt | 2/25 | **8/8** |
| SFX đè lời (đường bao −40 dB) | 9,2 s (đo lỏng hơn: 11,9 s) | **0 s** |
| Hook / stomp b07, phone-A so với giọng | −35,9 / −30,8 dB | **−6,0 / −6,0 dB** |
| True peak của mix | −0,35 dBTP | **−1,5 dBTP** |

**Nguyên nhân kỹ thuật:**
1. 13/13 block tự sinh cue.
2. Mốc whisper nuốt 20/21 khoảng ngắt; onset sau khoảng ngắt sớm 232–689 ms.
3. File không hợp loa điện thoại: bass-hit-short 99,5% năng lượng dưới 250 Hz, swoosh-quick 94%.
4. Ducker đo trên 2.mp4 (−20,3 LUFS) thay vì vo-clean (−16,0).
5. Đuôi tiếng dài hơn khoảng ngắt; CTA bị đập đôi.
6. Hai trục thời gian: final.mp4 trễ 42,67 ms (bằng 2048 mẫu AAC priming). SFX được bù, giọng thì không.

**Nguyên nhân quy trình:**
1. Skill đứng yên ở 1.0.0; số trong brief trôi từ v5 sang video 2.
2. edit.json video 2 vi phạm 15 luật mà không script nào bắt.
3. Cổng kiểm không đo vị trí hay mức SFX.
4. Card t_81a309b2 gộp 6 bước, đốt 47/60 lượt vào 17 script thử whisper.
5. Không card nào qua verifier.
6. **Mới:** ghép video với kịch bản theo số là sai, và một số mp4 đã hỏng lời ngay từ lúc tạo trên HeyGen.

---

## 4. Kiến trúc

### 4.1 Ba tầng

| Tầng | Nội dung | Ai sửa |
|---|---|---|
| Luật (dữ liệu) | `releases/<ver>/rules.json` + `rules.schema.json`. Mỗi tham số có `value`, `source` (nhãn căn cứ) và `confidence`. Bất biến sau khi tag. | Phiên Claude Code / opa-dev-be, qua F1 |
| Máy (code tất định) | `stage.py` + các module (§4.2) | Như trên |
| Phán đoán | PREP (`stages/PREP.md`), PLAN (`stages/PLAN.md`), B1 (`stages/B1.md`, từ 1.2) | opa-editor |

`stages/PLAN.md` = nội dung chuyển từ `references/edit-json.md` của 1.0.0, cộng các quy tắc *phán đoán* trong `references/style.md`: ý nghĩa style/color, accent, xen toàn/cận, từ chỉ hướng → x, bảng steps → y, shot cuối đẩy vào CTA. Kèm `examples/edit.json` đã chuyển sang schema mới. **Tư duy dựng của 1.0.0 được giữ, chỉ đổi chỗ ở.**

### 4.2 Cấu trúc thư mục

```
shared-skills/video/dung-video-talking-head/        ← git repo; tag v1.1.0, v1.1.1, v1.2.0…
  SKILL.md                     ← router ≤ 40 dòng: "đọc card → chạy stage.py <STAGE>"
  CHANGELOG.md
  releases/1.1.x/
    rules.json  rules.schema.json  MANIFEST.sha256
    template/                  ← Remotion chỉ render hình; comp đọc display_s
    scripts/
      stage.py                 ← điều phối INTAKE/PLAN/BUILD/VERIFY/PREP; append STATE.md; khoá
      intake.py  make_cards.py  check_drift.py                  (P0, M0)
      map_videos.py            ← ghép mp4 ↔ mục v3 ↔ dòng phân loại/đạo diễn theo nội dung
      check_prep.py
      vo_clear.py  align_script.py  voice_timing.py              (INTAKE: S28, §6, S04)
      propose_edit.py  validate_edit.py                          (PLAN)
      picture_lock.py  check_text_safe.py  planner_sfx.py  mix_audio.py
      lint_sfx.py  lint_rules.py  render_video.py  mux.py  make_report.py   (BUILD)
      verify.py                                                  (VERIFY)
      import_sfx.py  import_bgm.py                               (asset)
    stages/PLAN.md  stages/PREP.md  examples/edit.json
    sfx/  sfx_manifest.json
    bgm/  bgm_manifest.json
  tests/                       ← property test + fixture video 2 + fixture ghép kịch bản
  docs/                        ← spec này chép vào khi repo có 1.1.0

Vid Heygen/
  _batches/bNN/                ← cấp lô (operator/intake.py ghi)
    batch_manifest.json  mapping.csv  vo_script/<n>.txt (+ .sha256)
    prep/prep-<k>.json  PREP-SHEET.md  APPROVALS.md  kpi.jsonl
  <n>/
    <n>.mp4
    .stage.lock                ← khoá theo video, dùng chung mọi version
    edit-r1.1.1/               ← mỗi version luật một folder; không migrate tại chỗ
      rules.lock  STATE.md  meta.json  vo_script.txt  words.json  pauses.json
      fix.json  propose_edit.json  edit.json  overrides.json  picture_lock.json
      public/vo-clean.wav  sfx_stem.wav  bgm_bed.wav  mix.wav  mix-nobgm.wav
      out/final.mp4  final-nobgm.mp4  final-social.mp4
      out/sfx_plan.json  sfx_lint.json  QA.json  EDITOR-REPORT.md
      out/verify/VERDICT.{json,md}  out/verify/kpi.json
      out/r1-<variant>/        ← chỉ ở R1, không xuất bản
```

### 4.3 Khoá version và chặn trôi

- `rules.lock` = {version, sha256 của MANIFEST}. Mọi script đọc số **chỉ** từ `releases/<ver>/rules.json` theo lock. `lint_rules.py` so lock với release; lệch là FAIL.
- Card chỉ ghi `RULES: dung-video-talking-head@<ver>`. Hermes không khoá được version skill, nên khoá do `rules.lock`, lint và V1 làm.
- Đổi luật không làm thay đổi video đang dựng. Dựng lại theo luật mới thì mở folder `edit-r<ver mới>`.
- **Chặn các kênh trôi đã thấy:**
  - operator dán số → card con trỏ do script sinh;
  - copy component từ video trước → template lấy từ release;
  - `background_review` → tắt cho editor/verifier;
  - bản skill trong profile che bản shared → V1 kiểm;
  - summary "Recent work" mang thông số → summary do script in, không chứa số.
- **Version:**
  - 1.0.0 → 1.1.0 là lần tái cấu trúc duy nhất được phép đổi schema và pipeline trong một bản minor (ngoại lệ ghi trong CHANGELOG).
  - Sau R1: tag **1.1.1** với số đã chốt. Các lô sản xuất dùng @1.1.1.
  - Từ đó: patch = đổi số hoặc sửa lint; minor = thêm luật/stage; major = đổi schema hoặc thứ tự pipeline.

---

## 5. Luật âm thanh (S01–S29)

### 5.1 Định nghĩa đo

- **Downmix:** mono (L+R)/2.
- **Envelope:** RMS 20 ms, cửa sổ đặt giữa, bước ≤ 5 ms.
- **Khoảng ngắt [t0, t1]:** RMS < −35 dBFS liên tục ≥ 120 ms, trong đó có ≥ 60 ms < −45 dBFS. Ngưỡng tuyệt đối hợp lệ vì vo-clean đã chuẩn −16 LUFS; đổi đích loudness thì dời ngưỡng cùng số dB.
- **Onset thật:** mỗi t1 gán cho **từ sớm nhất** thoả s − 100 ms ≤ t1 ≤ e + 50 ms. Các từ sau giữ s whisper, kẹp ≥ onset trước + 20 ms.
- **phone-K:** HPF 300 Hz Butterworth bậc 4 → K-weighting BS.1770 → momentary 400 ms. Đây là miền **ra quyết định** mức.
- **phone-A:** HPF 300 Hz bậc 4 → A-weighting → 400 ms. **Chỉ để báo cáo.**
- **VO_REF:** median momentary phone-K của vo-clean trên các khung có RMS100 > −35 dBFS.
- **attack20 / tail30 / tail40:** mẫu đầu → đỉnh; đỉnh → lúc đường bao rơi −30 / −40 dB.
- **fps:** 30 (từ `rules.json`). Frame k ứng với thời điểm k/30 s.

### 5.2 Bảng luật

Cưỡng chế: `code` = planner/stage tự làm; `lint` = checker FAIL build.

Căn cứ:
- `[chuẩn]` = tiêu chuẩn;
- `[NC]` = nghiên cứu peer-reviewed;
- `[ngành]` = thực hành nghề (≥ 2 nguồn);
- `[đo]` = đo trên kênh;
- `[GĐ→R1]` = giả định có cơ sở, hiệu chỉnh ở R1.

Chi tiết từng căn cứ: `research/final_sfx_rulebook.txt` (rationale + evidence từng mã) và `research/rsfx.json` (URL).

| Mã | Luật | Giá trị | Cưỡng chế | Căn cứ |
|---|---|---|---|---|
| S01 | Tầng và hạng cố định; tranh chấp thì hạng cao thắng. | **A:** hook(1), stomp/quote/reveal(2). **B:** CTA(3), thẻ liệt kê(4), chuyển đoạn / vào B-roll(5). **C:** cắt zoom(6), lấp khoảng trống(7).<br>Bên thua: **GỘP** vào cue thắng; hoặc **CHỈ CHỮ** (A); hoặc **BỎ** (B/C).<br>**BỎ = không có tiếng; hình của sự kiện giữ nguyên thời điểm của chính nó.**<br>Hoà hạng: chọn slot xa các cue đã đặt nhất; vẫn hoà thì chọn cái sớm hơn. | code | [NC] Moreno & Mayer 2000; [ngành] |
| S02 | Sự kiện hình chỉ là ứng viên. | `auto_cue_per_block = false`.<br>Ứng viên chuyển đoạn, **cùng hạng 5**:<br>**(5a)** ranh giới đoạn văn trong vo_script, cần khoảng ngắt ≥ 250 ms (S05);<br>**(5b)** đầu block có khoảng ngắt ≥ 400 ms ngay trước.<br>5a và 5b trùng một khoảng ngắt thì gộp và ghi nguồn 5a. Phân bổ vẫn theo tie-break S01. `ellipsis` chỉ để báo cáo. | code | [ngành] "hit list là ứng viên"; [đo] §6.3 |
| S03 | Mỗi vai một họ tiếng; file chọn theo **ràng buộc đo của từng vai**; agent không chọn file. | Bảng `roles` trong rules.json:<br>• impact: 1 onset, attack20 ≤ 80 ms, <250 Hz ≤ 50%, crest phone-K ≤ 21 dB.<br>• sparkle, slide, whoosh, air: có trần attack20, tail30, crest và dải tần riêng.<br>Ở R0a chốt các trần sao cho đúng 10 file §5.5 PASS vai của mình và các file bị loại FAIL. **Số onset chỉ áp cho impact.**<br>Mỗi vai A/B có ≥ 2 file khác md5. | code | [đo] measure_files.py (39 file) |
| S04 | Mốc lấy từ năng lượng vo-clean, không lấy riêng s/e của whisper. | §5.1 | code | [đo] whisper nuốt 20/21 khoảng ngắt |
| S05 | Thân cue nằm trọn trong một khoảng ngắt. | PAUSE_MIN tầng A/B 250 ms, tầng C 210 ms. Mẫu đầu ≥ t0 + 20 ms. Tại t1 − 60 ms, RMS20 cue ≤ max(−50 dBFS, đỉnh − 30 dB). Tối đa 1 cue mỗi khoảng ngắt. Cue đè lời để v2. | code | [ngành] masking; [GĐ→R1] |
| S06 | Vị trí đỉnh theo mode. | **pre-hit** (mặc định): thân kết thúc tại t1 − 60 ms; đỉnh = t1 − 60 ms − đuôi_dùng.<br>`đuôi_dùng = min(tail30, max(30 ms, ((t1 − 60) − (t0 + 20)) − min(attack20, 60 ms)))`.<br>**post-hit** (chỉ hook/stomp; CTA theo S20): mẫu đầu = t0 + 20 ms; đỉnh = t0 + 20 ms + attack20.<br>Frame k = floor (pre) / ceil (post); đỉnh đặt đúng k/30.<br>Cắt pre-roll trước t0 + 20 ms. **Fade-in theo vai:** impact/sparkle 10 ms; whoosh/slide/air 30 ms. | code | [ngành]; prototype |
| S07 | Cửa sổ neo; dự phòng. | pre-hit: khoảng ngắt có t1 = onset thật (±20 ms) của từ neo; chữ hiện trước từ neo ≤ 600 ms.<br>post-hit: t0 ∈ [e − 100; e + 300] ms của từ cuối cụm.<br>Không có slot: A → CHỈ CHỮ; B/C → BỎ (trừ CTA theo S20). **Không bao giờ dời cue lên âm tiết đang nói.** | code | [NC] Coupé 2019; [ngành] |
| S08 | Đỉnh tiếng = frame đồng bộ của hình. | `display_s = đỉnh − SYNC_FRAME/fps` cho chữ, thẻ, pill của sự kiện có tiếng. Stomp có tiếng: top + hero hiện cùng lúc; bottom theo lời. Dung sai trên final: sớm ≤ 1 f, trễ ≤ 2 f. | code | [chuẩn] ITU-R BT.1359 |
| S09 | Số lớp. | Giọng + nhạc nền + **≤ 1 SFX** (đuôi tính tới −30 dB). v1 không có cue chồng nhau. | lint | [ngành] Murch "2,5 lớp" |
| S10 | Khoảng cách, cố định mọi preset. | Đỉnh–đỉnh ≥ 1000 ms. A↔A ≥ 6000 ms. Stomp↔stomp ≥ 8000 ms. Cùng file ≥ 5000 ms và không liền nhau cùng vai. ±1000 ms quanh CTA không có cue khác. | code | [ngành] ~1 nhịp thở |
| S11 | Ngân sách. | Theo preset (§5.3): MAX_5S, MAX_10S, `PER_VIDEO = ceil(k × thời_lượng_s / 10)`.<br>**Cố định mọi preset:** MAX_A = 4, trong đó ≤ 1 ở 0–3,5 s; cue cắt zoom (hạng 6) ≤ 2 mỗi video và không ở 2 cú cắt liên tiếp. | code | [ngành]; [GĐ→R1] |
| S12 | Đuôi và fade trộn sẵn vào stem. | Fade-out tuyến tính theo dB 80 ms (sparkle 120 ms), kết thúc tại t1 − 60 ms. Fade-in theo S06. Fade làm Mmax giảm > 3 dB thì thử file kế. | code | [ngành] forward masking |
| S13 | Cổng asset SFX. | `import_sfx.py`: decode → WAV 48 kHz → mono (L+R)/2 → HPF 120 Hz Butterworth bậc 2 → chuẩn hoá sample peak −1 dBFS (không limiter).<br>Manifest: md5, source_url, license, license_checked_at, lag, attack20, pre30, tail30, tail40, onsets, % năng lượng <250 / 250–1k / 1–4k / >4k, Mmax K, Mmax phone-K, crest.<br>Loại file license unknown hoặc trùng md5. | code | [đo] |
| S14 | Mức theo tầng so với VO_REF (phone-K). | **`gain_dB = (VO_REF + mục_tiêu_tầng) − Mmax_phoneK(cue đã cắt/fade)`**.<br>standard: A −3 / B −8 / C −12 dB.<br>TP cue ≤ −2,0 dBTP; trần TP buộc hụt > 1,5 dB thì thử file kế.<br>`sfx_plan` ghi mức ở phone-K, K và phone-A. | code | **[GĐ→R1]**: không có chuẩn nào cho mức SFX so với lời trong khoảng lặng |
| S15 | Không duck giọng. | Bỏ DUCK_DB. Tham chiếu = `public/vo-clean.wav`. Nhạc nền theo S29. | code | [ngành] giọng đã nén (LRA 2,8) |
| S16 | Vệ sinh phổ. | Loại file > 50% năng lượng dưới 250 Hz (sau HPF). Speech-safe để v2. | lint | [ngành] loa điện thoại; [đo] |
| S17 | Xoay vòng file tất định. | Theo thứ tự thời gian qua danh sách file của vai, bỏ qua file vi phạm S10. Jitter/pitch để v2 (seed sha256). | code | kỹ thuật |
| S18 | Loudness. | Sau khi trộn: **loudnorm 2 pass tuyến tính** cho mix → final −16 ±0,5 LUFS, TP ≤ −1,5. mix-nobgm cùng cách. social: 2 pass tuyến tính → −14 ±0,5, TP ≤ −1,5, 48 kHz.<br>S-max ≤ I + 5 LU. SFX làm tăng I ≤ 0,5 LU (đo trước chuẩn hoá). M-max mix ≤ M-max giọng + 1 LU. | lint | [chuẩn] EBU R128 s1; nền tảng re-encode |
| S19 | Không bao giờ có tiếng. | Cắt nhảy cùng cỡ; camera trôi; ra B-roll; hero script (trừ lấp S26); đổi dòng phụ đề; pop từng chữ; mục liệt kê (v1); tít hook 0–0,3 s; overlay disclosure AI; câu đùa/cảm xúc; mọi cue đè lời (v1). Cấm tone/bleep/notify, meme, laugh track. | lint (L13) | [NC] Newman & Schwarz 2018; feedback user "giống game" |
| S20 | CTA độc quyền, neo theo index từ. | Neo = `cta.range[0]` (bắt buộc). 1 cue tầng B pre-hit trong khoảng ngắt ngay trước từ neo; pill chạm đích ở frame đỉnh.<br>Không vừa pre-hit thì post-hit trong khoảng ngắt sau từ cuối (S27); **pill vẫn hiện ở đầu câu CTA và tại đó không có tiếng**. Không có slot sau từ cuối thì CTA không có tiếng.<br>±1000 ms im. Không block stomp nào chứa keyword CTA. | code | kỹ thuật |
| S21 | Timeline đổi thì tính lại toàn bộ; cấm đặt tay. | Đổi edit/broll/words/pauses/fix/overrides → planner chạy lại 100%. Lint so sha256 của sfx_plan với output planner. | lint (L10) | [ngành] khoá hình trước, âm sau |
| S22 | Hook hai lớp. | Tít hiện trước frame 9, giữ ≥ 1,5 s, không tiếng. `hook.hit_word` phải nằm trong hero stomp của một block **và có onset ≤ 3,5 s** (validate_edit kiểm); lời không có từ phù hợp thì bỏ `hit_word`, hook không có tiếng.<br>Thứ tự thử: pre-hit → post-hit ≤ 300 ms → chỉ chữ.<br>0–3,5 s: ≤ 1 cue tầng A; không B-roll trừ hook_proof. | code | [ngành]; kịch bản kênh "tắt tiếng vẫn hiểu" |
| S23 | Minh bạch. | `sfx_plan.json`: mọi ứng viên, quyết định (OK / GỘP / CHỈ CHỮ / BỎ), slot đã thử, mã luật, mức 3 miền. `sfx_lint.json`: PASS/FAIL kèm frame. `make_report.py` chép vào EDITOR-REPORT. | lint (L14) | kỹ thuật |
| S24 | SYNC_FRAME = frame đầu tiên animation đạt ≥ 90% tiến độ. | Chữ block (9 f outCubic) 5 f; thẻ (10 f) 6 f; mục liệt kê 5 f; pill CTA (12 f outBack) 4 f; tít hook 6 f; cú cắt 0 f. Unit test so với code template. ±1 f ở R1. | code | [đo trong code] |
| S25 | Một trục âm thanh. | `sfx_stem.wav` và `bgm_bed.wav` 48 kHz đặt trên trục vo-clean; `mix.wav` = vo + bed + stem; `mix-nobgm.wav` = vo + stem. Remotion chỉ render hình; ffmpeg mux. Bỏ `OUTPUT_AUDIO_OFFSET_F` và cột `from`.<br>Gate: \|xcorr(vo-clean, nguồn)\| ≤ 2 ms **(INTAKE)**; \|xcorr(final, mix)\| ≤ 2 ms và cue −1/+2 f **(BUILD, L11)**. | code | [đo] lệch 42,67 ms |
| S26 | Sàn mật độ. | MAX_GAP 8 s: đoạn > 8 s không có cue mà có khoảng ngắt ≥ 250 ms ở đầu một block chưa dùng thì thêm 1 cue C ở chỗ gần giữa đoạn nhất (tuân S05–S11); lặp lại. Không lấp được / < 3 cue / thiếu cả hook lẫn CTA → `WARN LOW_DENSITY` → `DONE_WITH_CONCERNS`. | code | [ngành] + [GĐ→R1] |
| S27 | Phần kết. | t_end = đầu khoảng ngắt sau từ cuối + 500 ms (≤ độ dài nguồn). Sau từ cuối không có cue mới trừ CTA dự phòng. Pill CTA giữ tới frame cuối. Fade audio 150 ms cuối. | lint | [ngành] + [GĐ→R1] |
| S28 | Chuỗi giọng `vo-clear-1`. | highpass 110 Hz; lowpass 10 kHz; EQ −6 dB @220 Hz (Q 1.1); +3,5 dB @3,5 kHz (Q 1.3); compressor thr −18 dB, ratio 2,2, attack 10 ms, release 90 ms, makeup 2 dB; loudnorm 2 pass tuyến tính → −16 ±0,5 LUFS, TP ≤ −2,0; WAV 48 kHz.<br>QA: tilt (1–3,5 kHz so với 250 Hz–1 kHz) ≥ −8,5 dB; 80–250 Hz so với 250 Hz–1 kHz ≤ −12 dB; xcorr ≤ 2 ms; ghi `voice_hf_ratio`. | code | [đo] chuỗi v5 + tilt.py |
| S29 | Nhạc nền. | §5.6 | code + lint (L12) | [ngành] lời ≥ 10 LU trên nhạc; nền ≥ 15 LU; [GĐ→R1] |

Luật hình dùng ngay từ 1.1.0: **B13** (ngân sách lớp hình) và **B14** (safe zone). Chúng nằm ở §8.2 nhưng phát hành cùng 1.1.0, vì BUILD có cổng text-safe.

### 5.3 Preset (cả 3 nằm trong rules.json)

| | calm | **standard (mặc định kênh)** | punchy |
|---|---|---|---|
| MAX_5S | 2 | **2** | 3 |
| MAX_10S | 2 | **3** | 4 |
| PER_VIDEO = ceil(k × giây / 10), k = | 2,0 | **2,5** | 3,0 |
| Mức A / B / C (dB so với VO_REF, phone-K) | −5 / −10 / −14 | **−3 / −8 / −12** | −2 / −6 / −11 |
| Mô phỏng video 2 | 7 cue | **8 cue** | 10 cue |

- Preset chỉ được đổi MAX_5S, MAX_10S, k và mức tầng. Mọi thứ khác cố định.
- Sau R1 chốt preset mặc định của kênh. Đổi preset cho riêng một video chỉ qua F1, kèm id feedback.

### 5.4 Bảng sự kiện → tiếng

| Sự kiện | Tầng / hạng | Họ tiếng | Thời điểm | Mức (phone-K) | Tối đa / video |
|---|---|---|---|---|---|
| Tít hook 0–0,3 s | — | không tiếng | tít hiện trước frame 9, giữ ≥ 1,5 s | — | 0 |
| Hook hit (từ reveal, onset ≤ 3,5 s) | A/1 | impact đơn | pre-hit → post-hit ≤ 300 ms → chỉ chữ | −3 dB | 1 |
| Stomp / quote / reveal | A/2 | impact đơn, xoay vòng | pre-hit neo đầu block → post-hit → chỉ chữ | −3 dB | ≤ 3 (MAX_A = 4) |
| CTA | B/3 | sparkle | pre-hit trước `cta.range[0]` → post-hit sau từ cuối | −8 dB | 1; ±1 s im |
| Thẻ liệt kê vào | B/4 | slide | pre-hit trước mục 1; thẻ hiện trước ≤ 600 ms | −8 dB | 1 mỗi danh sách |
| Từng mục liệt kê | — | không tiếng (chuỗi tick để v2) | — | — | 0 |
| Chuyển đoạn (5a / 5b) | B/5 | whoosh mềm | pre-hit; cú cắt camera (nếu có) đặt ở frame đỉnh | −8 dB | theo S11 |
| Vào B-roll (từ 1.2) | B/5 | whoosh mềm hoặc foley của asset | điểm vào trong khoảng ngắt | −8 dB | chung ngân sách chuyển đoạn |
| Ra B-roll | — | không tiếng | cắt cứng trong khoảng ngắt | — | 0 |
| Cắt zoom (Δscale ≥ 0,12), không trùng chuyển đoạn | C/6 | air cao tần | cú cắt snap vào khoảng ngắt ≥ 210 ms | −12 dB | ≤ 2, không liên tiếp (S11) |
| Lấp khoảng trống (S26) | C/7 | air cao tần | pre-hit ở đầu block trong đoạn > 8 s | −12 dB | tới khi hết đoạn > 8 s |
| Nhạc nền | lớp nền | bài đã chọn | 0 → t_end | giọng − 15 LU | 1 bài mỗi video |
| Kết | — | không cue mới | t_end = khoảng ngắt sau từ cuối + 500 ms | — | 0 |

### 5.5 Thư viện SFX v1 (10 file, đều có giấy phép Mixkit SFX Free License)

| Vai | File (pack = skill hiện tại, lib = `video-shotcraft/assets/audio/sfx`) | Ghi chú đo |
|---|---|---|
| Impact (hook, stomp) | `pack:impact/hit-blow`, `lib:impact/hit-weak` | attack20 76 / 46 ms, 1 onset |
| Sparkle (CTA) | `lib:light/sparkle-wand`, `pack:light/sparkle-touch` | fade mất ≤ 3 dB |
| Slide (thẻ) | `lib:paper/paper-slice-quick`, `lib:glass/glass-plate-slide` | |
| Whoosh mềm (chuyển đoạn) | `lib:transition/transition-soft`, `lib:transition/wind-swoosh-short`, `lib:transition/transition-snap` | |
| Air (cắt, lấp) | `pack:transition/sweep-short`, `lib:transition/transition-snap` | sweep-short 86,6% năng lượng trên 4 kHz |

**File bị loại, lý do tính theo vai:**
- Toàn cục (mọi vai):
  - `bass-hit-short`, `bass-hit-futuristic`, `sweep-fast-small`, `swoosh-quick`: > 50% năng lượng dưới 250 Hz (S16).
  - `riser-cine`, `sparkle.mp3`, `whoosh-big`: không truy được license (S13).
- Vai impact: `impact-zoom-quick` (attack 189 ms, thực chất là riser); `camera-shutter-hard`, `pop-electric`, `hit-fast-exciting` (> 1 onset).
- Vai slide: `paper-slide` (crest 26,8 dB).
- Vai air/whoosh: `air-woosh-quick` (tail30 796 ms, 80% năng lượng ở 250 Hz–1 kHz).

URL nguồn nằm trong `video-shotcraft/assets/audio/ATTRIBUTION.md` và `dung-video-talking-head/assets/ATTRIBUTION.md`.

### 5.6 S29 — Nhạc nền

- **Chọn nhạc (bước BGM-SELECT, một lần, trước cổng R0a mục 8):**
  - Phiên Claude hoặc opa-editor lọc 5–6 bài.
    - Ứng viên sẵn có: 5 bài Mixkit Stock Music trong `video-shotcraft/assets/audio/bgm/` (thiên về năng lượng cao).
    - Bổ sung từ Pixabay Music và YouTube Audio Library.
  - `import_bgm.py` ghi `bgm_manifest.json`: md5, source_url, license, license_checked_at, `content_id_risk` (phải `none`), integrated LUFS, điểm loop, cờ `selected`, `order`.
  - **User nghe và chọn 1–3 bài.** N = số bài `selected`.
- **Xử lý:** HPF 100 Hz; EQ khoét −3 dB quanh 2 kHz (Q 0,7, phủ 1–4 kHz); chuẩn về **giọng − 15 LU**, đo sau EQ.
- **Tĩnh:** không duck, không nhích trong khoảng ngắt (SFX nằm ở đó), không sidechain.
- **Thời gian:** fade in 1,0 s từ frame 0; fade out 1,5 s kết thúc tại t_end. Bài ngắn hơn video thì loop tại điểm loop, crossfade 500 ms.
- **Chọn bài tất định:** `bgm = selected[video_number mod N]`, theo `order`.
- **Xuất:** `final.mp4` (có nhạc), `final-nobgm.mp4` (cho nhạc trend trên app), `final-social.mp4` (có nhạc, −14 LUFS).
- **L12:** integrated của bed lệch mục tiêu ≤ 1 LU; short-term max của bed ≤ integrated của bed + 6 LU.
- **R1 A/B:** bed −12 / −15 / −18 LU; SFX −2 dB khi có nhạc. Mặc định v1 giữ nguyên mức SFX.

### 5.7 Thuật toán planner (tất định; chi tiết `research/final_sfx_planner_algorithm.txt`; prototype `prototype/planner_v11.py`)

0. **Đầu vào:** rules.json (theo lock), preset, words.json, fix.json, pauses.json (có designed_breaks), vo-clean.wav, edit.json, overrides.json, picture_lock.json, sfx_manifest.json, bgm_manifest.json.
1. **Phân tích giọng (S04):** cache theo sha của vo-clean.
2. **Sinh ứng viên:** hook (`hit_word`); stomp/quote; reveal (block `reveal: true`); CTA; thẻ liệt kê; chuyển đoạn 5a/5b; cắt zoom. Loại ngay S19 và S20.
3. **Liệt kê slot (S05, S07):** pre-hit cho mọi ứng viên; post-hit cho hook/stomp; **CTA: pre-hit, rồi post-hit sau từ cuối (S20)**; cắt zoom: khoảng ngắt có tâm ≤ 600 ms từ cú cắt.
4. **Dựng thử cue trên tín hiệu thật** cho mỗi (slot × file theo vòng xoay): đỉnh (S06), cắt/fade (S12), gain (S14), trần TP. Loại nếu fade mất > 3 dB, TP buộc hụt > 1,5 dB, hoặc chữ đi trước lời > 600 ms.
5. **Phân bổ theo hạng (S01):** kiểm S05, S09, S10, S11. Không slot qua thì A → CHỈ CHỮ, B/C → BỎ. Khoảng ngắt đã có cue thì GỘP. Ghi mọi slot đã thử kèm mã luật trượt.
6. **Sàn mật độ (S26).**
7. **Đồng bộ hình (S08, S24):** ghi `display_s` vào picture_lock.json cho sự kiện có tiếng. **Sự kiện bị gộp hoặc bỏ giữ nguyên thời điểm hiển thị của chính nó.**
8. **Trộn và xuất (S25, S29, S18):** stem, bed, mix, mix-nobgm, loudnorm; `sfx_plan.json`; sha vào STATE.md.
9. **Lint độc lập** (`lint_sfx.py` đọc lại stem, vo-clean, manifest, picture_lock rồi đo lại từ đầu).

### 5.8 Lint

| Mã | Chạy lúc | Kiểm (luật) |
|---|---|---|
| L1 | trước mux | S05: mỗi cue nằm trong đúng một khoảng ngắt đủ dài; mẫu đầu ≥ t0 + 20 ms; tắt tại t1 − 60 ms; 0 mẫu cue trên khung có tiếng |
| L2 | trước mux | S09: ≤ 1 SFX tại mọi thời điểm |
| L3 | trước mux | S10: khoảng cách |
| L4 | trước mux | S11/S26: ngân sách (PER_VIDEO theo công thức ceil), MAX_A, cắt zoom ≤ 2 và không liên tiếp; `WARN LOW_DENSITY` |
| L5 | trước mux | S14/S12: mức phone-K lệch mục tiêu ≤ 1,5 dB; TP cue ≤ −2 dBTP; fade mất ≤ 3 dB |
| L6 | trước mux | S13/S16/S03: file có trong manifest, license đã biết, md5 không trùng, <250 Hz ≤ 50%, đúng ràng buộc vai |
| L7 | trước mux | S20: CTA |
| L8 | trước mux | S22: hook |
| L9 | trước mux | S08/S24: đỉnh = k/30 của frame đồng bộ; display_s khớp |
| L10 | trước mux | S21: hash sfx_plan bằng hash output planner |
| L11 | sau mux + social | S25/S18/S27: xcorr ≤ 2 ms; cue −1/+2 f; loudness final/nobgm/social; phần kết; **đủ 3 bản xuất** |
| L12 | trước mux | S29: mức bed, S-max của bed |
| L13 | trước mux | S19: không cue nào gắn sự kiện thuộc danh sách NEVER_SOUND |
| L14 | trước mux | S23: sfx_plan đủ ứng viên, quyết định, slot đã thử, mã luật, mức 3 miền |

**Kiểm thử bắt buộc:** bảng 25 cue cũ của video 2 phải FAIL ở L1, L2, L3, L4, L7.

---

## 6. Kịch bản, ghép video và lời chuẩn

### 6.0 Ba tài liệu, ba vai

| File | Vai | Đánh số |
|---|---|---|
| `60 kịch bản HeyGen v3 — phiên bản 45–60 giây.md` | **Lời chuẩn** (VIDEO SCRIPT đã dán vào HeyGen) và chỉ dẫn motion | Số của v3 = số folder (whisper xác nhận 58/60; ngoại lệ ở §7.1; `audit/video_v3_mapping.csv`) |
| `60-kich-ban-video-ngan-ai-vm-dabest.md` | Kịch bản đạo diễn (cảnh, B-roll dự kiến) | **Lệch số với v3 từ mục 06** |
| `60-kich-ban-heygen-talking-head.md` | Phân loại HYBRID/talking, ghi chú B-roll/claim | Theo số của file đạo diễn → **lệch v3** |

### 6.1 Ghép video (`map_videos.py`, chạy trong `intake.py` ở P0)

1. **mp4 → mục v3:** whisper 25 s đầu, so token (chuẩn hoá §6.2) với cả 60 mục VIDEO SCRIPT, lấy mục giống nhất.
   - PASS khi điểm ≥ 0,60 và cách mục thứ hai ≥ 0,10 (hiệu chỉnh theo lượt quét 2026-09-11).
   - Số folder khác số mục giống nhất → `needs_input: SỐ LỆCH`.
   - Ví dụ: `34.mp4` ở gốc có nội dung giống mục 35.
2. **mục v3 → dòng đạo diễn và dòng phân loại:** so **tiêu đề + lời** (không so số).
   - Không đạt ngưỡng thì để trống; PREP tự phán đoán.
   - Ví dụ ghép tiêu đề: phân loại #18 "Thoại như brochure" ↔ v3 #16; #25 ↔ v3 #21; #31 ↔ v3 #27.
3. **Phát hiện hỏng (`needs_rerender`):**
   - mục v3 có placeholder `[IN HOA]` và whisper nghe thấy chính các từ đó;
   - hoặc lời nghe được giống khối APPLY CUSTOM MOTION hơn giống VIDEO SCRIPT;
   - hoặc độ khớp toàn bài < 0,80 (§6.2).
4. Ghi `_batches/bNN/mapping.csv` và `batch_manifest.json`. Không ai ghi vào folder video ở bước này.

### 6.2 Lời chuẩn và căn chữ

- **Tách lời:** `intake.py` (P0) tách VIDEO SCRIPT của mục đã ghép ra `_batches/bNN/vo_script/<n>.txt` + sha256. Bỏ APPLY CUSTOM MOTION. PREP đọc từ đây. **INTAKE chép vào `edit-r<ver>/vo_script.txt` và ghi STATE.**
- **Chuẩn hoá hai phía** (bảng trong `rules.json → text_norm`, có test trên 01/02):
  - NFC, chữ thường, bỏ dấu câu;
  - số tiếng Việt ↔ chữ số: một…chín, mười/mươi, lăm/nhăm, tư, mốt, trăm, nghìn/ngàn, "hai mươi" ↔ 20;
  - `%` ↔ "phần trăm"; `90%` ↔ `90 %`.
- **Căn:** whisper large-v3 trên vo-clean lấy mốc từng từ → `SequenceMatcher` căn token script với token whisper → từ khớp nhận mốc, từ không khớp nội suy.
- **Chữ hiển thị = chữ trong vo_script.** whisper chỉ cho thời gian.
- **Cổng độ khớp toàn bài** (hiệu chỉnh R1):
  - ≥ 0,90: PASS;
  - 0,80–0,90: PASS kèm CONCERN;
  - < 0,80: `needs_rerender`, hoặc `needs_input` nếu nghi lời bị sửa trên HeyGen.
- **CONCERN tự động:** có `guess:true` hoặc độ khớp < 0,90 → verify.py kết luận `DONE_WITH_CONCERNS`, nên user chắc chắn xem.
- **Không có vo_script** (ngoài 60 mục): ASR như cũ, `guess:true`. **Cấm tự viết script thử whisper.** ASR không bao giờ làm dừng dây chuyền.
- PLAN chỉ được đổi cách hiển thị số trong hero/stomp (năm → 5) qua `display` của block.

### 6.3 Nhịp ngắt có chủ đích

- `...` và chỗ xuống dòng giữa hai đoạn trong vo_script được map sang index từ, ghi vào `pauses.json → designed_breaks[]` (`ellipsis` | `paragraph`).
- `paragraph` là ứng viên 5a (S02); `ellipsis` chỉ để báo cáo.
- Bằng chứng: cả 5 ranh giới đoạn của video 02 đều trùng một cue planner đã chọn độc lập từ năng lượng (3 chuyển đoạn 'Từ', 'nhưng', 'AI'; stomp b07 ngay trước 'Tôi'; CTA 'Lưu').

### 6.4 INTAKE (một lệnh `stage.py INTAKE`)

- **Việc làm:** scaffold từ release → master.mp4 → vo-clean.wav (S28) → chép vo_script → whisper + căn chữ → words.json, fix.json → pauses.json (S04 + designed_breaks) → VO_REF → meta.json → ASR_REPORT.md → STATE.md.
- **Gate:** lint_rules PASS; QA vo-clean; xcorr(vo-clean, nguồn) ≤ 2 ms; mốc từ đơn điệu tăng; cổng độ khớp.

---

## 7. Bước 0 — PREP: phiếu chuẩn bị (phát hành 1.1.0, theo D4/D6/D13)

### 7.1 Việc và đầu ra

- **1 card PREP xử lý ≤ 5 video.**
- **Đầu vào:** mapping.csv, vo_script, dòng đạo diễn và dòng phân loại đã ghép, danh sách `needs_rerender` / `needs_input` của `intake.py`.
- **Đầu ra:** `_batches/bNN/prep/prep-<k>.json` và phần tương ứng trong `_batches/bNN/PREP-SHEET.md`. Mỗi video ghi:
  - `status`: `ok` | `needs_rerender` (kèm lý do: placeholder / motion / lời lệch) | `needs_input`;
  - `broll_class`: `none` | `light` | `heavy`;
  - danh sách asset: mô tả, câu/từ neo, loại (`ai_image`, `ai_video`, `screen_rec`, `real_output`, `stock_context`, `remotion_card`), ai làm, hạn;
  - `claim_gate` + lý do (cần test thật, cần consent, case thật, tin chưa có nguồn/ngày, số liệu không nguồn).
- **Gate:** `check_prep.py` (schema; mọi video có status và broll_class; asset `heavy` có mô tả và từ neo).

**Kết quả quét toàn bộ ngày 2026-09-11** (whisper 25 s đầu × 60 file, so với 60 mục v3; `audit/video_v3_mapping.csv`):

- **58/60 file khớp đúng mục cùng số**, điểm 0,87–0,95, mục kế tiếp chỉ ≤ 0,34.
- 2 ngoại lệ: `34.mp4` (giống mục 35) và 38 (không khớp mục nào).
- Trong 58 file khớp số, 4 file (31, 32, 33, 37) thuộc mục còn placeholder.
- **54 video không có vấn đề.**
- `55.mp4` nằm ở thư mục gốc, không có folder `55/`, nhưng nội dung khớp mục 55. `intake.py` tạo folder `55/` và ghi đường dẫn nguồn vào manifest, **không di chuyển file của user**.

| Video | Tình trạng |
|---|---|
| 31 | `needs_rerender`: HeyGen đọc nguyên placeholder ("tính năng **tin mới**… **mô tả nền G**… **ngang hàng**… **USC Case**") |
| 33 | `needs_rerender`: đọc [BƯỚC CŨ], [TIN MỚI], [BƯỚC MỚI] ("tôi phải **bước khe**… thành **bước mới**") |
| 37 | `needs_rerender`: đọc [CÔNG CỤ], [CLAIM] ("**Claim công kỳ** làm được **CLIM**") |
| 38 | `needs_rerender`: lời không khớp mục nào (0,14). HeyGen đọc bản dịch khối APPLY CUSTOM MOTION ("Bắt đầu với một giảm bài nghe nhanh… khi nói về 10 phút") |
| 32 | ⚠️ `[CÔNG CỤ]` đọc thành "công cụ", câu vẫn nghĩa ("Đừng tải công cụ chỉ vì thấy một video viral"). PREP ghi CONCERN, user quyết |
| `34.mp4` (gốc) | `needs_input`: file **khác** `35/35.mp4` (160 MB so với 147 MB) nhưng đọc **cùng kịch bản mục 35**, dài bằng nhau (42,22 s) |
| Mục 34 v3 ("Tin AI trong 30 giây") | **chưa có video**. Kịch bản còn placeholder, cần điền rồi mới render |

### 7.2 Điểm dừng chờ user duyệt

- `make_cards.py` tạo card **APPROVE-PREP-<k>**: assignee `user`, `--initial-status blocked`, `--parent` = card PREP.
- User đọc PREP-SHEET và trả lời. Operator chép **nguyên văn** lời duyệt vào comment và `APPROVALS.md`, rồi complete card.
- Card INTAKE của các video trong phiếu có `--parent` = APPROVE-PREP-<k>. Video `needs_rerender` / `needs_input` không có card INTAKE cho tới khi user xử lý.
- **Nguồn quyết định B-roll duy nhất** là `broll_class` trong phiếu đã duyệt. Cột HYBRID của file phân loại chỉ là gợi ý cho PREP.

---

## 8. B-roll (phát hành 1.2.0; riêng B13, B14 từ 1.1.0)

### 8.1 Luồng theo loại

- `none`: A-roll là bản cuối.
- `light`: A-roll → B1 → B2 (agent) → B3.
- `heavy`: A-roll xuất trước (không đăng như bản cuối); B-roll ghép khi user giao asset. **Slot `heavy`/proof quá hạn thì block `needs_input` và hỏi user, không tự bỏ.**

### 8.2 Luật B-roll

| Mã | Luật | Giá trị | Cưỡng chế | Căn cứ |
|---|---|---|---|---|
| B01 | B-roll là lớp bằng chứng, minh hoạ đúng điều đang nói | Mỗi slot có `vo_quote`, `claim`, `kind` ∈ {proof, example, list_item, ui, context, cover_glitch, hook_proof}. Ngữ nghĩa: verifier ghi CONCERN; user duyệt theo D5 (canary gồm cả kế hoạch B-roll). | lint | [NC] Mayer (coherence) |
| B02 | Đúng 1 từ kích hoạt; hình vào ở đầu cụm danh từ | Deictic (này/đây), đầu ra/ví dụ cụ thể, sản phẩm/UI, trước–sau, mục liệt kê là đồ vật. trigger − a ≤ 3 từ. P1 deictic/proof > P2 số liệu/UI > P3 che lỗi avatar. | lint | [NC] B-Script CHI'19 |
| B03 | Vùng cấm | [0; 3,5 s) trừ hook_proof; từ `cta.range[0]` − 0,3 s; 3 s cuối; hero stomp/quote; lúc steps hiện; câu ngôi thứ nhất tạo uy tín; danh từ trừu tượng. | lint | [NC] Kizilcec 2014 |
| B04 | Độ phủ | `light`/`heavy` hybrid: 25–40% (trần 50%). Talking: ≤ 20%. Số slot ≤ floor(giây/6). Giữa 2 slot ≥ 1,5 s thấy mặt. | lint | [NC] B-Script 13,2%; [GĐ→R1] |
| B05 | Thời lượng | Still 1,2–3,5 s; clip 1,5–5 s; montage 0,6–1,6 s/shot, tổng ≤ 6 s; hook_proof 0,6–1,2 s; hình có nhãn ≥ 1,5 s. | lint | [NC] Potter 2014 |
| B06 | Điểm cắt suy từ index từ + năng lượng giọng; không cắt giữa từ | **Vào:** frame đỉnh cue vào (pre-hit); không tiếng thì t0 + 45% khoảng ngắt. **Ra:** cắt cứng ở t0 + 45% khoảng ngắt đầu tiên sau từ cuối. Không có khoảng ngắt trong ±300 ms thì dùng ranh giới từ. | code | [ngành] |
| B07 | Mặc định kiểu J | L-hold ≤ 0,6 s (≤ 3 từ); không phủ từ đầu ý mới/CTA. | lint | [ngành] |
| B08 | Chế độ khung | full mặc định; asset không phải 9:16 → card 880×800 trên nền mờ 40 px; pip/split v2; cấm lower-third. | lint | nền tảng |
| B09 | Chuyển động ảnh tĩnh | push 1,00→1,06 (≤ 5%/s); ảnh có chữ Δ ≤ 0,02; UI punch 1,25–1,40 một lần; Sequence premountFor 30; QA frame-diff > 0,5/255. | code | kỹ thuật |
| B10 | Chuyển cảnh | Vào: cắt cứng + settle 4 f cho ≥ 2/3 số slot, whoosh_blur 6 f cho ≤ 1/3; cấm crossfade. Ra: luôn cắt cứng trong khoảng ngắt. | lint | kỹ thuật |
| B11 | B-roll không tăng tổng số cue | Vào = ứng viên hạng 5 khi điểm vào nằm trong khoảng ngắt; ra 0 cue; cue hero/cắt trong slot bị nuốt; montage shot 2..n im; planner chạy lại, tie-break "dính". | code | thiết kế |
| B12 | Cắt camera quanh B-roll do build suy ra | `picture_effective = f(edit.picture, broll)`; không shot trong (t0; t1); reframe dời về t1; hai cú cắt cách ≥ 0,5 s. | code | kỹ thuật |
| **B13** (1.1.0) | Ngân sách lớp hình | Mỗi frame: 1 nền + phụ đề + ≤ 1 overlay (hook \| steps \| CTA \| nhãn B-roll). **Disclosure AI là lớp riêng**, cố định góc trên trái, không tính vào ngân sách. Thứ tự: Footage → Broll → Grade → StepList → Subtitle → Hook → Cta → Disclosure. Broll không có zIndex. Nhãn ≤ 22 ký tự, ≤ 15 ký tự/s. | lint | thiết kế |
| **B14** (1.1.0) | Safe zone chung | Chữ trong x 140–940, y 270–1436. Phụ đề: đáy cách mép 484 px, maxWidth 800, căn giữa 540 (A/B với 400 px ở R1). Chủ thể asset trong y 270–1080. `check_text_safe`: alpha > 0 ngoài hộp là FAIL. | lint | nền tảng (TikTok) |
| B15 | Nhất quán sản phẩm và màu | 1 product_ref mỗi video; WB 5000–5500 K; grade chung; cấm lọc màu để giả biến thể. | lint | uy tín |
| B16 | Nguồn và bản quyền | Ưu tiên: kết quả thật / quay màn hình (user) > ảnh/clip AI (Grok qua 9router) > thẻ Remotion. Stock có license: **chỉ bối cảnh, không làm proof (D3a, chờ xác nhận)**. Cấm logo, người không có release, watermark. Mỗi file một dòng ATTRIBUTION. | lint | pháp lý |
| B17 | Công bố nội dung AI | `assets.json → ai_disclosure` (chủ: B2) = true khi có asset AI → overlay disclosure (lớp riêng B13); checklist đăng bài có mục bật nhãn AI (TikTok, YouTube). | lint | nền tảng |
| B18 | Trạng thái asset; không ship đồ giữ chỗ | status ∈ {needed, delivered, approved, rejected, skipped}.<br>• Asset agent làm: user duyệt contact sheet của canary, verifier kiểm kỹ thuật B19.<br>• Asset user làm: verifier kiểm kỹ thuật.<br>Chỉ render `approved`. Tự bỏ slot (`BROLL_SKIPPED`) **chỉ cho slot `light`/`context` quá hạn**. Độ lệch chuẩn độ sáng < 30/255 thì FAIL. | lint | kỹ thuật |
| B19 | Chuẩn giao file | Still JPG q ≥ 90, ≥ 1620×2880; video H.264 30 fps CRF ≤ 18, không audio; tên `^br\d{2}[a-z]?_[a-z0-9-]+_v\d+\.(jpg\|png\|mp4\|webm)$`. | lint | kỹ thuật |
| B20 | B-roll bắt buộc theo phiếu | `broll_class ≠ none` trong prep đã duyệt thì bắt buộc có slot. Waiver chỉ hợp lệ khi có id feedback của user; waiver do máy tự ghi (B18) không thoả B20. | lint | D4/D6 |
| B21 | Che lỗi avatar | scale ≤ 1,22 (1,25 tối đa 2 shot); `cover_glitch` chỉ khi có hình đúng nghĩa. | code | [chưa kiểm] |

### 8.3 Tạo asset AI (B2, agent)

- Gọi 9router qua endpoint OpenAI-compatible. Key đọc từ `NINEROUTER_API_KEY` (có sẵn trong `.env` của opa-editor, opa-operator, opa-design); base_url đọc từ `providers.ninerouter.base_url` trong config Hermes. **Không ghi key vào code, card hay report.**
- **Cổng R0b (bắt buộc trước khi bật B2-AI):** ngày 2026-09-11, `GET /v1/models` chỉ trả về 26 model chữ (grok-3/4/4.5/4.6, gemini, claude…). **Không model nào có `imageOutput`**, không có model video.
  - User cần bật hoặc xác nhận model ảnh/video Grok trên 9router.
  - Cổng đạt khi tạo được 1 ảnh và 1 clip thử, rồi ghi model id vào `rules.json → broll.ai.models`.
  - Chưa đạt thì `light` chỉ dùng stock bối cảnh + thẻ Remotion.
- Endpoint là HTTP thường tới một IP, nên key đi không mã hoá. Khuyến nghị HTTPS hoặc đổi key định kỳ.

---

## 9. Dây chuyền

| Stage | Chủ | Vào | Ra | Gate | Ngân sách (lượt / runtime / retries / goal) |
|---|---|---|---|---|---|
| **M0** Dọn (một lần) | User + phiên Claude | staging cũ, SOUL, config | §13.1 | `check_drift.py` kiểm từng mục D9 + **user xác nhận** | — |
| **BGM-SELECT** (một lần) | Phiên Claude hoặc opa-editor; user nghe | thư viện free | bgm_manifest có 1–3 bài `selected` | license + content_id_risk `none`; user chọn | — |
| **R0a** Phát hành 1.1.0 | Phiên Claude / opa-dev-be | spec, prototype, fixture | repo git + `releases/1.1.0` + tag | §13.2 | 4–6 card dev |
| **R1** Hiệu chỉnh | opa-editor + opa-verifier; user nghe | tag 1.1.0; 5 video chưa dựng | `out/r1-<variant>/` (**không xuất bản**), phiếu nghe, video mốc, **tag 1.1.1** | §13.3 | như INTAKE/PLAN/BUILD/VERIFY |
| **P0** Lập lô | opa-operator (chỉ chạy script) | thư mục Vid Heygen, 3 file kịch bản | `_batches/bNN/` (manifest, mapping, vo_script), board `vm-heygen-bNN`, card | `make_cards.py --check` PASS | — |
| **PREP** | opa-editor (phán đoán) | §7.1 | prep-<k>.json, PREP-SHEET.md | `check_prep.py` | ≤ 25 / 20 phút / 2 / không (R43: stage.py gác complete) |
| **APPROVE-PREP** | **user** (card blocked) | PREP-SHEET | lời duyệt nguyên văn trong APPROVALS.md | user trả lời | — |
| **INTAKE** | opa-editor | mp4, `_batches/.../vo_script/<n>.txt`, release | §6.4 | §6.4 | ≤ 15 / 25 phút / 1 / không |
| **PLAN** | opa-editor; a2 dùng model mạnh hơn (`ag/claude-sonnet-4-6`, cờ model override của `hermes kanban create`, kiểm tên cờ ở R0a) | words, pauses, meta, `propose_edit.json` (code sinh), kịch bản, `stages/PLAN.md` | `edit.json` (§9.1) | `validate_edit` (§9.1) | ≤ 25 / 20 phút / 2 / không (R43); tối đa 3 vòng sửa |
| **BUILD** | opa-editor | edit, fix, meta, overrides, manifest | picture_lock, script.ts, sheet.png, sfx_plan/lint, stem/bed/mix, final/nobgm/social, QA, report | dừng ở FAIL đầu: text-safe → L1–L10, L12–L14 → loudness mix → mux + L11 | ≤ 15 / 25 phút / 1 / không |
| **VERIFY** | opa-verifier | mọi artifact + STATE + rules.lock | VERDICT.json/.md, kpi.json | `verify.py` V1–V7 | ≤ 20 / 15 phút / 1 / không |
| **APPROVE-CANARY** | **user** (card blocked) | VERDICT + video canary | lời duyệt nguyên văn | user trả lời | — |
| **R0b** Phát hành 1.2.0 | Phiên Claude / opa-dev-be | B01–B21, cổng 9router | check_broll, Broll.tsx mới, schema broll/assets, planner nhận B-roll | bắt lỗi B-roll của video 1; golden A-roll không đổi âm ngoài ±2 s quanh slot | — |
| **B1** | opa-editor | A-roll VERIFIED, prep đã duyệt | broll.json, broll-plan.md | `check_broll` PASS | ≤ 20 / 20 phút / 2 / `--goal-max-turns 2` |
| **B2** | agent (AI/stock/thẻ) hoặc **user** (quay màn hình; card blocked) | asset_spec cùng họ của nhiều video | `public/broll/br*_v*`, ATTRIBUTION, assets.json | `check_broll --assets`; duyệt theo B18 | 1 card = 1 họ asset |
| **B3** | opa-editor (BUILD') → opa-verifier (VERIFY') | artifact A-roll + asset approved | `out/broll-r<ver>-<preset>/` | như BUILD/VERIFY + diff sfx_plan A↔B, tổng cue không tăng, phụ đề hiện trên mọi slot | như BUILD / VERIFY |
| **F1** | operator ghi nguyên văn; phiên dev phân loại, đo, sửa; user duyệt A/B | FEEDBACK.jsonl + verify | diff rules.json + CHANGELOG + release mới | user duyệt A/B trên điện thoại; property test PASS | áp từ đợt sau |

**Ngân sách lượt là mức tham khảo (FS-6):** Hermes chỉ ép runtime và retries; không có cờ lượt theo card, trần thật là `agent.max_turns` (60) của profile mỗi lần chạy. Cột "lượt" được đo sau lượt chạy — số `API call #N` lớn nhất của từng lần chạy trong `profiles/<p>/logs/agent.log`, tính cả lần chạy lại — rồi so với bảng và với 60 (OPERATOR.md §2).

**Canary (D5):**
- `make_cards.py` chỉ mở chuỗi card của **video canary** (video đầu đợt đã qua APPROVE-PREP). Card INTAKE của các video còn lại có `--parent` = **APPROVE-CANARY**.
- Mẫu 1/5 do `make_cards.py` chọn tất định (seed = slug board) và in vào `APPROVALS.md` từ đầu.

### 9.1 edit.json (đầu ra PLAN) và validate_edit

**Schema (chỉ nhãn, không có giây):**
- `blocks[]`: `top`/`hero`/`bottom` (range index từ), `style` ∈ {script, stomp, quote}, `color`, `accent`, `display`, `reveal` (bool; chỉ cho block script).
- `hook`: `text`, `color`, `hit_word`.
- `steps`: `title`, `items[]{range, label}`.
- `shots[]`: `cut_at_word`, `s0`, `s1`, `x?`, `y?`.
- `cta`: `range`, `label`, `keyword`.

**validate_edit kiểm:**
- schema; block 1,5–3 s; hero 2–5 từ; không bỏ từ (trừ đoạn nhường steps/hook);
- stomp cách ≥ 8 s; tổng stomp + quote + reveal ≤ 3;
- `hit_word` nằm trong hero stomp và có onset ≤ 3,5 s;
- có `cta.range`; không block stomp nào chứa keyword CTA;
- scale ≤ 1,22 (1,25 tối đa 2 shot); **khoảng cách shot 2–4 s**; cú cắt snap được vào khoảng ngắt.
- **Chế độ legacy:** đổi edit.json 1.0.0 (giây) sang index từ để test cổng R0a.

---

## 10. Giao thức giao việc

### 10.1 Phân vai

| Vai | Được làm | Không được làm |
|---|---|---|
| opa-operator | Chạy `intake.py`, `make_cards.py`; theo dõi; archive card hỏng và tạo lần thử mới; ghi feedback và lời duyệt **nguyên văn**; complete card APPROVE-* **chỉ sau khi user trả lời** | Viết edit.json; build/render; dán số vào card/comment/summary; ghi vào `<n>/edit*`; unblock một card lần hai; `python -c` |
| opa-editor | Mỗi card đúng 1 stage bằng `stage.py <STAGE>`; phán đoán ở PREP, PLAN, B1 | Sửa rules/build/component/gate; tạo script mới; `python -c`; tự viết chuỗi ffmpeg |
| opa-verifier | Chạy `stage.py VERIFY` (script được append STATE.md và ghi `out/verify/`) | Ghi bất cứ chỗ nào khác |
| opa-design / user | Làm asset B2 | Sửa edit.json, broll.json |
| Phiên Claude Code / opa-dev-be | R0, F1, bump version, chạy golden | Đổi luật cho video đang chạy |

### 10.2 Card là con trỏ (do `make_cards.py` sinh)

```
TITLE: [vmh-07] BUILD
VIDEO: 7   STAGE: BUILD   RULES: dung-video-talking-head@1.1.1
PRESET: standard   ATTEMPT: a1
```

- Cờ Hermes: `--parent <card trước> --workspace dir:D:/MMO/Van Minh AI/Vid Heygen/<n> --idempotency-key vmh-<n>-<stage>-a<k> --skill dung-video-talking-head` + ngân sách theo bảng §9.
- Lệnh đầu tiên luôn là `python <skill>/releases/<ver>/scripts/stage.py <STAGE>`. Script đọc body qua `hermes kanban show $HERMES_KANBAN_TASK --json`; body lệch mẫu thì block với lý do "card ngoài mẫu".
- Script in sẵn NEXT/FAIL, SUMMARY (không số) và METADATA; model chép nguyên văn.
- Card cơ học không dùng swarm, `--triage` hay goal loop.

### 10.3 Override được phép

- Preset lấy từ batch_manifest (mặc định kênh). Đổi cho một video chỉ qua F1, kèm id feedback.
- `overrides.json` (chỉ F1 ghi; ≤ 3 dòng mỗi video): `{target: "<candidate_id>", action: "none" | "promote_A", reason: "<trích lời user>", fb_id: "<id>"}`. Lint vẫn áp S05–S12.
- Waiver B-roll: xem B18/B20. **Mọi thứ khác là FAIL.**

### 10.4 Mỗi file một chủ; STATE.md là chuỗi provenance

| File | Ai ghi | Sửa sau đó |
|---|---|---|
| `_batches/bNN/*` (manifest, mapping, vo_script, APPROVALS, kpi.jsonl) | `intake.py` / `make_cards.py` (operator) | chỉ script đó |
| `_batches/bNN/prep/*` | PREP | PREP chạy lại |
| meta.json, vo_script.txt (bản chép) | INTAKE | không ai |
| words.json, pauses.json, fix.json | INTAKE | INTAKE chạy lại; đổi số từ sau PLAN thì phải chạy lại PLAN |
| propose_edit.json | code trong `stage.py PLAN` | sinh lại |
| edit.json | PLAN (agent) | chỉ PLAN chạy lại |
| broll.json / assets.json (có ai_disclosure) | B1 / B2 | chủ của file |
| overrides.json | F1 | F1 |
| picture_lock, script.ts, stem, bed, mix, sfx_plan, QA, report | BUILD | sinh lại, không sửa tay |
| out/verify/* (gồm kpi.json) | VERIFY | — |

- STATE.md chỉ do `stage.py` append, mỗi dòng: stage, giờ, task id, run id, profile, sha release, sha từng file.
- verify.py REJECT artifact không có dòng hợp lệ hoặc sha không khớp.
- Operator gom `out/verify/kpi.json` vào `_batches/bNN/kpi.jsonl`.

### 10.5 Ma trận lỗi

**Luật Hermes:** card đã block thì **không unblock lần hai**. Cách đúng: archive, tạo card mới `-a<k+1>`. (Riêng card APPROVE-* được complete một lần sau khi user trả lời.)

| Stage | Lỗi | stage.py làm gì | Ai xử lý |
|---|---|---|---|
| P0 | Số lệch / nghi hỏng | ghi `needs_input` / `needs_rerender` vào manifest; không tạo INTAKE | user (qua PREP-SHEET) |
| INTAKE | ASR nghi sai | `guess:true`, đi tiếp; verify → DONE_WITH_CONCERNS | user |
| INTAKE | Độ khớp < 0,80 | block `needs_input` | user |
| INTAKE | QA vo-clean / xcorr FAIL | block `capability` | dev (F1) |
| INTAKE, BUILD | Treo / timeout | resume theo STATE; lần 2 thì block `transient` | operator tạo a2 |
| PLAN | validate FAIL sau 3 vòng | block `needs_input` | operator tạo a2 với model mạnh hơn |
| BUILD | text-safe FAIL | block; owner PLAN hoặc template | operator / dev |
| BUILD | lint_sfx FAIL | block `capability` (lỗi skill) | dev; video chờ |
| BUILD | loudness FAIL | tự thử lại 1 lần | lần 2 thì dev |
| BUILD | xcorr / sync FAIL | block `capability` | dev |
| VERIFY | REJECTED | in `owner_stage` | operator mở card mới cho owner_stage |

**Mã → owner_stage (theo mã lint/gate):**

| Mã | owner_stage |
|---|---|
| S04, S28, S25 (xcorr nguồn), cổng độ khớp | INTAKE / dev |
| L1–L14, S25 (L11), S01–S03, S05–S27, S29 | BUILD (lỗi skill) → dev |
| validate_edit, B21 | PLAN |
| B13, B14, text-safe | PLAN hoặc template |
| B01–B12 | B1 |
| B15–B19 | B2 |
| B20 | PREP (phân loại) hoặc B1 |

### 10.6 Khoá và song song

- Khoá `Vid Heygen/<n>/.stage.lock` theo video (dùng chung mọi version), cộng một khoá toàn máy cho whisper và render.
- `kanban.max_in_progress_per_profile: 1` trong `opa-operator/config.yaml` (dispatcher chạy trong gateway của operator).

---

## 11. Kiểm tra chất lượng

### 11.1 `verify.py` (tất định)

| Mã | Kiểm |
|---|---|
| V1 | rules.lock khớp card; MANIFEST khớp; không có bản skill che trong `profiles/*/skills` |
| V2 | Chạy lại validate_edit, lint_sfx (L1–L14), check_text_safe từ `releases/<ver>` |
| V3 | xcorr(final, mix) ≤ 2 ms; cue −1/+2 f; mức lệch ≤ 1,5 dB so với sfx_plan |
| V4 | Loudness S18 trên final, final-nobgm, social (48 kHz) |
| V5 | Chuỗi provenance STATE.md |
| V6 | Report đủ mục (sfx_plan, lint, loudness, "đoán", độ khớp vo_script, waiver); PATCHES rỗng |
| V7 | Model xem contact sheet; chỉ được ghi CONCERN |

- Kết luận: `VERIFIED` / `DONE_WITH_CONCERNS` / `REJECTED(owner_stage)`.
- `DONE_WITH_CONCERNS` bắt buộc khi có: WARN LOW_DENSITY, `guess:true`, độ khớp < 0,90, CONCERN của V7.

### 11.2 Người duyệt (D5)

- Duyệt canary (gồm B-roll của canary nếu có) → APPROVE-CANARY. Sau đó 1/5 mẫu tất định, cộng mọi `DONE_WITH_CONCERNS` và claim_gate.
- **Cách nghe:** loa điện thoại ~50% âm lượng rồi tai nghe; chỗ yên rồi chỗ ồn; nghe 1 lượt không nhìn timeline rồi mới ghi `mm:ss`.

### 11.3 KPI mỗi đợt

Tỉ lệ pass lần đầu theo stage; số lượt dùng; FAIL theo mã luật; lời chê theo mã luật; phút máy mỗi video; số video `needs_rerender`.

---

## 12. Feedback thành luật (F1)

**Mẫu 1 dòng:**
`FB | video 07 @1.1.1 standard | 00:24.9 | tag: bé | mức 2 | "cú đập chỗ khóa 3 thứ nhỏ quá"`

Tag ∈ {to, bé, dày, thưa, trễ, sớm, lạc chất, giọng, nhạc, hình, chữ}.

| Triệu chứng | Đo trước | Núm chỉnh (mỗi lần) | Giới hạn |
|---|---|---|---|
| bé | L5; cue có trong khoảng ngắt không | S14 tầng +1 dB, hoặc preset punchy | A không vượt −1 dB |
| to | L5, S18 M-max | S14 −1 dB | — |
| dày | L4 | S11 / preset calm | — |
| thưa | S26 WARN | MAX_GAP −1 s / preset punchy | MAX_GAP ≥ 6 s |
| trễ / sớm | L11, SYNC | S24 ±1 f | — |
| lạc chất | S03 | thay file qua import_sfx | ≥ 2 file mỗi vai |
| nhạc to/nhỏ | L12 | S29 ±1 LU | bed ≤ giọng − 10 LU |
| giọng | S28 QA | vo-clear-2 / A/B tốc độ 1,05× đều hình + tiếng | ngoài SFX |

**Phân loại** (phiên dev, dựa trên output verify):
- (a) lỗi thực thi/lint;
- (b) tham số trong dải;
- (c) tình huống mới;
- (d) khẩu vị riêng một video → overrides.json.

Luật mới áp từ đợt sau; video đã xong giữ nguyên. ID luật không đánh số lại.

---

## 13. Triển khai

### 13.1 M0 — Dọn (user bấm config; phiên Claude liệt kê và `check_drift.py` kiểm)

1. Chuyển `C:\Users\Minh PC\AppData\Local\hermes\profiles\opa-operator\staging\vm-heygen-1-20260910\` (PACKET-*.md chứa 0.82 và DUCK_DB 1.0, cùng `create_kanban_*.py`) vào `_superseded/`, kèm ghi chú `DEPRECATED — dùng dung-video-talking-head@1.1.x`.
2. SOUL.md của opa-operator, opa-editor, opa-verifier: thêm mục trỏ tới giao thức §10, thay mẫu packet tự do.
3. Cấu hình (D9). Phiên Claude đọc config thật để ghi đúng tên key trước khi user sửa:
   - `opa-operator/config.yaml` → `kanban.max_in_progress_per_profile: 1`; **giữ `kanban.auto_decompose: true`**;
   - `opa-editor/config.yaml`, `opa-verifier/config.yaml` → `auxiliary.background_review.enabled: false`;
   - `opa-operator/config.yaml` → bỏ quyền `execute_code` và mục cho phép `-c`/`-e` trong allowlist lệnh;
   - xoá `profiles/opa-operator/skills/claude-import/remotion-best-practices/rules/sfx.md`.
4. Archive `t_81a309b2` và board `vm-heygen-1`.
5. `check_drift.py` (chỉ đọc) kiểm từng mục 1–4. **User xác nhận.**

### 13.2 R0a — Cổng phát hành 1.1.0 (kiểm tính chất, không so bảng cue)

1. Planner PASS lint của chính nó trên fixture video 2.
2. Lint FAIL bảng 25 cue cũ (L1, L2, L3, L4, L7).
3. Chạy 2 lần ra cùng sha.
4. `validate_edit` (chế độ legacy) bắt đủ vi phạm của edit.json video 2 cũ thuộc các luật còn trong schema mới: stomp < 8 s, block ngoài 1,5–3 s, hero > 5 từ, khoảng cách shot ngoài 2–4 s.
5. Unit test SYNC_FRAME khớp code template.
6. Gate xcorr đạt trên một render thử.
7. Căn vo_script trên 01/02 đạt ≥ 0,90; test bảng chuẩn hoá số.
8. `map_videos.py` ghép đúng cả 60 mục (so với `audit/video_v3_mapping.csv` đã kiểm tay) và bắt được 31, 33, 37, 38 là `needs_rerender`.
9. Mix có nhạc (bài từ BGM-SELECT) qua L12.
10. `check_prep.py` PASS trên một phiếu PREP chạy thử của đợt 1.
11. opa-editor chạy **bản sao** video 2 (thư mục kiểm thử, không xuất bản) qua INTAKE → PLAN → BUILD, rồi opa-verifier chạy VERIFY. Mọi card nằm trong ngân sách §9 và không chạm trần 60 lượt.

Đạt thì tag `v1.1.0`.

### 13.3 R1 — Nghe hiệu chỉnh

- Chọn **5 video chưa dựng, `status: ok`**: 2 talking-head thuần, 1 nhiều liệt kê, 1 nói nhanh nhất (từ/giây), 1 hybrid điển hình.
- **A/B** (chế độ variant, xuất vào `out/r1-<variant>/`, lint dùng giá trị của variant, đánh dấu không xuất bản):
  - preset calm / standard / punchy trên 1 video;
  - nhạc nền −12 / −15 / −18 LU;
  - SFX −2 dB khi có nhạc;
  - phụ đề đáy 484 so với 400 px;
  - cài đặt xuất / giọng full-band của HeyGen trên 1 video.
- **Đầu ra:** preset kênh, mức nhạc, SYNC ±1 f, **video mốc** (reference cut + cue sheet có chú thích + contact sheet + 2–3 short tham chiếu bên ngoài), **tag 1.1.1**.
- **Bản R1 chỉ để hiệu chỉnh.** 5 video này dựng lại trong lô theo @1.1.1 và đi qua PREP như mọi video khác.

### 13.4 Thứ tự lô

1. **Trước đợt có các video này:**
   - user điền placeholder trong v3 rồi render lại trên HeyGen các video `needs_rerender` (31, 33, 37, 38; quyết định cho 32);
   - xử lý `34.mp4` (bản trùng kịch bản 35);
   - render mục 34 nếu muốn có đủ 60 video.

   54 video không có vấn đề đi bình thường.
2. **Đợt 1:** video talking-head thuần, xác định sau khi ghép nội dung (§6.1). Ứng viên theo ghép tiêu đề: folder 16 (lời thoại như brochure), 21 (đổi model), 27 (khi nào không dùng AI), 51, 53, 59, 60. PREP xác nhận.
3. **Các đợt hybrid:** A-roll theo lô tối đa 10 video; PREP báo trước asset cần chuẩn bị.
4. **Sau R0b:** B-roll gom theo họ asset.
5. **claim_gate:** vẫn dựng, không đăng trước khi user xác nhận. PREP gắn theo nội dung đã ghép:
   - cần test thật (ví dụ "miễn phí và trả phí");
   - cần consent hoặc bài học viên (nhóm cộng đồng);
   - case phải có thật;
   - tin AI thiếu nguồn hoặc ngày;
   - số liệu không nguồn.
6. **Ngoài phạm vi:**
   - video 1–2: không dựng lại (D11). Bản đã giao của video 01 có claim "90%" không nguồn; nên xác nhận trước khi đăng.
   - video không ghép được, B1–B19, A_Minh_*, Video_avatar*: `needs_input`.

**Thông lượng:** khoảng 4 card mỗi video + 1 PREP mỗi 5 video + card duyệt. 20–30 phút máy mỗi video. Xoá `node_modules` của project sau khi VERIFIED.

---

## 14. Bảo mật và bản quyền

- Không có secret trong repo, rules, card, report hay memory. API lấy key từ biến môi trường của profile Hermes.
- Key 9router đã bị dán vào một phiên chat: khuyến nghị đổi key. Endpoint HTTP không mã hoá: khuyến nghị HTTPS.
- Mọi SFX, nhạc nền và B-roll có ATTRIBUTION (nguồn, license, ngày kiểm). File license unknown bị loại tự động (S13, S29, B16).
- Không commit spec hay tài liệu vận hành vào `video-shotcraft` (repo công khai của bên thứ ba).

---

## 15. Ngoài phạm vi v1 (v2)

- Cue đè lời có kiểm soát (speech-safe); chuỗi tick cho mục liệt kê; macro riser → impact.
- Jitter/pitch; cold-open hook.
- Nhạc nền nhích trong khoảng ngắt không có cue; sidechain.
- Card "sound designer" LLM; tối ưu theo retention (cần ≥ 10 video đã đăng); preset theo nền tảng.
- pip/split-screen B-roll; `node_modules` dùng chung qua junction.

---

## 16. Rủi ro và việc còn mở

| Rủi ro / việc mở | Xử lý |
|---|---|
| Mức SFX và nhạc mới là điểm xuất phát, chưa ai nghe | R1 bắt buộc trước khi mở lô |
| Một số mp4 hỏng lời (placeholder/motion) | `needs_rerender` ở P0; user render lại trên HeyGen trước đợt |
| Ghép video ↔ kịch bản sai số | `map_videos.py` theo nội dung + cổng R0a mục 8 |
| Model ảnh/video Grok chưa có trên 9router | Cổng R0b; `light` tạm dùng stock bối cảnh + thẻ Remotion |
| Video ít khoảng ngắt → quá thưa tiếng | S26 WARN → DONE_WITH_CONCERNS; R1 có 1 video nói nhanh |
| Giọng HeyGen cắt băng ~3,75 kHz ("ồm") | S28 + thử cài đặt xuất ở R1 |
| Flash model bịa schema ở PLAN | propose_edit sinh khung; validate chặn; a2 dùng model mạnh hơn |
| Nhạc free dính Content ID | `content_id_risk: none` bắt buộc; user nghe duyệt |
| Chờ user xác nhận | D3a (stock chỉ bối cảnh), D13 (render lại video hỏng) |

---

## Phụ lục A — Nguồn chính

- **Chuẩn:**
  - ITU-R BT.1359 (lệch tiếng–hình)
  - ITU-R BS.1770 (LUFS, K-weighting)
  - EBU R128 s1 (nội dung ngắn)
  - AES TD1008 (streaming)
  - ATSC A/85, Netflix mix spec (đo theo dialog)
- **Nghiên cứu:**
  - Moreno & Mayer 2000 (coherence)
  - Newman & Schwarz 2018 (âm khó nghe làm giảm độ tin)
  - Coupé et al. 2019 (mật độ thông tin âm tiết)
  - Huber et al. 2019 B-Script (B-roll quanh từ khoá; phủ 13,2%)
  - Kizilcec et al. 2014 (mặt người và niềm tin)
  - Potter et al. 2014 (tốc độ nhận hình)
- **Ngành:** Walter Murch, *Dense Clarity – Clear Density* (luật 2,5 lớp); Mixkit SFX / Stock Music Free License; chính sách nhãn AI của TikTok và YouTube.
- Loudness nền tảng (TikTok, Reels, Facebook): **không có tài liệu chính thức**; −14 LUFS là quy ước cộng đồng.
- Danh sách đầy đủ kèm URL và mức tin cậy: `research/rsfx.json`, `research/rbroll.json`, `research/final_diagnosis_markdown.txt` §6.

## Phụ lục B — Bằng chứng

- `audit/timeline.png`: giọng, khoảng ngắt, 25 cue cũ của video 2.
- `audit/cues.csv`, `pauses.csv`, `results.json`: số đo từng cue, từng khoảng ngắt.
- `audit/video_v3_mapping.csv`: ghép từng mp4 với mục v3 theo nội dung (whisper 25 s đầu), cờ số lệch / placeholder / motion.
- `prototype/planner_v11.py` + `sim_v11_*.json`: planner đã chạy thật. Đây là **tham chiếu thuật toán**; R0a viết lại thành module có test.
- `prototype/measure_files.py` + `files_v11.json`: đo 39 file SFX.
- `prototype/xcorr_check.py`, `tilt.py`: lệch 42,67 ms và phổ giọng HeyGen.
- `research/*.json`: 6 báo cáo khảo sát, 3 báo cáo phản biện (workflow 1).
- `research/final_*.txt`: bản chốt của workflow.
- `research/spec_review_2026-09-11.json`: 2 báo cáo soát chéo spec bản 1 (58 phát hiện; bản 2 này đã xử lý).
