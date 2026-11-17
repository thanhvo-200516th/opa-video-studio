# Quy trình nhận lệnh: kịch bản → A-roll HeyGen nhiều góc + B-roll + source thật + tư liệu thật

Áp dụng khi người dùng gửi lệnh kiểu: "đọc kịch bản số … từ link …, làm A-roll trên HeyGen và B-roll trên Muse / Flow, đây là key HeyGen …".
Chốt với người dùng 2026-11-17. Mỗi bước MỘT lệnh, đọc kết quả rồi mới sang bước sau. ⏸ = dừng cho người dùng duyệt trước khi tốn credit.

## Bước 0 — Kiểm hạ tầng (0 credit, làm trước mọi thứ)
| Dịch vụ | Lệnh kiểm | Hỏng thì |
|---|---|---|
| HeyGen | khoá chỉ nhận trong lệnh: `export HEYGEN_API_KEY=…` trong phiên hoặc `--key-file <file người dùng chỉ>`; KHÔNG ghi khoá vào file / báo cáo (G2, A4). `$PY scripts/heygen_looks.py list --group <id> --out W/looks.json` (hoặc `--all`) | không có khoá → mọi lệnh HeyGen chạy thử; báo "cần khoá" |
| Muse | `$PY scripts/broll_fix.py ready` rồi `curl -s http://127.0.0.1:18610/readyz` (đọc `accounts.available / invalid`) | tài khoản `invalid` (401) → nhờ người dùng đăng nhập lại trong trang quản trị muse2api; Muse chỉ là phương án phụ (D3, D15) |
| Google Flow | MCP `google-flow` (đăng ký cho Claude Code ở user scope): `flow_list_accounts`, `flow_inspect_account`, `flow_job_status` cho job đang "processing"; không có công cụ `flow_*` → trình duyệt Cindy (`references/flow-broll.md`) | phiên Flow hết hạn → người dùng bấm Connect Flow trong extension (không gõ mật khẩu hộ); không mua credit |

## Bước 1 — Đọc lô kịch bản
`$PY scripts/analyze_and_scaffold.py from-spec "<SPEC.md>" --out-dir "<thư mục tổng>"` (JSON: `from-json`). Ra mỗi kịch bản một thư mục có `00_storyboard_manifest.json`.

## Bước 2 — Quyết định số A-roll mỗi video (luật cứng)
- Mỗi video **2–4 cảnh A-roll**, ở **các góc khác nhau** (looks của cùng một người trong HeyGen): mở đầu (hook), bước ngoặt, kêu gọi (CTA), thêm 1 cảnh tuỳ nội dung.
- Đọc kỹ kịch bản TRƯỚC khi chốt: đoạn nào có **source quay thật** phù hợp (thư mục "soucre thô", D10: mỗi clip ≤ 2 lần) thì dùng source thật, không làm A-roll cho đoạn đó.
- Phần còn lại: B-roll Google Flow (mặc định, D15), **tư liệu thật** (bài báo / video / số liệu tìm được — thẻ nguồn có ghi tên báo + ngày), asset 3D, chèn minh hoạ (đồ thị, polaroid, thẻ trích dẫn — hồ sơ minimal-edu).

## Bước 3 — Ngân hàng A-roll dùng chung cho cả lô (30–50 kịch bản)
`$PY scripts/aroll_bank.py <các manifest> --out W/aroll_bank [--looks 5 --reuse-max 3 --max-slots 4]` → `bank.json`, `plans.json`, `stats.json`, `approval.md`.
- Chỉ dùng chung **câu giống hệt nhau** (HeyGen khớp khẩu hình theo lời). Đo 2026-11-17 trên 41 kịch bản: trùng tự nhiên = 0 (giống nhất 0,44) → câu chung lấy từ `references/aroll-bank-library.json` (mở đầu / chuyển ý / kêu gọi viết chung), ý riêng của từng video chuyển sang B-roll + chữ trên màn hình.
- Số render tối thiểu = ⌈số video × số cảnh A-roll / số lần dùng lại⌉ (41 video × 2 cảnh / 3 lần = 28; 30 × 2 / 3 = 20). Báo người dùng con số thật, không hứa 15–20 khi phép tính không cho phép.
- ⏸ Người dùng duyệt `approval.md` (câu gốc → câu chung, từ khoá kêu gọi) trước khi dựng.

## Bước 4 — Gán góc quay
`$PY scripts/heygen_looks.py pick --looks W/looks.json --videos KB08=3,KB09=2 --angles 3` — mỗi video 2–4 góc khác nhau, hai cảnh A-roll liền nhau không trùng góc, các góc được dùng đều trong lô. Chi tiết: `references/kb-heygen-multi-angle.md`.

## Bước 5 — Dựng A-roll
1. `$PY scripts/render_heygen_aroll.py --bank W/aroll_bank/bank.json --looks W/looks.json --assign auto --estimate --usd-per-min <giá>` → in tổng giây / chi phí ước tính. ⏸ duyệt chi phí.
2. `… --yes --key-file <file>` (mỗi câu chung dựng MỘT lần vào `bank/<bank_id>.mp4`).
3. `$PY scripts/render_heygen_aroll.py link W/aroll_bank/bank.json "<thư mục tổng>"` → gắn đúng `<STT>_a-roll-<N>.mp4` vào từng video.

## Bước 6 — B-roll
SKILL §2 bước 5 / 5b (prompt tiếng Anh từ chính lời cảnh, Flow mặc định, Muse khi Flow hỏng và tài khoản Muse còn hoạt động). Kiểm `broll_fix.py verify` + nhìn bảng ảnh.

## Bước 7 — Tư liệu thật (đang thử nghiệm)
Với câu có dữ kiện / số / tên riêng: tìm bài báo (RSS báo Việt, Google News) → kiểm câu trích có trong bài → chụp tiêu đề → thẻ nguồn (tên báo · ngày). Bản thử: `.handoff/evidence-inserts/proto/evidence.py` (chưa nằm trong skill). Luôn ghi nguồn, chỉ trích ngắn, không tải video của người khác.

## Bước 8 — Dựng & duyệt
SKILL §3 (FilmCraft). Kiểu minimal / Brooks / Joseph → hồ sơ `minimal-edu` (P6–P12, tốc độ 1.05x). Không xuất MP4 khi chưa được "duyệt" (A1).
