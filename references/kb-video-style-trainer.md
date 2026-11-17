# kb-video-style-trainer — toàn văn tài liệu của nguồn `video-style-trainer`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/video-style-trainer/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: video-style-trainer/SKILL.md ===== -->
---
name: video-style-trainer
description: Huấn luyện và đóng gói skill edit video mới từ video mẫu theo quy trình 5 Phase + 4 Round Feedback Loop (chuẩn Thơ EDITOR @lopphovlog). Dùng khi người dùng muốn "train skill edit video", "học style từ video mẫu", "talking head ui", "nhân bản style edit", "phân tích video mẫu tạo skill", hoặc biến một phong cách dựng (HyperFrames / Remotion / FilmCraft) thành skill 1-Prompt Production chạy được trên mọi máy.
---

# Video Style Trainer (`video-style-trainer`)

Biến **1 video mẫu** (để nhân bản chính xác 100%) hoặc **2–3 video cùng style** (để rút pattern chung) thành một **skill edit video hoàn chỉnh, 100% portable**, có khả năng chạy **1-Prompt Production** trên footage thô.

> Tham chiếu chi tiết nguồn quy trình: `references/lopphovlog-talking-head-blueprint.md`  
> Preset mặc định: `references/presets/talking-head-ui-hyperframes.json`  
> Template HyperFrames chuẩn: `templates/hyperframes-talking-head-ui/`

---

## Quy trình 5 Phase + Vòng lặp 4 Round

### Phase 1 — Chọn chiến lược video mẫu
- **Đúng 1 video mẫu:** Khi muốn **nhân bản chính xác 100%** đúng một phong cách cụ thể, không bị pha trộn chất của nhiều editor khác nhau.
- **2–3 video cùng style:** Khi muốn AI tự tách được **pattern cốt lõi lặp lại** (nhịp cắt, kiểu chữ, cấu trúc UI) khỏi các chi tiết ngẫu nhiên của từng video.

### Phase 2 — Phân tích 9 trục kỹ thuật + Đo máy + Nhìn khung hình
Chạy `style_trainer.py probe` để vừa **đo đạc thông số thật** (`ffprobe`, `scdet` cắt cảnh, `ebur128` loudness) vừa **xuất contact sheet** để AI nhìn trực tiếp từng khung hình (có thể bổ sung `faster-whisper` để lấy word-level timestamps và các công cụ đo đạc của `opa-video-studio` khi dựng).

Phân tích đầy đủ **9 trục kỹ thuật**:
1. **Nhịp dựng:** `cuts/10s`, `median_shot_sec`, chu kỳ chèn UI/zoom (`2.5–4.0s`).
2. **Typography:** Font, weight, tracking, **word-by-word highlight màu cho từ khoá**, độ to rõ khi **tắt tiếng trên điện thoại (Chữ = Âm thanh)**.
3. **Animation Text:** Đường cong **`ease-in-out` bắt buộc** (`cubic-bezier(0.42, 0, 0.58, 1)`), **cấm `linear`**; tốc độ đủ chậm (`text_speed_scale: 1.2`) để mắt đọc kịp.
4. **Fake Camera:** Zoom in / zoom out mượt ngay trên khung hình trong **10 giây đầu**.
5. **Motion Graphics & UI Elements:** Icon badge, glass card, orbit nodes, stat pill — **tuyệt đối không đè mặt người nói**.
6. **Face-Safe Zone:** Khai báo rõ `x_range` & `y_range` vùng khuôn mặt để tách chữ/UI ra ngoài.
7. **Transition:** Flash cam, smooth wipe, punch zoom theo nhịp cắt.
8. **Audio & SFX:** Giọng nói rõ nét, nhạc nền thấp hơn giọng `~-17 đến -22 LU`, SFX nhấn từng nhịp UI/chữ.
9. **Engine & Portability:** Đóng gói tương đối (`assets/`, `templates/`), không hardcode đường dẫn cá nhân.

Sau đó chạy `style_trainer.py scaffold` để sinh bộ khung skill mới.

### Phase 3 — Round 1: Baseline Test mù (Zero-Guidance)
- Lấy một đoạn footage talking head thô.
- Gửi cho skill vừa scaffold **chỉ 1 câu lệnh thật ngắn**, **cố tình KHÔNG hướng dẫn thêm** (không nhắc easing, cỡ chữ hay vị trí).
- Mục tiêu: Đo giới hạn tự động thực sự của skill ở phiên bản đầu tiên (thường bản Round 1 sẽ chưa đạt — đây là bước bắt buộc để lộ đúng điểm yếu cần sửa vĩnh viễn).

### Phase 4 — Round 2 → 3 → 4: Vòng lặp Feedback & Ghi đè vĩnh viễn
Mọi góp ý đều phải chạy qua `style_trainer.py feedback` để vừa ghi log vào `references/feedback-log.md`, vừa **cập nhật thẳng vào `config.json`** để mọi video sau tự động kế thừa:

- **Round 2 — Motion Speed & Ép `ease-in-out`:**
  - Nếu chữ chạy quá nhanh hoặc chuyển động đều cứng như máy (`linear`), chỉnh chậm lại và ép `ease-in-out` cho mọi keyframe:
  - `--set motion.easing=ease-in-out --set motion.text_speed_scale=1.2`
- **Round 3 — Visual Screenshot Feedback & Face-Safe Zone:**
  - *Mẹo vàng:* Lỗi liên quan tới vị trí / đè mặt / chữ nhỏ → **chụp ảnh màn hình đúng khung hình lỗi** gửi kèm `--screenshot <path>`. AI nhìn ảnh hiểu nhanh và chuẩn hơn mô tả bằng chữ.
  - Tăng cỡ chữ để đọc khi tắt tiếng (`--set typography.scale=1.15`) và tách UI khỏi `face_safe_zone`.
- **Round 4 — Tối ưu 10 giây đầu & Kiểm tra Portability:**
  - Bật `fake camera in/out` trong 10 giây đầu (`--set hook.fake_camera=true --set hook.hook_window_sec=10`) dùng đồ thị `ease-in-out`.
  - Chạy `style_trainer.py lint-skill <skill_dir>` kiểm tra cấu trúc, quy tắc `ease-in-out`, `face_safe_zone`, kiểm tra `SKILL.md` lồng nhau, và đảm bảo **0 đường dẫn cứng cá nhân** (`C:\`, `D:\`, `/home/...`) để gửi sang máy bất kỳ đều chạy được.

### Phase 5 — Đóng gói 1-Prompt Production
Khi `lint-skill` trả về `RESULT: PASS`, skill đã sẵn sàng cho sản xuất hàng loạt: mỗi video mới chỉ cần **1 câu lệnh ngắn kèm footage thô**.

---

## Bảng lệnh CLI (`scripts/style_trainer.py`)

Chạy bằng Python trong venv `~/.venvs/video-skills/bin/python` (hoặc `python3` có `Pillow` + `ffmpeg`/`ffprobe` trên `PATH`):

| Lệnh | Cú pháp | Tác dụng chính |
|---|---|---|
| **probe** | `python scripts/style_trainer.py probe <video_or_dir> --out <dir> [--fps 1.0] [--no-sheets]` | Đo `ffprobe`, cắt cảnh `scdet`, loudness `ebur128`, tạo contact sheet ảnh lưới + `probe_report.json` & `probe_summary.md`. |
| **scaffold** | `python scripts/style_trainer.py scaffold <skill_name> --out <dir> [--preset talking-head-ui-hyperframes \| --profile <json>] [--engine hyperframes\|remotion\|filmcraft] [--probe <probe_report.json>]` | Sinh trọn bộ skill mới (`SKILL.md`, `config.json`, `references/`, `templates/`, `assets/`), hoàn toàn portable. |
| **feedback** | `python scripts/style_trainer.py feedback <skill_dir> --round <N> --note "<nội dung>" [--screenshot <img_path>] [--set key=val ...]` | Copy screenshot vào `references/feedback_shots/`, ghi log vòng N vào `references/feedback-log.md`, và cập nhật thẳng `config.json` + `templates/edit.config.json`. Hỗ trợ dot-key (`motion.text_speed_scale=1.2`, `typography.scale=1.15`, `hook.fake_camera=true`). |
| **lint-skill** | `python scripts/style_trainer.py lint-skill <skill_dir> [--json]` | Kiểm tra đủ file cấu trúc, `SKILL.md` frontmatter, không có `SKILL.md` lồng nhau ngoài ý muốn, `ease-in-out`, `face_safe_zone`, và **0 đường dẫn cứng cá nhân** (`C:\`, `D:\`, `/Users/`, `/home/`). |

---

## 7 Nguyên lý viral của Talking Head (Kim chỉ nam)

1. **Khuôn mặt người:** Não người ưu tiên chú ý khuôn mặt trước mọi thứ → giữ `face_safe_zone` sạch tuyệt đối.
2. **Tin con người hơn thương hiệu (Parasocial):** Sự hiện diện đều đặn tạo cảm giác quen thân một chiều và độ tin cậy cao.
3. **Phần dựng làm video cuốn:** Chữ nhảy theo từng từ, đổi màu từ khoá, cứ vài giây có zoom/cut/UI mới để mắt không kịp chán.
4. **Sinh ra cho điện thoại (Chữ = Âm thanh):** Khung dọc 9:16, xem 1 tay, đa số lướt khi tắt tiếng → typography phải to, rõ, tương phản cao.
5. **Rẻ và dễ lặp lại:** 1 điện thoại + 1 mic + 1 ý tưởng; quay 1 buổi ra nhiều clip → skill phải đạt chuẩn **1-Prompt Production**.
6. **Phễu bán hàng tự nhiên:** Trao giá trị thực trước, chuyển đổi thành khách hàng sau mà không mang cảm giác quảng cáo gượng ép.
7. **Giá trị thật nằm ở ý tưởng:** Hiệu ứng mượt giữ người xem vài giây đầu; câu nói đáng nghe mới khiến họ lưu, chia sẻ và follow.
<!-- ===== /file: video-style-trainer/SKILL.md ===== -->

<!-- ===== file: video-style-trainer/references/lopphovlog-talking-head-blueprint.md ===== -->
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
<!-- ===== /file: video-style-trainer/references/lopphovlog-talking-head-blueprint.md ===== -->

<!-- ===== file: video-style-trainer/references/presets/talking-head-ui-hyperframes.json ===== -->
{
  "preset_id": "talking-head-ui-hyperframes",
  "name": "Talking Head UI (HyperFrames Viral Style)",
  "source_reference": "@lopphovlog/video/7706795032463936769",
  "engine": "hyperframes",
  "aspect_ratio": "9:16",
  "resolution": [1080, 1920],
  "fps": 30,
  "easing": "ease-in-out",
  "text_speed_scale": 1.2,
  "hook_window_sec": 10,
  "motion": {
    "easing": "ease-in-out",
    "cubic_bezier": [0.42, 0.0, 0.58, 1.0],
    "forbid_linear": true,
    "text_speed_scale": 1.2,
    "word_pop_ms": 260,
    "ui_enter_ms": 360,
    "ui_exit_ms": 280
  },
  "hook": {
    "hook_window_sec": 10,
    "fake_camera": true,
    "min_cuts_in_hook": 3,
    "require_kinetic_caption_from_0s": true
  },
  "fake_camera": {
    "enabled": true,
    "window_sec": 10,
    "pattern": "zoom_in_out",
    "min_scale": 1.0,
    "max_scale": 1.12,
    "easing": "ease-in-out",
    "cycle_sec": 3.5,
    "pan_px": [0, -12]
  },
  "typography": {
    "font_family": "'Inter', 'Montserrat', 'Noto Sans', sans-serif",
    "scale": 1.15,
    "base_size_px": 56,
    "keyword_size_px": 68,
    "font_weight": 800,
    "tracking_em": 0.02,
    "line_height": 1.16,
    "word_by_word": true,
    "keyword_highlight": true,
    "highlight_colors": ["#FFD43B", "#38BDF8", "#FB7185", "#4ADE80"],
    "default_color": "#FFFFFF",
    "stroke_px": 3,
    "stroke_color": "#0F172A",
    "shadow": "0 8px 24px rgba(0, 0, 0, 0.55)",
    "max_lines": 2,
    "max_words_per_chunk": 5,
    "mobile_mute_readable": true,
    "caption_zone_y_range": [0.64, 0.84]
  },
  "pacing": {
    "target_cuts_per_10s": [2.5, 4.5],
    "median_shot_sec": 2.4,
    "ui_beat_interval_sec": [2.5, 4.0],
    "max_static_sec": 2.5
  },
  "ui_elements": {
    "types": ["icon_badge", "glass_card", "orbit_nodes", "stat_pill", "callout_arrow"],
    "max_concurrent": 2,
    "avoid_face_overlap": true,
    "preferred_zones": ["lower_third_above_caption", "upper_corner_left", "upper_corner_right"],
    "glass_card_style": {
      "backdrop_blur_px": 14,
      "background": "rgba(15, 23, 42, 0.68)",
      "border": "1px solid rgba(255, 255, 255, 0.22)",
      "border_radius_px": 20
    }
  },
  "face_safe_zone": {
    "enabled": true,
    "x_range": [0.22, 0.78],
    "y_range": [0.16, 0.56],
    "padding_px": 36,
    "strict_no_overlap": true,
    "rule": "Khong dat phu de, UI card, icon hay orbit node de len vung khuon mat nguoi noi."
  },
  "transitions": {
    "allowed": ["flash_cam", "smooth_wipe", "punch_zoom"],
    "easing": "ease-in-out",
    "duration_ms": 260
  },
  "audio": {
    "voice_target_dbfs": [-5.0, -3.0],
    "bgm_below_voice_lu": [-22.0, -17.0],
    "sfx_peak_dbfs": [-12.0, -8.0],
    "sfx_on_ui_beat": true,
    "sfx_on_transition": true
  },
  "portable_assets": {
    "bundle_fonts": true,
    "bundle_sfx": true,
    "relative_assets_dir": "assets",
    "forbid_absolute_paths": true
  }
}
<!-- ===== /file: video-style-trainer/references/presets/talking-head-ui-hyperframes.json ===== -->


## 6. Học style 3 trục + bảng 4 câu hỏi (bổ sung 3.6.6, từ cách Joseph | Video Editing dạy Claude)

Nguồn: `.handoff/tiktok-haihoang/BAO_CAO_TOAN_DIEN.md` §3 bước B, `deep_086_129.md` (Figma 86–99 s), `deep_129_172.md` (131–133 s). Cho mỗi mẫu hiệu ứng, học ĐỒNG THỜI ba trục (lệnh gốc: "study three main things"):

| Trục | Câu hỏi | Ghi lại |
|---|---|---|
| 1. Vị trí theo lời ("Where it sits in the script") | hiệu ứng đặt ở đâu so với lời nói? | từ kích hoạt, độ sớm / trễ so với lời (hình đi trước lời 0–1,9 s; điểm cắt trước đầu câu 10–60 ms), loại cảnh theo nghĩa (giới thiệu kiểu mới → giữ mặt, mô tả → cho xem) |
| 2. Thiết kế ("Study the animation design") | bố cục gồm những phần tử nào? | font, màu, cỡ, tỉ lệ, vùng đặt, texture (chi tiết ở bảng 4 câu hỏi dưới đây) |
| 3. Logic chuyển động ("Study the animation logic") | dài bao lâu, cảm giác ra sao, để dựng lại được? | số khung ở 30 fps, easing, thứ tự vào / ra, có hiệu ứng thoát hay không |

Video mẫu dạy CHUYỂN ĐỘNG; bảng Figma dạy THIẾT KẾ — cần cả hai ("mẫu dạy chuyển động, Figma dạy thiết kế"). Quy trình gốc: chụp ~130 cảnh vào một bảng cảm hứng → gom vào 10 khung nhóm theo nguyên tắc → phóng to MỘT mẫu mỗi nhóm, vẽ đường chú thích đỏ và trả lời 4 câu hỏi:

| # | Câu hỏi trên bảng Figma (nguyên văn) | Trả lời bằng |
|---|---|---|
| 1 | What makes it up? | liệt kê phần tử: nền, giấy / halftone, chữ nhỏ, chữ lớn, đường, minh hoạ, ảnh |
| 2 | What are the fonts? | cặp font + vai trò (vd Inter ExtraBold chữ chính, Inter Light chữ phụ, Playfair Display Italic từ đặc biệt) |
| 3 | The colors | mã màu lấy mẫu pixel, màu nào dùng cho từ chốt / đường / hộp số |
| 4 | The sizes and patterns | tỉ lệ cỡ (vd "khoảng cách chữ phụ = 75 % chữ lớn đậm"), quy luật lặp (sandwich 1 từ lớn + từ nhỏ hai bên) |

Ba chú thích mẫu trên thẻ "common" (93.5–94.5 s): "Multiple sans light small text" · "Singular or double bold sans text" · "Distance of the light sans text is 75% of the big bold text".
Ghi chú: các tài liệu trên nêu rõ ba trục và bốn câu hỏi như trên; KHÔNG nêu thêm trục thứ tư nào, và không nêu câu trả lời mẫu cho 4 câu hỏi ngoài ví dụ thẻ "common" (cột "Trả lời bằng" ở trên là gợi ý của skill này).

Áp dụng trong skill: mỗi mẫu học xong thành MỘT mục thư viện (`kb-effect-library.md`: `still.png`, `strip.jpg`, `clip.mp4`, `notes.md` ghi số đo ba trục + dòng "dựng lại trên FilmCraft"); `lib_extract.py segments` gợi ý đoạn, `entry` ghi mục, `index` kiểm. Đầu ra gốc của họ là skill `arthur-brooks-minimal-animation` (SKILL.md + 225 mục tham chiếu).
