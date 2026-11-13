# kb-craft-handoff — toàn văn tài liệu của nguồn `craft-handoff`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/craft-handoff/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: craft-handoff/SKILL.md ===== -->

---
name: craft-handoff
description: >-
  Dựng project gốc FilmCraft (.fcproj) và EffectCraft (.ecproj) từ kết quả của bất kỳ skill dựng video
  nào (HyperFrames, Remotion, talking-head, captions, B-roll, SFX…), để mở ra là thấy đủ timeline,
  clip, keyframe, chữ, effect, SFX, phụ đề và sửa tiếp được — không phải một MP4 phẳng. Dùng khi user
  muốn mở/sửa video trong FilmCraft hoặc EffectCraft, cần file .fcproj/.ecproj, "đưa vào FilmCraft",
  "mở bằng EffectCraft", "giao project để sửa tiếp", hoặc chuyển một bản dựng code sang timeline.
  Build native FilmCraft / EffectCraft projects (editable timeline, clips, keyframes, text, effects)
  from any video skill's output.
---

# Craft handoff — FilmCraft & EffectCraft

FilmCraft 0.13 (dựng, thay Premiere) và EffectCraft 0.17 (compositing, thay After Effects) trên máy
Linux này đều có cổng điều khiển. Skill này viết một **timeline spec** rồi để chính app dựng và lưu
project, nên file mở ra hợp lệ và mọi thứ sửa được.

## Quy trình

1. Viết spec `X.craft.json` theo [references/timeline-spec.md](references/timeline-spec.md). Mỗi skill
   video có cách chia riêng: [references/skills-map.md](references/skills-map.md). Ví dụ đầy đủ:
   `examples/demo.craft.json`.
2. FilmCraft: `python3 tools/fc_build.py X.craft.json X.fcproj --report X.report.json --frames 3`
3. EffectCraft: `python3 tools/ec_build.py X.craft.json X.ecproj --report X.ec-report.json --frames 3`
4. Đọc report: số track/clip/keyframe/effect phải khớp spec (lệch thì tool thoát mã khác 0), xem ảnh
   khung hình kiểm tra, và báo user mọi mục trong `unsupported`.
5. Giao đường dẫn project. **Không tự xuất MP4** trừ khi user yêu cầu.

`dung-video-talking-head`: `python3 tools/adapters/th_to_craft.py <VID_ROOT>/<n>/edit-r<ver> X.craft.json`
ra spec từ project đã BUILD (chữ thành text clip theo style của skill; SRT ghi cạnh spec, chỉ gắn vào
timeline khi thêm `--captions`, nếu không chữ hiện hai lần).

## Điều cần biết khi viết spec

- Easing đặt trên keyframe theo kiểu Premiere/AE: `easeIn` = chậm dần khi tới key đó, `easeOut` =
  chậm khi rời key đó. Chuyển động "đáp nhẹ" → `easeIn` ở key cuối.
- Thời gian bắt về khung hình; nhiều key trong một khung bị gộp (report cảnh báo). Clip không có `dur`
  bị cắt tới clip kế trên cùng track — SFX cần đuôi dài thì cho track riêng.
- `motion.scale` của text clip co giãn quanh `anchor` (mặc định tâm khung) — đặt `anchor` = `position`
  để chữ nảy tại chỗ.
- Font phải có trong máy, nếu không app thay bằng font khác (report ghi lại). Bộ font cinematic của
  `dung-video-talking-head` đã cài ở `~/.local/share/fonts/cinematic-fonts-pack`.
- EffectCraft không có track âm thanh hay track phụ đề: mỗi SFX là một layer audio, mỗi dòng phụ đề
  là một text layer. Effect FilmCraft chưa map được sang EffectCraft nằm trong `unsupported`.

## Lưu ý vận hành

- Mỗi lần dựng, tool mở **một FilmCraft/EffectCraft riêng** trên màn hình ảo Xephyr `:93`
  (`CRAFT_DISPLAY`) với thư mục dữ liệu/cấu hình riêng — không đụng cửa sổ user đang mở. Đặt
  `CRAFT_DISPLAY=:0` nếu muốn thấy app dựng trên màn hình thật.
- Lệnh của app: [references/filmcraft-commands.json](references/filmcraft-commands.json),
  [references/effectcraft-commands.json](references/effectcraft-commands.json) (`engine.commands`).
- Effect FilmCraft ↔ EffectCraft: [references/effect-map.md](references/effect-map.md).
- Preset của user (`~/.local/share/filmcraft/effect-presets.json`) được nhập vào bản FilmCraft riêng khi
  spec gọi tên (khớp tiền tố duy nhất cũng được); file preset gốc không bị sửa.
- Tuỳ chọn "Allow Scripts to Write Files" của EffectCraft không ảnh hưởng `ec_build` (lưu bằng lệnh
  `file.saveAs`); nó chỉ chặn script `.jsx` tự ghi file trong EffectCraft.
- Project lưu đường dẫn media tuyệt đối: đừng di chuyển media sau khi dựng.
- Test: `python3 -m pytest tests` (test `-m craft` mở app thật trên Xephyr).
- Thêm/làm mới mục "Mở và sửa tiếp trong FilmCraft / EffectCraft" ở các skill video (cần chạy lại
  sau khi skill được cập nhật bằng công cụ của nó): `python3 tools/install_pointers.py --apply`.

<!-- ===== /file: craft-handoff/SKILL.md ===== -->

<!-- ===== file: craft-handoff/references/effect-map.md ===== -->

# FilmCraft → EffectCraft mapping (`tools/ec_build.py`)

A spec names effects by their **FilmCraft id** and FilmCraft parameter names (timeline-spec.md).
`ec_build.py` turns the ids below into EffectCraft effects. Anything else lands in the report's
`unsupported` list as `where: what — why`. Nothing is dropped silently.

How a parameter is addressed: EffectCraft's `effect.list` gives every effect's parameters in order
(ids like `basicCorrection/tone/exposure`). ec_build.js walks the effect's leaf properties in that
same order and checks the display name before setting a value. At start-up the builder checks that
every id in this table still exists in the running EffectCraft, and stops with a clear error if one
is missing. Popup values are zero-based in the spec and become one-based in JS. Colours `#RRGGBB` or
`[r, g, b(, a)]` (0–1) become RGBA. Any parameter can be a keyframe list (see the interpolation table
at the end).

## Effects

| FilmCraft id | FilmCraft param | EffectCraft effect (id · AE matchName) | EffectCraft param | Notes |
|---|---|---|---|---|
| `gaussian_blur` | `blurriness` | Gaussian Blur (`ec.blur.gaussian` · `ADBE Gaussian Blur 2`) | `blurriness` | 1:1 (px). Other params → unsupported. |
| `directional_blur` | `direction`, `length` | Directional Blur (`ec.blur.directional` · `ADBE Motion Blur`) | `direction`, `length` | 1:1. |
| `lumetri` | `exposure` `contrast` `highlights` `shadows` `whites` `blacks` | Lumetri Color (`ec.color.lumetri` · `ADBE Lumetri`) | `basicCorrection/tone/<same>` | 1:1, same ranges (exposure −5…5 stops, the rest −100…100). |
| `lumetri` | `temperature`, `tint` | Lumetri Color | `basicCorrection/whiteBalance/<same>` | 1:1. |
| `lumetri` | `saturation` | Lumetri Color | `basicCorrection/saturation` | 1:1 (100 = unchanged, 0…200). |
| `lumetri` | `faded_film` `sharpen` `vibrance` `shadow_tint` `highlight_tint` | Lumetri Color | `creative/adjustments/fadedFilm` … `shadowTint` `highlightTint` | 1:1; tints are colours. |
| `lumetri` | `vignette_amount` `_midpoint` `_roundness` `_feather` | Lumetri Color | `vignette/vignetteAmount` … | 1:1. |
| `lumetri` | `basic_on` `creative_on` `vignette_on` `curves_on` `wheels_on` `hsl_on` | — | — | EffectCraft Lumetri has no section switches. `true` is ignored; `false` → unsupported (the section's values are still applied). |
| `lumetri` | `look_lut`, `look_intensity`, curves, wheels, HSL | — | — | → unsupported (FilmCraft's built-in LUT names have no EffectCraft equivalent). |
| `drop_shadow` | `color` `opacity` `direction` `distance` `softness` | Drop Shadow (`ec.perspective.dropshadow` · `ADBE Drop Shadow`) | same names | 1:1. Both apps default to 50 % / 135° / 5 px / softness 0. |
| `rounded_crop` | `left` `right` `top` `bottom` `radius` | layer **mask** (rounded-rectangle Bezier path) | — | **Approximated.** Crop values are taken as % of the source size, radius in source px. Static only: animated values keep their first key and are reported. Other params (e.g. `feather`) → unsupported. |
| `rounded_crop` | `border`, `border_color` | Stroke (`ec.generate.stroke` · `ADBE Stroke`) on that mask | `brushSize` = border, `color` | **Approximated:** the stroke is centred on the mask edge, not inside it. |
| `motion`, `opacity` (as effects) | — | — | — | → unsupported: write them as the clip's `motion` / `opacity` keys (below). |
| `grow`, `shrink`, `move` | — | — | — | → unsupported. Their timing semantics are FilmCraft-internal; express the move as `motion` keys instead. |
| `lowpass` and other audio effects | — | (EffectCraft has High-Low Pass `ec.audio.highlowpass`) | — | → unsupported until FilmCraft's parameter names are confirmed. |
| anything else | — | — | — | → unsupported. |

## Clip properties (not effects)

| Spec | EffectCraft | Notes |
|---|---|---|
| `motion.position` / `anchor` / `scale` / `rotation` | Transform › Position / Anchor Point / Scale / Rotation | Frame px, top-left origin. Anchor is in the source's own px; the default is the source centre, as in both apps. Scale `n` → `[n, n]`. |
| `opacity` | Transform › Opacity | 0–100. |
| `blend` | layer blending mode | normal / screen / multiply / add / overlay. |
| `speed` | layer Stretch = 100 × 100 / speed | `startTime = at − in × stretch / 100`. Checked with a 200 % clip against the source frame. |
| `gain_db` (constant or keys) | Audio › Audio Levels `[dB, dB]` | Keys become Audio Levels keys. |
| `audio: false` | layer audio switch off | A video file on an audio track has its video switch off. |
| `transition_in` / `transition_out` `cross_dissolve` | Opacity keys 0 → value over `frames` | **Approximated.** For `transition_in`, the clip just before it on the same track (if it ends at the cut and has source left) is extended `frames` under it, so the result is a real dissolve. Its sound is cut at the original out point with two Audio Levels keys (hold, then −192 dB). Clips that animate their own opacity skip the transition (reported). Other transition ids → unsupported. |
| text `font` + `style` | TextDocument font family + style | Resolved against `text.fonts`. A missing style takes the closest weight; a missing family falls back to Inter (bundled). Every fallback goes to the report's `fonts`. |
| text `stroke.width` | stroke width × 2, fill over stroke | AE strokes are centred on the outline. Doubling shows `width` px outside the glyph, like FilmCraft's outer stroke. |
| text `shadow` {color, opacity, blur, distance} | Drop Shadow effect | blur → softness. |
| text `size`, `color`, stroke (animated) | first key only | → unsupported. A text layer has one style unless Source Text is keyed. |
| text `position` | layer position (anchor 0,0 = first baseline at the alignment point) | Same meaning as the spec. |
| captions SRT | one text layer per cue, above every track | Wrapped at ~0.9 × frame width (0.5 em per glyph estimate), last line on the baseline at 75 % of the height. Style keys in `captions` (font, style, size, color, position, stroke…) override the default (Be Vietnam Pro Bold 64, white, 4 px black outer stroke). EffectCraft also shrinks a cue that is still too wide; the font-size change goes to warnings. |
| markers | comp markers | Comment = `name` (`: comment` appended). |
| top-level `unsupported` / `notes` (adapters) | report `unsupported` / `notes` | Passed through so the user hears about them. |

## Keyframe interpolation

The interpolation written on a key describes **that key** (Premiere / AE meaning, same as fc_build.py):

| Spec | AE key in-side | AE key out-side |
|---|---|---|
| `linear` (default) | linear | linear |
| `bezier` | Easy Ease (speed 0, influence 33.3 %) | Easy Ease |
| `easeIn` — slow arrival at this key | Easy Ease | linear |
| `easeOut` — slow departure from this key | linear | Easy Ease |
| `hold` | linear | hold (value stays until the next key) |

So `easeOut` on a clip's last key has no visible effect. EffectCraft keys sit on whole frames. Key
times are clip-relative and rounded to the nearest frame. When several keys fall inside one frame
(e.g. a 10 ms SFX fade), the first stays, the last moves to the next frame and the ones between are
dropped. That case is reported under `approximations`.

<!-- ===== /file: craft-handoff/references/effect-map.md ===== -->

<!-- ===== file: craft-handoff/references/skills-map.md ===== -->

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

<!-- ===== /file: craft-handoff/references/skills-map.md ===== -->

<!-- ===== file: craft-handoff/references/timeline-spec.md ===== -->

# Craft timeline spec (`*.craft.json`)

One JSON file describes the edit. `tools/fc_build.py` turns it into a FilmCraft project (`.fcproj`),
`tools/ec_build.py` into an EffectCraft project (`.ecproj`). Both builders drive the real app through
its control port, so the saved project is written by the app itself and opens with every track, clip,
keyframe, text and effect editable.

## Top level

```json
{
  "name": "KB03 Tu duy AI",          // sequence / comp name
  "width": 1080, "height": 1920,     // frame size (px)
  "fps": 25,                         // timeline frame rate
  "sample_rate": 48000,              // optional, default 48000
  "duration": 30.0,                  // optional; default = end of the last clip
  "tracks": [ ... ],                 // bottom → top for video, A1 → An for audio
  "captions": {"srt": "/abs/subs.srt"},          // optional
  "markers": [{"at": 3.0, "name": "Beat 2", "comment": ""}],  // optional
  "notes": ["..."],                  // optional, free text for whoever opens the project
  "unsupported": [{"what": "...", "why": "...", "where": "..."}]   // optional: what the source edit
                                     // had that the spec could not carry; builders copy it to the report
}
```

All paths are absolute. All times are **seconds**. `at` is where the clip starts on the timeline;
key times inside a clip are **relative to the clip start**.

## Tracks

```json
{"type": "video", "name": "V1 A-roll", "clips": [ ... ]}
{"type": "text",  "name": "V3 Title",  "clips": [ ... ]}   // FilmCraft: graphic clips; EffectCraft: text layers
{"type": "audio", "name": "A2 SFX",    "clips": [ ... ]}
```

Video and text tracks share one stack in list order: the first visual track is V1 (bottom), the next
sits above it. Audio tracks are A1, A2… in list order. A video clip that carries sound puts it on the
first audio track unless the clip says `"audio_track": "A3"` or `"audio": false`.

## Clips

Media clip (video, image or audio track):

```json
{
  "src": "/abs/a-roll.mp4",
  "at": 0.0,            // timeline start
  "in": 12.4,           // source in point, default 0
  "dur": 4.0,           // default: rest of the source (stills: 5 s)
  "name": "Hook",       // optional clip name
  "speed": 100,         // optional, percent
  "gain_db": -6,        // optional, audio
  "audio": true,        // optional, false = video only
  "motion": {"scale": 100, "position": [540, 960], "rotation": 0, "anchor": [540, 960]},
  "opacity": 100,
  "blend": "normal",    // optional: normal|screen|multiply|add|overlay
  "effects": [{"effect": "gaussian_blur", "params": {"blurriness": 0}}],
  "preset": "[DViet] Flash Out",                 // optional, FilmCraft preset name
  "transition_in":  {"effect": "cross_dissolve", "frames": 8},
  "transition_out": {"effect": "cross_dissolve", "frames": 8}
}
```

Text clip (text track):

```json
{
  "text": "Tư duy AI", "at": 1.0, "dur": 2.5,
  "font": "Be Vietnam Pro", "style": "ExtraBold", "size": 120,
  "color": "#FFFFFF", "align": "center",               // left|center|right
  "position": [540, 700],                              // alignment point of the first baseline
  "stroke": {"color": "#000000", "width": 6},          // optional
  "shadow": {"color": "#000000", "opacity": 60, "blur": 12, "distance": 0},   // optional
  "tracking": 0, "leading": 0,
  "motion": {...}, "opacity": ..., "effects": [...], "transition_in": {...}
}
```

## Animated values

Any number, `[x, y]` or colour above can be a keyframe list instead of a constant:

```json
"scale": [[0, 100], [0.4, 112, "bezier"], [3.6, 112], [4.0, 100]]
"position": [[0, [540, 1100], "easeOut"], [0.5, [540, 960], "easeIn"]]
"opacity": [[0, 0], [0.25, 100], [2.25, 100], [2.5, 0]]
```

Each key is `[time, value, interpolation?]`; interpolation is `linear` (default), `bezier`,
`easeIn`, `easeOut`, `hold`, with the Premiere / After Effects meaning on the key it sits on:
`easeIn` slows the arrival **into** that key, `easeOut` slows the departure **from** it, `bezier`
eases both sides, `hold` keeps the value until the next key. To make a move settle softly, put
`easeIn` on the key where it lands (an `easeOut` on a clip's last key does nothing).
Units follow the apps: scale in %, rotation in degrees, opacity 0–100, position/anchor in frame
pixels with (0, 0) top-left. A text clip's `motion.scale` scales around its `anchor`, which defaults
to the frame centre — set `anchor` to the text `position` for a pop in place.

## Timing rules the builders apply

- Times snap to whole frames (half-up): 4.5 s at 25 fps lands on 4.52 s.
- Clips on one track must not overlap. A clip without `dur` that would run into the next clip on its
  track is trimmed to that clip's start and the report warns. Give overlapping sounds (an SFX tail
  under the next cue) their own track instead.
- A video clip's sound cannot land on an audio track that already has clips at that time — the build
  stops with an error; give it `"audio_track"` or `"audio": false`.
- Not expressible yet: caption style / language (FilmCraft imports the SRT with its default style),
  marker colours. Fonts the app does not have are substituted and reported as warnings.

## Effects

`effect` is the FilmCraft effect id (`effects.list` in FilmCraft, e.g. `gaussian_blur`, `lumetri`,
`drop_shadow`, `rounded_crop`, `grow`, `shrink`, `lowpass`). `params` uses that effect's parameter
names; any param can be animated as above. `ec_build.py` maps the ids it knows to EffectCraft effects
(see `references/effect-map.md`) and reports the ones it cannot map instead of dropping them silently.

## What does not belong in a spec

- A finished render of the whole video as one clip. The point is an editable timeline: cuts, zooms,
  text, SFX and overlays each stay their own clip.
- Graphics that only code can draw (Remotion / HyperFrames / Manim scenes) as one flattened layer
  over the footage. Render each graphic element with alpha (ProRes 4444 `.mov` or PNG sequence) and
  give it its own clip and track, timed where it appears.

<!-- ===== /file: craft-handoff/references/timeline-spec.md ===== -->
