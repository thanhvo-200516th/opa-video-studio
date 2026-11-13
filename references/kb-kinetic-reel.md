# kb-kinetic-reel — toàn văn tài liệu của nguồn `kinetic-reel`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/kinetic-reel/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: kinetic-reel/SKILL.md ===== -->

---
name: kinetic-reel
description: >-
  Make kinetic-typography motion reels (MP4) in code: showreels, portfolio or work reels, product promos, intro films, "motion design"-style videos with bold condensed type, HUD micro-type, black/cream/lime palette, three.js generative layers (particle terrain, liquid marble, chrome knot, particle clouds), shape-continuity transitions and a synthesized, beat-locked score. Canvas 2D + WebGL rendered frame by frame in headless Chrome, encoded with ffmpeg. Use when the user asks for a reel, showreel, motion-graphics / kinetic-type video, a "Work Reel" in this style, or to extend/re-cut the Work Reel ’26.
---

# Kinetic reel

A method for making editorial, high-energy motion reels entirely in code, distilled from "Work Reel ’26" (an 84 s
portfolio reel: Microsoft → UW–Madison Surgery → Enterprise RAG → trace finale). It's bundled as a runnable
`template/` (a 17 s demo that uses every technique) and a full worked example in `examples/work-reel-26/`.

**How it works.** Every frame is a pure function of `t`. `reel/index.html` loads `reel/cues.js` (the timeline) and
`reel/reel.js` (an ES module: three.js layers, a 2D type canvas and a WebGL post pass). `render.mjs` drives headless
Chrome to render contact sheets, strips and stills for review, or every frame in parallel, and ffmpeg encodes the MP4.
`music/score.mjs` synthesizes the score in Node from the same `cues.js`, so every hit lands on its frame.

## Workflow

### 0. Scaffold
```bash
bash ~/.claude/skills/kinetic-reel/scripts/new_project.sh <project-dir>
```
Then read [references/style-guide.md](references/style-guide.md) (the look, the motion vocabulary, the transition
catalogue, layout rules) and [references/sound.md](references/sound.md) in full before designing. Skim
`examples/work-reel-26/reel.js` for how a long reel is organised.

### 1. Decide the emphasis, then storyboard
- Ask (or settle) **what leads and how much time each part gets**. Viewers notice proportions: v2 of the Work Reel had
  Microsoft at ~60% and had to be rebalanced. The fix was to *add* runtime for the other chapters rather than cut the
  one people loved. Aim for the lead ≈ 35–40%.
- Write `STORYBOARD.md` from the template: time budget, the source of truth for facts, a unifying device, and one row
  per shot (headline, visual mechanism, transition in, sound).
- **Facts are sacred.** Only figures from the provided source, each with its scope ("~180 self-built cases",
  "320 bilingual prompts"). Anything illustrative (tool IDs, doc IDs, example answers, an AST) is labelled
  `SCHEMATIC` in the HUD. Never draw per-dimension data you don't have. Visualise the *process*. Medical/clinical
  work: no efficacy claims, say "in development / not yet validated" when true.

### 2. Build
- `reel/cues.js`: `S` (scene starts), `hits` (every beat that matters), `CH` (chapters → the segmented progress bar),
  `dur`. 120 BPM: cuts on beats, chapter changes on bars.
- `reel/reel.js`: one function per shot, `sName(t)`. Each paints the whole frame: `bg()` → GL layer via
  `glShot(...)` → type and shapes → `hud(t, {...})`. Register the shot in `SCENES` with a key; add a transition into it
  in `TR` (or leave it out for a hard cut on the beat).
- Keep the `CJK` constant listing every Chinese character you draw (fonts load as a subset).

### 3. Look at it, every shot, several times
```bash
node render.mjs --sheet=1,4,7,10,13,15.5 --cols=3 --w=640 --out=out/check/sheet.jpg   # key frames
node render.mjs --stills=10.4 --out=out/stills                                          # full-res detail
ffmpeg -ss 16.0 -t .6 -i out/reel.mp4 -vf "fps=10,scale=320:-1,tile=6x1" out/check/tr.jpg   # a transition, from the encode
```
Open every image with Read. Check for collisions (labels over lines, stats over stats, text into HUD bands), empty
frames on a cut, legibility at 1600 px wide, and that each transition *starts on something* and lands cleanly.
Budget: a sheet per chapter, a full-res still per dense shot, a strip per transition type.

### 4. Score, render, encode
```bash
node music/score.mjs && ffmpeg -y -i music/score.wav -af "highpass=f=30,equalizer=f=250:t=q:w=1:g=-2,loudnorm=I=-14:TP=-1.2:LRA=8" -c:a aac -b:a 192k assets/score.m4a
node render.mjs --frames --workers=4                                    # ~8–40 ms/frame on a Mac GPU: seconds, not minutes
node render.mjs --encode --audio=assets/score.m4a --out=out/reel.mp4 --fps=30
# web copy: ffmpeg -i out/reel.mp4 -vf scale=1600:900:flags=lanczos -c:v libx264 -preset slow -crf 23 -c:a aac -b:a 128k -movflags +faststart out/reel-web.mp4
```
You can't hear the score: check it with `showspectrumpic` and per-section RMS, and say so when you report. Audio-only
changes don't need a re-render: remux (`-map 0:v -map 1:a -c:v copy`).

## The rules that matter most
1. **Type is the hero.** Condensed display (Anton) for headlines, one wide grotesk (Archivo Black) for slams, italic
   serif (Instrument Serif) for the one "voice" line, mono (JetBrains Mono) for every label. Big English headlines,
   small Chinese annotations when the audience is bilingual.
2. **Every shot has a mechanism**, not just words: a grid routing, a matrix scanning, a token hopping a state machine,
   lists fusing, packets passing gates. The headline names it; the mechanism proves it.
3. **Beat-locked.** Letters, chips, counters and cuts sit on `hits`. Fast in (expo-out), hold, next.
4. **Continuity.** Prefer shape-continuity transitions (zoom through the element the eye is on, iris from the thing
   that just lit up) to hard cuts inside a chapter. Hard cuts + an impact are for chapter slams.
5. **No noise whooshes.** In-key swells into chapters, quiet tonal cues inside them, silence on about half the cuts.
6. **Honest data** (see step 1) and a `SCHEMATIC` label on anything illustrative.
7. **Guard the math.** Radii from `backOut()` can dip below 0 (canvas throws): `circle`/`starburst`/`jelly` already guard.
   In the synth, clamp local time to ≥ 0 before `pow()` and clamp SVF `f`/`q` (both already in the template).

## Shipping a reel as a site intro
The Work Reel ships as its site's entry page: `index.html` plays the reel full-screen and hands off to the portfolio.
The pattern is bundled in [examples/site-intro/](examples/site-intro/) (`index.html`, `css/intro-reel.css`,
`js/intro-reel.js`, plus a Cloudflare Worker that adds HTTP Range support):
- Try to autoplay with sound. If refused, play muted with a pulsing "tap for sound". If that is refused too, or
  `prefers-reduced-motion`, show the end screen in "start" mode (play is the lead button).
- During playback: small glass pills at top centre, since the reel's HUD owns the corners. "Skip intro" carries a
  ring that fills with the reel. A sound toggle's equalizer bars pulse at the reel's BPM. Esc skips, M mutes.
- End screen: the reel's grammar in HTML. Corner brackets, the name as drop-in letters (Anton), mono micro-type,
  a segmented trace bar, a 2D dot-field version of the particle terrain, a lime primary CTA (text roll on hover,
  sheen, magnetic, a pulse every bar), and a ghost "watch again".
- Leave through a lime iris from the pressed control, duck the audio, then navigate.
- Two encodes (1600×900 at ~1.3 Mbps, 960×540 at ~0.6 Mbps for phones / save-data), `preload="auto"`, a poster.
  Serve them with HTTP Range (206), or seeking and Safari break.

<!-- craft-handoff:start -->
## Mở và sửa tiếp trong FilmCraft / EffectCraft

Khi user muốn sửa tiếp trong FilmCraft hoặc EffectCraft, không giao một MP4 phẳng: viết timeline spec rồi dùng skill `craft-handoff` dựng project gốc (`.fcproj` / `.ecproj`) có đủ track, clip, keyframe, chữ, effect và SFX. Với skill này: mỗi cảnh một clip (nền trong suốt nếu phủ lên nền khác); tiêu đề ít chuyển động → text clip gốc; cần chỉnh chuyển động từng ký tự → EffectCraft qua `ae-script-builder`. Chi tiết: `craft-handoff/references/skills-map.md`.
<!-- craft-handoff:end -->

<!-- ===== /file: kinetic-reel/SKILL.md ===== -->

<!-- ===== file: kinetic-reel/README.md ===== -->

<div align="center">

# kinetic-reel

<a href="README.md"><img src="https://img.shields.io/badge/English-0E0F0E?style=for-the-badge" alt="English"></a>
<a href="README.zh-CN.md"><img src="https://img.shields.io/badge/简体中文-DDF53D?style=for-the-badge" alt="简体中文"></a>

A Claude Code skill for producing kinetic-typography motion reels with Claude Opus 5.5.
Part of [opus-video-skills](../../README.md).

</div>

![Work Reel ’26](docs/work-reel-sheet.jpg)

## Overview

The skill enables Claude Opus 5.5 to produce editorial, high-energy motion reels of the kind used for portfolios, showreels and product introductions. It covers the time budget, storyboarding, typographic animation, generative backgrounds, transitions, a synthesized score and the final encode. All imagery and all music are generated in code.

## How It Works

1. **Time budget and storyboard.** Claude decides which part leads and what share of the runtime each part receives. It then writes a shot list with a headline, a visual mechanism, a transition and a sound for every shot.
2. **Drawing.** Each shot is a JavaScript function that paints the complete frame: a 2D canvas for type and diagrams, three.js layers for generative backgrounds, and a WebGL post pass for RGB split, slice glitch and grain. Every frame is a pure function of time.
3. **Review.** Contact sheets, full-resolution stills and transition strips are rendered in headless Chrome. Claude inspects them for collisions, legibility and clean transitions, and revises the code.
4. **Score.** A small synthesizer in Node reads the same timeline as the picture and writes the music: drums, bass, arpeggios, pads, and in-key cues for every hit and transition.
5. **Output.** Frames are rendered in parallel (typically 8–40 ms per frame on a Mac GPU) and encoded to MP4 with ffmpeg.

## Characteristics

- **Type-led design.** Condensed display type for headlines, a wide grotesk for slams, an italic serif for a single voice line, and monospaced micro-type for labels, arranged on a fixed HUD grid.
- **A mechanism in every shot.** Each claim is illustrated by a working diagram: a tool grid that routes, an evaluation matrix that scans, a token that moves through a state machine, ranked lists that fuse, answers that pass through safety gates.
- **Shape-continuity transitions.** Zoom through the element in focus, iris from a highlighted node, wipe, slats, pixel grid and push. Each is 0.45–0.6 s and they are varied throughout.
- **Beat-locked picture and sound.** The picture and the score read one timeline at 120 BPM, so letters, counters and cuts land on beats. Transitions use in-key cues instead of repeated noise sweeps.
- **Sourced figures.** On-screen numbers come only from the provided source and carry their evaluation scope. Illustrative content is labelled SCHEMATIC.

## Example: Work Reel ’26

<p align="center"><img src="docs/work-reel.gif" width="640" alt="Work Reel ’26"></p>

An 84-second portfolio reel for an AI engineer. The time budget follows the order of emphasis: 30 seconds for an internship at Microsoft Cloud & AI (tool-calling evaluation, constrained decoding, a ReAct agent, a planner–reviewer multi-agent system, an incident-response pipeline, reliability), 18 seconds for clinical AI research at the UW–Madison Department of Surgery, and 14 seconds for an enterprise RAG system. It ends with the whole reel laid out as an agent trace. The reel also ships as the entry page of the author's website, with skip, sound, replay and enter controls in the same visual language.

The source is in [examples/work-reel-26](examples/work-reel-26/), and the entry page in [examples/site-intro](examples/site-intro/).

## Requirements

- Claude Code with Claude Opus 5.5
- Node.js, Google Chrome, ffmpeg

## Installation

See the [collection README](../../README.md#installation). As a plugin:

```
/plugin marketplace add tuzhechen2005/opus-video-skills
/plugin install kinetic-reel@opus-video-skills
```

## Usage

Describe the reel in Claude Code, for example:

> Make a 60-second kinetic-type reel of my three projects from this résumé. The first project should lead.

The skill can also be invoked directly with `/kinetic-reel`. It scaffolds a project from `template/` (a 17-second demo that uses every technique), presents a storyboard, builds and reviews each shot, synthesizes the score and writes `out/reel.mp4`.

## Directory Structure

| Path | Description |
|---|---|
| `SKILL.md` | Workflow and rules followed by Claude |
| `template/` | Engine and demo reel: `reel/reel.js`, `reel/cues.js`, `music/score.mjs`, `render.mjs` |
| `scripts/new_project.sh` | Project scaffolding and toolchain check |
| `references/style-guide.md` | Palette, typography, layout grid, motion helpers, GL layers, transition catalogue |
| `references/sound.md` | Synthesizer, transition sound rules, arrangement, known pitfalls |
| `examples/work-reel-26/` | Full source of the 84-second example |
| `examples/site-intro/` | The reel as a website entry page, with a Cloudflare Worker for HTTP Range |

## License

MIT. The renderer is derived from [ClaudeAnimationBase](https://github.com/JohnHeibel/ClaudeAnimationBase) by John Heibel (MIT). See the repository [LICENSE](../../LICENSE).

<!-- ===== /file: kinetic-reel/README.md ===== -->

<!-- ===== file: kinetic-reel/README.zh-CN.md ===== -->

<div align="center">

# kinetic-reel

<a href="README.md"><img src="https://img.shields.io/badge/English-0E0F0E?style=for-the-badge" alt="English"></a>
<a href="README.zh-CN.md"><img src="https://img.shields.io/badge/简体中文-DDF53D?style=for-the-badge" alt="简体中文"></a>

基于 Claude Opus 5.5 的动态排版短片制作技能（Claude Code Skill）。
属于 [opus-video-skills](../../README.zh-CN.md) 合集。

</div>

![Work Reel ’26](docs/work-reel-sheet.jpg)

## 概述

本技能使 Claude Opus 5.5 能够制作节奏紧凑、以排版为主的动态短片，适用于作品集、Showreel 和产品介绍。它涵盖时间分配、分镜、排版动画、生成式背景、转场、合成配乐与最终编码。所有画面和音乐均由代码生成。

## 技术原理

1. **时间分配与分镜。** Claude 先确定以哪部分为主，以及各部分分别占多少时长；再编写镜头表，为每个镜头确定大标题、视觉机制、转场与音效。
2. **绘制。** 每个镜头是一个 JavaScript 函数，负责绘制完整画面：二维画布绘制文字与图示，three.js 图层生成背景，WebGL 后期处理负责 RGB 分离、切片故障和颗粒感。每一帧都由时间唯一确定。
3. **审查。** 在无头 Chrome 中渲染关键帧拼图、全分辨率单帧和转场序列。Claude 检查元素重叠、可读性与转场是否干净，并据此修改代码。
4. **配乐。** Node 编写的小型合成器读取与画面相同的时间轴生成配乐，包括鼓、贝斯、琶音、铺底，以及为每个动作点与转场准备的同调音效。
5. **输出。** 各帧并行渲染（在 Mac GPU 上通常每帧 8–40 毫秒），由 ffmpeg 编码为 MP4。

## 主要特性

- **以排版为主导。** 大标题用窄体展示字体，重击词用宽体无衬线，全片唯一的「旁白」句用斜体衬线，标注用等宽小字，统一排布在固定的 HUD 网格上。
- **每个镜头都有机制。** 每一项论点都有一张可运转的示意图来说明，例如负责路由的工具网格、逐行扫描的评测矩阵、在状态机中跳转的标记、相互融合的排名列表、依次通过安全闸门的回答。
- **形状连贯的转场。** 从视线所在的元素钻入、从高亮节点圆形展开、擦除、百叶窗、像素格溶解和推移。每次转场 0.45–0.6 秒，全片交替使用。
- **画面与声音按节拍锁定。** 画面与配乐读取同一条 120 BPM 的时间轴，文字、计数器与切镜都落在节拍上。转场使用同调乐音，不用重复的噪声扫频。
- **数据有出处。** 画面中的数字只取自提供的资料，并注明评测口径；示意性内容一律标注 SCHEMATIC。

## 示例：Work Reel ’26

<p align="center"><img src="docs/work-reel.gif" width="640" alt="Work Reel ’26"></p>

一位 AI 工程师的 84 秒作品集短片，时长按重点依次分配：
- **30 秒：微软 Cloud & AI 实习。** 包括工具调用评测、约束解码、ReAct 智能体、规划—审查多智能体、事件响应管道与可靠性保障。
- **18 秒：UW–Madison 外科系的临床 AI 研究。**
- **14 秒：企业级 RAG 系统。**

片尾把整支短片展开成一次 Agent 运行的 trace。这支短片同时是作者个人网站的入口页，页面上的跳过、声音、重播与进入按钮沿用同一套视觉语言。

源码见 [examples/work-reel-26](examples/work-reel-26/)，入口页见 [examples/site-intro](examples/site-intro/)。

## 环境要求

- Claude Code 及 Claude Opus 5.5
- Node.js、Google Chrome、ffmpeg

## 安装

参见[合集说明](../../README.zh-CN.md#安装)。以插件方式安装：

```
/plugin marketplace add tuzhechen2005/opus-video-skills
/plugin install kinetic-reel@opus-video-skills
```

## 使用方法

在 Claude Code 中描述所需短片，例如：

> 根据这份简历，把我的三个项目做成一支 60 秒的动态排版短片，以第一个项目为主。

也可通过 `/kinetic-reel` 直接调用。技能会基于 `template/`（一支用到全部技巧的 17 秒演示片）创建项目、提交分镜、逐个镜头制作并审查，合成配乐后输出 `out/reel.mp4`。

## 目录结构

| 路径 | 说明 |
|---|---|
| `SKILL.md` | Claude 遵循的工作流程与规则 |
| `template/` | 引擎与演示片：`reel/reel.js`、`reel/cues.js`、`music/score.mjs`、`render.mjs` |
| `scripts/new_project.sh` | 项目初始化与环境检查 |
| `references/style-guide.md` | 色板、字体、版式网格、动效函数、GL 图层与转场目录 |
| `references/sound.md` | 合成器、转场音效规则、编曲方法与已知问题 |
| `examples/work-reel-26/` | 84 秒示例的完整源码 |
| `examples/site-intro/` | 把短片做成网站入口页的实现，附带支持 HTTP Range 的 Cloudflare Worker |

## 许可协议

MIT。渲染器改编自 John Heibel 的 [ClaudeAnimationBase](https://github.com/JohnHeibel/ClaudeAnimationBase)（MIT 协议），详见仓库的 [LICENSE](../../LICENSE)。

<!-- ===== /file: kinetic-reel/README.zh-CN.md ===== -->

<!-- ===== file: kinetic-reel/examples/site-intro/README.md ===== -->

# Example: a reel as a site's entry page

How the Work Reel ’26 ships on its portfolio: the reel plays full-screen, then the end screen offers
"Enter the site" and "Watch again".

| File | What it does |
|---|---|
| `index.html` | The page: `<video>`, skip + sound pills, the end screen, the exit iris |
| `css/intro-reel.css` | The reel's look in CSS: ink / cream / lime, Anton + JetBrains Mono, HUD corners, beat-timed motion |
| `js/intro-reel.js` | Autoplay with sound, then muted, then a "start" screen. It also handles skip / Esc / M, replay, the magnetic CTAs, a 2D dot-field background and the iris exit |
| `worker.js` | A Cloudflare Worker that answers Range requests with 206. Workers static assets return the whole file, which breaks seeking and Safari playback. Route only the video path through it with `assets.run_worker_first` |

To adapt it, change the video paths in `intro-reel.js` (`v.src`), the name, role and links in `index.html`, and
`HOME` in `intro-reel.js`. Self-host Anton and JetBrains Mono (both SIL OFL, from Google Fonts) under `fonts/`,
or change the `@font-face` rules. Encode two sizes (for example 1600×900 at ~1.3 Mbps and 960×540 at ~0.6 Mbps)
and pass `-movflags +faststart`.

<!-- ===== /file: kinetic-reel/examples/site-intro/README.md ===== -->

<!-- ===== file: kinetic-reel/examples/work-reel-26/README.md ===== -->

# Worked example: Work Reel ’26 (v3.1, 84 s)

The full source of the reel this skill was distilled from: a portfolio reel for an AI engineer, in three chapters
(Microsoft Cloud & AI → UW–Madison Department of Surgery → Enterprise RAG) and a trace finale. The files are as
they ran in the original project:

- `reel.js`: all scenes (intro, index, 10 Microsoft shots, 5 Surgery shots, 5 RAG shots, trace, end), the
  transition map `TR` and `SCENES`. It imports three.js from `../../site/vendor/three/three.module.js`. When you
  copy it into a scaffolded project, change that import to `../node_modules/three/build/three.module.js`.
- `cues.js`: the 84 s timeline (`S`, `hits`, `CH`).
- `score.mjs`: the score. It requires `../kinetic/cues.js`; point it at `../reel/cues.js`.
- `STORYBOARD.md`: the v3 structure and v1's original storyboard.

Read it for how to pace a long reel and budget chapter emphasis. It also shows the trace finale,
`cloud.project()` wiring 2D retrieval lines to 3D points, RRF computed for real in `FUSED`, and the choice of
transition inside each chapter.

All figures on screen come from the author's résumé. Use your own sourced figures. Never reuse these.

<!-- ===== /file: kinetic-reel/examples/work-reel-26/README.md ===== -->

<!-- ===== file: kinetic-reel/examples/work-reel-26/STORYBOARD.md ===== -->

# Work Reel ’26 · 动态排版版

**当前版本 v3**：84 s，16:9，30 fps，120 BPM。v1（42 s）和 v2（52 s，微软约占 60%）的源码存档在 `kinetic/v1/`、`kinetic/v2/`，
对应视频是 `out/kinetic-v1*.mp4` 和 `out/kinetic-v2*.mp4`。

## v3 结构（按重点排序：微软 → UW 外科系 → 企业 RAG）

| 时间 | 段落 | 画面 |
|---|---|---|
| 0–10 | 开场 | 同 v1：BOOT → EVERY ANSWER NEEDS EVIDENCE → 名字 |
| 10–12 | 目录 | 01 微软 / 02 UW–Madison 外科系 / 03 企业 RAG，各带角色和时长；镜头从「01」钻进下一镜 |
| 12–42 | **01 微软**（30 s） | 标题 → 24 个工具格 → 6 维评测矩阵 → 约束解码 → 61%→87% → ReAct 状态机 → AutoGen 规划/审查 → 事件管道 → FAIL SAFE → 回顾胶带 |
| 42–60 | **02 UW–Madison 外科系**（18 s） | DEPARTMENT OF SURGERY（字母里填流体纹理）+ 粒子聚合成甲状腺 + **AI RESEARCHER** → 病历切块进入向量星团，查询检索 top-k → 每句话都有出处 → 四道安全闸门（一个答案被拒答并转交医生）→ *Cite it — or abstain.* |
| 60–74 | **03 企业 RAG**（14 s） | 标题配铬金属扭结 → BM25 与稠密两路召回、RRF 融合（按真实 RRF 公式排序）+ 级联重排漏斗 → DistilBERT 意图路由加 LLM 兜底 → SQL AST 守卫拦截 DROP → 高并发指标 |
| 74–78 | Trace | 整支片展开成一次 Agent 运行的 span 瀑布图，STATUS OK |
| 78–84 | 片尾 | 名字、水母标志、联系方式 → 故障效果 → 收成一个点 |

**v3 新增的手法**：镜头之间不硬切，改用形状连贯的转场，包括钻进被选中的 UI 元素、圆形放大、扫描线擦除、百叶窗、像素格溶解、推移。
底部进度条按章节分段，整支片就是一条 trace。三维粒子云从灰尘聚合成甲状腺，再散开成向量空间，检索线接到按三维投影算出的真实点上。

---

## v1 原始分镜（42 s，供参考）

参考风格：一段动态排版参考片（未收录）。粗体窄字号大标题加 HUD 式小字标注；配色是黑、米白、荧光青柠，点缀电光蓝和信号红；
配合生成式画面（粒子地形、流体大理石纹、铬金属扭结、方框隧道、数据柱）和卡拍转场（斜切、切片、RGB 分离）。
纸海里的 Jelly 在这里简化成一个几何水母标志，顶替参考片里星芒的位置。

**文字规则**：大字用英文，小字标注里夹少量中文。所有数字都来自简历和网站原文，附带口径说明（测试集、样本量）。
医疗相关只写「决策支持」「研发中、尚未进行患者端验证」。

**节拍**：120 BPM，一拍 0.5 s，一小节 2 s，每次切镜都卡在拍点上。配乐是 `music/score_kinetic.mjs`，读取 `kinetic/cues.js`。

| 时间 | 段落 | 画面 |
|---|---|---|
| 0–4 | BOOT | 黑底，HUD 四角括号画出，时间码开始走；粒子地形升起 → 2.0 中心亮起青柠圆点，卡拍跳动 → 3.0 展开成水母标志 → 闪白 |
| 4–6 | EVERY / ANSWER | 巨大的 EVERY 加上下描边叠字滚动 → 5.0 翻转成 ANSWER |
| 6–7 | needs | 米白底，细圆圈画出，衬线斜体 *needs*，一个红点 |
| 7–8 | EVIDENCE | 电光蓝满屏，EVIDENCE 带动态模糊砸进来；中文小字「每个回答，都需要依据」；切片故障出场 |
| 8–10 | 名片 | ZHECHEN TU. 从描边到实心，RGB 故障入场；AI APPLICATION · AGENT ENGINEER，涂喆宸，衬线副标 |
| 10–13 | 01 企业 RAG | 米白底，ROUTE. / RETRIEVE. / RERANK. 逐字母落下；青柠圆里的水母标志；每行配一个技术标签 |
| 13–16 | 01 数据 | 黑底，流体纹理填充的柱状图加红色曲线；计数器滚到 093%（路由准确率），然后 +18% Recall@10；S 曲线面板 → 斜切转场 |
| 16–19 | 02 多智能体 | 旋转的青柠/白色方框隧道，中心圆内写 FIVE / AGENTS / ONE CASE，五个角色标签卡拍绕圆出现 |
| 19–20 | 02 红旗 | 信号红满屏 RED FLAG，画面震动，写明「转交医生」 |
| 20–22 | 02 指标 | 96%+ 急症召回率，配三个小指标；口径：约 180 条自建用例，决策支持、不做诊断 |
| 22–25 | 03 微软 | 青柠底 CALL / THE RIGHT / TOOL，右侧铬金属扭结旋转；24 个 Azure REST 工具 |
| 25–28 | 03 指标 | 61% → 87% 像里程表一样翻滚（Phi-3 完整调用准确率，320 条双语评测） |
| 28–30 | 04 甲状腺 | 流体大理石纹满屏，衬线斜体 *Cite it — or abstain.* 逐词出现 → 竖条切片 |
| 30–32 | 04 信息 | 米白底 CLINICAL RAG 大字；右列逐条打勾：主导 AI 工程师、6.9 万美元资助、两位 PI、依据生成、安全评测 |
| 32–36 | 04 胶带 | 两条斜向胶带反向滚动：TRACEABLE ✳ GROUNDED ✳ SAFE / CITE ↗ SOURCE ↗ ABSTAIN；巨大的描边 04；底部小字「研发中，尚未进行患者端验证」 |
| 36–42 | 片尾 | ZHECHEN / TU 字母升起，青柠水母标志旋转，圆形进度环；邮箱和 GitHub → 40.5 RGB 故障 → 收成一个点 → 黑场。片尾只用英文 |

<!-- ===== /file: kinetic-reel/examples/work-reel-26/STORYBOARD.md ===== -->

<!-- ===== file: kinetic-reel/references/sound.md ===== -->

# Sound: the synthesized, beat-locked score

`music/score.mjs` is a small offline synth in Node (no samples, no dependencies). It reads `reel/cues.js`, places
every sound in time with `put(t0, len, gen(tt), {gain, pan, rev, bus})`, and writes `music/score.wav`.
There are two buses. `drum` stays dry. `mus` is ducked by the kick (sidechain): each `kick()` writes into `duck[]`.
A Freeverb send, tanh glue and normalization follow; loudnorm (−14 LUFS) runs in ffmpeg.

## Instruments
`kick`, `clap`, `hat(open?)`, `tick` · `bass` (saw/square through tanh) · `pluck` · `pad` (detuned, slow swell) ·
`stab` (chord hit) · `blip` (in-key sine ping) · `odo` (a burst of ticks for a rolling counter) · `glitch`
(square-wave crumbs) · `impact` (kick + low-passed noise tail + sub drop) · `softImpact` (no noise tail) ·
`riser` (tonal sweep with a little low-passed noise).

## Transition sounds (a hard rule, learned from feedback)
**No noise whooshes on transitions.** v3 fired 29 in 84 s; it was "cool at first, then annoying". Use:
- `swell(tEnd, chordNotes, len)`: a reversed pad that grows and stops dead on a chapter cut. Match the chord.
- `bloom(t, notes)`: a soft bell chord, for iris transitions.
- `glide(t, len, m0, m1)`: a quiet triangle glide up, for a zoom-through.
- `harp(t, span, notes, v, dir)`: a quick pluck run, for slats (vary the direction).
- `hatRoll(t)`: 3–4 rising hats, for wipes.
- **nothing**, for about half the cuts: the downbeat and the next shot's own entrance sounds (tile ticks, scan blips,
  typing) carry them.
Never use the same cue twice in a row. Keep `impact()` (with its noise tail) for about five structural moments. Use
`softImpact()` for other slams.

## Arrangement
- A groove loop runs over the reel: 4-on-the-floor kick, claps on 2 and 4, 8th hats (16ths for the lead chapter),
  a two-note bass per beat, a pluck arpeggio, and a pad per bar. Chords: Am F C G.
- Give chapters different energy. A serious chapter goes half-time: kick on beat 1, soft clap on 3, a *decaying* sine
  sub (not a sustained drone). Aim for about 5 dB RMS lower than the lead chapter. Check with per-section RMS.
- Take the drums out under a glitch exit. Leave a breath (kick only) on a quiet word.
- Tie hits to the picture: ticks per letter/tile/row, blips on chips and nodes, `odo` under counters, a stab when a
  number lands, a low buzz on a rejection, a bell per retrieved item.

## Gotchas (both cost real time)
- `t0 * SR` isn't an integer, so the first sample's local time can be −1e−16, and `Math.pow(negative, 2.2)` is NaN,
  which silences the whole mix after normalization. `put()` clamps `tt >= 0`. Keep it.
- The state-variable filter in `noise()` explodes near `f = 1`: `f` is clamped to .85 and `q` to ≥ .45. Keep it.
- You can't listen. Verify with `ffmpeg -lavfi showspectrumpic`, per-section RMS, and a count of the calls you
  meant to remove (e.g. `grep -c "whoosh("`). Tell the user you couldn't hear it.

<!-- ===== /file: kinetic-reel/references/sound.md ===== -->

<!-- ===== file: kinetic-reel/references/style-guide.md ===== -->

# Style guide: the Work Reel look

## Palette (`K` in reel.js)
| token | hex | use |
|---|---|---|
| `ink` | `#0E0F0E` | default dark ground, type on light grounds |
| `ink2` | `#171917` | nodes/cards on ink |
| `cream` | `#F1EEE6` | light ground, type on dark |
| `lime` | `#DDF53D` | THE accent: the lead chapter, the chosen item, the "OK" state, the mark |
| `blue` | `#2F3CFF` | second ground (one slam per reel, one full-bleed scene), secondary emphasis on cream |
| `red` | `#E8412F` | danger/rejection only (a red flag, a blocked query, a failed gate) and the full stop in a headline |
| `grey`/`mid` | `#8B908A` / `#5E625D` | dimmed type |
Rotate grounds between shots (ink → lime → ink → cream → blue …) so every cut is a visible change. A darker
`#0B0D0C` ground marks a more serious chapter.

## Typography (`F` in reel.js)
- Headlines: `font(F.cond, 130–330)`, one or two lines, ending in a full stop. Colour the key word (lime on dark, blue
  on cream) or just the full stop (red).
- Slams: `font(F.wide, 172–250)` (Archivo Black) for one-word statements (EVERY / ANSWER / EVIDENCE), with outlined
  echoes stacked above and below.
- Voice line: `italic 124px ${F.serif}` over the liquid layer, word by word on beats.
- Labels, HUD, chips, tables: `font(F.mono, 14–26, 700)` with 2–8 px letter-spacing. Chinese: `font(F.zh, 20–34, 500)`
  with 4–14 px spacing.
- Numbers: `F.cond` at 84–420 px. Counters roll (`count()` expo) or flip (`odometer()`).

## Layout
- Canvas 1920×1080. Left margin **140**, right edge **1780**. Headline baselines around y 250–470.
- The HUD owns the four corners: brackets at 40 px, micro-type at (58, 63) / (1862, 63) / (58, 1022) / (1862, 1022),
  one optional Chinese line at y ≈ 988 (left or right), the segmented progress bar at y 1050. Keep content out of
  y > 950.
- Put stats in a row at y ≈ 900 or stacked in a right column at x ≈ 1400–1540. Never two stats in the same 300 px
  horizontal band at the same height: they collide. Check with a full-res still.

## Motion vocabulary (all in reel.js)
| helper | what it does |
|---|---|
| `dropWord(s, x, y, font, t0, t, {fall, stag, fillAt})` | letters fall in with expo-out and a stagger; `fillAt(i)` recolours one letter |
| `letters(s, x, y, o, fn)` | per-letter transform (dy, r, s, a, fill): build your own entrances |
| `chip(s, x, y, {k, bg, fg})` | a label that wipes in; returns its width so chips can be laid out in a row |
| `stat(v, label, x, y, {k, size, col})` | a big number with its label |
| `count(t, t0, t1, v0, v1)`, `odometer(v0, v1, k, x, y, font, col)` | number roll / per-digit flip |
| `arrow`, `line`, `circle`, `rrect`, `starburst`, `asterisk`, `arrowNE`, `jelly` (a simple mark) | shapes |
| `redacted(x, y, w, h, seed, col)` | "text" as rounded blocks: never invent real content |
| `thread(p0, p1, k, col)` | a cubic "citation" line drawn up to k |
| `texWindow(draw, src)` | letters as windows onto a shader layer (e.g. a headline filled with liquid marble) |
| `tape(t, y, rot, col, fg, words, speed, dir, k)` | a diagonal scrolling tape with ✳ / ↗ separators |
| `glitchIn(lt, seed)` | slice + RGB split on a hard cut in (auto-disabled during transitions) |
| `hud(t, {tl, tr, bl, br, zh, dark, brackets})` | the corner system + segmented progress bar |

## GL layers (render into `glA`, then `glShot()` draws it into the 2D frame)
- `terrain(t, {fade, amp, push, camY})`: additive particle landscape, for openings and chapter titles on ink.
- `liquid(t, {zoom, seed, strips, stripAmt})`: blue/red/lilac domain-warped marble, for the one "principle" line. With
  `strips` it becomes a vertical-slice glitch for exits.
- `knot(t, {x, y, s})`: a chrome torus knot with an inked outline, for "form"/"tool" shots on lime or cream. Shade it
  with a soft oval shadow.
- `cloud(t, {k, rot, x, y, s, hi})`: 9k particles morphing from a shell (k 0) to a silhouette (k 1).
  `cloud.project(i, t, o)` returns a point's screen position, so 2D lines can hit real 3D points (retrieval).
  Swap the silhouette's `inside(x, y)` for your subject.
- Post pass (`FX`): `split` (RGB offset), `slice` (row glitch), `grain`, `vign`, `flash`.

## Transitions (the `TR` map: `key: [duration, fn]`)
| fn | use it when | example |
|---|---|---|
| `trZoom(rect or () => rect)` | the eye is on a UI element (a tile, a chip, a card): zoom *through* it into the next shot | tile T07 → the eval matrix; the "01" in the index → the chapter title |
| `trIris(cx, cy, ring)` | something just lit up / a dot / a node: the next shot grows out of it | the ANSWER node → the next scene |
| `trPush(dx, dy)` | a change of topic at the same level; add nothing else | diagram → diagram |
| `trWipe(col)` | a scan / sweep already moving across the screen | the matrix scan line → the next shot |
| `trSlats(n)` | a "reveal" beat, rhythmically, on a bar | pipeline → pipeline |
| `trGrid(cols, rows, col)` | ending a section on a grid-like image (tests, pixels) | the test grid → the recap tapes |
Scenes register the rect they'll be zoomed through in `RECT` while they draw (A is rendered frozen on its last frame,
then B live; A's FX are dropped). Keep each transition 0.45–0.6 s and vary them: never three of one kind in a row.

## Recurring devices that work
- An **index/contents** card that states the order of emphasis (with each chapter's role and duration).
- The **trace** device: a segmented progress bar per chapter, and a finale that lays the whole reel out as a span
  waterfall ("STATUS OK").
- A **mark** that recurs (start: a dot becomes the mark; end: the mark next to the name; the reel collapses to a dot).
- Tapes in two directions for a chapter recap.
- Red for exactly the failures that the system catches (red flag, blocked DROP, failed gate).

<!-- ===== /file: kinetic-reel/references/style-guide.md ===== -->

<!-- ===== file: kinetic-reel/template/STORYBOARD.md ===== -->

# <Reel title> · kinetic reel (<N> s, 16:9, 30 fps, 120 BPM)

**Emphasis / time budget**: which chapter is the lead and what share of the runtime each gets
(e.g. 01 lead 36% · 02 21% · 03 17% · intro, index, finale 26%). Decide this before any code.

**Source of truth for on-screen facts**: <résumé / brief / doc>. Every number on screen comes from it, with its scope
(test set, sample size). Schematic visuals (IDs, example rows, diagrams) are labelled SCHEMATIC.

**Thread / device**: the one idea that ties the reel together (v3 used "the reel is an agent trace": segmented progress
bar + a span waterfall finale).

| Time | Chapter / shot | Headline (big type) | Visual mechanism | Transition in | Sound |
|---|---|---|---|---|---|
| 0–3 | open | — | particle terrain → dot → mark | from black | riser, blip, impact |
| 3–6 | 01 title | MAKE IT / MOVE. | drop-in letters, chip row | iris from the mark | bloom |
| … | | | | | |

<!-- ===== /file: kinetic-reel/template/STORYBOARD.md ===== -->
