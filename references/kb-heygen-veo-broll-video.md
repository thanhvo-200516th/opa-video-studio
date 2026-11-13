# kb-heygen-veo-broll-video — toàn văn tài liệu của nguồn `heygen-veo-broll-video`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/heygen-veo-broll-video/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: heygen-veo-broll-video/SKILL.md ===== -->

---
name: heygen-veo-broll-video
description: >-
  Tự động hóa sản xuất video ngắn kết hợp A-Roll từ HeyGen Avatar IV API (render.py, chuẩn hóa văn bản tiếng Việt để AI đọc chuẩn số, phần trăm %, từ khóa tiếng Anh và tối ưu chi phí credit) cùng B-Roll điện ảnh dọc 9:16 từ Google Flow / Veo theo công thức nhịp dựng 32% A-Roll + 68% B-Roll. Kích hoạt khi người dùng muốn gọi API HeyGen tạo video avatar nói tiếng Việt hàng loạt, chuẩn hóa kịch bản thoại cho HeyGen, hoặc viết bộ prompt tạo video B-Roll 9:16 trên Google Flow / Veo khớp với lời thoại A-Roll.
---

# HeyGen & Veo B-Roll Video — Tự Động Hóa A-Roll HeyGen Avatar IV & B-Roll Điện Ảnh Google Flow

Skill này cung cấp quy trình khép kín để sản xuất hàng loạt video ngắn dọc (`9:16`, `1080x1920`) kết hợp giữa **A-Roll nhân vật ảo (HeyGen Avatar IV API)** và **B-Roll điện ảnh thực tế (Google Flow / Veo)** theo tỷ lệ giữ chân người xem tối ưu.

---

## Chạy trên máy Linux này

- Python: `~/.venvs/video-skills/bin/python` (máy không có lệnh `python`/`py`; venv có numpy, scipy, matplotlib, opencv, scikit-image, Pillow, fontTools, resvg-py, faster-whisper). Lệnh `python …` trong tài liệu chạy bằng đường dẫn này.
- Ghép A-roll HeyGen và B-roll Veo trên Linux bằng FilmCraft 0.13 (`.fcproj`) thay Premiere, theo skill `talking-head-premiere`.
- Đặt khóa trước khi chạy `scripts/render.py`: `export HEYGEN_KEY=<api key>` (lệnh `set`/`$env:` trong script là cú pháp Windows).

---

## 1. Cấu Trúc Thư Mục Trong Skill

- **`scripts/render.py`** — Script Python gọi trực tiếp **HeyGen API (`v2/video/generate`)** với động cơ `Avatar IV`, tự động gửi kịch bản, theo dõi trạng thái xử lý (`polling status`) và tải file `.mp4` hoàn chỉnh về máy.
- **`references/README-preset.md`** — Sổ tay cấu hình Preset HeyGen Avatar IV (Avatar ID, Voice ID tiếng Việt, tốc độ đọc, quy tắc viết lời thoại chống đọc sai và mẹo tiết kiệm credit).
- **`references/PROMPT_TAO_VIDEO_BROLL_KICH_BAN_01_GOOGLE_FLOW.md` & `PROMPT_TAO_VIDEO_BROLL_KICH_BAN_03_GOOGLE_FLOW.md`** — Bộ mẫu thiết kế B-Roll điện ảnh dọc `9:16` trên Google Flow (Veo) khớp từng giây với lời thoại A-Roll, kèm bảng dựng chi tiết trên Premiere / CapCut.
- **`examples/kich-ban-30-bai.json` & `examples/bai03-tuduyai-loi-thoai.txt`** — Dữ liệu kịch bản mẫu 30 bài và văn bản thoại đã được chuẩn hóa phát âm.

---

## 2. Quy Tắc Chuẩn Hóa Văn Bản Thoại Tiếng Việt Cho HeyGen Avatar IV

> [!IMPORTANT]
> Bộ đọc giọng nói AI (TTS) của HeyGen sẽ đọc vấp, đọc bằng tiếng Anh hoặc nuốt chữ nếu gặp ký hiệu viết tắt (`%`, `/`, `24/7`, số ghép) hoặc tên từ khóa viết hoa. Bắt buộc chuẩn hóa văn bản theo 5 quy tắc sau trước khi đưa vào `scripts/render.py`:

1. **Ký hiệu phần trăm (`%`) và con số:**
   - Không viết `80%`, `100%`, `24/7`, `3-5 phút`.
   - **Phải viết bằng chữ tiếng Việt đầy đủ:** `tám mươi phần trăm`, `một trăm phần trăm`, `hai mươi tư trên bảy`, `ba đến năm phút`.
2. **Từ khóa bình luận (CTA Comment Keyword):**
   - Ở câu kêu gọi hành động cuối video (ví dụ: *"Bình luận chữ TƯ DUY"*), hãy đặt từ khóa trong dấu ngoặc kép và tách nhịp bằng dấu phẩy: `Bình luận chữ, "Tư Duy", xuống bên dưới...` để Avatar nhấn giọng rõ ràng.
3. **Ngắt nhịp thở tự nhiên bằng dấu câu:**
   - Không viết câu dài quá `18 từ` không có dấu phẩy.
   - Dùng dấu phẩy `,` cho nghỉ ngắn (`0.2s`) và dấu chấm `.` cho nghỉ chuyển ý (`0.45s`).
4. **Từ mượn tiếng Anh thông dụng:**
   - Giữ nguyên các từ quốc tế phổ biến mà TTS đã biết (`AI`, `video`, `marketing`, `chatbot`, `fanpage`), nhưng phiên âm hoặc dịch sang tiếng Việt các thuật ngữ chuyên ngành dễ bị đọc lơ lớ.
5. **Tối ưu thời lượng & Credit HeyGen:**
   - Giữ độ dài kịch bản trong khoảng **95 – 125 từ** (tương đương **36 – 45 giây** với `speed = 1.05`). Đây là khoảng thời lượng vàng vừa tối ưu tỷ lệ xem hết (Completion Rate), vừa tiết kiệm hạn ngạch credit Avatar IV.

---

## 3. Công Thức Phối Hợp Nhịp Điệu: 32% A-Roll (HeyGen) + 68% B-Roll (Google Flow / Veo)

Một video sử dụng Avatar AI nếu để hình người nói đứng yên suốt 40 giây sẽ nhanh chóng gây nhàm chán và lộ nét nhân tạo. Công thức dựng chuẩn trong skill này là:

| Tỷ trọng | Thành phần | Vai trò & Thời điểm xuất hiện |
|---|---|---|
| **32% Thời lượng** | **A-Roll (HeyGen Avatar IV)** | Chỉ xuất hiện toàn khung hình ở **3 giây đầu (Hook mở màn)**, **1–2 nhịp chuyển ý giữa bài (`14s–17s`)**, và **5 giây cuối (Chốt CTA kêu gọi hành động)**. Trong toàn bộ thời gian còn lại, chỉ giữ **tiếng nói (Audio)** của HeyGen làm Voiceover! |
| **68% Thời lượng** | **B-Roll Điện Ảnh 9:16 (Google Flow / Veo)** | Phủ kín các đoạn giải thích nỗi đau, bằng chứng và quy trình (`03s–14s` và `17s–35s`). Mỗi cảnh B-Roll dài **`2.5s – 4.0s`**, quay dọc `9:16`, ánh sáng điện ảnh thực tế (*Cinematic shallow depth of field, 35mm/50mm lens, natural Vietnamese office/studio environment*). |

---

## 4. Cấu Trúc Viết Prompt Tạo B-Roll 9:16 Trên Google Flow (Veo)

Khi viết bộ Prompt B-Roll đi kèm kịch bản A-Roll (xem mẫu trong `references/PROMPT_TAO_VIDEO_BROLL_KICH_BAN_01_GOOGLE_FLOW.md`), mỗi cảnh B-Roll phải bao gồm:
1. **Mốc thời gian & Câu thoại A-Roll tương ứng:** Giúp người dựng biết đặt clip B-Roll đè lên đoạn thoại nào trên rãnh `V2`.
2. **Thông số khung hình đầu vào:** `Vertical 9:16 (1080x1920), 24fps cinematic motion, photorealistic, shot on ARRI Alexa Mini LF with 35mm f/1.4 lens`.
3. **Bối cảnh & Nhân vật cụ thể:** Mô tả rõ không gian làm việc hiện đại tại Việt Nam, hành động tay gõ phím, nét mặt căng thẳng (khi mô tả nỗi đau) hoặc thư thái mỉm cười (khi có giải pháp tự động hóa).
4. **Chuyển động máy quay (Camera Movement):** *Slow push-in*, *Over-the-shoulder tracking shot*, *Macro rack focus from coffee cup to laptop screen*.
5. **Chỉ dẫn hậu kỳ (Post-Production Note):** Ghi chú rõ vị trí đặt phụ đề, hiệu ứng âm thanh (tiếng gõ phím, tiếng thông báo tin nhắn, tiếng whoosh chuyển cảnh) và mức độ cắt cúp.

<!-- ===== /file: heygen-veo-broll-video/SKILL.md ===== -->

<!-- ===== file: heygen-veo-broll-video/examples/bai03-tuduyai-loi-thoai.txt ===== -->

Chín mươi phần trăm chủ doanh nghiệp đi học các lớp AI về đều bỏ xó chỉ sau đúng 2 tuần. Không phải vì AI không hiệu quả, mà vì bạn đang học AI theo cách của một nhân viên thực thi, chứ không phải của một người điều hành.

Hãy nhìn lại mà xem. Bạn bỏ ra vài ngày cuối tuần đi học cách gõ câu lệnh viết bài Facebook, cách dùng AI vẽ ảnh, cắt video. Về đến công ty, bạn hào hứng tự ngồi làm được 3 hôm, đến hôm thứ 4 công việc kinh doanh ngập đầu, bạn không có thời gian gõ lệnh nữa, còn nhân viên của bạn thì vẫn làm việc theo lối cũ. Thế là mọi thứ quay về vạch xuất phát. Nếu người làm chủ học AI chỉ để tự tay ngồi làm thay việc của nhân viên, bạn đang tự trả lương Giám đốc cho một công việc của thực tập sinh.

Khi tôi cố vấn và đào tạo cho các doanh nghiệp từ 5 đến 50 nhân sự, người làm chủ chỉ cần nắm 3 việc cốt lõi trên màn hình này.

Tầng 1, hiểu giới hạn công nghệ. Bạn cần biết rõ tác vụ nào trong công ty AI có thể rút ngắn từ 4 tiếng xuống 15 phút, để không bị nhân viên báo cáo khống thời gian.

Tầng 2, thiết lập tiêu chuẩn. Cùng các trưởng bộ phận đóng gói kiến thức của công ty thành các biểu mẫu AI cố định cho từng vị trí.

Tầng 3, đào tạo và đo lường KPI mới. Đưa đội ngũ nhân sự vào chương trình huấn luyện thực chiến, để chính họ là người bấm nút vận hành hệ thống đó mỗi ngày, còn bạn chỉ kiểm soát kết quả đầu ra.

Đừng biến mình thành người giỏi công cụ nhất công ty. Hãy biến mình thành người sở hữu đội ngũ biết dùng AI giỏi nhất. Comment từ khóa TƯ DUY AI bên dưới, để nhận Bản đồ Lộ trình Chuyển đổi AI dành riêng cho CEO và chủ doanh nghiệp SME.

<!-- ===== /file: heygen-veo-broll-video/examples/bai03-tuduyai-loi-thoai.txt ===== -->

<!-- ===== file: heygen-veo-broll-video/references/PROMPT_TAO_VIDEO_BROLL_KICH_BAN_01_GOOGLE_FLOW.md ===== -->

# 🎬 PHÂN TÍCH SỐ LƯỢNG CẢNH TRÁM & BỘ PROMPT TẠO VIDEO B-ROLL GOOGLE FLOW — KỊCH BẢN #01

> **Kịch bản**: **BÀI #01 (Tuần 1 · Thứ 2 · TOFU): Nghịch lý nuôi 20 nhân sự nhưng Chủ doanh nghiệp vẫn làm 14 tiếng/ngày**  
> **Từ khóa Lead (CTA)**: `GIAIPHONG`  
> **Tổng thời lượng kịch bản**: `75 giây (00:00 – 01:15)`  
> **Định dạng khuyến nghị trên Google Flow (Veo)**: `Text-to-Video` · Tỷ lệ `9:16 (Vertical TikTok/Reels)` · Độ dài mỗi clip `4s – 5s`

---

## 📊 PHẦN 1: NGHIÊN CỨU & PHÂN TÍCH — CẦN BAO NHIÊU CẢNH TRÁM B-ROLL CHO KỊCH BẢN #01?

### 1.1. Con số tối ưu: **12 Cảnh Trám B-Roll** (Tương đương **13 Clip ngắn 4s–5s** trên Google Flow)
Với một video Talking Head (HeyGen) dài **75 giây (`01:15`)**, nếu giữ nguyên khung hình nhân vật nói quá **5 giây liên tục**, người xem TikTok sẽ nhận ra chuyển động lặp của AI Avatar và lướt qua ngay. Ngược lại, nếu đè B-roll kín 100% thời lượng thì sẽ mất đi **uy tín chuyên gia (Authority)** của người Cố vấn.

👉 **Tỷ lệ vàng cho Kịch bản #01 (`75 giây`)**:
* **Lộ mặt HeyGen (A-Roll)**: Chiếm **`~24 giây (32%)`** — xuất hiện ở 6 điểm neo cảm xúc (1.5s mở Hook, câu hỏi kết Hook, câu mở Chẩn đoán, câu dẫn vào Demo, câu mở Đúc kết CEO và câu đọc từ khóa `GIAIPHONG`).
* **Cảnh trám B-Roll (Track V2)**: Chiếm **`~51 giây (68%)`**, chia thành **12 cảnh trám B-Roll** (mỗi cảnh dài từ **`3.0s – 5.0s`**) bám sát từng hành động cụ thể trong lời thoại.

### 1.2. Bảng Phân Bổ 12 Cảnh Trám B-Roll Theo 4 Nhịp Kịch Bản #01

| Nhịp Kịch Bản | Thời Lượng | Số Cảnh Trám B-Roll | Lý Do Cần Trám Tại Các Điểm Này |
| :--- | :---: | :---: | :--- |
| **Nhịp 1: HOOK LỘ MẶT** | `00:00 – 00:05` *(5s)* | **1 Cảnh** *(Cảnh #01)* | 1.5s đầu lộ mặt tạo uy quyền ➔ Trám ngay **3.0s** cảnh văn phòng 20 nhân viên đã về hết, chỉ còn Sếp ngồi lại một mình lúc 22h đêm bên bảng lương trăm triệu ➔ 0.5s cuối cắt về mặt hỏi trực diện. |
| **Nhịp 2: CHẨN ĐOÁN NỖI ĐAU QUẢN TRỊ** | `00:05 – 00:22` *(17s)* | **4 Cảnh** *(Cảnh #02 ➔ #05)* | Lời thoại liệt kê **4 nỗi đau hình ảnh liên tiếp**: (1) Gõ lại từng báo giá ➔ (2) Trả lời lặp lại câu hỏi khách ➔ (3) Mất cả chiều viết 1 bài bán hàng ➔ (4) Sếp mất 4 tiếng/ngày ngồi đọc, duyệt và sửa lỗi cơ bản. Mỗi ý cần đúng **1 cảnh B-roll 3s–4.5s** để người xem "thấy mình trong đó". |
| **Nhịp 3: DEMO MÀN HÌNH & HỆ THỐNG** | `00:22 – 00:55` *(33s)* | **5 Cảnh** *(Cảnh #06 ➔ #10)* | Đoạn này dài 33 giây. Nếu chỉ chiếu 1 tấm ảnh chụp màn hình đứng yên suốt 33 giây thì tỷ lệ thoát trang (Drop-off) sẽ rất cao. Cần tách thành **5 cảnh B-roll động**: (1) Bảng Ma trận 2 cột ➔ (2) Bước 1: Gom việc vào Khung AI Chuẩn hóa ➔ (3) Bước 2A: Chạy qua Trợ lý AI Kiểm duyệt ➔ (4) Bước 2B: AI bắt lỗi & chấm điểm `8.5/10` ➔ (5) Kết quả: Sếp giảm từ 4 tiếng sửa bài xuống còn 20 phút/ngày. |
| **Nhịp 4: ĐÚC KẾT CEO & CTA CHUYỂN ĐỔI** | `00:55 – 01:15` *(20s)* | **2 Cảnh** *(Cảnh #11 ➔ #12)* | Giữ lộ mặt ở câu đúc kết mở đầu, sau đó trám **Cảnh #11** (So sánh tuyển thêm Phó GĐ phình quỹ lương vs Cắm AI vào khâu trung gian) và **Cảnh #12** (Cận cảnh bộ tài liệu quà tặng *"Bảng Kiểm toán 20 đầu việc SME"* khi đọc từ khóa `GIAIPHONG`). |

---

## 🎬 PHẦN 2: CHI TIẾT 12 CẢNH TRÁM & PROMPT TẠO VIDEO B-ROLL TRÊN GOOGLE FLOW (VEO)

---

### 🔹 NHỊP 1: HOOK LỘ MẶT (`00:00 – 00:05`)

* **`00:00 – 00:01.5` [Lộ mặt HeyGen]**: *"Nuôi một bộ máy 15, 20 nhân sự..."*
* **`00:01.5 – 00:04.5` [CHÈN B-ROLL #01]** (`3.0s`): *"...**mỗi tháng ngốn hơn trăm triệu tiền lương, nhưng người về muộn nhất và mệt nhất công ty vẫn là bạn**."*
* **`00:04.5 – 00:05.0` [Lộ mặt HeyGen]**: *"Bạn có từng tự hỏi tại sao chưa?"*

#### 🎯 Cảnh B-Roll #01 (`00:01.5 – 00:04.5` | Thời lượng: `3.0s`) — Văn phòng 20 bàn trống không lúc đêm muộn, chỉ còn Sếp sáng đèn
* **Ý đồ đạo diễn**: Máy quay lướt qua dãy 15–20 bàn làm việc của nhân viên đã tắt màn hình, ghế đẩy gọn gàng vì đã tan làm, tiến thẳng về phía phòng kính của Giám đốc ở cuối hành lang vẫn sáng đèn vàng ấm, nơi vị CEO đang ngồi thở dài mệt mỏi trước chồng hồ sơ và bảng chi lương.
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video, realistic commercial film quality. Smooth dolly push-in shot moving through a dark, empty modern open-plan office at 10 PM where 20 employee desks have turned-off monitors and empty chairs. At the end of the hall, a glass-walled executive office is the only room still lit with warm tungsten lamp light, revealing a tired 35-year-old Vietnamese male CEO in a white dress shirt with loosened tie sitting alone, rubbing his eyes in exhaustion amidst stacks of payroll sheets and laptops. High-contrast moody teal and amber lighting, shallow depth of field, 4k photorealistic, no text overlays.
```

---

### 🔹 NHỊP 2: CHẨN ĐOÁN NỖI ĐAU QUẢN TRỊ (`00:05 – 00:22`)

* **`00:05.0 – 00:07.5` [Lộ mặt HeyGen]**: *"Lý do không phải vì nhân viên của bạn kém. Mà vì 70% quỹ thời gian quý giá của họ đang bị chôn vùi vào những tác vụ thủ công lặp đi lặp lại:"*

#### 🎯 Cảnh B-Roll #02 (`00:07.5 – 00:10.5` | Thời lượng: `3.0s`) — Nhân viên ngồi gõ lại từng cái báo giá thủ công
* **Lời thoại khớp hình**: *"...**ngồi gõ lại từng cái báo giá**..."*
* **Ý đồ đạo diễn**: Cận cảnh nhân viên văn phòng đang nhìn giấy ghi chú rồi cặm cụi gõ từng con số, copy-paste từng dòng vào bảng báo giá Excel/Word trên màn hình với tốc độ chậm chạp, vẻ mặt uể oải.
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video. Close-up over-the-shoulder shot of a Vietnamese office employee sitting at a cluttered desk, looking back and forth between a paper calculator and a computer monitor, slowly typing numbers one by one into a complex spreadsheet price quotation table. Repetitive manual office work atmosphere, warm muted office lighting, shallow depth of field, 4k photorealistic, no gibberish text.
```

#### 🎯 Cảnh B-Roll #03 (`00:10.5 – 00:13.5` | Thời lượng: `3.0s`) — Trả lời đi trả lời lại những câu hỏi giống hệt nhau của khách
* **Lời thoại khớp hình**: *"...**trả lời đi trả lời lại những câu hỏi giống hệt nhau của khách**..."*
* **Ý đồ đạo diễn**: Nhân viên trực page/CSKH đeo tai nghe trước màn hình máy tính và điện thoại liên tục nảy bong bóng tin nhắn chat giống nhau, hai tay gõ phím liên hồi trong trạng thái quá tải.
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video. Medium close-up shot of a stressed Vietnamese female customer service staff wearing a headset in a busy SME office, frantically typing replies on both a laptop and two smartphones propped on her desk as endless chat message bubbles pop up on the screens. Fast-paced overwhelming atmosphere, cool screen reflection on her face, smooth camera pan, 4k photorealistic.
```

#### 🎯 Cảnh B-Roll #04 (`00:13.5 – 00:16.5` | Thời lượng: `3.0s`) — Mất cả buổi chiều mới viết xong một bài đăng bán hàng
* **Lời thoại khớp hình**: *"...**hay mất cả buổi chiều mới viết xong một bài đăng bán hàng**."*
* **Ý đồ đạo diễn**: Cảnh nhân viên Marketing ngồi trước màn hình soạn thảo văn bản gần như trắng trơn với con trỏ nhấp nháy, tay chống cằm vò đầu suy nghĩ trong khi ánh nắng ngoài cửa sổ chuyển dần từ trưa sang chiều muộn (Time-lapse nhẹ).
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video. Medium shot of a frustrated young Vietnamese marketing employee sitting at an office desk staring at a nearly blank document on a laptop screen with a blinking cursor. He sighs, deletes a line of text, and rests his head on his hand in writer's block while sunlight through the window shifts rapidly from bright afternoon to golden sunset, showing hours wasted on a single social media post. 4k photorealistic, cinematic lighting.
```

#### 🎯 Cảnh B-Roll #05 (`00:16.5 – 00:22.0` | Thời lượng: `5.5s`) — Sếp mất 4 tiếng mỗi ngày ngồi đọc, duyệt và sửa lỗi cơ bản cho nhân viên
* **Lời thoại khớp hình**: *"Và tệ hơn nữa, **chính bạn lại mất 4 tiếng mỗi ngày chỉ để ngồi đọc, duyệt và sửa những lỗi cơ bản đó cho nhân viên**."*
* **Ý đồ đạo diễn**: Cảnh vị Giám đốc ngồi tại bàn làm việc chất đầy các bản thảo hợp đồng, báo giá và bài viết của nhân viên trình lên. Sếp cầm cây bút đỏ gạch sửa chi chít các lỗi sai cơ bản trên giấy và trên màn hình laptop, lắc đầu ngao ngán nhìn đồng hồ điểm qua 4 tiếng đồng hồ.
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video. Medium close-up shot of a 35-year-old Vietnamese male CEO at his executive desk surrounded by stacks of employee reports and draft contracts. He holds a red pen, circling basic formatting mistakes and crossing out errors on printed pages while comparing them to a laptop screen, shaking his head in frustration as a desk clock in the foreground shows hours passing by. Dramatic corporate lighting, shallow depth of field, 4k photorealistic.
```

---

### 🔹 NHỊP 3: DEMO MÀN HÌNH & QUY TRÌNH ĐÃ CẮM TRỢ LÝ AI (`00:22 – 00:55`)

* **`00:22.0 – 00:24.0` [Lộ mặt HeyGen]**: *"Hãy nhìn vào bảng cấu trúc vận hành mà tôi đã thiết lập lại cho một doanh nghiệp thương mại 18 nhân sự ở đây."*

#### 🎯 Cảnh B-Roll #06 (`00:24.0 – 00:29.0` | Thời lượng: `5.0s`) — Bảng Ma Trận Kiểm Toán Công Việc SME (2 Cột Đối Lập)
* **Lời thoại khớp hình**: *"Thay vì để nhân viên tự làm từ con số 0 rồi mang lên trình sếp duyệt:"*
* **Ý đồ đạo diễn**: Cận cảnh màn hình máy tính hiển thị **Bảng Ma Trận Kiểm Toán Công Việc SME** chia làm 2 cột rõ rệt: Bên trái màu đỏ trầm là quy trình thủ công rối rắm nhiều bước; Bên phải màu xanh dương – ngọc lục bảo là quy trình tự động hóa đã cắm Trợ lý AI gọn gàng, sáng rõ.
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video. Close-up over-the-shoulder shot of an AI business consultant demonstrating a sleek dark-mode studio monitor displaying a two-column comparison matrix UI. The left column glows in muted red showing a tangled, slow manual workflow; the right column glows in vibrant royal blue and emerald green showing a streamlined, automated AI-assisted workflow with clean connected nodes. Smooth slow dolly-in toward the monitor, high-end SaaS dashboard aesthetic, 4k, no messy text.
```

#### 🎯 Cảnh B-Roll #07 (`00:29.0 – 00:37.0` | Thời lượng: `8.0s` — tách làm 2 clip 4s: #07A & #07B) — Bước 1: Gom các tác vụ lặp lại vào Khung Quy Trình AI Chuẩn Hóa
* **Lời thoại khớp hình**: *"- **Bước 1:** Chúng tôi **gom toàn bộ các tác vụ lặp lại của từng bộ phận — từ viết kịch bản quảng cáo, soạn hợp đồng, đến tổng hợp số liệu cuối ngày — đưa vào một Khung Quy trình AI Chuẩn hóa**."*

##### 🔸 Clip #07A (`00:29.0 – 00:33.0` | `4.0s`): Gom việc viết kịch bản, soạn hợp đồng, tổng hợp số liệu
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video. Modern 3D motion graphic style blended with live-action office view: floating translucent digital cards representing ad scripts, legal contracts, and daily financial charts smoothly converge from different office desks into a central glowing blue AI workflow hub on a glass boardroom screen. Sleek futuristic corporate visual, smooth camera tracking, 4k.
```

##### 🔸 Clip #07B (`00:33.0 – 00:37.0` | `4.0s`): Đưa vào Khung Quy Trình AI Chuẩn Hóa (Standardized AI Framework)
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video. Close-up shot of an employee's computer screen showing a clean, standardized Notion and AI workflow dashboard where department templates lock neatly into structured modules with glowing cyan connection lines, generating complete drafts in seconds with a single click. Crisp shallow depth of field, modern tech office lighting, 4k, no garbled text.
```

#### 🎯 Cảnh B-Roll #08 (`00:37.0 – 00:43.0` | Thời lượng: `6.0s`) — Bước 2 (Phần A): Chạy qua Trợ Lý AI Kiểm Duyệt Nội Bộ trước khi trình Sếp
* **Lời thoại khớp hình**: *"- **Bước 2:** Trước khi bất kỳ công việc nào được gửi lên cho Giám đốc, **nhân viên bắt buộc phải chạy qua một Trợ lý AI Kiểm duyệt Nội bộ đã được nạp sẵn tiêu chuẩn của sếp**."*
* **Ý đồ đạo diễn**: Nhân viên văn phòng sau khi làm xong báo cáo liền kéo thả file vào giao diện **Trợ lý AI Kiểm duyệt Nội bộ (AI Quality Gate)** trên màn hình máy tính, một luồng ánh sáng quét dọc qua tài liệu để kiểm tra theo bộ tiêu chuẩn của Giám đốc.
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video. Over-the-shoulder shot of a Vietnamese office staff member dragging a completed document file into an AI Quality Control Assistant interface on a sleek monitor. A glowing blue laser scan line sweeps vertically across the document page, cross-checking it against a sidebar of golden executive standard rules. High-tech corporate workflow aesthetic, smooth camera push-in, 4k photorealistic.
```

#### 🎯 Cảnh B-Roll #09 (`00:43.0 – 00:49.0` | Thời lượng: `6.0s`) — Bước 2 (Phần B): AI tự bắt lỗi chính tả, kiểm tra báo giá và chấm điểm đạt trên 8/10
* **Lời thoại khớp hình**: *"Con AI này **tự động bắt lỗi chính tả, kiểm tra thông số báo giá và chấm điểm đạt trên 8/10 thì mới được phép trình lên cho bạn**."*
* **Ý đồ đạo diễn**: Cận cảnh màn hình giao diện AI tự động khoanh vùng sửa các điểm lỗi đỏ thành màu xanh lá chuẩn xác, kiểm tra bảng số liệu khớp 100%, rồi vòng tròn điểm số trên màn hình quay vọt lên mức xanh lá **9/10 (Approved)** kèm nút gửi trình Giám đốc phát sáng.
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video. Macro close-up of a dark-mode AI review screen where red error highlights on a document automatically transform into clean emerald green checkmarks, financial table bars align perfectly, and a circular quality score gauge smoothly animates upward into a glowing green 90% approved badge. Crisp UI motion lighting, shallow depth of field, 4k, no unreadable text.
```

#### 🎯 Cảnh B-Roll #10 (`00:49.0 – 00:55.0` | Thời lượng: `6.0s`) — Kết quả: Thời gian Sếp ngồi sửa việc vặt giảm từ 4 tiếng xuống 20 phút/ngày
* **Lời thoại khớp hình**: *"- Kết quả là **thời gian sếp phải ngồi sửa việc vặt giảm từ 4 tiếng xuống chỉ còn đúng 20 phút mỗi ngày**."*
* **Ý đồ đạo diễn**: Cảnh vị Giám đốc phong thái điềm đạm, thảnh thơi ngồi nhâm nhi tách cà phê sáng trong văn phòng ngập nắng, chỉ cần lướt nhẹ trên iPad bấm nút duyệt xanh lá các bản báo cáo đã đạt chuẩn của nhân viên, mỉm cười hài lòng rồi gập máy lại chỉ sau 20 phút.
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video. Medium shot of a relaxed, confident Vietnamese CEO in a tailored blazer sitting in a sunlit modern executive office in the morning. He holds a cup of coffee in one hand and effortlessly taps green approval buttons on a sleek iPad with the other hand, smiling with satisfaction as his desk remains completely clean and paper-free. Warm golden morning sunlight, smooth dolly camera movement, 4k photorealistic.
```

---

### 🔹 NHỊP 4: ĐÚC KẾT CEO & CTA CHUYỂN ĐỔI (`00:55 – 01:15`)

* **`00:55.0 – 00:58.0` [Lộ mặt HeyGen]**: *"Trong kỷ nguyên này, giải phóng lãnh đạo..."*

#### 🎯 Cảnh B-Roll #11 (`00:58.0 – 01:05.0` | Thời lượng: `7.0s`) — Không tuyển thêm Phó Giám đốc phình quỹ lương, mà cắm AI vào khâu trung gian
* **Lời thoại khớp hình**: *"...**không phải là tuyển thêm phó giám đốc cho phình quỹ lương, mà là cắm AI vào các khâu trung gian và nâng chuẩn đầu ra của nhân sự**."*
* **Ý đồ đạo diễn**: Góc máy rộng điện ảnh: Vị Chủ doanh nghiệp đứng quan sát văn phòng 18 nhân sự đang làm việc nhịp nhàng, giữa các bàn làm việc là các màn hình hệ thống AI tự động hóa luồng công việc mượt mà, không khí hiện đại, tinh gọn và hiệu suất cao.
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video, inspiring wide-to-medium tracking shot. A confident Vietnamese CEO stands in a sleek glass-walled office overlooking his lean team of 18 employees working in perfect synchronization with glowing AI automation dashboards on their monitors. Subtle futuristic light streams connect the workstations to the executive dashboard, symbolizing AI embedded into middle-management workflows. Warm gold and cyan corporate color grading, 4k commercial film look.
```

* **`01:05.0 – 01:08.0` [Lộ mặt HeyGen]**: *"Bạn hãy gõ từ khóa **'GIAIPHONG'** ở phần bình luận bên dưới..."*

#### 🎯 Cảnh B-Roll #12 (`01:08.0 – 01:15.0` | Thời lượng: `7.0s`) — Quà tặng CTA: Bảng Kiểm toán 20 đầu việc ngốn thời gian nhất trong SME bàn giao cho AI
* **Lời thoại khớp hình**: *"...**tôi sẽ gửi tặng bạn Bảng Kiểm toán 20 đầu việc ngốn thời gian nhất trong SME có thể bàn giao ngay cho AI trong tuần này**."*
* **Ý đồ đạo diễn**: Cận cảnh thương mại sang trọng: Bộ tài liệu **"Bảng Kiểm Toán 20 Đầu Việc SME"** đóng bìa chuyên nghiệp đặt cạnh chiếc MacBook Pro và iPad đang hiển thị danh sách 20 đầu việc được đánh dấu tích xanh bàn giao cho AI, bàn tay của Cố vấn đặt nhẹ lên tài liệu trao tặng.
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical product B-roll video. Luxury commercial close-up shot on an executive wooden desk: a sleek MacBook Pro and an iPad Pro display a clean, structured 20-row executive audit checklist with glowing green AI automation toggles, placed next to a premium navy-and-gold printed strategy workbook. A consultant's hand in a crisp suit cuff smoothly slides the workbook forward toward the camera as an invitation. Dramatic warm gold and cyan rim lighting, shallow depth of field, 4k photorealistic.
```

<!-- ===== /file: heygen-veo-broll-video/references/PROMPT_TAO_VIDEO_BROLL_KICH_BAN_01_GOOGLE_FLOW.md ===== -->

<!-- ===== file: heygen-veo-broll-video/references/PROMPT_TAO_VIDEO_BROLL_KICH_BAN_03_GOOGLE_FLOW.md ===== -->

# 🎬 TRỌN BỘ PROMPT TẠO VIDEO TRÁM CẢNH B-ROLL TRÊN GOOGLE FLOW (VEO) — KỊCH BẢN #03

> **Kịch bản**: **BÀI #03 (Thứ 5 - TOFU): Sai lầm chết người khi Chủ doanh nghiệp đi học câu lệnh AI lẻ tẻ như một nhân viên**  
> **Từ khóa Lead (CTA)**: `TUDUYAI`  
> **Định dạng khuyến nghị trên Google Flow**: `Text-to-Video` · Tỷ lệ `9:16 (Vertical TikTok/Reels)` · Thời lượng mỗi clip `4s – 5s`

---

## 🗺️ SƠ ĐỒ ĐIỂM CHÈN B-ROLL TRÊN TIMELINE HEYGEN (`00:00 – 01:15`)

Nguyên tắc dựng kết hợp **HeyGen Talking Head (Track V1)** và **Video B-Roll Google Flow (Track V2)**:
- **Giữ lộ mặt HeyGen** ở `1.5s – 2s` đầu mỗi nhịp để giữ kết nối mắt (Eye Contact) với người xem.
- **Đè cảnh B-Roll (Track V2)** ngay tại các cụm từ khóa hình ảnh (được bôi đậm bên dưới) để minh họa trực quan nỗi đau và giải pháp, tránh cảm giác "nói chay" một góc máy.

---

## PHẦN 1: NHỊP 1 — HOOK LỘ MẶT (`00:00 – 00:05`)

* **00:00 – 00:01.5**: Giữ **Lộ mặt HeyGen** mở đầu đanh thép: *"90% chủ doanh nghiệp..."*
* **00:01.5 – 00:05.0**: **CHÈN B-ROLL #01**

### 🎯 Cảnh B-Roll #01 (`00:01.5 – 00:05.0` | Thời lượng: `3.5s`)
* **Lời thoại khớp hình**: *"...đi học các lớp AI về đều **bỏ xó chỉ sau đúng 2 tuần**. Không phải vì AI không hiệu quả, mà vì bạn đang học AI theo cách của một nhân viên thực thi, chứ không phải của một người điều hành."*
* **Ý đồ hình ảnh**: Cảnh một chủ doanh nghiệp Việt Nam ngồi trong lớp hội thảo cuối tuần hăng say ghi chép tài liệu AI, sau đó chuyển cảnh mượt (match-cut) sang cảnh cuốn sổ tay & tập tài liệu khóa học AI bị vứt lăn lóc, phủ bụi ở góc bàn làm việc tối đèn sau 2 tuần.
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video, realistic commercial film style. A sleek whip-pan transition between two moments: First, a 35-year-old Vietnamese business owner in a smart blazer sitting in a weekend seminar room eagerly taking notes in a leather notebook with a laptop showing AI interfaces. Then, the camera pans smoothly to a moody executive office desk two weeks later where that exact same notebook and printed course materials lie tossed aside and untouched in a dim corner next to a cold cup of coffee, while a blurred calendar pages flip rapidly in the background. Shallow depth of field, dramatic warm amber and cool teal corporate color grading, 4k photorealistic, no text overlays.
```

---

## PHẦN 2: NHỊP 2 — CHẨN ĐOÁN NỖI ĐAU QUẢN TRỊ (`00:05 – 00:25`)

* **00:05.0 – 00:06.5**: Cắt về **Lộ mặt HeyGen**: *"Hãy nhìn lại mà xem:"*
* **00:06.5 – 00:11.5**: **CHÈN B-ROLL #02**
* **00:11.5 – 00:18.5**: **CHÈN B-ROLL #03**
* **00:18.5 – 00:20.0**: Cắt nhanh về **Lộ mặt HeyGen**: *"Nếu người làm chủ học AI chỉ để tự tay ngồi làm thay việc của nhân viên..."*
* **00:20.0 – 00:25.0**: **CHÈN B-ROLL #04**

---

### 🎯 Cảnh B-Roll #02 (`00:06.5 – 00:11.5` | Thời lượng: `5.0s`)
* **Lời thoại khớp hình**: *"Bạn bỏ ra vài ngày cuối tuần **đi học cách gõ câu lệnh viết bài Facebook, cách dùng AI vẽ ảnh, cắt video**."*
* **Ý đồ hình ảnh**: Góc máy qua vai (Over-the-shoulder) quay cảnh vị Giám đốc ngồi một mình trong văn phòng vắng vẻ ngày cuối tuần, cặm cụi gõ từng câu lệnh dài trên màn hình laptop, mở nhiều tab tạo ảnh AI và timeline cắt ghép video nhỏ lẻ, vẻ mặt mệt mỏi và căng thẳng.
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video, over-the-shoulder medium close-up shot. A tired Vietnamese male CEO in his 30s wearing glasses and a rolled-up dress shirt sits alone in a quiet modern office on the weekend. He hunches closely over a glowing laptop screen, typing long text prompts with two fingers while switching between social media post drafts, AI image generation grids, and a video editing timeline on his monitor. Cool blue monitor light reflects on his glasses, slow dolly-in camera movement, realistic modern office atmosphere, 4k, no unreadable text.
```

---

### 🎯 Cảnh B-Roll #03 (`00:11.5 – 00:18.5` | Thời lượng: `7.0s` — có thể tách làm 2 clip 3.5s: #03A & #03B)

#### 🔹 Clip #03A (`00:11.5 – 00:15.0` | `3.5s`): Sếp ngập đầu trong công việc ở ngày thứ 4
* **Lời thoại khớp hình**: *"Về đến công ty, bạn hào hứng tự ngồi làm được 3 hôm, **đến hôm thứ 4 công việc kinh doanh ngập đầu, bạn không có thời gian gõ lệnh nữa**..."*
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video. Dynamic medium shot of a stressed Vietnamese male CEO sitting at his executive desk on a busy weekday morning. Assistants walk in placing thick stacks of paper contracts and financial reports onto his desk while his smartphone rings nonstop. He closes his laptop in frustration, takes off his glasses, and rubs his forehead overwhelmed by management workload. Fast-paced realistic corporate office environment, natural daylight mixed with warm office lighting, 4k photorealistic.
```

#### 🔹 Clip #03B (`00:15.0 – 00:18.5` | `3.5s`): Nhân viên vẫn làm việc thủ công theo lối cũ
* **Lời thoại khớp hình**: *"...**còn nhân viên của bạn thì vẫn làm việc theo lối cũ. Thế là mọi thứ quay về vạch xuất phát**."*
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video. Rack focus shot from an overwhelmed CEO in the foreground to the open-plan office behind a glass partition where 6 office employees are working slowly the old-fashioned way—manually typing one finger at a time into messy spreadsheets, flipping through thick paper binders, and passing sticky notes by hand. Moody desaturated corporate lighting conveying inefficiency and stagnation, smooth camera pull-back, 4k photorealistic.
```

---

### 🎯 Cảnh B-Roll #04 (`00:20.0 – 00:25.0` | Thời lượng: `5.0s`)
* **Lời thoại khớp hình**: *"...bạn đang **tự trả lương Giám đốc cho một công việc của thực tập sinh**."*
* **Ý đồ hình ảnh**: Cảnh ẩn dụ điện ảnh (Visual Metaphor) cực đắt giá: Máy quay lia từ chiếc bảng tên chức danh **"CEO / GIÁM ĐỐC"** mạ vàng sang trọng trên bàn gỗ óc chó, kéo rộng ra thấy vị Giám đốc mặc vest lịch lãm nhưng lại đang ngồi còng lưng cặm cụi làm công việc tay chân vụn vặt như một thực tập sinh giữa đống giấy tờ lộn xộn.
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video, dramatic visual metaphor. The shot starts with a macro close-up of a luxury gold-plated executive desk nameplate gleaming under warm spotlight, then smoothly pulls back and tilts up to reveal a Vietnamese CEO in an expensive tailored suit hunched awkwardly over a cluttered desk, manually cutting paper, sorting sticky notes, and typing repetitive data like an overworked intern. High-contrast dramatic lighting, shallow depth of field, Arri Alexa commercial look, 4k.
```

---

## PHẦN 3: NHỊP 3 — DEMO MÀN HÌNH & MINH HỌA THÁP 3 TẦNG CHUYỂN ĐỔI AI (`00:25 – 00:55`)

* **00:25.0 – 00:27.5**: Cắt về **Lộ mặt HeyGen** (hoặc Picture-in-Picture góc dưới): *"Khi tôi cố vấn và đào tạo cho các doanh nghiệp từ 5 đến 50 nhân sự, người làm chủ chỉ cần nắm 3 việc cốt lõi trên màn hình này:"*
* **00:27.5 – 00:31.0**: **CHÈN B-ROLL #05** (Tổng quan Tháp 3 Tầng)
* **00:31.0 – 00:39.0**: **CHÈN B-ROLL #06** (Tầng 1: Rút ngắn 4 tiếng xuống 15 phút)
* **00:39.0 – 00:47.0**: **CHÈN B-ROLL #07** (Tầng 2: Thiết lập tiêu chuẩn & Biểu mẫu AI cố định)
* **00:47.0 – 00:55.0**: **CHÈN B-ROLL #08** (Tầng 3: Đào tạo đội ngũ bấm nút & CEO kiểm soát KPI đầu ra)

---

### 🎯 Cảnh B-Roll #05 (`00:27.5 – 00:31.0` | Thời lượng: `3.5s`) — Tổng Quan Tháp 3 Tầng Chuyển Đổi AI
* **Lời thoại khớp hình**: *"...người làm chủ chỉ cần nắm **3 việc cốt lõi trên màn hình này**:"*
* **Ý đồ hình ảnh**: Màn hình máy tính / không gian 3D Hologram trên bàn họp chiến lược hiển thị khối **Kim Tự Tháp 3 Tầng (3-Tier AI Transformation Pyramid)** phát sáng tuần tự từ Tầng đáy (Tầng 1) lên Tầng giữa (Tầng 2) và Đỉnh tháp (Tầng 3).
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video. Close-up over-the-shoulder shot of a strategic AI consultant pointing a stylus pen at a sleek large dark-mode studio monitor in a modern boardroom. On the screen, a clean futuristic 3-tier glowing architectural pyramid diagram animates sequentially from bottom tier (amber gold) to middle tier (royal blue) to top apex (emerald green) with clean minimalist workflow nodes and progress bars. Smooth camera push-in, high-tech B2B consulting aesthetic, 4k, no gibberish text.
```

---

### 🎯 Cảnh B-Roll #06 (`00:31.0 – 00:39.0` | Thời lượng: `8.0s` — tách 2 clip 4s: #06A & #06B) — Tầng 1: Hiểu Giới Hạn Công Nghệ (4 Tiếng ➔ 15 Phút)
* **Lời thoại khớp hình**: *"- **Tầng 1 – Hiểu giới hạn công nghệ:** Bạn cần biết rõ **tác vụ nào trong công ty AI có thể rút ngắn từ 4 tiếng xuống 15 phút** để **không bị nhân viên báo cáo khống thời gian**."*

#### 🔹 Clip #06A (`00:31.0 – 00:35.0` | `4.0s`): Rút ngắn 4 tiếng làm tay xuống 15 phút bằng AI
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical split-screen comparison B-roll video. Top half in warm muted tones shows an employee struggling for hours with a wall clock spinning fast and stacks of paperwork piling up. Bottom half in crisp futuristic cyan-blue lighting shows the same task completed in seconds as an AI workflow progress bar rapidly fills to 100% with green checkmarks on a sleek monitor. Dynamic modern commercial motion, 4k photorealistic.
```

#### 🔹 Clip #06B (`00:35.0 – 00:39.0` | `4.0s`): CEO nắm định mức thời gian, chặn báo cáo khống
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video. A sharp, confident Vietnamese CEO sits at his desk reviewing a digital time-audit dashboard on a tablet while an employee stands across the desk holding a paper report. The CEO calmly taps the tablet screen showing green efficiency metrics and shakes his head slightly with a knowing smile, signaling complete transparency over task duration. Crisp executive office lighting, shallow depth of field, 4k.
```

---

### 🎯 Cảnh B-Roll #07 (`00:39.0 – 00:47.0` | Thời lượng: `8.0s` — tách 2 clip 4s: #07A & #07B) — Tầng 2: Thiết Lập Tiêu Chuẩn (Biểu Mẫu AI Cố Định)
* **Lời thoại khớp hình**: *"- **Tầng 2 – Thiết lập tiêu chuẩn (Standardization):** **Cùng các trưởng bộ phận đóng gói kiến thức của công ty** thành các **Biểu mẫu AI cố định cho từng vị trí**."*

#### 🔹 Clip #07A (`00:39.0 – 00:43.0` | `4.0s`): CEO họp cùng các Trưởng bộ phận đóng gói chất xám
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video. A collaborative strategy session in a glass-walled SME boardroom: a Vietnamese CEO and three department heads stand around a large interactive digital whiteboard, organizing glowing modular workflow cards and connecting company knowledge nodes into a standardized system. Warm professional lighting, smooth tracking camera movement around the table, 4k photorealistic.
```

#### 🔹 Clip #07B (`00:43.0 – 00:47.0` | `4.0s`): Biểu mẫu AI cố định cho từng vị trí nhân sự
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video. Close-up shot of a clean dark-mode Notion-style workflow interface on a desktop monitor where standardized AI template cards neatly snap into a structured 2x2 grid for different departments, glowing with blue and emerald status indicators as an employee simply selects a preset template with one mouse click. Smooth macro camera pan across the screen, 4k, clean UI visual without messy text.
```

---

### 🎯 Cảnh B-Roll #08 (`00:47.0 – 00:55.0` | Thời lượng: `8.0s` — tách 2 clip 4s: #08A & #08B) — Tầng 3: Đào Tạo Thực Chiến & Đo Lường KPI Mới
* **Lời thoại khớp hình**: *"- **Tầng 3 – Đào tạo & Đo lường KPI mới:** **Đưa đội ngũ nhân sự vào chương trình huấn luyện thực chiến để chính họ là người bấm nút vận hành hệ thống đó mỗi ngày**, còn **bạn chỉ kiểm soát kết quả đầu ra**."*

#### 🔹 Clip #08A (`00:47.0 – 00:51.0` | `4.0s`): Huấn luyện thực chiến — Đội ngũ nhân sự đồng loạt bấm nút vận hành
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video. An energetic hands-on AI training workshop inside a modern Vietnamese company office: a row of 10 young office staff sitting at dual-monitor workstations simultaneously press enter on their keyboards with confident smiles as automated AI workflows launch across their screens. Dynamic dolly shot moving down the aisle of desks, bright inspiring tech-corporate lighting, 4k.
```

#### 🔹 Clip #08B (`00:51.0 – 00:55.0` | `4.0s`): CEO thảnh thơi chỉ kiểm soát kết quả đầu ra (Output KPI)
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video. A calm, composed Vietnamese CEO in a tailored blazer stands by a floor-to-ceiling office window holding a cup of espresso and a sleek tablet displaying rising green KPI charts and completion gauges. In the soft-focus background, his entire team works smoothly and autonomously at their desks. Warm golden-hour sunlight streaming through the glass, slow camera push-in, 4k photorealistic.
```

---

## PHẦN 4: NHỊP 4 — ĐÚC KẾT CEO & CTA CHUYỂN ĐỔI (`00:55 – 01:15`)

* **00:55.0 – 00:57.0**: Cắt về **Lộ mặt HeyGen**: *"Đừng biến mình thành người giỏi công cụ nhất công ty..."*
* **00:57.0 – 01:03.5**: **CHÈN B-ROLL #09**
* **01:03.5 – 01:07.0**: Cắt về **Lộ mặt HeyGen** kêu gọi trực diện: *"Comment từ khóa 'TUDUYAI' bên dưới..."*
* **01:07.0 – 01:15.0**: **CHÈN B-ROLL #10** (hoặc chia đôi màn hình: Trên lộ mặt HeyGen, Dưới chạy B-Roll #10)

---

### 🎯 Cảnh B-Roll #09 (`00:57.0 – 01:03.5` | Thời lượng: `6.5s`)
* **Lời thoại khớp hình**: *"...**hãy biến mình thành người sở hữu đội ngũ biết dùng AI giỏi nhất**."*
* **Ý đồ hình ảnh**: Góc máy Hero Shot từ dưới hướng nhẹ lên (Low-angle Hero Shot): Vị Chủ doanh nghiệp đứng chính giữa văn phòng hiện đại với phong thái thủ lĩnh đĩnh đạc, hai bên phía sau là đội ngũ nhân sự trẻ trung, chuyên nghiệp đang làm việc tốc độ cao cùng hệ thống AI.
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical B-roll video, inspiring low-angle hero shot. A confident Vietnamese male CEO in a sharp dark navy suit stands in the center aisle of a modern high-tech office with arms crossed and a calm, authoritative smile. Behind him on both sides, a synchronized team of 12 young professionals work efficiently on glowing dual-monitor AI workstations. Slow cinematic dolly-in toward the CEO, warm golden rim light and sleek cyan office accents, 4k commercial film quality.
```

---

### 🎯 Cảnh B-Roll #10 (`01:07.0 – 01:15.0` | Thời lượng: `8.0s`)
* **Lời thoại khớp hình**: *"Comment từ khóa **'TUDUYAI'** bên dưới để nhận **Bản đồ Lộ trình Chuyển đổi AI dành riêng cho CEO & Chủ doanh nghiệp SME**."*
* **Ý đồ hình ảnh**: Cảnh quay sản phẩm (Product B-roll) sang trọng: Cuốn hồ sơ chiến lược bìa cứng màu xanh đen mạ vàng kết hợp chiếc iPad Pro đặt trên bàn đá cẩm thạch đang mở sẵn sơ đồ Lộ trình Chuyển đổi AI 3 tầng rực sáng, bàn tay Giám đốc lướt nhẹ mở trang tài liệu.
* **Prompt tạo Video Google Flow (Copy vào ô Prompt):**
```text
Cinematic 9:16 vertical product B-roll video. Close-up luxury commercial shot on a dark marble executive desk: a sleek iPad Pro and an executive navy-and-gold strategy binder open side by side, displaying a glowing, well-structured architectural AI transformation roadmap flowchart with three distinct tiers and green milestone nodes. A businessman's hand wearing a classic mechanical watch smoothly swipes the tablet screen to reveal the full blueprint. Dramatic warm gold and cyan rim lighting, shallow depth of field, 4k.
```

<!-- ===== /file: heygen-veo-broll-video/references/PROMPT_TAO_VIDEO_BROLL_KICH_BAN_03_GOOGLE_FLOW.md ===== -->

<!-- ===== file: heygen-veo-broll-video/references/README-preset.md ===== -->

# Preset render talking head — Kênh AI Doanh Nghiệp (anh Huy)

Chốt ngày 26/10/2026: dùng **bản B — photo avatar sân golf** làm chuẩn cho toàn bộ 30 kịch bản.

## Thông số đã khóa

| Mục | Giá trị |
|-----|---------|
| Avatar look | `761364fad106369de1c3ada3994aee9c` — "AHuy - Golf Cart CEO" |
| Avatar group | `d2ca30ee30804228ada59ec6a0f596e3` — nhóm "AHuy" (chung với digital twin cũ) |
| Voice | `09bed03ed2984542836268ac73ffc18c` — voice clone AHuy, tiếng Việt, nam |
| Khung hình | 9:16, 1080p, fit `cover` |
| Engine | Avatar IV (mặc định) |
| Expressiveness | `medium` |
| Motion prompt | executive nói thẳng camera, quay đầu tự nhiên, giữ eye contact |

API: `POST https://api.heygen.com/v3/videos`, header `X-Api-Key`.

## Cách render một bài

```powershell
$env:HEYGEN_KEY = "<api key>"
python render.py 5                 # chỉ in lời thoại, KHÔNG tốn credit
python render.py 5 --yes           # render thật + tự tải về folder này
```

Luôn chạy lần 1 không có `--yes` để đọc lại lời thoại. Script tự bóc markdown,
nhưng **không tự sửa** ba thứ sau — phải tự tay chỉnh rồi render bằng `--text`:

1. **Ký tự `%`** — viết thành chữ. `90%` → "chín mươi phần trăm".
2. **Từ khóa comment viết liền** — `TUDUYAI` → "TƯ DUY AI", `HUANLUYEN` → "HUẤN LUYỆN".
3. **Chữ số nhạy cảm** — nghe lại đoạn có số, giọng đọc đôi khi đọc sai.

Quy trình khi cần sửa tay:

```powershell
python render.py 5 > bai05-huanluyen-loi-thoai.txt   # rồi mở file ra sửa
python render.py 5 --text bai05-huanluyen-loi-thoai.txt --yes
```

## Chi phí thực tế

Đo trên 2 video đầu, mỗi video 1 phút 40 giây ở 1080p:

- **~130 plan credit + ~$6.6 ví** cho mỗi video.
- Số dư sau bài #03: **243 credit, $12.15** — chỉ đủ thêm khoảng 2 bài.

Cách giảm nếu chạy hết 30 bài:

- Hạ `RESOLUTION` xuống `"720p"` trong `render.py`.
- Chỉ render phần talking head (00:00–00:25 và 00:55–01:15). Đoạn giữa 00:25–00:55
  là screen demo, bị che 70–80% khung hình theo brief kênh — render mặt ở đó là phí tiền.

## Phần API không làm được

- **Phụ đề**: HeyGen không trả `.srt` cho preset này. Phải tự làm bằng CapCut/Premiere.
- **Screen demo**: đoạn 00:25–00:55 phải tự quay màn hình rồi ghép picture-in-picture.
  Quy chuẩn kênh: zoom 150–200%, khoanh đỏ các con số tài chính / thời gian.

## File trong folder

- `render.py` — script render, đọc preset ở đầu file.
- `kich-ban-30-bai.json` — trọn bộ 30 kịch bản lấy từ trang dashboard.
- `bai03-tuduyai-B-photo-golf.mp4` — bản chuẩn đã duyệt.
- `bai03-tuduyai-A-digital-twin.mp4` — bản so sánh, dùng digital twin cũ (đã loại).

<!-- ===== /file: heygen-veo-broll-video/references/README-preset.md ===== -->
