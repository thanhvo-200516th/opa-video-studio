# OPA Agent — Ads 01: phương án dựng After Effects

Nguồn kịch bản: [Video 01 — Tổng quan OPA Agent](https://opa-agent-video-roadmap-pitch.vercel.app/#video-01), đọc ngày 21/10/2026. Bản dựng giữ 5 nhịp **0–5 / 5–11 / 11–22 / 22–30 / 30–36 giây**. Ưu tiên 1920 × 1080; có bản 1080 × 1920 được sắp lại bố cục. Cả hai 30 fps, 36 giây, pixel vuông.

## Hướng mỹ thuật

Một chủ shop, hai trạng thái: đầu video bị tin nhắn bao vây; sau kết nối OPA, công việc đi vào luồng rõ ràng. Minh họa phẳng 2D, nền trắng xanh, chữ lớn, giao diện dạng thẻ; phần nỗi đau chuyển sang xanh đêm. Xanh OPA lấy từ logo gốc, gần #0068FF. Cam dành cho quá tải, xanh lá cho thao tác hoàn tất. Không dùng số liệu tăng doanh thu hay chứng thực chưa có trong kịch bản.

Headline dùng Montserrat Bold / ExtraBold; phần giải thích và UI dùng Arial để giữ dấu tiếng Việt. Cụm nhấn `THỜI GIAN?`, `OPA tự động hóa`, `OPA lo việc lặp lại` tách text layer, đổi font và có hiệu ứng riêng. Dòng hiển thị bắt đầu bằng chữ hoa. Dấu xuống dòng là chủ đích bố cục, sửa câu dài cần kiểm tra lại hình.

## Storyboard và cách dựng

| Đoạn | Bản 16:9 | Chuyển động / layer AE | Bản 9:16 |
|---|---|---|---|
| 0–5s — Hook | Chủ shop quay lưng bên trái; headline bên phải; đồng hồ ở trên; 3 tin nhắn xuất hiện quanh bàn | Nhân vật gồm đầu, tóc, cổ, áo, tay, laptop, ghế, bàn, chậu cây; null điều khiển nhịp người. Kim đồng hồ quay bằng expression. Bubble scale 82 → 104 → 100%, opacity và position có easing. Cụm `THỜI GIAN?` trượt lên cùng gạch chân mở ngang. | Headline ở trên, nhân vật ở giữa/dưới; bubble phân bố quanh nhân vật. Giữ phần chữ quan trọng trong x=90–900. |
| 5–11s — Pain | Màn hình inbox nhiều trang bên trái, ba thẻ nỗi đau bên phải; nền tối dần | `UI_01_INBOX_OVERLOAD` dựng lại bằng shape/text. Trạng thái chờ nhấp nháy, từng hàng hội thoại vào lệch nhịp. Nền tối thêm nhẹ, ba pain card trượt lên lần lượt. | Inbox nằm dưới headline, ba thẻ nỗi đau xếp dọc phía dưới. |
| 11–22s — Solution | Giao diện chat → POS bên trái; headline và 5 pill bên phải; mascot xuất hiện nhỏ | Vòng tròn xanh phủ khung hình quanh mốc 11s rồi tan. Tin hỏi ở 0.4s của cảnh, AI trả lời ở 1.4s, yêu cầu lên đơn ở 3.2s, xác nhận ở 5.4s, thẻ POS vào ở 6.4s. Năm pill lần lượt vào theo nhịp: tồn kho, chốt đơn, xác minh ảnh, nhắc giỏ, tiếp quản. Icon là shape, dấu check dùng Trim Paths. | Headline → UI → năm pill xếp dọc; cùng nội dung, bố cục riêng. Không crop nguyên bản ngang. |
| 22–30s — Relief | Chủ shop thư giãn bên trái; ba check card bên phải | Rig chủ shop riêng với tay dang, mắt, miệng cười. Ba check card vào cách nhau 1.85s; check vẽ bằng Trim Paths. Giữ cảnh kết để người xem đọc. | Nhân vật thu gọn dưới headline; ba check card xếp dọc phía dưới. |
| 30–36s — CTA | Mascot bên trái; logo, lời hứa, nút CTA và URL bên phải | Logo gốc giữ PNG trong precomp đúng vùng alpha. Mascot 2D gồm các shape riêng. CTA pop-in; con trỏ vào và click; vòng click lan ra. Kết thúc có hold để đọc domain. | Logo ở trên, mascot ở giữa, lời hứa và CTA ở dưới. URL giữ một dòng trong vùng an toàn. |

Chuyển cảnh dùng cut ở mốc 5, 22 và 30s; vòng tròn xanh tại 11s tạo điểm đổi trạng thái. Native Motion Blur bật, shutter angle 180°. Không cần Saber, FX Console hay plugin trả phí để mở project.

## Cấu trúc chỉnh sửa

| Thư mục trong Project panel | Nội dung |
|---|---|
| `00_EXPORT — Open MASTER here` | Hai master theo tỷ lệ, marker 5 cảnh, audio VO/BGM/SFX riêng |
| `01_SCENES_16x9 — Edit text + motion` | H_S01_HOOK đến H_S05_CTA |
| `02_SCENES_9x16 — Reflowed layout` | V_S01_HOOK đến V_S05_CTA |
| `03_UI_COMPONENTS — Shared demo interface` | Inbox quá tải và chat tự động → POS; chỉnh một lần cập nhật cả hai tỷ lệ |
| `04_CHARACTERS + LOGO — Native rigs` | Chủ shop bận, chủ shop thư giãn, mascot 2D, đồng hồ, logo |
| `05_FOOTAGE — Replace brand / voice` | Logo gốc, ảnh mascot tham chiếu, VO placeholder, BGM và SFX |
| `99_README + QA` | Hướng dẫn ngay trong AE, color controller, báo cáo cấu trúc |

`TXT_` là chữ sửa được; `CARD_`, `PILL_`, `ICON_`, `BG_` là shape; `CTRL_` là null/controller. `GUIDE_SAFE` là guide layer tắt sẵn và không xuất vào video. Khi chỉnh text riêng từng tỷ lệ, vào đúng thư mục H hoặc V.

Text/shape trực tiếp có thể Ctrl+D rồi sửa độc lập. Nhân bản một **precomp layer** vẫn dùng chung source: để tạo phiên bản nội dung độc lập, nhân bản composition trong Project panel rồi thay source layer. Các UI/rig dùng chung là chủ đích để sửa đồng thời hai tỷ lệ.

## Âm thanh và lời bình

- `SFX-36s-original.wav`: tiếng tích tắc và tin nhắn trong đoạn đầu, whoosh ở mốc chuyển, tick khi hoàn tất, click CTA và âm logo.
- `BGM-36s-original-guide.wav`: nhạc điện tử tối giản 120 BPM bắt đầu ở đoạn giải pháp; là nhạc guide tự tổng hợp để dựng nhịp, có thể thay bằng bài đã cấp phép.
- `VO-REPLACE-36s-silent.wav`: track im lặng có chủ đích, đặt sẵn trong cả hai master; **chưa phải giọng đọc**.
- Lời bình gốc và bản rút gọn đề xuất nằm ở `03-LOI-BINH.md`. Đoạn pain gốc dài nhất so với 6 giây được cấp. Thu lời bình rồi chỉnh nhịp theo câu thật; không ép tốc độ đọc nếu nghe gấp.

## Những lựa chọn cần chốt ở khâu cuối

1. Thay VO bằng bản thu thật và căn lại điểm vào/ra theo marker.
2. Duyệt câu chữ, tính năng và ưu đãi dùng thử; URL `chat.overpowers.agency` được giữ theo nguồn kịch bản, chưa kiểm tra đăng nhập hoặc ưu đãi ở runtime.
3. Duyệt mascot: bản 2D trong video là diễn giải dựng riêng từ hướng bò xanh, chưa được coi là mascot thương hiệu đã duyệt. Ảnh mascot gốc trên máy được kèm làm tham chiếu.
4. Nếu cần UI chính xác từng pixel, thay minh họa bằng quay màn hình OPA/Pancake POS đã xác nhận. UI hiện tại thể hiện câu chuyện, không phải bằng chứng sản phẩm đang vận hành.
5. Nghe và cân nhạc/SFX với VO; kiểm tra lại cả hai tỷ lệ khi đổi câu dài.

Kịch bản nguồn nhắc SMIT Ads Check Pro. Bản này triển khai cấu trúc và timing trong bảng nguồn; không khẳng định đã tái tạo chính xác khung hình hoặc animation của video SMIT.
