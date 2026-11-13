Phim 3D Bò OPA — Ý 2 "Thủ môn" · BẢN 2 · 21/10/2026
Trạng thái: **ĐÃ DUYỆT 21/10.** Minh duyệt hướng sửa (`DE-XUAT-V2.md`, "Duyệt hướng sửa bản 2 như đề xuất, dựng lại đi"), rồi xem, nghe và duyệt bản 2 cùng ngày. Ngày 22/10 Minh chọn bản âm dùng thư viện SFX (`docs/film3d/am-thu-vien/README.md`). Bản giao: `out/thu-mon-3d-16x9-ban2/` (gốc dự án).
- Bản 1 (G2 duyệt 19/10, sau đó Minh chê và không đăng) giữ ở `PROMPT-PACK.ban1.md`. Hình bản 1 còn nguyên ở `out/animatic-hq/`, `out/thu-mon-3d-16x9/` (gốc dự án).
- Mã `timeline.js` bản 1 đã được thay bằng bản 2 (dự án không có git).
- Giữ từ bản 1: hình Bò (look C2, dày t), tổng 21 s, end card, cú cắt khớp 3D → 2D, âm sắc phương án A.

# Kịch bản (prompt pack 6 khối)

```text
BRAND
HERO: Bò OPA — dấu hình học chỉ là cái đầu: mõm chữ U bo tròn có lòng O xuyên, 2 sừng cong, khe trán
(2 mép = 2 lỗ mũi). Đùn từ geometry.json "mark", dày t, cạnh vát vào trong. Look C2: mặt trước và mặt sau
#0068FF, thành bên #003C99 → gần #0068FF. Không mắt, miệng, tay chân; không bóp méo; sừng cử động quanh chân
sừng, về khung khóa ở cuối. Diễn bằng tư thế, sừng, hơi thở phì (hạt xanh từ 2 lỗ mũi).
ĐỐI THỦ: tin nhắn của khách — đúng biểu tượng tin nhắn V2 (vỏ bo R28, đuôi trái, 2 vạch chữ trắng ở cả hai
mặt), dày 7 mm. Tin khách #003C99; hứng xong chuyển #0068FF.
THẾ GIỚI: nền liền một màu như V2 (bàn, tường, sàn cùng một màu không chịu đèn): đêm #003C99, sáng trắng.
Điện thoại khổng lồ thân trắng dựng sau Bò (màn hình sáng là nền ngay sau Bò); trên màn hình là cột tin cũ
màu nhạt #E6F0FF, tin mới hiện ngay dưới cột. Bảng CRM nhỏ ngay bên phải Bò, luôn trong khung (tên giả của
V2, "Đã trả lời"). Chồng sổ bên trái. Đồ vật có đèn cố định và vệt bóng tiếp xúc nhuộm xanh.
BẪY: chính khối chữ U — tin lọt khe trán, rơi xuống đáy lòng O, chuyển xanh OPA, thành thẻ khách lùi ra sau
qua lỗ O rồi vòng sang bảng CRM.
BẢNG MÀU: #0068FF, #003C99, #FFFFFF, #E6F0FF, #0A0A0A.
KẾT: sáng ra, "Bỏ sót khách" bị gạch đúng lúc Bò hứng tin buổi sáng → "Không bỏ sót khách"; Bò lấy đà,
vùng xanh tràn từ lòng O, Bò chuyển trắng, khóa đúng chỗ Bò của end card 16:9.

FORMAT: một film.html, three.js 0.160.0, 1920×1080, 60 fps, 16 s 3D + 5 s end card Remotion; poseAt(t)
là hàm thuần của t; random có seed; mọi cú chạm là một dòng EVENTS dùng chung cho hình và âm.

LOOK: phẳng như V2, không còn phòng tối có đèn. Bò không chịu đèn (C2). DOF nhẹ, Bò luôn nét; không tone map
ACES; nhòe chuyển động 16 mẫu. Rạng sáng trộn màu nền trong sRGB như V2 (trộn tuyến tính ra xám đục).

BEATS (s): một nhịp đều 120 BPM (phách 0,5 s), mọi cú hứng rơi đúng phách. Xem bảng storyboard.

CAMERA: một đường máy duy nhất: đẩy vào đều 0 → 14,85 s, trôi ngang/dọc ±1 cm (hai chu kỳ lệch nhau, không
lúc nào cùng dừng); không lia gấp, không xoay quanh Bò. Cột chữ trái x ≤ 780 px là nền trơn; mép trái màn
hình ≥ ~850 px; bảng CRM luôn trong khung. Cuối: dolly-zoom FOV 30° → 7° về khung khóa.

CHECKS: mặt trước Bò #0068FF (lệch CIEDE2000 ≤ 2) mọi khung đo; ban đêm nền ngay sau Bò sáng; khung khóa khớp
Bò 2D ≤ 2 px; không xuyên vật, không chồng bóng; ngọn sừng cách mép ≥ 24 px; mỗi 2 s ≤ 15 % khung gần đứng,
chuỗi ≤ 12 khung; chữ phủ ≥ 65 % phần 3D, khoảng trống giữa hai nhóm ≤ 0,6 s; tương phản chữ ≥ 4,5 : 1.
```

# Storyboard theo giây (60 fps)

| # | Giây | Khung | Người xem thấy | Bò diễn | Máy | Chữ |
|---|---|---|---|---|---|---|
| 1 | 0,00–1,50 | 0–89 | Đêm, nền phẳng #003C99. Điện thoại khổng lồ thân trắng sau Bò; cột tin cũ màu nhạt. 1,00 s: tin mới #003C99 hiện ở ô ngay dưới cột, rung như báo tin. | Đung đưa nhẹ (lắc 1,2°/2 s, xoay 2,5°/4 s), thở chu kỳ 2,4 s; 0,95–1,35 quay nhìn tin | Đẩy vào đều, trôi ±1 cm | **L1** "Khách nhắn / Tối qua…" |
| 2 | 1,50–3,40 | 90–203 | Tin 1 bật khỏi màn hình, lật một vòng, nhỏ dần, trượt chéo xuống trên đầu Bò rồi lọt khe đúng 3,00 s, chuyển xanh OPA. 3,20 thẻ lùi qua lỗ O, vòng sau lưng Bò, tới bảng CRM 3,80; cột tin cuộn lên một dòng. | Ngẩng nhìn (1,5–2,4), phì 2,25, trượt trái tới chỗ hứng, nảy 6 mm đúng phách, gật nhận tin | như trên | **L4** "AI trực thay / Anh chị." (khối nhấn "Anh chị." quét đúng 3,00 s) |
| 3 | 3,40–5,00 | 204–299 | Tin 2 (hiện 3,20, bay 3,40) hứng 4,50; tin 3 hiện 4,30. | Trượt phải đón tin 2 | như trên | (L4 rút) |
| 4 | 5,00–7,50 | 300–449 | Tin dày, đều mỗi 0,5 s: hứng 5,5 · 6,0 · 6,5 (nhảy cao 9 cm, hứng trên không) · 7,0. Mỗi thẻ thêm một dòng ở bảng CRM, cột tin cuộn mỗi cú hứng. | Hứng liên tiếp, gọn; thở nhanh (chu kỳ 1,3 s); phì mạnh 7,25 sau đợt dồn | như trên | **L5** "OPA ghi lại / Từng khách." |
| 5 | 7,50–9,70 | 450–581 | Bò quay sang bảng CRM. Tua cả đêm 8,2–9,6: cột tin cuộn đều 10 dòng, CRM thêm 12 dòng "Đã trả lời", đồng hồ CRM 22:51 → 07:00. | Quay sang CRM (7,4–8,0), gật soát theo phách 8,5 · 9,0, quay lại 9,3 | như trên | **L6** "Trả lời ngay, / Cả ngoài giờ" |
| 6 | 9,70–10,20 | 582–611 | Rạng sáng: nền chuyển dần #003C99 → trắng; máy trắng hòa vào nền. | Đung đưa, thở | như trên | (giữa L6 và câu chốt) |
| 7 | 10,20–12,00 | 612–719 | Tin buổi sáng hiện 10,40, bay 10,60; Bò ngẩng nhìn; hứng 11,50 đúng lúc chữ gạch "Bỏ sót khách"; tin ở lại lòng O (nguồn vùng xanh). | Ngẩng 4°, xoay 5° nhìn tin; hứng | như trên | **L8 → L8b**: "Bỏ sót khách" hiện 10,20, bị gạch 11,50; "Không bỏ sót khách" trồi 11,75, khối nhấn quét 12,00 |
| 8 | 12,00–14,50 | 720–869 | Sáng, nền trắng. | Hếch đầu tự hào (12,1–13,3); nảy liền mạch theo phách, chạm đáy đúng 12,0 · 12,5 · … · 14,5; sừng giật nhẹ mỗi phách; phì 12,50 | như trên | L8b đọc trọn, rút xong trước 14,80 |
| 9 | 14,50–16,00 | 870–959 | Lấy đà 14,50–14,85, bật xả: vùng xanh tràn từ lòng O (14,85–15,35); Bò chuyển trắng theo từng điểm ảnh, dẹt thành dấu 2D, khóa 15,98 đúng vị trí, cỡ, góc sừng, độ nghiêng, nhịp thở của Bò end card. | Hít hơi (phồng 4 %), ngửa 5°, nhổm 4 mm nhanh dần → xả | Dolly-zoom FOV 30° → 7° | — |
| 10 | 16,00–21,00 | 960–1259 | End card 16:9 "trạm OPA" của V2, giữ nguyên bản 1: "OPA" khóa 16,60; "AI CRM + AI Sales Agent"; "Nhắn OPA / Để nhận báo giá" + nút "“KHÔNG SÓT KHÁCH”" đứng yên từ 19,60. | Bò 2D | — | end card |

**Tổng: 21,0 s** (16,0 s 3D + 5,0 s end card).

# Chữ (lời V2 bản 16:9 Minh đã duyệt, không viết lời mới)

- Lấy nguyên văn bằng `copyGroupsW()`, theo thứ tự mới:
  - L1 "Khách nhắn / Tối qua…"
  - L4 "AI trực thay / Anh chị."
  - L5 "OPA ghi lại / Từng khách."
  - L6 "Trả lời ngay, / Cả ngoài giờ"
  - Câu chốt kiểu V2: L8 "Bỏ sót khách" bị gạch (`StrikeW`) → L8b "Không bỏ sót khách"
- Đêm chữ trắng trên #003C99; ngày chữ đen trên trắng.
- Cột trái x ≤ 780 px cho L1–L6. Riêng câu chốt nới cột (giữ cỡ 112 px và khối nhấn #0068FF như V2), nằm trên y = 450 px ở phần x ≥ 1130 px để không chạm sừng Bò.
- Mọi nhóm trôi nhẹ liên tục lúc đứng, như máy quay ảo của V2.

# Luật rút từ bản 2

1. Nền phẳng làm cùng một chuyển động ra ít điểm ảnh đổi hơn hẳn phòng có đèn (thước "độ chuyển động" của bản 1 nhỏ đi khoảng 10 lần). Vì vậy:
   - Máy phải trôi liên tục, chọn pha để không lúc nào cùng dừng.
   - Bò luôn đung đưa nhẹ.
   - Nhịp lặng thì dùng cử chỉ theo phách (nảy, gật), không đứng.
   - Đo khung đứng trên bản chất lượng cuối, sau khi ghép chữ.
2. Tin bay ra không được đi ngang qua cột tin cũ (lỗi "bóng đè vạch ô tin" của bản 1). Tin bật khỏi ô theo hướng xa cột, đủ nhanh để tin sau (cách 0,45 s) hiện không chạm tin trước.
3. Vật cùng màu Bò không được lướt trước thân Bò (chỉ còn 2 vạch trắng nhòe, trông như lỗi). Thẻ lùi ra sau, để Bò che.
4. Ban đêm, nền ngay sau Bò luôn là màn hình sáng (kiểm bằng độ sáng vòng nền quanh bóng Bò).
5. Cú cắt 3D → 2D như bản 1: tư thế khóa lấy từ `out/endcard-bo.json`, Bò dẹt dần thành dấu 2D, `qa.py lock` ≤ 2 px. Khi đo chuyển động, khai báo 15,95–16,05 s là khoảng lặng có chủ ý.
