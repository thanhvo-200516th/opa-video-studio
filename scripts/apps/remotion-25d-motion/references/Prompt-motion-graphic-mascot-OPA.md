Owner: Hùng (thiết kế) · phối hợp Thành (nội dung)
Ngày cập nhật: 06/10/2026
Trạng thái: Nháp, chờ Minh duyệt lời thoại và giá. File mới, không thay file nào.

# Bộ prompt dựng motion graphic quảng cáo OPA với mascot Bò

## Cách dùng (đọc trước)

1. Chép cả thư mục `Motion-graphic-mascot/` (gồm `logo/`) vào thư mục làm việc của Claude Code.
2. Mở Claude Code tại thư mục đó. Dán **Prompt 0** trước (dựng nền thương hiệu + mascot dùng chung). Chỉ chạy Prompt 0 một lần.
3. Sau đó dán từng **Prompt V1 → V7**, mỗi lần một video. Mỗi prompt đều nhắc lại "theo BRAND-SPEC", nên có thể chạy ở phiên mới.
4. Giá đang là đề xuất đến khi chốt **15/10**. Trước 15/10 chỉ render bản **không có giá** (`SHOW_PRICE=false`). Sau 15/10 điền giá vào `prices.json` rồi render lại.
5. AI dựng, người duyệt: mọi video phải qua Hùng (hình) và Minh (lời, giá) trước khi đăng.

Ký hiệu `{{...}}` là chỗ cần điền. Không tự bịa số kết quả khách hàng.

---

## Prompt 0: Dựng nền thương hiệu và mascot (chạy 1 lần)

```text
Bạn là motion designer + kỹ sư dựng video. Dự án: bộ video quảng cáo motion graphic cho OPA (OverPowers Agency), đối tác vận hành AI cho đội bán hàng và marketing của doanh nghiệp vừa và nhỏ Việt Nam.

BƯỚC 1. Kiểm tra skill motion graphic đang cài (liệt kê skill khả dụng). Nếu có /motion-director thì dùng nó làm đầu vào chính để lên kịch bản, nhịp và kỹ thuật dựng; dùng thêm các skill motion khác nếu có. Nếu skill yêu cầu công cụ cụ thể (Remotion, After Effects script, Lottie, Motion Canvas...) thì theo skill. Nếu không có ràng buộc, mặc định dùng Remotion (React) và render MP4 H.264.

BƯỚC 2. Đọc 3 file logo trong ./logo/ (PNG 2000x2000, nền trong suốt):
- OPA-mascot-blue.png  (xanh #0068FF) – bản chính
- OPA-mascot-black.png (đen #000000)  – dùng trên nền sáng
- OPA-mascot-white.png (trắng #FFFFFF) – dùng trên nền xanh hoặc nền tối
Dựng lại mascot thành SVG vector (trace từ PNG, ví dụ potrace, rồi làm sạch path) và TÁCH thành các phần để animate riêng:
  (a) sừng trái, (b) sừng phải, (c) khối mõm hình chữ U bo tròn, (d) khe hở giữa đỉnh mõm (2 "lỗ mũi").
So khớp SVG với PNG gốc (chồng lên nhau, sai lệch không quá 2px ở khung 2000px). Không đổi tỉ lệ, không thêm mắt, miệng hay chi tiết mới vào mascot.

BƯỚC 3. Tạo file BRAND-SPEC.md và component dùng chung theo đặc tả dưới đây. Mọi video sau đều import từ đây, không định nghĩa lại màu hay chuyển động.

=== BRAND-SPEC ===
Màu (chỉ dùng các màu này và sắc độ của xanh):
- Xanh OPA #0068FF (chủ đạo) · Đen #0A0A0A (nền tối) · Trắng #FFFFFF
- Sắc độ xanh cho nền phụ: #E6F0FF (rất nhạt), #003C99 (đậm)
- Chữ trên nền xanh: trắng. Chữ trên nền trắng: đen hoặc xanh.
Font: "Be Vietnam Pro" (Google Fonts, hỗ trợ đủ dấu tiếng Việt). Tiêu đề ExtraBold, nội dung Medium. Kiểm tra mọi dấu (ă â ê ô ơ ư đ, dấu hỏi ngã nặng) hiển thị đúng, không bị cắt dấu ở dòng trên.
Khung hình mặc định: 1080x1920 (9:16, TikTok/Reels/Facebook), 30fps. Có biến thể 1080x1080 và 1920x1080 khi được yêu cầu.
Vùng an toàn 9:16: chừa 250px trên, 420px dưới, 120px bên phải (giao diện TikTok/Reels).
Phong cách: phẳng, khối hình học, nhiều khoảng trắng, chuyển cảnh dứt khoát. Không gradient cầu vồng, không hiệu ứng 3D bóng loáng, không ảnh stock người.
Giọng chữ: tiếng Việt, xưng "OPA", gọi khách là "anh chị". Câu ngắn, mỗi khung tối đa 7–9 chữ.

Tính cách mascot "Bò OPA": khỏe, chắc, đáng tin, chủ động lao vào việc. Không hề, không dễ thương kiểu trẻ con.
Thư viện chuyển động mascot (tạo thành component có tham số):
1. reveal: sừng vẽ dần (stroke draw-on) từ gốc lên ngọn 0.6s, mõm chữ U bật lên từ dưới (spring, hơi nảy 1 lần), khối đổ màu xanh.
2. idle: "thở" scale 1.00→1.03→1.00 chu kỳ 2.4s, sừng nghiêng nhẹ ±2°.
3. charge (húc): cúi đầu 8°, lùi 20px, rồi lao tới 60px kèm motion blur ngắn, dừng có rung nhẹ. Dùng khi chuyển sang lời giải.
4. snort (thở phì): 2 cụm hạt nhỏ bay ra từ khe mõm (d), 0.4s. Dùng nhấn mạnh.
5. catch (hứng): khối chữ U làm "cái phễu" hứng các chấm/biểu tượng tin nhắn rơi xuống, không chấm nào rơi ra ngoài. Đây là ẩn dụ chính cho "không bỏ sót khách".
6. badge: mascot thu nhỏ vào góc dưới trái làm watermark (cao 96px, độ mờ 90%), giữ suốt video.
7. outro: mascot xanh giữa khung + chữ "OPA" + dòng "Đối tác vận hành AI cho đội bán hàng" + CTA, 2.5s.
Easing chủ đạo: cubic-bezier(0.2, 0.8, 0.2, 1) cho vào cảnh, spring (damping ~12) cho bật nảy.
Âm thanh: mỗi video để sẵn 1 track nhạc nền trống (placeholder) và SFX gợi ý tại các điểm charge/snort/catch. Không dùng nhạc có bản quyền.
=== HẾT BRAND-SPEC ===

BƯỚC 4. Tạo:
- prices.json với các khóa sau, giá trị để trống, và cờ SHOW_PRICE=false. Khi SHOW_PRICE=false, mọi khung giá được thay bằng dòng "Nhắn OPA để nhận báo giá".
  { "SHOW_PRICE": false, "THU_THACH_7_NGAY": "", "AI_AUDIT": "", "DAO_TAO_DOI_NGU": "", "AI_CRM": "", "AI_SALES_AGENT": "", "AI_SALES_AGENT_THANG": "", "AI_OPS_CARE_THANG": "" }
- links.json: { "WEBSITE": "opa.business", "FANPAGE": "{{link fanpage}}", "DANG_KY_WEBINAR": "{{link đăng ký}}", "BO_7_MAU": "{{link tải}}" }
- Một video thử 6 giây "mascot-sting" dùng reveal → snort → outro để kiểm tra component.

QUY TẮC NỘI DUNG (áp dụng cho mọi video):
- Không đưa con số kết quả (%, số đơn, doanh thu tăng...) nếu không có câu chuyện khách hàng thật đi kèm. Chỉ nói lợi ích dạng định tính: không bỏ sót khách, phản hồi nhanh, có báo cáo, đội tự dùng được AI.
- Không dùng tên, logo, ảnh chụp màn hình hay dữ liệu thật của khách. Giao diện minh họa dùng dữ liệu giả, tên giả rõ ràng.
- Không nhắc khóa kiếm tiền online, trợ lý AI kế toán hay pháp chế.

ĐẦU RA: render ./out/mascot-sting.mp4 và 1 ảnh PNG khung đẹp nhất. Báo lại: skill đã dùng, công cụ dựng, đường dẫn file, và chỗ nào trong SVG chưa khớp PNG gốc.
```

---

## Prompt V1 → V7: từng video

Thứ tự ưu tiên: V2, V3, V6 trước (phục vụ tuyến 70% doanh nghiệp), rồi V4, V5, V7, V1.

| Mã | Video | Gói / giai đoạn | Dài | Kênh chính |
|---|---|---|---|---|
| V1 | Giới thiệu OPA | Thương hiệu | 20s | Fanpage, ghim đầu trang |
| V2 | Không bỏ sót khách | G5 AI CRM + AI Sales Agent | 30s | Facebook Minh, fanpage, kênh Huy |
| V3 | Khám sức khỏe AI | G4 AI Audit | 20s | Fanpage, nhóm Zalo |
| V4 | Đội tự dùng được AI | G4 Đào tạo đội ngũ | 20s | Facebook Minh, fanpage |
| V5 | Ở lại vận hành | G5 AI Ops Care | 15s | Retarget khách cũ, fanpage |
| V6 | Mời webinar doanh nghiệp | Cửa vào G4 | 15s | Mọi kênh, đăng lại hằng tháng |
| V7 | Bắt đầu miễn phí | G0 Bộ 7 mẫu → G1 Thử thách 7 ngày | 15s | Kênh Huy, nhóm Facebook |

### V2: Không bỏ sót khách (AI CRM + AI Sales Agent)

```text
Theo BRAND-SPEC và component mascot đã dựng. Dựng video "v2-khong-bo-sot-khach", 30s, 1080x1920, 30fps. Dùng /motion-director (nếu có) để chỉnh nhịp trước khi render.
Mục tiêu: chủ doanh nghiệp vừa và nhỏ nhận ra đội mình đang bỏ sót khách nhắn tin, và OPA dựng + vận hành hệ thống AI để không sót khách nào.

Cảnh 1 (0–4s) – nền trắng. Nhiều bong bóng tin nhắn (Zalo, Messenger, website: dùng icon chung chung, không dùng logo nền tảng) rơi xuống, vài cái rơi ra khỏi khung và mờ đi. Chữ: "Khách nhắn tối qua…" → "Sáng nay mới thấy."
Cảnh 2 (4–8s) – chữ: "Mỗi tin nhắn sót là một khách đi mất." Bong bóng rơi ra đổi sang xám.
Cảnh 3 (8–12s) – mascot xanh reveal giữa khung rồi charge vào giữa luồng tin nhắn. Snort.
Cảnh 4 (12–20s) – mascot dùng catch: khối chữ U hứng mọi bong bóng. Mỗi bong bóng vào phễu biến thành 1 dòng trong bảng CRM minh họa (tên giả: "Chị Lan – hỏi giá", "Anh Tùng – hẹn demo"...), gắn nhãn trạng thái màu xanh. Chữ lần lượt: "Ghi lại mọi khách" · "Trả lời ngay, cả ngoài giờ" · "Nhắc đội chăm tiếp".
Cảnh 5 (20–25s) – thẻ báo cáo cuối ngày trượt lên (biểu đồ cột đơn giản, KHÔNG ghi số cụ thể, chỉ trục và cột). Chữ: "Cuối ngày có báo cáo. Không đoán mò."
Cảnh 6 (25–30s) – outro. Dòng chính: "AI CRM + AI Sales Agent". Dòng giá: nếu SHOW_PRICE=true hiển thị "Từ {AI_CRM}" và "Sales Agent {AI_SALES_AGENT} + {AI_SALES_AGENT_THANG}/tháng", nếu false hiển thị "Nhắn OPA để nhận báo giá". CTA: "Nhắn fanpage OPA: \"KHÔNG SÓT KHÁCH\"".
Badge mascot ở góc từ cảnh 4 đến hết. Phụ đề cháy chữ (burned-in) cho toàn bộ lời, vì phần lớn người xem tắt tiếng.
Đầu ra: ./out/v2-khong-bo-sot-khach_9x16.mp4, thêm bản 1x1 và 1 ảnh bìa PNG. Báo lại thời lượng thực tế và danh sách chữ trên màn hình để người duyệt soát.
```

### V3: Khám sức khỏe AI cho đội bán hàng (AI Audit)

```text
Theo BRAND-SPEC. Dựng "v3-ai-audit", 20s, 1080x1920.
Ý chính: trước khi đầu tư AI, để OPA soi xem đội bán hàng và marketing đang mất khách ở đâu.
Cảnh 1 (0–4s) – nền xanh #0068FF, chữ trắng: "Đầu tư AI… bắt đầu từ đâu?" Mascot trắng idle, nghiêng đầu (xoay 6°) như đang hỏi.
Cảnh 2 (4–10s) – mascot charge mở ra một "bản đồ quy trình" dạng sơ đồ khối: Quảng cáo → Tin nhắn → Tư vấn → Chốt → Chăm sóc. Một vòng kính lúp lướt qua, 2 khối nhấp nháy đỏ nhạt rồi đổi xanh. Chữ: "Soi từng bước bán hàng" · "Chỉ ra chỗ đang rò khách".
Cảnh 3 (10–15s) – một tài liệu trượt ra, tiêu đề "Kế hoạch AI cho đội của anh chị", 3 gạch đầu dòng mờ. Chữ: "Ra kế hoạch làm gì trước, làm gì sau."
Cảnh 4 (15–20s) – outro. "AI Audit cho doanh nghiệp". Giá: {AI_AUDIT} nếu SHOW_PRICE=true, ngược lại "Nhắn OPA để nhận báo giá". CTA: "Đăng ký webinar để được tư vấn trước".
Đầu ra: 9x16 + 1x1 + ảnh bìa.
```

### V4: Đội của anh chị tự dùng được AI (Đào tạo đội ngũ)

```text
Theo BRAND-SPEC. Dựng "v4-dao-tao-doi-ngu", 20s, 1080x1920.
Ý chính: OPA không làm thay mãi, OPA đào tạo để đội của khách tự dùng được AI trong việc hằng ngày.
Cảnh 1 (0–4s) – 4 biểu tượng người (khối hình học tối giản, không mặt) đứng cạnh một ô "AI" xám đang khóa. Chữ: "Mua AI rồi… đội không ai dùng?"
Cảnh 2 (4–12s) – mascot xanh reveal, snort, rồi đi qua từng người; mỗi người được "gắn" một biểu tượng công cụ phát sáng xanh (soạn tin, lên nội dung, tổng hợp báo cáo). Chữ: "Học trên việc thật của đội" · "Mỗi người một quy trình dùng được ngay".
Cảnh 3 (12–16s) – 4 người làm việc song song, các dòng việc chạy nhanh. Mascot thu về góc (badge). Chữ: "AI soạn. Người duyệt."
Cảnh 4 (16–20s) – outro. "Đào tạo đội ngũ dùng AI". Giá {DAO_TAO_DOI_NGU} hoặc "Nhắn OPA để nhận báo giá". CTA: "Nhắn fanpage OPA: \"ĐÀO TẠO ĐỘI\"".
Đầu ra: 9x16 + 1x1 + ảnh bìa.
```

### V5: OPA ở lại vận hành hằng tháng (AI Ops Care)

```text
Theo BRAND-SPEC. Dựng "v5-ai-ops-care", 15s, 1080x1920.
Ý chính: hệ thống AI cần người trông. OPA ở lại theo dõi, sửa, cập nhật hằng tháng.
Cảnh 1 (0–4s) – một hệ thống dạng bánh răng/khối đang chạy rồi khựng lại, một khối chuyển xám. Chữ: "Hệ thống AI chạy được 1 tháng rồi… đứng?"
Cảnh 2 (4–10s) – mascot charge vào, khối xám bật lại xanh; lịch tháng hiện ra với dấu tick đều đặn mỗi tuần. Chữ: "Theo dõi hằng tuần" · "Sửa và cập nhật kịp thời" · "Báo cáo mỗi tháng".
Cảnh 3 (10–15s) – outro. "AI Ops Care". Giá "{AI_OPS_CARE_THANG}/tháng" hoặc "Nhắn OPA để nhận báo giá". Dòng phụ: "Tài khoản đứng tên anh chị. Bảo mật 2 lớp."
Đầu ra: 9x16 + 1x1.
```

### V6: Mời webinar doanh nghiệp hằng tháng

```text
Theo BRAND-SPEC. Dựng "v6-moi-webinar", 15s, 1080x1920, dạng template tái dùng mỗi tháng.
Tham số đầu vào (đặt trong webinar.json): TIEU_DE, NGAY, GIO, HINH_THUC (online/offline), LINK_DANG_KY.
Cảnh 1 (0–3s) – nền đen #0A0A0A, mascot xanh reveal. Chữ trắng: "Webinar cho chủ doanh nghiệp".
Cảnh 2 (3–10s) – TIEU_DE hiện từng cụm chữ, nhịp mạnh. Thẻ lịch lật ra NGAY · GIO · HINH_THUC. Mascot snort khi thẻ lịch dừng.
Cảnh 3 (10–15s) – "Miễn phí. Số chỗ có hạn." CTA LINK_DANG_KY lớn, mascot badge.
Tạo thêm bản 1920x1080 cho bài sự kiện Facebook và 1 ảnh bìa 1200x628.
Mẫu tiêu đề tháng này (người duyệt sửa): "Đưa AI vào đội bán hàng: bắt đầu từ đâu?"
```

### V7: Bắt đầu miễn phí (Bộ 7 mẫu → Thử thách 7 ngày)

```text
Theo BRAND-SPEC. Dựng "v7-bat-dau-mien-phi", 15s, 1080x1920, nhịp nhanh hợp TikTok/Reels kênh Huy.
Ý chính: người mới tò mò về AI có lối vào miễn phí, rồi thử làm thật trong 7 ngày.
Cảnh 1 (0–3s) – hook chữ lớn: "Muốn dùng AI mà không biết bắt đầu?" Mascot bật ra từ dưới khung.
Cảnh 2 (3–8s) – 7 thẻ mẫu xếp quạt trượt ra từ khối chữ U của mascot. Chữ: "Bộ 7 mẫu + bài 15 phút" · "Miễn phí".
Cảnh 3 (8–12s) – thanh tiến độ 7 ô, từng ô sáng xanh, mascot charge tới ô thứ 7. Chữ: "Thử thách 7 ngày" · giá {THU_THACH_7_NGAY} nếu SHOW_PRICE=true · "Làm đủ 7/7 được trừ vào Bootcamp".
Cảnh 4 (12–15s) – CTA: "Bình luận \"7 MẪU\" để nhận bộ mẫu". Mascot badge.
Đầu ra: 9x16 + ảnh bìa.
```

### V1: Giới thiệu OPA (video thương hiệu)

```text
Theo BRAND-SPEC. Dựng "v1-gioi-thieu-opa", 20s, 1080x1920 và 1920x1080.
Cảnh 1 (0–5s) – nền trắng, mascot xanh reveal đầy đủ, snort. Chữ: "OPA – OverPowers Agency".
Cảnh 2 (5–14s) – 4 lợi ích lần lượt, mỗi cái 2s, mascot làm 1 động tác tương ứng: "Không bỏ sót khách" (catch) · "Phản hồi nhanh" (charge) · "Có báo cáo rõ ràng" (thẻ báo cáo bật lên) · "Đội tự dùng được AI" (idle cạnh 4 biểu tượng người).
Cảnh 3 (14–20s) – "Đối tác vận hành AI cho đội bán hàng và marketing." → outro chuẩn với website opa.business.
Đầu ra: 2 tỉ lệ + ảnh bìa.
```

---

## Prompt soát lỗi trước khi giao (dán sau mỗi video)

```text
Soát video vừa render theo BRAND-SPEC, trả về bảng Đạt/Chưa đạt:
1. Màu chỉ gồm #0068FF, #0A0A0A, #FFFFFF và sắc độ xanh trong spec.
2. Mascot đúng hình gốc, không méo, không thêm chi tiết; bản trắng chỉ đặt trên nền xanh hoặc tối.
3. Dấu tiếng Việt hiển thị đủ, không bị cắt, không lỗi chính tả.
4. Chữ nằm trong vùng an toàn 9:16.
5. Không có con số kết quả khách hàng; giá chỉ hiện khi SHOW_PRICE=true.
6. Không có tên, logo, dữ liệu khách thật.
7. Mỗi khung chữ đứng đủ lâu để đọc (ít nhất 1.2s cho 7 chữ).
Xuất 6 ảnh chụp khung tại các mốc chuyển cảnh vào ./out/review/ để người duyệt xem nhanh.
```

---

## Việc tiếp theo

| Việc | Người phụ trách | Hạn |
|---|---|---|
| Chạy Prompt 0, duyệt mascot SVG và sting 6s | Hùng | T6 09/10 |
| Duyệt lời V2, V3, V6 | Minh | T6 09/10 |
| Render V2, V3, V6 bản không giá | Hùng | T6 16/10 |
| Điền prices.json sau khi chốt giá, render lại | Hùng | T6 16/10 |
