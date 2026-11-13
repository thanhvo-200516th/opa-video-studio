# Hướng dẫn dựng intro logo OPA từ 3 template

**Dành cho After Effects trên Windows · Kiểm tra file ngày 21/10/2026 · AE 2026 / 26.3**

## 1. Nên bắt đầu từ mẫu nào?

**Dùng template 1 - Abstract Techno Logo Reveal làm bản chính.** Nét sáng, các lớp chiều sâu, camera và vệt highlight của mẫu này phù hợp nhất với phần logo có khối trong video tham chiếu. Dùng template 3 khi muốn nhấn vào công nghệ/AI bằng lớp mã và lưới. Template 2 phù hợp với một phiên bản HUD, có vòng và hình lục giác bao quanh logo.

Hướng dẫn này có ba phần thực hành thay logo riêng và một cách dựng video OPA dài 16 giây. Bạn nên hoàn tất template 1 trước, sau đó dựng các cảnh nhận diện ở mục 9. Mục 7 và 8 giúp làm thêm hai phương án khác.

| Bộ trong thư mục của bạn | File nên mở trên AE 2026 | Comp kết quả đã kiểm tra | Thông số gốc | Vai trò đề xuất |
|---|---|---|---|---|
| Template 1 / Abstract Techno Logo Reveal | `Abstract Techno Logo Reveal 25.x.aep` | `## RENDER THIS` | 3840×2160, 30 fps, 10s | Intro chính: nét, chiều sâu, highlight |
| Template 2 / Sci-fi Logo | `Sci-fi Logo.aep` | `_MAIN COMP` | 1920×1080, 29,97 fps, khoảng 12,012s | Phương án HUD / vòng công nghệ |
| Template 3 / FRA - Digital Sci-fi Coding Logo Reveal | `FRA - Digital Coding Logo Reveal (Universalized Expression).aep` | `Digital Code Logo Reveal - Render HD (1920x1080)` | HD, 30 fps, 10,033s; có bản 4096×2160 | Phương án lớp mã / camera / lưới |

Ba file 18.x, 23.x, 25.x trong template 1 là các bản tương thích của cùng bộ, không phải ba mẫu khác nhau. Cả ba có 44 project item và 23 comp. Template 3 có bản thường và bản Universalized Expression; bản Universalized dùng các tham chiếu expression thuận tiện hơn khi khác ngôn ngữ giao diện. Không import đồng thời cả hai phiên bản của cùng một bộ.

### Nguồn đã đọc

Thư mục gốc: `/media/vmiz/Over Powers/video AE/template intro/template giải nén`.

Đã kiểm tra 6 file `.aep` bằng After Effects, 2 PDF của template 1, video hướng dẫn của template 2 và 3, các readme và các file ảnh/vector đi kèm. Readme của template 3 đang trống. Các footage đang được tham chiếu trong ba bộ đều có file tại thư mục đã giải nén.

Các tên bên dưới lấy từ project thật. Những con số trong bảng **preset OPA đề xuất** là điểm bắt đầu để dựng; không phải thông số trong bộ nhận diện chính thức.

## 2. Video Download.mp4 thực sự đang làm gì?

Nguồn: `/media/vmiz/Over Powers/THÀNH V/Download.mp4`. Video có hình 576×1024, 30 fps, **478 frame**, phần hình dài 15,933s. Đây là video quay màn hình đang chạy motion logo Framer. Khung dọc còn chứa màn hình AE, phối cảnh máy quay, phản chiếu đèn và watermark; phần logo bên trong màn hình mới là tham chiếu chuyển động.

Đã xem lại toàn bộ 478 frame. Frame được đánh số từ 0; các mốc chuyển động mềm có sai số quan sát khoảng 1-2 frame. Các mốc cắt rõ như frame 50, 214, 244, 259, 304, 334, 349, 379 và 439 có thể mở lại trong thư mục `Images/Reference`.

| Mốc trong nguồn | Frame | Hình ảnh / dạng motion | Áp dụng vào OPA |
|---|---|---|---|
| 0-1,633s | 0-49 | Điểm, đoạn thẳng dựng dần icon trên nền xanh | Lấy cách vẽ contour; cần artwork O/P/A của OPA |
| 1,667-3,100s | 50-93 | Cắt sang nền tối, logo sáng có cảm giác khối | Template 1: camera và các lớp extrusion/gloss |
| 3,133-4,100s | 94-123 | Một phần logo xanh, xuất hiện đường và nhãn | Chọn bảng xanh OPA; giữ lớp phụ vừa phải |
| 4,133-5,600s | 124-168 | Vệt sáng, góc nghiêng, bloom/flash; đỉnh sáng khoảng 4,7s | Template 1 có highlight và chiều sâu; giảm cường độ nếu mất khoảng rỗng O/P |
| 5,633-6,600s | 169-198 | Glow xanh bùng lên rồi giảm thành contour | Giữ một nhịp sáng rõ, sau đó trả logo về màu đọc được |
| 6,633-7,100s | 199-213 | Icon thu nhỏ về giữa, settle | Giảm chuyển động trước đoạn nhận diện |
| 7,133-9,100s | 214-273 | Wordmark trên nền sáng, xanh nhạt, tối rồi xanh đậm | Dựng 4 biến thể nền, mỗi biến thể khoảng 0,5s |
| 9,133-10,100s | 274-303 | Typography phóng lớn, trượt ngang, chồng nhiều lớp | Dùng chính artwork OPA phóng lớn và trượt; giữ nguyên tỉ lệ |
| 10,133-11,100s | 304-333 | Các thẻ màu | Dựng shape card Blue / White / Ink |
| 11,133-11,600s | 334-348 | Icon phẳng trên nền sáng | Dùng chữ O từ artwork, căn giữa |
| 11,633-12,600s | 349-378 | Icon quang học, viền màu trên nền xanh | Có thể dùng một vệt sáng ngắn; màu OPA vẫn là màu chính |
| 12,633-14,600s | 379-438 | Badge tròn biến dạng thành một chiếc mũ | Bản OPA hướng dẫn ở đây dùng badge O; phần mũ cần thêm asset/mockup 3D riêng |
| 14,633-15,433s | 439-463 | Đổi nền xanh, vật thể xoay/rời khung | Kết bằng wordmark OPA trắng trên nền xanh |
| 15,467-15,900s | 464-477 | Quay lại điểm/nét đầu để loop | Tùy mục đích, giữ logo cuối để ghép nội dung hoặc làm loop riêng |

Ba template mới cung cấp engine reveal và các lớp kỹ thuật. Các cảnh biến thể nền, chữ lớn, thẻ màu, badge và cảnh kết được dựng thêm bằng shape/text/pre-comp trong AE. Riêng phép biến dạng thành mũ trong nguồn là một hạng mục asset/3D khác.

![Bảng mốc tham chiếu](Images/reference-keyframes.jpg)

## 3. Chuẩn bị đúng logo OPA

### 3.1. Dùng file nào?

Bộ hướng dẫn có các PNG trong suốt được căn gọn từ artwork OPA đã cung cấp, giữ nguyên hình O/P/A:

| File trong `Assets` | Dùng khi nào |
|---|---|
| `OPA-blue-1500x500.png` | Thay logo trong cả ba template; nền sáng hoặc hiệu ứng giữ màu nguồn |
| `OPA-white-1500x500.png` | Logo trắng trên nền xanh/tối và cảnh kết |
| `OPA-ink-1500x500.png` | Logo tối trên nền trắng/xanh nhạt |
| `OPA-O-white-512x512.png` | Icon O trắng trong badge |

PNG gốc có canvas 3082×1751 nhưng vùng artwork thực chỉ khoảng **732×221**, tại bounding box `(1175,765)-(1907,986)`. Template 1 tự fit theo kích thước canvas, vì vậy dùng nguyên PNG gốc sẽ làm logo nhìn rất bé. Các PNG 1500×500 trong bộ này có artwork rộng khoảng 1440 px, còn một ít khoảng trống để không sát mép.

PNG được xuất qua AE để giữ alpha. Đây là artwork raster được căn lại, không phải vector AI/SVG gốc. Khi có vector thương hiệu chính thức, có thể thay source tương ứng và kiểm tra lại độ dày nét.

### 3.2. Màu và chữ dùng cho bản dựng

| Thành phần | Giá trị đề xuất |
|---|---|
| Xanh OPA | `#0068FF` |
| Trắng | `#FFFFFF` |
| Nền tối cho reveal | `#04060D` hoặc `#0B1220` |
| Nền sáng | `#F7F9FC` |
| Highlight xanh nhạt | `#59BFFF` |
| Tagline bản dựng | `Marketing × Công nghệ × AI` |
| Font tagline dễ dùng | Arial Regular, có dấu tiếng Việt |

Wordmark OPA luôn dùng file artwork. Không gõ chữ OPA bằng font thay thế. Tagline trên là phương án cho video, bạn có thể đổi theo câu được doanh nghiệp duyệt.

### 3.3. Tạo bản làm việc

1. Tạo thư mục `/media/vmiz/Over Powers/video AE/OPA-INTRO-WORK` và các folder `Assets`, `Projects`, `Exports`.
2. Copy các PNG OPA cần dùng vào `Assets`.
3. Khi mở từng template, dùng **File → Save As → Save As…** để lưu bản làm việc vào `Projects`, ví dụ `OPA_T1_Abstract.aep`, `OPA_T2_HUD.aep`, `OPA_T3_Digital.aep`.
4. Nếu AE hỏi chuyển phiên bản project, mở và lưu thành bản làm việc nói trên.
5. Mở comp kết quả, chọn **Fit** - Vừa khung và **Half/Quarter** - Một nửa/Một phần tư khi chỉnh; xuất ở Full.

**Điểm kiểm tra:** file đang chỉnh có tên OPA trong `Projects`; nguồn template và thư mục Footage vẫn còn nguyên.

## 4. Những thao tác AE cần hiểu trước

| Nhãn / phím | Nghĩa và tác dụng |
|---|---|
| Project | Bảng danh sách file và composition |
| Composition / comp | Khung hình và timeline của một cảnh |
| Pre-comp | Một comp được đặt làm layer trong comp khác |
| Effect Controls / F3 | Bảng điều khiển hiệu ứng của layer đang chọn |
| S / P / T / R | Scale - Tỷ lệ / Position - Vị trí / Opacity - Độ hiện / Rotation - Góc xoay |
| U / UU | Hiện thuộc tính có keyframe / hiện các thuộc tính đã thay đổi |
| Stopwatch | Đồng hồ bật/tắt keyframe của một thuộc tính |
| F9 / Easy Ease | Làm chuyển động tăng/giảm tốc mềm ở keyframe đã chọn |
| Ctrl+I | Import - Nhập file, kể cả một project `.aep` khác |
| Ctrl+N / Ctrl+K | Tạo comp mới / mở thông số comp hiện tại |
| Ctrl+T | Horizontal Type Tool - Công cụ chữ ngang |
| Ctrl+M | Add to Render Queue - Thêm comp vào hàng đợi xuất |

**Layer trực tiếp và pre-comp khác nhau thế nào?** Khi Ctrl+D một layer PNG/shape/text, mỗi bản có transform hoặc nội dung layer riêng. Khi Ctrl+D một layer pre-comp trong timeline, các bản vẫn cùng đọc một comp nguồn. Sửa bên trong nguồn sẽ đổi cả hai. Muốn một cảnh khác nội dung, duplicate comp trong bảng Project rồi dùng comp mới. Nếu comp mới còn chứa các pre-comp con dùng chung thì các phần con đó vẫn liên kết.

Các tên gốc như `## RENDER THIS`, `SOURCE`, `Digital Code Logo Reveal` được expression tham chiếu. Đặt tên OPA cho master mới hoặc folder bao ngoài; giữ các tên nội bộ của template.

## 5. Template 1 - Dựng bản OPA chính

### 5.1. Mở đúng file và comp

Đường dẫn: `/media/vmiz/Over Powers/video AE/template intro/template giải nén/template 1/Abstract Techno Logo Reveal/Abstract Techno Logo Reveal 25.x.aep`.

1. Nhấn Ctrl+O, mở file trên; lưu bản OPA bằng Save As.
2. Trong bảng Project, double-click **`## RENDER THIS`**.
3. Kéo playhead đến khoảng 4-5s để thấy đoạn reveal; đến 8-9s để xem logo gần hoàn thiện.

**Điểm kiểm tra:** comp 3840×2160, 30 fps, 10 giây. Trong timeline có layer `Settings` và `MAIN `.

### 5.2. Thay logo ở đúng chỗ

1. Trong bảng Project tìm **`## LOGO REPLACE`**. Đây là **footage ảnh**, không phải comp.
2. Right-click nó → **Replace Footage → File…** - Thay file nguồn.
3. Chọn `OPA-blue-1500x500.png` trong Assets.
4. Quay lại `## RENDER THIS` ở 8-9s.

Template dùng comp `SOURCE` 3840×3840 để auto fit; expression fit theo chiều rộng/chiều cao của file nguồn. Không thêm một PNG OPA nằm đè lên comp kết quả: cách đó chỉ tạo logo phẳng ở trên, các lớp chiều sâu bên dưới vẫn lấy logo demo.

**Điểm kiểm tra:** silhouette trong các lớp nét và khối đều là O/P/A; không còn hình AP của demo.

### 5.3. Chỉnh kích thước và bảng màu

1. Trong `## RENDER THIS`, chọn layer **`Settings`**, nhấn **F3**.
2. Chỉnh theo bảng này. Đây là preset đã được lưu thử để kiểm tra hướng dẫn; có thể tinh chỉnh sau khi xem chuyển động.

| Tên control chính xác | Giá trị bắt đầu cho OPA | Cách dùng |
|---|---|---|
| `Logo Scale` | 150 | Nếu logo quá lớn lúc camera đến gần, giảm từng bước 10; giữ hai chiều đồng đều |
| `Line Thickness` | 7 | Tăng lên 8-10 nếu nét bị mất ở Full HD; giảm nếu lỗ O/P bị bít |
| `Dropdown Menu Control` | 1 - Custom Color | 1 dùng màu custom; 2 lấy màu từ nguồn |
| `Color 1` | `#0068FF` | Màu chính của các lớp hiệu ứng |
| `Color 2` | `#59BFFF` | Màu highlight, giữ sáng hơn màu chính |
| `Floor Colour` | `#04060D` | Màu sàn/nền tối của hiệu ứng |
| `Text Position` | Bắt đầu từ `[1500,600]` | Điều khiển trong comp chữ; xem trực tiếp trước khi đổi |

Bạn cũng có thể dùng panel **Essential Graphics** khi có trong giao diện: chọn primary comp `## RENDER THIS`, sẽ thấy LOGO SCALE, LOGO REPLACE, TEXT REPLACE và nhóm Settings. PDF gốc có hình minh họa panel đồ họa; đường `Settings → F3` ở trên là cách chỉnh trực tiếp đã đối chiếu với file `.aep`.

Chỉ chọn menu/màu ở control gốc; không cần vào comp `3D ` với hơn 100 lớp FX để đổi từng lớp.

### 5.4. Sửa tagline và font

1. Mở comp **`TEXT`** trong bảng Project.
2. Chọn layer **`Lorem Ipsum 3`**.
3. Dùng Ctrl+T để thay thành `Marketing × Công nghệ × AI`.
4. Chọn font **Arial Regular**, cỡ bắt đầu **60** trong comp TEXT.
5. Mở lại `## RENDER THIS`, xem ở 8-9s. Nếu dài quá, giảm font size; điều chỉnh vị trí bằng `Settings → Text Position`.

Font gốc của câu demo là `Between1-Medium`; không cần cài font này để giữ logo OPA vì wordmark là artwork. PDF gốc cũng ghi nhạc preview được tải riêng, không có trong bộ này.

### 5.5. Kiểm tra trước khi dựng tiếp

- 2s: đã bắt đầu nhìn ra contour OPA.
- 4-5s: hình vẫn còn khoảng rỗng ở O/P, highlight không làm logo thành một mảng trắng.
- 7s: các lớp khối và camera không cắt mất đầu/cuối wordmark.
- 9s: logo và tagline đọc được, không còn Lorem Ipsum.

Nếu viền đỏ/xanh lá của demo quá mạnh: mở `MAIN ` → chọn `Adjustment Layer 8` → F3 → tắt riêng hiệu ứng **`3D Glasses`** bằng nút fx cạnh hiệu ứng, rồi so sánh lại. Control màu ở Settings không loại bỏ hoàn toàn hiệu ứng tách kênh này. Giữ hoặc giảm tùy phong cách bạn muốn.

![Template 1 - khung kiểm tra OPA](Images/T1-OPA-preview.png)

Ảnh trên là một frame kiểm tra setup, không đại diện cho toàn bộ 10 giây chuyển động.

## 6. Cách dùng bản template 1 trong video hoàn chỉnh

**Bản intro đơn:** giữ nguyên 10s của `## RENDER THIS`. Tạo comp mới `OPA_INTRO_T1_HD`, 1920×1080, 30 fps, 10s. Kéo `## RENDER THIS` vào và đặt Scale **50%**, Position `[960,540]`. Đặt audio ở comp mới này.

**Bản nhận diện 16s giống nhịp tham chiếu hơn:** dùng engine 10s làm phần đầu 7,2s, rồi thêm biến thể màu, chữ lớn, thẻ màu và badge. Cách dựng nằm ở mục 9. Đây là lựa chọn dựng nhịp, không sửa trực tiếp tốc độ của từng camera trong template.

Nếu cần xem lại video tutorial của hai bộ còn lại, mốc hướng dẫn tương ứng được liệt kê trong phần của từng bộ. Đó là thời gian trong video **hướng dẫn thao tác**, không phải thời gian của animation đầu ra.

## 7. Template 3 - Phương án Digital / AI

### 7.1. Mở và nhận diện các comp

Đường dẫn: `/media/vmiz/Over Powers/video AE/template intro/template giải nén/template 3/FRA - Digital Sci-fi Coding Logo Reveal/FRA - Digital Coding Logo Reveal (Universalized Expression).aep`.

| Tên comp/layer | Việc cần làm |
|---|---|
| `Your Logo` | Thay artwork và câu `envato.com` |
| `Digital Code Logo Reveal → Color Control` | Đổi màu các thành phần được nối với control |
| `Digital Code Logo Reveal - Render 4K (4096x2160) → CC` | Màu nền/ánh sáng phụ và Curves |
| `Digital Code Logo Reveal - Render HD (1920x1080)` | Comp HD để preview/xuất |
| `Overlay Codes`, `Overlay Codes 2` | Các dòng mã và hình kỹ thuật |
| `glass texture` | Texture kính; cần giữ file DirtWindowStains… đi kèm |

### 7.2. Thay logo mà không giữ nhầm Scale của EPS demo

1. Lưu bản làm việc OPA.
2. Mở **`Your Logo`**, canvas 4096×2160.
3. Ctrl+I nhập `OPA-blue-1500x500.png`; kéo file vào comp.
4. Đặt Position **`[2048,1080]`**, Scale **112,5%** ở cả hai chiều. Artwork rộng khoảng 1620 px là điểm bắt đầu phù hợp với khung logo demo.
5. Đặt layer mới chạy hết comp Your Logo, khoảng 16,44s.
6. Tắt mắt layer **`EnvatoLogoLight.eps`**.
7. Giữ `SAFE AREA` làm guide; guide không xuất ra video. Layer `Shape Layer 1` của bản gốc đang tắt.

EPS demo đang có Scale khoảng **575,44%** vì kích thước nguồn EPS nhỏ. Nếu Alt-kéo một PNG lớn vào đúng layer EPS rồi giữ Scale ấy, logo mới sẽ phóng quá mức. Cách thêm layer mới và đặt số ở trên tránh lỗi đó.

**Điểm kiểm tra:** logo vừa vùng SAFE AREA, đúng tỉ lệ; trong comp `Digital Code Logo Reveal` các lớp bóng, contour và khối đều lấy OPA từ cùng pre-comp `Your Logo`.

### 7.3. Đổi chữ và màu

1. Trong `Your Logo`, sửa layer **`envato.com`** thành tagline; bắt đầu với Arial Regular, cỡ **90** trong comp gốc.
2. Giữ animation Anchor Point/Opacity vốn có của layer chữ. Chọn layer, nhấn U để xem trước khi thay transform.
3. Mở `Digital Code Logo Reveal`, chọn **`Color Control`** → F3.
4. Đặt **`Color Control 1`** thành `#0068FF`.
5. Mở comp render 4K, chọn **`CC`** → F3. Đổi năm màu nền theo tông xanh tối để bỏ mảng cam/tím demo.

| Control của CC | Preset OPA đề xuất |
|---|---|
| `Background Color 01` | `#081F40` |
| `Background Color 02` | `#05142E` |
| `Background Color 03` | `#04060D` |
| `Background Color 04` | `#0A2E59` |
| `Background Color 05` | `#051A42` |

`Curves` trong CC có keyframe sẵn, vì vậy trước tiên giữ nguyên. Nếu hình tối quá, tăng dần nền hoặc chỉnh Curves sau khi nhìn cả đoạn, tránh đổi toàn bộ nền thành xanh sáng cùng lúc làm mất nét logo.

### 7.4. Làm bớt rối cho thương hiệu doanh nghiệp

Trong `Digital Code Logo Reveal`, các layer `Overlay Codes` và `Overlay Codes 2` có thể giảm Opacity hoặc tắt từng layer để so sánh. Để giữ cảm giác AI mà logo vẫn nổi, bắt đầu với 40-60% ở các lớp mã đang hiện. Đây là mức đề xuất về thiết kế, không phải slider tổng có sẵn trong template.

Mở comp render HD ở khoảng 5s và 9s để kiểm tra camera, logo, tagline và nền. Nguồn 4K là **4096×2160**, khác 3840×2160. Wrapper HD có Scale 50%, nghĩa là hình nguồn rộng 2048 và được cắt nhẹ hai bên trong canvas 1920. Giữ chữ/logo trong SAFE AREA khi dùng bản HD.

Các comp logo/background gốc có cả 25 fps; comp render là 30 fps. Giữ cấu trúc này khi sửa nguồn, không đổi hàng loạt mọi pre-comp sang 30 fps.

![Template 3 - khung kiểm tra OPA](Images/T3-OPA-preview.png)

Mốc trong `help.mp4`: 20-60s thay logo/chữ; 80-110s xem màu/nét; 120-170s chỉnh nền/Curves; 180-220s chuyển sang comp render và xuất. Xem lại các ảnh hướng dẫn trong `Images/Tutorials/T3-sheet-1.jpg` và `T3-sheet-2.jpg`.

## 8. Template 2 - Phương án HUD

Đường dẫn: `/media/vmiz/Over Powers/video AE/template intro/template giải nén/template 2/Sci-fi Logo/Sci-fi Logo.aep`.

### 8.1. Thay logo

1. Mở file và Save As bản OPA.
2. Mở **`EDIT YOUR LOGO HERE`**, canvas 1000×1000.
3. Import/kéo `OPA-blue-1500x500.png` vào comp.
4. Đặt Position **`[500,500]`**, Scale **60%**. Canvas ảnh rộng 900 px; artwork thực rộng khoảng 864 px.
5. Cho layer chạy hết comp, khoảng 10,01s. Layer `Instructions` vốn đang tắt, giữ tắt.
6. Mở `_MAIN COMP` và xem lúc camera nghiêng khoảng 3-5s, sau đó lúc kết 9-11s.

Nếu dùng icon O thay vì cả wordmark trong HUD, dùng icon nguồn riêng và chỉnh lại Scale để vừa vòng. Với bản OPA doanh nghiệp, wordmark đầy đủ giúp người xem nhận tên thương hiệu ngay.

### 8.2. Chỉnh đúng CONTROLLERS

Trong **`_MAIN COMP`**, chọn layer **`CONTROLLERS`** → F3.

| Control đúng tên | Giá trị / thao tác cho OPA |
|---|---|
| `Use Logo Original Color` | Bật khi dùng PNG OPA xanh; lúc này nguồn quyết định màu logo |
| `Logo Color` | `#0068FF`; muốn control này tô lại logo thì tắt Use Logo Original Color |
| `Disable URL` | Để tắt nếu dùng tagline trong template; bật nếu muốn bỏ hẳn dòng phụ |
| `Disable Lights` | Bắt đầu tắt; bật nếu cần xem phiên bản ít ánh sáng |
| `Lights Color` | `#59BFFF` |
| `Lines Color` | `#0068FF` |
| `Background Grid` | `#0F2647` |
| `Background Dots 01` | `#0F2647` |
| `Background Dots 02` | `#0068FF` |

Không phải đổi `Logo Color` là chắc chắn đổi logo: checkbox giữ màu gốc là điểm quyết định. Video tutorial minh họa đúng việc chuyển màu logo ở vùng 140-170s.

### 8.3. Sửa dòng URL thành tagline

1. Mở **`EDIT YOUR URL HERE`**, canvas 1000×100.
2. Sửa layer **`www.yourwebsite.com`** thành `Marketing × Công nghệ × AI`.
3. Chọn Arial Regular, cỡ bắt đầu **27**; giữ câu nằm trong chiều ngang 1000 px và chiều cao 100 px.
4. Giữ `Instructions` tắt.
5. Quay về `_MAIN COMP`, xem ở đoạn cuối nơi URL được hiển thị.

Font HUD nhỏ trong bản gốc là `BebasNeueBook`, câu URL là `CenturyGothic`. Nếu báo thiếu font, có thể thay text phụ bằng Arial/Arial Narrow đang có trên máy và kiểm tra tràn dòng. Hình logo OPA vẫn lấy từ PNG, không phụ thuộc font này.

Template 2 dùng **29,97 fps**, khoảng **12,012s**. Giữ nguyên comp gốc khi chỉnh. Nếu đưa vào master 30 fps, AE lấy mẫu theo timeline master; không cần đổi trực tiếp toàn bộ engine HUD.

![Template 2 - khung kiểm tra OPA](Images/T2-OPA-preview.png)

Mốc trong `How to use this template.mp4`: 30-90s nhập và đặt logo; 100-130s sửa URL; 130-180s các controller; 180-221s thử logo/URL ở đoạn kết. Readme cũng chỉ rõ ba comp cần sửa: `_MAIN COMP`, `EDIT YOUR LOGO HERE`, `EDIT YOUR URL HERE`.

## 9. Dựng video nhận diện OPA 16 giây theo nhịp tham chiếu

Đây là kịch bản thực hành hoàn chỉnh bằng template 1 và các cảnh native AE. Template 2 hoặc 3 có thể thay phần reveal khi bạn muốn một phong cách khác. Nếu muốn dùng cả ba, xem cách ghép tùy chọn ở mục 10.

### 9.1. Tạo master và đặt nhịp

1. Sau khi sửa xong template 1, tạo comp mới **`OPA_MASTER_16S`** bằng Ctrl+N.
2. Đặt Width 1920, Height 1080, Pixel Aspect Square Pixels, Frame Rate 30, Duration 16 giây.
3. Kéo `## RENDER THIS` vào master, Scale 50%, Position `[960,540]`.
4. Right-click layer đó → **Time → Time Stretch…** - Co giãn thời gian. Đặt Stretch Factor **72%**, giữ đầu layer ở 0. Engine 10s sẽ chạy trong 7,2s.
5. Đặt tên layer ngoài là `01_REVEAL_T1`. Giữ tên comp nguồn như cũ.

| Timeline master | Frame 30 fps, mốc cuối không tính | Cảnh | Nguồn |
|---|---|---|---|
| 0-7,2s | 0-215 | Nét, khối, highlight, camera rồi settle | Template 1, Time Stretch 72% |
| 7,2-9,2s | 216-275 | 4 biến thể logo/nền, mỗi biến thể 0,5s | Comp `OPA_COLOR_VARIANTS` |
| 9,2-10,2s | 276-305 | Artwork lớn trượt ngang, một nhịp chuyển mạnh | Comp `OPA_KINETIC` |
| 10,2-11,6s | 306-347 | 3 thẻ màu | Comp `OPA_PALETTE` |
| 11,6-13,6s | 348-407 | Icon O trên badge | Comp `OPA_BADGE` |
| 13,6-16s | 408-479 | Logo trắng trên xanh, tagline và giữ cảnh kết | Comp `OPA_FINAL` |

Tạo mỗi comp cảnh mới ở 1920×1080/30 fps với đúng thời lượng của cảnh. Trong master, kéo từng comp vào, đưa playhead đến mốc bắt đầu và nhấn **`[`** để đưa đầu layer tới đó. `[` di chuyển layer; **Alt+`[` / Alt+`]`** cắt đầu/cuối layer. Nhấn U để kiểm tra keyframe trước khi dùng phím cắt.

Vì phần reveal đã được tăng tốc, hãy RAM Preview cả đoạn 0-7,2s. Nếu muốn chuyển động chậm và sang hơn, dùng bản reveal đủ 10s và kéo dài master; thứ tự các cảnh nhận diện giữ nguyên.

### 9.2. Cảnh 4 biến thể nền, 2 giây

1. Tạo `OPA_COLOR_VARIANTS`, dài 2s.
2. Tạo 4 cặp layer background + PNG logo. Mỗi cặp xuất hiện trong 0,5s liên tiếp: 0-0,5; 0,5-1; 1-1,5; 1,5-2.
3. Các nền dùng solid bằng **Layer → New → Solid…**. Các logo là PNG riêng, đặt giữa `[960,540]`, Scale khoảng **60%**; artwork rộng khoảng 864 px.
4. Cặp 1: nền trắng, logo xanh. Cặp 2: nền `#EAF3FF`, logo tối. Cặp 3: nền `#0B1220`, logo trắng. Cặp 4: nền `#0068FF`, logo trắng.
5. Dùng hard cut giữa các cặp để giữ nhịp nhanh. Không thêm 4 transition dài làm mềm hết cảm giác đổi biến thể.

**Điểm kiểm tra:** cả 4 logo nằm đúng cùng tâm và có cùng bề rộng. Không co một bản theo chiều ngang chỉ để vừa câu chữ.

### 9.3. Cảnh artwork lớn trượt ngang, 1 giây

1. Tạo `OPA_KINETIC`, nền xanh OPA, dài 1s.
2. Thêm PNG OPA trắng, Scale **160%** để artwork rộng khoảng 2304 px, lớn hơn khung.
3. Bật stopwatch Position. Đặt ba keyframe: **0s `[2500,540]`**, **0,2s `[960,540]`**, **1s `[-1500,540]`**.
4. Chọn các keyframe → F9. Preview; tăng tốc ra khung nếu thấy logo dừng lâu.
5. Ctrl+D layer hai lần. Lùi hai bản sau lần lượt **2 frame và 4 frame**, giảm Opacity còn **25% và 12%** để có cảm giác chồng lớp; bật Motion Blur của layer và của comp.

Đây là chuyển động artwork, không phải gõ chữ OPA bằng font. Nếu quá rối, giữ một layer chính và một bản trễ.

### 9.4. Cảnh bảng màu, 1,4 giây

1. Tạo `OPA_PALETTE`, nền `#F7F9FC`, dài 1,4s.
2. Bỏ chọn mọi layer rồi dùng Rounded Rectangle Tool để tạo 3 **shape layer** riêng. Nếu đang chọn PNG, công cụ vẽ có thể tạo mask thay vì shape.
3. Mỗi card khoảng **300×440**, bo góc **18**; tâm ở **`[620,500]`, `[960,500]`, `[1300,500]`**. Màu lần lượt Blue, White, Ink.
4. Tạo text Arial 24 dưới card ở y=790: `OPA Blue`, `OPA White`, `OPA Ink`. Card trắng có thể thêm stroke `#DDE5EF`, 2 px để tách khỏi nền.
5. Với mỗi card và nhãn, animate Position từ y=650 tới y=500 và Opacity 0→100 trong **0,25s**. Cho card 2 trễ **3 frame**, card 3 trễ **6 frame**.
6. Giữ đủ tới khoảng 1,1s; trong 0,3s cuối kéo lên thêm 50 px và fade out.

**Điểm kiểm tra:** thứ tự xanh-trắng-tối rõ ràng; text không dính vào cạnh card. Căn các nhãn theo tâm card, không căn theo bề rộng chữ.

### 9.5. Badge O, 2 giây

1. Tạo `OPA_BADGE`, nền sáng, dài 2s.
2. Vẽ ellipse **420×420**, Fill `#0068FF`, Position `[960,540]`.
3. Thêm icon `OPA-O-white-512x512.png`, đặt tâm `[960,540]`; bắt đầu Scale **60%**. Chỉnh nhỏ hơn nếu khoảng xanh quanh O bị hẹp.
4. Nếu chỉ có wordmark, dùng mask để chỉ giữ chữ O trong một pre-comp riêng, sau đó căn lại Anchor Point vào giữa O trước khi animate Scale.
5. Pre-compose circle và icon thành `OPA_BADGE_GROUP`, chọn **Move all attributes into the new composition** - Chuyển thuộc tính vào comp mới.
6. Animate Scale nhóm ở local 0s=70%, 0,35s=100%, 1,6s=100%, 2s=130%; Opacity 0→100 trong 0,2s, giữ, rồi fade trong 0,2s cuối. Dùng F9.

Giữ cả circle và O trong cùng nhóm để khi scale, hai phần đi cùng nhau. Đây là ứng dụng nhận diện dạng badge, thay cho cảnh biến dạng thành mũ trong video nguồn.

### 9.6. Cảnh kết xanh, 2,4 giây

1. Tạo `OPA_FINAL`, dài 2,4s, nền `#0068FF`.
2. Đặt wordmark OPA trắng tại **`[960,460]`**, Scale **60%**; bề rộng artwork khoảng 864 px.
3. Tạo tagline Arial Regular **36 px**, trắng, center tại khoảng **`[960,680]`**.
4. Trong 0,3s đầu, logo đi từ y=480→460, Opacity 0→100. Tagline trễ 4 frame, từ y=700→680 và fade 0→100 trong 0,3s.
5. Giữ logo/tagline đứng yên phần còn lại. Đừng fade ra đen ở cuối nếu sẽ ghép ngay sang video doanh nghiệp; quyết định điểm cắt theo nội dung phía sau.

**Điểm kiểm tra:** từ khoảng 14,3s của master đến hết, người xem đọc được đầy đủ OPA và tagline.

## 10. Nếu muốn kết hợp cả 3 template trong một video

Hãy làm từng bản thay logo trước rồi import các `.aep` làm việc vào một master bằng Ctrl+I. AE đưa project được import vào folder; giữ tên comp con để expression tiếp tục đúng. Ba engine cùng chạy dễ nặng, nên dựng và kiểm tra từng cảnh trước khi bật preview cả master.

Cách ghép đề xuất: **0-1,8s template 3** lấy contour/lưới đang hình thành → **1,8-6,2s template 1** lấy phần có khối/highlight → **6,2-7,2s template 2** lấy một nhịp HUD → **7,2-16s** dùng các cảnh nhận diện ở mục 9.

Đây là **phương án biên tập**: chọn đoạn nguồn bằng mắt sau khi thay logo, không lấy mặc định 1,8s đầu của mọi template vì có thể chỉ có nền. Dùng ba frame kiểm tra đã render để định hướng, rồi RAM Preview để chọn mốc in/out thực tế. Cắt theo mức sáng, vị trí và độ lớn logo; dùng hard cut hoặc dissolve tối đa khoảng 3-5 frame khi cần nối.

Để thống nhất hình: cùng tông nền tối, xanh OPA làm chính, giảm HUD/codes nếu lấn wordmark. Mỗi đoạn chỉ có một lớp logo chính. Nếu nhịp HUD quá khác, dùng template 2 thành một phiên bản intro riêng và giữ bản 16s đi theo template 1.

## 11. Audio và nhịp cắt

Trong ba bộ đã giải nén không có file nhạc riêng dạng WAV/MP3; các MP4 help là video hướng dẫn. Template 1 dẫn tới nhạc preview bán riêng trong PDF. Bạn có thể đặt nhạc/sound design đã có quyền sử dụng ở master.

| Mốc master 16s | Âm thanh gợi ý |
|---|---|
| 0-2s | Một texture điện tử nhẹ, không che tiếng nếu có voice-over |
| 3-6s | Một whoosh/sweep đi cùng highlight hoặc chuyển góc |
| 7,2s | Một nhịp chốt khi bắt đầu bản nhận diện phẳng |
| 9,2s | Whoosh ngắn theo cảnh artwork trượt |
| 10,2s | 2-3 click nhẹ theo thẻ màu |
| 11,6s | Pop mềm cho badge |
| 13,6s | Một âm chốt thương hiệu và đuôi reverb ngắn |

Trong AE nhấn **L** trên layer audio để mở Audio Levels. Bắt đầu ở mức nhỏ, preview với tai nghe, giảm nếu nhiều effect cộng lại bị gắt. Giữ peak dưới 0 dBFS; có thể chừa khoảng 1 dB ở bản xuất. Không cần đặt whoosh cho mọi layer chuyển động.

## 12. Xuất file và gom project để chuyển máy

### Xuất video

1. Mở `OPA_MASTER_16S` hoặc comp intro HD bạn đã tạo.
2. Ctrl+M để đưa comp vào Render Queue.
3. Render Settings: **Best Settings**, Resolution **Full**, 30 fps ở master.
4. Output Module trên AE hiện tại có preset **`H.264 - Match Render Settings - 15 Mbps`**; chọn preset này để có MP4 xem/gửi.
5. Output To: chọn thư mục Exports, đặt tên rõ `OPA_Intro_T1_10s_HD.mp4` hoặc `OPA_BrandFilm_16s_HD.mp4`.
6. Render, sau đó mở MP4 kiểm tra từ đầu tới cuối. RAM Preview ở Half/Quarter không phản ánh chính xác độ nét xuất Full.

Để xuất UHD 3840×2160, tạo master riêng kích thước đó, scale vị trí/shape/text tương ứng. Template 1 có engine đúng 3840×2160. Template 2 chỉ HD; phóng nó lên không tạo thêm chi tiết thật. Template 3 có bản 4096×2160, cần quyết định crop/fit khi đưa vào UHD.

### Chuyển cả project và footage

Trong bản làm việc, chọn **File → Dependencies → Collect Files…** - Gom file phụ thuộc. Chọn thu thập cho project/các comp cần bàn giao, kiểm tra đủ ảnh và audio, rồi chọn thư mục đích mới. Đây là thao tác Adobe hướng dẫn để gom project cùng nguồn; xem [tài liệu Adobe về nhập và gom project](https://helpx.adobe.com/after-effects/desktop/work-with-other-applications/work-with-adobe-premiere/importing-effects-premiere-pro.html).

Giữ PNG logo và texture cạnh bản làm việc hoặc dùng Collect Files. Nếu bị missing footage, right-click footage đó trong Project → **Replace Footage → File…**, chọn file cùng tên trong thư mục đã giải nén. Thay file texture của template 3 ở item `DirtWindowStains005_COL_6K.jpg`; không thay vào layer logo.

## 13. Lỗi thường gặp và cách xử lý

| Triệu chứng | Kiểm tra và sửa |
|---|---|
| Logo OPA rất bé | PNG gốc có nhiều khoảng trong suốt; dùng PNG 1500×500 đi kèm, rồi chỉnh control hoặc Scale đúng chỗ |
| Template 1 vẫn hiện logo AP trong khối | Đã đè logo ở comp kết quả; thay footage `## LOGO REPLACE` để mọi pre-comp đọc cùng nguồn |
| Template 3 logo quá to | Layer EPS demo có Scale khoảng 575%; thêm PNG mới, đặt Scale 112,5% và tắt EPS |
| Template 2 đổi Logo Color mà hình không đổi | `Use Logo Original Color` đang bật; tắt nó để dùng Logo Color, hoặc giữ bật và sửa artwork nguồn |
| Logo có hình chữ nhật đen | Kiểm tra alpha/checkerboard trong viewer; dùng PNG trong suốt, không dùng JPG logo có nền |
| Viền O/P bị lấp | Giảm Line Thickness/glow, kiểm tra tại Full; giữ màu highlight có chi tiết |
| Tagline mất dấu | Dùng Arial hỗ trợ tiếng Việt, kiểm tra chữ trong Character và trên frame xuất |
| Chữ bị cắt | Xem canvas TEXT / URL HERE, giảm font size hoặc đặt lại vị trí; không chỉ kéo rộng layer theo X |
| Sửa một bản làm bản khác đổi theo | Hai layer pre-comp đang dùng chung nguồn; duplicate comp trong Project nếu cần nội dung độc lập |
| Expression đỏ sau khi đổi tên | Khôi phục tên comp gốc hoặc sửa tham chiếu; ưu tiên đặt tên OPA cho wrapper/master |
| Render chậm | Preview Quarter, chỉ preview Work Area cần xem; ba engine đều có nhiều lớp/comp lớn, nhất là T1 |
| Lệch màu/nét khi ghép 3 mẫu | Thống nhất bảng xanh-tối, kiểm tra frame giao nhau, giảm lớp HUD/codes và độ sáng phụ |
| Đoạn màu/badge có frame trống | Kiểm tra in/out của layer cảnh theo bảng frame master; mốc cuối là exclusive, cảnh sau bắt đầu ngay mốc đó |

## 14. Checklist hoàn tất

- Đúng silhouette O/P/A và khoảng rỗng, không gõ lại wordmark bằng font.
- Logo, contour và các lớp khối đều đọc nguồn OPA.
- Không còn AP, Envato, `envato.com`, `www.yourwebsite.com` hoặc Lorem Ipsum của demo.
- Nền tối/sáng và logo có đủ tương phản; highlight không lấn hình.
- Tagline viết hoa đầu dòng, đủ dấu, nằm trong khung.
- Không nhầm mốc thời gian của tutorial 3 phút với mốc của intro 10-12 giây.
- Xem đủ phần giữa và cảnh kết; không chỉ kiểm tra frame đầu/cuối.
- Đã xem MP4 xuất Full, có audio đúng mức và đúng tỉ lệ hình.
- Có bản Collect Files khi chuyển máy.

## 15. Bằng chứng và các file mở lại

| File/thư mục trong bộ hướng dẫn | Nội dung |
|---|---|
| `Evidence/source-inventory.json` | Danh sách và SHA256 các file nguồn trước khi đọc |
| `Evidence/Download-probe.json` | Thông số đúng video Download.mp4, 478 frame và checksum |
| `Native/*-inspection.json` | Comp, layer, effect và giá trị control đọc trực tiếp trong AE |
| `Images/Reference/all-frames-1.jpg` đến `all-frames-6.jpg` | Bảng hình bao phủ toàn bộ video tham chiếu |
| `Images/Tutorials/T2-sheet-*.jpg`, `T3-sheet-*.jpg` | Bảng mốc của hai video hướng dẫn |
| `Images/PDF/AE-Help-*.png`, `Script-*.png` | Trang PDF của template 1 đã render để đọc hình và chữ |
| `Examples/OPA_T1_SETUP.aep`, T2/T3 tương ứng | Bản setup OPA để thực hành; đã thay logo/màu/chữ và kiểm tra một frame mỗi bộ |
| `QA` | Log render các frame kiểm tra và báo cáo xác minh bộ hướng dẫn |

Phần cấu trúc và control đã được đọc từ file thật trên AE 26.3; các bản setup dùng logo OPA để render frame kiểm tra. Kịch bản 16 giây ở mục 9 là hướng dẫn triển khai tiếp, với thông số dựng được đề xuất rõ ràng. Bản Blueprint OPA ở lượt trước nằm riêng tại `/media/vmiz/Over Powers/video AE/OPA-Blueprint-OPA`, không dùng nhầm làm nguồn của ba template mới.

Các project trong Examples đi cùng Assets. Mở một bản để đối chiếu ngay các control đã đặt, hoặc tự làm lại từ file gốc theo từng bước trong tài liệu. Texture/EPS của template 3 được copy vào `Assets/T3-Footage` cho các bản setup này.
