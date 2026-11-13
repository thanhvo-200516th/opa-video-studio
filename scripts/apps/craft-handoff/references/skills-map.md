# Đưa kết quả của từng skill video vào FilmCraft / EffectCraft

Nguyên tắc chung (mọi skill):

1. **Không giao một MP4 phẳng làm project.** Mỗi cắt cảnh là một clip; mỗi lần zoom/đẩy khung là
   keyframe `motion.scale` / `motion.position` trên clip đó; mỗi dòng chữ là một text clip; mỗi SFX là
   một audio clip đúng thời điểm; nhạc nền một track riêng; phụ đề là SRT (`captions.srt`).
2. **Đồ hoạ chỉ code vẽ được** (cảnh Remotion / HyperFrames / Manim, card, lower-third, logo động):
   render **từng phần tử riêng, nền trong suốt**, rồi đặt mỗi file thành một clip trên track riêng,
   đúng thời điểm nó xuất hiện. Chữ đơn giản (tiêu đề, phụ đề) thì dựng lại bằng text clip gốc
   để sửa được chữ.
3. Viết spec theo `references/timeline-spec.md`, rồi:
   `python3 tools/fc_build.py X.craft.json X.fcproj --report X.report.json --frames 3`
   và/hoặc `python3 tools/ec_build.py X.craft.json X.ecproj --report X.ec-report.json --frames 3`.
   Đọc `unsupported` trong report và báo user những gì bị đơn giản hoá.
4. FilmCraft cho việc dựng (cắt, chữ, SFX, màu, phụ đề); EffectCraft khi cần sửa chuyển động / hiệu
   ứng từng lớp. Motion graphics dựng từ đầu bằng lớp gốc của EffectCraft (shape, text animator,
   camera 3D) thì dùng `ae-script-builder` (chạy được trên EffectCraft, lưu `.ecproj`).
5. Không tự xuất MP4 từ project Craft trừ khi user yêu cầu (giống `talking-head-premiere`).

## Lệnh render nền trong suốt

| Công cụ | Lệnh (một phần tử / một cảnh) |
|---|---|
| Remotion | `npx remotion render <Comp> out.mov --image-format=png --pixel-format=yuva444p10le --codec=prores --prores-profile=4444` (một `<Composition>` cho mỗi phần tử, hoặc `--frames=a-b` theo từng `<Sequence>`) |
| HyperFrames | `npx hyperframes render -c compositions/<phan-tu>.html --format mov -o out.mov` (hoặc `--format webm` / `png-sequence`); thời điểm lấy từ `npx hyperframes timeline --json` |
| Manim | `manim -qh --transparent --format=mov scene.py Scene` |
| Canvas / p5 / frame PNG (kinetic-reel, painted-animation, lemo-opuscar) | xuất dãy PNG RGBA từng cảnh rồi gói thành ProRes 4444: `ffmpeg -framerate <fps> -i f_%05d.png -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le out.mov` |

## Theo nhóm skill

| Nhóm | Skill | Vào timeline thế nào |
|---|---|---|
| Dựng footage thật | `video-editing`, `master-video-edit`, `talking-head-premiere` (đã ra `.fcproj` sẵn), `dung-video-talking-head` (dùng `tools/adapters/th_to_craft.py`) | A-roll V1 chia clip theo cắt cảnh + keyframe zoom; B-roll V2; chữ V3+; SFX A2; nhạc A3; phụ đề SRT |
| Đồ hoạ phủ lên người nói | `talking-head-recut`, `facecammaxxing`, `embedded-captions` | Footage gốc V1 nguyên vẹn; mỗi card / hiệu ứng render alpha thành một clip trên track riêng; người tách nền (nếu skill có) là track trên cùng để chữ nằm sau đầu; phụ đề kiểu chữ động → text clip theo cụm từ, phụ đề thường → SRT |
| HyperFrames | `hyperframes`, `hyperframes-core`, `-animation`, `-keyframes`, `-audio`, `-creative`, `-registry`, `-studio`, `-cli`, `general-video`, `media-use` | Mỗi clip trong `timeline --json` thành một clip: media gốc (video/ảnh/âm thanh) đặt thẳng file nguồn; phần HTML động render alpha theo sub-composition; keyframe zoom/punch-in của `hyperframes-keyframes` thành `motion` keyframe trên clip footage; BGM/SFX/fade của `hyperframes-audio` thành audio clip + keyframe âm lượng |
| Remotion | `remotion-best-practices`, `remotion-video-creation`, `remotion-create`, `remotion-render`, `remotion-captions`, `remotion-markup`, `remotion-multimedia`, `remotion-maps`, `remotion-studio`, `remotion-interactivity`, `remotion-saas`, `remotion-upgrade`, `remotion-docs`, `remotion` (json-render), `remotion-25d-motion` | Mỗi `<Sequence>` / phần tử thành một clip; `<Video>`/`<Audio>`/`<Img>` đặt file gốc kèm `in`/`dur`; phần vẽ bằng React render ProRes 4444; captions của `remotion-captions` → SRT hoặc text clip |
| Chữ động / motion code | `kinetic-reel`, `kinetic-typography`, `motion-director`, `manim-video`, `lemo-opuscar`, `painted-animation`, `omni-flash-motion-director` | Mỗi cảnh một clip (alpha nếu phủ lên nền khác); tiêu đề tĩnh / ít chuyển động → text clip gốc với keyframe scale/opacity; cần chỉnh chuyển động từng ký tự → EffectCraft qua `ae-script-builder` |
| Sinh media bằng AI | `video-shortform`, `fal-ai-media`, `comfyui`, `heygen-video`, `heygen-avatar`, `heygen-translate`, `heygen-veo-broll-video`, `ai-avatar-production-global`, `audio-jingle` | Clip sinh ra là nguyên liệu: avatar/người nói V1, B-roll V2 kèm transition, jingle/voice/SFX là audio clip; giữ nguyên file gốc, không ghép sẵn |
| Âm thanh | `motion-sfx-audio-mastering`, `dviet-viral-text-audio-edit` | SFX chọn được đặt từng clip trên A2 đúng cue; giọng đã làm sạch thay clip A1; nhạc A3 kèm keyframe ducking; preset âm thanh FilmCraft (`presets.apply`) nếu có |
| Đã có Craft riêng | `ae-script-builder`, `ae-logo-intro-reveal`, `ae-template-customizer`, `sketch-to-mobile-ui`, `mascot-film-3d` | Theo hướng dẫn EffectCraft trong skill đó; ghép kết quả vào phim bằng spec như trên |
