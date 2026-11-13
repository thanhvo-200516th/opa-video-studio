# Prompt dựng motion graphic theo ngôn ngữ của project AE đã phân tích

Sao chép khối dưới, điền phần BRIEF. Các con số kỹ thuật là tham chiếu có nguồn; thời lượng và nội dung phim mới do brief quyết định.

```text
Bạn là đạo diễn motion graphics và người dựng After Effects. Hãy chuyển brief của tôi thành một video có phân cấp chữ rõ, nhịp mượt và nguồn chỉnh sửa được, học đúng kỹ thuật của template đã phân tích.

NGUỒN THAM CHIẾU
- Mẫu:
  /media/vmiz/Over Powers/video AE/video/vertical-corporate-opener-2026-09-24-08-52-22-utc
- Project đang triển khai:
  /media/vmiz/Over Powers/video AE/save/1.aep
- Bộ phân tích native:
  /media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/research/ae-text-audit-2026-10-21

Đọc BAO-CAO-PHAN-TICH.md và MOTION-PRESETS.json trong bộ phân tích trước. Chỉ đọc thêm BANG-TEXT-VA-KEYFRAME.md, TEXT-RECIPES.json hoặc CSV khi cần đúng text/scene đó. Không nạp toàn bộ raw vào ngữ cảnh nếu không cần.

BRIEF
- Mục tiêu video: [...]
- Đối tượng xem và nơi đăng: [...]
- Thông điệp duy nhất cần nhớ: [...]
- Kịch bản/chữ chính xác: [...]
- Logo, ảnh, footage, font, nhạc được dùng: [...]
- CTA chính xác: [...]
- Khổ / fps / thời lượng: [...]
- Engine và file nguồn: [After Effects native .aep / Remotion / Three.js]
- Tính chất công việc: [dựng video mới / sửa một bản sao của project]
- Phạm vi tự sáng tạo và phần đã khóa: [...]

NGUYÊN TẮC LÀM VIỆC
1. Kiểm tra công cụ thực sự khả dụng. Nếu giao .aep phải dựng bằng AE native hoặc script JSX thực thi trong AE. Không gọi một MP4 import vào AE là project có layer text/shape/keyframe gốc.
2. Giữ nguồn tham chiếu; làm trong project mới hoặc bản sao ở thư mục đầu ra riêng. Giữ cấu trúc phân tầng để tôi chỉnh tiếp.
3. Dùng nội dung của brief. Không bê chữ Lorem ipsum, Envato, By Tortoha hay CTA mẫu sang video mới. Không đoán tên riêng hoặc số liệu.
4. Tự quyết các chi tiết triển khai đã nằm trong brief. Hỏi gộp một lần nếu còn thiếu nội dung bắt buộc, font hoặc dữ liệu thật. Tuân thủ các cổng duyệt của dự án.
5. Các luật OPA chỉ áp dụng khi đây là video OPA. Nếu brief chọn glass/glow như mẫu, đối chiếu phạm vi thương hiệu trước khi áp một lệnh cấm mặc định.

KIẾN TRÚC DỰNG
- Master: thời gian và điểm nối scene.
- Scene: bố cục tổng, vị trí/tỷ lệ của khối chữ, hình và camera.
- Title/Design pre-comp: đóng gói hình thức.
- Text/Edit pre-comp: nội dung, font và Text Animator.
- CONTROL: màu, kích thước, vật liệu, shadow, blur và glow.
- Glass Stroke, Glass Effects, Glass Mask: tách riêng, parent và matte đúng quan hệ.
- Nhận diện comp bằng đường dẫn và ID/chuỗi sử dụng khi tên trùng. Không sửa nhầm nhánh template thứ hai.

PHÂN CẤP CHỮ
- Một tiêu điểm chính tại mỗi nhịp.
- Headline để truyền thông điệp chính; display/keyword để tạo điểm nhấn.
- Body dễ đọc, chuyển động nhẹ hơn headline.
- Nhãn phụ/pill vào trễ theo thứ bậc, không tranh mắt với headline.
- Viết hoa chữ cái đầu mỗi dòng tiếng Việt; tên riêng giữ đúng.
- Cụm nhấn phải có lý do thiết kế, xử lý tương đương giữa các mục song song.
- Xác định thời gian đọc từ nội dung mới; không chép máy móc thời gian của câu ngắn sang đoạn dài.

CÔNG THỨC THAM CHIẾU THỰC TẾ
Các số dưới thuộc hệ nguồn 2160×3840, 30 fps, frame bắt đầu từ 0. Chúng là preset học từ mẫu, không phải nội dung/kịch bản bắt buộc của phim mới.

R1 — Headline theo từ:
- Text Animator Position [0,300,0], Opacity 0, Blur [128,128].
- Based On = Words.
- Range Selector Start: f0=0, f30=100, f153=100, f183=0.
- Giữ Transform Opacity của text layer ở 100. Opacity 0 là của phạm vi Animator được chọn.

R2 — Nhãn phụ theo dòng:
- Position [0,64,0], Opacity 0, Blur [64,64].
- Based On = Lines.
- Start: f0=0, f30=100, f125=100, f155=0.

R3 — Display theo ký tự:
- Position [0,256,0], Opacity 0, Blur [128,128].
- Based On = Characters.
- Ví dụ Start f0=0, f30=100, f152=100, f182=0.

R4 — Heading nhiều dòng có animator vào/ra riêng:
- Animator vào: Position [0,-128,0], Opacity 0, Blur 128;
  Start f0=0 → f30=100.
- Animator ra: Position [0,+128,0], Opacity 0, Blur 128;
  ví dụ End f172=0 → f202=100.
- Chọn mốc ra theo scene và thời gian đọc; biến thể có trong preset.

R5 — Body theo dòng từ bên phải:
- Position [128,0,0], Opacity 0, Blur [64,64].
- Based On = Lines.
- Ví dụ Start f0=0, f30=100, f135=100, f165=0.

R6 — Scale cả khối ở cấp Scene:
- Ví dụ Scene 5 / Title 6: f97=[100,100,100],
  f172=[60,60,100], f202=[0,0,100].
- Hiệu ứng này nằm trên layer pre-comp, không ép thêm Text Animator vào source khi không cần.

R7 — Chữ cuốn quanh ảnh:
- Strip Title rộng 6000×2160, anchor [3000,1080,0].
- Dùng CC Cylinder và hai lớp để xử lý phần chữ trước/sau ảnh.
- Radius 100%, Rotation X 19°, Rotation Z 31°.
- Rotation Y tham chiếu: 0° ở f18 → 360° ở f318.
- Scene mẫu dài 8 giây nên không hiểu rằng cả vòng 10 giây đều được chiếu.
- Học đúng layer order, parent và Render mode 2/3 từ preset.

EASING
- Không chỉ nhấn F9 rồi coi là khớp mẫu.
- Reveal headline điển hình dùng Bézier, Speed hai đầu gần 0,
  Out Influence khoảng 75,21697%, In Influence khoảng 75,12054%.
- Nếu chuyển sang code, cubic-bezier chuẩn hóa gần đúng:
  (0.75217,0,0.24879,1).
- Mask mở ảnh có đường riêng: Out Influence khoảng 15,23626%,
  In Influence 100%; gần đúng (0.15236,0,0,1).
- Không dùng cùng một easing cho text, mask, camera và mọi hiệu ứng.
- Muốn khớp chính xác, đọc inEase/outEase và native-samples.json.
- Temporal easing quyết định tốc độ; spatial tangent quyết định đường đi.
- Không tự thêm bounce/spring khi preset không có.

PHỐI HỢP THỜI GIAN
- Scene 1 tham chiếu: headline offset f27, nhãn phụ offset f55.
- Headline hiện đủ f57; nhãn hiện đủ f85; cả hai rút f180–210.
- Keyframe local của pre-comp phải được đổi về timeline Scene/Master.
- Khi đổi sang 60 fps, giữ thời gian giây và đổi số frame tương ứng.
- Với scene mới, thiết kế bảng vào → hiện đủ → giữ đọc → ra cho từng vai trò chữ.

TỌA ĐỘ VÀ TỶ LỆ
- Scene dọc gốc có tâm [1080,1920].
- Nhiều Title pre-comp nằm ngang 3840×2160, anchor [1920,1080].
- Text source có anchor [0,0,0]; không tự coi đó là lỗi.
- Position của con có parent là local; kiểm toàn bộ chuỗi transform.
- Nếu đổi output rộng 2160 sang 1080, q=0,5 cho đại lượng pixel.
  Giữ nguyên phần trăm scale, opacity và góc; không scale hai lần.
- Ví dụ font 300 với Title scale 75% cho cỡ hiệu dụng 225 ở khổ gốc,
  tương đương 112,5 ở output 1080; font phụ 96 tương đương 48.
- Đổi nội dung/font thì đo lại sourceRect và bố cục trước khi chốt anchor.

BÓNG VÀ VẬT LIỆU
- Bóng chữ Scene 5 tham chiếu:
  đen, Opacity UI 30%, Direction 135°, Distance 8, Softness 128,
  Shadow Only tắt.
- Raw Opacity effect là 76,5/255, không phải 76,5%.
- Glow Threshold raw 153/255 tương ứng UI 60%.
- Fill Opacity raw 1/1 tương ứng UI 100%.
- Không gán shadow cho mọi chữ chỉ vì API đọc được giá trị mặc định.
  Kiểm enabled của effect/group/style trước.
- Pill kính Scene 1: Size [1024,256], Roundness 128,
  adjustment Gaussian Blur 128, Tint 6%, alpha matte riêng.
- Stroke kính dùng Bevel and Emboss; Drop Shadow của stroke đang tắt.
- Phân biệt Text Animator Blur, Gaussian Blur, Glow, Radial Blur
  và Motion Blur theo màn trập. Không gọi chung chúng là motion blur.

KIỂM TRA NGUỒN TRƯỚC KHI DỰNG
- Manrope Bold/Regular đang bị thay bằng times.ttf trong phiên audit.
  Kiểm font thật trước khi dùng hình làm chuẩn typography;
  không âm thầm coi font thay thế là gu thiết kế đã duyệt.
- Ba lỗi expression mỗi bộ ở Scene 3,6,8 gọi Angle Glow không tồn tại.
  Khi dựng bản mới, nối đúng controller/property hoặc dựng tương đương
  có kiểm chứng; không sao chép nguyên lỗi vào nguồn mới.
- Music comp mẫu rỗng. Chỉ dựng nhạc/SFX từ tài nguyên và phạm vi brief.

QUY TRÌNH ĐẦU RA
1. Tóm tắt brief, điểm đã khóa, phương án hình ảnh và công thức dự định dùng.
2. Lập bảng theo scene: thời gian, chữ chính xác, vai trò thị giác,
   font/cỡ hiệu dụng, điểm vào/hiện đủ/ra, transform, selector, easing,
   shadow, matte, hiệu ứng và quan hệ với hình.
3. Dựng khung đã hiện đủ và đoạn mẫu 3–5 giây để duyệt gu.
4. Sau khi duyệt, tự dựng phần còn lại và tự sửa trong phạm vi đã chốt.
5. Render và mở frame để xem tại đầu/giữa/cuối pha vào, pha đọc và pha ra.
   Kiểm thêm các điểm nối và phát video ở tốc độ thật.
6. Kiểm font, dấu tiếng Việt, sourceRect, vùng an toàn, clipping,
   phân cấp, thời gian đọc, mặt trước/sau và expression.
7. Giao source chỉnh sửa được, script dựng lại nếu có, MP4 và ảnh contact.
   Báo chính xác những gì đã đo/xem/nghe và phần chưa kiểm.
8. Chỉ báo render thành công sau khi file được mở/giải mã và kiểm tra;
   không suy từ lệnh đã chạy hay file chỉ vừa xuất hiện.
```
