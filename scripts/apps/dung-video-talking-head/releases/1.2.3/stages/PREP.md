# PREP — phiếu chuẩn bị của lô (spec §7)

Bước 0 của mỗi lô, trước khi dựng video nào: đọc lời chuẩn từng video, xác nhận
trạng thái, phân loại nhu cầu B-roll, gắn cờ claim. **Agent chỉ viết một file:
`prep/prep-<k>.json`.** Không dựng, không tạo card, không sửa file nào khác.
User đọc `PREP-SHEET.md` (script dựng từ phiếu) rồi duyệt ở card
`APPROVE-PREP-<k>` — **chỉ phiếu đã duyệt mới là nguồn quyết định B-roll**
(§7.2). Card INTAKE của các video trong phiếu chỉ chạy sau lời duyệt đó.

## 1. Vòng làm việc

1. Lệnh đầu của card (SKILL.md mục 1: `stage.py PREP --task <id>`) — script in: file này,
   `mapping.csv`, hai file kịch bản đạo diễn/phân loại, nơi ghi phiếu, và với
   từng video: trạng thái intake.py, đường dẫn lời chuẩn, dòng `mapping.csv`
   (điểm ghép, điểm giống khối motion, cờ, **lời whisper nghe được ở đầu
   video**), ba dòng **gợi ý** ghép (mục v3, dòng đạo diễn, dòng phân loại —
   kèm điểm). So lời whisper nghe được với lời chuẩn để thấy HeyGen đọc sai.
   Script cũng in lời user về `PREP-<k>` trong `APPROVALS.md`; từ lần thử a2
   (user đòi sửa phiếu) thì sửa phiếu đúng theo các lời đó.
2. Đọc lời chuẩn `_batches/<b>/vo_script/<n>.txt` của từng video. Cần thêm ý
   cảnh/B-roll dự kiến thì đọc đúng dòng `## Video NN — …` trong file đạo diễn.
3. Viết `prep/prep-<k>.json` theo khuôn §2, **đủ mọi video của card** (kể cả
   video `needs_rerender` / `needs_input` — user cần thấy lý do).
4. Kiểm phiếu: chạy đúng lệnh ở dòng NEXT (`stage.py PREP --check --task <id>`,
   đường dẫn tuyệt đối trong ngoặc kép) — chạy `check_prep.py`, kiểm phiếu đúng
   lô và đúng bộ video của card, rồi dựng `PREP-SHEET.md`. In `ĐẠT` và
   `RESULT: PASS` là xong card: gọi tool `kanban_complete` đúng như dòng NEXT
   (summary chép nguyên văn dòng `ĐẠT: …` và dòng `RESULT: PASS`, metadata =
   JSON dòng `METADATA`).
5. `FAIL` thì sửa đúng các lỗi được in rồi chạy lại lệnh ở dòng NEXT. FAIL hay
   BLOCK thì **không** complete.

## 2. Khuôn `prep-<k>.json`

```jsonc
{
  "batch": "b01",
  "videos": [
    { "n": 16, "status": "ok", "reasons": [],
      "broll_class": "heavy",
      "assets": [ { "desc": "Quay màn hình tạo 5 ảnh từ 1 ảnh gốc",
                    "anchor_quote": "5 tài sản từ 1 ảnh",
                    "kind": "screen_rec", "owner": "user", "due": "2026-09-20" } ],
      "claim_gate": true, "claim_reasons": ["cần test thật: \"miễn phí và trả phí\""],
      "note": "tuỳ chọn — CONCERN, gợi ý ghép sai, lời user đã trả lời" },
    { "n": 7, "status": "ok", "reasons": [],
      "broll_class": "light",
      "assets": [ { "desc": "Lưới chín góc chụp cùng một sản phẩm trên nền studio",
                    "anchor_quote": "Tôi yêu cầu AI tạo chín góc",
                    "kind": "ai_video", "owner": "agent", "due": null },
                  { "desc": "Cận chất liệu da của sản phẩm dưới ánh sáng mềm",
                    "anchor_quote": "Ảnh cận chất liệu dùng để tăng tin tưởng",
                    "kind": "ai_image", "owner": "agent", "due": null } ],
      "claim_gate": false, "claim_reasons": [] },
    { "n": 31, "status": "needs_rerender", "reasons": ["placeholder: đọc nguyên [TIN MỚI]"],
      "broll_class": "none", "assets": [], "claim_gate": false, "claim_reasons": [] }
  ]
}
```

- **Mọi khoá phải có mặt** (trừ `note`), không thêm khoá lạ. Danh sách trống thì
  để `[]`.
- `n` = số video của card; mỗi video đúng một lần.

## 3. `status` — video có dựng được không

| Giá trị | Khi nào | `reasons` |
|---|---|---|
| `ok` | lời nghe được đúng lời chuẩn, dựng được | `[]` |
| `needs_rerender` | HeyGen đọc sai, phải render lại: đọc nguyên placeholder `[IN HOA]`, đọc chỉ dẫn APPLY CUSTOM MOTION, lời lệch hẳn lời chuẩn | bắt buộc: `placeholder` / `motion` / `lời lệch` + trích câu |
| `needs_input` | cần user quyết: số folder lệch mục v3, file trùng kịch bản, placeholder đọc thành chữ mà câu vẫn có nghĩa | bắt buộc, nói rõ user cần quyết gì |

- Giữ status của intake.py, trừ khi lời chuẩn cho thấy rõ intake.py sai — khi đó
  ghi lý do vào `note`.
- Chỉ đổi `needs_rerender` / `needs_input` thành `ok` khi user đã trả lời rõ;
  chép nguyên văn lời user vào `note`.
- Ca như video 32 (`[CÔNG CỤ]` đọc thành "công cụ", câu vẫn nghĩa): ghi CONCERN
  vào `note`, để user quyết khi duyệt.

## 4. `broll_class` — nhu cầu B-roll (D6)

**Từ 1.2.0 (user duyệt 2026-09-23, Ruling R206): mặc định `light`.** Mọi video của lô dựng bằng 1.2.0 có B-roll AI minh hoạ
(code tự tìm chỗ chèn, agent PLAN viết prompt) — kể cả talking-head chia sẻ tư duy: minh hoạ bối cảnh/ví dụ vẫn làm video đỡ đơn điệu.
Chỉ chọn khác khi đúng điều kiện ở bảng:

| Giá trị | Khi nào | Asset |
|---|---|---|
| `light` | **mặc định** — minh hoạ AI agent tự làm được (ví dụ, bối cảnh, đồ vật, thao tác được nhắc tới) | nên có 2–4 asset `ai_image`/`agent` với `desc` + `anchor_quote` để code chấm đúng ô; không có vẫn hợp lệ |
| `heavy` | câu nói cần **cảnh thật** mới đúng (kết quả thật, màn hình thật, số liệu, case thật) — **không tự bỏ**; `claim_gate` true (R200) | ≥ 1, mỗi asset có `desc` và `anchor_quote`; asset cảnh thật `owner` `user` |
| `none` | CHỈ khi user ghi rõ video đó không B-roll (ghi lời user vào `note`) | `[]` (bắt buộc rỗng) |

Cột HYBRID/talking trong file phân loại chỉ là gợi ý; «talking-head thuần» KHÔNG còn là lý do để chọn `none`.

## 5. `assets` — thứ cần chuẩn bị

| Trường | Ghi gì |
|---|---|
| `desc` | hình cần có, một câu cụ thể (ai làm cũng hiểu) |
| `anchor_quote` | câu/từ **trích đúng lời chuẩn** mà hình phải khớp |
| `kind` | `ai_image` · `ai_video` (Grok qua 9router, chờ cổng R0b) · `screen_rec` (user quay màn hình) · `real_output` (kết quả thật user giao) · `stock_context` (stock có license, **chỉ bối cảnh, không làm bằng chứng** — D3a) · `remotion_card` (thẻ chữ/số dựng bằng code) |
| `owner` | `user` hoặc `agent` |
| `due` | hạn `YYYY-MM-DD`, hoặc `null` khi chưa hẹn |

- Asset minh hoạ: `kind` `ai_image` (hoặc `ai_video` cho một cảnh chính), `owner` `agent`, `desc` tả CẢNH nhìn thấy được, `anchor_quote` chép NGUYÊN một câu có thật trong vo_script (code dùng câu này để chấm ô B-roll).
- `heavy` chỉ khi câu nói cần cảnh thật (kết quả thật, màn hình thật, số liệu); khi đó `claim_gate` true (R200) và ghi asset `owner` `user`.

## 6. `claim_gate` — không đăng trước khi user xác nhận (§13.4)

`true` khi lời có một trong các loại sau; mỗi lý do một dòng trong
`claim_reasons`, kèm câu trích:

- cần test thật (ví dụ so "miễn phí và trả phí");
- cần consent hoặc là bài của học viên / nhóm cộng đồng;
- case phải có thật;
- tin AI thiếu nguồn hoặc ngày;
- số liệu không có nguồn.

Video có `claim_gate` vẫn dựng bình thường; chỉ việc đăng phải chờ user.

## 7. Dòng "gợi ý" có thể sai (Ruling R14)

Mục v3, dòng đạo diễn, dòng phân loại do máy ghép theo tiêu đề + lời, kèm điểm.
Tiêu đề của một gợi ý không cùng chủ đề với lời chuẩn thì gợi ý đó **sai** — bỏ
qua, tự phán đoán từ lời chuẩn, và ghi vào `note` ("gợi ý đạo diễn #18 sai chủ
đề"). "không ghép được" nghĩa là tự phán đoán từ lời chuẩn.

## 8. Lỗi thường gặp của `PREP --check`

| Lỗi in ra | Cách sửa |
|---|---|
| `'…' is a required property` | thiếu khoá — so lại khuôn §2 |
| `… is not one of […]` | giá trị ngoài danh sách (status, broll_class, kind, owner) |
| `status … phải kèm reasons` | thêm lý do cho video không `ok` |
| `claim_gate true phải kèm claim_reasons` | ghi lý do claim, hoặc để `false` |
| `broll_class heavy phải có ít nhất một asset` / `asset của video heavy phải có …` | thêm asset, điền `desc` và `anchor_quote` |
| `broll_class none thì assets phải rỗng` | xoá asset, hoặc đổi `broll_class` |
| `phiếu ghi video […], card giao video […]` | phiếu phải có đúng các video của card |

## 9. Không được làm

- Không sửa `vo_script/`, `batch_manifest.json`, `mapping.csv`, `APPROVALS.md`,
  `PREP-SHEET.md` (script dựng lại từ phiếu).
- Không bịa asset, câu neo hay nguồn số liệu không có trong lời chuẩn.
- Không tạo card, không tự unblock, không chạy `python -c`, không tự viết script.
