Phim 3D Bò OPA "Thủ môn" · Đề xuất bản 2 sau góp ý của Minh ngày 19/10/2026 · Soạn: Claude Code (Opus 5.5)
Trạng thái: **MINH ĐÃ DUYỆT HƯỚNG SỬA 21/10/2026, rồi xem, nghe và DUYỆT BẢN 2 cùng ngày.** Bản 2 ở `out/thu-mon-3d-16x9-ban2/` (gốc dự án); kết quả đo và rà chéo trong `FOLLOWUPS.md`. Dải "độ chuyển động 1,5–8" ở bảng dưới không đạt theo nghĩa đen trên nền phẳng (đã báo, xem `FOLLOWUPS.md` mục "Để ngỏ"). Bản 1 giữ nguyên ở `out/thu-mon-3d-16x9/`.

Góp ý của Minh: "biểu tượng tin nhắn vẫn bị lỗi, background thì đen không đồng nhất, hiệu ứng thì lúc nhanh lúc chậm, text thì không dàn trải nên làm ý nghĩa của video khó hiểu! Xem không đọng lại gì cho người xem cả".

Tờ một trang: `out/thu-v2/de-xuat-v2.png` (ảnh trước/sau + biểu đồ nhịp).

# 1. Đổi lời chê thành việc đo được

| Minh nói | Soi lại thấy (bằng chứng) | Sửa ở bản 2 | Đạt khi |
|---|---|---|---|
| Biểu tượng tin nhắn vẫn bị lỗi | Bong bóng trắng bay trước màn hình trắng gần như vô hình (3,17 s). Bóng bật ra đè lên vạch của ô tin trông như lỗi hình (5,70 s, 11,55 s). Bóng là khối trắng viền dày, không có vạch chữ nên không đọc ra là tin nhắn (6,83 s). | Bong bóng đúng biểu tượng tin nhắn của V2 (vỏ bo, đuôi, 2 vạch chữ trắng ở cả hai mặt), dày 7 mm. Tin khách màu #003C99, hứng xong chuyển #0068FF. Ô tin trên màn hình đổi sang nền nhạt; chỉ tin mới nhất màu #003C99 và chính nó bay ra. | Ảnh thử `out/thu-v2/moi/*.png`. Mọi khung có bóng bay: bóng không nằm trên nền cùng màu (soi tờ khung). |
| Nền đen không đồng nhất | Phòng tối có đèn: tường xám đen, mặt bàn loang sáng, sàn đen. Ba mảng tối khác nhau, có vệt sáng. V2 vẽ đêm là nền phẳng #003C99, ngày là nền phẳng trắng. | Nền liền một màu như V2: đêm #003C99, sáng chuyển dần sang trắng. Bàn, tường, sàn cùng một màu không chịu đèn. Đồ vật dùng đèn cố định, có bóng tiếp xúc nhuộm xanh. | Ảnh thử. Nền ngoài đồ vật lệch không quá 2 mức trong cả khung. |
| Hiệu ứng lúc nhanh lúc chậm | Đo độ chuyển động mỗi khung: lúc có chữ gần đứng yên (0,3–0,7), lúc hứng bóng dồn dập (3–16), cú lia sang CRM 46, gấp khoảng 100 lần. Biểu đồ `out/thu-v2/nhip-ban-cu.png`. | Một nhịp đều 120 BPM: mọi cú hứng rơi đúng phách (mỗi 0,5–1,5 s). Máy quay một đường chậm, đều; bỏ cú lia gấp sang CRM, cú xoay 180°, cú lao ra mép bàn và nhịp khựng. Bảng CRM luôn trong khung. | Trung bình mỗi 0,5 s nằm trong dải 1,5–8. Không đỉnh nào quá 12, trừ cú dolly-zoom cuối. |
| Chữ không dàn trải, khó hiểu ý | Chữ chỉ hiện 6,2 / 16 s của phần 3D. Đoạn 2,3–10,2 s (8 s hứng bóng) không có chữ nào giải thích. | Chữ chạy suốt phim, mỗi nhịp một câu, đều một cột trái. Dùng **lời V2 bản 16:9 Minh đã duyệt**, không viết lời mới. | Chữ phủ ≥ 65 % phần 3D; khoảng trống giữa hai nhóm ≤ 0,6 s. |
| Xem không đọng lại gì | Chưa có câu chốt; ý "không sót khách" chỉ nằm trên nút của end card. | Cao trào là câu chốt của V2: "Bỏ sót khách" bị gạch, đổi thành "Không bỏ sót khách". End card nhắc lại bằng nút "KHÔNG SÓT KHÁCH". | Người xem chỉ nhớ một câu: "Không bỏ sót khách". |

# 2. Kịch bản bản 2 (21 s, giữ end card đã duyệt)

Mạch truyện một câu: **khách nhắn lúc đêm → AI của OPA trực, hứng hết từng tin → ghi lại, trả lời ngay → sáng ra: không bỏ sót khách nào → nhắn OPA.**

| # | Giây | Người xem thấy | Bò diễn | Máy | Chữ (lời V2 16:9 đã duyệt) |
|---|---|---|---|---|---|
| 1 | 0,0–2,5 | Đêm: nền #003C99 phẳng. Điện thoại khổng lồ sáng sau Bò, đồng hồ 22:47. Một ô tin mới hiện trên màn hình rồi bay ra (1,5 s). | Thở chậm, ngẩng theo tin | Đẩy vào chậm, đều | **L1** "Khách nhắn / Tối qua…" (0,3–2,3) |
| 2 | 2,5–5,0 | Bò trượt sang hứng tin 1 qua khe trán (3,0 s). Tin chuyển xanh OPA, thành thẻ bay sang bảng CRM; bảng thêm dòng "Đã trả lời". Tin 2 tới, hứng (4,5 s). | Trượt gọn, đáp đúng phách | Bám ngang chậm | **L4** "AI trực thay / Anh chị." (2,6–4,7) |
| 3 | 5,0–7,5 | Tin tới dày hơn, đều đặn mỗi 0,5 s: hứng ở 5,5 · 6,0 · 6,5 (nhảy hứng quả cao) · 7,0. Mỗi thẻ thêm một dòng ở bảng CRM. | Hứng liên tiếp, gọn, chắc | Lùi nhẹ cho thấy cả bảng CRM | **L5** "OPA ghi lại / Từng khách." (5,0–7,1) |
| 4 | 7,5–10,0 | Bảng CRM: mọi dòng "Đã trả lời". Đồng hồ trên bảng tua 22:59 → 07:00. | Đứng vững, thở đều | Trôi về khung chữ | **L6** "Trả lời ngay, / Cả ngoài giờ" (7,6–9,7) |
| 5 | 10,0–13,8 | Trời sáng: nền chuyển dần sang trắng phẳng. "Bỏ sót khách" hiện, bị gạch, đổi thành "Không bỏ sót khách" (đúng kiểu V2). | Hếch đầu tự hào, một hơi phì | Đẩy vào chậm | **L8 → L8b** "Bỏ sót khách" → "Không bỏ sót khách" (10,2–13,6) |
| 6 | 13,8–16,0 | Vùng xanh tràn từ lòng O; Bò chuyển trắng, khóa đúng chỗ Bò của end card (như bản 1, lệch ≤ 2 px). | Sừng, nhịp thở về khung khóa | Dolly-zoom | — |
| 7 | 16,0–21,0 | End card "trạm OPA" (giữ nguyên bản đã duyệt) | Bò 2D | — | "OPA" / "AI CRM + AI Sales Agent", rồi "Nhắn OPA / Để nhận báo giá" + nút "“KHÔNG SÓT KHÁCH”" |

- **Số cú hứng:** 7 (bản 1: 10), đều nhịp, mỗi cú một thẻ sang CRM. Bỏ: xoay 180°, bóng đậu ngọn sừng rồi hất, lao ra mép bàn, nhịp khựng, cú lia gấp sang CRM.
- **Chữ:** 5 nhóm lời V2 đã duyệt, đặt theo thứ tự mới. Không thêm lời mới, không đổi chữ.
- **Giữ nguyên:** hình Bò (look C2, dày t), tổng 21 s, end card, cú cắt khớp 3D → 2D, giọng âm (phương án A cả ba nhóm). Nhạc dựng lại theo nhịp mới.

# 3. Việc phải làm nếu duyệt (ước lượng)

1. Lead: viết lại `timeline.js` theo bảng trên; bật `world: { bg: 'flat', bubble: 'icon' }`; đổi ô tin trên màn hình sang nền nhạt + tin mới nhất bay ra; luật đêm vẫn giữ (Bò xanh luôn đứng trước màn hình sáng). Khoảng 1–2 giờ.
2. Lane R: lớp chữ theo 5 nhóm mới (dùng lại `StrikeW` của V2 cho L8 → L8b), end card giữ nguyên. Khoảng 30–45 phút.
3. Lane A: dựng lại cue và nhạc theo nhịp mới, giữ âm sắc phương án A. Khoảng 1 giờ.
4. Thang kiểm 8 nấc + rà chéo bằng agent mới, rồi gửi Minh bản có giờ phim.
