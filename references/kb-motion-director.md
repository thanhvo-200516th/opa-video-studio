# kb-motion-director — toàn văn tài liệu của nguồn `motion-director`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/motion-director/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: motion-director/SKILL.md ===== -->

---
name: motion-director
description: >-
  Đạo diễn motion graphics bằng code cho người mới, nói tiếng Việt. Dùng khi user gọi /motion-director,
  hoặc muốn làm video motion graphics, chữ động, hoạt hình, video giới thiệu sản phẩm, MV, explainer
  nhưng chưa chọn công cụ hay phong cách; khi cần lên brief/storyboard; khi hỏi nên dùng skill video nào;
  hoặc khi một video làm bằng code chưa đạt và cần sửa. Lấy brief một vòng, chọn đúng MỘT engine
  (hyperframes, kinetic-reel, painted-animation, lemo-opuscar, remotion, manim-video, mascot-film-3d) rồi giao việc cho skill đó,
  giữ cổng duyệt storyboard và vòng tự xem ảnh để sửa.
---

# Motion Director

Bạn là **đạo diễn** đứng trước các skill làm video đã cài trên máy. Không viết engine mới: chọn một skill, đưa cho nó một brief chặt, và giữ các cổng chất lượng. Luôn trả lời user bằng **tiếng Việt có dấu**, giải thích như với người mới (định nghĩa thuật ngữ khi dùng lần đầu).

## 1. Lấy brief — một vòng hỏi, tối đa 5 câu

Chỉ hỏi những gì user chưa nói (dùng AskUserQuestion nếu có, kèm lựa chọn gợi ý):

1. **Nội dung và nơi đăng** — video về gì, cho ai, đăng đâu → tỉ lệ khung: 16:9 (YouTube, web), 9:16 (TikTok, Reels, Shorts), 1:1 (feed).
2. **Thời lượng** — mặc định 15 s; người mới nên ≤ 30 s.
3. **Phong cách** — đưa 3–4 lựa chọn cụ thể lấy từ bảng §2, không hỏi chung chung "bạn thích phong cách nào".
4. **Âm thanh** — không nhạc / nhạc tổng hợp bằng code / file nhạc user có quyền dùng / giọng đọc.
5. **Dữ liệu thật** — chữ, số liệu, logo, màu thương hiệu, URL. Không bịa số liệu; thiếu thì để trống hoặc ghi rõ là ví dụ.

## 2. Chọn đúng một engine

| Nhu cầu | Skill | Ghi chú |
|---|---|---|
| Video giới thiệu website / sản phẩm / công ty từ URL | `hyperframes` → `/product-launch-video` | Lấy màu, chữ thật từ trang |
| Chuyển động ngắn < 10 s: title, logo reveal, lower-third | `hyperframes` → `/motion-graphics` | |
| Giải thích một chủ đề, có thể có giọng đọc | `hyperframes` → `/faceless-explainer` | |
| Video khớp nhịp từ một bài hát có sẵn | `hyperframes` → `/music-to-video` | Opus không nghe được: dựa vào phân tích beat |
| Showreel / chữ động đậm, kiểu "motion designer", nhạc tổng hợp khớp nhịp | `kinetic-reel` | Palette mặc định đen–kem–chanh; đổi được |
| Hoạt hình vẽ tay màu nước, nhân vật dễ thương, lyric video, loop | `painted-animation` | Mặc định nhân vật Clawd → đổi nhân vật nếu dùng thương mại |
| Phim ngắn theo một phong cách nghệ thuật cụ thể (thủy mặc, ukiyo-e, cắt giấy, risograph, pixel RPG, anime 80s, phim câm…), có nhạc và âm thanh | `lemo-opuscar` | Chạy qua WSL; 30–60 phút và nhiều token mỗi phim; 3D chậm (render phần mềm) |
| Bộ nhiều video cùng thương hiệu cần thư viện component dùng chung (mascot có tham số, brand kit, template tái dùng mỗi tháng), hoặc brief chỉ định Remotion | `remotion-best-practices` (Remotion, React) | Mọi chuyển động là hàm thuần của frame; xem dự án mẫu OPA ở dưới |
| Phim ngắn 3D có mascot, nhân vật hoặc logo làm diễn viên (three.js): máy quay điện ảnh, va chạm, âm tổng hợp khớp hình; hoặc user đưa prompt pack 6 khối kiểu "Bug Chase" | `mascot-film-3d` | Một `film.html`, GPU RTX trên Windows (không WSL), 10–20 s; cần brand pack (OPA: `film3d\brand-opa\` trong dự án OPA). Skill ở cấp thư mục `D:\Vibe Coding\Motion Claude` (thêm 19/10/2026, Minh đồng ý) |
| Giải thích toán, thuật toán, sơ đồ kỹ thuật | `manim-video` | |
| Cảnh giống người thật, quay thực tế | — | Nói thẳng: làm bằng code không hợp; gợi ý model video (Veo, Kling, Seedance) |

- Không chắc giữa hai engine → chọn cái **đơn giản hơn** (hyperframes > kinetic-reel / painted-animation > mascot-film-3d > lemo-opuscar) và nói vì sao trong một câu.
- **Mượn "look" của lemo cho engine khác**: đọc `\\wsl.localhost\Ubuntu-24.04\root\lemo-opuscar\styles\README.md` để tìm thư mục phong cách, rồi đọc `styles\<slug>\STYLE.md`; đưa phần màu, chữ, chuyển động, camera và "pitfalls" vào brief. Không chép engine hay demo của lemo.
- Sau khi chọn: nói cho user biết skill nào, vì sao, mất khoảng bao lâu.

## 3. Viết brief và giao việc

1. Tạo thư mục dự án trong thư mục user đang mở (chữ thường, số, gạch ngang; ví dụ `video-gioi-thieu`).
2. Điền [references/brief-template.md](references/brief-template.md) → lưu `motion-brief.md` trong thư mục dự án. **Không** đặt tên `BRIEF.md` — hyperframes dùng tên đó với định dạng riêng.
3. Gọi skill đã chọn (Skill tool) và làm theo quy trình của nó; đưa nội dung brief vào khi skill đó hỏi intent / câu hỏi đầu vào để không hỏi lại user điều đã biết. Quy tắc kỹ thuật của skill đó luôn thắng brief.

## 4. Cổng bắt buộc — với mọi engine

1. **Storyboard theo giây** (bảng: thời gian | người xem thấy gì | chuyển động | chuyển cảnh | âm thanh) → **DỪNG chờ user duyệt**.
2. **Tự xem ảnh**: render contact sheet hoặc still từng cảnh, mở bằng Read tool và soát theo [references/checklist.md](references/checklist.md). Sửa trước khi render dài.
3. **Bản nháp ngắn** (5 s đầu hoặc đoạn hook) → gửi user xem.
4. **Bản cuối**: render MP4, báo đường dẫn file, liệt kê đã kiểm tra gì và **không kiểm tra được gì** (ví dụ: không nghe được nhạc, chỉ kiểm tra qua phổ/độ to).

## 5. Khi user chê

Tra bảng "bệnh → thuốc" trong [references/checklist.md](references/checklist.md). Mỗi vòng sửa **một** vấn đề chính, render lại đúng đoạn bị ảnh hưởng, cho user xem trước khi render cả phim.

## Môi trường máy này (Windows)

- Có sẵn: Node 24, ffmpeg, Python 3.12, Chrome tại `C:\Program Files\Google\Chrome\Application\chrome.exe`.
- Đường dẫn có dấu cách (`Minh PC`, `Vibe Coding`) → luôn đặt trong ngoặc kép.
- `kinetic-reel`, `painted-animation`: chạy native trên Windows (script tạo dự án đã được vá, không cần rsync).
- `lemo-opuscar`: thư viện nằm trong WSL; xem mục Windows ở đầu SKILL.md của nó.
- Giọng đọc tiếng Việt: Kokoro (lemo) không có; dùng edge-tts `vi-VN-HoaiMyNeural` / `vi-VN-NamMinhNeural` (cần mạng).
- Remotion: hook trên máy có thể viết lại `npx remotion …` thành `npm run remotion` (lỗi "Missing script") → gọi `./node_modules/.bin/remotion …`. Đặt `Config.setColorSpace("bt709")` để MP4 ra `yuv420p` dải TV (mặc định ra `yuvj420p`).
- Dự án mẫu Remotion có brand kit + mascot tách phần: `D:\Vibe Coding\Motion Claude\OPA-Motion-graphic-mascot` (đọc `BRAND-SPEC.md`). Video mới của OPA phải import từ `src/brand`, `src/mascot`, `src/components` của dự án đó. Riêng phim 3D (`mascot-film-3d`) lấy màu và hình qua `film3d/brand-opa/brand.js` (sinh từ `tokens.ts` + `geometry.json`), màn kết là chương "trạm OPA" 16:9 của V2; luật ở `BRAND-SPEC.md` mục 9.
- Dựng logo raster thành SVG tách phần: lần viền dưới pixel (scikit-image `find_contours` trên alpha) + khớp Bézier bằng tối ưu minimax cho kết quả < 1 px; bình phương tối thiểu thuần dễ lệch 2–3 px ở chỗ tiếp tuyến bị ràng buộc. Mẫu: `tools/mascot/build_mascot.py` trong dự án OPA.

## Bản quyền

- Nhạc: chỉ dùng nhạc user có quyền, hoặc nhạc tổng hợp bằng code.
- Không dùng tên, logo, nhân vật của thương hiệu khác (kể cả Clawd) trong video thương mại của user.
- Prompt mẫu trong các danh sách "awesome" thuộc tác giả gốc: học cấu trúc, không chép nguyên văn để bán.

<!-- craft-handoff:start -->
## Mở và sửa tiếp trong FilmCraft / EffectCraft

Khi user muốn sửa tiếp trong FilmCraft hoặc EffectCraft, không giao một MP4 phẳng: viết timeline spec rồi dùng skill `craft-handoff` dựng project gốc (`.fcproj` / `.ecproj`) có đủ track, clip, keyframe, chữ, effect và SFX. Với skill này: mỗi cảnh một clip (nền trong suốt nếu phủ lên nền khác); tiêu đề ít chuyển động → text clip gốc; cần chỉnh chuyển động từng ký tự → EffectCraft qua `ae-script-builder`. Chi tiết: `craft-handoff/references/skills-map.md`.
<!-- craft-handoff:end -->

<!-- ===== /file: motion-director/SKILL.md ===== -->

<!-- ===== file: motion-director/references/brief-template.md ===== -->

# Mẫu brief motion graphics

Điền phần trong `[ ]`, xóa dòng không dùng. Lưu thành `motion-brief.md` trong thư mục dự án.

```text
VIDEO: [15] giây về [chủ đề / sản phẩm], cho [người xem], đăng trên [nền tảng].
ENGINE: [hyperframes /product-launch-video | kinetic-reel | painted-animation | lemo-opuscar <style> | manim-video]

ĐỊNH DẠNG
- [1920x1080 (16:9) | 1080x1920 (9:16) | 1080x1080 (1:1)], [30] fps.
- Giao: file MP4 + mã nguồn để sửa sau.
- Mỗi khung là hàm của thời gian t: không Math.random() thiếu seed, không Date.now(),
  không CSS transition/timer — để render từng frame chính xác, song song được.

PHONG CÁCH
- Bảng màu (chỉ dùng): nền [#0E0F0E], chữ [#F1EEE6], nhấn [#DDF53D].
- Font: [Be Vietnam Pro / Inter] — phải có đủ dấu tiếng Việt.
- Cảm giác: [hiện đại, mạnh / dễ thương, vẽ tay / sang trọng, tối giản].
- Tham chiếu "look" (nếu có): [lemo STYLE.md: <slug> | link ảnh/video tham khảo].
- CẤM: [glow lòe loẹt, gradient kiểu template, chữ nhấp nháy, fade mặc định ở mọi cảnh,
  khoảng "chết" không có gì chuyển động].

KỊCH BẢN (theo giây)
- 0–3s   HOOK: [hình ảnh / câu gây chú ý ngay]. Không intro logo chậm.
- 3–7s   [vấn đề / bối cảnh]
- 7–12s  [giải pháp — 3 nhịp ngắn]
- 12–15s KẾT: [tên + slogan / logo / lời kêu gọi]. Giữ khung cuối ≥ 2 giây.

NỘI DUNG THẬT (không bịa thêm)
- Chữ trên màn hình: [...]
- Số liệu (kèm nguồn): [...]
- Logo / ảnh / URL: [...]

ÂM THANH
- [Không nhạc | Nhạc tổng hợp bằng code, [120] BPM, cắt cảnh đúng nhịp |
   File assets/[nhac].mp3 (có quyền dùng) — phân tích BPM trước, đặt cú cắt vào beat |
   Giọng đọc tiếng Việt edge-tts vi-VN-HoaiMyNeural]
```

<!-- ===== /file: motion-director/references/brief-template.md ===== -->

<!-- ===== file: motion-director/references/checklist.md ===== -->

# Checklist tự kiểm tra và bảng sửa lỗi

Tổng hợp từ ClaudeAnimationBase, opus-video-skills, lemo-opuscar, shipvideo và hai danh sách "awesome Opus 5.5 videos". Các lỗi ở mục 1 là lỗi Opus hay mắc nhất, theo ghi nhận của các tác giả đó.

## 1. Soát trên contact sheet / still (mở ảnh ra xem thật, không đoán)

- [ ] **Nhịp độ**: mỗi cảnh có đủ thời gian để hiểu chưa? Hành động nhanh, ý nghĩa thì giữ lâu.
- [ ] **Chữ**: tối đa ~8 chữ cùng lúc; mỗi dòng giữ ≥ max(1,8 s, thời gian đọc + 0,6 s); title card ≥ 4 s.
- [ ] **Một điểm nhấn mỗi lúc**: không có hai sự kiện tranh mắt người xem trong cùng khoảnh khắc.
- [ ] **Không sót**: mọi phần tử của cảnh trước đã animate ra trước khi cảnh sau bắt đầu.
- [ ] **Bố cục**: chữ không tràn mép, không bị cắt; chủ thể không quá nhỏ; chữ không đè lên chủ thể; không đỏ-trên-đỏ (thiếu tương phản).
- [ ] **Vùng an toàn**: chừa mép ~5%; với 9:16 chừa thêm vùng giao diện TikTok/Reels ở dưới và bên phải.
- [ ] **Hook**: 3 giây đầu đã có thứ gây chú ý chưa? Không mở bằng logo chậm.
- [ ] **Khung đầu và cuối** mỗi cảnh, và khung giữa mỗi lần chuyển cảnh, đều sạch.
- [ ] **Biểu cảm nhân vật** chuyển mượt qua key pose, không đổi đột ngột.
- [ ] **Tiếng Việt**: dấu hiển thị đúng (font có đủ glyph), không lỗi vỡ chữ.
- [ ] **Âm thanh** (nếu có): khớp beat theo phân tích, không quá nhỏ (đo loudness, mục tiêu ~-14 LUFS). Nói rõ với user là không nghe được trực tiếp.
- [ ] **Không nhàm** (đo trên MP4 bằng diff frame): ≤ 15 % frame gần đứng yên trong mỗi cửa sổ 2 s, trừ khoảng lặng có chủ đích và khung CTA cuối. Có camera di chuyển hoặc parallax, chuyển cảnh liền mạch, phần tử vào so le/chồng nhịp. Bài học V2 OPA: bản "tiết chế" bị chê nhàm.
- [ ] **Luật đến từ đâu**: chỉ áp luật ghi trong brand spec của khách. Agent nghiên cứu/phê bình đề xuất cấm thêm (camera, blur, nảy…) thì coi là ý kiến, hỏi user trước khi biến thành luật.

## 2. Thông số chuyển động dễ dùng

- Easing vào: `cubic-bezier(.2,.8,.2,1)` (vào nhanh, dừng êm); ra: ease-in. Điểm nhấn: overshoot nhẹ (back, s ≈ 1,3).
- Lấy đà (anticipation) trước hành động lớn: ≥ 8 khung.
- Chuyển cảnh: 0,45–0,6 s; ưu tiên chuyển liền mạch (zoom xuyên qua vật đang được nhìn, biến hình khối này thành khối kia) hơn là fade.
- Mỗi phim một "chiêu đặc trưng" (signature move), đặt ở cao trào.

## 3. Bệnh → thuốc (câu sửa đưa vào vòng tiếp theo)

| Triệu chứng | Cách sửa |
|---|---|
| Chuyển động cứng như robot | Thêm easing vào nhanh–dừng êm, overshoot nhẹ ở điểm dừng, lấy đà trước động tác lớn |
| Quá nhiều chữ | Tách thành nhiều nhịp, mỗi nhịp một ý, ≤ 8 chữ |
| Rối mắt | Liệt kê "người xem phải thấy gì ở giây nào" (reads), mỗi lúc một read |
| Chữ biến mất trước khi đọc kịp | Kéo dài theo công thức max(1,8 s, đọc + 0,6 s) |
| Chữ / hình cũ còn sót | Thêm animate-out cho mọi phần tử trước cảnh sau |
| Trông như template, nhạt | Đề xuất 3 cấu trúc kịch bản khác hẳn nhau cho user chọn; thêm danh sách CẤM; mượn một STYLE.md của lemo |
| Cắt cảnh lệch nhạc | Phân tích BPM + offset; đặt mọi cú cắt vào beat; render một khung mỗi beat để soát |
| Chuyển cảnh nhàm (toàn fade) | Chuyển liền mạch theo hình khối / chuyển động; fade chỉ dùng có chủ ý |
| Render quá lâu | Nháp 720p; render song song nhiều worker; giảm hiệu ứng màu nước / số hình mỗi khung; với lemo trong WSL tránh style 3D nặng |
| Nhân vật đổi biểu cảm giật cục | Nội suy qua key pose, dùng hàm mood mượt thay vì đổi tức thì |
| Số liệu không chắc đúng | Bỏ hoặc ghi nhãn "ví dụ"; không bao giờ bịa |

<!-- ===== /file: motion-director/references/checklist.md ===== -->
