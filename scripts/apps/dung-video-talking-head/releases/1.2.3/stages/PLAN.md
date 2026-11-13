# PLAN — chọn trong plan.json

Đây là chỗ phán đoán duy nhất của dây chuyền A-roll: nghe lời, chọn hook,
chọn điểm nhấn, thẻ liệt kê, CTA và kiểm tra cột hero. **Agent chỉ viết một
file: `plan.json`.** Mọi mốc thời gian, frame, cắt cảnh và thẻ phụ đề do code
sinh ra từ file này — không sửa `edit.json`, không viết giây, không đặt số
frame tay.

## 1. Vòng làm việc (tối đa 3 vòng)

1. Chạy stage: chạy đúng lệnh ở dòng NEXT của stage (nó sinh `PLAN-SHEET.md` và `plan.json` nháp).
2. Đọc `PLAN-SHEET.md` — tài liệu **duy nhất** cần đọc.
3. Điền **6 ô `?`** trong `plan.json`. Đồng ý với bản đề xuất thì chép nguyên khối §8 của sheet. PLAN-SHEET có §B ⇒ trong plan.json giữ `"broll"` của §8, viết prompt tiếng Anh cho từng ô theo hướng dẫn §B (8–60 từ, tả cảnh, không chữ/logo). Nhiều ô cùng một sản phẩm ⇒ chép NGUYÊN một cụm mô tả sản phẩm vào prompt mọi ô ấy (tả cả dáng + màu); không tên hãng. Lỗi BROLL_* ⇒ dán đúng phần «Sửa:».
4. Kiểm tra: chạy đúng lệnh ở dòng NEXT (`stage.py PLAN --check --task <id>`). In `ĐẠT` và `RESULT: PASS` là xong card: gọi tool `kanban_complete` đúng như dòng NEXT (summary chép nguyên văn dòng `ĐẠT: …` và dòng `RESULT: PASS`, metadata = JSON dòng `METADATA`). FAIL ⇒ dán đúng dòng `Sửa:` vào `plan.json` rồi chạy lại. **Tối đa 3 vòng.**

**7 việc phải quyết:**
1. Hook: chọn cú mở hoặc để `null`.
2. Điểm nhấn (`emphasis`): video từ 30 giây cần ít nhất 1, hoặc ghi lý do vào `no_emphasis_reason`.
3. Thẻ liệt kê (`steps`): chỉ chọn phương án S sheet ghi «đề xuất» (kèm tiêu đề và nhãn); S «không đề xuất» thì để `null`.
4. CTA (`cta`): chọn phương án kêu gọi hành động hoặc để `null`.
5. Cột HERO (`hero`): thay hero yếu bằng phương án sheet đã liệt kê.
6. Đọc lại mạch chữ: chỗ nào còn gợn ghi vào `flags`.
7. B-roll (`broll`): giữ các ô đề xuất trong `"broll"` (hoặc đổi id theo §B), thay MỌI `"prompt": "?"` bằng prompt tiếng Anh; video không có §B thì để `"broll": []`.

**Chốt dừng lượt 20**: tới lượt thứ 20 mà chưa xong thì chạy `--check` ngay; PASS thì complete, FAIL thì `kanban_block`.

## 2. plan.json

Bản nháp `plan.json` do code tạo mang schema `plan/2` và hash kiểm tra lời `words_sha`.
Agent cần điền 6 ô quyết định (giá trị là **id ứng viên** như `"H1"`, `"K1"`, `"S2"`, `"C1"`, hoặc `null`/mảng rỗng):

- `hook`: id ứng viên hook (vd: `"H1"`), hoặc `null` nếu lời mở không có số hay từ đập.
- `emphasis`: danh sách id ứng viên điểm nhấn (vd: `["K1", "K2"]`), hoặc `[]`.
- `steps`: id ứng viên bảng liệt kê (vd: `"S1"`), hoặc `null`.
- `cta`: id ứng viên kêu gọi hành động (vd: `"C1"`), hoặc `null`.
- `hero`: mảng các cặp chỉ số từ ghi đè hero `[[start, end], ...]`, hoặc `[]`.
- `broll`: danh sách các ô B-roll `[{"id": "B2", "media": "still", "prompt": "...", "v": 1}, ...]`, hoặc `[]`.

Các trường đi kèm:
- `breaks`: danh sách mốc tách thẻ phụ đề `[word_index, ...]`, mặc định `[]`.
- `no_emphasis_reason`: chuỗi giải thích khi video ≥ 30 s nhưng `emphasis` để `[]`.
- `flags`: danh sách ghi chú câu từ còn gợn `["chú thích...", ...]`, mặc định `[]`.
- Gợi ý nhãn có thể sửa: `steps_title`, `steps_labels`, `cta_label`, `cta_keyword`.

## 3. blocks — thẻ phụ đề ba tầng

Hệ thống tự động quy hoạch động (DP) chia thẻ phụ đề theo lời và nhịp ngắt:
- Mỗi block là một thẻ gồm: dòng nhỏ trên (`top`), dòng chữ đập (`hero`), dòng nhỏ dưới (`bottom`).
- `style`: `script` (nghiêng, nền tím), `stomp` (chữ đập in hoa màu đặc), `quote` (stomp kèm ngoặc kép).
- `color`: `warn` (vấn đề, cảnh báo), `gold` (giải pháp, con số, CTA).
- `accent`: từ điểm nhấn màu cyan trong hero.
- Agent không tự cắt thẻ thủ công. Nếu cần ngắt thẻ ở vị trí cụ thể, thêm chỉ số từ vào `breaks`. Khi hero tự động quá dài hoặc ngắt sai ý, điền cặp phạm vi ghi đè vào `hero`.

## 4. hook — cú mở

- Chọn ứng viên hook khi lời mở đầu có con số, thống kê hoặc từ đập mạnh (`20`, `90%`, `3 LỖI`, `SAI RỒI`).
- Chọn id ứng viên `H...` từ `PLAN-SHEET.md` phù hợp nhất với nhịp mở đầu.
- Lời mở không có số hay từ đập mạnh: để `"hook": null`, không gượng ép dựng hook.

## 5. steps — bảng liệt kê

- Dùng khi lời nói liệt kê 3–5 luận điểm/bước nối tiếp nhau.
- Chọn id ứng viên `S...` từ `PLAN-SHEET.md`.
- Có thể tinh chỉnh `steps_title` (in hoa) và `steps_labels` (ngắn gọn, ≤ 26 ký tự mỗi nhãn) ngay trong `plan.json` cho sát nội dung.
- Lời không liệt kê: để `"steps": null`.

## 6. shots — cỡ cảnh (camera 2.5D)

- Code tự động phân bổ cỡ cảnh toàn/cận, trôi góc và nhịp cắt 2–4 giây khớp khoảng ngắt giọng.
- Tự động hạ thấp hoặc đẩy khung hình khi xuất hiện bảng liệt kê hoặc mặt người dẫn.
- Agent không chỉnh sửa shot hay camera trong `plan.json`.

## 7. cta — kêu gọi hành động

- Chỉ chọn khi lời nói thực sự có kêu gọi hành động ở cuối video.
- Chọn id ứng viên `C...` từ `PLAN-SHEET.md`.
- Có thể chỉnh `cta_label` (≤ 14 ký tự, vd: `"Bình luận"`) và `cta_keyword` (≤ 16 ký tự, từ khoá cần gõ).
- Lời không có kêu gọi hành động: để `"cta": null`. Tuyệt đối không bịa lời hứa hoặc quà tặng.

## 8. Bảng mã lỗi

Khi lệnh `--check` báo lỗi (hoặc operator mở lại card PLAN kèm mã lỗi từ BUILD), đối chiếu mã để sửa `plan.json`. Dòng lỗi nào có `Sửa:` thì dán nguyên mảnh đó vào `plan.json`:

| Mã | Nghĩa | Sửa ô nào trong `plan.json` |
|---|---|---|
| `PLAN_JSON` | Sai định dạng JSON, sai schema hoặc thiếu trường | Khôi phục đúng cấu trúc JSON và các khoá chuẩn |
| `PLAN_UNDECIDED` | Còn ô mang dấu hỏi `?` chưa quyết định | Điền id ứng viên hợp lệ hoặc `null`/`[]` cho các ô được nêu |
| `PLAN_STALE` | `words_sha` không khớp `words.json` hiện tại (INTAKE đã chạy lại sau khi bạn điền) | Chạy lại lệnh đầu tiên ở dòng NEXT (không có `--check`). **Lệnh này ghi đè `plan.json` bằng nháp mới** — đọc lại `PLAN-SHEET.md` rồi điền lại 6 ô; id ứng viên cũ có thể đã đổi |
| `UNKNOWN_ID` | Id ứng viên không tồn tại trong danh sách đề xuất | Sửa lại đúng id có trong `PLAN-SHEET.md` tại ô báo lỗi |
| `HERO_RANGE` | Phạm vi ghi đè hero không hợp lệ (ngoài 2–5 từ hoặc vắt qua 2 thẻ) | Chỉnh lại cặp `[start, end]` trong `hero` đúng 2–5 từ trong 1 thẻ |
| `NO_EMPHASIS` | Video ≥ 30 giây nhưng thiếu điểm nhấn | Chọn ít nhất 1 id trong `emphasis` hoặc điền `no_emphasis_reason` |
| `STRAY_SCRIPT` | Có file script lạ xuất hiện trong thư mục làm việc | Xoá toàn bộ file script thừa do agent tự tạo |
| `FACE_ROOM` | Chữ phụ đề che miệng hoặc mắt người dẫn — mã này **do BUILD báo**, operator mở lại card PLAN kèm nguyên dòng lỗi | Dán gợi ý ở dòng `Sửa:` vào `hero` (nối thêm phần tử — `(một hàng)`: hero đó dựng một hàng co cỡ) hoặc `breaks`, rồi chạy `--check`; gợi ý đã được BUILD chạy thử qua `--check` |

## 9. Không được làm

- Không sửa `edit.json` (VERIFY ghép lại sẽ bắt `PLAN_DRIFT`).
- Không sửa `words.json`, `pauses.json`, code hệ thống hay template.
- Không tự viết script nháp, không dùng `python -c` hay công cụ ngoài.
- Không bịa thêm thông tin ngoài lời thoại thực tế của video.

## Phụ lục: Schema `edit/1.1` (chỉ để đọc)

Schema `edit.json` do hệ thống tự sinh từ `plan.json`, chỉ dùng để tham khảo:

```jsonc
{
  "schema": "edit/1.1",
  "hook":  { "text": "20", "color": "warn", "hit_word": 7 },      // hoặc null
  "blocks": [
    { "id": "b02", "top": [5, 7], "hero": [7, 9], "bottom": null,
      "style": "stomp", "color": "warn", "accent": null, "display": {}, "reveal": false }
  ],
  "steps": { "title": "5 TÀI SẢN TỪ 1 ẢNH",
             "items": [ { "range": [28, 32], "label": "Hero cho website" } ] },   // hoặc null
  "shots": [ { "cut_at_word": 21, "s0": 1.18, "s1": 1.22, "x": 0.0, "y": -0.06 } ],
  "cta":   { "range": [147, 162], "label": "Bình luận", "keyword": "5 TÀI SẢN" }  // hoặc null
}
```
