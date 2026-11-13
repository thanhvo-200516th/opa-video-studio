# Bố cục và chất liệu đã duyệt

## Khung dọc an toàn

- Thiết kế 9:16. Đặt toàn bộ nội dung quan trọng trong khoảng x=8–92% chiều rộng, y≈11–47% chiều cao nếu footage là hai người đứng trên bãi biển với nhiều khoảng trời; xem ảnh khoanh mới nhất và chỉnh theo vị trí đầu người ở footage khác. Chừa mép trên cho UI và crop của TikTok/Reels/Shorts.
- Với canvas làm việc 720×1280 của clip bãi biển: ảnh x≈50..670, y≈145..345; chữ chính quanh y≈335, chữ phụ quanh y≈420. Với clip hai người trước cổng dự án: ảnh x≈60..660, y≈175..440; chữ chính quanh y≈470, chữ viết tay quanh y≈540. Đây là điểm xuất phát, không áp dụng máy móc cho footage khác.
- Căn giữa chữ theo chiều ngang. Hai dòng đủ gần để đọc như một cụm, nhưng không chạm dấu tiếng Việt/glow. Giữ mặt và người hoàn toàn rõ; tránh bố trí vào phần thân dưới.

## Typography

- Chữ chính: Montserrat Bold/ExtraBold, viết hoa; gradient xanh dương (`#52B9F3` → `#1159B5`) hoặc xanh lá tùy nền và yêu cầu mới nhất. Chọn lõi đủ đậm trên vùng sáng; gradient mềm, không để đầu chữ nhạt chìm vào nền. Chỉ thêm glow xanh mỏng ngoài lõi và bóng **cùng tông** rất nhẹ; không dùng stroke đen dày hay hiệu ứng 3D thô.
- Chữ phụ: `1FTV Autography` đã dùng trong bản duyệt (hoặc `Fz Photograph` nếu người dùng cung cấp và yêu cầu cụ thể); **màu vàng** có lõi đủ đậm trên nền trắng, glow vàng nhẹ. Kiểm tra glyph tiếng Việt trước khi dựng; không âm thầm thay bằng Montserrat Italic.
- Dùng màu xanh dương hoặc xanh lá theo yêu cầu từng dự án; chữ viết tay vẫn vàng trừ khi người dùng chỉ định khác. Không phủ đen vùng trời để tạo tương phản.

## Ảnh kiến trúc

- Đặt ảnh trên trục giữa vùng trời, phía trên cụm chữ. Cho tan nhẹ ở **mép**; phần giữa đủ rõ để nhận ra căn hộ, biển, dự án. Tránh phủ alpha thấp toàn ảnh khiến nó nhợt và khó thấy.
- Mức tham chiếu của bản cuối: center alpha khoảng 0.9; feather mép ngang cỡ 5% và mép dọc cỡ 10%; tăng tương phản vừa phải và sharpen nhẹ. Không cắt thành thẻ UI, không viền hay nhãn “Hình ảnh minh hoạ”.
- Chọn **nhiều** cảnh ảnh theo nội dung lời: dự án/khu nhà, địa điểm/biển Hạ Long, không gian căn hộ. Chuyển ảnh khi ý thoại đổi bằng crossfade mềm, không lặp một hình từ đầu đến cuối. Ảnh AI/chung chỉ là tư liệu gợi ý, không ngụ ý đây là ảnh thật của dự án. Ảnh đứng sau chữ và không che người.

## Motion

- Chỉ chọn vài cụm nhấn. Trong mỗi cụm, từng từ xuất hiện khi từ ấy bắt đầu được nói, fade in 0,12–0,22 giây và nhích lên 6–12 px ở canvas 720; các từ cũ **giữ nguyên** để cụm hoàn chỉnh đọc được. Sau mốc cuối, giữ cụm thêm vừa đủ rồi fade out cả cụm 0,25–0,4 giây. Không hiển thị sớm cả cụm, không đợi nói xong mới cho chữ lên, không chớp liên tiếp các từ ngắn.
- Zoom footage khoảng 1.00–1.06 xuyên qua clip, có cả zoom in và zoom out; không làm méo hình hay đổi khuôn mặt.
- Không thêm thanh, vạch dọc, vạch ngang hoặc các trang trí che nền. Mục tiêu là ảnh và chữ tinh tế trên footage gốc.
