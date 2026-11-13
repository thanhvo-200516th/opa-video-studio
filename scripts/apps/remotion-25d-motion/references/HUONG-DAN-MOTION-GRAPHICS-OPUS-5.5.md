# Làm Motion Graphics bằng Claude Opus 5.5 — Hướng dẫn cho người mới

> Tổng hợp từ việc đọc mã nguồn 10 repo GitHub "tuần Opus 5.5" (clone và đọc ngày 06/10/2026, không chạy code của repo).
> Số sao (⭐) là số thật đo bằng `gh` hôm đó. Nhiều repo đã tăng sao so với bài đăng gốc.

---

## 1. Tóm tắt 30 giây

- **Opus 5.5 KHÔNG tạo ra video kiểu Sora hay Veo.** Nó **viết code** (HTML, Canvas, p5.js, Three.js). Code đó **vẽ từng khung hình**, rồi máy tính chụp lại và ghép thành MP4.
- **Nó rất mạnh cho:** chữ động (kinetic typography), video giới thiệu sản phẩm, video giải thích, hoạt hình 2D có phong cách (màu nước, pixel, cắt giấy…), biểu đồ động và cảnh 3D tạo bằng thuật toán.
- **Nó yếu ở:** hình ảnh giống người thật (photoreal), giữ nhân vật nhất quán qua nhiều cảnh, khớp khẩu hình (lip-sync), và "nghe" nhạc. Opus không nghe được âm thanh, nên phải phân tích nhịp bằng script.
- **Bí quyết của mọi repo tốt đều giống nhau:**
  1. Viết kịch bản theo giây trước.
  2. Mỗi khung hình là một hàm của thời gian.
  3. Bắt Claude tự render ảnh và **tự nhìn lại** để sửa.
  4. Cuối cùng mới render ra MP4.
- **Prompt ngắn thì video nhạt.** Câu prompt "làm showreel 15 giây" bị copy khoảng 108 lần trong danh sách 475 video. Video đẹp đến từ **brief dài, có cấu trúc**, hoặc từ **skill dựng sẵn**.
- **Máy bạn đã đủ đồ nghề:** Node 24, ffmpeg, Python 3.12 và Chrome, cùng các skill **HyperFrames** và **Remotion** đã cài sẵn. Bạn có thể bắt đầu ngay hôm nay.

---

## 2. Hiểu bản chất trong 1 phút: "Sách lật" (flip-book)

Bạn còn nhớ trò sách lật không? Mỗi trang vẽ một hình hơi khác nhau, lật nhanh thì thấy hình chuyển động.

Làm video bằng Opus 5.5 y hệt vậy. Chỉ khác là **không ai vẽ tay từng trang**: Claude viết ra **"luật vẽ"** cho mọi trang.

```
 BẠN                      CLAUDE OPUS 5.5                   MÁY TÍNH
 ───                      ───────────────                   ────────
 Ý tưởng / brief  ──▶  1. Viết KỊCH BẢN theo giây (STORYBOARD.md)
                       2. Viết CODE: "ở giây t, vẽ cái này"
                       3. Chụp thử vài khung → TỰ NHÌN → sửa   ◀──┐
                          (lặp đến khi ổn)                         │ vòng
                                                                   │ tự sửa
                       4. Ra lệnh render  ──────────▶  Trình duyệt ẩn (headless
                                                       Chrome) chụp khung 0, 1,
                                                       2… (30 khung = 1 giây)
                                                                 │
                                                       ffmpeg ghép ảnh + nhạc
                                                                 ▼
                                                            video.mp4 🎬
```

### Từ điển nhanh

| Thuật ngữ | Nghĩa dễ hiểu |
|---|---|
| **Frame (khung hình)** | Một trang trong sách lật |
| **fps** | Số khung mỗi giây. 24 fps thì giống phim, 30 hoặc 60 fps thì mượt kiểu mạng xã hội |
| **Render** | Cho máy "vẽ" ra từng khung thật sự |
| **Headless browser** | Trình duyệt Chrome chạy ẩn, không có cửa sổ, chuyên để chụp khung hình |
| **ffmpeg** | Phần mềm ghép hàng nghìn ảnh và file nhạc thành MP4 |
| **Storyboard** | Kịch bản hình ảnh: giây nào xuất hiện cái gì |
| **Deterministic (tất định)** | Vẽ khung số 100 lúc nào cũng ra đúng một hình. Vì vậy cấm `Math.random()` không có seed và cấm đồng hồ thật |
| **Easing** | Cách chuyển động tăng tốc hay giảm tốc. Thiếu nó thì chuyển động trông cứng như robot |
| **Contact sheet** | Một ảnh ghép nhiều khung nhỏ, để Claude và bạn "liếc" cả cảnh trong một lần |
| **Beat / BPM** | Nhịp nhạc và số nhịp mỗi phút, dùng để cắt cảnh đúng nhịp |
| **Skill (Claude Code)** | Gói hướng dẫn dựng sẵn để Claude làm đúng quy trình |

**Vì sao phải "tất định"?** Vì máy render nhiều khung **song song** và **không theo thứ tự**. Nếu khung 100 phụ thuộc khung 99 thì render song song sẽ hỏng, và video có thể giật. Tất cả repo tốt đều ép quy tắc này.

---

## 3. Đánh giá 10 repo — nên làm gì với từng cái

Điểm "Người mới" tính trên thang 1–5. "License" quyết định bạn có được copy code hay chỉ được học ý tưởng.

| # | Repo | Là gì | ⭐ thật | Người mới | License | Nên dùng để |
|---|---|---|---|---|---|---|
| 6 | **ClaudeAnimationBase** | Bộ khởi đầu làm hoạt hình kiểu vẽ tay (p5.js + p5.brush) | 844 | **4/5** | MIT ✅ | **BẮT ĐẦU Ở ĐÂY**: hoạt hình màu nước |
| 10 | **opus-video-skills** | 2 skill: `kinetic-reel` (chữ động) và `painted-animation` | 114 | **3/5** (riêng kinetic-reel 4/5) | MIT ✅ | **Bắt đầu**: chữ động có nhạc tự tổng hợp |
| 2 | awesome-opus5-5-videos | 475 video kèm prompt | 2.132 | 3/5 | MIT (prompt thuộc tác giả gốc) | Thư viện prompt mẫu, chỉ đọc mục có prompt đầy đủ |
| 7 | awesome-opus-5-5-videos | Nghiên cứu hơn 1.400 video: thể loại, công cụ, quy trình | 473 | 3/5 | CC BY 4.0 | Học cách **lên brief** (`docs/production-brief.md`) |
| 5 | lemo-opuscar | 43 phong cách phim, mỗi phong cách có một file `STYLE.md` | 1.194 | 3/5 | MIT ✅ | Kho "công thức phong cách", nhưng cần **WSL** và khá nặng |
| 8 | shipvideo | Dán URL, ra video launch dạng HTML | 293 | 4/5 (bản online) | **Không có** ⚠️ | Học **system prompt** cho video launch. Không có âm thanh |
| 1 | PDoomVideo | MV 156 giây, mọi khung hình bằng code | 1.827 | 2/5 | **Không có** ⚠️ | Case study: làm dự án dài với nhiều subagent |
| 4 | claude-opus-5-5-demo | 3 game 3D, mỗi game một prompt | 992 | 4/5 (để chơi và đọc) | **Không có** ⚠️ | Học **camera điện ảnh bằng code** (chế độ `cine`) |
| 3 | tidewater | Game câu cá WebGPU, khoảng 80 nghìn dòng | 1.116 | 2/5 | MIT | Xem "trần" năng lực: chuyên gia và Opus làm khoảng 30 giờ |
| 9 | motion-graphics-music-video-skill | Có bài hát là ra MV có nhân vật | 130 | **1/5** | MIT | Chỉ học ý tưởng. Tốn khoảng $30 tiền fal.ai, cần Ruby, thiên về macOS |

### Chi tiết ngắn từng repo

**ClaudeAnimationBase (khuyên dùng số 1)**

Tác giả của MV P(doom) rút gọn kinh nghiệm thành bộ này. Cốt lõi là file `ANIMATION_GUIDE.md` dài 461 dòng, viết **cho Claude đọc**: quy tắc, quy trình, danh sách lỗi hay gặp.

Hiệu ứng "vẽ tay" được tạo hoàn toàn bằng code, không dùng ảnh texture:
- Nét mực có độ thuôn.
- Màu nước loang ở mép.
- Giấy được tạo bằng thuật toán.
- Đường viền "rung" 12 lần mỗi giây, giống hoạt hình vẽ tay thật.

Prompt mẫu duy nhất trong README chỉ là: *"Read ANIMATION_GUIDE.md, then make a 15-second video of Clawd trying to catch a butterfly."* Phần lớn chất lượng nằm sẵn trong file hướng dẫn.

Bộ render chạy được trên Windows và có cờ `--soft-gl` cho máy không có GPU rời. Tác giả nói mức **reasoning xhigh** quyết định độ chi tiết của cảnh.

- **Lỗi đã biết:** `--encode` bỏ qua `PROJECT.audio`. Muốn có nhạc thì phải truyền `--audio=...`.

**opus-video-skills**

Hai skill này được chuyển thể từ ClaudeAnimationBase. `kinetic-reel` là skill **motion graphics đúng nghĩa**:
- Chữ là nhân vật chính.
- Chuyển cảnh liền mạch theo hình khối.
- Nhạc được **tổng hợp bằng code** và khớp nhịp với hình nhờ dùng chung một file `cues.js`.

Không tốn tiền API ngoài. Lỗi trên Windows: script `new_project.sh` cần `rsync`, mà máy bạn không có. Cách khắc phục: bảo Claude copy thư mục `template/` bằng tay rồi chạy `npm install`.

**awesome-opus5-5-videos (yihui-dev)**

- Có 475 mục nhưng **41% không có prompt** (chỉ là nội dung tweet).
- Khoảng 108 mục là cùng một prompt showreel.
- Cách dùng: lọc các mục có prompt đầy đủ, đọc 10–15 prompt **dài nhất** (của các tác giả twoclipping, techhalla, brainextends, koldo2k), rồi chép lại và thay nội dung của bạn vào.

**awesome-opus-5-5-videos (athemeroy)**

Repo này không chép prompt mà **phân tích**:
- Ai dùng công cụ gì.
- Thể loại nào phổ biến: game, quảng cáo hoặc launch, giáo dục.
- Hai file đáng đọc nhất là `docs/production-brief.md` và `docs/visual-effects-fit.md`. File thứ hai giúp chọn công cụ hợp với từng loại video.

Một số tài liệu chỉ có tiếng Trung.

**lemo-opuscar**

- Có 43 phong cách: màu nước, thủy mặc, ukiyo-e, cắt giấy đỏ, risograph, Swiss motion, anime thập niên 80, pixel RPG, phim câm 1920…
- Mỗi phong cách là một file `STYLE.md` dài 5–13 KB, gồm 11 mục: màu, chữ, chuyển động, camera, âm thanh, lỗi cần tránh…
- Có bộ tự kiểm tra rất kỹ: thời gian đọc chữ, độ lệch nhạc so với hình, độ to âm thanh.
- Mỗi phim mất 30–60 phút và **khá nhiều token**.
- Cần WSL vì script viết cho Linux.
- **Mẹo:** dù không cài, bạn vẫn có thể mở một file `STYLE.md` và dán vào prompt của mình làm "bảng phong cách".

**shipvideo**

System prompt của repo là bài học quý:
- Video dài 20–40 giây, chia 6–10 nhịp.
- Tối đa 8 chữ trên màn hình.
- Easing là `cubic-bezier(.2,.8,.2,1)`.
- Cấu trúc: nỗi đau → tên sản phẩm → cách hoạt động (3 nhịp) → bằng chứng (**không bịa số liệu**) → màn kết.
- Mọi thứ phải được animate **ra** trước cảnh sau.

Nhược điểm:
- Chạy trên nền tảng OpenComputer, không chạy local được ngay.
- Không có âm thanh.
- **Không có license**, nên chỉ học ý tưởng, không copy code.
- Claude không "nhìn" khung hình mà chỉ kiểm tra chữ và lỗi.

Tác giả ước tính khoảng 100 nghìn token và 4 phút cho mỗi video.

**PDoomVideo**

Đây là MV màu nước 2 phút 36 giây. Opus làm storyboard trước, rồi **chia 9 chương cho 9 subagent làm song song**. Mỗi subagent chỉ được sửa file của mình, và phải tự render contact sheet để kiểm tra. Repo này hay để học cách tổ chức dự án lớn, nhưng không có license và gắn chặt với một bài hát.

**claude-opus-5-5-demo**

Ba game 3D bằng Three.js. Phần đáng học nhất cho motion graphics là **chế độ camera `cine`** trong `pelican-bike/src/main.js`: danh sách cảnh quay được viết thành code. Mỗi shot có thời lượng, vị trí camera, điểm nhìn, độ mở ống kính (FOV), và chuyển mượt giữa các shot. Không có license, nên chỉ học ý tưởng. Hai game là bản tái hiện game thương mại.

**tidewater**

Đại dương, mây và ánh sáng ở mức game AAA, trong khoảng 80 nghìn dòng WebGPU. Đây **không phải** sản phẩm của một prompt: chuyên gia và Opus làm khoảng 30 giờ. Repo không có tính năng xuất video. Nên xem để biết Opus làm được đến đâu khi có người giỏi dẫn dắt.

**motion-graphics-music-video-skill**

Quy trình bài bản: phân tích beat, có cổng duyệt kế hoạch trước khi tiêu tiền, có review theo từng đợt. Nhưng nó cần Ruby, ImageMagick, tài khoản fal.ai trả phí, và một số phần chỉ chạy trên macOS.

- **Cảnh báo:** bài hát và ảnh của bạn sẽ được **gửi lên máy chủ fal.ai**.
- Tác giả ước tính khoảng $30 tiền fal cộng khoảng 3 triệu token Opus cho một MV dài 3 phút.

---

## 4. Đánh giá thẳng: Opus 5.5 làm motion graphics tốt đến đâu?

### Theo loại video

Bảng dưới là nhận định tổng hợp từ bằng chứng trong các repo, không phải đo đạc chính thức.

| Loại video | Mức phù hợp | Ghi chú |
|---|---|---|
| Chữ động, title, lower-third | ⭐⭐⭐⭐⭐ | Điểm mạnh nhất. Code vẽ chữ rất sắc nét |
| Video launch hoặc quảng cáo sản phẩm từ website | ⭐⭐⭐⭐⭐ | shipvideo và HyperFrames đều có quy trình riêng |
| Explainer (giải thích khái niệm) | ⭐⭐⭐⭐ | Có thể kèm giọng đọc TTS |
| Biểu đồ động (data viz) | ⭐⭐⭐⭐ | Nhớ dặn "chỉ dùng số liệu thật" |
| Hoạt hình 2D có phong cách (màu nước, pixel, cắt giấy) | ⭐⭐⭐⭐ | Cần bộ hướng dẫn như ClaudeAnimationBase hoặc STYLE.md |
| Cảnh 3D bằng thuật toán (biển, trời, hạt) | ⭐⭐⭐ | Làm được nhưng nặng máy, khó cho người mới |
| MV khớp nhạc | ⭐⭐⭐ | Phải có script phân tích nhịp, vì Opus không nghe được |
| Nhân vật nhất quán, lip-sync | ⭐⭐ | Các repo phải mượn thêm model tạo ảnh hoặc video (fal.ai) |
| Hình ảnh giống thật (photoreal) | ⭐ | Nên dùng model video chuyên dụng như Veo, Kling hoặc Seedance |

### Điểm mạnh thật sự

- **Có mã nguồn để sửa bằng lời.** Bạn chỉ cần nói "cảnh 3 nhanh hơn, đổi màu nhấn sang cam", không phải làm lại từ đầu như với AI tạo video.
- **Chữ luôn sắc nét và đúng chính tả**, kể cả tiếng Việt, vì chữ được vẽ bằng font thật chứ không phải AI "vẽ" chữ.
- **Tự kiểm tra bằng mắt.** Trong Claude Code, Opus tự render ảnh, đọc ảnh và sửa lỗi như chữ tràn hay hình chồng nhau.
- **Rẻ hơn thuê người** cho video ngắn, và không cần biết After Effects.

### Điểm yếu cần biết trước

Đây là các lỗi chính tác giả ClaudeAnimationBase tự quan sát được ở Opus:

1. **Nhịp độ (timing) sai là lỗi số 1**: quá nhanh, quá chậm, hoặc không đủ thời gian để đọc chữ.
2. **Lạm dụng chữ** trên màn hình.
3. **Nhiều thứ xảy ra cùng lúc**, khiến mắt không biết nhìn đâu.
4. **Biểu cảm đổi đột ngột** (mặt nhân vật "giật").

Ngoài ra:
- Opus **không nghe được nhạc**. Repo `kinetic-reel` dặn Claude phải thừa nhận "tôi không nghe được" và chỉ kiểm tra qua phổ âm thanh.
- **Render chậm.** Hiệu ứng màu nước mất khoảng 1,5–2,5 giây mỗi khung. Video 15 giây ở 24 fps có 360 khung, tức khoảng 10–15 phút nếu render một luồng, nhanh hơn nếu song song 4 luồng. Đây là ước tính.
- **Cần mức reasoning cao** (high hoặc xhigh) nên **tốn token**. Dự án lớn có thể mất hàng triệu token.
- **Nhiều repo viết cho Mac hoặc Linux.** Trên Windows hay gặp lỗi đường dẫn và lệnh `rsync`.

---

## 5. Lộ trình cho người mới — chọn 1 trong 3 con đường

> **Cập nhật 06/10/2026: đã cài trên máy bạn** (toàn máy, trong `C:\Users\Minh PC\.claude\skills\`):
>
> | Skill | Dùng khi nào |
> |---|---|
> | `motion-director` | Cửa vào bằng tiếng Việt: hỏi brief, chọn công cụ, giữ cổng duyệt |
> | `kinetic-reel` | Chữ động |
> | `painted-animation` | Hoạt hình vẽ tay, cùng bộ máy với ClaudeAnimationBase |
> | `lemo-opuscar` | 43 phong cách phim, chạy qua WSL |
> | `hyperframes` | Có sẵn từ trước |
>
> **Cách dùng nhanh nhất:** gõ `/motion-director` rồi mô tả video bạn muốn. Không cần cài thêm gì cho con đường B và C bên dưới.
>
> **Lưu ý:** nếu gõ yêu cầu chung chung như "làm video…", nhiều skill có thể cùng nhận việc. Gọi `/motion-director` hoặc nêu đúng tên skill để Claude chọn đúng.

### 🟢 Con đường A — Dễ nhất: dùng HyperFrames (đã cài sẵn trên máy bạn)

HyperFrames là framework biến HTML thành video. Nó có sẵn quy trình cho từng loại video, và chính là thứ được nhắc nhiều trong các danh sách video Opus 5.5:

| Loại video | Quy trình |
|---|---|
| Video chuyển động ngắn dưới khoảng 10 giây | `/motion-graphics` |
| Video giới thiệu website hoặc sản phẩm (giống shipvideo) | `/product-launch-video` |
| Video khớp nhạc | `/music-to-video` (giống repo 9) |
| Video giải thích | `/faceless-explainer` |

**Cách làm:**
1. Mở Claude Code trong thư mục `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude`.
2. Trong ô chọn model, chọn **Opus 5.5** và mức effort **high** hoặc **xhigh**.
3. Gõ:
   > Dùng HyperFrames làm video motion graphics 10 giây giới thiệu [thương hiệu / sản phẩm của bạn], 1920x1080, 30fps, xuất MP4.
4. Trả lời vài câu hỏi Claude đặt ra, duyệt storyboard, rồi chờ video.

### 🟡 Con đường B — Hoạt hình vẽ tay: ClaudeAnimationBase

Chạy các lệnh sau trong terminal, tại thư mục `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude`:

```bash
git clone https://github.com/JohnHeibel/ClaudeAnimationBase
cd ClaudeAnimationBase
npm install
node render.mjs --sheet=0,1,2,3,4,5 --out=out/sheet.jpg
```

Lệnh cuối là bài kiểm tra nhanh. Nếu tạo ra file `out/sheet.jpg` thì máy đã sẵn sàng.

Sau đó mở thư mục `ClaudeAnimationBase` trong Claude Code và gõ:

> Đọc ANIMATION_GUIDE.md. Viết STORYBOARD.md cho video 15 giây về [một chú mèo cố bắt con bướm] rồi DỪNG cho tôi duyệt. Sau khi tôi duyệt thì làm từng shot, tự xem contact sheet để sửa, cuối cùng render ra out/video.mp4.

**Mẹo:** dùng `studio.html` (mở bằng Chrome) để tua xem từng khung.

### 🔵 Con đường C — Chữ động (kinetic typography): skill `kinetic-reel`

Skill này đã được cài, và lỗi `rsync` đã được vá. Bạn chỉ cần mở Claude Code và gõ:

> Làm một kinetic-type reel 30 giây về [chủ đề].

> **Gợi ý thứ tự:** A trước (để thấy kết quả nhanh), rồi B hoặc C tùy bạn thích hoạt hình hay chữ động.

---

## 6. Công thức prompt "điền vào chỗ trống"

Template này gom từ các prompt thực tế cho kết quả tốt (repo 2 và 7), system prompt của shipvideo, và quy tắc của lemo-opuscar và ClaudeAnimationBase. Chép nguyên khối, thay phần trong `[ ]`:

```text
Làm một video motion graphics [15] giây về: [chủ đề / sản phẩm].

ĐỊNH DẠNG
- [1920x1080 (16:9)], [30]fps. Giao file MP4 + giữ mã nguồn để sửa sau.
- Công cụ: [HyperFrames / p5.js / HTML+Canvas]. Không dùng ảnh hay video bên ngoài.
- Mỗi khung hình là hàm của thời gian t: không Math.random() thiếu seed,
  không Date.now(), không CSS transition — để render từng frame chính xác.

PHONG CÁCH
- Bảng màu (chỉ dùng các màu này): nền [#0E0F0E], chữ [#F1EEE6], nhấn [#DDF53D].
- Font: [Inter / Be Vietnam Pro]. Cảm giác: [hiện đại, mạnh mẽ / dễ thương, vẽ tay].
- Easing: vào nhanh ra êm (cubic-bezier(.2,.8,.2,1)), có chút nảy nhẹ ở điểm nhấn.
- CẤM: glow lòe loẹt, gradient kiểu template, chữ nhấp nháy, khoảng "chết" không có gì chuyển động.

KỊCH BẢN (theo giây)
- 0–3s  HOOK: [hình ảnh/câu gây chú ý]. Không intro logo chậm.
- 3–7s  [vấn đề / bối cảnh]
- 7–12s [giải pháp — 3 nhịp ngắn]
- 12–15s KẾT: [tên + slogan / logo]. Giữ khung cuối 2 giây.
- Tối đa 8 chữ trên màn hình cùng lúc. Mỗi lúc chỉ MỘT điểm nhấn.
- Mọi phần tử phải được animate ra trước khi cảnh sau bắt đầu.
- Chỉ dùng thông tin tôi cung cấp, KHÔNG bịa số liệu.

ÂM THANH
- [Không nhạc] / [Tự tổng hợp nhạc bằng code, 120 BPM, cắt cảnh đúng nhịp]
  / [Dùng file assets/nhac.mp3 — phân tích BPM trước, đặt cú cắt vào beat].

QUY TRÌNH (bắt buộc)
1. Viết STORYBOARD.md dạng bảng: thời gian | nội dung | chuyển động | chuyển cảnh.
   Rồi DỪNG chờ tôi duyệt.
2. Sau khi duyệt: code từng cảnh.
3. Render contact sheet mỗi cảnh và TỰ XEM ảnh: sửa chữ tràn, hình chồng, cảnh trống,
   chữ hiện không đủ lâu để đọc.
4. Render bản nháp 5 giây đầu cho tôi xem.
5. Render bản cuối MP4 và báo cáo những gì đã kiểm tra.
```

**Vì sao template này hiệu quả:** mỗi dòng sửa một lỗi đã biết của AI.
- "Tối đa 8 chữ" chống lạm dụng chữ.
- "Một điểm nhấn" chống việc nhiều thứ xảy ra cùng lúc.
- "Duyệt storyboard" chặn hướng đi sai từ sớm, trước khi tốn token.
- "Tự xem ảnh" bật vòng lặp tự sửa.

---

## 7. Mười quy tắc vàng (rút ra từ cả 10 repo)

1. **Kịch bản trước, code sau.** Repo nào cũng bắt viết `STORYBOARD.md` theo giây trước.
2. **Nói rõ thông số:** thời lượng, tỉ lệ khung, độ phân giải, fps, và yêu cầu giao cả MP4 lẫn mã nguồn.
3. **Mọi khung hình là hàm của thời gian, tất định.** Đây là nền tảng để render đúng và nhanh.
4. **Bảng màu cố định và danh sách CẤM.** Hai thứ này giúp video không trông giống "AI làm".
5. **Hook trong 3 giây đầu.** Không mở bằng logo chậm.
6. **Mỗi lúc một ý, tối đa khoảng 8 chữ.** Chữ phải hiện đủ lâu để đọc, ít nhất khoảng 1,8 giây.
7. **Bắt Claude tự nhìn lại.** Yêu cầu contact sheet, strip, render thử 5 giây, rồi mới render toàn bộ.
8. **Dùng dữ liệu thật, không bịa.** Lấy màu và chữ thật từ website hay sản phẩm của bạn.
9. **Nhạc cần phân tích nhịp hoặc tổng hợp bằng code.** Đừng tin Claude "nghe" được.
10. **Effort cao và kiên nhẫn sửa nhiều vòng.** Không video đẹp nào ra trong một lần.

---

## 8. Bảng "bệnh nào, thuốc nấy" — nói gì với Claude khi video chưa ổn

| Triệu chứng | Câu nên nói với Claude |
|---|---|
| Chuyển động cứng như robot | "Thêm easing: vào nhanh ra êm, có chút overshoot ở điểm dừng." |
| Quá nhiều chữ | "Mỗi cảnh tối đa 8 chữ, tách thành nhiều nhịp, mỗi nhịp một ý." |
| Rối mắt, nhiều thứ cùng lúc | "Mỗi lúc chỉ một điểm nhấn. Liệt kê cái người xem cần thấy ở từng giây." |
| Chữ biến mất trước khi đọc kịp | "Mỗi dòng chữ giữ ít nhất 1,8 giây. Kiểm tra lại thời gian đọc." |
| Chữ cũ còn sót sang cảnh mới | "Mọi phần tử phải animate ra trước cảnh tiếp theo." |
| Trông như template, nhạt | "Đưa 3 hướng kịch bản khác nhau để tôi chọn. Thêm danh sách cấm: …" |
| Cắt cảnh lệch nhạc | "Phân tích BPM và offset của file nhạc, đặt mọi cú cắt vào beat, render một khung mỗi beat cho tôi xem." |
| Chuyển cảnh nhàm (toàn fade) | "Chuyển cảnh liền mạch: zoom xuyên qua vật thể đang được nhìn, hoặc biến hình khối này thành khối kia." |
| Render quá lâu | "Render nháp 720p trước; render song song 4 luồng; giảm hiệu ứng màu nước hoặc số hình mỗi khung." |
| Nhân vật đổi biểu cảm giật cục | "Chuyển biểu cảm mượt qua các key pose, không đổi đột ngột." |

---

## 9. Bài tập đầu tiên (khoảng 30–60 phút)

**Mục tiêu:** một video chữ động 10 giây giới thiệu bản thân hoặc thương hiệu của bạn.

1. Chọn con đường A (HyperFrames).
2. Chép template ở mục 6, điền:
   - **Thời lượng:** 10 giây.
   - **Hook:** tên bạn hiện lên với hiệu ứng mạnh.
   - **Thân bài:** 3 từ khóa mô tả bạn.
   - **Kết:** một câu slogan.
3. Duyệt storyboard. Nếu thấy dài dòng thì bảo Claude cắt bớt.
4. Xem bản nháp 5 giây và sửa **một** thứ theo bảng ở mục 8.
5. Render bản cuối.
6. Lần sau, đổi bảng màu hoặc phong cách. Có thể mượn một file `STYLE.md` của lemo-opuscar, ví dụ `styles/watercolor/STYLE.md`, dán vào prompt.

---

## 10. Lưu ý bản quyền và an toàn

- **Repo không có license** (PDoomVideo, shipvideo, claude-opus-5-5-demo): mặc định "giữ mọi quyền". Bạn **học ý tưởng thoải mái**, nhưng **không copy code** để dùng thương mại.
- **Nhân vật "Clawd"** trong ClaudeAnimationBase và opus-video-skills là linh vật của Claude Code. Nếu làm video thương mại, hãy bảo Claude thay bằng nhân vật của bạn. Bộ hướng dẫn có khuyến khích việc này.
- **Nhạc:** chỉ dùng nhạc bạn có quyền dùng, hoặc nhạc Claude tổng hợp bằng code. PDoomVideo dùng bài hát của người khác.
- **Prompt trong danh sách awesome** thuộc về tác giả gốc. License MIT chỉ áp dụng cho repo, không áp dụng cho từng prompt.
- **Gửi dữ liệu ra ngoài:** repo 9 tải bài hát và ảnh của bạn lên fal.ai. Cân nhắc nếu nội dung nhạy cảm.
- Không đưa tên hay thương hiệu người khác vào video của bạn. Lemo-opuscar có vài phim fan-made, đừng mang tên thương hiệu của chúng sang video của bạn.
