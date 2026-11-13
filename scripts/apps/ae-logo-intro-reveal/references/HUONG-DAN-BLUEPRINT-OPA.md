# Hướng dẫn dựng OPA từ Blueprint Logo Reveal

Project làm việc: `/media/vmiz/Over Powers/video AE/OPA-Blueprint-OPA/OPA-Blueprint-OPA.aep`.

Giữ nguyên thư mục Assets bên cạnh project. File gốc của PixelTruck vẫn nằm tại `/media/vmiz/Over Powers/video AE/video/mẫu intro logo/Blueprint Logo Reveal`.

## 1. Mở đúng bản dựng

1. Trong After Effects, chọn **File → Open Project…** — Mở project; phím tắt **Ctrl+O**.
2. Chọn `OPA-Blueprint-OPA.aep` trong thư mục bàn giao.
3. Trong bảng **Project**, mở folder **00_OPA_EXPORTS**.
4. Double-click `OPA_10s_16x9_1920x1080` để xem intro 10 giây. Để xem bản có bảng màu và badge, mở `OPA_16s_BRAND_FILM_1920x1080`.
5. Chọn độ phóng đại **Fit** — Vừa khung. Khi chỉnh, có thể chọn độ phân giải **Half** — Một nửa; khi xuất chọn Full.

**Điểm kiểm tra:** có đúng chữ OPA, phần rỗng của O/P còn nguyên và không có sọc màu báo thiếu footage.

## 2. Hiểu cấu trúc trước khi sửa

| Comp/layer | Công dụng |
|---|---|
| `MAIN COMP` | Engine Blueprint 4K của template, 3840×2160 / 30 fps / 10s |
| `MAIN COMP → CONTROL` | Nét logo, echo, grid, rulers, màu, blur và vị trí chữ |
| `MAIN COMP → AUXILIARY GEOMETRY ` | Hướng và cường độ các hình học phụ |
| `MAIN COMP → CC` | Nhiễu và chỉnh hình tổng |
| `MAIN COMP → MOTION BLUR` | Pixel Motion Blur của tác giả; đã tắt trong bản OPA để nét rõ và render nhẹ hơn |
| `YOUR LOGO` | Artwork logo dùng chung cho các comp của template |
| `YOUR TEXT ` | Dòng tagline; tên comp gốc có khoảng trắng cuối |
| `ALL RULERS` | Các thước của tác giả và bộ đường `OPA_RULER_*` đã thêm |
| `OPA_10s_16x9_1920x1080` | Bản Full HD chứa `MAIN COMP` ở Scale 50% và audio riêng |
| `OPA_16s_BRAND_FILM_1920x1080` | Intro dùng chung, sau đó là thẻ màu, badge O và cảnh kết xanh |

Một **pre-comp** là một composition được đặt làm layer trong composition khác. Hai layer cùng dùng một pre-comp sẽ cập nhật cùng nhau. Vì vậy sửa `YOUR LOGO` sẽ cập nhật các vị trí dùng logo trong phần Blueprint. Các thẻ màu và hình O ở đoạn mở rộng là shape layer riêng.

Không đổi tên các comp gốc như `MAIN COMP`, `YOUR LOGO`, `YOUR TEXT `: expression của tác giả tham chiếu các tên đó.

## 3. Chỉnh artwork OPA

1. Mở `YOUR LOGO`.
2. Tìm ba layer `OPA_VECTOR_O`, `OPA_VECTOR_P`, `OPA_VECTOR_A`.
3. Mỗi layer là **Shape Layer** — Layer hình dạng. Mở **Contents → … path → Path** để chỉnh các điểm của chữ đó.
4. Khi chỉ muốn đổi kích thước toàn bộ logo, chọn cả ba layer và chỉnh cùng mức **Scale** — Tỷ lệ; không kéo riêng chiều ngang hoặc dọc. Nếu giữ hiệu ứng vệt sáng, chọn thêm ba layer `OPA_LIGHT_PASS_O/P/A` để chúng đổi cùng tỉ lệ, hoặc tắt mắt ba layer vệt sáng.
5. Layer `OPA_PNG_REFERENCE / Disabled` là ảnh gốc để đối chiếu. Có thể bật tạm để so sánh, rồi tắt trước khi xuất để tránh chồng hai phiên bản.

Các layer `OPA_LIGHT_PASS_O/P/A` tạo vệt sáng lướt ở khoảng 6–7,3s. Chọn một layer, nhấn U để xem keyframe opacity và mask. Tắt mắt cả ba layer nếu muốn logo giữ màu xanh phẳng trong suốt đoạn reveal.

Các đường shape được trace từ alpha của ảnh OPA đã cung cấp, không phải bộ vector AI/SVG chính thức. Artwork trong PNG gốc có vùng vẽ thực 732×221 px trên canvas 3082×1751. Bộ trace đã được đối chiếu theo mask trước khi đưa vào AE; khi cần hiệu chỉnh nhận diện ở mức brand guideline, dùng vector gốc được duyệt.

Nếu thay bằng logo khác: import ảnh/vector trong suốt bằng Ctrl+I, thêm vào `YOUR LOGO`, căn giữa canvas 1500×1500 và giữ tỉ lệ. Tắt ba layer OPA vector đang có. Cần chỉnh lại rulers và cảnh O icon ở đoạn mở rộng cho logo mới.

**Điểm kiểm tra:** riêng trong `YOUR LOGO`, OPA nằm giữa canvas; bề rộng bố cục khoảng 1360 trên canvas 1500, còn khoảng trống ở hai bên.

## 4. Sửa tagline

1. Mở `YOUR TEXT `.
2. Chọn layer `OPA_TAGLINE / Edit this text`.
3. Dùng công cụ **Horizontal Type Tool** — Công cụ chữ ngang, phím **Ctrl+T**; double-click dòng chữ rồi thay nội dung.
4. Bản hiện tại dùng “Marketing × Công nghệ × AI”, font Arial để có dấu tiếng Việt.
5. Nếu câu dài hơn, giảm **Font Size** — Cỡ chữ trong bảng Character; giữ nguyên tỉ lệ layer.
6. Mở lại `MAIN COMP` tại khoảng 8–9 giây và kiểm tra khoảng cách giữa logo với chữ.

Cảnh kết của brand film lấy nội dung chữ từ `YOUR TEXT ` bằng expression; phần style của dòng cuối được đặt riêng để dùng chữ trắng trên nền xanh.

## 5. Chỉnh màu và mức hiệu ứng của Blueprint

1. Mở `MAIN COMP`.
2. Chọn layer `CONTROL`, nhấn **F3** để mở **Effect Controls** — Bảng điều khiển hiệu ứng.
3. Kéo playhead đến marker tương ứng: **Setups 1**, **Setups 2**, **Setups 3**. Các marker là ghi chú mốc chỉnh của tác giả.

| Điều khiển | Ý nghĩa | Hướng chỉnh cho OPA |
|---|---|---|
| `RGB split ` | Tách kênh màu | Tắt để giữ nét rõ |
| `Camera lens blur` | Độ mờ ống kính | Giảm nếu cần logo rõ sớm hơn |
| `Logo line width ` | Bề dày nét vẽ | Điều chỉnh vừa đủ đọc ở Full HD |
| `Logo line color` | Màu contour | OPA Blue `#0068FF` |
| `Logo line_echo intensity ` | Cường độ vệt nét | Giữ thấp để không rối hình O/P/A |
| `Logo line_echo quantity` | Số lớp vệt | 2 là điểm bắt đầu của bản này |
| `Rulers intensity` | Cường độ đường đo | Có keyframe giảm dần trước cảnh kết |
| `Auxiliary lines intensity` | Đường phụ | Có keyframe giảm dần |
| `Grid intensity ` | Lưới | Có keyframe giảm về 0 để cảnh kết thoáng |
| `Text intensity` | Độ hiện của chữ | 100 khi dùng tagline |
| `Text color` | Màu tagline | Màu tối trên nền sáng |
| `Text position ` | Vị trí tagline | Xem trực tiếp ở 8–9s rồi kéo điểm điều khiển |
| `Background color` | Hai màu ánh xạ nền | Hai tông sáng, thiên xanh rất nhẹ |

Một số tên hiệu ứng có khoảng trắng cuối do file gốc; giao diện nhìn gần như giống nhau. Khi sửa bằng tay, chọn theo nhãn trong Effect Controls.

Các slider có stopwatch xanh đã có keyframe. Để đổi mức cho cả đoạn, chọn các keyframe liên quan; thay một giá trị tại một thời điểm có thể chỉ tạo/sửa một keyframe.

## 6. Chỉnh đường dựng theo hình OPA

1. Mở `ALL RULERS`.
2. Các layer `RULER`, `RULER 2`, `RULER (PROTRACTOR)…`, `RULER (RADIUS)…` của logo demo đã được tắt mắt.
3. Các layer `OPA_RULER_1` đến `OPA_RULER_6` là đường dựng mới. Mở **Contents → Editable path → Path** để sửa đầu mút.
4. `OPA_LABEL_W` và `OPA_LABEL_H` là nhãn chữ có thể sửa.
5. Mở `MAIN COMP` ở khoảng 3–4s để xem đường dựng cùng góc camera thực tế.

Nếu muốn dùng lại bộ thước gốc của tác giả: bật mắt thước cần dùng trong `ALL RULERS`, mở comp `RULER…` tương ứng, chọn `CONTROL ` và nhấn F3. Chỉnh `Ruler_position`, `Ruler_rotation`, các `Auxiliary lines_position_*` và độ dài. Chỉnh ở cuối phần animation của thước như PDF của tác giả hướng dẫn. Không bật tất cả thước cùng lúc nếu chưa căn lại theo OPA.

## 7. Chỉnh bản brand film 16 giây

Mở `OPA_16s_BRAND_FILM_1920x1080` và dùng các marker trên timeline:

1. **0–10s:** layer `01_BLUEPRINT_10s / Shared source` dùng chung nguồn intro. Sửa engine và tagline ở các comp gốc.
2. **10–12,3s:** sửa màu trong `CARD_OPA Blue`, `CARD_OPA White`, `CARD_OPA Ink`; sửa tên màu trong các layer `LABEL_…`.
3. **12,3–13,5s:** `O_ICON_BADGE` là nền tròn; `OPA_O_ICON` là chữ O dạng shape.
4. **13,5–16s:** `BG_FINAL_BLUE`, ba layer `FINAL_OPA_*` và `TXT_FINAL_TAGLINE` là cảnh kết.
5. Nhấn **U** trên layer để hiện các thuộc tính có keyframe; nhấn **UU** để xem các thuộc tính đã thay đổi.

Đoạn bảng màu/badge/cảnh kết lấy nhịp và ý tưởng triển khai nhận diện từ video tham chiếu. Phần đầu vẫn giữ engine Blueprint của file người dùng cung cấp.

## 8. Audio và xuất video

Audio nằm ở các layer `SFX / …` và trong Assets. Đây là sound-design hướng dẫn tự tạo. Có thể tắt biểu tượng loa để thay bằng audio khác.

1. Mở comp cần xuất.
2. Nhấn **Ctrl+M** — Add to Render Queue, thêm vào hàng đợi xuất.
3. Chọn **Best Settings**, **Resolution: Full**, 30 fps.
4. Chọn **H.264 - Match Render Settings - 15 Mbps** trong Output Module trên AE hiện tại.
5. Chọn file đích trong `Exports`, nhấn **Render**.

Với bản 4K, xuất `MAIN COMP` thay vì comp Full HD. Nếu muốn audio đi cùng bản 4K, thêm audio vào một wrapper 3840×2160 hoặc ghép audio sau khi xuất; `MAIN COMP` gốc là engine hình.

## 9. Kiểm tra nhanh trước khi dùng

- Không có color bars hoặc báo thiếu footage.
- OPA giữ đúng tỉ lệ, khoảng rỗng O/P không bị lấp.
- Tagline đủ dấu tiếng Việt và không cắt chữ.
- Không có đoạn đen giữa các cảnh 10s, 12,3s và 13,5s của bản dài.
- Giữ cảnh kết đủ lâu để đọc; dùng bản 10s khi cần mở đầu, bản 16s khi trình bày nhận diện.
- Chỉ chuyển cả thư mục project cùng Assets; không chuyển mỗi file `.aep` sang máy khác.

Chi tiết đối chiếu video gốc nằm trong `PHAN-TICH-VIDEO-VA-KICH-BAN.md`.
