# Blueprint Học Style Dựng Video Từ Video Mẫu — Thơ EDITOR (`@lopphovlog/video/7706795032463936769`)

Tài liệu này hệ thống hoá toàn bộ phương pháp **train skill edit video từ con số 0** trong video của **Thơ EDITOR** (`@lopphovlog/video/7706795032463936769`), kết hợp đo đạc kỹ thuật tự động (`ffprobe`, `scdet`, `ebur128`, contact sheet) và vòng lặp phản hồi trực quan để đóng gói thành skill **1-Prompt Production** có thể chạy trên mọi máy.

> *"AI không thay bạn hiểu cái đẹp, nó chỉ học nhanh hơn khi bạn biết mình muốn gì."*

---

## 1. Chiến lược chọn video mẫu (Phase 1)

| Số lượng video mẫu | Khi nào dùng | Nguyên tắc |
|---|---|---|
| **2–3 video cùng style** | Muốn học một *phong cách tổng quát* (nhịp chung, cấu trúc chung) | AI tách được đâu là **pattern cốt lõi lặp lại** và đâu chỉ là chi tiết ngẫu nhiên của từng clip. |
| **Đúng 1 video mẫu** | Muốn **nhân bản chính xác 100%** đúng một style cụ thể | Tránh bị "pha trộn" (blend) giữa 3 editor khác nhau làm loãng chất riêng. |

---

## 2. Phân tích 9 trục kỹ thuật + Đo máy + Nhìn khung hình (Phase 2)

Với Talking Head, motion và typography **không phải phần trang trí, mà là toàn bộ linh hồn của video** — bỏ đi thì chỉ còn một người ngồi nói và người xem lướt qua trong 2 giây.

### 9 trục kỹ thuật bắt buộc bóc tách

1. **Nhịp dựng (Pacing & Cuts):**
   - Đo bằng `scdet`: số điểm cắt trên mỗi 10 giây (`cuts/10s`), độ dài shot trung vị (`median_shot_sec`), khoảng tối đa không có biến đổi thị giác (`max_static_sec` ≤ 2.5s).
2. **Typography (Hệ thống chữ):**
   - Font family, độ dày (`font_weight`), giãn chữ (`tracking_em`), line-height, độ tương phản (stroke/shadow).
   - Chế độ **word-by-word** (chữ nhảy theo từng nhịp nói) và **highlight màu riêng cho từ khoá**.
   - Khả năng đọc khi **tắt tiếng trên điện thoại** (`mobile_mute_readable: true`).
3. **Animation Text (Chuyển động chữ):**
   - Bắt buộc dùng đường cong **`ease-in-out`** (`cubic-bezier(0.42, 0, 0.58, 1)`), **cấm `linear`** (chạy đều nhìn như máy).
   - Tốc độ chữ (`text_speed_scale`, mặc định ~`1.2` để chậm hơn một nhịp cho mắt đọc kịp trên màn hình dọc).
4. **Fake Camera (Chuyển động máy ảo):**
   - Zoom in / zoom out mượt ngay trên khung hình thô (đặc biệt trong **10 giây đầu**), dùng đồ thị `ease-in-out`.
5. **Motion Graphics & UI Elements:**
   - Cứ vài giây có một yếu tố thị giác mới: `icon_badge`, `glass_card`, `orbit_nodes`, `stat_pill`, `callout_arrow`.
   - **Quy tắc Face-Safe Zone:** Tuyệt đối không đặt element hay chữ đè lên khuôn mặt người nói.
6. **Transition (Chuyển cảnh):**
   - Flash cam, smooth wipe, punch zoom theo nhịp cắt hoặc ý chính.
7. **Bố cục & Vùng an toàn (Layout & Face-Safe Zone):**
   - Khung 9:16 (1080×1920), vùng mặt ở khoảng `x: [0.22, 0.78]`, `y: [0.16, 0.56]`, padding tối thiểu `36px`.
   - Phụ đề nằm tách bạch ở vùng dưới (`y: [0.64, 0.84]`), card UI đặt góc trên hoặc lower-third phía trên phụ đề.
8. **Audio & SFX (Âm thanh):**
   - Giọng nói rõ nét (`-5` đến `-3 dBFS`), nhạc nền thấp hơn giọng (`-17` đến `-22 LU`), SFX nhấn đúng nhịp chuyển UI / pop chữ (`-12` đến `-8 dBFS`).
9. **Engine & Portability (Nền tảng & Tính di động):**
   - Chạy trên HyperFrames / Remotion / FilmCraft; tài nguyên (font, SFX, template) đóng gói tương đối trong `assets/` và `templates/`, không hardcode đường dẫn cá nhân.

### Prompt mẫu gửi AI ở Phase 2 (khi đã có số đo + Contact Sheet)

```text
Hãy phân tích video mẫu đính kèm (cùng file probe_report.json và ảnh contact sheet) theo 9 trục kỹ thuật:
1. Nhịp dựng (cuts/10s, median shot duration, nhịp chèn UI).
2. Typography (font, weight, tracking, word-by-word highlight màu cho từ khoá, kích thước đọc được khi tắt tiếng trên điện thoại).
3. Animation Text (tốc độ xuất hiện, đường cong easing — bắt buộc ease-in-out, không linear).
4. Fake Camera (zoom in/out, pan mượt trong 10 giây đầu).
5. Motion Graphics & UI Elements (icon, glass card, orbit nodes, vị trí xuất hiện).
6. Face-Safe Zone (vùng khuôn mặt người nói tuyệt đối không bị UI/chữ đè lên).
7. Transition (flash cam, wipe, punch zoom).
8. Audio & SFX (tỉ lệ giọng / BGM LUFS, vị trí SFX theo nhịp UI).
9. Đóng gói kết quả thành skill dựng video trên [HyperFrames/Remotion/FilmCraft] dùng đường dẫn tương đối 100% portable.
```

---

## 3. Bảy nguyên lý viral của Talking Head (Kim chỉ nam mọi skill)

| # | Nguyên lý | Cơ chế tâm lý & Hành vi | Hệ quả kỹ thuật cho Skill Edit |
|---|---|---|---|
| **1** | **Khuôn mặt người** | Não người lập trình để chú ý khuôn mặt trước mọi thứ khác; thấy người nhìn thẳng nói chuyện, ngón tay tự khựng lại 1 nhịp. | Bảo vệ tuyệt đối `face_safe_zone`; không che mặt bằng text/UI. |
| **2** | **Tin con người hơn thương hiệu (Parasocial)** | Xem một người nói chuyện mỗi ngày tạo cảm giác quen thân một chiều → tin tưởng và xem đến hết video. | Giữ sự hiện diện tự nhiên của người nói; UI chỉ đóng vai trò trợ giảng trực quan. |
| **3** | **Phần dựng làm video cuốn (Alex Hormozi style)** | Người xem ở lại vì điều họ nghe, nhưng **không bỏ đi nhờ điều họ nhìn thấy**: chữ nhảy từng từ, đổi màu từ khoá, vài giây có zoom/cut/UI mới. | Nhịp biến đổi thị giác mỗi `2.5–4.0s`; `word_by_word` + `keyword_highlight`. |
| **4** | **Sinh ra cho điện thoại — Chữ = Âm thanh** | Khung dọc 9:16, xem bằng một tay, rất nhiều người lướt khi **đã tắt tiếng** (trên xe buýt, văn phòng, cạnh người đang ngủ). | Chữ nhỏ hoặc đặt sai chỗ = video coi như **câm**. Typography phải to, rõ, tương phản cao. |
| **5** | **Rẻ và dễ lặp lại** | Không cần bối cảnh/diễn viên; chỉ cần điện thoại + mic + ý tưởng; quay 1 buổi ra chục video để đăng đều cho thuật toán. | Skill phải đóng gói **1-Prompt Production**, chạy hàng loạt không cần chỉnh tay từng clip. |
| **6** | **Phễu bán hàng không giống đang bán hàng** | Người xem đến vì mẹo hay, ở lại vì tin người nói, rồi mua sản phẩm/khoá học tự nhiên. | Hỗ trợ highlight giá trị / con số / từ khoá nỗi đau bằng `stat_pill` hoặc `glass_card`. |
| **7** | **Giá trị thật nằm ở ý tưởng** | Chữ đẹp, hiệu ứng mượt giữ người xem thêm vài giây; thứ khiến họ lưu, chia sẻ, follow vẫn là **một câu nói đáng nghe**. | Dựng giỏi không cứu được nội dung rỗng; skill edit phải phục vụ làm nổi bật ý tưởng cốt lõi, không rối mắt. |

---

## 4. Quy trình thử mù & Vòng lặp 4 Round Feedback (Phase 3 → Phase 4)

### Round 1 — Baseline Test mù (Zero-Guidance)
- **Cách làm:** Lấy một đoạn talking head thô, chỉ gửi **1 câu lệnh thật ngắn** (VD: *"Dựng đoạn talking head này theo skill"*), **cố tình KHÔNG hướng dẫn thêm**.
- **Mục đích:** Đo giới hạn tự động thực sự của skill ở trạng thái mặc định; chuẩn bị tâm lý bản đầu tiên thường chưa đạt.

### Round 2 — Motion Speed & Ép `ease-in-out`
- **Vấn đề thường gặp sau Round 1:** Chữ chạy quá nhanh (khó đọc trên điện thoại), chuyển động dùng `linear` nhìn cứng như máy.
- **Hành động:**
  - Chỉnh motion chậm lại rõ ràng (`motion.text_speed_scale=1.2`).
  - Ép `motion.easing=ease-in-out` (`cubic-bezier(0.42, 0, 0.58, 1)`) cho **toàn bộ** keyframe chữ, UI và camera (tăng tốc nhẹ rồi hãm lại cho mượt).
  - Ghi vĩnh viễn vào `config.json` qua `style_trainer.py feedback`.

### Round 3 — Visual Screenshot Feedback & Face-Safe Zone
- **Mẹo vàng từ video:** *"Lỗi nào liên quan tới vị trí, cứ chụp ảnh màn hình đúng khung hình đó gửi kèm. AI nhìn ảnh hiểu đúng ý bạn nhanh hơn nhiều so với ngồi tả bằng chữ."*
- **Vấn đề thường gặp:** Typography hơi nhỏ khi xem điện thoại tắt tiếng; UI element / card đè thẳng lên mặt người nói.
- **Hành động:**
  - Chụp screenshot khung hình lỗi, đính kèm `--screenshot` khi chạy `feedback`.
  - Tăng cỡ chữ (`typography.scale=1.15`), cân lại bố cục tránh `face_safe_zone`.

### Round 4 — Tối ưu 10 giây đầu (`Fake Camera`) & Kiểm tra Portability
- **Tầm quan trọng:** 10 giây đầu quyết định người xem ở lại hay lướt đi. Nếu mở đầu chậm hoặc đứng yên, video mất retention ngay lập tức.
- **Hành động:**
  - Thêm `fake camera in/out` (zoom vào, zoom ra ngay trên khung hình) trong `hook_window_sec: 10` với đồ thị `ease-in-out`.
  - Chạy `lint-skill` kiểm tra **Portability**: đảm bảo không có đường dẫn cứng cá nhân (`C:\`, `D:\`, `/home/...`), mọi font/SFX/template đi kèm tương đối để gửi sang máy bất kỳ là chạy ngay.

---

## 5. Đóng gói 1-Prompt Production (Phase 5)

Sau khi qua đủ 4 Round và `lint-skill` đạt `PASS`:
- Mọi bản cập nhật đã nằm vĩnh viễn trong `config.json`, `SKILL.md` và `templates/`.
- Với mọi video talking head thô mới, người dùng chỉ cần **1 câu lệnh ngắn kèm file video** — không cần nhắc lại `ease-in-out`, cỡ chữ hay vùng mặt nữa.
