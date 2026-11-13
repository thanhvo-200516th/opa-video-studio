# OPA × Hi-Tech Logo Reveal — Manum-FX / NH2GY3D

## Trạng thái và mục tiêu

Người dùng xác nhận chưa tải template. Tài liệu này hoàn thành kịch bản và quy trình chỉnh sửa; chưa phải hướng dẫn đã kiểm chứng trên AEP của NH2GY3D. Các tên `OPA_MASTER`, `OPA_END_BG`, `OPA_WORDMARK` dưới đây là tên hướng dẫn bạn tự tạo, không phải tên layer được tác giả cung cấp.

Trang đã đối chiếu: https://elements.envato.com/hi-tech-logo-reveal-NH2GY3D . Thuộc tính hiện niêm yết After Effects CC, 1920×1080, 10 giây, không yêu cầu plugin bổ sung. Cần mở AEP để xác nhận fps, thời lượng comp thực tế, tên controller và cấu trúc layer. Video preview có thể khác một chút về thời lượng so với comp xuất.

Mục tiêu sáng tạo: một hệ thống công nghệ khởi động, nhận diện chữ O bằng vòng quét, sau đó trình bày đầy đủ OPA rõ ràng. Chữ O dùng trong cảnh reveal là đề xuất chuyển động; dấu hiệu nhận diện cuối vẫn là nguyên logo OPA.

## 1. Kịch bản đề xuất

Bản chính khoảng 12 giây: khoảng 10 giây template và khoảng 2 giây kết thương hiệu. Các mốc trong đoạn HUD là định hướng cảm giác, không phải keyframe gốc đã đo từ AEP.

| Thời gian dự kiến | Hình ảnh | Cảm giác / âm thanh đề xuất |
|---|---|---|
| 0–2s | Nền xanh đen, grid và các điểm dữ liệu xuất hiện | Hệ thống khởi động, tiếng điện tử nhẹ |
| 2–5s | Các vòng HUD tách lớp, xoay và tiến về tâm theo chuyển động mẫu | Quét và tập hợp thông tin, một tiếng sweep |
| 5–8s | Vòng ổn định dần, chữ O trắng của OPA hiện ở tâm | Nhận diện được kích hoạt, một điểm nhấn âm thanh |
| 8–9,6s | Giữ chữ O trong HUD, các chi tiết phụ lắng lại theo mẫu | Cho người xem kịp nhận hình |
| 9,6–10,3s | Nền xanh đen phủ dần lên HUD; đầy đủ OPA xanh xuất hiện | Chuyển êm, âm thanh giảm dần |
| 10,3–12s | Logo OPA nguyên bản đứng rõ trên nền sạch | Giữ thương hiệu, kết gọn |

Không thêm tagline hay địa chỉ web vào bản chính vì chưa có nội dung được chốt. Không dùng font gõ lại chữ OPA để thay cho file logo.

### Màu và bố cục đề xuất

- Xanh thương hiệu: `#0068FF`.
- Nền cảnh kết: `#071526` — màu nền đề xuất, không phải màu nền gốc đã đo.
- HUD: giữ nhiều nét trắng/xanh nhạt; dùng xanh thương hiệu làm điểm nhấn.
- Logo trong vòng: `OPA-O-white-512x512.png`, giữ đúng hình và khoảng hở của O.
- Logo cảnh kết: `OPA-blue-1500x500.png`, đặt giữa khung.
- Logo đầy đủ ngang khoảng 3,3:1, vì vậy không ép nó thành hình vuông để vừa vòng HUD.

## 2. Chuẩn bị thư mục và tải đúng gói

Thư mục hướng dẫn và asset đã chuẩn bị:

```text
/media/vmiz/Over Powers/video AE/OPA-NH2GY3D-Guide/
    HUONG-DAN-OPA-NH2GY3D.md
    Assets\
        OPA-O-white-512x512.png
        OPA-blue-1500x500.png
        OPA-white-1500x500.png
```

Khi tải về, bạn tự tạo thêm các thư mục sau:

```text
Source\      gói NH2GY3D giải nén, giữ đầy đủ cây thư mục
Project\     bản .aep chỉnh cho OPA
Render\      video xuất thử và bản cuối
```

1. Mở trang NH2GY3D, kiểm tra tác giả là **Manum-FX**.
2. Đăng nhập tài khoản có quyền tải và tải gói template. Nút **Download preview** chỉ lấy video mẫu, không phải project chỉnh sửa.
3. Giải nén đầy đủ vào `Source`. Giữ nguyên vị trí tương đối của AEP và thư mục footage đi kèm.
4. Đọc file Help/Tutorial trong gói nếu có để tìm comp thay logo và color controls.

**Điểm kiểm tra:** trong gói phải có project `.aep` hoặc project AE tương ứng, không chỉ có `.mp4`.

## 3. Mở và lưu bản OPA

1. Mở After Effects, chọn **File > Open Project** và mở AEP vừa giải nén.
2. Nếu AE chuyển đổi project phiên bản cũ, lưu thành bản mới.
3. Chọn **File > Save As > Save As**, lưu tại:
   `/media/vmiz/Over Powers/video AE/OPA-NH2GY3D-Guide/Project/OPA-NH2GY3D-v01.aep`.
4. Nếu có Missing Footage, chọn một footage bị thiếu ở Project panel, dùng **Replace Footage > File** và trỏ đúng file trong thư mục giải nén.
5. Nếu có Missing Font, kiểm tra tutorial và layer text tương ứng. Bản chính không cần tagline nên không tự thay font của logo.

**Điểm kiểm tra:** chạy preview bản gốc trong project đã Save As trước khi sửa. Nếu bản gốc chưa giống preview, xử lý tài nguyên thiếu trước.

## 4. Nhận diện comp chính và comp thay logo

**Composition / comp** là một cảnh có timeline. **Pre-comp** là một comp nằm như một layer trong comp khác. Chỉnh nội dung pre-comp có thể thay đổi tất cả nơi đang dùng nó.

1. Trong **Project panel** — bảng chứa tài nguyên, tìm comp có đầy đủ nền, vòng HUD và logo.
2. Mở comp và đưa playhead đến gần cuối. Đối chiếu với video mẫu để nhận ra comp xuất chính.
3. Nhấn **Ctrl+K** mở Composition Settings. Ghi lại kích thước, fps và duration thực tế; giữ nguyên fps của mẫu.
4. Tạm gọi comp đó là **comp HUD chính** trong hướng dẫn; không cần đổi tên comp tác giả vì expressions có thể tham chiếu tên cũ.
5. Xem tutorial để tìm comp thay logo. Các từ như Logo, Replace, Edit là từ khóa gợi ý, không phải tên đã xác nhận của NH2GY3D.
6. Nếu chưa thấy, trong comp HUD chính, mở dần layer pre-comp có chứa hình logo cho đến khi thấy ảnh logo mẫu.

**Điểm kiểm tra:** bạn tìm được nơi thay ảnh logo, nhưng các vòng HUD/camera vẫn nằm trong phần animation của mẫu. Không đặt ảnh OPA đè thẳng lên cảnh chính nếu muốn nó hưởng hiệu ứng reveal.

Lưu ý: Ctrl+D một comp chính không tự nhân bản toàn bộ pre-comp con. Bản Save As ở bước 3 giúp giữ project nguồn gốc riêng.

## 5. Import và thay chữ O vào vị trí logo

1. Nhấn **Ctrl+I** — Import File.
2. Import ba PNG trong thư mục `Assets` của hướng dẫn.
3. Mở comp thay logo, bật biểu tượng ô bàn cờ trong Composition viewer để kiểm tra nền trong suốt.
4. Nếu ảnh logo mẫu chỉ là một layer tĩnh bên trong comp thay logo: kéo `OPA-O-white-512x512.png` vào comp đó; tắt mắt layer ảnh mẫu, giữ lại các layer matte/effect liên quan.
5. Chọn layer O vừa thêm, nhấn **S** — Scale. Giữ hai chiều liên kết, chỉnh để vừa vùng logo mẫu. Không mặc định Scale phải bằng 100%.
6. Nhấn **P** — Position, đưa O vào giữa comp thay logo. Nếu comp có kích thước W×H, tâm hình học thường là `[W/2, H/2]`; kiểm tra bằng mắt ở comp chính sau đó.
7. Quay lại comp HUD chính để xem O có đi cùng vòng, ánh sáng và reveal hay không.

**Nếu layer logo mẫu có animation riêng:** nhấn **U** để xem keyframes trước khi thay. Khi cần giữ nguyên animation của layer đó, tạo một comp chứa O với kích thước bằng source logo cũ; sau đó giữ **Alt** và kéo comp mới từ Project panel thả lên đúng layer logo cũ trong Timeline. Cách này giữ thuộc tính layer; vẫn phải kiểm tra căn tâm và kích thước vì source mới có thể khác source cũ.

**Điểm kiểm tra:** logo mẫu đã biến mất, O đúng hình, không có hộp nền đen, không bị méo và không bị che mất khoảng hở.

## 6. Xử lý dòng chữ mặc định

1. Tìm layer text đang hiển thị URL hoặc chữ mẫu trong cảnh.
2. Nếu layer text nằm trong một comp riêng, mở đến layer chữ có biểu tượng T.
3. Với bản chính không tagline, tắt mắt đúng layer chữ mẫu. Giữ lại các layer điều khiển, matte hoặc thành phần HUD khác.
4. Quay lại comp HUD chính và chạy qua cả đoạn reveal.

Nếu chữ đã nằm trong footage dựng sẵn, không thể sửa bằng Type Tool; cần kiểm tra AEP trước khi quyết định cách che/thay. Không đoán rằng mọi chữ trên preview đều là text editable.

**Điểm kiểm tra:** không còn tên, logo hay URL mặc định của mẫu trong khung hình.

## 7. Chỉnh màu cho OPA

1. Mở comp chính và chọn layer điều khiển màu được tutorial tác giả chỉ định, nếu có.
2. Vào **Window > Effect Controls** — bảng chỉnh hiệu ứng của layer đang chọn.
3. Nếu có các ô màu cho HUD/accent/background, chỉnh từng ô một rồi xem lại ảnh. Tên các ô thực tế cần xác nhận từ AEP.
4. Đặt điểm nhấn năng lượng về `#0068FF`, giữ các vạch nhỏ trắng hoặc xanh nhạt để rõ chi tiết.
5. Chỉ chỉnh màu nền qua control của tác giả nếu có. Cảnh kết riêng ở bước sau sẽ dùng `#071526`.
6. Nếu không có controller, cần xác định đúng layer sinh màu của HUD trước; không áp Fill lên toàn bộ cảnh vì sẽ làm mất các sắc độ/chi tiết.

**Điểm kiểm tra:** cảnh có tông xanh OPA, O vẫn rõ, các nét HUD không cháy trắng hoặc bít vào nhau. Chưa cần thay keyframe camera, xoay vòng hay tốc độ của mẫu.

## 8. Tạo comp xuất mới để thêm cảnh kết

Giữ nguyên animation trong comp HUD chính. Tạo một comp bao ngoài để thêm đủ logo OPA cuối video.

1. Trong Project panel, kéo comp HUD chính vào nút **New Composition**. AE tạo comp mới bao chứa nó và kế thừa thông số.
2. Chọn comp mới, nhấn **Ctrl+K**, đặt tên `OPA_MASTER`.
3. Gọi thời lượng comp HUD chính là **T**. Đặt duration comp mới thành **T + 2 giây**, giữ nguyên fps. Nếu T=10s thì comp xuất là 12s.
4. Kiểm tra layer HUD bắt đầu ở giây 0 và kết thúc đúng T. Không bật Time Remapping hoặc Time Stretch cho bản đầu.

Thứ tự layer trong `OPA_MASTER` sau khi làm xong, từ trên xuống:

```text
OPA_WORDMARK    PNG logo đầy đủ, 2D
OPA_END_BG      solid xanh đen, 2D
Comp HUD chính pre-comp gốc đã thay O và màu
Audio          nếu có dùng âm thanh riêng
```

Các layer cảnh kết không parent với camera hoặc null của template. Cảnh kết dùng vị trí màn hình cố định.

## 9. Tạo nền cảnh kết

1. Trong `OPA_MASTER`, đưa playhead về giây 0, chọn **Layer > New > Solid** hoặc nhấn **Ctrl+Y**.
2. Đặt tên `OPA_END_BG`, màu `#071526`, bấm **Make Comp Size**.
3. Đặt solid ở trên layer HUD. Giữ layer 2D, Mode Normal.
4. Đưa playhead tới **T − 0,4 giây**, chọn solid rồi nhấn **T** — Opacity.
5. Bấm đồng hồ Opacity, đặt **0%**.
6. Đưa playhead tới **T**, đặt Opacity **100%**.
7. Kéo out-point solid phủ đến cuối `OPA_MASTER` nếu layer chưa đủ dài.

Ví dụ nếu T=10s: nền có Opacity 0% ở 9,6s và 100% ở 10,0s. Ở fps không biểu diễn được đúng 9,6s, chọn frame gần nhất.

**Điểm kiểm tra:** trước đoạn chuyển, HUD vẫn rõ. Khi comp HUD kết thúc, nền mới đã kín khung và không có frame đen/trong suốt ngoài ý muốn.

## 10. Thêm đầy đủ OPA và tạo keyframe

1. Đưa playhead về giây 0 rồi kéo `OPA-blue-1500x500.png` vào `OPA_MASTER`, đặt trên `OPA_END_BG`. Kiểm tra in-point của layer không nằm sau thời điểm bắt đầu fade.
2. Đổi tên layer thành `OPA_WORDMARK`, giữ layer 2D.
3. Nhấn **P**, đặt Position `[960, 540]` nếu comp là 1920×1080.
4. Nhấn **S**, đặt Scale khởi điểm khoảng **50%**, giữ liên kết hai chiều. Đây là điểm bắt đầu để chỉnh bằng mắt; không phải giá trị logo placeholder gốc.
5. Đưa playhead tới **T − 0,2s**, nhấn **T**, bấm đồng hồ và đặt Opacity **0%**.
6. Tới **T + 0,3s**, đặt Opacity **100%**.
7. Nhấn **S**. Tại **T − 0,2s**, tạo keyframe Scale **48%**. Tại **T + 0,3s**, tạo keyframe **50%**.
8. Chọn hai keyframe Scale, nhấn **F9** — Easy Ease để chuyển động mềm.
9. Giữ logo đứng yên, Opacity 100% đến cuối. Không thêm nhấp nháy hoặc glitch ở đoạn giữ cuối.
10. Kiểm tra layer PNG kéo dài đến cuối comp.

Ví dụ T=10s:

| Layer / thuộc tính | Mốc đầu | Mốc sau |
|---|---|---|
| OPA_END_BG / Opacity | 9,6s → 0% | 10,0s → 100% |
| OPA_WORDMARK / Opacity | 9,8s → 0% | 10,3s → 100% |
| OPA_WORDMARK / Scale | 9,8s → 48% | 10,3s → 50% |

Phím T vừa là chữ viết tắt biến thời lượng trong tài liệu, vừa là phím AE mở Opacity khi một layer đang chọn; hai ý này khác nhau.

**Điểm kiểm tra:** sau chuyển cảnh, người xem nhìn thấy đủ O/P/A đúng tỷ lệ, ở giữa khung, nền sạch. Vòng HUD không đè lên wordmark ở cảnh cuối.

## 11. Phương án đơn giản hơn: dùng cả logo ngay trong HUD

Nếu không muốn dùng riêng chữ O, ở bước 5 thay bằng `OPA-white-1500x500.png`. Giữ đúng tỷ lệ và thu nhỏ để toàn bộ wordmark nằm trong vùng trống của vòng.

Kiểm tra ở Composition viewer 100% và cả khi xem nhỏ như trên điện thoại. Nếu logo ngang bị nhỏ khó đọc hoặc cắt P/A, ưu tiên bản O → đầy đủ OPA ở trên. Không kéo giãn logo hoặc thay đổi kích thước của comp placeholder tùy tiện vì có thể ảnh hưởng matte/effect.

## 12. Âm thanh, xem thử và xuất

### Âm thanh

Trang mẫu liên kết một track âm thanh riêng, nên cần kiểm tra gói tải có audio hay không. Không mặc định nhạc preview đã nằm trong AEP. Nếu thêm âm thanh, đặt sweep theo vòng quét, impact theo lúc O hiện rõ; để đuôi âm thanh giảm mềm trong cảnh kết. Không nhân đôi audio nếu comp gốc đã có track.

### Xem thử

1. Preview toàn bộ `OPA_MASTER`, trước tiên ở Half resolution để xem nhịp.
2. Kiểm tra lại các frame O vừa xuất hiện, trước/sau nền phủ HUD và frame logo cuối ở Full resolution / 100%.
3. Xác nhận không còn logo/URL mẫu, không méo OPA, không còn matte cắt logo, không thiếu footage/font/effect.
4. Xác nhận đoạn giữ logo cuối đủ dài và không cắt mất đuôi âm thanh.
5. Save project bằng Ctrl+S.

### Xuất MP4 xem thử

1. Mở đúng `OPA_MASTER`.
2. Chọn **Composition > Add to Render Queue**.
3. Render Settings: Best Settings, phạm vi toàn comp. Nếu Work Area chưa phủ toàn clip, sửa Time Span về toàn bộ comp trước khi render.
4. Output Module: chọn H.264 nếu bản AE đang dùng có hỗ trợ. Với Full HD, có thể bắt đầu khoảng 15–20 Mbps để xem thử chất lượng; đây là đề xuất xuất, không phải thiết lập gốc template.
5. Output To: `/media/vmiz/Over Powers/video AE/OPA-NH2GY3D-Guide/Render/OPA-NH2GY3D-v01.mp4`.
6. Nếu bản AE không có H.264 trong Render Queue, dùng **Composition > Add to Adobe Media Encoder Queue**, chọn H.264 / Match Source và kiểm tra lại kích thước, fps, phạm vi xuất.
7. Render rồi mở chính MP4 vừa xuất để xem từ đầu đến cuối. Render xong không đồng nghĩa đã kiểm tra chất lượng.

Sau khi hoàn thiện có thể dùng **File > Dependencies > Collect Files** để gom project và footage cho việc lưu trữ/chuyển máy. Tài liệu hướng dẫn không phải một AEP đã dựng sẵn.

## 13. Lỗi thường gặp

| Hiện tượng | Kiểm tra trước |
|---|---|
| OPA quá nhỏ trong vòng | Logo ngang cần vùng rộng; dùng O trong HUD và wordmark cuối |
| PNG hiện nền đen | Bật checkerboard, kiểm tra alpha và đúng PNG; màu đen viewer chưa chắc là nền trong ảnh |
| Thay PNG nhưng không thấy reveal | Có thể đang đặt ảnh ở sai cấp; cần thay bên trong comp logo mà animation tham chiếu |
| Thay source làm lệch tâm | Kiểm tra source dimensions, Anchor Point, Position, Scale; tạo comp insert cùng kích thước source cũ |
| P/A bị cắt | Kiểm tra mask/matte và vùng trống của placeholder, không kéo méo logo |
| Chỉnh màu không tác dụng | Xác định đúng controller / đúng comp; màu có thể do expression điều khiển |
| Cảnh cuối không thấy logo | Logo phải trên solid, Opacity có keyframe 100%, layer đủ dài và không parent vào camera |
| Cuối video xuất bị cắt | Kiểm tra duration OPA_MASTER, layer out-point và Time Span trong Render Queue |

## Nguồn đối chiếu

- Template: https://elements.envato.com/hi-tech-logo-reveal-NH2GY3D
- Adobe — pre-comp và comp lồng: https://helpx.adobe.com/after-effects/desktop/work-with-compositions/precomposing-and-nesting/precomposing-nesting-pre-rendering.html
- Adobe — xuất H.264 trực tiếp: https://helpx.adobe.com/after-effects/desktop/render-and-export/export-h-264-from-the-after-effects/exporting-h264-from-the-after-effects-render-queue.html
- Adobe — render/export và Collect Files: https://helpx.adobe.com/after-effects/desktop/render-and-export/basics-of-rendering-and-exporting/basics-rendering-exporting.html

Khi có AEP thật, phần cần cập nhật là: tên comp chính, tên comp logo, tên layer text/controller, fps và duration T. Kịch bản, asset OPA và cách thêm cảnh kết bao ngoài vẫn là cơ sở để triển khai.
