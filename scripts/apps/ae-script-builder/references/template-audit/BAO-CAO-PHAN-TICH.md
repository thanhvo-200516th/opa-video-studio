# Phân tích chữ và chuyển động từ project After Effects thực tế

Ngày đọc: 21/10/2026. Công cụ trích: After Effects 26.3x87, ExtendScript chạy trong phiên riêng. Nguồn gốc được mở để đọc, không lưu thay đổi. Số liệu trong tài liệu là dữ liệu lấy từ AE, trừ chỗ ghi rõ là đề xuất hoặc quy đổi gần đúng.

## Kết quả cần dùng ngay

Chữ trong mẫu chủ yếu được dựng bằng **Text Animator + Range Selector**, kết hợp Position, Opacity và Blur trên từng từ, dòng hoặc ký tự. Transform của text thường đứng yên. Cảm giác hoàn chỉnh còn đến từ cấp pre-comp Title, layer Scene, parent, mask, adjustment layer và controller.

Chất lượng của mẫu nằm ở cách phối hợp các cấp này. Một prompt chỉ yêu cầu “chữ bay lên, opacity 0–100, thêm shadow” sẽ bỏ mất phần lớn cơ chế thật.

Đọc `MOTION-PRESETS.json` để lấy 10 công thức gọn, `BANG-TEXT-VA-KEYFRAME.md` để xem từng chữ đang dùng trong master, và `PROMPT-HOAN-CHINH-OPUS.md` để giao việc cho AI.

## 1. Phạm vi đã đọc và trạng thái thực tế

| File | Comp | Layer | Text layer trong thư viện | Tổng keyframe lưu trong file |
|---|---:|---:|---:|---:|
| Corporate Opener Mobile.aep | 224 | 435 | 65 | 773 |
| Corporate Opener Mobile copy 23.x.aep | 224 | 435 | 65 | 773 |
| save/1.aep | 449 | 872 | 130 | 1.556 |
| save/Untitled Project.aep | 0 | 0 | 0 | 0 |
| Auto-Save/Untitled Project auto-save 1.aep | 449 | 872 | 130 | 1.556 |
| Auto-Save/Untitled Project auto-save 2.aep | 449 | 872 | 130 | 1.556 |

- File đang mở khi bắt đầu là `/media/vmiz/Over Powers/video AE/save/1.aep`, 589 project item, chưa có thay đổi chưa lưu tại thời điểm đọc trạng thái.
- File 1.aep nhập **hai bộ template**, một nhánh copy 23.x và một nhánh bản hiện hành. Vì vậy 130 text layer là hai thư viện 65 lớp, không phải 130 đoạn chữ khác nhau đang xuất hiện trong video.
- Master chính được phân tích là `!Corporate Opener`, ID 3, thuộc nhánh `Corporate Opener Mobile copy 23.x.aep`; nó được bọc bởi `!Corporate Opener 2`, ID 6386.
- Từ master ID 3 lần theo các source comp của layer đang bật: 145 comp liên quan, **26 text layer nguồn thực sự được sử dụng**. Một nguồn có thể được dùng qua nhiều lớp, như chữ vòng ở Scene 6.
- Hai phiên bản template có cùng keyframe chữ/chuyển động được trích. So sánh native phát hiện 431 khác biệt ở alpha của Material Options / Shadow Color; đây không phải 431 thay đổi thiết kế hay 431 lỗi motion.
- Nhánh thứ hai trong 1.aep giữ các tham số tĩnh/keyframe được so sánh với template hiện hành. Nhánh đầu có thay đổi màu/controller của Scene 1 và thêm một layer nền trong Glow Elements; phần lớn cấu trúc chữ vẫn từ mẫu.
- Các thư mục được cung cấp không chứa MP4/MOV, JSX/JSXBIN, FFX hay AEPX độc lập. Các biểu thức điều khiển nằm bên trong AEP: working có 544 expression lưu trong hai bộ.
- Music comp trong cả hai nhánh đều rỗng. Chưa có âm thanh để phân tích nhịp dựng theo nhạc.
- Đã đọc trang HELP.pdf. Tài liệu mô tả controller theo scene, thư mục Edit/Texts, placeholder và font Manrope. Các chỉ dẫn đó được dùng như tài liệu mô tả mẫu, không phải lệnh thay đổi project.

### Những điểm ảnh hưởng chất lượng

1. **Thiếu font thực tế.** Native `fontObject.isSubstitute=true` cho Manrope-Bold và Manrope-Regular; cả hai đang trỏ `C:\Windows\Fonts\times.ttf`. Vì thế chữ serif trong ảnh đang thấy là font thay thế. Không nên dùng hình serif này làm chuẩn của Manrope.
2. **Có expression lỗi sẵn trong nguồn.** Mỗi bộ template có ba lỗi ở Scene 3, 6, 8: Bevel and Emboss / Angle gọi `CONTROL → Title 2 → Angle Glow`, trong khi thuộc tính tên đó không tồn tại. Working nhập hai bộ nên ghi nhận sáu lỗi. Chưa sửa nguồn trong nhiệm vụ phân tích này.
3. **Ảnh/video còn là placeholder.** Các frame có mũi tên tải xuống đúng như source hiện có. Chưa thể kết luận chất lượng bố cục với footage thật.

## 2. Định dạng, thời gian và phân cấp

Master gốc: **2160 × 3840, 30 fps, 71 giây**. Scene 1–10 dài 8 giây; Scene 11 dài 3,0667 giây. Các scene chồng thời gian trên master.

| Scene | Bắt đầu trên master | Frame master, từ 0 |
|---|---:|---:|
| 1 | 0,0000 s | 0 |
| 2 | 7,0667 s | 212 |
| 3 | 13,8667 s | 416 |
| 4 | 20,6333 s | 619 |
| 5 | 27,4000 s | 822 |
| 6 | 34,1667 s | 1025 |
| 7 | 40,9000 s | 1227 |
| 8 | 47,6667 s | 1430 |
| 9 | 54,4000 s | 1632 |
| 10 | 61,2000 s | 1836 |
| 11 | 67,9333 s | 2038 |

Chuỗi dựng điển hình:

`Master → Scene → Designs/Title → Edits/Texts/Text → Text layer → Animator → Range Selector`.

Mỗi cấp làm một nhiệm vụ:

- **Text source:** nội dung, font, căn chữ, vũ đạo theo từ/dòng/ký tự.
- **Title design:** đóng gói text source để thay nội dung mà giữ cách dựng.
- **Scene:** vị trí, tỷ lệ, thời gian vào/ra của cả khối chữ; Fill, Shadow, Cylinder và quan hệ với hình.
- **Glass/Mask/Adjustment:** vật liệu và vùng tác động, không phải thuộc tính font.
- **CONTROL:** đổi màu, kính, độ sáng, bóng qua pseudo effect và expression.
- **Master:** thứ tự, điểm nối và thời gian chồng các scene.

Tên comp bị trùng giữa hai nhánh. Khi tự động hóa phải nhận diện bằng ID kèm đường dẫn thư mục/chuỗi sử dụng, không chỉ gọi tên `Text 1` hay `Scene 1`.

## 3. Các công thức text chính

Tất cả frame ở bảng này là **frame cục bộ của comp Text**, bắt đầu từ 0, tại 30 fps. Những tham số pixel thuộc khổ nguồn, chưa nhân tỷ lệ của layer cha.

| Công thức | Ví dụ nguồn | Font/cỡ nguồn | Chọn theo | Giá trị Animator | Keyframe điều khiển |
|---|---|---|---|---|---|
| R1 Tiêu đề chính | Scene 1 / Text 1 / Visual Graphics | Manrope Bold 300 | Từ | Position [0,300,0]; Opacity 0; Blur [128,128] | Start: f0=0 → f30=100 → f153=100 → f183=0 |
| R2 Nhãn phụ | Scene 1 / Text 2 / Motion Design | Manrope Regular 96 | Dòng | Position [0,64,0]; Opacity 0; Blur [64,64] | Start: f0=0 → f30=100 → f125=100 → f155=0 |
| R3 Display | Scene 2 / Text 3 / Minimalist | Manrope Bold 360 | Ký tự | Position [0,256,0]; Opacity 0; Blur [128,128] | Start: f0=0 → f30=100 → f152=100 → f182=0 |
| R4 Heading hai chiều | Scene 3 / Text 4 / Brand Promo / By Tortoha | Manrope Bold 256 | Dòng | Animator 1: Y=-128; Animator 2: Y=+128; cả hai Opacity 0, Blur 128 | Animator 1 Start f0=0 → f30=100; Animator 2 End f172=0 → f202=100 |
| R5 Body | Scene 3 / Text 5 / Lorem ipsum… | Manrope Regular 64 | Dòng | Position [128,0,0]; Opacity 0; Blur [64,64] | Start f0=0 → f30=100 → f135=100 → f165=0 |

### Vì sao Opacity Animator bằng 0 nhưng chữ vẫn hiện?

Giá trị 0 là độ mờ của **nhóm ký tự đang được selector chọn**. Khi Start chạy từ 0 lên 100, từng phần thoát khỏi phạm vi bị đẩy/ẩn/làm mờ và trở về hình thức gốc. Transform / Opacity của layer vẫn 100.

Đây là chuyển động kết hợp có thứ tự: chữ đang bị dịch và mờ → selector đi qua → chữ về đúng chỗ, sắc nét và hiện đủ. Chỉ keyframe Transform / Opacity của cả layer sẽ không tái tạo được cách dựng theo từ/dòng/ký tự.

Các thời gian cuối có biến thể giữa scene. Ví dụ Heading R4 ở Scene 6 thoát bằng End từ f130 đến f160, không phải lúc nào cũng f172–202. Bảng chi tiết 26 text nằm trong `BANG-TEXT-VA-KEYFRAME.md`.

## 4. Keyframe ở đâu: ví dụ Scene 1

Đường đọc trong AE:

- Mở nhánh template copy 23.x → Scene 1 → Edits → Texts → Text 1.
- Text layer → Text → Animator 1 → Range Selector 1 → Start.
- Chuyển động riêng của từng từ nằm ở đây; Transform của text source không có keyframe.
- Trở lại Scene 1 để xem layer Title 1, Title 2 và các lớp kính.

| Thành phần | Offset của pre-comp trong Scene 1 | Mốc trên timeline Scene 1 |
|---|---:|---|
| Visual Graphics | f27 | Bắt đầu f27; hiện đủ f57; bắt đầu rút f180; hết f210 |
| Motion Design | f55 | Bắt đầu f55; hiện đủ f85; bắt đầu rút f180; hết f210 |
| Glass Stroke / Glass Effects của nhãn | f55 | Opacity f55=0 → f85=100 → f180=100 → f210=0 |
| Glass Mask 2 của ảnh | f60 | Size f60=[0,0] → f90=[2500,4180] → f165=[2500,4180] → f195=[0,1024] |
| Image Scene 1 | f67 | Layer ảnh bắt đầu ở f67; kết quả hiện hình còn phụ thuộc mask và pre-comp |

Ví dụ: keyframe f30 trong Text 1 không phải frame 30 của Scene 1. Vì Title 1 bắt đầu f27 và source bên trong bắt đầu f0, key đó xuất hiện ở f57 của Scene 1. Với scene khác còn phải cộng offset của Scene trên master và xử lý stretch/time remap nếu có.

Nhịp vào của chữ chính và nhãn phụ lệch **28 frame = 0,9333 giây**. Nhịp ra của hai nhóm lại đồng bộ ở f180–210. Cách dàn thời gian này tạo thứ bậc khi vào, rồi gom nhóm khi kết cảnh.

## 5. Position, Scale, Rotation, Anchor Point và Opacity

### Text source và pre-comp không dùng cùng hệ tọa độ

- Scene dọc: 2160×3840, tâm [1080,1920].
- Nhiều Text/Title pre-comp nằm ngang: 3840×2160, tâm [1920,1080].
- Text layer thật trong Text source có Anchor Point [0,0,0], gắn với hệ gốc/baseline chữ; không phải tâm của Scene.
- Parent biến đổi tiếp vị trí/tỷ lệ của con. Một Position của con có parent là tọa độ local, không thể đọc thẳng thành vị trí cuối trên khung hình.

### Ví dụ chính xác của Scene 1

| Layer | Anchor Point | Position | Scale | Rotation | Opacity Transform |
|---|---|---|---|---:|---:|
| Text layer thật của Text 1 | [0,0,0] | [1925,2499;1154,25;0] | [100,100,100] | 0 | 100 |
| Title 1 trong Scene 1 | [1920,1080,0] | [1080,2952,0] | [75,75,100] | 0 | 100 |
| Text layer thật của Text 2 | [0,0,0] | [1919,5199;1102,56;0] | [100,100,100] | 0 | 100 |
| Title 2 trong Scene 1 | [1920,1080,0] | [1080,3340,0] | [100,100,100] | 0 | 100 |

Các giá trị này là tĩnh. Trong Scene 1, cảm giác chữ trồi lên đến từ Text Animator, không phải keyframe Position của các hàng trong bảng.

Font chính 300×75%=225 px hiệu dụng trong output rộng 2160. Nếu xuất cùng bố cục ở 1080×1920, nó tương đương khoảng **112,5 px**. Nhãn phụ 96 px với scale 100% tương đương **48 px** ở khổ rộng 1080. Bởi vậy không thể lấy trực tiếp font 300 rồi dùng trên khung 1080.

### Những trường hợp Transform thực sự có keyframe

- **Scene 2 / Title 3 / Position:** f60 [1080,1920,0] → f90 [1080,410,0]. Cả tiêu đề đổi vị trí sau giai đoạn reveal bên trong source.
- **Scene 5 / Title 6 / Scale:** f97 [100,100,100] → f172 [60,60,100] → f202 [0,0,100]. Text source “Ultimate Visuals” không có Animator riêng; hiệu ứng thu chữ nằm ở cấp Scene.
- **Scene 6 / Title 7 / CC Cylinder / Rotation Y:** f18=0° → f318=360°. Đây là rotation của effect, không phải Transform / Rotation của text. Scene dài 8 giây nên chỉ dùng một phần khoảng quay 10 giây đã định nghĩa.
- Anchor Point của text trong các ví dụ trên là tĩnh; không có căn cứ để yêu cầu AI phải animate Anchor Point cho mọi chữ.

## 6. Làm mượt: đây là Bézier đã chỉnh, không chỉ F9

Native xác nhận enum BEZIER=6613, LINEAR=6612, HOLD=6614. Các keyframe reveal điển hình là Bézier, Temporal Auto Bezier=false, Temporal Continuous=false; tay nắm được chỉnh riêng.

**R1 / Start / đoạn f0–30:**

- Key f0, Out: Speed ≈0,00000705; Influence **75,2169715%**.
- Key f30, In: Speed ≈−0,00001077; Influence **75,1205431%**.
- Những speed rất nhỏ gần 0 là dữ liệu số gốc; không phải một lần đi lùi có chủ đích.
- Đường chuẩn hóa gần đúng: `cubic-bezier(0.75217,0,0.24879,1)`.
- Cảm giác: đầu chậm → tăng tốc mạnh ở giữa → giảm tốc về điểm dừng. Không phải spring và không có overshoot đáng kể từ công thức này.

**Mask ảnh / Size / đoạn f60–90:**

- Out Influence khoảng **15,2362572%**, In Influence **100%**; speed đầu/cuối gần 0.
- Chuẩn hóa gần đúng: `cubic-bezier(0.15236,0,0,1)`.
- Mask mở nhanh sớm rồi kéo đuôi giảm tốc dài, khác đường cong của chữ.

`EASING-THUC-TE.png` được vẽ từ **valueAtTime native mỗi 0,25 frame**, không phải đồ thị tự ước lượng. File mẫu nằm ở `raw/native-samples.json`. Hai cubic-bezier nêu trên là cách chuyển gần đúng khi dựng bằng code; nếu dùng AE hãy giữ Speed/Influence gốc.

Temporal easing điều khiển tốc độ theo thời gian. Spatial tangent điều khiển hình dạng đường đi của Position 2D/3D. Hai loại không thay thế cho nhau; dữ liệu tangent đã được giữ trong CSV/JSON khi thuộc tính hỗ trợ.

## 7. Đổ bóng: thông số UI và dữ liệu raw khác nhau

Bóng chữ rõ ràng được áp ở **Scene 5 / Title 1, Title 3, Title 6**, bằng `ADBE Drop Shadow`, nối controller `Text Shadow`.

| Tham số | Giá trị đúng để hiểu/dựng |
|---|---|
| Shadow Color | Đen [0,0,0] |
| Opacity trên UI/controller | **30%** |
| Opacity raw đọc bằng scripting | **76,5 trên thang 0–255** |
| Direction | 135° |
| Distance | 8 px nguồn |
| Softness | 128 px nguồn |
| Shadow Only | Tắt |

Điểm rất dễ sai: nhìn raw 76,5 rồi viết “Opacity 76,5%”. Native đã kiểm controller=30, max của effect=255. Khi làm bằng code cần chuyển opacity về 0,30. Khi xuất 1080 từ hệ nguồn 2160, khoảng cách tương đương 4 px và độ mềm theo hệ nguồn tương đương 64 px; không coi tham số Softness AE là Gaussian sigma CSS có thể chép một-một mà không render đối chiếu.

Tương tự, Glow Threshold raw=153 trên thang 0–255 tương ứng UI=60%; Fill Opacity raw=1 trên thang 0–1 tương ứng UI=100%. Mỗi effect có miền giá trị riêng.

Không phải mọi chữ đều có Drop Shadow. Nhiều giá trị Layer Styles mặc định vẫn đọc được qua API dù group đang tắt. Báo cáo chỉ coi style/effect có nhánh đang bật là đang áp dụng.

## 8. Kính, glow và blur

Nhãn “Motion Design” ở Scene 1 là một tổ hợp:

1. Title 2 chứa text.
2. Glass Stroke: shape viền, parent vào Title 2.
3. Glass Effects: adjustment layer, parent vào Title 2.
4. Glass Mask: alpha matte giới hạn vùng adjustment.
5. CONTROL điều khiển kích thước, bo góc, màu, tint và blur bằng expression.

Thông số nhãn Scene 1:

- Rectangle Size [1024,256], Roundness 128.
- Tint Amount 6%; Gaussian Blur (Legacy) 128.
- Stroke dùng **Bevel and Emboss đang bật**: size 5, angle 90°, altitude 30°, highlight opacity 75%, shadow opacity 50%.
- **Drop Shadow của stroke đang tắt.** Bóng trong Bevel and Emboss không phải Drop Shadow rời đã phân tích ở Scene 5.
- Glass Stroke và Glass Effects có opacity keyframe đồng bộ f55–85–180–210.

Không cần suy diễn đây là mô phỏng khúc xạ kính vật lý. Cấu trúc thật dùng blur nền, tint, matte, viền và bevel.

Blur của chữ là **Text Animator Blur**. Motion Blur cấp comp/layer trong các Scene đã kiểm đang tắt. Gaussian Blur của kính, Glow Radius và CC Radial Blur của nền là các cơ chế khác nữa. Prompt phải gọi đúng loại blur đang cần.

## 9. Chữ cuốn quanh ảnh: Scene 6

- Source strip `Title 7` rộng 6000×2160, anchor [3000,1080,0].
- Hai lớp Title 7 nằm trước và sau lớp ảnh, dùng hai giá trị Render của CC Cylinder là 2 và 3 để xử lý hai phần mặt.
- Radius 100%; Rotation X=19°, Rotation Z=31°.
- Rotation Y ở lớp chính có keyframe f18=0°, f318=360°; lớp phụ phụ thuộc cấu trúc parent.
- Layer chính scale [210,210,100].
- Ambient=200, Diffuse=0, Specular=0; Glow Radius=64, Intensity=1, Threshold UI=60%.

Kết quả là chữ có chiều sâu và bị ảnh che ở phần phía sau. Chỉ xoay Z một dòng chữ phẳng sẽ không có cùng kết quả.

## 10. Phân cấp thị giác và cách chuyển thành prompt

Quan sát source và 22 frame native cho thấy các vai trò chữ được tách rõ:

- Headline lớn, thường 1–2 dòng, chịu trách nhiệm thông điệp chính.
- Display/keyword chọn theo ký tự để tạo nhịp riêng, có thể đổi vị trí ở cấp Scene.
- Heading nhiều dòng có animator vào và ra riêng.
- Body nhỏ, reveal theo dòng từ bên phải, không dùng vũ đạo cỡ lớn của headline.
- Nhãn phụ nằm trong pill kính, vào trễ hơn headline.
- Chữ vòng làm lớp không gian phụ, kết hợp front/back của hình.

Đây là các công thức lấy từ mẫu, không phải quy tắc bất biến cho mọi thương hiệu. Khi đổi nội dung, giữ vai trò và nhịp nhưng phải kiểm chiều dài dòng, thời gian đọc và vùng an toàn. Không đưa nguyên Lorem ipsum, Envato, By Tortoha hoặc chữ mẫu vào video mới khi brief không yêu cầu.

## 11. Cách dùng bộ giao cho Opus

1. Đọc báo cáo này và `MOTION-PRESETS.json` trước. File preset khoảng 40 KB, đủ để bắt đầu, không cần nạp toàn bộ raw gần 200 MB.
2. Khi cần đúng một text/scene, đọc mục tương ứng trong `BANG-TEXT-VA-KEYFRAME.md` hoặc `TEXT-RECIPES.json`.
3. Khi cần đối chiếu keyframe đầy đủ, đọc `analysis/working-1/keyframes.csv` (1.556 hàng dữ liệu). Frame trong CSV là local của comp, không phải master mặc định.
4. Dùng `PROMPT-HOAN-CHINH-OPUS.md` và điền brief. Nếu cần .aep chỉnh layer được, chọn AE native. Nếu chọn Remotion/Three.js phải diễn dịch effect có kiểm chứng, không coi import MP4 là có layer AE gốc.
5. Tạo bài thử nhỏ: headline + pill kính + 1 khung ảnh, rồi render để khóa gu trước khi dựng toàn bộ.

## 12. Đã kiểm và giới hạn

- Đã mở và trích đủ sáu file AEP bằng AE, không dùng suy đoán từ tên file để điền thông số.
- Đã trích text, hierarchy, keyframes, temporal easing, spatial tangent, expression và trạng thái effect/style.
- Đã kiểm missing font bằng API native, đồng thời xác nhận font thay thế qua ảnh render.
- Đã render và giải mã được **22 frame native 540×960**: 12 mốc của Scene 1 và một mốc cho mỗi Scene 2–11. `SCENE-01-CONTACT.jpg` và `SCENE-OVERVIEW.jpg` là ảnh ghép các frame đó.
- RenderQueue trả trạng thái `ERR_STOPPED` 3019 dù ghi ra TIFF; từng TIFF đã được mở/giải mã thành công. Các ảnh là bằng chứng still native, không phải bằng chứng pipeline render toàn video đã đạt. `saveFrameToPng` trước đó không ghi được ảnh nên không dùng làm bằng chứng.
- Chưa render/phát toàn bộ 71 giây, chưa kiểm motion blur ở mọi comp không dùng, chưa nghe nhạc vì Music comp rỗng.
- Font thiếu và expression lỗi được báo lại, chưa sửa file nguồn.
- Hash nguồn trước/sau và kiểm tính toàn vẹn của bộ giao nằm trong `VERIFICATION.json`.

### Tài liệu API dùng để xác định cách đọc

- Adobe Scripts: https://helpx.adobe.com/after-effects/using/scripts.html
- Property / keyframe easing: https://ae-scripting.docsforadobe.dev/property/property/
- Font substitution: https://ae-scripting.docsforadobe.dev/text/fontsobject/

Các tài liệu web giải thích API. Các con số của template trong báo cáo lấy từ dữ liệu native tại máy, không lấy từ một bài hướng dẫn chung trên mạng.
