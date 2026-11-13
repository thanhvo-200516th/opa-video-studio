# Vòng soát và follow-up cho phim 3D

**Follow-up** là đoạn yêu cầu sửa, viết sau mỗi lần xem (ảnh tĩnh, bản ghép, số đo). Ở ca mẫu, Claude tự xem và tự viết follow-up; Minh chỉ duyệt ở các cổng. Mọi vòng ghi vào `film3d/films/<id>/FOLLOWUPS.md`.

Nguyên tắc: **đo trước, xem ảnh sau.** Phần lớn lỗi của phim 3D (cắt mép, lệch màu, chữ đè nền sáng, đứng hình, lệch cú cắt) đo được bằng số. Đo trước thì bớt vòng sửa và bớt token đọc ảnh. Lệnh đo: `qa-checklist.md`.

Ví dụ đủ: `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/OPA-Motion-graphic-mascot/film3d/films/thu-mon/FOLLOWUPS.md`.

## 1. Nhịp vòng soát

| Lúc | Đo trước | Rồi xem | Ai quyết |
|---|---|---|---|
| G1 thử look | `qa.py shape`; `qa.py brand` trên ảnh tĩnh; `qa.py video` trên đoạn 4 s | một tờ so sánh các kiểu look | Minh trả lời 3 câu có/không |
| G2 bản ghép | màu, cắt mép, chữ, khung đứng, cú cắt | bản ghép có giờ phim + tờ duyệt một trang | Minh duyệt |
| Sau góp ý của Minh | phép đo liên quan | ảnh trước/sau cùng góc, phóng 3× chỗ được chê | Minh |
| Minh chê bản đã giao | đo lại đúng thứ bị chê trên bản cũ (ca mẫu: độ chuyển động mỗi khung, độ phủ chữ) | tờ đề xuất một trang: ảnh trước/sau + biểu đồ nhịp (mục 3) | Minh duyệt hướng, rồi mới dựng lại |
| G4 tự soát | đủ bộ đo trên bản ghép | 24 khung (4 tờ × 6 ô) + dải 5 khung quanh mọi nhịp chạm; mọi khung ở đoạn vật dồn dập | Claude |
| Sau mỗi lần sửa | đúng phép đo đã trượt | 12 khung ở chỗ đã sửa | Claude |
| G6 âm | độ to, true peak, lệch tiếng, loa điện thoại (lane A) | sau mix đầu; sau khi solo từng bus; bộ A/B (ca mẫu bản 2: âm tổng hợp với âm thư viện) | Minh nghe |
| G8 | đủ 8 nấc, đo lại sau mỗi đợt sửa | agent mới rà chéo, chấm điểm, xếp mức lỗi; vòng 2 cùng người rà | Minh, Hùng |

**Vì sao cần rà chéo dù đã tự soát:**
- Bản 1: agent rà chéo bắt được một lỗi bắt buộc (bóng lơ lửng 5,13–5,25 s). Dải 5 khung của G4 đã chứa lỗi này, nhưng người tự soát đọc nhầm thành lỗi xuyên vật. Người rà chấm 4 mục: không nhàm 8,5 · thương hiệu 9 · chữ 8,5 · rõ chuyện 7, và tìm thêm 7 lỗi "nên sửa". Mục thấp nhất (rõ chuyện) là chỗ số đo không bắt được.
- Bản 2: vòng 1 bắt lỗi bắt buộc nằm giữa hai nhịp (tin chồng nhau, cắm vào vai khe lúc Bò nhảy, 6,10–7,12 s), nên dải 5 khung không chứa. Vòng 1 còn bắt chữ giật do bước ghép, có từ bản 1 mà chưa ai thấy. Vòng 2 cùng người rà: "phần hình giao được".

- **Tờ khung** (contact sheet) là một ảnh ghép nhiều khung nhỏ. Xem tờ 6 ô thay cho 6 ảnh rời tốn ít token ảnh hơn khoảng 4 lần.
- **Chọn khung:** rải đều theo thời gian, cộng mọi nhịp chạm trong `EVENTS` (hứng, đáp, thẻ bay, phì, cú cắt).
- **Dải 5 khung** là các khung f−2 … f+2 quanh một nhịp f. Cắt từ bản 3D FFV1 (không mất chất lượng), không cắt từ MP4 đã nén.
- Chỗ nghi ngờ: phóng to ở độ phân giải gốc (ca mẫu: `bong-qua-khe-7.70s-x3.png`). Chân mascot và bóng tiếp xúc: `tools/film3d/crop_base.py`.
- Mỗi vòng tối đa khoảng 6 lỗi. Thứ tự: khung cắt và màu mascot trước, va chạm sau, câu chuyện cuối.
- Muốn xem nhanh một chỗ đã sửa: job `frames` vài khung (vài giây). Đo màu và chống nhàm thì luôn trên bản đủ, chất lượng cuối.
- Gửi Minh bản có giờ phim ở góc (`render.py compose ... --timecode`), để Minh chỉ đúng giây.

## 2. Mẫu một vòng follow-up

```text
Vòng {n} · sau {bản ghép G2 | tờ khung G4 | số đo | góp ý của Minh ngày ...}
Đã ổn, khóa lại: {những gì không được đụng tới}.
Lỗi:
{k}. [{giây hoặc khung}] Thấy: {mô tả, kèm tên ảnh hoặc số đo}.
     Sửa: {bằng số: mét, độ, px, khung; tên hằng trong code}.
     Đạt khi: {lệnh đo + ngưỡng}; xem lại {ảnh nào}.
```

Trong `FOLLOWUPS.md`, ghi thành bảng `# | Lỗi | Bằng chứng | Sửa | Kiểm lại`, kèm hai mục:
- **Đã soát, không lỗi**: để người rà chéo khỏi soát lại.
- **Để ngỏ, có lý do**: chỗ trông như lỗi nhưng cố ý (ví dụ cận cắt thân mascot đã được duyệt ở G2).

Ví dụ, lỗi 7 của ca mẫu viết theo mẫu:

```text
7. [3,15–3,35 s, máy nhìn xuyên lòng O] Thấy: ngọn sừng cách mép trên 0–42 px, khung 3,25 s ra ngoài
   khung (qa.py boxes).
   Sửa: máy ở khóa 3,25 s lùi 0,62 → 0,70 m.
   Đạt khi: qa.py boxes --allow 6.55:7.65,12.30:12.95 báo pass; ngọn sừng ≥ 24 px ở mọi khung.
```

## 3. Đổi lời chê thường thành yêu cầu đo được

Minh chê bằng lời thường. Đổi sang dạng trên, đọc lại cho Minh, rồi mới sửa. Ví dụ góp ý của Minh ở G2 ca mẫu:

| Minh nói | Đổi thành |
|---|---|
| "Góc chưa 3D" | Thành bên một màu phẳng → look C2: thành bên nhận sáng theo đèn trong không gian vật, cạnh vát bo 0,08t có vệt sáng |
| "Răng cưa" | Ranh màu khấc theo mặt lưới → trọng số cạnh vát tính theo vị trí chiều sâu; so ảnh phóng 3× trước/sau |
| "Bóng chưa đẹp" | Bóng tiếp xúc nhuộm xanh dưới chân; đèn chính có diện tích (lệch 7° mỗi mẫu) cho bóng mềm |
| "Bố cục chưa cân" | Điện thoại giữa, sổ trái, bảng CRM phải; vật không che chân mascot |

Gửi lại một tờ "trước / bây giờ" cùng góc xoay (ca mẫu: 35°), có ảnh phóng 3× đúng chỗ bị chê.

**Khi Minh chê bản đã giao,** làm file đề xuất trước khi đụng code (ca mẫu: `film3d/films/thu-mon/DE-XUAT-V2.md`):
1. Chép nguyên văn lời chê.
2. Mỗi ý một dòng: Minh nói | soi lại thấy (bằng chứng: giây, ảnh, số đo) | sửa ở bản mới | đạt khi.
3. Kịch bản bản mới theo giây, chỉ dùng lời đã duyệt.
4. Ghi rõ giữ nguyên gì (ca mẫu: hình Bò, tổng 21 s, end card, cú cắt 3D → 2D, âm sắc).
5. Tờ một trang: ảnh trước/sau + biểu đồ nhịp. Chờ Minh duyệt hướng.

Bảng của ca mẫu (Minh chê bản 1 ngày 19/10):

| Minh nói | Soi lại thấy | Sửa ở bản 2 | Đạt khi |
|---|---|---|---|
| "Biểu tượng tin nhắn vẫn bị lỗi" | Bong bóng trắng trước màn hình trắng gần như vô hình; bóng bật ra đè vạch ô tin; khối trắng viền dày không ra tin nhắn | Đúng biểu tượng tin nhắn V2 (vỏ bo, đuôi, 2 vạch chữ), #003C99, hứng xong chuyển #0068FF; cột tin cũ màu nhạt | không khung nào bóng nằm trên nền cùng màu |
| "Background thì đen không đồng nhất" | Phòng tối có đèn: tường, bàn, sàn ba mảng tối khác nhau, có vệt sáng | Nền liền một màu như V2: đêm #003C99, sáng trắng | nền ngoài đồ vật lệch ≤ 2 mức |
| "Hiệu ứng thì lúc nhanh lúc chậm" | Độ chuyển động mỗi khung: lúc có chữ 0,3–0,7, lúc hứng 3–16, cú lia sang CRM 46 | Một nhịp đều 120 BPM, mọi cú hứng đúng phách; một đường máy; bỏ lia gấp, xoay 180°, nhịp khựng | ô động nhất gấp ô lặng nhất ít lần (bản 2: 4,8; bản 1: 56) |
| "Text thì không dàn trải ... khó hiểu" | Chữ chỉ hiện 6,2 / 16 s; 8 s hứng bóng không có chữ nào | Chữ chạy suốt phim, mỗi nhịp một câu, lời V2 đã duyệt | chữ phủ ≥ 65 %, trống ≤ 0,6 s (bản 2: 80 %, 0,52 s) |
| "Xem không đọng lại gì" | Chưa có câu chốt; ý chính chỉ nằm trên nút end card | Câu chốt V2: "Bỏ sót khách" bị gạch đúng cú hứng cao trào → "Không bỏ sót khách" | người xem nhắc lại được một câu |

Bài học: đề xuất bản 2 hứa "độ chuyển động mỗi 0,5 s trong dải 1,5–8", đặt theo thước của phòng có đèn. Nền phẳng làm số nhỏ đi khoảng 10 lần, nên dải đó không đạt theo nghĩa đen dù phim đã đều, và phải giải thích lại với Minh. Đặt ngưỡng sau khi dựng thử vài giây trên đúng kiểu nền, hoặc dùng tỉ số không phụ thuộc nền (ô động nhất / ô lặng nhất).

## 4. Bệnh → thuốc

Rút từ `FOLLOWUPS.md` (bản 1 và bản 2), `g1-thu-look.md` và bài học của ca mẫu. Cột "Đo" là cách biết đã khỏi.

### Màu và look

| Bệnh | Thuốc | Đo |
|---|---|---|
| Mặt trước mascot tối đi khi xoay (đèn đặt cố định trong cảnh: lệch 1,36 / 2,97 / 5,41 ở 0° / 20° / 35°) | Bỏ đèn cố định. Dùng kiểu C/C2 (mặt trước tô phẳng) hoặc B (đèn bám theo mascot) | `qa.py brand` ở 0°, 20°, 35° với cùng một bộ đèn |
| Mặt trước lệch sang lơ hay tím | Không tone map ACES; vật liệu không phản xạ bóng; phơi sáng (EXPO) tính bằng công thức từ cường độ đèn, không đoán | trung vị ΔE2000 ≤ 2 |
| Vật không chịu đèn (màn hình, bong bóng, hạt, vùng tràn xanh) ra sai màu token | Nhân màu với `INV_EXPO` (= 1/EXPO) trước khi vẽ | soi màu điểm ảnh trên khung |
| Vòng đặt màu chung ghi đè màu riêng (G1: hạt thở mất màu xanh) | Vòng chung chỉ cho vật trắng; vật có màu riêng đặt màu một lần lúc dựng | xem khung có hạt |
| "Góc chưa 3D": thành bên một màu phẳng | Look C2: thành bên đi từ #003C99 tới gần #0068FF theo đèn; vệt sáng dọc cạnh vát | ảnh 35° trước/sau |
| Răng cưa giả, khấc ở ranh mặt trước và thành bên | Trọng số cạnh vát tính theo khoảng cách chiều sâu (0 trên mặt, 1 ở thành bên), không theo pháp tuyến từng mặt nhỏ; cạnh vát 6 đoạn, pháp tuyến mượt | ảnh phóng 3× |
| Mascot trắng mất hình trước màn hình trắng | Luật đêm: mascot xanh trước nền sáng; mascot trắng chỉ trên nền xanh hoặc tối | `ringLuma` của `qa.py brand` hoặc `qa.py video` |
| Mascot trắng có thành bên xám #D1D1D1 (kiểu B) | Kiểu C/C2: thành bên #E6F0FF | `qa.py brand --color white` |
| Bóng xám hay đen | Bóng tiếp xúc nhuộm xanh; đèn chính có diện tích cho bóng mềm | xem chân mascot (`crop_base.py`) |
| Ban đêm mặt bàn trắng xóa (đèn màn hình cường độ 4) | Hạ cường độ đèn màn hình còn 1,0 | xem khung đêm |
| Nền tối loang, không đồng nhất (phòng có đèn: tường, bàn, sàn ba mảng tối, có vệt sáng) | Nền phẳng như V2: bàn, tường, sàn một màu không chịu đèn (`world.bg = 'flat'`) | nền ngoài đồ vật lệch ≤ 2 mức |
| Chuyển nền đêm → ngày ra xám đục giữa chừng | Trộn màu nền trong sRGB như V2 (trộn mã sRGB), không trộn trong ánh sáng tuyến tính | tờ khung mỗi 0,25 s qua rạng sáng |
| Vật cùng màu nền tan mất (sổ #003C99 trên nền đêm #003C99) | Đổi vật sang màu token khác (#0068FF) | tờ khung đêm |
| Một nét đen duy nhất trên nền sáng hút mắt, cắt ngang chữ (viền điện thoại) | Thân máy trắng | tờ khung ban ngày |
| Chấm đen ở góc bảng bo tròn | Canvas của bảng tô trắng cả góc ngoài vùng bo | ảnh phóng góc bảng |

### Hình và khung cắt

| Bệnh | Thuốc | Đo |
|---|---|---|
| Ngọn sừng sát hay ra khỏi mép khung ở cú cận | Lùi máy (ca mẫu: 0,62 → 0,70 m ở khóa 3,25 s) | `qa.py boxes`: ngọn sừng ≥ 24 px |
| Thân mascot ra khỏi khung | Cố ý: ghi khoảng giây vào storyboard và `--allow`. Không cố ý: lùi máy | `qa.py boxes` |
| Dải vật sáng lấp ló ở mép khung (ca mẫu: bảng CRM 59 px ở 0,3–2,0 s) | Dời vật ra xa (`SET.crm.x` 0,66 → 0,73). Mọi đích bay, cú lia tính theo hằng bố cục nên tự đi theo | đo dải sáng ở mép = 0 px |
| Đồng hồ, nhãn trong cảnh bị cắt mép | `boxes` hiện chỉ đo mascot và sừng; vật khác soát bằng mắt trên tờ khung | tờ khung |
| Mascot trông như tấm mỏng | Tránh dừng lâu ở góc xoay ngang quá ~35°; dày t (0,6t trông như huy hiệu) | ảnh tĩnh nhiều góc |
| Mascot lún vào bàn khi gật hay lắc | Xoay quanh mép đáy: bù vị trí theo góc gật, góc lắc (`boPose` của ca mẫu) | dải khung quanh cú đáp |

### Chữ

| Bệnh | Thuốc | Đo |
|---|---|---|
| Chữ đè màn hình sáng khi máy quét (thấp nhất 1,0 : 1) | Máy lùi xa và dạt trái ở nhịp chữ; mép trái màn hình sáng ở x ≥ ~850 px; chỉ quét qua cột chữ khi chữ đã rút; dời mốc chữ | `qa.py text` ≥ 4,5 : 1 (sau sửa: 15,9 : 1) |
| Chữ đè lên vật nhiều chi tiết (G1: chữ "thay" đè giao diện điện thoại) | Giao diện trên màn hình dồn sang nửa phải; nửa trái là tường trơn | `qa.py text` |
| Bảng tên trống dòng khi số khách vượt danh sách (9 tên, ~22 khách) | Quay vòng danh sách tên | khung lúc bảng đầy nhất |
| Chữ thưa, người xem không hiểu ý (bản 1: chữ chỉ hiện 6,2 / 16 s) | Chữ chạy suốt phim, mỗi nhịp một câu, kết bằng câu chốt; chỉ dùng lời đã duyệt | chữ phủ ≥ 65 % phần 3D, trống ≤ 0,6 s |
| Chữ giật, cứ 3 khung lặp 1; end card lệch dần (cả bản 1 cũng bị) | `compose` đưa cả hai nguồn về `settb=1/60,setpts=N` trước khi chồng (đã sửa trong `render.py` 21/10) | so khung chữ trên bản ghép với khung lớp phủ: bản 2 khớp 31/31 và 101/101 khung, end card 300/300 |
| Câu chốt dài hơn cột chữ | Nới cột riêng cho nhịp câu chốt, giữ một dòng và cỡ chữ như V2; phần vượt cột nằm cao hơn ngọn sừng | ảnh khung câu chốt; tương phản đo cục bộ |
| `qa.py text` báo 1,0 : 1 ở chữ có tấm nền riêng (khung trắng, khối nhấn) | Báo động giả: đo cục bộ nét chữ so với nền quanh nét | `qa-checklist.md` nấc 5 (bản 2: 4,70 : 1) |
| Chữ trong cảnh quá nhỏ (bảng CRM: chữ 5–8 px) | Bảng to hơn (0,17 × 0,12 → 0,21 × 0,15 m); chỉ giữ chữ to: giờ, số khách, 2 dòng mới nhất | giờ cao 24–25 px; trên điện thoại vẫn nhỏ |
| Chữ trong cảnh nhòe ở khung đầu | Chặn đồng hồ, chữ trong cảnh ở t ≥ 0 (mẫu nhòe chuyển động lấy t < 0) | khung 0 đọc được |

### Chuyển động

| Bệnh | Thuốc | Đo |
|---|---|---|
| Đứng hình ở nhịp "khựng" (ca mẫu: 33 khung liền ở 9,42–10,0 s) | Nín thở nhưng vẫn chao nhẹ giữ thăng bằng, sừng run khẽ, máy đẩy chậm vào | `metrics.py`: chuỗi đứng ≤ 12 khung (sau sửa: 10) |
| Chống nhàm "đạt" giả | Bản nháp 1 mẫu có nhiễu răng cưa làm khung nào cũng "đổi". Chỉ đo trên bản 16 mẫu | `metrics.py` trên bản chất lượng cuối |
| Khóa cuối đứng lâu trước cú cắt | Dời khóa sát cú cắt (15,85 → 15,98 s); khai báo khoảng lặng 1 khung quanh cú cắt | `metrics.py --declared 15.95:16.05` |
| Hứng lặp đơn điệu, giống "game hứng trứng" | Tăng dần (bản 1: 1 → 2 → 3 vật; bản 2: dày dần theo phách, cách 1,5 s rồi 0,5 s), mỗi lần một kiểu hứng (bản 2: một cú nhảy hứng trên không); không điểm số, không tiếng "boing" | xem tờ khung theo nhịp |
| Sừng giật 1,8° trong 1 khung (ca mẫu: 7,00 s và 7,40 s) | Bỏ công tắc bật/tắt 0/1 trong hàm tư thế (ở đây: tắt dao động sừng khi nín thở). Để pha thở đứng yên thì sừng tự đứng đúng chỗ | dải khung quanh mốc bật/tắt |
| Lúc nhanh lúc chậm: cú lia gấp hơn ~100 lần lúc chậm nhất (bản 1) | Một nhịp đều (ca mẫu 120 BPM), mọi cú chạm rơi đúng phách; muốn dồn thì tăng mật độ cú chạm, không tăng tốc máy; một đường máy; bỏ lia gấp, xoay 180°, nhịp khựng | ô động nhất / ô lặng nhất mỗi 0,5 s (bản 2: 4,8 lần; bản 1: 56) |
| Nền phẳng: 42 % khung gần đứng dù vẫn có chuyển động | Mascot đung đưa liên tục (lắc 1,2° chu kỳ 2 s, xoay 2,5° chu kỳ 4 s); nảy theo phách; máy trôi ±1 cm theo hai chu kỳ lệch nhau (5,3 s và 4,1 s), pha chọn bằng quét lưới để không lúc nào cùng dừng; vật nền cuộn (cột tin); lấy đà trước cú bật | `metrics.py`: phần 3D 42 % → 4,4 %; bản ghép 1,04 % |
| Mascot gần như đứng ở nhịp lặng (nảy 2–4 px) | Nảy theo phách: biên 9 mm, dạng \|sin\|, chạm đáy đúng phách | 6–12 px mỗi phách |
| `metrics.py` báo cắt cứng ở cú chuyển màu nền chậm | Chuyển đều, đủ dài (bản 2: rạng sáng 0,97 s tuyến tính, ~3,5 mức mỗi khung). Đường cong êm 0,65–0,75 s bị nhiễu H.264 đẩy vượt ngưỡng | 0 cắt cứng |

### Kể chuyện

| Bệnh | Thuốc | Đo |
|---|---|---|
| Mascot giật mình mà không rõ vì sao (vật gây ra nhỏ, sát mép trên) | Vật to, rõ, xa mép; xuất hiện trước phản ứng ~0,15 s; có cú "bụp" phồng 1,3 lần (ca mẫu: tin đầu dời 2,05 → 1,95 s, phóng từ ô tin thứ 2) | khung quanh nhịp, bóng ~60 px |
| Vật mang thông tin không bao giờ vào khung (ca mẫu: đồng hồ trên điện thoại) | Chuyển thông tin lên vật máy có quay tới (giờ lên tiêu đề bảng CRM) | tờ khung: đọc được giờ |
| Bảng cuộn nhòe đúng lúc máy lia tới | Cho danh sách đứng yên trước khi máy tới (ca mẫu: từ 12,58 s) | khung cận bảng đọc được 5 dòng |
| Lời kêu gọi cuối đứng không đủ đọc (9 chữ, ~1,6 s) | Tính thời gian đọc ở G2; nới end card nếu Minh đồng ý (ca mẫu: cần ~22 s; Minh giữ 21 s khi duyệt hướng bản 2) | đếm chữ × thời gian đọc |
| Xem không đọng lại gì (bản 1) | Một câu chốt đã duyệt, đặt đúng cú chạm cao trào (bản 2: "Bỏ sót khách" bị gạch đúng lúc Bò hứng tin buổi sáng → "Không bỏ sót khách"); end card nhắc lại | người xem nhắc lại được một câu |
| Vật mang ý nghĩa không đọc ra (bong bóng là khối trắng viền dày) | Làm giống biểu tượng 2D đã duyệt (tin nhắn V2: vỏ bo, đuôi, 2 vạch chữ ở cả hai mặt) | tờ khung |

### Vật và va chạm

| Bệnh | Thuốc | Đo |
|---|---|---|
| Vật bay ra khỏi lòng mascot xuyên qua thành (ca mẫu: thẻ khách xuyên cánh chữ U ở 5,20 s, 6,37 s) | Xuất phát đúng chỗ vật nằm, đi thẳng ra trước 18 cm qua lỗ O (Bezier bậc 3, điểm điều khiển đầu thẳng phía trước), rồi mới vòng sang đích | dải 5 khung quanh nhịp |
| Vật lơ lửng: rời mascot khi mascot còn trên không (ca mẫu: 5,13–5,25 s, lỗi bắt buộc) | Vật chỉ rời sau khi mascot đáp xong (`hold` 0,30 s) | dải 5 khung quanh cú đáp; rà chéo |
| Vật văng ra hông khi mascot còn đang xoay (ca mẫu: 6,27–6,37 s) | Đợi mascot quay mặt lại (`hold` 0,31 s); vật bật ra nhanh rồi chậm dần (ease-out) để rời chỗ trước vật kế tiếp | dải khung, không chồng vật |
| Vật lật hướng trong 1 khung lúc vào khe (ca mẫu: 5,95 s, 6,30 s) | Đường bay kết thúc đúng hướng của mascot lúc tới (nối bằng quaternion), rồi mới chuyển sang toạ độ mascot | khung đúng lúc chuyển |
| Nhiều vật cùng lúc bay ra ngoài mép trên | Hạ điểm phóng; ngửa máy lên vài cm ở các khóa đó | khung đủ mọi vật |
| Khung đầu của vật nhảy vị trí (~3,4 cm) | Khung đầu đặt đúng chỗ vật đang nằm, giữ góc xoay của mascot | dải 5 khung |
| Hạt thở phì quá nhỏ, lẹm vào thành khe | To 34–56 px logo, sinh trong lòng khe, lớn dần trong 60 ms, bay thẳng lên rồi mới tỏa | khung có hạt, phóng 3× |
| Không chắc vật lọt khe có chạm thành | Phóng 3× khung lọt khe; tính kích thước (ca mẫu: khe 53 mm, bóng 40 mm; bóng dày 16 mm < Bò dày 43 mm) | ảnh phóng + số |
| Vùng tràn xanh bị vật phía trước che thành vết khuyết trên mascot | Vẽ vùng xanh xong thì xóa độ sâu, để mascot vẽ đè lên | khung cầu |
| Vệt tối dài 200–310 px trên vùng tràn xanh (bản 2, 15,2–16,0 s) | Bóng tiếp xúc của đồ vật là vật trong suốt, vẽ sau vùng xanh: tắt khi vùng xanh tràn | điểm ảnh lệch nền xanh: 1500–2000 → ≤ 6 |
| Tin sau hiện đè tin trước chưa rời chỗ (tin bay chủ yếu theo chiều sâu nên trên hình gần như đứng yên) | Tính đường bay theo màn hình: ngang ease-out bậc 3 (bật rất nhanh), dọc 1,6k − 0,6k² (nhanh rồi chậm), sâu tuyến tính; tin hiện 0,20 s rồi mới bay | tờ khung quanh mỗi lần hiện |
| Vật bay đè qua cột vật cũ trên màn hình | Luôn bay xuống, xa cột; bỏ kiểu "ném lên" | ảnh phóng quanh cột |
| Vật cùng màu mascot lướt trước thân mascot (chỉ còn vạch trắng nhòe) | Vật lùi ra sau qua lỗ O, vòng sau lưng để mascot che, rồi mới tới đích | dải khung |
| Vật chờ cắm vào vai khe khi mascot đang nhảy (đường bay nhắm chỗ mascot sau khi đáp) | Vật giữ cao, rơi muộn; đoạn rơi nối liền vận tốc: gia tốc a = 2(D − v·Td)/Td² với D quãng rơi, Td thời gian rơi, v vận tốc cuối đường bay (để không gãy tốc độ) | soát mọi khung đoạn nhảy |
| Vật mới rơi đè vật cũ còn trong lòng mascot | Vật cũ lùi ngay khi hứng, hoặc trước cú nhảy; lúc lùi tính trong toạ độ của mascot để bám theo cả khi mascot nhảy | soát mọi khung; khoảng cách nhỏ nhất giữa hai vật trên hình (bản 2: 7 px) |

### Cầu 3D → 2D

| Bệnh | Thuốc | Đo |
|---|---|---|
| Họa tiết nền end card bật ra đúng cú cắt | Khung 2D đầu chỉ có nền trơn + mascot; họa tiết nở dần (ca mẫu: khung 960–990, từ mascot ra) | nền ngoài mascot ở khung đầu lệch ≤ 1 mức |
| Mascot 3D lệch mascot 2D ở cú cắt | Đo vị trí 2D bằng chính hàm vẽ của Remotion (`endcard-bo.json`); 3D về đúng vị trí, cỡ, góc sừng, nhịp thở đó | `qa.py lock` ≤ 2 px (ca mẫu: 1,05 px) |
| Thành trong lòng O, khe lộ ra do phối cảnh ở khung khóa | Dẹt độ dày 1 → 0,03 lúc tô phẳng; ống kính hẹp dần (FOV 30° → 7°) | `qa.py lock` |

### Render và máy

| Bệnh | Thuốc | Đo |
|---|---|---|
| Render chậm 5–6 lần | Đang chạy GPU Intel: kiểm cờ GPU | `renderer` trong `render-meta.json` có "NVIDIA" |
| Khung đầu chậm (250–660 ms) | Bình thường: biên dịch shader. Không tính vào tốc độ; xem trung vị | `msMedian` trong `render-meta.json` |
| Vệt nhòe có vân sọc khi vật bay rất nhanh (ca mẫu: khung 298, 446) | Tăng mẫu cho đúng khoảng khung đó: `"sppBoost": [[292, 304, 48], [440, 452, 48]]` trong job `clip` | phóng to khung đó |
| Bản có giờ phim ghi khung 960 là "15.999" | In giờ phim theo số khung (giờ:phút:giây:khung), không theo giây làm tròn | xem khung 960 hiện `00:00:16:00` |
