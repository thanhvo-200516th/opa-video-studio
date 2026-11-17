# kb-effect-library — thư viện hiệu ứng có mẫu xem được (still / strip / clip / notes)

Mục đích: mỗi hiệu ứng của một phong cách có MỘT thư mục mẫu để NHÌN và ĐỌC số đo trước khi dựng lại, thay vì chỉ có tên hàm trong code.
Học từ cách tác giả "Joseph | Video Editing" dạy Claude (thư mục `References/225 Animations/V01-A01 …`, mỗi mục 4 tệp). Thư viện của họ không công khai;
thư viện này tự dựng bằng `scripts/style_analysis/lib_extract.py` từ video mẫu đã phân tích.

## 1. Chỗ để và luật
- Gốc: env `OPA_LIBRARY_DIR`, mặc định `~/opa-software/opa-video-studio-library` — NGOÀI repo skill. Clip mẫu là của bên thứ ba: KHÔNG commit, không đóng gói vào skill, không đăng lại.
- `<gốc>/<style>/index.json` = `{"style", "entries": [...]}`; mỗi mục có thư mục `<id>/` gồm `still.png` (khung nét nhất), `strip.jpg` (cứ 2 khung một ô, có nhãn `fN`),
  `clip.mp4` (≤ 3 s, không tiếng), `entry.json` (đúng đối tượng trong index), `notes.md` (tiếng Việt: chuyện gì xảy ra, số đo, dựng lại ở đâu).
- `id` dạng `Vxx-Ayy` (xx = video nguồn, yy = số thứ tự hiệu ứng). `kind` ∈ caption · broll · painting · line_text · line_illus · quote · illus_mid · illus_side · object · graph · transition · text_motion.
  `principle` 1–10 (10 nguyên tắc của phong cách) hoặc null (chuyển cảnh / hiệu ứng ngoài 10 nguyên tắc). `measures` là số tự do: khung, ms, px, bbox chuyển động, màu chủ đạo.

## 2. Cách dùng khi dựng
1. Từ nhịp lời (kế hoạch C3 / `plan_doc.py`), chọn nguyên tắc rồi mở `index.json`, lọc theo `principle` hoặc `kind`.
2. MỞ `strip.jpg` bằng công cụ xem ảnh (đừng chỉ đọc notes): thấy chữ vào ở khung nào, đường vẽ mấy khung, cắt ở đâu.
3. Đọc `notes.md` → dòng "Dựng lại trên FilmCraft" chỉ tới hàm / `SCENE_GFX` kind (polaroid, arrow, graph, quote, cutaway, painting, path_text, path_illus, illus_mid, illus_side, quote_paper — kind nào chưa có trong `build_spec_minimal.py` là kind đang bổ sung ở brief B).
4. Số đo là THAM CHIẾU (đo trên bản repost 1080×1920, clip thật chỉ rộng ≈ 330 px nên sai số cỡ chữ ±20 %): dựng rồi dùng `fc_fast_qa.py --frames-dir` so strip của mình với strip mẫu.

## 3. Lệnh (`scripts/style_analysis/lib_extract.py`, ffmpeg theo env `FFMPEG` hoặc PATH)
```
lib_extract.py segments <video> --out D [--transcript F.json] [--crop X,Y,W,H] [--threshold 10]
    # bóc lời (faster-whisper, GPU rơi về CPU int8, hoặc dùng transcript có sẵn) + dò điểm cắt ffmpeg scdet → D/segments.json, segments.md (đoạn đề xuất kèm lời)
lib_extract.py entry <video> --id V01-A03 --t S E --kind K --title "…" --root R --style S [--principle N] [--crop X,Y,W,H]
                     [--still-at S] [--notes TEXT | --notes-file F] [--rebuild TEXT] [--url U] [--author A]
    # ghi still / strip / clip / entry.json / notes.md (số đo tự động: khung, ms, bbox chuyển động bằng chênh khung, màu chủ đạo) + cập nhật index.json
lib_extract.py index --root R --style S      # dựng lại index từ entry.json, kiểm hợp lệ (thiếu tệp, kind sai, clip > 3 s hoặc còn tiếng); mã thoát ≠ 0 nếu lỗi
```
`--crop` cần khi mẫu nằm trong khung bọc (bản TikTok: clip 9:16 trong thẻ ngang; màn hình 16:9 là `20,402,1040,586`). Mốc `--t E` lấy ĐÚNG khung đầu cảnh sau thì lùi 1 khung (≈ 0,034 s) để clip không lẫn cảnh kế.

## 4. Bộ mẫu đã dựng: `minimal-edu` (29 mục, nguồn: video "How to Edit VIRAL Talking Head Videos Using ONLY Claude!", Joseph | Video Editing, bản repost TikTok @haihoang_airaviec 5:44)
Mốc `t` là giây trong `tiktok-haihoang/video.mp4`. Phần thành phẩm (284–344 s) là clip Arthur Brooks 9:16 thật; phần còn lại là màn hình hướng dẫn (có mockup dựng lại).
Phân bố: nguyên tắc 1 (×5) 2 (×2) 3 (×5) 4 (×2) 5 (×1) 6 (×1) 7 (×1) 8 (×1) 9 (×3) 10 (×3), cộng 5 mục không thuộc nguyên tắc (chuyển cảnh / thẻ chương).

| id | NT | kind | t (s) | hiệu ứng |
|---|---|---|---|---|
| V01-A01 | 1 | `caption` | 284.43–285.50 | Phụ đề mặt: 'psychologically' serif italic blur-in dưới 'career patterns,' |
| V01-A02 | 1 | `caption` | 302.10–303.20 | Mặt + 'a lot of / people / who are watching / this show': sandwich nhỏ-lớn-nhỏ |
| V01-A03 | 1 | `caption` | 307.80–309.00 | Mặt cận chặt: 'The first turn is' nhỏ + 'hardest.' blur-in 4 khung |
| V01-A04 | 1 | `text_motion` | 311.17–312.30 | 'brutal.' serif italic đậm blur-in 4–5 khung (từ cảm xúc) |
| V01-A05 | 2 | `broll` | 305.23–306.47 | B-roll hành lang đen trắng: 'What they need is to take' từng từ + 'their career' blur-in |
| V01-A06 | 2 | `broll` | 306.50–307.77 | B-roll 'down to / the studs / and start / again': hai từ nhỏ cách nhau đúng bề ngang từ lớn |
| V01-A07 | 3 | `painting` | 295.57–296.43 | Tranh phụ nữ khâu: ảnh vào mờ ngang 5 khung, 'barista' blur-in 6 khung |
| V01-A08 | 3 | `painting` | 296.47–298.13 | Tranh 'Nụ hôn' (Hayez): chữ ở vùng trống phía trên phải, 'San Diego.' serif italic |
| V01-A09 | 3 | `transition` | 296.40–296.87 | Tranh → tranh: nhoè ngang ≈ 13 khung |
| V01-A10 | 3 | `painting` | 300.47–302.07 | Tranh 'dad' + mũi tên cong + hộp xanh '42 years' wipe |
| V01-A11 | 4 | `line_text` | 314.97–317.63 | Đường xanh dày bị chữ 'your calling' cắt ngang, whip-pan dọc đường |
| V01-A12 | 4 | `transition` | 316.10–316.67 | Whip-pan dọc đường: nội dung chạy sang trái, nhoè ngang cực đại giữa chừng (≈ 9 khung) |
| V01-A13 | 10 | `graph` | 288.63–291.50 | Đồ thị bậc thang: chấm xanh leo, camera trượt lên theo chấm, mũi tên cong vẽ tới 'careers.' |
| V01-A14 | 10 | `graph` | 298.97–300.43 | Đường ngang + chấm xanh trượt phải = 'slow and steady' |
| V01-A15 | 10 | `graph` | 285.53–286.17 | Trục L trắng mảnh + chấm xanh vẽ ≈ 17 khung (giới thiệu kiểu mới bằng đồ hoạ) |
| V01-A16 | 7 | `illus_mid` | 303.23–305.20 | Xoắn ốc vẽ từ tâm ra: 23 khung, ≈ 4,2 vòng, ease-out, quầng sáng; đứng yên 1,2 s |
| V01-A17 | 6 | `quote` | 313.40–314.93 | Thẻ trích dẫn gradient xanh + dấu ngoặc kép: 'entrepreneurial' blur-in, 'life' serif italic |
| V01-A18 | 9 | `object` | 309.03–311.13 | Polaroid kèn French horn → nhà khoa học: pop-in 1 khung, lắng 6–7 khung, nhoè toàn khung 2 khung để bố cục lại |
| V01-A19 | 9 | `object` | 338.40–340.43 | Polaroid 'Going back and getting a PhD': chữ từng từ phía trên ảnh, 'PhD' sans đậm xanh |
| V01-A20 | 8 | `illus_side` | 343.47–343.97 | Chân dung duotone xanh/trắng + vòng cung trắng đang vẽ quanh đầu |
| V01-A21 | 1 | `text_motion` | 341.63–343.43 | Sandwich lặp lại trên mặt: 'Second turn, easier.' / 'I'm on my fourth turn right now.' |
| V01-A22 | 9 | `transition` | 312.25–312.62 | Đoạn chèn 6 khung: cắt vào 'Going' rồi cắt ra ở chỗ ngắt lời |
| V01-A23 | 3 | `transition` | 300.40–300.77 | Vào cảnh bằng blur-focus: cắt cứng vào khung nhoè rồi nét trong 4 khung |
| V01-A24 | – | `transition` | 0.90–3.87 | Hook: ba thẻ dọc đứng yên, mỗi thẻ đổi nội dung bằng cắt cứng 1 khung lệch nhịp |
| V01-A25 | – | `transition` | 130.60–131.37 | Camera tilt xuống: lưới trượt lên với motion blur, bảng mới trượt vào từ dưới (≈ 18 khung) |
| V01-A26 | – | `transition` | 99.60–100.77 | Cắt cứng sang nền tối rồi cửa sổ trồi lên blur→nét (≈ 15 khung, ease-out) |
| V01-A27 | – | `transition` | 235.40–236.07 | Nhoè Gauss mạnh ≈ 4–5 khung rồi tối dần sang cảnh khác (≈ 8 khung) |
| V01-A28 | – | `text_motion` | 4.10–6.97 | Thẻ chương + thẻ nguyên tắc kích hoạt lần lượt (nứt kính, ≈ 1 s/thẻ), hàng thẻ cuộn trái nhanh dần |
| V01-A29 | 5 | `line_illus` | 95.00–97.97 | Figma board: nhóm 'Line + Illustrations' (nguyên tắc 5) trong bảng mổ xẻ — chỉ có thumbnail |

## 5. Giới hạn đã biết
- Nguyên tắc 5 (đường + minh hoạ) chỉ có V01-A29: bản TikTok không chiếu cảnh này ở cỡ lớn, mẫu là thumbnail Figma; cần dựng lại từ định nghĩa (a)(b)(c) trong `kb-video-style-trainer.md` rồi bổ sung mẫu khi có nguồn tốt hơn.
- V01-A20 (chân dung duotone + vòng cung): video TikTok dừng giữa câu nên chỉ thấy 0,5 s đầu; chưa chắc thuộc nguyên tắc 7 hay 8.
- Các số "khung" trong notes lấy từ phân tích 9 tác tử (1/30 s) và đã đối chiếu lại bằng strip (xem từng khung) ở phần lớn các mục; chỗ lệch được ghi trong notes (vd V01-A27). Thẻ clip trôi ngang ±20 px nên strip có lề tối mỏng.
- Không phân tích âm thanh: SFX (click chữ, highlighter đồ thị, whoosh chuyển cảnh, 74 SFX/57 s) xem `audit_sfx.py` / luật F, không có trong thư viện.
- Thêm mẫu mới: `segments` để chọn đoạn → xem strip → `entry` → `index`; mỗi mục phải có `notes.md` ghi số đo và dòng dựng lại. Kịch bản tạo bộ này nằm ở `<gốc>/minimal-edu/seed_manifest.json` (id, mốc, kind).
