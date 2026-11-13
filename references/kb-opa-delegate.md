# kb-opa-delegate — toàn văn tài liệu của nguồn `opa-delegate`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/opa-delegate/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: opa-delegate/SKILL.md ===== -->

---
name: opa-delegate
description: Use khi user muốn giao việc cho các agent OPA Hermes chạy nền thay vì Claude tự làm — thường để tiết kiệm token. Triggers — "giao việc cho OPA", "chia việc cho agent OPA Hermes", "để OPA làm", "đẩy sang Hermes", "chạy bằng agent opa", "giảm token bằng cách giao cho agent". KHÔNG use cho — việc cần Claude tự sửa code ngay tại chỗ, hỏi đáp, hoặc khi user muốn subagent/Workflow của Claude (đó là hệ khác, xem mục Phân biệt).
license: MIT
version: 1.0
argument-hint: "<mô tả việc cần giao> [--board <slug>]"
---

# OPA Delegate — giao việc cho agent Hermes

> Cầu nối giữa yêu cầu tiếng Việt của user và CLI `hermes kanban`.
> Claude Code **không có MCP tool nào** gọi được OPA. Đường duy nhất là CLI qua Bash.

## Vì sao skill này tồn tại

Khi user nói "chia việc cho các agent OPA Hermes", Claude thường hiểu nhầm thành
subagent/Workflow của chính nó rồi tung nhiều agent Opus — **ngược hẳn** mục tiêu
tiết kiệm token. Skill này ép đúng đường: đẩy việc sang process Hermes riêng chạy
model rẻ hơn, token của nó **không vào context Claude**.

## Phân biệt hai hệ (đọc trước khi làm)

| | Agent OPA Hermes | Subagent Claude |
|---|---|---|
| Gọi bằng | `hermes kanban create` (Bash) | tool `Agent` / `Workflow` |
| Token | KHÔNG vào context Claude | Vào, tính đủ |
| Model | grok-4.6 qua cliproxy | Opus/Sonnet |
| Dùng khi | Việc dài, chạy nền, cần tiết kiệm | Việc cần kết quả ngay trong lượt |

User nói "OPA" / "Hermes" → **luôn** là cột trái. Không được thay bằng subagent Claude.

## Binary

```
"C:/Users/Minh PC/AppData/Local/hermes/hermes-agent/venv/Scripts/hermes.exe"
```

Đặt vào biến cho gọn: `HB="C:/Users/Minh PC/AppData/Local/hermes/hermes-agent/venv/Scripts/hermes.exe"`

## Chọn profile theo loại việc

| Profile | Giao việc gì |
|---|---|
| `opa-operator` | Điều phối, dispatcher. **Mặc định** khi không rõ giao ai |
| `opa-dev` | Full-stack, tích hợp |
| `opa-dev-fe` | Frontend, UI, web |
| `opa-dev-be` | Backend, API, dữ liệu |
| `opa-platform` | DevOps, SRE, deploy, production |
| `opa-architect` | Kiến trúc hệ thống, solution design |
| `opa-verifier` | QA độc lập, thu thập bằng chứng |
| `opa-product` | PRD, roadmap, acceptance |
| `opa-design` | Visual design, design system |
| `opa-research` | Nghiên cứu, kiểm chứng nguồn |
| `opa-reporter` | Báo cáo tổng hợp, decision log |
| `opa-data` | Analytics, metric, event taxonomy |
| `opa-marketing` / `opa-sale` | Marketing / Sales |
| `opa-accounting` / `opa-legal` | Kế toán / Pháp lý |
| `opa-editor` | Video, post-production |

## Quy trình

### 1. Chọn board

Mỗi board là một hàng đợi độc lập, DB riêng, dispatcher riêng.

```bash
$HB kanban boards list                        # xem board đang có
$HB kanban boards create <slug> --name "Tên"  # tạo board mới cho project mới
```

Luôn truyền `--board <slug>` trong mọi lệnh để khỏi phụ thuộc board đang active.

### 2. Tạo task

```bash
$HB kanban --board <slug> create "Tiêu đề ngắn" \
  --body "Spec đầy đủ: bối cảnh, file liên quan, ràng buộc, tiêu chí hoàn thành" \
  --assignee opa-dev-fe \
  --workspace worktree \
  --priority 2 \
  --created-by claude-code \
  --json
```

Tuỳ chọn hay dùng:

- `--workspace scratch|worktree|dir:<path>` — `worktree` khi task cần sửa code và ra PR riêng
- `--branch wt/<ten>` — đặt tên nhánh cho task worktree
- `--parent <task_id>` — task con, chỉ chạy sau khi cha xong (lặp lại được)
- `--skill <ten>` — nạp sẵn skill vào worker
- `--max-runtime 30m` — chặn task chạy vô hạn
- `--idempotency-key <key>` — chống tạo trùng khi chạy lại
- `--triage` — chưa rõ spec, để specifier làm rõ trước

### 3. Chia việc lớn

Nhiều task song song + một task tổng hợp phụ thuộc chúng:

```bash
P=$($HB kanban --board <slug> create "Tổng hợp kết quả" --assignee opa-reporter --json | python -c "import sys,json;print(json.load(sys.stdin)['id'])")
$HB kanban --board <slug> create "Nhánh A" --assignee opa-dev-fe --workspace worktree --json
$HB kanban --board <slug> create "Nhánh B" --assignee opa-dev-be --workspace worktree --json
$HB kanban --board <slug> link <id_A> $P    # A là cha của P
```

Hoặc dùng swarm dựng sẵn (worker song song → verifier → synthesizer):

```bash
$HB kanban --board <slug> swarm "Mục tiêu cuối" \
  --worker opa-dev-fe:"Làm UI" --worker opa-dev-be:"Làm API" \
  --verifier opa-verifier --synthesizer opa-reporter
```

### 4. Theo dõi (rất ít token)

```bash
$HB kanban --board <slug> stats                  # đếm theo status + assignee
$HB kanban --board <slug> list --status running
$HB kanban --board <slug> show <task_id>         # chi tiết + comment + event
```

Dispatcher chạy **trong gateway**, quét mỗi 60s. Không cần gọi `dispatch` tay.
Nếu gateway chết thì task nằm im — kiểm tra bằng `$HB gateway status`.

### 5. Lấy kết quả

`show <task_id>` in ra field `result` (summary do worker ghi khi `kanban_complete`).
Đọc summary, **không** đọc toàn bộ log — mục đích là tiết kiệm token.

## Bẫy thường gặp

- **Đừng tự chạy `dispatch`** trừ khi gateway chết. Gateway đã tự quét.
- **Brief phải tự đủ.** Worker không thấy hội thoại này. Thiếu path/ràng buộc → làm sai.
- **`--workspace scratch` là mặc định**, không sửa được code repo. Cần sửa code thì phải `worktree` hoặc `dir:<path>`.
- **Worktree tích tụ.** Dọn định kỳ bằng `$HB worktree`.
- **Tắt Ultracode** khi làm việc kiểu này — nó đẩy Claude tự tung Workflow, đối nghịch mục tiêu tiết kiệm token.

## Xác nhận trước khi tạo hàng loạt

Tạo >3 task một lúc thì **trình danh sách cho user duyệt trước** (tiêu đề + assignee),
tạo sau khi user gật. Task đã dispatch thì worker chạy ngay, huỷ tốn công hơn hỏi.

<!-- ===== /file: opa-delegate/SKILL.md ===== -->
