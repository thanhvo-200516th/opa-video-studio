# OPA — Blueprint Logo Reveal và video tham chiếu

## Nguồn đã đối chiếu

- Video người dùng: `/media/vmiz/Over Powers/THÀNH V/Download.mp4`.
- SHA256: `816bf634df21cc6da2634ce541900520e5b00d133d9e0dc30bf5e7488d079c7f`.
- Hình: 576 × 1024, 30 fps, giải mã đủ 478 frame, thời lượng hình 15,933 giây. Audio dài khoảng 15,953 giây.
- Đây là video quay màn hình một bài motion logo Framer; khung dọc còn có màn hình AE, phối cảnh, phản chiếu và watermark. Phần motion trong màn hình được dùng làm tham chiếu.
- Template người dùng cung cấp: `/media/vmiz/Over Powers/video AE/video/mẫu intro logo/Blueprint Logo Reveal/Blueprint Logo Reveal.aep`.
- File gốc có SHA256 `4d1296a63d87e2a088ad68dc6bb458782e29be760aed4702ac1727cc0da1ed31`.
- MAIN COMP của template: 3840 × 2160, 30 fps, 10 giây; file được AE hiện tại chuyển từ phiên bản 18.4.1.

## Bảng chuyển động theo video gốc

Frame đánh số từ 0. Các mốc dưới đây là mốc quan sát trên file được cung cấp, có thể lệch 1–2 frame ở đoạn có blur hoặc chuyển cảnh liên tục.

| Video gốc | Frame | Điều nhìn thấy | Cách áp dụng vào OPA |
|---|---|---|---|
| 0,000–1,633s | 0–49 | Nền xanh; điểm và đoạn thẳng lần lượt dựng silhouette Framer | Giữ cách dựng theo nét. Template dùng contour của OPA và camera/lưới có sẵn |
| 1,667–3,100s | 50–93 | Cắt sang nền tối; khối logo sáng rõ dần | Dùng quá trình outline → logo màu trong template; giữ hình OPA đúng artwork |
| 3,133–4,100s | 94–123 | Một phần logo chuyển xanh; đường chéo và nhãn nhỏ xuất hiện | Chuyển bảng màu về OPA Blue; đường phụ ưu tiên trục ngang/dọc của wordmark |
| 4,133–5,600s | 124–168 | Vệt sáng kéo dài; cảm giác khối nghiêng/xoay, chớp sáng | Lấy nhịp chuyển nét thành khối và chuyển động chiều sâu làm tham chiếu; dùng camera/echo của template |
| 5,633–6,600s | 169–198 | Glow xanh bùng lên rồi giảm, để lại outline | Giảm echo về mức vừa phải, giữ nét và logo còn đọc được |
| 6,633–7,100s | 199–213 | Logo nhỏ, cô đọng ở trung tâm | Có một giai đoạn settle trước cảnh nhận diện cuối |
| 7,133–9,100s | 214–273 | Wordmark Framer trên nền sáng → xanh nhạt → đen → xanh đậm; mỗi biến thể khoảng 0,5s | Bản intro 10s dừng ổn định; bản brand film bổ sung đoạn bảng màu và nền xanh |
| 9,133–10,100s | 274–303 | Typography phóng lớn, trượt ngang, các lớp chữ lệch nhau | Không kéo giãn wordmark OPA; giữ hình học chính xác và dùng chuyển động layer/card |
| 10,133–11,600s | 304–348 | Các thẻ màu, sau đó trở về icon trên nền trắng | Đoạn 10–12,3s trong brand film: ba thẻ OPA Blue / White / Ink |
| 11,633–12,600s | 349–378 | Logo có viền màu quang học trên nền xanh | Dùng giới hạn xanh–trắng của OPA; RGB split của template được tắt để nét gọn |
| 12,633–14,600s | 379–438 | Icon trên hình tròn rồi biến dạng thành vật thể dạng mũ | Đoạn ứng dụng icon O trên badge tròn; không cần thêm hình mũ chưa có trong bộ thương hiệu |
| 14,633–15,433s | 439–463 | Đổi nền xanh; vật thể xoay/rời khung | Chuyển về nền OPA Blue và wordmark trắng ở cảnh kết |
| 15,467–15,900s | 464–477 | Quay lại đoạn điểm/nét ban đầu, tạo cảm giác loop | Intro OPA giữ cảnh kết đủ lâu để ghép vào video doanh nghiệp |

## Kịch bản bản intro 10 giây

| Thời gian | Hình ảnh và chuyển động | Mục đích |
|---|---|---|
| 0–3s | Camera và các lớp nét của Blueprint tạo cấu trúc OPA | Giới thiệu hình học của thương hiệu |
| 3–5,2s | Contour O/P/A hoàn thiện, xuất hiện đường dựng và nhãn W/H | Gợi cảm giác thiết kế chính xác |
| 5,2–7,2s | Chuyển sang logo xanh, giảm các chi tiết kỹ thuật | Tập trung vào dấu hiệu nhận diện |
| 7,2–10s | Logo OPA và dòng “Marketing × Công nghệ × AI” | Giữ đủ thời gian đọc trước nội dung chính |

## Kịch bản bản brand film 16 giây

| Thời gian | Nội dung |
|---|---|
| 0–10s | Bản intro Blueprint dùng chung nguồn chỉnh sửa |
| 10–12,3s | Ba thẻ OPA Blue / OPA White / OPA Ink trượt vào và rời khung |
| 12,3–13,5s | Icon O từ artwork gốc xuất hiện trên badge tròn |
| 13,5–16s | Nền xanh, wordmark OPA trắng, tagline xuất hiện nhẹ và giữ đến cuối |

## Các quyết định về thiết kế

- Wordmark lấy từ artwork OPA đã cung cấp; O/P/A là shape path riêng, không gõ lại bằng font.
- Bảng màu cốt lõi: OPA Blue `#0068FF`, trắng và màu chữ tối.
- Các thước đo góc/bán kính của logo demo được tắt. Các đường `OPA_RULER_*` được dựng theo bounding box của wordmark OPA. W/H là ký hiệu chiều rộng/chiều cao, không phải tuyên bố tỷ lệ vàng hay số đo kỹ thuật được thương hiệu phê duyệt.
- Cảnh bảng màu và badge dùng shape/text gốc của AE, có thể chỉnh trong timeline.
- Audio là sound-design hướng dẫn tự tạo trong bộ asset; không lấy nhạc của video Framer hoặc nhạc bán riêng của template.
- Câu tagline đang dùng là phương án dựng cho bản này và có thể sửa ở `YOUR TEXT `.

## Nguồn để mở lại

- [Blueprint Logo Reveal — PixelTruck](https://elements.envato.com/blueprint-logo-reveal-KPBZ8GD).
- PDF hướng dẫn nằm trong thư mục `Tutorial and links` của bộ template người dùng cung cấp.
- Bảng khung hình và dữ liệu đo nằm trong bộ `Reference` của lượt phân tích trước.
