# Tài liệu kế hoạch cho hồ sơ minimal-edu (plan_doc → minimal_plan.json)

Dùng khi dựng bằng mẫu `assets/motion-fx/build_spec_minimal.py` (hồ sơ minimal-edu). Người duyệt chọn A / B / C cho từng nhịp trong một file HTML offline;
bộ chuyển đổi biến lựa chọn thành `W/minimal_plan.json` mà mẫu tự nạp (GROUPS / SCENE_GFX / CTA_WORD / PAIN). `W` = thư mục `work/` của phiên bản.

## 1. Quy trình (Claude làm từng bước)
1. `build_spec_q.py` (KEY_SPECS trống cũng được) → ra `W/words_tl.json`.
2. Dựng bản nháp theo từ khoá để có danh sách nhịp:
   `plan_doc.py build W --manifest <V>/00_storyboard_manifest.json --out W/edit_plan.html` (ghi thêm `W/plan_draft.json`).
3. **Bước theo NGHĨA (Claude, xem §2)**: đọc `plan_draft.json` + kịch bản, viết `W/beats_meaning.json`.
4. Dựng lại có nghĩa: `plan_doc.py build W --manifest … --meaning W/beats_meaning.json --out W/edit_plan.html`. Badge «Gợi ý» giờ ghi lý do theo nghĩa.
5. Người dùng mở HTML, chọn từng nhịp, bấm «Xuất JSON» (hoặc «Copy Plan»); Claude chạy `plan_doc.py export <file tải về> W` → `W/plan_export.json`.
6. `plan_to_minimal.py W [--cta "Bất Động Sản"]` → `W/minimal_plan.json` + `W/minimal_plan_review.json`; đọc bảng tóm tắt in ra.
7. Chạy `build_spec_minimal.py` như thường: có `minimal_plan.json` thì mẫu dùng nó, không thì dùng khối `# EDIT`.

## 2. beats_meaning.json — bước làm cho gợi ý «theo nghĩa» (D16)
Từ khoá chỉ đoán được vài mẫu (số, tên riêng). Hiểu một câu đang làm việc gì thì cần đọc: vì vậy chính Claude (agent đọc kịch bản) gán nhãn.
Với MỖI nhịp trong `plan_draft.json` (đánh số từ 1), đọc `text` rồi nghĩ: câu này đang làm gì cho người xem? Ghi:
```json
[{"beat": 1, "label": "intro_new_concept", "why": "giới thiệu ý chính của video"},
 {"beat": 2, "label": "describe_object",  "why": "tả bãi đất trống người xem phải hình dung"}]
```
| nhãn | khi nào | gợi ý |
|---|---|---|
| `intro_new_concept` | giới thiệu khái niệm / ý mới | A — giữ mặt + cụm chữ |
| `describe_person` | tả người | C polaroid |
| `describe_object` | tả vật / nơi chốn | C illus_mid |
| `number_data` | số liệu, so sánh số | C graph |
| `process_steps` | các bước / hành trình | C path_illus (zigzag) |
| `emotion` | cảm xúc, nhấn giọng | B — mặt cận + chữ serif |
| `conclusion` | câu chốt, trích dẫn đáng nhớ | C quote_paper |
| `story` | kể chuyện, bối cảnh | C painting |
Quy tắc: `why` bắt buộc viết bằng lời của bạn (1 câu); đừng gán theo từ khoá (có chữ «triệu» chưa chắc là số liệu). Nhịp bỏ trống → quay về từ khoá.
Nhãn lạ hoặc số nhịp ngoài phạm vi → `build` dừng và nói rõ. Gợi ý chỉ là badge: KHÔNG tự chọn thay người dùng.

## 3. Ba phương án mỗi nhịp
- **A** — giữ mặt + cụm chữ nhỏ, từ lớn **sans** (`*`); từ lớn mặc định lấy cuối nhịp, sửa được.
- **B** — cụm chữ khác kiểu: từ lớn **serif** (`~`), cụm nhấn khác (đoạn dài nhất), có thể thêm chữ viết tay.
- **C** — cắt sang cảnh đồ hoạ: ô thả xuống chọn kiểu + trường điền sẵn (từ bắt đầu, số cảnh, giây, dòng chữ, đường dẫn ảnh):
  polaroid · arrow · graph · quote · cutaway · painting · path_text · path_illus (zigzag / rise) · illus_mid · illus_side (left / right) ·
  quote_paper (white / blue). Cảnh manifest đã là B-roll thì C = B-roll có sẵn (không có ô kiểu). Ảnh minh hoạ do người dùng chỉ đường dẫn.

## 4. SEEN IN THE REELS (xem mẫu thật)
Có thư viện hiệu ứng (`OPA_LIBRARY_DIR` hoặc `~/opa-software/opa-video-studio-library`, định dạng ở `kb-effect-library.md`; `--library <thư mục>` để chỉ rõ)
thì mỗi phương án hiện tối đa 3 ảnh thật từ reel, khớp theo kind và nguyên tắc của entry (A: caption · B: text_motion · C: theo kiểu đang chọn).
Ảnh là thumbnail JPEG ≤ 30 KB nhúng base64 (HTML vẫn một file, offline). Không có thư viện → bỏ phần này, mọi thứ khác chạy như cũ.

## 5. plan_to_minimal.py — luật chuyển đổi
- **groups**: mỗi nhịp thành các cụm `nhỏ | nhỏ | *từ lớn` phủ HẾT lời (mẫu khớp tuần tự; mỗi từ trong words_tl là một TIẾNG). Cụm 4–7 tiếng, đóng ở dấu câu / trước từ phụ.
  Từ lớn = cụm người dùng đã đánh dấu ở A / B (chữ gốc, `*` sans cho A, `~` serif cho B); cụm còn lại hoặc nhịp chưa chọn → đoạn nội dung dài nhất ≤ 3 tiếng.
- Cảnh có C kiểu `quote` / `quote_paper` → một `None` cho cả cảnh (thẻ toàn chữ do SCENE_GFX dựng), không sinh cụm.
- **scene_gfx**: `[kind, …trường theo thứ tự trong plan_doc.GFX_KINDS]`, sắp theo giờ. Ảnh không tồn tại → cảnh báo (mẫu sẽ dừng nếu không sửa).
- **cta_word**: `--cta`, hoặc nhịp có ghi chú chứa «CTA»; phải là từ lớn của một cụm (trả đúng hoa / thường trong groups), không thì cảnh báo.
- **pain**: sao từ `W/pain.json`.
- `minimal_plan_review.json` = các từ lớn TỰ CHỌN. Tiếng Việt tách theo tiếng nên có thể cắt giữa từ ghép («*sản tiền tỷ»): Claude đọc danh sách,
  sửa chuỗi trong `minimal_plan.json` (hoặc nhờ người dùng đánh dấu từ lớn ở A / B rồi chạy lại) trước khi dựng.
