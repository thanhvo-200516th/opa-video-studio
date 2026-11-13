# BẢNG HƯỚNG DẪN DỰNG TOÀN BỘ VIDEO OPA TRÊN AFTER EFFECTS

> Làm theo thứ tự từ trên xuống. Không chuyển bước khi cột **Kết quả phải thấy** chưa đạt.

## A. Chuẩn bị project — 20 đến 30 phút

| STT | Bạn phải làm | Thao tác chính xác | File sử dụng | Kết quả phải thấy |
|---:|---|---|---|---|
| 1 | Mở After Effects | Khởi động AE → `New Project` | — | Project trắng, không báo lỗi. |
| 2 | Chạy script tạo project | `File > Scripts > Run Script File…` → chọn `06_AFTER_EFFECTS/OPA_SETUP_PROJECT.jsx` | `OPA_SETUP_PROJECT.jsx` | Project có folder `00_MASTER` đến `06_RENDER`, comp `OPA_MASTER_60S` và 8 scene. |
| 3 | Lưu project ngay | `File > Save As` → đặt tên `OPA_BrandFilm_v01.aep` | — | File AEP nằm trong thư mục dự án của bạn. |
| 4 | Chọn 16 bpc | Nhấn chữ `8 bpc` dưới Project panel → chọn `16 bpc` | — | Góc dưới Project panel hiển thị `16 bpc`. |
| 5 | Đặt màu làm việc | `File > Project Settings > Color > Working Space > Rec.709 Gamma 2.4` | — | Project sử dụng Rec.709 Gamma 2.4. |
| 6 | Import logo | `File > Import > File…` | `01_BRAND/opa-logo-official.png` | Logo OPA xuất hiện trong Project panel. |
| 7 | Import storyboard | Chọn toàn bộ 8 PNG trong folder | `03_STORYBOARD_PNG/*.png` | Có đủ S01 đến S08. |
| 8 | Import icon | Chọn toàn bộ 12 PNG trong folder | `05_ICONS_PNG/*.png` | Có 12 icon nền trong suốt. |
| 9 | Import animatic | `File > Import > File…` | `08_REFERENCE/OPA_ANIMATIC_REFERENCE_60S.mp4` | Có video reference đúng 60 giây. |
| 10 | Đưa animatic vào master | Kéo animatic vào `OPA_MASTER_60S`; đặt ở dưới cùng; giảm Opacity 20%; bật Shy | Animatic MP4 | Có thể bật/tắt animatic để so timing. |
| 11 | Bật autosave | `Edit > Preferences > Auto-Save` → 5 phút, 20 phiên bản | — | AE tự lưu dự phòng. |
| 12 | Tạo guide | Trong comp chính: `View > Show Rulers`; kéo guide cách mép trái/phải 120 px | — | Chữ và CTA không vượt vùng an toàn. |

## B. Quy tắc layer áp dụng cho tất cả các scene

| Loại layer | Tên phải dùng | Màu label | Ghi chú |
|---|---|---|---|
| Nền | `BG_White`, `BG_Gradient` | Brown | Luôn đặt cuối timeline. |
| Text | `TXT_Headline`, `TXT_Body`, `TXT_Label` | Yellow | Dùng DM Sans nếu đã cài. |
| Shape/card | `SHP_Card_*` | Blue | Dựng bằng Shape Layer để sửa được. |
| Icon | `ICO_*` | Cyan | Có thể dùng PNG hoặc vẽ lại từ SVG. |
| Null điều khiển | `CTRL_*` | Red | Dùng để parent nhiều layer. |
| Matte | `MAT_*` | Purple | Tắt biểu tượng mắt nếu matte không cần nhìn thấy. |
| Adjustment | `ADJ_*` | Orange | Blur, glow hoặc grade toàn cảnh. |
| Audio | `VO_*`, `MUSIC_*`, `SFX_*` | Green | Voice luôn ở trên music trong timeline. |

## C. Công thức keyframe dùng xuyên suốt

| Hiệu ứng | Frame 0 | Frame giữa | Frame cuối | Tổng thời gian | Graph Editor |
|---|---:|---:|---:|---:|---|
| Card xuất hiện | Position Y +40; Scale 96%; Opacity 0 | Scale 102% | Position chuẩn; Scale 100%; Opacity 100 | 14–16 frame | Đầu 30%, cuối 75–85% Influence |
| Text body xuất hiện | Y +18; Opacity 0 | — | Y 0; Opacity 100 | 10–14 frame | Ease Out |
| Headline mạnh | Scale 112%; Opacity 0 | Scale 97% | Scale 100%; Opacity 100 | 16–20 frame | Hãm mạnh ở cuối |
| Icon pop | Scale 0; Rotation -8° | Scale 112% | Scale 100%; Rotation 0° | 10–12 frame | Overshoot nhẹ |
| Button CTA | Y +24; Scale 98%; Opacity 0 | Scale 103% | Y 0; Scale 100%; Opacity 100 | 14–18 frame | Ease Out |
| Đường vẽ | Trim Paths End 0% | — | End 100% | 18–40 frame | Tăng nhanh rồi hãm |
| Checkmark | Trim Paths End 0% | — | End 100% | 6–8 frame | Ease Out |

**Cách đặt keyframe:** chọn layer → nhấn `P` cho Position, `S` cho Scale, `T` cho Opacity, `R` cho Rotation → nhấn Stopwatch → di chuyển playhead → đổi giá trị. Chọn keyframe và nhấn `F9` để Easy Ease.

---

# D. DỰNG TỪNG SCENE

## Scene 01 — Chaos — 00:00 đến 00:04

| Bước | Việc làm | Thao tác và thông số | Asset | Kết quả phải thấy |
|---:|---|---|---|---|
| 1 | Mở scene | Double-click `S01_CHAOS` | `S01_CHAOS.png` làm reference | Comp dài 4 giây. |
| 2 | Đặt reference | Kéo PNG vào comp; Opacity 30%; khóa layer | Storyboard S01 | Có hình mẫu để canh bố cục. |
| 3 | Tạo headline | Text: `Quá Nhiều Công Cụ. Quá Nhiều Thao Tác.`; DM Sans Bold 72 px | — | Headline nằm phía trên, giữa khung. |
| 4 | Tạo card mẫu | Rounded Rectangle 500×190; Roundness 30; Fill trắng; Stroke 2 px; Shadow 12% | Icon spreadsheet | Một card giống storyboard. |
| 5 | Pre-compose card | Chọn shape, icon, text → `Ctrl+Shift+C` → `COMP_CARD_SPREADSHEET` | — | Card thành một pre-comp. |
| 6 | Nhân thành 4 card | Duplicate và đổi thành Email, CRM, Calendar | 4 icon tương ứng | Bốn card nằm quanh tâm. |
| 7 | Animate card 1 | Dùng công thức Card xuất hiện; bắt đầu frame 5 | — | Card vào nhanh, dừng mềm. |
| 8 | Stagger card | Card 2 trễ 3 frame; card 3 trễ 6; card 4 trễ 9 | — | Card xuất hiện liên tiếp. |
| 9 | Tạo chiều sâu | Card gần Scale 105%; card xa Scale 92–96%; giảm opacity card xa | — | Cảnh có foreground/background. |
| 10 | Tạo camera | New Camera 35 mm + Null `CTRL_Camera`; parent camera vào null | — | Có thể zoom toàn cảnh. |
| 11 | Animate camera | 2 giây cuối: zoom out 10–15% | — | Cuối cảnh hé lộ toàn bộ sự hỗn loạn. |
| 12 | Bật motion blur | Bật biểu tượng Motion Blur cho card và comp | — | Card mượt khi đi nhanh, nét khi dừng. |

**Đạt khi:** xem ở Full Resolution, headline đọc rõ; bốn card không che nhau; không có card nào chạy linear.

## Scene 02 — 10 bước thủ công — 00:04 đến 00:12

| Bước | Việc làm | Thao tác và thông số | Kết quả phải thấy |
|---:|---|---|---|
| 1 | Đặt storyboard S02 | Opacity 30%, khóa layer | Có mẫu pipeline ngang. |
| 2 | Vẽ đường chính | Pen Tool → Shape Layer → Stroke đỏ/cam 5 px → `Add > Trim Paths` | Một đường ngang từ trái sang phải. |
| 3 | Animate đường | End 0% ở frame 0 → 100% tại 2,5 giây | Đường được vẽ dần. |
| 4 | Tạo node mẫu | Circle 76 px; Fill trắng; Stroke đỏ 5 px; số `01` ở giữa | Một node rõ và cân. |
| 5 | Nhân 10 node | Căn đều bằng `Window > Align` | Mười node có khoảng cách đều. |
| 6 | Thêm label | Tạo lead, Tìm email, Soạn nội dung, Gửi, Chờ, Follow-up, Đánh giá, Đặt lịch, CRM, Meeting | Mỗi label tối đa hai từ hoặc rất ngắn. |
| 7 | Animate node | Scale 0 → 115 → 100 khi đầu Trim Path đi tới | Node nảy nhẹ đúng thời điểm. |
| 8 | Stagger label | Label vào sau node 2 frame; Y +14 → 0; Opacity 0 → 100 | Label không xuất hiện quá sớm. |
| 9 | Tạo token | Circle 28 px màu đỏ; copy Path pipeline và paste vào Position | Token chạy dọc pipeline. |
| 10 | Camera pan | Pan nhẹ từ node 1 sang node 10 | Người xem cảm nhận quy trình dài. |

**Đạt khi:** khán giả hiểu “nhiều bước” dù không đọc đủ mười label; token không chạy vượt trước đường vẽ.

## Scene 03 — Freeze và logo — 00:12 đến 00:21

| Bước | Việc làm | Thao tác và thông số | Asset/Kết quả |
|---:|---|---|---|
| 1 | Đặt pipeline mờ | Dùng frame cuối S02 hoặc pre-compose pipeline; Opacity 15–25% | Nền gợi lại cảnh trước. |
| 2 | Tạo dòng nhỏ | `Mất Quá Nhiều Thời Gian Cho`; 36 px; Slate | Hiện trước headline. |
| 3 | Tạo headline | `10 Bước Thủ Công`; 100 px; Bold; đỏ/cam | Là điểm nhìn chính. |
| 4 | Animate headline | Scale 125 → 96 → 100; Opacity 0 → 100 trong 17 frame | Cảm giác bị đóng dấu. |
| 5 | Tạo underline | Rectangle cao 10 px; Anchor Point về trái; Scale X 0 → 100 | Gạch chân mở từ trái sang phải. |
| 6 | Hút card vào tâm | Card Position về tâm; Scale → 0; Rotation 8–20°; stagger 2 frame | Vấn đề bị thu gọn. |
| 7 | Đặt logo chuẩn | Import `opa-logo-official.png`; đặt chính giữa | Dùng logo thật, không gõ chữ OPA. |
| 8 | Reveal logo không plugin | Scale 92 → 103 → 100; Opacity 0 → 100 | Logo xuất hiện sạch. |
| 9 | Saber tùy chọn | Solid → Saber → Layer Masks; End Offset 0 → 100; fade Saber về 0 | Glow chỉ tồn tại lúc vẽ. |
| 10 | Giữ logo | Logo dừng hoàn toàn ít nhất 12 frame | Người xem nhận diện được thương hiệu. |

## Scene 04 — Ba trụ cột — 00:21 đến 00:27

| Bước | Việc làm | Thao tác | Kết quả |
|---:|---|---|---|
| 1 | Tạo ba card | Marketing, Công Nghệ, AI; 470×210; Roundness 30 | Ba card cùng hệ thiết kế. |
| 2 | Thêm icon | Target/marketing, technology, ai | Icon nằm trong circle màu nhạt. |
| 3 | Animate card trái | X -80 → 0; Scale 96 → 102 → 100 | Marketing vào từ trái. |
| 4 | Animate card phải | X +80 → 0 | AI hoặc Công nghệ vào từ phải. |
| 5 | Animate card giữa | Y +60 → 0 | Card giữa vào sau 3–4 frame. |
| 6 | Vẽ đường nối | Trim Paths từ card về core giữa | Ba năng lực hội tụ. |
| 7 | Tạo headline cuối | `Marketing × Công Nghệ × AI` | Headline gradient xanh–tím. |
| 8 | Chuẩn bị match cut | Đường cuối scene nằm đúng vị trí đường đầu S05 | Hai scene nối liền không nhảy. |

## Scene 05 — AI Pipeline — 00:27 đến 00:39

| Bước | Việc làm | Thao tác và thông số | Kết quả |
|---:|---|---|---|
| 1 | Tạo component node | Card 380×220; icon, title, description, status dot | Một node hoàn chỉnh. |
| 2 | Nhân 4 node | Kết nối CRM; AI Chấm Điểm Lead; Follow-Up Tự Động; Meeting Booked | Bốn node căn đều. |
| 3 | Tạo trạng thái Idle | Opacity 40%; border xám | Node chưa hoạt động mờ. |
| 4 | Tạo trạng thái Active | Opacity 100%; border xanh; Scale 104% | Chỉ một node active. |
| 5 | Tạo trạng thái Complete | Nền xanh rất nhạt; icon check | Node đã xử lý dịu lại. |
| 6 | Vẽ pipeline | Shape Stroke 8–10 px chạy sau card | Một tuyến dữ liệu liên tục. |
| 7 | Tạo token | Circle 30 px gradient xanh–tím | Token là chủ thể chuyển động chính. |
| 8 | Cho token chạy | Copy path vào Position; dừng 8–12 frame tại mỗi node | Token đi lần lượt 1→4. |
| 9 | Node 1 micro-motion | Icon link hoặc database pulse | Hiểu CRM đã kết nối. |
| 10 | Node 2 counter | Slider Control 0 → 92; Source Text `Math.round(effect("Score")("Slider"))+"/100"` | Hiện `92/100`. |
| 11 | Node 3 email | Flap Rotation mở; arrow Position đi ra | Hiểu follow-up đã gửi. |
| 12 | Node 4 check | Trim Paths dấu check 0 → 100 trong 8 frame | Meeting booked hoàn thành. |
| 13 | Giữ kết quả | Hold node cuối ít nhất 20 frame | Khán giả đọc được kết quả. |
| 14 | Thêm SFX | Một click nhẹ tại từng node; chime rõ nhất ở node 4 | Hình và âm khớp đúng frame. |

**Đạt khi:** tắt voice-over vẫn hiểu quy trình; chỉ token và node active thu hút mắt; không có bốn node cùng glow.

## Scene 06 — Hệ sinh thái dịch vụ — 00:39 đến 00:47

| Bước | Việc làm | Thao tác | Kết quả |
|---:|---|---|---|
| 1 | Tạo card lớn | Marketing Đa Nền Tảng; nền xanh nhạt | Card chiếm khoảng 45% chiều ngang. |
| 2 | Tạo hai card phụ | Giải Pháp Công Nghệ; Ứng Dụng AI | Xếp dọc bên phải. |
| 3 | Thêm tag | Mỗi card tối đa 3–4 tag | Text không quá dày. |
| 4 | Tạo matte reveal | Rectangle Scale Y 0 → 100; card Y +24 → 0 | Card mở ra sạch. |
| 5 | Stagger card | Card lớn vào trước; card phụ trễ 5 frame | Có hierarchy. |
| 6 | Animate tag | Trễ nhau 2 frame | Tag hiện lần lượt, không đồng loạt. |

## Scene 07 — Kết quả — 00:47 đến 00:54

| Bước | Việc làm | Thao tác | Kết quả |
|---:|---|---|---|
| 1 | Xác minh số liệu | Chỉ dùng 3×, 10K+, 95% khi OPA duyệt | Không xuất bản claim chưa xác nhận. |
| 2 | Tạo ba stat card | Cùng kích thước, cùng spacing | Ba cột cân bằng. |
| 3 | Tạo counter 3× | Slider 0 → 3; thêm `×` trong expression | Số dừng ở 3×. |
| 4 | Tạo counter 10K+ | Slider 0 → 10; thêm `K+` | Số dừng ở 10K+. |
| 5 | Tạo counter 95% | Slider 0 → 95; thêm `%` | Số dừng ở 95%. |
| 6 | Stagger | Counter sau trễ hơn counter trước 5 frame | Số chạy lần lượt. |
| 7 | Settle | Khi đạt số cuối: Scale 100 → 104 → 100 | Kết quả có điểm kết thúc. |
| 8 | Hold | Giữ toàn bộ số ổn định ít nhất 1,2 giây | Khán giả đọc đủ. |

## Scene 08 — CTA — 00:54 đến 01:00

| Bước | Việc làm | Thao tác | Kết quả |
|---:|---|---|---|
| 1 | Đặt logo chuẩn | Chính giữa, hơi cao hơn tâm | Logo có khoảng thở. |
| 2 | Tạo tagline | `Tăng Trưởng Thông Minh.` và `Mở Rộng Nhanh Hơn.` | Dòng hai dùng gradient. |
| 3 | Mask reveal tagline | Text Y +24 → 0 trong matte | Hai dòng vào cách nhau 4 frame. |
| 4 | Tạo CTA | Rounded Rectangle xanh; text `Đăng Ký Tư Vấn Miễn Phí` | Button rõ, không quá lớn. |
| 5 | Animate CTA | Y +24 → 0; Scale 98 → 103 → 100 | CTA vào mềm. |
| 6 | Light sweep | CC Light Sweep chạy một lần | Không loop ánh sáng. |
| 7 | Thêm website | `opa.business` dưới CTA | Đọc rõ ở màn hình nhỏ. |
| 8 | Hold cuối | Giữ toàn bộ frame tĩnh ít nhất 1,5 giây | Video kết thúc chắc chắn. |

---

# E. ÂM THANH VÀ NHỊP

| Track | Mức tham khảo | Việc phải làm |
|---|---:|---|
| Voice-over | Peak -6 đến -3 dB | Đặt trước, cắt scene theo câu thoại. |
| Music | Khoảng -24 đến -18 dB dưới voice | Hạ nhạc khi giọng đọc dày. |
| Whoosh | Khoảng -18 đến -10 dB | Chỉ dùng ở chuyển cảnh lớn. |
| UI click | Khoảng -24 đến -16 dB | Khớp frame node active. |
| Final chime | Khoảng -16 đến -10 dB | Dùng ở Meeting Booked hoặc CTA. |
| Master | Không vượt -1 dB | Không được clipping. |

## Điểm đặt SFX

| Timecode | SFX |
|---:|---|
| 00:00–00:04 | Card pop nhỏ, paper/UI movement |
| 00:04 | Pipeline start whoosh |
| 00:12 | Impact ngắn khi freeze |
| 00:16–00:21 | Energy rise/logo chime |
| 00:27 | Digital whoosh mở AI pipeline |
| Mỗi node S05 | Soft click |
| Node Meeting Booked | Confirmation chime |
| 00:47 | Statistic rise nhẹ |
| 00:54 | Brand resolve/chime |

---

# F. KIỂM TRA TRƯỚC KHI RENDER

| STT | Kiểm tra | Đạt khi |
|---:|---|---|
| 1 | Xem không âm thanh | Vẫn hiểu vấn đề → giải pháp → kết quả → CTA. |
| 2 | Chỉ nghe âm thanh | Voice rõ, music không lấn, SFX không quá nhiều. |
| 3 | Xem Full Resolution | Không có layer nhảy, matte hở hoặc chữ rung. |
| 4 | Kiểm tra chữ | Mỗi dòng bắt đầu bằng chữ hoa; dấu tiếng Việt không bị cắt. |
| 5 | Kiểm tra Graph Editor | Không có chuyển động linear ngoài progress/token chủ ý. |
| 6 | Kiểm tra logo | Dùng đúng `opa-logo-official.png`, không méo tỷ lệ. |
| 7 | Kiểm tra claim | Số liệu đã được OPA xác nhận. |
| 8 | Kiểm tra CTA | Giữ đủ 1,5 giây và đọc được khi thu nhỏ preview 50%. |
| 9 | Kiểm tra mobile | Xem thử video trên màn hình điện thoại. |
| 10 | Xem file render lại | Không chỉ xem RAM Preview trong After Effects. |

# G. RENDER

| Bản | Thiết lập |
|---|---|
| Master | QuickTime → Apple ProRes 422 HQ → 1920×1080 → 30 fps → PCM 48 kHz |
| Web/Social | H.264 High Profile → VBR 2 Pass → Target 16–20 Mbps → Max 24–30 Mbps → AAC 320 kbps |
| Tên file | `OPA_BrandFilm_60s_16x9_Web_v01.mp4` |

## Thứ tự làm thực tế

1. Hoàn thành S01 và render thử 4 giây.
2. Hoàn thành S02–S03 và kiểm tra transition.
3. Hoàn thành S04–S05; đây là phần quan trọng nhất.
4. Hoàn thành S06–S08.
5. Ghép voice-over.
6. Thêm music và SFX.
7. Xem ba vòng QA.
8. Render master trước, H.264 sau.

Không dựng cả tám scene cùng lúc. Hoàn thiện chuyển động của một card và một node trước; sau đó nhân hệ thống đó cho toàn bộ video.
