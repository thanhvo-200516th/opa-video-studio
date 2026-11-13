# kb-personal-brand-video-engine — toàn văn tài liệu của nguồn `personal-brand-video-engine`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/personal-brand-video-engine/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: personal-brand-video-engine/SKILL.md ===== -->

---
name: personal-brand-video-engine
description: >-
  Hệ thống chiến lược và vận hành thương hiệu cá nhân 90 ngày qua video ngắn ("Dựng Có Chủ Đích"): Hồ sơ giọng văn & từ vựng đặc trưng (Voice Profile), Ma trận 4 trụ cột nội dung (P1–P4), Cấu trúc kịch bản 4 nhịp 35–45 giây (Hook 0–3s, Proof 3–10s, Body 10–32s, Close/CTA 32–42s), Quy trình SOP sản xuất cuốn chiếu 4 video/tuần trong 7h30p, Kho 60 kịch bản mẫu theo 4 Sprint và Hệ thống tự động đăng bài đa kênh chạy ngầm (DBTD). Kích hoạt khi người dùng muốn xây dựng chiến lược thương hiệu cá nhân bằng video ngắn, viết kịch bản TikTok/Reels/Shorts theo chuẩn 4 nhịp giữ chân người xem, lập lịch sản xuất hàng tuần, hoặc thiết lập bot tự động đăng bài.
---

# Personal Brand Video Engine — Hệ Thống Xây Dựng Thương Hiệu Cá Nhân 90 Ngày & Tự Động Hóa Đăng Kênh

Skill này đóng gói toàn bộ chiến lược định vị **"Dựng Có Chủ Đích"**, quy chuẩn giọng văn thực chiến, kho **60 kịch bản chia theo 4 Sprint (90 ngày)**, quy trình sản xuất cuốn chiếu hàng tuần (SOP) và công cụ **tự động đăng bài chạy ngầm (`DBTD`)**.

---

## Chạy trên máy Linux này

- Đường dẫn Windows trong tài liệu đã đổi sang Linux: `F:\` → `/media/vmiz/Over Powers/`, `D:\` → `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/` (bản sao lưu ổ D ngày 2026-10-28). Ổ USB `Over Powers` phải đang gắn. `E:\` không có trên máy; tài nguyên thay thế ở `/home/vmiz/Thanh/Media/TNEDIT/` (`02_SFX`, `08_Nhac_Nen`, `01_Font`, `06_B-Roll`…).
- Bot DBTD (`scripts/dbtd/`): file `.bat`, `.vbs` và lịch `schtasks` chỉ chạy trên Windows. Trên Linux: `npm install` → `node bot_autopost.mjs --login` (lần đầu) → `node bot_autopost.mjs --run`, lên lịch 15 phút bằng cron hoặc lịch của Cindy. Bot đăng bài công khai: chỉ bật lịch khi người dùng yêu cầu.

---

## 1. Cấu Trúc Thư Mục Trong Skill

- **`references/00_CHIEN_LUOC/`** — Nền tảng chiến lược và quy trình vận hành:
  - `NGAY_01_DINH_VI.md` & `NGAY_02_HO_SO_KENH_VA_3_VIDEO_GHIM.md`: Định vị ngách chuyên gia, tối ưu hồ sơ kênh (Bio, Avatar, Banner) và cấu trúc **3 Video Ghim đầu kênh** (Video 1: Tuyên ngôn & Kết quả thực tế; Video 2: Phá bỏ lầm tưởng lớn nhất ngành; Video 3: Case Study / Quy trình chuyển đổi).
  - `VOICE_PROFILE_VA_QUY_CHUAN_CONTENT.md`: Hồ sơ giọng nói, từ vựng nên dùng / cấm dùng, ma trận 4 trụ cột nội dung và công thức kịch bản 4 nhịp.
  - `SOP_SAN_XUAT_VIDEO_HANG_TUAN.md`: Lịch trình 7 ngày sản xuất cuốn chiếu (Batch Production) 4 video/tuần chỉ tốn tổng cộng **7 giờ 30 phút**.
- **`references/01_Y_TUONG_VA_SCRIPT/`** — Kho 60 kịch bản hoàn chỉnh chia theo 4 giai đoạn tăng trưởng:
  - `00_MASTER_INDEX_60_VIDEO.md`: Bảng danh mục tổng thể 60 video.
  - `01_SPRINT_1_TUAN_01_03_THU_NGHIEM.md`: Tuần 1–3 (Phá băng, tìm góc tiếp cận thắng lợi).
  - `02_SPRINT_2_TUAN_04_06_XAY_BANG_CHUNG.md`: Tuần 4–6 (Show hậu trường, bóc tách quy trình, chứng minh năng lực).
  - `03_SPRINT_3_TUAN_07_09_TOI_UU_HE_THONG.md`: Tuần 7–9 (Đóng gói công thức, tặng tài nguyên miễn phí thu phễu).
  - `04_SPRINT_4_TUAN_10_12_CHUYEN_DOI.md` & `05_12_VIDEO_DU_PHONG_BAO_CAO_VA_CHUYEN_DOI_SAU.md`: Tuần 10–12 (Chuyển đổi khách hàng chất lượng cao).
  - `06_SHOT_LIST_QUAY_BATCH_TUAN_1.md`: Bảng phân cảnh quay gộp một buổi cho cả tuần.
- **`references/05_ASSET/` & `references/06_KPI_VA_CASE_STUDY/`** — Bộ tài liệu quà tặng thu phễu (`STARTER_KIT_V1_DUNG_CO_CHU_DICH.md`) và khung đo lường KPI / Case Study (`KHUNG_3_CASE_STUDY_VA_BAO_CAO_SPRINT.md`).
- **`references/HUONG_DAN_SU_DUNG_VA_CHAY_NGAM.md` & `scripts/dbtd/`** — Hệ thống bot tự động đăng bài đa nền tảng chạy ngầm trên Windows (`danh_sach_60_bai_autopost.json`, các script điều khiển trình duyệt và tác vụ chạy ẩn `.vbs` / `.bat`).

---

## 2. Hồ Sơ Giọng Văn (Voice Profile) & Ma Trận 4 Trụ Cột Nội Dung

### Đặc trưng giọng văn ("Dựng Có Chủ Đích"):
- **Trực diện, thực chiến, có con số đo lường:** Nói thẳng vào vấn đề ngay giây đầu tiên; luôn đi kèm bằng chứng màn hình dự án thật, timeline thật hoặc chỉ số trước/sau.
- **Từ vựng cấm dùng:** Không mở đầu bằng *"Xin chào các bạn, hôm nay mình sẽ..."*, không dùng các mỹ từ sáo rỗng (*"siêu đỉnh", "bí kíp thần thánh", "kiếm tiền dễ dàng"*).
- **Cấu trúc câu:** Câu ngắn (`8 – 16 từ`), giàu động từ hành động, đối lập rõ giữa **Cách làm bản năng (tốn sức, không ra chuyển đổi)** và **Cách làm có hệ thống (đúng mục tiêu kinh doanh)**.

### Ma trận 4 Trụ cột nội dung hàng tuần (4 Video / Tuần):
1. **P1 — Phá bỏ lầm tưởng & Góc nhìn ngược (30%):** Chỉ ra lỗi sai phổ biến khiến video nhiều hiệu ứng nhưng không giữ được người xem hoặc không ra đơn.
2. **P2 — Giải phẫu hậu trường & Kỹ thuật thực chiến (35%):** Mở trực tiếp timeline Premiere / After Effects / Quy trình AI để bóc tách tại sao cảnh đó lại hiệu quả.
3. **P3 — Hệ thống hóa & Công cụ tăng tốc (20%):** Chia sẻ quy trình tự động hóa, preset, template, cách kết hợp AI để rút ngắn 70% thời gian sản xuất.
4. **P4 — Bằng chứng thực tế & Case Study chuyển đổi (15%):** Phân tích kết quả thực tế từ dự án khách hàng và kêu gọi nhận bộ tài nguyên / tư vấn.

---

## 3. Cấu Trúc Kịch Bản Video Ngắn 4 Nhịp (`35 – 45 Giây`)

Mọi kịch bản trong hệ thống đều tuân thủ chặt chẽ cấu trúc 4 nhịp tính theo giây:
- **Nhịp 1 — HOOK (`00s – 03s`):** Câu mở đầu đánh thẳng vào nỗi đau hoặc sự tò mò lớn nhất + **Visual Hook** (màn hình kết quả, so sánh Trước/Sau hoặc hành động thị giác mạnh ngay khung hình đầu tiên).
- **Nhịp 2 — PROOF / CONTEXT (`03s – 10s`):** Đưa ra bằng chứng ngay lập tức để xác lập uy tín (*"Đây là timeline dự án 13 cảnh mình vừa xử lý..."*) trước khi giải thích chi tiết.
- **Nhịp 3 — BODY 3 ĐIỂM (`10s – 32s`):** Trình bày tối đa 3 bước hoặc 3 nguyên tắc cốt lõi, mỗi ý dài `6–7 giây`, luôn có B-Roll minh họa hoặc quay màn hình thao tác thật.
- **Nhịp 4 — CLOSE & CTA (`32s – 42s`):** Đúc kết bằng 1 câu ngắn gọn và kêu gọi 1 hành động cụ thể duy nhất (*"Bình luận từ khóa [X] để nhận bộ khung dự án / Starter Kit"*).

---

## 4. Quy Trình SOP Sản Xuất Cuốn Chiếu 1 Tuần Trong 7 Giờ 30 Phút

| Ngày | Công việc trọng tâm | Thời lượng |
|---|---|---|
| **Thứ Hai** | Chọn 4 chủ đề từ kho 60 bài + Hoàn thiện 4 kịch bản & danh sách cảnh quay (Shot list) | `90 phút` |
| **Thứ Ba** | Quay gộp (Batch Recording) cả 4 video A-Roll + Thu âm + Quay màn hình dự án | `120 phút` |
| **Thứ Tư** | Dựng thô (Rough Cut), cắt jump-cut, ghép B-Roll cho Video 1 & Video 2 | `90 phút` |
| **Thứ Năm** | Dựng thô Video 3 & Video 4 + Gắn phụ đề động, Icon và SFX cho cả 4 video | `90 phút` |
| **Thứ Sáu** | Kiểm duyệt chất lượng (QA), xuất file MP4 + Nạp vào hệ thống tự động đăng (`scripts/dbtd/`) | `60 phút` |
| **Cuối tuần** | Hệ thống tự động đăng bài theo lịch vàng & Phản hồi bình luận thu phễu khách hàng | *Chạy ngầm* |

<!-- ===== /file: personal-brand-video-engine/SKILL.md ===== -->

<!-- ===== file: personal-brand-video-engine/references/00_CHIEN_LUOC/NGAY_01_DINH_VI.md ===== -->

# Ngày 01 — Định vị thương hiệu cá nhân

Ngày thực hiện: 21/10/2026

## Kết quả được chọn cho 90 ngày thử nghiệm

**Định vị cốt lõi**  
Thành giúp creator và thương hiệu cá nhân biến ý tưởng thành video có chủ đích bằng tư duy marketing, kỹ năng dựng và AI.

**Signature**  
Dựng Có Chủ Đích.

**Mô tả vai trò**  
Video Editor | Marketing Mindset | AI Workflow

**Giới thiệu 15 giây**  
Mình là Thành, video editor có nền tảng marketing. Mình chia sẻ cách dựng video rõ thông điệp và ứng dụng AI đúng chỗ, để mỗi video không chỉ đẹp mà còn có mục tiêu.

## Ba phiên bản bio thử nghiệm

1. **Bio tổng quát:** Video Editor | Marketing Mindset | AI Workflow. Chia sẻ cách dựng video có chủ đích bằng marketing và AI.
2. **Bio hướng khách hàng:** Giúp creator biến ý tưởng thành video rõ thông điệp. Edit • Marketing • AI workflow.
3. **Bio hành trình:** Học và làm Premiere, After Effects, AI. Mỗi tuần một thử nghiệm dựng có chủ đích.

## Ba phương án đã cân nhắc

1. **Kết quả cho khách hàng:** Thành giúp creator và thương hiệu cá nhân biến ý tưởng thành video có chủ đích bằng tư duy marketing, kỹ năng dựng và AI.
2. **Vai trò chuyên môn:** Editor có nền tảng marketing, chia sẻ cách làm video rõ thông điệp, gọn quy trình và có khả năng chuyển đổi.
3. **Hành trình học công khai:** Từ brief đến video: Thành thử nghiệm Premiere, After Effects và AI để dựng nhanh hơn mà không đánh mất tư duy marketing.

Phương án 1 được chọn vì bắt đầu từ giá trị cho người xem, kết nối đủ Marketing — Editing — AI và không phóng đại thâm niên.

## Tệp khán giả ưu tiên

- **Tệp chính:** Creator và người xây thương hiệu cá nhân mới bắt đầu, đã có ý tưởng nhưng chưa biết biến thành video ngắn rõ thông điệp và duy trì đều.
- **Tệp phụ:** Chủ doanh nghiệp nhỏ hoặc đội marketing cần quy trình video ngắn gọn hơn, có thể thuê dựng hoặc ứng dụng AI vào khâu nội dung và hậu kỳ.
- **Vấn đề chung:** Video có thể đẹp nhưng thiếu mục tiêu, quy trình tốn thời gian và chưa biết dùng AI đúng chỗ.
- **Ba hướng doanh thu hiện hữu:** Dịch vụ edit/media; hoa hồng/affiliate Zero To AI; affiliate Xưởng Media. Sản phẩm tri thức cá nhân chỉ triển khai sau khi có dữ liệu và case thực tế.

## Ba mục tiêu đo được trong 90 ngày

1. **Nội dung:** Xuất bản tối thiểu 36 video ngắn trong 12 tuần, tương ứng 3 video bắt buộc mỗi tuần; mục tiêu mở rộng là 48 video bằng video linh hoạt. Tối thiểu 85% video bắt buộc phải đúng lịch.
2. **Bằng chứng năng lực:** Hoàn thành 3 case study, 1 Starter Kit và 4 báo cáo sprint. Sau mỗi sprint giữ tối đa 2 series để thử tiếp; cuối 90 ngày chọn 3 format cốt lõi dựa trên watch time, save/share, profile visit, lead và phản hồi thật.
3. **Cơ hội kinh doanh:** Tạo tối thiểu 12 cuộc trao đổi đủ điều kiện, nhận ít nhất 3 brief dịch vụ và có tối thiểu 30 lượt click được theo dõi tới Zero To AI hoặc Xưởng Media.

**Định nghĩa đo lường**

- Cuộc trao đổi đủ điều kiện: đúng tệp và có nhu cầu, kèm mốc thời gian hoặc ngân sách dự kiến.
- Brief hợp lệ: có mục tiêu, đầu vào, đầu ra, deadline và phạm vi mong đợi.
- Click hợp lệ: đo bằng UTM hoặc công cụ theo dõi link, loại lượt test nội bộ.
- Case khách hàng: chỉ công bố khi có quyền sử dụng và kết quả được xác thực; nếu chưa có, ghi rõ là case kỹ thuật hoặc case quy trình.

## Nguyên tắc giọng tạm thời

Đây là nguyên tắc thử nghiệm, chưa phải hồ sơ giọng nói cố định. Chỉ khóa voice profile sau khi có 5–20 video thật.

- Nói trực tiếp, cụ thể, dùng ví dụ hoặc hình ảnh chứng minh.
- Xưng “mình”, gọi người xem theo đúng ngữ cảnh; tránh giọng chuyên gia toàn năng.
- Một video chỉ có một thông điệp, một tệp người xem và một CTA.
- Ưu tiên before/after, timeline, input/output và quyết định dựng thật.
- Không hứa AI thay thế editor; luôn chỉ rõ phần AI làm thô và phần con người chỉnh tinh.
- Tránh các cụm sáo như “bí quyết bùng nổ”, “thay đổi cuộc đời”, “AI làm tất cả”.

## Tiêu chí hoàn thành Ngày 01

- [x] Có một câu định vị nêu rõ tệp, vấn đề và giá trị.
- [x] Có signature và mô tả vai trò nhất quán.
- [x] Có bài giới thiệu nói được trong khoảng 15 giây.
- [x] Có ba phiên bản bio để đồng bộ và thử nghiệm.
- [x] Có ba mục tiêu 90 ngày đo được.
- [x] Có cấu trúc thư mục dự án để bắt đầu sản xuất.

## Ruling

Chọn định vị theo kết quả cho khách hàng thay vì tự gọi mình là chuyên gia. Chi phí nếu định vị chưa khớp là phải điều chỉnh sau Sprint 1; đổi lại, nó trung thực với kinh nghiệm hiện tại và vẫn mở đường cho dịch vụ, khóa học và affiliate.

<!-- ===== /file: personal-brand-video-engine/references/00_CHIEN_LUOC/NGAY_01_DINH_VI.md ===== -->

<!-- ===== file: personal-brand-video-engine/references/00_CHIEN_LUOC/NGAY_02_HO_SO_KENH_VA_3_VIDEO_GHIM.md ===== -->

# Ngày 02 — Đồng Bộ Hồ Sơ Kênh & Kịch Bản 3 Video Ghim

> **Mục tiêu:** Thiết lập mặt tiền đồng nhất trên **TikTok** (kênh thử nghiệm hook & khám phá) và **Facebook** (kênh xây dựng niềm tin, quan hệ & chuyển đổi), kèm kịch bản sản xuất **3 Video Ghim** giúp khách hàng và người xem mới hiểu ngay Thành là ai, làm được gì và bắt đầu từ đâu.

---

## 1. BỘ HỒ SƠ ĐỒNG NHẤT (PROFILE & BIO)

### A. Tên & Nhận diện cơ bản
- **Tên hiển thị (Display Name):** `Thành — Dựng Có Chủ Đích`
- **Username gợi ý (TikTok / FB URL):** `@thanh.dungcochudich` hoặc `@thanhmediamkt`
- **Ảnh đại diện (Avatar):** Ảnh chụp nửa người rõ mặt, ánh sáng sạch, phông nền gọn (góc bàn làm việc có màn hình timeline mờ phía sau), trang phục đơn sắc tối giản.
- **Màu sắc & Phụ đề nhận diện (30 ngày đầu):**
  - Không mất thời gian thiết kế logo phức tạp.
  - Phụ đề chính: Font không chân rõ nét (SF Pro Display / Inter / Montserrat Semibold), chữ trắng kem `#F6F1E8` viền/đổ bóng tối nhẹ, từ khóa nhấn màu xanh dương `#1A73E8` hoặc vàng ấm `#FFD166`.
  - Luôn đặt phụ đề trong vùng an toàn (Safe Zone 9:16: cách đáy tối thiểu 320px, cách hai cạnh 90px).

### B. Bio TikTok (Tối đa 80 ký tự/dòng — Ngắn, rõ giá trị & hành động)
```text
Video Editor | Marketing Mindset | AI Workflow
Biến ý tưởng thành video rõ thông điệp & có mục tiêu.
👇 Nhận Starter Kit miễn phí & trao đổi dịch vụ Edit:
```

### C. Bio / Giới thiệu Facebook Cá nhân & Fanpage
```text
Mình là Thành — Video Editor có nền tảng Digital Marketing.
Mình chia sẻ cách kết hợp tư duy Marketing, kỹ năng dựng (Premiere/AE) và AI để biến ý tưởng thành video có chủ đích: người xem hiểu nhanh, nhớ lâu và biết cần làm gì tiếp theo.
📩 Nhắn "EDIT" nếu bạn cần dựng video cho kênh cá nhân / sản phẩm.
📂 Tài liệu Starter Kit, lộ trình học AI & công cụ mình dùng ở link bên dưới.
```

### D. Cấu trúc Link Bio 3 Nhánh (Không để quá 3 lựa chọn)
1. **Nhánh 1 (Tài liệu miễn phí — Thu Lead):** `[Nhận miễn phí] Starter Kit: Checklist Dựng Có Chủ Đích + 15 Hook + 5 Prompt AI + Mẫu Brief`
2. **Nhánh 2 (Dịch vụ — Tạo Doanh thu chính):** `[Làm việc cùng Thành] Dịch vụ Edit Video & Media có chủ đích (Gửi Brief / Nhắn chữ EDIT)`
3. **Nhánh 3 (Học AI & Công cụ — Affiliate):**
   - `Lộ trình học AI thực chiến cho người mới (Zero To AI)`
   - `Tổ hợp công cụ tạo ảnh, video & workflow AI mình đang dùng (Xưởng Media - link affiliate)`

---

## 2. KỊCH BẢN SẢN XUẤT 3 VIDEO GHIM (PINNED VIDEOS)

---

### 📌 VIDEO GHIM 01: GIỚI THIỆU ĐỊNH VỊ (Vị trí Ghim 1)
- **Tiêu đề:** Mình là Thành — Vì sao mình chọn "Dựng Có Chủ Đích"?
- **Mục tiêu:** Giúp người mới vào trang cá nhân hiểu ngay trong 25 giây: Thành là ai, kênh này giải quyết vấn đề gì và vì sao nên theo dõi.
- **Tệp người xem:** Creator, người xây thương hiệu cá nhân, chủ shop, editor mới.
- **Claim duy nhất:** Một video hiệu quả cần sự kết hợp của 3 lớp: Marketing quyết định nói gì, Edit biến thông điệp thành hình ảnh giữ mắt, và AI giúp thử nghiệm nhanh hơn.
- **CTA:** Theo dõi kênh để xem cách mình mổ xẻ và dựng video có chủ đích mỗi tuần.

#### Bảng phân cảnh chi tiết (25–30 giây)
| Thời gian | Hình ảnh / Góc máy / B-roll | Text trên màn hình | Lời thoại (Voiceover / Nói trực tiếp) |
| :--- | :--- | :--- | :--- |
| `00:00 - 00:04` | **Split-screen:** Bên trái là video nhiều hiệu ứng chuyển cảnh loè loẹt nhưng không rõ bán gì; bên phải là video cắt gọn, rõ thông điệp ngay 3 giây đầu. | **Đẹp thôi chưa đủ.**<br>Video cần tạo ra kết quả. | Rất nhiều video dựng cực kỳ mượt, nhưng người xem lướt qua sau ba giây vì không hiểu video đang nói với ai. |
| `00:04 - 00:10` | **A-roll:** Thành ngồi trước bàn làm việc, màn hình phía sau mở timeline Premiere Pro. Cắt cận vừa (Medium Close-up). | **Thành — Dựng Có Chủ Đích**<br>Marketing + Video Editing + AI | Mình là Thành, một video editor xuất phát từ nền tảng digital marketing. |
| `00:10 - 00:21` | **Screen Record + B-roll 3 nhịp theo lời nói:**<br>1. Bản brief/insight gạch chân 1 câu thông điệp.<br>2. Timeline Premiere cắt nhịp before/after.<br>3. Màn hình AI tạo 3 phương án hook và asset. | **1. Marketing:** Chọn đúng 1 thông điệp<br>**2. Edit:** Dẫn mắt & giữ nhịp<br>**3. AI:** Tăng tốc thử nghiệm | Trên kênh này, mình ghi lại quá trình kết hợp ba thứ: dùng tư duy marketing để khóa đúng một thông điệp, dùng kỹ thuật dựng để dẫn mắt người xem, và dùng AI đúng chỗ để rút ngắn thời gian làm phần thô. |
| `00:21 - 00:28` | **A-roll:** Thành nhìn thẳng ống kính, hiển thị 3 khung nội dung tiêu biểu trên kênh (Breakdown, Before/After, AI Workflow). | **Theo dõi kênh để làm video rõ & hiệu quả hơn** | Nếu bạn muốn làm video không chỉ đẹp mà còn khiến người xem hiểu, nhớ và hành động — theo dõi kênh nhé. Đó là cách mình dựng có chủ đích. |

#### Caption đăng bài
- **TikTok:** Mình không tự nhận là chuyên gia toàn năng. Đây là nơi mình chia sẻ cách kết hợp Marketing, Editing và AI để mỗi vết cắt trên timeline đều có lý do của nó. #dungcochudich #videoeditor #marketingvideo #aiworkflow
- **Facebook (Bài ghim trang cá nhân):**
  Chào bạn, nếu bạn mới ghé qua trang của mình thì đây là tóm tắt ngắn gọn mình đang làm gì.
  Mình học và làm Digital Marketing trước khi bước sang nghề Video Editor. Nhờ vậy, mỗi khi mở Premiere hay After Effects lên, câu hỏi đầu tiên của mình không phải là *"bỏ hiệu ứng gì cho ngầu"*, mà là *"người xem cần hiểu điều gì sau 30 giây này?"*.
  Trong 90 ngày tới, mình công khai toàn bộ quá trình làm nghề, các ca sửa video before/after, cách mình dùng AI làm phần thô và chỉnh tinh bằng tay.
  - Nếu bạn tự làm kênh: bạn sẽ tìm thấy checklist hook, cấu trúc kịch bản và cách dựng giữ chân người xem.
  - Nếu bạn cần người đồng hành dựng video có mục tiêu: nhắn chữ **EDIT** cho mình bất cứ lúc nào.

---

### 📌 VIDEO GHIM 02: BẰNG CHỨNG NĂNG LỰC BEFORE/AFTER (Vị trí Ghim 2)
- **Tiêu đề:** Cùng một bộ quay thô: Sửa 3 điểm này để biến video giới thiệu thành video ra khách
- **Mục tiêu:** Chứng minh tay nghề thực tế để chuyển đổi khách hàng dịch vụ Edit/Media.
- **Tệp người xem:** Khách hàng tiềm năng (chủ shop, thương hiệu cá nhân, doanh nghiệp nhỏ).
- **Claim duy nhất:** Thay đổi cấu trúc mở đầu, nhịp cắt và lời kêu gọi hành động trên cùng một footage gốc sẽ tạo ra hai kết quả hoàn toàn khác nhau.
- **CTA:** Nhắn chữ **"EDIT"** kèm mục tiêu của bạn nếu muốn mình xem và dựng lại video theo hướng này.

#### Bảng phân cảnh chi tiết (35–40 giây)
| Thời gian | Hình ảnh / Góc máy / B-roll | Text trên màn hình | Lời thoại (Voiceover / Nói trực tiếp) |
| :--- | :--- | :--- | :--- |
| `00:00 - 00:04` | **Before/After song song:** Cùng 1 đoạn footage gốc, bản A mở đầu bằng cảnh chào hỏi 5s; bản B mở ngay bằng kết quả sản phẩm/dịch vụ. | **Cùng 1 footage thô**<br>Vì sao bản B giữ người xem lâu gấp đôi? | Cùng một thư mục quay thô khách gửi, nhưng chỉ cần đổi ba quyết định dựng, hiệu quả giữ người xem đã khác hẳn. |
| `00:04 - 00:14` | **Screen Record Timeline:** Phóng to 3 giây đầu trên timeline. Kéo đoạn kết quả từ giây thứ 18 lên giây 00:00. | **Quyết định 1: Đảo kết quả lên 3 giây đầu** | Thứ nhất: mình cắt bỏ toàn bộ 5 giây chào hỏi đầu video và đẩy cảnh kết quả rõ nhất từ cuối lên ngay hai giây đầu tiên. |
| `00:14 - 00:24` | **Waveform & Visual Cut:** Cho xem đoạn cắt bỏ khoảng thở thừa và chèn B-roll minh họa đúng vào từ khóa khách hàng quan tâm. | **Quyết định 2: Cắt theo ý, đắp B-roll đúng từ khóa** | Thứ hai: thay vì cắt đều theo nhịp nhạc, mình giữ nhịp nhanh ở phần nêu vấn đề và chèn cận cảnh bằng chứng đúng lúc người nói nhắc đến lợi ích chính. |
| `00:24 - 00:32` | **So sánh 2 màn hình kết thúc (End card):** Bản cũ "Nhớ follow mình nhé" vs Bản mới "Nhắn mã [X] để nhận báo giá theo diện tích phòng". | **Quyết định 3: Đổi CTA chung chung → Lời mời cụ thể** | Thứ ba: mình bỏ câu kêu gọi theo dõi chung chung ở cuối, thay bằng một lời mời hành động cụ thể gắn với nhu cầu mua hàng. |
| `00:32 - 00:40` | **A-roll Thành:** Nói trực diện, hiển thị quy trình 3 bước nhận brief trên màn hình. | **Cần dựng video rõ thông điệp?**<br>Nhắn chữ **"EDIT"** | Nếu bạn đang có sẵn footage hoặc ý tưởng nhưng video lên chưa ra đúng chất và mục tiêu, nhắn chữ "EDIT" cho mình để mình xem thử nhé. |

#### Caption đăng bài
- **TikTok:** Đừng vội quay lại từ đầu khi video ít chuyển đổi. Nhiều khi vấn đề nằm ở thứ tự thông tin trên timeline. Nhắn "EDIT" nếu bạn cần người gỡ rối phần dựng nhé. #dungcochudich #beforeafter #videoediting #dichvuedit
- **Facebook:**
  Nhiều anh chị chủ shop hoặc làm thương hiệu cá nhân gửi file quay cho mình với tâm lý: *"Chắc phải đi quay lại chứ bản này nhìn chán quá"*.
  Nhưng khi mình mở footage ra xem, hình và tiếng đều đủ dùng — thứ duy nhất bị ngược là **thứ tự kể chuyện**: kết quả đẹp nhất lại giấu ở giây 25, còn 5 giây đầu lại dùng để giới thiệu tên tuổi.
  Trong video này là 3 bước mình luôn làm khi nhận một project: đảo kết quả lên đầu, cắt theo trọng tâm thông điệp và khóa lại bằng một CTA rõ ràng.
  Bạn đang có footage thô cần dựng thành video hoàn chỉnh? Nhắn chữ **EDIT** vào tin nhắn cho mình nhé.

---

### 📌 VIDEO GHIM 03: BẮT ĐẦU TỪ ĐÂU & STARTER KIT (Vị trí Ghim 3)
- **Tiêu đề:** Mới tự làm video xây kênh: Đừng quay trước khi có 4 thứ này
- **Mục tiêu:** Chuyển đổi người xem mới thành Lead qua bộ tài liệu miễn phí **Starter Kit v1**.
- **Tệp người xem:** Creator mới, chủ shop tự làm nội dung, người mới học làm video và AI.
- **Claim duy nhất:** Chuẩn bị trước Hook, cấu trúc 1-Claim, Shot List và Prompt AI trên 1 trang giấy giúp giảm một nửa thời gian quay dựng.
- **CTA:** Nhận miễn phí bộ **Starter Kit: Dựng Có Chủ Đích** ở link bio.

#### Bảng phân cảnh chi tiết (30–35 giây)
| Thời gian | Hình ảnh / Góc máy / B-roll | Text trên màn hình | Lời thoại (Voiceover / Nói trực tiếp) |
| :--- | :--- | :--- | :--- |
| `00:00 - 00:04` | **A-roll + Cận cảnh màn hình:** Thành giơ tờ/màn hình Checklist 1 trang bên cạnh timeline Premiere gọn gàng. | **Quay 2 tiếng nhưng lúc dựng thiếu cảnh?**<br>Dùng bộ khung 4 bước này. | Lý do lớn nhất khiến bạn quay hai tiếng nhưng lúc ngồi vào máy vẫn thiếu cảnh là vì bật máy quay trước khi khóa thông điệp. |
| `00:04 - 00:13` | **Screen Record:** Lướt nhanh qua 4 phần của Starter Kit: (1) 15 khung Hook, (2) Khung kịch bản 1-Claim, (3) Bảng Shot List, (4) 5 Prompt AI. | **1. 15 khung Hook 3 giây**<br>**2. Kịch bản 1-Claim** | Trước mỗi buổi quay batch 4 video, mình luôn đi qua bốn bước: một là chọn đúng một khung hook khớp với nỗi đau người xem; hai là gọt kịch bản về đúng một ý chính. |
| `00:13 - 00:23` | **Screen Record tiếp:** Cảnh dùng Prompt AI tách kịch bản thành bảng Shot List (A-roll, B-roll, Screen record) và Checklist 10 điểm trước khi Export. | **3. Bảng Shot List & 5 Prompt AI**<br>**4. Checklist 10 điểm trước khi xuất file** | Ba là dùng AI chuyển kịch bản đó thành danh sách cảnh quay để không sót B-roll; và bốn là rà qua 10 điểm kiểm tra phụ đề, âm thanh, CTA trước khi bấm xuất file. |
| `00:23 - 00:33` | **A-roll + Hướng dẫn bấm link bio:** Hiển thị giao diện link bio trên điện thoại, khoanh vào mục "Starter Kit". | **Tải miễn phí Starter Kit v1**<br>Ở ngay Link Bio của mình | Mình đã đóng gói toàn bộ checklist, mẫu brief, 15 cấu trúc hook và 5 prompt AI này thành bộ Starter Kit miễn phí. Bạn bấm vào link ở bio của mình để lấy về dùng ngay cho video tuần này nhé. |

#### Caption đăng bài
- **TikTok:** Toàn bộ quy trình chuẩn bị trước khi quay và checklist kiểm tra trước khi xuất video của mình nằm gọn trong Starter Kit này. Lấy miễn phí ở bio nhé! #dungcochudich #starterkit #xaykenhtiktok #videomarketing
- **Facebook:**
  Khi mới bắt đầu làm nội dung đều đặn mỗi tuần, thứ làm mình đuối sức nhất không phải là thao tác phần mềm, mà là mỗi lần ngồi vào bàn lại phải nghĩ lại từ đầu: *"Hôm nay mở đầu thế nào? Cần quay những cảnh gì? Viết prompt cho AI ra sao để đỡ sáo rỗng?"*
  Mình đã gom lại toàn bộ các biểu mẫu mình dùng hằng tuần thành bộ **Starter Kit v1 — Dựng Có Chủ Đích**, bao gồm:
  1. 15 khung Hook 3 giây đầu chia theo 3 mức độ nhận thức của người xem.
  2. Khung kịch bản 30 giây (1 Video = 1 Claim = 1 CTA).
  3. 5 Prompt AI thực chiến để tìm góc nội dung, viết lại script tự nhiên và lập Shot List.
  4. Mẫu Brief 1 trang & Checklist 10 điểm kiểm tra trước khi đăng.
  Bạn có thể tải về dùng miễn phí tại link bio hoặc bình luận dưới bài viết này để mình gửi trực tiếp nhé!

<!-- ===== /file: personal-brand-video-engine/references/00_CHIEN_LUOC/NGAY_02_HO_SO_KENH_VA_3_VIDEO_GHIM.md ===== -->

<!-- ===== file: personal-brand-video-engine/references/00_CHIEN_LUOC/SOP_SAN_XUAT_VIDEO_HANG_TUAN.md ===== -->

# Quy Trình Sản Xuất Batch 4 Video/Tuần (`DA-01`) & Ngân Hàng Câu Hỏi Khán Giả (`DA-02`)

> **Mục tiêu:** Giúp Thành duy trì nhịp xuất bản đều đặn **4 video/tuần trong 12 tuần (48 video)** mà không bị kiệt sức hay bí ý tưởng giữa chừng.

---

## 1. NHỊP SẢN XUẤT HÀNG TUẦN (BATCH WORKFLOW 7 NGÀY)

Để không rơi vào cảnh *"ngày nào đăng bài mới cuống cuồng viết và dựng ngày đó"*, toàn bộ lịch 90 ngày vận hành theo nguyên tắc **Tuần hiện tại đăng bài đã làm xong từ tuần trước, đồng thời sản xuất gối đầu cho tuần kế tiếp**:

| Thứ | Trọng tâm trong ngày | Đầu việc cụ thể | Thời lượng | Đầu ra bắt buộc |
| :--- | :--- | :--- | :---: | :--- |
| **Thứ Hai** | **Đăng Bài 1 (Bắt buộc)** + Khóa chủ đề tuần sau | - Đăng video số 1 trong tuần (TikTok + FB Reels/Post).<br>- Dành 30 phút trả lời bình luận và tin nhắn.<br>- Xem nhanh bảng KPI tuần trước.<br>- Khóa 4 mã `C0xx` của tuần tiếp theo (chốt rõ Tệp xem, 1 Claim, 1 CTA). | 120 phút | Link bài đăng 1 + 4 chủ đề tuần sau đã khóa. |
| **Thứ Ba** | **Đăng Bài 2 (Bắt buộc)** + Viết 4 Script tuần sau | - Đăng video số 2 trong tuần.<br>- Mở file kịch bản của Sprint tương ứng trong `01_Y_TUONG_VA_SCRIPT`, cá nhân hóa số liệu/ví dụ thật của tuần đó cho 4 script tuần sau.<br>- Lập danh sách tài nguyên màn hình cần quay. | 150 phút | Link bài đăng 2 + 4 kịch bản & shot list sẵn sàng bấm máy. |
| **Thứ Tư** | **Quay Batch 4 Video tuần sau** + Dựng nháp 2 bài | - Quay liền 1 mạch 4 phần A-roll của tuần sau (thay 2 áo để đổi cảm giác thị giác).<br>- Quay toàn bộ Screen Record (Premiere, AE, AI workflow) và B-roll bàn làm việc.<br>- Chép file vào `02_FOOTAGE` đúng mã `C0xx` và cắt nháp (Rough cut) 2 video đầu. | 240 phút | 4 bộ footage đủ hình/âm + 2 bản Rough cut. |
| **Thứ Năm** | **Đăng Bài 3 (Bắt buộc)** + Hoàn thiện 2 video đầu & Làm dự án dài ngày | - Đăng video số 3 trong tuần.<br>- Hoàn thiện dựng 2 video đầu của tuần sau.<br>- Dành 60 phút làm dự án dài ngày (`Starter Kit`, `Case Study`, hoặc `Funnel`). | 180 phút | Link bài đăng 3 + 2 video tuần sau hoàn chỉnh + 1 mốc dự án. |
| **Thứ Sáu** | **Hoàn thiện 2 video còn lại & Kiểm duyệt (QA)** | - Dựng nốt 2 video còn lại của tuần sau.<br>- Chạy Checklist QA 10 điểm (safe zone, chính tả phụ đề, âm thanh, CTA).<br>- Viết sẵn Caption TikTok & Bài đăng Facebook từ file kịch bản. | 210 phút | Đủ 4 file `.mp4` trong `04_EXPORT` + Caption sẵn sàng. |
| **Thứ Bảy** | **Đăng Bài 4 (Linh hoạt)** + Lên lịch tuần sau & Thu câu hỏi | - Đăng video số 4 trong tuần (nếu tuần đó quá tải công việc khách hàng, được phép lùi bài linh hoạt này nhưng tuyệt đối giữ 3 bài Thứ 2 - Thứ 3 - Thứ 5).<br>- Lên lịch sẵn tối thiểu 3 video tuần sau.<br>- Ghi ít nhất 5 câu hỏi/insight thật của khán giả vào bảng bên dưới. | 120 phút | Link bài đăng 4 + 5 câu hỏi khán giả + 3 bài tuần sau đã hẹn giờ. |
| **Chủ Nhật** | **Review Tuần / Sprint & Nghỉ ngơi (Buffer)** | - Nhập số liệu vào Sheet `Báo cáo KPI`.<br>- Nếu là cuối Tuần 3, 6, 9, 12: Làm báo cáo Sprint (`DA-06`).<br>- Thời gian còn lại nghỉ ngơi, không nhồi quay thêm 4 video mới. | 60–120 phút | Bảng KPI đã cập nhật. |

---

## 2. QUY TẮC QUẢN LÝ FILE TRONG THƯ MỤC DỰ ÁN

- **`02_FOOTAGE/`**: Tạo thư mục con theo mã, ví dụ `C001_BaGiayDau/`. Bên trong đặt tên chuẩn:
  - `C001_AROLL_01.mp4` (Cảnh nói trực diện)
  - `C001_SCREEN_01.mp4` (Quay màn hình Premiere / AI)
  - `C001_BROLL_01.mp4` (Cảnh phụ thao tác tay / màn hình phụ)
- **`03_PROJECT_EDIT/`**: Lưu project Premiere/After Effects theo tuần, ví dụ `TUAN_01_SPRINT_1.prproj`.
- **`04_EXPORT/`**: Lưu file xuất cuối cùng chuẩn `1080x1920`, đặt tên `C001_FINAL_20261026.mp4` kèm ảnh bìa `C001_THUMB.png`.

---

## 3. SỔ THEO DÕI NGÂN HÀNG CÂU HỎI KHÁN GIẢ (`DA-02` — Mục tiêu: 60 câu hỏi thật)

> Mỗi Thứ Bảy, trích xuất tối thiểu 5 bình luận, tin nhắn hoặc thắc mắc thực tế của khách hàng/người xem vào bảng này để biến thành chất liệu thực tế cho các tuần tiếp theo:

| STT | Ngày ghi nhận | Nguồn (Comment TikTok / FB / DM khách) | Nguyên văn câu hỏi hoặc vấn đề của người xem | Thuộc Pillar nào (`P1–P4`) | Gắn vào mã kịch bản nào hoặc tạo ý tưởng mới |
| :---: | :---: | :--- | :--- | :---: | :--- |
| 01 | 31/10/2026 | *[Ví dụ: Comment bài C001]* | *"Mình bán đồ gia dụng thì 3 giây đầu nên quay cảnh gì để khách không lướt qua?"* | P1 (`MKT01`) | Dùng làm ví dụ mở đầu cho bài `C003` (Chủ shop) |
| 02 | 31/10/2026 | *[Ví dụ: DM khách hỏi giá]* | *"Anh có sẵn 10 clip quay bằng điện thoại nhưng lộn xộn lắm, bên em có nhận cắt lại không?"* | P2 (`EDIT01`) | Đưa vào kịch bản `C023` & `C038` |
| 03 | 31/10/2026 | *[Ví dụ: Comment bài C040]* | *"Làm sao để ChatGPT không viết ra mấy câu kiểu 'Trong kỷ nguyên số ngày nay' vậy bạn?"* | P3 (`AI02`) | Dùng trực tiếp làm màn hình minh họa cho bài `C044` |
| 04 | ... | | | | |
| 05 | ... | | | | |

<!-- ===== /file: personal-brand-video-engine/references/00_CHIEN_LUOC/SOP_SAN_XUAT_VIDEO_HANG_TUAN.md ===== -->

<!-- ===== file: personal-brand-video-engine/references/00_CHIEN_LUOC/VOICE_PROFILE_VA_QUY_CHUAN_CONTENT.md ===== -->

# Hồ Sơ Giọng Điệu (Voice Profile) & Quy Chuẩn Sản Xuất Content — Thành (Dựng Có Chủ Đích)

> **Skills áp dụng:** `brand-voice` (xây dựng Voice Profile chuẩn hóa) + `content-engine` (chuyển hóa nguồn chiến lược thành kịch bản gốc theo từng nền tảng) + `crosspost` (chuyển thể đa kênh TikTok ↔ Facebook Reels ↔ Bài viết Facebook cá nhân).

---

## 1. VOICE PROFILE (`brand-voice` Canonical Schema)

```text
VOICE PROFILE
=============
Author: Thành — Dựng Có Chủ Đích (Marketing Video Editor ứng dụng AI)
Goal: Xây dựng uy tín thực chiến qua 48–60 video trong 90 ngày; thu hút lead Dịch vụ Edit/Media, người nhận Starter Kit, học viên Zero To AI và người dùng Xưởng Media mà không phóng đại kinh nghiệm.
Confidence: Medium-High (Khởi tạo từ Brief cá nhân, Ngày 01 Định vị và Hệ nội dung; sẽ khóa cố định sau 12–20 video thực tế).

Source Set
- THUONG_HIEU_CA_NHAN_THANH_90_NGAY/00_CHIEN_LUOC/NGAY_01_DINH_VI.md
- Sheet "Tổng quan", "Hệ nội dung", "Ngân hàng content", "Funnel & CTA" (He-thong-content-ca-nhan-Thanh.xlsx)
- Sheet "Lịch 90 ngày" & "Bảng thực thi" (generate_90_day_execution.mjs)

Rhythm
- Câu ngắn (8–16 từ/câu khi nói trên video).
- Mở đầu trực diện bằng kết quả, lỗi cụ thể trên màn hình hoặc 2 giây before/after.
- Ngắt nhịp rõ giữa các ý; dùng khoảng dừng 0.5–1 giây trước câu kết luận thay vì nhồi từ nối rườm rà.

Compression
- Độ nén cao: mỗi video 30–45 giây chỉ giải quyết đúng 1 vấn đề, 1 claim, 1 tệp người xem và 1 CTA.
- Không giải thích lý thuyết suông; luôn gắn liền với thao tác trên timeline Premiere/After Effects, màn hình prompt AI, hoặc bản so sánh A/B.

Capitalization
- Chuẩn tiếng Việt thông thường trong bài viết và phụ đề.
- Trên khung hình video (On-screen Text / Title Card): Viết hoa chữ cái đầu mỗi dòng hiển thị; từ khóa cần nhấn chỉ chọn 1 cụm duy nhất trên 1 khung hình.

Parentheticals
- Trong kịch bản nói: hạn chế ngoặc đơn làm đứt mạch nói.
- Trong bài viết Facebook: chỉ dùng ngoặc đơn để ghi chú thông số thật, điều kiện áp dụng hoặc giới hạn của công cụ AI (ví dụ: "(bản thô AI mất 2 phút, nhưng mình mất thêm 10 phút chỉnh lại nhịp cắt)").

Question Use
- Hiếm và có chủ đích.
- Chỉ dùng câu hỏi khi đó là câu hỏi thật của khách hàng/creator trong brief hoặc để mở ra phép thử Before/After.
- Tuyệt đối không dùng câu hỏi câu tương tác sáo rỗng ở cuối bài kiểu "Các bạn nghĩ sao?".

Claim Style
- Mọi nhận định đều đi theo cấu trúc: [Lỗi/Tình huống cụ thể] → [Quyết định dựng / Marketing / AI] → [Bằng chứng nhìn/nghe thấy được trên màn hình].
- Xưng "mình", gọi người xem là "bạn" (hoặc gọi rõ ngữ cảnh: "nếu bạn đang tự quay video bán hàng...", "khi mình nhận footage từ khách...").
- Định vị trung thực: người làm nghề có nền tảng marketing, gần 1 năm đi làm và hơn 6 tháng tập trung edit + ứng dụng AI công khai (build in public).

Preferred Moves
- Cho xem 2 giây bản gốc bị lỗi ngay đầu video rồi dừng hình để chỉ ra điểm gãy.
- Đặt kết quả (Final Cut) lên trước quy trình (Timeline).
- Luôn tách bạch phần "AI làm thô" (tìm góc, nháp script, tạo asset tĩnh/B-roll ngắn) và phần "Editor làm tinh" (chọn nhịp cắt, giữ cảm xúc, đặt điểm nhấn, kiểm soát thông điệp bán hàng).
- Kết video bằng câu khoá nhẹ nhàng hoặc biến thể tự nhiên của signature: "Đó là cách mình dựng có chủ đích."

Banned Moves
- Cấm mở đầu bằng: "Xin chào mọi người, mình là Thành...", "Trong thời đại AI bùng nổ hiện nay...", "Bí quyết triệu view", "Thay đổi cuộc đời".
- Cấm dùng các từ sáo rỗng: "siêu phẩm", "đỉnh nóc kịch trần", "AI làm thay 100%", "chỉ cần 1 click".
- Cấm tự nhận là "chuyên gia AI", "bậc thầy marketing" hay hứa hẹn cam kết doanh số ảo.
- Cấm nhồi 2–3 CTA hoặc bán cả Dịch vụ + Khóa học + Công cụ trong cùng một video.
- Cấm dùng câu hỏi mồi tương tác giả tạo ở cuối bài Facebook/TikTok.

CTA Rules
- Mỗi video chỉ gắn ĐÚNG 1 CTA khớp với giai đoạn Funnel và Offer của tuyến nội dung đó:
  1. Nhận biết (P1/P2/P4 không bán): "Lưu lại checklist/cấu trúc này để đối chiếu khi dựng video tiếp theo" hoặc "Theo dõi kênh để xem tiếp series..."
  2. Lead Magnet (Starter Kit): "Mình để sẵn bản Checklist / Template Hook–Body–Close / Mẫu Shot List trong Starter Kit ở bio, bạn vào lấy về dùng ngay."
  3. Chuyển đổi Dịch vụ (Edit/Media): "Nếu bạn có sẵn footage hoặc ý tưởng nhưng video chưa ra đúng thông điệp muốn bán, nhắn chữ 'EDIT' cho mình kèm mục tiêu video nhé."
  4. Chuyển đổi Học AI (Zero To AI): "Nếu bạn muốn học cách ứng dụng AI vào nội dung từ gốc theo lộ trình rõ ràng, xem mục Zero To AI ở bio của mình."
  5. Chuyển đổi Công cụ (Xưởng Media): "Mình chạy thử workflow tạo ảnh/video này trên Xưởng Media — link dùng thử (có affiliate) mình để rõ ở bio."

Channel Notes
- TikTok (Kênh thử nghiệm chính):
  - Video 9:16 (1080x1920), thời lượng 25–45s.
  - 3 giây đầu phải có chuyển động hình ảnh (split-screen, khoanh đỏ trên video lỗi, hoặc zoom timeline) + câu Hook đánh thẳng vào vấn đề.
  - Caption ngắn gọn (2–3 dòng), nêu lại core claim + 1 chỉ dẫn CTA rõ + 3–4 hashtag đúng ngách (#dungcochudich #videoediting #marketingvideo #aiworkflow).
- Facebook Reels (Kênh phủ & nuôi dưỡng):
  - Dùng cùng file video gốc nhưng viết lại phần mở đầu caption gần gũi hơn với tệp chủ shop / thương hiệu cá nhân / khách hàng tiềm năng.
- Facebook Cá Nhân / Bài Viết Dài (Kênh xây niềm tin & chuyển đổi):
  - Không copy-paste caption của TikTok.
  - Chuyển hóa kịch bản thành bài viết ngắn 150–250 chữ theo cấu trúc: Tình huống thực tế khi làm việc → 3 quyết định cụ thể (Marketing / Edit / AI) → Hình chụp màn hình timeline hoặc video đính kèm → Lời mời trao đổi hoặc nhận tài liệu.
```

---

## 2. ĐỐI CHIẾU & ĐỒNG BỘ 3 TRANG TRONG GOOGLE SHEET

Qua việc đọc kỹ 3 trang **Hệ nội dung**, **Ngân hàng content** và **Lịch sản xuất / Lịch 90 ngày**, bộ tài liệu này giải quyết triệt để sự khác biệt giữa hai bảng lịch trong Sheet để bạn vận hành trơn tru:

1. **Trang `Hệ nội dung`**:
   - Khóa tỷ trọng 4 Pillar: **P1 Marketing trong video (35%)** — **P2 Edit & Storytelling (30%)** — **P3 AI trong workflow editor (25%)** — **P4 Hành trình & Bằng chứng (10%)**.
   - Chia thành **23 tuyến nội dung** (`MKT01`–`MKT06`, `EDIT01`–`EDIT06`, `AI01`–`AI07`, `JRN01`–`JRN05`).
2. **Trang `Ngân hàng content`**:
   - Gồm **60 mã nội dung (`C001` đến `C060`)**, được sắp xếp theo từng nhóm Pillar (`C001`–`C021` là P1; `C022`–`C039` là P2; `C040`–`C054` là P3; `C055`–`C060` là P4).
3. **Đồng bộ giữa trang `Lịch sản xuất` và `Lịch 90 ngày` (`Bảng thực thi`)**:
   - Ở tab `Lịch sản xuất` ban đầu, danh sách lấy tuần tự từ `C001` đến `C048` nên 5 tuần đầu toàn bộ là P1 (chưa trộn đều 4 Pillar).
   - Ở tab `Lịch 90 ngày` (bản thực thi chuẩn), **48 video chính thức trong 12 tuần** đã được trộn chuẩn tỷ lệ **35% P1 / 30% P2 / 25% P3 / 10% P4** (mỗi tuần gồm **3 video bắt buộc** vào Thứ Hai, Thứ Ba, Thứ Năm + **1 video linh hoạt** vào Thứ Bảy).
   - **Giải pháp triển khai trong bộ content này**:
     - Chúng tôi viết **đầy đủ kịch bản chi tiết cho cả 60/60 mã (`C001`–`C060`)** + **3 Video Ghim**.
     - Sắp xếp các file kịch bản theo đúng **4 Sprint (12 tuần) của `Lịch 90 ngày`** (48 video) và đóng gói riêng **12 video còn lại (`C018`–`C021`, `C036`–`C039`, `C052`–`C054`, `C060`)** thành bộ **Video Báo Cáo Sprint, Case Study & Chuyển Đổi Sâu**. Nhờ vậy, dù bạn tra theo **Ngày/Tuần** hay tra theo **Mã `C001`–`C060`**, bạn đều có ngay kịch bản quay từng giây!

---

## 3. KHUNG KỊCH BẢN VIDEO NGẮN CHUẨN (`content-engine` Short Video Spec)

Mỗi video trong bộ 60 kịch bản đều tuân thủ cấu trúc 4 nhịp:

| Nhịp | Thời lượng | Mục tiêu | Quy tắc hình ảnh (Visual) | Quy tắc lời thoại (Audio) |
| :--- | :--- | :--- | :--- | :--- |
| **1. HOOK** | `00:00 – 00:03` | Giữ mắt + Nêu đúng nỗi đau hoặc kết quả | Cho xem ngay lỗi sai, bản so sánh A/B hoặc kết quả cuối cùng. Có text tiêu đề rõ trong vùng an toàn. | 1 câu duy nhất (dưới 12 từ). Không chào hỏi. |
| **2. PROOF / TENSION** | `00:03 – 00:10` | Chứng minh vấn đề là thật | Khoanh vùng trên frame, mở timeline Premiere hoặc chỉ vào đoạn script/output AI bị lỗi. | Chỉ ra nguyên nhân cốt lõi vì sao cách làm cũ khiến người xem lướt qua hoặc không hiểu. |
| **3. BODY (1 CLAIM)** | `00:10 – 00:32` | Giải quyết bằng 2–3 bước cụ thể | Cắt cảnh mỗi 2–4 giây: A-roll nói trực diện xen kẽ Screen Record thao tác thật và kết quả sau khi sửa. | Nói cụ thể từng bước: cắt chữ nào, đổi shot nào, nhập prompt gì, giữ lại gì. |
| **4. CLOSE & CTA** | `00:32 – 00:42` | Chốt bài học + 1 hành động tiếp theo | Chạy lại 2–3 giây bản hoàn chỉnh + Text card hiển thị CTA khớp với Offer. | Chốt câu ngắn gọn + 1 lời mời hành động tự nhiên (Lưu bài / Nhận Starter Kit / Nhắn EDIT / Xem lộ trình). |

<!-- ===== /file: personal-brand-video-engine/references/00_CHIEN_LUOC/VOICE_PROFILE_VA_QUY_CHUAN_CONTENT.md ===== -->

<!-- ===== file: personal-brand-video-engine/references/01_Y_TUONG_VA_SCRIPT/00_MASTER_INDEX_60_VIDEO.md ===== -->

# Master Index — Hệ Thống 60 Video Xây Kênh & Lịch Sản Xuất 12 Tuần

> **Tài liệu này đồng bộ hoàn toàn 3 trang trên Google Sheet:**
> 1. **Hệ nội dung:** 4 Pillar (`P1` 35% Marketing, `P2` 30% Edit & Storytelling, `P3` 25% AI Workflow, `P4` 10% Hành trình & Bằng chứng) và 23 tuyến nội dung (`MKT01`–`JRN05`).
> 2. **Ngân hàng content:** Đầy đủ 60 mã nội dung từ `C001` đến `C060`.
> 3. **Lịch sản xuất 12 tuần & Lịch 90 ngày:** 48 video chính thức phân bổ theo 4 Sprint (mỗi tuần 3 video bắt buộc vào Thứ Hai, Thứ Ba, Thứ Năm + 1 video linh hoạt vào Thứ Bảy, bắt đầu từ **26/10/2026** đến **16/01/2027**) + 12 video Báo cáo Sprint / Case Study / Chuyển đổi sâu.

---

## 1. DANH MỤC FILE KỊCH BẢN TRONG THƯ MỤC `01_Y_TUONG_VA_SCRIPT`

- [01_SPRINT_1_TUAN_01_03_THU_NGHIEM.md](file:///f:/THÀNH V/THCN thành/THUONG_HIEU_CA_NHAN_THANH_90_NGAY/01_Y_TUONG_VA_SCRIPT/01_SPRINT_1_TUAN_01_03_THU_NGHIEM.md): Kịch bản chi tiết 12 video Sprint 1 (Tuần 1–3: `C001, C022, C040, C055, C002, C003, C023, C041, C004, C024, C042, C056`).
- [02_SPRINT_2_TUAN_04_06_XAY_BANG_CHUNG.md](file:///f:/THÀNH V/THCN thành/THUONG_HIEU_CA_NHAN_THANH_90_NGAY/01_Y_TUONG_VA_SCRIPT/02_SPRINT_2_TUAN_04_06_XAY_BANG_CHUNG.md): Kịch bản chi tiết 12 video Sprint 2 (Tuần 4–6: `C005, C006, C025, C043, C007, C026, C044, C057, C008, C009, C027, C045`).
- [03_SPRINT_3_TUAN_07_09_TOI_UU_HE_THONG.md](file:///f:/THÀNH V/THCN thành/THUONG_HIEU_CA_NHAN_THANH_90_NGAY/01_Y_TUONG_VA_SCRIPT/03_SPRINT_3_TUAN_07_09_TOI_UU_HE_THONG.md): Kịch bản chi tiết 12 video Sprint 3 (Tuần 7–9: `C010, C028, C046, C058, C011, C012, C029, C047, C013, C030, C048, C059`).
- [04_SPRINT_4_TUAN_10_12_CHUYEN_DOI.md](file:///f:/THÀNH V/THCN thành/THUONG_HIEU_CA_NHAN_THANH_90_NGAY/01_Y_TUONG_VA_SCRIPT/04_SPRINT_4_TUAN_10_12_CHUYEN_DOI.md): Kịch bản chi tiết 12 video Sprint 4 (Tuần 10–12: `C014, C015, C031, C049, C016, C032, C033, C050, C017, C034, C035, C051`).
- [05_12_VIDEO_DU_PHONG_BAO_CAO_VA_CHUYEN_DOI_SAU.md](file:///f:/THÀNH V/THCN thành/THUONG_HIEU_CA_NHAN_THANH_90_NGAY/01_Y_TUONG_VA_SCRIPT/05_12_VIDEO_DU_PHONG_BAO_CAO_VA_CHUYEN_DOI_SAU.md): Kịch bản chi tiết 12 video Báo cáo Sprint, Case Study & Chuyển đổi sâu (`C018, C019, C020, C021, C036, C037, C038, C039, C052, C053, C054, C060`).
- [06_SHOT_LIST_QUAY_BATCH_TUAN_1.md](file:///f:/THÀNH V/THCN thành/THUONG_HIEU_CA_NHAN_THANH_90_NGAY/01_Y_TUONG_VA_SCRIPT/06_SHOT_LIST_QUAY_BATCH_TUAN_1.md): Kế hoạch bấm máy Batch 1 buổi (240 phút) cho 4 video Tuần 1 + 3 Video Ghim.

---

## 2. LỊCH SẢN XUẤT & XUẤT BẢN 48 VIDEO CHÍNH THỨC (12 TUẦN / 4 SPRINT)

### SPRINT 1: THỬ NGHIỆM HOOK & FORMAT (Tuần 1 – Tuần 3 | 26/10/2026 – 15/11/2026)

| Thứ tự | Ngày đăng | Thứ | Tuần | Mã ID | Pillar | Tuyến | Tiêu đề làm việc | Format | Tệp xem | Funnel | CTA | Offer | Loại lịch |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| 01 | 26/10/2026 | Thứ Hai | Tuần 1 | **C001** | P1 | MKT01 | Ba giây đầu đang làm người xem bỏ đi | Before/after | Creator | Nhận biết | Lưu checklist | Starter Kit | Bắt buộc |
| 02 | 27/10/2026 | Thứ Ba | Tuần 1 | **C022** | P2 | EDIT01 | Cùng footage, hai cách kể chuyện | Before/after | Khách hàng | Cân nhắc | Nhắn EDIT | Dịch vụ | Bắt buộc |
| 03 | 29/10/2026 | Thứ Năm | Tuần 1 | **C040** | P3 | AI01 | Tôi dùng AI để tìm 10 góc video từ một vấn đề | Screen record | Creator | Nhận biết | Nhận prompt | Zero To AI | Bắt buộc |
| 04 | 31/10/2026 | Thứ Bảy | Tuần 1 | **C055** | P4 | JRN01 | Tôi học marketing nhưng lại chọn nghề editor | Story | Tất cả | Tin cậy | Theo dõi hành trình | Không bán | Linh hoạt |
| 05 | 02/11/2026 | Thứ Hai | Tuần 2 | **C002** | P1 | MKT01 | Một hook yếu và ba cách viết lại | Talking head | Creator | Nhận biết | Bình luận hook | Không bán | Bắt buộc |
| 06 | 03/11/2026 | Thứ Ba | Tuần 2 | **C003** | P1 | MKT01 | Đừng mở video bằng câu xin chào | Breakdown | Chủ shop | Nhận biết | Lưu video | Không bán | Bắt buộc |
| 07 | 05/11/2026 | Thứ Năm | Tuần 2 | **C023** | P2 | EDIT01 | Tôi sửa nhịp video này trong 15 phút | BTS | Khách hàng | Tin cậy | Nhắn EDIT | Dịch vụ | Bắt buộc |
| 08 | 07/11/2026 | Thứ Bảy | Tuần 2 | **C041** | P3 | AI01 | ChatGPT, Claude và Gemini: tôi giao việc gì cho từng công cụ? | Comparison | Người học AI | Cân nhắc | Xem lộ trình | Zero To AI | Linh hoạt |
| 09 | 09/11/2026 | Thứ Hai | Tuần 3 | **C004** | P1 | MKT01 | Cách đặt kết quả lên trước quy trình | Screen record | Creator | Nhận biết | Theo dõi series | Không bán | Bắt buộc |
| 10 | 10/11/2026 | Thứ Ba | Tuần 3 | **C024** | P2 | EDIT01 | Chỉ thay thứ tự shot, cảm xúc đã khác | Breakdown | Creator | Nhận biết | Lưu video | Không bán | Bắt buộc |
| 11 | 12/11/2026 | Thứ Năm | Tuần 3 | **C042** | P3 | AI01 | AI cho ý tưởng nhưng ai chịu trách nhiệm chọn? | Talking head | Creator | Tin cậy | Lưu framework | Zero To AI | Bắt buộc |
| 12 | 14/11/2026 | Thứ Bảy | Tuần 3 | **C056** | P4 | JRN02 | Tuần này tôi học được gì trong After Effects? | Weekly log | Editor mới | Tin cậy | Theo dõi series | Không bán | Linh hoạt |

---

### SPRINT 2: XÂY BẰNG CHỨNG & STARTER KIT (Tuần 4 – Tuần 6 | 16/11/2026 – 06/12/2026)

| Thứ tự | Ngày đăng | Thứ | Tuần | Mã ID | Pillar | Tuyến | Tiêu đề làm việc | Format | Tệp xem | Funnel | CTA | Offer | Loại lịch |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| 13 | 16/11/2026 | Thứ Hai | Tuần 4 | **C005** | P1 | MKT02 | Video này đẹp nhưng không biết đang bán gì | Audit | Chủ shop | Cân nhắc | Nhắn EDIT | Dịch vụ | Bắt buộc |
| 14 | 17/11/2026 | Thứ Ba | Tuần 4 | **C006** | P1 | MKT02 | Một insight nên thành một video | Whiteboard | Marketer | Nhận biết | Lưu framework | Starter Kit | Bắt buộc |
| 15 | 19/11/2026 | Thứ Năm | Tuần 4 | **C025** | P2 | EDIT02 | Ba thao tác Premiere giúp timeline sạch hơn | Screen record | Editor mới | Nhận biết | Lưu tutorial | Không bán | Bắt buộc |
| 16 | 21/11/2026 | Thứ Bảy | Tuần 4 | **C043** | P3 | AI02 | Từ brief thành shot list bằng AI | Workflow demo | Creator | Cân nhắc | Nhận template | Zero To AI | Linh hoạt |
| 17 | 23/11/2026 | Thứ Hai | Tuần 5 | **C007** | P1 | MKT02 | Từ nỗi đau khách hàng thành câu mở đầu | Case | Creator | Cân nhắc | Nhận mẫu | Starter Kit | Bắt buộc |
| 18 | 24/11/2026 | Thứ Ba | Tuần 5 | **C026** | P2 | EDIT02 | Khi nào nên dùng adjustment layer? | Tutorial | Editor | Nhận biết | Theo dõi series | Không bán | Bắt buộc |
| 19 | 26/11/2026 | Thứ Năm | Tuần 5 | **C044** | P3 | AI02 | AI viết script nghe như máy, tôi sửa thế nào? | Before/after | Creator | Nhận biết | Nhận prompt | Zero To AI | Bắt buộc |
| 20 | 28/11/2026 | Thứ Bảy | Tuần 5 | **C057** | P4 | JRN02 | 30 ngày học motion: tiến bộ nào nhìn thấy được? | Progress | Editor mới | Tin cậy | Lưu hành trình | Không bán | Linh hoạt |
| 21 | 30/11/2026 | Thứ Hai | Tuần 6 | **C008** | P1 | MKT02 | Brief nói nhiều nhưng video cần nói một điều | BTS | Khách hàng | Tin cậy | Nhắn brief | Dịch vụ | Bắt buộc |
| 22 | 01/12/2026 | Thứ Ba | Tuần 6 | **C009** | P1 | MKT03 | CTA theo dõi không phù hợp mọi video | Talking head | Creator | Nhận biết | Lưu bảng CTA | Starter Kit | Bắt buộc |
| 23 | 03/12/2026 | Thứ Năm | Tuần 6 | **C027** | P2 | EDIT02 | Cách dựng phiên bản dọc từ footage ngang | Tutorial | Creator | Nhận biết | Nhận checklist | Starter Kit | Bắt buộc |
| 24 | 05/12/2026 | Thứ Bảy | Tuần 6 | **C045** | P3 | AI02 | Dùng AI tạo ba phiên bản hook để A/B test | Screen record | Marketer | Cân nhắc | Nhận prompt | Zero To AI | Linh hoạt |

---

### SPRINT 3: TỐI ƯU HỆ THỐNG & FUNNEL (Tuần 7 – Tuần 9 | 07/12/2026 – 27/12/2026)

| Thứ tự | Ngày đăng | Thứ | Tuần | Mã ID | Pillar | Tuyến | Tiêu đề làm việc | Format | Tệp xem | Funnel | CTA | Offer | Loại lịch |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| 25 | 07/12/2026 | Thứ Hai | Tuần 7 | **C010** | P1 | MKT03 | Ba CTA cho ba mức độ sẵn sàng mua | Carousel video | Chủ shop | Cân nhắc | Nhận bảng | Starter Kit | Bắt buộc |
| 26 | 08/12/2026 | Thứ Ba | Tuần 7 | **C028** | P2 | EDIT03 | Khi nào Premiere đủ, khi nào cần After Effects? | Talking head | Editor mới | Nhận biết | Lưu video | Không bán | Bắt buộc |
| 27 | 10/12/2026 | Thứ Năm | Tuần 7 | **C046** | P3 | AI03 | Tạo asset sản phẩm bằng AI rồi đưa vào Premiere | Workflow demo | Chủ shop | Cân nhắc | Dùng thử công cụ | Xưởng Media | Bắt buộc |
| 28 | 12/12/2026 | Thứ Bảy | Tuần 7 | **C058** | P4 | JRN03 | Một ngày làm media của tôi | BTS vlog | Khách hàng | Tin cậy | Nhắn câu hỏi | Dịch vụ | Linh hoạt |
| 29 | 14/12/2026 | Thứ Hai | Tuần 8 | **C011** | P1 | MKT03 | Sửa CTA cuối video dịch vụ | Before/after | Khách hàng | Chuyển đổi | Nhắn EDIT | Dịch vụ | Bắt buộc |
| 30 | 15/12/2026 | Thứ Ba | Tuần 8 | **C012** | P1 | MKT04 | Công thức hook–body–close trong 30 giây | Tutorial | Creator | Nhận biết | Nhận template | Starter Kit | Bắt buộc |
| 31 | 17/12/2026 | Thứ Năm | Tuần 8 | **C029** | P2 | EDIT03 | Một text animation để nhấn đúng từ khóa | Screen record | Editor | Nhận biết | Theo dõi hành trình | Không bán | Bắt buộc |
| 32 | 19/12/2026 | Thứ Bảy | Tuần 8 | **C047** | P3 | AI03 | Một ảnh sản phẩm có thể tạo bao nhiêu video? | Experiment | Affiliate marketer | Nhận biết | Xem workflow | Xưởng Media | Linh hoạt |
| 33 | 21/12/2026 | Thứ Hai | Tuần 9 | **C013** | P1 | MKT04 | Một video chỉ nên có một claim | Screen record | Creator | Nhận biết | Lưu video | Không bán | Bắt buộc |
| 34 | 22/12/2026 | Thứ Ba | Tuần 9 | **C030** | P2 | EDIT03 | Motion đẹp nhưng có làm người xem hiểu hơn? | Before/after | Creator | Cân nhắc | Nhắn EDIT | Dịch vụ | Bắt buộc |
| 35 | 24/12/2026 | Thứ Năm | Tuần 9 | **C048** | P3 | AI03 | AI video nào dùng được, video nào phải bỏ? | Review | Creator | Cân nhắc | Lưu checklist | Xưởng Media | Bắt buộc |
| 36 | 26/12/2026 | Thứ Bảy | Tuần 9 | **C059** | P4 | JRN04 | Sai lầm lớn nhất khi mới nhận job edit | Reflection | Editor mới | Tin cậy | Lưu bài học | Không bán | Linh hoạt |

---

### SPRINT 4: CHUYỂN ĐỔI OFFER & TỔNG KẾT (Tuần 10 – Tuần 12 | 28/12/2026 – 17/01/2027)

| Thứ tự | Ngày đăng | Thứ | Tuần | Mã ID | Pillar | Tuyến | Tiêu đề làm việc | Format | Tệp xem | Funnel | CTA | Offer | Loại lịch |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| 37 | 28/12/2026 | Thứ Hai | Tuần 10 | **C014** | P1 | MKT04 | Cách biến một ý tưởng thành năm góc nội dung | Whiteboard | Creator | Nhận biết | Nhận worksheet | Starter Kit | Bắt buộc |
| 38 | 29/12/2026 | Thứ Ba | Tuần 10 | **C015** | P1 | MKT04 | Tạo shot list trước khi quay có ích gì? | BTS | Creator | Cân nhắc | Nhận mẫu shot list | Starter Kit | Bắt buộc |
| 39 | 31/12/2026 | Thứ Năm | Tuần 10 | **C031** | P2 | EDIT04 | Khoảng dừng đôi khi mạnh hơn một transition | Breakdown | Editor | Nhận biết | Lưu bài học | Không bán | Bắt buộc |
| 40 | 02/01/2027 | Thứ Bảy | Tuần 10 | **C049** | P3 | AI04 | AI làm thô, editor làm tinh: tập 1 | Before/after | Khách hàng | Cân nhắc | Theo dõi series | Dịch vụ | Linh hoạt |
| 41 | 04/01/2027 | Thứ Hai | Tuần 11 | **C016** | P1 | MKT05 | Mổ video 30 giây: vì sao đoạn này giữ mắt? | Breakdown | Marketer | Nhận biết | Theo dõi series | Không bán | Bắt buộc |
| 42 | 05/01/2027 | Thứ Ba | Tuần 11 | **C032** | P2 | EDIT04 | Cách cắt theo ý, không chỉ cắt theo nhạc | Tutorial | Editor | Nhận biết | Nhận checklist | Starter Kit | Bắt buộc |
| 43 | 07/01/2027 | Thứ Năm | Tuần 11 | **C033** | P2 | EDIT04 | Tạo reveal để giữ sự tò mò | Remake | Creator | Nhận biết | Theo dõi series | Không bán | Bắt buộc |
| 44 | 09/01/2027 | Thứ Bảy | Tuần 11 | **C050** | P3 | AI04 | Năm lỗi AI không tự nhận ra trong video | Audit | Creator | Nhận biết | Lưu video | Không bán | Linh hoạt |
| 45 | 11/01/2027 | Thứ Hai | Tuần 12 | **C017** | P1 | MKT05 | Một quảng cáo đang nhồi quá nhiều thông tin | Audit | Chủ shop | Cân nhắc | Nhắn EDIT | Dịch vụ | Bắt buộc |
| 46 | 12/01/2027 | Thứ Ba | Tuần 12 | **C034** | P2 | EDIT05 | Ba lỗi subtitle khiến video khó đọc | Audit | Creator | Nhận biết | Nhận checklist | Starter Kit | Bắt buộc |
| 47 | 14/01/2027 | Thứ Năm | Tuần 12 | **C035** | P2 | EDIT05 | Sound effect không nên có mặt ở mọi cut | Before/after | Editor | Nhận biết | Lưu video | Không bán | Bắt buộc |
| 48 | 16/01/2027 | Thứ Bảy | Tuần 12 | **C051** | P3 | AI04 | Tại sao AI chưa thay editor trong case này? | Case study | Khách hàng | Tin cậy | Nhắn EDIT | Dịch vụ | Linh hoạt |

---

## 3. 12 VIDEO BÁO CÁO SPRINT, CASE STUDY & CHUYỂN ĐỔI SÂU (TRONG NGÂN HÀNG 60 CONTENT)

> Dùng để thay thế vào các tuần Review Sprint (Tuần 3, 6, 9, 12), khi công bố 3 Case Study (`DA-03`), hoặc tăng tốc chuyển đổi Offer ở Giai đoạn Chuyển đổi (`DA-07`).

| Mã ID | Pillar | Tuyến | Tiêu đề làm việc | Format | Tệp xem | Funnel | CTA | Offer | Thời điểm khuyên dùng |
| :---: | :---: | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| **C018** | P1 | MKT05 | Phân tích một video bán hàng không cần hiệu ứng mạnh | Breakdown | Chủ shop | Nhận biết | Lưu video | Không bán | Dự phòng P1 / Tuần 5–8 |
| **C019** | P1 | MKT06 | Sau 12 video tôi giữ lại format nào? | Report | Creator | Tin cậy | Nhận bảng KPI | Starter Kit | Cuối Sprint 1 (15/11/2026) |
| **C020** | P1 | MKT06 | Nhiều view nhưng không có khách vì sao? | Talking head | Creator | Cân nhắc | Kiểm tra funnel | Không bán | Cuối Sprint 2 (06/12/2026) |
| **C021** | P1 | MKT06 | Ba chỉ số editor nên xem ngoài lượt xem | Tutorial | Editor | Nhận biết | Lưu checklist | Starter Kit | Cuối Sprint 3 (27/12/2026) |
| **C036** | P2 | EDIT05 | Cách chọn một từ để nhấn bằng motion | Tutorial | Editor | Nhận biết | Theo dõi series | Không bán | Dự phòng P2 / Tuần 8–11 |
| **C037** | P2 | EDIT06 | Quy trình của tôi từ brief đến bản dựng | BTS | Khách hàng | Tin cậy | Nhắn EDIT | Dịch vụ | Mở bán Dịch vụ (Tuần 9–10) |
| **C038** | P2 | EDIT06 | Vì sao editor cần hỏi mục tiêu trước khi nhận file? | Talking head | Khách hàng | Cân nhắc | Nhận mẫu brief | Starter Kit | Khi ra mắt Starter Kit (Tuần 6) |
| **C039** | P2 | EDIT06 | Một vòng feedback tốt cần những gì? | Tutorial | Khách hàng | Tin cậy | Nhắn EDIT | Dịch vụ | Đẩy dịch vụ Edit (Tuần 10–12) |
| **C052** | P3 | AI05 | So sánh hai model bằng cùng một prompt | Comparison | Người học AI | Cân nhắc | Dùng thử | Xưởng Media | Đẩy affiliate Xưởng Media (Tuần 11) |
| **C053** | P3 | AI06 | Workflow từ ý tưởng đến 10 biến thể nội dung | Flow demo | Agency, creator | Chuyển đổi | Xem workflow | Xưởng Media | Đẩy affiliate Xưởng Media (Tuần 11–12) |
| **C054** | P3 | AI07 | Nếu bắt đầu AI video từ số 0, tôi học theo thứ tự này | Roadmap | Người mới | Chuyển đổi | Xem lộ trình | Zero To AI | Đẩy affiliate Zero To AI (Tuần 10–12) |
| **C060** | P4 | JRN05 | Case study: từ footage thô đến video hoàn chỉnh | Case study | Khách hàng | Chuyển đổi | Nhắn EDIT | Dịch vụ | Mốc hoàn thành Case Study (29/11, 13/12, 27/12) |

<!-- ===== /file: personal-brand-video-engine/references/01_Y_TUONG_VA_SCRIPT/00_MASTER_INDEX_60_VIDEO.md ===== -->

<!-- ===== file: personal-brand-video-engine/references/01_Y_TUONG_VA_SCRIPT/01_SPRINT_1_TUAN_01_03_THU_NGHIEM.md ===== -->

# KỊCH BẢN SẢN XUẤT CHI TIẾT — SPRINT 1: THỬ NGHIỆM HOOK & FORMAT (TUẦN 1 – TUẦN 3)

> **Giai đoạn:** Tuần 1 đến Tuần 3 (`26/10/2026 – 15/11/2026`)
> **Mục tiêu Sprint 1:** Thiết lập baseline về khả năng giữ chân 3 giây đầu (Hook rate), kiểm chứng tệp khán giả trên 4 Pillar (`P1 Marketing`, `P2 Edit & Storytelling`, `P3 AI Workflow`, `P4 Hành trình`) và rèn nhịp sản xuất 4 video/tuần (3 bắt buộc + 1 linh hoạt).
> **Quy chuẩn áp dụng:** Tuân thủ nghiêm ngặt `VOICE_PROFILE_VA_QUY_CHUAN_CONTENT.md` (`brand-voice` + `content-engine` + `crosspost`).

---

## TUẦN 1: THIẾT LẬP BASELINE HOOK & GIỮ NGƯỜI XEM (26/10/2026 – 31/10/2026)

---

### 🎬 VIDEO 01 — MÃ `C001`: BA GIÂY ĐẦU ĐANG LÀM NGƯỜI XEM BỎ ĐI

#### 1. Thông tin định danh
- **Ngày đăng:** Thứ Hai, 26/10/2026 (Lịch bắt buộc)
- **Pillar / Tuyến nội dung:** `P1 — Marketing trong video` / `MKT01 — Hook & 3 giây đầu`
- **Format:** Before/After (So sánh trực diện bản lỗi và bản sửa)
- **Tệp người xem:** Creator, người xây thương hiệu cá nhân mới bắt đầu
- **Mục tiêu Funnel:** Nhận biết (Awareness)
- **Claim duy nhất:** Người xem lướt qua không phải vì nội dung dở, mà vì 3 giây đầu toàn lời chào hỏi và cảnh lấy hơi thừa thay vì đi thẳng vào kết quả.
- **Bằng chứng cần chuẩn bị:** 1 đoạn video tự dựng có 2 phiên bản: Bản A (mở đầu hít hơi, chào hỏi 3 giây) và Bản B (cắt thẳng vào câu kết luận + hình ảnh minh họa).
- **CTA & Offer:** Lưu checklist 3 giây đầu / Giới thiệu nhẹ **Starter Kit** ở bio.

#### 2. Bảng kịch bản chi tiết (36 giây)
| Timecode | Hình ảnh / Thao tác màn hình | Text trên màn hình | Lời thoại của Thành + Nhịp / SFX |
| :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **Bản Before (2 giây đầu):** Cảnh một bạn creator đang chỉnh áo, hít hơi rồi nói *"À ừm, hello mọi người..."*. Đúng giây 00:02: Dừng hình (Freeze frame), đóng khung đỏ + icon ngón tay lướt qua. | **Ba giây đầu** đang làm người xem bỏ đi | *[2s tiếng video gốc]* — *[SFX: Phanh gấp / Click]* Đây là lý do video của bạn mất bảy mươi phần trăm người xem ngay ba giây đầu. |
| `00:03 – 00:10` | **A-roll Thành (Medium Close-up):** Ngồi góc bàn làm việc, màn hình Premiere mở sẵn phía sau. Cắt zoom nhẹ 105% vào câu chốt. | Đừng bắt người lạ chờ bạn **lấy đà** | Khi người xem chưa biết bạn là ai, họ không có lý do để chờ bạn chào hỏi hay giới thiệu tên. *[Nghỉ 0.5s]* |
| `00:10 – 00:20` | **Screen Record Timeline Premiere:** Phóng to khu vực `00:00 – 00:05`. Dùng công cụ Razor (C) cắt phăng đoạn lấy hơi + câu chào đầu. Kéo cảnh kết quả ở giây `00:22` lên đầu timeline. | **Bước 1:** Cắt bỏ đoạn lấy hơi & chào hỏi<br>**Bước 2:** Đẩy câu kết quả lên giây `00:00` | Cách mình sửa trên timeline rất đơn giản. *[SFX: Whoosh nhẹ]* Một: cắt bỏ toàn bộ khoảng lấy hơi và câu chào đầu tiên. Hai: tìm câu nói rõ kết quả nhất ở giữa bài, kéo thẳng lên giây không không. |
| `00:20 – 00:30` | **Bản After chạy thực tế (Split-screen trên/dưới với Waveform):** Video mở vào phát ăn ngay câu trọng tâm kèm B-roll minh họa sát chữ. | **Bản gốc:** Mất 4 giây mới vào đề<br>**Bản sửa:** Vào thẳng vấn đề ở giây đầu tiên | Nhìn lại bản sau khi sửa nhé: vừa mở lên là thấy ngay vấn đề của người xem và bằng chứng trên màn hình. Nhịp gọn hơn hẳn mà không cần thêm hiệu ứng phức tạp. |
| `00:30 – 00:36` | **A-roll Thành + Card Checklist trên màn hình:** Hiện 3 dòng checklist kiểm tra 3 giây đầu (Không chào hỏi / Có chuyển động hình / Nêu đúng 1 nỗi đau). | Lưu lại **checklist 3 giây đầu** ở bio | Trước khi xuất file, bạn hãy kiểm tra lại đúng ba giây đầu tiên này. *[Nghỉ 0.5s]* Mình để sẵn bản checklist đầy đủ trong Starter Kit ở bio, bạn lưu lại để đối chiếu khi dựng nhé. |

#### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] `C001_AROLL_01.mp4`: Thành nói trực diện ống kính toàn bộ lời thoại (quay 2–3 take liền mạch, giữ ánh mắt tĩnh).
- [ ] `C001_BROLL_SAMPLE_RAW.mp4`: Đoạn video mẫu tự quay có 3 giây đầu chỉnh mic, hít hơi, chào hỏi rườm rà.
- [ ] `C001_SCREEN_01.mp4`: Quay màn hình Premiere Pro (1920x1080 hoặc crop dọc) cảnh dùng phím `C` cắt bỏ 3 giây đầu, Ripple Delete và kéo clip từ cuối lên đầu.
- [ ] `C001_ASSET_01.png`: Ảnh chụp trang Checklist 3 giây đầu trong bộ Starter Kit.

#### 4. Bản phân phối đa kênh (`crosspost`)
- **Caption TikTok / Reels:**
  - **Text trên Thumbnail:** Ba giây đầu làm mất người xem
  - **Caption:** Đừng để người xem rời đi trước khi nghe phần hay nhất ở giữa video. Cắt bỏ câu chào hỏi và đẩy kết quả lên giây 00:00. Bản checklist kiểm tra 3 giây đầu mình để sẵn trong Starter Kit ở bio nhé. `#dungcochudich #videoediting #marketingvideo #xaykenhtiktok`
- **Bài đăng Facebook cá nhân (155 chữ):**
  Tuần này khi ngồi rà lại những video tự quay lúc mới tập làm kênh, mình nhận ra một lỗi cực kỳ phổ biến: mình thường dùng 4 giây đầu tiên chỉ để lấy hơi, chỉnh lại cổ áo và nói câu *"Xin chào mọi người, hôm nay mình sẽ chia sẻ..."*.
  Với bạn bè quen biết thì họ có thể kiên nhẫn xem tiếp. Nhưng với người lạ trên feed, 4 giây không có thông tin đó là lúc họ lướt qua.
  Khi dựng có chủ đích, mình xử lý 3 giây đầu bằng 3 thao tác cố định trên timeline:
  1. Cắt sát vào chữ đầu tiên có nghĩa (xoá toàn bộ khoảng thở mở bài).
  2. Lấy câu kết luận đắt nhất ở giây thứ 20 đẩy lên làm câu mở đầu.
  3. Đặt 1 dòng tiêu đề ngắn trên màn hình khớp đúng nỗi đau của người xem (viết hoa chữ cái đầu, nhấn đúng 1 cụm từ khóa).
  Mình có đóng gói bảng rà soát 3 giây đầu này vào bộ Starter Kit miễn phí ở phần giới thiệu trang cá nhân, bạn có thể lấy về để tự kiểm tra trước khi bấm xuất video tiếp theo.

---

### 🎬 VIDEO 02 — MÃ `C022`: CÙNG FOOTAGE, HAI CÁCH KỂ CHUYỆN

#### 1. Thông tin định danh
- **Ngày đăng:** Thứ Ba, 27/10/2026 (Lịch bắt buộc)
- **Pillar / Tuyến nội dung:** `P2 — Edit & Storytelling` / `EDIT01 — Tư duy cắt dựng & nhịp độ`
- **Format:** Before/After (Chạy song song bản dựng thường và bản dựng có chủ đích)
- **Tệp người xem:** Khách hàng tiềm năng (Chủ shop, thương hiệu cá nhân, đội marketing nhỏ)
- **Mục tiêu Funnel:** Cân nhắc (Consideration)
- **Claim duy nhất:** Cùng một bộ footage quay thô, nếu dựng theo thứ tự thời gian thì thành video báo cáo nhạt nhẽo, nhưng dựng theo cấu trúc tâm lý khách hàng thì thành video bán hàng.
- **Bằng chứng cần chuẩn bị:** 4 clip quay thô có bản quyền (ví dụ: pha cà phê / đóng gói sản phẩm / làm việc tại bàn): (1) Cảnh chuẩn bị nguyên liệu, (2) Cảnh thao tác, (3) Cảnh lỗi/vấn đề, (4) Cảnh thành phẩm đẹp mắt.
- **CTA & Offer:** Nhắn chữ **"EDIT"** nếu bạn có sẵn footage nhưng dựng chưa ra đúng thông điệp bán hàng (Offer: **Dịch vụ Edit/Media**).

#### 2. Bảng kịch bản chi tiết (38 giây)
| Timecode | Hình ảnh / Thao tác màn hình | Text trên màn hình | Lời thoại của Thành + Nhịp / SFX |
| :--- | :--- | :--- | :--- |
| `00:00 – 00:04` | **Split-screen dọc:** Bên trên là "Bản dựng theo thứ tự quay", bên dưới là "Bản dựng có chủ đích". Cả hai dùng chung đúng 4 file video gốc. | **Cùng một bộ quay thô**<br>Hai cách kể chuyện khác hẳn nhau | Cùng một thư mục quay thô bốn cảnh, nhưng cách bạn sắp xếp trên timeline sẽ quyết định người xem lướt đi hay nhắn tin mua hàng. |
| `00:04 – 00:13` | **Phóng to Bản 1 (Dựng thuận chiều thời gian):** Cảnh 1 lấy đồ → Cảnh 2 pha chế → Cảnh 3 đóng nắp → Cảnh 4 thành phẩm. Nhịp cắt đều 2.5s/cảnh. | **Cách 1: Dựng theo thứ tự quay**<br>Đẹp nhưng người xem không thấy liên quan | *[SFX: Tick-tock đều]* Ở bản thứ nhất, mình xếp đúng theo trình tự lúc bấm máy: chuẩn bị, thao tác rồi mới tới thành phẩm. Nhìn vẫn sạch, nhưng ba giây đầu không nói được lợi ích gì cho khách. |
| `00:13 – 00:24` | **Screen Record Timeline Bản 2:** Thành đảo Cảnh 4 (Thành phẩm bắt mắt nhất) lên `00:00`, nối ngay bằng Cảnh 3 (Vấn đề khách hay gặp), rồi mới mở ra quy trình giải quyết. | **Cách 2: Dựng theo tâm lý mua hàng**<br>Kết quả → Nỗi đau → Bằng chứng xử lý | *[SFX: Whoosh + Click]* Sang bản thứ hai, mình đổi lại thứ tự kể chuyện. Mở đầu ngay bằng cận cảnh thành phẩm đẹp nhất trong một phẩy năm giây, tiếp theo là lỗi khách thường gặp, rồi mới dùng cảnh thao tác làm bằng chứng. |
| `00:24 – 00:31` | **Chạy kết quả Bản 2 toàn màn hình (5 giây):** Nhịp cắt nhanh ở 2 cảnh đầu, chậm lại ở cảnh chi tiết chất lượng sản phẩm, có text nhấn lợi ích. | Giữ nhịp nhanh ở **vấn đề**<br>Chậm lại ở **bằng chứng chất lượng** | Bạn có thể thấy: không cần quay lại một cảnh nào, chỉ cần đổi điểm mở đầu và giữ lâu hơn ở khung hình chứng minh chất lượng, cảm giác tin cậy đã tăng lên rõ rệt. |
| `00:31 – 00:38` | **A-roll Thành nói trực diện:** Khung hình sạch, hiển thị dòng hướng dẫn nhắn tin gọn ở góc dưới. | Có sẵn footage nhưng chưa ra chất?<br>Nhắn chữ **EDIT** cho mình | Đó là cách mình dựng có chủ đích. *[Nghỉ 0.5s]* Nếu bạn đang có sẵn footage sản phẩm hoặc kênh cá nhân nhưng lên video chưa ra đúng thông điệp muốn bán, nhắn chữ "EDIT" cho mình nhé. |

#### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] `C022_AROLL_01.mp4`: Thành nói đoạn phân tích và câu kết CTA (góc Medium Close-up).
- [ ] `C022_BROLL_RAW_01..04.mp4`: Bộ 4 cảnh quay thực tế (bàn làm việc/sản phẩm mẫu) có đủ góc rộng, góc trung, góc cận chi tiết và cảnh kết quả.
- [ ] `C022_SCREEN_01.mp4`: Quay màn hình 2 Sequence đặt cạnh nhau trong Premiere Pro (`Seq_01_Chronological` và `Seq_02_PurposeDriven`), thấy rõ màu label clip được đảo vị trí.

#### 4. Bản phân phối đa kênh (`crosspost`)
- **Caption TikTok / Reels:**
  - **Text trên Thumbnail:** Cùng 1 footage — 2 cách kể chuyện
  - **Caption:** Quay xong thấy video nhạt chưa chắc do máy quay hay ánh sáng, mà thường do mình đang xếp cảnh theo thứ tự lúc bấm máy thay vì thứ tự tâm lý người xem. Nhắn chữ "EDIT" nếu bạn cần người gỡ rối đống footage thô nhé. `#dungcochudich #videoediting #storytelling #marketingvideo`
- **Bài đăng Facebook cá nhân (165 chữ):**
  Khi nhận file quay thô từ các anh chị chủ shop hoặc người xây kênh cá nhân, câu mình nghe nhiều nhất là: *"Footage đợt này quay bình thường quá Thành ơi, chắc không dựng ra gì đặc sắc được đâu"*.
  Thực tế là người xem trên mạng xã hội không chấm điểm máy quay của bạn. Họ chỉ quan tâm thông tin xuất hiện ở giây thứ mấy.
  Nếu chúng ta dựng theo kiểu nhật ký bấm máy (bước 1 chuẩn bị → bước 2 làm → bước 3 xong kết quả), người xem đã rời đi từ bước 1.
  Khi dựng lại bộ footage đó theo hướng có chủ đích, mình luôn đảo cấu trúc thành 3 nhịp:
  1. Đưa khung hình kết quả thuyết phục nhất lên 2 giây đầu (cho mắt người xem một lý do để dừng lại).
  2. Đặt vấn đề sát sườn ngay sau đó.
  3. Dùng các cảnh thao tác hậu trường làm bằng chứng chứng minh lời nói (chỉ giữ lại 30% độ dài clip gốc, cắt bỏ toàn bộ thao tác thừa).
  Nếu bạn đang có sẵn thư mục footage quay rồi mà chưa lên được video ưng ý, nhắn chữ **EDIT** kèm mục tiêu video cho mình để mình xem thử cấu trúc nhé.

---

### 🎬 VIDEO 03 — MÃ `C040`: TÔI DÙNG AI ĐỂ TÌM 10 GÓC VIDEO TỪ MỘT VẤN ĐỀ

#### 1. Thông tin định danh
- **Ngày đăng:** Thứ Năm, 29/10/2026 (Lịch bắt buộc)
- **Pillar / Tuyến nội dung:** `P3 — AI trong workflow editor` / `AI01 — Ideation & Research bằng AI`
- **Format:** Screen Record (Quay màn hình thao tác thật Input → Output → Lọc tay)
- **Tệp người xem:** Creator, marketer, người tự làm nội dung bị bí ý tưởng
- **Mục tiêu Funnel:** Nhận biết (Awareness)
- **Claim duy nhất:** AI chỉ ra được ý tưởng dùng được khi bạn nạp đúng 3 dữ kiện đầu vào (tệp người xem, nỗi đau thật, bằng chứng bạn quay được), sau đó chính con người phải lọc bỏ 70% góc sáo rỗng.
- **Bằng chứng cần chuẩn bị:** Màn hình gõ prompt thật (so sánh câu lệnh cụt lủn vs câu lệnh có cấu trúc 3 biến số) và cảnh Thành gạch bỏ 7 ý tưởng chung chung, giữ lại 3 góc quay được ngay.
- **CTA & Offer:** Nhận mẫu prompt & xem lộ trình học AI thực chiến tại mục **Zero To AI** ở bio.

#### 2. Bảng kịch bản chi tiết (39 giây)
| Timecode | Hình ảnh / Thao tác màn hình | Text trên màn hình | Lời thoại của Thành + Nhịp / SFX |
| :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **Screen Record Split:** Bên trái là câu lệnh *"Cho tôi 10 ý tưởng TikTok"* ra toàn kết quả chung chung; bên phải là bảng 10 góc chia sẵn theo format quay của Thành. | Đừng bảo AI **“cho 10 ý tưởng”** chung chung | Nếu bạn chỉ gõ vào AI câu *"cho tôi mười ý tưởng làm video"*, thứ bạn nhận lại sẽ là mười gạch đầu dòng đọc lên nghe rất quen nhưng không quay được. |
| `00:03 – 00:11` | **A-roll Thành + Highlight Prompt trên màn hình:** Thành chỉ vào 3 dòng biến số màu vàng trong khung prompt. | Prompt cần khóa **3 dữ kiện đầu vào**:<br>1. Tệp xem · 2. Nỗi đau · 3. Bằng chứng có sẵn | Khi dùng AI để tìm góc nội dung, mình luôn khóa trước ba dữ kiện: một là người xem cụ thể là ai, hai là lỗi họ đang gặp, và ba là trên máy mình đang có sẵn bằng chứng gì để show ra. |
| `00:11 – 00:22` | **Screen Record kết quả Output:** AI trả về 10 góc chia theo Before/After, Breakdown, Screen Record, Story. Thành dùng chuột tô đỏ gạch bỏ 7 góc lý thuyết, khoanh xanh 3 góc có timeline/footage. | **AI làm thô:** Đưa ra 10 góc tiếp cận<br>**Mình làm tinh:** Gạch bỏ 7 góc không có bằng chứng | *[SFX: Tiếng bút gạch]* Bạn nhìn kết quả trên màn hình nhé: AI trả ra mười góc trong mười giây. Nhưng bước quan trọng nhất nằm ở đây: mình gạch bỏ ngay bảy góc nói lý thuyết suông, chỉ giữ lại đúng ba góc mà mình mở timeline Premiere lên chứng minh được ngay. |
| `00:22 – 00:31` | **Cận cảnh bảng Backlog 3 góc được chọn:** Chuyển 3 góc đó sang cột Shot List gồm `C001`, `C002`, `C003`. | Từ 1 vấn đề → **3 kịch bản quay được ngay** | Nhờ cách lọc này, chỉ từ một vấn đề là *"ba giây đầu yếu"*, mình có ngay ba video khác nhau cho cả tuần mà không bị trùng lặp cách nói. |
| `00:31 – 00:39` | **A-roll Thành nói trực diện:** Hiện khung bio chỉ vào nhánh Zero To AI / Nhận Prompt. | Xem lộ trình **Zero To AI** & mẫu prompt ở bio | AI giúp bạn đi nhanh phần thô, nhưng người chọn góc phải là bạn. *[Nghỉ 0.5s]* Nếu bạn muốn lấy mẫu prompt này và học cách ứng dụng AI vào làm nội dung từ gốc, xem mục Zero To AI ở bio của mình nhé. |

#### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] `C040_AROLL_01.mp4`: Thành nói trực diện ống kính (Medium Close-up).
- [ ] `C040_SCREEN_BAD_PROMPT.mp4`: Màn hình gõ câu lệnh ngắn ngủn và kết quả AI trả về chung chung ("1. Chia sẻ mẹo hay, 2. Kể chuyện thành công...").
- [ ] `C040_SCREEN_GOOD_PROMPT.mp4`: Màn hình nhập prompt chuẩn 3 biến số của Thành và kết quả bảng 10 góc rõ format.
- [ ] `C040_SCREEN_FILTER.mp4`: Thao tác tô màu xanh 3 góc được chọn và xóa/gạch 7 góc không có bằng chứng hình ảnh.

#### 4. Bản phân phối đa kênh (`crosspost`)
- **Caption TikTok / Reels:**
  - **Text trên Thumbnail:** Tìm 10 góc video bằng AI (và cách lọc)
  - **Caption:** AI không thiếu ý tưởng, thứ nó thiếu là bối cảnh làm việc và bằng chứng thực tế của bạn. Đây là cách mình nạp 3 dữ kiện để lấy 10 góc rồi lọc lấy 3 bài quay được ngay. Mẫu prompt và lộ trình học AI bài bản có ở mục Zero To AI trên bio mình nhé. `#dungcochudich #aiworkflow #contentcreator #zerotoai`
- **Bài đăng Facebook cá nhân (170 chữ):**
  Nhiều bạn mới dùng AI làm nội dung hay rơi vào cảnh: bảo AI viết 10 ý tưởng thì thấy cái nào nghe cũng hợp lý, nhưng đến lúc bật máy quay lên lại không biết nói gì hay lấy hình ảnh ở đâu minh họa.
  Sau hơn 6 tháng đưa AI vào quy trình làm video hằng ngày, nguyên tắc của mình rất rõ: **AI làm thô phần liệt kê, còn mình chịu trách nhiệm lọc bằng chứng**.
  Mỗi khi cần khai thác 1 chủ đề, mình không hỏi câu chung chung mà ép AI chạy theo 3 ràng buộc trong prompt (mất khoảng 2 phút thiết lập đầu vào):
  1. Người xem đang ở giai đoạn nào (mới tự quay hay đang cần thuê dựng).
  2. Một lỗi sai cụ thể nhìn thấy được bằng mắt trên màn hình.
  3. Giới hạn chỉ đề xuất những góc có thể chứng minh bằng Timeline Premiere, bản so sánh A/B hoặc màn hình thao tác thật.
  Khi AI trả về 10 phương án, mình thẳng tay bỏ 7 góc mang tính lý thuyết, chỉ giữ 3 góc có sẵn tư liệu để bấm máy trong tuần.
  Bạn nào muốn tham khảo cấu trúc prompt này và lộ trình học AI từ số 0 cho công việc nội dung thì xem ở mục **Zero To AI** trên phần giới thiệu trang cá nhân của mình nhé.

---

### 🎬 VIDEO 04 — MÃ `C055`: TÔI HỌC MARKETING NHƯNG LẠI CHỌN NGHỀ EDITOR

#### 1. Thông tin định danh
- **Ngày đăng:** Thứ Bảy, 31/10/2026 (Lịch linh hoạt)
- **Pillar / Tuyến nội dung:** `P4 — Hành trình & Bằng chứng` / `JRN01 — Câu chuyện nghề & Định vị`
- **Format:** Story (Kể chuyện kết hợp B-roll mốc thật trong công việc)
- **Tệp người xem:** Tất cả (Creator, khách hàng tiềm năng, editor mới)
- **Mục tiêu Funnel:** Tin cậy (Trust)
- **Claim duy nhất:** Nền tảng marketing giúp một editor không bị cuốn vào hiệu ứng phô diễn, mà luôn đặt câu hỏi "video này giúp người xem hiểu và làm gì tiếp theo?" trước mỗi vết cắt.
- **Bằng chứng cần chuẩn bị:** B-roll thật của Thành: sổ tay/tài liệu thời học & làm marketing, màn hình Premiere/After Effects trong gần 1 năm đi làm và hơn 6 tháng tập trung edit + AI, bảng kế hoạch 90 ngày trên màn hình.
- **CTA & Offer:** Theo dõi hành trình 90 ngày "Dựng Có Chủ Đích" (Offer: **Không bán**).

#### 2. Bảng kịch bản chi tiết (38 giây)
| Timecode | Hình ảnh / Thao tác màn hình | Text trên màn hình | Lời thoại của Thành + Nhịp / SFX |
| :--- | :--- | :--- | :--- |
| `00:00 – 00:04` | **A-roll kết hợp B-roll bàn làm việc:** Một bên là sổ ghi chú chiến dịch Marketing / bảng Funnel, một bên là bàn phím + timeline Premiere Pro đang mở. | Học **Marketing** nhưng lại chọn làm **Video Editor** | Mình xuất phát từ ngành marketing, nhưng sau gần một năm đi làm thực tế, công việc mình chọn gắn bó mỗi ngày lại là dựng video. |
| `00:04 – 00:13` | **B-roll hồi tưởng công việc:** Cảnh Thành xem lại một bản kế hoạch nội dung dài trên Docs nhưng khi lên thành video thì bị rời rạc, người xem thoát sớm. | Nhiều bản kế hoạch rất hay trên giấy<br>Nhưng **gãy hoàn toàn** ở 3 giây đầu trên video | Lúc làm marketing, mình từng thấy rất nhiều ý tưởng viết trên giấy thì cực kỳ chặt chẽ. Nhưng khi chuyển thành video, chỉ vì ba giây đầu mở sai nhịp hoặc nhồi quá nhiều chữ mà người xem lướt qua sạch. |
| `00:13 – 00:24` | **B-roll quá trình luyện Edit & AI hơn 6 tháng qua:** Cảnh Thành thực hành cắt timeline Premiere, chỉnh keyframe trong After Effects và thử nghiệm workflow AI lúc tối muộn. | Hơn **6 tháng** tập trung rèn Premiere, AE & AI<br>Góc nhìn: **Mỗi vết cắt phải phục vụ thông điệp** | Đó là lý do hơn sáu tháng qua, mình dồn toàn bộ thời gian vào Premiere, After Effects và các công cụ AI. Mình chưa phải người dựng lâu năm nhất, nhưng nền tảng marketing cho mình một thói quen: luôn hỏi người xem nhận được gì trước khi chèn bất kỳ hiệu ứng nào. |
| `00:24 – 00:32` | **Screen Record:** Mở nhanh bảng `Lịch 90 ngày` và thư mục dự án `THUONG_HIEU_CA_NHAN_THANH_90_NGAY` trên máy tính. | Thử nghiệm **90 ngày** xây kênh công khai<br>**Dựng Có Chủ Đích** | Mình lập kênh này để ghi lại trọn vẹn chín mươi ngày thử nghiệm kết hợp ba thứ: tư duy marketing, kỹ năng dựng và AI ứng dụng thực tế. |
| `00:32 – 00:38` | **A-roll Thành nhìn thẳng ống kính:** Ánh sáng ấm, chân thành, không gồng. | Theo dõi hành trình **Dựng Có Chủ Đích** cùng mình | Mọi thứ mình học được, làm được và cả những ca phải sửa lại đều sẽ được cập nhật ở đây. *[Nghỉ 0.5s]* Theo dõi kênh để đồng hành cùng mình nhé. |

#### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] `C055_AROLL_01.mp4`: Thành kể chuyện trực diện, giọng điềm tĩnh, nhịp vừa phải.
- [ ] `C055_BROLL_MKT_NOTES.mp4`: Cận cảnh cuốn sổ ghi chú marketing / bảng kế hoạch nội dung & funnel đặt cạnh chuột máy tính.
- [ ] `C055_BROLL_EDITING_DESK.mp4`: Góc quay nghiêng (Over-the-shoulder) cảnh Thành đang thao tác cắt trên Premiere và chỉnh keyframe trên After Effects.
- [ ] `C055_SCREEN_90DAYS.mp4`: Quay màn hình bảng kế hoạch 90 ngày và cấu trúc thư mục làm việc thật của Thành.

#### 4. Bản phân phối đa kênh (`crosspost`)
- **Caption TikTok / Reels:**
  - **Text trên Thumbnail:** Học Marketing sao lại đi làm Editor?
  - **Caption:** Gần 1 năm đi làm và hơn 6 tháng ăn ngủ cùng timeline Premiere, After Effects và AI. Mình chọn nghề dựng vì muốn biến những ý tưởng marketing trên giấy thành video giữ được mắt người xem thật sự. Theo dõi hành trình 90 ngày Dựng Có Chủ Đích của mình nhé! `#dungcochudich #videoeditor #marketingmindset #buildinpublic`
- **Bài đăng Facebook cá nhân (175 chữ):**
  Có vài người bạn hỏi mình: *"Học Digital Marketing ra sao không làm plan hay chạy chiến dịch thuần túy, lại ngồi cắt từng giây video làm gì cho cực?"*
  Thật ra chính quãng thời gian làm marketing trong gần 1 năm qua lại là lý do đưa mình sang nghề Editor. Mình từng chứng kiến nhiều brief sản phẩm rất tốt, insight viết trên file chữ rất trúng, nhưng đến khâu ra video thành phẩm thì người xem rớt ngay từ giây thứ 3 — chỉ vì mở đầu lan man, cảnh hình không khớp lời nói và cuối bài không có lấy một hướng dẫn hành động rõ ràng.
  Hơn 6 tháng nay, mình tập trung rèn sâu kỹ năng dựng trên Premiere, học thêm After Effects và đưa AI vào làm phần thô. Mình không dám nhận là bậc thầy kỹ xảo, nhưng mình chọn theo đuổi một nguyên tắc rõ ràng: **Dựng Có Chủ Đích** — mỗi vết cắt, mỗi dòng chữ trên màn hình đều phải phục vụ mục tiêu giúp người xem hiểu nhanh và biết cần làm gì tiếp theo.
  Bắt đầu từ tuần này, mình khởi động chuỗi 90 ngày ghi lại toàn bộ các bài học, ca sửa video và thử nghiệm AI thực tế trên kênh. Rất vui nếu được kết nối và trao đổi cùng mọi người trên hành trình này.

---

## TUẦN 2: KIỂM CHỨNG TỆP KHÁN GIẢ & FORMAT (02/11/2026 – 07/11/2026)

---

### 🎬 VIDEO 05 — MÃ `C002`: MỘT HOOK YẾU VÀ BA CÁCH VIẾT LẠI

#### 1. Thông tin định danh
- **Ngày đăng:** Thứ Hai, 02/11/2026 (Lịch bắt buộc)
- **Pillar / Tuyến nội dung:** `P1 — Marketing trong video` / `MKT01 — Hook & 3 giây đầu`
- **Format:** Talking Head kết hợp Text Card trực quan trên màn hình
- **Tệp người xem:** Creator, người tự viết kịch bản video ngắn
- **Mục tiêu Funnel:** Nhận biết (Awareness)
- **Claim duy nhất:** Một câu mở đầu báo cáo chủ đề luôn yếu; chỉ cần chuyển nó sang 1 trong 3 góc (Kết quả nhìn thấy, Lỗi sai đang mắc, hoặc Con số đối lập) là giữ chân người xem tốt hơn ngay lập tức.
- **Bằng chứng cần chuẩn bị:** 1 câu hook gốc yếu (*"Hôm nay mình sẽ hướng dẫn cách chỉnh màu video"*) và 3 bản viết lại hiển thị kèm ví dụ hình ảnh thực tế trên màn hình.
- **CTA & Offer:** Bình luận câu mở đầu video sắp tới của bạn để cùng gọt lại (Offer: **Không bán**).

#### 2. Bảng kịch bản chi tiết (37 giây)
| Timecode | Hình ảnh / Thao tác màn hình | Text trên màn hình | Lời thoại của Thành + Nhịp / SFX |
| :--- | :--- | :--- | :--- |
| `00:00 – 00:04` | **A-roll Thành + Text Card đỏ trên đầu:** Hiển thị câu hook yếu bị gạch chéo: ~~"Hôm nay mình hướng dẫn cách quay video tại nhà"~~. | Đừng mở đầu bằng câu<br>**“Hôm nay mình chia sẻ...”** | Câu mở đầu *"Hôm nay mình sẽ chia sẻ cách quay video tại nhà"* không sai, nhưng nó giống như một dòng thông báo khiến người xem lướt qua ngay. |
| `00:04 – 00:13` | **Card 1 trượt vào + B-roll minh họa:** So sánh góc phòng tối và góc phòng đã bật 1 đèn. | **Cách 1: Mở bằng Kết quả cụ thể**<br>“Biến góc bàn tối thành khung hình sạch chỉ với 1 cây đèn” | Cùng chủ đề đó, đây là ba cách mình viết lại để giữ người xem ở lại. *[SFX: Pop]* Cách một — mở bằng kết quả nhìn thấy được: *"Biến góc bàn làm việc tối thành khung hình sạch chỉ với một cây đèn bàn."* |
| `00:13 – 00:22` | **Card 2 trượt vào + Khoanh đỏ lỗi bóng đổ trên mặt:** Chỉ thẳng vào lỗi người mới hay gặp. | **Cách 2: Mở bằng Lỗi sai quen thuộc**<br>“Đặt đèn trước mặt nhưng da vẫn bị xỉn màu là vì lỗi này” | *[SFX: Pop]* Cách hai — đánh thẳng vào lỗi sai người xem đang gặp: *"Đặt đèn ngay trước mặt nhưng lên hình da vẫn bị bệt và bóng đổ là vì bạn quên tắt đèn trần."* |
| `00:22 – 00:31` | **Card 3 trượt vào + Split-screen con số đối lập:** Bên trái bộ đèn đắt tiền, bên phải 1 đèn nhỏ + cửa sổ. | **Cách 3: Mở bằng Con số / Đối lập**<br>“Góc quay 500 nghìn này giữ mắt tốt hơn bộ đèn 5 triệu đặt sai chỗ” | *[SFX: Pop]* Và cách ba — tạo sự đối lập bằng con số cụ thể: *"Góc quay năm trăm nghìn này lên hình có chiều sâu hơn cả bộ đèn năm triệu đặt sai góc."* |
| `00:31 – 00:37` | **A-roll Thành:** Hiện tóm tắt 3 công thức (Kết quả / Lỗi sai / Đối lập) trên màn hình. | Bạn đang chuẩn bị quay chủ đề gì?<br>**Để lại câu mở đầu ở bình luận nhé** | Trước khi bấm máy, bạn hãy viết ra đủ ba phương án này rồi chọn câu gãy gọn nhất. *[Nghỉ 0.5s]* Bạn đang định quay chủ đề gì tuần này, để lại câu mở đầu dưới bình luận mình cùng góp ý nhé. |

#### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] `C002_AROLL_01.mp4`: Thành nói trực diện, tay chỉ nhẹ lên vùng hiển thị Text Card ở góc trên/giữa khung hình.
- [ ] `C002_BROLL_LIGHT_BA.mp4`: Cảnh ngắn 3 giây tắt/bật đèn bàn làm việc tạo độ tương phản trước/sau.
- [ ] `C002_GRAPHIC_CARDS.prproj`: 3 thẻ chữ thiết kế gọn trên Premiere/AE (nền tối mờ, chữ trắng kem `#F6F1E8`, nhấn xanh `#1A73E8`).

#### 4. Bản phân phối đa kênh (`crosspost`)
- **Caption TikTok / Reels:**
  - **Text trên Thumbnail:** 1 Hook yếu & 3 cách viết lại
  - **Caption:** Thay vì mở bài bằng câu thông báo chủ đề, hãy đổi sang 1 trong 3 góc: Kết quả cụ thể, Lỗi sai quen thuộc hoặc Con số đối lập. Bạn đang viết kịch bản chủ đề gì, bình luận câu đầu tiên xuống dưới mình cùng sửa nhé! `#dungcochudich #vietkichban #hook3giay #marketingvideo`
- **Bài đăng Facebook cá nhân (150 chữ):**
  Lúc kiểm tra kịch bản trước ngày bấm máy, mình có một quy tắc nhỏ: nếu câu đầu tiên bắt đầu bằng cụm *"Hôm nay mình sẽ nói về..."* hoặc *"Video này dành cho những ai..."* thì bắt buộc phải viết lại.
  Lý do là người xem trên mạng xã hội không đi tìm một "bài thuyết trình". Họ dừng lại khi thấy kết quả họ đang muốn, hoặc thấy đúng cái lỗi đang làm họ bực mình.
  Thay vì vắt óc nghĩ từ ngữ hoa mỹ, mình luôn đặt câu mở đầu vào 3 khuôn cố định (mất đúng 3 phút để viết nháp cả 3 câu rồi chọn 1):
  1. **Theo Kết quả:** [Kết quả mong muốn] + trong [Thời gian/Điều kiện giới hạn].
  2. **Theo Lỗi sai:** Bạn đang làm [Hành động quen thuộc] nhưng vẫn bị [Kết quả tệ] là vì điểm này.
  3. **Theo Sự đối lập:** Tại sao [Cách đơn giản/ít tốn kém] lại hiệu quả hơn [Cách phức tạp nhiều người lầm tưởng].
  Khi đã có 3 câu này trên giấy, việc chọn cảnh B-roll mở màn trên timeline cũng dễ hơn rất nhiều vì mỗi câu đều đã gợi ý sẵn hình ảnh cần đưa lên 3 giây đầu.

---

### 🎬 VIDEO 06 — MÃ `C003`: ĐỪNG MỞ VIDEO BẰNG CÂU XIN CHÀO

#### 1. Thông tin định danh
- **Ngày đăng:** Thứ Ba, 03/11/2026 (Lịch bắt buộc)
- **Pillar / Tuyến nội dung:** `P1 — Marketing trong video` / `MKT01 — Hook & 3 giây đầu`
- **Format:** Breakdown (Mổ xẻ 2 phiên bản video của chủ shop/thương hiệu cá nhân)
- **Tệp người xem:** Chủ shop, người bán hàng hoặc làm dịch vụ qua video ngắn
- **Mục tiêu Funnel:** Nhận biết (Awareness)
- **Claim duy nhất:** Với video giới thiệu sản phẩm/dịch vụ của chủ shop, thay câu "Xin chào mọi người, shop em mới về..." bằng cảnh giải quyết trực tiếp vấn đề của khách sẽ giữ chân đúng người có nhu cầu mua.
- **Bằng chứng cần chuẩn bị:** Hai phiên bản dựng từ cùng một tình huống bán hàng (ví dụ: giới thiệu balo chống nước / bàn làm việc / dịch vụ): Bản 1 mở đầu chào hỏi giới thiệu tên shop; Bản 2 mở đầu dội nước/thử nghiệm trực tiếp kết quả.
- **CTA & Offer:** Lưu video này lại để làm mẫu mở bài cho clip bán hàng tiếp theo (Offer: **Không bán**).

#### 2. Bảng kịch bản chi tiết (36 giây)
| Timecode | Hình ảnh / Thao tác màn hình | Text trên màn hình | Lời thoại của Thành + Nhịp / SFX |
| :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **So sánh 2 khung hình đầu tiên:** Bản A đứng trước kệ hàng vẫy tay chào; Bản B cận cảnh đổ nước lên bề mặt vải balo mà bên trong giấy vẫn khô nguyên. | Đừng mở video bán hàng bằng câu **“Xin chào”** | Nếu bạn là chủ shop tự quay video, câu *"Xin chào mọi người, hôm nay bên mình mới về..."* chính là điểm làm rớt khách nhanh nhất. |
| `00:03 – 00:12` | **Breakdown Bản A trên Timeline:** Hiển thị thanh thời gian chạy từ `00:00` đến `00:05` mới bắt đầu chạm vào sản phẩm. Biểu đồ giữ chân (Retention minh họa) tụt dốc ở giây thứ 2. | **5 giây đầu chỉ để chào hỏi**<br>Khách hàng chưa thấy lợi ích của họ | Nhìn vào timeline bản thứ nhất này nhé: mất đúng năm giây đầu chỉ để chào hỏi và đọc tên mã hàng. Lúc này khách hàng chưa thấy sản phẩm giải quyết được việc gì cho họ. |
| `00:12 – 00:23` | **Breakdown Bản B trên Timeline:** Cắt thẳng vào cảnh thử nghiệm thực tế ở giây `00:00` + Câu thoại đánh vào tình huống sử dụng thật của khách. | **Đưa cảnh kiểm chứng lên giây `00:00`**<br>Nói ngay tình huống khách đang cần | *[SFX: Whoosh]* Bây giờ nhìn sang bản thứ hai: mình bỏ hoàn toàn phần chào hỏi. Giây đầu tiên là cảnh kiểm chứng khả năng chống nước ngay lập tức, đi kèm câu nói: *"Đi mưa bất chợt mà laptop mười lăm inch bên trong vẫn khô nguyên."* |
| `00:23 – 00:31` | **A-roll Thành + Công thức 2 bước trên màn hình:** Chỉ rõ cấu trúc thay thế câu chào cho chủ shop. | **Công thức mở đầu cho chủ shop:**<br>Cảnh sử dụng thật + Kết quả khách nhận được | Khi khách đã dừng lại xem vì kết quả ở ba giây đầu, lúc đó bạn mới giới thiệu chi tiết chất liệu hay giá bán ở phần thân bài. |
| `00:31 – 00:36` | **A-roll Thành:** Chốt ngắn gọn, hiện nút Lưu video. | **Lưu video** để áp dụng cho lần quay tới | Đổi câu xin chào bằng cảnh kết quả thực tế — đó là cách mình dựng có chủ đích. *[Nghỉ 0.5s]* Bạn lưu lại cấu trúc này để thử ngay ở video bán hàng tiếp theo nhé. |

#### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] `C003_AROLL_01.mp4`: Thành nói trực diện, phân tích rõ ràng, nhịp dứt khoát.
- [ ] `C003_BROLL_SHOP_A.mp4`: Cảnh mẫu mở đầu kiểu truyền thống (đứng cầm sản phẩm chào hỏi 4–5 giây).
- [ ] `C003_BROLL_SHOP_B.mp4`: Cảnh mẫu cận cảnh test công năng sản phẩm ngay giây đầu tiên.
- [ ] `C003_SCREEN_TIMELINE.mp4`: Màn hình Premiere đặt 2 bản A và B song song để thấy độ chênh lệch 5 giây đầu.

#### 4. Bản phân phối đa kênh (`crosspost`)
- **Caption TikTok / Reels:**
  - **Text trên Thumbnail:** Đừng mở video bằng câu "Xin chào"
  - **Caption:** Khách hàng lướt feed không dừng lại vì lời chào của shop, họ dừng lại khi thấy món đồ đó giải quyết đúng vấn đề họ đang gặp. Lưu lại công thức mở bài bằng kết quả thực tế này cho lần bấm máy tới nhé! `#dungcochudich #videobanhang #marketingvideo #chushop`
- **Bài đăng Facebook cá nhân (160 chữ):**
  Mỗi lần xem kênh của các anh chị chủ shop mới tự làm video, mình thấy một thói quen rất lịch sự ngoài đời nhưng lại gây bất lợi khi lên video ngắn: đó là luôn mở đầu bằng câu *"Xin chào mọi người, hôm nay shop em xin giới thiệu..."*.
  Ngoài cửa hàng, khách bước vào thì mình chào. Nhưng trên TikTok hay Reels, khách đang lướt qua hàng trăm video mỗi phút. Nếu 4 giây đầu chỉ là lời chào và tên mã sản phẩm, họ sẽ lướt tiếp trước khi kịp biết sản phẩm của bạn tốt ở điểm nào.
  Cách sửa không đòi hỏi bạn phải diễn xuất cầu kỳ hơn, mà chỉ cần đổi điểm bắt đầu khi bấm máy (hoặc khi cắt trên timeline):
  1. Thay vì đứng cầm sản phẩm chào, hãy mở bằng **cảnh sản phẩm đang giải quyết 1 tình huống thật** (ví dụ: gập gọn trong 2 giây, chống thấm nước, mặc lên người che khuyết điểm).
  2. Thay câu giới thiệu tên shop bằng **1 câu mô tả kết quả khách nhận được**.
  3. Đẩy toàn bộ thông tin kích thước, chất liệu và lời mời nhắn tin xuống sau giây thứ 10 — khi người thực sự quan tâm đã dừng lại xem.

---

### 🎬 VIDEO 07 — MÃ `C023`: TÔI SỬA NHỊP VIDEO NÀY TRONG 15 PHÚT

#### 1. Thông tin định danh
- **Ngày đăng:** Thứ Năm, 05/11/2026 (Lịch bắt buộc)
- **Pillar / Tuyến nội dung:** `P2 — Edit & Storytelling` / `EDIT01 — Tư duy cắt dựng & nhịp độ`
- **Format:** BTS (Behind The Scenes — Time-lapse quá trình sửa timeline thật trong 15 phút)
- **Tệp người xem:** Khách hàng tiềm năng (Cần người dựng video gọn, rõ thông điệp, đúng hạn)
- **Mục tiêu Funnel:** Tin cậy (Trust)
- **Claim duy nhất:** Một bản dựng bị lê thê không cần làm lại từ đầu; chỉ cần 15 phút xử lý 3 điểm (cắt khoảng thở chết, đảo câu đắt giá lên đầu, đặt điểm rơi âm thanh đúng chỗ chuyển ý) là video lột xác.
- **Bằng chứng cần chuẩn bị:** Quay màn hình + góc máy phụ cảnh Thành sửa 1 timeline thật từ bản Rough Cut dài 52 giây xuống bản Final Cut gọn 34 giây, kèm đồng hồ bấm giờ 15 phút.
- **CTA & Offer:** Nhắn chữ **"EDIT"** nếu bạn muốn mình tối ưu lại nhịp và thông điệp cho video của bạn (Offer: **Dịch vụ Edit/Media**).

#### 2. Bảng kịch bản chi tiết (39 giây)
| Timecode | Hình ảnh / Thao tác màn hình | Text trên màn hình | Lời thoại của Thành + Nhịp / SFX |
| :--- | :--- | :--- | :--- |
| `00:00 – 00:04` | **Screen Record + Góc máy cạnh bàn:** Timeline bản thô dài 52 giây nhiều khoảng trống trên thanh Audio, gọt xuống còn 34 giây khít chặt. | Sửa nhịp video từ **52 giây xuống 34 giây**<br>Trong đúng 15 phút | Bản dựng thô này dài năm mươi hai giây và nghe khá đều đều. Đây là ba bước mình làm trong mười lăm phút để rút gọn xuống ba mươi tư giây mà thông điệp sắc hơn hẳn. |
| `00:04 – 00:13` | **Bước 1 (Phóng to Waveform âm thanh):** Cảnh Thành cắt sát vào đầu và cuối mỗi câu nói, dùng J-cut nhẹ để câu sau gối lên đuôi câu trước 2–3 frame. | **Phút 01–05:** Cắt khoảng lặng thừa & nối J-cut nhẹ | Năm phút đầu tiên: mình nhìn vào sóng âm thanh, cắt bỏ toàn bộ những khoảng nghỉ lấy hơi quá dài và các từ đệm *"à, ừm, thì là"*. Chỗ nào chuyển ý nhanh, mình kéo tiếng câu sau vào trước hình hai frame để mạch nói tự nhiên. |
| `00:13 – 00:22` | **Bước 2 (Screen Record Timeline):** Đánh dấu Marker màu xanh vào 3 từ khóa quan trọng nhất và đắp đúng 3 cảnh B-roll cận cảnh lên trên. | **Phút 05–10:** Chỉ chèn B-roll vào **đúng từ khóa cần chứng minh** | Năm phút tiếp theo: thay vì phủ B-roll kín mít cho đỡ trống, mình chỉ đặt hình minh họa vào đúng ba chỗ người nói đưa ra con số hoặc bằng chứng. Nhờ vậy người xem biết khi nào cần nhìn mặt người nói, khi nào cần nhìn chi tiết. |
| `00:22 – 00:32` | **Bước 3 (Audio Track):** Tắt bớt SFX thừa, chỉ giữ 1 tiếng nhấn và ngắt nhạc nền (Music drop) 1 giây ngay trước câu kết luận quan trọng nhất. | **Phút 10–15:** Ngắt nhạc nền 1 giây trước câu chốt | *[Nhạc nền ngắt đột ngột 1s rồi vào lại]* Năm phút cuối: mình gỡ bớt hiệu ứng âm thanh vụn vặt, và chủ động ngắt nhạc nền đúng một giây ngay trước câu kết luận chính để kéo lại sự tập trung. |
| `00:32 – 00:39` | **A-roll Thành + Chạy 3s bản Final mượt mà ở góc:** Hiện lời mời nhắn chữ EDIT. | Cần dựng video gọn nhịp & rõ ý?<br>Nhắn chữ **EDIT** cho mình | Cắt bớt thứ gây xao nhãng chính là cách làm nổi bật thông điệp. *[Nghỉ 0.5s]* Nếu bạn cần người đồng hành dựng video theo hướng gọn và rõ mục tiêu như thế này, nhắn chữ "EDIT" cho mình nhé. |

#### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] `C023_AROLL_01.mp4`: Thành nói trực diện phần mở và kết (Medium Close-up).
- [ ] `C023_BROLL_TIMELAPSE.mp4`: Góc máy đặt chéo sau lưng Thành (thấy màn hình Premiere và tay thao tác phím tắt + chuột trong 15 phút).
- [ ] `C023_SCREEN_WAVEFORM.mp4`: Quay màn hình cận cảnh thanh Waveform trước khi cắt (nhiều khoảng trống) và sau khi cắt gọn + J-cut.
- [ ] `C023_SCREEN_MUSICDROP.mp4`: Quay màn hình đoạn cắt nhạc nền (Audio track A2/A3) dừng 1 giây trước câu chốt.

#### 4. Bản phân phối đa kênh (`crosspost`)
- **Caption TikTok / Reels:**
  - **Text trên Thumbnail:** Sửa nhịp video trong 15 phút
  - **Caption:** Cắt bỏ 18 giây thừa để giữ lại 34 giây đắt giá nhất. Đôi khi một video tốt hơn không phải nhờ thêm hiệu ứng, mà nhờ biết gọt đi khoảng trống và đặt điểm lặng đúng chỗ. Nhắn "EDIT" nếu bạn cần dựng video cho kênh hoặc sản phẩm nhé! `#dungcochudich #videoeditor #premierepro #dichvuedit`
- **Bài đăng Facebook cá nhân (170 chữ):**
  Hôm qua mình ngồi sửa lại một bản dựng thô dài 52 giây. Nội dung gốc người nói chia sẻ rất thực tế, nhưng khi xem liền mạch từ đầu đến cuối lại có cảm giác hơi mệt và dễ mất tập trung ở khoảng giây thứ 15.
  Thay vì chèn thêm hiệu ứng chữ bay nhảy hay chuyển cảnh giật lắc để "cứu" nhịp, mình bấm đồng hồ 15 phút và chỉ can thiệp vào 3 chỗ trên timeline:
  1. **Gọt sóng âm (5 phút đầu):** Cắt bỏ toàn bộ khoảng lấy hơi thừa và từ đệm, rút ngắn thời lượng từ 52 giây xuống còn 34 giây mà không mất một ý chính nào.
  2. **Đặt B-roll có chọn lọc (5 phút giữa):** Chỉ đắp hình ảnh cận cảnh vào đúng 3 thời điểm người nói nêu bằng chứng cụ thể, còn lại giữ khung hình nói trực diện để tạo kết nối.
  3. **Tạo khoảng lặng âm thanh (5 phút cuối):** Chủ động ngắt nhạc nền 1 giây ngay trước câu kết luận quan trọng nhất — hiệu quả giữ sự chú ý cao hơn nhiều so với việc nhồi sound effect liên tục.
  Anh chị hoặc bạn nào đang cần dựng video xây kênh / giới thiệu dịch vụ theo phong cách gọn gàng, rõ trọng tâm như vậy thì nhắn chữ **EDIT** cho mình nhé.

---

### 🎬 VIDEO 08 — MÃ `C041`: CHATGPT, CLAUDE VÀ GEMINI: TÔI GIAO VIỆC GÌ CHO TỪNG CÔNG CỤ?

#### 1. Thông tin định danh
- **Ngày đăng:** Thứ Bảy, 07/11/2026 (Lịch linh hoạt)
- **Pillar / Tuyến nội dung:** `P3 — AI trong workflow editor` / `AI01 — Ideation & Research bằng AI`
- **Format:** Comparison (So sánh trên cùng một bài toán sản xuất video thực tế)
- **Tệp người xem:** Người học AI, creator, marketer muốn dùng AI thực tế thay vì sưu tầm công cụ
- **Mục tiêu Funnel:** Cân nhắc (Consideration)
- **Claim duy nhất:** Thay vì hỏi công cụ nào mạnh nhất, người làm nội dung nên chia việc theo đúng sở trường: Gemini để tra cứu nhanh và xử lý dữ liệu dài, ChatGPT để cấu trúc bảng biểu/shot list, và Claude để gọt lại lời thoại tiếng Việt tự nhiên.
- **Bằng chứng cần chuẩn bị:** Cùng 1 brief làm video 30 giây, mở 3 tab trên màn hình cho thấy rõ từng bước bàn giao giữa Gemini → ChatGPT → Claude (và phần Thành tự sửa câu cuối).
- **CTA & Offer:** Xem lộ trình học AI thực chiến từ gốc tại mục **Zero To AI** ở bio.

#### 2. Bảng kịch bản chi tiết (40 giây)
| Timecode | Hình ảnh / Thao tác màn hình | Text trên màn hình | Lời thoại của Thành + Nhịp / SFX |
| :--- | :--- | :--- | :--- |
| `00:00 – 00:04` | **A-roll Thành + Màn hình chia 3 cửa sổ (ChatGPT, Claude, Gemini):** Cùng một đề bài làm video 30 giây. | **ChatGPT · Claude · Gemini**<br>Mình giao việc gì cho từng công cụ? | Cùng một đề bài sản xuất video ngắn, mình không bắt một công cụ AI làm từ đầu đến cuối, mà chia thành ba chặng rõ ràng. |
| `00:04 – 00:13` | **Screen Record Tab 1 — Gemini:** Dán tài liệu thông tin sản phẩm dài + yêu cầu lọc ra 3 nỗi đau thực tế và kiểm chứng thông tin. | **1. Gemini:** Tổng hợp tài liệu dài & tìm dữ kiện nhanh | *[SFX: Click]* Chặng một — khi cần đọc nhanh một tài liệu sản phẩm dài hoặc tổng hợp các câu hỏi phổ biến của khách hàng, mình giao cho Gemini vì nó xử lý ngữ cảnh dài và tra cứu thông tin rất nhanh. |
| `00:13 – 00:22` | **Screen Record Tab 2 — ChatGPT:** Chuyển ý chính sang bảng chia cột (Timecode, Góc quay A-roll/B-roll, On-screen text). | **2. ChatGPT:** Đóng khung cấu trúc & lập bảng Shot List | *[SFX: Click]* Chặng hai — khi đã chốt được một ý chính, mình đưa sang ChatGPT để chia thành bảng phân cảnh có cột thời gian, góc máy và checklist chuẩn bị trước khi quay. |
| `00:22 – 00:32` | **Screen Record Tab 3 — Claude + Chỉnh tay của Thành:** Claude viết lời thoại câu ngắn, sau đó Thành tự tay sửa lại 2 cụm từ cho đúng khẩu ngữ của mình. | **3. Claude:** Viết nháp lời thoại tự nhiên<br>**+ Editor chỉnh tinh:** Sửa theo đúng giọng nói thật | *[SFX: Click]* Chặng ba — phần viết nháp lời thoại nói chuyện, mình ưu tiên Claude vì câu chữ tiếng Việt của nó đỡ mùi văn mẫu hơn. Sau đó mình vẫn tự đọc to lên và sửa lại mười lăm phần trăm câu chữ cho khớp nhịp thở của mình. |
| `00:32 – 00:40` | **A-roll Thành:** Hiển thị sơ đồ 3 bước gọn gàng + chỉ dẫn vào link bio Zero To AI. | Học cách phối hợp AI bài bản tại **Zero To AI** ở bio | Hiểu đúng điểm mạnh của từng công cụ giúp bạn tiết kiệm hàng giờ thử sai. *[Nghỉ 0.5s]* Nếu bạn muốn học cách ứng dụng AI vào công việc theo lộ trình bài bản từ gốc, xem mục Zero To AI ở bio của mình nhé. |

#### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] `C041_AROLL_01.mp4`: Thành nói trực diện ống kính (Medium Close-up).
- [ ] `C041_SCREEN_GEMINI.mp4`: Quay màn hình Gemini tóm tắt tài liệu brief dài thành 3 điểm cốt lõi.
- [ ] `C041_SCREEN_CHATGPT.mp4`: Quay màn hình ChatGPT xuất bảng Shot List chia cột rõ ràng.
- [ ] `C041_SCREEN_CLAUDE.mp4`: Quay màn hình Claude viết lời thoại ngắn và cảnh Thành gõ sửa trực tiếp câu chữ.

#### 4. Bản phân phối đa kênh (`crosspost`)
- **Caption TikTok / Reels:**
  - **Text trên Thumbnail:** Chia việc cho ChatGPT, Claude & Gemini
  - **Caption:** Đừng hỏi công cụ AI nào giỏi nhất, hãy hỏi khâu nào trong quy trình của bạn cần loại trợ lý nào. Đây là cách mình chia việc cho bộ ba này khi làm kịch bản và shot list mỗi tuần. Xem lộ trình học AI thực chiến tại mục Zero To AI ở bio nhé! `#dungcochudich #aiworkflow #chatgpt #claude #gemini`
- **Bài đăng Facebook cá nhân (175 chữ):**
  Mỗi tuần mình đều nhận được câu hỏi từ mấy bạn mới tìm hiểu AI: *"Giờ nên dùng ChatGPT, Claude hay Gemini để viết kịch bản video cho chuẩn?"*
  Nếu giao cả quy trình từ tìm ý tưởng, lập bảng cảnh quay đến viết lời thoại cho duy nhất một công cụ, bạn sẽ thấy chỗ thì nó làm rất tốt, chỗ thì câu chữ nghe cực kỳ cứng nhắc.
  Trong quy trình chuẩn bị 4 video mỗi tuần của mình, mình coi 3 công cụ này như 3 vị trí khác nhau trong bàn làm việc:
  1. **Gemini (Khâu nghiên cứu đầu vào):** Dùng khi cần đọc lướt tài liệu dài, tóm tắt thông tin sản phẩm và lọc ra những câu hỏi thực tế của người dùng.
  2. **ChatGPT (Khâu đóng khung hệ thống):** Dùng để chuyển ý tưởng đã chọn thành bảng Shot List có cột thời gian, góc máy A-roll/B-roll và danh sách file cần quay.
  3. **Claude (Khâu nháp lời thoại):** Dùng để viết lời nói thành câu ngắn, tự nhiên hơn bằng tiếng Việt (tất nhiên bước cuối cùng mình vẫn phải tự đọc thành tiếng để gọt lại từ ngữ cho đúng giọng thật của mình).
  Bạn nào mới bắt đầu muốn học cách dùng AI có hệ thống thay vì mò mẫm từng mẹo rời rạc thì có thể xem qua lộ trình **Zero To AI** mình để ở phần giới thiệu trang cá nhân nhé.

---

## TUẦN 3: KHÓA SPRINT 1 & CHỌN FORMAT THẮNG (09/11/2026 – 14/11/2026)

---

### 🎬 VIDEO 09 — MÃ `C004`: CÁCH ĐẶT KẾT QUẢ LÊN TRƯỚC QUY TRÌNH

#### 1. Thông tin định danh
- **Ngày đăng:** Thứ Hai, 09/11/2026 (Lịch bắt buộc)
- **Pillar / Tuyến nội dung:** `P1 — Marketing trong video` / `MKT01 — Hook & 3 giây đầu`
- **Format:** Screen Record (Show Final Cut trước rồi mới mổ xẻ Timeline quy trình)
- **Tệp người xem:** Creator, editor, người làm video hướng dẫn (tutorial) hoặc hậu trường (BTS)
- **Mục tiêu Funnel:** Nhận biết (Awareness)
- **Claim duy nhất:** Khi làm video hướng dẫn hoặc hậu trường, người xem chỉ chịu ngồi nghe quy trình 3 bước của bạn sau khi họ đã nhìn thấy thành quả cuối cùng ngay ở 3 giây đầu.
- **Bằng chứng cần chuẩn bị:** Timeline thật của một video tutorial/BTS trên Premiere Pro: cho xem cảnh kéo 2.5 giây thành phẩm cuối cùng đặt làm đoạn mở màn (`00:00 – 00:03`).
- **CTA & Offer:** Theo dõi series mổ xẻ cấu trúc video có chủ đích trên kênh (Offer: **Không bán**).

#### 2. Bảng kịch bản chi tiết (36 giây)
| Timecode | Hình ảnh / Thao tác màn hình | Text trên màn hình | Lời thoại của Thành + Nhịp / SFX |
| :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **Chạy ngay 2.5 giây thành phẩm Motion/Edit hoàn chỉnh sắc nét**, sau đó zoom ngược ra ngoài thấy toàn bộ giao diện Timeline Premiere Pro. | Cho xem **kết quả cuối cùng**<br>Trước khi nói về quy trình | Bạn vừa nhìn thấy thành phẩm hoàn chỉnh trước, rồi mới thấy timeline làm việc của mình. Đó chính là nguyên tắc: đặt kết quả lên trước quy trình. |
| `00:03 – 00:12` | **Screen Record lỗi thường gặp:** Một video hướng dẫn mở màn bằng cảnh mở phần mềm, tạo New Project, chỉnh thông số Sequence mất 6 giây đầu. | Lỗi hay gặp: Mở bài bằng **Bước 1, Bước 2...**<br>Khi người xem chưa biết kết quả ra sao | Rất nhiều bạn làm video chia sẻ chuyên môn hay bắt đầu theo kiểu: *"Bước một các bạn mở phần mềm lên, bước hai tạo file mới..."*. Khi người xem chưa thấy cái đích cuối cùng đẹp hay hữu ích thế nào, họ sẽ không kiên nhẫn xem bạn thao tác. |
| `00:12 – 00:23` | **Screen Record thao tác của Thành:** Dùng phím `Alt + Kéo chuột` (nhân bản clip Final ở cuối timeline) đưa lên giây `00:00`, chèn 1 câu khẳng định thời gian/độ khó. | **Thao tác trên timeline:**<br>Nhân bản 2 giây Final Cut → Đặt vào `00:00` | *[SFX: Click + Whoosh]* Trên timeline, cách xử lý của mình luôn là dựng xong toàn bộ quy trình trước. Sau đó mình cắt lấy đúng hai giây thành quả rõ nhất ở cuối bài, nhân bản và đặt thẳng lên vị trí mở đầu. |
| `00:23 – 00:30` | **Sơ đồ cấu trúc 3 nhịp trên màn hình:** `[0-3s: Thành quả] → [3-28s: 3 bước thực hiện] → [28-35s: Xem lại kết quả & Chốt]`. | **Cấu trúc giữ chân cho video quy trình:**<br>Thành quả → 3 bước chính → Kết luận | Chỉ cần hai giây đó đủ thuyết phục, toàn bộ phần giải thích ba bước phía sau của bạn sẽ được người xem theo dõi kỹ hơn rất nhiều. |
| `00:30 – 00:36` | **A-roll Thành nói trực diện:** Khung hình gọn, hiện lời mời theo dõi kênh. | **Theo dõi kênh** để xem tiếp series cấu trúc video | Cho người xem thấy đích đến trước khi rủ họ đi cùng quy trình — đó là cách mình dựng có chủ đích. *[Nghỉ 0.5s]* Theo dõi kênh để xem tiếp các bài mổ xẻ cấu trúc video nhé. |

#### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] `C004_AROLL_01.mp4`: Thành nói trực diện đoạn giải thích và câu kết.
- [ ] `C004_SCREEN_ZOOMOUT.mp4`: Cảnh chạy full-screen đoạn video thành phẩm 2.5 giây rồi thu nhỏ về cửa sổ Program Monitor trong Premiere Pro.
- [ ] `C004_SCREEN_ALTDRAG.mp4`: Quay màn hình thao tác giữ phím `Alt` kéo nhân bản đoạn clip kết quả từ cuối timeline về giây `00:00`.

#### 4. Bản phân phối đa kênh (`crosspost`)
- **Caption TikTok / Reels:**
  - **Text trên Thumbnail:** Đặt kết quả lên trước quy trình
  - **Caption:** Đừng bắt người xem nhìn cảnh bạn mở phần mềm ở 3 giây đầu tiên. Hãy cho họ thấy thành quả cuối cùng trước, rồi mới giải thích cách bạn làm ra nó. Theo dõi kênh để xem tiếp series dựng video có chủ đích nhé! `#dungcochudich #videoediting #contentstructure #marketingvideo`
- **Bài đăng Facebook cá nhân (150 chữ):**
  Khi làm các video chia sẻ quy trình làm nghề, hậu trường sản xuất hoặc hướng dẫn kỹ thuật, cái bẫy dễ mắc nhất là kể đúng theo trình tự mình làm: bước 1 chuẩn bị gì, bước 2 bấm vào đâu, bước 3 chỉnh thông số nào, và mãi đến giây cuối cùng mới cho xem kết quả.
  Vấn đề là người xem trên mạng xã hội chỉ quyết định bỏ ra 30 giây nghe quy trình khi họ biết chắc kết quả cuối cùng đáng để học hoặc đáng để thuê.
  Vì vậy, thao tác cuối cùng của mình trước khi xuất bất kỳ video hướng dẫn hay hậu trường nào trên Premiere luôn là:
  1. Chọn 2–3 giây thành phẩm hoàn chỉnh, rõ nét nhất ở cuối timeline.
  2. Nhân bản đoạn đó và kéo thẳng về vị trí `00:00 – 00:03`.
  3. Lồng 1 câu nói ngắn gọn nêu rõ kết quả đạt được và điều kiện thực hiện (ví dụ: *"Chỉ mất 3 bước để làm sạch đoạn âm thanh bị vang này"*), rồi mới đi vào chi tiết từng bước.

---

### 🎬 VIDEO 10 — MÃ `C024`: CHỈ THAY THỨ TỰ SHOT, CẢM XÚC ĐÃ KHÁC

#### 1. Thông tin định danh
- **Ngày đăng:** Thứ Ba, 10/11/2026 (Lịch bắt buộc)
- **Pillar / Tuyến nội dung:** `P2 — Edit & Storytelling` / `EDIT01 — Tư duy cắt dựng & nhịp độ`
- **Format:** Breakdown (Thực nghiệm Kuleshov ứng dụng vào dựng video ngắn thương mại/xây kênh)
- **Tệp người xem:** Creator, video editor muốn nâng tư duy kể chuyện bằng hình ảnh
- **Mục tiêu Funnel:** Nhận biết (Awareness)
- **Claim duy nhất:** Chỉ với đúng 3 cảnh quay cố định (Cận mặt người, Cận đồng hồ/màn hình giờ muộn, Cận thành phẩm), việc đổi thứ tự xuất hiện sẽ tạo ra 3 câu chuyện và cảm xúc hoàn toàn khác nhau.
- **Bằng chứng cần chuẩn bị:** 3 shot hình quay thật của Thành (Shot A: Cận mặt Thành nhìn tập trung; Shot B: Đồng hồ điểm 23:45; Shot C: Bản video vừa render xong 100%) được ghép thành 3 bản dựng khác thứ tự trên màn hình.
- **CTA & Offer:** Lưu video lại để thử đảo thứ tự shot ở project tiếp theo (Offer: **Không bán**).

#### 2. Bảng kịch bản chi tiết (38 giây)
| Timecode | Hình ảnh / Thao tác màn hình | Text trên màn hình | Lời thoại của Thành + Nhịp / SFX |
| :--- | :--- | :--- | :--- |
| `00:00 – 00:04` | **Hiển thị 3 ô cảnh quay gốc trên màn hình:**<br>- Shot 1: Đồng hồ `23:45`<br>- Shot 2: Mặt Thành nhìn màn hình<br>- Shot 3: Thanh Render `100% Complete` | Cùng **3 cảnh quay gốc**<br>Đổi thứ tự = Đổi hoàn toàn cảm xúc | Trên màn hình là đúng ba cảnh quay không hề có lời thoại. Nhưng chỉ cần mình đổi thứ tự ghép trên timeline, người xem sẽ hiểu thành ba câu chuyện khác nhau. |
| `00:04 – 00:13` | **Bản dựng 1 (`Shot 1 → Shot 2 → Shot 3`):** Đồng hồ 23:45 → Mặt Thành tập trung → Render xong 100% (thở phào nhẹ). | **Cấu trúc 1:** Giờ muộn → Tập trung → Hoàn thành<br>👉 Cảm giác: **Kiên trì & nhẹ nhõm** | *[SFX: Tiếng tích tắc nhẹ → Tiếng chuông báo xong]* Bản thứ nhất: mở bằng đồng hồ gần nửa đêm, qua nét mặt tập trung, rồi kết bằng màn hình xuất file xong một trăm phần trăm. Người xem sẽ cảm nhận đây là sự kiên trì và nhẹ nhõm khi xong việc. |
| `00:13 – 00:22` | **Bản dựng 2 (`Shot 3 → Shot 1 → Shot 2`):** Render xong 100% → Đồng hồ 23:45 → Mặt Thành vẫn nhìn đăm chiêu vào màn hình. | **Cấu trúc 2:** Xong việc → Giờ muộn → Vẫn đăm chiêu<br>👉 Cảm giác: **Chưa hài lòng, muốn làm kỹ hơn** | *[SFX: Whoosh]* Bản thứ hai: mình đảo cảnh xuất file xong lên đầu, tiếp theo là đồng hồ khuya, và kết bằng ánh mắt vẫn đang suy nghĩ. Lúc này cảm giác lại là: dù đã xong nhưng người làm vẫn chưa thật sự hài lòng. |
| `00:22 – 00:31` | **Bản dựng 3 (`Shot 2 → Shot 3 → Shot 1`):** Mặt Thành nhìn → Render 100% ngay lập tức → Đồng hồ. | **Cấu trúc 3:** Nhìn màn hình → Xong ngay → Kiểm tra giờ<br>👉 Cảm giác: **Làm việc gọn & chủ động tốc độ** | *[SFX: Whoosh]* Và bản thứ ba: mở bằng ánh mắt kiểm tra, sang ngay kết quả hoàn thành rồi mới nhìn giờ. Cảm giác mang lại là sự chủ động và tốc độ xử lý gọn gàng. |
| `00:31 – 00:38` | **A-roll Thành nói trực diện:** Giải thích ứng dụng thực tế khi dựng video cho khách/kênh. | Cảnh đứng cuối sẽ quyết định **dư âm của người xem**<br>**Lưu video** để đối chiếu khi dựng | Khi dựng video, cảnh bạn đặt ở đầu quyết định sự tò mò, còn cảnh bạn đặt ở cuối quyết định cảm xúc đọng lại. *[Nghỉ 0.5s]* Lưu video này lại để thử đảo thứ tự shot ở project tiếp theo của bạn nhé. |

#### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] `C024_AROLL_01.mp4`: Thành nói trực diện đoạn dẫn và đoạn kết.
- [ ] `C024_BROLL_SHOT1_CLOCK.mp4`: Cận cảnh đồng hồ bàn hoặc góc màn hình hiển thị `23:45`.
- [ ] `C024_BROLL_SHOT2_FACE.mp4`: Cận cảnh gương mặt Thành nhìn vào màn hình (ánh sáng màn hình hắt nhẹ lên mặt, biểu cảm trung tính tập trung).
- [ ] `C024_BROLL_SHOT3_RENDER.mp4`: Cận cảnh cửa sổ Premiere / Media Encoder chạy thanh xanh chạm mốc `100%`.

#### 4. Bản phân phối đa kênh (`crosspost`)
- **Caption TikTok / Reels:**
  - **Text trên Thumbnail:** Đổi thứ tự shot — Đổi cảm xúc
  - **Caption:** Không quay thêm bất kỳ cảnh mới nào, chỉ đổi vị trí 3 shot hình trên timeline là câu chuyện đã rẽ sang hướng khác. Cảnh mở đầu tạo sự tò mò, cảnh kết thúc quyết định dư âm. Lưu lại để thử ngay khi dựng B-roll nhé! `#dungcochudich #videoediting #storytelling #kuleshoveffect`
- **Bài đăng Facebook cá nhân (155 chữ):**
  Trong điện ảnh có một khái niệm kinh điển là hiệu ứng Kuleshov, nhưng khi áp dụng vào dựng video ngắn 30 giây hằng ngày, bạn có thể hiểu đơn giản là: **ý nghĩa không chỉ nằm ở bản thân cảnh quay, mà nằm ở việc cảnh nào đứng trước và cảnh nào đứng sau**.
  Trong video hôm nay, mình thử lấy đúng 3 cảnh B-roll rất quen thuộc của dân làm nghề:
  - Cảnh A: Đồng hồ chỉ 23h45 đêm.
  - Cảnh B: Gương mặt đang nhìn màn hình máy tính.
  - Cảnh C: Thanh xuất file báo hoàn thành 100%.
  Khi xếp theo thứ tự `A → B → C`, người xem thấy một buổi làm việc vất vả nhưng trọn vẹn. Nhưng khi đảo thành `C → A → B` (xong file rồi mà gần nửa đêm vẫn ngồi nhìn màn hình đăm chiêu), câu chuyện lập tức biến thành sự cầu toàn hoặc trăn trở vì bản dựng chưa ưng ý.
  Vì vậy, trước khi phàn nàn là thiếu cảnh quay đẹp, mình luôn thử đảo vị trí của cảnh Kết quả và cảnh Phản ứng trên timeline — rất nhiều lần câu chuyện trở nên sắc nét hơn mà không tốn thêm một phút bấm máy nào.

---

### 🎬 VIDEO 11 — MÃ `C042`: AI CHO Ý TƯỞNG NHƯNG AI CHỊU TRÁCH NHIỆM CHỌN?

#### 1. Thông tin định danh
- **Ngày đăng:** Thứ Năm, 12/11/2026 (Lịch bắt buộc)
- **Pillar / Tuyến nội dung:** `P3 — AI trong workflow editor` / `AI01 — Ideation & Research bằng AI`
- **Format:** Talking Head kết hợp Bảng tiêu chí 3 điểm trên màn hình
- **Tệp người xem:** Creator, người làm nội dung đang dùng AI nhưng kênh bị loãng chủ đề
- **Mục tiêu Funnel:** Tin cậy (Trust)
- **Claim duy nhất:** AI có thể đẻ ra 50 ý tưởng trong 1 phút, nhưng người chịu trách nhiệm khi video lên không đúng tệp là bạn; hãy lọc mọi ý tưởng của AI qua 3 câu hỏi trước khi viết kịch bản.
- **Bằng chứng cần chuẩn bị:** Bảng 3 tiêu chí lọc ý tưởng của Thành trên Notion/Sheet (Đúng tệp đang phục vụ không? Có bằng chứng quay thật được không? Dẫn về đúng 1 hành động tiếp theo không?) kèm ví dụ 1 ý tưởng AI nghe kêu nhưng bị loại.
- **CTA & Offer:** Lưu bộ 3 tiêu chí lọc ý tưởng này & xem lộ trình học AI thực chiến tại mục **Zero To AI** ở bio.

#### 2. Bảng kịch bản chi tiết (38 giây)
| Timecode | Hình ảnh / Thao tác màn hình | Text trên màn hình | Lời thoại của Thành + Nhịp / SFX |
| :--- | :--- | :--- | :--- |
| `00:00 – 00:04` | **A-roll Thành + B-roll màn hình AI chạy chữ dài dằng dặc:** Thành đóng máy hoặc khoanh đỏ vào 1 ý tưởng "Bắt trend triệu view" lệch hẳn định vị kênh. | AI đưa ra **50 ý tưởng**<br>Nhưng ai chịu trách nhiệm khi **lệch tệp**? | AI có thể cho bạn năm mươi ý tưởng trong một phút, nhưng nếu quay xong mà kênh bị loãng tệp người xem thì người chịu trách nhiệm vẫn là bạn, không phải AI. |
| `00:04 – 00:13` | **Tiêu chí 1 hiển thị kèm ví dụ trên bảng Backlog:** Gạch bỏ chủ đề "Tin tức công nghệ chung chung", giữ lại chủ đề "Cách dùng AI rút ngắn khâu dựng". | **Tiêu chí 1: Có giải quyết đúng vấn đề của tệp chính không?** | Để không bị AI dẫn đi lan man, mình luôn lọc mọi ý tưởng qua ba câu hỏi. *[SFX: Pop]* Câu hỏi một: chủ đề này có giải quyết đúng nỗi đau của tệp khách hàng hoặc người xem mình đang phục vụ không, hay chỉ là một chủ đề nghe có vẻ đông người hóng? |
| `00:13 – 00:22` | **Tiêu chí 2 hiển thị + Cận cảnh thư mục Footage/Timeline:** Mở folder `02_FOOTAGE` kiểm tra xem có hình ảnh thật để chứng minh không. | **Tiêu chí 2: Mình có bằng chứng thật để đưa lên hình không?** | *[SFX: Pop]* Câu hỏi hai: trong tuần này mình có sẵn timeline thật, bản so sánh trước sau hoặc thao tác thực tế nào để chứng minh cho ý tưởng đó không? Nếu chỉ ngồi nói miệng mà không có hình chứng minh, mình bỏ qua ngay. |
| `00:22 – 00:31` | **Tiêu chí 3 hiển thị + Cột CTA & Offer trên Sheet:** Nối rõ từ Chủ đề → 1 CTA (Lưu bài / Starter Kit / Dịch vụ / Zero To AI). | **Tiêu chí 3: Xem xong 30 giây, người xem làm gì tiếp theo?** | *[SFX: Pop]* Và câu hỏi ba: sau khi xem hết ba mươi giây đó, bước hành động tiếp theo hợp lý nhất của người xem là gì? |
| `00:31 – 00:38` | **A-roll Thành nói trực diện:** Hiện khung tổng kết 3 tiêu chí + chỉ dẫn mục Zero To AI ở bio. | Lưu lại **3 tiêu chí lọc ý tưởng**<br>Xem lộ trình AI tại mục **Zero To AI** ở bio | Dùng AI để mở rộng góc nhìn, nhưng dùng tư duy marketing để khóa lựa chọn — đó là cách mình dựng có chủ đích. *[Nghỉ 0.5s]* Bạn lưu lại ba tiêu chí này và xem thêm lộ trình ứng dụng AI bài bản ở mục Zero To AI trên bio của mình nhé. |

#### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] `C042_AROLL_01.mp4`: Thành nói trực diện ống kính, phong thái đĩnh đạc, rõ ràng từng tiêu chí.
- [ ] `C042_SCREEN_CRITERIA.mp4`: Quay màn hình bảng lọc ý tưởng 3 cột trên Google Sheet / Notion của Thành (có tích xanh ✅ và gạch đỏ ❌).
- [ ] `C042_BROLL_FOOTAGE_CHECK.mp4`: Cảnh mở thư mục Footage/Project trên máy tính đối chiếu với ý tưởng đã chọn.

#### 4. Bản phân phối đa kênh (`crosspost`)
- **Caption TikTok / Reels:**
  - **Text trên Thumbnail:** AI cho ý tưởng — Ai chịu trách nhiệm chọn?
  - **Caption:** Cái bẫy lớn nhất khi dùng AI làm nội dung là thấy ý tưởng nào AI gợi ý cũng hay, dẫn đến làm 10 bài về 10 hướng khác nhau. Hãy lọc qua 3 câu hỏi này trước khi bấm máy. Xem thêm lộ trình học AI thực chiến ở mục Zero To AI trên bio mình nhé! `#dungcochudich #aiworkflow #contentstrategy #zerotoai`
- **Bài đăng Facebook cá nhân (165 chữ):**
  Từ ngày có AI, việc "bí ý tưởng" gần như biến mất, nhưng một vấn đề mới lại xuất hiện: **bội thực hướng đi**.
  Bạn chỉ cần gõ 1 dòng lệnh là có ngay 30 chủ đề video. Nhưng nếu hôm nay mình làm một bài điểm tin công nghệ vì thấy AI gợi ý đang hot, ngày mai lại làm một bài mẹo vặt đời sống, thì sau 1 tháng người vào trang cá nhân sẽ không hiểu mình thực sự làm nghề gì.
  AI không chịu trách nhiệm cho định vị cá nhân hay doanh thu của bạn. Vì vậy, trước khi đưa bất kỳ gợi ý nào của AI vào lịch quay hằng tuần, mình luôn bắt nó đi qua 3 bộ lọc của con người:
  1. **Bộ lọc Tệp xem:** Ý tưởng này thu hút người xem giải trí lướt qua hay thu hút đúng người đang cần làm video có mục tiêu?
  2. **Bộ lọc Bằng chứng:** Mình có mở được timeline, file thiết kế hay kết quả thực tế lên màn hình để chứng minh không? (Không có bằng chứng hình ảnh = Không quay).
  3. **Bộ lọc Hành động:** Video này dẫn người xem tới bước tiếp theo nào trong hệ thống (lưu tài liệu, hỏi dịch vụ hay tìm hiểu lộ trình học)?
  Bạn nào muốn rèn tư duy làm chủ AI từ gốc thay vì chạy theo công cụ thì tham khảo mục **Zero To AI** trên bio của mình nhé.

---

### 🎬 VIDEO 12 — MÃ `C056`: TUẦN NÀY TÔI HỌC ĐƯỢC GÌ TRONG AFTER EFFECTS?

#### 1. Thông tin định danh
- **Ngày đăng:** Thứ Bảy, 14/11/2026 (Lịch linh hoạt — Khép lại 12 video Sprint 1)
- **Pillar / Tuyến nội dung:** `P4 — Hành trình & Bằng chứng` / `JRN02 — Nhật ký nâng cấp kỹ năng (Build in Public)`
- **Format:** Weekly Log (Nhật ký học & ứng dụng 1 kỹ thuật thực tế trong tuần)
- **Tệp người xem:** Editor mới, creator tự dựng video muốn nâng cấp hình ảnh vừa đủ
- **Mục tiêu Funnel:** Tin cậy (Trust)
- **Claim duy nhất:** Không cần đợi học hết After Effects mới dám dùng; chỉ cần nắm vững 1 kỹ thuật nhỏ là chỉnh đồ thị tốc độ (Speed Graph) cho thẻ chữ (Text Card) là đã giúp điểm nhấn thông điệp mượt và có trọng lượng hơn hẳn keyframe mặc định.
- **Bằng chứng cần chuẩn bị:** Quay màn hình bài tập thực hành thật trong After Effects của Thành tuần này: so sánh chuyển động Linear (đều đều, cứng) với chuyển động đã kéo Speed Graph (nhanh đầu, phanh mượt ở điểm dừng để người xem đọc chữ).
- **CTA & Offer:** Theo dõi series nhật ký học & làm nghề mỗi tuần trên kênh (Offer: **Không bán**).

#### 2. Bảng kịch bản chi tiết (37 giây)
| Timecode | Hình ảnh / Thao tác màn hình | Text trên màn hình | Lời thoại của Thành + Nhịp / SFX |
| :--- | :--- | :--- | :--- |
| `00:00 – 00:04` | **Split-screen trên After Effects:** Bên trên là thẻ chữ trượt vào bằng keyframe thường (cứng, đều); bên dưới là thẻ chữ trượt vào có chỉnh Speed Graph (vào nhanh, dừng êm đúng nhịp đọc). | Nhật ký học **After Effects** tuần 3:<br>Làm chủ **Speed Graph** cho thẻ chữ | Tuần này khi luyện After Effects, mình không học hiệu ứng cháy nổ phức tạp, mà tập trung làm chủ đúng một thứ: đồ thị tốc độ cho các thẻ chữ trên màn hình. |
| `00:04 – 00:13` | **Screen Record cửa sổ Timeline AE:** Phóng to 2 keyframe Position hình thoi mặc định (Linear). Chạy thử thấy thẻ chữ trượt từ từ rất mất thời gian. | **Keyframe mặc định (Linear):**<br>Chuyển động đều đều, làm chậm nhịp đọc | Lúc mới dùng After Effects, mình hay đặt hai điểm keyframe rồi để mặc định. Kết quả là thẻ chữ trượt vào rất đơ và mất gần một giây người xem mới đọc rõ được dòng chữ. |
| `00:13 – 00:23` | **Screen Record thao tác nhấn `F9` (Easy Ease) → Mở `Graph Editor`:** Cảnh Thành kéo tay cầm (handle) đồ thị tốc độ dốc cao ở đầu và thoải dần về cuối. | **Nhấn F9 → Mở Speed Graph:**<br>Vào nhanh ở 4 frame đầu, phanh êm để mắt đọc chữ | *[SFX: Click + Whoosh mượt]* Cách mình sửa trong tuần này: bôi đen keyframe nhấn F9, mở bảng Speed Graph và kéo đỉnh tốc độ dồn hết về phía đầu. Nhờ vậy, thẻ chữ lao vào khung hình chỉ trong bốn frame đầu rồi phanh êm lại ngay lập tức để mắt người xem đọc được từ khóa. |
| `00:23 – 00:31` | **B-roll ứng dụng thực tế:** Đưa đúng preset Text Card vừa làm trong AE sang Premiere Pro (qua MOGRT / Dynamic Link) áp vào video `C002` và `C042`. | Đóng gói thành **Preset dùng lại** cho cả tuần | Làm xong một lần, mình lưu luôn chuyển động này thành mẫu cố định để áp vào toàn bộ các thẻ tiêu đề trong bốn video của tuần. |
| `00:31 – 00:37` | **A-roll Thành nói trực diện:** Góc bàn làm việc quen thuộc, nụ cười nhẹ nhàng. | Học 1 kỹ thuật nhỏ → **Ứng dụng ngay vào việc thật**<br>**Theo dõi kênh** để xem nhật ký tuần tới | Học một kỹ thuật nhỏ nhưng phục vụ trực tiếp cho việc giữ mắt người xem — đó là cách mình dựng có chủ đích. *[Nghỉ 0.5s]* Theo dõi kênh để xem tuần tới mình nâng cấp tiếp phần nào nhé. |

#### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] `C056_AROLL_01.mp4`: Thành nói trực diện ống kính (Medium Close-up).
- [ ] `C056_SCREEN_AE_LINEAR.mp4`: Quay màn hình After Effects cảnh 2 keyframe hình thoi Linear và chuyển động thẻ chữ bị cứng.
- [ ] `C056_SCREEN_AE_GRAPH.mp4`: Quay màn hình thao tác bấm `F9`, mở `Graph Editor` (chọn Edit Speed Graph) và kéo đường cong vận tốc hình vây cá mập.
- [ ] `C056_SCREEN_APPLY.mp4`: Cảnh kéo thẻ chữ đó vào timeline Premiere Pro của video thực tế trên kênh.

#### 4. Bản phân phối đa kênh (`crosspost`)
- **Caption TikTok / Reels:**
  - **Text trên Thumbnail:** Tuần này mình học gì trong After Effects?
  - **Caption:** Không đợi giỏi hết mọi kỹ xảo mới dám ứng dụng. Tuần này mình rèn đúng phần Speed Graph trong After Effects để các thẻ tiêu đề vào khung hình nhanh, phanh êm và giúp người xem đọc từ khóa dễ hơn. Theo dõi kênh để cùng học và làm nghề mỗi tuần nhé! `#dungcochudich #aftereffects #motiongraphics #buildinpublic`
- **Bài đăng Facebook cá nhân (165 chữ):**
  Trước đây mỗi lần mở After Effects lên là mình hơi khớp vì giao diện quá nhiều bảng điều khiển, cứ nghĩ phải làm được những đoạn intro 3D hay hiệu ứng chuyển cảnh phức tạp mới gọi là biết dùng AE.
  Nhưng khi quay về đúng mục tiêu **Dựng Có Chủ Đích** cho video ngắn, mình tự đặt quy tắc học mới cho bản thân: **Mỗi tuần chỉ rèn đúng 1 kỹ thuật nhỏ, miễn là áp dụng được ngay vào các video đang dựng**.
  Bài tập tuần này của mình là chỉnh **Speed Graph (đồ thị tốc độ)** cho các bảng chữ (Text Card) minh họa ý chính:
  1. Thay vì để keyframe mặc định làm thẻ chữ trôi đều đều mất gần 1 giây mới vào giữa màn hình, mình dùng Easy Ease (`F9`) và kéo đồ thị tốc độ vọt lên ở 4–5 frame đầu tiên.
  2. Phần đuôi đồ thị kéo thoải dài ra để thẻ chữ "phanh êm" ngay đúng vị trí mắt người xem đang nhìn.
  3. Đóng gói lại thành 1 file mẫu để tái sử dụng cho các video phân tích trên Premiere, tiết kiệm được rất nhiều thời gian căn chỉnh thủ công.
  Bạn nào cũng đang tự học thêm After Effects để bổ trợ cho Premiere thì thử bắt đầu từ chính bảng Graph Editor này nhé, nhỏ nhưng thay đổi cảm giác thị giác rõ rệt lắm.

---

## 5. BẢNG KIỂM TRA CHẤT LƯỢNG (QA CHECKLIST) CHO CẢ 12 VIDEO SPRINT 1

Trước khi chuyển bất kỳ video nào từ `03_PROJECT_EDIT` sang `04_EXPORT`, kiểm tra đủ 8 tiêu chí sau:
- [ ] **Đúng tỷ lệ Pillar Sprint 1:** 5 video `P1` (`C001, C002, C003, C004` = 33.3%–35%), 3 video `P2` (`C022, C023, C024` = 25%–30%), 3 video `P3` (`C040, C041, C042` = 25%), 2 video `P4` (`C055, C056` = 16.7%).
- [ ] **3 giây đầu:** Không có câu chào hỏi, có chuyển động thị giác ngay giây `00:00`, tiêu đề nằm gọn trong vùng an toàn.
- [ ] **Độ nén 1-Claim:** Mỗi video chỉ giải quyết đúng 1 vấn đề, thời lượng nằm trong khung `35 – 40 giây`.
- [ ] **Bằng chứng thật trên màn hình:** Có mặt ít nhất 1 trong 3 yếu tố: Before/After, Timeline Premiere/AE thật, hoặc Input/Output AI thật.
- [ ] **Quy chuẩn On-screen Text:** Viết hoa chữ cái đầu dòng, font không chân rõ nét (`#F6F1E8`), mỗi khung hình chỉ nhấn màu 1 cụm từ khóa.
- [ ] **Đúng 1 CTA khớp Funnel:** Không nhồi 2 lời kêu gọi hành động trong cùng 1 video.
- [ ] **Âm thanh:** Giọng nói đạt `-6dB` đến `-3dB`, nhạc nền `-24dB` đến `-20dB`, không lạm dụng SFX ở mọi vết cắt.
- [ ] **Crosspost riêng biệt:** Bài đăng Facebook cá nhân được đăng bằng văn bản chi tiết 150–180 chữ kèm video/ảnh chụp màn hình, tuyệt đối không copy-paste nguyên caption ngắn của TikTok.

<!-- ===== /file: personal-brand-video-engine/references/01_Y_TUONG_VA_SCRIPT/01_SPRINT_1_TUAN_01_03_THU_NGHIEM.md ===== -->

<!-- ===== file: personal-brand-video-engine/references/01_Y_TUONG_VA_SCRIPT/02_SPRINT_2_TUAN_04_06_XAY_BANG_CHUNG.md ===== -->

# KỊCH BẢN SẢN XUẤT CHI TIẾT — SPRINT 2 (TUẦN 04 – TUẦN 06)
## Giai đoạn: Xây Bằng Chứng & Ra Mắt Starter Kit (16/11/2026 – 05/12/2026)

> **Định vị xuyên suốt:** Thành — Dựng Có Chủ Đích (Marketing Video Editor ứng dụng AI)
> **Mục tiêu Sprint 2:** Chuyển từ giai đoạn định hình góc nhìn sang chứng minh năng lực qua các ca sửa bài (Audit), quy trình làm sạch timeline, ứng dụng AI giải quyết khâu tiền kỳ (Brief -> Shot list / Script / Hook A/B test) và chính thức đẩy lưu lượng vào **Starter Kit** miễn phí trên bio cùng lời mời trải nghiệm **Dịch vụ Edit** và **Zero To AI**.
> **Quy chuẩn áp dụng:** `brand-voice` (câu ngắn 8–16 từ, mở đầu trực diện không chào hỏi, xưng "mình" - gọi "bạn") + `content-engine` (cấu trúc 4 nhịp 00:00–00:40) + `crosspost` (tách biệt Caption TikTok/Reels và Bài đăng Facebook cá nhân 120–180 chữ).

---

# PHẦN I: LỊCH TỔNG QUAN SPRINT 2 (VIDEO #13 ĐẾN VIDEO #24)

| TT | Mã Video | Ngày đăng | Thứ | Pillar & Tuyến | Format | Tệp người xem | Funnel | CTA & Offer | Tiêu đề gốc |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **13** | **C005** | 16/11/2026 | Thứ Hai | P1 - MKT02 | Audit | Chủ shop | Cân nhắc | Nhắn EDIT (Dịch vụ) | Video này đẹp nhưng không biết đang bán gì |
| **14** | **C006** | 17/11/2026 | Thứ Ba | P1 - MKT02 | Whiteboard | Marketer | Nhận biết | Lưu framework (Starter Kit) | Một insight nên thành một video |
| **15** | **C025** | 19/11/2026 | Thứ Năm | P2 - EDIT02 | Screen record | Editor mới | Nhận biết | Lưu tutorial (Không bán) | Ba thao tác Premiere giúp timeline sạch hơn |
| **16** | **C043** | 21/11/2026 | Thứ Bảy (LH) | P3 - AI02 | Workflow demo | Creator | Cân nhắc | Nhận template (Zero To AI) | Từ brief thành shot list bằng AI |
| **17** | **C007** | 23/11/2026 | Thứ Hai | P1 - MKT02 | Case | Creator | Cân nhắc | Nhận mẫu (Starter Kit) | Từ nỗi đau khách hàng thành câu mở đầu |
| **18** | **C026** | 24/11/2026 | Thứ Ba | P2 - EDIT02 | Tutorial | Editor | Nhận biết | Theo dõi series (Không bán) | Khi nào nên dùng adjustment layer? |
| **19** | **C044** | 26/11/2026 | Thứ Năm | P3 - AI02 | Before/after | Creator | Nhận biết | Nhận prompt (Zero To AI) | AI viết script nghe như máy, tôi sửa thế nào? |
| **20** | **C057** | 28/11/2026 | Thứ Bảy (LH) | P4 - JRN02 | Progress | Editor mới | Tin cậy | Lưu hành trình (Không bán) | 30 ngày học motion: tiến bộ nào nhìn thấy được? |
| **21** | **C008** | 30/11/2026 | Thứ Hai | P1 - MKT02 | BTS | Khách hàng | Tin cậy | Nhắn brief (Dịch vụ) | Brief nói nhiều nhưng video cần nói một điều |
| **22** | **C009** | 01/12/2026 | Thứ Ba | P1 - MKT03 | Talking head | Creator | Nhận biết | Lưu bảng CTA (Starter Kit) | CTA theo dõi không phù hợp mọi video |
| **23** | **C027** | 03/12/2026 | Thứ Năm | P2 - EDIT02 | Tutorial | Creator | Nhận biết | Nhận checklist (Starter Kit) | Cách dựng phiên bản dọc từ footage ngang |
| **24** | **C045** | 05/12/2026 | Thứ Bảy (LH) | P3 - AI02 | Screen record | Marketer | Cân nhắc | Nhận prompt (Zero To AI) | Dùng AI tạo ba phiên bản hook để A/B test |

---

# PHẦN II: KỊCH BẢN SẢN XUẤT CHI TIẾT TUẦN 4 (16/11/2026 – 21/11/2026)

---

## VIDEO #13 — MÃ C005: "Video này đẹp nhưng không biết đang bán gì"

### 1. Thông tin định danh
* **Ngày đăng:** Thứ Hai, 16/11/2026 (Lịch cố định)
* **Pillar / Tuyến nội dung:** P1 - Marketing trong video (`MKT02` — Thông điệp & Cấu trúc bán hàng)
* **Format:** Audit (Phân tích & sửa lỗi trực tiếp trên video thực tế)
* **Tệp người xem mục tiêu:** Chủ shop (Thời trang, F&B, Phụ kiện, Mỹ phẩm đang tự quay/thuê quay video sản phẩm)
* **Mục tiêu Funnel:** Cân nhắc (Chứng minh khả năng chẩn đoán đúng bệnh video đẹp nhưng không ra đơn)
* **Claim duy nhất:** Video quay đẹp mà giấu mất lợi ích cốt lõi trong 5 giây đầu và thiếu bối cảnh sử dụng thực tế thì người xem chỉ khen cảnh đẹp rồi lướt qua, không biết bạn đang bán giải pháp gì.
* **Bằng chứng cần chuẩn bị:** 1 video sản phẩm thực tế đã xin phép chủ shop (ví dụ: video quay cận cảnh đèn bàn học hoặc túi da handmade với góc máy cinematic lung linh nhưng 10 giây đầu chỉ toàn cảnh pan máy chậm), kèm bản dựng lại bố cục thông tin trên Premiere.
* **CTA & Offer:** Nhắn chữ `EDIT` kèm mục tiêu video (Offer: Dịch vụ Edit/Media).

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) + SFX / Nhịp |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03** *(Hook)* | Mở màn bằng 2 giây video gốc của shop: ánh sáng ấm, lia máy slow-motion qua chiếc túi da trên bàn gỗ. Đúng giây 02, dừng hình (Freeze Frame), đóng khung đỏ kèm dấu hỏi lớn. | Quay rất đẹp nhưng đang **bán cái gì?** | *(SFX: Tiếng phanh đĩa / Record scratch nhẹ)* Video này quay cực kỳ nịnh mắt, nhưng xem xong không ai biết shop đang bán gì. |
| **00:03 – 00:10** *(Proof / Tension)* | Thu nhỏ video gốc về góc trái trên, bên dưới mở timeline Premiere của bản gốc. Thành khoanh vùng đỏ đoạn `00:00 – 00:08` toàn các cú lia máy cảnh деко (cốc cà phê, cuốn sách, góc túi). | Mất 8 giây đầu chỉ để **khoe góc máy** | Bạn nhìn timeline bản gốc nhé. Tám giây đầu tiên chỉ toàn cảnh lia qua ly cà phê và góc bàn. Người mua lướt qua trước khi kịp thấy chiếc túi đựng vừa laptop 14 inch. |
| **00:10 – 00:18** *(Body - Bước 1)* | Cắt sang A-roll Thành ngồi trước màn hình (2s), rồi zoom thẳng vào thao tác kéo shot "Bỏ vừa laptop 14 inch + sạc mà phom túi không phồng" từ giây 18 lên ngay giây 00:00. | Bước 1: Đưa **công năng đắt nhất** lên giây đầu | Khi mình dựng lại video này cho chủ shop, mình sửa ba điểm. Một: kéo cảnh nhét gọn chiếc laptop 14 inch từ cuối bài lên ngay hai giây đầu. |
| **00:18 – 00:25** *(Body - Bước 2)* | Màn hình chia đôi (Split-screen): Bên trái là cảnh lia máy vô định (gạch chéo đỏ), bên phải là cảnh người mẫu đeo túi bước vào quán làm việc + text callout chỉ rõ chất liệu chống nước. | Bước 2: Gắn text chỉ rõ **ngữ cảnh sử dụng** | Hai: cắt bỏ một nửa số cảnh quay chậm trùng góc. Thay vào đó là dòng chữ đặt đúng vị trí khóa kéo chống nước để khách đọc được ngay khi tắt tiếng. |
| **00:25 – 00:32** *(Body - Bước 3)* | Show sơ đồ 3 khối màu trên timeline mới: Đỏ (Vấn đề: Túi da hay bị mất phom khi đựng máy nặng) -> Vàng (Test thực tế) -> Xanh lá (Thông số & bảo hành). | Bước 3: Xếp lại theo trục **Vấn đề - Bằng chứng** | Ba: gom lại bố cục thông tin. Nêu đúng nỗi sợ túi bị gãy phom, cho xem cảnh test chịu lực, rồi mới chốt màu sắc và chế độ bảo hành. |
| **00:32 – 00:40** *(Close & CTA)* | Chạy 3 giây bản Final sau khi dựng lại (nhịp gãy gọn, chữ nổi rõ), sau đó chuyển về A-roll Thành nhìn thẳng ống kính, hiện bảng chữ CTA phía dưới trong vùng an toàn. | Nhắn **EDIT** nếu video của bạn chưa ra thông điệp | Hình đẹp giúp giữ mắt, nhưng bố cục thông tin mới giúp bán được hàng. Đó là cách mình dựng có chủ đích. Nếu bạn có sẵn footage đẹp mà chưa ra đơn, nhắn chữ EDIT cho mình nhé. |

### 3. Checklist Shot List cần quay / chụp
- [ ] **A-roll:** Thành ngồi tại bàn làm việc, góc máy 45 độ thấy màn hình timeline phía sau (quay 3 câu: câu dẫn Bước 1, câu kết + CTA).
- [ ] **Screen Record 1:** Mở video gốc trên Premiere, play 8 giây đầu và dùng công cụ vẽ khoanh vùng các đoạn B-roll thừa.
- [ ] **Screen Record 2:** Thao tác ripple-move kéo clip "nhét laptop vào túi" từ giây 18 về giây 00:00 trên timeline.
- [ ] **Export so sánh:** Render đoạn 5 giây đầu Before (chỉ lia máy cảnh vật) vs After (thấy ngay công năng + text callout rõ ràng).

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
* **Caption TikTok:**
  Quay đẹp giúp giữ mắt 2 giây đầu, nhưng bố cục thông tin mới quyết định khách có hỏi mua hay không.
  Nếu bạn có sẵn nguồn quay đẹp nhưng video chưa bật được lý do mua hàng, nhắn chữ "EDIT" kèm ngành hàng cho mình nhé.
  `#dungcochudich` `#marketingvideo` `#videoediting` `#auditvideo`
* **Caption Facebook Reels (Điều chỉnh mở đầu gần gũi với chủ shop):**
  Nhiều chủ shop gửi suộc quay cho mình đều gặp chung một tình trạng: hình ảnh rất lung linh nhưng khách xem xong chỉ thả tim chứ không inbox hỏi giá. Đây là 3 bước mình sắp xếp lại bố cục thông tin trên cùng một bộ footage để người xem hiểu ngay giá trị sản phẩm. Nếu shop bạn đang có sẵn footage mà lên bài chưa hiệu quả, nhắn chữ "EDIT" cho mình nhé.

#### B. Bài đăng Facebook cá nhân (120–180 chữ)
Tuần trước mình nhận kiểm tra giúp một chủ shop phụ kiện da một video quay rất chỉn chu. Ánh sáng đẹp, máy lia mượt, nhưng chạy thử 3 ngày hầu như không có tin nhắn hỏi mua.

Khi mở timeline ra xem, lỗi không nằm ở người quay mà nằm ở thứ tự thông tin khi dựng. Tám giây đầu tiên chỉ dùng để khoe góc quán cà phê, trong khi chi tiết đắt giá nhất là "đựng vừa laptop 14 inch mà không gãy phom túi" lại bị giấu ở tận giây thứ 18.

Mình đã giữ nguyên bộ footage đó và chỉ sửa lại 3 quyết định dựng:
1. Đưa cảnh thử tải trọng laptop lên ngay 2 giây đầu tiên để lọc đúng tệp dân văn phòng.
2. Cắt bỏ 40% các cảnh slow-motion trùng góc, giữ nhịp cắt 2,5 giây/cảnh.
3. Gắn callout text ngắn gọn đúng vào vị trí da chống xước để khách xem tắt tiếng vẫn nắm được ý chính (toàn bộ bản sửa chỉ mất 25 phút sắp xếp lại cấu trúc).

Hình ảnh dưới comment là so sánh bố cục timeline trước và sau khi mình xếp lại. Nếu bạn có sẵn footage sản phẩm nhưng video chưa nói rõ được điểm bán hàng, nhắn chữ "EDIT" cho mình kèm mục tiêu video nhé.

---

## VIDEO #14 — MÃ C006: "Một insight nên thành một video"

### 1. Thông tin định danh
* **Ngày đăng:** Thứ Ba, 17/11/2026 (Lịch cố định)
* **Pillar / Tuyến nội dung:** P1 - Marketing trong video (`MKT02` — Thông điệp & Cấu trúc bán hàng)
* **Format:** Whiteboard (Giải thích trên bảng trắng / iPad / Notion sơ đồ trực quan)
* **Tệp người xem mục tiêu:** Marketer in-house, Content Creator, Chủ shop tự viết kịch bản
* **Mục tiêu Funnel:** Nhận biết (Tạo lượt lưu cao nhờ quy tắc bóc tách ý tưởng rõ ràng)
* **Claim duy nhất:** Nhồi 5 lợi ích vào một video 40 giây làm người xem quên sạch; tách mỗi insight thành một video độc lập vừa giúp thông điệp sắc bén vừa nhân 5 lần số lượng bài đăng từ cùng một buổi quay.
* **Bằng chứng cần chuẩn bị:** 1 trang kịch bản mẫu bị lỗi "tham thông tin" (vừa nói giá rẻ, vừa nói chất liệu bền, vừa nói đổi trả 30 ngày, vừa kể chuyện xưởng sản xuất, vừa hướng dẫn phối đồ) và sơ đồ tách thành 5 kịch bản đơn nhiệm trên bảng/Notion.
* **CTA & Offer:** Lưu lại framework / Lấy mẫu khung tách kịch bản trong **Starter Kit** ở bio.

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) + SFX / Nhịp |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03** *(Hook)* | Cận cảnh tờ kịch bản in giấy (hoặc iPad) bị gạch đỏ chi chít 5 đoạn đánh số từ 1 đến 5. Thành cầm bút khoanh tròn chữ "1 Video = 5 Ý" rồi gạch chéo. | Đừng nhồi **năm thông điệp** vào một video | *(SFX: Tiếng bút dạ gạch mạnh trên giấy)* Một kịch bản bốn mươi giây mà nhồi năm ý bán hàng chính là lý do kênh của bạn nhanh cạn ý tưởng. |
| **00:03 – 00:10** *(Proof / Tension)* | Zoom vào bản kịch bản mẫu của một sản phẩm áo sơ mi chống nhăn: dòng 1 khen vải mát, dòng 2 nói không cần ủi, dòng 3 khoe đường may, dòng 4 báo giá sale, dòng 5 hướng dẫn 3 cách phối đồ. | Tham thông tin làm người xem **quên sạch** | Đây là kịch bản thật mình từng nhận. Trong ba mươi giây, bài viết cố nói từ chất vải, chống nhăn, cách phối đồ cho tới chính sách đổi trả. Kết quả là người xem không nhớ nổi điểm mạnh nhất. |
| **00:10 – 00:18** *(Body - Bước 1)* | Thành viết lên bảng trắng (hoặc kéo sơ đồ trên màn hình): Rút 1 ý "Áo rút từ vali ra mặc đi họp luôn không cần ủi" thành Video số 1 (Tệp hay đi công tác). | Video 1: Giải quyết **nỗi sợ nhăn áo** khi đi xa | Cách mình xử lý là áp dụng quy tắc một insight thành một video. Ý chống nhăn mình tách riêng thành video số một, đánh đúng vào người hay đi công tác vội. |
| **00:18 – 00:25** *(Body - Bước 2)* | Kéo tiếp nhánh thứ 2 và thứ 3 trên bảng: Ý "Mặc 8 tiếng ngồi điều hòa hay chạy ngoài nắng không bí lưng" -> Video số 2; Ý "1 áo sơ mi phối 3 quần đi làm cả tuần" -> Video số 3. | Mỗi video chỉ giữ **một góc nhìn** duy nhất | Ý thoáng khí khi chạy xe ngoài nắng tách thành video số hai. Còn phần hướng dẫn phối đồ thành video số ba dạng lookbook nhanh. Mỗi bài chỉ chứng minh đúng một lời hứa. |
| **00:25 – 00:32** *(Body - Bước 3)* | Hiển thị bảng tổng kết: 1 buổi quay (2 giờ) -> 5 câu Hook khác nhau + 1 bộ B-roll dùng chung -> Xuất ra 5 video cho cả tuần. | Một buổi quay tạo ra **năm video** độc lập | Làm cách này, bạn chỉ cần quay một buổi nhưng có ngay năm video cho cả tuần. Quan trọng hơn, bạn đo được chính xác khách hàng mua vì áo chống nhăn hay vì dễ phối đồ. |
| **00:32 – 00:40** *(Close & CTA)* | Thành đứng cạnh bảng sơ đồ hoàn chỉnh, chỉ tay vào khung cấu trúc "1 Insight - 1 Bằng chứng - 1 CTA". | Lưu lại **khung tách ý** trong Starter Kit ở bio | Bớt thông tin đi là cách nhanh nhất để thông điệp rõ lên. Đó là cách mình dựng có chủ đích. Bạn lưu lại sơ đồ này hoặc lấy bảng mẫu tách kịch bản trong Starter Kit ở bio nhé. |

### 3. Checklist Shot List cần quay / chụp
- [ ] **A-roll + Whiteboard:** Góc máy ngang ngực hướng vào Thành và bảng trắng (hoặc quay top-down tay Thành vẽ sơ đồ trên giấy A4 chấm bi / iPad).
- [ ] **Insert B-roll 1:** Cận cảnh trang kịch bản mẫu có highlight 5 màu khác nhau cho 5 ý bị chồng chéo.
- [ ] **Insert B-roll 2:** Màn hình Notion / Excel trong bộ Starter Kit hiển thị 1 chủ đề gốc được chia thành 5 hàng kịch bản (Hook - Proof - CTA riêng).

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
* **Caption TikTok:**
  Đừng bắt một video 30 giây phải gánh cả chất liệu, giá tiền, câu chuyện thương hiệu lẫn hướng dẫn sử dụng. Tách mỗi insight thành 1 video riêng vừa dễ dựng vừa biết chính xác khách mua vì lý do nào.
  Mình để sẵn bảng mẫu tách kịch bản trong Starter Kit ở bio, bạn vào lấy về dùng ngay.
  `#dungcochudich` `#contentmarketing` `#kịchbảnvideo` `#marketingvideo`
* **Caption Facebook Reels:**
  Lỗi phổ biến nhất khi viết kịch bản video ngắn là sợ thiếu ý nên cái gì cũng muốn đưa vào. Khi tách 1 kịch bản "ôm đồm" thành 5 video đơn nhiệm, bạn vừa giải quyết được bài toán thiếu bài đăng hàng tuần, vừa giúp Editor dựng nhịp video dứt khoát hơn rất nhiều. Bản mẫu chia nhánh ý tưởng mình để sẵn trong Starter Kit ở bio nhé.

#### B. Bài đăng Facebook cá nhân (120–180 chữ)
Nhiều bạn làm content hoặc chủ shop bảo mình là "quay một buổi cực quá nên muốn gom hết điểm mạnh sản phẩm vào một video cho đỡ phí". Nhưng thực tế khi dựng lên, video càng ôm đồm thì tỷ lệ xem hết càng tụt.

Hôm trước mình đọc một bản nháp dài 45 giây của khách: vừa nói chuyện vải mát, vừa test chống nhăn, vừa chỉ 3 cách phối đồ, cuối bài lại thêm chương trình giảm giá. Người xem lướt TikTok không đủ kiên nhẫn để tiêu hóa 4 tầng thông tin như vậy.

Thay vì cố cắt ép cho đủ 45 giây, mình dùng quy tắc "1 Insight = 1 Video":
1. Lọc ra 5 lý do mua hàng độc lập từ bản nháp ban đầu.
2. Mỗi video chỉ chọn 1 nỗi đau cụ thể (ví dụ: rút áo từ vali ra mặc đi họp ngay không cần bàn ủi) và dành trọn 25 giây để chứng minh đúng điều đó.
3. Tái sử dụng chung kho B-roll quay trong 1 buổi, chỉ thay 3 giây mở đầu và lời dẫn (giúp tiết kiệm 70% thời gian quay mới).

Mình có đính kèm sơ đồ tách ý ở ảnh dưới. Bạn nào cần file mẫu chia kịch bản thì vào mục Starter Kit trên bio của mình lấy về dùng nhé.

---

## VIDEO #15 — MÃ C025: "Ba thao tác Premiere giúp timeline sạch hơn"

### 1. Thông tin định danh
* **Ngày đăng:** Thứ Năm, 19/11/2026 (Lịch cố định)
* **Pillar / Tuyến nội dung:** P2 - Edit & Storytelling (`EDIT02` — Quy trình dựng & Tối ưu Timeline)
* **Format:** Screen record (Quay màn hình thao tác thực chiến kết hợp A-roll ngắn)
* **Tệp người xem mục tiêu:** Editor mới, Creator tự dựng video bằng Premiere Pro
* **Mục tiêu Funnel:** Nhận biết (Xây dựng uy tín nghề nghiệp qua kỷ luật quản lý project)
* **Claim duy nhất:** Một timeline được gắn màu theo khối Hook–Body–Close, gom nhóm B-roll có quy tắc và khóa track âm thanh gốc giúp bạn giảm một nửa thời gian khi khách yêu cầu sửa feedback.
* **Bằng chứng cần chuẩn bị:** Project Premiere thật có 2 tab sequence: 1 sequence lộn xộn 12 track chồng chéo cùng màu xanh mặc định vs 1 sequence đã tổ chức gọn gàng thành 4 track Video + 3 track Audio phân màu rõ rệt.
* **CTA & Offer:** Lưu lại tutorial để áp dụng ngay cho project tiếp theo (Offer: Không bán).

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) + SFX / Nhịp |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03** *(Hook)* | Split-screen trên màn hình Premiere: Trên là timeline rối như mạng nhện (10 track nhảy loạn xạ), dưới là timeline phẳng gọn chia 3 dải màu. | Timeline sạch giúp **sửa bài nhanh gấp đôi** | *(SFX: Tiếng click chuột dứt khoát)* Nhìn vào timeline Premiere là biết bạn sẽ mất năm phút hay hai tiếng khi khách báo sửa bài. |
| **00:03 – 00:10** *(Proof / Tension)* | Zoom vào timeline lộn xộn: khi thử kéo dịch 1 câu thoại ở giây 05, toàn bộ chữ, SFX và B-roll phía sau bị lệch nhịp (out-sync) hàng loạt. | Kéo một đoạn làm **lệch toàn bộ** phía sau | Khi để mọi clip chung một màu mặc định và xếp chồng mười track, bạn chỉ cần cắt bớt một câu ở đầu là toàn bộ hiệu ứng âm thanh phía sau lệch nhịp hết. |
| **00:10 – 00:18** *(Body - Bước 1)* | Quay màn hình thao tác thật: Quét chọn cụm 0–3s đổi Label màu Rose (Hồng/Đỏ), cụm 3–30s màu Mango (Cam), cụm 30–40s màu Forest (Xanh lá). | Thao tác 1: Tô **Color Label** theo ba khối nội dung | Đây là ba thao tác mình luôn làm trước khi dựng chi tiết. Một: gán phím tắt đổi màu clip theo cấu trúc bài. Màu hồng cho Hook, màu cam cho thân bài và xanh lá cho đoạn CTA. |
| **00:18 – 00:25** *(Body - Bước 2)* | Chỉ vào các cụm hiệu ứng so sánh Before/After gồm 4 lớp ảnh + mũi tên -> Chuột phải chọn Nest và đặt tên `NEST_01_PROOF_COMPARE` thay vì `Nested Sequence 01`. | Thao tác 2: Đặt tên **Nest** theo đúng chức năng | Hai: chỉ gom Nest cho những cụm đồ họa đã khóa vị trí, và bắt buộc đổi tên ngay thành chức năng của cụm đó. Tuyệt đối không để tên Nested Sequence số một, số hai. |
| **00:25 – 00:32** *(Body - Bước 3)* | Thao tác khóa Track A1 (nhạc nền đã cắt nhịp cuối) hoặc dùng Sync Lock + Ripple Delete (`Shift + Delete`) để rút ngắn đoạn giữa mà phần đuôi tự trượt khít theo. | Thao tác 3: Dùng **Sync Lock** khi cắt rút khoảng trống | Ba: bật đúng Sync Lock trên các track chữ và SFX khi dùng Ripple Delete. Khi khách bảo bỏ câu thứ hai, bạn xóa một nhịp là cả dự án tự trượt khít vào nhau không lệch một frame. |
| **00:32 – 00:40** *(Close & CTA)* | Quay về A-roll Thành trước màn hình chứa timeline sạch đẹp. Hiện bảng tóm tắt 3 quy tắc màu và track. | **Lưu lại** để dọn sạch project tiếp theo của bạn | Dựng nhanh không phải là bấm phím nhanh, mà là không phải đi dọn rác do chính mình bày ra. Đó là cách mình dựng có chủ đích. Bạn lưu lại để thử ngay ở project tối nay nhé. |

### 3. Checklist Shot List cần quay / chụp
- [ ] **Screen Record 1 (60fps):** Quay màn hình Premiere thao tác lỗi lệch sync khi xóa 1 đoạn trên timeline rối.
- [ ] **Screen Record 2:** Quay cận cảnh bảng Label Colors trong Premiere và thao tác gán màu nhanh bằng phím tắt cho 3 phần Hook - Body - Close.
- [ ] **Screen Record 3:** Thao tác đặt tên lại `Nested Sequence` và dùng `Shift + Delete` (Ripple Delete) với Sync Lock bật sáng.
- [ ] **A-roll:** Thành nói câu kết ở góc bàn dựng phim (ánh sáng màn hình hắt nhẹ phía sau).

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
* **Caption TikTok:**
  Dựng bản đầu tiên có thể mất 1 tiếng, nhưng nếu timeline bừa bộn thì lúc sửa feedback cho khách sẽ mất thêm 2 tiếng nữa. 3 thói quen nhỏ trong Premiere giúp mình kiểm soát toàn bộ cấu trúc video chỉ bằng mắt thường.
  Lưu lại video này để đối chiếu khi bạn mở project tiếp theo nhé.
  `#dungcochudich` `#premierepro` `#videoeditor` `#editortips`
* **Caption Facebook Reels:**
  Anh em mới dựng video thường chỉ quan tâm kết quả xuất ra mà quên mất "vệ sinh" timeline. Đến khi khách nhắn "em cắt giúp chị câu ở giây thứ 5 nhé" là toát mồ hôi vì kéo 1 chỗ lệch 10 chỗ. Đây là 3 thao tác cơ bản mình áp dụng ở mọi project để sửa bài trong vài phút. Lưu lại áp dụng thử ngay nhé!

#### B. Bài đăng Facebook cá nhân (120–180 chữ)
Hồi mới đi làm edit, nỗi ám ảnh lớn nhất của mình không phải là lúc dựng bản nháp đầu tiên, mà là tin nhắn của khách lúc 10 giờ đêm: "Em ơi bỏ giúp anh câu thứ 2 ở đầu video nhé, còn lại giữ nguyên".

Với một cái timeline 12 track chồng chéo, cùng một màu xanh mặc định của Premiere, việc rút bớt 3 giây ở đầu đồng nghĩa với việc phải ngồi kéo lại từng dòng chữ, từng tiếng whoosh, từng tấm ảnh minh họa phía sau vì bị trật nhịp.

Sau nhiều lần tự làm khổ mình, mình khóa cứng 3 quy tắc dọn timeline cho mọi project:
1. Tô màu (Color Label) theo đúng cấu trúc marketing: Đỏ cho 3 giây Hook, Cam cho phần chứng minh và Xanh lá cho đoạn chốt CTA. Nhìn từ xa đã biết đoạn nào đang bị dài quá.
2. Chỉ gom Nest khi cụm đồ họa đã chốt bố cục và luôn đặt tên theo nội dung (ví dụ: `NEST_SoSanh_TruocSau` thay vì để mặc định).
3. Quản lý Sync Lock để khi dùng Ripple Delete (phím tắt `Shift + Delete`), toàn bộ hệ thống chữ và âm thanh phía sau tự động trượt khít theo câu thoại.

Timeline sạch thì đầu óc mới thoáng để nghĩ về nhịp cắt. Bạn nào đang tự dựng video cứ lưu lại 3 bước này áp dụng dần nhé.

---

## VIDEO #16 — MÃ C043: "Từ brief thành shot list bằng AI"

### 1. Thông tin định danh
* **Ngày đăng:** Thứ Bảy, 21/11/2026 (Lịch linh hoạt)
* **Pillar / Tuyến nội dung:** P3 - AI trong workflow editor (`AI02` — AI hỗ trợ tiền kỳ, kịch bản & cấu trúc)
* **Format:** Workflow demo (Quay màn hình quy trình thực tế từ Input -> AI -> Chỉnh sửa tay -> Output)
* **Tệp người xem mục tiêu:** Creator độc lập, Marketer kiêm quay dựng, Editor nhận kịch bản chữ từ khách
* **Mục tiêu Funnel:** Cân nhắc (Cho thấy AI giúp tiết kiệm thời gian tiền kỳ thực chất ra sao, dẫn dắt vào hệ thống học bài bản)
* **Claim duy nhất:** Đừng bảo AI "viết kịch bản quay đi", hãy đưa cho nó kịch bản thoại đã chốt kèm danh sách bối cảnh sẵn có để AI chia thành bảng 3 cột A-roll, B-roll và Screen Record trong 2 phút.
* **Bằng chứng cần chuẩn bị:** 1 đoạn kịch bản/brief thực tế (khoảng 120 chữ) -> Màn hình câu lệnh (Prompt) nhập vào Claude/ChatGPT -> Bảng kết quả 3 cột xuất ra -> Bước Thành tự tay gạch bỏ 2 góc quay phi thực tế và thay bằng góc quay khả thi.
* **CTA & Offer:** Nhận template prompt + Xem mục **Zero To AI** ở bio.

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) + SFX / Nhịp |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03** *(Hook)* | Màn hình chia đôi: Bên trái là đoạn văn bản brief chữ dày đặc; bên phải là bảng Shot List 3 cột rõ ràng được tạo ra sau 1 cú bấm. | Biến brief chữ thành **shot list** trong hai phút | *(SFX: Tiếng gõ phím cơ nhanh)* Cầm kịch bản chữ đi quay ngay là cách nhanh nhất để lúc ngồi dựng phát hiện ra mình thiếu cảnh. |
| **00:03 – 00:10** *(Proof / Tension)* | Quay màn hình một câu lệnh sai thường gặp: *"Hãy lên góc quay cho video giới thiệu khóa học này"* -> AI trả về những gợi ý viển vông như "Cảnh flycam bay qua tòa nhà văn phòng", "Cảnh diễn viên quần chúng thảo luận". | Prompt chung chung sẽ ra **góc quay ảo** | Nếu bạn chỉ ném kịch bản vào AI rồi bảo "lên góc quay giúp tôi", nó sẽ bày ra cảnh flycam hay phòng họp mười người mà bạn không hề có sẵn để quay. |
| **00:10 – 00:18** *(Body - Bước 1)* | Zoom vào cấu trúc Prompt thật của Thành trên màn hình: Cột 1 dán kịch bản lời thoại 40s; Cột 2 khóa giới hạn bối cảnh: *"Chỉ quay 1 người tại bàn làm việc, có 1 điện thoại, 1 laptop và màn hình Premiere"*. | Bước 1: Khóa chặt **bối cảnh có sẵn** trong prompt | Cách mình dùng AI làm tiền kỳ thực tế hơn nhiều. Đầu tiên, mình dán lời thoại đã chốt và khóa điều kiện: chỉ có một người ngồi tại bàn làm việc, một laptop và quay màn hình. |
| **00:18 – 00:25** *(Body - Bước 2)* | Quay màn hình AI xuất ra bảng Markdown gồm 4 cột: `Timecode` | `Lời thoại` | `Loại cảnh (A-roll / B-roll / Screen Record)` | `Chuyển động mắt/tay`. | Bước 2: Bắt AI chia bảng **ba nhóm cảnh** rõ ràng | Thứ hai, mình yêu cầu AI chia từng câu thoại thành ba nhóm cảnh: đoạn nào nói trực diện A-roll, đoạn nào chèn B-roll tay thao tác, và đoạn nào phải quay màn hình. |
| **00:25 – 00:32** *(Body - Bước 3)* | Thành copy bảng sang Notion/Google Sheet, dùng chuột sửa trực tiếp 2 dòng: gộp 3 cảnh A-roll lẻ tẻ thành 1 lần bấm máy liên tục để tiết kiệm thời gian setup đèn. | Bước 3: Tự gộp các **góc trùng nhau** để quay nhanh | Bước cuối cùng AI không làm thay được: mình tự rà lại bảng, gộp các câu A-roll cùng góc máy lại để quay một mạch, rồi mới quay cuốn chiếu phần B-roll. |
| **00:32 – 00:40** *(Close & CTA)* | Hiện kết quả tờ checklist Shot List đặt cạnh máy quay ngoài đời thực + A-roll Thành cầm tờ giấy/iPad tích dấu hoàn thành. | Xem lộ trình ứng dụng AI thực chiến tại **Zero To AI** ở bio | AI giúp bạn lên khung nháp trong hai phút, nhưng người quyết định góc máy khả thi vẫn là bạn. Đó là cách mình dựng có chủ đích. Nếu bạn muốn học cách ứng dụng AI vào nội dung từ gốc theo lộ trình rõ ràng, xem mục Zero To AI ở bio của mình nhé. |

### 3. Checklist Shot List cần quay / chụp
- [ ] **Screen Record 1:** Demo kết quả lỗi của AI khi dùng prompt ngắn cụt lủn (đề xuất flycam, studio lớn).
- [ ] **Screen Record 2:** Quay cận cảnh khung Prompt 3 phần của Thành (Vai trò + Giới hạn thiết bị/bối cảnh + Định dạng bảng đầu ra) và tốc độ AI sinh bảng.
- [ ] **Screen Record 3:** Thao tác Thành chỉnh sửa bảng trên Notion (đánh dấu màu груп A-roll để quay 1 lần).
- [ ] **A-roll + B-roll thực tế:** Cảnh Thành cầm iPad mở đúng bảng Shot List đó tích chọn từng cảnh tại góc bàn làm việc.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
* **Caption TikTok:**
  Có kịch bản chữ rồi mà cứ thế bấm máy quay thì lúc lên timeline kiểu gì cũng thiếu B-roll che vết cắt. Đây là cách mình dùng AI chuyển 1 đoạn kịch bản thành bảng Shot List 3 cột khớp đúng thiết bị mình có sẵn.
  Nếu bạn muốn học cách ứng dụng AI vào làm nội dung từ gốc theo lộ trình rõ ràng, xem mục Zero To AI ở bio của mình nhé.
  `#dungcochudich` `#aiworkflow` `#contentcreator` `#shotlist`
* **Caption Facebook Reels:**
  Nhiều bạn tự quay video hay bị cảnh ngồi nói từ đầu đến cuối vì lúc quay không hình dung được đoạn nào cần cảnh chèn (B-roll). Mình dùng AI để tách kịch bản thành danh sách cảnh quay chi tiết chỉ trong 2 phút, nhưng bí quyết nằm ở câu lệnh "khóa bối cảnh có thật". Bạn xem hết quy trình trong video và tham khảo lộ trình Zero To AI ở bio của mình nếu muốn làm chủ workflow này nhé.

#### B. Bài đăng Facebook cá nhân (120–180 chữ)
Lúc mới tự xây kênh và nhận dựng cho khách, mình rất hay gặp cảnh: ngồi vào máy dựng mới phát hiện ra cả video 40 giây chỉ có độc một góc mặt nói chuyện, không có lấy một cảnh B-roll hay quay màn hình nào để minh họa cho lời nói.

Đi quay lại thì mất cả buổi setup đèn, mà dựng tiếp thì video nhạt. Giờ trước khi bấm máy, mình luôn dành 5 phút chạy bước chuyển từ Script sang Shot List:
1. Đưa kịch bản thoại đã chốt vào AI, nhưng bắt buộc kèm dòng giới hạn tài nguyên thật (ví dụ: "Bối cảnh chỉ có bàn làm việc, 1 laptop, 1 điện thoại, không gợi ý cảnh ngoài trời hay diễn viên phụ").
2. Yêu cầu AI xuất ra bảng chia rõ: câu nào giữ A-roll, câu nào cần quay cận tay thao tác, câu nào phải chụp màn hình bằng chứng (bản thô AI chạy mất 30 giây).
3. Mình tự lọc lại bảng đó, gom tất cả các câu cùng góc máy vào một nhóm để quay dứt điểm một lần, tránh việc đổi góc đèn liên tục.

Ảnh dưới là câu lệnh và bảng Shot List mình dùng cho chính video hôm nay. Bạn nào muốn học cách đưa AI vào quy trình làm nội dung bài bản từ gốc thì xem mục Zero To AI trên bio của mình nhé.

---

# PHẦN III: KỊCH BẢN SẢN XUẤT CHI TIẾT TUẦN 5 (23/11/2026 – 28/11/2026)

---

## VIDEO #17 — MÃ C007: "Từ nỗi đau khách hàng thành câu mở đầu"

### 1. Thông tin định danh
* **Ngày đăng:** Thứ Hai, 23/11/2026 (Lịch cố định)
* **Pillar / Tuyến nội dung:** P1 - Marketing trong video (`MKT02` — Thông điệp & Cấu trúc bán hàng)
* **Format:** Case (Phân tích trường hợp thực tế từ dữ liệu khách hàng)
* **Tệp người xem mục tiêu:** Creator, Chủ shop, Marketer hay bị bí câu mở đầu (Hook)
* **Mục tiêu Funnel:** Cân nhắc (Đẩy người xem nhận tài liệu mẫu trong Starter Kit)
* **Claim duy nhất:** Câu mở đầu giữ chân người xem tốt nhất không nằm trong đầu người viết, mà nằm nguyên văn trong tin nhắn than phiền hoặc bình luận hỏi thật của khách hàng.
* **Bằng chứng cần chuẩn bị:** Ảnh chụp màn hình 2 bình luận/tin nhắn thật của khách đã che tên & avatar (ví dụ: *"Mình quay bằng điện thoại cam sau nét lắm mà sao đăng lên TikTok cứ bị mờ đục với tối mặt vậy bạn?"*) và bảng biến đổi tin nhắn đó thành 3 góc Hook khác nhau.
* **CTA & Offer:** Nhận mẫu công thức chuyển hóa Hook trong **Starter Kit** ở bio.

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) + SFX / Nhịp |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03** *(Hook)* | Thành chỉ tay vào ảnh chụp màn hình một tin nhắn khách hàng (đã làm mờ tên) nổi lên giữa khung hình. | Đừng tự nghĩ hook, hãy **lấy từ tin nhắn** khách hàng | *(SFX: Tiếng thông báo tin nhắn Pop)* Mỗi lần bí câu mở đầu video, mình không ngồi vắt óc nghĩ chữ mới mà mở ngay hộp thư khách hàng. |
| **00:03 – 00:10** *(Proof / Tension)* | So sánh 2 câu mở đầu trên màn hình: Câu tự viết: *"Hướng dẫn cài đặt thông số quay video nét trên iPhone"* (màu xám nhạt) vs Câu từ tin nhắn thật: *"Quay cam sau thì nét mà đăng lên cứ bị mờ đục?"* (màu vàng sáng). | Ngôn ngữ sách vở **không chạm** được nỗi đau | Khi tự viết, chúng ta hay dùng từ chuyên môn kiểu "cách tối ưu thông số camera". Nhưng khách hàng ngoài đời không tìm cụm từ đó, họ chỉ hỏi: sao quay ở máy thì nét mà đăng lên lại bị mờ đục? |
| **00:10 – 00:18** *(Body - Bước 1)* | Trên màn hình Notion, Thành gạch chân 2 cụm từ khóa cảm xúc trong tin nhắn của khách: `"quay cam sau nét"` và `"đăng lên bị mờ đục"`. | Bước 1: Giữ nguyên **cụm từ mô tả lỗi** của khách | Từ một câu hỏi thật này, mình rút ra ba câu mở đầu khác nhau. Một là góc trực diện: dùng lại đúng cụm từ của khách — "Tại sao video nhìn trong máy rất nét nhưng đăng lên lại bị bệt màu?". |
| **00:18 – 00:25** *(Body - Bước 2)* | Viết tiếp dòng Hook số 2 kèm ví dụ visual 2 giây đặt 2 màn hình điện thoại cạnh nhau. | Bước 2: Đổi sang góc **phản trực giác** gây tò mò | Hai là góc phản trực giác để giữ chân người xem lâu hơn: "Quay 4K trên điện thoại chính là lý do khiến video của bạn bị mờ khi đăng lên mạng". |
| **00:25 – 00:32** *(Body - Bước 3)* | Viết tiếp dòng Hook số 3 kèm thao tác tắt nút HDR/60fps ngay giây đầu tiên. | Bước 3: Mở đầu bằng **hành động sửa lỗi** ngay lập tức | Ba là góc hành động: vừa vào video mình bấm tắt ngay một nút trong phần cài đặt camera rồi nói — "Tắt nút này trước khi quay nếu bạn không muốn video đăng lên bị tối mặt". |
| **00:32 – 00:40** *(Close & CTA)* | Quay về A-roll Thành. Phía trên hiện khung tổng hợp: 1 Comment thật -> 3 Hook (Đồng cảm / Phản trực giác / Hành động). | Lấy bảng **công thức 3 góc Hook** trong Starter Kit ở bio | Khách hàng đã viết hộ bạn câu mở đầu đắt giá nhất rồi, việc của bạn chỉ là đặt nó vào đúng ba giây đầu. Đó là cách mình dựng có chủ đích. Mình để sẵn bảng mẫu chuyển hóa câu hỏi khách hàng thành Hook trong Starter Kit ở bio, bạn vào lấy về dùng ngay nhé. |

### 3. Checklist Shot List cần quay / chụp
- [ ] **Graphic chuẩn bị:** Ảnh chụp màn hình comment/inbox thật của khách hàng (đã blur tên và ảnh đại diện sạch sẽ).
- [ ] **Screen Record:** Màn hình Notion/FigJam ghi rõ quá trình bóc từ khóa trong comment thật sang 3 câu Hook hoàn chỉnh.
- [ ] **B-roll minh họa:** Cảnh cầm điện thoại bấm tắt chế độ HDR Video trong Settings iPhone để minh họa cho Hook số 3.
- [ ] **A-roll:** Thành nói trực diện, nhịp giọng nhấn rõ sự đối lập giữa "ngôn ngữ người bán" và "ngôn ngữ người mua".

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
* **Caption TikTok:**
  Ngồi trước trang giấy trắng tự nghĩ câu mở đầu rất dễ rơi vào lối mòn giáo điều. Hãy mở ngay phần bình luận hoặc tin nhắn khách hàng từng hỏi bạn — kho câu Hook giữ chân người xem nằm hết ở đó.
  Mình để sẵn mẫu chuyển hóa câu hỏi khách hàng thành 3 dạng Hook trong Starter Kit ở bio, bạn vào lấy về dùng ngay.
  `#dungcochudich` `#videomarketing` `#hookvideo` `#contenttips`
* **Caption Facebook Reels:**
  Tại sao có những video vừa nghe câu đầu tiên người xem đã thấy "ơ đúng cái mình đang bị"? Vì câu mở đầu đó được lấy nguyên văn từ cách khách hàng than phiền chứ không phải từ sách vở marketing. Trong video là 3 bước mình biến 1 tin nhắn hỏi thật thành 3 góc mở bài khác nhau. Bạn vào Starter Kit ở bio để lấy file mẫu về áp dụng cho sản phẩm của mình nhé.

#### B. Bài đăng Facebook cá nhân (120–180 chữ)
Nhiều bạn khi bắt đầu làm video xây kênh hay hỏi mình: "Làm sao để viết được câu mở đầu nghe cuốn mà không bị sến hay giật tít quá đà?".

Kinh nghiệm của mình là: đừng cố sáng tác câu chữ mới, hãy đi lục lại tin nhắn của khách hàng hoặc phần bình luận dưới các bài viết cùng ngách. Người làm nghề hay mắc bệnh dùng từ chuyên môn (như "tối ưu bitrate", "cân bằng trắng", "cấu trúc chuyển đổi"), trong khi khách hàng chỉ nói đúng hiện tượng họ nhìn thấy bằng mắt thường ("sao đăng lên mặt cứ bị xám xịt vậy em?").

Mỗi khi tìm được 1 câu hỏi thật như vậy, mình luôn tách thành 3 hướng mở bài:
1. Hướng đồng cảm: Nhắc lại nguyên văn triệu chứng khách đang gặp trong 2 giây đầu.
2. Hướng phản trực giác: Chỉ ra thói quen tưởng là tốt nhưng lại gây ra lỗi đó (ví dụ: cứ bật 4K 60fps trong phòng thiếu sáng làm hình bị bệt).
3. Hướng hành động trực tiếp: Cho xem ngay thao tác sửa ở giây 01 rồi mới giải thích nguyên nhân.

Mình đã đóng gói bảng mẫu chuyển từ "Lời than phiền của khách -> 3 Câu Hook" trong bộ Starter Kit miễn phí trên bio. Bạn nào hay bí ý tưởng mở bài cứ vào lấy về dùng nhé.

---

## VIDEO #18 — MÃ C026: "Khi nào nên dùng adjustment layer?"

### 1. Thông tin định danh
* **Ngày đăng:** Thứ Ba, 24/11/2026 (Lịch cố định)
* **Pillar / Tuyến nội dung:** P2 - Edit & Storytelling (`EDIT02` — Quy trình dựng & Tối ưu Timeline)
* **Format:** Tutorial (Hướng dẫn thao tác thực tế giải quyết 1 tình huống cụ thể)
* **Tệp người xem mục tiêu:** Editor mới, Creator tự dựng video trên Premiere / CapCut PC
* **Mục tiêu Funnel:** Nhận biết (Nuôi dưỡng tệp học dựng video thực chiến)
* **Claim duy nhất:** Chỉ dùng Adjustment Layer khi bạn cần đồng bộ màu sắc hoặc tạo nhịp zoom chung cho một cụm cảnh liên tiếp mà vẫn giữ nguyên thông số gốc của từng clip bên dưới; lạm dụng nó cho từng clip lẻ chỉ làm timeline nặng và rối.
* **Bằng chứng cần chuẩn bị:** Project Premiere có 1 đoạn A-roll đã cắt nhỏ thành 6 clip liên tiếp: so sánh cách copy-paste hiệu ứng Lumetri/Transform vào từng clip (khi muốn sửa lại độ sáng phải sửa 6 lần) với việc đặt 1 lớp Adjustment Layer phủ đúng cụm đó + cảnh báo lỗi khi đặt Adjustment Layer đè lên cả Text/Logo làm biến dạng chữ.
* **CTA & Offer:** Theo dõi kênh để xem tiếp series tối ưu thao tác dựng (Offer: Không bán).

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) + SFX / Nhịp |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03** *(Hook)* | Quay màn hình Premiere: một lớp Adjustment Layer kéo dài phủ lên cả chữ phụ đề làm chữ bị ám vàng và méo góc khi zoom. | Dùng sai **Adjustment Layer** làm hỏng cả phụ đề | *(SFX: Tiếng chuông báo lỗi nhẹ)* Rất nhiều bạn mới học Premiere dùng Adjustment Layer theo thói quen mà không biết khi nào nên dùng, khi nào nên tránh. |
| **00:03 – 00:10** *(Proof / Tension)* | Cận cảnh timeline: Đoạn A-roll 20 giây đã bị cắt nhỏ thành 8 mảnh (do cắt bỏ chữ ờ, à). Khi chỉnh màu trực tiếp lên clip 1 rồi copy-paste sang 7 clip kia, lúc khách chê hơi tối lại phải ngồi sửa lại cả 8 mảnh. | Copy hiệu ứng vào từng mảnh làm **sửa bài cực lâu** | Giả sử bạn có một đoạn nói chuyện đã cắt bỏ khoảng nghỉ thành tám mảnh nhỏ. Nếu bạn chỉnh màu trực tiếp vào mảnh đầu rồi dán sang bảy mảnh còn lại, lúc cần hạ sáng một chút bạn sẽ phải làm lại tám lần. |
| **00:10 – 00:18** *(Body - Bước 1)* | Thao tác tạo 1 Adjustment Layer đặt ở Track V2, nằm ngay trên 8 mảnh A-roll ở V1, chỉ chỉnh Lumetri Color một lần trên lớp này. | Trường hợp 1: Đồng bộ màu cho **cụm cảnh cùng góc** | Đây là lúc Adjustment Layer phát huy tác dụng nhất. Bạn đặt một lớp phủ đúng lên cụm tám mảnh cùng góc máy đó ở track V2. Cần tăng sáng hay giảm vàng, bạn chỉ chỉnh đúng một chỗ. |
| **00:18 – 00:25** *(Body - Bước 2)* | Thao tác thêm hiệu ứng `Transform` lên một Adjustment Layer ngắn (2 giây) vắt ngang qua vết cắt giữa 2 clip để tạo cú Push-in (zoom nhẹ 100% -> 112%) liền mạch. | Trường hợp 2: Tạo nhịp **zoom bắc cầu** qua vết cắt | Trường hợp thứ hai là tạo chuyển động zoom bắc cầu qua hai clip liên tiếp mà không làm thay đổi thông số Scale gốc của từng clip bên dưới. |
| **00:25 – 00:32** *(Body - Bước 3)* | Chỉ rõ quy tắc sắp xếp Track: Track V1 (A-roll/B-roll) -> Track V2 (Adjustment Layer Màu/Zoom) -> Track V3 (Subtitles / Graphic / Logo). | Quy tắc: Luôn đặt **dưới track chữ** và đồ họa | Nhưng hãy nhớ một nguyên tắc sống còn: luôn đặt Adjustment Layer ở dưới track phụ đề và logo. Nếu bạn để nó ở track cao nhất, mỗi lần zoom hay chỉnh màu là chữ trên màn hình cũng bị biến dạng và sai màu theo. |
| **00:32 – 00:40** *(Close & CTA)* | Chạy lại 3 giây so sánh trước/sau khi xếp đúng thứ tự Track V1-V2-V3, sau đó về A-roll Thành chốt câu cuối. | **Theo dõi kênh** để xem tiếp series dựng thực chiến | Hiểu đúng bản chất công cụ giúp bạn thao tác ít hơn nhưng kiểm soát tốt hơn. Đó là cách mình dựng có chủ đích. Theo dõi kênh để xem tiếp các mẹo làm sạch quy trình dựng nhé. |

### 3. Checklist Shot List cần quay / chụp
- [ ] **Screen Record 1:** Minh họa lỗi đặt Adjustment Layer ở Track V4 (trên cùng) khiến Text ở V3 bị ám màu LUT và bị phóng to mất chữ ở mép khung hình.
- [ ] **Screen Record 2:** Thao tác đặt Adjustment Layer ở V2 (giữa Footage V1 và Text V3) để chỉnh màu Lumetri cho 8 clip cắt nhỏ cùng lúc.
- [ ] **Screen Record 3:** Thao tác đặt keyframe `Transform -> Scale 100% -> 112%` trên Adjustment Layer ngắn để tạo hiệu ứng push-in mượt qua điểm cắt.
- [ ] **A-roll:** Thành ngồi trước màn hình giải thích câu dẫn và câu kết.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
* **Caption TikTok:**
  Adjustment Layer không phải là thứ cứ mở project ra là kéo phủ từ đầu đến cuối. Dùng đúng 2 trường hợp này và đặt đúng thứ tự track sẽ giúp bạn chỉnh sửa nhanh hơn gấp nhiều lần mà không làm hỏng màu chữ.
  Theo dõi kênh để xem tiếp series tối ưu thao tác dựng thực chiến nhé.
  `#dungcochudich` `#premierepro` `#videotutorial` `#kinhnghiemedit`
* **Caption Facebook Reels:**
  Một lỗi nhỏ nhưng mình gặp rất nhiều khi nhận file project từ các bạn editor mới: để Adjustment Layer ở track cao nhất khiến toàn bộ phụ đề và logo thương hiệu bị ám màu theo video. Video này mình tóm gọn đúng 2 trường hợp nên dùng Adjustment Layer và vị trí track chuẩn nhất. Theo dõi mình để xem tiếp các bài hướng dẫn thực chiến nhé!

#### B. Bài đăng Facebook cá nhân (120–180 chữ)
Khi mới chuyển từ các phần mềm dựng cơ bản sang Premiere, nhiều bạn rất thích dùng Adjustment Layer vì cảm giác "chuyên nghiệp", cứ tạo một lớp kéo dài từ giây đầu đến giây cuối. Nhưng dùng không có quy tắc lại gây ra hai rắc rối lớn khi xuất file.

Thứ nhất là để lớp Adjustment Layer chỉnh màu và zoom nằm đè lên trên cả track phụ đề (Text) và Logo. Kết quả là màu thương hiệu của khách bị biến đổi theo LUT màu, còn chữ thì bị đẩy tràn ra khỏi vùng an toàn mỗi khi có nhịp zoom. Thứ hai là dùng chung một lớp cho cả cảnh quay trong nhà lẫn ngoài trời khiến màu sắc không đồng nhất.

Trong quy trình của mình, Adjustment Layer chỉ được dùng ở 2 vị trí:
1. Đặt ngay trên cụm A-roll cùng một góc máy đã bị cắt vụn (để chỉnh sáng/màu 1 lần thay vì copy-paste ra 10 mảnh).
2. Đặt một đoạn ngắn 2–3 giây vắt qua vết cắt giữa hai cảnh để tạo nhịp zoom nhẹ (push-in) mà không đụng vào thông số Scale gốc của clip.
3. Luôn khóa cố định: Track V1 là Footage, V2 là Adjustment Layer, từ V3 trở lên mới là Text và Graphic.

Hiểu đúng chức năng từng lớp giúp file project luôn nhẹ và sạch. Bạn nào đang học dựng nhớ lưu ý thứ tự track này nhé.

---

## VIDEO #19 — MÃ C044: "AI viết script nghe như máy, tôi sửa thế nào?"

### 1. Thông tin định danh
* **Ngày đăng:** Thứ Năm, 26/11/2026 (Lịch cố định)
* **Pillar / Tuyến nội dung:** P3 - AI trong workflow editor (`AI02` — AI hỗ trợ tiền kỳ, kịch bản & cấu trúc)
* **Format:** Before/after (So sánh trực tiếp văn bản AI gốc và bản đã biên tập sang văn nói)
* **Tệp người xem mục tiêu:** Creator, Chủ shop, Marketer đang dùng ChatGPT/Claude viết kịch bản nhưng đọc lên bị ngượng miệng
* **Mục tiêu Funnel:** Nhận biết -> Cân nhắc (Chứng minh khả năng kiểm soát chất lượng đầu ra của AI, dẫn về Zero To AI)
* **Claim duy nhất:** Kịch bản AI nghe như văn dịch vì nó thừa trạng từ chuyển tiếp, câu dài quá 20 chữ và nói chung chung; chỉ cần cắt hết từ nối sáo rỗng, tách câu theo nhịp thở 12 chữ và thay tính từ khen ngợi bằng một con số cụ thể là đọc lên tự nhiên ngay.
* **Bằng chứng cần chuẩn bị:** 1 đoạn kịch bản 3 câu do AI viết nguyên bản (ví dụ: *"Bạn có bao giờ cảm thấy vô cùng mệt mỏi khi phải dành hàng giờ đồng hồ để chỉnh sửa video? Trong kỷ nguyên số hiện nay, việc tối ưu hóa quy trình là chìa khóa vô cùng quan trọng..."*) và bản sửa trực tiếp từng dòng sang giọng nói thật của Thành.
* **CTA & Offer:** Nhận bộ câu lệnh rèn văn nói + Xem mục **Zero To AI** ở bio.

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) + SFX / Nhịp |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03** *(Hook)* | Thành cầm điện thoại đọc thử 1 câu văn AI với vẻ mặt cứng đờ: *"Bạn có bao giờ cảm thấy vô cùng mệt mỏi..."* rồi hạ điện thoại xuống lắc đầu. | Lý do kịch bản AI đọc lên **nghe như văn dịch** | *(SFX: Tiếng buzzer ngắn)* "Bạn có bao giờ cảm thấy vô cùng mệt mỏi..." — Chỉ cần nghe năm chữ đầu này là người xem biết ngay bạn đang đọc văn của AI. |
| **00:03 – 00:10** *(Proof / Tension)* | Quay màn hình đoạn script AI vừa xuất ra: Tô đỏ các cụm từ `"Bạn có bao giờ cảm thấy"`, `"vô cùng"`, `"Trong kỷ nguyên số hiện nay"`, `"tối ưu hóa toàn diện"`. | AI luôn lạm dụng **từ nối và tính từ rỗng** | Lỗi không phải vì AI dở, mà vì mặc định nó viết văn đọc bằng mắt chứ không phải văn nói bằng miệng. Câu dài ba mươi chữ và đầy những từ sáo rỗng mà ngoài đời không ai nói. |
| **00:10 – 00:18** *(Body - Bước 1)* | Thao tác xóa thẳng tay các cụm từ mở đầu rườm rà trên màn hình. Đổi câu *"Bạn có bao giờ mệt mỏi vì dựng video lâu?"* thành *"Dựng một clip 30 giây mà mất cả buổi tối thì chắc chắn quy trình đang kẹt ở một khâu."* | Bước 1: Gạch bỏ hoàn toàn **câu hỏi mồi sáo rỗng** | Trước khi thu âm, mình luôn sửa lại bản nháp AI qua ba bước. Một: gạch sạch các cụm "Bạn có bao giờ", "Trong thời đại hiện nay". Thay bằng một tình huống thật mà người xem vừa trải qua. |
| **00:18 – 00:25** *(Body - Bước 2)* | Trên màn hình, đổi cụm tính từ *"cải thiện tốc độ một cách đáng kinh ngạc"* thành con số cụ thể *"rút thời gian nhặt sườn bài từ 45 phút xuống còn 10 phút"*. | Bước 2: Thay tính từ khen bằng **con số đo được** | Hai: cứ thấy tính từ như "vô cùng hiệu quả", "nhanh chóng vượt trội" là mình xóa đi, thay bằng con số cụ thể. Ví dụ: giảm thời gian lọc sườn bài từ bốn mươi lăm phút xuống mười phút. |
| **00:25 – 00:32** *(Body - Bước 3)* | Thành dùng phím `/` ngắt câu dài thành các cụm ngắn 8–14 chữ, rồi đọc mẫu 1 câu sau khi sửa cực kỳ tự nhiên, đúng nhịp thở. | Bước 3: Ngắt câu dưới **mười lăm chữ** theo nhịp thở | Ba: đọc thành tiếng một lượt. Câu nào làm mình hụt hơi là phải tách đôi ngay, giữ mỗi câu dưới mười lăm chữ để khi lên hình nói như đang trò chuyện. |
| **00:32 – 00:40** *(Close & CTA)* | Màn hình hiển thị song song Bản AI thô (bên trái) và Bản đã biên tập văn nói (bên phải). Sau đó chuyển về A-roll Thành chốt bài. | Xem lộ trình làm chủ AI nội dung tại **Zero To AI** ở bio | Dùng AI để có sườn ý nhanh, nhưng câu chữ phát ra từ miệng phải mang hơi thở của bạn. Đó là cách mình dựng có chủ đích. Nếu bạn muốn học cách ứng dụng AI vào nội dung từ gốc theo lộ trình rõ ràng, xem mục Zero To AI ở bio của mình nhé. |

### 3. Checklist Shot List cần quay / chụp
- [ ] **A-roll:** Thành diễn lại 2 giây đọc văn mẫu AI ở đầu video + đoạn kết trực diện.
- [ ] **Screen Record 1:** Màn hình Google Docs / Notion hiển thị đoạn văn AI gốc với các cụm từ sáo rỗng được tô bút nhớ màu đỏ.
- [ ] **Screen Record 2:** Quá trình gõ sửa trực tiếp 3 bước (Xóa câu hỏi mồi -> Đổi tính từ thành con số phút -> Đánh dấu `/` ngắt nhịp câu dưới 15 từ).
- [ ] **Split-screen Card:** Khung so sánh Trước (38 chữ/đoạn văn dịch) vs Sau (24 chữ/văn nói gãy gọn).

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
* **Caption TikTok:**
  Đừng trách AI viết kịch bản nghe như google dịch nếu bạn lấy nguyên bản nháp đầu tiên của nó đem đi quay. Chỉ cần 3 phút biên tập lại theo quy tắc "xoá tính từ - thêm con số - ngắt nhịp thở" là kịch bản tự nhiên khác hẳn.
  Nếu bạn muốn học cách ứng dụng AI vào làm nội dung từ gốc theo lộ trình rõ ràng, xem mục Zero To AI ở bio của mình nhé.
  `#dungcochudich` `#aiscript` `#contentcreator` `#videomarketing`
* **Caption Facebook Reels:**
  Nhiều bạn dùng ChatGPT viết kịch bản xong lúc đứng trước ống kính cứ bị líu lưỡi vì câu văn dài lê thê, toàn những từ ngoài đời chẳng ai nói với nhau. Đây là 3 bước mình "gọt" lại mọi bản nháp của AI thành văn nói tự nhiên trước khi bấm máy. Bạn nào muốn học cách làm chủ AI bài bản từ gốc thì xem mục Zero To AI ở bio của mình nhé.

#### B. Bài đăng Facebook cá nhân (120–180 chữ)
Có một dấu hiệu rất dễ nhận ra ở những video dùng kịch bản AI nguyên bản 100%: người nói trên hình cứ bị hụt hơi, còn câu chữ thì đầy những cụm kiểu "Bạn có bao giờ cảm thấy vô cùng bối rối...", "Trong kỷ nguyên số hóa hiện nay...", "Giải pháp toàn diện vượt trội".

Văn viết để đọc bằng mắt khác hoàn toàn với văn nói để nghe bằng tai. AI rất giỏi gom ý và sắp xếp bố cục logic (giúp mình tiết kiệm khoảng 15–20 phút ngồi nhìn trang giấy trắng), nhưng nếu bê nguyên văn bản đó lên đọc trước camera thì người xem sẽ thấy xa cách ngay.

Mỗi khi nhận bản nháp từ AI, mình luôn dành 5 phút chạy bộ lọc 3 bước bằng tay:
1. Cắt bỏ toàn bộ câu mở đầu mồi cảm xúc sáo rỗng, đi thẳng vào tình huống thực tế ở câu thứ hai.
2. Xóa sạch các trạng từ và tính từ tán dương ("cực kỳ", "đáng kinh ngạc", "tuyệt vời"), ép mình phải thay bằng một hành động hoặc con số cụ thể.
3. Đọc to thành tiếng một lượt: bất kỳ câu nào dài quá một hơi thở (trên 16 chữ) đều phải ngắt thành hai câu ngắn.

Ảnh dưới là một đoạn kịch bản trước và sau khi mình gọt lại. Bạn nào muốn học cách ứng dụng AI vào nội dung từ gốc theo lộ trình rõ ràng thì xem mục Zero To AI ở bio của mình nhé.

---

## VIDEO #20 — MÃ C057: "30 ngày học motion: tiến bộ nào nhìn thấy được?"

### 1. Thông tin định danh
* **Ngày đăng:** Thứ Bảy, 28/11/2026 (Lịch linh hoạt)
* **Pillar / Tuyến nội dung:** P4 - Hành trình & Bằng chứng (`JRN02` — Quá trình rèn luyện kỹ năng thực tế)
* **Format:** Progress (So sánh tiến độ thực tế Ngày 1 vs Ngày 30 — Build in Public)
* **Tệp người xem mục tiêu:** Editor mới, người tự học dựng video và motion graphics cơ bản
* **Mục tiêu Funnel:** Tin cậy (Xây dựng sự đồng cảm và uy tín thật qua quá trình tự rèn nghề, không tô hồng)
* **Claim duy nhất:** Sau 30 ngày tự luyện motion phục vụ video marketing, sự khác biệt lớn nhất không phải là làm được hiệu ứng phức tạp hơn, mà là biết chỉnh đồ thị tốc độ (Speed Graph) mượt mắt và dám bỏ bớt chuyển động thừa để người xem tập trung vào chữ chính.
* **Bằng chứng cần chuẩn bị:** Hai file output thực tế của Thành: Output Ngày 1 (chuyển động Linear đều tăm tắp, cứng nhắc, 4–5 phần tử bay ra từ tứ phía cùng lúc gây loạn mắt) vs Output Ngày 30 (chỉ 2 nhịp chuyển động có Speed Graph nhanh đầu - êm cuối, mắt người xem được dẫn từ con số chính sang dòng kết luận).
* **CTA & Offer:** Lưu lại hành trình / kinh nghiệm để tự đối chiếu khi luyện tập (Offer: Không bán).

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) + SFX / Nhịp |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03** *(Hook)* | Màn hình chia đôi chạy song song 2 đoạn animation 3 giây: Bên trái là Ngày 1 (cứng, giật, rối mắt), bên phải là Ngày 30 (mượt, có điểm rơi dứt khoát). | Khác biệt thật sự sau **30 ngày** tự rèn motion | *(SFX: Tiếng chuyển động mượt Whoosh trầm)* Đây là cảnh motion mình dựng ở ngày đầu tiên, và đây là kết quả sau đúng ba mươi ngày tự luyện mỗi tối. |
| **00:03 – 00:10** *(Proof / Tension)* | Zoom vào bản Ngày 1: Mở keyframe Linear (hình thoi mặc định) và chỉ vào 4 icon bay vào cùng lúc khiến người xem không biết phải nhìn vào đâu. | Ngày 1: Keyframe đều tăm tắp và **tham hiệu ứng** | Nhìn lại bài ngày một, mình mắc đúng hai lỗi của người mới. Một là để keyframe mặc định nên hình trôi đều như robot. Hai là cái gì cũng bắt nó bay lượn làm người xem hoa mắt. |
| **00:10 – 00:18** *(Body - Điểm tiến bộ 1)* | Quay màn hình mở bảng Graph Editor (Speed Graph): So sánh đường thẳng ngang của Ngày 1 với đường cong có đỉnh nhọn lệch trái (nhanh ở đầu, hãm êm ở cuối) của Ngày 30. | Thay đổi 1: Làm chủ **đồ thị tốc độ** thay vì dùng preset | Sau ba mươi ngày, có ba thứ thay đổi rõ nhất. Đầu tiên là đồ thị tốc độ. Thay vì ném preset có sẵn vào, mình tự kéo đường cong để vật thể lao vào nhanh rồi phanh êm lại đúng nhịp nói. |
| **00:18 – 00:25** *(Body - Điểm tiến bộ 2)* | Minh họa trên bản Ngày 30: Khung nền hiện ra trước (frame 01–08) -> Con số `35%` bật lên ở frame 09 -> Mũi tên chỉ dẫn chạy ra ở frame 15. | Thay đổi 2: Xếp thứ tự xuất hiện để **dẫn mắt người xem** | Thứ hai là thứ tự xuất hiện. Ngày trước mình cho năm thứ hiện ra cùng một frame. Giờ mình tách lệch nhau vài frame để mắt người xem đọc lần lượt từ khung nền, tới con số, rồi mới tới kết luận. |
| **00:25 – 00:32** *(Body - Điểm tiến bộ 3)* | So sánh thời lượng làm việc: Ngày 1 mất 2 tiếng cho 5 giây rối rắm; Ngày 30 mất 25 phút cho 5 giây gọn gàng, phục vụ đúng câu thoại. | Thay đổi 3: Bớt hiệu ứng thừa để **làm nổi thông điệp** | Và thay đổi lớn nhất là mình biết dừng lại. Cái gì không giúp câu thoại rõ nghĩa hơn thì mình để đứng yên, không cố nhồi thêm chuyển động chỉ để khoe kỹ thuật. |
| **00:32 – 00:40** *(Close & CTA)* | Chạy lại toàn màn hình đoạn Ngày 30 kết hợp với giọng đọc trong video thật, sau đó về A-roll Thành mỉm cười nhẹ nhàng. | **Lưu lại** ba điểm này nếu bạn cũng đang tự luyện | Ba mươi ngày chưa biến mình thành motion designer chuyên sâu, nhưng đủ để các đoạn giải thích trong video marketing gọn và có điểm nhấn hơn. Đó là cách mình dựng có chủ đích. Bạn lưu lại ba điểm này nếu cũng đang tự rèn kỹ năng mỗi ngày nhé. |

### 3. Checklist Shot List cần quay / chụp
- [ ] **Export 2 Output:** Render file `Day_01_Motion.mp4` (keyframe hình thoi Linear, nhiều icon bay loạn) và `Day_30_Motion.mp4` (Speed graph mượt, phân cấp thông tin rõ) đặt cạnh nhau.
- [ ] **Screen Record 1:** Mở cửa sổ Graph Editor trong Premiere / After Effects, kéo trực tiếp tay cầm Bezier để thấy sự thay đổi tốc độ chuyển động.
- [ ] **Screen Record 2:** Zoom vào timeline của cảnh Ngày 30 cho thấy các layer được xếp bậc thang (staggered layers) lệch nhau 4–6 frames.
- [ ] **A-roll:** Thành chia sẻ chân thật tại góc làm việc buổi tối (ánh đèn bàn ấm áp, đúng tinh thần nhật ký rèn nghề).

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
* **Caption TikTok:**
  30 ngày tự luyện motion mỗi tối không biến mình thành dân chuyên hiệu ứng phức tạp, nhưng giúp mình sửa được căn bệnh "cái gì cũng bắt nó bay" của người mới.
  Lưu lại 3 thay đổi cốt lõi này để rút ngắn thời gian tự học của bạn nhé.
  `#dungcochudich` `#hoceditvideo` `#motiongraphics` `#buildinpublic`
* **Caption Facebook Reels:**
  Hồi mới tập làm mấy đoạn chữ và biểu đồ chuyển động cho video marketing, mình cứ nghĩ càng nhiều thứ bay nhảy trên màn hình thì nhìn càng "đắt tiền". Sau 30 ngày tự gọt giũa, mình nhận ra sự tinh tế nằm ở đồ thị tốc độ (Speed Graph) và thứ tự dẫn mắt người xem. Bạn nào đang tự học dựng video lưu lại 3 điểm này để đỡ mất thời gian mò mẫm nhé!

#### B. Bài đăng Facebook cá nhân (120–180 chữ)
Hôm nay mình ngồi mở lại file project luyện tập cách đây tròn 1 tháng để tự đối chiếu xem 30 ngày qua tay nghề thay đổi ở đâu.

Ở ngày đầu tiên, một đoạn đồ họa giải thích dài 5 giây làm mình mất gần 2 tiếng đồng hồ. Lúc đó tâm lý của người mới là sợ khung hình đơn điệu, nên có bao nhiêu chữ, mũi tên, icon là mình cho bay vào cùng một lúc với tốc độ trượt đều tăm tắp. Xem lại thấy rất mệt mắt mà chẳng đọng lại được chữ nào.

Sau 30 ngày kiên trì luyện mỗi tối một đoạn ngắn phục vụ cho video marketing, 3 tiến bộ mình nhìn thấy rõ nhất bằng mắt thường là:
1. Không còn dùng keyframe mặc định (Linear) hay phụ thuộc hoàn toàn vào preset, mà tập chỉnh đồ thị tốc độ (Speed Graph) để chuyển động lao vào dứt khoát rồi hãm êm ở cuối.
2. Biết xếp các lớp (layer) lệch nhau 4–6 frame theo hình bậc thang để dẫn mắt người xem đọc đúng thứ tự từ ý chính đến ý phụ.
3. Dám cắt bỏ 50% các chuyển động trang trí không phục vụ cho thông điệp bán hàng (nhờ vậy thời gian dựng 1 cụm đồ họa giảm xuống còn khoảng 20–25 phút).

Mình để видео so sánh Ngày 1 và Ngày 30 ở dưới. Anh em nào đang tự rèn thêm kỹ năng mới cứ lưu lại đối chiếu cùng mình nhé.

---

# PHẦN IV: KỊCH BẢN SẢN XUẤT CHI TIẾT TUẦN 6 (30/11/2026 – 05/12/2026)

---

## VIDEO #21 — MÃ C008: "Brief nói nhiều nhưng video cần nói một điều"

### 1. Thông tin định danh
* **Ngày đăng:** Thứ Hai, 30/11/2026 (Lịch cố định)
* **Pillar / Tuyến nội dung:** P1 - Marketing trong video (`MKT02` — Thông điệp & Cấu trúc bán hàng)
* **Format:** BTS (Behind The Scenes — Hậu trường xử lý đề bài thật của khách hàng)
* **Tệp người xem mục tiêu:** Khách hàng tiềm năng (Chủ shop, Founder, Brand Manager cần thuê dựng video hiểu marketing)
* **Mục tiêu Funnel:** Tin cậy -> Chuyển đổi (Chứng minh quy trình làm việc có tư duy lọc thông điệp trước khi chạm vào phần mềm dựng)
* **Claim duy nhất:** Khi khách gửi một trang brief dài hai mặt giấy, việc đầu tiên của một Marketing Video Editor không phải là mở Premiere lên cắt cảnh, mà là rút gọn cả trang giấy đó về đúng 1 câu thông điệp xương sống dưới 15 chữ.
* **Bằng chứng cần chuẩn bị:** 1 bản Google Docs Brief thật của khách hàng (đã ẩn tên thương hiệu và thông tin nhạy cảm) dài khoảng 1,5 trang A4 liệt kê đủ lịch sử công ty, 6 tính năng sản phẩm, 3 tệp khách hàng -> Màn hình khung lọc "1 Câu Xương Sống" của Thành trước khi vào timeline.
* **CTA & Offer:** Nhắn chữ `EDIT` hoặc gửi brief để trao đổi hướng dựng (Offer: Dịch vụ Edit/Media).

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) + SFX / Nhịp |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03** *(Hook)* | Quay cận cảnh màn hình: trang Google Docs brief của khách dài kín 2 trang giấy (đã làm mờ logo), bên cạnh là tờ giấy note chỉ ghi đúng 1 câu ngắn. | Brief dài hai trang nhưng video chỉ nói **một điều** | *(SFX: Tiếng giấy lật nhanh)* Khách gửi cho mình một bản brief dài hai trang A4, nhưng video hoàn chỉnh chỉ dài đúng ba mươi lăm giây. |
| **00:03 – 00:10** *(Proof / Tension)* | Cuộn nhanh qua bản brief đã che tên: mục nào cũng ghi "Quan trọng" — từ lịch sử thương hiệu 5 năm, quy trình kiểm định, 6 thành phần cho tới chương trình khuyến mãi. | Đưa hết vào video sẽ thành **bài đọc quảng cáo** | Nếu mình bê nguyên cả sáu gạch đầu dòng này vào timeline, video sẽ biến thành một bài thuyết trình đọc vội. Người xem lướt qua ngay vì không thấy điểm nào liên quan trực tiếp tới họ. |
| **00:10 – 00:18** *(Body - Bước 1)* | Thành ngồi trước màn hình (BTS góc nghiêng), dùng chuột bôi vàng duy nhất 1 dòng trong mục Khách hàng mục tiêu: *"Dân văn phòng hay bị đau mỏi cổ vai gáy lúc 3 giờ chiều"*. | Bước 1: Tìm đúng **một khoảnh khắc đau** của khách | Trước khi mở Premiere, mình luôn lọc brief qua ba câu hỏi. Một: khách hàng cần sản phẩm này nhất vào khoảnh khắc nào? Ở đây mình chỉ giữ lại chi tiết mỏi cổ lúc ba giờ chiều tại văn phòng. |
| **00:18 – 00:25** *(Body - Bước 2)* | Trên đầu trang brief, Thành gõ vào ô đóng khung đỏ câu thông điệp xương sống: *"Giải tỏa căng cứng cổ vai ngay tại ghế làm việc trong 10 phút nghỉ giải lao"*. | Bước 2: Chốt **một câu xương sống** dưới mười lăm chữ | Hai: mình tóm toàn bộ hai trang giấy thành một câu xương sống dưới mười lăm chữ. Mọi cảnh quay không phục vụ cho câu "giảm mỏi cổ ngay tại ghế văn phòng" mình đều xin phép khách cắt bỏ. |
| **00:25 – 00:32** *(Body - Bước 3)* | Mở timeline Premiere của dự án đó: chỉ vào các phần thông tin phụ (chứng nhận, bảo hành 12 tháng) được chuyển thành dòng text nhỏ ở góc dưới thay vì đọc thành lời. | Bước 3: Chuyển thông tin phụ sang **chữ hiển thị nhỏ** | Ba: những thông tin phụ như chế độ bảo hành mười hai tháng, mình không bắt giọng đọc phải gồng lên nói hết, mà đặt thành dòng chữ nhỏ gọn ở ba giây cuối. |
| **00:32 – 00:40** *(Close & CTA)* | Quay về A-roll Thành nhìn thẳng ống kính, phía sau là màn hình ghép bản Brief gốc và Timeline gọn gàng. | Nhắn **EDIT** kèm brief nếu bạn cần dựng đúng trọng tâm | Một người dựng có tư duy marketing sẽ giúp bạn gạn đục khơi trong trước khi cắt cảnh đầu tiên. Đó là cách mình dựng có chủ đích. Nếu bạn đang có sẵn brief và footage nhưng chưa biết gọt thông điệp sao cho gọn, nhắn chữ EDIT cho mình nhé. |

### 3. Checklist Shot List cần quay / chụp
- [ ] **Screen Record 1:** Bản Brief Google Docs thật (đã thay tên thương hiệu bằng `[Thương hiệu A]` và làm mờ số liệu nội bộ) cuộn từ trang 1 xuống trang 2.
- [ ] **Screen Record 2:** Thao tác highlight màu vàng vào đúng 1 dòng insight và gõ câu "Thông điệp xương sống" vào khung đầu trang.
- [ ] **Screen Record 3:** Màn hình Premiere cho thấy cách đưa thông tin phụ ("Bảo hành 1 đổi 1 trong 12 tháng") thành dòng badge text gọn ở góc dưới thay vì đọc thoại.
- [ ] **A-roll BTS:** Cảnh Thành ngồi đọc brief, ghi chú nhanh ra sổ tay rồi quay sang nói trực diện với camera.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
* **Caption TikTok:**
  Khách hàng thương sản phẩm nên cái gì cũng muốn đưa vào brief, nhưng người xem trên mạng chỉ cho bạn 3 giây để trả lời câu hỏi "Cái này giải quyết được việc gì cho tôi?".
  Nếu bạn đang có sẵn đề bài và footage nhưng cần một người dựng biết lọc đúng trọng tâm bán hàng, nhắn chữ "EDIT" cho mình nhé.
  `#dungcochudich` `#marketingvideo` `#videoeditor` `#behindthescenes`
* **Caption Facebook Reels:**
  Đây là việc mình luôn làm 15 phút trước khi bắt đầu dựng bất kỳ dự án nào cho khách: rút một bản đề bài (brief) dài 2 trang giấy thành đúng 1 câu thông điệp xương sống. Khi trục chính đã rõ, việc chọn cảnh đầu tiên và cắt bỏ cảnh thừa trở nên cực kỳ dứt khoát. Nếu bạn cần tìm người đồng hành dựng video hiểu rõ mục tiêu marketing, nhắn chữ "EDIT" cho mình nhé.

#### B. Bài đăng Facebook cá nhân (120–180 chữ)
Khi làm việc với các chủ shop hoặc anh chị phụ trách nhãn hàng, mình rất hiểu tâm lý: vì quá tâm huyết với sản phẩm nên khi viết brief gửi cho editor, anh chị thường liệt kê đủ 7–8 gạch đầu dòng từ lịch sử xưởng, nguyên liệu nhập khẩu, quy trình 5 bước cho đến chính sách bảo hành.

Nhưng nếu người dựng chỉ làm đúng chức năng "thợ cắt ghép" — tức là trong brief có bao nhiêu chữ thì cố nhét bấy nhiêu cảnh vào 40 giây — thì video ra lò sẽ giống hệt một tờ rơi biết nói. Người xem bị ngợp thông tin và lướt qua ngay.

Trong quy trình nhận bài của mình, bước đầu tiên không bao giờ là mở phần mềm dựng, mà là ngồi lọc lại brief cùng khách:
1. Chọn ra đúng 1 bối cảnh sử dụng đắt giá nhất trong cả trang giấy để đưa lên 3 giây đầu.
2. Viết lại "1 câu thông điệp xương sống" (dưới 15 chữ) ở ngay đầu timeline. Cảnh nào không chứng minh cho câu này thì mạnh dạn cất đi dành cho video sau.
3. Chuyển các thông số kỹ thuật và chế độ bảo hành thành chữ hiển thị (on-screen text) ở cuối bài để giữ cho lời thoại luôn gọn và giàu cảm xúc.

Nếu bạn đã có sẵn nguồn quay và đề bài nhưng muốn video lên hình đi thẳng vào lý do mua hàng, nhắn chữ "EDIT" kèm mục tiêu video cho mình nhé.

---

## VIDEO #22 — MÃ C009: "CTA theo dõi không phù hợp mọi video"

### 1. Thông tin định danh
* **Ngày đăng:** Thứ Ba, 01/12/2026 (Lịch cố định)
* **Pillar / Tuyến nội dung:** P1 - Marketing trong video (`MKT03` — Tối ưu điểm chạm & Kêu gọi hành động CTA)
* **Format:** Talking head (Nói trực diện kết hợp bảng Mapping trực quan trên màn hình)
* **Tệp người xem mục tiêu:** Creator xây kênh cá nhân, Chủ shop, Marketer
* **Mục tiêu Funnel:** Nhận biết (Tạo lượt lưu cao và điều hướng người xem tải bảng Mapping CTA trong Starter Kit)
* **Claim duy nhất:** Kết thúc mọi video bằng câu "Hãy bấm nút theo dõi kênh nhé" là sự lãng phí lưu lượng; mỗi dạng nội dung phải đi kèm đúng một hành động tự nhiên nhất với tâm lý người xem ở giây cuối cùng.
* **Bằng chứng cần chuẩn bị:** Bảng Mapping 3 cột (Loại video -> Tâm lý người xem sau khi xem xong -> Câu CTA chuyển đổi cao nhất) hiển thị rõ trên màn hình Notion/FigJam.
* **CTA & Offer:** Lưu lại bảng Mapping CTA hoặc tải trọn bộ trong **Starter Kit** ở bio.

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) + SFX / Nhịp |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03** *(Hook)* | Thành nói trực diện, tay phải đưa lên gạt nhẹ dòng chữ mẫu *"Nhớ bấm Follow mình nhé!"* đang bay ngang màn hình. | Đừng kết thúc mọi video bằng câu **bấm theo dõi** | *(SFX: Tiếng gạt giấy Whoosh)* Nếu cuối video nào bạn cũng nói "nhớ bấm theo dõi kênh của mình nhé", bạn đang bỏ phí hơn một nửa cơ hội chuyển đổi. |
| **00:03 – 00:10** *(Proof / Tension)* | Hiện biểu đồ/con số minh họa sự lệch pha: Người xem vừa xem xong 1 mẹo sửa lỗi kỹ thuật -> họ sợ quên công thức chứ chưa có nhu cầu theo dõi con người bạn. | Kêu gọi lệch tâm lý khiến người xem **bỏ qua** | Lý do rất đơn giản: người lạ mới xem một video của bạn chưa đủ gắn kết để bấm theo dõi ngay. Họ chỉ hành động khi lời kêu gọi khớp đúng với thứ họ đang cần ở giây cuối cùng. |
| **00:10 – 00:18** *(Body - Nhóm 1)* | Trên màn hình hiện dòng 1 của Bảng Mapping: `Video chỉ lỗi / Mẹo thao tác` -> Tâm lý: *"Sợ lúc làm bị quên"* -> CTA chuẩn: **Lưu lại video**. | Nhóm 1: Video sửa lỗi cụ thể -> Kêu gọi **Lưu bài** | Trong hệ thống của mình, mình chia CTA theo ba mục tiêu rõ ràng. Một: với video chỉ lỗi hoặc hướng dẫn thao tác nhanh, hãy bảo họ lưu lại để mở ra đối chiếu lúc làm thật. |
| **00:18 – 00:25** *(Body - Nhóm 2)* | Hiện tiếp dòng 2 của Bảng Mapping: `Video quy trình / Framework nhiều bước` -> Tâm lý: *"Muốn có sẵn file mẫu để điền vào"* -> CTA chuẩn: **Nhận tài liệu ở Bio**. | Nhóm 2: Video quy trình -> Kêu gọi **Nhận biểu mẫu** | Hai: với video chia sẻ quy trình hay khung kịch bản, người xem ngại tự kẻ bảng lại từ đầu. Hãy mời họ vào bio lấy biểu mẫu làm sẵn về dùng ngay. |
| **00:25 – 00:32** *(Body - Nhóm 3)* | Hiện tiếp dòng 3 của Bảng Mapping: `Video phân tích Case Study / Sửa bài thật` -> Tâm lý: *"Mình cũng đang gặp y hệt ca này"* -> CTA chuẩn: **Nhắn từ khóa riêng**. | Nhóm 3: Video sửa bài thật -> Kêu gọi **Nhắn từ khóa** | Ba: chỉ khi nào bạn chiếu ca sửa bài thực tế trước và sau cho khách, lúc đó mới kêu gọi người đang gặp vấn đề tương tự nhắn một từ khóa cụ thể để làm việc cùng bạn. |
| **00:32 – 00:40** *(Close & CTA)* | Hiển thị trọn vẹn Bảng Mapping 3 nhóm trên màn hình 3 giây để người xem chụp/lưu, sau đó về A-roll Thành chốt câu kết. | Lưu **bảng phân loại CTA** hoặc lấy trong Starter Kit ở bio | Đúng người, đúng nội dung nhưng phải đúng cả lời mở lời ở giây cuối cùng. Đó là cách mình dựng có chủ đích. Bạn lưu lại bảng này hoặc lấy bản đầy đủ trong Starter Kit ở bio của mình nhé. |

### 3. Checklist Shot List cần quay / chụp
- [ ] **A-roll chính:** Thành ngồi góc chính diện (Talking head), ánh sáng rõ nét, chừa khoảng trống 1/3 phía trên đầu hoặc bên cạnh để chèn bảng Mapping trực quan.
- [ ] **Graphic / Screen Record:** Bảng Mapping CTA thiết kế sạch sẽ trên nền tối hoặc giấy sáng (3 hàng x 3 cột: Loại video - Tâm lý người xem - Mẫu câu CTA hoàn chỉnh).
- [ ] **Insert B-roll:** Cận cảnh trang `Funnel & CTA` trong bộ Starter Kit của Thành để tăng tính thuyết phục "mình đang dùng chính bảng này".

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
* **Caption TikTok:**
  Không phải video nào cũng nên kết thúc bằng câu "hãy bấm follow kênh". Chọn đúng hành động khớp với tâm lý người xem ở giây thứ 35 mới là thứ giúp video vừa có tương tác thật vừa ra được khách hàng.
  Bạn lưu lại bảng phân loại CTA này hoặc vào Starter Kit ở bio lấy bản đầy đủ về dùng nhé.
  `#dungcochudich` `#videomarketing` `#xaykenhtiktok` `#contentstrategy`
* **Caption Facebook Reels:**
  Rất nhiều bạn làm nội dung xong đến 3 giây cuối lại buột miệng nói một câu CTA theo quán tính: "Like và follow mình nhé". Thực tế, mỗi định dạng video phục vụ một tầng tâm lý hoàn toàn khác nhau. Mình tổng hợp lại bảng ghép cặp giữa "Loại video" và "Câu kêu gọi hành động" hiệu quả nhất trong clip này. Lưu lại hoặc lấy file chi tiết trong Starter Kit ở bio nhé!

#### B. Bài đăng Facebook cá nhân (120–180 chữ)
Khi rà soát lại kịch bản cho các kênh cá nhân và kênh bán hàng, phần bị viết qua loa nhất hầu như luôn là 5 giây cuối cùng (CTA - Kêu gọi hành động). Quán tính chung của chúng ta là viết thật kỹ phần mở bài, rồi đến cuối lại chốt một câu quen thuộc: "Nếu thấy hay hãy bấm like và theo dõi kênh nhé".

Nhưng trên thực tế, một người lạ vừa xem xong video 35 giây của bạn rất hiếm khi bấm theo dõi chỉ vì bạn nhắc. Họ chỉ làm theo lời gợi ý khi hành động đó mang lại lợi ích ngay lập tức cho chính họ:
1. Nếu video vừa chỉ ra 3 bước sửa một lỗi kỹ thuật: tâm lý người xem là sợ đến lúc mở máy lên làm sẽ quên -> Hãy nhắc họ "Lưu lại video này để đối chiếu khi dựng bài tối nay".
2. Nếu video chia sẻ một khung tư duy hoặc bảng kế hoạch: tâm lý người xem là muốn có sẵn mẫu để đỡ phải kẻ lại -> Hãy mời họ nhận file mẫu ở bio.
3. Nếu video là ca sửa bài (Audit / Case study) trước và sau: lúc này niềm tin đã có -> Hãy mời những ai đang kẹt ở tình huống tương tự nhắn một từ khóa riêng để trao đổi.

Mình để bảng ghép cặp CTA chi tiết trong bộ Starter Kit miễn phí trên bio, bạn nào đang xây kênh vào lấy về đối chiếu nhé.

---

## VIDEO #23 — MÃ C027: "Cách dựng phiên bản dọc từ footage ngang"

### 1. Thông tin định danh
* **Ngày đăng:** Thứ Năm, 03/12/2026 (Lịch cố định)
* **Pillar / Tuyến nội dung:** P2 - Edit & Storytelling (`EDIT02` — Quy trình dựng & Tối ưu Timeline)
* **Format:** Tutorial (Hướng dẫn kỹ thuật kết hợp bố cục thị giác)
* **Tệp người xem mục tiêu:** Creator, Chủ shop, Editor cần cắt video ngắn (TikTok/Reels/Shorts) từ nguồn quay ngang 16:9 (YouTube, Podcast, Sự kiện, TVC)
* **Mục tiêu Funnel:** Nhận biết -> Cân nhắc (Thu hút người xem tải Checklist/Khung Safe Zone trong Starter Kit)
* **Claim duy nhất:** Chuyển video ngang 16:9 sang dọc 9:16 không phải là bấm Auto Reframe cho máy tự cắt hay chèn hai dải mờ (blur) trên dưới trông cũ kỹ, mà là chia lại tỷ lệ khung hình theo vai trò của cảnh và đặt chữ đúng vùng an toàn.
* **Bằng chứng cần chuẩn bị:** 1 footage quay ngang 16:9 (4K hoặc 1080p) có cảnh nói chuyện 2 người hoặc cảnh giới thiệu sản phẩm trên bàn -> So sánh 3 cách xử lý: (1) Để dải mờ trên dưới kiểu cũ, (2) Phóng to toàn khung 9:16 cho cảnh cận, và (3) Bố cục Split-screen trên/dưới (cảnh toàn + cảnh cận hoặc màn hình minh họa) kèm khung lưới Safe Zone TikTok.
* **CTA & Offer:** Nhận khung Safe Zone 9:16 và Checklist dựng video dọc trong **Starter Kit** ở bio.

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) + SFX / Nhịp |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03** *(Hook)* | So sánh 2 khung hình dọc 9:16 trên màn hình: Bên trái là video ngang đặt giữa kèm 2 vệt mờ (blur) trên dưới lỗi thời; bên phải là khung hình dọc tràn viền sắc nét, bố cục chia tầng hiện đại. | Đừng chèn **hai dải mờ** khi cắt video ngang sang dọc | *(SFX: Tiếng xé giấy / Swipe nhanh)* Khi cắt một video quay ngang sang khổ dọc đăng TikTok, cách làm giảm giá trị hình ảnh nhất là chèn hai dải làm mờ ở trên và dưới như thế này. |
| **00:03 – 00:10** *(Proof / Tension)* | Chỉ vào khung hình có 2 dải blur: diện tích hình thật chỉ còn chiếm 1/3 màn hình điện thoại, chữ đè lên vùng giao diện của TikTok làm người xem phải nheo mắt. | Hình chính bị **bé tí** trên màn hình điện thoại | Kiểu chèn nền mờ này làm khung hình chính bị thu nhỏ còn một phần ba màn hình điện thoại, nhìn vừa cũ vừa không giữ được sự tập trung của người xem. |
| **00:10 – 00:18** *(Body - Cách 1)* | Quay màn hình Premiere: Với cảnh 1 người nói quay ở độ phân giải 4K, phóng Scale lên tràn khung 9:16, đặt hai mắt nhân vật nằm đúng đường kẻ 1/3 trên. | Cách 1: Phóng tràn khung và khóa **trục mắt một phần ba** | Tùy vào góc quay gốc, mình dùng ba cách xử lý sạch hơn nhiều. Một: nếu file gốc quay 4K đủ nét, hãy phóng tràn khung dọc và căn hai mắt nhân vật nằm đúng đường một phần ba trên. |
| **00:18 – 00:25** *(Body - Cách 2)* | Với cảnh 2 người đối thoại hoặc vừa nói vừa thao tác tay trên bàn: Chia khung 9:16 thành 2 nửa trên/dưới (Trên là cận mặt người nói, dưới là cận tay/sản phẩm hoặc người nghe). | Cách 2: Chia đôi **trên và dưới** khi có hai chủ thể | Hai: nếu góc ngang có hai người nói chuyện hoặc có cảnh thao tác tay trên bàn, đừng cố lia qua lia lại. Hãy nhân đôi layer, nửa trên lấy cận mặt người nói, nửa dưới lấy cận tay thao tác. |
| **00:25 – 00:32** *(Body - Cách 3)* | Bật lớp Overlay PNG "TikTok/Reels Safe Zone" màu đỏ mờ đè lên Program Monitor để kiểm tra vị trí đặt phụ đề (nằm ở khoảng 1/3 dưới nhưng trên vùng caption của app). | Cách 3: Bật **khung vùng an toàn** trước khi đặt chữ | Ba: luôn bật lớp khung vùng an toàn trước khi đặt phụ đề. Tuyệt đối không đặt chữ sát đáy hoặc sát mép phải vì sẽ bị nút tim và phần mô tả của nền tảng che khuất. |
| **00:32 – 00:40** *(Close & CTA)* | Chạy 3 giây kết quả video dọc hoàn chỉnh (chuyển mượt từ cảnh phóng tràn khung sang cảnh chia đôi trên/dưới), rồi về A-roll Thành chốt bài. | Lấy **khung Safe Zone** và checklist trong Starter Kit ở bio | Tái sử dụng nguồn quay ngang rất tiết kiệm, miễn là bạn dựng lại bố cục cho vừa mắt người dùng điện thoại. Đó là cách mình dựng có chủ đích. File khung vùng an toàn và checklist dựng dọc mình để sẵn trong Starter Kit ở bio, bạn vào lấy về dùng ngay nhé. |

### 3. Checklist Shot List cần quay / chụp
- [ ] **Screen Record 1:** Ví dụ lỗi đặt video 16:9 vào khung 9:16 với hiệu ứng Gaussian Blur ở nền dưới (gạch đỏ).
- [ ] **Screen Record 2:** Thao tác căn chỉnh Scale & Position cho footage 4K ngang sang dọc (căn mắt ở đường lưới 1/3 trên).
- [ ] **Screen Record 3:** Thao tác dùng `Crop` эффект chia màn hình 50/50 trên-dưới từ cùng một hoặc hai góc máy ngang.
- [ ] **Screen Record 4:** Thao tác bật/tắt layer PNG `Safe_Zone_9x16.png` trên Premiere để đặt vị trí phụ đề chuẩn xác.
- [ ] **A-roll:** Thành ngồi trước màn hình hướng dẫn ngắn gọn và đọc câu kết.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
* **Caption TikTok:**
  Có sẵn video quay ngang trên YouTube hoặc buổi quay sự kiện mà muốn cắt ra đăng TikTok/Reels thì đừng chèn 2 dải mờ trên dưới nữa. Áp dụng 3 bố cục này giúp video nhìn như được quay riêng cho màn hình dọc.
  Mình để sẵn file khung Safe Zone 9:16 và checklist trong Starter Kit ở bio, bạn vào lấy về dùng ngay nhé.
  `#dungcochudich` `#videoediting` `#premierepro` `#reelsediting`
* **Caption Facebook Reels:**
  Rất nhiều thương hiệu và creator có sẵn kho video quay ngang chất lượng cao nhưng khi cắt sang khổ dọc đăng Reels lại chỉ thu nhỏ hình vào giữa rồi làm mờ hai đầu trên dưới. Cách đó làm hình ảnh sản phẩm bị bé đi một nửa trên điện thoại. Đây là 3 cách mình bố cục lại footage ngang sang dọc sạch và hiện đại hơn. Bạn vào Starter Kit ở bio để lấy khung vùng an toàn về đặt vào phần mềm dựng nhé!

#### B. Bài đăng Facebook cá nhân (120–180 chữ)
Một yêu cầu mình nhận được rất thường xuyên từ khách hàng là: "Bên anh có sẵn video quay ngang cho YouTube/Website rồi, giờ em cắt ngắn ra khổ dọc 9:16 để đăng TikTok và Reels giúp anh nhé".

Sai lầm nhanh nhất khi làm việc này là ném thẳng file ngang vào khung dọc, thu nhỏ lại cho vừa chiều ngang rồi chèn hai dải nền làm mờ (blur) ở trên và dưới. Cách làm đó khiến khung hình chính chỉ còn bé bằng cái tem thư trên màn hình điện thoại, người xem lướt qua cảm giác ngay là video "cắt vội".

Để một video chuyển từ ngang sang dọc nhìn tự nhiên như quay gốc, mình luôn xử lý theo 3 quy tắc:
1. Nếu nguồn quay là 4K và chỉ có 1 chủ thể: phóng tràn khung 9:16 và khóa vị trí hai mắt nhân vật nằm đúng đường lưới 1/3 trên.
2. Nếu khung ngang rộng có cả mặt người nói lẫn sản phẩm trên bàn: nhân đôi layer và dùng lệnh Crop chia bố cục trên/dưới (nửa trên giữ biểu cảm mặt, nửa dưới zoom cận cảnh thao tác tay).
3. Luôn đặt một lớp ảnh khung vùng an toàn (Safe Zone) ở track trên cùng để căn vị trí phụ đề, tránh bị giao diện của TikTok/Reels che mất chữ.

Mình có để sẵn file khung Safe Zone và checklist trong mục Starter Kit ở bio, bạn nào cần cứ vào tải về dùng nhé.

---

## VIDEO #24 — MÃ C045: "Dùng AI tạo ba phiên bản hook để A/B test"

### 1. Thông tin định danh
* **Ngày đăng:** Thứ Bảy, 05/12/2026 (Lịch linh hoạt — Khép lại Sprint 2)
* **Pillar / Tuyến nội dung:** P3 - AI trong workflow editor (`AI02` — AI hỗ trợ tiền kỳ, kịch bản & cấu trúc)
* **Format:** Screen record (Quay màn hình kết hợp hướng dẫn dựng thực tế)
* **Tệp người xem mục tiêu:** Marketer, Chủ shop chạy quảng cáo hoặc xây kênh chuyển đổi, Creator
* **Mục tiêu Funnel:** Cân nhắc (Đẩy chuyển đổi tìm hiểu lộ trình **Zero To AI**)
* **Claim duy nhất:** Thay vì đoán mò câu mở đầu nào sẽ giữ chân người xem, hãy dùng AI viết 3 góc Hook khác nhau (Nỗi đau – Kết quả – Phản trực giác) cho cùng một phần thân bài, rồi chỉ cần quay thêm 2 phút và thay 3 giây đầu trên timeline để có ngay 3 phiên bản A/B test.
* **Bằng chứng cần chuẩn bị:** Màn hình Prompt yêu cầu AI sinh đúng 3 góc Hook cho 1 sản phẩm/chủ đề (giữ nguyên câu chuyển sang phần thân bài ở giây thứ 04) + Màn hình timeline Premiere cho thấy phần Body–Close (00:04 – 00:35) giữ cố định, chỉ thay 3 khối Hook A / Hook B / Hook C ở 4 giây đầu tiên.
* **CTA & Offer:** Nhận mẫu prompt A/B test Hook + Xem lộ trình **Zero To AI** ở bio.

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) + SFX / Nhịp |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03** *(Hook)* | Màn hình Premiere hiển thị 1 phần thân bài (màu cam) cố định phía sau, nhưng ở 3 giây đầu có 3 lớp Hook A, Hook B, Hook C xếp chồng lên nhau để xuất ra 3 video test. | Tạo **ba phiên bản test** chỉ bằng cách thay ba giây đầu | *(SFX: Tiếng tách lớp Click-Click-Click)* Đừng bao giờ để số phận của cả một video phụ thuộc vào việc đoán mò một câu mở đầu duy nhất. |
| **00:03 – 00:10** *(Proof / Tension)* | Chỉ vào biểu đồ giữ chân người xem (Retention graph) bị gãy tụt ở giây thứ 02 dù phần nội dung từ giây 05 trở đi rất chất lượng. | Nội dung hay vẫn chết nếu **gãy ở ba giây đầu** | Rất nhiều video mình dựng cho khách có phần giải thích sản phẩm cực kỳ thuyết phục, nhưng lượt xem vẫn thấp chỉ vì câu mở đầu đầu tiên chưa chạm đúng tệp người mua. |
| **00:10 – 00:18** *(Body - Bước 1)* | Quay màn hình câu lệnh (Prompt) của Thành trên AI: Dán phần thân bài cố định vào trước, yêu cầu AI viết 3 câu mở đầu theo 3 góc: (1) Đánh vào nỗi đau, (2) Đưa kết quả lên trước, (3) Góc phản trực giác. | Bước 1: Dùng AI tách **ba góc tiếp cận** khác nhau | Cách mình kết hợp AI và tư duy dựng để giải bài toán này như sau. Một: mình dán phần thân bài đã chốt vào AI, yêu cầu nó viết ba câu mở đầu theo đúng ba góc: nỗi đau, kết quả trực tiếp và góc ngược số đông. |
| **00:18 – 00:25** *(Body - Bước 2)* | Zoom vào dòng điều kiện quan trọng nhất trong Prompt: *"Cả 3 câu Hook đều phải nối khớp tự nhiên vào câu đầu tiên của phần thân bài: 'Và đây là 3 bước mình đã sửa...'"*. | Bước 2: Khóa câu nối để **khớp chung một thân bài** | Hai: điểm mấu chốt trong câu lệnh là bắt AI viết sao cho cả ba câu mở đầu đều nối khớp mượt mà vào cùng một câu đầu tiên của phần thân bài. |
| **00:25 – 00:32** *(Body - Bước 3)* | Quay màn hình Premiere: Phần thân và kết (từ giây 04 đến giây 38) được giữ nguyên; ở 4 giây đầu, Thành bật/tắt mắt (Toggle Track Output) giữa Track V1 (Hook A), V2 (Hook B), V3 (Hook C) và bấm Queue sang Media Encoder xuất 3 file cùng lúc. | Bước 3: Chỉ quay thêm một phút để **xuất ba phiên bản** | Ba: lúc bấm máy, bạn chỉ tốn thêm một phút để đọc ba câu mở đầu đó. Khi lên timeline, bạn giữ nguyên phần thân, chỉ thay bốn giây đầu là xuất được ba phiên bản để đo xem góc nào giữ chân khách tốt nhất. |
| **00:32 – 00:40** *(Close & CTA)* | Hiện 3 file video xuất ra (`Video_HookA_NoiDau.mp4`, `Video_HookB_KetQua.mp4`, `Video_HookC_PhanTrucGiac.mp4`), sau đó về A-roll Thành chốt bài. | Xem lộ trình ứng dụng AI thực chiến tại **Zero To AI** ở bio | AI giúp bạn nhân bản góc nhìn marketing, còn kỹ thuật dựng giúp bạn nhân bản video mà không tốn sức làm lại từ đầu. Đó là cách mình dựng có chủ đích. Nếu bạn muốn học cách ứng dụng AI vào nội dung từ gốc theo lộ trình rõ ràng, xem mục Zero To AI ở bio của mình nhé. |

### 3. Checklist Shot List cần quay / chụp
- [ ] **Screen Record 1:** Màn hình Prompt AI hiển thị rõ cấu trúc: `[Thân bài cố định]` + `[Yêu cầu 3 góc Hook: Nỗi đau / Kết quả / Phản trực giác]` + `[Điều kiện khớp nối vào câu đầu thân bài]`.
- [ ] **Screen Record 2:** Màn hình timeline Premiere với 3 clip Hook ngắn (màu Hồng, Tím, Xanh dương) xếp chồng ở 4 giây đầu nối vào cùng 1 khối Body (màu Cam).
- [ ] **Screen Record 3:** Cảnh Adobe Media Encoder đang xếp hàng (Queue) render 3 phiên bản `v1_Hook_NoiDau`, `v2_Hook_KetQua`, `v3_Hook_PhanTrucGiac` cùng lúc.
- [ ] **A-roll:** Thành nói câu dẫn và câu chốt tại bàn làm việc.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
* **Caption TikTok:**
  Làm sao để biết khách hàng sẽ dừng lại vì "nỗi đau" hay vì "kết quả"? Đừng đoán mò, hãy dùng AI viết 3 góc mở đầu nối chung vào 1 phần thân bài để test thực tế mà chỉ tốn thêm 1 phút quay.
  Nếu bạn muốn học cách ứng dụng AI vào làm nội dung từ gốc theo lộ trình rõ ràng, xem mục Zero To AI ở bio của mình nhé.
  `#dungcochudich` `#aimarketing` `#abtesting` `#videoediting`
* **Caption Facebook Reels:**
  Đây là mẹo kết hợp giữa AI và dựng video giúp các bạn làm marketing tiết kiệm cực nhiều chi phí sản xuất khi chạy thử nghiệm nội dung (A/B test). Thay vì quay 3 video mới hoàn toàn, mình dùng AI thiết kế 3 góc Hook khác nhau nhưng khớp chung vào một phần thân bài cố định. Xem hết quy trình trong clip và tham khảo mục Zero To AI ở bio của mình nếu bạn muốn áp dụng hệ thống này nhé!

#### B. Bài đăng Facebook cá nhân (120–180 chữ)
Khi làm video cho mục tiêu bán hàng hoặc chạy quảng cáo, điều tiếc nhất là bạn đầu tư rất nhiều công sức cho phần chứng minh sản phẩm ở giữa bài, nhưng video lại vắng người xem chỉ vì 3 giây đầu tiên chọn sai góc tiếp cận.

Thay vì ngồi tranh luận trong phòng họp xem câu mở đầu nào hay hơn, cách làm thực tế nhất của mình là để dữ liệu trả lời thông qua việc tách 3 phiên bản Hook cho cùng 1 video:
1. Đưa phần thân bài đã chốt vào AI, yêu cầu viết 3 câu mở đầu theo 3 tâm lý khác nhau: đánh trực diện vào nỗi sợ, mở màn bằng kết quả cuối cùng, và góc nhìn ngược đám đông.
2. Thêm một điều kiện bắt buộc trong câu lệnh: cả 3 câu mở đầu này phải dẫn dắt khớp hoàn toàn vào câu đầu tiên của phần thân bài (nhờ vậy vết cắt ở giây thứ 4 không bị gượng).
3. Lúc ghi hình chỉ cần đọc thêm 2 câu mở đầu phụ (tốn thêm đúng 1 phút). Khi dựng trên Premiere, mình giữ nguyên toàn bộ phần thân bài 30 giây phía sau, chỉ thay 4 giây đầu tiên và đẩy sang Media Encoder xuất ra 3 file một lượt.

Ảnh dưới là câu lệnh và cách mình xếp track để xuất 3 bản test. Bạn nào muốn học cách ứng dụng AI vào quy trình nội dung bài bản từ gốc thì xem mục Zero To AI trên bio của mình nhé.

---

# PHẦN V: CHECKLIST NGHIỆM THU CUỐI SPRINT 2 (TUẦN 04 – TUẦN 06)

Trước khi chuyển sang **Sprint 3 (Tuần 07 – Tuần 09: Tăng tốc Chuyển đổi & Hệ thống hóa Workflow)**, hãy rà soát các chỉ số và tài sản sau vào tối Chủ Nhật (06/12/2026):

- [ ] **Độ phủ & Tỷ trọng Pillar trong Sprint 2 (12 video):**
  - **P1 - Marketing trong video:** 5 video (`C005`, `C006`, `C007`, `C008`, `C009`) — Đóng vai trò thu hút chủ shop, marketer và đẩy lưu lượng vào Starter Kit + Dịch vụ Edit.
  - **P2 - Edit & Storytelling:** 3 video (`C025`, `C026`, `C027`) — Khẳng định tay nghề kỹ thuật sạch, có kỷ luật.
  - **P3 - AI trong workflow editor:** 3 video (`C043`, `C044`, `C045`) — Chứng minh tư duy làm chủ AI ở khâu tiền kỳ (Shot list, Biên tập văn nói, A/B test Hook), dẫn dắt tự nhiên về **Zero To AI**.
  - **P4 - Hành trình & Bằng chứng:** 1 video (`C057`) — Duy trì nhịp Build in Public trung thực (30 ngày tự luyện motion).
- [ ] **Tài sản chuyển đổi (Conversion Assets) đã kích hoạt:**
  - Bộ **Starter Kit** trên bio đã có đủ các biểu mẫu được nhắc trong video: *Khung tách 1 Insight = 1 Video (`C006`)*, *Mẫu chuyển Comment khách hàng -> 3 Hook (`C007`)*, *Bảng Mapping CTA (`C009`)*, *File PNG Safe Zone 9:16 & Checklist dựng dọc (`C027`)*.
  - Tin nhắn tự động hoặc kịch bản phản hồi khi có người nhắn từ khóa **`EDIT`** (`C005`, `C008`).
  - Trang giới thiệu lộ trình **`Zero To AI`** trên bio (`C043`, `C044`, `C045`).

<!-- ===== /file: personal-brand-video-engine/references/01_Y_TUONG_VA_SCRIPT/02_SPRINT_2_TUAN_04_06_XAY_BANG_CHUNG.md ===== -->

<!-- ===== file: personal-brand-video-engine/references/01_Y_TUONG_VA_SCRIPT/03_SPRINT_3_TUAN_07_09_TOI_UU_HE_THONG.md ===== -->

# KỊCH BẢN SẢN XUẤT CHI TIẾT — SPRINT 3 (TUẦN 07 ĐẾN TUẦN 09: 07/12/2026 – 26/12/2026)
## GIAI ĐOẠN 3: TỐI ƯU HỆ THỐNG & CHUẨN HÓA SERIES (VIDEOS #25 – #36)

> **Hệ quy chiếu thực thi:**
> - **Voice Profile:** Thành — Dựng Có Chủ Đích (Marketing Video Editor ứng dụng AI). Xưng "mình", gọi "bạn". Câu ngắn (8–16 từ), trực diện, có khoảng nghỉ nhịp 0.5–1s trước câu chốt, không sáo ngữ, không phóng đại kết quả.
> - **Mục tiêu Sprint 3 (Tuần 7–9):** Sau 6 tuần chạy nền tảng và thử nghiệm, Sprint 3 tập trung **chuẩn hóa các series hiệu quả nhất** (CTA chuyển đổi, Cấu trúc kịch bản 30s, Phân ranh Premiere vs After Effects, Kiểm duyệt asset AI từ Xưởng Media đưa vào Premiere, và Quy trình làm việc chuyên nghiệp).
> - **Cấu trúc 4 nhịp chuẩn `content-engine`:** Hook (`00:00–00:03`) → Proof/Tension (`00:03–00:10`) → Body 1 Claim (`00:10–00:32`) → Close & 1 CTA (`00:32–00:40`).
> - **Quy tắc On-screen Text:** Viết hoa chữ cái đầu mỗi dòng hiển thị; mỗi khung hình chỉ nhấn đúng **1 cụm từ khóa** (đặt trong ngoặc vuông `[Từ khóa]`).

---

## TỔNG QUAN LỊCH ĐĂNG SPRINT 3 (12 VIDEO)

| STT | Mã | Ngày đăng | Thứ | Pillar & Tuyến | Tiêu đề kịch bản | Tệp người xem | Funnel | CTA & Offer |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **25** | `C010` | 07/12/2026 | Thứ Hai | P1 - `MKT03` | Ba CTA cho ba mức độ sẵn sàng mua | Chủ shop | Cân nhắc | Nhận bảng (`Starter Kit`) |
| **26** | `C028` | 08/12/2026 | Thứ Ba | P2 - `EDIT03` | Khi nào Premiere đủ, khi nào cần After Effects? | Editor mới | Nhận biết | Lưu video (`Không bán`) |
| **27** | `C046` | 10/12/2026 | Thứ Năm | P3 - `AI03` | Tạo asset sản phẩm bằng AI rồi đưa vào Premiere | Chủ shop | Cân nhắc | Dùng thử công cụ (`Xưởng Media`) |
| **28** | `C058` | 12/12/2026 | Thứ Bảy (Linh hoạt) | P4 - `JRN03` | Một ngày làm media của tôi | Khách hàng | Tin cậy | Nhắn câu hỏi (`Dịch vụ`) |
| **29** | `C011` | 14/12/2026 | Thứ Hai | P1 - `MKT03` | Sửa CTA cuối video dịch vụ | Khách hàng | Chuyển đổi | Nhắn EDIT (`Dịch vụ`) |
| **30** | `C012` | 15/12/2026 | Thứ Ba | P1 - `MKT04` | Công thức hook–body–close trong 30 giây | Creator | Nhận biết | Nhận template (`Starter Kit`) |
| **31** | `C029` | 17/12/2026 | Thứ Năm | P2 - `EDIT03` | Một text animation để nhấn đúng từ khóa | Editor | Nhận biết | Theo dõi hành trình (`Không bán`) |
| **32** | `C047` | 19/12/2026 | Thứ Bảy (Linh hoạt) | P3 - `AI03` | Một ảnh sản phẩm có thể tạo bao nhiêu video? | Affiliate marketer | Nhận biết | Xem workflow (`Xưởng Media`) |
| **33** | `C013` | 21/12/2026 | Thứ Hai | P1 - `MKT04` | Một video chỉ nên có một claim | Creator | Nhận biết | Lưu video (`Không bán`) |
| **34** | `C030` | 22/12/2026 | Thứ Ba | P2 - `EDIT03` | Motion đẹp nhưng có làm người xem hiểu hơn? | Creator | Cân nhắc | Nhắn EDIT (`Dịch vụ`) |
| **35** | `C048` | 24/12/2026 | Thứ Năm | P3 - `AI03` | AI video nào dùng được, video nào phải bỏ? | Creator | Cân nhắc | Lưu checklist (`Xưởng Media`) |
| **36** | `C059` | 26/12/2026 | Thứ Bảy (Linh hoạt) | P4 - `JRN04` | Sai lầm lớn nhất khi mới nhận job edit | Editor mới | Tin cậy | Lưu bài học (`Không bán`) |

---

# TUẦN 7: CHUẨN HÓA CTA THEO PHỄU & PHỐI HỢP CÔNG CỤ (07/12/2026 – 12/12/2026)

---

## VIDEO #25 — MÃ `C010`: BA CTA CHO BA MỨC ĐỘ SẴN SÀNG MUA

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Hai, 07/12/2026
- **Pillar / Tuyến nội dung:** P1 (Marketing trong video) — `MKT03` (Tối ưu CTA & Chuyển đổi)
- **Format:** Carousel video (Video lật thẻ trực quan kết hợp A-roll giải thích ngắn)
- **Tệp người xem mục tiêu:** Chủ shop đang tự làm video sản phẩm nhưng không ra tin nhắn
- **Mục tiêu Funnel:** Cân nhắc (Consideration)
- **Claim duy nhất:** Bắt người mới xem kênh lần đầu "mua ngay" ở cuối video sẽ làm gãy chuyển đổi; mỗi mức độ sẵn sàng mua cần đúng một kiểu CTA tương ứng.
- **Bằng chứng cần chuẩn bị:** Ba thẻ (card) so sánh trực quan 3 câu CTA đặt ở 3 giây cuối của cùng một dòng sản phẩm (Đồ gia dụng / Thời trang) trên màn hình Premiere.
- **CTA & Offer:** Nhận bảng phân loại CTA theo phễu trong `Starter Kit` ở bio.

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio / Voiceover) + Nhịp/SFX |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03**<br>*(Hook)* | Cận cảnh 3 giây cuối một video bán hàng trên timeline Premiere với dòng chữ to "Mua ngay kẻo hết". Bàn tay Thành gạt thẻ đỏ gạch chéo khung hình đó. | Video nào cũng kêu `[Mua ngay]` là tự chặn khách | *(SFX: Tiếng còi báo lỗi nhẹ)*<br>Video nào bạn cũng kết bằng câu "mua ngay" thì rất dễ mất khách. |
| **00:03 – 00:10**<br>*(Proof / Tension)* | A-roll Thành ngồi trước màn hình có 3 cột thẻ màu (Lạnh - Ấm - Nóng). Zoom nhẹ vào cột "Khách lạ mới lướt qua". | Khách mới biết chưa đủ `[Tin tưởng]` để chốt đơn | Người mới thấy shop bạn lần đầu trên xu hướng chưa có đủ niềm tin để rút ví. Ép họ mua ngay chỉ khiến họ lướt qua. *(Nghỉ 0.5s)* |
| **00:10 – 00:17**<br>*(Body - Mức 1)* | Lật Card 1 trên màn hình (màu xanh dương): Video mẹo phối đồ/sử dụng sản phẩm. Cuối video hiện nút "Lưu lại" và trỏ sang phần 2. | Mức 1 - Mới biết: Kêu gọi `[Lưu video]` hoặc xem tiếp | Khi làm video cho khách mới, mình chia CTA làm ba mức rõ ràng. *(SFX: Flip card)*<br>Mức một: Người mới biết. Chỉ xin một hành động nhẹ như lưu lại mẹo này hoặc xem tiếp phần hai. |
| **00:17 – 00:25**<br>*(Body - Mức 2)* | Lật Card 2 (màu vàng cam): Video so sánh chất liệu hoặc hướng dẫn chọn size. Cuối video hiện bảng quy đổi size tải miễn phí. | Mức 2 - Đang cân nhắc: Mời nhận `[Bảng chọn size]` hoặc checklist | *(SFX: Flip card)*<br>Mức hai: Người đang tìm hiểu cách chọn. Hãy mời họ nhận bảng chọn size, bảng báo giá mẫu hoặc checklist kiểm tra hàng trước khi mua. |
| **00:25 – 00:32**<br>*(Body - Mức 3)* | Lật Card 3 (màu xanh lá): Video giải quyết nỗi đau gấp (cần quà tặng/cần sửa lỗi ngay). Cuối video hiện mã từ khóa ngắn gọn để nhắn tin. | Mức 3 - Cần gấp: Nhắn đúng `[Một từ khóa]` để nhận giải pháp | *(SFX: Flip card)*<br>Mức ba: Người đang cần giải quyết gấp. Lúc này mới mời họ nhắn một từ khóa ngắn kèm tình trạng để bạn tư vấn thẳng. |
| **00:32 – 00:40**<br>*(Close & CTA)* | Quay lại A-roll Thành, bên cạnh hiện ảnh chụp Bảng 15 mẫu câu CTA theo 3 cấp độ trong Starter Kit. | Lấy bảng 15 câu CTA trong `[Starter Kit]` ở bio | *(Nghỉ 0.5s)* Đúng người, đúng nhiệt độ thì lời kêu gọi mới có tác dụng. Đó là cách mình dựng có chủ đích. Mình để sẵn bảng mười lăm câu CTA theo ba mức độ này trong Starter Kit ở bio, bạn vào lấy về dùng nhé. |

### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] **Shot 1 (Screen Record):** Đuôi video bán hàng mẫu trên Premiere có text "Mua ngay - Inbox liền tay" bị gạch đỏ.
- [ ] **Shot 2 (A-roll):** Thành ngồi góc nghiêng 15 độ trước màn hình, nói câu Tension và câu Kết.
- [ ] **Shot 3 (Graphic / Carousel Card 1 - 2 - 3):** Thiết kế sẵn 3 tấm thẻ dọc 9:16 sạch sẽ trên Premiere/Canva thể hiện 3 mức độ: *Mới biết (Lưu/Xem tiếp)* — *Đang tìm cách làm (Nhận bảng/Checklist)* — *Cần giải quyết ngay (Nhắn mã từ khóa)*.
- [ ] **Shot 4 (B-roll tài liệu):** Cảnh mở trang "Bảng 15 câu CTA theo mức độ sẵn sàng mua" nằm trong bộ `Starter Kit`.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
Đừng bắt người mới thấy video của bạn lần đầu phải "mua ngay". Chia CTA theo 3 mức độ sẵn sàng mua giúp giữ chân khách lạ và lọc đúng khách nét.
👉 Mình để sẵn Bảng 15 câu CTA mẫu theo 3 cấp độ này trong **Starter Kit** ở bio, bạn vào lấy về ráp vào video nhé.
`#dungcochudich` `#marketingvideo` `#videoediting` `#banhangonline`

#### B. Bài đăng Facebook cá nhân (155 chữ)
Tuần trước khi xem lại 10 video của một chủ shop thời trang, mình thấy cả 10 video đều kết thúc bằng đúng một câu: "Anh chị đặt hàng nhắn tin ngay cho shop nhé". Kết quả là video có lượt xem nhưng hộp thư vẫn im lặng.

Vấn đề không nằm ở sản phẩm, mà nằm ở việc dùng một câu CTA cho mọi trạng thái tâm lý của người xem (trong khi người mới lướt qua chưa hề có lý do để nhắn tin). Khi dựng lại hệ thống video cho kênh, mình luôn tách CTA thành 3 nấc:
1. **Video thu hút người mới biết:** Chỉ mời họ "Lưu lại bảng phối màu này để lúc cần mở ra xem".
2. **Video cho người đang phân vân:** Mời họ "Lấy bảng đo size chuẩn theo cân nặng ở phần bình luận/bio".
3. **Video cho người cần mua gấp:** Đưa ra lời mời cụ thể "Nhắn mã SƠMI kèm chiều cao để shop chọn sẵn 2 mẫu vừa người".

Mình đã đóng gói bảng 15 mẫu câu CTA chia theo 3 mức độ này vào bộ **Starter Kit** ở bio. Bạn đang tự quay dựng video cho shop có thể vào lấy về đối chiếu ngay trước khi xuất file.

---

## VIDEO #26 — MÃ `C028`: KHI NÀO PREMIERE ĐỦ, KHI NÀO CẦN AFTER EFFECTS?

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Ba, 08/12/2026
- **Pillar / Tuyến nội dung:** P2 (Edit & Storytelling) — `EDIT03` (Kỹ thuật dựng & Motion có chủ đích)
- **Format:** Talking head kết hợp ví dụ hình ảnh split-screen trực quan
- **Tệp người xem mục tiêu:** Editor mới vào nghề (hay bị sa đà vào việc mở After Effects cho những tác vụ đơn giản)
- **Mục tiêu Funnel:** Nhận biết (Awareness)
- **Claim duy nhất:** 80% video ngắn bán hàng và xây kênh chỉ cần Premiere là đủ nhanh; chỉ bật After Effects khi cần giải quyết 3 bài toán hình ảnh mà Premiere làm sẽ lâu hoặc giả.
- **Bằng chứng cần chuẩn bị:** 3 cặp ví dụ trực quan trên màn hình: (1) Cắt nhịp + Sub + Zoom nhẹ bằng Transform trong Premiere (mất 2 phút) vs (2) Tách lớp vật thể 3D / Tracking chuyển động phức tạp / Biểu đồ số liệu động trong After Effects.
- **CTA & Offer:** Lưu video (`Không bán`).

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio / Voiceover) + Nhịp/SFX |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03**<br>*(Hook)* | Cảnh màn hình đang chờ Dynamic Link từ Premiere sang After Effects quay vòng vòng kèm đồng hồ đếm giờ. Cắt sang A-roll Thành. | Đừng mở `[After Effects]` cho việc Premiere làm mất 2 phút | *(SFX: Tiếng thở dài nhẹ + tiếng click chuột)*<br>Đừng tốn một tiếng mở After Effects cho việc Premiere làm mất đúng hai phút. |
| **00:03 – 00:10**<br>*(Proof / Tension)* | A-roll Thành nói trực diện, trên góc màn hình hiện cảnh project AE nặng 4GB chỉ để làm chữ chạy và zoom ảnh. | Nhiều editor mới tự làm `[Chậm tiến độ]` vì lạm dụng AE | Hồi mới dựng, mình từng đưa cả đoạn video ba mươi giây sang After Effects chỉ để làm chữ bay và zoom khung hình. Máy vừa giật, lúc khách sửa một chữ lại phải render lại từ đầu. *(Nghỉ 0.5s)* |
| **00:10 – 00:18**<br>*(Body - Tình huống 1)* | Screen Record trong Premiere: Kéo preset Transform có Motion Blur (Shutter Angle 180) + gắn phụ đề nhấn từ khóa. | 1. Cắt nhịp, zoom có blur và phụ đề: Dùng `[Premiere]` | Bây giờ mình chia ranh giới rất rõ bằng ba tình huống thực tế. *(SFX: Pop)*<br>Một: Cắt nhịp nói, zoom khung hình có độ nhòe chuyển động và làm phụ đề. Cứ dùng hiệu ứng Transform ngay trong Premiere là xong. |
| **00:18 – 00:25**<br>*(Body - Tình huống 2)* | Split-screen: Bên trái là highlight khoanh vùng đơn giản (Premiere), bên phải là đường line chạy bám dính theo ngón tay người đang di chuyển (AE Tracking). | 2. Bám theo vật thể chuyển động liên tục: Chuyển sang `[After Effects]` | *(SFX: Whoosh)*<br>Hai: Khi cần chữ hoặc mũi tên bám dính theo đúng tay người hay sản phẩm đang di chuyển. Lúc này mới cắt riêng đoạn ba giây đó đưa sang After Effects để track. |
| **00:25 – 00:32**<br>*(Body - Tình huống 3)* | Ví dụ trên màn hình AE: Minh họa cơ chế sản phẩm tách lớp (layer breakdown) hoặc biểu đồ tăng trưởng vẽ theo nhịp giọng nói. | 3. Minh họa cơ chế tách lớp hoặc biểu đồ: Dùng `[After Effects]` | *(SFX: Ding)*<br>Ba: Khi lời nói trừu tượng cần vẽ lại bằng sơ đồ chuyển động hoặc tách lớp sản phẩm để người xem hiểu ngay trong ba giây. |
| **00:32 – 00:40**<br>*(Close & CTA)* | A-roll Thành kết bài. Hiện bảng tóm tắt nhỏ: "Premiere = Nhịp & Cấu trúc | AE = Giải thích trực quan". | `[Lưu video]` để phân chia đúng công cụ trước khi dựng | *(Nghỉ 0.5s)* Công cụ nào giúp người xem hiểu nhanh hơn mà bạn vẫn kịp deadline thì chọn công cụ đó. Đó là cách mình dựng có chủ đích. Bạn lưu lại ba mốc này để đỡ tốn giờ render nhé. |

### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] **Shot 1 (Screen Record):** Cảnh bấm "Replace with After Effects Composition" bị treo loading lâu.
- [ ] **Shot 2 (A-roll):** Thành ngồi tại bàn dựng, chia sẻ thẳng thắn với tệp editor mới.
- [ ] **Shot 3 (Screen Record Premiere):** Bảng Effect Controls mở sẵn `Transform` với `Use Composition's Shutter Angle` tắt đi và chỉnh `Shutter Angle = 180`.
- [ ] **Shot 4 (Screen Record After Effects):** 1 đoạn ngắn 3–4 giây dùng 3D Camera Tracker hoặc Null Object bám theo sản phẩm + 1 đoạn minh họa sơ đồ/con số.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
Làm sao biết lúc nào chỉ cần Premiere, lúc nào mới đáng mở After Effects? Mình dựa vào 3 tình huống thực tế này để không tự làm khổ máy tính và trễ deadline.
📌 Lưu lại video này để kiểm tra trước khi bấm "Replace with After Effects Composition" nhé.
`#dungcochudich` `#videoediting` `#premierepro` `#aftereffects`

#### B. Bài đăng Facebook cá nhân (165 chữ)
Có một cái bẫy rất quen thuộc với các bạn editor mới (và chính mình hồi mới làm cũng dính): Cứ nghĩ video phải đem qua After Effects làm chữ bay lượn, chuyển cảnh phức tạp thì mới gọi là "dựng kỹ".

Đến khi nhận 4–5 video ngắn cần giao trong ngày và khách báo sửa lại đúng 2 chữ trong kịch bản, việc mở lại từng comp After Effects để render lại mới thực sự là ác mộng.

Sau hơn nửa năm tối ưu lại quy trình dựng video marketing, mình giữ nguyên tắc phân việc rất gọn giữa hai phần mềm:
- **Premiere gánh 85% thời lượng:** Toàn bộ phần cắt nhịp câu nói, lọc khoảng thở, âm thanh, phụ đề và các cú zoom/pan cơ bản (chỉ cần dùng effect Transform bật Shutter Angle 180 là đã rất mượt).
- **After Effects chỉ xử lý các đoạn 3–5 giây "đắt":** Khi cần tracking chữ bám theo chuyển động thật, hoặc khi cần vẽ một sơ đồ trực quan để giải thích số liệu/cơ chế mà lời nói không tả hết được.

Dựng nhanh ở chỗ cần nhanh để dành thời gian chăm chút đúng 3 giây quyết định. Bạn đang học edit cứ lưu quy tắc này lại áp dụng nhé.

---

## VIDEO #27 — MÃ `C046`: TẠO ASSET SẢN PHẨM BẰNG AI RỒI ĐƯA VÀO PREMIERE

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Năm, 10/12/2026
- **Pillar / Tuyến nội dung:** P3 (AI trong workflow editor) — `AI03` (Tạo B-roll & Asset hình ảnh bằng AI)
- **Format:** Workflow demo (Quay màn hình thao tác thật kết hợp A-roll ngắn)
- **Tệp người xem mục tiêu:** Chủ shop có ít tư liệu quay, chỉ có vài tấm ảnh chụp sản phẩm tĩnh bằng điện thoại
- **Mục tiêu Funnel:** Cân nhắc (Consideration)
- **Claim duy nhất:** Khi chủ shop chỉ có 1 tấm ảnh sản phẩm tĩnh, đừng kéo giãn ảnh suốt 15 giây; hãy dùng AI tạo bối cảnh chuyển động ngắn 3 giây rồi đưa vào Premiere cắt nhịp, ghép chữ và tiếng động thật.
- **Bằng chứng cần chuẩn bị:** 1 ảnh gốc chụp chai nước hoa/hộp trà trên nền trắng → Màn hình thao tác trên **Xưởng Media** tách nền, đặt lên mặt bàn gỗ có nắng chiếu nhẹ và tạo chuyển động camera pan chậm 3 giây → Timeline Premiere ghép nối với cảnh thật, chèn SFX và text thông tin.
- **CTA & Offer:** Dùng thử công cụ (`Xưởng Media` — link ở bio).

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio / Voiceover) + Nhịp/SFX |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03**<br>*(Hook)* | Split-screen: Bên trái là ảnh chụp chai serum/hộp trà trên nền trắng đứng im; bên phải là cảnh video sản phẩm đặt trên bàn gỗ có ánh nắng chuyển động nhẹ kèm text giá trị. | Từ 1 ảnh tĩnh thành `[Video mở đầu]` có chiều sâu | *(SFX: Tiếng chụp ảnh chuyển sang tiếng nhạc ambient mượt)*<br>Khi khách chỉ gửi đúng một tấm ảnh sản phẩm chụp vội, mình xử lý thế nào? |
| **00:03 – 00:10**<br>*(Proof / Tension)* | Màn hình Premiere chiếu cảnh tấm ảnh tĩnh chỉ được phóng to thu nhỏ (zoom in/out) đơn điệu suốt 8 giây. | Phóng to ảnh tĩnh mãi nhìn rất `[Giả và chán]` | Nếu chỉ bỏ tấm ảnh đó vào Premiere rồi kéo zoom ra zoom vào suốt mười giây, người xem sẽ nhận ra ngay video thiếu đầu tư và lướt qua. *(Nghỉ 0.5s)* |
| **00:10 – 00:18**<br>*(Body - Bước 1: AI tạo bối cảnh)* | Quay màn hình trên **Xưởng Media**: Tải ảnh gốc lên, giữ nguyên nhãn sản phẩm, tạo bối cảnh mặt bàn gỗ sáng sớm và xuất đoạn chuyển động nhẹ 3 giây. | Bước 1: Tạo bối cảnh và chuyển động nhẹ trên `[Xưởng Media]` | Thay vì vậy, mình làm ba bước này. *(SFX: Click)*<br>Bước một: Đưa ảnh gốc lên Xưởng Media, giữ nguyên chi tiết nhãn hộp và tạo một bối cảnh mặt bàn có ánh nắng chuyển động nhẹ trong ba giây. |
| **00:18 – 00:25**<br>*(Body - Bước 2: Đưa vào Premiere)* | Kéo file video 3 giây từ Xưởng Media vào timeline Premiere. Cắt bỏ 0.5s cuối bị dư, chỉ lấy đúng 2.5s mượt nhất làm cảnh mở đầu. | Bước 2: Cắt lấy đúng `[2.5 giây]` mượt nhất trong Premiere | *(SFX: Cut sound)*<br>Bước hai: Đưa đoạn video đó vào Premiere. Mình không dùng hết mà chỉ cắt lấy hai giây rưỡi tự nhiên nhất để làm cảnh mở đầu giữ mắt. |
| **00:25 – 00:32**<br>*(Body - Bước 3: Editor hoàn thiện)* | Bật layer SFX (tiếng đặt hộp nhẹ, tiếng nắng sớm) và layer Text nêu điểm mạnh sản phẩm trên timeline Premiere. | Bước 3: Ghép âm thanh môi trường và `[Text lợi ích]` | *(SFX: Tiếng đặt lọ thủy tinh nhẹ + Whoosh)*<br>Bước ba: Thêm tiếng động môi trường thật và đặt dòng chữ lợi ích sản phẩm đúng nhịp chuyển cảnh sang phần tư vấn. |
| **00:32 – 00:40**<br>*(Close & CTA)* | Chạy lại 3 giây thành phẩm hoàn chỉnh, sau đó về A-roll Thành. | Trải nghiệm thử workflow trên `[Xưởng Media]` ở bio | *(Nghỉ 0.5s)* AI giúp tạo phần nguyên liệu hình ảnh còn thiếu, nhưng editor mới là người ghép nó thành câu chuyện bán hàng. Đó là cách mình dựng có chủ đích. Link dùng thử Xưởng Media mình để sẵn ở bio cho bạn nào muốn test với ảnh của shop nhé. |

### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] **Shot 1 (Asset gốc):** 1 tấm ảnh chụp sản phẩm thật (lọ mỹ phẩm, hộp cà phê hoặc phụ kiện) trên nền đơn giản.
- [ ] **Shot 2 (Screen Record Xưởng Media):** Quá trình đưa ảnh lên Xưởng Media, tạo bối cảnh lifestyle và xuất clip chuyển động ngắn.
- [ ] **Shot 3 (Screen Record Premiere):** Timeline thể hiện rõ việc cắt gọt đoạn AI (chỉ lấy 2.5s tốt nhất), chèn 2 track SFX bên dưới và 1 track Graphic Text bên trên.
- [ ] **Shot 4 (A-roll):** Thành ngồi trước màn hình kết bài.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
Chỉ có ảnh chụp sản phẩm tĩnh thì làm sao dựng mở đầu video cho bắt mắt? Đây là cách mình kết hợp tạo bối cảnh trên Xưởng Media rồi đưa về Premiere cắt nhịp và ghép âm thanh.
👉 Bạn có thể thử tạo asset từ ảnh sản phẩm của shop trên **Xưởng Media** (link dùng thử có affiliate mình để rõ ở bio).
`#dungcochudich` `#aiworkflow` `#xuongmedia` `#marketingvideo`

#### B. Bài đăng Facebook cá nhân (170 chữ)
Rất nhiều chủ shop khi làm việc với mình đều gặp chung một tình trạng: Muốn có video chạy quảng cáo hoặc đăng kênh đều đặn, nhưng trong máy chỉ có vài tấm ảnh sản phẩm chụp tĩnh trên nền trắng từ lúc mới nhập hàng.

Nếu chỉ đem mấy tấm ảnh đó vào phần mềm dựng rồi cho chạy hiệu ứng lật trang hay phóng to thu nhỏ, video nhìn chẳng khác nào một bản trình chiếu slide.

Cách mình giải quyết bài toán thiếu tư liệu hình ảnh mà không tốn chi phí thuê studio chụp lại:
1. **Phần việc của AI (Xưởng Media):** Dùng ảnh gốc của sản phẩm (giữ nguyên bao bì và chữ trên nhãn), tạo thêm bối cảnh bàn làm việc hoặc ánh nắng tự nhiên kèm chuyển động máy quay chậm khoảng 3–4 giây (mất khoảng 3 phút tạo).
2. **Phần việc của Editor (Premiere):** Đưa clip về timeline, cắt bỏ những giây đầu/cuối nếu chuyển động hơi thừa, chỉ giữ lại 2–2.5 giây đắt giá nhất làm Hook.
3. **Làm thật cảm giác:** Đắp thêm lớp âm thanh môi trường (tiếng đặt sản phẩm, tiếng không gian) và typography chỉ rõ lợi ích sản phẩm.

Bạn muốn tự tay thử biến ảnh tĩnh của shop thành cảnh quay ngắn thì xem mục **Xưởng Media** ở bio của mình nhé (link có affiliate).

---

## VIDEO #28 — MÃ `C058`: MỘT NGÀY LÀM MEDIA CỦA TÔI

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Bảy, 12/12/2026 (Slot linh hoạt cuối tuần)
- **Pillar / Tuyến nội dung:** P4 (Hành trình & Bằng chứng) — `JRN03` (Hậu trường làm việc & Quy trình thực tế)
- **Format:** BTS vlog (Nhật ký hậu trường công việc ngắn gọn, nhịp độ rõ ràng, bảo mật tuyệt đối dữ liệu khách hàng)
- **Tệp người xem mục tiêu:** Khách hàng tiềm năng (Chủ shop, Founder, Brand nhỏ muốn biết người đứng sau dịch vụ làm việc có quy củ hay không)
- **Mục tiêu Funnel:** Tin cậy (Trust)
- **Claim duy nhất:** Một video bán hàng gọn gàng không bắt đầu từ lúc mở phần mềm dựng, mà được quyết định từ khâu lọc brief buổi sáng đến bước kiểm tra phụ đề cuối ngày.
- **Bằng chứng cần chuẩn bị:** Các cảnh quay B-roll thật trong ngày của Thành (màn hình Notion/Sheet đã làm mờ tên khách, sổ tay ghi 1 claim, cảnh lọc footage, cảnh dựng nháp trên Premiere và cảnh xem lại bằng điện thoại trước khi gửi).
- **CTA & Offer:** Nhắn câu hỏi / Trao đổi nhu cầu (`Dịch vụ` Edit/Media).

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio / Voiceover) + Nhịp/SFX |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03**<br>*(Hook)* | Cảnh 08:30 sáng: Thành đặt ly cà phê xuống bàn, mở sổ tay ghi dòng chữ to "Hôm nay video này bán 1 ý gì?", phía sau là màn hình Premiere chưa mở. | Một ngày làm media bắt đầu từ `[Bản brief]`, không phải Premiere | *(SFX: Tiếng đặt ly xuống bàn + tiếng lật sổ)*<br>Nhiều người nghĩ công việc của mình là ngồi cắt video cả ngày, nhưng phần quan trọng nhất lại diễn ra trước khi mở Premiere. |
| **00:03 – 00:10**<br>*(Proof / Tension)* | Góc quay qua vai: Thành đọc bảng brief của khách (đã làm mờ logo/tên riêng), dùng bút highlight đúng 1 câu mục tiêu chuyển đổi và 1 tệp người xem. | 09:00 — Lọc đúng `[Một thông điệp]` từ yêu cầu của khách | Chín giờ sáng, việc đầu tiên của mình là đọc kỹ đề bài của khách để lọc ra đúng một thông điệp duy nhất cho video, thay vì ôm đồm năm bảy ý. *(Nghỉ 0.5s)* |
| **00:10 – 00:18**<br>*(Body - Buổi trưa: Tư liệu & AI hỗ trợ)* | 11:00 trưa: Cảnh Thành gom các đoạn quay thô khách gửi, phân loại vào 3 thư mục `01_Hook`, `02_Proof`, `03_CTA` và dùng AI tạo nháp cấu trúc câu nói. | 11:00 — Phân loại footage theo `[Ba nhịp]` Hook - Proof - CTA | *(SFX: Tiếng gõ bàn phím đều đặn)*<br>Mười một giờ, mình lọc toàn bộ cảnh quay thô khách gửi vào ba thư mục: câu mở đầu, bằng chứng thật và lời kêu gọi hành động. Phần nào thiếu cảnh phụ, mình mới dùng AI hỗ trợ tạo thêm. |
| **00:18 – 00:25**<br>*(Body - Buổi chiều: Dựng nháp & Nhịp cắt)* | 14:30 chiều: Cận cảnh bàn tay Thành trên chuột và bàn phím cắt A-roll, đặt điểm nhấn âm thanh và cân chỉnh màu sắc trên Premiere. | 14:30 — Cắt nhịp câu nói và đặt `[Điểm nhấn]` thị giác | *(SFX: Tiếng click chuột + tiếng cắt clip)*<br>Buổi chiều là lúc mình tập trung cắt nhịp. Mình ưu tiên để giọng nói gãy gọn, hình ảnh khớp đúng từ khóa đang nhắc tới chứ không đắp hiệu ứng thừa. |
| **00:25 – 00:32**<br>*(Body - Cuối chiều: Kiểm duyệt trên điện thoại)* | 17:30 chiều: Thành xuất bản nháp sang điện thoại, cầm điện thoại xem ở chế độ tắt tiếng và bật tiếng để kiểm tra vùng an toàn của chữ. | 17:30 — Kiểm tra vùng chữ trên `[Màn hình điện thoại]` trước khi giao | *(SFX: Tiếng ting tin nhắn)*<br>Trước khi gửi khách lúc năm rưỡi chiều, mình luôn mở video trên điện thoại để kiểm tra lại chính tả và xem chữ có bị giao diện che mất không. |
| **00:32 – 00:40**<br>*(Close & CTA)* | A-roll Thành nhìn lên ống kính trong ánh đèn bàn làm việc ấm áp lúc chiều muộn, mỉm cười nhẹ. | Có câu hỏi về quy trình dựng? `[Nhắn cho mình]` nhé | *(Nghỉ 0.5s)* Làm rõ từ đầu thì lúc dựng không phải đoán mò. Đó là cách mình dựng có chủ đích. Nếu bạn đang cần người đồng hành chuẩn hóa video cho kênh hoặc shop, cứ nhắn câu hỏi cho mình nhé. |

### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] **Shot 1 (B-roll 08:30):** Góc rộng bàn làm việc buổi sáng, cuốn sổ ghi chú và màn hình brief (đã che thông tin nhạy cảm của khách).
- [ ] **Shot 2 (B-roll 11:00):** Cận cảnh màn hình thư mục quản lý file gọn gàng (`01_Hook`, `02_Proof`, `03_CTA`).
- [ ] **Shot 3 (B-roll 14:30):** Góc máy ngang tay thao tác phím tắt trên Premiere Pro.
- [ ] **Shot 4 (B-roll 17:30):** Cảnh Thành cầm điện thoại xem lại video dọc 9:16 và tích vào checklist kiểm tra chất lượng trước bàn giao.
- [ ] **Shot 5 (A-roll):** Cảnh kết ngồi tại bàn làm việc.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
Một ngày làm việc thực tế của mình diễn ra như thế nào để mỗi video bàn giao vừa đúng tiến độ, vừa bám sát mục tiêu bán hàng của khách?
💬 Nếu bạn đang vướng ở khâu lên khung nội dung hay cắt dựng video cho kênh, cứ nhắn câu hỏi cho mình nhé.
`#dungcochudich` `#marketingvideo` `#videoeditor` `#buildinpublic`

#### B. Bài đăng Facebook cá nhân (168 chữ)
Nhiều khách hàng khi mới nhắn tin cho mình thường hỏi: "Thành ơi bên em gửi đống video quay thô qua rồi em cắt luôn giúp chị nhé?".

Thực tế, trong một ngày làm media của mình, việc mở phần mềm dựng lên cắt chỉ chiếm khoảng một nửa thời gian. Nửa thời gian còn lại nằm ở những bước chuẩn bị và kiểm soát để video ra đúng mục tiêu:
- **Buổi sáng (Lọc mục tiêu):** Đọc kỹ yêu cầu của khách để chốt đúng 1 câu trả lời: *Sau khi xem hết 35 giây này, người xem sẽ nhớ 1 ý gì và làm 1 hành động gì?*.
- **Giữa ngày (Gom & phân loại tư liệu):** Sắp xếp toàn bộ footage khách gửi theo cấu trúc Hook – Bằng chứng – CTA (những đoạn thiếu B-roll minh họa mình mới dùng AI bổ sung).
- **Cuối chiều (Kiểm duyệt trên điện thoại):** Xuất file sang màn hình điện thoại thật để kiểm tra tốc độ đọc phụ đề, lỗi chính tả và vùng an toàn hiển thị trước khi bàn giao.

Một quy trình rõ ràng giúp cả người làm lẫn khách hàng tiết kiệm hàng giờ sửa đi sửa lại. Bạn đang cần rà soát lại quy trình làm video cho shop thì nhắn mình trao đổi nhé.

---

# TUẦN 8: TỐI ƯU CHUYỂN ĐỔI & CHUẨN HÓA KHUÔN MẪU 30 GIÂY (14/12/2026 – 19/12/2026)

---

## VIDEO #29 — MÃ `C011`: SỬA CTA CUỐI VIDEO DỊCH VỤ

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Hai, 14/12/2026
- **Pillar / Tuyến nội dung:** P1 (Marketing trong video) — `MKT03` (Tối ưu CTA & Chuyển đổi)
- **Format:** Before/after (So sánh trực tiếp 2 phiên bản kết video dịch vụ trước và sau khi sửa)
- **Tệp người xem mục tiêu:** Khách hàng tiềm năng (Người làm dịch vụ, tư vấn, đào tạo, chủ doanh nghiệp nhỏ đang làm video thu hút khách hàng)
- **Mục tiêu Funnel:** Chuyển đổi (Conversion)
- **Claim duy nhất:** Câu kêu gọi "Inbox ngay để được tư vấn" tạo cảm giác sắp bị chốt sale; hãy đổi sang lời mời nhận một giá trị chẩn đoán nhỏ kèm từ khóa cụ thể để giảm rào cản nhắn tin.
- **Bằng chứng cần chuẩn bị:** Hai bản dựng 6 giây cuối của một video giới thiệu dịch vụ (Bản A: "Liên hệ hotline/inbox ngay để được tư vấn báo giá" vs Bản B: "Nhắn chữ EDIT kèm link kênh để mình gửi 3 góp ý tối ưu trước").
- **CTA & Offer:** Nhắn chữ `EDIT` kèm mục tiêu video (`Dịch vụ` Edit/Media).

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio / Voiceover) + Nhịp/SFX |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:04**<br>*(Hook - Before/After)* | Phát liền 2 giây Bản A ("Inbox ngay để được tư vấn nhé") rồi cắt xoẹt sang 2 giây Bản B ("Nhắn chữ EDIT kèm link kênh, mình gửi trước 3 điểm cần sửa"). | Đổi 1 câu cuối để khách `[Dễ mở lời]` hơn | *(SFX: Tiếng tua băng + Ding)*<br>Cùng một video dịch vụ, chỉ cần sửa lại năm giây cuối như thế này là người xem dễ nhắn tin hơn hẳn. |
| **00:04 – 00:10**<br>*(Proof / Tension)* | Dừng hình ở Bản A có chữ "Inbox ngay để được tư vấn". Khoanh đỏ cụm từ "để được tư vấn". | "Inbox để tư vấn" tạo cảm giác sắp bị `[Ép mua hàng]` | Khi bạn nói "Inbox ngay để được tư vấn", người xem thường ngại vì sợ vừa nhắn vào đã bị hỏi mua gói dịch vụ đắt tiền, và họ cũng không biết phải bắt đầu câu chuyện từ đâu. *(Nghỉ 0.5s)* |
| **00:10 – 00:21**<br>*(Body - Nguyên tắc sửa 1: Giảm rào cản)* | Trên timeline Premiere, Thành xóa dòng text cũ, gõ lại dòng text mới: "Gửi link kênh -> Nhận 3 góp ý cụ thể". | Bước 1: Đổi từ "tư vấn" sang `[Một kết quả nhỏ]` xem trước | Để gỡ tâm lý phòng thủ đó, mình sửa CTA theo hai bước. *(SFX: Typing)*<br>Một: Thay từ "tư vấn" chung chung bằng một kết quả nhỏ mà họ nhận được ngay, ví dụ: "mình xem và gửi trước ba điểm cần sửa ở ba giây đầu". |
| **00:21 – 00:31**<br>*(Body - Nguyên tắc sửa 2: Từ khóa hành động)* | Zoom vào thẻ End Card mới trên màn hình: Biểu tượng khung chat hiện sẵn cú pháp `EDIT + Link kênh`. | Bước 2: Cho sẵn `[Một từ khóa]` để khách không phải nghĩ câu mở lời | *(SFX: Pop)*<br>Hai: Đưa sẵn một từ khóa ngắn gọn để họ chỉ việc gõ theo mà không phải suy nghĩ câu chào hỏi dài dòng. |
| **00:31 – 00:40**<br>*(Close & CTA)* | Chạy lại Bản B hoàn chỉnh trong 3 giây, sau đó về A-roll Thành nhìn thẳng vào camera. | Nhắn chữ `[EDIT]` kèm link kênh để mình xem giúp 3 điểm | *(Nghỉ 0.5s)* Giảm rào cản mở lời chính là bước đầu tiên của chuyển đổi. Đó là cách mình dựng có chủ đích. Nếu bạn có sẵn kênh hoặc footage nhưng video chưa ra khách, cứ nhắn chữ EDIT kèm mục tiêu cho mình nhé. |

### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] **Shot 1 (Screen Record Before - Bản A):** Đuôi video dịch vụ với text "Inbox ngay để được tư vấn miễn phí!" và giọng đọc chung chung.
- [ ] **Shot 2 (Screen Record After - Bản B):** Đuôi video dịch vụ đã thiết kế lại End Card gọn gàng: Cú pháp nhắn tin + Món quà chẩn đoán cụ thể.
- [ ] **Shot 3 (Screen Record Premiere):** Cảnh thay đổi text layer và căn lại nhịp xuất hiện của thẻ hướng dẫn nhắn tin.
- [ ] **Shot 4 (A-roll):** Thành nói trực diện phần giải thích tâm lý người xem và lời mời cuối video.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
Tại sao video giới thiệu dịch vụ có người xem hết nhưng không ai bấm nhắn tin? Thử đổi câu "Inbox để được tư vấn" ở 5 giây cuối sang cấu trúc giảm rào cản này nhé.
📩 Nếu bạn đang có sẵn footage hoặc kênh nhưng video chưa ra đúng thông điệp muốn bán, nhắn chữ **EDIT** kèm mục tiêu video cho mình nhé.
`#dungcochudich` `#marketingvideo` `#videoediting` `#chuyendoikhachhang`

#### B. Bài đăng Facebook cá nhân (162 chữ)
Hầu hết các video giới thiệu dịch vụ (từ nha khoa, spa, tư vấn tài chính cho đến dịch vụ media) đều kết thúc bằng một câu rất quen: "Hãy inbox ngay cho chúng tôi để được tư vấn chi tiết".

Đứng ở góc độ người xem, câu nói đó vô tình dựng lên hai rào cản:
1. Họ sợ vừa nhắn vào là bị nhân viên sale hỏi dồn và chào các gói dịch vụ lớn.
2. Họ không biết phải gõ câu đầu tiên như thế nào để trình bày vấn đề của mình.

Khi dựng lại phần kết (5 giây cuối) cho các video dịch vụ, mình luôn áp dụng công thức **Đổi lời chào bán lấy một bước chẩn đoán nhỏ**:
- Thay vì nói *"Inbox để được báo giá dịch vụ dựng video"*, mình đổi thành *"Nhắn chữ EDIT kèm 1 video bạn vừa đăng, mình sẽ chỉ ra 3 điểm đang làm rơi người xem ở 5 giây đầu"*.

Khách hàng biết chính xác họ cần gõ chữ gì và sẽ nhận lại được gì mà không bị áp lực. Nếu bạn đang muốn tối ưu lại các video bán dịch vụ của mình, nhắn chữ **EDIT** cho mình nhé.

---

## VIDEO #30 — MÃ `C012`: CÔNG THỨC HOOK–BODY–CLOSE TRONG 30 GIÂY

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Ba, 15/12/2026
- **Pillar / Tuyến nội dung:** P1 (Marketing trong video) — `MKT04` (Cấu trúc kịch bản & Nhịp thông điệp)
- **Format:** Tutorial (Hướng dẫn thực hành trực tiếp trên timeline mẫu)
- **Tệp người xem mục tiêu:** Creator / Chủ shop tự quay dựng thường bị lan man, video ngắn mà kéo dài 1 phút rưỡi vẫn chưa vào ý chính
- **Mục tiêu Funnel:** Nhận biết (Awareness)
- **Claim duy nhất:** Một video 30 giây gọn gàng cần được khóa cứng bằng 3 khối màu thời lượng trên timeline: 0–3s (Hook), 3–24s (Một luận điểm + bằng chứng), và 24–30s (Kết & 1 CTA).
- **Bằng chứng cần chuẩn bị:** Timeline Premiere thực tế đã được Thành tô 3 màu Label rõ rệt: Màu Đỏ/Hồng (`00:00–00:03`), Màu Xanh Dương (`00:03–00:24`), Màu Xanh Lá (`00:24–00:30`).
- **CTA & Offer:** Nhận template cấu trúc Hook–Body–Close trong `Starter Kit` ở bio.

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio / Voiceover) + Nhịp/SFX |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03**<br>*(Hook)* | Cận cảnh timeline Premiere 30 giây được chia thành 3 khối màu cực kỳ bắt mắt (Đỏ - Xanh dương - Xanh lá). Tay Thành chỉ vào 3 khối. | Chia timeline thành `[Ba khối màu]` để không bao giờ lan man | *(SFX: Tiếng click khóa vị trí)*<br>Đây là khung ba mươi giây mình luôn dựng sẵn trên Premiere để video không bao giờ bị lan man. |
| **00:03 – 00:10**<br>*(Proof / Tension)* | So sánh với một timeline dài 1 phút 20 giây toàn một màu tím, phần mở đầu dài tận 18 giây mới vào chủ đề. | Mở đầu mất 18 giây là người xem đã `[Lướt mất]` | Nhiều bạn quay xong cứ cắt nối theo cảm tính, dẫn đến phần dẫn chuyện đầu video dài tới mười lăm, hai mươi giây mà chưa vào được ý chính. *(Nghỉ 0.5s)* |
| **00:10 – 00:17**<br>*(Body - Khối 1: 0-3s)* | Zoom vào khối màu Đỏ (`00:00–00:03`) trên timeline: Chỉ có đúng 1 câu nói và 1 hình ảnh kết quả/lỗi sai. | 0 đến 3 giây (Màu đỏ): Nêu thẳng `[Nỗi đau hoặc kết quả]` | Mình khóa chặt tỷ lệ thời lượng bằng ba khối màu như sau. *(SFX: Ding)*<br>Khối màu đỏ từ không đến ba giây: Chỉ đặt đúng một câu nêu thẳng lỗi sai hoặc kết quả cuối cùng. Tuyệt đối không chào hỏi. |
| **00:17 – 00:25**<br>*(Body - Khối 2: 3-24s)* | Zoom vào khối màu Xanh Dương (`00:03–00:24`): Gồm 1 câu giải thích nguyên nhân và 2–3 bước thao tác kèm hình ảnh chứng minh. | 3 đến 24 giây (Màu xanh): Giải quyết `[Một luận điểm]` + Bằng chứng | *(SFX: Whoosh)*<br>Khối màu xanh dương từ giây thứ ba đến hai mươi tư: Dành trọn hai mươi mốt giây này để chứng minh một luận điểm duy nhất bằng hình ảnh thật trên màn hình. |
| **00:25 – 00:32**<br>*(Body - Khối 3: 24-30s)* | Zoom vào khối màu Xanh Lá (`00:24–00:30`): Câu đúc kết ngắn + 1 thẻ CTA. | 24 đến 30 giây (Xanh lá): Chốt bài học và `[Một CTA]` | *(SFX: Pop)*<br>Và khối xanh lá sáu giây cuối: Một câu chốt lại nguyên tắc kèm đúng một lời mời hành động rõ ràng. |
| **00:32 – 00:40**<br>*(Close & CTA)* | A-roll Thành kết bài, bên cạnh hiện ảnh chụp file Template Kịch Bản 30s trong Starter Kit. | Lấy `[Template Hook-Body-Close]` trong Starter Kit ở bio | *(Nghỉ 0.5s)* Khung thời gian càng kỷ luật thì thông điệp càng sắc. Đó là cách mình dựng có chủ đích. Mình để sẵn bản Template Hook–Body–Close ba mươi giây này trong Starter Kit ở bio, bạn vào lấy về dùng ngay nhé. |

### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] **Shot 1 (Screen Record):** Timeline Premiere 30s với 3 Adjustment Layer / Color Matte đánh dấu 3 vùng: `00:00-00:03 (HOOK)`, `00:03-00:24 (1 CLAIM + PROOF)`, `00:24-00:30 (CLOSE + 1 CTA)`.
- [ ] **Shot 2 (Screen Record đối chứng):** Timeline dài lê thê không phân đoạn.
- [ ] **Shot 3 (A-roll):** Thành ngồi trước màn hình chỉ tay vào timeline và kết bài.
- [ ] **Shot 4 (B-roll tài liệu):** Trang Template Hook–Body–Close trong bộ `Starter Kit`.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
Làm sao gói trọn một ý tưởng vào đúng 30 giây mà người xem hiểu ngay và không bị ngợp? Mình chia sẵn timeline thành 3 khối màu cố định như thế này trước khi cắt.
👉 Bản **Template Hook–Body–Close** điền sẵn khung thời gian này mình để trong **Starter Kit** ở bio, bạn vào lấy về dùng nhé.
`#dungcochudich` `#videoediting` `#contentcreator` `#marketingvideo`

#### B. Bài đăng Facebook cá nhân (158 chữ)
Khi mới bắt đầu làm video ngắn, lỗi dễ mắc nhất là "nói đến đâu dựng đến đó". Bạn định làm một video 30 giây chia sẻ mẹo nhỏ, nhưng lúc ghép xong nháp đầu tiên nhìn lại đã vọt lên 1 phút 15 giây, trong đó 15 giây đầu chỉ toàn là lời dẫn nhập vòng vo.

Để rèn tính kỷ luật cho cả khâu viết kịch bản lẫn khâu cắt dựng, mình đặt sẵn 3 khối màu đánh dấu (Marker) ngay trên timeline Premiere cho mọi video 30 giây:
1. **00:00 – 00:03 (Khối Đỏ - Hook):** 1 câu dưới 12 chữ kèm hình ảnh kết quả hoặc lỗi sai trực diện. Nếu câu mở đầu tràn qua giây thứ 5, mình buộc phải cắt ngắn lại chữ.
2. **00:03 – 00:24 (Khối Xanh Dương - Body):** Chỉ triển khai 1 luận điểm duy nhất và cho người xem nhìn thấy bằng chứng (thao tác thật, so sánh trước/sau).
3. **00:24 – 00:30 (Khối Xanh Lá - Close & CTA):** 1 câu đúc kết + 1 hành động tiếp theo.

Mình đã đưa khung **Template Hook–Body–Close** này vào bộ **Starter Kit** ở bio, bạn vào lấy về làm khung sườn trước khi bấm máy nhé.

---

## VIDEO #31 — MÃ `C029`: MỘT TEXT ANIMATION ĐỂ NHẤN ĐÚNG TỪ KHÓA

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Năm, 17/12/2026
- **Pillar / Tuyến nội dung:** P2 (Edit & Storytelling) — `EDIT03` (Kỹ thuật dựng & Motion có chủ đích)
- **Format:** Screen record (Quay màn hình project After Effects / Premiere chỉ rõ keyframe và tư duy thiết kế chữ)
- **Tệp người xem mục tiêu:** Editor đang làm video ngắn (thường dùng preset chữ nhảy từng từ liên tục làm mỏi mắt người xem)
- **Mục tiêu Funnel:** Nhận biết (Awareness)
- **Claim duy nhất:** Cho cả câu phụ đề nhảy nhót liên tục sẽ làm không từ nào nổi bật; hãy giữ tĩnh câu dẫn và chỉ dùng 1 chuyển động Scale + đổi Font/Màu cho đúng từ khóa mang ý nghĩa quyết định.
- **Bằng chứng cần chuẩn bị:** Project After Effects thực tế mở sẵn Graph Editor (Speed Graph) và so sánh 2 bản: Bản 1 (mọi chữ đều pop-up nảy tưng tưng) vs Bản 2 (câu chữ đứng yên nhẹ nhàng, chỉ riêng cụm từ khóa `"Giảm 40% thời gian"` trượt nhẹ lên và khóa nét).
- **CTA & Offer:** Theo dõi hành trình (`Không bán`).

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio / Voiceover) + Nhịp/SFX |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03**<br>*(Hook)* | Split-screen: Bên trên là phụ đề nhảy tưng tưng từng chữ một (kiểu preset tự động); bên dưới là dòng chữ tĩnh sạch sẽ, chỉ có đúng cụm từ khóa bật nhẹ lên theo giọng nói. | Khi chữ nào cũng nhảy thì `[Không chữ nào]` nổi bật | *(SFX: Tiếng pop liên thanh rối tai chuyển sang 1 tiếng click gọn)*<br>Khi mọi chữ trên màn hình đều nhảy nhót, người xem sẽ không nhớ được từ khóa nào cả. |
| **00:03 – 00:10**<br>*(Proof / Tension)* | Zoom vào bản phụ đề nhảy liên tục: Mỗi giây có 4 chữ phóng to thu nhỏ đổi màu xanh đỏ vàng. | Lạm dụng preset làm mắt người xem `[Bị mệt]` sau 5 giây | Nhiều bạn áp nguyên một preset nảy chữ cho toàn bộ video. Nhìn năm giây đầu thì vui mắt, nhưng tới giây thứ mười là người xem mỏi mắt và mất tập trung vào lời nói. *(Nghỉ 0.5s)* |
| **00:10 – 00:18**<br>*(Body - Bước 1: Tách lớp chữ tĩnh và từ khóa)* | Quay màn hình After Effects: Trong câu *"Giúp bạn tiết kiệm 40% thời gian lọc cảnh"*, Thành tách phần chữ thường (Font Sans-serif trắng tĩnh) và cụm `"40% thời gian"` thành layer riêng. | Bước 1: Giữ tĩnh câu dẫn, tách riêng `[Một cụm từ khóa]` | Khi muốn nhấn mạnh một ý trên After Effects, mình làm rất tiết chế theo ba bước. *(SFX: Click)*<br>Một: Giữ nguyên phần đầu câu đứng yên với font không chân dễ đọc, và tách riêng cụm từ khóa quan trọng ra một layer độc lập. |
| **00:18 – 00:25**<br>*(Body - Bước 2: Tương phản Font/Màu có chủ đích)* | Đổi cụm `"40% thời gian"` sang màu vàng ấm hoặc đặt trên một thanh highlight hộp chữ nhật bo góc mở ngang từ trái sang phải. | Bước 2: Tạo tương phản bằng `[Thanh nền]` hoặc độ dày chữ | *(SFX: Whoosh nhẹ)*<br>Hai: Thay vì làm chữ bay vòng vèo, mình tạo độ tương phản bằng một thanh nền mở ngang phía sau cụm từ khóa để gom điểm nhìn. |
| **00:25 – 00:32**<br>*(Body - Bước 3: Keyframe & Graph Editor)* | Mở bảng Graph Editor trong AE: Chỉ đặt 2 keyframe Position/Scale trong 8 frame, kéo cần Speed Graph dốc ở đầu và êm ở cuối (Ease Out 80%). | Bước 3: Đặt 2 keyframe trong `[8 frames]` với đường cong mượt | *(SFX: Tiếng khóa nét êm)*<br>Ba: Đặt đúng hai keyframe trong khoảng tám frame, kéo đường cong tốc độ nhanh ở đầu và dừng êm ở cuối đúng nhịp giọng đọc nhấn xuống. |
| **00:32 – 00:40**<br>*(Close & CTA)* | Chạy lại đoạn video 4 giây hoàn chỉnh, sau đó chuyển về A-roll Thành. | `[Theo dõi kênh]` để xem tiếp cách dựng có chủ đích | *(Nghỉ 0.5s)* Chuyển động của chữ sinh ra là để dẫn mắt chứ không phải để khoe hiệu ứng. Đó là cách mình dựng có chủ đích. Bạn theo dõi kênh để xem tiếp các kỹ thuật dựng phục vụ thông điệp nhé. |

### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] **Shot 1 (Screen Record Before):** 1 câu thoại ngắn áp hiệu ứng pop-up/wiggle cho từng chữ một nhìn rối mắt.
- [ ] **Shot 2 (Screen Record After Effects):** Timeline comp tách riêng layer chữ dẫn và layer `[Từ khóa]` + layer Shape Box chạy `Trim Paths / Scale X`.
- [ ] **Shot 3 (Screen Record Graph Editor):** Cận cảnh đường cong Speed Graph được kéo mượt (Influence ~75–85%).
- [ ] **Shot 4 (A-roll):** Thành ngồi trước màn hình AE giải thích và chốt CTA.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
Đừng bắt mắt người xem phải đuổi theo từng chữ nhảy nhót trên màn hình. Giữ tĩnh phần câu dẫn và chỉ đặt keyframe cho đúng 1 cụm từ khóa quan trọng sẽ giúp thông điệp ghim sâu hơn nhiều.
➕ Theo dõi kênh của mình để xem tiếp series giải phẫu kỹ thuật dựng phục vụ marketing nhé.
`#dungcochudich` `#aftereffects` `#videoediting` `#typography`

#### B. Bài đăng Facebook cá nhân (152 chữ)
Một hiểu lầm khá phổ biến khi mới học motion text cho video ngắn là: Cứ phải làm cho chữ chuyển động liên tục từ giây đầu đến giây cuối thì video mới sinh động.

Thực tế, mắt người xem trên điện thoại chỉ có chưa đầy 2 giây để quét một câu chữ. Nếu chữ nào trong câu cũng nảy lên, xoay ngang hoặc đổi màu liên tục, não người xem sẽ bị quá tải thị giác và kết quả là họ không đọng lại được từ khóa nào.

Nguyên tắc làm text animation của mình trong các video marketing rất đơn giản:
1. **80% chữ trên khung hình phải đứng yên và dễ đọc:** Dùng một font không chân sạch sẽ để người xem lướt mắt qua là hiểu ngữ cảnh.
2. **Chỉ chuyển động đúng 1 cụm từ khóa mang kết quả/con số:** Tách riêng cụm từ đó, thêm thanh highlight nền phía sau và đặt 2 keyframe (khoảng 8–10 frames, kéo Speed Graph dừng êm) khớp đúng lúc giọng đọc nhấn mạnh.

Tiết chế hiệu ứng ở những chữ phụ chính là cách làm nổi bật chữ chính. Bạn đang luyện edit cứ thử áp dụng ngay ở project tiếp theo nhé.

---

## VIDEO #32 — MÃ `C047`: MỘT ẢNH SẢN PHẨM CÓ THỂ TẠO BAO NHIÊU VIDEO?

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Bảy, 19/12/2026 (Slot linh hoạt cuối tuần)
- **Pillar / Tuyến nội dung:** P3 (AI trong workflow editor) — `AI03` (Tạo B-roll & Asset hình ảnh bằng AI)
- **Format:** Experiment (Thử nghiệm thực tế và đánh giá trung thực kết quả)
- **Tệp người xem mục tiêu:** Affiliate marketer / Người làm nội dung bán hàng cần test nhiều góc video từ nguồn ảnh hạn chế
- **Mục tiêu Funnel:** Nhận biết (Awareness)
- **Claim duy nhất:** Từ 1 tấm ảnh sản phẩm gốc, bạn có thể dùng AI tạo ra 3 góc mở đầu video cho 3 tệp khách khác nhau, nhưng phải biết chọn cảnh nào dùng được ngay và cảnh nào bắt buộc phải cắt dựng lại.
- **Bằng chứng cần chuẩn bị:** 1 tấm ảnh sản phẩm gốc (ví dụ: Đèn bàn học chống cận hoặc Bình giữ nhiệt) → Đưa lên **Xưởng Media** chạy thử 3 góc bối cảnh/chuyển động khác nhau → Đặt 3 kết quả cạnh nhau, chấm điểm thật (Cảnh 1 dùng ngay, Cảnh 2 phải cắt bỏ giây cuối bị méo nhẹ, Cảnh 3 ghép cùng cảnh quay thật).
- **CTA & Offer:** Xem workflow & dùng thử công cụ (`Xưởng Media` — link ở bio).

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio / Voiceover) + Nhịp/SFX |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03**<br>*(Hook)* | Từ 1 tấm ảnh chụp chiếc bình giữ nhiệt ở giữa màn hình, tách ra thành 3 ô video chuyển động với 3 bối cảnh hoàn toàn khác nhau. | Từ `[1 ảnh gốc]` tách ra 3 góc mở đầu video khác nhau | *(SFX: Tiếng tách 3 khung hình)*<br>Từ đúng một tấm ảnh sản phẩm gốc, mình thử tạo ra ba video mở đầu cho ba nhóm khách khác nhau. |
| **00:03 – 00:10**<br>*(Proof / Tension)* | A-roll Thành cầm điện thoại có tấm ảnh gốc, sau đó chuyển sang màn hình **Xưởng Media**. | Không phải cảnh AI nào tạo ra cũng `[Dùng nguyên xi]` được | Nhiều bạn làm affiliate chỉ có ảnh từ nhãn hàng nhưng muốn test nhiều góc nội dung. Tuy nhiên, không phải video AI nào xuất ra cũng đăng lên ngay được. *(Nghỉ 0.5s)* |
| **00:10 – 00:17**<br>*(Body - Góc 1: Dân văn phòng)* | Màn hình Xưởng Media xuất Cảnh 1: Bình giữ nhiệt đặt cạnh laptop trong văn phòng hiện đại, camera đẩy nhẹ vào (Push-in). Tích xanh "Dùng ngay 3s đầu". | Góc 1 (Văn phòng): Camera đẩy nhẹ, giữ chuẩn form -> `[Dùng ngay]` | Mình test thực tế trên Xưởng Media với ba góc. *(SFX: Ding)*<br>Góc một nhắm vào dân văn phòng: Đặt sản phẩm cạnh laptop với chuyển động máy đẩy nhẹ vào. Cảnh này giữ nguyên chuẩn form sản phẩm nên dùng làm hook được ngay. |
| **00:17 – 00:25**<br>*(Body - Góc 2: Người tập thể thao)* | Cảnh 2: Bình giữ nhiệt đặt trên ghế phòng gym, có hơi nước lạnh. Ở giây thứ 4, phần nắp hơi biến dạng nhẹ. Thành kéo vào Premiere cắt bỏ 1.5s cuối. | Góc 2 (Phòng tập): Đẹp 2 giây đầu, cần `[Cắt bỏ]` đoạn cuối bị lem | *(SFX: Cut sound)*<br>Góc hai cho người tập thể thao: Hai giây đầu ánh sáng rất đẹp, nhưng tới giây thứ tư phần nắp hơi bị lem nhẹ. Mình đưa vào Premiere cắt bỏ đoạn đuôi, chỉ lấy đúng hai giây đầu. |
| **00:25 – 00:32**<br>*(Body - Góc 3: Quà tặng)* | Cảnh 3: Bối cảnh hộp quà trên bàn gỗ ấm. Ghép nối tiếp bằng cảnh tay thật mở nắp bình và bảng thông số giữ nhiệt 12 tiếng. | Góc 3 (Quà tặng): Dùng mở màn rồi nối ngay vào `[Cảnh test thật]` | *(SFX: Whoosh)*<br>Góc ba làm quà tặng: Dùng cảnh AI mở màn hai giây để gợi cảm xúc, rồi nối ngay vào cảnh test khả năng giữ nhiệt thật để tạo niềm tin. |
| **00:32 – 00:40**<br>*(Close & CTA)* | Hiển thị đồng thời 3 video hoàn chỉnh 9:16 sau khi đã qua tay Thành cắt dựng lại. Quay về A-roll Thành. | Xem workflow tạo asset trên `[Xưởng Media]` ở bio | *(Nghỉ 0.5s)* Một tấm ảnh có thể đẻ ra nhiều góc test, miễn là bạn biết gạn lọc bằng mắt của editor. Đó là cách mình dựng có chủ đích. Toàn bộ workflow trên Xưởng Media mình để sẵn ở bio cho bạn tham khảo nhé. |

### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] **Shot 1 (Asset gốc):** 1 tấm ảnh sản phẩm rõ nét (bình giữ nhiệt, tai nghe hoặc đồ gia dụng nhỏ).
- [ ] **Shot 2 (Screen Record Xưởng Media):** Quá trình nhập 3 bối cảnh khác nhau (Văn phòng / Phòng tập / Bàn quà tặng) từ cùng 1 ảnh gốc.
- [ ] **Shot 3 (Screen Record Premiere):** Cảnh Thành cắt bỏ 1.5s cuối bị lỗi artefact nhẹ ở Góc 2 và ghép nối với footage thật ở Góc 3.
- [ ] **Shot 4 (A-roll):** Thành nhận xét trung thực ưu/nhược điểm của từng output.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
Một tấm ảnh sản phẩm có thể biến thành bao nhiêu góc mở đầu video? Mình test thử 3 bối cảnh khác nhau trên Xưởng Media và chỉ rõ đoạn nào dùng được ngay, đoạn nào cần cắt lại trong Premiere.
👉 Bạn có thể xem và thử workflow tạo asset này trên **Xưởng Media** (link dùng thử có affiliate mình để ở bio).
`#dungcochudich` `#aiworkflow` `#affiliatemarketing` `#xuongmedia`

#### B. Bài đăng Facebook cá nhân (175 chữ)
Anh em làm affiliate hoặc chạy test sản phẩm mới thường gặp bài toán: Nhãn hàng chỉ cung cấp một bộ ảnh chụp studio giống hệt nhau, nếu ai cũng lấy đúng tấm ảnh đó ghép nhạc đăng lên thì video rất dễ bị trùng lặp.

Hôm nay mình làm một phép thử nhỏ: Lấy đúng 1 tấm ảnh sản phẩm gốc đưa lên **Xưởng Media** để tách thành 3 góc mở đầu (Hook) cho 3 tệp người mua khác nhau, và đây là kết quả thực tế (mất khoảng 10 phút tạo cho cả 3 cảnh):
1. **Góc 1 – Bối cảnh bàn làm việc văn phòng (Camera đẩy nhẹ):** Giữ nguyên vẹn 100% chi tiết logo và hình dáng sản phẩm, lấy ra dùng làm 3 giây mở đầu được ngay.
2. **Góc 2 – Bối cảnh phòng tập có ánh nắng xiên:** 2.5 giây đầu rất bắt mắt, nhưng 1 giây cuối khi góc máy xoay ngang thì viền nắp hơi biến dạng nhẹ. Giải pháp: Đưa vào Premiere cắt bỏ 1 giây cuối, chỉ dùng 2.5 giây đầu.
3. **Góc 3 – Bối cảnh hộp quà tặng:** Dùng 2 giây đầu để dẫn vào chủ đề quà tặng, sau đó nối ngay sang cảnh quay tay thật cầm sản phẩm.

Công cụ giúp mình nhân bản góc tiếp cận rất nhanh, nhưng khâu chọn lọc và cắt nhịp cuối cùng vẫn phải do mình kiểm soát. Bạn muốn thử nghiệm workflow này thì xem link **Xưởng Media** ở bio của mình nhé.

---

# TUẦN 9: KIỂM DUYỆT CHẤT LƯỢNG & KỶ LUẬT MỘT THÔNG ĐIỆP (21/12/2026 – 26/12/2026)

---

## VIDEO #33 — MÃ `C013`: MỘT VIDEO CHỈ NÊN CÓ MỘT CLAIM

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Hai, 21/12/2026
- **Pillar / Tuyến nội dung:** P1 (Marketing trong video) — `MKT04` (Cấu trúc kịch bản & Nhịp thông điệp)
- **Format:** Screen record kết hợp A-roll (Sửa trực tiếp một kịch bản tham lam trên màn hình)
- **Tệp người xem mục tiêu:** Creator / Chủ shop hay nhồi nhét 4–5 lợi ích sản phẩm vào cùng một video 30 giây
- **Mục tiêu Funnel:** Nhận biết (Awareness)
- **Claim duy nhất:** Một video ngắn 30 giây ôm đồm 4 luận điểm sẽ khiến người xem quên sạch sau khi lướt qua; hãy gạch bỏ 3 ý phụ để dồn toàn bộ bằng chứng vào 1 claim duy nhất.
- **Bằng chứng cần chuẩn bị:** Màn hình Google Docs / Notion chứa 1 kịch bản gốc dài 180 chữ có 4 ý (vừa giới thiệu thương hiệu, vừa kể 5 thành phần, vừa hướng dẫn cách dùng, vừa báo chương trình khuyến mãi) → Thành gạch đỏ 3 ý và tách thành 3 video riêng, chỉ giữ lại 1 trục duy nhất cho video hiện tại.
- **CTA & Offer:** Lưu video (`Không bán`).

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio / Voiceover) + Nhịp/SFX |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03**<br>*(Hook)* | Cận cảnh màn hình kịch bản có 4 đoạn tô 4 màu khác nhau. Thành kéo chuột bôi đen 3 đoạn dưới và bấm gạch ngang (Strikethrough). | Một video 30 giây chỉ nên giữ lại `[Một luận điểm]` | *(SFX: Tiếng gạch bút маркеr mạnh)*<br>Trước khi bấm máy quay hay mở Premiere, việc mình làm nhiều nhất là gạch bỏ bớt ý trong kịch bản. |
| **00:03 – 00:10**<br>*(Proof / Tension)* | Zoom vào bản kịch bản gốc của khách: Đoạn 1 kể lịch sử quán, Đoạn 2 nói nguyên liệu, Đoạn 3 chỉ đường đi, Đoạn 4 giảm giá 20%. | Nhồi 4 ý vào 30 giây làm người xem `[Không nhớ được gì]` | Đây là kịch bản ba mươi giây mình vừa nhận: vừa muốn kể câu chuyện thương hiệu, vừa liệt kê năm thành phần, vừa hướng dẫn sử dụng lại vừa báo khuyến mãi. Nhồi hết vào một video thì mỗi ý chỉ lướt qua năm giây, người xem không đọng lại được gì. *(Nghỉ 0.5s)* |
| **00:10 – 00:18**<br>*(Body - Bước 1: Chọn 1 trục đắt nhất)* | Thành giữ lại đúng Ý số 2 ("Giải quyết dứt điểm lỗi X trong 3 phút") và đóng khung màu xanh lá. | Bước 1: Giữ lại `[Một nỗi đau]` lớn nhất của người xem | Cách mình xử lý rất dứt khoát. *(SFX: Ding)*<br>Một: Chọn đúng một vấn đề mà người xem đang quan tâm nhất để làm trục chính cho video hôm nay. |
| **00:18 – 00:25**<br>*(Body - Bước 2: Biến 3 ý bị gạch thành 3 video sau)* | Kéo 3 đoạn vừa gạch bỏ sang cột bên phải có tiêu đề: `Video #2 (Cách dùng)`, `Video #3 (Thành phần)`, `Video #4 (Ưu đãi)`. | Bước 2: Cất 3 ý còn lại thành `[Ba video tiếp theo]` | *(SFX: Whoosh)*<br>Hai: Ba ý vừa gạch bỏ không hề mất đi. Mình chuyển chúng sang cột bên cạnh để làm chất liệu cho ba video tiếp theo trong tuần. |
| **00:25 – 00:32**<br>*(Body - Bước 3: Dồn thời lượng cho bằng chứng)* | Bản kịch bản sau khi sửa: Gọn đúng 90 chữ, có 15 giây ở giữa chuyên để chiếu cảnh test thực tế cho luận điểm duy nhất đó. | Bước 3: Dành 20 giây giữa video để `[Chứng minh]` cho ý đó | *(SFX: Pop)*<br>Ba: Khi chỉ còn một ý duy nhất, mình có đủ hai mươi giây ở giữa video để cho người xem nhìn thấy bằng chứng thật trên màn hình. |
| **00:32 – 00:40**<br>*(Close & CTA)* | A-roll Thành nhìn vào camera, phía sau là màn hình so sánh Bản kịch bản tham 4 ý vs Bản kịch bản 1 trục gọn gàng. | `[Lưu video]` để rà lại kịch bản trước khi bấm máy | *(Nghỉ 0.5s)* Bớt ý đi không làm video nghèo hơn, mà làm thông điệp sắc hơn. Đó là cách mình dựng có chủ đích. Bạn lưu lại nguyên tắc "một video một luận điểm" này để kiểm tra kịch bản trước khi quay nhé. |

### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] **Shot 1 (Screen Record):** Trang Notion/Google Docs mở sẵn kịch bản 4 ý (đánh số Ý 1, Ý 2, Ý 3, Ý 4 rõ ràng).
- [ ] **Shot 2 (Screen Record thao tác):** Cảnh gạch bỏ 3 ý và kéo thả sang bảng "Ngân hàng ý tưởng video tiếp theo".
- [ ] **Shot 3 (Screen Record đối chiếu):** Màn hình chia đôi Bản Trước (dài 180 chữ, 4 chủ đề) và Bản Sau (gọn 85 chữ, 1 chủ đề + 1 bằng chứng cụ thể).
- [ ] **Shot 4 (A-roll):** Thành giải thích và kết bài.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
Cảm giác tiếc ý, cái gì cũng muốn nói hết trong 1 video 30 giây chính là thủ phạm làm video mất lực. Gạch bớt 3 ý phụ đi, bạn vừa có 1 video sắc bén, vừa dư ra thêm 3 kịch bản mới.
📌 Lưu lại video này để tự kiểm tra kịch bản trước mỗi buổi quay nhé.
`#dungcochudich` `#marketingvideo` `#kichbanvideo` `#contentcreator`

#### B. Bài đăng Facebook cá nhân (160 chữ)
Khi sửa kịch bản video ngắn cho các bạn creator hoặc chủ shop, câu mình hay nói nhất là: "Kịch bản này của bạn không hề dở, chỉ là bạn đang nhét 4 video vào làm một".

Tâm lý chung của người bán hàng là sợ khách không biết hết điểm tốt của sản phẩm: nào là chất liệu nhập khẩu, đường may kỹ, có đủ 5 màu, đang được miễn phí vận chuyển lại còn được đổi trả 7 ngày. Nhưng trên nền tảng video ngắn, khi bạn nói 5 ý trong 30 giây, mỗi ý chỉ tồn tại 6 giây mà không có bất kỳ bằng chứng hình ảnh nào đủ sâu.

Quy tắc "1 Video = 1 Claim" giúp mình giải quyết cùng lúc hai việc:
1. **Tăng sức nặng cho video hiện tại:** Dành trọn 20 giây thân bài chỉ để chứng minh duy nhất 1 điểm mạnh (ví dụ: chỉ test độ chống nhăn của vải sau khi vò mạnh).
2. **Không bao giờ cạn ý tưởng:** 3–4 ý vừa cắt ra sẽ tự động trở thành chủ đề cho các video tiếp theo trong tuần.

Trước khi mở máy quay, bạn cứ thử gạch bớt một nửa số ý trong nháp xem sao nhé.

---

## VIDEO #34 — MÃ `C030`: MOTION ĐẸP NHƯNG CÓ LÀM NGƯỜI XEM HIỂU HƠN?

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Ba, 22/12/2026
- **Pillar / Tuyến nội dung:** P2 (Edit & Storytelling) — `EDIT03` (Kỹ thuật dựng & Motion có chủ đích)
- **Format:** Before/after (So sánh trực diện giữa Motion trang trí và Motion có chức năng dẫn mắt)
- **Tệp người xem mục tiêu:** Creator / Khách hàng làm kênh kiến thức, kinh doanh, dịch vụ cần truyền tải thông tin dễ hiểu
- **Mục tiêu Funnel:** Cân nhắc (Consideration)
- **Claim duy nhất:** Motion graphic đẹp mà làm người xem không biết phải nhìn vào đâu thì là hiệu ứng thừa; motion đúng phải dẫn mắt người xem đi từ vấn đề sang con số kết quả theo đúng thứ tự lời nói.
- **Bằng chứng cần chuẩn bị:** Hai phiên bản dựng cùng 1 đoạn thoại giải thích số liệu 8 giây:
  - **Phiên bản 1 (Motion trang trí):** Icon 3D xoay vòng, tia sáng chạy bốn góc, chữ bay từ 3 hướng cùng lúc làm người xem loạn mắt.
  - **Phiên bản 2 (Motion có chức năng):** Nền tối giản, Điểm A (Chi phí cũ) hiện ra trước → Đường mũi tên vẽ sang Điểm B (Chi phí sau khi tối ưu giảm 35%) đúng theo nhịp giọng đọc.
- **CTA & Offer:** Nhắn chữ `EDIT` (`Dịch vụ` Edit/Media).

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio / Voiceover) + Nhịp/SFX |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:04**<br>*(Hook - Before/After)* | Phát song song hoặc nối tiếp 2 giây Bản 1 (icon xoay, chữ bay tứ phía) và 2 giây Bản 2 (sơ đồ dẫn mắt từ A sang B cực kỳ rõ ràng). | Motion để `[Trang trí]` khác hoàn toàn với motion để `[Dẫn mắt]` | *(SFX: Tiếng xè xè rối rắm chuyển sang tiếng trượt mượt)*<br>Cùng một câu nói về con số, nhưng một bên làm người xem rối mắt, còn một bên giúp hiểu ngay trong ba giây. |
| **00:04 – 00:11**<br>*(Proof / Tension)* | Dừng hình ở Bản 1: Thành khoanh đỏ 4 chi tiết đang chuyển động cùng một lúc ở 4 góc màn hình. | 4 thứ chuyển động cùng lúc làm người xem `[Mất tiêu điểm]` | Ở bản đầu tiên, nhìn thì có vẻ rất nhiều công sức với icon xoay, viền sáng và chữ bay. Nhưng vì bốn thứ cùng nhúc nhích một lúc, mắt người xem không biết phải nhìn vào đâu. *(Nghỉ 0.5s)* |
| **00:11 – 00:19**<br>*(Body - Nguyên tắc 1: Mỗi thời điểm 1 tiêu điểm)* | Mở timeline Bản 2 trên After Effects/Premiere: Tắt bớt các icon phụ, làm tối nhẹ hậu cảnh để làm nổi bật con số chính giữa màn hình. | Bước 1: Tại một giây chỉ cho `[Một yếu tố]` chuyển động | Khi dựng lại theo hướng có chức năng, mình đổi ba điểm. *(SFX: Click)*<br>Một: Tại mỗi thời điểm trên màn hình, chỉ cho phép duy nhất một yếu tố chuyển động để khóa điểm nhìn của người xem. |
| **00:19 – 00:26**<br>*(Body - Nguyên tắc 2: Dẫn hướng từ trái sang phải / trên xuống dưới)* | Màn hình Bản 2: Khi giọng đọc nói "Từ mức 10 triệu", khối bên trái hiện lên; khi nói "giảm xuống còn 6 triệu", đường line vẽ sang khối bên phải màu xanh. | Bước 2: Dùng đường dẫn từ `[Vấn đề]` sang `[Kết quả]` | *(SFX: Whoosh nhẹ + Ding)*<br>Hai: Thay vì cho chữ bay ngẫu nhiên, mình dùng một đường nối dẫn mắt đi thẳng từ con số cũ sang con số kết quả đúng theo thứ tự câu nói. |
| **00:26 – 00:32**<br>*(Body - Nguyên tắc 3: Giữ tĩnh 1.5s sau khi hiện xong)* | Sau khi con số kết quả hiện ra, toàn bộ khung hình giữ tĩnh 1.5 giây để người xem kịp đọc xong. | Bước 3: Giữ tĩnh `[1.5 giây]` cuối để não kịp đọc số liệu | Ba: Khi con số quan trọng đã hiện ra, mình giữ nó đứng yên một giây rưỡi để người xem kịp đọc và ghi nhớ. |
| **00:32 – 00:40**<br>*(Close & CTA)* | Chạy lại Bản 2 mượt mà rồi cắt về A-roll Thành. | Nhắn chữ `[EDIT]` nếu bạn cần dựng video rõ thông điệp | *(Nghỉ 0.5s)* Motion tốt nhất là khi người xem hiểu ngay ý của bạn mà không bị hiệu ứng làm phân tâm. Đó là cách mình dựng có chủ đích. Nếu bạn muốn video của kênh vừa gọn mắt vừa rõ thông điệp, nhắn chữ EDIT cho mình nhé. |

### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] **Shot 1 (Screen Record Bản 1 - Motion trang trí):** 1 đoạn 4 giây có nhiều layer glow, icon lắc lư, chữ xuất hiện cùng lúc ở nhiều góc.
- [ ] **Shot 2 (Screen Record Bản 2 - Motion có chức năng):** Cùng câu thoại đó nhưng trình bày bằng 2 khối so sánh Trước → Sau rõ ràng, có khoảng dừng 1.5s để đọc.
- [ ] **Shot 3 (Screen Record Timeline):** Cảnh tắt các layer trang trí thừa và căn lại thứ tự xuất hiện (stagger layers) theo waveform giọng nói.
- [ ] **Shot 4 (A-roll):** Thành phân tích sự khác biệt và mời nhắn chữ `EDIT`.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
Hiệu ứng đẹp đến mấy mà làm người xem quên mất bạn đang nói gì thì vẫn là hiệu ứng thừa. Đây là cách mình sửa một đoạn motion "trang trí" thành motion "dẫn mắt" giúp người xem nắm bắt con số ngay lập tức.
📩 Nếu bạn có sẵn nội dung hoặc footage nhưng cần người dựng làm nổi bật đúng thông điệp bán hàng, nhắn chữ **EDIT** cho mình nhé.
`#dungcochudich` `#motiongraphics` `#videoediting` `#marketingvideo`

#### B. Bài đăng Facebook cá nhân (165 chữ)
Mình từng xem nhiều video chia sẻ kiến thức kinh doanh hoặc giới thiệu giải pháp có phần hậu kỳ cực kỳ cầu kỳ: icon 3D bay lượn ở bốn góc, tia sáng chạy dọc khung hình, chữ lật liên tục. Nhưng xem xong 30 giây, hỏi lại video vừa nói về con số nào thì hầu như không ai nhớ.

Lý do rất đơn giản: **Sự chú ý của người xem là hữu hạn**. Khi trên màn hình có 4 vật thể cùng chuyển động tại một thời điểm, mắt người xem sẽ bị phân tán thay vì tập trung vào thông điệp chính.

Khi dựng motion cho các video giải thích hoặc bán hàng, mình luôn tự hỏi hiệu ứng này có giúp người xem **hiểu nhanh hơn** không, dựa trên 3 quy tắc:
1. **Mỗi thời điểm chỉ có 1 điểm chuyển động chính:** Cái gì đang được nhắc đến trong giọng nói thì cái đó mới xuất hiện.
2. **Chuyển động phải có hướng dẫn dắt:** Đi từ Nguyên nhân → Kết quả, hoặc từ Trước → Sau.
3. **Luôn có nhịp nghỉ 1–1.5 giây:** Để mắt người xem kịp đọc hết con số trước khi chuyển cảnh.

Nếu bạn đang cần dựng lại các video chuyên môn/bán hàng sao cho gãy gọn và dễ hiểu, nhắn chữ **EDIT** cho mình nhé.

---

## VIDEO #35 — MÃ `C048`: AI VIDEO NÀO DÙNG ĐƯỢC, VIDEO NÀO PHẢI BỎ?

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Năm, 24/12/2026
- **Pillar / Tuyến nội dung:** P3 (AI trong workflow editor) — `AI03` (Tạo B-roll & Asset hình ảnh bằng AI)
- **Format:** Review / Kiểm duyệt thực tế (Soi lỗi và chấm điểm nhiều output video AI trên màn hình)
- **Tệp người xem mục tiêu:** Creator / Editor đang dùng AI tạo B-roll nhưng hay đưa cả những cảnh lỗi biến dạng vào video làm giảm uy tín kênh
- **Mục tiêu Funnel:** Cân nhắc (Consideration)
- **Claim duy nhất:** Đừng đưa mọi video AI vừa tạo xong vào timeline; hãy lọc qua 3 tiêu chí kiểm duyệt của editor (độ nhất quán vật thể, hướng chuyển động tự nhiên, và lỗi biến dạng chữ/bàn tay) để biết cảnh nào giữ, cảnh nào bỏ.
- **Bằng chứng cần chuẩn bị:** 4–6 đoạn output video thực tế tạo trên **Xưởng Media** (có cả bản đạt chuẩn rất mượt và bản bị lỗi biến dạng ngón tay/chữ trên bao bì/vật thể tự mọc thêm) đặt trên màn hình Premiere để Thành duyệt trực tiếp.
- **CTA & Offer:** Lưu checklist kiểm duyệt & xem công cụ (`Xưởng Media` — link ở bio).

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio / Voiceover) + Nhịp/SFX |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03**<br>*(Hook)* | Màn hình lưới 4 đoạn video AI vừa tạo xong: Thành tích xanh 2 ô và gạch đỏ 2 ô bị lỗi. | 3 tiêu chí để biết cảnh AI nào `[Dùng được]`, cảnh nào `[Phải bỏ]` | *(SFX: Tiếng đóng dấu Duyệt / Loại)*<br>Khi dùng AI tạo cảnh phụ cho video, làm sao biết đoạn nào dùng được, đoạn nào bắt buộc phải bỏ? |
| **00:03 – 00:10**<br>*(Proof / Tension)* | Zoom vào 1 đoạn video AI mà chiếc ly cà phê đang cầm trên tay tự nhiên biến thành hình dạng khác ở giây thứ 3. | Một cảnh AI bị biến dạng sẽ làm giảm `[Độ tin cậy]` của cả video | Chỉ cần để lọt một giây hình ảnh bị méo mó hay giả tạo vào video bán hàng, người xem sẽ mất thiện cảm với cả sự chỉn chu của thương hiệu. *(Nghỉ 0.5s)* |
| **00:10 – 00:18**<br>*(Body - Tiêu chí 1: Độ nhất quán vật thể - Continuity)* | So sánh 2 clip trên màn hình: Clip trái (sản phẩm bị đổi tỷ lệ khi xoay góc) -> Loại; Clip phải (sản phẩm giữ nguyên form từ đầu đến cuối) -> Giữ. | Tiêu chí 1: Vật thể phải giữ nguyên `[Hình dáng và tỷ lệ]` | Trước khi kéo bất kỳ clip AI nào từ Xưởng Media vào Premiere, mình luôn soi qua ba tiêu chí này. *(SFX: Ding)*<br>Một là độ nhất quán vật thể: Khi máy quay di chuyển, hình dáng và tỷ lệ sản phẩm không được tự ý phình to hay co nhỏ lại. |
| **00:18 – 00:25**<br>*(Body - Tiêu chí 2: Hướng chuyển động tự nhiên)* | Xem 1 clip khói trà bốc lên hoặc ánh nắng di chuyển nhẹ (tự nhiên) so với clip nước chảy ngược hoặc chuyển động giật cục. | Tiêu chí 2: Hướng chuyển động phải đúng `[Vật lý tự nhiên]` | *(SFX: Whoosh)*<br>Hai là hướng chuyển động: Ánh sáng, khói hay chuyển động máy phải êm và thuận theo vật lý tự nhiên. Cảnh nào chuyển động quá gắt thường dễ lộ nét giả. |
| **00:25 – 00:32**<br>*(Body - Tiêu chí 3: Lỗi chữ & bàn tay - Artefact)* | Khoanh đỏ vào phần chữ trên nhãn sản phẩm hoặc ngón tay người nếu bị nhòe/dư ngón. Chỉ giữ lại những góc quay cận sản phẩm hoặc trung cảnh không bị lỗi chi tiết. | Tiêu chí 3: Kiểm tra kỹ `[Chữ trên nhãn]` và chi tiết bàn tay | *(SFX: Click)*<br>Ba là soi kỹ lỗi biến dạng ở hai vị trí nhạy cảm nhất: chữ in trên bao bì và bàn tay con người. Nếu bị nhòe chữ, phải loại ngay hoặc thay bằng góc quay khác. |
| **00:32 – 00:40**<br>*(Close & CTA)* | Hiện bảng Checklist 3 tiêu chí kiểm duyệt AI Video gọn gàng trên màn hình, sau đó về A-roll Thành. | `[Lưu checklist]` này lại và xem thử Xưởng Media ở bio | *(Nghỉ 0.5s)* AI tạo ra mười cảnh, editor giỏi là người biết chọn đúng ba cảnh đạt chuẩn nhất. Đó là cách mình dựng có chủ đích. Bạn lưu lại checklist này để lọc cảnh, và có thể test thử tạo B-roll trên Xưởng Media ở bio của mình nhé. |

### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] **Shot 1 (Screen Record Grid 4 Clips):** 2 clip AI chất lượng tốt (chuyển động camera chậm, giữ chuẩn vật thể) và 2 clip có lỗi điển hình (morphing hình dáng, nhòe chữ hoặc lỗi ngón tay) tạo từ các lần thử trên Xưởng Media.
- [ ] **Shot 2 (Screen Record Zoom-in):** Khoanh vùng cụ thể điểm lỗi ở giây thứ 2–3 để người xem nhìn thấy bằng mắt thường.
- [ ] **Shot 3 (Graphic Card):** Bảng tóm tắt "3 Tiêu Chí Duyệt Video AI Của Editor: 1. Continuity (Độ nhất quán) — 2. Motion (Chuyển động tự nhiên) — 3. Artefact (Chữ & Bàn tay)".
- [ ] **Shot 4 (A-roll):** Thành ngồi trước màn hình kết bài trung thực.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
Đừng để một cảnh AI bị biến dạng làm hỏng cả video tâm huyết của bạn. Đây là 3 tiêu chí kiểm duyệt mình luôn dùng để lọc B-roll trước khi đưa vào timeline Premiere.
📌 Lưu lại checklist 3 tiêu chí này nhé. Bạn nào muốn thử tạo B-roll thì mình để sẵn link **Xưởng Media** (có affiliate) ở bio.
`#dungcochudich` `#aiworkflow` `#videoediting` `#xuongmedia`

#### B. Bài đăng Facebook cá nhân (172 chữ)
Khi ứng dụng AI để tạo thêm các cảnh phụ (B-roll) cho video, sai lầm lớn nhất là tâm lý "tạo xong thấy chuyển động được là bê nguyên xi vào video".

Khán giả bây giờ rất tinh mắt. Chỉ cần trong video xuất hiện 2 giây cảnh bàn tay có 6 ngón, chữ trên vỏ hộp bị nhòe thành ký tự lạ, hoặc cái ly đang tròn bỗng méo đi khi xoay góc máy, họ sẽ lập tức cảm thấy nội dung này thiếu chỉn chu.

Khi tạo B-roll trên **Xưởng Media** để phục vụ công việc dựng phim, mình luôn đóng vai người kiểm duyệt với 3 bộ lọc bắt buộc:
1. **Độ nhất quán vật thể (Continuity):** Sản phẩm từ giây thứ nhất đến giây thứ ba có giữ nguyên tỷ lệ và thiết kế không?
2. **Chuyển động vật lý tự nhiên:** Mình ưu tiên những chuyển động máy chậm (slow pan/push-in) và ánh sáng môi trường thay vì bắt AI làm các chuyển động phức tạp dễ lộ lỗi.
3. **Soi lỗi Artefact (Chữ & Bàn tay):** Nếu cảnh nào bị biến dạng chữ trên bao bì, mình bỏ ngay lập tức hoặc chỉ cắt lấy đúng 2 giây đầu chưa bị biến dạng.

Bạn lưu lại 3 tiêu chí này để lọc tư liệu, và có thể trải nghiệm thử **Xưởng Media** qua link ở bio của mình nhé.

---

## VIDEO #36 — MÃ `C059`: SAI LẦM LỚN NHẤT KHI MỚI NHẬN JOB EDIT

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Bảy, 26/12/2026 (Slot linh hoạt cuối tuần — Khép lại Sprint 3)
- **Pillar / Tuyến nội dung:** P4 (Hành trình & Bằng chứng) — `JRN04` (Bài học nghề & Sai lầm thực tế)
- **Format:** Reflection (Chia sẻ bài học xương máu từ trải nghiệm thật kèm quy trình khắc phục cụ thể)
- **Tệp người xem mục tiêu:** Editor mới vào nghề (và cả khách hàng để thấy sự chín chắn trong tư duy làm việc của Thành)
- **Mục tiêu Funnel:** Tin cậy (Trust)
- **Claim duy nhất:** Sai lầm tốn thời gian nhất khi mới nhận job edit là lao vào cắt dựng ngay khi chưa hỏi rõ mục tiêu video của khách; hãy khóa 3 câu hỏi trước khi mở Premiere để không phải đập đi dựng lại từ đầu.
- **Bằng chứng cần chuẩn bị:** Hình ảnh thư mục project cũ có tới 5 bản xuất (`Final_v1`, `Final_v2`, `Final_sua_theo_khach_v3`, `Final_chot_v4`...) so sánh với bảng **3 câu hỏi chốt Brief trước khi dựng** mà Thành đang áp dụng hiện tại.
- **CTA & Offer:** Lưu bài học (`Không bán`).

### 2. Bảng kịch bản sản xuất chi tiết (00:00 – 00:40)

| Timecode | Hình ảnh / Thao tác màn hình (Visual) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio / Voiceover) + Nhịp/SFX |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:03**<br>*(Hook)* | Cận cảnh màn hình thư mục chứa hàng loạt file xuất: `Video_Final_1.mp4`, `Video_Final_2_sua_lai_het.mp4`, `Video_Final_chot_thuc_su.mp4`. Cắt sang A-roll Thành. | Sai lầm khiến mình từng phải `[Dựng lại từ đầu]` cả video | *(SFX: Tiếng thở dài nhẹ + tiếng click chuột)*<br>Sai lầm lớn nhất của mình hồi mới nhận job edit là vừa nhận file quay xong đã mở Premiere lên cắt ngay. |
| **00:03 – 00:11**<br>*(Proof / Tension)* | A-roll Thành kể lại câu chuyện thật, xen cảnh timeline một bản dựng nhịp nhanh sôi động bị khách phản hồi "Chị cần video sâu sắc để tuyển đại lý chứ không phải bán lẻ". | Dựng xong hết mới biết mình đi `[Lệch mục tiêu]` của khách | Có lần mình thức cả buổi tối cắt một video nhịp cực nhanh, nhạc sôi động để bán lẻ. Đến khi gửi bản nháp, khách mới bảo: "Video này chị dùng để tạo uy tín tuyển đối tác, không phải video chốt đơn giá rẻ". Thế là phải đập đi dựng lại toàn bộ cấu trúc. *(Nghỉ 0.5s)* |
| **00:11 – 00:18**<br>*(Body - Câu hỏi 1: Mục tiêu & Tệp người xem)* | Mở bảng "3 Câu Hỏi Trước Khi Mở Premiere" trên màn hình Notion của Thành. Highlight Câu số 1. | Câu hỏi 1: Video này nói với `[Ai]` và ở giai đoạn nào? | Từ sau lần đó, mình tự đặt quy tắc phải rõ ba câu hỏi này với khách trước khi đụng vào timeline. *(SFX: Ding)*<br>Một: Video này đang nói chuyện với khách lạ mới biết kênh hay khách đã theo dõi lâu rồi? |
| **00:18 – 00:25**<br>*(Body - Câu hỏi 2: Một thông điệp giữ lại)* | Highlight Câu số 2 trên bảng Notion kèm ví dụ cụ thể. | Câu hỏi 2: Xem xong 30 giây, khách cần nhớ `[Đúng 1 ý gì]`? | *(SFX: Pop)*<br>Hai: Sau khi xem hết ba mươi giây, đâu là một ý duy nhất anh chị muốn người xem nhớ nhất? |
| **00:25 – 00:32**<br>*(Body - Câu hỏi 3: Hành động tiếp theo - CTA)* | Highlight Câu số 3 trên bảng Notion: Chốt rõ 1 hành động ở 5 giây cuối. | Câu hỏi 3: Cuối video muốn người xem `[Làm hành động gì]`? | *(SFX: Click)*<br>Và ba: Ở năm giây cuối cùng, anh chị muốn họ bấm lưu bài, lấy tài liệu hay nhắn tin theo từ khóa nào? |
| **00:32 – 00:40**<br>*(Close & CTA)* | Quay lại A-roll Thành với màn hình thư mục hiện tại chỉ gọn gàng `Draft_01` và `Final_Approved`. | `[Lưu lại 3 câu hỏi]` này để không phải sửa đi sửa lại | *(Nghỉ 0.5s)* Tốn mười phút hỏi kỹ từ đầu sẽ cứu cho bạn cả một ngày sửa đi sửa lại. Đó là cách mình dựng có chủ đích. Bạn nào mới nhận job edit nhớ lưu lại ba câu hỏi này để dùng trước mỗi dự án nhé. |

### 3. Checklist Shot List cần quay / chuẩn bị
- [ ] **Shot 1 (Screen Record):** Thư mục project có 4–5 file xuất đặt tên `Final_v1`, `Final_v2`, `Final_v3_sua_lai` (minh họa nỗi đau sửa nhiều lần vì lệch hướng).
- [ ] **Shot 2 (A-roll):** Thành ngồi chia sẻ chân thành câu chuyện bài học nghề của chính mình.
- [ ] **Shot 3 (Screen Record Notion):** Bảng "Checklist 3 Câu Hỏi Chốt Trước Khi Mở Premiere" sạch sẽ, rõ ràng.
- [ ] **Shot 4 (Screen Record đối chứng):** Thư mục bàn giao gọn gàng chỉ gồm `01_Brief_Chot`, `02_Draft_v1`, `03_Final`.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok / Facebook Reels
Nhận footage xong lao vào cắt ngay tưởng là nhanh, nhưng lệch mục tiêu của khách thì phải dựng lại từ con số 0. Đây là 3 câu hỏi mình luôn chốt rõ trước khi mở Premiere.
📌 Lưu lại bài học này để áp dụng ngay ở job tiếp theo của bạn nhé.
`#dungcochudich` `#videoeditor` `#freelanceeditor` `#marketingvideo`

#### B. Bài đăng Facebook cá nhân (174 chữ)
Hồi mới bắt đầu nhận các job dựng video bên ngoài, mình từng nghĩ một editor nhiệt tình là người vừa nhận được link Google Drive chứa footage của khách lúc 8 giờ tối thì 11 giờ đêm đã cắt xong bản nháp đầu tiên gửi qua.

Nhưng chính sự vội vàng đó từng làm mình trả giá bằng việc phải thức trắng để dựng lại từ đầu. Mình chọn nhạc nhanh, cắt nhịp dồn dập theo kiểu video bán lẻ, trong khi mục đích thật sự của khách ở video đó là chia sẻ câu chuyện làm nghề trầm tĩnh để tạo niềm tin với đối tác lớn.

Bài học lớn nhất mình rút ra sau gần một năm làm nghề: **Đừng bao giờ mở Premiere khi chưa chốt xong 3 câu hỏi với khách hàng**:
1. Video này dành cho người mới biết đến thương hiệu hay người đang phân vân mua hàng?
2. Trong toàn bộ buổi quay này, đâu là 1 luận điểm quan trọng nhất cần giữ lại làm trục chính?
3. Kết thúc video, chúng ta muốn người xem thực hiện đúng 1 hành động cụ thể nào?

Dành 10 phút thống nhất mục tiêu trước khi cắt sẽ giúp cả editor lẫn khách hàng tiết kiệm hàng giờ sửa chữa. Bạn nào mới vào nghề lưu lại 3 câu hỏi này nhé.

---

## TỔNG KẾT & NGHIỆM THU SPRINT 3 (TUẦN 07 – TUẦN 09)

1. **Đảm bảo đúng tỷ trọng Pillar & Phễu của Sprint 3:**
   - **P1 (Marketing trong video):** 4 video (`C010`, `C011`, `C012`, `C013`) — Chuẩn hóa hệ thống CTA 3 tầng, sửa CTA dịch vụ, khuôn mẫu 30s Hook–Body–Close, và kỷ luật 1 video 1 claim.
   - **P2 (Edit & Storytelling):** 3 video (`C028`, `C029`, `C030`) — Phân ranh Premiere vs After Effects, kỹ thuật nhấn từ khóa bằng text animation tiết chế, và so sánh motion trang trí vs motion dẫn mắt.
   - **P3 (AI trong workflow editor):** 3 video (`C046`, `C047`, `C048`) — Quy trình tạo asset từ ảnh tĩnh trên **Xưởng Media** đưa vào Premiere, thử nghiệm nhân bản 3 góc nội dung từ 1 ảnh gốc, và bộ 3 tiêu chí kiểm duyệt video AI.
   - **P4 (Hành trình & Bằng chứng):** 2 video (`C058`, `C059`) — Nhật ký một ngày làm media thực tế và bài học xương máu 3 câu hỏi chốt brief trước khi mở Premiere.
2. **Điểm kiểm tra chất lượng cuối Tuần 9 (Chuẩn bị bước vào Sprint 4 — Thu hoạch & Chuyển đổi):**
   - Thống kê tỷ lệ giữ chân ở giây thứ 3 (`3s View Rate`) và thời lượng xem trung bình của 36 video đã đăng.
   - Tổng hợp số lượt nhận `Starter Kit`, số lượt bấm link `Xưởng Media`, và số tin nhắn từ khóa `EDIT` để chọn ra các định dạng thắng cuộc đưa vào Sprint 4.

<!-- ===== /file: personal-brand-video-engine/references/01_Y_TUONG_VA_SCRIPT/03_SPRINT_3_TUAN_07_09_TOI_UU_HE_THONG.md ===== -->

<!-- ===== file: personal-brand-video-engine/references/01_Y_TUONG_VA_SCRIPT/04_SPRINT_4_TUAN_10_12_CHUYEN_DOI.md ===== -->

# SPRINT 4 (TUẦN 10 – TUẦN 12): CHUYỂN ĐỔI OFFER & KHÓA HỆ THỐNG 48 VIDEO
**Thời gian thực thi:** `28/12/2026 – 16/01/2027`
**Trọng tâm chiến lược:** Chuyển hóa lượng người xem đã tích lũy từ 3 Sprint đầu thành người nhận **Starter Kit** (Lead Magnet) và khách hàng hỏi **Dịch vụ Edit/Media**, đồng thời khẳng định vị thế thực chiến của Thành qua chuỗi phân tích sâu **"AI làm thô, Editor làm tinh"**, kỹ thuật **Pacing / Sound Design / Subtitle** và **Audit video bán hàng thực tế**.

> **Quy chuẩn áp dụng xuyên suốt (`brand-voice` + `content-engine` + `crosspost`):**
> - **Xưng hô:** Xưng *"mình"*, gọi người xem là *"bạn"*. Không mở đầu bằng lời chào sáo rỗng, vào thẳng vấn đề hoặc kết quả ngay giây `00:00`.
> - **Độ nén (Compression):** Mỗi video chỉ giải quyết đúng **1 vấn đề — 1 claim — 1 tệp người xem — 1 CTA**.
> - **On-screen Text:** Viết hoa chữ cái đầu mỗi dòng, nằm trong vùng an toàn (Safe Zone), mỗi khung hình chỉ nhấn đậm **1 cụm từ khóa duy nhất**.
> - **Phân phối đa kênh (`crosspost`):** Tách biệt hoàn toàn Caption TikTok, Caption Facebook Reels và Bài viết dài trên Facebook cá nhân (120–180 chữ, có số liệu/ngữ cảnh thực tế, không dùng câu hỏi câu tương tác giả tạo ở cuối bài).

---

## TỔNG QUAN DANH MỤC 12 VIDEO SPRINT 4 (VIDEO #37 – #48)

| STT | Mã | Ngày đăng | Thứ | Pillar & Tuyến | Format | Tệp mục tiêu | Funnel | Offer & CTA |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **37** | `C014` | 28/12/2026 | Thứ Hai | P1 - MKT04 | Whiteboard | Creator | Nhận biết | **Starter Kit** — Nhận worksheet |
| **38** | `C015` | 29/12/2026 | Thứ Ba | P1 - MKT04 | BTS | Creator | Cân nhắc | **Starter Kit** — Nhận mẫu shot list |
| **39** | `C031` | 31/12/2026 | Thứ Năm | P2 - EDIT04 | Breakdown | Editor | Nhận biết | **Không bán** — Lưu bài học |
| **40** | `C049` | 02/01/2027 | Thứ Bảy *(Linh hoạt)* | P3 - AI04 | Before/after | Khách hàng | Cân nhắc | **Dịch vụ** — Theo dõi series |
| **41** | `C016` | 04/01/2027 | Thứ Hai | P1 - MKT05 | Breakdown | Marketer | Nhận biết | **Không bán** — Theo dõi series |
| **42** | `C032` | 05/01/2027 | Thứ Ba | P2 - EDIT04 | Tutorial | Editor | Nhận biết | **Starter Kit** — Nhận checklist |
| **43** | `C033` | 07/01/2027 | Thứ Năm | P2 - EDIT04 | Remake | Creator | Nhận biết | **Không bán** — Theo dõi series |
| **44** | `C050` | 09/01/2027 | Thứ Bảy *(Linh hoạt)* | P3 - AI04 | Audit | Creator | Nhận biết | **Không bán** — Lưu video |
| **45** | `C017` | 11/01/2027 | Thứ Hai | P1 - MKT05 | Audit | Chủ shop | Cân nhắc | **Dịch vụ** — Nhắn EDIT |
| **46** | `C034` | 12/01/2027 | Thứ Ba | P2 - EDIT05 | Audit | Creator | Nhận biết | **Starter Kit** — Nhận checklist |
| **47** | `C035` | 14/01/2027 | Thứ Năm | P2 - EDIT05 | Before/after | Editor | Nhận biết | **Không bán** — Lưu video |
| **48** | `C051` | 16/01/2027 | Thứ Bảy *(Linh hoạt)* | P3 - AI04 | Case study | Khách hàng | Tin cậy | **Dịch vụ** — Nhắn EDIT |

---

# TUẦN 10: HỆ THỐNG HÓA TIỀN KỲ & KHỞI ĐỘNG SERIES "AI LÀM THÔ, EDITOR LÀM TINH"
*(28/12/2026 – 02/01/2027)*

---

## VIDEO 37 — MÃ `C014`: CÁCH BIẾN MỘT Ý TƯỞNG THÀNH NĂM GÓC NỘI DUNG

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Hai, 28/12/2026
- **Pillar / Tuyến nội dung:** P1 (Marketing trong video) — `MKT04` (Kịch bản, cấu trúc & phát triển ý tưởng)
- **Format:** Whiteboard (Sơ đồ bảng trắng / iPad / Notion trực quan)
- **Tệp người xem:** Creator (Người xây kênh cá nhân, chuyên gia tự làm nội dung hay bị bí ý tưởng sau 1–2 tuần đầu)
- **Mục tiêu Funnel:** Nhận biết (Awareness → Thu hút tải tài liệu)
- **Claim duy nhất:** Bạn không thiếu ý tưởng quay video, bạn chỉ đang tiêu xài một chủ đề tốt vào đúng một góc nói duy nhất rồi bỏ phí bốn góc còn lại.
- **Bằng chứng cần chuẩn bị:** Trang Worksheet *"1 Ý Tưởng → 5 Góc Nội Dung"* đã điền sẵn 1 ví dụ thực tế (Chủ đề gốc: *"Quay video giới thiệu sản phẩm tại nhà"*).
- **CTA & Offer:** Nhận Worksheet trong **Starter Kit** ở bio.

### 2. Bảng kịch bản chi tiết (Thời lượng: ~38 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác màn hình (Visual & Timeline) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) & SFX/Nhịp |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | Cận cảnh tay Thành gạch bỏ dòng chữ *"Tìm 5 chủ đề mới mỗi tuần"* trên bảng trắng, rồi vẽ 1 vòng tròn ở giữa nối ra 5 nhánh rõ ràng. | Đừng tìm năm chủ đề mới, hãy tách **một ý tưởng thành năm góc** | *(Nhịp nhanh, dứt khoát)* Bạn bị bí ý tưởng không phải vì thiếu chuyện để kể, mà vì bạn mới khai thác một phần năm giá trị của chủ đề đó. `[SFX: Tiếng bút dạ gạch giấy sột soạt]` |
| `00:03 – 00:10` | **2. PROOF / TENSION** | A-roll Thành cầm bảng Worksheet in sẵn, chỉ vào cột bên trái (chỉ có 1 dòng tiêu đề chung chung) đối chiếu với cột bên phải (5 ô kịch bản cụ thể). | Một chủ đề nói chung chung chỉ ra được **một video duy nhất** | Ví dụ bạn định làm chủ đề tự quay sản phẩm tại nhà. Nếu gom hết vào một clip bốn mươi giây, bạn nói vừa nông vừa hết sạch vốn cho tuần sau. `[Nghỉ 0.4s]` |
| `00:10 – 00:17` | **3. BODY (Góc 1 & 2)** | Cut cận vào nhánh số 1 và số 2 trên bảng trắng. Thành viết nhanh từ khóa và chèn 2 khung hình ví dụ nhỏ ở góc phải màn hình. | Góc 1: **Vấn đề thường gặp**<br>Góc 2: **Lỗi sai phổ biến** | Khi tách vào worksheet, mình chia làm năm góc. Góc một là vấn đề thường gặp: quay ở phòng hẹp bị tối mặt. Góc hai là lỗi sai phổ biến: bật đèn trần làm bóng đổ dưới mắt. `[SFX: Pop nhẹ khi hiện nhánh 1-2]` |
| `00:17 – 00:25` | **3. BODY (Góc 3 & 4)** | Camera pan nhẹ sang nhánh số 3 và số 4 trên bảng. B-roll chèn nhanh cảnh Thành đặt đèn 45 độ (Góc 3) và cảnh so sánh trước/sau của 1 khách hàng thật (Góc 4). | Góc 3: **Cách làm từng bước**<br>Góc 4: **Case thực tế** | Góc ba mới là hướng dẫn từng bước cách đặt một chiếc đèn chếch bốn lăm độ. Góc bốn là case thực tế: mình sửa đúng góc đèn đó cho một shop phụ kiện như thế nào. |
| `00:25 – 00:32` | **3. BODY (Góc 5)** | Cận cảnh nhánh số 5 trên bảng trắng, sau đó zoom out toàn bộ sơ đồ 5 nhánh hoàn chỉnh trên trang Worksheet Notion/PDF. | Góc 5: **Quan điểm nghề nghiệp** | Và góc năm là quan điểm làm nghề: vì sao ánh sáng rõ sản phẩm quan trọng hơn việc mua máy ảnh đắt tiền. `[Nghỉ 0.6s]` Một ý tưởng gốc đã thành lịch đăng cả tuần. |
| `00:32 – 00:38` | **4. CLOSE & CTA** | A-roll Thành nhìn thẳng ống kính, đặt nhẹ bút xuống bàn. Màn hình hiện Pop-up minh họa file Worksheet trong bộ Starter Kit. | Tải **worksheet 5 góc nội dung** trong Starter Kit ở bio | Đó là cách mình lên kịch bản có chủ đích. Mình để sẵn bản worksheet năm góc nội dung này trong Starter Kit ở bio, bạn vào lấy về điền thử ngay nhé. |

### 3. Checklist Shot List cần quay/chụp
- [ ] **Shot 1 (B-roll / Hook):** Cận cảnh từ trên xuống (Top-down) bàn làm việc: tay Thành cầm bút dạ đen gạch dòng chữ *"Tìm 5 chủ đề mới"* và khoanh vào sơ đồ 5 nhánh.
- [ ] **Shot 2 (A-roll chính):** Thành ngồi trước bàn làm việc, góc máy ngang tầm mắt, cầm tờ Worksheet in giấy A4 chỉ trực tiếp vào bảng.
- [ ] **Shot 3 (B-roll cận bảng/iPad):** Quay cận từng nhánh 1 → 5 khi Thành viết chữ hoặc tick dấu kiểm tra.
- [ ] **Shot 4 (Screen Record):** Quay màn hình file Worksheet trên Notion/Google Sheets đã điền mẫu chủ đề *"Tự quay sản phẩm tại nhà"* để ghép PiP ở giây `00:25–00:38`.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok
```text
Bí ý tưởng khi xây kênh thường không phải vì bạn hết chuyện để nói, mà vì bạn gom cả 5 góc khai thác nhồi vào đúng 1 video rồi bỏ luôn chủ đề đó.
Mình để sẵn bản Worksheet tách 1 ý tưởng thành 5 góc nội dung trong Starter Kit ở bio, bạn vào lấy về dùng ngay cho lịch đăng tuần này nhé.
#dungcochudich #xaykenhtiktok #contentcreator #marketingvideo
```

#### B. Caption Facebook Reels
```text
Nhiều bạn tự quay video xây kênh hay bị kẹt ở tuần thứ 3: cảm giác những gì mình biết đã nói hết trong 4-5 clip đầu tiên rồi.
Thực ra 1 chủ đề tốt luôn có đủ 5 góc để bóc tách: từ triệu chứng người xem hay gặp, lỗi sai phổ biến, cách làm từng bước, ví dụ thực tế cho tới góc nhìn làm nghề của bạn.
Mình có đóng gói sẵn mẫu Worksheet 5 góc này trong bộ Starter Kit (link ở phần giới thiệu trang cá nhân), bạn tải về điền thử 1 chủ đề sẽ thấy nhẹ đầu hơn rất nhiều.
#dungcochudich #videoediting #contentmarketing #xaykenhcanhan
```

#### C. Bài đăng Facebook cá nhân (Viết riêng — 165 chữ)
```text
Tuần trước ngồi rà lại lịch nội dung cùng một bạn đang tự xây kênh chuyên môn, mình thấy bạn liệt kê được 6 chủ đề rồi dừng lại bảo: "Em hết cái để nói rồi anh ạ."

Khi mình mở từng chủ đề ra xem, hóa ra bạn đang gom cả một mảng kiến thức lớn nhồi vào đúng một chiếc video 45 giây. Làm vậy vừa khiến video bị loãng, vừa tự đốt sạch chất liệu của chính mình.

Lúc lên khung nội dung (mình thường mất khoảng 15 phút trên một trang giấy trước khi viết lời thoại), mình luôn tách 1 ý tưởng gốc thành 5 góc cố định:
1. Vấn đề người xem đang vướng mỗi ngày.
2. Lỗi sai phổ biến khi họ tự xử lý.
3. Hướng dẫn từng bước để sửa đúng 1 điểm.
4. Một ví dụ hoặc case thực tế đã làm.
5. Quan điểm làm nghề đằng sau cách xử lý đó.

Chỉ cần đổi góc tiếp cận, một chủ đề cốt lõi sẽ nuôi được kênh suốt cả tuần mà không bị lặp lời. Mình để sẵn mẫu Worksheet 1-ra-5 này trong bộ Starter Kit ở phần giới thiệu, bạn nào đang lên lịch quay tuần mới có thể lấy về dùng ngay.
```

---

## VIDEO 38 — MÃ `C015`: TẠO SHOT LIST TRƯỚC KHI QUAY CÓ ÍCH GÌ?

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Ba, 29/12/2026
- **Pillar / Tuyến nội dung:** P1 (Marketing trong video) — `MKT04` (Tiền kỳ & Tổ chức sản xuất thực chiến)
- **Format:** BTS (Behind The Scenes — Hậu trường so sánh buổi quay thực tế)
- **Tệp người xem:** Creator (Người tự quay hoặc quay cùng nhân sự nhưng khi ngồi vào máy dựng luôn bị thiếu cảnh minh họa)
- **Mục tiêu Funnel:** Cân nhắc (Consideration → Nhận thấy giá trị của quy trình chuẩn)
- **Claim duy nhất:** Dành 5 phút lập bảng shot list 3 cột trước khi bấm máy giúp bạn không bao giờ rơi vào cảnh quay thừa 20 phút nói chuyện nhưng thiếu đúng 3 giây cận cảnh bằng chứng lúc ngồi dựng.
- **Bằng chứng cần chuẩn bị:** Folder chứa 40 file quay lỗi/thừa của buổi quay không có shot list vs Bảng Shot List 3 cột thật (`Câu thoại gốc` | `Góc máy cần quay` | `Bằng chứng trên hình`) đặt cạnh timeline Premiere khớp từng cảnh.
- **CTA & Offer:** Nhận Mẫu Shot List 3 cột trong **Starter Kit** ở bio.

### 2. Bảng kịch bản chi tiết (Thời lượng: ~40 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác màn hình (Visual & Timeline) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) & SFX/Nhịp |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | Split-screen: Bên trái là folder 38 file quay lộn xộn; bên phải là timeline Premiere bị trống một khoảng đen có dấu chấm hỏi đỏ ở tầng V2 (B-roll). | Quay hai tiếng nhưng lúc dựng vẫn **thiếu đúng cảnh cần** | Đã bao giờ bạn quay xong hai tiếng đồng hồ, nhưng lúc mở máy lên dựng lại thiếu đúng cảnh cận cảnh quan trọng nhất chưa? `[SFX: Tiếng báo lỗi nhẹ trên máy tính]` |
| `00:03 – 00:10` | **2. PROOF / TENSION** | Cảnh BTS Thành ngồi trước timeline toàn A-roll (cảnh ngồi nói từ đầu đến cuối), tua đi tua lại tìm cảnh sản phẩm/màn hình nhưng không có. | Không có shot list: **thừa cảnh ngồi nói**, thiếu bằng chứng | Khi bấm máy mà chỉ cầm mỗi kịch bản chữ, bạn sẽ có xu hướng đọc một mạch từ đầu tới cuối. Kết quả là thừa hàng chục file ngồi nói, nhưng không có lấy một cảnh chứng minh lời mình vừa nói. |
| `00:10 – 00:19` | **3. BODY (Cột 1 & 2)** | Cận cảnh tờ giấy kẹp trên clipboard hoặc màn hình iPad mở **Bảng Shot List 3 Cột** thật của Thành. Tay Thành chỉ vào Cột 1 và Cột 2. | Bảng shot list **ba cột trước khi bấm máy** | Trước mỗi buổi quay, mình luôn dành năm phút điền bảng shot list ba cột này. Cột một là ý chính của câu nói. Cột hai là góc máy: câu nào nhìn thẳng ống kính, câu nào phải chuyển sang quay cận tay thao tác. |
| `00:19 – 00:27` | **3. BODY (Cột 3 - Quyết định)** | Zoom vào Cột 3 trên bảng: *"Bằng chứng nhìn thấy được"*. Chuyển cảnh BTS Thành cầm điện thoại quay cận 3 giây màn hình kết quả và tick chữ `V` vào tờ giấy. | Cột 3 quan trọng nhất: **bằng chứng nhìn thấy được** | Nhưng cột ăn tiền nhất là cột thứ ba: bằng chứng trên màn hình. Hễ kịch bản có câu kết quả hoặc con số, cột ba bắt buộc phải ghi rõ cần quay cận vật phẩm hay chụp màn hình nào để đè lên. `[SFX: Tiếng bút tick giấy dứt khoát]` |
| `00:27 – 00:33` | **3. BODY (Kết quả)** | Screen Record timeline Premiere: Các file quay được đặt tên theo số thứ tự Shot List, thả vào timeline khớp khít tầng V1 (A-roll) và V2 (B-roll). | Quay đúng **mười lăm phút**, dựng khớp từng giây | Nhờ bảng này, một video bốn mươi giây mình chỉ cần quay đúng sáu cảnh trong mười lăm phút. Lúc đưa vào timeline là khớp ngay lập tức. `[Nghỉ 0.6s]` |
| `00:33 – 00:40` | **4. CLOSE & CTA** | A-roll Thành cầm bảng Shot List trên tay tại góc quay, ánh sáng gọn gàng. Hiện card hướng dẫn tải file ở bio. | Lấy **mẫu shot list 3 cột** trong Starter Kit ở bio | Đó là cách mình chuẩn bị tiền kỳ có chủ đích. Mình có để sẵn mẫu shot list ba cột này trong Starter Kit ở bio, bạn tải về in ra hoặc mở trên điện thoại lúc quay nhé. |

### 3. Checklist Shot List cần quay/chụp
- [ ] **Shot 1 (Screen Record):** Mở cửa sổ Explorer/Finder có 35–40 file `IMG_xxxx.MOV` chưa phân loại đặt cạnh timeline Premiere có khoảng trống B-roll.
- [ ] **Shot 2 (BTS A-roll):** Thành ngồi ở bàn dựng, tay chống cằm lướt qua dãy clip A-roll giống hệt nhau.
- [ ] **Shot 3 (Cận cảnh đạo cụ thật):** Quay cận bảng Shot List 3 cột thật (in giấy kẹp clipboard hoặc mở trên iPad), thấy rõ chữ viết tay/ghi chú ở 3 cột.
- [ ] **Shot 4 (BTS thao tác quay):** Cảnh góc rộng thấy Thành nhìn bảng Shot List, chỉnh lại chân máy quay cận bàn tay/màn hình trong 3 giây rồi gạch hoàn thành.
- [ ] **Shot 5 (A-roll kết):** Thành đứng cạnh chân máy đèn quay, cầm clipboard nói câu chốt và CTA.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok
```text
Cầm mỗi kịch bản chữ đi quay rất dễ rơi vào cảnh: quay thừa 20 phút ngồi nói nhưng lúc dựng lại thiếu đúng 3 giây cận cảnh bằng chứng.
Mình để sẵn Mẫu Shot List 3 cột trong bộ Starter Kit ở bio, bạn tải về điền 5 phút trước khi bấm máy là nhàn cả lúc quay lẫn lúc dựng.
#dungcochudich #shotlist #quay dựngvideo #contentcreator
```

#### B. Caption Facebook Reels
```text
Lý do nhiều bạn rất ngại dựng video sau khi quay xong không nằm ở phần mềm dựng, mà nằm ở lúc mở thẻ nhớ ra thấy 30-40 file giống hệt nhau không biết chọn file nào.
Từ ngày tập thói quen kẻ bảng Shot List 3 cột (Ý nói - Góc máy - Bằng chứng hiển thị) trước khi bật đèn, thời gian quay mỗi clip của mình giảm một nửa mà lúc dựng không bao giờ bị thiếu B-roll.
Bạn nào hay tự quay một mình có thể lấy mẫu bảng này trong Starter Kit ở trang cá nhân của mình về dùng thử ngay nhé.
#dungcochudich #videomarketing #videoediting #xaykenh
```

#### C. Bài đăng Facebook cá nhân (Viết riêng — 170 chữ)
```text
Hồi mới nhận dựng video cho các bạn tự quay tại nhà, cảnh mình sợ nhất là mở Google Drive khách gửi ra thấy 45 file video, mỗi file dài hơn 1 phút và tất cả đều là đúng 1 góc ngồi nói thẳng vào camera.

Khi ghép lên timeline, cứ đến đoạn người nói nhắc tới "kết quả thực tế", "chất liệu sản phẩm" hay "sự khác biệt trước và sau" là mình không tìm đâu ra hình ảnh để đè lên. Cuối cùng lại phải nhắn khách bày đồ ra quay bù, rất mất nhịp.

Thực ra để giải quyết chuyện này chỉ mất đúng 5 phút trước khi bấm máy bằng một bảng Shot List 3 cột:
1. Câu thoại / Ý chính ở đoạn đó là gì.
2. Góc máy nào phục vụ ý đó (toàn, trung hay cận).
3. Bằng chứng nào bắt buộc phải hiện lên mắt người xem (hình chụp màn hình, cận cảnh bề mặt, hay thao tác tay).

Điền xong bảng này (thường một clip 40 giây chỉ cần 5–7 dòng), bạn quay tới đâu gạch tới đó, vào máy dựng là lắp khớp như xếp hình. Mình có để sẵn file mẫu Shot List 3 cột này trong Starter Kit ở phần giới thiệu cho bạn nào cần.
```

---

## VIDEO 39 — MÃ `C031`: KHOẢNG DỪNG ĐÔI KHI MẠNH HƠN MỘT TRANSITION

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Năm, 31/12/2026
- **Pillar / Tuyến nội dung:** P2 (Edit & Storytelling) — `EDIT04` (Nhịp dựng, Pacing & Kiểm soát sự chú ý)
- **Format:** Breakdown (Phân tích trực tiếp trên sóng âm & hình ảnh timeline)
- **Tệp người xem:** Editor (Video editor trẻ, hoặc người tự dựng hay có thói quen cắt khít mọi hơi thở và nhồi hiệu ứng chuyển cảnh)
- **Mục tiêu Funnel:** Nhận biết (Awareness → Khẳng định tư duy dựng có chủ đích)
- **Claim duy nhất:** Đặt một khoảng lặng 0.6 giây trước câu kết luận quan trọng giúp kéo lại sự tập trung của người xem mạnh hơn bất kỳ hiệu ứng zoom hay tiếng whoosh nào.
- **Bằng chứng cần chuẩn bị:** Sóng âm (Audio Waveform) rõ ràng trên Premiere Pro với 2 phiên bản A/B của cùng một đoạn kết: Bản A cắt sát rạt kèm whoosh/zoom; Bản B ngắt nhạc và để khoảng trống `0.6s` (15 frames ở 25fps / 18 frames ở 30fps) trước câu chốt.
- **CTA & Offer:** Lưu bài học (**Không bán**).

### 2. Bảng kịch bản chi tiết (Thời lượng: ~37 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác màn hình (Visual & Timeline) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) & SFX/Nhịp |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | Zoom thẳng vào timeline Premiere Pro: con trỏ chuột xóa hiệu ứng Transition + SFX Whoosh, kéo giãn một khoảng trống đúng `00:00:18` (0.6 giây) trên cả track thoại và nhạc. | Đôi khi **0.6 giây im lặng** mạnh hơn một transition | Có những lúc thứ giữ người xem ở lại không phải là một cú chuyển cảnh mượt, mà là không có âm thanh nào cả. `[Nghỉ 0.5s hoàn toàn không nhạc]` |
| `00:03 – 00:11` | **2. PROOF (Bản A - Lỗi)** | Phát 4 giây **Bản A**: các câu thoại cắt dính sát vào nhau, chèn zoom liên tục và tiếng *Whoosh* to. Sóng âm dày đặc không có khe hở. | Cắt sát + chèn whoosh liên tục làm **trôi mất câu chốt** | Bạn nghe thử đoạn này nhé. *(Phát Bản A 3s)*. Khi mọi câu đều nối đuôi nhau với cùng một tốc độ và tiếng whoosh dồn dập, tai người xem sẽ bị trơ. Câu quan trọng nhất bị trôi tuột đi. |
| `00:11 – 00:20` | **3. BODY (Thao tác sửa)** | Screen Record cận cảnh: Thành dùng Razor Tool (`C`) cắt ngắt track nhạc nền ngay trước câu kết luận, kéo lùi câu thoại lại đúng `0.6s`, bỏ hiệu ứng zoom giật, thay bằng cắt thẳng sang góc cận (Punch-in nhẹ 108%). | Ngắt nhạc và để trống **0.6 giây trước câu kết** | Thay vì nhồi thêm hiệu ứng, mình làm ngược lại. Ngay trước câu kết luận đắt nhất của video, mình cắt đứt nhạc nền và mở một khoảng nghỉ đúng không phẩy sáu giây. |
| `00:20 – 00:28` | **3. BODY (Bản B - Bằng chứng)** | Phát **Bản B** kèm thanh Playhead chạy qua khoảng trống `0.6s` trên màn hình để người xem vừa nghe vừa thấy trực quan độ nảy của câu chốt sau khoảng lặng. | Khoảng trống âm thanh tạo **tương phản sự chú ý** | Nghe lại bản đã sửa này: *"Đó không phải là lỗi thiết bị..."* `[Im lặng hoàn toàn 0.6s — Playhead đi qua vùng trống]` *"...mà là lỗi thông điệp."* |
| `00:28 – 00:33` | **3. BODY (Đúc kết)** | A-roll Thành ngồi trước màn hình dựng, giải thích ngắn gọn bằng biểu cảm điềm tĩnh. | Tai người xem nhạy với **sự thay đổi đột ngột** | Khi âm thanh đang chạy đều mà dừng lại nửa giây, não người xem sẽ tự động ngước lên kiểm tra xem chuyện gì sắp xảy ra. `[Nghỉ 0.5s]` |
| `00:33 – 00:37` | **4. CLOSE & CTA** | Hiện khung tổng kết quy tắc `0.6s Pause` trên timeline. | **Lưu lại mẹo nhịp nghỉ** cho lần dựng tiếp theo | Đó là cách mình dựng có chủ đích. Bạn lưu lại mẹo không phẩy sáu giây này để thử ngay ở câu chốt của video tiếp theo nhé. |

### 3. Checklist Shot List cần quay/chụp
- [ ] **Shot 1 (Screen Record độ phân giải cao):** Quay màn hình timeline Premiere phóng to track Audio A1 (Voice) và A2 (Music), thấy rõ sóng âm dày đặc của Bản A và khoảng trống `0.6s` được đánh dấu Marker màu xanh của Bản B.
- [ ] **Shot 2 (A-roll):** Thành ngồi góc nghiêng 30 độ cạnh màn hình, đeo tai nghe kiểm âm (hoặc để tai nghe trên bàn), nói trực diện vào camera.
- [ ] **Shot 3 (Close-up tay):** Cận cảnh ngón tay bấm phím `C` (Razor) và kéo lùi clip trên bàn phím/chuột.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok
```text
Nhiều bạn dựng video sợ khoảng lặng nên cắt khít mọi hơi thở rồi chèn whoosh liên tục, làm câu quan trọng nhất bị trôi tuột đi.
Thử ngắt nhạc và để trống đúng 0.6 giây trước câu kết luận, bạn sẽ thấy sức nặng của câu nói khác hẳn. Lưu lại để thử ở project tiếp theo nhé.
#dungcochudich #videoediting #premierepro #pacing
```

#### B. Caption Facebook Reels
```text
Một thói quen rất phổ biến khi mới dựng video ngắn là sợ người xem chán nên cắt bỏ toàn bộ hơi thở, câu sau đè lên câu trước và nhồi thêm hiệu ứng chuyển cảnh.
Nhưng nếu từ giây đầu đến giây cuối đều nhanh như nhau, người xem sẽ không biết đâu là câu họ cần nhớ. Đôi khi chỉ cần nhường lại 0.6 giây im lặng trước câu chốt, câu nói đó tự khắc có trọng lượng hơn mọi hiệu ứng.
#dungcochudich #editor #storytelling #videomarketing
```

#### C. Bài đăng Facebook cá nhân (Viết riêng — 155 chữ)
```text
Hồi mới tập dựng video ngắn, mình từng nghĩ nhịp dựng nhanh đồng nghĩa với việc phải cắt sạch mọi khoảng thở trên timeline. Chỗ nào hai câu cách nhau nửa giây là mình kéo sát lại ngay hoặc đè một tiếng whoosh vào cho đỡ trống.

Nhưng khi xuất file ra xem lại bằng tâm thế của người lướt điện thoại, mình nhận ra một vấn đề: video nghe rất gấp, nhưng xem xong không đọng lại được câu nào. Vì câu phụ và câu chính đều được phát ra với cùng một tốc độ.

Sau này mình học được cách dùng khoảng lặng như một dấu hai chấm bằng âm thanh:
1. Giữ nhịp gọn ở phần dẫn dắt để không làm mất thời gian của người xem.
2. Ngay trước câu kết luận quan trọng nhất, cắt ngắt nhạc nền.
3. Mở một khoảng nghỉ từ 0.5 đến 0.6 giây (khoảng 15–18 frames) rồi mới thả câu chốt.

Sự im lặng đột ngột trong nửa giây luôn kéo mắt người xem quay lại màn hình nhanh hơn bất kỳ hiệu ứng zoom giật nào. Bạn nào đang dựng clip nói chuyện thử áp dụng ở câu chốt tiếp theo xem sao nhé.
```

---

## VIDEO 40 — MÃ `C049`: AI LÀM THÔ, EDITOR LÀM TINH: TẬP 1

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Bảy, 02/01/2027 *(Lịch linh hoạt)*
- **Pillar / Tuyến nội dung:** P3 (AI trong workflow editor) — `AI04` (So sánh thực chứng AI vs Editor)
- **Format:** Before/after (Đặt bản xuất tự động từ AI cạnh bản Editor tinh chỉnh lại)
- **Tệp người xem:** Khách hàng (Chủ doanh nghiệp, thương hiệu cá nhân đang phân vân giữa việc dùng app cắt tự động bằng AI với việc thuê Editor có tư duy marketing)
- **Mục tiêu Funnel:** Cân nhắc (Consideration → Thấy rõ giá trị phần "làm tinh" của Thành)
- **Claim duy nhất:** Công cụ AI có thể giúp cắt bỏ khoảng thừa và lên phụ đề thô trong 3 phút, nhưng chính việc chỉnh lại nhịp nhấn câu bán hàng, vị trí chữ và độ cân bằng âm thanh trong Premiere mới quyết định video có giữ được sự chuyên nghiệp của thương hiệu hay không.
- **Bằng chứng cần chuẩn bị:** File video xuất thẳng từ công cụ AI auto-edit (OpusClip / CapCut AutoCut) vs File xuất từ Premiere Pro của Thành trên cùng một source footage 30 giây của khách hàng.
- **CTA & Offer:** Theo dõi series *"AI làm thô, editor làm tinh"* (Định hướng nhận diện **Dịch vụ Edit/Media**).

### 2. Bảng kịch bản chi tiết (Thời lượng: ~40 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác màn hình (Visual & Timeline) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) & SFX/Nhịp |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:04` | **1. HOOK** | Split-screen dọc: Trái là **Bản AI tự dựng (3 phút)**; Phải là **Bản mình sửa lại (15 phút)**. Phát 2 giây đầu của cả hai để thấy sự khác biệt ngay lập tức. | AI dựng trong ba phút khác gì **editor làm tinh**? | Đây là video do AI tự cắt trong ba phút, còn đây là bản mình chỉnh lại thêm mười lăm phút trên Premiere. `[SFX: Click chuyển tab sang bản so sánh]` |
| `00:04 – 00:11` | **2. PROOF (Điểm mạnh & Giới hạn của AI)** | Quay màn hình giao diện AI đã tự cắt khoảng trống và tạo phụ đề, sau đó khoanh đỏ vào 3 điểm lỗi trên bản xuất của AI. | AI làm thô rất nhanh nhưng **mắc ba lỗi cảm xúc** | Phải công nhận AI làm phần thô rất tốt: nó lọc khoảng nghỉ và tạo phụ đề chỉ mất vài phút. Nhưng nếu đăng ngay bản này lên kênh bán hàng, bạn sẽ lộ ngay ba điểm yếu. |
| `00:11 – 00:19` | **3. BODY (Sửa điểm 1: Timing)** | Zoom vào timeline Premiere: Bản AI cắt đều tăm tắp từng câu; Thành kéo lại điểm cắt ở chữ cuối câu để không bị cụt âm và giữ lại cái gật đầu xác nhận của người nói. | 1. Giữ lại **biểu cảm xác nhận** cuối câu nói | Thứ nhất là nhịp cắt. AI cứ hết chữ là cắt phăng đi, làm mất luôn cái gật đầu tạo niềm tin của người nói. Mình phải nới lại tám frame cuối câu để giữ trọn biểu cảm đó. |
| `00:19 – 00:26` | **3. BODY (Sửa điểm 2: Trọng tâm chữ)** | So sánh khung hình: Bản AI tô màu vàng ngẫu nhiên vào từ nối (*"nhưng mà"*, *"thì là"*); Bản của Thành chỉ highlight đúng cụm từ lợi ích cốt lõi (*"Giảm 40% chi phí"*). | 2. Đặt màu nhấn vào đúng **từ khóa chuyển đổi** | Thứ hai là trọng tâm chữ. AI tô màu tự động vào cả những từ nối vô nghĩa. Mình tắt hiệu ứng nhảy chữ rối mắt và chỉ tô sáng đúng con số lợi ích mà khách hàng cần đọc. |
| `00:26 – 00:33` | **3. BODY (Sửa điểm 3: Âm thanh)** | Mở Audio Track Mixer / Keyframe âm lượng: Bản AI để nhạc nền ngang hàng suốt clip; Bản của Thành hạ nhạc `-22dB` khi vào câu báo giá/cam kết. | 3. Hạ nhạc nền khi vào **câu cam kết quan trọng** | Thứ ba là âm thanh. Khi người nói bước vào câu cam kết quan trọng nhất, AI vẫn để nhạc nền đánh đều đều, còn mình kéo nhạc xuống để giọng nói hoàn toàn làm chủ. `[Nghỉ 0.5s]` |
| `00:33 – 00:40` | **4. CLOSE & CTA** | Chạy 3 giây mượt mà của bản Final Cut. A-roll Thành xuất hiện ở khung nhỏ góc dưới hoặc toàn màn hình chốt câu khóa. | **Theo dõi series** AI làm thô, editor làm tinh | AI giúp mình tiết kiệm thời gian dọn nháp, nhưng phần tinh chỉnh để ra chất thương hiệu vẫn là việc của người dựng. Bạn theo dõi kênh để xem tiếp tập hai của series này nhé. |

### 3. Checklist Shot List cần quay/chụp
- [ ] **Shot 1 (Screen Record AI Tool):** Quay màn hình kết quả xuất ra từ tool auto-cut AI (thấy rõ chữ tô màu ngẫu nhiên vào từ phụ và vết cắt cụt cuối câu).
- [ ] **Shot 2 (Screen Record Premiere Pro):** Quay thao tác kéo giãn tail của clip thêm 8 frames, chỉnh lại Essential Graphics (chỉ tô màu 1 cụm từ khóa) và vẽ keyframe hạ âm lượng nhạc nền.
- [ ] **Shot 3 (Export A/B):** Xuất 2 đoạn video 5 giây (Bản AI thô vs Bản Thành làm tinh) đặt cạnh nhau.
- [ ] **Shot 4 (A-roll):** Thành ngồi tại bàn làm việc có 2 màn hình (hoặc laptop + màn hình rời), nói trực diện điềm đạm.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok
```text
AI giúp cắt bỏ khoảng thừa và lên phụ đề nháp trong 3 phút, nhưng nếu đăng thẳng bản đó lên kênh thương hiệu thì rất dễ mất điểm ở nhịp cắt, từ khóa nhấn và âm thanh.
Theo dõi kênh của mình để xem tiếp series "AI làm thô, editor làm tinh" qua các project thực tế nhé.
#dungcochudich #aiworkflow #videoediting #marketingvideo
```

#### B. Caption Facebook Reels
```text
Nhiều khách hàng hỏi mình: "Giờ có app AI tự cắt video rồi thì editor còn làm gì ở giữa?"
Câu trả lời nằm ở 15 phút sau khi AI chạy xong. AI giúp mình dọn phần thô rất nhanh, nhưng việc giữ lại nửa giây biểu cảm đáng tin cậy của người nói, chọn đúng từ khóa bán hàng để tô sáng và kiểm soát nhạc nền không lấn át câu chốt lại là thứ máy chưa tự quyết định thay được.
Mình mở đầu series "AI làm thô, editor làm tinh" bằng ca thực tế này, mời bạn cùng xem sự khác biệt nhé.
#dungcochudich #videomarketing #aivideo #branding
```

#### C. Bài đăng Facebook cá nhân (Viết riêng — 175 chữ)
```text
Tuần rồi có một anh khách gửi cho mình xem thử đoạn video anh tự chạy qua app AI cắt tự động. Anh bảo: "Anh thấy nó cắt khoảng nghỉ với chạy chữ nhanh lắm, chỉ mất có 3 phút, nhưng sao nhìn tổng thể vẫn chưa đủ tự tin để chạy quảng cáo hay đăng lên kênh chính?"

Mình tải file gốc của anh về, vẫn cho AI xử lý bước nháp đầu tiên để tiết kiệm thời gian lọc thoại, rồi đưa vào Premiere chỉnh lại trong 15 phút ở 3 điểm:
1. Nhịp cắt cuối câu (bản AI cắt phăng ngay khi vừa dứt tiếng khiến mặt người nói bị giật; mình nới thêm 8 frames để giữ lại cái gật đầu chắc chắn ở cuối câu).
2. Trọng tâm phụ đề (bản AI tự động tô màu vàng vào cả chữ "nhưng mà", "hiện tại"; mình đổi lại chỉ nhấn đúng cụm số liệu khách cần nhớ).
3. Độ ưu tiên âm thanh (hạ nhạc nền xuống sâu hơn ở đúng 8 giây cuối khi anh nói về cam kết dịch vụ).

AI làm phần thô cực kỳ giỏi, nhưng phần "làm tinh" để giữ uy tín cho người xuất hiện trên hình vẫn cần bàn tay kiểm soát có chủ đích. Mình sẽ chia sẻ tiếp các ca thực tế trong series này trên trang cá nhân nhé.
```

---

# TUẦN 11: MỔ XẺ VIDEO GIỮ MẮT, KỸ THUẬT CẮT THEO Ý & KIỂM SOÁT LỖI AI
*(04/01/2027 – 09/01/2027)*

---

## VIDEO 41 — MÃ `C016`: MỔ VIDEO 30 GIÂY: VÌ SAO ĐOẠN NÀY GIỮ MẮT?

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Hai, 04/01/2027
- **Pillar / Tuyến nội dung:** P1 (Marketing trong video) — `MKT05` (Phân tích & Mổ xẻ video thực chiến)
- **Format:** Breakdown (Pause tại 4 mốc thời gian trên thanh tiến trình 30 giây)
- **Tệp người xem:** Marketer (Người làm nội dung quảng cáo, performance marketing, hoặc biên tập kịch bản cần hiểu cấu trúc giữ chân người xem bằng hình ảnh)
- **Mục tiêu Funnel:** Nhận biết (Awareness → Xây dựng uy tín phân tích Marketing x Edit)
- **Claim duy nhất:** Một video 30 giây giữ được mắt người xem đến cuối không nhờ hiệu ứng phức tạp, mà nhờ 4 quyết định hình ảnh đặt đúng vào giây thứ 0, giây thứ 7, giây thứ 15 và giây thứ 25.
- **Bằng chứng cần chuẩn bị:** 1 video sản phẩm/dịch vụ dài 30 giây có nguồn rõ ràng (project của Thành hoặc mẫu quảng cáo được phép phân tích), gắn thanh Timebar 30 giây trên màn hình với 4 điểm mốc đánh dấu sáng.
- **CTA & Offer:** Theo dõi series mổ xẻ video (**Không bán**).

### 2. Bảng kịch bản chi tiết (Thời lượng: ~39 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác màn hình (Visual & Timeline) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) & SFX/Nhịp |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | Trên màn hình hiện thanh tiến trình `00:00 ──●────●────●────●── 00:30` với 4 mốc phát sáng tại `0s`, `7s`, `15s`, `25s`. Thành chỉ tay thẳng vào 4 điểm đó. | Bốn mốc giữ mắt trong **một video ba mươi giây** | Một video ba mươi giây giữ được người xem đến cuối không phải nhờ may mắn, mà nhờ bốn chốt chặn hình ảnh đặt đúng giây. `[SFX: Bốn tiếng टिक-tắc nhanh khớp 4 chấm sáng]` |
| `00:03 – 00:11` | **2. BODY (Mốc 1: 0–3s)** | Phóng to mốc `00:00 – 00:03` của video mẫu: cảnh mở đầu không có logo hay lời chào, mà là cận cảnh sản phẩm đang giải quyết trực tiếp vết bẩn/lỗi. | Giây 0 đến 3: **Cho thấy kết quả trước**, giải thích sau | Chốt chặn đầu tiên là từ giây không đến giây thứ ba. Video này không hề giới thiệu tên sản phẩm trước, mà cho xem ngay hành động xử lý vấn đề để khóa mắt người lướt. |
| `00:11 – 00:18` | **3. BODY (Mốc 2: Giây thứ 7)** | Thanh tiến trình chạy đến `00:07` và Pause lại: từ góc trung người nói chuyển sang góc nghiêng kết hợp đồ họa so sánh 2 bên trên màn hình. | Giây thứ 7: **Đổi bố cục khung hình** khi hết câu mở đầu | Chốt chặn thứ hai nằm ở giây thứ bảy. Đây là lúc hiệu ứng tò mò ban đầu vừa giảm xuống. Người dựng lập tức đổi từ cảnh một người nói sang khung hình chia đôi để tạo kích thích thị giác mới. |
| `00:18 – 00:26` | **3. BODY (Mốc 3: Giây thứ 15)** | Thanh tiến trình chạy đến `00:15` và Pause: khung hình zoom cận 100% vào bề mặt chất liệu / con số đo đạc thật, không dùng ảnh stock. | Giây thứ 15: **Đưa bằng chứng cận cảnh** vào giữa video | Chốt chặn thứ ba ở đúng giây mười lăm. Khi người xem bắt đầu tự hỏi lời quảng cáo có thật không, một cú quay cận cảnh không cắt ghép xuất hiện để trả lời ngay lập tức. |
| `00:26 – 00:33` | **3. BODY (Mốc 4: Giây thứ 25)** | Thanh tiến trình chạy đến `00:25`: toàn bộ B-roll phụ biến mất, chỉ còn gương mặt người nói + 1 dòng chữ tóm tắt lợi ích duy nhất trước khi sang CTA. | Giây thứ 25: **Thu gọn khung hình** để khóa một thông điệp | Và chốt chặn thứ tư ở giây hai mươi lăm: dọn sạch mọi chi tiết phụ trên màn hình, chỉ giữ lại đúng một dòng thông điệp cốt lõi để dẫn vào lời kêu gọi hành động. `[Nghỉ 0.6s]` |
| `00:33 – 00:39` | **4. CLOSE & CTA** | Hiện lại sơ đồ 4 mốc `0s - 7s - 15s - 25s` gọn gàng trên màn hình. Thành gật đầu nhẹ. | **Theo dõi kênh** để xem tiếp series mổ video thực chiến | Đó là cách mình đọc cấu trúc giữ mắt có chủ đích. Bạn theo dõi kênh để xem tiếp các bài mổ xẻ video thực chiến trong series này nhé. |

### 3. Checklist Shot List cần quay/chụp
- [ ] **Shot 1 (Graphic Overlay):** Thiết kế thanh tiến trình 30 giây có 4 điểm mốc (`0s - 7s - 15s - 25s`) trên Premiere/After Effects.
- [ ] **Shot 2 (Screen Record Video mẫu):** Chuẩn bị video mẫu 30 giây đã được đánh dấu 4 freeze-frame tại đúng 4 mốc thời gian trên.
- [ ] **Shot 3 (A-roll):** Thành đứng hoặc ngồi cạnh màn hình lớn (hoặc ghép Green Screen/PiP gọn ở góc dưới bên trái), tay chỉ đúng hướng thanh tiến trình.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok
```text
Mổ xẻ một video 30 giây giữ chân người xem tốt: không nằm ở hiệu ứng màu mè, mà nằm ở 4 quyết định hình ảnh đặt đúng vào giây thứ 0, giây 7, giây 15 và giây 25.
Theo dõi kênh của mình để xem tiếp series bóc tách cấu trúc video marketing thực chiến nhé.
#dungcochudich #marketingvideo #videoediting #contentstrategy
```

#### B. Caption Facebook Reels
```text
Khi xem một video quảng cáo 30 giây có tỷ lệ xem hết cao, nếu tắt tiếng đi và chỉ nhìn vào sự thay đổi trên khung hình, bạn sẽ thấy một nhịp điệu rất có tính toán.
Cứ mỗi 7 đến 8 giây — đúng vào lúc mắt người xem chuẩn bị lướt đi — khung hình lại thực hiện một nhiệm vụ mới: mở bằng hành động (0s), đổi bố cục (7s), đưa bằng chứng cận cảnh (15s) và thu gọn thông điệp (25s).
Bạn lưu lại 4 mốc này để đối chiếu ngay với kịch bản 30 giây tiếp theo của team nhé.
#dungcochudich #videomarketing #marketer #performancevideo
```

#### C. Bài đăng Facebook cá nhân (Viết riêng — 165 chữ)
```text
Khi ngồi xem lại những video 30 giây có tỷ lệ giữ chân người xem ổn định nhất mà mình từng tham gia dựng, mình nhận ra chúng đều tuân theo một "nhịp đập hình ảnh" rất rõ ràng chứ không cắt cảnh ngẫu hứng.

Nếu chia 30 giây đó thành một trục thời gian, luôn có 4 mốc quyết định mà cả người viết kịch bản lẫn editor phải phối hợp chặt với nhau:
1. Giây 0 – 3 (Hook thị giác): Đưa ngay hành động hoặc kết quả lên hình, tuyệt đối không mở đầu bằng logo tĩnh hay câu chào xã giao.
2. Giây thứ 7 (Điểm đổi bố cục): Khi câu mở đầu vừa dứt, đổi từ khung hình đơn sang split-screen hoặc góc máy thứ hai để giữ nhịp chú ý.
3. Giây thứ 15 (Điểm bằng chứng): Đúng giữa video, khi người xem cần lý do để tin, phải có cảnh cận thật (sản phẩm, số liệu, thao tác trực tiếp).
4. Giây thứ 25 (Điểm khóa thông điệp): Bỏ hết hiệu ứng phụ, làm sạch khung hình để người xem chỉ tập trung vào đúng 1 hành động cuối.

Mình sẽ tiếp tục mổ xẻ các case ngắn như thế này trong chuỗi bài tuần tới, bạn nào làm marketing hoặc sản xuất nội dung cùng theo dõi nhé.
```

---

## VIDEO 42 — MÃ `C032`: CÁCH CẮT THEO Ý, KHÔNG CHỈ CẮT THEO NHẠC

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Ba, 05/01/2027
- **Pillar / Tuyến nội dung:** P2 (Edit & Storytelling) — `EDIT04` (Kỹ thuật cắt dựng theo tư duy nội dung)
- **Format:** Tutorial (Hướng dẫn thao tác từng bước trên Transcript & Timeline Premiere)
- **Tệp người xem:** Editor (Editor mới vào nghề hoặc người tự dựng hay rải marker theo nhịp trống của nhạc rồi cắt hình theo nhạc cho cả video nói chuyện)
- **Mục tiêu Funnel:** Nhận biết (Awareness → Thu hút tải tài liệu quy trình dựng)
- **Claim duy nhất:** Với video chia sẻ kiến thức hoặc bán hàng, bạn phải đánh dấu các từ khóa chuyển ý trên transcript trước rồi mới đặt điểm cắt hình và nhạc đi theo lời nói, thay vì bắt câu nói phải cắt vụn theo nhịp trống của nhạc.
- **Bằng chứng cần chuẩn bị:** Cửa sổ Text/Transcript trong Premiere Pro có tô sáng 3 từ khóa chuyển ý (`"Nhưng vấn đề là..."`, `"Cách sửa rất đơn giản..."`, `"Kết quả sau 3 ngày..."`) nối thẳng xuống các điểm cắt trên timeline.
- **CTA & Offer:** Nhận Checklist cắt dựng theo ý trong **Starter Kit** ở bio.

### 2. Bảng kịch bản chi tiết (Thời lượng: ~39 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác màn hình (Visual & Timeline) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) & SFX/Nhịp |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | Screen Record: Một timeline rải đầy Marker theo nhịp trống nhạc (Beat Edit), làm câu nói của nhân vật bị cắt giật cục ngay giữa chữ. Thành nhấn `Ctrl + A` xóa sạch hàng Marker nhạc đó. | Video nói chuyện: hãy **cắt theo ý**, đừng cắt theo nhạc | Cắt theo nhịp nhạc rất hợp với video du lịch hay thời trang, nhưng nếu áp vào video nói chuyện bán hàng thì người xem sẽ cực kỳ mệt. `[SFX: Tiếng xóa sạch marker gọn gàng]` |
| `00:03 – 00:10` | **2. PROOF / TENSION** | Phát 3 giây bản cắt theo beat nhạc: cứ mỗi nhịp trống lại đổi góc máy hoặc nhảy B-roll dù người nói mới nói được nửa câu, làm câu chữ bị đứt mạch. | Đổi cảnh theo nhịp trống làm **đứt mạch hiểu của người xem** | Khi bạn đặt nhạc vào trước rồi cứ đúng nhịp trống là cắt cảnh, hình ảnh sẽ nhảy ngay lúc người nói chưa diễn đạt xong ý. Người xem nhìn thì vui mắt nhưng không hiểu bạn đang nói gì. |
| `00:10 – 00:18` | **3. BODY (Bước 1: Đánh dấu Transcript)** | Mở bảng **Text (Transcript)** trong Premiere Pro. Con trỏ chuột bôi vàng 3 cụm từ chuyển ý: *"Nhưng thực tế là"*, *"Bước đầu tiên"*, *"Kết quả là"*. | Bước 1: Đánh dấu **từ khóa chuyển ý** trên bảng thoại | Khi dựng video có lời thoại, mình luôn đi theo ba bước ngược lại. Bước một: mở bảng transcript, tìm và đánh dấu những cụm từ báo hiệu chuyển ý như *"nhưng thực tế là"*, *"bước đầu tiên"*, hoặc *"kết quả là"*. |
| `00:18 – 00:26` | **3. BODY (Bước 2: Đặt điểm cắt hình)** | Từ 3 cụm từ trên bảng Transcript, Thành đặt điểm cắt đổi góc máy (zoom-in) hoặc thả B-roll vào khớp chính xác chữ đầu tiên của cụm chuyển ý đó. | Bước 2: Đổi góc máy hoặc thả B-roll **đúng chữ chuyển ý** | Bước hai: mình chỉ đổi góc máy hoặc đưa B-roll minh họa vào đúng khoảnh khắc người nói vừa phát âm cụm từ chuyển ý đó. Hình ảnh lúc này đóng vai trò gạch đầu dòng cho tai người nghe. |
| `00:26 – 00:33` | **3. BODY (Bước 3: Nhạc đi theo lời)** | Track nhạc nền bên dưới được cắt và dịch chuyển để nhịp vào nhạc (Drop nhẹ) rơi đúng vào chữ *"Kết quả là"* của người nói. | Bước 3: Kéo điểm nhấn của nhạc **khớp vào lời nói** | Bước ba mới đến phần nhạc: mình dịch chuyển track nhạc nền để nhịp nhấn của bài nhạc rơi đúng vào chữ quan trọng nhất của câu thoại. `[Nghỉ 0.5s]` Nhạc phải phục vụ lời nói, không phải ngược lại. |
| `00:33 – 00:39` | **4. CLOSE & CTA** | A-roll Thành nhìn thẳng camera, bên cạnh hiện ảnh thu nhỏ tờ Checklist kiểm tra nhịp cắt trong Starter Kit. | Lấy **checklist dựng theo ý** trong Starter Kit ở bio | Đó là cách mình dựng có chủ đích. Mình để sẵn bản checklist kiểm tra điểm cắt theo ý này trong Starter Kit ở bio, bạn vào lấy về áp dụng ngay nhé. |

### 3. Checklist Shot List cần quay/chụp
- [ ] **Shot 1 (Screen Record lỗi):** Timeline có hàng chục Marker trên track nhạc và vết cắt hình cắt ngang câu nói.
- [ ] **Shot 2 (Screen Record cửa sổ Text/Transcript Premiere):** Quay rõ thao tác highlight 3 cụm từ chuyển ý tiếng Việt trong bảng Transcript của Premiere.
- [ ] **Shot 3 (Screen Record Timeline sửa):** Đặt B-roll và căn lại điểm vào của track nhạc khớp với Marker của câu thoại.
- [ ] **Shot 4 (A-roll):** Thành ngồi trước bàn dựng giải thích bước 1–2–3 rõ ràng, tốc độ vừa phải.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok
```text
Với video chia sẻ kiến thức hoặc bán hàng, nếu bạn rải marker theo nhịp trống rồi cắt hình theo nhạc thì câu nói sẽ bị vụn và rất khó theo dõi.
Hãy đánh dấu từ khóa chuyển ý trên transcript trước rồi mới cho hình và nhạc đi theo lời nói. Checklist quy trình này mình để sẵn trong Starter Kit ở bio nhé.
#dungcochudich #videoediting #premierepro #editortips
```

#### B. Caption Facebook Reels
```text
Nhiều bạn mới học dựng hay có thói quen: bỏ bài nhạc vào timeline trước, nghe tiếng trống đập ở đâu là bấm phím M đánh dấu ở đó, rồi cắt hình nhảy theo nhạc.
Cách đó rất đẹp khi dựng clip tổng hợp sự kiện hoặc thời trang. Nhưng với video có người nói chuyện giải thích vấn đề, điểm cắt hình phải nằm ở chỗ "chuyển ý" chứ không phải chỗ "chuyển nhịp trống".
Mình chia sẻ lại 3 bước cắt theo transcript trong video này, kèm bản Checklist mình để sẵn ở phần giới thiệu trang cá nhân cho bạn nào cần đối chiếu lúc dựng.
#dungcochudich #editor #storytelling #videomarketing
```

#### C. Bài đăng Facebook cá nhân (Viết riêng — 165 chữ)
```text
Một lỗi mình gặp rất nhiều khi xem bài test của các bạn editor mới là: thói quen "bắt lời nói phải chạy theo nhịp nhạc".

Tức là ngay khi tạo sequence mới, việc đầu tiên bạn làm là thả bài nhạc nền xuống, bấm phím M rải một hàng marker theo nhịp trống, rồi cứ đến marker là đổi cảnh hoặc chèn B-roll — bất chấp lúc đó người trong video mới nói được nửa câu. Kết quả là hình ảnh nhảy liên tục nhưng người xem lại không nắm được ý chính.

Với video thiên về nội dung và chuyển đổi, thứ tự ưu tiên trên timeline của mình luôn là:
1. Đọc bảng Transcript trước, đánh dấu các từ khóa chuyển trạng thái (ví dụ: từ nêu vấn đề sang giải pháp, từ lý thuyết sang ví dụ).
2. Đặt vết cắt đổi góc máy hoặc thả B-roll vào đúng chữ đầu tiên của ý mới để mắt và tai người xem nhận tín hiệu cùng lúc.
3. Cuối cùng mới cắt và dịch chuyển track nhạc nền sao cho điểm nhấn của nhạc nâng đỡ câu chốt.

Mình có đúc kết quy trình này thành một Checklist nhỏ trong bộ Starter Kit ở phần giới thiệu, bạn nào đang luyện dựng video talking-head có thể lấy về tham khảo nhé.
```

---

## VIDEO 43 — MÃ `C033`: TẠO REVEAL ĐỂ GIỮ SỰ TÒ MÒ

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Năm, 07/01/2027
- **Pillar / Tuyến nội dung:** P2 (Edit & Storytelling) — `EDIT04` (Kể chuyện bằng cấu trúc mở nút)
- **Format:** Remake (Dựng lại cùng 1 source nguyên liệu theo cấu trúc giữ nhịp mở kết quả)
- **Tệp người xem:** Creator (Người làm nội dung chia sẻ mẹo, hậu trường, case study hoặc biến hình sản phẩm nhưng người xem hay thoát ra từ giây thứ 6)
- **Mục tiêu Funnel:** Nhận biết (Awareness → Tăng tỷ lệ xem hết và lượt theo dõi series)
- **Claim duy nhất:** Thay vì nói toạc toàn bộ quy trình và kết quả ngay từ giây thứ 5, việc chỉ cho xem vấn đề kèm một mảnh manh mối nhỏ rồi mở kết quả ở cuối giúp giữ sự tò mò của người xem đi hết video.
- **Bằng chứng cần chuẩn bị:** Cùng 1 bộ source video (ví dụ: sửa một góc quay bị ngược sáng tại văn phòng) được dựng thành 2 timeline: **Bản Cũ** (tiết lộ hết cách làm từ giây thứ 5) và **Bản Remake** (Cấu trúc: Vấn đề → 1 Manh mối gây tò mò → Quá trình ngắn → Reveal kết quả A/B ở giây 25).
- **CTA & Offer:** Theo dõi series Remake (**Không bán**).

### 2. Bảng kịch bản chi tiết (Thời lượng: ~38 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác màn hình (Visual & Timeline) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) & SFX/Nhịp |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | Trên màn hình là 2 biểu đồ Retention mô phỏng đặt cạnh 2 timeline: Bản trên rơi dốc đứng ở giây thứ 6; Bản dưới giữ ngang đến giây thứ 28 nhờ đổi vị trí clip Reveal. | Đừng nói toạc kết quả từ **giây thứ năm** | Nếu bạn giải thích toạc cả cách làm lẫn kết quả ngay từ giây thứ năm, người xem không còn lý do gì để ở lại đến giây thứ ba mươi. `[SFX: Tiếng kéo khối clip trên timeline sang cuối]` |
| `00:03 – 00:11` | **2. PROOF (Bản cũ bị lộ sớm)** | Phát 4 giây của **Bản Cũ**: mở đầu nói *"Hôm nay mình xoay chiếc bàn 90 độ và kéo rèm lại để hết ngược sáng, kết quả đây"* ngay ở giây thứ 5. | Tiết lộ hết ngay đầu làm **mất động lực xem tiếp** | Ở bản dựng cũ này, ngay giây thứ năm người nói đã kể xong hết: xoay bàn, kéo rèm và cho xem luôn cảnh đẹp hoàn chỉnh. Phần hai mươi giây giải thích phía sau gần như thừa. |
| `00:11 – 00:19` | **3. BODY (Bước 1: Vấn đề + 1 Manh mối)** | Screen Record **Bản Remake**: Mở đầu bằng cảnh ngược sáng tối đen (Vấn đề), tiếp theo chỉ lộ đúng 1 cảnh tay Thành cầm một tờ giấy trắng A4 (Manh mối gây tò mò), chưa cho xem toàn cảnh đã sửa. | Cho xem vấn đề + **một mảnh manh mối gây tò mò** | Khi dựng lại từ đúng bộ file gốc đó, mình đổi cấu trúc. Ba giây đầu cho xem cảnh mặt bị tối đen vì ngược sáng. Ngay sau đó, mình chỉ nhá đúng một cảnh tay cầm tờ bìa trắng kèm câu nói: *"Không cần mua thêm đèn, mình chỉ đổi đúng một góc phản sáng."* |
| `00:19 – 00:26` | **3. BODY (Bước 2: Dẫn dắt gọn)** | Cắt nhanh 2 thao tác xoay góc máy và đặt tấm hắt sáng trong 6 giây, giữ góc máy cận chưa lộ toàn bộ gương mặt đã sáng. | Giữ góc cận trong lúc thao tác để **nuôi sự chờ đợi** | Trong sáu giây tiếp theo, mình chỉ dùng các góc quay cận tay thao tác để người xem vừa hiểu nguyên lý vừa muốn nhìn thấy khung hình cuối cùng trông ra sao. |
| `00:26 – 00:33` | **3. BODY (Bước 3: Mở Reveal đúng điểm)** | Đúng giây 26: Cắt sang khung hình A/B trượt ngang (Wipe Before/After) từ cảnh ngược sáng tối đen sang cảnh sáng trong trẻo hoàn chỉnh. | Mở kết quả hoàn chỉnh (Reveal) ở **nhịp cuối video** | Và đến giây thứ hai mươi sáu, mình mới mở toàn cảnh trước và sau đặt cạnh nhau. Lúc này khoảnh khắc mở kết quả mới thực sự tạo được cảm giác thỏa mãn. `[Nghỉ 0.5s]` |
| `00:33 – 00:38` | **4. CLOSE & CTA** | A-roll Thành nhìn ống kính, phía trên là sơ đồ 3 khối: `Vấn đề + Manh mối` → `Quá trình cận cảnh` → `Reveal A/B`. | **Theo dõi kênh** để xem tiếp series dựng lại video | Đó là cách mình sắp xếp lại thứ tự kể chuyện có chủ đích. Bạn theo dõi kênh để xem tiếp các bài dựng lại video trong series này nhé. |

### 3. Checklist Shot List cần quay/chụp
- [ ] **Shot 1 (Screen Record so sánh 2 Timeline):** Timeline 1 để khối clip kết quả màu xanh lá ở đầu (`00:05`); Timeline 2 chuyển khối màu xanh lá đó về cuối (`00:26`) và đặt khối màu vàng (Manh mối) ở `00:04`.
- [ ] **Shot 2 (Source ví dụ thực tế):** Cảnh góc bàn làm việc bị ngược sáng cửa sổ (Before), cảnh cận tay chỉnh góc/tấm phản sáng (Process), và cảnh sau khi chỉnh sáng rõ (After Reveal).
- [ ] **Shot 3 (A-roll):** Thành ngồi trước màn hình phân tích sự khác nhau giữa "kể toạc hết" và "mở manh mối".

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok
```text
Nhiều video mẹo vặt hoặc hậu trường bị rớt người xem ngay từ giây thứ 6 vì nói toạc hết cả cách làm lẫn kết quả quá sớm.
Thử giữ lại toàn cảnh kết quả cho phần Reveal cuối video, còn ở đầu chỉ đưa ra vấn đề + 1 mảnh manh mối nhỏ nhé. Theo dõi kênh để xem tiếp series Remake.
#dungcochudich #storytelling #videoediting #contentcreator
```

#### B. Caption Facebook Reels
```text
Khi dựng các video dạng "cải tạo góc làm việc", "sửa lỗi quay chụp" hay "hậu trường làm sản phẩm", thứ tự bạn sắp xếp các cảnh quay quyết định việc người xem có ở lại đến cuối hay không.
Nếu ngay giây thứ 5 bạn đã cho xem hết toàn cảnh kết quả và kể xong quy trình, 25 giây còn lại sẽ mất đi sức hút. Hãy cho xem vấn đề rõ ràng, nhá 1 chi tiết giải pháp gây tò mò, giữ góc cận khi làm và mở toàn cảnh trước/sau ở nhịp cuối.
#dungcochudich #videomarketing #videoeditor #xaykenh
```

#### C. Bài đăng Facebook cá nhân (Viết riêng — 160 chữ)
```text
Hôm qua mình nhận dựng lại (remake) một chiếc video chia sẻ hậu trường từ đúng bộ file quay cũ của một bạn creator. Bản đầu bạn tự cắt có nội dung rất thực tế, nhưng người xem hầu như rời đi ngay sau 6 giây đầu tiên.

Lý do rất đơn giản: ở giây thứ 4, bạn đã cho hiện luôn bức ảnh kết quả hoàn chỉnh kèm một câu tóm tắt toàn bộ cách làm. Khi não người xem đã nhận đủ câu trả lời, họ sẽ lướt sang video tiếp theo ngay lập tức.

Mình không quay thêm bất kỳ cảnh nào, chỉ đảo lại vị trí các clip trên timeline theo 3 nhịp:
1. Giây 0 – 4: Cho thấy rõ khung hình đang bị lỗi ngược sáng (đặt câu hỏi trong đầu người xem).
2. Giây 4 – 8: Chỉ cắt vào cảnh cận bàn tay cầm một món đồ xử lý kèm 1 câu gợi mở, tuyệt đối chưa mở góc rộng.
3. Giây 8 – 26: Đi qua 2 bước thao tác gọn gàng rồi mới đặt cú trượt Before/After toàn cảnh ở nhịp cuối.

Cùng một nguyên liệu quay, chỉ cần kiểm soát thời điểm mở kết quả (Reveal) là giữ được mạch tò mò từ đầu tới cuối.
```

---

## VIDEO 44 — MÃ `C050`: NĂM LỖI AI KHÔNG TỰ NHẬN RA TRONG VIDEO

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Bảy, 09/01/2027 *(Lịch linh hoạt)*
- **Pillar / Tuyến nội dung:** P3 (AI trong workflow editor) — `AI04` (Kiểm định chất lượng đầu ra AI)
- **Format:** Audit (Khoanh lỗi trực tiếp trên từng frame đầu ra của AI)
- **Tệp người xem:** Creator (Người đang dùng các công cụ AI tạo/cắt video tự động nhưng thắc mắc vì sao video trông vẫn thiếu tự nhiên và kém thuyết phục)
- **Mục tiêu Funnel:** Nhận biết (Awareness → Định vị chuyên môn kiểm soát chất lượng AI)
- **Claim duy nhất:** Công cụ AI dựng video hiện tại không tự nhận ra được 5 lỗi về ngữ cảnh, cảm xúc và trọng tâm bán hàng — và đó là 5 điểm bạn bắt buộc phải kiểm tra lại bằng mắt trước khi bấm đăng.
- **Bằng chứng cần chuẩn bị:** 5 đoạn trích thực tế từ đầu ra của công cụ AI video (Auto-cut, AI B-roll generator, Auto-caption, Auto-ducking) được khoanh đỏ rõ ràng từng lỗi trên màn hình.
- **CTA & Offer:** Lưu video để làm bảng rà lỗi trước khi xuất file (**Không bán**).

### 2. Bảng kịch bản chi tiết (Thời lượng: ~41 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác màn hình (Visual & Timeline) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) & SFX/Nhịp |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | Thành đứng/ngồi cạnh màn hình đang dừng ở một frame B-roll do AI tự chèn bị lệch hẳn bối cảnh Việt Nam. Khung đỏ khoanh vào lỗi kèm nhãn `AI OUTPUT AUDIT`. | Năm lỗi trong video mà **AI không tự nhận ra** | Dùng AI để phụ dựng video rất nhanh, nhưng có năm lỗi này máy không bao giờ tự báo cho bạn biết. `[SFX: Tiếng còi báo nhẹ / khoanh bút đỏ]` |
| `00:03 – 00:10` | **2. BODY (Lỗi 1: Cắt mất âm đuôi)** | Zoom vào sóng âm cuối câu của một bản AI Auto-cut: vết cắt chém ngang khi chữ cuối câu vẫn còn đang ngân nhẹ, làm câu nói nghe bị hụt hơi. | 1. Cắt cụt **chữ cuối câu** khi giọng còn đang ngân | Lỗi thứ nhất: cắt mất đuôi chữ. AI nhận diện khoảng lặng bằng ngưỡng âm lượng, nên khi bạn hạ giọng ở cuối câu, nó rất hay cắt phăng mất nửa chữ cuối cùng. |
| `00:10 – 00:17` | **3. BODY (Lỗi 2: Nhấn sai từ khóa)** | Khung hình phụ đề AI tự tạo: chữ *"cực kỳ"* được phóng to màu đỏ, trong khi chữ *"bảo hành 12 tháng"* lại viết nhỏ màu trắng. | 2. Phóng to từ cảm thán, **bỏ quên từ khóa bán hàng** | Lỗi thứ hai: nhấn sai trọng tâm bán hàng. AI thường tô màu vào những từ bạn đọc to như *"cực kỳ"*, *"rất là"*, thay vì tô vào thông tin khách cần mua như *"bảo hành mười hai tháng"*. |
| `00:17 – 00:25` | **3. BODY (Lỗi 3: B-roll lệch văn hóa)** | Khung hình AI tự chèn B-roll: Lời thoại đang nói về *"chủ tiệm tạp hóa ở Việt Nam"* nhưng AI lại tự chèn cảnh siêu thị châu Âu với bảng giá đô-la. | 3. Chèn B-roll tự động **lệch bối cảnh Việt Nam** | Lỗi thứ ba: B-roll lệch ngữ cảnh văn hóa. Bạn nói về cửa hàng nhỏ ở Việt Nam nhưng AI lại tự động chèn cảnh phố xá phương Tây, làm người xem tụt cảm giác tin tưởng ngay lập tức. |
| `00:25 – 00:34` | **3. BODY (Lỗi 4 & 5: Biểu cảm & Nhạc nền)** | Chia đôi màn hình: Bên trái là hiệu ứng chuyển cảnh của AI đè lên đúng khoảnh khắc người nói mỉm cười gật đầu; Bên phải là thanh nhạc nền không chịu hạ xuống ở câu kết. | 4. Đè hiệu ứng lên **biểu cảm thật**<br>5. Không hạ nhạc ở **câu chốt** | Lỗi thứ tư là chèn hiệu ứng đè lên đúng biểu cảm thật trên gương mặt. Và lỗi thứ năm là nhạc nền giữ nguyên âm lượng từ đầu tới cuối, lấn át cả câu chốt quan trọng nhất. `[Nghỉ 0.5s]` |
| `00:34 – 00:41` | **4. CLOSE & CTA** | Hiện bảng tổng kết 5 điểm rà soát sau khi dùng AI trên màn hình. | **Lưu lại 5 điểm này** để kiểm tra trước khi xuất video | Đó là lý do mình luôn kiểm tra lại bằng mắt sau khi AI chạy xong. Bạn lưu lại năm điểm này để rà soát trước khi xuất video tiếp theo nhé. |

### 3. Checklist Shot List cần quay/chụp
- [ ] **Shot 1 (Screen Record Lỗi 1):** Cận cảnh sóng âm bị AI cắt sát vào phần đuôi chữ.
- [ ] **Shot 2 (Screen Record Lỗi 2):** Frame phụ đề AI tô màu vào từ *"cực kỳ"* thay vì từ khóa chính.
- [ ] **Shot 3 (Screen Record Lỗi 3):** Frame AI Auto B-roll chèn cảnh văn phòng/cửa hàng Tây Âu vào câu thoại tiếng Việt bình dân.
- [ ] **Shot 4 (Screen Record Lỗi 4 & 5):** Frame hiệu ứng transition che mất gương mặt + đường âm lượng nhạc thẳng tắp.
- [ ] **Shot 5 (A-roll):** Thành ngồi trước màn hình, chỉ vào từng lỗi và tổng kết ở cuối.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok
```text
AI giúp rút ngắn khâu cắt nháp rất nhiều, nhưng có 5 lỗi về cảm xúc, trọng tâm chữ và bối cảnh văn hóa mà máy không tự nhận ra được.
Lưu lại 5 điểm này để làm bước kiểm tra cuối cùng trước khi bạn bấm xuất file đăng kênh nhé.
#dungcochudich #aiworkflow #videoediting #contentcreator
```

#### B. Caption Facebook Reels
```text
Nếu bạn đang dùng các tính năng tự cắt khoảng lặng, tự tạo phụ đề hay tự chèn hình minh họa bằng AI, đừng bấm xuất file đăng ngay.
Chỉ cần dành thêm 5 phút kiểm tra lại 5 điểm mà máy thường xử lý máy móc: đuôi chữ cuối câu, từ khóa cần tô màu, bối cảnh hình minh họa có hợp Việt Nam không, biểu cảm gương mặt và âm lượng nhạc ở câu chốt.
Lưu lại video này để đối chiếu mỗi lần bạn dùng AI hỗ trợ dựng nhé.
#dungcochudich #aivideo #videomarketing #xaykenh
```

#### C. Bài đăng Facebook cá nhân (Viết riêng — 175 chữ)
```text
Trong hơn 6 tháng đưa các công cụ AI vào quy trình dựng video hàng ngày, mình luôn giữ một nguyên tắc: AI được quyền làm bản nháp đầu tiên, nhưng không bao giờ được quyền bấm nút "Export" cuối cùng.

Lý do là vì thuật toán xử lý theo ngưỡng âm thanh và từ khóa bề mặt, nên nó thường xuyên mắc 5 lỗi mà chỉ mắt người làm nội dung mới nhận ra:
1. Cắt cụt âm đuôi: Khi người nói hạ giọng trầm xuống ở cuối câu để tạo chiều sâu, AI tưởng là tiếng ồn nền và cắt phăng đi.
2. Nhấn sai từ khóa: Máy hay phóng to các từ đọc lớn tiếng ("cực kỳ", "luôn đó") thay vì cụm từ mang tính chuyển đổi.
3. Hình minh họa (Auto B-roll) lệch văn hóa: Đang nói chuyện bán lẻ tại Việt Nam nhưng máy lại lấy stock siêu thị nước ngoài đè vào.
4. Hiệu ứng chuyển cảnh đè mất ánh mắt hoặc cái gật đầu thật của người nói.
5. Nhạc nền giữ đều một mức, không biết lùi lại khi vào câu kết luận.

Bạn nào đang dùng AI để tăng tốc độ làm video nhớ dành ra 5 phút cuối rà lại đúng 5 gạch đầu dòng này, chất lượng bản xuất ra sẽ chỉn chu hơn hẳn.
```

---

# TUẦN 12: CHUYỂN ĐỔI DỊCH VỤ, CHUẨN HÓA SUBTITLE/SFX & KHÓA 48 VIDEO CHÍNH THỨC
*(11/01/2027 – 16/01/2027)*

---

## VIDEO 45 — MÃ `C017`: MỘT QUẢNG CÁO ĐANG NHỒI QUÁ NHIỀU THÔNG TIN

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Hai, 11/01/2027
- **Pillar / Tuyến nội dung:** P1 (Marketing trong video) — `MKT05` (Audit & Tối ưu thông điệp video bán hàng)
- **Format:** Audit (Đánh dấu trực tiếp các claim dư thừa trên video quảng cáo của chủ shop và dựng lại bản tinh gọn)
- **Tệp người xem:** Chủ shop (Chủ shop thời trang, mỹ phẩm, gia dụng, F&B tự làm video quảng cáo nhưng hay cố nhồi hết mọi ưu điểm sản phẩm vào 30 giây)
- **Mục tiêu Funnel:** Cân nhắc → Chuyển đổi Dịch vụ (Consideration → Lead Generation)
- **Claim duy nhất:** Nhồi 5 lời hứa bán hàng khác nhau vào một video 30 giây khiến khách hàng không nhớ được bất kỳ điểm mạnh nào; cắt gọn về đúng 1 thông điệp chuyển đổi duy nhất mới là cách giúp video ra đơn.
- **Bằng chứng cần chuẩn bị:** 1 video quảng cáo 30 giây của chủ shop (đã xin phép sử dụng hoặc che mờ tên thương hiệu nếu cần) có 5 nhãn dán đỏ đánh số `Claim #1` đến `Claim #5` đặt cạnh bản dựng lại chỉ tập trung chứng minh sâu `Claim #1`.
- **CTA & Offer:** Nhắn chữ **EDIT** kèm mục tiêu video (**Dịch vụ Edit/Media**).

### 2. Bảng kịch bản chi tiết (Thời lượng: ~40 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác màn hình (Visual & Timeline) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) & SFX/Nhịp |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | Trên màn hình là khung hình video của một chủ shop, chỉ trong 15 giây nhưng xuất hiện liên tiếp 5 nhãn đỏ: `1. Chất vải mát` / `2. Không nhăn` / `3. Đủ 6 màu` / `4. Đổi trả 30 ngày` / `5. Giảm 30%`. | Nhồi **năm thông điệp vào 30 giây** làm khách quên sạch | Đây là lý do nhiều chủ shop quay video rất kỹ nhưng chạy quảng cáo lại không ai hỏi mua: bạn đang bắt khách nhớ năm thứ trong ba mươi giây. `[SFX: 5 tiếng "bíp" dồn dập khi 5 nhãn hiện lên]` |
| `00:03 – 00:11` | **2. PROOF / TENSION** | Mở timeline của bản gốc: cứ mỗi 5 giây người nói lại nhảy sang một ưu điểm khác mà không có cảnh nào chứng minh tới nơi tới chốn. | Mỗi ưu điểm chỉ nói lướt qua **năm giây không đủ tin** | Bạn nhìn timeline bản gốc này nhé. Giây thứ ba nói về chất vải mát, giây thứ tám đã nhảy sang chuyện có sáu màu, giây mười bốn nói chuyện đổi trả, giây hai mươi lại báo khuyến mãi. Không một ưu điểm nào đủ sâu để khách tin. |
| `00:11 – 00:20` | **3. BODY (Bước 1: Cắt bỏ 4 claim phụ)** | Thành dùng thao tác trên Premiere tắt/gạt 4 khối thông tin phụ sang một bên, chỉ giữ lại và phóng to khối duy nhất: *"Không nhăn sau khi giặt máy"*. | Giữ lại **một lý do mua hàng mạnh nhất** | Khi nhận sửa lại video này, việc đầu tiên mình làm là cất bốn thông điệp phụ sang cho các video sau. Trong clip ba mươi giây này, mình chỉ giữ lại đúng một điểm đắt giá nhất với dân văn phòng: áo bỏ máy giặt xong lấy ra mặc luôn không cần ủi. |
| `00:20 – 00:31` | **3. BODY (Bước 2: Dành trọn 25s chứng minh 1 claim)** | Chạy bản dựng mới của Thành: 3s đầu vò áo/lấy từ lồng giặt → 12s giữa zoom cận bề mặt vải phẳng phiu so với áo thường → 10s cuối lên dáng mặc đi làm + 1 dòng chú thích ưu đãi nhỏ ở góc. | Dành trọn 25 giây để **chứng minh tận mắt một điểm** | Toàn bộ hai mươi lăm giây sau đó chỉ phục vụ đúng thông điệp này: từ cảnh rút áo khỏi lồng giặt, zoom cận bề mặt vải phẳng phiu cho tới lúc khoác lên người đi làm. Còn chuyện có sáu màu, mình chỉ để một dòng chữ nhỏ gọn ở cuối. `[Nghỉ 0.6s]` |
| `00:31 – 00:40` | **4. CLOSE & CTA** | A-roll Thành nhìn thẳng ống kính, bên cạnh là khung so sánh `Bản 5 Claim (Rối)` vs `Bản 1 Claim (Rõ trọng tâm)`. | Nhắn chữ **EDIT** kèm mục tiêu video của bạn | Một video bán hàng tốt không phải là nói được nhiều nhất, mà là làm khách tin chắc chắn vào một điểm. Nếu bạn có sẵn footage nhưng video chưa ra đúng thông điệp muốn bán, nhắn chữ EDIT cho mình kèm mục tiêu video nhé. |

### 3. Checklist Shot List cần quay/chụp
- [ ] **Shot 1 (Screen Record Audit):** Video gốc của shop với 5 thẻ tag màu đỏ bật lên liên tục ở các giây `03s`, `08s`, `14s`, `20s`, `25s`.
- [ ] **Shot 2 (Screen Record Timeline):** Thao tác xóa/ẩn 4 đoạn thoại lan man và ghép chuỗi B-roll chứng minh 1 thông điệp duy nhất.
- [ ] **Shot 3 (Split-screen A/B):** Đặt bản cũ rối chữ cạnh bản mới tập trung vào cận cảnh sản phẩm.
- [ ] **Shot 4 (A-roll):** Thành ngồi tại bàn dựng, nói rõ ràng, chân thành với tệp chủ shop.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok
```text
Nhiều chủ shop vì tiếc công quay nên cố nhồi cả chất liệu, bảng màu, giá bán, đổi trả và khuyến mãi vào chung 1 video 30 giây — kết quả là khách lướt qua mà không nhớ được gì.
Nếu bạn có sẵn footage quay sản phẩm nhưng dựng lên chưa ra đúng trọng tâm bán hàng, nhắn chữ "EDIT" cho mình kèm mục tiêu video nhé.
#dungcochudich #videobanhang #marketingvideo #videoediting
```

#### B. Caption Facebook Reels
```text
Tâm lý chung của người bán hàng khi tự làm video là sợ nói thiếu: sợ không nhắc tới bảng màu thì khách tưởng có 1 màu, sợ không nói bảo hành thì khách không yên tâm.
Thế là trong đúng 30 giây, chúng ta bắt người xem nghe tới 5 lời hứa khác nhau. Cuối cùng mỗi thứ chỉ lướt qua 4-5 giây, chẳng có điểm nào đủ sâu để thuyết phục.
Mình vừa sửa lại một ca thực tế bằng cách cắt bỏ 4 ý phụ để dồn toàn bộ hình ảnh vào đúng 1 lý do mua hàng mạnh nhất. Nếu bạn đang có sẵn nguyên liệu quay mà chưa biết gọt thông điệp sao cho gọn, nhắn chữ "EDIT" cho mình nhé.
#dungcochudich #chushop #videomarketing #quangcaovideo
```

#### C. Bài đăng Facebook cá nhân (Viết riêng — 175 chữ)
```text
Tuần trước một chị chủ shop thời trang gửi cho mình đoạn video 32 giây chị tự quay và dựng để chạy quảng cáo, kèm câu hỏi: "Sao chị nói đủ hết ưu điểm của áo rồi mà khách xem xong cứ trôi tuột đi em nhỉ?"

Khi mở video ra đếm, mình thấy trong đúng 32 giây đó có tới 5 lời hứa bán hàng chen chúc nhau: chất vải mát (giây 3), chống nhăn (giây 8), đủ 6 màu (giây 14), freeship đổi trả (giây 20) và giảm giá khi mua đôi (giây 26). Vì cái gì cũng muốn nói, nên mỗi ưu điểm chỉ được xuất hiện 5 giây — không đủ thời gian để mắt người xem kiểm chứng.

Mình xử lý lại từ đúng bộ file quay sẵn của chị theo 3 quyết định:
1. Cắt bỏ 4 thông điệp phụ (để dành làm 4 video riêng cho các ngày sau).
2. Chọn đúng 1 nỗi đau lớn nhất của khách công sở: "giặt máy xong mặc luôn không cần ủi".
3. Dành trọn 25 giây hình ảnh chỉ để chứng minh lời hứa đó (từ cảnh rút áo ở lồng giặt đến zoom cận thớ vải).

Nếu bạn đang có sẵn footage sản phẩm nhưng video dựng lên vẫn bị dàn trải, nhắn chữ "EDIT" cho mình kèm mục tiêu video để mình xem qua nhé.
```

---

## VIDEO 46 — MÃ `C034`: BA LỖI SUBTITLE KHIẾN VIDEO KHÓ ĐỌC

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Ba, 12/01/2027
- **Pillar / Tuyến nội dung:** P2 (Edit & Storytelling) — `EDIT05` (Bố cục chữ, Subtitle & Trải nghiệm thị giác)
- **Format:** Audit (Soi 3 lỗi phụ đề phổ biến trực tiếp trên giao diện điện thoại và cách sửa)
- **Tệp người xem:** Creator (Người tự dựng video trên CapCut/Premiere hay dùng preset phụ đề tự động mà quên kiểm tra khả năng đọc thực tế trên màn hình điện thoại)
- **Mục tiêu Funnel:** Nhận biết → Thu hút tải tài liệu (Lead Magnet)
- **Claim duy nhất:** Phụ đề sinh ra để giúp người xem nắm ý nhanh hơn khi tắt tiếng, nhưng 3 lỗi về vị trí vùng chết, cách ngắt dòng và độ tương phản đang biến phụ đề thành thứ cản trở mắt người xem.
- **Bằng chứng cần chuẩn bị:** Khung giả lập giao diện TikTok/Reels thật (có vùng nút Tim/Comment bên phải và vùng Tên kênh/Caption bên dưới) đè lên 3 ví dụ phụ đề lỗi vs 3 bản đã sửa chuẩn Safe Zone.
- **CTA & Offer:** Nhận Checklist & Khung Safe Zone đặt chữ trong **Starter Kit** ở bio.

### 2. Bảng kịch bản chi tiết (Thời lượng: ~39 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác màn hình (Visual & Timeline) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) & SFX/Nhịp |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | Khung hình điện thoại hiển thị một video có dòng phụ đề bị dòng mô tả bài đăng và cụm nút Tim/Share của TikTok đè kín không đọc được. Thành bật lớp lưới đỏ `SAFE ZONE` lên. | Ba lỗi phụ đề làm người xem **mỏi mắt lướt qua** | Rất nhiều bạn mất công làm phụ đề cho video, nhưng khi đăng lên thì một nửa số chữ đó không ai đọc được vì ba lỗi này. `[SFX: Tiếng bật khung lưới cảnh báo]` |
| `00:03 – 00:11` | **2. BODY (Lỗi 1: Vùng chết giao diện)** | Minh họa trực quan **Lỗi 1**: Dòng phụ đề đặt quá thấp bị caption của TikTok che khuất. Thành kéo cụm chữ lên cao hơn (nằm ở khoảng 1/3 dưới khung hình, trên vùng caption). | 1. Đặt chữ rơi vào **vùng nút bấm và mô tả** | Lỗi thứ nhất: đặt chữ rơi vào vùng chết của ứng dụng. Khi dựng trên máy tính bạn thấy khoảng dưới rất trống, nhưng khi lên điện thoại, toàn bộ phần đáy và cạnh phải sẽ bị tên kênh, mô tả và nút thả tim che khuất. |
| `00:11 – 00:20` | **3. BODY (Lỗi 2: Quá dài hoặc nhảy từng chữ)** | Minh họa **Lỗi 2**: Một bên là dòng phụ đề dài 3 hàng chữ nhỏ xíu; một bên là hiệu ứng nhảy từng chữ một (1-word pop-up) chớp liên tục. Thành sửa lại thành cụm 4–6 chữ/dòng theo nhịp nói. | 2. Để dòng quá dài hoặc **nhảy từng chữ mỏi mắt** | Lỗi thứ hai: ngắt dòng sai nhịp đọc. Nếu bạn để một lần hiện ba dòng dài thì người xem đọc không kịp, còn nếu cho nhảy từng chữ một liên tục suốt bốn mươi giây thì mắt họ sẽ rất mỏi. Hãy ngắt theo cụm từ bốn đến sáu chữ một lần. |
| `00:20 – 00:28` | **3. BODY (Lỗi 3: Tương phản kém với nền)** | Minh họa **Lỗi 3**: Chữ trắng không viền/bóng đặt đè lên chiếc áo sơ mi trắng của người nói nên chữ biến mất hoàn toàn. Thành thêm lớp Drop Shadow mềm (`Opacity 75%`, `Distance 4`, `Size 12`) hoặc thanh nền mờ. | 3. Chữ sáng đè lên nền sáng **thiếu độ tương phản** | Lỗi thứ ba: chữ chìm vào nền. Khi người nói mặc áo sáng màu mà bạn để chữ trắng không có bóng đổ nhẹ hoặc lớp nền mờ phía sau, dòng chữ sẽ tàng hình ngay lập tức. |
| `00:28 – 00:33` | **3. BODY (Tổng kết trước/sau)** | Đặt khung hình Phụ đề Lỗi cạnh khung hình Phụ đề Chuẩn (nằm gọn trong Safe Zone, 5 chữ/dòng, nổi rõ trên nền sáng). | Phụ đề tốt là **nhìn lướt một nhịp hiểu ngay** | Một dòng phụ đề tốt là khi người xem đang tắt tiếng ngoài đường vẫn đọc lướt được ngay lập tức mà không phải nheo mắt. `[Nghỉ 0.5s]` |
| `00:33 – 00:39` | **4. CLOSE & CTA** | A-roll Thành chỉ vào màn hình có file PNG khung lưới Safe Zone đặt sẵn trên timeline. | Tải **checklist và khung Safe Zone** trong Starter Kit ở bio | Đó là cách mình đặt chữ có chủ đích. Mình để sẵn checklist phụ đề kèm khung kiểm tra vùng an toàn trong Starter Kit ở bio, bạn vào lấy về đè lên timeline nhé. |

### 3. Checklist Shot List cần quay/chụp
- [ ] **Shot 1 (Screen Record / Graphic):** Khung overlay giao diện TikTok/Reels PNG trong suốt đặt đè lên timeline Premiere để chứng minh vùng bị che chữ.
- [ ] **Shot 2 (Screen Record Lỗi 2):** So sánh preset nhảy từng chữ (1-word) vs preset 3 dòng dài vs bản ngắt cụm 4–6 chữ chuẩn.
- [ ] **Shot 3 (Screen Record Lỗi 3):** Thao tác chỉnh thông số Drop Shadow / Background trong bảng Essential Graphics của Premiere trên nền áo trắng.
- [ ] **Shot 4 (A-roll):** Thành mặc áo sáng màu (để làm trực quan luôn cho ví dụ số 3), ngồi trước màn hình dựng.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok
```text
Làm phụ đề xong nhớ kiểm tra 3 điểm này trước khi xuất file: có bị caption/nút bấm của app che mất không, mỗi dòng có vừa tầm mắt quét (4–6 chữ) không, và chữ có bị chìm vào áo sáng màu không.
Mình để sẵn Checklist kiểm tra chữ và khung vùng an toàn trong Starter Kit ở bio, bạn vào lấy về dùng ngay nhé.
#dungcochudich #videoediting #subtitle #contentcreator
```

#### B. Caption Facebook Reels
```text
Hơn một nửa người xem video ngắn trên điện thoại có thói quen xem ở nơi công cộng với âm lượng rất nhỏ hoặc tắt tiếng ở vài giây đầu. Lúc này, dòng phụ đề chính là thứ giữ họ ở lại.
Nhưng nếu dòng chữ đó bị đẩy xuống sát đáy màn hình (đè vào phần tên tài khoản), nhảy từng chữ một làm hoa mắt, hoặc chữ trắng nằm đè lên chiếc áo trắng thì công sức gõ phụ đề coi như bỏ phí.
Bạn có thể lấy bộ Checklist phụ đề kèm khung canh vùng an toàn trong Starter Kit ở trang cá nhân của mình để gắn cố định vào phần mềm dựng nhé.
#dungcochudich #videomarketing #xaykenh #capcut #premierepro
```

#### C. Bài đăng Facebook cá nhân (Viết riêng — 165 chữ)
```text
Lúc dựng video trên màn hình máy tính 24 inch hoặc 27 inch, khung hình 9:16 trông lúc nào cũng rộng rãi và thoáng mắt. Chính vì thế mà rất nhiều bạn đặt dòng phụ đề ở đâu cũng thấy ổn — cho đến khi đăng lên điện thoại thật.

Trong quy trình kiểm tra bản dựng cuối cùng trước khi gửi file cho khách, mình luôn bật một lớp khung giả lập giao diện điện thoại lên timeline để rà đúng 3 lỗi phụ đề:
1. Lỗi vùng chết (25% diện tích cạnh dưới và 15% cạnh phải của màn hình sẽ bị tên kênh, dòng mô tả và dãy nút tương tác che mất).
2. Lỗi nhịp đọc (để nguyên cả câu dài 15–18 chữ trên một khung hình khiến mắt không quét kịp, hoặc dùng hiệu ứng nháy từng chữ một liên tục gây mỏi mắt).
3. Lỗi mất tương phản (chữ trắng hoặc vàng nhạt đặt trực tiếp lên nền áo sơ mi sáng màu mà không có bóng đổ mềm phía sau).

Mình có đính kèm sẵn bảng Checklist phụ đề và khung canh vùng an toàn trong bộ Starter Kit ở phần giới thiệu, bạn nào hay tự dựng video tải về áp vào project là chuẩn ngay từ đầu.
```

---

## VIDEO 47 — MÃ `C035`: SOUND EFFECT KHÔNG NÊN CÓ MẶT Ở MỌI CUT

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Năm, 14/01/2027
- **Pillar / Tuyến nội dung:** P2 (Edit & Storytelling) — `EDIT05` (Sound Design & Tiết chế âm thanh)
- **Format:** Before/after (So sánh trực tiếp Audio A/B giữa bản lạm dụng SFX và bản đặt SFX có chủ đích)
- **Tệp người xem:** Editor (Editor trẻ hoặc creator tự dựng đang bị cuốn vào trào lưu nhồi tiếng *whoosh, pop, ding, riser, chuột click* vào mọi vết cắt mỗi 1–2 giây)
- **Mục tiêu Funnel:** Nhận biết (Awareness → Khẳng định gu thẩm mỹ và tư duy biên tập âm thanh chuyên nghiệp)
- **Claim duy nhất:** Khi mọi vết cắt đều gắn sound effect thì không còn vết cắt nào là điểm nhấn nữa; chỉ đặt âm thanh phụ trợ vào đúng điểm chuyển trạng thái hoặc từ khóa chính mới giúp video sang và rõ thông điệp.
- **Bằng chứng cần chuẩn bị:** Timeline Premiere Pro hiển thị 3 track SFX (A3, A4, A5): **Bản A** chi chít 14 file âm thanh trong 12 giây vs **Bản B** rút gọn chỉ còn đúng 3 file âm thanh đặt tại điểm mở vấn đề, điểm hiện số liệu và điểm khóa kết quả.
- **CTA & Offer:** Lưu video để làm chuẩn kiểm tra âm thanh (**Không bán**).

### 2. Bảng kịch bản chi tiết (Thời lượng: ~38 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác màn hình (Visual & Timeline) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) & SFX/Nhịp |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | Timeline Premiere có 12 giây nhưng xếp chồng 14 file SFX màu hồng kín mít ở track A3–A4. Thành quét chuột chọn và xóa đi 11 file, chỉ chừa lại 3 điểm. | Đừng chèn sound effect vào **mọi vết cắt trên timeline** | Nếu cứ mỗi lần đổi cảnh hay hiện chữ bạn lại chèn một tiếng whoosh hay tiếng pop, video của bạn sẽ nghe giống một hội chợ âm thanh hơn là một nội dung chuyên nghiệp. |
| `00:03 – 00:11` | **2. PROOF (Nghe Bản A - Lạm dụng)** | Phát 5 giây **Bản A**: Cứ mỗi giây lại kêu *Whoosh - Pop - Ding - Boing - Click* dồn dập đè lên giọng người nói. Đồng hồ đo âm lượng (Audio Meter) nhảy đỏ liên tục. | Quá nhiều hiệu ứng âm thanh làm **nhiễu giọng nói chính** | Bạn nghe thử năm giây lạm dụng sound effect này nhé: *(Phát Bản A 4s với tiếng whoosh, pop, ding liên hồi)*. Khi mọi chi tiết đều kêu lên cùng lúc, tai người nghe bị quá tải và không còn tập trung vào lời nói nữa. |
| `00:11 – 00:21` | **3. BODY (Quy tắc tiết chế 3 điểm)** | Screen Record **Bản B**: Thành giữ lại đúng 3 vị trí SFX trên timeline, đánh dấu rõ vai trò của từng điểm và hạ âm lượng SFX xuống mức `-18dB` đến `-15dB` (thấp hơn giọng nói ít nhất `10dB`). | Chỉ đặt SFX ở **điểm chuyển trạng thái** và từ khóa chính | Khi làm sạch lại bản dựng này, mình bỏ đi bảy mươi phần trăm tiếng động thừa và chỉ giữ lại ở ba chỗ có mục đích rõ ràng: một tiếng chuyển nhẹ khi bước từ câu mở đầu sang phần phân tích; một tiếng gõ gọn khi con số bằng chứng hiện lên; và một nhịp trầm khóa câu kết. |
| `00:21 – 00:28` | **3. BODY (Nghe Bản B - Tinh tế)** | Phát lại đúng 5 giây đó ở **Bản B**: Giọng nói tròn vành rõ chữ, các vết cắt nhảy góc bình thường hoàn toàn tự nhiên không cần tiếng whoosh, chỉ đến đúng con số kết quả mới có một tiếng *Click/Pop* trầm tinh tế ở `-16dB`. | Vết cắt thông thường **không cần tiếng động đi kèm** | Nghe lại bản đã tiết chế nhé: *(Phát Bản B 4s — giọng nói sạch, êm, điểm nhấn số liệu vang nhẹ rất sang)*. |
| `00:28 – 00:33` | **3. BODY (Đúc kết)** | A-roll Thành ngồi trước màn hình, chỉ nhẹ vào cột Audio Meter đang giữ mức cân bằng giữa Voice (`-6dB`) và SFX (`-16dB`). | Hiệu ứng âm thanh chỉ có giá trị khi **được dùng đủ ít** | Những vết cắt đổi góc thông thường hoàn toàn không cần tiếng động đi kèm. Hiệu ứng âm thanh chỉ thực sự có sức nặng khi nó xuất hiện đủ ít. `[Nghỉ 0.5s]` |
| `00:33 – 00:38` | **4. CLOSE & CTA** | Hiện thẻ tóm tắt quy tắc: `Giọng nói (-6dB)` > `SFX điểm nhấn (-15dB đến -18dB)` > `Nhạc nền (-22dB)`. | **Lưu lại quy tắc âm thanh** này cho project tiếp theo | Đó là cách mình thiết kế âm thanh có chủ đích. Bạn lưu lại quy tắc này để rà soát lại các track âm thanh ở video tiếp theo nhé. |

### 3. Checklist Shot List cần quay/chụp
- [ ] **Shot 1 (Screen Record Timeline A/B):** Quay cận cảnh track Audio A1–A5 trên Premiere khi chưa dọn (14 clip SFX) và sau khi dọn (3 clip SFX).
- [ ] **Shot 2 (Export Audio A/B):** Xuất 2 đoạn 4–5 giây có âm thanh đối lập rõ rệt để người xem nghe bằng loa điện thoại cũng phân biệt được ngay.
- [ ] **Shot 3 (Screen Record Audio Meter):** Cận cảnh bảng chỉnh dB (`-6dB` cho thoại, `-16dB` cho SFX, `-22dB` cho nhạc nền).
- [ ] **Shot 4 (A-roll):** Thành ngồi tại bàn dựng nói câu dẫn và câu kết.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok
```text
Khi mọi vết cắt trên timeline đều kêu whoosh, pop hay ding, tai người xem sẽ bị mỏi và câu nói quan trọng nhất lại mất đi điểm nhấn.
Hãy thử xóa bớt 70% sound effect thừa, chỉ giữ lại ở đúng điểm chuyển trạng thái và từ khóa chính với âm lượng thấp hơn giọng nói khoảng 10dB. Lưu lại để thử ngay nhé.
#dungcochudich #sounddesign #videoediting #premierepro
```

#### B. Caption Facebook Reels
```text
Có một giai đoạn rất nhiều bạn mới học dựng video nghĩ rằng: chèn càng nhiều tiếng động (whoosh, pop, ding, tiếng gõ phím) vào mỗi vết cắt thì video càng chuyên nghiệp.
Nhưng thực tế khi xem những video thương hiệu có chiều sâu, bạn sẽ thấy phần lớn các vết cắt đổi góc máy đều diễn ra trong im lặng tự nhiên. Sound effect chỉ xuất hiện đúng lúc cần hướng mắt người xem vào một con số hoặc một sự thay đổi trạng thái quan trọng.
Mình làm phép so sánh A/B ngay trong video này để bạn nghe thử sự khác biệt nhé.
#dungcochudich #editor #videomarketing #amthanhvideo
```

#### C. Bài đăng Facebook cá nhân (Viết riêng — 165 chữ)
```text
Nếu mở ngẫu nhiên 10 chiếc video ngắn hướng dẫn hoặc chia sẻ kiến thức hiện nay, không khó để bắt gặp kiểu dựng mà cứ mỗi 1.5 giây lại có một tiếng "whoosh" xẹt qua, một tiếng "pop" nổ lên kèm một tiếng "ding" chói tai.

Hồi mới gom được bộ thư viện vài trăm file Sound Effects (SFX), mình cũng từng thích nhét kín các track âm thanh bên dưới như vậy vì nhìn timeline rất "hoành tráng". Nhưng khi nghe lại bằng loa điện thoại, chính đống âm thanh phụ trợ đó lại đánh nhau trực tiếp với giọng của người nói.

Hiện tại, khi rà soát phần âm thanh cho khách hàng, mình luôn áp dụng 3 nguyên tắc tiết chế:
1. Các vết cắt đổi góc máy thông thường (jump cut / punch-in) không gắn bất kỳ tiếng whoosh nào.
2. Chỉ đặt SFX vào đúng 2–3 điểm cần neo sự chú ý trong suốt 30 giây (khoảnh khắc chuyển từ vấn đề sang giải pháp, hoặc lúc hiện con số bằng chứng).
3. Luôn kéo âm lượng SFX nằm thấp hơn giọng nói từ 10dB đến 12dB (thoại ở khoảng -6dB thì SFX chỉ nằm ở -16dB đến -18dB) để làm nền tôn giọng nói lên.

Đôi khi bớt đi 10 tiếng động thừa lại là bước làm cho video nghe sang hơn hẳn.
```

---

## VIDEO 48 — MÃ `C051`: TẠI SAO AI CHƯA THAY EDITOR TRONG CASE NÀY? *(VIDEO KHÓA SPRINT 4 & 48 VIDEO)*

### 1. Thông tin định danh
- **Ngày đăng:** Thứ Bảy, 16/01/2027 *(Lịch linh hoạt — Khóa mốc 48 video của 12 tuần)*
- **Pillar / Tuyến nội dung:** P3 (AI trong workflow editor) — `AI04` (Case study thực tế kết hợp AI & Tư duy Editor)
- **Format:** Case study (Bóc tách toàn diện 1 dự án thật từ lúc nhận bài toán, dùng AI tăng tốc 40% khâu chuẩn bị đến quyết định biên tập giữ uy tín cho khách hàng)
- **Tệp người xem:** Khách hàng (Chủ doanh nghiệp, chuyên gia, thương hiệu cá nhân cần một người đồng hành dựng video hiểu marketing, biết dùng AI để tối ưu chi phí/thời gian nhưng đặt uy tín thương hiệu lên hàng đầu)
- **Mục tiêu Funnel:** Tin cậy → Chuyển đổi Dịch vụ (Trust → Conversion)
- **Claim duy nhất:** Trong dự án thực tế này, AI giúp mình rút ngắn 40% thời gian lọc nháp và tạo tư liệu phụ trợ, nhưng quyết định cắt bỏ câu nói dễ gây hiểu lầm và giữ lại nhịp ngập ngừng chân thật để tạo niềm tin cho khách hàng là việc mà chỉ một editor có tư duy marketing mới làm được.
- **Bằng chứng cần chuẩn bị:** Hồ sơ project thật trên máy của Thành: Bảng đo thời gian thực hiện (`Khâu AI làm thô: giảm từ 50 phút xuống 20 phút`) + Timeline Premiere hiển thị đoạn thoại khách hàng bị vấp/nói quá đà được Thành biên tập lại mạch lạc và giữ lại khoảnh khắc chân thật đắt giá.
- **CTA & Offer:** Nhắn chữ **EDIT** kèm mục tiêu video (**Dịch vụ Edit/Media**).

### 2. Bảng kịch bản chi tiết (Thời lượng: ~42 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác màn hình (Visual & Timeline) | Text trên màn hình (On-screen Text) | Lời thoại của Thành (Audio) & SFX/Nhịp |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:04` | **1. HOOK** | Thành mở project thực tế trên màn hình: một bên là cửa sổ AI hỗ trợ lọc transcript & tạo B-roll minh họa; một bên là timeline Premiere hoàn chỉnh. Hiện con số `AI giảm 40% thời gian thô`. | AI giúp nhanh hơn 40%, nhưng **hai quyết định này thuộc về editor** | Trong dự án này, AI giúp mình tiết kiệm bốn mươi phần trăm thời gian chuẩn bị, nhưng có hai quyết định sống còn trên timeline mà máy không thể làm thay. `[SFX: Tiếng mở project sâu, đĩnh đạc]` |
| `00:04 – 00:12` | **2. PROOF (Phần AI làm rất tốt)** | Screen Record nhanh 3 việc AI đã hỗ trợ trong project: (1) Gỡ băng 25 phút quay thô ra văn bản, (2) Lọc các câu nói lắp, (3) Tạo 2 tấm графиc nền minh họa thông số. | AI làm tốt: gỡ băng thoại, **lọc câu nói lắp** và tạo hình nháp | Khi nhận hai mươi lăm phút quay thô từ một khách hàng làm dịch vụ tư vấn, mình dùng AI để gỡ băng văn bản và lọc nhanh các đoạn nói vấp. Khâu dọn dẹp vốn mất gần một tiếng giờ chỉ mất hai mươi phút. |
| `00:12 – 00:22` | **3. BODY (Quyết định 1 của Editor: Bảo vệ uy tín thương hiệu)** | Zoom vào đoạn transcript được AI chấm điểm cao nhất (vì giọng nói rất sung: *"Bên mình xử lý cái này một trăm phần trăm thành công ngay tuần đầu"*). Thành gạch bỏ câu đó và chọn take nói điềm đạm, chuẩn xác hơn: *"Thông thường sau hai tuần đầu đối chiếu số liệu, mình mới chốt phương án"*. | Quyết định 1: Cắt bỏ câu **nói quá đà gây mất uy tín** | Nhưng đây là chỗ con người phải can thiệp. Công cụ AI chấm điểm cao nhất cho câu khách lỡ miệng nói rất sung là *"cam kết một trăm phần trăm ngay tuần đầu"* vì nghe giống câu giật tít. Còn mình chủ động cắt bỏ câu đó và chọn lại đoạn khách giải thích lộ trình hai tuần thực tế — vì với tệp khách hàng cao cấp, nói quá đà là mất uy tín ngay. |
| `00:22 – 00:32` | **3. BODY (Quyết định 2 của Editor: Giữ nhịp thở tạo niềm tin)** | Zoom vào timeline ở giây thứ 20 của video: trước khi khách chia sẻ một bài học thất bại thật, có một nhịp thở trầm xuống 0.7 giây. AI định cắt bỏ khoảng lặng này, nhưng Thành giữ nguyên và tắt nhạc nền. | Quyết định 2: Giữ lại **nhịp ngập ngừng chân thật** tạo niềm tin | Quyết định thứ hai nằm ở giây hai mươi: khi khách kể về một lần tự làm sai trong quá khứ, anh ấy dừng lại thở nhẹ nửa giây rồi mới nói tiếp. AI coi đó là khoảng thừa cần xóa, còn mình giữ nguyên khoảnh khắc đó vì chính sự ngập ngừng thật ấy mới làm người xem tin. `[Nghỉ 0.6s]` |
| `00:32 – 00:42` | **4. CLOSE & CTA** | A-roll Thành nhìn thẳng vào ống kính, ánh sáng ấm áp, chuyên nghiệp. Khung hình hiện dòng chữ tổng kết hành trình & lời mời hợp tác rõ ràng. | Nhắn chữ **EDIT** kèm mục tiêu video bạn đang cần làm | AI giúp chúng ta đi nhanh hơn ở phần thô, nhưng giữ được sự tử tế và thông điệp đúng cho thương hiệu vẫn là việc của người dựng có chủ đích. Nếu bạn đang cần một người đồng hành như vậy cho kênh hoặc chiến dịch sắp tới, nhắn chữ EDIT cho mình kèm mục tiêu video nhé. |

### 3. Checklist Shot List cần quay/chụp
- [ ] **Shot 1 (Screen Record Bảng so sánh công việc):** Khung chia rõ `Phần AI xử lý (20 phút)` vs `Phần Editor quyết định (25 phút)`.
- [ ] **Shot 2 (Screen Record Transcript & Take Selection):** Hình ảnh so sánh 2 take thoại trên bảng Text (Take 1 nói quá đà bị AI gợi ý chọn vs Take 2 chuẩn mực, đáng tin cậy được Thành chọn).
- [ ] **Shot 3 (Screen Record Timeline nhịp nghỉ):** Cận cảnh đoạn sóng âm nhịp thở 0.7 giây được giữ lại và đánh dấu Marker xanh lá `GIỮ CẢM XÚC THẬT`.
- [ ] **Shot 4 (A-roll chính & kết):** Thành ngồi trước trạm làm việc hoàn chỉnh, phong thái chững chạc, điềm đạm sau hành trình 12 tuần.

### 4. Bản phân phối đa kênh (`crosspost`)

#### A. Caption TikTok
```text
Trong project thực tế này, AI giúp mình giảm 40% thời gian lọc file thô, nhưng việc cắt bỏ câu nói dễ gây hiểu lầm và giữ lại nhịp ngập ngừng chân thật để tạo niềm tin cho khách hàng lại là quyết định của người dựng.
Nếu bạn có sẵn nguyên liệu quay và cần một editor hiểu mục tiêu marketing đồng hành, nhắn chữ "EDIT" cho mình nhé.
#dungcochudich #marketingvideo #aiworkflow #videoediting
```

#### B. Caption Facebook Reels
```text
Sau hàng chục video kết hợp cả AI lẫn dựng thủ công, khách hàng hay hỏi mình: "Đâu là ranh giới thật sự giữa máy và người dựng?"
Trong dự án gần đây nhất mình làm cho một anh khách bên mảng dịch vụ tư vấn, AI giúp mình gỡ băng 25 phút quay thô chỉ trong vài phút. Nhưng khi chọn câu đưa lên hình, AI lại ưu tiên câu anh lỡ nói hơi quá đà vì nghe giống câu "giật tít". Mình đã cắt bỏ câu đó và chọn lại take anh nói điềm đạm, thực tế hơn để bảo vệ uy tín dài hạn cho thương hiệu của anh.
Nếu bạn đang tìm người dựng hiểu cả công cụ AI lẫn thông điệp kinh doanh đằng sau từng câu nói, nhắn chữ "EDIT" cho mình nhé.
#dungcochudich #videomarketing #personalbranding #editor
```

#### C. Bài đăng Facebook cá nhân (Viết riêng — 180 chữ)
```text
Tuần này khép lại mốc 48 video chính thức trong lộ trình 12 tuần xây dựng kênh "Dựng Có Chủ Đích" của mình. Nhìn lại các dự án thực tế đã làm, câu hỏi mình nhận được nhiều nhất từ khách hàng vẫn là: "Dùng AI vào quy trình dựng thì khách hàng được lợi gì, và editor còn giữ vai trò gì?"

Ở một dự án gần đây (tổng thời lượng quay thô dài 25 phút), mình áp dụng song song cả hai:
1. Phần AI làm thô (giúp rút ngắn khoảng 40% thời gian chuẩn bị): Tự động gỡ băng toàn bộ lời thoại ra văn bản, lọc bỏ các đoạn đọc vấp và nháp nhanh bố cục minh họa.
2. Quyết định bảo vệ uy tín thương hiệu: Thuật toán AI tự động chấm điểm cao nhất cho một câu nói khách lỡ miệng cam kết hơi quá đà vì nó giống cấu trúc "câu view". Mình chủ động gạt câu đó ra và chọn lại take khách nói đúng thực tế triển khai để giữ niềm tin với tệp khách hàng doanh nghiệp.
3. Quyết định giữ cảm xúc thật: Giữ lại đúng 0.7 giây khách trầm ngâm trước khi chia sẻ bài học thật, thay vì cắt phẳng lì như máy.

Nếu bạn đang có sẵn footage hoặc kế hoạch làm nội dung video cần đúng cả tốc độ lẫn chiều sâu thương hiệu, nhắn chữ "EDIT" cho mình kèm mục tiêu video để anh em mình trao đổi cụ thể nhé.
```

---

## BẢNG KIỂM SOÁT CHẤT LƯỢNG & CHUYỂN ĐỔI SPRINT 4 (TUẦN 10 – TUẦN 12)

| Chỉ số kiểm soát | Quy chuẩn bắt buộc trong Sprint 4 | Trạng thái trong bộ kịch bản |
| :--- | :--- | :--- |
| **Tỷ trọng Pillar (12 video)** | 4 video P1 (`C014`, `C015`, `C016`, `C017`) + 5 video P2 (`C031`, `C032`, `C033`, `C034`, `C035`) + 3 video P3 (`C049`, `C050`, `C051`) | Đạt chuẩn phân bổ Lịch 90 ngày |
| **Tỷ trọng Funnel & Offer** | - **Starter Kit (Lead Magnet):** 4 video (`C014`, `C015`, `C032`, `C034`)<br>- **Dịch vụ Edit/Media (Conversion/Consideration):** 3 video (`C049`, `C017`, `C051`)<br>- **Không bán (Xây uy tín & Lưu/Follow):** 5 video (`C031`, `C016`, `C033`, `C050`, `C035`) | Đạt chuẩn không spam bán hàng, mỗi video đúng 1 CTA |
| **Chuẩn Giọng Điệu (`brand-voice`)** | Xưng *"mình"* - gọi *"bạn"*; không mở đầu bằng câu chào; có chỉ dẫn `[Nghỉ 0.5s - 0.6s]` trước câu chốt; kết bằng signature *"Đó là cách mình dựng có chủ đích"* | 12/12 video tuân thủ 100% |
| **Chuẩn Đa Kênh (`crosspost`)** | Mỗi video có riêng: Caption TikTok ngắn + Caption FB Reels gần gũi + Bài viết Facebook cá nhân 155–180 chữ có cấu trúc 3 quyết định thực tế | 12/12 video có đủ 3 phiên bản độc lập |

<!-- ===== /file: personal-brand-video-engine/references/01_Y_TUONG_VA_SCRIPT/04_SPRINT_4_TUAN_10_12_CHUYEN_DOI.md ===== -->

<!-- ===== file: personal-brand-video-engine/references/01_Y_TUONG_VA_SCRIPT/05_12_VIDEO_DU_PHONG_BAO_CAO_VA_CHUYEN_DOI_SAU.md ===== -->

# BỘ 12 VIDEO BÁO CÁO SPRINT, CASE STUDY & CHUYỂN ĐỔI SÂU (`C018–C021`, `C036–C039`, `C052–C054`, `C060`)

> **Vai trò chiến lược của bộ 12 video này:**
> - Trong **Ngân hàng 60 Content**, 48 video đã được phân bổ trực tiếp vào 12 tuần thực thi chuẩn (`Sprint 1` đến `Sprint 4`).
> - **12 mã nội dung trong tài liệu này** (`C018, C019, C020, C021, C036, C037, C038, C039, C052, C053, C054, C060`) đóng vai trò là **Vũ khí Chuyển đổi Sâu & Review Sprint**:
>   1. Dùng để đăng vào **slot Linh hoạt (Thứ Bảy)** cuối mỗi Sprint (Tuần 3, 6, 9, 12) nhằm công bố báo cáo số liệu thật và lọc format thắng.
>   2. Dùng làm **Video Chuyển Đổi Trực Tiếp (Bottom-of-Funnel)** khi kênh bắt đầu có lượng truy cập hồơ sơ (Profile Visit) cao, đẩy thẳng về 3 Offer: **Dịch vụ Edit/Media**, **Cộng đồng/Lộ trình Zero To AI**, và **Công cụ Xưởng Media** (cùng Lead Magnet **Starter Kit v1**).
>   3. Dùng làm **Quỹ video dự phòng chiến lược** để thay thế ngay bất kỳ format nào có tỷ lệ giữ chân 3 giây dưới ngưỡng chuẩn trong quá trình chạy 90 ngày.

---

## PHẦN 1: NHÓM PILLAR 1 — PHÂN TÍCH CHUYỂN ĐỔI & ĐO LƯỜNG KÊNH (`C018` – `C021`)

---

### VIDEO 1: `C018` — Phân tích một video bán hàng không cần hiệu ứng mạnh

#### 1. Thông tin định danh
- **Mã nội dung:** `C018`
- **Pillar & Tuyến:** P1 (Marketing trong video) — `MKT05` (Phân tích video chuyển đổi)
- **Format:** Breakdown (Phân tích trên màn hình + Timeline)
- **Tệp khán giả:** Chủ shop / Người tự quay video bán sản phẩm vật lý
- **Giai đoạn Funnel:** Nhận biết (Awareness)
- **CTA:** Lưu video
- **Offer đích:** Không bán
- **Bằng chứng sử dụng:** Case video bán hàng công khai (ví dụ: video bán bàn phím cơ / đèn bàn học / phụ kiện công nghệ chỉ dùng cắt thẳng).
- **Core Claim:** Video bán hàng ra đơn nhờ đặt bằng chứng sử dụng lên đầu và chỉ rõ lợi ích, không phải nhờ hiệu ứng chuyển cảnh xoay lật.

#### 2. Bảng kịch bản sản xuất chi tiết (38 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác Timeline (Visual) | Text trên màn hình (On-screen Text) | Lời thoại (Voiceover / A-roll) & SFX |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | Split-screen trên dưới: Phía trên là video bán đèn bàn học cắt thẳng (Straight cut) đạt tương tác hỏi mua cao; phía dưới là timeline Premiere hoàn toàn không có cục preset hiệu ứng nào. | Video bán hàng này không dùng một hiệu ứng chuyển cảnh nào | **[SFX: Tiếng click chuột dứt khoát]** Video bán hàng này không dùng một hiệu ứng chuyển cảnh nào nhưng khách vẫn hỏi giá liên tục. |
| `00:03 – 00:10` | **2. PROOF / TENSION** | Phóng to đoạn bình luận hỏi mua thật (đã che tên shop) rồi kéo playhead qua 3 vết cắt đầu tiên trên timeline: chỉ có cắt thẳng và âm thanh gốc. | Không lật cảnh — Chỉ tập trung vào **bằng chứng** | Nhiều bạn chủ shop cứ nghĩ phải thêm chữ bay hoặc xoay màn hình thì người xem mới ở lại. **[ngừng 0.5s]** Thực tế khách mua hàng cần thấy sản phẩm hoạt động thật trong 3 giây đầu. |
| `00:10 – 00:18` | **3. BODY (Bước 1)** | Khoanh đỏ 3 giây đầu của video mẫu: cảnh bật công tắc đèn trong phòng tối, thấy rõ vùng sáng không bị chói màn hình laptop. | Bước 1: Mở đầu bằng **cảnh sử dụng thật** | Nhìn vào cấu trúc 3 nhịp của video này nhé. **[SFX: Whoosh nhẹ]** Một: Ba giây đầu không chào hỏi, bật đèn ngay trong phòng tối để chứng minh độ phủ sáng. |
| `00:18 – 00:26` | **3. BODY (Bước 2)** | Cắt sang cảnh zoom cận 2X vào khớp xoay hợp kim của đèn và tiếng bẻ khớp chắc chắn; hiển thị sóng âm thanh (Waveform) rõ trên timeline. | Bước 2: Cận cảnh chi tiết giải quyết **nỗi lo** | Hai: Từ giây thứ 4 đến 15, dùng ba góc cận cảnh liên tiếp vào khớp xoay và chất liệu. **[ngừng 0.5s]** Khách sợ đèn bị rũ cổ sau vài tuần, cảnh cận này trả lời thẳng nỗi lo đó. |
| `00:26 – 00:32` | **3. BODY (Bước 3)** | Hiển thị 5 giây cuối của video mẫu: đặt đèn cạnh bàn làm việc hoàn chỉnh + dòng text chỉ dẫn nơi mua rõ ràng. | Bước 3: Chốt bằng **ngữ cảnh đặt hàng** rõ ràng | Ba: Năm giây cuối chỉ nói đúng một lý do nên chọn phiên bản này và chỉ chỗ bấm vào giỏ hàng. |
| `00:32 – 00:38` | **4. CLOSE & CTA** | A-roll Thành ngồi trước màn hình timeline, gật đầu nhẹ. Cuối frame hiện bảng tóm tắt 3 bước: `1. Cảnh test thật -> 2. Cận cảnh giải quyết nỗi lo -> 3. CTA rõ`. | Lưu lại cấu trúc **3 nhịp cắt thẳng** này | Khi thông điệp và cảnh quay cận đã đủ thuyết phục, cắt thẳng luôn là cách dựng tôn sản phẩm nhất. **[ngừng 0.5s]** Bạn lưu lại cấu trúc ba nhịp này để đối chiếu khi quay video sản phẩm tiếp theo nhé. |

#### 3. Shot List chuẩn bị
- **A-roll:** 1 góc trung cận Thành ngồi bàn làm việc, màn hình phụ phía sau mở timeline Premiere.
- **Screen Record:** Timeline mô phỏng lại cấu trúc cắt thẳng của 1 video bán hàng thực tế (chia 3 vùng màu: Màu xanh lá = Hook test thật; Màu vàng = 3 shot cận cảnh proof; Màu cam = CTA).
- **Asset đồ họa:** Khung khoanh đỏ vùng sản phẩm, bảng tóm tắt 3 nhịp ở màn hình kết.

#### 4. Caption TikTok & Facebook Reels
- **Caption TikTok:**
  Một video bán hàng ra đơn nhờ cảnh chứng minh sản phẩm thật chứ không phải nhờ hiệu ứng xoay lật.
  Cấu trúc 3 nhịp cắt thẳng cho chủ shop tự quay: Mở bằng cảnh test thật → Cận cảnh giải quyết nỗi lo → Chỉ dẫn mua rõ ràng.
  Lưu lại video này để làm khung đối chiếu trước khi bấm máy nhé.
  `#dungcochudich #videoediting #marketingvideo #banhangquavideo`
- **Caption Facebook Reels:**
  Nếu bạn là chủ shop tự quay video sản phẩm và ngại mình không biết làm hiệu ứng cầu kỳ, hãy nhìn cấu trúc của video này. Không có một chuyển cảnh xoay lật nào, toàn bộ là cắt thẳng (straight cut) nhưng giữ chân người mua nhờ 3 quyết định chọn cảnh rất thực tế. Bạn lưu lại 3 nhịp này để áp dụng ngay cho sản phẩm của shop mình nhé.

#### 5. Bài đăng Facebook cá nhân (`crosspost`)
```text
Hôm qua có một bạn chủ shop đồ gia dụng nhắn hỏi mình: "Em tự quay bằng điện thoại, chỉ biết cắt ghép cơ bản trên CapCut chứ không làm được hiệu ứng bay lượn thì video có bán được hàng không anh?"

Câu trả lời của mình luôn là: Với video bán hàng trực tiếp, hiệu ứng mạnh đôi khi còn làm khách nghi ngờ bạn đang che giấu khuyết điểm sản phẩm.

Mình vừa mổ xẻ lại một video bán đèn bàn làm việc có tỷ lệ hỏi mua rất tốt dù trên timeline chỉ dùng đúng kỹ thuật cắt thẳng (straight cut). Lý do nó thuyết phục được người mua nằm ở 3 quyết định chọn cảnh:

1. Giây 01–03 (Bằng chứng thị giác ngay lập tức): Không mở đầu bằng lời chào hay logo shop. Video bắt đầu ngay khoảnh khắc bật công tắc đèn trong phòng tối để người xem thấy dải sáng thực tế không gây lóa màn hình máy tính.
2. Giây 04–15 (Cận cảnh trả lời nỗi sợ của khách): Người mua đèn kẹp bàn sợ nhất là khớp nối bị lỏng sau vài tuần. Video dành 3 cú cắt cận cảnh (2X) vào khớp kim loại kèm âm thanh vặn ốc thật (bản dựng giữ nguyên tiếng động gốc tại hiện trường thay vì đè nhạc lớn).
3. Giây 16–25 (Một lời chỉ dẫn duy nhất): Đặt đèn vào tổng thể bàn làm việc gọn gàng và chỉ rõ phân loại nào hợp với bàn dưới 1m2.

Khi hình ảnh đã trả lời đúng câu hỏi trong đầu khách hàng, nhiệm vụ của người dựng chỉ là cắt bỏ những giây thừa để nhịp xem không bị ngắt quãng. Đó là cách mình dựng có chủ đích.

(Mình đính kèm ảnh chụp sơ đồ 3 nhịp cắt dưới bình luận, bạn nào đang tự quay sản phẩm cho shop có thể lưu về đối chiếu ngay trước buổi quay tới).
```

---

### VIDEO 2: `C019` — Sau 12 video tôi giữ lại format nào?

#### 1. Thông tin định danh
- **Mã nội dung:** `C019`
- **Pillar & Tuyến:** P1 (Marketing trong video) — `MKT06` (Đo lường & tối ưu kênh)
- **Format:** Report (Báo cáo Sprint công khai số liệu thật)
- **Tệp khán giả:** Creator / Người đang xây kênh cá nhân
- **Giai đoạn Funnel:** Tin cậy (Trust)
- **CTA:** Nhận bảng KPI
- **Offer đích:** Starter Kit (`STARTER_KIT_V1_DUNG_CO_CHU_DICH`)
- **Bằng chứng sử dụng:** Bảng theo dõi số liệu thật sau 12 video đầu tiên (Retention 3s, Watch time trung bình, Save/Share rate, Profile visit).
- **Core Claim:** Đánh giá kênh sau 12 video không nhìn vào tổng lượt xem mà nhìn vào tỷ lệ lưu bài và lượt bấm vào hồ sơ để quyết định giữ hay bỏ format.

#### 2. Bảng kịch bản sản xuất chi tiết (40 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác Timeline (Visual) | Text trên màn hình (On-screen Text) | Lời thoại (Voiceover / A-roll) & SFX |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | Quay cận màn hình bảng Google Sheet theo dõi 12 video đầu tiên của Thành, có các dòng tô xanh (Giữ) và tô đỏ (Bỏ). | Sau 12 video đầu tiên: Giữ format nào, bỏ format nào? | **[SFX: Tiếng gõ phím cơ]** Sau 12 video đầu tiên trên kênh, mình quyết định dừng một format dù nó có lượt xem cao nhất. |
| `00:03 – 00:10` | **2. PROOF / TENSION** | Zoom vào 2 dòng số liệu đối lập trên bảng KPI: Video A (View cao nhưng Save 0.4%, Profile visit thấp) vs Video B (View vừa phải nhưng Save 6.2%, Profile visit cao gấp 4 lần). | Nhiều view nhưng không ai **lưu bài** hay **vào hồ sơ** | Lý do nằm ở bảng theo dõi này. **[ngừng 0.5s]** Những video chỉ nói về công cụ AI mới có lượt xem khá tốt, nhưng tỷ lệ lưu bài dưới 1% và gần như không ai bấm vào trang cá nhân. |
| `00:10 – 00:22` | **3. BODY (Quyết định 1 & 2)** | Cắt sang cảnh Thành chỉ tay vào 2 nhóm format màu xanh lá trên bảng: (1) Sửa lỗi video Before/After và (2) Bóc tách workflow AI + Premiere. | Giữ lại 2 format có **Save > 4%** và **Profile Visit** cao | Ngược lại, hai format có lượt xem vừa phải nhưng tạo ra hơn 80% lượt lưu và tin nhắn hỏi dịch vụ là: **[SFX: Pop]** Một, sửa lỗi video trước và sau trên cùng một khung hình. Hai, chỉ rõ bước nào AI làm thô, bước nào mình chỉnh tay trên Premiere. |
| `00:22 – 00:32` | **3. BODY (Quyết định 3)** | Hiển thị quy tắc lọc Sprint của Thành trên màn hình: `Giữ 3s > 65%` + `Save/Share > 3%` + `Có Profile Visit`. | Ba tiêu chí lọc format sau mỗi **12 video** | Vì vậy sang 12 video tiếp theo, mình cắt hẳn các bài điểm tin công cụ. **[ngừng 0.5s]** Mình chỉ giữ lại những format đạt đủ ba chỉ số: giữ chân 3 giây đầu, tỷ lệ lưu bài trên 3% và tạo ra lượt ghé thăm hồ sơ. |
| `00:32 – 00:40` | **4. CLOSE & CTA** | A-roll Thành cầm bản in hoặc mở trang Checklist & Bảng theo dõi KPI 12 video trong bộ Starter Kit. | Lấy mẫu **Bảng theo dõi KPI 12 video** ở bio | Làm nội dung có chủ đích là dám cắt bỏ thứ chỉ mang lại con số bề nổi. **[ngừng 0.5s]** Mình để sẵn mẫu bảng theo dõi 12 video này trong Starter Kit ở bio, bạn vào lấy về để tự đo kênh của mình nhé. |

#### 3. Shot List chuẩn bị
- **A-roll:** Thành ngồi trước màn hình lớn mở bảng Google Sheet `Bảng thực thi / KPI 12 video`.
- **Screen Record:** Quay cận thao tác lọc (Filter) cột `Save Rate` và `Profile Visit` trên bảng KPI, khoanh vùng 2 format thắng cuộc.
- **Asset đồ họa:** Card đồ họa hiển thị 3 ngưỡng chuẩn (`Hook 3s`, `Save/Share`, `Profile Visit`).

#### 4. Caption TikTok & Facebook Reels
- **Caption TikTok:**
  Tổng kết sau 12 video đầu tiên: Vì sao mình bỏ format nhiều view nhất để giữ lại 2 format có tỷ lệ lưu bài (Save) và vào hồ sơ (Profile Visit) cao hơn?
  Mình để sẵn mẫu Bảng theo dõi KPI 12 video trong bộ Starter Kit ở bio, bạn tải về dùng ngay cho kênh của mình nhé.
  `#dungcochudich #xaykenhtiktok #contentcreator #marketingvideo`
- **Caption Facebook Reels:**
  Cứ mỗi 12 video (tương đương 3 tuần làm đều đặn), mình lại ngồi nhìn lại bảng số liệu để quyết định giữ hay bỏ từng dạng bài. Có những video nhìn lượt xem rất vui mắt nhưng không mang lại một lượt lưu hay tin nhắn đúng tệp nào. Mình chia sẻ lại 3 chỉ số mình dùng để lọc format và gửi kèm biểu mẫu theo dõi này trong Starter Kit ở bio cho bạn nào đang tự xây kênh cá nhân.

#### 5. Bài đăng Facebook cá nhân (`crosspost`)
```text
Tuần này mình vừa hoàn thành mốc 12 video đầu tiên trong kế hoạch 90 ngày xây kênh "Dựng Có Chủ Đích". Thay vì chỉ nhìn vào tổng lượt xem rồi đoán mò bài tiếp theo nên làm gì, mình xuất toàn bộ dữ liệu ra một bảng theo dõi 5 chỉ số.

Kết quả làm mình phải gạch bỏ ngay một định kiến ban đầu: Video nhiều view nhất trong 12 bài vừa qua lại là video mang về ít giá trị chuyển đổi nhất (tỷ lệ lưu bài chỉ đạt 0.4% và gần như không tạo ra lượt bấm vào hồ sơ cá nhân).

Sau khi đối chiếu số liệu, đây là 3 quyết định mình chốt cho Sprint tiếp theo:

1. Loại bỏ các bài chỉ nói về "công cụ AI mới ra mắt": Nhóm bài này rất dễ hút người xem hiếu kỳ đại trà nhưng họ xem xong là lướt đi ngay, không phải tệp creator hay khách hàng cần cải thiện chất lượng video.
2. Giữ lại và nhân đôi format "Before/After sửa lỗi trên 1 khung hình": Dù lượt xem trung bình chỉ ở mức khá, tỷ lệ Save (Lưu lại để áp dụng) luôn đạt trên 5% vì người xem thấy ngay cách sửa câu mở đầu hoặc nhịp cắt.
3. Đo lường theo cụm 12 video thay vì buồn vui theo từng bài lẻ: Một video tụt view có thể do giờ đăng hoặc chủ đề hẹp, nhưng xu hướng của 12 video liên tiếp luôn nói thật về việc kênh đang thu hút ai.

Mình đã đóng gói sẵn biểu mẫu "Bảng theo dõi KPI 12 Video" kèm bộ khung kịch bản 30 giây vào trong tài liệu Starter Kit v1. Bạn nào đang xây kênh và muốn theo dõi nội dung bằng số liệu thực tế thì bấm vào link ở phần giới thiệu (bio) của mình để lấy bản mẫu về dùng ngay nhé.
```

---

### VIDEO 3: `C020` — Nhiều view nhưng không có khách vì sao?

#### 1. Thông tin định danh
- **Mã nội dung:** `C020`
- **Pillar & Tuyến:** P1 (Marketing trong video) — `MKT06` (Đo lường & tối ưu kênh)
- **Format:** Talking head kết hợp phân tích biểu đồ phễu (Funnel Breakdown)
- **Tệp khán giả:** Creator / Freelancer / Chủ dịch vụ xây kênh bán hàng
- **Giai đoạn Funnel:** Cân nhắc (Consideration)
- **CTA:** Kiểm tra funnel
- **Offer đích:** Không bán
- **Bằng chứng sử dụng:** Ảnh chụp màn hình số liệu 2 video thực tế (đã che thông tin nhạy cảm của khách): 1 video 50.000 view = 0 inbox vs 1 video 3.200 view = 4 cuộc trao đổi dịch vụ.
- **Core Claim:** Video có nhiều view nhưng không ra khách thường bị đứt ở một trong ba điểm: câu mở đầu gọi sai tệp, ví dụ quá chung chung, hoặc cuối video thiếu lời chỉ dẫn hành động khớp với vấn đề vừa giải quyết.

#### 2. Bảng kịch bản sản xuất chi tiết (39 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác Timeline (Visual) | Text trên màn hình (On-screen Text) | Lời thoại (Voiceover / A-roll) & SFX |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | A-roll Thành đưa lên màn hình 2 tấm thẻ số liệu cạnh nhau: Bên trái `50.000 lượt xem — 0 tin nhắn`; Bên phải `3.200 lượt xem — 4 khách hỏi dịch vụ`. | 50.000 view không có khách — 3.200 view ra **4 khách hàng** | **[SFX: Tiếng chuông báo tin nhắn]** Một video 50 nghìn lượt xem không có nổi một tin nhắn, còn video 3 nghìn lượt xem lại mang về 4 khách hàng. |
| `00:03 – 00:10` | **2. PROOF / TENSION** | Zoom vào biểu đồ nguồn lưu lượng và hành vi người xem của hai video (đã làm mờ tên tài khoản). | Lượt xem cao chưa chắc đã đi vào **phễu chuyển đổi** | Khi mình kiểm tra hậu trường hai video này, điểm khác biệt không nằm ở thuật toán phân phối, mà nằm ở việc video đang gọi ai ở lại ngay từ 3 giây đầu. |
| `00:10 – 00:18` | **3. BODY (Điểm đứt 1)** | Vẽ sơ đồ phễu 3 tầng trên màn hình. Khoanh đỏ tầng 1 (`Hook`): So sánh câu "Mẹo edit cực ảo trên điện thoại" (hút tệp xem giải trí) vs "Lỗi khiến video giới thiệu dịch vụ bị lướt qua" (hút đúng người bán hàng). | Điểm đứt 1: Câu Hook thu hút **người xem giải trí** | Có ba điểm đứt khiến video nhiều view vẫn không ra khách. **[SFX: Whoosh]** Một: Câu mở đầu quá rộng hoặc thiên về giải trí, khiến 90% người dừng lại xem là người không có nhu cầu mua. |
| `00:18 – 00:26` | **3. BODY (Điểm đứt 2)** | Khoanh đỏ tầng 2 (`Proof`): Cảnh phần thân video chỉ nói lý thuyết chung chung mà không chiếu quy trình làm việc hoặc kết quả sửa thật. | Điểm đứt 2: Phần thân thiếu **bằng chứng năng lực** | Hai: Phần giữa video chỉ chia sẻ mẹo vặt bề nổi mà không cho thấy cách bạn xử lý một ca thực tế, nên người xem thấy hay nhưng chưa đủ tin để giao việc. |
| `00:26 – 00:33` | **3. BODY (Điểm đứt 3)** | Khoanh đỏ tầng 3 (`CTA`): Cuối video chỉ nói "Follow mình nhé" thay vì dẫn sang bước nhận tài liệu hoặc nhắn tin tư vấn. | Điểm đứt 3: Cuối video không có **bước tiếp theo** rõ | Ba: Cuối video bạn quên đặt một bước chuyển tiếp hợp lý, khiến người đang có nhu cầu xem xong cũng không biết phải bắt đầu làm việc với bạn từ đâu. |
| `00:33 – 00:39` | **4. CLOSE & CTA** | A-roll Thành nhìn thẳng ống kính, bên cạnh hiện 3 câu hỏi tự kiểm tra phễu: `1. Hook gọi đúng ai? -> 2. Đã có bằng chứng thật chưa? -> 3. Bước tiếp theo là gì?`. | Kiểm tra lại **3 điểm chạm** này trong 5 video gần nhất | Bạn thử mở lại 5 video nhiều view nhất trên kênh của mình và kiểm tra xem phễu đang bị hở ở điểm nào trong 3 điểm trên nhé. |

#### 3. Shot List chuẩn bị
- **A-roll:** Thành nói trực diện, ánh sáng key light rõ nét, phong thái điềm tĩnh.
- **Screen Record / Đồ họa:** Sơ đồ phễu 3 tầng (`Hook lọc tệp` → `Thân bài chứng minh năng lực` → `CTA dẫn lối`) và ảnh chụp so sánh 2 cột số liệu ẩn thông tin nhạy cảm.

#### 4. Caption TikTok & Facebook Reels
- **Caption TikTok:**
  Vì sao video lên 50.000 view nhưng hộp thư vẫn trống trơn, trong khi video 3.000 view lại có 4 khách nhắn hỏi làm việc?
  Kiểm tra ngay 3 điểm đứt trong phễu nội dung: Câu mở đầu gọi sai tệp, phần thân thiếu bằng chứng thật, hoặc cuối video thiếu bước hành động tiếp theo.
  `#dungcochudich #marketingvideo #personalbranding #videomarketing`
- **Caption Facebook Reels:**
  Rất nhiều bạn làm dịch vụ hoặc kinh doanh khi xây kênh thường bị cuốn vào cuộc đua lượt xem, để rồi nản lòng vì kênh cả trăm nghìn view vẫn không ra đơn hay ra khách. Mình bóc tách lại 2 video thực tế để chỉ ra 3 điểm đứt phổ biến nhất giữa "người xem" và "khách hàng". Bạn đối chiếu thử với 5 video gần nhất trên kênh của mình xem sao nhé.

#### 5. Bài đăng Facebook cá nhân (`crosspost`)
```text
"Kênh của anh cũng có vài video lên mấy chục nghìn view, bình luận rôm rả lắm nhưng tuyệt nhiên không có ai nhắn hỏi dịch vụ cả Thành ạ."

Đó là câu mình nghe rất nhiều khi ngồi xem lại kênh cùng các bạn freelancer và chủ dịch vụ nhỏ. Khi mở số liệu hậu trường của một video 50.000 view (0 khách) đặt cạnh một video 3.200 view (4 khách nhắn trao đổi), sự khác biệt nằm ở cách thiết kế phễu ngay trong kịch bản 35 giây:

1. Lọc tệp ngay từ câu mở đầu (Hook): Video 50.000 view mở đầu bằng một câu gây tò mò đại chúng ("Xem AI biến hình cực đỉnh trong 3 giây"). Thuật toán đẩy rất mạnh cho tệp thích xem giải trí. Trong khi đó, video 3.200 view mở đầu bằng đúng nỗi đau của người thuê dịch vụ ("Vì sao bạn quay 10 clip giới thiệu dịch vụ mà khách vẫn chỉ hỏi giá rồi im lặng?"). Lượt xem ít hơn 15 lần, nhưng người dừng lại nghe là người đang gặp đúng bài toán đó.
2. Chứng minh bằng quy trình thật ở phần thân (Proof): Người mua dịch vụ không xuống tiền vì bạn biết một mẹo nhỏ; họ tin khi thấy bạn phân tích nguyên nhân và chiếu cảnh trước/sau khi sửa một ca cụ thể.
3. Đặt đúng cây cầu ở 5 giây cuối (CTA): Nếu cả video bạn đang phân tích quy trình làm việc cho khách hàng, 5 giây cuối hãy chỉ rõ cách họ gửi đề bài cho bạn (ví dụ: nhắn kèm mục tiêu và thời hạn), thay vì chỉ nói "Thả tim và follow kênh nhé".

View đại trà nuôi cảm giác hào hứng nhất thời, còn view đúng tệp mới nuôi được công việc đường dài. Đó là lý do trước khi bấm nút dựng, mình luôn hỏi video này đang nằm ở tầng nào của phễu.
```

---

### VIDEO 4: `C021` — Ba chỉ số editor nên xem ngoài lượt xem

#### 1. Thông tin định danh
- **Mã nội dung:** `C021`
- **Pillar & Tuyến:** P1 (Marketing trong video) — `MKT06` (Đo lường & tối ưu kênh)
- **Format:** Tutorial (Hướng dẫn đọc số liệu dành cho Editor)
- **Tệp khán giả:** Video Editor / Creator tự dựng video
- **Giai đoạn Funnel:** Nhận biết (Awareness)
- **CTA:** Lưu checklist
- **Offer đích:** Starter Kit (`STARTER_KIT_V1_DUNG_CO_CHU_DICH`)
- **Bằng chứng sử dụng:** Dashboard mẫu phân tích biểu đồ giữ chân (Retention Graph) liên kết trực tiếp với Timeline Premiere.
- **Core Claim:** Một editor có tư duy marketing không chỉ nhìn lượt xem tổng mà đọc 3 chỉ số (Giữ chân 3 giây, Tỷ lệ Lưu/Chia sẻ, và Tỷ lệ vào Hồ sơ) để biết chính xác cần sửa nhịp cắt nào trên timeline.

#### 2. Bảng kịch bản sản xuất chi tiết (37 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác Timeline (Visual) | Text trên màn hình (On-screen Text) | Lời thoại (Voiceover / A-roll) & SFX |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | Đặt biểu đồ Retention của TikTok nằm đè khớp theo chiều ngang ngay phía trên Timeline Premiere Pro của cùng một video. | Đừng chỉ nhìn lượt xem — Hãy đọc **3 chỉ số này** để sửa bản dựng | **[SFX: Tiếng bíp đo nhịp]** Nếu bạn là editor mà chỉ nhìn tổng lượt xem, bạn sẽ không biết phải sửa cú cắt nào ở video tiếp theo. |
| `00:03 – 00:10` | **2. PROOF / TENSION** | Chỉ con trỏ chuột vào điểm gãy dốc đứng ở giây thứ 02 và giây thứ 14 trên biểu đồ Retention, gióng thẳng xuống đoạn clip tương ứng trên timeline. | Biểu đồ số liệu chỉ rõ **cú cắt nào** đang làm rớt người xem | Tổng lượt xem chỉ cho biết kết quả cuối cùng. **[ngừng 0.5s]** Còn ba chỉ số dưới đây mới chỉ đích danh đoạn nào trên timeline của bạn đang có vấn đề. |
| `00:10 – 00:18` | **3. BODY (Chỉ số 1)** | Phóng to mốc `00:03` trên biểu đồ. Khoanh vùng 3 giây đầu trên timeline: cắt bỏ 1.5 giây lấy hơi và đẩy text tiêu đề lên frame đầu tiên. | 1. Tỷ lệ giữ chân **3 giây đầu** (Đo chất lượng Hook) | Một: Tỷ lệ giữ chân ở giây thứ ba. **[SFX: Pop]** Nếu chỉ số này dưới 60%, lỗi nằm ở khung hình mở đầu quá tĩnh hoặc câu đầu tiên chưa chạm vào vấn đề. |
| `00:18 – 00:25` | **3. BODY (Chỉ số 2)** | Hiển thị icon `Save` (Lưu) và `Share` (Chia sẻ) kèm công thức tính nhanh: `(Save + Share) / View`. Chiếu cảnh bảng tổng kết 3 bước rõ ràng ở giữa video. | 2. Tỷ lệ **Lưu và Chia sẻ** (Đo độ hữu ích của nội dung) | Hai: Tỷ lệ lưu và chia sẻ. **[ngừng 0.5s]** Khi người xem bấm lưu, nghĩa là cách bạn trình bày thông tin và chữ trên màn hình đủ gọn để họ muốn xem lại. |
| `00:25 – 00:31` | **3. BODY (Chỉ số 3)** | Hiển thị chỉ số `Profile Visits` (Lượt xem hồ sơ) và gióng xuống 5 giây cuối của timeline (đoạn Close & CTA). | 3. Lượt bấm vào **hồ sơ** (Đo sức thuyết phục của phần kết) | Ba: Lượt bấm vào hồ sơ. Chỉ số này đo trực tiếp xem 5 giây kết của bạn có đủ thuyết phục để họ tìm hiểu thêm hay không. |
| `00:31 – 00:37` | **4. CLOSE & CTA** | A-roll Thành chỉ vào bản Checklist QA & Bảng đo KPI trong bộ Starter Kit. | Tải **Checklist QA & Bảng KPI** trong Starter Kit ở bio | Đọc số liệu để biết cách cắt timeline chính là lợi thế của editor hiểu marketing. **[ngừng 0.5s]** Bạn lấy bản checklist và bảng đo này trong Starter Kit ở bio về dùng nhé. |

#### 3. Shot List chuẩn bị
- **A-roll:** Thành ngồi trước màn hình kép (1 bên là trang Analytics/Dashboard, 1 bên là Premiere Pro).
- **Screen Record:** Hiệu ứng gióng đường kẻ đứt nét màu vàng từ điểm tụt trên biểu đồ Retention xuống đúng vết cắt trên Timeline Premiere.
- **Asset đồ họa:** 3 thẻ chỉ số (`Hook 3s > 60%`, `Save + Share > 3%`, `Profile Visit`).

#### 4. Caption TikTok & Facebook Reels
- **Caption TikTok:**
  3 chỉ số giúp Editor biết chính xác cần sửa đoạn nào trên timeline ở video tiếp theo:
  1. Giữ chân 3 giây đầu (sửa cảnh mở đầu & text hook)
  2. Tỷ lệ Lưu & Chia sẻ (sửa cách đóng gói thông tin phần thân)
  3. Lượt vào hồ sơ (sửa nhịp kết & CTA)
  Bảng đo KPI và Checklist kiểm duyệt trước khi xuất file mình để sẵn trong Starter Kit ở bio nhé.
  `#dungcochudich #videoeditor #premierepro #marketingvideo`
- **Caption Facebook Reels:**
  Khi mới tập dựng video, mình từng chỉ nhìn xem video được bao nhiêu view rồi tự đoán xem mình dựng đẹp hay xấu. Từ lúc ghép biểu đồ giữ chân người xem (Retention) nằm đè lên timeline Premiere, mình mới thấy từng vết cắt, từng dòng chữ trên màn hình đều phản ánh thẳng vào 3 con số này. Bạn nào đang làm editor hoặc tự dựng video cho kênh có thể lấy bảng theo dõi mẫu trong Starter Kit ở bio của mình về áp dụng ngay.

#### 5. Bài đăng Facebook cá nhân (`crosspost`)
```text
Nhiều bạn editor khi giao file cho khách xong là coi như hết việc, hoặc nếu có xem lại video đăng lên kênh thì cũng chỉ nhìn lướt qua tổng số view.

Nhưng nếu bạn muốn nâng giá trị công việc từ "người cắt ghép theo lệnh" lên "người dựng video có tư duy marketing", hãy tập thói quen đặt biểu đồ số liệu nằm cạnh timeline Premiere. Ngoài lượt xem tổng, đây là 3 chỉ số mình luôn xem để biết cần chỉnh tay ở đâu cho video tiếp theo:

1. Tỷ lệ giữ chân ở giây thứ 03 (3-Second Retention): Chỉ số này chấm điểm trực tiếp 3 giây đầu trên timeline của bạn. Nếu hơn một nửa người xem rời đi trước giây thứ 3, mình biết ngay lần tới phải cắt bỏ khoảng lấy hơi ở đầu clip, đẩy hình ảnh kết quả lên frame đầu tiên và làm gọn lại dòng tiêu đề trên màn hình.
2. Tỷ lệ Lưu và Chia sẻ (Save & Share Rate): Người xem thả tim vì cảm xúc, nhưng họ bấm Lưu khi thông tin được trình bày rõ ràng, dễ tra cứu. Nếu video có thời lượng xem tốt nhưng ít người lưu, mình sẽ thêm một khung hình tổng kết 3 gạch đầu dòng ở giây thứ 28 để họ dễ chụp màn hình hoặc lưu lại.
3. Lượt ghé thăm hồ sơ (Profile Visits / Link Clicks): Đây là thước đo cho 5 giây cuối video. Nếu người xem coi hết bài mà không bấm vào trang cá nhân, nghĩa là câu chốt và lời kêu gọi hành động (CTA) đang bị rời rạc so với chủ đề chính.

Khi bạn nói chuyện với khách hàng bằng 3 chỉ số này thay vì chỉ bàn chuyện "màu này đẹp hay chưa", vị thế làm việc của bạn sẽ khác hẳn.

(Mình có để sẵn bảng theo dõi 12 video kèm các mốc chỉ số tham chiếu trong bộ Starter Kit v1 ở bio, bạn nào cần cứ bấm vào lấy về dùng nhé).
```

---

## PHẦN 2: NHÓM PILLAR 2 — KỸ THUẬT NHẤN MOTION & QUY TRÌNH LÀM VIỆC VỚI KHÁCH HÀNG (`C036` – `C039`)

---

### VIDEO 5: `C036` — Cách chọn một từ để nhấn bằng motion

#### 1. Thông tin định danh
- **Mã nội dung:** `C036`
- **Pillar & Tuyến:** P2 (Edit & Storytelling) — `EDIT05` (Motion & Text có chủ đích)
- **Format:** Tutorial (So sánh A/B trên After Effects / Premiere)
- **Tệp khán giả:** Video Editor / Creator muốn làm chữ chuyển động (Motion Typography) gọn và sang
- **Giai đoạn Funnel:** Nhận biết (Awareness)
- **CTA:** Theo dõi series
- **Offer đích:** Không bán
- **Bằng chứng sử dụng:** Project demo trên After Effects/Premiere so sánh cùng 1 câu nói: Bản A làm hiệu ứng nảy màu cho 5 chữ liên tiếp vs Bản B chỉ nhấn đúng 1 từ khóa mang thông điệp chính.
- **Core Claim:** Khi mọi chữ trên màn hình đều phóng to và đổi màu thì không còn chữ nào nổi bật; chỉ chọn đúng 1 từ khóa đại diện cho kết luận của câu để đặt chuyển động.

#### 2. Bảng kịch bản sản xuất chi tiết (36 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác Timeline (Visual) | Text trên màn hình (On-screen Text) | Lời thoại (Voiceover / A-roll) & SFX |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | Split-screen trái/phải chạy cùng một câu nói 4 giây: Bên trái chữ nhảy liên tục 5 màu + 5 tiếng whoosh/pop; Bên phải chữ tĩnh gọn gàng, chỉ có đúng cụm từ **"Giữ chân"** phóng nhẹ và đổi màu vàng. | Khi chữ nào cũng nhảy, người xem sẽ **không nhớ chữ nào** | **[SFX: Tiếng pop dồn dập rồi ngắt phựt]** Khi bạn làm hiệu ứng chuyển động cho mọi từ trong câu, người xem sẽ không kịp nhớ từ nào cả. |
| `00:03 – 00:10` | **2. PROOF / TENSION** | Dừng hình ở Bản A (bên trái): trên màn hình có 4 từ khác nhau cùng được tô màu đỏ, vàng, xanh và phóng to lệch dòng. | Nhấn 4–5 chữ cùng lúc làm mắt người xem **bị loạn** | Đây là thói quen rất hay gặp khi mới tập làm motion text: thấy câu có 8 chữ thì tô màu và gán keyframe nảy cho cả 4 chữ, làm mắt người xem bị mỏi chỉ sau 5 giây. |
| `00:10 – 00:19` | **3. BODY (Quy tắc 1)** | Chuyển sang giao diện timeline của Bản B. Thành gạch chân câu thoại trong bảng Transcript: *"Đừng thêm hiệu ứng nếu nó không giúp giữ chân người xem."* Chỉ khoanh tròn chữ **"giữ chân"**. | Bước 1: Che hết câu lại, tìm đúng **1 từ khóa** mang kết luận | Cách mình chọn từ để đặt motion chỉ gồm hai bước. **[SFX: Click]** Một: Đọc cả câu thoại và tự hỏi nếu xóa hết chỉ giữ lại một cụm từ quan trọng nhất thì đó là từ nào. Ở câu này, đó là cụm từ "giữ chân". |
| `00:19 – 00:29` | **3. BODY (Quy tắc 2)** | Mở bảng Keyframe Scale & Color của cụm từ **"Giữ chân"**: các chữ còn lại để font thường màu trắng cỡ 55, riêng từ **"Giữ chân"** để Bold màu vàng cỡ 68 kèm 2 keyframe trượt nhẹ theo nhịp giọng nhấn. | Bước 2: Giữ tĩnh các chữ phụ — Chỉ đặt keyframe vào **từ khóa chính** | Hai: Giữ toàn bộ các chữ còn lại đứng yên với màu trắng đồng nhất. **[ngừng 0.5s]** Mình chỉ đặt keyframe phóng nhẹ và một tiếng động nhỏ đúng vào khoảnh khắc giọng nói nhấn chữ "giữ chân". |
| `00:29 – 00:36` | **4. CLOSE & CTA** | Chạy lại mượt mà 3 giây Bản B hoàn chỉnh, sau đó chuyển về A-roll Thành chốt câu kết. | Theo dõi kênh để xem tiếp series **Dựng Có Chủ Đích** | Giảm bớt 80% keyframe thừa không chỉ giúp bạn dựng nhanh hơn mà còn làm khung hình có điểm nhìn rõ ràng. **[ngừng 0.5s]** Bạn theo dõi kênh để xem tiếp các bài bóc tách kỹ thuật dựng có chủ đích nhé. |

#### 3. Shot List chuẩn bị
- **A-roll:** Thành ngồi trước màn hình After Effects / Premiere Pro.
- **Screen Record:** Project demo so sánh Bản A (Over-edited text) và Bản B (Minimalist intentional motion text), zoom cận vào Graph Editor / Keyframe của từ khóa duy nhất.
- **Asset đồ họa:** Khung so sánh Trái/Phải (`Nhấn 5 từ` vs `Nhấn 1 từ`).

#### 4. Caption TikTok & Facebook Reels
- **Caption TikTok:**
  Quy tắc chọn từ khóa khi làm Motion Text: Nếu chữ nào trên màn hình cũng phóng to và đổi màu, nghĩa là không có chữ nào được nhấn cả.
  Chỉ chọn 1 cụm từ mang kết luận trong câu để đặt keyframe và hiệu ứng âm thanh.
  Theo dõi kênh để xem tiếp series bóc tách kỹ thuật dựng có chủ đích nhé.
  `#dungcochudich #videoediting #aftereffects #premierepro`
- **Caption Facebook Reels:**
  Lúc mới học After Effects và Premiere, mình từng nghĩ đặt càng nhiều keyframe cho chữ nhảy liên tục thì video trông càng "đắt tiền". Nhưng khi xem lại bằng con mắt của người lướt điện thoại, việc tô màu 4–5 chữ trên cùng một khung hình chỉ làm người xem mỏi mắt và quên mất ý chính. Đây là quy tắc 2 bước giúp mình chọn đúng 1 từ duy nhất để nhấn trên mỗi câu thoại.

#### 5. Bài đăng Facebook cá nhân (`crosspost`)
```text
Có một nghịch lý khi dựng phụ đề và chữ chuyển động (motion text) cho video ngắn: Bạn càng cố làm nổi bật nhiều chữ trong cùng một câu, người xem càng không đọng lại được ý nào.

Hồi mới tập làm motion trên Premiere và After Effects, mình cũng từng mắc lỗi cứ cách 2 chữ lại đổi một màu (chữ màu vàng, chữ màu xanh lá, chữ phóng to, chữ xoay nghiêng) kèm tiếng "pop, whoosh" dồn dập. Kết quả là mình mất gấp đôi thời gian gán keyframe, còn người xem thì bị phân tán khỏi nội dung chính của lời nói.

Hiện tại, trước khi đặt bất kỳ keyframe chuyển động nào cho chữ trên màn hình, mình luôn áp dụng 3 quy tắc gọn này:

1. Quy tắc "1 Khung hình = 1 Điểm nhìn": Trong một câu thoại dài 8–12 từ, mình luôn tự hỏi: "Nếu người xem đang tắt tiếng và chỉ lướt mắt qua màn hình trong 1 giây, đâu là cụm 2–3 chữ họ bắt buộc phải đọc được?". Chỉ cụm từ đó mới được đổi màu nhấn hoặc tăng kích thước.
2. Để phần chữ phụ làm nền tĩnh: Muốn từ khóa chính nổi lên, các chữ xung quanh phải chịu lùi lại. Mình giữ toàn bộ chữ phụ ở cùng một cỡ chữ, màu trắng (hoặc xám nhạt) và không gắn hiệu ứng nảy.
3. Đặt chuyển động khớp với trọng âm giọng nói: Thay vì cho chữ bay vào một cách ngẫu nhiên, mình nhìn sóng âm (waveform) của câu thoại và đặt keyframe đúng vào nhịp người nói nhấn giọng.

Bớt đi những chuyển động trang trí thừa thãi vừa giúp editor tiết kiệm hàng giờ đồng hồ mỗi tuần, vừa trả lại sự tập trung cho thông điệp của video. Đó là cách mình dựng có chủ đích.
```

---

### VIDEO 6: `C037` — Quy trình của tôi từ brief đến bản dựng

#### 1. Thông tin định danh
- **Mã nội dung:** `C037`
- **Pillar & Tuyến:** P2 (Edit & Storytelling) — `EDIT06` (Quy trình làm việc chuyên nghiệp)
- **Format:** BTS (Behind The Scenes / Quy trình làm việc thực tế)
- **Tệp khán giả:** Khách hàng tiềm năng (Chủ thương hiệu cá nhân, Chủ shop, Đội marketing cần thuê dựng)
- **Giai đoạn Funnel:** Tin cậy (Trust)
- **CTA:** Nhắn EDIT
- **Offer đích:** Dịch vụ Edit/Media
- **Bằng chứng sử dụng:** Màn hình quy trình 5 bước thực tế trên Notion/Google Drive + Timeline Premiere có đánh dấu Marker các cổng duyệt (Checkpoint).
- **Core Claim:** Một quy trình dựng 5 bước có điểm chốt duyệt ngay từ phần khung kịch bản và nháp thô giúp khách hàng không bao giờ rơi vào cảnh "dựng xong hết mới phát hiện lệch ý".

#### 2. Bảng kịch bản sản xuất chi tiết (41 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác Timeline (Visual) | Text trên màn hình (On-screen Text) | Lời thoại (Voiceover / A-roll) & SFX |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | A-roll Thành mở thư mục dự án của khách hàng trên màn hình (được chia sẵn từ `01_Brief` đến `05_Final_Export`) kèm sơ đồ 5 bước gọn gàng. | Quy trình **5 bước** giúp video đúng ý ngay từ bản dựng đầu tiên | **[SFX: Tiếng mở folder gọn gàng]** Lý do nhiều khách hàng ngại thuê editor bên ngoài là sợ cảnh chờ 3 ngày xong nhận về một bản dựng lệch hẳn mục tiêu. |
| `00:03 – 00:10` | **2. PROOF / TENSION** | Chiếu cảnh một đoạn tin nhắn sửa bài lòng vòng (mô phỏng lại lỗi phổ biến: dựng xong cả hiệu ứng rồi mới phải cắt lại từ đầu vì sai thông điệp). | Dựng xong hết mới sửa thông điệp sẽ làm **mất gấp đôi thời gian** | Vấn đề thường không phải do kỹ năng cắt ghép, mà do thiếu các điểm chốt ý trước khi editor bắt tay vào làm hiệu ứng chi tiết. |
| `00:10 – 00:20` | **3. BODY (Bước 1 & 2)** | Quay màn hình Bước 1 (Bảng Brief 1 trang chốt Mục tiêu, Tệp xem, CTA) và Bước 2 (Bản nháp thô A-roll cắt bỏ câu thừa trên Premiere để chốt mạch nội dung). | Bước 1 & 2: Chốt **mục tiêu** và duyệt **mạch nội dung thô** trước | Để tránh việc đó, mình làm việc theo đúng 5 bước có 2 điểm kiểm tra. **[SFX: Pop]** Bước một: Chốt mục tiêu và một hành động duy nhất của video. Bước hai: Dựng nháp phần lời nói để khách duyệt đúng mạch thông điệp trước. |
| `00:20 – 00:31` | **3. BODY (Bước 3, 4 & 5)** | Chuyển sang Bước 3 (Dùng AI tạo asset bổ trợ & đặt B-roll), Bước 4 (Đặt text nhấn từ khóa & chỉnh âm thanh), và Bước 5 (Kiểm duyệt 10 điểm QA trước khi gửi link). | Bước 3, 4 & 5: Phủ **hình ảnh minh họa**, nhấn từ khóa và **kiểm duyệt QA** | Khi mạch nói đã chuẩn, mình mới sang bước ba: phủ cảnh minh họa và dùng AI tạo thêm góc hình còn thiếu. **[ngừng 0.5s]** Bước bốn là đặt chữ nhấn từ khóa, và bước năm là rà soát qua checklist 10 điểm trước khi bàn giao. |
| `00:31 – 00:41` | **4. CLOSE & CTA** | A-roll Thành nhìn thẳng ống kính, bên cạnh hiện thẻ thông tin liên hệ: `Nhắn "EDIT" + Mục tiêu video của bạn`. | Nhắn chữ **EDIT** kèm mục tiêu video để mình gửi quy trình chi tiết | Nhờ chốt khung ngay từ đầu, trung bình mỗi video chỉ cần tối đa một vòng tinh chỉnh nhẹ. **[ngừng 0.5s]** Nếu bạn có sẵn footage và cần một quy trình dựng rõ ràng như vậy, nhắn chữ "EDIT" kèm mục tiêu video cho mình nhé. |

#### 3. Shot List chuẩn bị
- **A-roll:** Thành ngồi tại góc làm việc chỉn chu, màn hình hiển thị sơ đồ 5 bước làm việc.
- **Screen Record:** Quay thư mục dự án chuẩn hóa (`01_Brief_MucTieu`, `02_RoughCut_MachNoiDung`, `03_Broll_AI_Asset`, `04_Motion_Sound`, `05_Final_QA`) và bảng theo dõi tiến độ.
- **Asset đồ họa:** Sơ đồ 5 bước có đánh dấu 2 Checkpoint (`Checkpoint 1: Duyệt mạch chữ/A-roll`, `Checkpoint 2: Duyệt bản hoàn thiện`).

#### 4. Caption TikTok & Facebook Reels
- **Caption TikTok:**
  Làm sao để khách hàng và editor không mất thời gian sửa đi sửa lại 4–5 vòng cho một video ngắn?
  Đây là quy trình 5 bước của mình: Chốt mục tiêu & CTA → Duyệt mạch nói thô (Rough Cut) → Bổ sung B-roll & AI asset → Nhấn chữ có chủ đích → Kiểm duyệt 10 điểm QA.
  Nếu bạn có sẵn footage và cần video lên đúng thông điệp bán hàng, nhắn chữ "EDIT" cho mình nhé.
  `#dungcochudich #videoeditor #dichvueditvideo #marketingvideo`
- **Caption Facebook Reels:**
  Nỗi sợ lớn nhất của cả người thuê dựng lẫn editor là: Editor thức đêm làm xong hết hiệu ứng chữ nghĩa, gửi qua thì khách bảo "Đoạn đầu này không đúng ý anh muốn nhấn rồi em ơi", thế là phải đập đi làm lại từ đầu. Mình giải quyết triệt để chuyện này bằng quy trình 5 bước với 2 điểm chốt duyệt rất gọn. Bạn nào đang tìm người đồng hành hậu kỳ video cho kênh cá nhân hoặc shop có thể nhắn chữ "EDIT" để mình trao đổi cụ thể nhé.

#### 5. Bài đăng Facebook cá nhân (`crosspost`)
```text
Khi một khách hàng nói với mình: "Trước đây anh thuê dựng bên ngoài cực quá, gửi file xong im bặt 3 ngày, lúc nhận về thì lệch hẳn ý muốn nói nên sửa đi sửa lại mất cả tuần", mình hiểu ngay vấn đề nằm ở quy trình giao nhận chứ không hẳn ở tay nghề kỹ thuật.

Nếu editor nhận một cục Google Drive gồm 15 file quay thô rồi nhảy vào cắt hiệu ứng ngay mà không thống nhất trước cái khung, khả năng phải tháo timeline ra làm lại là rất cao.

Để tiết kiệm thời gian cho cả hai bên, mọi video mình nhận dựng đều đi qua đúng 5 bước với 2 điểm chốt (Checkpoint) rõ ràng:

1. Chốt đề bài trên 1 trang (Brief): Trước khi mở phần mềm, hai bên thống nhất đúng 3 gạch đầu dòng: Ai là người xem? Xem xong họ cần nhớ 1 câu kết luận gì? Và cuối video dẫn họ đi đâu?
2. Chốt bản dựng thô (Rough Cut — Checkpoint 1): Mình cắt gọn phần lời nói (A-roll), lọc bỏ câu vấp, sắp xếp lại thứ tự câu mở đầu (Hook) để khách xem lướt trong 2 phút. Khi khách gật đầu "Đúng mạch ý anh muốn nói rồi", mình mới đi tiếp.
3. Đắp hình ảnh chứng minh & AI Asset: Những đoạn cần hình minh họa mà lúc quay bị thiếu, mình kết hợp kho B-roll và tạo thêm visual bằng AI (sau đó chỉnh lại màu sắc cho khớp với cảnh thật).
4. Đặt chữ nhấn từ khóa & Cân chỉnh âm thanh: Chỉ nhấn đúng từ khóa quan trọng trên từng khung hình và xử lý giọng nói rõ, sạch.
5. Tự kiểm duyệt 10 điểm (QA — Checkpoint 2): Kiểm tra vùng an toàn của chữ trên TikTok/Reels, độ khớp của CTA rồi mới xuất file bàn giao.

Quy trình rõ ràng giúp khách hàng luôn nắm được tiến độ, còn mình tập trung được 100% năng lượng vào chất lượng bản dựng.

Nếu bạn đang có sẵn footage quay cho thương hiệu cá nhân hoặc sản phẩm nhưng chưa có quy trình hậu kỳ gọn như vậy, nhắn cho mình chữ "EDIT" kèm mục tiêu kênh của bạn để mình trao đổi nhé.
```

---

### VIDEO 7: `C038` — Vì sao editor cần hỏi mục tiêu trước khi nhận file?

#### 1. Thông tin định danh
- **Mã nội dung:** `C038`
- **Pillar & Tuyến:** P2 (Edit & Storytelling) — `EDIT06` (Quy trình làm việc chuyên nghiệp)
- **Format:** Talking head + Minh họa Mẫu Brief 1 Trang
- **Tệp khán giả:** Khách hàng thuê dựng / Creator làm việc với Editor
- **Giai đoạn Funnel:** Cân nhắc (Consideration)
- **CTA:** Nhận mẫu brief
- **Offer đích:** Starter Kit (`STARTER_KIT_V1_DUNG_CO_CHU_DICH`)
- **Bằng chứng sử dụng:** Mẫu Brief 1 trang thực tế của Thành so sánh 2 cách dựng từ cùng 1 file quay gốc (1 bản dựng để tăng Lưu bài vs 1 bản dựng để thu hút Nhắn tin tư vấn).
- **Core Claim:** Cùng một file quay gốc nhưng nếu mục tiêu là lấy lượt lưu bài hay lấy tin nhắn mua hàng thì câu được chọn mở đầu và nhịp cắt 5 giây cuối sẽ hoàn toàn khác nhau.

#### 2. Bảng kịch bản sản xuất chi tiết (38 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác Timeline (Visual) | Text trên màn hình (On-screen Text) | Lời thoại (Voiceover / A-roll) & SFX |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | A-roll Thành giơ tờ Mẫu Brief 1 Trang lên trước màn hình có 2 timeline dựng khác nhau từ cùng 1 file gốc. | Vì sao mình luôn hỏi **3 câu này** trước khi mở file của khách? | **[SFX: Tiếng giấy lật nhẹ]** Trước khi tải file quay của khách về máy, mình luôn hỏi trước ba câu hỏi về mục tiêu. |
| `00:03 – 00:10` | **2. PROOF / TENSION** | Chiếu màn hình Premiere có 1 file quay gốc dài 3 phút, tách làm 2 Sequence: `Sequence A (Mục tiêu: Lưu bài)` và `Sequence B (Mục tiêu: Nhắn tin hỏi dịch vụ)`. | Cùng một file quay — Khác mục tiêu là **khác hẳn cách cắt** | Nhiều bạn nghĩ gửi file cho editor thì cứ cắt hết câu thừa rồi chèn chữ là xong. **[ngừng 0.5s]** Thực tế, cùng một file quay gốc nhưng khác mục tiêu thì cấu trúc cắt sẽ khác hẳn nhau. |
| `00:10 – 00:17` | **3. BODY (Câu hỏi 1)** | Phóng to câu hỏi số 1 trên Mẫu Brief: `1. Người xem chính của video này là ai?` kèm ví dụ chọn câu Hook tương ứng. | Câu hỏi 1: Video này đang nói chuyện với **tệp người xem nào**? | Ba câu mình luôn hỏi là: **[SFX: Pop]** Một: Người xem cụ thể là ai? Biết rõ tệp người xem giúp mình chọn đúng câu mở đầu từ file quay thô để giữ họ lại ở 3 giây đầu. |
| `00:17 – 00:25` | **3. BODY (Câu hỏi 2)** | Phóng to câu hỏi số 2: `2. Xem xong họ cần hiểu đúng 1 ý gì?` kèm cảnh gạt bỏ 2 đoạn lan man trên timeline. | Câu hỏi 2: Một **kết luận duy nhất** cần đọng lại là gì? | Hai: Xem xong 30 giây, họ cần nhớ đúng một ý gì? **[ngừng 0.5s]** Câu trả lời này là căn cứ để mình mạnh dạn cắt bỏ những đoạn nói thêm rất hay nhưng làm loãng chủ đề. |
| `00:25 – 00:32` | **3. BODY (Câu hỏi 3)** | Phóng to câu hỏi số 3: `3. Hành động tiếp theo (CTA) là gì?` kèm cảnh thiết kế màn hình kết. | Câu hỏi 3: Xem xong muốn họ **làm hành động gì** tiếp theo? | Ba: Hành động tiếp theo là lưu bài, bấm vào bio hay nhắn tin? Nếu cần lưu bài, mình sẽ làm bảng tóm tắt ở cuối; nếu cần nhắn tin, mình đẩy bằng chứng kết quả lên sát câu kết. |
| `00:32 – 00:38` | **4. CLOSE & CTA** | A-roll Thành chỉ vào trang `Mẫu Brief & Shot List 1 Trang` trong bộ Starter Kit. | Lấy **Mẫu Brief 1 trang** trong Starter Kit ở bio | Ba câu hỏi đó chỉ mất 2 phút để điền nhưng quyết định hiệu quả của cả video. **[ngừng 0.5s]** Mẫu brief một trang này mình để sẵn trong Starter Kit ở bio, bạn vào lấy về dùng nhé. |

#### 3. Shot List chuẩn bị
- **A-roll:** Thành ngồi bàn làm việc, cầm bản in (hoặc iPad/màn hình) hiển thị `Mẫu Brief & Shot List 1 Trang`.
- **Screen Record:** Quay 2 Sequence trên Premiere dùng chung 1 file A-roll gốc nhưng chọn đoạn mở đầu và màn hình kết khác nhau tùy theo mục tiêu.
- **Asset đồ họa:** 3 pop-up câu hỏi cốt lõi (`1. Ai xem?` — `2. Nhớ 1 ý gì?` — `3. Làm gì tiếp theo?`).

#### 4. Caption TikTok & Facebook Reels
- **Caption TikTok:**
  Cùng một file quay gốc 3 phút, nhưng nếu mục tiêu là lấy lượt Lưu bài hay lấy Tin nhắn khách hàng thì cách chọn câu mở đầu và dựng 5 giây cuối sẽ hoàn toàn khác nhau.
  Đó là lý do mình luôn hỏi 3 câu này trước khi nhận file.
  Mẫu Brief & Shot List 1 trang mình để sẵn trong Starter Kit ở bio cho cả Creator và người thuê dựng nhé.
  `#dungcochudich #videoediting #marketingvideo #contentcreator`
- **Caption Facebook Reels:**
  Nếu bạn gửi file quay thô cho editor và chỉ nhắn một câu "Em cắt ghép làm sao cho mượt giúp anh nhé", editor sẽ chỉ biết cắt theo cảm tính. Chỉ cần làm rõ 3 câu hỏi ngắn trước khi dựng: Ai xem? Nhớ 1 ý gì? Hành động tiếp theo là gì?, bản dựng trả về sẽ bám sát mục tiêu kinh doanh của bạn hơn rất nhiều. Mình gửi tặng mẫu Brief 1 trang này trong bộ Starter Kit ở bio nhé.

#### 5. Bài đăng Facebook cá nhân (`crosspost`)
```text
Khi nhận một file quay dài 3–4 phút từ khách hàng để dựng thành một video ngắn 35 giây, có ít nhất 3 cách cắt hoàn toàn khác nhau từ cùng một nguồn nguyên liệu đó.

Nếu không hỏi rõ mục tiêu trước khi mở Premiere, người dựng rất dễ chọn nhầm đoạn mở đầu hoặc cắt mất chính câu nói có khả năng thuyết phục khách mua hàng. Vì vậy, trước khi bắt tay vào bất kỳ dự án nào (hay trước khi tự dựng video cho chính kênh của mình), mình luôn trả lời 3 câu hỏi trên đúng 1 trang giấy:

1. Người xem mục tiêu của video này là ai?
Cùng nói về chuyện "làm video bán hàng", nếu nói với bạn chủ shop tự quay bằng điện thoại thì 3 giây đầu phải mở bằng cảnh thực tế ngoài cửa hàng. Nhưng nếu nói với chủ doanh nghiệp muốn thuê đội ngũ hậu kỳ, 3 giây đầu phải mở bằng bài toán quy trình và chi phí thời gian.

2. Sau khi xem hết 35 giây, họ cần nhớ đúng 1 câu kết luận gì?
Khi khách hàng nói trước ống kính, họ thường chia sẻ rất tâm huyết và vô tình nói sang cả 3–4 chủ đề nhỏ. Nắm rõ "1 câu kết luận duy nhất" giúp mình biết chính xác câu nào phải giữ lại làm trục xương sống, và câu nào nên tách ra thành một video riêng cho tuần sau.

3. Hành động tiếp theo (CTA) sau khi xem xong là gì?
- Nếu mục tiêu là tăng lượt Lưu (Save): Mình sẽ thiết kế một khung hình tổng kết dạng danh sách (Checklist) ở 4 giây cuối để người xem muốn lưu lại tra cứu.
- Nếu mục tiêu là thu hút Tin nhắn tư vấn (Lead): Mình sẽ đặt cảnh bằng chứng kết quả (Before/After) ngay trước câu mời nhắn tin.

Mình đã trình bày sẵn "Mẫu Brief & Shot List 1 Trang" này trong bộ tài liệu Starter Kit v1. Bạn nào đang tự sản xuất video hoặc đang làm việc cùng editor có thể lấy về ở link bio của mình để dùng ngay cho buổi quay tới.
```

---

### VIDEO 8: `C039` — Một vòng feedback tốt cần những gì?

#### 1. Thông tin định danh
- **Mã nội dung:** `C039`
- **Pillar & Tuyến:** P2 (Edit & Storytelling) — `EDIT06` (Quy trình làm việc chuyên nghiệp)
- **Format:** Tutorial / So sánh Before & After vòng sửa bài
- **Tệp khán giả:** Khách hàng thuê dựng / Quản lý nội dung / Editor làm việc với khách
- **Giai đoạn Funnel:** Tin cậy (Trust)
- **CTA:** Nhắn EDIT
- **Offer đích:** Dịch vụ Edit/Media
- **Bằng chứng sử dụng:** Ví dụ so sánh thực tế giữa tin nhắn feedback cảm tính ("Làm cho nó cháy hơn đi em") và bảng feedback có Timestamp + Mục tiêu thông điệp.
- **Core Claim:** Một phản hồi sửa bài hiệu quả không mô tả bằng tính từ cảm tính mà chỉ rõ mốc giây (timestamp), vấn đề người xem đang gặp tại mốc đó và mục tiêu cần đạt.

#### 2. Bảng kịch bản sản xuất chi tiết (39 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác Timeline (Visual) | Text trên màn hình (On-screen Text) | Lời thoại (Voiceover / A-roll) & SFX |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | Đặt cạnh nhau 2 khung phản hồi: Bên trái là tin nhắn *"Làm cho đoạn đầu nó cháy hơn đi em"*; Bên phải là ghi chú *"00:02 — Đẩy cảnh kết quả lên trước để giữ chân người xem"*. | Cách biến câu *"Làm cho cháy hơn"* thành bản sửa đúng ý trong **1 lần** | **[SFX: Tiếng tin nhắn đến]** Khi nhận được câu góp ý "Làm cho đoạn đầu cháy hơn đi em", cả khách hàng lẫn editor đều rất dễ tốn thêm ba ngày đoán ý nhau. |
| `00:03 – 00:10` | **2. PROOF / TENSION** | Chiếu cảnh editor thêm lửa, hiệu ứng rung lắc (Shake) và nhạc dồn dập vào 3 giây đầu nhưng khách xem xong lại bảo: *"Ý anh không phải vậy, nhìn rối quá"*. | Tính từ cảm tính khiến mỗi người hiểu theo **một kiểu khác nhau** | Lý do là chữ "cháy hơn" hay "mượt hơn" là tính từ cảm tính. **[ngừng 0.5s]** Editor hiểu là thêm hiệu ứng chuyển cảnh, trong khi khách hàng thực ra đang muốn thông điệp mở đầu mạnh hơn. |
| `00:10 – 00:18` | **3. BODY (Thành phần 1)** | Mở bảng hướng dẫn ghi chú sửa bài của Thành gửi cho khách: Cột 1 là `Mốc thời gian (Timestamp)` — ví dụ `00:00 – 00:04`. | 1. Ghi rõ **mốc giây** cần điều chỉnh trên video | Để mỗi video chỉ cần đúng một vòng tinh chỉnh, mình luôn hướng dẫn khách góp ý theo công thức ba phần. **[SFX: Click]** Một: Ghi rõ mốc giây cụ thể cần sửa, ví dụ từ giây 00 đến giây 04. |
| `00:18 – 00:25` | **3. BODY (Thành phần 2)** | Cột 2 là `Vấn đề đối với người xem` — ví dụ *"3 giây đầu đang giới thiệu tên sản phẩm hơi lâu, khách dễ lướt qua"*. | 2. Nêu rõ **cảm nhận của người xem** tại mốc giây đó | Hai: Nêu vấn đề dưới góc nhìn của người xem, chẳng hạn như "Ba giây đầu đang nói lý thuyết hơi lâu, sợ khách lướt qua mất". |
| `00:25 – 00:32` | **3. BODY (Thành phần 3)** | Cột 3 là `Hướng xử lý trên Timeline`: Thành kéo cảnh kết quả từ giây 18 lên giây 01 và xuất lại bản so sánh ngay lập tức. | 3. Chốt **mục tiêu thông điệp** để editor chọn kỹ thuật dựng | Ba: Khi biết mục tiêu là giữ chân bằng kết quả thực tế, mình sẽ chủ động kéo cảnh thành phẩm từ giây 18 lên đầu video thay vì nhồi thêm hiệu ứng. |
| `00:32 – 00:39` | **4. CLOSE & CTA** | A-roll Thành mỉm cười, màn hình hiện tóm tắt công thức `Mốc giây + Vấn đề người xem + Mục tiêu` và lời mời nhắn `EDIT`. | Nhắn chữ **EDIT** nếu bạn cần người dựng hiểu rõ mục tiêu thông điệp | Khi khách hàng nói rõ mục tiêu còn editor giải quyết bằng kỹ thuật dựng, việc hợp tác sẽ rất nhẹ nhàng. **[ngừng 0.5s]** Nếu bạn đang tìm một người dựng làm việc theo cách đó, nhắn chữ "EDIT" cho mình nhé. |

#### 3. Shot List chuẩn bị
- **A-roll:** Thành ngồi tại bàn dựng, giải thích rõ ràng với thái độ tôn trọng và cầu thị với khách hàng.
- **Screen Record:** Giao diện bảng góp ý 3 cột (`Mốc giây` | `Vấn đề người xem` | `Phương án dựng lại`) đặt cạnh timeline Premiere trước và sau khi sửa.
- **Asset đồ họa:** Card so sánh `Feedback cảm tính` vs `Feedback có chủ đích`.

#### 4. Caption TikTok & Facebook Reels
- **Caption TikTok:**
  Làm sao để biến câu "Em làm cho đoạn đầu nó cháy hơn đi" thành một bản sửa đúng ý ngay trong lần đầu tiên?
  Công thức 1 vòng feedback gọn cho cả khách hàng và editor: Mốc giây cụ thể + Vấn đề dưới góc nhìn người xem + Mục tiêu thông điệp.
  Nếu bạn cần một editor hiểu mục tiêu marketing để phối hợp nhanh gọn, nhắn chữ "EDIT" cho mình nhé.
  `#dungcochudich #videoeditor #marketingvideo #freelanceeditor`
- **Caption Facebook Reels:**
  Chuyện khách hàng nhắn "Làm cho video nhìn sang hơn / cháy hơn giúp anh" là tình huống rất quen thuộc. Thực ra khách hàng không có nghĩa vụ phải biết thuật ngữ kỹ thuật của Premiere hay After Effects; việc của một editor có tư duy marketing là đặt câu hỏi để dịch mong muốn đó thành quyết định chọn cảnh và cắt nhịp cụ thể. Đây là cách mình thiết kế vòng phản hồi để hai bên chỉ mất 1 lần chỉnh là chốt được file cuối.

#### 5. Bài đăng Facebook cá nhân (`crosspost`)
```text
Trong nghề dựng video, câu góp ý dễ làm cả khách hàng lẫn editor mệt mỏi nhất thường là: "Em sửa sao cho đoạn đầu nhìn nó cháy hơn / cuốn hơn giúp anh nhé."

Nhiều bạn editor khi nghe câu này sẽ lập tức mở kho preset, chèn thêm hiệu ứng rung màn hình, tia chớp, đổi font chữ thật to và tăng âm lượng nhạc nền. Nhưng khi xuất file gửi lại, khách vẫn lắc đầu: "Không phải kiểu này em ơi, nhìn rối mắt quá."

Thực tế, khách hàng là người hiểu sản phẩm và khách mua hàng của họ, chứ họ không làm nghề dựng để nói bằng ngôn ngữ keyframe hay timeline. Khi họ nói "chưa đủ cuốn", 90% trường hợp là họ đang cảm thấy thông điệp mở đầu chưa đủ sức giữ chân người mua.

Vì vậy, khi làm việc cùng khách hàng ở bước duyệt bài, mình luôn chủ động chuyển các góp ý cảm tính về một khung 3 câu hỏi rất gọn:

1. Mốc thời gian cụ thể nào đang làm anh/chị lăn tăn? (Ví dụ: Giây 00:00 đến 00:05).
2. Ở mốc giây đó, anh/chị sợ người xem sẽ phản ứng thế nào? (Ví dụ: "Anh sợ mở đầu bằng cảnh nói chuyện tại bàn lâu quá, khách chưa kịp thấy chất liệu áo thật đã lướt đi mất").
3. Thay đổi trên bản dựng: Khi hiểu đúng nỗi lo đó, giải pháp của mình không phải là thêm hiệu ứng "cháy nổ", mà là cắt lấy 2 giây cảnh zoom cận đường may chiếc áo ở giữa video đắp thẳng lên 2 giây đầu tiên (J-cut).

Chỉ mất đúng 15 phút chỉnh lại cấu trúc cảnh là khách gật đầu duyệt ngay. Khi editor biết lắng nghe mục tiêu marketing đằng sau lời góp ý của khách, quá trình làm việc sẽ tiết kiệm được rất nhiều thời gian cho cả hai phía.

Bạn nào đang có sẵn nguồn quay và muốn tìm một người dựng phối hợp theo cách rõ ràng như vậy thì nhắn chữ "EDIT" cho mình nhé.
```

---

## PHẦN 3: NHÓM PILLAR 3 — SO SÁNH MODEL, WORKFLOW NHÂN BẢN & LỘ TRÌNH HỌC AI (`C052` – `C054`)

---

### VIDEO 9: `C052` — So sánh hai model bằng cùng một prompt

#### 1. Thông tin định danh
- **Mã nội dung:** `C052`
- **Pillar & Tuyến:** P3 (AI trong workflow editor) — `AI05` (Đánh giá & Chọn công cụ thực tế)
- **Format:** Comparison (So sánh trực diện 2 model trên cùng 1 Prompt & Đưa vào Timeline)
- **Tệp khán giả:** Người học AI / Editor ứng dụng AI tạo B-roll
- **Giai đoạn Funnel:** Cân nhắc (Consideration)
- **CTA:** Dùng thử
- **Offer đích:** Xưởng Media (Link trải nghiệm công cụ ở bio — có ghi chú affiliate minh bạch)
- **Bằng chứng sử dụng:** 1 câu Prompt cố định (chủ đề B-roll sản phẩm đặt trên bàn gỗ ánh nắng chiều) chạy song song trên 2 model tạo ảnh/video trong giao diện **Xưởng Media**, sau đó thả vào timeline Premiere để test độ ăn nhập.
- **Core Claim:** Đánh giá model AI cho công việc dựng video không chấm điểm bằng độ lung linh khi đứng lẻ, mà chấm bằng 3 tiêu chí: độ bám sát mô tả góc máy, độ thật của ánh sáng và khả năng ghép khớp màu với cảnh quay thật trên timeline.

#### 2. Bảng kịch bản sản xuất chi tiết (40 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác Timeline (Visual) | Text trên màn hình (On-screen Text) | Lời thoại (Voiceover / A-roll) & SFX |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | Split-screen trái/phải hiển thị 2 kết quả video B-roll chạy song song từ cùng 1 dòng Prompt hiển thị ở giữa màn hình. | Cùng một câu prompt — Model nào đưa vào **bản dựng thật** tốt hơn? | **[SFX: Tiếng click đúp]** Cùng một câu prompt tạo cảnh B-roll trên Xưởng Media, nhưng chỉ một trong hai kết quả này dùng được vào timeline thật. |
| `00:03 – 00:10` | **2. PROOF / TENSION** | Chiếu dòng Prompt cố định: *"Cận cảnh góc 45 độ ly cà phê đặt cạnh laptop trên bàn gỗ, nắng chiều chiếu xiên qua rèm, chuyển động khói nhẹ"*. | Đẹp khi đứng một mình chưa chắc đã **ghép khớp** được với cảnh quay thật | Khi chọn model AI để hỗ trợ dựng video, mình không tìm bức hình trông ảo diệu nhất, mà chấm điểm theo ba tiêu chí thực tế của editor. |
| `00:10 – 00:18` | **3. BODY (Tiêu chí 1)** | So sánh góc máy của Model A (tự ý đổi sang góc chính diện, mất chiếc laptop) và Model B (giữ đúng góc 45 độ và bố cục có laptop bên trái). | Tiêu chí 1: Độ bám sát **góc máy và bố cục** trong prompt | **[SFX: Pop]** Một là độ bám sát góc máy. Ở đây mình cần góc 45 độ có khoảng trống bên phải để chèn chữ. Model A tự ý đẩy vật thể ra giữa khung hình, còn Model B giữ đúng bố cục mình yêu cầu. |
| `00:18 – 00:25` | **3. BODY (Tiêu chí 2)** | Phóng to 200% vùng bóng đổ và chi tiết bề mặt gỗ của hai kết quả. Model A bị bệt màu vùng tối, Model B giữ được vân gỗ và hướng nắng xiên tự nhiên. | Tiêu chí 2: Hướng **ánh sáng** và chi tiết bề mặt vật liệu | Hai là hướng ánh sáng. **[ngừng 0.5s]** Model B tạo ra bóng đổ nắng chiều khớp với hướng đèn trong cảnh quay người nói của mình, còn Model A làm bề mặt bị bóng nhựa. |
| `00:25 – 00:33` | **3. BODY (Tiêu chí 3)** | Kéo trực tiếp file của Model B thả vào giữa 2 đoạn A-roll trên Timeline Premiere, chỉnh nhẹ Lumetri Color 10 giây là tiệp màu hoàn toàn. | Tiêu chí 3: Đưa vào **timeline Premiere** có khớp nhịp và màu không? | Ba là tính ứng dụng trên timeline. Khi thả kết quả của Model B vào giữa hai cảnh quay thật trên Premiere, mình chỉ mất 10 giây chỉnh lại độ ấm màu là hai cảnh nối với nhau rất tự nhiên. |
| `00:33 – 00:40` | **4. CLOSE & CTA** | A-roll Thành chỉ vào giao diện Xưởng Media nơi cho phép chuyển đổi qua lại giữa các model trên cùng 1 khung làm việc. | Trải nghiệm thử trên **Xưởng Media** qua link ở bio | Test song song hai model trên cùng một giao diện giúp mình chọn đúng cảnh chỉ sau vài phút. **[ngừng 0.5s]** Mình chạy thử nghiệm này trên Xưởng Media, link dùng thử có affiliate mình để rõ ở bio nhé. |

#### 3. Shot List chuẩn bị
- **A-roll:** Thành ngồi trước màn hình mở song song trình duyệt chạy Xưởng Media và Premiere Pro.
- **Screen Record:** Quá trình dán cùng 1 câu prompt tiếng Việt/Anh chuẩn hóa vào 2 model trên Xưởng Media, xuất file và kéo vào timeline Premiere chỉnh Lumetri Color.
- **Asset đồ họa:** Bảng chấm điểm 3 tiêu chí (`1. Bố cục góc máy` — `2. Ánh sáng tự nhiên` — `3. Khớp timeline`).

#### 4. Caption TikTok & Facebook Reels
- **Caption TikTok:**
  Cách mình so sánh 2 model AI tạo B-roll bằng cùng 1 câu prompt: Không chấm theo độ lung linh khi đứng lẻ, mà chấm theo 3 tiêu chí của Editor (Đúng bố cục để chèn text, Đúng hướng ánh sáng, và Ghép khớp màu với cảnh quay thật trên Premiere).
  Mình chạy thử nghiệm này trên Xưởng Media — link dùng thử (có affiliate) mình để rõ ở bio nhé.
  `#dungcochudich #aiworkflow #videoeditor #xuongmedia`
- **Caption Facebook Reels:**
  Mỗi tuần lại có thêm model tạo ảnh, tạo video mới nhưng với một người làm hậu kỳ, câu hỏi quan trọng nhất vẫn là: "Đưa file đó vào timeline Premiere cạnh cảnh quay thật thì trông có bị lạc quẻ không?". Mình dùng đúng 1 câu prompt cố định để test song song 2 model trên Xưởng Media theo 3 tiêu chí thực chiến này. Bạn nào muốn tự tay test thử cho dự án của mình có thể xem link ở bio nhé.

#### 5. Bài đăng Facebook cá nhân (`crosspost`)
```text
Khi xem các video demo AI trên mạng, chúng ta rất dễ bị choáng ngợp bởi những cảnh đại cảnh khoa học viễn tưởng hoặc hiệu ứng biến hình rực rỡ. Nhưng khi quay về bàn làm việc của một video editor làm nội dung thương hiệu cá nhân và bán hàng, bài toán lại thực tế hơn nhiều: "Làm sao tạo ra một cảnh B-roll 3 giây trông tự nhiên để lấp vào đoạn chuyển ý mà không bị lệch tông với cảnh quay thật?".

Tuần này mình dành thời gian test song song hai model tạo visual trên Xưởng Media bằng cùng một câu prompt cố định (cảnh góc bàn làm việc có nắng chiều chiếu xiên để làm nền chèn chữ). Thay vì đánh giá cảm tính, mình chấm điểm theo 3 tiêu chí của người dựng:

1. Khả năng chừa khoảng trống bố cục (Negative Space): Trong video ngắn có chèn chữ (On-screen text), nếu AI lúc nào cũng đặt vật thể chính chình ình giữa khung hình thì khi đè chữ lên sẽ rất rối. Mình ưu tiên model hiểu đúng lệnh "đặt vật thể ở 1/3 khung hình bên dưới, chừa khoảng trống phía trên".
2. Độ chân thực của ánh sáng và chất liệu (Texture): Các model thiên về nghệ thuật thường làm da người hoặc mặt bàn gỗ bị mịn quá mức như nhựa. Khi đặt cạnh cảnh quay bằng điện thoại hoặc máy ảnh thật, người xem nhận ra ngay sự giả tạo.
3. Thời gian xử lý hậu kỳ trên Premiere: Một output AI tốt nhưng chuyển động bị méo ở giây cuối hoặc sai lệch nhiệt độ màu quá nặng sẽ làm editor tốn thêm 15 phút cắt gọt. Mình chỉ giữ lại kết quả nào thả vào timeline, chỉnh nhẹ Lumetri Color trong 10–15 giây là ăn nhập với đoạn A-roll.

Điểm tiện lợi là trên Xưởng Media mình có thể gõ 1 câu prompt rồi đổi qua lại giữa các model để đối chiếu ngay mà không phải mở 3–4 tab tài khoản rời rạc.

(Link dùng thử Xưởng Media — có gắn mã giới thiệu affiliate của mình — mình để sẵn ở phần bio trang cá nhân cho bạn nào muốn tự test workflow này nhé).
```

---

### VIDEO 10: `C053` — Workflow từ ý tưởng đến 10 biến thể nội dung

#### 1. Thông tin định danh
- **Mã nội dung:** `C053`
- **Pillar & Tuyến:** P3 (AI trong workflow editor) — `AI06` (Tối ưu năng suất & Nhân bản nội dung)
- **Format:** Flow demo (Vẽ sơ đồ quy trình + Chạy demo thực tế)
- **Tệp khán giả:** Agency nhỏ / Đội ngũ Marketing in-house / Creator cần sản xuất số lượng đều
- **Giai đoạn Funnel:** Chuyển đổi (Conversion)
- **CTA:** Xem workflow
- **Offer đích:** Xưởng Media (Link trải nghiệm công cụ ở bio — có ghi chú affiliate minh bạch)
- **Bằng chứng sử dụng:** Sơ đồ thực tế biến 1 chủ đề gốc thành 10 biến thể (3 góc tiếp cận × 3 biến thể Hook + bộ Visual Asset đồng bộ tạo trên Xưởng Media và đóng gói trong Premiere).
- **Core Claim:** Nhân bản 1 ý tưởng thành 10 biến thể không phải là bảo AI viết 10 bài giống hệt nhau, mà là giữ cố định 1 thông điệp cốt lõi rồi dùng AI tách góc tiếp cận và thay 3 giây hình ảnh mở đầu trên Xưởng Media.

#### 2. Bảng kịch bản sản xuất chi tiết (42 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác Timeline (Visual) | Text trên màn hình (On-screen Text) | Lời thoại (Voiceover / A-roll) & SFX |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | Quay màn hình sơ đồ cây từ 1 ô màu vàng (`1 Ý tưởng gốc`) tỏa ra 10 file video hoàn chỉnh trên màn hình Premiere Pro. | Cách mình biến **1 ý tưởng gốc** thành 10 biến thể video có chủ đích | **[SFX: Tiếng vẽ sơ đồ nhanh]** Đây là quy trình giúp mình biến một ý tưởng gốc thành 10 biến thể video thử nghiệm mà không phải quay lại từ đầu. |
| `00:03 – 00:10` | **2. PROOF / TENSION** | Chiếu cảnh một người ngồi quay 10 lần liên tiếp hoặc bảo AI viết ra 10 kịch bản văn phong y hệt nhau (gạch chéo đỏ). | Nhân bản nội dung không phải là tạo ra **10 bài nói giống hệt nhau** | Khi cần test xem góc nội dung nào hiệu quả cho sản phẩm, nếu bạn quay mới hoàn toàn cả 10 video sẽ cực kỳ tốn sức, còn nếu nhờ AI viết tự động cả bài thì giọng văn rất máy móc. |
| `00:10 – 00:18` | **3. BODY (Bước 1)** | Mở sơ đồ Bước 1: Giữ nguyên phần Thân bài (15 giây chứng minh sản phẩm/quy trình thật), chỉ dùng AI tách ra 3 góc mở đầu cho 3 nhóm người xem khác nhau. | Bước 1: Giữ cố định **phần bằng chứng** — Tách góc mở đầu theo tệp xem | Mình chia quy trình này làm ba bước rõ ràng. **[SFX: Pop]** Một: Phần thân bài chứng minh sản phẩm khoảng 15 giây mình giữ cố định bằng cảnh quay thật. Mình chỉ dùng AI để tách vấn đề đầu vào thành 3 góc cho 3 nhóm khách hàng. |
| `00:18 – 00:26` | **3. BODY (Bước 2)** | Mở giao diện **Xưởng Media**: Từ mỗi góc tiếp cận, tạo nhanh các bộ Visual Hook (cảnh mở đầu 3 giây: cảnh so sánh, cảnh bối cảnh sử dụng, cảnh phóng cận) đồng bộ bảng màu. | Bước 2: Tạo bộ **cảnh mở đầu 3 giây** cho từng góc trên Xưởng Media | Hai: Với mỗi góc mở đầu, mình lên Xưởng Media tạo các cảnh visual 3 giây đầu tiên tương ứng với bối cảnh của từng tệp người xem, tạo thành 10 tổ hợp mở bài khác nhau. |
| `00:26 – 00:34` | **3. BODY (Bước 3)** | Mở Timeline Premiere Pro: Tổ chức theo cấu trúc mô-đun (`Track 1: 10 Hook Visual + Voice` ghép nối với `Track 2: Phần thân Proof cố định` + `Track 3: 2 biến thể CTA`). | Bước 3: Lắp ghép dạng **mô-đun trên Premiere** để xuất 10 phiên bản | Ba: Đưa toàn bộ vào Premiere theo dạng lắp ghép mô-đun: thay 3 giây hình ảnh và câu mở đầu ở đầu timeline, giữ phần bằng chứng thật ở giữa, giúp mình xuất ra 10 biến thể rất gọn. |
| `00:34 – 00:42` | **4. CLOSE & CTA** | A-roll Thành chỉ vào sơ đồ tổng thể `AI tách biến thể Hook (Xưởng Media) + Editor kiểm soát phần Proof thật (Premiere)`. | Xem công cụ **Xưởng Media** mình dùng trong workflow này ở bio | AI giúp bạn nhân nhanh các phép thử ở phần mở đầu, còn cảnh thật ở giữa giữ trọn niềm tin của khách. **[ngừng 0.5s]** Bạn có thể xem và dùng thử Xưởng Media mình chạy trong workflow này qua link affiliate ở bio nhé. |

#### 3. Shot List chuẩn bị
- **A-roll:** Thành ngồi trước bảng vẽ/iPad hoặc màn hình sơ đồ Flowchart rồi chuyển sang màn hình máy tính.
- **Screen Record:**
  1. Sơ đồ Flowchart: `1 Core Proof (15s quay thật)` + `3 Góc khách hàng` × `3 Visual Hook tạo trên Xưởng Media` + `Biến thể CTA` = `10 Video test`.
  2. Màn hình thao tác tạo hàng loạt visual asset đồng bộ phong cách trên Xưởng Media.
  3. Màn hình Timeline Premiere xếp sẵn 10 đoạn đầu nối vào phần thân chuẩn.

#### 4. Caption TikTok & Facebook Reels
- **Caption TikTok:**
  Workflow biến 1 ý tưởng gốc thành 10 biến thể video để test hiệu quả chuyển đổi:
  - Giữ cố định 15 giây bằng chứng thật ở phần thân (Editor kiểm soát)
  - Dùng AI tách góc tiếp cận & tạo 10 cảnh mở đầu 3 giây trên Xưởng Media
  - Lắp ghép dạng mô-đun trên Premiere Pro.
  Link dùng thử Xưởng Media (có affiliate) mình để rõ ở bio cho bạn nào muốn áp dụng workflow này nhé.
  `#dungcochudich #aiworkflow #xuongmedia #marketingvideo`
- **Caption Facebook Reels:**
  Với các đội ngũ marketing nhỏ hoặc creator bận rộn, việc phải nghĩ và quay mới hoàn toàn 10 video mỗi tuần là áp lực rất lớn. Thay vì làm mới 100% từng bài, mình áp dụng nguyên tắc "Mô-đun hóa": Giữ nguyên phần lõi chứng minh sản phẩm bằng cảnh quay thật, và chỉ dùng AI kết hợp Xưởng Media để tạo ra 10 biến thể mở đầu (Hook 3s) cho từng nhóm khách hàng khác nhau. Bạn xem thử sơ đồ 3 bước trong video nhé.

#### 5. Bài đăng Facebook cá nhân (`crosspost`)
```text
Làm sao để một đội marketing 1–2 người hoặc một creator cá nhân có thể test được 10 biến thể video từ một chủ đề gốc mà không bị kiệt sức vì quay đi quay lại, cũng không biến kênh thành một bãi rác "video công nghiệp" giống hệt nhau?

Câu trả lời của mình nằm ở việc tách một video 35 giây thành các khối lắp ghép (mô-đun) và giao đúng việc cho AI lẫn con người:

1. Khối cố định — Phần Bằng chứng thật (Giây 04 đến 25 — Con người làm 100%):
Khi bạn đã có một đoạn quay thực tế chứng minh chất lượng sản phẩm hoặc quy trình làm việc rất tốt, đừng chỉ dùng nó đúng 1 lần rồi bỏ kho. Đây là phần tạo dựng niềm tin nên mình giữ nguyên cảnh thật, giọng thật.

2. Khối biến thiên — 10 Tổ hợp Câu mở đầu & Hình ảnh 3 giây đầu (AI + Xưởng Media hỗ trợ):
Cùng một sản phẩm (ví dụ: dịch vụ thiết kế hoặc một món đồ công nghệ), người mua đến từ nhiều nỗi đau khác nhau: người cần tiết kiệm thời gian, người sợ mua nhầm hàng kém bền, người cần làm quà tặng. Mình dùng AI để liệt kê các góc tiếp cận này, sau đó lên Xưởng Media tạo nhanh bộ hình ảnh/chuyển động 3 giây đầu khớp với từng tình huống đó.

3. Lắp ghép và kiểm soát nhịp trên Premiere (Editor hoàn thiện):
Mình đưa 10 đoạn mở đầu đó vào một project chuẩn trên Premiere, nối mượt với phần thân bằng chứng thật và xuất ra các phiên bản khác nhau để đo xem góc tiếp cận nào có tỷ lệ giữ chân 3 giây và tỷ lệ hỏi mua cao nhất.

Cách làm này vừa giữ được sự chân thật của sản phẩm, vừa tận dụng đúng tốc độ sản xuất visual của AI.

(Công cụ mình dùng để tạo đồng bộ các cảnh visual mở đầu trong video là Xưởng Media — mình có để link trải nghiệm kèm mã giới thiệu affiliate ở bio trang cá nhân cho bạn nào muốn test thử quy trình này nhé).
```

---

### VIDEO 11: `C054` — Nếu bắt đầu AI video từ số 0, tôi học theo thứ tự này

#### 1. Thông tin định danh
- **Mã nội dung:** `C054`
- **Pillar & Tuyến:** P3 (AI trong workflow editor) — `AI07` (Lộ trình học & Ứng dụng AI bài bản)
- **Format:** Roadmap (Lộ trình 4 bước từ gốc đến ngọn)
- **Tệp khán giả:** Người mới bắt đầu tìm hiểu AI làm nội dung / Editor muốn tích hợp AI vào nghề
- **Giai đoạn Funnel:** Chuyển đổi (Conversion)
- **CTA:** Xem lộ trình
- **Offer đích:** Zero To AI (Link tìm hiểu lộ trình học & cộng đồng ở bio — có ghi chú affiliate minh bạch)
- **Bằng chứng sử dụng:** Sơ đồ Lộ trình 4 bước thực tế mà Thành đã đi qua trong hơn 6 tháng tập trung ứng dụng AI + các sản phẩm mẫu ở từng chặng.
- **Core Claim:** Người mới học làm video với AI hay bỏ cuộc vì nhảy ngay vào tạo video chuyển động phức tạp; thứ tự đúng để làm ra sản phẩm dùng được là: Tư duy kịch bản & Prompt → Tạo ảnh tĩnh đồng nhất → Tạo chuyển động ngắn 2–4 giây → Đưa vào trình dựng để kiểm soát thông điệp.

#### 2. Bảng kịch bản sản xuất chi tiết (43 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác Timeline (Visual) | Text trên màn hình (On-screen Text) | Lời thoại (Voiceover / A-roll) & SFX |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | A-roll Thành đứng/ngồi trước tấm bảng lộ trình 4 bậc thang từ `Bước 1: Kịch bản` đến `Bước 4: Timeline hoàn chỉnh`, gạch bỏ lối tắt nhảy vọt từ số 0 lên thẳng tạo video dài. | Bắt đầu làm **AI Video từ số 0**: Đừng học ngược từ ngọn xuống gốc | **[SFX: Tiếng gạch bút dạ]** Nếu hôm nay bắt đầu học ứng dụng AI vào làm video từ con số 0, mình sẽ không bao giờ nhảy vào bấm nút tạo video ngay lập tức. |
| `00:03 – 00:10` | **2. PROOF / TENSION** | Chiếu cảnh thư mục chứa hàng chục clip AI bị biến dạng khuôn mặt, sai góc máy và không thể ghép thành một câu chuyện hoàn chỉnh. | Nhảy vào tạo video ngay rất dễ tốn tiền credit mà **không ghép thành bài được** | Sai lầm khiến mình từng đốt rất nhiều thời gian và chi phí thử nghiệm lúc mới học là cố ép AI xuất ra ngay một video dài, để rồi nhân vật mỗi cảnh một mặt và không dùng được vào việc thật. |
| `00:10 – 00:17` | **3. BODY (Bước 1 & 2)** | Chiếu Bước 1 (Khung Prompt tìm góc nội dung & tách Shot List 3 cột) và Bước 2 (Tạo 4 bức ảnh tĩnh có cùng nhân vật, ánh sáng và góc máy). | Bước 1 & 2: Làm chủ **cấu trúc kịch bản** và tạo **ảnh tĩnh đồng nhất** | Thứ tự 4 bước giúp bạn làm ra sản phẩm dùng được ngay là: **[SFX: Pop]** Một: Học cách viết prompt để lọc ý tưởng và chia kịch bản thành từng cảnh ngắn. Hai: Học tạo ảnh tĩnh trước để kiểm soát được bố cục, ánh sáng và sự đồng nhất của nhân vật. |
| `00:17 – 00:26` | **3. BODY (Bước 3)** | Chiếu Bước 3: Đưa bức ảnh tĩnh đã chuẩn vào model tạo video, chỉ yêu cầu 1 chuyển động máy quay nhẹ dài 3 giây (Camera pan / Zoom in nhẹ). | Bước 3: Biến ảnh tĩnh thành **chuyển động ngắn 2–4 giây** có chủ đích | Ba: Khi đã có bức ảnh tĩnh đúng ý 100%, bạn mới đưa ảnh đó sang công cụ tạo video để thêm những chuyển động ngắn từ 2 đến 4 giây như lia máy nhẹ hoặc chuyển động ánh sáng. |
| `00:26 – 00:34` | **3. BODY (Bước 4)** | Chiếu Bước 4: Đưa các đoạn 3 giây đó vào Premiere/CapCut, kết hợp giọng đọc thật, phụ đề nhấn từ khóa và âm thanh môi trường. | Bước 4: Đưa vào **trình dựng** để ghép nhịp, giọng nói và thông điệp | Bốn: Đưa các cảnh đó vào phần mềm dựng để ghép với giọng nói, đặt chữ nhấn thông điệp và thêm tiếng động. **[ngừng 0.5s]** Đây là bước biến các mảnh ghép AI thành một video có hồn và có mục tiêu. |
| `00:34 – 00:43` | **4. CLOSE & CTA** | A-roll Thành chỉ vào sơ đồ 4 bước hoàn chỉnh và giới thiệu ngắn gọn mục `Zero To AI` ở bio. | Xem lộ trình học bài bản tại mục **Zero To AI** ở bio của mình | Đi từ gốc kịch bản đến ảnh tĩnh rồi mới tới chuyển động và hậu kỳ sẽ giúp bạn không bị ngợp trước hàng trăm công cụ mới. **[ngừng 0.5s]** Nếu bạn muốn học bài bản theo lộ trình rõ ràng từ đầu, xem mục Zero To AI mình để ở bio nhé. |

#### 3. Shot List chuẩn bị
- **A-roll:** Thành ngồi trước màn hình hiển thị sơ đồ 4 chặng đường (`1. Script & Prompt` → `2. Consistent Image` → `3. Intentional Motion 2-4s` → `4. Editing & Storytelling`).
- **Screen Record:** Minh họa trực quan 1 ví dụ đi xuyên suốt 4 bước: Câu kịch bản → Ảnh tĩnh chuẩn bố cục → Clip 3s chuyển động từ ảnh đó → Thành phẩm trên timeline Premiere.
- **Asset đồ họa:** Infographic 4 bước lộ trình học AI Video cho người mới.

#### 4. Caption TikTok & Facebook Reels
- **Caption TikTok:**
  Nếu bắt đầu học ứng dụng AI làm video từ con số 0, đừng nhảy ngay vào tạo video chuyển động phức tạp.
  Hãy đi theo đúng 4 bước này để làm ra video dùng được cho công việc thật:
  1. Prompt tư duy kịch bản & chia cảnh
  2. Tạo ảnh tĩnh đồng nhất bố cục & ánh sáng
  3. Tạo chuyển động ngắn 2–4 giây từ ảnh tĩnh
  4. Đưa vào trình dựng để kiểm soát nhịp & thông điệp.
  Nếu bạn muốn học theo lộ trình bài bản từ gốc, xem mục Zero To AI (link affiliate) ở bio của mình nhé.
  `#dungcochudich #zerotoai #aiworkflow #hoclamvideo`
- **Caption Facebook Reels:**
  Rất nhiều bạn mới tìm hiểu AI làm nội dung thường bị choáng vì mỗi ngày lại thấy người ta nhắc tên một công cụ mới, thử cái nào cũng ra được vài giây ngẫu nhiên nhưng không tài nào ghép thành một video hoàn chỉnh phục vụ công việc. Nhìn lại hơn 6 tháng tập trung kết hợp AI vào quy trình dựng, đây là thứ tự 4 bước thực tế nhất để bạn đi từ số 0 mà không bị tốn tiền và thời gian vô ích. Lộ trình chi tiết mình có để ở mục Zero To AI trên bio nhé.

#### 5. Bài đăng Facebook cá nhân (`crosspost`)
```text
Tuần trước có một bạn mới bắt đầu tìm hiểu AI nhắn hỏi mình: "Anh ơi bây giờ có chục công cụ tạo video AI khác nhau, em là người mới tinh thì nên mua gói của bên nào để bấm ra được video hoàn chỉnh luôn ạ?"

Mình trả lời thật là: Nếu chưa nắm được khung kịch bản và cách kiểm soát hình ảnh tĩnh mà bạn nạp tiền vào các công cụ tạo video ngay, khả năng rất cao là bạn sẽ đốt hết số điểm (credit) chỉ sau hai buổi tối mà vẫn không ghép nổi một video 30 giây có đầu có đuôi.

Nhìn lại quá trình mình tự mày mò và áp dụng AI vào công việc hậu kỳ thực tế, nếu hôm nay bắt đầu lại từ số 0, mình sẽ học theo đúng thứ tự 4 bậc thang này:

1. Bậc 1 — Dùng AI để làm rõ Kịch bản & Chia cảnh (Text-to-Structure):
Trước khi nghĩ đến hình ảnh, phải biết dùng AI để gọt một ý tưởng lan man thành kịch bản 30 giây (1 vấn đề - 1 thông điệp - 1 lời kêu gọi) và tách thành bảng phân cảnh (Shot List) rõ ràng.

2. Bậc 2 — Kiểm soát Ảnh tĩnh đồng nhất (Text-to-Image):
Đừng vội làm chuyển động. Hãy học cách mô tả góc máy, tiêu cự, hướng ánh sáng để tạo ra một bức ảnh tĩnh đúng ý mình trước. Khi bạn kiểm soát được ảnh tĩnh, bạn đã thắng được 70% chất lượng thị giác của video.

3. Bậc 3 — Tạo chuyển động ngắn có chủ đích (Image-to-Video 2–4 giây):
Lấy chính bức ảnh tĩnh đã duyệt ở Bậc 2 đưa vào công cụ tạo video và chỉ yêu cầu một chuyển động rất gọn (như lia máy chậm, nhân vật gật đầu, khói bay nhẹ). Cách làm từ Ảnh sang Video giúp hình ảnh không bị biến dạng ngẫu nhiên.

4. Bậc 4 — Lắp ghép và thổi hồn trên phần mềm dựng (Editing):
Đưa các đoạn 2–4 giây đó về Premiere hoặc CapCut để ghép với giọng đọc thật, đặt chữ nhấn đúng từ khóa và cân chỉnh âm thanh.

Đi từng bậc như vậy sẽ giúp bạn làm chủ công cụ thay vì chạy theo công cụ. Bạn nào muốn bắt đầu học ứng dụng AI vào nội dung một cách có hệ thống từ gốc có thể tham khảo lộ trình và cộng đồng Zero To AI mình để sẵn ở link bio cá nhân (link có gắn affiliate minh bạch của mình) nhé.
```

---

## PHẦN 4: NHÓM PILLAR 4 — CASE STUDY CHUYỂN ĐỔI DỊCH VỤ (`C060`)

---

### VIDEO 12: `C060` — Case study: từ footage thô đến video hoàn chỉnh

#### 1. Thông tin định danh
- **Mã nội dung:** `C060`
- **Pillar & Tuyến:** P4 (Hành trình & Bằng chứng) — `JRN05` (Case Study thực tế)
- **Format:** Case study (Bóc tách từ đề bài gốc → 3 quyết định dựng lại → So sánh Before/After → Kết quả)
- **Tệp khán giả:** Khách hàng tiềm năng (Chủ thương hiệu cá nhân, Chủ doanh nghiệp nhỏ, Creator cần thuê dựng)
- **Giai đoạn Funnel:** Chuyển đổi (Conversion)
- **CTA:** Nhắn EDIT
- **Offer đích:** Dịch vụ Edit/Media
- **Bằng chứng sử dụng:** Dự án có quyền công bố (hoặc Case quy trình/kỹ thuật được ghi chú minh bạch theo chuẩn định vị Ngày 01): Footage quay thô dài 2 phút 40 giây bị đều giọng và thiếu cảnh minh họa → Bản dựng hoàn chỉnh 36 giây.
- **Core Claim:** Biến một file quay thô dài dòng thành video 36 giây giữ chân người xem không nằm ở việc đắp hiệu ứng, mà nằm ở 3 quyết định: đảo câu kết quả lên làm Hook, cắt bỏ 60% lời dẫn dắt trùng lặp và bổ sung B-roll + chữ nhấn đúng từ khóa chuyển đổi.

#### 2. Bảng kịch bản sản xuất chi tiết (44 giây)

| Timecode | Nhịp | Hình ảnh / Thao tác Timeline (Visual) | Text trên màn hình (On-screen Text) | Lời thoại (Voiceover / A-roll) & SFX |
| :--- | :--- | :--- | :--- | :--- |
| `00:00 – 00:03` | **1. HOOK** | Split-screen Trên/Dưới: Phía trên là file quay thô gốc dài `02:40` chỉ có 1 góc ngồi nói đều đều; Phía dưới là bản Final Cut `00:36` có nhịp cắt sắc gọn, B-roll minh họa và chữ nhấn rõ ràng. | Từ file quay thô **2 phút 40 giây** thành video hoàn chỉnh **36 giây** | **[SFX: Tiếng kéo khóa / Whoosh]** Đây là cách mình biến một file quay thô dài gần 3 phút chỉ có một góc máy thành bản dựng 36 giây đúng mục tiêu thu hút khách hàng. |
| `00:03 – 00:10` | **2. PROOF / TENSION** | Mở đề bài (Brief) và file gốc trên Premiere: 18 giây đầu của file gốc đang chào hỏi, giới thiệu tên tuổi và nói vòng vo chưa vào chủ đề chính. | Vấn đề của file gốc: **18 giây đầu** chưa nói rõ người xem nhận được gì | Khi nhận file này, mục tiêu là làm người xem nhắn tin nhận tư vấn, nhưng 18 giây đầu của bản quay thô lại toàn là lời chào và dẫn nhập chung chung. **[ngừng 0.5s]** Nếu giữ nguyên thứ tự này, người xem sẽ lướt đi ngay từ giây thứ ba. |
| `00:10 – 00:19` | **3. BODY (Quyết định 1)** | Thao tác trên Timeline: Thành cắt câu đắt giá nhất nằm ở phút `01:52` của file gốc kéo thẳng về giây `00:00` làm câu Hook mở đầu, kèm zoom 115%. | Quyết định 1: Đảo câu **kết quả ở phút thứ 2** lên làm 3 giây mở đầu | Mình đã thực hiện ba quyết định dựng lại cấu trúc. **[SFX: Click]** Một: Nghe hết file gốc, nhặt đúng câu nêu kết quả cụ thể nhất ở phút thứ hai đẩy thẳng lên làm 3 giây mở đầu, đồng thời cắt bỏ hơn 60% những câu lặp ý. |
| `00:19 – 00:27` | **3. BODY (Quyết định 2)** | Chiếu đoạn giữa timeline (Giây 05–25): Chèn cảnh quay màn hình quy trình thật + 2 cảnh visual minh họa tạo bằng AI đã chỉnh tiệp màu để phá thế "1 góc máy ngồi nói". | Quyết định 2: Đắp **bằng chứng trực quan** và visual AI vào đoạn giải thích | Hai: Vì file gốc chỉ có một góc ngồi nói một chỗ, ở mỗi luận điểm quan trọng mình đắp thêm cảnh quay màn hình bằng chứng và tạo thêm hai cảnh bối cảnh bằng AI để mắt người xem luôn có điểm bám. |
| `00:27 – 00:35` | **3. BODY (Quyết định 3)** | Chiếu 5 giây cuối của Bản Final: Chữ trên màn hình chỉ tô vàng đúng 1 cụm từ khóa mỗi câu, âm thanh sạch và kết thúc bằng tấm thẻ hướng dẫn hành động rõ ràng. | Quyết định 3: Nhấn đúng **1 từ khóa mỗi câu** và khóa lại bằng **CTA rõ** | Ba: Mình chuẩn hóa lại toàn bộ phần chữ trên màn hình theo nguyên tắc mỗi khung hình chỉ nhấn một từ khóa, xử lý lại âm thanh giọng nói và đặt khung hướng dẫn nhắn tin ở 4 giây cuối. |
| `00:35 – 00:44` | **4. CLOSE & CTA** | Chạy trọn vẹn 4 giây ấn tượng nhất của bản Before đặt cạnh bản After, sau đó chuyển sang A-roll Thành chốt câu Signature & CTA. | Có sẵn footage cần dựng rõ thông điệp? Nhắn chữ **EDIT** cho mình | Đó là cách mình kết hợp tư duy marketing, kỹ năng dựng và AI để dựng có chủ đích. **[ngừng 0.5s]** Nếu bạn có sẵn footage thô và muốn biến thành video rõ thông điệp như thế này, nhắn chữ "EDIT" kèm mục tiêu của bạn cho mình nhé. |

#### 3. Shot List chuẩn bị
- **A-roll:** Thành ngồi tại bàn dựng, ánh sáng chuyên nghiệp, chỉ trực tiếp vào màn hình Before/After.
- **Screen Record:**
  1. Timeline Sequence 1 (`01_RAW_FOOTAGE_02m40s` — 1 track video, 1 track audio dài).
  2. Timeline Sequence 2 (`02_FINAL_CUT_36s` — cấu trúc lại thứ tự câu, cắt gọn còn 36s, có track B-roll/AI, track Text nhấn từ khóa và Sound Design vừa đủ).
  3. Khung hình so sánh Before/After chạy song song.
- **Asset đồ họa:** Thẻ tóm tắt 3 quyết định dựng (`1. Đảo Hook từ phút thứ 2` — `2. Phủ Proof & AI B-roll` — `3. Nhấn 1 từ khóa + CTA rõ`).

#### 4. Caption TikTok & Facebook Reels
- **Caption TikTok:**
  Case Study: Biến file quay thô 2 phút 40 giây (chỉ có 1 góc ngồi nói) thành video 36 giây giữ chân người xem và dẫn về hành động nhắn tin.
  3 quyết định trên timeline:
  1. Nhặt câu kết quả ở phút thứ 2 đẩy lên làm Hook 3 giây đầu
  2. Gọt bỏ 60% câu lặp ý & đắp bằng chứng trực quan + AI B-roll
  3. Nhấn đúng 1 từ khóa mỗi khung hình & khóa bằng CTA rõ.
  Nếu bạn có sẵn footage nhưng video chưa ra đúng thông điệp muốn bán, nhắn chữ "EDIT" cho mình nhé.
  `#dungcochudich #casestudy #videoeditor #marketingvideo`
- **Caption Facebook Reels:**
  Rất nhiều anh chị chủ doanh nghiệp hoặc chuyên gia khi ngồi trước máy quay thường nói rất đầy đủ trong 3–4 phút, nhưng nếu đăng nguyên bản đó lên Reels hay TikTok thì người xem lướt qua ngay ở 5 giây đầu vì đoạn mở bài quá dài. Đây là cách mình nhận một file quay thô 2 phút 40 giây, sắp xếp lại cấu trúc thông điệp theo tư duy marketing và rút gọn thành bản dựng 36 giây sắc nét. Bạn nào đang có sẵn nguồn quay cần xử lý hậu kỳ có chủ đích thì nhắn chữ "EDIT" cho mình nhé.

#### 5. Bài đăng Facebook cá nhân (`crosspost`)
```text
Nhiều khách hàng khi gửi file quay thô cho mình thường lo lắng: "Anh ngồi nói trước máy quay có một góc cố định suốt gần 3 phút, lại hay bị lặp từ và dẫn dắt hơi dài ở đoạn đầu, không biết lên video ngắn có giữ được người xem không em?".

Thực ra, bạn không cần phải là một MC chuyên nghiệp nói trôi chảy ngay từ giây đầu tiên. Việc biến một bản ghi hình thô 2 phút 40 giây thành một video 36 giây gãy gọn, đúng trọng tâm chính là phần việc của một editor có tư duy marketing.

Trong case thực tế mình vừa thực hiện (đã được sự đồng ý chia sẻ về mặt quy trình), thay vì giữ nguyên thứ tự lời nói từ đầu đến cuối rồi đắp hiệu ứng lên, mình đã can thiệp bằng 3 quyết định dựng lại cấu trúc:

1. Đảo cấu trúc thông điệp (Kéo câu ở phút 01:52 lên giây 00:00):
Khi người nói mới bấm máy, 15–20 giây đầu thường là lúc họ đang "lấy đà" nên câu chữ rất chung chung. Mình nghe toàn bộ gần 3 phút file gốc, tìm ra câu nói đắt giá nhất có con số và kết quả cụ thể nằm ở phút 01:52, cắt câu đó đặt thẳng lên 3 giây đầu tiên làm Hook. Riêng bước này đã thay đổi hoàn toàn khả năng giữ chân ở 3 giây đầu.

2. Cắt bỏ 60% lời giải thích lặp ý và phủ hình ảnh chứng minh:
Để rút từ 160 giây xuống 36 giây, mình lược bỏ toàn bộ các câu nối rườm rà và những ý bị lặp lại lần thứ hai. Ở những câu nêu luận điểm quan trọng, mình chèn cảnh quay màn hình bằng chứng thực tế kết hợp thêm 2 cảnh bối cảnh tạo bằng AI (đã chỉnh lại màu sắc cho tiệp với cảnh quay thật) để người xem không bị nhàm chán vì một góc máy tĩnh.

3. Kiểm soát điểm nhìn bằng chữ và CTA cuối bài:
Thay vì cho phụ đề nhảy nhót đủ màu, trên mỗi câu thoại mình chỉ tô màu nhấn vào đúng 1 cụm từ khóa mang kết luận, đồng thời khóa lại ở 4 giây cuối bằng một lời chỉ dẫn hành động duy nhất khớp với mục tiêu ban đầu của đề bài.

Một bản dựng tốt không làm người nói biến thành một người khác, mà giúp phiên bản rõ ràng và thuyết phục nhất của họ xuất hiện ngay trong 30 giây đầu tiên. Đó là cách mình dựng có chủ đích.

Nếu bạn đang có sẵn footage quay cho thương hiệu cá nhân hoặc dịch vụ nhưng chưa có thời gian (hoặc chưa biết cách) biên tập lại cấu trúc thông điệp như vậy, nhắn cho mình chữ "EDIT" kèm mục tiêu kênh của bạn để mình trao đổi cụ thể nhé.
```

<!-- ===== /file: personal-brand-video-engine/references/01_Y_TUONG_VA_SCRIPT/05_12_VIDEO_DU_PHONG_BAO_CAO_VA_CHUYEN_DOI_SAU.md ===== -->

<!-- ===== file: personal-brand-video-engine/references/01_Y_TUONG_VA_SCRIPT/06_SHOT_LIST_QUAY_BATCH_TUAN_1.md ===== -->

# KẾ HOẠCH BẤM MÁY BATCH 240 PHÚT — TUẦN 1 + 3 VIDEO GHIM (NGÀY 04 — 24/10/2026)

> **Ngày thực hiện:** Thứ Bảy, 24/10/2026 (Ngày 04 — Giai đoạn Chuẩn bị Nền móng `DA-00` & `DA-01`)
> **Tổng thời lượng:** `240 phút` (4 tiếng tập trung)
> **Đầu ra bắt buộc cuối buổi:**
> 1. Đủ toàn bộ Footage (A-roll, B-roll, Screen Record) cho **4 video Tuần 1 (`C001, C022, C040, C055`)** + **3 Video Ghim đầu kênh (`GHIM-01, GHIM-02, GHIM-03`)**.
> 2. Toàn bộ file đã được sao lưu và đổi tên chuẩn theo `Content ID` trong thư mục `02_FOOTAGE`.
> 3. Hoàn thành **2 bản dựng thô (Rough Cut)** cho `C001` và `C022` để Ngày 05 (`25/10/2026`) chỉ việc hoàn thiện phụ đề, âm thanh, QA và lên lịch.
> **Nguyên tắc kỷ luật tại trường quay:** Không sửa lại kịch bản trong lúc quay (trừ khi phát hiện lỗi sai sự thật). Không quay lẻ từng bài từ đầu đến cuối mà **gom theo Góc máy (Batch by Setup)** để không mất thời gian dời đèn và đổi фокус.

---

## 1. PHÂN BỔ THỜI GIAN 240 PHÚT (TIMELINE BUỔI QUAY)

| Khung giờ (Gợi ý) | Thời lượng | Hạng mục công việc | Đầu ra kiểm tra được |
| :--- | :---: | :--- | :--- |
| **Block 1 (`00:00 – 00:25`)** | 25 phút | **Setup bối cảnh, ánh sáng, âm thanh & màn hình nền** | 1 clip test 10 giây kiểm tra nét, sáng, tiếng đạt `-6dB`, không vang/rè |
| **Block 2 (`00:25 – 01:15`)** | 50 phút | **PHIÊN 1 — Góc máy A-Roll (Nói trực diện ống kính)** cho cả 7 video (`GHIM-01..03` + `C001, C022, C040, C055`) | 7 file A-roll hoàn chỉnh (mỗi bài 2–3 take chuẩn nhất trong 1 file) |
| **Block 3 (`01:15 – 01:55`)** | 40 phút | **PHIÊN 2 — Góc máy B-Roll (Bàn làm việc, thao tác tay & cảnh mẫu Before/After)** | Đủ toàn bộ cảnh quay phụ và cảnh diễn mẫu lỗi cho 7 video |
| **Block 4 (`01:55 – 02:45`)** | 50 phút | **PHIÊN 3 — Quay màn hình (Screen Record Premiere Pro, After Effects, AI & Starter Kit)** | Toàn bộ file quay màn hình 60fps độ phân giải cao, rõ con trỏ chuột |
| **Block 5 (`02:45 – 03:05`)** | 20 phút | **Ingest, đổi tên file theo chuẩn Content ID & Sao lưu** | Thư mục `02_FOOTAGE` gọn sạch, đúng mã `C001`–`GHIM03` |
| **Block 6 (`03:05 – 04:00`)** | 55 phút | **Dựng Rough Cut 2 video đầu tuần (`C001` & `C022`)** | 2 Sequence đã cắt xong A-roll + đắp B-roll chính trong `03_PROJECT_EDIT` |

---

## 2. CHECKLIST THIẾT LẬP BỐI CẢNH (BLOCK 1 — 25 PHÚT)

Trước khi bấm nút Record cho Phiên 1, rà soát nhanh 5 điểm cố định sau:
- [ ] **Khung hình (Framing):** Đặt máy dọc `9:16` (`1080x1920` hoặc `4K 2160x3840` tại `30fps`), góc máy ngang tầm mắt Thành, cỡ cảnh Medium Close-up (từ ngang ngực lên trên đỉnh đầu chừa khoảng trống 15% cho Text Card tiêu đề).
- [ ] **Hậu cảnh (Background):** Bàn làm việc gọn gàng (chỉ để màn hình mở sẵn giao diện Premiere Pro có timeline màu sắc rõ ràng, 1 cuốn sổ ghi chú marketing, chuột và bàn phím). Tắt đèn trần gây bóng đổ hốc mắt, dùng 1 nguồn sáng chính (Key light) chéo 45 độ trước mặt.
- [ ] **Âm thanh (Audio):** Mic cài áo cách miệng 15–20cm. Thu thử 1 câu nói bình thường và 1 câu nhấn mạnh để đảm bảo mức âm lượng nằm trong khoảng `-12dB` đến `-6dB`, không bị vỡ tiếng (clipping).
- [ ] **Trang phục (Wardrobe):** Chuẩn bị sẵn **2 áo đơn sắc tối giản** (ví dụ: 1 áo đen/xám than cho nhóm `GHIM` + `C001, C040`; 1 áo trắng kem/xanh navy cho `C022, C055`) để khi đăng lên kênh nhìn các video có sự thay đổi tự nhiên dù quay chung 1 buổi.
- [ ] **Kịch bản nhắc chữ (Prompting):** Đặt bản kịch bản ở ngay sát dưới cụm camera điện thoại/máy ảnh. Đọc nhẩm 1 lượt câu chữ trước khi nói, giữ đúng nhịp nghỉ `0.5s` giữa các câu theo Voice Profile.

---

## 3. PHIÊN 1: QUAY BATCH GÓC MÁY A-ROLL NÓI TRỰC DIỆN (BLOCK 2 — 50 PHÚT)

> **Cách quay tối ưu:** Giữ nguyên vị trí máy và đèn. Mỗi video bấm quay 1 file duy nhất, đọc liền mạch từng câu; nếu vấp chữ thì nghỉ 1 giây rồi nói lại từ đầu câu đó (vỗ tay 1 tiếng trước câu nói lại để lúc nhìn Waveform cắt trong 2 giây).

### Ca 1A — Trang phục 1 (Áo tối màu đơn sắc) — 30 phút

| Thứ tự bấm máy | Mã Video | Tên File Lưu Chuẩn | Nội dung lời thoại cần đọc trực diện ống kính (Trích nguyên văn kịch bản) | Ghi chú biểu cảm & cử chỉ tay |
| :---: | :---: | :--- | :--- | :--- |
| **01** | `GHIM-01` | `GHIM01_AROLL_01.mp4` | 1. *"Rất nhiều video dựng cực kỳ mượt, nhưng người xem lướt qua sau ba giây vì không hiểu video đang nói với ai."*<br>2. *"Mình là Thành, một video editor xuất phát từ nền tảng digital marketing."*<br>3. *"Trên kênh này, mình ghi lại quá trình kết hợp ba thứ: dùng tư duy marketing để khóa đúng một thông điệp, dùng kỹ thuật dựng để dẫn mắt người xem, và dùng AI đúng chỗ để rút ngắn thời gian làm phần thô."*<br>4. *"Nếu bạn muốn làm video không chỉ đẹp mà còn khiến người xem hiểu, nhớ và hành động — theo dõi kênh nhé. Đó là cách mình dựng có chủ đích."* | Nhìn thẳng ống kính, câu 3 giơ 3 ngón tay nhịp nhàng theo 3 trụ cột Marketing – Edit – AI. |
| **02** | `GHIM-03` | `GHIM03_AROLL_01.mp4` | 1. *"Lý do lớn nhất khiến bạn quay hai tiếng nhưng lúc dựng vẫn thiếu cảnh là vì bật máy quay trước khi khóa thông điệp."*<br>2. *"Trước mỗi buổi quay batch bốn video, mình luôn đi qua bốn bước: một là chọn đúng một khung hook khớp với nỗi đau người xem; hai là gọt kịch bản về đúng một ý chính."*<br>3. *"Ba là dùng AI chuyển kịch bản đó thành danh sách cảnh quay để không sót B-roll; và bốn là rà qua mười điểm kiểm tra phụ đề, âm thanh, CTA trước khi bấm xuất file."*<br>4. *"Mình đã đóng gói toàn bộ checklist, mẫu brief, mười lăm cấu trúc hook và năm prompt AI này thành bộ Starter Kit miễn phí. Bạn bấm vào link ở bio của mình để lấy về dùng ngay cho video tuần này nhé."* | Ở câu 1 tay cầm tờ Checklist 1 trang giơ nhẹ lên ngang ngực; câu 4 chỉ nhẹ tay xuống hướng link bio. |
| **03** | `C001` | `C001_AROLL_01.mp4` | 1. *"Đây là lý do video của bạn mất bảy mươi phần trăm người xem ngay ba giây đầu."*<br>2. *"Khi người xem chưa biết bạn là ai, họ không có lý do để chờ bạn chào hỏi hay giới thiệu tên."*<br>3. *"Cách mình sửa trên timeline rất đơn giản. Một: cắt bỏ toàn bộ khoảng lấy hơi và câu chào đầu tiên. Hai: tìm câu nói rõ kết quả nhất ở giữa bài, kéo thẳng lên giây không không."*<br>4. *"Nhìn lại bản sau khi sửa nhé: vừa mở lên là thấy ngay vấn đề của người xem và bằng chứng trên màn hình. Nhịp gọn hơn hẳn mà không cần thêm hiệu ứng phức tạp."*<br>5. *"Trước khi xuất file, bạn hãy kiểm tra lại đúng ba giây đầu tiên này. Mình để sẵn bản checklist đầy đủ trong Starter Kit ở bio, bạn lưu lại để đối chiếu khi dựng nhé."* | Nhịp vào câu 1 dứt khoát ngay sau tiếng phanh gấp; nghỉ rõ `0.5s` sau câu 2. |
| **04** | `C040` | `C040_AROLL_01.mp4` | 1. *"Nếu bạn chỉ gõ vào AI câu 'cho tôi mười ý tưởng làm video', thứ bạn nhận lại sẽ là mười gạch đầu dòng đọc lên nghe rất quen nhưng không quay được."*<br>2. *"Khi dùng AI để tìm góc nội dung, mình luôn khóa trước ba dữ kiện: một là người xem cụ thể là ai, hai là lỗi họ đang gặp, và ba là trên máy mình đang có sẵn bằng chứng gì để show ra."*<br>3. *"Bạn nhìn kết quả trên màn hình nhé: AI trả ra mười góc trong mười giây. Nhưng bước quan trọng nhất nằm ở đây: mình gạch bỏ ngay bảy góc nói lý thuyết suông, chỉ giữ lại đúng ba góc mà mình mở timeline Premiere lên chứng minh được ngay."*<br>4. *"Nhờ cách lọc này, chỉ từ một vấn đề là 'ba giây đầu yếu', mình có ngay ba video khác nhau cho cả tuần mà không bị trùng lặp cách nói."*<br>5. *"AI giúp bạn đi nhanh phần thô, nhưng người chọn góc phải là bạn. Nếu bạn muốn lấy mẫu prompt này và học cách ứng dụng AI vào làm nội dung từ gốc, xem mục Zero To AI ở bio của mình nhé."* | Ở câu 2 tay chỉ nhẹ sang góc màn hình nơi sẽ chèn khung highlight 3 biến số Prompt. |

### Ca 1B — Trang phục 2 (Đổi áo sáng màu / xanh navy) — 20 phút

| Thứ tự bấm máy | Mã Video | Tên File Lưu Chuẩn | Nội dung lời thoại cần đọc trực diện ống kính (Trích nguyên văn kịch bản) | Ghi chú biểu cảm & cử chỉ tay |
| :---: | :---: | :--- | :--- | :--- |
| **05** | `GHIM-02` | `GHIM02_AROLL_01.mp4` | 1. *"Cùng một thư mục quay thô khách gửi, nhưng chỉ cần đổi ba quyết định dựng, hiệu quả giữ người xem đã khác hẳn."*<br>2. *"Thứ nhất: mình cắt bỏ toàn bộ năm giây chào hỏi đầu video và đẩy cảnh kết quả rõ nhất từ cuối lên ngay hai giây đầu tiên."*<br>3. *"Thứ hai: thay vì cắt đều theo nhịp nhạc, mình giữ nhịp nhanh ở phần nêu vấn đề và chèn cận cảnh bằng chứng đúng lúc người nói nhắc đến lợi ích chính."*<br>4. *"Thứ ba: mình bỏ câu kêu gọi theo dõi chung chung ở cuối, thay bằng một lời mời hành động cụ thể gắn với nhu cầu mua hàng."*<br>5. *"Nếu bạn đang có sẵn footage hoặc ý tưởng nhưng video lên chưa ra đúng chất và mục tiêu, nhắn chữ 'EDIT' cho mình để mình xem thử nhé."* | Phong thái đĩnh đạc, tin cậy như đang tư vấn trực tiếp cho khách hàng dịch vụ. |
| **06** | `C022` | `C022_AROLL_01.mp4` | 1. *"Cùng một thư mục quay thô bốn cảnh, nhưng cách bạn sắp xếp trên timeline sẽ quyết định người xem lướt đi hay nhắn tin mua hàng."*<br>2. *"Ở bản thứ nhất, mình xếp đúng theo trình tự lúc bấm máy: chuẩn bị, thao tác rồi mới tới thành phẩm. Nhìn vẫn sạch, nhưng ba giây đầu không nói được lợi ích gì cho khách."*<br>3. *"Sang bản thứ hai, mình đổi lại thứ tự kể chuyện. Mở đầu ngay bằng cận cảnh thành phẩm đẹp nhất trong một phẩy năm giây, tiếp theo là lỗi khách thường gặp, rồi mới dùng cảnh thao tác làm bằng chứng."*<br>4. *"Bạn có thể thấy: không cần quay lại một cảnh nào, chỉ cần đổi điểm mở đầu và giữ lâu hơn ở khung hình chứng minh chất lượng, cảm giác tin cậy đã tăng lên rõ rệt."*<br>5. *"Đó là cách mình dựng có chủ đích. Nếu bạn đang có sẵn footage sản phẩm hoặc kênh cá nhân nhưng lên video chưa ra đúng thông điệp muốn bán, nhắn chữ 'EDIT' cho mình nhé."* | Nhấn rõ sự đối lập giữa "bản thứ nhất" và "bản thứ hai". |
| **07** | `C055` | `C055_AROLL_01.mp4` | 1. *"Mình xuất phát từ ngành marketing, nhưng sau gần một năm đi làm thực tế, công việc mình chọn gắn bó mỗi ngày lại là dựng video."*<br>2. *"Lúc làm marketing, mình từng thấy rất nhiều ý tưởng viết trên giấy thì cực kỳ chặt chẽ. Nhưng khi chuyển thành video, chỉ vì ba giây đầu mở sai nhịp hoặc nhồi quá nhiều chữ mà người xem lướt qua sạch."*<br>3. *"Đó là lý do hơn sáu tháng qua, mình dồn toàn bộ thời gian vào Premiere, After Effects và các công cụ AI. Mình chưa phải người dựng lâu năm nhất, nhưng nền tảng marketing cho mình một thói quen: luôn hỏi người xem nhận được gì trước khi chèn bất kỳ hiệu ứng nào."*<br>4. *"Mình lập kênh này để ghi lại trọn vẹn chín mươi ngày thử nghiệm kết hợp ba thứ: tư duy marketing, kỹ năng dựng và AI ứng dụng thực tế."*<br>5. *"Mọi thứ mình học được, làm được và cả những ca phải sửa lại đều sẽ được cập nhật ở đây. Theo dõi kênh để đồng hành cùng mình nhé."* | Giọng kể chuyện trầm ấm, chân thật, tốc độ chậm hơn các bài tutorial khoảng 10%. |

---

## 4. PHIÊN 2: QUAY BATCH GÓC MÁY B-ROLL & CẢNH MẪU (BLOCK 3 — 40 PHÚT)

> **Cách quay tối ưu:** Dời chân máy sang góc chéo 45 độ cạnh bàn làm việc (Over-the-shoulder) và góc cận cảnh mặt bàn (Top-down / Close-up). Quay liên hoàn toàn bộ các cảnh phụ cho cả 7 video trong 1 lần đổi góc máy.

| Thứ tự | Phục vụ Mã Video | Tên File Lưu Chuẩn | Mô tả cảnh quay chi tiết (3–6 giây/cảnh) | Đạo cụ / Bối cảnh cần trên bàn |
| :---: | :---: | :--- | :--- | :--- |
| **01** | `C001` & `GHIM-02` | `C001_BROLL_SAMPLE_RAW.mp4` | **Cảnh mẫu làm lỗi Before (2–4 giây):** Thành ngồi trước máy, tay chỉnh cổ áo, hít hơi sâu, nhìn hơi ngập ngừng rồi nói: *"À ừm, xin chào mọi người, hôm nay mình sẽ chia sẻ..."* | Giữ nguyên góc máy trước bàn, diễn tự nhiên đúng lỗi người mới hay mắc. |
| **02** | `C022` & `GHIM-02` | `C022_BROLL_RAW_01.mp4`<br>`C022_BROLL_RAW_02.mp4`<br>`C022_BROLL_RAW_03.mp4`<br>`C022_BROLL_RAW_04.mp4` | **Bộ 4 cảnh quay thô cùng 1 chủ đề (Setup bàn làm việc / Đóng gói sản phẩm mẫu / Pha đồ uống):**<br>- `RAW_01`: Cảnh chuẩn bị đồ đạc đặt lên bàn (3s).<br>- `RAW_02`: Cảnh thao tác lắp đặt / pha chế (4s).<br>- `RAW_03`: Cảnh cận điểm lỗi thường gặp (dây cáp rối / góc bàn tối / thao tác vướng) (3s).<br>- `RAW_04`: Cảnh thành phẩm hoàn chỉnh, bật đèn đẹp mắt, sắc nét nhất (4s). | Bộ đồ vật trên bàn làm việc hoặc 1 sản phẩm mẫu có sẵn của Thành. |
| **03** | `C055` & `GHIM-01` | `C055_BROLL_MKT_NOTES.mp4` | **Cận cảnh (Close-up):** Tay Thành dùng bút gạch chân 1 câu thông điệp cốt lõi trên cuốn sổ ghi chú Marketing / tờ Brief đặt ngay cạnh bàn phím và chuột. | Sổ tay ghi chú sơ đồ Funnel (`Nhận biết → Cân nhắc → Chuyển đổi`) + bút highlight. |
| **04** | `C055` & `GHIM-01` | `C055_BROLL_EDITING_DESK.mp4` | **Góc nghiêng qua vai (Over-the-shoulder):** Thấy rõ tay trái Thành bấm phím tắt (`C`, `V`, `Space`), tay phải di chuột cắt timeline Premiere Pro và chỉnh keyframe trên After Effects. | Màn hình mở project thật có nhiều lớp layer màu sắc rõ ràng. |
| **05** | `GHIM-03` & `C001` | `GHIM03_BROLL_STARTERKIT.mp4` | **Cận cảnh màn hình điện thoại / iPad hoặc bản in:** Cảnh lướt qua trang bìa "Starter Kit v1 — Dựng Có Chủ Đích" và cảnh bấm vào nhánh số 1 trên Link Bio điện thoại. | Điện thoại mở sẵn giao diện Link Bio 3 nhánh. |

---

## 5. PHIÊN 3: QUAY MÀN HÌNH — SCREEN RECORD PREMIERE, AE & AI (BLOCK 4 — 50 PHÚT)

> **Thiết lập OBS / Phần mềm quay màn hình:** Độ phân giải `1920x1080` (hoặc `2560x1440`), `60fps`, bật hiển thị con trỏ chuột, phóng to giao diện Premiere/Trình duyệt lên `125%–150%` để khi cắt dọc `9:16` người xem trên điện thoại đọc rõ từng chữ.

| Thứ tự | Phục vụ Mã Video | Tên File Lưu Chuẩn | Thao tác cần thực hiện trên màn hình | Lưu ý để lên hình sạch & thuyết phục |
| :---: | :---: | :--- | :--- | :--- |
| **01** | `C001` & `GHIM-02` | `C001_SCREEN_01.mp4` | Mở timeline Premiere của clip mẫu: Phóng to thanh Waveform 3 giây đầu → Dùng công cụ Razor (`C`) cắt bỏ đoạn lấy hơi + câu chào → Nhấn `Shift + Delete` (Ripple Delete) → Kéo đoạn kết quả màu xanh lá từ giây `00:20` lên thẳng `00:00`. | Tô màu Label: đoạn lỗi đầu màu **Đỏ (Rose)**, đoạn kết quả kéo lên đầu màu **Xanh lá (Caribbean)** để mắt người xem nhận biết ngay. |
| **02** | `C022` & `GHIM-02` | `C022_SCREEN_01.mp4` | Mở 2 Sequence xếp chồng (Pancake Timeline) trong Premiere:<br>- Sequence trên (`Bản 1 - Thứ tự quay`): `Clip 1 → Clip 2 → Clip 3 → Clip 4`.<br>- Sequence dưới (`Bản 2 - Có chủ đích`): Kéo `Clip 4 (Kết quả)` lên đầu → nối `Clip 3 (Vấn đề)` → `Clip 2 (Bằng chứng)`. | Chạy thanh Playhead qua cả 2 timeline để thấy sự khác biệt ngay ở 3 giây đầu. |
| **03** | `GHIM-02` | `GHIM02_SCREEN_ENDCARD.mp4` | Quay màn hình so sánh 2 thẻ kết thúc (End card): Bản cũ chữ *"Nhớ follow kênh nhé"* đổi thành Bản mới *"Nhắn chữ EDIT để mình xem thử footage của bạn"*. | Bật/tắt mắt layer trên Premiere để thấy sự thay đổi trước/sau. |
| **04** | `C040` | `C040_SCREEN_BAD_PROMPT.mp4` | Mở trình duyệt AI, gõ câu lệnh cụt lủn: `"Cho tôi 10 ý tưởng làm video TikTok về edit video"` → Cuộn qua danh sách kết quả chung chung. | Dừng lại 2 giây ở các dòng kết quả sáo rỗng để lát nữa đóng khung đỏ. |
| **05** | `C040` & `GHIM-01` | `C040_SCREEN_GOOD_PROMPT.mp4` | Mở tab AI thứ hai, dán Prompt chuẩn 3 biến số của Thành:<br>`"Đóng vai Marketing Video Editor. Tệp xem: Creator mới tự quay video bị mất người xem ở 3s đầu. Bằng chứng tôi có sẵn: Timeline Premiere và bản so sánh Before/After. Hãy đề xuất 10 góc video ngắn 35 giây..."` → AI xuất bảng 10 góc. | Phóng to trình duyệt `150%` để chữ tiếng Việt hiện sắc nét trên khung dọc. |
| **06** | `C040` | `C040_SCREEN_FILTER.mp4` | Chuyển bảng 10 góc của AI sang Google Sheet / Notion: Thao tác tô màu xám/gạch ngang 7 góc lý thuyết, tô màu xanh lá 3 góc có bằng chứng quay được ngay (`C001, C002, C003`). | Thao tác chuột dứt khoát, rõ ràng giữa phần "AI làm thô" và "Mình lọc tinh". |
| **07** | `GHIM-03` | `GHIM03_SCREEN_KIT.mp4` | Quay màn hình lướt qua 4 tab/trang trong tài liệu **Starter Kit v1**: (1) 15 khung Hook 3 giây, (2) Khung kịch bản 1-Claim, (3) Bảng Shot List & 5 Prompt AI, (4) Checklist 10 điểm trước khi Export. | Cuộn mượt từng mục, dừng 2 giây ở mỗi tiêu đề lớn. |
| **08** | `C055` | `C055_SCREEN_90DAYS.mp4` | Quay màn hình mở file `He-thong-content-ca-nhan-Thanh.xlsx` (tab `Lịch 90 ngày` và `Hệ nội dung`) + mở cây thư mục `THUONG_HIEU_CA_NHAN_THANH_90_NGAY` trên máy tính. | Chứng minh hệ thống làm việc thật và kế hoạch 90 ngày đã sẵn sàng. |

---

## 6. QUY TẮC ĐẶT TÊN FILE & CẤU TRÚC THƯ MỤC LƯU TRỮ (BLOCK 5 — 20 PHÚT)

Ngay sau khi quay xong Phiên 1, 2, 3, chép toàn bộ thẻ nhớ và file quay màn hình vào thư mục `02_FOOTAGE` theo đúng quy ước chuẩn dưới đây để không mất thời gian tìm file khi dựng:

### A. Công thức đặt tên file chuẩn
```text
[Mã_Content_ID]_[Loại_File]_[Số_Thứ_Tự]_[Mô_Tả_Ngắn].mp4
```
- **Mã Content ID:** `GHIM01`, `GHIM02`, `GHIM03`, `C001`, `C022`, `C040`, `C055`.
- **Loại File:**
  - `AROLL`: Cảnh Thành nói trực diện ống kính (có thu âm chính).
  - `BROLL`: Cảnh quay phụ bàn làm việc, thao tác tay, sản phẩm mẫu.
  - `SCREEN`: Cảnh quay màn hình máy tính / điện thoại.
  - `ASSET`: Ảnh chụp màn hình, bảng biểu, thẻ chữ tĩnh (`.png` / `.jpg`).

### B. Sơ đồ cây thư mục sau khi Ingest xong (Cuối Block 5)
```text
THUONG_HIEU_CA_NHAN_THANH_90_NGAY/
└── 02_FOOTAGE/
    ├── 00_PINNED_VIDEOS/
    │   ├── GHIM01_AROLL_01.mp4
    │   ├── GHIM02_AROLL_01.mp4
    │   ├── GHIM02_SCREEN_ENDCARD.mp4
    │   ├── GHIM03_AROLL_01.mp4
    │   ├── GHIM03_BROLL_STARTERKIT.mp4
    │   └── GHIM03_SCREEN_KIT.mp4
    └── 01_TUAN_01_2610_3110/
        ├── C001_BaGiayDau/
        │   ├── C001_AROLL_01.mp4
        │   ├── C001_BROLL_SAMPLE_RAW.mp4
        │   ├── C001_SCREEN_01.mp4
        │   └── C001_ASSET_01.png
        ├── C022_HaiCachKeChuyen/
        │   ├── C022_AROLL_01.mp4
        │   ├── C022_BROLL_RAW_01.mp4
        │   ├── C022_BROLL_RAW_02.mp4
        │   ├── C022_BROLL_RAW_03.mp4
        │   ├── C022_BROLL_RAW_04.mp4
        │   └── C022_SCREEN_01.mp4
        ├── C040_10GocVideoAI/
        │   ├── C040_AROLL_01.mp4
        │   ├── C040_SCREEN_BAD_PROMPT.mp4
        │   ├── C040_SCREEN_GOOD_PROMPT.mp4
        │   └── C040_SCREEN_FILTER.mp4
        └── C055_MarketingSangEditor/
            ├── C055_AROLL_01.mp4
            ├── C055_BROLL_MKT_NOTES.mp4
            ├── C055_BROLL_EDITING_DESK.mp4
            └── C055_SCREEN_90DAYS.mp4
```

---

## 7. HƯỚNG DẪN DỰNG ROUGH CUT 2 VIDEO ĐẦU TUẦN (BLOCK 6 — 55 PHÚT)

Trong 55 phút cuối cùng của buổi Batch Ngày 04, mở Premiere Pro tạo file dự án `03_PROJECT_EDIT/TUAN_01_BATCH.prproj` và hoàn thành Rough Cut cho `C001` (đăng Thứ Hai 26/10) và `C022` (đăng Thứ Ba 27/10):

1. **Phút 00 – 25 (Rough Cut `C001`):**
   - Kéo `C001_AROLL_01.mp4` vào Sequence `C001_RoughCut` (1080x1920, 30fps).
   - Nhìn sóng âm (Waveform) cắt giữ lại các take nói chuẩn nhất, gọt sạch khoảng thở đầu/cuối câu để tổng thời lượng giọng đọc về đúng khung `35–36 giây`.
   - Đặt `C001_BROLL_SAMPLE_RAW.mp4` vào giây `00:00 – 00:02` và đắp `C001_SCREEN_01.mp4` lên lớp V2 ở đoạn `00:10 – 00:30`.
2. **Phút 25 – 50 (Rough Cut `C022`):**
   - Kéo `C022_AROLL_01.mp4` vào Sequence `C022_RoughCut`, cắt gọn nhịp thoại về khung `37–38 giây`.
   - Dựng nhanh 2 cụm B-roll từ bộ `C022_BROLL_RAW_01..04.mp4` (Cụm 1 xếp xuôi chiều thời gian ở giây `00:04 – 00:13`; Cụm 2 đảo `RAW_04` lên đầu ở giây `00:24 – 00:31`) và đặt `C022_SCREEN_01.mp4` vào đoạn giữa `00:13 – 00:24`.
3. **Phút 50 – 55 (Lưu Project & Chốt buổi):**
   - Bấm `Ctrl + S`, sao lưu file `.prproj` sang ổ đĩa/cloud dự phòng.
   - Đánh dấu hoàn thành Ngày 04 (`Quay batch tuần 1`) trong bảng theo dõi 90 ngày, sẵn sàng cho Ngày 05 hoàn thiện phụ đề, âm thanh và lên lịch xuất bản.

<!-- ===== /file: personal-brand-video-engine/references/01_Y_TUONG_VA_SCRIPT/06_SHOT_LIST_QUAY_BATCH_TUAN_1.md ===== -->

<!-- ===== file: personal-brand-video-engine/references/05_ASSET/STARTER_KIT_V1_DUNG_CO_CHU_DICH.md ===== -->

# STARTER KIT V1 — DỰNG CÓ CHỦ ĐÍCH
### Bộ Công Cụ Thực Chiến: Từ Ý Tưởng Đến Video Ngắn Rõ Thông Điệp, Giữ Chân Người Xem & Tạo Chuyển Đổi

> **Tác giả:** Thành — Dựng Có Chủ Đích (`Video Editor | Marketing Mindset | AI Workflow`)  
> **Phiên bản:** v1.0 (Tài liệu Lead Magnet chính thức — Sẵn sàng nhân bản sang Notion hoặc xuất PDF)  
> **Dành cho:** Creator xây thương hiệu cá nhân, Chủ shop tự làm video bán hàng, Đội ngũ Marketing nhỏ và Video Editor muốn làm video có mục tiêu rõ ràng.

---

## LỜI MỞ ĐẦU NGẮN: VÌ SAO BẠN CẦN BỘ STARTER KIT NÀY?

Phần lớn video ngắn bị lướt qua trong 3 giây đầu hoặc có lượt xem nhưng không tạo ra khách hàng không phải vì thiếu hiệu ứng chuyển cảnh phức tạp, mà vì **thiếu chủ đích ngay từ lúc lên khung**:
1. Mở đầu bằng lời chào hỏi hoặc dẫn nhập quá dài khiến người xem rời đi trước giây thứ 3.
2. Nhồi 3–4 thông điệp và 2–3 lời kêu gọi (CTA) vào cùng một video 35 giây khiến người xem không nhớ được ý nào.
3. Dùng AI viết kịch bản hoặc tạo hình ảnh một cách tự động mà thiếu bước biên tập lại theo ngôn ngữ nói và nhịp cắt thực tế.

Bộ **Starter Kit v1 — Dựng Có Chủ Đích** này đóng gói **5 công cụ thực chiến** mà mình sử dụng hàng ngày khi lên kịch bản, ứng dụng AI và hậu kỳ trên Premiere/After Effects. Bạn không cần đọc từ đầu đến cuối như một cuốn sách lý thuyết — hãy mở đúng phần bạn đang cần ngay trước mỗi buổi viết kịch bản, bấm máy hoặc xuất file.

---

## PHẦN 1: 15 CÔNG THỨC HOOK 3 GIÂY ĐẦU (KÈM CHỈ DẪN HÌNH ẢNH)

> **Quy tắc 3 giây đầu (`Dựng Có Chủ Đích`):**
> - **Tuyệt đối không mở đầu bằng:** *"Xin chào mọi người, mình là..."*, *"Hôm nay mình sẽ chia sẻ..."*, *"Trong thời đại AI bùng nổ..."*.
> - **Độ dài câu nói mở đầu:** Tối đa 1 câu ngắn (**8–14 từ**), đọc gọn trong **2.5 – 3 giây**.
> - **Bắt buộc đi kèm chuyển động thị giác ngay giây `00:00`:** Khung hình chia đôi (Split-screen), khoanh đỏ điểm lỗi, zoom vào kết quả cuối cùng hoặc thao tác thật trên màn hình.

### Nhóm A: 5 Công Thức Hook Từ Lỗi Sai & Nỗi Đau Cụ Thể (Giữ chân người đang gặp bế tắc)

| STT | Công thức câu nói (Điền vào `[...]`) | Ví dụ áp dụng thực tế | Chỉ dẫn hình ảnh (Visual 00:00–00:03) |
| :--- | :--- | :--- | :--- |
| **01** | **Đừng `[hành động quen thuộc]` nếu bạn chưa kiểm tra `[điểm mấu chốt này]`.** | *"Đừng bấm xuất file video bán hàng nếu bạn chưa kiểm tra 3 giây đầu này."* | Quay cận tay sắp bấm nút Export trên màn hình rồi dừng hình, khoanh đỏ 3 giây đầu trên timeline. |
| **02** | **Đây là lý do bạn `[nỗ lực nhiều]` nhưng vẫn bị `[kết quả tệ]`.** | *"Đây là lý do bạn quay 10 video giới thiệu sản phẩm nhưng khách vẫn lướt qua."* | Cho chạy 2 giây một video mẫu bị lỗi mở đầu chậm, kèm biểu đồ giữ chân tụt dốc ở giây thứ 2. |
| **03** | **Một lỗi nhỏ ở `[vị trí cụ thể]` đang làm video của bạn mất `[% hoặc kết quả]`.** | *"Một lỗi nhỏ ở dòng chữ trên màn hình đang làm người xem mỏi mắt sau 5 giây."* | Phóng to khung hình có 4–5 chữ nhảy màu loạn xạ, sau đó gạch chéo đỏ. |
| **04** | **Nếu `[tình huống của người xem]` đang bị `[dấu hiệu lỗi]`, hãy bỏ ngay bước này.** | *"Nếu kịch bản bạn viết bằng AI nghe vẫn giống văn mẫu, hãy bỏ ngay câu lệnh này."* | Chiếu đoạn văn bản ChatGPT dài dòng rồi dùng chuột bôi đen xóa thẳng đoạn mở bài sáo rỗng. |
| **05** | **90% người mới làm `[công việc]` đều tốn hàng giờ vì làm ngược bước này.** | *"Nhiều bạn mới học AI video tốn hết credit mà không ghép được bài vì học ngược bước này."* | Chiếu thư mục gồm hàng chục clip AI bị lỗi biến dạng mặt đặt cạnh sơ đồ lộ trình 4 bước. |

---

### Nhóm B: 5 Công Thức Hook Đặt Kết Quả Lên Đầu (Chứng minh năng lực ngay lập tức)

| STT | Công thức câu nói (Điền vào `[...]`) | Ví dụ áp dụng thực tế | Chỉ dẫn hình ảnh (Visual 00:00–00:03) |
| :--- | :--- | :--- | :--- |
| **06** | **Đây là cách mình biến `[đầu vào thô/khó]` thành `[kết quả hoàn chỉnh]` trong `[số bước/thời gian]`.** | *"Đây là cách mình biến file quay thô gần 3 phút thành video 36 giây đúng mục tiêu bán hàng."* | Split-screen Trên/Dưới: Trên là cảnh quay thô 1 góc tĩnh; Dưới là bản dựng hoàn chỉnh có B-roll và chữ nhấn. |
| **07** | **Video `[chủ đề]` này không dùng `[thứ phức tạp]`, chỉ tập trung vào `[yếu tố cốt lõi]`.** | *"Video bán hàng này không dùng một hiệu ứng chuyển cảnh nào nhưng khách vẫn hỏi giá liên tục."* | Chiếu video sản phẩm cắt thẳng (straight cut) đặt trên timeline Premiere hoàn toàn trống hiệu ứng. |
| **08** | **Kết quả sau khi mình cắt bỏ `[thứ dư thừa]` khỏi `[sản phẩm/video]`.** | *"Kết quả sau khi mình cắt bỏ 60% lời dẫn dắt thừa khỏi video giới thiệu dịch vụ."* | Chạy 2 giây bản dựng mới sắc gọn ngay đầu tiên, sau đó lật sang timeline đầy những vết cắt gọn. |
| **09** | **Chỉ cần thay đổi đúng `[1 chi tiết nhỏ]` này, `[kết quả đầu ra]` đã khác hẳn.** | *"Chỉ cần đảo câu kết luận ở phút thứ hai lên đầu, 3 giây mở màn đã khác hẳn."* | Thao tác chuột kéo một đoạn clip màu vàng từ cuối timeline đặt thẳng về mốc `00:00`. |
| **10** | **Quy trình `[số bước]` giúp mình `[kết quả thực tế]` mà không cần `[cách làm cực nhọc cũ]`.** | *"Quy trình 5 bước giúp khách duyệt bản dựng ngay lần đầu mà không phải sửa đi sửa lại."* | Mở thư mục dự án được đánh số từ `01` đến `05` gọn gàng kèm bảng tiến độ có tích xanh. |

---

### Nhóm C: 5 Công Thức Hook So Sánh Before/After & Con Số (Tạo độ tương phản thị giác)

| STT | Công thức câu nói (Điền vào `[...]`) | Ví dụ áp dụng thực tế | Chỉ dẫn hình ảnh (Visual 00:00–00:03) |
| :--- | :--- | :--- | :--- |
| **11** | **Cùng một `[đầu vào cố định]`, nhưng `[Cách B]` hiệu quả hơn `[Cách A]` nhờ điểm này.** | *"Cùng một câu prompt tạo cảnh B-roll, nhưng chỉ một trong hai model này đưa vào timeline thật được."* | Split-screen Trái/Phải chạy song song 2 output AI từ cùng 1 câu lệnh hiển thị ở giữa. |
| **12** | **`[Con số A]` nhưng không có `[kết quả]`, còn `[Con số B nhỏ hơn]` lại tạo ra `[kết quả thật]`.** | *"Một video 50 nghìn view không có tin nhắn nào, còn video 3 nghìn view lại mang về 4 khách hàng."* | Cầm 2 tấm thẻ số liệu (hoặc 2 ảnh chụp màn hình thống kê) đặt cạnh nhau trước ống kính. |
| **13** | **So sánh 3 giây đầu khi `[cách làm cũ]` và khi `[cách làm có chủ đích]`.** | *"So sánh 3 giây đầu khi nhấn màu cả 5 chữ và khi chỉ nhấn đúng 1 từ khóa."* | Chạy 1.5 giây bản chữ nhảy rối mắt (bên trái) rồi chuyển ngay sang 1.5 giây bản chữ tĩnh nhấn 1 từ (bên phải). |
| **14** | **Sau `[con số thực nghiệm]`, mình quyết định dừng `[thứ A]` và chỉ giữ lại `[thứ B]`.** | *"Sau 12 video đầu tiên trên kênh, mình quyết định dừng một format dù nó có lượt xem cao nhất."* | Quay cận bảng Google Sheet theo dõi KPI 12 video có dòng tô đỏ (Bỏ) và dòng tô xanh (Giữ). |
| **15** | **Từ `[1 nguyên liệu gốc]` ra `[N biến thể]` mà không phải `[làm lại từ đầu]`.** | *"Cách mình biến 1 ý tưởng gốc thành 10 biến thể video thử nghiệm mà không phải quay lại từ đầu."* | Sơ đồ nhánh cây từ 1 ô trung tâm tỏa ra 10 khung hình video nhỏ trên màn hình. |

---

## PHẦN 2: KHUNG KỊCH BẢN 30–40 GIÂY (`1 VIDEO = 1 CLAIM = 1 CTA`)

### 2.1. Quy tắc Cốt lõi trước khi viết
Trước khi viết bất kỳ dòng kịch bản nào, hãy điền đúng 4 ô kiểm soát này. Nếu ô số 2 có nhiều hơn 1 câu kết luận, hãy tách thành 2 video riêng:
- **Tệp người xem duy nhất của video này:** `......................................................`
- **1 Claim (1 câu kết luận duy nhất người xem cần nhớ):** `.........................................`
- **Bằng chứng nhìn thấy trên màn hình (Proof):** `....................................................`
- **1 CTA duy nhất ở cuối bài:** `...................................................................`

### 2.2. Bảng Khung Kịch Bản 4 Nhịp Chuẩn

| Nhịp | Thời lượng | Mục tiêu | Phần Hình ảnh & Chữ trên màn hình | Phần Lời thoại (8–16 từ/câu) |
| :--- | :--- | :--- | :--- | :--- |
| **1. HOOK** | `00:00 – 00:03` (1 câu) | Giữ mắt người xem + Nêu thẳng vấn đề hoặc kết quả | - Cắt bỏ toàn bộ khoảng lấy hơi đầu clip.<br>- Cho thấy ngay kết quả cuối hoặc lỗi sai.<br>- Text tiêu đề viết hoa chữ cái đầu, nằm trong vùng an toàn. | Nói thẳng 1 câu dưới 14 từ. Không chào hỏi, không giới thiệu bản thân. |
| **2. PROOF / TENSION** | `00:03 – 00:10` (2 câu) | Chứng minh vấn đề là thật bằng hình ảnh | - Khoanh đỏ vùng lỗi trên màn hình, mở timeline hoặc chiếu số liệu đối chứng. | Chỉ rõ nguyên nhân vì sao cách làm cũ gây mất người xem hoặc tốn thời gian. |
| **3. BODY (1 CLAIM)** | `00:10 – 00:32` (3–5 câu) | Giải quyết vấn đề bằng 2–3 bước cụ thể | - Đổi góc nhìn hoặc cắt cảnh mỗi 2–4 giây (A-roll xen kẽ Screen Record / B-roll).<br>- Mỗi câu chỉ tô màu nhấn **1 cụm từ khóa duy nhất**. | Trình bày tuần tự: Một là... Hai là... Ba là... Gắn liền với thao tác thật, không nói lý thuyết suông. |
| **4. CLOSE & CTA** | `00:32 – 00:40` (2 câu) | Chốt bài học + Chỉ dẫn 1 hành động tiếp theo | - Chạy lại 2–3 giây bản hoàn chỉnh.<br>- Hiển thị thẻ tóm tắt 3 bước hoặc chỉ dẫn CTA rõ ràng. | 1 câu đúc kết + 1 lời mời hành động khớp trực tiếp với chủ đề vừa nói. |

---

### 2.3. Ví dụ Thực Tế: Trước & Sau Khi Gọt Bỏ Ý Thừa

#### ❌ BẢN TRƯỚC KHI SỬA (Lỗi phổ biến: Mở bài dài, nhồi 3 chủ đề, 3 CTA cùng lúc)
> *"Xin chào tất cả mọi người, chào mừng mọi người đã quay trở lại với kênh của mình. Dạo này mình thấy rất nhiều bạn đang tập tành xây kênh TikTok và Reels để bán hàng nhưng chưa biết cách quay dựng sao cho đẹp. Hôm nay mình sẽ chia sẻ cho các bạn tất tần tật về cách chọn đèn quay, cách viết kịch bản bằng ChatGPT và cả cách chỉnh màu trên Premiere nữa nhé. Đầu tiên là về đèn thì các bạn nên mua đèn tầm 500k thôi, còn kịch bản thì cứ bảo AI viết rồi đọc theo, chỉnh màu thì kéo sáng lên một chút là được. Nếu các bạn thấy hay thì nhớ thả tim, follow kênh, chia sẻ video cho bạn bè và bạn nào cần thuê dựng video hay học khóa học AI của mình thì nhắn tin ngay cho mình nhé!"*
- **Chẩn đoán lỗi:** Mất 11 giây đầu chỉ để chào hỏi; nhồi cả 3 chủ đề (Đèn quay + Kịch bản AI + Chỉnh màu) khiến không phần nào đủ sâu; cuối bài đòi 4 hành động cùng lúc.

#### ✅ BẢN SAU KHI SỬA THEO CHUẨN `DỰNG CÓ CHỦ ĐÍCH` (35 giây — Chỉ giữ 1 Claim về Kịch bản AI)
- **`00:00 – 00:03 (Hook)`:** *(Hình: Bôi đỏ đoạn mở bài văn mẫu trên màn hình ChatGPT)*  
  "Nếu kịch bản bạn viết bằng AI nghe vẫn giống văn mẫu, hãy sửa ngay dòng lệnh đầu tiên này."
- **`00:03 – 00:10 (Proof/Tension)`:** *(Hình: So sánh bản AI viết mặc định dài 25 từ/câu và bản đã gọt)*  
  "Khi bạn chỉ bảo AI 'hãy viết kịch bản về sản phẩm A', nó sẽ luôn mở đầu bằng những câu giới thiệu rất dài dòng khiến người xem lướt qua ngay."
- **`00:10 – 00:30 (Body — 3 bước)`:** *(Hình: Quay cận 3 dòng điều kiện trong câu Prompt và kết quả xuất ra)*  
  "Trước khi bấm tạo kịch bản, mình luôn khóa ba điều kiện vào câu lệnh. Một: Cấm dùng câu chào hỏi ở 3 giây đầu. Hai: Giới hạn mỗi câu nói tối đa 14 chữ để khi đọc không bị hụt hơi. Ba: Bắt buộc đi kèm một gợi ý hình ảnh chứng minh cho mỗi câu nói."
- **`00:30 – 00:36 (Close & CTA)`:** *(Hình: Hiển thị khung Prompt hoàn chỉnh trong bộ Starter Kit)*  
  "Chỉ cần khóa khung như vậy, bản nháp của AI sẽ sát với ngôn ngữ nói hơn rất nhiều. Mình để sẵn nguyên văn 5 câu prompt này trong bộ Starter Kit ở bio, bạn vào lấy về dùng ngay nhé."

---

## PHẦN 3: 5 PROMPT AI THỰC CHIẾN CHO CREATOR & EDITOR

> **Nguyên tắc sử dụng AI của Thành:**  
> AI làm rất tốt phần **nháp thô** (liệt kê góc tiếp cận, rà soát cấu trúc, chia bảng phân cảnh), nhưng **con người phải làm phần tinh** (chọn ví dụ thật của mình, đọc lại thành tiếng để sửa chữ bị ngượng miệng, và quyết định nhịp cắt trên timeline).

---

### Prompt 01: Tìm 10 góc nội dung thực tế từ 1 vấn đề của khách hàng
*(Dùng khi bạn bí ý tưởng hoặc muốn khai thác sâu 1 sản phẩm/dịch vụ mà không bị lặp bài)*

```text
Đóng vai một người làm nội dung video ngắn có tư duy marketing thực chiến.
Tôi đang làm trong lĩnh vực: [Điền lĩnh vực/sản phẩm/dịch vụ của bạn].
Tệp khách hàng mục tiêu của tôi là: [Điền rõ tệp người xem, ví dụ: chủ shop thời trang tự quay video bằng điện thoại].
Vấn đề lớn nhất họ đang gặp phải là: [Điền vấn đề cụ thể, ví dụ: quay video lên hình bị tối và nói lan man không ra đơn].

Hãy giúp tôi tách vấn đề này thành 10 góc video ngắn (30–40 giây) hoàn toàn khác nhau, chia đều vào 3 nhóm:
1. Nhóm chỉ ra lỗi sai cụ thể trên thực tế (4 góc).
2. Nhóm hướng dẫn từng bước sửa nhanh trong 3 bước (3 góc).
3. Nhóm phân tích so sánh Trước/Sau hoặc Case thực tế (3 góc).

Yêu cầu bắt buộc:
- Không dùng các từ ngữ sáo rỗng như "bí quyết triệu view", "đỉnh cao", "bùng nổ doanh số".
- Mỗi góc nội dung phải ghi rõ: (1) Tiêu đề 1 câu, (2) 1 kết luận duy nhất (Core Claim), và (3) Cảnh hình ảnh cụ thể nên xuất hiện trong 3 giây đầu tiên.
```

---

### Prompt 02: Viết lại kịch bản nháp để loại bỏ "giọng văn máy" (AI Detox)
*(Dùng khi bạn đã có ý tưởng hoặc bản nháp nhưng đọc lên nghe giống văn viết báo cáo)*

```text
Dưới đây là bản nháp nội dung video ngắn của tôi:
"""
[Dán bản nháp hoặc ý tưởng thô của bạn vào đây]
"""

Hãy biên tập lại thành kịch bản nói trên video ngắn (thời lượng 35 giây) theo đúng các quy tắc giọng điệu sau:
1. Xưng "mình", gọi người xem là "bạn". Giọng điềm tĩnh, trực diện, như đang ngồi chỉ trực tiếp trên màn hình cho một người bạn đồng nghiệp.
2. Cắt bỏ 100% lời chào hỏi ở đầu bài và các câu hỏi câu tương tác giả tạo ở cuối bài (như "Các bạn nghĩ sao?").
3. Độ dài câu: Mỗi câu nói chỉ từ 8 đến 16 từ. Ngắt câu dứt khoát. Đánh dấu [ngừng 0.5s] ở những chỗ cần nhấn giọng.
4. Mọi nhận định phải đi theo trình tự: [Tình huống/Lỗi cụ thể] -> [Cách xử lý thực tế] -> [Kết quả nhìn thấy được].
5. Tuyệt đối không dùng các từ: "siêu phẩm", "thay đổi cuộc đời", "chỉ cần 1 click", "trong thời đại hiện nay".
```

---

### Prompt 03: Tạo 3 biến thể Hook 3 giây đầu để thử nghiệm (A/B Test)
*(Dùng trước khi bấm máy: Quay 3 câu mở đầu khác nhau trong 2 phút cho cùng 1 phần thân bài)*

```text
Tôi chuẩn bị quay một video ngắn 35 giây với thông điệp cốt lõi (Core Claim) là:
"[Điền 1 câu kết luận chính của video]"
Tệp người xem chính là: "[Điền tệp người xem]"

Hãy viết cho tôi 3 phương án mở đầu (Hook 3 giây đầu tiên) để tôi quay thử nghiệm, mỗi phương án chỉ gồm ĐÚNG 1 CÂU NÓI dưới 14 từ, kèm theo mô tả khung hình 3 giây đầu và dòng chữ hiển thị trên màn hình (On-screen Text):
- Phương án A (Đánh vào lỗi sai/nỗi đau trực diện): ...
- Phương án B (Đưa kết quả hoàn chỉnh lên giây đầu tiên): ...
- Phương án C (So sánh đối lập Trước/Sau hoặc Con số thực tế): ...

Lưu ý: Dòng chữ trên màn hình chỉ viết hoa chữ cái đầu câu và đánh dấu **in đậm** đúng 1 cụm từ khóa duy nhất cần tô màu nhấn.
```

---

### Prompt 04: Chuyển kịch bản chữ thành Bảng Phân Cảnh (Shot List) 3 cột cho Editor
*(Dùng để biến kịch bản thành bảng hướng dẫn quay và dựng ngay trên Premiere/CapCut)*

```text
Dưới đây là lời thoại kịch bản 35 giây đã chốt của tôi:
"""
[Dán lời thoại đã chốt vào đây]
"""

Hãy chuyển kịch bản này thành bảng sản xuất chi tiết gồm 5 cột theo đúng 4 nhịp (00:00–00:03 Hook | 00:03–00:10 Proof | 00:10–00:32 Body | 00:32–00:40 Close & CTA):
- Cột 1: Mốc thời gian (Chia nhỏ mỗi cảnh từ 2–4 giây).
- Cột 2: Loại cảnh quay (Ghi rõ đoạn nào là A-roll nói trực diện, đoạn nào là B-roll quay cận thao tác, đoạn nào là Quay màn hình hoặc tạo ảnh/video bổ trợ bằng AI).
- Cột 3: Chi tiết hình ảnh & Chuyển động trên khung hình.
- Cột 4: Text trên màn hình (Ngắn gọn dưới 8 chữ, chỉ in đậm 1 cụm từ khóa duy nhất mỗi khung hình).
- Cột 5: Lời thoại tương ứng & Gợi ý hiệu ứng âm thanh (SFX vừa đủ, không lạm dụng).
```

---

### Prompt 05: Kiểm tra lỗ hổng thông điệp & độ khớp CTA trước khi quay
*(Dùng như một "người duyệt bài" để tránh quay xong mới phát hiện kịch bản bị lan man)*

```text
Hãy đóng vai một biên tập viên khắt khe kiểm tra lại kịch bản video ngắn dưới đây giúp tôi:
- Tệp người xem mục tiêu: [Điền tệp]
- Hành động mong muốn sau khi xem (CTA): [Lưu bài / Bấm vào bio nhận tài liệu / Nhắn tin hỏi dịch vụ]
- Bản thảo kịch bản:
"""
[Dán kịch bản vào đây]
"""

Hãy chấm điểm và chỉ thẳng cho tôi 4 điểm sau:
1. Trong 3 giây đầu tiên, người xem thuộc tệp mục tiêu có nhận ra ngay video này dành cho họ không? Nếu chưa, hãy sửa lại câu đầu.
2. Kịch bản này có đang vô tình nhồi nhiều hơn 1 chủ đề không? Hãy gạch bỏ những câu làm loãng thông điệp chính.
3. Đoạn nào đang nói lý thuyết suông mà thiếu bằng chứng hình ảnh (Proof)? Hãy gợi ý cảnh chứng minh cụ thể để đắp vào đoạn đó.
4. Câu CTA ở 5 giây cuối đã nối mượt từ phần thân bài sang chưa, hay đang bị gượng ép?
```

---

## PHẦN 4: MẪU BRIEF & SHOT LIST 1 TRANG TRƯỚC KHI BẤM MÁY

> Bạn có thể sao chép bảng dưới đây ra một trang Notion hoặc in ra giấy A4 đặt cạnh máy quay / gửi cho khách hàng điền trong 2 phút trước khi bắt đầu dự án.

### 4A. Phiếu Chốt Đề Bài 3 Câu Hỏi (Dành cho Khách hàng gửi yêu cầu Edit hoặc Creator tự lên khung)

| Hạng mục | Nội dung trả lời ngắn gọn (Không quá 2 dòng mỗi ô) |
| :--- | :--- |
| **Tên video / Mã dự án:** | Ví dụ: `Video 08 — Phân tích quy trình hậu kỳ 5 bước` |
| **Câu hỏi 1: Người xem chính của video này là ai?** *(Họ đang ở hoàn cảnh nào khi lướt thấy video?)* | `....................................................................................................` |
| **Câu hỏi 2: Sau 35 giây, họ cần nhớ đúng 1 câu kết luận gì?** *(Chỉ 1 ý duy nhất)* | `....................................................................................................` |
| **Câu hỏi 3: Hành động tiếp theo (CTA) sau khi xem xong là gì?** *(Chọn đúng 1 ô)* | `[ ]` Lưu bài / Theo dõi kênh *(Nhận biết)*<br>`[ ]` Bấm vào Bio lấy Starter Kit *(Thu thập Lead)*<br>`[ ]` Nhắn từ khóa `"EDIT"` để trao đổi dịch vụ *(Chuyển đổi Dịch vụ)*<br>`[ ]` Bấm link Bio tìm hiểu lộ trình / công cụ *(Zero To AI / Xưởng Media)* |
| **Bằng chứng thực tế (Proof) sẽ đưa lên màn hình là gì?** | `[ ]` Cảnh Before/After &nbsp;&nbsp; `[ ]` Quay màn hình Timeline/Số liệu &nbsp;&nbsp; `[ ]` Cảnh test sản phẩm cận cảnh |
| **Nguồn nguyên liệu đầu vào hiện có:** | - Link thư mục Footage quay thật (A-roll / B-roll): `..........................................`<br>- Những cảnh bị thiếu cần tạo bổ sung bằng đồ họa / AI: `..................................` |

---

### 4B. Bảng Shot List Thực Thi Nhanh Trước Khi Bấm Máy (Tối đa 6–8 cảnh cho video 35s)

| STT Cảnh | Nhịp kịch bản | Loại cảnh (`A-roll` / `B-roll` / `Screen` / `AI`) | Mô tả khung hình cần quay / chuẩn bị | Từ khóa duy nhất cần nhấn trên màn hình | Đã có file? |
| :---: | :--- | :---: | :--- | :--- | :---: |
| **01** | `00:00–00:03` (Hook) | `A-roll + Split` | Cảnh kết quả cuối đặt cạnh cảnh gốc bị lỗi | **từ khóa mở đầu** | `[ ]` |
| **02** | `00:03–00:10` (Proof) | `Screen / Cận` | Khoanh đỏ điểm lỗi cụ thể trên màn hình / sản phẩm | **nguyên nhân chính** | `[ ]` |
| **03** | `00:10–00:17` (Bước 1) | `A-roll + B-roll` | Nói trực diện câu dẫn + Cắt sang thao tác Bước 1 | **bước thứ nhất** | `[ ]` |
| **04** | `00:17–00:25` (Bước 2) | `Screen / AI` | Chiếu thao tác Bước 2 hoặc visual minh họa từ AI | **bước thứ hai** | `[ ]` |
| **05** | `00:25–00:32` (Bước 3) | `B-roll kết quả` | Chạy mượt kết quả sau khi đã áp dụng đủ các bước | **bước thứ ba** | `[ ]` |
| **06** | `00:32–00:38` (Close/CTA) | `A-roll + Card` | Nói câu chốt + Hiển thị bảng tóm tắt & hướng dẫn CTA | **hành động tiếp theo** | `[ ]` |

---

## PHẦN 5: CHECKLIST 10 ĐIỂM KIỂM DUYỆT (QA) TRƯỚC KHI XUẤT FILE & BẢNG ĐO KPI 12 VIDEO

### 5.1. Checklist 10 Điểm Kiểm Duyệt Bản Dựng Video 9:16 (`1080x1920`)
*(Đánh dấu `[x]` đủ 10 điểm trước khi bấm Export bàn giao cho khách hoặc đăng lên kênh)*

- [ ] **01. Cắt sát 0.5 giây đầu tiên:** Đã cắt bỏ hoàn toàn đoạn lấy hơi, chớp mắt hoặc khoảng lặng ở frame đầu tiên (`00:00`). Mở video ra là có tiếng nói và chuyển động ngay.
- [ ] **02. Hook 3 giây rõ vấn đề/kết quả:** Nghe lại 3 giây đầu tiên khi không nhìn hình — đã biết ngay video này giải quyết chuyện gì chưa?
- [ ] **03. Bằng chứng xuất hiện trước giây thứ 10:** Từ giây `00:03` đến `00:10` đã có hình ảnh chứng minh thực tế (Before/After, màn hình thao tác, sản phẩm thật) thay vì chỉ có 1 góc ngồi nói suông.
- [ ] **04. Quy tắc "1 Khung hình = 1 Từ khóa nhấn":** Rà soát toàn bộ chữ trên màn hình (On-screen Text) — viết hoa chữ cái đầu dòng, không có khung hình nào tô màu lòe loẹt 3–4 chữ cùng lúc.
- [ ] **05. Vùng an toàn hiển thị (Safe Zone 9:16):** Chữ phụ đề và bảng đồ họa không nằm sát 15% cạnh trên, 25% cạnh dưới (nơi chứa caption TikTok/Reels) và 15% cạnh phải (nơi chứa cột nút Tim/Lưu/Chia sẻ).
- [ ] **06. Nhịp thay đổi thị giác mỗi 2–4 giây:** Không có đoạn nào giữ nguyên một khung hình tĩnh quá 5 giây mà không có thay đổi tiêu cự, chèn B-roll hoặc điểm nhấn đồ họa.
- [ ] **07. Tính ăn nhập của AI Asset (nếu có dùng AI):** Các cảnh ảnh/video tạo bằng AI đã được chỉnh lại nhiệt độ màu và độ tương phản để tiệp với cảnh quay thật, không bị cảm giác "nhựa" hoặc lạc tông.
- [ ] **08. Tỷ lệ âm lượng Giọng nói vs Nhạc nền & SFX:** Giọng nói (Voice) đạt ngưỡng chuẩn (`-6dB` đến `-3dB`), rõ chữ; nhạc nền nằm dưới mức `-22dB` đến `-18dB`; tiếng động SFX vừa đủ hỗ trợ điểm nhấn, không chát chúa.
- [ ] **09. Kiểm tra chính tả & thuật ngữ:** Đã đọc soát một lượt từ đầu đến cuối toàn bộ chữ trên màn hình để không sót lỗi đánh máy.
- [ ] **10. Đúng 1 CTA duy nhất ở 5 giây cuối:** Lời kêu gọi hành động ở cuối video khớp 100% với mục tiêu của bài viết và caption đi kèm (không vừa bảo lưu bài, vừa bảo mua hàng, vừa bảo vào nhóm).

---

### 5.2. Bảng Theo Dõi KPI 12 Video (1 Sprint = 3 Tuần)

> **Hướng dẫn đọc số liệu sau mỗi 12 video:**
> - **Giữ chân 3 giây đầu (`Hook 3s %`):** Dưới `55%` → Cần sửa lại câu mở đầu và hình ảnh 3 giây đầu. Đạt `> 65%` → Hook tốt.
> - **Tỷ lệ Lưu & Chia sẻ (`(Save + Share) / View`):** Dưới `1.5%` → Nội dung chưa đủ tính ứng dụng hoặc thiếu bảng tóm tắt cuối video. Đạt `> 3%` → Nội dung có giá trị lưu trữ cao.
> - **Lượt vào Hồ sơ / Click Bio (`Profile Visit`):** Đo trực tiếp sức thuyết phục để chuyển đổi người xem thành khách hàng hoặc người nhận tài liệu.

| Thứ tự | Mã Video | Pillar (`P1/P2/P3/P4`) | Chủ đề / Format thử nghiệm | Lượt xem (Sau 7 ngày) | Giữ chân 3s (`%`) | Thời lượng xem TB (`s`) | Tỷ lệ Lưu + Chia sẻ (`%`) | Lượt vào Hồ sơ / Click Bio | Tin nhắn / Lead thu về | Quyết định sau Sprint (`Giữ` / `Sửa` / `Bỏ`) |
| :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **01** | `C001` | `P1` | *Ví dụ: Sửa 3 giây đầu* | `...` | `...%` | `...s` | `...%` | `...` | `...` | `[ ] Giữ [ ] Sửa [ ] Bỏ` |
| **02** | `C022` | `P2` | *Ví dụ: Before/After nhịp cắt* | `...` | `...%` | `...s` | `...%` | `...` | `...` | `[ ] Giữ [ ] Sửa [ ] Bỏ` |
| **03** | `C040` | `P3` | *Ví dụ: AI làm thô vs Editor làm tinh* | `...` | `...%` | `...s` | `...%` | `...` | `...` | `[ ] Giữ [ ] Sửa [ ] Bỏ` |
| **04** | `...` | `...` | `...` | `...` | `...%` | `...s` | `...%` | `...` | `...` | `[ ] Giữ [ ] Sửa [ ] Bỏ` |
| **05** | `...` | `...` | `...` | `...` | `...%` | `...s` | `...%` | `...` | `...` | `[ ] Giữ [ ] Sửa [ ] Bỏ` |
| **06** | `...` | `...` | `...` | `...` | `...%` | `...s` | `...%` | `...` | `...` | `[ ] Giữ [ ] Sửa [ ] Bỏ` |
| **07** | `...` | `...` | `...` | `...` | `...%` | `...s` | `...%` | `...` | `...` | `[ ] Giữ [ ] Sửa [ ] Bỏ` |
| **08** | `...` | `...` | `...` | `...` | `...%` | `...s` | `...%` | `...` | `...` | `[ ] Giữ [ ] Sửa [ ] Bỏ` |
| **09** | `...` | `...` | `...` | `...` | `...%` | `...s` | `...%` | `...` | `...` | `[ ] Giữ [ ] Sửa [ ] Bỏ` |
| **10** | `...` | `...` | `...` | `...` | `...%` | `...s` | `...%` | `...` | `...` | `[ ] Giữ [ ] Sửa [ ] Bỏ` |
| **11** | `...` | `...` | `...` | `...` | `...%` | `...s` | `...%` | `...` | `...` | `[ ] Giữ [ ] Sửa [ ] Bỏ` |
| **12** | `...` | `...` | `...` | `...` | `...%` | `...s` | `...%` | `...` | `...` | `[ ] Giữ [ ] Sửa [ ] Bỏ` |
| **TỔNG / TB** | **12 bài** | **Đủ 4P** | **Chốt tối đa 2 Format thắng** | **`...`** | **`...%`** | **`...s`** | **`...%`** | **`...`** | **`...`** | **Chốt kế hoạch Sprint tới** |

---

## BƯỚC TIẾP THEO CÙNG THÀNH (`DỰNG CÓ CHỦ ĐÍCH`)

Sau khi áp dụng bộ **Starter Kit v1** này vào kênh của bạn, tùy thuộc vào nhu cầu thực tế hiện tại, bạn có thể kết nối tiếp với mình qua 3 hướng dưới đây:

1. **Bạn có sẵn footage quay hoặc ý tưởng nhưng cần người đồng hành dựng video rõ thông điệp bán hàng:**  
   👉 Nhắn trực tiếp cho mình chữ **`"EDIT"`** kèm mục tiêu kênh của bạn để mình gửi quy trình phối hợp 5 bước.
2. **Bạn muốn học cách ứng dụng AI vào quy trình làm nội dung và video từ con số 0 theo lộ trình bài bản:**  
   👉 Xem mục **`Zero To AI`** tại đường link trên bio của mình *(link giới thiệu có gắn affiliate minh bạch)*.
3. **Bạn muốn trải nghiệm công cụ tạo hình ảnh & video B-roll đa model trên cùng một giao diện như các bài test trên kênh:**  
   👉 Xem mục **`Xưởng Media`** tại đường link trên bio của mình *(link dùng thử có gắn affiliate minh bạch)*.

<!-- ===== /file: personal-brand-video-engine/references/05_ASSET/STARTER_KIT_V1_DUNG_CO_CHU_DICH.md ===== -->

<!-- ===== file: personal-brand-video-engine/references/06_KPI_VA_CASE_STUDY/KHUNG_3_CASE_STUDY_VA_BAO_CAO_SPRINT.md ===== -->

# Khung 3 Case Study Năng Lực (`DA-03`) & Mẫu Báo Cáo 4 Sprint (`DA-06`)

> **Mục tiêu:** Cung cấp sẵn bộ khung chuẩn để Thành điền dữ liệu thật ở các mốc kiểm tra trong Lịch 90 ngày:
> - **3 Case Study (`DA-03`):** Hạn hoàn thành Case 1 (`29/11/2026`), Case 2 (`13/12/2026`), Case 3 (`27/12/2026`).
> - **4 Báo cáo Sprint (`DA-06`):** Hạn review sau mỗi 12 video vào `15/11/2026`, `06/12/2026`, `27/12/2026` và `17/01/2027`.

---

## PHẦN 1: BỘ KHUNG 3 CASE STUDY NĂNG LỰC (`DA-03`)

> **Quy tắc bắt buộc trước khi đăng Case Study:**
> 1. Phải có xác nhận quyền công bố footage từ khách hàng (hoặc dùng dự án tự thực hiện / ẩn danh thông tin nhạy cảm).
> 2. Không nói chung chung "mình đã dựng video này đẹp hơn"; phải chỉ ra **3 quyết định dựng gắn với mục tiêu Marketing** và kết quả đo được.

### 📁 CASE STUDY 01 (Mốc hoàn thành: 29/11/2026) — Sửa Cấu Trúc & 3 Giây Đầu Để Giữ Chân Người Xem
- **Tên dự án / Khách hàng:** `[Điền tên kênh hoặc lĩnh vực ẩn danh, ví dụ: Kênh thương hiệu cá nhân ngành Tư vấn / Chủ shop Thời trang]`
- **Vấn đề ban đầu (Before):**
  - Footage gốc dài `[X]` phút, mở đầu bằng 6 giây chào hỏi và giới thiệu dài dòng.
  - Nhiều ý bị trộn lẫn trong cùng 1 video khiến người xem rời đi ở giây thứ 3–4.
- **Mục tiêu của bản dựng mới:**
  - Tăng tỷ lệ giữ chân 3 giây đầu (3s Retention) và làm nổi bật duy nhất 1 thông điệp cốt lõi.
- **3 Quyết định "Dựng Có Chủ Đích":**
  1. **Marketing (Cấu trúc):** Cắt bỏ 100% phần mở đầu xã giao; bốc câu kết luận đắt giá nhất ở giây `[X]` đẩy lên giây `00:00`.
  2. **Editing (Nhịp & Hình):** Cắt bỏ khoảng thở thừa trên waveform; đặt 1 cú đổi góc khung hình (100% → 115% scale) và B-roll bằng chứng ở giây thứ 4.
  3. **Subtitle & CTA:** Chuẩn hóa phụ đề trong vùng an toàn, chỉ tô màu 1 cụm từ khóa chính trên mỗi câu; đổi CTA cuối thành 1 hành động cụ thể.
- **Bằng chứng hình ảnh cần chụp/quay màn hình:**
  - [ ] Ảnh chụp màn hình Timeline trước và sau khi sắp xếp lại khối màu.
  - [ ] Video Split-screen 5 giây đầu (Bản cũ vs Bản mới).
  - [ ] Chỉ số giữ chân người xem hoặc phản hồi thật của khách hàng.

---

### 📁 CASE STUDY 02 (Mốc hoàn thành: 13/12/2026) — Kết Hợp AI Làm Thô & Editor Làm Tinh Cho Video Sản Phẩm/Dịch Vụ
- **Tên dự án / Khách hàng:** `[Điền tên dự án / Sản phẩm thử nghiệm]`
- **Vấn đề ban đầu (Before):**
  - Khách hàng / Creator thiếu cảnh quay B-roll minh họa và mất quá nhiều thời gian viết kịch bản từ brief thô.
- **Mục tiêu của bản dựng mới:**
  - Rút ngắn thời gian chuẩn bị tiền kỳ bằng AI nhưng vẫn giữ độ thật, cảm xúc và uy tín của người nói.
- **3 Quyết định "Dựng Có Chủ Đích":**
  1. **AI làm thô (Tiền kỳ & Asset):** Dùng AI lọc từ brief ra 1 góc thông điệp duy nhất + tạo `[X]` cảnh B-roll/asset sản phẩm bổ trợ qua Xưởng Media.
  2. **Editor làm tinh (Hậu kỳ Premiere/AE):** Cắt bỏ các frame AI bị lỗi chuyển động (artefact), chỉnh lại màu sắc đồng bộ với footage quay thật.
  3. **Âm thanh & Nhịp nghỉ:** Đặt khoảng dừng `0.5s` trước câu chốt giá trị và cân chỉnh giọng nói ở mức `-16 LUFS`, nhạc nền thấp hơn giọng `15 LU`.
- **Bằng chứng hình ảnh cần chụp/quay màn hình:**
  - [ ] Màn hình Prompt đầu vào & Output AI gốc (chỉ rõ điểm AI làm chưa tốt).
  - [ ] Màn hình Premiere/AE sau khi Editor cắt gọt, thêm text animation và sound design.
  - [ ] Thời gian tiết kiệm được + Kết quả video hoàn chỉnh.

---

### 📁 CASE STUDY 03 (Mốc hoàn thành: 27/12/2026) — Tối Ưu Video Chuyển Đổi (Từ Lượt Xem Sang Tin Nhắn/Lead)
- **Tên dự án / Khách hàng:** `[Điền tên dự án dịch vụ hoặc video chuyển đổi tốt nhất trên kênh Thành]`
- **Vấn đề ban đầu (Before):**
  - Video có lượt xem nhưng người xem không bấm vào hồ sơ hoặc không nhắn tin/để lại lead.
- **Mục tiêu của bản dựng mới:**
  - Thiết kế lại mạch thuyết phục (Hook → Proof → 1 Claim → CTA giảm rào cản) để tạo ra tin nhắn hỏi dịch vụ hoặc lượt tải tài liệu.
- **3 Quyết định "Dựng Có Chủ Đích":**
  1. **Gọi đúng tệp ngay câu đầu:** Thay hook đại trà bằng câu nêu trúng tình huống của tệp khách hàng mục tiêu.
  2. **Đưa bằng chứng lên màn hình sớm:** Hiển thị kết quả thật / quy trình thật ở giây thứ 8–15 thay vì chỉ nói miệng.
  3. **Sửa CTA cuối video:** Chuyển từ *"Follow kênh nhé"* sang *"Nhắn chữ EDIT kèm mục tiêu của bạn để mình gửi 3 góp ý trước khi dựng"*.
- **Bằng chứng hình ảnh cần chụp/quay màn hình:**
  - [ ] So sánh kịch bản CTA cũ vs mới.
  - [ ] Số liệu Profile Visit, Link Click và số tin nhắn/lead thu được (ẩn tên riêng khách hàng).

---

## PHẦN 2: MẪU BÁO CÁO REVIEW SAU MỖI SPRINT (12 VIDEO / 3 TUẦN — `DA-06`)

> Sao chép bảng dưới đây vào cuối Tuần 3 (`15/11/2026`), Tuần 6 (`06/12/2026`), Tuần 9 (`27/12/2026`) và Tuần 12 (`17/01/2027`).
> **Nguyên tắc vàng:** Chỉ so sánh với **trung vị (median) của chính kênh mình**, không kết luận chỉ từ lượt xem, và mỗi Sprint chỉ thay đổi **ĐÚNG 1 BIẾN LỚN**.

### 📊 BẢNG TỔNG HỢP SPRINT `[1 / 2 / 3 / 4]`
- **Giai đoạn:** `Từ ngày .../.../2026 đến .../.../2026`
- **Số video đã đăng / Mục tiêu:** `... / 12 video` (Tỷ lệ đúng lịch: `...%`)
- **Trung vị kênh trong Sprint này:**
  - Views trung vị: `...`
  - Giữ 3 giây đầu (3s Retention) trung vị: `...%`
  - Thời gian xem trung bình (Avg Watch Time): `... giây`
  - Tỷ lệ Lưu + Chia sẻ (Save + Share rate): `...%`
  - Lượt ghé thăm hồ sơ (Profile Visits): `...`
  - Lượt bấm link bio / Lead / DM dịch vụ: `...`

### 🔍 8 CÂU HỎI QUYẾT ĐỊNH SAU 12 VIDEO
| STT | Hạng mục phân tích | Dữ liệu thực tế (Ghi mã C00x) | Quyết định cho Sprint tiếp theo |
| :---: | :--- | :--- | :--- |
| 1 | **3 video có tỷ lệ giữ chân 3 giây (Hook) tốt nhất** | 1. `C0...` (`...%`)<br>2. `C0...` (`...%`)<br>3. `C0...` (`...%`) | Nhân bản cấu trúc mở đầu và cách đặt hình 3 giây đầu của 3 bài này. |
| 2 | **3 video có tỷ lệ Lưu & Chia sẻ (Save/Share) cao nhất** | 1. `C0...` (`...%`)<br>2. `C0...` (`...%`)<br>3. `C0...` (`...%`) | Phát triển thành Series cố định hàng tuần và gắn CTA nhận Starter Kit. |
| 3 | **Video kéo nhiều lượt vào trang cá nhân (Profile Visit) nhất** | `C0...` (`... lượt`) | Kiểm tra lại 3 video ghim và Bio xem đã khớp với chủ đề video này chưa. |
| 4 | **Video tạo ra nhiều Lead / DM hỏi dịch vụ hoặc click link nhất** | `C0...` (`... lead/DM`) | Giữ nguyên công thức CTA và ngữ cảnh dẫn chuyện của bài này. |
| 5 | **Pillar nào đang tạo cơ hội kinh doanh thực tế tốt nhất?** | `P1 / P2 / P3 / P4` | Giữ hoặc tăng nhẹ tỷ trọng ở Sprint sau nếu chất lượng vẫn đảm bảo. |
| 6 | **Format nào nằm dưới mức trung vị kênh 3 lần liên tiếp?** | `[Ghi tên Format & mã video]` | **Dừng** format đó hoặc thay toàn bộ cách mở đầu trong 3 giây đầu. |
| 7 | **5 câu hỏi lặp lại nhiều nhất từ bình luận/tin nhắn khán giả (`DA-02`)** | 1. ...<br>2. ...<br>3. ... | Đưa trực tiếp thành câu Hook mở đầu cho các video ở Sprint tới. |
| 8 | **MỘT thay đổi lớn duy nhất áp dụng cho Sprint tiếp theo** | `[Chỉ ghi 1 biến duy nhất, ví dụ: Đổi góc quay split-screen 3s đầu / Đổi cách gọi tên tệp chủ shop]` | Theo dõi kết quả của thay đổi này sau 12 video kế tiếp. |

<!-- ===== /file: personal-brand-video-engine/references/06_KPI_VA_CASE_STUDY/KHUNG_3_CASE_STUDY_VA_BAO_CAO_SPRINT.md ===== -->

<!-- ===== file: personal-brand-video-engine/references/HUONG_DAN_SU_DUNG_VA_CHAY_NGAM.md ===== -->

# HƯỚNG DẪN VẬN HÀNH HỆ THỐNG ĐĂNG BÀI TỰ ĐỘNG CHẠY NGẦM (`DBTD`)

> **Thư mục gốc:** `/media/vmiz/Over Powers/THÀNH V/THCN thành/THUONG_HIEU_CA_NHAN_THANH_90_NGAY/DBTD`

---

## 1. CẤU TRÚC THƯ MỤC ĐÃ ĐƯỢC KHỞI TẠO SẴN TRONG `DBTD`

Toàn bộ **48 bài lịch chính thức (12 tuần)**, **3 bài ghim** và **12 bài dự phòng/case study** đã được tạo sẵn thư mục theo đúng ngày và mã bài:

- `00_PINNED_VIDEOS/` (`20261025_PIN01`, `20261025_PIN02`, `20261025_PIN03`)
- `01_TUAN_01_2610_3110/`
  - `20261026_C001/` (Thứ Hai 26/10/2026)
  - `20261027_C022/` (Thứ Ba 27/10/2026)
  - `20261029_C040/` (Thứ Năm 29/10/2026)
  - `20261031_C055/` (Thứ Bảy 31/10/2026)
- `02_TUAN_02_0211_0711/` ... đến `12_TUAN_12_1101_1601/`
- `13_DU_PHONG_VA_CASE_STUDY/` (`DUPHONG_C018` ... `DUPHONG_C060`)
- `_he_thong_bot/` (Chứa bộ điều khiển trình duyệt chạy ngầm 100%)

> 💡 **Mẹo:** Trong mỗi thư mục bài đăng (ví dụ `20261026_C001`), đã có sẵn file **`THONG_TIN_BAI_DANG.txt`** ghi rõ tên file cần đặt và toàn bộ Caption TikTok + Bài đăng Facebook của đúng ngày hôm đó.

---

## 2. QUY TẮC ĐẶT TÊN FILE CỐ ĐỊNH ĐỂ BOT TỰ NHẬN DIỆN

Khi xuất video hoặc ảnh xong cho ngày nào, bạn chỉ cần bỏ vào thư mục của ngày đó theo công thức:

- **Video chính (TikTok / FB Reels / Fanpage):** `[Mã_Thư_Mục]_VIDEO.mp4`
  - Ví dụ ngày 26/10 (`C001`): `20261026_C001_VIDEO.mp4`
- **Ảnh bìa Video (Thumbnail):** `[Mã_Thư_Mục]_THUMB.png` (hoặc `.jpg`)
  - Ví dụ: `20261026_C001_THUMB.png`
- **Ảnh bài viết Facebook / Fanpage (1 ảnh hoặc nhiều ảnh):** `[Mã_Thư_Mục]_IMG_01.png`, `[Mã_Thư_Mục]_IMG_02.png`...
  - Ví dụ: `20261026_C001_IMG_01.png`, `20261026_C001_IMG_02.png`

---

## 3. CÁCH CHẠY NGẦM 100% KHÔNG BẬT CỬA SỔ TRÌNH DUYỆT

Hệ thống sử dụng **2 lớp ẩn cửa sổ**:
1. **Lớp trình duyệt (`--headless=new`):** Chrome tự mở trang, gắn file và bấm nút Đăng hoàn toàn trong bộ nhớ RAM mà không vẽ giao diện ra màn hình.
2. **Lớp hệ điều hành (`2_CHAY_NGAM_KHONG_CUA_SO.vbs` với cờ `vbHide = 0`):** Ẩn luôn cả cửa sổ đen Command Prompt (CMD). Bạn đang dựng Premiere/After Effects sẽ không bao giờ bị một cửa sổ nào nhảy lên làm phiền.

### 3 Bước kích hoạt:
1. **Bước 1 (Chỉ làm 1 lần duy nhất):** Mở thư mục `_he_thong_bot`, nhấp đúp vào **`1_DANG_NHAP_LAN_DAU.bat`**.
   - Một cửa sổ Chrome riêng sẽ hiện lên để bạn đăng nhập sẵn **TikTok** và **Facebook**.
   - Đăng nhập xong, bạn tắt cửa sổ Chrome đó đi. Toàn bộ phiên đăng nhập đã được lưu cứng vào `_he_thong_bot/browser_profile`.
2. **Bước 2:** Mở file `_he_thong_bot/config.json`, điền đường dẫn URL Fanpage của bạn vào dòng `"fanpageUrl"`.
3. **Bước 3 (Bật tự động chạy ngầm):** Nhấp đúp vào **`3_CAI_LICH_TU_DONG_WINDOWS.bat`**.
   - Windows sẽ tự động kiểm tra lịch ngầm mỗi 15 phút và tự đăng bài khi tới đúng Ngày + Giờ mà không hiện bất kỳ cửa sổ nào.
   - Mọi kết quả đều được ghi lại trong `_he_thong_bot/logs/autopost.log`.

---

## 4. CẬP NHẬT LÊN GOOGLE SHEET CỦA BẠN

Trong thư mục `DBTD` đã có sẵn 2 file bảng tính đã điền đủ 60 kịch bản & caption:
1. **`He-thong-content-ca-nhan-Thanh-AutoPost.xlsx`**: File Excel đầy đủ 9 tab (đã sửa lại tab `Lịch sản xuất` chuẩn 4 Pillar và thêm tab mới **`Lịch Đăng Tự Động`**).
2. **`Lich_Dang_Tu_Dong_Import_GGSheet.csv`**: Bạn có thể mở Google Sheet hiện tại của bạn $\rightarrow$ Bấm **Tệp (File) > Nhập (Import) > Tải lên (Upload)** $\rightarrow$ Chọn file CSV này và chọn *"Chèn trang tính mới (Insert new sheet)"* là có ngay tab `Lịch Đăng Tự Động` trên Google Sheet!

<!-- ===== /file: personal-brand-video-engine/references/HUONG_DAN_SU_DUNG_VA_CHAY_NGAM.md ===== -->

<!-- ===== file: personal-brand-video-engine/references/NGAY_01_DINH_VI.md ===== -->

# Ngày 01 — Định vị thương hiệu cá nhân

Ngày thực hiện: 21/10/2026

## Kết quả được chọn cho 90 ngày thử nghiệm

**Định vị cốt lõi**  
Thành giúp creator và thương hiệu cá nhân biến ý tưởng thành video có chủ đích bằng tư duy marketing, kỹ năng dựng và AI.

**Signature**  
Dựng Có Chủ Đích.

**Mô tả vai trò**  
Video Editor | Marketing Mindset | AI Workflow

**Giới thiệu 15 giây**  
Mình là Thành, video editor có nền tảng marketing. Mình chia sẻ cách dựng video rõ thông điệp và ứng dụng AI đúng chỗ, để mỗi video không chỉ đẹp mà còn có mục tiêu.

## Ba phiên bản bio thử nghiệm

1. **Bio tổng quát:** Video Editor | Marketing Mindset | AI Workflow. Chia sẻ cách dựng video có chủ đích bằng marketing và AI.
2. **Bio hướng khách hàng:** Giúp creator biến ý tưởng thành video rõ thông điệp. Edit • Marketing • AI workflow.
3. **Bio hành trình:** Học và làm Premiere, After Effects, AI. Mỗi tuần một thử nghiệm dựng có chủ đích.

## Ba phương án đã cân nhắc

1. **Kết quả cho khách hàng:** Thành giúp creator và thương hiệu cá nhân biến ý tưởng thành video có chủ đích bằng tư duy marketing, kỹ năng dựng và AI.
2. **Vai trò chuyên môn:** Editor có nền tảng marketing, chia sẻ cách làm video rõ thông điệp, gọn quy trình và có khả năng chuyển đổi.
3. **Hành trình học công khai:** Từ brief đến video: Thành thử nghiệm Premiere, After Effects và AI để dựng nhanh hơn mà không đánh mất tư duy marketing.

Phương án 1 được chọn vì bắt đầu từ giá trị cho người xem, kết nối đủ Marketing — Editing — AI và không phóng đại thâm niên.

## Tệp khán giả ưu tiên

- **Tệp chính:** Creator và người xây thương hiệu cá nhân mới bắt đầu, đã có ý tưởng nhưng chưa biết biến thành video ngắn rõ thông điệp và duy trì đều.
- **Tệp phụ:** Chủ doanh nghiệp nhỏ hoặc đội marketing cần quy trình video ngắn gọn hơn, có thể thuê dựng hoặc ứng dụng AI vào khâu nội dung và hậu kỳ.
- **Vấn đề chung:** Video có thể đẹp nhưng thiếu mục tiêu, quy trình tốn thời gian và chưa biết dùng AI đúng chỗ.
- **Ba hướng doanh thu hiện hữu:** Dịch vụ edit/media; hoa hồng/affiliate Zero To AI; affiliate Xưởng Media. Sản phẩm tri thức cá nhân chỉ triển khai sau khi có dữ liệu và case thực tế.

## Ba mục tiêu đo được trong 90 ngày

1. **Nội dung:** Xuất bản tối thiểu 36 video ngắn trong 12 tuần, tương ứng 3 video bắt buộc mỗi tuần; mục tiêu mở rộng là 48 video bằng video linh hoạt. Tối thiểu 85% video bắt buộc phải đúng lịch.
2. **Bằng chứng năng lực:** Hoàn thành 3 case study, 1 Starter Kit và 4 báo cáo sprint. Sau mỗi sprint giữ tối đa 2 series để thử tiếp; cuối 90 ngày chọn 3 format cốt lõi dựa trên watch time, save/share, profile visit, lead và phản hồi thật.
3. **Cơ hội kinh doanh:** Tạo tối thiểu 12 cuộc trao đổi đủ điều kiện, nhận ít nhất 3 brief dịch vụ và có tối thiểu 30 lượt click được theo dõi tới Zero To AI hoặc Xưởng Media.

**Định nghĩa đo lường**

- Cuộc trao đổi đủ điều kiện: đúng tệp và có nhu cầu, kèm mốc thời gian hoặc ngân sách dự kiến.
- Brief hợp lệ: có mục tiêu, đầu vào, đầu ra, deadline và phạm vi mong đợi.
- Click hợp lệ: đo bằng UTM hoặc công cụ theo dõi link, loại lượt test nội bộ.
- Case khách hàng: chỉ công bố khi có quyền sử dụng và kết quả được xác thực; nếu chưa có, ghi rõ là case kỹ thuật hoặc case quy trình.

## Nguyên tắc giọng tạm thời

Đây là nguyên tắc thử nghiệm, chưa phải hồ sơ giọng nói cố định. Chỉ khóa voice profile sau khi có 5–20 video thật.

- Nói trực tiếp, cụ thể, dùng ví dụ hoặc hình ảnh chứng minh.
- Xưng “mình”, gọi người xem theo đúng ngữ cảnh; tránh giọng chuyên gia toàn năng.
- Một video chỉ có một thông điệp, một tệp người xem và một CTA.
- Ưu tiên before/after, timeline, input/output và quyết định dựng thật.
- Không hứa AI thay thế editor; luôn chỉ rõ phần AI làm thô và phần con người chỉnh tinh.
- Tránh các cụm sáo như “bí quyết bùng nổ”, “thay đổi cuộc đời”, “AI làm tất cả”.

## Tiêu chí hoàn thành Ngày 01

- [x] Có một câu định vị nêu rõ tệp, vấn đề và giá trị.
- [x] Có signature và mô tả vai trò nhất quán.
- [x] Có bài giới thiệu nói được trong khoảng 15 giây.
- [x] Có ba phiên bản bio để đồng bộ và thử nghiệm.
- [x] Có ba mục tiêu 90 ngày đo được.
- [x] Có cấu trúc thư mục dự án để bắt đầu sản xuất.

## Ruling

Chọn định vị theo kết quả cho khách hàng thay vì tự gọi mình là chuyên gia. Chi phí nếu định vị chưa khớp là phải điều chỉnh sau Sprint 1; đổi lại, nó trung thực với kinh nghiệm hiện tại và vẫn mở đường cho dịch vụ, khóa học và affiliate.

<!-- ===== /file: personal-brand-video-engine/references/NGAY_01_DINH_VI.md ===== -->

<!-- ===== file: personal-brand-video-engine/references/NGAY_02_HO_SO_KENH_VA_3_VIDEO_GHIM.md ===== -->

# Ngày 02 — Đồng Bộ Hồ Sơ Kênh & Kịch Bản 3 Video Ghim

> **Mục tiêu:** Thiết lập mặt tiền đồng nhất trên **TikTok** (kênh thử nghiệm hook & khám phá) và **Facebook** (kênh xây dựng niềm tin, quan hệ & chuyển đổi), kèm kịch bản sản xuất **3 Video Ghim** giúp khách hàng và người xem mới hiểu ngay Thành là ai, làm được gì và bắt đầu từ đâu.

---

## 1. BỘ HỒ SƠ ĐỒNG NHẤT (PROFILE & BIO)

### A. Tên & Nhận diện cơ bản
- **Tên hiển thị (Display Name):** `Thành — Dựng Có Chủ Đích`
- **Username gợi ý (TikTok / FB URL):** `@thanh.dungcochudich` hoặc `@thanhmediamkt`
- **Ảnh đại diện (Avatar):** Ảnh chụp nửa người rõ mặt, ánh sáng sạch, phông nền gọn (góc bàn làm việc có màn hình timeline mờ phía sau), trang phục đơn sắc tối giản.
- **Màu sắc & Phụ đề nhận diện (30 ngày đầu):**
  - Không mất thời gian thiết kế logo phức tạp.
  - Phụ đề chính: Font không chân rõ nét (SF Pro Display / Inter / Montserrat Semibold), chữ trắng kem `#F6F1E8` viền/đổ bóng tối nhẹ, từ khóa nhấn màu xanh dương `#1A73E8` hoặc vàng ấm `#FFD166`.
  - Luôn đặt phụ đề trong vùng an toàn (Safe Zone 9:16: cách đáy tối thiểu 320px, cách hai cạnh 90px).

### B. Bio TikTok (Tối đa 80 ký tự/dòng — Ngắn, rõ giá trị & hành động)
```text
Video Editor | Marketing Mindset | AI Workflow
Biến ý tưởng thành video rõ thông điệp & có mục tiêu.
👇 Nhận Starter Kit miễn phí & trao đổi dịch vụ Edit:
```

### C. Bio / Giới thiệu Facebook Cá nhân & Fanpage
```text
Mình là Thành — Video Editor có nền tảng Digital Marketing.
Mình chia sẻ cách kết hợp tư duy Marketing, kỹ năng dựng (Premiere/AE) và AI để biến ý tưởng thành video có chủ đích: người xem hiểu nhanh, nhớ lâu và biết cần làm gì tiếp theo.
📩 Nhắn "EDIT" nếu bạn cần dựng video cho kênh cá nhân / sản phẩm.
📂 Tài liệu Starter Kit, lộ trình học AI & công cụ mình dùng ở link bên dưới.
```

### D. Cấu trúc Link Bio 3 Nhánh (Không để quá 3 lựa chọn)
1. **Nhánh 1 (Tài liệu miễn phí — Thu Lead):** `[Nhận miễn phí] Starter Kit: Checklist Dựng Có Chủ Đích + 15 Hook + 5 Prompt AI + Mẫu Brief`
2. **Nhánh 2 (Dịch vụ — Tạo Doanh thu chính):** `[Làm việc cùng Thành] Dịch vụ Edit Video & Media có chủ đích (Gửi Brief / Nhắn chữ EDIT)`
3. **Nhánh 3 (Học AI & Công cụ — Affiliate):**
   - `Lộ trình học AI thực chiến cho người mới (Zero To AI)`
   - `Tổ hợp công cụ tạo ảnh, video & workflow AI mình đang dùng (Xưởng Media - link affiliate)`

---

## 2. KỊCH BẢN SẢN XUẤT 3 VIDEO GHIM (PINNED VIDEOS)

---

### 📌 VIDEO GHIM 01: GIỚI THIỆU ĐỊNH VỊ (Vị trí Ghim 1)
- **Tiêu đề:** Mình là Thành — Vì sao mình chọn "Dựng Có Chủ Đích"?
- **Mục tiêu:** Giúp người mới vào trang cá nhân hiểu ngay trong 25 giây: Thành là ai, kênh này giải quyết vấn đề gì và vì sao nên theo dõi.
- **Tệp người xem:** Creator, người xây thương hiệu cá nhân, chủ shop, editor mới.
- **Claim duy nhất:** Một video hiệu quả cần sự kết hợp của 3 lớp: Marketing quyết định nói gì, Edit biến thông điệp thành hình ảnh giữ mắt, và AI giúp thử nghiệm nhanh hơn.
- **CTA:** Theo dõi kênh để xem cách mình mổ xẻ và dựng video có chủ đích mỗi tuần.

#### Bảng phân cảnh chi tiết (25–30 giây)
| Thời gian | Hình ảnh / Góc máy / B-roll | Text trên màn hình | Lời thoại (Voiceover / Nói trực tiếp) |
| :--- | :--- | :--- | :--- |
| `00:00 - 00:04` | **Split-screen:** Bên trái là video nhiều hiệu ứng chuyển cảnh loè loẹt nhưng không rõ bán gì; bên phải là video cắt gọn, rõ thông điệp ngay 3 giây đầu. | **Đẹp thôi chưa đủ.**<br>Video cần tạo ra kết quả. | Rất nhiều video dựng cực kỳ mượt, nhưng người xem lướt qua sau ba giây vì không hiểu video đang nói với ai. |
| `00:04 - 00:10` | **A-roll:** Thành ngồi trước bàn làm việc, màn hình phía sau mở timeline Premiere Pro. Cắt cận vừa (Medium Close-up). | **Thành — Dựng Có Chủ Đích**<br>Marketing + Video Editing + AI | Mình là Thành, một video editor xuất phát từ nền tảng digital marketing. |
| `00:10 - 00:21` | **Screen Record + B-roll 3 nhịp theo lời nói:**<br>1. Bản brief/insight gạch chân 1 câu thông điệp.<br>2. Timeline Premiere cắt nhịp before/after.<br>3. Màn hình AI tạo 3 phương án hook và asset. | **1. Marketing:** Chọn đúng 1 thông điệp<br>**2. Edit:** Dẫn mắt & giữ nhịp<br>**3. AI:** Tăng tốc thử nghiệm | Trên kênh này, mình ghi lại quá trình kết hợp ba thứ: dùng tư duy marketing để khóa đúng một thông điệp, dùng kỹ thuật dựng để dẫn mắt người xem, và dùng AI đúng chỗ để rút ngắn thời gian làm phần thô. |
| `00:21 - 00:28` | **A-roll:** Thành nhìn thẳng ống kính, hiển thị 3 khung nội dung tiêu biểu trên kênh (Breakdown, Before/After, AI Workflow). | **Theo dõi kênh để làm video rõ & hiệu quả hơn** | Nếu bạn muốn làm video không chỉ đẹp mà còn khiến người xem hiểu, nhớ và hành động — theo dõi kênh nhé. Đó là cách mình dựng có chủ đích. |

#### Caption đăng bài
- **TikTok:** Mình không tự nhận là chuyên gia toàn năng. Đây là nơi mình chia sẻ cách kết hợp Marketing, Editing và AI để mỗi vết cắt trên timeline đều có lý do của nó. #dungcochudich #videoeditor #marketingvideo #aiworkflow
- **Facebook (Bài ghim trang cá nhân):**
  Chào bạn, nếu bạn mới ghé qua trang của mình thì đây là tóm tắt ngắn gọn mình đang làm gì.
  Mình học và làm Digital Marketing trước khi bước sang nghề Video Editor. Nhờ vậy, mỗi khi mở Premiere hay After Effects lên, câu hỏi đầu tiên của mình không phải là *"bỏ hiệu ứng gì cho ngầu"*, mà là *"người xem cần hiểu điều gì sau 30 giây này?"*.
  Trong 90 ngày tới, mình công khai toàn bộ quá trình làm nghề, các ca sửa video before/after, cách mình dùng AI làm phần thô và chỉnh tinh bằng tay.
  - Nếu bạn tự làm kênh: bạn sẽ tìm thấy checklist hook, cấu trúc kịch bản và cách dựng giữ chân người xem.
  - Nếu bạn cần người đồng hành dựng video có mục tiêu: nhắn chữ **EDIT** cho mình bất cứ lúc nào.

---

### 📌 VIDEO GHIM 02: BẰNG CHỨNG NĂNG LỰC BEFORE/AFTER (Vị trí Ghim 2)
- **Tiêu đề:** Cùng một bộ quay thô: Sửa 3 điểm này để biến video giới thiệu thành video ra khách
- **Mục tiêu:** Chứng minh tay nghề thực tế để chuyển đổi khách hàng dịch vụ Edit/Media.
- **Tệp người xem:** Khách hàng tiềm năng (chủ shop, thương hiệu cá nhân, doanh nghiệp nhỏ).
- **Claim duy nhất:** Thay đổi cấu trúc mở đầu, nhịp cắt và lời kêu gọi hành động trên cùng một footage gốc sẽ tạo ra hai kết quả hoàn toàn khác nhau.
- **CTA:** Nhắn chữ **"EDIT"** kèm mục tiêu của bạn nếu muốn mình xem và dựng lại video theo hướng này.

#### Bảng phân cảnh chi tiết (35–40 giây)
| Thời gian | Hình ảnh / Góc máy / B-roll | Text trên màn hình | Lời thoại (Voiceover / Nói trực tiếp) |
| :--- | :--- | :--- | :--- |
| `00:00 - 00:04` | **Before/After song song:** Cùng 1 đoạn footage gốc, bản A mở đầu bằng cảnh chào hỏi 5s; bản B mở ngay bằng kết quả sản phẩm/dịch vụ. | **Cùng 1 footage thô**<br>Vì sao bản B giữ người xem lâu gấp đôi? | Cùng một thư mục quay thô khách gửi, nhưng chỉ cần đổi ba quyết định dựng, hiệu quả giữ người xem đã khác hẳn. |
| `00:04 - 00:14` | **Screen Record Timeline:** Phóng to 3 giây đầu trên timeline. Kéo đoạn kết quả từ giây thứ 18 lên giây 00:00. | **Quyết định 1: Đảo kết quả lên 3 giây đầu** | Thứ nhất: mình cắt bỏ toàn bộ 5 giây chào hỏi đầu video và đẩy cảnh kết quả rõ nhất từ cuối lên ngay hai giây đầu tiên. |
| `00:14 - 00:24` | **Waveform & Visual Cut:** Cho xem đoạn cắt bỏ khoảng thở thừa và chèn B-roll minh họa đúng vào từ khóa khách hàng quan tâm. | **Quyết định 2: Cắt theo ý, đắp B-roll đúng từ khóa** | Thứ hai: thay vì cắt đều theo nhịp nhạc, mình giữ nhịp nhanh ở phần nêu vấn đề và chèn cận cảnh bằng chứng đúng lúc người nói nhắc đến lợi ích chính. |
| `00:24 - 00:32` | **So sánh 2 màn hình kết thúc (End card):** Bản cũ "Nhớ follow mình nhé" vs Bản mới "Nhắn mã [X] để nhận báo giá theo diện tích phòng". | **Quyết định 3: Đổi CTA chung chung → Lời mời cụ thể** | Thứ ba: mình bỏ câu kêu gọi theo dõi chung chung ở cuối, thay bằng một lời mời hành động cụ thể gắn với nhu cầu mua hàng. |
| `00:32 - 00:40` | **A-roll Thành:** Nói trực diện, hiển thị quy trình 3 bước nhận brief trên màn hình. | **Cần dựng video rõ thông điệp?**<br>Nhắn chữ **"EDIT"** | Nếu bạn đang có sẵn footage hoặc ý tưởng nhưng video lên chưa ra đúng chất và mục tiêu, nhắn chữ "EDIT" cho mình để mình xem thử nhé. |

#### Caption đăng bài
- **TikTok:** Đừng vội quay lại từ đầu khi video ít chuyển đổi. Nhiều khi vấn đề nằm ở thứ tự thông tin trên timeline. Nhắn "EDIT" nếu bạn cần người gỡ rối phần dựng nhé. #dungcochudich #beforeafter #videoediting #dichvuedit
- **Facebook:**
  Nhiều anh chị chủ shop hoặc làm thương hiệu cá nhân gửi file quay cho mình với tâm lý: *"Chắc phải đi quay lại chứ bản này nhìn chán quá"*.
  Nhưng khi mình mở footage ra xem, hình và tiếng đều đủ dùng — thứ duy nhất bị ngược là **thứ tự kể chuyện**: kết quả đẹp nhất lại giấu ở giây 25, còn 5 giây đầu lại dùng để giới thiệu tên tuổi.
  Trong video này là 3 bước mình luôn làm khi nhận một project: đảo kết quả lên đầu, cắt theo trọng tâm thông điệp và khóa lại bằng một CTA rõ ràng.
  Bạn đang có footage thô cần dựng thành video hoàn chỉnh? Nhắn chữ **EDIT** vào tin nhắn cho mình nhé.

---

### 📌 VIDEO GHIM 03: BẮT ĐẦU TỪ ĐÂU & STARTER KIT (Vị trí Ghim 3)
- **Tiêu đề:** Mới tự làm video xây kênh: Đừng quay trước khi có 4 thứ này
- **Mục tiêu:** Chuyển đổi người xem mới thành Lead qua bộ tài liệu miễn phí **Starter Kit v1**.
- **Tệp người xem:** Creator mới, chủ shop tự làm nội dung, người mới học làm video và AI.
- **Claim duy nhất:** Chuẩn bị trước Hook, cấu trúc 1-Claim, Shot List và Prompt AI trên 1 trang giấy giúp giảm một nửa thời gian quay dựng.
- **CTA:** Nhận miễn phí bộ **Starter Kit: Dựng Có Chủ Đích** ở link bio.

#### Bảng phân cảnh chi tiết (30–35 giây)
| Thời gian | Hình ảnh / Góc máy / B-roll | Text trên màn hình | Lời thoại (Voiceover / Nói trực tiếp) |
| :--- | :--- | :--- | :--- |
| `00:00 - 00:04` | **A-roll + Cận cảnh màn hình:** Thành giơ tờ/màn hình Checklist 1 trang bên cạnh timeline Premiere gọn gàng. | **Quay 2 tiếng nhưng lúc dựng thiếu cảnh?**<br>Dùng bộ khung 4 bước này. | Lý do lớn nhất khiến bạn quay hai tiếng nhưng lúc ngồi vào máy vẫn thiếu cảnh là vì bật máy quay trước khi khóa thông điệp. |
| `00:04 - 00:13` | **Screen Record:** Lướt nhanh qua 4 phần của Starter Kit: (1) 15 khung Hook, (2) Khung kịch bản 1-Claim, (3) Bảng Shot List, (4) 5 Prompt AI. | **1. 15 khung Hook 3 giây**<br>**2. Kịch bản 1-Claim** | Trước mỗi buổi quay batch 4 video, mình luôn đi qua bốn bước: một là chọn đúng một khung hook khớp với nỗi đau người xem; hai là gọt kịch bản về đúng một ý chính. |
| `00:13 - 00:23` | **Screen Record tiếp:** Cảnh dùng Prompt AI tách kịch bản thành bảng Shot List (A-roll, B-roll, Screen record) và Checklist 10 điểm trước khi Export. | **3. Bảng Shot List & 5 Prompt AI**<br>**4. Checklist 10 điểm trước khi xuất file** | Ba là dùng AI chuyển kịch bản đó thành danh sách cảnh quay để không sót B-roll; và bốn là rà qua 10 điểm kiểm tra phụ đề, âm thanh, CTA trước khi bấm xuất file. |
| `00:23 - 00:33` | **A-roll + Hướng dẫn bấm link bio:** Hiển thị giao diện link bio trên điện thoại, khoanh vào mục "Starter Kit". | **Tải miễn phí Starter Kit v1**<br>Ở ngay Link Bio của mình | Mình đã đóng gói toàn bộ checklist, mẫu brief, 15 cấu trúc hook và 5 prompt AI này thành bộ Starter Kit miễn phí. Bạn bấm vào link ở bio của mình để lấy về dùng ngay cho video tuần này nhé. |

#### Caption đăng bài
- **TikTok:** Toàn bộ quy trình chuẩn bị trước khi quay và checklist kiểm tra trước khi xuất video của mình nằm gọn trong Starter Kit này. Lấy miễn phí ở bio nhé! #dungcochudich #starterkit #xaykenhtiktok #videomarketing
- **Facebook:**
  Khi mới bắt đầu làm nội dung đều đặn mỗi tuần, thứ làm mình đuối sức nhất không phải là thao tác phần mềm, mà là mỗi lần ngồi vào bàn lại phải nghĩ lại từ đầu: *"Hôm nay mở đầu thế nào? Cần quay những cảnh gì? Viết prompt cho AI ra sao để đỡ sáo rỗng?"*
  Mình đã gom lại toàn bộ các biểu mẫu mình dùng hằng tuần thành bộ **Starter Kit v1 — Dựng Có Chủ Đích**, bao gồm:
  1. 15 khung Hook 3 giây đầu chia theo 3 mức độ nhận thức của người xem.
  2. Khung kịch bản 30 giây (1 Video = 1 Claim = 1 CTA).
  3. 5 Prompt AI thực chiến để tìm góc nội dung, viết lại script tự nhiên và lập Shot List.
  4. Mẫu Brief 1 trang & Checklist 10 điểm kiểm tra trước khi đăng.
  Bạn có thể tải về dùng miễn phí tại link bio hoặc bình luận dưới bài viết này để mình gửi trực tiếp nhé!

<!-- ===== /file: personal-brand-video-engine/references/NGAY_02_HO_SO_KENH_VA_3_VIDEO_GHIM.md ===== -->

<!-- ===== file: personal-brand-video-engine/references/SOP_SAN_XUAT_VIDEO_HANG_TUAN.md ===== -->

# Quy Trình Sản Xuất Batch 4 Video/Tuần (`DA-01`) & Ngân Hàng Câu Hỏi Khán Giả (`DA-02`)

> **Mục tiêu:** Giúp Thành duy trì nhịp xuất bản đều đặn **4 video/tuần trong 12 tuần (48 video)** mà không bị kiệt sức hay bí ý tưởng giữa chừng.

---

## 1. NHỊP SẢN XUẤT HÀNG TUẦN (BATCH WORKFLOW 7 NGÀY)

Để không rơi vào cảnh *"ngày nào đăng bài mới cuống cuồng viết và dựng ngày đó"*, toàn bộ lịch 90 ngày vận hành theo nguyên tắc **Tuần hiện tại đăng bài đã làm xong từ tuần trước, đồng thời sản xuất gối đầu cho tuần kế tiếp**:

| Thứ | Trọng tâm trong ngày | Đầu việc cụ thể | Thời lượng | Đầu ra bắt buộc |
| :--- | :--- | :--- | :---: | :--- |
| **Thứ Hai** | **Đăng Bài 1 (Bắt buộc)** + Khóa chủ đề tuần sau | - Đăng video số 1 trong tuần (TikTok + FB Reels/Post).<br>- Dành 30 phút trả lời bình luận và tin nhắn.<br>- Xem nhanh bảng KPI tuần trước.<br>- Khóa 4 mã `C0xx` của tuần tiếp theo (chốt rõ Tệp xem, 1 Claim, 1 CTA). | 120 phút | Link bài đăng 1 + 4 chủ đề tuần sau đã khóa. |
| **Thứ Ba** | **Đăng Bài 2 (Bắt buộc)** + Viết 4 Script tuần sau | - Đăng video số 2 trong tuần.<br>- Mở file kịch bản của Sprint tương ứng trong `01_Y_TUONG_VA_SCRIPT`, cá nhân hóa số liệu/ví dụ thật của tuần đó cho 4 script tuần sau.<br>- Lập danh sách tài nguyên màn hình cần quay. | 150 phút | Link bài đăng 2 + 4 kịch bản & shot list sẵn sàng bấm máy. |
| **Thứ Tư** | **Quay Batch 4 Video tuần sau** + Dựng nháp 2 bài | - Quay liền 1 mạch 4 phần A-roll của tuần sau (thay 2 áo để đổi cảm giác thị giác).<br>- Quay toàn bộ Screen Record (Premiere, AE, AI workflow) và B-roll bàn làm việc.<br>- Chép file vào `02_FOOTAGE` đúng mã `C0xx` và cắt nháp (Rough cut) 2 video đầu. | 240 phút | 4 bộ footage đủ hình/âm + 2 bản Rough cut. |
| **Thứ Năm** | **Đăng Bài 3 (Bắt buộc)** + Hoàn thiện 2 video đầu & Làm dự án dài ngày | - Đăng video số 3 trong tuần.<br>- Hoàn thiện dựng 2 video đầu của tuần sau.<br>- Dành 60 phút làm dự án dài ngày (`Starter Kit`, `Case Study`, hoặc `Funnel`). | 180 phút | Link bài đăng 3 + 2 video tuần sau hoàn chỉnh + 1 mốc dự án. |
| **Thứ Sáu** | **Hoàn thiện 2 video còn lại & Kiểm duyệt (QA)** | - Dựng nốt 2 video còn lại của tuần sau.<br>- Chạy Checklist QA 10 điểm (safe zone, chính tả phụ đề, âm thanh, CTA).<br>- Viết sẵn Caption TikTok & Bài đăng Facebook từ file kịch bản. | 210 phút | Đủ 4 file `.mp4` trong `04_EXPORT` + Caption sẵn sàng. |
| **Thứ Bảy** | **Đăng Bài 4 (Linh hoạt)** + Lên lịch tuần sau & Thu câu hỏi | - Đăng video số 4 trong tuần (nếu tuần đó quá tải công việc khách hàng, được phép lùi bài linh hoạt này nhưng tuyệt đối giữ 3 bài Thứ 2 - Thứ 3 - Thứ 5).<br>- Lên lịch sẵn tối thiểu 3 video tuần sau.<br>- Ghi ít nhất 5 câu hỏi/insight thật của khán giả vào bảng bên dưới. | 120 phút | Link bài đăng 4 + 5 câu hỏi khán giả + 3 bài tuần sau đã hẹn giờ. |
| **Chủ Nhật** | **Review Tuần / Sprint & Nghỉ ngơi (Buffer)** | - Nhập số liệu vào Sheet `Báo cáo KPI`.<br>- Nếu là cuối Tuần 3, 6, 9, 12: Làm báo cáo Sprint (`DA-06`).<br>- Thời gian còn lại nghỉ ngơi, không nhồi quay thêm 4 video mới. | 60–120 phút | Bảng KPI đã cập nhật. |

---

## 2. QUY TẮC QUẢN LÝ FILE TRONG THƯ MỤC DỰ ÁN

- **`02_FOOTAGE/`**: Tạo thư mục con theo mã, ví dụ `C001_BaGiayDau/`. Bên trong đặt tên chuẩn:
  - `C001_AROLL_01.mp4` (Cảnh nói trực diện)
  - `C001_SCREEN_01.mp4` (Quay màn hình Premiere / AI)
  - `C001_BROLL_01.mp4` (Cảnh phụ thao tác tay / màn hình phụ)
- **`03_PROJECT_EDIT/`**: Lưu project Premiere/After Effects theo tuần, ví dụ `TUAN_01_SPRINT_1.prproj`.
- **`04_EXPORT/`**: Lưu file xuất cuối cùng chuẩn `1080x1920`, đặt tên `C001_FINAL_20261026.mp4` kèm ảnh bìa `C001_THUMB.png`.

---

## 3. SỔ THEO DÕI NGÂN HÀNG CÂU HỎI KHÁN GIẢ (`DA-02` — Mục tiêu: 60 câu hỏi thật)

> Mỗi Thứ Bảy, trích xuất tối thiểu 5 bình luận, tin nhắn hoặc thắc mắc thực tế của khách hàng/người xem vào bảng này để biến thành chất liệu thực tế cho các tuần tiếp theo:

| STT | Ngày ghi nhận | Nguồn (Comment TikTok / FB / DM khách) | Nguyên văn câu hỏi hoặc vấn đề của người xem | Thuộc Pillar nào (`P1–P4`) | Gắn vào mã kịch bản nào hoặc tạo ý tưởng mới |
| :---: | :---: | :--- | :--- | :---: | :--- |
| 01 | 31/10/2026 | *[Ví dụ: Comment bài C001]* | *"Mình bán đồ gia dụng thì 3 giây đầu nên quay cảnh gì để khách không lướt qua?"* | P1 (`MKT01`) | Dùng làm ví dụ mở đầu cho bài `C003` (Chủ shop) |
| 02 | 31/10/2026 | *[Ví dụ: DM khách hỏi giá]* | *"Anh có sẵn 10 clip quay bằng điện thoại nhưng lộn xộn lắm, bên em có nhận cắt lại không?"* | P2 (`EDIT01`) | Đưa vào kịch bản `C023` & `C038` |
| 03 | 31/10/2026 | *[Ví dụ: Comment bài C040]* | *"Làm sao để ChatGPT không viết ra mấy câu kiểu 'Trong kỷ nguyên số ngày nay' vậy bạn?"* | P3 (`AI02`) | Dùng trực tiếp làm màn hình minh họa cho bài `C044` |
| 04 | ... | | | | |
| 05 | ... | | | | |

<!-- ===== /file: personal-brand-video-engine/references/SOP_SAN_XUAT_VIDEO_HANG_TUAN.md ===== -->

<!-- ===== file: personal-brand-video-engine/references/VOICE_PROFILE_VA_QUY_CHUAN_CONTENT.md ===== -->

# Hồ Sơ Giọng Điệu (Voice Profile) & Quy Chuẩn Sản Xuất Content — Thành (Dựng Có Chủ Đích)

> **Skills áp dụng:** `brand-voice` (xây dựng Voice Profile chuẩn hóa) + `content-engine` (chuyển hóa nguồn chiến lược thành kịch bản gốc theo từng nền tảng) + `crosspost` (chuyển thể đa kênh TikTok ↔ Facebook Reels ↔ Bài viết Facebook cá nhân).

---

## 1. VOICE PROFILE (`brand-voice` Canonical Schema)

```text
VOICE PROFILE
=============
Author: Thành — Dựng Có Chủ Đích (Marketing Video Editor ứng dụng AI)
Goal: Xây dựng uy tín thực chiến qua 48–60 video trong 90 ngày; thu hút lead Dịch vụ Edit/Media, người nhận Starter Kit, học viên Zero To AI và người dùng Xưởng Media mà không phóng đại kinh nghiệm.
Confidence: Medium-High (Khởi tạo từ Brief cá nhân, Ngày 01 Định vị và Hệ nội dung; sẽ khóa cố định sau 12–20 video thực tế).

Source Set
- THUONG_HIEU_CA_NHAN_THANH_90_NGAY/00_CHIEN_LUOC/NGAY_01_DINH_VI.md
- Sheet "Tổng quan", "Hệ nội dung", "Ngân hàng content", "Funnel & CTA" (He-thong-content-ca-nhan-Thanh.xlsx)
- Sheet "Lịch 90 ngày" & "Bảng thực thi" (generate_90_day_execution.mjs)

Rhythm
- Câu ngắn (8–16 từ/câu khi nói trên video).
- Mở đầu trực diện bằng kết quả, lỗi cụ thể trên màn hình hoặc 2 giây before/after.
- Ngắt nhịp rõ giữa các ý; dùng khoảng dừng 0.5–1 giây trước câu kết luận thay vì nhồi từ nối rườm rà.

Compression
- Độ nén cao: mỗi video 30–45 giây chỉ giải quyết đúng 1 vấn đề, 1 claim, 1 tệp người xem và 1 CTA.
- Không giải thích lý thuyết suông; luôn gắn liền với thao tác trên timeline Premiere/After Effects, màn hình prompt AI, hoặc bản so sánh A/B.

Capitalization
- Chuẩn tiếng Việt thông thường trong bài viết và phụ đề.
- Trên khung hình video (On-screen Text / Title Card): Viết hoa chữ cái đầu mỗi dòng hiển thị; từ khóa cần nhấn chỉ chọn 1 cụm duy nhất trên 1 khung hình.

Parentheticals
- Trong kịch bản nói: hạn chế ngoặc đơn làm đứt mạch nói.
- Trong bài viết Facebook: chỉ dùng ngoặc đơn để ghi chú thông số thật, điều kiện áp dụng hoặc giới hạn của công cụ AI (ví dụ: "(bản thô AI mất 2 phút, nhưng mình mất thêm 10 phút chỉnh lại nhịp cắt)").

Question Use
- Hiếm và có chủ đích.
- Chỉ dùng câu hỏi khi đó là câu hỏi thật của khách hàng/creator trong brief hoặc để mở ra phép thử Before/After.
- Tuyệt đối không dùng câu hỏi câu tương tác sáo rỗng ở cuối bài kiểu "Các bạn nghĩ sao?".

Claim Style
- Mọi nhận định đều đi theo cấu trúc: [Lỗi/Tình huống cụ thể] → [Quyết định dựng / Marketing / AI] → [Bằng chứng nhìn/nghe thấy được trên màn hình].
- Xưng "mình", gọi người xem là "bạn" (hoặc gọi rõ ngữ cảnh: "nếu bạn đang tự quay video bán hàng...", "khi mình nhận footage từ khách...").
- Định vị trung thực: người làm nghề có nền tảng marketing, gần 1 năm đi làm và hơn 6 tháng tập trung edit + ứng dụng AI công khai (build in public).

Preferred Moves
- Cho xem 2 giây bản gốc bị lỗi ngay đầu video rồi dừng hình để chỉ ra điểm gãy.
- Đặt kết quả (Final Cut) lên trước quy trình (Timeline).
- Luôn tách bạch phần "AI làm thô" (tìm góc, nháp script, tạo asset tĩnh/B-roll ngắn) và phần "Editor làm tinh" (chọn nhịp cắt, giữ cảm xúc, đặt điểm nhấn, kiểm soát thông điệp bán hàng).
- Kết video bằng câu khoá nhẹ nhàng hoặc biến thể tự nhiên của signature: "Đó là cách mình dựng có chủ đích."

Banned Moves
- Cấm mở đầu bằng: "Xin chào mọi người, mình là Thành...", "Trong thời đại AI bùng nổ hiện nay...", "Bí quyết triệu view", "Thay đổi cuộc đời".
- Cấm dùng các từ sáo rỗng: "siêu phẩm", "đỉnh nóc kịch trần", "AI làm thay 100%", "chỉ cần 1 click".
- Cấm tự nhận là "chuyên gia AI", "bậc thầy marketing" hay hứa hẹn cam kết doanh số ảo.
- Cấm nhồi 2–3 CTA hoặc bán cả Dịch vụ + Khóa học + Công cụ trong cùng một video.
- Cấm dùng câu hỏi mồi tương tác giả tạo ở cuối bài Facebook/TikTok.

CTA Rules
- Mỗi video chỉ gắn ĐÚNG 1 CTA khớp với giai đoạn Funnel và Offer của tuyến nội dung đó:
  1. Nhận biết (P1/P2/P4 không bán): "Lưu lại checklist/cấu trúc này để đối chiếu khi dựng video tiếp theo" hoặc "Theo dõi kênh để xem tiếp series..."
  2. Lead Magnet (Starter Kit): "Mình để sẵn bản Checklist / Template Hook–Body–Close / Mẫu Shot List trong Starter Kit ở bio, bạn vào lấy về dùng ngay."
  3. Chuyển đổi Dịch vụ (Edit/Media): "Nếu bạn có sẵn footage hoặc ý tưởng nhưng video chưa ra đúng thông điệp muốn bán, nhắn chữ 'EDIT' cho mình kèm mục tiêu video nhé."
  4. Chuyển đổi Học AI (Zero To AI): "Nếu bạn muốn học cách ứng dụng AI vào nội dung từ gốc theo lộ trình rõ ràng, xem mục Zero To AI ở bio của mình."
  5. Chuyển đổi Công cụ (Xưởng Media): "Mình chạy thử workflow tạo ảnh/video này trên Xưởng Media — link dùng thử (có affiliate) mình để rõ ở bio."

Channel Notes
- TikTok (Kênh thử nghiệm chính):
  - Video 9:16 (1080x1920), thời lượng 25–45s.
  - 3 giây đầu phải có chuyển động hình ảnh (split-screen, khoanh đỏ trên video lỗi, hoặc zoom timeline) + câu Hook đánh thẳng vào vấn đề.
  - Caption ngắn gọn (2–3 dòng), nêu lại core claim + 1 chỉ dẫn CTA rõ + 3–4 hashtag đúng ngách (#dungcochudich #videoediting #marketingvideo #aiworkflow).
- Facebook Reels (Kênh phủ & nuôi dưỡng):
  - Dùng cùng file video gốc nhưng viết lại phần mở đầu caption gần gũi hơn với tệp chủ shop / thương hiệu cá nhân / khách hàng tiềm năng.
- Facebook Cá Nhân / Bài Viết Dài (Kênh xây niềm tin & chuyển đổi):
  - Không copy-paste caption của TikTok.
  - Chuyển hóa kịch bản thành bài viết ngắn 150–250 chữ theo cấu trúc: Tình huống thực tế khi làm việc → 3 quyết định cụ thể (Marketing / Edit / AI) → Hình chụp màn hình timeline hoặc video đính kèm → Lời mời trao đổi hoặc nhận tài liệu.
```

---

## 2. ĐỐI CHIẾU & ĐỒNG BỘ 3 TRANG TRONG GOOGLE SHEET

Qua việc đọc kỹ 3 trang **Hệ nội dung**, **Ngân hàng content** và **Lịch sản xuất / Lịch 90 ngày**, bộ tài liệu này giải quyết triệt để sự khác biệt giữa hai bảng lịch trong Sheet để bạn vận hành trơn tru:

1. **Trang `Hệ nội dung`**:
   - Khóa tỷ trọng 4 Pillar: **P1 Marketing trong video (35%)** — **P2 Edit & Storytelling (30%)** — **P3 AI trong workflow editor (25%)** — **P4 Hành trình & Bằng chứng (10%)**.
   - Chia thành **23 tuyến nội dung** (`MKT01`–`MKT06`, `EDIT01`–`EDIT06`, `AI01`–`AI07`, `JRN01`–`JRN05`).
2. **Trang `Ngân hàng content`**:
   - Gồm **60 mã nội dung (`C001` đến `C060`)**, được sắp xếp theo từng nhóm Pillar (`C001`–`C021` là P1; `C022`–`C039` là P2; `C040`–`C054` là P3; `C055`–`C060` là P4).
3. **Đồng bộ giữa trang `Lịch sản xuất` và `Lịch 90 ngày` (`Bảng thực thi`)**:
   - Ở tab `Lịch sản xuất` ban đầu, danh sách lấy tuần tự từ `C001` đến `C048` nên 5 tuần đầu toàn bộ là P1 (chưa trộn đều 4 Pillar).
   - Ở tab `Lịch 90 ngày` (bản thực thi chuẩn), **48 video chính thức trong 12 tuần** đã được trộn chuẩn tỷ lệ **35% P1 / 30% P2 / 25% P3 / 10% P4** (mỗi tuần gồm **3 video bắt buộc** vào Thứ Hai, Thứ Ba, Thứ Năm + **1 video linh hoạt** vào Thứ Bảy).
   - **Giải pháp triển khai trong bộ content này**:
     - Chúng tôi viết **đầy đủ kịch bản chi tiết cho cả 60/60 mã (`C001`–`C060`)** + **3 Video Ghim**.
     - Sắp xếp các file kịch bản theo đúng **4 Sprint (12 tuần) của `Lịch 90 ngày`** (48 video) và đóng gói riêng **12 video còn lại (`C018`–`C021`, `C036`–`C039`, `C052`–`C054`, `C060`)** thành bộ **Video Báo Cáo Sprint, Case Study & Chuyển Đổi Sâu**. Nhờ vậy, dù bạn tra theo **Ngày/Tuần** hay tra theo **Mã `C001`–`C060`**, bạn đều có ngay kịch bản quay từng giây!

---

## 3. KHUNG KỊCH BẢN VIDEO NGẮN CHUẨN (`content-engine` Short Video Spec)

Mỗi video trong bộ 60 kịch bản đều tuân thủ cấu trúc 4 nhịp:

| Nhịp | Thời lượng | Mục tiêu | Quy tắc hình ảnh (Visual) | Quy tắc lời thoại (Audio) |
| :--- | :--- | :--- | :--- | :--- |
| **1. HOOK** | `00:00 – 00:03` | Giữ mắt + Nêu đúng nỗi đau hoặc kết quả | Cho xem ngay lỗi sai, bản so sánh A/B hoặc kết quả cuối cùng. Có text tiêu đề rõ trong vùng an toàn. | 1 câu duy nhất (dưới 12 từ). Không chào hỏi. |
| **2. PROOF / TENSION** | `00:03 – 00:10` | Chứng minh vấn đề là thật | Khoanh vùng trên frame, mở timeline Premiere hoặc chỉ vào đoạn script/output AI bị lỗi. | Chỉ ra nguyên nhân cốt lõi vì sao cách làm cũ khiến người xem lướt qua hoặc không hiểu. |
| **3. BODY (1 CLAIM)** | `00:10 – 00:32` | Giải quyết bằng 2–3 bước cụ thể | Cắt cảnh mỗi 2–4 giây: A-roll nói trực diện xen kẽ Screen Record thao tác thật và kết quả sau khi sửa. | Nói cụ thể từng bước: cắt chữ nào, đổi shot nào, nhập prompt gì, giữ lại gì. |
| **4. CLOSE & CTA** | `00:32 – 00:42` | Chốt bài học + 1 hành động tiếp theo | Chạy lại 2–3 giây bản hoàn chỉnh + Text card hiển thị CTA khớp với Offer. | Chốt câu ngắn gọn + 1 lời mời hành động tự nhiên (Lưu bài / Nhận Starter Kit / Nhắn EDIT / Xem lộ trình). |

<!-- ===== /file: personal-brand-video-engine/references/VOICE_PROFILE_VA_QUY_CHUAN_CONTENT.md ===== -->
