# kb-real-estate-video-editing — toàn văn tài liệu của nguồn `real-estate-video-editing`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/real-estate-video-editing/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: real-estate-video-editing/MODULE.md ===== -->

<!-- master-video-edit: mô-đun nhập 2026-10-29 -->
> **Mô-đun `real-estate-video-editing`** của `master-video-edit` — kiến thức tham khảo (không chạy công cụ trong file nếu chưa có).
> Thêm gì: Approved real-estate vertical style: 2K 1440x2560, word-timed gradient text, feathered property photos
> Nguồn (USB): `/media/vmiz/Over Powers/MMO/real-estate-video-editing`
> **Khi dùng trên máy Linux này:**
> - font '1FTV Autography' (and optional 'Fz Photograph') not installed: supply or substitute (Montserrat is installed)
> - drop agents/openai.yaml and the Codex $real-estate-video-editing invocation
> - mark the beach/gate coordinates and timing table as examples
> Công cụ OpenChatCut nhắc trong file (nếu có) chỉ dùng được khi app OpenChatCut mở, qua MCP `openchatcut`; không có thì làm bằng ffmpeg / faster-whisper / FilmCraft.

---
name: real-estate-video-editing
description: Dựng và chỉnh sửa video bất động sản dọc từ footage, lời thoại, storyboard/PDF và ảnh tham chiếu. Dùng cho clip BĐS có chữ Montserrat xanh dương hoặc xanh lá gradient, chữ viết tay vàng, glow nhẹ, ảnh thay đổi theo ý thoại, motion chữ khớp từng từ, giữ tiếng gốc và xuất 2K; áp dụng khi người dùng yêu cầu video BĐS theo phong cách đã chốt hoặc gọi $real-estate-video-editing.
---

# Real Estate Video Editing

Tạo video BĐS sang, thoáng, đặt người dẫn và tiếng nói làm trung tâm. Dùng storyboard/PDF và hình người dùng đã duyệt làm chỉ dẫn bố cục, nhưng lấy **lời thoại thật trong footage** làm nguồn nội dung và thời gian hiển thị. Đọc [visual-system.md](references/visual-system.md) trước khi thiết kế và [delivery-qa.md](references/delivery-qa.md) trước khi xuất.

## Quy trình

1. Kiểm tra nguồn bằng `ffprobe`: thời lượng, frame rate, rotation, video, audio, kích thước. Xem các frame đầu/giữa/cuối và mọi ảnh người dùng khoanh. Giữ nguyên mặt, người, chuyển động và tiếng gốc.
2. Chép nguyên lời thoại có dấu; đối chiếu những chữ dễ nhầm. Tạo mốc bắt đầu **từng từ** hoặc âm tiết được chọn lên màn hình. Nếu có PDF, đối chiếu lại từng cụm trong PDF với thoại và sửa nội dung sai trước khi dựng; không sao chép những khẩu hiệu minh hoạ không xuất hiện trong giọng nói.
3. Chọn **vài ý chính**, không chạy phụ đề toàn bộ. Ghi mốc bắt đầu từng từ được nhấn bằng nghe lại footage và waveform/ASR; ASR chỉ là bản nháp. Cho từng từ bắt đầu fade đúng lúc âm của từ đó vang lên (trễ tối đa vài frame), không hiện cả cụm trước lời và cũng không đợi nói xong cụm mới hiện. Từ trước tiếp tục đứng yên khi từ kế tiếp xuất hiện; giữ cả cụm đủ đọc rồi fade out theo nhịp kế tiếp, tránh chớp tắt từng 0,1 giây. Chữ rút gọn phải đúng nghĩa, nhất là số tiền và địa danh.
4. Dùng **nhiều ảnh phù hợp từng ý thoại**: ví dụ hình dự án/khu nhà, bối cảnh địa điểm, rồi nội thất/căn hộ. Chuyển ảnh bằng fade mềm tại ranh giới ý, không giữ một ảnh lặp suốt clip. Đặt ảnh phía trên chữ trong vùng an toàn theo [visual-system.md](references/visual-system.md); giữa ảnh phải rõ, mép tan mềm, không che mặt/người/chữ. Không đặt nhãn “Hình ảnh minh hoạ” lên video.
5. Dùng Montserrat Bold/ExtraBold cho chữ chính, gradient **xanh dương hoặc xanh lá** sao cho đủ tương phản với background; chữ phụ bằng font viết tay người dùng cung cấp, màu **vàng**. Glow cùng màu nhẹ, sắc nét ở lõi chữ; tránh viền đen dày, bóng tối gắt hoặc neon lòe. Giữ trục chữ ở giữa và chừa khoảng cho dấu tiếng Việt. Không thêm đường kẻ, thẻ, logo, badge hay mảng đen nếu người dùng không yêu cầu.
6. Cho từng từ fade in khoảng 0,12–0,22 giây, nhích lên/settle nhẹ hoặc pop rất nhỏ; giữ từ đã xuất hiện để tạo thành cụm, fade out toàn cụm khoảng 0,25–0,4 giây. Không dùng fade out cho từng từ ngay khi từ kế tiếp bắt đầu. Ảnh fade riêng, không giật. Nếu thêm click/chime, để nhỏ hơn lời thoại và đặt đúng mốc từ.
7. Xuất MP4 dọc **2K 1440×2560**, H.264 + AAC, giữ frame rate nguồn nếu phù hợp. Không tự xuất 1080×1920 làm bản giao cuối. Kiểm tra theo [delivery-qa.md](references/delivery-qa.md), sửa rồi mới gửi.

## Điều kiện ưu tiên

- Nếu người dùng đưa font, ảnh, bố cục hoặc màu mới, dùng yêu cầu mới nhất của họ. Ở dự án đã duyệt, font chính là Montserrat Bold/ExtraBold; font viết tay đã dùng là `1FTV Autography`. Nếu người dùng cấp `Fz Photograph` và yêu cầu cụ thể, dùng font đó; kiểm tra glyph tiếng Việt và không thay bằng font khác một cách âm thầm.
- Nếu yêu cầu storyboard PDF trước video, tạo PDF 4 trang với khung hình, mốc thoại, chữ chính/phụ và hướng chuyển động, rồi dựng clip khi họ yêu cầu. Nếu họ yêu cầu video trực tiếp, tiến hành dựng; PDF không phải bước bắt buộc.
- Dùng hình thật của dự án khi có. Hình AI/chung chỉ diễn tả cảm giác BĐS; không biến nó thành khẳng định về công trình cụ thể. Không để bất kỳ chữ nào được tạo sẵn trong ảnh minh hoạ lọt vào video.
- Không thay tiếng gốc bằng track rỗng hoặc chỉ có SFX. Khi ghép âm, chọn đúng stream voice, giữ đoạn thoại theo đúng vị trí thời gian, rồi xác minh trong MP4 cuối.

<!-- ===== /file: real-estate-video-editing/MODULE.md ===== -->

<!-- ===== file: real-estate-video-editing/references/delivery-qa.md ===== -->

# Kiểm tra trước khi giao video

1. **Lời và chữ:** Nghe lại âm đầu của từng từ được nhấn và so với frame đầu tiên có chữ. Xem frame ngay trước âm, lúc âm bắt đầu, 0,2 giây sau và lúc fade out. Không hiện chữ sớm, không đợi người dẫn nói xong cụm mới hiện. Từ trước phải còn trên màn hình khi từ sau vào; toàn cụm ở lại đủ đọc và fade mềm, không nhấp nháy. Kiểm tra dấu, số tiền và địa danh.
2. **Ảnh và safe area:** Xem từng lần đổi ảnh ở kích thước điện thoại. Có ảnh khác nhau phù hợp các ý thoại; ảnh đủ rõ giữa, mép mờ mềm, chuyển không giật, không che người/mặt/chữ. Không có chữ “Hình ảnh minh hoạ”. Không có chữ/ảnh chạm vùng crop phía trên hoặc hai mép.
3. **Tiếng:** Xác nhận video gốc có audio stream và file cuối vẫn có AAC stream. Giải mã file cuối, đo âm lượng/RMS; nghe những đoạn đầu, giữa và cuối hoặc so dạng sóng tiếng gốc với đầu ra để chắc giọng gốc được giữ. SFX chỉ là lớp phụ, không nuốt chữ, không clipping.
4. **Hình:** `ffprobe` phải cho thấy 1440×2560, H.264, thời lượng đúng với source và frame rate hợp lý. Xem frame đại diện để kiểm tra lõi chữ gradient xanh dương/xanh lá rõ trên background, chữ phụ vàng, glow nhẹ thực sự có nhưng không lóa, không viền đen thô, motion fade/nhích mượt. Không dựa chỉ vào tên file “2K”.
5. **Giao:** Cung cấp MP4 cuối cùng; khi chỉnh vòng sau, thay đúng video trước để người dùng không phải phân biệt nhiều bản. Nêu ngắn gọn những thay đổi và kết quả kiểm tra tiếng.

## Ví dụ nhịp đã duyệt (chỉ dùng cho footage này)

| Tiếng nói | Chữ màn hình | Bắt đầu |
| --- | --- | ---: |
| 5 phút di chuyển từ dự án | 5 PHÚT / di chuyển từ dự án | 1.52 / 1.90 s |
| không khí biển Hạ Long mỗi ngày | KHÔNG KHÍ BIỂN / Hạ Long mỗi ngày | 4.54 / 5.06 s |
| một căn hộ không chỉ để ở | MỘT CĂN HỘ / không chỉ để ở | 6.96 / 7.42 s |
| tận hưởng cuộc sống | TẬN HƯỞNG / cuộc sống | 8.86 / 9.28 s |

Lấy mốc từng từ từ nguồn mới khi dựng footage khác. Các con số trên không phải timing mặc định cho mọi clip.

<!-- ===== /file: real-estate-video-editing/references/delivery-qa.md ===== -->

<!-- ===== file: real-estate-video-editing/references/visual-system.md ===== -->

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

<!-- ===== /file: real-estate-video-editing/references/visual-system.md ===== -->
