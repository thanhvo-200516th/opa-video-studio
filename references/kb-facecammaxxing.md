# kb-facecammaxxing — toàn văn tài liệu của nguồn `facecammaxxing`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/facecammaxxing/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: facecammaxxing/SKILL.md ===== -->

---
name: facecammaxxing
description: Facecam maxxing - add pro motion-graphics effects to a real talking-head clip (a facecam / selfie / phone video of the user talking), rendered with Remotion + GSAP + Three.js (and headless Blender for modelled 3D props) over a clean cut-out of the person, directed with an award-level reel director's workflow (brief, one idea per sentence, a beat plan where every effect says what it makes the viewer believe, hardest beat first, measured self-review). It is a library of 22 effects, all equal, grouped by the job they do: proof and numbers - over-the-shoulder (camera pushes over each shoulder to Before / After proof cards behind the head, with motion blur), kallaway-split (the clip drops into a card on grid paper and the creator's numbers rise out of its top edge as a skyline that peaks behind their head), glass-graph, glass-widgets, tier-list (S-D tier list builds under the chin); type and captions - text-behind (a huge word rises from behind the head), backdrop-word, kinetic-caption (word-by-word captions in two type faces, editorial or podcast style, top words tucked behind the head); camera, light and look - lean-in (punch-in with motion blur and depth of field), slow-push, spotlight, color-grade (flat LOG look wiped into a cinematic grade with Before / After), grade, locked-on; 3D and depth - prop-3d (a Blender-modelled trophy, a clock whose hands sweep the hours, a coin, a phone showing the real screen, a check, an X, or any GLB, lit like the room), carousel-spin and orbit of reels; people, openers and framing - freeze-frame (shot freezes, room greys, white sticker outline + name tag), name-tag (lower third), silhouette-intro, window-cards (retro desktop windows of your reels that a cursor clicks), bottom-fade. Effects track the face, sit behind or in front of the person, never cover the face, keep out of the Reels UI zones and follow measured motion rules. Use when the user says facecam maxxing / facecammaxxing, gives a talking-head clip and asks for an effect, names one of the effects, asks for "text behind my head", "cards behind me", kinetic / word-by-word captions, a lower-third name tag, retro window cards, a silhouette intro, a Kallaway split / split-screen chart, a freeze frame, a tier list, a before/after grade, a 3D object / prop / trophy / Blender model next to them, or wants the Claude-edit style effects on their own footage.
---

# Facecam maxxing

Work as an award-winning motion designer, UI designer and Three.js developer directing short vertical film: the person on camera
is the hero, every effect performs the sentence it lands on, every frame is worth a screenshot, and you judge your own stills and
render instead of self-certifying. **Read `docs/director.md` (the workflow, the judgment and which tool does which job, distilled
from pro-animation-director) and `docs/motion-rules.md` (the measured numbers) before planning, changing or adding an effect.**

The stack, one job each:
- **Remotion** - frames and layers: one stage stacks **room → behind → sticker → you → front → screen** under one camera; deeper
  layers zoom less (real parallax).
- **GSAP** - choreography: timelines built paused and seeked to the frame (seek-safe), eases for every move.
- **Three.js** - depth, light and material (`remotion/src/lib/three.tsx`): rings of cards, slabs, clearcoat, reflections, GLB props.
- **Blender**, headless - only when a beat needs a modelled object: a Python script (`scripts/blender/`) → GLB → `prop-3d`.

Under it, a Python pass (`scripts/track.py`) splits the clip into layers: `source.mp4` (8-bit H.264 at 1080 wide), `person.webm`
(the person cut out with alpha, RobustVideoMatting; MediaPipe fallback), a smoothed face path and head top (YuNet), and on a
still camera a clean plate + `room.mp4` with the person removed.

All paths below are relative to this skill's folder. Everything runs through `scripts/fcm.py` with the skill's own venv:
`PY=<skill>/.venv/bin/python`, `FCM="$PY <skill>/scripts/fcm.py"`.

## The workflow (in this order, never skip)

### 0. First run
`$FCM setup` (or `bash scripts/setup.sh`) prints READY. It makes the venv (uv, Python 3.11), downloads the three models and
installs the Remotion project (needs Node 22+; nvm's v22 is found automatically). The first render downloads Remotion's headless
Chrome (~170 MB) once; offline, point it at a Chrome of your own with `FCM_BROWSER=/path/to/chrome`. Blender is optional: only
new props need it (see step 5).

### 1. Brief
Fill the BRIEF at the end of `docs/director.md` with the user: the one true thing the clip says, audience and language, the source
of every number, which side the room's key light is on, and (for a whole reel) the KEYWORD. Ask for the real numbers; a blank
line means stop and ask, not invent.

### 2. Track the clip (once per clip)
`$FCM track <video> [<job-dir>]` - default job dir `./<video-name>_facecam`. ~40 s for a 7 s 4K clip. It reports whether the
camera is still (parallax and the clean room need a still camera; on a moving camera those moves fall back to flat zooms).
If the clip is on an SD card or external drive, put the job dir in the project, not on the card.
Look at one frame of `person.webm` over a colour (see "Checking the cut-out") before going on: every behind-you effect is only as
good as this matte.

### 3. Listen: word times
`$FCM words <job>` (whisper word times into `words.json`). Read the transcript as a script (hook → proof → mechanism → payoff →
CTA) and mark the sentences that carry a claim: those are the beats; the rest stays clean footage. An effect lands ~2 frames
before its word. With no timing given, ask once, or place it where the clip is calm. Never let an effect run into the last ~0.8 s
if the person reaches for the camera there.

### 4. Beat plan
For each beat, find the idea that belongs only to that sentence (never the first association; cover the creator's name and ask if
anyone could run the same effect on the same line). Proof gets proof (real numbers, real UI), a claim gets a **literal prop**
(hours → `clock`, money → `coin`, the win → `trophy`, rejection → `x`, "the app" → `phone` with the real screenshot), opinions get
type, lists get a tier list, a reveal gets a camera move. One effect per sentence, one accent event each. Write it down next to
the job, every entry with `buys` (what the viewer believes after it) and `on` (its word) - effects ignore both, the review reads them:
```json
{"effects": [
  {"fx": "over-the-shoulder", "start": 0.3, "end": 3.1, "before": "1,204 views", "after": "412K views",
   "buys": "this format took them from 1K to 412K", "on": "views"},
  {"fx": "prop-3d", "start": 3.4, "end": 5.6, "model": "clock", "hours": 6, "light": "left",
   "buys": "it saves six hours a week", "on": "hours"},
  {"fx": "text-behind", "start": 5.8, "end": 8.8, "text": "VIRAL", "buys": "the result is the point", "on": "viral"}
]}
```

### 5. Pick the lane, model what is missing
Each beat's lane is the lightest that can carry its idea: HTML/CSS + GSAP for type, cards and UI; Three.js for depth, light and
material; Blender only for a modelled object. The built-in props (`trophy`, `clock`, `coin`, `phone`, `check`, `x`) ship as GLBs
in `props/` and need no Blender. For a new one, or a new colour:
```bash
$FCM blender <job> coin --color '#D97757' --name coin      # a built-in prop, recoloured  -> <job>/models/coin.glb
cp scripts/blender/template.py my_mic.py                   # a prop of your own, built with scripts/blender/kit.py
$FCM blender <job> my_mic.py --name mic                    # -> <job>/models/mic.glb, used as "model": "mic"
```
It finds Blender 3.6+ (`$BLENDER`, PATH, the macOS app, snap, flatpak) or a Python 3.11 with `pip install bpy` (`$BLENDER_PY`).
Prop conventions (front faces -Y, named moving parts, PBR only, low-poly) are in `docs/director.md`.

### 6. Hardest beat first, then check stills
Build the hero beat alone first. `$FCM check <job> plan.json` (or `--at 1.2,3.4`) renders stills at 30 % and 60 % of every effect
and a contact sheet `<job>/check/<plan>/sheet.jpg`. **Look at the sheet yourself.** Fix what covers the face, clips at an edge,
lands in a platform zone, reads too small, or (for a prop) is lit from the wrong side - then check again, then add the other beats.

### 7. Render, review, deliver
`$FCM render <job> plan.json [--out final.mp4] [--draft] [--range 0.3-3.3]`. ~25 s for a 7 s clip at 1080p. The original audio is
kept. `--draft` is half size. Watch it at real speed and answer the self-review in `docs/director.md` in writing; fix in the order
untrue → face / platform UI → idea → connections → hierarchy → timing → finish. Deliver the file path, the cover frame and the
short NOTE (each effect and what it buys, what is real vs illustrative, what you would still fix), and remind the user in one line
to watch it before posting.

Some effects are written against a set length (over-the-shoulder 2.8 s, kallaway-split 4 s, window-cards 1.8 s; freeze-frame,
tier-list, text-behind, color-grade and glass-graph 3 s). Give them that window; a longer window slows every move to match (the user
can ask "make it 4 seconds"). `$FCM list` prints every effect and its options (read from the code, so it is always current).

## The effect library
22 effects, all equal: one library, grouped here only by the job they do in a beat (proof gets proof, a claim gets a prop, a reveal
gets a camera move). Every effect has a ready plan in `examples/<fx>.json` and a demo render of it in `demo/<fx>.mp4`; two
combined plans show effects working together (`examples/editorial-hook.json`, `examples/podcast-hook.json`).

### Proof and numbers
| fx | What happens | Options |
|---|---|---|
| `over-the-shoulder` | Camera pushes over the left shoulder to a Before card, swings to the right for After, settles. Cards slide out from behind the head and tuck back; motion blur follows camera speed. | `before`, `after`, `before_label`, `after_label`, `parallax` |
| `kallaway-split` | "You're the peak": plays full frame, then drops (motion-blurred, its shadow tightening as it lands) into a rounded card on grained grid paper. The card's top edge is the chart's ground: bars rise out from behind it as a skyline that peaks behind your head, the best number in Claude orange, the rest hatched in ink falling away to both sides, values counting up from the outside in, the hero last. A marker loop circles the hero; the title's accent word gets a marker underline; opens back to full frame. | `bars` (`Label:Value\|...`), `title`, `by`, `accent`, `pop`, `card`, `scale` |
| `glass-graph` | A frosted glass card rises at chest height; the number counts up in 18 frames and an orange graph draws with it. | `text`, `from`, `to`, `color` |
| `glass-widgets` | Frosted glass widgets around your head: a counting stat, a climbing watch-time graph, a follow card, an "Edited by Claude" pill. | `text`, `label`, `delta`, `graph`, `hours`, `name`, `handle`, `pill`, `tone` (dark \| light) |
| `tier-list` | Classic creator tier list (pastel S-D tiles, charcoal bars, white items) under the chin; items drop in every 4 frames, rows nudge as they land, status rolls to "Ranked". | `text` (topic), `S` `A` `B` `C` `D` (items with `\|`), `logos` (folder; file names = items) |

### Type and captions
| fx | What happens | Options |
|---|---|---|
| `text-behind` | A huge condensed word rises out from behind the body, focusing, holds behind the head with a slow lift, sinks back (or `exit: blow`). | `text`, `color`, `height`, `y`, `exit` |
| `backdrop-word` | A giant word drops in behind you letter by letter, with motion blur, and stays still while the camera moves. | `text`, `color`, `font` (anton \| bold \| serif), `width`, `y` |
| `kinetic-caption` | Words land one at a time, each focusing up from a blur. Big words are condensed caps (editorial) or heavy tight sans (podcast); `_underscored_` words are the small voice (a script, or small white). At `y: top` the last line straddles the top of your head and sits behind you; lower down it is in front and keeps its size through a punch-in. Leaves by `drop` (falls out with vertical motion blur) or `blow` (grows past the camera, going soft). | `text` (`_If you want your_ / CONTENT`), `style` (editorial \| podcast), `y` (top \| chest \| low \| 0-1), `layer`, `times` (clip seconds per word from `fcm words`), `rate` (4 frames), `size`, `color`, `exit`, `exit_dur` |

### Camera, light and look
| fx | What happens | Options |
|---|---|---|
| `lean-in` (`punch-in`) | The hard punch on one word: in over 5 frames with camera motion blur while the room and the words behind you go soft (`dof`), a slow creep while it holds, out over 6 frames. | `zoom`, `parallax`, `dof`, `in`, `out` |
| `slow-push` | A slow cinematic push-in while the room melts out of focus; real parallax on a still camera. | `zoom`, `blur`, `parallax` |
| `spotlight` | The lights go down, you stay lit with a warm rim, an optional glowing word behind you. | `text`, `color`, `push` |
| `color-grade` | Flat LOG look; a line of light wipes across leaving a cinematic teal/warm grade; Before / After pills ride the line. | - |
| `grade` | A colour grade on the room and you, with a vignette. | `grade` (moody \| bw \| warm \| cool \| pop) |
| `locked-on` | Corner brackets snap onto your face, a tag and a readout, and the camera follows you. It uses page chrome the director's rules list under "never ship": use it when the user asks for it. | `zoom`, `text`, `color` |

### 3D and depth
| fx | What happens | Options |
|---|---|---|
| `prop-3d` | A modelled prop (Blender GLB) lands beside your head (the side with more room; under the chin when neither fits) from oversize, turning into place, sways or spins while it holds, and drops out with motion blur. Lit by the studio environment plus a key light from the room's side, with a soft shadow. A clock's hands sweep `hours` and land exactly on the new time; a phone shows `image` (the real screenshot) on its screen, unlit so the UI reads true. | `model` (`trophy` \| `clock` \| `coin` \| `phone` \| `check` \| `x` \| a name in `<job>/models/` \| a `.glb` path), `side` (auto \| left \| right \| chin), `size`, `y`, `layer` (front \| behind), `spin` (deg/s; 0 = sway), `sway`, `tilt`, `light` (left \| right), `key`, `hours`, `time` (10:10), `image` |
| `carousel-spin` | Your reels spin around you in a real 3D carousel (Three.js), the front cards passing under your chin, then settle. | `images` (folder), `count`, `size`, `radius`, `tilt`, `turns`, `dof` |
| `orbit` | Your reels orbit your head in 3D: behind you at the top, in front at the bottom. | `images` (folder), `count`, `size`, `speed`, `tilt` |

### People, openers and framing
| fx | What happens | Options |
|---|---|---|
| `freeze-frame` | Shot freezes with a 4 % pop, room greys over 12 frames, white sticker outline + name tag, slow push while frozen, then lets go. | `name`, `role`, `flash` (0/1) |
| `name-tag` | Lower third: an outlined pill open on the left edge, name + role, slides in from the left focusing, slides back out. | `name`, `role`, `y` |
| `silhouette-intro` | The first few frames show you as a flat cream silhouette over the real room, then the footage cuts in. Put it at 0. | `frames` (4), `color` |
| `window-cards` | Retro desktop windows showing your reels (`thumbs/` or `images`) slide in under the chin like a conveyor; a cursor flies in and clicks one; it grows to the centre while the others leave; all drop out. | `images`, `count` (4), `pick` (2), `grow`, `title`, `titles` |
| `bottom-fade` | The bottom of the frame fades to dark (over you, under the captions: list it before them), optional soft room. | `amount`, `from`, `soft` |

Combining them: run `$FCM words <job>` and pass each caption's word starts as `times`, so every word lands on the voice. Chest
captions, `window-cards`, `tier-list` and chin props share the band under the chin: don't overlap them in time. Yellow editorial
captions want a darker wall; on a light wall pass `color` (or use `style: podcast` with `color: "#ffffff"`). Put camera effects
first in the plan; don't stack a full-width word with a big push.

## Intro: ChatRender, and the Outro
**ChatRender** (~2.4 s) opens any render with the chat beat of the studied "36 effects" reel (`references/instagram/De7JFJdo4KX.mp4`,
local only): a warm dark chat (menu, a Chat / Code toggle, compose), the clip attached in the "Reply to Claude..." box. "/"
opens a command card, "e" is typed and the card tapped to autocomplete `/effects`, two letters of the effect are typed and
tapped to complete it; the command turns orange once recognised; letter keys pop a magnified balloon and the predictive bar
quotes the word. Send: the keyboard drops, the clip and the orange command go up as the sent message, "Editing with
<effect>..." spins beside a small `SPED UP` tag, and a big 9:16 tile of orange specks fills into a mosaic that resolves into
the clip. The clip **plays inside the tile** from that frame on, the tile grows to fill the screen, and the film carries on
from there (nothing plays twice).
```json
{"intro": {"command": "/effects kallaway-split", "description": "your numbers rise as a chart above you"},
 "effects": [{"fx": "kallaway-split", "start": 0.2, "end": 4.2}]}
```
- `intro` takes `command` (default `/effects <first effect>`), `description` (the effect's card line), `base` (the
  `/effects` card line, default "N video effects for your clips"), `tag` (`SPED UP`, `""` for none), `placeholder` and
  `seconds` (2.4; every beat stretches to match). `"intro": true` or `fcm render ... --intro` uses the defaults.
- With an intro, `--range 0.2-4.4` picks the part of the clip that follows it; start it where the first effect starts.
  `fcm check` adds stills of the intro's beats (`i0.6` is 0.6 s into the intro).
- Its message box and keyboard sit in the bottom platform zone by design: it is a phone screen, not an overlay.

**Outro** (~4.4 s) ends a reel on the comment keyword: the viewer's comment ("claude") is the sent message, Claude answers
word by word ("Comment “claude” and I'll send you all N effects"), a dot tile resolves into a grid of every effect segment
playing, which fills the screen under a "Comment “claude”" headline with an orange "to get all N effects" pill; a comment box
then types the keyword and posts it, and a heart lands. A plan with `"outro"` renders it:
```json
{"outro": {"segments": ["1_kallaway-split.mp4", "..."], "labels": ["kallaway-split", "..."], "keyword": "claude", "count": 22, "skip": 60}}
```
`segments` are rendered effect MP4s (paths relative to the plan), `skip` the frames to skip into each (its chat intro), `count`
what the DM really sends. A full reel = one render per effect with its intro, then the outro, joined with hard cuts
(`ffmpeg -f concat`); see `examples/reel/run.sh`. Components: `remotion/src/intro/ChatRender.tsx`, `remotion/src/intro/Outro.tsx`,
`remotion/src/Film.tsx`.

## Rules (read `docs/director.md` and `docs/motion-rules.md` before changing or adding an effect)
- **Never cover the face.** Cards go beside the head or below the chin; front layers that could cross it use `faceGuard`.
- **Platform zones** (1080 × 1920): nothing in y 0-250 or 1536-1920, nothing at x > 940 for y 864-1536. Panels under the chin
  shrink to fit (to ~0.72) instead of entering the caption zone. A face that sits low in the frame leaves little room under the
  chin: say so, and suggest framing with the eyes at about a third of the height next time.
- **Real numbers.** The defaults (1,204 → 412K, the AI-tools tier list) are examples. Ask for the user's real numbers; if they
  have none, mark the numbers as examples on screen or in the caption.
- **Motion**: entries do most of their travel in the first 4-8 frames, exits ease in; things arrive by moving, unmasking or
  focusing, almost never by fading; one visible spring per film (the freeze-frame pop); no light flashes; every hold keeps one
  living thing.
- Visuals only: sound effects and captions are added elsewhere (CapCut, or reelmaxxing's captions).

## Adding an effect
An effect is an `FxDef` in `remotion/src/effects/` (see `lib/core.ts`): optional `camera`, `room` / `person` / `world` CSS
filters, `Behind` / `Front` / `Screen` components, `freeze`, `sticker`, `personScale`, `split`, `card` + `Backdrop` (shrink the shot into a card over a set), `cameraBlur`, `depth`.
Every component is a pure function of `c.t` (seconds into the effect) and `c.face`; use `specFrame(c, N)` to write timings in
30 fps frames of an N-frame reference. 3D goes through `lib/three.tsx`: `PixelCanvas` (z = 0 is the frame in pixels, `at()` places
things), `roundedBox`, `usePainted` / `textCanvas`, and for Blender models `useGLB` + `useFitted` (+ `useMeshTexture` / `cover` for
an image on a named mesh); `effects/Prop3D.tsx` is the worked example. Use `useTimeline` (GSAP built paused, seeked per frame) or `e()` / `fr()` eases - never
a timeline that plays on its own clock, never `Math.random()` without a seed. Register it in `effects/index.tsx`, run
`npx tsc --noEmit` in `remotion/`, then check stills.

## Checking the cut-out
```bash
ffmpeg -v error -y -ss 2 -c:v libvpx-vp9 -i <job>/person.webm -frames:v 1 /tmp/p.png
ffmpeg -v error -y -f lavfi -i color=c=0xff3366:s=1080x1920 -i /tmp/p.png -filter_complex overlay -frames:v 1 /tmp/matte.jpg
```
Hair edges should be clean and props the person holds (a mic) kept. If it is soft or flickers, re-track with
`--matte mediapipe` to compare, or improve the light on the next shoot.

## Credits and licences
Based on [claude-video-effects](https://github.com/Vibha-Ramprakash/claude-video-effects) by Vibha Ramprakash
(@vibha.in.progress, MIT): the idea, many effect concepts and names, and the ChatRender / ending look. Keep this credit.
Face: OpenCV YuNet (MIT). Cut-out: RobustVideoMatting (GPL-3.0, downloaded at setup, not bundled) or MediaPipe Selfie
Segmenter (Apache 2.0). Fonts via @remotion/google-fonts (OFL). Remotion is free for individuals and companies of up to 3
people; larger teams need a Remotion company licence. GSAP and Three.js are free. Blender and the `bpy` module are GPL; they are only run as tools, and the props you make with them are
yours. The built-in props in `props/` were made with `scripts/blender/props.py` and are MIT like the rest of this skill's code.

<!-- craft-handoff:start -->
## Mở và sửa tiếp trong FilmCraft / EffectCraft

Khi user muốn sửa tiếp trong FilmCraft hoặc EffectCraft, không giao một MP4 phẳng: viết timeline spec rồi dùng skill `craft-handoff` dựng project gốc (`.fcproj` / `.ecproj`) có đủ track, clip, keyframe, chữ, effect và SFX. Với skill này: footage gốc V1 nguyên vẹn; mỗi card / hiệu ứng render nền trong suốt thành một clip trên track riêng đúng thời điểm; phụ đề thường → SRT, chữ động theo cụm → text clip. Chi tiết: `craft-handoff/references/skills-map.md`.
<!-- craft-handoff:end -->

<!-- ===== /file: facecammaxxing/SKILL.md ===== -->

<!-- ===== file: facecammaxxing/README.md ===== -->

# facecammaxxing

Pro motion-graphics effects on your own talking-head clip, as a Claude Code skill. Remotion + GSAP + Three.js render the
effects over a clean cut-out of you (RobustVideoMatting), so words, cards, 3D rings and Blender-modelled props sit **behind your
head** or float in front of you, track your face, and stay out of the Reels UI. It works like an award-level reel director:
brief, one idea per sentence, a beat plan, the hardest beat first, and a measured self-review (`docs/director.md`).

> **Based on [claude-video-effects](https://github.com/Vibha-Ramprakash/claude-video-effects) by Vibha Ramprakash
> ([@vibha.in.progress](https://instagram.com/vibha.in.progress)).** The idea of a drop-in-your-clip effects skill for Claude
> Code, many of the effect concepts and names, and the look of the ChatRender intro and the comment-keyword ending come from
> her repo and reels. This version rebuilds the pipeline on Remotion, GSAP and Three.js. Her work is MIT licensed; its notice
> is kept in [LICENSE](LICENSE). Go give her a follow 💛

```bash
bash install.sh                                   # link into ~/.claude/skills/facecammaxxing
.venv/bin/python scripts/fcm.py setup             # venv, models, Remotion (prints READY)
.venv/bin/python scripts/fcm.py track clip.mp4 job
.venv/bin/python scripts/fcm.py check job plan.json
.venv/bin/python scripts/fcm.py render job plan.json --out final.mp4
.venv/bin/python scripts/fcm.py blender job my_prop.py --name mic   # optional: model a 3D prop in headless Blender
```

## The effect library

22 effects, all equal: one library, grouped only by the job each does in a beat. Every preview below is a real render on the same
6.8 s DJI clip; click one for the MP4, or the name for the plan that made it (`examples/<fx>.json`). Numbers, names and tier-list
items on screen are examples: pass your own.

### Proof and numbers
<table>
<tr><td align="center" valign="top" width="25%"><a href="demo/over-the-shoulder.mp4"><img src="demo/over-the-shoulder.webp" width="180" alt="over-the-shoulder"></a><br><a href="examples/over-the-shoulder.json"><code>over-the-shoulder</code></a><br><sub>Camera pushes over each shoulder to Before / After cards</sub></td><td align="center" valign="top" width="25%"><a href="demo/kallaway-split.mp4"><img src="demo/kallaway-split.webp" width="180" alt="kallaway-split"></a><br><a href="examples/kallaway-split.json"><code>kallaway-split</code></a><br><sub>The clip drops into a card; your numbers rise behind your head</sub></td><td align="center" valign="top" width="25%"><a href="demo/glass-graph.mp4"><img src="demo/glass-graph.webp" width="180" alt="glass-graph"></a><br><a href="examples/glass-graph.json"><code>glass-graph</code></a><br><sub>Frosted card, the number counts up, an orange line draws</sub></td><td align="center" valign="top" width="25%"><a href="demo/glass-widgets.mp4"><img src="demo/glass-widgets.webp" width="180" alt="glass-widgets"></a><br><a href="examples/glass-widgets.json"><code>glass-widgets</code></a><br><sub>Glass stat, graph, follow card and pill around your head</sub></td></tr>
<tr><td align="center" valign="top" width="25%"><a href="demo/tier-list.mp4"><img src="demo/tier-list.webp" width="180" alt="tier-list"></a><br><a href="examples/tier-list.json"><code>tier-list</code></a><br><sub>An S-D tier list builds under your chin</sub></td></tr>
</table>

### Type and captions
<table>
<tr><td align="center" valign="top" width="25%"><a href="demo/text-behind.mp4"><img src="demo/text-behind.webp" width="180" alt="text-behind"></a><br><a href="examples/text-behind.json"><code>text-behind</code></a><br><sub>A huge word rises from behind your body</sub></td><td align="center" valign="top" width="25%"><a href="demo/backdrop-word.mp4"><img src="demo/backdrop-word.webp" width="180" alt="backdrop-word"></a><br><a href="examples/backdrop-word.json"><code>backdrop-word</code></a><br><sub>A giant word drops in behind you, letter by letter</sub></td><td align="center" valign="top" width="25%"><a href="demo/kinetic-caption.mp4"><img src="demo/kinetic-caption.webp" width="180" alt="kinetic-caption"></a><br><a href="examples/kinetic-caption.json"><code>kinetic-caption</code></a><br><sub>Word-by-word captions, top line tucked behind your head</sub></td></tr>
</table>

### Camera, light and look
<table>
<tr><td align="center" valign="top" width="25%"><a href="demo/lean-in.mp4"><img src="demo/lean-in.webp" width="180" alt="lean-in"></a><br><a href="examples/lean-in.json"><code>lean-in</code></a><br><sub>A hard punch-in on one word, with motion blur and depth of field</sub></td><td align="center" valign="top" width="25%"><a href="demo/slow-push.mp4"><img src="demo/slow-push.webp" width="180" alt="slow-push"></a><br><a href="examples/slow-push.json"><code>slow-push</code></a><br><sub>A slow push-in with real parallax; the room melts soft</sub></td><td align="center" valign="top" width="25%"><a href="demo/spotlight.mp4"><img src="demo/spotlight.webp" width="180" alt="spotlight"></a><br><a href="examples/spotlight.json"><code>spotlight</code></a><br><sub>Lights down, you lit with a warm rim, a glowing word</sub></td><td align="center" valign="top" width="25%"><a href="demo/color-grade.mp4"><img src="demo/color-grade.webp" width="180" alt="color-grade"></a><br><a href="examples/color-grade.json"><code>color-grade</code></a><br><sub>Flat LOG look wiped into a cinematic grade</sub></td></tr>
<tr><td align="center" valign="top" width="25%"><a href="demo/grade.mp4"><img src="demo/grade.webp" width="180" alt="grade"></a><br><a href="examples/grade.json"><code>grade</code></a><br><sub>A colour grade on you and the room</sub></td><td align="center" valign="top" width="25%"><a href="demo/locked-on.mp4"><img src="demo/locked-on.webp" width="180" alt="locked-on"></a><br><a href="examples/locked-on.json"><code>locked-on</code></a><br><sub>Brackets snap onto your face and the camera follows</sub></td></tr>
</table>

### 3D and depth
<table>
<tr><td align="center" valign="top" width="25%"><a href="demo/prop-3d.mp4"><img src="demo/prop-3d.webp" width="180" alt="prop-3d"></a><br><a href="examples/prop-3d.json"><code>prop-3d</code></a><br><sub>A Blender-modelled prop lands beside your head, lit like the room</sub></td><td align="center" valign="top" width="25%"><a href="demo/carousel-spin.mp4"><img src="demo/carousel-spin.webp" width="180" alt="carousel-spin"></a><br><a href="examples/carousel-spin.json"><code>carousel-spin</code></a><br><sub>Your reels spin around you in a 3D carousel</sub></td><td align="center" valign="top" width="25%"><a href="demo/orbit.mp4"><img src="demo/orbit.webp" width="180" alt="orbit"></a><br><a href="examples/orbit.json"><code>orbit</code></a><br><sub>Your reels orbit your head, behind you and in front</sub></td></tr>
</table>

### People, openers and framing
<table>
<tr><td align="center" valign="top" width="25%"><a href="demo/freeze-frame.mp4"><img src="demo/freeze-frame.webp" width="180" alt="freeze-frame"></a><br><a href="examples/freeze-frame.json"><code>freeze-frame</code></a><br><sub>Freeze, the room greys, a sticker outline and a name tag</sub></td><td align="center" valign="top" width="25%"><a href="demo/name-tag.mp4"><img src="demo/name-tag.webp" width="180" alt="name-tag"></a><br><a href="examples/name-tag.json"><code>name-tag</code></a><br><sub>A lower-third name tag slides in from the edge</sub></td><td align="center" valign="top" width="25%"><a href="demo/silhouette-intro.mp4"><img src="demo/silhouette-intro.webp" width="180" alt="silhouette-intro"></a><br><a href="examples/silhouette-intro.json"><code>silhouette-intro</code></a><br><sub>Opens on a flat silhouette, then the footage cuts in</sub></td><td align="center" valign="top" width="25%"><a href="demo/window-cards.mp4"><img src="demo/window-cards.webp" width="180" alt="window-cards"></a><br><a href="examples/window-cards.json"><code>window-cards</code></a><br><sub>Retro windows of your reels; a cursor clicks one</sub></td></tr>
<tr><td align="center" valign="top" width="25%"><a href="demo/bottom-fade.mp4"><img src="demo/bottom-fade.webp" width="180" alt="bottom-fade"></a><br><a href="examples/bottom-fade.json"><code>bottom-fade</code></a><br><sub>The bottom fades dark so captions and tags read</sub></td></tr>
</table>

### Intro
<table>
<tr><td align="center" valign="top" width="25%"><a href="demo/chat-render.mp4"><img src="demo/chat-render.webp" width="180" alt="chat-render"></a><br><a href="examples/chat-render.json"><code>ChatRender</code></a><br><sub>A 2.5 s chat intro: the command is typed and sent, then dots resolve into the effect</sub></td></tr>
</table>

Any plan can open with it: add `"intro": {"command": "/glass-graph", "description": "A glass card with a graph that climbs"}`, or
pass `--intro` to `fcm render`.

### Effects together
<table>
<tr><td align="center" valign="top" width="25%"><a href="demo/editorial-hook.mp4"><img src="demo/editorial-hook.webp" width="180" alt="editorial-hook"></a><br><a href="examples/editorial-hook.json"><code>editorial-hook</code></a><br><sub>Captions behind the head, retro windows, two punch-ins</sub></td><td align="center" valign="top" width="25%"><a href="demo/podcast-hook.mp4"><img src="demo/podcast-hook.webp" width="180" alt="podcast-hook"></a><br><a href="examples/podcast-hook.json"><code>podcast-hook</code></a><br><sub>Silhouette open, name tag, small lead-in over a big word</sub></td></tr>
</table>

See `SKILL.md` for the workflow, `docs/director.md` for how to direct it and `docs/motion-rules.md` for the motion and layout
rules every effect follows.

Needs: macOS or Linux, ffmpeg, Python 3.10-3.12 (or uv), Node 22+. Optional: Blender 3.6+ (or `pip install bpy` on Python 3.11)
for new 3D props; the built-in ones ship in `props/`.

<!-- ===== /file: facecammaxxing/README.md ===== -->

<!-- ===== file: facecammaxxing/docs/director.md ===== -->

# Director's brief for facecam effects

Distilled from *pro-animation-director* (the award-level reel director, animator and editor prompt) and adjusted for this
skill: the film is the creator's own talking-head clip, the voice is already recorded, and the work is the effects laid over it,
built with **Remotion + GSAP + Three.js**, with **Blender** for any modelled 3D object. The measured numbers live in
`motion-rules.md`; this file is how to think, in what order to work, and which tool does which job.

## Who you are
A senior motion designer, animation director and editor whose short vertical films win awards; an award-level UI designer and
Three.js developer. You direct the idea, design every frame as if it will be screenshotted, time every move to the frame, and
treat the person on camera as the hero: effects perform what they are saying and never compete with their face. You never
self-certify: you look at your own stills and render, judge them against the numbers and checklists here, and say plainly what
still fails.

## How you work (in this order, never skip)
1. **Brief.** Fill the brief at the end of this file. When the clip is a whole reel, also write its offer in four lines: the one
   true thing it proves, who it is for, what the viewer gets when they comment (it must already exist), and the KEYWORD (one word,
   4-8 letters, caps, easy to type on a phone). A blank line means stop and ask.
2. **Listen.** `fcm words` gives every word's time. Read the transcript as a script: hook → proof → 2-4 mechanism beats → payoff →
   CTA. Find the sentences that carry a claim; those are your beats. The rest stays clean footage.
3. **The idea.** For each beat, find the visual idea that belongs only to this sentence: its object, its gesture, its number, its
   verb, its success moment. Never the first association (a rocket for "launch", stars for a star-named product). Test: cover the
   creator's name; if any creator could run the same effect on the same line, find another idea.
   - Proof sentences get proof: the real number on a card, a chart that builds, the real UI on a phone screen.
   - A claim gets a **literal prop**: hours → a clock whose hands sweep; money → a coin; the win → a trophy; rejection → a red X;
     "it works" → a check; "the app" → a phone showing the real screen. If the prop does not exist yet, model it in Blender.
   - Opinions get type (a word behind the head), lists get structure (a tier list), a reveal gets a camera move.
4. **Beat plan.** One effect per sentence at most, each written into `plan.json` with:
   `buys` (the viewer believes ___ after it; no sentence, no beat), `on` (the word it lands on), the hero object, its one accent
   event (a punch-in OR a pop OR a pulse), and its lane (below). A headline, if any, states the claim in at most 7 words / 36
   characters; never a label like "STEP 2".
5. **Storyboard, then the hardest beat first.** Build the hero beat alone, run `fcm check`, look at the stills, fix, and only then
   build the rest. The check stills are the storyboard.
6. **Review your own render** with the checklist at the end. Fix in this order: untrue → covers the face or platform UI → the idea →
   beat connections → hierarchy → timing → finish.

## What good is
- **Show it, then say it.** The claim is performed on screen at the moment it is spoken: one specific case, real UI, real numbers.
  Proof is the largest share of the film.
- **Every beat causes the next.** The last frame of one effect hands off to the next: a carried object, a camera move that starts in
  A and lands in B, a match on the creator's gesture. A hard cut between effects must mean something.
- **Emphasis is spent, not spread.** One lit thing per frame (three at most). One accent event per beat. Big needs small around it.
  Endings get smaller in scale and bigger in feeling.
- **Time breathes.** Hold before what matters; give reading exactly its time; stop before the idea is used up. A designed breath of
  0.6-1.5 s before a payoff is good if you can say why.
- **One world.** One logic of light, material, lens and drawing for the whole film: one material (smoked glass with a thin light
  border, or the creator's own), one key light matching the room the clip was shot in, one lens. A 3D prop is lit like the room
  around the person, or it reads as a sticker.
- **Ambition where it counts.** The hero moment gets the hardest work: a modelled prop, real light, real depth of field, a dense
  composite. It should be worth a screenshot.
- **Alive, always.** No static effect: a held prop sways, a glint crosses a clearcoat, a push creeps in, a word lifts. Effects react
  to the person (land on a nod, leave on a gesture). But light stays stable: no flashes, ramp any light change over 12-30 frames.

## Craft laws (30 fps; numbers in motion-rules.md)
- **Cut on motion, never on rest.** An effect lands ~2 frames before its word is heard, already moving.
- **Land decelerates, leave accelerates.** Most of an entry's travel in the first 4-8 frames, then a long soft tail; exits ease in.
  Median move ≈ 10 frames. One visible spring per film.
- **Arrive from oversize, never from zero:** ~6 frames from scale 1.45 and -6°; a punch-in on a key word is 1 → 1.06-1.08 in
  5 frames, back over ~24.
- **Almost nothing fades.** Arrive by moving, unmasking (rising out from behind the body), cutting or focusing; leave by dropping out
  with motion blur or blowing past the camera. No cross-dissolves, no fade to black.
- **No dead frame.** A held frame keeps one living thing.
- **Words at speech rhythm.** Caption words 2-12 frames apart (median ~6), 1-3 words per line, each landing ~2 frames before it is
  heard. Letter-by-letter typing only inside the product's own input field, with an irregular rhythm.
- **The demo is physical.** A cursor parks before it clicks; a press squashes 2-3 frames and the target answers a frame later;
  counters step every frame for 8-18 frames and land exactly on the value (a clock's hands sweep and land on the new time).
- **One system per film.** One frame clock, one blur grammar, one accent colour with one meaning (Claude orange `#D97757` = the win),
  the creator's own type.

## The format around the person (1080 × 1920)
- Length 15-35 s (45 s hard max), 7-11 beats of 1.6-4.4 s. Frame 0 already moves and the first word is spoken by frame 6. No logo,
  greeting or "in this video".
- Keep out of 0-250 px (platform top UI), 1536-1920 px (caption and username) and the right rail (x > 940 for y 864-1536).
  Headline band 270-370, hero zone 400-1300, captions 1320-1470.
- Never cover the face. Cards and props go beside the head or below the chin; type that sits higher goes *behind* the head.
- The ending is the KEYWORD (typed into a comment box, or as the last caption), 1.5-3.5 s, still in motion: the reel loops.

## The props are characters
- A prop is cast by its role in the beat (the win, the hours, the money, the app), one silhouette that reads at thumbnail size.
- It acts: it lands, turns to the camera, sways, and leaves on a gesture. One or two actions per beat, never a frozen sticker.
- One prop belongs to one reel. Recolour or remodel it rather than reusing last week's.

## The build: which tool does which job
Every effect is a pure function of its own clock `c.t` and the tracked face `c.face`. Remotion renders frames out of order and in
parallel, so nothing may run on its own clock: no `useFrame`, no playing timeline, no `Math.random()` without a seed.

| Lane | Use it for | How |
|---|---|---|
| **Remotion** (layers + camera) | The stack: room → behind → you → front → screen, the one camera move, parallax, freeze, split, card | `FxDef` slots in `remotion/src/effects/`, see `lib/core.ts` |
| **GSAP** (choreography) | Every move's timing and ease | Build a timeline once, paused, in reference frames, and seek it per frame: `useTimeline(specFrame(c, N), ...)`; single moves with `e()` / `fr()` |
| **HTML / CSS** | Type, captions, glass cards, real UI, grades | Plain components; `backdrop-filter` glass over the real room; `faceGuard` on anything in front that could cross the face |
| **Three.js** | Anything that needs depth, light or material: rings of cards, slabs, extruded type, clearcoat, reflections | `PixelCanvas` (z = 0 maps 1:1 onto frame pixels, so `at(W, H, x, y)` places objects next to the face), `roundedBox`, `usePainted` + `textCanvas` for crisp text textures, a studio environment map |
| **Blender** (headless) | A modelled object: a literal prop, a trophy, a device, a mic | A Python script built on `scripts/blender/kit.py` → `fcm blender <job> <prop or script.py>` → `<job>/models/<name>.glb` → `prop-3d`, or `useGLB` + `useFitted` in an effect of your own |

### The Blender lane, step by step
1. **Is it needed?** Only when the beat's prop is an object no HTML card or Three.js primitive can be (a cup, a clock, a phone).
   The built-in props (`trophy`, `clock`, `coin`, `phone`, `check`, `x`) ship ready-made in `props/`; use them without Blender,
   or rebuild one in another colour with `fcm blender <job> coin --color '#D97757' --name coin`.
2. **Model it.** Copy `scripts/blender/template.py` and build with `kit.py`: `lathe` (cups, knobs, bottles), `box` with `bevel`,
   `cylinder` (`facing='front'` for dials and coins), `torus`, `plane` (screens, labels), `material` (Principled BSDF: colour,
   metallic, roughness, emission, coat). Real proportions in metres; `export()` centres the prop and scales its largest side to 1.
3. **Conventions** (so `prop-3d` can place, light and animate any prop): the front faces Blender's front view (-Y); low-poly
   (under ~20k triangles), PBR materials only, no textures you would need to ship separately; moving parts are separate objects
   named `hand_hour` / `hand_minute` (turn about the front axis), `screen` (a plane with 0..1 UVs; gets the `image`), `spin`.
4. **Run it headless:** `fcm blender <job> my_prop.py --name mic` finds Blender (`$BLENDER`, PATH, the macOS app, snap, flatpak) or
   a Python with the `bpy` module (`$BLENDER_PY`), runs `blender -b --factory-startup -P my_prop.py -- <out.glb>`, and prints the
   prop's size.
5. **Place, light and time it** in the plan: `{"fx": "prop-3d", "model": "mic", "side": "left", "light": "right", ...}`. Match
   `light` to the side the room's key light comes from. Then `fcm check` and look: the prop must read as lit by the same room.

## Sound (hand-off; this skill makes the picture)
Voice 3.5-4.1 words/s with no silence over ~0.15 s, a music bed to the last frame ducked ~9 dB under speech, -14 LUFS integrated,
true peak ≤ -1 dBTP, 2-4 synced SFX per beat on pops, stamps, whips, prop landings and the keyword. Hand the effect times from
`plan.json` to whoever mixes.

## Never ship (delete it; do not argue for it)
- Page chrome: a corner logo, tracked-caps labels, scene counters ("02 / THE WAIT"), timecodes, progress bars, corner brackets.
- Deck layouts: a held left-aligned headline block, a kicker above a title, "headline left, device right".
- Generic web UI: a rounded card with a status dot and "label · value", zinc greys, skeleton bars, invented names or numbers.
- Invented statistics or fake proof; a stat slide (a big centred number over a small label); a placeholder "0" left on screen.
- Slogan copy: "Not just X, it's Y", "Unlock", "Meet X", "the future of", "game-changer", three one-word sentences.
- House-style defaults: a giant word cropped by the frame edge, colour-flood or circle wipes, a dot that becomes the logo, a
  headline typed with a caret, a fade to black.
- An object pinned at the same screen position for three or more beats; an end card held longer than 1.4 s.
- A 3D prop lit differently from the room, or one that floats without a shadow.
- A render you did not watch, or "verified" claims without numbers.

## Self-review before you hand over
Watch the render at real speed, then answer in writing:
1. One sentence per effect: what is the hero, what does it make the viewer believe (`buys`), which word does it land on?
2. Is every number real and sourced? Anything illustrative marked as an example?
3. Any frame static or empty for more than 3 frames? Any light pop or flicker?
4. Readable on a phone (UI text and hero numbers at least ~4 % of the frame height)? One hero per frame?
5. Does anything collide with the face, another effect or the platform zones?
6. Does every 3D prop sit in the room's light, with a shadow?
7. What would you still improve, in order of impact?

Deliver: the film's path, the cover frame (the hero beat's best still), and a short NOTE: each effect and what it buys, what is
real vs illustrative, the measured numbers, and what you would still fix. When the clip is a whole reel, add the post caption
(line 1 = the hook in other words; line 2 = the comment-keyword offer; one line of value; 3-5 specific hashtags) and the DM reply.

## BRIEF (fill per clip)
- The one true thing this clip says:
- Audience and language (e.g. Indonesian, casual "aku/kamu"):
- Source of every number on screen (links), or "examples":
- Words that carry a claim (from `fcm words`):
- Props the claims call for (built-in, recoloured, or to model in Blender):
- Room light: which side the key light comes from:
- Length target, and the KEYWORD + what the DM sends (whole reels only):
- Tools available: Remotion + GSAP + Three.js (always), Blender (yes / no / `bpy`):

<!-- ===== /file: facecammaxxing/docs/director.md ===== -->

<!-- ===== file: facecammaxxing/docs/motion-rules.md ===== -->

# Motion rules for facecam effects

Distilled from *pro-animation-director* (the reelmaxxing / motionmaxxing house rules) down to what applies to an effect laid
over a real talking-head clip. These numbers are measured at 30 fps, and every effect in the library is held to them. Where an
effect's original look breaks a rule, the rule wins and the original stays available as an option (noted below).

## Timing
- **Land decelerates, leave accelerates.** An entry does most of its travel in the first 4-8 frames, then a long soft tail
  (`expo.out` / `power3.out`). An exit eases in and leaves (`power2.in`). The median move is about 10 frames.
- **Arrive from oversize, never from zero.** Cards, chips and tags pop in over ~6 frames from scale ~1.45 and -6° (mirror the
  angle on the other side). Nothing grows from scale 0.
- **One visible spring per film.** Here it is the freeze-frame's 4 % body pop. Everything else lands without overshoot.
- **Counters** step every frame for 8-18 frames and land exactly on the value (no long crawl, no near-miss).
- **Punch-in** on a key word: a subtle one is 1 → 1.06-1.08 in 5 frames, back over ~24 frames. The editorial punch (`lean-in`,
  from the studied reel) is harder: 1 → 1.3 in 5 frames with camera motion blur and the room / behind words going soft, a
  slow creep while held, back out in 6 frames. One hard punch per sentence at most.

## Arrival and exit
- **Exits leave by moving.** A front caption or card drops out of frame with vertical motion blur (`drop`); a word behind
  you grows past the camera and goes soft (`blow`). Both ease in over ~8 frames.
- **Almost nothing fades.** Things arrive by moving, unmasking (rising out from behind your body, being revealed by a wipe line)
  or focusing (blur to sharp). A fade, if any, lasts 2-4 frames and hides inside a move.
- **No dead frame.** A held shot keeps one living thing: a slow drift, a lift, a pulse, a slow push on a frozen frame.
- **Light stays stable.** No flashes or sudden brightness pops; ramp a light change over 12-30 frames.
  (Guide conflict: the freeze-frame's white flash is off by default, `flash=1` brings it back.)

## Emphasis
- One lit thing per frame (three at most), one accent event per effect: a punch-in OR a pop OR a pulse.
- Big needs small around it: one hero number per card, everything else small and quiet.
- One material for the whole film: glass (smoked or clear) with a thin light border and a soft shadow. No zinc-grey web UI,
  no status dot + "label · value" cards.
- One accent colour with one meaning: Claude orange `#D97757` = the win.
- A 3D prop (`prop-3d`) follows the same rules as a card: arrives from oversize in ~6 frames while turning into place over ~14,
  sways or spins while held (the living thing), drops out over 8 frames. It is lit from the room's key side (`light`) and
  casts a soft shadow; a prop lit differently from the room reads as a sticker.

## Layout (1080 × 1920, scale for other sizes)
- Keep out of the top 0-250 px (platform UI), the bottom 1536-1920 px (caption and username) and the right rail
  (x > 940 for y 864-1536).
- Hero zone 400-1300. Never cover the face: cards go below the chin or beside the head. If the face sits low in the frame,
  panels shrink to fit the band under the chin (down to ~0.7) before they ever touch the caption zone.
- Proof must read on a phone: the hero number at least ~4 % of the frame height (≈ 77 px at 1920).

## Never ship
- Page chrome: corner brackets, timecodes, tracked-caps labels, scene counters, progress bars.
- A giant word cropped by the frame edge.
- Invented numbers presented as real: the defaults (1,204 → 412K, the AI-tools tier list) are examples; replace them with the
  creator's real numbers, or say on screen that they are examples.

## Self-review (after every render)
1. Watch it at real speed. One sentence per effect: what is the hero, what does it prove?
2. Any frame static for more than 3 frames? Any light pop or flicker?
3. Is the hero number readable on a phone? One hero per frame?
4. Does anything collide with the face, another card or the platform zones?
5. Are the numbers real? What would you still improve, in order of impact?

<!-- ===== /file: facecammaxxing/docs/motion-rules.md ===== -->

<!-- ===== file: facecammaxxing/examples/reel/segments.txt ===== -->

1_kallaway-split 0.2 1.901
2_over-the-shoulder 0.6 2.234
3_backdrop-word 2.0 3.634
4_glass-widgets 3.2 4.834
5_spotlight 1.2 2.834
6_color-grade 3.0 4.634

<!-- ===== /file: facecammaxxing/examples/reel/segments.txt ===== -->

<!-- ===== file: facecammaxxing/models/NOTICE.md ===== -->

# Models

Downloaded by `scripts/setup.sh` from their official homes:

- `yunet.onnx`: YuNet face detector (face_detection_yunet_2023mar), https://github.com/opencv/opencv_zoo, MIT licence.
- `selfie_segmenter.tflite`: MediaPipe Selfie Segmenter, https://ai.google.dev/edge/mediapipe/solutions/vision/image_segmenter, Apache License 2.0.
- `rvm_mobilenetv3_fp32.onnx`: RobustVideoMatting (MobileNetV3), https://github.com/PeterL1n/RobustVideoMatting, GPL-3.0.
  Not committed to this repo; if you redistribute the skill, the matte model stays a separate download.

<!-- ===== /file: facecammaxxing/models/NOTICE.md ===== -->

<!-- ===== file: facecammaxxing/requirements.txt ===== -->

numpy
opencv-python
pillow
mediapipe
onnxruntime

<!-- ===== /file: facecammaxxing/requirements.txt ===== -->
