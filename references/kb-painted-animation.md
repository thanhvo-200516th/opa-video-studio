# kb-painted-animation — toàn văn tài liệu của nguồn `painted-animation`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/painted-animation/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: painted-animation/SKILL.md ===== -->

---
name: painted-animation
description: Make hand-painted watercolour-and-ink cartoon videos (MP4) with code — p5.js + p5.brush rendered frame by frame in headless Chrome, encoded with ffmpeg — starring Clawd or any character. Use when the user asks to make an animation, animated short, cartoon, music video, lyric video, animated GIF/loop or "a video of Clawd…", or mentions the PDoomVideo / ClaudeAnimationBase approach. Covers storyboarding, the engine API, the render-and-look review loop, music/lyric sync and splitting long videos across subagents.
---

# Painted animation

A method for making short cartoons entirely in code, distilled from [JohnHeibel/PDoomVideo](https://github.com/JohnHeibel/PDoomVideo) (a 156 s music video painted by Claude Opus) and its generalised kit [ClaudeAnimationBase](https://github.com/JohnHeibel/ClaudeAnimationBase) (MIT), which is bundled here as `template/`.

**How it works:** every frame is a pure function of time `t`. `studio.html` loads p5.js + p5.brush and your scene files; each shot paints the whole 1920×1080 frame with watercolour fills and boiling ink lines. `render.mjs` drives headless Chrome to render contact sheets for review, or every frame in parallel, and ffmpeg encodes the MP4 (with audio if given).

## Workflow

### 0. Scaffold

```bash
bash ~/.claude/skills/painted-animation/scripts/new_project.sh <project-dir>        # add --keep-demo to keep the example scene hooked up
```

This copies the template, unhooks the demo scene, runs `npm install` and checks node / ffmpeg / Chrome. Then **read `<project-dir>/ANIMATION_GUIDE.md` in full** before designing anything: it holds the rules, the animation principles and the complete engine / Clawd API. Look at `docs/emotions.jpg` and `docs/views.jpg` (the model sheets) with the Read tool.

For a music video or anything longer than ~20 s, also read [references/music-video.md](references/music-video.md). For a lyric video, ask for the song file and an LRC first, and measure the tempo with `scripts/beat_grid.py`: lines are usually faster than you'd guess.

### 1. Storyboard before code

Write `STORYBOARD.md` in the project (format in the guide: logline, world + palette arc, motif, the character's emotion arc, then shots with **reads** — the timed list of what the viewer must understand). Worked example: [examples/xiaozhen/](examples/xiaozhen/) (a 31 s lyric video: storyboard and full scene code).

Show the storyboard to the user and let them react before building, unless they said to just go ahead.

### 2. Build shot by shot

- Set `duration`, `bpm`, `offset` (and `audio`) in `src/config.js`.
- One IIFE-wrapped file per scene/chapter in `src/scenes/`, ending with `shots([[t0, fn], ...])`; add its `<script>` to `studio.html`.
- Block key poses first, check them as stills, then add the motion between them.

### 3. Render and look — every shot, several times

You can't see motion by reading code. From the project dir:

```bash
node render.mjs --sheet=0.1,0.8,1.6,2.4 --cols=4 --w=480 --out=out/check/a.jpg        # key frames
node render.mjs --strip=2.1:2.6 --out=out/check/strip.jpg                             # every frame of a moment
node render.mjs --sheet=2.3 --crop=760,420,500,400 --w=500 --out=out/check/face.jpg   # full-res detail
```

Open each image with Read and actually check it against the guide's review list: event clear? character big enough? reads timed so a first-time viewer gets them? anticipation / follow-through, no snaps? feet and held props touching? transitions at every seam? no text, no 3D, no pure black/white, no muddy glows? Fix and look again. Budget: ≥ 1 sheet per shot, a strip per key motion and transition, a crop per story-carrying face.

### 4. Render the video

```bash
node render.mjs --clip --out=out/video.mp4                                   # short videos, one worker
node render.mjs --frames --workers=4 && node render.mjs --encode --out=out/video.mp4 [--audio=assets/song.mp3]   # long ones, parallel + resumable
```

Report the output path, length and ms/frame. Offer `open out/video.mp4`.

## The rules that matter most

These are the guide's rules condensed; the guide is authoritative.

1. **Handmade medium.** Only `paint()` / `inkLine()` (p5.brush) — never plain p5 `rect`/`ellipse`/`fill`. Flat 2D only: turns go through drawn key views (`turn()`, `spinView()`), never 3D projection. Light via `glow()` (additive), because pigment-mixing makes yellow-over-blue go green.
2. **No text.** No captions, labels, signs or word bubbles; show it instead. Reactions are painted emotes (`!`, sweat, hearts…). The one exception is karaoke in a lyric video, and at most a few big SFX.
3. **Something happens in every shot** — an event, cause → reaction, set-ups that pay off.
4. **Time for the viewer.** List each shot's reads; one read at a time; fast actions, held meanings; lead the eye; the reads set the shot length. This is where generated animation fails most.
5. **Alive.** Nothing is still (idles from `feel()`, drifting cameras, boil); faces change through `emotions()` never by swapping; the character is big (medium shot u≈20–28, close-up 40–70); everything rides the beat.
6. **Transitions at every seam**, chosen to fit the story (brush wipe, iris / shaped iris, whip pan, match cut, cut on action, camera carry-through).
7. **One piece.** One world, a colour arc, an emotional thread, linked scenes, an ending that rhymes with the opening.

## Engine gotchas

- **Pure functions of `t`.** Frames render in parallel and out of order: no state across frames, no `Math.random()`, no frame-by-frame physics. `hash(i)` for stable randomness, `jit()` for boil.
- **`boilSeed(key)`** before each separate background element/prop, or a moving thing makes everything drawn after it re-boil every frame (jitter).
- **Don't name globals after p5's.** p5 defines `line`, `OVERLAY`, `text`, `color`, `scale`, … as globals; a top-level `function line()` fails with `Cannot redefine property` and the page never becomes ready (the renderer times out). Keep helpers inside the scene IIFE or give them distinct names.
- **Layering in doorways, windows and screens:** draw what's inside, then paint the surrounding wall/frame back over it, so nothing wider than the opening shows outside it (the train's `inDoor` + door jambs, the TV bezel pieces).
- A `NaN` in a point list throws `Failed to construct 'OffscreenCanvas'` — guard degenerate geometry.
- Under camera zoom ≳ 2, huge shapes lose outlines; outline weight scales with zoom, so scale `sw` down in close-ups.
- Cost = number of fills and strokes. Aim for ≤ ~1.5–2.5 s/frame (the log prints ms/frame). Prefer fewer, bigger shapes. On machines without a real GPU, watercolour fills are slow — consider fewer `fill` shapes, or `--soft-gl` as a last resort.
- macOS: the renderer uses `--use-angle=metal` and finds `/Applications/Google Chrome.app` automatically; otherwise pass `--chrome=<path>`.

## Adapting

- Clawd is the default star, not a requirement. New characters, props and emotions are drawn with the same tools (`paint`, `ribbon`, `through`, `glow`) and kept on-model across shots; new emotions go in `EMO` in `src/clawd.js`.
- `src/karaoke.js` (template) adds word-by-word karaoke for lyric videos via the `window.overlayHook` hook in `core.js`.
- `LOOPS.name = t => {...}; LOOPS.name.len = 4;` + `node render.mjs --loop=name --png` makes a seamless loop for GIFs (`ffmpeg -i out/loop_name/f%04d.png …`).
- Higher reasoning effort tends to give more extravagant, detailed scenes.

<!-- craft-handoff:start -->
## Mở và sửa tiếp trong FilmCraft / EffectCraft

Khi user muốn sửa tiếp trong FilmCraft hoặc EffectCraft, không giao một MP4 phẳng: viết timeline spec rồi dùng skill `craft-handoff` dựng project gốc (`.fcproj` / `.ecproj`) có đủ track, clip, keyframe, chữ, effect và SFX. Với skill này: mỗi cảnh một clip (nền trong suốt nếu phủ lên nền khác); tiêu đề ít chuyển động → text clip gốc; cần chỉnh chuyển động từng ký tự → EffectCraft qua `ae-script-builder`. Chi tiết: `craft-handoff/references/skills-map.md`.
<!-- craft-handoff:end -->

<!-- ===== /file: painted-animation/SKILL.md ===== -->

<!-- ===== file: painted-animation/README.md ===== -->

<div align="center">

# painted-animation

<a href="README.md"><img src="https://img.shields.io/badge/English-2B2233?style=for-the-badge" alt="English"></a>
<a href="README.zh-CN.md"><img src="https://img.shields.io/badge/简体中文-D97757?style=for-the-badge" alt="简体中文"></a>

A Claude Code skill for producing hand-painted animation and lyric videos with Claude Opus 5.5.
Part of [opus-video-skills](../../README.md).

</div>

![小镇姑娘](docs/xiaozhen-sheet.jpg)

## Overview

The skill enables Claude Opus 5.5 to produce complete animated videos, including storyboarding, character animation, camera work, transitions, music synchronisation and karaoke subtitles. All imagery is drawn procedurally in code; no image generation model is involved.

The method is derived from two projects by John Heibel: [PDoomVideo](https://github.com/JohnHeibel/PDoomVideo), a 156-second music video produced largely autonomously by Opus 5.5, and [ClaudeAnimationBase](https://github.com/JohnHeibel/ClaudeAnimationBase), a general-purpose animation kit based on it. This skill packages both into a single workflow and extends it with a lyric-video pipeline that covers tempo detection, audio clipping and karaoke subtitles.

## How It Works

1. **Storyboard.** Claude writes a shot list covering setting, palette, character arc and transitions. For each shot it lists the "reads", the timed sequence of what the viewer must understand.
2. **Drawing.** Each shot is a JavaScript function that paints the complete frame with p5.js and the [p5.brush](https://github.com/acamposuribe/p5.brush) watercolour library. Every frame is a pure function of time.
3. **Review.** Contact sheets, frame strips and close-up crops are rendered in headless Chrome. Claude inspects the images and revises the code until each shot meets the guidelines.
4. **Output.** Frames are rendered in parallel and encoded to MP4 with ffmpeg, with audio muxed in if provided.

## Characteristics

- **Character consistency.** Each character is defined by a single drawing function, so its design is identical across all shots.
- **Frame-accurate timing.** Because frames are computed from time, events can be aligned precisely to beats or to individual sung syllables.
- **Localised revision.** A change to one element requires editing only the relevant code and re-rendering the affected range; the rest of the video is unaffected.
- **Built-in animation principles.** The engine provides anticipation, squash and stretch, follow-through and acted expression changes as reusable functions.
- **Automated self-review.** Rendered frames are checked against an explicit list covering legibility, timing, contacts, transitions and colour.

## Example: 小镇姑娘 (David Tao)

<p align="center"><img src="docs/koi-gag.gif" width="520" alt="大经理 → 大锦鲤"></p>

A 31-second lyric video for one verse of the song. Inputs: the lyrics, a request to take the song's wider context into account, a request to include the fan wordplay in which "大经理" (big manager) is heard as "大锦鲤" (big lucky koi), the audio file, and LRC timestamps.

- **Setting.** One small-town railway station throughout, with the ending mirroring the opening: her departure by train one year earlier, and his own departure at the end.
- **Visual motif.** A flower identifies the female character in each of her forms: at the train window, on the television, as a koi, and as a star.
- **Timing.** The song measures 154 BPM with 8 beats per line, and all action is cut to that grid.
- **Wordplay.** On the syllables "经理", the television image transforms into a koi while the subtitle is struck through and replaced with "锦鲤". The koi then leaves the screen and becomes the "shining star" of the following line.

The storyboard and scene code are available in [examples/xiaozhen](examples/xiaozhen/). The audio is not included for copyright reasons.

## Requirements

- Claude Code with Claude Opus 5.5
- Node.js, Google Chrome, ffmpeg
- Python 3 with numpy (for tempo detection only)

## Installation

See the [collection README](../../README.md#installation). As a plugin:

```
/plugin marketplace add tuzhechen2005/opus-video-skills
/plugin install painted-animation@opus-video-skills
```

## Usage

Describe the desired video in Claude Code, for example:

> Make a 15-second video of Clawd trying to catch a butterfly.

> Make a lyric video for this song. (with the audio file and an LRC file attached)

The skill can also be invoked directly with `/painted-animation`. It creates a project, presents a storyboard, builds and reviews each shot, and writes the result to `out/video.mp4`. Render times depend on the GPU; watercolour fills are considerably slower on integrated graphics.

## Repository Structure

| Path | Description |
|---|---|
| `SKILL.md` | Workflow and rules followed by Claude |
| `template/` | Animation engine: character, brushes, camera, transitions, karaoke, renderer |
| `scripts/new_project.sh` | Project scaffolding and toolchain check |
| `scripts/beat_grid.py` | Tempo and beat-phase detection with LRC line alignment |
| `references/music-video.md` | Guidelines for music videos and longer productions |
| `examples/xiaozhen/` | Storyboard and scene code for the example above |

## Acknowledgements

The animation engine and guide are adapted from [ClaudeAnimationBase](https://github.com/JohnHeibel/ClaudeAnimationBase) by John Heibel (MIT License; see [template/LICENSE](template/LICENSE)). The overall method follows his [PDoomVideo](https://github.com/JohnHeibel/PDoomVideo). The project uses p5.js, p5.brush, Puppeteer and ffmpeg. The skill and the example were produced with Claude Opus 5.5 in Claude Code.

## License

MIT. See the repository [LICENSE](../../LICENSE).

<!-- ===== /file: painted-animation/README.md ===== -->

<!-- ===== file: painted-animation/README.zh-CN.md ===== -->

<div align="center">

# painted-animation

<a href="README.md"><img src="https://img.shields.io/badge/English-2B2233?style=for-the-badge" alt="English"></a>
<a href="README.zh-CN.md"><img src="https://img.shields.io/badge/简体中文-D97757?style=for-the-badge" alt="简体中文"></a>

基于 Claude Opus 5.5 的手绘风格动画与歌词 MV 制作技能（Claude Code Skill）。
属于 [opus-video-skills](../../README.zh-CN.md) 合集。

</div>

![小镇姑娘](docs/xiaozhen-sheet.jpg)

## 概述

本技能使 Claude Opus 5.5 能够独立完成动画视频的制作，涵盖分镜设计、角色动画、镜头运动、转场、音乐同步与卡拉 OK 字幕。所有画面均由代码程序化绘制，不依赖任何图像生成模型。

该方法源自 John Heibel 的两个项目：[PDoomVideo](https://github.com/JohnHeibel/PDoomVideo) 和 [ClaudeAnimationBase](https://github.com/JohnHeibel/ClaudeAnimationBase)。前者是一部主要由 Opus 5.5 自主完成的 156 秒音乐视频，后者是在其基础上整理的通用动画工具包。本技能将二者整合为统一的工作流程，并在此基础上增加了歌词 MV 流程，包括节拍检测、音频剪辑与卡拉 OK 字幕。

## 技术原理

1. **分镜。** Claude 编写镜头表，确定场景、配色、角色情绪线与转场方式。每个镜头都列出观众需要依次理解的信息，并为每条信息分配时间。
2. **绘制。** 每个镜头是一个 JavaScript 函数，使用 p5.js 与水彩笔刷库 [p5.brush](https://github.com/acamposuribe/p5.brush) 绘制完整画面。每一帧都由时间唯一确定。
3. **审查。** 在无头 Chrome 中渲染关键帧拼图、逐帧序列与局部特写，由 Claude 检查画面并修改代码，直至每个镜头符合规范。
4. **输出。** 各帧并行渲染后，由 ffmpeg 编码为 MP4；如提供音频，一并合入。

## 主要特性

- **角色一致性。** 每个角色由单一绘制函数定义，在所有镜头中造型保持一致。
- **逐帧精确的时间控制。** 画面由时间计算得出，事件可精确对齐到节拍乃至单个唱词。
- **局部修改。** 修改某一元素只需调整相应代码并重新渲染受影响的片段，其余部分不受影响。
- **内置动画原理。** 引擎以可复用函数的形式提供预备动作、挤压与拉伸、跟随动作及表情过渡。
- **自动审查。** 渲染画面会依据明确的检查清单逐项核对，涵盖可读性、节奏、接触关系、转场与色彩。

## 示例：陶喆《小镇姑娘》

<p align="center"><img src="docs/koi-gag.gif" width="520" alt="大经理 → 大锦鲤"></p>

本例为该曲一段主歌的 31 秒歌词 MV。输入包括：歌词；参考整首歌上下文的要求；体现歌迷将"大经理"谐音为"大锦鲤"这一梗的要求；原曲音频；LRC 时间轴。

- **场景。** 全片设定在同一座小镇火车站，首尾呼应：开头为一年前女主角乘火车离开，结尾为男主角登上火车离去。
- **视觉线索。** 女主角头上的小花贯穿她的各个形态：车窗中、电视里、锦鲤与星星。
- **节奏。** 经测定，歌曲速度为 154 BPM，每句 8 拍，全部动作均按此节拍剪辑。
- **谐音梗。** 唱到"经理"时，电视画面中的人物变为锦鲤，字幕中的"经理"同时被划去并替换为"锦鲤"；随后锦鲤跃出屏幕，化作下一句中"闪亮的星星"。

分镜与场景代码见 [examples/xiaozhen](examples/xiaozhen/)。因版权原因，仓库中不包含音频。

## 环境要求

- Claude Code 及 Claude Opus 5.5
- Node.js、Google Chrome、ffmpeg
- Python 3 及 numpy（仅节拍检测需要）

## 安装

参见[合集说明](../../README.zh-CN.md#安装)。以插件方式安装：

```
/plugin marketplace add tuzhechen2005/opus-video-skills
/plugin install painted-animation@opus-video-skills
```

## 使用方法

在 Claude Code 中描述所需视频，例如：

> 制作一段 15 秒的动画：Clawd 试图抓住一只蝴蝶。

> 为这首歌制作歌词 MV。（附音频文件与 LRC 文件）

也可通过 `/painted-animation` 直接调用。技能会创建项目、提交分镜、逐个镜头制作并审查，最终输出 `out/video.mp4`。渲染耗时取决于显卡性能；在集成显卡上，水彩填充会明显变慢。

## 目录结构

| 路径 | 说明 |
|---|---|
| `SKILL.md` | Claude 遵循的工作流程与规则 |
| `template/` | 动画引擎：角色、笔刷、镜头、转场、卡拉 OK、渲染器 |
| `scripts/new_project.sh` | 项目初始化与环境检查 |
| `scripts/beat_grid.py` | 节拍与相位检测，并将 LRC 歌词对齐到节拍 |
| `references/music-video.md` | 音乐视频与长篇制作规范 |
| `examples/xiaozhen/` | 上述示例的分镜与场景代码 |

## 致谢

动画引擎与动画指南改编自 John Heibel 的 [ClaudeAnimationBase](https://github.com/JohnHeibel/ClaudeAnimationBase)（MIT 协议，见 [template/LICENSE](template/LICENSE)），整体方法参照其 [PDoomVideo](https://github.com/JohnHeibel/PDoomVideo)。本项目使用了 p5.js、p5.brush、Puppeteer 与 ffmpeg。技能本身及示例由 Claude Opus 5.5 在 Claude Code 中完成。

## 许可协议

MIT，见仓库的 [LICENSE](../../LICENSE)。

<!-- ===== /file: painted-animation/README.zh-CN.md ===== -->

<!-- ===== file: painted-animation/examples/xiaozhen/STORYBOARD.md ===== -->

# Example · 小镇姑娘 (David Tao), a 31 s lyric video

Made with this skill by Claude Opus 5.5 in Claude Code. The prompt was the lyrics of one verse plus three notes: read the song's context so the visuals aren't abrupt; fans joke that "大经理" (big manager) is "大锦鲤" (big lucky koi), so show that; and later, the song file and the LRC timings. The scene code is in [xz_set.js](xz_set.js) (the world, cast and props) and [xz_shots.js](xz_shots.js) (the shots). To run it, scaffold a project, copy both files into `src/scenes/`, add `src/karaoke.js` with the song's `LY` table, and put your own copy of the song in `assets/`. The song isn't included.

![contact sheet](../../docs/xiaozhen-sheet.jpg)

**Logline:** A year ago the small-town girl left on the train, crying at the window. Now I hear she's a "big manager" (a big lucky koi). Seeing her shine like a star and happy, I can finally stop worrying, and I take the train myself.

**Song grid:** 154 BPM (half-time 77.125), one lyric line = 8 beats ≈ 3.1 s. The clip is 146.887–177.987 s of the song: one bar before the first line, room after the last line for the ending, and a 2 s fade.

**One world:** a small-town railway station in three lights: dusk now → the sepia memory (old-film scratches) → night now. **Motif:** her flower. It's on her head, then on the koi, then on the star, so you always know it's her. **Rhyme:** she left by train at the start; I leave by the same kind of train at the end.

| Clip time | Line | Shot | In |
|---|---|---|---|
| 0–3.02 | (intro bar) | Dusk. I sit on the bench with my suitcase, staring down the empty line, and sigh. | iris from dark |
| 3.02 | 还记得一年前站在火车站 | Sepia memory. She turns, walks to the train, and hops into the doorway; I step after her with a hand out. | sepia brush wipe |
| 6.07 | 看着自己的悲剧演完 | The door shuts. The platform becomes a stage: a spotlight on me, a rain cloud, and the red curtain falls. | cut on action |
| 9.08 | 透过玻璃窗看见你的泪满面 | The curtain opens on the train window (my POV): she cries and presses her paw to the glass, and the window slides away. | curtain |
| 12.38 | 那车头依然吐着烟 | The engine puffs a cloud on every beat as it pulls out; I run, stop and wave; the smoke swallows the frame. | cut on action |
| 15.39 | 听说现在的你成了大经理 | Night, the waiting-room TV: she's on an award stage in a tie. **On "经理" (≈17.6):** poof, she's a big golden koi (with the flower and tie), the crowd bows to it, and the lyric is struck through and becomes **锦鲤**. That line is then held above the next one for 1.4 s. | smoke clears |
| 18.64 | 前途好比闪亮的星星 | The koi leaps out of the TV, out of the window, swims up the night sky, and **becomes a star** on "星星". | cut on action |
| 21.54 | 我只希望这所有能够让你欢喜 | Tilt down to me. Her star smiles and winks; I clasp my hands, a little heart floats up to her, and the star glows. | camera carries through |
| 25.01 | 我才能放心走 | The night train pulls in; I pick up my case, wave up at her star, and hop aboard; the door shuts and it pulls out. Tilt up to her star, it winks, iris. | — |

**Lessons it taught the skill:** get the LRC and measure the tempo before storyboarding (the first draft, timed by feel, was twice too slow); carry a gag across a line boundary instead of slowing the song; paint a doorway's jambs back over whoever stands in it; don't name globals after p5's (`line`).

<!-- ===== /file: painted-animation/examples/xiaozhen/STORYBOARD.md ===== -->

<!-- ===== file: painted-animation/references/music-video.md ===== -->

# Long-form and music videos (lessons from the P(doom) video)

The P(doom) music video (156.6 s, 9 chapters, ~7,800 lines) was built by Claude Opus in Claude Code with only two instructions from the human: "use the Clawd character" and "give each lyric interesting visuals and transitions". This file captures how it was organised, so a video longer than ~20 s can be made the same way. Its storyboard is at [PDoomVideo/STORYBOARD.md](https://github.com/JohnHeibel/PDoomVideo/blob/main/STORYBOARD.md); a finished lyric video made with this skill is in [examples/xiaozhen](../examples/xiaozhen/).

## 1. Lock the song grid first

- **Ask for the song file and an LRC** (or the time each line starts). Never guess lyric timing from a slow "feel": pop songs are usually faster than they sound, and one line is often only 2–3 s.
- Measure the tempo and beat phase: `python3 scripts/beat_grid.py song.mp3 --from=100 --to=200 --lrc=song.lrc` (needs numpy). It prints the BPM, a beat time, and each lyric line's beat index. Lines usually start a fraction of a beat before a bar line (pickups).
  - P(doom): 88 BPM, beat 0.682 s. 小镇姑娘: 154 BPM (half-time 77), one line = 8 beats ≈ 3.1 s.
  - For a ballad, set `PROJECT.bpm` to the half-time pulse so idles and bounces don't look frantic.
- **Cut a clip on a bar line**: start one bar (or two) before the first line you use, end a bar or two after the last, and fade out:
  `ffmpeg -ss <start> -t <len> -i song.mp3 -af "afade=t=in:d=.25,afade=t=out:st=<len-2>:d=2" -c:a aac assets/clip.m4a`.
  Clip time = song time − start. Choose `start` so a beat lands on clip time 0, then `offset: 0`.
- Lyric table `LY` in `src/karaoke.js`: `[start, end, "text", opts]` in clip time, lines running into each other. `opts.sing` = seconds to sing the line (drives the fill); `opts.hold` keeps a line up (lifted, two-row KTV style) after the next starts; `opts.pun = { from, to, at }` strikes `from` and pops `to` above it.
- **Fast lines, one visual per line.** Budget every shot to its line's 8 beats; put the gag on the word it belongs to (find the word's beat), and when a gag needs more read time than the line gives, carry it into the next line (the koi keeps swimming and leaps out on the next line; the struck lyric is held above the next one) instead of slowing the song.
- Put the audio in `assets/` and set `PROJECT = { duration, bpm, offset, audio: 'assets/clip.m4a' }`.
- Write the beat times of each chapter at the top of its file as a comment: `const B = n => OFF + n * BEAT; // B(4) 2.94 · B(12) 8.39 …` so hits land exactly.

## 2. Storyboard shape for a song

- **One idea for the whole video**, stated in a paragraph (P(doom): "a stage show that goes off the rails… the whole apocalypse was a play").
- **Cast table**: each recurring character, their look and their arc (Clawd grows tiny → planet-sized → back to cute).
- **What ties it together**: a recurring set (all choruses return to the *same stage*, escalating each time), an escalating motif (the P(doom) thermometer climbs 8→34→61→86→99.9), a palette arc, a rule for transitions.
- **Chapters** = song sections (intro, verse, chorus, bridge…). Each gets one setting and a small palette, e.g. `The Lab · night indigo, lamp ochre, monitor teal`.
- **Shot table per chapter**: `| Time | Lyric | Shot | Out |`. One shot per lyric line (1.4–4 s). The *Out* column names how it leaves: "camera keeps pushing in", "CHOMP: mouth closes over the camera to black", "the cube drops through the floor".
- **Act the lyric, don't write it.** Every line is a visual gag that shows the meaning. The karaoke already carries the words, so no signs or captions that repeat them.
- A handful of big SFX across the whole video (FOOM, BOOM, CHOMP, SLAM) is fine; not more.
- End by rhyming with the opening (curtain opens at 0 s → curtain falls at the end).

## 3. Code layout for many chapters

- One file per chapter in `src/scenes/` (`c01_intro.js`, `c02_chorus1.js`, …), each an IIFE whose helpers stay private, ending with `shots([...])` for its shots. Add each `<script>` to `studio.html` in order.
- Shared, stable things (characters, recurring props like the stage/thermometer, palette, lyrics) live in shared files that chapter authors don't edit. Guest characters a later chapter reuses get exported on a shared object (`CAST.basilisk = (x, y, s, t, o) => {...}`).
- Chapter breaks get a transition (P(doom) used a brush wipe at each chapter boundary, with a different colour pair per chapter). Inside a chapter, the action carries across the cut.
- For karaoke, include `src/karaoke.js` after `timeline.js` in `studio.html` and fill `LY`. Keep key action above y ≈ 960 while a line shows. It loads a Chinese brush font (Ma Shan Zheng) for exactly the characters in `LY` through `window.EXTRA_FONTS`.

## 4. Parallel subagents (optional, for long videos)

P(doom)'s second generation was painted by parallel subagents, one per chapter, all briefed by the same guide. Do this only if the user asks for subagents or the video is long enough to justify it; otherwise build chapters yourself in order.

1. Write the storyboard, the shared files and at least one finished chapter yourself first, so there is a working reference for style and API.
2. Write a short `CHAPTER_BRIEF.md` in the project (the orchestrator's brief to subagents). It should contain:
   - "Read ANIMATION_GUIDE.md and STORYBOARD.md first."
   - Only edit your own chapter file. If a shared helper is missing, write it privately inside your IIFE. If you find a bug in a shared file, report it; don't edit it.
   - Frames are pure functions of `t` (they render in parallel, out of order): no state across frames, no `Math.random()`.
   - The canvas conventions (1920×1080, karaoke band), the beat grid, the chapter's palette, and the size rule (the lead character ≈ 40% of frame height in dance shots).
   - Performance budget: ≤ ~2.5 s/frame; hundreds of fills/strokes, not thousands.
   - The review loop: render sheets and strips of every shot, first/last frames, and the seams into and out of the chapter; open them and iterate until each shot is charming, readable and lively.
3. Spawn one subagent per chapter with that brief plus its chapter's storyboard rows and time range. Several can render at once.
4. When they finish, render sheets across every chapter seam yourself and fix continuity (palette, character scale, screen direction, the escalating motif).

## 5. Rendering a long video

```bash
node render.mjs --frames --workers=4          # parallel, resumable JPEG frames into out/frames
node render.mjs --encode --audio=assets/song.mp3 --out=out/video.mp4
```

`--frames` skips frames already on disk, so a crash or a fix to one chapter only needs `rm out/frames/f0XXXX.jpg` for that range and a re-run (or `--range=a:b`).

<!-- ===== /file: painted-animation/references/music-video.md ===== -->

<!-- ===== file: painted-animation/template/ANIMATION_GUIDE.md ===== -->

# Animating Clawd

Read this whole file before you draw anything. It covers how to make a short, hand-painted cartoon, starring Clawd or any character you design: the rules and animation principles that make it look good, the workflow that catches mistakes, and the full reference for the character and the engine.

The person prompting you decides **what** the video is about. This guide decides **how** it's made. If they ask for something the rules below forbid (a caption, a 3D spin), do what they ask.

**No design here is final.** Clawd, the emotions, the props and the helpers are a starting point, not a limit. Change any of them, Clawd's own design included, and add whatever new characters, props or emotions the idea needs. Paint new things with the same tools and rules, so they belong with the rest.

Look at the model sheets first:
- [docs/emotions.jpg](docs/emotions.jpg): all 31 emotions.
- [docs/views.jpg](docs/views.jpg): the five key views, the motion helpers and the hats.

---

## The three goals

Every rule below serves one of three goals.

- **Handmade.** The video should look like someone painted it by hand, frame by frame. That means brush strokes, ink lines that boil, flat 2D and no lettering.
- **Alive.** Something is always moving and something is always happening. Faces act instead of snapping, and characters are big enough to feel.
- **One piece.** It's one short film, not a pile of clips. Plan it before you draw it, and link every scene to the next.

Underneath all three, the viewer has to be able to follow it. Timing (rule 4) is the rule models get wrong most often.

## The rules

### 1. The medium is solid: brush strokes, flat 2D, boil

- **Paint everything with p5.brush through `paint()` and `inkLine()`.** Characters get flat `wash` colour plus an ink outline. Backgrounds get soft watercolour `fill` shapes, usually with no outline or a thin one. Never use plain p5 shapes (`rect`, `ellipse`, `fill()`): they look like 2000s Flash.
- **The linework boils.** `jit()` and `random()` are reseeded 12 times a second (`BOIL`), so every drawing wobbles slightly, like hand-drawn animation. That's the look; don't fight it. For anything that must stay put from frame to frame (star positions, tuft heights), use `hash(i)`. Give each separate element its own seed with `boilSeed(key)` (see Engine), or one moving thing makes everything drawn after it jitter.
- **Everything is flat 2D. Never project 3D.** Don't rotate a box in perspective, don't use `rotateY` or WEBGL 3D and don't fake depth with math. Clawd turns through **drawn key views** (front → 3/4 → side → back 3/4 → back), exactly like a cartoon model sheet: see `turn()` and `spinView()`. Depth comes from overlap, scale and colour (farther = smaller, bluer, paler), never from a projection.
- **Light is the one exception.** p5.brush mixes colour like pigment, so a yellow glow painted over blue turns green, and a thin wash over it turns grey. Use `glow()` for anything that shines: it adds real light, under the paper grain.
- **Soft palette, no pure black or white.** Use `PAL.ink` for black and `PAL.cream` or `PAL.paper` for white. Keep colours soft and harmonious, and keep Clawd clearly readable against the background.

### 2. No text

- **Show it, don't write it.** Models overuse text. No captions, no titles, no labels on objects, no signs, no speech bubbles with words, no words on screens, no "ZZZ" typed in a font.
- **Clawd's reactions are painted marks, never letters**: `!`, `?`, zzz, sweat, hearts, a bulb, a rain cloud. Use the emotes (see the reference).
- **A sign that repeats the story is the classic failure.** If Clawd holds a sign saying "I'm lost", the shot has failed. Show Clawd being lost: looking left, then right, the map upside down, a sweat drop.
- If the prompt truly needs a word (a name, a shop sign that is the joke), use `letter()`. Paint it into the scene, keep it to one or two words and use it once.

### 3. Something happens in every scene

- **Every shot needs an event:** something changes between its first frame and its last. Clawd wants something, finds something, tries, fails, reacts or gets it. "Clawd stands in a meadow being cute" is not a shot.
- **One focal action at a time.** Stage it with a clear silhouette and nothing competing for attention, so it reads at a glance.
- **Cause, then reaction.** When something happens, Clawd reacts to it: a take, an emotion change, a turn toward it. The reaction is often the funniest part, so give it time.
- **Pay it off.** Whatever you set up in a shot (a door, a sandwich, a strange noise) gets resolved on screen, in that shot or a later one.

### 4. Timing: model the viewer

Timing turns a set of drawings into a story. It's also where generated animation fails most often: everything moves at one brisk speed, events pile on top of each other, and moments are over before anyone understands them.

You know what happens because you wrote the code. The viewer doesn't: they see it once, at full speed, for the first time. **For every moment, ask what the viewer needs to understand and how long that will take them, and time it for that.**

- **Write the reads.** For each shot, list in order what the viewer has to understand. Each item is a *read*. Every read needs time for the eye to find it, time to understand it, and a moment to register before the next thing starts. Small, distant, fast or subtle things take longer to find and understand than big, central, obvious ones.
- **One read at a time.** Don't start a new read while the viewer is still taking in the last one. When two things happen at once, the viewer sees only one of them. Put a cause and its reaction in sequence, not on top of each other.
- **Fast actions, slow meanings.** A motion can be very quick if it's anticipated, but what it means needs held time. Anticipation tells the viewer where to look before the action, and the hold after it lets them understand it. Move quickly through what doesn't matter to the story, and spend time on what does. That contrast between quick and held is what gives a film rhythm; one constant speed, fast or slow, makes it flat and hard to follow.
- **Lead the eye.** The viewer looks at whatever moves, is bright, is big or is being looked at. Before an important read, get their eye to the right place (a character looks at it, the camera moves to it, it moves or lights up first), and give the eye time to get there.
- **Let the reads set the length.** A shot is as long as its reads need. A shot with many reads can't be short, and a shot whose reads have all landed shouldn't be padded. That includes the last shot: its final read needs time to land before the video ends.

For a worked example, see how the demo times its ending, at the end of this guide.

### 5. Alive

- **Nothing is ever still.** Every emotion has its own idle motion (`feel()`), cameras drift or push, grass sways, stars twinkle and the linework boils. A frozen frame reads as a bug.
- **Faces act, they never snap.** Change moods with `emotions()`. It does anticipation, a squint, a take and overshoot around every change. Never swap `eyes`/`mouth` by hand between two frames.
- **Move like a cartoon, not a machine.** Every move follows the animation principles in the next section.
- **Clawd is big.** In a medium shot, `u` is about 20–28 (Clawd is 10u wide, 8u tall). In a close-up it's 40–70. Tiny Clawds (u < 12) are for wide establishing shots only, and never for the whole video.
- **Everything moves on a beat.** `PROJECT.bpm` drives every idle, bounce and dance, so the whole film shares one pulse. Put the hits on beats (`pulse()`, `beatN()`), even with no music.

### 6. Transitions always

- **Every seam gets a transition:** into the first shot, between every pair of shots and out of the last one. Never start on a hard frame, and never just stop.
- **Pick a transition that belongs to the story**, and don't default to the same one every time. Some options:
  - a brush wipe (`brushWipe`)
  - an iris or shaped iris (`iris`, `irisShape`)
  - a whip pan with a smear
  - a match cut (the same shape or motion across the cut)
  - a cut on action (cut mid-move, and finish the move in the next shot)
  - a camera move that carries through into the next shot
  - a fade or push from paper or black
- A plain cut is fine only when it's on action or a deliberate smash cut.
- **Changes inside a shot are transitions too:** emotions go through `emotions()` and turns go through `turn()`. Props arrive and leave on arcs, never popping in.

### 7. One piece: a vision before any code

- **Storyboard first**, in writing, before you write any scene code (the workflow below has the format). If you're working with a person, show them the storyboard and let them react before you build.
- **One world.** Pick a palette and a setting that carries through, with a colour arc across the video (e.g. cold night → warm dawn as Clawd's mood lifts).
- **One thread.** The story has a beginning, a middle and an end, and Clawd's emotional arc follows it. Plan the emotion keys across the whole video, not per shot.
- **Rhyme the ending with the opening:** the same place, pose or motif, changed. It makes the film feel whole.
- **Link scenes:** motion continues across cuts, and screen direction stays consistent (if Clawd travels right, keep travelling right). Props and characters carry over.

---

## Animation principles

These are the classic principles of character animation, as they apply here. Most of them fix one problem: motion written as code comes out mechanical, because code moves every part at once, on the same curve, by the same amount.

- **Anticipation.** Before a big move, make a small move the opposite way: a crouch before a jump, a wind-up before a throw, a squint before a take. It tells the viewer something is coming and where to look. `jump()` and `emotions()` build it in.
- **Squash and stretch.** Bodies squash on impact and stretch when they move fast, keeping their volume (`sq`).
- **Slow in, slow out.** Almost nothing moves at a constant speed. Things ease out of one pose and into the next. A plain `lerp` over time looks mechanical, so run its progress through an easing (`ease`, `easeIn`, `easeOut`, `backOut`).
- **Weight.** How something starts and stops says what it weighs. Heavy things take longer to get going and to stop, and land with little bounce. Light things snap into motion, bounce and flutter to rest.
- **Arcs.** Living things move on arcs, not straight lines: thrown props, hops, arm swings, head turns (`arcPt`).
- **Overlapping action and follow-through.** Don't move every part at once. The eyes lead, the body follows, and arms, hats, props and tails drag behind, overshoot and settle last. Offset each part's timing a little from the one it hangs off (`spring`, `ring` and `backOut` for the settle).
- **Avoid twinning.** Code copies values, so both arms end up at the same angle, both eyes blink together and a crowd bounces in unison. Give one arm the action and the other something smaller, and offset timings, phases and `seed`s between characters.
- **Exaggeration.** Push poses, takes, squash and leans further than feels natural. In a short cartoon, subtle reads as nothing. If it looks like too much on the sheet, pull it back.
- **Strong key poses.** Each shot's storytelling poses should read as stills, with a clear silhouette and the body leaning into what it's doing, before any motion goes between them. If the key poses don't read, the motion won't fix it.
- **Show the thought.** A character notices, thinks, then acts, and the eyes move first. The viewer understands a choice when they see it being made.
- **Secondary action.** Small actions that support the main one (a hat bobbing, an emote popping, grass stirring) add life, but they never compete with it.

---

## Workflow

### 1. Storyboard

Write `STORYBOARD.md` before any scene code:

```
Logline: one sentence. Clawd wants ___, but ___, so ___.
World: setting, a small palette, light, how the colour changes across the video.
Motif: the thing that recurs and pays off.
Clawd's arc: the emotion keys across the whole video.
Shots:
  A  start–end  [transition in: ___]  what's seen · the EVENT · Clawd's reaction · camera
     reads:  start–end  the first thing the viewer must understand
             start–end  the next one (where is the viewer's eye when it starts?)
             ...
  B  start–end  [transition: ___]  ...
  ...
  [transition out: ___]
```

The reads are the timing sheet. Give each one a start and an end, make sure each has time to be found and understood, and make sure no two important reads overlap. If a shot's reads don't fit its length, lengthen the shot or cut a read; don't squeeze them.

Check the storyboard against the rules:
- Is there an event in every shot?
- Does every read have time to land before the next one starts?
- Is there a transition at every seam?
- Is there any text anywhere?
- Does the ending rhyme with the opening?

### 2. Build

- Set `duration` (and `bpm`) in [src/config.js](src/config.js).
- Put your scene in a new file (e.g. `src/scenes/my_video.js`), wrapped in an IIFE, and end it with `shots([...])`. In [studio.html](studio.html), **replace** the `demo.js` script tag with yours.
- Build and check one shot at a time, in order.
- Within a shot, block the key poses first and check them as stills (`--sheet` at the key times). Add the motion between them once they read.

```js
// src/scenes/my_video.js
(() => {
  function park(t, lt, dur) {                        // t = video time, lt = time in this shot, dur = shot length
    camBegin(960 + 20 * Math.sin(lt * .6), 540, 1 + .02 * lt);   // slow drift and push: the camera is never dead
    paint(rectPts(-200, -200, W + 400, H + 400), { wash: PAL.sky, ink: null });           // background
    paint(ellPts(960, 1150, 1400, 380, 40, 2), { wash: PAL.sap, ink: PAL.ink, sw: 1 });   // ground
    const mood = emotions(lt, [[0, 'bored'], [1.2, 'surprised'], [1.7, 'excited']]);      // acted changes
    const hop = jump(lt, 2.2, 2.7, 3);                                                    // add poses that share fields
    clawd(960, 860, 26, { ...mood, dy: mood.dy + hop.dy, sq: mood.sq + hop.sq });
    const at = toScreen(960, 860 - 4 * 26);          // Clawd's screen position, for the iris
    camEnd();
    if (lt < .45) iris(...at, lerp(0, 1500, easeIn(lt / .45)));            // transition in
    if (lt > dur - .3) brushWipe((lt - (dur - .3)) / .6);                 // transition out (next shot finishes it)
  }
  shots([[0, park] /*, [3.5, nextShot], ... */]);
})();
```

### 3. Look at it: the review loop

You can't see motion by reading code. Render and look at every shot, several times, at three zoom levels:

```bash
# contact sheet: the shape of the whole piece (every shot's first, middle and last frames)
node render.mjs --sheet=0.1,0.8,1.6,2.4,3.1,3.9 --cols=6 --w=320 --out=out/check/sheet.jpg
# strip: EVERY frame of a moment (turns, takes, jumps, throws, transitions)
node render.mjs --strip=2.1:2.6 --cols=6 --w=320 --out=out/check/strip.jpg
# crop: full-resolution detail (faces, hands, contacts, glows); crop=x,y,w,h in frame pixels
node render.mjs --sheet=2.3,2.4 --crop=760,420,500,400 --w=500 --out=out/check/face.jpg
# crop-at: the same, following a WORLD point through each frame's camera (a foot or a prop on a moving shot);
# x,y in world pixels (or an expression evaluated in the page), w,h in frame pixels
node render.mjs --strip=2.1:2.6 --crop-at=960,700,500,400 --out=out/check/feet.jpg
```

Open each image and actually look at it. Check:

- **Read:** is the event of each shot clear from its sheet alone? Is Clawd big enough, and does Clawd separate from the background?
- **Timing.** You can't judge timing from single frames, so read it like a viewer:
  - Render the shot as a sheet at a fixed step (every 0.1–0.15 s) and read it in order.
  - At each frame ask: where is the viewer looking right now, and do they understand it yet?
  - Count the frames each read gets (24 frames = 1 s). A read that flashes by in a few frames, or shares its frames with another read, will be missed.
  - After each important moment, is there time to take it in before the next thing starts?
- **Motion:** in strips, does every move have anticipation and follow-through? Are there any pops, jumps or snaps between frames? Do the parts move at different times, or all at once? Is anything moving at a constant speed, or mirrored left and right? Are the poses pushed far enough to read?
- **Boil:** in a strip, each pair of frames that share a boil drawing should match except where something moves. Anything still that changes every frame needs its own `boilSeed()`.
- **Contacts:** do feet touch the ground? Do held things touch the arm tips? Do thrown things leave from the hand?
- **Transitions:** check the first and last 0.5 s of every shot and every seam. Does it open and close with a transition?
- **Rules:** is there any text? Is there any 3D? Is there any dead stretch where nothing is happening?
- **Colour:** any muddy glows (use `glow()`), pure black or pure white?

Fix what you find, then look again. **Budget:** at least one sheet per shot, a strip for every key motion and transition, and a crop for every face that carries the story. Contact sheets run about 0.1–1 s per frame, so this is cheap: don't skip it.

### 4. Render

```bash
node render.mjs --clip --out=out/video.mp4                      # the whole video, straight to MP4
node render.mjs --frames --workers=4                            # or: parallel + resumable JPEG frames into out/frames …
node render.mjs --encode --out=out/video.mp4                    # … then encode them
```

---

## Engine

### Files

| file | what's in it |
|---|---|
| `src/config.js` | `PROJECT = { duration, bpm, offset, audio? }` |
| `src/core.js` | canvas, palette, timing and motion helpers, `paint()`, camera, full-frame effects, `glow()`, lettering, paper, render hooks |
| `src/clawd.js` | Clawd: views, emotions, eyes, mouths, hats, emotes, moves |
| `src/timeline.js` | `shots()`, `LOOPS`, `brushWipe()` |
| `src/sheets.js` | the model sheets as loops (`?loop=emotions`, `?loop=views`) |
| `src/scenes/demo.js` | an 11-second example. **Don't copy it** (see the end of this guide) |
| `studio.html` | open it in Chrome to scrub the video (`?t=2.5` jumps to a time, `?loop=emotions` shows a loop) |
| `render.mjs` | headless renderer: sheets, strips, crops, stills, PNG loops, MP4 |

### Frames are pure functions of time

- **Frames render in parallel and out of order.** A shot is `fn(t, lt, dur)` and must draw the same frame for the same `t`, every time. No state carried between frames, no counters, no `Math.random()`, no physics that integrates frame by frame. Compute everything from `t`, in closed form (the helpers below do this for you).
- Randomness: `hash(i)` for stable per-object values, and `jit(a)`/`random()` for boil (they change 12 times a second).
- **Seed each element with `boilSeed(key)`.** Each boil drawing holds for two frames, so anything that isn't moving must draw the same in both. But a moving thing uses a different amount of randomness each frame, which shifts the stream for everything drawn after it, and all of that re-boils every frame and looks jittery.
  - `boilSeed(key)` restarts the stream from the boil frame and a key that stays the same every frame (any string or number, unique within the frame).
  - Call it before each separate element: each background layer, prop and effect.
  - `clawd()` seeds itself and each of its parts, then reseeds when it's done, so nothing drawn after it depends on its pose. Its key is its call order; set `boilKey` if characters come and go mid-shot.
- **Each shot paints the whole frame,** background included. The paper texture is under everything and the grain is multiplied over the top, so leaving paper showing is a valid look.
- **Canvas:** 1920×1080, origin top-left, y down.
- `LOOPS.name = t => {...}; LOOPS.name.len = 4;` makes a standalone loop (tests, GIFs, sheets), rendered with `--loop=name`.

### Painting

`paint(pts, o)` paints one shape from a point list `[[x, y], ...]`:

| option | meaning |
|---|---|
| `wash, washOp` | flat colour (opacity 0–255, default 255). For characters, props, anything solid. |
| `fill, fillOp, bleed, tex, border` | watercolour fill with bleeding edges and pigment texture. For skies, hills, shading and shadows. `bleed` ~.05–.3, `tex` ~.3–.9. |
| `hatch: { d, a, o, b, c, w }` | hatching (distance, angle, `{rand, gradient}`, brush e.g. `'charcoal'`/`'HB'`, colour, weight). Texture, sparingly. |
| `ink, sw, br` | outline colour (default `PAL.ink`), weight (~.4–2), brush. **`ink: null` means no outline.** |
| `curv` | 0–1: smooth the outline through the points. |

- **Lines:** `inkLine(pts, sw, colour, brush = 'ink', curvature)`. The kit's brushes are `'ink'`, `'inkfine'` and `'dry'` (bristly). p5.brush's built-ins also work: `'2B'`, `'HB'`, `'charcoal'`, `'marker'`, `'pen'`, `'cpencil'`, `'rotring'`, `'spray'`.
- **Shapes:**
  - `rectPts(x, y, w, h, jitter)`
  - `ellPts(cx, cy, rx, ry, n, jitter, rot)`
  - `rrPts(x, y, w, h, r, jitter)`: a rounded rectangle
  - `starPts(cx, cy, r, inner, n, rot)`
  - `heartPts(cx, cy, r)`
  - `through(P)`: a smooth curve through the points
  - `ribbon(P, w0, w1)`: a tapered ribbon along a path, as one outline. Use it for tails, trails, vines and noodly arms.
- **One shape, one outline.** Build a creature or prop from as few outlines as you can, so it doesn't look like glued-on stickers: a tail is one `ribbon`, not five circles.
- **Light:** `glow(x, y, r, colour, a)`. It's additive, so it stays warm on dark grounds and barely shows on light ones (as real light would). Draw it before the things that sit in front of the light.
- **Palette** `PAL`: `paper, ink, clay, clayDk, clayLt, night, indigo, rose, ochre, sap, teal, violet, cream, sky`. `mixCol(a, b, k)` mixes two hex colours in RGB. Any hex colour works: pick a small palette per video.
- **p5.brush quirks:**
  - Colours mix like pigment: yellow over blue makes green. Layer light colours over dark ones with a full-opacity `wash`, or use `glow()`.
  - `wash` at 255 is exact colour; lower opacities mix.
  - Strokes drawn far from the origin under a zoomed camera collapse: from zoom ~2, an outline or a line at large
    world coordinates leaves only a dot at its first vertex. `paint()` and `inkLine()` draw each shape around its own
    centre, which avoids it. A shape much bigger than the canvas can still lose its outline: draw long edges as
    `inkLine`s no bigger than the canvas.
  - Outline weight is in world units, so it grows with the camera's zoom: a fine outline on a small shape becomes a
    dark blob in a close-up. Scale `sw` down with the zoom for small shapes.
  - A NaN in a point list throws `Failed to construct 'OffscreenCanvas': Value is not of type 'unsigned long'`, with
    a stack pointing at your scene rather than the NaN. Guard geometry that can degenerate (`Math.acos` of a ratio > 1).
  - p5 `push()/pop()/translate()/rotate()/scale()` work with all brush calls.
  - Cost is the number of `fill` shapes and strokes: hundreds are fine, thousands are not. Aim for ≤ 1.5 s per frame. The render log prints ms/frame.
  - Some scenes make p5.brush log five `WebGL: INVALID_OPERATION ... not from the associated program` warnings once per page. They're harmless (frames come out identical). Any other page error is real.

### Time and motion (all pure functions of t)

- **Progress and keys:**
  - `seg(t, a, b)`: 0..1 progress through [a, b]
  - `kf(t, [[t0, v0], [t1, v1], ...], ease)`: keyframes; values may be arrays
  - `lerp`, `clamp`, `frac`, `wob(t, freq, phase)`, `TAU`
- **Easing:** `ease`, `easeIn`, `easeOut`, `backOut` (overshoot) and `elasticOut`.
- **Rhythm:** `BEAT` (seconds per beat), `bpOf(t)` (beat position), `beatN(t)` (beat number), and `pulse(t, k)` / `pulse2(t, k)`, which are 1 on each beat (or eighth) and then decay.
- **Acting:**
  - `jump(t, t0, t1, h)`: crouch, stretch, arc and squash-land. Returns `{dy, sq}`.
  - `take(t, t0, amt)`: a surprise take, returns `{sq, dy}`.
  - `stroll(t, t0, t1, x0, x1, u)`: an eased walk. Returns `{x, walk, view, flip, dy}`.
  - `spring(t, t0, k, w)`: a damped wobble after an event, for settles and follow-through.
  - `ring(t, [t0, t1, ...])`: one `spring` kick per event time.
  - `arcPt(p0, p1, h, k)`: a point on a thrown arc.
  - `onTwos(t)`: holds each drawing for two frames. Wrap a shot's `t` in it for a snappier, hand-drawn feel.
- **Camera:**
  - `camBegin(cx, cy, zoom, rot)` … `camEnd()`: world point (cx, cy) lands at screen centre. One level only; always pair them.
  - `toScreen(x, y)`: world → screen while a camera is active. Use it to aim an iris at a character.
  - `shakeXY(t, amount)`: [dx, dy] to add to the camera on impacts.
- **Full-frame effects** (screen space, after `camEnd()`):
  - `brushWipe(p, [c1, c2])`: fat strokes cover the frame (p 0 → .5) and then drag off (.5 → 1). Cut under full cover. Its comment in timeline.js shows the two calls.
  - `iris(cx, cy, r, colour)` and `irisShape(pts, colour)`: shaped reveals.
  - `flash(k, colour)`: a full-frame flash.
- **Lettering** (only if you must, see "No text"):
  - `letter(txt, x, y, size, colour, {pop, rot, alpha, screen})`
  - `sfx(txt, x, y, size, colour, age)`
  - Both are composited at `flushLetters()`, after the shot. If a wipe or iris must cover them, call it yourself first.

---

## Clawd

Clawd is the Claude Code mascot: a terracotta block (`PAL.clay`), 10 units wide and 6 tall, with four stubby legs, two little arm nubs and two tall slit eyes. There's no mouth at rest. It's drawn in flat wash with an ink outline and boils like everything else. That's the default design, not a rule: change it if the idea needs it. Within one video, though, keep every character on model, with the same shape and features in every shot.

```js
clawd(x, y, u, options)   // (x, y) = ground point between the feet; u = size unit
```

**Sizes:** Clawd is 10u × 8u (legs included).

| shot | u | on screen |
|---|---|---|
| wide | 10–16 | small in the landscape |
| medium | 20–28 | the usual acting size |
| close-up | 40–70 | face acting |
| extreme close-up | 90+ | camera pushed in on the eyes |

### Options

| group | options |
|---|---|
| pose | `dx`, `dy` (in u; −dy = up), `sq` (squash; negative stretches), `rot` (pivots at the feet), `flip`, `sx`, `sy`, `aL`, `aR` (arm angle: 0 = straight out, + = up, − = down; ±1.5 is vertical), `walk` (leg phase), `noLegs`, `noShadow` |
| view | `view`: front, q, side, qback, back. `smear` 0..1 + `smearDir` ±1 (0 = both sides) for fast moves |
| face | `eyes`, `mouth`, `lookX`/`lookY` (−1..1), `squint` 0..1, `blush` 0..1, `gloom` 0..1, `lid` 0..1, `seed` (blink timing) |
| colour | `tint` (pale, flush, blue, rosy, green, gold, or any hex) + `tintK`, or `col`/`dk`/`lt` directly |
| extras | `hat`, `emote` + `emoteK` (0..1 pop) + `emoteAge`, `draw(u, sw)`, `armL(u, sw)`, `armR(u, sw)` |
| boil | `boilKey`: a stable id for its boil seeds (default: call order) |

Options compose by spreading: `clawd(x, y, u, { ...feel('happy', t), ...turn(t, 1, 1.15, 0, .25), hat: 'party' })`. Later spreads win, so put the emotion first and the pose after it. If both an emotion and a pose move the same field (`dy`, `sq`), add them together rather than letting one silently replace the other.

### Views and turns

These are drawn key views. Every view faces screen-right; add `flip: true` to face left.

| view | what you see |
|---|---|
| `front` | the face, both arms, four legs |
| `q` | 3/4: the face shifted toward the heading, the side face as a darker strip behind it |
| `side` | profile: one eye near the leading edge, one arm |
| `qback` | 3/4 from behind: no face |
| `back` | no face |

- **Turn with `turn(t, t0, t1, a0, a1)`.** Headings are in turns: 0 = front, .25 = facing right, .5 = back, −.25 = facing left. It steps through the key views over 0.12–0.25 s with smears, like a drawn turn. For a single heading, use `spinView(a)`.
- **Walks across the screen** read best in `side` view with `walk` driving the legs. `stroll()` gives `q`; override it with `view: 'side'` for a trot.
- **Facing right, `aL` is the near arm** (drawn in front of the body), and the far arm is behind and darker.

### Emotions

31 emotions. Each is a face, a colour and a way of moving, all locked to the beat. `feel(name, t, over)` returns all of it at time t:

```js
clawd(x, y, u, feel('happy', t));                                   // one emotion, alive
clawd(x, y, u, feel('sad', t, { view: 'q', lookX: -1 }));             // with overrides
clawd(x, y, u, emotions(t, [[0, 'sleepy'], [1.9, 'surprised', { lookX: .8 }], [2.5, 'idea']]));   // acted changes
```

| family | emotions |
|---|---|
| joy | happy, excited, laugh, love, proud, starstruck, playful, hopeful, relieved |
| sly | smug, cool, mischief, suspicious |
| low | sad, cry, bored, sleepy, ko |
| hot | angry, furious (the lunchbox lid opens), determined, disgusted |
| alarm | scared, nervous, surprised, confused, dizzy |
| mind | neutral, thinking, idea, shy |

- **`emotions(t, keys)`** is how moods change in a shot. Around each key it squints and squashes just before the change (anticipation), swaps the face under the squint, and fires a take sized to the new emotion. The body then settles into the new motion with overshoot, colour cross-fades and the new emote pops in.
  - `emotions(t, keys, { take: .5 })` scales every take.
  - The third element of a key overrides fields for that stretch (e.g. `{ lookX: .8, emote: 'music' }`).
- To make a new emotion, add an entry to `EMO` in clawd.js. It needs eyes, mouth, optional tint/blush/gloom/lid/emote, `take` (reaction size) and `body(t)` (its idle motion, locked to the beat through `_b(t)`).

### Parts

- **Eyes:** normal, look, wide, happy, closed, sleepy, wink, narrow, angry, determined, sad, teary, cry, squeeze, shine, scared, blank, spark, red, heart, x, swirl, dot, shades.
  - A pair gives mismatched eyes, e.g. `['narrow', 'wide']`.
  - `lookX`/`lookY` aim the pupils, and `squint` closes the eyes from any shape.
- **Mouths:** o, O, smile, grin, flat, wobble, cat, frown, smirk, laugh, open, wail, teeth, tongue, pout, yawn. Use `null` for none (Clawd's resting face).
- **Lunchbox lid:** `lid` 0..1 hinges the top of the body open, with teeth pointing into the mouth. It's for fury, chomping and shouting, in the front view only.
- **Hats:** party, hard, crown, halo, wizard, hood, top, fedora, band, sweatband, beanie, bow, flower, headphones, cat (ears and whiskers). Face pieces: masq, mask, bowtie.
- **Emotes** are painted marks that pop in by the head: `!` `?` `!!` `!?` zzz, sweat, spark, heart, hearts, anger, steam, bulb, dots, scribble, music, swirl, stars, cloud.
  - `emoteK` is the 0..1 pop and `emoteAge` drives the looping ones; `emotions()` sets both.
  - `emote(kind, x, y, s, k, age)` draws one anywhere, for example over a prop.
- **Body colour:**
  - `tint` shifts it with the mood: pale (fear), flush (anger), blue (sadness), rosy (love), green (disgust), gold (pride).
  - `gloom` adds a dark forehead with hanging lines, and `blush` adds cheeks (hatched when above .6).

### Hooks: props and accessories

- **`draw(u, sw)`** paints in body-local space, on top of everything else on the body (face, hat, near arm). It squashes, flips and rotates with Clawd. Front-view coordinates:
  - the body spans x −5u..5u and y −8u..−2u
  - the eyes are at (±2.5u, −6u)
  - the mouth is near (0, −4.3u)
- **`armL(u, sw)` / `armR(u, sw)`** are called at the arm tip, in arm space (+x runs outward along the arm), so a held prop just draws around (0, 0) and follows the arm automatically:

```js
clawd(x, y, 24, { ...feel('proud', t), aR: 1.2, armR: (u, sw) => paint(starPts(u * .8, 0, u * 1.4, .5, 5), { wash: '#FFE27A', sw }) });
```

- Anything the arms can't carry, like a big object overhead, is drawn separately at a point computed from the same pose. The demo's star does this. Make sure it touches: check it with a crop.

### Dances

`move(style, t, seed)` returns beat-locked pose offsets. The styles are bounce, hop, roof (arms up), sway, spin (a drawn spin through the key views once a bar), wave, walk, run, idle, stomp and shimmy. `mix` changes style every two bars. `dancer(x, y, u, style, t, extra)` is `clawd` + `move`. You can combine a dance with a face: `{ ...move('bounce', t), eyes: 'happy', mouth: 'grin' }`.

---

## Music (optional)

The kit doesn't need music, but it's built for it:

1. Set `bpm` to the song's tempo in [src/config.js](src/config.js), and set `offset` to the time of its first downbeat in seconds. Every idle, dance and `pulse()` then locks to the song.
2. Put the audio in `assets/` and set `PROJECT.audio` (or pass `--audio=`). `--clip` and `--encode` mux it in.
3. Land hits, cuts and takes on beats (`beatN`, `pulse`). Cut on bar lines for big changes, and give each musical phrase its own visual.
4. **Lyrics are not text.** Don't put words on screen. Act the meaning of a line instead.

## Common failures

These are the things that make a Clawd video look generated. Check your storyboard and sheets against them:

- signs, captions, labels or speech bubbles with words
- Clawd standing still and smiling while nothing happens
- everything moving at one brisk speed, with events stacked on top of each other and no holds
- moments that are over before the viewer understands them
- a tiny Clawd in a big empty landscape for the whole video
- faces that snap from one expression to another
- mechanical motion: linear moves, every part moving at once, both arms or several characters in sync
- timid poses and takes that barely read
- jittery linework: still things re-boiling every frame because something moving before them shifted the random stream (`boilSeed`)
- hard cuts everywhere, or a video that just starts and stops
- 3D rotation, perspective boxes or projected turns
- plain p5 shapes, gradients or digital glows mixed into the paint (use `paint`/`inkLine`/`glow`)
- muddy green-grey glows from painting yellow over blue
- props floating near a hand instead of touching it
- every shot a different world with nothing linking them

## About the demo

[src/scenes/demo.js](src/scenes/demo.js) ("The fallen star") exists to show the kit working: an acted emotion timeline, a drawn turn, a trot, a pickup, a throw on an arc, `glow`, a brush wipe and an iris in and out. **It's one idea, not a template.** Don't reuse its story, night sky, hills, star or shot structure. Start from the prompt and your own storyboard, and replace its script tag in `studio.html` with yours.

### Worked example: how the demo times its ending

This shows rule 4 applied to one shot of one video. The reads, the numbers and the way it ends are specific to this story; yours will be different. Read it for the reasoning, not the numbers. It's the demo's last shot, from the throw on, in video time:

| time | read | why it's timed this way |
|---|---|---|
| 6.95–7.1 | wind-up and throw | fast motion; it reads because the wind-up anticipates it |
| 7.1–7.9 | the star flies home | long enough for the eye to follow it from Clawd to the top of the frame; the camera eases back to give it sky |
| 7.9–8.35 | it arrives: a flare, a sparkle, the sky twinkles | the payoff. Clawd only watches, so nothing competes with it |
| 8.35–8.95 | Clawd falls in love | the reaction starts only after the viewer has seen the cause |
| 8.95–9.4 | Clawd waves goodbye | a new action, on its own |
| 9.4–9.8 | the star twinkles back | the answer to the wave |
| 9.8–11.0 | iris to Clawd, hold, shut | the last read gets time to land before the video ends |

The first version packed all of this into about 1.3 s, and nobody could tell what had happened.

<!-- ===== /file: painted-animation/template/ANIMATION_GUIDE.md ===== -->

<!-- ===== file: painted-animation/template/README.md ===== -->

# Claude Animation Base

This is a small starter kit with code, instructions and assets for animating a character in [p5.js](https://p5js.org) and [p5.brush](https://github.com/acamposuribe/p5.brush) with Claude Opus 5.5. It's based on the code from the music video [I'm Upping My P(doom)](https://github.com/JohnHeibel/PDoomVideo) and an analysis of what the model did and didn't do well. I highly recommend playing around with your prompting: make it give you the storyboard before coding, give it very broad instructions, try being very specific, ask for subagents, and try a bunch of other fun ways of testing the model's capabilities. In my testing, it can do a lot with very little, but it's also quite accurate when you give it more requirements. Also try asking the model to swap out the character or make new emotions or costumes, give it your own reference images, and try many other fun things like that. I've found that the reasoning level corresponds to how "extravagant" and detail-oriented the model makes the scene. All test videos were generated with Opus 5.5 on xhigh reasoning in Claude Code.

![Clawd's emotions, animated](docs/emotions.webp)

## Make a video

Clone it, open it in Claude Code (or any coding agent) and ask for what you want:

> Read ANIMATION_GUIDE.md, then make a 15-second video of Clawd trying to catch a butterfly.

The model storyboards first, builds shot by shot, renders contact sheets to check its own work, and writes `out/video.mp4`. [ANIMATION_GUIDE.md](ANIMATION_GUIDE.md) holds the rules it follows: handmade, alive, one piece, no text, transitions always, something happens in every scene, and a solid medium of brush strokes, flat 2D and boiling linework. It also covers timing for the viewer and the core principles of character animation.

## Run it yourself

You need Node.js, Google Chrome and ffmpeg.

Without a dedicated GPU, p5.brush's watercolour fills make render times fairly slow, measured in seconds per frame. If you're running on integrated graphics, I recommend asking the model to avoid those fills and replace them with something else appropriate. (I love the look of the watercolours, though.)

```bash
npm install
node render.mjs --clip --out=out/video.mp4
```

That renders the 11-second demo in [src/scenes/demo.js](src/scenes/demo.js). Open [studio.html](studio.html) in Chrome to scrub through it. Add `?loop=emotions` or `?loop=views` to see the model sheets. If Chrome isn't in a standard location, pass `--chrome=<path>` or set `CHROME_PATH`.

On Linux, `render.mjs` starts Chrome with `--no-sandbox` (Ubuntu 23.10+ blocks Chrome's sandbox in headless use) and also finds a Chromium installed by Playwright. With no GPU at all, add `--soft-gl` to render WebGL in software: slow on watercolour fills, but it works. On a headless Linux machine with an NVIDIA GPU (a cloud or cluster node), add `--gpu-angle=gl-egl` (or `vulkan`); `node gpu_probe.mjs <chrome path>` shows which renderer each set of flags gets.

## What's here

| path | what it is |
|---|---|
| [ANIMATION_GUIDE.md](ANIMATION_GUIDE.md) | The rules, the workflow and the full API. Read it first. |
| [src/clawd.js](src/clawd.js) | Clawd: views, emotions, eyes, mouths, hats, emotes, dances |
| [src/core.js](src/core.js) | Painting, timing, motion helpers, camera, light, paper |
| [src/timeline.js](src/timeline.js) | Shots, loops and the brush-wipe transition |
| [src/config.js](src/config.js) | Length and tempo |
| [src/scenes/](src/scenes/) | Your video goes here (the demo is an example) |
| [render.mjs](render.mjs) | Headless renderer: contact sheets, frame strips, crops, stills, MP4 |
| [docs/](docs/) | Model sheets: [emotions](docs/emotions.jpg) (also [animated](docs/emotions.webp)) and [views, motion and hats](docs/views.jpg) |

<!-- ===== /file: painted-animation/template/README.md ===== -->
