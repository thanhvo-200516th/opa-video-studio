# OPERATOR — việc của opa-operator (spec §7.2, §9, §10, §11.2, §12, Ruling R15)

Operator **chỉ chạy script** và theo dõi board; không viết `edit.json`, không
build/render, không dán số vào card/comment/summary, không ghi vào
`<n>/edit*`. Không có skill riêng cho vai này (Ruling R15) — mọi hướng dẫn
nằm ở đây. Chỉ chạy từ một phiên opa-operator tương tác (chat với user),
không bao giờ như một card kanban: trong card worker, Hermes chặn mọi lệnh
kanban ghi (complete, link, archive, comment) qua terminal.

**Đường dẫn và id card.** Script nằm ở
`C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/scripts/`
— luôn gõ đầy đủ, trong ngoặc kép (đường dẫn có dấu cách). Thư mục lô là
`D:/MMO/Van Minh AI/Vid Heygen/_batches/<b>/`; board của lô là `vm-heygen-<b>`.
Lệnh `hermes kanban` cần **id card** (`t_…`), không phải tiêu đề: tra trong
`_batches/<b>/cards.json`, khoá `vmh-<b>-approve-prep-<k>-a1`,
`vmh-<b>-approve-canary-a1`, `vmh-<n>-<stage>-a<k>` → trường `"id"`. Ví dụ dưới
đây dùng lô `b01`.

## 1. Luồng một lô, đầu tới cuối

1. **P0 — lập lô** (chỉ chạy script, không phán đoán). Hai điều kiện trước
   lệnh `make_cards.py` thật:
   - **Đúng một gateway gốc đang chạy.** Kiểm bằng lệnh chỉ đọc
     `hermes gateway list`: dòng `default` phải có `✓` kèm `PID …`, **mọi**
     dòng `opa-*` phải là `✗ … not running`. Dispatcher là singleton của
     gateway bật trước, đọc `kanban.*` trong config của gateway đó — gateway
     gốc đọc `C:/Users/Minh PC/AppData/Local/hermes/config.yaml`. Sai (dòng
     `default` là `✗`, hay có dòng `opa-*` là `✓`) thì dừng, báo user/controller:
     gateway gốc chỉ do user hoặc controller bật, bằng
     `MSYS_NO_PATHCONV=1 schtasks /run /tn Hermes_Gateway` (task
     `Hermes_Gateway` chạy `gateway-service/Hermes_Gateway.cmd`, đặt
     `HERMES_HOME` về thư mục gốc). **Không bao giờ** gõ `hermes gateway run`
     trong terminal của agent/operator: terminal đó mang `HERMES_HOME` của
     profile nên lệnh sẽ bật gateway của opa-operator. File
     `C:/Users/Minh PC/AppData/Local/hermes/logs/gateway.log` cộng dồn mọi lần
     chạy — chỉ tính dòng `kanban dispatcher: holding singleton dispatcher lock`
     và dòng `kanban dispatcher: embedded in gateway` nằm sau dòng
     `Starting Hermes Gateway...` cuối cùng (và không có `Gateway stopped` sau
     chúng). Không có dispatcher thì card nằm `ready` mãi mà `make_cards.py`
     không báo gì.
   - **Board của lô** (một lần mỗi lô):
     `hermes kanban boards create vm-heygen-b01 --name "Van Minh AI · HeyGen b01"`.
     `make_cards.py` chạy thật in `VID_ROOT: …` (phải là
     `D:/MMO/Van Minh AI/Vid Heygen`; biến `TH_VID_ROOT` còn đặt thì FAIL) rồi
     kiểm board trước tiên; thiếu board thì FAIL kèm đúng lệnh này, không tạo
     card nào.
   ```
   PYTHONIOENCODING=utf-8 python "C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/scripts/intake.py" --batch b01 --videos 16,21,27,51,53,59,60 --transcriber whisper --preset standard --rules 1.2.3
   PYTHONIOENCODING=utf-8 python "C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/scripts/make_cards.py" --batch b01 --board vm-heygen-b01 --check
   PYTHONIOENCODING=utf-8 python "C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/scripts/make_cards.py" --batch b01 --board vm-heygen-b01
   ```
   Một lô tối đa `batch.max_videos` (10) video, chọn bằng `--videos` (đợt 1:
   §13.4 mục 2). Video `batch.exclude_videos` (1, 2 — D11, đã giao) luôn bị
   loại. Không dùng `--all` cho lô dựng: nó chỉ chạy kèm `--allow-all`, là lệnh
   quét toàn bộ của dev (Gate 8) ghi ra `--out` nháp.
   `make_cards.py` (phase `prep`, mặc định) chỉ tạo **PREP-<k>** (opa-editor,
   ≤ `batch.prep_videos_per_card` video/card) → **APPROVE-PREP-<k>** (assignee
   `user`, status mặc định — dispatcher không bao giờ chạy card giao cho `user`
   (Ruling R28), card đứng chờ tới khi operator complete). Chưa có card video
   nào — canary chưa được chọn.
2. **PREP → APPROVE-PREP-<k>**: opa-editor viết phiếu, dựng `PREP-SHEET.md`.
   User đọc phiếu và trả lời. Operator **chép nguyên văn** lời duyệt (§3), rồi
   mới `hermes kanban --board vm-heygen-b01 complete <id APPROVE-PREP-<k>>`.
3. **Phase videos** — chỉ khi **mọi** card APPROVE-PREP-<k> của lô đã complete:
   ```
   PYTHONIOENCODING=utf-8 python "C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/scripts/make_cards.py" --batch b01 --board vm-heygen-b01 --phase videos --check
   PYTHONIOENCODING=utf-8 python "C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/scripts/make_cards.py" --batch b01 --board vm-heygen-b01 --phase videos
   ```
   Script đọc các phiếu `prep/prep-<k>.json` đã duyệt, in `canary: video <n>`
   (video `ok` intake.py đánh canary nếu phiếu vẫn ghi ok, không thì video ok
   số nhỏ nhất) rồi tạo theo thứ tự cha trước con: chuỗi **canary** INTAKE →
   PLAN → BUILD → VERIFY → **APPROVE-CANARY** (assignee `user`, status mặc định
   như trên) → 4 card INTAKE/PLAN/BUILD/VERIFY của từng video `ok` còn lại (cha
   = APPROVE-PREP của nó **và** APPROVE-CANARY). Video phiếu ghi `needs_*` không
   có card nào, nên không có chuỗi nào phải archive. Script FAIL và không tạo gì
   khi thiếu phiếu, phiếu sai khuôn, hoặc còn APPROVE-PREP chưa complete.
   `--check` FAIL khi card đã tạo có cha khác kế hoạch (status đổi sau khi tạo
   card) — dừng lại, hỏi dev.
4. **Canary** chạy đủ INTAKE → PLAN → BUILD → VERIFY trước bất cứ video nào khác.
5. **APPROVE-CANARY**: gửi user `final.mp4` + `VERDICT.md` của canary (gồm kế
   hoạch B-roll của nó nếu có; cách gửi và cách nghe ở §5). Operator chép
   nguyên văn lời duyệt (§3) rồi mới
   `hermes kanban --board vm-heygen-b01 complete <id APPROVE-CANARY>` — **các
   video còn lại của lô chỉ chạy sau card này**.
6. **Phần còn lại của lô**: các video `ok` khác (trừ canary) chạy 4 card
   INTAKE/PLAN/BUILD/VERIFY **lần lượt, không song song**: opa-editor chỉ chạy
   một card một lúc (`kanban.max_in_progress_per_profile: 1`, §10.6); card VERIFY
   của opa-verifier có thể chạy cùng lúc, còn whisper/render của mọi card xếp
   hàng qua khoá máy `_batches/.heavy.lock`. Mỗi card tự dừng ở `stage.py` —
   operator không can thiệp trừ khi có lỗi (§2).
7. **KPI và người duyệt (D5)** — sau mỗi card VERIFY complete, và một lần khi
   hết lô, chạy:
   ```
   PYTHONIOENCODING=utf-8 python "C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/scripts/collect_kpi.py" --batch b01
   ```
   Script ghi lại toàn bộ `_batches/b01/kpi.jsonl` (mỗi video đã VERIFY một dòng:
   `out/verify/kpi.json` + canary, mẫu, claim_gate; chạy lại không nhân đôi) và
   in mỗi video phải gửi user một dòng `GỬI USER: …` — làm theo §5.
8. **Đóng lô** — khi user đã trả lời mọi video `GỬI USER` và không còn video nào
   chờ dựng lại, xoá `node_modules` của các dự án đã xong (§13.4):
   ```
   PYTHONIOENCODING=utf-8 python "C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/scripts/collect_kpi.py" --batch b01 --prune-node-modules
   ```
   Chỉ xoá `node_modules` (cài lại được) của video VERIFIED / DONE_WITH_CONCERNS;
   video REJECTED và mọi file khác giữ nguyên.

## 2. Ma trận lỗi (spec §10.5) — ai xử lý gì

| Stage | Lỗi | `stage.py` làm gì | Ai xử lý |
|---|---|---|---|
| P0 | Số lệch / nghi hỏng | ghi `needs_input`/`needs_rerender` vào manifest; không tạo card INTAKE | user (qua PREP-SHEET) |
| INTAKE | ASR nghi sai | `guess:true`, đi tiếp; VERIFY → DONE_WITH_CONCERNS | user |
| INTAKE | Độ khớp < 0,80 | block `needs_input` | user |
| INTAKE | QA vo-clean / xcorr FAIL | block `capability` | dev (F1) |
| INTAKE | Dò mặt trượt quá ngưỡng (`face.json`, cổng `FACE_TRACK`: tỉ lệ trượt, chuỗi trượt dài nhất, chiều cao mặt) | block `capability` | dev |
| INTAKE, BUILD, VERIFY | Treo / timeout | process con quá trần (ffmpeg master 600 s, `npm install` và `remotion browser ensure` 900 s, still 180 s, render 1200 s) ⇒ giết cả cây, block `transient`. Hermes dừng card quá `max_runtime` (run `timed_out`) ⇒ Hermes tự chạy lại, nhưng process con cũ có thể còn giữ khoá nên lần chạy lại block `transient` | operator: sau `timed_out`, kill process sót (dưới bảng) **rồi mới** `--retry` |
| PLAN | `plan.json` `--check` FAIL sau 3 vòng | block `needs_input` | operator tạo `a2` với model mạnh hơn; `a2` dùng lại `plan.json` đang có, không làm lại từ đầu |
| PLAN | Agent viết script trong `Vid Heygen/<n>/` (`STRAY_SCRIPT`) | `--check` FAIL, nêu đường dẫn từng file | agent xoá rồi chạy lại |
| BUILD | text-safe FAIL | block; owner PLAN hoặc template | operator / dev |
| BUILD | `face_safe` còn chữ che miệng/mắt (`FACE_ROOM`) | block; owner PLAN — dòng lỗi có sẵn `Sửa:` dạng `breaks` hoặc `hero` | operator mở PLAN mới |
| BUILD | `lint_sfx` FAIL | block `capability` (lỗi skill) | dev; video chờ |
| BUILD | loudness FAIL | tự thử lại 1 lần | lần 2 thì dev |
| BUILD | xcorr / sync FAIL | block `capability` | dev |
| VERIFY | REJECTED | in `owner_stage` | operator mở card mới cho đúng `owner_stage` |
| VERIFY | `edit.json` khác bản ghép lại từ `plan.json` (`PLAN_DRIFT`) | REJECTED, owner PLAN — có người sửa tay `edit.json` | operator mở PLAN mới |
| VERIFY | Khung mặt lệch so với lúc dò (`FACE_DRIFT`) | CONCERN, không REJECT | user xem khi duyệt |
| VERIFY | Còn script lạ trong `Vid Heygen/<n>/` (`STRAY_SCRIPT`) | CONCERN, không REJECT | operator dọn |

Mã lỗi → `owner_stage` (từ `VERDICT.json`/lint): S04, S28, S25 (xcorr nguồn),
cổng độ khớp → INTAKE/dev; L1–L14, S01–S27, S29 → BUILD (lỗi skill) → dev;
`FACE_TRACK` → INTAKE/dev;
`PLAN_JSON`, `PLAN_UNDECIDED`, `PLAN_STALE`, `UNKNOWN_ID`, `HERO_RANGE`, `NO_EMPHASIS`, `STRAY_SCRIPT`, `PLAN_DRIFT`, `FACE_ROOM`, B21 → PLAN; B13, B14, text-safe → PLAN hoặc template.
Hợp đồng PLAN 1.1.1: **agent ghi `plan.json`; code ghép ra `edit.json`**. Không ai sửa tay `edit.json` — VERIFY ghép lại sẽ bắt `PLAN_DRIFT`.

**Process sót sau `timed_out`** (`hermes kanban --board vm-heygen-b01 show <id>`
có run kết thúc `timed_out`): Hermes chỉ giết process worker; `stage.py` và
process con của nó (python/node/ffmpeg) có thể vẫn chạy, giữ
`VID_ROOT/<n>/.stage.lock` và `_batches/.heavy.lock`. Trước `--retry`, liệt kê
rồi kill cả cây các process có dòng lệnh chứa thư mục dự án
`VID_ROOT/<n>/edit-r1.2.3` hoặc `stage.py … --task <id card cũ>` — ví dụ video
16, card cũ `t_abc12345` (`?` khớp cả `/` lẫn `\`):

```
MSYS_NO_PATHCONV=1 powershell -NoProfile -Command 'Get-CimInstance Win32_Process | Where-Object { $_.Name -match "^(python|node|ffmpeg)" -and ($_.CommandLine -like "*Vid Heygen?16?edit-r1.2.3*" -or $_.CommandLine -like "*stage.py*t_abc12345*") } | Select-Object ProcessId,Name,CommandLine | Format-List'
MSYS_NO_PATHCONV=1 powershell -NoProfile -Command 'Get-CimInstance Win32_Process | Where-Object { $_.Name -match "^(python|node|ffmpeg)" -and ($_.CommandLine -like "*Vid Heygen?16?edit-r1.2.3*" -or $_.CommandLine -like "*stage.py*t_abc12345*") } | ForEach-Object { taskkill /F /T /PID $_.ProcessId }'
```

Lệnh đầu chỉ liệt kê, lệnh sau kill cả cây. Chạy lại lệnh đầu phải không còn
dòng nào, rồi mới `make_cards.py … --retry <n>:<STAGE>` (§4).

**Đọc một card bị block:** `kind` chính là nguyên nhân, và `reason` bắt đầu
bằng cùng chữ đó: `transient` (video hoặc máy đang bận, hay process con quá
trần thời gian), `needs_input` (thiếu đầu vào, cần user/operator quyết),
`capability` (lỗi skill hoặc lỗi máy → việc của dev). Block nào của worker
Hermes cũng giữ tới khi có người xử lý — luôn xử lý bằng `--retry` (§4),
không unblock.

**Số lần Hermes tự chạy lại** (treo, timeout, worker chết, thiếu `kanban_complete`):
`budgets.<stage>.retries` trong `rules.json` là số lần thử lại **sau** lần đầu
(INTAKE/BUILD/VERIFY 1, PREP/PLAN 2). Hermes `--max-retries N` ngắt ở lần hỏng
thứ N, nên `make_cards.py` truyền `--max-retries <retries + 1>` — ví dụ BUILD
hỏng lần 1 thì Hermes tự chạy lại, hỏng lần 2 thì card tự block (§10.5 "lần 2
thì block").

**Số lượt (`budgets.<stage>.turns`) chỉ là mức tham khảo:** Hermes chỉ ép
`max_runtime` và số lần thử lại, không ép số lượt theo card; trần thật là
`agent.max_turns` (60) của profile cho mỗi lần chạy. Đo sau lô: với mỗi card,
lấy số `API call #N` lớn nhất của từng lần chạy (mã phiên trong ngoặc vuông) ở
`C:/Users/Minh PC/AppData/Local/hermes/profiles/<opa-editor|opa-verifier>/logs/agent.log`,
tính cả các lần chạy lại, rồi so với `turns` (PREP/PLAN 25, INTAKE/BUILD 15,
VERIFY 20) và với 60.

## 3. Ghi lời duyệt của user — nguyên văn, không diễn giải

Với mọi card `APPROVE-*` (PREP hay CANARY), và mọi lời duyệt video ở §5:

1. Copy **y nguyên** câu trả lời của user (không rút gọn, không đổi ý, không
   thêm số liệu của mình vào).
2. Card `APPROVE-*`: dán vào comment của card bằng tool `kanban_comment`
   (task_id = id card, board = `vm-heygen-b01`, body = lời user nguyên văn) —
   không qua shell. Buộc phải dùng terminal thì chỉ dùng heredoc nháy đơn (Git
   Bash đổi `$`, `` ` ``, `"` nằm trong đối số nháy kép, heredoc thì không):
   ```
   hermes kanban --board vm-heygen-b01 comment <id> "$(cat <<'EOF'
   <lời user nguyên văn>
   EOF
   )"
   ```
3. Dán cùng câu đó vào cuối `_batches/<b>/APPROVALS.md`, dưới mục
   "## Lời duyệt" (khung do `intake.py` tạo), thành **một mục mới**: dòng đầu
   mục bắt đầu bằng `- ` và phải có tên card (hoặc số video) **và ngày dạng
   `YYYY-MM-DD`** — ví dụ `- APPROVE-PREP-1 — 2026-09-20: <lời user nguyên văn>`.
   Lời user nhiều dòng thì dán tiếp y nguyên ngay dưới, kể cả dòng user gạch
   đầu `- ` (script chỉ mở mục mới ở dòng `- ` có ngày). Chỉ ghi thêm, không
   sửa dòng cũ; `intake.py` không bao giờ đụng mục này.
4. Chỉ sau khi cả hai bước trên xong mới
   `hermes kanban --board vm-heygen-b01 complete <id>` — **card APPROVE-\* là
   card duy nhất operator được complete, và chỉ complete một lần sau khi user
   đã trả lời.**

## 3b. User muốn sửa phiếu PREP

Khi user trả lời `PREP-SHEET.md` bằng yêu cầu sửa (chưa duyệt):

1. **Không** complete card APPROVE-PREP-<k>.
2. Ghi lời user nguyên văn như §3 bước 1–3: comment trên APPROVE-PREP-<k>, và
   một mục mới dưới "## Lời duyệt" của `APPROVALS.md` có chữ `PREP-<k>`, ví dụ:
   ```
   - APPROVE-PREP-1 — 2026-09-20 — sửa phiếu: "Sửa mấy chỗ:
   - video 16 để needs_input, chờ tôi quay màn hình
   - video 21 ghép mục v3 số 12"
   ```
   `stage.py PREP` của lần thử mới in đúng các mục nhắc `PREP-<k>` này (đủ mọi
   dòng của lời user) và dặn agent sửa phiếu theo đó — comment trên card duyệt
   thì agent không thấy.
3. Chạy `make_cards.py … --retry PREP-<k>` (§4) và làm đủ việc nó in (link,
   unlink, archive).
4. Khi card `PREP-<k> a<N>` xong, gửi lại `PREP-SHEET.md` mới cho user và xin
   duyệt lại từ đầu (§3). Chỉ complete card APPROVE-PREP-<k> sau lời duyệt mới đó.

## 4. Không bao giờ unblock một card lần hai

Luật Hermes (spec §10.5): **card đã block thì không unblock lần hai.** Cách
đúng khi cần chạy lại một stage:

```
PYTHONIOENCODING=utf-8 python "C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/scripts/make_cards.py" --batch b01 --board vm-heygen-b01 --retry <n>:<STAGE>
PYTHONIOENCODING=utf-8 python "C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/scripts/make_cards.py" --batch b01 --board vm-heygen-b01 --retry PREP-<k>
```

Lệnh trên tự tính lần thử kế tiếp (`a<k+1>`) và in đúng việc operator phải
làm tay (id thật đã điền sẵn), luôn theo thứ tự:

1. Nếu chuỗi cũ có card duyệt (APPROVE-PREP-<k> hoặc APPROVE-CANARY) nối vào:
   `hermes kanban --board vm-heygen-b01 link <id card mới> <id card duyệt>` rồi
   `hermes kanban --board vm-heygen-b01 unlink <id card cũ cuối> <id card duyệt>`
   — nối lại **trước** khi archive, vì card cha đã archive tính là xong nên card
   duyệt (hay card con cũ) sẽ chạy/complete được ngay.
2. `hermes kanban --board vm-heygen-b01 archive <id card cũ> [...]` — archive
   card(s) cũ, từ cuối chuỗi về đầu (thứ tự script in sẵn).

Không tự gõ `hermes kanban unblock` — không có thao tác "unblock" hợp lệ ở
đây; luôn đi qua `--retry` + archive + tạo mới.

**Không chạy lại `intake.py` cho cả lô.** Lô đã có `batch_manifest.json` thì
`intake.py` từ chối nếu thiếu `--update`; `--update --videos <n>` chỉ ghép lại
đúng video đó, giữ nguyên video khác và mục "## Lời duyệt" của `APPROVALS.md`.
Chỉ dùng `--update` khi reason của card nêu đúng lệnh đó — card INTAKE block vì
"vo_script … không khớp sha256" (lời chuẩn bị sửa sau P0): hỏi user; user xác
nhận lời chuẩn trong kịch bản v3 thì chạy **nguyên văn** lệnh `intake.py …
--update --videos <n> --transcriber "cache:…/mapping.csv" …` in trong reason,
rồi `make_cards.py … --retry <n>:INTAKE` như trên. Video `needs_*` user đã
render lại thì **không** kéo lại vào lô cũ: đưa vào một lô sau
(`intake.py --batch b02 --videos …`), đi PREP và duyệt như mọi video khác.

## 5. Gửi video cho user duyệt (D5, spec §11.2)

**Gửi video nào:** canary (qua card APPROVE-CANARY, §1 bước 5), mẫu 1/5 (cờ
`sample` trong `batch_manifest.json`, cũng in ở đầu `APPROVALS.md`), **mọi**
video DONE_WITH_CONCERNS và **mọi** video có `claim_gate`. `collect_kpi.py`
in đúng danh sách này, mỗi video một dòng `GỬI USER: video <n> — <lý do> —
<final.mp4> + <VERDICT.md>`. Video REJECTED không gửi user (mở lần thử mới, §4).

**Gửi thế nào:** qua kênh chat operator đang dùng với user, gửi file
`out/final.mp4` và `out/verify/VERDICT.md` đúng đường dẫn script in ra, kèm lý
do (chép nguyên chữ của dòng `GỬI USER`, không tự tóm tắt số) và cách nghe:
loa điện thoại khoảng nửa âm lượng rồi tai nghe; chỗ yên rồi chỗ ồn; nghe một
lượt không nhìn timeline rồi mới ghi `mm:ss`. Video `claim_gate`: nhắc user
**không đăng trước khi user xác nhận** claim (§13.4 mục 5).

**Ghi lại:** lời duyệt → `APPROVALS.md` như §3; lời chê → `FEEDBACK.jsonl` (§6).

## 6. B-roll (1.2.0)

- BUILD block `broll_assets` + `BROLL_GEN …` ⇒ kiểm 9router (hạn mức/mạng), rồi `make_cards.py … --retry <n>:BUILD`; asset đã tạo nằm trong bộ đệm.
- `BROLL_FLAT …` ⇒ `--retry <n>:PLAN`, lần PLAN đó đổi prompt hoặc tăng `"v"` của ô bị báo.
- Ảnh lạc đề/lỗi hình (V7 hay controller thấy) ⇒ ghi comment ô nào + lý do, `--retry <n>:PLAN`, PLAN tăng `"v"` và viết lại prompt ô đó.
- Video heavy luôn có claim_gate — không đăng trước khi user duyệt. Chi phí: tối đa 1 clip ≈ $0,35/video.

## 7. Feedback thành luật (F1, spec §12) — `_batches/<b>/FEEDBACK.jsonl`

Mỗi lời chê/ý kiến của user về một video là **một dòng JSON** ghi thêm vào cuối
`D:/MMO/Van Minh AI/Vid Heygen/_batches/<b>/FEEDBACK.jsonl` (tạo file nếu chưa
có; không sửa, không xoá dòng cũ). Dòng spec §12
`FB | video 07 @1.1.0 standard | 00:24.9 | tag: bé | mức 2 | "cú đập chỗ khóa 3 thứ nhỏ quá"`
ghi thành:

```
{"fb_id": "b01-07-01", "video": 7, "rules": "1.1.0", "preset": "standard", "at": "00:24.9", "tag": "bé", "muc": 2, "quote": "cú đập chỗ khóa 3 thứ nhỏ quá", "date": "2026-09-20"}
```

- `fb_id` = `<lô>-<số video 2 chữ số>-<thứ tự 2 chữ số>` (01, 02… trong video
  đó) — `overrides.json` của F1 trỏ về id này (§10.3).
- `rules`, `preset`: chép từ thân card của video (dòng `RULES: …@<ver>`,
  `PRESET:`). `at` (`mm:ss.s`), `tag`, `muc` và `quote` là **lời của user**,
  chép nguyên văn — `tag` ∈ {to, bé, dày, thưa, trễ, sớm, lạc chất, giọng, nhạc,
  hình, chữ}; user chưa nói mốc hay mức thì hỏi lại, không tự đoán.
- Operator chỉ ghi. Phân loại, đo và sửa luật là việc của phiên dev (F1); luật
  mới áp từ lô sau, video đã xong giữ nguyên.

## 8. Không bao giờ được làm (spec §10.1)

- Viết `edit.json`; tự build hay render.
- Dán số (thời lượng, dB, ms, sha…) vào card, comment, hay summary — số chỉ
  do script in ra, agent/operator chỉ chép nguyên văn.
- Ghi vào bất cứ đâu trong `<n>/edit*` (đó là việc của INTAKE/PLAN/BUILD/VERIFY)
  — ngoại lệ duy nhất là `collect_kpi.py --prune-node-modules` ở bước đóng lô.
- Unblock một card lần thứ hai (xem §4).
- Chạy `python -c`, `node -e`, `execute_code`, hay tự viết code/lệnh mới — code
  chỉ chạy qua script có sẵn trong `releases/<ver>/scripts/` hoặc lệnh in
  nguyên văn trong file này. Luật này nói về chạy code: nối thêm vào
  `APPROVALS.md` (§3) và `FEEDBACK.jsonl` (§6) bằng tool file (chỉ ghi thêm
  cuối file, không sửa dòng cũ) là **được phép**.
- Complete một card `APPROVE-*` trước khi user đã thực sự trả lời.

## M0 — con trỏ trong SOUL.md (controller ghi một lần khi chuyển sang 1.1)

Không phải việc của operator; ghi ở đây để hai dòng có phiên bản. Mỗi
`profiles/<p>/SOUL.md` có đúng dòng dưới đây, nguyên văn, trên **một** dòng —
`tools/check_drift.py` mục 7 đòi dấu `dung-video-talking-head@1.1`, đường dẫn
và chữ `KHÔNG áp dụng` cùng nằm trên dòng đó. Controller chạy
`tools/check_drift.py` trước mỗi lô và sau mỗi card; mục 9 FAIL khi thư mục
skill đang dùng có thay đổi chưa commit (worker sửa skill).

opa-editor và opa-verifier:

```
dung-video-talking-head@1.1 — card có dòng "RULES: dung-video-talking-head@<ver>": chỉ làm theo C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/SKILL.md và dòng NEXT của stage.py; các quy trình riêng trong SOUL này KHÔNG áp dụng cho card đó (không tự render, không tự chấm thêm, summary/metadata đúng như dòng NEXT của stage.py dặn, REJECTED thì kanban_block đúng như NEXT).
```

opa-operator:

```
dung-video-talking-head@1.1 — lô vm-heygen-*: chỉ làm theo C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/releases/1.2.3/stages/OPERATOR.md; task packet và quy trình riêng trong SOUL này KHÔNG áp dụng cho các lô đó.
```
