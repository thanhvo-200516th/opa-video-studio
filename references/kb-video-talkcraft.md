# kb-video-talkcraft — toàn văn tài liệu của nguồn `video-talkcraft`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/video-talkcraft/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: video-talkcraft/MODULE.md ===== -->

<!-- master-video-edit: mô-đun nhập 2026-10-29 -->
> **Mô-đun `video-talkcraft`** của `master-video-edit` — chạy được trên máy này (đã sửa theo ghi chú).
> Thêm gì: 108 code-backed Remotion motion cards, SHOTBOOK shot planning, freeze/static QA for narrated videos
> Nguồn (USB): `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/AI Video/output/research-integration-20261002/sources/video-talkcraft`
> **Khi dùng trên máy Linux này:**
> - copy SKILL.md, references/, template/, scripts/, runtime/ manifests only (skip .git 2.2MB, workbench/ 1.8MB, demos/)
> - runtime/check-runtime.sh npm-installs node_modules INSIDE the skill dir: point it at an external runtime dir
> - exclude scripts/tts_fishaudio.py + test_tts_fishaudio.py (key)
> - Remotion pinned 4.0.519 (installed 4.0.539)
> - Chinese docs; scripts/fetch_icons.py calls api.iconify.design (network, no key)
> Công cụ OpenChatCut nhắc trong file (nếu có) chỉ dùng được khi app OpenChatCut mở, qua MCP `openchatcut`; không có thì làm bằng ffmpeg / faster-whisper / FilmCraft.

---
name: video-talkcraft
description: 终极口播视频 skill：中文口播稿 + 成品配音 → CPU 字级时间戳 → SHOTBOOK 层矩阵分镜 → Remotion 电影感成片（横屏默认/竖屏）。当用户要"做口播视频"、"解说/科普视频"、"把文案变成视频"、"给配音配画面动效"时使用。默认使用成品配音，可选 Fish Audio 从稿子合成配音与时间戳；数字人生成技术不在本 skill 内（人物素材是输入）。含统一视觉语言（Apple 范式）、108 张动效配方卡、镜头三面分层工作单、七层镜头反PPT系统（极缓推拉相机/让位，运动做减法）、六式运动承接转场（每式一卡）、长镜头世界画布、anime.js+three.js 桥、自动静止检测 + 独立 subagent 评估循环。
---

# video-talkcraft — 口播视频 skill

三大来源合体：**管线**（配音→字级时间戳→Remotion）+ **词汇**（108 张动效配方卡，全配可播 demo + 自包含 tsx）+ **镜头**（七层模型反 PPT 系统）+ **视觉语言**（Apple 范式默认版）。

核心范式：解说词驱动画面，每句都要有**活的画面响应**（相机极缓推拉/已有元素的变化），
但**新元素只在语义拍边界进场，禁止机械的"一句一个新元素"**（一句一元素是堆积型凌乱的制度根源；
分镜按语义段落切，排版预算见 cinematography.md §4.5）；
**一个节拍只有一个主角，说完就让位**；字幕句边界 = 全片时间锚点。

## 流程

```
① 文案 → ② 配音输入+时间戳(本机CPU) → ③ 素材 → ④ SHOTBOOK 层矩阵 → ⑤ 实现(全局系统 → 首镜先做先确认 → 其余镜头)
                                → ⑥ 渲染 → ⑦ 三重验收（机器闸全过 + 1 轮审片修 P0/P1）→ ⑧ 交付（可选续审 ≤3 轮）
```

## ⓪ 开工体检：统一依赖 + 画幅与视觉语言
**依赖只有一份**：所有口播工程的 `remotion/node_modules` 与 `workbench/node_modules` 都是指向 `<skill根>/runtime/node_modules` 的软链，版本只在
`runtime/package.json` 里钉（`@remotion/*` 全家同号）。**新片开工第一件事**（用户 2026-09-15 定版：每次新做视频都要检查更新）：
```bash
bash <skill根>/runtime/check-runtime.sh --upgrade   # 装好共享依赖 + 共享无头浏览器 + 链好 workbench；Remotion 有新版就全家升级并冒烟渲 1 帧，不过自动回滚
```
末行 `[runtime] OK` 才往下走；升了级要把 `runtime/package.json` / `package-lock.json` 的改动提交。**制作中途不升级**（母版段缓存不认依赖版本，混版本渲出的段不一致）。
工程目录里**永远不跑 `npm install`**（会写进共享目录）；要加包 → 加进 `runtime/package.json`，`npm ci`，再提交。

### 画幅与视觉语言（开工先定，全流程引用）
- **画幅默认横屏 1920×1080**（用户偏好）；明确要发抖音/竖屏渠道才用 1080×1920
- 视觉语言：**用户明确点了风格就按用户的来**（整套 token 替换）；没点时**先从口播稿判定领域、派生本片风格档**
  （`references/design-language.md` §0：读全稿答"讲什么 / 对谁讲 / 什么口吻"→ 领域 → 风格档表给底色策略 / accent / 字体气质 / 材质与卡造型 / 图表语言 / 素材气质 / 能量档，
  写进 SHOTBOOK §0 `G0 风格档`），骨架仍是 Apple 范式（一个强调色/一个投影/底色交替分幕/两档字重/
  默认幕底：浅 `pastel-mesh-flow` / 深 `mesh-flow-dark`——12 款幕底见 §1.1，代码 `template/motion-systems/backdrop.tsx`），
  派生本片 token 落成 `theme.ts`。对任何风格都成立的只有一条：禁止逐场景随手取色。
  **卡是中性 UI，进片必须蒙皮**：动效卡的 demo / tsx 是无风格的中性呈现，复制进工程后按风格档改皮（颜色 / 字体 / 圆角 / 材质 / 图表坐标轴与标记 / 占位图形）、
  不改运动命门（时序 / 缓动 / 几何比例 / 层级），契约与反例见 design-language §0.4；SHOTBOOK 每镜写**蒙皮行**

## ① 口播稿
- 每句一个信息点，钩子在第一句（数字/冲突）；13 句 ≈ 95s
- **数字一律汉字**（时间戳按文本逐字锚定，`197747` 无法与"十九万七千"的读音对位）；英文品牌词直接写（中英混合对齐已验证）
- 先调研核实事实，列"事实红线清单"（不可说错的数字/未验证数据不引用）

## ② 配音输入 → 预剪 → 字级时间戳（默认本机 CPU；可选 Fish Audio）
**默认使用成品配音**：真人录音或任何 TTS 皆可，输入 = 一条完整配音（wav/mp3）+ 与之逐字一致的口播稿。
没有录音且用户选择合成时，可使用下面方案 B；它不会替换已有配音或默认的本机 CPU 流程。

**②-0 配音预剪（真人录音必做；TTS 只会压气口，可跳过）**——剪掉口水词（嗯 / 呃 / 那个…）、结巴重说、过长停顿，
**在做时间戳之前**跑（时间戳做完再动音频 = timing / beats 全体错位；预剪 → 时间戳 → 一切后续，顺序不可换）：
```bash
python3 scripts/voice_trim.py audio/raw.wav script.json --dry-run --words-out audio/asr_words.json   # 先只出报告：逐条 [filler / repeat / pause] 起止 + 共剪多少；ASR 结果落盘
python3 scripts/voice_trim.py audio/raw.wav script.json --words audio/asr_words.json --out audio/full.wav \
    [--video dh/host_raw.mp4 --video-out dh/host.mp4]               # 用户认可后落盘（吃回上一步的词表，不再跑一次 ASR）；同一条录音的人物视频用同一 EDL 剪（音画逐帧同长）
```
- **稿子是真值，宁漏勿错**：只剪 ASR 里**稿子没有的插入段**——全由口水词表拼成的（filler）、等于紧邻稿文的结巴 / 重说（repeat）；
  ASR 听错稿子里的字永不剪（剪它就剪掉了那个字的真实发音）；稿外改了措辞的重说只报告，`--cut-unmatched` 才剪。
  词表来源缺省跑 FireRed（与下面时间戳同一后端），也吃剪映等导出的**逐字** SRT（`--srt`）或词级 JSON（`--words`）；
  句级 SRT 定位不到口水词，脚本会警告。无稿时只剪**整 token 文字恰为**保守词表（嗯 / 呃 / 额 / um…）的口水词——按规范化文字精确比对、不认同音（五≠唔、饿≠呃）；
  紧邻重复的短词无稿只报告不剪（逐字 token 下分不清叠词与结巴）。剪同录的透明 webm 时会解一帧核 alpha，帧数对但透明丢了也算 FAIL。
- 停顿：≥0.7s 的静音压到 0.35s（留段内最安静的一窗真实房间音，不补数字零），首尾留白 0.25 / 0.5s；
  切点先找能量谷、再吸附 30fps 帧网格；`cuts.json` 是 EDL（含源 → 新时间轴映射表，剪人物视频与后续任何对账都吃它）。
- **dry-run 报告必须给用户过目再落盘**：标了「切点未落在静音里，听一下」的条目让用户听那一处；脚本只删不合成，不改语速不改音高。
  剪完人物视频后跑 ③ 的 `preflight.py --media-only` 核时长——同一 EDL 只对同一条录音成立。

字级时间戳（对**预剪后**的 `audio/full.wav`）：
```bash
# 方案 A（已有录音，本机 CPU 对齐）：
pip install zhconv pypinyin sherpa-onnx soundfile numpy   # 默认后端 FireRedASR2-CTC int8 的全部依赖
# 首次：下载模型 767MB（model.int8.onnx + tokens.txt）放 ~/.cache/koubo/<模型名>/，地址见脚本头注释
python3 scripts/timestamps_cpu.py audio/full.wav script.json audio/timestamps.json
# 备选（免手动下模型）：pip install faster-whisper 后加 --backend whisper（首跑自动下载 460MB）
python3 scripts/make_timing.py audio/timestamps.json remotion/src/timing.json

# 方案 B（可选生成配音 + 时间戳，默认请求 s2.1-pro-free；可用性以 Fish Audio 为准）：
pip install requests python-dotenv   # 还需 ffmpeg，生成前会检查
# 在 .env 配置 FISH_AUDIO_API_KEY=xxx 及可选 FISH_AUDIO_REFERENCE_ID=xxx（见 .env.example）
python3 scripts/tts_fishaudio.py script.json audio/full.wav audio/timestamps.json --timing-out remotion/src/timing.json
```
- tts_fishaudio.py：默认 `--mode sentence` 每句一次请求，插入 `--pause-sec` 指定的真实静音（默认 0.25 秒）；`--mode stream` 整稿一次请求、保留自然停顿。两者均接收 UTF-8 SSE，生成结束才写文件，不提供流式播放。先解码 PCM 再拼接，偏移按采样数计算。空音频、缺失/无效对齐或文本不匹配时报错；只忽略标点、大小写与字符宽度，不自动转换数字读法。中文用接口字级锚点，英文词内插值；`match/ok` 仅确认文本映射，仍需试听。合成后若再预剪，须重新运行 CPU 对齐。
- timestamps_cpu.py：ASR 词级时间戳 → 与口播稿字符级对齐（**CJK 是可靠锚点**，
  匹配键=繁简归一+无声调拼音，同音字不算错；拉丁词各家 ASR 都常拼错，在锚点间插值）→
  每句 match 质检，<0.90 标出人工听核。默认后端 FireRedASR2-CTC（尾部最稳、零误报；整段喂入 ~200s 崩、内存平方涨，脚本默认按静音切 ≤75s 段再加回偏移，`--chunk-sec` 可调），备选 faster-whisper；
  各后端横评数据与模型下载地址见脚本头注释。
- timestamps.json schema：`{sr, total, sentences:[{i,text,start,end,match,ok,words:[{text,start,end}]}]}`
  ——words 为 CJK 逐字 + 拉丁整段 token（标点跳过）；满足此 schema 的任何对齐工具都可替换。
- make_timing.py：转成 timing.json（chars 与文本逐字符 1:1，标点零时长），供 `tSay/msSay` 锚点查询
- 配音自查（耳听）：无爆音/截断/误读；句间留 ~0.3s 气口，时间锚点更稳

### ②-1 语义标注（2026-09-22 起必做，正主 `references/semantic-annotation.md`）
口播稿逐句标「这句在做什么」，落成工程根 `semantics.json`——**这是选卡的需求侧产物**，没有它，选卡只剩输入类型一道过滤、剩下几十张卡靠印象挑（2026-09-21 那支片的「我是万里」就这样拿到了全库能量最低的文字卡，库里 P0 的人名条没人查到）。
```bash
python3 <skill根>/scripts/semantic_annotate.py --init     # 从 timestamps.json 出骨架（带词法提示 hint）
#   逐句填 sem（26 词封闭词表，见 taxonomy.md「语义索引」）/ weight（main 主句 = 允许进新元素、sub 陪衬句）/ entities / need
python3 <skill根>/scripts/semantic_annotate.py --stats    # 校验：与时间戳逐字一致 · 词表封闭 · 词法硬规（我是X→自我介绍、点赞订阅→号召、数量词→数据）· 每镜至少一个 main
```
标注是**派生物**：预剪 → 时间戳 → 标注 → 其后一切；改稿或重剪后 `text` 对不上就是标注失效，重新 `--init`。
**②-1 早于分镜，所以 `shot` 字段此时是空的**（SHOTBOOK 还没写）：④ 写完后必须回填一次，否则下游的镜头级覆盖核不到任何东西——
```bash
python3 <skill根>/scripts/semantic_annotate.py --sync-shots   # ④ 之后：按 SHOTBOOK 标题的起止秒（或 shots.json）回填 shot，只动 shot，标注不丢
```

## ③ 素材
- **素材清单从 ②-1 的语义标注生成，不靠拍脑袋**：`need` 是 `证据` 的句去截真页 / 找出处，`身份` 要头像与账号信息，`量化` 要图表或数据源，`entities` 里的人名 / 品牌 / 地点 / URL 就是检索词。
- **先给每个镜头标素材模式（多选，可组合）**：`B-roll`（实拍视频）/ `图片`（照片 / 海报 / 插图）/ `截图`（网页 / 界面证据画面）/
  `纯动效`——如"B-roll 打底 + 截图证据卡"。新闻/信息类话题证据优先：Playwright 实时截图比泛用 B-roll 更有信息量。
  四档对应 taxonomy.md 输入类型代号 **V / 图 / 截图 / 文**，SHOTBOOK 每镜写一行 `素材：V（路径）· 图（路径）· 文`（格式见 ④）
- **实拍素材是必需项，不是可选项**（2026-09-06 硬规）：全片零 B-roll / 图片 = 只有动效 + 口播人物 = 观众看到的是"讲 PPT"。
  `preflight.py` 对账 SHOTBOOK：**零 V / 图 镜头直接 FAIL**，V / 图 镜头占比 < 1/3 WARN（要在 SHOTBOOK 给依据，如证据类题材以截图为主）。
  「本片不做 B-roll」**不允许**写成设计决定；视频源搜不到就降级图片（Pexels photos 原图 → Pixabay），图片也没有才进「未完成 / 未采集清单」。
  图片与视频同源同 key，采集规格（分辨率下限、落盘目录、登记）见 `references/broll-sources.md`「配图采集」
- **真图硬规**：话题存在可截的真实页面（产品官网/GitHub/文档/画廊）时，
  成片中的浏览器/页面类镜头**禁止用代码 mock 冒充截图**——卡片 demo 里的灰条假 UI 是占位物，
  成片必须按卡片"复用指引"整块换成 `<img>` 真图；mock 只允许表现无真实对应物的示意 UI，
  且 SHOTBOOK 逐镜标注"为何无真图"。**引申**：口播讲"这样的成片/效果"时，
  示例画面必须是真成片片段（`<OffthreadVideo>` 内嵌已有成片/真机内录裁切，muted）；
  讲"长页面/看板/参数页"时用 Playwright **全页长截图**（放大镜/巡航类动效直接吃真图坐标）。
  **真图上的标注坐标一律机器实测，禁目测**：页面元素用 DOM `getBoundingClientRect`、成图用逐像素量测
  （目测偏 ±30px 就会把环框到别的元素上）；**会滚动/移动的真图，标注（环/框/pill）必须钉在内容坐标系上随内容动**，
  钉屏幕固定位就是错位根源
- **单视频镜头要有主题边框**（2026-09-07 用户定版）：镜头里唯一主体是一段视频（录屏 / 单条 B-roll / 引用别人的成片或采访）时，
  **禁止裸贴满幅、禁止裸放白卡、也不装假播放器**（进度条 / 播放键 / 时间码一律不要——不是真播放器就是在撒谎），视频区必须包一层
  `template/components/theme-frame.tsx` 的 `<ThemeFrame kind>`：八式（复古浏览器窗口 / 杂志相框 / 35mm 胶片 / 拍立得 / 工程图纸 / 笔记本 / 邮票齿边 / 双发丝线），
  **按片子调性选一式、一片只用一式**，写进 SHOTBOOK 蒙皮行；多视频的卡（bed-echo-blur 前景 / split-60-40-story 左格 / gallery-wall-dolly）的视频区也包同一式。
  框只管造型与自己的装饰接力，整体入场 / 退场 / 极缓推归镜头层；框里的画面零处理（不滤镜 / 不缩放 / 不淡入淡出）。
  例外只有两种：视频当**底床**不当主体（bed-echo-blur / §1.2 实拍底床），以及产品界面卡（chat-gpt / claude-code 类，皮即内容）。
  静图不进框（框说"这是录像"，画面不动一眼假；图用 media-pop-in / slow-push-in）。规则与八式表：design-language §1.3
- **网页拍摄不贴图**：找资料/找素材时判定可用的网页，成片里**禁止以静态截图贴屏**，
  必须像手持镜头一样"拍"它——**滚**（`evidence-scroll-tour◆`：匀速上滚 ≈10% 页高/s，讲到关键条提前减速停 1~2s）/
  **巡**（`stage-keyframe-tour◇`：长页躺台上不动，相机挨个停靠兴趣点）/ **放大**（`magnifier-detail` 圆形放大镜
  看一眼就撤，`pip-zoom-box◈` 拎出来长期挂着）/ **划**（`highlighter-sweep` 扫整句、`ink-underline◇` 划一个词、
  `scribble-annotation` 圈注箭头、`corner-bracket-frame◈` 框区域）；一屏装完的页面至少走 `slow-push-in` 底噪。
  **一镜一主式**：滚动/巡游段内不弹放大镜、不现场划线，顺序是「滚到 → 停 → 划/放大 → 再滚」；
  拍法选型表见 shot-design.md §2④「网页拍摄」。素材按 broll-sources.md「网页拍摄素材采集」规格落盘：
  Playwright **全页 2× 长截图 + 同一会话 DOM 实测的目标坐标 JSON**（放大镜/划线/停点全吃这份坐标，接上一条"禁目测"）。
  拍摄一律由 Remotion 在长截图上完成（seek-safe、可对词锚），**不用浏览器录屏**（帧率不稳、懒加载与粘性头穿帮、
  对不上字级时间戳）。唯一放行：一屏装得下且只当配角（media-pop-in 多张堆叠里的一张）的小截图可静态入卡，
  但仍带 Ken Burns，不得是该拍主体
- 标了 B-roll 的镜头列 2–3 个英文视觉概念词跑 **Pexels + Pixabay API 双源并行**，候选落 `assets/broll/`；
  源分层与授权红线（**只用免署名源**）见 `references/broll-sources.md`
- **调研记账**：承载关键事实的来源页逐一截图存档，`sources.md` 里链接与本地截图一一对应
  （禁止只存链接不留证据）；成片引用时优先用存档截图当画面证据 + micro 阶来源行
- **有 B-roll/截图 + 对应口播的人物素材（录播/数字人成品）时，人物一律降级成角标常驻**——
  圆形头像章（`host-shrink-to-chip◆`）或抠人贴角，落左下 / 右下角；不许切走人、不许人物占满画幅。
  两路选型与全部硬约束以 `references/host-footage.md` §5 为准，镜头预设见 shot-design.md §2⑦
- Manim 图表：`--transparent --format=mov` 后**必转 VP9 webm**（`-c:v libvpx-vp9 -pix_fmt yuva420p`）
- 全部落盘 public/，禁止渲染时拉远程
- **③ 收尾必跑素材体检**（把 host-footage / broll-sources 里的入场硬规变成断言；答案早就写在 reference 里、但没人在正确时刻去查，
  是 2026-09-06 复盘里两个最大的坑的共同失效模式——所以不再补文档，改成开工前必跑）：
```bash
python3 scripts/preflight.py --media-only --host remotion/public/dh/host.webm --fps 30 --voice audio/full.wav
# 查：人物素材 r/avg 帧率一致（VFR）· 源片无重复帧签名 · 素材 fps = 成片 fps（不等→成片改成素材 fps，禁 -r 直转）·
#     时长与配音逐帧对齐 · 真实宽高比 · 素材盘点（实拍/图片/网页长图数）· sources.md 在册。任一 FAIL 不进 ④
```

## ④ SHOTBOOK（必产出，实现前评审）
先用 `references/shot-design.md` 给每个镜头填**三面分层工作单**（背景面/主体面/文字面 + 各面动效
+ 七种镜头类型预设），再按 `references/cinematography.md` §4 展开成层矩阵，范例 `references/shotbook-example.md`。
每场景：一句意图 + 主体接力线 + 逐节拍层矩阵（节拍锚定字级时间戳；每行动作必须答得出"配合谁"）。
**每镜必写「素材：」行**（机器可读，preflight 逐个 stat 文件）：`- 素材：V（public/broll/gpu.mp4）· 图（public/stills/a.jpg, public/stills/b.jpg）· 截图（public/pages/gh/page.png）· 文`——
V / 图 / 截图 必须括号给路径，写"待采"= FAIL；纯动效镜也要写 `素材：文`。
**必填「## 未完成 / 未采集清单」节**：任何"本片不做 X"二选一——归入 §0 的设计决定（+依据），或归入本节（+阻塞原因 + 兜底源是否试过）；
允许写"无"，不允许缺节。这一节专门拦"未完成被包装成设计原则、进而变成不再被质疑的前提"（2026-09-06 复盘的真正失效模式）。
**G0 写一行「样板镜：sNN」**（⑤-1 首镜先做先确认用）：默认 s01；s01 是章节卡 / 空镜等不带主体动效的镜头时，选第一个有卡、有字幕、有人物或素材的镜头。
**节拍必须机器可验**：每条画面重音落成 `remotion/beats.json`
（`{t, anchor, sentence, what}`，t 一律由 timing.json/`atChar()` 查得，**禁止手敲近似秒数**——
手敲的误差静帧 QA 看不出来），SHOTBOOK 节拍表与 beats.json 一致，
机器闸用 `scripts/beat_lint.py` 对 timestamps.json 校验 |Δ|≤0.1s。
**未到拍不显形**：词锚未到的数字/图形必须完全不可见（opacity 0），
禁止压暗/灰显"预告"；行内数字要连同其后继字符一起 gate（「就 __ 类」的空洞挂着同样是缺陷）。
**开镜不空台**：镜头开场到第一个动效锚点 >1.5s 的空窗必须有承载画面
（真实 b-roll / 上一镜元素延续 / 真素材墙），不许空画布干等词锚。
**镜尾保护带**：词锚动效落点距镜头出点 <0.7s 的，要么提前、要么挪进下一镜——落点会被转场吞掉；
`beat_lint.py --shots shots.json` 机器查 ≥0.5s 硬底线。
**幕级转场事件同样入 beats.json**：shape wipe/换幕的**遮挡峰值**时刻也由词锚生成入表——
手敲绝对秒的转场事件表游离在机器可验体系外，静帧 QA 与 beat_lint 都看不见。
**排版预算**（全表 cinematography.md §4.5）：分镜按语义段落切、每镜一个 primary visual job；
**纯文镜必配陪衬图形**（2026-09-07 用户反馈"只有文字动效往上堆太单一"）：素材行只有「文」的镜头（章节卡除外），层矩阵必须多一行
「G5 线稿示意图 ← 讲 X 所以画 Y」（`references/schematic.md`，代码 `template/motion-systems/schematic.tsx`），preflight 对缺行的纯文镜 WARN；
枢轴句（"但这次不是X"式转折/设问）的动效归它**开启**的下一镜；任一时刻同屏主体组 ≤3（降权留守**计入**）、
每镜至少留一个空象限；hero 造型一屏一个。
**排版规范**（全表 `references/layout.md`）：预算管"放多少"，规范管"放哪、多大、怎么对齐"——
SHOTBOOK 每镜写**版式行**（栏跨度 + 组包围盒 + 对齐基准 + 字阶），定妆帧开 `debugOverlay` 核九项，任一失败 = P1；
独句 hero 居中但不得覆盖人脸（含 B-roll 里的人脸，纵向改取人脸之外的三分线）。
**版式轮换**（2026-09-21 用户：成片"人物在左下角、素材在中间方块、右边放文字，过于固定"；全表 cinematography.md §4.5 第 9 条）：写逐镜矩阵**之前**先在 G0 写「版式节奏表」
（`| 镜 | 人物形态·方位 | 素材容器 | 主卡 |`，格式 cinematography.md §4）——同一张呈现卡（素材呈现 / 数据 / 运镜类）不连用 3 镜、全片 ≤1/3（≥6 镜的片）；人物形态（半身 / 角标左下 / 角标右下 / 分屏格内 / 抠人贴角 / 短暂离场）
与素材容器（出血全屏 / 装框 / 分屏格 / 底床 / 多图编排 / 3D 墙 / 长页）连续 3 镜至少换其一；同一条 B-roll 不进相邻两镜。单条 B-roll 按 shot-design.md §2⑦ 七式选、相邻镜不同式，
多素材按 §2④′ 关系表；preflight 按节奏表 + 蒙皮行核（连用 / 占比 FAIL）。轮换是换构图不是加运动——每式内部仍只有相机极缓推拉。
**每镜必写「选卡行」**（②-1 的语义 → 卡；候选由机器给）：
```bash
python3 <skill根>/scripts/card_match.py --out qa/card-candidates.md   # 语义 × 素材行 × 卡索引 → 每镜每个主句语义的可行候选 + 排序理由 + 落选理由
```
跑之前先 `semantic_annotate.py --sync-shots` 回填 shot（②-1 时还没有分镜）。候选表除按语义列候选，还会给声明了素材的镜单列一行
**素材承接候选**——声明了 V / 图 / 截图 却没有呈现 / 运镜类卡承接 = 素材裸贴，preflight 判 FAIL。
SHOTBOOK 每镜写 `- 选卡行：<语义> → <卡>、<语义> → <卡>`（选卡行里的卡要真的落进蒙皮行，preflight 对账）；
**选候选之外的卡**要在该镜写一行 `- 语义偏离：自我介绍 ← 开场已报身份，s11 不再重复`（理由 ≥4 字，preflight 认这行放行）。
层矩阵的节拍行加一列**语义**（值取自 semantics.json，不另造词），这样「这一拍在做什么」在分镜里就是机器可读的。
**选卡必读卡经验**：每张选中的卡，把 `references/cards/<slug>.md` 的「已知坑」与「落位自检」**逐条抄进该镜层矩阵的自检列**，
实现后按条核（例：取景框 / 圈注 / 下划线类卡必核标注是否套住目标；`gooey-morph` 只用于图不用于字且无人物时居中；`chapter-title-card` **每章一套主题色 + 一个与本章内容相关的线稿 motif**，SHOTBOOK 写章节主题行——四张同色同纹样的章节卡是"又来了"不是"翻页"）——
卡经验不进 SHOTBOOK 就等于没读。
动效词汇从 **108 张配方卡** 里选，两道过滤都查 `references/taxonomy.md` 的机器生成索引（源头是各卡 frontmatter 的「输入 / 语义 / 素材形态 / 位置 / props」五个字段，`scripts/cards_index.py --write` 生成、`--check` 校验，手改索引无效）：**先按这一镜的输入过滤**（人 / V / 图 / 截图 / 文 / 界 / 场——「输入类型索引」），**再按这句口播的语义过滤**（自我介绍 / 数据 / 对比 / 列举 / 引用 / 号召……26 词封闭词表——「语义索引」，一张卡只列在它专为之而设的语义下）；索引里带 ◦ 的卡**没有可换内容的 prop**（只暴露资源 / 皮肤类，或什么都不暴露），改文案 / 数据要动 tsx（各卡复用指引的 props 行写了改哪里）。◉◎ 两批新卡（29 张）md 开头另有「输入类型」表 + 「常用场景」四条。然后 `references/taxonomy.md` 分类索引 → `references/cards/<slug>.md` 参数与坑 → `template/cards/<slug>.tsx` **自包含 Remotion 源码（实现以它为准，复制进工程改 CONFIG 即用）**；`demos/<slug>/index.html` 是同画面的 HTML 预览（`open gallery/index.html` 一屏浏览、demo 滚入即自动播放；带★实战卡的生产母本另在 template/motion-systems|components）。
**保真铁律**：每张用到的卡在工程里必须真实存在 `src/cards/<slug>.tsx`
（自 template 复制改 CONFIG）——只读 md 就凭卡名手写"神似"简化版是最大翻车源
（回弹/拍击/密度全丢、取景框括号方向画反、名片变色块），机器闸用 `scripts/card_lint.py`
逐 slug 校验存在性与相似度（≥0.55，改 CONFIG/文案在容忍内）。
**蒙皮不是重写**：复制来的卡是中性 UI，必须按 SHOTBOOK §0 风格档改皮——颜色全换 theme token、字体栈与字重、圆角 / 描边 / 投影 / 材质、
图表卡的坐标轴 / 网格 / 标记 / 数字字体、卡片类的占位图形换真素材或风格化图形——**只改皮层，不改时序 / 缓动 / 几何比例 / 层级**；
每镜层矩阵旁写**蒙皮行**（`卡名 → 改了什么皮`），同一片内同类卡共用一套皮；契约、例外（产品界面卡不蒙皮、语义色不换色相）与反例见 design-language §0.4。
card_lint 的 0.55 就是给蒙皮留的余量：改皮过得了，重写运动才掉下去。
三段式铁律：入场 0.2~0.8s → hold（**静置即可**——画面的活由场景相机极缓推拉负责）→ 出场 0.15~0.5s；入场永远比出场用力；同屏重音同一时刻只能有一个。
**选了动效就要带上它的音效**：每张卡在 `demos/_lib/sfx-map.js` 有 cue 表（`{t, name, vol, rate?, clip?}`，t 为卡内相对秒）——
SHOTBOOK 选卡时把 cue 抄进该镜头的层矩阵（换算成绝对秒；**vol 按成片口径重标 ≤0.35**，
demo 库的 0.65 上限是试听口径不是成片口径）。实现时按 ⑤ 的 sfx 步骤落地。
覆盖口径：**主要动效入场全覆盖**，对齐 demo 库密度
（每卡 2~6 记 ≈ 0.4 记/s，100s 的片约 40~50 记）——"少而准"管的是单点不叠双记、
音量克制（≤0.35）、连续揭示类（缓拉/对焦/逐字升起）与金句纯文字卡、logo 落幕留白、
转场只配蓄势不配落点、不要收尾叮当与重砸；不是砍覆盖面。真采样（`pk-` 前缀）优先。
**cue 的 file 名以 `ls public/sfx/` 为准**（`pk:` 键名里的冒号导出成 `pk-`，
个别键自带前缀会出现 `pk-transition-transition-soft` 这类双段名——名字错了渲染直接 404 失败）。

**④→⑤ 闸：SHOTBOOK 写完先过 preflight 全量，再进实现**（③ 的素材体检 + SHOTBOOK 对账，任一 FAIL 挡住 ⑤）：
```bash
python3 scripts/preflight.py --shotbook SHOTBOOK.md --host remotion/public/dh/host.webm --fps 30 --voice audio/full.wav --shots remotion/shots.json --semantics semantics.json
# SHOTBOOK 对账：每镜有「素材：」行 · V/图/截图 的文件都在盘上 · 零 V/图 镜头 FAIL · 占比 <1/3 WARN · 「未完成 / 未采集清单」节在册 · shots.json 与镜头 id 一致
#           · 版式轮换：同卡连用 ≥3 镜 / 呈现卡 >1/3 / 节奏表连续 3 镜同形态同容器 FAIL；版式行复制 / 素材相邻复用 / 缺节奏表 WARN
```

## ⑤ 实现（Remotion）
**先装全局系统再写场景**（代码 `template/motion-systems/`，规范正主 cinematography.md §2，运动做减法）：
只装 **G1 CameraRig**（每场景一条极缓推进或拉出的 scale 曲线，1.00→1.04~1.06 或反向，不做 x/y/旋转/模糊，`impulses` 留空，shots.ts 表驱动）
与 **G3 让位状态机**（`Live demoteAt` = 下一主体锚点 / Defocus，`idle` 关、落定即静置；**demoteAt 是降权留守不是退场**——
元素压暗缩小后仍占着原槽、计入同屏预算，新主体不得摆进它的位置；旧名 `retireAt` 仍可用但已 deprecated，2026-09-06 因名字误导出过 P0 文字相撞）；
G2 视差、G4 分幕色温可选、默认不装；主体 idle / 环境呼吸 vignette / 扫光 / 曝光脉冲 / 相机脉冲一律不做。
**G5 线稿示意图**（`schematic.tsx` + `icons.ts`）只给纯文镜装：DrawPath / DrawIcon / Connector / Node / Plate / Panel / Cross / Tick / Traveller / Label，
全部 abs 秒驱动、机器一笔画、线到哪亮哪、一套皮；图标缺什么跑 `python3 scripts/fetch_icons.py <slug,...> --merge --out <工程里 icons.ts 的路径>`（不带 `--out` 写的是库内 `template/motion-systems/icons.ts`；Iconify lucide = ISC + 部分 Feather MIT，**根目录 `THIRD_PARTY_NOTICES.md` 随 icons.ts 一起拷进工程**并登记进 sources.md）。

**每个镜头边界必须有明确转场处置，禁止裸切**：运动承接六式（lead/tail 重叠 12–16 帧 + ShotFade，
代码 `template/motion-systems/transitions.tsx`）或 caret/shape-wipe 轻量式，选型见 cinematography.md §3；
一个边界只用一式。空间/流程叙事段落可改用**长镜头世界画布**（`longtake.tsx`，cinematography.md §3.5）。
`template/components/` 是即取即用件：Subtitles 整句硬现版（chunks 由 props 注入）/FlowerWord 花字/SmashWord 砸字/HighlightSweep 荧光笔/PencilDraw 铅笔手绘/Mascot 吉祥物/NumberRoll。
**底部字幕：素排、无标点**（正主 design-language.md §5）：跟读字幕不加任何动效、整句硬现，不含任何句读（数字/型号间的半角点号除外，停顿靠拆卡）；
唯一例外 `keyword-pop-highlight` 关键词弹出且全片 **≤3 次**（motion-systems 版 `keywords` prop 有此上限自检）。
**音效落地**：`node scripts/sfx_dump.mjs remotion/public/sfx` 把库里采样解码成 mp3 →
SHOTBOOK 抄来的 cue 表落成一张 `sfx.ts`（绝对秒），场景里 `<Audio src={staticFile(...)} startFrom/volume>` 逐条摆；
音效电平比人声低 ~12dB、同帧最多一条 cue。
anime.js v4 / three.js 走 `anime-remotion.ts` / `three-anime.ts` 桥（seek-safe，工程铁律见 cinematography.md §6：零 Math.random、初始 opacity:0、lead 补偿收敛一处）。

### ⑤-1 首镜先做先确认（2026-09-09 用户定版——其余镜头动工前的必经关）
不再"整片做完再看第一镜"：全片共性（蒙皮 / 字幕样式 / 相机幅度 / 卡的密度 / 音效电平）在一镜上就判得出，做完 13 镜再改是 13 倍返工；
"改一行就整渲"的冲动也集中在这一段（2026-09-08 issue #24：9 次整片直渲全发生在制作完、验收前）。
1. **先搭全合成骨架**：`remotion/` 目录建好后先 `bash <skill根>/runtime/link-runtime.sh <本片工程>`（`node_modules` 软链到统一依赖、`package.json` 依赖版本抄 runtime——不自建、不 `npm install`），
   然后 entry / 全片时长 / `shots.ts` + `shots.json` 全表（时间来自 SHOTBOOK 与 timestamps，此时就写全）/ 全局系统（G1 相机、G3 让位、幕底、字幕、theme）
   / `src/sfx.ts` **先建成空表**（`export const CUES: SfxCue[] = []`）——⑤-2 拆解契约的六个文件（shots / scenes/index / Subtitles / sfx / timing / camera）骨架期就要齐，
   工作台一接入就是多轨、之后每落一条 cue 轨上就多一块；缺 sfx.ts 进不了多轨、工作台右下角会点名缺哪个契约模块（`@kbsrc/*` 真实 / stub 的别名在 dev server 启动时定，后补文件要重跑 link-project.sh 并重启）；
   **其余镜头一律占位**——`MainVideo-example.tsx` 里 `SCENES[shot.id]` 查不到就落到 `PlaceholderScene`（只露幕底 + 字幕，不写任何动效）。
   骨架搭全是为了 render_shots 的段表 / 时长断言原样生效，不为首镜开豁免。
2. **只实现样板镜**（SHOTBOOK G0「样板镜」行，默认 s01）：按 SHOTBOOK 全量落地——蒙皮行、卡 tsx 复制、音效 cue、转场处置——不做"先糙后精"。
3. **渲一条有声单镜预览给用户看**：只渲这一段的视频和这一段的音频，不渲整条音轨（其余镜头都是占位，整条音轨没意义；2026-09-09 demo v4 实测 6s 首镜 47s 出预览：段 34s + 段音频 10s）：
```bash
# 在工程 remotion/ 目录下
node <skill根>/scripts/render_shots.mjs --shots shots.json --only s01 --seg-audio --preview-dir out/preview
open out/preview/s01.mp4        # 打开给用户看
```
   `--seg-audio` 的段音频只活在这条预览里（渲完即删）；拼装 / 交付仍走 `--audio` 整条音轨，纪律 A 不破。
4. **问一次，等回答**（AskUserQuestion 类工具，两个选项，不替用户决定）：「样板确认，继续做其余镜头」/「先改样板」。
   改完重渲同一条预览再问；**样板未确认前不得动其余镜头**。确认后样板镜的蒙皮 / 字幕 / 相机幅度就是全片基线，其余镜头不得另起一套。

### 布局红线（数值表 design-language.md §5；几何总纲 `references/layout.md`）
- 字幕位置 / 宽度 / 字号 / 常驻件方位按画幅取 design-language §5 表（竖屏常驻件必须**左下**，右缘是抖音点赞栏）
- 横屏内容主列 ≤1440px 居中、边距 action-safe 96 / 标题 160（design-language §3；栏跨度与吸附见 layout.md §1）
- 通用：切镜后 ≤10 帧必须有主视觉入场；深色场景隐藏全局顶部标题；
  文字不叠截图文字（加白底卡）；卡片文字防裁切（预留 padding）
- **人物在场**：先跑 `scripts/face_bbox.py` 实测人脸安全区（口径 host-footage.md §3），
  任何文字/卡片/字幕**及其背景**全时刻不得进入；主信息面板放人物对侧

### ⑤-2 工作台实时看板（骨架搭完就开，制作全程常开）
把 ⑧ 里"交付后才打开工作台"前移到这里：**⑤-1 合成骨架搭完（shots.json + Main.tsx 落盘）就接入并打开工作台**，用户此后随时能看到
"做到哪了、哪镜什么状态"、能播当前实时成片、能点单镜有声预览；agent 每存一次盘预览就刷新，不用等成片（`workbench/docs/live-pipeline.md`）。
**打开即多轨**（2026-09-21 用户定版：制作中的看板与交付面是**同一个多轨工作台**，不是单轨"进度台"）——骨架一搭完，时间线上就是
字幕 / 转场标记 / 全部镜头（占位镜画斜纹）/ 幕底 / 配音 / 逐条音效各轨；agent 每落一条 cue、每实现一镜、每改一句字幕，对应轨上 ≤3s 出现
（shots / 场景 / sfx.ts / 字幕一落盘就按稳定 id 自动同步，用户改过的不覆盖）；进度轨 + 每个镜头 clip 的角标显示 占位 / 已实现 / 已渲 / 已过闸。
```bash
bash <skill根>/runtime/check-runtime.sh                                # 依赖统一在 runtime/，这一步顺手把 workbench/node_modules 链好（不在 workbench 里 npm install）
cd <skill根>/workbench
bash scripts/link-project.sh <本片工程>       # kbsrc → remotion/src；public/ 先清掉指向别的工程的旧链接再逐项软链；末行必须打印「拆解契约 OK」——否则多轨进不去，它会说缺哪个文件
npm run dev &                                                          # 已在跑就跳过；链接变了要重跑一次 npm run gen；契约文件是后补的要重启 dev server（别名启动时定）
sleep 4 && curl -s http://localhost:5199 | grep -q '动效工作台' && echo "工作台 OK" || echo "FAIL: 工作台未起"
open 'http://localhost:5199/?tracks'                                   # 进来就是多轨（字幕 / 转场 / 逐镜 / 幕底 / 配音 / 音效 + 进度轨），之后自动跟盘；?live 同义
                                                                       # 契约不全不会装任何工程，右下角点名缺哪个模块——回 ⑤-1 补齐；单轨"成片（实时）"2026-09-21 已下线
```
- **状态清单 `pipeline.json`**（工程根）：工作台 dev server 按盘上产物**实时推导**每镜状态（占位 / 已实现 / 已渲 / 已过闸、场景比段新 = 过期），
  不依赖 agent 记得写；agent 只在盘上推不出的事上落一笔，都走 `node <skill根>/scripts/pipeline_state.mjs`（在工程根或 remotion/ 下执行）：

  | 时机 | 命令 | 说明 |
  |---|---|---|
  | ⑥⑦ 某镜机器闸 + 审片过 | `--pass s03,s04` | 进度轨变绿；`--pass all` 整片 |
  | 审片发现未清缺陷 | `--issue "s07\|P1\|字幕带压到人脸安全区 12.3–12.8s"` | 进度块红点 + 镜头面板列出；修完 `--clear-issues s07` |
  | 阶段与推断不符时 | `--stage ⑥⑦` | 平时不用，阶段按产物自动推 |
  | 任何时候想核对 | 不带参数 | 重算并落盘，末行打印摘要 |

- **半成品不盖页**：Vite 报错不再罩住整个工作台，右下角一条提示 + 画面停在上一版；单 clip 渲染出错只把那一格画红；
  页面打开时工程就是坏的，修好后成片卡自动恢复（载入失败不缓存）。**只有 Player 里容错**——`render_shots` / 工作台导出走 Remotion CLI 时任何卡抛错就是渲染失败，不会把红色错误画面当成片。
- 看板画布 = 工程原尺寸（Root.tsx 的 width / height / fps **必须写数字字面量**，写变量会按默认 1920×1080@30 并在 `npm run gen` 时告警）。
- `--pass` 绑定当时的产物：段被删 / 场景之后又改过 → 该镜回到推导状态并提示"曾通过"，重渲复核后再 `--pass`。
- **Main 组件别调 `getInputProps()`**（Remotion Player 里必抛，看板上那一格会红）：debug / sfxSolo 之类开关改成组件 props（Composition defaultProps），
  或守卫 `typeof window !== 'undefined' && !(window as any).remotion_isPlayer`。
- 看板只看不驱动：不提供"点按钮触发某一步"的接口，skill 仍是主控。
- **拆解契约（工作台多轨 + 逐镜调参吃这几个导出，`template/motion-systems/` 都有样例）**：
  `shots.ts` 导出 `SHOTS`（每镜 `lead` / `tail` 帧数、`hardOut`）+ `shotSequence`；`scenes/index.ts` 导出 `SCENES`（镜头 id → 场景组件）与 `SCENE_PARAMS`（镜头 id → 该场景的 `PARAMS`）；
  **每个场景 `export const PARAMS = [...] as const satisfies readonly ParamField[]`，场景内 `const p = useParams(shot.id, PARAMS)` 取值**——表里只放语境级参数
  （文案 / 颜色 / 字号 / 位置 / 入场方向），词锚时刻、时长、缓动、几何比例、层级是命门不进表（design-language §0.4 同一条线）；
  `Subtitles.tsx` 导出 `Subtitles` + `phrases()`（全部可见字幕段：已扣静音区、已做显示映射）+ `SubtitleLine`（单句静态渲染，Subtitles 自己也用它画）；
  `Environment.tsx` 导出 `Environment`（幕底画布，画在所有镜头之下）与 `Overlays`（幕级覆盖：黑震切帧 / 落幕等，画在镜头之上、字幕之下），`Main.tsx` 从这里取；
  `params.ts` 照模板抄（`useParams` / `ParamsProvider` / `OVERRIDES`），`remotion/overrides.json` 建成 `{}`；
  **配音文件放 `public/narration.wav`**（模板 `MainVideo-example.tsx` 的约定；工作台多轨的配音块按 narration / full 解析，别叫别的名字——2026-09-21 实测叫错名字多轨整条静音、导出丢人声）；
  实拍底床用 `template/components/bed.tsx` 的 `Bed`（根元素 `className="wb-bed"`）——工作台右键导透明通道时按这个标记把底床去掉，只留动效本体。
  **`overrides.json` 归工作台写、agent 永不改**：用户在面板改的键以它为准，agent 只改 tsx 默认值——这就是双写冲突的解法；
  渲染（render_shots / 工作台导出）读同一份，所以定版前要看一眼它是否为空（用户调过参就以调过的为准交付，交付说明里写明）。
  契约是否齐全由机器闸 `python3 scripts/workbench_contract_lint.py <工程根>` 核（⑥⑦ 六条闸之一；样板镜阶段加 `--allow-placeholder`）。

## ⑥⑦ 渲染 + 三重验收（机器闸全过 → 1 轮审片 → 交付）

### 迭代纪律（管着本节全部循环）
- **闸报 FAIL 先读闸怎么量的，再动手改**（闸源码就在 scripts/）：motion_check 的静止判定是 `freezedetect n=0.003 d=0.8`
  （逐帧平均像素差 >0.3% 才算动）——平滑渐变、漂背景、纯透明度呼吸都不产生像素变化，**相机缩放才改每一个像素**；
  sfx_check --mix 量的是 `[t−0.05, t+0.45]` 0.5s 窗。读闸还能判出**闸本身够不够得着**
  （句间气口 <0.3s 而音效电平上限 −22dB 时，UNMASKED 在数学上不可达）——这种"输入决定、不是本片可修"的结论必须早下。
- **静帧优先**：`render_stills.mjs` 约 10s 一批，能答掉九成"这个改动对不对"（落点/遮挡/文案/配色/层级/取景）；
  整渲只留给跑机器闸和静帧查不了的时域缺陷（抖动/闪烁/音画/freezedetect）。
- **改哪段渲哪段、复审改动攒批再渲**：`--only s2,s4` / `--changed sNN` 只渲改动段，
  复核时逐段对时间戳确认"改的段是新的、没改的段沿用缓存"，别习惯性 `--all`；多批 P0/P1 攒成 1~2 批再渲。

**⑥-0 渲染前静态预检（零母版成本）**——三道把返修拦在母版前：
```bash
python3 scripts/beat_gap_check.py remotion/beats.json remotion/shots.json   # 空台预检（advisory，从节拍表推算）
# 每条 WARN 都要答得出"这窗里什么在动"：正常答案只有一个——该镜的相机极缓推拉覆盖了这窗（不补 idle/呼吸层）；相机确在动就 --ok 声明
cd remotion && python3 ../scripts/freeze_probe.py --shots shots.json          # 静止探针：每镜 3 个时点渲「相隔 0.8s 的两帧」，按 freezedetect 同款 yuv420p 均差判
# 量的是真实合成像素（beat_gap_check 看不见持续运动）；15 镜 90 张静帧实测 ~2 分钟，替掉"渲 10~20 分钟母版才知道 S06 过不了静止闸"。
# 2026-09-06 v4 实测：45 个采样点与母版 freezedetect 一致 98%（1 个 mafd 0.72 的边界点多报）；是单点粗筛，不是全覆盖
```
清单二·**状态切换窗**：人物轨道每个 half↔chip 切换点、每个 wipe 时刻 ±0.5s 列入静帧抽样点——
字幕带换位与人物几何过渡的穿越冲突（黑字压黑衣）只藏在这种窗口里，句级/锚点抽帧都错过。
**字幕带换位必须等几何过渡完成再切**（half→chip 延后 ~0.45s 落位）。

**⑥-1 静帧抽样**（一次 bundle 批量渲，比逐张 `npx remotion still` 快一个量级）：
```bash
# 两个 node 渲染脚本都必须在工程 remotion/ 目录下执行（Remotion 模块从工程自己的 node_modules 解析，
# 并自动加载工程的 remotion.config.ts——webpack alias / publicDir / browserExecutable 与 CLI 渲染一致；
# 吃 inputProps 的合成给 --props @props.json；素材是符号链接时 --public-dir 指向解引用同步后的目录）。
# 首跑没装浏览器会联网下载 Chrome Headless Shell（~95MB）；离线机先 npx remotion browser ensure，或 --browser 指向本机 headless shell
# 中间帧格式：renderMedia 不读 remotion.config.ts，此前永远是默认 JPEG-80——render_shots 现在透传配置里显式设的
# setVideoImageFormat / setJpegQuality / setCrf，命令行 --image-format png|jpeg --jpeg-quality 95 --crf 18 再覆盖，
# 生效值打在日志首行 `encode: …`。默认建议 jpegQuality 95：2026-09-06 白底片同段三格式实测，jpeg95 对 png 的 PSNR 47.9dB、
# jpeg80 46.0dB，静态窗噪声底三者相同（2.83/2.83/3.07），渲染时间差异小于本机运行间噪声——格式按画质定不按速度定；
# 深底渐变片的色带（用户实测 raw_mean 0.67→0.39）本次没有对应素材复测，深底风格档仍按 png。
node <skill根>/scripts/render_stills.mjs --times 2.0,7.2,...   # 抽样点=每镜入/出+关键锚点+状态切换窗
```

**⑥-1.5 定渲染节奏**（样板镜已在 ⑤-1 由用户确认，这里不再单独渲首镜给用户看；**首渲仍禁止直接 `--all`**——先问节奏）：
若 ⑤-1 之后改过全局系统（theme / 字幕 / 相机 / 幕底），先 `--only s01 --seg-audio --preview-dir out/preview` 重出样板镜，自查与确认版一致即可，不必再问用户。
然后**问一次**（AskUserQuestion 类工具，两个选项，不替用户决定）：
1. **整片渲**：⑥-2 的 `--all --parallel 4 --concat … --audio … --mux …`；
2. **逐镜节奏**：`--only s02 --audio … --preview-dir out/preview` 渲一镜、开给用户看一镜、等用户说"继续 / 改"再下一镜，
   改动用 `--changed sNN`；全部看完再 `--concat + --mux` 拼装。
两种节奏最后都要过 ⑥-2 的帧数断言与 ⑦ 三重验收——"用户看过"不等于"验收过"，机器闸与独立审片照做。

**⑥-2 分段渲染母版制**——按镜头切段、段内单进程连续渲（段内光栅自洽；多 tab 并发会产生周期性相位抖动），
段间 `--parallel 4` 实测比单进程快 1.3~1.8×（本机负载不同两次分别 253→139s、307→230s，4 镜 900 帧）；
整条音轨没有光栅问题，`--audio-concurrency 4`（默认）实测 419s→175s（116s 片），`imageFormat:'none'` 只省 6%——浏览器逐帧 seek 才是音轨渲染的主成本；
段边界都是切镜点，K 段并行：
```bash
# 在工程 remotion/ 目录下执行。首渲：K 段并行 + 拼装 + 整条音轨 + 混音
node <skill根>/scripts/render_shots.mjs --shots shots.json --all --parallel 4 \
     --concat out/assembled.mp4 --audio out/full-mix.wav --mux out/vN.mp4
# 改一个镜头 → 只重渲该段±邻段（lead/tail 交叠波及邻镜边缘）再拼装
node <skill根>/scripts/render_shots.mjs --shots shots.json --changed s14 \
     --concat out/assembled.mp4 --audio out/full-mix.wav --mux out/vN+1.mp4
npx remotion render src/entry.ts <Comp> out/sfx-solo.wav --props='{"sfxSolo":true}' --codec=wav
```
音画对齐三条硬纪律（脚本内建断言，缺一必错位）：**音轨整条不分段**（视频段全 muted，
音轨单渲一次交付时混入——每段各带 AAC 再拼会因编码器前导延迟逐段错位）；
**段边界取整与 Sequence 同规则**（差 1 帧=画面节拍整体偏 33ms）；**帧数断言**（每段实数帧+
拼装总帧数精确相等，不等即 FAIL）。音轨缓存过三关才复用：时长 == 合成时长、素材/inputProps/时序配置文件
（beats.json、cues.json、src/sfx.ts 等文件名含 sfx|cue|beat|audio|sound|timing）三项指纹未变、非半截临时文件；
指纹看不见的改动（音量常量写在组件里）用 `--force-audio`。
**修复验证同理只渲受影响段过闸**（freezedetect 单段可跑），不整渲。

```bash
# —— 关卡 1 机器闸：六条命令一次跑完，全 PASS 才进关卡 2 独立审片 ——
python3 scripts/motion_check.py out/vN.mp4 --baseline remotion/public/dh/host.webm --window <t>,<人物区 W:H:X:Y>
                                                  # 画面健康：静止段 + 抖动。抖动先查重复帧签名（人物区周期性近零差 = 素材帧率病，
                                                  # 处方在 preflight，--concurrency=1 治不了），再查并发光栅；--baseline 同窗量源片，
                                                  # 素材自带的噪声降 WARN——有人物素材的片必给，人物区窗必加
python3 scripts/sfx_check.py out/sfx-solo.wav cues.json                  # 音效在场（峰值 ≥−45dBFS）
python3 scripts/sfx_check.py --mix out/vN.mp4 audio/full.wav cues.json --timestamps audio/timestamps.json
                                                  # 音效可听（掩蔽分级）；--timestamps 数气口，UNMASKED 门槛不超过气口数并打印"不可达"原因
python3 scripts/card_lint.py remotion/src <slug,slug,...>                # 卡片保真（复制自 template/cards）
python3 scripts/beat_lint.py remotion/beats.json audio/timestamps.json --shots remotion/shots.json --anchors anchors.json
                                                  # 词落点 |Δ|≤0.1s + 镜尾保护带 ≥0.5s + label 只许 [A-Za-z0-9_-]（进文件名/JS 字符串）
python3 scripts/workbench_contract_lint.py <本片工程根>                      # 工作台拆解契约（⑤-2）：六个契约文件 · SCENES/SCENE_PARAMS 与 shots.json 对账 ·
                                                  # 每镜 PARAMS + useParams · params.ts / overrides.json · Subtitles 的 phrases/SubtitleLine——
                                                  # 漏一个导出 = 用户打开工作台才发现按钮灰 / 面板空；⑤-1 只有样板镜时加 --allow-placeholder
# 评审材料抽帧：每句 2 帧 + 动效锚点帧（anchors.json 从 beats.json 导出）
# 连拍三帧对只抽 anchors.json 里标了 "burst": true 的锚点——状态切换（两态翻转/换场/砸入落位）
# 与高风险区域必须标；其余锚点只抽定妆帧。
# motion_check 的抖动闸只量 ≤12 个 18s 间隔的固定裁剪窗、快速运动窗还跳过——窗外的短闪烁它看不见，
# 所以连拍不是可选项；--bursts 全抽只在抖动闸报警需人眼定位时用。同一份 anchors.json 也喂给 motion_check
python3 scripts/qa_extract.py out/vN.mp4 audio/timestamps.json /tmp/qa_vN 540 anchors.json
python3 scripts/motion_check.py out/vN.mp4 --anchors anchors.json   # 锚点 t+0.6s 各加一窗，结尾打印实际覆盖窗数
# 评审拼图：帧目录拼 3×4 网格（评审先整版浏览、可疑帧再回原目录单张放大）
python3 scripts/contact_sheet.py /tmp/qa_vN /tmp/qa_vN_sheets
```
机器闸口径备忘：音效两查要求工程主音轨支持 `{!getInputProps().sfxSolo && <Audio .../>}`；
可听度 MASKED>50% 或 UNMASKED 少于 max(3, 片长/30s) 即 FAIL（"81/81 在场但全被人声掩蔽"是典型翻车），
良品口径：转场/边界 cue 落句间 ~0.3s 气口出声；shots.json = 分镜表导出的 `[{"id","start","end"}]`（与 shots.ts 同源）。

**关卡 2 独立审片**（协议正主 `references/review-protocol.md`，评审 subagent 被派时必须先读它）：
必须派**全新上下文**的 subagent——不许制作者自评、禁止 fork/复用制作对话当"评审"、禁止对同一评审做 followup 复审
（fork 出来的评审继承制作者视角，对照物又是制作者自己写的 SHOTBOOK，形成自证闭环）。
派发 / 等待 / 判活 / 重派按 review-protocol §1.6 的 **harness 无关原语表**（PACKET / DISPATCH / FAN-OUT / WAIT / LIVENESS / RE-DISPATCH，Claude Code · Codex · headless 各一列）；**WAIT 以落盘 `REVIEW.md` 的结束行为准，不以子代理完成通知为准**。
制作者自己的首轮版式过目也委托子代理（只回文字缺陷清单，几十张图的图像 token 不进主上下文）。
备齐协议 §1.2 的材料五件套，评审按 rubric 出 P0/P1/P2 清单，**修完 P0 + P1 才算过关**；返修按协议 §3 给量测数字、只渲受影响段。
**关卡 3 规则合规**：cinematography.md §5 八条逐镜核 + 交付前终检（调试 overlay 关、成片缩到 390px 宽可读），条目见 review-protocol.md §2。
**审片循环**：机器闸全过后只做 **1 轮**独立审片 → 修 P0/P1 → **即交付**，同时问用户是否续审（自动轮次封顶 3 轮）
并打开动效工作台（⑧）；遗留 P2 清单随交付物。细则 review-protocol.md §4。

## ⑧ 交付
两遍 loudnorm（单遍是动态模式，会压音效瞬态；且 loudnorm 内部升到 192kHz，不加 `-ar` 会把 96k 漏进 AAC——2026-09-06 实测）：
```bash
# 第一遍量测（只看 stderr 的 JSON）
ffmpeg -i out/final.mp4 -af "loudnorm=I=-15:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p' > /tmp/ln.json
# 第二遍线性归一（measured_* 从 /tmp/ln.json 抄：input_i / input_tp / input_lra / input_thresh / target_offset）
ffmpeg -i out/final.mp4 -c:v copy \
  -af "loudnorm=I=-15:TP=-1.5:LRA=11:measured_I=<input_i>:measured_TP=<input_tp>:measured_LRA=<input_lra>:measured_thresh=<input_thresh>:offset=<target_offset>:linear=true" \
  -ar 48000 -c:a aac -b:a 192k delivery.mp4
```
听一遍确认配音无爆音/截断、音效不压人声不叠帧（loudnorm 之后音效相对电平会变）——
**agent 自己听不了成品，`sfx_check.py --mix` 就是耳听的机器替身：交付前必须对 delivery.mp4 重跑一次**；
简介附素材来源行（用了库内采样时加 sfx 来源，见 demos/_lib/sfx/ATTRIBUTION.md）。

**交付时工作台应已自 ⑤-2 起常开**（没开就按 ⑤-2 那段接入并打开；不要等用户问；与"是否继续自动审改"的询问同时给出，
见 ⑥⑦ 审片循环制度）——给用户一个剪映式界面做人工微调，并 `pipeline_state.mjs --pass …` 把过闸镜头钉绿：

```bash
bash <skill根>/runtime/check-runtime.sh          # 统一依赖体检 + 链好 workbench/node_modules（不在 workbench 里 npm install）
cd <skill根>/workbench
bash scripts/link-project.sh <本片工程>          # 链接本片工程（机器本地符号链接，不进库；手写 ln -sfn 循环不会替换指向旧工程目录的链接——2026-09-15 实测 logos 仍指上一支片）
mkdir -p public && for f in <本片工程>/remotion/public/*; do ln -sfn "$f" "public/$(basename "$f")"; done
npm run dev &                                     # 浏览器打开 http://localhost:5199/?tracks 并告知用户（多轨面；?live 同义）
sleep 4 && curl -s http://localhost:5199 | grep -q '动效工作台' && echo "工作台 OK" || echo "FAIL: 工作台未起——禁止用 remotion studio 代替"
```
**防误操作**：交付给用户的界面**只能是这个工作台**（页面标题「TalkCraft Workbench · 动效工作台」，上面那行断言就是核验）。
`npx remotion studio`（工程内）或工作台的 `npm run studio` 是开发者调参入口，**不是**交付面，不得用它代替工作台；
`npm run dev` 必须从 `<skill根>/workbench` 执行（别在本片工程目录里起）。

工作台打开（`?tracks`）就是多轨：逐句字幕（文本可改）/ 幕级覆盖 / 转场标记 / 逐镜参数化镜头 / 幕底 / 配音 / 逐条音效——自 ⑤-2 起它就在，交付时只是全部变绿；
**交付面必须是这个多轨面**，不是单轨「成片（实时）」（2026-09-21 用户反馈：成片做完打开的还是单轨进度台，没法分轨改背景 / 动效 / 字幕 / 音效）；
镜头里每个场景 `PARAMS` 声明的文案 / 颜色 / 字号 / 位置 / 入场方向逐项可调（词锚节拍、时长、缓动、相机固定），
改动写回本片 `remotion/overrides.json`，渲染读同一份；改完点「导出成片」（内置 Remotion 渲染，遵守单并发纪律）。详见 `workbench/README.md` / `GUIDE.md` ⑥。
接入按真实路径解析、契约模块缺哪个只降级哪个（`workbench/kbsrc.map.mjs`）；本 skill 产出的工程按 ⑤「拆解契约」六个文件写就能拆——
拆解按钮灰着，先看 `npm run gen` 末行报的是缺哪个契约文件，别去补造 promo 形态的 PromoScenes / Host。
发布时**推荐（非强制）**在简介 @ 一下本 skill 作者——对作者是最好的支持：
X [`@VincentWei93`](https://x.com/VincentWei93) ·
抖音 [@Vincent](https://www.douyin.com/user/MS4wLjABAAAAK1pkjBxilk2Oi_9h_vFyD-lTAu9CTlvhmOtkosDvvxg) ·
小红书 [@Vincent](https://xhslink.cn/m/At9iP2d5C1V)。
有建议、反馈欢迎扫 README「微信讨论群」小节的二维码进交流群。

## 目录路由

| 要做什么 | 看哪里 |
|---|---|
| 定视觉语言（色板/字阶/间距/字幕规范）· 幕底 12 款 | `references/design-language.md`（Apple 范式默认版；§1.1 幕底菜单 → `template/motion-systems/backdrop.tsx`） |
| 排版：放哪 / 多大 / 怎么对齐（栅格 · 间距令牌 · 居中 · 字阶 · 碰撞 · 校验九项） | `references/layout.md` |
| 给镜头做背景/主体/文字分层设计 | `references/shot-design.md`（三面工作单 + 七型预设） |
| 镜头方法论/反PPT/SHOTBOOK格式/验收 | `references/cinematography.md`（+ shotbook-example.md） |
| 审片：关卡 2 材料五件套 / rubric / 缺陷分级 · 关卡 3 · 返修纪律 · 审片循环 | `references/review-protocol.md`（评审 subagent 必读） |
| 转场（六式代码）/ 长镜头 | `template/motion-systems/transitions.tsx` / `longtake.tsx`（cinematography.md §3、§3.5） |
| 纯文字镜配线稿示意图（G5：词汇 · 语义图形词典 · 节拍纪律 · 落位自检）| `references/schematic.md` → `template/motion-systems/schematic.tsx` + `icons.ts`（`scripts/fetch_icons.py` 抓 Iconify lucide） |
| 视频容器边框八式（单视频镜不裸贴、不装假播放器；任何卡的视频区可包） | `template/components/theme-frame.tsx`（规则与选式：design-language §1.3） |
| 选动效/查参数和坑 | `references/taxonomy.md`（两道生成索引：输入类型 / 语义）→ `references/cards/` → `template/cards/`（tsx 源码）+ `demos/`/`gallery/`（预览） |
| 口播稿逐句语义标注（②-1）· 选卡候选表 · 卡索引生成 | `references/semantic-annotation.md` · `scripts/semantic_annotate.py` · `scripts/card_match.py` · `scripts/cards_index.py` |
| 找素材 · 配图采集 · 网页拍摄素材采集（全页 2× 长图 + DOM 坐标 JSON） | `references/broll-sources.md` |
| 开工体检（③ 素材期 `--media-only` / ④→⑤ 闸全量：人物素材帧率·重复帧·时长·比例 + SHOTBOOK 素材对账·未完成清单） | `scripts/preflight.py` |
| 静止探针（母版前用真实合成帧差预判 freezedetect） | `scripts/freeze_probe.py` |
| 人物素材（输入规格 / CPU 抠像 / 人脸安全区）· 与 B-roll 同屏怎么摆 | `references/host-footage.md` + `scripts/face_bbox.py` |
| 新增配方卡 | `references/demo-spec.md`，验证 `node scripts/verify-demo.mjs <slug>` |
| 可复制代码 | `template/cards/`（108 卡逐卡自包含 tsx）、`template/motion-systems/`（极缓推拉相机/让位/桥）、`template/components/`（字幕/花字/铅笔/吉祥物） |
| 成片后人工微调 / 导出 | `workbench/`（剪映式工作台：多轨时间线 + 全卡参数化 + 成片拆解 + Remotion 渲染导出） |
| 制作全程实时看板（⑤-2 起常开、打开即多轨且自动跟盘：进度轨 / 镜头状态角标 / 阶段栏 / 单镜预览 / 半成品不盖页）· 状态清单 | `workbench/docs/live-pipeline.md` · `scripts/pipeline_state.mjs`（`--pass` / `--issue` / `--stage`；状态按产物自动推） |
| 字级时间戳（本机 CPU） | `scripts/timestamps_cpu.py`（FireRedASR2-CTC 默认 / faster-whisper 备选，+ 口播稿逐字对齐）→ `scripts/make_timing.py` |
| 一键配音+时间戳（Fish Audio 免费层） | `scripts/tts_fishaudio.py`（基于 s2.1-pro-free 流式 TTS，生成 full.wav + timestamps.json + 可选 timing.json） |
| 配音预剪（口水词 / 结巴重说 / 过长停顿，时间戳之前跑；同一 EDL 剪人物视频） | `scripts/voice_trim.py`（②-0；稿子为真值只剪稿外插入段；词表来源 ASR / 逐字 SRT / 词级 JSON；`cuts.json` EDL 含时间轴映射） |
| **闸报 FAIL 了怎么办 · 怎么少烧母版** | ⑥⑦「迭代纪律」三条——先读闸怎么量的再改 · 静帧优先 · 改哪段渲哪段、复审改动攒批 |
| 机器闸（画面健康 / 保真 / 词落点+镜尾 / 音效） | `scripts/motion_check.py`（静止段+并发光栅抖动双判定）/ `scripts/card_lint.py`（卡片须复制自 template/cards）/ `scripts/beat_lint.py`（词落点对 timestamps + `--shots` 镜尾保护带）/ `scripts/sfx_check.py`（solo 在场 + `--mix` 可听度） |
| 渲染提速（分段母版 / 批量静帧 / 空台预检 / 评审拼图）· 首镜先做先确认（⑤-1） | `scripts/render_shots.mjs`（段渲+拼装+音轨混入+帧数断言；`--changed sNN` 单镜头迭代 53s；`--only s01 --seg-audio --preview-dir` 样板镜有声预览、不渲整条音轨（⑤-1）；⑥-1.5 问用户整片还是逐镜）/ `scripts/render_stills.mjs`（一次 bundle 批量 still）/ `scripts/beat_gap_check.py`（渲染前空台预检）/ `scripts/contact_sheet.py`（QA 帧拼 3×4 网格） |
| 动效配套音效 | 逐卡 cue 表 `demos/_lib/sfx-map.js`（口味纪律见 `references/demo-spec.md`「Demo 硬性要求」第 8 条）；制作端 `node scripts/sfx_dump.mjs` 导出采样 |

<!-- ===== /file: video-talkcraft/MODULE.md ===== -->

<!-- ===== file: video-talkcraft/README.md ===== -->

<div align="center">

<img src="assets/logo.svg" alt="video-talkcraft logo" width="150">

<h1>video-talkcraft</h1>

[![Gallery](https://img.shields.io/badge/Gallery-live%20previews-7A5AF8)](https://vincentwei1021.github.io/video-talkcraft/)
[![License](https://img.shields.io/badge/License-PolyForm%20Noncommercial-blue)](LICENSE)
[![WeChat](https://img.shields.io/badge/WeChat-%E8%AE%A8%E8%AE%BA%E7%BE%A4-07C160?logo=wechat&logoColor=white)](assets/wechat-group.jpg)

**口播视频的 agent skill：字级配音同步 · 108 张动效配方卡 · 七层反 PPT 镜头系统 · 三重验收**

[中文](README.md) | [English](README_EN.md)

</div>

**video-talkcraft** 是 [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)
系列的口播视频篇：一个把 Claude Code / Codex 变成口播视频动效工作室的 AI agent skill。
给它一份口播稿和一条成品配音，它在本机对齐字级时间戳、把每个语义拍写进 SHOTBOOK
分镜，然后用 [Remotion](https://www.remotion.dev/) 渲出高质量的解说成片——动态字卡、
证据截图、运镜、素排字幕、影视级音效，全部锁在人声上。

🖼️ [**在线画廊：108 张动效预览一页全览 »**](https://vincentwei1021.github.io/video-talkcraft/)

[![video-talkcraft 在线画廊](assets/gallery-zh.png)](https://vincentwei1021.github.io/video-talkcraft/)

## 统一依赖（runtime/）

所有口播工程的 `remotion/node_modules` 与 `workbench/node_modules` 都软链到 `runtime/node_modules`，版本只在 `runtime/package.json` 钉一处（`@remotion/*` 全家同号）。
- 新片开工：`bash runtime/check-runtime.sh --upgrade`（装依赖 + 共享无头浏览器 + 链 workbench；Remotion 有新版就升级并冒烟渲 1 帧，不过回滚）。
- 接工程：`bash runtime/link-runtime.sh <工程根>`（软链 + package.json 版本对齐）。工程目录里不跑 `npm install`。
- 一份 `node_modules` ≈ 760 MB（含 190 MB 无头浏览器）；之前每支片各装一份，六个工程 3.9 GB。

## 🆕 更新（What's new）
<!-- 写法约定：每条一句话、≤ 200 字（含指向链接），只写"是什么 + 改了什么行为"；细节、参数、卡名清单一律 → 指向 references / SKILL.md 章节，不在这里展开；中英同步。口径由 2026-09-05 PR #12 定，#14/#18 曾回到长段落，2026-09-07 收回。 -->

**2026-09-11**

- ✂️ **配音预剪 `scripts/voice_trim.py`**——真人录音先以口播稿为真值剪掉口水词 / 结巴重说 / 过长停顿再做时间戳（只剪稿子里没有的插入段，ASR 听错的字永不剪），词表来源可选 FireRed ASR / 逐字 SRT / 词级 JSON，切点吸附帧网格、同一 EDL 可剪人物视频保音画同长（→ SKILL.md ②-0）。
- 🫥 **工作台右键导出透明通道**——时间轨上右键任一动效片段可导出只含这一段的透明视频（MOV ProRes 4444 / WebM VP9 alpha），根底透明、自动去掉卡根层幕底与人物剪影占位，给剪映 / PR / AE 当叠加素材；右键菜单同时带分割 / 复制 / 删除（→ `workbench/GUIDE.md` ⑦）。
- 📺 **工作台实时看板（L1）**——⑤-1 骨架搭完就接入并开着工作台：阶段栏 + 进度轨（每镜 占位 / 已实现 / 已渲 / 已过闸 / 过期 / 红点）+ 镜头视图（单镜预览 · issues · SHOTBOOK 段落）+ 实时成片卡（2026-09-21 起单轨成片卡下线，看板即多轨），状态按盘上产物自动推、`scripts/pipeline_state.mjs --pass/--issue` 只补人工判定，代码半成品不再盖页（→ SKILL.md ⑤-2、`workbench/docs/live-pipeline.md`）。
- 🔗 **工作台接入加固**——`kbsrc` 改按真实路径解析、契约模块缺哪个只回退哪个 stub、导出形态差异由 `src/kb/` 适配层归一：接入 skill 正式工程（`Main.tsx` + `scenes/`，无 promo 模块）不再整页 500，「拆解导入」按钮按契约自动禁用（→ `workbench/README.md`「接入口播成片工程」）。

**2026-09-09**

- 🎬 **首镜先做先确认**——⑤ 实现改为先搭全合成骨架、其余镜头占位，只做样板镜并用 `--seg-audio` 出一条有声单镜预览给用户确认，确认后再做其余镜头；⑥-1.5 只剩"整片还是逐镜"一问（→ SKILL.md ⑤-1）。

**2026-09-07**

- ✏️ **G5 线稿示意图系统**——纯文字镜必配一张图标 + 方框 + 箭头的线稿陪衬图，文字不裸放、每句至少一个可见变化，缺陪衬行 preflight 报 WARN（→ `template/motion-systems/schematic.tsx`、`references/schematic.md`）。
- 🎞️ **视频容器边框八式 + 章节主题层**——单视频镜头必须包一式主题边框（浏览器窗 / 胶片 / 拍立得 / 图纸等八式，一片一式、不做假播放器），章节卡按章换色 + 线稿 motif（→ `template/components/theme-frame.tsx`、design-language §1.3）。

**2026-09-05**

- 🔁 **19 张 video-shotcraft 移植卡（89 → 108）**——从姊妹库 [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) 两轮筛选移植（09-06 删定格圈注余 18），tsx 改成本库自包含契约、带母本溯源（→ `references/taxonomy.md` 第八批◎）。
- 🎨 **领域定风格 · 中性卡蒙皮**——开工先由口播稿判定领域、派生风格档写进 SHOTBOOK G0；库里的卡是中性 UI，进片按风格档改皮不改运动命门，每镜写蒙皮行（→ `references/design-language.md` §0）。
- 🧩 **10 张多素材同屏新卡（79 → 89）**——并列句排版、三联画接力、对比分屏、传送带、卡堆扇开、照片墙推轨 / 时间线照片带等，每卡标注输入类型与常用场景，选卡先按素材类型过滤（→ `references/taxonomy.md` 输入类型索引）。
- 📐 **排版规范 `references/layout.md`**——12 栏栅格、间距令牌、字阶最小档、包围盒不相交等九项自检，选中卡的「已知坑 / 落位自检」必须抄进 SHOTBOOK。
- 🎨 **12 款动态幕底入库**——`template/motion-systems/backdrop.tsx` 深浅各 6 款、frame 驱动零随机，默认幕底改为浅 `pastel-mesh-flow` / 深 `mesh-flow-dark`。

**2026-09-04**

- 🎥 **运动系统做减法**——每场景只保留一条极缓推拉相机曲线 + 让位，idle 微动 / 环境呼吸 / 脉冲全部默认关闭。
- 🌐 **网页拍摄不贴图**——网页素材不再静态贴屏，改为镜头滚动 / 巡游 / 放大镜 / 划重点"拍"出来，坐标全吃 Playwright 实测（→ SKILL.md §③、`references/shot-design.md` §2④）。

**2026-09-02**

- 🎛️ **动效工作台 `workbench/`**——剪映式的成片后期台：多轨时间线 + 素材库（素材 / 动效库 / 音效 / 背景）+
  schema 属性面板 + 实时预览 + 一键「导出成片」。108 张动效卡 100% 参数化（文案 / 颜色 / 字号 / 位置可调，
  节奏命门固定不暴露）；口播成片可一键拆成字幕 / 转场 / 环境 / 数字人 / 镜头 / 配音 / 音效七类多轨单元逐项微调。
  skill 交付成片后会主动打开它。→ [**图文指南 workbench/GUIDE.md**](workbench/GUIDE.md)

  <a href="workbench/GUIDE.md"><img src="workbench/docs/img/01-overview.png" alt="动效工作台总览" width="720"></a>

- ⚡ **渲染提速：分段渲染母版制**——`scripts/render_shots.mjs` 按镜头切段并行渲、段内单进程保光栅一致，
  拼装 + 整条音轨混入 + 帧数断言；改一个镜头只重渲该段±邻段。`scripts/render_stills.mjs` 一次 bundle 批量出静帧。
- 🧮 **评审 token 减量**——`scripts/contact_sheet.py` 把 QA 帧拼成 3×4 网格给评审子代理整版浏览；连拍三帧对只对标了
  `"burst": true` 的状态切换锚点抽（曾占评审材料 2/3）。
- ✅ **一轮审片即交付**——机器闸全过后只做 1 轮独立审片、修完 P0/P1 即交付，再询问是否续审（累计封顶 3 轮），
  替代旧的"循环到全过"。

| 实测（201s 竖屏片） | 之前 | 现在 |
|---|---|---|
| 全片首渲 | 13 min | 9 min |
| 改一个镜头出有声新片 | 整渲 | 53 s |
| 43 张静帧抽样 | 11 min | ~1 min |
| 评审读 160 张 QA 帧 | ≈16 万 token / 21 min | ≈4 万 token / 7 min（拼图） |

- 🤝 新卡：社区贡献 **douyin-follow-card 抖音主页关注卡**（[@scpcn01vision-oss](https://github.com/scpcn01vision-oss)），库存 79 张。

## ✨ 亮点

- **字级配音同步**——`scripts/timestamps_cpu.py` 把口播稿对齐到音频
  （默认 FireRedASR2-CTC int8，备选 faster-whisper 免手动下载）。110s 中英混合口播
  对照 GPU 强制对齐器实测：字级偏差中位 20–40ms、最差 200ms、质检零误报。
  每个动效节拍都锚在确切的字上。
- **108 张动效配方卡**——每张有意图、参数、已知坑、可直接复制的自包含 Remotion tsx 源码和可跑的 HTML 预览，
  [在线画廊](https://vincentwei1021.github.io/video-talkcraft/)一页全览
  （本地 `open gallery/index.html` 同款）。动态字卡、数据镜头、证据巡游、
  六式运动承接转场、长镜头世界画布、人物合成等。
- **七层反 PPT 系统**——每场景一条极缓推进 / 拉出的相机曲线 + 让位生命周期 + 六式运动承接转场
  （2026-09-04 起做减法：不再要求主体 idle 与环境呼吸）。
  静止帧在结构上不可能出现（漏网的也会被自动检测抓住）。
- **经得住审片的排版纪律**——语义拍分镜、同屏元素预算、留白锚、枢轴句切镜规则、
  用真实检测（`scripts/face_bbox.py`）量出来的人脸安全区，不靠目测。
- **三重验收**——画面健康双判定（静止段 + 并发光栅抖动，时域缺陷机器抓）、
  纯音效轨逐 cue 能量验证、带动效锚点帧与评审拼图的独立评审。

## 🚀 快速开始

**最直接的方式：把仓库链接丢给你的 agent。**
在 Claude Code / Codex 里直接说：

```text
帮我安装这个 skill：https://github.com/Vincentwei1021/video-talkcraft
```

或用 [skills](https://skills.sh/) CLI / 手动安装：

```bash
npx skills add Vincentwei1021/video-talkcraft
```

```bash
git clone https://github.com/Vincentwei1021/video-talkcraft.git
cd video-talkcraft
ln -s "$(pwd)" ~/.claude/skills/video-talkcraft   # Claude Code
# 或
ln -s "$(pwd)" ~/.codex/skills/video-talkcraft    # Codex
```

环境（agent 会按需自行配置）：

- Node 18+（Remotion 渲染；单片工程内 `npm install`）
- Python 3.10+
  - 本机 CPU 时间戳对齐：`pip install zhconv pypinyin sherpa-onnx soundfile numpy`
    （首次使用下载一次 767MB 的 FireRedASR2-CTC 模型，地址见
    `scripts/timestamps_cpu.py` 头注释；或加 `--backend whisper` 免手动下载）
  - 一键流式配音+时间戳（Fish Audio 免费层）：`pip install requests python-dotenv`
- ffmpeg

然后这样下需求：

```text
用 video-talkcraft 把这份口播稿 + voiceover.wav 做成视频。
做一条 100 秒的 <话题> 解说，稿子和音频在这里。
```

### 🎙️ 可选：Fish Audio 生成配音 + 字级时间戳

默认仍是「成品配音 + 本机 CPU 对齐」。没有录音时，可主动选择 Fish Audio 接入；脚本默认请求 `s2.1-pro-free`，模型的免费额度与可用期限以 Fish Audio 为准。

1. 安装 `ffmpeg` 和 Python 依赖 `pip install requests python-dotenv`。
2. 复制 `.env.example` 为 `.env`，填写 `FISH_AUDIO_API_KEY`。`FISH_AUDIO_REFERENCE_ID` 可填音色库中的音色 ID，留空使用服务默认音色。
3. 准备 `script.json`，例如 `{"sentences": ["这是第一句。", "这是第二句。"]}`；也支持字符串数组或每行一句的 `.txt`。
4. 生成音频与时间戳：
   ```bash
   # 默认逐句模式：每句一次请求，句间插入 0.25 秒真实静音
   python3 scripts/tts_fishaudio.py script.json audio/full.wav audio/timestamps.json --timing-out remotion/src/timing.json
   # 整稿一次请求，保留模型生成的句间节奏
   python3 scripts/tts_fishaudio.py script.json audio/full.wav audio/timestamps.json --timing-out remotion/src/timing.json --mode stream
   ```

两种模式均接收 SSE 音频与对齐快照；`stream` 表示流式接收，**文件在全部生成完成后写出，不提供边生成边播放**。`--pause-sec` 只控制逐句模式额外插入的静音。音频先分别解码成 PCM，再拼接、编码，时间戳按实际采样数累计。`--format mp3|wav|opus` 控制接口返回格式，输出格式由音频文件扩展名决定。

中文沿用接口的字级锚点；英文在词内按字符插值，标点零时长。空音频、缺失/无效对齐、解码失败、规范化后稿子与对齐文本不一致都会报错退出。规范化忽略标点、大小写与字符宽度，不推测 `2` 与 `two` 等读法转换；遇到此类差异请改写为实际朗读文本，或使用已有音频走本机 CPU 对齐。`match=1` / `ok=true` 表示文本映射通过，不代表已人工确认发音或字级精度，仍需试听。

回归验证（无需 API Key，需要 `requests` 与 `ffmpeg`）：
```bash
python3 -m unittest discover -s scripts -p 'test_*fish*.py' -v
```

## 🎞 你提供什么 vs. 它做什么

| 你提供（输入） | skill 负责 |
| --- | --- |
| 口播稿 | 字级时间戳对齐，逐句质检标记 |
| 成品配音——任何 TTS 或真人录音 | SHOTBOOK 分镜：语义拍、层矩阵、排版预算 |
| 可选的人物素材——普通实拍视频即可（抠像 + 人脸安全区工具已含，绿幕抠得最干净） | Remotion 实现：全局系统（极缓推拉相机/让位）、转场、音效落位 |
| 可选的 B-roll / 截图 | 渲染 + 三重验收（机器闸全过 + 一轮独立审片修完 P0/P1 即交付，可选续审累计 ≤3 轮），响度归一交付 |

## 📦 库里有什么

| 内容 | 说明 |
| --- | --- |
| 108 张动效配方卡 | 意图、能量档、参数、实现要点、已知坑——每张都配自包含 Remotion tsx 源码（`template/cards/`，复制单文件即用）+ 可跑的 HTML demo |
| 画廊 | [在线版](https://vincentwei1021.github.io/video-talkcraft/)或本地 `open gallery/index.html`——108 个预览一页自动播放，按名称/关键词搜索 |
| 动效系统 | CameraRig（极缓推拉）、让位生命周期、六式转场、长镜头世界画布；视差 / 环境层可选（`template/motion-systems/`） |
| 组件 | 素排字幕、花字、砸字、荧光笔、铅笔手绘、数字滚动、视频容器边框八式（`template/components/`） |
| 管线脚本 | 字级时间戳（双 ASR 后端）、人脸安全区检测、静止检测、音效在场检查、QA 抽帧（`scripts/`） |
| 方法论 | 设计语言（Apple 范式默认）、镜头三面工作单、电影感规范、分镜格式、验收口径（`references/`） |
| 内嵌音效 | 逐卡 cue 表 + 真采样内嵌 demo 库（授权见 `demos/_lib/sfx/ATTRIBUTION.md`） |

## 🗂 目录结构

```text
video-talkcraft/
├── SKILL.md                    # agent 入口：八步管线与硬规则
├── references/
│   ├── design-language.md      # 默认视觉系统（色板/字阶/布局/字幕）
│   ├── shot-design.md          # 三面工作单 + 七型镜头预设
│   ├── cinematography.md       # 七层模型、转场、排版预算、验收关卡
│   ├── shotbook-example.md     # 完整分镜范例
│   ├── cards/                  # 108 张动效配方卡
│   ├── taxonomy.md             # 按类别与来源的卡片索引
│   ├── broll-sources.md        # 免署名素材源（API、授权坑）
│   ├── host-footage.md         # 人物素材：输入规格、抠像、人脸安全区
│   └── demo-spec.md            # 卡片/demo 编写规范
├── demos/                      # 108 个可跑的 HTML 预览（共享库内嵌音效）
├── gallery/                    # 单页本地画廊
├── template/                   # 即取即用的 Remotion 代码
│   ├── cards/                  # 108 卡逐卡自包含 tsx 源码（skill 首选引用）
│   ├── motion-systems/         # 相机/视差/让位/环境/转场/长镜头系统
│   └── components/             # 字幕/花字/砸字/铅笔等组件
└── scripts/                    # 时间戳、人脸检测、QA 工具
```

完整工作流从 [SKILL.md](SKILL.md) 进入。

## ❓ FAQ

**video-talkcraft 是什么？**
一个开源的 AI agent skill（Claude Code / Codex 技能包），用于 AI 视频制作：
把口播稿 + 成品配音自动做成带动效的口播视频。它不是剪辑软件，也不是模板站——
agent 读方法论、选动效配方卡、写 [Remotion](https://www.remotion.dev/) 代码、
跑三重验收，产出可直接发布的解说成片。

**能做哪类视频？**
知识科普、产品评测、新闻解读、观点锐评等口播/解说类横屏视频。
中文口播优先设计，中英混排完全支持。

**需要准备什么？**
口播稿（文本）+ 成品配音（任何 TTS 或真人录音）；人物出镜素材与 B-roll 可选。

**免费吗？**
个人、教育、研究用途免费（PolyForm Noncommercial 1.0.0），
用它做出的视频归你所有；工具本身的商业使用需先授权（见下）。

## 📄 许可

[PolyForm Noncommercial 1.0.0](LICENSE)——个人、教育、研究用途免费。
**将本工具用于任何商业用途需事先获得授权**——发邮件至
[vincentwei1021@gmail.com](mailto:vincentwei1021@gmail.com) 或提 GitHub issue 联系。

**用本 skill 做出的视频归你所有。** 如果它帮到了你，欢迎在视频简介里
@ 一下作者的账号——非强制，但对作者是最好的支持。

## 🔊 音频与素材说明

- 内嵌音效采样的来源与授权：[demos/_lib/sfx/ATTRIBUTION.md](demos/_lib/sfx/ATTRIBUTION.md)。
- B-roll 素材源指南只收免署名源（Pexels、Pixabay、Mixkit Free、Coverr、NASA），
  并记录了被排除源的授权陷阱——见 [references/broll-sources.md](references/broll-sources.md)。
- demo 里的主持人素材（`demos/_lib/dh-host.webm`）是 AI 生成的演示形象占位，
  生产时请替换为你自己的人物素材。

## 🙏 致谢

- **[Remotion](https://www.remotion.dev/)**——驱动全部渲染的 React 视频框架
  （注意其自身[许可](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md)）。
- **[FireRedASR2](https://github.com/FireRedTeam/FireRedASR2S)**（经
  **[sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx)**）与
  **[faster-whisper](https://github.com/SYSTRAN/faster-whisper)**——时间戳后端；
  **Qwen3-ASR/ForcedAligner** 是精度基准参照。
- **OpenCV YuNet**——人脸安全区规则背后的检测器。
- **Pexels · Pixabay · NASA · Mixkit**——免署名素材来源。
- **Claude Code**——本库由 AI 编码 agent 构建、迭代与验收，用的正是 skill 自己教的那套评审循环。

## 关注作者

<p>
  <a href="https://www.douyin.com/user/MS4wLjABAAAAK1pkjBxilk2Oi_9h_vFyD-lTAu9CTlvhmOtkosDvvxg"><img alt="在抖音关注作者" src="https://img.shields.io/badge/%E6%8A%96%E9%9F%B3-%E5%85%B3%E6%B3%A8%E6%88%91-000000?style=for-the-badge&logo=tiktok&logoColor=white"></a>
  <a href="https://xhslink.cn/m/At9iP2d5C1V"><img alt="在小红书关注作者" src="https://img.shields.io/badge/%E5%B0%8F%E7%BA%A2%E4%B9%A6-%E5%85%B3%E6%B3%A8%E6%88%91-FF2442?style=for-the-badge&logo=xiaohongshu&logoColor=white"></a>
  <a href="https://x.com/VincentWei93"><img alt="在 X 关注作者" src="https://img.shields.io/badge/X-%E5%85%B3%E6%B3%A8%E6%88%91-000000?style=for-the-badge&logo=x&logoColor=white"></a>
</p>

## 微信讨论群

有建议、反馈或使用问题？扫码加入 video-talkcraft 交流群（3 群）：

<img src="assets/wechat-group.jpg" alt="video-talkcraft 微信交流群二维码" width="300">

二维码更新于 2026-10-01，过期后会不定期更新；也可通过上方社媒直接联系作者。

<!-- ===== /file: video-talkcraft/README.md ===== -->

<!-- ===== file: video-talkcraft/README_EN.md ===== -->

<div align="center">

<img src="assets/logo.svg" alt="video-talkcraft logo" width="150">

<h1>video-talkcraft</h1>

[![Gallery](https://img.shields.io/badge/Gallery-live%20previews-7A5AF8)](https://vincentwei1021.github.io/video-talkcraft/)
[![License](https://img.shields.io/badge/License-PolyForm%20Noncommercial-blue)](LICENSE)

**An agent skill for crafting high-quality voiceover-driven videos: word-level voiceover sync · 108 motion recipe cards · a 7-layer anti-slideshow shot system · triple-gate QA**

[中文](README.md) | [English](README_EN.md)

</div>

**video-talkcraft** is the voiceover-driven explainer installment of the
[video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) series:
an AI agent skill that turns Claude Code or Codex into a motion-design studio
for narrated explainer videos. Give it a narration script and a finished
voiceover, and it aligns word-level timestamps locally, storyboards every
semantic beat into a SHOTBOOK, then renders a polished explainer with
[Remotion](https://www.remotion.dev/) — kinetic type, evidence screenshots,
camera moves, plain-cut subtitles, and film-grade SFX, all locked to the voice.

> The methodology docs and recipe cards are written in Chinese — the toolkit is
> built Chinese-narration-first (mixed Chinese/English narration is fully
> supported). Agents read them natively.

🖼️ [**Browse all 108 motion previews in the live Gallery »**](https://vincentwei1021.github.io/video-talkcraft/)

[![video-talkcraft live gallery](assets/gallery-en.png)](https://vincentwei1021.github.io/video-talkcraft/)

## 🆕 What's new
<!-- Style rule: one sentence per entry, ≤ 350 characters including the pointer link, stating what it is and what behaviour changed; details, parameters and card lists point to references / SKILL.md sections instead of being expanded here. Keep zh and en in sync. Set by PR #12 (2026-09-05); #14/#18 drifted back to long paragraphs, tightened again 2026-09-07. -->

**2026-09-11**

- ✂️ **Voice pre-trim `scripts/voice_trim.py`** — a human recording is now cleaned before timestamping, using the script as ground truth to cut filler words / stutters and re-takes / over-long pauses (only insertions absent from the script are cut, ASR mishearings of scripted characters never are); word timings come from FireRed ASR, a per-character SRT or a word-level JSON, cut points snap to the frame grid, and the same EDL can trim the host video so audio and picture stay frame-aligned (→ SKILL.md ②-0).
- 🫥 **Workbench: right-click → export with alpha** — right-click any motion clip on the timeline to render just that clip as a transparent video (MOV ProRes 4444 or WebM VP9 alpha) with a transparent canvas, the card's root backdrop and host-silhouette placeholder stripped automatically, ready as an overlay in CapCut / Premiere / After Effects; the same menu carries split / duplicate / delete (→ `workbench/GUIDE.md` ⑦).
- 📺 **Workbench live production board (L1)** — the workbench now attaches as soon as the ⑤-1 skeleton exists and stays open: a stage bar, a per-shot progress track (placeholder / implemented / rendered / passed / stale / open-issue dot), a shot view (single-shot preview, issues, SHOTBOOK excerpt) and a live composition card; status is derived from on-disk artifacts, `scripts/pipeline_state.mjs --pass/--issue` only records human verdicts, and half-written code no longer blanks the page (→ SKILL.md ⑤-2, `workbench/docs/live-pipeline.md`).
- 🔗 **Hardened workbench project linking** — `kbsrc` now resolves through the real path, each contract module falls back to its stub individually, and `src/kb/` normalises export shapes: linking a regular skill-built project (`Main.tsx` + `scenes/`, no promo modules) no longer 500s the whole page, and "拆解导入" (split import) disables itself with a reason when the contract isn't met (→ `workbench/README.md`, "接入口播成片工程").

**2026-09-09**

- 🎬 **First shot before the rest** — step ⑤ now scaffolds the whole composition with placeholder shots, builds only the sample shot, renders it as a single-shot preview with `--seg-audio` (no full audio track) for user sign-off, and only then builds the remaining shots; ⑥-1.5 keeps just the "full render or shot by shot" question (→ SKILL.md ⑤-1).

**2026-09-07**

- ✏️ **G5 line-art schematic system** — every text-only shot must carry an icon + box + arrow line drawing, text is never placed bare, at least one visible change per sentence, and preflight WARNs when that companion row is missing (→ `template/motion-systems/schematic.tsx`, `references/schematic.md`).
- 🎞️ **Eight video theme frames + chapter theme layer** — a single-video shot must sit inside one themed frame (browser window / film / instant photo / blueprint and four more; one frame per film, no fake player), and chapter cards switch colours plus a line-art motif per chapter (→ `template/components/theme-frame.tsx`, design-language §1.3).

**2026-09-05**

- 🔁 **19 cards ported from video-shotcraft (89 → 108)** — two review rounds over the sister library [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) kept 19 (freeze-frame annotate removed 2026-09-06, 18 remain), each tsx rewritten to this library's self-contained contract, source cited (→ batch ◎ in `references/taxonomy.md`).
- 🎨 **Domain-driven style and card skinning** — derive a style profile from the script's domain before storyboarding (SHOTBOOK G0); library cards are neutral UI and are re-skinned to that profile without touching their motion vitals, one skinning line per shot (→ `references/design-language.md` §0).
- 🧩 **10 new multi-asset cards (79 → 89)** — parallel-sentence layouts, triptych relay, compare slider, filmstrip, stack fan-out, gallery-wall dolly / timeline photo strip and more; every card lists its input types and common scenarios, so card selection starts by filtering on the shot's material (→ input-type index in `references/taxonomy.md`).
- 📐 **Layout spec `references/layout.md`** — 12-column grid, spacing tokens, minimum type sizes, non-overlapping boxes and a 9-point still check; each chosen card's pitfalls / placement checks must be copied into the SHOTBOOK.
- 🎨 **12 dynamic backdrops shipped** — `template/motion-systems/backdrop.tsx`, 6 dark / 6 light, frame-driven with zero randomness; defaults are now light `pastel-mesh-flow` / dark `mesh-flow-dark`.

**2026-09-04**

- 🎥 **Motion system slimmed down** — one very slow push / pull camera curve per scene plus the yield lifecycle; idle wobble, breathing and pulses are off by default.
- 🌐 **Web pages are filmed, not pasted** — pages are shot by the camera (scroll, tour, magnifier, highlighter) instead of appearing as static screenshots, with every coordinate read from Playwright measurements (→ SKILL.md §③, `references/shot-design.md` §2④).

**2026-09-02**

- 🎛️ **Motion workbench `workbench/`** — a CapCut-style post-production desk for finished videos: multi-track timeline,
  library (media / motion cards / SFX / backgrounds), schema-driven inspector, live preview and one-click **Export**.
  All 108 motion cards are parameterized (copy, colors, sizes, positions editable; timing vitals stay fixed).
  A narration video can be split into seven kinds of editable units — subtitles / transitions / environment /
  avatar / shots / voiceover / SFX. The skill opens it for you after delivery. → [**Illustrated guide (zh)**](workbench/GUIDE.md)

  <a href="workbench/GUIDE.md"><img src="workbench/docs/img/01-overview.png" alt="Workbench overview" width="720"></a>

- ⚡ **Faster renders: shot-segmented master rendering** — `scripts/render_shots.mjs` renders per-shot segments in
  parallel (single-process inside each segment to keep rasterization consistent), then concatenates, mixes in the
  full audio track and asserts frame counts; changing one shot re-renders only that segment ± neighbours.
  `scripts/render_stills.mjs` renders batches of stills from a single bundle.
- 🧮 **Fewer review tokens** — `scripts/contact_sheet.py` tiles QA frames into 3×4 sheets for the reviewer subagent;
  burst triples are extracted only at anchors flagged `"burst": true` (they used to be 2/3 of the review material).
- ✅ **One review round, then deliver** — after the machine gates pass, a single independent review round fixes
  P0/P1 and the video ships; further rounds are opt-in (3 max) instead of "loop until clean".

| Measured (201 s vertical video) | Before | Now |
|---|---|---|
| Full first render | 13 min | 9 min |
| New video with audio after changing one shot | full re-render | 53 s |
| 43 sampled stills | 11 min | ~1 min |
| Reviewer reading 160 QA frames | ≈160k tokens / 21 min | ≈40k tokens / 7 min (sheets) |

- 🤝 New card: community-contributed **douyin-follow-card** ([@scpcn01vision-oss](https://github.com/scpcn01vision-oss)) — 79 cards total.

## ✨ Highlights

- **Word-level voiceover sync** — `scripts/timestamps_cpu.py` aligns
  your script to the audio (FireRedASR2-CTC int8 by default, faster-whisper as
  the zero-download fallback). Benchmarked against a GPU forced aligner on a
  110s mixed-language narration: median per-character offset 20–40 ms,
  worst case 200 ms, zero false QA flags. Every motion beat anchors to the
  exact word.
- **108 motion recipe cards** — each with intent, parameters, known pitfalls,
  a copy-paste self-contained Remotion tsx source, and a runnable HTML
  preview — browse them all in the
  [online Gallery](https://vincentwei1021.github.io/video-talkcraft/) or
  locally with `open gallery/index.html`. Kinetic type, data shots, evidence
  tours, six motion-carry transitions, a long-take world canvas, host
  compositing, and more.
- **A 7-layer anti-slideshow system** — one very slow push-in or pull-out camera
  curve per scene, a yield lifecycle and six motion-carry transitions (slimmed
  down on 2026-09-04: subject idle and the breathing environment are no longer
  required). Statically frozen
  frames are structurally impossible (and automatically detected if they
  slip through).
- **Layout discipline that survives review** — semantic-beat storyboarding,
  on-screen element budgets, whitespace anchors, pivot-sentence cut rules,
  and face safety zones measured by real detection
  (`scripts/face_bbox.py`), not by eye.
- **Triple-gate QA** — automated stillness detection, per-cue SFX energy
  verification on a solo track, and an independent-reviewer pass armed with
  anchor frames (plus burst triples at state-switch anchors, which catch
  time-domain defects single frames can't show).

## 🚀 Quick start

**The most direct way: hand the repo link to your agent.**
In Claude Code / Codex or a similar agent, just say:

```text
Install this skill for me: https://github.com/Vincentwei1021/video-talkcraft
```

Or install with the [skills](https://skills.sh/) CLI / manually:

```bash
npx skills add Vincentwei1021/video-talkcraft
```

```bash
git clone https://github.com/Vincentwei1021/video-talkcraft.git
cd video-talkcraft
ln -s "$(pwd)" ~/.claude/skills/video-talkcraft   # Claude Code
# or
ln -s "$(pwd)" ~/.codex/skills/video-talkcraft    # Codex
```

Environment (the agent will set this up as needed):

- Node 18+ (Remotion render; `npm install` inside the per-video project)
- Python 3.10+
  - For local CPU timestamp alignment: `pip install zhconv pypinyin sherpa-onnx soundfile numpy`
    (downloads 767 MB FireRedASR2-CTC model once; or use `--backend whisper`)
  - For 1-step cloud TTS + timestamps (Fish Audio free tier): `pip install requests python-dotenv`
- ffmpeg

Then make requests like:

```text
Use video-talkcraft to turn this narration script + voiceover.wav into a video.
Make a 100-second explainer about <topic>; here is the script and the audio.
```

### 🎙️ Optional: Fish Audio voiceover + character timestamps

Finished voiceover plus local CPU alignment remains the default workflow. When you need to synthesize narration, opt into Fish Audio. The script requests `s2.1-pro-free` by default; free quota and model availability are controlled by Fish Audio.

1. Install `ffmpeg` and Python dependencies: `pip install requests python-dotenv`.
2. Copy `.env.example` to `.env` and set `FISH_AUDIO_API_KEY`. Optionally set `FISH_AUDIO_REFERENCE_ID` to a voice ID from the voice library; leaving it empty uses the service's default voice.
3. Prepare `script.json`, for example `{"sentences": ["First sentence.", "Second sentence."]}`. A JSON string array or a `.txt` file with one sentence per line also works.
4. Generate audio and timestamps:
   ```bash
   # Default: one request per sentence, with 0.25 seconds of actual silence inserted between requests
   python3 scripts/tts_fishaudio.py script.json audio/full.wav audio/timestamps.json --timing-out remotion/src/timing.json
   # One request for the whole script; retain the model's natural pacing
   python3 scripts/tts_fishaudio.py script.json audio/full.wav audio/timestamps.json --timing-out remotion/src/timing.json --mode stream
   ```

Both modes receive SSE audio and alignment snapshots. **Files are written after synthesis finishes; streaming playback is not implemented.** `--pause-sec` controls additional silence in sentence mode only. Each response is decoded to PCM before concatenation and encoding; offsets use actual decoded sample counts. `--format mp3|wav|opus` selects the API response format; the audio output extension selects the saved format.

Chinese characters retain API alignment spans; English character times are interpolated within each word, with zero-duration punctuation. Empty audio, missing/invalid alignment, decoding failures, and mismatched normalized text cause an error exit. Normalization ignores punctuation, case and character width; it does not guess spoken-number substitutions such as `2` versus `two`. Use spoken-form text for such cases, or use local CPU alignment with an existing recording. `match=1` / `ok=true` confirms text mapping, not pronunciation or independently verified timing accuracy; listen to the result.

Offline regression checks (no API key; requires `requests` and `ffmpeg`):
```bash
python3 -m unittest discover -s scripts -p 'test_*fish*.py' -v
```

## 🎞 What you bring vs. what it does

| You bring (inputs) | The skill does |
| --- | --- |
| Narration script | Word-level timestamp alignment, with per-sentence QA flags |
| Finished voiceover — any TTS or human recording | SHOTBOOK storyboarding: semantic beats, layer matrices, layout budgets |
| Optional host footage — ordinary video works (keying + face-zone tooling included; green screen keys cleanest) | Remotion implementation on four global systems (camera / parallax / yield / environment), transitions, SFX placement |
| Optional B-roll / screenshots | Render + triple-gate QA (machine gates all green + one independent review round with P0/P1 fixed, then deliver; optional extra rounds, 3 max), loudness-normalized delivery |

## 📦 What's included

| Content | Description |
| --- | --- |
| 108 motion recipe cards | Intent, energy, parameters, implementation notes, and known pitfalls — every card ships a self-contained Remotion tsx source (`template/cards/`, copy one file and go) plus a runnable HTML demo |
| Gallery | [Online](https://vincentwei1021.github.io/video-talkcraft/) or local (`open gallery/index.html`) — browse and autoplay all 108 previews, search by name/keyword |
| Motion systems | CameraRig (slow push/pull), yield lifecycle, six transitions, long-take world canvas; parallax and environment layer optional (`template/motion-systems/`) |
| Components | Plain-cut subtitles, flower-word titles, smash words, highlight sweeps, pencil draw, number rolls, eight video container frames (`template/components/`) |
| Pipeline scripts | Word-level timestamps (2 ASR backends), face-zone detection, stillness check, SFX presence check, QA frame extraction (`scripts/`) |
| Methodology | Design language (Apple-paradigm default), shot design worksheets, cinematography rules, storyboard format, QA rubrics (`references/`) |
| Embedded SFX | Per-card sound cue tables with real samples embedded in the demo lib (licenses in `demos/_lib/sfx/ATTRIBUTION.md`) |

## 🗂 Repository structure

```text
video-talkcraft/
├── SKILL.md                    # Agent entry point: the 8-step pipeline and hard rules
├── references/
│   ├── design-language.md      # Default visual system (palette/type/layout/subtitles)
│   ├── shot-design.md          # 3-plane worksheet + 7 shot-type presets
│   ├── cinematography.md       # 7-layer model, transitions, layout budget, QA gates
│   ├── shotbook-example.md     # A full storyboard example
│   ├── cards/                  # 108 motion recipe cards
│   ├── taxonomy.md             # Card index by category and source
│   ├── broll-sources.md        # Attribution-free stock sources (APIs, license traps)
│   ├── host-footage.md         # Host footage: input spec, keying, face safety zone
│   └── demo-spec.md            # Card/demo authoring spec
├── demos/                      # 108 runnable HTML previews (+ shared lib with embedded SFX)
├── gallery/                    # One-page local gallery
├── template/                   # Copy-paste Remotion code
│   ├── cards/                  # Per-card self-contained tsx sources (the skill's primary reference)
│   ├── motion-systems/         # Camera / parallax / yield / environment / transitions / long-take
│   └── components/             # Subtitles, flower words, smash words, pencil, etc.
└── scripts/                    # Timestamps, face bbox, QA tooling
```

For the full workflow, start at [SKILL.md](SKILL.md).

## ❓ FAQ

**What is video-talkcraft?**
An open-source AI agent skill (for Claude Code / Codex) that turns a narration
script plus a finished voiceover into a fully animated, voiceover-driven
explainer video. It is
not an editor and not a template site — the agent reads the methodology, picks
motion recipe cards, writes [Remotion](https://www.remotion.dev/) code, and
runs triple-gate QA to deliver a publish-ready explainer.

**What kinds of videos can it make?**
Landscape, voiceover-driven explainer videos: knowledge explainers, product
reviews, news breakdowns, opinion commentary. Designed Chinese-narration-first; mixed
Chinese/English narration is fully supported.

**What do I need to provide?**
A narration script (text) and a finished voiceover (any TTS or human
recording); host footage and B-roll are optional.

**Is it free?**
Free for personal, educational, and research use (PolyForm Noncommercial
1.0.0), and the videos you produce belong to you; commercial use of the
toolkit itself requires prior authorization (see below).

## 📄 License

[PolyForm Noncommercial 1.0.0](LICENSE) — free for personal, educational, and
research use. **Any commercial use of the toolkit requires prior
authorization** — email
[vincentwei1021@gmail.com](mailto:vincentwei1021@gmail.com) or open
a GitHub issue.

**Videos you produce with this skill belong to you.** If it helped, a mention
of the author's accounts in your video description is appreciated — and
entirely optional.

## 🔊 Audio and asset notes

- Embedded SFX samples: sources and licenses in
  [demos/_lib/sfx/ATTRIBUTION.md](demos/_lib/sfx/ATTRIBUTION.md).
- The B-roll sourcing guide only admits attribution-free stock (Pexels,
  Pixabay, Mixkit Free, Coverr, NASA) and documents the license traps of the
  ones it rejects — see
  [references/broll-sources.md](references/broll-sources.md).
- The demo host footage (`demos/_lib/dh-host.webm`) is an AI-generated
  presenter used as a placeholder; replace it with your own host footage in
  production.

## 🙏 Acknowledgements

- **[Remotion](https://www.remotion.dev/)** — the React video framework
  powering every render here (note its own
  [license](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md)).
- **[FireRedASR2](https://github.com/FireRedTeam/FireRedASR2S)** via
  **[sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx)** and
  **[faster-whisper](https://github.com/SYSTRAN/faster-whisper)** — the
  timestamp backends; **Qwen3-ASR/ForcedAligner** served as the benchmarking
  reference.
- **OpenCV YuNet** — the face detector behind the face-safety-zone rule.
- **Pexels · Pixabay · NASA · Mixkit** — attribution-free asset sources.
- **Claude Code** — this library was built, iterated, and QA'd with an AI
  coding agent, using the same review loops the skill teaches.

## Follow me

<p>
  <a href="https://x.com/VincentWei93"><img alt="Follow Vincent on X" src="https://img.shields.io/badge/X-Follow_Me-000000?style=for-the-badge&logo=x&logoColor=white"></a>
  <a href="https://www.douyin.com/user/MS4wLjABAAAAK1pkjBxilk2Oi_9h_vFyD-lTAu9CTlvhmOtkosDvvxg"><img alt="Follow Vincent on Douyin" src="https://img.shields.io/badge/Douyin-Follow_Me-000000?style=for-the-badge&logo=tiktok&logoColor=white"></a>
  <a href="https://xhslink.cn/m/At9iP2d5C1V"><img alt="Follow Vincent on Red Note" src="https://img.shields.io/badge/Red_Note-Follow_Me-FF2442?style=for-the-badge&logo=xiaohongshu&logoColor=white"></a>
</p>

<!-- ===== /file: video-talkcraft/README_EN.md ===== -->

<!-- ===== file: video-talkcraft/THIRD_PARTY_NOTICES.md ===== -->

# 第三方许可声明 / Third-party notices

本仓库自身的许可见 `LICENSE`（PolyForm Noncommercial）。下列第三方内容随仓库分发，其许可要求**版权与许可声明随副本保留**——
把对应文件复制进成片工程时，请把本文件一并带上（并在工程 `sources.md` 登记来源与授权）。
demo 用的示意视频 / 图片 / 音效的来源与授权见 `demos/_lib/media/ATTRIBUTION.md` 与 `demos/_lib/sfx/ATTRIBUTION.md`。

## Lucide icons（`template/motion-systems/icons.ts`）

`icons.ts` 由 `scripts/fetch_icons.py` 从 Iconify 的 `lucide` 集合抓取，把 path / circle / rect / line / polyline 统一转成 path d，
供 G5 线稿示意图系统（`schematic.tsx` 的 DrawIcon）逐段描画。图标形状即 Lucide 的图标；其中 arrow-right · check · clock · code ·
corner-down-right · link · minus · target · x 等源自 Feather，按下文 MIT 条款。以下为 Lucide 仓库 LICENSE 全文
（https://github.com/lucide-icons/lucide/blob/main/LICENSE，2026-09-07 取）：

```
ISC License

Copyright (c) 2026 Lucide Icons and Contributors

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

---

The following Lucide icons are derived from the Feather project:

airplay, alert-circle, alert-octagon, alert-triangle, aperture, arrow-down-circle, arrow-down-left, arrow-down-right, arrow-down, arrow-left-circle, arrow-left, arrow-right-circle, arrow-right, arrow-up-circle, arrow-up-left, arrow-up-right, arrow-up, at-sign, calendar, cast, check, chevron-down, chevron-left, chevron-right, chevron-up, chevrons-down, chevrons-left, chevrons-right, chevrons-up, circle, clipboard, clock, code, columns, command, compass, corner-down-left, corner-down-right, corner-left-down, corner-left-up, corner-right-down, corner-right-up, corner-up-left, corner-up-right, crosshair, database, divide-circle, divide-square, dollar-sign, download, external-link, feather, frown, hash, headphones, help-circle, info, italic, key, layout, life-buoy, link-2, link, loader, lock, log-in, log-out, maximize, meh, minimize, minimize-2, minus-circle, minus-square, minus, monitor, moon, more-horizontal, more-vertical, move, music, navigation-2, navigation, octagon, pause-circle, percent, plus-circle, plus-square, plus, power, radio, rss, search, server, share, shopping-bag, sidebar, smartphone, smile, square, table-2, tablet, target, terminal, trash-2, trash, triangle, tv, type, upload, x-circle, x-octagon, x-square, x, zoom-in, zoom-out

The MIT License (MIT) (for the icons listed above)

Copyright (c) 2013-present Cole Bemis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

<!-- ===== /file: video-talkcraft/THIRD_PARTY_NOTICES.md ===== -->

<!-- ===== file: video-talkcraft/references/broll-sources.md ===== -->

# 免费素材源（2026-08 实测验证 · 只收免署名源）

> **授权红线（2026-08-28 用户定版）：需要署名的 B-roll/配图源一律不接入**——
> Dareful、Wikimedia Commons 视频、Vecteezy、Openverse 等 CC BY 系全部排除。
> 唯一例外义务是 API 条款级的一行简介致谢（规则 3），那是 API 使用条款，不是素材授权署名。

## 推荐组合
- **实拍素材是必需项**（SKILL.md ③，2026-09-06 硬规）：全片零 B-roll / 图片 = 动效 + 口播人物 = 讲 PPT。视频找不到降级图片，图片也没有才进 SHOTBOOK「未完成 / 未采集清单」，
  不允许写成"本片不做 B-roll"的设计决定。`scripts/preflight.py` 对账。
- **视频 B-roll**：Pexels（主）→ Pixabay（备）→ Mixkit Free（逐条核对授权标签，见排除清单）→
  Coverr（接受其条款时；API 免费档只够开发用）→ NASA（航天/卫星/地球类）→ 无结果降级 **图片**（下一条）
- **图片**（照片 / 海报 / 插图，taxonomy 输入类型「图」；与视频同源同 key）：Pexels photos（**取 `original`**）→ Pixabay images（免费档长边上限 1280，只够 720p / 竖屏 / 配角小图）。
  采集规格见下文「配图采集」；表现侧规则已齐：证据素材白边卡 + 唯一投影 + Ken Burns（design-language §1/§5）、静态素材必由相机动起来（taxonomy 运镜类）、
  图片专用卡 stack-fan-out / gallery-wall-dolly / timeline-photo-strip / still-layout-relay / media-pop-in / grid-to-hero
- **logo/图标**：Iconify `logos:` 彩色 → simple-icons via jsDelivr 单色 → Wikimedia Commons（**只取 PD/CC0**，
  按 LicenseShortName 字段过滤）。单色 logo 注意底色适配：深色 logo（如 Anthropic #181818）深底模式不可直用，
  需白底卡承载或取反色变体
- **动效贴纸**：LottieFiles GraphQL（未文档化接口，做容错）
- **新闻类话题首选**：Playwright 实时抓取真实页面（GitHub/官网/榜单/HN），比泛用 B-roll 更有信息量——
  但成片里**不贴静态截图**：按下文「网页拍摄素材采集」采全页 2× 长图 + 坐标 JSON，交给滚/巡/放大/划四种拍法
  （SKILL.md §③、shot-design.md §2④）

## 领域路由（检索前先想去哪家）

| 领域 | 首选 |
|---|---|
| 人物生活 / 办公 / 城市 / 科技通用 | Pexels（现代审美强，数十万条） |
| 自然 / 延时 / 抽象与动画背景 | Pixabay（量最大 500 万+；API 支持 `lang=zh` 中文查询词） |
| 精选质感 / 竖屏 | Coverr、Mixkit Free（策展型，量小质高，均无可量产 API） |
| 航天 / 火箭 / 地球俯瞰 / 科研 | NASA（公有领域，实测 8,692 条视频，免 key API） |

## 分辨率下限与落盘（源表；此前"1080 优先"只写在 curl 注释里被读成能力上限，2026-09-06 提到这里）

运镜共有纪律：**素材分辨率 ≥ 画幅 × 最大缩放**（taxonomy 运镜；1080p 横屏缓推 1.15 → 宽 ≥2208px，1.8× 放大镜 → 3456px）。

| 源 | 取哪一档 | 横屏 1080p 够不够 | 落盘 |
|---|---|---|---|
| Pexels 视频 | `video_files[]` 里 height ≥1080 的 HD/UHD 直链 | 够（4K 可选） | `assets/broll/` 候选 → 选中后 `public/broll/` |
| Pixabay 视频 | `videos.large`（4K）或 `videos.medium`（1080） | 够 | 同上 |
| Mixkit 视频 | `{id}-1080.mp4` **优先**，无则 `-720`（720 只够竖屏 / 配角） | 1080 够；720 不够放大 | 同上 |
| NASA 视频 | manifest 里 `~orig` 原始 mp4 | 够 | 同上 |
| Pexels 图片 | `src.original`（全尺寸；`large2x` 只有 1880 宽） | 够 | `assets/stills/` 候选 → `public/stills/` |
| Pixabay 图片 | `largeImageURL`（长边 ≤1280；`fullHDURL` / `imageURL` 需申请 full API access） | **不够**缓推，只当 720p / 竖屏 / 小图配角 | 同上 |
| 网页长图 | Playwright 全页 2×（下文） | 够 | `public/pages/<slug>/` |

## 关键请求格式
```
# Mixkit Free（无 API，但列表页可免 key 解析直链——2026-08-31 实测；逐条核对授权标签）
#   curl -sL "https://mixkit.co/free-stock-video/<关键词>/" -H "User-Agent: Mozilla/5.0" \
#     | grep -oE 'https://assets\.mixkit\.co/videos[^"]*\.mp4'      # {id}-1080.mp4 优先，无则 -720
#   标题↔id 对照：同页 href="/free-stock-video/<slug>-<id>/" 的 <a> 文本；Pexels/Pixabay 无 key 时的首选兜底

# Pexels 视频（Header: Authorization: <KEY>，200次/时 + 20,000次/月）
GET https://api.pexels.com/v1/videos/search?query=data%20center&orientation=portrait&size=medium&per_page=15
# 下载 video_files[].link（按档给直链 mp4，SD/HD/4K）

# Pixabay 视频（?key=<KEY>，100次/分钟，必须落盘禁热链——返回 URL 有时效）
GET https://pixabay.com/api/videos/?key=<KEY>&q=server+room&per_page=20&safesearch=true
# 四档 videos.large(4K)/medium(1080)/small/tiny；支持 &lang=zh

# Iconify 彩色 logo（免 key）
GET https://api.iconify.design/logos/openai.svg
# simple-icons 单色（注意 cdn.simpleicons.org 会被 Cloudflare 拦 curl，走 jsDelivr）
GET https://cdn.jsdelivr.net/npm/simple-icons@v16/icons/anthropic.svg
# 注意：openai 已从 simple-icons 下架，用 Iconify logos: 集合

# LottieFiles（免认证 GraphQL，字段可能变动）
POST https://graphql.lottiefiles.com/
{"query":"{ searchPublicAnimations(query:\"confetti\", first:5) { edges { node { name jsonUrl } } } }"}

# NASA（免 key，公有领域；item 的 collection.json manifest 里有 ~orig 原始高清 mp4）
GET https://images-api.nasa.gov/search?q=satellite&media_type=video
```

## 配图采集（图片作为正式素材的采集侧，2026-09-06；表现侧规则在 design-language / taxonomy）

```
# Pexels 图片（Header: Authorization: <KEY>，与视频同 key、同配额 200 次/时）
GET https://api.pexels.com/v1/search?query=data%20center&orientation=landscape&size=large&per_page=15
# 下载 photos[].src.original（全尺寸）；large2x=1880 宽只在竖屏/小图时够用。photos[].width/height 直接给真实尺寸，落盘前按上表核下限

# Pixabay 图片（?key=<KEY>，100 次/分钟，24h 缓存条款同视频）
GET https://pixabay.com/api/?key=<KEY>&q=server+room&image_type=photo&orientation=horizontal&min_width=1920&per_page=20&safesearch=true
# 免费档只给 largeImageURL（长边 ≤1280）——min_width 过滤的是原图尺寸，下载到的仍是 1280 版；不够横屏缓推，只当备选
```
- 检索词与视频同一套英文视觉概念词（规则 1）；同一镜头**先搜视频再搜图片**，图片是降级不是并列首选（图片撑镜头要靠相机动，视频自带运动）。
- 落盘 `assets/stills/`（候选）→ 选中的进 `public/stills/`，文件名 `<镜号>-<概念词>-<源>-<id>.<ext>`。
- **每张图和每条视频一样进 `sources.md`**（规则 6）：检索词、源站、ID/URL、授权、真实尺寸。
- 竖图放横屏、只有一张图的镜头：`bed-echo-blur◉`（同源模糊底床）是标准答案；多图：`still-layout-relay◉` / `stack-fan-out◉` / `gallery-wall-dolly◉` / `timeline-photo-strip◉`。

## 规则
1. **搜索词一律英文**（唯一例外：Pixabay API 的 `lang=zh`）：中文口播稿分镜 → LLM 翻译成
   2-3 个英文视觉概念词（"大模型训练"→ `data center` / `GPU computing`）
2. 素材全部下载到项目 `assets/`/`public/` 本地化（确定性渲染 + Pixabay 24h 缓存条款）
3. 视频简介放一行 "Video assets from Pexels & Pixabay"（Pexels API 条款要求页面某处有致谢链接；
   这是 API 义务不是素材署名）
4. logo 只做"指代品牌"使用（新闻/评论合理使用），不暗示背书
5. Internet Archive 大陆网络不可达，不接入；Unsplash 需 production 审批 + 打点义务，不默认接入
6. 选中的每条 B-roll **和每张图片** 在 `sources.md` 登记：检索词、源站、素材 ID/URL、授权、真实尺寸（与调研截图记账同一张表）；
   `preflight.py` 查 sources.md 是否存在

## 已排除源与死站（2026-08-28 调研，防旧教程误引）
- **Videvo / Mazwai 已死**：域名 301 → Magnific（前 Freepik），免费层强制署名——不接入
- **Vecteezy 免费层**：署名 + $1,000 项目预算帽——不接入
- **Dareful**：4K 风光好但 CC BY 要署名——不接入
- **Wikimedia Commons 视频**：多数 CC BY / BY-SA 要署名（BY-SA 还传染），且只有 webm 需转码——
  B-roll 不接入；仅 logo 检索时取 PD/CC0 文件
- **Mixkit 双轨坑**：同站混放 Free License（可商用免署名，含 monetized YouTube）与
  Restricted License（仅个人非商用，明文禁 monetized YouTube/广告）——逐条核对页面授权标签，
  标 Restricted 的不下载；无 API
- **Coverr API**：免费档 50 calls/h 且限开发环境，production 档收费；条款另禁 AI 训练用途（做视频不受影响）

## 网页拍摄素材采集（Playwright，2026-09-04 定版）

成片里的网页是被"拍"的（滚 / 巡 / 放大 / 划，选型表见 shot-design.md §2④「网页拍摄」），不是贴上去的截图——
所以采集物不是一张 PNG，而是**一张全页 2× 长图 + 一份同会话 DOM 实测的坐标 JSON**，一起落 `public/pages/<slug>/`。

- **全页 + 2× DPR**：`fullPage: true` + `deviceScaleFactor: 2`（视口宽 1280 → 长图宽 2560）。放大镜 1.8×、缓推 1.15、
  巡游 zoom 都吃这张图；运镜共有纪律"素材分辨率 ≥ 画幅 × 最大缩放"（taxonomy.md 运镜）只有 2× 才够，1× 图一放大即糊
- **坐标同会话实测**：截图前对每个要停 / 要放大 / 要划的目标取 `getBoundingClientRect()` + `scrollX/Y`，写成页面 CSS px 坐标
  （选择器命中多个时取首个 w/h>0 的可见元素——隐藏导航里的零尺寸副本是实测撞过的坑），
  连同 `dpr`、视口宽、页高存 `targets.json`——放大镜 `px/py`、荧光笔落点、滚动停点 `stopY` 全从这里读，**禁目测**
  （SKILL.md §③ 2026-09-01 定版）。Remotion 里换算：图像像素 = CSS px × dpr，再乘 卡内容宽 / 长图宽 + 卡内边距
  （shot-design.md §2④ 几何公式）
- **截前清场**（长截图三大穿帮源）：`position: fixed/sticky` 的头部 / 侧栏改 `static`（否则全页图里粘性头重复出现或盖住正文）；
  关掉 cookie / 登录 / 订阅弹层；懒加载图先把页面滚到底再回顶（否则长图下半截是灰占位块）
- **字体与语言**：`locale: 'zh-CN'` + 等 `document.fonts.ready`，避免中文回退成宋体或方块
- **记账**：`sources.md` 该条同时登记 URL、抓取时间、长图与 `targets.json` 路径——它既是成片素材也是调研证据存档
  （"禁止只存链接"同一张表）
- **不用浏览器录屏当素材**：录屏帧率不稳、懒加载 / 粘性头穿帮、无法对齐字级时间戳；滚动与运镜一律由 Remotion 在长图上做（seek-safe）

```js
// 最小采集脚本（node ≥18，需 playwright）：node capture.mjs <url> <slug> [css选择器 ...]
// 产出 public/pages/<slug>/page.png（全页 2×）+ targets.json（选择器 → 页面 CSS px 坐标）
import { chromium } from "playwright";
import { mkdirSync, writeFileSync } from "node:fs";
const [url, slug, ...sels] = process.argv.slice(2);
const dir = `public/pages/${slug}`; mkdirSync(dir, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 2, locale: "zh-CN" });
await page.goto(url, { waitUntil: "load" });
await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {}); // GitHub 类长连接站点等不到 idle 就继续（实测会 30s 超时）
// 清场：滚到底触发懒加载 → 回顶 → 等字体 → 粘性/固定元素改 static（evaluate 一律传字符串，见 scripts/shot-at.mjs 注释）
await page.evaluate(`(async () => {
  for (let y = 0; y < document.documentElement.scrollHeight; y += 800) { scrollTo(0, y); await new Promise(r => setTimeout(r, 120)); }
  scrollTo(0, 0); await document.fonts.ready;
  for (const el of document.querySelectorAll("*")) { const p = getComputedStyle(el).position; if (p === "fixed" || p === "sticky") el.style.position = "static"; }
})()`);
// 取首个「可见」命中（w/h>0）：GitHub 一类站点同一链接在隐藏导航里还有一份零尺寸副本，querySelector 会先撞上它
const targets = await page.evaluate(`(sels => sels.map(s => {
  const el = [...document.querySelectorAll(s)].find(e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; });
  if (!el) return { sel: s, missing: true };
  const r = el.getBoundingClientRect(); return { sel: s, x: r.x + scrollX, y: r.y + scrollY, w: r.width, h: r.height }; }))(${JSON.stringify(sels)})`);
const pageH = await page.evaluate("document.documentElement.scrollHeight");
await page.screenshot({ path: `${dir}/page.png`, fullPage: true });
writeFileSync(`${dir}/targets.json`, JSON.stringify({ url, capturedAt: new Date().toISOString(), viewport: 1280, dpr: 2, pageH, targets }, null, 2));
await browser.close();
console.log(`${dir}/page.png  ${pageH}px 高  targets=${targets.length}`);
```

<!-- ===== /file: video-talkcraft/references/broll-sources.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/alt-block-lines.md ===== -->

---
name: alt-block-lines
标题: 双色块对句
优先级: P1
代码: template/cards/alt-block-lines.tsx
一句话: 两行对句各坐在自己的色块上、块宽贴合各自文字，两行错峰 0.12s——每行色块从左 scaleX 展开 0.26s，文字用 clip-path 从右侧收 100%→0 同曲线同时长**滞后 2 帧**跟着被块的右缘"刷"出来；对句关系靠同结构反色表达（块1 实色白字 / 块2 白底黑字 + 1px 灰描边）
适用: 口播里的两句对照——"先做减法 / 再做加法"、"不是 A / 而是 B"、"以前 X / 现在 Y"；方法论型、有编辑气质的知识区口播；也可当双行小标题
时长: 起手静置 0.4s → 第一行块展开 0.26s（字滞后 2 帧跟随）→ 第二行错峰 0.12s 起、同样 0.26s → 收尾定格 1.8s；共约 2.58s
能量: 中
类别: 字幕花字
输入: 文, 人(可选)
语义: 对比, 论点, 列举
素材形态: 无
位置: 任意
props: hostSrc
---

## 意图
对句的难点是**让两行读作一组而不是两条**。最省事的做法是两行各自淡入、错峰一下——
结果观众读到的是"一行字，然后又一行字"，两句之间的**对照关系**要靠文案自己去说。

这张卡把关系交给形式来说，两个手段：
① **同结构反色**——两行的块结构完全一样（一样的圆角、padding、字号、展开方式），
只有明暗反过来（块1 实色 + 白字 / 块2 白底 + 黑字 + 1px 灰描边）。
"同结构"让它们是一组，"反色"让它们是一对。
② **块刷出字**——文字不是自己淡入的，是被色块的右缘刷出来的。
两条轨同曲线、同时长、字滞后 2 帧，观众读作**一个**动作（一道色扫过，字跟着显形），
而不是"块展开 + 字淡入"两个动作。

命门一条：**文字必须被块"刷"出来（clip 跟随），不许块和字各自淡入**。
块和字各自淡入的版本里，块在字的下面独立跑完，字在块上独立跑完——
慢放下能看到"字已经在了，块还没铺到那里"，那一帧就是假的。
clip 跟随保证字的显形边缘**永远落在块的右缘之后**，物理上说得通。

## 动效核心
- **每行两条轨，是同一件事的两半**：
  - 轨① 色块：`scaleX 0 → 1`，`transform-origin: 0% 50%`（**从左展开**），`0.26s power3.out`
  - 轨② 文字：`clip-path: inset(0 100% 0 0) → inset(0 0% 0 0)`（右侧的裁切量 100% → 0），
    **同曲线（`power3.out`）同时长（0.26s）**，起点滞后 `0.067s`（2 帧 @30fps）
  - 两条轨的曲线与时长必须完全一致：换了任一个，字的显形边缘就会与块的右缘"错开又追回"，
    读作两个元素在赛跑
- **滞后 2 帧是这个卡的全部手感**：0 帧则字的边缘与块的右缘完全重合（读作块本身带着字，
  像一张色块 PNG 在展开）；>5 帧则块已经铺完一截而字还没出来（读作"块是块、字是字"）。
  2 帧刚好让字始终"在块里面一点"，物理上是"油墨还没干"的那点滞后
- **两行错峰 0.12s**：小于 0.08s 两行读作一次展开（对句关系丢了）；
  大于 0.25s 两行断成两个动效（"一行字，然后又一行字"，回到了要解决的问题）
- **同结构反色的实现纪律**：两行共用 `.ab-row` 的全部结构（padding / 圆角 / origin / 时序），
  只有两条 CSS 规则不同 —— `.ab-row.a` 的块是实色 + 白字，`.ab-row.b` 的块是白底 + 黑字 +
  `box-shadow: inset 0 0 0 1px #d8d8d8`（**用 inset shadow 而不是 border**：
  border 会改变元素盒模型尺寸，两行的块高就差 2px，"同结构"当场破掉）
- **块宽贴合各自文字**：`.ab-row` 是 `inline-block`，宽度由文字撑出。
  两行字数不同时块宽自然不同——这是参考图的构图特征（不是 bug），
  两块等宽会读作"表格的两个单元格"
- **两块左对齐**：`.ab-stack` 用 `align-items: flex-start`。左对齐是"两句并列"的骨架；
  居中对齐会让两块成为一个居中的图形组（读作 logo 而不是对句）
- **DOM 三层**：`.ab-row`（相对定位 + padding）→ `.ab-bg`（绝对定位铺满，唯一被 `scaleX` 的元素）
  + `.ab-t`（相对定位压在 bg 之上，唯一被 `clip-path` 的元素）。
  两个动画属性作用在两个不同元素上，互不干扰
- **层级**：舞台白底 → 两行的 flex 列 → 每行：块 bg（z 底）→ 文字（z 上，被 clip）
- **强调色只上在第一个块上**：`#0aa3a3`（参考图青系）。第二个块是白底 + 灰描边 + 黑字——
  全卡只有一个彩色元素

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `textLag` | 0.067s（2 帧） | **本卡命门**，字相对块的滞后；0 则块与字边缘重合（读作一张色块 PNG 在展开），>0.17s 块铺完一截字还没出（块和字变成两个物件） |
| `dur` | 0.26s | 单行展开时长（块与字共用），能量旋钮；<0.16s 读作硬切揭示（"刷"这个动作没了），>0.4s 观众等着一行开完、口播已经念到第二句 |
| 缓动 | `power3.out`（两轨同一条） | 块与字**必须同一条**；块用 power3 字用 power2 立刻能看出两者边缘错开又追回，读作赛跑 |
| `rowStagger` | 0.12s | 两行错峰；<0.08s 两行读作一次展开（对句关系丢），>0.25s 断成两个动效 |
| 两行 gap | 16px（≈字号 24%） | 两块之间的垂直间距；<字号 12% 两块粘成一个色块组，>字号 45% 读作两个独立标题 |
| padding | 11/24/13 px @66px | 块比字大一圈的量；左右 <14px 字贴块边（像被裁），>34px 块空得像色条；下比上多 2px（中文视觉重心偏上） |
| 描边（块2） | `inset 0 0 0 1px #d8d8d8` | 白块的边界；**必须用 inset shadow 不用 border**（border 改盒模型，两行块高差 2px）；去掉则白块在白底上没有边界，第二行读作"没有块" |
| `hold` | 1.8s | 收尾定格——**对句要停久**，两行都读完才成"对句"；<1.2s 观众只读了第一行 |
| 字数 | 每行 3~6 字 | 两行字数可以不等（块宽跟着不等，那是构图特征）；>7 字块会长得压过安全区，且"对句"的对称感消失 |

## 已知坑
- 块和字各自淡入（省掉 clip 跟随）——慢放下能看到"字已经在了，块还没铺到那里"，一眼假；这是两个动效不是一个。
- 文字用 `opacity` 从左往右逐字淡入（想模拟"刷"）——逐字是离散的，块的右缘是连续的，两者永远对不上；`clip-path` 是唯一对得上的实现。
- 块与字用不同的缓动或不同的时长——字的显形边缘与块的右缘"错开又追回"，读作两个元素在赛跑。
- 滞后写成 0（字与块边缘完全重合）——读作一张带字的色块 PNG 在展开，"刷出来"这个动作消失。
- 块用 `width: 0 → 100%` 而不是 `scaleX`——改 width 每帧重排，块内的字会跟着一帧一帧挤动（而且 clip 的基准也在动，两者叠加后字会抽动）。
- 块从中心展开（`transform-origin: 50% 50%`）——那是 `slab-punch-title` 的语言，且从中心展开时"右缘"是往右跑的同时左缘往左跑，clip 跟随（只裁右侧）就对不上了。
- 第二行的白块用 `border: 1px` 而不是 `inset box-shadow`——border 参与盒模型，第二行的块比第一行高 2px、宽 2px，"同结构反色"当场破掉。
- 两块做成等宽（给固定 width 或 `align-items: stretch`）——读作表格的两个单元格，不是两句话。
- 两块居中对齐——成为一个居中的图形组（读作 logo），"两句并列"的骨架塌了。
- 两行都用实色块（只换色相，比如青块 + 橙块）——违反唯一强调色红线，而且两个实色块读作"两个标签"而不是一对；反色（实/虚）才是"对"。
- 第二行的黑字换成灰字（想做"弱一点"）——对句的两句是**对等**的，不是主次；灰字立刻读作"注释"。
- `rowStagger` 给到 0.3s 以上再配长 hold——两行之间空太久，观众读完第一行开始等，第二行来时已经不是"对句"而是"补充"。

## 复用指引
- props：仅 `hostSrc`；两行文案在 JSX 常量 `ROWS` 里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/alt-block-lines.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/alt-block-lines/index.html。**换文案改两处 HTML 文本**（两个 `.ab-t` 各 3~6 字）——
  块宽由字自动撑出，两行字数可以不等。
  换强调色改一处：`.ab-row.a .ab-bg` 的 `background`（青 `#0aa3a3` / 紫 `#7A5AF8` / 红 `#e0452c` 任取）。
  换字号改 `.ab-t` 的 `font-size`，同时按比例改 `.ab-row` 的 padding 与 `.ab-stack` 的 `gap`（约字号 24%）。
  能量只调 `dur`；`textLag`（2 帧）与 `rowStagger`（0.12s）是手感常量，换尺寸换语速都不要动。
  **加第三行**：直接在 `.ab-stack` 里再加一个 `.ab-row`（脚本按 `[data-bg]`/`[data-t]` 自动遍历，
  错峰序列是运行时算的）——但三行以上就不是"对句"了，语义上该换 `line-by-line-slide`。
- Remotion 移植：`clip-path` 在 Remotion（Chromium）里完全可用——用模板字符串拼出
  `clipPath = "inset(0 " + (100 - p * 100) + "% 0 0)"`，其中
  `p = interpolate(f, [start + 2, start + 2 + 8], [0, 1], {easing: Easing.out(Easing.cubic), extrapolateLeft:'clamp', extrapolateRight:'clamp'})`。
  30fps 换算：`lead 12f`、`dur 7.8f≈8f`、`rowStagger 3.6f≈4f`、`textLag 2f`。
  **块与字必须共用同一个 `easing` 常量**（提成一个 `const EASE = Easing.out(Easing.cubic)` 传给两处），
  这是"同一件事"的实现保证。块 `transform: scaleX(...)` + `transformOrigin: '0% 50%'`。
  `extrapolateLeft: 'clamp'` 不能省——不 clamp 的话第二行在自己起点前会算出 `inset(0 130% 0 0)`，
  Chrome 里负宽度的 clip 行为未定义。
- 剪辑软件对应物：剪映/CapCut——每行做成"色块贴纸 + 文本层"两层，
  色块打"缩放"X 通道 0 → 100（锚点设左边缘，剪映要在"编辑-锚点"里改）；
  文字层套**"蒙版-线性"**（把蒙版旋转 90° 变成竖直边缘）并给蒙版位置打关键帧从右扫到左，
  起点比色块晚 2 帧、时长与色块相同。第二行整组复制后错后 4 帧、把色块换成白色描边款。
  **剪映的"擦除"入场预设不要用**——它是给整个层擦的，擦不出"块在下、字在上、字跟着块的右缘"这个关系。
  AE——色块层 `Scale` X 通道 0 → 100（`Anchor Point` 移到左边缘）；
  文字层加 `Linear Wipe`（`Wipe Angle` 270°、`Transition Completion` 100 → 0），
  两层的关键帧用**同一组 Easy Ease** 且文字层整体后移 2 帧；两行做成两个预合成，第二个后移 4 帧。
- 与本库同类卡的分工：`slab-punch-title` = 一行铺垫 + 一行重点，块**从中心撑开**且字**砸**出来（语义是结论的重量）；
  `highlighter-sweep` = 荧光笔扫过**已经在屏上**的字（字先在、色后到，块在字下层且半透明）；
  `line-by-line-slide` = 多行依次滑入（3 行以上的列表/段落，无块无反色）；
  `type-contrast-emphasis` = 一句里靠字体气质砸重音（无块）；
  **本卡 = 两句对照关系的可视化**，特征是"同结构反色"+"块刷出字"，
  它不做强调（两句对等），做的是**关系**。

## 动效范围
- 属于本卡的：文字必须被色块的右缘"刷"出来这条纪律——`clip-path: inset()` 与块的 `scaleX` **同曲线、同时长、滞后 2 帧**（`textLag 0.067s` 这个"油墨没干"的量级）；块 `transform-origin: 0% 50%` 从左展开这个方向；两行错峰 `0.12s`（"一组"与"两条"之间的窗口）；同结构反色表达对句关系（两行共用全部结构参数，只有明暗相反；白块用 **inset shadow 而非 border** 以保证盒模型一致）；块宽各自贴合文字（两行不等宽是构图特征）+ 两块左对齐；DOM 三层分工（padding 层 / 唯一被 scaleX 的 bg / 唯一被 clip 的字）；`hold 1.8s` 这个"对句要停到两行都读完"的时长纪律。
- 不属于本卡的：demo 那两句「先做减法 / 再做加法」的具体文案、66px 字号与 700 字重、`#0aa3a3` 这个青（同色系任取）、白块描边的 `#d8d8d8` 这个灰阶、`padding: 11/24/13` 这组像素与 4px 圆角、两行 16px 的 gap、右侧主持人（数字人）占位、以及"两行落在左侧白区、左边距 82px、垂直居中"这个落位（下三分之一、居中都成立）。
- 迁移接口：内容入口是两段纯文本（各 3~6 字，字数可不等），块宽自动贴合不需要量宽；能量只调 `dur`（0.16~0.4s）；`textLag`（2 帧）与 `rowStagger`（0.12s）是手感常量，换尺寸换语速都不要动；换字号时 `font-size`、`.ab-row` 的 padding、`.ab-stack` 的 `gap`（字号 24%）按同一比例缩放；换强调色只改 `.ab-row.a .ab-bg` 一处；`hold` 按两行总字数给（每字约 0.2s，且不少于 1.2s）；行数可扩到 3 行（脚本自动遍历）但语义上就不再是对句；竖屏把字号收到 48~56px（本卡没有横向推挤，唯一约束是较长那行的块不超过可用宽度的 88%）。
- 底色要求：白底即可——**第二行的"白底黑字"块依赖白底才成立**（它是"底色本身"充当块，靠 1px 灰描边划出边界）。换深底时这个反色对必须整体重做：块1 用强调色 + 白字不变，块2 改成"深底同色 + 白字 + 1px 亮边"（即在深底上做同样的实/虚对比）。**渐变底与实拍花底不行**：白块靠 1px 灰描边定边界，底上任何高频细节都会把这条线吃掉，第二行会读作"没有块"。

<!-- ===== /file: video-talkcraft/references/cards/alt-block-lines.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/bar-chart-growth.md ===== -->

---
name: bar-chart-growth
标题: 柱状增长
一句话: 标题淡入后基线从左画出 0.24s 立好地面，七根柱以 0.06s 的密错峰从基线一路升起（读作一次连续动作而不是七个动效），最后一根到顶那一帧结论 chip 在柱顶留白里弹出
适用: 口播讲一个连续区间的增长/下滑趋势（"半年翻了一倍"、"从 1 月到 7 月一路涨"）；需要"整体形状"而不是"逐项对比"的数据段；节奏偏快的口播（整组 1.0s 内长完，跟得上语速）
时长: 静置 0.3s → 基线 0.24s → 七柱 0.06s×6 + 0.28s = 0.64s → chip 0.2s → hold 1.8s；共约 3.2s
能量: 中
类别: 数据信息图
输入: 文, 人(可选)
语义: 数据
素材形态: 无
位置: 任意
props: hostSrc
优先级: P0
代码: template/cards/bar-chart-growth.tsx
---

## 意图
柱状图有两种读法：**逐项对比**（这几年谁高谁低）和**整体形状**（这条线在往上走）。
本库已有的 `chart-grow` 做的是前者——5 根柱、错峰 0.13s、每根柱顶带数值、最高柱换色高亮，
观众被引导着**一根一根读**，那是"念数据"的语感。

这张卡做的是后者。区别在三处，缺一处就变回 `chart-grow`：
- **柱多（7 根）、错峰密（0.06s）**——0.06s × 6 = 0.36s，整组在 0.64s 内长完，
  肉眼读作**一次连续的抬升**（像一道波扫过去），不是七个先后事件。
- **柱顶不带数值**——单根柱的值不重要，重要的是这一排的**斜率**。柱顶挂七个数字
  就把观众拉回"逐项读"，形状语义直接消失。
- **结论收在一个 chip 上**——「增长 42%」这一句才是要被复述的东西，它替代了七个数值。

命门两条：
① **柱子只用 `scaleY`**。改 `height` 每帧触发重排，7 根柱 × 60fps 下会掉帧；
更要紧的是 `scaleY` 配 `transform-origin: 50% 100%` 才有"从地里长出来"的语义，
改 height 是"柱子被拉长"（顶部在动，底部也在重算）。
② **最高柱要留顶部余量给 chip**。chip 的 `bottom` 由**最高柱的实际像素高度**算出
（`maxH + chipGap`），不是写死的 CSS 值——换一组数据后 chip 自动跟着抬，永远压不到柱顶。
写死了就必然有一天压上去。

## 动效核心
- **层级**（自下而上）：白舞台 → 标题（34px/600 黑）→ 柱组容器（`display:flex; align-items:flex-end;
  justify-content:space-between`，高度 = 量程）→ 基线（2px 灰，`transform-origin: 0% 50%`）→
  x 轴月份标签（灰 13px）→ 结论 chip（绝对定位，`right: 0`，`bottom` 由 JS 算）。
  主持人占位在右侧 47%，图表块左对齐在 96px。
- **① 标题**：`opacity 0→1`，0.2s `power2.out`，`t = 0.30`。
- **② 基线**：`t = 0.42` 起，`scaleX 0→1`（`origin left`），0.24s `power2.out`。
  **先有地面柱子才能"长出来"**——没有基线的柱子读作"七个矩形淡入"。
- **③ 七根柱**：`t = 0.62 + i × 0.06`，每根 `scaleY 0→1`，0.28s `power3.out`，
  `transform-origin: 50% 100%`。柱高在 `register` 里按 `dataset.v / maxVal × 容器高` 换算成
  **像素 height 写进 style**（这一步是布局，不是动画），动画只动 `scaleY`。
- **④ 结论 chip**：`lastTop = 0.62 + 6×0.06 + 0.28 = 1.26`，
  `opacity 0→1` + `scale 0.8→1`，0.2s `back.out(1.4)`，`transform-origin: 100% 50%`
  （从右端展开——chip 右对齐，从自己的锚点长出来）。
  `back` 的回弹量刻意压到 1.4（不是漫画感的 2.2）：这是"结论落章"不是"弹跳"。
- **⑤ hold 1.8s**：整图静置。
- **量程固定**：`maxVal = 100` 全程不变。中途改量程（比如按当前最大值动态归一）
  柱子之间的对比就是骗人的。
- **唯一语义色 `#e8720c`（橙）**：只上在柱体和 chip 上。标题黑、基线 hairline、月份灰。
  **七根柱同色**——`chart-grow` 那种"最高柱换色"在这里是错的：换色 = 指认一项，
  和"看整体形状"的意图相反。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `barStagger` | 0.06s | **本卡第一命门**；>0.1s 读作"七个动效"（回到 `chart-grow` 的逐项语感），0 则整排同时起立、读作一块阶梯形色块被推上来（没有方向） |
| 柱数 | 7 | 5 根以下"形状"不成立（该用 `chart-grow` 做逐项对比），>10 根柱宽被压到 20px 以下、读作条形码 |
| `barGrow` | 0.28s | 单柱升起时长；<0.18s 柱子"闪"出来（看不见生长），>0.45s 单柱的动作盖过整组的错峰节奏 |
| `barEase` | `power3.out` | 起步猛尾段缓，柱顶有"顶到位"的手感；`power1.out` 太软读作充气，`back.out` 柱顶过冲一下读作弹簧（数据不该弹） |
| `baseDur` | 0.24s | 基线画出；0（基线一开始就在）也成立但少了"先立地面"这一拍，>0.4s 观众在等一条灰线画完 |
| `chipGap` | 18px | chip 底边距最高柱顶的留白；<10px 视觉上贴到柱顶（读作柱子的标签而不是结论），>40px chip 飘在空中和图脱开 |
| `chipPop` | 0.2s | 结论落定；>0.35s 结论来得软，抵不住前面七柱的动势 |
| `back.out(1.4)` | 1.4 | chip 的回弹量；>2 读作漫画弹跳（数据卡不该有的语言），1.0（= 无回弹）则少了"落章"的确认感 |
| `maxVal` | 100 | 量程，**全程固定**；改成"按当前最大值动态归一"柱间对比立刻失真 |
| `hold` | 1.8s | 收尾定格；chip 那句话要读完，<1.2s 观众只看到图没看到结论 |

## 已知坑
- 柱子动 `height` 而不是 `scaleY`——每帧重排，7 根柱在 60fps 下掉帧；且顶部与底部同时重算，
  读作"矩形被拉长"不是"从地里长出来"。
- chip 的 `bottom` 写成固定 CSS 值——换一组数据后最高柱抬高，chip 直接压在柱顶上（本卡最常见的翻车）。
  必须由最高柱的实际像素高度算出。
- 错峰放大到 0.13s 还叫它"柱状增长"——那已经是 `chart-grow` 的逐项列举语感，整体形状读不出来了。
- 柱顶挂七个数值——观众被拉回"一根一根读"，形状语义消失；本卡的数值只有 chip 上那一个。
- 最高柱换成另一个色高亮——"指认某一项"和"看整体趋势"是相反的意图，换色就散架。
- chip 在柱子还在长的时候就弹出——结论比数据先到，读作数是往结论上凑的。
- 忘了基线直接长柱——七个矩形在白底上淡入，没有"地面"就没有量级参照，读作装饰色块。
- 柱间距用 `justify-content: space-around` 且不给 x 标签同宽——柱和月份标签对不齐，
  慢放一眼看出（demo 里柱与标签都固定 44px 宽 + `space-between`，天然对齐）。
- 语义色上到标题上——`design-language.md` §1 红线：positive/negative 与图表色只进图表本体，
  标题一律 ink 黑。
- hold 期给柱子加呼吸/微抖——数据是结论，抖起来读作"还在算"（§4 禁的定格抖动之外，
  连续微动在这里也不合语义）。

## 复用指引
- props：仅 `hostSrc`；数据 / 月份 / 文案在 `BARS` / `MONTHS` 与 JSX 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/bar-chart-growth.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：`demos/bar-chart-growth/index.html`。**换数据只改 HTML 里七个 `.bar` 的 `data-v`**
  （0~`maxVal`），柱高、chip 落位都是运行时按容器高度算的；换文案改 `.title` / `.grow-chip` /
  `.xlabels`。柱数增减：HTML 里加减 `.bar` 与对应 `.xlabels span`（两边数量必须一致，
  `space-between` 才对齐），`barStagger` 按"整组 ≤0.4s"反算（10 根柱 ⇒ 0.045s）。
  做下滑趋势：`data-v` 递减 + `CONFIG` 里颜色换 `#d70015`、chip 文案改「下滑 38%」，
  时序一个字不用改（本卡的动效对方向无感）。
- Remotion 移植：柱子逐帧算 `scaleY`，不建时间线：
  `const p = interpolate(t, [0.62 + i*0.06, 0.62 + i*0.06 + 0.28], [0, 1],
  {easing: Easing.out(Easing.cubic), extrapolateLeft:'clamp', extrapolateRight:'clamp'})`，
  样式 `transform: scaleY(${p})` + `transformOrigin: '50% 100%'`。
  `clamp` 不能省——不 clamp 的话 `t` 在起点前会算出负 `scaleY`，柱子会往地面下方翻出来。
  chip 的 `bottom` 在组件里用 `Math.max(...values) / maxVal * chartH + chipGap` 算（和 demo 同式子）。
  基线用 `scaleX` + `transformOrigin: 'left center'`。
- 剪辑软件对应物：剪映/CapCut——七个矩形形状层，各打"缩放 Y" 两键（0→100%），
  **锚点必须拖到矩形底边**（剪映默认中心锚点，从中间往两边长 = 完全另一个动效），
  入点按 0.06s（约 2 帧 @30fps）逐层往后推；chip 一层做"缩放弹入"。
  七层 × 2 帧的手工排列在剪映里很枯燥，但**错峰值不能为了省事拉大**，那是本卡的命门。
  AE——一个 Shape Layer 里七个 Rectangle，或用 `Scale` 属性 + `Anchor Point` 移到底边；
  更省事的做法是七个层套一个 `Sequence Layers`（Keyframe Assistant）设 0.06s 偏移；
  chip 用 `Scale` 两键 + `Easy Ease` 再把手柄拉出一点过冲（≈ `back.out(1.4)`）。
- 与本库同类卡的分工：`chart-grow` = 5 柱逐项对比（错峰 0.13s、柱顶带值、最高柱高亮换色，
  "念数据"）；`line-chart-story-draw` = 一条线讲一个故事（分段推演 + 标注 + 对比虚线）；
  `metric-with-sparkline` = 一个数 + 它的趋势；`number-slab-pop` = 只报一个结论数字；
  **本卡 = 一段连续区间的整体形状**（多柱、密错峰、无柱顶数值、结论收在一个 chip 上）。

## 动效范围
- 属于本卡的：`barStagger 0.06s` 这个"密到读作一次连续动作"的错峰量级；柱子只走 `scaleY` + `transform-origin: 50% 100%`（拒绝动 height）这条实现纪律；「基线先画出、柱子后升起」这个顺序；七柱**同色无柱顶数值**这个"看形状不看单项"的减法；结论 chip 押在最后一根到顶那一帧弹出、`back.out(1.4)` 的压抑回弹量；chip 落位由**最高柱实际高度**算出（`maxH + chipGap`）这个自适应要求；量程全程固定；hold 期完全静置。
- 不属于本卡的：「数据说话 / 增长 42% / 1月~7月」这套具体文案与那组递增数据、`#e8720c` 这个橙（换 accent 蓝或 negative 红都成立）、44px 柱宽与 4px 圆角、240px 的量程高度、chip 的 12px 圆角与 22px 字号、右侧主持人（数字人）占位、以及"图表左对齐在 96px、贴底 96px"这个落位。
- 迁移接口：HTML 里的 `data-v` 是唯一的内容入口；柱数变了要按"整组升起 ≤0.4s"反算 `barStagger`（`0.4 / (n-1)`）；柱宽按可用宽度 ÷ (柱数 × 1.9) 取（留出约等宽的间隙）；`chipGap` 按柱宽的 40% 缩放；量程高度按舞台高的 45% 取；换方向（下滑）只改数据与颜色，时序不动；竖屏把柱数减到 5 并把柱宽提到 56px（横向空间少，7 柱在竖屏里会压到 26px 以下）。
- 底色要求：白底即可。深底成立（柱色换 `#ff9f0a` 一类的深底橙、基线换 `rgba(255,255,255,0.14)`、标题反白），唯一约束是**底不能有横向网格线**——柱子在长的过程中会与网格线反复交叠，读作"柱子在闪"。要网格就把它压到 3% 以下的对比度，或干脆不要（本卡靠基线给量级参照，不需要网格）。

<!-- ===== /file: video-talkcraft/references/cards/bar-chart-growth.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/bed-echo-blur.md ===== -->

---
name: bed-echo-blur
标题: 同源模糊底床
一句话: 竖屏素材（9:16）装白边卡放右侧，同一条素材放大 1.25 + blur 26 + brightness .45 + saturate .8 铺满当底床且慢放 0.5×；左侧标题两行 + 来源两行逐行升入，前景卡落位后极缓推 1→1.03，7.2s 字与卡退场、底床同帧收
适用: 竖屏素材放横屏不留黑边——竖拍实拍 / 竖屏录屏 / 竖版采访与网友投稿的口播片段 / 竖图（海报、长截图局部；tsx 直出仅收视频，静图需换 `<Img>`）；只有一条可用素材的镜头；中性、克制的调性
时长: 7.7s（0.3 前景卡落位 → 0.8 起四行文字 0.11 错峰 → 7.2 字与卡退场 0.5s → 7.3~7.7 底床收）；成片 = 口播句长，底床缓推 duration 随镜头伸缩
能量: 低
类别: 素材呈现
输入: V, 人(可选)
语义: 例证, 引用
素材形态: 竖屏, 单条视频
位置: 任意
props: src, title, note
优先级: P0
代码: template/cards/bed-echo-blur.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✓ 竖屏口播原片 / 采访片段——自己当自己的底床（人物不进别的底床，只进自己的） | ✓ 竖拍 B-roll（主料） | △ 竖图（海报、长截图的一段）需改源码：tsx 的 `src` 仅走 `<OffthreadVideo>`，换 `<Img>` 见复用指引；静图底床相当于定帧，最稳 |

口播视频与 B-roll 直接走 `src`：一条视频渲两份（前景清晰 1× + 底床慢放 0.5×），不用找第二条素材，颜色一定和谐；静图要先把 `<OffthreadVideo>` 换成 `<Img>`（见复用指引）。

## 常用场景
1. 竖屏手机实拍 / 竖屏录屏放横屏，不留黑边（demo 演的："网友发来的现场画面"）
2. 竖版采访、网友投稿的口播片段
3. 只有一条可用素材的镜头——不用凑第二条 B-roll
4. 竖图：海报、长截图的一段（需按复用指引把 `<OffthreadVideo>` 换成 `<Img>`）

## 意图
竖屏素材放横屏是口播里最常见的尴尬：两侧黑边像没做完，拉伸变形更差。剪辑软件的"模糊填充"（blur fill）是标准答案，但默认做法是同一帧同步放大再模糊——前景与底床同源同步运动，观众读到的是**重影**而不是氛围。
2026-09-04 底床调研（素材呈现实验室 A 组；实验室目录已撤，结论留在本卡）与本卡直接相关的口径：
1. **底床不是"调低透明度"**：透明度只在深底上勉强成立，叠在浅底上会把画面洗成灰雾。标准处理链是压暗 brightness .35~.50 + 去饱和 .5~.7 + 极慢运动（缩放 ≤0.6%/s），可选模糊 20~30。同源模糊底床是这条链的特例——**blur ≥20 才读作"氛围"而不是"糊了 / 没对上焦"**。
2. **底床要慢放（0.5×）或定帧**：与前景同步的同源运动会重影；慢放后两层各有各的时间，前景才立得起来。
3. **两层速度错开**：底床 1.25→1.295 匀速缓推、前景卡只 1→1.03，都 duration = 镜头；底床 : 内容的视差口径 0.5 : 1。前景与底床同速 = 整屏在缩放，深度感全丢。
4. **白字可读靠底床压暗（brightness .45），不靠整体透明度**，也不需要另加 scrim——整床已经压到位。
5. **字与画同起同收**（2026-09-05 用户定版）：底床缓推 duration 就是镜头时长，字退场那 0.4s 底床一起收，不留"字没了画面还在动"的尾巴。

## 动效核心
- 层级（下→上）：底床 echo → 左侧文字组 → 前景白边卡。
- **底床**：同一条素材 `object-fit: cover` 铺满 960×540，再从 `scale 1.25` 起以 `0.07/12 ≈ 0.0058 倍/s` 匀速推到镜头结束（7.7s → 1.295，linear）；`filter: blur(26px) brightness(.45) saturate(.8)` 与 transform 在**同一元素**上（blur 随 scale 一起放大，模糊软边被 1.25 推出画外）；视频 `playbackRate 0.5`。
- **前景卡**：270×464 白边卡（内 250×444 = 9:16，白边 10，圆角 12 / 内 5，投影 `0 12px 60px rgba(0,0,0,.22)`）@ (590, 38)；0.3s 起 0.6s `power3.out`：opacity 0→1、scale .92→1、y 22→0；0.9s 起匀速推 scale 1→1.03 直到 7.2（linear，末速非零）。
- **文字组**：left 90 / top 150 / 宽 440，白字；标题 40px 700 行高 1.25 两行、字距 −0.6；来源说明 16px 白 72% 行高 1.7 两行、上距 16；四行 0.8s 起 stagger 0.11、各 0.5s `power3.out`、y 16→0。
- **退场**：7.2s 文字 + 前景卡 opacity→0 0.5s `power2.in`；7.3s 底床 opacity→0 0.4s `power2.in`；7.7s 同一帧收完，露出白底。
- demo 里的示意视频（Mixkit 海面实拍，demos/_lib/media；底床副本 0.5× 慢放）是演示语境，成片用 `src` 注入真视频。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `echoBlur` 底床模糊 | 26px | 20~30；<20 读作"没对上焦"，>34 变纯色板、同源感消失 |
| `echoBright` 底床压暗 | .45 | 白字可读的上限 ≈.5；<.35 底床成黑板、同源色彩丢失 |
| `echoSat` 去饱和 | .8 | 再低成灰片；1 时底床颜色抢前景 |
| `echoFrom` / `echoRate` | 1.25 / 0.0058 倍/s | 起点 <1.15 模糊软边露进画；速率 >0.01 观众会看见底床在动 |
| `echoSpeed` 慢放 | 0.5× | 1× 重影；0（定帧）最稳，但 B-roll 有明显运动时底床会"死" |
| `cardPush` 前景推幅 | 1.03 | >1.05 与底床的速度差被抹平；1 = 静置也成立 |
| 竖卡尺寸 | 250×444 + 白边 10 | 高 ≤464 留上下 38；宽按素材真实比例反推，不按 9:16 假设 |
| `textIn` / stagger | 0.8 / 0.11 | 四行在一句话内出完；>0.2 变逐行念 |
| `exitAt` / `end` | 7.2 / 7.7 | 成片 = 口播句长；底床 duration 随 `end` 伸缩，速率不变 |

## 已知坑
- 底床与前景同步同速（剪辑软件默认 blur fill）——重影 + 整屏在缩放，一眼假。
- 底床只调透明度不压暗——白字洗成灰雾，什么都读不清。
- blur <20——观众读作"背景没对上焦"，不是氛围。
- 前景不加白边直接贴在底床上——前景与底床粘成一片，看不出"一张卡放在上面"。
- 底床运动写死 12s 而字 7s 就退——底床独自空转拖尾巴（首版实验室就是这么错的）。
- 竖卡放正中——文字无处可放；竖卡永远偏一侧，文字在对侧半幅。
- 人物竖屏原片当底床时脸被放大糊在正中——看得出是脸就有诡异感：给底床那份 Footage 的 style 加 `objectPosition` 往上偏（tsx 未暴露该参数，需改源码）或 `echoBright` 再压一档到 .38。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/bed-echo-blur.tsx——`src` 一条竖屏视频（同一条渲两份：前景 1× + 底床 `playbackRate 0.5`），`title` / `note` 两行文案；durationInFrames 243；句长不同改 `CONFIG.exitAt / end`。素材规格：前景 1080p 竖屏即可，底床同源不用另备。tsx 的 `src` 仅走 `<OffthreadVideo>`；要放静图把 `Footage` 里的 `<OffthreadVideo>` 换成 `<Img>`（Remotion 自带，去掉 `playbackRate`，静图底床即定帧），其余不动。
- HTML/GSAP：demos/bed-echo-blur/index.html——`CONFIG` 是全部节奏；`.fgcard .ph` 与 `.echo-inner .ph` 整块换成 `<video>`（底床那份 `playbackRate = 0.5`）即真素材。
- 剪辑软件对应物：剪映"背景→模糊"（默认同步，要手动把背景层变速 50% 并再压暗）；PR 复制轨道 → 高斯模糊 26 + Lumetri 曝光 −1.2 + 饱和 80 + 变速 50%；ffmpeg `split` + `gblur` + `setpts=2*PTS`（junian.dev 的 blur fill 配方加慢放）。
- 与 layout.md 的接口：文字组落在素材对侧半幅（§4）；标题 40@960 = 80@1080p 属 title 档、来源行 16@960 = 32@1080p 属 caption 档（§5）；竖卡右缘离画幅 100@960 ≥ 安全边（§1）。

## 动效范围
- 属于本卡的：同源底床处理链（cover 铺满 + scale 1.25 起、blur 26 / brightness .45 / saturate .8、慢放 0.5×、0.0058 倍/s 匀速缓推、duration = 镜头）；前景白边卡 0.6s power3.out 落位与 1→1.03 极缓推；两层速度错开；四行文字 0.11 错峰升入；7.2 / 7.3 → 7.7 同帧收的退场编排；"竖卡偏一侧 + 文字在对侧"的版式关系。
- 不属于本卡的：示意视频（演示语境素材，demos/_lib/media，不属于本卡）、示例文案、竖卡的具体坐标（按画幅重排）、白底舞台（只在收尾 0.4s 露出）。
- 迁移接口：`src` 换素材；`CONFIG.end / exitAt` 随句长；1080p 输出所有 px ×2（blur 26→52、白边 10→20、字 40→80）；竖屏输出时竖卡可放大到画幅高 70% 居中、文字改到上下。
- 底色要求：白底即可——底床满铺，舞台底色只在最后 0.4s 露出；素材整体偏亮时把 `echoBright` 压到 .38 保白字。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- 竖卡比例 = 素材真实比例（`ffprobe` 量），宽 = 高 × 比例，白边 10 四边等宽；不按 9:16 假设。
- 竖卡与文字组分居左右半幅：文字组包围盒中心落左半幅（x≈310@960，偏差 ≤48）；竖卡右缘离画幅 ≥48@960（≥96@1080p）。
- 底床可读性：定妆帧在标题处采样底床亮度 L ≤110/255；白字对比 ≥4.5:1；不够就 `echoBright` 再压。
- 无重影：隔 1s 截两帧，底床位移 ≈ 前景位移 × 0.5（慢放生效）。
- 同收：`node scripts/shot-at.mjs bed-echo-blur --play 7.72` 截帧应为纯白，无任何残留。

<!-- ===== /file: video-talkcraft/references/cards/bed-echo-blur.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/behind-text-title.md ===== -->

---
name: behind-text-title
标题: 人后大字视差
优先级: P1
代码: template/cards/behind-text-title.tsx
一句话: 超大标题 0.6s 从人物身后升起、字距由松收紧，下缘被人物剪影遮住；hold 期间标题与人物各 ±4px 反向极缓漂移，平面画面读出伪 3D 层次
适用: 开场题眼、章节大标题、结尾点题；vlog 化 / 电影感调性的真人出镜口播（人物层需抠像，无出镜场景不适用）
时长: 起手延迟 0.4s + 标题升起 0.6s，小字晚 0.35s 跟进；hold 漂移周期 8s 循环，可随口播任意延长
能量: 中
类别: 人物互动
输入: 人(必需), 文
语义: 钩子, 标题
素材形态: 透明通道, 人脸
位置: 任意
props: hostSrc
---

## 意图
标题直接叠在人物上面读作"字幕"，从人身后升起、被身体遮挡穿出，观众读到的是**空间**——
一行字瞬间有了片头的仪式感。命门三条：
1. **必须有遮挡**：标题与人物重叠面积 ≥25%（demo 里人物头顶吃进标题下缘），零重叠就是普通标题。
2. **hold 期间反向漂移**：标题与人物各往相反方向极缓移动，视差才成立；同向漂移层次感当场消失。
3. **字要够大且有立体质感**：字号占屏高 40%+（demo 235px），小字被遮一角只会像排版事故；字面用 3D 挤出艺术字（渐变字面 + 灰阶递进 text-shadow 侧面 + 落地投影），平面黑字压不住这个构图。

常见于：影视飓风（signature）、何同学、vlog 化知识区。

## 动效核心
- 三层 z-index：背景（z0）→ 大字标题层（z1）→ 前景人物剪影（z2，实拍中来自抠像）；
  另加小字副标（z1，标题上方）
- 标题入场（0.4s 起）：opacity 0→1 + y 70px→0 + letter-spacing 0.14em→0.02em 收拢，0.6s `power3.out`——
  升起与收字距同步，像"从人背后聚拢成形"
- 副标小字：晚 0.35s，opacity 0→1 + y 10px→0，0.4s `power2.out`
- hold（入场完成即开始）：标题 x 0→+4px、人物 x 0→-4px，`sine.inOut` + yoyo 无限往复，
  半周期 4s（整周期 8s）——快了穿帮，慢到 8s 才像"镜头在呼吸"
- 遮挡由层级天然完成，不用 mask；人物剪影高度决定吃进标题多少

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `titleIn` | 0.6s | <0.4s 像弹出失去庄重感；>0.8s 拖沓，观众等字 |
| `riseFrom` | 70px | 越大"从身后钻出"越明显；>80px 会从人物中段穿身而过穿帮 |
| `trackFrom` → `trackTo` | 0.14em → 0.02em | 收拢量越大越有"聚焦成形"感；不收字距入场读作平移 |
| `driftPx` | 4px | >8px 像素材没固定住在漂；0 则 hold 期间死板如截图 |
| `driftPeriod` | 8s | <4s 读作晃动穿帮；越长越像呼吸镜头 |
| `subDelay` | 0.35s | 与主标同帧出=层次塌掉；>0.6s 观众以为没有副标 |
| `.bt-title` font-size | 235px | 屏高 40%+；再小遮挡读不出"在身后" |
| `.bt-host` height | 430px | 控制遮挡面积：头顶须吃进标题下缘 ≥25%，矮了就是普通标题 |

## 已知坑
- 文字与人物零重叠——没有遮挡就没有"身后"，一眼只是普通大标题。
- 漂移同向或幅度相同方向相同——视差的本质是层间相对运动，同向等于整体平移。
- hold 期间完全静止——像卡帧/贴图，伪 3D 骗术全靠那 ±4px 维持。
- 字号太小或标题放得太高躲开人物——遮挡消失，效果退化为片头字幕。
- 漂移周期太短——观众看出"元素在动"而不是"镜头在呼吸"，立刻廉价。

## 复用指引
- props：仅 `hostSrc`（抠像口播视频）；标题 / 副标文案在 JSX 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/behind-text-title.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/behind-text-title/index.html。换文案改 `.bt-title`（主标）与 `.bt-sub`（副标）内文本；
  换色改 `.bt-title` 的 `color:#b9b9bf`（挤出侧面）与 `.bt-title::after` 的渐变字面、`.bt-sub` 的 `color:#8a8a8a`；
  时序手感全部在顶部 `CONFIG`（titleIn / riseFrom / trackFrom / trackTo / driftPx / driftPeriod / subDelay）；
  遮挡量调 `.bt-host` 的 width/height。核心动画即 `DemoShell.register` 内那一段，连 CONFIG 一起复制可直接摘走。
- Remotion 移植：三个绝对定位层按 z-index 叠放（人物层用抠像视频 `<OffthreadVideo>` 或带 alpha 的序列帧）；
  升起用 `interpolate(frame, [t0, t0+0.6*fps], [70, 0], {easing: Easing.out(Easing.cubic)})` 同步驱动 y、
  opacity 与 letterSpacing（0.14em→0.02em）；hold 漂移用 `Math.sin((frame/fps) * 2*Math.PI / 8) * 4`，
  标题取正、人物层取负，帧驱动天然 seek 安全。
- 剪辑软件对应物：剪映/CapCut 用"智能抠像"复制一层人物置顶、文字轨夹在原片与抠像层之间（教程常叫
  "text behind person / 人物遮挡文字"）；AE 里 Roto Brush 抠前景置顶，标题层 Position 打关键帧 +
  `loopOut("pingpong")` 做反向漂移；FCPX 用 Keyer + 三层堆叠同理。

## 动效范围
- 属于本卡的：3D 挤出艺术字质感（渐变字面 + 灰阶递进阴影侧面——立体靠灰阶层次，颜色是迁移接口）；三层 z 序（背景 → 大字标题 → 前景人物）以及由层级天然完成的遮挡（不用 mask）；标题入场 opacity 0→1 + y 70px→0 + `letter-spacing 0.14em→0.02em` 三者同步（0.6s、`power3.out`，"从人背后聚拢成形"）；副标晚 0.35s 的 opacity + y 10px→0；hold 期标题 +4px / 人物 −4px 的**反向**极缓漂移（`sine.inOut` + yoyo 无限，半周期 4s）；标题与人物重叠面积 ≥25% 这条几何约束。
- 不属于本卡的：背景（demo 已去掉渐变与暗角，纯白）、标题/副标文案与字体、人物剪影的画法（demo 用 host-placeholder 的灰阶版，实拍来自抠像）、字幕、235px 与 430px 这两个绝对值（按画幅折算）。
- 迁移接口：字色改 `.bt-title` 的 `color`（默认墨色 #1d1d1f）与 `.bt-sub` 的辅助灰 #8a8a8a；时序在 `CONFIG`（`titleIn`/`riseFrom`/`trackFrom`/`trackTo`/`driftPx`/`driftPeriod`/`subDelay`）；换尺寸时字号按**屏高 40%+**折算、`riseFrom` 与 `driftPx` 同比缩放（`driftPeriod` 不缩放，它是呼吸感的绝对时间）；遮挡量调 `.bt-host` 的 width/height 或换成真实抠像层，务必让头顶吃进标题下缘 ≥25%。
- 底色要求：白底即可，前提是**标题、人物、底三者明度要分得开**——本卡的效果全靠"字被人挡住"这个层次读出来。白底上人物剪影用浅灰（#e3e3e6/#ececef）、字用墨色即成立；实拍落地时人物层是抠像素材，标题色需与人物主色拉开对比，否则遮挡边界看不出来，效果退化成普通标题。

<!-- ===== /file: video-talkcraft/references/cards/behind-text-title.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/black-slam-transition.md ===== -->

---
name: black-slam-transition
标题: 黑震切转场
一句话: 出场镜头相机定格一拍（全片唯一不动的时刻）+ 重音冲顶，最后 1 帧 opacity 直接归零（零交叠硬切），入场镜头满亮直切且开场自带运动——切点一拍三段递减震位 + 从 1.10 后拉刹住
适用: 全片最大的那一次反转/揭示，**一部片只许用一次**；前一句是悬念或结论前的停顿，后一句是答案
时长: 定格 0.34s → 重音冲顶 0.12s → 硬切（零交叠）→ 震位 0.20s + 后拉刹住 0.50s；从定格起到刹住共 0.96s（切点后 0.5s）
能量: 高
类别: 转场结构
输入: 场
语义: 转场, 转折
素材形态: 无
位置: 中段
props: hostSrc(未使用)
优先级: P0
代码: template/cards/black-slam-transition.tsx
---

## 意图
其余五式都在做"动量交接"，黑震切反过来——它是**故意的断裂**，用一次合法的硬切换取最大冲击。
关键不在"硬切"本身（那是 PPT 感的病根），而在硬切两侧的**特权安排**：
出场侧给一拍定格（全片唯一静止的时刻），入场侧给一拍震动 + 自带运动。
定格制造预备，震动兑现冲击；如果两边都平平地切，就退化成了它要避免的那个毛病。

做对的命门：① **定格必须是全片唯一的**——其余镜头的 hold 期相机永不静止，只有这里停一拍，
静止才成为信号而不是失误；② **零交叠**（`hardOut`，最后 1 帧直接消失，不淡出）——有交叠就不是"震"了；
③ **入场满亮直切且开场自带运动**——切进来那一帧就已经在 1.10 并且带震位，直切到静止画面会读作幻灯片跳页；
④ **全片限一次**——用第二次时，第一次的分量立刻蒸发。

## 动效核心
时间结构（`cut = at + 0.12`，参数全在 `CONFIG.slam`）：

| 阶段 | 时刻 | 出场镜头 | 重音层 | 入场镜头 |
|---|---|---|---|---|
| 定格 | `at−0.34` → `at` | 相机**完全静止**（hold 只做前段慢推，末段留空） | — | 停在 `scale 1.10`、`opacity 0` |
| 重音冲顶 | `at` → `cut` | 仍定格 | `opacity 0→0.34`，`power3.in` | — |
| 切点 | `cut` | `tl.set(opacity: 0)` —— hardOut，不淡出 | 峰值 | `tl.set(opacity: 1)` —— 满亮直切 |
| 震一拍 | `cut` → `cut+0.20` | — | 0.20s `power2.out` 回落 | `x: +9 → −4.95 → +2.52 → 0`（三段递减，每段 0.06/0.06/0.08s，前两段 `ease:none`、末段 `power2.out`） |
| 后拉刹住 | `cut` → `cut+0.50` | — | — | `scale 1.10→1.0`，`power4.out` |
| 交班 | — | — | — | hold 期慢漂（`drift 10px` + `push 0.03`） |

- **`hardOut` 是本式的技术标记**：GSAP 里用 `tl.set(out, {opacity: 0}, cut)`，
  Remotion 里是 `<ShotFade hardOut>`（`opacity *= frame >= total - 1 ? 0 : 1`）。
  两侧都用 `set` 而不是 `to`——这一帧的瞬变就是"震"的来源。
- **三段递减震位，不是抖动**：`+9 → −4.95 → +2.52 → 0`，幅度按 0.55 衰减，只在切点这一拍发生一次。
  这与项目定版的"不做定格抖动/line boil"不冲突：抖动是持续的微振（读作廉价），
  震位是**边界上的单次冲击**（读作物理）。用 `repeat` 做成持续抖动就踩了红线。
- **前两段 `ease:none`、末段 `power2.out` 的三段位移**：前两段线性、段间硬转向，才有"撞"的棱角，末段 0.08s 用 `power2.out` 刹回 0；用 `elastic`/`back` 会读作果冻。
- **后拉用 `power4.out`**：极陡的减速——切进来那一帧速度最大，0.15s 内吃掉九成，剩下 0.35s 缓慢落定。
  这条曲线让"满亮直切"不显得突然，因为观众看到的是"冲进来然后被刹住"。
- **重音峰值 0.34（白底压暗）**：比过曝翻页高（0.10），因为它要承担整次冲击；
  深底工程换回白色径向过曝时可到 0.55~0.7。极性规则与 [[overexpose-flip-transition]] 相同。

Remotion 对应写法（`template/motion-systems/transitions.tsx`）：

- 出场 shot（末段**不加相机键** = 定格，配 hardOut）：`{ tail: 1, hardOut: true, path: [{t:0, scale:1.02}, {t:tFreeze, scale:1.06}] }`，外壳 `<ShotFade lead={lead} tail={1} narrationFrames={n} hardOut>`
- 入场 shot（`lead: 0` 零交叠，`path` 自带起手运动）：`{ lead: 0, path: [{t:0, scale:1.10, x:9}, {t:0.2, x:0}, {t:0.5, scale:1.0}] }`
- 它是六式里**唯一没有 CamKey 生成器**的一式——出场侧的动作是"不加键"，入场侧的起手运动按当场内容定（震位方向、后拉量都可调）。
- 闪光由场景自己画（或 `transitions.tsx` 的 `<Overexpose>`）；`env.tsx` 的 `TRANSITION_FLASHES` 表按 cinematography.md §2 留空不用。

## 参数表
| 参数 | 典型值 | 调节手感 |
|---|---|---|
| 定格时长 `freeze` | 0.34s（≈10 帧） | <0.2s 观众来不及注意到"停了"，预备拍失效；>0.6s 读作卡顿/掉帧 |
| 重音冲顶 `punch` | 0.12s（≈4 帧） | >0.25s 观众提前预知要切，冲击被泄掉；<0.06s 重音来不及被看见 |
| 重音峰值 `peak` | 白底 0.34 / 深底 0.55~0.7 | 比过曝翻页高——它承担整次冲击；白底 <0.2 读作"闪了一下没意义" |
| 重音回落 `fall` | 0.20s | 比过曝翻页的 0.42s 短：这里要让新画面尽快亮出来 |
| 震位幅度 `shake` | 9px @960 宽 | <5px 看不见；>16px 读作故障/穿帮；按屏宽比例缩放 |
| 震位段时长 | 0.06 / 0.06 / 0.08s | 每段 ≥0.1s 就成了"晃"而不是"震"；段数 >3 就成了抖动（踩红线） |
| 入场起手景别 `kickScale` | 1.10 | =1.0 是直切到静止画面 = 幻灯片跳页；>1.25 后拉太长，冲击被拖散 |
| 后拉刹住 `kick` | 0.50s，`power4.out` | 换 `power2.out` 减速太软、失去"被刹住"感；>0.8s 冲击拖尾过久 |
| 交叠 | **0（hardOut）** | 任何非零交叠都让本式退化成推穿的一个弱版本 |

## 已知坑
- 用了两次以上：第一次的分量当场蒸发。全片限一次，留给最大反转。
- 出场侧没有定格（照旧慢推）：硬切没有预备拍，读作剪辑失误而不是设计。
- 定格那一拍加了 idle 微动"以免太死"：那就不是定格了，本式的信号消失。
- 入场侧不带运动直切：静止画面瞬现 = PPT 跳页，把本卡最想避免的毛病请回来了。
- 把震位做成 `repeat` 持续抖动：踩项目红线（不做定格抖动），且读作廉价。震只发生一次。
- 用了交叠淡化（忘了 `hardOut`）：软化了边界，冲击全无。
- 白底工程照抄白色过曝重音：被底色吞掉（同 [[overexpose-flip-transition]] 的极性约束）。
- 定格 + 硬切放在一句话中间：本式必须压在句末/停顿处，否则语音连续而画面断裂，读作丢帧。
- 入场侧前 0.4s 只有匀质深底在"动"：运动存在但不产生像素变化，`motion_check` 的 freezedetect 照样报静止——**主体必须与硬切同帧登场**才有着力点，不能等底色稳住再进。

## 复用指引
- props：仅 `hostSrc`（本卡未使用）；两个镜头（白 / 浅灰 tile + 式名大字）在 JSX 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/black-slam-transition.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：`demos/black-slam-transition/index.html`。摘 `blackSlam(出场镜头, 入场镜头, 起始秒) → 结束秒`
  一个函数 + `CONFIG.slam` 一组参数 + `.flash` 那段 CSS。**注意排片**：出场镜头的 `hold()` 时长要写成
  `hold - freeze`（末段留空 = 定格），这一句不能省，否则定格不存在。
- Remotion：出场 shot 末段不加 CamKey + `<ShotFade hardOut>` + `tail: 1`；入场 shot `lead: 0`，
  `path` 首键自带 `scale 1.10` 与震位；闪光由场景自己画，不走 `TRANSITION_FLASHES`。
- 家族关系：它是六式里唯一的硬切，其余五式都有交叠。想要冲击但不想断裂 → 用 [[overexpose-flip-transition]]；
  想要"零补间硬切当节拍器"的连续版本 → 那是另一张卡 color-slam-beat-card（底色跳变节拍），不要与本式混用。
- 剪辑软件对应物：剪映/PR 里就是不加转场的硬切 + 前一镜定格帧 + 后一镜"缩放+位置"两个关键帧；
  AE 用 Exposure 冲顶 + 后镜 Scale/Position 关键帧（Easy Ease 改成 90% 出）——本卡把三件事绑成了一个时间形状。

## 动效范围
- 属于本卡的：出场侧**相机定格一拍**（全片唯一静止的时刻，作为硬切的预备拍）+ 重音 0.12s `power3.in` 冲顶；
  **零交叠 hardOut**（最后 1 帧 `opacity` 直接归零，用 `set` 不用 `to`）；入场侧满亮直切（同帧 `set opacity:1`）
  且开场自带运动——切点一拍的三段递减震位（`+9 → −4.95 → +2.52 → 0`，前两段 `ease:none`、末段 `power2.out`，只发生一次）
  + `scale 1.10→1.0` 的 `power4.out` 后拉刹住；重音 0.20s `power2.out` 回落；hold 期相机永不静止的慢漂。
- 不属于本卡的：两个镜头里的文字与配色（白/浅灰 tile + 灰字式名是"认式子的标签"，不是台词字幕）、
  左上说明角标、**重音是亮还是暗**（随底色定）、震位往左还是往右、`.shot` 的 `inset:-14%` 具体数值。
- 迁移接口：时序全在 `CONFIG.slam`（`freeze`/`punch`/`peak`/`fall`/`kick`/`kickScale`/`shake`）；
  **重音层极性随底色切换**（白底暗压 0.34，深底白色径向过曝 0.55~0.7，包络不动）；
  换尺寸时 `shake` 按屏宽比例缩放，`kickScale` 与画幅无关；
  **零交叠是本式的定义，不可参数化**——一旦给了交叠就该改用别的式。
- 底色要求：白底可跑，**但重音层必须换极性**（白色过曝在白底上被完全吞掉，改成压暗一拍）。
  相机曲线与底色无关。这与 [[overexpose-flip-transition]] 共享同一条底色耦合约束。

<!-- ===== /file: video-talkcraft/references/cards/black-slam-transition.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/callout-line-label.md ===== -->

---
name: callout-line-label
标题: 标注引出线
一句话: 目标上圆点 pop 亮起并荡开一圈涟漪 → 折线沿 45°/水平拐点向外生长 → 线端文字标签遮罩揭示，三拍严格串行、一气呵成
适用: 口播念到"这里/这个部位/这两处"时，在截图或产品图上指哪看哪；评测、拆解、地图解说类调性，冷静专业不抢戏
时长: 单个标注约 0.95s（圆点 0.2s + 折线 0.4s + 标签 0.25s、文字再滞后 0.1s）；多标注错峰 0.8s；停留 1.6s 后 0.5s 反向收回
能量: 中
类别: 强调标注
输入: 图, 文
语义: 强调
素材形态: 无
位置: 任意
props: 无
优先级: P1
代码: template/cards/callout-line-label.tsx
---

## 意图
口播说"真正值钱的是这两处"时，观众的眼睛需要被牵到画面的具体位置——callout 把"用手指"翻译成三拍因果：点亮起（在哪）→ 线生长（往哪看）→ 标签揭示（是什么）。
命门：**三拍必须严格串行**（同时出现就没有引导视线的因果感）；**折线拐点只用 45° 或水平**（工程制图的秩序感，斜率随意像草图）；**标签永远最后出现**（答案不能比手指先到）。

常见于：Johnny Harris、Vox、AE 模板 Call-Out Titles（4.5K 销量）、产品评测。

## 动效核心
- 圆点：SVG circle 落在目标上，scale 0→1，0.2s `back.out(2.2)`；同时一圈同色描边涟漪 scale 0.4→3.2、opacity 0.9→0，0.5s `power2.out`
- 折线：SVG path（1~2 个拐点，全部 45° 或水平），`stroke-dasharray` = 总长，`stroke-dashoffset` 从总长→0 描画 0.4s `power2.out`；**起点排在圆点 pop 结束之后**（t0 + dotIn）
- 标签：HTML div 贴在线端，`clip-path: inset()` 从线端方向展开 0.25s `power3.out`（线从右来就 `inset(0 0 0 100%)` 起步），内部文字 opacity 再滞后 0.1s 淡入 0.2s
- 多标注：第二个 callout 整体延迟 0.8s，逐条对齐口播列举的节奏
- 退场：反向收回——标签先收（power2.in）、线回吸、点熄灭，三段按 out 比例分配（0.4/0.4/0.3），第二个标注再错 0.15s

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `dotR` | 7 | 圆点半径 px；>10 像按钮，<5 在视频压缩后看不见 |
| `dotIn` | 0.2s | 圆点 pop 时长；>0.35s 拖沓，<0.1s 没有"叮"的落点感 |
| `lineDraw` | 0.4s | 折线描画时长；>0.6s 观众等得着急，<0.25s 线"闪现"没有生长引导感 |
| `labelIn` | 0.25s | 标签遮罩展开时长（文字固定再滞后 0.1s）；>0.4s 读作幕布拉开，太慢 |
| `hold` | 1.6s | 全部就位后的停留；对齐口播讲完该卖点的时长，讲得长就调大 |
| `out` | 0.5s | 反向收回总时长（标签/线/点按 0.4/0.4/0.3 比例分配）；>0.8s 退场喧宾夺主 |
| `stagger` | 0.8s | 第二个标注的延迟；<0.5s 两个标注抢视线，必须错峰逐条出现 |
| `color` | #d8383a | 点、涟漪、线同色的标注色（白底 demo 用红，深底可换高亮黄）；换品牌色时保持与底图高对比 |
| `callouts[]` | target/points/label | target=圆点坐标；points=拐点+终点（只放 45°/水平位置）；label 的 `lines` 两行（主句 / 补充）、x/y 贴线端、`from` 定展开方向（"right"=从右往左收拢的线） |

## 已知坑
- 点、线、标签三段同时开始——没有"点→线→字"的因果链，眼睛不知道先看哪，一眼假。
- 折线斜率随手拉——拐点必须落在 45° 或水平网格上，否则像草稿涂鸦而不是标注。
- 标签先于线出现（最常见错序）——答案比手指先到，引出线沦为装饰。
- 标签压在目标本体上或线太短——标注必须把文字引到空白区，盖住本体等于白标。
- 用 opacity 渐显代替 clip-path 展开——标签失去"从线端长出来"的方向感，和线脱节。

## 复用指引
- props：无；被标注对象是 CSS `.phone` 占位，圆点 / 折线坐标与标签文字在 `CONFIG.callouts` 常量里，上真截图或换标注需改源码。
- Remotion/tsx（skill 首选）：template/cards/callout-line-label.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。上真截图把 `.phone` 那段 JSX 换成 `<Img src>`（视频截帧用 `<OffthreadVideo>`），再按真图重量 `CONFIG.callouts` 的坐标。
- HTML/GSAP：demos/callout-line-label/index.html。换文案/换位置只改 `CONFIG.callouts`：`label.html` 换标签文字（`<b>`主句+`<small>`补充）、`target`/`points`/`label.x/y` 换坐标、`label.from` 换展开方向；`CONFIG.color` 换主题色；假手机是 `.phone` 一段纯 CSS，替换成自己的截图元素即可。入场基准延迟 0.6s 写死在 register 内的 `t0 = 0.6 + i * CONFIG.stagger`。核心动画即 `DemoShell.register` 回调整段，复制 CONFIG + 回调可直接摘走。
- Remotion 移植：tsx 不用 `<Sequence>`，三拍按 `t0 = 0.6 + i×stagger`、`tLine = t0 + dotIn`、`tLabel = tLine + lineDraw` 逐帧 tween；折线总长用 `polyLen()` 按拐点算（不需要 `getTotalLength()`），`strokeDasharray = len`、`strokeDashoffset` 从 len→0；圆点 `back.out(2.2)` 过冲（opacity 封顶 1）；标签 `clipPath: inset()` 按 `label.from` 选左右哪一侧收缩，文字 opacity 延迟 0.1s（3 帧）。
- 剪辑软件对应物：AE 里即 "Call-Out Titles" 类模板，自建 = 形状图层折线加"修剪路径"（Trim Paths）+ 文本层矩形蒙版位移揭示；剪映用贴纸搜"标注/指示线"或线条生长素材叠字幕入场"擦除"；CapCut 搜 callout/annotation 模板。

## 动效范围
- 属于本卡的：圆点 scale 0→1 pop（0.2s、back.out(2.2)）+ 同色描边涟漪 scale 0.4→3.2 淡出（0.5s、power2.out）；折线 stroke-dashoffset 从总长→0 描画（0.4s、power2.out、拐点只走 45°/水平）；标签 clip-path inset 从线端方向展开（0.25s、power3.out）、内部文字再滞后 0.1s 淡入；三拍严格串行的时序（点→线→字，各段起点相接）；多标注整体错峰 0.8s；反向收回（标签 0.4 / 线 0.4 / 点 0.3 比例分段、power2.in）。
- 不属于本卡的：被标注的产品图占位（demo 里那部灰阶线框手机）、标签的排版/边框/字号、示例文案与坐标、字幕行。
- 迁移接口：`CONFIG.color` 一处换标注色（点/涟漪/线同色，需与底图高对比）；`CONFIG.callouts[]` 换 `target`（圆点坐标）/ `points`（拐点+终点，保持 45°/水平）/ `label.x,y` 与 `label.from`（展开方向）；时长四件套 `dotIn / lineDraw / labelIn / hold` 按语速整体乘同一系数缩放；`dotR`、`stroke-width` 随输出分辨率等比缩放。
- 底色要求：白底即可。标注色只需与底图有足够对比——深底把 `CONFIG.color` 换成高亮黄、标签底色改深色即可，动效时序不变。

## 落位自检（2026-09-05 用户定版，选卡时抄进 SHOTBOOK 该镜自检列）
- 标注几何（框 / 圈 / 线 / 箭头 / 放大镜锚点）一律由**目标的实测包围盒**反推——DOM `getBoundingClientRect` / `measureText`，四边留白 16~24px 等距，**不目测**。
- 实现后抽该镜定妆帧核对：标注是否恰好套住 / 指向目标，偏差 **> 8px 返工**（`references/layout.md` §3）。
- 目标会滚动 / 移动时，标注钉在内容坐标系随内容动（SKILL.md ③）。

<!-- ===== /file: video-talkcraft/references/cards/callout-line-label.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/caret-wipe-transition.md ===== -->

---
name: caret-wipe-transition
标题: 光标擦除转场
优先级: P1
代码: template/cards/caret-wipe-transition.tsx
一句话: 一条 3px 文本光标从左到右扫过 1.33s 完成换场——走过之处露出新场景（沉降解糊，像刚被打出来），未到之处仍是旧场景（上浮失焦，像正被退格吃掉），互补裁切永不露缝
适用: 讲代码/编辑器/文档/AI 生成内容的镜头边界——"改完了""重写这一段""换个版本"；边界本身要有语义的时刻；不适合真人出镜之间的切换（光标隐喻与人像无关）
时长: 扫完全屏 1.33s（≈40 帧 @30fps）；配 hold A 0.8s + hold B 0.9s 的完整一拍约 3.0s
能量: 中
类别: 转场结构
输入: 场
语义: 转场
素材形态: 无
位置: 中段
props: hostSrc(未使用)
---

## 意图
本库的运动承接六式全是**相机动量交接**（推穿/翻页/横摇/砸黑/拉出/焊接）——
边界处发生的是"镜头在动"，边界线本身没有含义；`shape-wipe-transition` 的色块扫屏也一样，
色块是一块**不透明的遮挡物**，它的职责就是"让你看不见换场那一帧"。

这张卡是本库第一个**边界本身有语义**的转场：那条竖线不是遮挡物，是一个文本光标。
于是同一次擦除同时说了两件事——光标**走过的地方"刚被打出来"**（新内容从下方沉降、从模糊解糊），
**没走到的地方"正被退格吃掉"**（旧内容往上浮、逐渐失焦）。
讲"我把这段重写了""这个版本换成了那个版本""AI 把它改成了这样"时，
它比任何色块或相机运动都贴题：编辑器的隐喻自己把因果讲完了。

命门三条：① **互补裁切**——新旧两层的 `clipPath` 必须严格互补（`inset(0 (100−x)% 0 0)` 对
`inset(0 0 0 x%)`），两边共用同一个进度量 x，差半个百分点就会在边界露一条底色缝；
② **两侧微反差是灵魂**——新场景 `y +3→0` / `blur 2→0`，旧场景 `y 0→−6` / `blur 0→4`。
去掉它就退化成一次普通的硬边 wipe（那已经是 shape-wipe 的地盘了），
"打出来 / 被吃掉"这层语义全部来自这两组极小的反向运动；
③ **白底不加发光**——原版给光标加了 `box-shadow: 0 0 18px` 的光晕（它是深底 + 荧光绿的设计语言），
搬到本库白底舞台上只会在边界糊出一团脏边，改成实色细条。

## 动效核心
- **一个进度量驱动三件事**：`p.x` 从 0 走到 100（`cubic-bezier(0.65,0,0.35,1)`，1.33s）。
  每帧 `onUpdate` 里写三处：新场景 `clipPath: inset(0 (100−x)% 0 0)`、
  旧场景 `clipPath: inset(0 0 0 x%)`、光标 `translateX(x% × 画幅宽)`
- **裁切必须互补**：新场景只露 `[0, x]` 带，旧场景只留 `[x, 100]` 带，两带首尾相接。
  两层同尺寸、同位铺满，所以任何 x 都不会露出底色
- **两侧微反差（各自一条曲线，与裁切曲线分开）**：
  - 新场景：`y +3 → 0`（同 EASE，走满 1.33s）+ `blur 2 → 0`（`power1.out`，只走 80%——落定那一刻已经是清的）
  - 旧场景：`y 0 → −6`（`ease:none` 匀速上浮）+ `blur 0 → 4`（`power1.in`，**起手延后 10%**，让"被吃掉"发生在光标真的开始走之后）
  - 位移量刻意做小（3 / 6px）：这是"内容在被编辑"，不是相机在推
- **光标条**：3px 宽、屏高 50%、`translateX(-50%)` 骑在边界上、实色 `#1d1d1f`、圆角 = 宽度。
  **两端各 8% 进度内淡入淡出**——不这么做，第一帧和最后一帧会看到光标"突现/突灭"
- **缓动 `cubic-bezier(0.65,0,0.35,1)`**：中段快、末尾减速，像敲下最后一列后手指停住。
  匀速扫读作"刷新条"，`power4.out` 那种起手猛冲读作甩镜（那是 whip-pan 的地盘）
- **两层的 inset 纪律**：`inset: -10px 0` —— 上下各溢出 10px 给 ±6px 的竖向微反差留余量（不留会在上下缘漏一线白），
  **左右必须严格等于画幅**：`clipPath` 的 `inset(%)` 按元素自身宽度算，横向多溢出一点，
  裁切边界就与按画幅算的光标位置错开几个 px（一眼看到光标"压在缝旁边"而不是"骑在缝上"）
- **`onUpdate` 里直接写 `style`，不用 `gsap.set`**：`gsap.set` 会被排到下一个 tick，
  光标与裁切边界差一帧，看上去像"光标追不上擦除线"（本 demo 踩过，probe 出来实测差 1 帧 ≈ 30px）
- **层级**：舞台白底 → 旧场景（被裁到右带）→ 新场景（被裁到左带）→ 光标条（不裁切、最上层）

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `wipe` | 1.33s（≈40 帧 @30fps） | 扫完全屏；<0.7s 读作硬边闪切、两侧微反差全看不见，>2.0s 观众等着它走完、节奏塌 |
| 缓动 | `cubic-bezier(0.65,0,0.35,1)` | 末尾减速是"敲下最后一列"；匀速读作刷新进度条，起手猛冲（`power4.out`）读作甩镜 |
| `caretW` | 3px | 光标宽；1px 在 1080p 缩放后会闪，>6px 变成一根柱子、读回色块 wipe |
| `caretH` | 0.5（屏高 50%） | 光标高；<0.35 太小、抓不住视线，=1.0（贯穿全屏）读作分屏线而不是光标 |
| `caretFade` | 0.08（两端各 8% 进度） | 防边帧突现；0 = 第一/末帧看到光标凭空出现与消失，>0.2 光标大半程都在半透明 |
| `inY` / `inBlur` | +3px / 2px | 新场景沉降解糊（"刚被打出来"）；两者都为 0 就退化成普通硬边 wipe，>8px / >5px 读作相机在推（那是推穿的地盘） |
| `outY` / `outBlur` | −6px / 4px | 旧场景上浮失焦（"正被退格吃掉"）；比新场景的量**故意大一倍**——被吃掉的一侧要更"松"，两侧等量会读作对称转场、没有主次 |
| 旧场景失焦起手延后 | 10% 进度 | 让"被吃掉"发生在光标真的开始走之后；0 = 光标还没动画面已经在糊，读作播放器卡了 |
| 新场景解糊终点 | 80% 进度 | 落定那一刻必须已经清；=100% 则最后一帧还在解糊，收尾"软"了 |
| `dir` | `right` | 从左往右打（默认，符合"正在写"）；`left` = 反向退格，适合"撤销/回到上一版"的语境 |

## 已知坑
- 两层裁切不互补（各写各的百分比、或用了不同的进度量）——边界处露出一条舞台底色缝，1080p 下是一根白线，一眼是 bug。
- 两层 `inset` 横向也溢出（比如 `inset: -10px` 全向）——`clipPath` 的 `inset(%)` 按元素自身宽度算，裁切边界与按画幅算的光标位置错开几 px，光标压在缝旁边。
- 在 `onUpdate` 里用 `gsap.set` 改裁切/光标——被排到下一个 tick，光标与边界差一帧（≈30px），读作"光标追不上擦除线"；直接写 `element.style`。
- 省掉两侧微反差——退化成硬边色块 wipe，"打出来/被吃掉"的语义消失，那就该直接用 `shape-wipe-transition`（它更快更省）。
- 两侧反差做成等量（都 ±5px）——读作对称的对开幕布，没有主次；被吃掉的一侧位移必须明显更大。
- 给光标加发光（`box-shadow` / `filter: drop-shadow`）——原版是深底荧光绿的设计语言，白底上糊成一团脏边（design-defaults 也禁 glow）。
- 光标不做两端淡入淡出——转场的第一帧和最后一帧看到它凭空出现/消失，边帧突现是最廉价的破绽。
- 位移量按相机的量级给（±20px 以上）——本卡是"内容在被编辑"，不是镜头在动；量大了就与运动承接六式抢地盘且两者规则冲突。
- 用在真人出镜镜头之间——光标隐喻与人像无关，观众读不出任何因果，只剩一根莫名其妙的竖线扫过脸。
- 一片里反复用（≥3 次）——它的语义太具体（编辑器），第三次出现时观众开始觉得"这个片子只会这一招"；同一片限 1~2 次，且都用在真的与文本/代码有关的边界上。
- 两个场景的示意大字都居中——擦除边界会停在任意横向位置，中段时两行字在边界处叠成乱码；demo 里让新场景标签靠左（最早露出的带）、旧场景标签靠右（最后被吃掉的带）。
- 场景内容是纯色块（没有满幅纹理）——中段之后未到之处是一片空白，看不出"这仍是旧场景"；两侧都要有铺满画幅的可辨识内容。

## 复用指引
- props：仅 `hostSrc`（本卡未使用）；两个场景（纹理 tile + 认式标签）在 JSX 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/caret-wipe-transition.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/caret-wipe-transition/index.html。核心是 `caretWipe(out, inn, at)` 这个函数——
  把两个铺满画幅的场景层传进去就能用，返回擦除结束的时刻（便于接着排 hold）。
  换方向改 `CONFIG.dir`；`clipOld` / `clipNew` 两个函数已经把方向分支写好了。
  `cubicBezier()` 是通用的缓动解算器（GSAP core 不带 `CustomEase`），可以直接抄走。
- Remotion 移植：template/cards/caret-wipe-transition.tsx 已是帧驱动实现——一个进度量 `x` 同时驱动 `clipOld(x)` / `clipNew(x)` / 光标 `translateX`。
  若要包成 `@remotion/transitions` 的 `TransitionPresentation`，`presentationProgress` 就是本卡的 `x/100`：
  `entering` 分支给新场景（`clipPath` + `translate` + `blur`），`!entering` 分支给旧场景，
  光标只画在 `entering` 分支里（否则会出现两根）。
  接进本库 `template/motion-systems/transitions.tsx` 的话，它与六式**不同族**——
  六式是 CamKey 生成器（改相机 path），这张卡不动相机，是一对互补的 `clipPath` 包在 Sequence 外层；
  所以不要塞进 `pushThroughOut/settleIn` 那套接口，单独作为一个 presentation 用。
- 剪辑软件对应物：剪映/CapCut——"线性擦除/线性划像"转场 + 手动给两侧各加一组位移与模糊关键帧
  （预设本身只有裁切、没有微反差，微反差必须手加，这是本卡的全部差别）；光标另起一个 3px 的色块层做位移关键帧。
  AE——`Linear Wipe`（Feather 0）作裁切，光标用 Shape Layer 的 Position 跟同一条 `cubic-bezier`（Graph Editor 里手拉），
  两侧的 `Fast Box Blur` + Position 各一组键；**别用 CC Light Wipe / Card Wipe** 那类带发光和碎块的。
- 与本库转场类的分工：**六式**（push-through / overexpose-flip / whip-pan / black-slam / pullback-cool / particle-weld）
  = 相机动量交接，边界是"镜头在动"，任何内容都能用；**shape-wipe** = 无相机系统时的轻量遮挡；
  **本卡** = 边界本身有语义（编辑器隐喻），只在内容真的与文本/代码/文档/生成结果有关时用。
  一个边界只用一式——本卡与六式**不叠加**（相机在推的同时又有一根光标扫过，两套空间逻辑打架）。

## 动效范围
- 属于本卡的：一个进度量同时驱动"新旧两层互补 `clipPath` + 光标位置"这条机制；两侧微反差（新场景 y +3→0 / blur 2→0 沉降解糊，旧场景 y 0→−6 / blur 0→4 上浮失焦，且被吃掉一侧的位移量约为新场景的两倍）；旧场景失焦起手延后 10% 进度、新场景解糊在 80% 进度前收完这两条时间纪律；`cubic-bezier(0.65,0,0.35,1)` 的末尾减速；3px 实色细条 + 屏高 50% + 骑在边界上 + 两端各 8% 进度淡入淡出的光标规格；"白底不加发光"这条取舍；两层左右严格等于画幅、只上下溢出的 inset 纪律；`onUpdate` 里直写 style 以避免光标与边界差一帧。
- 不属于本卡的：demo 两个场景的横线纸/点阵纹理与「刚被打出来」「被退格吃掉」这两个认式标签、灰阶取值（`#ffffff` / `#f1f1f4` / `#8a8a8a`）、光标的 `#1d1d1f`、hold A 0.8s 与 hold B 0.9s 这个排片（应用侧由叙事长度决定）、以及"两个场景是静态 tile"这件事（真实应用里两侧都是完整镜头）。
- 迁移接口：`caretWipe(out, inn, at)` 是唯一的调用入口——传两个铺满画幅的场景层与起始时刻；`wipe` 定快慢（唯一常改的参数）；`dir` 定"正在写"（right）还是"撤销回上一版"（left）；`inY/inBlur/outY/outBlur` 是**手感常量，换画幅不要按比例放大**（它们是"内容被编辑"的量级，不是相机的量级）；`caretW` 按分辨率取整（1080p 用 3px，4K 用 5~6px，避免半像素闪烁）；竖屏把 `caretH` 提到 0.6~0.7（竖幅里 50% 的光标显得太短）。
- 底色要求：白底/浅底最佳（光标是深色实条，靠对比成立）。深底场景把光标换成浅色实条即可，其余参数不变；**两个场景的底色不必相同**（demo 就是白 + 浅灰），但两侧都必须有铺满画幅的可辨识内容——纯色块会让中段之后的未到之处读作空白。

<!-- ===== /file: video-talkcraft/references/cards/caret-wipe-transition.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/chapter-progress-list.md ===== -->

---
name: chapter-progress-list
标题: 章节进度
优先级: P1
代码: template/cards/chapter-progress-list.tsx
一句话: 暗场里四条章节从右侧错峰 0.1s 滑进来，全部站定后**只有当前那一条**换成强调色、左边弹出一枚圆点、整行再往前一步，同帧四角电影角框向内收 10px 淡入把这一幕封住
适用: 长口播的分段处——"接下来第二部分"、"我们先说第一件事"；开场先给全片目录；多集系列片的"本集进度"；需要观众知道"讲到哪了、还剩几段"的时刻。不适合只有两段的短口播（两条列表撑不起一次转场）
时长: 起手静置 0.35s → 四条错峰滑入 0.65s → 高亮 + 角框 0.3s → 收尾 hold 2.0s；共约 3.3s
能量: 中
类别: 转场结构
输入: 文, 人(可选)
语义: 章节
素材形态: 无
位置: 中段
props: hostSrc
---

## 意图
长口播最大的流失点不是内容不好，是**观众不知道自己在哪**。听到第 7 分钟还在讲第二部分，
但他以为已经讲完一半了——于是走了。本库已有 `chapter-title-card`（一张幕标题卡砸出来），
它解决的是"新的一幕开始了"，但它**不给坐标**：观众看不到前面有几段、后面还有几段。

这张卡补的正是坐标：**把整份目录摆出来，然后指一下"你在这"**。观众一眼拿到三条信息——
全片有四段、当前是第二段、还剩两段。这三条信息合起来才叫"进度"，少一条就退化成标题卡。

命门三条：① **高亮只有一条**。两条高亮就没有"当前"这个概念，读作"这两段比较重要"；
② **未激活行靠 dim 实色区分，绝不叠透明度**（design-language §1 红线）。深底上 `#a1a1a6` 对 `#1d1d1f`
已经是安全对比，再叠 0.5 opacity 直接掉出可读区——它们是"还没讲/已经讲完"，不是"看不清"；
③ **四条全部站定之后才高亮**。滑入过程中就把第二条染红，读作"第二条飞得比别人快"，
"站定—点名"这两拍才是"指一下你在这"。

## 动效核心
- **层级**：暗场底（`#1d1d1f`）→ 人物层（左列）→ 章节列表（右侧，垂直居中）→ 四角角框（最上层）
- **① 列表入场**：四条 `x +24 → 0` + `opacity 0 → 1`，每条 `0.24s power3.out`，**错峰 0.10s**。
  表头（CHAPTER）提前 0.06s 单独淡入 0.22s——它是标签不是列表项，不参与错峰序列
- **② 高亮（全部到位 + 0.06s 呼吸后）**，三条属性同帧同 0.20s：
  - 编号与标题 `color: #a1a1a6 → #e0452c`（`power2.out`）
  - 左侧圆点 `scale 0 → 1`（`back.out(2)`——唯一允许回弹的件，它是"落点"）
  - 整行 `x 0 → +6px`（`power3.out`）：在列表里"站出一步"
- **③ 四角角框**：与高亮**同帧**起，`x/y` 从各自外侧 ±10px 收到 0 + `opacity 0 → 1`，`0.30s power2.out`。
  比高亮慢（0.30 vs 0.20）、比高亮淡——它是**衬**，抢了就散
- **④ hold 2.0s**：四条章节 + 一个当前位置，观众要读三遍才拿到"进度"这个信息
- **未激活态是终态**：`#a1a1a6` 实色。`opacity` 只出现在入场那 0.24s 里，落定后回到 1，
  静置态没有任何一件叠着透明度

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `rowStagger` | 0.10s | 行错峰，本卡的"一串感"旋钮；>0.2s 读作四个独立动效（观众会去数），<0.05s 读作整块淡入（丢掉"逐条列出"的语义） |
| `rowIn` | 0.24s | 单行滑入耗时；>0.4s 四条加起来 1.6s，转场变拖沓；<0.15s 看不出行与行的先后 |
| `rowShift` | 24px | 从右侧进入的位移；0 只剩淡入（少了"从边上推进来"的方向），>60px 读作横向飞入（抢过高亮那一拍） |
| `hlDelay` | 0.06s | **命门**：全部站定 → 高亮 之间的呼吸；0 会读作"最后一行特殊"，>0.3s 两拍断开、观众以为动效已经结束了 |
| `hlAdvance` | 6px | 当前行额外前进量；0 少了"站出一步"的身体感，>16px 读作这一行被拽出列表（对齐关系破掉） |
| `cornerInset` | 10px | 角框向内收的距离；0 只剩淡入（没有"合拢封场"），>24px 读作四个角在飞（衬的位移超过主体位移就抢戏） |
| `cornerDur` | 0.30s | 角框耗时，**必须大于 `hlDur` 0.20s**——衬比主体慢是层级纪律 |
| 章节条数 | 3~5 条 | 2 条撑不起"进度"（用 `chapter-title-card`），>6 条读作菜单不是章节表，且行高压缩后 dim 行糊成一片 |
| `hold` | 2.0s | 收尾停留；<1.2s 观众只读到高亮那一行，"还剩几段"这条信息没拿到 |

## 已知坑
- 未激活行叠 `opacity: 0.45` 来"压下去"——深底上 `#a1a1a6` 叠透明度后对比度掉到 2:1 出头，
  观众读不出那几行写了什么，"全片有四段"这条信息直接失效（design-language §1 红线）。
- 两条以上高亮——"当前"这个概念是唯一性给的，高亮两条读作"这两段重要"，进度语义归零。
- 高亮在滑入过程中就发生——读作"第二条跑得比别人快"，而不是"点名第二条"。
- 圆点用 `elastic` 或 `back.out(4)` 弹——它是一个直径 10px 的点，大回弹在这个尺寸上只会读作抖动。
- 角框做成四条完整边框——那是"取景框/画框"，是另一种语言；电影角框只画四个角的 L。
- 角框比高亮更快更亮——衬抢主体，一屏两个重音，转场读作花屏。
- 在白底上做这张卡——章节转场的语义是"幕间暗场"，白底上四条列表读作"页面上的目录"，
  少了"这里是一个切口"的转场性质（本卡是全库唯一为此破白底默认的列表卡，理由见「动效范围」）。
- 深底照抄浅底的 `#8a8a8a` 做 dim——深底模式的 ink-muted 是 `#a1a1a6`，`#8a8a8a` 在 `#1d1d1f` 上
  只有 3:1 出头，未激活行直接沉进底里。
- 重播只重置 transform 不重置 `color`——高亮是"改属性"，上一轮的红会留在第二行，
  第二遍播放时它一开场就是红的，"站定—点名"两拍全丢。

## 复用指引
- props：仅 `hostSrc`；章节名与当前项（`current: true`）在 `ROWS` 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/chapter-progress-list.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/chapter-progress-list/index.html。**换内容改 `.ch-row` 的文案**，
  当前章节把 `current` 类挪到对应行（圆点 `<span class="ch-dot">` 跟着挪）。节奏全在 `CONFIG`：
  `rowStagger` 调"一串感"、`hlDelay` 调两拍之间的呼吸、`hold` 按条数给（每条约 0.5s）。
  换强调色只改 `CONFIG.accent` 与 `.ch-dot` 的 `background` 两处。
  角框的臂长在 `.cine-corner` 的 `width/height`（42px @540h ≈ 7.8%，换尺寸等比）。
- Remotion 移植：一个 `<Sequence>` 装列表，第 i 行 `from={Math.round(i*0.10*fps)}`，
  行内 `interpolate` 驱动 `translateX` 与 `opacity`（`Easing.out(Easing.cubic)`）。
  高亮那一拍单独一个 `Sequence from={hlFrame}`，用 `interpolateColors(frame, [hlFrame, hlFrame+6], [dim, accent])`
  换色（**别用 CSS transition**，帧驱动下不可复现）；圆点用 `spring({damping: 12, stiffness: 200})`。
  角框四个用同一个 `interpolate` 出 `inset` 值，各自乘 ±1 定方向。
- 剪辑软件对应物：剪映/CapCut——四条文本层 + 关键帧"位置 + 不透明度"，逐层往后拖 3 帧（0.1s）；
  高亮那一行**要复制成两层**（灰的一层、红的一层）在高亮点硬切，剪映做不出文字颜色的补间；
  圆点用一个圆形贴纸 + 缩放关键帧。AE——列表做成一个预合成，
  `Animate → Position + Opacity` + `Range Selector` 的 `Offset` 走 −100%→0%（`Ease High` 拉满），
  高亮行单独一层加 `Fill` 效果对 Color 打两个关键帧；角框四层 `Position` 关键帧 + 父级绑到一个 Null。
- 与本库同类卡的分工：`chapter-title-card` = 一张幕标题砸出来（有转场性质、不给坐标）；
  **本卡 = 给坐标的章节转场**（目录 + "你在这"）；`numbered-step-stack` = 清单堆叠（讲操作步骤，
  四条是并列的动作，没有"当前"的概念）；`step-timeline-vertical` = 时间轴推进（有先后依赖）。
  三张列表卡的分工是：本卡答"讲到哪了"、`numbered-step-stack` 答"要做哪几件"、
  `step-timeline-vertical` 答"按什么顺序做"。

## 动效范围
- 属于本卡的：四行 `x +24 → 0` + `opacity` 的错峰滑入（`0.10s` 错峰 / 每行 `0.24s power3.out`）这条时序；**未激活行用 dim 实色、静置态零透明度**这条纪律；"全部站定 + 0.06s 呼吸 → 才高亮"这两拍的先后；高亮的三属性同帧组合（换色 + 圆点 `back.out(2)` 弹出 + 该行 `x +6px`）；**高亮唯一性**（只有一条）；四角角框与高亮同帧、但更慢更淡（`0.30s` vs `0.20s`）这条主/衬层级；`hold 2.0s` 让"还剩几段"这条信息被读到。
- 不属于本卡的：demo 里那四条具体章节名与「CHAPTER」这个表头字样、`#e0452c` 这个强调色（取参考图①暖色系，换任意 accent 都成立）、23px/15px 的字号与 600 字重、列表落在右侧、左列的数字人占位、角框 42px 的臂长与 2px 描边宽、行高与 `gap`。
- 迁移接口：颜色三个 token —— `CONFIG.accent`（强调色）、`CONFIG.dim`（未激活行实色，浅底用 `#7a7a7a`、深底用 `#a1a1a6`）、底色；尺寸基准 `rowShift 24px` 与 `cornerInset 10px` 都按舞台宽等比（960 ⇒ 1920 时翻倍）；时长缩放规则 —— `rowStagger` 是**手感常量不要动**，`hold` 按章节条数给（每条约 0.5s）；竖屏把列表改成整屏居中、条数收到 3~4 条（竖屏行宽够但屏高被 UI 吃掉）。
- 底色要求：**需要深底 `#1d1d1f`（本卡是本组唯一的例外）**。理由：本卡的语义不是"页面上的一份目录"而是**一次章节转场**，而转场在视频里的读法是"幕间暗场"——画面暗下来、目录浮出来、指一下当前位置、再回到内容。白底上做同样的动效，观众只会读作"屏幕上多了个列表"，缺的正是"这里是一个切口"这层意思（design-language §4 明写"底色交替就是章节感"，浅底 ↔ 深底的切换本身就是分隔符）。深底同时是列表可读性的前提：四条 dim 行在暗场上是"还没亮起的灯"，在白底上则是"没印清的字"。深底模式下配套换值：`ink` 用 `#f5f5f7`、`ink-muted` 用 `#a1a1a6`、角框用 `#d2d2d7` 实色（**不加 blur/glow**——发光是另一套语言）。

<!-- ===== /file: video-talkcraft/references/cards/chapter-progress-list.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/chapter-title-card.md ===== -->

---
name: chapter-title-card
标题: 章节标题卡
一句话: 段落切换时全屏色块 0.3s 压入盖屏，屏高 40% 的章节编号先落位，章节名随后从编号旁遮罩揭示，停 1.2s 后色块同向扫出切回口播；每章一套主题色 + 一个与本章内容相关的线稿 motif 在色块盖屏后于背景描出，章节名下一条 accent 短线接上
适用: 长口播（5 分钟以上）的段落切换点；财经解读、事件复盘、纪录片式叙事等需要"翻页感"的调性
时长: 单卡约 2.5s：扫入 0.3s + 编号 0.4s + 章节名 0.35s + hold 1.2s + 扫出 0.3s；两卡示范间隔 0.7s
能量: 高
类别: 转场结构
输入: 文, 人(可选)
语义: 章节, 转场
素材形态: 无
位置: 中段
props: hostSrc, themes
优先级: P0
代码: template/cards/chapter-title-card.tsx
---

## 意图
长口播讲到第 4 分钟观众注意力必然涣散——章节卡是一次强制"翻页"，让观众喘口气并重置预期（"哦，进入新话题了"）。
命门：**层次**（编号先落位立骨架，章节名再进——同时出现层次就塌了）、
**不呆滞**（hold 期间整组带极缓漂移，完全静止 1 秒读作视频卡帧）、
**快进快出**（全程 ≤2.5s，转场比内容还长就是喧宾夺主）。

常见于：差评君、小Lin说、LEMMiNO、Johnny Harris、IC实验室。

## 动效核心
- 全屏色块 `.chapter-card`（品牌色/深色，flex 居中排编号+文字组）：`xPercent -100 → 0`，0.3s，`power4.inOut`，从左压入盖住口播画面
- 章节编号 `.chapter-num`（衬线体 Georgia/宋体，216px ≈ 屏高 40%）：色块盖屏后 opacity 0→1 + scale 1.3→1，0.4s，`power3.out`
- 章节名 `.chapter-name`：外层 `overflow:hidden` 容器内做 `clip-path: inset(0 100% 0 0) → inset(0 0% 0 0)` 侧向遮罩揭示，0.35s，`power3.out`，起点比编号晚 0.18s
- 小字戳 `.chapter-sub`（英文章节号+日期，字距拉大）：比章节名再晚 0.1s，opacity 0→1 + x -14px→0，0.3s
- hold：编号与文字组整体 x 0→10px 线性漂移贯穿停留期（1.7s），防卡帧感
- 出场：色块继续同方向 `xPercent 0 → 100`，0.3s，`power4.in`，露出底下口播画面（主持人+字幕区一直在色块下层没动过）
- **主题层（2026-09-07 加）**：色块盖屏后 +0.05s，本章 motif（200×200 viewBox 的线稿，右下 1/4、240px ≈ 屏高 45%、上缘在文字组之下、`opacity .14`、stroke = 本章 ink）各段 `pathLength=1` 的 dashoffset 1→0 接力描画共 0.5s（`power2.inOut`）；它在 L6 背景层，**不参与**编号 / 章节名 / 小字的三层错峰；hold 漂移按 ×0.6 跟（背景更慢 = 深度）
- **accent 短线**：章节名揭示完的那帧起，名字下方 72×3 的本章 accent 色线 `scaleX 0→1` 0.25s `power3.out`（origin left）——一章一色的签名，也是章色里 accent 的唯一出场
- demo 连演两张卡（01 墨 + 泡沫曲线 motif → 02 中灰 + 门与箭头 motif），中间回到口播 0.7s，示意真实节奏

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `wipeIn` | 0.3s | >0.5s 像幕布拉过没有"压入"劲；<0.2s 观众没意识到发生了转场 |
| `numIn` | 0.4s | 编号是骨架，太快（<0.25s）立不住；太慢挤压后面节拍 |
| `nameIn` | 0.35s | 遮罩揭示再慢就读作"加载中"；比编号晚 0.18s 起是层次的来源 |
| `subDelay` | 0.1s | 小字与章节名的错峰；0 则三层同出层次塌掉 |
| `hold` | 1.2s | 观众读完标题所需时间；>2s 拖节奏，<0.8s 长标题读不完 |
| `driftPx` | 10 | hold 期防呆滞的漂移量；>20px 读作运镜失误，0 则像卡帧 |
| `wipeOut` | 0.3s | 出场比入场可略快；用 `power4.in` 加速离场才有"翻过去"感 |
| `gapBetween` | 0.7s | 两章之间回口播的间隔，仅 demo 示范用；实际由口播内容决定 |
| `motifIn` | 0.5s | motif 描画总时长（各段接力）；>0.8 会拖到章节名之后还在画，抢层次；<0.3 像闪现 |
| `motifOpacity` | 0.14 | 0.12~0.18 是"纹样"区间；>0.25 变成第二个主角与编号打架；<0.1 白画 |
| `motifParallax` | 0.6 | motif 漂移倍率；1.0 = 与文字同速没有深度；0 = 背景死住，hold 期只剩文字在漂 |
| `ruleIn` | 0.25s | accent 短线长出时长；它接在章节名揭示完之后，提前会与遮罩揭示抢同一条视线 |

## 已知坑
- 编号和章节名同帧出现——没有先后就没有层次，读作一张静态 PPT 突然糊上来。
- hold 期间所有元素完全静止——观众会怀疑视频卡了；极缓漂移是"活着"的最低成本证明。
- 全程超过 2.5s——转场比正文还隆重，观众等得不耐烦，一眼业余。
- 编号用细无衬线小字——章节感靠的就是超大衬线编号的"书卷分量"，缩小或换细体立刻廉价。
- 色块出场换方向（从右回弹）——观众预期"翻页"是单向的，来回晃读作撤销。
- 四章同一块色板、同一个 motif（或干脆没有 motif）——四张卡长得一样，观众第三次看到时已经不把它当"翻页"，只当"又来了"（2026-09-07 用户反馈：章节卡太单调）。
- motif 画成实心图标、亮度和编号一样——背景纹样变成第二主角，编号 / 章节名的层次被搅乱；motif 是纹理不是图标。
- motif 与本章内容无关（随手放个几何装饰）——装饰性元素违反"内容即主角"；motif 必须能一句话说出它和本章的关系（讲速度 = 仪表 / 讲写作 = 笔迹 / 讲离场 = 门）。

## 复用指引
- props：`hostSrc`、`themes`（`ChapterTheme[]`：每章 bg / ink / accent / motif）；编号 / 章节名 / 小字文案在 JSX 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/chapter-title-card.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/chapter-title-card/index.html。换文案改 `.chapter-num` / `.chapter-name` / `.chapter-sub` 内文本；换色改 `.chapter-card.c1` / `.c2` 的 `background`；节奏全部在顶部 `CONFIG`（`wipeIn`/`numIn`/`nameIn`/`subDelay`/`hold`/`driftPx`/`wipeOut`/`gapBetween`）。加第三章 = 复制一段 `.chapter-card` DOM + 在 register 里多调一次 `chapterBeat(tl, cards[2], at)`。核心节拍函数 `chapterBeat` 可整段摘走。
- Remotion 移植：每章一个 `<Sequence>`；色块用 `interpolate(frame, [0, wipeIn*fps], [-100, 0], {easing: Easing.inOut(Easing.quart)})` 驱动 `translateX%`；编号 scale/opacity 与章节名 `clipPath` 的 inset 百分比同样用 interpolate（`Easing.out(Easing.cubic)`）；hold 漂移是一条贯穿的线性 interpolate；出场放同一 Sequence 尾部用 `Easing.in(Easing.quart)`。
- （实测变体）暗色纹理版：黑底 + 星座粒子 + 同心环做底，eyebrow 英文小字先出、主标衬线大字随后、副字再延迟 0.4s——三层错峰的骨架不变，只把"品牌色块"换成有纹理的暗场，适合叙事更重的长片开幕。见小Lin说·韩股崩盘。
- （实测变体）荧光菱形徽章版：不用满屏色块压入，而是一枚菱形渐变徽章带章节数字从小弹大立在画面中，截图卡随后升入接管画面——章节卡与素材入场合成一拍，比"盖屏再揭开"省 0.5s，适合竖屏快节奏。见 TheAIScaler（Apm_oCzPEQs）。
- 剪辑软件对应物：剪映"文字模板→片头/章节"类 + "向右擦除"转场叠色块；AE 里是纯色层 Position 关键帧（Easy Ease 拉重入场）+ 文字层 Scale 关键帧 + 轨道遮罩（Track Matte）做章节名揭示；CapCut 搜 "chapter title" 模板。

## 动效范围
- 属于本卡的：全屏色块 `xPercent -100→0` 压入盖屏（0.3s、`power4.inOut`）；本章 motif 在盖屏后 +0.05s 于 L6 背景层接力描画 0.5s 并以 0.6× 跟随漂移；章节名揭示完后 accent 短线 `scaleX 0→1` 0.25s；编号 opacity 0→1 + scale 1.3→1 落位（0.4s、`power3.out`，在色块盖屏之后）；章节名 `clip-path inset(0 100%→0)` 侧向遮罩揭示（0.35s，比编号晚 0.18s）；小字再晚 0.1s 的 opacity + x −14→0；hold 期整组 x 0→10px 线性漂移防卡帧；色块**同方向**继续 `xPercent 0→100` 扫出（0.3s、`power4.in`）。这七段的先后与那条单向进出的运动语言就是本卡全部。
- 不属于本卡的：每章具体的 bg / ink / accent 色值与 motif 图形（demo 的泡沫曲线 / 门与箭头只是示例，成片按本章内容重画）、编号的衬线字体与 216px 字号、章节名/小字的具体文案与字距、底下口播画面（主持人占位 + 字幕）、demo 连演两张卡与 `gapBetween` 间隔（仅示范节奏，实际由口播内容决定）。
- 迁移接口：**章节主题 = 复用者的品牌色接口**——tsx 改 `DEMO_THEMES` 或给组件传 `themes`（`ChapterTheme = { bg, ink, accent, motif }`，每章一套；demo 收敛成中性灰阶两档 #1d1d1f / #55565a，换成本片色板派生的章色即可）；demo 对应改 `.chapter-card.c1` / `.c2` 的 `background` 与 `--ink` / `--accent`，motif 换 `<svg class="chapter-motif">` 里的 path；节奏全在顶部 `CONFIG`（`wipeIn`/`numIn`/`nameIn`/`subDelay`/`hold`/`driftPx`/`wipeOut`/`motifIn`/`ruleIn`）；编号字号按屏高 40% 折算，换尺寸时同比缩放；加章节 = tsx 多放一个 `<ChapterCard theme={themes[n]}>`，demo 复制一段 `.chapter-card` DOM + 多调一次 `chapterBeat`。扫入扫出方向要保持同向，改方向须同时改两处。
- 底色要求：白底即可（色块自带满屏遮盖，底色只在色块进出的前后两拍露出）。色块本身必须与底色有足够明度差，白底配深色块、深底配亮色块。

## 章节主题层（2026-09-05 配色轮换 + 2026-09-07 主题 motif，选卡时抄进 SHOTBOOK 该镜自检列）
- **章节卡底色按章轮换**，禁止每章同一黑：深底 4 套 藏蓝 `#0f1e3d` / 墨绿 `#10261f` / 酒红 `#2b1218` / 炭黑 `#16161a`，或从本片色板派生 4 套浅底；编号与章节名用对比色随底切换（layout.md §7）。
- 编号 + 章节名整组包围盒居中（无人物）；编号（衬线 216px）与章节名基线对齐、间距取令牌 48。
- **一章一套主题 = 底色 + 字色 + accent + motif 四件**（tsx 的 `ChapterTheme`）：accent 只在章节名下的短线出场（不许给编号或章节名整字换色）；四章的 accent 可以是同一条 accent 的四个明度档，也可以取本片色板派生的四色，但底色必须四章不同。
- **每章一个与本章内容相关的线稿 motif**：先用一句话写出关系（"第 1 章讲速度 → 仪表 / 秒表"、"第 4 章讲写作 → 笔迹 / 稿纸行"），再从本片风格档的图标体系（线稿集或自画 ≤30 行 SVG，200×200 viewBox）取形；四章不得复用同一个 motif；motif 是纹样不是图标——`opacity .12~.18`、右下 1/4（上缘在文字组之下，下缘可出画）、屏高 ≈45%、只描边不填充。
- motif 在色块盖屏后 +0.05s 开始描画、0.5s 画完，**不改**编号 / 章节名 / 小字的三层时序；hold 漂移 ×0.6。
- SHOTBOOK 该镜必须写**章节主题行**：`第 N 章 · 底色 #… / accent #… / motif = <形> ← <与本章的关系一句话>`，四行并列一眼可核"不重、相关"。
- 定妆帧自检：motif 不与编号 / 章节名 / 小字包围盒相交（motif 上缘 60% 屏高、文字组竖向居中即可）；accent 短线左缘 = 章节名首字左缘；四张卡的 motif 描边宽度一致（3px@960）。

<!-- ===== /file: video-talkcraft/references/cards/chapter-title-card.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/chart-grow.md ===== -->

---
name: chart-grow
标题: 图表生长
一句话: 坐标轴先 0.3s 淡入立好舞台，柱子从 0 依次错峰长出、柱顶数字跟着弹出，最高的关键柱高亮并触发一次轻 punch
适用: 口播里念数据对比的段落（"营收翻了七倍"）；财经/科普/评测类横屏视频的标配，配合逐项列举的语速
时长: 起手 0.2s → 轴 0.3s → 柱 0.55s 起、每柱 0.5s、错峰 0.13s（最高柱 1.57s 到顶）→ 关键柱 punch 0.3s；5 柱全程约 1.9s
能量: 中
类别: 数据信息图
输入: 文
语义: 数据, 对比
素材形态: 无
位置: 任意
props: 无
优先级: P0
代码: template/cards/chart-grow.tsx
---

## 意图
让数字"长"出来而不是贴出来——生长的先后顺序就是口播的列举顺序，观众的眼睛跟着话走。
命门：**轴先柱后**（没有坐标系柱子就没有量级）、**逐根错峰**（同时长出=没有"逐项列举"的语感）、
**y 轴满量程全程固定**（中途缩放，柱子间的对比就是骗人）。

常见于：小Lin说（signature）、回形针、Vox、Wendover、Infographics Mega Bundle（2.2K 销量）。

## 动效核心
- 第一拍：轴线 + 网格线 + 图题 opacity 0→1，0.3s power2.out
- 柱子：每根 scaleY 0→1（transform-origin 底部）0.5s power3.out，柱间 stagger 100~150ms
- 柱顶数字：在该柱长到约 72% 进度（`labelPopAt`）时 scale 0.4→1 + opacity 弹出（back.out(2)），和柱到顶几乎同帧
- 层级色：普通柱灰调（白底 demo 用 #d2d2d7），关键柱（最高/结论柱）用语义高亮色（demo #d8383a）且数字更大——重要的是"一根有色其余灰"的关系，色值随风格换
- 收尾：关键柱到顶瞬间整图 scale 1→1.03→1 轻 punch 一拍（0.08s 上 + 0.22s back.out 回）

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 单柱生长 | 0.5s | >0.8s 观众等得着急；<0.3s 五根柱挤成一团动 |
| 柱间错峰 | 130ms | >250ms 拖成逐个介绍；<80ms 读作同时长出 |
| `labelPopAt` 数字弹出时机 | 柱进度 72% | 柱到顶后才出像贴上去的；柱刚起就出剧透终值 |
| 关键柱颜色 | 一根高亮其余灰 | 根根有色=没有结论；灰柱是给红柱当背景板的 |
| punch 幅度 | 1.03 | >1.06 图表在跳舞；不 punch 结论柱就没有"落锤"感 |
| y 轴满量程 | 固定（demo 100） | 跟着最大值动态缩放，柱高对比全部失真 |

## 已知坑
- 所有柱同时长出——没有"第一年、第二年……"的语感，信息密度归零。
- y 轴中途改刻度——85 的柱子看起来只比 45 高一点，数据欺诈既视感。
- 标签和柱不同步——柱停了数字才慢悠悠出现，像两个人做的动画。
- 柱子用 height 动画而不是 scaleY——布局回流卡顿，低端机掉帧。

## 复用指引
- props：无；数据 / 年份 / 高亮列在 `COLS` 常量里（`hot: true` 标关键柱），图题在 JSX，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/chart-grow.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/chart-grow/index.html，改 `.bar-col` 的 `data-v` 与年份文字即可换数据（高度自动按 `CONFIG.maxVal` 计算）；关键柱挪 `hot` class；节奏在 `CONFIG`。
- Remotion 移植：tsx 逐帧 tween——柱 `tw(t, 0.55 + i×barStagger, barGrow, power3Out)` 驱动 scaleY；数字在该柱 `barGrow × labelPopAt` 后 0.25s `back.out(2)` 弹出；punch 在最高柱到顶时 0.08s 推到 1.03、再 0.22s `back.out(3)` 回 1。
- （实测变体）分组错峰：多指标分组时不是逐柱 stagger，而是**逐组**从左到右出现（组间约 0.5s），组内多柱同时生长——错峰层级从"根"提到"组"，对齐口播的"第一个季度……第二个季度……"；全组长完后一个大数字结论压顶弹出收尾。见 TheAIScaler（Apm_oCzPEQs）。
- 剪辑软件对应物：剪映"图表"贴纸只有成品样式，精细版要 AE（矩形层 scale 关键帧 + 锚点置底）或 PR MOGRT；Excel 录屏是反面教材。

## 动效范围
- 属于本卡的：坐标轴 + 网格 + 图题 opacity 0→1（0.3s、power2.out）打头的"先立坐标系"一拍；每根柱 scaleY 0→1（0.5s、power3.out、transform-origin 底部）、柱间 stagger 100~150ms 的逐项列举节奏；柱顶数字在该柱约 72% 进度时 scale 0.4→1 + 淡入弹出（0.25s、back.out(2)）；y 轴满量程全程固定这条约束；关键柱到顶瞬间整图 scale 1→1.03→1 轻 punch（0.08s 上 + 0.22s back.out(3) 回）；"一根高亮、其余灰"的层级色关系（哪根被高亮属于本卡，具体色值不属于）。
- 不属于本卡的：具体数据与年份文案、柱宽/圆角/间距、网格线密度、字幕行与图题文字、高亮色的具体色值。
- 迁移接口：数据改 `.bar-col` 的 `data-v`，高亮柱挪 `hot` class（tsx 改 `COLS` 的 `v` / `hot`）；`maxVal` 定满量程（必须固定）；`barGrow` / `barStagger` 按列举语速整体缩放；`labelPopAt` 调数字与柱到顶的同步；`punchScale` 调结论落锤力度；配色只需两个 token——常规柱灰阶 + 关键柱语义色（柱顶数字与字幕强调词跟着关键柱色走）。
- 底色要求：白底即可（轴 #c8c8cc、网格 #ececef、常规柱 #d2d2d7）。深底把这三层反相为深灰阶、关键柱色保持高饱和即可，时序不变。

<!-- ===== /file: video-talkcraft/references/cards/chart-grow.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/chat-gpt.md ===== -->

---
name: chat-gpt
标题: ChatGPT 对话框
优先级: P1
代码: template/cards/chat-gpt.tsx
一句话: ChatGPT 首屏三件套按阅读顺序错峰淡入（问候大标题 → 药丸输入条 → 建议 chips，位移带视差），提示词逐字打进单行药丸、圆形语音键**原地变形成圆形发送键**且建议 chips 同时淡出下移，发送后问候语退场让位给对话，回答分块流式吐出
适用: 口播讲 AI 话题时把「我是这么问的、它是这么答的」演成现在进行时——ChatGPT 相关的提示词技巧、AI 工具测评、模型能力讨论；不适合需要展示长对话历史的场景（自演只演一问一答）
时长: 三段错峰入场 0.13→1.07s → 1.40s 起打 → 打字 1.41s（12 字 @8.5 字/s）+ 0.33s → 发送 → 思考 0.52s → 流式回答 1.50s；整卡约 6.4s
能量: 中
类别: 素材呈现
输入: 界, 人(可选)
语义: 过程演示, 例证
素材形态: 界面
位置: 任意
props: hostSrc
---

## 意图
**AI 产品界面自演比对话截图值钱**：截图是"事后的证据"，自演是"正在发生"——观众看着提示词一个字一个字打进去、
按钮变形、回答流式吐出来，那句"我是这么问的、它是这么答的"就成了现在进行时。
本卡演的是 ChatGPT 的首屏语法：**单行药丸**（一次一句话，不是一段长提示词）、**建议 chips 摆在输入条下面**
（首屏在教你能问什么）、**问候语占据画面正中**（首屏是空的，对话开始才让位）、morph 是**圆 → 圆**
（形态不变，只换图标与底色）、点睛色在**语音**端而不是发送端。这五条是这个产品的取向，不是随便定的样式。
**产品皮 = 内容本身（2026-08-25 用户定版）**：本卡涉及真实产品界面，所以**完全还原 ChatGPT 的样式**，
不做中性化——`#0D0D0D` 墨字、`#E3E3E3` 药丸描边、`#F4F4F4` 用户气泡、`#2F6FED` 语音键、`#9B9B9B` 占位灰、
助手位那朵 OpenAI 结，全部照抄源码 `THEMES.light` + `accentColor`。理由：观众要一眼认出"这是 ChatGPT"——
灰阶化之后它退成"某个聊天框"，上面那五条产品取向全部读不出来，这张卡就只剩一个通用打字机了。
可编辑的是**内容**（问候语/提示词/回答/chips 文案），外观不动。

命门：**三段错峰的位移视差**（源码给标题 ×0.4、药丸 ×0.6 两个不同乘数——同一个弹入里三层不齐步，
拉平了就是"整块一起飘上来"的模板感）、**chips 随 morph 退场而不是随发送退场**（"手一落键，建议就不需要了"
是这个产品的因果，等发送才退就慢了半拍）、**chips 一去不回**（退场跟不回退的 morph 正向进度，
否则发送键回退语音态时 chips 会跟着回来，读作"首屏又回来了"）。

## 动效核心
- **三段错峰淡入（本卡的入场骨架）**：问候标题 `[0.13, 0.67]` → 药丸 `[0.33, 0.87]` → chips `[0.53, 1.07]`
  （源码 `fadeUpAt[4,20] / [10,26] / [16,32]`），各带 9px 上移。**错峰顺序 = 阅读顺序**（先看标题、再看输入框、最后看建议）
- **位移视差（最易漏掉的一处）**：同一个弹入位移（`introY` 21px，0.62s `back.out(1.05)` 近似源码 spring），
  标题乘 **0.4**（`greetPar`）、药丸与 chips 乘 **0.6**（`pillPar`）——远的元素动得少。这两个乘数的差就是全部视差来源，
  拉平成同一个值立刻退化成"整块一起飘上来"
- **1.40s 起打**（源码 `TYPING_START_FRAME 42`）：静置留给口播开口
- **逐字揭示，不分块**：中文 8.5 字/s（源码 `TYPING_CPS 22` 是英文字符速率）。
  药丸是**单行 `nowrap`**——提示词长度有硬上限（这也是这个产品的语法：一次一句话）
- **输入光标两态**：有字时跟在文本尾（插入点），空态时在占位文案前；打字中实心不闪，
  未开打 / 打完待发才 1Hz 闪（`caretHz`）
- **morph（圆 → 圆）**：同一个 33px 方框里两个**都是圆**的图层交叉，与打字**同帧**开始、0.40s 完成——
  语音圆（点睛色底 + 白波形）`opacity 1 → 0` + `scale 1 → 0.9`，发送圆（墨底 + 白箭头）
  `opacity 0 → 1` + `scale 0.8 → 1` 带 `back.out(1.7)`。
  **形态不变，只换图标与底色**——morph 有两种形态路线（圆 → 圆、圆 → 方角），这个产品走的是圆 → 圆
- **点睛色在语音端**：源码把 accent（`#2F6FED`）给了 morph 的**起**端（语音键），发送键是墨色 `#0D0D0D`。
  accent 给起端还是终端是产品的取向差（有的产品反过来把亮色留给发送键）——**这个产品在语音端**，别顺手改
- **chips 随 morph 退场**：`opacity ×= (1 − morph)`、下移 6px × morph——源码独有的一拍，
  因果是「开始输入了，建议就不需要了」。退场跟的是**不回退**的 morph 正向进度：
  发送键可以在发出后退回语音态（输入框空了），但 chips 一旦进了对话就不该回来
- **发送键按压**：`sendAt` 为中心 ±0.11s 的时间窗内 `scale 1 → 0.86 → 1`
- **问候语退场 0.30s**：发送那一帧起淡出，与用户消息块弹入**交叉**（首屏让位给对话）。
  两者位置错开一档（会话区在问候语上方），交叉期不会读作两层内容打架；
  但**打字期间问候必须还在**——那是「首屏还没提交」的唯一证据
- **用户消息块弹入 0.42s**：发送同帧占位，`y 10 → 0` + `scale .95 → 1` + 淡入，浅灰圆角块靠右
- **思考标识 0.52s**：助手位的几何**圆**以 1.2Hz 呼吸（只改亮度，不做位移不做抖动），流式一开始即撤
- **流式回答分块吐**：`revealed = min(len, ceil(linear / 2) × 2)` @22 字/s，尾巴挂块光标、吐完即撤，
  **回答无气泡**（纯文本 + 左侧 OpenAI 结标识）
- **层级**：白底舞台 → 问候标题（与会话区共用同一条基线带，一淡出一淡入，零布局动画）→ 会话区 → 药丸（阴影浮起）→ chips

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `greetPar` / `pillPar` | 0.4 / 0.6 | 位移视差的两个乘数，本卡入场的命门；两者相等（无论取什么值）立刻退化成"整块一起飘上来"的模板感；差值 >0.4 则标题几乎不动、读作两组元素不属于同一次入场 |
| 三段错峰间距 | 0.20s | 标题 → 药丸 → chips 的起点间距；<0.1s 三段糊成一段（错峰白做），>0.4s 观众等最后一段等得住急 |
| `cps` | 8.5 字/s（中文） | 打字速率，≈3.5 帧/字；<6 观众开始读输入框，>12 读作机器代打。英文提到 18~22 |
| `typeStart` | 1.40s | 起打前静置（源码第 42 帧）；要 ≥ chips 淡入结束（1.07s），否则首屏还没摆好就已经在打字 |
| `morphDur` | 0.40s | 语音圆 → 发送圆；<0.2s 读作硬切换图标，>0.7s 观众盯着按钮不听你讲 |
| morph 起点 | **= 打字起点** | 等打完才 morph 就退化成「打字机」加「按钮换图标」两件不相干的事；同帧起才是"界面在实时响应输入" |
| `chipsOutY` | 6px | chips 退场下移量；=0 则只是淡出（少了"让位"的方向感），>14px 读作被踢下去 |
| chips 退场触发 | **morph 正向进度** | 跟 `sendAt` 就慢半拍（打字期间建议还赖在那儿）；跟**会回退**的 morph 值则 chips 会在发送后回来，读作"首屏又回来了" |
| `greetOut` | 0.30s | 问候语退场；触发必须是 `sendAt` 而不是打字起点——打字期间问候还在，那是"首屏还没提交"的证据 |
| `sendGap` | 0.33s | 打完到按下发送的停顿；=0 读作自动脚本，>0.6s 观众以为卡住 |
| `thinkDur` | 0.52s | 首 token 之前的思考；<0.3s 看不出"它在想"，>1.2s 观众开始等 AI |
| `streamRate` / `streamChunk` | 22 字/s / 2 | 流式速率与分块；`chunk=1` 退化成逐字匀速（打字机不是流式），`chunk>4` 读作整句硬切 |
| 提示词长度 | 10~14 字 | 单行药丸的硬上限（616px @14.5px 不折行）；超了就不适合这个形态（这个产品的语法就是一次一句话），该换宽卡 composer 类的界面去演 |
| 回答长度 | 28~36 字 | 单行不折行的上限；折两行以上观众切换到"读回答"模式 |

## 已知坑
- 三层位移用同一个乘数（视差拉平）——入场退化成"整块一起飘上来"，本卡入场编排的全部价值消失。
- 三段错峰改成同时淡入——错峰白做；顺序必须是阅读顺序（标题 → 输入框 → 建议）。
- chips 等到发送才退——慢半拍，打字期间建议还赖在下面；因果是"手一落键就不需要了"。
- chips 退场跟着**会回退**的 morph 值——发送键退回语音态时 chips 跟着回来，读作"首屏又回来了"；必须跟不回退的正向进度。
- 问候语在打字期间就退——丢掉"首屏还没提交"这层状态；它必须活到发送那一帧。
- 问候语与用户消息在同一位置硬切——两层内容在同一帧打架；两者位置错开一档、淡入淡出交叉才干净。
- morph 等打完才开始——退化成「打字机」加「按钮换图标」两件不相干的事。
- morph 做成圆 → 方——那是宽卡 composer 类产品的形态；这个产品是圆 → 圆（只换图标与底色），改了就不是它了。
- 点睛色给发送端——同上，这个产品的 accent 在**语音**端；两张卡的这个方向差是做对比视频时的内容。
- 回答套气泡——退回成普通聊天卡，AI 产品的界面语法全丢。
- 回答逐字匀速吐——那是打字机的手感；流式是 token 成簇到达，`chunk 2` 是下限。
- 思考标识做成三点跳——那是 IM 的"对方正在输入"；AI 的思考是单点呼吸。
- **把 ChatGPT 的皮灰阶化**（2026-08-25 用户定版否掉的做法）——灰阶化之后它退成"某个聊天框"，
  单行药丸/chips/问候语/圆→圆 morph/点睛色在语音端这五条产品取向全部读不出来，只剩一个通用打字机。照抄源码取值。
- 助手位用几何圆占位——ChatGPT 的助手消息前面是那朵结，换成裸圆就读不出是哪个产品了（回答本身无气泡，标识是唯一的产品线索）。
- 提示词超出单行——药丸 `nowrap` 会把它挤出去（或折行破坏药丸形态）；长提示词该换宽卡形态。
- 建议 chips 摆四枚以上——首屏变成菜单，观众开始读 chips；三枚是这个形态的容量。
- 一段演两问两答——观众切换到"读对话"模式；一问一答是自演的容量上限。

## 复用指引
- props：仅 `hostSrc`（角标）；prompt / reply / placeholder 在 `CONFIG`，问候语与三枚 chips 文案在 JSX 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/chat-gpt.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/chat-gpt/index.html。**换内容只改 `CONFIG.prompt` / `CONFIG.reply` / `CONFIG.placeholder`**——
  时刻表 `buildSchedule()` 按字数自动重算。节奏参数全在 `CONFIG`
  （`greetPar` / `pillPar` / 三段 `*Fade` 窗 / `cps` / `morphDur` / `chipsOutY` / `greetOut` / `thinkDur` / `streamRate` / `streamChunk`）；
  问候语改 `.greet` 的文案，三枚 chips 改 `.chips` 里的 `<span>`（图标是内联 SVG，换意图就换 path）；
  **配色不要改**——它是 ChatGPT 的皮，属于内容（要改就是在做另一个产品的卡）；
  真要换成**别的**产品皮时改两个 morph 图层的 `border-radius` 与底色 + 药丸圆角 + 助手位标识，**时刻表与所有时长一律不动**。
- Remotion 移植：template/cards/chat-gpt.tsx 即实现（`CONFIG` + `buildSchedule()` + 逐帧求值，`meta.durationInFrames` 由 `S.total` 算出）。
  视差是 `introY × greetPar(0.4)`（标题）与 `× pillPar(0.6)`（药丸 / chips）两处乘法——**照抄这两个乘数**；
  chips 退场是 `chipsO = cF.o × (1 − mFwd)` 与 `translateY += chipsOutY × mFwd`（`mFwd` 是不回退的 morph 正向进度）；
  morph 用 `out3(mRaw)` 交叉、发送圆按 `back.out(morphPop 1.7)` 涨出，发出后按 `revertDur` 回退。
  秒 ↔ 帧换算（30fps）：三段 fade 窗 [0.13,0.67]/[0.33,0.87]/[0.53,1.07]s、`typeStart` 1.40s = 42 帧、morph 0.40s ≈ 12 帧。
  流式用 `Math.ceil(linCnt / streamChunk) × streamChunk` 取子串（**不要用 `Math.random`**，多趟渲染会闪）。
- 剪辑软件对应物：剪映/CapCut——三段错峰就是三个图层各自的入场预设（"向上滑入 + 淡入"）**错开 0.2s 起始**，
  视差靠给标题层的位移量调小（比如药丸走 14px、标题只走 9px）；
  morph 是两个圆形按钮图层的交叉（Opacity 100→0 + Scale 100→90 / Opacity 0→100 + Scale 80→100 带弹性），
  关键帧**必须与打字第一帧对齐**；chips 整组打一个组，Opacity 与 Position 的关键帧起点也钉在打字第一帧；
  问候语的淡出关键帧钉在发送那一帧。AE——一个 Slider 当时钟，
  `fadeUpAt` 三段各写 `linear(s, a, b, 0, 1)`，视差就是同一个 `y` 表达式乘不同系数，
  回答的 Source Text 用 `text.sourceText.substring(0, Math.ceil(n/2)*2)`，
  思考标识 `0.35 + 0.65*(Math.sin(time*2*Math.PI*1.2)+1)/2` 的 Opacity 表达式。
  任何软件的"AI 聊天模板"要先检查三件事：三层有没有视差、morph 是否与打字同帧、chips 是不是跟着发送才退——市面模板三条基本全踩。

## 动效范围
- 属于本卡的：三段错峰淡入按阅读顺序排（标题 → 输入条 → 建议，间距 0.20s，各带 9px 上移且淡入窗独立于位移）；**位移视差**（同一个 spring 位移乘 0.4 / 0.6 两个不同系数）；输入框逐字符揭示与光标"跟文本尾 / 空态在占位前"两态位置、"打字中实心 / 停手 1Hz 闪"两态闪烁；**morph 与打字同帧起**这条纪律，圆 → **圆**的形态（只换图标与底色）与两图层交叉方向（退的缩、进的涨带回弹）；点睛色在 morph **起**端这个方向；chips 随 morph **正向**进度淡出下移（不回退）；问候语在**发送**那一帧起淡出并与用户消息弹入交叉；发送键 ±0.11s 时间窗按压；用户消息块与发送同帧占位并弹入；思考标识单点呼吸（1.2Hz，只改亮度）与流式一开始即撤；流式回答的分块揭示 + 尾巴块光标 + 吐完即撤；**回答无气泡**这条结构纪律；"一问一答 + 三枚 chips"这两个容量上限。
- 不属于本卡的：demo 那句「帮我查这条数据的原始出处」与那条回答的具体文案、「今天想聊点什么？」这句问候、三枚 chips 的具体标签与图标（生成图片/写作润色/联网查证）、14.5px 字号这组等比换算、角标主持人（数字人）。
  **注意与其他卡不同：ChatGPT 的皮（`#0D0D0D` / `#E3E3E3` / `#F4F4F4` / `#2F6FED` / `#9B9B9B` 这套取值、616×48 药丸 + 24px 圆角这组源码几何、OpenAI 结、`+` 与麦克风两个图标）属于"内容本身"而不是"可换的风格"**——见下面的底色要求。同一套时序当然可以套在别的"单行药丸 + 建议 chips"AI 产品首屏上，但那时皮要换成那个产品的皮（换了就不叫 chat-gpt 了）。
- 迁移接口：`CONFIG.prompt` / `CONFIG.reply` 是唯一的迁移入口——换成真实问过的那一问一答（提示词 10~14 字受单行约束、回答 28~36 字），时刻表自动重算；语速变化时改 `sendGap` 与 `thinkDur`（**`cps` / `morphDur` / `streamRate` / `streamChunk` / 两个视差乘数保持不变**——它们是手感常量）；换语言改 `cps`（中文 8.5 字/s、英文 18~22 字符/s）并重算单行容量；尺寸按画幅等比缩放，三段错峰的间距与视差乘数**不随尺寸变**；竖屏把药丸放到画幅宽度的 90%、chips 减到两枚并排（三枚会挤到折行，折行的 chips 排立刻读作乱）、`streamRate` 降到 18；换成**别的**产品皮时（那就是另一张卡了）只改两个 morph 图层的圆角/底色 + 药丸圆角 + 助手位标识，**时序一律不动**。
- 底色要求：**产品皮 = 内容本身，2026-08-25 用户定版：完全还原产品样式**。本卡涉及真实产品界面（ChatGPT 浅色皮），
  所以取值锁在源码 `THEMES.light`（页 `#FFFFFF` / 输入条 `#FFFFFF` + `#E3E3E3` 描边 / 主文 `#0D0D0D` /
  占位 `#9B9B9B` / chips `#E3E3E3` 描边 + `#5D5D5D` 字 / 发送 `#0D0D0D` 底白箭头 / accent `#2F6FED`），
  **不受"白舞台中性化"约束**——把它灰阶化会让它退成"某个聊天框"，五条产品取向全部读不出来。
  这个产品的浅色皮正好就是纯白，所以与白舞台天然一致（舞台底 = 产品底，不需要额外容器）。
  深色皮也在源码里（页 `#212121` / 输入条 `#303030` / 主文 `#ECECEC` / chips 描边 `#454545`），
  需要深色 ChatGPT 时整套换过去，**唯一要跟着翻的是发送圆**（浅皮墨底白箭头 → 深皮白底墨箭头，源码 `sendBg/sendArrow` 就是这么翻的）。
- 与相邻卡的分工：**vs [chat-message-flow](chat-message-flow.md)（通用聊天自演）**——那张演*人和人*（两侧气泡、三点跳、反应表情，一段 2~4 条往复），本卡演*人和 AI 产品*（首屏三件套、morph、无气泡回答、流式吐字，一问一答）。**vs [claude-code](claude-code.md)（同批姊妹卡）**——那张是终端里的编码智能体（深底窗、工具调用循环、diff）；讲"AI 帮我写代码"用那张。**vs [terminal-typing-log](terminal-typing-log.md)（通用终端）**——那张是 stdout 流水且载体是终端；本卡的流式虽同样分块突进，但结构是「一问一答」，载体是产品界面。
  **要演别的聊天型 AI 产品**（宽卡 composer 形态、morph 走圆 → 方角、accent 在发送端、无 chips、无首屏问候）时：
  本卡的时序骨架照搬即可，皮按那个产品的界面重画（morph 圆角 / 底色、药丸圆角、助手位标识）。
  本库目前只保留 ChatGPT 这一张聊天型产品卡（同批的 claude-chat 卡已于 2026-08-25 撤掉）。

<!-- ===== /file: video-talkcraft/references/cards/chat-gpt.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/chat-message-flow.md ===== -->

---
name: chat-message-flow
标题: 聊天记录自演
优先级: P0
代码: template/cards/chat-message-flow.tsx
一句话: 聊天记录自己演一遍——我方消息先在底部输入框逐字打出、停 0.33s 后弹上屏，对方先出"正在输入"三点气泡（时长按回复长度算）再弹消息，反应表情在消息落定 0.27s 后贴上；整张时刻表由文本长度自动生成
适用: 口播甩聊天记录当证据的时刻——"客户是这么说的""团队当时的讨论""我问了它，它这么回"；产品复盘、职场沟通、AI 对话演示、争议还原；不适合需要展示大量历史消息的场景（自演只演 2~4 条）
时长: 起手静置 0.4s → 我方打字 0.6~2.6s（按字数）+ 0.33s + 上屏 0.47s → 对方 1.1~2.3s 输入气泡 + 上屏 0.47s；消息间隔 0.6s；3 条一段共约 8.8s
能量: 中
类别: 素材呈现
输入: 界, 人(可选)
语义: 例证, 引用, 过程演示
素材形态: 界面
位置: 任意
props: hostSrc
---

## 意图
聊天截图是口播里出现频率最高的证据素材，但截图只能被"拍上台"（media-pop-in），它永远是**过去式**的。
本卡把同一份记录变成**现在进行时**：观众看着我方在输入框里把话打出来、看着对方那三个点跳了一秒半才回，
"这场对话正在发生"的临场感比"这是一张截图"强一个量级——而且**每条消息的出现时刻天然对齐你的讲述**，
你念到哪一句，那一句正好上屏。
命门：**两条链路各有自己的前戏**（我方经过输入框，对方经过输入气泡；缺了前戏就退化成"气泡依次淡入"）、
**时刻表由文本长度自动生成**（手数帧的表换一次文案就全废，也必然出现"两个字的消息打了两秒"的破绽）、
**灰阶中性皮**（一旦做成微信绿/iMessage 蓝，观众开始读平台品牌、并且你要为仿真背锅）。

## 动效核心
- **时刻表自动生成（本卡的骨架）**：`buildSchedule()` 一遍算完每条消息的所有时刻点，运行时只查表。
  我方 `typeDur = clamp(字数 × 0.12s, 0.6, 2.6)`；对方 `thinkDur = clamp(字数 × 0.115s, 1.1, 2.3)`。
  中文按**字符数**算，0.12s/字 ≈ 3~4 帧/字 @30fps（原版 2.2 帧/字对中文偏快，读作机器代打）
- **我方链路（输入框 → 上屏）**：输入框逐字揭示（`slice(0, floor(p × len))`，**逐字符不分块**——
  手在打字）→ 打完停 `sendGap 0.33s`（"手指抬起再按发送"的那一下）→ 发送与上屏**同帧**
- **发送键两段反馈**：有字即从灰底转墨底（激活）；发送那一瞬 `scale 1 → 0.84 → 1`，
  时间窗 ±0.23s（`sendWindow` 作半宽）内线性升降（`1 − 0.16 × pulse`）。按压是"我按下去了"的物理证据
- **输入框光标**：打字中**实心不闪**，打完（进入 `sendGap`）才开始 2Hz 闪 ——
  "停手了，正要发出去"。全程闪或全程不闪都会丢掉这半拍的语义
- **对方链路（输入气泡 → 上屏）**：三点气泡淡入 0.27s（`y 10 → 0`）→ 一直跳 → 消息上屏前 0.2s 淡出。
  两者时间窗不重叠，所以永远不会看见"三点和消息叠着"
- **三点跳动**：正弦上下跳，`w = (sin(2π(t × 1.1 − i/6)) + 1) / 2`，`y = −5px × w`、`opacity = 0.45 + 0.55w`。
  **相位差 = 周期/6**（= 周期/(点数 × 2)）——波从左往右推，三点齐跳读作"三个点在呼吸"不是"有人在打字"
- **气泡上屏弹入 0.47s**：`y 12 → 0`（`power3.out`）+ `scale 0.94 → 1` + 淡入（`power2.out`），
  `transform-origin` 在下沿（我方右下、对方左下）——从自己那一侧的下方浮起来
- **行占位比弹入早 0.07s**：消息行 `display` 硬切占位（把上面的消息整体顶上去）→ 气泡才落下来。
  先顶后落，反了就是"气泡落定后画面又抖一下"
- **反应表情 0.47s**：消息落定后再 `reactDelay 0.27s` 贴出，`scale 0 → 1` 带 `back.out(1.9)` 回弹
  （全卡唯一允许过冲的动作），前 35% 淡入。白环 2.5px 让它读作"叠在气泡上"而不是气泡自带的图标
- **布局纪律**：消息区 `justify-content: flex-end`（底部对齐），
  输入气泡**绝对定位**盖在消息气泡上（不进流）——换成消息时零重排；
  气泡靠 `opacity` 隐藏而不是 `display`（**在流内占位**，布局只跳 `presenceStart` 那一次）
- **层级**：面板底 → 消息流（气泡）→ 输入气泡（绝对定位覆盖层）→ 反应表情（带白环，最上）→ 输入框

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `charDur` | 0.12s/字 | 我方打字速度，中文 3~4 帧/字；<0.08s 读作机器代打（人手打不了那么快），>0.2s 观众等不动、开始读输入框而不是听你讲 |
| `typeMin` / `typeMax` | 0.6s / 2.6s | 打字时长的 clamp；短消息 <0.5s 一闪而过（没看见"在打"），长消息 >3s 整段节奏被一条消息吃掉 |
| `sendGap` | 0.33s | 打完到发送的停顿，这一拍就是"手指抬起再按下"；=0 则打完即发、读作自动脚本，>0.6s 观众以为它卡住 |
| `thinkPerChar` | 0.115s/字 | 对方"正在输入"时长 = 回复字数 × 它；长回复自动想得久（这是"时刻表自动生成"最值钱的一处），设成常数则每条回复都想一样久、一眼是假 |
| `thinkMin` / `thinkMax` | 1.1s / 2.3s | 输入气泡时长 clamp；<0.8s 三点还没跳完一个周期（读作闪了一下），>2.8s 观众开始等对方而不是听你 |
| `reveal` | 0.47s | 气泡上屏弹入；<0.25s 读作硬切出现，>0.7s 气泡"飘"上来、丢掉消息的爽脆感 |
| `msgGap` | 0.60s | 消息间隔；<0.35s 两条黏成一条，>1.0s 对话读作"两段独立的话" |
| `reactDelay` / `reactDur` | 0.27s / 0.47s | 反应表情比消息落定晚多少 / 弹出时长；delay=0 则读作气泡自带的图标（不是"有人点了个赞"），>0.6s 像迟到的补充 |
| `reactPop` | 1.9（`back.out`） | 反应回弹强度；这是全卡唯一允许过冲的动作，>3 显廉价、=0 就只是缩放出现 |
| `dotAmp` / `dotCps` | 5px / 1.1 周期/s | 三点跳幅与频率；幅度 >8px 三点在气泡里乱窜，频率 >1.6 读作焦虑抖动、<0.7 像在呼吸不像在打字 |
| 相位差 | 周期/6 | = 周期/(点数×2)，"波从左往右推"的唯一来源；=0（三点齐跳）立刻退化成呼吸灯 |
| `pushLead` | 0.07s | 行占位比气泡弹入早多少；=0 则顶上去和落下来同帧发生、读作"整屏抖一下" |
| 消息条数 | 2~4 | 一段自演的容量；>5 条观众开始读聊天记录、离开你的讲述（要展示长记录改用 evidence-scroll-tour） |

## 已知坑
- 所有气泡直接依次淡入（砍掉输入框与输入气泡两段前戏）——退化成"列表加载动画"，"对话正在发生"的全部价值消失。
- 手数帧写死时刻表——换一次文案全废，且必然出现"两个字的消息打了两秒"这种破绽；时刻表必须由字数算。
- 对方"正在输入"用固定时长——每条回复都想一样久，一眼是循环播放的贴图；时长必须跟回复长度挂钩。
- 我方消息不经过输入框直接弹出——观众读作"对方发的第二条"，分不清谁在说；我方消息的身份靠输入框建立。
- 输入框逐字**分块**揭示（4 字一簇）——那是机器 stdout 的手感（见 terminal-typing-log），人打字是一个一个的。
- 输入框光标全程闪或全程不闪——丢掉"打字中实心 / 停手才闪"这半拍；停手那一下的闪就是"正要发出去"。
- 三点齐跳（相位差 = 0）——读作"三个点在呼吸"，不是"有人在打字"；相位差必须是周期/6。
- 输入气泡和消息气泡时间窗重叠——某几帧能同时看见两个气泡，一眼是 bug；淡出必须在上屏前完成。
- 输入气泡**进流**（跟消息气泡抢布局）——换成消息那一帧整段重排跳一下；它必须绝对定位盖在上面。
- 气泡用 `display: none` 隐藏——出现时把上面的消息猛地顶一下，与弹入叠成"抖两下"；用 `opacity` 在流内占位，只在 `presenceStart` 跳一次。
- 反应表情与消息同帧出现——读作气泡自带的图标；晚 0.27s 才是"有人点了个赞"。
- 反应表情没有白环（直接贴在气泡上）——和气泡糊成一块，看不出是叠加的反应。
- 反应表情被容器裁掉半个——它探出气泡下沿 13px，消息区下留白必须 ≥ 这个量（本 demo 踩过）。
- 仿微信绿 / iMessage 蓝 / 带尖角小三角——观众开始读平台品牌（"这是微信截图吗？"），且你要为仿真背锅；灰阶中性气泡（墨底/浅灰底 + 单侧小圆角）已经足够表达"谁在说"。
- 一段塞 6 条以上消息——观众切换到"读聊天记录"模式，你的讲述变成背景音；长记录用 evidence-scroll-tour。
- 给气泡加渐变/投影/头像照片——聊天面板变成主角；线框灰阶 + 首字头像圆足够。

## 复用指引
- props：仅 `hostSrc`（角标）；消息在 `CONFIG.messages` 常量里，联系人名 / 头像首字在 JSX，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/chat-message-flow.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/chat-message-flow/index.html。**换内容只改 `CONFIG.messages`**——
  每条 `{ from: "me" | "them", text, react? }`，时刻表自动重算（这是本卡设计的全部意义，不要手动补时间）。
  节奏参数全在 `CONFIG`（`charDur` / `sendGap` / `reveal` / `msgGap` / `thinkPerChar` / `reactDelay` / `dotAmp` / `dotCps`）；
  联系人名与头像首字改 `.head` 里的文案和 `rows` 构建处的 `av.textContent`；
  英文文案把 `charDur` 减半到 0.06s 左右（英文按字符数算，一个词≈5 字符）。
  面板尺寸变了要保证消息区下留白 ≥ 反应表情探出量（13px）。
- Remotion 移植：tsx 已是这个结构——`buildSchedule()` 纯函数算出 `SCHED` / `TOTAL`，`meta.durationInFrames` 由 `TOTAL` 算出（**帧数由内容算出来**，不用手填）；搬进别的工程把秒 × `fps` 变帧号即可。
  气泡弹入用 `spring({frame: frame - revealAt, fps, config: {damping: 18, stiffness: 120}})` 驱动 `translateY/scale/opacity`，
  或直接三条 `interpolate` + `Easing.out(Easing.cubic)`；
  三点用 `const w = (Math.sin(Math.PI*2*((frame/fps)*1.1 - i/6)) + 1)/2`（**不要用 `Math.random`**，多趟渲染会闪）；
  反应表情 `spring({config: {damping: 11, stiffness: 220, mass: 0.6}})`；
  输入框文本 `text.slice(0, Math.floor(progress * text.length))`；
  行占位在帧驱动下用条件渲染 `frame >= presenceStart && <Row/>`，气泡本身靠 opacity 占位。
- 剪辑软件对应物：剪映/CapCut——每条消息一个气泡贴图/文本框，入场用"向上弹入 + 缩放"组合（把时长压到 0.4~0.5s），
  输入框那段用一个文本层套"打字机"入场（速度调到 3~4 帧/字），三点用一个三点 PNG 配"上下浮动"循环预设（**必须能设相位/延迟**，否则三点齐跳）或干脆做三个点各自延迟 0.05s 的浮动；
  发送键按压用两个 Scale 关键帧（1 → 0.84 → 1，共 0.46s）；反应表情用"弹性放大"入场且**贴在消息入场后 0.27s**。
  AE——整段用一个 Slider 当时钟，气泡 Position/Scale/Opacity 三条曲线配 Easy Ease，三点用 `-5*(Math.sin(time*2*Math.PI*1.1 - index/6*2*Math.PI)+1)/2` 的 Position 表达式（`index` 用图层序号），
  输入框文字用 `text.sourceText.substring(0, Math.floor(t))` 配 Slider；反应表情用 Scale 关键帧 + Overshoot 表达式。
  任何软件的"聊天动画模板"要先检查两件事：有没有输入框前戏、三点是不是齐跳——市面模板九成两条都不合格。

## 动效范围
- 属于本卡的：时刻表由文本长度自动生成这套机制（我方 `clamp(字数 × charDur)`、对方 `clamp(字数 × thinkPerChar)`，换文案不重数帧）；我方链路的三拍（输入框逐字符揭示 → `sendGap` 停顿 → 发送与上屏同帧）；发送键的两段反馈（有字转激活 + 发送瞬间 `scale −16%` 的 ±0.23s 时间窗按压）；输入框光标"打字中实心不闪 / 停手才 2Hz 闪"这半拍语义；对方链路的两拍（三点气泡淡入 0.27s + 跳动 + 上屏前 0.2s 淡出，时间窗不重叠）；三点正弦跳动与"相位差 = 周期/(点数×2)"这条纪律；气泡上屏弹入（`y 12→0` + `scale .94→1` + 淡入 0.47s，`transform-origin` 在自己那一侧下沿）；行占位比弹入早 0.07s 的先顶后落顺序；反应表情晚 0.27s 贴出 + `back.out(1.9)` 回弹 + 白环；布局纪律（消息区底部对齐、输入气泡绝对定位不进流、气泡靠 opacity 在流内占位）；"一段 2~4 条"这个容量上限。
- 不属于本卡的：demo 那三条讨论筛选器的具体文案、"林工 · 设计评审"这个联系人与首字头像、`👍` 这个具体表情、灰阶皮的全部取值（`#1d1d1f` 墨底气泡 / `#f0f0f2` 浅灰气泡 / `#fafafa` 输入框底 / 16px 圆角 + 单侧 6px 小圆角）、460×448 这个面板尺寸与 16px 字号、`+` 与箭头两个图标、"在线"状态行、角标主持人（数字人）、"聊天面板"这个载体（同一套时序可以套在评论区、客服工单、AI 对话流上）。
- 迁移接口：`CONFIG.messages` 是唯一的迁移入口——把消息换成真实记录的节选（保留"我问 → 对方想 → 对方答"的往复结构，2~4 条），反应表情只给最关键的那一条；语速变化时改 `msgGap` 与 `sendGap`（**`charDur` / `thinkPerChar` / `reveal` / `dotCps` 保持不变**——这四个是手感常量，跟着语速缩放会让快语速下的打字变成机器代打）；换语言改 `charDur`（中文 0.12s/字、英文约 0.06s/字符）；尺寸按画幅等比缩放，消息区下留白必须 ≥ 反应表情探出量；竖屏面板可占满画幅宽度、消息区更高（能多显示一条历史消息，但自演条数仍不超过 4）；换成目标产品皮时只改两个气泡底色与文字色 + 圆角，**时刻表与所有时长一律不动**。
- 底色要求：白底即可（中性聊天面板天生浅色，墨底气泡与浅灰气泡在白底上对比充足）。深色皮同样成立，唯一硬要求是**我方与对方两个气泡的明度差要保住**（深底上把我方改为亮底深字、对方改为略亮于面板的深灰），反应表情的白环随之改为面板底色的同色环——它的作用是"和气泡隔开"，不是"白"。

<!-- ===== /file: video-talkcraft/references/cards/chat-message-flow.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/chevron-lower-third.md ===== -->

---
name: chevron-lower-third
标题: 动态人名条
一句话: 姓名行从左推出（x -26→0，0.26s），职称 chip 错峰 0.1s 从左 scaleX 展开 0.22s、chip 内字滞后 2 帧淡入，三枚 chevron 再依次扫过点亮当"条子还在延伸"的收尾；hold 2.0s 后整条从左收回
适用: 真人出镜嘉宾首次开口的 3~5 秒；也用于连线、自我介绍、引用他人观点时标注身份；比 lower-third-nameplate 多一档"节目感/动态感"（vlog、播客、体育/科技节目）；正式访谈与纪录片建议用那张更克制的
时长: 起手静置 0.4s → 姓名推出 0.26s → chip 展开 0.22s（错峰 0.1s，内字滞后 0.067s）→ chevron ×3 错峰 0.07s → hold 2.0s → 整条收回 0.2s；共约 3.2s
能量: 低
类别: 人物互动
输入: 人(可选), 文
语义: 自我介绍, 引用, 介绍他人
素材形态: 无
位置: 任意
props: hostSrc
优先级: P1
代码: template/cards/chevron-lower-third.tsx
---

## 意图
观众需要在人物开口的头两秒知道"这是谁、凭什么听他说"——人名条是成本最低的信任背书。
这个需求本库已有 `lower-third-nameplate` 在解决，所以本卡的存在必须靠**区别**站住：

**`lower-third-nameplate` = 色条 → 姓名 → 头衔的三段接力**（一根横色条先展开，
文字被 clip 从左揭示；克制、新闻感、"横向语言"统一）。
**本卡 = chip 展开 + chevron 收尾**：职称不是一行灰字，而是坐在**实心 chip** 上
（身份被"发牌"出来，像一枚标签）；收尾多了三枚 chevron 依次点亮，
读作"这条子还在往右延伸"——一个**没有停下来的**收尾。
所以本卡比那张多一档动态感：那张是"贴上去一块名牌"，本卡是"发出一枚标签、并且还在走"。
选卡标准很直接：正式访谈/纪录片用那张，节目感/网感的片子用这张。

命门三条：
① **chip 内的字滞后 chip 2 帧（0.067s）**。字跟着 chip 一起被刷出来读作一整块 PNG；
chip 先成形、字后落，才有"发牌"的两拍。
② **chevron 是收尾不是装饰**。它必须在 chip 落定**之后**依次点亮，且错峰要密
（0.07s）——三枚读作**一道扫过**，不是三个小箭头各自出现。
③ **hold 要给 2.0s**。人名条的本职是让人读完姓名 + 头衔，读不完等于没打；
其他动效 1.5s 够，这张不够。

## 动效核心
- **结构**（@960×540 舞台）：左下安全区内（左 72 / 下 96），第一行 44px/700 墨字姓名；
  第二行是 flex 行：实心 chip（高 40，`border-radius: 12` 小件圆角档，
  内 21px/600 白字）+ 12px 间隙 + 三枚 15×26 的 chevron（4.5px 描边 `round` 端头）。
  整条包在一个 `transform-origin: left center` 的 `.clt` 里（退场时整条一起收回）
- **① 姓名推出**：`x -26→0` + `opacity 0→1`，`0.26s power3.out`
- **② chip 展开**：chip 背景是独立层 `.clt-chip-bg`（`transform-origin: left center`，
  `scaleX 0→1`，`0.22s power3.out`），起步 = 姓名起步 + `0.1s`（错峰，不等姓名走完）；
  chip 内字 `opacity 0→1`（`0.14s`），滞后 chip `0.067s`（≈2 帧 @30fps）。
  **字不参与 scaleX**（否则被横向拉扁），chip 容器加 `overflow: hidden` 兜底
- **③ chevron 扫过**：`opacity 0→1` + `x +5→0`，各 `0.14s power2.out`，错峰 `0.07s`；
  起步 = chip 落定。错峰密到读作一道扫过而不是三个元素
- **④ hold 2.0s**：全部静置（元素小，不需要防呆滞漂移）
- **⑤ 退场**：整条 `.clt` 一起 `scaleX 1→0` + `opacity 1→0`，`0.2s power2.in`
  （比入场的 0.26s 快——出场永远比入场轻，design-language §4）
- **层级**：人物画面 → 人名条（最上，且必须高于字幕安全区）

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `namePush` | -26px | 姓名推出位移；0 = 纯淡入（少了"推上来"的方向），<-60px 读作从画外飞入，抢了 chip 的戏 |
| `nameDur` | 0.26s | 姓名推出时长；<0.15s 读作硬现，>0.45s 后面两段等不起（整条入场超过 1s 就拖） |
| `chipGap` | 0.1s | chip 相对姓名起步的错峰；0 = 两行一起进（层次塌），>0.3s 读作两个独立动效（"名字来了…哦还有个标签"） |
| `chipDur` | 0.22s | chip 展开；<0.12s 读作色块硬现，>0.4s 观众看着 chip 慢慢长，节奏散 |
| `chipTxtLag` | 0.067s（2 帧 @30fps） | **本卡第一命门**；0 = 字跟着 chip 一起被刷出来（整块 PNG 感），>0.2s 读作 chip 空着等字 |
| `chevStagger` | 0.07s | **本卡第二命门**；<0.04s 三枚几乎同时（读作一个整体图形），>0.15s 读作三个小箭头各自出现（装饰化） |
| `chevDur` | 0.14s | 单枚 chevron 点亮；比 chip 快（它是轻件），拉长会让收尾比主体还重 |
| `chevSlide` | 5px | chevron 点亮时的 x 位移；0 = 纯淡入（可用，"延伸感"弱一点），>12px 读作三个小箭头在飞 |
| chevron 枚数 | 3 | 2 枚"延伸感"不够（读作两个点），≥4 枚在小尺寸下糊成一片；3 是"还在走"的最小可读数量 |
| `hold` | 2.0s | **本卡第三命门**；<1.5s 观众读不完姓名 + 头衔（等于没打），>8s 变成常驻台标（那是另一件事） |
| `outDur` | 0.2s | 退场时长；**必须短于 `nameDur`**（出场比入场轻）；>0.4s 读作"舍不得走" |
| 头衔字数 | ≤12 字一行 | 超过一行读不完；多余身份直接删（"供应链咨询顾问 · 12 年"已是上限） |
| 落位 | 左 72 / 下 96 | 必须在 action-safe 内且**高于字幕安全区**；下缘小于 64px 会和字幕打架 |

## 已知坑
- chip 内的字跟着 chip 一起 `scaleX`——字被横向拉扁，慢放下非常明显；字必须是 chip 背景层之上的独立层。
- chip 内字不滞后（与 chip 同时淡入）——整条读作一张预先做好的 PNG 贴上来，"发牌"的两拍消失。
- chevron 在 chip 落定前就点亮——收尾语义变成"和主体一起进场的装饰"，"条子还在延伸"这层意思全丢。
- chevron 错峰拉到 0.15s 以上——三枚变成三个独立小箭头依次出现，读作装饰而不是一道扫过。
- chevron 加到四枚以上——在实际投放尺寸（手机竖屏）上糊成一片色，还挤占了头衔的横向空间。
- 退场直接整体淡出——像素材播完了自然消失；反向收回才是"完整的一次亮相"（这条与 `lower-third-nameplate` 共享）。
- 退场做得比入场慢——违反 design-language §4（出场永远比入场轻），读作"舍不得走"。
- hold 只给 1.2~1.5s（照抄别的卡）——人名条的本职是让人读完，读不完等于没打；这张卡必须给 2.0s。
- chip 用 `width` 动画而不是 `scaleX`——width 变化触发回流，chip 内的字会跟着换行/跳动。
- 姓名和 chip 用两个不同的强调色——同屏第二个"看这里"色（design-language §1 红线）；chip 与 chevron 共用唯一强调色，姓名走墨色。
- 压在画面正下方字幕区——和字幕打架；人名条的家在左下但必须高于字幕安全区。
- 头衔写两行——读不完，而且 chip 变成一个方块（chip 的语义是"一枚标签"，标签是扁的）。
- 忘了给 `.clt` 设 `transform-origin: left center`——退场时整条从中心收，读作"被吸走"而不是"收回左边"。

## 复用指引
- props：仅 `hostSrc`；姓名 / 头衔文案在 JSX 常量里（`.clt-name` / `.clt-chip span`），换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/chevron-lower-third.tsx——自包含单文件，复制进工程即可用；节奏参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/chevron-lower-third/index.html。换文案改 `.clt-name` 与
  `.clt-chip span`（头衔 ≤12 字），chip 宽度自动跟着文字走（`padding: 0 18px`）；
  改强调色只动 `:root --acc`（chip + chevron 共用，姓名保持墨色）；
  节奏全在 `CONFIG`（`namePush`/`nameDur`/`chipGap`/`chipDur`/`chipTxtLag`/
  `chevStagger`/`hold`/`outDur`）；落位改 `.clt` 的 `left`/`bottom`。
  实拍落地时给姓名与 chip 补一层投影或半透明底板——那是**迁移方自加的可读性层**，不属于本卡。
- Remotion 移植：整条包一个 `<div style={{transformOrigin: "left center", transform: `scaleX(${out})`}}>`；
  姓名 `x = interpolate(f, [0, 8], [-26, 0], {easing: Easing.out(Easing.cubic), extrapolateRight: "clamp"})`；
  chip 背景 `scaleX` 用 `f - 3` 局部时钟、chip 内字用 `f - 3 - 2`；
  chevron 三枚用 `f - 10 - i*2`；退场用 `interpolate(f, [outFrame, outFrame+6], [1, 0])`。
  帧换算 @30fps：`nameDur 0.26s ⇒ 8f`、`chipGap 0.1s ⇒ 3f`、`chipTxtLag 0.067s ⇒ 2f`、
  `chipDur 0.22s ⇒ 7f`、`chevStagger 0.07s ⇒ 2f`、`hold 2.0s ⇒ 60f`、`outDur 0.2s ⇒ 6f`。
- 剪辑软件对应物：剪映/CapCut——"文字模板 → 字幕条/人名条"分类里有大量带 chip 的款，
  但**内置款的 chip 与字基本是一起进场的**（丢掉本卡第一命门）；要做对就自己搭：
  文字层 + 色块层，色块用"向右展开"入场、文字用"渐显"并把入场时间往后拖 2 帧；
  chevron 用三个 `>` 文字层或箭头贴纸，入场时间各差 2 帧。
  AE——Shape Layer 做 chip（Scale X 0→100%，锚点移到左边缘）+ 文字层单独 Opacity 关键帧
  晚 2 帧；三枚 chevron 各自 Position + Opacity，用 `Sequence Layers`（Overlap 关掉）
  自动排 2 帧错峰；整条用一个 Null 父级做退场 Scale X。FCPX 内置 Lower Thirds 生成器
  改不出 chip 滞后，建议自搭。
- 与本库同类卡的分工：**`lower-third-nameplate` = 色条 → 姓名 → 头衔三段接力**
  （克制、新闻/纪录片感、横向语言统一、头衔是灰字）；
  **本卡 = 姓名推出 → chip 展开 → chevron 收尾**（节目感/网感、头衔是一枚实心标签、
  收尾"还在延伸"）。两张不要在同一片子里混用——人名条是全片一致的模板件，
  换款会让观众以为换了节目。`host-shrink-to-chip` = 人物本身缩成角标（构图变化，不是标注）；
  `subscribe-cta` = 行动号召（常驻件）。

## 动效范围
- 属于本卡的：姓名 `x -26→0 + opacity`（0.26s `power3.out`）推出；chip 背景 `scaleX 0→1`（origin left，0.22s）错峰 `0.1s` 跟上、**chip 内字滞后 2 帧（0.067s）淡入且不参与 scaleX**（本卡第一命门）；三枚 chevron 在 chip 落定**之后** `opacity 0→1 + x+5→0`、错峰 `0.07s` 密到读作一道扫过（收尾语义："条子还在延伸"）；hold **2.0s**（人名条专属的长 hold）；退场整条 `scaleX→0 + opacity`（0.2s `power2.in`，**必须快于入场**）且 `transform-origin: left center`；"chip（实心标签）+ chevron（延伸）"这个与三段接力式人名条相区别的组合关系。
- 不属于本卡的：demo 那个「陈知远 / 供应链咨询顾问 · 12 年」的具体人名头衔、44px 与 21px 的字号、蓝色 `#0066cc` 这个具体取值、chip 高 40 与圆角 12 的绝对数值、chevron 的具体形状（`>` 折线可换三角/箭头）、左 72 / 下 96 的具体安全区数值（按画幅重算）、人物画面（demo 用数字人占位）、实拍落地时补的投影或半透明底板（那是可读性层，迁移方自加）。
- 迁移接口：强调色 `#0066cc` 在 tsx 里写在 `.clt-chip-bg` 的 background 与 `.clt-chev path` 的 stroke 两处（chip + chevron 共用，姓名走墨色，同屏不允许第二个），换色两处同改（HTML demo 是 `:root --acc` 一个变量）；字号与 chip 高度按画幅等比（44px/40px @540 舞台高 ⇒ ×2 @1080）；落位按目标画幅的 action-safe 重算，且必须**高于字幕安全区**（横屏字幕 bottom 100px ⇒ 人名条 bottom ≥ 170px；竖屏字幕 bottom 350px ⇒ 人名条要么更高要么改到上方）；节奏在 `CONFIG`，`chipTxtLag`（2 帧）与 `chevStagger`（0.07s）是**手感常量**，换尺寸换语速都不要动；`hold` 按"姓名 + 头衔读两遍"给（实拍建议 3~5s，demo 压到 2.0s）；`outDur` 必须短于 `nameDur`。
- 底色要求：白底即可。实拍落地时底色是任意视频画面，因此**对比度要自证**——chip 与姓名必须在目标背景上读得出（浅色背景上墨字姓名成立；深色/花色背景上要给姓名补描边或垫半透明底板）。这是迁移方的责任，不是本卡的动效内容。

<!-- ===== /file: video-talkcraft/references/cards/chevron-lower-third.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/chip-grid-single-select.md ===== -->

---
name: chip-grid-single-select
标题: 五选一反黑
一句话: N 个候选 chip 3+2 居中铺开让观众读题（前 2s）；选中帧先插 1 帧灰色按压，紧接 5 帧 linear 反黑（底→墨、字→白）+ 1→1.04→1 极轻正弦回弹，其余 chip 降到 18% 但位置锁死；停 1.5s 看清选中态后余项归零、黑 chip 上移 46px 收窄 0.82 并横向补偿回中线，下方算式行浮现逐词加深——"选了它，然后……"
适用: 口播里"N 个方案 / 套餐 / 工具我选哪个 → 选了它之后会怎样"的决策 + 因果镜头；投票 / 调研结果揭晓；排除法收到最后一个。输入是纯文字，人物不参与
时长: 6.8s（0.1 问题 → 0.5 候选逐个淡入 → 2.0 选中：1 帧灰闪 + 5 帧反黑 + 回弹、余项降 18% → 3.5 余项归零、黑 chip 上移回中线 → 3.75 算式行逐词加深 → 6.4 整体退场 0.4s）；成片把选中帧对到口播说出选项的那个字
能量: 中
类别: 数据信息图
输入: 文
语义: 对比, 数据, 选择
素材形态: 无
位置: 中段
props: question, options, selected, equation
优先级: P1
代码: template/cards/chip-grid-single-select.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 人物不参与（人在场时整组放人物对侧半幅，chip 行宽 ≤ 半幅） | ✗ | ✗ 卡自带 chip 与算式；不吃素材 |

只吃文字：一行问题 + 2～6 个候选 + 选中项 + 一行算式（哪几个词强调）。

## 常用场景
1. "五个方案我选哪个 → 选了它每月省 72 小时"（demo 演的）
2. 套餐 / 档位 / 工具选型："三个版本我买了 Pro，因为……"
3. 投票 / 调研结果揭晓：选中 = 多数人的选择
4. 排除法：讲到哪个排除哪个，最后剩下的反黑

## 意图
口播讲"几个选项里我选了这个"，`parallel-items-with-host` 灰转彩是**逐个点亮全部**（并列，没有取舍），`focus-dim-spotlight` 是讲到哪亮哪、其余压暗但**不做选择**（焦点还会移走）。五选一反黑是**单选 + 因果**：一帧按下、变黑、其余退到 18% 仍在原位——"没被选中"而不是"消失了"；停够 1.5s 后被选中的那个上移收窄居中，算式行接上"选了它之后……"。做对五条：
1. **灰闪只能 1 帧**：给 2 帧以上就读作 hover 高亮，不是按下。
2. **反黑 linear 不加 ease**："变黑"这件事不该有过程感，太软。
3. **余项位置锁死**（transform 恒为 none）：降到 18% 仍在原位才读作"没被选中"；一动就成了"被拖走 / 消失"。
4. **选中后 ≥1.5s 再收束**：观众要看清选中态；0.5s 就赶。
5. **收束时横向补偿回中线**：黑 chip 上移收窄若不补 cx，会偏在原列位置，读作"被拖走"。

## 动效核心
- **几何**（960×540）：问题行 30px/700 居中 @ top 116；chip 容器 top 200，两行 y=0 / 66；chip 高 48、圆角 24、padding 0 22、1.5px 描边 #d6d6dc、20px/600 墨字；每行最多 3 枚，量宽后以 480 为中心排布、间距 14；算式行 30px/600 居中 @ top 300，强调词 700 强调色。
- **读题**：问题 0.1s 起 0.4s `power3.out`（opacity + y 8→0）；chip 0.5s 起每 0.1s 一枚淡入 0.25s。
- **选中 FS = 2.0s**：灰闪层 `rgba(120,120,120,.5)` 在 [FS, FS+0.033) 可见（1 帧）；FS+0.033 起 0.17s linear 反黑（bg #fff→#1d1d1f、字 #1d1d1f→#fff、描边→#1d1d1f）；同起 0.34s 正弦回弹 `scale = 1 + sin(p·π)·0.04`；余项同起 0.34s `power2.out` opacity→0.18，transform 不动。
- **收束 LIFT = FS+1.5**：余项 0.3s opacity→0；黑 chip 0.4s `power2.inOut` `translate(cx, −46) scale(0.82)`，`cx = 480 − (chip 中心 x)`；算式行 LIFT+0.25 起 0.3s 浮现，LIFT+0.3 起逐词 0.16s 间隔从 0.25 加深到 1。
- **退场**：6.4s 问题 + 黑 chip + 算式 opacity→0 0.4s `power2.in`，6.8s 结束。落定即静置。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `FS` 选中时刻 | 2.0s | 前半读题后半看结果；<1.2 观众还没读完选项 |
| `flash` 灰闪 | 0.033s（1 帧） | **命门**：2 帧以上读作 hover 高亮 |
| `black` 反黑 | 0.17s linear | linear 是故意的；加 ease 太软 |
| `bounceAmp` 回弹 | 0.04 | 极轻；0.1 就成弹跳按钮抢戏 |
| `dim` 余项透明度 | 0.18 | 位置锁死；降到 0 就成"消失"，>0.35 读不出选择 |
| `lift` 收束延迟 | 1.5s | 看清选中态的最短驻留 |
| `liftY / liftScale` | −46px / 0.82 | 上移让出算式行位置；不补 cx 读作被拖走 |
| `eqStagger` | 0.16s/词 | 逐词加深是"结论慢慢成立"；同帧全亮读作贴字 |
| 候选数 | 2～6（每行 ≤3） | >6 两行放不下且读不完；2 个用 split-compare 更合适 |

## 已知坑
- 灰闪 2 帧以上——hover 不是按下。
- 反黑加了 ease——变黑有了"过程感"，软掉。
- 余项降权时挪位或缩小——读作消失 / 被拖走；必须 transform:none。
- 收束太早（<1s）——观众没看清选了谁。
- 上移不补 cx——黑 chip 偏在原列位置。
- 算式行同帧全亮——结论没有"成立"的过程。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/chip-grid-single-select.tsx——`question / options / selected / equation=[{text, accent}]`；durationInFrames 216；选中时刻改 `CONFIG.FS`，句长改 `exitAt / end`。chip 宽度 useLayoutEffect 量一次（delayRender），排布与 cx 由此推出。
- HTML/GSAP：demos/chip-grid-single-select/index.html——`.chip` 文案与 `.sel` 类、`.eq span` 文案与 `.acc` 类、`CONFIG`。
- 母本：video-shotcraft `chip-grid-single-select-blackout`（产品定价交互版；本卡换口播决策文案，机制原样）。
- 剪辑软件对应物：剪映每枚 chip 一张贴纸，选中帧上加 1 帧灰色蒙版 + 颜色关键帧 5 帧；余项透明度关键帧到 18%；AE 用 Fill 效果颜色关键帧（linear）+ Opacity。
- 与 layout.md 的接口：chip 行以 480 为中心量宽排布（§4 包围盒居中）；chip 20px = 条目档下限 40@1080p（§5）；问题 / chip / 算式三组纵向间距 84 / 100 ≥ 组内 14（§2）。

## 动效范围
- 属于本卡的：1 帧灰闪 → 5 帧 linear 反黑 → 正弦回弹的选中三段；余项 18% 位置锁死；1.5s 驻留后上移收窄 + cx 回中线；算式行逐词加深；整体同收。
- 不属于本卡的：具体文案、白底舞台、chip 的具体尺寸。
- 迁移接口：`question / options / selected / equation`；`FS` 按口播词锚；1080p 输出 chip 96 高、字 40 / 60、liftY −92。
- 底色要求：白底即可（反黑靠墨色对比）；深底时选中态改"反白"（底→白、字→墨），机制不变。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- 每行 chip 包围盒中心 x 偏差 ≤48；两行都居中。
- `shot-at FS+0.02` 冻在灰闪帧：只有选中 chip 有灰层、其余不变；`shot-at FS+0.5`：选中全黑白字、余项 18% 且位置与选中前一帧完全相同。
- `shot-at LIFT+0.5`：黑 chip 中心 x = 480 ± 8、余项 opacity 0、算式行已浮现。
- 无元素进字幕带 y ≥ 450（算式行底 ≈ 340）。
- 收尾帧只剩问题 + 黑 chip + 算式三组，全部静止。

<!-- ===== /file: video-talkcraft/references/cards/chip-grid-single-select.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/claude-code.md ===== -->

---
name: claude-code
标题: 编码智能体终端
优先级: P1
代码: template/cards/claude-code.tsx
一句话: 深底终端窗弹入后三段错峰按阅读顺序铺开（欢迎框 → What's new 栏 → 提示行），命令逐字符敲进提示行、回车后整行退成灰，接着「工具调用 → 结果 → diff → 结论」的因果链逐行分块蹦出，工具调用行的状态点在出结果前一直呼吸，diff 的 `+` 行是全窗唯一语义色
适用: 口播讲 AI 编程——「我让它改了一行，它是这么改的」；AI 编码工具测评/对比、Agent 工作流讲解、开发者向教程与踩坑复盘；不适合非技术受众的软性内容（终端本身会筛掉观众）
时长: 窗体弹入 0.62s → 三段错峰 0.20→1.20s → 1.60s 起打 → 命令 2.18s（24 字 @11 字/s）+ 0.36s 回车 → 七行工作日志 4.9s（不等距，4.14→9.04s）→ 尾巴留白 0.9s；整卡约 9.9s
能量: 中
类别: 素材呈现
输入: 界, 人(可选)
语义: 过程演示, 例证
素材形态: 界面
位置: 中段
props: hostSrc
---

## 意图
`terminal-typing-log` 已经解决了「通用终端当证据」——命令 → 日志 → 结论的 stdout 流水。
但 coding agent 的终端**不是流水**：它是**因果链**。每一步都得看清「它调了什么工具、参数是什么、
返回了什么、于是改了哪一行」——这条链是 AI 编程内容的全部信息量所在。
观众要判断的不是「它跑没跑」（那是构建日志的事），而是「它到底干了什么、干得对不对」。
所以本卡的结构与那张根本不同：**工具调用行带状态点且在出结果前一直呼吸**（"它在干活"这一拍）、
**结果行带折角缩进**（视觉上挂在调用行下面，因果关系靠缩进表达）、**diff 两行几乎连着出**
（同一次编辑的两半，中间不该有间隙）、**`+` 行是唯一语义色**（"文件真的被改了"这一拍的重量全在这抹绿上）。
再加上源码那套首屏——欢迎框 + What's new + 提示行**按阅读顺序三段错峰**，"这是一个刚启动的智能体"就立住了。
**产品皮 = 内容本身（2026-08-25 用户定版）**：本卡涉及真实产品界面，所以**完全还原 Claude Code 的样式**，
不做中性化——陶土橙 `#D97757`（虚线框 + 骑边标题 + What's new 小标 + 吉祥物）、深底 `#1B1A18` / 窗饰条 `#3A3633`、
主文 `#E8E5DD` / 次文 `#8A857C` / 更暗 `#6B6660`、macOS 三灯真色、源码那枚像素兽，全部照抄源码 `THEMES.dark` + `accentColor`。
理由：这张卡要当"我真的让它干过这个"的证据，观众得一眼认出是哪个工具——灰阶化之后它是"某个终端"，
证据的指向性就没了。可编辑的是**内容**（命令/日志/身份栏文案），外观不动。

命门：**三段错峰顺序 = 阅读顺序**（乱序或同时淡入就丢掉"界面在铺开"）、**行间延迟不等距**
（工具调用前等得久=它在想调什么，diff 两行几乎连着=同一次编辑；全表等距一眼是假数据）、
**语义色只给 `+` 行**（del 行用灰不用红——两色对上就变成彩虹 diff，"改了什么"反而看不清）。

## 动效核心
- **窗体弹入 0.62s**：`y 21 → 0` + `scale .97 → 1`（源码 `spring(damping 14 / stiffness 110 / mass 0.7)`，
  略欠阻尼 → 等价 `back.out(1.05)` 的微过冲）。深底窗 `#1B1A18` + macOS 三灯真色（源码 `#FF5F57 / #FEBC2E / #28C840`）
- **三段错峰淡入（本卡的入场骨架）**：欢迎框 `[0.20, 0.73]` → What's new 栏 `[0.40, 1.00]` →
  提示行 `[0.60, 1.20]`（源码 `fadeUpAt[6,22] / [12,30] / [18,36]`），各带 9px 上移。
  **顺序 = 阅读顺序**：先看框、再看右栏、最后落到提示行——落点正是接下来要打字的地方
- **欢迎框的骑边标题**：虚线框 + 标题片**骑在上边框上**，标题片用窗体底色盖掉那一段虚线——
  所以标题看着是"嵌"在边框里的（源码这处细节，成本极低但少了它框子就很业余）
- **1.60s 起打**（源码 `TYPING_START_FRAME 48`，比两张聊天卡晚 6 帧——首屏内容更多，多留一拍）
- **命令逐字符揭示**：`chunk 1` @11 字/s（中英混排；源码 `TYPING_CPS 18` 是纯 ASCII 速率）。
  **人在敲键盘不会 3 个字一起蹦**——这与下面日志的分块正好是一组对比（见下条）
- **方块光标三态**：打字中**实心不闪**、未开打 / 打完待回车 **2Hz 闪**（终端行业默认，比聊天卡的 1Hz 快一档）、
  **提交后即撤**（交给日志行的光标）
- **提交后整行退成灰**：`> 命令` 从亮字变灰字——"这句已经交出去了"，与下面正在生成的日志分出层次。
  少了这一步，命令行和日志行同亮，观众读不出哪个是输入哪个是输出
- **工作日志分块突进**：`revealed = min(len, ceil(linear / 3) × 3)` @54 char/s——**3 字一簇蹦出**（机器在吐）。
  与上面命令行的 `chunk 1` @11 字/s 差一个量级，这就是"人打的"和"机器吐的"的区别
- **行间延迟不等距**：工具调用前 0.42 / 0.28s（它在想调什么），结果行前 0.50 / 0.32s（等返回），
  **diff 两行只隔 0.14s**（同一次编辑的两半，几乎连着出），结论前 0.44s 再顿一下。
  全表等距一眼是假数据
- **工具调用行的状态点**：出结果之前以 1.1Hz **呼吸**（`opacity 0.35 → 1`，正弦），出结果即**定亮**。
  "它在干活" vs "这一步完事了"——**只改亮度，不做位移不做抖动**
- **行光标**：只在该行未打完时存在（打完即撤），2Hz 方波闪。所以行间停顿段画面**真静止**，不是"有个东西在闪"
- **四级颜色分级**：工具调用行亮（`#E8E5DD`）/ 结果行暗（`#8A857C`）/ diff `-` 行灰（`#6B6660`）/
  diff `+` 行绿（`#33d16b`，**diff 里唯一的语义色**，与 `terminal-typing-log` 同一支绿）。结论行的 `✓` 也用这抹绿。
  陶土橙不参与这套分级——它是**产品的身份色**（框/标题/小标/吉祥物/状态点），跟"改了什么"这条信息无关，两者不冲突
- **行占位纪律**：未到时刻的行 `visibility: hidden` 而不是 `display: none`——占位但不显示，整段布局零重排
- **层级**：白底舞台 → 深底终端窗（唯一深色区域）→ 欢迎框（虚线 + 骑边标题）→ 提示行 → 工作日志

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 三段错峰间距 | 0.20s | 欢迎框 → 右栏 → 提示行的起点间距；<0.1s 三段糊成一段（错峰白做），>0.4s 首屏铺得太慢、打字迟迟不开始 |
| 错峰顺序 | **阅读顺序** | 框 → 右栏 → 提示行。乱序（比如提示行先出）就丢掉"界面在铺开"的因果，读作三块各自独立淡入 |
| `typeStart` | 1.60s | 起打前静置（源码第 48 帧）；必须 ≥ 提示行淡入结束（1.20s），否则行还没显形就在打字 |
| `cps` | 11 字/s（中英混排） | 命令打字速率；<8 观众开始读命令而不是听你讲，>16 读作机器代打。纯 ASCII 命令可提到 18 |
| `logRate` / `logChunk` | 54 char/s / 3 | 日志揭示速率与分块粒度，本卡第二命门；`chunk=1` 退化成逐字符（那是人在敲，不是机器在吐），`chunk>5` 每簇太长读作整行硬切；速率必须**明显高于** `cps`，两者拉平就分不出"人打的"和"机器吐的" |
| `submitGap` | 0.36s | 打完到按回车的停顿（手指抬起再敲那一下）；=0 读作自动脚本，>0.7s 观众以为卡住 |
| 行间延迟 `d` | 0.14~0.50s | **必须不等距**：工具调用前久（它在想）、diff 两行几乎连着（同一次编辑）、结论前再顿一下；全表同值一眼是假数据 |
| `dotHz` | 1.1 | 工具调用状态点的呼吸频率；>1.6 读作焦虑闪烁、<0.7 看不出在动。只改亮度，加位移就撞库内"不做微抖"的偏好 |
| `cursorHz` | 2 | 方块光标闪烁；终端行业默认，比聊天卡的 1Hz 快一档（这一档差就是"终端"和"输入框"的手感差） |
| 日志行数 | 6~8 行 | 一条因果链的容量；<5 行链条不完整（看不出"调用 → 结果 → 改动 → 结论"），>10 行观众开始读日志、离开你的讲述 |
| 语义色位置 | **只给 `+` 行与 `✓`** | del 行用灰不用红；两色都上就变成彩虹 diff，"改了什么"反而看不清 |

## 已知坑
- 三段同时淡入或乱序——丢掉"界面在铺开"的阅读引导；顺序必须是框 → 右栏 → 提示行。
- 命令行和日志同速同粒度——分不出"人在敲"与"机器在吐"，整段变成一台机器自言自语。
- 日志逐字符匀速（`chunk 1`）——一眼是 `setInterval` 教程；机器输出是成簇蹦出的。
- 行间延迟全表等距——节奏机械，一眼是假数据；真实智能体每一步耗时长短不齐（尤其 diff 两行必须几乎连着）。
- 工具调用行没有状态点，或状态点全程定亮——丢掉"它在干活"这一拍，工作日志退化成静态文本逐行出现。
- 状态点加抖动/旋转/位移——撞库内偏好（手作感靠形状不靠微抖）；只改亮度就够。
- diff 的 `-` 行上红色——彩虹 diff，"改了什么"反而看不清；`-` 用灰，语义色只给 `+`。
- 语义色发给多个类型（工具调用蓝、结果黄、`+` 绿、`-` 红全上）——"文件真的被改了"这一拍没有重量。
- 提交后命令行不退灰——命令行与日志同亮，观众读不出哪个是输入哪个是输出。
- 提交后提示行光标不撤——终端里同时两个光标在闪，一眼是 bug。
- 行光标打完不撤（常驻已完成行末）——七行同时闪成圣诞树；且行间停顿段画面不再静止。
- 未到时刻的行用 `display: none`——行一出现就把整段重排一遍，读作"每出一行抖一下"；用 `visibility: hidden` 占位。
- 结果行不缩进不带折角——因果关系断了，读作两条并列的日志；缩进 + `⎿` 才表示"这是上面那次调用的返回"。
- 结论行放在中间——后续日志会把它冲下去，观众记不住结果；结论永远末行。
- **把 Claude Code 的皮灰阶化**（2026-08-25 用户定版否掉的做法）——灰阶终端是"某个终端"，
  "我真的让这个工具干过这个"的指向性就没了。照抄陶土橙 `#D97757` 与那组深底取值。
- 吉祥物换成方块几何占位——像素兽是这个工具首屏最强的识别物，换掉之后首屏就认不出了；用源码 `Mascot` 那条 path。
- 命令写成 `lorem` 或假路径——观众读得出假，"我真的让它干过这个"的说服力归零；写真实感的文件路径与任务。
- 日志写十几行完整 agent trace——终端是**证据**不是内容；6~8 行的一条链足够，再多观众开始读日志。

## 复用指引
- props：仅 `hostSrc`（角标主持人）；命令 / 日志在 `CONFIG.prompt` / `CONFIG.lines`，身份栏与 What's new 文案在 JSX 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/claude-code.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长由 `buildSchedule()` 按字数算出（meta 随之）。
- HTML/GSAP：demos/claude-code/index.html。**换内容只改 `CONFIG.prompt` 与 `CONFIG.lines`**——
  每行 `{ k, t, d }`：`k` 取 `tool`（工具调用，带状态点）/ `res`（结果，带 `⎿` 折角缩进）/
  `del`（diff 删除，灰）/ `add`（diff 新增，唯一语义色）/ `ok`（结论，带 `✓`），`d` 是行间延迟。
  时刻表 `buildSchedule()` 按字数自动重算（**不要手补时间**）。
  节奏参数全在 `CONFIG`（`cps` / `logRate` / `logChunk` / `submitGap` / `dotHz` / `cursorHz`）；
  身份栏文案改 `.colL`（欢迎语 / 模型 / cwd），What's new 改 `.colR` 的 `<li>`；
  语义色改 `.lg.add` 与 `.lg.ok b` 两处的 `color`（报错场景把这抹绿换成警示红，同样只给一行）；
  **陶土橙与那组深底不要改**——它们是 Claude Code 的皮，属于内容（要改就是在做另一个工具的卡）；
  改字号要同步改 `.lg` 的 `height`（行高）与窗高——本卡日志不滚动，但行高不齐会让停顿段看着"漏了一行"。
- Remotion 移植：本卡 tsx 就是移植终点，可直接抄的部分——`CONFIG`（`boxFade/colRFade/promptFade` 三段窗、`typeStart 1.60`、`cps 11`、`submitGap 0.36`、`logRate 54 / logChunk 3`、`dotHz 1.1`、`cursorHz 2`）、`buildSchedule()`（按字数一遍算完所有时刻）、`fadeUp(t, [a,b])`（独立 opacity 窗 + 9px 上移）、`backOut(p, 1.05)`（窗体弹入）。
  秒 ↔ 帧换算（30fps）：三段窗 = 原版 `fadeUpAt[6,22]/[12,30]/[18,36]` = [0.20,0.73]/[0.40,1.00]/[0.60,1.20]s、
  起打第 48 帧 = 1.60s、`submitGap` 0.36s ≈ 11 帧。
  原版 remocn 组件**止于命令打完**（160 帧 = 5.33s 定格，只演到人按回车之前）——
  回车 / 工具调用 / 结果 / diff / 结论这条因果链是本卡补的。日志部分的帧驱动写法与
  [terminal-typing-log](terminal-typing-log.md) 完全一致：
  `const linear = Math.floor(interpolate(frame, [start, start+dur], [0, len], {extrapolateLeft:'clamp', extrapolateRight:'clamp'})); const revealed = Math.min(len, Math.ceil(linear/3)*3)`；
  状态点 `0.35 + 0.65*(Math.sin(2*Math.PI*((frame-start)/fps)*1.1)+1)/2`；
  行光标 `Math.floor((frame/fps)*2) % 2 === 0 && revealed < len`。
  **不要用 `Math.random` 给速率加抖动**——多趟渲染会闪；分块本身已提供不匀感。
- 剪辑软件对应物：剪映/CapCut——终端窗是一张静态深底图，三段错峰是三个图层各自"向上滑入 + 淡入"**错开 0.2s 起始**；
  命令行用一个文本层套"打字机"入场（速度调到 3 帧/字），提交后**换成一个灰色文本层硬切**（这就是"退灰"）；
  日志每行一个文本层，打字机预设的速度要调到能看出成簇（多数预设做不到，可退而把每行切成 2~3 段硬切）；
  行间延迟就是各层起始时间**故意不等距**；状态点用一个小圆图层配"呼吸"循环预设（**只改不透明度**，
  凡是带缩放/位移的预设一律不用）。AE——一个 Slider 当时钟，
  日志的 Source Text 用 `text.sourceText.substring(0, Math.ceil(n/3)*3)`（`ceil/3*3` 就是分块），
  状态点 Opacity 用 `0.35 + 0.65*(Math.sin(time*2*Math.PI*1.1)+1)/2`，
  光标用方块 Solid 配 `Math.floor(time*2)%2` 的 Opacity 表达式。
  任何软件的"终端/黑客打字预设"一律不用——全是逐字匀速 + 常驻闪烁光标，两条命门全踩。

## 动效范围
- 属于本卡的：三段错峰淡入按**阅读顺序**排（欢迎框 → 右栏 → 提示行，间距 0.20s，各带 9px 上移且淡入窗独立于窗体位移）；欢迎框的骑边标题（标题片用窗体底色盖掉一段虚线）；命令行逐字符揭示（`chunk 1`，人在敲）与日志分块突进（`ceil(linear/3)*3`，机器在吐）**两条速率差一个量级**这条纪律；方块光标三态（打字中实心 / 待回车 2Hz 闪 / 提交后即撤）；提交后命令行退成灰这一层次切分；「工具调用 → 结果 → diff → 结论」这条因果链的结构（结果行缩进带折角挂在调用行下）；**行间延迟不等距**（调用前久、diff 两行几乎连着、结论前再顿）；工具调用状态点在出结果前 1.1Hz 呼吸、出结果即定亮（只改亮度）；行光标只在该行未打完时存在（打完即撤，停顿段画面真静止）；四级颜色分级里"**语义色只给 diff `+` 行与 `✓`**、del 行用灰"这条纪律；未到时刻的行 `visibility: hidden` 占位（布局零重排）；"6~8 行一条链"这个容量上限。
- 不属于本卡的：demo 那句「改 src/theme.ts，加一个深色模式开关」与七行日志的具体文案（142 行、8 行、`useColorScheme()` 全是演示语境）、「欢迎回来，阿维！」「~/code/koubo-site」这两处可换的身份文案、What's new 那三条、800×456 这个窗尺寸与 12.5~14px 字号这组等比换算、角标主持人（数字人）。
  **注意与其他卡不同：Claude Code 的皮（陶土橙 `#D97757`、`#1B1A18` / `#3A3633` 这组深底、`#E8E5DD` / `#8A857C` / `#6B6660` 三级字色、macOS 三灯真色与 12px 圆角、像素兽吉祥物、「Claude Code v2.0.0」这个骑边标题）属于"内容本身"而不是"可换的风格"**——见下面的底色要求。同一套结构当然可以套在别的 coding agent TUI 上，但那时皮要换成那个工具的皮（换了就不叫 claude-code 了）。
- 迁移接口：`CONFIG.prompt` 与 `CONFIG.lines` 是唯一的迁移入口——把命令与日志换成你真实跑过的那一次（保留「调用 → 结果 → diff → 结论」四段结构与**不等距**的 `d`，结论永远末行，`add` 行只有一条）；语速变化时只改 `submitGap` 与各行 `d`（**`cps` / `logRate` / `logChunk` / `dotHz` / `cursorHz` 保持不变**——这五个是手感常量，跟着语速缩放会让快语速下的分块糊成匀速）；尺寸按画幅等比缩放，`.lg` 行高与窗高要一起改；竖屏把窗宽收到画幅宽度的 94%、把 What's new 栏整列去掉（双栏在竖屏里挤成两条窄柱）、日志文案缩短到不折行（等宽字体折行会破坏行高等距）；报错场景把 `add` 的绿换成警示红、`ok` 行换成 `✗ + 报错摘要`，**时序一律不动**。
- 底色要求：**产品皮 = 内容本身，2026-08-25 用户定版：完全还原产品样式**。本卡涉及真实产品界面（Claude Code 终端），
  所以取值锁在源码 `THEMES.dark`（窗体 `#1B1A18` / 窗饰条 `#3A3633` / 主文 `#E8E5DD` / 次文 `#8A857C` /
  更暗 `#6B6660` / 框线与标题 = accent `#D97757`），**不受"白舞台中性化"约束**。
  这一条与 [terminal-typing-log](terminal-typing-log.md) 的深底例外叠加成立："命令行"这层语义本来就靠深底，
  且 diff `+` 行的绿只有在深底上才有足够对比。舞台本身仍是白底，深色只占那个窗口。
  Claude Code 另有浅色主题（tsx 未做；页 `#E8E5DD` / 窗饰条 `#D8D3CA` / 窗体 `#FBFAF7` / 主文 `#1F1E1D` / 次文 `#73726C`，
  **accent 不变**——陶土橙是身份色，跨主题不动），需要浅色 Claude Code 时整套换过去，此时 `+` 行的绿要换成 `#1a7f3c` 一级，否则在浅底上糊掉。
- 与相邻卡的分工：**vs [terminal-typing-log](terminal-typing-log.md)（通用终端，最需要对照读）**——那张是 **stdout 流水**（命令 → 日志 → 结论，`...` 结尾行悬停 0.6s、写满 8 行后缓冲区整跳一个行高），演的是"我跑了一遍、它装上了/构建成功了"；本卡是**因果链**（工具调用 → 结果 → diff → 结论，状态点呼吸、结果行缩进挂靠），演的是"AI 到底干了什么、改了哪一行"。讲构建/部署/安装用那张；讲 AI 编程用本张。两张共享分块突进与行占位这两条手感纪律，但本卡不做滚动（一条链放得下）、那张不做状态点。**vs [chat-gpt](chat-gpt.md)（同批姊妹卡）**——那张是**聊天型** AI 产品（药丸输入条 + morph + 无气泡流式回答），本卡是**终端型**编码智能体（深底窗 + 工具调用循环 + diff）；讲"我和 AI 聊天/提示词技巧"用那张，讲"AI 帮我写代码"用本张。两张一起上就是"聊天型 + 终端型"的完整 AI 产品证据链。**vs [ui-flow-theater](ui-flow-theater.md)（界面剧场子类的母卡）**——那张演的是**人操作界面**（光标走位 + 控件状态机），本卡演的是**界面自己在生成内容**（没有鼠标光标、没有点击，全部动作来自智能体；终端里的文本光标另算）。

<!-- ===== /file: video-talkcraft/references/cards/claude-code.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/color-slam-beat-card.md ===== -->

---
name: color-slam-beat-card
标题: 纯色硬切节拍卡
一句话: 整屏一帧硬切到高饱和纯色底（零过渡零擦除），色块上大字先"显影"后变实、素材卡带投影升入错峰跟上，停 1.5~5s 再硬切回口播——用底色跳变本身当节拍器
适用: 短口播（60s 内）抛观点/下判断/列条目的每一个重音；快节奏、态度鲜明的调性，AI/科技/带货/观点号常用，长口播里当"重锤句"也成立
时长: 单卡 2.5~6s：硬切 0 帧 + 大字显影变实 0.22s（切后 0.18s 起）+ 素材卡升入 0.42s（与大字错峰 0.2~0.5s）+ 停留 1.5~5s + 切出 0 帧（硬切）或 0.34s（色块上移让位）
能量: 高
类别: 转场结构
输入: 场, 文, 人(可选)
语义: 金句, 转场
素材形态: 无
位置: 任意
props: hostSrc
优先级: P0
代码: template/cards/color-slam-beat-card.tsx
---

## 意图
短口播每句都想是重音，但补间转场（扫屏、压入）本身要花 0.3~0.6s，一分钟里放五次就只剩转场在演。
纯色硬切把转场成本压到 0 帧：**底色的跳变本身就是节拍器**——观众不是"看到画面被换掉"，
而是"感到被打了一拍"。命门：**零补间**（一帧到位，任何淡入/擦除/缩放都会把节拍摊成动画表演）、
**一片一色**（一张卡一个高饱和纯色，出现第二个色或渐变，跳变的"打击感"立刻散掉）、
**跳变之后才轮到元素动**（硬切是节拍，卡上元素错峰入场是节拍之后的余韵，两者不能同帧抢戏）。

## 动效核心
- 满屏纯色层 `.slam-card`（`position:absolute; inset:0`）：`tl.set()` 一帧 `autoAlpha 0→1` + 写入 `background`，**零 duration**——这是整张卡唯一的"转场"
- 大字 `.slam-title`（62~72px、800 字重、左栏竖向居中）：硬切同帧就已在位，但颜色是**同色系淡色**（tint，如底 `#1B3CF5` 配 `#8A9BFF`）；切后 0.18s 起 `color → #fff`，0.22s，`power2.out`——像相纸显影，不是淡入
- 小字戳 `.slam-sub`（字距 5px 的编号/副题）：比大字变实再晚 0.12s，`autoAlpha 0→1`，0.24s
- 素材卡 `.slam-shot`（白底 + 圆角 + 深投影，投影是"实体被拍上来"的语义）：与大字错峰 **0.2~0.5s** 后入场，`y +56px → 0` + `blur(10px) → 0` + `autoAlpha 0→1`，0.42s，`power3.out`——升入与模糊飞入同一条 tween
- 停留期（1.5~5s，由口播念完这句的时长决定）：元素**不再做任何动作**，整组静置（2026-08-29 用户定版 `driftPx=0`——此前的极缓漂移在成片里被读成"画面在飘"；超长停留怕读成卡帧时可开 ≤8px 线性漂移）
- 切出二选一：① **硬切**（`tl.set(autoAlpha 0)`，零帧回口播——默认，节奏最硬）；② **色块整体上移让位**（`yPercent 0 → -100`，0.34s，`power3.out`，整块带元素一起走，底下口播从下方露出）
- 连续多卡时每张换一个高饱和底色，色相拉开（demo 演蓝 → 红），"一片一色"是纪律不是配色
- 与邻卡的分工：`shape-wipe-transition` 是色块扫过屏（0.6s 补间），`chapter-title-card` 是色块压入 + 编号章名分层（2.5s 仪式）；本卡**零补间**，节奏感全部来自跳变

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 切入过渡 | 0 帧 | 这是本卡的命；给它 0.1s 淡入就退化成普通标题卡，节拍变成动画 |
| `developAt` | 0.18s | 硬切后多久大字开始变实；0 = 没有显影这一拍，大字读作静态贴图；>0.4s 观众已经开始读淡色字了 |
| `developDur` | 0.22s | 显影耗时；>0.5s 读作"加载中"，<0.1s 看不出显影、等于直接换色 |
| `subDelay` | 0.12s | 小字戳与大字的错峰；0 则两层同出，层次塌掉 |
| `shotDelay` | 0.45s | 大字 → 素材卡的错峰，0.2~0.5s；0 = 一坨糊上来，>0.7s 卡上出现空档、观众以为没了 |
| `shotRise` | 56px | 升入行程；>120px 读作从画外飞进来抢戏，0 则只有模糊变化、没有"升"的方向 |
| `shotBlur` | 10px | 模糊飞入起始值；0 = 只升不飞少了速度感，>20px 前几帧糊成一团脏 |
| `hold` | 1.5~5s | 停留 = 这句口播的长度；<1.2s 大字读不完就跳走，>5s 高饱和底色开始灼眼、观众想快进 |
| `driftPx` | 0（2026-08-29 定版） | 停留期漂移量；默认静置——非 0 时观众读作"画面在飘"；确需防卡帧（停留 >4s）开 ≤8px，>20px 读作运镜失误 |
| `liftOut` | 0.34s | 上移让位耗时（仅 lift 出场）；>0.5s 拖节奏，<0.2s 不如直接硬切 |
| 底色饱和度 | 高饱和纯色 | 低饱和/灰调 = 跳变力度不足，读作换了张 PPT；渐变或双色 = "一片一色"破功，打击感散掉 |

## 已知坑
- 给硬切加了淡入/擦除/缩放——0.2s 的补间就把"打了一拍"摊成"播了个动画"，本卡唯一的机制当场失效。
- 底色用渐变、双色拼接或低饱和莫兰迪——跳变幅度不够，观众读作"换了张幻灯片"，不是节拍。
- 大字与素材卡同帧入场——两个动作抢同一拍，画面糊成一坨，错峰 0.2~0.5s 才有层次。
- 大字做淡入（opacity 0→1）而不是同色系淡色变实——淡入是"字飞进来"，显影是"字一直在、只是浮出来"，后者才不与硬切抢那一拍。
- 给停留期加漂移求"活着"——实测（2026-08-29 用户审片）满屏纯色上的整组漂移读作"画面在飘"，比担心中的"卡帧"更扎眼；停留期的"活着"感交给素材卡入场余韵与口播节奏，不靠位移。真要开（停留 >4s）也压在 ≤8px。
- 停留超过 5s——高饱和满屏色灼眼，节拍卡变成了罚站卡。
- 素材卡没有投影、直接贴在纯色底上——读作矢量插画的一部分，失去"把证据拍上来"的实体感。
- 连着三张卡用同一个底色——跳变了但色没变，等于只切了内容；每张换色（且各自一片一色）才是节拍器。

## 复用指引
- props：仅 `hostSrc`；底色在 `CONFIG.cards`，大字 / 小字文案与素材卡内容在 JSX 常量里（`cards[]` 的 title / sub / shot），换内容需改源码；素材卡是 CSS 假截图（`Shot1` / `Shot2`），放真图把 `<Shot1 />` 换成 `<Img>`（Remotion 自带），其余不动。
- Remotion/tsx（skill 首选）：template/cards/color-slam-beat-card.tsx——自包含单文件，复制进工程即可用；节奏参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/color-slam-beat-card/index.html。核心函数 `slamBeat(tl, el, spec, at, exit)` 可整段摘走，`exit` 传 `"cut"`（硬切回）或 `"lift"`（色块上移让位）。换色改 `CONFIG.cards`（每项 `{bg, tint}`，tint = bg 的同色系淡色）；换文案改 `.slam-title` / `.slam-sub` 内文本；加卡 = 复制一段 `.slam-card` DOM + `CONFIG.cards` 多一项 + 多调一次 `slamBeat`；节奏全在顶部 `CONFIG`。
- Remotion 移植：切入用**帧判断而非 interpolate**——`frame >= cutFrame && frame < outFrame` 决定纯色层是否渲染（任何 interpolate 都会引入补间，破坏零帧硬切）；显影用 `interpolateColors(frame, [d, d+devF], [tint, '#fff'])`；素材卡 `interpolate(frame, [s, s+riseF], [56, 0], {easing: Easing.out(Easing.cubic), extrapolateRight:'clamp'})` 驱动 `translateY`，同区间另一条 interpolate 驱动 `filter: blur(Npx)`；停留期静置（`driftPx=0` 定版；开启时是一条贯穿的线性 interpolate）；lift 出场 `interpolate(frame, [o, o+liftF], [0, -100])` 驱动 `translateY%`。每张卡一个 `<Sequence>`，硬切 = 两个 Sequence 首尾相接、无 transition。
- 剪辑软件对应物：剪映/CapCut——纯色素材直接铺在主轨上，**转场处不放任何转场**（这就是全部），大字用关键帧只改文字颜色、素材卡用"位置 + 模糊"两条关键帧；AE——纯色层（Solid）按时间切入切出、层间不加效果，文字层用 Fill 颜色关键帧做显影，素材层 Position + Fast Box Blur 关键帧配 Easy Ease；上移让位 = 把纯色层与其子层预合成后打 Position 关键帧。

## 动效范围
- 属于本卡的：**满屏纯色层一帧硬切进出（零 duration、零擦除、零缩放）这个机制本身**；大字从同色系淡色 `color → 实色` 的"显影"（切后 0.18s 起、0.22s、`power2.out`）；小字戳晚 0.12s 的 `autoAlpha` 跟进；素材卡与大字错峰 0.2~0.5s 后的 `y +56→0` + `blur 10→0` 同 tween 升入（0.42s、`power3.out`）；停留期元素整组静置（`driftPx=0`，2026-08-29 定版；≤8px 漂移是可选开关）；切出的两种收法（硬切 / `yPercent 0→-100` 整体上移让位 0.34s `power3.out`）；以及"一张卡一个高饱和纯色、连续多卡换色"这条纪律。
- 不属于本卡的：底下口播场景（数字人占位 + 字幕文案）、素材卡里的假截图/假图表内容、大字与小字的具体文案与字号字距、demo 连演两张卡与 `gapBetween` 间隔（仅示范节奏，实际由口播落点决定）、左字右卡的这套构图（元素落位可自由改，错峰时序才是本体）。
- 迁移接口：**底色 = 复用者的品牌色接口，但有语义约束**——改 `CONFIG.cards` 的 `bg`（每项另配一个同色系淡色 `tint` 作显影起点），必须是**高饱和纯色、一片一色**，多卡之间色相拉开；卡上文字色随底色明度取反（当前 `#fff` / `rgba(255,255,255,.78)`）。时序全在顶部 `CONFIG`，其中 `hold` 按每句口播实际时长逐卡改（1.5~5s），`developAt`/`shotDelay` 的错峰关系跟着总时长等比缩放即可；换尺寸时只需重算 `shotRise`（约屏高 10%）与字号，硬切与错峰时序与画幅无关；竖屏改成上字下卡时把素材卡的升入方向保持"由下往上"不要反。
- 底色要求：**需要高饱和纯色底（动效语义必需，中性化契约的例外）**——本卡的机制就是"底色跳变当节拍器"，白底或低饱和底根本没有可跳的变化，跳变幅度即动效强度。demo 的口播场景仍是白底（中性），只有节拍卡这一层用高饱和色，且该色是唯一的品牌色接口。

<!-- ===== /file: video-talkcraft/references/cards/color-slam-beat-card.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/converging-arrows.md ===== -->

---
name: converging-arrows
标题: 双箭头聚焦
优先级: P1
代码: template/cards/converging-arrows.tsx
一句话: 两支手绘箭头从对角空白处几乎同时画向关键词（错峰仅 0.06s，杆 0.26s + 头 0.11s，箭尖停在离词 16px 处不戳字），两支箭尖都到位那一帧关键词换成强调色（只换色、不缩放），箭头留在屏上 hold 1.6s
适用: 口播抛出"记住这 3 点""关键就在这里"这种**要观众钉住一个词**的时候；教学、清单、方法论口播；需要比手绘圈更强的指向性（箭头有方向，圈没有）；不适合同屏有多个候选词（双箭头只能夹一个目标）
时长: 起手静置 0.42s → 第一支画杆 0.26s（第二支 +0.06s 切入）+ 箭头须 0.11s → 关键词换色 0.1s → 收尾定格 1.6s；共约 2.6s
能量: 中
类别: 强调标注
输入: 文, 人(可选)
语义: 强调
素材形态: 无
位置: 任意
props: hostSrc
---

## 意图
箭头和圈的区别是**方向**。圈说"就这几个字"，箭头说"从这里看过去，看那个字"——
它多了一个来向，所以能表达"我把你的视线牵过来"。两支从对角同时来的箭头再加一层意思：
**夹住**。视线从两个方向被同时挤到中间那个词上，那是全库指向性最强的强调手段。

命门两条：① **箭头先到、词后变**。两支箭尖都到位的那一帧关键词才换成强调色。
反过来（词先动）读作"这个词把箭头吸引过来了"，主动方错了——本卡的语义是
**口播者用箭头指给你**，动因在箭头。
（**关键词不做缩放**，用户 2026-08-25 定版：箭头已经把视线送到位了，
字再放大缩小一下是第二个动效，抢箭头的戏；换色是状态确认，够了。）
② **箭尖必须留白**（离词 14~18px）。戳到字上就成了"划掉/打叉"，语义直接反向；
留白才是"指向"。这一条比看起来重要：戳字的箭头是最常见的廉价错法。

第三条不算命门但一样致命：**两支错峰只有 0.06s**（几乎同时）。错峰放大到 0.2s 以上，
读作"两支箭依次飞来"——那是两次强调，"夹住"的同时性没了。

## 动效核心
- **箭头层 = 盖在文字上的全屏 SVG**（`viewBox="0 0 960 540"`、`pointer-events:none`），
  `fill:none` + `stroke-linecap/linejoin: round`
- **箭尖坐标从关键词盒子推出**：tsx 里关键词盒子是 `CONFIG.box = {x:182, y:262.4, w:130.64, h:76}`
  （量自 demo 运行时 `boxOf(word)`；换文案要重量一次再填回），箭尖落在**盒子外的对角方向上**、
  离盒子角点 `tipGap / √2`（命门②）。HTML demo 用 `data-arrow="key"` 运行时量盒子，改文案箭头自动跟着走
- **两支箭头的差异**（对称但不对等 —— 全等的两支读作镜像图形）：

  | | 右上支 | 左下支 |
  |---|---|---|
  | 起点 | +0 | +0.06s（几乎同时） |
  | 指向角 | 关键词右上角 | 关键词左下角 |
  | 起笔点位移 | (+176, −132) | (−124, +104) — 更短 |
  | 杆弧度 `bow` | +24（向外凸） | −20（**反向**凸） |
  | 箭须长/张角 | 21px / 27° | 18px / 25° |

- **杆的弧度是手作感的主来源**：起笔点 → 箭尖的弦，两个控制点（0.3 / 0.68 处）沿弦的
  **法向**偏 `bow`。直线杆读作 UI 引线（Figma 的连接线），不是手画的箭头
- **起笔粗收笔细**：杆的同一条 `d` 叠三层 stroke（4.8 / 3.8 / 2.8px），每层
  `stroke-dasharray = [全长×frac, 全长]`（frac = 0.16 / 0.46 / 1），三层 `dashoffset`
  由**同一个弧长进度**驱动（lockstep）—— 笔尖只有一个。
  箭须用单一线宽（它在收笔端，不需要粗细变化）
- **先杆后头的两笔笔顺**：杆 `dashoffset` 全长→0，0.26s `power3.out`；
  杆到位那一刻箭须接上，0.11s `power2.out`。**两根须长度略不等**（21 / 18.5px，
  张角 27° / −32°）—— 等长对称的箭头是矢量图标
- **命门①的落点**：`allTipsAt = max(两支的 杆+头 结束时刻)` —— 两支都到位才换色。
  关键词 `color` 由墨黑切成强调色（0.1s 线性，不做渐变——换色是状态切换不是过渡）。
  **不做 scale**（用户定版）：关键词全程零位移零缩放，只有颜色一个通道在变
- **关键词起手必须是平淡的黑字**：换色的力量是相对前半拍的落差，一上来就是强调色就没有落差
- **排版是本卡的前提**：箭头要从对角**空白处**画进来，所以上一行要故意写短、
  给右上方留出跑道。这不是动效，是用这张卡时必须让出的版面
- **画完保持干净静置**：不做 line boil / 定格抖动（design-language.md §4）
- **层级**：白舞台 → 文字（两行，上行 dim 实色）→ 箭头 SVG 层 → 主持人占位（右 47%）

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `tipGap` | 16px（14~18） | **本卡第二命门**；=0 箭尖戳进字里读作"划掉/打叉"（语义反向）；>26px 指向变含糊，读作"箭头指的是这一带" |
| `arrows[1].at` | 0.06s | **同时性**；=0 也成立（更"夹"）；>0.2s 读作两支箭依次飞来（两次强调，夹住感没了） |
| `colorDur` | 0.1s | 关键词换色时长；本质是硬切（`ease: none` 的 0.1s 只为躲过 1 帧的突变），>0.3s 变成颜色过渡，读作"字慢慢想起来自己是重点" |
| `bow`（+24 / −20） | 两支反向 | 杆的弧度；=0 是直线（UI 引线，一眼假）；两支同向读作两支平行箭头（不是夹击）；\|bow\| >45 杆弯成钩子 |
| `shaft` | 0.26s | 画杆耗时；<0.15s 箭头"闪"出来看不出方向；>0.45s 单支像进度条 |
| `headDur` | 0.11s | 箭须耗时（收笔快扫）；>0.25s 箭头会"迟到"（杆到了半天才长出头） |
| `fromDX/DY` | (176,−132) / (−124,104) | 起笔点相对箭尖的位移 = 箭头长度与来向；两支等长读作镜像图形；杆长 <90px 读作小箭头图标不是"从远处指过来" |
| `headLen` / `headSpread` | 21 / 27°（两须略不等） | 箭须长度与张角；张角 <18° 读作细尖（针不是箭），>40° 读作 V 形；两须完全等长对称一眼是矢量图标 |
| `tiers`（4.8/3.8/2.8） | frac 0.16/0.46/1 | 最细那层是杆的"本宽"；<2px 读作 UI 描边，>6px 粗杆压住周围的字 |
| `startDelay` | 0.42s | 等口播念到"记住"；<0.2s 箭头比声音早 |
| `hold` | 1.6s | 收尾定格，箭头保留在屏上让观众看清"夹住的是这几个字" |

## 已知坑
- 词先动、箭头后到——本卡最致命的一条。动因反了，读作"这个词把箭头吸过来了"，
  而本卡的语义是口播者用箭头把你的视线牵过去。
- **`tipGap` 量的是箭尖到目标盒子角点的留白（沿对角 `tipGap/√2`），盒子必须是真正要夹的那几个字的实测盒**（2026-08-28 实战踩坑）：
  目标是一整行宽词（几百 px）时若把整行当盒子、或把箭尖对到行中心，两支共线箭杆会整段插进字里、
  读作一条删除线。宽目标要把 `CONFIG.box` 收到关键的那几个字，或干脆把箭尖点挪到词框外缘。
- 给关键词加 punch 缩放（`scale 1.18→1` 那一档）——**2026-08-25 用户定版删除**。
  箭头已经把视线送到位，字再"炸"一下是同一拍上的第二个动效，两个都在抢注意力；
  换色本身就是确认，缩放多余。
- 箭尖戳到字上——语义从"指向"翻成"划掉/打叉"。最常见的廉价错法。
- 两支错峰给到 0.2s 以上——读作两支箭依次飞来（两次强调），"夹住"的同时性没了。
- 杆画成直线——一眼是 Figma 连接线 / UI 引线。手画的箭头杆一定有弧度，而且两支弧向相反。
- 两支箭头做成完全镜像（等长、同弧度、同箭须）——对称但不对等才是手画的；
  完全镜像读作一个矢量图形的两半。
- 箭须两根等长且严格对称——矢量图标的特征。真实的箭头两根须一长一短、张角略不等。
- 用 `<marker>` / `<polygon>` 做箭头头部——那是几何三角形（矢量图标），
  而且没法参与"先杆后头"的笔顺描画。箭须必须是两笔 path。
- 箭须角度自己填死值——杆有弧度，末端切线方向不是"起点→箭尖"的方向；
  须必须按**杆末端切线**（`c2 → tip`）算，否则箭头会朝歪。
- 用 `stroke-width` tween 做"起笔粗收笔细"——那是整条杆一起变粗；笔压是沿线分布的。
- 三层 stroke 各跑自己的 tween——三个笔尖互相超车。必须共用一个弧长进度。
- 排版不留跑道就上这张卡——箭头会从别的字上穿过去，读作"箭头划掉了上一行"。
  用这张卡必须把对角两片区域腾空（demo 里上一行故意写短就是为了这个）。
- 关键词一上来就是强调色——"炸"是相对前半拍的落差，没有平淡的前半拍就没有落差。
- 同屏有两个以上候选词——双箭头只能夹一个目标。要点名多项请换 `scribble-annotation`
  的扇形多箭头变体（整组淡入 + 数字逐个弹入）。
- 画完加 line boil / 定格抖动——本库定版禁项（design-language.md §4）。

## 复用指引
- props：仅 `hostSrc`；两行文案与关键词在 JSX 常量里、关键词盒子在 `CONFIG.box`，换内容需改源码并重量盒子。
- Remotion/tsx（skill 首选）：template/cards/converging-arrows.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/converging-arrows/index.html。**换关键词不用改坐标**：
  给目标元素加 `data-arrow="key"`（箭尖从它的盒子算，改文案自动跟随）。
  换来向改 `arrows[].corner`（`topRight`/`bottomLeft`/`topLeft`/`bottomRight` 四选二）
  + `fromDX/DY`；弧度调 `bow`（两支必须反向）；节奏调 `shaft`/`headDur`/`arrows[1].at`；
  换色改 `color`（同时是箭头色与关键词换色的目标色 —— 同屏只有一个"看这里"色）。
  核心逻辑 = `CONFIG` + `boxOf()` + `arrowPaths()` + `inkStroke()` + `register` 内那段时间线，可整段摘走。
  **单支版**：`arrows` 只留一支即可（语义从"夹住"降级成"指向"，能量降一档，也很好用）。
- Remotion 移植：`d` 用同一套 `arrowPaths()` 在组件外预生成（纯函数、无随机 → 帧间一致）。
  描画三层手算：第 k 层 `strokeDasharray = [L·frac_k, L]`、
  `strokeDashoffset = max(0, L·frac_k − p·L)`，
  `p = interpolate(frame, [s, s+shaftF], [0,1], {easing: Easing.out(Easing.cubic), extrapolateLeft:"clamp", extrapolateRight:"clamp"})`；
  箭须是第二段（`[s+shaftF, s+shaftF+headF]`）。
  关键词只有一个通道：`color` 从 `allTipsAt` 起 0.1s 线性由墨色插到强调色（tsx `lerpColor`；本质是硬切，0.1s 只为躲过 1 帧突变），
  **不给 scale**。
- 剪辑软件对应物：AE = 两个形状图层，各用钢笔画**带弧度的杆**（两个手柄拉出反向弧）+
  `修剪路径`(Trim Paths) End 0→100%（0.26s）；箭须另做一个两段折线路径的形状图层，
  入点比杆晚 8 帧、Trim 0→100% 3 帧；笔压复制杆三层、各层描边宽度不同 +
  `虚线` Dash 设成路径长度的 16%/46%/100% 并给 `偏移` 打关键帧；
  关键词只在箭尖到位那一帧把 `填充颜色` 硬切成强调色（**不打缩放关键帧**）。
  剪映/CapCut 没有描画通道：用"贴纸 → 手绘箭头"选**带弧度**的两款（一支正一支反，
  选静置无抖动帧），入场用"向右擦除/向左擦除"近似描画方向，两支起点差 2 帧；
  关键词换色靠在箭尖到位那一帧切一个同位置的彩色文本层（不做入场缩放）。
- 与本库同类卡的分工：`scribble-annotation` = 圈/线/箭头三笔串行标注**素材里的位置**
  （语境是"跟你一起看这张图"，箭头只是其中一笔）；`callout-line-label` = 引线 + 标签
  （语义是"给这个东西起个名"，有文字标签）；`hand-drawn-ellipse` = 手绘圈
  （"就这几个字"，无方向）；
  **本卡 = 两支箭头从对角夹住一个词 + 词后换色**（全库指向性最强的强调卡；
  它与 `hand-drawn-ellipse` 的分工就是"有方向 vs 无方向"，一屏只能用一种）。

## 动效范围
- 属于本卡的：**箭头先到、词后变**的因果时序（`allTipsAt` = 两支的杆+头都结束，才换色；两支中较慢的那支决定换色时刻）；**箭尖留白 14~18px** 这条落位纪律（戳字即语义反向）；**两支错峰仅 0.06s** 的同时性（"夹住"的全部来源）；两支箭头**对称但不对等**（长度不等、弧向相反、箭须长短与张角略不等）这条形状要求；杆的弧度靠控制点沿弦法向偏 `bow` 实现（直线杆即 UI 引线）；**先杆后头**的两笔笔顺，箭须按**杆末端切线**算（保证永远朝目标）；`dashoffset` 全长→0 的描画（杆 0.26s `power3.out`、须 0.11s `power2.out`，起收有快慢）；**多层 stroke 共用一个弧长笔尖**实现的"起笔粗收笔细"（杆三层 4.8/3.8/2.8px、frac 0.16/0.46/1；须单一线宽）；箭尖绑定关键词盒子的对角方向这条坐标纪律；箭尖到位那一帧关键词 `color` **硬切**成强调色（不做颜色渐变），且关键词**只换色、不缩放不位移**（用户 2026-08-25 定版删掉 punch）；关键词起手必须是平淡黑字（落差的前半拍）；箭头 hold 期保留在屏上（不淡出——它是"指向"的凭证）；画完保持干净静置——不做 line boil / 定格抖动；箭头 SVG 层盖在文字之上、`pointer-events:none` 的层级关系。
- 不属于本卡的：demo 那两句「今天只要你 / 记住这 3 点就够了」的具体文案、32/40px 两级字号与 400/600 字重、上行用 dim 实色这个排版选择、橙 `#e8720c` 这个取值（参考图②同色系，换任何一个 accent 都成立）、白底舞台、右侧 47% 的主持人（数字人）占位、正好两支箭头（单支版语义降级为"指向"，同样成立）。**但"对角两片区域必须腾空"是用本卡的前提条件**——它不是动效本体，却是动效成立的版面约束，复用时必须一起搬。
- 迁移接口：`color` 是唯一的颜色入口（箭头色 = 关键词换色目标色）；`tipGap`、`fromDX/DY`、`headLen`、`tiers` 的三个线宽按画幅**同比缩放**（960 宽的值 ×2 用于 1080p），`bow` 按 `fromDX/DY` 同比缩放（弧度是相对弦长的），`headSpread` 是角度常量不缩放；节奏 `shaft`/`headDur`/`arrows[1].at`/`startDelay`/`hold` 与画幅无关，只跟语速走；换来向改 `corner` + `fromDX/DY`（四个角任选两个对角；同侧两支读作平行箭头，不成立）；关键词换位置只改 `data-arrow`；目标不是 DOM（视频/图片素材上的字）时把 `boxOf()` 换成手填矩形，`arrowPaths()` 不用动。竖屏改用 `topRight` + `bottomLeft` 且把 `fromDY` 加大、`fromDX` 收小（竖屏的空白在上下方向上）。
- 底色要求：白底即可（马克笔橙压在白底上是本卡的原生语境）。深底上把 `color` 换成高亮度色（`#ff9f45` 级），并把最细那层 `tiers[2].w` 从 2.8 加到 3.6——深底吃掉细线的视觉重量，2.8px 的收笔端在深底上会断。**底不能有高频细节**——箭头是细线元素，实拍花底上会看不清指向（要么先压一层半透明底板，要么加白色描边层 outline）。

## 落位自检（2026-09-05 用户定版，选卡时抄进 SHOTBOOK 该镜自检列）
- 标注几何（框 / 圈 / 线 / 箭头 / 放大镜锚点）一律由**目标的实测包围盒**反推——DOM `getBoundingClientRect` / `measureText`，四边留白 16~24px 等距，**不目测**。
- 实现后抽该镜定妆帧核对：标注是否恰好套住 / 指向目标，偏差 **> 8px 返工**（`references/layout.md` §3）。
- 目标会滚动 / 移动时，标注钉在内容坐标系随内容动（SKILL.md ③）。

<!-- ===== /file: video-talkcraft/references/cards/converging-arrows.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/corner-bracket-frame.md ===== -->

---
name: corner-bracket-frame
标题: 对角角框
一句话: 左上与右下两个 L 形角框**同帧**从各自的外侧对角方向平移 20px 进入，框先立住 0.22s 后标题两行错峰 0.1s 淡入上浮，画完全部静置
适用: 一段口播的"本集只讲这一件事"式定题——开场立论点、章节小标题、把一句话从口播流里"框出来"；克制而有取景感的调性（知识区、行业分析、纪录片式旁白）；不适合需要砸重音的爆点句
时长: 起手静置 0.4s → 角框进入 0.3s → 标题两行错峰 0.1s（各 0.3s）→ 收尾 hold 1.7s；共约 2.7s
能量: 低
类别: 强调标注
输入: 文, 人(可选)
语义: 标题
素材形态: 无
位置: 任意
props: hostSrc
优先级: P1
代码: template/cards/corner-bracket-frame.tsx
---

## 意图
口播里最常见的失败是"每句话都一样重"——观众听了 30 秒不知道哪句是论点。
本卡解决的是**给一句话划定边界**：角框一出，观众立刻知道"框里这句是这一段的题目"。

它和四角取景框是**两种语言**：四个角是"取景/监视器"语义（在看什么），
两个对角角框是"框选/引述"语义（这一块是重点）。本库的其他强调卡都是给
**词**加信号（`keyword-pop-highlight` 砸重音、`highlighter-sweep` 扫荧光笔、
`ink-underline` 划墨线），本卡是给**整块**划边界的（原位出现、定题；画外飞入咬合的 `reticle-lock-on` 是另一档）。

命门三条：
① **两个 L 必须同帧同曲线进入**。对角对称是这个构图的全部骨架，错峰 0.05s 就能看出
"一个先到一个后到"，读作两个独立元素飘进来，取景关系立刻散架。
② **只画两个角，且两臂等长**。三个角、四个角、两臂不等长——三种都会让它从"框选"
掉回"装饰边角"。
③ **框先立住、字后进框**。框与字同时淡入读作一张 PNG；框先到 0.22s 再放字，
才是"我先划范围，然后把话放进来"。

## 动效核心
- **结构**：一个不可见的方框（450×200 @960×540 舞台，左 66 / 上 152）定位在左侧留白区，
  只在左上 / 右下两个角各放一个 54×54 的 L（`border-left + border-top` / `border-right + border-bottom`，
  4px 描边，唯一强调色）；标题两行落在框内左侧 34px 处
- **① 角框进入**：`opacity 0→1` + 沿外侧对角方向平移。左上角框起点 `(x:-20, y:-20)`、
  右下角框起点 `(x:+20, y:+20)`——**两者共用一条 tween**（`gsap.to([tl, br], ...)`），
  从代码层面保证同帧；`0.3s power3.out`
- **② 标题两行**：`opacity 0→1` + `y +6→0`，各 `0.3s power2.out`，错峰 `0.1s`；
  起步点 = 角框起步 + `0.22s`（角框走完约 73% 时，框的形状已经读得出）
- **③ hold 1.7s**：画完全部静置。不做 line boil / 定格抖动（design-language §4）
- **标题下不加下划线/弧线**（用户 2026-08-25 定版）：角框已经把边界划完了，
  再加一道横线是第二个"分隔"信号，两个信号打架；本卡只有"框"这一个动作
- **层级**：白底 → 主持人（右侧列，演示语境）→ 角框与标题（同层）

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `brTravel` | 20px | 角框沿对角方向的进入位移；0 = 只淡入（少了"从画外收进来"的取景感），>40px 读作角框飞进来，抢了标题的戏 |
| `brIn` | 0.3s | 角框进入时长；<0.18s 读作硬现（框的"收拢"过程看不到），>0.5s 观众等着框停下来，口播已经念完了 |
| 臂长 | 54px（≈ 框短边 27%） | **必须两臂相等**；短于框短边 15% 读作装饰小角，长于 40% 就快连成整框（那是 `outline-box-title` 的语言） |
| 描边宽 | 4px @540 舞台高 | 细于 2.5px 在压缩后掉边；粗于 6px 角框比标题还重，主次颠倒 |
| `linesAt` | 0.22s | **框先立住的时长，本卡第三命门**；0 = 框与字同时进（读作一张 PNG），>0.5s 空拍太长像卡了 |
| `lineStagger` | 0.1s | 两行错峰；0 = 两行一起淡入（可用但更平），>0.25s 读作两个独立动效 |
| `lineRise` | 6px | 标题上浮量；0 少了一点重量，>16px 方向感盖过"进框" |
| `hold` | 1.7s | 收尾停留，按两行字数给（每字约 0.13s，读完再留半拍） |

## 已知坑
- 两个角框错峰进入——一眼看出是两个独立元素飘进来，对角对称这个骨架直接消失。
- 画四个角当"取景框"——语义变了（"在看什么"而不是"这块是重点"），而且四个角在白底上非常吵。
- 两臂长度不等（一臂长一臂短）——读作画歪了的装饰，不是取景符号；L 的两臂等长是它成为"符号"的前提。
- 框与标题同时淡入——整组读作一张预先做好的 PNG 贴上来，"我先划范围"这层意思全丢。
- 角框加圆角——L 的直角是它的语义（对齐、精确、机器画的）；圆角一上就成了手绘括号。
- 角框和标题用两种颜色——同屏第二个"看这里"色（design-language §1 红线），角框必须是唯一强调色。
- **在标题下加一道下划线/弧线——2026-08-25 用户定版删除**。角框已经把这块内容的边界划完了，
  底下再来一横是第二个"分隔"信号；两个信号同屏，"框选"这层语义被摊薄，
  而且弧线的手绘感与 L 角框的机器精确感直接打架。要下划线请换 `ink-underline`（那是另一张卡）。
- hold 期给角框加漂移/呼吸——角框是精确的取景符号，动起来就成了"没对准"。

## 复用指引
- props：仅 `hostSrc`；标题两行文案在 JSX 常量里（`.cb-line.l1 / .l2`），换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/corner-bracket-frame.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/corner-bracket-frame/index.html。换文案改 `.cb-line.l1 / .l2` 的文字，
  框的尺寸改 `.cb-frame` 的 `width/height`（框要比文字块四周各留 30px 上下气口）；
  改强调色只动 `:root --acc` 一个变量（角框专用）；节奏全在 `CONFIG`
  （`brTravel`/`brIn`/`linesAt`/`lineStagger`/`hold`）。
- Remotion 移植：两段用一个 `Sequence` 内的两组 `interpolate` 即可，不需要时间线。
  角框：`x = interpolate(f, [0, 9], [∓20, 0], {easing: Easing.out(Easing.cubic), extrapolateRight:"clamp"})`，
  两个角框传**同一个 f 区间**（同帧的保证）；标题两行 `f - i*3` 做局部时钟。
  帧换算 @30fps：`brIn 0.3s ⇒ 9f`、`linesAt 0.22s ⇒ 7f`、`lineStagger 0.1s ⇒ 3f`。
- 剪辑软件对应物：剪映/CapCut——没有现成"对角角框"，做法是两个"边框"贴纸各自打
  位置 + 不透明度两个关键帧，**两个贴纸的关键帧必须放在同一帧**（剪映里对齐靠吸附，
  务必检查）。
  AE——两个 Shape Layer 各画一个 L（Rectangle 描边 + Trim Paths 留 25%，或直接两条 Stroke），
  一个 Null 父级带两个角框同时做 Position（这是保证"同帧"最稳的做法）。
- 与本库同类卡的分工：`outline-box-title` = 完整闭合的描边框（框选一个短语，机器画一圈）；
  `focus-dim-spotlight` = 压暗周围来强调（减法）；`highlighter-sweep` / `ink-underline` /
  `scribble-annotation` = 给词加手绘信号；`callout-line-label` = 引线指到画面里的某个位置；
  **本卡 = 给一块内容划定边界**（对角两个角，取景/引述语义，能量最低的一档"框住"）。

## 动效范围
- 属于本卡的：两个 L 角框**共用一条 tween**、沿各自外侧对角方向 20px 平移 + 淡入进入（0.3s `power3.out`）这条"同帧同曲线"纪律；只画**对角两个**角且两臂等长这条形状纪律；框先立住 0.22s 再放字这个先后关系；标题两行 `opacity + y+6→0` 错峰 0.1s；**标题下不加任何下划线/弧线**（用户 2026-08-25 定版：角框已是唯一的边界信号）；hold 期全部静置（不加漂移、不做 line boil）。
- 不属于本卡的：demo 那句「一条思路 / 讲清楚一件事」的具体文案、52px/700 的字号字重、青色 `#0aa3a3` 这个具体取值（唯一强调色的**位置**属于本卡，色值不属于）、450×200 的框尺寸与 54px 臂长的绝对像素、右侧主持人（数字人）占位、标题落在左侧留白区这个构图（居中、右侧、竖屏上半屏都成立）。
- 迁移接口：强调色 `#0aa3a3` 在 tsx 里写在 `.cb-br.tl / .br` 的四条 border 上（角框专用，同屏不允许第二个），换色四处同改（HTML demo 是 `:root --acc` 一个变量）；框尺寸按文字块四周各留 30px 气口重算，臂长取框短边的 25~30%、描边宽取舞台高的 0.7%；节奏在 `CONFIG`，能量档只调 `brIn` 与 `brTravel`（两者要一起动：位移大就该慢一点）；`linesAt` 是**手感常量**（框先立住的那 0.22s），换尺寸换语速都不要动；`hold` 按标题字数给（每字约 0.13s）。竖屏把框放在上三分之一、宽度取画幅 80%，臂长按新的框短边重算。
- 底色要求：白底即可。深底同样成立（角框换成深底模式的强调色 `#2997ff` 系，标题反白）。唯一约束是**底不能有高频细节**——L 角框只有两条 4px 的线，压在花底上会被吃掉，那种场合要么加粗到 6px 要么先垫一层浅底板。

## 落位自检（2026-09-05 用户定版，选卡时抄进 SHOTBOOK 该镜自检列）
- **框必须套住字**：先量标题两行的实测包围盒（`getBoundingClientRect`），左上 L 的内角 = 包围盒左上外扩 (24, 20)，右下 L 的内角 = 包围盒右下外扩 (24, 20)；两臂等长 54，4px 描边。
- 实测反例（2026-09-05 用户抓出）：左上角框离首字 80px、右下角框压到末字下方——框与字各摆各的，"框选"语义归零。
- 实现后抽定妆帧核四个角点，任一偏差 **> 8px 返工**（`references/layout.md` §3）；标题左边缘还要吸附栏线（layout.md §1）。

<!-- ===== /file: video-talkcraft/references/cards/corner-bracket-frame.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/count-badge-title.md ===== -->

---
name: count-badge-title
标题: 数字重音标题
优先级: P1
代码: template/cards/count-badge-title.tsx
一句话: 数字「3」先单独从 1.6 倍缩到位并在落定那刻换成强调色，紧接着「个方法」被它从右缘 clip 推出来，第二行错峰 0.1s 淡入上浮，收尾数字再补一记 5 帧 punch
适用: 口播开场承诺条数——"三个方法""五个坑""两件事"；章节内的分点预告；需要观众记住"有几条"的每一次（列表卡之前的那一屏）
时长: 起手静置 0.4s → 数字入场 0.3s（落定换色）→「个方法」0.22s 被带出 → 第二行错峰 0.1s 后 0.28s 淡入 → 间隔 0.35s 后数字 punch 5 帧 → 定格 1.7s；共约 3.3s
能量: 中
类别: 字幕花字
输入: 文, 人(可选)
语义: 钩子, 数据, 列举, 标题
素材形态: 无
位置: 开场
props: hostSrc
---

## 意图
"三个方法解决问题"这句话里，真正的信息只有一个字：**3**。观众记不住"方法"两个字，
但会记住"有三条，我得听完"。可绝大多数标题动效把这七个字当成一块整体淡入——
七个字一样重，那个"3"就白给了，观众听完只剩一句模糊的"他讲了几个方法"。

本卡做的事是把**数字变成主语**：它先到、单独到、比其余字大一倍多、落定时还单独换色。
其余的字不是"和它一起出现"，而是**被它带出来的**——「个方法」从数字右缘被推着揭示，
第二行才跟上。这条时序把一句话的语法关系直接翻译成了画面的先后关系。

它和本库现有两张重音卡分工清楚：`keyword-pop-highlight` 是**句子里砸一个词**
（正文先在、关键词后炸、带色块底和震屏，能量高、服务字幕）；
`type-contrast-emphasis` 是**靠字体/字重的静态对比**分出主次（没有时序，是版式）；
本卡是**标题级的数字重音**——它不在句子里，它就是这一屏；靠的是"先后"而不是"砸"。

命门两条：① **数字必须先到且单独到**。三段同时淡入就没有"3 个"这个重音，
读作一个普通两行标题（本卡等于不存在）。② **换色发生在落定那一帧，不在飞行途中**。
飞着变色读作"一路在闪"；到位才亮才是"这个数就是它了"的确认。

## 动效核心
- **三段严格分先后，每段一个单一动作**：
  - ① 数字：`scale 1.6 → 1` + `opacity 0 → 1`，`0.30s power3.out`。
    **只有 scale + opacity，不带任何位移**——重音是"压下来"不是"飞进来"；
    `transform-origin: 50% 72%`（重心偏下，缩到位时数字不往上飘）
  - ② 落定换色：`color: ink → accent`，`0.14s power1.out`，起点 = 落定时刻 − `0.07s`
    （提前半个时长起，让"到位"与"变色"在观感上是同一帧）
  - ③ 量词：`clip-path: inset(0 100% 0 0) → inset(0 0% 0 0)` + `x −8 → 0`，
    `0.22s power3.out`，两条**同曲线同时长** ⇒ 读作一件事（被拖出来），
    而不是"揭示"和"位移"两个动效；起点 = 落定 + `0.02s`（几乎贴着，才读作"被带出来"）
  - ④ 第二行：`opacity 0 → 1` + `y 6 → 0`，`0.28s power3.out`，错峰 `0.10s`。
    普通淡入上浮——它是补足语义的，**不许抢重音**
  - ⑤ 收尾 punch：`scale 1 → 1.06`（`0.04s`）→ `1`（`0.13s power3.out`），共 5 帧 @30fps，
    落在第二行落定后 `0.35s`（对齐口播念到重音的那一下）
- **层级只有两级**：数字 `138px / 700`，其余全部 `62px / 600`。
  「个方法」与第二行**同一字阶**是刻意的——三级字号会把"其余的字"内部也分出主次，
  重音就散了（design-language §2：一屏文字层级 ≤3 级，本卡只用 2 级）
- **`align-items: baseline`**：数字与量词共基线。数字再大也不许把行推歪；
  用 `center` 对齐会让量词浮在数字中腰，读作两个不相干的元素
- **`font-variant-numeric: tabular-nums`**：数字不跳宽（换成两位数 `12` 时排版不塌）
- **700 字重全片只给这一处**（design-language §2：700 = 砸字档，留给极特殊时刻）
- **强调色只上在数字上**，量词与第二行保持墨色 `#1d1d1f`

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `numScale` | 1.6 | 数字入场起始缩放，本卡的能量旋钮；1.4~1.8 是"压下来"的档；>2 读作糊到镜头上（喜剧向），<1.25 缩到位的行程太短、看不出这是个重音 |
| `numIn` | 0.30s | 数字入场耗时；<0.2s 读作硬现（少了"压下来"的过程），>0.45s 数字在半空停太久、口播已经念完"三个方法"了 |
| `hueDur` | 0.14s | 落定换色耗时；**起点必须是落定时刻 − hueDur/2**。>0.3s 读作慢慢染色（丢掉"确认"的干脆），0 则硬切换色（可用，但少一点亮起的质感） |
| `restLag` | 0.02s | 量词相对数字落定的滞后，**本卡第一命门的下半句**；接近 0 才读作被数字带出来；>0.15s 变成"数字先出、量词再出"两个动效 |
| `restIn` | 0.22s | 量词揭示耗时；必须与 `x` 补偿同时长同曲线。>0.35s 读作字被慢慢刷出来（那是 `highlighter-sweep` 的语言） |
| `restX` | −8px | 量词起始横向偏移；**负值**（从数字那侧被拖出来）；0 则只有 clip 揭示（缺一点"被带"的惯性），<−20 读作从数字里飞出来 |
| `l2Lag` | 0.10s | 第二行错峰，**本卡第二命门的量**；>0.25s 读作两个独立动效（上下两行没关系了），0 则与量词同时出、抢掉"被带出来"那一拍 |
| `l2Rise` | 6px | 第二行上浮量；>16px 位移感盖过"跟上"这个语义（第二行不该有自己的方向） |
| `punchGap` | 0.35s | 第二行落定到数字补拍的间隔；实拍里按口播重音落点调（这是唯一需要跟音频对齐的参数） |
| `punchScale` | 1.06 | 补拍幅度；1.04~1.08（design-language §4 punch token）；>1.15 读作第二次入场，观众以为动效重播了 |
| 数字位数 | 1~2 位 | 3 位以上（"100个方法"）数字宽度会挤掉量词，`numScale` 要降到 1.35 并把字号收到 110px |

## 已知坑
- 三段同时淡入——"3 个"这个重音消失，读作一个普通两行标题，本卡等于没做。
- 数字入场带位移（从下飞上来 / 从左推入）——重音变成入场，"数字是主语"这层语义被方向感盖掉；只许 scale + opacity。
- 飞行途中就在变色——读作"一路在闪"；到位才亮才是确认。换色起点必须贴着落定帧。
- 量词与数字同帧出现——它就不是"被带出来"的了，两者读作一起淡入的两块字。
- 量词的 clip 与 x 用两条不同曲线/时长——慢放下能看出字先被刷出来、再单独滑一下，割裂。
- 量词字号做成第三级（比第二行小一点）——一屏三级字阶，"其余的字"内部又分了主次，重音散掉。
- 数字与量词用 `align-items: center`——量词浮在数字中腰，读作两个不相干的元素；必须共 baseline。
- 数字不加 `tabular-nums`——换成两位数后排版跳宽，量词的落位跟着变。
- 收尾 punch 做到 1.2 倍——读作动效重播了一次，观众会以为漏看了什么；punch 是"顿一下"不是"再来一次"。
- 强调色顺手也给量词或第二行上一点——一屏只有一个"看这里"（design-language §1 红线），数字的重音立刻被稀释。
- 用 700 字重给整屏——700 是本卡给数字的专属重量，全屏 700 就没有轻重了。
- 换成"三"这个汉字数字——汉字数字宽高与其余汉字一样，`numScale` 撑再大也读作"一个大字"，丢掉"数量"这个语义；本卡要阿拉伯数字。

## 复用指引
- props：仅 `hostSrc`；数字 / 量词 / 第二行文案在 JSX 常量里（`.cb-num / .cb-rest / .cb-l2`），强调色在 `CONFIG.accent`，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/count-badge-title.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/count-badge-title/index.html。换文案改三处文本：`.cb-num`（1~2 位阿拉伯数字）、
  `.cb-rest`（量词，2~4 字）、`.cb-l2`（第二行，3~6 字）。
  换强调色只改 `CONFIG.accent` 一个值。能量只调 `numScale`；
  节奏只调 `l2Lag` 与 `punchGap`（前者是结构、后者跟音频）。
  换字号时数字与其余字的**比例要保持约 2.2:1**（138:62），单独放大数字会压掉行距。
  落位改 `.cb-text` 的 `left/top`（demo 让开右侧 47% 的主持人列）。
- Remotion 移植要点：五段各一组 `interpolate`，共用绝对帧号（30fps：起手 12 帧、
  数字入场 9 帧、量词 7 帧、第二行 8 帧、punch 5 帧）：
  数字 `scale = interpolate(frame, [12, 21], [1.6, 1], {easing: Easing.out(Easing.cubic)})`；
  换色用 `interpolateColors(frame, [19, 23], [ink, accent])`（**帧区间要跨过落定帧 21**，
  这就是"提前 hueDur/2 起"）；
  量词 `clipPath = \`inset(0 ${interpolate(frame,[22,29],[100,0])}% 0 0)\``（模板字符串拼百分比，
  Remotion 里 clip-path 不能用 spring 直接插值对象）；
  punch 用两段拼：`frame < 45 ? interpolate(frame,[44,45],[1,1.06]) : interpolate(frame,[45,49],[1.06,1],{easing:Easing.out(Easing.cubic)})`。
  全部 `extrapolateLeft/Right: 'clamp'`。
- 剪辑软件对应物：剪映/CapCut——**三个独立文本层**（数字 / 量词 / 第二行），
  数字层套"入场：放大"（把"动画时长"拉到 0.3s）；换色剪映做不到"落定那一帧换"，
  取舍做法是**两个数字层叠着**（墨色的那层在落定帧硬切消失、强调色那层同帧出现，
  0 帧交接肉眼就是"到位变色"）；量词层套"入场：向右擦除" 0.22s 并把 In 点放在数字层结束处；
  punch 用"关键帧·缩放" 100→106→100 三个点。
  AE——一个文本层用 `Animator`（Scale + Opacity，Range Selector 全选）做数字入场，
  颜色用 `Fill` 效果打两个关键帧（19f / 23f）；量词用 `Linear Wipe`（Transition Completion 100→0，
  Wipe Angle 90°）+ `Position` 两键**同一段时间、同一 Easy Ease**；
  punch 直接在 `Scale` 上打 100 / 106 / 100 三键（间距 1f / 4f）。
- 与本库同类卡的分工：`keyword-pop-highlight` = **句子里砸一个词**（正文先在、关键词后炸、
  色块底 + 震屏，高能量、服务字幕）；`type-contrast-emphasis` = **静态的字体/字重对比**
  （没有时序，是版式手段）；`number-counter` = **滚动计数**（数字有过程感，讲"涨到了多少"）；
  **本卡 = 标题级的数字重音**（数字是主语，靠"先后"而不是"砸"，讲"有几条"）。
  要讲"从 0 涨到 67%"用 `number-counter`；要讲"有三个方法"用本卡——
  前者的数字是结果，后者的数字是**目录**。

## 动效范围
- 属于本卡的：三段严格分先后这条时序纪律（数字单独到 → 量词被带出 → 第二行跟上）；数字入场只用 `scale 1.6→1` + `opacity`、**拒绝任何位移**；换色起点 = 落定帧 − `hueDur/2` 这个"到位才亮"的对齐；量词的 `clip-path` 与 `x` 补偿同曲线同时长（读作一件事）且 `restLag ≈ 0`；第二行错峰 `0.10s` 的量级；收尾 5 帧 `1.06` punch 的幅度与"落在第二行之后"的位置；数字与其余字约 2.2:1 的字号比 + 只有两级字阶；`align-items: baseline` 共基线；`transform-origin: 50% 72%`；`tabular-nums`；强调色只上在数字上。
- 不属于本卡的：demo 那句「3 个方法 / 解决问题」的具体文案、`#7A5AF8` 这个具体强调色（参考图同色系任一个都成立）、138px/62px 这两个具体字号（比例才是本体）、700/600 这组字重的绝对值、标题落在左侧白区这个落位（居中、下三分之一都成立）、白底舞台、以及右侧那列数字人主持人占位。
- 迁移接口：内容入口 = `.cb-num`（1~2 位阿拉伯数字）/`.cb-rest`/`.cb-l2` 三处文本；配色入口 = `CONFIG.accent` 一个值；能量入口 = `numScale`；节奏入口 = `l2Lag`（结构）与 `punchGap`（跟音频重音）；换字号时保持数字:其余 ≈ 2.2:1，`l2Rise` 按第二行字号的 10% 给。竖屏：把「个方法」换到第二行、第二行下移成第三行（竖屏行宽放不下 `138px 数字 + 4 字`），三段时序完全不变。数字位数 ≥3 时 `numScale` 降到 1.35。
- 底色要求：白底即可。深底把量词与第二行反白、强调色换成 design-language 深底档（如紫 `#9B87FF`）即可，时序不动。唯一约束是**数字落定时的换色必须在底上有足够反差**——强调色与底色的对比低于 3:1 时"亮起"这一拍读不出来，换色就白做了（此时改为换字重或加 accent 下划线）。

<!-- ===== /file: video-talkcraft/references/cards/count-badge-title.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/countdown-arc-scatter.md ===== -->

---
name: countdown-arc-scatter
标题: 数字弧落标题
一句话: 一串相邻递减的数字 11 / 10 / 9 … 5 / 4 / 3 切向挂在半径 150 的弧上，整盘从 96° 扫回 0°（0.57s，power2.out 急停），位置角超 ±70° 的数字用角度算透明度"转进视野"；停稳那一刻被选中的"5"正在弧顶，随即 0.3s 平移到标题首字符位并同步回正，其余数字原地 blur 3 淡出不位移，"分钟 / 搭好 / 创作系统"逐词解糊，末词 1.75s 染强调色；落定后整幕静止到 4.6s 同收
适用: 数字本身是悬念的标题——时长承诺（"5 分钟搭好创作系统"）、数量揭晓（"3 个原则"）、倒计时语义的开场、需要"仪表盘"语汇的短镜；数字先从一串候选里被"扫停"再落位，比数字直接落更有揭晓感
时长: 5.0s（0.3 起扫 0.57s → 0.85 其余散去 / 0.87 选中数落位 → 0.95 / 1.10 / 1.25 三词解糊 → 1.75 末词染色 → 4.6 同收 0.4s）；成片把"扫停"对到口播念出数字的字锚
能量: 高
类别: 字幕花字
输入: 文
语义: 钩子, 数据
素材形态: 无
位置: 开场
props: numbers, pick, words, accent
优先级: P2
代码: template/cards/countdown-arc-scatter.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 纯文字卡；人在场时整组放人物对侧半幅（layout §4） | ✗ | ✗ |

作用于标题层，不作用于底部跟读字幕（素排铁律）。

## 常用场景
1. 时长承诺："5 分钟搭好创作系统"——"5"从 11…3 里扫停落位（demo 演的）
2. 数量揭晓："3 个原则 / 7 个习惯"——数字串按目标数上下各留几格
3. 倒计时语义的开场："10 秒告诉你…"
4. 需要"仪表盘"语汇的数据短镜（评分 / 排名的揭晓）

## 意图
标题里带数字时，`count-badge-title` 让数字先落再推出后半句——数字是**给定**的；本卡让数字从一串候选里被**扫停**出来——数字是**被选中**的，多一层"为什么是 5"的揭晓感，适合数字本身是口播悬念的场合。表盘只在开头出现一拍，落定后整幕静止，不违反运动减法。做对五条：
1. **扫动 power2.out 急停**：减速急停是"到位"的全部力道；改 inOut 就成了缓缓停下，没有仪表的干脆。
2. **用角度算透明度**：|位置角| > 70° 全透、70→48° 渐显——数字是"转进视野"的，不用遮罩（遮罩硬边会暴露"一张贴图在转"）。
3. **选中数落位紧接扫停、不留静置**：留了就断成两个动作；落位与回正同一条曲线（power2.inOut）。
4. **其余数字原地失焦散去、不位移**：位移会跟选中数的平移抢戏；且比落位早 0.02 起手先让路。
5. **刻度 0.35 倍差速**：刻度跟转比盘慢，造出"盘面 + 指针"的层次；同速读作一整块贴图在转。

## 动效核心
- **几何**（960×540）：枢轴零尺寸锚点 @ (480, 318)；数字 52px / 600 / tabular-nums / 字距 −1 墨色，第 i 个在位置角 `pa = (i − pickIdx)·24° + rot`，坐标 `(sin pa·150, −cos pa·150)`，自身 `rotate(pa)`（切向排布，像刻在盘面上）；15 根刻度（3×22，`#c9c9cf`）在 R+38 圈上，位置角 `(k−7)·12° + rot·0.35`。标题 `.cas-ttl` 居中于 (480, 250)，52px / 600、词距 16，首位是宽度 = 选中数真实宽度的隐形槽。
- **扫动**：`rot = lerp(96, 0, tw(t, 0.3, 0.57, power2.out))`；数字透明度 `clamp01((70 − |pa|)/22)`；刻度透明度 `clamp01((80 − |pa|)/20)·0.8`。
- **散去**：0.85s 起 0.3s `power1.in`，非选中数 opacity ×(1−out)、`blur(out·3px)`，位置不变；刻度同乘 (1−out)。
- **落位**：0.87s 起 0.3s `power2.inOut`，选中数 `(x, y)` 从弧上位置 lerp 到隐形槽中心（相对枢轴 `(slotW/2 − ttlW/2, −68)`），自身旋转 `pa·(1−hand)` 回正，opacity `max(角度透明度, hand)`。
- **标题**：三词各 0.35s `power2.out`：opacity 0→1、blur 6→0，起点 0.95 / 1.10 / 1.25（窗重叠约 0.2）；末词 1.75s 起 0.25s 颜色从墨色线性插到强调色。
- **退场**：4.6s 枢轴 + 标题 opacity→0 0.4s `power2.in`，5.0s 结束。落定即静置，无 idle。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 数字串 | 相邻递减 9 个，选中数在第 7 位（前 6 个扫过、后 2 个预留） | 相邻数字读作倒数 / 量程；选中数位置决定扫过几格——前面留 ≥4 个才有"扫过一串"的感觉 |
| `step` | 24° | <18° 数字挤在一起，>30° 一次只看见 3 个数 |
| `R` | 150px | <100 挤成小圈，>220 弧近乎直线、表盘感消失 |
| `sweepFrom` / `sweep` | 96° / 0.57s power2.out | 96° ≈ 扫过 4 格；急停是唯一"到位"信号，改 inOut 就没有仪表的干脆 |
| `visAngle` / `visFeather` | 70° / 22° | 渐变宽约一格；调大成 40 数字半透着进出、糊；0 就是硬切出现 |
| `handAt` / `handDur` | 0.87 / 0.3s power2.inOut | 紧接扫停（0.87 = 0.3 + 0.57）；中间留静置就断成两个动作 |
| `outAt` | 0.85（比落位早 0.02） | 先让路；晚于落位会读作两组东西同时在动 |
| `tickRatio` | 0.35 | 差速是"盘 vs 指针"的层次来源；1.0 读作一整块贴图 |
| `wordStagger` / `wordDur` | 0.15 / 0.35s | 窗重叠约 0.2 才读作"一句话"；排队读作三个词各自出场 |
| `accentAt` | 1.75s | 全卡唯一颜色事件，落在最后一个词上就是句子的落点 |

## 已知坑
- 扫动用 inOut 缓动——缓缓停下，没有仪表的干脆；命门违例。
- 数字用遮罩裁而不是按角度算透明度——硬边暴露"贴图在转"。
- 选中数落位前留静置——断成"停盘"和"飞字"两个动作。
- 其余数字带位移散去——跟选中数的平移抢戏，观众不知道看哪个。
- 刻度与数字同速——层次消失，读作一整块在转。
- 数字串不等距 / 不相邻（母本的 45 / 35 / 28…）——用户 2026-09-06 定版：用相邻递减数字，读作倒数不是量程。
- 标题三词排队出场（窗不重叠）——读作三个词各自登场，不是一句话。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/countdown-arc-scatter.tsx——`numbers / pick / words / accent` 四个 prop；durationInFrames 162；标题宽与隐形槽宽用 `useLayoutEffect + delayRender` 量一次（选中数的落点由此反推）。
- HTML/GSAP：demos/countdown-arc-scatter/index.html——改 `NUMBERS / PICK / WORDS / ACCENT` 与 `CONFIG`；`apply()` 由三个代理量（rot / hand / out）纯函数地摆全部数字与刻度。
- 母本：video-shotcraft `countdown-arc-scatter`（数字串从不等距量程改为相邻递减，其余原样）。
- 与 `count-badge-title` 的分工：那张数字是给定的（1.6× 缩到位 + 推出后半句），用于数字不是悬念的普通计数标题；本卡数字是被扫停选中的，用于数字本身是揭晓点的标题。一支片两张都用时错开段落。
- 剪辑软件对应物：剪映无等价物；AE 用 Null 做枢轴、9 个文字图层父子级绑定 + 旋转关键帧（Easy Ease Out 加大 influence），透明度用表达式按 `Math.abs(位置角)` 算；选中数单独一层做位置关键帧。
- 与 layout.md 的接口：标题包围盒居中于 (480, 250)（§4，偏差 ≤48）；52px ≥ title 档下限（§5）；表盘扫动期间数字最高点 y ≈ 168、刻度 ≈ 130，不入安全边。

## 动效范围
- 属于本卡的：弧上切向排布 + 整盘扫回急停；角度算透明度的"转进视野"；选中数落位 + 回正同曲线；其余原地失焦散去；刻度差速；标题逐词解糊 + 末词染色。
- 不属于本卡的：具体数字串与文案、强调色色值、白底舞台。
- 迁移接口：`numbers / pick / words / accent`；1080p 输出字号 ×2（104）、R 300、step 不变；"扫停"时刻按口播念出数字的字锚摆（`sweepAt = 字锚 − 0.57`）。
- 底色要求：白底 / 羊皮纸底成立；深底时数字与刻度反白、刻度 `#5a5a60`。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- 定妆帧三张：扫动中（如 0.6s）弧上可见 5~6 个数字、两端渐隐；扫停瞬间（0.87s）选中数在弧顶正上方 (480, 168)；落定后（如 2.4s）选中数与后续词基线对齐、词距 16。
- 标题包围盒水平居中偏差 ≤48，中心 y ≈ 250；选中数与隐形槽中心重合偏差 ≤4px。
- 落定后（≥2.0s）至少 60 帧画面静止（刻度、数字、标题无一在动）。
- 人物在场时整组放人物对侧半幅中心（x = 240 或 720@960），枢轴同步平移。

<!-- ===== /file: video-talkcraft/references/cards/countdown-arc-scatter.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/crash-zoom-punch.md ===== -->

---
name: crash-zoom-punch
标题: 急推特写
一句话: 全景静置 1s 让观众看清整页，然后 6 帧 ease-in 急推到截图里的目标文字块（zoom 1→2.3，相机中心同步收敛到目标中心），过冲后 5 帧回收 4.5% 到 2.2 落定；急推那 6 帧叠一记短促 blur 当运动模糊，之后画面钉死——一次性的重音"就是这一行"
适用: 口播说"就是这一行 / 看这里"时把观众视线一拍按到截图的某一行、某个单元格、某句话上（账单 / 设置 / 条款 / 聊天记录 / 表格）；一支片 ≤2 次。输入是图片（含 B-roll 截帧），人物不参与
时长: 4.4s（0～1.0 全景静置 → 1.0 急推 6 帧 → 1.2 回收 5 帧落定 → 钉死 → 4.0 退场 0.4s）；成片 hold 与落定后的静置按口播句长伸缩，急推那 11 帧不变
能量: 高
类别: 强调标注
输入: 图, 截图
语义: 强调, 例证
素材形态: 横屏
位置: 中段
props: src, target, label, sub
优先级: P1
代码: template/cards/crash-zoom-punch.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 人物不参与（动讲者景别是另一件事，本卡只推素材） | △ 先截帧成图再推（急推是对静止证据的一拍） | ✓（默认输入）截图 / 表格 / 聊天记录 / 文档 |

截图铺满 800×396 白卡（1080p 下 1600×792），目标 bbox（舞台坐标）由实测反推后经 `target` 注入——急推中心就是它的中心。

## 常用场景
1. "就是这一行"：账单 / 设置 / 条款截图里按住关键行（demo 演的：自动续费）
2. 聊天记录截图里急推到那句话
3. 数据表格里急推到异常单元格
4. B-roll 实拍里急推到某个物件（先截帧再推）

## 意图
口播要指出截图里的"这一处"时，库里有四条路：`slow-push-in` 整镜极缓推（没有"这一处"的指向）、`cursor-locked-zoom` 光标当导游（多一个角色）、`magnifier-detail` / `pip-zoom-box` 另开放大窗（保留全景、多一层框）。急推是第五条：**整个相机一拍撞上去**，"看这里"的指令感最强，代价是全景消失——所以先给 1s 全景让观众建立位置，再撞。它是**切**不是 hold 期运动，与"相机只做极缓推拉"的纪律管的不是同一段时间。做对四条：
1. **急推 ≤8 帧**：>10 帧就是普通推近，冲击感消失。
2. **目标中心钉死**：推进与回收共用同一 (px, py)，三个构图是同一个镜头的一拍；每档重新构图就是三个镜头。
3. **过冲后回收 3～6%**：无过冲读作滑到即停，>6% 读作弹簧玩具。
4. **落定即钉死**：之后一切静止，让观众读；一支片 ≤2 次，连用即廉价。

## 动效核心
- **几何**（960×540）：舞台底 #f5f5f7（羊皮纸档，让白卡有边界）；截图卡 800×396 @ (80, 48)（卡底 444，不进字幕带），白底 + 1px 发丝线 + 圆角 14；demo 假设置页：60px 标题栏 + 5 行 64px 设置行，每行三列「图标列 28..248 | 标签列（卡内 x=248 起、宽 216）| 开关」；目标 = 第 3 行"自动续费 / 下次扣款…"文字块，实测 bbox (328, 236, 216×64)（舞台坐标），中心 (436, 268)，离卡左边 356px ≥ 218。**目标是行内的文字块，不是整行**——整行的中心是空白；**标签列放在卡中列**是为了落定后不露舞台底（首版目标在卡左列 x=108，2.2× 后左侧露出 176px 舞台色带，评审判例）。
- **相机变换**（`.cam` 包住截图，`transform-origin 0 0`）：`camTo(z, px, py)` = `x = W/2 − z·px, y = H/2 − z·py`，再钳制 `x ∈ [W − W·z, 0]`、`y ∈ [H − H·z, 0]` 不露舞台边。
- **急推**：1.0s 起 0.2s（6 帧）`power3.in`，scale 1 → 2.3、x/y 同步 0 → camTo(2.3) —— 一条 tween 同时改三个量，中心才不漂。
- **运动模糊**：与急推同起，`blur 0→5px` 0.12s `power2.in`，再 0.15s 落回 0——只包急推段，落定段清晰。
- **回收**：1.2s 起 0.17s（5 帧）`power2.out`，scale 2.3 → 2.2、x/y → camTo(2.2)；之后钉死。
- **退场**：4.0s opacity→0 0.4s `power2.in`，4.4s 结束。可选**撞停款**（未做默认）：不回收，到位帧起机位抖 `14px·e^(−t/1.8f)` 6 帧收干——与运动减法相冲，成片慎用。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `hold` 全景静置 | 1.0s | 观众建立"整页在哪"的时间；<0.6 观众不知道推到了哪里，>2 等得久 |
| `punch` 急推时长 | 0.2s（6 帧） | 4～8 帧；>10 帧读作普通推近，冲击感消失 |
| `zoom` 过冲峰值 | 2.3 | 终点构图以目标占画面 60～75% 为准；整行宽目标 1.8～2.2、单元格 2.6～3.0 |
| `settle` 落定倍率 | 2.2（回收 4.5%） | 3～6%；过大读作弹簧玩具，无回收读作滑到即停 |
| `settleDur` 回收时长 | 0.17s（5 帧） | >8 帧读作二次推近 |
| `blur` 运动模糊峰值 | 5px | 只包急推段；>8 落定帧还糊，0 则急推像跳切 |
| 急推缓动 | `power3.in` | 急加速是"撞"的来源；ease-out 就成了普通推近 |
| 目标 bbox | 实测反推 | 目标必须是可读内容块（文字 / 单元格），不是整行——整行中心多半是空白 |

## 已知坑
- 目标取整行中心——推进后看到的是行中间的空白（首版判例：目标 = `.tg` 整行，2.6× 后画面里只剩"9 / 月"）；目标要取文字块。
- 急推超过 10 帧——变成普通推近，"撞"的感觉没了。
- 三个构图各自居中——是三个镜头不是一拍；推进与回收必须共用同一 origin。
- 目标离截图边太近——camTo 只钳舞台边不钳卡片边，推进后会露出舞台底色；目标离卡边 ≥ 卡宽 × (1 − 1/zoom) / 2 才不露。
- 落定后继续缓推——重音之后又叠运动，读作没停稳；落定即钉死。
- 一支片连用三次以上——每次都撞，第三次起观众麻木；≤2 次。
- 撞停震屏当默认——震屏是持续几帧的抖动，与运动减法冲突；只在用户点名要"重量感"时开。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/crash-zoom-punch.tsx——props `src` 真截图、`target={x,y,w,h}` 目标 bbox（舞台坐标）、`label / sub`（仅无 src 时假设置页的目标行文案）；durationInFrames 144；全景时长改 `CONFIG.hold`，句长改 `exitAt / end`；`zoom / settle` 按目标大小配。`camTo` 已内联。
- HTML/GSAP：demos/crash-zoom-punch/index.html——`.shot` 里换 `<img>` 即真截图，目标块给 `.tg .k` 两个类（几何照旧由 offset 反推）；`CONFIG` 改节奏。
- 母本：video-shotcraft `crash-zoom-punch` 回弹款（产品片里推功能卡；本卡对象换成口播的截图证据局部，CameraMotionBlur 用短促 blur 近似，撞停款留作可选）。
- 剪辑软件对应物：剪映"缩放"关键帧 6 帧 ease-in + 5 帧回弹（或直接用"急推"转场特效）；PR 位置 / 缩放贝塞尔关键帧 + 方向模糊 6 帧；AE 摄像机 Zoom 关键帧 + CC Force Motion Blur。
- 与 layout.md 的接口：截图卡 (80,48)–(880,444) 离画幅边 80 / 48（§1 安全边 48）、卡底 444 不进字幕带 y≥450（§6）；急推后目标文字块落画面正中（§4 单主体落中线）；目标 bbox 实测反推（§3）。

## 动效范围
- 属于本卡的：1s 全景静置；6 帧 power3.in 急推 + 中心同步收敛；急推段短促 blur；5 帧回收 3～6%；落定钉死；camTo 钳制。
- 不属于本卡的：CSS 假设置页、目标行文案、羊皮纸底、白卡样式。
- 迁移接口：`src / target`；`zoom / settle` 按目标尺寸；1080p 输出 blur 5→10px、其余是比例量不变；深底舞台时截图卡投影加重。
- 底色要求：舞台底与截图卡要有阶差（demo 用 #f5f5f7 + 白卡），否则全景阶段看不出卡的边界；深底同样成立。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- 目标 bbox 由截图实测反推（DOM offset / 图片标注），取**可读内容块**不取整行；中心 (px, py) 写进 SHOTBOOK。
- 定妆帧：急推落定帧（`shot-at 1.4`）目标文字块中心与画面中心 (480, 270) 偏差 ≤ 16px；目标占画面 60～75%。
- 全景帧（`shot-at 0.8`）截图卡完整在画面内、离边 ≥ 48、卡底 ≤ 444（字幕带外）。
- 落定后到退场前任意两帧 transform 相同（真钉死）。
- 目标中心离截图卡边 ≥ 卡宽 × (1 − 1/settle) / 2（demo：800 × 0.545 / 2 = 218px；本例 356）否则推进后露出舞台底——目标在卡左列时把它挪到中列，不是缩 zoom。
- 同一支片 ≤2 次；与 `slow-push-in` 同镜互斥（一个镜头只有一个相机动作）。

<!-- ===== /file: video-talkcraft/references/cards/crash-zoom-punch.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/cursor-actor-demo.md ===== -->

---
name: cursor-actor-demo
标题: 光标演员演示
优先级: P0
代码: template/cards/cursor-actor-demo.tsx
一句话: 一枚超常规尺寸的系统光标在界面（tsx 为 CSS/SVG 线框假 UI，控件要能响应）上"移动-悬停-点击"，每落到一个目标元素就即时响应（hover 底色加深 / 开关滑块滑过去 / 缩略图从光标处 pop-in），一个动作对齐一个口播词——光标是替观众操作的演员，不是鼠标轨迹录屏
适用: 口播演示工具/软件怎么用的段落——"你就点这里""把图拖进来""这两个开关先打开"；工具测评、AI 产品讲解、教程类口播的标配呈现方式。输入是**可重建的界面**（活控件），不是静态截图——截图只能当底，要响应的元素得在其上重画
时长: 起手静置约 0.45s 等口播开口 → 每个动作 = 移动 0.3~0.6s + 悬停 0.2s + 按压 0.09s + 元素响应 0.3s ≈ 1s/动作；3~4 个动作一段共 4~6s
能量: 中
类别: 素材呈现
输入: 界, 人(可选)
语义: 过程演示, 步骤
素材形态: 界面
位置: 中段
props: hostSrc
---

## 意图
口播讲"这个工具怎么用"时，真实录屏的光标只有 12px、轨迹又直又抖，观众在手机上根本看不见操作
落在哪；纯截图切换又丢掉了"是我在操作"的因果感。光标演员把鼠标当成一个**放大的演员**：
它走到哪、停多久、点什么，都是导演过的，观众的视线被它带着走，而元素的即时响应替口播完成了
"你看，点完就变了"这句话。命门：**光标要够大**（放大到真实尺寸 2~3 倍，缩略图尺寸下仍认得出是箭头）、
**每个动作必须有响应**（点了没反应等于演砸，观众读作静态图配了个假光标）、
**一动作一口播词**（光标动作是语音的节拍器，密了像演示录屏、疏了像卡顿）。

## 动效核心
- **光标**：深墨实心 + 白描边 + 柔投影的箭头（SVG，30×45px @960 舞台 ≈ 真实尺寸 2.5 倍），
  `transform-origin: 0% 0%` 锚在箭头尖——按压微缩时尖端不移位。
  造型走**圆角贝塞尔轮廓**（尖端锐、腰身直、肩与尾跟倒角 0.4~0.9），不是尖锐折线多边形；
  实现用**同一条 path 描两遍**：先 `stroke-width: 2.05` 的白色描边层（`stroke-linejoin/linecap: round`）、
  再压深墨 `#1d1d1f` 实心层，得到粗细均匀的白轮廓（比给单层 path 加 stroke 更干净，不会在锐角处爆尖）；
  外加 `filter: drop-shadow(0 2px 5px rgba(0,0,0,.28))` 让光标浮在 UI 之上。
  `overflow: visible` 必须开——白描边与投影要能溢出 viewBox
- **移动**：x / y 分开插值、用不同缓动（x `power2.inOut` + y `sine.inOut`），
  合成出来的轨迹天然是弧线；单段 0.3~0.6s（跨区域 0.5~0.6s，相邻目标 0.3~0.4s）。
  **绝不做直线匀速平移**——那是图层在被推，不是手在动
- **悬停**：到位后停 0.2s 才点（"要点这里"要给观众看见）；同时目标出 hover 态——
  行底色 `#f0f0f0` 淡入 0.16s / 边框加深，`power2.out`
- **按压**：光标 `scale 1→0.9→1`，各 0.09s；同帧目标元素 `scale 1→0.94→1`（回弹段稍长 1.6×）
- **按压涟漪**：从箭头尖为圆心弹出一圈圆环，`scale 0.3→1.6` + `opacity 1→0`，0.35s
  （扩散 `power2.out` / 淡出 `power2.in`）——比按压本身长，按完还在扩，"点击"这个动作才有确认感。
  圆环用与光标同一套 **深芯 + 白边**语言（`1.7px` 深环 + 内外各一道 `1.5px` 白 `box-shadow`）：
  涟漪常常正好扩过刚变深的开关轨道，纯深色环压上去会糊成一团。
  层级夹在 UI 与光标之间（`z-index` 29，光标 30）；圆心用负偏移（`left/top: -15px`，即 -半径）把
  元素中心对到 x/y 坐标，这样涟漪与光标可以共用同一组落点坐标
- **状态切换在"按下"那一刻就发生**（按压中点 ≈ 0.55×press 起算），不等抬手——
  等抬手会有一帧"点了没反应"的延迟感
- **三种响应语言**（按目标类型选一种，别混）：
  ① 开关：滑块 x 滑到轨另一端 0.28s `power2.out` + 轨道底色转深 + 滑块转白
  ② 按钮：底色/边框变深 + 按压微缩
  ③ 缩略图落位：从**光标位置**为原点 `scale 0.4→1` + 淡入 0.34s `power3.out`（`transform-origin` 对齐落点内的光标位置）
- **拖拽**：按住后被拖元素与光标共用同一条移动曲线（同起点同时长），拖速比空移慢
  （0.62s vs 0.52s——拖着东西走的手会更稳）；松手时拖影 0.12s 淡出、目标位 pop-in 同帧接上
- **离开即熄**：光标移开后 hover 高亮 0.2s 退回（响应只在光标停留期成立，不然满屏都是亮的行）
- **层级（三层，硬约束）**：底 UI < 响应高亮层（hover 底色，压在底 UI 之上、文字之下）< 光标（最顶）。
  光标被任何元素盖住一次，"演员"的身份立刻破产

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 光标尺寸 | 30×45px @960 宽（真实的 2.5 倍） | <20px 手机上看不见操作落点，>50px 箭头吃掉半个控件、盖住要被读的状态变化 |
| `moveLong` / `moveShort` | 0.52s / 0.34s | 跨区域 / 相邻目标的移动耗时；<0.2s 读作瞬移（丢掉"手在移动"的因果），>0.8s 口播已经说完下一句了 |
| `moveDrag` | 0.62s | 拖拽移动耗时，必须 > 空移；等于空移则"拖着重物"的手感消失 |
| `hoverHold` | 0.22s | 到位到点击之间的微停顿；0 则读作程序自动点击，>0.5s 观众以为光标卡住了 |
| `press` | 0.09s | 按压下压时长（抬手同值）；>0.2s 像慢动作按键，0 则完全没有"点下去"的实感 |
| `pressScale` | 0.9 | 光标按压微缩倍数；<0.8 像箭头被吸进屏幕，1.0 则点击瞬间无反馈 |
| `ripple` | 0.35s | 按压涟漪扩散耗时；<0.2s 一闪而过读不到"确认"，>0.6s 涟漪还没散下一个动作已经开始了 |
| `rippleFrom` / `rippleTo` | 0.3 / 1.6 | 涟漪起止倍数（基准直径 30px = 光标宽）；`rippleTo` >2 圆环比控件还大、抢戏，<1.2 扩不出去像个静止的点 |
| `hlIn` | 0.16s | hover 高亮淡入；>0.3s 高亮追不上光标（人到了色还没到） |
| `toggleSlide` | 0.28s | 开关滑块行程；<0.15s 看不清滑块滑过去（读作直接换图），>0.5s 开关变成主角抢戏 |
| `popIn` / `popFrom` | 0.34s / 0.4 | 缩略图落位弹入；`popFrom` >0.7 弹入幅度不够、看不出"从光标处长出来"，<0.2 像从一个点炸开 |
| 动作间隔 | ≈1s/动作 | 一动作一口播词；<0.6s 观众来不及看清响应，>1.5s 画面在等语音、节奏塌 |

## 已知坑
- 光标用真实系统尺寸——手机上一片糊，观众根本不知道点了哪里；本卡的第一条就是"放大"。
- 直线匀速平移到目标——读作图层被程序推着走。必须 x/y 分缓动出弧线 + 两端加减速。
- 光标一路加抖动噪声模拟手抖——不做（库内定版禁 line boil / 定格抖动）；"像手"靠弧线与加减速，不靠噪声。
- 点了目标没有任何响应，或响应延迟到抬手之后——一眼假；观众读作"截图上贴了个假光标"。
- hover 高亮一直亮着不退——满屏发亮的行，观众不知道光标此刻在哪。
- 光标被弹出的卡片/对话框盖住——层级破产，演员被道具挡在后面。
- 按压时光标缩放锚点在中心——箭头尖会跟着位移，"尖端咬住目标"的准确感丢了；必须锚 `0% 0%`。
- 光标画成尖锐折线多边形 + 细描边（系统箭头的直接摹写）——放大 2.5 倍后每个折角都在扎人，
  一眼"截图里抠出来的系统控件"；轮廓要走圆角贝塞尔、描边要粗到 2px 上下，放大了才立得住。
- 光标不加投影——箭头与 UI 贴在同一个平面上，"演员站在界面前面"的层次没有了；
  但投影别overdo（`blur` >8px、`y` >4px 就开始像贴纸浮起来）。
- 涟漪只有一个深色圆环——扩过开关刚变深的轨道时直接糊掉（涟漪与它撞色的概率极高，
  因为它总是在刚被点亮的控件上扩）；深环两侧各夹一道白就永远读得出。
- 涟漪的 SVG/元素忘了纳入重播复位段——重播第一帧残留着上一轮扩到最大的圆环。
- 一次动作里同时上三种响应（变色+滑动+pop-in 全来）——观众不知道该看哪个变化，一个目标一种响应语言。
- 动作排得比语音密（0.3s 点一下）——退化成加速录屏，节奏与讲述脱钩；光标是节拍器，节拍由词决定。
- 拖拽时被拖元素与光标不同步（各自一条曲线）——两个东西各走各的，"抓住了"的因果感断掉。

## 复用指引
- props：仅 `hostSrc`（角标主持人）；UI 是 CSS/SVG 线框、四个落点在 `POS` 常量（实测值）、动作时刻由 `CONFIG` 累加，换内容需改源码。要用真截图：在 `.ui-window` 里垫一张 `<Img>`（Remotion 自带）当底、把要响应的控件（开关 / 插槽）按截图位置重画在其上，并重量 `POS`；纯静态截图做不出滑块 / pop-in 响应。
- Remotion/tsx（skill 首选）：template/cards/cursor-actor-demo.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/cursor-actor-demo/index.html。换 UI 只改 `#stage` 内的灰阶线框结构（本卡的动作序列按选择器取目标：`.pref-row` 行 / `.tg` 开关 / `.thumb.pick` 缩略图 / `.slot` 落点）；目标点用运行时 `P(el, fx, fy)` 反算舞台坐标（换布局不用改任何数字，`fx/fy` 是元素内相对落点）；节奏全在顶部 `CONFIG`（`moveLong` / `moveShort` / `moveDrag` / `hoverHold` / `press` / `pressScale` / `ripple` / `rippleFrom` / `rippleTo` / `hlIn` / `toggleSlide` / `popIn` / `popFrom` / `startDelay`）；`moveTo()` / `press()` 两个函数 + `CONFIG` 就是可摘走的动效本体（`press(at, p)` 的第二参是本次按压的落点，涟漪靠它把圆心贴到箭头尖）。光标形状换成手型/文本光标只改 `.ui-cursor` 里那两条同形 path（描边层与实心层要同步改，保持 `transform-origin` 锚在热点）。
- Remotion 移植：光标位置 `x: interpolate(frame, [t0, t1]*fps, [x0, x1], {easing: Easing.inOut(Easing.quad), extrapolate*: 'clamp'})`、`y` 同区间换 `Easing.inOut(Easing.sin)`——两轴不同 easing 就是弧线；按压 `scale` 用 `[tp, tp+3, tp+6] → [1, 0.9, 1]`，涟漪同起点另开一组 `scale: [tp, tp+11] → [0.3, 1.6]` + `opacity: [tp, tp+11] → [1, 0]`（`Easing.out(Easing.quad)` / `Easing.in(Easing.quad)`），圆环用 `borderRadius: '50%'` 的 div 并把 `left/top` 设为 -半径；开关滑块 `translateX: interpolate(frame, [tOn, tOn+8], [0, 20], {easing: Easing.out(Easing.quad)})`，轨道色用 `interpolateColors`；pop-in `scale: interpolate(frame, [tUp, tUp+10], [0.4, 1], {easing: Easing.out(Easing.cubic)})` + `transformOrigin` 写成落点内光标的百分比坐标；拖拽阶段让被拖元素与光标读同一组 interpolate（只差一个常量偏移）。整段动作序列建议做成 `ACTIONS` 数组（`{target, at, kind}`）在组件里 map，帧号由词级时间戳换算。
- 剪辑软件对应物：剪映/CapCut——导入一张放大的光标 PNG（去底）单独一轨，打"位置"关键帧并把两端设"缓入/缓出"，UI 响应用同一截图的两个版本（关/开）在按下帧硬切 + 开关滑块单独一层做位移关键帧；AE——光标层 Position 关键帧 + 空间插值改"贝塞尔"手动拉出弧线（关键：别用线性），Scale 关键帧做按压，开关滑块 Position + Easy Ease，缩略图 pop-in 用 Scale 关键帧并把锚点拖到光标位置；录屏软件的"放大光标/点击高亮"内置功能一律不用（尺寸与节奏都不受控，且自带涟漪特效）。

## 动效范围
- 属于本卡的：光标的移动语言（x/y 分缓动合成弧线、两端加减速、跨区域 0.5~0.6s / 相邻 0.3~0.4s、拖拽段更慢）；到位后 0.2s 悬停微停顿；按压（光标 scale 1→0.9→1、锚点在箭头尖 + 目标 scale 1→0.94→1 + 从箭头尖扩散的涟漪 scale 0.3→1.6 / opacity 1→0 共 0.35s）；"状态切换发生在按下那一刻、不等抬手"这条时序纪律；三种响应语言（开关滑块滑动 + 轨道转深 / 按钮变色 / 缩略图以光标为原点 scale 0.4→1 弹入）及"一个目标只用一种"的纪律；hover 高亮的淡入淡出与"离开即熄"；拖拽时被拖元素与光标共用同一条曲线；三层层级（底 UI < 响应高亮 < 光标，光标永远最顶）；"一动作一口播词、约 1s/动作"的节奏契约。
- 不属于本卡的：demo 里那个"生成设置"假 UI 的结构与排版（开关行/对话框/素材库全是演示语境）、灰阶线框这套配色（`#f0f0f0` hover 底、`#1d1d1f` 开关轨、`#c8c8cd` 线稿色都是占位取值）、示例台词与字幕切换、角标主持人（数字人）、缩略图里的 SVG 线稿内容、深墨箭头这个具体光标形状与配色（手型/文本光标同样成立，只要热点锚点跟着换；填充色是占位取值，深底翻白即可）。
- 迁移接口：光标尺寸按画幅等比缩放（以"缩略图尺寸下仍认得出箭头"为准，约画幅短边 6~8%）；动作序列 = `(目标元素, 落点 fx/fy, 响应类型)` 的列表，目标点 = 落点坐标表（tsx `POS`；HTML demo 用 `P(el, fx, fy)` 运行时反算），换 UI 要重量 `POS`；时长全量对齐语音——把每个动作的 `at` 换成该口播词的词级时间戳（`hoverHold` 之后就是词的重音点）；响应色换成目标 UI 自己的 hover/active token（深色 IDE 截图把 hover 底色改为提亮、开关轨改为高亮色，光标描边由黑改白保持与底的对比）；pop-in 的 `transform-origin` 必须跟着落点内光标的实际位置改，不能写死。
- 底色要求：白底即可（demo 的浅色 UI 是最常见情形）。深色 UI 截图同样成立，唯一硬要求是**光标与底的对比必须保住**——本卡的"深墨实心 + 白描边"在浅底与深底上都成立（白描边就是深底上的保命层），深底只需把 `drop-shadow` 调淡、必要时把实心层翻成白色并改用深色描边层；涟漪同理（深芯白边两色互换）。hover 高亮由"加深"改为"提亮"。

<!-- ===== /file: video-talkcraft/references/cards/cursor-actor-demo.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/cursor-locked-zoom.md ===== -->

---
name: cursor-locked-zoom
标题: 光标锁定跟拍
优先级: P1
代码: template/cards/cursor-locked-zoom.tsx
一句话: 一条长命令在灰阶终端窗里逐字打出，相机 2.6~2.8x 锁死在光标上跟拍（tx = W/2 − zoom·cursorX 反解 + transform-origin 0 0），字符从画面右侧被"喂"进来、光标恒在正中；打完停 0.75s 让人读完，再用 0.8s inOut 把 zoom 拉回 1 收在全景居中
适用: 竖屏/小屏里念一条长命令、长路径、长配置、长代码行——"你要跑的是这一条"；tsx 只实现终端打字光标这一种锚点，要跟拍进度点 / 正在被填的表单字段等其他移动目标，按复用指引改锚点函数
时长: 实拍：起手 0.4~0.6s → 打字段（长度 ÷ 15 char/s，一条 50 字符命令约 3.4s）→ 读完 hold 0.6~0.9s → 拉回全景 0.8s → 尾 0.5s；合计 5.5~7s。demo：全程 6.0s
能量: 中
类别: 运镜
输入: 界
语义: 过程演示, 步骤
素材形态: 界面
位置: 中段
props: hostSrc(未使用)
---

## 意图
小屏念长命令是口播的一个真实死角：整条 60 字符的命令铺在竖屏里，字号只能给到勉强可辨，
观众读不清；放大到能读，一屏又装不下。本卡是这个死角的唯一解法——**不要让观众读完整条，让他们跟着写的人往前走**。
镜头 2.7x 怼上去锁死在光标上，字符从右侧被"喂"进来，光标恒在画面正中：
任何时刻画面里都只有当前正在打的那七八个字符，而它们大到不可能看不清。

这一拍与本库其他运镜卡的根本区别在**镜头的驱动源**：其他卡的镜头是独立的关键帧（时间 → 姿态），
本卡的镜头**没有自己的时间轴**——它每帧由"已揭示了多少个字符"算出来。
所以打字快镜头就快、打字停镜头就停，两者不可能失步。移植时如果给镜头单独排一条位移 tween
去"追"打字，任何速率改动都会让它们错开，观感立刻塌成"放大的终端在播打字动画"。

第三条是收尾：**跟拍必须以全景收尾**。观众刚跟着走完一条命令，眼里只有片段，
需要一眼看到"这条命令整体长什么样、在哪个上下文里"。不收这一拍等于没讲完。

## 动效核心
- 结构两层：`.camera`（铺满舞台的世界坐标层，`transform-origin: 0 0`，全卡唯一被 transform 的元素）→ 素材（终端窗）。素材在世界坐标里**位置固定**，动的只有相机
- **`transform-origin: 0 0` 是反解式子成立的前提**。默认的 `center` 会让 `scale` 绕元素中心发生，那条式子整个不成立（移植时最容易漏的一行）
- **核心反解（一行就是全部）**：`tx = W/2 − zoom·cursorX`、`ty = H/2 − zoom·cursorY`、`scale = zoom`。含义是"把锚点的缩放后位置搬到画面正中"
- **锚点由打字算出**：`cursorX = 文本起点 + 已揭示字符数 × 字宽`，`字宽 = fontSize × 0.6`（Menlo / SFMono 等宽字体实测系数）。
  `cursorY = 窗顶 + 窗栏高 + 内边距 + 行序 × 行高 + 行高/2`（行高 = `round(fontSize × 1.6)`）
- **等宽字体是硬前提**：整套锚点靠"字符数 × 字宽"算，比例字体下每个字符宽度不同，反解会越打越偏
- **边界钳制（白底舞台的必需补丁，原版没有）**：把可视世界矩形关在素材四边之内——
  `半宽 = W/(2·zoom)`，`cx = clamp(cursorX, 素材左 + 半宽, 素材右 − 半宽)`，纵向同理；素材比可视区还小时退化为居中。
  纯反解在行首/行尾会把画幅推出素材外，原版是深色背景所以看不出，白底舞台上就是大片空舞台
- **收尾只需 tween `zoom` 一个值**：`zoom` 变小 ⇒ 可视矩形变大 ⇒ 钳制范围收窄 ⇒ 中心被连续挤回素材正中；`zoom = 1` 时素材比画幅小、钳制退化为居中 ⇒ 恰好落在全景居中。不需要第二条位移 tween（这是钳制顺带给的便宜）
- 打字段缓动 `none`（线性）：人敲键盘是匀速的，加缓动会读作"机器在渐快渐慢"。速率 15 char/s（人在敲命令，比日志输出慢一个量级）
- 收尾缓动 `power2.inOut` 0.8s：**两端都要收**——这是"结束"（一个有始有终的事件），不是持续运镜
- 光标状态语言：竖条 2px × 24px，**打字时实心不闪、停下后才 2Hz 闪**。实心＝"正在输出"，闪烁＝"在等下一步"，这是终端唯一的状态语言；全程闪会读作"卡住了"
- 素材语境：终端窗深底（"命令行"这层语义靠深底成立）+ 三交通灯灰阶；上方留两行压暗的会话记录（`ls` + 输出），让被跟拍的那一行读作"接着上文在敲"而不是空屏起手
- **窗宽必须让整条命令在 `zoom = 1` 时完整可读**——收尾给的就是"全貌"，全貌里命令还被窗口裁掉半截，这一拍就白收了

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `zoom` | 2.65（范围 2.6~2.8） | 跟拍焦距。<2 起不到"小屏也看得清"的作用（那不如不跟拍）；>3.2 字重被放大到发虚、且一屏只剩四五个字符，观众失去上下文 |
| `rate` | 15 char/s（范围 12~20） | 打字速率。>22 读作"机器在贴"不是"人在敲"；<10 观众等得难受。**命令必须比日志输出慢一个量级**（日志是 60~70 char/s，见 [terminal-typing-log](terminal-typing-log.md)） |
| `charW` | 0.6 | 等宽字宽系数。Menlo / SFMono / Consolas 实测都在 0.6；换字体必须实测（错 0.02 到行尾就偏出半个字符） |
| `fontSize` | 20px | 与 CSS 必须一致（字宽与行高都由它算）。这是 `zoom = 1` 时的字号，跟拍时的视觉字号 = 20 × 2.65 ≈ 53px |
| `lineH` | 32px（= round(fontSize × 1.6)） | 行高。多行跟拍时它就是纵向跟踪的步长 |
| `leadIn` | 0.45s | 起手静置。镜头先锁在行首等口播开口；0 = 观众还没看清是个终端就开始打了 |
| `holdEnd` | 0.75s（实拍 0.6~0.9s） | 打完停留。**让人读完整条命令**，此时光标开始闪；<0.4s 观众来不及读最后一段 |
| `pullDur` | 0.80s | 拉回全景。<0.5s 读作"弹回去"；>1.2s 观众以为还有下一处要看 |
| `cursorHz` | 2 | 停下后闪烁频率。这是终端的通用值，不建议改 |
| 命令长度 | 40~65 字符 | <30 字符不需要跟拍（一屏就能读清，直接给全景）；>80 字符跟拍时间过长、观众会走神 |

## 已知坑
- **`transform-origin` 用了默认的 `center`**——反解公式失效，镜头位置全错（且错得"看起来像个 bug 但说不清哪儿不对"）。必须 `0 0`。
- **给镜头单独排一条位移 tween 去"追"打字**——两者会在任何速率改动后失步。镜头必须每帧由 `已揭示字符数` 现算，这是本卡的定义性特征。
- **比例字体**（默认无衬线）——"字符数 × 字宽"的反解越打越偏，行尾时光标已经跑出画面。等宽字体是硬约束。
- **纯反解不加边界钳制**——行首那几个字符和整条打完时，画幅会被推出素材之外。原版（remocn）是深色背景所以看不出；白底舞台上就是大片空白。这是移植到本库必须补的一段。
- 打字段加缓动（`power2` 之类）——读作"机器在渐快渐慢"，人敲键盘是匀速的。这一段的 ease 必须是 `none`。
- 光标全程闪烁——读作"终端卡住了 / 在等输入"，与"正在输出"的语义打架。**打字时实心，停下才闪。**
- 不收全景就结束——观众眼里只有片段，不知道这条命令整体长什么样。跟拍必须以全貌收尾。
- 窗宽不足，`zoom = 1` 时命令仍被裁——收尾那一拍白收了。窗宽按"最长那条命令 × 字宽 + 内边距 + 提示符"反推。
- `zoom` 开到 3.5 以上——一屏只剩四五个字符，观众彻底失去上下文，跟拍变成"在一堆字母里游泳"。
- 用它跟拍短命令（`npm i`）——不需要。30 字符以内直接给全景 + 一次 [slow-push-in](slow-push-in.md) 就够，本卡的成本不划算。
- 一屏里同时跟拍**两个**移动目标（光标 + 进度条）——镜头只能锁一个。要讲两个就拆两拍。

## 复用指引
- props：`hostSrc` 声明但未使用（本卡无主持人层）；命令文案与终端几何在 `CONFIG`（`cmd / winL / winT / winW / winH / pad / chromeH`），换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/cursor-locked-zoom.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：`demos/cursor-locked-zoom/index.html`。换命令改 `CONFIG.cmd`（同时按新长度检查窗宽）；速率与焦距在 `CONFIG.rate` / `CONFIG.zoom`；素材换成别的窗口时改 `CONFIG.winL/winT/winW/winH/pad/chromeH` 这组几何（它们既用来推锚点，也当相机的钳制边界）。核心可摘走：`CONFIG` + `apply()`（反解 + 钳制那七八行）。
- 换素材的最小流程：① 把素材在世界坐标里的四边填进 `winL/winT/winW/winH`；② 锚点公式换成"素材里那个移动目标的中心坐标"（不一定是字符光标——进度点、被填的表单字段、正在被高亮的行都行）；③ 其余不动。**只要能写出"目标中心的世界坐标"这一个函数，本卡就能跟拍它。**
- **多行代码跟拍**（源头的 `glass-code-walk` 变体）：把 `cmdRow` 从整数换成浮点行号，`cursorY = 窗顶 + 窗栏 + 内边距 + linePosition × lineH + lineH/2`，`linePosition` 在相邻行之间插值（扫读第 3 行到第 4 行时它是 3.0 → 4.0）⇒ 镜头在行间平滑滑过而不是整跳。横向可以只锁 x 到行首（读代码是整行读，不是逐字读），或对整行取中点。
- Remotion 移植：本卡 tsx 即成品——`CONFIG` + 组件内那十行可整段摘走：`revealed = lerp(0, N, clamp01((t − leadIn) / (N / rate)))` 线性揭示 → `cx = textX + floor(revealed) · charW` 反解 → 半宽 `W/(2z)` 钳制 → 收尾只 tween `z`。命令行逐字符揭示（不分块），日志才分块（见 [terminal-typing-log](terminal-typing-log.md)）。原型来自 remocn 的 terminal-cursor-zoom 组件（无边界钳制，移植到白底舞台必须补）。
- 剪辑软件对应物：AE——把终端截图/录屏放进合成，加一个空对象（Null）当"光标锚点"、按打字节奏给它打位置关键帧，再把摄像机或图层的位置**表达式**绑到 `W/2 − zoom × null.position[0]`（表达式比手打关键帧准得多，也是唯一能保证不失步的做法）；缩放拉回用 `Scale` 的两个关键帧 + Easy Ease 双侧。剪映——只能手动逼近：把录屏放大后按打字节奏打一串"位置"关键帧（会失步，且长命令关键帧数量大），不推荐。Premiere——`Motion` 的 Position 关键帧同理，或用 After Effects 动态链接。**真实制作里更常见的做法是直接录屏 + 后期跟拍**，但录屏的打字速率不可控（人手不匀），本卡的价值恰恰是让速率与镜头都可编排。
- 音效：`typekey` 稀疏连发——**不要逐字符给声**（50 个字符 50 记声音会糊成一片噪音）。按"词"分组，每个词起头给 2~3 记，`vol` 0.24~0.30 之间轮换、`rate` 0.94~1.24 之间轮换（同一音色反复出现必须变调，否则读作机械循环）；拉回全景那一下一记 `whoosh`（`vol` 0.26、`rate` 0.92）。hold 段无声。

## 动效范围
- 属于本卡的：**相机锁定移动目标跟拍**这一整套——反解公式 `tx = W/2 − zoom·cursorX`（`transform-origin: 0 0` 为前提）、**镜头由内容进度驱动而非独立关键帧**这条定义性纪律、锚点由"已揭示字符数 × 字宽（fontSize × 0.6）"算出、等宽字体的硬约束、把可视矩形关在素材四边内的边界钳制（以及"只 tween zoom 一个值、位移由钳制自动跟出"这个便宜）、打字段 `ease: none` 的匀速纪律、2.6~2.8x 的焦距区间、"打字时光标实心 / 停下才 2Hz 闪"的状态语言、以及 0.8s `power2.inOut` 拉回 `zoom = 1` 收在全景居中的收尾一拍（含"窗宽必须让全貌可读"这条反推纪律）。
- 不属于本卡的：demo 里的终端窗视觉（深底 / 三交通灯 / 路径标题 / 上方两行会话记录）、那条 ffmpeg 命令本身及其内容、命令行这个题材（跟拍对象换成进度点、表单字段、被高亮的行都成立）、打字速率取 15 char/s 这个具体值、素材尺寸 760×384 这组具体几何、终端配色。
- 迁移接口：把素材四边填进 `winL/winT/winW/winH` 即完成钳制配置；把"目标中心的世界坐标"写成一个随进度求值的函数即完成跟拍配置（这两件事是本卡唯一需要适配的东西）；`zoom` 按"跟拍时最小字号的视觉尺寸够不够读"验收（不是按构图）——竖屏 1080 宽下 `fontSize × zoom ≥ 44px` 是安全线；`rate` 按口播语速给（他念一个参数你打一个参数，别让镜头跑在解说前面）；`charW` 换字体必须实测；窗宽按最长命令反推。
- 底色要求：舞台白底成立（demo 已验证），但**素材本体需要深底**——"命令行"这层语义靠深底成立。若跟拍对象不是终端（比如浅色表单界面），素材浅底同样成立，此时边界钳制更加不可省（浅素材与白底舞台之间没有明度差，露边会读作"素材消失了"）。
- 与本库其他运镜卡的边界：[slow-push-in](slow-push-in.md) / [slow-pull-reveal](slow-pull-reveal.md) 的目标是静止的，镜头走独立关键帧；[stage-keyframe-tour](stage-keyframe-tour.md) 是多关键帧停靠**预设**的兴趣点（位置在动画前就已知），本卡的目标位置**只有运行时才知道**（取决于打到第几个字符）——这是"关键帧运镜"与"跟拍"的分界。素材侧的边界：[terminal-typing-log](terminal-typing-log.md) 讲的是终端**逐行推进 + 滚动**（镜头不动、内容在动），本卡是单行长命令 + 镜头在动；两张卡可以接在一起用（先跟拍念完命令，拉回全景后切给逐行日志跑起来）。

<!-- ===== /file: video-talkcraft/references/cards/cursor-locked-zoom.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/danmu-bubble-praise.md ===== -->

---
name: danmu-bubble-praise
标题: 弹幕气泡
优先级: P1
代码: template/cards/danmu-bubble-praise.tsx
一句话: 四枚评论气泡按 0.55s 错峰从最近的边缘外侧飘入，每枚只停 0.75s 就上移 18px 淡出——进出交叠到第 3 枚进场时第 1 枚正在走，四枚里只有一枚是强调色
适用: 口播讲到"评论区都在说""大家反馈最多的就是这点"时；开场证明这条内容有共识；结尾引导互动前的铺垫；社区感、轻快调性的口播（知识区、测评、生活方式）
时长: 起手静置 0.4s → 四枚错峰 0.55s 依次进（每枚进 0.3s / 停 0.75s / 走 0.4s）→ 末枚走后留白 0.45s；共约 3.95s
能量: 中
类别: 人物互动
输入: 文, 人(可选)
语义: 引用, 例证
素材形态: 无
位置: 任意
props: hostSrc
---

## 意图
口播里"大家都在说"这句话最容易空——嘴上说有共识，画面上没有任何人在说。
弹幕气泡把这句话变成可见的**多人在场**：四条别人的短评从画面两侧漂过，观众读到的不是
"主播贴了四个标签"，而是"这条内容底下真的有人在聊"。

它和本库的 `chat-message-flow` 分工不同：那张是**一段对话**（有先后、有回应、气泡沿一条轴堆积，
是叙事载体）；这张没有对话关系，四条评论互不相关、各自从各自的边进出，是**氛围层**——
它不承担信息，只承担"人多"这个感觉，所以它可以叠在任何一句口播上而不抢内容。

命门两条：① **必须交叠进出**。全进全出（四枚一起出现、一起消失）读作"一组标签"，
那是版式不是弹幕；只有当第 3 枚进场时第 1 枚正在走，观众才补出"屏幕外还有更多评论正在滚"
这个画面之外的量。② **只有一枚带强调色**，其余走灰阶实色。四枚都彩色 = 花屏，
而且"哪条评论最重要"这个唯一的语义抓手就没了。
与 `x-follow-card` 的分工：那张是"这个人凭什么"的完整档案（一个人、一次交互），本卡是"很多人都这么说"的即时共识（多人、氛围层）。

## 动效核心
- **单枚的三拍是固定模板**（四枚完全同构，只有起点时间与落位不同）：
  - 进：`x ±26 → 0` + `scale 0.88 → 1` + `opacity 0 → 1`，`0.30s power3.out`。
    横向方向 = **朝画面中心**（左侧的枚从 −26 推入、右侧的枚从 +26 推入），弹幕从最近的边进
  - 停：`0.75s` 完全静置（不漂、不呼吸——微动会把它从"别人的评论"变成"会动的贴纸"）
  - 走：`y 0 → −18px` + `opacity → 0`，`0.40s power1.in`。**出场只动 opacity 与 y，scale 不再动**
    （出场永远比入场轻，design-language §4）；上移是"往上滚出去"这个弹幕方向的最小表达
- **错峰 0.55s 与停留 0.75s 是一对**：单枚全程 = `0.30 + 0.75 + 0.40 = 1.45s`，
  是错峰的 2.6 倍 ⇒ 任一时刻屏上有 2~3 枚、且总有一枚在进或在走。
  交叠量的判据：`inDur + hold ≤ 2 × stagger`（本卡 1.05 ≤ 1.10，刚好卡在临界，密度最高）
- **落位分布**：左右各两枚，四枚的 `top` 全不相同（92 / 158 / 296 / 372），
  纵向间距不等（66 / 138 / 76）。等间距会读作一列列表；左右交替（左·右·左·右）让视线来回摆
- **静态倾斜 ±1.2~1.8°**（`-1.5 / +1.5 / +1.2 / -1.8`）：贴歪感是**形状属性**，
  落定后全程不抖（design-language §4 禁 stop-motion 定格抖动）
- **气泡形制**：`border-radius: 999px` 纯圆角胶囊。**无尾巴三角**
  （用户 2026-08-25 定版删除——弹幕是飘过的浮层，尾巴是"谁在说"的对话框语义，
  会把它拉回 `chat-message-flow` 那张卡的语言）；无投影、无描边——
  它不是"落在底上的实物"，是浮层。`side-l/side-r`（tsx 为 `BUBBLES[].dir` ±1）只决定**进场方向**，不再决定尾巴朝向
- **色阶四级（唯一强调色 + 三级灰阶实色）**：强调枚 `#e0452c` 底 / 白字；
  其余三枚 `#e8e8ec`·`#f2f2f4`·`#e8e8ec` 底配 `#1d1d1f`·`#6e6e73`·`#545458` 字——
  **靠底色与字色的明度分层，不叠 opacity**（design-language §1 红线）
- **层级**：人物全景（z1） → 气泡（z3）。气泡永远压在人物上（评论是叠在画面上的浮层）

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `stagger` | 0.55s | **枚与枚的进场错峰，本卡第一命门**；与 `hold` 一起决定交叠量。>0.9s 每枚孤立出现、读作四个独立动效；<0.35s 四枚糊成一波，观众一条也读不完 |
| `hold` | 0.75s | 单枚在屏停留；判据 `inDur + hold ≤ 2 × stagger`。放到 1.4s 以上四枚会同时在屏 = 一组标签（本卡就死了）；<0.5s 观众读不完一条短评 |
| `inDur` | 0.30s | 单枚进场耗时；>0.45s 每枚都像在"郑重登场"，弹幕要的是随手飘进来 |
| `outDur` | 0.40s | 单枚淡出耗时；比 `inDur` 长是对的（进要有落点、走要不被注意），但 >0.6s 会有四枚长期半透明挂着 |
| `inX` | 26px | 进场横向位移；0 变成原地淡入（丢掉"从边缘外飘进来"的方向），>50px 读作被甩进来 |
| `outY` | −18px | 飘走上移量；0 变成纯淡出（少了弹幕往上滚的方向感），>40px 读作气球升空 |
| `inScale` | 0.88 | 进场起始缩放；<0.7 读作 pop 弹出（是另一种语言，气泡该是飘的）；1 则少一点纵深 |
| `tilt` | ±1.2~1.8° | 各枚静态倾斜；0 读作系统 UI 组件（干净但少了手作感），>4° 读作贴纸墙 |
| 枚数 | 4 | 3 枚交叠不足（总有一段只剩一枚在屏），6 枚以上单屏读不完——要更多就延长总时长而不是加密错峰 |
| 强调枚数 | 1 | **恒为 1**，本卡第二命门。2 枚起就没有"哪条最重要"，四枚彩色是花屏 |

## 已知坑
- 四枚一起进、一起出——读作"一组标签"（一个版式），弹幕这层语义直接消失；必须交叠。
- 每枚停 2s 以上求"看清"——四枚同时在屏，等于把弹幕做成了四行字幕，画面被占满还是没有"在滚"的感觉。
- 四枚都上彩色（每枚一个色）——花屏，且视线没有落点；灰阶三级 + 强调一枚才有层级。
- 灰阶枚用 `opacity: 0.5` 压淡——白底上 dim 件叠透明度必掉出可读区（design-language §1 实测红线）；要更淡就换更浅的底色实色，不动字的透明度。
- 落位纵向等间距——四枚读作一列纵向列表，与"从两侧随机飘过"的弹幕感相反；间距要不等。
- 落定后给气泡加漂浮/呼吸微动——它立刻从"别人的评论"变成"会动的装饰贴纸"，也违反 §4 定版偏好。
- 出场也做 scale（缩回去）——出场比入场重了，观众的眼睛会被"消失"这件事拽走一次。
- 气泡加投影或描边——它是浮层不是证据素材；投影只给截图/照片（design-language §3）。
- **气泡加尾巴三角——2026-08-25 用户定版删除**。尾巴是对话框语义（"这句话是某个人在说"），
  弹幕是匿名飘过的氛围层；加了尾巴四枚就读作四个人围着主播说话，也和
  `chat-message-flow` 撞语言。纯胶囊就够了。
- 气泡压住人物脸——弹幕可以压身体，压脸就成遮挡；落位先避开人物头部矩形。
- 用 `Math.random()` 生成落位或错峰——重播两次不一样，卡库要求可复现（用固定数组）。

## 复用指引
- props：仅 `hostSrc`；四句评论与进场方向在 `BUBBLES` 常量（`dir` ±1）、落位与配色在 CSS `#b1~#b4`、节奏在 `CONFIG`，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/danmu-bubble-praise.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/danmu-bubble-praise/index.html。换文案改四个 `.db-b` 的文本（每条 4~8 字，
  `white-space: nowrap` 是硬要求）；换落位改 `#b1~#b4` 的 `left/top`，同时把 `side-l/side-r`
  改成"离哪边近就从哪边进"（这个 class 只决定进场方向）。
  能量只调 `stagger` 与 `hold` 这一对，改完用判据 `inDur + hold ≤ 2 × stagger` 复核。
  换强调色只改 `#b2` 的 `--fill`/`--ink` 两个变量，其余三枚永远灰阶。
- Remotion 移植要点：单枚 = 一个 `<Bubble>` 组件，props 传 `enterFrame / side / tone`。
  每枚三段 `interpolate` 用同一个局部时钟 `local = frame - enterFrame`：
  `opacity` 走 `[0, 9, 9+23, 9+23+12] → [0,1,1,0]`（30fps：进 9 帧、停 23 帧、走 12 帧），
  `translateX` 只在前 9 帧 `[±26 → 0]`（`Easing.out(Easing.cubic)`），
  `translateY` 只在最后 12 帧 `[0 → −18]`（`Easing.in(Easing.quad)`），
  `scale` 同前 9 帧 `[0.88 → 1]`。`extrapolateLeft/Right: "clamp"` 不能省。
  四枚的 `enterFrame` = `12 + i * 17`（0.4s + i×0.55s @30fps）。倾斜写死在样式里不进 interpolate。
- 剪辑软件对应物：剪映/CapCut——四个文本贴纸各自套"入场：向左/向右滑动 0.3s" +
  "出场：向上滑动 0.4s"，然后**手动把四条轨错开 0.55s** 拖成阶梯（错峰是唯一要手动做的事，
  剪映没有 stagger 概念）；气泡底用"文字背景"开圆角拉满。
  AE——一个 `Bubble` 预合成做完三拍，复制四份用 `Sequence Layers`（Overlap 勾上，
  Duration 设 0.9s）自动错开，或直接给四层的 In 点手动 +17 帧；倾斜在图层 Rotation 上写死。
- 与本库同类卡的分工：`chat-message-flow` = **一段对话**（有先后有回应、沿轴堆积、承担信息）；
  `subscribe-cta` = 一次性的行动号召（单枚、要停住让人读完）；
  **本卡 = 氛围层的多人在场**（互不相关、进出交叠、不承担信息）。
  本卡可以叠在任何一句口播上，也因此它不能承担任何具体信息——真要观众记住某条评论，
  用 `quote-card` 单独立一屏。

## 动效范围
- 属于本卡的：单枚"进 0.3s / 停 0.75s / 走 0.4s"这个三拍模板；`stagger 0.55s` 与 `hold 0.75s` 这一对（以及 `inDur + hold ≤ 2×stagger` 这条交叠判据）；进场朝画面中心 `x ±26 → 0` + `scale 0.88→1`、出场只走 `y −18` + `opacity`（出场不动 scale）这条纪律；四枚纵向落位不等距 + 左右交替这个分布规则；落定后完全静置（不漂不呼吸）；静态倾斜 ±1.2~1.8° 作为形状属性；"四枚里恒有且仅有一枚强调色，其余靠底色/字色明度三级分层而非透明度"这条配色纪律。
- 不属于本卡的：demo 那四句具体评论文案（说得太对了 / 干货满满 👍 / 收藏了 / 已经在用了）、`#e0452c` 这个具体强调色（参考图同色系任一个都成立）、21px 字号与 600 字重、`border-radius: 999px` 胶囊这个具体气泡形制（换成方角小卡、圆角矩形 chip 都不影响动效；**但尾巴三角不许加回来**——那是对话框语义，见已知坑）、四枚的具体 `left/top` 数值、白底舞台、以及铺满舞台的数字人主持人占位。
- 迁移接口：内容入口 = 四个 `.db-b` 的文本 + `side-l/side-r`；落位入口 = 各枚 `left/top`；配色入口 = tsx 里 `#b1~#b4` 四条规则的 `background / color`（HTML demo 是各枚 `--fill`/`--ink` 变量），强调枚只有一枚；能量入口 = `stagger` + `hold` 这一对（改完复核判据）；总时长 = `startDelay + (n−1)×stagger + inDur + hold + outDur + tailHold`，加枚数请延长总时长而不是加密错峰。竖屏：落位改成"上下各两枚"（竖屏两侧宽度不够放 6~8 字的气泡），`inX` 换成 `inY ±26`，其余时序不动。
- 底色要求：白底即可。唯一约束是**底不能与气泡的灰阶三级撞明度**——灰阶枚靠底色明度分层，深底上必须整套反相（气泡底改深灰三级、字反白），不能只把字反白。

<!-- ===== /file: video-talkcraft/references/cards/danmu-bubble-praise.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/doc-park-left-pill-deal.md ===== -->

---
name: doc-park-left-pill-deal
标题: 文档驻留发牌
一句话: 700×420 的文档先满幅在场 0.9s，然后不淡出而是以左边缘为锚驻留（0.8s power2.inOut：translateX −514 + scale .92，只露约 35%——"来源还在"），右侧按旁白节奏每 1.3s 慢发牌一张白底描边药丸（0.2s 淡入 + 0.37s back.out(1.7) 落定，先实后稳），每张落定 0.3s 后其下说明行逐词加深并留住；文档内容全程 −18.75 px/s 极慢自动滚动"正在被读"；三张落齐是静态结论清单，6.6s 同收
适用: "读完这份报告 / 论文 / 长文，我记下三条"式的要点提炼；评审意见逐条给出（左边是被评的东西）；"这个页面告诉我三件事"；文档理解类 AI 话题的结论镜头。输入是一张文档 / 长截图 + 三条结论文案；无人物在场
时长: 7.0s（0.9 满幅读 → 0.9–1.7 驻留 → 1.9 / 3.2 / 4.5 三次发牌，各带说明行逐词加深 → 6.6 同收 0.4s）；成片把三次发牌对到口播念出每条结论的时刻
能量: 中
类别: 素材呈现
输入: 截图, 文
语义: 引用
素材形态: 长图
位置: 中段
props: docTitle, pills, notes, hint, docSrc, accent
优先级: P1
代码: template/cards/doc-park-left-pill-deal.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 人物不参与（要人在场的要点列举用 split-60-40-story 左格放人） | ✗ 文档是静态被读物；录屏当文档也成立但要慢放 | ✓（默认输入）文档 / 报告 / 论文的长截图，驻留后仍慢滚 |

只吃一张文档 + 三条结论文字（+ 各一行说明）。

## 常用场景
1. "读完 60 页报告，我记下三条"——文档驻留左侧，三条结论逐个发牌（demo 演的）
2. 论文 / 长文的要点提炼：左边论文首页，右边三条 takeaway
3. 评审 / 点评：左边被评的页面 / 作品，右边逐条意见
4. "这个页面告诉我三件事"：左边网页截图，右边三条

## 意图
口播从"读一份东西"过渡到"给出结论"时，常见做法是文档淡出、结论淡入——来源消失了，结论像凭空说的。`split-60-40-story` 一开始就分屏、没有"读"的过程。本卡的戏在**驻留**这个动作：文档先满幅让观众看清它是什么，再**缩到一边而不消失**，右侧腾出的空间按旁白节奏发结论——语义是"读完 → 提炼"，来源全程在场。做对四条：
1. **驻留不是淡出**：以左边缘为锚缩放，文档右缘停在 x≈260，露出的 35% 足够认出"这是刚才那份"。
2. **驻留窗在首张药丸之前收住**（1.7 < 1.9）：重叠会出现"文档还在滑、药丸已在发"的浑浊。
3. **药丸先实后稳**：透明度 0.2s 快、位移 0.37s 慢带过冲——"发牌落桌"的手感；两窗等长读作普通淡入。
4. **说明行逐词加深后留住**（用户 2026-09-06 定版，母本是下一张来之前清场）：三张落齐 = 一张静态结论清单，观众可以回看。

## 动效核心
- **几何**（960×540）：文档 `.dpk-doc` 130×60 起 700×420、白底 1px hairline、圆角 14、唯一投影、`transform-origin 0% 50%`；内部 `.in` 内边距 34×40、标题 26px / 700、灰条 12 高（小标题条 16 高 60% 宽）。提示行 `.dpk-hint` 380×78 起 16px `#7a7a7a` 字距 1。药丸列 `.dpk-pills` 380×130 起宽 500：药丸高 52、圆角 26、白底 1.5px `#d6d6dc` 描边、22px / 600、左侧 10px 强调色圆点，纵向每张 100；说明行 18px `#7a7a7a` 在药丸下 60，逐词 span 初始 opacity .3。
- **常驻滚动**：`.in` `translateY(−18.75 px/s × t)` 线性，时长 = 镜头时长（写速率不写秒数）。
- **驻留**：0.9s 起 0.8s `power2.inOut`：`x 0→−514`、`scale 1→.92`；提示行 1.4s 起 0.4s 淡入。
- **发牌**（`T0 = [1.9, 3.2, 4.5]`）：药丸 `opacity 0→1` 0.2s `power2.out` + `y 14→0 / scale .94→1` 0.37s `back.out(1.7)`；说明行 +0.3s 起 0.1s 显、逐词 0.12s 线性加深到 1、词间隔 = `(下一张起点 − 0.1 − 本张起点 − 0.3) × 0.7 / 词数`（末 30% 静置阅读）；加深后不再变化。
- **退场**：6.6s 文档 + 提示 + 药丸 + 说明 opacity→0 0.4s `power2.in`，7.0s 结束。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `parkAt` / `parkDur` | 0.9 / 0.8s | 先满幅读 ≥0.8s 观众才认得出文档；驻留必须在首张药丸前收住 |
| `parkX` / `parkScale` | −514 / .92（露约 35%） | 露 <25% 文档成装饰失去"来源"语义；>40% 右侧放不下药丸 |
| `T0` 发牌起点 | 1.9 / 3.2 / 4.5（间隔 1.3） | 间隔 = 一句短旁白；<0.9 说明行逐词加深来不及走完 |
| `pillIn` / `pillLand` | 0.2 / 0.37s back.out(1.7) | 透明度窗比位移窗短是有意的（先实后稳）；换 outCubic 变成平淡浮起 |
| `noteDelay` | 0.3s | 药丸落定后才起字；提前会出现说明先于结论 |
| `noteShare` | 0.7 | 加深占该句可见时长 70%，末 30% 静置阅读；调到 1.0 刚读完就到下一张 |
| `scrollRate` | −18.75 px/s（≈0.6 px/f） | "正在读"的暗示级速度；>3 px/f 抢注意力变成滚动展示 |
| 药丸 / 说明字号 | 22 / 18 | 药丸 ≥ 条目档 20@960；说明行 18 ≥ 最小可读 14@960 |

## 已知坑
- 文档淡出而不是驻留——来源消失，结论像凭空说的；这是本卡与"切镜到结论页"的全部区别。
- 驻留与首张药丸重叠——文档还在滑、药丸已在发，画面浑浊。
- 药丸透明度窗与位移窗等长——读作普通淡入，没有"发牌落桌"。
- 说明行在下一张来之前清场（母本做法）——用户定版要留住；清场后观众回看不到。
- 文档露太少（<25%）——退成装饰条；露太多右侧放不下 22px 药丸。
- 自动滚动太快——抢注意力，读作滚动展示；停止滚动——文档死掉，"正在被读"的暗示没了。
- 三张药丸文案长度差太大——列表参差；控制在 9~12 字。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/doc-park-left-pill-deal.tsx——`docTitle / pills / notes / hint / docSrc / accent`；durationInFrames 222；传 `docSrc` 时真文档长截图铺进文档卡并随内容慢滚。
- HTML/GSAP：demos/doc-park-left-pill-deal/index.html——改 `PILLS / NOTES` 与 `CONFIG`；`.dpk-doc .in` 整块换成 `<img>` 即真文档。
- 母本：video-shotcraft `doc-park-left-pill-deal`（文档 park 到 35% + 慢发牌 + 字幕逐词加深）。口播化改造：字幕改说明行且落定后留住；文档先满幅读 0.9s 再驻留。
- 剪辑软件对应物：剪映文档图层"缩放 + 位置"两个关键帧（锚点设左中）+ 三个文字条逐个"弹入"；AE 用 Anchor Point 左中 + Scale/Position 关键帧 easy-ease，药丸用 Shape Layer + Text Animator Opacity 按词。
- 与 layout.md 的接口：驻留后文档右缘 260、药丸列左缘 380，组间距 120 ≥ 组内 100 ≥ 元素内 22（§2 层级）；药丸与说明左边缘对齐同一栏线（§3）；三张药丸 + 说明包围盒 (380,130)–(880,410) 中心 x=630 落右半幅中心 (720) 偏左 90——有文档在左时属"主从"版式，不按无人物居中判（§4）。

## 动效范围
- 属于本卡的：满幅 → 驻留（左缘锚、露 35%）的动作；驻留必须先于发牌；慢发牌的先实后稳；说明行逐词加深并留住；文档常驻慢滚。
- 不属于本卡的：文档的具体内容、结论文案、药丸描边样式（风格档可改成 pastel 底板）。
- 迁移接口：`pills / notes / docSrc`；1080p 输出字号 ×2、文档 1400×840、parkX ×2；发牌点按口播摆。
- 底色要求：羊皮纸 `#f5f5f7` 默认（白文档与白药丸要从底上抬起来）；纯白底时文档与药丸改发丝线描边加重到 `#d0d0d5`。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- 1.7s 后任一帧：文档右缘 x ≈ 260（±10），左缘已在画外（x ≈ −384 = 130 − 514）——只露右侧那段（锚左缘判据）。
- 1.7s 前文档不得与任何药丸同屏（驻留先于发牌）。
- 每张药丸落定帧：其下说明行尚未出现（noteDelay 判据）；说明行加深后任一帧 opacity 不回落（留住判据）。
- 三张药丸左边缘 x 相等，纵向等距 100；药丸文字不越出药丸。
- 文档内容全程有位移（慢滚判据），但任一秒位移 ≤19px。

<!-- ===== /file: video-talkcraft/references/cards/doc-park-left-pill-deal.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/douyin-follow-card.md ===== -->

---
name: douyin-follow-card
标题: 抖音主页关注卡
优先级: P1
代码: template/cards/douyin-follow-card.tsx
一句话: 抖音用户主页卡整体 spring 弹入 → 头像/昵称/抖音号/数据/简介按阅读顺序错峰 blur-in → 光标弧线移入点"＋关注"，同帧按钮两态交叉 + 涟漪 + 副位图标→"发私信"；粉丝数静态（同原版 X，不做 +1）
适用: 口播里介绍某个人/账号——嘉宾出场、"这个人你该关注"、引用某人观点时给出处、推荐同行/作者；一条视频里同一张卡只出现一次
时长: 卡弹入 0.62s → 内容错峰（每层 0.07s 递进）→ 静置到 1.55s → 光标移入 0.95s → 2.58s 点击（翻转 + 涟漪 + 发私信；粉丝数静态）→ hold 0.85s；demo 全程 4.03s
能量: 中
类别: 人物互动
输入: 界, 图
语义: 引用, 介绍他人
素材形态: 界面
位置: 中段
props: avatar
---

## 意图
口播说"这个人做的内容你该关注"，观众心里的问题是"他是谁、凭什么、什么水平"。一张抖音主页卡把这三个问题一次答完：头像、昵称、抖音号、简介、**获赞 / 关注 / 粉丝**。
本卡的价值不在"贴一张主页图"，而在**让卡自己演一遍被关注**——光标走过去点下"关注"，按钮从"＋关注"翻成"已关注"（粉丝数静态，同原版 X 源码：源码的互动数是静态值）。这一下把静态主页变成社会证明：不是你在夸他，是"有人正在关注他"。

命门三条。**第一条是壳与内容分两拍**：卡整体先 spring 弹入到位，内容**再**逐层落。全同时亮 = 一张图淡入，那就只是贴图；壳先到位、内容后落，观众的眼睛才有机会按阅读顺序扫过去。
**第二条是光标必须走过去**（与 [subscribe-cta](subscribe-cta.md) / [x-follow-card](x-follow-card.md) 共享的纪律）：瞬移点击读作"状态自己变了"，不是"有人关注了他"。
**第三条是点击那一刻同帧发生**：按钮两态交叉 + 涟漪 + 副位图标→"发私信"（粉丝数静态，不做无法读出的 +1，同原版 X 源码）。前几件是"这一下按到了"，按钮状态翻转本身就是"关注生效"的反馈。

**产品皮 = 内容本身（2026-08-25+ 用户定版）**：本卡涉及真实产品界面（抖音对外主页），所以**完全还原抖音的样式**，不做中性化——背景默认蓝渐变、关注钮未关注红 `#EB455B`、已关注钮浅灰 `#F1F1F2` + 黑字、数据/简介正文黑 `#161823`、次级灰 `#9299A4`、`@` 蓝链 `#1E9FFF`。理由同 X 卡：观众要一眼认出"这是抖音主页上的某个人"，平台身份是这张卡的信息量之一，灰阶化之后"社会证明"的出处就断了。
可编辑的是**内容**（昵称 / 抖音号 / 获赞·关注·粉丝三连 / 简介多行 / 头像 / 背景），外观不动。头像是**默认人形剪影占位**（灰底白剪影），用户要放真头像就自备一张图：tsx 传 `avatar` prop（URL/staticFile），demo 放进 `.avatar` 内。

## 动效核心
- **卡整体弹入 0.62s**：`y 46→0` + `scale 0.9→1`，`back.out(1.35)` 微过冲（弹簧欠阻尼）。**淡入独立时间窗**（0.05→0.35s）——位移先动、透明度后跟。
- `transform-origin: 50% 0%`（卡顶）：弹入时卡从上边缘"垂下来"，绕中心缩放是弹窗不是卡片落位。
- **内容错峰 blur-in**：每层 `blur 8px→0` + `opacity 0→1` + `y 8→0`，单层 0.24s、层距 0.07s。三属性同动才是 "blur-in"；只做淡入是普通 stagger。**层序按阅读顺序**：背景→顶部导航→头像 + 昵称/抖音号（同一层）→数据三连→简介→**按钮行最后**（待交互目标最后落位，光标才有东西可点）。
- **多行简介整块一层**（不是每行一层）：行数变化只让卡片高度变，不牵动单层时序——否则简介 3 行和 7 行的错峰节奏就乱了。
- **静置到 1.55s**：内容铺完 + 0.34s 什么都不发生，给口播介绍这个人的余量。
- **光标弧线移入 0.95s**：x 用 `power2.inOut`、y 用 `sine.inOut` **异速叠出弧线**；从舞台右下外侧进场；`transform-origin: 0% 0%` 锚在箭头尖，按压微缩不让尖端移位。
- **落点必须在按钮"终态"位置上量**（老 bug：先铺了 `y:46 / scale:0.9` 再量，量到的是卡还在半空、还缩着 0.9 时的按钮；等光标走到那儿，卡早已落位，按钮上移 ~46px ⇒ 点击帧光标压在按钮下方的空处）。量之前先 `gsap.set(card,{clearProps:"transform,opacity"})`，在终态量一次再铺初始态。
- **点击帧的反馈链**（同帧起，缺一环就假）：光标 `scale→0.9` 一拍（0.09s）+ 按钮下压至 0.92（0.08s `power2.in`）+ 两态交叉 + 涟漪 + 副位图标→"发私信"，随后按钮 `back.out(3)` 回弹 0.22s。
- **两态交叉不是换文案**：同一个盒子里叠两层——"＋关注"层 `opacity 1→0` + `scale 1→0.92`（缩着退），"已关注∨"层 `opacity 0→1` + `scale 0.86→1` 带 `back.out(1.7)`（涨着进）。直接改 `textContent` 读作"字变了"，交叉才读作"按钮换了状态"。
- **粉丝数静态（同原版 X）**：粉丝数直接显示，不做纸带滚动。原版 X 源码（母本 x-follow-card）的互动数是硬编码静态值，本卡遵循默认静态——只有当粉丝数"能看到可读变化"时（见参数表）才考虑 +1，否则保持其截图读到的静态值。
- **副位"发私信"联动**：未关注态副位只显纸飞机图标；已关注态变成"✈ 发私信"文字。
- **胶囊形涟漪**：`inset −8`、`border-radius 999`，`scale 0.92→1.3` + `opacity 0.55→0`，0.5s `power2.out`。`fromTo` 必须 `immediateRender:false`——否则涟漪在"还没被点"时提前挂在按钮外圈。
- **光标用完即走**：顺势朝右下滑出淡出 0.45s。常驻光标一直吸引注意力。
- 层级：背景 cover（白底卡下的渐变色层）→ 顶部导航 → 头像/昵称/抖音号 → 白卡区（数据/简介/按钮）→ 光标（z-index 20）。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `cardIn` | 0.62s | 卡弹入。<0.35s 读作硬弹出（没有"落位"的重量）；>0.9s 观众等它进场 |
| `back.out` 过冲 | 1.35 | 弹入微过冲。=0 只是缩放出现；>2.2 显廉价，卡像蹦上来的 |
| `layerStagger` | 0.07s | 内容错峰间隔。=0 退化成"一张图淡入"；>0.14s 铺满要很久，观众逐条读而不听你讲 |
| `layerDur` | 0.24s | 单层 blur-in 时长。<0.15s 读作硬闪；>0.4s 与下一层重叠过多 |
| `layerBlur` | 8px | 入场模糊起点。<4px 看不出"对上焦"；>16px 每层进来都糊一下 |
| `cursorStart` | 1.55s | 光标起手（= 内容铺满 + 0.34s）。这 0.34s 是给口播介绍这个人的；<0.1s 内容没落完就有人来点，>1.2s 卡在那儿干等 |
| `cursorMove` | 0.95s | 光标弧线移入。<0.4s 接近瞬移，"有人在点"的证据消失；>1.4s 观众开始等它 |
| `clickDip` | 0.92 | 点击下压。>0.96 看不出按了；<0.88 按钮像被捏爆 |
| `flipDur` | 0.34s | 两态交叉。<0.18s 读作硬切图标；>0.6s 按钮慢慢化，观众盯着它不听你讲 |
| 粉丝数 | 静态（同原版 X） | 默认直接显示，不做 +1。若确定粉丝数"能看到可读变化"（精确个位或一档约数）可另加数字变化动效；约数（7.5万）无可读变化，保持静态（同原版 X 源码：互动数静态） |
| 简介行数上限 | `MAX_BIO_LINES = 5` | 卡高随行数自适应（宽度 500）。**超过 5 行截断**（`content.bio.slice(0,5)`），避免卡过高顶到竖屏字幕位；建议超出时精简/删次要行，而不是加高卡 |
| 卡片宽度 | 500 | 成片 meta 宽 500（逻辑基准 900 内凡缩放）。更矮更紧凑，简介更长也不易上下超屏；高度 = 内容高 × 缩放因子 |
| 出现次数 | 1 次/条 | 同一张卡两次 = 观众第二次直接跳过；换人才换卡 |
| 在场时长 | 3~5s | >8s 变牛皮癣挡内容；<2.5s 观众还没读完名字就没了 |

## 已知坑
- **内容同时全亮**——退化成"一张图淡入"，本卡最贵的那拍（逐层落位）就废了。壳先到位、内容后落是两拍。
- **blur-in 只做淡入不做 blur**——那是普通 stagger。三属性（blur/opacity/y）一起动。
- **多行简介逐行分档**——行数一多，错峰时间预算被拉爆，节奏乱；简介整块一层，行数只改卡高不改节奏。
- **在铺了重播初始态之后才量按钮位置**（2026-08-25 实修的 bug）——量到的是卡还在半空、还缩着 0.9 时的坐标，光标走到那儿按钮已上移 ~46px ⇒ 点击帧光标压在按钮下方空处。量之前先 `clearProps` 卡 transform，在终态量。
- **光标坐标没减箭头尖偏移**——`x/y` 设的是元素左上角，直接对准按钮心会让尖偏在按钮右下角外。减掉 `TIP`。
- **只跑 verify 的 t0/t1 两张截图就算验收过了**——交互卡必须**截点击那一帧**单独看（`node scripts/shot-at.mjs douyin-follow-card 2.58`），肉眼确认尖压在按钮上。
- **按钮行排在层序中间**——待交互目标先落位、后面还有内容在动，光标点下去时画面还没安定。按钮行放最后。
- **光标瞬移到按钮上**——读作"状态自己变了"，不是"有人关注了他"。社会证明说服力归零。
- **两态用改 `textContent`**——读作"字变了"；两层叠着交叉、退的缩、进的涨。
- **给约数硬做 +1**——`7.5万` 还是 `7.5万`，观众看不出变化，等于没做；约数保持静态（同原版 X 源码）。
- **`fromTo` 忘了 `immediateRender:false`**——涟漪建表时就把 from 态刷上去，按钮"还没被点"时环已经挂在外圈。
- **卡 `transform-origin` 用默认 center**——弹入时整卡上下长大，读作弹窗不是卡片落位；锚在卡顶。
- **把抖音的皮灰阶化**——黑底白字胶囊 + 中性八角标看着"像个社交卡"但**不是任何平台**，观众读不出这是哪儿的账号，社会证明出处就没了。产品皮 = 内容本身，照抄 `#EB455B`。
- **从"我的页"截图直接贴**——那是自己视角（编辑主页/互关/主播中心/订单/钱包），观众看不到，且**没有"关注"按钮**。要么提供"别人视角"截图，要么按"我的页→对外口径"转换（删互关、去自管项、补关注/发私信）。
- **标签栏硬塞**——IP/性别年龄/MCN/实名整栏不显示（用户定版），不要为了"还原"把它放进去。
- **入口区误留**——群聊/橱窗/直播动态/专属会员入口不显示（用户定版），卡片不含横向入口区。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/douyin-follow-card.tsx——props：仅 `avatar`；账号内容（昵称 / 抖音号 / 获赞·关注·粉丝 / 简介 / 背景）在 CONTENT 常量里，换内容需改源码。自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/douyin-follow-card/index.html。**换账号只改 HTML 里那几处内容**（`.name` / `.dvid` / `.stats` 三个 `<b>` / `.bio` 行 / `.avatar` 头像）——时序全在 `CONFIG`，与内容解耦，改文案不用碰任何时刻。
  - 粉丝数直接改 `.stats` 里最后一个 `<b>` 文本。
  - 节奏在 `CONFIG.cardIn` / `layerStagger` / `layerDur` / `cursorStart` / `cursorMove` / `flipDur`；层序改 `layers` 数组（阅读顺序，按钮行最后）；光标落点由 `P(el, fx, fy)` 从元素实际位置反算，换布局不用改坐标数字。
  - 核心可摘走：`CONFIG` + `DemoShell.register` 回调里的四段（①卡弹入 ②内容错峰 ③光标弧线 ④点击帧同帧五件事）。
- **换头像/背景**：一律走"产品皮 = 内容本身"——背景默认蓝渐变，上传头图 `{bg.type:'image',src}`；头像是**默认人形剪影占位**，要放真人/自制头像就自备一张图放进 `.avatar` 内。
- **"我的页"→对外口径转换**（只要自己视角截图也能出片，用户定版）：
  - 提取：背景、头像、昵称（去消息角标）、抖音号、**获赞 / 关注 / 粉丝**（删"互关"）、简介（多行）。
  - 删：编辑主页、互关、主播中心/我的订单/观看历史/我的钱包/全部功能、私密作品、"创建 AI 形象"、系统状态栏、底部 tab。
  - 补：＋关注/已关注∨ + 发私信（抖音对外通用规范样式，不因账号变）；粉丝数取截图值**静态显示**（不做 +1）。
  - 不涉及：标签栏（IP/性别年龄/MCN/实名）整栏无；入口区（群聊/橱窗/直播/频道）整块无。
- **剪辑软件对应物**：剪映/CapCut——卡做成一张静态图整体套"放大弹入"入场（0.6s 带回弹）；错峰只能切成多个图层（背景/头像/昵称/数据/简介/按钮）分别给 0.07s 递进入场；两态翻转是两个按钮图层交叉（"＋关注"层 Opacity 100→0 + Scale 100→92，"已关注"层 Opacity 0→100 + Scale 86→100 带弹性，关键帧必须对齐点击帧）；粉丝数静态（一两行数字即可）。
- 音效：卡弹入一记 `pop`（`vol` 0.5、`rate` 0.94，降调=有重量）；内容起头一记 `paper`（`vol` 0.26、`rate` 1.12，铺底不逐层给声）；点击帧一记 `click`（`vol` 0.55）。hold 段无声。

## 动效范围
- 属于本卡的：**壳与内容分两拍**的结构纪律（卡整体 spring 弹入到位 → 内容再逐层落）、卡弹入的"位移先动 + 淡入独立窗"错位与 `transform-origin` 锚卡顶、**内容错峰 blur-in**（blur 8→0 + opacity + y 三属性同动、0.07s 层距、按钮行最后）与**多行简介整块一层**的取舍、内容铺完后 0.34s 的静置（给口播的余量）、光标从屏外**弧线**移入（x `power2.inOut`/y `sine.inOut` 异速叠弧、锚点箭头尖）、**落点在按钮终态位置上量且减箭头尖偏移**这条纪律（连同"交互卡必须截点击帧验收"）、点击帧**同帧反馈**（光标缩一拍 + 按钮下压 + 两态交叉 + 涟漪 + 副位图标→"发私信"，随后 `back.out(3)` 回弹）、**两态交叉方向**（退的缩 1→0.92、进的涨 0.86→1 带 `back.out(1.7)`）、**粉丝数静态**（同原版 X）、**副位图标→"发私信"**联动、胶囊形涟漪 `0.92→1.3` 与 `immediateRender:false`、光标用完即走。
- 不属于本卡的：demo 那个人（Vincent / 335248116 / 3.2万·238·6455 / 两条简介）——那是可替换的演示内容；获赞·关注·粉丝三连的**具体数字**；**默认剪影头像**（占位样式）；顶部导航的具体图标形状；光标 SVG 的具体形状；**底部作品列表、标签栏、入口区**（都不在本卡内，用户定版：标签栏、入口区整块不显示）。
  **注意与 X 卡不同：抖音的皮（渐变背景、红色关注钮、灰关注钮、黑字、`@` 蓝链）属于"内容本身"而不是"可换的风格"**——灰阶化之后观众认不出这是抖音主页，社会证明出处就断了。
- 迁移接口：HTML 里那几处文本是唯一内容入口（时序与内容解耦）；粉丝数改 `.stats` 里最后一个 `<b>`；`cursorStart` 按口播语速给；换尺寸只改 `.scaler` 那一个 `scale()`（卡内值是 900 宽基准，不参与换算）；换人只改昵称/抖音号/数据/简介/头像，不碰任何时刻。
- 底色要求：**产品皮 = 内容本身**。背景默认抖音蓝渐变（`#BBD7EF→#75A4D0`）；上传头图则用 `img`。关注钮未关注红 `#EB455B`（从真实截图取样），已关注钮浅灰 `#F1F1F2` + 黑字；数据/简介正文黑 `#161823`、次级灰 `#9299A4`；`@` 蓝链 `#1E9FFF`。不受"白舞台中性化"约束（产品皮=内容本身），舞台本身仍白底，卡靠自身色 + 阴影与实拍背景分离（深色渐变盖实拍比浅色更稳）。
- 与相邻卡的分工：**vs [subscribe-cta](subscribe-cta.md)（多平台关注 CTA）**——那张是**语法合集**（三平台式样、落地只留一段、目标是"示范观众去点"，用在收尾）；本卡是**单卡精做的社会证明道具**（一张完整主页卡 + 一次关注交互，目标是"证明这个人值得看"，用在介绍嘉宾/账号的中段）。两张共享"控件弹入 → 光标弧线 → 点击反馈链 → 状态翻转"，差别是**卡还是控件**、**证明还是号召**、**中段还是收尾**。**vs [x-follow-card](x-follow-card.md)**——那张是 X 资料卡（深色卡 + 蓝关注钮，介绍"某人在 X 上"）；本卡是抖音主页（渐变背景 + 红关注钮，介绍"某人在抖音上"）。同一条视频里可以用 X 卡介绍某人在 X 的账号、用本卡介绍另一个人在抖音的账号，但同一张卡不要挨着放。**vs [lower-third-nameplate](lower-third-nameplate.md)**——那张是"这个人是谁"的最小信息（名字+头衔，出镜自报身份）；本卡是"这个人凭什么"的完整主页档案 + 一次交互，介绍**别人**并要观众记住这个账号时用本张。

<!-- ===== /file: video-talkcraft/references/cards/douyin-follow-card.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/error-retype.md ===== -->

---
name: error-retype
标题: 打字改口
一句话: 句干"口播做得好，靠的是"先在，后半句以打字机节奏（0.09s/字，帧确定硬切）打出"模型大小"→ 停 0.55s、光标以 4 帧半周期闪两下（犹豫）→ 以更快的 0.06s/字退掉 → 零犹豫同速重打"讲述方法"→ 完稿光标闪两下后摘除，整句静置 ≥2.6s 再同收。三档速度差是戏的全部，光标是演员的脸
适用: 否定式文案（"靠的不是 X，是 Y"）、纠正常见误解（"大家以为是 A，其实是 B"）、金句反转（先写出错的那半句）、片头 hook 的自我修正；作用于标题 / 主张句层，不作用于底部字幕
时长: 5.5s（0.7 起打 4 字 → 1.06 闪两下 → 1.61 起退 → 1.97 起重打 → 2.51 闪两下 → 3.06 光标摘除 → 5.11 同收 0.4s）；成片把"起退"对到口播说"不是"的时刻
能量: 低
类别: 字幕花字
输入: 文
语义: 转折
素材形态: 无
位置: 任意
props: prefix, first, second, accent
优先级: P1
代码: template/cards/error-retype.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 纯文字卡；人在场时整句放人物对侧半幅（layout §4） | ✗ | ✗ |

作用于标题 / 主张句层，不作用于底部跟读字幕（素排铁律）。

## 常用场景
1. 否定式文案："口播做得好，靠的是 ~~模型大小~~ 讲述方法"（demo 演的）
2. 纠正常见误解："大家以为是 A，其实是 B"——先打 A 再退掉
3. 金句反转：先写出错的那半句，停一拍再改成对的
4. 片头 hook 的自我修正："今天讲怎么涨粉 → 怎么不掉粉"

## 意图
口播里"不是 X，是 Y"这类改口，画面若直接出 Y，听觉上的"先错后对"就丢了；若用划线（`strike-and-replace`），是**空间上**标出错误。打字改口是**时间上**的改口：观众看着字被打出、犹豫、被退掉、再打对——情绪是"说错了改"，比"标出错误"更像人在说话。做对四条：
1. **三档速度差必须可感**：打 0.09 / 删 0.06 / 重打 0.06（s/字）。等速改口读作 bug 不是戏。
2. **光标三态**：打删常亮 = 果断；停顿才闪（4 帧半周期闪两下）= 犹豫；完稿闪两下后**条件摘除**——残留 0.05 opacity 都毁真静止。
3. **字符固定宽槽位、左缘锚定**：变宽字体整串测宽会逐帧重排抖动；光标用 x 补偿钉在最后一字后（空槽仍占位）。
4. **字符出现是帧确定的硬切**：任何缓动打字都读作加载动画。

## 动效核心
- **几何**（960×540）：整句 40px / 700 / 字距 −0.5 墨色 `#1d1d1f`，`.ert-tw` 绝对定位 `top 240`（行高 60，中心 y=270 中线）；`left = (960 − (句干宽 + N×44 + 4 + 6)) / 2` 由隐形尺子量出一次算定（N = 两个半句的最长字数）。槽位每字符 44px 居中；光标 6×46 强调色方块、左距 4。
- **时间表**：`tType = 0.7`；`tB1 = tType + 4×0.09 = 1.06`（闪两下）；`tDel = tB1 + 0.55 = 1.61`；`tRe = tDel + 4×0.06 + 0.12 = 1.97`；`tB2 = tRe + 4×0.06 + 0.3 = 2.51`（闪两下）；`tOff = tB2 + 0.55 = 3.06` 光标摘除；`exitAt = tB2 + 2.6 = 5.11`，0.4s `power2.in` 同收，5.51 结束。
- **打 / 删 / 重打**：已打字数 n 是帧确定的阶梯——打 `n = floor((t−tType)/0.09)+1`，删 `n = 3 − floor((t−tDel)/0.06)`，重打 `n = floor((t−tRe)/0.06)+1`；光标 `translateX(−(N−n)×44)`。
- **光标**：默认 opacity 1；两个闪烁窗 `[tB1, tB1+0.52)` / `[tB2, tB2+0.52)` 内按 0.13s 半周期方波（灭-亮-灭-亮）；`t ≥ tOff` 归 0。
- **入场 / 退场**：句干 0.1s 起 0.3s 淡入；`exitAt` 句干 + 槽位 opacity→0（光标此时已摘）。落定即静置，无 idle。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `type` / `del` / `retype` | 0.09 / 0.06 / 0.06 s/字 | 三档差必须可感——等速读作 bug；打 <0.07 中文读不出字，删 >0.08 退得不够决绝 |
| `pause` | 0.55s | "犹豫"的长度：<0.4 闪不完两下，>0.9 读作卡住 |
| `blink` | 0.13s（4f 半周期） | 快于 3f 像故障；慢于 6f 闪两下要 0.8s，拖节奏 |
| `gap` | 0.12s | 删完到重打的空档：0 读作一口气，>0.3 又成第二次犹豫 |
| `cursorOff` | 0.55s | 完稿闪两下后再等一拍摘除；不摘除的光标毁真静止 |
| `holdEnd` | 2.6s（≥50f） | 对的半句是全段目的，静置读完 |
| `slotW` | 44px | ≈ 40px 字号的字宽 + 呼吸；太窄字挤在一起，太宽读作字距拉开 |
| 半句字数 | 2~6 字，两半句字数接近 | 字数差 >2 时空槽占位明显；长的那半句决定 N |

## 已知坑
- 打 / 删 / 重打等速——观众读作 bug 不是"改口"，命门违例。
- 光标全程等速闪——光标是演员的脸，全程闪就没有"犹豫"那一拍。
- 完稿后光标还在——0.05 opacity 都毁真静止；必须条件摘除。
- 用变宽字体整串测宽——每加一个字整句重排抖动；必须固定宽槽位。
- 打字带缓动 / 淡入——读作加载动画不是打字机。
- 错的半句与对的半句字数差太大——空槽占位读作字距故障；改文案让两半句字数接近。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/error-retype.tsx——`prefix / first / second / accent` 四个 prop；durationInFrames 177（4 字 → 4 字，字数变了按 `tB2 + holdEnd + exitDur` 重算）；句干宽用 `useLayoutEffect + delayRender` 量一次。
- HTML/GSAP：demos/error-retype/index.html——改 `PREFIX / FIRST / SECOND` 与 `CONFIG`；字符出现用 `tl.call` 硬切，光标 x 由 `put()` 补偿。
- 母本：video-shotcraft `typewriter-moves` B 式 error-retype（A 式终端敲命令急推是开发者产品开场，不搬）。
- 剪辑软件对应物：剪映"文字 → 打字机"只能打不能删，需两段文字 + 关键帧手排；AE 用 Text Animator 的 Range Selector（Start 关键帧阶梯，Hold 关键帧）做打 / 删，光标另开形状图层用表达式 `wiggle` 不行——要 `Math.floor(time/0.13)%2` 方波。
- 与 layout.md 的接口：单主体落中线 y=270（§1）；整句按"句干 + N 槽 + 光标"总宽居中（§4，偏差 ≤48）；40px ≥ 条目档下限 20@960（§5）。

## 动效范围
- 属于本卡的：打 → 犹豫 → 删 → 重打的四段结构；三档速度差；光标三态（常亮 / 闪两下 / 摘除）；固定宽槽位 + 光标 x 补偿；帧确定硬切。
- 不属于本卡的：具体文案、光标色值（用本片强调色）、白底舞台。
- 迁移接口：`prefix / first / second / accent`；1080p 输出字号 ×2（80）、槽宽 88、光标 12×92；"起退"时刻按口播说"不是"的字锚摆。
- 底色要求：白底 / 羊皮纸底成立；深底时字反白、光标仍用强调色。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- 定妆帧三张：打字中途（如 1.0s）光标紧贴最后一个已出的字（间距 4px）；退掉一半（如 1.7s）光标同样紧贴；完稿（如 4.0s）光标已摘、整句静止。
- 整句包围盒水平居中偏差 ≤48，中心 y ≈ 270；人物在场时放人物对侧半幅中心（x = 240 或 720@960）。
- 用 `shot-at --play` 核 3.1s 后画面无任何元素在动（光标真静止）。
- 三档速度在成片 30fps 下各自可辨：打 ≈3f/字、删 / 重打 ≈2f/字。

<!-- ===== /file: video-talkcraft/references/cards/error-retype.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/evidence-scroll-tour.md ===== -->

---
name: evidence-scroll-tour
标题: 证据长页慢滚
优先级: P0
代码: template/cards/evidence-scroll-tour.tsx
一句话: 超出屏高的长截图页作为画面唯一动元素匀速上滚（约 10% 页高/s），预标注的红框/高亮随页滚动，讲到关键条目提前减速、停 1~2s 再滚完——滚速就是讲述节奏
适用: 口播出示文档/协议/README/搜索结果等长页证据、需要"我们从头看一遍，重点在这一条"的时刻；财经拆解、测评对比、事件梳理等冷静举证的调性
时长: 起手静置 0.6s → 缓入起滚 0.69s → 匀速慢滚（demo 2.5s，随页高）→ 提前 1.38s 减速、关键条目停在视口中线 1.5s → 再启动 0.69s → 匀速 1.5s → 收尾减速 1.38s 停在页尾；demo 全程 10.28s（加减速段 = 2×距离/速度，随 accelDist / decelDist / scrollSpeed 变）
能量: 低
类别: 素材呈现
输入: 截图, 人(可选)
语义: 例证, 引用, 强调
素材形态: 长图
位置: 中段
props: hostSrc
---

## 意图
口播念长文档证据时，逐段截图切页会打断"这是同一份文件"的连续感——把整页拉成一条长卷慢慢滚过去，
观众亲眼看到上下文完整、重点是从原文里"路过"时停下来看的，可信度远高于跳切。命门：
**页面是唯一动元素**（标注预先画好随页走，不现场画——现场画会分走视线，滚动的"巡览感"就没了）、
**匀速+关键处减速停留**（滚速对齐讲述节奏：匀速段是铺垫语速，停留段是"你看这一条"）、
**停留必须防死**（停 1~2s 里目标标注做连续呼吸，不是随机抖，也不是整帧冻结）。

## 动效核心
- 长页（2.5~4 屏高的文档/README/搜索结果截图）放进固定视口（可带极简窗口框示意"这是一份文件"），页面 `y` 是全卡唯一持续运动的属性
- 起滚：先静置 `startDelay` 0.6s 等口播开场，再 `power2.in` 缓入约 0.7s（= 2×accelDist/v）接上匀速（避免第 0 帧突然满速像 seek）
- 匀速段：`ease: none`，速度约 10% 页高/s（960×540 demo 里 130px/s；折算任何尺寸都以"观众能扫读小标题"为准）
- 预置标注：红框/下划线/色块直接画在页面元素上（`position:relative` 包裹 + 绝对定位框），随页滚动，无自身入场动画
- 减速停留：距停点提前 ~90px（约 1.4s = 2×decelDist/v）用 `power2.out` 减速，让目标条目停在**视口垂直中线**附近；停 1~2s 对齐台词"关键就在这条"
- 停留防死：目标红框 scale 1→1.03→1 一次完整呼吸（`sine.inOut`、yoyo，时长≈停留时长），连续缓动不抖动
- 再启动：`power2.in` 约 0.7s 加速回匀速，滚完剩余页面后以同样的 `power2.out` 减速停在页尾

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `scrollSpeed` | 130px/s（≈10% 页高/s） | 快了像在跳过证据、观众读不到小标题；<70px/s 铺垫段拖节奏，观众先于讲述读完 |
| `stopHold` | 1.5s | 停留时长对齐这句台词；<0.8s 观众没来得及聚焦，>2.5s 该切下一卡了 |
| `stopAlign` | 0.5（视口中线） | 目标条目停的位置；>0.7 沉在底部像没停到，<0.3 顶着窗框压抑 |
| `decelDist` | 90px | 减速提前量；太短像急刹（程序 seek 感），太长观众提前知道要停、悬念没了 |
| `accelDist` | 45px | 起滚/再启动的加速距离；0 会瞬间满速，读作跳变 |
| `breathScale` | 1.03 | 停留期红框呼吸幅度；>1.06 像警报闪烁，1.0 整帧冻结画面死 |
| `startDelay` | 0.6s | 起滚前静置一拍，等口播开场 |

## 已知坑
- 停留时现场画红框/划线——那是 scribble-annotation 卡的事；本卡标注必须预置随页走，现场画会夺走"页面是唯一动元素"的巡览感。
- 匀速直接急停、停完瞬间满速——速度阶跃读作程序 seek，不是"人拖着页面看到重点停下来"。
- 停留 1~2s 整帧完全静止——画面死掉，观众以为卡顿；防死靠标注连续呼吸，不靠随机抖。
- 滚速忽快忽慢或加手抖噪声——观众正在扫读，速度噪声直接造成晕动感。
- 页面不足 2 屏高——没有"长卷巡览"的信息量感，直接整页展示（media-pop-in）更诚实。
- 关键条目停在视口边缘——观众不知道该看哪一行，停留白停。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/evidence-scroll-tour.tsx——props：仅 `hostSrc`；长页内容与红框在 JSX 常量里，停点几何在 GEO 常量（vh 369 / pageH 1162 / boxTop 629.94 / boxH 30，demo 运行时测量后定值），换内容需改源码并重测 GEO。自包含单文件，复制进工程即可用；节奏参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/evidence-scroll-tour/index.html。换证据改 `.doc-page` 内文（红框停点是 `#stop-box`，任意换到别的句子上，停点位置运行时自动测量）；换标注色改 `.mark-box` 的 `border-color`；节奏全在顶部 `CONFIG`（`scrollSpeed` / `stopHold` / `stopAlign` / `decelDist` / `accelDist` / `breathScale`）。多个停点把"减速→呼吸→加速"三段照抄串联即可。
- Remotion 移植：把"位移-时间"曲线拆成分段 `interpolate(frame, [t0,t1,t2,t3,t4,t5]*fps, [0, -accelDist, -(stopY-decelDist), -stopY, -stopY, -(stopY+accelDist), -total])`，各段 easing 依次 `Easing.in(Easing.quad)` / linear / `Easing.out(Easing.quad)` / 常值（hold）/ `Easing.in(Easing.quad)` / linear；段时长按 `距离/scrollSpeed`（加减速段 `2*dist/v`）；呼吸用 hold 区间内的 `Math.sin` 单周期映射 scale。
- 剪辑软件对应物：剪映——长截图导入后打"位置"关键帧，匀速段两点线性、停点前后各加一个关键帧并对减速点右键"缓出"/启动点"缓入"；AE——Position 关键帧 + 停点两侧 Easy Ease（速度图里把停点速度拉到 0），红框呼吸用 scale 表达式 `1+0.03*Math.sin(...)`; CapCut 同剪映 keyframe 做法。

## 动效范围
- 属于本卡的：长页 `y` 轴匀速上滚（≈10% 页高/s、ease none）及其"缓入起滚→匀速→提前减速（power2.out）→停 1~2s→加速再启动（power2.in）→滚完"的完整速度曲线；停留期目标标注一次连续呼吸（scale 1→1.03→1、sine.inOut）；"标注预置随页滚动、不现场画"的原则。一条速度曲线 + 一个防死呼吸是本卡的全部。
- 不属于本卡的：页面内容与排版（demo 的假协议文档、灰阶占位条）、窗口框样式、字幕文案与切换、角标主持人；红框的绘制入场动画（现场画属 scribble-annotation）。
- 迁移接口：`scrollSpeed` 对齐讲述语速（换尺寸按页高比例折算）；停点=页内任一元素的位置（demo 运行时测 offset；tsx 写在 GEO 常量，换页面重测 boxTop / pageH）；多停点串联"减速→呼吸→加速"三段；标注色是单一 semantic 色 token（深色截图换高对比色）。
- 底色要求：白底即可（长页本身通常是浅色文档；深色终端/IDE 截图同样成立，仅需换标注色保证对比）。

<!-- ===== /file: video-talkcraft/references/cards/evidence-scroll-tour.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/filmstrip-conveyor.md ===== -->

---
name: filmstrip-conveyor
标题: 传送带列举 + 减速停靠
一句话: 六格 240×160 白边卡接成一条传送带匀速左行 176px/s，经过中线的格按"离中线的距离"每帧连续放大到 1.08 并提亮（不是到点触发）；讲到第四格时按位置-时间分段积分减速（匀速 → 0.5s 减速 → 0.25× 慢速 1.4s → 0.6s 加速 → 匀速），减速结束点正好是"第四格居中"；六格全部过完中线后整体退场
适用: 列举 ≥5 项且只有一项要重点说的段落——六种构图、十个 App、一年的作品、盘点 / 回顾 / 片尾作品流；"其中第 N 个最重要"就在第 N 格减速
时长: 7.9s（匀速 2.14 → 减速 0.5 → 慢速停靠 1.4 → 加速 0.6 → 匀速到第六格过中线 6.92 → 7.5 退场 0.4）；格数 / 关键格 / 停靠时长按口播改
能量: 中
类别: 素材呈现
输入: 图
语义: 例证, 列举
素材形态: 横屏, 多图
位置: 任意
props: srcs, labels, title, note
优先级: P1
代码: template/cards/filmstrip-conveyor.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| 不适用（格子 240 宽，人说话看不清；人用 D 组并列句卡） | tsx 的 `srcs` 仅走 `<Img>`；要每格放短视频（格子经过中线那 2~3s 是它的戏）按复用指引换成 `<OffthreadVideo>` | **默认输入**（≥5 张同尺寸的图；截图 / 封面 / 海报） |

格子同尺寸是硬要求（横竖混合统一裁到 3:2 外框，裁切不缩放）。少于 5 项别用传送带——三四项直接摆开（`hero-duo-layout` / 并列句卡），传送带的成本只在"多到摆不开"时划算。

## 常用场景
1. 列举 ≥5 项、其中一项重点讲：去年爆款封面的六种构图，讲到第四种减速（demo）
2. 回顾 / 盘点段落：今年做过的十个项目、读过的八本书，匀速流过
3. "其中第 N 个最重要"：关键项减速停靠 1.4s，其余只是经过
4. 片尾作品流：不减速，匀速走完即结束（把 `slowDur` 设 0）

## 意图
口播列举五项以上时，逐张弹出（`media-pop-in`）观众数不清，九宫格一次摆全又没有顺序。
传送带把"顺序"变成物理运动：素材从右往左流过中线，讲到哪个哪个正好在中间。做对的命门：
1. **放大 / 提亮按距离连续算**，不是"到中线那一刻触发"——每帧由 `|cx − 480|` 算权重 `k`，格子是渐渐变大变亮、再渐渐退回去，读作"经过"；到点触发会读作"闪一下"。
2. **减速是位置-时间的分段积分**，不是硬停——匀速 v → 0.5s 减速到 0.25v → 慢速 1.4s → 0.6s 加速回 v，各段端点速度相等；减速起点由"减速结束时关键格正好居中"反推。硬停读作"卡住了"，速度跳变读作"抖"。
3. **速度就是讲述节奏**：匀速段 = "还有这些"，慢速段 = "这个要说两句"；观众从速度变化就知道重点在哪，不需要额外标注。

## 动效核心
- 结构：`.hdr` 标题（26px 700 #1d1d1f，60/70 起，小注 14px #8a8a8a）→ `.center` 中线停靠区（280×200 虚线框，演示语境）→ `.strip`（`left: 0; top: 190; display: flex; gap: 24`，整条 `translateX(−x)`）→ 12 个 `.item`（240×160 白边卡 padding 6、圆角 10、投影 `0 12px 40px rgba(0,0,0,.16)`；后六格是前六格的副本，传送带右端不留空）；每格左下 14px 标签胶囊。
- 几何：格距 pitch = 240 + 24 = 264，一组 setW = 6 × 264 = 1584；匀速 v = setW / loopDur = 1584 / 9 = **176px/s**（≤220 上限；24fps 成片抖动先降到 ~150）。
- 位移曲线 `stripX(t)`（五段拼接，端点速度相等）：
  - 关键格（第四格，idx 3）居中时 `centerX = 3 × 264 + 120 − 480 = 432`
  - 减速段距离 `dDecel = v × 0.5 × (1 + 0.25) / 2 = 55` → 减速起点 `x0 = 432 − 55 = 377`，`t1 = 377 / 176 = 2.142s`
  - `t1–t2 (0.5s)` 减速：`x = x0 + dDecel × e↓(s)`，`e↓(s) = 1.6s − 0.6s²`（起速 v、末速 0.25v）
  - `t2–t3 (1.4s)` 慢速 0.25v：`dSlow = 61.6`
  - `t3–t4 (0.6s)` 加速：`dAccel = 66`，`e↑(s) = 0.4s + 0.6s²`（起速 0.25v、末速 v）
  - 之后匀速；第六格居中在 6.92s
  - 通式：`e↓(s) = 2/(1+r)·s − (1−r)/(1+r)·s²`，`e↑(s) = 2r/(1+r)·s + (1−r)/(1+r)·s²`，r = slowTo。实验室原型用 `power2.out/in` 配同样的距离，起速是 3v、末速 0，会在段接点跳速——入库版改成这两条速度连续的曲线。
- 逐格权重：`cx = −x + i × 264 + 120`（格中心屏幕 x），`d = min(1, |cx − 480| / 420)`，`k = (1 − d)²`；`scale = 1 + 0.08k`，`brightness = 0.5 + 0.5k`，`z-index = round(10k)`。
- 收尾（入库版，不无限循环）：`7.5s` 标题退 → `7.54` 传送带 + 停靠区退（`power2.in` 0.4s，错峰 0.04）→ `7.94` 结束。传送带在退场期间继续匀速走（持续运动的 duration = 镜头）。
- 一切状态由 `t` 纯函数算出（`stripX(t)` + `weight(i, x)`），HTML 与 tsx 同一条公式；demo 的 GSAP 只 tween 一个时钟 `o.t`，`onUpdate` 里算样式。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `loopDur` → v | 9s → 176px/s | 一组走完的时长定匀速；>220px/s 看不清格内容，24fps 先降到 ~150 |
| `slowIdx` 关键格 | 3（第四格） | 讲到第几格减速；减速起点由它反推，不用手算 |
| `slowTo` 慢速比 | 0.25 | 慢速段速度；0 = 硬停（读作卡住），>0.4 读不出"这个要说两句" |
| `decel` / `accel` | 0.5 / 0.6s | 减速比加速略短（"到了"比"走了"干脆）；<0.3 像刹车 |
| `slowDur` 停靠 | 1.4s | 成片 = 讲这一格的那句话；0 = 不减速的片尾作品流 |
| `maxScale` | 1.08 | 中线放大；>1.12 邻格被压、>1.15 出格 |
| `dimTo` | 0.5 | 离中线最远的亮度；白底上 <0.4 卡发灰、>0.7 读不出焦点 |
| `reach` | 420px | 权重影响半径；越小"聚光"越窄，<300 相邻格全暗像幻灯片 |
| `gap` / `w` | 24 / 240 | 格距 / 格宽；改了 pitch 全部几何随动 |
| `exitAt` | 7.5s | 第六格过中线（6.92）后 ~0.6s 退场；片尾作品流可延到副本走完 |

## 已知坑
- 到点触发放大（`if (cx ≈ 480) scale = 1.08`）——格子在中线"闪一下"，前后两帧跳变；必须按距离连续算。
- 减速做成 `timeScale` 降到 0 再回来（硬停）——读作"视频卡了"；慢速段速度必须非零。
- 减速 / 加速用 `power2.out/in` 配 trapezoid 距离——起速 3v、末速 0，段接点速度跳变，画面"顿一下"；用文中两条速度连续的曲线。
- 减速结束点没对齐关键格居中——观众看到的是"停在两格中间"，不知道在说哪个。
- 匀速给到 220 以上——格内内容读不清，只剩色块在飘；标签更是完全糊掉。
- 只放六格不接副本——第六格过中线时右侧空出白板，传送带的"无穷"暗示断了。
- 无限循环——demo 循环是预览便利，成片必须有限时长、退场与口播句尾对齐（2026-09-05 时长纪律）。
- 格子不同尺寸 / 横竖混排——传送带靠等距节律，一格高一格矮节律就散了；统一裁到 3:2。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/filmstrip-conveyor.tsx——`srcs`（六张真图，`<Img>` cover）、`labels`（六格标签）、`title` / `note`；节奏全在 `CONFIG`（改 `slowIdx` / `slowDur` / `loopDur` 时间表自动重算），`meta.durationInFrames = 250`；格数不是 6 时改 `CONFIG.n` 并把 `exitAt` 按"最后一格过中线时刻 + 0.6"重算。tsx 的 `srcs` 仅走 `<Img>`；要放视频把 `<Img>` 换成 `<OffthreadVideo muted>`（Remotion 自带；grid-to-hero.tsx 里有按后缀自动切换的现成写法），其余不动。
- HTML/GSAP：demos/filmstrip-conveyor/index.html——`.strip` 由脚本按 `CONFIG.n × 2` 生成，`.ph` 换 `<img>`，`NAMES` 换标签；核心可摘走：`CONFIG` + `stripX(t)` + `weight(i, x)` + `apply()`，四段代码进任何时钟驱动的环境都能用。
- 与 layout.md 的接口：标题距左 60 / 距顶 70（≥48）；传送带 y 190–350 居中线 270；格内标签 14px（=28@1080 最小可读档）；传送带两端出画是语义（"还有更多"），不算贴边。
- 剪辑软件对应物：剪映 / CapCut 把六张图排成一行合成后打"位置"关键帧（匀速段两个线性关键帧、减速段中间加两个关键帧再调曲线），中线放大靠每张单独的缩放关键帧（很费）；AE 是一个 Null 控制 Position + 每张的 scale/brightness 用表达式按 `Math.abs(thisLayer.position[0] − 960)` 算——就是本卡的 `weight()`。素材站叫 "filmstrip / carousel / conveyor belt showcase"。

## 动效范围
- 属于本卡的：传送带匀速 + 按位置-时间分段积分的减速停靠（五段拼接、端点速度相等、减速终点对齐关键格居中）；按"离中线的距离"每帧连续算的放大 1.08 / 提亮 .5→1 / 层级；六格 + 六格副本的传送带结构（右端不留空）；有限时长收尾（最后一格过中线后 ~0.6s 整体退场，错峰 0.04，退场期间传送带继续走）。
- 不属于本卡的：demo 的六张示意图（演示语境素材，demos/_lib/media，不属于本卡）、"构图 一~六"与标题小注文案、中线停靠区虚线框（演示语境，成片可去）、白边卡的具体圆角与投影值、白底舞台。
- 迁移接口：`srcs` / `labels` 换素材文案；`slowIdx` / `slowDur` 对齐口播（讲到第几格、讲多久）；`loopDur` 定匀速（24fps 成片放慢到 ~150px/s）；换画幅时 `w` / `gap` / `reach` 按画幅宽等比缩放，中线始终 = 画幅中心；竖屏可把传送带改成竖向（`translateY`，权重按 `|cy − H/2|`）。
- 底色要求：白底即可——白边卡靠投影分层，`dimTo .5` 在白底上读作"退到后面"；深底要把 `dimTo` 提到 .6 并加亮投影。

## 落位自检（2026-09-05 用户定版，选卡时抄进 SHOTBOOK 该镜自检列）
- **关键格居中**：把时钟冻在 `t2`（减速结束，demo 2.64s）截帧，关键格中心 x 与 480 偏差 ≤4px（否则 `centerX` 算错或格宽 / 格距与 CSS 不一致）。
- **速度连续**：`t1` / `t2` / `t3` / `t4` 四个接点前后各截一帧，位移差一致（无跳变）；肉眼看 `--play` 不许有"顿一下"。
- **渐变不跳变**：中线格与邻格的 scale / brightness 逐帧单调过渡（没有 `if` 阈值）。
- **可读**：匀速 ≤220px/s（24fps ≤150）、格内标签 ≥14@960、标题 ≥26@960；缩到 390 宽复看标签仍可读。
- **收尾**：`exitAt` ≥ 最后一格过中线时刻 + 0.4，且 ≤ 副本第二格过中线（否则观众看到"构图一"又来一遍）；退场与本镜结束对齐，不无限循环。

<!-- ===== /file: video-talkcraft/references/cards/filmstrip-conveyor.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/flying-words.md ===== -->

---
name: flying-words
标题: 关键词隧道
一句话: 深底上 22 个名词按黄金角铺在扁椭圆截面（半径 82~247）上，沿 z 轴从 −1750 匀速飞到 +800 穿过相机平面擦身而过，每词相位 i/N 均分、跑满 2 整圈首尾无缝；生命曲线 [0,1,.5,.2,0]——前 1/4 猛亮、中段压到半透给前景让位、末段拖尾消失；越近越往画外散（drift .5→1.85），冲到眼前（u>.86）加运动模糊；中心一枚静态光晕钉住"隧道尽头"。它是幕底级背景层，前景放人物或标题
适用: 名词科普片的开场底层（"这期讲的 22 个概念"）、片头片尾的"信息量"垫底、能力清单的动态背景（前景放人物或标题）、纵深穿越感的转场垫层；深底专用（白底整套失效）；一支片 ≤1 段
时长: 6.0s（0–0.6 整层淡入 → 匀速两整圈 → 5.5–6.0 整层淡出）；成片时长 = 镜头时长，圈数按时长取整数（每 3s 一圈）
能量: 中
类别: 字幕花字
输入: 文
语义: 氛围, 钩子
素材形态: 无
位置: 开场
props: words
优先级: P2
代码: template/cards/flying-words.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 本卡不吃人物，但前景可叠人物（它在 L5/L6 背景层） | ✗ | ✗ 只吃一张词表（12~30 个词） |

背景层卡：输出的是一层"会动的底"，前景（标题 / 人物 / 素材卡）由镜头另叠，落定即静的纪律作用在前景。

## 常用场景
1. 名词科普片的开场底层：22 个 AI 名词穿过镜头，前景标题"AI 名词，一次讲清"（demo 只演底，不放前景字——按用户要求）
2. 片头 / 片尾的"信息量"垫底：关键词飞过，前景是频道名或人物
3. 能力清单的动态背景："它会的这些事"在底层飞，前景逐条讲
4. 纵深穿越感的转场垫层：上一镜淡出、词隧道跑一圈、下一镜淡入

## 意图
"这期要讲很多概念"这句话本身没有画面。词云是常见解法但静态词云是 PPT，逐词弹入又太慢。让词**从远处飞向观众并擦身而过**，用纵深代替排版：观众不必读全每个词，只感到"很多、在涌来"。它是库里唯一的文字类背景层——不是标题的入场，是标题下面那层底。做对四条：
1. **终点必须过相机平面**（+800）：不过 0 只有"飞到脸前停住"，没有"擦身"。
2. **生命曲线中段 0.5 是给前景让位的**：一路满亮会抢前景；早早归零隧道变空。
3. **CYCLES 必须整数**：t=0 与 t=1 画面完全一致才能无缝 loop；非整数 loop 处一跳。
4. **深底专用**：深底浅字发光是本卡的身份证；白底套本卡直接失效（母本判例），要浅底得整套重配成深字 + 无光晕，那已是另一张卡。

## 动效核心
- **场景**（960×540）：`.fwd-scene` 全幅 `perspective 1100px`、origin 50% 50%、`overflow hidden`；中心光晕 220px 径向渐变 `rgba(120,150,255,.28)→0` + blur 6，**静态不呼吸**（运动做减法，母本呼吸 2 次已删）。
- **铺位**（每词 i）：角 `a = i·2.39996 + srand(i·7+1)·0.8`（黄金角避开正中），半径 `r = 82 + srand(i·11)·165`，y 半径 ×0.6 压成扁椭圆；字号 `20 + srand(i·3)·16`，色 `hsl(200 + srand(i·5+1)·130, 80%, 78%)`（蓝→紫）。`srand` = 正弦哈希，帧确定、demo 与 tsx 同公式。
- **推进**：`u = (t/dur·cycles + i/N) % 1`；`z = lerp(−1750, 800, u)`；`drift = .5 + u·1.35`；`x = cos(a)·r·drift`、`y = sin(a)·r·.6·drift`；`transform: translate3d(x,y,z) translate(−50%,−50%)`。
- **透明度**：分段线性 `OP=[0,1,.5,.2,0] @ OT=[0,.25,.6,.85,1]`。
- **近端糊化**：`u > .86` 时 `blur((u−.86)·26)px`（既是运动模糊也是遮丑）。
- **整层起落**：0–0.6s 淡入（power1.out）、5.5–6.0s 淡出（power2.in）；成片里若接前后镜可去掉起落直接交叠。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 词表 | 22 词，字号 20~36 / 800 | 词数与相位 i/N 绑定：<12 词画面稀，>30 词近处糊成一片；字号随机是层次感来源，全同号读作贴图 |
| `zFrom` / `zTo` | −1750 / +800，perspective 1100 | 起点更远词太小认不出；终点不过 0 没有"穿过去" |
| `drift0` / `drift1` | 0.5 / 1.35 | 系数 <1 词全从正中喷出像爆炸；>2 早早飞出画外，隧道变喷泉 |
| 生命曲线 | [0,1,.5,.2,0] @ [0,.25,.6,.85,1] | 中段 0.5 给前景让位；改成一路满亮就抢主角，早归零隧道变空 |
| `cycles` | 2（必须整数） | 非整数 loop 一跳；圈数越多单词过镜越快；成片按镜头时长每 3s 一圈 |
| `blurAt` / `blurK` | 0.86 / 26 | 阈值提到 0.95 巨大词硬边扎眼；系数 >40 末段成色斑 |
| 配色 | 蓝→紫浅字 + 蓝紫光晕 | 深底浅字发光是身份证；白底整套失效 |
| 光晕 | 220px、blur 6、静态 | 删了隧道尽头没有焦点，词像随机乱飞；母本的呼吸已按减法删除 |

## 已知坑
- 白底用本卡——浅字看不见、光晕无效；要浅底就不是这张卡。
- 前景不放东西——它是底，单独播 6s 观众不知道看哪（demo 例外，为了看清底本身）。
- 圈数非整数——loop 接缝一跳。
- 词表太长 / 字号全同——近处糊成一片 / 读作贴图。
- 给光晕加呼吸、给词加自转——违反运动减法；本卡的运动只有 z 推进这一条。
- 前景文字与飞过的词同色同号——分不出层；前景用白 / 更大字号 / 有底板。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/flying-words.tsx——`words` 一个 prop；durationInFrames 192；成片改 `CONFIG.dur = 镜头时长`、`cycles = round(dur/3)`。前景层在你的场景里另叠。
- HTML/GSAP：demos/flying-words/index.html——改 `WORDS` 与 `CONFIG`；`apply(t)` 是全部动画，可原样搬。
- 母本：video-shotcraft `flying-words`（22 词黄金角 3D 隧道 + 中心光晕呼吸）。口播化改造：词表中文、光晕改静态、去掉母本前景字、作为背景层入库。
- 剪辑软件对应物：AE 3D 图层 + Position Z 表达式 `linear(time, 0, dur, -1750, 800)` 逐词错相位 + Opacity 表达式分段；剪映无等价物（需预渲染成透明 webm 当背景素材）。
- 与 layout.md 的接口：背景层不占排版预算（cinematography §4.5 同屏主体组 ≤3 不计入）；前景照常守安全边与字幕带。

## 动效范围
- 属于本卡的：z 轴穿越 + 黄金角铺位 + 生命曲线 + 越近越散 + 近端糊化 + 整数圈无缝；中心静态光晕。
- 不属于本卡的：词表内容、前景的一切、深底的具体色值（`#1d1d1f` 是本库深底 token）。
- 迁移接口：`words`、`CONFIG.dur / cycles`；1080p 输出 zFrom/zTo/半径 ×2、字号 ×2、perspective 2200。
- 底色要求：**深底是成立条件**（demo 覆写舞台底色为 `#1d1d1f`，原因见意图第 4 条）；浅底片子不用本卡。它是背景层，前景落定即静的纪律不受它影响。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- 任一帧：至少 6 个词 opacity >0.3（隧道不空）；同时没有词 opacity >0.55 且 z >600（近处不遮前景）。
- t=0 与 t=dur 两帧词位置一致（整数圈判据）。
- 前景标题 / 人物在场时，前景与飞词层级分明（前景白 / 更大 / 有底板），字幕带 y≥450 内飞词不影响字幕可读（字幕带上加 scrim）。
- 光晕全程不变（无呼吸判据）。
- 本卡在 SHOTBOOK 记作 L6 环境层，不计入同屏主体组。

<!-- ===== /file: video-talkcraft/references/cards/flying-words.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/focus-dim-spotlight.md ===== -->

---
name: focus-dim-spotlight
标题: 聚焦压暗切换
优先级: P0
代码: template/cards/focus-dim-spotlight.tsx
一句话: 讲到哪里哪里亮——目标行/卡片保持原亮并点亮发光描边，其余整屏压暗 40%，焦点随口播 0.2s 滑到下一目标，讲完整体 0.4s 恢复
适用: 口播出示表格/清单/代码/多卡版面，逐项讲"这一行→下一行"的时刻；也用于整屏退让给一句结论。财经财报拆解、AI 工具演示、评测参数对比等信息密度高、需要"我说到哪你看哪"的冷静调性
时长: 起手静置 0.45s → 焦点建立 0.3s（压暗缓入 + 描边撑开同帧）→ 首目标停 1.25s、其余各停 1.0s、焦点跳转 0.2s（可连续 N 次）→ 描边退、窗口撑到整卡 0.45s 停 1.5s → 整体恢复 0.4s；四目标一段 7.95s
能量: 低
类别: 强调标注
输入: 截图, 人(可选)
语义: 强调, 数据
素材形态: 无
位置: 中段
props: hostSrc
---

## 意图
表格/清单/多卡版面上同时有十几个数字，口播念到第三行时观众还在第一行——聚焦压暗把
"视觉权重"整块搬到目标上：目标不动、不放大、不加色，**只是周围全暗下去**，观众
无从选择只能看那一行。它和荧光笔的分工是尺度：荧光笔在**一行文字内**画重点（笔触、
色块、行级），本卡在**版面尺度**上切焦点（一整行 / 一张卡 / 一个区域，靠明度差而非涂色）。
命门：**目标本身零改动**（一压暗就想给目标加放大加换色，三件套一起上就成了 PPT 强调预设，
本卡的力量全在"其余变暗"这一个动作上）、**焦点是滑过去的不是切过去的**（0.2s 位移让
观众眼睛跟得上"从上一行到这一行"，硬切等于每次重新找目标）、**讲完必须整体恢复**
（暗着不收观众会以为画面就是这么暗的，聚焦感只在"暗-亮"的对照里成立）。

## 动效核心
- 结构：一个**聚光窗口**元素浮在内容之上，用超大 spread 的 `box-shadow: 0 0 0 9999px rgba(0,0,0,dimTo)`
  把窗口以外的整屏压暗（容器 `overflow:hidden` 裁掉溢出）；移动/缩放这个窗口 = 焦点跳转，
  非目标区暗度自动跟着换。目标本身**不改任何属性**
- 目标矩形：demo 运行时测量（`getBoundingClientRect` 换回设计坐标）；tsx 写成 `TARGETS`（四行）/ `WIDE`（整卡）常量，换目标改常量
- 通道①**压暗**：非目标区 `dimTo` 0.35~0.45（白底）暗度蒙层 0.3s `power2.out` 缓入
- 通道③**描边**：目标被圆角发光框圈住——`opacity 0→1` + `scale 0.95→1` 撑开，0.3s `power3.out`，
  外挂一层 `box-shadow` 辉光单独做 `sine.inOut` yoyo 微脉动（半周期 1.6s，防死、不是闪烁）；其余仍压暗
- 两通道**可叠**：①是底座，③叠在①上（demo 与 tsx 都是 ①+③）；收束段只留 ①（描边退场、窗口撑到整卡）
- 焦点跳转：窗口与描边框**同一条 tween** 同步位移+改尺寸，0.2s `power2.out`，可连续 N 次
- 尺度可变：同一个窗口从"一行"形变到"整张卡"只是改 width/height（0.45s `power2.out`）——
  焦点从局部放大到版面，用来收束"四行放在一起看"的结论句
- 收尾：描边在窗口撑到整卡那一刻 0.25s 退场（此后只剩压暗）；讲完蒙层 `opacity → 0` 0.4s `power2.out` 整体恢复
- 字幕/花字层在蒙层**之上**（`z-index` 高于聚光窗口）——字幕是叙述层，不参与被压暗

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `dimTo` | 0.40（白底）/ 0.20~0.25（深底） | 非目标区暗度；<0.25 在白底上几乎看不出压暗、强调失效，>0.55 上下文变成一整块黑、观众想回看读不到 |
| `dimIn` | 0.30s | 蒙层缓入；<0.15s 读作切黑闪一下（像掉帧），>0.5s 焦点来得比语音晚、跟不上台词 |
| `jump` | 0.20s | 焦点跳到下一目标；0（硬切）观众每次要重新找目标，>0.4s 焦点在半路时台词已经念完了 |
| `hold` / `firstHold` | 1.0s / 1.25s | 每目标停留，对齐这一行的台词（首目标多停一拍，观众要先认出整张表）；<0.7s 只够扫一眼读不到数字，>2.5s 该切下一卡了 |
| `ringFrom` | 0.95 | 描边撑开的起始倍数；1.0 读作贴上去的静态框，<0.85 变成弹框入场、抢戏 |
| `glowHalf` | 1.6s | 辉光脉动半周期；<0.8s 读作报警闪烁，脉动幅度为 0 则长停留时画面死 |
| `morph` / `wideHold` | 0.45s / 1.5s | 行级焦点 → 整卡焦点的形变与整卡停留，收束"四行放在一起看"的结论句 |
| `restore` | 0.40s | 整体恢复；不恢复观众会把压暗当成画面底色，聚焦感事后归零 |

## 已知坑
- 压暗的同时给目标加放大 / 换色 / 加投影——三件套一起上就是剪映"强调"预设，本卡的克制感尽失；**目标零改动**是本体纪律。
- 焦点硬切（`jump = 0`）——每次跳转观众都要重新在版面里找目标，等于每行都从头聚焦一次。
- 蒙层压得太黑（>0.55）——上下文被"删掉"，观众失去对照能力，反而想回看却读不到（同 highlighter-sweep 的 `dimTo` 坑）。
- 讲完不恢复——暗态成了新的常态，下一次聚焦没有对照、读不出"这里亮了"。
- 字幕/花字被一起压暗——叙述层跟着变灰，观众以为是渲染错误；字幕必须在蒙层之上。
- 发光描边用纯色硬框无辉光、或辉光做成闪烁——前者读作表单 focus 状态（浏览器 outline 感），后者读作报警；要的是连续呼吸的"点亮"。
- 描边框贴着目标边缘零留白——框压在文字/卡片边线上读作选中态；左右内缩到内容盒、上下外扩 3px 左右。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/focus-dim-spotlight.tsx——props：仅 `hostSrc`；数据表内容在 JSX 常量里、焦点矩形在 TARGETS / WIDE 常量里，换内容需改源码。自包含单文件，复制进工程即可用；节奏参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/focus-dim-spotlight/index.html。换目标改 `.trow.data` 选择器（矩形运行时测量，坐标不用改）；换聚焦几何改 `focusInsetX` / `focusPadY`；节奏全在顶部 `CONFIG`（`dimIn` / `jump` / `hold` / `restore`）；焦点色一个 CSS 变量 `--focus`；暗度 `dimTo` 直接写进 `.spot` 的 `box-shadow` spread 色值。核心可摘走部分 = `CONFIG` + `DemoShell.register` 回调体（含 `rectIn` / `focusBox` 两个测量函数）。
- Remotion 移植：聚光窗口用一个绝对定位 div，`boxShadow: \`0 0 0 9999px rgba(0,0,0,${interpolate(frame,[d,d+dimInF],[0,dimTo])})\``（外层 `overflow:'hidden'`）；焦点跳转把 `left/top/width/height` 各自 `interpolate(frame, [t,t+jumpF], [from, to], {easing: Easing.out(Easing.quad)})`，目标矩形在构建时静态算好（Remotion 无外壳缩放，直接写设计坐标）；描边 `scale: interpolate(..., [0.95,1], {easing: Easing.out(Easing.cubic)})`；辉光脉动 `opacity: 0.35 + 0.65*(0.5+0.5*Math.sin(frame/fps*Math.PI/glowHalf))`。
- 剪辑软件对应物：剪映——新建黑色色块铺满画面、不透明度 40%，加"蒙版→矩形"并**反转蒙版**，蒙版位置/大小打关键帧即焦点跳转；发光框用"边框"贴纸或矩形描边素材 + 发光滤镜；AE——黑色 Solid + Mask（Mode 设 Subtract）、Mask Path 关键帧移动，或 Set Matte；发光框用 Shape Layer 描边 + Glow 效果，Opacity 表达式做呼吸；CapCut——同剪映的 inverted mask keyframe 做法。

## 动效范围
- 属于本卡的：聚光窗口以外整屏压暗至 `dimTo`（0.3s 缓入 `power2.out`）；焦点在目标间**同步位移+改尺寸**跳转（0.2s `power2.out`，可连续 N 次）；目标发光描边亮起（`opacity 0→1` + `scale 0.95→1`、0.3s `power3.out`）与辉光 `sine.inOut` 微脉动（半周期 1.6s）；焦点从"行"形变到"整卡"的尺度切换（0.45s）；讲完整体恢复（0.4s，描边先于蒙层退场）；两通道（压暗 / 描边）的组合纪律（①是底座、③叠①）；**目标本身零改动**与字幕层不被压暗这两条硬约束。
- 不属于本卡的：demo 里的灰阶数据表卡（排版、字号、假数据）、角标主持人（数字人是演示语境素材）、示例台词与字幕切换、右上角"通道①/③"注记、`--focus: #ffb020` 这个具体焦点色、卡片圆角与边框样式。
- 迁移接口：`dimTo` **随底色明度取值**（白底 0.4 / 深底 0.2~0.25，深底压暗过头会糊成一片黑）；焦点色一个 token `--focus`（深底换高明度色）；目标 = 坐标矩形（tsx 的 TARGETS / WIDE 常量；demo 运行时测量）；`jump`/`hold` 对齐词级语音时刻；换尺寸时描边线宽与圆角、`focusInsetX`/`focusPadY` 按画幅等比缩放，`9999px` spread 无需改（只要容器裁剪）。
- 底色要求：白底即可（压暗蒙层在浅底对比最强，是本卡最自然的场景）。深底截图/终端画面同样成立，但 `dimTo` 必须减半、焦点色换高明度值，否则暗区与暗底并成一块、焦点无处可寻。

## 落位自检（2026-09-05 用户定版，选卡时抄进 SHOTBOOK 该镜自检列）
- 标注几何（框 / 圈 / 线 / 箭头 / 放大镜锚点）一律由**目标的实测包围盒**反推——DOM `getBoundingClientRect` / `measureText`，四边留白 16~24px 等距，**不目测**。
- 实现后抽该镜定妆帧核对：标注是否恰好套住 / 指向目标，偏差 **> 8px 返工**（`references/layout.md` §3）。
- 目标会滚动 / 移动时，标注钉在内容坐标系随内容动（SKILL.md ③）。

<!-- ===== /file: video-talkcraft/references/cards/focus-dim-spotlight.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/gallery-wall-dolly.md ===== -->

---
name: gallery-wall-dolly
标题: 照片墙推轨
一句话: 三张平级案例（430×290）挂在 rotateY −12° 的 3D 墙上（深灰径向幕底 + 地面反光），相机全景 z .61 → 逐张推近停靠 z 1.15（移 1.0s + 停 0.9s；缩放绕当前图发生，其余压暗 .5 + blur 3px，当前图内部 1→1.03 微推）→ 拉回全景与字同收
适用: "接下来三个例子一个一个看"、作品集 / 案例集巡览、三个方案巡完再拉回比较；三个**平级**的东西（有先后关系的几站用 timeline-photo-strip）；口播逐个讲、讲完还要看全貌的段落
时长: 8.2s（全景 0.8 → 三站各 1.0 + 0.9 → 拉回 1.2 → 退场 0.4）；成片站数与停靠按口播改，hold = "讲这一张要几秒"
能量: 中
类别: 素材呈现
输入: 图
语义: 例证, 对比, 列举
素材形态: 横屏, 多图
位置: 中段
props: srcs, labels
优先级: P1
代码: template/cards/gallery-wall-dolly.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| 不适用（人在场用 D 组并列句卡 `parallel-items-with-host`） | tsx 的 `srcs` 仅走 `<Img>`；要每站放短视频（停靠那 0.9s 是它的戏；混放时统一到同一外框比例，裁切不缩放）按复用指引换成 `<OffthreadVideo>` | **默认输入**（三张同尺寸；wall 是"三个平级案例"） |

## 常用场景
1. "接下来三个例子一个一个看"：三张代表作挂墙逐个停靠再拉回比较（demo）
2. 作品集 / 案例集巡览：三件作品各停一拍，拉回时观众看到它们并排
3. 三个方案巡完再比较：先各看一遍再回全景，由口播下结论
4. 三个功能 / 三个证据截图：平级关系、彼此不分先后

## 意图
口播"一个一个讲"几张图，最省事的做法是逐张全屏切——但观众看完不知道它们的关系。把三张图挂进一面有空间关系的 3D 墙，让相机去巡，
观众同时得到"逐个看"和"它们并排挂着"两层信息。做对的命门：
1. **相机层是唯一被 transform 的元素**：`transform-origin: 0 0`，每一站用 `camTo(z, px, py)` 反解出 `scale / x / y` 把目标点搬到画心——**缩放绕当前图发生**。用固定原点 + 位移去凑，zoom 变化时会甩出横向漂移，读作"镜头在找东西"（`stage-keyframe-tour` 同一条纪律）。
2. **停靠段真静止，但当前图内部微推**：本卡是停靠类（`stage-keyframe-tour` 例外），相机在 hold 里不续走；防死的责任交给当前图内部 1→1.03 的微推——画面每帧都在变，但"停下来看这一张"的语义不被破坏。
3. **巡完必拉回全景**：观众刚看了三处细节，需要一眼知道它们在整体里的位置；拉回后的照片退场与字同收。

## 动效核心
- 结构：`.world`（`perspective: 1200px; perspective-origin: 50% 50%`，深灰径向幕底）→ `.cam`（相机层，`position: absolute; inset: 0; transform-origin: 0 0; preserve-3d`）→ `.wall`（1700×540，`rotateY(−12°)`，`transform-origin: 850px 270px`，含 `.floor` 地面反光 `rotateX(80°)`）→ 三张 430×290 白边卡（padding 10、圆角 12、投影 `0 12px 60px rgba(0,0,0,.22)`，内部 `.frame` 裁切 + `.ph` 素材）在 `left 140 / 640 / 1140, top 125`（中心 x 355 / 855 / 1355，y 270）。
- `camTo(z, px, py) = { scale: z, x: 480 − z·px, y: 270 − z·py }`——相机层不是满铺素材、底是静态幕底，无"露边"问题，故不像 `slow-push-in` 那样钳制。
- 因为墙绕 x=850 转了 −12°，停靠目标用**旋转后的坐标** `wallX(cx) = 850 + (cx − 850)·cos12°`，否则每站偏心 11~14px。全景 `camTo(.61, 942, 270)`：透视下近端更宽，.61 时三张投影两侧各留 53px，目标 x 942 由投影包围盒居中解出（实验室 .72 / 850 会切掉第三张）。
- 时间表：`0–0.8` 全景 → 每站 `move 1.0s power2.inOut` 到 `camTo(1.15, wallX(cx), 270)` + `hold 0.9`（其余照片从移动 0.5s 起 0.5s 内 `brightness .5 + blur 3px`；当前照片 `.ph` 从移动 0.7s 起 1.2s 内 `scale 1→1.03` linear）→ `6.5–7.7` 拉回全景（6.8 起 0.6s 全部复原）→ `7.7` 照片退场 0.4（错峰 0.04）→ `8.2` 结束。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `stopZ` 停靠焦距 | 1.15 | 放大 ≤1.2；<1.05 读不出"停下来看这一张" |
| `wideZ` / `wideAt` 全景 | .61 / 942 | 全景要装下三张且两侧 ≥48；有透视，近端更宽——改墙角就重解 |
| `move` 站间移动 | 1.0s | <0.7 读作"甩过去"（转场语气），>1.5 观众等它到位 |
| `hold` 停靠 | 0.9s | **信息在 hold 里**；成片按"讲这一张要几秒"给；<0.6 白跑一趟 |
| `dim` / `blur` | .5 / 3px | 其余照片的降权；景深虚化是"近处清远处糊"的空间暗示 |
| `push` | 1.03 | 停靠段当前图的防死微推；>1.05 读作第二次推镜 |
| `pull` 拉回 | 1.2s | 比单站移动略长（跨的距离更远） |
| `wallRy` | −12° | 3D 墙倾角；≤25° 才可读；换角度要重解 `wideZ` / `wideAt` |

## 已知坑
- 用固定 `transform-origin`（center）+ 位移凑停靠——zoom 变化时甩出横向漂移，"镜头在找东西"；每站的目标必须反解到画心。
- 用未旋转的照片中心当目标——墙转了 −12°，投影中心偏 11~14px，每站都停偏一点；用 `wallX()` 旋转后坐标。
- 全景照抄 .72——透视下近端更宽，第三张被画幅切掉；全景焦距要按投影包围盒解，不按平面尺寸。
- 停靠段相机续走（套 `camEase` 末速非零）——本卡是停靠类，续走会让"停下来讲这一张"变成"路过"；防死交给图内微推。
- 停靠段什么都不动（无微推）——0.9s 全静止，观众以为卡帧（motion_check 也 FAIL）。
- 不拉回全景就收——观众看完三处不知道它们在整体的什么位置，巡游读作三个不相干的特写。
- 白底上用 3D 墙——rotateY 的照片像浮着的纸片，其余照片的压暗 / 虚化在白底上成灰片（见底色要求）。
- 有先后关系的几站硬套本卡——"三个平级"和"先后几站"语法不同，先后用 `timeline-photo-strip`。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/gallery-wall-dolly.tsx——`srcs` 三张真图、`labels` 压图标签；时长 258 帧（8.2s + 0.4s），导出的 `END` 是动画结束秒；站数不同时改 `CONFIG.centers`（同时改照片 `left`）、hold 要长改 `CONFIG.hold`。tsx 的 `srcs` 仅走 `<Img>`；要放视频把 `<Img>` 换成 `<OffthreadVideo muted>`（Remotion 自带；grid-to-hero.tsx 里有按后缀自动切换的现成写法），其余不动。
- HTML/GSAP：demos/gallery-wall-dolly/index.html——`CONFIG` 是全部节奏；`.ph` 整块换 `<img>`，`.tag` 换文案；核心可摘走：`CONFIG` + `camTo()` + `wallX()` + 时间轴。
- 与 `timeline-photo-strip` 的边界：那张是有先后的几站沿时间线横移；本卡是平级的三张挂墙——先定关系再选卡，两张不在一镜里连用。
- 与 `stage-keyframe-tour` 的边界：那张是一张超出画幅的长页 + 多关键帧兴趣点巡游；本卡是**多张独立素材**挂在世界里 + 相机层 `origin 0 0` 反解，相机纪律同源、素材形态不同。
- 与 layout.md 的接口：全景三张两侧 ≥48（实测 53）、tag 20px（停靠时 23 ≈ 46@1080）。
- 剪辑软件对应物：AE 把三张图摆进一个合成（3D 图层 + 摄像机），给摄像机 Position / Zoom 打关键帧、每站两个同值关键帧构成 hold，Easy Ease 后把手柄拉成 inOut。素材站叫 "gallery wall dolly"。
- 音效：每段相机起步一记 `pk:counter-clock-tick-single`（vol .4，clip ~1），拉回一记压低的 `pk:transition-air-whoosh-powerful`（vol ≤.3）；**hold 段绝对不给声**。

## 动效范围
- 属于本卡的：相机层 `origin 0 0` + `camTo` 反解到画心的巡览停靠结构（每站缩放绕当前图发生）；"全景 → 移动 power2.inOut → 真静止停靠 → 下一站 → 拉回全景 → 与字同收"的节拍（1.0 + 0.9 / 拉回 1.2）；停靠段当前图内部 1→1.03 微推 + 其余压暗 .5 + blur 3 的焦点处置；3D 墙（−12°、透视 1200、地面反光、旋转后坐标 `wallX`、按投影包围盒解全景）。
- 不属于本卡的：demo 的示意图（演示语境素材，demos/_lib/media，不属于本卡）、"案例一~三"文案、白边卡的具体圆角 / 投影值、幕底的具体色值。
- 迁移接口：`srcs` / `labels` 换素材文案；`hold` 对齐口播；站数改 `centers`（+ 照片 `left`）；换画幅时几何按 960×540 等比缩放，`camTo` 里的 480 / 270 换成新画心。
- 底色要求：**需要深灰径向幕底**（`radial-gradient(ellipse at 50% 40%, #26262e, #0f0f13 75%)`）——3D 墙上的白边照片靠深底 + 地面反光才读出"挂在墙上"。浅底风格档的片按 design-language §0.4 换成同风格的深 tile 幕。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- **停靠居中**：每站 hold 中段截帧，当前图中心与画心 (480, 270) 偏差 ≤8px（偏 >8 通常是没用 `wallX` 旋转后坐标）。
- **全景装得下**：全景帧三张两侧 ≥48（实测 53）；改墙角后重解 `wideZ` / `wideAt`。
- **hold 真静止 + 微推在走**：hold 段相机 transform 逐帧相等；当前图 `.ph` scale 在 1→1.03 单调走。
- **字号**：tag ≥20@960（缩到 390 宽复看仍可辨）。
- **有拉回**：时间表末尾有拉回全景，退场与本镜结束对齐。

<!-- ===== /file: video-talkcraft/references/cards/gallery-wall-dolly.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/glass-code-walk.md ===== -->

---
name: glass-code-walk
标题: 玻璃代码走读
优先级: P1
代码: template/cards/glass-code-walk.tsx
一句话: 玻璃质感代码块弹入、10 行代码逐行落位，相机推到 1.68x 后按「读一行 → 滑到下一行」逐句走读（浮点行号 linePosition 同时驱动相机与高亮带，行间是滑过去的不是跳格），非当前行压暗到 0.30，读完 0.85s 拉回全景解除压暗
适用: 口播里带观众读一小段真实代码/配置——技术教程、代码讲解、开源项目介绍、"这几行就是关键"的时刻；6~10 行、每行都值得念一句的量
时长: 块弹入 0.55s → 逐行落位 1.0s → 推近 0.55s → 走读 9 句（每句 dwell 0.32s + 滑 0.26s）→ hold 0.30s → 拉回 0.85s → 尾 0.5s；demo 全程 8.24s。行数变化按「行数 × 0.58s」加减
能量: 中
类别: 素材呈现
输入: 界
语义: 例证, 强调
素材形态: 界面
位置: 中段
props: hostSrc
---

## 意图
口播讲代码有两个死角：贴一整屏代码，观众眼睛不知道该落在哪儿，你念到第 5 行时他还在读第 1 行；
只贴关键那两行，观众看不出它们在什么结构里。本卡是这个死角的解法——**代码整块都在，但同一时刻只有一行是亮的**。
观众的视线被那条高亮带牵着走，节奏由你定；周围的行压暗但没消失，结构感一直在。

命门有三条。**第一条是浮点行号**：`linePosition` 是浮点数，相机与高亮带都由它现算，
所以走读第 2 行到第 4 行时它连续走过 2.0 → 4.0，带子在行间**滑过去**。
一格一格跳的高亮是"程序在切 class"，滑过去的才是"眼睛在移动"。
**第二条是停顿式而不是匀速**：每行停 `dwell` 再滑 `stepDur` 到下一行。匀速滑动的传送带读作"代码在自动播放"，
观众会等它播完而不是听你讲；停顿式才是"我念完这句了，看下一句"。
**第三条是收全景**：观众跟着走完 8 句，眼里只有片段，需要一眼看到整段代码长什么样。
拉回 `zoom = 1` 同时解除压暗——从"读这一行"回到"读整体结构"，不收这一拍等于没讲完。

玻璃块本身是**手段不是目的**：半透明深底让语法色成立（浅玻璃上 token 色一律糊成粉笔字），
backdrop blur 把背后的东西揉开、块内块外能看出同一片背景的两种状态——这是"玻璃"读得出来的唯一证据。

**源码原始视觉（2026-08-25 用户定版：放弃改编，按 remocn 源码原样实现）**：玻璃块的全部视觉取值
1:1 照抄 `glass-code-block`——`rgba(10,10,10,0.6)` 玻璃底 + `blur(16px)`、1px 渐变描边、
`0 50px 120px rgba(0,0,0,.55)` 投影、40px chrome + macOS 三灯真色（`opacity .6`）+ `#a1a1aa` 标题、
28px 行号槽 `#3f3f46`、五个 token 色（`#e4e4e7` / `#52525b` / `#86efac` / `#c4b5fd` / `#fcd34d`）。
舞台底也按源码的 `previewBackdrop`（一张暖褐→墨绿的暗调照片 `/bg.jpg`）复刻——demo 禁外网资源，
所以用 CSS 渐变还原那张图的色调分布。这也解决了改编版要靠"三团灰阶软斑"硬凑玻璃背景的问题：
**源码本来就是深色照片背景，玻璃有真东西可糊。**

## 动效核心
- 结构两层：`.camera`（铺满舞台的世界坐标层，`transform-origin: 0 0`，全卡唯一被 transform 的元素）→ 玻璃块（世界坐标里位置固定）。动的只有相机 + 高亮带 + 各行的 opacity
- **`transform-origin: 0 0` 是反解式子成立的前提**。默认 `center` 会让 `scale` 绕元素中心发生，整条式子失效
- **核心反解**：`tx = W/2 − zoom·cx`、`ty = H/2 − zoom·cy`、`scale = zoom`。含义是"把锚点的缩放后位置搬到画面正中"
- **锚点纵向由浮点行号插值算出**：`linePosition` 在相邻行之间连续（`lo = floor(p)`、`hi = lo+1`、按 `p − lo` 线性混合两行的行心 y）。
  行心由行高常量静态算出（正常行 26、空行 14、行距 4：`ROW_TOP[i] + ROW_H[i]/2`；demo 从 DOM 现量）——换行数/空行自动跟上；换字号要同步改这三个常量
- **横向恒取块心，不跟字符**：读代码是**整行读**。这是与 [cursor-locked-zoom](cursor-locked-zoom.md) 的第一个分界（那张锁 x 到字符光标）
- **高亮带与相机同源**：带子的 `top`/`height` 也由同一个 `linePosition` 插值出来（`trackedRow()` 一次返回 y / top / h 三个值）。
  同源 ⇒ 只有一条时间轴在推进，两者不可能失步。给带子单独排一条 tween 去"追"相机，任何时长改动都会错开
- **压暗是连续量不是二值**：`near = max(0, 1 − |i − linePosition|)`，离当前行越远越暗。
  带子滑到两行之间时上下两行**同时半亮**，这一拍读作"正在挪"；二值切换（只有整数行才亮）会让"滑动"退化成"闪"
- **走读只停在有内容的行上**：空行是排版不是一句话，`stops` 数组把空行过滤掉。但插值仍然经过空行（`linePosition` 是连续的），所以跨过空行时带子平滑掠过它
- **停顿式节奏**：`dwell 0.32s` 停 + `stepDur 0.26s` 滑（`power2.inOut`——两端都收，一次"跳行"是有始有终的事件）
- **边界钳制（白底舞台的必需补丁，源码没有）**：`半宽 = W/(2·zoom)`，`cx = clamp(cx, 块左 + 半宽, 块右 − 半宽)`，纵向同理；素材比可视区小时退化为居中。
  **块宽必须大于走读焦距下的可视宽**（960 / 1.68 ≈ 571px，所以 demo 取 600px）——否则横向钳制退化为居中、画幅两侧露出白舞台细边
- **收尾只 tween `zoom` 与 `dimAmt` 两个值**：`zoom` 变小 ⇒ 可视矩形变大 ⇒ 钳制范围收窄 ⇒ 中心被连续挤回块正中；`zoom = 1` 时块比画幅小、钳制退化为居中 ⇒ 恰好落在全景居中。位移不用第二条 tween
- 入场两拍：块 `y 16→0` + `scale 0.965→1`（`back.out(1.3)` 微过冲）、淡入是**独立时间窗**（位移先动、透明度后跟，remocn 全系入场的写法）；随后逐行 `y 6→0` + 淡入、行距 0.08s（源码 `staggerFrames 10` 帧 ≈ 0.33s，本卡收紧到 0.08s——10 行铺完只花 1.0s，不占口播时间）
- **行必须是 block 不是 flex**：flex 容器会丢掉纯空白的匿名子项 ⇒ token 之间的空格与行首缩进全部消失（`export function` 挤成 `exportfunction`）。这是实测踩到的坑
- 语法色只给四个锚点（关键字紫 `#c4b5fd` / 字符串绿 `#86efac` / 数字黄 `#fcd34d` / 注释灰 `#52525b`，普通码 `#e4e4e7`），极简正则分词，不是真高亮器（不属于本卡动效，但取值锁在源码 `TOKEN_COLORS`）
- **字号由块宽反推，不是审美选择**：块宽 600 是 `zoom 1.68` 下的下限（960/1.68 ≈ 571 + 余量），可用文本宽 = 600 − 2×24 padding − 28 行号槽 = 524px；等宽字符宽 ≈ 0.6em ⇒ 最长行 49 字符时 `fs ≤ 17.8`，取 **17px**（行高 26 = round(17×1.55)、空行 14 = 17×0.8）。源码是 880 宽 @18px，本卡块窄了 280px，**字号必须跟着收，否则行尾溢出块外**（实测踩到：18px 时 import 那行的右引号被切在块外）

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `zoom` | 1.68（范围 1.5~1.8） | 走读焦距。**整行必须完整在画幅内**——这是"走读"与 deep-zoom 的硬分界；>2 行尾被裁，观众读半句；<1.4 放大等于没放，压暗一个人在干活 |
| `dwell` | 0.32s | 每行停留（读这一行的时间）。按口播语速给——他念完一句你才滑走；<0.2s 观众来不及看清就被拖走，>0.6s 带子像卡在那儿 |
| `stepDur` | 0.26s | 行间滑动。<0.15s 读作跳格（浮点插值白做了），>0.45s 每次跳行都要等，8 句累计多出 1.5s |
| `dimFloor` | 0.30 | 非当前行的压暗底。0 = 只剩一行可见（结构感全丢，那不如只贴那一行）；>0.55 看不出在走读 |
| 行数 | 6~10 行 | <5 行不需要走读（一屏读得清，直接给全景 + 一次 [slow-push-in](slow-push-in.md)）；>12 行走读时长超过 8s，观众走神 |
| 行宽 vs 字号 | 见上 | **改块宽/焦距/行宽任一项都要按 `可用文本宽 ÷ (最长行字符数 × 0.6)` 复算字号**——这是本卡唯一的硬耦合 |
| 行宽 | ≤ 49 字符 | 600px 块 @17px 等宽的上限（见上面的反推式）；折行会让行高不齐、行心插值跳一下 |
| `pushDur` | 0.55s | 全景 → 走读焦距的推近（同时压暗、带子显形）。<0.3s 读作硬切，>0.9s 观众等它推完 |
| `holdEnd` | 0.30s | 最后一行读完的停留。给"这句念完了"一个句读；0 = 读完立刻被拉走 |
| `pullDur` | 0.85s | 拉回全景。<0.5s 读作"弹回去"；>1.2s 观众以为还有下一处要看 |
| `lineIn` | 0.08s | 逐行入场间隔。>0.15s 铺完 10 行要 1.5s，口播白等；0 = 整块一起亮，"逐行落位"这拍没了 |
| 块 backdrop blur | 16px（源码值） | 玻璃的 backdrop blur。<8px 玻璃读作"半透明色块"；>26px 背后的背景糊成均匀灰，玻璃感反而消失 |

## 已知坑
- **字号与块宽的可算式**（2026-08-27 实战补）：卡里那条"字号与块宽是硬耦合"给个式子——
  `字号 ≤ (块宽 − 左右 padding) ÷ zoom ÷ (最长行字符数 × 0.6)`，且**中文字符按 1.0 而不是 0.6 计**
  （带中文注释的行往往就是最长行）。实测 900px 块 / zoom 1.6 / 21px 会把 44 字符的 import 行切在块外。
- **高亮带用整数行号切 class**——一格一格跳，读作"程序在切样式"不是"眼睛在移动"。浮点行号 + 插值是本卡的定义性特征。
- **给高亮带单独排 tween 去追相机**——两者会在任何时长改动后失步。带子与相机必须由同一个 `linePosition` 现算。
- **压暗做成二值**（只有当前整数行亮）——滑动那 0.26s 里画面在"闪"而不是在"挪"；压暗必须是 `1 − |i − linePosition|` 的连续量。
- **匀速滑过所有行**（没有 dwell）——读作"代码在自动播放"，观众等它播完而不听你讲。停顿式才是"我念完这句了"。
- **`transform-origin` 用了默认 `center`**——反解公式失效，镜头位置全错（且错得"像 bug 但说不清哪儿不对"）。必须 `0 0`。
- **纯反解不加边界钳制**——首行/末行时画幅被推出块外，白底舞台上就是大片空白。源码是深色背景所以看不出，这是移植必补的一段。
- **块宽小于走读焦距下的可视宽**（960/zoom）——横向钳制退化为居中，画幅两侧常年露白边，读作"素材消失了"。按 `960/zoom + 余量` 反推块宽。
- **行用 `display: flex`**——flex 丢掉纯空白匿名子项，token 间空格与行首缩进全部消失（`export function` → `exportfunction`）。行必须是 block + `white-space: pre`。
- **浅玻璃（半透明白）装代码**——语法色在浅底上一律糊成粉笔字，四个锚点色全废。玻璃块内部必须深底。
- **玻璃背后什么都没有**（纯白舞台）——backdrop blur 没东西可糊，"玻璃"退化成"半透明灰块"。块背后必须有可糊的深色背景（源码用照片，本卡用等价的 CSS 渐变）。
- **块宽收窄了但字号照抄源码的 18px**——最长那行的行尾被切在块外（本卡实测踩到）。字号与块宽是硬耦合，按反推式复算。
- **走读停在空行上**——空行是排版不是一句话，停在那儿观众不知道在看什么。`stops` 要过滤空行（但插值仍连续经过它）。
- **不收全景就结束**——观众眼里只有片段，不知道这段代码整体长什么样。走读必须以全貌收尾，且**同时解除压暗**（只拉焦距不解压暗，全景还是暗的，等于没给全貌）。
- **拿它读 30 行代码**——走读时长直接爆到 20s。>12 行要么裁到关键段，要么换 [evidence-scroll-tour](evidence-scroll-tour.md) 滚动浏览。
- 代码写 lorem 或伪代码——观众一眼看出是假的，"这是真代码"的说服力归零；写真实感短代码（能编译的那种）。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/glass-code-walk.tsx——props：签名收 `hostSrc` 但未使用（本卡无主持人占位）；代码在 `CONFIG.code` 常量里，换代码需改源码（分词 / 行心 / stops / 时刻表随之自动重算）。自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：`demos/glass-code-walk/index.html`。**换代码只改 `CONFIG.code`**——分词、建行、行心、`stops`（空行过滤）、走读句数全部自动跟着走，不用手补任何坐标或时刻。
  节奏在 `CONFIG.dwell` / `stepDur` / `pushDur` / `pullDur`；焦距 `CONFIG.zoom`（改了要按 `960/zoom` 复查块宽）；压暗深度 `CONFIG.dimFloor`；块几何 `blkL/blkT/blkW/blkH`（既推行心，也当相机钳制边界，CSS 的 `.ring` 要同步改）。
  核心可摘走：`CONFIG` + `trackedRow()` + `apply()`（反解 + 钳制 + 带子 + 压暗，共二十来行）。
- 换素材的最小流程：① 把素材四边填进 `blkL/blkT/blkW/blkH`；② 把"当前项的 top / height / 行心 y"写成一个按浮点序号求值的函数（不一定是代码行——列表项、表格行、清单条目都行）；③ 其余不动。**只要能写出"第 p 项的世界坐标"这一个函数，本卡就能走读它。**
- 与母本（remocn glass-code-walk + glass-code-block）的差异——template/cards/glass-code-walk.tsx 已是完整移植，视觉与分词器内联在文件里：
  **视觉是 1:1 照抄的**（2026-08-25 用户定版：用源码原始视觉），连示例代码都是源码的 `DEFAULT_CODE`。
  源码的 `linePosition = interpolate(frame, [0, scanEnd], [0, lineCount − 1])` 是**匀速扫过所有行**（含空行），
  本卡改成"停顿式 + 只停有内容的行"——这是移植时最值得改的一处（匀速扫读的手感是机器在扫，不是人在读）。
  秒 ↔ 帧换算（30fps）：源码 `staggerFrames 10` = 0.33s/行（本卡收到 0.08s）、`PULL_BACK_FRAMES 24` = 0.80s（本卡 0.85s）、`durationInFrames 150` = 5.0s、默认 `zoom 2.6` 是 deep-zoom 档（本卡走读档取 1.68）。
  源码的 `ANCHOR_SCREEN_X 110` 把锚点钉在**画面左侧 110px** 而不是正中（配 deep-zoom 用），本卡走读档改成"横向恒取块心"。
  源码用 `lineHeightOf(line)`（空行 `fontSize×0.8`、正常 `fontSize×1.55`）算行心，tsx 按同一规则用常量静态算出（26 / 14 + 行距 4），demo 从 DOM 现量。
  相机层用 `translate` + `scale` + `transformOrigin: "0 0"`（源码写法一致），移植时补上边界钳制。
- 剪辑软件对应物：AE——代码块做成一张图/预合成，加一个空对象（Null）当"当前行锚点"、按念稿节奏给它打**位置关键帧**（每行一个，Easy Ease 双侧），摄像机或图层位置绑表达式 `W/2 − zoom × null.position[1]`；高亮带是一个矩形形状图层、位置绑同一个 Null（这样它和镜头天然同源）；压暗用一个反向遮罩的黑色调整层，不透明度跟着 Null 走。
  剪映——只能手动逼近：代码块放大后按念稿节奏打一串"位置"关键帧 + 一个白色半透明色块当高亮带跟着打同样的关键帧（两串关键帧必须逐帧对齐，否则带子与镜头错开），压暗只能整体降亮度做不到逐行；**行数多时不推荐**。
  Premiere——`Motion` 的 Position/Scale 关键帧同理，高亮带用一个 Graphic 图层。任何软件里"高亮带与镜头必须同源"这条都要靠**同一个锚点驱动两者**来保证。
- 音效：逐行走读每次跳行给一记 `tick`（`vol` 0.30，`rate` 在 0.96~1.14 之间轮换——同一音色反复出现必须变调，否则读作机械循环）；块弹入一记 `whoosh`（`vol` 0.34、`rate` 1.05）；推近那一下一记 `lowpad`（`vol` 0.22、`dur` 0.6、`rate` 0.9）压住焦距变化；拉回全景一记 `whoosh`（`vol` 0.30、`dur` 0.8、`rate` 0.86，降调 = 收）。**dwell 段无声**——停顿是给口播的，不是给音效的。
  cue 时刻由行数决定：`pushAt = leadIn + (行数−1)×lineIn + 0.26 + 0.10`，第 k 次跳行 = `pushAt + pushDur + dwell + (k−1)×(dwell + stepDur)`，拉回 = 最后一跳 + `stepDur + holdEnd`。**改行数必须重算这串**（10 行时是 1.40 / 2.27 起每 0.58 一跳 / 6.89 拉回）。

## 动效范围
- 属于本卡的：**浮点行号 `linePosition` 同时驱动相机与高亮带**这条定义性纪律（同源 ⇒ 不可能失步）、行间线性插值（`lo`/`hi`/`p − lo` 混合行心）带来的"滑过去而不是跳格"、**停顿式节奏**（`dwell` 停 + `stepDur 0.26s` `power2.inOut` 滑，不是匀速传送带）、**横向恒取块心不跟字符**（读代码是整行读）这条取舍、压暗的**连续量**写法（`1 − |i − linePosition|`，带子在两行之间时上下同时半亮）、走读只停有内容的行而插值仍连续经过空行、反解公式 `tx = W/2 − zoom·cx`（`transform-origin: 0 0` 为前提）、把可视矩形关在块四边内的边界钳制（以及"只 tween zoom 与 dimAmt、位移由钳制自动跟出"这个便宜）、1.5~1.8x 的走读焦距区间与"整行必须完整在画幅内"这条验收标准、**拉回 zoom=1 同时解除压暗**的收尾一拍、块入场的"位移先动 + 淡入独立窗"错位、逐行落位的 0.08s 错峰、"字号由块宽反推"这条硬耦合（改块宽/焦距/行宽都要复算字号，否则行尾溢出块外）。
- 不属于本卡的：demo 那段示例代码的内容（= 源码 `DEFAULT_CODE`）、`scene.tsx` 这个文件名、600×440 这组几何与 17px 字号（但两者之间的**耦合关系**属于本卡）、高亮带的圆角与左侧 3px 亮条这个画法、"代码"这个题材本身（列表项、表格行、清单条目走读都成立）。
  **注意：玻璃块的视觉与 token 配色不是"我们的设计"而是 remocn 源码原样**（`rgba(10,10,10,0.6)` + `blur(16px)`、1px 渐变描边、`0 50px 120px` 投影、40px chrome + macOS 三灯真色、`#a1a1aa` 标题、28px 行号槽 `#3f3f46`、五个 `TOKEN_COLORS`、暗调照片背景）——2026-08-25 用户定版要求按源码原始视觉走，所以复用时**照抄这一整套**，不要再各自改编（改编版曾把玻璃改成 `rgba(22,22,28,.74)` + 18px blur + 灰阶三灯 + 自选四色 + 三团灰阶软斑，已废弃）。
- 迁移接口：`CONFIG.code` 是唯一的迁移入口——换成你真实要念的那 6~10 行，分词/建行/行心/空行过滤/走读句数全部自动重算（但**行数变了要重算 sfx cue 的 t 串**，公式见复用指引；**最长行变长了要按反推式复算字号**）；`dwell` 按口播语速给（他念完一句你才滑走，别让带子跑在解说前面）；`zoom` 按"走读时行尾有没有被裁"验收（不是按构图）——**整行完整在画幅内是硬标准**，改了 `zoom` 必须按 `960/zoom + 余量` 复查块宽、再按块宽复算字号；`dimFloor` 按"周围行还读不读得出结构"给；换素材只需重写"第 p 项的世界坐标"这一个函数；竖屏把块宽放到画幅宽度的 92%、行宽压到 28 字符以内、`zoom` 降到 1.4（竖屏字大，1.68 会裁行尾）。
- 底色要求：**源码原始视觉 = 内容本身，2026-08-25 用户定版：按 remocn 源码原样实现**。
  舞台底是**暗调背景**（源码 `previewBackdrop` 是一张暖褐→墨绿的照片 `/bg.jpg`；demo 禁外网资源，用等价的 CSS 渐变复刻其色调分布），
  **不受"白舞台中性化"约束**。两条理由都是硬的：① 玻璃块内部必须深底，语法色靠深底成立（浅玻璃上四个锚点色一律糊成粉笔字）；
  ② **块背后必须有可糊的东西**——纯白背景下 backdrop blur 没有素材可揉，"玻璃"退化成"半透明灰块"，这张卡的招牌材质就没了。
  落到实拍/深色画面上时舞台底可直接换成那段素材（比 CSS 渐变更好——真实素材被玻璃揉开时块内块外的对照更明显）；
  换浅色背景则本卡不成立，要改用不带玻璃的代码块（高亮带走读那套机制本身与材质无关，可以单独搬）。
- 与相邻卡的分工：**vs [cursor-locked-zoom](cursor-locked-zoom.md)（同源机制的另一档）**——两张共享同一条反解公式与"镜头由内容进度驱动"的纪律，但档位不同：那张是 2.6~2.8x **deep-zoom 跟光标**（锁 x 到字符、一屏只剩七八个字符、目标在**逐字符**移动），本卡是 1.5~1.8x **逐行高亮走读**（锁 x 到块心、整行完整可读、目标在**逐行**移动）+ 玻璃块 + 压暗。**浅走读用这张、深怼镜头用那张**：念一条长命令（横向长、单行）用那张，读一段多行代码（纵向长、每行一句话）用本张。**vs [terminal-typing-log](terminal-typing-log.md)**——那张是内容在动（逐行打出 + 滚动）、镜头不动；本卡是内容静止（一次铺完）、镜头与高亮在动。**vs [evidence-scroll-tour](evidence-scroll-tour.md)**——那张是长素材滚动浏览（量大、不逐句念），本卡是短素材逐句走读（量小、每行都念）。**vs [focus-dim-spotlight](focus-dim-spotlight.md)**——那张压暗聚焦但**不动镜头也不换焦点**（一次锁定一处），本卡的焦点在连续移动；只强调一处用那张。

<!-- ===== /file: video-talkcraft/references/cards/glass-code-walk.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/gooey-morph.md ===== -->

---
name: gooey-morph
标题: 图块拼入
优先级: P1
代码: template/cards/gooey-morph.tsx
一句话: n 张图各自走 L 形路径从画外飞来——先横向滑到自己的列、再纵向落进行位，起飞时刻故意不按左右顺序，几张图几乎相接地拼成一条横排，拼完即落点
适用: 一次性把 3~6 张并列证据摆上来的时刻——"这几个案例/这四个平台/这几张对比图"；需要"它们是一组"而不是"一张一张讲"的语义；组图、九宫格式素材、多平台横排
时长: 各张错峰起飞 0/0.13/0.27/0.43s，单张行程 1.0s ⇒ 全部到位约 1.43s → 收尾定格 1.4s；全程 2.83s
能量: 中
类别: 素材呈现
输入: 图, 人(可选)
语义: 例证
素材形态: 多图
位置: 中段
props: hostSrc
---

## 意图
2026-08-26 用户定版：这张卡原来叫**粘液融字**——四个色块飞入排成一条，然后走 goo 三段管线
（高斯糊 → alpha 阈值收紧 → 湍流位移）融化成四个字。现在**只保留前半部分**：
方块本身就是要展示的内容（图），拼完就是落点，不再融化成任何东西。

去掉后半段是对的，理由与机制有关：goo 管线的用途是"色块换形成字"，
它必须先把画面糊成一团 alpha 场才能重新收紧出硬边。而图是要看清内容的东西——
把图糊掉再收紧，观众只会觉得这一拍渲染坏了。**留下来的 L 形入场才是这张卡真正值钱的部分。**

于是它从"字幕花字"挪进了**素材呈现**类，和 `media-pop-in` / `motion-blur-slam-in` 排在一起。
三者的分工：`media-pop-in` 是**歪着叠**（三张各自带旋转、层层压住，读作"一沓照片拍上桌"）、
`motion-blur-slam-in` 是**同向怼**（带方向模糊高速甩入急停，读作"怼到你脸前"）、
本卡是**并列拼**（几张严丝合缝地拼成一条，读作"这是一组，它们并列"）。
要"一组并列的证据"就用本卡，要"堆"或"砸"用那两张。

命门两条：
① **L 形路径**——x 走前半程、y 走后半程，两轴分开。两轴同时走就是斜线飞入（普通 fly-in），
拐点那一下"到了自己的列、然后落进行位"才是俄罗斯方块的手感；
② **起飞时刻不按左右顺序**（0 / 0.13 / 0.27 / 0.43s，第 2 张最先到、第 4 张最后到）——
按顺序依次到位读作程序在循环刷 DOM，错开才读作"各自从画外来"。

## 动效核心
- **落位是算出来的，不是写死的**：一条横排、整体居中于图区。
  `整条宽 = count×picW + (count−1)×gap`，左端 = `(图区宽 − 整条宽)/2`，逐个累加。
  **`count` 是唯一的"几张图"入口**——单张宽以 `picW` 为上限，整条装不下时按图区可用宽自动等比收窄
  （`picW = min(picW, ⌊(图区宽 − 2×sideMargin − gap×(count−1)) / count⌋)`，高按 `picAspect` 跟着收）。
  所以 3 张到 6 张只改这一个数字，不会有任何一张被图区的 `overflow` 切掉
- **L 形路径**：单张行程 1.0s，`k = ease(局部进度)`，然后
  `kx = min(1, k×2)`（前半程走完 x）、`ky = max(0, k×2 − 1)`（后半程走完 y）。
  于是同一条缓动同时描述两段，拐点自动落在 k=0.5
- **入场一律从图区右外侧来**（`entryFrom` 的 x 全为正）：图区左边紧挨着数字人，
  从左飞入会横穿人物身上、而且被 `overflow: hidden` 切掉半张。竖向偏移一半从上一半从下（±150 以上），
  四张不同轨才不像同一个队列在排队
- **缓动 `cubic-bezier(0.88,0.14,0.12,0.86)`**（沿用源码 travelEase）：**极陡的中段**——
  起手慢、中间猛、收尾稳。这是"方块被吸到位"的手感；匀速读作程序在拖元素，`power2.out` 读作滑行
- **一张图 = 白边 + 投影**：与 `media-pop-in` 同一套"实体素材"物质约定（白边 4px + 柔投影）。
  demo 里的灰阶假图（日 + 远近两座山的极简剪影）是占位，接应用时整块换成 `<img>`
- **实现是逐帧求值**：一条线性虚拟时钟 tween + `frameAt(t)`（位置是 t 的纯函数），
  与 Remotion 的 `useCurrentFrame` 同构 —— seek / 慢放 / 重播全部一致
- **层级**：白底舞台 → 人物列（47%）→ 图区（右 53%，`overflow: hidden`）→ 各张图（唯一被 transform 的元素）

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `count` | 4（3~6） | **唯一的张数入口**，宽度自动适配；3 张下"拼成一条"的并列感最强，6 张单张只剩 70px 宽、内容开始看不清，>6 张请改成两行网格（那不是这张卡） |
| `gap` | 5px | 张间缝；**小缝才读作"拼成一条"**，>20px 就是几张各自摆着（要那个效果用 media-pop-in） |
| `travel` | 1.0s | 单张行程；<0.5s 读作弹窗，>1.6s 观众等着方块走完 |
| `entryAt` 错峰 | 0 / 0.13 / 0.27 / 0.43s | 各张起飞时刻，**故意不按左右顺序**；全部同时 = 一次整体平移，按顺序 = 程序循环感 |
| `entryFrom` | x 300~500（**必须为正**）/ y ±175~195 | 起手位相对落位的偏移；x 给负值会让图横穿人物并被切掉；\|y\| <100 看不出"落进行位"这一下 |
| `picW` / `picAspect` | 106px / 0.755 | 单张宽的上限与高宽比；4:3 略扁读作照片，1:1 读作色块（那就回到原来的"色块"语义了） |
| `sideMargin` | 34px | 整条两侧至少留的余白，同时是自动收窄的依据；调到 0 则末张紧贴图区边缘、读作没排版 |
| `hold` | 1.4s | 收尾定格——拼好的一条就是本卡的落点，<0.8s 观众来不及看完几张图 |

## 已知坑
- 两轴同时走（x/y 一条 tween）——变成斜线飞入，就是最普通的 fly-in，L 形拐点那一下的"方块感"全部消失。
- 各张按左到右依次起飞——读作程序在循环刷 DOM。错峰顺序必须打乱。
- `entryFrom` 给负 x 让图从左侧飞入——图会横穿数字人身上，而且被图区 `overflow` 切掉半张。一律从右外侧进场。
- 张间缝按"看起来舒服"给 20~40px——"拼成一条"的并列语义没了，变成几张各自摆着。缝要 ≤8px。
- 改 `count` 却手动写死 `picW`——整条撑破图区，末张被 `overflow` 无声切掉（本 demo 踩过：count=6 时两端各切掉半张）。宽度交给自动适配。
- 缓动用匀速或 `power2.out`——匀速读作程序在拖元素，`power2.out` 读作滑行；要的是陡中段的"被吸到位"。
- 给图加旋转让它"活泼一点"——那是 `media-pop-in` 的语义（歪着叠）。本卡的全部意义是**并列整齐**，一歪就没有"这是一组"了。
- 拿它当转场用（上一镜的图拼成下一镜）——本卡作用在一个镜头内部，是素材入场；跨镜头换形态用 `particle-weld-transition`。
- 一片里反复用——并列拼是"摆证据"的动作，同一段口播里出现两次，观众会以为前面那组还在。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/gooey-morph.tsx——props：仅 `hostSrc`；张数在 `CONFIG.count`，每格内容是 JSX 里的 CSS 假图（`.gm-pic` 内部三个 div），换图需改源码（整块换成 `<Img>`，白边与投影留着）。自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/gooey-morph/index.html。**换张数只改 `CONFIG.count`**（宽度自动适配）；
  换内容把 `.gm-pic` 内部那三个灰阶 div 整块换成 `<img>`（白边与投影留着——那是"实体素材"的语义）。
  节奏只动 `travel` 与 `entryAt`。`cubicBezier()` 是通用缓动解算器，可直接抄走。
  结构是"一条线性虚拟时钟 tween + `frameAt(t)` 逐帧求值"，所以 seek / 慢放 / 重播一致。
- Remotion 移植：位置是纯函数，原样搬——
  `const k = Easing.bezier(0.88,0.14,0.12,0.86)(clamp((frame - startF)/travelF))`，
  再 `kx = min(1, k*2)`、`ky = max(0, k*2-1)`，`x = lerp(fromX, restX, kx)`、`y = lerp(fromY, restY, ky)`。
  秒↔帧（30fps）：错峰 0/0.13/0.27/0.43s = 0/4/8/13 帧、行程 1.0s = 30 帧。
  母本（remocn gooey-morph）的 `barRestPositions` / `barStartPositions` / `barEntryFrames` 对应本卡 tsx 的 `REST` / `CONFIG.entryFrom` / `CONFIG.entryAt`，**但它后半段的 goo 滤镜链本卡已不用**（连同 `morphStartFrame` 等参数一起去掉）。
- 剪辑软件对应物：剪映/CapCut——每张图两段位置关键帧（先横后竖），缓动手动拉成陡中段；
  AE——位置属性打三个键（起手 / 拐点 / 落位），把拐点键的 x 设成落位 x、y 还是起手 y，就是 L 形；
  几张图错开起始帧即可。这张卡在剪辑软件里最好做，因为它没有滤镜、只有位移。
- 与本类同伴的分工见「意图」段：`media-pop-in` 歪着叠 / `motion-blur-slam-in` 同向怼 / 本卡并列拼。
  三者**不在同一段口播里混用**（三套素材入场逻辑打架）。

## 动效范围
- 属于本卡的：L 形路径（x 走前半程、y 走后半程，拐点在缓动进度 0.5）这条机制；起飞时刻故意不按左右顺序的错峰（0/0.13/0.27/0.43s）；`cubic-bezier(0.88,0.14,0.12,0.86)` 的陡中段；落位按张数自动算成"一条横排、整体居中、张间缝 ≤8px"（含装不下时按图区等比收窄单张宽）这条排版纪律；入场一律从图区外侧（远离人物那一侧）进场；白边 + 投影的"实体素材"物质约定；拼完即落点、不做任何后续形变这条时间纪律。
- 不属于本卡的：demo 里的灰阶假图内容（日 + 两座山的剪影）、`count = 4` 这个具体张数、单张 106×80 这个尺寸、主持人占位与"人物左 47% / 图区右 53%"的布局、图区的具体余白值。
- 迁移接口：`count` 是唯一的张数入口（3~6，宽度自动适配）；换素材替换 `.gm-pic` 内部内容；`entryFrom` 的 x 符号由"人物在哪一侧"决定（人物在左 ⇒ x 为正从右进；人物在右 ⇒ x 为负从左进）；`travel` / `entryAt` 按口播语速缩放；`picW` 按输出宽度等比缩放，`gap` **不要**跟着放大（缝一放大就散成几张各自摆着）。
- 底色要求：白底即可。深底把 `.gm-pic` 的白边换成深色描边（或直接去掉边、只留投影）；本卡没有任何滤镜，不依赖底色的色彩空间。

## 适用对象与落位（2026-09-05 用户定版，选卡时抄进 SHOTBOOK 该镜自检列）
- **只用于图片 / 图形块，不用于文字方块**：三四个写着"文档 / 表格 / 小工具"的白框飞入拼排，读作 PPT 表格而不是"一组证据"。文字类并列改用 `line-by-line-slide` / `numbered-step-stack` / chips（chip 文字 ≥40px、底板淡色系区分，layout.md §5/§7）。
- **无人物在场时整组包围盒水平居中**（不是靠右半幅）；有人物时放人物对侧半幅中心（layout.md §4）。实测反例：三个色块整体偏右、左半幅全空。
- 拼完的一条横排离画幅左右边 ≥ 96px（贴边 <64 判缺陷）。

<!-- ===== /file: video-talkcraft/references/cards/gooey-morph.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/grid-to-hero.md ===== -->

---
name: grid-to-hero
标题: 网格收成主角
一句话: 2×2 网格错峰 120ms 落位先并列，讲到那一格时它 0.8s 长成 620×444 主图、其余三格同一条曲线收成右侧一列 220×132 小图（不消失），停 2s 后回到网格，再一起退场
适用: "四个里我们选了这个"——封面候选 / 四条评论最狠一条 / 四个版本的最终版；任何"先并列再聚焦"的选择题，且选项之间要保留对照关系
时长: 7.33s（0.3 起错峰落位 → 2.41 重排 0.8 → 停 2.0 → 5.21 回网格 0.8 → 停 0.8 → 6.81 退场 0.4）；成片网格停留与主图停留随口播伸缩
能量: 中
类别: 素材呈现
输入: 图, V
语义: 对比, 列举, 选择
素材形态: 横屏, 多图
位置: 中段
props: labels, srcs, heroIdx
优先级: P1
代码: template/cards/grid-to-hero.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 人物不在此镜 | 可（四格图 / 视频混排；`srcs` 传 .mp4 / .webm / .mov 自动走 `<OffthreadVideo>`，重排时不重置） | 可（默认输入：封面 / 截图 / 评论卡） |

四格外框比例随重排变化（2:1 → 1.4:1 → 1.67:1），素材以 cover 裁切、不拉伸——主体别贴着素材边。

## 常用场景
1. "四个方案里我们选了这个"：封面候选 ①②③④ → 选 ③（demo 所演）
2. 四条评论里最狠的一条 / 最有代表性的一条
3. 四个版本里的最终版（先看全部再看定稿）
4. 任何"先并列再聚焦"的选择题（四选一、三选一改 3 格即可）

## 意图
"从几个里选了一个"是最常见的叙事之一。做错的两种：只放最终那张（观众不知道选自哪些）、四张轮播（对照关系没了）。本卡把"并列"和"聚焦"做成一个镜头里的两个状态，命门四条：
1. **网格先并列**：错峰 120ms 落位（不是四张一起淡入），观众先数清有几个。
2. **主图长大与其余收缩走同一条 inOut、同一时刻起止**——是一次"重排"，不是"一张放大、三张飞走"两件事。
3. **其余不消失**：收成等大等距的一列，保留"是从这四个里选的"这层意思；观众能随时把主角和落选者对照。
4. **讲完回到网格再退场**：首尾对称，退场时观众记住的是"四选一"而不是"这一张"。

## 动效核心
- `0.3 / 0.42 / 0.54 / 0.66s` 四格落位（`y 24→0 + scale .97→1 + opacity`，power3.out 0.55s，错峰 0.12）→ `2.41s` 网格停 1.2s 后重排（power3.inOut 0.8s）：主角 → 主图 620×444 @ (48, 48)，其余按原顺序 → 右侧一列 220×132 @ x 692、y 48 / 204 / 360（列顶与主图顶对齐，间距 24）→ 停 2.0s（主图内部 `1→1.05` 匀速缓推，重排起 → 回网格止）→ `5.21s` 回到网格（power3.inOut 0.8s，缓推 power2.inOut 收回）→ 停 0.8s → `6.81s` 一起退场（0.4s power2.in，错峰 0.04）→ `7.33s` 结束。
- 位置用 `transform: translate()`、尺寸用 width / height 插值（**不动 left / top**）：cover 裁切的图在宽高变化时重新取景、不失真——纯 FLIP（translate + 非等比 scale）会把图和标签拉变形，重排完还得换回真实尺寸，所以只借 FLIP 的位移半边。Remotion 每帧独立渲染，width / height 插值没有实时布局抖动的问题。
- 主角 z-index 在其余之上（重排时左上那格从主图后面收走）；标签 16px 600 白字 + 文字投影压在图左下（left 20 / bottom 18）。
- 几何（960×540）：四边 48 安全边、间距 24 → 网格 420×210 @ (48, 48) / (492, 48) / (48, 282) / (492, 282)；主图 620 = 65% 宽；列宽 220、三格 132 高 + 两条 24 间距 = 444 = 主图高。白边卡 padding 8 / 圆角 12 / 唯一投影。
- demo 里的示意图（Picsum，demos/_lib/media）是演示语境；成片 `srcs` 注入真素材、`labels` 换标签、`heroIdx` 指定哪格是主角。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `stagger` 网格错峰 | 0.12s | 100~150ms 读作"先后"；>250 像逐张展示，<60 像一起淡入 |
| `holdGrid` 网格停留 | 1.2s | = 口播念完"四个候选"；<0.8 观众还没数清 |
| `reflow` 重排 | 0.8s | power3.inOut；<0.5 像切换，>1.2 拖；长大与收缩必须同一值 |
| `holdHero` 主图停留 | 2.0s | = 讲这一格的句长，任意伸缩 |
| `heroPush` | 1.05 | 主图内部缓推，速率 = .05 / (reflow + holdHero)；停留越长推得越慢 |
| `holdBack` 回网格后停留 | 0.8s | 首尾对称的"再看一眼"；>1.5 拖 |
| 主图占宽 | 65%（620/960） | 60~68%；再宽小图列窄到看不清，再窄主角不够主 |
| 小图列 | 220×132 / 间距 24 | 等大等距；列顶与主图顶对齐，列高 = 主图高 |
| `heroIdx` | 2（第 3 格） | 内容决定；不是节奏参数 |

## 已知坑
- 四张一起淡入——网格读作一张贴图，"四选一"的"四"没了。
- 主图放大 0.6s、其余收缩 0.9s——两件事；重排必须同一条曲线同起同止。
- 落选三格淡出消失——退成"单图展示"，对照关系没了；它们要收成一列陪着。
- 用 left / top 动画（实时预览）或纯 FLIP 非等比 scale（图变形）——位置走 transform、尺寸走 width / height。
- 小图列不等距 / 列顶没和主图顶对齐——一眼假的"随手摆"。
- 讲完直接退场不回网格——观众记住的是最后那一张，而不是"选了一个"。
- 网格离画幅边 <48@960——贴边（layout.md ①）；实验室原型的 40 边距入库时改成 48。
- 标签 <16@960 或没有文字投影——压在浅色图上读不出。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/grid-to-hero.tsx——`srcs` 四格真素材（按后缀自动 `<Img>` / `<OffthreadVideo>`）、`labels` 四条标签、`heroIdx` 主角格；导出的 `END` 是动画结束秒；停留要随台词伸缩改 `CONFIG.holdGrid / holdHero`（T1 / T2 / T_OUT 自动重算）。
- HTML/GSAP：demos/grid-to-hero/index.html——`CONFIG` 顶置（节奏 + 几何一处改）；`.pic` 整块换成 `<img>` / `<video>` 即真素材。
- 与 layout.md 的接口：四边 48 安全边、间距令牌 24（§1 §2）；无人物 → 组包围盒居中（§4，网格 48~912 居中）；同组同造型（§8）。
- 剪辑软件对应物：剪映四层画中画各打位置 / 缩放关键帧（同一区间、同一曲线）；AE 是四层 Position + Scale 关键帧共用 Easy Ease；CapCut 同理。

## 动效范围
- 属于本卡的：错峰 120ms 落位 → 停 → 同一条 power3.inOut 重排（主角长大 + 其余收成等大等距一列）→ 停 → 回网格 → 一起退场的时间表；主图内部 1→1.05 缓推（重排起回网格止）；位置 transform / 尺寸 width-height 的实现约定；网格 / 主图 / 小图列的几何比例（65% 主图、列高 = 主图高、四边 48、间距 24）。
- 不属于本卡的：示意图（演示语境素材，demos/_lib/media，不属于本卡）、标签文案、白底舞台。
- 迁移接口：`srcs` / `labels` / `heroIdx` 换内容与主角；`CONFIG.holdGrid / holdHero` 按口播伸缩；3 格版把 `grid` 删到 3 项、列改两格（列高不够就把 `col.h` 放到 210）；换画幅按 960×540 等比缩放，竖屏改 2 行 2 列 → 主图在上、三小图一行在下。
- 底色要求：白底即可（白边卡 + 投影分层）。

## 落位自检（2026-09-05 用户定版，选卡时抄进 SHOTBOOK 该镜自检列）
- **网格几何**：四格 420×210，四边到画幅 48、间距 24，组包围盒 48~912 居中（偏差 >48 返工）。
- **重排后几何**：主图 (48, 48, 620, 444)、小图列 x 692、y 48 / 204 / 360、220×132，列顶 = 主图顶、列底 = 主图底（>8px 偏差返工）。
- **同起同止**：重排帧（2.41 → 3.21）主图与三小图同时开始、同时到位；定妆帧取 2.8s，主图与小图都在中途。
- **落选不消失**：主图停留段（3.21~5.21）三张小图全时刻可见、等大等距。
- **标签字号**：≥16@960（≥32@1080）、白字带文字投影；缩到 390 宽复看可读。
- **首尾对称**：回网格帧（6.01）四格几何与落位帧完全一致；退场前不新增元素。

<!-- ===== /file: video-talkcraft/references/cards/grid-to-hero.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/hand-drawn-ellipse.md ===== -->

---
name: hand-drawn-ellipse
标题: 手绘圈重点
优先级: P0
代码: template/cards/hand-drawn-ellipse.tsx
一句话: 一笔逆时针画出的歪椭圆圈住关键短语——0.5s 画到 1.08 圈让尾巴过头 8% 与起笔交叉，圈画完之后短语才 punch 1.06→1 一拍，然后静置 1.8s
适用: 口播说"就是这一点""记住这个词"这种**指认单个短语**的时候；观点类、方法论、锐评口播；需要比双线更强、比爆点字更克制的强调档；不适合圈整句（圈的语义是"就这几个字"，圈一整行读作框选）
时长: 起手静置 0.42s → 画圈 0.5s → 呼吸 0.06s → 短语 punch 0.22s → 收尾定格 1.8s；共约 3.0s
能量: 中
类别: 强调标注
输入: 文, 人(可选)
语义: 强调
素材形态: 无
位置: 任意
props: hostSrc
---

## 意图
"圈起来"是所有强调手势里最像**人**的一个——它有明确的笔顺、有起点终点、必然画不圆。
本库的 `scribble-annotation` 已经有圈，但它的语境是**标注素材**（圈截图里的价格、圈按钮），
一次画三笔，圈只是其中一种笔；这张卡把圈单独拆出来，语境换成**圈口播里的一个短语**，
并且加了一件 scribble-annotation 没有的事：**圈完之后被圈的短语自己动一下**。

那一拍 punch 是本卡的核心信息。圈本身只是"我指这里"，punch 是"而且它很重要"——
两个信息分两拍给，观众的注意力先被圈引到位置上，再被 punch 确认强度。
同时给（圈和 punch 一起）就乱了：读作"字被圈撞了一下"，动因反了。

命门两条：① **必须过头交叉**（画到 1.08 圈、每绕一圈半径外扩 5.5%，尾巴落在起笔外侧）。
闭合成完美椭圆一眼是矢量图形——手画的圈闭不上，这是常识级的真实性判据；
② **圈画完才 punch**（中间留 0.06s 呼吸）。同时发生就少了那个先后关系。

## 动效核心
- **圈层 = 盖在文字上的全屏 SVG**（`viewBox="0 0 960 540"`、`pointer-events:none`），
  `fill:none` + `stroke-linecap/linejoin: round`
- **圈的几何绑定被圈短语的墨迹盒**：demo 给目标 DOM 打 `data-ink="key"`，运行时用 canvas `measureText`
  量它的**墨迹盒**（`actualBoundingBoxAscent/Descent` + baseline，不是行盒——行盒上下带
  line-height 留白，照行盒画圈会整体偏高一截）。圈心 = 墨迹中心，半径 = 半宽/半高 + pad。
  **tsx 是纯函数渲染，把 demo 算出的 path 原样烘焙成 `ELLIPSE` 常量（`d` + 实测长度 `len` 471.44）**——换短语要在源码外重新生成
- **歪椭圆的四个不完美**（手作感全在这里，一个都不能少；这四项是 demo `ellipsePath()` 的形状参数，在 tsx 里已烘焙进 `ELLIPSE.d`，不是 CONFIG 项）：
  - `turns: 1.08` —— 画 1.08 圈，尾巴过头 8%（命门①）
  - `grow: 0.055` —— 每绕一圈半径外扩 5.5%，让尾巴落在起笔**外侧**而不是压住它
  - `tilt: -3.5°` —— 整体静态倾斜（不是动效，是形状属性）
  - `wobble: 3.4` —— 半径带确定性正弦起伏 ±3.4%
    （`0.62·sin(3.7a+seed) + 0.38·sin(9.1a+seed·2.3)`，**不用 `Math.random`**）
- **长短轴比 ≈3.4:1**（由文字盒决定：`padX: 26` / `padY: 15`）。**横向 pad 必须比直觉大一档**——
  椭圆在字高处腰已经收窄，padX <16 时圈的左右腰会切进首末字
- **逆时针一笔**（`dir: -1`、`startAngle: -145°` ≈ 左上角起笔）：右手画圈的自然方向
- **单条 path、恒定线宽 3.2px**（`stroke-linecap: round`）：**不模拟笔压**——
  多层叠描/粗细渐变那套（起笔粗收笔细）实测线宽忽粗忽细，比匀速线还难看。
  手作感全部交给**形状层**（1.08 圈过头交叉 + 逐圈外扩 + 静态倾斜 + 半径起伏），
  笔宽不参与表演
- **时序**：`dashoffset` 全长→0，0.5s `power2.out`（起笔快收笔缓；匀速一眼假）
  → 呼吸 0.06s → 短语 `scale 1.06 → 1`，0.22s `power3.out`（`transform-origin: 50% 55%`）
- **被圈短语必须是独立的 `inline-block`**：punch 只能作用在它自己身上，不能带动整行重排
- **画完保持干净静置**：本库定版**不做 line boil / 定格抖动**（design-language.md §4）
- **层级**：白舞台 → 文字（两行，上行 dim 实色）→ 圈 SVG 层 → 主持人占位（右 30%）

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `startDelay` | 0.42s | 起手静置，等口播念到这个短语 |
| `punchGap` | 0.06s | **本卡第二命门**；=0 圈与 punch 同时发生，读作"字被圈撞了一下"；>0.25s 两件事脱钩，punch 读作独立的第二次强调 |
| `punchScale` | 1.06 | punch 幅度；<1.03 看不出来（那不如不做）；>1.12 读作弹跳，本卡是"重音确认"不是"弹出" |
| `punchDur` | 0.22s | punch 回落时长（`power3.out`）；与 `punchScale` 一起决定"重音"的干脆度 |
| `draw` | 0.5s | 画圈耗时；<0.3s 看不出笔顺方向（圈"闪"出来）；>0.8s 观众在等一个圈画完 |
| `width` | 3.2px（3~3.5） | 圈的恒定线宽（全程一个值，**不做粗细变化**）；<2.5px 读作 UI 描边（没有笔的墨量），>4.5px 粗圈会咬到字 |
| `hold` | 1.8s | 收尾定格，被圈的短语是本卡的落点，按字数给（每字约 0.3s） |

形状常量（**不是 tsx 可调参数**——烘焙在 `ELLIPSE.d` 里；demo 的 `ellipsePath()` 才收它们，重新生成 path 时按这些值给）：`turns` 1.08（**第一命门**；=1.0 精确闭合一眼是矢量椭圆，>1.3 读作"划掉"，1.05~1.15 是甜点）、`grow` 0.055（=0 尾巴压在起笔上像画粗了，>0.12 读作两个不同心的圈）、`padX / padY` 26 / 15（**padX <16 圈的左右腰切进首末字**，>40 读作框住一片区域）、`tilt` −3.5°（=0 太正读作图形，>8° 读作贴歪）、`wobble` ±3.4%（=0 完美椭圆，>7 读作抖手）、`startAngle / dir` −145° / −1（左上角逆时针起笔，正右/正下起笔读作机器起点）；描画缓动 tsx 固定 `power2.out`（起笔快收笔缓，匀速读作 loading 圈）。

## 已知坑
- 圈精确闭合——最致命的一条。闭合的椭圆一眼是矢量图形，"有人画了这个圈"这件事直接消失。
  必须过头 5%~15% 且尾巴落在起笔外侧（靠 `grow`；tsx 的 `ELLIPSE.d` 已是过头 8% 的路径，重新生成 path 时保住这两项）。
- 圈和 punch 同时发生——先后关系是本卡的第二个信息。同时给读作"字被圈撞了一下"，动因反了。
- 用 `<ellipse>` 元素 + `stroke-dasharray` 描画——那是完美椭圆，`turns`/`wobble`/`grow`
  三件事一件都做不出来。必须用采样点算出来的 path。
- 重新生成 path 时 `padX` 照 `padY` 抄同一个值——椭圆在字高处腰已收窄，等 pad 时圈的左右腰一定切进首末字。
  横向 pad 要比纵向大 60%~80%。
- 重新生成 path 时照行盒（`getBoundingClientRect()`）算圈心——27px 字的行盒比字形高十几 px，圈会整体偏上，
  下沿从字中间穿过去。必须用 canvas `measureText` 的墨迹盒。
- 被圈短语没有单独包 `inline-block` 就 punch——scale 会带动整行（甚至触发重排），
  圈和字瞬间错位。
- **模拟笔压（起笔粗收笔细）——2026-08-25 用户定版删除**。不管用多层 dasharray 叠描
  还是 `stroke-width` tween，落到静帧上都是**线宽忽粗忽细**，读作"画歪了/描边没对齐"，
  比恒定线宽的匀圈还难看。本卡的手作感只做在**形状**上（过头交叉 + 逐圈外扩 + 倾斜 + 半径起伏），
  笔宽全程恒定 3.2px。
- 匀速描画——读作 loading 圈，不是人手。（描画的快慢曲线要保留，只是**线宽**不许变。）
- 画完加 line boil / 定格抖动——本库定版禁项（design-language.md §4）。
- 行距按正常正文给（1.9 以下）——圈的上下沿外扩 `padY`，行距太密圈会咬到上一行的字。
  用这张卡的那一行需要 2.3+ 的行距。
- 圈一整句——圈的语义是"就这几个字"。圈住一整行读作"框选一段区域"，
  那是 `outline-box-title`（机器画的框）的语言，两种别混。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/hand-drawn-ellipse.tsx——props：仅 `hostSrc`；两行文案与被圈短语在 JSX 常量里，圈的 path 是 `ELLIPSE` 常量（demo 运行时算出后照抄），换短语需改源码并在源码外重新生成 path。自包含单文件，复制进工程即可用；节奏 / 线宽 / 颜色参数在顶部 CONFIG（`startDelay / color / draw / width / punchGap / punchScale / punchDur / hold`），时长/尺寸在 meta。
- HTML/GSAP：demos/hand-drawn-ellipse/index.html。**换圈的对象不用改坐标**：给目标元素加
  `data-ink="key"`（几何全部从 DOM 量出来，改文案/改字号圈自动跟着走）。
  松紧调 `padX/padY`，形状调 `turns/grow/tilt/wobble/seed`，节奏调 `draw/punchGap/punchDur`，
  线宽改 `width`（恒定值），换色改 `color`。核心逻辑 = `CONFIG` + `inkBoxOf()` +
  `ellipsePath()` + `smooth()` + `inkStroke()`，可整段摘走；`inkStroke()` 与
  `scribble-annotation` 的 `drawStroke()` 等价（都是单条 path 恒定线宽的 dasharray 描画）。
- Remotion 移植（tsx 现状）：`d` 与长度 `len` 由 demo 的 `ellipsePath()` + `getTotalLength()` 预生成后写成 `ELLIPSE` 常量（纯函数、无随机 → 帧间完全一致；换短语重跑 demo 取新值）。单条 path：
  `strokeWidth = 3.2`（常量）、`strokeDasharray = L`、`strokeDashoffset = L·(1 − p)`，
  `p = interpolate(frame, [s, s+drawF], [0,1], {easing: Easing.out(Easing.quad), extrapolateLeft:"clamp", extrapolateRight:"clamp"})`。
  punch 用第二段 `interpolate(frame, [s+drawF+gapF, s+drawF+gapF+punchF], [1.06, 1], {easing: Easing.out(Easing.cubic)})` 驱动 `scale`。
- 剪辑软件对应物：AE = 钢笔画一个**故意不闭合、尾巴过头**的椭圆路径（形状图层）+
  `修剪路径`(Trim Paths) 的 End 0→100%（0.5s，`Easy Ease Out`）；描边宽度固定 3.2px
  （**不要**做锥形描边/多层叠描去模拟笔压）；
  punch 在文字层的 `缩放` 打 1.06→1 两键，起点比描画结束晚 2 帧。
  剪映/CapCut 没有描画通道：用"贴纸 → 手绘圈/涂鸦圈"里**尾巴过头**的那款（选静置无抖动帧）
  摆到短语上，入场用"放大"（缩放 0.9→1，0.4s）近似，再给文字层加一个"缩放"关键帧做 punch。
  **不要用"圆形蒙版 + 描边"**——那一定是完美椭圆。
- 与本库同类卡的分工：`scribble-annotation` = 圈/线/箭头三笔串行标注**素材里的位置**
  （语境是"跟你一起看这张图"）；
  `outline-box-title` = 机器画的圆角框（匀速 inOut、精确闭合，是"框选"不是"手绘"）；
  **本卡 = 单个短语的一笔手绘圈 + 圈完 punch**（唯一带"圈完确认"两拍的强调卡）。
  与 `outline-box-title` 是刻意的一对反例：**同一个"围起来"的动作，手画 vs 机器画是两种语言**，
  一屏里只能用一种。手画的判据是**形状不完美**（过头交叉、歪、起伏），不是线宽变化。

## 动效范围
- 属于本卡的：**过头交叉**这件事（`turns 1.08` + `grow 0.055` 让尾巴落在起笔外侧）——它是本卡真实性的全部来源；**圈画完才 punch** 的两拍时序（`punchGap 0.06s` 这个呼吸不能为 0）；`dashoffset` 全长→0、0.5s `power2.out` 的描画（起笔快收笔缓，匀速即失效）；**单条 path + 恒定线宽 3.2px**（`linecap round`）这条实现纪律——手作感只做在形状上，**不许模拟笔压**（粗细变化实测忽粗忽细，用户 2026-08-25 定版删除）；圈心绑定目标**墨迹盒**中心、半径 = 半宽/半高 + pad 且 **padX 必须比 padY 大一档**这条落位纪律；歪椭圆的四个不完美（1.08 圈 / 逐圈外扩 / 静态倾斜 −3.5° / 半径正弦起伏）与**不用 `Math.random`** 的确定性要求；punch 幅度 1.06 与 `transform-origin: 50% 55%`（重心略偏下，落定时字不往上飘）；被圈短语独立 `inline-block` 这条实现纪律；画完保持干净静置——不做 line boil / 定格抖动；圈 SVG 层盖在文字之上、`pointer-events:none` 的层级关系。
- 不属于本卡的：demo 那两句「要求可以再高一点，但对自己 / 更松弛一点」的具体文案、28px 字号与 400/600 两档字重、上行用 dim 实色这个排版选择、橙 `#e8720c` 这个取值（参考图③同色系，换任何一个 accent 都成立）、白底舞台、右侧 30% 的主持人（数字人）占位、"两行字落在左侧白区"这个落位、2.4 的行距（那是为了给圈让地方的**排版前提**，不是动效）。
- 迁移接口：`color` 是唯一的颜色入口（同屏只能有它一个"看这里"色）；`padX/padY` 与 `width` 按画幅**同比缩放**（960 宽的值 ×2 用于 1080p），`wobble/grow/turns/tilt` 是**比例/角度常量，换尺寸不要动**；节奏 `draw/punchGap/punchDur/startDelay/hold` 与画幅无关，只跟语速走；换圈的对象：demo 只改 `data-ink`；tsx 要用 demo 的 `ellipsePath(inkBoxOf(...))` 重新生成 `d` / `len` 写进 `ELLIPSE`；目标不是 DOM（视频/图片素材上的字）时把 `inkBoxOf()` 换成手填 `{x, y, w, h, cx, cy}`，`ellipsePath()` 不用动。短语长度超过 8 字时把 `padX` 收到 18~20（长盒子的长短轴比已经够扁，不需要再加横向余量）。
- 底色要求：白底即可（马克笔橙压在白底上是本卡的原生语境）。深底上把 `color` 换成高亮度色（`#ff9f45` 级），并把 `width` 从 3.2 加到 3.8——深底吃掉细线的视觉重量，3.2px 的圈在深底上偏轻。

## 落位自检（2026-09-05 用户定版，选卡时抄进 SHOTBOOK 该镜自检列）
- 标注几何（框 / 圈 / 线 / 箭头 / 放大镜锚点）一律由**目标的实测包围盒**反推——DOM `getBoundingClientRect` / `measureText`，四边留白 16~24px 等距，**不目测**。
- 实现后抽该镜定妆帧核对：标注是否恰好套住 / 指向目标，偏差 **> 8px 返工**（`references/layout.md` §3）。
- 目标会滚动 / 移动时，标注钉在内容坐标系随内容动（SKILL.md ③）。

<!-- ===== /file: video-talkcraft/references/cards/hand-drawn-ellipse.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/highlighter-sweep.md ===== -->

---
name: highlighter-sweep
标题: 荧光笔高亮扫过
优先级: P0
代码: template/cards/highlighter-sweep.tsx
一句话: 半透明黄色荧光笔从左到右 0.4~0.8s 扫过引用文段的关键句，同帧其余文字压暗，扫完整句轻微浮起，读者视线被押着走
适用: 口播引用报告/文献/新闻里的一句话（引文重排成文字卡，tsx 不贴截图）、念到"就是这一句"的时刻；纪录片解说、知识区拆解等冷静讲证据的调性
时长: 起手静置约 0.7s 等语音到位 → 扫过 0.6s（0.4~0.8s 随语速）+ 压暗 0.45s 同帧 → 扫完 0.3s 浮起定格
能量: 低
类别: 强调标注
输入: 文
语义: 引用, 强调
素材形态: 无
位置: 中段
props: hostSrc(未使用)
---

## 意图
口播念一段引用时，观众不知道该看哪一行——荧光笔扫过 + 其余压暗，等于替观众划重点，
把"听到的那句"和"看到的那句"锁在一起。命门：**色块不许盖字**（multiply 或半透明，盖住字
等于涂掉证据）、**扫速对齐朗读**（0.4~0.8s，跟着语音走才像"现场划"而不是特效）、
**必须压暗其余文字**（只加高亮不减环境，强调失效一半）。

常见于：Vox、Johnny Harris、Cleo Abram、James Jani。

## 动效核心
- 引用文字卡先在屏（白底 + 1px #e0e0e0 发丝线 + 圆角 6，640 宽，DOM 文本），卡本身全程静止——缓推属镜头层，不在本卡
- 关键句包一层 `position:relative` 的 span，内部绝对定位色块：#FFE949、opacity 0.6、`mix-blend-mode:multiply`
- 色块四角用不规则 border-radius（`12px 5px 10px 4px / 7px 12px 5px 10px`）模拟笔触，左右各溢出 6~8px
- 扫过：色块 `scaleX 0→1`，`transform-origin: left center`，0.6s，`power2.inOut`（起收笔略缓，匀速像 loading）
- 同帧：其余段落 opacity 1→0.4，0.45s，`power2.out`
- 扫完：关键句整句 scale 1→1.03 + y -2px，0.3s，`power2.out`，origin 左侧——强调落定

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `startDelay` | 0.7s | 卡片静置一拍等语音念到关键句；0 则像自动播放的 PPT，>1.5s 观众开始自己乱读 |
| `sweep` | 0.6s | 0.4~0.8 匹配朗读语速；<0.3s 像渲染 bug，>1s 观众读完了笔还没划完 |
| `dimTo` | 0.4 | 其余段落压暗到的透明度；>0.7 强调不出来，<0.3 像上下文被删掉、观众想去读反而读不到 |
| `liftScale` | 1.03 | 扫完的浮起倍数；>1.08 会破行宽挤排版，1.0 则收尾没有"落定"感 |

## 已知坑
- 色块不透明或叠在文字上层不做 multiply——字被涂掉，一眼假（真荧光笔是透的）。
- 匀速或 <0.3s 扫完——读作程序绘制/渲染故障，不是人手在划。
- 只加高亮不压暗其余文字——画面里所有行权重相同，等于没划重点。
- 色块四角规整直角——读作表格选中/文本选区，不是笔触；必须不规则圆角 + 左右微溢出。
- 高亮的不是完整语义句（半句/跨两行断开）——观众读不出"这一句"的完整性。

## 复用指引
- props：仅 `hostSrc`（声明未使用，本卡无人物）；引文文案在 JSX 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/highlighter-sweep.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。tsx 不收 `src`：关键句是 `.hl-wrap` 包住的 DOM 文本，色块相对文字定位；要在截图上划重点，把引文重排成文字，或按截图实测包围盒给 `.hl-block` 绝对坐标。
- HTML/GSAP：demos/highlighter-sweep/index.html。换文案改 `.quote-line` 各行文本，关键句放进 `.hl-wrap` 内（`.hl-block` 保留在最前）；换色改 `.hl-block` 的 `background: #FFE949` 与 `opacity: 0.6`（深色截图上可改 `mix-blend-mode` 为 `screen` 并换深色荧光）；节奏全在顶部 `CONFIG`（`startDelay` / `sweep` / `dimTo` / `liftScale`）。
- Remotion 移植：色块 `transform: scaleX(${interpolate(frame, [d, d+sweepF], [0, 1], {easing: Easing.inOut(Easing.quad), extrapolateRight: 'clamp'})})` + `transformOrigin: 'left center'`，容器 div 保留 `mixBlendMode: 'multiply'`；压暗用同起点的 opacity interpolate；浮起接在 `d+sweepF` 帧之后 spring 或 quad-out。
- 剪辑软件对应物：剪映——黄色色块素材设混合模式"正片叠底"+ 蒙版"线性"关键帧从左扫到右（或贴纸搜"荧光笔"），其余区域盖半透明黑色块压暗；AE——黄色 Solid 设 Multiply 混合 + Linear Wipe 效果（或 scaleX 关键帧、锚点在左），配 Easy Ease；CapCut——"highlight pen" 贴纸或同样的 mask wipe 做法。

## 动效范围
- 属于本卡的：荧光色块从关键句左端 scaleX 0→1 扫过（0.4~0.8s、power2.inOut、origin left、multiply 混合不盖字、不规则圆角笔触）；同帧其余文字压暗至 0.4~0.7 透明度（0.45s）；扫完整句 scale 1.03 + y −2px 浮起落定（0.3s）。三个动作与一个时序是本卡的全部。
- 不属于本卡的：引用卡片的排版/边框/字体字号、示例文案、演示里曾有的 Ken Burns 缓推（那属于镜头层，由全局系统提供）。
- 迁移接口：荧光色换 `background`（深底改 `mix-blend-mode: screen` + 高亮色）；扫速 `sweep` 对齐朗读时长；压暗程度 `dimTo` 随底色明度调；目标行的选择器与色块几何（left/right 内缩）按实际文字盒调整。
- 底色要求：白底即可（multiply 在浅底天然成立；深底需换 screen 混合并复核字的可读性）。

## 落位自检（2026-09-05 用户定版，选卡时抄进 SHOTBOOK 该镜自检列）
- 标注几何（框 / 圈 / 线 / 箭头 / 放大镜锚点）一律由**目标的实测包围盒**反推——DOM `getBoundingClientRect` / `measureText`，四边留白 16~24px 等距，**不目测**。
- 实现后抽该镜定妆帧核对：标注是否恰好套住 / 指向目标，偏差 **> 8px 返工**（`references/layout.md` §3）。
- 目标会滚动 / 移动时，标注钉在内容坐标系随内容动（SKILL.md ③）。

<!-- ===== /file: video-talkcraft/references/cards/highlighter-sweep.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/host-card-glass-board.md ===== -->

---
name: host-card-glass-board
标题: 人物竖卡玻璃台
一句话: 左 1/3 口播人物装 250×444 的 9:16 竖卡常驻（圆角 22、2px 半透白描边、演播室底），右 2/3 一块 570×408 的玻璃道具台以左缘为轴 rotateY −18° → −10° 显影、sheen 扫一次；板头期数小字 → 大标题逐字解糊 → 英文字距行，板内道具按口播接力：三步 tile 逐个 back.out pop、连接线从左长出带箭头、结果胶囊最后落定；6.1s 板、人、装饰同收
适用: 讲工作流 / 系统 / 步骤（"文稿 → 配音 → 成片"）；讲工具链（tile 换 logo）；多步教程（板上 tile 按词锚逐个 pop、人不动）；竖屏口播原片放横屏成片（竖卡刚好 9:16）。"人一直在、板上换道具"——同一块板能连讲几个道具而不换镜
时长: 6.6s（0.2 板显影 0.7 → 0.3 人物滑入 0.5 → 0.6 sheen 0.9 → 0.9 期数 / 1.0 标题逐字 / 1.45 英文行 → 1.6 / 2.5 / 3.4 三步 tile → 2.05 / 2.95 连接线 → 4.1 结果胶囊 → 6.1 同收 0.5）；成片 tile 时刻对到口播讲到每一步的词锚，板可跨句常驻
能量: 中
类别: 人物互动
输入: 人(必需), 文, 界
语义: 步骤
素材形态: 竖屏, 人脸, 透明通道
位置: 中段
props: hostSrc, tag, title, en, steps, result
优先级: P1
代码: template/cards/host-card-glass-board.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✓ **必需**——人物装进左侧 9:16 竖卡（`hostSrc` alpha 视频；竖屏原片直接用，横屏抠像素材按卡取半身特写） | ✗ 板上不放实拍（玻璃台是道具台不是播放器；要放视频用 split-60-40-story） | ✗（tsx）tile 图标位是字符（`steps[].icon`），不收图；要放 logo 见复用指引 |

人物只吃一种形态：竖卡半身特写。板上道具吃文字 + 图标字符（logo 需改源码，见复用指引）。

## 常用场景
1. 讲工作流 / 系统："文稿 → 配音 → 成片"三步 tile + 结果胶囊（demo 演的）
2. 讲工具链：tile 换成 logo + 工具名 + 一句副标，连接线不变
3. 多步教程：同一块板上 tile 按词锚逐个 pop（2~4 步），人物全程不动；tsx 不做上一步退暗
4. 竖屏口播原片放横屏成片：竖卡 250×444 正好 9:16，不留黑边也不裁人

## 意图
口播里"人 + 图解"最常见的做法是分屏或角标：`split-60-40-story` 是平面 60/40（素材左、要点右），`parallel-items-with-host` 是人物在场的并列句排版，`bed-echo-blur` 是竖屏素材装白边卡。本卡是第四条路：**人物装进一张常驻的竖卡，旁边立一块 3D 道具台**——板本身是舞台，道具（流程 tile、logo、截图缩略、数字）在板上接力登场，人始终在左边说话。价值是"人一直在、板上换道具"：讲三步、讲四个工具、讲一条流程，都不用换镜切人。做对四条：
1. **人物先立住、全程在场**：竖卡 0.3s 滑入后不再动；板上无论换几轮道具，人不缩、不隐、不换位。
2. **板的透视只做一次**：−18° → −10° 显影是登场动作，落定后板角固定；sheen 扫一次即止（循环扫光是廉价感来源）。
3. **道具接力一拍一主角**：tile pop → 连接线长出 → 下一个 tile，同一种入场（back.out），不混淡入 / 飞入；连接线只在两端 tile 都落定后才长。
4. **板上文字在透视下仍可读**：透视角 −8~−12°、标题 46px、tile 标签 20px、副标等宽小字 9px 是"装饰不阅读"档——真要读的字不放小字行。

## 动效核心
- **几何**（960×540，深底 `#12131a`）：竖卡 `left 64 / top 48 / 250×444`，圆角 22，`2px rgba(255,255,255,.42)` 描边，演播室渐变底（`#3a2a58 → #1d2140 → #12131a`）+ 顶部紫色光斑；人物视频 `height 106%`、底部 −6%（半身特写，卡即取景框，容器标 `data-crop-ok`）。玻璃板 `left 340 / top 58 / 570×408`，圆角 18，`perspective 1400`（`perspective-origin 30% 50%`）、`transform-origin 0% 50%`、`rotateY −10°`；材质 = 白 11%→3%→7% 斜向渐变 + `1.5px rgba(255,255,255,.3)` 描边 + 内高光 1px + 大投影。板与竖卡间距 26px（≥24，不重叠）。
- **板头**：期数小字 `top 18`（Courier 13px 字距 4）；大标题 `top 42`（46px 800 字距 6，每字一个 span）；英文行 `top 106`（Courier 12px 字距 5）。
- **板内道具**：tile 组 `top 170`，N 个 140×130 玻璃块（白 8% 底 + 白 30% 描边 + 内高光），间距 41 = 连接线长；整组在板内水平居中（`left = (570 − W)/2`，3 步时 34）；tile 内 44px 圆形图标位（`#8ab4ff`）+ 20px 标签 + 9px 等宽副标；连接线 `top 63`（2px `#8ab4ff` 带辉光，`transform-origin 0 50%`）+ 12px 旋转 45° 的 L 形箭头；结果胶囊 `top 328` 居中（`rgba(138,180,255,.16)` 底 + 60% 描边，17px 700 `#cfe0ff`）。四角 ∿（Courier 26px 白 35%）；地面水印词 COPY / 19 / IDEA（Courier 22px 白 9% 斜体，y 498）。
- **时序**：0→0.8 地面词淡入；0.2 板 `rotateY −18→−10` + opacity 0→1（0.7s `power3.out`）；0.3 竖卡 `x −40→0` + opacity（0.5s `power3.out`）；0.6 sheen `x 0→900`（0.9s `power1.inOut`，skewX −18°）；0.9 期数（0.4s，y 6→0）；1.0 标题逐字 `blur 8→0`、`y 8→0`、opacity（各 0.45s `power2.out`，stagger 0.06）；1.45 英文行；1.6 / 2.5 / 3.4 tile `opacity 0→1`、`scale .8→1`（0.5s `back.out(1.6)`）；每个 tile 起点 +0.45 连接线 `scaleX 0→1`（0.35s `power2.out`），线到位前 0.1s 箭头亮；4.1 结果胶囊 `y 8→0`（0.45s `power3.out`）；6.1 板、人、四角、地面词 opacity→0（0.5s `power2.in`），6.6 结束。落定即静置，无 idle。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `rot` 板落定角 | −10° | −8~−12；更斜板上标题变形、tile 副标不可读；−5 以内读不出"一块板"，成了平面分屏 |
| `rotFrom` 起始角 | −18° | 与落定角差 8° 是"转过来"的可感量；差 >20° 读作翻页 |
| `boardIn` / `hostIn` | 0.7 / 0.5s | 板先起人后到，两者都在 1s 内立住；人物入场 >0.8s 读作慢吞吞 |
| `sheenDur` | 0.9s，只扫一次 | 循环 sheen 是廉价玻璃质感的根源；删掉也成立 |
| `tileAt` | [1.6, 2.5, 3.4]（0.9s 一档） | 跟口播讲到每一步的词锚；<0.6s 一档读作一起出现；tile 2~4 个，5 个以上板放不下 |
| `connDelay` / `connDur` | 0.45 / 0.35s | 线在 tile 落定后才长（先长线读作"路修好了等人"）；线长 41px，>80 两 tile 关系松 |
| `tilePop` | 0.5s `back.out(1.6)` | 过冲是"摆上去"的手感；改 power 淡入就是幻灯片 |
| `resultAt` | 4.1s | 结果在最后一个 tile 落定 +0.7s——留出"看懂三步"的时间再给结论 |
| 竖卡尺寸 | 250×444（9:16） | 竖屏原片直接装；横屏抠像素材按 106% 高取半身；卡宽 <220 人脸太小 |
| 字号 | 标题 46 / tile 标签 20 / 结果 17 / 副标 9 | 标签 20@960 = 40@1080p 条目档下限；9px 等宽副标是装饰档，不承载要读的信息 |

## 已知坑
- 板 sheen 循环扫、tile 落定后呼吸——"活的玻璃"读作模板感，落定即静。
- 人物竖卡随板一起做透视——人是人，不是道具；竖卡永远正视。
- 竖卡与板重叠或间距 <24——两块主体打架；板内 tile 组不居中读作"少了一块"。
- 板上放整段可读文字（段落、长副标）——透视下读不了，要读的字放竖卡对侧的平面层或换卡。
- 连接线先于第二个 tile 出现——线指向空处；线必须在两端都落定后再长。
- 忘了 `data-crop-ok`——verify-demo 会把竖卡对人物的取景判成"截断"；它是刻意特写，要在容器上豁免并在此写明。
- 浅底片直接套这套玻璃材质——白底上玻璃失效；蒙皮见「动效范围」。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/host-card-glass-board.tsx——`hostSrc`（alpha 视频，必需输入）、`tag / title / en`、`steps: {icon,label,sub}[]`（2~4 步，组内自动居中）、`result`；durationInFrames 210；tile 时刻改 `CONFIG.tileAt`，句长改 `exitAt / end`。`steps[].icon` 是字符串字符渲染在 `.hcg-ic` 圆位里，要放 logo 把该 `<div className="hcg-ic">` 换成 `<Img src>`（Remotion 自带），其余不动。
- HTML/GSAP：demos/host-card-glass-board/index.html——`.hostcard` 里的 `.host-placeholder` 由 demo-shell 注入数字人；tile 与连接线的 `left` 按 140 / 41 步进手排，改 `CONFIG`。
- 母本：用户提供的抖音口播截图的版式结构（左人物竖卡 + 右 3D 玻璃板）；板上道具（三步 tile + 连接线 + 结果胶囊）为本库设计，不复刻截图内容。
- 剪辑软件对应物：剪映 / CapCut 两条画中画（人物竖版蒙版圆角 + 板层 3D 旋转关键帧一次）+ 三张贴纸逐个弹出；AE 一个 3D 图层放板 + 卡片预合成 spring 入场。
- 与 layout.md 的接口：两主体组（竖卡 + 板）宽度比 250 : 570 ≈ 1 : 2.3（§4 双元素组允许到黄金比外一档，因为板是道具台不是并列主体）；板内 tile 组按包围盒居中（§4）；人脸安全区落在竖卡内；竖卡（底 491）与板（透视后底 ≈479）是全幅构图、会越过字幕带 y≥450——**字幕不居中**，落在板下方底带且左边界 ≥330（避开竖卡），或右对齐于板（§6 叠层例外：字幕带里只有卡与板的底边，没有正文）。

## 动效范围
- 属于本卡的：竖卡 + 3D 玻璃板的两主体版式；板 −18° → −10° 单次显影 + 单次 sheen；标题逐字解糊；tile → 连接线 → tile → 结果的接力编排（同一种 pop 入场、线在两端落定后才长）；全部落定真静止与同收。
- 不属于本卡的：人物视频本体（演示语境素材）、示例文案、tile 数量与图标字符、地面水印词与四角 ∿（装饰）、深底舞台与玻璃材质的具体色值。
- 迁移接口：`hostSrc / tag / title / en / steps / result`；`tileAt` 按词锚；1080p 输出 px ×2；竖屏输出改上下叠放（人物卡在上 40%、板在下 60% 且不做 rotateY）。
- **底色要求**：demo 为深底演播室调性——这是科技 / AI 创作领域的风格档皮（design-language §0），玻璃材质在白底上失效，所以 demo 例外不用白舞台。浅底片按 §0.4 蒙皮：玻璃板换白卡 + 1px 发丝线 + 唯一投影、tile 换 pastel 底板、连接线与图标换本片 accent、地面词与 ∿ 删除；动效一律不变。
- 取景说明：竖卡对人物是刻意的半身特写（视频高 106%、底部 −6%），容器标 `data-crop-ok` 豁免截断检查；成片人脸安全区 = 竖卡内区域，任何板上元素与字幕不得进卡。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- 竖卡与板间距 ≥24（demo 26）、不重叠；板右缘离画幅右边 ≥48（透视后实测）。
- 板落定角 −8~−12°；定妆帧读一遍板上标题与 tile 标签，透视下仍可读。
- tile 组包围盒在板内水平居中（偏差 >8px 返工）；连接线两端各贴 tile 边缘，箭头不压 tile。
- 人脸安全区（`scripts/face_bbox.py` 实测）全在竖卡内；竖卡与板的底边会进字幕带（491 / ≈479 > 450）——成片字幕**不得居中**，落在板下方底带、x ≥ 330（避开竖卡）或右对齐于板；要字幕居中就得把竖卡缩到 226×402（人脸变小，需用户拍板）。
- 定妆帧三张：1.3s（板已落定、标题解糊中）、3.0s（两个 tile + 一条线）、4.6s（全部落定）；任一帧 sheen 不得还在动（0.6~1.5s 之外无 sheen）。
- `hostSrc` 用横屏抠像素材时核一次人物是否被卡左右边切到肩以外——切到肩是特写，切到脸是错误。

<!-- ===== /file: video-talkcraft/references/cards/host-card-glass-board.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/host-shrink-to-chip.md ===== -->

---
name: host-shrink-to-chip
标题: 人物缩位让台
优先级: P1
代码: template/cards/host-shrink-to-chip.tsx
一句话: 图形要上台时讲者从全屏 0.4s 缩进角落的圆形头像章继续口播，图形从对侧错峰 0.15s 入场接位——让台是单程的，主角让位但人不消失
适用: 口播从"我说给你听"切到"我给你看图/数据/截图"的每一次交接；讲解、财经拆解、教程类需要反复在人与图之间来回的长口播
时长: 缩位 0.35~0.5s（power2.inOut）+ 图形错峰 0.15s 后入场 0.45s；角标期随口播任意长（demo 2s）；单程让台，回归交给应用侧下一节拍
能量: 中
类别: 人物互动
输入: 人(必需), 文, 图
语义: 例证
素材形态: 人脸, 透明通道
位置: 中段
props: hostSrc
---

## 意图
图形上台最常见的两种错法都在丢东西：**切走人**（画面只剩图，说话的人凭空消失，口播变成配音 PPT）
或**图形叠在人身上**（谁都不是主角，观众两边看不清）。缩位让台给出第三条路——人主动缩到角标，
把舞台正中让给图形，但表情、口型、手势全程在线，观众始终知道"是这个人在给我讲"。命门三条：
1. **角标里的人必须还在动**：缩完不许换成静态头像/定格帧，那是"人走了留了张证件照"，比切走更假。
2. **让位与接位必须错峰**：人先动、图形晚 0.15s 进——同帧进出两个主角在画面里打架，读作"卡了一下"。
3. **角标期位置死锁**：chip 不许漂、不许呼吸、不许换位置。让台的意义是"我不抢戏了"，角标一动就前功尽弃。

## 动效核心
- 层级：图形主角（z2）→ 人物裁切窗（z3）→ chip 描边（z4）→ 字幕（z5）
- **工程结构**：裁切窗（`clip-path`，几何锁在舞台坐标系）+ 内层人物层（`transform: scale/x/y`）。
  两层由**同一个进度 t**（0 = 全屏主角，1 = 角标 chip）驱动，`onUpdate` 里一起写——
  拆成两条 tween 会因缓动不同步让人脸半路出框
- 缩位（t 0→1）：`clip-path: inset(...)` 从 `inset(0)` 插值到 chip 的四边内缩 + `round r`（圆角同步长到 r
  才能得到真圆），同时人物层 `scale 1→0.72` + 位移，`transform-origin` 设在**取景锚点**（50% / 32.4% 屏高，
  略低于头部中心，取景才带上肩）；位移 = chip 圆心 − 锚点，缩放绕锚点做所以位移就是两点之差
- 时长 0.42s（0.35~0.5），`power2.inOut`——起收都要缓；这是"让"不是"弹"
- chip 直径 = 屏宽 18%，**落位必须在左下或右下角**（2026-08-27 用户定版：chip 圆心在画面下 1/3 带内、
  下缘贴 action-safe 96px；v3 实测圆心放到 66% 高度被判"太靠上"）；内缩量取屏宽 4.2% / 屏高 8.9%（`chipInsetX` 0.042 / `chipInsetBottom` 0.089）；
  描边 1px #e0e0e0 在缩位 55% 处 0.2s 淡入
- 图形主角：晚于缩位起点 0.15s，从**对侧**（人物 chip 在左 → 图形从右）滑入 90px + 淡入，0.45s `power3.out`
- 角标期：位置全程锁定，画面里唯一在动的是 chip 里的人（口播）
- 回归：tsx / demo 都不做（让台默认单程）。应用侧要做时图形先退、人物后反向放大；顺序反过来（人先放大）会把还没退场的图形压住

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `shrink` | 0.42s | 0.35~0.5 的"让"；<0.3s 像被踢出画面，>0.6s 观众等得心慌、图形迟到 |
| `chipRatio` | 0.18 | chip 直径 / 屏宽。<0.12 脸小到读不出表情，等于放了个图标；>0.26 让台不彻底，还在抢图形的位置 |
| `chipScale` | 0.72 | 角标期人物层缩放，决定 chip 里的取景。调大变大头特写（脸溢出圆边），调小变全身缩略（脸太小） |
| `anchorY` | 0.324 | 取景锚点高度 / 屏高。调小取景上移只剩头，调大会把脸推出 chip 上缘——换素材第一个要重调的值 |
| `gfxLag` | 0.15s | 图形相对缩位起点的错峰。0 = 两个主角同帧打架读作卡顿；>0.4s 中间出现"空台"一拍 |
| `gfxIn` / `gfxSlide` | 0.45s / 90px | 图形接位的入场时长与对侧滑入位移（power3.out） |
| `startDelay` | 0.8s（demo） | 全屏口播先站一拍；成片 = 语音说到"我先把图摆出来"的时刻 |
| `hold` | 2.0s（demo） | 实拍 = 讲完这张图的真实时长，可任意延长；<1.5s 观众还没看完图人就回来了，缩位白做 |

## 已知坑
- **角标里换成静态头像/定格帧**——人不动等于人已经走了，比直接切走更假（口型停了但声音还在）。
- **切走人物再淡入一个 chip**——中间断了一帧连续性，观众读作"两个镜头"，缩位的"同一个人"语义全丢。
- **人物与图形同帧进出**——两个主角在同一时间抢注意力，观感是"卡了一下"，不是交接。
- **角标期让 chip 漂移/呼吸/换位置**——让台的语义是"我不抢戏"，角标一动观众视线立刻被拽回去。
- **只缩不裁（只做 scale）**——人物层直接缩小成"一个悬在角上的小人"，没有 chip 边界就不是"头像章"。
- **裁切窗与人物层分成两条 tween**——缓动不同步，缩位中途脸会挤出圆窗边缘，一眼是 bug。
- **（若做回归）回归时人先放大**——还没退场的图形被压在人后面，读作抢戏而非接管。
- **chip 放在字幕区或图形要用的那一侧**——让位让到别人身上，等于没让。

## 复用指引
- props：仅 `hostSrc`；图形卡内容在 JSX 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/host-shrink-to-chip.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。tsx 无 `src` 通道：图形位是 JSX 里的 `.gfx` 灰阶图表卡，要放截图 / 视频把 `.gfx` 内容换成 `<Img>` / `<OffthreadVideo muted>`（Remotion 自带），位置与入场 transform 不动。
- HTML/GSAP：demos/host-shrink-to-chip/index.html。核心是 `setHost(t)` 这一个函数 + 顶部 `CONFIG`，
  连 `lerp` 一起复制即可摘走；换素材只需重调 `anchorY` / `chipScale` 让脸在 chip 里居中。
  chip 左下↔右下换边改 `chipInsetX`（并把图形 `gfxSlide` 取反保持对侧入场）；成片落位只许下角；
  想要"底部圆角卡"变体：`chipRatio` 换成宽度比 1/3、`round r` 改成固定 12px 圆角、锚点相应下移。
  图形卡（`.gfx`）整块可替换成任意内容。
- Remotion 移植：`const t = interpolate(frame, [d, d+shrinkF], [0, 1], {easing: Easing.inOut(Easing.quad),
  extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})`，同一个 `t` 同时算外层 `clipPath` 字符串与内层
  `transform`（`scale(lerp(1, chipScale, t)) translate(...)`）——帧驱动天然同步、seek 安全；
  人物层用 `<OffthreadVideo>` 抠像素材（tsx 为 `muted transparent`，口播声走成片的配音轨）。
- **分割抠人变体（B-roll 镜头专用，2026-08-27 用户定版）**：让台的对象是一段 B-roll 视频而不是图形卡时，
  角标可以不做圆窗——用 segmentation（绿幕走 `colorkey`，实拍走 RVM/SAM 系人像分割）取 alpha，
  **保留人物真实外形**直接贴在 B-roll 的左下或右下角，读作"人站在素材前面讲"。
  与本卡圆窗路的分工：素材抠不干净、或只要"是这个人在讲"这一个信息 → 圆窗（边界自己吃掉毛边）；
  人物有手势要看、要发布会式临场感 → 分割贴角。两路的缩位时序、错峰 0.15s、位置死锁、
  "角标里的人必须还在动"这四条纪律完全共用；选型与方位见 `references/host-footage.md`
  「人物素材与 B-roll 同屏」。注意分割路没有 `clip-path` 兜底，人物被画框切到时**把人整体往画面里挪**
  或收窄 B-roll，不许等比缩小人物。
- 剪辑软件对应物：剪映/CapCut——人物轨加"蒙版→圆形"，蒙版大小/位置与素材的缩放/位置**同段关键帧**
  （必须同时打，否则脸出框），缓动选"缓入缓出"；AE——人物层套 Mask 或 Shape Layer 做 Alpha Matte，
  Mask Path + Scale + Position 三条属性同帧关键帧 + Easy Ease，或直接父级化到一个 Null 上只 K 一层；
  FCPX——"变形/裁剪"里的圆形遮罩 + Transform 关键帧。

## 动效范围
- 属于本卡的：人物层从全屏到角标 chip 的**缩位**——裁切窗 `clip-path` 四边内缩 + 圆角同步长到 r，与内层 `scale 1→0.72` + 位移由**同一进度 t 驱动**（0.35~0.5s、`power2.inOut`、`transform-origin` 落在取景锚点）；图形主角晚 0.15s 从**对侧**滑入接位的错峰关系；角标期"位置死锁、人继续口播"这条硬约束。让台默认单程；回归属于应用侧的下一个节拍（要做时遵守"图形先退→人再放大"顺序）。
- 不属于本卡的：图形卡的内容/排版/灰阶线框画法（柱子自己的生长动效属于 chart-grow 卡）、字幕文案、chip 描边的颜色粗细、主持人素材本身（demo 由 demo-shell 注入数字人，属演示语境）、chip 落在左下还是右下这个具体选边
（但"必须是下角"属于硬约束，不是可迁移项）。
- 迁移接口：几何全部是**比例**——`chipRatio`（直径/屏宽）、`chipInsetX / chipInsetBottom`（边距/屏宽·屏高）、`anchorX/Y`（取景锚点/屏宽·屏高），换画幅换尺寸不用改代码；换人物素材调 `anchorY` + `chipScale` 对齐取景；`hold` 按口播真实时长设；chip 方位改 `chipInsetX/Y` 后必须把 `gfxSlide` 取反保持"对侧入场"；底部圆角卡变体把 `round r` 换成固定圆角并改宽高比。
- 底色要求：白底即可，但**chip 必须有可见边界**——白底 + 浅色服装时那根 1px #e0e0e0 描边是唯一的边界线，去掉就读不出"头像章"（深底上改为浅色描边或干脆靠明度差，可省描边）。

<!-- ===== /file: video-talkcraft/references/cards/host-shrink-to-chip.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/impact-open-title.md ===== -->

---
name: impact-open-title
标题: 冲击开场
优先级: P0
代码: template/cards/impact-open-title.tsx
一句话: 整句一次砸出（scale 1.08→1 + opacity，0.2s power4.out），末词延后 3 帧单独换成强调色并再 punch 一次；四角 L 取景框与整句**同帧**起但走 0.3s 更慢地向内收 12px，点阵网格最后错峰淡入 0.4s 且只到 0.5 不透明度，副题收尾上浮——一屏只砸一次，其余全是衬
适用: 视频最开头的 3 秒钩子（"三秒抓住重点"这类承诺句）、大章节的开幕标题；节奏快、态度强的短口播与知识区开场；全片只用 1~2 次
时长: 起手静置 0.4s → 整句砸出 0.2s（角框同帧起、0.3s 收完）→ 末词换色 punch 0.167s → 点阵淡入 0.4s → 副题淡入 0.28s → 收尾定格 1.6s；共约 3.14s
能量: 高
类别: 字幕花字
输入: 文, 人(可选)
语义: 钩子, 章节, 标题
素材形态: 无
位置: 开场
props: hostSrc
---

## 意图
开场钩子的困难不在"怎么砸得响"，在**怎么让一屏里只有一个重音**。
参考图这个构图有四类元素（大标题 / 末词强调色 / 四角框 / 点阵网格 / 副题），
新手做法是让它们各自入场、各有一个动作——结果观众的眼睛在 0.5 秒里被拽了五次，
"冲击"变成"混乱"。这张卡的全部设计都在做**分层降权**：

- 标题：`power4.out` 0.2s，最猛最快 → **唯一的砸**
- 角框：与标题**同帧起**，但 `power2.out` 0.3s（慢 1.5 倍、缓动低两阶）→ 同时发生但不争
- 点阵：角框落定后才起，`0.4s` 最慢，且 `opacity` 只到 **0.5** → 最轻
- 副题：最后一拍，灰字小号上浮 8px → 补充信息

命门两条：① **一屏里"砸"只有一次**。角框和点阵是衬，必须比标题更慢更淡；
给角框也来一次 `back.out` 弹入，观众会读作"四个角在抢主标题的位"，构图散架。
② **角框与标题同帧起、不同时停**。错峰让角框晚起会读作"标题出来了，然后有人给它加了个框"（两件事）；
同帧起 + 更慢的曲线才是"框和字是一个版式，只是框更沉"（一件事）。

## 动效核心
- **五个元素、四拍，权重严格递减**：
  - 拍① `t=0.40` 整句：`scale 1.08 → 1` + `opacity 0 → 1`，`0.20s` **`power4.out`**，
    作用在**整行**上（不是逐字），`transform-origin: 0% 50%`（护住左基线）
  - 拍①b `t=0.40`（**同帧**）四角 L 框：各自 `x/y ±12 → 0`（对角单位向量 × 12）+ `opacity 0 → 1`，
    `0.30s power2.out` —— 同帧起、慢 1.5 倍、缓动低两阶
  - 拍② `t=0.70`（整句落定 + 3 帧）末词：`color #1d1d1f → #e8720c` 与 `scale 1.15 → 1` 同轨，
    `0.167s power3.out`（punch 5 帧），`transform-origin: 0% 50%`（1.15 倍只往右长，不压前一个字）
  - 拍③ `t=0.80`（角框落定 + 0.1s）点阵：`opacity 0 → 0.5`，`0.40s power1.out` —— 全卡最慢最淡
  - 拍④ `t=0.96` 副题：`opacity 0 → 1` + `y 8 → 0`，`0.28s power2.out`
- **换色与 punch 必须同轨（同起同停）**：分开写会看到"字先变橙、然后才放大"或反之，
  两个动作读作两拍，末词就有了两次强调
- **末词的 3 帧延后是关键值**：0 帧则整句砸出时末词已经是橙的（观众读作"这句话本来就有个橙词"，
  没有"重点在这里"的推进）；>8 帧则读作两个独立动效（一句话砸出，然后一个词变色）
- **四角 L 框各自只画两条边**：`border: 4px solid` + 对应两边 `border: 0` 成 L。
  臂长必须相等（46×46）——不等长读作随手放的装饰而不是取景框
- **角框 `z-index: 5`**：它框的是**整个画面**，必须压在人物之上；压在人物下面读作"墙上贴的胶带"
- **点阵网格用单个元素 + `radial-gradient` 圆点阵**（`background-size: 24px 24px`，5×4 = 116×92px），
  不是 20 个 div。它只被 `opacity` 驱动，没有任何位移——衬的最低成本实现
- **点阵的 `opacity` 上限 0.5 是硬约束**：>0.6 它开始与标题争视觉重量；
  白底上 0.5 的橙点阵读作"很轻的纹理"，正好
- **副题是灰 `#8a8a8a` 小号 25px**：它不参与强调，是"补充说明"这一档信息
- **层级**：舞台白底 → 点阵（左上偏右，标题上方空区）→ 主持人（右侧）→ 四角 L 框（z:5，压过人物）
  → 整句标题 → 副题
- **强调色只上在末词与衬件上**：`#e8720c`（参考图橙系）用于末词、角框、点阵三处——
  它们是同一个"强调系统"的三个强度档（实色字 / 4px 描边 / 0.5 点阵），不是三个颜色

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `slamDur` | 0.20s（`power4.out`） | 整句砸出时长，**全卡唯一的猛**；>0.35s power4 的劲被摊平读作普通淡入，<0.14s 砸得看不见过程（读作硬切） |
| `slamScale` | 1.08 | 整句起始倍数；<1.04 砸不出来，>1.15 整句起手会超出安全区，且大字缩放会让字重看起来变了 |
| `cornerDur` | 0.30s（= 标题的 1.5 倍） | **本卡第一命门**：角框必须比标题慢；= `slamDur` 则角框与标题同强度，一屏两个砸；>0.5s 角框在标题落定后还在爬，读作加载慢 |
| 角框缓动 | `power2.out` | 比标题低两阶（power4 → power2）；给角框 `back.out` 立刻抢主标题的位 |
| `cornerIn` | 12px | 角框从外侧收进来的距离；0 只剩淡入（可用但少了"取景框合上"的语义），>24px 角框起手在画外，读作四个东西飞进来 |
| `wordDelay` | 0.10s（3 帧） | **本卡第二命门**：末词延后量；0 则整句自带橙词（没有"重点在这里"的推进），>0.27s 读作两个独立动效 |
| `wordScale` | 1.15 | 末词 punch 起始倍数；<1.08 punch 读不出，>1.3 末词起手会撞到前一个字（`origin: 0% 50%` 只能护住左侧） |
| `dotsOpacity` | 0.50 | **点阵的重量上限**；>0.6 点阵与标题争视觉重量（一屏两个焦点），<0.3 点阵等于不存在（可以直接删掉那层） |
| `dotsDur` | 0.40s | 点阵淡入时长，全卡最慢的一条；<0.2s 点阵"出现"了（有了入场感就不是衬） |
| `dotsGap` | 0.10s | 角框落定 → 点阵起淡；0 则点阵与角框同拍（衬件挤在一起），>0.4s 观众已经开始读副题了 |
| `hold` | 1.6s | 收尾定格——完整的开场版式就是落点；开场钩子后面接口播，hold 不必超过 2s |

## 已知坑
- 角框也来一次弹入（`back.out` / 更大的位移）——一屏两个砸，观众不知道该看哪个，"冲击"读作"混乱"。
- **点阵进了相机缩放层就会"抖"**（2026-08-28 实战踩坑）：demo 里镜头不动看不出来，
  成片里叠上 CameraRig 慢推，1.4px 点距 18px 的点阵亚像素爬行，整块读作画面抖动。
  成片参数取点径 ≥2.5px / 间距 ≥32px 并调淡（工程铁律「细密纹理禁入相机缩放层」）。
- 角框错峰晚起（而不是与标题同帧起 + 更慢）——读作"标题出来了，然后有人给它加了个框"，一个版式被拆成两件事。
- 点阵 `opacity` 拉到 1（或用实色圆点 div）——它从衬变成第二个焦点，白底上的橙点阵在 1.0 时比灰副题还重，构图上下颠倒。
- 点阵给位移/逐点错峰（"让它也动一下"）——衬件一有入场动作就不再是衬；这层的正确状态是"它一直在那，只是刚刚才看清"。
- 末词换色与 punch 分成两拍写——看到"字先变橙、然后才放大"，一个词被强调了两次，比不强调更乱。
- 末词 `transform-origin` 取中心——1.15 倍会往左长，压到前一个字上（"住重"叠在一起）；取 `0% 50%` 只往右长。
- 四角 L 框臂长不等（或四个角的 border 宽度不一致）——读作随手放的装饰，取景框语义消失。
- 角框压在人物下面（忘了 `z-index`）——它框的是整个画面，被人物挡住一角读作"墙上的胶带"。
- 逐字砸整句（每个字自己 scale）——那是 `per-character-rise` 的语言；本卡的"一次砸"必须作用在整行的一个 transform 上，逐字会让"一次"变成 N 次。
- 副题用黑字或加粗——它立刻升到与标题同档，一屏三级文字层级塌成两级（design-language §2：一屏 ≤3 级）。
- 角框/点阵用与末词不同的颜色（比如角框橙、点阵灰）——违反唯一强调色红线；它们是同一强调系统的三个强度档，颜色必须同一个。
- 全片用超过两次——开场钩子的力量来自稀缺，第三次出现观众就把它当栏目包装了（design-language §2：hero 字阶全片 1~2 次）。

## 复用指引
- props：仅 `hostSrc`；标题 / 末词 / 副题文案在 JSX 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/impact-open-title.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/impact-open-title/index.html。**换文案改两处 HTML**：
  `#ioLine` 的前半句（3~5 字）+ `#ioLast` 里的末词（**必须是 2~3 字的独立 span**，它是唯一换色的元素），
  以及 `#ioSub` 的副题（10~18 字）。
  换强调色改三处 `#e8720c`：`.io-c` 的 `border`、`.io-dots` 的 `radial-gradient`、`CONFIG.accent`（必须同色）。
  换字号改 `.io-line` 的 `font-size`，`.io-sub` 保持约 1/3；角框尺寸 `.io-c` 的 width/height 按舞台高的 8.5% 给。
  点阵位置改 `.io-dots` 的 `left/top`（要落在标题上方的空区，不能与标题或人物重叠）。
  能量只调 `slamDur`；`cornerDur` 必须保持 `slamDur` 的 1.5 倍、`dotsOpacity` 必须 ≤0.5。
- Remotion 移植：五个元素五个独立的 `interpolate` 组，共用一个 `frame` 时钟。
  30fps 换算：`lead 12f`、`slamDur 6f`、`cornerDur 9f`、`wordDelay 3f`、`wordPunch 5f`、
  `dotsGap 3f`、`dotsDur 12f`、`subDur 8f`。
  整句 `scale: interpolate(f, [12,18], [1.08,1], {easing: Easing.out(Easing.poly(4)), ...clamp})`；
  角框 `[12,21]` 配 `Easing.out(Easing.quad)`（**同一个起点 12、不同的终点**，这就是"同帧起不同时停"）；
  末词换色用 `interpolateColors(f, [21,26], ['#1d1d1f', '#e8720c'])`（Remotion 内置，不用手插值）；
  点阵 `opacity: interpolate(f, [24,36], [0,0.5], {...clamp})` —— **上限写 0.5 不是 1**。
  四角的方向向量在 Remotion 里最省的写法是一个 `[[-1,-1],[1,-1],[-1,1],[1,1]].map()`。
- 剪辑软件对应物：剪映/CapCut——主标题一个文本层（"缩放"108% → 100% + "不透明度" 0 → 100，0.2s），
  末词**必须拆成独立文本层**叠在主标题上（剪映不能给一句话里的单词单独打关键帧），
  该层延后 3 帧再打"缩放"115% → 100% + 换文字颜色（换色做不了补间，直接在起点帧切换颜色即可，
  3 帧的位置观众读作同一瞬间）。四角用四个 L 形贴纸各打"位置"+"不透明度"关键帧，**时长设成主标题的 1.5 倍**。
  点阵用一张 PNG 点阵图（或"网格"贴纸），只打"不透明度" 0 → 50。
  **剪映的"冲击"类入场预设不要用**——它们自带模糊和抖动，会把"一屏一次砸"变成全屏震动。
  AE——主标题 `Scale` + `Opacity` 配 `Easy Ease Out` 手柄拉到 90%（模拟 power4）；
  四角做成一个预合成，`Scale`/`Position` 用同起点、更长的关键帧区间；
  末词用 `Text Animator` 的 `Fill Color` + `Scale`，`Range Selector` 只框住末词，`Offset` 延后 3 帧；
  点阵用 `Grid` 效果或 `CC Ball Action`，只给 `Opacity` 打 0 → 50。
- 与本库同类卡的分工：`chapter-title-card` = 章节转场（有色块压屏 + 扫出，是**转场**不是开场）；
  `behind-text-title` = 标题从人物身后升起（做空间层次，低能量，可长时间挂着）；
  `color-slam-beat-card` = 整屏硬切纯色 + 大字（每句重音都能用，是节拍器）；
  `slab-punch-title` = 两行"铺垫 / 结论"（重点装在色块里，语义是重量）；
  **本卡 = 视频最开头那 3 秒的钩子**，特征是"一次砸 + 一整套衬件同时立起"，
  它给的是"这个片子接下来很紧凑"这个承诺，全片只用 1~2 次。

## 动效范围
- 属于本卡的：「一屏里砸只有一次」这条构图纪律，及其实现——权重严格递减的四层（标题 `power4.out` 0.2s / 角框 `power2.out` 0.3s / 点阵 `power1.out` 0.4s 且 `opacity ≤0.5` / 副题最后一拍）；角框与标题**同帧起、不同时停**（`cornerDur` = `slamDur` 的 1.5 倍、缓动低两阶）这个"同一版式里更沉的那件"的表达法；末词延后 **3 帧**、换色与 punch **同轨同停**、`transform-origin: 0% 50%` 防压字这组末词纪律；砸作用在**整行的一个 transform** 上（不是逐字）；四角 L 框臂长相等 + 对角方向向量 × 12px 向内收 + `z-index` 压过人物；点阵**只被 opacity 驱动、无任何位移**这条衬件底线；末词/角框/点阵三者共用同一强调色（同一系统的三个强度档）。
- 不属于本卡的：demo 那句「三秒抓住重点 / 接下来这三分钟，只讲清楚一件事」的具体文案、72px 与 25px 这两个字号、`#e8720c` 这个橙（同色系任取）、角框 46px 臂长与 4px 描边的具体值（比例是舞台高的 8.5% / 0.75%）、点阵 5×4 的格数与 24px 间距、点阵落在标题上方偏右这个具体位置、副题的灰 `#8a8a8a`、右侧主持人（数字人）占位、以及"标题落在左侧、左边距 78px"这个落位。
- 迁移接口：内容入口三段纯文本（前半句 3~5 字 / 末词 2~3 字必须是独立元素 / 副题 10~18 字）；能量只调 `slamDur`（0.14~0.35s），`cornerDur` 必须跟着保持 1.5 倍比例；`dotsOpacity ≤0.5` 与 `wordDelay 3 帧` 是命门常量，换尺寸换语速都不要动；换字号时主标题 `font-size`、副题（约 1/3）、角框尺寸（舞台高 8.5%）、`cornerIn`（角框臂长的 26%）按同一比例缩放；换强调色改三处（角框 border / 点阵 gradient / `CONFIG.accent`）且必须同色；竖屏把标题拆成两行（每行 4~5 字）、字号收到 60~68px，角框改成只留**对角两个**（竖屏四角框会把画面框得太满，对角两角是 `corner-bracket-frame` 那张卡的做法，在竖屏里更成立）。
- 底色要求：白底即可。深底也成立（标题反白、副题换 `#a1a1a6`、角框与点阵保持强调色），但深底上点阵的 0.5 上限要收到 0.35——深底上同样不透明度的暖色点更显眼。**渐变底与实拍花底不行**：四角 L 框是 4px 硬边线、点阵是 3px 圆点，底上任何高频细节都会让这两层读作噪点而不是版式。

<!-- ===== /file: video-talkcraft/references/cards/impact-open-title.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/info-card-assemble.md ===== -->

---
name: info-card-assemble
标题: 信息卡逐字段自建
一句话: 一张信息卡（书 / 工具 / 人物）像被结构化抽取一样自己长出来：封面 rise → 标题 rise → 三枚标签 pop → 价格行 rise → 三行要点逐行 rise、其中两行被马克底块 5 帧从左刷过 → 三块色卡 pop；相邻字段只隔 2 帧（配方帧）、单字段行程 0.5s 远大于间隔所以画面是"涌"不是"点"，整卡全程极慢前推 1→1.06
适用: 口播介绍"一本书 / 一个工具 / 一个人 / 一门课"的信息卡；"结构化抽取 / 自动填充 / 数据自己长出来"类 AI 话题的演示。输入是文字 + 一张封面 / 头像图，人物不参与
时长: 6.8s（0 封面 → 0.33 标题 → 0.67~1.0 三标签 → 1.33 价格 → 2.5~2.83 三行要点 → 2.83 / 3.0 马克刷过 → 3.33~3.67 色卡 → 0~3.75 整卡前推 → 6.4 整体退场 0.4s）；成片按词锚把字段分成 3~4 组落（图+标题 / 标签+价格 / 要点 / 色卡）
能量: 中
类别: 素材呈现
输入: 图, 文
语义: 例证
素材形态: 无
位置: 中段
props: src, caption, title, pills, price, lines, highlightLines, swatches
优先级: P1
代码: template/cards/info-card-assemble.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 人物不参与（人在场时整卡放人物对侧半幅，卡宽 420 正好一侧） | ✗ 封面位不放视频（动的封面会抢字段落位） | ✓（默认输入）封面 / 头像 / 产品图一张 |

只吃一张图 + 文字（标题、≤3 枚标签、价格或关键数字、≤3 行要点、色卡）。

## 常用场景
1. 推荐一本书的信息卡：封面 → 书名 → 标签 → 价格 → 三行要点（demo 演的）
2. 人物介绍卡：头像 → 名字 → 身份标签 → 代表作三行
3. 工具 / 课程 / 服务的信息卡：图 → 名称 → 标签 → 价格 → 要点
4. "结构化抽取"类 AI 话题："它从一段文字里抓出了这些字段"

## 意图
口播介绍"这本书 / 这个工具"时，`media-pop-in` 是整张截图弹上来、`info-term-card` 是名词解释卡整卡滑入——都是**一块东西一次到位**，观众只能整体看。信息卡逐字段自建把一张卡拆成十几个字段**按信息分组依次长出**：先图后名再标签再要点，读的顺序就是出现的顺序，是库里信息密度最高的一拍。做对四条：
1. **字段时间表用"配方帧"写**（60 分母折成秒）：同类字段隔 2 帧、跨类隔 4~14 帧——间隔的疏密就是信息分组，全改成等间隔就成机械点名。
2. **单字段行程远大于间隔**（0.5s vs 2 帧）：同时有五六个字段在动，画面是"涌"，压到 0.13s 以下就成逐个硬闪。
3. **小件 pop、大件 rise**：标签与色卡从 0.4 pop 到 1（小，过冲不撞邻居），图 / 标题 / 要点只沉 6px（大件 pop 显得廉价）。
4. **整卡极慢前推 6%** 摊在前 75%：与所有字段无关，作用是让密集的小事件之间画面仍在推进。
母本有"原价硬切划线降级 + 新价 spring 跳出"一段，用户定版去掉——口播里价格行与其他字段同样落位，不做反转戏。

## 动效核心
- **几何**（960×540，浅底 #f5f5f7）：信息卡 420×460 @ (270, 40)，白底 + 1px 发丝线 #e0e0e0 + 圆角 18 + 内边距 18，`transform-origin 50% 50%`；卡内自上而下：封面 150 高（圆角 10）→ 标题 24px/700（上距 14）→ 标签行（14px/600、#f2f2f5 胶囊、间距 8）→ 价格行 34 高（28px/700 强调色，tabular-nums）→ 要点三行 17px（行距 1.5，间距 4）→ 色卡三块 26×26 圆角 8。左侧版面说明 20px #7a7a7a @ (80, 60)，宽 160。
- **配方帧** `F(f) = f / 60 × D`，D = 5.0s：封面 0 / 标题 4 / 标签 8·10·12 / 价格 16 / 要点 30·32·34 / 马克 34·36 / 色卡 40·42·44 → 秒：0 / 0.33 / 0.67·0.83·1.0 / 1.33 / 2.5·2.67·2.83 / 2.83·3.0 / 3.33·3.5·3.67。
- **rise**（图 / 标题 / 价格 / 要点）：opacity 0→1 + y 6→0，0.5s `power2.out`。**pop**（标签 / 色卡）：opacity 0→1（power2.out）+ scale 0.4→1（`back.out(1.7)`），0.5s。
- **马克底块**：要点行内绝对定位 `#E8F0FF` 底块（左右外扩 4、上下内缩 3、圆角 4、z-index −1），`transform-origin 0 50%`，scaleX 0→1 0.17s `power1.out`——比字段落位快，读作"笔一划"。
- **整卡前推**：scale 1→1.06，0→3.75s（D×0.75）`power1.out`。
- **退场**：6.4s 整卡 + 说明 opacity→0 0.4s `power2.in`，6.8s 结束。落定即静置。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `frames` 字段配方帧 | 0/4/8·10·12/16/30·32·34/34·36/40·42·44 | 同类隔 2 帧、跨类隔 4~14 帧：疏密就是分组；全部等间隔读作机械点名 |
| `D` 时间基 | 5.0s | 母本 60 帧对应 D；口播放慢就调 D，字段相对节奏不变 |
| `fieldDur` 单字段行程 | 0.5s | 远大于间隔 → "涌"；<0.13s 逐个硬闪 |
| `riseY` | 6px | 大件只沉一点点；>20px 与整卡前推的方向感打架 |
| `popFrom` | 0.4 | 明确的"从无到有"；小件才 pop，大件 pop 显廉价 |
| `hlDur` 马克刷过 | 0.17s（≈5 帧） | 马克笔速度；>0.5s 读作背景色渐变而不是划线 |
| `push` / `pushEnd` | 1.06 / 0.75 | 6% 摊在 3.75s 是纯呼吸；>12% 卡撞画框、内边距里的字被推出 |
| 字段数 | 图 + 标题 + ≤3 标签 + 价格 + ≤3 要点 + ≤3 色卡 | 超出的按 2 帧续排；要点 >3 行卡高不够，删字不缩号 |

## 已知坑
- 字段等间隔——机械点名，分组感没了。
- 单字段行程压短到接近间隔——逐个硬闪，"涌"的密度消失。
- 大件也用 pop——图和标题从 0.4 弹出读作廉价弹窗。
- 2 帧错峰对口播偏密——成片按词锚把字段收成 3~4 组（图+标题 / 标签+价格 / 要点 / 色卡）落，组内保留 2 帧错峰。
- 整卡前推超过 12%——卡撞画框，18px 内边距里的文字被推出边界。
- 母本的"划掉原价 + 新价弹出"——口播里不做（用户定版），价格行普通落位。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/info-card-assemble.tsx——`src` 封面、`title / pills / price / lines / highlightLines / swatches / caption` 文案；durationInFrames 216；放慢改 `CONFIG.D`，句长改 `exitAt / end`。
- HTML/GSAP：demos/info-card-assemble/index.html——`.pc` 里的字段元素与 `CONFIG.frames`；`.ph` 换 `<img>` 即真封面。
- 母本：video-shotcraft `product-card-progressive-assemble`（商品详情卡；本卡换成口播信息卡、去掉划价降级段、浅底色板）。
- 剪辑软件对应物：剪映给每个字段元素单独加"渐显 + 轻微上移"入场并按 2 帧错开、标签用"弹入"；AE 用 Position/Scale 关键帧 + 每层错开 2 帧的 sequence layers；马克底块用 Shape Layer 的 Scale X 关键帧。
- 与 layout.md 的接口：卡 420 宽 @ 270 → 中心 x=480 居中（§4）；卡内字阶 24 / 17 / 14（14 是标签，条目档以下但属胶囊内文字，1080p 下 28 仍 ≥ 最小可读）；左侧说明离左边 80 吸附标题边（§1）；卡底 500 < 字幕带 450？——卡底 500 超过 450，**成片有字幕时卡高压到 400 或上移到 top 24**（§6）。

## 动效范围
- 属于本卡的：配方帧字段时间表（同类 2 帧、跨类 4~14 帧）；rise / pop 两种落位及其分工；马克底块 5 帧刷过；整卡 1→1.06 前推；整体同收。
- 不属于本卡的：封面示意图（演示语境素材，demos/_lib/media，不属于本卡）、具体文案、浅底舞台、卡的具体尺寸。
- 迁移接口：`src / title / pills / price / lines / highlightLines / swatches`；`D` 按口播；1080p 输出卡 840×920、字阶 ×2、riseY 6→12。
- 底色要求：浅底羊皮纸 #f5f5f7（白卡靠发丝线抬起）；白底同样成立；深底时卡换深 tile + 浅字。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- 卡包围盒水平居中（中心 x 偏差 ≤48）；有人物时整卡放人物对侧半幅中心。
- 卡底边 ≤ 430@960（有字幕时）——demo 卡底 500 是无字幕演示，成片按 §6 上移或压高。
- 定妆帧两张：`shot-at 1.0`（三标签刚落齐、价格未出）核对分组感；`shot-at 3.0`（马克刷过中）核对底块只在要点行内、不压字。
- 字段出现顺序 = 阅读顺序（图 → 名 → 标签 → 价格 → 要点 → 色卡），任一字段不得早于其上一组。
- 收尾帧整卡静止、scale = 1.06、所有字段 opacity 1。

<!-- ===== /file: video-talkcraft/references/cards/info-card-assemble.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/info-term-card.md ===== -->

---
name: info-term-card
标题: 名词解释悬浮卡
一句话: 说到专业名词的瞬间，圆角信息卡（图标+词条+两行释义）从人物对侧屏外 0.35s 滑入带 3% 过冲，停留期间 ±6px 正弦浮动像悬浮着，念完原路滑出
适用: 口播里第一次抛出专业名词/黑话时（QE、市盈率、Transformer）；财经、科普、知识区讲解调性，节奏平稳不抢戏
时长: 入场 0.35s + 过冲回稳 0.16s + 悬浮停留 3.2s（浮动周期 2.8s）+ 出场 0.25s，全程约 4s
能量: 中
类别: 数据信息图
输入: 文, 人(可选)
语义: 定义
素材形态: 无
位置: 中段
props: hostSrc
优先级: P1
代码: template/cards/info-term-card.tsx
---

## 意图
口播抛出专业名词时，观众要么懂要么走——这张卡让不懂的人 3 秒内跟上，又不打断懂的人的收看节奏。
命门：**悬**（落位后必须持续正弦浮动 + 大投影，静止的卡读作贴图水印）、
**让位**（从人物对侧滑入，永远不压人脸）、**短**（释义两行封顶，念完就收，赖着不走变成遮挡物）。

常见于：小Lin说（signature）、IC实验室、财经知识区、FCPX/剪映同款预设商品。

## 动效核心
- 卡片结构：浅底卡（demo 为白底 + #e0e0e0 描边）+ 投影（白底上 0 10px 24px rgba(0,0,0,.10) 足够分层；深底需加深）+ 左侧 46px 圆形图标 + 词条名 20px 粗体（缩写小字跟在后面）+ 14px 两行释义
- 入场：x 从屏外 480px → -12px（过冲），0.35s `power3.out`；再 x → 0，0.16s `power2.out` 回稳——过冲约卡宽 3%，给"弹"感
- 悬浮：y 0 → +6px，半周期 1.4s，`sine.inOut` + yoyo 往返（demo repeat 3 即 2 个完整周期）
- 图标微转：rotate 0 → 8°，与浮动同节奏同缓动（`"<"` 对齐），让卡"活着"
- 出场：x → 480px 原路滑出，0.25s `power2.in`，起始时刻 = 入场 0.35 + 回稳 0.16 + 停留 3.2
- 层级：卡在人物层之上、字幕层之下；主持人靠左时卡定位在 right:56px / top:36%

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| slideIn | 0.35s | >0.5s 拖沓像 PPT 飞入；<0.25s 观众来不及注意到卡出现 |
| overshootPx | 12 | 设 0 就没有"弹"感、读作平移贴图；>30 像撞墙回弹，太闹 |
| floatPx | 6 | >10 像漂走/信号不良；<3 看不出在浮，等于静止 |
| floatPeriod | 2.8s | <1.5s 变成上下抖动很躁；>4s 一屏内看不完一个来回 |
| holdBeforeOut | 3.2s | 对齐口播念完释义的时长；太短观众没读完，太长变遮挡物 |
| slideOut | 0.25s | 出场要比入场干脆；>0.4s 恋恋不舍拖节奏 |
| iconTilt | 8° | >15° 图标像坏了在晃；0 则卡少一层"活"的细节 |

## 已知坑
- 浮动幅度开大（>10px）——卡像被风吹走而不是悬浮，一眼假。
- 卡从人物同侧滑入或定位压住人脸——信息层抢了人物层，构图立刻业余。
- 释义写三行以上——观众在停留时间内读不完，等于没解释。
- 去掉投影——卡贴死在背景上，没有"悬"在画面上方的空间感，读作静态水印。
- 落位后完全静止——与截图素材无区分，"悬浮卡"变"贴纸"。

## 复用指引
- props：仅 `hostSrc`；词条 / 缩写 / 释义 / 图标符号在 JSX 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/info-term-card.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/info-term-card/index.html。换文案改 `.term-card` 内三处：`.icon` 里的符号（¥/％/AI 单字都行）、`.term` 词条名与 `<small>` 缩写、`.desc` 释义（两行内）；换色改 `.term-card` 的 `background` 渐变与 `.icon` 的渐变；时长手感全在顶部 `CONFIG`（slideIn / overshootPx / floatPx / floatPeriod / holdBeforeOut / slideOut / iconTilt）。若主持人在右侧：去掉 `.host-left`、卡改 `left` 定位、把 `gsap.set` 与出场的 x=480 改成 -480。
- Remotion 移植：入场用 `spring({frame, fps, config:{damping:14, stiffness:120}})` 插值 x: 480→0（spring 自带过冲，替代两段 tween）；悬浮用 `Math.sin((frame/fps) * 2*Math.PI / floatPeriod) * floatPx` 直接写进 translateY，帧驱动天然可 seek；出场 `interpolate(frame, [outStart, outStart+0.25*fps], [0, 480], {easing: Easing.in(Easing.quad)})`。
- （实测变体）手持词牌：卡不从屏外滑入，而是固定叠在人物胸前手的位置（略带一点手的倾角），人物说话时手偶尔越过卡边缘，产生"举着牌子在讲"的错觉——比屏外滑入更有人味，也天然解决"卡不压人脸"的构图问题；代价是卡的位置被人物姿态锁定，只能用在手位稳定的机位。见小Lin说·韩股崩盘。
- 剪辑软件对应物：剪映＝贴纸/文字模板搜"名词解释/科普弹窗"，入场动画"右滑"+循环动画"轻微浮动"；AE＝position 关键帧入场 + `y` 加表达式 `value + [0, Math.sin(time*2*Math.PI/2.8)*6]`；FCPX 有同款付费预设（Callout/Lower Third Info 类）。

## 动效范围
- 属于本卡的：卡片从人物对侧屏外 x 位移入场（0.35s、power3.out）+ 约卡宽 3% 的过冲、再 0.16s power2.out 回稳的两段式落位；落位后 y ±6px 正弦浮动（半周期 1.4s、sine.inOut、yoyo 往返）——"悬"这层语义靠它和投影共同成立；图标 rotate 0→8° 与浮动同节奏同缓动对齐（`"<"`）；停留 3.2s 后原路 x 滑出（0.25s、power2.in，出场比入场干脆）；"必须带一层投影"这条约束（无投影即读作贴纸水印）。
- 不属于本卡的：卡片的圆角/边框/背景、图标的形状与符号、词条与释义文案、字号行高、主持人占位、字幕行。
- 迁移接口：`offX` 换入场方向（人物在右侧改成 -480，出场自动同向）；`slideIn` / `slideOut` / `holdBeforeOut` 按念完释义的时长缩放；`overshootPx` 取卡宽 3% 左右（换卡宽要同比改）；`floatPx` / `floatPeriod` 控悬浮幅度与周期；`iconTilt` 控图标"活"的细节；换风格只改卡片 `background`、`border` 与投影强度，投影可弱但不能没有。
- 底色要求：白底即可（卡片白底 + #e0e0e0 边 + 一层 10% 黑投影就能与舞台分层）。深底把卡片改浅色块、投影换成更暗更散的一层即可，浮动与入出场时序不变。

<!-- ===== /file: video-talkcraft/references/cards/info-term-card.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/ink-underline.md ===== -->

---
name: ink-underline
标题: 墨迹下划线
优先级: P1
代码: template/cards/ink-underline.tsx
一句话: 一条起笔压满、收笔提细的墨色缎带沿关键词下方 0.4~0.5s 生长出来——变宽不是描边粗细而是路径自己的两条边算出来的，笔尖走过那一刻的宽度就是它的终宽，画完静置
适用: 口播念到"重点是这三个字"的时刻；一句话里给 1~2 个关键词划线（对比式论述尤其合适：先划错的说法、再划对的）；书评/拆解/教学等"我在替你标注"的调性
时长: 起手静置 0.55s 等语音到位 → 单条描画 0.4~0.5s（随词长）→ 条间隔 0.75s（口播逐个点名的节拍）→ 收尾定格 1.0s
能量: 低
类别: 强调标注
输入: 文, 人(可选)
语义: 强调, 对比
素材形态: 无
位置: 中段
props: hostSrc
---

## 意图
本库已有两种"给字加记号"：`highlighter-sweep` 是**荧光笔色块**（一个 multiply 的矩形扫过整句，
强调的是"这一整句"，靠面积压住视线）；`scribble-annotation` 是**圈注箭头**（绕着目标画圈、拉线，
强调的是"画面上的这个东西"，作用对象是素材而不是文字）。

这张卡补的是第三种：**一条有笔压的线，作用在句子里的一个词上**。
它比荧光笔轻——不占面积、不改字的底色，所以能在一句话里连着划两个词而画面不脏；
它比圈注准——线的两端就是词的两端，观众读到的是"就这两个字"，不是"这一块区域"。
口播里最常用的语境是**对比式论述**：先给错的说法划一条，再给对的说法划一条，
两条线的存在本身就把"不是这个、是那个"讲完了。

命门三条：
① **变宽靠路径不靠描边**——`stroke-width` 是常数，画不出笔压。必须沿脊线逐点求法线、
按 taper 向两侧撑出半宽，左岸正走 + 右岸倒走闭合成一个**填充路径**（`fill`，`stroke:none`）。
这是源码 `brush.tsx` 的 `brushRibbon` 的全部内容，也是这张卡与"一条 6px 圆头线"的全部差别；
② **截断脊线而不是 dashoffset**——描画的实现是"每帧按 progress 截短脊线再重算缎带"。
关键是 taper 的 t 仍按**整条脊线**算（不是按已画部分归一化），
于是笔尖此刻的宽度就是它落定后的宽度，读作"笔走过去"；
若按已画部分归一化，每一帧的收笔端都是最细的，看上去像一条会变粗的橡皮筋。
用 `stroke-dasharray` 描一个填充路径更是错的——那会沿着缎带的**轮廓**跑一圈；
③ **画完静置**——源码是"5 个定格姿态 + 每格重新哈希抖动"（`steppedRamp` 3 帧一格 + `hashRange`），
正撞本库"不做沸腾/定格抖动"的定版偏好。本卡改成连续缓动的一次生长，
手作感全部交给形状（脊线的弧度 + taper 的收细 + 边缘颗粒），落定后不再有任何变化。

## 动效核心
- **脊线（spine）**：一条三次贝塞尔，40 点采样。两个控制点上下**反向**偏 `wobble` px
  （30% 处 `+w`、70% 处 `−w`、终点 `+0.6w`）——一个极浅的 S 弯，这是"手画的线"与"CSS border-bottom"的分界。
  `wobble` 只有 ±1px 上下，大了立刻读作波浪线（那是拼写错误的记号）。两条线的 `wobble` 取**反号**，
  避免两条线并置时弯法一致、读作程序批量生成
- **缎带（ribbon）**：沿脊线逐点求法线（前后邻点连线的垂线），半宽
  `half(t) = thickness/2 × (pressure + (release − pressure) × t)`。
  `pressure 1 → release 0.15`：起笔压满纸、收笔提到 15% —— 笔离纸的那一下。
  左岸 `spine[i] + normal × half`、右岸 `spine[i] − normal × half`，右岸倒序接在左岸后面闭合成 `Z`
- **两岸各自平滑**（Catmull-Rom → 三次贝塞尔）：直接 `L` 连采样点会在缎带边缘看出 40 段折线
- **生长**：`progress 0→1`，`power1.out`，0.4~0.5s。每帧 `drawn = round(progress × 39) + 1` 截断脊线重算路径。
  **直写 `setAttribute("d", …)` 而非 `gsap.set`**——后者被排到下一 tick，描画比音效晚一帧
- **边缘颗粒**：`feTurbulence(fractalNoise, baseFrequency 0.7, numOctaves 3)` + `feDisplacementMap`，
  位移量 `thickness × 0.5 × grain`。**seed 固定、不随时间变**——毛边是形状的一部分，不是沸腾。
  `grain 0.5` 是本库取值（源码 1.0）：1.0 在 10px 的线上会把收笔那一端咬断成几点墨
- **墨的透水度 `opacity 0.85`**：1.0 读作矢量色块，<0.7 读作没蘸够墨
- **坐标（tsx 硬编码）**：每条线的 `target` 指向 `BOXES` 里一个「左右缘 + 真实 baseline」盒（demo 运行时用 canvas `measureText` 的
  `fontBoundingBoxAscent` 实测、按 960×540 设计坐标写死；行盒下沿有字体留白，照行盒画线会飘在下面一截），
  线心落在 `baseline + baselineGap`。tsx 改文案/改字号必须重量 `BOXES`；demo 版绑 `data-ink` 运行时自动跟
- **层级**：文字层 → 墨迹 SVG 层（`pointer-events:none`，盖在字上但因为线在 baseline 下方不压字）

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `dur` | 0.4~0.5s | 单条描画时长，按词长给（4 字 0.5s / 2 字 0.4s）；<0.25s 读作一条线突然出现，>0.8s 观众读完了笔还在走 |
| `thickness` | 10px | 起笔处的线宽（收笔处是它的 15%）；<6px 笔压的收细看不出来（变宽变成噪声），>16px 读作荧光笔色块、抢字 |
| `pressure` / `release` | 1 / 0.15 | 起笔压 / 收笔压。两者相等 = 等宽线（笔感全无）；`release` >0.5 收笔不够细、读作马克笔；反过来 `pressure` 小 `release` 大 = 起细收粗，那是"提笔顿收"的另一种笔法，也成立 |
| `wobble` | ±1px | 脊线弯量；0 = 直尺画的线，>3px 读作波浪线（拼写错误记号）。两条线取反号 |
| `baselineGap` | 6px | 线心离 baseline 的距离；<3px 压住字的下缘（撞到"了/丁"的竖钩），>12px 线飘在句子外面 |
| `overhang` | 8~9px | 两端各超出文字多少；0 = 线与字严格等长、读作表格边框，>20px 读作划掉了旁边的字 |
| `grain` | 0.5 | 边缘颗粒；0 = 矢量光边（干净但少一层纸感），≥1 会把收笔的细端咬断成几点墨 |
| `inkOpacity` | 0.85 | 墨的透水度；1.0 读作矢量色块，<0.7 读作没蘸够墨 |
| `gapBetween` | 0.75s | 两条线之间的间隔，对齐口播逐个点名；<0.3s 两条线像同时出现、对比感消失 |
| `samples` | 40 | 脊线采样点数；<20 缎带边缘看出折线，>80 白算 |

## 已知坑
- 用 `stroke-width` 画线然后指望有笔压——描边宽度是常数，怎么调都是等宽线；变宽必须是填充路径的两条边算出来的。
- 用 `stroke-dasharray/dashoffset` 描这个填充路径——dash 会沿着缎带的**轮廓**跑一圈（先描上边再描下边），看上去像一根线在绕圈，不是笔在走。
- taper 的 t 按"已画部分"归一化——每一帧的笔尖都是最细的，落定后又变粗，读作一条会膨胀的橡皮筋。t 必须按整条脊线算。
- 照行盒（`getBoundingClientRect`）算 baseline——中文字体行盒下沿有一截留白，线会飘在句子外面；必须用 `measureText` 的 `fontBoundingBoxAscent`。
- 画完加沸腾/定格抖动（源码原版就是 5 个定格姿态 + 逐格重新哈希）——撞本库定版偏好，且在 1080p 上读作渲染不稳定。
- `grain` 照搬源码的 1.0——在 10px 的线上位移量 5px，收笔那一端（宽度只有 1.5px）会被咬断成几点墨，读作墨迹干了。
- 一句话里划 3 个以上的词——同屏重音只能有一个，第三条线出现时观众已经不知道该看哪；上限 2 条。
- 线宽给 16px 以上——读作荧光笔，那是 `highlighter-sweep` 的地盘，且色块会压住字的下缘。
- 两条线的 `wobble` 同号同量——并置时弯法完全一致，读作程序批量生成（手画不会连续画出两条一样的弧）。
- 在 `onUpdate` 里用 `gsap.set` 改 `d`——被排到下一 tick，描画比 scratch 音效晚一帧。

## 复用指引
- props：仅 `hostSrc`；台词在 JSX 常量、墨迹盒坐标在 `BOXES` 里，换内容需改源码并重量坐标。
- Remotion/tsx（skill 首选）：template/cards/ink-underline.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG（`marks` 每项一条线），坐标在 `BOXES`，时长/尺寸在 meta。
- HTML/GSAP：demos/ink-underline/index.html。核心是三个函数——`spineOf()`（脊线）、
  `ribbon(spine, o, progress)`（变宽缎带，**这个函数可以整段抄走**，它与本卡的其他部分无耦合）、
  `baselineOf()`（量真实 baseline）。加一条线就在 `CONFIG.marks` 里加一项并给目标元素打 `data-ink`。
- Remotion 移植：直接用 template/cards/ink-underline.tsx——`sampleCubic` / `spineOf` / `halfWidth` / `ribbon` 四个纯函数可整段抄走（与其余部分无耦合）；
  生长是连续的 `power1Out`（`tw(t, at, dur, power1Out)`），不做定格抖动，`wobble` 为常量，`grain` 0.5。
  秒↔帧（30fps）：描画 0.5s = 15 帧、静置 0.55s = 16.5 帧、间隔 0.75s = 22.5 帧。
- 剪辑软件对应物：AE——用 Shape Layer 的 Stroke + **Taper**（AE 2020+ 内置起收笔收细，
  正是本卡的 taper）+ Trim Paths 的 End 关键帧做生长，Roughen Edges 给颗粒；
  剪映/CapCut——没有真正的变宽笔触，退而用"手写字/笔刷"贴纸的描出动画（形状固定、只能选预设），
  或者预先在 AE/Figma 里把缎带导成序列帧再当素材用。
- 与本类其余卡的分工：**本卡** = 作用在句子里的**一个词**上的有笔压的线（不占面积，一句可两条）；
  **highlighter-sweep** = 荧光色块扫过**整句**（靠面积压视线，必须配其余文字压暗）；
  **scribble-annotation** = 圈/箭头作用在**素材上的元素**（圈住价格、指向按钮）。
  一句话里三者不叠加。

## 动效范围
- 属于本卡的：变宽缎带的生成机制（脊线 → 逐点法线 → taper 半宽 → 左岸正走右岸倒走闭合成填充路径）；`pressure 1 → release 0.15` 的起笔压满收笔提细；截断脊线做生长且 **taper 的 t 按整条脊线算**这条纪律；脊线两控制点上下反偏 ±1px 的浅 S 弯、两条线取反号；静态 `feTurbulence + feDisplacementMap` 边缘颗粒（seed 固定不随时间变）；`opacity 0.85` 的墨透水度；线心落在真实 baseline + 6px；描画 `power1.out` 0.4~0.5s、条间隔 0.75s 的节拍；画完静置不抖这条取舍；`onUpdate` 里直写 `setAttribute` 以免晚一帧。
- 不属于本卡的：demo 的两行示例台词与"成本上涨/渠道结构"这组对比文案、字号 30px 与行高 1.95、墨色 `#6f7f35`（换成任何深色都成立，它只需与底色有对比）、被划词只加字重不加颜色这个排版选择、主持人占位（演示语境素材）、右侧 70% 布局。
- 迁移接口：`CONFIG.marks` 的每一项 = 一条线，`target` 指向 `BOXES` 的键（demo 里是 `data-ink` 元素）；`color` 换墨色（深底改浅色墨，其余参数不变）；`thickness` 按字号等比给（30px 字号用 10px 线 ≈ 字号的 1/3，1080p 上 60px 字号给 20px）；`dur` 按词长给；`baselineGap` / `overhang` 是**手感常量**，随字号等比缩；`grain` 随 `thickness` 反向调（线越细颗粒要越小，否则咬断收笔端）。
- 底色要求：白底/浅底最佳（墨是深色，靠对比成立）。深底把 `color` 换成浅色墨即可，`inkOpacity` 可提到 0.9（浅色墨在深底上透太多会显灰）。

## 落位自检（2026-09-05 用户定版，选卡时抄进 SHOTBOOK 该镜自检列）
- 标注几何（框 / 圈 / 线 / 箭头 / 放大镜锚点）一律由**目标的实测包围盒**反推——DOM `getBoundingClientRect` / `measureText`，四边留白 16~24px 等距，**不目测**。
- 实现后抽该镜定妆帧核对：标注是否恰好套住 / 指向目标，偏差 **> 8px 返工**（`references/layout.md` §3）。
- 目标会滚动 / 移动时，标注钉在内容坐标系随内容动（SKILL.md ③）。

<!-- ===== /file: video-talkcraft/references/cards/ink-underline.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/keyword-pop-highlight.md ===== -->

---
name: keyword-pop-highlight
标题: 关键词弹出强调
优先级: P0
代码: template/cards/keyword-pop-highlight.tsx
一句话: 字幕念到关键词的瞬间，该词带色块底从 0 弹到 1.65 倍再回落定格 1.15 倍，画面跟着微震一下
适用: 每段口播的信息峰值（数字、结论、反转词）；真人出镜与无出镜都通用，是口播强调的第一默认动作
时长: 弹出 0.18s → 停在 1.65 倍至震动结束（弹出起 0.24s）→ 回落 0.22s，总 0.46s；关键词比整句晚 0.4~0.6s 出现（demo 0.55s）
能量: 高
类别: 字幕花字
输入: 文, 人(可选)
语义: 强调, 数据
素材形态: 无
位置: 任意
props: hostSrc
---

## 意图
口播的听觉重音需要一个视觉重音来配对——观众静音刷视频时也能抓到重点。
命门：**快**（弹出 ≤0.2s，慢了像 PPT 入场）、**晚半拍**（等语音念到该词才弹，
与整句字幕同时出现就没有"砸出来"的劲）、**有反冲**（过冲到 1.65 再回落，
线性放大读作缩放素材而不是强调）。

## 动效核心
- 关键词单独包 span，`transform-origin` 设在词底部中心（50% 80%）
- 入场：scale 0→1.65 + rotate -8°→2°，0.18s，`power4.out`
- 回落：scale 1.65→1.15 + rotate 归零，0.22s，`back.out(2.5)`——定格比正文略大
- 冲击帧：弹出瞬间整个画面 x 方向 ±7px 抖 3 个来回（0.04s/次），传导"砸"的力
- 色块底：暗红色块 skewX(-6°)，跟词一起弹；关键词用高饱和黄压在色块上，与正文字色拉开
- 关键词 span 左右留 ≥0.3em 外边距：1.15 倍定格 + skew 会横向溢出，边距不够色块压相邻字

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 最大倍数 | 1.65 | >1.9 读作搞笑/整活；<1.3 强调感不足 |
| 弹出时长 | 0.18s | >0.3s 读作 PPT 动画；<0.1s 看不清运动方向 |
| 定格倍数 | 1.15 | 回到 1.0 强调消失；>1.3 破坏整句排版 |
| 延迟 | 0.4~0.6s | 必须对齐语音重音；提前出现剧透，滞后读作卡顿 |
| 震动幅度 | 7px | >12px 读作故障；0 则"砸"感减半 |
| 词左右边距 | 0.36em | 给定格放大 + skew 留溢出位；<0.2em 色块会压住相邻字 |

## 用量上限（2026-08-27 用户定版）
- 本卡是**唯一允许作用于底部跟读字幕的动效**（底部字幕素排铁律见 design-language.md §5），
  且同一个视频内**最多出现 3 次**，除非用户明确要求更多。超了不是多强调，是把强调稀释成噪音。
- `template/motion-systems/Subtitles.tsx` 的 `keywords` prop 内建这个上限自检（超 3 个直接抛错，
  用户明确要求时传 `allowExtraKeywordPops` 放行）。

## 已知坑
- 与整句字幕同帧出现——没有时间差就没有强调，一眼假。
- transform-origin 用默认中心——词往上下两头胀，挤压相邻文字；设在词底才像"从字幕里长出来"。
- 用透明度渐显代替 scale 弹出——读作打字机而不是重音。
- 一句里弹两个以上关键词——重音互相打架，等于没有重音。

## 复用指引
- props：仅 `hostSrc`；字幕与关键词文案在 JSX 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/keyword-pop-highlight.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/keyword-pop-highlight/index.html，改 `.caption` 内文案和 `CONFIG` 常量即可；色块颜色在 `.kw::before`。
- Remotion 移植：用 `spring({frame, config:{damping:12, stiffness:200}})` 驱动 scale，震动用 `Math.sin(frame*3)*7*exp(-frame/4)` 衰减；关键词 delay 换算成帧数对齐音频波形峰值。
- 剪辑软件对应物：剪映"文字模板→综艺感"类；AE 里是 scale 关键帧 + Overshoot 表达式；CapCut "text bounce"。
- （实测变体）强调的第三条通道是**字体对比**——缩放弹跳、换色之外，还可以把重音词换成衬线斜体大字、运动刻意做轻不过冲，走克制编辑气质而非综艺感。这条通道已独立成卡：见 references/cards/type-contrast-emphasis.md（TheAIScaler 8/10 shorts 的招牌机制）。分工：本卡=听觉重音要"砸"（弹跳+震动+色块），type-contrast-emphasis=重音要"稳"（字形落差+轻上滑）；**两者不可在同一句里混用**，回弹与气质对比同屏一眼假。

## 动效范围
- 属于本卡的：关键词 scale 0→1.65 + rotate −8°→2° 弹出（0.18s、power4.out、transform-origin 设在词底 50% 80%）；scale 1.65→1.15 + rotate 归零的过冲回落（0.22s、back.out(2.5)）；同帧整屏 x ±7px 抖 3 个来回的冲击帧（0.24s、匀速）；色块底与词同 transform 一起弹（skewX −6° 静态形变，不单独做动画）；关键词比整句字幕晚 0.4~0.6s 出现的时序关系。
- 不属于本卡的：主持人剪影与字幕区占位、示例台词、字号字重与字体、色块与关键词的具体颜色值（暗红/高饱和黄只是"色块与字要拉开对比"的一种取值）。
- 迁移接口：`popScale`/`restScale` 定强调量级，`popIn`/`settle` 定快慢，`delay` 对齐语音重音帧，`shakePx` 定冲击力；换配色改 `.kw` 的 color 与 `.kw::before` 的 background（只需保证两者与正文字色三方对比成立）；换尺寸时 padding/margin 用 em 跟字号等比缩放，词左右边距别低于 0.2em。
- 底色要求：白底即可（色块底自带不透明背景，动效不依赖舞台底色；深底上只需把正文字色与关键词色反过来配）。

<!-- ===== /file: video-talkcraft/references/cards/keyword-pop-highlight.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/lead-word-zoom-assemble.md ===== -->

---
name: lead-word-zoom-assemble
标题: 首词占满补句
一句话: 首词"效率"以 2.3 倍字号独占画面正中、hold 0.4s 期间继续推近 6%；随后一条 power3.inOut 曲线同时完成"缩回终字号"（0.4s）与"整行左滑归位"（0.8s，同起同曲线时长两倍），后续词各自从槽位右侧 28px 被推进来（0.4s power4.out，淡入只 2 帧），结论词落位即强调色；整行落定后上移 28px、副行同一时窗浮出，静置 3s 后同收
适用: 一句话主张先让主语立住（"效率 才是唯一的护城河"）、产品名 / 人名 introducing 字卡、数字先行（"3 倍 的产出，同样的时间"）、反转句先亮否定词（"不是 → 不是不努力，是方向错了"）；金句 / 转折镜头的文字面，首词 ≤4 字
时长: 4.8s（0.1 首词现 → 0.5 缩回 + 左滑 → 0.7 / 0.83 / 0.96 后续词推入 → 1.4 上移 + 副行 → 4.4 同收 0.4s）；成片按口播念出首词的时刻起手，念到后续词时它们正好推入
能量: 高
类别: 字幕花字
输入: 文
语义: 金句, 转折, 标题
素材形态: 无
位置: 任意
props: words, subline, accentIndex, accent
优先级: P1
代码: template/cards/lead-word-zoom-assemble.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 纯文字卡；人在场时整行放人物对侧半幅，首词 2.3× 时不得入人脸安全区 | ✗ | ✗ |

作用于金句 / 主张 / 标题层，不作用于底部跟读字幕。

## 常用场景
1. 一句话主张，主语先立住："效率 → 效率 才是唯一的护城河"（demo 演的）
2. 产品名 / 人名 introducing 字卡（首词换强调色，`accentIndex = 0`）
3. 数字先行："3 倍 → 3 倍 的产出，同样的时间"
4. 反转句：先亮否定词"不是"→ 补齐"不是不努力，是方向错了"

## 意图
口播念一句主张时，重音通常落在第一个词上（"效率——才是唯一的护城河"），`type-contrast-emphasis` 是念到重音词才放大，而这张卡反过来：**重音词先以占满画面的尺度出现，再缩回让整句补齐**——观众先被一个词砸到，再看懂它在句子里的位置。尺度差（2.3×）是冲击的来源，"一条曲线"是电影感的来源。做对四条：
1. **缩回与左滑共用一条缓动**：字号落定后位置还在走那段"滑行尾巴"是电影感来源；各走各的曲线会断成"先缩小、再滑走"两拍。
2. **后续词是被推进来的，不是淡进来的**：位移 28px 走 0.4s，淡入只 2 帧；淡入拉长词就"浮现"，推入的力学感消失。
3. **支点钉首词中心**：transform-origin = 首词中心在整行里的占比，缩放期间首词不挪，观众的视线锚点不动。
4. **上移与副行同一时窗**：整行让出的空间当帧被副行填掉；先上移再出副行会多一个空当拍。

## 动效核心
- **几何**（960×540）：整行 56px / 600 / 字距 −1 墨色，`.lwz-line` 绝对定位 `left 50% / top 250`，基准 `translate(-50%, -50%)`；词之间用独立 inline-block `.lwz-sp`（宽 0.28em）撑间隔——跟在词 span 内部尾随的空格会被行盒裁掉（母本判例）；结论词 `#0066cc`。副行 22px `#7a7a7a`，`top 318` 居中。整行上移后与副行的组中心 ≈ y 270。
- **支点实测**：`L = 整行宽`、`c = 首词 offsetLeft + 宽/2`、`ratio = c/L` → `transform-origin: ratio×100% 50%`；偏心距 `slide = L × (0.5 − ratio)`，让 2.3× 时首词落在画面正中。
- **首词独占**：0.1s 首词 0.15s 淡入；整行 scale 2.3 → 2.438（×1.06）0.4s `power2.out`（hold 期继续朝观众来）。
- **缩回 + 左滑**：0.5s 起 scale 2.438 → 1 0.4s `power3.inOut`；x slide → 0 0.8s `power3.inOut`（同起、同曲线、时长两倍）。
- **后续词**：第 i 词在 `0.5 + 0.2 + i×0.13` 起 x 28 → 0 0.4s `power4.out`，opacity 0 → 1 0.07s；间隔 span 同帧硬现。
- **上移 + 副行**：1.4s 整行 y 0 → −28 0.53s `power2.out`；副行 opacity 0 → 1、y 16 → 0 同窗同曲线。
- **退场**：4.4s 整行 + 副行 opacity → 0 0.4s `power2.in`，4.8s 结束；不做母本末段的 crash-zoom 推近失焦（口播里落定即静，转场交给运动承接六式）。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `leadScale` | 2.3 | 让首词横向溢出一点（"太大了装不下"）；<1.8 只是稍大的字，冲击消失；首词 >4 字 2.3× 会溢出两侧 |
| `pushScale` | 1.06 | hold 期"还在朝观众来"的最小可感量；>1.15 缩回时读作反向弹跳 |
| `hold` | 0.4s（≈12 帧）| <0.27 读不完一个词；>0.67 整句节奏塌 |
| `shrink` / `slide` | 0.4s / 0.8s，同 power3.inOut | 左滑比缩回长一倍是"滑行尾巴"；单独给缩回一条更快的曲线整行会"先缩完再滑" |
| `wordDelay` / `wordStagger` | 0.2s / 0.13s（≈4 帧）| 首词开始缩回才放后续词；错峰 0 则整段后缀一起进，回到"整句淡入" |
| `wordPush` / `wordFade` | 28px / 0.07s | 28px ≈ 0.5em 是"刚从槽位外面"；>1em 读作从画外飞入；淡入 >0.2s 词会"浮现" |
| `up` / `upDur` | −28px / 0.53s | 让出副行的位置；副行必须同窗 |
| `holdEnd` | 3.0s | 读整句 + 副行的时间；<1.5 观众来不及读副行 |
| 字距 | −1px（负字距）| 负字距在放大 2.3 倍时才不散架；正字距的大字读作横幅 |

## 已知坑
- 缩回与左滑各走各的曲线——断成"先缩小、再滑走"两拍。
- 后续词淡入拉长到 0.2s+——词"浮现"而不是"被塞进槽位"。
- 词间空格写在词 span 内部——落定后所有词黏成一团（母本判例）；间隔用独立 inline-block。
- 首词超过 4 个字——2.3× 溢出画面两侧；改短首词或降到 1.8×（同时接受冲击减半）。
- 保留母本末段 crash-zoom——单独播像"没结束"；口播里落定即静。
- 副行等整行上移完再出——多一个空当拍。
- 正字距大字——读作标语横幅，不是一个词砸过来。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/lead-word-zoom-assemble.tsx——`words`（首词在第一个）/ `subline` / `accentIndex` / `accent`；durationInFrames 156；支点用 `useLayoutEffect + delayRender` 量一次。
- HTML/GSAP：demos/lead-word-zoom-assemble/index.html——改 `.lwz-line` 里的词与 `.lwz-sub` 文案，`CONFIG` 调节奏；支点由脚本实测。
- 母本：video-shotcraft `lead-word-zoom-assemble`（砍掉末段 crash-zoom 交棒；基线实测改为行盒垂直中心）。
- 剪辑软件对应物：剪映给首词单独一个文本层做"缩放 + 位置"关键帧、其余词做"位置 + 不透明度"关键帧（不透明度 2 帧内完成）；AE 用文本图层 Anchor Point 钉在首词中心 + Scale/Position 同一缓动曲线，后续词用 Text Animator Position 按词 Range。
- 与 layout.md 的接口：整行 + 副行组中心 ≈ y 270 中线（§1）；水平居中偏差 ≤48（§4）；hero 级独句 56px@960（§5）；有人物在场时整行放人物对侧且首词 2.3× 不入人脸安全区。

## 动效范围
- 属于本卡的：首词 2.3× 独占 + hold 期 6% 推近；缩回与左滑同起同曲线（1:2 时长）；后续词推入 28px / 淡入 2 帧的比例；支点钉首词中心；上移与副行同窗。
- 不属于本卡的：文案、强调色值、副行有无（可省）。
- 迁移接口：`words / subline / accentIndex / accent`；1080p 输出字号 ×2（112 / 44）、wordPush 56、up −56。
- 底色要求：白底 / 羊皮纸底成立；深底反色即可。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- 定妆帧三张：首词独占（0.3s）、缩回中（0.9s）、落定后（2.6s）。首词独占帧首词水平居中偏差 ≤48，两侧不越出安全边 48。
- 缩回中那一帧首词中心 x 与独占帧一致（支点判据），后续词部分可见但淡入已完成。
- 落定后整行 + 副行组包围盒中心 y ≈ 270 ± 16，水平居中偏差 ≤48。
- 结论词换色只发生在结论词上，句中不出现第二个强调色。
- 落定后 ≥45 帧真静止。

<!-- ===== /file: video-talkcraft/references/cards/lead-word-zoom-assemble.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/line-by-line-slide.md ===== -->

---
name: line-by-line-slide
标题: 逐行滑入
优先级: P1
代码: template/cards/line-by-line-slide.tsx
一句话: 多行要点一行一行从左侧（字号 78%）外滑进来（位移 0.47s / 淡入 0.90s，行间错峰 0.13s），读完整叠再从同一侧往右穿出去——进从左、出向右不是倒放，出场错峰只有入场的一半、横向位移还要迟 0.27s 才起
适用: 3~4 行并列要点/步骤/清单的整段上屏——"三件事""两个前提""四步走"这种口播段落；也用于分行的金句（每行一个短句）；不适合单行文字（退化成普通滑入）与 5 行以上（首行早已淡出，"一叠"读不出来）
时长: 起手静置 0.3s → 逐行入场 0.90s / 错峰 0.133s（3 行在 1.47s 处全实）→ 停留 1.4s → 逐行出场 0.60s / 错峰 0.067s → 共约 3.6s
能量: 中
类别: 字幕花字
输入: 文
语义: 步骤, 列举
素材形态: 无
位置: 任意
props: 无
---

## 意图
"三件事"这类并列要点在口播里极常见，而它有一个专属的难题：**整段是一个整体，但要一行一行讲**。
把三行一起淡入观众读不出顺序；把三行做成三段各自入场的动画又割裂成三张卡。

这张卡的解法是**一叠里的错峰**：行间错峰 0.13s（4 帧）——大到能读出"第一行、第二行、第三行"的先后，
又小到三行的入场在时间上大幅交叠（第一行还在淡入，第三行已经起手了），所以观众收到的是
"一叠东西滑进来，而且有顺序"，不是三次独立的入场。

真正把这张卡与市面清单预设区分开的是**出场**：
① **进从左、出向右**——不是倒放。整叠是"穿过画面"而不是"来了又退回去"，
这让它天然可以接下一段内容（退回去的动作会读作"这段作废了"）；
② **出场的横向位移比淡出迟 0.27s 起**——前 0.27s 整叠只在原地变淡、不动，
然后才被"抽走"。这一下延迟是全卡最精致的地方：它让出场读作"整叠先松开、再被带走"，
而位移与淡出同起会读作"被一把扫掉"（粗暴，且会让观众觉得没读完）；
③ **出场错峰只有入场的一半**（0.067s vs 0.13s）——出场不需要再讲一遍顺序，
所以收得更齐、更快，整叠几乎是一起走的。

## 动效核心
- **入场：每行两条轨，位移先停**
  - 位移轨：`translateX −distance → 0`（distance = 字号 78%，demo 60px ⇒ 47px），`enterTravel = 0.467s`
  - 淡入轨：`opacity 0 → 1`，`enterDur = 0.90s`（= 位移的 2.1 倍，位移占 52%）
  - 缓动都是 `cubic-bezier(0.22, 1, 0.36, 1)`（缓出：冲进来再长距离缓收）
  - 行间错峰 `enterStagger = 0.133s`（源码 4 帧 @30fps）
- **出场：淡出立刻起、位移迟 0.27s 起、方向朝右**
  - 淡出轨：`opacity 1 → 0`，`exitDur = 0.60s`，**从出场时刻立刻开始**
  - 位移轨：`translateX 0 → +distance`，**延迟 `exitDelay = 0.267s` 才起**，时长 `0.60 − 0.267 = 0.333s`
    （两轨同时收尾——tsx 把位移的输入区间写成 `[out + exitDelay, out + exitDur]`，即同一条时钟上的后段）
  - 缓动 `cubic-bezier(0.64, 0, 0.78, 0)`（**缓入**：先粘住再加速甩走，与入场的缓出方向相反）
  - 行间错峰 `exitStagger = 0.067s`（源码 2 帧）= 入场错峰的**一半**
- **入场与出场顺序接力**：tsx 按 `t < out` 分段——出场前走入场轨、出场后走出场轨（demo 用 GSAP 顺序 tween），
  两者时序等价；因为出场永不早于入场结束，不需要相乘 / 相加的叠加写法
- **出场时刻**：tsx `exitStart = enterEnd + hold`（`enterEnd = lead + enterDur + (n−1)×enterStagger`）——
  **出场永远不早于入场结束**；demo 的 GSAP 时间线同样排在"最后一行入场结束 + hold"之后
- **左对齐是硬要求**（源码 `textAlign: left`）：逐行滑入靠**共享的左端**才读作"一叠"，
  居中对齐会让每行的左端各自不同、滑入的方向感散掉
- **每行是 `display: block` + `transform-origin: 0% 50%`**（左端为轴），只走横向位移，不做竖向
- **行高改动**：源码 `lineHeight: 1.1` 是拉丁字母值；中文字面高，1.1 会让行与行粘住，本库取 **1.35**
- **层级**：舞台白底 → 左对齐文本块 → 行（唯一被 transform 的元素）

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `lines` 行数 | 3~4 | 本卡的硬约束；1 行退化成普通滑入（换 `soft-blur-in`），2 行读不出"一叠"，≥5 行首行早已淡出、整叠的整体感消失且观众读不完 |
| `enterDur` | 0.90s | 每行淡入时长；<0.5s 三行入场挤成一团（错峰读不出顺序），>1.3s 整叠上屏要 2s 以上、口播已经讲到第二点了 |
| `enterTravel` | 0.467s | **位移占 `enterDur` 的 52%，命门之一**；= `enterDur`（同停）读作三块板子被推进来，<30% 行到位太早、后半程只在原地变实 |
| `enterStagger` | 0.133s | **行间错峰，本卡的核心量级**；<0.07s 三行几乎同时（顺序读不出），>0.25s 三行割裂成三次独立入场（"一叠"消失，且整段拖到 2s 以上） |
| `distance` | ≈字号 78%（60px ⇒ 47px） | 横向位移量，**比例常量**；<字号 40% 读作原地淡入，>字号 150% 行从画幅外飞进来、抢掉内容 |
| `exitDur` | 0.60s | 出场时长 = 入场的 67%（出场一律比入场快，这是通则）；>0.9s 整叠磨磨蹭蹭不肯走 |
| `exitDelay` | 0.267s | **淡出起 → 位移起的延迟，本卡最精致的一条**；0（位移与淡出同起）读作"被一把扫掉"，观众觉得没读完；>0.4s 位移只剩一瞬、读作硬切 |
| `exitStagger` | 0.067s | 出场错峰 = 入场的**一半**；= `enterStagger` 出场也在讲一遍顺序（啰嗦），0 则整叠齐走（能用，但少了一点收束的层次） |
| `hold` | 1.4s | 整叠读完的停留；按总字数给（每字约 0.12s），3 行 × 8 字 ≈ 1.4s；<0.8s 观众读不完第三行 |
| `lineHeight` | 1.35（中文） | 源码 1.1 是拉丁值；中文 <1.25 行与行粘住、滑入时相邻行的字会互相压 |
| `lead` | 0.3s | 起手静置等口播开口 |

## 已知坑
- 出场做成入场的倒放（往左退回去）——读作"这段作废了/我说错了"，接不上下一段内容；出场必须朝**同一方向穿出去**（进左出右）。
- 出场的横向位移与淡出同时起——整叠读作"被一把扫掉"，观众会觉得自己还没读完；那 0.27s 的延迟是本卡的签名，别省。
- 出场错峰照抄入场错峰——出场又讲一遍顺序，啰嗦且拖长；出场错峰取入场的一半。
- 用居中对齐——每行左端各自不同，横向滑入的方向感散掉，"一叠"读成"几行分别在动"；必须左对齐。
- 中文照抄源码 `lineHeight: 1.1`——中文字面比拉丁字母高，1.1 会让相邻行粘住，滑入过程中上下行的字互相压。
- 行数放到 5 行以上——第一行的淡出已经开始、最后一行还在入场，"一叠"这个整体读不出来；同时观众读不完。
- 入场位移与淡入同停（`enterTravel = enterDur`）——三行读作三块半透明板子被推进来，与市面清单预设无差别。
- 出场缓动照抄入场的缓出——"甩走"变成"缓缓飘走"，收不干净；出场必须是缓入 `(0.64, 0, 0.78, 0)`（先粘住再加速）。
- `distance` 写成绝对像素值跟着复用——换字号后大字号下滑入幅度不够、小字号下行从画幅外飞进来；必须按字号 78% 等比。
- 每行不锁 `white-space: nowrap`（或容器太窄）——某一行自己折成两行，行数就变了，错峰序列与视觉上的行对不上。
- 出场排在入场结束之前（`hold` 给负或太小）——某行还在淡入就开始淡出，opacity 两段相乘会让那行整体偏暗、像是没入场成功。
- 重播不重建 DOM 只重置 transform——换文案后行数变了，旧的 span 还在，错峰序列与实际行数对不上。

## 复用指引
- props：无；文案在 `CONFIG.lines`（3~4 行），换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/line-by-line-slide.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/line-by-line-slide/index.html。**换内容只改 `CONFIG.lines`** 这个字符串数组（3~4 行），
  入场/出场的时刻表都是从行数算出来的。节奏只调 `enterStagger`（`enterTravel` 要跟着 `enterDur` 保持约 52%）；
  停留时间调 `hold`（按总字数，每字约 0.12s）；换字号改 `.lbl-text` 的 `font-size`，
  同时把 `CONFIG.distance` 改成新字号的 78%。整叠的落位改 `.lbl-block`
  （demo 是 `inset: 0` + flex 整屏居中的**纯文字卡**，不放主持人；
  `.lbl-text` 是 `inline-block` + `text-align: left`——收缩到最长行的宽度，
  于是"整叠视觉居中"与"行与行共享同一条左端"同时成立。
  **`text-align: left` 与 `inline-block` 都不要改**：改成 `center` 每行左端各自不同，滑入方向感就散了）。
  只要入场不要出场：把 `exitDur` 那两条 `tl.to` 删掉即可（`hold` 就成了定格）。
  `cubicBezier()` 那个解算器是通用的，别的 demo 要 `cubic-bezier` 缓动可以直接抄走。
- Remotion 移植：直接用 template/cards/line-by-line-slide.tsx（逐帧查表写法，自带 `cubicBezier()` 解算器）。
  出场时刻 `exitStart = enterEnd + hold`，不由 `durationInFrames` 反推；每行 `opacity` / `x` 按 `t < out` 顺序分段，
  出场位移从 `out + exitDelay` 起、走 `exitDur − exitDelay`（同一条时钟的后段，不是新时钟）。
  **帧↔秒换算（30fps）**：`enterDur 27` ⇒ 0.90s、`enterTravel 14` ⇒ 0.467s、`enterStagger 4` ⇒ 0.133s、
  `exitDur 18` ⇒ 0.60s、`exitDelay 8` ⇒ 0.267s、`exitStagger 2` ⇒ 0.067s。
  缓动 `cubic-bezier(0.22,1,0.36,1)`（入）/ `cubic-bezier(0.64,0,0.78,0)`（出），进度全部 clamp。
  尺寸：960 舞台上三行中文取 60px、`distance` 按字号 78% ⇒ 47、`lineHeight 1.35`（中文；1.1 是拉丁值会粘行）。
- 剪辑软件对应物：剪映/CapCut——**每行一个独立文本层**（不要用一个多行文本层，那样做不出错峰），
  每层入场打两组键：位置（左 `distance` → 0，0.47s）+ 不透明度（0 → 100，0.90s），
  层与层的起点各差 4 帧；出场每层打不透明度（100 → 0，0.60s）+ 位置（0 → 右 `distance`，**从出场后第 8 帧才开始**，0.33s），
  层与层各差 2 帧。剪映的"向右滑出"预设做不出那 8 帧延迟，位置必须手打。
  AE——三个文本层（或一个层配三个 `Text Animator` 按 `Range Selector` 分行），
  入场/出场各两组 Position + Opacity 关键帧，曲线在 Graph Editor 里拉成对应 bezier；
  出场位移的第一个关键帧**打在淡出开始后 8 帧**（这是全卡最容易漏的一步）；
  别用 `CC Slide` 或转场类效果（它们裁切边缘，本卡的行是整体位移不裁切）。
- 与本库同类卡的分工：`keyword-pop-highlight` = 砸一个重音；
  `per-character-rise` / `soft-blur-in` = 都是**单句**入场（竖向顶起 / 对焦）；
  `quote-card` = 整屏让位的多行金句大字卡（**带底板、人物压暗、整卡退场**，是一个"卡"）；
  **本卡 = 不带底板的多行要点**（字直接落在现有画面上，人物照常出镜，讲完穿出去）。
  与 `quote-card` 的分界很清楚：要不要让位。金句要仪式感 ⇒ `quote-card`；
  要点是"边讲边挂在旁边" ⇒ 本卡。两张不在同一段里混用。

## 动效范围
- 属于本卡的：入场"位移 0.47s / 淡入 0.90s（位移占 52%）+ 行间错峰 0.133s"这组时序；出场"进从左、出向右"这个**穿过式**方向（不是倒放）；出场横向位移比淡出**迟 0.267s** 才起这条延迟（本卡签名）；出场错峰恒为入场的**一半**；入场缓出 `(0.22,1,0.36,1)` 与出场缓入 `(0.64,0,0.78,0)` 这一对方向相反的曲线；横向位移量恒为**字号的 78%**；`opacity` 两段相乘 / 位移两段相加这个叠加写法；出场永不早于入场结束这条下界；**左对齐**（共享左端才成"一叠"）与"行数 3~4"这个上限。
- 不属于本卡的：demo 那三行「第一，把问题写下来 / 第二，只留一个变量 / 第三，跑最小实验」的具体文案与"第 N，"这种编号写法、60px 字号与 600 字重、`#171717` 这个墨色、`letter-spacing: -0.03em`、`lineHeight 1.35`（这是中文可读性的下限值，不是动效参数）、无衬线字族的选择、白底舞台、以及"整叠居中落在舞台正中"这个落位（画幅左侧、右侧、下半区都成立，**只要保持行与行左对齐**）。**demo 是纯文字卡、不放主持人**（2026-08-25 用户定版）——整屏交给这一叠要点，人物占位会把注意力从"一行一行滑进来"上分走；但应用侧要让人物照常出镜同样成立（整叠挂在人物旁的留白列），落位不属于本卡的动效本体——**左对齐才是**。
- 迁移接口：`CONFIG.lines` 是唯一的内容入口（3~4 行）；节奏调 `enterStagger`（`enterTravel` 跟着 `enterDur` 保持约 52%）；`hold` 按总字数给（每字约 0.12s）；`distance` 按字号 78% 等比缩放；**`exitDelay` / `exitStagger` 与两条缓动是手感常量，换尺寸换语速都不要动**；只要入场不要出场就删掉出场那两条 tween（`hold` 变定格）；竖屏用 3 行并把字号收到 32~38px（每行 `nowrap` 后不超出可用宽度的 90%，中文一行别超 12 字）。
- 底色要求：白底或深底都成立（深底把字色反白即可）。唯一约束是**底不能有纵向条纹或纵向渐变**——行在底上横向滑动，带纵向纹理的底会与横向位移产生视差错觉。实拍花底上可用，但要给字加描边或半透明底板保证可读（本卡不自带背板——需要背板的场合用 `quote-card`）。

<!-- ===== /file: video-talkcraft/references/cards/line-by-line-slide.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/line-carry-transition.md ===== -->

---
name: line-carry-transition
标题: 线条接力转场
一句话: A 镜标题下先画出一条强调色下划线，停一拍后它继续向右冲出画面，镜头跟着线横移 960px（2s power2.inOut；横移段线的生长量 = 镜头位移量，笔头钉在画面 x≈640 永不出画也永不落后），线到位后拐直角向上、向右、向下、向左围出一个 560×330 的画框，框闭合那一帧笔头消失、B 镜内容在框内淡入——全程无剪切，一条线把两镜缝在一起
适用: 章节 A → 章节 B 的接缝（A 的标题下划线变成 B 的画框）；进度条 → 图表坐标轴、一条数据线 → 下一镜卡片边框等有图形亲缘的两镜之间；全片唯一的"招牌转场位"（Saul Bass / Catch Me If You Can 片头语法）。作用于前后两镜，B 内容可为图片 / 截图
时长: 6.4s（0.1 A 标题入场 → 0.4 下划线 0.6s → 1.2 镜头横移 2.0s，线同速冲出并围框 → 3.2 框闭合笔头卸载 → 3.3 B 内容淡入 0.5s → 真静止 ≥36 帧 → 6.0 同收 0.4s）；成片 A 侧信息必须在 1.2 横移前讲完
能量: 中
类别: 转场结构
输入: 场, 图, 文
语义: 转场, 章节
素材形态: 横屏
位置: 中段
props: titleA, subA, titleB, subB, srcB
优先级: P1
代码: template/cards/line-carry-transition.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 人物不进这一镜（人在 A 或 B 里各自的镜头里出现，转场帧不留人） | ✗（tsx）`srcB` 仅走 `<Img>`；要放 B-roll 见复用指引 | ✓（默认输入）B 内容是截图 / 照片；A 侧只有标题 + 副标 |

作用于前后两镜（**场**）：A 侧吃标题文字，B 侧吃一张图 + 标题。

## 常用场景
1. 章节 A → 章节 B：A 的标题下划线变成 B 的画框（demo 演的）
2. 进度条 → 图表坐标轴：A 的进度条冲出画外，拐角成为 B 折线图的 x/y 轴
3. 一条数据线 → 下一镜的卡片边框（图形亲缘：线是同一根）
4. 全片唯一的招牌转场位——片头 hook 结束进入正文第一章

## 意图
库里的转场分两族：**运动承接六式**是相机在交接动量（推穿 / 翻页 / 甩镜 / 黑场砸 / 拉远冷却 / 粒子焊接），**几何擦除**（`shape-wipe` / `caret-wipe`）是一条边界扫过完成交接。线条接力是第三族——**画面里的一个图形元素自己跑到下一镜去当容器**：A 的下划线是 B 的画框，观众的眼睛一路跟着笔头，"换章"这个动作被一条线讲完，没有任何一帧是"切"。它的价值在于**图形亲缘**：两镜之间本来就有一条线的语义（下划线 → 边框、进度条 → 坐标轴），转场只是把这条线的身份交接出去。做对四条：
1. **横移段线生长 = 镜头位移**：`drawn = underline + cam`，笔头钉在画面 x≈640（约 67%）——居中读作"线追镜头"，贴边一颤就出画；一旦失速，观众跟丢线就等于跟丢转场。
2. **直角硬拐不倒圆**：圆角软拐丢掉制图感，Saul Bass 味就没了。
3. **框没闭合，B 内容不能先出**：线的悬念到闭合那一帧才兑现；内容先出等于把答案提前说了。
4. **闭合后笔头墨点必须卸载**：残留即毁静止；B 内容淡入完成后 ≥36 帧真静止。

与运动承接六式的关系：六式管"镜头边界怎么交接动量"（一个边界只用一式），本卡管"两镜之间的一条线怎么接力"；**一支片只用一次**（招牌位，重复即廉价），且 A 侧信息要在横移前讲完（横移会把 A 的标题带出画）。

## 动效核心
- **几何**（世界画布 1920×540，镜头 = 世界 translateX）：A 标题 48px/700 @ (80, 150)，副标 20px/500 灰、上距 12；下划线 y=262（副标底边 +18），从 x=80 到 640（560 长）；冲出段 640 → 1160（520 长）；B 画框 (1160, 110)–(1720, 440)，560×330——镜头到位（cam 960）后屏幕 x 200~760，包围盒中心 x=480（layout §4）；B 内容 @ 框内 (1174, 142) 532 宽：图 532×222 圆角 6 + 标题 22px/700 + 副标 16px 灰，上下各留 32。线 6px 强调色实线、`stroke-linejoin: miter`（直角）、笔头 r=8 同色墨点。
- **折线路径**（一条 path，`stroke-dasharray = 总长 2860`，`dashoffset = 总长 − 已画长`）：(80,262) → (640,262) → (1160,262) → (1160,110) → (1720,110) → (1720,440) → (1160,440) → (1160,262)——从画框左边中点进入，顺时针回到入口闭合。分段长 560 / 520 / 152 / 560 / 330 / 560 / 178。
- **A 段**：0.1s 标题入场（0.4s `power3.out`，y 10→0）；0.35s 笔头出现；0.4s 下划线 0→560（0.6s `power2.out`）。
- **横移段**：1.2→3.2s 镜头 cam 0→960（`power2.inOut`）。已画长 `L = max(underline 进度, camL(cam))`：`cam ≤ 520` 时 `camL = 560 + cam`（线与镜头同速，笔头屏幕 x 恒 640）；`cam > 520` 时余下 440px 位移里把画框周长 1780 画完（`camL = 1080 + (cam − 520) / 440 × 1780`，笔头在屏幕内沿框跑）。
- **闭合**：3.2s 笔头 opacity→0（0.2s）；3.3s B 内容淡入（0.5s `power2.out`）；3.8→6.0s 真静止。
- **退场**：6.0s B 内容与线 opacity→0 0.4s `power2.in`，6.4s 结束。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 线体 | 6px 强调色实线 | 太细横移中读丢；虚线读作未完成态 |
| `cam / camDur` 横移 | 960px / 2.0s（16px/f） | 更远的横移等比拉长时长，**别提速**——>40px/f 笔头开始拖影跟丢 |
| 笔头屏幕位置 | x≈640（约 67%） | 居中读作"线追镜头"；贴边一颤就出画 |
| 拐角 | 直角硬拐（miter），不倒圆 | 圆角软拐丢掉制图感 |
| `run` 冲出段 | 520（= 画框左边 − 下划线终点） | 决定 B 画框在世界里的位置；镜头到位后框必须整组居中（屏幕 200~760） |
| 画框 | 560×330 | 与 layout §4 双元素组比例无关，是 B 内容的容器；比例按 B 素材定，周长变了 `camL` 自动跟 |
| `bIn` B 内容淡入 | 闭合后 +0.1s，0.5s | 框没闭合内容先出 = 悬念白搭 |
| 闭合后静止 | ≥36 帧（demo 3.8→6.0 = 2.2s） | 笔头墨点必须条件卸载，残留即毁静止 |
| 下划线 | 560 / 0.6s `power2.out` | 要先停一拍（1.0→1.2）再横移，观众才知道"这条线要去哪" |

## 已知坑
- 线与镜头不同速——笔头在屏幕上漂移，观众跟丢线 = 跟丢转场。
- 笔头居中或贴边——居中读作线追镜头，贴边一颤就出画。
- 拐角倒圆——制图感没了，像 UI 进度条。
- 框没闭合 B 内容先出——线的悬念白搭。
- 笔头闭合后不卸载——一颗蓝点毁掉整段静止。
- 横移前 A 侧信息没讲完——A 标题会被镜头带出画，口播还在讲 A 就成了配音 PPT。
- 一支片用两次——招牌位重复即廉价；第二处章节交接用运动承接六式。
- B 画框在镜头到位后偏一边——`run` 与画框 x 要一起算：框左 = 640 + run，框中心 = 960 + 480。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/line-carry-transition.tsx——`titleA / subA / titleB / subB / srcB`；durationInFrames 204；横移起点改 `CONFIG.camAt`（对到口播换章的那一拍），句长改 `exitAt / end`；画框尺寸改 `CONFIG.frame`（周长与 `camL` 自动跟）。折线全是直线段，沿线取点是解析计算（不依赖 DOM）。tsx 的 `srcB` 仅走 `<Img>`；要放视频把 `<Img>` 换成 `<OffthreadVideo muted>`（Remotion 自带），其余不动。
- HTML/GSAP：demos/line-carry-transition/index.html——`CONFIG` 同名；`.tb .ph` 换 `<img>` / `<video>` 即真素材；demo 用 SVG `getPointAtLength`。
- 母本：video-shotcraft `line-carry-transition`（3840 宽世界、进度条 560 + 冲出段 + 直角 + 560×330 矩形框，横移段 drawn = 1100 + cam，笔头钉在 x≈1500/1920）；移植按 960 舞台等比缩放，语义从"进度条 → 卡框"改成"章节标题下划线 → 章节画框"。
- 剪辑软件对应物：剪映做不了（无路径描画 + 跟踪）；AE 用 Trim Paths 驱动 path 生长 + 摄像机 / 父级 null 的 Position 与 Trim End 用同一表达式变量（`cam = ease(time,…)`；`trimEnd = (560 + cam) / total`）；Motion 用 Write On + 摄像机联动。
- 与 layout.md 的接口：A 标题左边缘 80（标题边 80@960）；B 画框到位后包围盒 (200,110)–(760,440) 中心 x=480、底边 440 < 字幕带 450（§1 / §4）；框内内容左右内缩 14、上下各 32，标题 22 / 副标 16（caption 档以上）。

## 动效范围
- 属于本卡的：下划线 → 冲出 → 镜头同速跟随 → 直角围框 → 闭合卸笔头 → B 内容后出的整条因果链；`drawn = underline + cam` 的同速纪律；笔头钉屏 67%；直角 miter；闭合后 ≥36 帧静止。
- 不属于本卡的：A / B 的具体文案与字号、B 素材、画框尺寸、白底舞台、B 格示意图（演示语境素材，demos/_lib/media，不属于本卡）。
- 迁移接口：`titleA / subA / titleB / subB / srcB`；`CONFIG.frame` 按 B 素材比例改；1080p 输出线 6→12px、笔头 r 8→16、横移 960→1920（时长不变 2.0s = 32px/f，仍 <40）。
- 底色要求：白底即可；深底舞台时线换 `#2997ff`、B 内容卡加 hairline 描边。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- 定妆帧三张：横移中段（≈2.2s）笔头屏幕 x 在 640±8、线尾在画左边缘外；闭合帧（3.2s）笔头已消失、框四边闭合、B 内容 opacity 0；闭合后（≥3.8s）框包围盒中心 x=480 偏差 ≤48、底边 ≤440。
- 横移期间无任何一帧笔头出画（x ∈ [0, 960]）。
- A 侧口播在 `camAt` 前讲完（SHOTBOOK 里 A 的最后一个字时间戳 ≤ camAt）。
- 全片本卡 ≤1 次。
- 线宽 ≥6@960、拐角 miter；B 内容文字 ≥16@960（caption 档）。

<!-- ===== /file: video-talkcraft/references/cards/line-carry-transition.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/line-chart-story-draw.md ===== -->

---
name: line-chart-story-draw
标题: 折线分段推演
一句话: 历史段一开始就在场，讲到假设时新线段从拐点向右 0.4~0.8s stroke 生长、段完成瞬间 ▲5% 标签+弧线箭头弹出，对比虚线再从同一拐点岔出第二种未来，最后竖向色带逐个罩住相关区间
适用: 口播做"如果当时…那么现在…"的假设推演、给同一起点算两种未来、讲某段区间的相关性；财经拆解、政策复盘、投资算账类冷静推理的调性
时长: 历史线静置 0.6s → 拐点亮起 + "这里买入"标注 0.25s + 停 0.35s → 每段生长 0.6s（段间停 0.35s）+ 段末标签 0.25s → 停 0.4s 后对比虚线 0.7s + ×2 标签 → 色带错峰 0.3s 逐个淡入；全程约 4.8s
能量: 中
类别: 数据信息图
输入: 文, 人(可选)
语义: 数据, 对比
素材形态: 无
位置: 中段
props: hostSrc
优先级: P0
代码: template/cards/line-chart-story-draw.tsx
---

## 意图
口播做假设推演时，一次性画完的折线等于剧透——观众看见终点就不再听推理过程。分段生长把
"一条线"拆成"一句话一段"：历史段先在场立住事实基准，讲到假设才让线从拐点往右长，
对比虚线从同一拐点岔出，两种未来的分歧被眼睛直接量出来。命门：
**历史段不生长**（它是既成事实，跟着一起长就变成"数据也是我编的"）、
**逐段严格由语音触发**（段间必须留停顿，连着长完就退化成一次性描线动画）、
**对比线必须共用同一个拐点**（换起点画第二条线，"同一起点两种未来"的论证当场失效）。

## 动效核心
- 历史段：灰阶折线（demo #a8a8ad、2.6px）第一帧就在场，全程不动；`bandTop/bandBottom` 之间一条"今天"竖虚线把历史/推演分开
- 拐点：白芯圆点 scale 0→1（0.22s `back.out(2.4)`）+ 一圈同色描边涟漪 scale 0.5→3.2、opacity 0.9→0（0.5s `power2.out`）——"就是这里"的落点
- 拐点标注：文字标签 scale 0.7→1 + y 6→0 弹出（0.25s `back.out(2)`），弧线箭头同帧 scale 0.55→1 从箭尖 origin 张开，指向拐点；标注落定后再停 0.35s 才开始生长
- 分段生长：每段一条独立 SVG path，`stroke-dasharray = 整段长`、`stroke-dashoffset` 从整长→0，单段 0.4~0.8s `power2.out`（起笔快收笔缓 = 手在画），**段之间留 0.3~0.4s 停顿等语音**
- 段末标签：该段 dashoffset 归零那一帧，`▲5%` 标签 + 弧线箭头一起弹出（0.25s `back.out(2)`），箭头指回段末点
- 端点数值标签：一个 chip 贴着线端（+12, −30 px 偏移）跟随移动，数字由 `getPointAtLength().y` 反算实时刷新（`tabular-nums` 防跳字）
- 对比虚线：从同一拐点、以更大斜率的第二条 path，虚线笔画不能直接动 dashoffset → 套一层 16px 实心 stroke 的 `<mask>`，动 mask 的 dashoffset 揭开（0.7s `power2.out`），端点落一个深色空心点 + `涨幅×2` 标签
- 区间罩显：竖向半透明色带（demo `rgba(216,56,58,.07)`）+ 底部灰色区间名，两条错峰 0.3s 各 0.3s `power2.out` 淡入，画在折线**下方**图层

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `hold0` | 0.6s | 历史线静置几拍等语音念到"假设"；0 则观众还没看清事实就开始推演 |
| `segments[].dur` | 0.6s | 单段生长时长；<0.4s 读作闪现（没有"正在推演"），>0.8s 观众等得着急 |
| `segGap` | 0.35s | 段间停顿——**本卡的命门参数**；<0.15s 几段连成一条一次性描线，分段叙事归零 |
| `annotPop` | 0.25s | 标签+箭头弹出时长；>0.4s 拖沓，<0.15s 没有"叮"的落定感 |
| `annotHold` | 0.35s | 标注落定到开始生长的停顿；0 则标注和线抢同一帧，观众不知道先看哪 |
| `altGap` | 0.4s | 实线讲完 → 虚线岔出的停顿；两条线不留缝就变成"同时两条"，不是"另一种可能" |
| `alt.dur` | 0.7s | 对比线略慢于主线，读作"再算一遍"；比主线快会抢走结论 |
| `bandStagger` | 0.3s | 色带错峰；同时淡入 = 一块大色底，"逐个罩住哪几段"的语义消失 |
| `chipDx/chipDy` | 12 / −30 | 端点数值 chip 相对线端的偏移；贴太近压线，离太远读不出"这是线端的值" |
| `scale` | yBase/vBase/yStep/vStep | y 像素→数值的线性映射，换数据只改这四个数（满量程必须固定） |

## 已知坑
- 历史段跟着一起生长——事实和假设一样是"现场画出来"的，数据可信度当场归零。
- 几段连着长完（`segGap` 太小或干脆一条 path 一次描完）——这就退化成 chart-grow 的折线变体，本卡的"分段叙事"完全没做出来。
- 对比虚线换了起点——"同一起点、两种未来"的论证前提破了，观众读作两组无关数据。
- 虚线直接动 `stroke-dashoffset` 生长——dasharray 已被虚线占用，效果是虚线在原地流动（像跑马灯），必须用 mask 揭示。
- 端点数值 chip 用非等宽数字——数字位数变化时 chip 宽度抖，读作画面在颤（`font-variant-numeric: tabular-nums` 解决）。
- 区间色带画在折线上层或饱和度太高——线被罩糊，罩显反而遮掉了要看的证据。
- 标签先于线段出现——结论比推演先到，逐段推理的悬念全废。

## 复用指引
- props：仅 `hostSrc`（主播 PiP 小窗）；数据点位 / 标签 / 色带 / 节奏全在 CONFIG，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/line-chart-story-draw.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/line-chart-story-draw/index.html。换数据只改 `CONFIG`：`history` 换历史点位、`pivot` 换拐点、`segments[].pts/dur/label` 换推演段与段末标签、`alt` 换对比线与端点标签、`annot` 换拐点标注（`arc` 三点定弧线箭头）、`bands` 换罩显区间、`scale` 定 y→数值映射；节奏全在 `hold0/segGap/annotHold/altGap/bandStagger`。核心动画即 `DemoShell.register` 回调整段（`growSeg` / `popLabel` 两个小函数），复制 CONFIG + 回调可直接摘走。
- Remotion 移植：每段一个 `<Sequence from={段起始帧}>`，`strokeDashoffset={interpolate(frame, [0, dur*fps], [L, 0], {easing: Easing.out(Easing.quad), extrapolateRight:'clamp'})}`（`L` 用 `useLayoutEffect` 里 `getTotalLength()` 量或预先算好写死）；段末标签用 `spring({frame: frame - (段起 + dur*fps), config:{damping:10}})` 驱动 scale；端点 chip 位置用同一 `interpolate` 的进度调 `getPointAtLength`（把点位预采样成数组避免每帧测量）；对比虚线保留 mask 结构，动 mask path 的 dashoffset；色带用 opacity interpolate + `i*bandStagger*fps` 延迟。**帧驱动下段间停顿要写成显式空帧**，别指望时间线自然拉开。
- 剪辑软件对应物：AE——形状图层折线 + "修剪路径"(Trim Paths) End 关键帧，每段一个图层错开入点（虚线段用 Trim Paths 配合"描边"效果的虚线开关，或同样做遮罩层揭示）；剪映——折线只能用"线条生长"贴纸拼段，分段叙事需要把每段做成独立素材依次入场；CapCut 搜 line chart / graph animation 模板，但内置的多是一次性描完，分段得自己切。

## 动效范围
- 属于本卡的（与 chart-grow 划界：那张卡是柱状图从零一次性亮相、回答"这几个数各是多少"，本卡是**折线的分段叙事**——图已在场、事实段不动，只有"假设"被逐段推出来，回答"如果这样、接下来会怎样"）：历史段第一帧即在场、全程不生长这条约束；拐点圆点 scale 0→1 pop（0.22s、back.out(2.4)）+ 同色涟漪 scale 0.5→3.2 淡出（0.5s、power2.out）；每段折线 `stroke-dashoffset` 从整长→0 从拐点向右生长（0.4~0.8s、power2.out）、**段与段之间留 0.3~0.4s 停顿由语音逐段触发**的分段时序；段完成同帧标签 scale 0.7→1 + y 6→0 与弧线箭头 scale 0.55→1 一起弹出（0.25s、back.out(2)）；端点数值 chip 贴线端跟随移动、数值随线端高度实时刷新；对比虚线从**同一拐点**以不同斜率生长（mask 揭示，0.7s，略慢于主线）+ 端点点亮与标签；竖向区间色带逐个错峰淡入（0.3s、错峰 0.3s、图层在折线之下）。
- 不属于本卡的：坐标轴/网格/刻度与"今天"分界虚线的样式、具体数据与年份文案、标签的边框圆角字号、字幕行、主播小窗与数字人占位、灰阶+红这一套具体色值。相邻卡的分工也不在本卡内：只在静态画面上指一处用 callout-line-label（点→线→字三拍是独立动作，本卡的拐点标注只服务于线的生长节奏）；要单独强调一个终值叠 number-counter（本卡端点 chip 的数值是线端位置的副产品，跟着线走才变，不是独立计数动画）。
- 迁移接口：数据全在 `CONFIG` 的 `history/pivot/segments/alt` 点位表 + `scale` 的 y→数值映射（满量程必须固定，中途缩放对比即失真）；配色只需三个 token——历史灰 `histColor` + 主推演语义色 `hotColor` + 对比线色 `altColor`（色带用 `hotColor` 的 7% 透明版）；节奏按语速整体乘同一系数缩放 `segments[].dur / segGap / altGap / alt.dur`；线宽、`chipDx/chipDy`、涟漪半径随输出分辨率等比缩放。
- 底色要求：白底即可。深底把历史灰改为浅灰阶、标签底色反相、色带换成 `rgba(白, .06)` 即可，时序与生长逻辑完全不变。

<!-- ===== /file: video-talkcraft/references/cards/line-chart-story-draw.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/logo-enter.md ===== -->

---
name: logo-enter
标题: Logo 登场
优先级: P1
代码: template/cards/logo-enter.tsx
一句话: 品牌圆牌用 spring 从 0.5 倍弹到位（唯一带过冲的一拍），错峰 0.233s 后字标从圆牌一侧推出、副行再错峰一拍，同时一圈描线绕着圆牌合拢——三拍收尾，落定即终帧
适用: 片头的身份交代（"我是…"）与片尾的品牌收束；系列视频每期固定的开场/落幕；产品名/机构名的正式立牌。一片各用一次（开头一次、结尾一次）
时长: 起手静置 0.35s → 圆牌弹入 0.60s → 字标推出 0.45s（错峰 0.233s / 0.466s）→ 描环合拢 0.70s → 收尾定格 1.30s；全程约 2.6s
能量: 中
类别: 素材呈现
输入: 文, 图
语义: 自我介绍, 结尾
素材形态: 矢量
位置: 任意
props: hostSrc(未使用)
---

## 意图
收尾是全片最容易做俗的一拍：logo 旋转飞入、光晕扫过、粒子炸开——观众看过一万次，
且它们都在抢戏（片尾的职责是"落幕"，不是"再来一个高潮"）。

remocn 的 `logo-enter` 给出的做法很克制：一个 spring 同时驱动三件事
（`opacity 0→1` / `scale 0.5→1` / `y 22px→0`），damping 13 / stiffness 130 / mass 0.8，
约 0.60s 落定、过冲仅 4%。没有旋转、没有发光、没有第二个方向的运动。
本卡把它的骨架（spring 手感 + 0.233s 拍距）搬过来，把源码的"一串同级圆牌错峰弹入"
换成口播片的标准收尾编排：**圆牌 → 字标 → 描环合拢**三拍。

命门三条：
① **只有第一拍有过冲**——圆牌是唯一带弹性的元素（`back.out(1.1)` ≈ spring 的 4% 过冲）。
字标和描环都是纯缓出。给字也加弹跳，两个弹性元素互相抢，收尾就变成了开场；
② **拍距 0.233s（源码 stagger 7 帧）**——三拍不能同时发生（读作一张贴图淡入），
也不能拉到 0.5s 以上（读作三件无关的事依次发生）。0.2~0.25s 是"一件事的三个部分"的距离；
③ **落定即终帧，不加 idle 微动**——收尾画面就该停住。这里是全库少数明确**不要**呼吸/漂移的地方
（hold 期微动是防止画面死掉，但片尾的"死"正是它要的效果）。

白底适配的一处改动：源码圆牌是 `border: 5px solid #fff` + `boxShadow 0 20px 48px rgba(0,0,0,0.5)`
（深底上靠亮度分层）。白底上白环会消失、那层重投影会糊成一团脏斑，
改成浅灰环 `#ececef` + 轻投影 `0 10px 26px rgba(0,0,0,0.10)`。

## 动效核心
- **第①拍 · 圆牌弹入**（`lead = 0.35s` 起）：三件事同一条曲线——
  `opacity 0→1`、`scale 0.5→1`、`y 22px→0`，0.60s，`back.out(1.1)`。
  三个属性共用一条曲线是源码的写法（同一个 spring 值驱动三者），
  分开给不同缓动会让"弹到位"散成三件事
  - **spring → GSAP 换算**：源码 `spring({damping:13, stiffness:130, mass:0.8})` @30fps
    ≈ 18 帧（0.60s）落定、峰值过冲约 +4%。GSAP core 无 spring，`back.out(1.1)` 的过冲量与之对齐。
    `back.out(1.7)`（本库 `media-pop-in` 用的值）过冲 ~10%，在收尾场景读作综艺感
- **第②拍 · 字标推出**（`lead + 0.233s`）：品牌名 `opacity 0→1` + `x −20px→0`，0.45s，`power3.out`；
  副行再错峰一拍（`lead + 0.466s`）同样参数。
  横向位移方向是"从圆牌一侧推出"（圆牌在左则字向右推），读作字是被圆牌带出来的
  - 两档字重（品牌名 800 / 副行 500）+ 副行大字距——这是版式，不是动效，但错峰的**顺序**是动效：
    重的先来、轻的后到
- **第③拍 · 描环合拢**（`lead + 0.233s`，与字标同时起）：一圈 2px 细线沿圆牌外缘
  `stroke-dashoffset` 从全长走到 0，0.70s，`power2.inOut`（起笔快、合拢那一下停住；
  匀速读作 loading 圈）。起笔在 12 点（`rotate(-90deg)`）
  - **`dasharray` 取周长 + 3px**：恰等于周长时首尾在起笔点留一道亚像素白缝，1080p 下一眼可见
  - 描环与字标**同时起、更慢收**（0.70s vs 0.45s）——它是把三拍"收口"的那条线，
    最后落定的应该是它
- **层级**：白底 → 圆牌（底色 + 灰环 + 轻投影）→ logo 图形（占圆牌 52%，源码比例）→ 描环（绝对定位盖在圆牌上）→ 字标（同级，flex 右侧）
- **不做的事**：不旋转、不发光、不加粒子、不给 logo 单独的入场（logo 跟着圆牌一起弹，
  它不是独立的主体）、落定后不呼吸

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `lead` | 0.35s | 起手静置，等口播说到"我是…"；0 则像自动播放的片头，>1s 观众以为卡了 |
| `badgeDur` | 0.60s | 圆牌弹入（= spring 落定时长）；<0.35s 读作弹窗，>0.9s 弹性感被拉散成缓慢放大 |
| `badgeFrom` | 0.5 | 起始缩放（源码值）；0.8 以上行程太短看不出弹，<0.3 读作从远处飞来（那是开场不是收尾） |
| `badgeRise` | 22px | 起始下沉（源码值）；0 = 纯缩放（少一层"落定"），>50px 读作从画外飞入 |
| `badgeEase` | `back.out(1.1)` | 过冲 ~4%，对齐源码 spring(13/130/0.8)；`back.out(1.7)` 过冲 10% 读作综艺感，`power3.out` 无过冲则收尾"软" |
| `stagger` | 0.233s | 拍距（源码 7 帧）；0 = 三拍同时发生（读作一张贴图淡入），>0.5s 读作三件无关的事 |
| `wordDur` | 0.45s | 字标推出；比圆牌快是对的（跟随者不该比主体慢） |
| `wordShift` | 20px | 字标横向推出距离；0 = 纯淡入（丢掉"被带出来"的关系），>50px 读作字从画外滑进来、与圆牌无关 |
| `ringDur` | 0.70s | 描环合拢；必须**比字标慢**（它是收口的那条线，最后落定）；<0.4s 读作 loading 转圈 |
| `hold` | 1.30s | 收尾定格；片尾可拉到 2~3s（配片尾音乐尾巴），**期间不加任何微动** |

## 已知坑
- 给字标也加 `back.out` 弹跳——两个弹性元素互相抢，收尾变成开场；过冲只给圆牌一个。
- 三拍同时发生（`stagger` 给 0）——读作一张做好的 logo 图片淡入，编排白做。
- 描环用匀速（`ease:none`）——读作 loading 进度圈，观众以为在等加载；合拢那一下必须减速停住。
- 描环比字标先落定——收口的线先没了，最后落定的是字，三拍的收束感散掉。
- `dasharray` 恰等于周长——首尾在起笔点留一道亚像素白缝，1080p 下一眼可见（本 demo 踩过）；给周长 + 3px。
- 白底上照搬源码的白环 + `rgba(0,0,0,0.5)` 重投影——环消失、投影糊成脏斑；改浅灰环 + 轻投影。
- 给 logo 单独加入场（logo 自己再缩放/描线一次）——它不是独立主体，跟着圆牌一起弹；单独动会读作两个 logo。
- 落定后加呼吸/漂移微动——片尾的"停住"是它的效果，加了就成了"还没结束"。这是全库少数不要 idle 的地方。
- 加旋转/发光/粒子——三样都是收尾最俗的做法，且都在抢戏（片尾的职责是落幕）。
- logo 图形填满圆牌——源码的 52% 是留白比例，填满后圆牌读作一个按钮而不是徽标底座。
- 一片里用 3 次以上——它是身份标识，开头一次、结尾一次足够；中间反复出现读作水印。

## 复用指引
- props：仅 `hostSrc`（未使用）；品牌名 / 副行文案 / logo SVG 写死在 JSX 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/logo-enter.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/logo-enter/index.html。**替换成自己的 logo**：把 `.badge` 里那段
  `<svg viewBox="0 0 100 100">…</svg>` 整段换掉（demo 里是灰阶几何占位标：三角 + 挖圆）。
  换品牌文案改 `.brand` / `.tag` 两行；节奏全在顶部 `CONFIG`。
  三拍各自独立——不要描环就删第③拍（`ring` 那一段），不要副行就删 `tag` 那一 tween。
- Remotion 移植：直接用 template/cards/logo-enter.tsx（tsx 以 `tw`/`backOut(1.1)` helper 等价 spring）。要还原原生 spring 手感——
  `spring({fps, frame: frame*speed − i*stagger, config:{damping:13, stiffness:130, mass:0.8}})`
  一个值驱动 `opacity: s` / `scale: interpolate(s,[0,1],[0.5,1])` / `offset: interpolate(s,[0,1],[22,0])`。
  秒↔帧（30fps）：静置 0.35s = 10.5 帧、圆牌 0.60s = 18 帧（spring 自然落定，不用给 duration）、
  拍距 0.233s = 7 帧、字标 0.45s = 13.5 帧、描环 0.70s = 21 帧。
  白底取值 tsx 已落实：环色 `#ececef`、投影 `rgba(0,0,0,0.10)`（深底改回 `#fff` / `rgba(0,0,0,0.5)`）；
  单牌 + 字标，不做多牌重叠。
  描环在 Remotion 侧用 `strokeDasharray={len} strokeDashoffset={interpolate(frame,[a,b],[len,0])}`。
- 剪辑软件对应物：剪映/CapCut——logo 素材用"弹入"入场动画（缩放 + 位移，把回弹调到最弱一档），
  字标另起一层用"向右滑入"，描环用圆形贴纸的"描边生长"或直接用一段圆环 MG 素材；
  AE——logo 层 Scale/Position/Opacity 三条键都挂同一个 `Overshoot` 表达式
  （或 RubberHose/Motion 插件的 spring），描环用 Shape Layer + `Trim Paths` 的 End 关键帧，
  拍距按 7 帧摆。**别用** CC Light Sweep / Shine 那类扫光（本库 design-defaults 禁 glow）。
- 与本类其余卡的分工：`media-pop-in` / `motion-blur-slam-in` 是**证据素材**的入场（要歪、要叠、要密，
  强调"啪啪啪甩上来"）；本卡是**身份标识**的入场（要正、要单、要停住，强调"这是谁"）。
  两者的过冲量差一倍不是巧合——甩证据要 10%，立品牌只要 4%。

## 动效范围
- 属于本卡的：一个 spring 值同时驱动 `opacity/scale/y` 三属性这条写法（及其 `back.out(1.1)` ≈ 4% 过冲的换算）；`0.5 → 1` 缩放 + `22px → 0` 下沉的行程量；0.233s 拍距的三拍编排（圆牌 → 字标 → 描环）与"重的先来轻的后到"的顺序；**过冲只给第一拍**这条纪律；字标从圆牌一侧横推 20px 表达"被带出来"的关系；描环 `dashoffset` 全长→0、`power2.inOut`、且比字标更慢收（最后落定的是它）；`dasharray` = 周长 + 3px 的接缝处理；logo 占圆牌 52% 的留白比例；**落定即终帧、不加 idle 微动**这条取舍；白底上环色与投影的改法。
- 不属于本卡的：demo 的灰阶几何占位标（**应用时替换成自己的 logo**）、示例品牌名「知远研究所」与副行文案、圆牌尺寸 118px 与字号 46/17px、圆牌底色 `#f5f5f7` 与环色 `#ececef` 的具体取值、logo 在左字标在右这个左右关系（镜像也成立）、`gap: 26px` 的间距。
- 迁移接口：logo 换 `.badge` 内的 SVG（或换成 `<img>`，保持 52% 占比）；圆牌尺寸改 `.badge` 的 `width/height`（描环 `.ring` 要同步 +10px 并重算 `viewBox`）；`badgeRise` / `wordShift` 是**手感常量，换画幅不要等比放大**（它们是"落定"的量级，不是相机的量级）；`stagger` / `badgeEase` / 三拍顺序不要改（那是本卡的全部）；片尾想拉长只改 `hold`。竖屏把 lockup 改成上下排（`flex-direction: column`），字标的推出方向同步改成纵向。
- 底色要求：白底/浅底即可（圆牌靠浅灰环 + 轻投影分层，描环与字标是深色）。深底改回源码做法——环色换白、投影加重到 `rgba(0,0,0,0.5)`、描环与字标换浅色；三拍的时序参数全部不变。

<!-- ===== /file: video-talkcraft/references/cards/logo-enter.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/long-take-world.md ===== -->

---
name: long-take-world
标题: 长镜头世界画布
一句话: 全部内容钉在一张大画布的不同位置，一台相机随讲述连续运镜过去，新内容在镜头快到时才成形——没有切镜，空间本身就是叙事结构
适用: 有空间/流程/地图隐喻的话题（管线、时间线、生态图景）；想要"一镜到底"的高级感段落
时长: demo 三站共 6.7s（起点 hold 1.1s → 运镜 1.5s → 站 B hold 1.2s → 运镜 1.5s → 站 C hold 1.4s）；生产中一段 20s~全片，站间运镜 1~2.5s、到站讲述 5~15s
能量: 中
类别: 转场结构
输入: 文
语义: 转场, 步骤, 空间叙事
素材形态: 无
位置: 任意
props: 无
优先级: P1
代码: template/cards/long-take-world.tsx
---

## 意图
多镜头是"剪辑思维"，长镜头是"空间思维"：观众始终知道自己在哪、从哪来、往哪去，
信息之间的关系被空间布局直接表达（下一步在右边、原因在下面、回顾就是往回走）。
做对的命门：① 相机永不瞬移（速度上限内的连续曲线）；② 内容在相机**快到时**开始成形，不是到站后才播动画；③ 到站后相机仍有微漂，让位规则照常执行。

## 动效核心
卡 tsx：`CONFIG.stops: {x, y, zoom, hold}[]` 站点表 + `travel`（站间 1.5s，sine.inOut 逐段插值 x/y/zoom），
相机 = 世界层的反向 transform `scale(zoom) translate(-x,-y)`，叠双不可通约正弦微漂（`drift` ±5px，y 取 0.7 倍）。
站点内容钉在世界坐标（`STATIONS` 绝对定位）；接近度揭示内联计算：相机到站点距离 < `arriveLead`（420px）
起 opacity / 位移 26px / scale 0.94→1 随距离成形，实现"镜头一转过去东西正在长出来"。
生产母本 `template/motion-systems/longtake.tsx` 在此之上提供 `WorldRig`（站点表带 t 字级锚点 + `impulses` 重音脉冲）、
`WorldPlane depth` 视差、`WorldItem` 与 `useArrive(x, y, radius)` 钩子（讲完的区域可挂 `1-arrive` 做离场退焦）。

## 参数表
| 参数 | 典型值 | 调节手感 |
|---|---|---|
| 运镜速度 | ≤1.5 屏宽/秒 | 更快就该改用 whip 转场；<0.3 屏/秒观众以为没动 |
| `travel` | 1.5s | 站间运镜时长，配合站距守 ≤1.5 屏宽/s（demo 两段 0.83 / 0.67 屏/s） |
| 站点 zoom | 0.9~1.15 | 移动中微拉远再推近（呼吸）；全程等 zoom 像平移扫描 |
| `arriveLead` | 420px（约 0.44 屏；longtake.tsx 的 `useArrive` 默认 radius 900） | 接近半径，距离小于它内容开始成形；大=提前很久开始成形（从容）；小=擦到跟前才出（紧张） |
| `drift` 微漂 | ±5px | 到站防静止的底线，关掉必挂 motion_check |
| 世界布局 | 站点间距 1~2 屏（demo 1.25 / 1.0 屏） | 太近互相穿帮（上一站还在画面里），太远运镜时间全是空旷 |

## 已知坑
- 站点布成一条水平直线=传送带 PPT；布局要用二维（右→下→斜上），路径带折返和 zoom 变化。
- 相邻站点内容在运镜途中同框穿帮：布局时按 zoom 算可视范围，途中露出的半成品要么提前成形要么退焦。
- 长镜头不豁免七层：世界画布只是把 L1 从"每镜一条曲线"换成"一条大曲线"，idle/让位/环境照旧。
- 与多镜头混用时时间基要分清：WorldRig 的 t 与场景内动画锚点用同一时间源（绝对秒，经 time.ts 换算）。
- （实战·longtake.tsx）世界网格自己铺盖满全站点的超大 div；GridField 等 AbsoluteFill 屏幕件放进 WorldPlane 的 0×0 容器会塌为零。
- （实战·longtake.tsx）WorldItem 锚点=盒中心只对普通内容成立；绝对定位子元素铺开的站点，视觉中心会漂离锚点（实测 460px），内容要自证以 (0,0) 为视觉中心。
- （实战）运镜途中 ≥0.5s 的全空舞台=评审必挑；给途中路线放前景视差符号垫场（到站构图外、只在途中入画，按视锥验算位置）。

## 复用指引
- props：无；站点文案 / 坐标在 `STATIONS` 与 `CONFIG.stops` 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/long-take-world.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- 生产母本：template/motion-systems/longtake.tsx
- Remotion：`longtake.tsx`，站点表写在 shots.ts 旁做表驱动；组合范式见文件头注释。
- SHOTBOOK 写法：先画世界布局草图（各站点世界坐标 + 相机路线箭头），层矩阵按"站"分节。
- 状态：已实战验证（2026-08-19，作者内部工程 V3 幕：23.1s 三站，运镜 1.08 屏/s，无途中穿帮，三重验收全过；该工程为过程资产不随库分发）。可复制实现即上面的 `longtake.tsx`。
- 剪辑软件对应物：AE 大合成 + camera 关键帧（Prezi/Motion 的 spatial narrative）。

## 动效范围
- 属于本卡的：一台相机在世界坐标上连续运镜（站点表稀疏关键帧 + `sine.inOut` 插值，速度 ≤1.5 屏宽/s，永不瞬移）；相机 = 世界层的反向 transform（`scale(zoom) translate(-x,-y)`）这一机制；**接近度揭示** `useArrive`——内容在相机赶到前约 0.4 屏就开始成形（opacity/位移/scale 挂距离衰减，不是到站后才播动画）；到站后双不可通约正弦微漂 ±5px（任何"到站"时刻都不完全静止）；站点的二维布局（右→下→斜上，带折返与 zoom 变化）。
- 不属于本卡的：站点卡片的边框圆角与字号、示例文案、途经点圆点的样式、字幕、站点的具体坐标数值。世界网格是个边界情况——它不是装饰纹理而是**让相机位移可被看见**的参照物（没有它，白底上的连续运镜看起来像静止），所以保留，但线色可任意换。
- 迁移接口：站点表 `CONFIG.stops`（`x`/`y`/`zoom`/`hold`）+ `travel` 站间时长 + `arriveLead` 接近半径 + `drift` 微漂幅度；换尺寸时站点坐标与 `arriveLead` 按舞台宽同比缩放（间距保持 1.2~2 屏）；网格 `background-size` 与线色改 `#worldgrid`。**强调色接口**：demo 把原先的 #0066cc 收敛为墨色，途经点 `.waypoint` 的描边是唯一预留的一处强调位，复用时整组换品牌色即可（站点标题的 `em` 同理）。
- 底色要求：白底即可。唯一实质要求是底上得有**可辨认的空间参照**（网格/地图/纹理任选），否则相机在纯色空场里运镜观众读不出"在移动"——这是空间连续性的载体，不是风格装饰。

<!-- ===== /file: video-talkcraft/references/cards/long-take-world.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/lower-third-nameplate.md ===== -->

---
name: lower-third-nameplate
标题: 人名条展示牌
一句话: 画面左下色条先横向展开 0.3s，姓名随后从左遮罩揭示，头衔行再延迟 0.15s 跟进；停留后按反向顺序收回
适用: 真人出镜/访谈嘉宾首次开口的 3~5 秒；也用于自我介绍、连线、引用他人观点时标注身份；新闻、评测、访谈调性
时长: 入场三段接力重叠后共约 0.6s（色条 0.3s → 姓名在色条 70% 处起 0.25s → 头衔再延迟 0.15s）；hold 3~5s（demo 压到 2s）；出场反向收回 outDur 0.3s（文字段 ×0.7）、三段各错 0.08s 共约 0.45s
能量: 低
类别: 人物互动
输入: 人(可选), 文
语义: 自我介绍, 引用, 介绍他人
素材形态: 无
位置: 任意
props: hostSrc
优先级: P0
代码: template/cards/lower-third-nameplate.tsx
---

## 意图
观众需要在人物开口的头两秒内知道"这是谁、凭什么听他说"——人名条是成本最低的信任背书。
命门：**三段接力**（色条 → 姓名 → 头衔，任意两段同时出层次就塌）、
**出场反向收回**（文字先收、色条后收；直接淡出像素材播完了，收回去才是"完整的一次亮相"）、
**对比度**（色条要饱和、字要加投影，压在任何实拍背景上都读得出）。

常见于：影视飓风、MKBHD、ColdFusion、新闻/访谈类节目；Videohive lower thirds 品类 2.6 万商品。

## 动效核心
- 结构：姓名（大字 42px/960 舞台）→ 横向色条（高 7px 饱和色）→ 头衔（小字 19px 灰白），左下角安全区内（左 56px、下 64px）
- 入场：色条 scaleX 0→1（origin left）0.3s `power4.out` → 姓名 `clip-path: inset(0 100% 0 0)`→`inset(0 0 0 0)` 从左揭示 0.25s（在色条走完 70% 时起步，接力不等待）→ 头衔同法延迟 0.15s
- hold：2~5s，完全静止即可（元素小，不需要防呆滞漂移）
- 出场反向：头衔先收 → 姓名 +0.08s → 色条最后 scaleX→0（`power4.in`）；总 0.5s 内
- 层级：实拍画面 → 人名条（最上），千万别被字幕压住

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 色条时长 | 0.3s | 快了（0.15s）像故障闪现；慢了后面两段等不起 |
| 姓名揭示时长 | 0.25s | clip 揭示要干脆；>0.4s 像窗帘拉开 |
| 头衔延迟 | 0.15s | 层次感的最小单元；0 = 层次塌，>0.3s 像卡了 |
| hold 时长 | 3~5s（demo 2s） | 按"观众读完姓名+头衔两遍"计；超 8s 变成台标 |
| 出场时长 outDur | 0.3s | 色条收回时长，文字段取 0.7 倍；头衔 → 姓名 → 色条各错 0.08s 反向收回 |
| 接力起步点 | 色条走完 70% 处 | 等色条 100% 才出字会有可感知的空拍；50% 之前出字像抢跑 |
| 色条颜色 | 品牌色/高饱和红 | 低饱和融进实拍背景；色条是视线锚点必须跳出来 |

## 已知坑
- 姓名和头衔同时出——信息一次全到，层次塌掉，观众反而两个都没读进去。
- 出场直接整体淡出——像素材放完了自然消失；反向收回（后出的先收）才是"动效有始有终"。
- 色条用 width 动画而不是 scaleX——width 回流卡顿且文字跟着换行；transform 才顺滑。
- 文字没有 clip 揭示直接淡入——和色条的"横向语言"不统一，模板感立现。
- 压在画面正下方字幕区——和字幕打架；人名条的家在左下但要高于字幕安全区。
- 头衔写两行以上——读不完；一行 12 字内，多余身份删掉。

## 复用指引
- props：仅 `hostSrc`；姓名 / 头衔文案写死在 JSX，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/lower-third-nameplate.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/lower-third-nameplate/index.html。改 `.name/.title` 文案、`.bar` 换品牌色；节奏都在 `CONFIG`（barDur/nameDur/titleLag/hold/outDur）。
- Remotion 移植：三段用 `<Sequence from={...}>` 串接；clip 揭示 `clipPath: inset(0 ${interpolate(frame,[0,8],[100,0])}% 0 0)`；出场用总时长减帧数做反向 interpolate。
- 剪辑软件对应物：剪映"文字模板→字幕条/人名条"分类；AE 是 Videohive "lower thirds" 品类（2.6 万商品直接套）；FCPX 内置 Lower Thirds 生成器；CapCut "Name tag" 贴纸。

## 动效范围
- 属于本卡的：色条 `scaleX 0→1`（origin left，0.3s，`power4.out`）→ 姓名 `clip-path inset(0 100%→0)` 从左揭示（0.25s，在色条走完 70% 时起步，接力不等待）→ 头衔同法再延迟 0.15s 的三段接力；出场**反向收回**（头衔先收 → 姓名 +0.08s → 色条最后 `scaleX→0`，`power4.in`，总 0.5s 内）；文字与色条统一的"横向语言"（都从左侧展开，不用淡入）。hold 期完全静止即可（元素小，不需要防呆滞漂移）。
- 不属于本卡的：色条颜色、姓名/头衔文案与字号、实拍画面（demo 用灰阶主持人占位）、左下 56/64px 的具体安全区数值（按画幅重算）。原 demo 上的文字投影也不属于本卡——那是为压在实拍背景上加的可读性补丁，白底上不需要。
- 迁移接口：**色条颜色 = 复用者的品牌色接口**——改 `.lt .bar` 的 `background`（demo 收敛为墨色 #1d1d1f；实拍场景建议换高饱和品牌色，低饱和会融进背景，色条是视线锚点必须跳出来）；节奏在 `CONFIG`（`barDur`/`nameDur`/`titleLag`/`hold`/`outDur`）；换尺寸时字号与色条高度（7px @960 舞台）同比缩放；压在实拍上时给文字补投影或垫半透明底，这属于迁移时自加的可读性层。
- 底色要求：白底即可。实拍落地时底色是任意视频画面，因此**对比度要自证**——色条与文字必须在目标背景上读得出（这是迁移方的责任，不是本卡的动效内容）。

<!-- ===== /file: video-talkcraft/references/cards/lower-third-nameplate.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/magnifier-detail.md ===== -->

---
name: magnifier-detail
标题: 局部放大镜
优先级: P1
代码: template/cards/magnifier-detail.tsx
一句话: 截图目标处 0.3s 弹出一个圆形放大镜（1.8 倍，深灰 2px 细描边、不加投影）落到旁边空白区，本体同步压暗留一圈细描边框，连接线随后描回出处
适用: 评测/教程口播说到截图里某个具体数字、按钮、条款时——"注意看这里"；信息密度高的证据截图必备，理性讲解调性
时长: 截图先静置 0.45s → 弹出 0.3s（压暗同帧）→ 连接线 0.25s 接力；hold 期间镜内 1.4s 半周期轻扫视
能量: 中
类别: 强调标注
输入: 图, 截图
语义: 强调
素材形态: 无
位置: 任意
props: hostSrc(未使用)
---

## 意图
截图信息密度高，口播念到某个数字时观众在画面里找不到——放大镜一次解决两个问题：
**在哪**（原位细描边框 + 连接线指回出处）和**是什么**（1.5~2 倍看清内容）。
命门：**对得上位**（放大内容必须和原图逐像素对应，错位一眼假）、
**弹到空白区**（镜子盖住目标本体等于自己遮自己）、**本体压暗**（不压暗则镜内镜外抢视线，放大失去意义）。

常见于：笔吧评测室等评测类、差评君、剪映标准教程。

## 动效核心
- 结构：底层假截图；放大镜 = 圆形容器（`overflow:hidden`，2px 深灰描边 `#1d1d1f`，不加投影）内放同一截图的克隆副本，
  副本 `scale = zoom`，偏移量 `x = magSize/2 − zoom·px`、`y = magSize/2 − zoom·py`（px/py 为目标点在截图内坐标），使目标点正好落在镜心
- 入场：放大镜从目标点原位起跳，scale 0.3→1 + 位移到旁边空白区落位，0.3s `power3.out`；
  同帧底图 `brightness` 1→`dimTo`（0.3s，白底截图取 0.8、深底取 0.6），目标处指示色细描边框 0.2s 淡入
- 连接线：入场将完时（popIn − 0.05s）SVG line 用 `stroke-dasharray` 从目标点向镜心描出 0.25s `power2.out`——先有镜再有线，线是"指回出处"，顺序反了就没有因果感
- hold：镜内副本 x 方向 ±(panPx×zoom) 正弦 yoyo 平移（1.4s 半周期），模拟视线扫视，画面不呆
- 起手留白：截图先静置 0.45s 再弹镜，观众先知道"这是张什么图"再看局部
- 副本也可用 CSS background 双图技巧实现（`background-size` 放大 + `background-position` 对准目标点），对位公式同上

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `zoom` | 1.8 | 1.5~2 之间；>2 内容发糊像马赛克，<1.4 放大感不足不如加粗 |
| `magSize` | 210px | 放大镜直径；太小看不清，太大盖版面（勿超舞台高 1/3） |
| `magX` / `magY` | 745 / 252 | 落位中心，必须是截图旁空白区；离目标越远连接线越重要 |
| `popIn` | 0.3s | >0.45s 拖节奏像 PPT 飞入；<0.2s 看不出"从原位弹出"的轨迹 |
| `dimTo` | 0.8（白底截图）/ 0.6（深底截图） | 底图压暗亮度，随底图明度取值：白底截图压到 0.6 会变成一整块灰，取 0.75~0.85 刚好"退让不失读"；1.0 完全不压=强调失效 |
| `startDelay` | 0.45s | 截图先看清一拍；0 会让观众没看懂整图就被拽进局部 |
| `panPx` | 7px | hold 期间扫视幅度；>15 像镜头在漂，0 则 hold 期读作静止贴图 |

## 已知坑
- 放大内容和原图对不上位——副本偏移没按 `magSize/2 − zoom·目标坐标` 校准（或截图被外壳缩放后用了屏幕坐标），观众一对照就穿帮。
- 放大镜落在目标本体上——自己遮住出处，读者不知道放大的是哪。
- 没有连接线/描边框——镜子孤零零浮着，读者在原图里找不到出处，等于白放大。
- 底图不压暗——镜内镜外两份同样亮的内容抢视线，"看这里"的指向性归零。
- hold 期间完全静止——放大镜读作贴上去的静态圆图，不像"正在看"。

## 复用指引
- props：仅 `hostSrc`（未使用）；截图内容写死在 JSX（`ShotContent`），目标坐标 `TARGET` 与落位 `magX/magY` 在常量 / CONFIG 里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/magnifier-detail.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/magnifier-detail/index.html。换截图内容改 `.shot .body` 里各行文案；换放大目标只需把 `id="magTarget"` 挂到任意元素上（目标坐标运行时自动反推，副本对位与连接线端点跟着变）；换落位/倍数/压暗程度改 `CONFIG` 的 `magX/magY`、`zoom`、`dimTo`；换强调色改 `.target-box` 边框色与 `#lline` 的 `stroke`（#ff4d4d），放大镜描边色在 `#magnifier` 的 `border`；口播字幕在 `.caption-zone` 内。核心可摘走：复制 `CONFIG` + `DemoShell.register` 回调体即可。
- Remotion 移植：同一截图渲染两个 `<Img>`，上层包在 `borderRadius:'50%'; overflow:'hidden'` 的圆形容器里，内层 `transform: scale(zoom) translate(...)` 按同一公式对位；入场用 `spring({frame, config:{damping:200}})` 驱动 scale 0.3→1，位置用 `interpolate(frame, [t0,t1], [targetX, magX])`；压暗 `filter: brightness(interpolate(...))`；连接线 SVG `<line>` 用 `strokeDasharray = \`${interpolate(frame,...,[0,len])} ${len}\``；hold 扫视 `Math.sin(frame/fps * 2π/2.8) * panPx * zoom`。
- 剪辑软件对应物：剪映——画中画复制同素材 + "蒙版→圆形" + 缩放放大，或素材库搜"放大镜"贴纸；AE——复制图层加椭圆蒙版 + Scale 关键帧，或直接用内置 Magnify（放大）效果 + 描边圆形固态层；CapCut——"Magnifier" 贴纸 / PIP + circle mask 同法。

## 动效范围
- 属于本卡的：放大镜从目标点**原位起跳**——`scale 0.3→1` + 位移到旁边空白区落位（0.3s、power3.out）；同帧底图 `brightness 1→dimTo` 压暗（0.3s）与目标处细描边框 0.2s 淡入；连接线在入场将完时（popIn − 0.05s）从目标点向镜心用 `stroke-dasharray` 描出（0.25s、power2.out）——**先有镜再有线**的因果顺序；hold 期间镜内副本 x 方向 ±(panPx×zoom) 正弦 yoyo 扫视（1.4s 半周期），画面不呆；起手截图静置 0.45s。对位公式（`x = magSize/2 − zoom·px`）是本卡的技术本体，必须一起带走。
- 不属于本卡的：假评测截图占位（窗口条、行文案、数据）、示例口播字幕、放大镜落位坐标 `magX/magY`（随版面变）、指示色 #ff4d4d 与镜圈色的具体取值、镜子的投影质感（已移除，属于风格）。
- 迁移接口：`zoom` 定放大倍数（1.5~2），`magSize` 定镜径（勿超舞台高 1/3），`magX/magY` 定落位（必须是目标旁的空白区），`popIn` 定弹出快慢，`dimTo` **随底图明度取值**（白底 0.8 / 深底 0.6），`panPx` 定 hold 扫视幅度；换目标只需把 `id="magTarget"` 挂到任意元素上，坐标运行时反推、副本对位与连接线端点自动跟随；换尺寸时 magSize 与镜圈线宽按画幅等比缩放。
- 底色要求：白底即可（镜圈用深灰细描边即可从白底分离，不依赖投影）。唯一与底色联动的是 `dimTo`——白底截图压暗过深会变成一整块灰，见参数表取值。

## 落位自检（2026-09-05 用户定版，选卡时抄进 SHOTBOOK 该镜自检列）
- 标注几何（框 / 圈 / 线 / 箭头 / 放大镜锚点）一律由**目标的实测包围盒**反推——DOM `getBoundingClientRect` / `measureText`，四边留白 16~24px 等距，**不目测**。
- 实现后抽该镜定妆帧核对：标注是否恰好套住 / 指向目标，偏差 **> 8px 返工**（`references/layout.md` §3）。
- 目标会滚动 / 移动时，标注钉在内容坐标系随内容动（SKILL.md ③）。

<!-- ===== /file: video-talkcraft/references/cards/magnifier-detail.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/map-route-pin.md ===== -->

---
name: map-route-pin
标题: 地图路线图钉
一句话: 地图上虚线从 A 城生长到 B 城，到达瞬间图钉从上方砸下带一次压扁回弹，地名标签侧滑而出
适用: 口播讲到地理转移/行程/事件链时（"从北京到上海，再到深圳"）；纪实解说、商业分析、事件复盘调性
时长: 单段路线生长 0.8~1.5s + 落钉 0.25s + 回弹 0.28s + 标签 0.2s；两段三城全程约 4.8s
能量: 中
类别: 数据信息图
输入: 文, 人(可选)
语义: 时间地点, 步骤, 空间叙事
素材形态: 无
位置: 任意
props: hostSrc
优先级: P1
代码: template/cards/map-route-pin.tsx
---

## 意图
口播讲空间叙事（迁移、行程、供应链、事件链）时，光靠嘴说观众记不住地理关系——
路线按叙事顺序逐段"长"出来，把时间顺序翻译成空间顺序，观众跟着线头走。
命门：**弧线 + 缓动**（匀速直线立刻读作 PPT 连接线）、**钉要砸下来**（加速下落 +
落地压扁回弹才有"到达"的重量，淡入的钉是贴纸）、**一次只长一条线**（叙事顺序就是
路线生长顺序，齐长全丢）。

常见于：Johnny Harris、Wendover、LEMMiNO、Half as Interesting。

## 动效核心
- 底图：内联 SVG 抽象地图——陆地一层极浅填充（demo #f5f5f7）+ 灰阶描边海岸线/岛屿 + 极淡经纬网，不要真实地图数据；关键是陆海可区分，路线才读得出走向
- 起点钉先亮：t≈0.15s 起点图钉先落且用区分色（demo 深色 `#1d1d1f`，后续钉红 `#d8383a`），先回答"从哪儿出发"
- 路线生长：贝塞尔虚线（Q 控制点向外弓），mask 里放同形实线路径，`strokeDashoffset: L→0`
  1.1s `power1.inOut` 揭开虚线；mask 路径用 butt 线帽（offset=L 时 round 帽会在起点漏出一个点）
- 线头跟随物：小机头图形（demo 用灰阶 SVG，不用彩色 emoji）以 `getPointAtLength(progress*L)` 贴线头走，取前方 2px 的点算切线角旋转对齐航向
- 图钉落下：y -60px→0，0.25s `power2.in` 加速砸下；落地一帧 squash（scaleY 0.7 + scaleX 1.3，0.06s）
  再 `back.out(3)` 回弹 0.28s；`transform-origin: 50% 100%`（钉尖为轴，不然压扁会离地）
- 落地反馈：地面尘圈 scale 0.2→1.6 淡出 0.45s；地名标签 x -14→0 + 淡入 0.2s 从钉侧滑出
- 第三地延迟接入：上一钉落定后停 0.4s（`legPause`）再长第二段

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| routeGrow | 1.1s | 调大 >1.5s 观众在等地图、拖节奏；调小 <0.8s 看不清走向，读作瞬移 |
| routeEase | power1.inOut | 换成 none（匀速）立刻变 PPT 连接线；缓动太重（power3）线头像卡顿 |
| pinDropFrom | 60px | 调大砸感更重，>100px 读作"天外飞钉"；调小落差不足，像原地冒出来 |
| pinDrop | 0.25s | 调大变慢动作、重量感消失；调小 <0.15s 看不到下落只剩闪现 |
| squashX / squashY | 1.3 / 0.7 | 调大更卡通、偏整活调性；归 1.0 落地轻飘飘，"钉住"感减半 |
| rebound | 0.28s | 压扁后 back.out(3) 回弹时长，与 pinDrop 一起决定"砸"的重量 |
| labelSlide | 0.2s | 调大标签像迟到的补充说明；调小与落钉同帧，抢走砸落的视觉重音 |
| legPause | 0.4s | 调大停顿明显，适合分句讲解一地一句；调小两段连成一笔，"再到"的层次消失 |
| planeAngle | 0°（demo 机头朝右） | 跟随物图形朝向补正；机头没贴切线就调它，差 90° 是侧着飞的飞机，一眼假 |

## 已知坑
- 路线画成匀速直线——没有弧度没有缓动，读作 PPT 连接线而不是旅程。
- 图钉淡入或匀速降落、无 squash——轻飘飘没有到达感，像贴了张贴纸。
- 多条路线同时长出——先后关系全丢，观众不知道该看哪条线。
- 用真实地图截图当底——细节噪声抢戏还有版权风险；抽象海岸线反而更有"解说感"。
- 起点没有先亮的标记——观众不知道从哪儿出发，路线长到一半才反应过来方向。

## 复用指引
- props：仅 `hostSrc`；城市坐标 `CITY` / 路线 `ROUTE_D` / 地名 `LABELS` 写死在常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/map-route-pin.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/map-route-pin/index.html。换城市：改三个 `.pin-anchor` 的 left/top 和标签文案，
  同步改两条 `route`/`reveal` mask 的 path `d`（起终点对准城市坐标、Q 控制点向外弓）；
  节奏与砸感全在顶部 `CONFIG`；起点钉颜色在 `.pin-anchor.start .pin-head`。
- Remotion 移植：路线用 `@remotion/paths` 的 `evolvePath(progress, d)` 拿 strokeDasharray/offset，
  progress 用 `interpolate(frame, [0, dur], [0, 1], {easing})`；图钉 y 用
  `spring({frame, config:{damping:10, stiffness:180}})`，squash 把同一 spring 的过冲映射到
  scaleX/scaleY 反向；飞机取点同款 `path.getPointAtLength(progress * L)`。
- 剪辑软件对应物：AE 是"修剪路径（Trim Paths）"+ 图钉 Scale 关键帧加 Overshoot 表达式；
  剪映"贴纸→地图/图钉" + 手动 K 位置关键帧；CapCut 模板市场搜 "travel map" 可整体替代。

## 动效范围
- 属于本卡的：起点钉先落（t≈0.15s，用区分色回答"从哪出发"）；路线沿贝塞尔弧逐段生长——mask 内实线路径 strokeDashoffset L→0（1.1s、power1.inOut，mask 必须 butt 线帽）逐步揭开虚线；线头跟随物用 `getPointAtLength` 贴线头走并取前方 2px 算切线角旋转；图钉 y −60px→0 加速砸下（0.25s、power2.in）→ 一帧 squash（scaleX 1.3 / scaleY 0.7、0.06s、origin 50% 100% 钉尖为轴）→ back.out(3) 回弹 0.28s；地面尘圈 scale 0.2→1.6 淡出 0.45s；地名标签 x −14→0 + 淡入 0.2s 从钉侧滑出；第二段路线延迟 0.4s 接入的叙事停顿。
- 不属于本卡的：地图底的形状/海岸线/经纬网密度（抽象线框只是占位，换成任何底图都成立）、图钉与标签的造型和配色、城市名与字幕文案、主播小窗、线头跟随物的具体图形（灰阶机头可换成任意小图标）。
- 迁移接口：换城市改三个 `.pin-anchor` 的 left/top + 标签文案，同步改 `route-*` 与 `reveal-*` mask 的 path `d`（起终点对准坐标、Q 控制点向外弓）；`routeGrow` / `legPause` 按解说语速缩放；`pinDropFrom` / `pinDrop` / `squashX,squashY` / `rebound` 调砸落重量；`planeAngle` 按跟随物图形朝向补正（本 demo 机头朝右故为 0）；配色两个 token——途经点/路线语义色 + 起点区分色，字幕高亮色跟路线色走。
- 底色要求：**允许最小例外**——陆地用极浅灰 #f5f5f7、海域留白（#ffffff），因为"路线跨陆/跨海"是本卡地理语义的载体，纯白无区分时路线读不出走向。除这一层浅灰外全部灰阶描边（#d2d2d7 海岸线、#ececef 经纬网），无渐变无质感。换成真实底图或深色地图时，只需保证图钉色/路线色与底图的对比度，动效时序不变。

<!-- ===== /file: video-talkcraft/references/cards/map-route-pin.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/media-pop-in.md ===== -->

---
name: media-pop-in
标题: 素材弹入堆叠
一句话: 截图/照片带白边投影从 80% 弹到 100% 带回弹，随机歪 5~10°，多张以 100~150ms 错峰依次"拍"上来压角堆叠
适用: 口播甩证据的时刻（截图、聊天记录、转账单、报道）；"一张一张给你看"的列举语感；爆料、辟谣、盘点调性
时长: 起手 0.45s；单张 0.3s（0.25~0.35）；三张错峰 150ms（100~150），全组 0.6s 内拍完；落位后整组 ±0.8% 呼吸 idle（1.6s 半程）
能量: 中
类别: 素材呈现
输入: 图, 截图, 人(可选)
语义: 例证, 列举
素材形态: 多图
位置: 任意
props: hostSrc
优先级: P0
代码: template/cards/media-pop-in.tsx
---

## 意图
证据素材需要入场仪式感——"啪啪啪"拍上桌的密度让观众相信"证据确凿"，规规矩矩的轮播只是配图。
命门：**要歪要叠**（随机 ±5~10° 旋转 + 后来者压前者一角，工整排版=PPT）、
**回弹收尾**（back.out 过冲到 1.02 再落回 1，直线放大没有"拍"的手感）、
**错峰要密**（100~150ms 一张，拉开到 0.5s 以上就丢了"甩"的气势）。

常见于：Fireship、Ali Abdaal、Johnny Harris、差评君、剪映入场动画。

## 动效核心
- 每张素材：白描边 6~10px + 投影（白底上 `0 12px 26px rgba(0,0,0,.16)` 即可分层，深底用更重的一层）+ 圆角 4px
- 入场：scale 0.8→1（`back.out(1.7)` 自带过冲到 ~1.02）0.25~0.35s；opacity 0→1 在前半程完成；rotation 从"目标角度再歪 6°"收到目标角度（旋转跟着收正，比固定角度更有落位感）
- transform-origin 设 50% 60%（略低于中心，像被手按下去）
- 多张 stagger 100~150ms，位置手工错开、后来者层级更高压住前者一角
- 全部落位后整组极轻呼吸（scale ±0.8%，2~3s 周期，可选）防止画面死掉

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 单张时长 | 0.3s | >0.4s 拖节奏像幻灯片；<0.2s 密到看不清是什么素材 |
| 回弹力度 back.out | 1.7 | 调大到 3 是综艺感"哐哐"砸；1.2 以下几乎无过冲，变普通淡入放大 |
| 起始缩放 | 0.8 | 更小（0.5）冲击感强但像从远处飞来；0.9 以上行程太短看不出弹 |
| 旋转错落 | ±5~10° | 全部同角度=模板感；超过 15° 素材内容读不清 |
| 张间错峰 | 150ms | 密度感的命：>300ms 变逐张展示，<80ms 观众数不清张数 |
| 白边宽度 | 8px | 白边是"实体照片"的暗示；没有白边就只是浮着的截图 |

## 已知坑
- 不旋转不堆叠——排得整整齐齐就是 PPT SmartArt，"甩证据"的现场感全无。
- 每张都弹到正中央再轮播——密度感消失，观众也记不住前一张；要同屏堆叠共存。
- 入场超过 0.4s——口播语速下一句话能说 3 个词，素材还没落地。
- 素材之间零重叠——各占一块像九宫格；压角 10%~20% 才像随手拍上去的一沓。
- 投影太小或没有——素材贴死在背景上，"拍上来"的空间层次消失。

## 复用指引
- props：仅 `hostSrc`；三张素材是写死在 JSX 的 CSS 假截图（无 images[]），换真素材需改源码替换为 `<Img>`。
- Remotion/tsx（skill 首选）：template/cards/media-pop-in.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/media-pop-in/index.html。三张假截图是纯 CSS（`.shot-browser/.shot-chat/.shot-pay`），整块换成 `<img>` 即可用真素材；每张的落位角度在 `data-rot`，节奏在 `CONFIG.stagger/popDur`。
- Remotion 移植：每张一个 `spring({frame: frame - i*4, config: {damping: 12, stiffness: 200}})` 驱动 scale，opacity 用同 spring 的前半段 clamp；旋转 interpolate 从 rot-6 到 rot。
- （实测变体）分屏压上：不在人物旁边堆素材，而是人物缩入下方圆角卡、B-roll 落入上半区，两件事错峰 3~5 帧完成——整版一次换装，比逐张拍上来更干净，适合只有一条素材要看的时刻。人物缩位这一半已独立成卡（见 references/cards/host-shrink-to-chip.md）。见 TheAIScaler（Apm_oCzPEQs）。
- （实测变体）模糊甩入：把 scale 弹跳通道换成"位移 + 方向运动模糊 + 0.2s 急停"，气质更凌厉，已独立成卡（见 references/cards/motion-blur-slam-in.md）；同一段素材两者二选一，不叠用。
- 剪辑软件对应物：剪映"入场动画→弹入/甩入"逐张错帧摆放；AE 是 scale + rotation 关键帧套 Overshoot 表达式；CapCut "Bounce In"。

## 动效范围
- 属于本卡的：单张素材 scale 0.8→1 带 back.out(1.7) 过冲落位（0.25~0.35s）、opacity 在前半程完成；rotation 从"落位角度再多歪 6°"收正到落位角度（旋转跟着收正才有"拍"的手感）；transform-origin 50% 60%（略低于中心，像被手按下去）；多张 stagger 100~150ms 的密度感与"后来者压前者一角"的层级堆叠；白边 + 投影这层"实体素材"语义（离开背景一层才叫"拍上来"）；全部落位后整组 ±0.8% 极轻呼吸。
- 不属于本卡的：三张假截图的内容与灰条排版、素材的具体位置与落位角度值、字幕文案、主持人占位。
- 迁移接口：换真素材把 `.shot-*` 内部整块替换成 `<img>`，保留 `.shot` 的白边 + 投影与 `data-rot`；`popDur` / `stagger` 按"甩证据"的语速缩放（stagger 别超 300ms 否则丢密度）；`overshoot` 调拍击力度、`fromScale` 调行程、`preTilt` 调收正幅度；白边宽度与投影强度随输出尺寸等比缩放。
- 底色要求：白底即可，但**素材的白边与投影必须保留**——白底上靠这一层投影把素材与舞台分开；若目标是纯白极简风，把投影调弱到 8%~10% 黑即可，不要归零。

<!-- ===== /file: video-talkcraft/references/cards/media-pop-in.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/metric-with-sparkline.md ===== -->

---
name: metric-with-sparkline
标题: 数字带趋势
一句话: 小标签先淡入，大数字 0→67 滚 0.9s，下方小折线在同一刻起跑用 0.6s 画完、四个数据点跟着线端依次弹出；数字停住那一帧「%」和上箭头才出现——结论比过程晚半拍
适用: 口播念一个带方向的指标时（"效率提升了 67%"、"退货率降到 3%"）；财经/评测/复盘类段落里"一个数 + 它怎么来的"这种双层信息；不适合只报一个孤立数字（那用 number-slab-pop）
时长: 静置 0.3s → 标签 0.16s → 0.5s 起计数 0.9s ‖ 折线 0.6s（同刻起跑）→ 1.4s 单位+箭头 0.2s → hold 1.8s；共约 3.4s
能量: 中
类别: 数据信息图
输入: 文, 人(可选)
语义: 数据
素材形态: 无
位置: 任意
props: hostSrc
优先级: P0
代码: template/cards/metric-with-sparkline.tsx
---

## 意图
口播报一个百分比时，观众要的其实是两件事：**这个数是多少**，和**它是怎么走到这里的**。
只给数字（`number-counter` / `number-slab-pop`）观众信了但不知道趋势；只给折线
（`line-chart-story-draw` / `chart-grow`）观众看到趋势但抓不到那个可以复述的数。
这张卡把两者压成**一个动效**：数字和曲线同一刻起跑，观众的眼睛在两者之间来回一次，
就同时拿到了"多少"和"往哪走"。

命门两条：
① **滚动结束前不许出现单位和箭头**。数字还在跳的时候屏上就写着「%↑」，等于结论比计算先到——
观众读作"这个数是摆上来的，滚动只是装饰"。单位与箭头是**结论签名**，必须押在数字定住那一帧。
② **折线与计数同刻起跑，不是先后**。两者错开哪怕 0.2s，读作"先讲数字，再补个图"——
两个动效。同刻起跑才是一件事：`lineDur (0.6s) < countDur (0.9s)`，曲线先到位、
数字最后落定，视线自然从曲线收回到数字上，落点就是那个要被复述的数。

与 `number-counter` 的分工：那张卡的主体是**滚动这件事本身**（odometer 滚轮 + 千分位大数，
"烧了多少钱"的量级感）；这张卡的滚动只是把注意力钉住 0.9s 的手段，主体是
**数字 + 趋势的合成语义**。

## 动效核心
- **层级**（自下而上）：白舞台 → 小标签（灰 `#8a8a8a` / letter-spacing 3px）→
  大数字行（`display: flex; align-items: baseline`，整行 `white-space: nowrap` +
  `font-variant-numeric: tabular-nums`）→ 小折线 SVG（含一条静态灰基线）→ x 轴周次标签。
  主持人占位在右侧 47%，指标块左对齐在 96px 安全边内。
- **① 标签**：`opacity 0→1`，0.16s `power2.out`，`t = 0.30`（起手静置）。
- **② 计数**：`t = 0.50` 起，`{v:0} → {v:67}`，0.9s `power2.out`，
  `onUpdate` 里 `Math.round` 写进 textContent。**`tabular-nums` 是硬要求**——
  比例数字下 67 比 26 窄，整行会在滚动中左右呼吸。
- **④ 折线**：`t = 0.50`（与②同值，这是命门）起，`stroke-dashoffset dashL → 0`，
  0.6s `power1.inOut`。`dashL = Math.ceil(L) + 2`（整数长度：GSAP 会把 dashoffset 取整而
  dasharray 保留小数，两者差出的亚像素会在起笔处漏出一小截笔画）。
- **数据点跟线端**：四个点 `scale 0→1`，0.18s `back.out(2)`，**触发时刻由线长比例反推**：
  第 i 点的累积弧长比例 `r = cum[i]/total`，再过一遍 `power1.inOut` 的**反函数**
  （`r<0.5 ? √(r/2) : 1-√((1-r)/2)`）换成时间比例，`at = 0.50 + 0.6 × invEase(r)`。
  直接按时间均分四份是错的——`inOut` 中段快两端慢，均分下点会在中段落在线端后面、两端跑到线端前面。
- **③ 结论签名**：`landAt = 0.50 + 0.9 = 1.40`。同一刻两件事：
  单位「%」`opacity 0→1` 0.2s `power2.out`；上箭头 `y +12→0` + `scale 0.8→1` +
  `opacity 0→1`，0.2s `power3.out`，`transform-origin: 50% 100%`（从下弹入，箭头的
  重心在尾部）。箭头是 SVG path 不是字符「↑」——字体箭头的度量各系统不同，基线永远对不齐。
- **⑤ hold 1.8s**：整块指标静置（不做任何微动——数据是结论，结论不该抖）。
- **唯一语义色 `#2fb344`（positive）**：只上在数字、单位、箭头、折线、数据点描边上。
  标签走灰、基线走 hairline、x 轴标签走灰。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `countDur` | 0.9s | 本卡的能量旋钮；<0.5s 读作硬切（滚动这层过程感丢掉），>1.4s 口播已经讲下一句了、观众在等一个数 |
| `lineDur` | 0.6s | **必须 < `countDur`**（约 2/3）；= `countDur` 时曲线和数字同时落定，两个落点抢一拍；> `countDur` 则数字先定住、曲线还在爬，结论签名被曲线的动作盖掉 |
| `countAt` | 0.5s | **与折线起点同值，本卡第一命门**；两者差 >0.15s 就读作"先数字后补图" |
| `countEase` | `power2.out` | 计数的"先快后慢"；`none` 读作机器读数（没有"算出来"的手感），`power4.out` 前 1/4 就冲到 90%、后面 0.7s 在磨最后两个数，读作卡住 |
| `lineEase` | `power1.inOut` | 曲线的匀速感；用 `out` 曲线起笔就冲出去、尾段爬不动，读作"线被甩出来"而不是"走出来" |
| `unitIn` / `arrowIn` | 0.2s | 结论签名的落定时长；>0.35s 结论来得太软，抵不住前面 0.9s 的动作 |
| `arrowRise` | 12px | 箭头弹入位移；0 读作单位的一部分（少了"涨"这个方向），>24px 箭头自己成了一个动效抢戏 |
| `dotPop` | 0.18s | 数据点弹出；>0.3s 点比线还显眼，读作"四个点连起来"而不是"一条线上有四个刻度" |
| 数据点数 | 3~5 | 6 个以上点密到看不出"依次"，此时删掉点只留线（趋势不需要刻度） |
| `hold` | 1.8s | 收尾定格；数字 + 曲线两层信息要各读一遍，<1.2s 观众只来得及读数字 |

## 已知坑
- 单位「%」参与滚动（写在 textContent 里跟着变）——数字还在跳单位就在那，结论比计算先到，一眼假。
- 箭头和数字同时入场——"涨"这个判断在数还没算完时就下了，读作数据是编的。
- 折线比计数早起或晚起——两个动效，观众的眼睛要看两次，"一个数 + 它的趋势"这层合成语义直接散掉。
- 不写 `font-variant-numeric: tabular-nums`——比例数字下每帧字宽都不同，整行左右呼吸，慢放一眼看出。
- 大数字行不写 `white-space: nowrap`——单位淡入那一帧行宽变了，箭头被挤到下一行，起手排版就是错的。
- 数据点按时间均分触发——`power1.inOut` 中段快两端慢，点会脱离线端（中段落后、两端超前），
  读作"点和线是两个动画"。必须用缓动反函数从弧长比例换算时间。
- `dasharray` / `dashoffset` 用小数长度——GSAP 取整后两者差出亚像素，起笔处漏出一小截笔画。
- 用字符「↑」当箭头——字体的箭头字形基线和度量各系统不同，和数字对不齐，且字重跟不上 600。
- hold 期给数字加呼吸/漂移——数据是结论，结论抖起来读作"还没定"（design-language §4 的手作感通道不适用于数字）。
- 语义色上到标签和 x 轴标签上——`design-language.md` §1 红线：positive/negative 只进图表和涨跌标注，
  版式件（标签/刻度）一律灰阶。

## 复用指引
- props：仅 `hostSrc`；数值 `target` / 点位 `pts` / 颜色在 CONFIG，标签与 x 轴文案写死在 JSX，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/metric-with-sparkline.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：`demos/metric-with-sparkline/index.html`。**换数据改两处**：`CONFIG.target`（计数终值）
  和 `CONFIG.pts`（折线点位，SVG 局部坐标 `viewBox 0 0 400 96`，y 越小越高）；换文案改 HTML 里的
  `.label` 与 `.xlabels`。换涨跌方向：`CONFIG.color` 换 `#d70015`（negative）、
  箭头 SVG 的 path 上下镜像（`viewBox` 内把 `M10 2 … Z` 的 y 翻过来）、`arrowRise` 改成负值
  （跌要从上往下落）。`invPower1InOut` 那个反函数只对 `power1.inOut` 成立——
  换 `lineEase` 必须同步换反函数，或退回"点按弧长比例 × 线性时间"（此时 `lineEase` 也得用 `none`）。
- Remotion 移植：不建时间线，逐帧查表更直接。`frame` → 秒后：
  计数 `interpolate(t, [0.5, 1.4], [0, 67], {easing: Easing.out(Easing.quad), extrapolateLeft:'clamp', extrapolateRight:'clamp'})`
  再 `Math.round`；折线用 `<path strokeDasharray={L} strokeDashoffset={L * (1 - p)} />`，
  `p = interpolate(t, [0.5, 1.1], [0, 1], {easing: Easing.inOut(Easing.ease), …clamp})`；
  数据点的触发时刻在**编译期算好**（弧长比例过反函数），别在渲染里算。
  `clamp` 不能省——不 clamp 的话 t<0.5 时 dashoffset 会算出 > L 的值（无害）但计数会出负数。
- 剪辑软件对应物：剪映/CapCut——数字用"数字滚动"预设或直接打字帧（剪映没有真滚动计数，
  常见做法是把 0→67 拆成 8~10 个关键文本帧，**必须选等宽数字字体**否则跳宽），
  折线用"线条生长"或给一条形状层加"描边"效果打 dashoffset 两键；单位和箭头是**独立两层**，
  入点押在数字最后一帧（这一步不能省，省了就是本卡最大的坑）。
  AE——数字层用 Slider Control + `Math.round(effect("量")("滑块"))` 表达式，滑块打两键 0→67；
  折线用 Shape Layer + `Trim Paths` 的 `End` 0→100%；数据点四个层，入点按 Trim Paths 到该点的
  **实际进度**手对（AE 里可以直接拖着看，比算反函数快）。
- 与本库同类卡的分工：`number-counter` = 滚动本身是主体（odometer 滚轮 + 大额千分位，量级感）；
  `number-slab-pop` = 一次弹出的结论（无过程）；`chart-grow` = 多项对比的柱状生长；
  `line-chart-story-draw` = 一条线讲一个故事（分段推演 + 标注）；
  **本卡 = 一个数 + 它的趋势压成一拍**（两层信息、一个动效、一个落点）。

## 动效范围
- 属于本卡的：「计数与折线同刻起跑、`lineDur ≈ 2/3 countDur`」这条时间纪律；「单位与箭头押在计数结束那一帧」这条结论签名纪律；数据点触发时刻由**弧长比例过缓动反函数**换算（而不是时间均分）这个实现要求；箭头 `y+12 → 0` + `scale 0.8→1`、`transform-origin: 50% 100%` 的从下弹入；`tabular-nums` + 整行 `nowrap` 这个排版纪律；折线 `dasharray` 取整数长度这个避漏笔的细节；hold 期完全静置（数字不做微动）。
- 不属于本卡的：「本周剪辑效率 / 67% / 周一~周四」这套具体文案与数据、`#2fb344` 这个绿（换 accent 或 negative 红都成立）、86px/34px 的字号、折线 400×96 的画布尺寸与 3px 笔宽、数据点的白心圆样式、右侧主持人（数字人）占位、以及"指标块左对齐在 96px"这个落位（居中、右对齐、下三分之一都成立）。
- 迁移接口：`CONFIG.target` + `CONFIG.pts` 是唯一的内容入口；能量只调 `countDur`，`lineDur` 必须跟着保持约 2/3 的比例；`arrowRise` 按字号的 14% 等比缩放；换 `lineEase` 必须同步换数据点的缓动反函数；换涨跌方向要同改 `color`、箭头 path 朝向、`arrowRise` 正负三处；竖屏把折线宽度收到舞台宽的 80%、字号降到 64px 并把数据点减到 3 个（横向空间少，4 点以上密到读不出"依次"）。
- 底色要求：白底即可。深底成立（数字与折线反白或换 `#30d158`，基线换 `rgba(255,255,255,0.14)`），唯一约束是**底不能有网格或纹理**——折线只有 3px 宽，底上的高频细节会和它抢，观众读不出那是一条趋势线。

<!-- ===== /file: video-talkcraft/references/cards/metric-with-sparkline.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/motion-blur-slam-in.md ===== -->

---
name: motion-blur-slam-in
标题: 模糊甩入急停
一句话: 配合数字人的一卡——素材卡带横向运动模糊从人物旁的画外高速飞入，0.2s 内急停落位，模糊量跟着速度由重到清、停住那一帧归零，落位再 2~3px 过冲回正
适用: 口播"直接甩给你看"的压上时刻（数据卡、产品截图、对比图）；凌厉、有攻击性的高能段落；AI 工具盘点、爆点拆解、观点硬怼
时长: 起手 0.4s；单卡飞入 0.2s（0.15~0.25）+ 过冲回正 0.1s；两卡同方向连发间隔 0.4s（0.3~0.5），1.1s 全部落定
能量: 高
类别: 素材呈现
输入: 图, 截图, 人(可选)
语义: 例证
素材形态: 无
位置: 任意
props: hostSrc
优先级: P1
代码: template/cards/motion-blur-slam-in.tsx
---

## 意图
**2026-08-26 用户定版：本卡是配合数字人的一卡**（原来的 demo 是左右分屏的
"对照组普通淡入 vs 本卡甩入"教学版）。这张卡的用法本来就是口播念到爆点时把素材怼上来，
观众看的是"人在说 + 素材砸到他旁边"；分屏对照是讲课用的，不是它在片子里的样子。
对照组那半屏也正好是人物要站的位置——于是人物占左 46%，素材从右侧净白区的外侧甩进来。

同样是"把素材压上来"，弹跳入场（media-pop-in）是"啪"地拍上桌，带着手作与俏皮；
甩入急停是"咣"地怼到你脸前，带着速度与压迫。口播念到爆点、要观众瞬间闭嘴看图时用它。
命门三条：**模糊必须有方向**（各向同性的 `blur()` 读作失焦，不是速度）、
**模糊量跟着速度走且停住那一帧必须归零**（停住还糊 = 渲染没算完的 bug 感）、
**停要真急停**（power4/expo.out 的强减速；power2.out 读作"滑进来"，气质立刻软掉）。

## 动效核心
- 元素：素材卡（截图/数据卡），一层轻投影把它与白底分开（投影让拖影更可读，但投影本身不是本卡动效）
- **飞入方向要背着人物**：人物在左 ⇒ 素材从右外侧进场。朝着人物飞会横穿人物身上，
  而且素材区的 `overflow: hidden` 会把越界那半张切掉
- 位移：沿单一直线从舞台外飞入，行程 ≥ 半屏（560px 级），0.2s，`power4.out`——快起 + 强减速 = 撞停手感
- 方向模糊：SVG `feGaussianBlur stdDeviation="σ 0"`（只糊横向 = 有方向），σ 由**速度**驱动：
  `σ = blurMax * (1 - p)^0.75`（p 为位移的**已缓动**进度，指数 0.75 是 power4.out 的速度衰减律）——
  一条 tween 同时驱动位移与模糊，天然对齐，不会出现"停住还糊"
- 落位过冲：飞入终点先多冲 2~3px（沿运动方向），再 0.1s `power2.out` 回正——一帧级的"顶到底"回弹，不是 back.out 大弹跳
- 多卡连发：同方向、间隔 0.3~0.5s，后来者层级更高压前者一角（20~30%）；方向一律统一，才读作"一沓一沓怼上来"
- 层级：底 UI/人物 < 先到的卡 < 后到的卡；模糊滤镜只挂在卡本体上，不要连着背景一起糊

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `fromX` | 560px（≥ 半屏） | 屏外起始距离 = 速度累积；<200px 像"挪了一下"，模糊无处发生；过大则前几帧完全在屏外，观感等于凭空出现 |
| `slam` | 0.2s | 0.15~0.25 是"甩"的窗口；>0.35s 变成平移滑入，凌厉感消失；<0.12s 观众只看到结果，看不到过程 |
| `slamEase` | `power4.out` | 急停的命；`expo.out` 更狠，`power2.out` 读作滑入，`linear` 读作程序在拖动元素 |
| `blurMax` | 18（240~300px 宽的卡） | 起点横向 σ，视觉拖影约 2~3σ；>25 糊成一团云雾看不出是什么素材，<8 等于没做模糊 |
| `blurFalloff` | 0.75 | 模糊随速度衰减的指数；调小（0.4）模糊拖得更久更狠但容易"停住还糊"，调大（1.5）模糊几乎只闪一帧 |
| `overshoot` | 3px | 到位过冲；0 则收尾发死，>8px 变成回弹入场（那是 media-pop-in 的气质） |
| `settle` | 0.1s | 过冲回正耗时；>0.2s 回正被看成第二段运动，"一帧顶到底"的脆感就没了 |
| `burst` | 0.4s | 多卡连发间隔；<0.2s 观众数不清几张，>0.6s 断成两个独立事件 |

## 已知坑
- 用 `filter: blur(Npx)` 整体糊——各向同性模糊一眼读作失焦/景深，完全读不出运动方向，白做。
- 模糊没在停住那一帧归零（或干脆全程挂着 σ>0）——静止画面还带拖影，观众读作渲染没算完的脏帧。
- 缓动用 `power2.out` 或匀速——变成"素材平移滑入"，跟廉价模板转场同类；急停必须是 power4/expo 级强减速。
- 过冲给到 8px 以上或用 `back.out(1.7)`——气质切回弹跳入场，这张卡与 media-pop-in 就没有区别了。
- 多卡各飞各的方向（一张从左、一张从上）——读作"随便加了几个入场特效"；同方向连发才有"一沓怼上来"的势。
- 模糊连着背景/人物一起糊——变成整屏运动模糊转场，素材本身失去主角地位。
- 飞入距离只有一两百 px——没有速度累积，模糊没地方发生，最后只是个位移淡入。

## 复用指引
- props：仅 `hostSrc`；两张素材卡是写死在 JSX 的 CSS 假截图（无 images[]），换真素材需改源码替换为 `<Img>`。
- Remotion/tsx（skill 首选）：template/cards/motion-blur-slam-in.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/motion-blur-slam-in/index.html。方向模糊 = `<defs>` 里每张卡一个 `feGaussianBlur stdDeviation="σ 0"` 滤镜（卡上 `data-mb="mbA"` 指过去），`setSigma()` 负责写 σ 并在 σ→0 时把 `filter` 摘成 `none`；节奏与手感全在顶部 `CONFIG`（`fromX`/`slam`/`slamEase`/`blurMax`/`blurFalloff`/`overshoot`/`settle`/`burst`）。换素材把 `.shot` 内部整块换成 `<img>` 即可；换方向把 `fromX` 换成 y 通道并把 σ 写成 `"0 σ"`（竖向甩入）。
- Remotion 移植：`const p = interpolate(frame, [f0, f0 + slamF], [0, 1], {easing: Easing.out(Easing.poly(4)), extrapolateRight: 'clamp'})`，位移 `translateX(${fromX * (1 - p) - overshoot * p}px)`，模糊 `σ = blurMax * Math.pow(1 - p, 0.75)` 写进同一 composition 里的 `<svg><filter>` 的 `stdDeviation={`${σ} 0`}`（或用 `filter: url(#mb)` 的 style）；过冲回正另起一段 `interpolate(frame, [f0+slamF, f0+slamF+settleF], [-overshoot, 0], {easing: Easing.out(Easing.quad)})`。多卡就是 `f0 = start + i * burstF`。σ 到 0 时把 style.filter 置空，避免整帧走一遍无用滤镜。
- 剪辑软件对应物：剪映——"入场动画→甩入/向左滑动"缩到 6~7 帧，再叠"运动模糊/拖影"特效（或复制两层降透明度做残影）；AE——位置关键帧 + Easy Ease 后拉曲线成急停，开图层 Motion Blur（或 ReelSmart/CC Force Motion Blur / Directional Blur 关键帧）；CapCut——"Slide in" + Motion Blur 效果，快门角度调大。

## 动效范围
- 属于本卡的：卡片沿单一直线从屏外飞入（行程 ≥ 半屏、0.15~0.25s、power4.out 强减速急停）；**方向性**模糊 σ 由位移的已缓动进度驱动 `σ = blurMax * (1 - p)^0.75` 并在停住那一帧归零；落位 2~3px 同向过冲 + 0.1s power2.out 回正；多卡同方向连发 0.3~0.5s 间隔与"后来者压前者一角"的层级堆叠。
- 不属于本卡的：demo 里的灰阶假截图内容与排版、卡片的具体落位坐标与尺寸、投影与描边样式（投影只是让拖影更可读的演示选择）、主持人数字人占位与"人物左 46% / 素材区右 54%"这个布局比例（**但"配合数字人"这条语境属于本卡**——见「意图」段）。
- 迁移接口：`fromX` 按输出宽度等比缩放（保持"≥ 半屏"，且方向要背着人物那一侧），`blurMax` 按卡片宽度等比缩放（240~300px 卡用 18，翻倍尺寸就翻倍 σ）；换飞入方向 = 换位移通道 + 把 σ 写到对应轴（`"0 σ"` 为竖向）；`slam`/`burst` 按口播语速缩放，缩放时 `slam` 与 `settle` 要同比例，否则脆感会变；配色/字体/投影全部可换，动效不依赖任何颜色。
- 底色要求：白底即可。唯一约束是滤镜要设 `color-interpolation-filters="sRGB"`，否则默认 linearRGB 会让模糊边缘在白底上出现发灰的脏边；深底同样成立（深底上拖影更明显，可把 `blurMax` 下调 20%）。

<!-- ===== /file: video-talkcraft/references/cards/motion-blur-slam-in.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/news-card-desk.md ===== -->

---
name: news-card-desk
标题: 新闻卡片划重点
一句话: 新闻截图包成白色圆角卡片、带 1~2° 歪度从下方 0.4s 滑上桌，1s 后红色下划线 0.3s 扫过标题关键句，第二张卡再从右侧压叠上来，卡片全程 8s 极缓 Ken Burns
适用: 解读/评论新闻、引用报道原文做证据的段落；财经、时事、盘点类口播的"先看这条新闻"时刻，调性冷静专业
时长: 单卡上桌 0.4s；红线在 1.0s 处扫 0.3s；第二卡 1.9s 入场；Ken Burns 全程 8s 铺底
能量: 中
类别: 素材呈现
输入: 图, 截图
语义: 引用, 例证
素材形态: 无
位置: 任意
props: hostSrc(未使用)
优先级: P0
代码: template/cards/news-card-desk.tsx
---

## 意图
口播里直接糊一张新闻截图 = 静态 PPT；把截图包成"摆上桌"的卡片并当着观众的面划出重点，
既给素材入场仪式感，又替观众完成"该看哪一句"的视线引导。命门三条：
**Ken Burns 必须极缓**（8s 才推 4%，快了读作镜头晃）；**红线要等朗读到关键词才扫**
（与卡片同时出现就不是"划重点"而是"印刷体"）；**卡片必须轻微歪 1~2°**
（直挺挺立在正中读作软件弹窗，歪了才像"摆上桌"的实物）。

常见于：小Lin说、差评君（伪窗口版）、IC实验室、评论向频道。

## 动效核心
- 卡片结构：白底圆角（radius 8px）+ 描边 #e0e0e0 + 投影（白底桌面上 0 14px 30px rgba(0,0,0,.14) 足够分层；深底桌面需加深）+ 假新闻排版：报头/日期一行 + 粗底线、标题 h2、正文用灰条代替
- 卡 A 入场：opacity 0→1 + y 60px→0，0.4s，`power3.out`，带 rotate -1.5° 定歪
- Ken Burns：卡内包一层 `.kb-inner`（transform-origin 50% 40%），落位后 scale 1→1.04，8s，`ease:none`——卡片"活着"但不晃
- 红线：标题关键词包 span，内嵌绝对定位红条（#d8383a，高 5px，贴字底），1.0s 时 scaleX 0→1，0.3s，`power2.out`，`transform-origin: left center`——从左往右"划"出来
- 卡 B 堆叠：1.9s 时从右侧 x 320px→0 + 淡入，0.4s，`power3.out`，rotate +2°（与卡 A 反向歪），DOM 顺序在后自然压在卡 A 之上，落位后同样开始自己的 Ken Burns
- 层级：红线时刻要与口播台词呼应（"重点是这一万亿"）；字幕件不在 tsx 内，落地时留在卡片层之上

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| slideIn | 0.4s | >0.6s 上桌拖沓像浮现；<0.25s 读作弹窗 |
| slideY | 60px | 越大"从桌外拿进来"感越强；>120px 滑程抢戏 |
| tiltA / tiltB | -1.5° / 2° | 归零立刻假（软件弹窗感）；>4° 读作东倒西歪 |
| redlineAt | 1.0s | 必须对齐朗读到关键词的时刻；提前=印刷体，滞后=划错重点 |
| redline | 0.3s | >0.5s 像慢镜头描字；<0.15s 看不出"划"的动作 |
| cardBAt | 1.9s | 跟着口播列举节奏走；太近两卡打架，太远堆叠感断掉 |
| kenburns | 1.04 | >1.08 开始读作 zoom 镜头；1.0 卡片死板 |
| kbDur | 8s | 越长越沉稳；<4s 就像手持晃动 |

## 已知坑
- Ken Burns 推快了（<4s 或倍数 >1.08）——观众读到的是"镜头在晃"而不是"素材活着"。
- 红线和朗读不同步——红线先于人声划出等于剧透，一眼看穿是预渲染动画。
- 卡片直挺挺立在画面正中——零旋转 + 居中 = 软件 alert 弹窗，歪 1~2° 才是"摆上桌"。
- 两张卡不重叠、各占一边——没有压叠就没有"桌面越摆越满"的列举感，成了并排 PPT。
- 红线用 width 动画而不是 scaleX——width 回流抖动且不吃 GPU，扫动不顺滑。

## 复用指引
- props：仅 `hostSrc`（未使用）；两张新闻卡的报头 / 日期 / 标题写死在 JSX，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/news-card-desk.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/news-card-desk/index.html。换文案改两张卡里的 `.paper`（报头）、`.date`、`h2` 标题即可；要划的关键句包在 `<span class="kw">…<span class="redline"></span></span>` 里；红线颜色改 `.redline` 的 `background: #d8383a`，卡底色改 `.news-card` 的 `background`。节奏全部在顶部 `CONFIG`：`redlineAt` 对齐你的语音重音，`cardBAt` 对齐第二条素材的口播时刻，`tiltA/tiltB` 控制歪度。核心动画即 `DemoShell.register` 内那一段 timeline，连同 CONFIG 复制可直接摘走。
- （实测变体）译文条覆盖：外文截图不用红线划重点，而是在关键句上直接叠一条白底黑字的译文横条（宽度对齐该句，压在原文之上）——观众省掉"读外文再理解"的一步；适合引用英文报道/推文的段落，与红线通道二选一。见小Lin说·韩股崩盘。
- Remotion 移植：卡片入场用 `spring({frame, config:{damping:200}})` 驱动 y/opacity；Ken Burns 用 `interpolate(frame, [inFrame, inFrame+8*fps], [1, 1.04])` 慢推（clamp）；红线单独包 `<Sequence from={redlineAt*fps}>`，内部 `interpolate(frame, [0, 0.3*fps], [0, 1])` 驱动 scaleX；第二张卡再包一个 `<Sequence from={cardBAt*fps}>` 重复同一入场组件。
- 剪辑软件对应物：剪映——素材加"白色边框"贴纸打底 + 入场动画"向上滑动"，红线用"画笔/线条贴纸"的擦除入场，缓推用"缩放"关键帧拉满全程；AE——卡片做预合成，Position/Opacity 关键帧 + Scale 100→104 线性，红线是 Shape Layer + Trim Paths；CapCut——"Photo frame" 模板 + "wipe right" 的线条 element，zoom 用 keyframe 手动拉。

## 动效范围
- 属于本卡的：卡片"摆上桌"入场——opacity 0→1 + y 60px→0（0.4s、power3.out）并带 1~2° 定歪（零旋转即读作软件弹窗）；落位即起的极缓 Ken Burns（内层 `.kb-inner`、scale 1→1.04、8s、ease none，origin 50% 40%）；划重点的下划线 scaleX 0→1（0.3s、power2.out、origin left center）且必须等朗读到关键词才扫（早于人声＝剧透）；第二张卡延迟入场从侧向滑入 + 反向歪度、DOM 顺序在后自然压叠，落位后各自跑自己的 Ken Burns；卡片必须离开背景一层（投影/描边）这条约束。
- 不属于本卡的：假新闻的排版（报头、日期、灰条正文）、标题与字幕文案、卡片圆角与字号、下划线的具体色值、桌面底色。
- 迁移接口：`redlineAt` 对齐你的语音重音、`cardBAt` 对齐第二条素材的口播时刻（两者是唯一需要跟音频对齐的参数）；`slideIn` / `slideY` 调上桌行程；`tiltA` / `tiltB` 控歪度（保持一正一负）；`kenburns` / `kbDur` 控"活着但不晃"（>1.08 或 <4s 就读作镜头晃）；`cardBFrom` 换第二张卡的进场方向；划重点色换 `.redline` 的 `background` 一处。
- 底色要求：白底即可。卡片本身也是白底，靠 #e0e0e0 描边 + 一层 14% 黑投影与舞台分层——这两者不能同时去掉。深底桌面时把卡片保持白、投影加深即可，时序不变。

<!-- ===== /file: video-talkcraft/references/cards/news-card-desk.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/number-counter.md ===== -->

---
name: number-counter
标题: 数字滚动计数
一句话: 大号数字从 0 滚到目标值，1~1.5s 先快后慢，落定瞬间轻放大一拍、涨跌箭头随后淡入；变体是逐位滚轮高位先停
适用: 财经/科普口播抛出关键数字的时刻（营收、销量、涨幅）；让数字"长"出来而不是贴出来；数据密集调性
时长: 计数 1~1.5s + 落定弹一拍 0.27s + 单位淡入 0.25s；odometer 变体延后 0.5s 起、高位滚 1s、每低一位多滚 0.22s
能量: 中
类别: 数据信息图
输入: 文, 人(可选)
语义: 数据
素材形态: 无
位置: 任意
props: hostSrc
优先级: P0
代码: template/cards/number-counter.tsx
---

## 意图
数字直接贴上屏，观众只是"看到"；从 0 滚上去，观众会跟着"数"，量级感是滚出来的。
命门：**先快后慢**（easeOut 让最后几位清晰可读，线性滚动没有落定感）、
**落定要弹一拍**（scale 1→1.08→1，告诉观众"就是这个数"）、
**别滚太久**（>2s 观众已经听完这句话了，动效还没完就是抢戏）。

常见于：小Lin说、何同学、Wendover、影视飓风、Odometer 模板（1.2K 销量）。

## 动效核心
- 模式 a（tween 版）：数值对象 0→目标，1~1.5s `power3.out`，`onUpdate` 里实时 `toLocaleString` 千分位格式化；落定帧 scale 1→1.08（0.09s）→1（0.18s `back.out(3)`，origin 设在数字左下角避免整行漂移）；单位/涨跌箭头随后 0.25s 淡入 + 上移 6px
- 模式 b（odometer 版）：每位数字一个竖向滚轮（0-9 重复 2~3 圈的长条，容器 overflow hidden），reel 的 y 按"步数 × 行高"（demo 行高 64px）滚动到目标位；高位时长短、低位每位多 0.15~0.25s——高位先停低位后收敛，低位要多滚整圈数（必须是 10 的整倍数，否则落错数字）
- 排版：大字（占屏宽 1/3 以上）+ `font-variant-numeric: tabular-nums`（等宽数字防抖列）；旁配小字标签说明数字是什么。底色深浅都成立，只需数字与底有足够对比
- 层级：标签先在（或同时淡入）→ 数字滚 → 单位/箭头最后

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 计数时长 | 1.3s | 调短到 0.8s 干脆利落适合快剪；>2s 观众等得不耐烦 |
| 缓动 | power3.out | 换 power1.out 尾段还在跳数字，读不清；expo.out 尾段太黏 |
| 落定弹幅 | 1.08 | >1.15 像重音强调抢了数字本身的戏；不弹则"到了没有"说不清 |
| 单位淡入延迟 | 落定后立即 | 和数字同时出会分散视线；晚超过 0.5s 像漏做了 |
| odometer 高低位时差 | 0.22s/位 | 调大滚轮感更强更"机械"；为 0 全部同时停 = 普通数字翻页 |
| 低位额外圈数 | 2 圈 | 越多越有"老虎机"感；0 圈低位几乎不动，滚轮白做 |

## 已知坑
- 线性滚动——匀速到达没有"落定"的呼吸，观众不知道数字停没停。
- 小数/低位一起乱滚——量级读不出来；要么只滚整数，要么 odometer 让高位先停锚定量级。
- 数字不等宽——列宽随数字抖动，整行文字跟着跳（必须 tabular-nums 或等宽字体）。
- 滚动中就把单位、箭头全堆上——信息一次全到，滚动的悬念白费；单位是"落定"的奖励。
- 目标值太小还硬滚（如 0→7）——两位数以内直接弹出即可，滚动反而做作。

## 复用指引
- props：仅 `hostSrc`；`target` / `odoTarget` 在 CONFIG，标签与单位文案写死在 JSX，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/number-counter.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/number-counter/index.html。模式 a 改 `CONFIG.target/countDur`，模式 b 改 `CONFIG.odoTarget`（字符串保位数）；`buildOdometer()` 自动按位生成滚轮，含千分位逗号。
- Remotion 移植：模式 a `Math.floor(interpolate(frame, [0, dur], [0, target], {easing: Easing.out(Easing.cubic)}))` 再 toLocaleString；模式 b 每位一个 `<div>` 用 spring 驱动 translateY，delay 按位序递增。
- （实测变体）记账卡跳变：分步账目推演时不滚动——账目行的数字**瞬时跳变**到新值，旁边一个"+20"角标小弹出，同帧该行整体轻高亮；因为观众要读的是"这一步加了多少"，滚动会把差值糊掉。适合逐笔算账、成本拆解类段落。见小Lin说·韩股崩盘。
- 剪辑软件对应物：剪映"文字模板→数据/计数"类；AE 用 Slider Control + `Math.floor` 表达式（经典做法）；CapCut "Number counter" 贴纸。

## 动效范围
- 属于本卡的：模式 a——数值 0→目标的 tween（1~1.5s、power3.out、onUpdate 里实时千分位格式化）、落定瞬间 scale 1→1.08→1 弹一拍（0.09s 上 + 0.18s back.out(3) 回、origin 数字左下）、涨跌/单位随后 0.25s 淡入 + 上移 6px；模式 b——每位滚轮 translateY 按"步数 × 行高"滚到目标位（power3.out）、高位时长短低位每位多 0.22s（高位先停低位后收敛）、低位额外整圈数必须是 10 的整倍数。层级顺序（标签先在 → 数字滚 → 单位/箭头最后）也属于本卡。
- 不属于本卡的：主持人占位与分栏线、示例数值与标签文案、字号字重与 `tabular-nums` 之外的排版、滚轮窗口的圆角/描边样式、涨跌色的具体色值。
- 迁移接口：`target` / `odoTarget` 换数值；`countDur`、`odoBase`、`odoStagger` 按语速缩放（口播一句话内滚完为准）；`landScale` 调落定力度；`spins` 调滚轮机械感；`digitH` 必须与滚轮 DOM 的行高一致（改字号时同步改）；数字色用文字主色、涨跌色用一个语义色 token。
- 底色要求：白底即可（数字用 #1d1d1f）。深底只需把数字与滚轮窗口反色，计数与滚轮的时序、缓动完全不变。

<!-- ===== /file: video-talkcraft/references/cards/number-counter.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/number-slab-pop.md ===== -->

---
name: number-slab-pop
标题: 数字弹出
一句话: 实色块先从上方落定 0.24s（数字此刻还不在场），块稳住后巨大整数一次弹出 scale 0.72→1（back.out 1.7），小数与单位延后 6 帧单独淡入，说明行最后淡入上浮 6px
适用: 口播抛出一个结论数字时（"23.6%，这是去年的增幅"、"只要 3 步"）；一句话就要立住的钩子数字、封面数、章节里的单点结论；不适合需要展示"怎么算出来的"的数（那用 number-counter / metric-with-sparkline）
时长: 静置 0.3s → 块落 0.24s → 数字弹 0.28s（小数 +0.2s 延后）→ 说明行 0.24s → hold 1.8s；共约 3.0s
能量: 中
类别: 数据信息图
输入: 文, 人(可选)
语义: 数据, 钩子
素材形态: 无
位置: 任意
props: hostSrc
优先级: P0
代码: template/cards/number-slab-pop.tsx
---

## 意图
一个数字在口播里有两种职能：**过程**和**结论**。

`number-counter` 做的是过程——滚轮转、千分位跳、观众盯着它爬，那 1.3 秒的"算"本身是内容
（"钱是一点点烧掉的"）。`metric-with-sparkline` 也是过程（0→67 的 0.9s 滚动 + 同刻画出的趋势线）。
过程感的代价是**观众必须等**：数字在动，结论还没成立。

这张卡是**结论感**：数字不给过程，一次弹出就到位。用在口播已经把话说完、
现在需要一个"钉"把这句话钉在屏上的时候——观众不需要看它怎么来的，只需要它**立住**。
这也是它能做封面数、钩子数的原因：0.3 秒内屏上就有一个可复述的东西。

命门两条：
① **块和数字不能同时进**。同时进就是一整块 PNG 飞进来——观众读作"贴了一张图"，
数字失去主语地位。**块先落定（0.24s），块稳住的那一帧数字才开始弹**。
这 0.24s 的空块在屏上是有意义的：它是"位置已经占好了，内容马上到"的预告。
② **小数延后单独淡入**。「23」先立住，「.6」是精度补充——这个先后关系传达的是
"这个数大概是 23，准确说是 23.6"，符合人报数字的自然顺序。整个「23.6」一起弹出没错，
但少了这层"整数是主干、小数是细节"的层级，读作一个更长的数字串。

## 动效核心
- **层级**（自下而上）：白舞台 → 实色块（`display: inline-block`，圆角 28px = design-language
  §3 的卡片档，padding 26/40/30）→ 数字行（`display:flex; align-items:baseline`，
  `white-space: nowrap` + `font-variant-numeric: tabular-nums`，白字 600）→
  说明行（块外、下方 22px，灰 20px）。主持人占位在右侧 47%，色块左对齐在 108px。
  **块宽由数字撑出来**（`inline-block` + padding），不写死宽度——换数字位数自动跟着变。
- **① 块先落**：`t = 0.30` 起，`opacity 0→1` + `y −20→0` + `scale 0.94→1`，
  0.24s `power3.out`，`transform-origin: 50% 50%`。
  从**上方**落（不是下方升起）——"落"有重量，"升"有轻盈感，结论数字要重量。
- **② 数字弹出**：`numAt = 0.30 + 0.24 = 0.54`（= 块落定的那一帧），
  整行 `opacity 0→1` + `scale 0.72→1`，0.28s `back.out(1.7)`，
  `transform-origin: 50% 60%`（重心略偏下：弹出时字不往上飘）。
  **`back.out` 在本库是受限使用的缓动**（design-language §4：夸张弹跳才用）——
  这里是它成立的场合之一：一次弹出的"结论落地"就是要那一点过冲，
  回弹量 1.7 比 `bar-chart-growth` 的 chip（1.4，落章）更弹一点，但离漫画弹跳（≥2.2）还有距离。
- **②b 小数 + 单位延后**：`numAt + 0.20`（≈6 帧 @30fps）起，`opacity 0→1` 0.18s `power2.out`。
  **它们从一开始就占位**（只动 `opacity`，不动 `display`）——否则淡入那一帧整行宽度变了，
  整数被推着挪一下（本卡最隐蔽的坑）。
- **③ 说明行**：`capAt = numAt + 0.20 + 0.18 = 0.92`，`opacity 0→1` + `y +6→0`，
  0.24s `power2.out`。它在**块外**——说明是注解，不是块的内容。
- **④ hold 1.8s**：全静置。
- **唯一语义色 `#0066cc`（accent 蓝）**：只上在色块上，块内字反白，说明行走灰。
- **`tabular-nums` 是硬要求**：本卡虽然不滚动，但一旦复用者把它接到"数字会换"的场景
  （比如同一个组件报不同的数），比例数字下块宽会跳。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `slabDur` | 0.24s | 块落定时长；<0.15s 块"闪"出来（"位置占好了"的预告读不到），>0.4s 观众盯着一个空色块等内容 |
| `slabDrop` | 20px | 块的下落位移；0 则块只是淡入（没有重量），>40px 读作块从画外掉进来（转场语感，抢了数字的戏） |
| `slabScale` | 0.94 | 块的起始缩放；1.0（无缩放）也成立但少一点"落到位"的手感，<0.85 块自己成了一个弹出动效 |
| `numScale` | 0.72 | **数字起始缩放，本卡的能量旋钮**；0.9 读作轻微放大（结论不够"砸"），<0.5 数字从一个点炸开、读作特效不是数据 |
| `numDur` | 0.28s | 数字弹出时长；<0.2s 配 `back.out(1.7)` 过冲太急读作抖了一下，>0.4s 弹性变软、结论感松掉 |
| `back.out(1.7)` | 1.7 | 回弹量；1.0（= 无过冲）读作普通放大淡入（结论落地的"钉"感丢掉），>2.2 读作漫画弹跳（数据卡不该有的语言） |
| `decLag` | 0.20s | **小数延后，本卡第二命门**；0 则整串一起弹（少了"整数主干 / 小数细节"的层级），>0.4s 小数来得太晚、读作后面又补了个数 |
| `capRise` | 6px | 说明行上浮；0 可用（更安静），>16px 说明行自己成了一个入场动效，和数字抢 |
| `hold` | 1.8s | 收尾定格；一个结论数字要停住让人复述，<1.0s 观众来不及记 |
| 整数字号 | 96px | 相对舞台高（540）的 18%——**这个比例是本卡的骨架**；<12% 数字撑不起"结论"，>25% 块的 padding 挤不出来、数字贴边 |

## 已知坑
- 块和数字同时入场——一整块 PNG 飞进来，数字失去主语地位；块必须先落定，这是本卡一号命门。
- 块从**下方**升起——"升"是轻盈的（`media-pop-in` 的语言），结论数字要"落"的重量。
- 小数和单位用 `display: none → block` 切换（而不是 `opacity`）——淡入那一帧整行宽度变了，
  整数被推着横向挪一下，慢放一眼看出。它们必须从头占位。
- 块写死宽度——换成位数不同的数字（`8.2%` / `128.6%`）后必然出现左右留白不对称或数字撞边。
  块宽必须由数字撑出来（`inline-block` + padding）。
- 数字 `transform-origin` 用默认的 `50% 50%`——弹出末段字会往上飘一点点（因为视觉重心比几何中心低），
  取 `50% 60%` 才稳。
- 说明行放在块内——那就成了块的一部分（读作"色块里有两行内容"），本卡的说明是**块外的注解**。
- 回弹量拉到 2.2 以上还叫它数据卡——那是漫画弹入的语言，
  数据一弹三抖读作"这数在开玩笑"。
- 不写 `tabular-nums`——本卡不滚动所以单次播放看不出，但复用到"同一组件报不同数"的场景时块宽会跳。
- 给数字做滚动计数——那就变回 `number-counter` / `metric-with-sparkline` 了，
  本卡的全部价值在于**没有过程**。要过程请直接用那两张。
- hold 期给块或数字加漂移/呼吸——结论是"钉住"的，动起来读作"还没定"。
- 语义色除了块之外还上到说明行——`design-language.md` §1：一屏只有一个强调色的载体，
  说明行是 dim 实色（`#8a8a8a`，且**不许再叠 opacity**，§1 浅底红线）。

## 复用指引
- props：仅 `hostSrc`；数字 `.int` / `.dec` / `.pct` 与说明行 `.slab-cap` 文案写死在 JSX，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/number-slab-pop.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：`demos/number-slab-pop/index.html`。**换数字改 HTML 里三个 span**：
  `.int`（整数）/ `.dec`（小数，含小数点）/ `.pct`（单位）；没有小数就删掉 `.dec` span
  并把 `decLag` 用于单位（时序不用改）；换文案改 `.slab-cap`。
  换色改 `.slab` 的 `background`（块内字保持白）；块宽自适应，不用动。
  **整数字号是骨架**：改 `.num-row .int` 的 `font-size` 时 `.dec` 要同步（两者必须同号，
  差一号读作两个数字），`.pct` 取整数的 55%。
  想要更"砸"：只调 `numScale`（0.72 → 0.6），不要动 `back.out` 的回弹量（那会改变语言类别）。
- Remotion 移植：三层各自逐帧算，不建时间线：
  块 `opacity/y/scale` 三条 `interpolate(t, [0.30, 0.54], …, {easing: Easing.out(Easing.cubic), extrapolateLeft:'clamp', extrapolateRight:'clamp'})`；
  数字的 `back.out(1.7)` 在 Remotion 里用 `spring({frame: frame - 0.54*fps, fps, config: {damping: 12, stiffness: 200, mass: 0.6}})`
  近似（或用 `Easing.out(Easing.back(1.7))`，后者与 GSAP 的 `back.out(1.7)` 数学上等价，更省事）；
  小数与单位是同一条 `interpolate(t, [0.74, 0.92], [0, 1])` 的 opacity，
  **两个 span 从第 0 帧就渲染**（只是 opacity 0）——不要条件渲染，否则会出现宽度跳变。
  `clamp` 不能省：不 clamp 时 `t < 0.30` 的块会算出负 opacity 与 > 1 的 scale。
- 剪辑软件对应物：剪映/CapCut——**两个独立层**：色块（形状/背景层）打"位置 + 缩放 + 不透明度"
  两键（0.24s），数字（文本层）入点押在色块最后一帧、用"弹性弹出"或"放大入场"预设
  （剪映的"弹性"就是 back 家族，回弹量不可调，接受即可）；小数如果要单独延后，
  **把「.6」拆成第三个文本层**手动对位（剪映没有"文本内部分段动画"）——
  这一步在剪映里成本不低，只做整数 + 单位两层是合理取舍（丢掉本卡的第二命门，保住第一命门）。
  AE——块层 `Position` + `Scale` + `Opacity` 三组两键；数字层 `Scale` 两键 +
  `Easy Ease` 后把手柄拉出过冲，或直接上 `Overshoot` 类脚本；
  小数做成独立文本层，入点 +6 帧。`Anchor Point` 记得移到 `50% 60%`。
- 与本库同类卡的分工：`number-counter` = 滚动计数的**过程感**（odometer 滚轮 + 千分位大额，
  "一点点烧掉"）；`metric-with-sparkline` = 一个数 + 它的趋势（也是过程感，0.9s 滚动 + 同刻折线）；
  `count-badge-title` = 数字当标题的重音（"3 个方法"里的 3，数字是句子成分）；
  `behind-text-title` / `slab-punch-title` = 色块 + 文字的标题类（主体是字不是数）；
  **本卡 = 一次弹出的结论数字**（无过程、块先字后、整数主干 + 小数细节）。
  同屏出现过一次本卡后，全片其余数字建议走过程感的那两张——**结论感用多了就不是结论了**。

## 动效范围
- 属于本卡的：「块先落定、块稳住那一帧数字才弹」这条两拍纪律（含中间那 0.24s 空块作为"位置预告"）；块从**上方**落（`y −20 → 0` + `scale 0.94`）这个"重量"选择；数字 `scale 0.72→1` + `back.out(1.7)` 的一次弹出、`transform-origin: 50% 60%` 的略偏下重心；小数与单位**延后 6 帧单独淡入**且**从头占位只动 opacity**（拒绝 display 切换）这个层级与实现纪律；说明行在**块外**、最后淡入上浮 6px；块宽由数字撑出（不写死）；`tabular-nums`；hold 期完全静置。
- 不属于本卡的：「23.6% / 较去年增长」这套具体文案与数值、`#0066cc` 这个蓝（换任何一个 accent 都成立）、96px/52px/20px 的字号、28px 圆角与 26/40/30 的 padding、右侧主持人（数字人）占位、以及"色块左对齐在 108px、垂直居中"这个落位（居中、右对齐、封面正中都成立）。
- 迁移接口：HTML 里 `.int` / `.dec` / `.pct` 三个 span 是唯一的内容入口；整数字号按舞台高的 18% 取（`.dec` 同号、`.pct` 取 55%），`slabDrop` 按整数字号的 20% 缩放，`capRise` 按说明行字号的 30% 取；能量只调 `numScale`（不动 `back` 的回弹量——那会改变动效的语言类别）；无小数时把 `decLag` 转用于单位、时序不动；竖屏整数字号取舞台宽的 22%（竖屏可用宽度是瓶颈，不是高度）。
- 底色要求：白底即可。深底成立且更常见（块换 `#2997ff` 一类的深底 accent，说明行换 `#a1a1a6`；块内字保持白）。唯一约束是**块与底必须有明确明度差**——本卡的第一拍是"一个空块落下来"，块看不清这一拍就没了；浅底上不要用比 `#f5f5f7` 更浅的块色，深底上不要用比 `#2a2a2c` 更深的块色。

<!-- ===== /file: video-talkcraft/references/cards/number-slab-pop.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/numbered-step-stack.md ===== -->

---
name: numbered-step-stack
标题: 编号步骤堆入
优先级: P1
代码: template/cards/numbered-step-stack.tsx
一句话: 四枚带编号方块的横条从右侧以严格均匀的 0.11s 错峰依次堆进来，每枚落定的同一帧它的编号块 punch 一下（1.12→1，4 帧）当作"落地确认"，四枚都到位后整组轻微上浮 4px 把它们收成一件事
适用: 口播里"给方法"的段落——"记住这四条"、"操作就三步"、清单式干货；需要观众截图保存的时刻；带货/教程类口播的要点罗列。不适合有先后依赖的流程（那用 step-timeline-vertical）
时长: 起手静置 0.4s → 四枚错峰堆入 0.71s → 整组收束 0.28s → 收尾 hold 1.8s；共约 3.2s
能量: 中
类别: 数据信息图
输入: 文, 人(可选)
语义: 步骤, 列举
素材形态: 无
位置: 任意
props: hostSrc
---

## 意图
口播里最常见的一种句子是"我给你四条"。它的动效需求非常朴素：**四条要看得清、要感觉是一组、
要让人有截图的冲动**。听起来简单，但绝大多数做法会踩两个坑之一——要么四条一起淡入
（读作一张静态图，观众不知道该从哪读起），要么四条各自花式弹跳（读作四个动效，
观众开始数动画而不是读内容）。

这张卡走的是中间那条线：**逐条进、但错峰密到读作一串**（0.11s × 4 = 0.44s 走完全部），
然后**用一次极轻的整组上浮把四条收束成一件事**。观众的体验是"啪啪啪啪，四条给完了"——
逐条给了阅读顺序，整组收束给了"这是一组、清单完整"的确认。

它与 `step-timeline-vertical` 是一对孪生卡，区别只有一条但很硬：**这张没有线**。
没有线就没有因果，四条是并列的、顺序可换的；有线就有依赖，顺序不能颠倒。
选错卡的代价是观众理解错了内容的结构，比动效丑更严重。

命门两条：① **错峰必须严格均匀（0.11s × 4）**。不均匀（0.1 / 0.16 / 0.09）读作卡顿或掉帧，
是本卡唯一会让人觉得"这视频做得糙"的地方；② **编号块的 punch 是"落地确认"不是弹跳**——
4 帧、`power2.out`、从 1.12 收到 1，**没有回弹**。用 `back.out` 会读作四个小球在蹦。

## 动效核心
- **层级**：白底 → 人物层（左列）→ 四枚横条（右侧，垂直居中，`gap 14px`）；
  每枚横条 = 编号方块（左，实色强调色）+ 文字（右）+ 1px hairline 边框（`#e0e0e0`，**不用投影**）
- **① 横条堆入**：每枚 `x +40 → 0` + `opacity 0 → 1`，`0.24s power3.out`，**错峰严格 0.11s**
- **② 编号块 punch**：在该枚横条**落定的同一帧**触发（`at + barIn`），
  `scale 1.12 → 1`，`0.133s`（4 帧 @30fps），`power2.out`，**无回弹**。
  只作用在编号块上——横条整体不参与，punch 是"这一条落地了"的局部确认
- **③ 整组收束**（末枚 punch 完 + 0.08s 呼吸后）：**整个 `.stack` 容器** `y 0 → −4px`，
  `0.20s power2.out`。位移必须极小（4px @540h ≈ 0.7%）——它不是"整组飞起来"，
  是一次几乎读不出的"合上"，宣告清单完整
- **④ hold 1.8s**：四条要读完（每条约 0.45s）
- **总时长账**：`0.4`（lead）+ `3×0.11`（错峰）+ `0.24`（末枚入场）+ `0.133`（punch）
  + `0.08`（呼吸）+ `0.20`（收束）+ `1.8`（hold）= 约 3.18s

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `barStagger` | 0.11s | **命门**：错峰量，且必须**四枚等值**；>0.2s 读作四个独立动效（观众数动画），<0.06s 读作整块淡入（丢掉阅读顺序），任何不均匀都读作卡顿 |
| `barIn` | 0.24s | 单枚入场耗时；>0.4s 四枚加起来太久、口播已经念到第三条了；<0.15s 位移看不见、退化成淡入 |
| `barShift` | 40px | 从右侧进入的位移（约横条宽的 8%）；0 只剩淡入（没有"堆进来"的动作），>90px 读作横向飞入（四枚飞入 = 花屏） |
| `punchScale` | 1.12 | 编号块 punch 起始倍数；<1.06 看不出"落地"，>1.25 读作编号块单独在弹（抢过横条本身的入场） |
| `punchDur` | 0.133s（4 帧） | punch 时长，**必须短**；>0.3s 读作编号块在做自己的入场动画，与横条脱钩 |
| punch 缓动 | `power2.out` | **不许用 `back`**；带回弹立刻读作四个小球在蹦（本卡的能量档整个跳上去，也就不再是"清单"了） |
| `settleLift` | 4px | 整组收束位移；0 少了"这是一组"的收口（可用但更散），>12px 读作整组飞起来（末枚刚落地又整体动，观众读作两个动效） |
| `settleGap` | 0.08s | 末枚 punch → 整组收束 的呼吸；0 收束混在 punch 里读不出来，>0.3s 两拍断开（观众以为结束了又动一下） |
| 条数 | 3~5 条 | 4 是最舒服的；>5 条行高压缩、错峰累积到 0.66s 以上（首尾差太大，读作"扫过"不是"一串"），要么减 `barStagger` 到 0.08s 要么拆两屏 |
| `hold` | 1.8s | 收尾停留；按条数给（每条约 0.45s）。这是给"截图"留的时间，宁长勿短 |

## 已知坑
- 错峰不均匀（手写 delay 时最容易犯）——四枚间隔 0.1 / 0.16 / 0.09 读作掉帧，
  是本卡唯一会让整条视频显得"糙"的错法。必须由 `i * barStagger` 算出来。
- 编号块 punch 用 `back.out`——四个小球在蹦，清单的冷静感全丢（这是本卡与
  贴纸涂鸦类花字卡的分界线）。
- punch 作用在整枚横条上——横条刚落定又整体缩放一下，读作"没停稳"（像回弹过冲）。
  punch 必须只在编号块这个局部。
- 整组收束的位移给到 12px 以上——末枚刚落地整组又走一段，观众读作"第五个动效"，
  收束的意思是"合上"不是"再来一下"。
- 横条加投影做层级——design-language §3：投影只给证据素材（截图/照片）。
  清单条用 1px hairline + 底色差立层级就够，加投影一眼是 PPT 模板。
- 四枚横条都上强调色底 + 白字——四条一样重就没有层级，整屏读作一块色板；
  强调色只上在编号块上（占比小、位置固定，读作"序号"而不是"高亮"）。
- 给某一条单独高亮——那是 `chapter-progress-list` 的语言（"当前"）。清单里四条等重，
  想强调其中一条说明你要的是另一张卡。
- 用它来讲有依赖的流程——观众会以为顺序可换。有依赖必须有线（`step-timeline-vertical`）。
- 横条宽度按各自文字贴合（宽度不齐）——清单的"是一组"靠**等宽 + 等高 + 等间距**表达，
  宽度不齐读作四个独立卡片。
- 重播不重置编号块的 `scale`——`fromTo` 写法能自愈，但若改成 `to` 写法，
  上一轮的 1.0 会让第二遍 punch 无事发生（四枚安静落地，"确认感"消失）。

## 复用指引
- props：仅 `hostSrc`；四条文案与编号在 `STEPS` 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/numbered-step-stack.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/numbered-step-stack/index.html。**换内容改 `.step-txt` 文案 + `.step-no` 编号**；
  加/减条数直接复制或删掉整个 `.step-bar`（时序是 `i * CONFIG.barStagger` 算的，**不用改任何 delay**），
  条数变了只需把 `hold` 按"每条 0.45s"重算。
  换强调色只改 `.step-no` 的 `background` 一处。换尺寸时 `barShift` / `settleLift` 按舞台宽等比。
  能量只调 `barStagger`（0.08 更急 / 0.14 更稳），**别动 punch 的缓动**。
- Remotion 移植：四枚各一个 `<Sequence from={Math.round(i * 0.11 * fps)} durationInFrames={rest}>`，
  条内 `interpolate(frame, [0, 7], [40, 0], {easing: Easing.out(Easing.cubic), extrapolateRight: "clamp"})`
  驱动 `translateX`，同一个局部时钟驱动 `opacity`。
  编号块 punch 在 `frame >= 7` 之后再走 4 帧：
  `interpolate(frame, [7, 11], [1.12, 1], {easing: Easing.out(Easing.quad), extrapolateLeft: "clamp", extrapolateRight: "clamp"})`
  （**两头 clamp 都不能省**——不 clamp 时 `frame < 7` 的帧会算出 >1.12 的 scale，编号块开场就是放大的）。
  整组收束放在外层容器上，`from = 3*11 + 7 + 4 + 2` 帧起走 6 帧到 `−4px`。
  **别用 `spring()` 做 punch**——spring 自带回弹，会踩上面那条坑。
- 剪辑软件对应物：剪映/CapCut——四条各做成一个"文本 + 色块"组合，
  用"位置 + 不透明度"关键帧从右进入，**逐条往后拖 3 帧（0.1s，剪映最小单位就是帧，正好均匀）**；
  编号块的 punch 用"缩放"两个关键帧（112% → 100%，4 帧）并把缓动设成"缓出"（**不要选"回弹"**）；
  整组收束在剪映里要把四条打成一个组合再打位置关键帧（没有组合功能就手动四条一起选中拖）。
  AE——四层横条 + 一个 Null 做父级：横条各自 `Position` + `Opacity` 关键帧，
  用 `Sequence Layers`（Keyframe Assistant）自动等间距排开（这正好保证错峰均匀）；
  编号块单独一层 `Scale` 两键 + `Easy Ease Out`；整组收束打在 Null 的 `Position` 上。
- 与本库同类卡的分工：**本卡 = 清单堆叠**（无线、并列、顺序可换、答"要做哪几件"）；
  `step-timeline-vertical` = 时间轴推进（有线、有因果、顺序不能颠倒、可标"当前在第几步"）；
  `chapter-progress-list` = 章节坐标（深底转场，答"讲到哪了"，唯一高亮）；
  `line-by-line-slide` = 逐行推句子（是字幕/段落，不是带编号的清单件）。
  一句话选卡：**顺序无关 → 本卡；顺序不能颠倒 → step-timeline-vertical；讲到哪了 → chapter-progress-list。**

## 动效范围
- 属于本卡的：四枚横条 `x +40 → 0` + `opacity` 的堆入（每枚 `0.24s power3.out`）；**错峰严格均匀 `0.11s × 4`** 这条纪律；编号块在该枚落定**同一帧** punch（`scale 1.12→1`、4 帧、`power2.out`、**无回弹**）这个"落地确认"；四枚都到位后**整组容器**上浮 `4px`（`0.20s`）的收束（"这是一组"）；四条**等重无高亮**（强调色只落在编号块）；用 1px hairline 而非投影立层级；`hold 1.8s` 给截图留时间。
- 不属于本卡的：demo 那四句具体步骤文案与 01~04 的编号写法、`#2fb344` 这个强调色（取参考图③绿系）、22px 字号与 600 字重、横条 66px 高 / 486px 宽 / `gap 14px` 的具体尺寸、编号块 64px 见方与 `12px 0 0 12px` 的圆角、`#e0e0e0` 边框色、列表落在右侧、左列的数字人占位、白底舞台。
- 迁移接口：内容入口是 `.step-bar` 的增删（时序自动按 `i × barStagger` 派生）；尺寸基准 `barShift 40px` / `settleLift 4px` 按舞台宽等比（960 ⇒ 1920 时翻倍）；颜色一个 token（编号块底色 = accent）+ 一个 hairline；时长缩放规则 —— `barStagger` 与 punch 的 4 帧是**手感常量，换尺寸换语速都不要动**，条数超过 5 时才把 `barStagger` 减到 0.08s，`hold` 按"每条 0.45s"重算；竖屏把横条改成占屏宽 88%、条数收到 3~4 条、`barShift` 改成屏宽的 8%。
- 底色要求：**白底即可**。深底也成立，换值：横条底改 `#272729`、边框改 `rgba(255,255,255,0.14)`、文字改 `#f5f5f7`，编号块的强调色不动（实色块在深底上照样立得住）。唯一约束是底不能有强纹理或渐变：四枚横条靠"等宽等高 + 1px 细边"读作一组，底上的花纹会让细边断续，四条就散成四个独立卡片。

<!-- ===== /file: video-talkcraft/references/cards/numbered-step-stack.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/orbit-drift.md ===== -->

---
name: orbit-drift
标题: 环绕微漂
优先级: P1
代码: template/cards/orbit-drift.tsx
一句话: 3D 空间里绕静态页面做小幅环绕——rotateY 与 rotateX 两条正弦相位错开 90°，合成一条闭合椭圆轨迹（幅度 ±6°/±3.4°），叠一层前后呼吸与反向跟随的投影，无始无终、整段都是 hold
适用: 静态页面要在屏上停留很久的段落（长讲述、逐条分析、边看边聊），需要一条"永不重复得太明显"的持续底噪；也用于让页面稳定地当背景道具，前面叠字幕/图表/数据
时长: 环绕一圈 = 实拍 9~14s（demo 压缩到 5.6s 一圈）；本卡没有入场也没有出场，随讲述长度无限续
能量: 低
类别: 运镜
输入: 图, 截图
语义: 氛围
素材形态: 无
位置: 任意
props: hostSrc(未使用)
---

## 意图
本卡是"镜头呼吸"的高级版，专门解决一个具体问题：**页面要在屏上待很久**。
[slow-push-in](slow-push-in.md) 的推镜是单向的，推 30s 就推到糊了；
[tilt-3d-page](tilt-3d-page.md) 的立面 hold 慢漂是单向的，漂久了会漂到边界。
环绕是唯一**可以无限持续**的运镜——轨迹闭合，永远回到原点，但每一帧都在动。
做对的命门：**幅度必须小**（rotY ≤7°、rotX ≤4°；大了就变成 3D 旋转秀，正文读不了）、
**相位差必须是 90°**（0 或 180° 会退化成一条斜线，读作"摆动"而不是"环绕"）、
**长时段要让椭圆缓慢进动**（两轴同周期时轨迹严格闭合，超过 2 圈观众会认出重复的轨道、读作机械转台）。

## 动效核心
- 结构三层：`.world`（`perspective: 900px`——比 [tilt-3d-page](tilt-3d-page.md) 更近一点，环绕的位移差才读得出来）→ `.camera`（相机层，`preserve-3d`）→ `.shadow` 投影层 + `.page` 页面层
- 姿态 = 基准姿态 + 两条正弦：
  - `rotateY = baseRotY + ampRotY · sin(2π·t/orbit)`
  - `rotateX = baseRotX + ampRotX · sin(2π·(t/(orbit·ratio) + 0.25))` ← **0.25 = 90° 相位差，是"环绕"的唯一来源**
  - `z = ampZ · sin(2π·(t/orbit + 0.6))`（前后微呼吸，相位与两轴都错开，读作第三层独立的"活"）
- 为什么 90° 相位差 = 环绕：`sin` 走到极值时另一轴正好过零 ⇒ 两轴的合成轨迹是**椭圆**；
  相位差为 0 时两轴同步到达极值 ⇒ 轨迹退化成一条**斜线**，那是"摆动"（来回晃），不是"绕着走"
- 基准姿态（`baseRotY: -8°`、`baseRotX: 2.5°`）：环绕是绕着这个姿态漂，不是绕正视位。
  `0/0` 也完全成立（正视位微漂，更隐形），给一点基准更像"摆在空间里的一张页"
- 投影**反向**跟随：页面向左倾（`sin` 为负）时影子往右挪 `shadowShift`，浓度随 `z` 微变——光源不动、物体在绕，影子必须反着走
- 实现是**单条 tween 驱动一个时间标量** + `onUpdate` 里算三条正弦，整段一个连续曲线：没有段落、没有起止、没有 hold 之外的任何东西
- **周期策略（本卡最关键的落地决定）**：
  - 短用（≤2 圈，或需要无缝循环如画廊小窗）：**三轴同周期**，轨迹严格闭合，每 `orbit` 秒严丝合缝回到起点，循环无跳帧（demo 用这个）
  - 长用（>2 圈，实拍讲述 30s+）：把 `periodXRatio` 设成 **0.75~0.8**（如 9s / 6.8s），两轴周期不可通约 ⇒ 椭圆缓慢**进动**，轨迹永不重复，观众认不出轨道
- 文字可读性：环绕幅度小，正文全程可读；但如果配了 `baseRotY` 基准姿态，可读性按**基准 + 幅度**的最坏姿态验收（本卡最坏是 -14.2°，仍在 25° 安全区内）

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `orbit` | 实拍 9~14s / demo 5.6s | 环绕一圈的时长。<5s 读作"页面在晃"（观众会晕）；>16s 幅度感被稀释、接近静止；越长越"高级" |
| `ampRotY` | 6.2°（范围 3~7） | 横向环绕幅度。<2° 读不出在动；>8° 页面左右边缘透视差过大、远端文字变形，变成 3D 旋转秀 |
| `ampRotX` | 3.4°（约取 `ampRotY` 的一半） | 纵向幅度。取一半让椭圆更宽更自然；两轴等幅会读作正圆环绕（更"演示"更不自然） |
| `phaseX` | 0.25（= 90°） | **不要改**。这是"环绕"与"摆动"的唯一分界；0 或 0.5 会退化成一条斜线 |
| `periodXRatio` | 1.0（短用）/ 0.75~0.8（长用） | 两轴周期比。1.0 = 轨迹严格闭合、可无缝循环；0.75~0.8 = 椭圆缓慢进动、长时段不重复。**这是短用/长用的开关** |
| `baseRotY` / `baseRotX` | -8° / 2.5° | 基准姿态。`0/0` 也成立（正视位微漂，更隐形）；给基准后可读性按"基准+幅度"的最坏姿态验收 |
| `ampZ` | 22px | 前后微呼吸。0 = 只转不进退（弱一档）；>50px 明显读作在推拉，抢了环绕 |
| `perspective`（父容器） | 900px（范围 800~1100） | 环绕专用较近透视。>1400px 环绕的位移差看不出来（等于白做）；<600px 鱼眼变形 |
| `shadowShift` | 20px | 投影反向跟随量。0 = 页面读作贴纸；>45px 影子的动比页面还明显，本末倒置 |

## 已知坑
- 相位差给成 0（或 180°）——两轴同步到达极值，合成轨迹退化成一条**斜线**，读作"页面在斜着来回摆"。环绕的全部技术含量就在这个 90°。
- 幅度给到 10° 以上——不再是"微漂"，页面左右边缘透视差过大、远端文字变形，本卡的定位（隐形底噪）彻底改变，成了 [tilt-3d-page](tilt-3d-page.md) 的劣化版。
- 长时段（30s+）用两轴同周期——轨迹严格闭合、每圈完全重复，观众在第三圈就认出了轨道，读作电动转台在匀速转。长用必须让椭圆进动（`periodXRatio` 0.75~0.8）。
- 反过来：需要无缝循环的场合（画廊小窗、循环 loop 素材）用了不可通约周期——循环点会跳帧。短用要同周期。
- 环绕周期太短（<5s 一圈）——读作页面在晃，观众会晕；这不是"更明显"，是做坏了。要更明显应该加幅度（在 7° 上限内），不是提速。
- `perspective` 给到 1400px 以上——透视太弱，±6° 的环绕几乎看不出位移，动效等于白做。环绕比立面卡更需要近透视。
- 投影不跟随或同向跟随——同向跟随尤其糟（影子和页面往同一边挪，物理上不可能），读作贴纸或穿模。必须反向。
- 忘了 `transform-style: preserve-3d`——`translateZ` 失效，投影拍平、`ampZ` 呼吸也没了。
- 用 `Math.random()` 加噪声让它"更自然"——本库不做定格抖动/沸腾（用户定版）；且 Remotion 里随机数会破坏 seek 一致性。自然感来自三条不同相位的正弦叠加，不是噪声。
- 拿本卡当入场——它没有入场也没有出场。素材的入场交给 media-pop-in，姿态的建立交给 [tilt-3d-page](tilt-3d-page.md)（可以先立面、再挂本卡当 hold 底噪，两卡串联是推荐组合）。

## 复用指引
- props：仅 `hostSrc`（声明未使用）；页面素材为 JSX 写死的 `.page` DOM，换素材需改源码。
- Remotion/tsx（skill 首选）：template/cards/orbit-drift.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：`demos/orbit-drift/index.html`。换素材改 `.page` 内整块 DOM（或换成铺满的 `<img>`）；轨迹全在顶部 `CONFIG`（`orbit` / `baseRotY` / `baseRotX` / `ampRotY` / `ampRotX` / `phaseX` / `ampZ` / `phaseZ` / `shadowShift` / `cycles` / `periodXRatio`）；透视改 `.world` 的 `perspective`。核心可摘走：`CONFIG` + `apply()` 那七行三角函数 + 驱动它的单条 tween。**长用改一个数**：`periodXRatio: 0.78`。
- Remotion 移植：本卡是**最适合 Remotion 的一张**——纯 `frame` 的函数，天然 seek-safe、零状态：`const t = frame / fps;` 然后 `const ry = baseRotY + ampRotY * Math.sin(2*Math.PI * t/orbit);`、`const rx = baseRotX + ampRotX * Math.sin(2*Math.PI * (t/(orbit*ratio) + 0.25));`、`const z = ampZ * Math.sin(2*Math.PI * (t/orbit + 0.6));`——**不需要 interpolate**。套在外层 `perspective: 900` + 相机层 `transformStyle: 'preserve-3d'` + `transform: \`rotateY(${ry}deg) rotateX(${rx}deg) translateZ(${z}px)\``；投影层 `transform: \`translateZ(-40px) translate(${-sy*20}px, ${sx*10}px)\``。这套写法直接就是全局系统 G3 的 idle 微动的 3D 版（见 `template/motion-systems/`），可以整段并入 CameraRig 当 hold 期底噪。
- 剪辑软件对应物：AE——3D 图层的 `Y Rotation` / `X Rotation` 各挂表达式 `value + 6.2*Math.sin(time*2*Math.PI/9)` 和 `value + 3.4*Math.sin(time*2*Math.PI/6.8 + Math.PI/2)`（**注意第二条里的 `+ Math.PI/2` 就是那个 90° 相位差**），`Position` 的 Z 挂第三条；这是 AE 里做"idle 呼吸"的标准表达式写法，比打关键帧准确得多。剪映/CapCut——没有表达式，只能用"3D 旋转"打若干关键帧手动近似一个椭圆（4~6 个关键帧一圈，设成缓入缓出），或直接用"轻微晃动"类预设（幅度通常偏大，需调小）。Premiere——`Basic 3D` 的 `Swivel`/`Tilt` 打关键帧同法，或用表达式（PR 表达式能力弱于 AE）。

## 动效范围
- 属于本卡的：**两轴正弦相位错开 90° 合成的椭圆环绕轨迹**（`rotateY` ±3~7° / `rotateX` ±2~4°，`phaseX = 0.25` 是"环绕 vs 摆动"的技术分界）；叠加的第三层前后微呼吸 `z`（相位与两轴都错开）；**投影反向跟随**（页面倾向一侧、影子挪向另一侧，浓度随 `z` 微变）；三层结构（父容器 `perspective` 800~1100px 的**近透视**要求 / 相机层 `preserve-3d` / 投影层 `translateZ`）；"整段都是 hold、无入场无出场、可无限续"这一定位；**周期策略**——短用/需无缝循环时三轴同周期（轨迹严格闭合），长用（>2 圈）时 `periodXRatio` 0.75~0.8 让椭圆进动以免被认出轨道；"自然感来自多相位正弦叠加、不靠随机噪声"这条纪律（本库不做沸腾/定格抖动）。
- 不属于本卡的：demo 里的灰阶线框应用界面（侧栏 / 顶栏 / 卡片列表 / 详情面板及其全部文案与数值）、基准姿态 `-8°/2.5°` 这一具体取值（`0/0` 同样成立）、投影的模糊半径与浓度、素材入场动画、页面上叠加的字幕或图表。
- 迁移接口：`orbit` 定一圈时长（实拍 9~14s，越长越高级）；`ampRotY/ampRotX` 定幅度（上限 7°/4°，可读性按"基准+幅度"的最坏姿态验收）；`phaseX` **锁死 0.25**；`periodXRatio` 是短用/长用的唯一开关；`ampZ`/`shadowShift` 按画幅等比缩放（本卡按 960 宽 / 700px 页宽设计）；`perspective` 按画幅等比缩放但要保持"较近"。与 [tilt-3d-page](tilt-3d-page.md) 串联使用时：立面卡负责建立姿态，本卡的 `baseRotY/baseRotX` 接立面卡的终点姿态即可无缝交接。
- 底色要求：白底即可——本卡零颜色、零装饰，只是三条正弦驱动的 transform。深色素材同样成立，仅投影需换成亮边（同 [tilt-3d-page](tilt-3d-page.md)）。

<!-- ===== /file: video-talkcraft/references/cards/orbit-drift.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/outline-box-title.md ===== -->

---
name: outline-box-title
标题: 描边框标题
一句话: 圆角描边框沿路径**一笔画完一圈**（0.42s 近匀速，精确闭合不过头），框闭合后实心 chip 从左 scaleX 展开 0.2s、chip 内白字滞后淡入，最后三枚 chevron 依次点亮
适用: 口播里"我的核心观点是…"这类**给结论加框**的时刻——立论点、下定义、把一个短语标成术语；理性、条理、有条款感的调性（行业分析、产品讲解、教程）；不适合情绪爆点与手绘调性的片子
时长: 起手静置 0.4s → 框画一圈 0.42s → chip 展开 0.2s（内字滞后 0.1s）→ chevron ×3 错峰 0.08s → 收尾 hold 1.6s；共约 3.0s
能量: 中
类别: 字幕花字
输入: 文, 人(可选)
语义: 定义, 标题
素材形态: 无
位置: 任意
props: hostSrc
优先级: P1
代码: template/cards/outline-box-title.tsx
---

## 意图
口播讲到"核心观点"时，观众需要一个**明确的容器**——不是强调某个词，而是宣布
"接下来这几个字是本段的结论"。描边框给的就是这个容器感。

本卡的全部气质取决于一件事：**框是机器画的**。
`hand-drawn-ellipse`（手绘圈）和本卡在视觉上都是"一条线围住一个短语"，
但语义相反——手绘圈是**人在纸上圈重点**（过头交叉、粗细变化、笔触），
描边框是**系统在界面里框选**（近匀速、精确闭合、圆角统一、粗细恒定）。
两者混用（比如给描边框加过头的尾巴）会让整片的气质变得暧昧：既不像手作也不像界面。

第二层设计是**框 → chip 的反色对句**：前半句"核心观点"在**空框**里（轻、是容器），
后半句"在这里"在**实心 chip** 上（重、是落点）。同一个强调色的两种用法把
"观点 → 位置"这个句子结构直接画了出来。

命门三条：
① **框必须 `power2.inOut` 近匀速、精确闭合**。用 `power3.out`（起手快尾段慢）
会读作"手甩出来的一圈"，语言就串味了。
② **框闭合了才放 chip**。同时进读作两个色块一起飘进来，"框选完成 → 给出位置"
这个推进感丢掉。
③ **chevron 从 0.25 亮到 1，不是从 0 淡入**。它们的语义是"本来就在那儿的方向提示，
被依次点亮"；从 0 出现读作三个装饰飘进来。

## 动效核心
- **结构**（@960×540 舞台）：第一行 356×104 的容器，内含 56px/700 的墨字 +
  一个同尺寸的 SVG 圆角矩形描边框（4px 描边，唯一强调色，圆角 14px）；
  第二行 260×66 的实心 chip（`border-radius: 12`，小件圆角档）+ 40px/700 白字；
  下方三枚 26×34 的 chevron（`>` 折线，5px 描边 `round` 端头）
- **① 框选**：SVG path 从**上边中偏左**（`M 34 2`）起，顺时针 H → 圆角 → V → 圆角 →
  H → 圆角 → V → 圆角 → `Z` 精确闭合；`stroke-dasharray = len`、
  `stroke-dashoffset len→0`，`0.42s power2.inOut`。
  起点特意不在角上——从角起笔读作"两条边同时长出来"，从边中间起笔才读作"一笔绕一圈"
- **② chip 展开**：`transform-origin: left center`，`scaleX 0→1`，`0.2s power3.out`，
  起步 = 框闭合 + `0.04s`（几乎接上，不留空拍）；
  chip 内白字 `opacity 0→1`（`0.16s`），滞后 chip `0.1s`——
  chip 是独立的背景层（`.ob-chip-bg`），字不参与 scaleX（否则字会被横向拉扁）
- **③ chevron 点亮**：`opacity 0.25→1` + `x +4→0`，各 `0.16s power2.out`，错峰 `0.08s`；
  起步 = chip 落定 + `0.06s`
- **④ hold 1.6s**：全部静置。不做 line boil / 定格抖动（design-language §4）
- **层级**：白底 → 主持人（右侧列，演示语境）→ 文字 → 描边框 SVG / chip → chevron

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `boxDur` | 0.42s | 框画一圈；<0.25s 读作"框闪出来"（画的过程看不见，等于硬现），>0.7s 观众看着线爬，口播已经念到下一句 |
| 框的缓动 | `power2.inOut` | **本卡第一命门**；换成 `power3.out` 立刻读作手甩的一圈（手绘语言），换成 `linear` 也可以（更机器），但 `back` / `elastic` 一律禁止 |
| 起笔点 | 上边中偏左（`M 34 2`） | 从角起笔读作"两条边长出来"，从边中间起笔才是"一笔绕一圈"；起笔点越靠角，机器感越弱 |
| 描边宽 | 4px @540 舞台高 | 细于 2.5px 压缩后掉边；粗于 6px 框比字重，容器抢了内容 |
| 框圆角 | 14px | 0（直角）读作表格单元格；>24px 成了 pill（那是按钮语义，不是框选） |
| `chipGap` | 0.04s | **框闭合到 chip 起步的间隔，本卡第二命门**；0 也可（接得更紧），但**不许为负**（chip 在框闭合前出来就是两个动效撞车），>0.3s 中间一个明显空拍 |
| `chipDur` | 0.2s | chip 展开；<0.12s 读作硬现，>0.35s 和框的 0.42s 一样长，两拍变成一拍 |
| `chipTxtLag` | 0.1s | chip 内字的滞后；0 = 字跟着 chip 一起被"刷"出来（层次塌成一件事），>0.25s 读作 chip 空着等字 |
| `chevDim` | 0.25 | **chevron 起始不透明度，本卡第三命门**；0 读作三个装饰飘进来，>0.45 点亮的对比不够（看不出"依次"） |
| `chevStagger` | 0.08s | chevron 错峰；<0.05s 三枚几乎同时（读作一个整体），>0.15s 读作三个独立动效在排队 |
| `hold` | 1.6s | 收尾停留，按框内 + chip 的总字数给（每字约 0.2s） |

## 已知坑
- 框用 `power3.out` 或 `back.out` 画出——一眼读作手甩的一圈，"机器框选"这层语义全丢，和 `hand-drawn-ellipse` 撞语言。
- 框画过头（尾巴超出起点）——那是手绘圈的做法；描边框过头一点点就显得"没对准"，不是手作感。
- 从角落起笔——观众看到的是"两条边同时长出来"，读不出"一笔绕一圈"。
- 框和 chip 同时进——两个色块一起飘进来，"框选完成 → 给出位置"的推进感消失，整组读作一张 PNG。
- chip 内的字跟着 chip 一起 `scaleX`——字被横向拉扁，慢放下非常明显；字必须是 chip 背景层之上的独立层。
- chip 不加 `overflow: hidden`（或字不做独立层）——展开到一半时字已经露在 chip 之外，读作"字先到、块后追"。
- chevron 从 `opacity 0` 淡入——读作三个装饰飘进来；它们的语义是"本来在那儿被点亮"。
- chevron 错峰超 0.15s——读作三个独立动效在排队，"扫过点亮"这一件事被拆成三件。
- 框用一个颜色、chip 用另一个颜色——同屏第二个"看这里"色（design-language §1 红线）；框 / chip / chevron 必须共用唯一强调色，靠"空框 vs 实心"制造对比。
- 框的圆角和 chip 的圆角不一档——同屏混用两种圆角语法（design-language §6 Don't）；框 14 / chip 12 属于同一档（小件），差 2px 是尺寸差不是语法差。
- hold 期给框加呼吸/漂移——机器画的框动起来就成了"没对准"。

## 复用指引
- props：仅 `hostSrc`；文案「核心观点 / 在这里」在 JSX 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/outline-box-title.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/outline-box-title/index.html。换文案改 `.ob-row1 .txt` 与 `.ob-chip-txt`，
  **同时**要改 `.ob-row1` / `#obBox` 的 `width` 与 `#obBoxPath` 的 `d`（框是写死尺寸的
  path，不会跟着文字自适应——这是有意的：框的尺寸是排版决定，不该由文字宽度抖出来），
  chip 宽度改 `.ob-row2` 的 `width`；改强调色只动 `:root --acc`（框 + chip + chevron 共用）；
  节奏全在 `CONFIG`（`boxDur`/`chipGap`/`chipDur`/`chipTxtLag`/`chevDim`/`chevStagger`/`hold`）。
  换框尺寸时 `d` 的写法：`M {r+20} 2 H {w-r} A {r} {r} 0 0 1 {w-2} {r+2} V {h-r} … Z`（`r` = 圆角）。
- Remotion 移植：`strokeDasharray={len}` + `strokeDashoffset={interpolate(f, [0, 13], [len, 0],
  {easing: Easing.inOut(Easing.quad), extrapolateRight: "clamp"})}`——`len` 必须**预先量好写成常量**
  （SSR 里没有 `getTotalLength()`；用浏览器量一次，或按周长公式 `2(w+h) - 8r + 2πr` 估）。
  chip 用 `scaleX` + `transformOrigin: "left center"`；chip 内字单独一个 `interpolate` 的 opacity。
  chevron 三枚用 `f - i*2` 局部时钟。帧换算 @30fps：`boxDur 0.42s ⇒ 13f`、`chipDur 0.2s ⇒ 6f`、
  `chipTxtLag 0.1s ⇒ 3f`、`chevStagger 0.08s ⇒ 2~3f`。
- 剪辑软件对应物：AE——Shape Layer 画圆角矩形（只描边不填充）+ `Trim Paths`，
  `End` 从 0→100%，**`Offset` 设成让起点落在上边中间**，缓动用 `Easy Ease` 两端
  （F9 就很接近 `power2.inOut`）；chip 用 Shape Layer + `Scale` 的 X 分量 0→100%
  并把锚点移到左边缘。剪映/CapCut——"边框"贴纸只能整体淡入/缩放，**画不出"沿路径画一圈"**，
  折中方案是给边框贴纸做"线性擦除"两次（先横向再纵向）或直接接受"整框淡入"
  （损失本卡的第一命门，此时它退化成普通的框标题）；chip 用色块 + "向右展开"入场。
- 与本库同类卡的分工：`corner-bracket-frame` = 只画对角两个角（取景/引述，不闭合，能量更低）；
  `hand-drawn-ellipse`（B 组）= 手绘椭圆圈重点（过头交叉、笔触，人在圈）；
  `info-term-card` = 术语卡整块出现；`quote-card` = 引述整段；
  `chapter-title-card` = 章节级的整屏标题；
  **本卡 = 机器画的"框选一个短语" + 反色 chip 给出落点**（界面感、条款感的一档）。

## 动效范围
- 属于本卡的：描边框沿路径 `dashoffset` 画出一圈、`power2.inOut` 近匀速、**精确闭合不过头**、起笔点在边中间不在角上，这四条合起来构成"机器画的框选"这个语言（本卡的核心资产）；框闭合**之后**（`chipGap ≥ 0`）chip 才 `scaleX 0→1` 展开（origin left）这个先后关系；chip 内字滞后 chip `0.1s` 淡入且**不参与 scaleX**；chevron 从 `0.25` 点亮到 `1` + `x+4→0`、错峰 `0.08s` 的"依次扫过"；"空框（容器）+ 实心 chip（落点）"用同一个强调色做反色对句这个层级关系；hold 期全部静置。
- 不属于本卡的：demo 那句「核心观点 / 在这里」的具体文案、56px 与 40px 的字号、紫色 `#7A5AF8` 这个具体取值、356×104 与 260×66 的框 / chip 绝对尺寸、chevron 的具体形状（`>` 折线也可换成三角、箭头）与枚数（2~4 枚都成立）、右侧主持人（数字人）占位、整组落在左侧留白区这个构图。
- 迁移接口：强调色一个变量 `--acc`（框 + chip + chevron 共用，同屏不允许第二个）；框尺寸 = 文字宽 + 左右各 30px 气口，`#obBoxPath` 的 `d` 跟着重写（公式见「复用指引」），圆角取 12~16px、描边宽取舞台高的 0.7%；chip 宽 = 文字宽 + 左右各 26px；节奏在 `CONFIG`，能量档只调 `boxDur`（框画得越慢越"郑重"），`chipGap`/`chipTxtLag`/`chevDim` 是**手感常量**，换尺寸换语速都不要动；`hold` 按总字数给（每字约 0.2s）。竖屏把整组放在上三分之一、框宽取画幅 80%，chevron 可以减到两枚。
- 底色要求：白底即可。深底成立（框 / chip / chevron 换深底模式强调色 `#2997ff`，第一行字反白，chip 内字仍为白——此时 chip 与底的对比靠强调色本身的亮度）。唯一约束是**底不能有高频细节**：4px 的描边框在花底上会被吃掉，那种场合先垫一层浅底板，别靠加粗描边解决（加粗会让框比字重）。

<!-- ===== /file: video-talkcraft/references/cards/outline-box-title.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/overexpose-flip-transition.md ===== -->

---
name: overexpose-flip-transition
标题: 过曝翻页转场
一句话: 出场相机推向证据物直到 1.5x 占满画面，同帧一层重音（深底=白色径向过曝／白底=全场压暗）以切点为锚冲顶再回落，入场镜头从那个亮心里被拉出来
适用: 章节翻页、"讲完这一段进入下一段"的语义断点；也用在推进到一张关键截图/图表之后跳走的时刻。调性偏郑重，一片 2~4 次
时长: 出场推 0.55s → 交叠 0.40s（≈12 帧 @30fps）→ 入场沉降 0.55s；重音包络切前 0.26s 升、切后 0.42s 落
能量: 高
类别: 转场结构
输入: 场
语义: 转场, 章节
素材形态: 无
位置: 中段
props: hostSrc(未使用)
优先级: P0
代码: template/cards/overexpose-flip-transition.tsx
---

## 意图
[[push-through-transition]] 是无重音的基准式，读作"我穿过去了"；过曝翻页在同一条 scale 轴上**加一层曝光重音**，
读作"这一页翻完了"。它比推穿更重，因为闪光是听觉重音的视觉对位——通常压在一句话的句末重音或音乐落点上。

做对的命门：① **重音包络必须以切点为锚**——切前升、切后落，不对称；把它写成一个居中的对称 tween，
峰值会被回落段截断，白底上 3% 的压暗等于没有重音（实测踩过）；② **过曝不是白闪**——峰值 0.42~0.55，
要能隐约看见内容；冲到 1.0 就变成另一张卡（纯白闪转场）；③ **重音层极性随底色换**——白底上白色叠加会被
完全吞掉，必须改成压暗一拍。这是六式里唯一与底色耦合的一式。

## 动效核心
时间结构（`cut = at + 0.55 − 0.10`，参数全在 `CONFIG.blow`）：

| 阶段 | 时刻 | 出场镜头 | 重音层 | 入场镜头 |
|---|---|---|---|---|
| 推进证据物 | `at` → `at+0.55` | `scale 1.0→1.50` + `blur 0→4px`，`power2.in` | — | 停在 `scale 1.30` + `blur 6px` |
| 重音升段 | `cut−0.26` → `cut` | 继续推 | `opacity 0→peak`，`power2.in` | — |
| 切点 | `cut` | 开始 0.40s 淡出 | 峰值 | 开始 0.40s 淡入 |
| 重音落段 | `cut` → `cut+0.42` | — | `opacity peak→0`，`power2.out` | 沉降中 |
| 沉降 | `cut` → `cut+0.55` | — | — | `scale 1.30→1.03` + `blur→0`，`power2.out` |

- **推到 1.5x 而不是 1.35x**：这是"推进证据物直到它占满画面"的量——出场镜头的主体被推到出画，
  观众的注意力被交到一个纯亮/纯暗的场，再从那里被拉进新镜头。失焦反而比推穿轻（4px 而非 7px），
  因为亮心要看得清；糊过头会读作单纯的溶解。
- **不对称包络的实现**：两条独立 tween，一条从 `cut − rise` 到 `cut` 升到峰值，一条从 `cut` 起回落。
  写成一条 `yoyo` 或居中 keyframes 都会让峰值达不到设定值。
- **入场从 1.30 起步**：比推穿的 1.16 更高，因为亮心散去时观众正在"被拉出来"，路程要更长才读得出拉出感。
- **`.flash` 是径向而不是均匀铺满**：`radial-gradient(ellipse at 50% 46%, …)` 让重音有中心，
  46% 是视觉重心（略高于几何中心）；均匀铺满读作调亮度而不是过曝。

Remotion 对应写法（`template/motion-systems/transitions.tsx`）：

- 出场 shot：`{ tail: 12, path: [{t:0, scale:1.06}, ...blowoutOut(tEnd)] }`——`blowoutOut` 就是 `pushThroughOut(to:1.5, blur:4, dur:0.9)`
- 入场 shot：`{ lead: 12, path: [...settleIn(leadSec, {from:1.3}), {t:9, scale:1.0}] }`
- 叠加层（出场侧放，`at` = 叙事末尾秒；或入场侧放、`at` 取负落在 lead 里）：`<Overexpose at={tEnd} peak={0.55} riseF={10} fallF={10} color="255, 250, 240" />`
- `Overexpose` 的 `riseF/fallF` 是帧数，内部就是上面那条不对称包络（`df<=0` 走 `Easing.in`、`df>0` 走 `Easing.out`）。
- 闪光统一走 `template/motion-systems/transitions.tsx` 的 `<Overexpose>`，别在场景里散落；`env.tsx` 的 `TRANSITION_FLASHES` 表按 cinematography.md §2 留空不用（默认关）。

## 参数表
| 参数 | 典型值 | 调节手感 |
|---|---|---|
| 出场推到多大 `outScale` | 1.50 | <1.35 与推穿无区别、重音显得无理由；>1.7 主体早已出画，剩下几帧是空推 |
| 重音峰值 `peak` | 深底 0.42~0.55 / 白底 0.10 | 到 1.0 就是纯白闪转场（另一张卡）；深底 <0.3 或白底 <0.06 读作"闪了一下但没意义" |
| 升段 `rise` | 0.26s（≈8 帧） | <0.15s 读作爆闪/故障；>0.4s 观众提前知道要换场，惊喜没了 |
| 落段 `fall` | 0.42s（≈13 帧） | 必须比升段长（升快落慢才像曝光恢复）；等长读作机械闪烁 |
| 交叠帧数 `overlap` | 0.40s ≈ 12 帧 | 比推穿略短：重音已经盖住了边界，交叠可以更省 |
| 入场起手景别 `inScale` | 1.30 | =1.16 读作推穿+闪光；>1.45 拉出路程过长，落位拖沓 |
| 出场失焦 `outBlur` | 4px | 比推穿的 7px 轻——亮心要看得清；>8px 读作溶解 |

## 已知坑
- 重音包络居中写（对称 tween 或 `yoyo:true`）：升段被落段截断，峰值远达不到设定值，白底上等于没做。
- 白底工程照抄白色过曝层：叠加层被底色完全吞掉，转场重音消失。白底必须换成压暗一拍。
- 峰值冲到 1.0：变成纯白闪转场——那是另一种语法（零内容帧），不该混在本卡里。
- 闪光和切点错位：闪光峰值在切点后才到，观众先看到新画面再看到闪光，读作 bug。
- 只加闪光不加推进：静止画面上闪一下 = 相机闪光灯，没有动量交接，退化成硬切 + 特效。
- 一片里过曝翻页用了七八次：曝光重音会通胀，最后每次都不重要。2~4 次为上限。

## 复用指引
- props：仅 `hostSrc`（声明未使用）；两个镜头为 JSX 写死的 tile，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/overexpose-flip-transition.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：`demos/overexpose-flip-transition/index.html`。摘 `blowout(出场镜头, 入场镜头, 起始秒) → 结束秒`
  一个函数 + `CONFIG.blow` 一组参数 + `.flash` 那段 CSS；`hold()` 一起摘（转场两端要有慢推）。
  **白底工程直接用**；深底工程把 `.flash` 的 `radial-gradient` 底色换成白色、`peak` 提到 0.42~0.55，包络和时序都不动。
- Remotion：`blowoutOut` + `settleIn(…, {from:1.3})` + `<Overexpose>`（三者都在 `template/motion-systems/transitions.tsx`）。
- 家族关系：去掉重音层 = [[push-through-transition]]；把重音换成"零内容的纯白帧" = 白闪转场（另一语法）；
  重音 + 硬切 + 零交叠 = [[black-slam-transition]]。同一边界只用一式。
- 帧级压缩版（实测，小Lin说·韩股崩盘）：**白闪 + 运动模糊斜扫**——一层白色叠加冲到高位，同帧画面沿斜向拖模糊，
  白闪落下时已换场，全程 0.1~0.2s。注意本卡"重音层随底色换极性"的定版约束同样适用。
- 剪辑软件对应物：剪映"闪白/曝光转场"；AE 是 Exposure 关键帧 + 两侧 camera Z 位移；
  达芬奇用 Flash 转场但要手动把包络改成不对称。

## 动效范围
- 属于本卡的：出场 `scale 1.0→1.50` + `blur 0→4px` 的 `power2.in` 推进；入场 `scale 1.30→1.03` + `blur 6→0` 的
  `power2.out` 拉出；**重音层的不对称包络**（切前 0.26s `power2.in` 升到峰值、切后 0.42s `power2.out` 回落，锚点是切点而非中点）；
  交叠 0.40s（≈12 帧）交叉淡化与相机曲线分离；重音层为径向（中心 50% 46%）而非均匀铺满；
  hold 期相机永不静止的慢推。
- 不属于本卡的：两个镜头里的文字与配色（白/浅灰 tile + 灰字式名是"认式子的标签"，不是台词字幕）、
  左上说明角标、**重音是亮还是暗**（随底色定，见迁移接口）、`.shot` 的 `inset:-14%` 具体数值。
- 迁移接口：时序全在 `CONFIG.blow`（`out`/`overlap`/`settle`/`cutLead` + `peak`/`rise`/`fall`）；
  **重音层极性随底色切换**——`peak` 是峰值强度，`.flash` 的底色决定压暗还是过曝：白底用暗压 6~10%（demo 值 0.10），
  深底换回白色径向过曝 0.42~0.55（过曝要能隐约看见内容，到 1.0 就是另一张卡）；换尺寸不用改（只有 scale 轴 + 全屏叠加层）；
  `blur` 按输出分辨率线性缩放。
- 底色要求：白底可跑，**但重音层必须换极性**。实测教训：白色过曝叠加层在白底上会被完全吞掉，转场重音消失——
  所以 demo 改成了全场压暗一拍（峰值 0.10 实测可见）。深色工程反过来用白色过曝。这是六式里唯一与底色耦合的一式。

<!-- ===== /file: video-talkcraft/references/cards/overexpose-flip-transition.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/parallel-items-with-host.md ===== -->

---
name: parallel-items-with-host
标题: 并列句排版（人物在场）
一句话: 口播讲"A、B、C"三件并列的事而人还在画面里时，三项按口播逐个弹出（0.6s 一项）、标签压图且大，七种版式一卡切换——头顶横排 / 三横条灰转彩 / 竖列虚化底 / 顶部卡堆 / 竖切三分 / 斜切三分 / 背景轮换大字
适用: 任何"三件事 / 三个地方 / 三步 / 三种"的并列句，且人物出镜（抠像或原片）；知识、生活、旅行、效率类口播最高频的一种镜头
时长: 一式 3.1s（起手 0.4 → 三项 0.4 / 1.0 / 1.6s 逐个入场、单项 0.45 → 第三项 2.05s 落定 → 2.70s 起三项退场 0.35，实际 hold ≈0.65s）；demo 七式巡演 21.7s；成片一镜只用一式，拉长 `per` 即拉长 hold
能量: 中
类别: 人物互动
输入: 人(必需), 图
语义: 步骤, 例证, 列举
素材形态: 人脸, 透明通道, 多图
位置: 任意
props: layout, items, srcs, hostSrc
优先级: P0
代码: template/cards/parallel-items-with-host.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| **必需**（抠像全身 / 原片裁小框 / 圆头像 / 虚化成底，形态随版式变） | tsx 不直接支持（`srcs` 仅走 `<Img>`）；全屏切分类四式（② ⑤ ⑥ ⑦）的带 / 条 / 背景把 `<Img>` 换成 `<OffthreadVideo>` 后可放视频 | 全部可（三项素材的默认输入，经 `srcs`） |

小卡类三式（① ③ ④）的卡只有 200~340px 宽，放视频看不清，用图。人物用 `hostSrc` 注入 alpha 视频（`references/host-footage.md`）。

## 常用场景
1. 最通用的"三件事"：周末三件事、三个习惯、三个原因 —— ① 头顶横排卡
2. 三项都有好看大图（三种旅行、三座城市）、信息量大于人物 —— ② 三横条灰转彩 / ⑤ 竖切三分
3. 三个步骤 / 三款工具 / 清单（图换成 icon chip 也成立） —— ③ 竖列虚化底
4. 有先后的三步（拍 → 剪 → 发）、递进、一叠证据 —— ④ 顶部卡堆翻切
5. 能量高的并列（三种玩法 / 三个阵营） —— ⑥ 斜切三分
6. 每项都值一张大图、且不需要三项对照 —— ⑦ 背景轮换 + 大字（顺序讲、不同屏）

## 意图
口播里"第一…第二…第三…"是最高频的句式，人还站在画面里，三项素材往哪摆是每条片都要回答的问题。
抖音口播剪辑圈把这件事做成了"抄作业"级的套路（@剪辑李一手《新手剪辑并列句不会排版？直接抄作业》、@剪Bingo子《口播剪辑中并列句排版方式喂给你》，2026-09-05 逐帧读出、去重、改横屏后留七式）。
七式表面差得很远，底下是同一套纪律，做对三条就成立：
1. **人物永远在场**，但形态随版式变：全身站底（① ⑤ ⑦）/ 缩成小框（② ③ ④）/ 圆头像（⑥）/ 虚化铺底再补一个小框证明"我还在"（③）。人一消失，口播就成了配音 PPT。
2. **三项按口播逐个出现**（0.6s 一项、每项一次入场）。三张一起淡入观众读不出"第一第二第三"；间隔 >1s 又散成三张卡。灰转彩 / 背景轮换是同一节奏的两种做法。
3. **标签压在图上且大**：960 舞台 26px（≈1080p 52px），全屏切分类 36~40px，大字版 84px。小了等于没有（layout.md §5 条目 ≥40）。

## 动效核心
- 一式 = 一镜：`lead 0.4s`（人物先站住一拍）→ 三项在 `0.4 / 1.0 / 1.6s` 逐个入场（单项 `pop 0.45s`，第三项 `2.05s` 落定）→ hold ≈0.65s（退场起点 = `per − exit − 0.05` = `2.70s`，成片按口播伸缩 `per`）→ `2.70s` 三项一起退场 0.35s（错峰 0.04）→ `3.1s` 结束。七式共用这条时间表，⑦ 的项间隔放宽到 0.75s（整屏换图比卡片多一点时间）。
- 入场语法按版式分四种：**弹出**（① ③ ④：`scale .8→1` / `x 60→0` / `x 120→0 + rotate +6→落位角`，`back.out(1.7)` 或 `power3.out` 0.45~0.5s）、**回彩**（②：`grayscale 1→0 + brightness .55→1` 0.45s，标签同帧 `x 40→0` 从右滑入；上一条**不回灰**，累积到三条全亮）、**擦入**（⑤：`clip-path inset(0 100% 0 0) → inset(0)` 0.5s）、**滑入**（⑥：整条斜带 `translate(-140,-70)→0` 0.5s）、**交叉淡化**（⑦：背景 0.3s 淡入 + 0.9s `scale 1.04→1`，上一张在下一张起 0.05s 后淡出；大字 `y 20→0` 0.4s，换词时上一词 `y −14` 淡出）。
- 人物形态：全身容器高 410 / 455 / 477（视频高 = 88%）站在画面底；小框 120×130（②）/ 120×126 圆角 26（③）/ 180×220（④）`object-fit: cover; object-position: 50% 8%` 取头肩；圆头像 170 直径 `scale 1.35` 取脸。小框与头像有自己的入场（0.1s 起 `scale .9→1` / `y −12→0` / `y 10→0`，⑥ 的头像 0.6s 起 `back.out(1.6)`）。
- 几何（960×540）：① 三卡 200×124、间距 24、组宽 648 居中、top 48（卡底到头顶 ≥36）；② 三横带 180 高、标签 right 60；③ 卡 300×96 列居中 x 330、间距 18；④ 卡 340×210 @ (300, 36)、歪斜 −4° / +3° / −2°、错位 (0,0) / (18,10) / (36,20)，小框 180×220 @ (390, 286)；⑤ 三条 320 宽、标签 top 40；⑥ 斜率 260/540、带宽 380、头像 170 @ (395, 185)；⑦ 大字 top 60，顶部 35% 黑色 scrim 保可读。
- demo 里版式名标签与示意图（Picsum，demos/_lib/media）是演示语境；成片用 `srcs` 注入真图、`items` 换文案、`layout` 单选一式。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `gap` 项间隔 | 0.6s | 跟口播"第一…第二…"的节奏；<0.45 读作一起出，>1.0 散成三张卡 |
| `pop` 单项入场 | 0.45s | 卡片类 back.out 的过冲就是"拍上去"；>0.6 拖、<0.3 弹不起来 |
| `per` 每式总长 | 3.1s（demo） | 退场起点 = `per − exit − 0.05`，拉长 `per` 即拉长 hold（demo 实际 hold ≈0.65s）；成片 = 讲完这一句的时长，任意伸缩；三项退场前观众要读完第三个标签。`CONFIG.hold 0.8` 只在注释里、未接线 |
| `exit` 退场 | 0.35s | 比入场快是通则；>0.5 像不舍得走 |
| `swapGap`（⑦） | 0.75s | 整屏换图的项间隔；<0.6 背景闪、>1.2 每张都成了独立镜头 |
| 标签字号 | 26 / 36~40 / 84 | 960 舞台口径（×2 = 1080p）；低于 26 等于没有 |
| 小框 / 头像位 | 见几何 | 只许改到不入人脸安全区、不压标签的位置；⑥ 头像四周留 ≥40 |

## 已知坑
- 三张一起淡入——"并列"读不出顺序，观众抓不住"第几"。
- 标签太小（<26@960）或不压在图上（另起一行小字）——图与词分家，等于三张没名字的图。
- 人被切走或缩成静态头像——口播变配音 PPT；小框里必须是继续说话的视频。
- ② 回彩后上一条又回灰——变成"焦点切换"而不是"累积列举"，第三条亮时观众忘了第一条。
- ④ 后一张完全盖住前一张——读作"替换"不是"一叠"，前一张必须露出一角（错位 18px + 歪斜）。
- ⑥ 三条斜率不一致、或头像压到标签——斜切的动感全靠平行；标签落在带内避开头像的那个角。
- ⑦ 大字压到人脸——大字只在顶部 60~150 带，人物头顶之上；背景换、人物不换。
- 一镜里连用两式——版式即语法，一句话只说一种；demo 巡演七式是为了看全，成片一镜一式。

## 复用指引
- props：`layout` / `items` / `srcs` / `hostSrc`；各式默认文案与版式几何在 CONFIG / JSX 常量里。
- Remotion/tsx（skill 首选）：template/cards/parallel-items-with-host.tsx——`layout` 单选一式（默认 `"tour"` 巡演 = demo 画面），`items` 三项文案，`srcs` 三张真图，`hostSrc` 人物 alpha 视频；时长用导出的 `durationFor(layout)`（单式 105 帧、tour 663 帧），hold 要长就把 `CONFIG.per` 拉大（`durationFor` 跟着变；`CONFIG.hold` 未接线）。
- tsx 的 `srcs` 走 `<Img>`；放视频把对应 `<Img>` 换成 `<OffthreadVideo muted>`（grid-to-hero.tsx 里有按后缀自动切换的现成写法），其余不动。
- HTML/GSAP：demos/parallel-items-with-host/index.html——`PRESETS` 数组决定巡演顺序与式数（删到一个即单式预览）；`CONFIG` 是全部节奏；每式一个 `<div class="preset">`，占位 `.ph` 整块换成 `<img>` 即真图。
- 与 layout.md 的接口：人物在场时主体组放人物对侧 / 人脸安全区优先（§4）；标签 ≥ 条目档（§5）；三卡组包围盒居中、组内等距 24（§2 §4）。
- 剪辑软件对应物：剪映"画中画 + 关键帧"逐张摆位 + "入场动画→弹入"；CapCut 模板区搜"并列 / 三件事"；AE 是三层 scale/position 关键帧 + Overshoot 表达式。

## 动效范围
- 属于本卡的：一式 3.1s 的时间表（0.4 起手 / 0.6 项间隔 / 0.45 单项 / ≈0.65 hold / 0.35 退场）与七式的入场语法（弹出 / 回彩累积 / 擦入 / 斜带滑入 / 交叉淡化 + 大字换词）；人物形态随版式变的四种处置及其入场；三项"逐个、压图、大标签"三条纪律；各式的落位几何（组居中、卡底到头顶 ≥36、标签 right 60 / top 40、斜率 260/540、大字 top 60）。
- 不属于本卡的：数字人视频与示意图（演示语境素材，demos/_lib/media，不属于本卡）、三项的具体文案、版式名标签（demo 巡演用）、白底舞台。
- 迁移接口：`layout` 选式；`items` / `srcs` 换文案与图；`hostSrc` 换人；`CONFIG.per` 按口播句长伸缩（退场起点跟着 `per` 走）；换画幅时几何按 960×540 等比缩放，竖屏把 ① 的三卡改两行或用 ③ 竖列。
- 底色要求：白底即可；② ⑤ ⑥ ⑦ 满铺素材时舞台底色不可见；③ 的虚化底自带一层 `#dfe1e6` 中灰。

## 落位自检（2026-09-05 用户定版，选卡时抄进 SHOTBOOK 该镜自检列）
- **人脸安全区优先**：人物在场先跑 `scripts/face_bbox.py` 拿实测 bbox；① 的三卡底边到头顶 ≥36、⑤ ⑦ 的标签 / 大字全时刻不入 bbox、⑥ 头像四周 ≥40 不压标签——任一违反换式（layout.md §4）。
- **逐项出现**：三项的入场起点差 = `gap`（0.6s），定妆帧核第一项落定时第二项尚未起步。
- **标签字号**：卡类 ≥26@960（≥52@1080p），全屏切分类 ≥36，大字 84；缩到 390 宽复看仍可读（layout.md §5 ⑨）。
- **组几何**：① 三卡组包围盒水平居中（偏差 >48 返工）、组内等距 24；③ 列居中且与顶部小框同轴；④ 前一张露出一角（错位 ≥18）。
- **一镜一式**：SHOTBOOK 该镜只写一个 `layout`；相邻两镜不连用同一式（换式或换镜头类型）。

<!-- ===== /file: video-talkcraft/references/cards/parallel-items-with-host.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/particle-weld-transition.md ===== -->

---
name: particle-weld-transition
标题: 粒子溶接转场
一句话: 出场镜头主体轻升失焦碎成一批粒子向上漂散，入场镜头用**同一个 seed** 再放一次同方向的粒子——它们从下方继续上升、在新主体位置收拢，主体在粒子聚拢的末段成形
适用: 有"同一件东西换了形态"语义的镜头边界：数据变成图表、概念变成实例、素材变成结论；也用在幕与幕之间的诗意衔接。一片 1~2 次
时长: 出场碎解 0.60s → 交叠 0.50s（≈15 帧 @30fps）→ 入场聚拢 0.70s；单次转场约 1.18s
能量: 中
类别: 转场结构
输入: 场
语义: 转场
素材形态: 无
位置: 中段
props: hostSrc(未使用)
优先级: P0
代码: template/cards/particle-weld-transition.tsx
---

## 意图
其余五式的动量都在**相机**上，粒子溶接的动量在**物质**上：观众读到的不是"镜头动了"，
而是"同一批粒子跨过了边界"。这叫物质连续性——它比相机连续性更强，因为它宣称的是
"上一镜的东西变成了下一镜的东西"，所以只能用在语义上真的成立的地方。

做对的命门：① **两组粒子必须同 seed**——出场散开的那批和入场聚拢的那批，尺寸、落点、错峰全部一致，
换了 seed 就是两批不同的粒子，物质连续性当场失效（观众说不出为什么，但"不对"）；
② **同方向**——出场向上飘散，入场也必须"从下方继续向上"，不能反过来往下落（那读作两次独立的粒子特效）；
③ **粒子层在镜头之上**——它跨过切点、盖住边界，这是本式不需要闪光也能藏住换场的原因；
④ **主体在粒子聚拢的末段才成形**（滞后 0.30s）——粒子先到、主体后成，顺序反了就成了"主体出现 + 一堆装饰粒子"。

## 动效核心
时间结构（`cut = at + 0.60 − 0.12`，参数全在 `CONFIG.weld`）：

| 阶段 | 时刻 | 出场镜头 | 粒子层 | 入场镜头 |
|---|---|---|---|---|
| 碎解 | `at` → `at+0.48` | 主体 `opacity→0` + `y −14px` + `scale 1.03` + `blur 3px`，`power2.in` | 出场组错峰亮起（各自 `delay = r*0.26s`），`y → −rise*(0.55~1.15)` + `x ±sway`，`power2.out` | 停在 `scale 1.02` |
| 粒子消隐 | `at+delay+0.33` 起 | — | 出场组 0.30s 淡出 | — |
| 切点 | `cut = at+0.48` | 0.50s 淡出 `power1.inOut` | 入场组在 `cut−0.06 + r*0.20` 就位（落在 lead 里） | 0.50s 淡入 + `scale →1.0` |
| 聚拢 | `cut` → `cut+0.70` | — | 入场组 `y: +rise*(0.5~1.0) → 0`、`x: ±sway → 0`，`power2.out`；末段 0.24s 淡出 | 主体先 `set` 到 `opacity 0` + `scale 0.94` + `y 16px` |
| 主体成形 | `cut+0.40` → `cut+0.82` | — | 已在消隐 | 主体 `opacity→1` + `scale→1` + `y→0`，0.42s `power2.out` |

- **确定性伪随机（不用 `Math.random`）**：`rnd(s) = fract(sin(s*127.1 + 311.7) * 43758.5453)`，
  两组粒子调用 `makeParticles()` 时用同一个 `seed*1000 + i*7 + k` 键空间，于是逐颗对应。
  Remotion 侧同一个 `rand(seed)` 实现（`transitions.tsx` 里的 `rand`），保证渲染确定性——
  用 `Math.random` 会让每帧重算、渲染出闪烁的噪点。
- **粒子的生成包围盒 = 主体包围盒**：demo 里 `HOME = {x:480, y:268, w:340, h:74}`（舞台 960×540 的字块）。
  实战里应该取真实主体（图表/卡片/大字）的包围盒——粒子从主体所在的区域里长出来，才读作"它碎了"。
  从全屏随机撒点会读作下雪。
- **错峰是碎解感的来源**：每颗 `delay = r(3) * 0.26s`。全部同时起飞读作一次爆炸；
  错峰超过 0.4s 则最后几颗还没起飞第一批已经消隐，读作零散。
- **两侧粒子的方向都是"向上"**：出场组从主体位置往上走（`y` 负向），
  入场组从主体位置**下方**（`y` 正的初值）往上走回 0。所以跨过切点看到的是一条不间断的上升流。
  把入场组写成"从上往下落回主体"是最常见的错误——那是两次独立的粒子动画。
- **主体成形滞后**：`cut + gather − 0.30`，即粒子快聚齐时主体才开始现形，0.42s `power2.out` 长成。
  这 0.30s 的重叠让"粒子变成了主体"这件事被看见。
- **镜头层的相机动作很轻**（入场 `1.02 → 1.0`）：本式的注意力在粒子上，相机抢戏会打散物质连续性。

Remotion 对应写法（`template/motion-systems/transitions.tsx`）：

- 出场 shot：主体用 `<Shatter at={tEnd-0.6} dur={0.6}>` 包起来（轻升 + 模糊 + 淡出的"壳"），同位置放一次 `<ParticleDrift at={tEnd-0.6} seed={7} count={36} box={主体包围盒} rise={180} />`
- 入场 shot：同一个 seed 再放一次，`at` 取负（落在 lead 里）：`<ParticleDrift at={-0.5} seed={7} count={36} box={新主体包围盒} rise={180} />`
- `seed` 必须两侧一致，`count` / `rise` 也建议一致；`box` 换成各自主体的包围盒即可——**位置可以变，"是同一批"由 seed 保证**。
- 像素淡化仍交给 `<ShotFade>`，粒子层不参与镜头淡化（它在镜头之上跨过切点）。

## 参数表
| 参数 | 典型值 | 调节手感 |
|---|---|---|
| `seed` | 7（两组**必须相同**） | 不同 seed = 两批粒子，物质连续性立刻失效；具体值无所谓，一致最重要 |
| 粒子数 `count` | 18（demo）/ 36（Remotion 默认） | <10 读作几个小方块在飞；>60 在白底上读作噪点/脏 |
| 上升位移 `rise` | 200px @540 舞台高 | <100px 粒子还在主体附近就消隐，读不出"离开"；>350px 出画后再回来，聚拢显得突然 |
| 横向漂移 `sway` | 46px | 0 读作机械上升；>90px 粒子散得太开，聚拢时像被吸进去（可用于刻意的"漩涡"效果） |
| 出场碎解 `out` | 0.60s | <0.4s 主体"啪"地消失，碎解没发生；>0.9s 观众等粒子飘完 |
| 入场聚拢 `gather` | 0.70s | 比碎解略长（散容易、聚要看清）；<0.45s 读作粒子被吸走；>1.1s 拖沓 |
| 交叠帧数 `overlap` | 0.50s ≈ 15 帧 | 偏长——粒子层要有时间跨过边界；<0.35s 换场那一下会露出来 |
| 主体成形滞后 | `gather − 0.30s` | 0（同时）读作"主体出现 + 装饰粒子"；>0.5s 粒子已散尽主体才来，因果断裂 |
| 每颗错峰 `delay` | `r * 0.26s` | 0 读作一次爆炸；>0.4s 首尾脱节 |
| 粒子尺寸 | 5~12px @960 舞台宽 | 太小读作噪点；太大读作方块碎片（也可以是刻意风格） |

## 已知坑
- 两组粒子用了不同 seed（或干脆用 `Math.random`）：不是"同一批粒子"，物质连续性失效；
  `Math.random` 还会让 Remotion 每帧重算，渲染出闪烁。
- 入场粒子从上往下落回主体：方向反了，读作两次独立的粒子特效而不是一次溶接。
- 粒子从全屏随机撒点：读作下雪/星空，不是"主体碎了"。生成盒必须是主体包围盒。
- 粒子层放在镜头层下面：换场边界露出来，本式就白做了（它正是靠粒子跨过切点盖住边界）。
- 主体与粒子同时出现：因果颠倒，读作"新主体带了一堆装饰粒子"。主体必须滞后。
- 粒子全部同时起飞/同时落定：读作爆炸 + 吸入，不是碎解 + 溶接。错峰是必需的。
- 出场主体只淡出没有"轻升 + 失焦"：壳没有碎解的过程，粒子像凭空生出来的。
- 相机同时做大幅推拉：抢走注意力，物质连续性被相机运动掩盖。本式相机要轻。
- 用在语义不成立的边界（两镜内容毫无关系）：观众读到"这两个东西是同一个"，然后发现不是，比硬切更困惑。

## 复用指引
- props：仅 `hostSrc`（声明未使用）；两个镜头为 JSX 写死的 tile、粒子包围盒 `HOME` 为常量，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/particle-weld-transition.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：`demos/particle-weld-transition/index.html`。摘 `particleWeld(出场镜头, 入场镜头, 起始秒) → 结束秒`
  + `CONFIG.weld` + `rnd()` + `makeParticles()` + `#weld` 那段 CSS。
  **`HOME` 要改成你的主体包围盒**（demo 是舞台 960×540 里的字块 `{x:480,y:268,w:340,h:74}`）；
  出/入两组都调 `makeParticles()`，函数内的 seed 键空间保证两组逐颗对应，不要给它们不同的 seed。`hold()` 一起摘。
- Remotion：`<Shatter>` 包出场主体 + 两侧 `<ParticleDrift seed={同一个值}>`（入场侧 `at` 取负落在 lead 里）；
  `box` 换成各自主体的包围盒。`rand(seed)` 已在 `transitions.tsx` 里，别引入 `Math.random`。
- 家族关系：本式是六式里唯一动量不在相机上的一式，因此**它可以和很轻的相机运动共存**，
  但不要和 [[whip-pan-transition]] / [[black-slam-transition]] 这类强相机式在同一边界叠用。
  想要"物质感"但语义上两镜无关时，改用 [[push-through-transition]] 更诚实。
- 剪辑软件对应物：AE 是 CC Particle World / Particular 两次发射（同 seed）+ Turbulent Displace，
  或 Trapcode Form 的双向 morph；剪映/CapCut 的"粒子/星光转场"是预制版但两侧不同 seed，
  只能读作装饰——本卡的关键正是把两侧绑成同一批。

## 动效范围
- 属于本卡的：出场侧主体的碎解壳（`opacity→0` + `y −14px` + `scale 1.03` + `blur 3px`，`power2.in`）；
  出场组粒子从**主体包围盒**内错峰（`r*0.26s`）亮起、`power2.out` 向上飘散（`rise*(0.55~1.15)` + `x ±sway`）、
  各自 0.30s 淡出；入场组粒子**同 seed 逐颗对应**、在切点前后就位、从主体位置**下方继续向上**收拢回 0（`power2.out` 0.70s）；
  粒子层 `z-index` 高于镜头层（跨过切点盖住边界，本式不需要闪光的原因）；
  主体成形滞后到粒子聚齐前 0.30s（0.42s `power2.out` 长成）；交叠 0.50s（≈15 帧）交叉淡化；
  确定性伪随机（`fract(sin(s*127.1+311.7)*43758.5453)`，禁用 `Math.random`）；hold 期相机永不静止的慢推。
- 不属于本卡的：两个镜头里的文字与配色（白/浅灰 tile + 灰字式名是"认式子的标签"，不是台词字幕）、
  左上说明角标、**粒子是方块还是圆点/发光**（demo 用 2px 圆角深色方块，Remotion 默认是发光圆点）、
  粒子颜色、`HOME` 包围盒的具体数值（应取真实主体）、`.shot` 的 `inset:-14%` 具体数值。
- 迁移接口：时序全在 `CONFIG.weld`（`out`/`overlap`/`gather`/`cutLead`）；
  **两组粒子必须同 `seed`**（换了就不是"同一批粒子"，物质连续性立刻失效——这是本卡最硬的约束）；
  换尺寸时 `rise` 按屏高比例缩放、`sway` 与粒子尺寸按屏宽比例缩放；
  `HOME`（Remotion 侧是 `box`）换成你的主体包围盒——**位置可以两侧不同**（新主体在别处也没关系），
  "是同一批"由 seed 而不是位置保证；`count` 按底色调（白底上 >60 颗会读作脏）。
- 底色要求：白底即可（demo 粒子用深色 `#1d1d1f`）。深色工程把粒子换成亮色/发光即可，
  时序与方向不动。本式不含闪光叠加层，因此没有 [[overexpose-flip-transition]] 那种极性反转问题。

<!-- ===== /file: video-talkcraft/references/cards/particle-weld-transition.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/pencil-sketch-draw.md ===== -->

---
name: pencil-sketch-draw
标题: 铅笔手绘揭示
一句话: 一只手握着铅笔沿真实笔迹把卡片/图形当场画出来，笔尖走到哪线到哪，画完抬笔、线保持干净静置
适用: 讲概念/流程时"现场画给你看"；亲和、手作、低科技感调性；配 TTS 讲解节奏逐笔出图
时长: demo 三笔 1.1 / 1.3 / 0.45s（首笔 0.3s 起，每笔画完铅笔 0.25s 抬走、下一笔接在抬笔之后）→ 末尾标签 0.35s 跟进；共约 4.05s。多笔按语音节拍串接
能量: 中
类别: 素材呈现
输入: 图
语义: 定义, 步骤
素材形态: 矢量, 透明通道
位置: 任意
props: hostSrc(未使用), handSrc
优先级: P1
代码: template/cards/pencil-sketch-draw.tsx
素材: demos/pencil-sketch-draw/hand-pencil.png（绿幕抠像透明 PNG，817×640）
---

## 意图
截图和图表是"给你看结论"，手绘是"带你走过程"——观众会跟着笔尖预测下一笔，注意力被押着走。
做对的命门：① 笔尖必须真的骑在路径上（不是线自己长出来）；② 描画速度要有起收笔的快慢，匀速像 loading。
本库定版：**不做 line boil / 定格抖动**（用户偏好，见 design-language.md §4 运动 token 附注）。
手绘感由笔迹形状本身（歪斜、弧度）与铅笔跟随表达；画面的"活"交给全局系统（相机漂/环境呼吸），不靠线抖。

## 动效核心
SVG path + `pathLength=100` + `strokeDashoffset` 从 100 减到 0 做描画；同帧用 tsx 自带的纯函数 `pointAtLength`
（`samplePath` 把 M/L/Q 路径折线采样并建累计弧长表，二分查点，不依赖 `@remotion/paths`）取路径上的点，把铅笔组 translate 到该点，`rotate(握笔角)` 给倾角。
笔具用**手握铅笔实拍素材（绿幕抠像透明 PNG，笔尖锚定局部原点）**——一只右手握黄色六棱铅笔的照片，
比矢量笔多给"有人在画"的临场感（手指关节、指甲、皮肤纹理是矢量补不出来的）。
关键是把照片对齐到与矢量笔相同的坐标契约：**石墨尖 = 局部原点 (0,0)，笔身朝 −Y 生长**。
三层嵌套完成对齐：外层 `<g>` 由 `placePencil` 写 translate+rotate+scale ／ 内层 `<g>` 固定
`rotate(−axisDeg)` 把素材里斜着的笔轴掰正到 −Y ／ `<image>` 用 `x=−tipX, y=−tipY` 把笔尖像素挪到原点。
于是 translate 到生长点即等于笔尖零偏移落点，倾角完全交给外层 rotate，改缩放/改倾角都不会让笔尖脱离笔迹。
笔身角 = 固定握笔角 **+42°**（实拍是右手、笔身朝右上，手落在笔迹右上方，符合右手书写遮挡关系）
+ `follow` × 行进切线的竖直分量（转弯轻微跟随，合成角始终落在 +37°~+47°）。
画完（p≥1）后铅笔**沿笔身轴向**抬离 26px 并淡出 0.25s（不是平移，才像被"提起来"）。
（本卡 tsx 不传 `handSrc` 时退回内建纯矢量铅笔；`template/components/pencil.tsx` 的 `PencilDraw` 是同一套原点契约的独立组件，另有 `keepPencil` 可让笔留在纸上。）

## 参数表
| 参数 | 典型值 | 调节手感 |
|---|---|---|
| `strokes[].dur` | 1.1 / 1.3 / 0.45 s（demo 三笔，以秒计） | 调小=速写感；>1.3s 观众等得着急 |
| `strokes[].width` | 4 / 5 / 6 px | 铅笔线 4~6；马克笔感调到 8+ 并换色 |
| `pencil.scale` | 0.5（实拍 640px 高素材） | 手+笔占屏高 55~65% 最稳；<0.4 手小得没有临场感，>0.6 手会盖住已画的线 |
| `pencil.tilt`（握笔角） | +42°（实拍右手） | 出 +37°~+47° 就不像手写：太竖像戳、太平像涂。矢量笔（左手向）取 −40° |
| `pencil.follow`（转弯跟随） | 5° | 0=笔身死板不跟手；>12° 笔跟着笔画整圈转，像风向标 |
| `pencil.lift` 抬笔距离 | 26px（0.25s 抬离 + 淡出） | 想要"写完搁笔"的仪式感可加大 + 减速 |

## 已知坑
- 线自己长、笔悬空不动——立刻穿帮，笔尖必须逐帧取路径点（tsx `pointAtLength`）。
- **笔尖不在原点**：把笔画成"笔杆 rect + 旋转"再靠 translate 猜偏移，一改缩放/倾角笔尖就飘离笔迹。
  正解是让石墨尖坐在局部 (0,0)、笔身朝 −Y，其余零件全部由这根轴推导。
- **实拍素材的锚定要量不要猜**：`tipX/tipY`（笔尖像素坐标）与 `axisDeg`（笔轴与竖直向上的夹角）
  必须从**最终那张 PNG**上量——裁边和缩放都会改坐标，先定稿素材再量，量完别再动图。
  笔尖：取左下角深色石墨像素簇里沿轴向投影最远的点（不是 bbox 角点，木锥面会把角点带偏）。
  轴角：对黄笔杆像素做 PCA 取主轴，方向调成指向橡皮头，再算与 −Y 的夹角（顺时针为正）。
  校验：在图上画出 tip 圆圈 + 从 tip 沿 axisDeg 的射线，射线要贴着笔杆中线走，否则动画里笔会"斜着蹭纸"。
- **抠像不要全局 despill**：黄笔杆 = R+G，`despill=type=green` 会把黄铅笔洗成红铅笔（mix 0.05 就变色）。
  正解：`colorkey` 之后 matte 内收 1px（`MinFilter(3)`）去掉最外圈绿边，再**只对半透明边缘像素**
  压绿（G 不许超过 max(R,B)）——肤色和笔杆都不受影响。绿值先用 PIL 采角落像素定（本素材 0x09EE20）。
- **照片被画幅切断的小臂要羽化**：原照右/下边缘把手臂切平，直接贴到白底上读成"断臂"。
  沿这两条边做 alpha smoothstep 渐隐（约 150/110px），让小臂溶出画面。
- 铅笔画成"黄方块 + 小三角"——读不出是铅笔。至少要有金属箍与橡皮头（辨识度靠这两截），
  笔杆给 2~3 个色面才有六棱的立体感，木锥面的棱线要和笔杆棱线对齐，否则像两截拼起来的。（矢量笔适用）
- 画完的线是静态元素：所在镜头的运动量由相机曲线/idle/环境层保底（motion_check 口径），不要用线抖去凑。
- 路径太复杂一笔画完——真人不会一笔画完一辆车，按"笔画"拆成多个 path 串接（起笔快收笔缓）。

## 复用指引
- props：`hostSrc`（声明未使用）、`handSrc`（手握铅笔实拍透明 PNG；不传 = 内建纯矢量铅笔兜底，与 demo 画面不同）；笔画表 `CONFIG.strokes` 与标签文案在源码里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/pencil-sketch-draw.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- **笔具二选一**：要临场感 → `handSrc` 传入手握铅笔实拍素材（`demos/pencil-sketch-draw/hand-pencil.png`，绿幕抠像透明 PNG，
  817×640，`tip=(1,552)`、`axisDeg=44.24`，即 tsx 的 `ASSET`）；要能换色/无素材依赖 → 不传 `handSrc`（tsx 内建矢量笔）或用 `pencil.tsx`。
  两者共用同一个坐标契约（笔尖 = 局部原点、笔身朝 −Y）：tsx 只切 `<Pencil src>`，HTML demo 只改 `makePencil()`，`placePencil` 一行不动。
- **换自己的手素材**：绿幕拍/生图（笔尖要清晰可见且不被手指挡住）→ 按"已知坑"里的抠像与羽化流程出透明 PNG
  → 量 `tipX/tipY` 与 `axisDeg` 填进 `ASSET` → 左手素材把 `tilt` 取负值（笔身朝左上、手在笔迹左上方）。
- Remotion：`template/components/pencil.tsx` 的 `PencilDraw`，传 `d`（SVG path）+ `at`（帧）+ `viewBox` 即用（`dur` 以帧计、默认 24；`tilt` 默认 −40 为矢量左手向）；多笔用多个实例按 at 错峰。
- 手绘 path 来源：Figma/Illustrator 画好导出 path，或让模型直接写简单几何的 d。
- 剪辑软件对应物：剪映"手绘动画"贴纸、AE 的 stroke 描边 + 关键帧笔 Null 绑定。

## 动效范围
- 属于本卡的：`strokeDashoffset` 从满到 0 的描画进度（起笔快收笔缓，`power2.inOut`，demo 单笔 0.45~1.3s）；手握铅笔逐帧 `getPointAtLength` 骑在笔尖上、笔尖零偏移落在生长点，握笔角 +42° ± 转弯跟随（始终在 +37°~+47°）；多笔按笔画顺序串接（一笔画完再起下一笔）；画完铅笔沿笔身轴向抬离 26px 并淡出；末尾标签的 0.35s 跟进。画完的线保持干净静置——**不做 line boil / 定格抖动**是本卡定版的一部分。
- 不属于本卡的：纸色/底色（demo 已改纯白）、示例里画的那辆车与卡片框的具体 path 形状、标签文案、线宽与字号、素材里那只手的肤色/性别/持笔款式。手绘感来自笔迹形状（歪斜、弧度）本身，不来自任何纹理或抖动。
- 迁移接口：线色改 `CONFIG.stroke`（默认墨色 #1d1d1f）；笔画表改 `CONFIG.strokes` 的 `d` / `dur` / `width`（每条 = 一笔）；速写感调小 `dur`（0.45s 起），马克笔感把 `width` 调到 8+ 并换色；笔的落点行为改 `CONFIG.pencil` 的 `scale` / `tilt` / `follow` / `lift`；换手素材改 `ASSET`（`href` / `w` / `h` / `tipX` / `tipY` / `axisDeg`，后三个必须在新图上重量）。素材是实拍照片，肤色与笔杆黄不做灰阶化——灰手灰笔读不出"有人在画"；用矢量笔时同理保留木色 #e8c39a、笔杆黄 #FFD400、金属箍灰与橡皮粉 #E79E96（靠这几截才读得出是铅笔而不是黄棒子）。
- 底色要求：白底即可。纸色（原 #f5f2ea）属于风格层，复用者想要纸面质感自己在底下铺一层，动效不依赖它。

<!-- ===== /file: video-talkcraft/references/cards/pencil-sketch-draw.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/per-character-rise.md ===== -->

---
name: per-character-rise
标题: 逐字升起
优先级: P1
代码: template/cards/per-character-rise.tsx
一句话: 每个汉字从自己位置下方（字号 44%）升到位，位移 0.33s、淡入 0.70s 走两条不同缓动，逐字错峰仅 1 帧（0.033s）——整句读作"一股气顶上来"而不是一个个蹦，全程零模糊零缩放
适用: 一句话的判断/主张/口号立在画面上——段落开头的论点句、结论句、口号；语速稳、句子短（6~10 字）的时刻；想要方向感与"顶起来"的力道但不要弹跳廉价感的调性；不适合连续跟读的常规字幕（每句都升会让整片有下往上的抖）
时长: 起手静置 0.3s → 位移 0.33s（升起）→ 淡入 0.70s（位移先停、淡入后停）→ 逐字错峰 0.033s（8 字整句在 1.23s 处全实）→ 收尾定格 1.2s；共约 2.43s
能量: 中
类别: 字幕花字
输入: 文
语义: 论点, 金句
素材形态: 无
位置: 任意
props: 无
---

## 意图
"字从下面升起来"是最常见的字幕入场，也是最容易做塌的一个——市面预设九成是
"整块上滑 + 淡入，一条 ease-out 到底"，做出来的东西没有骨头：位移与淡入同一条曲线同时结束，
整句读作一块半透明的板子被推上来。

这张卡的差别只在两条参数，但它们决定了全部手感：
① **位移与淡入用两条不同的缓动**。位移走 `cubic-bezier(0.2, 0.8, 0.6, 0.85)`——
起手冲一下、然后**几乎匀速地滑到位**（尾段不刻意缓收）；淡入走 `cubic-bezier(0.2, 0.8, 0.2, 1)`——
起手同样快、但尾段拖得很长。所以字的"到位"是硬的（有落点），字的"实起来"是软的（有余韵）。
一条曲线做两件事就会两头都不像。
② **位移只占淡入时长的 48%**（0.33s / 0.70s）。字在还只有一半透明度的时候就已经到位了，
剩下 0.37s 它在原地变实——这就是"一股气顶上来"这个感受的机制：**力道在前、余韵在后**。

第三条纪律是**零模糊零缩放**。加一点 blur 它就变成 `soft-blur-in`（能量档掉到低），
加一点 scale 它就变成弹跳字幕（能量档跳到高）。逐字升起的力道全部来自纯位移，别的都是杂音。

## 动效核心
- **两条轨、两条缓动、时长比 48%**：
  - 位移轨：`translateY +rise → 0`（rise = 字号 44%，demo 72px ⇒ 32px），`travel = 0.333s`，缓动 `cubic-bezier(0.2, 0.8, 0.6, 0.85)`
    （起手快 → 尾段近匀速，"到位"是硬的）
  - 淡入轨：`opacity 0 → 1`，`dur = 0.70s`，缓动 `cubic-bezier(0.2, 0.8, 0.2, 1)`
    （起手快 → 尾段长缓收，"实起来"是软的）
  - 两轨同起，位移先停 —— **"力道在前、余韵在后"的全部机制**
- **逐字错峰 0.033s（源码 1 帧 @30fps）**：第 i 个字的起点 = `lead + i × 0.033`。
  中文按码点切字（`Array.from`）即逐汉字；标点也算一个字，跟着升起是对的
- **起始下沉 ≈ 字号的 44%**（源码 `distance 32` @72px；本库 demo 同为 72px ⇒ 32）。
  这是比例常量不是绝对值——换字号必须等比改
- **零模糊零缩放**：本卡唯一被动画的属性是 `translateY` 与 `opacity`。
  加 blur ⇒ 退化成 `soft-blur-in`；加 scale ⇒ 退化成弹跳字幕
- **每个字是独立的 `inline-block`**：`transform-origin: 50% 55%`（重心略偏下，升起收尾时字不往上飘）、
  `backface-visibility: hidden`（transform 合成层稳定）
- **整行 `letter-spacing: -0.05em`**（源码值）：略收紧，让升起后的整句读作"一句话"而不是"一排字"
- **`white-space: nowrap` 是硬要求**：每个字都是独立 inline-block，不锁 nowrap 时浏览器会在任意两字之间换行
- **层级**：舞台白底 → 整行 flex 居中 → 单字（唯一被 transform 的元素）

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `dur`（淡入） | 0.70s | 本卡的余韵长度；<0.4s 字"实"得太快、力道读作硬切上滑，>1.1s 字长时间半透明、整句显得犹豫 |
| `travel`（位移） | 0.333s | **位移占 `dur` 的 48%，本卡第一命门**；= `dur`（同停）读作一块板子被推上来（市面预设的通病），<30% 则字到位太早、后半程只在原地变实、力道断掉 |
| 两条缓动 | 位移 `(0.2,0.8,0.6,0.85)` / 淡入 `(0.2,0.8,0.2,1)` | **本卡第二命门，两条必须不同**；共用一条（无论哪条）都会让"到位"和"实起来"变成一件事，骨头就没了 |
| `stagger` | 0.033s | 逐字错峰；0 = 整块上滑（能用但少了那股气），>0.1s 变成"一个字一个字往上蹦"（能量档跳一级、且中文长句会读作波浪） |
| `rise` | ≈字号 44%（72px ⇒ 32px） | 起始下沉量，**比例常量**；<字号 20% 力道不够、读作轻微上浮，>字号 70% 字从行外飞进来、抢掉整句的注意力 |
| `lead` | 0.3s | 起手静置等口播开口；0 则字与画面同时出现，观众来不及把注意力挪过去 |
| `hold` | 1.2s | 收尾定格——立住的整句是本卡的落点，按字数给（每字约 0.15s，读完再留半拍） |
| 字数 | 6~10 字 | 更长的句子错峰累积会让整句读作波浪（16 字 ⇒ 首尾差 0.53s，中文字宽整齐、波浪感很明显），要拆句 |
| blur / scale | **0（不设）** | 本卡的硬约束；任何非零值都把它变成另一张卡（见"意图"第三条） |

## 已知坑
- 位移与淡入共用一条缓动——整句立刻读作"一块半透明板子被推上来"，这是市面上所有上滑淡入预设的通病，也是本卡存在的唯一理由。
- 位移与淡入同时结束（`travel = dur`）——同上，"力道在前、余韵在后"整个消失。
- 顺手加一点 `blur`——它就变成 `soft-blur-in` 了（能量档从中掉到低），两张卡在库里就重复了。
- 顺手加一点 `scale`（哪怕 0.96）——立刻读作逐词弹跳字幕（Hormozi captions）那种入场，一眼廉价。
- `rise` 写成绝对像素值跟着复用——换字号后大字号下升起幅度不够、小字号下字从行外飞进来；必须按字号 44% 等比。
- 整行不锁 `white-space: nowrap`——每个字是独立 inline-block，浏览器会在任意两字之间换行，起手那一帧整句排版就是错的。
- 给整行（而不是单字）做位移——逐字错峰全部失效，退化成整块上滑（还不如直接写整块版，少一层 DOM）。
- 错峰放大到 0.1s 以上用在中文长句上——中文字宽整齐，均匀的大错峰会读作一道正弦波浪（英文长短词参差反而看不出），一眼廉价。
- 用在连续跟读的常规字幕上——每句都从下往上升，整片读作画面在往上抖；本卡是"立一句"，不是"跟读一段"。
- 重播不重建 DOM 只重置 transform——换文案后字数变了，旧的 span 还在，错峰序列与实际字数对不上。

## 复用指引
- props：无；文案在 `CONFIG.text`，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/per-character-rise.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/per-character-rise/index.html。**换内容只改 `CONFIG.text`** 这一个字符串（6~10 字），
  切字与错峰序列都是运行时算的。手感只调 `dur`（`travel` 要跟着保持约 48% 的比例）；
  换字号改 `.pcr-text` 的 `font-size`，同时把 `CONFIG.rise` 改成新字号的 44%。
  整句的落位改 `.pcr-line`（demo 是 `inset: 0` + flex 整屏居中的**纯文字卡**，不放主持人；
  要让人物留在画面里就把 `.pcr-line` 收成一列白区，同时按新宽度把 `font-size` 收回去）。
  **两条缓动 `FADE_EASE` / `TRAVEL_EASE` 是手感常量，不要动、更不要合成一条。**
  `cubicBezier()` 那个解算器是通用的，别的 demo 要 `cubic-bezier` 缓动可以直接抄走。
- Remotion 移植：`template/cards/per-character-rise.tsx` 就是逐帧查表写法（不建时间线，每帧算每个字该在哪），
  比搬 GSAP 时间线更直接，可以原样抄。**帧↔秒换算（上游源码 30fps）**：
  `charDurationFrames 21` ⇒ `dur 0.70s`、`charTravelFrames 10` ⇒ `travel 0.333s`、`staggerFrames 1` ⇒ `stagger 0.033s`。
  每字两个 `interpolate`，**两条的 `easing` 必须分开传**：
  淡入 `Easing.bezier(0.2, 0.8, 0.2, 1)`、位移 `Easing.bezier(0.2, 0.8, 0.6, 0.85)`；
  两条都要 `extrapolateLeft/Right: "clamp"`（不 clamp 的话 `local < 0` 的字会算出负 opacity 并被提前渲染出来）。
  `local = frame - i * staggerFrames` 是两条 interpolate 共用的局部时钟。
  尺寸换算：源码 `fontSize 72` 是 1280×720 画幅的值；本库 demo 是**纯文字整屏**，960 舞台上直接用 72px，
  所以 `distance 32` 与源码同值（比例照旧：distance = 字号 44%）。
  **不要**顺手换成 `spring()`——spring 的过冲会带来回弹，本卡是零回弹的。
- 剪辑软件对应物：剪映/CapCut——"向上滑入"/"上移"预设都是位移与淡入同停的整块版（正是本卡要避开的），
  正确做法是一个文本层手打两组关键帧：位置（下方 `rise` = 字号 44% → 0，**0.33s**）+ 不透明度（0 → 100，**0.70s**），
  两组曲线各自单独调（剪映的曲线编辑器能分属性调，一定要分开调，这是全部差别）；
  逐字错峰做不出来（"逐字显示"是硬切），0.033s 肉眼几乎读不出，**放弃错峰做整块版**是合理取舍。
  AE——一个文本层 + `Text Animator`：加 `Position`（Y +24 → 0）与 `Opacity` 两个属性，
  但**必须建两个 Animator**（一个只带 Position、一个只带 Opacity），两个 `Range Selector` 的 Offset
  用不同时长的关键帧（0.33s / 0.70s），曲线在 Graph Editor 里各自拉成对应的 bezier；
  合在一个 Animator 里就只能共用一条曲线 —— 那就退化成市面预设了。
- 与本库同类卡的分工：`keyword-pop-highlight` = 一句里砸一个重音；
  `typewriter-reveal` = 逐字符敲出（有档案感的节拍）；`soft-blur-in` = 最低能量的整句对焦（无方向）；
  **本卡 = 有方向、有力道、零回弹的整句立起**（竖向顶上来，是同类里唯一"有劲但不跳"的那档）。

## 动效范围
- 属于本卡的：位移与淡入**两条不同缓动**（位移 `(0.2,0.8,0.6,0.85)` 近匀速到位 / 淡入 `(0.2,0.8,0.2,1)` 长尾缓收）这个组合；位移只占淡入时长 48% 这条时间纪律（力道在前、余韵在后）；起始下沉恒为**字号的 44%**这个比例；`stagger 0.033s`（源码 1 帧）这个"小到几乎不是逐字"的错峰量级；**零模糊零缩放**这条硬约束；`transform-origin: 50% 55%` 这个略偏下的重心；单字 `inline-block` + 整行 `nowrap` 这个实现纪律。
- 不属于本卡的：demo 那句「先想清楚，再动手」的具体文案、72px 字号与 600 字重、`#171717` 这个墨色、`letter-spacing: -0.05em`（拉丁字体的收紧值，中文可取 0 到 −0.05em 之间任意值）、无衬线字族的选择、白底舞台、以及"整句落在舞台正中"这个落位（画幅正中、下三分之一、字幕安全区都成立）。**demo 是纯文字卡、不放主持人**（2026-08-25 用户定版）——整屏交给这一句，人物占位会把注意力从"一股气顶上来"这个动作上分走；但应用侧要让人物照常出镜同样成立（句子落在人物旁的留白列或字幕安全区），落位不属于本卡的动效本体。
- 迁移接口：`CONFIG.text` 是唯一的内容入口（6~10 字）；手感只调 `dur`，`travel` 必须跟着保持约 48% 的比例；`rise` 按字号 44% 等比缩放；**两条缓动与 `stagger` 是手感常量，换尺寸换语速都不要动**（字数超过 10 时 `stagger` 减到 0.02s，或者直接拆句）；`hold` 按字数给（每字约 0.15s）；竖屏用 6~8 字并把字号收到 40~46px（本卡不改变排版宽度，唯一约束是整句 `nowrap` 后不超出可用宽度的 90%）。
- 底色要求：白底或深底都成立（深底把字色反白即可），本卡零模糊零缩放，对底色最不敏感。唯一约束是**底不能有横向条纹或横向渐变**——字在底上竖向升起，带横向纹理的底会与竖向位移产生视差错觉（字看起来在斜着走）。实拍花底上可用，但要给字加描边或半透明底板保证可读（本卡不自带任何背板）。

<!-- ===== /file: video-talkcraft/references/cards/per-character-rise.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/pip-zoom-box.md ===== -->

---
name: pip-zoom-box
标题: 画中画放大
优先级: P1
代码: template/cards/pip-zoom-box.tsx
一句话: 细描边取景框先在人物脸上出现停一拍，然后带着框里的画面 0.5s 平移放大到右侧空位定居，落位那刻换成白边卡 + 唯一投影，箭头随后从人物划向它
适用: 口播说到"我们把这一块单独拎出来看"——需要在保留全景的同时长期展示某个局部；讲解手部动作/表情/产品细节/截图局部；后半程还要继续讲全景时（局部留在侧边不撤）
时长: 起手静置 0.4s → 取景框浮现 0.2s → 瞄准停 0.15s → 平移放大 0.5s（白边卡在末段交接）→ 箭头 0.18s → 定居 hold 1.8s；共约 3.3s
能量: 中
类别: 运镜
输入: 人(可选), 图
语义: 强调
素材形态: 无
位置: 任意
props: hostSrc
---

## 意图
"看这里"有两种做法，本库各有一张卡，**区别在放大后那个局部住在哪里**：

`magnifier-detail` 是**原地放大**——镜片在出处附近弹出、本体压暗、连接线回指，语义是
"我现在指给你看这一处"。它是**巡视**的：镜片在 hold 期还轻微扫视，看完就该收，
一次只服务一句话，全景在它出现的那几秒是被压暗的配角。

本卡是**框带内容飞到侧边定居**——取景框在原位框住目标，然后**连框带画面一起**搬到画面外侧的
空位，从此以一块独立素材的身份长期挂在那里。全景**不压暗、不让位**，因为它还要继续讲。
语义是"这一块我拿出来放在旁边了，接下来我一边讲全景一边你可以一直看它"。
它是**定居**的：落位后完全静置，因为它已经不是一个动作，而是一块常驻素材。

所以选卡的判据只有一句：**放大的这一块，是看一眼就撤（放大镜），还是要一直挂着（画中画）**。

命门两条：① 框移动时**内容必须跟着走**。框的几何与框内画面的补偿必须由同一个进度单点写入——
拆成两条 tween 一定会因缓动不同步而让内容从框里滑出去，那一眼读作"一个空框飞过去了"。
② **框先出现、停一拍、再飞**。少了这 0.15s 的瞄准拍，读作框自己从右边飞过来抓了一把
——"框住这里"这个动作就没有发生过。

与运镜类其余七张的分界是**动的是不是画幅**：那七张相机一动全画幅都变，本卡只把一小块搬到旁边、
全景一直在——本类唯一**保留全景**的一张，所以能在"后半程还要继续讲全景"的段落里长期驻留。

## 动效核心
- **变换组三层，几何单点写入**：
  - `.pz-shell`（变换组）：`left/top/width/height` 四个值由 `setPip(t)` 写入
  - `.pz-win`（取景窗）：唯一做 `overflow: hidden` 的元素
  - `.pz-win > 画面副本`：与底层全景**同结构同像素**的第二份 DOM（demo 里第二个
    `.host-placeholder`，外壳会给每个都注入数字人视频）
- **`setPip(t)` 是本卡的全部**（t: 0 = 贴在脸上的 1:1 取景框，1 = 右侧定居的 zoom 倍画中画）：
  - `zoom = lerp(1, 2.2, t)`、`w = lerp(boxW/zoom, boxW, t)`、`h` 同理
  - 中心 `cx = lerp(faceX·SW, targetX, t)`、`cy = lerp(faceY·SH, targetY, t)`
  - **反向补偿**：副本 `transformOrigin: 0 0`、`scale = zoom`、
    `x = w/2 − zoom·faceX·SW`、`y = h/2 − zoom·faceY·SH`
    ⇒ 脸部锚点恒落在框心，**画面本身全程不变形**
  - `t=0` 时 `zoom=1` 且补偿正好抵消框位移 ⇒ 框内与框外像素严格连续（看不出有第二层）
- **时序四拍**：
  - ① 框浮现：整个变换组 `scale 0.9 → 1` + `opacity 0 → 1`，`0.20s power2.out`
    （scale 作用在**组**上 = "框与内容是一件事"的第一次声明）
  - ② 瞄准停 `0.15s`（本卡第二命门）
  - ③ 平移放大：`t: 0 → 1`，`0.50s power2.inOut`——**相机曲线唯一缓动**（design-language §4），
    起收都要缓；`power3.out` 会读作"被甩过去"
  - ④ 箭头：落位 +0.05s 后箭杆 `dashoffset` 划出 `0.18s power2.out`，箭头头部在箭杆走完 70% 时
    `0.1s` 补上（单向指示，箭尖离框留 ~18px 不戳到）
- **边饰交接（两层，几何都跟着 shell 走）**：
  - 起手：`box-shadow: 0 0 0 1.5px accent` 细取景描边（"取景"是机器动作，细线 + 强调色）
  - 落位：`0 0 0 8px #fff`（白边卡）+ `0 12px 60px rgba(0,0,0,0.22)`（**全系统唯一投影，
    只给落在底上的证据素材**，design-language §3）
  - 细描边在飞行后 60% 处 `0.22s` 淡出、白边卡在落位前 0.06s `0.18s` 淡入 ⇒ 交接在落位那一帧完成。
    **两层都只有 box-shadow、不占布局**，所以永不与框错位
- **圆角随尺寸走**：`4px → 10px`（小框配小圆角；固定 10px 在起手的 127px 小框上会读作圆角贴纸）
- **定居期完全静置**：不扫视、不呼吸——它已经是一块素材，不是一个动作
- **层级**：底层全景（z1） → 箭头（z4） → 画中画变换组（z5）

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `zoom` | 2.2 | 放大倍数，本卡的核心旋钮；<1.8 观众看不出"这是放大的"（读作贴了张小图），>3 素材分辨率兜不住（数字人 540p 在 3x 上已经能看到像素）。**它同时决定起手取景框的大小**（`boxW/zoom`）——调大 zoom，起手的框会自动变小、框得更准 |
| `boxW`/`boxH` | 280 / 280 px | 定居后取景窗尺寸（不含白边）；等宽高 = 方框（参考图形制）。>340 会挤到全景，<200 放大了也看不清 |
| `targetX/Y` | 764 / 270 | 定居中心（舞台坐标）；必须落在**全景的留白侧**，压到人物身上就成遮挡而不是"拿出来放旁边" |
| `faceX`/`faceY` | 0.275 / 0.315（比例） | 取景锚点，**换人物/换素材必须重校**。校准法：把 `t` 锁在 0 看细框是否正好框住目标。写成比例而非像素，换画幅不用重校 |
| `flyDur` | 0.50s | 平移放大耗时；<0.32s 读作"甩过去"（丢掉"搬"的重量），>0.8s 观众等着它落地、口播已经讲下一句了。缓动必须 `power2.inOut` |
| `aimHold` | 0.15s | 浮现到起飞的瞄准停，**本卡第二命门**；0 读作框自己飞过来（"框住这里"没发生），>0.4s 节奏断一拍 |
| `showDur` | 0.20s | 取景框浮现耗时；>0.35s 框自己变成一个动效（它只是个声明，要轻） |
| `hold` | 1.80s | 定居时长；实拍里 = 讲完这一段，可任意延长（本卡的价值就是能长期挂着） |
| `radius0`/`radius1` | 4 / 10 px | 圆角随框尺寸走；两者相等 = 小框上圆角过大读作贴纸 |
| `arrowDur` | 0.18s | 箭杆划出；它是落位后的补充说明，>0.3s 就抢了主体 |

## 已知坑
- 框和内容用两条 tween 各自动画——缓动一不同步内容就从框里滑出去，读作"一个空框飞过去了"（本卡最致命的错法）。几何必须单点写入。
- 只飞框、内容用固定的裁切图——起手那一帧框内与框外接不上（有一道明显的错位缝），观众立刻知道那是两层假的。
- 框一出现就飞——"框住这里"这个动作没有发生，读作右边飞过来一个框抓了一把。必须留瞄准拍。
- 用 `power3.out` 飞——起手猛、收得急，读作被甩过去；"搬一块素材"要 `power2.inOut`（起收都缓，相机曲线）。
- 落位后给画中画做扫视/呼吸——那是 `magnifier-detail` 的语言（巡视）；本卡是定居，微动会把"常驻素材"变回"一个动作"。
- 落位不换白边卡、全程只有细描边——少了"这是一块摆上来的实物"的实体感，读作一个 UI 浮层。
- 白边卡的投影自己调一个（比如 `0 4px 12px`）——全系统只有一个投影（`0 12px 60px rgba(0,0,0,0.22)`），换了就破了 design-language §3。
- 起手细描边不退场，白边卡叠在细描边上——两层边饰同时在，框读作"描了两道边"。必须交接。
- 圆角写成固定值——起手的框只有 `boxW/zoom` 那么大（本卡 127px），10px 圆角在它身上读作圆角贴纸。
- 底层全景跟着压暗——那是放大镜的语法（本体让位）；本卡全景还要继续讲，压暗等于告诉观众"别看这边了"。
- 换了人物素材不重校 `faceX/faceY`——起手的框框在耳朵上或框在空气里，第一拍就废了。
- 两层人物视频不对时——框内框外嘴形不一致，一眼看出是两层（demo 用 900ms 一次的 `currentTime` 对齐兜住；这是演示语境的工程细节，实拍里两层来自同一条素材没有这个问题）。

## 复用指引
- props：仅 `hostSrc`；被放大的全景是 `.pz-scene` 内 JSX（两份同构），换素材需改源码并重校 `faceX/faceY`。
- Remotion/tsx（skill 首选）：template/cards/pip-zoom-box.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/pip-zoom-box/index.html。**换素材只做两件事**：把 `.pz-scene` 的内容换掉
  （两份必须完全同结构——`.pz-win` 里那份是副本），然后重校 `CONFIG.faceX/faceY`
  （校准法：临时把 `setPip(0)` 后的 `tl` 注释掉，看细框有没有正好框住目标）。
  换落位改 `targetX/targetY`，换尺寸改 `boxW/boxH`（`zoom` 会自动决定起手框大小，不用另算）。
  `setPip(t)` 那个函数是通用的——任何"框带内容平移放大"都可以直接抄走，
  只要目标层是可被 `transform` 的 DOM（截图卡、图表、网页 iframe 皆可）。
- Remotion 移植要点：把 `setPip` 原样搬成每帧算的纯函数——
  `const t = interpolate(frame, [flyStart, flyStart+15], [0,1], {easing: Easing.inOut(Easing.quad), extrapolateLeft:'clamp', extrapolateRight:'clamp'})`
  （30fps：`flyDur 0.5s = 15 帧`），然后 `zoom/w/h/cx/cy` 全部由 `t` 现算。
  框外层用 `<div style={{position:'absolute', left, top, width, height, overflow:'hidden'}}>`，
  框内放**同一个 `<Scene/>` 组件的第二个实例**并套 `transform: scale(zoom) translate(...)`
  （`transformOrigin: '0 0'` 必须写，否则补偿公式全错）。
  实拍素材两层用同一个 `<OffthreadVideo>` 的同一 `startFrom` ⇒ 天然同步，不需要 demo 那个对齐兜底。
  白边卡与投影用 `boxShadow` 字符串在落位帧切换（Remotion 里直接 `frame >= landFrame ? cardShadow : hairline`
  加一个 3 帧的 opacity 交叉更干净）。
- 剪辑软件对应物：剪映/CapCut——**复制一条相同的视频轨**放在上层，给上层加"蒙版·矩形"
  （方框），然后**给上层的"缩放/位置"和蒙版的"大小/位置"打同一组关键帧**（两组关键帧的时间和
  曲线必须逐个对齐，这是全部工作量所在，剪映没有"组"的概念）；缓动选"缓入缓出"。
  白边用蒙版的"描边"或叠一个白色方形色块。
  AE——正确做法是**预合成**：把放大层与遮罩放进一个 comp，然后只对这个 comp 的
  `Scale` + `Position` 打两个关键帧（这就是"同一个变换组"，AE 里天然支持，比剪映省一半事）；
  框内内容的反向补偿用 comp 内层的 `Scale = 220%` 与 `Anchor Point` 定在脸上即可，不用表达式。
  `Drop Shadow`（Distance 12 / Softness 60 / Opacity 22%）在落位帧开。
- 与本库同类卡的分工：`magnifier-detail` = **原地放大 + 看完就撤**（圆镜、本体压暗、连接线回指、
  hold 期扫视，服务一句话）；`cursor-locked-zoom` = **相机跟着光标推近**（整个画面在动，没有第二层）；
  `focus-dim-spotlight` = **不放大，只压暗周围**（局部原尺寸、靠反差指路）；
  **本卡 = 框带内容飞到侧边定居**（全景不让位、局部长期挂着、落位后静置）。

## 动效范围
- 属于本卡的：`setPip(t)` 这个"框的几何 + 框内画面的反向补偿由同一进度单点写入"的工程纪律（本卡的本体）；`t=0` 时框内与框外像素严格连续这个约束；四拍时序「浮现 0.2s → 瞄准停 0.15s → 平移放大 0.5s `power2.inOut` → 箭头 0.18s」；scale 作用在整个变换组而非框或内容单独一方；两层边饰在落位那一帧交接（细取景描边淡出、白边卡 + 唯一投影淡入）；圆角随框尺寸从 4px 走到 10px；定居后完全静置（拒绝扫视/呼吸）；箭头在落位**之后**才划出且箭尖留白不戳到框。
- 不属于本卡的：demo 的数字人主持人这个具体被放大对象（换成截图卡、图表、网页都成立）、`#0066cc` 这个具体强调色、`faceX/faceY` 的具体数值（这是素材属性，换素材必重校）、`targetX/Y` 这个"定居在右侧"的具体落位（左侧、上方同样成立）、方框这个形制（圆形/竖长条也可以，只要框与内容同组）、白底舞台、以及 demo 里那段两层视频 `currentTime` 对齐的兜底代码（演示语境的工程细节，实拍两层同源时不需要）。
- 迁移接口：素材入口 = `.pz-scene` 的内容（两份必须同结构）+ 重校 `faceX/faceY`（比例值，换画幅不用改）；尺寸入口 = `zoom`（同时决定起手框大小）+ `boxW/boxH`；落位入口 = `targetX/targetY`；节奏入口 = `flyDur`（缓动锁死 `power2.inOut`）与 `aimHold`；`hold` 按口播实际长度给。换画幅：`faceX/faceY/targetX/targetY` 全是比例或按新舞台重算的坐标，`boxW/boxH` 按舞台短边等比缩（280/540 ≈ 52% 短边）；竖屏改成"定居在下方"（竖屏侧边没有 280px 的留白）。
- 底色要求：白底即可。唯一约束是**落位区必须是纯净留白**——白边卡 + 唯一投影是"实物摆在底上"的语义，底上有内容（文字、图形、人物）时投影会读作脏；同理深底上白边卡要改成深色边（`#2a2a2c`）并把投影换成 design-language 深底模式的辉光，否则白边在深底上比内容还抢眼。

## 落位自检（2026-09-05 用户定版，选卡时抄进 SHOTBOOK 该镜自检列）
- 标注几何（框 / 圈 / 线 / 箭头 / 放大镜锚点）一律由**目标的实测包围盒**反推——DOM `getBoundingClientRect` / `measureText`，四边留白 16~24px 等距，**不目测**。
- 实现后抽该镜定妆帧核对：标注是否恰好套住 / 指向目标，偏差 **> 8px 返工**（`references/layout.md` §3）。
- 目标会滚动 / 移动时，标注钉在内容坐标系随内容动（SKILL.md ③）。

<!-- ===== /file: video-talkcraft/references/cards/pip-zoom-box.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/pullback-cool-transition.md ===== -->

---
name: pullback-cool-transition
标题: 后拉冷却转场
一句话: 出场镜头相机收住不推不拉，靠内容自己褪暗失焦交出画面；入场镜头从 scale 0.90 起步——全片唯一 scale<1 的后拉——用 0.90s 缓慢拉到 0.99 落定，节奏是六式里最慢的
适用: 一段情绪的收尾：讲完激烈论证进入沉淀、结论前的呼吸、段落间的"我们退一步看"；也用在色温转冷/转暖的幕边界
时长: 出场沉暗 0.50s → 交叠 0.55s（≈16 帧 @30fps，全六式最长）→ 入场后拉 0.90s；单次转场约 1.35s
能量: 低
类别: 转场结构
输入: 场
语义: 转场
素材形态: 无
位置: 中段
props: hostSrc(未使用)
优先级: P0
代码: template/cards/pullback-cool-transition.tsx
---

## 意图
其余五式都在往前推、往旁甩、往里撞，处理的是"信息还在增加"。后拉冷却是唯一往后走的一式：
它让观众**退开一步**——上一段的内容自己沉下去（不是被推走），新一段从远处慢慢拉近到工作景别。
用在情绪收束点，它给出一次合法的呼吸；用错在信息推进段，整片节奏会当场塌掉。

做对的命门：① **相机收住，让内容自己退场**——出场侧的动作不在相机上（`scale` 回到 1.0 就停），
而在内容的亮度/焦点上；相机还在推的同时内容在沉暗，两个方向打架，读作"没做完"；
② **入场是全片唯一 scale<1 起步**——这个稀缺性就是本式的识别标志，别的地方用了它就不特殊了；
③ **节奏要真的慢**——`settle` 0.90s 是六式里最长的，交叠 0.55s 也是最长的；照抄推穿的 0.6s 会读作"后拉但很急"，
自相矛盾。

## 动效核心
时间结构（`cut = at + 0.50 − 0.05`，参数全在 `CONFIG.pull`）：

| 阶段 | 时刻 | 出场镜头 | 入场镜头 |
|---|---|---|---|
| 内容沉暗 | `at` → `at+0.50` | **内容层**（不是镜头层）`opacity 1→0.18` + `blur 0→2px`，`sine.in`；**镜头层** `scale →1.0` 收住，`sine.out` | 停在 `scale 0.90` + `blur 4px` |
| 切点 | `cut = at+0.45` | 0.55s 淡出，`sine.inOut` | 0.55s 淡入，`sine.inOut` |
| 后拉落定 | `cut` → `cut+0.90` | — | `scale 0.90→0.99` + `blur 4→0`，`power2.out` |
| 交班 | — | — | hold 期慢推（从 0.99 继续 +0.03，`sine.inOut`） |

- **出场侧分两层写**：内容层沉暗（demo 里是 `.big` 大字，实战里是整个主体面）、
  镜头层把 scale 收回 1.0。这不是"相机不动"，而是"相机停止发力"——它从 hold 期的慢推里减速到静止，
  是一次减速而不是一次停顿（和 [[black-slam-transition]] 的定格截然不同：那里是硬停，这里是软收）。
- **深底 vs 白底的沉暗语义**：深色工程里是"内容沉入近黑"（亮度归零，环境吃掉主体）；
  白底 demo 里等价物是"褪灰失焦"（`opacity 0.18` + 2px 模糊）。两者视觉不同、语义相同：内容主动退场。
  这一层是**场景内的事**，不在相机 rig 上，所以两种底色的写法可以不同而不影响相机曲线。
- **全部用 `sine` 系缓动**（`sine.in` / `sine.out` / `sine.inOut`）：正弦缓动没有 `power` 系的陡峭段，
  读作"呼吸"而不是"动作"。只有最后的后拉用 `power2.out`（要有落定感，不能一直飘）。
- **落点 0.99 不是 1.0**：留 0.01 给 hold 期继续推——本式最慢，但依然不许静止（相机永不静止是全库铁律）。
- **交叠 0.55s（≈16 帧）是全六式最长**：因为两侧都很轻（一个在沉暗、一个在缓慢放大），
  交叠短了会看到"旧的还没沉完新的已经全亮"的重影。
- **色温**：实战里这一式常配色温转冷（`env.tsx` 的 `ACTS` 表在幕边界做 1.2s cross-fade）。
  色温不属于本卡动效本体（见动效范围），但它是这一式最常见的同伴。

Remotion 对应写法（`template/motion-systems/transitions.tsx`）：

- 出场 shot（相机侧只写"收住"：末键把 scale 停在 1.0，之后不再加键；沉暗在场景内做）：`{ tail: 16, path: [{t:0, scale:1.05}, {t:tEnd, scale:1.0}] }`
- 入场 shot（全片唯一 scale<1 起步）：`{ lead: 16, path: [...pullBackIn(leadSec), {t:9, scale:1.0}] }`
- `pullBackIn(leadSec, {from:0.94, to:0.99, blur:4, settle:0.9})` 生成两个 CamKey，首键 `t` 取负（落在 lead 里）。
- 出场侧的内容沉暗用场景自己的 `interpolate`（亮度/滤镜），或直接走 `life.tsx` 的 `<Live demoteAt>` 让位状态机——它本来就做"缩 0.92 + 上移 + 亮度 −66% + 3px 模糊"（降权留守，元素仍占槽）。

## 参数表
| 参数 | 典型值 | 调节手感 |
|---|---|---|
| 入场起手景别 `inScale` | 0.90 | >0.95 后拉量太小、读不出"退一步"；<0.82 四周露底（镜头层必须铺过画幅），且落定路程过长 |
| 入场后拉时长 `settle` | 0.90s | 全六式最长。<0.6s 读作"急着后拉"，与冷却语义打架；>1.4s 观众等不住 |
| 交叠帧数 `overlap` | 0.55s ≈ 16 帧 | 全六式最长。<0.4s 出现新旧重影（两侧动作都很轻，遮不住边界）；>0.7s 两场糊在一起 |
| 出场沉暗时长 `out` | 0.50s | <0.3s 内容"啪"地暗掉读作断电；>0.8s 观众盯着一个正在变暗的画面等待 |
| 沉暗深度 `outDim` | 0.18（白底）/ 近黑（深底） | >0.4 沉得不够、读作"轻微变淡"；到 0 就成了纯色帧转场（另一语法） |
| 出场失焦 `outBlur` | 2px | 比推穿轻得多——本式不靠速度模糊，靠焦点撤离；>5px 读作被推走 |
| 切点提前量 `cutLead` | 0.05s | 全六式最小：交接靠"暗"而不是靠"快"，不需要提前吃掉加速段 |
| 后拉落点 `inSettle` | 0.99 | 落到 1.0 再静止 = 撞墙；留 0.01 给 hold 继续推 |

## 已知坑
- 出场侧相机还在推、内容同时在沉暗：两个方向打架，读作"这一镜没做完"。相机必须先收住。
- 照抄推穿的 0.6s settle：变成"急促的后拉"，与冷却语义自相矛盾。本式的慢是它的内容。
- 入场 scale<1 在片子别处也用了：稀缺性一失效，本式就只是"淡入 + 轻微放大"。
- 交叠给短了（<0.4s）：两侧动作都轻，遮不住边界，出现新旧画面重影。
- 用 `power3`/`back` 系缓动：陡峭段让"呼吸"变成"动作"，冷却感消失。sine 系是本式的语法。
- 沉暗写在镜头层（把整镜 `opacity` 拉到 0.18 再淡出）：那只是双重淡出，看不出"内容主动退场"。
  沉暗必须作用在内容层，镜头层的淡出交给交叠包络。
- 镜头层没铺过画幅：`scale 0.90` 起手时四周直接漏底色。demo 用 `.shot { inset:-14% }` 兜住。
- 用在信息推进段：整片节奏塌一次，观众以为要结束了。

## 复用指引
- props：仅 `hostSrc`（声明未使用）；两个镜头为 JSX 写死的 tile，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/pullback-cool-transition.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：`demos/pullback-cool-transition/index.html`。摘 `pullBack(出场镜头, 入场镜头, 起始秒) → 结束秒`
  一个函数 + `CONFIG.pull` 一组参数。**注意函数内部取了 `out.querySelector(".big")`**——
  沉暗作用在内容层而不是镜头层，迁移时把这个选择器换成你的主体面容器。`hold()` 一起摘。
- Remotion：`pullBackIn(leadSec)` spread 进入场 shot 的 `path`（首键 `t` 取负）；
  出场侧相机只写"收住"（末键 `scale: 1.0` 后不再加键），内容沉暗在场景内做或直接用 `life.tsx` 的 `<Live demoteAt>`。
  色温转冷在 `env.tsx` 的 `ACTS` 表配。
- 家族关系：它是 [[push-through-transition]] 的反向式（那个 scale>1 沉降，这个 scale<1 拉近），
  两者的入场起手方向相反，所以**同一片里两式可以互补使用**：推进段用推穿、收束段用后拉冷却。
  与 [[black-slam-transition]] 的区别：那里相机硬停一拍（信号），这里相机软收（呼吸）。
- 剪辑软件对应物：剪映"运镜转场→拉远"类 + 前一镜的"亮度/模糊"关键帧；
  AE 是后镜 camera Z 从远处推近 + Easy Ease，前镜用 Exposure/Camera Lens Blur 关键帧；
  达芬奇里常与一次 rack focus + 色温 offset 同帧做。

## 动效范围
- 属于本卡的：出场侧**相机收住**（从 hold 的慢推 `sine.out` 减速到 `scale 1.0` 静止，不推不拉）
  + **内容层**沉暗失焦（`opacity 1→0.18` + `blur 0→2px`，`sine.in`，作用在主体面而非镜头层）；
  入场侧**全片唯一 scale<1 起步的后拉**（0.90→0.99 + `blur 4→0`，`power2.out`，`settle` 0.90s 是全六式最长）；
  交叠 0.55s（≈16 帧，全六式最长）的 `sine.inOut` 交叉淡化；切点提前量最小（0.05s，交接靠"暗"不靠"快"）；
  全程 sine 系缓动的呼吸质感；落点留 0.01 给 hold 期慢推（相机永不静止）。
- 不属于本卡的：两个镜头里的文字与配色（白/浅灰 tile + 灰字式名是"认式子的标签"，不是台词字幕）、
  左上说明角标、**沉暗的具体视觉**（深底=沉入近黑 / 白底=褪灰失焦，语义相同视觉不同）、
  **色温转冷**（常见同伴，但它在 `env.tsx` 的 `ACTS` 表里，属于环境层不属于本卡）、`.shot` 的 `inset:-14%` 具体数值。
- 迁移接口：时序全在 `CONFIG.pull`（`out`/`overlap`/`settle`/`cutLead` + `outDim`/`inScale`/`inSettle`）；
  换尺寸不用改（只有 scale 轴）；`outBlur`/`inBlur` 按输出分辨率线性缩放；
  沉暗深度按底色改（白底 `outDim: 0.18`，深底改成亮度趋零）——**沉暗必须挂在内容层**，
  换工程时把 `out.querySelector(".big")` 换成你的主体面容器；`inScale` 是本式的识别标志，
  别在片子别处再用 scale<1 起步。
- 底色要求：白底即可。沉暗的实现随底色变（白底褪灰、深底沉黑），但这是**场景内的内容动作**，
  不是叠加层，所以不像 [[overexpose-flip-transition]] 那样存在极性反转问题。相机曲线与底色完全无关。

<!-- ===== /file: video-talkcraft/references/cards/pullback-cool-transition.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/push-through-transition.md ===== -->

---
name: push-through-transition
标题: 推穿转场
一句话: 出场镜头相机加速推到 1.35x 同时升起失焦，切点后入场镜头从模糊的 1.16 高位反向沉降落位——两侧都在"推"这一条轴上，观众被推着穿过镜头边界
适用: 从概念推进到证据、从全景推进到细节的镜头边界；六式里最中性的一式，同一片可以反复用而不腻
时长: 出场加速推 0.55s → 交叠 0.45s（≈14 帧 @30fps）→ 入场沉降 0.60s；单次转场约 1.05s
能量: 中
类别: 转场结构
输入: 场
语义: 转场
素材形态: 无
位置: 中段
props: hostSrc(未使用)
优先级: P0
代码: template/cards/push-through-transition.tsx
---

## 意图
硬切翻页是 PPT 感四病根之一：Sequence 边界内容整体瞬换，观众被"扔"进新场景。
推穿是运动承接家族里的**基准式**——出场镜头把相机加速推出去，入场镜头以同一方向的余势接住再刹住，
观众读到的不是"换了一张图"，而是"我穿过去了"。它没有闪光、没有位移、没有粒子，只有一条 scale 轴，
所以最安全、最可反复使用，也是判断"这一版转场到底有没有动量"的对照组。

做对的命门：① **两侧同向**——出场推近（scale 变大）、入场必须从更大的 scale 往回沉降，
方向断裂（出场推近 + 入场从 0.9 拉出）比硬切更糟；② **淡化只管像素**——透明度包络和相机曲线彻底分开写，
运动全在相机上；③ **入场不要沉回 1.0 就撒手**——落点停在 1.03，紧接着的 hold 从这里继续慢推，进场即自带运动。

## 动效核心
时间结构（`at` = 出场镜头开始交出画面的那一刻，全在 `CONFIG.push` 里）：

| 阶段 | 时刻 | 出场镜头 | 入场镜头 |
|---|---|---|---|
| 加速推 | `at` → `at+0.55` | `scale 1.0→1.35` + `blur 0→7px`，`power2.in` | 静默，停在 `scale 1.16` + `blur 7px` |
| 切点 | `cut = at + 0.55 − 0.10` | 开始 0.45s 淡出 `power1.inOut` | 开始 0.45s 淡入 `power1.inOut` |
| 沉降 | `cut` → `cut+0.60` | — | `scale 1.16→1.03` + `blur 7→0`，`power2.out` |
| 交班 | `cut+0.60` 之后 | — | hold 期慢推（`sine.inOut`，从 1.03 继续 +0.04） |

- **切点提前 0.10s（`cutLead`）**：交叠期在出场推到顶之前就开始，出场镜头最快的一段和入场镜头的沉降重合，
  这段重合就是"承接"本身。若把切点放在出场推完之后，中间会出现一帧两边都不在动的空档，动量断掉。
- **加速用 `power2.in`、沉降用 `power2.out`**：出场是"越来越快地离开"，入场是"越来越慢地落定"，
  两段缓动首尾相接读作一次连续的加速—减速，这是 match-on-action 的时间形状。
- **失焦是速度的证据**：`blur` 与 scale 同曲线升降；只推不糊会像 Keynote 的 Magic Move，糊了才有镜头感。
- **镜头层要超出画幅**：demo 里 `.shot { inset: -14% }`（对称 inset ⇒ 画面中心不变），
  推近/沉降时不漏白边；Remotion 里等价于场景自己用 `AbsoluteFill` 铺满，相机变换加在外层 rig 上。

Remotion 对应写法（`template/motion-systems/transitions.tsx`，生成器直接 spread 进 `shots.ts` 的 `path`）：

- 出场 shot（叙事末尾 tEnd 秒起加速推）：`{ tail: 14, path: [{t:0, scale:1.06}, ...pushThroughOut(tEnd)] }`
- 入场 shot（lead 内从模糊高位起步，settle 秒沉降到工作景别）：`{ lead: 14, path: [...settleIn(leadSec), {t:9, scale:1.0}] }`
- `pushThroughOut(tEnd, {from:1.06, to:1.2, blur:7, dur:0.5})` 生成两个 CamKey；`settleIn(leadSec, {from:1.14, to:1.04, blur:6, settle:0.5})` 的第一个键 `t` 取负（落在 lead 里）。
- 像素淡化交给 `<ShotFade lead tail narrationFrames>`，不要把位移写进去。

## 参数表
| 参数 | 典型值 | 调节手感 |
|---|---|---|
| 交叠帧数 `overlap` | 0.45s ≈ 14 帧 | <10 帧读作硬切；>20 帧两场糊在一起，谁都看不清 |
| 出场加速时长 `out` | 0.55s | <0.3s 从静止直接甩=没有预备拍，观众跟不上；>0.8s 读作"慢慢放大"而不是推穿 |
| 出场推到多大 `outScale` | 1.35 | 1.15 以下动量不够、读作轻微缩放；>1.6 是过曝翻页的量级，该换那一式 |
| 切点提前量 `cutLead` | 0.10s | 0 = 出场推完才切，中间一帧静止把动量掐断；>0.2s 交叠吃掉加速段，推的感觉没建立起来 |
| 入场起手景别 `inScale` | 1.16 | =1.0 就没有反向沉降（等于淡入）；>1.3 沉降路程太长，落位拖沓 |
| 失焦峰值 `outBlur/inBlur` | 7px | 0 读作 PPT 缩放；>12px 交叠期糊成一团，观众丢失空间连续性 |
| 入场落点 | 1.03（不是 1.0） | 落到 1.0 再静止 = 撞墙；留 0.03 给 hold 继续推，进场即自带运动 |

## 已知坑
- 两侧曲线各写各的忘了对方向：出场推近、入场从 0.9 拉出——方向断裂，比硬切更刺眼。
- 把运动写进 `ShotFade`：透明度和位移耦合，改一处坏两处，且没法单独调交叠帧数。
- 只推不糊：`blur` 全程 0，读作 Keynote Magic Move，没有镜头速度。
- 入场沉降到 1.0 后彻底静止：撞墙感，紧接的 hold 必须接着推/漂。
- 镜头层没铺过画幅：推近时四周漏底色（白底上是白边，一眼穿帮）。
- lead 补偿漏算：入场侧相机片段的 `t` 忘了取负，沉降从叙事第 0 帧才开始，交叠期入场镜头是静止的。

## 复用指引
- props：仅 `hostSrc`（声明未使用）；两个镜头为 JSX 写死的 tile，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/push-through-transition.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：`demos/push-through-transition/index.html`。核心是 `pushThrough(出场镜头, 入场镜头, 起始秒) → 转场结束秒`
  一个函数 + `CONFIG.push` 一组参数，整段可直接摘走；`hold()` 是镜头停留期的慢推，也一起摘（没有它转场两端会撞墙）。
- Remotion：`template/motion-systems/transitions.tsx` 的 `pushThroughOut` / `settleIn` spread 进 `shots.ts` 的 shot `path`：
  `path: [...settleIn(0.47), {t:9, scale:1.0}, ...pushThroughOut(18.4)]`；shot 间 lead / tail 交叠机制见 `shots.ts` 文件头注释。
- 与家族其他式的关系：推穿是基准式，**加重音层**就是 [[overexpose-flip-transition]]（推到 1.5x + 闪光），
  **换成横轴**就是 [[whip-pan-transition]]，**反向**就是 [[pullback-cool-transition]]。同一个边界只用一式。
- 帧级压缩版（实测，真实竖屏口播）：**crash-zoom 甩镜**（Apm_oCzPEQs）= 出场 2~3 帧内相机猛推到 1.4x 以上并叠拖影，
  入场接住余势后拉刹住——推穿的暴力版，总时长压到 0.1~0.2s，用在最强反转句上，一片一次。
- 剪辑软件对应物：剪映"运镜转场→推近"类；AE 是手 K 两侧 camera null 的 Z 位移 + Camera Lens Blur——本卡把手 K 固化成了参数。

## 动效范围
- 属于本卡的：相邻镜头交叠 0.45s（≈14 帧）、两侧同时在动的时间结构；出场侧 `scale 1.0→1.35` + `blur 0→7px` 的
  `power2.in` 加速推；入场侧从 `scale 1.16` + `blur 7px` 反向沉降到 1.03 的 `power2.out`；
  切点提前 0.10s 让加速段与沉降段重合；透明度包络（0.45s `power1.inOut` 交叉淡化）与相机曲线分离；
  入场落点留 0.03 余量交给 hold 期的慢推（`sine.inOut`，相机永不静止）。
- 不属于本卡的：两个镜头里的文字与配色（demo 用白/浅灰 tile + 灰字式名只为区分"换了一镜"并标出正在演哪一式，是标注不是台词字幕）、
  左上说明角标、`.shot` 的 `inset:-14%` 具体数值（按最大 scale 折算即可）。
- 迁移接口：时序全在 `CONFIG.push`（`out` 出场 / `overlap` 交叠 / `settle` 入场 / `cutLead` 切点提前量）；
  换尺寸不用改（本式只有 scale 轴，与画幅无关）；改动量强度只动 `outScale` + `inScale` 这一对，
  **且必须同时同向**（出场变大、入场从更大处沉降）；`blur` 按输出分辨率线性缩放（1080p 用 7px，4K 用 14px）。
- 底色要求：白底即可。本式不含叠加层，相机曲线与底色完全无关。

<!-- ===== /file: video-talkcraft/references/cards/push-through-transition.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/quote-bracket-pull.md ===== -->

---
name: quote-bracket-pull
标题: 引号夹句
优先级: P1
代码: template/cards/quote-bracket-pull.tsx
一句话: 两枚压过正文三倍的大引号从画外对角**同帧**向内推入把一片空白夹成"引文区"，引号走过一半时三行金句才开始错峰 0.09s 淡入上浮，末行关键短语最后被荧光笔扫过 0.26s
适用: 金句要"被引用"的时刻——引别人的话、复述观众留言、把自己的一句话立成引文；不想遮住人物的金句（本卡不盖底板，人物全程在画面里）；克制调性的知识区/访谈类口播。不适合需要"让位仪式"的暴论式金句（那用 quote-card）
时长: 起手静置 0.35s → 双引号同帧推入 0.32s → 三行错峰淡入 0.48s → 荧光笔扫 0.26s → 收尾 hold 2.2s；共约 3.6s
能量: 中
类别: 字幕花字
输入: 文, 人(可选)
语义: 引用, 金句
素材形态: 无
位置: 任意
props: hostSrc
---

## 意图
本库已有 `quote-card`（金句大字卡），它的机制是**让位仪式**：底板盖住人物、字占全屏、
逐行砸出来、停 2~4s、整卡下滑退场。它很有力，但代价是**人物消失了**，
而且整屏被接管——所以它一条视频只能用一两次，用多了每次都像"要开始念圣经了"。

这张卡解决的是同一个需求的另一半：**我想把一句话立成引文，但不想中断口播**。
它的机制完全不同——不盖底板、不动人物，而是用**两枚大引号夹住一片空白**，
在画面里现场划出一个"引文区"。观众读到的不是"画面停下来了"，而是"这句话被打上了引号"。
这是排版的语言（引用），不是舞台的语言（让位）。

与 `quote-card` 的三条硬区别，复用时别混：① **无底板、人物不退场**；② **引号是主动作**
（字是被夹出来的，不是自己砸出来的）；③ **错峰更密**（0.09s vs 0.15s）——本卡三行是**一句话**，
`quote-card` 的行是**逐句砸**。

命门两条：① **引号必须同帧同曲线**。这是"夹"这个动作的全部——两枚哪怕错开 3 帧，
就读作"两个符号各自飞进来"，构图当场散架；② **引号要立得住**：尺寸压过正文两倍以上
（demo 是 108px vs 32px，3.4 倍）、`opacity` 到 0.85~0.9。太小或太淡它就退化成装饰角标，
"引用"这层意思没有了。

## 动效核心
- **层级**：白底 → 人物（左下角标，全程不动）→ 金句块（版心，`width: fit-content` 贴合最长行）
  → 两枚大引号（绝对定位在金句块的左上 / 右下外侧）→ 荧光笔色块（在末行文字**下层**）
- **① 双引号推入（本卡的主动作）**，两枚**同帧同曲线** `0.32s power3.out`：
  - 左引号：`x −30 → 0`、`y −14 → 0`、`opacity 0 → 0.9`
  - 右引号：`x +30 → 0`、`y +14 → 0`、`opacity 0 → 0.9`（位移**反向对称**，这是"夹"的几何）
  - 尺寸 108px / 700 字重 / 衬线族（Georgia）——衬线的引号字形本身就有"引文"的文化编码
- **② 三行金句**：在引号**走过一半时**起（`lead + markDur × 0.5`，不空等），
  `opacity 0 → 1` + `y +6 → 0`，每行 `0.30s power2.out`，**错峰 0.09s**。
  上浮只有 6px：一点重量而已，位移大了就抢过引号的"夹"
- **③ 荧光笔**（末行到位 + 0.10s 呼吸后）：`scaleX 0 → 1`，`transform-origin: left center`，
  `0.26s power2.inOut`。`#FFE949` @ `opacity 0.6` + `mix-blend-mode: multiply`
  （design-language §1 的 marker token），不规则圆角 `9px 4px 8px 3px / 5px 9px 4px 8px` 模拟笔触。
  **色块在字下层**（`z-index` 与 DOM 顺序双保险），不许盖字
- **④ hold 2.2s**：金句要停。这是本卡最长的一段，比任何动作都长
- **落位纪律**：金句块用 `width: fit-content` 而不是固定宽——引号是绝对定位在**块的边缘**上的，
  块宽固定时引号会被钉在版心角落，离句子太远，"夹"的关系就断了

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 引号字号 | 108px（正文的 3.4 倍） | **命门**：引号的分量；<正文 2 倍读作装饰角标（"引用"语义消失），>正文 4.5 倍引号成了主角、句子变成配图 |
| `markOpacity` | 0.9 | 引号落定不透明度；<0.8 读作水印（分量不够压不住构图），1.0 时引号与正文一样黑、读作"句子里有两个大符号" |
| `markDx` / `markDy` | 30 / 14px | 引号推入距离，**两枚必须反向等值**；0 只剩淡入（"夹"这个动作没有了），>60px 读作两个符号从远处飞来（抢过整句） |
| `markDur` | 0.32s | 引号推入耗时，本卡的主动作时长；<0.2s 读作硬现（夹的过程看不见），>0.5s 观众等着两个符号就位、句子还没开始 |
| 引号错峰 | **0 s（严格同帧）** | **第一命门，不是可调参数**；错开 3 帧就读作"两个符号各自入场"，构图散架 |
| `lineStagger` | 0.09s | 行错峰；本卡刻意比 `quote-card`（0.15s）更密——三行是**一句话**不是三句；>0.15s 读作逐句砸（就该用 quote-card 了），<0.05s 整块淡入（少了阅读推进） |
| `lineRise` | 6px | 行上浮位移；>16px 行的入场分量超过引号，主次颠倒 |
| 起字时机 | 引号走完 50% | 引号到位后再起字会读作两个断开的动效；0%（同时起）读作"一整块淡入"，夹的动作被埋掉 |
| `markerDur` | 0.26s | 荧光笔扫过耗时；跟朗读语速走，<0.15s 像 bug 闪一下，>0.5s 拖过了口播的重音点 |
| 行数 | 2~4 行 | 3 行最舒服；>4 行引号要拉得太开、"夹"的张力松掉（且金句超过 4 行就不是金句了） |
| `hold` | 2.2s | 收尾停留，**本卡最重要的一段**；<1.5s 观众读完就切、金句没有余味；金句的价值全在这段静止里 |

## 已知坑
- 两枚引号错峰入场（做"依次夹住"）——**本卡最致命的错法**。"夹"是一个动作，
  必须由两个同步的位移共同完成；错峰后读作两个独立符号飞入，构图散架。
- 引号字号只比正文大一点（1.3~1.8 倍）——退化成"句子里的标点"，
  观众根本不会把它读作"引用"这个动作。
- 引号用 `opacity: 0.4` 求"轻盈"——变成水印，压不住构图；引号是**符号不是装饰**，
  0.85~0.9 是它的下限。
- 引号用无衬线族（跟正文同族）——无衬线的 `"` 是两个小竖块，放大到 108px 只是两个方块；
  衬线族的引号字形自带"引文"的文化编码，这是免费的语义。
- 金句块用固定宽度——引号被钉在版心角落，离句子十几个字宽，"夹住"的关系断掉
  （必须 `width: fit-content` 贴合最长行）。
- 荧光笔不用 `multiply` 或色块盖在字上层——黄块把字压成灰，"划重点"变成"涂掉"。
- 荧光笔用规则圆角（或直角矩形）——读作文本选区/背景色，不是笔触。
- 一句里划两处以上荧光笔——行行有高亮等于没有高亮（同 `quote-card` 的坑）。
- 加了底板盖住人物——那就是 `quote-card` 了，本卡的全部价值在于"不中断口播"。
- 引号做入场后还继续动（漂移/呼吸）——引号是符号，落定后必须绝对静止
  （design-language §4：画完/落定的元素保持干净静置）。
- hold 砍到 1s 以内——本卡的三个动作（夹 / 出字 / 划线）加起来才 1.06s，
  hold 比它们的总和还长才对；砍掉 hold 等于砍掉金句本身。

## 复用指引
- props：仅 `hostSrc`；三行金句与荧光笔关键短语在 JSX 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/quote-bracket-pull.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/quote-bracket-pull/index.html。**换内容改 `.qb-line` 的三行文案**
  （荧光笔的关键短语用 `.qb-mark-wrap` 包住即可，色块宽度自动贴合）；
  行数增减直接加删 `.qb-line`（错峰是 `stagger` 算的，不用改 delay），
  但引号的落位 `top/bottom` 要跟着微调（`.qb-mark.open` 的 `top`、`.close` 的 `bottom`）。
  **引号字号跟着正文字号等比**（正文 32px ⇒ 引号 108px，即 3.4 倍）；换字号时两个都要改。
  节奏只调 `markDur`（主动作）与 `hold`（余味），`lineStagger` 是手感常量。
  不要碰"两枚引号写在同一个 `tl.to([open, close], ...)` 里"这件事——那一行就是第一命门的实现。
- Remotion 移植：两枚引号**必须写在同一个 `interpolate` 局部时钟上**
  （`const p = interpolate(frame, [0, 10], [0, 1], {easing: Easing.out(Easing.cubic), extrapolateRight: "clamp"})`，
  然后左引号 `translate(${-30*(1-p)}px, ${-14*(1-p)}px)`、右引号乘 `+1`）——
  共用一个 `p` 是"同帧同曲线"的结构保证，分成两个 Sequence 早晚会被人改出错峰。
  三行各一个 `<Sequence from={Math.round((5 + i*2.7) * 1)}>`（@30fps：引号 10 帧，第 5 帧起字，行错峰 ≈2.7 帧，取整 3）；
  荧光笔用 `scaleX` + `transformOrigin: "left center"`，`mixBlendMode: "multiply"` 在 Remotion 里正常工作。
- 剪辑软件对应物：剪映/CapCut——两枚引号做成两个文本层，**同时打关键帧**
  （框选两层一起打，别一层一层做，手动做必然错峰）；三行文字三层"位置 + 不透明度"，
  逐层往后拖 3 帧；荧光笔用一个黄色矩形贴纸 + 缩放（横向）关键帧 + 图层混合模式设"正片叠底"，
  锚点拖到左端（默认中心锚点会让色块从中间往两头长，那是 `quote-hold-arrow` 的语言）。
  AE——两枚引号父级绑到**同一个 Null**，只给 Null 打一组 `Position` 关键帧，
  引号各自用 `Scale` 的 x 轴 ±100 做镜像（这样"同帧"是结构强制的，不靠手动对齐）；
  荧光笔用 Shape Layer 矩形 + `Scale` x 关键帧 + 图层混合模式 `Multiply`。
- 与本库同类卡的分工（**必读，两张金句卡容易混**）：
  - `quote-card` = **让位仪式**（底板盖住人物、整屏接管、逐句砸、行错峰 0.15s、出场下滑）。
    用在观点峰值、暴论、片尾收束；一条视频最多用一两次。
  - **本卡 = 排版式引用**（不盖板、人物不退场、引号夹出引文区、行错峰 0.09s、无出场动作）。
    用在引别人的话、念留言、把一句话立成引文；克制，同一条视频里可以用两三次。
  - `quote-hold-arrow` = **金句的第三种**：三行里**只有末行升级**（先平淡后高亮 + 箭头），
    重点是"这一句里的这一行"，不是整段引文。
  - `tracking-in` = 单行大标题的一次性入场（一行字的标题动作）；
    `highlighter-sweep` = 只做荧光笔那一下（在已有文档/长文上划重点，不带引号构图）。

## 动效范围
- 属于本卡的：两枚大引号**同帧同曲线**从对角向内推入（`x ∓30 / y ∓14 → 0` + `opacity 0→0.9`，`0.32s power3.out`）这个"夹"的动作——**同帧是本卡的结构，不是参数**；引号尺寸必须压过正文两倍以上、`opacity` 落在 0.85~0.9 这条"符号不是装饰"的分量纪律；引号走完 50% 才起字这个交叠时机；三行 `opacity` + `y +6→0` 的 `0.09s` 密错峰（区别于 `quote-card` 的 0.15s 逐句砸）；末行荧光笔 `scaleX 0→1 origin left` 走 `0.26s`、色块在字下层用 `multiply`、不规则圆角模拟笔触；`hold 2.2s` 比全部动作总和还长这条比例；**不盖底板、人物不退场**这条构图前提。
- 不属于本卡的：demo 那三行具体金句与「主动去解决问题」这个关键短语、32px 正文 / 108px 引号的绝对值（比例才是本体）、Georgia 这个具体衬线族、`#1d1d1f` 墨色、金句块落在版心偏上、左下角标数字人占位、`#FFE949` 之外的任何配色、白底舞台。
- 迁移接口：内容入口是 `.qb-line` 的文案与行数（荧光笔用 `.qb-mark-wrap` 包关键短语）；**引号与正文的字号比是 3.4:1**，换字号时两者等比同改（引号落位 `top/bottom` 跟着字号线性缩放）；`markDx/markDy` 按舞台宽等比（960 ⇒ 1920 时翻倍），两者**必须保持 30:14 的反向对称**；`lineStagger 0.09s` 是手感常量（换语速也不动）；`hold` 按字数给（每字约 0.1s，下限 1.5s）；竖屏把行数收到 2~3 行、正文降到 28px（引号跟着到 95px），引号落位改成"左上 / 右下贴块边缘"不变。
- 底色要求：**白底即可**。深底也成立，换值：正文与引号反白到 `#f5f5f7`（引号 `opacity` 仍 0.9），荧光笔的 `mix-blend-mode` 必须从 `multiply` 换成 `screen`（深底上 multiply 会把黄块乘成黑，划线直接消失）。唯一约束是底不能有画面元素落在引号位（引号在金句块外侧 30~40px 处，那两块区域必须是净空）——引号压在人物或素材上时，观众读不出它是符号，会当成画面里的图形。

<!-- ===== /file: video-talkcraft/references/cards/quote-bracket-pull.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/quote-card.md ===== -->

---
name: quote-card
标题: 金句大字卡
一句话: 说到金句时底板 0.25s 盖住人物，3~5 行大字自上而下逐行错峰弹出，关键词换色放大，停 2~4s 后整卡下滑退场
适用: 口播的观点峰值（金句、结论、暴论）；商业类/情感类竖屏口播的招牌收束动作，罗翔式纯黑白变体适合严肃调性
时长: 底板 0.25s（0.15s 起）+ 四行逐行入场 0.35→1.20s（行错峰 0.15s、单行 0.4s）+ hold ≈2.2s（退场起点 `outAt` 写死 3.40s；真实口播 2~4s）+ 出场 0.3s；共约 3.7s
能量: 中
类别: 字幕花字
输入: 文, 人(可选)
语义: 金句, 结尾
素材形态: 无
位置: 任意
props: hostSrc
优先级: P1
代码: template/cards/quote-card.tsx
---

## 意图
金句值得一个"让位仪式"——人先退场、字占全屏，观众才知道这句话是本条视频的钱。
命门：**底板要实**（透明度不够，文字和人物打架，仪式感归零）、**逐行不逐字**（行是节奏单位，
行内再加字级动画就花了）、**关键词只挑 1~2 个**（行行有高亮等于没有高亮）。

常见于：张琦/参哥类商业口播、罗翔（黑屏白字版）、何同学（白底黑字版）、抖音大字报片型。

## 动效核心
- 层级：人物层在底，`.quote-panel` 整屏底板（实底，demo 用灰阶 #1d1d1f）盖上
- 入场：底板 opacity 0→1，0.25s power2.out；同时人物被盖即"压暗"
- 正文：3~5 行大字（demo 4 行），每行 y 30px→0 + opacity 0→1，0.4s power3.out，行间 stagger 0.15s（`lineStagger`，可调 120~180ms）
- 关键词：行内 span 换高亮色（#ffd23e）且 font-size 1.2em——静态样式，不参与动画
- 出处小字延迟最后一行约 0.2s 淡入
- 出场：整卡 opacity→0 + y +40px，0.3s power2.in，直接回到人物
- 人物让位的另一种处理：不整屏盖住而是把人物**缩到一角**（缩角），底板仍是实底——压暗或缩角都成立，关键是字占全屏

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 底板不透明度 | 1（实底） | <0.9 人物透出来和文字打架；全实底才有"让位"感 |
| 行错峰 | 150ms | >250ms 像逐条列表不像一句话；<80ms 读作整段淡入 |
| 单行入场 | 0.4s | >0.6s 拖沓；<0.25s 行与行的先后关系看不出来 |
| 行数 | 3~5 行 | 超过 5 行就不是金句是段落，观众不读 |
| `outAt` 退场起点（= hold 长度） | 3.40s（末行 1.20s 落定 → hold ≈2.2s；真实口播 2~4s） | 跟着语速走：读完 +0.5s 就切，多留一秒都是空气。tsx 里 `outAt` 是组件内常量，`CONFIG.hold` 未接线 |
| 出场 | 0.3s 下滑 | 出场比入场轻；用弹跳出场会抢金句本身的余味 |

## 已知坑
- 行行都加弹跳/行内再加字级动画——重音互相打架，一眼廉价感。
- 金句超过 5 行——大字排不下就缩字号，缩了字号就不是大字报。
- 底板半透明看得见人物——文字浮在人脸上，读作弹幕不是金句卡。
- 出场用花哨转场——金句的余味在静，出场越轻越高级。

## 复用指引
- props：仅 `hostSrc`；金句四行、关键词 `.kw` 与出处在 JSX 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/quote-card.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。退场起点是组件内常量 `outAt = 3.40`（`CONFIG.hold` 未接线），改 hold 直接改 `outAt`。
- HTML/GSAP：demos/quote-card/index.html，改 `.quote-line` 文案与 `.kw` 位置即可换句子；节奏全在 `CONFIG`（panelIn/lineStagger/hold）。罗翔变体：底板换纯黑、去掉 `.kw` 色彩、行入场只留 opacity。
- Remotion 移植：每行一个 `<Sequence from={i*5}>` + `spring({damping:200})` 驱动 y/opacity；hold 用 Sequence duration 控制；出场 interpolate(frame, [out, out+9], [0, 40])。
- 剪辑软件对应物：剪映"文字模板→大字报"；CapCut "quote card"; AE 里是文本层 position/opacity 关键帧 + 纯色层做底板。

## 动效范围
- 属于本卡的：底板 opacity 0→1 盖住人物层的**遮蔽动作**（0.25s、power2.out，必须是实底）；正文 3~5 行各 `y 30→0 + opacity 0→1`（0.4s、power3.out）、行间 stagger 120~180ms 的自上而下逐行错峰；出处小字延迟最后一行约 0.2s 淡入；hold 2~4s；整卡 `opacity→0 + y +40px` 下滑退场（0.3s、power2.in）。纪律部分同属本卡：**逐行不逐字**（行是节奏单位，行内关键词只做静态换色放大、不参与动画）。
- 不属于本卡的：主持人剪影占位、示例金句与出处文案、字号 42px / 字重 800 / 字距、底板与关键词的具体色值（黑底白字 / 白底黑字 / 罗翔式纯黑白都成立）。
- 迁移接口：`panelIn` 定盖板速度，`lineStagger`/`lineIn` 定逐行节奏，`outAt`（tsx 退场起点）跟语速走，`out`/`outDrop` 定退场；换风格只改底板 background + 行文字 color + `.kw` 高亮色三个值（反色变体：底板换 #ffffff、文字换 #1d1d1f）；换尺寸时字号与 `lineRise`/`outDrop` 按画幅短边等比缩放。
- 底色要求：**需要与舞台底色有明度反差的实底板**（例外）。理由：本卡的核心动作是"底板盖住人物、字占全屏"的让位仪式——底板若与舞台同为白，遮蔽动作在画面上不可见，动效等于没发生。demo 取最中性的灰阶深底 #1d1d1f（无色相、不引入品牌色）。复用者反过来配也成立（白底板 + 深色人物层），关键是**反差本身**，不是深浅方向。

<!-- ===== /file: video-talkcraft/references/cards/quote-card.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/quote-hold-arrow.md ===== -->

---
name: quote-hold-arrow
标题: 金句停留
优先级: P1
代码: template/cards/quote-hold-arrow.tsx
一句话: 三行金句先全部以普通样式错峰淡入、末行原地平淡地停 0.34s，然后才**升级**——黄色高亮框从末行文字中心 scaleX 铺开 0.24s、框到位后文字 punch 一下，然后停住
适用: 口播里"话到这儿才是重点"的时刻——铺垫两句后落到结论、转折句、行动号召前的那一句；需要观众记住**整句里的哪一句**（不是哪个词）的场合。不适合一上屏就要砸的钩子句（那没有铺垫可升级）
时长: 起手静置 0.4s → 三行错峰淡入 0.52s → 末行平淡停 0.34s → 高亮框铺开 0.24s + punch 0.17s → 收尾 hold 2.2s；共约 3.9s
能量: 中
类别: 强调标注
输入: 人(可选), 文
语义: 金句, 转折
素材形态: 无
位置: 任意
props: hostSrc
---

## 意图
金句卡通常犯一个错：**一上屏就高亮**。三行字里第三行自带黄框飞进来——观众看到的是
"一张已经排好的图"，读作设计，不读作叙事。而口播的真实节奏从来不是这样：主播先说两句铺垫，
说到第三句时**语气才变**，那一瞬间观众才知道"哦，前面都是为了这句"。

这张卡把那个"语气变了"的瞬间做成了动效：**末行先以普通样式落地、平淡地停一拍，然后才升级**。
观众的体验是两段的——先读到一段平铺的话，再看到其中一行被点亮。这个"后知后觉"的结构
就是本卡的全部价值：它复现了**口播里重点浮现的时间顺序**，而不是把结论直接贴出来。

两个动作各有分工，别混：**框**说"是这一行"（范围）；**punch** 说"就是现在"（时间点）。
框先到、字后应，顺序不能改。

**2026-08-26 用户定版：去掉了原来第三拍从框右缘伸出的箭头。**
理由：金句的落点是"这一句被点亮、然后停住"——箭头把视线从句子引向画外，
反而削掉了那 2.2s 停留的余味；它还要在末行右侧占掉 104px 版面，而那正是人物站的位置。
要"往下一步去"的指向，用独立的转场卡去做，不要塞进金句里。

命门两条：① **末行必须两拍**（平淡 → 升级），中间那 0.34s 是本卡唯一不可省的空白；
② **框在文字下层、文字保持黑字**——这是荧光笔语义（在纸上划过），不是反白 chip（把字放进色块里）。
后者是 `alt-block-lines` / `slab-punch-title` 的语言，读法完全不同。

## 动效核心
- **层级**：白底 → 人物层（右列）→ 三行金句（左侧，垂直居中）→ 末行：高亮框（`z-index: 0`）
  在**文字下层**（`z-index: 1`）
- **① 三行淡入（第一拍：全部平淡）**：`opacity 0 → 1` + `y +8 → 0`，每行 `0.28s power2.out`，
  错峰 `0.12s`。**此刻末行与前两行一模一样**——没有框、没有色、没有重音
- **② 平淡停留 `0.34s`（本卡的命门空白）**：什么都不发生。这一拍让观众把三行当成一段话读完
- **③ 末行升级**：
  - 高亮框 `scaleX 0 → 1`，`transform-origin: 50% center`（**从文字中心向两侧铺开**），
    `0.24s power3.out`。`#FFE949` @ `opacity 0.62` + `mix-blend-mode: multiply`
    （design-language §1 的 marker token），不规则圆角 `11px 5px 9px 4px / 6px 11px 5px 9px` 模拟笔触
  - **框到位后**文字 `scale 1.05 → 1` punch，`0.17s`（5 帧 @30fps）`power2.out`，
    `transform-origin: 50% 50%`。框先到、字后应——反了读作"字被框追上"
- **④ hold 2.2s**：金句要停——punch 落定就是本卡的落点，后面不再有任何动作
- **总时长账**：`0.4 + (0.12×2 + 0.28) + 0.34 + 0.24 + 0.17 + 2.2` ≈ 3.9s

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `plainHold` | 0.34s | **第一命门**：末行"平淡"停留时长；0 时框跟着字一起来，两拍并成一拍——"重点在这一句"的推进感直接消失（就变成一张排好的图）；>0.8s 观众以为动效结束了，升级读作第二个动效 |
| `lineStagger` | 0.12s | 三行错峰；>0.2s 读作逐句砸（抢过升级那一拍），<0.06s 整块淡入（可用，但少了阅读顺序） |
| `hlDur` | 0.24s | 高亮框铺开耗时；跟朗读语速走，<0.15s 像 bug 闪一下，>0.45s 框还在长、口播已经念完这句了 |
| 框 `transform-origin` | `50% center`（中心） | **本卡与 `highlighter-sweep` 的分界**；改成 `left center` 就变成"从左划过"（阅读式划线，跟着朗读走）；中心铺开读作"这一整行被框住"（结论式，一次成型） |
| `punchScale` | 1.05 | 文字 punch 起始倍数；<1.03 看不出重音，>1.12 读作字要跳出框（框与字脱钩） |
| `punchDur` | 0.17s（5 帧） | punch 时长；>0.3s 读作整行在缩放（不是重音是动画），必须短 |
| punch 时机 | 框**到位后** | **不许与框同时**；同时发生读作"字被框追上"，框先到、字后应才是"框住了，所以这句重" |
| `hold` | 2.2s | 收尾停留；金句的余味全在这段静止里，<1.5s 观众刚读完就切 |

## 已知坑
- **多行是"块级外壳 + 内层 inline-block"两层结构**（2026-08-27 实战补）：高亮框要贴文字宽，
  所以内层必须 `inline-block`；但几行 inline-block 会**横向流成一行**（实测三行金句塌成一行）。
  每行外面再包一层块级 div。
- 末行一上屏就带框——**本卡最致命的错法**。两拍并成一拍后，观众读到的是一张排好的图，
  "重点在这一句"这个叙事完全消失（这时你其实该用 `keyword-pop-highlight` 或直接静态排版）。
- 框铺开与文字 punch 同帧——读作"字被框追上"。框先到位、字才应答，
  这半拍的先后是"因为被框住了所以这句重"的因果。
- 框做成实色反白 chip（黄底白字/黄底黑字盖住原字）——那是**色块语言**
  （`alt-block-lines` / `slab-punch-title`），读作"这行字坐在一个块上"；
  荧光笔语言是"字还在纸上，纸被划了一道"，两者的叙事完全不同。
- 框不用 `multiply`（或盖在字上层）——黄块把黑字压成灰，"划重点"变成"涂掉"。
- 框用规则圆角/直角——读作文本选区或背景色，不是笔触。
- `transform-origin` 忘了改成中心（用了默认或 `left`）——那是 `highlighter-sweep` 的
  "跟着朗读划过"，本卡要的是"一次框住这一整行"的结论感。
- 前两行也加了高亮/重音——三行都重就没有重点，本卡的结构是"两行铺垫 + 一行结论"。
- 在 punch 之后再补任何动作（箭头、下划线、图标）——那 2.2s 停留就是本卡的落点，加东西等于把余味填满。

## 复用指引
- props：仅 `hostSrc`；三行文案在 JSX 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/quote-hold-arrow.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/quote-hold-arrow/index.html。**换内容改 `.qh-line` 三行文案**
  （末行的字放在 `.qh-last-txt` 里，框会自动跟着宽度走）。
  节奏只调 `plainHold`（两拍之间的空白，本卡的能量旋钮）与 `hold`（余味）。
  想把框改成"跟着朗读划过"：
  `.qh-hl` 的 `transform-origin` 改 `left center` —— 但那就变成 `highlighter-sweep` 了，
  别在同一条视频里两种混用。
- Remotion 移植：三行各一个 `<Sequence from={Math.round(i*0.12*fps)}>`。
  升级那一拍单独一个 `Sequence from={upFrame}`（`upFrame = 三行结束帧 + Math.round(0.34*fps)`）：
  框 `interpolate(f, [0, 7], [0, 1], {easing: Easing.out(Easing.cubic), extrapolateRight: "clamp"})`
  驱动 `scaleX` + `transformOrigin: "50% center"`；punch 从第 7 帧起
  `interpolate(f, [7, 12], [1.05, 1], {easing: Easing.out(Easing.quad), extrapolateLeft: "clamp", extrapolateRight: "clamp"})`
  （**两头 clamp 都不能省**——不 clamp 时 `f < 7` 会算出 >1.05 的 scale，末行开场就是放大的）。
  `mixBlendMode: "multiply"` 在 Remotion 渲染里正常工作。
- 剪辑软件对应物：剪映/CapCut——三行文本层各打"位置 + 不透明度"关键帧，逐层拖 4 帧；
  末行**要在第一拍之后**再加一个黄色矩形贴纸，打"缩放（横向）"关键帧
  且**锚点保持在中心**（剪映默认就是中心，这次刚好对）+ 混合模式设"正片叠底"；
  punch 用末行文本层的"缩放"两键（105% → 100%，5 帧，缓出）。
  AE——末行文本层 + 一个 Shape Layer 矩形（`Scale` x 从 0 到 100，锚点在中心）+ 混合模式 `Multiply`；
  两个动作用 `plainHold` 的帧数在时间轴上手动隔开（这是本卡唯一需要盯着的对齐）。
- 与本库同类卡的分工：
  - `highlighter-sweep` = **只做荧光笔那一下**，从左划过（跟着朗读走），用在长文/文档上划重点，
    没有"两拍升级"的结构。
  - `keyword-pop-highlight` = 一句里砸**一个词**（词级重音）；本卡强调的是**一整行**。
  - `quote-card` = 让位仪式（底板 + 整屏接管 + 逐句砸）；`quote-bracket-pull` = 排版式引用
    （双引号夹出引文区，整段等重）；**本卡 = 三行里只有末行升级**（有铺垫、有转折）。
  - 一句话选卡：**要划一段文档里的话 → highlighter-sweep；要砸一个词 → keyword-pop-highlight；
    要立整段引文 → quote-bracket-pull；要"铺垫两句然后落到这一句" → 本卡。**

## 动效范围
- 属于本卡的：**末行"先平淡、后升级"的两拍结构**（中间 `plainHold 0.34s` 的空白是本卡的本体）；三行 `opacity` + `y +8→0` 的 `0.12s` 错峰淡入（第一拍里末行与前两行完全同款）；高亮框 `scaleX 0→1` 从**文字中心**铺开（`0.24s power3.out`）、在字**下层**用 `multiply`、不规则圆角模拟笔触、文字保持黑字这条荧光笔语义；**框到位后**文字才 punch（`1.05→1`，5 帧）这个先后因果；punch 落定即收、后面 `hold 2.2s` 不再有任何动作这条纪律。
- 不属于本卡的：demo 那三行具体金句与「是因为你正在走出舒适区」这个末行、33px 字号与 600 字重、`#1d1d1f` 墨色、`#FFE949` 之外的配色、金句落在左侧（右列让给人物）、右列的数字人占位、白底舞台。
- 迁移接口：内容入口是 `.qh-line` 的三行文案（末行包在 `.qh-last-txt` 里）；能量只调 `plainHold`（两拍之间的空白）与 `hold`（余味），`lineStagger` / `punchDur` 是**手感常量，换尺寸换语速都不要动**；尺寸基准 —— 框的 `left/right/top/bottom` 外扩量（12/14/4/4px）按字号等比、`lineRise 8px` 按舞台高等比；颜色两个 token —— marker（`#FFE949` @0.62）与 ink；竖屏把行数保持 3 行但字号降到 28px（框跟着等比）。
- 底色要求：**白底即可**。深底也成立，换两处：文字反白到 `#f5f5f7`，且荧光笔的 `mix-blend-mode` 必须从 `multiply` 换成 `screen`（深底上 multiply 会把黄块乘成黑，高亮框直接消失）——注意深底 + `screen` 后黄框会显著更亮，`opacity` 要从 0.62 收到 0.45 左右，否则框比字亮、读作"字被光糊住"。唯一约束是底不能有花纹落在末行区域：荧光笔靠"半透明黄 × 白底 = 黄"成立，底上有花纹时黄块会把花纹一起乘暗，读作污渍。

## 落位自检（2026-09-05 用户定版，选卡时抄进 SHOTBOOK 该镜自检列）
- 标注几何（框 / 圈 / 线 / 箭头 / 放大镜锚点）一律由**目标的实测包围盒**反推——DOM `getBoundingClientRect` / `measureText`，四边留白 16~24px 等距，**不目测**。
- 实现后抽该镜定妆帧核对：标注是否恰好套住 / 指向目标，偏差 **> 8px 返工**（`references/layout.md` §3）。
- 目标会滚动 / 移动时，标注钉在内容坐标系随内容动（SKILL.md ③）。

<!-- ===== /file: video-talkcraft/references/cards/quote-hold-arrow.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/rack-focus-pair.md ===== -->

---
name: rack-focus-pair
标题: 焦点接力
一句话: 两张白边卡前后叠放、永远一清一糊：讲到哪张，焦点 0.7s power2.inOut 转移过去（前张 blur 0→8 / brightness 1→.6 / scale 1.02→.97，后张反向），4.6s 再转回，6.4s 两张同收——像镜头在两张素材之间对焦
适用: "A 和 B"两件东西被来回提及（纸书 vs 电子书、两款产品）；两个人物 / 两个观点交替讨论、不切镜头只换焦点；新旧对照；引用 + 反驳。默认输入是两张图片；B-roll 要先把 tsx 的 <Img> 换成 <OffthreadVideo>（见复用指引）；人物不参与
时长: 6.8s（0.2 两张入场 → 2.0 焦点前→后 0.7s → 4.6 后→前 0.7s → 6.4 两张同收 0.4s）；成片按口播提到 A / B 的时刻摆转移点，两次转移之间 ≥1.8s
能量: 低
类别: 素材呈现
输入: 图
语义: 对比
素材形态: 横屏, 多图
位置: 中段
props: labels, srcs
优先级: P1
代码: template/cards/rack-focus-pair.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 人物不参与（人 + 素材用 D 组 / host-shrink-to-chip） | △ 一清一糊同样成立，但 tsx 的 srcs 仅走 <Img>，放视频先按复用指引换组件 | ✓（默认输入）两张截图 / 照片 |

两张尺寸可不同、比例按素材真实比例，但**白边一致、投影同一个**。

## 常用场景
1. "A 和 B"两件东西来回提及（demo 演的：纸书 vs 电子书）
2. 两个人物 / 两个观点交替讨论，不切镜头只换焦点
3. 新旧两张对照：先讲旧再讲新
4. 引用 + 反驳：前张是引文截图，后张是数据

## 意图
口播讲 A / B 两件东西时，切镜头 = 两个独立镜头（观众每次重新定位），并排分屏 = 对比（`split-compare-slider` 还要求同构图）。焦点接力是第三条路：**两张同在画面里，注意力靠"其余降权"转移**——多素材调研原则③"任一时刻只有一个主角"的两张版，电影学里就是 rack focus。做对四条：
1. **永远一清一糊**：同时清晰就没有"焦点"，只是两张并排图。
2. **被糊的那张原位不退场**：淡出或缩走就变成"切换"，不是对焦。
3. **转移时 scale 同步微变**（1.02 ↔ .97）：只改 filter 是平面"变糊"，加 5% 的尺寸差才有前后景深。
4. **两次转移之间 ≥1.8s**：观众要读完一张再走；来回超过两次就晕，三个以上对象换 `focus-relay-triptych` / `hero-duo-layout`。

## 动效核心
- **几何**（960×540）：后张 480×320 @ (400, 60)、标签贴右下（right 24 / bottom 24）；前张 380×270 @ (100, 160)、标签左下（left 24 / bottom 24）；前张压住后张左下角（重叠区 x 400~480、y 160~380）。白边 10、圆角 12 / 内 5、投影 `0 12px 60px rgba(0,0,0,.22)`；标签 20px 700 墨色、白 94% 底、圆角 8、投影 `0 4px 16px rgba(0,0,0,.18)`。
- **两态**：在焦 = `filter: blur(0) brightness(1)` + `scale 1.02`；失焦 = `blur(8px) brightness(.6)` + `scale .97`；`transform-origin 50% 50%`。
- **入场**：0.2s 后张、0.28s 前张，各 0.5s `power3.out`：opacity 0→1、y 14→0；前张初始在焦、后张初始失焦。
- **转移**：2.0s 前张 → 失焦、后张 → 在焦，两条 tween 同起 0.7s `power2.inOut`；4.6s 反向再转回。
- **退场**：6.4s 两张 opacity→0 0.4s `power2.in`，6.8s 结束。落定即静置，无 idle。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `softBlur` 失焦模糊 | 8px | 6~10；<5 读不出对焦，>12 素材内容认不出 |
| `softBright` 失焦压暗 | .6 | 与 blur 配合把注意力让出去；>.75 两张都像在焦，<.5 失焦张成黑块 |
| `sharpScale` / `softScale` | 1.02 / .97 | 5% 尺寸差 = 前后景深；差 >8% 读作缩放而不是对焦 |
| `shift` 转移时长 | 0.7s | 真镜头转焦的手感；<0.4 像硬切换，>1.0 观众在等 |
| `focusAt` 转移时刻 | [2.0, 4.6] | 跟口播提到 A / B 的时刻；两次间隔 ≥1.8s |
| 两张尺寸 | 480×320 / 380×270 | 按素材真实比例定，白边一致；后张略大也成立（在焦时它更重要） |
| 标签字号 | 20px | ≈40@1080p 条目档下限；标签放不被另一张压住的角 |

## 已知坑
- 两张同时清晰——没有"焦点"，就是两张并排图。
- 失焦那张淡出 / 缩走——变成"切换"不是"对焦"；它必须原位待着。
- 只 blur 不压暗——糊的那张仍然亮、照样抢眼。
- 转移只改 filter 不动 scale——平面"变糊"，没有前后景深。
- 两张完全不重叠——读作双分屏；重叠一角是"前后"的证据。
- 焦点来回超过两次——观众晕；三个以上对象换三联画 / 一主两辅。
- 后张标签压在被前张遮住的角——后张标签必须贴远离前张的一角（demo 右下）。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/rack-focus-pair.tsx——`srcs=[前张, 后张]` 两张真图、`labels` 两张标签；durationInFrames 216；转移点改 `CONFIG.focusAt`，句长改 `exitAt / end`。tsx 的 `srcs` 仅走 `<Img>`；要放视频把 `<Img>` 换成 `<OffthreadVideo>`（Remotion 自带），其余不动。
- HTML/GSAP：demos/rack-focus-pair/index.html——`.pf / .pb` 的尺寸坐标与 `CONFIG`；`.ph` 换成 `<img>` / `<video>` 即真素材。
- 剪辑软件对应物：剪映两条画中画轨 + 关键帧"模糊"+"亮度"各 0.7s；PR/AE 两层各 Gaussian Blur + 曝光关键帧 easy-ease；AE 真 3D 相机 + 焦距关键帧（LinkedIn Learning "faking rack focus"）。
- 与 layout.md 的接口：双元素组宽度比 480:380 ≈ 1.26:1（§4 双元素组 1:1~2:1 之间）；两张顶边刻意不对齐属"标注压在素材上"类的叠层例外（§6）；整组包围盒 (100,60)–(880,430) 中心 x=490 ≈ 480 居中（§4）。

## 动效范围
- 属于本卡的：一清一糊的两态定义（blur 8 / brightness .6 / scale 1.02 ↔ .97）；0.7s power2.inOut 两张同起的转移；失焦张原位不退；前后叠放的一角重叠；≥1.8s 的转移间隔；0.08 错峰入场与同收。
- 不属于本卡的：示意图（演示语境素材，demos/_lib/media，不属于本卡）、两张的具体尺寸坐标、标签文案、白底舞台。
- 迁移接口：`srcs` / `labels`；`focusAt` 按口播；1080p 输出 blur 8→16、白边 10→20、标签 20→40；深底舞台时投影加重到 `rgba(0,0,0,.4)`。
- 底色要求：白底即可（白边 + 唯一投影把卡从舞台上抬起来）；实验室原型用深灰径向底，入库改白底，两者都成立。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- 两张重叠一角 60~120px（demo 80×220）：不重叠 = 分屏，重叠 >1/3 = 遮挡。
- 每张标签落在不被另一张压住的角，离自身卡边 24 等距。
- 定妆帧两张：转移前（<2.0）与转移后（>2.7）各一帧，任一帧不得两张同时清晰；在焦 blur 0、失焦 blur 8。
- 无人物时组包围盒水平居中偏差 ≤48；有人物时整组放人物对侧半幅。
- 白边等宽 10、投影同一个；两张比例按素材真实比例（`ffprobe` / 图片尺寸）反推卡尺寸。

<!-- ===== /file: video-talkcraft/references/cards/rack-focus-pair.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/reticle-lock-on.md ===== -->

---
name: reticle-lock-on
标题: 准星咬合
一句话: 四个 L 角从四个画外方向（±700, ±500）10 帧扑向截图上的目标，到位时框仍是目标 bbox 的 2.2 倍，随即 6 帧收缩过头到 0.94 再 back.out 回弹到 1——"咔"的咬合感来自超调；咬合那一帧目标白闪 .55→.28 常驻微亮、标签同帧 back 弹出在目标右侧，之后全部钉死
适用: 口播"就是这个按钮 / 这个数字 / 这一条"的重音点名；评测里锁定关键参数；踩音效重拍的目标点名；替代箭头圈红且画面不冻结。输入是截图（含视频截帧），人物不参与
时长: 6.0s（1.3 四角起跳 → 1.63 到位 2.2× → 1.83 咬合：回弹 + 目标微亮 + 标签弹出 → 钉死 → 5.6 整体退场 0.4s）；成片把咬合帧对到口播说出目标的那个字
能量: 高
类别: 强调标注
输入: 截图, 图
语义: 强调
素材形态: 横屏
位置: 中段
props: src, target, label, buttonText
优先级: P2
代码: template/cards/reticle-lock-on.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 人物不参与（人在场时截图放人物对侧，标签朝外侧） | △ 先截帧成图再锁（咬合后画面要静止） | ✓（默认输入）设置页 / 账单 / 表格 / 落地页截图 |

截图铺满 700×420 白卡（1080p 下 1400×840），目标 bbox 由实测反推后经 `target` 注入；标签在目标右侧 18px。

## 常用场景
1. "就是这个按钮"：设置页 / 付费页上锁定一个按钮（demo 演的）
2. 账单 / 表格里锁定一个数字
3. 评测里锁定一个关键参数（配音效重拍）
4. 替代"箭头 + 圈红"：画面不冻结、有咬合的打击感

## 意图
库里给一个目标套框的卡有两张：`corner-bracket-frame` 是角框在原位出现套住一个词，`scanline-annotate` 是扫描线走到哪处取景框从 1.75 倍收拢。两张都是"框出现在目标上"。准星咬合的差别在**入场编排**：四角从四个画外方向扑过来（行程 ≥1000px），到位时还比目标大一倍多，再收缩过头、回弹咬住——像准星锁定目标那一声"咔"，冲击感比原位出现强一档，适合口播里"就是它"的重音。做对四条：
1. **行程 ≥1000px**：短了读作"角标出现"，不是"扑过来"。
2. **飞入与收缩解耦**：到位时框仍是 2.2 倍，收缩是第二拍；同时做就没有"先到再咬"。
3. **超调回弹**：收缩过头到 0.94 再回 1，无超调没有"咔"。
4. **咬合帧三件事同帧**：回弹起点、目标微亮、标签弹出——错帧就散了。
之后全部钉死：这是一次性的重音，不是 hold 期运动。

## 动效核心
- **几何**（960×540，浅底 #f5f5f7）：截图卡 700×420 @ (130, 60)，白底 + 1px 发丝线 + 圆角 12 + 顶部 40px 浏览器栏；目标（相对截图）demo 为按钮 (30, 300, 190×50)；框 = 目标 bbox 外扩 10 → (bx, by, bw, bh)，中心 (cx, cy)；四角 22×22、3px 强调色 L 形，终点 = 框的四个角；标签 22px/700 墨字白底 1.5px 强调色描边圆角 8，@ (bx+bw+18, cy−22)。
- **飞入**：1.3s 起 0.33s `power2.out`，四角各自从终点位移 (−700,−500) / (700,−500) / (−700,500) / (700,500) 飞到终点；飞入期间倍率 s 恒为 2.2（四角绕中心：`pos = c + (corner − c)·s`）。
- **收缩**：1.63s 起 0.2s `power2.in` s 2.2→0.94（过头）。
- **咬合 LOCK = 1.83s**：s 0.94→1 0.15s `back.out(2)`；目标白色微亮层 opacity 0→.55 0.04s 再 →.28 0.2s 常驻；标签 opacity + scale .6→1 0.35s `back.out(1.8)`——三者同帧起。
- **退场**：5.6s 截图 + 四角 + 标签 opacity→0 0.4s `power2.in`，6.0s 结束。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `off` 画外起点 | (±700, ±500) | 行程 ≥1000px 才是"扑过来"；<500 读作角标出现 |
| `fly` 飞入 | 0.33s（≈10 帧）power2.out | <6 帧看不见轨迹、>15 帧读作飘过来 |
| `big` 到位倍率 | 2.2 | 到位时要明显比目标大，1.3 看不出"再咬合" |
| `under` 过头 | 0.94 | 无过头没有"咔"；<0.9 会盖住目标边 |
| `shrink` / `snap` | 0.2s power2.in / 0.15s back.out(2) | 收缩加速、回弹带过冲——机械咬合的手感 |
| `pad` 外扩 | 10px | 框与目标的呼吸边；0 贴死、>20 读作框别的东西 |
| `flashPeak` / `flashHold` | .55 / .28 | 微亮常驻是"已锁定"的状态灯；峰值 >.7 目标被洗白 |
| 标签位置 | 目标右侧 18px、垂直居中 | 目标在右半幅时标签放左侧（同 18px） |

## 已知坑
- 四角从近处出现——没有"扑"，退化成 corner-bracket-frame。
- 飞入与收缩同时做——一路缩小到位，没有"先到再咬"两拍。
- 无超调——滑到即停，机械感减半。
- 目标微亮与标签错帧——两件事散成两个动作。
- 咬合后还在动（角标呼吸 / 标签浮动）——重音之后必须真静止。
- 同镜连锁两个目标——准星只锁一个；多处点名换 `scanline-annotate`。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/reticle-lock-on.tsx——`src` 真截图、`target={x,y,w,h}`（相对截图左上角）、`label`；durationInFrames 192；起跳时刻改 `CONFIG.at`，句长改 `exitAt / end`。四角几何全部由 target 推出。
- HTML/GSAP：demos/reticle-lock-on/index.html——`.shot .tg` 的坐标与 `CONFIG`；`.shot` 里换 `<img>` 即真截图（`.tg` 改成透明定位块，几何照旧由 offset 反推）。
- 母本：video-shotcraft `fui-hud-moves` B 式 reticle-lock-on（暗场 HUD 版；本卡改浅底强调色角标、标签墨字白底）。
- 剪辑软件对应物：剪映四个 L 形贴纸各加"从画外飞入"关键帧 + 整组缩放 220%→94%→100%；AE 四层 Position 关键帧 + 父级 Null 的 Scale 关键帧（220→94→100，末段 easy-ease 过冲）；音效在咬合帧配一记 `pk:mech-lock-quick`。
- 与 layout.md 的接口：截图卡 700 宽 @ 130 → 中心 480 居中（§4）；标签 22px ≥ 条目档（§5）；框几何由 bbox 实测反推、外扩 10 等距（§3 标注类几何）；标签不压截图内容（在目标右侧留白区）。

## 动效范围
- 属于本卡的：四角画外 ≥1000px 扑入；飞入 / 收缩解耦；2.2→0.94→1 超调咬合；咬合帧目标微亮 + 标签同帧；之后钉死；整体同收。
- 不属于本卡的：CSS 假设置页、目标坐标、标签文案、浅底舞台。
- 迁移接口：`src / target / label`；`at` 按口播词锚；1080p 输出角标 44 / 6px、外扩 20、标签 44px、起点 (±1400, ±1000)。
- 底色要求：浅底羊皮纸 #f5f5f7（白卡靠发丝线抬起）；白底同样成立；深底时角标换 #2997ff、标签改深 tile 浅字。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- **四角几何由目标 bbox 实测反推**（Playwright DOM 坐标 / 图片标注），框 = bbox 外扩 10，咬合后四角与框角偏差 ≤8px（layout.md §3）。
- `shot-at 1.5`（飞入中段）：四角在画面内、尚未到位、倍率 2.2；`shot-at 1.85`（咬合帧）：四角套住目标、目标微亮、标签已在右侧同高。
- 标签与目标垂直中心对齐（偏差 ≤8）；标签右边 ≤ 912，不入字幕带 y ≥ 450。
- 收尾帧四角 / 标签 / 微亮全部静止（连抽两帧 diff 为零）。
- 一镜只锁一个目标。

<!-- ===== /file: video-talkcraft/references/cards/reticle-lock-on.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/scanline-annotate.md ===== -->

---
name: scanline-annotate
标题: 扫描线逐处点名
一句话: 一条强调色扫描线匀速（零缓动）自上而下掠过截图，越过每个目标下缘那一刻取景框从 1.75 倍收拢对准（back.out）+ 7% 对焦确认闪，滞后 5 帧右侧标注淡入并常驻；右上状态行实时数 0/4 → 4/4 → "分析完成"——一次扫描点出 N 处，节奏由扫描线统一驱动
适用: 一张截图上有 3～6 处要逐个点评（落地页问题、功能点、合同条款、财报要点）；"AI 帮我读了这份文档"的过程镜头。输入是图片（含视频截帧），人物不参与
时长: 5.6s（0.5 扫描起 → 1.2 / 2.1 / 2.4 / 2.7 四处依次点名 → 2.9 扫描完 → 3.1 "分析完成" → 5.2 整体退场 0.4s）；成片扫描时长按口播念完 N 处的时间反推，标注常驻到讲完
能量: 中
类别: 强调标注
输入: 截图, 图
语义: 强调
素材形态: 横屏
位置: 中段
props: src, targets, labels
优先级: P1
代码: template/cards/scanline-annotate.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 人物不参与（人在场时截图放人物对侧，标注列再靠外一档） | △ 先截帧成图再扫（扫描线要求画面静止） | ✓（默认输入）落地页 / 文档 / 合同 / 财报截图 |

截图铺满 600×396 白卡（1080p 下 1200×792），目标 bbox 由实测反推后经 `targets` 注入；标注列在截图右侧独立一列，不压截图。

## 常用场景
1. "这张落地页有 4 个问题"逐处点评（demo 演的）
2. 对比评测：一张截图上 3～5 个功能点逐个点名
3. 合同 / 政策 / 财报截图逐条划重点
4. "AI 帮我读了这份文档"：扫描 = 正在读，标注 = 读出的结论

## 意图
口播要在一张图上指出多处时，连用 N 次 `callout-line-label`（圆点 → 折线 → 标签）每处一套动作，N=4 就是四次同样的仪式，观众第三次起就烦；`corner-bracket-frame` 只套一个词。本卡把 N 处点名收成**一条扫描线的一次匀速行程**：线是节拍器，走到哪处哪处弹，观众的视线被一条线牵着从上到下读完整张图。做对四条：
1. **扫描线零缓动**：匀速才读作机器在扫；加 ease 立刻变成"有人在拖进度条"。
2. **触发时刻由目标 bbox 反算**：扫描线越过目标**下缘**那一刻取景框才弹——线还没到就弹是穿帮，到了不弹是失职。
3. **框稳了才命名**：标注滞后取景框 5 帧；同时出现就乱。
4. **标注常驻**：这是口播不是产品自述——点出来的东西要留到讲完，全部退场时一起走。

## 动效核心
- **几何**（960×540）：截图卡 600×396 @ (80, 48)（卡底 444，不进字幕带），白底 + 1px 发丝线 #e0e0e0 + 圆角 12 + 投影 `0 12px 40px rgba(0,0,0,.08)`，顶部 38px 灰色浏览器栏；四个目标（相对截图）：标题块 (26,62,320×42) / 首图 (26,162,548×100) / CTA 按钮 (26,274,150×42) / 价格 (26,338,170×36)——**四个目标各占一行**，右侧标注列才不撞。
- **扫描线**：600×2px，`linear-gradient(90deg, transparent, #0066cc 18%, #0066cc 82%, transparent)` + `box-shadow 0 0 14px rgba(0,102,204,.55)`；0.35s 淡入 0.15s，0.5s 起 2.4s **ease none** 从 y=−30 走到 416（相对截图顶），2.9s 淡出 0.2s。
- **触发时刻**：`ft_i = t0 + ((y_i + h_i − yFrom) / (yTo − yFrom)) × dur`，再按 y 序钳 `ft_i = max(ft_i, ft_{i−1} + 0.15)`。demo 四处 ≈ 1.22 / 2.07 / 2.36 / 2.67s。
- **取景框**：目标 bbox 外扩 8px，四个 L 角臂 14px / 2px 强调色；`ft` 起 0.4s `back.out(2)` scale 1.75→1、opacity 同一条 tween 前半程满亮；框内实色层 `ft+0.12` 起 0.12s 升到 0.07、`ft+0.24` 起 0.35s 落回 0——像相机对焦成功的确认闪。
- **标注**：x=712 起、宽 200、左侧 2px 强调色竖线 + padding 14；主行 20px/600 墨色，副行 14px/500 #7a7a7a；`ft+0.17` 起 0.35s `power2.out` opacity 0→1、y 4→0；垂直中心对齐目标中心（top = 目标中心 − 22）。
- **状态行**：右上 (right 80, top 22) 等宽 14px 字距 1.5，实时 `扫描 · fired/N`；扫描结束 +0.2s 切 `分析完成 · N 处` 并转强调色。
- **退场**：5.2s 全部元素 opacity→0 0.4s `power2.in`，5.6s 结束。落定即静置。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `dur` 扫描时长 | 2.4s / 470px | 按口播念完 N 处的时间反推；<1.5s 观众跟不上标注，>4s 线走得像加载条 |
| 扫描缓动 | `none`（零缓动） | **命门**：加任何 ease 都读作"有人在拖进度条" |
| `gap` 最小触发间隔 | 0.15s（≈5 帧） | y 接近的两个目标会同帧弹；钳开后才逐个读得清 |
| `bkScale` 取景框起点 | 1.75 | 1.75 是"从外面收进来"的下限；1.2 看不出对准动作 |
| 角标臂长 | 14px（目标短边 38 的 1/3 内） | 超过目标短边 1/3 就成完整边框，丢掉"取景"语义 |
| `flashPeak` 对焦闪 | 0.07 | >0.15 盖住内容，读作"选中高亮"而非对焦确认 |
| `labelLag` 标注滞后 | 0.17s（≈5 帧） | 滞后是"框稳了才命名"的因果；同帧出现就乱 |
| 标注字号 | 20 / 14px | 20 ≈ 40@1080p 条目档下限；标注列宽 200 放不下就删字不缩号 |
| 目标数 | 3～6 | <3 不如单独 callout；>6 标注列排不下、扫描太密 |

## 已知坑
- 扫描线加了缓动——匀速感一丢就不是机器在扫。
- 触发时刻写死时间轴——一改 bbox 就对不上；必须由 bbox 反算，计数行也必须实时数 fired。
- 两个目标同一行（demo 首版 CTA 与价格并排）——右侧标注列直接相撞；同行目标要么合并成一个框，要么拆成两行。
- 标注压在截图上——口播里截图本身是证据，标注盖上去两边都读不清；标注放独立一列。
- 标注跟框同帧出现——读作两个不相干的东西一起弹；滞后 5 帧才有"先框住、再命名"的因果。
- 取景框收拢起点太小（1.2）——看不出"对准"；对焦闪太亮（>0.15）——读作选中高亮。
- 标注随扫描结束就撤——产品自述可以撤，口播里观众还没听完；常驻到整体退场。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/scanline-annotate.tsx——`src` 真截图、`targets=[{x,y,w,h}]` 目标 bbox（相对截图左上角，按 y 排序）、`labels=[{text,sub}]` 标注；durationInFrames 180；扫描时长改 `CONFIG.dur`，句长改 `exitAt / end`。触发时刻、取景框几何、计数全部由 targets 推出。
- HTML/GSAP：demos/scanline-annotate/index.html——`.shot .tgt` 的坐标与 `CONFIG`；`.shot` 里换 `<img>` 即真截图（目标 `.tgt` 改成透明定位块即可，几何照旧由 offset 反推）。
- 母本：video-shotcraft `scanline-annotate-focus`（暗场 HUD 版；本卡改浅底墨字、6.5px 等宽标注放大到 20px 独立一列、标注常驻）。
- 剪辑软件对应物：剪映"扫光"特效 + 关键帧位置的取景框贴纸 + 文字入场；AE 一条 Shape Layer 位置线性关键帧驱动，每个取景框用 Scale 关键帧 175→100 easy-ease；PR 无直接对应，用 mogrt。
- 与 layout.md 的接口：截图卡左边 80 吸附标题边；标注列左边 712 = 截图右边 680 + 32 组间距（§2）；标注与目标垂直中心对齐（§3 基线对齐的块级版）；取景框几何由 bbox 实测反推、外扩 8 等距（§3 标注类几何）。

## 动效范围
- 属于本卡的：零缓动扫描线；"越过目标下缘触发"的 bbox 反算；取景框 1.75→1 back.out 收拢 + 7% 对焦闪；标注滞后 5 帧、常驻；实时计数行；整体同收。
- 不属于本卡的：CSS 假落地页、四个目标的具体坐标、标注文案、浅底舞台。
- 迁移接口：`src / targets / labels`；`dur` 按口播；1080p 输出扫描线 2→4px、角标臂 14→28、外扩 8→16、标注 20→40 / 14→28；深底舞台时扫描线辉光加重到 `rgba(41,151,255,.7)`、标注改浅字。
- 底色要求：白底即可（截图卡靠发丝线 + 唯一投影抬起来）；深底同样成立。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- 每个目标 bbox 由截图实测（Playwright DOM 坐标 / 图片标注）反推，取景框 = bbox 外扩 8，四角偏差 ≤8px（layout.md §3）。
- 目标按 y 排序且**每行只一个目标**；任意两个目标的标注 top 相差 ≥ 56（标注高 44 + 12）。
- 定妆帧两张：某个取景框弹出那一刻（`shot-at <ft>`）核对"框套住目标、标注尚未出现"；`ft+0.35` 核对"标注已在框右侧同高"。
- 扫描线全程 y 只能是 t 的线性函数（抽两帧算斜率相等）。
- 收尾帧：计数行 = `分析完成 · N 处` 且 N = targets 数；全部标注仍在场。
- 截图卡离画幅边 ≥ 48@960；标注列右边 ≤ 912；无元素进字幕带 y ≥ 450。

<!-- ===== /file: video-talkcraft/references/cards/scanline-annotate.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/scribble-annotation.md ===== -->

---
name: scribble-annotation
标题: 手绘圈注箭头
优先级: P0
代码: template/cards/scribble-annotation.tsx
一句话: 马克笔质感的圈/下划线/箭头按真实笔顺现场画出，画完保持干净静置
适用: 口播点名素材/截图里的具体位置时（"看这个价""就这行小字""点这里"）；测评、锐评、扒皮解说等有"作者在场"感的调性
时长: 单笔 0.3~0.6s（圈 0.55s、下划线 0.4s、箭头杆 0.35s+头 0.15s），笔与笔间隔 0.55s 对齐逐条点名
能量: 中
类别: 强调标注
输入: 截图, 图
语义: 强调
素材形态: 无
位置: 中段
props: hostSrc(未使用)
---

## 意图
口播提到素材里某个细节时，观众的视线需要被"现场的一只手"牵到那儿——
印刷式高亮是排版，手绘线是动作，让人感到作者正在跟你一起看这张图。
命门：**真实笔顺**（一笔从起点画到终点，起收有快慢，匀速就是 loading 条）、

**线要粗且圆头**（4px 以下没有马克笔的"墨量感"）。

常见于：Ali Abdaal、Johnny Harris、Vox、Mrwhosetheboss、LottieFiles arrow/underline 品类。

## 动效核心
- 标注层 = 盖在假截图上的全屏 SVG（`viewBox="0 0 960 540"`，`pointer-events:none`），每笔一条 path，`fill:none`、`stroke-linecap/linejoin: round`、线宽 6px
- **标注几何由被标注目标的包围盒反推**（命门）：圈心 = 目标中心、下划线 y = 目标 baseline + 4px、箭尖 = 目标边缘外 8px。文字类目标要量**墨迹盒**（canvas `measureText` 的 `actualBoundingBoxAscent/Descent` + baseline），不是行盒：行盒上下带字体留白，照行盒画圈会整体偏高、下划线会飘出去 15px+。HTML demo 给目标打 `data-ink` 运行时量 DOM 算 path；tsx 是纯函数渲染，把 demo 算出的四笔 path（含实测长度 `len`）原样写死在 `STROKES`，换目标要按同一规则重算 path
- 描画：`stroke-dasharray` = path 全长，`stroke-dashoffset` 从全长 tween 到 0——圈 0.55s `power2.inOut`、下划线 0.4s `power2.out`、箭头先杆（0.35s `power2.inOut`）后头（0.15s `power2.out`）两笔
- 画完保持静置。本库定版：**不做 line boil / 定格抖动**（用户偏好，见 design-language.md §4 运动 token 附注）。 笔感全部由 path 形状（手绘歪斜的圈、带弧度的线）与描画节奏承担
- 三个标注串行，间隔 0.55s（对应口播逐条点名），起播前截图先静置 0.5s
- 圈不是椭圆工具：path 绕目标画约 1.6 圈、起笔终笔交叉重叠；颜色红 #ff4d4d / 黄 #ffd23e，压在浅色截图上

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `strokeW` | 6 | <4 没有笔感、读作印刷细线；>10 墨太肥会盖住被标注的字 |
| `STROKES[].t0` 笔序起点 | 0.50 / 1.60 / 2.55 / 2.90（笔间隔 0.55s，起播前静置 0.5s） | 间隔对齐口播逐条点名的呼吸；<0.3s 三笔糊成一次动作；>1s 观众在等 |
| `STROKES[].dur` | 圈 0.55 / 线 0.40 / 箭杆 0.35 / 箭须 0.15 | >0.8s 单笔像进度条；<0.25s 看不出笔顺方向；箭须是收笔快扫，拉长到 0.3s 以上箭头会"迟到" |
| `STROKES[].ease` | 圈 / 箭杆 power2.inOut，线 / 箭须 power2.out | 换成匀速一眼假；inOut 给圈"起笔快收笔缓"的手劲 |
| `STROKES[].color` | 圈 / 箭头 #ff4d4d、下划线 #ffd23e | 浅底用红 / 黄，深底换亮色系 |

## 已知坑
- 匀速描画——没有起收快慢的线读作加载动画，不是人手。
- 线太细（<4px）——没有马克笔墨量，读作 UI 描边。
- 圈画得太圆——正椭圆是几何工具画的，必须歪、必须绕 1.5 圈以上且首尾交叉才像手。
- **标注没对准目标（最致命）**——path 坐标沿用死值，改一次文案/字号就偏出去：圈套错了词、下划线飘在行间、箭头指向空白。观众会先看"这线怎么没对上"，动效再好也白做。坐标一律从被标注元素量出来算；tsx 的 `STROKES` 是按 demo 版式实测的死值，换文案 / 字号 / 素材必须重算，不能沿用。
- 拿行盒当文字位置——`getBoundingClientRect()` 含 line-height 留白（17px 字的行盒可比字形高 10px+），圈会整体偏上、下划线离字太远。要用字形墨迹盒 + baseline。

## 复用指引
- props：仅 `hostSrc`（声明未用）；假商品页写死在 JSX，四笔 path 与实测长度写死在 `STROKES` 常量里，换素材 / 换标注目标需改源码并重算 path；`CONFIG.startDelay / gapBetween` 未接线，节奏改 `STROKES[].t0 / dur`。
- Remotion/tsx（skill 首选）：template/cards/scribble-annotation.tsx——自包含单文件，复制进工程即可用；线宽在 `CONFIG.strokeW`，笔序在 `STROKES`，时长/尺寸在 meta。
- HTML/GSAP：demos/scribble-annotation/index.html。**换标注对象不用改坐标**：给目标元素加 `data-ink="xx"`，在 `CONFIG.marks` 里写 `{kind:"circle"|"underline"|"arrow", target:"xx"}` 即可，位置自动跟着 DOM 走；微调用 `padX/padY`（圈松紧）、`baselineGap/overhang`（线贴合）、`side/tipGap/fromDX/fromDY/bow`（箭头从哪来、指哪条边）。换色改 `marks[].color`，节奏改 `dur`/`gapBetween`。手抖用确定性函数（`sin` 组合 + `seed`）不用 `Math.random()`——重播形状一致，也便于逐帧渲染。核心逻辑 = `CONFIG` + `boxOf/inkBoxOf` + `circlePath/underlinePath/arrowPaths` + `smooth()` + `drawStroke()`，可整体摘走。
- Remotion 移植：tsx 直接用 `strokeDasharray = len`、`strokeDashoffset = len × (1 − progress)`（也可用 `@remotion/paths` 的 `evolvePath(progress, d)`），progress = `interpolate(frame, [start, start+durInFrames], [0,1], {easing: Easing.inOut(Easing.quad)})`；三笔的 start 帧按 gapBetween 换算错开。
- （实测变体）序号点名：要一次点名 5 项时不逐笔画，而是 5 根手绘箭头呈扇形**整组淡入**，数字 1-5 再在各箭头尾部逐个弹入（0.2s 间隔）——描画通道让给数字弹入通道，避免 5 笔描画吃掉 3 秒。见 TheAIScaler（Apm_oCzPEQs）。
- （实测变体）红笔斜划否定（a2iG5GkM8KE）：一笔粗红斜线快速划过要否定的词/选项，是"划掉"不是"圈出"，语义相反、笔速更快（0.2s 级）。
- （实测变体）荧光涂抹划除替换（i2fFSAZb5HM）：荧光笔粗涂抹盖住旧词，同帧新词在涂抹上方压入——把"改口/纠正"做成可见动作；涂抹保持静置，仍不做 line boil。
- 剪辑软件对应物：AE = 形状图层"修剪路径"(Trim Paths) 关键帧描画；剪映/CapCut 没有描画通道，用"贴纸→手绘/涂鸦"类圈注贴纸摆到目标上（选无抖动帧的静置款），或用"画笔"素材包替代。

## 动效范围
- 属于本卡的：**标注几何与被标注目标的绑定关系**（圈心=目标墨迹中心且半径外扩、下划线=baseline 下 2~6px 且两端略超出、箭尖=目标边缘外 5~10px）——"标得准"是本卡的语义，不是实现细节；每笔 `stroke-dasharray` = path 全长、`stroke-dashoffset` 全长→0 的描画（圈 0.55s power2.inOut、下划线 0.4s power2.out、箭头杆 0.35s power2.inOut + 头 0.15s power2.out）；**起收有快慢**的缓动纪律（匀速即读作 loading 条）；箭头先杆后头的两笔笔顺；三笔串行、间隔 0.55s 对齐口播逐条点名；起播前素材静置 0.5s；画完保持干净静置——**不做 line boil / 定格抖动**（本库定版禁项）；手作感由 path 形状本身承担（圈绕 1.6 圈、歪斜、首尾交叉，线带弧度）。标注层盖在素材之上、`pointer-events:none` 的层级关系也属于本卡。
- 不属于本卡的：假商品页截图占位（文案、价格、按钮、线框）、标哪几个元素（那是素材侧的事）、标注色 #ff4d4d / #ffd23e 的具体取值、截图的倾斜与投影（已移除，属于风格）。
- 迁移接口：`strokeW` 按画幅缩放（960 宽用 6px，1080p 上翻倍）；节奏在 tsx 改 `STROKES[].t0 / dur`（HTML demo 改 `gapBetween`/`marks[].dur`/`headDur`）；换标注对象——HTML demo 改 `data-ink` + `marks[].target`（坐标自动跟随），tsx 按"圈心 = 目标中心、线 = baseline 下、箭尖 = 边缘外"的同一规则重算 `STROKES[].d / len`；圈的外扩、线的贴合与箭尖留白这些像素量与 `strokeW` 同比缩放；换色改 `STROKES[].color`（浅底用红/黄，深底换亮色系）。目标不是 DOM（视频/图片素材）时，按素材上的目标矩形手算几何。
- 底色要求：白底即可（马克笔色压在浅底上是本卡的原生语境）。深底上需把标注色换成高亮度色系，否则粗线糊进背景。

## 落位自检（2026-09-05 用户定版，选卡时抄进 SHOTBOOK 该镜自检列）
- 标注几何（框 / 圈 / 线 / 箭头 / 放大镜锚点）一律由**目标的实测包围盒**反推——DOM `getBoundingClientRect` / `measureText`，四边留白 16~24px 等距，**不目测**。
- 实现后抽该镜定妆帧核对：标注是否恰好套住 / 指向目标，偏差 **> 8px 返工**（`references/layout.md` §3）。
- 目标会滚动 / 移动时，标注钉在内容坐标系随内容动（SKILL.md ③）。

<!-- ===== /file: video-talkcraft/references/cards/scribble-annotation.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/shape-wipe-transition.md ===== -->

---
name: shape-wipe-transition
标题: 色块扫屏转场
一句话: 两三层同色系色块以 50~80ms 错峰从同一方向扫过全屏，最后一层扫走时画面已换成下一场景
适用: 口播换章节、换话题、"讲完概念上数据"式的节奏切分点；综艺化/快节奏调性，正片与竖屏切片都常用
时长: 单层 0.45s、层间错峰 60~80ms，整段扫屏约 0.6s；内容在第二层过屏中线那一帧切换
能量: 高
类别: 转场结构
输入: 场, 人(可选)
语义: 转场, 章节
素材形态: 无
位置: 任意
props: hostSrc
优先级: P0
代码: template/cards/shape-wipe-transition.tsx
---

## 意图
口播里硬切换话题会让观众"没跟上"，色块扫屏给出一个 0.6s 的强节奏信号：上一章翻篇了。
命门：**多层错峰**（单层就是拉幕布，2~3 层错峰才有"刷"的层次）、
**换内容藏在遮挡帧里**（观众永远看不到切换的那一瞬间，只看到扫过之后世界变了）、
**快进快出**（power4.inOut 中段极快，慢了就从转场变成了动画表演）。

常见于：YouTuber 转场模板包（每包 15~140 个）、BASE（2.5K 销量）、影视飓风、综艺化口播。

## 动效核心
- 3 层色块（同色系浅→中→深，后扫的层叠在上面），矩形带 `skewX(-12°)` 斜切
- **色块要宽**：每层约 2.6 倍屏宽——power4 高速段里 70ms 的时间错峰会拉开约 2 个屏宽的空间间距，色块只有一屏宽必在中段露缝
- 每层 `xPercent -75 → 75`（按 2.6 倍屏宽折算，两端出画留斜切余量），单层 0.45s `power4.inOut`，层间 delay 60~80ms
- 途中拉伸：色块在过屏中段 `scaleX 1 → 1.22 → 1`（速度感），可拆成 power4.in + power4.out 两段在中点同步拉伸峰值
- **换内容回调**：在第二层运动中点（= 该层完全盖住全屏的那一帧）用 `tl.call()` 把场景 A 直接 `set` 成场景 B，瞬时切换，无过渡
- 视觉读法：领先边是浅色→中色两道细条，深色主体压后；扫走后新场景直接露出

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 单层扫屏时长 | 0.45s | >0.7s 读作幕布慢慢拉过、节奏塌掉；<0.3s 只剩一下闪烁，看不出方向 |
| 层间错峰 | 60~80ms | >120ms 层间露出缝隙、半张旧画面穿帮；<40ms 三层糊成一层，等于白做 |
| 斜切角度 | -12° | 0° 读作 PPT"推入"切换；>20° 色块变成尖刀，四角容易遮不满穿帮 |
| 途中拉伸倍数 | 1.22 | 1.0 匀速平推没有速度感；>1.4 色块明显变形，读作果冻/故障 |
| 换内容时机 | 第二层过中线帧 | 提前＝旧场景还露着就消失（闪黑穿帮）；押后＝新场景在色块缝里提前露脸 |
| 层数 | 3 | 2 层勉强成立；1 层＝拉幕布；>4 层读作彩带广告，喧宾夺主 |
| 色块宽度 | 2.6 倍屏宽 | 窄于 2.4 倍屏宽高速段层间露缝、新旧内容闪现；过宽只是浪费，无副作用 |

## 已知坑
- 单层色块扫过——就是拉了一块幕布，毫无包装感，一眼廉价。
- 层间错峰拉到 120ms 以上——层与层之间露缝，观众瞄到缝里旧画面，穿帮。
- 内容切换没卡在全遮挡帧内——切换瞬间被看见，转场的"魔术"当场拆穿。
- 三层用三个不同色系——读作彩虹广告条而不是一次转场；必须同色系深中浅。
- 用 linear/power1 匀速扫——没有加速度就没有"刷"感，读作屏保。
- 色块只做一屏宽——power4 中段速度是均速的 4 倍，60~80ms 错峰在空间上被放大成约 2 屏宽的缝，新场景从缝里闪出来，一眼穿帮。

## 复用指引
- props：仅 `hostSrc`；场景 A / B 的内容写死在 JSX，换场景需改源码。
- Remotion/tsx（skill 首选）：template/cards/shape-wipe-transition.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/shape-wipe-transition/index.html。改 `CONFIG.colors` 换色系（浅→中→深三个值），改 `CONFIG.wipeDur / layerDelay / skew / stretch` 调手感；场景 A/B 的内容替换 `.scene-a` / `.scene-b` 内部即可，换内容回调不用动。
- Remotion 移植：每层 `interpolate(frame, [start, start+half, start+dur], [-75, 0, 75])` 配 easing 拆两段（前半 Easing.in(Easing.quart)、后半 Easing.out(Easing.quart)）；换内容用同帧判断 `frame >= swapFrame ? <SceneB/> : <SceneA/>` 切 Sequence，swapFrame = 第二层的中点帧。
- 剪辑软件对应物：剪映"转场→MG 动画/划像"类；CapCut "shape wipe / MG transition"；AE 用 3 个固态层位置关键帧 + 各错开 2 帧 + Easy Ease 100%，中间帧上做剪辑点。

## 动效范围
- 属于本卡的：三层色块各自 `xPercent -75→75` 过屏（单层 0.45s，`power4.in` + `power4.out` 拆两段 = 整体 `power4.inOut`）；层间 60~80ms 错峰（三层的先后关系与深色层压最上的叠序）；过屏中段 `scaleX 1→1.22→1` 拉伸峰值同步到中点；`skewX(-12°)` 斜切；色块宽 2.6 倍屏宽（错峰在 power4 高速段会被放大成约 2 屏宽的空间间距，窄了必露缝）；**换内容回调卡在第二层完全盖屏的那一帧**做瞬时切换。
- 不属于本卡的：色块的颜色、场景 A/B 的全部内容（主持人占位、假图表、柱子长出动画、字幕文案）、章节角标。柱状图逐根长出与字幕跟进只是"转场之后世界变了"的证据，换场景时整段替换，回调不用动。
- 迁移接口：**色块颜色 = 复用者的品牌色接口**——改 `CONFIG.colors` 一个数组三个值，必须是**同色系浅→中→深**（demo 用中性墨色三档 #d8d8dc / #8a8a8e / #1d1d1f；三个不同色系读作彩虹广告条）；手感在 `CONFIG.wipeDur / layerDelay / skew / stretch`；换尺寸时色块宽度按"≥2.4 倍屏宽"重算，`xPercent` 的 ±75 是按 2.6 倍宽折算出来的，改宽度要同步改它；换方向把 `xPercent` 与 `skew` 一起取反。
- 底色要求：白底即可（转场期间色块满屏遮盖，底色不参与）。唯一约束是最深那层要能盖住新旧两个场景——色块与场景底色明度差不足时会在中段透出内容。

<!-- ===== /file: video-talkcraft/references/cards/shape-wipe-transition.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/slab-punch-title.md ===== -->

---
name: slab-punch-title
标题: 重点放大
优先级: P0
代码: template/cards/slab-punch-title.tsx
一句话: 两行标题里第二行的重点词坐在斜切色块上——第一行整块硬现 0.18s，色块从中心 scaleX 撑开 0.22s，**块撑到位那一帧**白字才硬切出现并从 1.12 倍 punch 落定（5 帧）
适用: 一句口播里"前半句铺垫 + 后半句是重点"的对照句式（"找到 / 关键点"、"问题不在 A / 在 B"）；态度鲜明的观点号、干货号、带货口播；也可当短口播的段落小标题
时长: 起手静置 0.4s → 第一行硬现 0.18s → 呼吸 0.07s → 色块中心撑开 0.22s → 白字 punch 0.167s → 收尾定格 1.6s；共约 2.64s
能量: 高
类别: 字幕花字
输入: 人(可选), 文
语义: 转折, 标题
素材形态: 无
位置: 任意
props: hostSrc
---

## 意图
"重点放大"要解决的不是"让字更大"，而是**让观众知道哪个词是结论**。
直接把第二行写成大红字也能大，但它跟第一行是同一种东西（都是字），观众读到的是"两行标题"；
一旦第二行被装进一个**块**里，两行就变成了"铺垫"和"结论"两种物件——层级是靠介质差做出来的，不是靠字号差。

命门三条：
① **块先到位、字后落**。色块撑开的 0.22s 里第二行是空块，白字在块停住的那一帧才出现。
反过来（字先在、块从字下面长出来）读作"字被块追上"，块变成了给字上色的马克笔，
这张卡就退化成 `highlighter-sweep`（那是荧光笔语义，能量档低一级）。
② **块的 -2.5° 斜切是静态形状属性，不是动效**。它写在 CSS 的 `transform: rotate()` 上，
GSAP 全程不碰。做成"落定后回正"或"落定后抖两下"都是错的——手作感由形状本身给（design-language §4），
不靠定格抖动。
③ **第一行是"硬现"不是"淡入"**：`scale 1.04 → 1` + opacity 走 0.18s，**无位移**。
1.04 这个量小到读不出缩放，但它让"出现"这件事有了一点厚度；给它加 y 位移立刻变成入场动效，
第一行就不再是"背景铺垫"而是抢了第二行的戏。

本卡是本批（◈）标题色块类的基准式，"铺垫 + 结论"对照句专用——同批其余块式标题都是在它的"块先到位、字后落"上做变奏。

## 动效核心
- **三拍串行，每拍只有一个主角**（这是它读起来干净的原因）：
  - 拍① `t=0.40` 第一行：`scale 1.04 → 1` + `opacity 0 → 1`，`0.18s power3.out`，**无位移**，
    `transform-origin: 0% 50%`（左对齐是构图基线，4% 的缩放不许把左边缘挪走）
  - 拍② `t=0.65`（第一行落定 + 0.07s 呼吸）色块：`scaleX 0 → 1`，`transform-origin: 50% 50%`，
    `0.22s power3.out` —— **从中心撑开**，不是从左展开（从左展开是 `alt-block-lines` 的语言）
  - 拍③ `t=0.87`（= 拍②结束的那一帧）白字：`opacity` **硬切 0 → 1**（0 帧，用 `tl.set`），
    同帧 `scale 1.12 → 1` 走 `0.167s power3.out`（punch 5 帧 @30fps）
- **白字的 opacity 必须是硬切**：给它 0.1s 的淡入，字就会在块里"显影"，
  和块撑开那一拍连成一段渐变，"块停 → 字砸"这个断点就没了
- **DOM 三层，各管一件事**（斜切与动画互不干扰的实现口径）：
  外层 `.sp-l2` 只有静态 `rotate(-2.5deg)` → 中层 `.sp-slab` 只有 padding（决定"块比字大一圈"）
  → 内层两个兄弟：`.sp-slab-bg`（绝对定位铺满，唯一被 `scaleX` 的元素）与 `.sp-l2-t`（相对定位压在 bg 之上）
- **块比字大一圈的量**：`padding: 10px 22px 12px` @84px 字号 ≈ 上下 12%、左右 26% 字号。
  下 padding 比上多 2px——中文字的视觉重心偏上，等 padding 会读作"字贴着块的下沿"
- **第二行 `margin-left: -22px`（= 块的左 padding）**：落定后第二行的**字**与第一行的字左端对齐，
  而不是块与字对齐。块比字宽，块对齐会让两行的字看起来错开一截
- **层级**：舞台白底 → 第一行（黑字）→ 第二行外层（静态斜切）→ 色块 bg（z 底）→ 白字（z 上）
- **强调色只上在块上**：`#e0452c`（参考图红系）。第一行是黑 `#1d1d1f`，白字是块上的反白——
  全卡只有一个彩色元素，就是那个块

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `slabDur` | 0.22s | 色块撑开时长，本卡的能量旋钮；<0.14s 块像闪出来的（少了"撑"这个动作），>0.35s 观众等着块开完、口播已经念过重点词了 |
| `gap` | 0.07s | 第一行落定 → 色块起撑的呼吸；0 则两拍粘成一拍（读作"两行一起出现"），>0.2s 两行断成两个动效 |
| `punchScale` | 1.12 | 白字 punch 起始倍数；<1.06 punch 读不出（字只是出现），>1.25 字会在块外露头一帧（块是硬边，露头一眼就是错） |
| `punchDur` | 0.167s（5 帧） | punch 时长，`power3.out`；>0.3s 读作"字慢慢长大"，砸的劲全泄了 |
| `l1Scale` | 1.04 | 第一行起始倍数，**必须小**；>1.08 第一行变成弹窗，抢第二行的重点位 |
| `l1Dur` | 0.18s | 第一行硬现时长；>0.3s 第一行成了主角，观众的注意力落在铺垫句上 |
| 斜切角 | -2.5°（CSS 静态） | 块的倾斜量；0 读作规整的排版色块（"设计感"没了但也成立），>-6° 块开始撞第一行的下缘，且中文字被斜得难读 |
| padding | 10/22/12 px @84px | "块比字大一圈"的量；左右 <14px 字贴块边（像被裁了），>34px 块空得像一个色条 |
| `hold` | 1.6s | 收尾定格——块 + 字的成品版式就是落点，按重点词字数给（每字约 0.4s，读完再留半拍） |

## 已知坑
- 字和块同时出现（或字先在、块从底下长出来）——读作"字被块追上"，块降格成马克笔，本卡与 `highlighter-sweep` 无区别。
- 白字用淡入而不是硬切——块停和字出连成一段渐变，"块先到、字后落"这个断点消失，两拍变一拍。
- 斜切做成动画（落定后回正 / 落定后抖两下）——违反 design-language §4 的定格抖动禁项，而且回正会让观众以为块"歪了又被修正"，斜切从形状属性变成了错误状态。
- 色块用 `width: 0 → 100%` 而不是 `scaleX`——改 width 每帧触发重排，块内的字会跟着一帧一帧挤动，慢放下一眼假（`scaleX` 只走合成层）。
- 色块从左展开（`transform-origin: 0% 50%`）——那是 `alt-block-lines` 的"刷出"语言，配上"块停字砸"的时序会读作两张卡缝在一起：从左展开的块观众预期字跟着刷出来，结果字是砸出来的。
- 第二行按**块**与第一行左对齐（忘了 `margin-left` 抵掉块的 padding）——两行的字看起来错开 22px，标题的左基线塌了。
- 白字 `transform-origin` 取左端——1.12 倍的 punch 会往右长出块外一帧；取 `50% 50%` 才是"在块里原地砸"。
- 第一行给 y 位移——它立刻变成一个入场动效，与第二行的"块 + 砸"两个动效并列，一屏两个重点，散。
- 块的强调色同时用在第一行的字上（想"呼应"）——违反 design-language §1 的唯一强调色红线，且第一行一变色就与第二行争"哪个是重点"。
- `padding` 上下等值——中文字视觉重心偏上，等 padding 读作字贴着块的下沿；下 padding 要比上多 2~3px。

## 复用指引
- props：仅 `hostSrc`；两行文案在 JSX 常量里，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/slab-punch-title.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/slab-punch-title/index.html。**换文案改两处 HTML 文本**（`#spL1` 的铺垫词 2~4 字、
  `#spL2` 的重点词 2~5 字）——块宽由字自动撑出，不用改任何常量。
  换强调色改 `.sp-slab-bg` 的 `background` 一处（红 `#e0452c` / 紫 `#7A5AF8` / 青 `#0aa3a3` 任取其一）。
  换字号改 `.sp-l1` 与 `.sp-l2-t` 的 `font-size`（两处必须同值），同时把 `.sp-slab` 的 padding
  与 `.sp-l2` 的 `margin-left`（= 左 padding 的负值）按比例缩放。
  能量只调 `slabDur`；`punchDur` 是手感常量（5 帧），换尺寸换语速都不要动。
- Remotion 移植：三拍串行，用一个 `frame` 时钟 + 三段 `interpolate` 就够，不用建时间线。
  30fps 换算：`lead 12f`、`l1Dur 5.4f≈5f`、`gap 2f`、`slabDur 6.6f≈7f`、`punchDur 5f`。
  **块与字必须是两个 `<div>`**：块 `transform: scaleX(interpolate(f, [26,33], [0,1], {easing: Easing.out(Easing.cubic), extrapolateLeft:'clamp', extrapolateRight:'clamp'}))`；
  字 `opacity: f < 33 ? 0 : 1`（三元硬切，**不要写成 interpolate**——interpolate 出来的是淡入）+
  `scale: interpolate(f, [33,38], [1.12,1], {...clamp})`。斜切写在最外层容器的静态 style 上，
  不进任何 interpolate。
- 剪辑软件对应物：剪映/CapCut——一个文本层（第一行）+ 一个色块贴纸（旋转 -2.5°）+ 一个文本层（重点词）。
  色块用"缩放"关键帧 0% → 100%（**锚点要设中心**，剪映默认就是中心，这条恰好对）；
  重点词的"不透明度"打两个**同值不同帧**的硬切键（0 → 0 → 100，中间两键只差 1 帧）再叠"缩放"112% → 100%。
  剪映的入场预设里没有"块撑开 + 字砸"这个组合，必须手打关键帧。
  AE——色块层 `Scale` 只改 X 通道（解锁等比）0 → 100，`Anchor Point` 在块中心；
  文字层 `Opacity` 用 `Hold` 关键帧（右键 → Toggle Hold Keyframe）做硬切，
  `Scale` 112 → 100 配 `Easy Ease Out` 再把手柄拉到底。
- 与本库同类卡的分工：`keyword-pop-highlight` = 字幕句子里砸一个词（词在句中，色块跟着词跑）；
  `highlighter-sweep` = 荧光笔扫过已经在屏上的字（字先在、色后到，低能量）；
  `alt-block-lines` = 两行各坐一个块、块刷出字（对句关系，块从左展开）；
  `speed-slab-title` = 块从画外冲入 + 速度线残影（同样是"块 + 标题"，但语义是速度不是重量）；
  **本卡 = 一句话里"前半铺垫 / 后半结论"的两行标题**，块是结论的容器，punch 是结论的落地声。

## 动效范围
- 属于本卡的：「块先到位、字后落」这条时序纪律（白字的起点 = 色块 tween 的结束帧，不许交叠）；色块 `scaleX 0→1` 从**中心**撑开这个方向；白字 opacity 的**硬切**（0 帧，不淡入）+ 同帧 `scale 1.12→1` 的 5 帧 punch；第一行 `scale 1.04→1` 无位移的"硬现"（1.04 这个"读不出的厚度"量级）；`gap 0.07s` 这个两行之间的呼吸；三拍串行、每拍只有一个主角这个结构；块的斜切是**静态形状属性**（GSAP 不碰）这条实现纪律；DOM 三层分工（静态斜切层 / padding 层 / bg 与字兄弟层）；`transform-origin` 的取法（第一行取左端护住左基线、白字取中心防露头、块取中心）。
- 不属于本卡的：demo 那句「找到 / 关键点」的具体文案、84px 字号与 700 字重、`#e0452c` 这个红（换成紫/青/橙同样成立，参考图本身也只是一个色系样本）、-2.5° 这个具体角度（-1.5°~-4° 都成立，0° 也成立只是少了手作感）、`padding: 10/22/12` 这组具体像素（比例是上下 12% / 左右 26% 字号）、块的 4px 圆角、右侧主持人（数字人）占位、以及"标题落在左侧白区、左边距 72px"这个落位（居中、下三分之一都成立）。
- 迁移接口：内容入口是两段纯文本（铺垫 2~4 字 / 重点 2~5 字），块宽自动贴合不需要量宽；能量只调 `slabDur`（0.14~0.35s），`punchDur` 与 `punchScale` 是手感常量不要动；换字号时 `font-size`（两处同值）、`.sp-slab` 的 padding、`.sp-l2` 的 `margin-left` 三者按同一比例缩放；换强调色只改 `.sp-slab-bg` 的 `background` 一处；`hold` 按重点词字数给（每字约 0.4s）；竖屏把字号收到 56~64px、两行的 `gap` 从 14px 收到 10px（本卡没有横向推挤，唯一约束是块的宽度不超过可用宽度的 88%——块是硬边，压到安全区外一眼就是错）。
- 底色要求：白底即可。深底也成立但要换实现——深底上第一行反白、白字块保持不变，此时"白字在实色块上"与"白字在深底上"的对比不够，块必须换成更亮的强调色（或给块加 1px 亮边）。**渐变底与实拍花底不行**：块是硬边矩形，底上的高频细节会让块边缘读作抠图毛边。

<!-- ===== /file: video-talkcraft/references/cards/slab-punch-title.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/slow-pull-reveal.md ===== -->

---
name: slow-pull-reveal
标题: 缓拉全貌
优先级: P0
代码: template/cards/slow-pull-reveal.tsx
一句话: 镜头起手咬在页面某处细节上（scale 1.26 + 偏移把它顶到画心），8~15s 匀速拉远回正到素材原样满画幅，观众在"原来这是一整张看板"的瞬间接到规模信息
适用: 出示的静态素材本身"量大"时——数据看板、长清单、密集表格、全景图；开场悬念（先看一个数字再揭示它在哪张表里）、段落收束（从细节退回全局做总结）两个时机最稳
时长: 实拍 8~15s（与本段口播等长）；demo 压缩演示：主拉 4.4s → hold 1.5s 拉完余量，全程 5.9s
能量: 低
类别: 运镜
输入: 图, 截图
语义: 钩子
素材形态: 横屏
位置: 任意
props: hostSrc(未使用)
---

## 意图
缓推是"往里走"，缓拉是"信息量揭示"——它的价值不在动，而在**终点比起点信息多**：
观众先被按在一个细节上（这个数字很惊人），再被拉开看到它所处的全貌（原来整张表都是这样）。
这个顺序做不了反：先看全貌再推细节是 [slow-push-in](slow-push-in.md) 的活，语义是"聚焦"；
缓拉的语义是"扩展"。做对的命门：
**起手必须真的看不见全貌**（1.2~1.35 且兴趣点顶到画心；起手 1.05 就等于全貌已在，拉了也没有揭示）、
**终点必须回正到素材原样**（scale 1、零偏移——拉过 1.0 会露出素材外的空白，整个真实感崩掉）、
**匀速为主 + 收尾收住而不撞停**（末速非零，hold 期接着走完最后一点）。

## 动效核心
- 结构：静态素材满画幅铺在**相机层**里，相机层是全卡唯一被 transform 的元素；素材本身零动画
- 起手画幅：`transform-origin` 固定在**画面中心**（不是兴趣点——拉镜的终点是"素材原样"，origin 必须是画心才能零偏移收尾），
  用 `scale = zoomFrom`（1.26）+ 位移 `x = −dx, y = −dy` 把兴趣点顶到画心，
  其中 `dx/dy` = 兴趣点中心相对舞台中心的**未缩放**偏移（HTML demo 运行时读包围盒反推；tsx 写死为常量 `D` = (−234.75, −156.5)，换兴趣点重算）
- 主拉：`scale zoomFrom → 1`，位移同步回零（两者必须同一条时间轴，否则会读成"边缩边平移"两个动作）
- 缓动：**匀速**或本库通用运镜 ease `p + (1−r)·p²·(1−p)`（`r = endRate ≈ 0.55`，比推镜更"收住"）。
  末速非零是刚性要求——`power2.out` 末速为 0，会在到位那帧停死
- hold 期：主拉只走全程的 `k`，剩下的 `(1−k)` 留给 hold 期**按主拉末速匀速走完**，正好停在素材原样。
  `k = 1 − (末速 × holdDur) / 总量`，两段速度连续，观众读不出段落切换
- 时长与推进量的关系同缓推：`pullDur` 对齐本段口播；`zoomFrom` 是观感常量，换时长不改它
- 素材分辨率要求：原始分辨率 ≥ 画幅 × `zoomFrom`（1080p 画幅起手 1.26 需要 ≥2420px 宽），起手糊比不运镜更糟

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `zoomFrom` | 1.26（范围 1.2~1.35） | 起手咬多紧。<1.15 全貌已经基本可见，"揭示"归零；>1.4 起手已经发虚，且拉的过程太长观众等不到 |
| `zoomTo` | 1.0（素材原样） | **不要改**。拉过 1.0 会露出素材外的空白，一眼假；素材四周确实有留白余量时才可以给到 0.96 |
| `pullDur` | 实拍 8~15s / demo 4.4s | 与本段口播等长。压到 2~3s 就成了"拉镜头"（一个事件，属 pullback-cool-transition 的语气），不是缓拉 |
| `endRate` | 0.55 | 末速占平均速的比。拉镜比推镜更该收住（0.5~0.65）；1 = 全程匀速也成立；<0.35 读作撒手 |
| `holdDur` | 实拍 3~8s / demo 1.5s | hold 时长随讲述走；这段走完余下的 `(1−k)`，画面仍在动 |
| 兴趣点 / `D` 起手偏移 | demo 挂 id 运行时反推；tsx 常量 (−234.75, −156.5) | 决定起手咬哪。选"最能勾住人的那个数字/那一行"；选在素材边角会让起手画幅露出素材外的空白；tsx 换兴趣点要重算 `D` |

## 已知坑
- 拉到 `scale < 1`——素材边缘外的舞台底色露出来，观众立刻知道这是"一张贴上去的图在缩小"，不是镜头在拉远。终点必须是素材原样满画幅。
- `transform-origin` 咬在兴趣点上（照搬缓推的做法）——那样收尾时素材不会回正到满画幅，必须再补一个位移，两个动作打架。拉镜的 origin 必须是画心，兴趣点靠**位移**顶到画心。
- 起手咬得太松（1.05~1.1）——观众一开始就看到了全貌，后面的"拉远"没有揭示任何新信息，白运镜。
- 用 `power2.out` 收尾——末速为零，到位那帧停死；缓拉的收尾要"收住"（减速）但不能"停住"。
- 缩放和位移放在两条时间轴/两段 tween 上——读作"先缩一下再平移一下"，不是一个连续的镜头。必须同一段。
- 起手位置让兴趣点贴着画幅边——兴趣点没顶到画心，起手构图就是歪的，观众第一眼在找"我该看哪"。
- 素材分辨率不够（1080p 画幅配 1600px 宽截图起手 1.26）——最糊的恰恰是最需要看清的起手那几秒。
- 当段口播讲的是"聚焦某一点"却用了缓拉——运镜方向和语义反了。往里聚焦用 [slow-push-in](slow-push-in.md)，往外扩展才用本卡。
- 同一段里既缓拉又缓推（拉一半又推回去）——观众读作"手抖了"或"没想好"。本卡与 [slow-push-in](slow-push-in.md) 语义互为反面，一段只能选一个方向；要反向就换镜头。

## 复用指引
- props：无（`hostSrc` 声明未用）；素材是写死在 JSX 的 DOM 假看板，起手偏移 `D` 是按该版式实测的常量，换素材 / 换兴趣点需改源码并重算 `D`。要放真截图把 `.page` 内的 DOM 换成一张铺满相机层的 `<Img>`（视频用 `<OffthreadVideo muted>`），`D` 按图内兴趣点像素坐标重算。
- Remotion/tsx（skill 首选）：template/cards/slow-pull-reveal.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：`demos/slow-pull-reveal/index.html`。换素材改 `.page` 内整块 DOM（或换成一张铺满 `.camera` 的 `<img>`）；换起手咬点把 `id="poi"` 挂到任意元素上（偏移量运行时反推）；节奏全在顶部 `CONFIG`（`zoomFrom` / `zoomTo` / `pullDur` / `holdDur` / `endRate`）。核心可摘走：`CONFIG` + `camEase` + `DemoShell.register` 回调体三段。
- Remotion 移植：`transformOrigin: 'center center'` 固定，三条 `interpolate` 同一时间轴——`const z = interpolate(frame, [0, pullEnd, holdEnd], [1.26, zMid, 1], {easing: Easing.bezier(0.33,0.33,0.5,0.85), extrapolateRight:'clamp'})`，`x` / `y` 从 `-dx/-dy` 插到 `0`（`dx/dy` 由兴趣点在素材内的百分比坐标 × 画幅算出，写死成常量即可）。要匀速就 `easing: Easing.linear`（**别用默认 bezier，它是 ease-in**）。`zMid` 与 `k` 按卡内公式算：`k = 1 − (总量/pullDur × endRate × holdDur) / 总量`。合成 `transform: scale(z) translate(${x}px, ${y}px)`。
- 剪辑软件对应物：这是 **Ken Burns 的拉镜半边**（推镜半边见 [slow-push-in](slow-push-in.md)）。剪映——图片打两个"缩放"关键帧（126% → 100%）+ 两个"位置"关键帧（偏移 → 0,0），**两端关键帧都设成线性**（默认的缓入缓出会让末速归零）；AE——Scale 126→100 + Position 关键帧，锚点保持素材中心，`Keyframe Interpolation → Linear`，或在速度图里把末端速度拉到非零；Premiere/CapCut 同理（PR 是 `Motion → Scale/Position` 线性关键帧）。

## 动效范围
- 属于本卡的：静态素材上的一条**缓拉曲线**——`scale zoomFrom(1.2~1.35)→1` 在 8~15s（demo 4.4s）里走完，位移**同一时间轴**从"兴趣点顶到画心"的偏移回到零，缓动为匀速或**末速非零的极缓减速**；`transform-origin` 固定画心（这是"终点能零偏移回正到素材原样"的技术前提）；起手偏移由兴趣点包围盒反推（demo 运行时量、tsx 写死常量 `D`）；hold 期按主拉末速走完余下的 `(1−k)`、正好停在素材原样（速度连续、镜头永不静止）；"终点必须是素材原样满画幅、不可拉过 1.0"这条纪律；"起点信息 < 终点信息"的语义方向。
- 不属于本卡的：demo 里的灰阶线框数据看板（顶栏/侧栏/KPI 卡/折线图/清单/底部小卡及其全部数值与排版）、起手咬在"日活跃用户"卡这一具体决定、素材的入场动画（属 media-pop-in）、页面上的标注与聚焦（属 focus-dim-spotlight / magnifier-detail）。
- 迁移接口：`zoomFrom` 定起手咬紧程度（按素材分辨率上限取值）；`pullDur` 对齐本段口播时长（换时长时 `zoomFrom` 不变）；`endRate` 定收尾收住的程度；起手咬点＝任意页内元素（HTML demo 挂 id、偏移运行时反推；tsx 重算常量 `D`）；`k` 与 hold 段终点由末速自动推出，不要手填；换画幅时 `dx/dy` 由包围盒重新测量。
- 底色要求：白底即可——本卡零颜色、零装饰，只是一条 transform 曲线，任何素材（浅色看板、深色终端、照片、长表格）上都成立。唯一实质要求是**素材要铺满画幅**（有留白的素材拉到原样时会露白，那属于素材问题不是运镜问题）。

<!-- ===== /file: video-talkcraft/references/cards/slow-pull-reveal.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/slow-push-in.md ===== -->

---
name: slow-push-in
标题: 缓推特写
优先级: P0
代码: template/cards/slow-push-in.tsx
一句话: 静态页面（截图/文档/图片）以匀速或极缓减速缓慢推进 scale 1→1.08~1.15，transform-origin 咬在兴趣点上、画幅同时微移把它让向构图位，8~15s 里读不出"某一帧在动"却始终没停
适用: 口播出示网页截图/文档/图片/UI 界面时的默认底噪运镜——静态素材一上屏就该有这条曲线；讲解、评测、财经拆解等冷静举证调性；也是"讲到这一段时把视线收拢到这一处"的引导手段
时长: 实拍 8~15s（与本段口播等长，一句话一条曲线）；demo 压缩演示：主推 4.2s → hold 1.6s 续推，全程 5.8s
能量: 低
类别: 运镜
输入: 图, 截图
语义: 例证
素材形态: 横屏
位置: 任意
props: hostSrc(未使用)
---

## 意图
静态截图往屏上一贴，画面立刻"死"——观众的眼睛没有理由留在上面，注意力回落到听觉，
一两秒后就开始想划走。缓推是最便宜也最通用的解药：镜头以观众察觉不到的速度往兴趣点走，
画面每一帧都在变，"还没看完"的感觉被持续维持。做对的命门：
**必须匀速或极缓减速**（`power2.out` 那种前快后慢会被读成"冲一下"，缓推的全部气质在"察觉不到"）、
**推进量要小**（1.08~1.15；超过 1.2 位图开始发虚，观众会注意到画质而不是内容）、
**推到位不能停死**（hold 期以主推末速继续走，这是本库"相机永不静止"信条最基础的一条）。

## 动效核心
- 结构：静态素材（截图/图片/DOM 页面）满画幅铺在一个**相机层**里，相机层是全卡唯一被 transform 的元素；素材本身零动画
- `transform-origin` 咬在**兴趣点中心**（引文块/关键数字/按钮）；HTML demo 运行时读该元素的包围盒反推坐标，tsx 写死为常量 `ORIGIN` = (316, 424.87)，换兴趣点重算
  兴趣点在原地不动、其余内容绕着它长大，读作"镜头正在往它走"；origin 放画面中心则读作"整体放大"（更弱但更安全）
- 主推：`scale zoomFrom → zoomTo`（1.0 → 1.10），时长 = 本段口播时长（实拍 8~15s）
- 缓动：**匀速**（`ease: none`）或**极缓前载减速**——本库通用运镜 ease：`p + (1−r)·p²·(1−p)`，
  起速 = 平均速、末速 = `r ×` 平均速（`r = endRate ≈ 0.6`）。关键性质是**末速非零**：`power2.out` 末速为 0，镜头会停死
- 焦点微移：主推同时叠 `x/y` 各 5~15px 的漂移，把兴趣点从"死正中"让到构图位（三分线附近）；方向与推进配合，不是随机抖
- hold 期（讲述停在这一页的那几秒）：沿用主推末速**匀速续推**（`scale` 再走 3~5%、漂移同比延长）。
  速度连续 ⇒ 观众读不出"段落切换"，只觉得镜头一直在走
- 素材尺寸要求：位图素材的原始分辨率要 ≥ 画幅 × `zoomTo`（1080p 画幅推到 1.15 就需要 ≥2210px 宽的截图），否则推进即变糊

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `zoomTo` | 1.10（范围 1.08~1.15） | 推进总量。<1.06 观众读不出在动（等于没运镜）；>1.20 位图发虚、且"推"变成"放大"，抢内容 |
| `pushDur` | 实拍 8~15s / demo 4.2s | 与本段口播等长。同样的 `zoomTo` 压到 3s 就成了"推镜头"（一个事件），拉到 20s 观众彻底察觉不到 |
| `endRate` | 0.6 | 末速占平均速的比。1 = 全程匀速（最安全）；0.6 = 极缓"到位"感；<0.35 像撒手不管，>0 但太小则接不上 hold |
| `driftX` / `driftY` | -13 / -7 px | 焦点微移量。0 = 纯放大（可用但更呆）；>25px 观众会看出"画面在平移"，那是 sway-parallax 的活 |
| `holdDur` | 实拍 3~8s / demo 1.6s | hold 时长随讲述走；关键不是长短而是这段**必须还在动** |
| `transform-origin` / `ORIGIN` | 兴趣点中心（tsx 常量 (316, 424.87)，demo 运行时反推） | 咬兴趣点＝"镜头往它走"；放画面中心＝"整体放大"（弱一档但永远安全，不知道兴趣点在哪时用它）；tsx 换兴趣点要重算 `ORIGIN` |

## 已知坑
- 用 `power2.out` / `power3.out` 之类的标准缓出——末速为零，镜头在到位那一刻**停死**，画面立刻读作卡帧；且前段过快会被读成"冲一下"，缓推的"察觉不到"气质全丢。缓推只能匀速或极缓前载减速。
- 推进量给到 1.3 以上——位图糊掉，观众注意到的是画质而不是你在讲的内容；矢量/DOM 素材虽然不糊，但也会从"推镜"变成"放大"，两回事。
- 推完就停（hold 期零运动）——本卡最常见的错法。观众对"完全静止"极其敏感（motion_check 也会 FAIL）；hold 必须以末速续走。
- 起手就带位移和缩放两个大动作 + 还叠了个入场淡入——缓推是**底噪**不是入场动效。素材的入场交给 media-pop-in / motion-blur-slam-in，缓推从素材落位后才开始。
- `transform-origin` 每段重设一次（比如 hold 期换了个 origin）——origin 一变，画面会瞬间跳一下位置。一条曲线里 origin 必须恒定。
- 素材分辨率不够就硬推——1080p 画幅配 1280px 宽的截图，推到 1.15 已经在放大插值，边缘发毛比不运镜更糟。
- 同一段里既缓推又缓拉（推一半又拉回来）——观众读作"手抖了"或"没想好"。一段一个方向；要反向就换镜头。

## 复用指引
- props：无（`hostSrc` 声明未用）；素材是写死在 JSX 的 DOM 假文章页，`transform-origin` 是按该版式实测的常量 `ORIGIN`，换素材 / 换兴趣点需改源码并重算 `ORIGIN`。要放真截图把 `.page` 内的 DOM 换成一张铺满相机层的 `<Img>`（视频用 `<OffthreadVideo muted>`），`ORIGIN` 按图内兴趣点像素坐标重算。
- Remotion/tsx（skill 首选）：template/cards/slow-push-in.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：`demos/slow-push-in/index.html`。换素材改 `.page` 内的整块 DOM（或换成一张 `<img>` 铺满 `.camera`）；换兴趣点把 `id="poi"` 挂到任意元素上（origin 坐标运行时反推）；节奏全在顶部 `CONFIG`（`zoomFrom` / `zoomTo` / `pushDur` / `holdDur` / `endRate` / `driftX` / `driftY`）。核心可摘走：`CONFIG` + `camEase` + `DemoShell.register` 回调体三段。
- Remotion 移植：整段就是一个 `interpolate`——`const z = interpolate(frame, [0, pushEnd, holdEnd], [1, 1.10, holdZoom], {easing: Easing.bezier(0.33, 0.33, 0.5, 0.85), extrapolateRight: 'clamp'})`，`x` / `y` 同法各一条；套在 `transform: scale(z) translate(x, y)` 上，`transformOrigin` 用兴趣点的百分比坐标。**要匀速就直接 `easing: Easing.linear`**（默认 `Easing.bezier(0.42,0,1,1)` 是 ease-in，会读成加速）；要极缓减速就用上面那条 bezier（末段仍有速度）。`holdZoom = zoomTo + (zoomTo−1)/pushDur × endRate × holdDur`，这样两段速度连续、无需拆 Sequence。图片素材记得 `<Img src={staticFile(...)}/>` 并保证原图 ≥ 画幅 × zoomTo。
- 剪辑软件对应物：剪映——图片素材打两个"缩放"关键帧（100% → 110%），**必须把两个关键帧都设成线性**（右键去掉默认的缓入缓出），位移关键帧同法；AE——Scale 两个关键帧 + 右键 `Keyframe Interpolation → Linear`，锚点（Anchor Point）拖到兴趣点上，或用 Transform 的 `Position` 配合；这就是各家素材站说的 **Ken Burns**（本卡是它的推镜半边，拉镜半边见 [slow-pull-reveal](slow-pull-reveal.md)）；CapCut/Premiere 同理（PR 用 `Motion → Scale` 线性关键帧 + `Anchor Point`）。

## 动效范围
- 属于本卡的：静态素材上的一条**缓推曲线**——`scale zoomFrom→zoomTo`（1.0→1.08~1.15）在 8~15s（demo 压缩到 4.2s）里走完，缓动为匀速或**末速非零的极缓前载减速**（`camEase(endRate)`，这是"不能用 power2.out"的技术答案）；`transform-origin` 咬在兴趣点中心并**全程恒定**；同时叠 5~15px 的焦点微移把兴趣点让向构图位；hold 期**沿用主推末速匀速续推**（速度连续、镜头永不静止）；"相机层是唯一被 transform 的元素、素材本身零动画"这一结构。
- 不属于本卡的：demo 里的灰阶线框文章页（导航条/标题/柱图/引文块/相关阅读栏及其全部文案与排版）、兴趣点选在引文块这一具体决定、`driftX/driftY` 的正负方向（随构图定）、素材的入场动画（属 media-pop-in / motion-blur-slam-in）、页面上的任何标注（属 highlighter-sweep / scribble-annotation / focus-dim-spotlight）。
- 迁移接口：`zoomTo` 定推进量（按素材分辨率上限取值，1.08~1.15）；`pushDur` 对齐本段口播时长（换时长时 `zoomTo` **不变**——推进量是观感常量，时长是节奏变量）；`endRate` 定"匀速 or 极缓到位"；`driftX/driftY` 按画幅宽等比缩放（本卡按 960 宽设计）；兴趣点＝任意页内元素（HTML demo 挂 id、坐标运行时反推；tsx 重算常量 `ORIGIN`）；`holdZoom` 由末速自动推出，不要手填。
- 底色要求：白底即可——本卡零颜色、零装饰，只是一条 transform 曲线，任何底色/任何素材（浅色文档、深色 IDE 截图、照片）上都成立。

<!-- ===== /file: video-talkcraft/references/cards/slow-push-in.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/soft-blur-in.md ===== -->

---
name: soft-blur-in
标题: 柔焦淡入
优先级: P1
代码: template/cards/soft-blur-in.tsx
一句话: 一句话像被镜头对焦出来——整块文字从 blur（字号 1/6）起、边解糊边淡入走满 0.9s，同时字号 22% 的下沉位移只占前 0.3s，逐字错峰仅 1 帧（0.033s）留下一道几乎读不出的左→右扫过感
适用: 需要"轻"的字幕入场——冷静的旁白句、结论句、章节内的小标题；柔和调性的口播（知识区、访谈、品牌片）；素材切换后第一句上屏的字；不适合要打点的重音词与要跟语速的连续跟读字幕
时长: 起手静置 0.3s → 解糊淡入 0.9s（位移只占前 0.3s）→ 逐字错峰 0.033s（9 字整句在 1.47s 处全清晰）→ 收尾定格 1.2s；共约 2.67s
能量: 低
类别: 字幕花字
输入: 文
语义: 论点
素材形态: 无
位置: 任意
props: hostSrc(未使用)
---

## 意图
本库现有的字幕类都在"打点"：`keyword-pop-highlight` 砸重音、`typewriter-reveal` 一个字一个字敲。
它们都有明确的节拍，
所以都有一个共同代价——**它们都在争注意力**。段落里全是这种字，观众的眼睛一直被拽。

这张卡补的是**最低能量档的字幕入场**：字不是"出现"的，是**被对焦出来**的。
观众感知到的是"画面本来就有这句话，只是刚刚看清"，而不是"一句话飞进来了"。
所以它能用在字很多、字很频繁的地方——旁白句、结论句、切素材后的第一句——
连着上五句也不会让人觉得画面在闹。

命门两条：① **解糊与淡入走满 0.9s，位移只占前 33%（0.3s）**。位移与解糊同停会读作
"整块被推上来"（一个有方向的入场），位移先停之后那 0.6s 只在解糊，才是"对焦"这个语义；
② **逐字错峰只有 1 帧（0.033s）**。这个值小到几乎不是"逐字"——9 个字的整句头尾只差 0.27s，
肉眼读作一整块，但仍留下一道极浅的左→右推进感。错峰放大到 0.1s 以上它立刻变成
另一张卡（"逐字柔焦"，能量档整个跳上去，也就不再是本卡了）。

## 动效核心
- **三条属性走同一条时间线，但位移比另两条早停**：
  - `opacity 0 → 1` 与 `filter: blur(字号 1/6) → 0`（demo 72px ⇒ 12px）：走满 `dur = 0.9s`
  - `translateY +12px → 0`：只走 `travel = 0.3s`（= `dur` 的 33%）
  - 三条同起，位移先停 —— **柔性的全部来源**
- **逐字错峰 0.033s（源码 1 帧 @30fps）**：第 i 个字的起点 = `lead + i × 0.033`。
  中文按码点切字（`Array.from`）即逐汉字；标点也算一个字，跟着走是对的
- **缓动全卡一条 `cubic-bezier(0.22, 1, 0.36, 1)`**（easeOutQuint 家族）：起手极快、尾段很长的缓收。
  位移与解糊同族缓动，两者的"减速感"才是一件事。GSAP core 不带 `CustomEase`，
  demo 里用牛顿迭代解 `x(t)=p` 再取 `y(t)`（8 次迭代，误差 <1e-5）
- **模糊量恒为字号的 1/6**（源码 12px @72px 字号；本库 demo 同为 72px ⇒ 12px）。这是比例常量不是绝对值——
  换字号必须等比改，否则大字号下"糊得不够"、小字号下"字被糊没了"
- **每个字是独立的 `inline-block`**：`transform-origin: 50% 55%`（重心略偏下，解糊收尾时字不往上飘）、
  `backface-visibility: hidden`（filter + transform 同时跑时避免 Safari 的合成层抖动）
- **整行 `letter-spacing: -0.05em`**（源码值）：略收紧，柔焦解开后整句读作"一整块"而不是"一排字"
- **`white-space: nowrap` 是硬要求**：每个字都是独立 inline-block，不锁 nowrap 时浏览器会在任意两字之间换行
- **层级**：舞台白底 → 整行 flex 居中 → 单字（唯一被 transform / filter 的元素）

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `dur` | 0.9s | 解糊 + 淡入总时长，本卡的能量旋钮；<0.5s 读作普通淡入（柔焦这层语义丢掉），>1.4s 观众等着字看清、口播已经讲下一句了 |
| `travel` | 0.3s | **位移占 `dur` 的前 33%，本卡第一命门**；= `dur`（位移与解糊同停）立刻读作"整块被推上来"，不再是对焦；0 则完全没有重量、字浮在空中解糊 |
| `stagger` | 0.033s | **逐字错峰，本卡第二命门**；0 = 纯整块（少一道推进感，可接受但更平），>0.1s 变成"逐字柔焦"（另一张卡，能量档跳一整级） |
| `blur` | 字号的 1/6（72px ⇒ 12px） | 起始模糊量，**比例常量**；<字号 1/12 读作轻微失焦、看不出"对焦"过程，>字号 1/4 起手是一团雾、观众不知道要看什么 |
| `rise` | 16px（≈字号 22%，72px ⇒ 16px） | 起始下沉量；0 少了那一点重量（可用但更飘），>字号 40% 读作"上滑淡入"（方向感盖过柔焦） |
| `lead` | 0.3s | 起手静置等口播开口；0 则字与画面同时出现，观众来不及把注意力挪过去 |
| `hold` | 1.2s | 收尾定格——清晰的整句是本卡的落点，按字数给（每字约 0.15s，读完再留半拍） |
| 字数 | 6~12 字 | 更长的句子错峰累积会拉长首尾差（20 字 ⇒ 0.67s，整句读作"扫过"而不是"一块"），要么减 `stagger` 到 0.02s 要么拆句 |

## 已知坑
- 位移与解糊同时结束——整句读作"被推上来"，柔焦对焦这层语义直接消失；位移必须只占前 33%。
- 错峰放大到 0.1s 以上还叫它柔焦淡入——那已经是"逐字柔焦"，能量档从低跳到中，用在旁白句上会抢戏。
- `blur` 写成绝对像素值跟着复用——换字号后大字糊不够、小字糊没了；模糊量必须按字号 1/6 等比。
- 整行不锁 `white-space: nowrap`——每个字是独立 inline-block，浏览器会在任意两字之间换行，起手那一帧整句排版就是错的。
- 给整行（而不是单字）加 `filter: blur()`——整行成为一个合成层，逐字错峰全部失效，且中文行会被整体糊成一条灰带。
- 位移与解糊用两条不同的缓动——两者的"减速感"不再是一件事，慢放下能看出字先停住再单独解糊，割裂。
- 单字忘了 `backface-visibility: hidden`——filter 与 transform 同时跑，Safari 的合成层会在解糊末段抖一下。
- 用在需要重音的句子里——本卡全程没有任何一个字比别的字重，想砸重音请换 `keyword-pop-highlight` 或 `type-contrast-emphasis`。
- 深底上直接抄墨色 `#171717`——本卡在深底上只需把字色反白，但 blur 在深底上"糊出来的光晕"更明显，`blur` 要收到字号的 1/8。
- 重播不重建 DOM 只重置 transform——换文案后字数变了，旧的 span 还在，错峰序列与实际字数对不上。

## 复用指引
- props：无（`hostSrc` 声明未用）；文案在 `CONFIG.text`，换内容需改源码。
- Remotion/tsx（skill 首选）：template/cards/soft-blur-in.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/soft-blur-in/index.html。**换内容只改 `CONFIG.text`** 这一个字符串（6~12 字），
  切字与错峰序列都是运行时算的。能量只调 `dur`（`travel` 要跟着保持约 33% 的比例，两者的比例才是手感）；
  换字号改 `.sb-text` 的 `font-size`，同时把 `CONFIG.blur` 改成新字号的 1/6、`CONFIG.rise` 改成新字号的 22%。
  整句的落位改 `.sb-line`（demo 是 `inset: 0` + flex 整屏居中——**纯文字卡**，不放主持人；
  要让人物留在画面里就把 `.sb-line` 收成一列白区，同时按新宽度把 `font-size` 收回去）。
  `cubicBezier()` 那个解算器是通用的，别的 demo 要 `cubic-bezier` 缓动可以直接抄走。
- Remotion 移植：`template/cards/soft-blur-in.tsx` 是逐帧查表写法（不建时间线，每帧算每个字该多糊），
  在 Remotion 里比搬 GSAP 时间线更直接，可以原样抄。**帧↔秒换算（源码 30fps）**：
  `charDurationFrames 27` ⇒ `dur 0.9s`、`charTravelFrames 9` ⇒ `travel 0.3s`、`staggerFrames 1` ⇒ `stagger 0.033s`。
  每字三个 `interpolate`，全部传 `easing: Easing.bezier(0.22, 1, 0.36, 1)` +
  `extrapolateLeft/Right: "clamp"`（**clamp 不能省**——不 clamp 的话 `local < 0` 的字会算出负 opacity 与负 blur，
  Chrome 里 `blur(-3px)` 直接不渲染，那个字会在起手前闪一下）：
  `local = frame - i * staggerFrames` 是三条 interpolate 共用的局部时钟。
  尺寸换算：源码 `fontSize 72` 是 1280×720 画幅的值；本库 demo 是**纯文字整屏**，960 舞台上直接用 72px，
  所以 `blur 12`、`distance 16` 都与源码同值（比例照旧：blur = 字号 1/6、distance = 字号 22%）。
- 剪辑软件对应物：剪映/CapCut——文本层套"模糊入场"或"渐显"预设**都不对**（前者没有位移、后者没有模糊），
  正确做法是一个文本层 + "高斯模糊"效果打两个关键帧（9 → 0，0.9s）+ 不透明度两键（0 → 100，0.9s）+
  位置两键（下方 12px → 0，**只 0.3s**）；逐字错峰在剪映里做不出来（"逐字显示"是硬切不是柔焦），
  0.033s 的错峰肉眼几乎读不出，**直接放弃错峰做整块版**是合理取舍。
  AE——一个文本层，`Fast Box Blur`（Blurriness 9 → 0）+ `Opacity` + `Position` 三组关键帧，
  曲线在 Graph Editor 里手拉成 `(0.22,1,0.36,1)`（或用 `Easy Ease Out` 再把手柄拉到底，很接近）；
  要错峰就上 `Text Animator`：Blur + Opacity + Position 三个属性，`Range Selector` 的 `Offset` 从 −100% 走到 0%，
  **`Advanced → Ease High` 拉满**（否则默认的线性范围选择器会让错峰读作一道明显的扫光）。
- 与本库同类卡的分工：`keyword-pop-highlight` = 一句里砸一个重音；
  `typewriter-reveal` = 逐字符敲出（有档案感的节拍）；`per-character-rise` = 逐字升起（有方向的入场）；
  **本卡 = 最低能量的整句入场**（不打点、不给方向、不给重音，只把字对焦出来）。
  本卡是唯一可以**连着用五句都不闹**的字幕卡，也因此它不能承担任何强调职责。

## 动效范围
- 属于本卡的：`opacity 0→1` 与 `blur → 0` 走满 0.9s、`translateY` 只占前 0.3s（33%）这条时间纪律；起始模糊量恒为**字号的 1/6** 这个比例；`stagger 0.033s`（源码 1 帧）这个"小到几乎不是逐字"的错峰量级；位移与解糊共用一条 `cubic-bezier(0.22, 1, 0.36, 1)`；`transform-origin: 50% 55%` 这个略偏下的重心；起始下沉 ≈ 字号 22%；单字 `inline-block` + 整行 `nowrap`（拒绝把 filter 加在整行上）这个实现纪律。
- 不属于本卡的：demo 那句「答案往往没那么复杂」的具体文案、72px 字号与 600 字重、`#171717` 这个墨色、`letter-spacing: -0.05em`（拉丁字体的收紧值，中文可以取 0 到 −0.05em 之间任意值）、无衬线字族的选择、白底舞台、以及"整句落在舞台正中"这个落位（画幅正中、下三分之一、字幕安全区都成立）。**demo 是纯文字卡、不放主持人**（2026-08-25 用户定版）——因为本卡的动作是"整句被对焦出来"，人物占位会把注意力从这个极低能量的动作上分走；但应用侧要让人物留在画面里同样成立（句子落在人物旁的留白列或字幕安全区，只要那一带足够空），落位不属于本卡的动效本体。
- 迁移接口：`CONFIG.text` 是唯一的内容入口（6~12 字）；能量只调 `dur`，`travel` 必须跟着保持约 33% 的比例；`blur` 按字号 1/6、`rise` 按字号 22% 等比缩放；`stagger` 是**手感常量，换尺寸换语速都不要动**（字数超过 12 时才减到 0.02s）；`hold` 按字数给（每字约 0.15s）；竖屏用 6~9 字并把字号收到 40~46px（本卡没有横向推挤，唯一约束是整句 `nowrap` 后不超出可用宽度的 90%）。
- 底色要求：白底或深底都成立（深底把字色反白即可）。唯一约束是**底不能有细密纹理或高频细节**——字在解糊的 0.9s 里始终是"半透明的糊块"，底上的细节会透过来与糊块混在一起，观众读不出那是字。渐变底可以（低频），实拍花底不行（要么先压一层半透明底板，要么改用白字加深色描边/投影的高对比字幕）。

<!-- ===== /file: video-talkcraft/references/cards/soft-blur-in.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/source-converge.md ===== -->

---
name: source-converge
标题: 多源汇聚
一句话: 四条细贝塞尔曲线错峰 0.15s 由左向右逐路接通，四个来源胶囊沿各自真实曲线 1.5s 滑向右侧汇聚点并三段式缩小（前 75% 1→.34 慢慢瘦身、后 25% 掉光——"被吸进去"），强调色数据包全程沿线滑行两个整周期；吞并瞬间"一张表"脉冲 +12%，曲线从起点方向擦除，结果胶囊 + 说明行 0.6s 滑到画面正中静置
适用: "把 N 个来源的数据汇到一处"的工作流讲解；"这几件事最后都指向同一个结论"；多渠道 → 一个入口（客服 / 收件箱 / 中台）；倒放即"一分多"。输入只有文字（来源名 / 汇聚点 / 说明），卡自带矢量；人物不参与
时长: 6.2s（0.3 来源胶囊淡入 → 0.5 逐路接通 → 0.8 汇聚胶囊入场 → 1.5–3.0 沿线汇入 → 2.85 吞并脉冲 → 3.25 擦线 → 3.5 说明行 → 3.8 结果居中 0.6s → 静置 → 5.8 同收 0.4s）；成片把汇入起点对到口播讲"汇到一起"的时刻
能量: 中
类别: 数据信息图
输入: 文
语义: 机制
素材形态: 矢量
位置: 中段
props: title, sources, hub, caption
优先级: P2
代码: template/cards/source-converge.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 不吃素材；人在场时整图放人物对侧半幅（layout §4） | ✗ | ✗ 卡自带矢量。来源胶囊可换成 logo 图标（同组同造型），汇聚点可换成产品截图缩略 |

只吃文字：2～6 个来源名 + 汇聚点文案 + 一行说明。

## 常用场景
1. "四个平台的数据，怎么汇成一张表"的工作流讲解（demo 演的）
2. "这几件事最后都指向同一个结论"——来源换成论据，汇聚点换成结论词
3. 多渠道 → 一个入口：客服渠道 / 收件箱 / 数据中台 / 统一账号
4. 倒放即"一分多"：一个源头拆成多条线（tsx 里把 conv 反向即可）

## 意图
库里讲"关系"的卡只有两张：`converging-arrows` 是两支箭头指向一个词（标注语义），`map-route-pin` 是地图上的路径。**没有一张"流程 / 机制图"类的动态图解**。多源汇聚是最简的一张"多对一"：观众看见四个名字**顺着各自的线**滑进同一个点、越靠近越小、最后被吞掉，"汇聚"不用说出口。做对四条：
1. **节点沿真实曲线走**（`getPointAtLength` / 弧长表反查），不是两点间直线插值——直线插值会脱离自己的线，"顺着通路进去"的语义就没了。
2. **三段式缩小、拐点在 75%**：前 3/4 行程慢慢瘦身（1→.34），最后 1/4 掉光——后段尺寸变化率是前段的 4 倍多，这就是"被吸进去"的加速感；拐点挪到 50% 变成"一路缩小"，吞并那一下就没了。
3. **擦除在节点全部消失之后、从起点方向退走**：读作"通路收回"；线先没了节点悬在空中就是 bug。
4. **汇聚完成后结果居中**（2026-09-05 用户定版）：来源都没了，结果还偏在右侧就是"画面空了一半"；胶囊 + 说明行一起 0.6s 滑到 x=480，之后真静止 ≥1.2s——这段静置是本卡的目的，不 hold 等于白汇聚。

## 动效核心
- **几何**（960×540）：标题 26px/700 @ (80, 60)；来源胶囊 128×44 圆角 22（白底 + `#d6d6dc` 1.5 描边，文字 20px/600），中心 x=200、y = 170 / 230 / 310 / 390；汇聚胶囊 152×60 圆角 30（强调色实底 + 白字 22px/700）@ (700, 290)；说明行 22px/600 居中于胶囊下方 y=372。曲线 `M 200,y C 380,y 520,290 700,290`（`#c9c9cf` 2px）——四条只差起点 y，曲率天然不同，汇入角度也不同。
- **接通**：0.3s 起胶囊错峰 0.08 淡入（0.3s）；0.5s 起四条线错峰 0.15 draw-on（`stroke-dasharray = len`，`dashoffset = len×(1−draw)`，各 0.5s `power2.out`）。
- **汇聚胶囊入场**：0.8s，0.4s `power3.out`：opacity 0→1、scale .7→1。
- **数据包**：0.9→3.0s 线性走两个整周期，各路相位 +i×0.13，`cycle = (pk×2 + i×0.13) % 1`，位置 = 曲线上 `cycle×len`，透明度 `1 − |cycle − .5|×.6`（中段最亮、两端淡——避免看到包在起点凭空出现）；0.9 起 0.3s 显、2.8 起 0.2s 隐。
- **汇入**：1.5→3.0s `power2.inOut`，节点位置 = 曲线上 `conv×len`；尺寸 `conv < .75 ? 1→.34 : .34→0`（文字随组缩放，不脱离节点）。
- **吞并脉冲**：2.85s 汇聚胶囊 scale 1→1.12（0.25s `back.out(2)`）→ 3.1s 回 1（0.25s `power2.out`）。
- **擦除**：3.25s `dashoffset = −erase×len`（0.4s `power2.out`），从起点方向退走。
- **说明行**：3.5s 淡入 0.4s。
- **居中**：3.8→4.4s 胶囊与说明行 x 700→480 `power2.inOut`；之后静止到 5.8s。
- **退场**：5.8s 标题 / 胶囊 / 说明行 opacity→0 0.4s `power2.in`，6.2s 结束。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 来源数 | 4（y 170/230/310/390，间距 60~80） | 4 条是曲率差异明显又不打结的甜点；>6 条中间几条贝塞尔几乎重合，汇入角读不出区别；2 条读作对比而非汇聚 |
| `drawStagger` 接通错峰 | 0.15s | 归零读作四条线一起刷出，失去"逐路接通"；>0.3 前后线相差太久像分批 |
| `convDur` 汇入窗 | 1.5s（占全卡 24%，主段落） | `power2.inOut` 缓起是"启动"、缓收是"到位"；换 linear 立刻变匀速传送带 |
| `shrinkKnee` 缩小拐点 | 0.75 | 越靠后吸入越突然；0.5 变"一路缩小"，吞并那一下没了 |
| 数据包周期 | 2 个整周期 | 非整数末帧包停在半路；加密到 4 读作数据流很急、易与节点重叠 |
| `pkPhase` 相位偏移 | 0.13/路 | 0 会看到四个包整齐并进像一次发车 |
| 脉冲幅度 | +12%（back.out(2)） | "接收到了"的量级；>25% 抢过汇聚本身 |
| `eraseAt` | 3.25s（节点 3.0 全消失后） | 早于节点消失 = 线没了节点悬空 |
| `centerDur` 居中 | 0.6s `power2.inOut` | <0.4 像被弹到中间；>0.9 观众在等 |
| 曲线颜色 | `#c9c9cf` 2px | 要够浅，否则四条线抢过节点；胶囊文字 ≥20px（条目档） |

## 已知坑
- 节点两点直线插值——脱离自己的曲线，"顺着通路进去"的语义没了。
- 一路匀速缩小（拐点 0.5）——没有"被吸进去"的那一下。
- 线在节点消失前就擦——节点悬在空中。
- 擦除方向从终点退——读作"线被汇聚点吐回去"；必须从起点方向退（通路收回）。
- 汇聚完成后结果留在右侧——左半画面空着，读作构图事故；结果必须居中再静置。
- 数据包非整数周期——末帧包停在半路。
- 来源换 logo 时混用彩色 logo 与文字胶囊——同组不同造型（layout §8）；要么全 logo 要么全文字。
- 曲线太深 / 太粗——四条线抢过节点与胶囊。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/source-converge.tsx——`title / sources[] / hub / caption`；durationInFrames 198；汇入起点改 `CONFIG.convAt`（对到口播讲"汇到一起"），句长改 `exitAt / end`；来源数 ≠4 时 y 在 170~390 等分。tsx 里沿线取点是纯函数（三次贝塞尔采样 200 段建弧长表再按长度反查），渲染确定，不依赖 DOM 的 `getPointAtLength`。
- HTML/GSAP：demos/source-converge/index.html——`SOURCES` 数组与 `CONFIG`；demo 用 SVG `getPointAtLength`。
- 母本：video-shotcraft `bezier-source-converge-merge`（四路 draw-on → 节点沿曲线三段式缩小 → 徽标脉冲 → 反向擦除）；移植时节点从小图标改成可读的文字胶囊（口播里来源要念得出）、汇聚点从圆徽标改成文字胶囊，并新增"汇聚完成后结果居中"一段。
- 剪辑软件对应物：剪映无路径跟随，只能关键帧逐点凑；AE 用 Position 跟随路径（粘贴 mask path 到 position）+ Scale 表达式 `linear(time, t0, t1, 100, 34)` 两段；Motion / Keynote 的"路径移动"可做节点，线的 draw-on 用 Trim Paths。
- 与 layout.md 的接口：来源列左边缘 136（胶囊左）、标题左边缘 80，两者都吸附栏线附近；汇聚后结果组包围盒中心 x=480（§4 无人物居中）；说明行 22px（body 档以上）；全部元素底边 ≤ 412 < 字幕带。

## 动效范围
- 属于本卡的：逐路 draw-on 错峰 0.15；节点沿真实曲线汇入 + 三段式缩小（拐点 .75）；数据包两个整周期 + 相位偏移 + 中段最亮；吞并脉冲 +12%；从起点方向擦除；结果 0.6s 居中后真静止；同收。
- 不属于本卡的：具体文案、四路的 y 坐标、胶囊样式（白底描边 / 强调色实底）、白底舞台。
- 迁移接口：`title / sources / hub / caption`；1080p 输出线 2→4px、胶囊 128×44 → 256×88、文字 20→40 / 22→44；来源换 logo 时把 `<text>` 换成 `<image>`，尺寸随组缩放不变。
- 底色要求：白底即可；深底舞台时曲线换 `rgba(255,255,255,.2)`、来源胶囊换深 tile（`#272729` + hairline 描边）、汇聚胶囊 accent 换 `#2997ff`。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- 定妆帧三张：接通完（≈1.5s）四条线全到汇聚点、四个胶囊都在起点；汇入中途（≈2.4s）每个胶囊都压在自己那条线上、尺寸已明显缩小；居中后（≥4.4s）胶囊 + 说明行包围盒中心 x=480、偏差 ≤48。
- 擦线开始那一帧（3.25s）画面里不得有任何来源胶囊残留。
- 来源胶囊文字 ≥20@960；胶囊之间等距（60~80），同组同造型。
- 曲线颜色浅于胶囊描边；数据包只有强调色。
- 有人物在场时整图放人物对侧半幅，居中目标改为该半幅中心（x=480 或 1440 的 960 版换算 240 / 720）。

<!-- ===== /file: video-talkcraft/references/cards/source-converge.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/speed-slab-title.md ===== -->

---
name: speed-slab-title
标题: 速度块标题
优先级: P1
代码: template/cards/speed-slab-title.tsx
一句话: 主标题硬现后，副题的斜切色块从**画面外左侧**（起点 −580px，起始帧完全不可见）冲入到位（0.28s power4.out），到位那一帧块左缘一次性张开三道长度不等的速度线（42/30/22px，错峰 2 帧）随后 0.2s 内淡尽——块内的字用 40px 反向补偿被裁一截，读作"字比块慢半拍在追"
适用: 需要"快"这个语义的标题——效率/提速/抢先/立刻的观点句，节奏快的短口播（60s 内）开场或段落重音；不适合冷静的结论句与需要停留阅读的金句
时长: 起手静置 0.4s → 主标题硬现 0.18s → 呼吸 0.08s → 块冲入 0.28s（字追赶 0.34s）→ 速度线张开+淡出 0.42s → 收尾定格 1.5s；共约 2.86s
能量: 高
类别: 字幕花字
输入: 人(可选), 文
语义: 钩子, 标题
素材形态: 无
位置: 任意
props: hostSrc
---

## 意图
"块从旁边冲进来"本身只是一个平移入场，它给的是**方向**不是**速度**——观众读到的是"这个块从左边来"。
让它读成速度需要一个物理线索：**残影**。三道平行短线在块停住的那一帧从块的左缘长出来，
再立刻消失——那是"块刚才走得太快，空气里还留着痕"这个视觉谎言。
这张卡的全部信息量都在那 0.4 秒的线上。

命门两条：
① **速度线必须在 0.2s 内消失**。残影的定义就是"该消失的东西还在"，
线留在屏上超过半秒它就变成了装饰性的三道杠——一个平面 logo 元素，而不是运动痕迹。
留下来的版本不是"更好看的本卡"，是另一张卡（装饰性斜块标题），能量档反而降了。
② **块内的字要慢半拍**。字与块一起硬绑在一起进场，整体读作一张 PNG 在平移；
给字一个 40px 的反向补偿（块 `overflow: hidden` 把它裁掉一截）+ 比块长 0.06s 的追赶时长，
字就获得了自己的惯性——观众读到的是"块带着字冲进来，字被甩在后面又追上"。
这 40px 是本卡"贵"的来源，也是最容易被省掉的一步。

## 动效核心
- **四拍，其中拍③④ 是同一件事的两半**：
  - 拍① `t=0.40` 主标题：`scale 1.04 → 1` + `opacity 0 → 1`，`0.18s power3.out`，无位移，
    `transform-origin: 0% 50%`（护住左基线）
  - 拍② `t=0.66` 紫块：`x -580 → 0`，`0.28s` **`power4.out`** —— 全卡唯一用 power4 的地方，
    它的"起手极猛、尾段极长"就是刹车感。
    **起点必须让块完全出画**：判据 `|slabFrom| > 块右缘距舞台左缘的距离 ÷ cos(斜切角)`
    （本 demo 块右缘 x≈562、−3° ⇒ 阈值 563，取 −580 留 17px 余量）。
    起始帧露出块的任何一部分都读作"块本来就在那儿，只是滑了一下"，"从画外冲进来"就没了
  - 拍②b 同帧起 块内字：`x -40 → 0`，`0.34s power3.out` —— 比块**长 0.06s**、缓动**低一阶**，
    两条都是"字更慢"的实现手段（只改时长不改缓动也成立，但慢感弱一半）
  - 拍③ `t=0.94`（= 块停住那一帧）三道速度线：各自 `scaleX 0 → 1`（`transform-origin: 100% 50%`
    ⇒ 从块左缘**往左长**），单道 `0.09s power3.out`，线间错峰 `0.067s`（2 帧 @30fps）
  - 拍④ 每道线张开结束立即 `opacity 1 → 0`，`0.20s power2.in`（**in** 不是 out：先慢后快地抹掉，
    像被空气吃掉；用 out 会读作"刻意淡出的装饰"）
- **速度线的长度必须不等**：`42 / 30 / 22px`（≈ 0.55 / 0.39 / 0.29 × 字号）。
  等长三道线是印刷符号（≡），不等长才是拖尾。落位比例 `0.24 / 0.50 / 0.76 × 块高`——
  中间那道最长会读作箭头尾，所以最长的那道放最上面
- **速度线与块共享同一个静态斜切**：三道线是 `.ss-row`（`rotate(-3deg)`）的子元素，
  所以天然与块平行。分开各自 rotate 一定会对不齐，且改角度要改四处
- **两行之间的净空是硬约束**：块斜切 −3° 后**右上角是最高点**，它正好落在主标题末字下方。
  `.ss-row` 的 `margin-top: 36px` 让块的最高点离主标题**字面底**（不是行盒底）
  还有 **14px** 净空（12~16px 是甜点区）。按 `margin-top` 直觉给 14px 的话
  块的右上角会压进主标题末字 7px —— 行盒底与字面底差十几 px，必须按字面算
- **块的 `overflow: hidden` 是硬要求**：字的 40px 反向补偿靠它裁切才看得出来。
  不裁切的话字只是"从块外面挪进来"，读作两个物件各自平移
- **`x` 的层级分离**：块被 `x` 平移（`.ss-slab`），字**在块的局部坐标里**再被 `x` 平移（`.ss-slab-t`）——
  两级 transform 叠加，字的实际位移 = 块的位移 + 自己的补偿。写成同一个元素做不出追赶
- **三道线的落位按块高度的 0.24 / 0.50 / 0.76 取**：HTML demo 运行时读 `slab.offsetHeight`；tsx 写死 `SLAB_H = 103`（76px × 1.06 + padding 10 + 12），换字号要同步改它
- **层级**：舞台白底 → 主标题 → 副题行（静态斜切）→ 速度线（块左侧，绝对定位 `right: 100%`）+ 紫块（内含被裁的字）
- **强调色只上在块与线上**：`#7A5AF8`（参考图紫系）。主标题黑 `#1d1d1f`，块内字反白

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `lineFade` | 0.20s | **本卡第一命门**；>0.5s 线成了装饰性三道杠（速度语义消失，卡降级），0 则线闪一帧看不见（残影要"被看到正在消失"） |
| `lagPx` | 40px（≈0.53 字宽） | **本卡第二命门**，字的反向补偿量；0 则块与字读作一张 PNG 平移，>0.9 字宽字在块里露出空白一截（观众读作"字没跟上是 bug"） |
| `lagDur` | 0.34s（= 块的 1.2 倍） | 字追上块的时长；= `slabDur` 则字与块同停（追赶感消失），>1.6 倍字在块停后还在爬，读作字幕加载慢 |
| `slabFrom` | -580px | 块的起点，**必须完全在画外**：`|slabFrom| > 块右缘距舞台左缘 ÷ cos(斜切角)`（本卡 563，取 -580）。给小了起始帧就能看见块的一截（用户 2026-08-25 审片反馈的错法），"从画外冲进来"直接降级成"原地滑一下" |
| `.ss-row` 的 `margin-top` | 36px（净空 14px） | 两行的垂直间距；块斜切后**右上角**是最高点，它离主标题**字面底**至少留 12~16px。按行盒直觉给 14px 会让块压进主标题末字 7px（用户 2026-08-25 审片反馈）；>60px 两行脱开，副题读作独立的第二个元素 |
| `slabDur` | 0.28s | 块冲入时长，能量旋钮；<0.2s 块像瞬移（没有"冲"的过程），>0.4s power4 的猛劲被摊平，读作普通滑入 |
| 块的缓动 | `power4.out` | **全卡唯一的 power4**；换成 power2 立刻读作"滑进来"（速度线就没有存在理由了） |
| `lineLens` | [42, 30, 22] px | 三道线长度，**必须不等**；等长读作印刷符号 ≡，长度差 <5px 等于等长；最长那道 >0.8 字宽会长出画面左边 |
| `lineStagger` | 0.067s（2 帧） | 线间错峰；0 三道线一起张开（读作一个整块图形），>0.15s 读作三个独立动效依次出现 |
| `lineOpen` | 0.09s | 单道线张开时长；>0.2s 线"画出来"的过程被看清，残影变成了手绘线（那是 B 组的语言） |
| `hold` | 1.5s | 收尾定格；本卡节奏快，hold 给到 2s 以上会让"快"这个语义在等待里稀释 |

## 已知坑
- 速度线留在屏上（不淡出或淡出 >0.5s）——它从运动残影变成装饰性三道杠，本卡最贵的那 0.4s 白做了。
- 字与块硬绑一起进场（省掉 `lagPx`）——整体读作一张 PNG 在平移，块和字之间没有惯性差，慢放下一眼是模板。
- 块忘了 `overflow: hidden`——字的反向补偿变成"字从块外面挪进来"，起手那一帧字露在块左边，构图直接错。
- **`slabFrom` 给得不够远（起始帧能看到块的一截）——2026-08-25 用户审片实测的错法**。
  原来的 −180 只够块走 180px，起始帧块的右侧大半还在画内，读作"块本来就在那儿滑了一下"，
  "从画外冲进来"这个前提就没了。起点按判据算：块右缘距舞台左缘 ÷ cos(斜切角)，再留一点余量。
- **副题块压住主标题**——块斜切后右上角是最高点，正好顶在主标题末字下方。
  两行间距按 `margin-top` 直觉给（14px 那档）时块会压进主标题字面 7px。
  净空要按**字面底**（不是行盒底）算，留 12~16px。
- 三道速度线等长——读作印刷符号 ≡ 或"信号强度图标"，不是拖尾。
- 速度线用 `power2.out` 淡出（而不是 `power2.in`）——淡出的前半段很慢，线在屏上"赖着"，读作刻意的装饰淡出而不是被抹掉。
- 三道线各自单独 rotate（不挂在块的斜切容器下）——一定与块不平行（浮点误差 + 各自的 origin 不同），且改斜切角要改四处。
- 块用 `power2.out` 冲入——刹车感没了，速度线失去存在理由（没有"太快"这件事哪来的残影）。
- 线的 `transform-origin` 取左端（`0% 50%`）——线会从块的左缘往**左端点**长，读作"线在往右缩"，方向完全反了。
- 块内字的 `x` 与块的 `x` 写在同一个元素上（两个值相加）——做不出追赶：单个 transform 只有一个位置，追赶需要两级坐标叠加。
- 速度线用强调色之外的颜色（比如灰）——它是块的残影，必须与块同色；灰线读作"另一个元素"，且在白底上几乎看不见。
- 主标题也加冲入（想"整体统一"）——一屏两个方向性入场，观众不知道该看哪个，而且主标题一动，副题块的"冲"就不再是唯一的运动。

## 复用指引
- props：仅 `hostSrc`；两行文案在 JSX 常量里，块高 `SLAB_H` 是常量，换内容 / 换字号需改源码。
- Remotion/tsx（skill 首选）：template/cards/speed-slab-title.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/speed-slab-title/index.html。**换文案改两处 HTML 文本**（`#ssL1` 主标题 4~7 字、
  `#ssSlabT` 副题 4~7 字）——块宽由字自动撑出，三道线的落位按块高度实测，都不用改常量；
  **但块宽一变 `CONFIG.slabFrom` 要重算**（判据见参数表：块右缘距舞台左缘 ÷ cos(3°) + 余量）。
  换强调色改两处：`.ss-slab` 的 `background` 与 `.ss-line` 的 `background`（必须同色）。
  换字号改 `.ss-l1` 与 `.ss-slab-t` 的 `font-size`（两处同值），同时按比例改 `CONFIG.lagPx`（约 0.53 字宽）
  与 `CONFIG.lineLens`（约 0.55/0.39/0.29 字宽）。
  能量只调 `slabDur`；`lineFade` 与 `lagPx` 是命门常量，换尺寸换语速都不要动。
- Remotion 移植：**关键是两级 transform 不能塌成一个**——外层 div 吃块的 `x`，内层 span 吃字的 `x`。
  30fps 换算：`lead 12f`、`l1Dur 5f`、`gap 2.4f≈2f`、`slabDur 8.4f≈8f`、`lagDur 10f`、
  `lineStagger 2f`、`lineOpen 2.7f≈3f`、`lineFade 6f`。
  块 `translateX: interpolate(f, [26,34], [-580,0], {easing: Easing.out(Easing.poly(4)), ...clamp})`
  （`-580` 按同一判据重算：块右缘距画面左缘 ÷ cos(斜切角)；Remotion 里画外起点写死成常量即可）
  —— `Easing.poly(4)` 就是 power4；字用 `Easing.out(Easing.cubic)` 跑 `[26,36]`。
  三道线各自两段：`scaleX: interpolate(f, [34+2i, 37+2i], [0,1], {...clamp})` 与
  `opacity: interpolate(f, [37+2i, 43+2i], [1,0], {easing: Easing.in(Easing.quad), ...clamp})`
  （**`extrapolateRight: 'clamp'` 不能省**——否则 hold 期算出负 opacity，Chrome 里线会闪回来一帧）。
  块的 `overflow: hidden` 在 Remotion 里同样必需，且要写在吃 `x` 的那一层上（不是它的父层）。
- 剪辑软件对应物：剪映/CapCut——块与字必须是**两个层**（块用色块贴纸、字用文本层），
  两层都打"位置"关键帧，字的起点比块多偏左 40px、结束帧比块晚 2 帧；块层套"蒙版-矩形"贴合块边缘做裁切
  （剪映的贴纸没有 overflow，裁切只能靠蒙版）。三道速度线用三个细长色块贴纸，
  各打"缩放"X 通道 0 → 100 + "不透明度" 100 → 0，起点各错 2 帧。
  **剪映的"速度线"特效不要用**——它是全屏径向线，是漫画爆点不是块的残影。
  AE——块层 `Position` 两键配 `Easy Ease Out` 且手柄拉到 90%（模拟 power4）；
  字层作为块层的子级（parent），自己再打一组 `Position` 关键帧，两级叠加天然成立；
  三道线用 `Scale` X 通道 + `Opacity`，三层用 `Sequence Layers`（间隔 2 帧）自动错峰。
- 与本库同类卡的分工：`slab-punch-title` = 块**原地从中心撑开** + 字砸（语义是重量/结论）；
  `motion-blur-slam-in` = 素材带动态模糊砸入（对象是素材卡不是标题，且用模糊而不是残影线）；
  `alt-block-lines` = 两块各自从左展开刷出字（对句关系，无速度语义）；
  `whip-pan-transition` = 整屏甩镜（转场，不是标题）；
  **本卡 = 唯一用"残影线"表达速度的标题卡**，语义锚在"快"这个词上，用在不需要"快"的句子上就是空转。

## 动效范围
- 属于本卡的：速度线是**冲入的残影**这个定义（张开后 0.2s 内必须淡尽，`power2.in` 抹掉而非 `out` 淡出）；三道线**长度不等**（0.55/0.39/0.29 字宽）+ 错峰 2 帧 + `transform-origin: 100% 50%` 从块左缘往左长这组形状纪律；块内字 `lagPx 40px` 反向补偿 + `lagDur` 比块长 20% 的"追赶感"；块的 `power4.out`（全卡唯一 power4）这条刹车曲线；**块的起点必须完全在画面外**（判据：`|slabFrom| > 块右缘距画面左缘 ÷ cos(斜切角)`，起始帧不许露出块的任何一部分——用户 2026-08-25 定版）；**副题块不许压到主标题字面**（块斜切后右上角是最高点，离主标题**字面底** 12~16px 净空，按字面而非行盒算——用户 2026-08-25 定版）；块用 `overflow: hidden` 裁切字、字与块**两级 transform** 这条实现纪律；速度线挂在块的静态斜切容器下（共享斜切、天然平行）；三道线按块高度比例落位（demo 运行时量块高，tsx 用常量 `SLAB_H`）；主标题"硬现且不参与任何方向性运动"这个分工。
- 不属于本卡的：demo 那两句「效率不是更快 / 而是不做错事」的具体文案、76px 字号与 700 字重、`#7A5AF8` 这个紫（同色系任取，参考图只是一个样本）、-3° 这个具体斜切角、`padding: 10/20/12` 这组像素、块的 4px 圆角、线的 7px 粗与 4px 圆头、右侧主持人（数字人）占位、以及"标题落在左侧白区、左边距 84px"这个落位。`slabFrom -580` 与 `.ss-row` 的 `margin-top: 36px` 这两个**具体数值**也不属于本卡（它们是按本 demo 的块宽与字号算出来的）——属于本卡的是那两条**判据**（完全出画 / 净空 12~16px）。
- 迁移接口：内容入口是两段纯文本（各 4~7 字），块宽自动贴合；能量只调 `slabDur`（0.2~0.4s）；`lineFade 0.2s` 与 `lagPx ≈0.53 字宽` 是命门常量，只随字号等比缩放、不随语速调；换字号时 `font-size`（两处同值）、`lagPx`、`lineLens`、`.ss-slab` 的 padding 按同一比例缩放；换强调色改 `.ss-slab` 与 `.ss-line` 两处 `background`（必须同色）；`slabFrom` **不是手感参数，是算出来的**——按 `块右缘距画面左缘 ÷ cos(斜切角)` 再留 15~20px 余量，换文案/换字号/换落位都要重算（块宽变了阈值就变了）；两行净空（`.ss-row` 的 `margin-top`）按主标题**字面底**到块**右上角**留 12~16px 重算，换字号要跟着调。竖屏字号收到 52~60px，`slabFrom` 按新的块右缘位置重算（竖屏块窄、阈值小得多）。
- 底色要求：白底即可。深底也成立（主标题反白、块与线保持强调色），但深底上残影线的可见度更低——`lineFade` 要放宽到 0.26s 才看得到"正在消失"这个过程。**渐变底与实拍花底不行**：速度线只有 7px 宽 0.2s 寿命，底上任何高频细节都会把它吃掉。

<!-- ===== /file: video-talkcraft/references/cards/speed-slab-title.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/split-60-40-story.md ===== -->

---
name: split-60-40-story
标题: 60/40 主从分屏
一句话: 左 60%（576px）一条素材缓推 1→1.06 做主（时长 = 镜头），3px 白中缝，右 40% 标题 30px 两行 + 三枚 pastel chip（24px 粗）按口播 1.0 / 1.6 / 2.2s 逐枚 back.out 弹出；6.8s 素材、中缝、字全部同帧收齐
适用: "看着它干活，边听边记要点"——录屏 / 实拍 + 三条要点；人 + 要点（左格放口播本人）；产品演示 + 三个卖点；教程步骤旁白。要点 ≤4 条
时长: 6.8s（0.3 标题 → 1.0 / 1.6 / 2.2 三枚 chip → 6.28~6.40 文字组尾对齐退场、6.4 素材 + 中缝退 → 6.8 收齐）；成片 = 口播句长，缓推 duration 随镜头伸缩
能量: 中
类别: 素材呈现
输入: 人(可选), V, 文
语义: 步骤, 列举
素材形态: 单条视频, 透明通道
位置: 任意
props: src, hostSrc, title, chips, chipBg
优先级: P1
代码: template/cards/split-60-40-story.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✓ 左格放口播本人（`hostSrc` alpha 视频，站格底、随格缓推） | ✓ 左格主料：录屏 / 实拍（`src`，cover 铺满） | 需改源码：tsx 的 `src` 只走 `<OffthreadVideo>`，放图片要把它换成 `<Img>`（见复用指引） |

左 60% 视频 / 人物直接注入、图片换一个组件即可，右 40% **永远是文字**。

> **占比纪律（2026-09-21）**：它只属于"主从"关系，不是"B-roll + 文字"的默认容器——一支 11 镜的片 8 镜用它 + 左下圆章，用户评"排版过于固定"。
> 全片 ≤1/3、不连用 3 镜（preflight FAIL）；相邻镜换 shot-design.md §2⑦ 的其他式（出血全屏 / 装框单侧 / 底床 / 截帧指认 / 多图编排 / 素材短暂独占）。

## 常用场景
1. 看视频讲要点：录屏 / 实拍 + 三条 chip（demo 演的："它一晚上干了三件事"）
2. 人 + 要点：左口播本人、右要点
3. 产品演示 + 三个卖点
4. 教程步骤旁白

## 意图
多素材调研第一条"排版先定关系"：主次 → 一主两辅、对比 → 双分屏、**主从 → 60/40**。左边是主（一条在动的素材，观众看着它），右边是从（要点，观众边听边记）——不是 50/50 的对比。做对四条：
1. **左格缓推 duration = 镜头**，速率恒定、末速非零（`slow-push-in` 的口径：镜头永不停死）。
2. **chip 按口播逐枚出现**（0.6s 一枚，back.out 过冲 = "拍上去"），三枚一起淡入就是 PPT。
3. **右栏左边缘吸附同一栏线**：标题首字左边 = chip 色块左边（x 620@960，layout.md §3）；chip 同高同 padding；底板 pastel 三色**同组不重复**（§7 的反例就是三枚白底同色 chip）。
4. **chip 字号 24@960 ≈ 48@1080p**，满足条目档 ≥40——"太小相当于没有"是用户 2026-09-05 抓出的缺陷。

## 动效核心
- **几何**（960×540）：左格 x 0~576、高 540，`overflow: hidden`（推出去的部分不越过中缝）；中缝 x 576~579 白；右栏从 x 620 起：标题 top 78（30px 700 行高 1.3 两行）、chip top 216 / 290 / 364（高 ≈54，间距 20）、padding 10×20、圆角 14、底 `#E8F0FF / #FFE9F0 / #E6F7F2`、字 24px 700 `#1d1d1f`。
- **左格缓推**：相机层 `scale 1→1.06` linear、duration = `end`（6.8s）、origin 50% 50%；`hostSrc` 时人物站格底（视频高 = 格高 88%），同样被缓推。
- **标题**：0.3s 起 0.5s `power3.out`：opacity 0→1、y 12→0。
- **chip**：`1.0 + i×0.6` 起各 0.45s `back.out(1.7)`：opacity 0→1、scale .9→1、y 10→0。
- **退场（尾对齐）**：文字组 6.28 / 6.32 / 6.36 / 6.40 依次 0.4s `power2.in`（标题先走、最后一枚 chip 6.8 收完）；素材 + 中缝 6.4~6.8 `power2.in`；6.8 一帧内全部收齐。
- demo 里左格的示意视频（Mixkit 打字实拍，demos/_lib/media）是演示语境，成片用 `src` / `hostSrc`。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `split` 左格宽 | 576（60%） | 55~65%；≤50% 主从颠倒读作对比；右栏宽 ≥ 最长 chip + 2×padding |
| `push` 缓推终点 | 1.06 | 1.04~1.08；>1.1 录屏文字发虚；速率 = 0.06/end，句子越长推得越慢 |
| `gap` chip 间隔 | 0.6s | 口播逐条的节奏 0.5~0.7；>1.0 散成三张卡 |
| `pop` 单枚弹出 | 0.45s | back.out 过冲即"拍上去"；<0.3 弹不起来 |
| chip 字号 | 24@960 | ≈48@1080p 条目档；<20@960 等于没有 |
| chip 数 | 3（≤4） | tsx `CHIP_TOP` 出厂 3 项，4 条改成 200 / 268 / 336 / 404；≥5 条换 `chapter-progress-list` |
| `chipBg` 底板 | 三 pastel | 同组不重复；强调色全片只有一个，chip 底不算强调色 |
| `stagger` 退场错峰 | 0.04 | 尾对齐到 end；0 = 一起收也成立 |

## 已知坑
- 三枚 chip 一起淡入——PPT。
- chip 底板同色（三个白框）——读作三个一样的空框（layout.md §7 反例）。
- chip 文字 <20@960——"太小相当于没有"。
- 缓推层不裁切——推出去的素材越过中缝压进右栏（实验室原型没裁，入库版左格 `overflow: hidden`）。
- 缓推写固定秒数：比镜头短素材停死、比镜头长字退了素材还在动——duration 必须 = 镜头。
- 标题与 chip 左边缘各自为政（chip 用 margin 硬对齐文字）——参差；两者容器都吸附 x 620。
- 左格放人物却让人物顶到格顶 / 被格边切——人物容器高 88% 居中，576 宽足够；不够就收窄右栏文案，不缩人。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/split-60-40-story.tsx——`src`（B-roll）/ `hostSrc`（口播本人，优先于 src）/ `title` 行数组 / `chips` / `chipBg`；durationInFrames 216；句长改 `CONFIG.end`（缓推与退场自动跟随）。tsx 的 `src` 仅走 `<OffthreadVideo>`（视频）；要放图片把它换成 `<Img>`（Remotion 自带），其余不动。chip 的 top 写死在 `CHIP_TOP`（3 项），第 4 枚按参数表加一项。
- HTML/GSAP：demos/split-60-40-story/index.html——`CONFIG` 是全部节奏；`.cam .ph` 整块换成 `<video class="fill">` 即真素材；chip 的 `top` 与 `background` 内联可直接改。
- 剪辑软件对应物：剪映画中画裁切到 60% + 关键帧缩放 100→106 拉满镜头 + 文字模板"标签"逐条入场；CapCut "Split Screen" 无 6:4 预设，同样手动裁；AE 左层 Scale 线性关键帧 + 右侧 shape+text 预合成套 Overshoot。
- 与 layout.md 的接口：右栏 x 620@960 = 1240@1080p，与 8 栏线 1269 相差 <32 属可接受（60/40 的天然栏线落在 1152 + gutter）；chip ≥ 条目档（§5）；同组底板 pastel（§7）；左格素材内文字不与右栏相撞（§6）。

## 动效范围
- 属于本卡的：60/40 主从关系与 3px 中缝；左格缓推 1→1.06 duration = 镜头、格内裁切；标题 0.3 升入；chip 0.6 逐枚 back.out 弹出；右栏左边缘同栏线、chip 同高同 padding、pastel 同组不重复；尾对齐同收编排。
- 不属于本卡的：示意视频（演示语境素材，demos/_lib/media，不属于本卡）、示例文案、三种 pastel 的具体色值（可换但同组不重复）、人物视频、白底舞台。
- 迁移接口：`src` / `hostSrc` / `title` / `chips` / `chipBg`；`CONFIG.end` 随句长；竖屏输出改上下 60/40（素材在上、chip 在下）；1080p 输出 px ×2。
- 底色要求：白底即可；实验室原型右栏 `#f5f5f7`，入库改白底后中缝与右栏同色——中缝仍保留，右栏换浅色底板时它就是分界线。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- 右栏左边缘：标题首字左边与 chip 色块左边同一 x（620@960），偏差 >4px 返工；chip 同高（padding 10/20）同圆角。
- chip 字号 ≥24@960（≥48@1080p）；缩到 390 宽复看仍可读。
- 左格缓推末帧素材仍在格内（`overflow: hidden`），中缝上无素材溢出。
- `hostSrc` 时人物不被格左右边切、呼吸边 ≥10（verify 自动查）；人脸安全区在左格内、不与右栏相撞。
- 左格素材自带文字（录屏 UI）不与右栏相撞；有则把 `push` 降到 1.04 或换素材裁切位。

<!-- ===== /file: video-talkcraft/references/cards/split-60-40-story.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/split-compare-slider.md ===== -->

---
name: split-compare-slider
标题: 对比双分屏（滑动揭示）
一句话: 两张同构图的图叠放，上层用 clip-path 裁掉右侧，一条 3px 白分割线（带圆钮）与裁切边由同一个进度值驱动——左图整屏起手 0.6s → 1.4s 滑到中线 → 停 1.5s → nudge 到 42% 再回中 → 滑到 8% 几乎全露右图 → 回中停 1s → 与两图同收；两图共用一条 1→1.04 的极慢推
适用: "前 / 后""新 / 旧""A / B"两张同构图的对比时刻（同机位两段视频要按复用指引换组件）；修图调色、改造前后、界面改版、参数 A/B；冷静举证调性
时长: 9.5s（起手 0.6 → 揭示 1.4 → 停 1.5 → nudge 0.45×2 → 近端 1.0 → 停 1.5 → 回中 1.0 → 停 1.0 → 退场 0.4）；成片两处停留按口播伸缩
能量: 中
类别: 素材呈现
输入: 图
语义: 对比
素材形态: 横屏, 多图
位置: 任意
props: srcBefore, srcAfter, labelBefore, labelAfter
优先级: P0
代码: template/cards/split-compare-slider.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| 不适用（人不需要"前后对比"，且人物会被分割线切开） | 需改源码：tsx 仅 `<Img>`，两段**同机位**视频要把 `<Img>` 换成 `<OffthreadVideo>`（上下两层同帧对齐） | **默认输入**（两张**同构图**的图；demo 用同一张两套滤镜） |

命门是两层素材 100% 同构图——机位、裁切、缩放全部一致，分割线扫过时被比较的才是"内容"。不同构图的两张图请用 `hero-duo-layout` 一主两辅或 `rack-focus-pair` 焦点接力。

## 常用场景
1. 修图 / 调色前后：同一张图两套色（demo：左"调色前"灰暗、右"调色后"通透）
2. 改造前后：房间、桌面、界面改版（同机位重拍 / 同尺寸截图）
3. 新旧版本 / 两个时间点同机位（v1 vs v4 首页、去年 vs 今年的同一角）
4. 两种参数同一场景（画质设置 A/B、两套字体 / 配色方案）

## 意图
口播讲"看，改完之后"时，把两张图左右并排是最弱的做法——观众要在两张小图之间来回找对应位置，比的是"位置"不是"内容"。
滑动揭示把两张图叠在同一机位上，分割线扫过的每一像素都是同一处的前后，对比不用找。做对的命门：
1. **裁切不移动**：上层用 `clip-path: inset(0 X% 0 0)` 裁掉右侧，两张图本体一像素不挪；移动两张图（一张往左推、一张往右拉）会让观众以为构图变了。
2. **分割线与裁切边同源**：两者由同一个进度值 `p` 驱动，永不错位；分开写两条 tween 迟早差一帧。
3. **分割线必须动过，但不来回扫不停**：揭示到中线 → 停 → 一次 nudge（"看右边"）→ 一次近端（几乎全露"后"）→ 回中。四个动作各有叙事职责，多一次就成了滑块玩具。
4. **标签只在该侧露出 ≥40% 时才亮**：露出一条缝就挂标签，读作"这是什么"还没看清就被告知。

## 动效核心
- 结构三层：下层 `.pane.r`（"后"图，整屏铺满）→ 上层 `.pane.l`（"前"图，同尺寸同位，`clip-path: inset(0 (100−p)% 0 0)`）→ `.divider`（3px 白 + `0 0 18px rgba(0,0,0,.6)` 阴影，`left: p%`，居中 46px 白圆钮带双向箭头）；两枚标签 `.lbl`（20px 700 白字，`rgba(0,0,0,.45)` 胶囊，距顶 48、距侧边 48）。
- 进度值 `p` = 左图露出的百分比（100 = 左图整屏，0 = 右图整屏）。全部状态由 `p` 一次写出：裁切边、分割线、左标签 `p ≥ 40` 可见、右标签 `100 − p ≥ 40` 可见。
- 时间表：`0–0.6` 左图整屏（先看清"前"）→ `0.6–2.0` p 100→50 `power3.inOut` → `2.0–3.5` 停（观众来回看两边）→ `3.5–3.95` p 50→42 `power2.inOut`（nudge，"看右边"）→ `4.0–4.45` 回 50 → `4.5–5.5` p 50→8 `power3.inOut`（几乎全露"后"）→ `5.5–7.0` 停 → `7.0–8.0` 回 50 → `8.0–9.0` 有意停留 → `9.0–9.48` 退场（标签 → 分割线 → 两图，错峰 0.04，`power2.in` 0.4s）。
- 两图共用一条极慢推 `scale 1 → 1.04`，`ease: none`，**时长 = 镜头**（9.48s）——两层同一条曲线才不会在分割线处错位。
- 缓动：揭示 / 近端两段用 `power3.inOut`（起停都柔，"手推滑块"的手感）；nudge 短程用 `power2.inOut`。
- demo 用同一张示意图（Picsum 1043，demos/_lib/media）两套滤镜保证 100% 同构图：左 `saturate(.3) brightness(.82) contrast(.9) grayscale(.4)`、右 `saturate(1.25) contrast(1.06)`；tsx 只传一张图（或两张相同）时自动套这两套滤镜，传两张不同图则不套。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `lead` 起手 | 0.6s | 左图整屏先让观众看清"前"；<0.4 观众还没看清就被揭示，>1.0 读作静止图 |
| `slide` 揭示 | 1.4s | 分割线从右端到中线；<1.0 像"擦除转场"，>2.0 拖 |
| `hold` 停留 | 1.5s（≥1.5） | 到中线后观众要左右各看一眼；成片按口播这句话的长度伸缩 |
| `nudge` | 42% | 中线往左晃 8%，语义是"看右边"；>15% 变成第二次揭示 |
| `farLeft` 近端 | 8% | 几乎全露"后"但留一条"前"作参照；0 = 完全切换，参照丢失 |
| `farDur` | 1.0s | 近端往返单程；比揭示短是通则（第二次不用再教观众规则） |
| `tailHold` | 1.0s | 回中后的有意停留（不是空尾）；成片 = 讲完这一句 |
| `push` 极慢推 | 1.04 | 两图共用；>1.06 位图边缘发虚、且推进抢了对比的戏 |
| `showAt` 标签阈值 | 40% | 该侧露出多少才亮标签；<25 露一条缝就挂字，>50 中线时两枚都不亮 |
| 分割线 | 3px 白 + 46px 圆钮 | 圆钮是"这是可滑动的分界"的暗示；去掉圆钮读作画面裂了一道 |

## 已知坑
- 移动两张图而不是裁切上层——左图往左走、右图往右来，观众读到的是"构图在变"，对比的对象从内容变成了位置。
- 分割线与裁切边分别 tween——差一帧就露出一条错位的缝或把"前"图切掉一线。
- 分割线来回扫不停（滑块玩具）——每次扫过都是一次注意力重置；本卡最多四个动作（揭示 / nudge / 近端 / 回中）。
- 一上来就在中线（没有整屏起手）——观众没看过完整的"前"，不知道后面在比什么。
- 两张图不同构图 / 不同缩放——分割线扫过时两边对不上，观众以为是两张图拼接；这种素材用 `hero-duo-layout` 或 `rack-focus-pair`。
- 标签在露出一条缝时就亮——"这是什么"还没看清先被告知；≥40% 再亮。
- 两图各自一条推镜——分割线处两边缩放不同步，缝里错位。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/split-compare-slider.tsx——`srcBefore` / `srcAfter` 两张真图（`<Img>` cover；要放视频把两处 `<Img>` 换成 `<OffthreadVideo>`（Remotion 自带）、两层同帧，其余不动），`labelBefore` / `labelAfter` 文案；只传一张（或两张相同）自动套"前 / 后"两套滤镜；时长 `meta.durationInFrames = 296`；两处 `hold` 要长就改 `CONFIG.hold` / `CONFIG.tailHold`（时间表由 CONFIG 推出，不用手改 T）。
- HTML/GSAP：demos/split-compare-slider/index.html——`.pane.r` / `.pane.l` 里的 `.ph` 整块换成 `<img>`（两张同尺寸），`.lbl` 换文案；节奏全在顶部 `CONFIG`；核心可摘走：`CONFIG` + `apply()`（由 p 写四个状态）+ 那条 timeline。
- 与 layout.md 的接口：标签距边 48@960（=96@1080 安全边）、20px（=40 body 档）；分割线是全高元素，不算贴边。
- 剪辑软件对应物：剪映 / CapCut "蒙版 → 线性"打关键帧（蒙版位置 = p，羽化 0），分割线是另一层 3px 白色矩形跟同一组关键帧；AE 是上层 `Linear Wipe` 的 Transition Completion 打关键帧 + 一根 Shape 线的 Position 用表达式跟它；Premiere 是 `Crop → Right` 关键帧。素材站里叫 "before / after slider / comparison wipe"。

## 动效范围
- 属于本卡的：上层 `clip-path inset` 裁切（不移动图）+ 分割线与裁切边同源于一个进度值的结构；四段动作的时间表（0.6 起手 / 1.4 揭示到中线 / 1.5 停 / 0.45 nudge 到 42 再回 / 1.0 到近端 8 / 1.5 停 / 1.0 回中 / 1.0 停）与缓动（揭示 / 近端 `power3.inOut`，nudge `power2.inOut`）；标签"该侧露出 ≥40% 才亮"的规则；两图共用一条时长 = 镜头的 1→1.04 极慢推；退场错峰 0.04 与两图同收。
- 不属于本卡的：demo 的示意图与两套滤镜（演示"调色"用）、"调色前 / 调色后"文案、分割线的白色与圆钮造型（可换色但要保留"可滑动分界"的暗示）、白底舞台。
- 迁移接口：`srcBefore` / `srcAfter` 换素材（两张必须同尺寸同构图）；`hold` / `tailHold` 对齐口播；`nudge` / `farLeft` 按"要强调哪一侧"调（想强调"前"就把 nudge 改到 58、近端改到 92）；换画幅时几何按比例（分割线百分比制、标签距边等比缩放）。
- 底色要求：白底即可——两图满铺时舞台底色不可见；退场后露出白底。

## 落位自检（2026-09-05 用户定版，选卡时抄进 SHOTBOOK 该镜自检列）
- **同构图**：两张素材同尺寸、同裁切、同缩放，定妆帧把 p 冻在 50 看分割线两侧的地平线 / 边缘是否连续（错位 >8px 返工，换素材不是调位置）。
- **同源驱动**：裁切边 x 与分割线 x 任意时刻相等（抽 t=1.3 / 3.7 / 5.5 三帧核，差 >2px 返工）。
- **四个动作、不多**：揭示 → nudge → 近端 → 回中；SHOTBOOK 里不许再加一轮。
- **标签**：距顶 / 距侧边 ≥48@960，字号 ≥20@960；p=50 时两枚都亮，p=8 时只亮右枚。
- **停留有声段落**：`hold` / `tailHold` 对齐口播句长，退场与本镜结束对齐（不留空尾）。

<!-- ===== /file: video-talkcraft/references/cards/split-compare-slider.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/split-text-stagger.md ===== -->

---
name: split-text-stagger
标题: 逐字裂升
一句话: 标题"把复杂的事，讲简单"9 个字各在自己的裁切盒（高 = 行高 78）里从下方 115% 升起、back.out(1.2) 带约 5% 过冲回落（极值 ≈1.053），字间错峰 2 帧（0.067s）、每字行程 0.5s；同时一条 3px 基线从左向右 scaleX 长到整行宽，生长时长 = 字的总错峰时长，长满与末字落定同帧——字像从一条线里长出来；1.4s 副标淡入，4.4s 整组同收
适用: 章节题 / 金句的利落入场、片名 / 频道名字卡、要点句逐条上台（每条一次）、与下划线类卡衔接（基线即下划线）；是 per-character-rise 的"裁切 + 基线"变体——要版式感（字被线裁着长出来）选它，要"一股气顶上来"的纯气势选 per-character-rise
时长: 4.8s（0.3 起逐字裂升，末字 0.84–1.34 落定，基线同步 0.3–1.34 长满 → 1.4 副标 → 4.4 同收 0.4s）；成片把第一个字的起升对到口播念标题首字的字锚
能量: 中
类别: 字幕花字
输入: 文
语义: 金句, 标题
素材形态: 无
位置: 任意
props: text, sub
优先级: P2
代码: template/cards/split-text-stagger.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 纯文字卡；人在场时整组放人物对侧半幅（layout §4） | ✗ | ✗ |

作用于标题层，不作用于底部跟读字幕（素排铁律）。

## 常用场景
1. 章节题 / 金句的利落入场："把复杂的事，讲简单"（demo 演的）
2. 片名 / 频道名字卡（基线当品牌线）
3. 要点句逐条上台：每条一次裂升，基线随条目宽度变
4. 与 `ink-underline` 衔接：裂升留下的基线就是后面划重点的线

## 意图
库里的逐字入场是 `per-character-rise`——每字从自己位置下方 44% 升到位、位移与淡入两条缓动、错峰仅 1 帧，读作"一股气顶上来"，零裁切零线条。本卡是它的**版式化变体**：每字在裁切盒里升起，字的下半截被基线"裁着"露出来，同时那条基线自己也在长——多了"字从线里长出来"的版式感，适合章节题 / 字卡这种要一点仪式的地方。做对四条：
1. **过冲要看得见**（back.out 1.2，极值 ≈1.053 即约 5%）：系数 <1.0 时过冲 <4%、可测不可感，正常速度要看得见回落那一下。
2. **裁切盒高 = 行高**：字从基线下方"被裁着"升出来——这一裁就是与 `per-character-rise` 的全部区别，盒子留了余量就成了普通位移。
3. **基线生长时长 = 字的总错峰时长**：长满与末字落定同帧；线先画完字再走、或字落完线还在长，都读作两个动画。
4. **全员落定真静止 ≥30f**：落定即静置，无 idle。

## 动效核心
- **几何**（960×540）：整行 64px / 700 / 字距 −1 墨色 `#1d1d1f`，`.sts-line` 居中（left 50% + translateX −50%）`top 240`，字间 gap 2；每字 `.sts-ch` 高 78 / 行高 78 / `overflow hidden`，内层 span 做 `translateY(%)`。基线 `.sts-base` 3px 墨色，`top 322`，宽 = 整行宽（量一次），`left 50%` + `translateX(−W/2)`，`transform-origin 0 50%`。副标 20px `#7a7a7a` 居中 `top 344`。
- **裂升**：第 i 字在 `0.3 + i×0.067` 起 0.5s `back.out(1.2)`：`translateY 115% → 0`（超出盒子的部分被裁）。9 字末字 0.84 起、1.34 落定。
- **基线**：0.3s 起 `scaleX 0→1`，时长 `0.5 + 0.067×8 = 1.036s`，`power2.out`。
- **副标**：1.4s 起 0.4s 淡入。
- **退场**：4.4s 整行 + 基线 + 副标 opacity→0 0.4s `power2.in`，4.8s 结束。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `over` | back.out(1.2) ≈ 5% 过冲（极值 1.053） | <1.0 过冲 <4%、可测不可感；1.7 ≈ 10%，>1.7 字弹得像卡通 |
| `stagger` | 0.067s（2 帧） | 0 整行一起升读作整句淡入；>0.12 读作逐字打字 |
| `dur` | 0.5s | <0.3 看不见过冲回落；>0.7 拖 |
| 裁切盒高 | = 行高 78 | 盒子比行高高就露出升起过程，裁切感消失 |
| 基线粗细 | 3px | 2px 在 960 舞台上读作发丝线，>4px 读作色条 |
| `subAt` | 1.4s（末字落定 +0.06） | 副标先于末字落定出现会抢戏 |
| 字数 | ≤14 字一行 | 超了拆行不缩字（layout §5），第二行另起一组 |

## 已知坑
- back.out 系数 <1.0（过冲 <4%）——可测不可感，跟无过冲一样。
- 裁切盒留余量——字整段可见地滑上来，成了普通位移，与 per-character-rise 无异。
- 基线与字的时长不同步——线先画完或字落完线还在长，读作两个动画。
- 字距用正值——大字号加正字距读作横幅；本卡 −1。
- 落定后还在动（基线呼吸、字微浮）——违反运动减法。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/split-text-stagger.tsx——`text / sub` 两个 prop；durationInFrames 156；整行宽用 `useLayoutEffect + delayRender` 量一次给基线。
- HTML/GSAP：demos/split-text-stagger/index.html——改 `TEXT / SUB` 与 `CONFIG`；基线宽由脚本量 `line.offsetWidth`。
- 母本：video-shotcraft `type-assembly-moves` A 式 split-text-stagger（B 漂移合拢带合体呼吸、C 字距呼吸、D 沿线流入均未搬）。
- 与 `per-character-rise` 的分工：那张是"一股气顶上来"（错峰 1 帧、无裁切、零过冲），用于金句 / 情绪句；本卡是"字从线里长出来"（错峰 2 帧、裁切、5% 过冲、基线），用于章节题 / 字卡。同一片两张都用时按"情绪 vs 结构"分配，不要同一幕混用。
- 剪辑软件对应物：剪映"文字 → 入场 → 逐字上升"无裁切，需给文字加蒙版；AE 用 Text Animator（Position Y + Range Selector）+ 文字图层 Alpha 遮罩，基线用形状图层 Trim Paths。
- 与 layout.md 的接口：整行包围盒居中（§4，偏差 ≤48），中心 y ≈ 279；64px 在 title 档（§5）；基线到副标 22px、标题到基线 4px 属同组内距（§2）。

## 动效范围
- 属于本卡的：裁切盒内逐字裂升（115%→0、back.out 1.2、错峰 2 帧）；基线与字总时长同步生长；副标滞后跟进。
- 不属于本卡的：具体文案、字号（按本片字阶）、白底舞台、基线颜色（按本片 ink）。
- 迁移接口：`text / sub`；1080p 输出字号 ×2（128）、盒高 156、基线 6px；起升时刻按口播念标题首字的字锚摆。
- 底色要求：白底 / 羊皮纸底成立；深底时字与基线反白。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- 定妆帧两张：裂升中（如 0.7s）前几个字已过冲回落、后几个字只露上半截、基线长到约 60%；落定后（如 2.0s）整行、基线、副标全部静止。
- 整行包围盒水平居中偏差 ≤48，中心 y ≈ 279；基线左右端与整行首末字边缘对齐（偏差 ≤4px）。
- 基线长满帧 = 末字落定帧（1.34s），前后不差 2 帧以上。
- 人物在场时整组放人物对侧半幅中心（x = 240 或 720@960）。

<!-- ===== /file: video-talkcraft/references/cards/split-text-stagger.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/stack-fan-out.md ===== -->

---
name: stack-fan-out
标题: 卡堆扇形展开
一句话: 五张 220×150 卡叠成一叠（微错位）→ 0.7s 绕卡堆下方 R=520 的弧心扇开成 −24°…+24° → 停 0.8s → 0.6s 铺平成一行等距五格（150 宽、间距 16、整行居中、旋转归零）→ 一起退场——"这一叠"变成"这五个"
适用: "我收集了这几张 / 今年拍了五张候选 / 本期要讲这几件事"——汇总 → 展开的任何清单（≤6 张）；图片专用（截图 / 照片 / 评论卡），人物不在此镜
时长: 6.4s（0.2 卡堆现身 → 1.0 扇开 0.7 → 停 0.8 → 2.5 铺平 0.6 → 停 2.7 → 5.8 退场 0.4）；铺平后的停留随口播伸缩
能量: 中
类别: 素材呈现
输入: 图
语义: 例证, 列举
素材形态: 横屏, 多图
位置: 任意
props: title, srcs
优先级: P1
代码: template/cards/stack-fan-out.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 人物不在此镜 | ✗ 卡在叠着和扇开时看不全，视频放进去没意义 | **专用**（截图 / 照片 / 评论卡 / 封面） |

五张同比例（220×150 ≈ 3:2）；横竖混合统一裁到同一外框。铺平后每张只有 150 宽，图内文字读不出——靠图的"样子"被认出即可，要读内容用 grid-to-hero 或 media-pop-in。

## 常用场景
1. 五个候选先"一叠"再"五个"：今年拍的五张候选封面（demo 所演）
2. "我收集了这几条评论 / 截图"→ 铺平后逐条讲
3. 汇总 → 展开的任何清单（≤6：五个理由、五款工具的图标卡）
4. 片头预告本期要讲的几件事（铺平那一行就是目录）

## 意图
"一叠东西"是实体世界的汇总隐喻——手里攥着一沓照片，摊开给你看。卡堆扇开做对了，观众先感到"有一堆"，再看清"有几个"，最后一行等距是"接下来一个一个说"。命门三条：
1. **扇开是绕弧心的旋转 + 平移**（弧心在卡堆下方 R），不是各卡原地转——手持一叠卡摊开时，每张的位置和角度是一起由手腕决定的。
2. **扇开 / 铺平两段动作之间必须停 ≥0.6s**：一段动作一个意思，"一叠" → "五个"要让观众在扇形态看一眼再变；连着动读作一次乱飞。
3. **铺平后每张旋转归零、等宽等距、整行居中**：铺平就是"排整齐"，剩一点歪就是没排好。

## 动效核心
- `0.2s` 标题升起（`y 10→0`，power3.out 0.45s）+ 卡堆淡入（0.4s，错峰 0.05）：五张同位 220×150 @ (370, 170)（中心 480, 245），微错位 `x (i−2)×3 / y (i−2)×−2 / rotate (i−2)×1.2°`，最后一张在最上。
- `1.0s` 扇开（power3.out 0.7s）：第 i 张目标角 `deg = −24 + 12i`，位置 = 以卡堆中心下方 R=520 为圆心的弧上点 `x = sin(a)·R, y = (1−cos a)·R`，旋转 = deg。两端卡中心到 (268, 290) / (692, 290)，最左边缘 ≈137 ≥48。
- `2.5s` 铺平（power3.inOut 0.6s）：`x = (i−2)×166, y = 0, rotate 0, scale 150/220`——五张 150 宽、间距 16，整行 814 居中（离边 73），仍以 y=245 为中线。
- `5.8s` 一起退场（0.4s power2.in，五张卡 → 标题，错峰 0.04）→ `6.4s` 结束。扇形态与铺平态之间、铺平后都是静置，无 idle。
- transform 顺序与 GSAP 一致：`translate(x, y) rotate(r) scale(s)`，origin 50% 50%；三态（叠 → 扇 → 行）两段不重叠，顺序 lerp。
- 标题 28px 700 居中 top 60 是演示语境（title 档）；卡 + 标题整组包围盒落在上三分线附近（y 60~296）。白边卡 padding 8 / 圆角 12 / 唯一投影。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `fanAngle` 扇角 | ±24° | 五张 12° 一档；>30° 两端卡开始出边、<15° 像没摊开 |
| `R` 弧心距 | 520 | 越大越像"平着摊"，越小越像"绕一点转"；R < 400 两端卡下沉过多压字幕带 |
| `fanDur` 扇开 | 0.7s | power3.out：起手快收尾稳；<0.5 甩、>1.0 拖 |
| 扇 → 铺平停留 | 0.8s | 必须 ≥0.6，让"一叠"被看见 |
| `flatDur` 铺平 | 0.6s | power3.inOut（两头都缓，"排整齐"的手感）；扇开用 out、铺平用 inOut 不要混 |
| `flatW` / `flatGap` | 150 / 16 | 五张 814 居中；六张改 130 / 14（≈850）仍 ≥48 边距 |
| `n` 卡数 | 5 | ≤6；>6 铺平后每张 <120 宽，认不出 |
| `exitAt` | 5.8s | = 讲完这几张；铺平后停留随口播伸缩 |

## 已知坑
- 各卡原地旋转（没有弧线位移）——像五张卡各自抖，不是一叠被摊开。
- 扇开接着就铺平（中间 <0.5s）——两段动作糊成一次乱飞，"一叠"没被看见。
- 铺平后还带一两度歪——"没排好"；铺平 = 旋转归零。
- 铺平后不等距 / 整行不居中——包围盒偏差 >48 即 P1（layout.md §4）。
- 叠放态五张完全重合（无微错位）——读作"一张卡"，扇开时突然变五张像变魔术；错位 3px / 1.2° 就够。
- 放视频——叠着和扇开时看不全，且五路视频同播浪费；本卡图片专用。
- 卡数 >6——扇角每档 <10° 分不开，铺平后每张 <120 宽。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/stack-fan-out.tsx——`srcs` 五张真图（数组顺序 = 叠放顺序，最后一张在最上）、`title` 标题（传 `""` 去掉）；导出的 `END` 是动画结束秒；铺平后停留要随台词伸缩改 `CONFIG.exitAt`。
- HTML/GSAP：demos/stack-fan-out/index.html——`CONFIG` 顶置（卡数 / 扇角 / 弧心 / 铺平宽距一处改）；`.pic` 整块换成 `<img>` 即真图。
- 与 layout.md 的接口：无人物 → 整行包围盒居中（§4）；两端卡在扇形态离边 ≥48（§2）；标题 title 档（§5）。
- 剪辑软件对应物：剪映五层画中画各打位置 + 旋转关键帧（同区间）；AE 五层 parent 到一个空对象、按弧心分配 Rotation 与 Position 表达式；CapCut 同理。

## 动效范围
- 属于本卡的：叠（微错位）→ 扇（绕弧心旋转 + 平移，power3.out 0.7）→ 停 ≥0.6 → 行（等宽等距居中、旋转归零，power3.inOut 0.6）→ 一起退场的时间表；扇角 ±24° / 弧心 R=520 / 铺平 150 宽 16 间距的几何比例；transform 顺序 translate → rotate → scale。
- 不属于本卡的：示意图（演示语境素材，demos/_lib/media，不属于本卡）、标题文案与字号、白底舞台。
- 迁移接口：`srcs` 换图；`title` 换或去掉；`n` 改卡数（≤6，`flatW / flatGap` 同步缩）；`CONFIG.exitAt` 按口播伸缩；换画幅按 960×540 等比缩放，竖屏把 R 加大到 700、扇角收到 ±18° 防出边。
- 底色要求：白底即可（白边卡 + 投影分层）。

## 落位自检（2026-09-05 用户定版，选卡时抄进 SHOTBOOK 该镜自检列）
- **扇形态几何**：两端卡中心 (268, 290) / (692, 290)、旋转 ∓24°，最左 / 最右边缘 ≥48 离画幅边；定妆帧取 1.7s。
- **停留**：扇开结束（1.7）到铺平开始（2.5）≥0.6s，期间五张静置。
- **铺平态几何**：五张 150 宽、间距 16、旋转 0、整行 814 包围盒中心 = 480（偏差 >48 返工）、中线 y=245；定妆帧取 3.1s。
- **叠放态**：微错位可见（相邻卡边缘 ≥2px 露出），最后一张在最上。
- **标题**：28@960 title 档、与卡堆 / 扇形不相交（标题底 ≤95、卡顶 ≥137 in 扇形态）。
- **一起退场**：5.8 起五张卡 → 标题错峰 0.04，6.4 全部消失，之后无任何元素残留。

<!-- ===== /file: video-talkcraft/references/cards/stack-fan-out.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/stage-keyframe-tour.md ===== -->

---
name: stage-keyframe-tour
标题: 长页兴趣点巡游
优先级: P1
代码: template/cards/stage-keyframe-tour.tsx
一句话: 一张超出画幅的长落地页躺在 3D 透视舞台上（perspective 900 + rotateX 14° + rotateY −20° + scale 0.86 + 接触阴影），相机沿一条多关键帧路径依次停靠 3 个兴趣点（每点 hold 0.8~1s）再拉开离场；每段都把目标兴趣点设为 transform-origin 并平移到画面正中，所以 zoom 与 roll 绕的是"当前在讲的那一块"而不是长页的几何中心
适用: 讲一张超出画幅的长东西——长落地页、长截图、长对话记录、长报表——且要"讲到哪儿镜头停到哪儿"的段落；产品巡览（Hero → 数据 → 价格）、"我们改了这三处"、把一张长图当一条时间线走完
时长: 实拍：落点 hold 0.6~1s → 每个兴趣点 1~1.3s 转场 + 0.8~1.2s hold → 离场拉开 1.2~1.6s；3 个兴趣点合计 8~11s。demo：0.8s 入场沉降 + 落点 hold 0.9s + 三段巡游 + 离场 1.4s，全程 8.75s
能量: 中
类别: 运镜
输入: 图, 截图
语义: 例证, 强调, 空间叙事
素材形态: 长图
位置: 任意
props: hostSrc
---

## 意图
长页有两种讲法：**页面动**（页面自己往上滚，相机不动 —— 那是 [evidence-scroll-tour](evidence-scroll-tour.md)）和**相机动**（页面躺着不动，相机在它上面飞）。
后者才是"巡游"：观众看到的不是一份在滚动的文档，而是**一个躺在台上的实物，被人拿着镜头挨个指点**。
差别在观感的主语——前者是"网页在演示自己"，后者是"我在带你看"。带着讲的段落必须用后者。

做对的命门只有一条，且移植时最容易漏：**每一段的 zoom 必须绕当前兴趣点发生**。
做法是把目标点算成像素、设为 `transform-origin`，再把该点平移到画面正中。
如果偷懒用固定原点（center）+ 位移去凑，缩放会绕 2200px 长页的几何中心放大，
镜头就会在 zoom 变化时**同时甩出一段没人要的横向漂移**——观感是"镜头在找东西"，
而不是"镜头已经知道要看哪儿"。这一条是本卡与"把长图放大再平移"的全部区别。

第二条纪律是**hold 必须真的静止**。巡游的信息量在 hold 里，不在移动里；
移动段只是"我们去下一处"的连接。段与段之间不留 hold，观众读不完任何一处。

## 动效核心
- 结构三层：`.world`（`perspective: 900px` + `perspective-origin: 50% 42%`，装在**父容器**上）→ `.camera`（相机层，`preserve-3d`，全卡唯一被 transform 的元素）→ `.page`（长页本体，高度远超画幅）
- 舞台基础姿态：`rotateX(14°)` + `rotateY(−20°)` + `scale(0.86)`。**俯角是必须的**——长页只有带俯角才读作"躺在台上"，纯 `rotateY` 读作"立着的墙"（那是 [tilt-3d-page](tilt-3d-page.md) 的语义）
- 长页几何：宽 = 画面宽 × 84%，高按内容自然展开（demo 是 806×2200）。`top = (H − planeH)/2` 是负值，长页上下都出画——**"超出画幅"是本卡的前提，不是副作用**
- 圆角 = 画面宽的 1.4%（960 画幅 → 13px），随画幅等比缩放
- 地面两层（都属于舞台，相机飞它们不动）：**接触阴影** = 68%×11% 的扁椭圆 + `blur(38px)`，是"贴地"唯一的证据；**地面反光** = `clip-path: polygon(7% 0, 93% 0, 78% 100%, 22% 100%)`（上宽下窄＝地面往远处收）+ `rotateX(58deg)` + `blur(26px)`
- **兴趣点寻址（核心手法）**：兴趣点用归一化坐标 `(px, py)` 给（0~1，相对长页宽高），每帧算成像素 `ox = px·planeW` / `oy = py·planeH`，然后
  `transform-origin: ox oy` + `x = W/2 − (left + ox)` + `y = H/2 − (top + oy)`。
  这样 `scale` 与 `rotation` 都绕这个点发生，位移把它搬到画面正中
- 关键帧路径：每个关键帧给 `{d, px, py, zoom, roll}`（d = 该段时长）。**相邻两帧姿态相同即为 hold**——不需要单独的 hold 机制，重复姿态就是停下来
- 段间缓动固定 `cubic-bezier(0.16, 1, 0.3, 1)`（Apple 那条）：起步快、末段长距离减速 ⇒ 读作"相机已经知道目标在哪、过去了、稳稳停住"。GSAP core 不带 CustomEase，demo 里用 22 次二分自解一条曲线（比拿 `expo.out` 近似更准）
- `roll`（机身倾角，±0.5~1°）：只给中段的兴趣点加，且**每段方向不同**。它的作用是让"停靠"看起来是手持找角度而不是机械滑轨对位
- 入场沉降 0.8s（`power2.out` ≈ spring damping 26 / stiffness 90）：`scale×0.94` / `rotateX +8°` / `rotateY −5°` / `y +64px` → 到位；地面两层同步淡入且位移按 0.28 / 0.35 的比例跟一点（近处的影子比远处的反光挪得多）
- 手持抖动：`CONFIG.shake` 在 tsx 与 demo 里都只是声明为 0 的占位（渲染未引用），本卡**没有**抖动实现；本库也不做定格抖动，需要时另起实现
- 离场：`zoom` 拉到 0.6 给全貌。**长页巡游必须以全貌收尾**——观众刚看了三处细节，需要一眼知道它们在整体里的位置

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `perspective`（父容器） | 900px（范围 800~1100） | 空间强度。长页纵深跨度大，比单屏页（[tilt-3d-page](tilt-3d-page.md) 用 1000）稍近一档才读得出"躺着"；<600px 读作鱼眼变形 |
| `rotX` | 14°（范围 10~18°） | 俯角。0 = 长页读作"立着的墙"，本卡语义崩塌；>22° 页面纵向压缩过头，正文行距看起来在打架 |
| `rotY` | −20°（范围 14~24°） | 侧仰。>30° 远端正文不可读（要读的页面绝对不能超） |
| `scale` | 0.86 | 基础缩放，与每段 `zoom` 相乘。基础值定"整体退多远"，`zoom` 定"这一处怼多近" |
| `zoom`（兴趣点） | 1.3~1.5（全貌 0.6~0.7） | 每处的焦距。>1.8 时长页侧边会退进画幅露出舞台地面（除非 `px` 严格取 0.5）；<1.2 读不出"停下来看这一处" |
| `px` / `py` | 0.5 / 0.11~0.85 | 兴趣点归一化坐标。**`px` 越偏离 0.5、`zoom` 越大，越容易露出长页侧边之外的舞台**；整幅宽的版块一律取 0.5，只有"给全貌"的姿态才故意露地面 |
| 段时长 | 1.05~1.3s | 移动段。<0.8s 读作"甩过去"（那是转场的语气）；>1.8s 观众等着它到位 |
| hold 时长 | 0.85~0.9s（实拍 0.8~1.2s） | 停靠。**这是信息真正被读到的地方**；<0.6s 白跑一趟；实拍按"讲这一处需要多少字"给 |
| `roll` | ±0.5~1° | 机身倾角。0 = 机械滑轨；>2° 观众会以为画面歪了（不是"手持"是"没端平"） |
| 段间缓动 | `cubic-bezier(0.16,1,0.3,1)` | 固定值，不建议换。`power2.out` 尾巴太短、读作"停得急"；`sine.inOut` 起步太软、读作"漂过去"而非"过去" |
| `entry` | 0.80s | 入场沉降。这一段结束前不要开始巡游（demo 用 0.9s 的落点 hold 盖住它） |
| `shake` | 0（占位） | tsx / demo 均未接线，改了没有效果 |

## 已知坑
- **`willChange: transform` 加在相机层上**——相机层持续分数缩放时，强制合成层会让长页那圈 1px 边框在锐利与模糊之间脉动（比不提层更难看）。正确做法：`will-change` 只加在**文字容器**上（demo 里是 `.sec`），让每段缩放内的字形栅格稳定；相机层不加，也不要逐字加。
- 用固定 `transform-origin`（center）+ 位移去凑兴趣点——zoom 变化时会甩出一段横向漂移，读作"镜头在找东西"。本卡的全部关键就是每帧把目标点设成原点。
- `zoom` 给大 + `px` 偏离 0.5——长页的侧边退进画幅，露出舞台地面，观众看到的是"一张纸的边"。整幅宽的版块 `px` 一律取 0.5；真要看左右侧的局部，得同时把 `zoom` 压回 1.2 以内。
- 段与段之间不留 hold（路径表里没有重复姿态）——变成一条从头滑到尾的连续运镜，那是 [long-take-world](long-take-world.md) 或 [slow-pull-reveal](slow-pull-reveal.md)，不是巡游。**巡游的信息量在 hold 里。**
- 地面反光照搬原版参数——remocn 是深底舞台 + 亮紫反光，白底上直接照搬会读成"页面两侧有两片脏灰楔形"。白底必须把浓度压到 0.05 以下、宽度收窄、模糊加大。
- 不以全貌收尾——观众看完三处细节不知道它们在整体的什么位置，巡游读作三个不相干的特写。
- 兴趣点排序违反页面的物理顺序（比如 py 0.11 → 0.85 → 0.5）——镜头来回折返，观众会以为漏看了什么。**兴趣点必须单调**（自上而下或自下而上走一趟）。
- 忘了 `preserve-3d`，或把 `perspective` 写在被 transform 的元素自己身上——空间会散（与 [tilt-3d-page](tilt-3d-page.md) 同坑，细节见那张卡）。
- 长页没有真的超出画幅（内容只有一屏半）——那就不需要巡游，`tilt-3d-page` 加一次缓推已经够了。本卡的成本只在长页上才划算。
- 兴趣点超过 4 个——观众记不住，巡游读作流水账；多了就拆成两镜。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/stage-keyframe-tour.tsx——props：仅 `hostSrc`（声明未使用）；长页内容在 JSX、`planeH`（2200）是函数内局部常量、兴趣点在 `CONFIG.moves`，换素材需改源码。自包含单文件，复制进工程即可用；舞台姿态与路径在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：`demos/stage-keyframe-tour/index.html`。换素材改 `.page` 内整块 DOM（或直接换成一张铺满的长截图 `<img>`），改 JS 里的 `planeH` 为素材真实高度；路径与节奏全在顶部 `CONFIG.moves`（每行一个关键帧 `{d, px, py, zoom, roll}`，相邻同姿态即 hold）；舞台姿态在 `CONFIG.rotX/rotY/scale`。核心可摘走：`CONFIG` + `bez()` + `DemoShell.register` 回调体里的 `apply()`，加上三层结构那几行 CSS。
- 换素材的最小流程：① 量出长截图的原始宽高，`planeH = 806 × (原高 / 原宽)`；② 兴趣点的 `py` 直接用"该版块中心在长图里的像素 y ÷ 原高"；③ `px` 取 0.5；④ 每段 `d` 按口播稿这句话的时长给，hold 段按"读完这一处要几秒"给。
- Remotion：已落地为 template/cards/stage-keyframe-tour.tsx——`CONFIG.moves` 每行 `{d, px, py, zoom, roll}`（d 为段时长，相邻同姿态即 hold），段间 `bez(0.16, 1, 0.3, 1)`，每帧把 `(px·planeW, py·planeH)` 设为 transform-origin 再平移到画面正中（L229-252）；入场沉降 `settle` 走 power2.out（L206, L223-228）。
- 竖向长距离巡游（一段就跨几千像素）：换用 remocn 的 smooth-descent 三段方案——起 30 帧 `in(cubic)` 加速、中段 `linear`、末 30 帧 `out(cubic)` 减速。它成立的算术是：30 帧三次方斜坡的位移正好等于匀速段同时长位移的 1/3，两端速度才接得上、无跳速。用单条 EXPO 走 2000px 会在中段快到糊。
- 剪辑软件对应物：AE——长图放进 3D 图层，加一台摄像机（Camera），给摄像机的 `Position` / `Zoom` 打关键帧，**每个兴趣点打两个相同的关键帧构成 hold**，关键帧插值用 `Easy Ease` 后进图表编辑器把手柄拉成"起步快末段长减速"；兴趣点绕点缩放靠调整图层的锚点（Anchor Point）或直接移动摄像机而非缩放图层。剪映——多段"位置+缩放"关键帧，缓动只有固定几档，hold 靠两个同值关键帧；透视舞台需要预先把长图做成带倾斜的图片（剪映的 3D 能力不足以实时给）。Premiere——`Motion` 的 Position/Scale 关键帧 + `Basic 3D`，同样用同值关键帧做 hold。**这就是各家素材站说的 "long page scroll showcase / website presentation" 品类**，但模板通常是"页面滚动"而非"相机巡游"，兴趣点寻址得自己搭。
- 音效：每段起步一记轻 `whoosh`（`vol` 0.20~0.24，`dur` 0.55~0.75，离场那记 `rate` 压到 0.86 = 更沉更长），入场配一记 `lowpad`。**hold 段绝对不给声**——静止是它的全部作用。

## 动效范围
- 属于本卡的：**多关键帧兴趣点巡游**这一整套——归一化兴趣点寻址（目标点设为 `transform-origin` 并平移到画面正中，使 zoom/roll 绕当前兴趣点发生）、"相邻同姿态即 hold"的路径表写法、段间固定 `cubic-bezier(0.16,1,0.3,1)`、每段不同方向的 ±0.5~1° `roll`、0.8s 沉降入场（`scale×0.94` / `rotateX+8°` / `rotateY−5°` / `y+64`）、以全貌收尾的纪律、兴趣点必须单调的排序纪律、"hold 才是信息载体、移动段只是连接"的时长分配、`will-change` 只提文字容器不提相机层这条踩坑纪律，以及超出画幅的长页 + 透视舞台（俯角 `rotateX` 是长页读作"躺着"的前提）+ 接触阴影 / 地面反光两层地面。
- 不属于本卡的：demo 里那张灰阶线框长落地页的全部内容（导航 / Hero / logo 墙 / 三栏特性 / 三个大数字 / 宽图表 / 三张价格卡 / 页脚及其文案排版）、兴趣点选"主张 → 数据 → 价格"这一具体编排、三个兴趣点这个具体数量（3~4 都成立，5 个以上观众记不住）、舞台姿态取 14°/−20° 这组具体值、地面两层的具体浓度与模糊半径（随底色调）、长页上叠加的任何字幕或高亮标注。
- 迁移接口：`perspective` 定空间强度，换画幅时按画幅宽等比缩放（本卡按 960 宽 / 806px 页宽设计）；`planeH` 按素材真实宽高比反算；兴趣点 `py` = 版块中心在原图的像素 y ÷ 原图高，`px` 整幅宽版块取 0.5；每段 `zoom` 按"这一处的最小字号在画面里够不够读"验收（不是按构图好不好看）；段时长与 hold 时长按口播稿逐句给（移动段 = 过渡词，hold = 讲这一处的那句话）；`rotX`/`rotY` 按"远端最小字号是否可读"验收；地面两层的浓度按底色反向调整（白底压淡、深底改亮边）。
- 底色要求：白底成立（demo 已验证），但地面两层必须按白底重调（浓度压到 0.05 档、模糊加大）。深底舞台是原版语境，那时反光可以用亮色渐变、接触阴影加深，观感更"影棚"。
- 与本库其他运镜卡的边界：[slow-push-in](slow-push-in.md) / [slow-pull-reveal](slow-pull-reveal.md) 是平面单段推拉；[tilt-3d-page](tilt-3d-page.md) 是"页面立起来成 3D 立面"（单屏、无兴趣点）；[sway-parallax](sway-parallax.md) 横摇、[orbit-drift](orbit-drift.md) 环绕微漂，都是**单段运动 + hold**；[long-take-world](long-take-world.md) 是世界坐标 2D 相机（无透视平面、无兴趣点寻址）；[evidence-scroll-tour](evidence-scroll-tour.md) 是页面自己上滚、相机不动。**本卡的差异化只有三样**：多关键帧路径、超出画幅的长页、归一化兴趣点寻址。若素材只有一屏、或只需要一次推近，用上面那几张，别付这张的成本。

<!-- ===== /file: video-talkcraft/references/cards/stage-keyframe-tour.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/step-timeline-vertical.md ===== -->

---
name: step-timeline-vertical
标题: 竖向步骤线
优先级: P1
代码: template/cards/step-timeline-vertical.tsx
一句话: 一条竖线从上往下 0.6s 画下去，线推到哪个位置那个圆节点就弹出来、2 帧后右侧两行字跟着左移淡入（三个节点每 0.18s 一个，是解线的缓动反函数算出来的）——三组全部到位后第一个节点升级成强调色空心环并放大 1.25 倍，标出"你现在在这一步"
适用: 讲有先后依赖的流程——"三步走"、"我是这样一步步做的"、复盘时间线；需要观众理解"顺序不能颠倒"的时刻；也能当"当前进度"用（空心环指向进行中的那一步）。不适合并列的清单（那用 numbered-step-stack）
时长: 起手静置 0.4s → 线画出 0.6s（三个节点在 0.52 / 0.70 / 0.88s 依次被线点亮，间隔 0.18s）→ 空心环升级 0.32s → 收尾 hold 2.0s；共约 3.5s
能量: 中
类别: 数据信息图
输入: 人(可选), 文
语义: 步骤
素材形态: 透明通道
位置: 任意
props: hostSrc
---

## 意图
"三步"有两种完全不同的说法。一种是**清单**：三件事都要做，先做哪件都行；另一种是**时间轴**：
第二步依赖第一步的结果，顺序错了就不成立。这两种在静帧上长得几乎一样（都是三行带编号的字），
观众只能靠**动效**来区分——而这张卡就是"时间轴"那一种。

区分的手段只有一个：**一条线在推进，节点是被线点亮的**。观众看到线走到第二个位置、
第二个点才亮，脑子里自动装上"第一步完成之后才有第二步"这个因果。反过来——线画完再统一弹三个点——
读作"这里有一条线和三个点"，因果关系一秒消失，那就退回清单了。

命门两条：① **节点必须跟着线的推进出现**，"线到哪、亮哪"是本卡全部的语义所在；
② **空心环是第三拍，在三组全部到位之后**。它答的是另一个问题——不是"有几步"而是"你在第几步"，
两个问题分开问才都听得清。

顺带一条纪律：右侧的 kicker（"第一步/第二步"）是 dim 实色 `#8a8a8a`，静置态不叠透明度
（design-language §1 红线）——它是层级更低的标签，不是"没读到的字"。

## 动效核心
- **层级**：白底 → 竖线（最底，`#d2d2d7` hairline 档）→ 三个圆节点 → 右侧三组文字 → 人物层（右列）
- **① 竖线**：`scaleY 0 → 1`，`transform-origin: 50% 0%`（origin top），`0.6s power1.inOut`。
  `inOut` 是刻意的——两头缓、中段近匀速，读作"时间在走"而不是"一根线被甩下来"。
  **但 inOut 的强度直接决定节点的间隔**（中段越快，三个点越挤）：`power2.inOut @0.4s` 实测
  三个节点只差 0.18s **总共**（读作同时亮，本卡语义作废）；`power1.inOut @0.6s` 得到
  **每 0.178s 一个**（0.52 / 0.70 / 0.88s），才读得出"线到哪、亮哪"。
  要更强的 inOut 就必须同步加长 `lineDur` —— 两者是一对，不能单独调
- **② 节点与文字跟着线走（本卡的实现关键）**：节点 i 的触发时刻不是拍脑袋的 delay，而是
  **解线的缓动函数反函数**求出来的：
  - 节点在线上的位置比例 `frac = nodeY / lineHeight`
  - 用二分法（40 次迭代）在 `ease` 上解 `ease(t) = frac`，得到线走到该位置的归一化时间 `t`
  - 触发时刻 = `lead + lineDur × t`
  换句话说**换节点位置、换线长、换缓动都不用重算 delay**，"线到哪、亮哪"永远成立
- **节点弹出**：`scale 0 → 1`，`0.18s back.out(1.6)`——极轻回弹，它是"打上一个点"
- **右侧文字**：`opacity 0 → 1` + `x −8 → 0`，`0.26s power3.out`，**滞后节点 2 帧（0.067s @30fps）**。
  点先亮、字后跟：观众的视线落在点上，字是被点带出来的
- **③ 空心环升级（三组全部到位 + 0.10s 呼吸后）**，三条属性同帧同 `0.22s power3.out`：
  - `border-width 0 → 3px`（描边色 = 强调色 `#e0452c`）
  - `background: #1d1d1f → #ffffff`（实心点变空心环——**中间必须真的空**）
  - `scale 1 → 1.25`
- **④ hold 2.0s**：三步的文字要读完
- **几何基准**：线长 264px，三个节点在 22 / 132 / 242px（首尾各留 22px 让线有"头和尾"，
  节点不压在线的端点上）

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `lineDur` | 0.6s | 线画出总时长，本卡的节奏总旋钮（节点触发时刻全部由它派生）；>1.0s 观众等着线走完，口播已经讲到第二步了；<0.4s 三个节点被挤到 0.12s 内依次亮（读作同时，"推进"看不见） |
| 线的缓动（tsx 写死 `power1.inOut`） | `power1.inOut` | **线的性格，同时是节点间隔的控制器**（见上）；`power2.inOut` 以上必须把 `lineDur` 加到 0.8s+ 才够撑开三个点；`none` 匀速读作进度条（机械感，但节点间隔最均匀，也能用）；`power3.out` 起手极快 = 线被甩下来（推进感丢掉，且三点全挤在开头）；`back` 系列一律不能用（线不会回弹） |
| `nodePop` | 0.18s | 节点弹出耗时；>0.3s 点还在长、线已经走过去了（因果倒置），<0.1s 读作硬现（少了"打点"的确认感） |
| 节点缓动（tsx 写死 `back.out(1.6)`） | `back.out(1.6)` | 节点唯一允许回弹的地方；回弹强度 >2.5 在 14px 的点上读作抖动，改 `power3.out` 也成立（更冷静） |
| `textLag` | 0.067s（2 帧） | **命门**：文字滞后节点的量；0 点与字同时出（读作"一组东西一起淡入"，视线没有落点），>0.2s 两者断开、读作四个动效 |
| `textShift` | 8px | 文字左移进入的位移；0 只剩淡入（可用但更平），>20px 读作文字横向飞入（抢过节点的"打点"） |
| `ringDelay` | 0.10s | 三组到位 → 空心环升级 的呼吸；0 读作"第一个节点比较特殊"而不是"当前在第一步"，>0.4s 两拍断开 |
| `ringScale` | 1.25 | 空心环放大倍数；<1.1 看不出"升级"，>1.5 环大过文字行高，读作一个圆形贴纸落在线上 |
| `ringWidth` | 3px | 环的描边宽（节点直径 14px ⇒ 21%）；<2px 在 540h 上看不见空心，>5px 环心糊掉（又变回实心点） |
| 节点数 | 3~4 个 | 3 是最舒服的（"三步走"）；>5 个线要拉长、行高压缩，节点与文字开始互相挤，该换 `numbered-step-stack` |
| `hold` | 2.0s | 收尾停留；按总字数给（三组 × 两行 ≈ 每组 0.6s） |

## 已知坑
- 线画完再统一弹三个点——"时间轴"这层语义**当场消失**，退化成"一条线和三个点"（清单）。
  这是本卡唯一的致命错法。
- 节点的 delay 手写死成 `0.1 / 0.25 / 0.4`——换线长或换缓动后线和点就错开了，
  慢放下能看见"点比线先亮"（因果倒置，比不同步更假）。必须由线的缓动反解。
- 文字与节点同帧出——视线没有落点，一组"点 + 两行字"读作一个整块淡入，
  "点先亮、字后跟"这半帧的层级关系是本卡的质感来源。
- 空心环用 `outline` 或 `box-shadow` 做——两者都不改变元素盒子，`scale 1.25` 时环会跟着糊；
  必须是 `border-width` 从 0 长出来（配合 `box-sizing: border-box` 让外径不变）。
- 环升级了但背景还是深色——"空心"必须真的空（背景换成底色），不然只是"点变粗了"。
- 三个节点都升级成空心环——"当前"是唯一性给的，三个都升级读作"三个都在进行中"。
- kicker（"第一步"）叠 `opacity: 0.6` 来压层级——`#8a8a8a` 在白底只有 4.29:1 余量，
  叠透明度后掉出可读区（design-language §1 红线）；它本来就是 dim 实色，要更淡就换更深的底。
- 线用 `height` 动画而不是 `scaleY`——每帧触发重排，慢放下能看见线的末端在抖。
- 缓动选了强 `inOut`（`power2/3.inOut`）却没加长 `lineDur`——中段被压缩后三个节点几乎同帧亮，
  "跟着线推进"实测就没了（`power2.inOut @0.4s`：三点前后只差 0.18s）。
  强 inOut 与 `lineDur` 必须一起调。
- 重播只重置 `scale` 不重置 `borderWidth` / `backgroundColor`——上一轮的空心环留在第一个节点上，
  第二遍播放时它开场就是环，"升级"这一拍全丢。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/step-timeline-vertical.tsx——props：仅 `hostSrc`；三步文案与节点 y 在 `STEPS` 常量（`{at, kicker, title}`，线长 `WRAP_H` 264），换内容需改源码。自包含单文件，复制进工程即可用；节奏参数在顶部 CONFIG（线 / 节点缓动写死为 `power1.inOut` / `back.out(1.6)`，非 CONFIG 项），时长/尺寸在 meta。
- HTML/GSAP：demos/step-timeline-vertical/index.html。**换内容改 `.tl-kicker` / `.tl-title` 的文案**；
  改节点位置只改 HTML 里的 `data-at="22|132|242"`（像素，相对 `.tl-wrap` 顶部）——
  节点触发时刻与文字落位都是运行时按它算的，**不用改任何 delay**。
  加/减节点：复制一组 `.tl-node` + `.tl-group`、给新的 `data-at`，然后把 `.tl-wrap` 的 `height`
  改成"末节点 + 22px"即可。节奏只调 `CONFIG.lineDur`（其余全部派生）——
  **加节点时要按比例加长 `lineDur`**（经验值：每个节点至少占 0.18s，四节点 ⇒ 0.75s）。
  那段 `timeAtProgress()`（二分解缓动反函数）是通用的——任何"跟随某条动画进度触发子事件"的
  demo 都可以直接抄走。
- Remotion：已落地为 template/cards/step-timeline-vertical.tsx——节点时刻不是预排的帧表，而是每帧用 `invPower1InOut(at / WRAP_H)` 反解出的秒（L55、L113-114）；线 / 节点 / 文字 / 空心环全部由 `tw()` 按秒驱动，没有 Sequence / spring；空心环三属性（`borderWidth` / `scale` / 背景 `lerpColor`）同用一个 `ringP`（L137-141）。
- 剪辑软件对应物：剪映/CapCut——线用一个细长矩形贴纸 + "缩放（纵向）"关键帧，
  锚点要先拖到顶端（剪映默认中心锚点会让线**从中间往两头长**，那是完全不同的读法）；
  三个圆点各一层缩放关键帧，时间点按线的进度手对（剪映没有缓动反解，
  **实用做法是把线改成匀速/线性**，这样节点时间就是等分的）；空心环做不出 border 补间，
  用"实心点淡出 + 空心环贴纸弹入"两层硬切代替。
  AE——线用 Shape Layer 的 `Trim Paths → End` 从 0% 到 100%（比 Scale 干净）；
  节点触发时刻在 Graph Editor 上看 `End` 的曲线读数直接对，或者给节点的 Scale 加个
  表达式跟着 `End` 的值：`s = thisComp.layer("line").content("Trim Paths 1").end; s > 33 ? 100 : 0`
  （改成 `linear()` 就有补间）。
- 与本库同类卡的分工：**本卡 = 时间轴推进**（有线、有因果、可标当前）；
  `numbered-step-stack` = 清单堆叠（无线、四条并列、只答"要做哪几件"）；
  `chapter-progress-list` = 章节坐标（答"讲到哪了"，是转场不是内容）；
  `line-chart-story-draw` = 数据线（线是数值不是顺序）；`map-route-pin` = 地理路径。
  一句话选卡：**顺序不能颠倒 → 本卡；顺序无关 → numbered-step-stack。**

## 动效范围
- 属于本卡的：竖线 `scaleY 0→1 origin top` 走 `0.6s power1.inOut` 这条"时间在走"的曲线（**缓动强度与 `lineDur` 是一对**——inOut 越强中段越快、节点越挤，实测每个节点间隔不能低于 0.15s）；**节点触发时刻由线的缓动反解得出**（"线到哪、亮哪"）这条实现纪律；节点 `scale 0→1 back.out(1.6)` 的"打点"手感；文字**滞后节点 2 帧**（`0.067s`）+ `x −8 → 0` 的跟随关系；三组全部到位 + `0.10s` 呼吸后才做的第三拍升级（`border-width 0→3px` + 背景换底色 + `scale 1→1.25` 三属性同帧）；空心环的**唯一性**；kicker 用 dim 实色、静置态零透明度。
- 不属于本卡的：demo 那三句具体步骤文案与「第一步/第二步/第三步」这个 kicker 写法、`#e0452c` 这个强调色、25px/14px 字号与 600 字重、线的 `#d2d2d7` 色与 2px 宽、节点 14px 直径、`left: 132px` 这个落位与 460px 的组宽、右列的数字人占位、白底舞台。
- 迁移接口：几何入口只有 `.tl-wrap` 的 `height` 与每个节点的 `data-at`（像素，相对组顶；tsx 对应 `WRAP_H` 与 `STEPS[].at`）——两者按舞台高等比缩放（960×540 ⇒ 1920×1080 时全部翻倍，含 `ringWidth`/节点直径/`textShift`）；节奏入口只有 `CONFIG.lineDur`，节点与文字的时刻全部派生（`textLag` 与 `nodePop` 是**手感常量，换尺寸不要动**）；颜色两个 token —— `accent`（空心环）与 hairline（线）；`hold` 按文字总量给（每组约 0.6s）；竖屏直接沿用（本卡是纵向布局，天生适合竖屏，只需把组宽收到屏宽 80% 并把节点数收到 3）。
- 底色要求：**白底即可**。深底也成立，换值：线用 `rgba(255,255,255,0.14)`、节点实心用 `#f5f5f7`、kicker 用 `#a1a1a6`、空心环的"空"要换成深底色（`#1d1d1f`）而不是白——否则环心是一块白斑，比实心点还重。唯一约束是底不能有横向纹理或网格线：竖线只有 2px 宽，底上任何横线穿过它都会让"线走到哪"读不清。

<!-- ===== /file: video-talkcraft/references/cards/step-timeline-vertical.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/still-layout-relay.md ===== -->

---
name: still-layout-relay
标题: 多图排版 + 焦点接力
一句话: 口播一句里要同时给几张图时，主图（首图）先落、其余同向错峰 80~150ms 入场，讲到谁谁亮（其余 brightness .6 / scale .985，主角 1.03~1.04 + 描边环）0.4s 接力，讲完全部回位再一起退场——两种版式一卡切换：一主两辅 / 三联竖图
适用: "论点 + 两条证据"（评测主图 + 细节、主截图 + 两条评论）用一主两辅；"三个人 / 三个时期 / 三张竖屏截图"用三联竖图；人物不在此镜，素材本身是主角
时长: 一主两辅 8.08s（0.3 主图落 → 0.8 / 0.95 佐证 → 2.4 / 4.2 接力 → 6.0 回位 → 7.6 退场）；三联 7.08s（0.3 起错峰 80ms → 1.4 / 2.8 / 4.2 接力 → 5.6 回位 → 6.6 退场）；demo 两式巡演 15.16s；成片一镜一式，站与站间隔随口播伸缩
能量: 低
类别: 素材呈现
输入: 图
语义: 例证, 强调, 列举
素材形态: 多图
位置: 任意
props: layout, captions, srcs, accent
优先级: P0
代码: template/cards/still-layout-relay.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 人物不在此镜（人在场讲三件事用 parallel-items-with-host） | 可（① 主图常是视频、佐证是截图；② 可放三段竖屏片段） | 可（默认输入：截图 / 照片 / 海报） |

图 / 视频可混排，但同组外框比例统一（裁切不缩放）。tsx 的 `srcs` 走 `<Img>`；放视频把对应 `<Img>` 换成 `<OffthreadVideo muted>`（grid-to-hero.tsx 里有按后缀自动切换的现成写法）。

## 常用场景
1. 评测：产品主图 + 两张细节（镜头群 / 握持）—— ① 一主两辅（demo 所演）
2. 观点：主截图 + 两条评论佐证；案例分析：作品大图 + 两个参考 —— ① 一主两辅
3. 三个人：三位受访者 / 团队三人 / 三个对手 —— ② 三联竖图
4. 三个时期同一对象、三张竖屏截图并列 —— ② 三联竖图

## 意图
多素材同屏最容易做成 PPT：三张一起淡入、各自为政、谁都不是主角。2026-09-05 素材呈现实验室（C1 一主两辅 + C6 三联画）合并入库，做对三条就成立：
1. **排版先定关系**：主次 → 一主两辅（主图 57% 宽 + 右列两张等大）；并列 → 三联竖图（4+4+4 栏）。关系错了版式就错了。
2. **入场有先后有方向**：主图（首图）先落，其余同向错峰 80~150ms（叙事级 50~100ms/项、总时长 <600ms）；全组同时同速淡入 = PPT。
3. **任一时刻只有一个主角**：焦点接力靠"其余降权"（brightness .6 / scale .985），主角本身只动 3~4%；切换 0.4s，两次之间 ≥1.4s。讲完全部回位（"三张都算"），再一起退场。

## 动效核心
- 一式 = 一镜。① hero-duo：`0.3s` 主图落（`y 30→0 + scale .96→1`，power3.out 0.6s）→ `0.8 / 0.95s` 两佐证从右滑入（`x 40→0`，power3.out 0.55s，错峰 0.15）→ `1.3s` 图注淡入（0.4s，错峰 0.1）→ `2.4s` 亮佐证 1 → `4.2s` 亮佐证 2 → `6.0s` 全部回位 → `7.6s` 一起退场（0.4s power2.in，每项 = 图 + 图注，错峰 0.04）→ `8.08s` 结束。主图内部全程 `1→1.06` 匀速缓推，duration = 镜头长 − lead（推到退场为止，写速率不写死秒数）。
- ② triptych：`0.3 / 0.38 / 0.46s` 三张从右滑入（`x 40→0`，power3.out 0.5s，错峰 0.08）→ `0.8s` 图注（错峰 0.08）→ `1.4 / 2.8 / 4.2s` 左 → 中 → 右接力 → `5.6s` 回位 → `6.6s` 退场 → `7.08s` 结束。无缓推（三张同级，谁推谁就成了主角）。
- 接力 = 同一帧三件事：主角 `brightness 1 / scale 1.04`（①）或 `1.03`（②）+ 描边环 0.25s 现身（inset −6、3px、单强调色 `#0066cc`）；其余 `brightness .6 / scale .985`；图注主角变墨色 `#1d1d1f`、其余变浅灰 `#9a9aa0`（回位全部回 `#6e6e73`）。切换 power2.inOut 0.4s，站与站不重叠。
- 几何（960×540）：① 主图 546×388 @ (62, 66)、佐证 250×176 @ (650, 66) / (650, 278)，组包围盒 62~900 水平居中，右下留空象限；图注 14px 在图下 6px、左边与图左对齐（+2 补字形侧距）。② 三张 262×380 @ x 66 / 349 / 632、top 70（4+4+4 栏、间距 21），图注 16px 600 在图下 12px、与图同宽居中。白边卡 padding 8 / 圆角 12 / 唯一投影 `0 12px 40px rgba(0,0,0,.16)` 全组一致。
- demo 里版式名标签与示意图（Picsum，demos/_lib/media）是演示语境；成片用 `srcs` 注入真图、`captions` 换图注、`layout` 单选一式。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 错峰 stagger | ① 0.15 / ② 0.08 | 80~150ms 读作"先后"；>300ms 变逐张展示、<50ms 数不清张数 |
| `dimB` 其余亮度 | 0.6 | .55~.65；再低像坏了，再高分不出主角 |
| `focusScale` 主角 | 1.03~1.04 | 主角只动 3~4%——它本来就在，靠其余退后；>1.08 像鼠标 hover |
| `switchDur` 切换 | 0.4s | power2.inOut；<0.25 闪、>0.6 拖 |
| 站与站间隔 | 1.4~1.8s | = 口播讲这一张的句长，成片按台词伸缩，≥1.4 让观众看完 |
| `heroPush` | 1.06 | 只给 ① 的主图；速率 = .06 / 镜头长，镜头越长推得越慢 |
| `exit` | 0.4s + 0.04 错峰 | 比入场快；图与图注同一项一起走 |
| 图注字号 | ① 14 / ② 16 @960 | caption 档（28~32@1080）；<14 等于没有 |

## 已知坑
- 三张一起同速淡入——PPT；观众读不出"哪张先"，也就读不出"哪张重要"。
- 佐证入场方向不一致（一张从右一张从下）——散；同组同向。
- 焦点靠主角放大（1.1+）而不是其余降权——像鼠标 hover；主角要"站着不动，别人退后"。
- 接力太密（<1s）——观众还没看清上一张；一站 ≥1.4s。
- 讲完不回位直接退场——最后一张被记成"结论"；回位是"三张都算"的语义。
- 白边 / 圆角 / 投影不统一，或横竖混合各自缩放——同组同造型，混合时统一到同一外框比例（裁切不缩放）。
- 图注压到图上或字号 <14@960——图注在图下、caption 档。
- 一镜里两式连用——版式即关系，一句话只有一种关系；demo 巡演两式是为了看全。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/still-layout-relay.tsx——`layout` 单选一式（默认 `"tour"` 两式巡演 = demo 画面）、`captions` 三条图注、`srcs` 三张真图（① 顺序：主图 / 佐证 1 / 佐证 2；② 左中右）、`accent` 描边环色；时长用导出的 `durationFor(layout)`（① 254 帧 / ② 224 帧 / tour 467 帧）；站与站要随台词伸缩改 `TABLE[layout].relays / reset / exitAt`。
- HTML/GSAP：demos/still-layout-relay/index.html——`ORDER` 决定巡演顺序与式数（删到一个即单式预览）；`CONFIG` 是共通节奏、`TABLE` 是两式时间表；`.pic` 整块换成 `<img>` 即真图。
- 与 layout.md 的接口：无人物 → 组包围盒居中（§4）；离画幅边 ≥48@960（§2）；图注 caption 档（§5）；同组同造型（§8）。
- 剪辑软件对应物：剪映"画中画 + 关键帧"三层摆位 + 对非主角层打"亮度 / 缩放"关键帧；AE 是 Brightness & Contrast + Scale 关键帧 + 描边 Shape Layer 跟随；CapCut 同理。

## 动效范围
- 属于本卡的：两式的时间表（主图 / 首图先落 → 同向错峰 → 图注 → 接力 → 回位 → 一起退场）；接力的三件事（其余 brightness .6 / scale .985、主角 1.03~1.04 + 描边环、图注变色）及其 0.4s power2.inOut；① 主图 1→1.06 匀速缓推（duration = 镜头）；退场 0.4s + 0.04 错峰；两式的落位几何（组居中、边距 ≥48、图注在图下 6 / 12px、白边卡造型一致）。
- 不属于本卡的：示意图（演示语境素材，demos/_lib/media，不属于本卡）、图注文案、版式名标签（demo 巡演用）、白底舞台。
- 迁移接口：`layout` 选式；`captions` / `srcs` 换文案与图；`accent` 换强调色（全片只有一个）；`TABLE` 的 relays / reset / exitAt 按口播句长伸缩；换画幅时几何按 960×540 等比缩放，竖屏 ① 改主图在上、两佐证在下一行。
- 底色要求：白底即可（白边卡 + 投影靠白底分层；深底把投影加重到 .35）。

## 落位自检（2026-09-05 用户定版，选卡时抄进 SHOTBOOK 该镜自检列）
- **组包围盒居中**：① 三张包围盒 x 62~900、② 66~894，中心与 480 偏差 >48 返工；离画幅边 ≥48（① 右列到右边 60、图注到底边 ≥58）。
- **入场先后**：定妆帧取主图落定那一刻（① 0.9s / ② 0.8s），其余尚在滑入（x >0）；三张同帧到位即错。
- **接力唯一**：任一时刻恰有一张 brightness 1 + 描边环，其余 .6；回位帧（① 6.4 / ② 6.0）三张全部 1、无环。
- **描边环几何**：inset −6、3px，圆角 = 卡圆角 + 6，四边等距（>8px 偏差返工）。
- **图注字号**：① ≥14@960、② ≥16@960（≥28 / 32@1080），缩到 390 宽复看可读；图注不压图、不压邻图。
- **一镜一式**：SHOTBOOK 只写一个 `layout`；站数 = 口播提到的张数（① 两站、② 三站）。

<!-- ===== /file: video-talkcraft/references/cards/still-layout-relay.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/strike-and-replace.md ===== -->

---
name: strike-and-replace
标题: 划线纠错替换
优先级: P1
代码: template/cards/strike-and-replace.tsx
一句话: 一条语义色横线 0.15s 快斩划穿旧值（power3.out），隔 0.1s 旧值淡出、新值从同一位置下方 8px 升起顶上来（0.25s），随后划线 + 新值同屏定格 2s——替换感来自"占了同一个位置"，容器宽度由隐形尺子撑住，句子其余部分零位移
适用: 口播里"不是 A，而是 B"这个高频句式——旧观念纠正、旧价格/旧参数作废、版本对比、辟谣；一句话里只替换一个值的时刻
时长: 起手静置 0.35s → 划线 0.15s → 隔 0.10s → 交换 0.25s → hold 2.0s；总 2.85s
能量: 中
类别: 强调标注
输入: 人(可选), 文
语义: 转折
素材形态: 透明通道
位置: 任意
props: hostSrc
---

## 意图
本库的强调类全是"**加强**"——`keyword-pop-highlight` 砸重音、`highlighter-sweep` 涂高亮、
`magnifier-detail` 放大细节、`focus-dim-spotlight` 压暗聚焦、`callout-line-label` 引线标注、
`scribble-annotation` 手绘圈注。它们能让一个词变重，但**没有一张能表达"否定"**。

而口播里"不是 A，而是 B"是极高频的句式：旧观念 → 新观念、旧价格 → 新价格、
上一代参数 → 这一代参数、传言 → 事实。这时候单纯把新值高亮出来是不够的——
观众需要看到**旧的那个被否掉**。这张卡的价值就在于：**划穿的动作本身就是论证**。
一条线从左划到右，你连"这个说法已经过时了"这句话都不用说完，观众已经接受了。

命门三条：① **新值必须出现在旧值的位置上**（两者绝对定位同位叠放）——
换行另起或旁边并列都会读作"这里有两个数据"，替换感全部来自"占了同一个位置"；
② **语义色只上那条线**，文字保持墨色——给新值也上色的话，观众的注意力被"新值好看"抢走，
"旧值被划掉"这一拍反而轻了（本库"一个画面一个语义色"的通例在这张卡上尤其致命）；
③ **容器宽度必须先被撑住**——把 `from` / `to` 里更长的那一串排进一个 `visibility: hidden` 的
"隐形尺子"占位，换值时句子其余部分零位移。

## 动效核心
三拍结构（固定秒数，起手静置 `lead` 0.35s 后开始）：

| 阶段 | 时刻 | 动作 |
|---|---|---|
| 快斩 | 0.35–0.50（`strikeDur` 0.15s） | 横线 `scaleX 0→1`（`transform-origin: left`，`power3.out`：冲出去收住） |
| 立换 | 0.60–0.85（斩完隔 `swapLag` 0.10s，`swapDur` 0.25s） | 旧值 `opacity 1→0`（`power1.out`）；新值 `opacity 0→1` + `y +8→0`（`power2.out`），**同位** |
| 定格 | 0.85–2.85（`hold` 2.0s） | 划线与新值同屏定格，让观众把"旧 → 新"这条论证读完 |

- **划线用 `scaleX` 不用 `width`**：`transform-origin: left center` + `scaleX 0→1`。
  动 `width` 是每帧重排（本库反例清单第一条），在 `inline-block` 的槽里还会带着整句抖
- **线的规格**：高 = 字号 × 8%（32px 字号 → 3px，随字号等比），圆角 2px，语义色（红 `#e0452c` / 橙）。
  它是 `.word.from` 的**子节点** —— 旧值淡出时线跟着一起走，不会留一条线压在新值上
- **划线缓动 `power3.out`、只给 0.15s**："否定"是一个决断动作，一瞬间冲出去再收住才像"手划过去"；匀速读作进度条，>0.4s 读作"慢慢涂"。
  但**不要回弹**（`back` / `elastic`）——这是纠错不是花字，回弹会把严肃的否定读成综艺整活
- **同位叠放**：旧值与新值都 `position: absolute` 在同一个 `.slot` 里，
  CSS `left: 50%` 配 GSAP `xPercent: -50` —— 两者都以槽中线为锚。
  于是**短的那个值在预留宽度里居中**：尺子撑出来的余量分到两边，读作排版留白；
  左对齐会在尾部留一个刺眼的空洞（观众读成"这里少打了一个字"）
- **隐形尺子**：`<span class="ruler">` 里排 `from`/`to` 中更长的那一串、`visibility: hidden`。
  它撑出槽的宽度，两个值都绝对定位不占流 ⇒ **换值零位移**。
  demo 句尾那句「，一年翻了八倍」就是证人：撑宽没做对，它会在替换那一帧横跳
- **新值升起 8px（≈ 字号 20%）**：方向朝上——"新的顶上来"。朝下（从上方落）读作"又来一条"，因果反了
- **`keepStrike`**：默认 `true`（划线留在屏上，论证的证据还在）；
  设 `false` 则划线随旧值一起淡出，读作"改完了、痕迹擦掉"——用在不想强调否定、只想换值的场合
- **层级**：舞台白底 → 句子（一行，`nowrap`）→ 替换槽（`inline-block`、宽度由尺子定）→ {尺子 / 旧值+线 / 新值}

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `strikeDur` | 0.15s | 快斩时长（tsx 注释：一瞬间的快斩；>0.4s 读作"慢慢涂"） |
| `swapLag` | 0.10s | 斩完到换值的间隔（tsx 注释：斩完立刻换，不留犹豫） |
| `swapDur` | 0.25s | 旧值淡出 + 新值升入的"替换"那一拍；太短读作硬切换字，太长两个值半透明叠在一起、糊成一团 |
| `hold` | 2.0s | 定格：划线 + 新值同屏让观众读完"旧 → 新"；<1s 等于没论证（见已知坑） |
| 线高 | 字号 × 8% | 3px @32px 字号；<5% 在 1080p 缩放后会断续，>12% 变成一条色条、把字盖住（那是高亮不是划掉） |
| 线的圆角 | 2px | 方头读作代码里的下划线，圆头才像笔划过；>4px 短值上会看到线变成胶囊 |
| `toRise` | 8px（≈ 字号 20%） | 新值升起距离；0 读作原地淡入（替换感减半），>20px 读作"从下面飞进来"、抢戏 |
| 划线缓动 | `power3.out` | 冲出去收住的决断感；匀速读作进度条；**禁 `back`/`elastic`**（纠错不是花字，回弹读作综艺整活） |
| 新值缓动 | `power2.out` | 顶上来后收住；`back.out` 会让新值弹一下，与"严肃更正"的气质冲突 |
| `lead` | 0.35s | 起手静置等口播念到这个值；0 则线已经划完观众还没看清旧值是什么 |
| `keepStrike` | `true` | 划线是否留在屏上；`true` = 证据还在（默认，否定更重），`false` = 改完擦掉痕迹 |
| 语义色 | 红 `#e0452c` / 橙 | **只上那条线**；上到文字上就会抢掉"划掉"这一拍 |

## 已知坑
- 新值另起一行或排在旧值旁边——读作"这里有两个数据"，替换感消失；两者必须绝对定位在同一个位置上叠放。
- 容器宽度没被隐形尺子撑住——替换那一帧句子其余部分横跳，一眼是 bug；`from`/`to` 里更长的那一串必须先占位。
- 短值在预留宽度里左对齐——尾部留一个刺眼的空洞，观众读成"这里少打了一个字"；两个值都以槽中线为锚。
- 划线动 `width` 而不是 `scaleX`——每帧重排，`inline-block` 的槽里会带着整句抖（本库反例清单第一条）。
- 划线的 `transform-origin` 用默认中心——线从中间往两头长，读作"删除线正在被插入"而不是"手划过去"。
- 划线是槽的兄弟节点而不是旧值的子节点——旧值淡出后线还留在屏上，压在新值身上（新值看起来也被划掉了）。
- 语义色同时上到新值/旧值上——注意力被"新值好看"抢走，"旧值被否掉"这一拍反而轻了；一段只给一个语义色，且只给线。
- 划线加回弹缓动——严肃的更正读成综艺整活，气质全毁。
- 新值从上方落下——因果反了（读作"又来一条"而不是"新的顶上来"）；必须从下方顶上来。
- 划完立刻换值（没有交换段）——硬切换字，观众来不及看清"是这个值被划掉了"。
- 一句话里替换两个以上的值——两条划线互相打架，观众不知道该看哪个否定；一句只否一个。
- hold 太短（<1s）——论证的落点是"划线 + 新值同屏"这个画面，没时间读就等于没论证。
- 句子设成可折行（没有 `nowrap`）——替换槽后面的字被挤到第二行，"零位移"这条纪律看不出来（demo 踩过：句子太长导致证人跑到下一行）。
- 用在"新增/强调"的语境——本卡的动作语义是**否定**，用来强调一个正确的值会让观众以为它被划掉了。
- **叠在上一话题的满画面上**（2026-08-28 v4 用户实判）——"但这次不是X"类枢轴句是**下一镜的开题动作**，
  本卡要上清过场的舞台；把它挤在旧镜（比如一屏统计数字）的角落里，划线会与旧内容相撞、
  转折的戏剧性也没了。切镜点提前到枢轴句起点（cinematography.md §4.5 第 2 条）。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/strike-and-replace.tsx——props：仅 `hostSrc`；`from` / `to` 在 CONFIG、句子其余文字在 JSX，换内容需改源码。自包含单文件，复制进工程即可用；节奏参数（`lead` / `strikeDur` / `swapLag` / `swapDur` / `hold` / `toRise` / `keepStrike`）在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：demos/strike-and-replace/index.html。**换内容只改 `CONFIG.from` / `CONFIG.to`** 与句子模板里
  替换槽前后的文字（`.sr-line` 里那句）；隐形尺子会自动取更长的那个值，不需要手改宽度。
  节奏只改 `CONFIG.strikeDur / swapLag / swapDur / hold`（demo 与 tsx 同名）。语义色改 `.strike` 的 `background`，
  线高改 `.strike` 的 `height`（保持 = 字号 × 8%）。
- 剪辑软件对应物：剪映/CapCut——旧值与新值各一个文本层**对齐到同一个位置**（关键：不要用"上下排列"的模板），
  划线用一个 3px 色条层做"缩放"或"擦除"入场（`transform-origin` 靠左，剪映里把锚点拖到左端），
  旧值在划完那一帧起 0.2s 不透明度 100→0、新值同帧起位置 +8px→0 配不透明度 0→100。
  AE——线用 Shape Layer 的 `Scale X` 键（Anchor Point 拖到左端）或 `Trim Paths` 的 `End 0→100%`（更干净），
  两个文本层同 Position、透明度对开；隐形尺子在 AE 里的等价做法是**用最长值先排好版再改文字**
  （或给两层套同一个固定宽度的 Null 父级）。
- 与本库强调类的分工：`keyword-pop-highlight`（砸重音）/ `highlighter-sweep`（涂高亮）/
  `type-contrast-emphasis`（字形落差）/ `magnifier-detail`（放大）/ `focus-dim-spotlight`（压暗）/
  `callout-line-label`（引线）/ `scribble-annotation`（手绘圈注）全是**加强**；
  **本卡是唯一的"否定"**。它与前述任何一张都不在同一句里混用——
  同一句里既有"被划掉的旧值"又有"被砸出来的重音"，观众不知道这句到底是肯定还是否定。
  同族的 `number-counter` 是"数字在涨"（过程），本卡是"值被否掉、换掉"（结果），两者语义不同。

## 动效范围
- 属于本卡的：三拍时间结构（快斩 0.15s → 隔 0.10s 交换 0.25s → 定格 2.0s，固定秒数、`hold` 对齐口播）；划线用 `scaleX` + `transform-origin: left`（拒绝动 `width`）与线高 = 字号 8% / 圆角 2px 的规格；旧值淡出与新值从下方 8px 顶上来在**同一位置绝对定位叠放**这条机制（替换感的全部来源）；划线作为旧值子节点、随旧值一起淡出这条实现纪律；隐形尺子撑宽容器以保证换值零位移；短值在预留宽度里居中（两值都以槽中线为锚）；"语义色只上那条线、文字保持墨色"这条取舍；划线缓动 `power3.out` 且禁回弹。
- 不属于本卡的：demo 那句「上下文窗口是 128K → 1M，一年翻了八倍」的具体文案与数值、32px 字号与 700 字重、`#e0452c` 这个具体红（橙同样成立）、`#1d1d1f` 墨色、白底舞台、左侧主持人（数字人）占位、以及"替换槽在句中"这个位置（句首句尾同样成立）。
- 迁移接口：`CONFIG.from` / `CONFIG.to` 是唯一的内容入口（尺子自动取更长者）；节奏只有 `strikeDur` / `swapLag` / `swapDur` / `hold` 四个固定秒数（`hold` 对齐口播句长）；`toRise` 与线高按字号等比缩放（20% / 8%），换画幅时这两条比例保持不变；`keepStrike` 切换"证据留屏 / 改完擦掉"；语义色换成品牌的警示色即可，但**只能上到线上**；竖屏把句子拆短（替换槽后面必须还留至少 3~4 个字当"零位移"的证人，且整句必须单行 `nowrap`）。
- 底色要求：白底/浅底最佳（墨色文字 + 语义色线靠对比成立）。深底把文字换成浅色、线换成更亮的警示色（红在深底上要提亮一档，否则与深底糊在一起），其余参数不变；**底不能有横向纹理**——划线是一条横向生长的线，带横向纹理的底会让线的端点位置读不准。

## 落位自检（2026-09-05 用户定版，选卡时抄进 SHOTBOOK 该镜自检列）
- 标注几何（框 / 圈 / 线 / 箭头 / 放大镜锚点）一律由**目标的实测包围盒**反推——DOM `getBoundingClientRect` / `measureText`，四边留白 16~24px 等距，**不目测**。
- 实现后抽该镜定妆帧核对：标注是否恰好套住 / 指向目标，偏差 **> 8px 返工**（`references/layout.md` §3）。
- 目标会滚动 / 移动时，标注钉在内容坐标系随内容动（SKILL.md ③）。

<!-- ===== /file: video-talkcraft/references/cards/strike-and-replace.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/subscribe-cta.md ===== -->

---
name: subscribe-cta
标题: 多平台关注 CTA
一句话: 控件 0.35s 弹入 → 光标 0.8s 弧线移入交互 → 状态翻转 + 确认动效（YouTube 变灰"已订阅"+铃铛 ±16° 衰减摇摆 / B站长按 0.55s 进度环走满后三图标 0.2s 间隔依次点亮 / 通用胶囊变"已关注"+对勾 0.36s 划入），单式样 3s 内完成后自动淡出
适用: 口播的收尾或价值兑现点（"觉得有用点个关注"）；按平台取其中一种式样，一条视频最多出现一次
时长: 单式样 2.6~3.6s（控件 0.35s + 光标 0.8s + 状态翻转 0.3s + 确认动效 0.4~0.8s + hold 0.5s；三连多一段 0.55s 长按最长）；demo 三式串演约 9.7s（A 0.1→3.25 / B 3.4→6.95 / C 7.1→9.7）
能量: 中
类别: 人物互动
输入: 人(可选), 界
语义: 号召
素材形态: 透明通道
位置: 收尾
props: hostSrc
优先级: P1
代码: template/cards/subscribe-cta.tsx
---

## 意图
不是"提醒关注"，是"示范关注"——光标替观众把整个动作做一遍，降低行动门槛。
命门：**光标必须走过去**（瞬移点击就没有"跟着做"的引导意义）、**点击要有反馈链**
（下压→状态翻转→确认动效，三个反馈缺一环就假）、**式样要认平台**（B站说"三连"却演一个订阅按钮，
观众对不上自己屏幕上的东西）、**用完即走**（overlay 停留超过 8s 变牛皮癣）。

常见于：几乎所有 YouTube 口播频道、B站三连引导、小红书/抖音关注贴纸、Like Subscribe Bell Overlay（1.7K 销量）、LottieFiles subscribe 品类。

## 动效核心
三种平台式样**共用同一套三段机制**，只换交互动作与确认动效：
① 控件弹入 → ② 光标弧线移入做交互 → ③ 状态翻转 + 确认动效。

**共有机制（三式一致）**
- 控件入场：scale 0→1.06→1，0.35s（0.65 段 `power3.out` + 0.35 段 `power2.out`）
- 光标移入：从屏外（x:1010）弧线移到控件，0.8s——x 用 `power2.inOut`、y 用 `sine.inOut`，异速叠出弧线；
  transform-origin 锚在箭头尖（0% 0%），按压微缩不让尖端移位
- 交互帧：光标 scale→0.9 一拍（0.09s）+ 控件下压至 0.94（0.08s `power2.in`）
- 状态翻转就在**按下那一刻**发生（不等抬手），随后 `back.out(3)` 回弹 0.2s
- 光标顺势朝右下滑出并淡出 0.45s
- 段落切换：淡出淡入各 0.3s，中间 0.15s 留白

**式样 A · YouTube 订阅（订阅 + 铃铛）**
- 红底白字圆角矩形"订阅" → 点击变灰白"已订阅"
- 铃铛：点击后 0.15s 淡入，`transform-origin: 50% 8%`（顶部悬点），rotation 按
  16→−12→8→−5→2→0 衰减序列摆 0.8s；同时一圈涟漪 scale 0.6→1.9 + opacity 0.7→0

**式样 B · B站一键三连（长按点亮）**
- 三枚灰阶线框圆图标（拇指/圆币/五角星）以 0.12s 间隔依次弹入
- 光标移到"点赞"**按住不放**：进度环（r=45、`stroke-dasharray` 282.7）0.55s `ease:"none"` 走满一圈
  ——三连的门槛感在这里，点一下就亮就不叫"三连"
- 环走满后**从左到右依次点亮**，间隔 0.2s：底盘转高亮色 + 线框 stroke 转白（各 0.16s）
  + scale 1→1.22→1 弹跳（0.14s `power3.out` + 0.26s `back.out(2.4)`）+ 一圈涟漪 scale 0.85→1.75

**式样 C · 通用关注（小红书 / 抖音 / X）**
- 黑底白字胶囊"关注" → 点击变灰白"已关注"，文案左侧腾出对勾位
- 确认动效：对勾按笔序划入——`stroke-dasharray` 27 / dashoffset 27→0，0.36s `power2.out`
- 同时一圈胶囊形涟漪（inset −8、border-radius 999）scale 0.9→1.28 + opacity 0.6→0

**收场**：每段做完 hold 0.5s 让观众读结果，随后整段 opacity→0（0.3s，`segFade`）。
**音效位**：点击帧标注"啵"、铃铛首摆"叮"、三连每次点亮各一声"叮"（逐次升调）、对勾划入"嗒"（demo 无声，成片补）。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 光标移入 | 0.8s | <0.4s 接近瞬移，引导感消失；>1.2s 观众开始等它 |
| 点击下压 | 0.94 | >0.97 看不出按了；<0.9 控件像被捏爆 |
| 铃铛首摆角 | 16° | >25° 像报警器；<8° 摇了等于没摇 |
| 铃铛摆次 | 4~5 次衰减 | 匀速摆是钟摆一眼假；2 次以内停得太急像卡住 |
| 三连长按环 | 0.55s | <0.3s 门槛感消失，退化成"点一下"；>0.9s 观众以为卡住了 |
| 三连点亮间隔 | 0.2s | <0.1s 三个像同时亮，读不出"连"；>0.35s 三段各自为政，不成一串 |
| 点亮弹跳峰值 | 1.22 | <1.1 点亮像换色不像被点中；>1.35 图标从队列里跳出来 |
| 对勾划入 | 0.36s | 直接显形=贴图；>0.6s 观众等它画完 |
| 单式样在场 | 3~5s | >8s 变牛皮癣挡内容；<2.5s 观众还没反应过来就没了 |
| 出现次数 | 1 次/条 | 多次出现=乞讨感，转化率反降 |

## 已知坑
- 铃铛匀速摇摆——没有阻尼的是节拍器不是铃铛，必须逐摆衰减。
- 光标瞬移到按钮上——观众没看到"移动→点击"的过程，示范意义为零。
- 点击后控件不变状态——没有"已订阅/已关注"的结果反馈，这次点击像没发生。
- 三连做成"点一下三个一起亮"——B站三连的手感命门是**长按**+**依次**，同时亮就成了普通点赞。
- 三连不给长按进度环——观众不知道要按多久，示范就少了最关键的那条信息。
- 对勾用现成 ✓ 字符淡入——确认动效要有"划"的笔序，淡入的对勾是贴图。
- 平台式样和平台不对版（对 B 站观众演订阅按钮）——观众在自己屏幕上找不到你演的那个东西。
- overlay 常驻画面——挡内容又降级成背景噪音，用完即走才有效。
- `fromTo` 忘了 `immediateRender: false`——涟漪环建表时就把 from 态刷上去，控件"还没被点"时红环已经挂在外圈（实测三连三个环全部提前显形）。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/subscribe-cta.tsx——props：仅 `hostSrc`；三式串演写死在 JSX 与 `B_A / B_B / B_C` 时间常量里，光标落点是 `CONFIG.P_SUB / P_LIKE / P_FL` 写死坐标，无 variant prop，换式样 / 文案 / 布局需改源码。自包含单文件，复制进工程即可用；节奏参数在顶部 CONFIG，时长由 `TOTAL` 推出、尺寸在 meta。
- HTML/GSAP：demos/subscribe-cta/index.html。三段各是一个独立函数（`segYouTube` / `segTriple` / `segFollow`），
  落地时**只留你要的那一段**——把 `[segYouTube, segTriple, segFollow]` 数组裁成一个即可，共用的
  `moveTo/down/up/cursorOut/P` 四个辅助函数不用改。换文案改 `.sub-btn` / `.ftxt` 与 `.call(...)` 里的"已订阅/已关注"；
  换配色改 `CONFIG.accent`。
- Remotion：已落地为 template/cards/subscribe-cta.tsx——三式内联、不用 Sequence；铃铛按 `bellSwings` 关键帧逐段 lerp（L285-292）；长按环 `arcOffset` 282.7→0 线性（L319）；三连按 `T_LIGHT + i×triStep` 逐个点亮（L301-314）；对勾 dashoffset 27→0（L333）。
- 剪辑软件对应物：LottieFiles 搜 "subscribe button bell" / "like coin favorite"，有大量现成 JSON 可直接挂；
  剪映"贴纸→订阅按钮/一键三连"动图；AE 用 Bounce/Overshoot 表达式 + 铃铛父子链摆动 + Trim Paths 画对勾。
- （实测变体）评论引导：不做按钮+光标+确认三件套，而是把 CTA 关键词（如 comment 的触发词）以蓝色/荧光高亮**常驻**在人物胸前，小字词流继续滚、大字关键词锚定不动——引导目标从"点按钮"换成"记住这个词去评论"，全程零光标、也不占收尾时段。见 TheAIScaler（u8OWXXTcu3Q / a2iG5GkM8KE）。

## 动效范围
- 属于本卡的：**三种平台式样共有的三段严格串行因果链**——控件 scale 0→1.06→1 弹入（0.35s）→ 光标从屏外**弧线**移入（0.8s，x 用 `power2.inOut`、y 用 `sine.inOut` 异速叠出弧线，锚点在箭头尖）→ 交互帧的反馈链（光标 scale→0.9 + 控件下压至 0.94 一拍 0.08s `power2.in` + **在按下那一刻**换状态 + `back.out(3)` 回弹 + 光标顺势滑出淡出）。三式各自的确认动效也属于本卡：铃铛 `transform-origin: 50% 8%`、按 16→−12→8→−5→2→0 **衰减**序列摆 0.8s + 一圈涟漪 scale 0.6→1.9；三连的**长按进度环** 0.55s `ease:"none"` 走满一圈 + **从左到右 0.2s 间隔依次点亮**（底盘换色 0.16s + scale 1→1.22→1 `back.out(2.4)` 弹跳 + 逐个涟漪 0.85→1.75）；关注的对勾 `stroke-dasharray` 划入 0.36s `power2.out` + 胶囊形涟漪 0.9→1.28。段落淡出淡入 0.3s / 段间留白 0.15s / 用完即走也属于本卡。
- 不属于本卡的：主持人占位（数字人）、平台名小字标签的文案与措辞、控件圆角与字号、三个图标的具体图形（拇指/圆币/星星只是"三个可点亮目标"的中性画法）、涟漪与铃铛的颜色、光标 SVG 的具体形状、为压实拍加的白底盘/白描边（属于对比度落地，见底色要求）。
- 迁移接口：**平台式样切换 = 只留一式**——HTML demo 保留 `segYouTube` / `segTriple` / `segFollow` 之一（三者共用 `moveTo/down/up/cursorOut/P`，删掉另两个不影响其余代码）；tsx 里三式内联，要留一式需删掉另两式的 JSX 块并把保留式的起点常量（`B_A` / `B_B` / `B_C`）改到 0.1 起。demo 把三段串起来只是为了一次看全三种机制。所有时序在 `CONFIG`：共有段用 `btnIn`/`cursorMove`/`clickDip`，A 段用 `bellSwings` 数组/`bellTime`，B 段用 `triStagger`/`holdPress`/`triStep`/`triPop`，C 段用 `checkDraw`，段落切换用 `segFade`/`segGap`/`segHold`。换尺寸时改 `CONFIG.START`（光标起点，按舞台宽重算）；落点 HTML 由 `P(el, fx, fy)` 从元素实际位置反算、换布局不用改数字，tsx 则是写死坐标 `CONFIG.P_SUB / P_LIKE / P_FL`，换布局要重新量并改这三组数字。文案改 `.sub-btn` / `.ftxt` 与 `.call(...)` 里的翻转文案（tsx 在 JSX 的"订阅 / 已订阅""关注 / 已关注"字面）；`triStep` 与三连图标数量解耦（按 index 排期，加减图标自动顺延）。
- 底色要求：白底即可。**`CONFIG.accent` = #e62117 是"这是那个按钮/已被点亮"的语义色，本卡保留**——它承担"这是那个控件"与"这一下生效了"的识别功能，换平台改成对应平台的按钮色（B 站粉、抖音红等），但不要灰阶化；未点亮态、已完成态、铃铛、涟漪一律走灰阶/墨色。落地时 overlay 压在实拍画面上，控件需自带足够对比：红底白字与白底盘天然成立；**黑胶囊要加白描边（`box-shadow: 0 0 0 3px #fff`）、深色铃铛要坐白色圆底盘、图标名走白底小胶囊**——实测不加这三样时它们会直接糊进人物的深色衣服。灰阶的"已订阅/已关注"态在深色背景上要提亮一档。

<!-- ===== /file: video-talkcraft/references/cards/subscribe-cta.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/sway-parallax.md ===== -->

---
name: sway-parallax
标题: 左右摇移
优先级: P1
代码: template/cards/sway-parallax.tsx
一句话: 镜头在一张比画幅宽近一倍的长页面前横向匀速平移扫过（150~170px/s），极轻 rotateY 3~4° 跟随倾斜，起摇缓入 0.55s、到位极缓收住但不停死，hold 期继续以末速漂
适用: 素材横向比画幅宽得多时——宽横幅、流程图、时间线、并列对比长图、超宽截图；口播正在顺着讲一条横向序列（"第一步…第二步…"）时最贴，摇移速度就是讲述节奏
时长: 实拍 8~15s（行程 ÷ 速度，与本段口播等长）；demo 压缩演示：缓入 0.55s → 匀速摇移 4.5s → hold 1.1s，全程 6.2s
能量: 低
类别: 运镜
输入: 图, 截图
语义: 例证, 氛围
素材形态: 横屏
位置: 任意
props: hostSrc
---

## 意图
一张超宽的图强行缩进画幅里，等于把所有细节压成一排看不清的色块；切成三张分屏，
又打断了"这是一条连续的线"。摇移两件事同时解决：**保住原始尺寸的清晰度**，
**保住横向序列的连续感**——观众亲眼看到第二步长在第一步右边。命门：
**速度有上限**（观众要边扫读边听口播，超过 ~190px/s 的文字跟不上）、
**rotateY 只做"跟随"**（≤4°；大了就不是摇移而是 3D 旋转，属 [tilt-3d-page](tilt-3d-page.md)）、
**两端不撞停**（起手缓入、到位极缓收住但末速非零，hold 期继续漂）。

## 动效核心
- 结构三层：`.world`（`perspective: 1200px`，摇移用**大透视**——值小了页面横向扫过时边缘会像鱼眼那样变形）→ `.camera`（相机层，`preserve-3d`，宽 1880px ≈ 画幅两倍）→ `.shadow` 投影层 + `.page` 页面层
- 页面必须**真的比画幅宽**（1.5~2 倍）。这是本卡成立的物理前提：不宽就没有可摇的东西
- 三段速度曲线：
  1. **起摇缓入** `sine.in` 0.55s——`sine.in` 的平均速正好是末速的一半，所以缓入段走过的距离 = `panSpeed × accelDur / 2`，与匀速段速度**严丝合缝地接上**（不做这个换算，两段之间会有速度阶跃，读作"顿了一下"）
  2. **匀速摇移**——`x` 从起手位走到终点位，速度恒定是"镜头在平移"的全部；末段用本库通用运镜 ease `p + (1−r)·p²·(1−p)`（`r = endRate ≈ 0.5`）极缓收住，末速非零
  3. **hold 期**——沿用末速 `panSpeed × endRate` 匀速续漂，`rotateY` 极缓回一点点（相机永不静止）
- `rotateY` 跟随：镜头往右摇（`x` 往负走）时页面右侧后仰 3~4°，与 `x` 同一时间轴。它的作用是让"平移"读作**镜头在页面前走**而不是**图片在滑动**；配合 `z` 方向轻微前移（14px）让透视位移更可读
- 行程 / 速度 / 时长三者只有两个自由度：`时长 = 行程 ÷ 速度`。实拍时**先定速度**（可读性上限），再由素材宽度算出时长，最后检查这个时长是否与本段口播匹配；不匹配就改素材宽度（裁掉一段）而不是提速
- hold 期终点不能超出素材右端——`xTo + 末速 × holdDur` 必须仍在页面内，否则 hold 期会摇出画布露白

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `panSpeed` | 168px/s（960 宽画幅；上限约 190） | 摇移速度。>190px/s 观众正在扫读的文字被抽走、跟不上；<90px/s 拖节奏、观众先于讲述读完整页 |
| `xFrom` / `xTo` | 40 / -770 px | 起手与终点位置。起手让页面左端露在画幅内**但留 40px 边距**（贴死边会露出素材外的空白）；终点要给 hold 期留余量 |
| `swayDeg` | 3.2°（上限 4°） | rotateY 跟随幅度。0 = 纯平移（读作图片在滑，弱一档但安全）；>6° 变成 3D 旋转卡，正文远端开始不可读 |
| `accelDur` | 0.55s | 起摇缓入。0 会瞬间满速、读作跳变/seek；>1.2s 观众等着它起步 |
| `endRate` | 0.5 | 末速占匀速的比。收住但不停死；1 = 一路匀速到底（也成立，更"机器"一点） |
| `zLift` | 14px | 摇移时页面整体前移量，让透视位移更可读。0 也成立；>40px 页面会明显变大，读作在推近 |
| `perspective`（父容器） | 1200px | 摇移专用大透视。<800px 页面横扫时边缘鱼眼变形；>1600px 透视太弱、rotateY 跟随白做 |
| `holdDur` | 实拍 2~6s / demo 1.1s | 到位停留；这段仍以末速漂，且**终点不能超出素材右端** |

## 已知坑
- 摇移速度超过 ~190px/s（按 960 宽画幅折算）——观众正在读页面上的文字，字被从视野里抽走，一句话没读完就过去了。这是本卡唯一的硬上限；要更快就说明这段不该摇移（该用硬切或 whip-pan）。
- 页面只比画幅宽一点（1.1~1.2 倍）——没有可摇的行程，摇了几十像素就到头，读作"画面抖了一下"。宽度不够就整页展示（配 [slow-push-in](slow-push-in.md)）更诚实。
- 起手/收尾撞停（没有缓入、或用 `power2.out` 末速归零）——瞬间满速读作程序 seek；末速归零则在到位那帧停死。两端都要连续。
- `rotateY` 给到 8° 以上——不再是"镜头在页面前平移"，而是页面在转，语义变成 [tilt-3d-page](tilt-3d-page.md)；且远端正文开始不可读。
- 缓入段的距离没按 `v × t / 2` 换算——匀速段与缓入段之间存在速度阶跃，观众读作"起步顿了一下"。这个换算是本卡时序的技术本体。
- hold 期摇出素材右端——画幅露出舞台底色，一眼假。`xTo` 必须给 hold 期留余量。
- 摇移方向与阅读方向相反（从右往左扫一条从左到右的流程）——观众的眼睛和镜头对着干。中文/英文横排素材一律往右摇（页面往左走）。
- 摇移中途变速（一会儿快一会儿慢）或叠了手抖噪声——观众正在扫读，速度噪声直接造成晕动感。本库不做定格抖动。
- 纵向长页误用本卡——纵向滚是 [evidence-scroll-tour](evidence-scroll-tour.md)（它带"讲到关键处减速停留"的完整语法）；本卡的横向摇移是不同的信息结构。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/sway-parallax.tsx——props：仅 `hostSrc`（声明未使用）；宽页内容与 `.camera` 宽 1880 在 JSX / CSS 常量里，换素材需改源码。自包含单文件，复制进工程即可用；速度与姿态参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：`demos/sway-parallax/index.html`。换素材改 `.page` 内整块 DOM（或换成一张超宽 `<img>`）并同步改 `.camera` 的 `width`；节奏与姿态全在顶部 `CONFIG`（`panSpeed` / `xFrom` / `xTo` / `swayDeg` / `accelDur` / `holdDur` / `endRate` / `zLift`）；透视值改 `.world` 的 `perspective`。**改 `panSpeed` 或行程后不用手算时长**——三段时长由 `dist`/`accelDist`/`mainDur` 运行时推出。核心可摘走：`CONFIG` + `camEase` + `DemoShell.register` 回调体。
- Remotion 移植：`x` 是一条三段 `interpolate`——`interpolate(frame, [0, tAccel, tMain, tHold].map(s => s*fps), [xFrom, xFrom + dir*accelDist, xTo, xTo + dir*holdRate*holdDur])`，缓入段 `Easing.in(Easing.sin)`、主段 `Easing.bezier(0.33,0.33,0.5,0.85)`（末速非零）、hold 段 `Easing.linear`；分段 easing 在 Remotion 里要么拆成三个 `interpolate` 按 `frame` 区间选，要么用一个 `interpolate` 配多段 `easing`（v4 支持数组式 easing 需自行分段）。`rotateY` / `z` 各一条同法。外层 `perspective: 1200`，相机层 `transformStyle: 'preserve-3d'` + `transform: \`translateX(${x}px) translateZ(${z}px) rotateY(${ry}deg)\``。**纵向变体**只需把 `x` 换成 `y`、`rotateY` 换成 `rotateX`，速度上限同样按可读性取。
- 剪辑软件对应物：这就是各家说的 **pan / 横移镜头（whip pan 的慢速版）**。剪映——超宽图片打两个"位置"关键帧（X 从 +40 到 -770），**两端都设线性**再单独给首尾各加一个缓动关键帧；"3D 旋转"的 Y 轴打 0→3° 跟随。AE——Position 的 X 打关键帧，速度图（Graph Editor）里把起点速度设 0、终点速度设为匀速的一半（这就是 `endRate`），3D 图层的 `Y Rotation` 跟 3°；或者反过来固定素材、给摄像机（Camera）的 Position 打关键帧（更接近"镜头在走"的物理）。Premiere——`Motion → Position` 线性关键帧 + `Basic 3D → Swivel` 微量跟随。

## 动效范围
- 属于本卡的：一条**横向摇移速度曲线**——`sine.in` 缓入 0.55s（缓入距离按 `v×t/2` 换算与匀速段严丝合缝接上，这是本卡时序的技术本体）→ 匀速扫过（速度 ≤190px/s@960 宽，可读性上限）→ 末段极缓收住且**末速非零** → hold 期沿末速续漂；`rotateY` ≤4° 的**跟随**倾斜（与 `x` 同一时间轴，把"图片在滑"改写为"镜头在页面前走"）+ `z` 轻微前移；三层结构（父容器 `perspective` 800~1600px / 相机层 `preserve-3d` / 投影层）；"页面必须比画幅宽 1.5~2 倍"与"摇移方向须顺阅读方向"两条前提纪律；`时长 = 行程 ÷ 速度` 且**先定速度再算时长**的取值顺序。
- 不属于本卡的：demo 里的灰阶线框宽横幅长页（左端品牌区 / 中段四段流程卡与箭头 / 右端数据总结格及其全部文案与数值）、行程与页面宽度的具体数值、摇移选"往右"这一具体决定（随素材阅读方向定）、投影浓度取值、素材入场动画、页面上的标注。
- 迁移接口：`panSpeed` 是**按画幅宽等比缩放**的量（本卡按 960 宽设计 168px/s，1920 画幅折算约 336px/s——可读性上限随之等比放大）；`xFrom/xTo` 由素材宽度与画幅宽算出（起手留 40px 边距、终点给 hold 余量）；`swayDeg` 定跟随幅度上限 4°；`accelDur` 起摇缓入；`endRate` 定收尾；`perspective` 按画幅等比缩放。**纵向变体**（长截图上下摇）：`x→y`、`rotateY→rotateX`，其余参数与纪律不变。
- 底色要求：白底即可——本卡零颜色、零装饰，只是一条 transform 曲线。深色素材同样成立，仅投影需按 [tilt-3d-page](tilt-3d-page.md) 同法换成亮边。

<!-- ===== /file: video-talkcraft/references/cards/sway-parallax.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/terminal-typing-log.md ===== -->

---
name: terminal-typing-log
标题: 终端逐行推进
优先级: P1
代码: template/cards/terminal-typing-log.tsx
一句话: 终端窗里命令逐字符敲出、日志成 4 字一簇地"蹦"出来，写满 8 行后缓冲区整跳一个行高（零插值），以 `...` 结尾的行打完自动冻结 0.6s 制造悬念，末尾成功行是全片唯一的语义色
适用: 口播讲"我跑了一遍""它真的能装上""构建/部署/测试的结果"——需要拿命令行当证据的时刻；开发工具测评、AI 编程演示、技术教程与踩坑复盘；不适合非技术受众的软性内容（终端本身会筛掉观众）
时长: 起手静置 0.32s → 命令 0.4~0.5s 敲完 → 每条日志 0.15~0.5s 打完 + 行间 0.27s；11 行一段共约 8.2s（`...` 悬停各占 0.6s）
能量: 中
类别: 素材呈现
输入: 人(可选), 界
语义: 例证, 过程演示
素材形态: 透明通道
位置: 任意
props: hostSrc
---

## 意图
讲"我真的跑过这个东西"时，静态终端截图的说服力接近零——观众看不出那是跑出来的还是拼出来的。
而"文字慢慢出现"的伪终端更糟：它读作网页加载动画，不是命令行。
本卡的价值在于三条**手感纪律**——真终端的输出不是匀速滴出的，是**成簇蹦出**的；
真终端的滚动**不滑行**，是整行整行地跳；真构建过程里那些 `...` 结尾的行**会卡住**，那个卡顿就是悬念。
把这三条同时做对，观众不用读懂日志内容也会相信"这段是真跑出来的"，然后把注意力交回给你的讲述。
命门：**分块突进**（逐字符匀速一眼是 CSS 教程）、**滚动零插值**（加 ease 立刻假）、
**语义色只给一个**（成功行绿色；日志、命令、报错都上色就变成彩虹终端，"成功"这一拍的重量没了）。

## 动效核心
- **窗体**：深底终端窗 836×356（= 40 窗栏 + 22×2 留白 + 8 行 × 34 行高，可见 8 行是硬约束）+ 三交通灯（灰阶）+ 中间路径标题。等宽字体 21px，行高 `round(fontSize × 1.6) = 34px`
- **① 分块突进（本卡的第一手感）**：先算线性揭示数 `linear = floor((t − start) × rate)`，
  再上取整到分块粒度 —— `revealed = min(len, ceil(linear / chunk) * chunk)`。
  日志 `chunk 4` @ 68 char/s（成簇蹦出）、命令 `chunk 1` @ 23 char/s（手在敲键盘，逐字符）。
  两条速率差一个量级是"人"和"机器"的区别，拉平了就都变成机器
- **② 滚动零插值（第二手感）**：`steps = 已开打的溢出行数`（下标 ≥ `visibleLines` 的行里 `t ≥ start` 的个数），
  缓冲区 `translateY = −steps × lineHeight`。**没有 tween、没有缓动**——该行开打的那一帧整跳一个行高。
  终端不会滑行，加 0.2s ease 立刻读作"网页在滚"
- **③ 省略号悬停（第三手感）**：以 `...` 结尾的行打完后自动冻结 0.6s，
  这 0.6s 里画面**完全静止**（光标也已撤掉），下一批日志才来。这是"它在想/在装"的唯一表达
- **光标**：方块 11×21px（≈ 字号 × 0.55），2Hz 方波闪（`floor(t × 2) % 2`），
  **只在该行未打完时存在**——打完即撤。所以冻结段是真静止，不是"有个东西在闪"
- **颜色分级**：命令 `#f2f2f4` 白 / 日志 `#9b9ba3` 灰 / 提示符 `#6f6f78` / 成功 `#33d16b`（唯一语义色）。
  报错场景把成功绿换成警示红，同样只给一行
- **行占位纪律**：未到时刻的行用 `visibility: hidden` 而不是 `display: none`——**占位但不显示**，
  整段布局零重排；跳的只有缓冲区那一个 transform
- **层级**：舞台白底 → 终端窗（深底，唯一深色区域）→ 缓冲区（唯一被 transform 的元素）→ 行 → 光标

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `logChunk` | 4 | 日志分块粒度，本卡第一命门；2~4 都成立（4 最"机器"），=1 退化成逐字符即刻变教程代码，>6 每簇太长读作"整行硬切" |
| `logRate` | 68 char/s | 日志线性底速（分块前）；<40 观众开始读日志内容（跑偏），>100 一行几乎瞬现、丢掉"在跑"的过程感 |
| `cmdRate` / `cmdChunk` | 23 char/s / 1 | 命令行速率与粒度；命令必须 `chunk 1`（手在敲不会 4 字齐蹦），速率要明显低于日志——两者一致就分不出"人打的"和"机器吐的" |
| `lineDelay` | 0.27s | 行间基础延迟；单行可用 `d` 覆写（真实日志段落长短不齐，全用同一个值一眼是假数据），全表 <0.15s 糊成一片、>0.5s 拖节奏 |
| `hover` | 0.60s | `...` 结尾行的自动冻结；<0.35s 看不出"卡了一下"，>1.0s 观众以为播放器卡住 |
| `visibleLines` | 8 | 视口可见行数（窗高由它反推）；<6 一直在跳、读作抖动，>12 溢出发生得太晚、看不到滚动这一拍 |
| `lineHeight` | 34px（= 21 × 1.6） | 行高＝滚动步长，两者必须严格相等；不等的话跳完会错半行，一眼是 bug |
| `cursorHz` | 2 | 光标闪烁；行业默认，调快像故障、调慢像死机 |
| `leadIn` | 0.32s | 起手静置（等口播开口）；0 则观众还没看到窗就已经在打字 |
| 成功行位置 | 末行 | 成功/失败必须是**最后一行**——中间给结论，后面的日志会把它冲掉 |

## 已知坑
- 逐字符匀速揭示（`chunk 1` 用于日志）——一眼是 `setInterval` 教程，真终端的 stdout 是缓冲区刷出来的、成簇。
- 滚动加了缓动（哪怕 0.15s ease）——终端不会滑行；平滑滚动立刻读作"这是个网页"。
- 命令行和日志同速——分不出"人在敲"与"机器在吐"，整段变成一台机器自言自语。
- 全表用同一个行间延迟——节奏机械等距，一眼是假数据；真实日志的段落长短不齐。
- 没有 `...` 悬停——整段变成匀速刷屏，"它在装/在编译"这层因果消失，只剩文字流。
- 悬停期间还有光标在闪——冻结的意义是**画面完全静止**，闪一下就把"卡住了"读成"还在跑"。
- 光标打完不撤（常驻在已完成行末）——每行结尾挂一个闪块，8 行同时闪成圣诞树。
- 语义色发给多个类型（日志蓝、警告黄、成功绿、报错红全上）——彩虹终端，"成功"那一拍没有重量；一段只给一个语义色。
- 结论行放在中间——后续日志会把它冲下去，观众记不住结果。
- 未到时刻的行用 `display: none`——行一出现就把整段布局重排一遍，与缓冲区的整跳叠加成"抖两下"。
- 只给 `.viewport` 加 `overflow: hidden` 就当裁切——那是**边框框**裁切，滚上去的行会露在内边距留白里显示半截；裁切层要单独一层、`inset` = 内边距（本 demo 踩过）。
- 每帧无条件写 `textContent`——11 行一起重排，慢放时能看到掉帧；只在揭示数真的变了才写 DOM。
- 用真实的长构建日志（几十行滚很久）——终端是**证据**不是内容，8~12 行足够；再多观众开始读日志、离开你的讲述。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/terminal-typing-log.tsx——props：仅 `hostSrc`（84px 圆角标）；日志内容在 `CONFIG.lines`（常量，非 prop），换内容需改源码。自包含单文件，复制进工程即可用；节奏参数在顶部 CONFIG，时长由 `buildSchedule()` 推出、尺寸在 meta。
- HTML/GSAP：demos/terminal-typing-log/index.html。**换内容只改 `CONFIG.lines`**——每行 `{ k, t, d?, p? }`：
  `k` 取 `cmd`（命令，逐字符）/ `log`（日志，分块）/ `ok`（成功，唯一语义色），
  `d` 覆写行间延迟、`p` 覆写打完后的冻结（缺省时 `...` 结尾行自动 `hover`）。
  节奏参数全在 `CONFIG`（`logChunk` / `logRate` / `cmdRate` / `lineDelay` / `hover` / `visibleLines`）。
  改字号要同步改 `lineHeight`（= `round(fontSize × 1.6)`）与 `.ln` 的 `height`、`.term` 的高度三处——
  滚动步长与行高不等会错半行。报错场景把 `.ln.ok` 的绿换成警示红即可，其余不动。
- Remotion 移植：`CONFIG.lines` 原样搬成 `LINES`，`buildSchedule()` 里的秒全部 × `fps` 变帧号（纯函数，可直接抄）。
  揭示数用 `const linear = Math.floor(interpolate(frame, [start, start + dur], [0, len], {extrapolateLeft:'clamp', extrapolateRight:'clamp'})); const revealed = Math.min(len, Math.ceil(linear/chunk)*chunk)`；
  滚动**不要用 interpolate** —— `let ty = 0; for (let i = VISIBLE; i < N; i++) if (frame >= starts[i]) ty -= LINE_H;`（这就是"零插值"在帧驱动下的等价写法，原版 terminal-simulator 也是这么写的）；
  光标 `Math.floor((frame/fps)*2) % 2 === 0 && revealed < len`；每行包一个 `<Sequence from={starts[i]} layout="none">` 或直接按 frame 判断可见性。
  **不要用 `Math.random` 给速率加抖动**——多趟渲染会闪烁；分块本身已经提供了不匀感。
- 剪辑软件对应物：剪映/CapCut——每行一个文本层，用"打字机"入场预设但**必须把它的速度调到能看出成簇**（多数预设是逐字匀速），
  `...` 悬停就是在那一行后面留 0.6s 空白不放任何层；滚动用整段位移的**两个关键帧贴在同一帧**（形成硬跳）或直接把整组文本层往上挪一个行高再切一次；
  AE——文本层的 Source Text 用 `slider` 驱动的表达式取子串（`text.sourceText.substring(0, Math.ceil(n/4)*4)`，`ceil/4*4` 就是分块），
  滚动用 Position 的 **Hold 关键帧**（右键 Toggle Hold Keyframe，这是"零插值"的原生实现，千万别用默认线性关键帧），光标用一个方块 Solid 配 `Math.floor(time*2)%2` 的 Opacity 表达式。
  任何软件的"终端/黑客打字预设"一律不用——全是逐字匀速 + 常驻闪烁光标 + 平滑滚动，三条命门全踩。

## 动效范围
- 属于本卡的：分块突进的揭示算法（`revealed = ceil(linear/chunk)*chunk`，日志 chunk 2~4 / 命令 chunk 1，两条速率差一个量级）；滚动零插值（溢出行开打那一帧整跳一个 `lineHeight`，无 tween 无缓动，步长严格等于行高）；`...` 结尾行打完自动冻结 0.6s 且冻结期画面完全静止；方块光标 2Hz 方波闪且只在当前行未打完时存在（打完即撤）；行间延迟可逐行覆写以造成不等距节奏；命令/日志/成功三级颜色分级里"一段只给一个语义色且放在末行"这条纪律；未到时刻的行 `visibility: hidden` 占位（布局零重排，只有缓冲区一个 transform 在动）；裁切层独立一层以内边距为界。
- 不属于本卡的：demo 那段 `pnpm install / pnpm build` 假日志的具体文案与数字（214.6 kB、6.42s 全是演示语境）、`~/projects/koubo-site` 这个路径标题、三交通灯与 12px 圆角这套 macOS 窗饰、`#17171a` / `#212126` 这组深底取值与 `#33d16b` 这个具体绿、21px 字号与 836×356 这个窗尺寸、角标主持人（数字人）、终端这个载体本身（同一套时序可以套在日志面板、CI 输出、聊天机器人的流式回答上）。
- 迁移接口：`CONFIG.lines` 是唯一的迁移入口——把日志换成目标项目的真实输出（保留"命令 → 日志 → 结论"的三段结构与不等距的 `d`），成功行永远放末位；语速变化时只改 `lineDelay` 与各行 `d`（**`logChunk` / `logRate` / `hover` / `cursorHz` 保持不变**——这四个是手感常量，跟着语速缩放会让快语速下的分块糊成匀速）；尺寸按画幅等比缩放，但 `lineHeight = round(fontSize × 1.6)`、`窗高 = 窗栏 + 留白×2 + visibleLines × lineHeight` 两条等式必须同时成立；竖屏把 `visibleLines` 提到 10~12、窗宽收窄并把日志文案缩短（等宽字体不折行是硬约束，折行会让滚动步长失效）。
- 底色要求：**终端窗内必须深底**（这是本卡唯一允许的非白例外）——"命令行"这层语义靠深底成立，且成功行的绿只有在深底上才有足够对比；舞台本身仍是白底，深色只占那个窗口。浅底终端（Solarized Light 一类）也能跑同一套时序，但要把日志灰压到 `#6b6b73` 一级、成功绿换成 `#1a7f3c` 一级，否则灰日志在白底上糊成一片。

<!-- ===== /file: video-talkcraft/references/cards/terminal-typing-log.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/tilt-3d-page.md ===== -->

---
name: tilt-3d-page
标题: 3D 立面展示
优先级: P1
代码: template/cards/tilt-3d-page.tsx
一句话: 静态页面先正视静置一拍让人读清，再用 1.2~1.8s 从平面倾斜成 3D 立面（perspective 1000px + rotateY 12~25° 配一点 rotateX），投影同步加深并往倾斜反侧偏移，立起后保持微透视慢漂
适用: 把网页/落地页/UI 界面当"产品"来展示的时刻——作品展示、产品介绍、"我们做了这么个东西"、案例墙；也用于让页面从"文档"降级为"背景道具"，好在它前面叠字幕或图表
时长: 实拍：正视静置 0.5~1s → 立起 1.2~1.8s → 立面 hold 3~10s（随讲述）；demo：0.5s + 1.5s + 3.0s，全程 5.0s
能量: 中
类别: 运镜
输入: 图, 截图
语义: 例证, 氛围
素材形态: 横屏, 界面
位置: 任意
props: hostSrc
---

## 意图
正视的页面截图是"信息"，倾斜的页面是"物件"——同一张图，立起来之后观众的解读从"我要读它"
变成"我在看一个东西"。这个转换有两个用处：一是**给页面加身份**（作品/产品，值得被展示），
二是**给页面降权**（它变成道具，前面就能压字幕、叠图表，而正视的页面压字会打架）。做对的命门：
**倾斜量必须留在可读区间**（rotateY 12~25°；超过 30° 页面远端的正文就读不了了——如果本来就不需要读，那是另一种设计，见"已知坑"）、
**透视值不能太小**（900~1200px；给到 400px 会读作鱼眼变形，不是空间）、
**投影必须跟着倾斜变**（加深 + 往反侧挪；投影不动的话页面读作一张贴纸而不是浮在空间里的实体）、
**立起后不静止**（微透视慢漂，两轴极缓续走）。

## 动效核心
- 结构三层：`.world`（`perspective: 1000px` + `perspective-origin`，装在**父容器**上）→ `.camera`（被 transform 的相机层，`transform-style: preserve-3d`）→ 内含 `.shadow` 投影层 + `.page` 页面层
- 投影层做法：与页面同尺寸的深色块 + `filter: blur(26px)` + `translateZ(-34px)` 沉在页面后方。
  因为它和页面同处一个 `preserve-3d` 空间，倾斜时**自动**被透视压扁并与页面产生位移差 —— 这就是"厚度感"的来源；
  另外再叠一层动效驱动的 `opacity` + `x/y` 偏移（光源不动、物体转了 ⇒ 影子必须挪）
- 页面层加 `backface-visibility: hidden`，避免倾斜时边缘半透明发灰
- 起手：正视平面（`rotateY: 0`）静置 `startHold`（0.5~1s）——先让观众读清"这是一张什么页"，再把它变成物件
- 立起：`rotateY 0 → −19°`（负值＝右侧后仰，左近右远）+ `rotateX 0 → 4.5°`（一点俯角）+ `scale → 0.94`（轻微后退），
  1.5s `power2.out`。**这里允许用 power2.out**——立起是一个"摆放"动作（有始有终的事件），不是持续运镜，收住是对的
- 为什么要配 rotateX：纯 rotateY 读作"门绕轴转"；加一点 rotateX 才读作"摆在展示墙上"
- 为什么要 `scale 0.94`：倾斜后页面的投影对角线变长，不后退就会顶到画幅边
- 投影同步：`opacity 0.05 → 0.19`（正视时几乎贴在舞台上 → 立起后浮起来）+ `x/y` 往倾斜反侧偏移，与立起**同一时长同一缓动**
- hold 期（微透视慢漂）：`rotateY −19° → −22.5°`、`rotateX 4.5° → 3.2°`，`sine.inOut` 走 3~10s。
  **两轴不同步**（一个继续转、一个往回收）是"活的镜头"与"机械转台"的分界；投影跟着再挪一点
- 文字可读性检查：立起后页面**远端**（后仰那一侧）的正文缩小最多，验收时按远端最小字号看，不是按近端

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `perspective`（父容器） | 1000px（范围 900~1200） | 空间强度。<600px 边缘拉伸像鱼眼、读作"变形"不是"空间"；>1600px 透视太弱，倾斜后近似平面斜切（等于白做 3D） |
| `rotYTo` | -19°（范围 12~25°，取负＝右侧后仰） | 立面强度。<10° 观众读不出立起来了；>30° 远端正文不可读（要读的页面绝对不能超） |
| `rotXTo` | 4.5° | 俯角。0 = 门轴转的观感；>10° 页面上边缘压缩严重，像从桌上俯拍（那是 evidence-scroll-tour 的 2.5D 变体） |
| `scaleTo` | 0.94 | 立起时的后退量。1.0 会让倾斜后的页面顶到画幅边；<0.85 页面变小、展示感变弱 |
| `tiltDur` | 1.5s（范围 1.2~1.8s） | 立起时长。<0.8s 读作"甩"（那是转场的语气）；>2.5s 拖节奏、观众等着它转完 |
| `startHold` | 0.5s（范围 0.5~1s） | 正视静置。0 = 观众还没读清页面就被转走了；>1.5s 就成了两个镜头 |
| `shadowTo` | 0.19 | 立面投影浓度。0.05 以下没有浮起感；>0.3 白底上读作脏，深底上则整块糊 |
| hold 两轴终点 | rotY -22.5° / rotX 3.2° | 慢漂目标。两轴**必须不同步**（一个进一个退）；同步会读作机械转台 |

## 已知坑
- 倾斜超过 30°——页面远端的正文彻底不可读。这时只有两条路：要么降回 25° 以内，要么承认"这一段不需要读页面内容"（纯道具用法），那就该把正文换成灰阶占位、别让观众徒劳地去读。
- `perspective` 给到 400~600px——页面边缘被强烈拉伸，读作鱼眼镜头/变形贴图，不是"空间里的一张页"。900~1200 是安全区。
- `perspective` 写在被 transform 的元素自己身上（而不是父容器）——CSS 里 `transform: perspective(...)` 与父容器 `perspective` 的透视中心不同，多元素场景下各转各的、空间会散。本卡固定写在 `.world` 父容器上。
- 投影不跟着倾斜变（固定的 `box-shadow`）——页面读作一张贴纸。投影必须①同处 `preserve-3d` 空间被透视压扁 ②浓度随倾斜加深 ③位置往倾斜反侧挪。
- 忘了 `transform-style: preserve-3d`——投影层和页面层被拍平到同一平面，`translateZ` 完全失效，厚度感归零（最容易犯且最难看出原因的一个）。
- 忘了 `backface-visibility: hidden`——倾斜时页面边缘发灰/透出底色。
- 立起后完全静止——本库通病。立面 hold 必须有微透视慢漂。
- hold 期两轴同相位同速续转——读作电动转台在匀速转，机械感；两轴要不同步（一进一退）。
- 立起用 `linear` 或匀速——"摆放"是个事件，匀速会读作机械臂。这里恰恰**要**用 `power2.out` 收住（与 [slow-push-in](slow-push-in.md) 的纪律相反，因为语义不同：那是持续运镜，这是一次动作）。
- 倾斜后页面顶到画幅边（甚至被裁）——立起时忘了配 `scale` 后退。倾斜后包围盒会变大，验收要看四角。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/tilt-3d-page.tsx——props：仅 `hostSrc`（声明未使用）；页面内容与 792×452 尺寸在 JSX / CSS 常量里，换素材需改源码。自包含单文件，复制进工程即可用；姿态与节奏参数在顶部 CONFIG，时长/尺寸在 meta。
- HTML/GSAP：`demos/tilt-3d-page/index.html`。换素材改 `.page` 内整块 DOM（或换成铺满的 `<img>`）；姿态与节奏全在顶部 `CONFIG`（`rotYFrom` / `rotYTo` / `rotXTo` / `scaleTo` / `tiltDur` / `holdDur` / `holdRotY` / `holdRotX` / `startHold` / `shadowFrom` / `shadowTo`）；透视值改 `.world` 的 `perspective`，投影质感改 `.shadow` 的 `blur` 与 `translateZ`。核心可摘走：`CONFIG` + `DemoShell.register` 回调体 + 三层结构的那几行 CSS（`perspective` / `preserve-3d` / `.shadow`）。
- Remotion 移植：外层 `<div style={{perspective: 1000, perspectiveOrigin: '50% 46%'}}>`，内层相机 `<div style={{transformStyle: 'preserve-3d', transform: \`rotateY(${ry}deg) rotateX(${rx}deg) scale(${s})\`}}>`；`ry` 用 `interpolate(frame, [t0, t1, t2], [0, -19, -22.5], {easing: Easing.out(Easing.quad), extrapolateRight: 'clamp'})`（立起段 `Easing.out(Easing.quad)`，hold 段换 `Easing.inOut(Easing.sin)` 需拆两个 interpolate 或用 `Easing.bezier`），`rx` / `s` 同法；投影是同尺寸的 `<div style={{filter: 'blur(26px)', transform: 'translateZ(-34px)', opacity: op, ...}}/>` 放在页面前面（DOM 顺序在下层）。注意 Remotion 的 `<AbsoluteFill>` 默认不带 `preserve-3d`，必须显式写。
- 剪辑软件对应物：AE——把截图放进 3D 图层（打开图层的 3D 开关），`Y Rotation` 打 0→-19° 关键帧，配一个摄像机（Camera）并设 Zoom 对应 perspective，投影用复制图层 + 压暗 + 快速模糊 + 稍微错位；或直接用 `CC Cylinder`/`Corner Pin` 的伪 3D 做法（不推荐，透视不真）。剪映——素材"3D 旋转"/"倾斜"关键帧（Y 轴），投影靠"阴影"参数（跟随变化有限，弱一档）。Premiere——`Basic 3D` 效果的 `Swivel` 参数 + `Distance to Image`。**这就是各家素材站说的 "3D mockup / device tilt" 品类**（Envato 上有大量现成 AE 模板）。

## 动效范围
- 属于本卡的：**平面→3D 立面的姿态转换**这一完整动作——正视静置 0.5~1s → `rotateY 0→12~25°`（负值右侧后仰）+ `rotateX 0→~4.5°` + `scale→0.94` 后退，1.2~1.8s `power2.out` 收住（"摆放"是事件，允许末速归零，与持续运镜的纪律相反）；三层结构（父容器 `perspective 900~1200px` / 相机层 `preserve-3d` / 独立投影层 `translateZ(-34px)` + blur）；**投影与倾斜同步联动**——同处 3D 空间被透视压扁 + 浓度 0.05→0.19 加深 + 位置往倾斜反侧偏移；hold 期**两轴不同步**的微透视慢漂（一轴续转、一轴回收，`sine.inOut`）；"倾斜量 ≤25° 以保正文可读"与"透视值 900~1200 以免读作变形"这两条阈值纪律。
- 不属于本卡的：demo 里的灰阶线框产品落地页（导航/Hero 大标题/主图占位/三栏特性卡/价格条及其全部文案与排版）、倾斜方向选右侧后仰这一具体决定、投影的具体模糊半径与浓度取值（随底色调）、素材的入场动画、页面上叠加的任何字幕或图表。
- 迁移接口：`perspective`（父容器）定空间强度，换画幅时按画幅宽等比缩放（本卡按 960 宽 / 792px 页宽设计）；`rotYTo` / `rotXTo` 定立面姿态（**按"远端最小字号是否可读"验收**，不是按近端）；`scaleTo` 按倾斜量反推（倾斜越大退得越多，保证四角不出画）；`tiltDur` 1.2~1.8s 与讲述"我们做了个东西"这句话等长；hold 两轴终点只需保持"不同步"，具体值随意；投影 `blur`/`translateZ`/`opacity` 三者按画幅等比缩放，深底素材把浓度降一半。
- 底色要求：白底即可（demo 白底 + 灰阶投影已足够读出"页面浮起来"）。深色底同样成立，但投影要改用**亮边**（深底上的暗投影不可见）——即把 `.shadow` 换成浅色微光层，或给页面加一圈 1px 亮描边替代投影，这属于迁移时的底色适配。

<!-- ===== /file: video-talkcraft/references/cards/tilt-3d-page.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/timeline-photo-strip.md ===== -->

---
name: timeline-photo-strip
标题: 时间线照片带
一句话: 有先后的几站（默认四张 240×160）沿一条时间线上下交替，日期 caption 靠线一侧；相机横移逐站停靠（移 0.9s + 停 1.0s，停靠 z 1.05 让邻站明确出画，当前站 1.03 亮 / 其余 .7）→ 拉开 z .62 看全条、有意停 1.2s → 与字同收
适用: 成长史、版本演进、四个时间点、年度回顾、事件梳理——**有先后**的 3~5 站（三个平级例子用 gallery-wall-dolly）；口播逐站讲、讲完还要看全条的段落
时长: 9.9s（第一站 0.4 + 1.0 → 三次横移各 0.9 + 1.0 → 拉开 1.1 → 看全条 1.2 → 退场 0.4）；成片站数与停靠按口播改，拉开后的停留 = 口播结语那句
能量: 中
类别: 素材呈现
输入: 图
语义: 时间地点, 步骤
素材形态: 横屏, 多图
位置: 中段
props: srcs, labels
优先级: P1
代码: template/cards/timeline-photo-strip.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| 不适用（人在场用 D 组并列句卡 `parallel-items-with-host`） | ✗（tsx 的 `srcs` 仅走 `<Img>`，不播视频；换法见复用指引） | **默认输入**（3~5 站每站一张；timeline 是"有先后的几站"） |

## 常用场景
1. 成长史 / 版本演进："从一台笔记本到一间工作室"四站横移（demo）
2. 事件梳理 / 年度回顾：3~5 个时间点沿一条线走完再看全条
3. 产品版本史：v1 → v4 每版一张截图，讲到哪版停哪版
4. "这三年发生了什么"式的回顾，拉开时观众看到整条时间线

## 意图
有先后的几张图逐张全屏切，观众记不住顺序。把它们挂在一条时间线上，相机沿线横移逐站停靠，观众同时得到"逐个看"和"它们的先后位置"两层信息；
拉开看全条那一拍是本卡的结论镜头。做对的命门：
1. **相机层是唯一被 transform 的元素**：`transform-origin: 0 0`，每一站用 `camTo(z, px, py)` 反解出 `scale / x / y` 把目标点搬到画心。
2. **停靠段真静止，当前站点亮防死**：相机在 hold 里不续走；当前站 `brightness 1 + scale 1.03`、其余 .7——画面有变化但"停下来看这一张"的语义不破。
3. **停靠焦距 1.05 让邻站明确出画**：1.0 时邻站与画幅边齐平、邻站 caption 离边 6px，读作贴边；1.05 让邻站出画 24px，是运镜语义不是贴边。
4. **走完必拉开看全条，且有意停留**：拉开后停 1.2s（成片 = 口播结语那句），停留结束与字同收。

## 动效核心
- 结构：白底；`.cam`（相机层，宽 1600，`transform-origin: 0 0`）→ 一条时间线（`left 60, top 300, 1500×3, #1d1d1f`）+ 四张 240×160 白边卡上下交替（`(120, 90) / (480, 330) / (840, 90) / (1200, 330)`，中心 x 240 / 600 / 960 / 1320，站距 360）；日期 caption 22px 700 靠时间线一侧（上排在线下 318、下排在线上 266）、`nowrap`。
- `camTo(z, px, py) = { scale: z, x: 480 − z·px, y: 270 − z·py }`；停靠 `camTo(1.05, cx, 270)`（上排照片离顶 49.5）；拉开 `camTo(.62, 780, 300)` 看全条（四张两侧各留 71）。
- 时间表：`0` 第一站居中、全部 `.7` → `0.4` 第一站点亮（`brightness 1 + scale 1.03`，0.4s）→ `1.4 / 3.3 / 5.2` 横移到二三四站（`move 0.9 power2.inOut`，点亮从移动中段 `move×0.5` = 0.45s 起）→ `7.1–8.2` 拉开（7.4 起 0.5s 全部复原）→ `8.2–9.4` 有意停留 → `9.4` caption + 时间线退、`9.44` 照片退（0.4，`power2.in`）→ `9.9` 结束。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `stopZ` 停靠焦距 | 1.05 | 1.0 邻站齐平画幅边（贴边感），>1.1 上排照片顶到安全边 |
| `wideZ` 拉开焦距 | .62 | 拉开要装下全部站且两侧 ≥48（实测 71） |
| `move` 站间横移 | 0.9s | <0.7 读作"甩过去"，>1.5 观众等它到位 |
| `hold` 每站停留 | 1.0s | **信息在 hold 里**；成片按"讲这一站要几秒"给 |
| `dim` / `focus` | .7 / 1.03 | 非当前站降权 / 当前站点亮；平面不用 blur |
| `pull` 拉开 | 1.1s | 比单站横移略长 |
| `tailHold` | 1.2s | 看全条的有意停留；成片 = 口播结语那句 |
| 站距 | 360 | 与停靠焦距一起决定邻站露多少；<300 一屏三站不像巡览，>420 横移太快 |

## 已知坑
- 用固定 `transform-origin`（center）+ 位移凑停靠——zoom 变化时甩出横向漂移；每站的目标必须反解到画心。
- 停靠 1.0 且站距 360——邻站与画幅边齐平、邻站 caption 离边 6px，读作贴边；1.05 让邻站明确出画。
- 照片不上下交替——四张一排，相邻两张的 caption 打架，且横移时整条读作一行缩略图。
- 停靠段什么都不动（无点亮）——1s 全静止，观众以为卡帧（motion_check 也 FAIL）。
- 拉开全条后不留停留直接切——观众刚看到全貌就被切走，等于没拉开；停留结束再退场。
- 三个平级的东西硬套时间线——观众会去找"先后"，没有先后的用 `gallery-wall-dolly`。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/timeline-photo-strip.tsx——`srcs` 四张真图、`labels` 日期 caption；时长 309 帧（9.9s + 0.4s），导出的 `END` 是动画结束秒；站数不同时改 `CONFIG.centers`（同时改 `POS` 与时间线长度），hold 要长改 `CONFIG.hold` / `tailHold`。tsx 的 `srcs` 仅走 `<Img>`；要放视频把 `<Img>` 换成 `<OffthreadVideo muted>`（Remotion 自带；grid-to-hero.tsx 里有按后缀自动切换的现成写法），其余不动。
- HTML/GSAP：demos/timeline-photo-strip/index.html——`CONFIG` 是全部节奏；`.ph` 整块换 `<img>`，`.cap` 换文案；核心可摘走：`CONFIG` + `camTo()` + 时间轴。
- 与 `gallery-wall-dolly` 的边界：那张是三个平级案例挂 3D 墙、全景起手；本卡是有先后的几站沿时间线横移、拉开收尾——先定关系再选卡。
- 与 `step-timeline-vertical◈` 的边界：那张是纯文字的竖向步骤时间轴；本卡每站是一张图。
- 与 layout.md 的接口：停靠上排照片离顶 ≥48（49.5）、caption 22px（停靠 23 / 拉开 13.6 ≈ 27@1080 最小可读边）、拉开时四张两侧 71；邻站出画是运镜语义，不算贴边。
- 剪辑软件对应物：剪映 / CapCut 把几张图和一条线合成后打"位置 + 缩放"多段关键帧，每站两个同值关键帧做 hold，压暗其余靠单独的亮度关键帧。素材站叫 "timeline photo strip"。
- 音效：每次横移起步一记 `pk:counter-clock-tick-single`（vol .4，clip ~0.9），拉开一记压低的 `pk:transition-air-whoosh-powerful`（vol ≤.3）；**hold 段绝对不给声**。

## 动效范围
- 属于本卡的：相机层 `origin 0 0` + `camTo` 反解到画心的横移停靠结构；"第一站 → 横移 power2.inOut → 真静止停靠 → 下一站 → 拉开看全条 → 有意停留 → 与字同收"的节拍（0.9 + 1.0 / 拉开 1.1 + 停 1.2）；当前站 1.03 点亮 + 其余 .7 的焦点处置；上下交替 + caption 靠线一侧 + 停靠 1.05 让邻站出画的几何。
- 不属于本卡的：demo 的示意图（演示语境素材，demos/_lib/media，不属于本卡）、"2019~2026"文案、时间线的颜色（#1d1d1f 可换）、白边卡的具体圆角 / 投影值。
- 迁移接口：`srcs` / `labels` 换素材文案；`hold` / `tailHold` 对齐口播；站数改 `centers`（+ `POS` / 时间线长度）；换画幅时几何按 960×540 等比缩放；竖屏改成竖向时间线（`camTo(z, 480, cy)` 纵向横移）。
- 底色要求：白底即可；深底风格档换深 tile 时时间线与 caption 换成浅色。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- **停靠居中**：每站 hold 中段截帧，当前站中心与画心 (480, 270) 偏差 ≤8px。
- **拉开装得下**：拉开帧四张两侧 ≥48（实测 71）；改站距后重解 `wideZ`。
- **hold 真静止 + 点亮到位**：hold 段相机 transform 逐帧相等；当前站已到 1.03 且亮 1。
- **邻站不贴边**：停靠帧邻站出画 ≥16（1.05 → 24），邻站 caption 被画幅切掉而不是离边 <48 悬着。
- **字号**：caption ≥22@960（拉开时 ≥13.6，缩到 390 宽复看仍可辨年份）。
- **有拉开 + 停留**：时间表末尾有拉开 + 停留，退场与本镜结束对齐。

<!-- ===== /file: video-talkcraft/references/cards/timeline-photo-strip.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/title-demote-to-label.md ===== -->

---
name: title-demote-to-label
标题: 标题降格成标签
一句话: 章节标题"第二步 · 拆解需求"56px 居中解糊显影（blur 12→0，0.4s）、站稳 0.7s，然后一条 power2.inOut 曲线 0.67s 同时完成"缩到 0.4 倍 + 飞到左上角 (80,72)"落成 22px 小节标签（居中修正量随补间同步归零）；降格进行到 0.4s 时三条内容块已开始在其下方按口播逐条生长（clip 从 35% 宽展开 + 上移 28px，0.55s 一条）——标题不消失，变成常驻路标；末条落定后静置 2.7s 同收
适用: 教程 / 方法论口播的小节交接（标题先当主角再让位给内容）、"第 N 点"结构（每点标题降格后留在左上角当路标直到下一点）、问答式（问题降格成标签、答案在下方展开）、与 chapter-progress-list 配合接进度条；内容 ≤4 条
时长: 5.9s（0.2 显影 → 0.6 站稳 → 1.3 降格 0.67s → 1.7 / 2.25 / 2.8 内容逐条生长 → 5.5 同收 0.4s）；成片按口播念到每条要点的时刻摆生长点，标题在念章节名时显影
能量: 中
类别: 字幕花字
输入: 文
语义: 章节, 步骤, 列举, 标题, 设问
素材形态: 无
位置: 中段
props: title, items, itemBg, accent
优先级: P0
代码: template/cards/title-demote-to-label.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 纯文字卡；人在场时整组（标签 + 内容）放人物对侧半幅，标签落点改到该半幅的栏线 | ✗ | ✗ 内容块也可换成图卡（同一生长动作），本卡 demo 只演文字 |

作用于章节标题 + 要点层，不作用于底部跟读字幕。

## 常用场景
1. 教程 / 方法论口播的小节交接："第二步 · 拆解需求"先当主角，再降格成路标，三条要点在下方逐条长出（demo 演的）
2. "第 N 点"结构：每点标题降格后留在左上角，直到下一点的标题再居中显影
3. 问答式：问题居中站稳 → 降格成标签 → 答案在下方展开
4. 与 `chapter-progress-list` 配合：降格后的标签接到进度条上当当前章

## 意图
`chapter-title-card` 是全屏色块压入 → 编号 + 章节名 → 扫出切回，标题**消失**；口播里"讲到第几点了"的路标需求很高频，观众走神回来要一眼看到"现在在讲哪一段"。本卡让标题**不消失**：先以 hero 尺度居中宣告一拍，再缩小飞到左上角变成常驻小节标签，内容在它下面长出来——一个元素完成"宣告 → 路标"两个角色。做对四条：
1. **降格是单次连续补间**：scale 与位置走同一条 inOut 曲线；分"先缩后飞"两段读作两个动作。
2. **显影后必须站稳 ≥18 帧再降格**：没站稳就缩，宣告拍被吃掉，观众没读完标题它就跑了。
3. **居中修正量随补间同步归零**：居中态靠 `translate(-50%, -50%)`，终点标签左对齐靶线——修正量 `-(1-d)×50%` 跟着 d 走，否则终点偏一个半宽。
4. **内容在降格进行到 12 帧时就开始长**：标题还在飞、内容已在长，交接无空档；等标题落位才长会空 8 帧冷场。

## 动效核心
- **几何**（960×540）：标题 56px / 700 墨色，居中位 `(480, 270)` 以 `translate(-50%, -50%)` 居中；标签落点 `(80, 72)`、`transform-origin 0% 50%`、缩放 0.4 → 22.4px（caption 档之上）。内容块 `left 80 / top 150 / width 800`：每条高 64、间距 22，26px 墨字 + 22px 内边距的淡色底板（layout §7 淡色系：蓝 `#E8F0FF` / 青 `#E6F7F2` / 黄 `#FFF4DC`，同组不重复），左侧 8×40 强调色竖条，`gap 18`。标签左边 = 内容块左边 = 栏线 x=80（标题边 160@1080）。标签底 83 到首条顶 150 间距 67 ≥ 32（§2）。
- **显影**：0.2s 起 0.4s `power3.out`，opacity 0 → 1、blur 12 → 0；站稳到 1.3s。
- **降格**：1.3s 起 0.67s `power2.inOut`，进度 d 同时驱动 `left/top = lerp(from, to, d)`、`scale = lerp(1, 0.4, d)`、`translate(-(1−d)×50%, −50%)`。
- **内容生长**：`growAt = 1.7`（降格起点 + 0.4），第 i 条在 `1.7 + i×0.55` 起 0.5s `power3.out`：`clip-path inset(0 65%→0 0 0)`（宽 0.35 → 1）+ y 28 → 0 + opacity 0 → 1。
- **退场**：`exitAt = 1.7 + 2×0.55 + 2.7 = 5.5`，标签 + 内容 opacity → 0 0.4s `power2.in`，5.9s 结束。落定即静置。
- 母本 B 式（登场时带"文本选中态高亮块扫入再撤"）是文字编辑类产品的身份暗示，口播不需要，不搬。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `stand` 站稳 | 0.7s（≥0.6）| 省掉这拍观众没读完标题它就跑了，降格白做 |
| `demote` | 0.67s（≈20 帧）power2.inOut | <0.47 读作标题被弹走；>1.0 观众在等 |
| `endScale` | 0.4（56 → 22px）| >0.45 标签太大压内容；<0.35 掉出 caption 可读档 |
| `to` 标签落点 | (80, 72) | 左边必须吸附内容块的栏线（§3 同组左边缘对齐）；y 太低压进内容 |
| `growDelay` | 0.4s（≈12 帧）| 交接无空档的量；0 则标题与内容同时动读作页面刷新，>0.67 空 8 帧冷场 |
| `stagger` | 0.55s / 条 | 按口播逐条；全部同时长出读作页面刷新而非"生长" |
| `clipFrom` / `rise` | 65% / 28px | 宽 0.35 → 1 是"长出来"的量；clip 归零就只剩淡入上浮 |
| 条目数 | 3（≤4）| 4 条 64 高 + 22 间距 = 322，top 150 起到 472 越过字幕带 y 450——4 条时 top 改 120 或条高 56 |
| 条目字号 | 26px@960 | ≥ 条目档下限 20@960（§5） |

## 已知坑
- 降格分两段（先缩后飞）——读作两个动作。
- 显影后不站稳直接降格——宣告拍被吃掉。
- 居中修正量不随补间归零——终点标签偏一个半宽，左边对不上内容块。
- 内容等标题落位才长——空 8 帧冷场；同时动——读作页面刷新。
- 标签落点没吸附内容块的栏线——两坨东西各自贴边（layout §2 间距倒挂）。
- 三条底板同色——读作三个一样的空框（§7）。
- 内容块比标签先出——路标还没立、内容先到，"让位"语义反了。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/title-demote-to-label.tsx——`title / items / itemBg / accent`；durationInFrames 189（3 条，条数变了按 `growAt + (n−1)×stagger + holdEnd + exitDur` 重算）。
- HTML/GSAP：demos/title-demote-to-label/index.html——改 `.tdl-ttl` 文案与 `.tdl-blk` 三条，`CONFIG.to` 改标签落点。
- 母本：video-shotcraft `title-demote-to-label` A 式（B 式选中高亮不搬）。
- 剪辑软件对应物：剪映文本层"缩放 + 位置"两条关键帧共用同一缓动（贝塞尔 ease-in-out），锚点设在文本左中；要点用"蒙版（矩形）+ 位置 + 不透明度"关键帧逐条做。AE：Anchor Point 左中 + Scale/Position 同一 easy-ease；要点用 Rectangle Mask Path 扩展。
- 与 layout.md 的接口：标签与内容块左边缘吸附同一栏线 x=80（§3）；组内间距 22 ≤ 组间距 67 ≤ 外边距 80（§2）；条目 ≥20px、底板淡色系不重复（§5 §7）；4 条时注意字幕带 y≥450（§6）。

## 动效范围
- 属于本卡的：hero 居中宣告 → 单次补间降格成左上标签的结构；站稳 ≥18 帧；居中修正随补间归零；内容在降格 +12 帧起错峰生长（clip 展开 + 上移）。
- 不属于本卡的：文案、底板色值、条目是文字还是图卡、标签落点在左上还是右上（人物在场时可镜像）。
- 迁移接口：`title / items / itemBg / accent`；1080p 输出字号 ×2（112 → 45 标签、52 条目）、落点 (160, 144)。
- 底色要求：白底 / 羊皮纸底成立；深底时底板换深 tile（`#272729` 系），竖条保持强调色。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- 定妆帧三张：站稳（1.0s，标题居中偏差 ≤48）、降格中（1.6s）、全部落定（3.6s）。
- 落定帧：标签左边 x 与内容块左边 x 相差 ≤4（吸附同一栏线）；标签字高 ≥14@960；标签底到首条顶 ≥32。
- 条目底板三色互不相同；条目字 ≥20@960；条目文字不越出自己的底板。
- 组包围盒（标签 + 内容）不入字幕带 y≥450；有人物在场时整组放人物对侧半幅。
- 末条落定后 ≥45 帧真静止。

<!-- ===== /file: video-talkcraft/references/cards/title-demote-to-label.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/tracking-in.md ===== -->

---
name: tracking-in
标题: 字距收拢
优先级: P1
代码: template/cards/tracking-in.tsx
一句话: 一行大标题的字距从 0.5em 极松收拢到 −0.03em，同一条 spring 同时把 9px 模糊解开——散开的字一边聚拢一边聚焦成一块，起手 0.3s 走掉 80%、剩下 0.5s 极慢地咬到位，全程零回弹
适用: 整屏让位给一句大标题的时刻——开场标题、章节论点、片尾落版、品牌短句（4~8 字）；需要"大片感/发布会气质"的单句；不适合多行文本、不适合常规字幕（这是标题动作不是字幕动作）
时长: 起手静置 0.3s → spring 收拢 + 解糊 1.0s（前 0.3s 走掉 80%）→ 淡入另走 0.5s 线性 → 收尾定格 1.3s；共约 2.6s
能量: 中
类别: 字幕花字
输入: 文
语义: 金句, 标题
素材形态: 无
位置: 任意
props: 无
---

## 意图
本库缺一档**标题的入场**——注意不是字幕。字幕的动作要短、要跟语速、要能连着上；
标题的动作可以长、可以只做一次、可以让整屏为它停下来。`chapter-title-card` 是"卡"（带色块压屏、有转场性质），
`quote-card` 是"多行金句 + 底板"，两张都自带一整套画面结构。这张卡只有**一行字**，
落在现有画面上，靠一个动作把整屏的注意力吸过去。

它的机制是唯一的：**字距（tracking）**。字从彼此隔得极远（0.5em ≈ 半个字宽的间隙）收拢到正常，
观众感知到的是"散落的东西正在归位"，而这个归位是横向的、对称的、从两端往中间的——
和本库任何一张字幕卡的运动方向都不重合。

命门两条：① **字距与模糊必须由同一条 spring 驱动**。字距在收、模糊在解，两件事共用一条曲线，
才会读作"一个动作"——散开的字聚拢成一块、同时聚焦成一块。分成两条缓动（哪怕参数很接近），
慢放下能看出字先咬到位再单独解糊，那就是两个动作了；
② **spring 是零回弹的长缓收**（damping 18 / stiffness 90，ζ=0.949）。
它的形状是"起手 0.3s 走掉 80%，剩下 0.5s 极慢地咬最后那 20%"——
最后那段极慢的咬合是这张卡全部的"贵气"来源。换成 `power2.out` 之类会明显更平；
换成弹性缓动（有回弹的 spring / `back.out`）字距会过冲到负值再弹回来，一眼廉价。

第三点值得注意：**淡入不跟 spring**（源码就是分开的两个 interpolate）。
opacity 走独立的 0.5s 线性——所以字在还只有一半透明度的时候，字距已经收掉 90% 了。
这个错位让"聚拢"这个动作在字完全显形之前就已经进行了大半，观众看到的是**结果的最后一段**，不是全过程。

## 动效核心
- **一条 spring 驱动两件事**（源码 `spring({config: {damping: 18, stiffness: 90}})`，mass 默认 1）：
  - `letter-spacing: 0.5em → −0.03em`（终态是**略收紧**，不是 0）
  - `filter: blur(9px) → 0`
  - 两者共用 spring 的输出 `t`，`interpolate(t, [0,1], [起, 终])` —— **一个动作**
- **spring 的形状**：ζ = `18 / (2√90)` = 0.949（欠阻尼），ω₀ = 9.487，ω₁ = 3.0。
  `x(t) = 1 − e^(−9t)·[3·sin(3t) + cos(3t)]`。
  x(0.3) = 0.800、x(0.5) = 0.966、x(1.0) = 1.00007 —— 过冲峰值只有 **8.1e-5**（t≈1.05s），肉眼是**零回弹**。
  实际走完约 **1.0s**（GSAP 里当自定义 ease 用：入参 0~1 的进度 × 1.0s 再喂进解析解）
- **淡入独立**：`opacity 0 → 1`，**0.5s 线性**，与 spring 无关（源码是第二个 `interpolate(frame,[0,15])`）。
  它比 spring 短一半 —— 字显形时字距已经收掉九成
- **`letter-spacing` 必须用 em 单位**：0.5em 是"半个字宽的间隙"，换字号自动等比。
  交给 GSAP 直接 tween 会被换算成 px，换字号后就不再等比 —— demo 里走代理对象 + `onUpdate` 手写样式
- **模糊量恒为字号的 1/8**（源码 12px @96px 字号；本库 72px ⇒ 9px）。比例常量，换字号必须等比改
- **`white-space: nowrap` 是硬要求**：0.5em 字距时整行比终态宽约 50%，
  不锁 nowrap 会在起手那一刻换行、收拢过程中再跳回一行
- **整行是一个元素**（不切字）：本卡的动画对象是"一行字"，字距是行的属性。
  切成单字再各自位移是另一条路（会失去 CSS 字距的对称性，且中文标点的位置会错）
- **零位移零缩放**：本卡不动 `transform`。所有的"运动感"都来自字距与模糊
- **层级**：舞台白底（源码显式 `background: white`——字距收拢靠"空"才读得出来）→ 整行（唯一被动画的元素）

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `startTracking` | 0.5em | 起始字距，本卡的能量旋钮；<0.25em 收拢幅度读不出来（退化成"有点糊的淡入"），>0.9em 起手时字散得认不出是一句话，且整行宽度接近画幅（中文尤其，字宽整齐、散开后是一排孤立方块） |
| `endTracking` | −0.03em | 终态字距，**略收紧不是 0**；0 收尾少了那一下"咬紧"，正值（放松）会让整行读作没收完 |
| spring 配置 | damping 18 / stiffness 90 | **本卡第二命门，零回弹的长缓收**；damping 调小（<14）出现可见回弹、字距过冲到负值再弹回，一眼廉价；stiffness 调大（>140）整个动作变短变硬、贵气消失 |
| `springDur` | 1.0s | spring 走完的实际时长（由 damping/stiffness 决定，不是独立参数——改配置就要重算）；本卡的"长"是刻意的，短于 0.7s 就不再是标题动作 |
| `startBlur` | 字号的 1/8（72px ⇒ 9px） | 起始模糊量，**比例常量**；0（不解糊）读作纯字距动画（机械，缺"聚焦成一块"那层），>字号 1/5 起手是一团雾、观众不知道要看什么 |
| `fadeDur` | 0.5s | 淡入时长 = spring 的一半，**这个错位是设计的一部分**；= `springDur` 则观众看到全过程（散开的字从头到尾都看得清，"归位"的惊喜感变成"等它排好"）；<0.3s 字几乎瞬间显形、又变成看全过程 |
| 字数 | 4~8 字 | 本卡的硬约束；≤3 字散开后是几个孤立的字、读不出"一句话"；≥10 字在 0.5em 字距下整行宽度超出画幅（中文按字号 × 字数 × 1.5 估算起手宽度） |
| `lead` | 0.3s | 起手静置等口播开口 |
| `hold` | 1.3s | 收尾定格——咬到位的大标题是本卡的落点；本卡是标题，定格可以给到 2s 以上 |
| 位移 / 缩放 | **0（不设）** | 本卡的硬约束：运动感全部来自字距与模糊，加位移就与 `per-character-rise` 撞车 |

## 已知坑
- 字距与模糊分成两条缓动——哪怕参数很接近，慢放下也能看出字先咬到位再单独解糊，"一个动作"变成两个；必须共用一条 spring。
- 换成有回弹的缓动（低 damping 的 spring / `back.out` / `elastic`）——字距过冲到负值（字互相压）再弹回来，一眼廉价，且中文字挤在一起那一帧非常难看。
- `letter-spacing` 用 px 单位（或交给 GSAP 自动 tween，它会换算成 px）——换字号后收拢幅度不再等比，大字号下"没散开"、小字号下"散得离谱"；必须走 em + `onUpdate` 手写样式。
- 终态字距写 0——收尾少了那一下"咬紧"的力道；源码是 −0.03em，这 0.03 是有用的。
- 整行不锁 `white-space: nowrap`——0.5em 字距时整行比终态宽 50%，起手那一刻会换行，收拢过程中再跳回一行（慢放下是明显的 bug）。
- 淡入跟着 spring 走满 1.0s——观众看到散开的字从头到尾都很清楚，"归位"的惊喜变成"等它排好队"；淡入必须比 spring 短一半。
- `startBlur` 写成绝对像素值跟着复用——换字号后大字糊不够、小字糊没了；必须按字号 1/8 等比。
- 用于多行文本——每行各自收拢，行与行的宽度变化不同步，整块读作在呼吸；本卡是**单行**标题动作（多行要点用 `line-by-line-slide`）。
- 用作常规字幕（连续几句都上这个）——1.0s 的动作跟不上语速，且每句都"归位一次"，整片显得慢；本卡一片里用 1~2 次。
- 字数超过 8（中文）——起手时整行宽度超出画幅，被 `overflow: hidden` 切掉两端，观众看到的是"两截字在往中间挤"。
- 底上有细密纹理——字在收拢的前半程是"半透明的糊块"，底上的细节透过来混在一起，读不出那是字。
- 起手那一帧整行的视觉中心比终态偏左约 `startTracking / 2`（CSS 的字距会在最后一个字后面也加一份，居中时把可见字形整体推向左）——**源码同样存在**，属于忠实搬运的一部分；真要消掉就给整行加 `margin-right: −<当前字距>`（跟着 `onUpdate` 一起改），但会与源码的观感有细微差别。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/tracking-in.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。props：无；文案「认知决定上限」在 JSX 常量里，换内容需改源码。
- HTML/GSAP：demos/tracking-in/index.html。**换内容只改 `#tiTitle` 的文案**（4~8 字，写在 HTML 里，
  本卡不切字所以没有内容数组）。能量只调 `startTracking`；换字号改 `.ti-title` 的 `font-size`，
  同时把 `CONFIG.startBlur` 改成新字号的 1/8（`startTracking` 是 em、自动等比，不用改）。
  `remotionSpring(damping, stiffness, mass)` 这个函数返回 Remotion `spring()` 的解析解，
  **可以直接抄到任何要复刻 Remotion spring 手感的 demo 里**（它同时带临界/过阻尼分支，改参数不会算错）；
  改了 spring 配置就要重算 `springDur`（跑 `SPRING(t)` 找 x(t) 稳定到 1 的时刻）。
  整行的落位改 `.ti-frame` 的 flex 对齐（demo 是整屏居中，因为本卡就是"整屏让位"的语义）。
- Remotion 移植：template/cards/tracking-in.tsx 已是最简形态（`remotionSpring(18, 90, 1)` 解析解同时喂 `letterSpacing` 与 `blur`，opacity 另走 0.5s 线性）；用 Remotion 原生 API 的等价写法：
  一个 `spring({frame, fps, config: {damping: 18, stiffness: 90}})` 喂两个 `interpolate`
  （字距 `[0,1] → [0.5, -0.03]` 输出 em 字符串、模糊 `[0,1] → [12, 0]`），
  opacity 另走 `interpolate(frame, [0, 15], [0, 1], {extrapolate: "clamp"})`。
  **帧↔秒换算（源码 30fps）**：opacity 的 `[0, 15]` ⇒ 0.5s；spring 没有显式帧数，
  由 damping/stiffness 决定实际时长（本配置 ≈ 30 帧 = 1.0s），`durationInFrames 90` ⇒ 3.0s（含定格）。
  尺寸换算：源码 `fontSize 96` @1280 画幅，本库 960 舞台 ×0.75 ⇒ 72，`startBlur 12 ⇒ 9`；
  `startTracking` 是 em，跨尺寸不用换算。
- 剪辑软件对应物：剪映/CapCut——**字距不是可打关键帧的属性**（剪映的"字间距"是静态滑杆），
  所以做不出本卡；能做的最近替代是把标题拆成单字文本层各自做横向位移（成本高，且失去 CSS 字距的对称性）。
  想要现成的就换 `soft-blur-in`（解糊淡入，剪映能做）。
  AE——`Source Text` 的 `Tracking` **是可以打关键帧的**（Animator 或图层的 Tracking 属性），
  两个关键帧（起 50 → 终 −3，AE 的 Tracking 单位是 1/1000 em，所以 0.5em = 500、−0.03em = −30）+
  `Fast Box Blur`（9 → 0）+ `Opacity`（0 → 100，只 15 帧）；
  **Tracking 与 Blur 的两条曲线必须完全一致**（在 Graph Editor 里复制粘贴曲线，别各自 Easy Ease）；
  要精确复刻 spring 的形状就用表达式：把上面那条 `x(t) = 1 − e^(−9t)(3sin3t + cos3t)` 写进
  Tracking 与 Blurriness 的表达式里（同一个 `t = time - inPoint`），比手拉曲线准。
- 与本库同类卡的分工：`chapter-title-card` = 章节卡（色块压屏 + 编号，带转场性质，是画面结构的切换）；
  `quote-card` = 多行金句大字卡（底板 + 人物让位 + 整卡退场）；
  `behind-text-title` = 标题穿在人物身后（层级把戏，人照常出镜）；
  `soft-blur-in` / `per-character-rise` = 单句**字幕**入场（能跟语速、能连着上）；
  **本卡 = 单行大标题的一次性入场**（不带底板、不切画面、不跟语速，靠字距归位吸走整屏注意力）。
  本卡与 `chapter-title-card` 的分界是**要不要切画面**：要色块压屏的章节切分用后者，
  只要一行字立在当前画面上用本卡。本卡一片里用 1~2 次（开场 + 落版），用多了"贵气"就贱了。

## 动效范围
- 属于本卡的：`letter-spacing 0.5em → −0.03em` 与 `blur → 0` 由**同一条 spring** 驱动这个机制（一个动作而不是两个）；spring 配置 damping 18 / stiffness 90（ζ=0.949，过冲 8e-5，**零回弹的长缓收**：0.3s 走掉 80%、剩 0.5s 咬合）；起始模糊量恒为**字号的 1/8**；终态字距 −0.03em（略收紧而非归零）这一下咬紧；淡入**独立于 spring** 且只有它一半时长（0.5s 线性）这个错位；`letter-spacing` 必须走 em 单位这条实现纪律；整行作为**单个元素**（不切字）与 `nowrap`；**零位移零缩放**这条硬约束；"字数 4~8"这个上限。
- 不属于本卡的：demo 那句「认知决定上限」的具体文案、72px 字号与 700 字重、`#171717` 这个墨色、无衬线字族的选择、白底舞台（源码显式白底，但深底把字色反白同样成立）、以及"整屏居中、不放主持人"这个落位——demo 不放主持人是因为本卡的语义就是"整屏让位给一句标题"，应用侧要让人物留在画面里也成立（标题落在人物上方或下方的留白区，只要那一带足够空）。
- 迁移接口：标题文案直接写在 HTML 里（4~8 字）；能量只调 `startTracking`（em，跨尺寸不用改）；`startBlur` 按字号 1/8 等比缩放；**spring 配置、`endTracking`、`fadeDur` 与 `springDur` 的比例是手感常量，换尺寸换语速都不要动**（改了 spring 配置必须重算 `springDur`）；`hold` 可以给到 2s 以上（本卡是标题不是字幕）；竖屏用 4~6 字并把字号收到 46~56px（起手宽度 ≈ 字号 × 字数 × 1.5，必须小于可用宽度的 90%，否则两端被切）。
- 底色要求：白底最佳（源码显式白底——**字距收拢靠"空"才读得出来**：字周围要有足够的空白，观众才能看见"间隙在变小"这件事）。深底把字色反白同样成立。硬约束两条：① 底不能有细密纹理或高频细节（收拢前半程字是半透明糊块，细节透过来就读不出字）；② 底不能有横向条纹或横向渐变（字距收拢是横向运动，带方向的横向底纹会与它产生视差错觉）。渐变底可以，实拍花底不行（本卡不自带背板，也不适合加描边——描边会把 0.5em 的间隙填得更满、削弱"散开"的读感）。

<!-- ===== /file: video-talkcraft/references/cards/tracking-in.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/type-contrast-emphasis.md ===== -->

---
name: type-contrast-emphasis
标题: 字体对比重音
优先级: P0
代码: template/cards/type-contrast-emphasis.tsx
一句话: 字幕逐词追加、普通词一律无衬线小字轻 pop，念到重音词的瞬间该词换成衬线斜体放大 1.5~2 倍（或换唯一强调色），强调完全靠字体气质的落差砸出来，运动本身刻意做轻、不弹不过冲
适用: 每段口播的判断句/反转句/结论词——尤其"不是 A，是 B"这种对照句式；克制、有编辑气质的知识区与个人观点口播，想要重音但不想要综艺弹跳的调性
时长: 普通词轻 pop 0.1s（scale 0.95→1 无回弹）；重音词入场 0.15s（上滑 + 轻放大淡入）；词间距抄真实语速（0.2~0.7s 不等）；一句 5 词约 2s，追加式全句完成后定格
能量: 低
类别: 字幕花字
输入: 人(可选), 文
语义: 对比, 转折, 强调
素材形态: 无
位置: 任意
props: hostSrc
---

## 意图
逐词弹跳字幕靠"动得更大"做重音，代价是整句都在跳、看久了廉价。字体对比走另一条路：
**重音靠字形气质的落差，不靠缩放弹跳**——普通词是无衬线中字的"叙述声"，重音词切成
衬线斜体大字的"引用声"，两种声音一同屏，观众耳朵还没反应过来眼睛已经知道哪个词是重点。
命门：**落差要够大**（字号 1.5~2 倍 + 换字族，只放大不换族读作缩放素材、只换族不放大
远看分不出）、**运动要够轻**（0.15s 上滑淡入，加了回弹就退化成弹跳字幕，两种语言混用一眼假）、
**一句只有一个重音**（两个衬线大字互相打架，等于没有重音）。

## 动效核心
- 整句按最终排版预占位：所有词先建 DOM、`opacity: 0` 占住位置，逐词追加时不回流
- **所有词共一条基线**（容器 `align-items: baseline`）：重音词的大字从共同基线往上长，
  基线一动整句就散——这是本卡唯一的排版硬约束
- 普通词：无衬线、字重 600、基准字号；入场 `opacity 0→1` + `scale 0.95→1`，0.1s `power2.out`，
  `transform-origin: 50% 100%`（锚在基线，轻 pop 不推基线）。无回弹
- 重音词 · 通道① 字形：切衬线族（Songti/STSong/Source Han Serif，西文 Georgia/Playfair）+
  字号 ×1.5~2；中文没有真斜体，用 `skewX(-6~-10°)` 显式倾斜（各端一致，不靠合成斜体）
- 重音词 · 通道② 色彩：字族不变，换全片唯一强调色 + 字重 800 + 字号 ×1.4~1.6
- 重音词入场：`y +14px→0` 从基线下方上滑回落，同帧 `scale 0.92→1` + 淡入，0.15s `power3.out`——
  "顶上来"落定，不过冲
- 两个通道是**替代关系**（同一个词二选一），不叠用：衬线斜体 + 强调色 + 放大三件套一起上读作贴纸花字
- 保留模式只有**追加式**（已说的词保留，全句完成后定格，适合对照句式）；tsx 的 `CONFIG.mode` 虽声明了 `"relay"` 但渲染逻辑未读取它，接力式（只留当前词、前词硬切）需自行实现
- 层级：重音词可单独一行、压在素材或人物上——大字加白描边即可，其余词留在字幕行

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `--tc-base` | 30~34px（960 宽） | 普通词基准字号，重音词字号由它派生；改这一个数就等比换尺寸 |
| `--tc-serif-scale` | 1.6 | 衬线重音词放大倍数；<1.4 远看分不出层级、强调失效；>2.1 一个词吃掉半行、整句读不成句 |
| `--tc-color-scale` | 1.5 | 换色重音词放大倍数；有颜色帮忙可比字形通道略收，1.3~1.6 都成立 |
| `obliqueDeg` | −7° | 中文斜体的显式倾斜角；0 则衬线大字读作"标题"而非"重音"，<−12° 开始读作贴歪的贴纸 |
| `accentIn` | 0.15s | 重音词入场；>0.3s 读作 PPT 入场，<0.08s 看不清是"顶上来"的 |
| `accentRise` | 14px（≈字号 30%） | 上滑距离；0 则只剩淡入没有"顶上来"的劲，>字号 60% 读作从下一行飞进来 |
| `wordIn` | 0.10s | 普通词轻 pop；>0.2s 跟不上语速，整句铺不完 |
| `wordFromScale` | 0.95 | 普通词起始倍数；<0.85 或换成 `back.out` 立刻退化成弹跳字幕，本卡的克制感就没了 |
| `beat` 间距 | 0.2~0.7s 不等 | 词级语音时刻，抄 forced-alignment 直出；匀速排布立刻跑马灯 |

## 已知坑
- 只放大不换字族——纯缩放读作"素材被拉大"，不是重音；字体对比这张卡的本体就是**换族**。
- 只换字族不放大——白底小字上衬线/无衬线的差别远看几乎为零，静音刷视频抓不到重点。
- 重音词加 `back.out`/`elastic` 回弹——退化成 keyword-pop-highlight 的语言，气质对比与弹跳强调混用一眼假；本卡的重音必须"稳稳顶上来"。
- 中文重音词直接写 `font-style: italic`——多数中文字族没有斜体字形，浏览器合成斜体在各端形态不一致（甚至无效）；必须 `skewX` 显式倾斜。
- 各词没有共同基线（用 `align-items: center` 或让大字自己撑行高）——大字一来整行上下乱跳，观众读作排版 bug。
- 重音词左右不留外边距——倾斜后的衬线大字右上角外探，会压住相邻字；至少留 4px（或 0.15em）。
- 一句里两个以上重音词都上衬线大字——重音互相打架，等于没有重音（两个通道分给两个词也算两个重音）。
- 强调色不止一个——本卡的色彩通道必须复用全片唯一 accent，多一个颜色就成花字。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/type-contrast-emphasis.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。props：仅 `hostSrc`；分词 / 词级时刻 / 通道标记在 `CONFIG.words` 里，换内容需改源码。
- 与 keyword-pop-highlight 的分工：那张卡的重音要"砸"（scale 1.65 过冲 + 色块 + 整屏震动），本卡的重音要"稳"（字形气质落差 + 0.15s 轻上滑，不过冲）。同一句里**只能选一张**——回弹强调与气质对比同屏混用一眼假；同一片子里可按段落调性分用（高能段落走 keyword-pop-highlight，判断句/结论句走本卡）。见 references/cards/keyword-pop-highlight.md。
- HTML/GSAP：demos/type-contrast-emphasis/index.html。换文案改 `CONFIG.words`（`w` 分词 + `beat` 词级语音时刻 + `emph: "serif" | "color"` 指定通道，不填即普通词）；换尺寸只改 CSS 变量 `--tc-base`；落差量级在 `--tc-serif-scale` / `--tc-color-scale`；强调色在 `.tc-word.emph-color` 的 `color`；手感在 `accentIn` / `accentRise` / `obliqueDeg`。核心可摘走部分 = `CONFIG` + `DemoShell.register` 回调内部。
- Remotion 移植：普通词 `opacity: interpolate(frame, [b, b+3], [0, 1])` + `scale: interpolate(frame, [b, b+3], [0.95, 1])`（b = 该词语音帧，`extrapolate*: 'clamp'`，`transformOrigin: '50% 100%'`）；重音词同区间取 `[b, b+5]`，`y: interpolate(..., [14, 0], {easing: Easing.out(Easing.cubic)})` + `scale [0.92, 1]`，`transform` 里把 `skewX(-7deg)` 写成静态项（别让它参与插值）；字族/字号落差全在 style 常量里，不进插值；`beat` 由 whisper/forced-alignment 词级时间戳换算帧直接填入。
- 剪辑软件对应物：剪映/CapCut——把重音词拆成独立文本轨，字体换成"宋体/思源宋体"并开倾斜、字号调到 1.5~2 倍，入场用"渐显 + 向上滑入"（关掉所有弹跳/花字预设）；AE——同一段文字用两个 Text Animator（一个 Range Selector 只作用普通词做 scale 0.95→1，一个只作用重音词做 Position + Scale），字族落差用 Source Text 关键帧或直接分层，倾斜用 Skew 属性；剪映的"文字模板"类预设一律不能用（自带弹跳与花字，破坏本卡的克制感）。

## 动效范围
- 属于本卡的：逐词追加的入场时序（词级语音时刻驱动，间距不均匀）；普通词轻 pop（opacity 0→1 + scale 0.95→1、0.1s、power2.out、origin 锚基线、**无回弹**）；重音词入场（y +14px→0 上滑回落 + scale 0.92→1 + 淡入、0.15s、power3.out、不过冲）；重音词的两个替代通道（① 换衬线族 + skewX 显式倾斜 + 字号 ×1.5~2；② 换唯一强调色 + 字号 ×1.4~1.6）与"二选一不叠用"的纪律；整句共一条基线且预占位不回流；一句只有一个重音；追加式保留模式。
- 不属于本卡的：主持人占位（数字人）、示例台词与分词、字幕落在右侧白区这个位置、`--tc-base` 32px 这个具体字号、宋体/PingFang 这两个具体字族（本卡要的是"衬线 vs 无衬线"的落差，不是某个字体）、`#0066cc` 这个具体强调色值、`#1d1d1f` 这个字色。
- 迁移接口：`beat` 换成目标音轨的词级时间戳；`--tc-base` 一个数等比换尺寸（`accentRise` 按字号 30% 同步缩放）；字族落差换成目标风格里的"正文族 / 引用族"一对（衬线↔无衬线、常规↔重型手写皆可，只要气质差异在缩略图尺寸下可辨）；色彩通道的 `color` 换成该项目的唯一 accent；深底或实拍花底把字色反过来（普通词白、重音词 accent）并给重音大字加 2~3px 描边保可读。
- 底色要求：白底即可（字形/字号落差与底色无关，是本卡最容易迁移的性质）。唯一硬要求是"普通词与重音词的对比同时成立"——花底上需给重音大字补描边，别让强调色掉进背景明度里。

<!-- ===== /file: video-talkcraft/references/cards/type-contrast-emphasis.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/typewriter-reveal.md ===== -->

---
name: typewriter-reveal
标题: 打字机档案戳
一句话: 等宽字体逐字符敲出时间地点戳，速度带随机抖动，末尾方块光标以 500ms 周期闪烁，句尾闪 3 次后副信息行再延迟 0.4s 跟进
适用: 纪录片式口播交代时间/地点/人物档案的时刻；悬疑、调查、盘点类调性；不适合高能快剪段落
时长: 主行约 0.8~1.2s 敲完（14 字左右），句尾闪 3 次 1.5s，副行再 1s；全套约 4s
能量: 低
类别: 字幕花字
输入: 人(可选), 文
语义: 时间地点
素材形态: 无
位置: 任意
props: hostSrc
优先级: P1
代码: template/cards/typewriter-reveal.tsx
---

## 意图
给叙事一个"档案调取中"的仪式感——观众看到逐字敲出的地点日期，会自动进入"接下来是背景资料"的收听模式。
命门：**速度要抖**（每字符 30~80ms 且 ±20ms 随机，匀速立刻变 CSS 教程）、
**光标必须在**（方块光标是"打字机"的身份证，没有它只是延迟出字）、
**两行要错峰**（副信息晚 0.4s 再敲，同时敲两行就没有"逐条录入"的档案感）。

常见于：Johnny Harris、LEMMiNO、Fireship（代码版）、James Jani。

## 动效核心
- 文本容器用等宽字体（Menlo/Consolas；中文字符天然等宽，混排数字必须等宽），行尾跟一个 `█` 方块光标（宽 0.62em、高 1.05em 的实心块）
- 逐字符出现：第 n 个字符在 `Σ(charMs ± jitterMs)` 时刻整字显示（不是淡入），30~80ms/字符
- 句尾：光标以 500ms 周期方波闪烁（半周期亮/半周期灭，不是渐隐）2~3 次
- 句尾闪完 3 次后再隔 0.4s（`line2Delay`）第二行开始敲，光标从第一行"移交"到第二行（第一行光标消失）
- 敲完后光标常驻闪烁
- 层级：底 → 出镜人物/素材（照片/B-roll）→ 打字戳（最上，落在人物对侧的留白区，占角落不占中央）

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 字符间隔 charMs | 55ms | 调小到 30ms 像高速电传，紧张感强；调大过 100ms 观众开始等，像 loading |
| 随机抖动 jitterMs | ±20ms | 0 = 匀速一眼假；抖太大（±40ms+）像网卡 |
| 光标闪烁周期 | 500ms | 行业默认；调快像故障，调慢像死机 |
| 句尾闪烁次数 | 3 | 少于 2 次副行接得太急；多于 4 次拖节奏 |
| 副行延迟 line2Delay | 0.4s（相对句尾闪烁结束） | 调大更有"调档案"的停顿感；为 0 时副行紧接闪烁结束就敲，少了"翻到下一条"的停顿 |
| 主行字号 | 36px（960 宽舞台；副行 18px） | 太大像标题卡抢戏；这是"戳"，应该占角落不占中央 |

## 已知坑
- 匀速出字——真打字有节奏波动，匀速的规整感一眼是 `setInterval` 教程代码。
- 没有方块光标——只剩"文字慢慢出现"，读作加载慢而不是打字机。
- 非等宽字体混排数字——字符宽度不一，光标随出字左右跳动，档案感全毁。
- 光标用透明度渐隐渐显——打字机光标是方波（亮/灭硬切），正弦呼吸感是网页登录框。
- 把戳放在画面正中——它是标注不是标题，居中就抢了素材的戏。
- 字符间距跳动的另一条补救：字体做不到等宽时，用 `ch` 单位给每个字符定宽，光标位置同样能锁住。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/typewriter-reveal.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。props：仅 `hostSrc`；文案 `line1` / `line2` 在 CONFIG 里，换内容需改源码。
- HTML/GSAP：demos/typewriter-reveal/index.html。demo 带口播语境：主持人（数字人）占左侧 40% 出镜，档案戳排在右侧白区下方——戳是标注，不压人物、不占中央。改 `CONFIG.line1/line2` 换文案，`charMs/jitterMs` 调手感；`.host-wrap` 与 `.host-placeholder` 只是演示语境（真人出镜位），应用侧换成实拍/数字人图层即可；`.stamp` 的 `left/bottom` 就是落位接口（人在左则戳在右，反之对调）；"档案感"（深底/做旧/纸纹）属于风格层，自己按片子调性加。
- Remotion 移植：按帧取 substring——`text.slice(0, charAt(frame))`，其中 charAt 用预生成的随机时刻表（useMemo 固定 seed）；光标 `opacity = Math.floor(frame / (fps*0.25)) % 2`。
- （实测变体）乱码 decode：命令/术语先在一枚胶囊里以乱码高速滚动，再**逐位从左到右锁定**为真字符——身份从"打字机"换成"解码中"，适合抛出命令行、模型名、密钥类字符串；方块光标可省，锁定的进度本身就是光标。见 TheAIScaler（u8OWXXTcu3Q）。
- （实测变体）终端窗口实时打字（Y17upxADWXs / HidOB0Ll7W8）：把打字戳放进一个终端窗口壳里，敲完回车后输出行整块出现（不逐字）——"输入逐字、输出整块"是终端的真实节奏，输出也逐字反而假。
- 剪辑软件对应物：剪映"文字动画→输入法/打字机"；AE 用 Text Animator + Opacity 100% 阶梯；CapCut "Typewriter" 预设——注意都要手动补方块光标层。

## 动效范围
- 属于本卡的：逐字符整字显示（不淡入），第 n 字符出现在 `Σ(charMs ± jitterMs)` 时刻——**间隔带随机抖动**是本卡的核心手感；句尾方块光标 500ms 周期方波闪烁（亮/灭硬切，非渐隐）2~3 次；光标从主行"移交"副行（主行光标 display:none、副行同帧点亮）；副信息行延迟 0.4s 再敲的错峰时序；敲完光标常驻闪烁。等宽字体是本卡的必要条件（非等宽会让光标随出字左右跳动）。
- 不属于本卡的：演示里的口播语境（左侧数字人出镜位 `.host-wrap`/`.host-placeholder`——由 demo-shell 统一注入，见 references/host-footage.md）、示例文案（北京 · 2008…）、字号 36px/18px 与戳的具体落位（右侧白区下方）、"档案感"的一切风格化——深底、做旧、纸纹、暗角、字投影都属于风格层，本卡不提供也不要求。
- 迁移接口：`charMs`/`jitterMs` 定打字速度与抖动量，`blinkPeriod`/`blinkTimes` 定光标节律，`line2Delay` 定两行错峰，`startDelay` 对齐语音入点；换风格改 `.stamp` 的 color 与光标 background（光标色必须跟字色同色，否则不像同一台打字机）；换尺寸时字号与光标的 0.62em×1.05em 保持 em 相对值即可自动跟随。
- 底色要求：白底即可（逐字符显示与方块光标不依赖底色对比，只需字色与底色可读）。原 demo 的深色档案底已移除——那是风格不是动效。

<!-- ===== /file: video-talkcraft/references/cards/typewriter-reveal.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/ui-flow-theater.md ===== -->

---
name: ui-flow-theater
标题: 界面流程剧场
优先级: P0
代码: template/cards/ui-flow-theater.tsx
一句话: 整套灰阶假设置面板按一条 STEPS 时刻表自演一遍完整流程——光标走位（路点弧线 + 按压涟漪）与控件换态（开关滑、分段切、滑杆拖、按钮转成功）共享同一批 at 常量同拍发生，最后一记成功 toast 滑入收尾：不是"贴一段录屏"，是界面按脚本演给你看
适用: 口播讲"这个产品/功能怎么用"的完整流程段落——"进设置把这个打开、主题换成深色、音量拉到七成、保存"；工具测评、SaaS/AI 产品讲解、教程与上手引导类口播；真录屏拿不到（产品未上线/要脱敏/流程太长）时的唯一不穿帮做法
时长: 入场整卡揭示 0.6s + 区块错峰 5×0.2s → 每拍 = 移动 0.4~0.62s + 悬停 0.2s + 按压 0.09s + 换态 0.27s ≈ 1s/拍；4 拍 + toast（滑入 0.47s + 停 1.8s）共 8~9s
能量: 中
类别: 素材呈现
输入: 界
语义: 过程演示, 步骤
素材形态: 界面
位置: 中段
props: 无
---

## 意图
口播讲"这个产品怎么用"时有三条常见路：录屏（光标 12px 看不见、节奏由手速决定、要脱敏就废了）、
截图硬切（丢掉"这一步导致了那一步"的因果）、逐个控件做动效（每个控件各自一条时间线，
排到第三个就对不上拍了）。界面流程剧场是第四条：**把整套界面当一个演员，给它一份剧本**。
剧本就是一张 `STEPS` 表，一行一拍；光标读它决定什么时候走到哪、什么时候按下，
控件读**同一张表的同一个 `at`** 决定什么时候换态。观众看到的是"手点下去 → 这个控件当场变了 →
手走到下一个"，因果链一节不断，而制作者只维护一张表。
命门：**时间只从一处进入**（`at` 是唯一的时间源，光标与控件都是它的函数，对齐靠共享常量不靠两处手数）、
**坐标是命名常量**（控件落点运行时反算成 `POS.xxx`，光标路点只引用名字，换布局不用改数字）、
**一个控件一种响应**（每个控件一个响应函数，函数内部没有时间参数）。
这三条不是代码风格，是这张卡能排到 4 拍以上还不散架的全部原因。
定位：本卡是「界面剧场」子类（整套界面按脚本自演）的**架构母卡**，讲完整流程；同源卡 terminal-typing-log / chat-gpt / claude-code / glass-code-walk / cursor-actor-demo 共用该子类的共有纪律。

## 动效核心
- **STEPS 时刻表（本卡的骨架）**：`[{ at, target, act, move, until }]`——
  `at` 是这一拍**按下**的时刻，`target` 指向 `POS` 里的命名坐标与 `RESPOND` 里的响应函数，
  `act` 是 `click` / `drag`，`until` 只有拖拽拍才有（松手时刻）。
  demo 四拍：2.10 开关 → 3.10 分段 → 4.05~4.95 滑杆 → 5.90 保存。**约 1s/拍**（一拍一个口播短句）
- **命名坐标常量（必抄）**：控件落点存成 `POS = { sw, seg, sld, sldEnd, save }`；光标路点、涟漪圆心、拖拽终点全部引用这些名字，
  **源码里绝不出现第二遍坐标数字**。HTML demo 在建时间线前用 `P(el, fx, fy)` / `getBoundingClientRect` 运行时反算一次（换画幅/换布局/改字号都不用改数字）；
  tsx 版把 demo 实测值照抄成常量（`POS` 写死，换布局须重量）
- **入场（先给全景，再动手）**：整卡 `blur 9→0` + 淡入 0.6s `power2.out`，随后卡内区块
  **每 0.2s 错峰一个**、各自 `blur 5→0` + `y 8→0` 0.53s。区块 = 标题 / 开关行 / 分段行 / 滑杆行 / 按钮行。
  光标起步时刻由首拍 `at` 反推（`at − hoverHold − moveLong` = 1.28s），而末两块区块要到 1.73s / 1.93s 才落定——demo 里两者重叠约 0.65s；要做到"区块全部落定后才动手"，首拍 `at` 需 ≥ `cardIn + 4×blkStep + blkIn + hoverHold + moveLong` ≈ 2.75s（或减小 `blkStep`）
- **光标走位**：与 `cursor-actor-demo◆` 同一套移动语言——x `power2.inOut` + y `sine.inOut`
  分开插值合成弧线，跨区域 0.62s / 相邻控件 0.40s；到位后停 `hoverHold` 0.2s 才按下。
  **移动的结束时刻由 `at` 反推**（`start = at - hoverHold - dur`）——所以改一拍的 `at`，
  移动、悬停、按压、换态四件事整体跟着挪，不用逐个改
- **按压**：光标 `scale 1→0.9→1` 各 0.09s（锚 `transform-origin: 0% 0%` 在箭头尖）+
  从箭头尖扩散的涟漪（`scale 0.3→1.6` / `opacity 1→0`，0.35s）。
  **换态发生在按下中点**（`at + press*0.55`），不等抬手
- **拖拽拍的特殊纪律**：`hold()` 只下压不回弹（按住不放），松手时才回弹；
  **被拖控件的值必须与光标 x 用同一个缓动**（都是 `power2.inOut`）——
  两边缓动不同，拖到中段箭头尖就飘出手柄外，"抓住了"当场破产
- **四种控件响应（一个控件一种，别混）**：
  ① 开关：滑块 `x 0→20px` 0.27s `power2.out` + 轨道转深 + 滑块转白
  ② 分段选择：指示器 `x` 滑一格（`x = 指示器自身宽度`，**只动 x 不动宽度**）+ 两个标签同拍换色
  ③ 滑杆：按下先给手柄 `scale 1.12` + 描边加深，值在拖拽段里跟手——
     填充宽度 / 手柄位置 / 百分比读数**共用同一个代理值**（`onUpdate` 里一起写）
  ④ 按钮：按压微缩 → 底色转语义色 + **label 与勾交叉淡化**（label 留在正常流撑住宽度、
     勾绝对定位覆盖，两者只驱动 opacity）——按钮框绝不跳
- **换态时长全库统一 0.27s `power2.out`**（press 态只给一半）——四个控件同一个数，
  界面才读作"一套"；每个控件各调一个时长，会读成四个独立小动画拼在一起
- **成功 toast 收尾**：最后一次按下后 0.33s 起，`y 16→0` + `scale 0.97→1` + 淡入 0.47s `power3.out`
  （`transform-origin: bottom center`），停 1.8s 后 0.47s 退。**它是全卡唯一的语义色**（和保存按钮那一拍共用）
- **层级**：底 UI < 控件状态层 < toast（z 20）< 涟漪（z 29）< 光标（z 30）。光标永远在最顶

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `STEPS[].at` | 2.10 / 3.10 / 4.05 / 5.90 | 每拍按下的时刻，全卡唯一的时间源；一拍一个口播短句，间隔 <0.6s 退化成加速录屏、>1.5s 画面在等语音 |
| `cardIn` / `cardBlur` | 0.60s / 9px | 整卡揭示；`cardBlur` >14px 揭示瞬间像隔了层毛玻璃，<5px 看不出"揭示"（读作普通淡入） |
| `blkStep` | 0.20s | 区块错峰步长；0 则五个区块同帧砸上来（一眼是贴图），>0.35s 观众等着面板长完 |
| `blkIn` / `blkBlur` / `blkLift` | 0.53s / 5px / 8px | 单区块揭示；`blkLift` >16px 每行都在飞、抢掉后面的操作戏 |
| `moveLong` / `moveShort` | 0.62s / 0.40s | 跨区域 / 相邻控件移动；<0.25s 读作瞬移，>0.9s 口播已经说到下一句 |
| `hoverHold` | 0.20s | 到位到按下的微停顿；0 则读作程序自动点击，>0.5s 像光标卡住 |
| `press` / `pressScale` | 0.09s / 0.9 | 按压时长（抬手同值）/ 微缩倍数；`pressScale` <0.8 像箭头被吸进屏幕 |
| `ripple` / `rippleFrom` / `rippleTo` | 0.35s / 0.3 / 1.6 | 涟漪扩散；`rippleTo` >2 圆环比控件还大、抢戏 |
| `swap` | 0.27s | **所有控件的换态时长**（唯一一个数）；<0.15s 看不清状态变了，>0.45s 控件变成主角 |
| `dragEase` | `power2.inOut` | 拖拽段缓动，**必须与光标 x 的缓动一致**；不一致时手柄会脱离箭头尖 |
| 拖拽段长（`until - at`） | 0.90s | 拖行程耗时；<0.4s 看不出"被拖过去"（读作换图），>1.4s 观众等不动 |
| `sldFrom` / `sldTo` | 28% / 76% | 滑杆起止值；行程 <25% 看不出被拖动，起点 0 或终点 100 显得像"拉满/清零"另一件事 |
| `toastIn` / `toastHold` / `toastOut` | 0.47s / 1.8s / 0.47s | toast 三段；`toastHold` <1s 观众读不完，>3s 画面停死 |
| `toastLift` | 16px | toast 滑入位移；>28px 像从屏外飞进来（抢掉刚才那一记点击的收尾） |

## 已知坑
- 光标一条时间线、控件各一条时间线，靠手数时间对齐——排到第三拍必然错开，且改任何一拍要改两处。
  本卡的全部架构价值就在"共享同一批 `at`"这一条；两套时间源是这类卡最常见的死法。
- 控件坐标在光标路点里手写一遍、在 CSS 里再写一遍——改布局漏改一处，光标就点在空气上。必须运行时反算成命名常量。
- 界面还在入场（区块在错峰揭示）时光标就开始走——两段动画叠在一起，观众不知道该看入场还是看操作（demo 首拍 at=2.10 未满足：光标 1.28s 起步、末块区块 1.93s 才落定，重叠约 0.65s）。
- 四个控件各用一个换态时长——读成四个独立小动画拼盘，界面不像"一套"。全卡一个 `swap`。
- 拖拽时手柄与光标缓动不同（一个 `power1`、一个 `power2`）——拖到中段箭头尖飘在手柄外，"抓住了"当场破产。
- 拖拽的按压做成"下压又回弹"——那是点击不是按住；按住不放必须只下压、到松手才回弹。
- 滑杆拖完才刷新百分比读数——观众读作"贴了张图然后换了个数"；填充 / 手柄 / 读数必须共用一个代理值。
- 分段选择的指示器用改宽度或改 `left` 实现——每帧重排会带着标签抖；只动 `transform: x`。
- 按钮成功态换文案不做交叉淡化（直接换 innerText）——按钮宽度当场跳一下，最该稳的收尾拍在抖。
  必须 label 留在正常流撑宽度、勾绝对定位覆盖，两者只驱动 opacity。
- 语义色上到多个控件（开关也红、分段也红、按钮也红）——一屏三个重点等于没有重点。
  全卡只有"保存成功"那一拍有色（按钮底 + toast 图标）。
- toast 紧贴最后一次点击同帧滑入——读作"点击自带一个弹窗特效"；隔 0.3s 左右才有"系统回应你"的因果。
- 给假 UI 加拟真质感（渐变按钮/内阴影/玻璃/多层投影）——界面变成主角，抢掉讲述；灰阶线框足够。
- 一拍里点两个控件（顺手把两个开关都点了）——观众来不及看清哪个变了；一拍一个控件。
- 光标被 toast 盖住——层级破产（toast z 20 必须低于涟漪 29 与光标 30）。
- 忘了把控件状态纳入重播复位段——重播第一帧开关还是开着的、滑杆还在 76%、按钮还是成功态。

## 动效范围
- 属于本卡的：STEPS 时刻表这套架构纪律（`at` 是唯一时间源、光标与控件读同一个数、移动起点由 `at` 反推、一个控件一个无时间参数的响应函数）；控件坐标运行时反算成命名常量这条做法；入场的两级揭示（整卡 blur 0.6s → 区块每 0.2s 错峰 0.53s blur-in；光标起步由首拍 at 反推，demo 与末两块揭示重叠 0.65s）；光标走位语言（x/y 分缓动成弧线、跨区 0.62s / 相邻 0.40s、到位悬停 0.2s、按压 0.09s 锚在箭头尖 + 涟漪 0.35s、换态发生在按下中点不等抬手）；拖拽拍的纪律（只下压不回弹到松手才回弹、被拖控件与光标共用同一缓动同一时长）；四种控件响应语言（开关滑块+轨道转深 / 分段指示器只动 x + 标签同拍换色 / 滑杆填充与手柄与读数共用一个代理值 / 按钮 label↔勾交叉淡化不跳框）及"全卡共用一个 0.27s 换态时长"；成功 toast 三段（滑入 0.47s + 停 1.8s + 退 0.47s，最后一次按下后 0.33s 起）；语义色只上收尾那一拍；五层层级（底 UI < 控件状态 < toast < 涟漪 < 光标）。
- 不属于本卡的：demo 里那套"输出设置"假面板的结构与文案（标题/三行设置项/取消与保存按钮/toast 文案全是演示语境）、灰阶线框这套取值（`#e0e0e0` 卡边框 / `#c8c8cd` 控件描边 / `#1d1d1f` 开关轨与指示器 / `#ececef` 滑杆轨都是占位）、`#d8383a` 这个具体语义色、控件的具体尺寸（开关 46×26 / 分段 220×34 / 滑杆轨 168 / 按钮 36 高）、"开关+分段+滑杆+按钮"这个具体控件组合（换成表单填写、多步骤向导、下拉筛选、聊天输入同样成立）、角标主持人（本卡未用）、深墨箭头这个具体光标造型（与 cursor-actor-demo 同款，形状属于那张卡）。
- **与 `cursor-actor-demo◆` 的边界（重要）**：那张卡是**光标单动作语法**——一枚光标怎么移动、怎么悬停、怎么按压、怎么拖，一个动作对一个口播词，讲的是"光标这个演员本身怎么演"；它的 demo 里控件响应只是用来证明"点了有反应"。本卡是**整套界面按脚本联动的架构**——光标降级成时刻表的一个消费者，真正的内容是"一张表同时驱动光标与全部控件"这套时序架构（`at` 共享、坐标命名常量、响应函数化）。选卡判断：只演一两个动作（"你就点这里"）用 cursor-actor-demo；要演一条完整流程（三拍以上、多个控件、有收尾回执）用本卡。两张卡的光标实现是同一份代码，**升级光标造型时两边同步改**。
- 迁移接口：`STEPS` 表是唯一的迁移入口——`at` 全量换成实际语音的词级时间戳，`target` 换成目标 UI 的控件名；新增控件 = 往 `POS` 加一个反算坐标 + 往 `RESPOND` 加一个响应函数（函数内部不碰时间）；尺寸按画幅等比缩放（光标约画幅短边 6~8%，控件尺寸跟着 UI 截图走）；语义色换成目标产品自己的 primary/success token（按钮底 + toast 图标两处同改）；语速变化时整表 `at` 重排，**各动作时长（`moveLong`/`hoverHold`/`press`/`swap`/`toastIn`）保持不变**——这些是手感常量，跟着语速缩放会让快语速下的操作糊成一团。
- 底色要求：白底即可（浅色设置面板是最常见情形）。深色 UI 同样成立，硬要求两条：**光标与底的对比必须保住**（深墨实心 + 白描边在两种底上都成立，深底把 `drop-shadow` 调淡）、**控件的开/关两态对比必须保住**（开关轨由"白→深"改为"深→高亮"，滑杆填充改为提亮，分段指示器改为亮块 + 深字）。toast 由白卡改为比背景略亮的深卡 + 保留同一个语义色图标。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/ui-flow-theater.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。props：无；STEPS / POS / 面板文案在 CONFIG 与 JSX 常量里，换内容需改源码。
- HTML/GSAP：demos/ui-flow-theater/index.html。**换流程只改 `STEPS`**（一行一拍：`at` 时间戳 + `target` 控件名 + `act` 动作 + 拖拽拍的 `until`）；换界面改 `#stage` 里的 `.panel` 结构，然后同步改两处、只有两处——`POS` 里那几行 `P(el, fx, fy)` 反算，和 `RESPOND` 里对应的响应函数（响应函数签名是 `(t, step)`，`t` 就是"该变了"的时刻，函数内部不允许出现别的时间数字）；节奏参数全在 `CONFIG`。可整段摘走的核心是四块：`CONFIG` + `moveTo/press/hold` 三个光标原语 + `POS` 反算 + `RESPOND` 表，最后那个 `STEPS.forEach` 走表循环是把它们缝起来的全部代码（不到 20 行）。注意 `.blk` 用的是 `filter: blur()` 揭示，**入场结束后 GSAP 会把 `filter` 留成 `blur(0px)`**——后面若要给区块加 `will-change`，只加在有文字的容器上（加在整卡层会让 1px 边框在锐利/模糊间脉动）。
- Remotion 移植：template/cards/ui-flow-theater.tsx 即实现真值——STEPS 表 + POS 常量 + 按 `at` 反推的光标段 + 四个控件响应，全部由 `t = frame / fps` 求值，**两边的 `at` 是同一个常量**（这就是"共享 at"在帧驱动下的写法）。本库的秒 → 帧换算：×30（`swap` 0.27s = 8 帧、`hoverHold` 0.2s = 6 帧、`toastIn` 0.47s = 14 帧、整卡揭示 0.6s = 18 帧、区块错峰 0.2s = 6 帧）。若改用 Remotion 原生写法：`interpolate(frame, [at*fps, (at+swap)*fps], [from, to], {easing: Easing.out(Easing.quad), extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})`，光标 x/y 两轴分别用 `Easing.inOut(Easing.quad)` 与 `Easing.inOut(Easing.sin)`。
- 剪辑软件对应物：剪映/CapCut——把界面拆成"底图 + 每个控件两张状态图（关/开）"，底图一轨常驻，每个控件两轨叠放并在该拍的按下帧硬切（下层关、上层开，用关键帧把上层不透明度 0→100 在两帧内切完，别用长淡入），光标是一张放大的 PNG 单独一轨打位置关键帧并把两端设"缓入/缓出"，滑杆填充用色块 + 蒙版位置关键帧、手柄单独一层同区间同缓动（两层必须选同一种缓动），toast 用一张卡片 PNG 做位置+不透明度关键帧；AE——每个控件一个预合成、状态切换用 Time Remap 或两层 Opacity 在同一帧对切，光标 Position 关键帧 + 空间插值改"贝塞尔"手动拉弧线，**所有关键帧的时间码从一张 marker 表来**（在时间轴上先按语音打好 marker，再把每个图层的关键帧吸附到 marker 上——这就是"共享 at"在 AE 里的等价物）；任何软件里的"UI 演示模板/鼠标点击特效预设"一律不用（节奏不受控、自带发光涟漪与拟真质感）。

<!-- ===== /file: video-talkcraft/references/cards/ui-flow-theater.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/ui-prop-theater.md ===== -->

---
name: ui-prop-theater
标题: 界面道具剧场
优先级: P1
代码: template/cards/ui-prop-theater.tsx
一句话: 拟物 UI 道具（进度条/任务清单）的状态按语音节拍逐步变化：进度 17%→96% 分段跳进、状态文案同帧换字、清单逐项打勾，收尾 100% 时完成勾唯一一次过冲——界面自己演戏，不是在跑 loading
适用: 口播讲"这东西怎么跑起来的""要等多久""要满足这几个条件"——进度/清单两类内容的默认呈现方式（滑杆拖动 + 数字联动见 ui-flow-theater◇）；工具测评、AI 产品讲解、教程与流程拆解类口播
时长: 起手静置约 0.55s 等口播开口 → 每拍 = 跳进 0.3s（+ 勾 0.2s / 换文案 0.32s）＋ 语音决定的停顿；4~5 拍一段共 4~6s
能量: 中
类别: 数据信息图
输入: 界, 人(可选)
语义: 过程演示, 步骤
素材形态: 界面
位置: 中段
props: hostSrc
---

## 意图
口播讲流程和进度时，观众要的是"到哪一步了"的实感。真实的 loading 条匀速爬，看起来是程序在忙，
和讲述完全脱钩；截图硬切又丢掉"它在往前走"的因果。界面道具剧场把 UI 当**演员**：
进度条不匀速填充而是在语音的重音点上分段**跳**一截，状态文案跟着跳那一下换，清单跟着念到的项打勾。
观众听到"先下载"看到进度跳到 17%，听到"再解压"看到勾落下——语音和界面互为字幕。
命门：**状态变化必须锚在语音节拍上**（匀速自动播 = 观众读作真在 loading，注意力立刻从讲述转到"还剩多久"）、
**跳进必须留静止段**（段间画面完全不动才显得"这一跳是被那个词触发的"）、
**一拍只推一件事**（进度跳 + 换文案 + 打勾可以同拍，但必须是同一个语义事件的三个面，不是三件事挤一起）。

## 动效核心
- **节拍表驱动（本卡的骨架）**：所有状态变化写成一张 `beats` 表——
  `{ at, pct, status, tick, done }`，`at` 就是该口播词的时间戳。段与段之间没有任何补间，画面静止。
  demo 的四段值取 17 → 43 → 71 → 96 → 100（**不等距**：真实安装的段落长短不一，等距分段一眼是假数据）
- **进度条分段跳进**：填充 `width` 从上一段值跳到本段值，单段 0.30s `power2.out`（起跳快、收尾软）；
  百分比读数与填充**共用同一个代理值**（`prog.p` 的 `onUpdate` 同时写 width 和文本）——
  两者分开各跑一条 tween 必然错开，"数字和条不同步"是最刺眼的破绽
- **状态文案换字（三段式，0.32s）**：旧文案 `y -6px` + 淡出 0.12s → 换文本 → 新文案从 `y +6px` 淡入 0.20s，
  都用 `power2.out`。换字必须与该拍的跳进**同帧起**（晚半拍就读作两件事）。收尾拍文案转强调色
- **清单逐项打勾（0.2s 画出）**：勾用 SVG path + `stroke-dashoffset` 从 0 画出（**不是淡入、不是缩放弹出**——
  画出才有"被逐笔勾掉"的手写因果），同帧 checkbox 描边转强调色、标签文字由灰转黑
- **打勾比跳进晚 0.16s**：先看见进度跳，再看见勾落下——因果顺序（进度推进 → 那一步完成），反了就成了"勾完才开始跑"
- **行微亮再落定（0.16s + 0.5s）**：勾落下同帧行底色淡入 `#f0f0f2`，0.18s 后回落到 `#f7f7f8` 的"已完成"底色。
  微亮是**瞬时反馈**，落定底色是**持久状态**——只做其中一个，要么完成项看不出来、要么整个清单一直在闪
- **收尾拍**：进度停 100% 的同一拍，完成勾 `scale 0.4→1` + 淡入 0.26s `back.out(2.2)`，
  勾线再延 0.08s 画出（先有圈、再有勾）。完成勾占**固定宽度**（`flex: 0 0 24px`）——
  否则弹出瞬间会把状态文案推挤位移
- **层级**：底 UI（卡片/轨道/未勾 checkbox）< 状态层（填充、行底色、已勾描边）< 弹出层（完成勾）

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `beats[].at` | 0.55 / 1.5 / 2.35 / 3.6 / 4.55 | 每拍锚定的语音时间戳，本卡的全部节奏都在这一列；改成等间距立刻退化成"自动播的假 loading" |
| `beats[].pct` | 17 / 43 / 71 / 96 / 100 | 分段值刻意不等距；段数 <3 看不出"分段"（读作一次填满），>6 观众数不过来、退化成匀速 |
| `jump` | 0.30s | 单段跳进耗时；<0.15s 读作数值瞬变（丢掉"往前推了一截"），>0.6s 段与段黏在一起又变匀速 |
| `swapOut` / `swapIn` | 0.12s / 0.20s | 状态文案出/入；入比出长才有"新状态落定"感，两者相等读作生硬替换 |
| `swapLift` | 6px | 换字位移；>12px 文字在行内乱窜抢戏，0 则读作直接替换文本（少了"翻页"的因果） |
| `tickDelay` | 0.16s | 勾比跳进晚多少；0 则两件事挤成一件、看不清先后，>0.4s 勾像迟到的补充说明 |
| `tickDraw` | 0.20s | 勾画出时长；>0.4s 慢得像在演示书法，<0.1s 读作直接出现（手写因果消失） |
| `rowGlow` / `rowSettle` | 0.16s / 0.5s | 行微亮淡入 / 回落到已完成底色；微亮 >0.3s 变成"这行在闪"，回落 <0.2s 看不出曾经亮过 |
| `donePop` | 0.26s `back.out(2.2)` | 完成勾弹出；这是全片唯一允许过冲的动作（收尾奖励），回弹强度 >3 显廉价 |

## 已知坑
- 进度条匀速从 0 爬到 100%——观众读作"真在 loading"，开始等进度而不是听讲；本卡的全部价值就在"分段跳 + 段间静止"。
- 分段值等距（25/50/75/100）——一眼是假数据；真实流程的段落长短不齐。
- 进度条填充和百分比数字各跑一条 tween——必然错开，"92% 配一条满格的条"一眼假；必须共用一个代理值。
- 状态文案换字晚于跳进——读作两件独立的事；文案换与那一跳必须同帧起。
- 勾用淡入或缩放弹出——读作"图标出现了"，不是"被勾掉了"；必须 `stroke-dashoffset` 画出。
- 勾先落、进度后跳——因果反了（还没干完就打勾）；勾必须比跳进晚 0.1~0.2s。
- 清单只打勾不改行状态（或只改底色不打勾）——完成项与待办项权重相同，一屏看不出进行到哪。
- 行微亮一直亮着不回落——整个清单在闪，观众不知道此刻推进到哪一行。
- 完成勾没有固定宽度——弹出瞬间把状态文案推得位移，收尾拍最该稳的一帧在抖。
- 一拍同时推三件不相关的事（进度跳 + 换标题 + 弹卡片）——观众不知道该看哪；一拍一个语义事件。
- 给 UI 加拟真质感（渐变/内阴影/玻璃/投影堆叠）——道具变成主角，抢掉讲述；线框灰阶足够。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/ui-prop-theater.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。props：仅 `hostSrc`（PiP 小窗）；节拍表 `beats` / 状态文案 / 清单条目在 CONFIG 与 `STEPS_DATA` 常量里，换内容需改源码。
- HTML/GSAP：demos/ui-prop-theater/index.html。**换内容只改 `CONFIG.beats`**（每行一拍：`at` 时间戳 + `pct` 目标值 + `status` 文案 + `tick` 行号 + `done` 收尾），清单条目改 `#stage` 里的 `.step` 结构（勾的 SVG path 保留）；换强调色改 `CONFIG.accent` 与 `.bar-fill` 的 `background`；节奏参数全在 `CONFIG`（`jump` / `swapOut` / `swapIn` / `tickDelay` / `tickDraw` / `rowGlow` / `rowSettle` / `donePop`）。**注意 `fromTo` 必须带 `immediateRender: false`**——否则建时间线那一刻就把起手文案打成 `opacity: 0`，第一拍前画面是空的（本 demo 踩过）。
- Remotion 移植：节拍表原样搬成 `BEATS` 数组，`at` 换算成帧号；进度用**分段查表**而不是一条 interpolate——`const seg = BEATS.filter(b => frame >= b.at*fps); const pct = interpolate(frame, [cur.at*fps, (cur.at+jump)*fps], [prev.pct, cur.pct], {easing: Easing.out(Easing.quad), extrapolate*: 'clamp'})`，段间自然静止；百分比文本读同一个 `pct` 变量（这就是"共用代理值"在帧驱动下的等价写法）；勾用 `strokeDashoffset: interpolate(frame, [tk*fps, (tk+0.2)*fps], [L, 0])`（`L` 用 `path.getTotalLength()` 或预量好的常量）；文案换字用两个 `<span>` 各自 interpolate opacity/translateY，切换点在 `at+swapOut`；完成勾用 `spring({frame: frame - done*fps, fps, config: {damping: 12}})`；行底色用 `interpolateColors(frame, [glowIn, glowOut], ['#f0f0f2', '#f7f7f8'])`。
- 剪辑软件对应物：剪映/CapCut——进度条用一个色块 + "线性擦除"或蒙版位置关键帧，**在每个语音节拍点打两个关键帧（跳的起止）、其余段落不打**（这就是分段跳进），状态文案用文本层在节拍点硬切+两端小幅淡入淡出，勾用"笔刷描边/线条生长"贴纸或勾的 PNG 配蒙版擦除；AE——进度用 Rectangle 的 Scale/Trim Paths 关键帧且**关键帧成对贴在节拍点**（中间保持段，别让 AE 自动补成匀速），勾用 Trim Paths 的 End 0→100% + Easy Ease，行底色用 Solid 的 Opacity 两段关键帧，完成勾 Scale 关键帧配 Overshoot 表达式；任何软件里的"进度条预设/loading 动画预设"一律不用（全是匀速，且自带光泽扫光）。

## 动效范围
- 属于本卡的：节拍表这套时序纪律（每个状态变化锚在一个口播词的时间戳上、段与段之间画面完全静止、一拍只推一个语义事件）；进度条分段跳进（0.3s `power2.out`、分段值不等距、填充与百分比读数共用同一代理值实时同步）；状态文案的三段式换字（上移淡出 0.12s → 换文本 → 下方浮入 0.20s，与跳进同帧起）；清单逐项打勾（`stroke-dashoffset` 画出 0.2s + checkbox 描边转强调色 + 标签转黑 + 行微亮 0.16s 后回落到已完成底色 0.5s）；"打勾比跳进晚 0.16s"这条因果顺序；收尾拍的完成勾弹出（`scale 0.4→1` + `back.out`，勾线延 0.08s 画出，占固定宽度不推挤）；三层层级（底 UI < 状态层 < 弹出层）。
- 不属于本卡的：demo 里那个"Studio 安装程序"假 UI 的结构与排版（卡片边框、图标、版本号、条目文案与右侧计量全是演示语境）、灰阶线框这套取值（`#ececef` 轨道 / `#d2d2d7` 未勾描边 / `#f7f7f8` 已完成底色都是占位）、`#d8383a` 这个具体强调色、进度条 10px 的高度与圆角、示例台词与字幕、角标主持人（数字人）、"进度条 + 清单"这个具体道具组合（换成任务队列/评分条/容量环/开关矩阵同样成立）。
- 迁移接口：`beats` 表是唯一的迁移入口——把 `at` 全量换成实际语音的词级时间戳，`pct` 换成真实流程的段落值（保持不等距）；强调色换成目标 UI 自己的 primary token（`CONFIG.accent` + 填充色 + 勾描边三处同改）；尺寸按画幅等比缩放（进度条高度约画幅短边 1.5~2%，勾 18~24px @960）；语速变化时整表时间戳重排，**各动作时长（`jump`/`tickDraw`/`swapIn`）保持不变**——这些是手感常量，跟着语速缩放会让快语速下的动作糊成一团；深色 UI 上把行微亮由"加深"改为"提亮"、未勾描边提亮、已完成底色改为略亮于卡片底。
- 底色要求：白底即可（浅色 UI 是最常见情形，灰阶轨道与白底天然分层）。深色 UI 截图同样成立，唯一硬要求是**进度填充与轨道、已勾与未勾两组对比都要保住**——轨道由 `#ececef` 改为比卡片底略亮的深灰，行微亮/落定底色的明度关系整组翻转。

<!-- ===== /file: video-talkcraft/references/cards/ui-prop-theater.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/unit-grid-proportion.md ===== -->

---
name: unit-grid-proportion
标题: 点阵比例图
一句话: 100 个小方格从网格中心分环长出（每环 4 帧 + ≤3 帧确定性抖动，1.1s 铺满；只做 opacity + scale .8→1，无位移），然后从左上起按阅读顺序逐格染成强调色（0.035s 一格），右侧 128px 大数字与染色同一时钟 0→37，图例最后浮出——把"37%"摊成 37 个可数的个体
适用: 比例型结论（"每 100 个 / 10 个人里有 N 个"）、转化率 / 留存率 / 成功率、社会统计与用户调研类口播；两组比例对比可左右各一个点阵。输入只有数据，卡自带矢量；人物不参与
时长: 6.1s（0.2 网格分环生长 1.1s → 1.4 大数字 / 标签入场 → 1.7 逐格染色 + 同步计数 1.3s → 3.2 图例浮出 → 5.7 全部同收 0.4s）；成片把染色起点对到口播念出数字的时刻
能量: 低
类别: 数据信息图
输入: 文
语义: 数据
素材形态: 无
位置: 中段
props: target, unit, label, legend, accent
优先级: P0
代码: template/cards/unit-grid-proportion.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 不吃素材；人在场时整组放人物对侧半幅（layout §4），或先 `host-shrink-to-chip` 让台 | ✗ | ✗ 卡自带矢量。格子可换成人形 / 品牌 logo / 产品图标，**同组同造型**（layout §8） |

只吃数据：一个 0~100 的整数 + 单位 + 标签 + 图例文案。

## 常用场景
1. 比例型结论："每 100 个观众有 37 个前 3 秒划走"（demo 演的）
2. "10 个人里有 7 个……"社会统计 / 调研数据（染 70 格，或改 10×1 一行）
3. 转化率 / 留存率 / 成功率 / 命中率——两色即可，语义色不进正文
4. 两组比例对比：左右各一个点阵，第二组染色晚 0.4s 起，数字并排

## 意图
`number-counter` 把比例抽象成一个滚动的数字，`bar-chart-growth` 抽象成一段长度——都要观众自己把"37%"换算回人。点阵比例图（数据可视化里的 unit chart / isotype）把比例**摊成可数的个体**：每格一个人，观众能一格一格数过去，"每 100 个里有 37 个"不用换算。口播讲"人"的时候，它比裸数字直观得多。做对四条：
1. **格子"长出来"不是"飞进来"**：只做 opacity + scale .8→1，无位移——位移读作卡片入场，不读作"一群人站好"。
2. **分环生长 + 同环抖动**：环号 = 到中心的欧氏距离取整，每环 4 帧；同环内再加 ≤3 帧确定性抖动——砍掉抖动，波前整齐得像机器扫描。
3. **染色按阅读顺序、与计数同一时钟**：从左上格起逐格染，大数字取 `round(进度 × target)`；数字先到、格子后到读作两件事。
4. **颜色只有强调色 + 灰**：未染格用 `#e3e3e8`，染色用唯一强调色；涨跌绿红只进图例语义，不上格子（design-language §1 红线）。

## 动效核心
- **几何**（960×540）：网格 10×10 @ (176, 82)，格 28、缝 6 → 334×334；右侧数字组 @ (584, 140)：大数字 128px/600（hero 阶，`tabular-nums`，字距 −4）+ 单位 44px 后置、标签 26px/600 两行（body 阶）、上距 18；图例 16px 灰 @ (176, 428)，三项 gap 18，色块 12×12 圆角 3。整组包围盒 (176, 82)–(~784, 448) 中心 x≈480（layout §4）；图例底边 448 < 字幕带 450。
- **生长**：格 i（列 c、行 r）环号 `ring = round(hypot(c−4.5, r−4.5))`，起点 `0.2 + ring×0.13 + srand(i)×0.1`，单格 0.3s `power2.out`：opacity 0→1、scale .8→1（`transform-origin 50% 50%`）；约 1.1s 铺满。`srand` 是正弦哈希（同 seed 同值，demo 与 tsx 同一公式）。
- **数字组入场**：1.4s 大数字、1.5s 标签，各 0.5s `power3.out`：opacity 0→1、y 14→0。
- **染色 + 计数**：1.7s 起第 i 格（i < target）在 `1.7 + i×0.035` 起 0.25s `power2.out` 底色 `#e3e3e8 → accent`（RGB 线性）；大数字同一时窗 `1.7 → 1.7 + target×0.035` 线性 0→target 取整。37 格 ≈ 1.3s。
- **图例**：染完 +0.2s 浮出 0.4s（opacity + y 14→0）。
- **退场**：5.7s 全部 opacity→0 0.4s `power2.in`，6.1s 结束。落定即静，无 idle。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `target` 染色格数 | 37（= 百分比） | <8 观众可能漏看；>60 该染"另一边"（留下的那 40），比例读法反转 |
| `cols × total` | 10 × 100 | 10×10 是比例最好读的规模；8×7 = 56 要换算；10×1 一行适合"10 个里有 N 个" |
| `ringDur` 每环间隔 | 0.13s（≈4 帧） | <0.1 读作闪现；>0.2 生长拖到 2s 抢了数字的戏 |
| `jitter` 同环抖动 | ≤0.1s | 归零波前整齐得像机器；>0.2 环序读不出，变成随机闪 |
| `growDur` 单格 | 0.3s，scale .8→1 | 起点 <.7 读作弹出；加位移就成了卡片入场 |
| `fillEach` 每格染色间隔 | 0.035s | 37 格 1.3s；<0.02 读作一刷子染完，>0.06 计数拖到 2s+ 观众等 |
| `fillDur` 单格过渡 | 0.25s | 太短像硬切像素，太长前后格颜色梯度拉成渐变条 |
| 大数字字号 | 128px/600 | hero 阶；与标签 26px 比 ≥2:1（layout §5） |
| 颜色 | accent `#0066cc` + base `#e3e3e8` | 只这两色；第二色出现即违规 |

## 已知坑
- 格子带位移飞入——读作一堆卡片入场，不是"一群人站好"。
- 生长同环无抖动——波前像雷达扫描，机器感。
- 染色随机散布（shotcraft 母本的"陆续发现异常"）——口播要的是"37 个"，随机染色观众数不过来；顺序染色才是比例。
- 数字与染色两条时钟——数字先到、格子后到，读作两件事。
- 用 8×7 / 6×6 等非 100 格网格——观众要换算，unit chart 的优势没了。
- 语义色（红 / 绿）染格子——"划走"染红是判断，不是统计；正文只用强调色。
- 图例压进字幕带（y ≥ 450）——图例底边必须 ≤ 448；成片有字幕时图例改放数字组下方。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/unit-grid-proportion.tsx——`target` 数字、`unit` 后缀、`label` 标签行、`legend` 三项、`accent`；durationInFrames 195；染色起点改 `CONFIG.fillStart`（对到口播念数字的时刻），句长改 `exitAt / end`。
- HTML/GSAP：demos/unit-grid-proportion/index.html——`CONFIG.target` 与 `.stat` / `.lgd` 文案；格子换图标时把 `.cell` 换成 `<svg>`，颜色改 `fill`。
- 母本：video-shotcraft `avatar-grid-radial-build-colorize`（分环生长 + 染色）与 `chart-live-moves` B 式 unit-dot-swarm 的"每个点是一个人"语义；移植时 8×7 头像卡改成 10×10 方格、随机染色改成顺序染色并与计数同钟。
- 剪辑软件对应物：剪映无原生 unit chart，用 100 个矩形贴纸 + 关键帧颜色（工作量大，建议直接渲 Remotion）；AE 用 Grid 效果 + 表达式 `index < target`；Flourish / Datawrapper 的 "pictogram" 图表可导 mp4 但没有生长节拍。
- 与 layout.md 的接口：网格 + 数字组是双元素组（§4），宽度比 334 : ~200 ≈ 1.7:1；两者顶边不对齐属刻意（数字组以大数字视觉中心对网格中带）；大数字 128 / 标签 26 / 图例 16 三档（§5：图例 16@960 = 32@1080，caption 档）。

## 动效范围
- 属于本卡的：分环生长（环号 = 欧氏距离取整、每环 4 帧 + ≤3 帧抖动、只 opacity + scale）；按阅读顺序逐格染色 0.035s/格；大数字与染色同一时钟取整；图例在染色结束后浮出；全部同收。
- 不属于本卡的：具体文案、单位、10×10 的坐标、白底舞台、格子造型（方格 / 人形 / logo 皆可）。
- 迁移接口：`target / unit / label / legend / accent`；1080p 输出格 28→56、缝 6→12、大数字 128→256、标签 26→52、图例 16→32；两组对比时第二份卡 `fillStart` 晚 0.4s。
- 底色要求：白底即可；深底舞台时 base 换 `rgba(255,255,255,.14)`（hairline 深色值）、accent 换 `#2997ff`。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- 网格 + 数字组包围盒水平居中：偏差 ≤48（无人物）；有人物时整组放人物对侧半幅中心。
- 图例底边 ≤ 448@960（字幕带之外）；成片带字幕时图例改到数字组下方。
- 定妆帧两张：染色中途（≈2.4s）核对已染格数 = 大数字读数；染完（≥3.2s）核对染色格数 = target、数字 = target。
- 染色格只有强调色一种；未染格与图例色块同一灰。
- 大数字 : 标签字号 ≥ 2:1；标签 ≥ 26@960（body 档）。

<!-- ===== /file: video-talkcraft/references/cards/unit-grid-proportion.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/whip-pan-transition.md ===== -->

---
name: whip-pan-transition
标题: 横甩转场
一句话: 出场镜头沿横轴甩出画外并带 8px 模糊（CSS `blur()`，各向同性）+ 1.4° 微旋，入场镜头从**同一方向的对侧**滑回画心、0.35s 刹住，再用二段回稳收掉旋转
适用: 平级并列的镜头边界——"这是 A，那是 B"、切到对比案例、切到另一个人物/另一个市场；快节奏与综艺化调性，也是竖屏切片最常用的一式
时长: 甩出 0.42s → 交叠 0.30s（≈9 帧 @30fps）→ 刹住 0.35s + 二段回稳 0.50s；从甩出起到回稳结束 1.21s（0.42 − 0.06 切点提前 + 0.35 + 0.50），其中刹住 + 回稳 0.85s
能量: 高
类别: 转场结构
输入: 场
语义: 转场
素材形态: 无
位置: 中段
props: hostSrc
优先级: P0
代码: template/cards/whip-pan-transition.tsx
---

## 意图
推穿处理的是"深入"，横甩处理的是"旁移"：两个镜头在叙事上是并列关系（不是递进），
用横向的一次挥摄把观众的视线从 A 甩到 B——空间上像转头，语义上像"另一边呢？"。
它是六式里能量最高、也最容易做错的一式，因为方向是可读的：**方向断裂比硬切更刺眼**。

做对的命门：① **两侧同向**——出场向左甩（x 走负），入场必须从右侧（x 正）滑回 0；
两侧都写"从左边进来"就是两次相反的挥摄拼在一起，观众会晕；② **必须刹车**——0.35s 的 `power3.out`
把速度吃掉，不刹直接停 = 撞墙；③ **二段回稳只收旋转，不收 scale**——scale 交给紧接着的 hold 继续推，
否则回稳结束那一刻画面彻底静止，又撞一次墙。

## 动效核心
时间结构（`cut = at + 0.42 − 0.06`，参数全在 `CONFIG.whip`；`dir = left` 时 `dist` 取负）：

| 阶段 | 时刻 | 出场镜头 | 入场镜头 |
|---|---|---|---|
| 甩出 | `at` → `at+0.42` | `x 0→−560` + `rotate 0→−1.4°` + `blur 0→8px`，`power3.in` | 停在 `x +560`、`rotate +1.4°`、`scale 1.06`、`blur 8px` |
| 切点 | `cut = at+0.36` | 0.30s 淡出（无 ease，甩镜期糊到看不清） | 0.12s 快速淡入 |
| 刹住 | `cut` → `cut+0.35` | — | `x →0` + `blur→0` + `rotate→+0.42°` + `scale→1.02`，`power3.out` |
| 二段回稳 | `cut+0.35` → `+0.85` | — | `rotate →0`，`sine.out`（**只收旋转**） |
| 交班 | — | — | hold 期慢推（从 1.02 继续 +0.04，`sine.inOut`） |

- **`cutLead` 只有 0.06s**：切点几乎就压在甩到最快的那一刻——这一帧两边都糊成一片，
  是天然的遮挡帧，交叠可以做到全六式里最短（0.30s）。切点太早会露出还没糊的旧画面。
- **`power3.in` → `power3.out` 的速度接力**：出场是三次方加速离场，入场是三次方减速入场，
  拼起来是一条完整的挥摄速度曲线。用 `power1`/`linear` 就没有"甩"，读作平移幻灯片。
- **微旋 1.4° 是手持感的来源**：出场旋 −1.4°、入场从 +1.4° 收到 +0.42° 再回 0。
  纯 x 位移读作机械推轨；旋转量超过 3° 就变成翻滚特效。注意旋转方向也要跟着 `dir` 一起翻。
- **入场起手 `scale 1.06`**：甩进来的画面略大一点，刹住时收到 1.02，等于横轴运动里搭了一丝纵深，
  让"刹住"这件事有两条轴同时减速，更像真镜头。
- **位移量 560px @ 960 舞台宽 ≈ 0.58 屏宽**：换尺寸按屏宽比例折算，不要照抄像素值。

Remotion 对应写法（`template/motion-systems/transitions.tsx`）：

- 出场 shot（`dir` 必须与入场一致）：`{ tail: 9, path: [{t:0, scale:1.02}, ...whipOut(tEnd, {dir:'left'})] }`
- 入场 shot：`{ lead: 9, path: [...whipIn(leadSec, {dir:'left'}), {t:9, scale:1.0}] }`
- `whipIn` 内部已经把方向取反（`x: -sign(dir) * dist` 起步），所以**两侧传同一个 `dir`** 就是同向；传相反的 `dir` 才是方向断裂。
- 它生成三个 CamKey：起手（画外 + blur + rot + scale 1.1）、`brake` 刹住（x=0、blur=0、rot 残留 30%）、`brake+0.65` 回稳（rot=0、scale=1.0）。

## 参数表
| 参数 | 典型值 | 调节手感 |
|---|---|---|
| 甩出时长 `out` | 0.42s | <0.25s 只剩一帧糊、读不出方向；>0.6s 读作"平移"而不是"甩" |
| 位移量 `dist` | 560px @960 宽（0.58 屏宽） | <0.35 屏宽读作抖了一下；>1 屏宽出场镜头早已出画，末段是空甩 |
| 模糊 `blur`（各向同性 CSS blur） | 8px | 0 读作幻灯片推入；>14px 交叠期完全糊掉，空间连续性丢失 |
| 微旋 `rot` | 1.4° | 0 读作机械推轨；>3° 读作翻滚/故障特效 |
| 刹车时长 `brake` | 0.35s | 不刹（直接 set x=0）= 撞墙；>0.6s 读作滑冰、失去挥摄的果断 |
| 二段回稳 `recover` | 0.50s | 省掉它 = 画面歪着不回正；>1s 像晕车 |
| 交叠帧数 `overlap` | 0.30s ≈ 9 帧 | 全六式最短——甩镜糊帧本身就是遮挡；>0.5s 两个糊画面叠在一起像脏 |
| 切点提前量 `cutLead` | 0.06s | 更大 → 露出还没糊的旧画面；0 → 切点落在减速已经开始之后，甩感被削 |

## 已知坑
- 两侧方向写反（出场向左甩、入场也从左侧进）：方向断裂，观众明确感到"错了"，比硬切更糟。
- 忘了旋转也要跟方向翻：位移同向、旋转反向，画面像被拧了一下。
- 不刹车直接 `set x:0`：撞墙，甩镜的全部果断感在最后一帧被浪费。
- 二段回稳把 scale 也收到 1.0：回稳结束即静止，撞第二次墙——scale 必须交给 hold 继续。
- 用 `linear`/`power1`：没有加速度就没有"甩"，读作 PPT 的"推入"切换。
- 镜头层没铺过画幅：甩出瞬间画面边缘漏底色（白底上是白边）。demo 用 `.shot { inset:-14% }` 兜住。
- 一片里左甩右甩随机混用：方向应服务叙事（时间轴向右、回溯向左），随机换向读作乱。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/whip-pan-transition.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。props：仅 `hostSrc`（未使用）；两侧镜头是占位 tile，成片组装走 transitions.tsx 的 `whipOut` / `whipIn`。
- HTML/GSAP：`demos/whip-pan-transition/index.html`。摘 `whipPan(出场镜头, 入场镜头, 起始秒) → 结束秒`
  一个函数 + `CONFIG.whip` 一组参数即可；换方向把 `dist` 与 `rot` 的正负**两侧一起**取反，
  以及初始 `gsap.set(S[1], {x: +dist})` 也要跟着翻。`hold()` 一起摘。
- Remotion：`whipOut(tEnd,{dir})` + `whipIn(leadSec,{dir})`，两侧传同一个 `dir`；
  `path: [...whipIn(0.30,{dir:'left'}), {t:9, scale:1.0}]`，path 组装写法参考 `template/motion-systems/MainVideo-example.tsx`（示例用的是别的式子，未含 whip）。
- 家族关系：把横轴换成 scale 轴 = [[push-through-transition]]；加曝光重音 = [[overexpose-flip-transition]]；
  想要"整体换台"而不是"空间旁移"时用下面的径向爆糊变体。同一边界只用一式。
- 帧级压缩版（实测，真实竖屏口播）：
  - **径向爆糊 whip**（Y17upxADWXs）：出场帧的径向模糊由中心炸开到满屏，入场侧从模糊高位收敛——
    横甩的**无方向版**，适合"话题整体换台"而非空间位移，0.1~0.2s 完成。
  - **速度线擦除**（小Lin说·韩股崩盘）：一组同向速度线（细长条）扫过屏面完成换场，方向感由线条承担，
    相机只做轻微同向漂——最轻量，不吃相机预算。
  两者与本卡同一条纪律：**两侧同向**、一个边界只用一式；帧级式样太短，方向断裂比标准版更刺眼。
- 剪辑软件对应物：剪映"运镜转场→左右甩动"；CapCut "whip pan"；
  AE 是两侧 camera 的 X 位移 + Blur（tsx 为各向同性 blur；AE 想要甩痕方向感可换 Directional Blur）+ 轻微 Z Rotation——本卡把手 K 固化成了参数。

## 动效范围
- 属于本卡的：出场 `x 0→±dist` + `rotate 0→∓1.4°` + `blur 0→8px` 的 `power3.in` 甩出；
  入场从对侧 `x ∓dist`、`rotate ±1.4°`、`scale 1.06`、`blur 8px` 起手，`power3.out` 在 `brake` 0.35s 内
  滑回 `x=0` / `blur=0` / `rot` 残留 30% / `scale 1.02`；**二段回稳只收旋转**（`sine.out` 0.50s，scale 留给 hold）；
  交叠 0.30s（全六式最短，因为甩镜糊帧本身是遮挡）+ 入场 0.12s 快速淡入；
  两侧方向严格同向（位移与旋转都要同向）；hold 期相机永不静止的慢推。
- 不属于本卡的：两个镜头里的文字与配色（白/浅灰 tile + 灰字式名是"认式子的标签"，不是台词字幕）、
  左上说明角标、`dist` 的具体像素值（按舞台宽折算）、`.shot` 的 `inset:-14%` 具体数值。
- 迁移接口：时序全在 `CONFIG.whip`（`out`/`overlap`/`brake`/`recover`/`cutLead`）；
  **换尺寸时 `dist` 按屏宽比例缩放**（demo 是 0.58 屏宽），`blur` 按输出分辨率线性缩放；
  **改方向必须两侧一起改**——`dist`、`rot`、入场初始 `x` 三处同时取反（方向断裂比硬切更糟）。
- 底色要求：白底即可。本式不含叠加层，相机曲线与底色无关；唯一要求是镜头层铺过画幅（`inset` 负值）以免甩出时漏底。

<!-- ===== /file: video-talkcraft/references/cards/whip-pan-transition.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/word-relay-filmstrip.md ===== -->

---
name: word-relay-filmstrip
标题: 动词接力胶片
一句话: 左列 360 宽的等高截图卡纵向排成胶片、深浅边框相间，右侧衬线两行——名词"一个 AI，能"恒定、动词原位接力：每 1.4s 旧词 0.18s 灰化淡出、胶片同起 0.4s power2.inOut 滚动恰好一卡高（212）、新词 +0.2s 起 0.25s 落位（先出后进不叠影），词块垂直中心钉在当前卡中点 y=264；末词换强调色，静置 0.9s 后胶片与词块同收——每切一个词，证据跟着翻一页
适用: "一个主体 × 多种能力"的枚举（AI 能写 / 画 / 剪 / 配，每个动词配一张截图）、作品集 / 案例流（每个案例一张图一个词）、产品多场景巡礼、"这些年我做过……"的个人经历列举；4~6 个词，每词一张图；无人物在场
时长: 6.4s（0.4 首词 → 1.8 / 3.2 / 4.6 三次切词各带一次步进 → 5.95 同收 0.45s）；成片按口播念到每个动词的时刻摆切词点，词期 1.0~1.8s 不必均匀
能量: 中
类别: 素材呈现
输入: 图, 截图, 文
语义: 例证, 列举
素材形态: 横屏, 多图
位置: 中段
props: noun, verbs, labels, srcs, accent
优先级: P1
代码: template/cards/word-relay-filmstrip.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 人物不参与（人在场的列举用 parallel-items-with-host） | ✗（tsx 的 `srcs` 仅走 `<Img>`，不播视频；换法见复用指引） | ✓（默认输入）每个动词一张截图 / 照片 |

一个动词对应一张卡；多给一张卡 = 露在视窗下方的"下一张"，暗示还有。

## 常用场景
1. "一个 AI，能 写文案 / 做配图 / 剪视频 / 配旁白"——每个动词配一张对应截图（demo 演的）
2. 作品集 / 案例流：左列是案例截图，右侧是"我做过 电商 / 教育 / 游戏"
3. 产品多场景巡礼：同一产品在不同场景的界面 + 场景名
4. 个人经历列举："这些年我 写过书 / 做过播客 / 开过课"

## 意图
口播讲"一个主体能干 N 件事"时，`word-slot-cycle` 只换词、没有证据；`filmstrip-conveyor` 只有图匀速流过、没有词。两者合在一起就是编辑部式的"词图对照"：名词钉死、动词接力，**每换一个词证据翻一页**——观众听到动词的同时看到它的截图。做对四条：
1. **胶片只在切词窗内滚动恰好一卡高**，其余时间零位移——持续滚动是违例（读作传送带），"咔哒"步进感是本卡的节拍。
2. **先出后进不叠影**：旧词 0.18s 灰化淡出、新词 +0.2s 起落位；同帧交叉必叠影（母本 v2 叠影"resebuilds"被抓）；间隙 >10 帧读作断片。
3. **词块垂直中心 = 当前卡中点**（像素级）：视线在词与图之间平移零距离；差 >8px 可感（母本用户单点意见）。
4. **深浅边框相间**：等高卡不相间读不出"滚了一格"；卡太窄失去"证据"分量。

## 动效核心
- **几何**（960×540）：视窗 `.wrf-win` 80×0 起 360×540 `overflow hidden`；胶片卡 360×200、间距 12（一卡高 212）、圆角 10、边框 6（奇数卡 `#1d1d1f` / 偶数卡白 + 1px hairline 外描），卡内左下 13px 标签；初始胶片 `y = 164` → 首卡中点 264。右侧词块 `.wrf-words` left 520、高 528 flex 居中（中心 264）：名词 34px / 600 / `#7a7a7a` 衬线、字距 2；动词 60px / 700 / 墨色衬线、行高 72、字距 2，末词强调色。
- **首词**：0.4s 起 0.25s `power2.out`（opacity 0→1、y 12→0）。
- **切词**（第 i 次在 `0.4 + i·1.4`）：旧词 `opacity→0、color→#9a9da6` 0.18s `power1.in`；胶片 `y → 164 − i·212` 0.4s `power2.inOut`（同起）；新词 +0.2s 起 0.25s `power2.out` 落位。
- **退场**：`exitAt = 末次切词 + 0.2 + 0.25 + 0.9 = 5.95`，胶片视窗 + 词块 opacity→0 0.45s `power2.in`，6.4s 结束。落定即静置，无 idle。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `period` 词期 | 1.4s（母本 45~60f） | 口播按句长摆，1.0~1.8 不必均匀；<0.9 读不完词 + 胶片看不清 |
| `scroll` 切词窗 | 0.4s power2.inOut | 恰好一卡高；持续滚动 = 命门违例；滚过头 / 不足读作机械故障 |
| `cardH` | 212 = 200 + 12 | 卡高与间距一起进步进量；改卡高必须同改 |
| `fadeOut` / `landIn` | 0.18 / 0.25s，间隔 0.02 | 同帧交叉必叠影；间隙 >0.33s 读作断片 |
| `startY` | 164（卡中点 264 = 词块中心） | 差 >8px 可感；词块高度变了要同调 |
| 字号 | 名词 34 / 动词 60 | 用户 2026-09-06 定版（首版 44 / 84 太大）；动词字重 ≥ 名词 |
| 字体 | 衬线（Songti / Noto Serif CJK） | 无衬线会丢"编辑部"气质 |
| 卡数 | 动词数 + 1 | 多一张露在下方 = "还有"；等于动词数则末词时视窗下方空一格 |

## 已知坑
- 胶片持续滚动——读作传送带（那是 `filmstrip-conveyor`），本卡的节拍在"咔哒"一格。
- 新旧词同帧交叉——叠影；旧词必须先出干净再进新词。
- 词块中心没对齐卡中点——视线在词与图之间要跳；差 >8px 可感。
- 卡同色不相间——等高卡滚一格看不出滚过。
- 用无衬线——"编辑部"气质没了，退成普通列表。
- 卡太窄（<300）——截图读不出内容，失去"证据"分量。
- 图与词不对应（图先换词后换或反之）——两个动画；胶片与词切换必须同起。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/word-relay-filmstrip.tsx——`noun / verbs / labels / srcs / accent`；durationInFrames 204（4 词；词数变了按 `exitAt + exitDur` 重算）；胶片滚动与词接力全部由 t 算。tsx 的 `srcs` 仅走 `<Img>`；要放视频把 `<Img>` 换成 `<OffthreadVideo muted>`（Remotion 自带；grid-to-hero.tsx 里有按后缀自动切换的现成写法），其余不动。
- HTML/GSAP：demos/word-relay-filmstrip/index.html——改 `NOUN / VERBS / CARDS` 与 `CONFIG`；`.ph` 换 `<img>` / `<video>` 即真素材。
- 母本：video-shotcraft `word-relay-filmstrip`（左列黑白页面卡步进 + 右侧 Didot 衬线名词恒定动词接力）。口播化改造：页面卡换证据截图、词期 45~60f → 1.4s、字号缩小、末词强调色收束。
- 剪辑软件对应物：剪映两条轨——图片轨逐张"位置"关键帧（每次 12 帧滑一卡高）+ 文字轨逐词淡入淡出；AE 用 Position 表达式 `valueAtTime` 阶梯 + Text Animator Opacity。
- 与 layout.md 的接口：双元素组（胶片 360 + 词块）宽度比约 1:1（§4）；胶片贴左边 80 ≥ 安全边 48@960（§1）；动词 60px 远超条目档；词块中心 264 与卡中点对齐（§3 基线对齐）。

## 动效范围
- 属于本卡的：名词恒定 + 动词原位接力（先出后进）；胶片只在切词窗滚一卡高的步进；词块中心 = 卡中点；深浅相间边框；末词强调色。
- 不属于本卡的：具体文案与截图、衬线字体的具体家族、胶片在左词在右（可镜像）。
- 迁移接口：`noun / verbs / labels / srcs`；1080p 输出字号 ×2（68 / 120）、卡 720×400、卡高步进 424；切词点按口播摆。
- 底色要求：白底 / 羊皮纸底成立；深底时卡边框改浅深相间反色、词色反色。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- 任一静置帧：当前卡（视窗内完整可见的那张）中点 y 与词块（名词 + 动词）中心 y 之差 ≤8px（动词行单独的中心在其下约 30px，不是对齐基准）。
- 切词窗外任一帧：胶片 y 为 `164 − i·212` 的精确值（零位移判据）。
- 切词中任一帧：不得同时看到两个动词 opacity >0.2（不叠影判据）。
- 末词落定后 ≥27 帧画面静止。
- 无人物在场；胶片左缘 x=80，词块左缘 x=520，两者间距 ≥80。

<!-- ===== /file: video-talkcraft/references/cards/word-relay-filmstrip.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/word-slot-cycle.md ===== -->

---
name: word-slot-cycle
标题: 词槽轮换
一句话: 句干"一个 AI，帮你"左端锚死不动，句尾深色胶囊每 0.7s 向上翻一格换一个短语（前 8 帧换位 power2.inOut + 运动模糊、后 13 帧静置读词），胶囊宽度随词长帧内插值伸缩，胶囊外上下露两行 13% 的幽灵项暗示"还有一串"；换完 4 个词胶囊 0.23s 上飞逃走，结论"搞定所有事"从下 90px 带 back.out(1.4) 过冲落进同一位置——全卡唯一一次过冲留给结论，之后静置 ≥1.5s 再与句干同收
适用: 口播里"它能帮你 A / B / C / D"式的功能或用途列举、受众列举（学生 / 上班族 / 创作者 → 所有人）、章节预告（今天讲 选品 / 定价 / 投放）、反复句式（不是 X，不是 Y，是 Z）；4~6 个短语、末词是结论；比逐条列表快、比逐词淡入有节拍
时长: 6.45s（0.2 句干 + 胶囊入场 → 1.1 / 1.8 / 2.5 三次换词 → 3.55 胶囊上飞 + 结论过冲落位 → 6.05 同收 0.4s）；成片按口播念到每个短语的时刻摆换词点，拍长 0.55~0.95s
能量: 中
类别: 字幕花字
输入: 文
语义: 转折, 列举
素材形态: 无
位置: 任意
props: stem, words, final, accent
优先级: P0
代码: template/cards/word-slot-cycle.tsx
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| ✗ 纯文字卡；人在场时把整句放人物对侧半幅（layout §4） | ✗ | ✗ |

作用于标题 / 要点层的一句话，不作用于底部跟读字幕（素排铁律）。

## 常用场景
1. "它能帮你 写代码 / 改简历 / 做 PPT / 查资料 → 搞定所有事"式的功能或用途列举（demo 演的）
2. 受众列举："适合 学生 / 上班族 / 创作者 → 所有人"，末词是结论
3. 章节预告："今天讲 选品 / 定价 / 投放 三件事"（结论换成"三件事"）
4. 反复句式："不是 X，不是 Y，是 Z"（末拍结论换强调色，前面的词保持墨色胶囊）

## 意图
口播讲"A、B、C、D"四件并列的事而画面里**没有人也没有素材**时，逐条列表要占四行、逐词淡入没有节奏，而观众听觉上是同一个句式在重复——画面就应该只动那个变化的槽位。词槽轮换把句干钉死、只换句尾一个词，是"列举"的最小画面形态：观众一眼认出句式，之后只跟着节拍读新词。做对四条：
1. **句干绝对定位左端锚死，不能 flex 居中**：胶囊变宽会带着句干重排，整句左右甩（shotcraft 首轮判例）。本卡的居中由"句干 + 间距 + 结论"总宽反推 left 一次算定。
2. **每拍前 8 帧换位、后 13 帧静置**：静置段是给观众读词的，读不完的拍等于没换；拍长 <0.55s 读不完短语，>0.95s 节拍器感散掉。
3. **新词减速落定、旧词加速逃走**：滚轮两头都缓（power2.inOut）是"起步与停稳"，胶囊最后上飞用 power2.in——方向感是"向上翻页"。
4. **全卡唯一一次过冲留给结论**：列举是平的，结论 back.out(1.4) 落位才有档次差；结论落定后静置 ≥1.5s，这句话是全段目的，不 hold 等于白列举。

## 动效核心
- **几何**（960×540）：整句 40px / 700 / 字距 -0.5 墨色 `#1d1d1f`，`.wsc-sent` 绝对定位 `top 238`（行高 64，中心落 y=270 中线），`left = (960 − (句干宽 + 14 + 结论宽)) / 2` 由隐形尺子量出后一次算定；句干与词槽间距 14。
- **胶囊**：高 56、圆角 999、底 `#1d1d1f`、白字 30px / 700、内边距 24×2 → 宽 = 词宽 + 48；`overflow hidden`，内部 `.wsc-reel` 竖排全部词（每行 56）。胶囊内字号必须小于句干（等大读作两个标题打架）。
- **幽灵项**：胶囊外上 `top -50` / 下 `top 62` 各一行 30px / 700 墨色、opacity 0.13，内容 = 当前词的前一个 / 后一个；换位起 0.1s 内隐、换位结束后 0.15s 现。
- **入场**：0.2s 句干、0.28s 胶囊，各 0.5s `power3.out`（opacity 0→1、y 14→0）；0.7s 幽灵项 0.3s 淡到 0.13。
- **换词**（第 i 次在 `1.1 + (i−1)·0.7`）：滚轮 `translateY → −i·56` 0.27s `power2.inOut`；同窗滚轮 blur 0→4（前 45%，power1.in）→0（后 55%，power2.out）；胶囊与词槽宽度同窗 `power2.inOut` 插到新词宽；幽灵项换字发生在换位结束那一帧。
- **收束**（`lastAt` = 末次换词 + 0.7 + 0.35 = 3.55）：幽灵项 −0.12s 先隐；胶囊 `y → −130 / blur 10 / opacity 0` 0.23s `power2.in`；词槽宽 0.3s `power2.out` 换成结论宽；结论 +0.12s 起 `y 90→0` 0.47s `back.out(1.4)`、opacity 前 1/3 淡完，颜色强调色 `#0066cc`。
- **退场**：`exitAt = lastAt + 2.5 = 6.05`，句干 + 结论 opacity→0 0.4s `power2.in`，6.45s 结束。落定即静置，无 idle。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `beat` 拍长 | 0.7s / 词 | <0.55 读不完短语；>0.95 节拍器感散掉；词数 4~6，8+ 观众开始数数 |
| `swap` 换位窗 | 0.27s（≈8 帧）| 拉到 0.4s+ 新旧同屏太久，读作两个词打架 |
| `row` / `pad` | 56 / 48 | 胶囊高与滚轮行高必须相等；pad <32 词贴边，>80 胶囊胖成按钮 |
| `swapBlur` | 4px | 去掉读作硬弹；>8 中间帧糊成色块 |
| `ghostAlpha` | 0.13 | "看得见但不抢"的甜点；>0.25 读作三行并列文字；删了"还有一串"的暗示就没了 |
| `flyOut` / `finalIn` | 0.23s / 0.47s back.out(1.4) | 出比入决绝；过冲 >2 结论像卡通，无过冲结论与列举没档次差 |
| `holdEnd` | 2.5s（≥1.5）| 结论是全段目的；不 hold 等于白列举 |
| `firstSwapAt` | 1.1s | 起手静置让观众先认出句式；<0.8 第一次换词时句干还没读完 |
| 词长差 | ≤2 倍 | 差 >2 倍胶囊跳变太猛、句子重心左右甩；长词拆成两词或缩短 |

## 已知坑
- 用 flex 居中整句——胶囊一变宽句干就跟着挪，整句左右甩（判例）；居中只能由总宽反推 left 一次算定。
- 静置段不够（拍长 <0.55）——观众读不完短语，换了等于没换。
- 换位不带 blur——读作硬弹；滚筒感来自"前快后极慢 + 一点模糊"。
- 胶囊内字号 ≥ 句干——读作两个标题打架；徽章依附句子必须更小。
- 结论没有过冲、或过冲给了中间的词——列举与结论没有档次差，观众不知道哪句是重点。
- 结论落定后立刻切镜——"这句话是全段目的"，静置 ≥1.5s。
- 幽灵项 >0.25——不再是"外圈暗示"，读作三行并列文字。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/word-slot-cycle.tsx——`stem / words / final / accent` 四个 prop 注入文案；durationInFrames 206（4 词，换词数变了按 `lastAt + holdEnd + exitDur` 重算）；词宽 / 句干宽 / 结论宽用 `useLayoutEffect + delayRender` 量一次（静态几何，不是自跑动画）。
- HTML/GSAP：demos/word-slot-cycle/index.html——改 `STEM / WORDS / FINAL` 与 `CONFIG`；句干 left 由脚本按总宽反推。
- 母本：video-shotcraft `pill-slot-cycle`（句干钉死 + 末拍收束）、`pill-chip-slot-cycle-handled`（胶囊宽度帧内插值）、`vertical-word-roll-blur-cycle`（滚筒相邻行）三卡合一。
- 剪辑软件对应物：剪映"文字模板 → 滚动字幕"里没有等价物，需逐词做关键帧：胶囊用"形状 + 宽度关键帧"，词用"位置 + 模糊"关键帧；AE 用 Text Animator（Position + Blur，Range Selector 按词）+ 形状图层宽度表达式绑文本 sourceRectAtTime。
- 与 layout.md 的接口：单主体落中线 y=270（§1）；整句包围盒按"结论态"居中（§4，偏差 ≤48）；胶囊内 30px ≥ 条目档下限 20@960（§5）。

## 动效范围
- 属于本卡的：句干钉死 + 单槽位换词的结构；0.7s 拍长里"8 帧换位 / 13 帧静置"的比例；滚轮 power2.inOut + 运动模糊；胶囊宽度随词长插值；幽灵项 0.13；末 pill 上飞 + 结论唯一过冲；结论 hold ≥1.5s。
- 不属于本卡的：具体文案、强调色的色值、胶囊深色（浅底上深胶囊是身份，深底舞台要整套反色重配）。
- 迁移接口：`stem / words / final / accent`；1080p 输出字号 ×2（80 / 60）、胶囊高 112、pad 96；换词点按口播念到每个短语的时刻摆。
- 底色要求：白底 / 羊皮纸底成立；深底时胶囊改浅色、文字反色，幽灵项透明度提到 0.18。

## 落位自检（选卡时抄进 SHOTBOOK 该镜自检列）
- 定妆帧两张：换词中（如 1.9s）与结论落定后（如 4.6s）；结论态整句包围盒水平居中偏差 ≤48，中心 y ≈ 270。
- 换词中那一帧：胶囊外上下各露一行幽灵项，opacity 0.13 ± 0.03；胶囊内词不越出胶囊。
- 任一换词前后：句干首字 x 不变（锚死判据），胶囊右缘随词宽变。
- 结论落定后至少 45 帧画面静止（无任何元素在动）。
- 人物在场时整句放人物对侧半幅中心（x = 240 或 720@960），不入人脸安全区。

<!-- ===== /file: video-talkcraft/references/cards/word-slot-cycle.md ===== -->

<!-- ===== file: video-talkcraft/references/cards/x-follow-card.md ===== -->

---
name: x-follow-card
标题: 关注卡弹出
优先级: P1
代码: template/cards/x-follow-card.tsx
一句话: X 资料卡整体 spring 弹入（0.62s 微过冲），十层内容随后按阅读顺序 0.07s 错峰 blur-in 逐层落位，光标弧线移入点击"关注"，同帧三件事一起发生——按钮两态交叉翻转 + 胶囊涟漪 + 粉丝数纸带上推 +1
适用: 口播里介绍某个人或账号——嘉宾出场、"这个人你该关注"、引用某人观点时给出处、推荐同行/作者；一条视频里同一张卡只出现一次
时长: 卡弹入 0.62s → 十层错峰 0.87s（0.34→1.21s）→ 静置到 1.55s → 光标移入 0.95s → 2.58s 点击（翻转 0.34s + 涟漪 0.5s + 计数 0.42s）→ hold 0.85s；全程 4.03s
能量: 中
类别: 人物互动
输入: 界
语义: 引用, 介绍他人
素材形态: 界面
位置: 中段
props: hostSrc
---

## 意图
口播说"这个人做的东西你该看看"，观众心里的问题是"他是谁、凭什么"。
一张资料卡把这两个问题一次答完：头像、名字、认证、一句 bio、地点/站点/加入时间、**关注者数**。
本卡的价值不在"贴一张卡"，在于**卡自己演一遍被关注的过程**——光标走过去点下"关注"，
按钮翻成"已关注"，粉丝数当场 +1。这一下把静态资料变成社会证明：不是你在夸他，是"有人正在关注他"。

命门三条。**第一条是壳与内容分两拍**：卡整体先 spring 弹入到位，十层内容**再**逐层落。
十层同时全亮 = 一张图淡入，那就只是贴图；壳先到位、内容后落，观众的眼睛才有机会按阅读顺序扫过去。
**第二条是光标必须走过去**（与 [subscribe-cta](subscribe-cta.md) 共享的纪律）：瞬移点击读作"状态自己变了"，
不是"有人关注了他"。**第三条是点击那一刻三件事同帧**：按钮两态交叉 + 涟漪 + 粉丝数 +1。
前两件是"这一下按到了"，第三件才是社会证明的落点——少了计数变化，这次点击只影响了一个按钮，没影响任何事实。

**产品皮 = 内容本身（2026-08-25 用户定版）**：本卡涉及真实产品界面，所以**完全还原 X 的样式**，
不做中性化——深色卡 `#16181c`、品牌蓝 `#1d9bf0` 的封面渐变/认证印章/关注按钮/tab 指示条、
右上那枚 X 标，全部照抄源码的 `THEMES.dark` + `accentColor`。理由：观众要一眼认出"这是 X 上的某个人"，
灰阶化之后那张卡谁都不是，"社会证明"这层意思也就断了——**平台身份是这张卡的信息量之一**。
可编辑的是**内容**（名字/handle/bio/地点/站点/计数/示例帖文案），外观不动。
头像仍走灰阶占位圆——那是 X 自己的默认头像样式（没有真头像素材时它就长这样）。

## 动效核心
- **卡整体弹入 0.62s**：`y 46→0` + `scale 0.9→1`，`back.out(1.35)` 的微过冲（源码 `spring(damping 12 / stiffness 120 / mass 0.8)`，ζ≈0.6 的欠阻尼）。
  **淡入是独立的时间窗**（0.05→0.35s）——位移先动、透明度后跟，remocn 全系入场的写法
- `transform-origin: 50% 0%`（卡顶）：弹入时卡从上边缘"垂下来"，绕中心缩放会让整卡上下同时长大，那是弹窗不是卡片落位
- **十层错峰 blur-in**：每层 `blur 8px → 0` + `opacity 0 → 1` + `y 8 → 0`，单层 0.24s、层距 0.07s（源码九组各差 2 帧 ≈ 0.067s）。
  三个属性一起动才是"blur-in"：只做淡入是普通 stagger，加上 blur 才有"从虚焦里对上焦"的落位感
- **层序按阅读顺序**：封面 → 头像 → 名字 → @handle → bio → meta 行 → 计数 → tabs → 示例帖 → **按钮行最后**。
  待交互的目标最后落位，光标才有东西可点（源码把按钮排在第 7 组，本卡挪到最后一组）
- **静置到 1.55s**：内容 1.21s 铺完，之后有 0.34s 什么都不发生——这是给口播介绍这个人的余量。卡就位了但还没有人动它
- **光标弧线移入 0.95s**（源码 32 帧 ≈ 1.07s）：x 用 `power2.inOut`、y 用 `sine.inOut` **异速叠出弧线**；
  从舞台右下外侧（1000, 470）进场；`transform-origin: 0% 0%` 锚在箭头尖，按压微缩不让尖端移位
- **落点必须在按钮的"终态"位置上量**（2026-08-25 修的 bug：光标没点到关注上）。两条纪律：
  ① 量之前先 `gsap.set(card, {clearProps: "transform"})`——若在铺了重播初始态（`y:46 / scale:0.9`）之后量，
  量到的是卡还在半空、还缩着 0.9 时的按钮位置；等光标 2.5s 后走到那儿，卡早已落到 `y:0 / scale:1`，
  按钮上移了约 46px ⇒ 点击帧光标压在按钮下方的空处。
  ② 减掉**箭头尖在 SVG 里的偏移**（尖在 `viewBox 14×21` 的 `(1,1)`，渲染 30×45 ⇒ 偏移 `(2.1, 2.1)`）——
  `x/y` 设的是元素左上角，不减就等于用"光标包围盒左上角"去对准按钮心，视觉上尖会偏在按钮右下。
  验收方式是**截点击那一帧**（`node scripts/shot-at.mjs x-follow-card 2.58`），肉眼确认尖压在按钮上
- **点击帧的反馈链**（同帧起，缺一环就假）：光标 `scale → 0.9` 一拍（0.09s）+ 按钮下压至 0.9（0.08s `power2.in`）+ 两态交叉 + 涟漪 + 计数滚动，随后按钮 `back.out(3)` 回弹 0.22s
- **两态交叉不是换文案**：同一个 116×40 盒子里叠两层（源码 `BUTTON_LAYOUT.horizontal` 的 `w/h`）——"关注"层 `opacity 1→0` + `scale 1→0.92`（缩着退），"已关注"层 `opacity 0→1` + `scale 0.86→1` 带 `back.out(1.7)`（涨着进）。
  直接改 `textContent` 读作"字变了"，交叉才读作"按钮换了状态"
- **粉丝数 +1 用纸带上推**：窗口 `overflow: hidden` 只露一行高（20px），里面一条上下两格的纸带 `y 0 → −20px`（`power3.out` 0.42s）——旧值出上沿、新值从下沿进。
  **动的是纸带不是窗口**（动窗口会把整行文字一起挪）。数字直接换值读作"数据刷新了"，滚动才读作"这个数涨了"
- **胶囊形涟漪**：`inset −6`、`border-radius 999`，`scale 0.92 → 1.3` + `opacity 0.55 → 0`，0.5s `power2.out`。
  `fromTo` 必须写 `immediateRender: false`——默认建表时就把 from 态刷上去，涟漪会在"还没被点"时提前挂在按钮外圈
- **光标用完即走**：顺势朝右下滑出并淡出 0.45s。常驻的光标会一直吸引注意力
- 层级：白底舞台 → 卡（深色卡 + 阴影浮起）→ 按钮行（绝对定位，贴封面下沿、与头像同一条基线）→ 光标（z-index 20）
- 卡按源码的 600px 参考宽度 1:1 写死，再由 `.scaler` 整体 `scale(0.885)` 装进 960×540 舞台——
  等价于源码的 `stageScale = min(w/refW, h/refH)`。**好处是所有样式值可以照抄源码不用换算**（改画幅只改这一个缩放数）

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| `cardIn` | 0.62s | 卡弹入。<0.35s 读作硬弹出（没有"落位"的重量）；>0.9s 观众等它进场 |
| `back.out` 过冲 | 1.35 | 弹入的微过冲。=0 只是缩放出现（卡没有重量）；>2.2 显廉价，卡像蹦上来的 |
| `layerStagger` | 0.07s | 十层错峰间隔。=0 退化成"一张图淡入"（本卡最容易改坏的一处）；>0.14s 铺完要 1.4s，观众开始逐条读而不听你讲 |
| `layerBlur` | 8px | 入场模糊起点。<4px 看不出"对上焦"；>16px 每层进场都糊一下，十层连起来像画面在抖 |
| `layerDur` | 0.24s | 单层 blur-in 时长。<0.15s 读作硬闪；>0.4s 与下一层重叠过多，错峰感糊掉 |
| `cursorStart` | 1.55s | 光标起手（= 内容铺完 + 0.34s）。这 0.34s 是给口播介绍这个人的；<0.1s 内容还没落完就有人来点，>1.2s 卡在那儿干等 |
| `cursorMove` | 0.95s | 光标弧线移入。<0.4s 接近瞬移，"有人在点"的证据消失；>1.4s 观众开始等它 |
| `clickDip` | 0.9 | 点击下压。>0.96 看不出按了；<0.85 按钮像被捏爆 |
| `flipDur` | 0.34s | 两态交叉。<0.18s 读作硬切图标；>0.6s 按钮在那儿慢慢化，观众盯着它不听你讲 |
| `rollDur` | 0.42s | 粉丝数纸带上推。<0.2s 读作数字闪了一下；>0.7s 一个数字滚这么久，注意力全跑过去 |
| 计数增幅 | 可读的一档 | 12.4万 → 12.5万。**必须肉眼可读出变化**——`128,431 → 128,432` 那一位观众看不见，等于没滚 |
| bio 长度 | 20~32 字 | 单卡两行以内；>40 字观众切换到"读卡"模式，你的讲述变成背景音 |
| 出现次数 | 1 次/条 | 同一张卡出现两次 = 观众第二次直接跳过；换人才换卡 |
| 在场时长 | 3~5s | >8s 变牛皮癣挡内容；<2.5s 观众还没读完名字就没了 |

## 已知坑
- **十层同时全亮**——退化成"一张图淡入"，本卡最贵的那拍（内容逐层落位）就废了。壳先到位、内容再逐层落是两拍。
- **blur-in 只做淡入不做 blur**——那是普通 stagger，"从虚焦里对上焦"的落位感没了。三个属性（blur / opacity / y）要一起动。
- **在铺了重播初始态之后才量按钮位置**（2026-08-25 实修的 bug）——量到的是卡还在半空、还缩着 0.9 时的坐标，
  光标走到那儿时卡早落位了，按钮上移约 46px ⇒ 点击帧光标压在按钮下方的空处，"有人点了关注"当场垮掉。
  量之前先 `clearProps` 卡的 transform，在终态量。
- **光标坐标没减箭头尖偏移**——`x/y` 设的是元素左上角，直接对准按钮心会让尖偏在按钮右下角外。减掉 `TIP`。
- **只跑 verify 的 t0/t1 两张截图就算验收过了**——那两帧大概率都不在点击时刻上，光标没点到按钮这类 bug 一路漏过去。
  交互卡必须**截点击那一帧**单独看。
- **按钮行排在层序中间**——待交互的目标先落位、后面还有内容在动，光标点下去的时候画面还没安定。按钮行放最后一组。
- **光标瞬移到按钮上**——读作"状态自己变了"，不是"有人关注了他"。社会证明的说服力归零。
- **两态用改 `textContent` 实现**——读作"字变了"不是"按钮换了状态"；两层叠着交叉、退的缩、进的涨。
- **点击后粉丝数不变**——这次点击只影响了一个按钮、没影响任何事实，社会证明的落点丢了。计数必须跟着 +1。
- **粉丝数直接换值**——读作"数据刷新了"；纸带滚动才读作"这个数涨了"。
- **滚动窗动的是窗口而不是纸带**——整行文字（含"关注者"三个字）会跟着一起挪。窗口固定、纸带在里面推。
- **计数增幅小到看不见**（`128,431 → 128,432`）——滚了等于没滚。增幅要落在肉眼可读的那一位上。
- **`fromTo` 忘了 `immediateRender: false`**——涟漪环建表时就把 from 态刷上去，按钮"还没被点"时环已经挂在外圈（本库实测过的老坑）。
- **卡的 `transform-origin` 用默认 center**——弹入时整卡上下同时长大，读作弹窗不是卡片落位；锚在卡顶（`50% 0%`）。
- **把 X 的皮灰阶化**（2026-08-25 用户定版否掉的做法）——黑底白字胶囊 + 中性八角星徽标看着"像个社交卡"但**不是任何平台**，
  观众读不出这是哪儿的账号，社会证明的出处就没了。这类卡产品皮 = 内容本身，照抄 `#1d9bf0` 与深色卡取值。
- **真人头像**——头像是唯一保持灰阶占位的一层（没有素材，且 X 默认头像本身就是灰剪影）；换成真人照要自己解决肖像授权。
- **光标常驻不走**——一直吸引注意力，观众看光标不看卡。点完即走。
- **同一张卡出现两次**——第二次观众直接跳过。换人才换卡。
- bio 写 lorem 或英文占位——"这是个真人"的说服力归零；写真实感中文。

## 复用指引
- Remotion/tsx（skill 首选）：template/cards/x-follow-card.tsx——自包含单文件，复制进工程即可用；参数在顶部 CONFIG，时长/尺寸在 meta。props：仅 `hostSrc`（未使用）；名字 / handle / bio / 计数 / 帖文在 JSX 常量里、坐标在 CONFIG，换内容需改源码。
- HTML/GSAP：`demos/x-follow-card/index.html`。**换人只改 HTML 里那几处文本**（`.name` / `.badge`（要不要认证）/ `.handle` / `.bio` / `.meta` 三条 / `.stats` 的两个数字 / `.post` 那条示例帖）——
  时序全在 `CONFIG`，与内容解耦，改文案不用碰任何时刻。粉丝数改 `.roll .strip` 里上下两个 `<i>`（上=旧值、下=新值，**窗口高 20px 与 `rollDur` 那条 tween 的 `−20px` 要同步**）。
  节奏在 `CONFIG.cardIn` / `layerStagger` / `layerDur` / `cursorStart` / `cursorMove` / `flipDur` / `rollDur`；层序改 `layers` 数组（按阅读顺序，按钮行留在最后）；光标起点 `CONFIG.START`（换尺寸时按舞台宽重算，落点由 `P(el, fx, fy)` 从元素实际位置反算，换布局不用改坐标数字）。
  核心可摘走：`CONFIG` + `DemoShell.register` 回调里的四段（①卡弹入 ②十层错峰 ③光标弧线 ④点击帧同帧五件事）。
- **不要关注交互、只要卡入场**（常见裁剪）：删掉 ③④⑤ 三段与 `.cursor` / `.rip` / `.f-on` 三个元素，①② 两段独立成立——这就是一张"资料卡弹入"的纯道具卡，时长压到 1.4s。
- Remotion：template/cards/x-follow-card.tsx 即实现真值——`CONFIG` + 四段编排（① `backOut(1.35)` 弹入 + 独立淡入窗 0.05→0.35s ② `layer(i)` 十层 blur-in ③ 光标 x `power2.inOut` / y `sine.inOut` 异速弧线，点击帧 `TC = cursorStart + cursorMove + 0.08` = 2.58s ④ 两态交叉 / 涟漪 / 纸带 `translateY 0→−20`），全部由 `t = frame / fps` 求值；粉丝数纸带用插值驱动，**不要用 `Math.random`**（多趟渲染会闪）。竖屏落地需按 720×1280 重排 `.scaler` 缩放与 `TARGET` / `START`。
- 剪辑软件对应物：剪映/CapCut——卡做成一张静态图，整体套"放大弹入"入场（时长 0.6s、带回弹）；十层错峰只能把卡**切成十张图层**分别给 0.07s 递进的入场（工作量大但效果对得上），偷懒版是切三段（封面/资料/按钮）；两态翻转是两个按钮图层交叉（"关注"层 Opacity 100→0 + Scale 100→92，"已关注"层 Opacity 0→100 + Scale 86→100 带弹性，关键帧**必须与点击帧对齐**）；粉丝数滚动用一个蒙版矩形 + 两行数字的文本层往上移。
  AE——`cardBounceIn` 用 `spring` 表达式或 Overshoot 预设；十层用 Sequence Layers + Gaussian Blur 的 Blurriness 关键帧（8→0）；光标弧线用一条 Path 绑 Position（比手打两条关键帧准）；纸带滚动用 Source Text 不变、Position 打两个关键帧（Easy Ease Out）。
  任何软件的"社交卡模板"要先检查两件事：各层是不是同时全亮、粉丝数有没有跟着变——市面模板九成两条都不合格。
- 音效：卡弹入一记 `pop`（`vol` 0.6、`rate` 0.94，降调 = 有重量）；十层起头一记 `paper`（`vol` 0.26、`rate` 1.12）铺底，**不要逐层给声**（十记会糊成噪音）；点击帧一记 `click`（`vol` 0.6）；粉丝数滚动两记升调 `tick`（0.34/1.10 与 0.36/1.22——升调读作"涨了"）。hold 段无声。

## 动效范围
- 属于本卡的：**壳与内容分两拍**这条结构纪律（卡整体 spring 弹入到位 → 十层再逐层落）、卡弹入的"位移先动 + 淡入独立窗"错位与 `transform-origin` 锚在卡顶、**十层错峰 blur-in**（blur 8→0 + opacity + y 三属性同动，层距 0.07s）与**层序按阅读顺序且按钮行最后**这条取舍、内容铺完后 0.34s 的静置（给口播的余量）、光标从屏外**弧线**移入（x `power2.inOut` / y `sine.inOut` 异速叠出弧线，锚点在箭头尖）、**落点在按钮终态位置上量且减掉箭头尖偏移**这条纪律（连同"交互卡必须截点击那一帧验收"这条验收方式）、点击帧**同帧五件事**的反馈链（光标缩一拍 + 按钮下压 0.9 + 两态交叉 + 涟漪 + 计数滚动，随后 `back.out(3)` 回弹）、**两态交叉的方向**（退的缩 `1→0.92`、进的涨 `0.86→1` 带 `back.out(1.7)`）、**粉丝数纸带上推 +1**（窗口固定、纸带在里面推，`power3.out` 0.42s）这一拍及"增幅必须肉眼可读"这条验收、胶囊形涟漪 `0.92→1.3` 与 `immediateRender: false`、光标用完即走（0.45s 滑出淡出）。
- 不属于本卡的：demo 那个人（"陈叙白 / @chenxubai / 杭州 / xubai.design / 2019 年 3 月加入"）与那句 bio、12.4万→12.5万这组具体数字、示例帖那句文案与三个互动数、灰阶头像剪影的画法、四个 tab 的文案（帖子/回复/媒体/喜欢）、光标 SVG 的具体形状。
  **注意与其他卡不同：X 的皮（深色卡取值、品牌蓝、认证印章、X 标、600px 卡宽 + 24px 圆角这组源码几何）属于"内容本身"而不是"可换的风格"**——见下面的底色要求。同一套时序当然可以套在别的"资料卡 + 一个可点的主操作 + 一个跟着变的计数"道具上（商品卡加购物车、课程卡报名、仓库卡 star 都成立），但那时它就不叫 x-follow-card 了，皮要换成那个产品的皮。
- 迁移接口：HTML 里那几处文本是唯一的内容入口（时序与内容解耦，改文案不碰任何时刻）；粉丝数改纸带上下两个 `<i>`（**窗口高与那条 tween 的位移量必须一致**）；`cursorStart` 按口播语速给（他介绍完这个人你才让光标进场）；`layerStagger` 按"十层铺完的总时长"给（层距 × 9 + `layerDur` ≤ 1.3s 是安全线，再长口播就要等）；换尺寸只改 `.scaler` 那一个 `scale()`（卡内所有值是源码原值，不参与换算）；换主操作时只改按钮两层的文案与 `flipDur`（交叉方向不动）；换计数语义时保证增幅落在肉眼可读的那一位；竖屏按源码的 vertical 布局走（卡宽 660、按钮在 542,336、光标从下方进场）；**不要关注交互只要卡入场**时删掉后三段即可（见复用指引）。
- 底色要求：**产品皮 = 内容本身，2026-08-25 用户定版：完全还原产品样式**。本卡涉及真实产品界面（X 资料卡），
  所以卡本体是 X 的深色皮（卡底 `#16181c` / 描边 `#2f3336` / 主文 `#e7e9ea` / 次文 `#71767b` / 品牌蓝 `#1d9bf0`），
  **不受"白舞台中性化"约束**——把它灰阶化会让卡"不是任何平台"，社会证明的出处随之消失。
  舞台本身仍是白底，深色只占那张卡；卡靠自身底色 + 阴影与背景分离，所以 overlay 压在实拍画面上同样成立
  （深色卡叠在实拍上比浅色卡更稳，不需要额外描边补丁）。浅色皮也在源码里（`THEMES.light`：卡底 `#ffffff` /
  描边 `#e6e9eb` / 主文 `#0f1419`），需要浅色 X 时整套换过去即可，**唯一要跟着翻的是"已关注"态**——
  浅皮下它是白底 + 灰描边 + 黑字，深皮下不能照抄那个白底（会比卡还亮、抢走全部注意力），要用卡底色 + 亮描边。
- 与相邻卡的分工：**vs [subscribe-cta](subscribe-cta.md)（多平台关注 CTA）**——那张是**语法合集**：三种平台式样（YouTube 订阅+铃铛 / B站三连长按 / 通用关注胶囊）串演，落地时只留一段，目标是"**示范观众去点**"，用在**收尾的价值兑现点**，overlay 只有控件没有卡。本卡是**单卡精做的社交证明道具**：一张完整资料卡（十层内容）+ 一次关注交互 + 计数变化，目标是"**证明这个人值得看**"，用在**介绍嘉宾/账号的时刻**。两张共享"控件弹入 → 光标弧线移入 → 点击反馈链 → 状态翻转"这套机制（本卡的 `P()`/弧线移动/`clickDip`/`immediateRender:false` 都与那张同源），差别是**卡还是控件**、**证明还是号召**、**中段还是收尾**。同一条视频里两张可以都出现（介绍嘉宾用本张，收尾要关注用那张），但不要挨着放。**vs [lower-third-nameplate](lower-third-nameplate.md)**——那张是"这个人是谁"的最小信息（名字 + 头衔，压在画面下三分之一，2~3s 用完即走），本卡是"这个人凭什么"的完整档案 + 一次交互；口播自己出镜报身份用那张，介绍**别人**并要观众记住这个账号用本张。**vs [media-pop-in](media-pop-in.md)**——那张是任意素材弹入的通用道具（无内容结构、无交互），本卡是有固定十层结构 + 交互编排的专用道具。

<!-- ===== /file: video-talkcraft/references/cards/x-follow-card.md ===== -->

<!-- ===== file: video-talkcraft/references/cinematography.md ===== -->

# 电影感规范：消除 PPT 感（口播视频的镜头方法论）

来源：ai-math-video 项目多轮调试结论（诊断 → 重构 → 实测）。这不是可选的风格建议，
是**结构性要求**——不满足时成片必然像"播放 PPT"。

## 0. PPT 感的四个病根（自检用）

1. **没有相机层**：画布静止，元素只是在固定舞台上淡入滑入。加"每场景 100%→104~106% 极缓慢推（或反向极缓拉出）"就能消掉一半 PPT 感。
2. **元素入场后就死了**：动画全是 entrance（opacity/translate 到位即冻结）——这正是 PPT"进入效果"的模型。动画感来自持续运动——**由场景相机的极缓推拉承担**，不靠元素自己抖。
3. **场景之间硬切翻页**：Sequence 边界内容整体瞬间替换。转场要靠**运动承接**，不是靠 crossfade。
4. **文档版式 + 信息堆积**：标题左上、要点网格是排版思路不是构图思路；元素只进不出，说到后面满屏静物。**一个节拍只讲一个主角**，说完就让位。

## 1. 七层镜头模型（词汇表）

| 层 | 职责 | 典型动作 |
|---|---|---|
| L1 相机 | 带观众穿过空间 | **极缓推进 / 极缓拉出**（唯一要求的运动；横移/环绕/dutch 不再作为场景相机动作） |
| L2 焦点 | 决定什么在光学上可读 | 虚→实入场、rack focus、集体退焦只留主体 |
| L3 主体 | 唯一主角的运动与变形 | 入场、接力、morph、kinetic type |
| L4 附着效果 | 主体的材质与状态提示 | 辉光、rim、粒子、闪光 |
| L5 配角 | 与主体互动、强化主体 | 反向运动、光束、环、时间轴、视差层 |
| L6 环境 | 氛围 | 分幕色温（静态 token，可选）；呼吸 vignette / 扫光 / 曝光脉冲已删 |
| L7 遮罩 | 控制可见性与取景 | 描边旅行、扫描线揭示、clip reveal |

层预算：**英雄时刻 4–6 层活跃；过渡镜头 2–3 层**；静息时刻允许只有相机一层在动（极缓推拉），
**不再要求主体 idle 与环境呼吸**（那套"处处在动"过了，不适用于口播——观众在听人说话、看字幕，画面的活只需一条几乎察觉不到的相机呼吸）。

## 2. 全局系统（先于任何场景实现，模板已提供代码）

代码在 `template/motion-systems/`，全部确定性（零 Math.random）、seek-safe。
**运动做减法（正主）**：口播视频的运动系统只保留两件——**G1 相机极缓推进或拉出** + **G3 让位状态机**。
主体 idle 微动、环境呼吸 vignette / 斜向扫光 / 曝光脉冲、相机重音脉冲、x/y 摇移、旋转与模糊曲线一律**不再要求**；
G2 视差与 G4 分幕色温降为可选。模板代码保留这些能力但默认关闭（`Live idle={false}`、`Environment` 三项默认 off）。

### G1 CameraRig（camera.tsx）
- 每场景**只有一条极缓的 scale 曲线**：推 1.00→1.04~1.06 或拉 1.06→1.00（按镜头意图选向），全程连续、末键落在镜尾之外（§6）。
- **不做** x/y 摇移、旋转（dutch）、模糊曲线，**不加**重音脉冲 / shake——`impulses` 留空数组；素材自身要动的用运镜卡作用在素材层，不动场景相机。
- `CamState`（含 progress）放进 Context；3D 场景用同一 progress 驱动 THREE 相机——一台相机两套投影。
- 相机路径集中在 shots.ts 一张表里（表驱动，与场景实现解耦），每条写推 / 拉方向与理由。
- **同起同收**：相机曲线、实拍底床、素材缓推这类持续运动的 duration = 镜头时长，**写速率不写固定秒数**
  （缩放 0.5%/s、横移 2.8px/s）；文字退场那 0.4s 底床与素材一起收。等最长那条 tween 跑完才结束镜头 = "字没了、画面还在空转"的尾巴。

### G2 Parallax 深度平面（camera.tsx 的 Plane）——可选，默认不装
- 场景内容分层：网格背景 depth 0.5、粒子 0.72、主内容 1.0、3D 画布 1.08、前景强调 1.12–1.2。
- `位移 = cam.x × (depth − 1)`，scale 同法偏置。推拉时前后景速度错开有纵深感，**但不再是要求**——静态幕底 + 相机极缓推拉已足够。

### G3 让位状态机（life.tsx）——idle 微动已删
- 生命周期：forming → resolved → **handing-off** → gone，全部 frame 纯函数。
- resolved 期**静置**：`Live` 默认 `idle={false}`，元素落定后一个像素不动——画面的活由相机极缓推拉负责。
- 让位规则：新主体入场帧 −6f，旧主体开始 `<Live demoteAt={新主体锚点秒}>`（0.5s 内缩 0.92 + 上移 + 亮度 −66% + 3px 模糊）。声明式：把下一主体的 ASR 锚点直接传给上一主体。
  **demoteAt = 降权留守，不是退场**：元素压暗后仍在原位占槽、计入 §4.5 同屏预算，新主体不得摆进它的位置（旧名 `retireAt` 读作"退场"曾直接导致 P0 文字相撞，2026-09-06 改名；旧名仍是 deprecated 别名）。
- `<Defocus>` 做 L2 集体退焦（只加模糊降透明度，不动位置）。
- **让位有三种方式，按"这元素还回不回来"选**：本拍讲完不再回指 →
  **真退场**（0.15–0.5s 出场后从版面消失）；马上还要回指/对照 → 降权留守（Live retire / Defocus，原位保留）；
  长镜头段 → 相机离开即让位。降权是合法手段，但**降权留守的元素仍占版面**——§4.5 排版预算
  （同屏 ≤3 组、空象限）必须把它计入；浅底上降权糊影依旧醒目，同屏留守别超 1 组。

### G4 Environment（env.tsx）——只留分幕色温，可选
- 呼吸 vignette 与斜向扫光**已删**（`breathe`/`sweep` 默认 false）；vignette 若要，是幕底配方里的**静态**一层（design-language §1.1），不是运动。
- 分幕色温做情绪曲线（幕边界 1.2s cross-fade——"让变化被感到而不是被看到"）。
- 曝光脉冲**已删**（`pulses` 默认 false）；重音靠主体自身的入场动效表达。
- 事件表只剩 ACTS（分幕色温，可选）；EXPOSURE_HITS / TRANSITION_FLASHES / VIGNETTE_TIGHTEN 留空不用。

### G5 线稿示意图（schematic.tsx）——纯文字镜必装，其余镜不装
- 素材行只有「文」的镜头（章节卡除外），主体面必须多一层"可看的物"：图标 + 方框 + 箭头 + 小标签的线稿示意图（`template/motion-systems/schematic.tsx`，图标 `icons.ts` 由 `scripts/fetch_icons.py` 生成）。
- 三条命门：**机器一笔画**（pathLength 归一 + dashoffset，power2.inOut，画完静置）、**线到哪亮哪**（连接线先画、节点被点亮后 pop）、**一套皮**（ink 3px + accent，磨砂白板托底，深底换 dark token）。
- 示意图每一拍挂词锚（beats.json），与 G1 推拉叠加；它不是第四个主体——与该镜标题是同一主体组的两半。规则、语义图形词典与落位自检见 `references/schematic.md`。

## 3. 运动转场库（Sequence 重叠 12–16 帧）

**硬规则：每个镜头边界都必须有明确的转场处置，禁止裸切**——
六式之一 / caret-wipe / shape-wipe / 长镜头连续运镜 / 图形接力（`line-carry-transition◎`：A 镜的下划线跑出画外围成 B 镜画框，全片只放一次当招牌位），五选一；SHOTBOOK 里每个边界写明用哪式。
（black-slam 的"最后 1 帧 opacity=0 硬出"是设计过的转场，不算裸切；Sequence 边界内容无处置地
整体瞬间替换才是裸切。）

机制：shots.ts 里每镜头声明 `lead`（叙事前多渲的帧）和 `tail`，相邻 Sequence 重叠；
`ShotFade` 只做像素淡化，**运动由两侧相机曲线同向承接**。
代码：`template/motion-systems/transitions.tsx`——ShotFade + 六式的 CamKey 生成器
（pushThroughOut/settleIn/whipOut/whipIn/blowoutOut/pullBackIn，直接 spread 进 path）
+ 叠加层（Overexpose 过曝亮心、Shatter+ParticleDrift 粒子溶接）。

每式一张配方卡（参数表/已知坑/HTML demo 见 `references/cards/<slug>.md`）：

| 转场 | 出场侧 | 入场侧 | 卡 |
|---|---|---|---|
| 推穿 | 相机加速推 + blur 升 | 从模糊高 scale 起步反向沉降（同向） | push-through-transition |
| 过曝翻页 | 推向证据物至 1.5x + 白色径向过曝（不对称包络：切前 10 帧升、切后 10 帧降） | 从亮心拉出 | overexpose-flip-transition |
| whip-pan 甩镜 | x 甩出 + blur 8 + 微旋 | **同向**进入，0.35s 刹住 + 二段回稳 | whip-pan-transition |
| 黑震切 | 定格闪光 → 最后 1 帧 opacity=0（hardOut） | lead:0 满亮进场，且开场自带运动 | black-slam-transition |
| 后拉冷却 | 一切沉入近黑 + 色温转变 | 全片唯一 scale<1 起步后拉 + rack focus | pullback-cool-transition |
| 粒子溶接 | 主体碎成粒子（index 确定性函数）上飘 | 下一场的粒子/星野承接同位置生成（物质连续性） | particle-weld-transition |

黑震切全片只许用一次，留给最大反转。**一个边界只用一式**；100s 的片 5~7 个边界，重复用同式比六式全上更有风格连贯性。

### 3.5 长镜头模式（one-take，转场的替代范式）

多镜头是剪辑思维，长镜头是空间思维：全部内容钉在一张世界画布的不同坐标上，
一台相机随讲述**连续运镜**过去，新内容在镜头快到时才成形——没有 Sequence 切换，空间连续性本身就是转场。
代码 `template/motion-systems/longtake.tsx`（WorldRig 站点表 + WorldPlane 视差 + WorldItem 钉点 + useArrive 接近度揭示），
选型与铁律见 `references/cards/long-take-world.md`。适合有空间/流程/时间线隐喻的段落；
可以整幕用长镜头、幕间仍走六式转场。长镜头不豁免让位规则，
运镜速度 ≤1.5 屏宽/秒，站点布局要防"途中穿帮"（相邻站点半成品入画）。

## 4. SHOTBOOK 规范（分镜必须写成层矩阵）

写层矩阵之前，先用 `references/shot-design.md` 的**三面分层工作单**（背景面/主体面/文字面
+ 各面动效菜单 + 七种镜头类型预设）把每个镜头的骨架定下来，再展开成逐节拍矩阵。

实现前必须产出 SHOTBOOK.md（完整范例见 `references/shotbook-example.md`）：

```markdown
### S3 · 25.04–43.24 · 意图：一个卡了46年的数字被顶开     ← 一句话意图
| 节拍 | Layer | 对象 | 动作 | 角色 |
|---|---|---|---|---|
| 36.08 卡在指数 | L3' | 0.5991 大数字 | 中心浮现；球群亮度−25% | 数字接任主体，环境让能量 |
| 41.52 零点六零四四 | L3'' | 0.6044 | 旧数字划线击落、新数字同帧punch入 | 单帧替换=英雄时刻 |
```

- 节拍列 = ASR 字级时间戳的锚字 + 绝对秒；**每行动作必须能回答"它在配合谁"，答不上来就删**。
- 每场景写一句意图 + 唯一主体接力线（谁让位给谁）。
- **每镜标题下第一行写「素材：」**（机器可读，`scripts/preflight.py` 逐个 stat）：
  `- 素材：V（public/broll/gpu.mp4）· 图（public/stills/a.jpg, public/stills/b.jpg）· 截图（public/pages/gh/page.png）· 文`
  代号同 taxonomy.md 输入类型索引（V = B-roll 视频 · 图 = 图片 · 截图 = 网页/界面证据 · 界 = 界面自演 · 文 = 纯文字 · 人 = 口播人物）；
  V / 图 / 截图 必须给路径，"待采"= FAIL；全片零 V / 图 = FAIL（实拍素材是必需项，SKILL.md ③）。
- 结尾附每镜相机方向（推 / 拉、起止 scale）和英雄时刻层数。
- **G0 必附「版式节奏表」**（2026-09-21 用户反馈"排版太固定"后加；写在逐镜矩阵**之前**——全片节奏摊在一张表里才看得出"八镜一个样"；
  `scripts/preflight.py` 按它核连续同态与容器种数，按各镜蒙皮行核同卡连用与占比）：

  ```markdown
  | 镜 | 人物形态·方位 | 素材容器 | 主卡 |
  |---|---|---|---|
  | s01 | 半身·右 | 无（文字左栏） | count-badge-title |
  | s02 | 角标·左下 | 装框·中 | split-60-40-story |
  | s03 | 离场 4s → 角标·右下 | 出血全屏 | bed + crash-zoom-punch |
  | s04 | 半身·左 | 无（金句） | quote-card |
  ```
  人物形态词表：半身 / 角标（左下 · 右下）/ 分屏格内 / 抠人贴角 / 离场；素材容器词表：无 / 出血全屏 / 装框 / 分屏格 / 底床 / 多图编排 / 3D 墙 / 长页。
  连续 3 镜同形态 + 同容器 = FAIL；同一张呈现卡连用 3 镜或全片 >1/3 = FAIL（§4.5 第 9 条）。
- **必填节「## 未完成 / 未采集清单」**：任何"本片不做 X"二选一——写进 §0 当设计决定（+依据），或写进本节（+阻塞原因 + 试过哪些兜底源）。
  允许内容为"无"，不允许缺节（preflight 查节存在）。它拦的是"未完成被包装成设计原则、进而成为不再被质疑的前提"。

### 4.5 排版预算（凌乱的克星，正主）

> 预算管"放多少"；**放哪、多大、怎么对齐**在 `references/layout.md`（栅格 / 间距令牌 / 对齐 / 居中 / 字阶 / 碰撞 / 底板配色 / 校验九项），两份一起核。

被判"凌乱"的镜头通常不是单个动效错了，而是**排版没有预算**——元素只进不出、四角+中带全占、同一信息写两遍。写 SHOTBOOK 时逐镜核：

1. **分镜按语义段落切**，禁止机械一句一镜；每镜只许一个 primary visual job
   （钩子/定义/数据/流程/对比/结论/CTA 之一）。
2. **枢轴句归下一镜**："但这次不是X"式转折/否定/设问是下一镜的**第一拍**——切镜点提前到枢轴句起点，
   旧镜先清场，开题动效（strike-and-replace/设问框）上干净的舞台，不叠在旧话题的满画面上。
3. **同屏预算**：任一时刻主体组 ≤3（字幕/常驻件不计；**降权留守的元素计入**）；
   第 4 组进场前必须有一组真退场。层矩阵加一列"同屏计数"自检。
4. **留白锚**：每镜全程保留至少一个空象限；四角+中带全占的环形满盘 = 画心空洞、视线无路径，判凌乱。
5. **hero 造型一屏一个**：多个数字/大字同屏时只有一个享受 hero 档造型（大字号/色块/换色），
   其余降行内注——三个数字三种 hero 造型互相抢戏读作凌乱。
6. **画面文字不照抄字幕**：画面文字是 ≤12 字的提炼，不是口播誊写；与字幕整句重复 = 同一信息双份同屏。
7. **布局事件预算**：人物形态切换/构图重排这类布局级变化每分钟 2–4 次，"切换是标点不是节拍器"——
   合法触发只有新论点/图表替换/前后对比/结论；纯时间流逝、每条字幕都不算。
8. **错峰三段序（正主）**：旧面板**完全退场** → 人物换位/新主体入场 → 新面板才淡入，三者不得交叠。
   人物在场的镜头先跑 `scripts/face_bbox.py` 定人脸安全区（口径 host-footage.md §3），主信息面板放人物对侧。
9. **版式轮换预算（2026-09-21 用户定版：成片"后面大部分都是人物在左下角、素材在中间的方块、右边放文字，过于固定"）**：
   1–8 条管一镜之内，这一条管镜与镜之间——"每镜都对"不等于"整片好看"，11 镜 8 镜同一张 60/40 卡就是每镜都过了闸的成片。
   - 同一张**呈现类卡**（素材呈现 / 人物互动 / 数据信息图 / 运镜）不得连用 3 镜（连 2 镜可以，第 3 镜必须换式），全片占比 ≤1/3（≥6 镜的片）；
   - **人物形态 × 方位**（半身 / 角标左下 / 角标右下 / 分屏格内 / 抠人贴角 / 短暂离场）与**素材容器**（出血全屏 / 装框 / 分屏格 / 底床 / 多图编排 / 3D 墙 / 长页）
     两个变量连续 3 镜至少换其一，两者都不变 = P1；≥8 镜的片素材容器至少三种。单条 B-roll 按 shot-design.md §2⑦ 七式选、相邻镜不同式；多素材按 §2④′ 关系表；
   - 同一条 B-roll 文件不进相邻两镜、全片 ≤2 镜（换素材或 `ffmpeg -ss` 换取景段）；版式行逐镜实测，不许复制上一镜的；
   - 与第 7 条的关系：**轮换是换构图，不是加运动**——切镜处换版式本来就是一次布局事件，不额外制造人物往返，每分钟 2–4 次的上限仍在；每一式内部仍只有相机极缓推拉。
   机器闸：`scripts/preflight.py` 按 G0 版式节奏表（§4）+ 各镜蒙皮行核——连用 / 占比 / 连续同态 FAIL，版式行复制 / 素材复用 / 缺表 WARN。

- **纯文镜的陪衬图形**（2026-09-07）：素材行只有「文」的镜头，层矩阵必须多一行「G5 陪衬图形 ← 关系一句话」（`references/schematic.md` §1）；只有文字动效在堆 = 幻灯片，preflight 给 WARN。

## 5. 验收口径（渲染后逐条核）

1. 英雄帧活跃层 4–6；任意静息帧**相机在动**（极缓推进或拉出；不再要求 ≥2 层）
2. **任意 1 秒抽帧不允许全静止** —— `python3 scripts/motion_check.py <video>` 自动检测（工具默认阈值 0.8s，严于 1s 口径），FAIL 必修
   - 有两类**卡定版要求的静止**会撞这一关：`logo-enter◇`「落定即终帧、不加 idle」、
     `stage-keyframe-tour◇`「hold 必须真静止」。**处置不是豁免，是让场景相机替它动**
     ——相机极缓续推/续拉，卡本体一个像素不动（实测可从 FAIL 转 PASS）。
3. **每个镜头边界都有明确转场处置（对照 SHOTBOOK 逐边界核，禁止裸切）**；转场处前后镜头运动方向连续（黑震切除外）
4. 锚点→帧量化误差 ≤16.7ms（30fps）；不宣称 <5ms（那需要 120fps）
5. 一个节拍只有一个主角；说完必须让位，不许堆积满屏（让位方式三选见 §2 G3，降权留守计入同屏预算）
6. 排版预算（§4.5）逐镜核：同屏主体组 ≤3、空象限在、hero 造型唯一、画面文字与字幕无整句重复、
   人脸安全区全时刻未被侵入（**文字的背景也算侵入**）
7. **网页证据无一处静态贴屏**：每个网页 / 长页类镜头对照 SHOTBOOK 核出它的拍法
   （滚 / 巡 / 放大 / 划 / 推之一，shot-design.md §2④）与坐标来源（`targets.json`）；静态截图当该拍主体 = P1
8. **字与画同起同收**：每镜最后一个退场结束 = 镜尾；镜尾之前不许出现"文字已退、底床 / 素材独自空转 >0.4s"；
   多素材镜头核关系 → 版式是否对（shot-design.md §2④′），并列句核一镜一式与三项逐个出现（layout.md §7.1）
9. **版式在轮换**（2026-09-21）：相邻三镜定妆帧连看，人物形态 × 方位或素材容器至少换过一次；同一张呈现卡没有连用 3 镜、全片没有一张卡 >1/3——
   评审看到"又是左下圆章 + 中间方框 + 右边文字"即记 P1（§4.5 第 9 条；对照 SHOTBOOK G0 版式节奏表）

## 6. 工程铁律（从可工作代码中提炼）

- anime.js v4 桥（anime-remotion.ts）：`engine.useDefaultMainLoop = false`；useLayoutEffect 建 timeline（autoplay:false）+ 每帧 `tl.seek(((frame-lead)/fps)*1000)`——seek 必须在 Remotion 截帧前同步完成。
- three.js 桥（three-anime.ts）：裸 WebGLRenderer + `import 'animejs/adapters/three'`；渲染顺序 seek → onCamera → render；remotion.config 需 `setChromiumOpenGlRenderer('angle')`。
- **零 Math.random**：一切随机走 `rand(seed)` sin-hash / index 取模 / 双正弦。
- **"永不发生"的哨兵用有限大数，不用 `Infinity`**（`const NEVER = 1e6`）：
  `until = Infinity` / `outAt ?? Infinity` 一旦进了 `interpolate` 的 inputRange，
  Remotion 第一帧就抛 `inputRange must contain only finite numbers`——是硬错误不是静默降级。
- **相机曲线的末键要落在片尾之外**：CameraRig 所有轨都走 `Easing.inOut(Easing.sin)`，
  **终点速度为零**。末键正好压在片尾时，最后 0.8~0.9s 会慢到停死，motion_check 照样报静止
  （实测）。把末键推到片长之后（值也随之外推），曲线就永远不在片内收住——
  这与运镜类「相机永不静止／不能用 power2.out」是同一件事，只是发生在**相机表**上。
- **新写卡片组件默认带 `if (abs < at) return null`**：少了它，组件会在整镜开头就以 p=0 的
  样子挂在屏上（实测比自己的锚点早 4.5s 显形）。
- **细密纹理禁入相机缩放层**（2026-08-28 实战定版）：特征 ≤2px、间距 ≤24px 的点阵/细网格
  放在被相机连续缩放的层里会亚像素爬行，整块读作"画面在抖"。要么把特征放大
  （点径 ≥2.5px、间距 ≥32px），要么把纹理挪到屏幕空间静态层（CanvasBands 一类）。
- **失焦（blur）出场只在深底成立**：浅底上出场侧加 blur 会叠上下一镜交叠的白纱，
  整页读作"变糊"而不是"冷却"——与「浅底白闪失效」同理，浅底出场只走 ShotFade + 极轻回缩。
  顺带：镜内的收尾运镜（拉远/回正）要在交叠开始前**停稳**，拉远中间态 + 白纱叠着必糊。
- **场景代码里的绝对秒只许出现在具名 props 上**（`at=` / `demoteAt=` / `tl(...)`），
  不要写进 `ease(abs, 106.9, ...)` 这类函数实参——重映射/重剪工具按语法位找锚点，
  函数实参里的字面量是批量改期时最容易漏的一批（v4 实测 31 处漏改直接产出 P0）。
- anime 目标元素初始 `opacity:0` 写在内联 style（防 timeline 未 seek 时闪现）。
- lead 补偿统一走一处：现成件 `motion-systems/time.ts`（useAbs/useToLocal）。三种时间基——绝对秒（SHOTBOOK 真相源）/ shot-local（CameraRig/WorldRig 内部）/ Sequence-local（Live/Defocus/粒子等模板件，含 lead）——场景组件一律经 time.ts 换算，别各算各的（已知易错点：Counter 的 startSec 要加 lead/fps）。
- 时间以**绝对秒**为分析真相源，只在 Remotion 边界换算一次帧；不要提前取整。镜头 ≠ 句子（聚合多句）时锚点一律写绝对秒字面量，tSay 的句级 scene-local 只在单句镜头里用。

<!-- ===== /file: video-talkcraft/references/cinematography.md ===== -->

<!-- ===== file: video-talkcraft/references/demo-spec.md ===== -->

# Demo 与配方卡编写规范

本库约定（2026-08-28 定版）：每个动效 = 一张配方卡（markdown）+ 一份自包含 Remotion tsx 源码
+ 一个可运行 HTML demo。**tsx 是 skill 引用的正主**（复用成本最小：复制单文件进 Remotion 工程即可用），
HTML demo 是免构建预览（浏览器直开、画廊活播）。卡片讲清何时用、参数怎么调。

## 目录约定

```
references/cards/<slug>.md     # 配方卡（frontmatter `代码:` 指向 tsx）
template/cards/<slug>.tsx      # 自包含 Remotion 源码（skill 首选引用，见下方 tsx 硬性要求）
demos/<slug>/index.html        # 自包含 HTML demo（可引用 ../_lib/ 下共享资源）
demos/_lib/                    # gsap.min.js / lottie.min.js / demo-shell.css / demo-shell.js
                               # + sfx.js（WebAudio 合成音效引擎）/ sfx-map.js（逐卡 cue 表）
```

**实战卡**：从已交付项目沉淀的动效，其生产母本在 `template/motion-systems/` 或
`template/components/`（"复用指引"里写清组件文件与关键 props）；`template/cards/<slug>.tsx`
仍然要有（与 demo 同画面的独立版本）。

## tsx 源码硬性要求（2026-08-28 定版）

1. **单文件自包含**：只 import `react` 与 `remotion`；不 import template/ 其他文件、不引外部资源
   （图标/占位一律内联 SVG/CSS）。演示语境素材（数字人、实拍手）经可选 prop 注入
   （`hostSrc?/handSrc?: string`），不传时灰阶剪影/矢量兜底。
2. **导出契约**：`export const meta = { width, height, fps: 30, durationInFrames }` +
   default 导出组件；CONFIG 常量顶置（与 demo 的 CONFIG 同名同注释）。
3. **纯函数渲染**：一切状态由 `useCurrentFrame()` 推出；禁 `Math.random`/`Date.now`/自跑动画，
   随机用 remotion 的 `random(seed)`（canvas 卡允许 `useEffect` 依赖帧号逐帧全量重画）。
4. **与 HTML demo 逐帧视觉一致**：demo 是视觉真值。**改 demo 时序/画面后必须同步改 tsx**
   （与 sfx cue 表同一条纪律）。

## Demo 硬性要求

1. **单文件**：所有样式和逻辑写在 `index.html` 内，只允许引用 `../_lib/` 下的共享文件。禁止外网 CDN（demo 必须离线可开）。
2. **统一外壳**：引入 `../_lib/demo-shell.css` 与 `../_lib/demo-shell.js`，内容画在 `<div id="stage">` 里，统一 960×540 标准舞台。
   **动效与画幅无关**：卡库的重点是动效效果的复刻——同一个动效理应能应用到横屏或竖屏，
   画幅是应用工程的容器属性，不是动效的属性。demo 不分横竖屏；画幅相关的落位规则
   （字幕位置、安全区）由 design-language.md §5 在应用侧管。demo 本身不放字幕、也不受字幕带约束；但卡的「落位自检」若承诺"不入字幕带 / 离画幅边 ≥48"，demo 几何就必须真的满足（评审判例：crash-zoom / scanline 首版卡底 495 / 464 与自检矛盾）——承诺不了的写成成片侧处置（字幕改落位 / 主体压高），不留与 demo 不一致的承诺。
3. **注册运行函数**：`DemoShell.register(({speed}) => { ... })`——每次调用必须从头重建动画（重播语义）。GSAP demo 用 `tl.timeScale(speed)` 支持慢放。
4. **有口播语境，但不带旁白字幕（2026-08-23 定版）**：动效不要孤立地演——舞台里放口播场景占位
   （`.host-placeholder` 主持人 / 假截图卡片等），让人一眼看懂"这个动效作用在什么上"。
   但 demo **不放旁白/台词字幕**：字幕不是动效本体，会把观众视线从动效上引走；
   demo 聚焦动效本身。例外：动效本体就是字幕（字幕花字类卡）时，那些字就是动效对象，保留。
   占位素材一律用 CSS/SVG 画，不引外部图片。
5. **技术选型**：优先 GSAP（`../_lib/gsap.min.js`）或纯 CSS/SVG/Canvas。动效本体的代码要**可摘走**：核心动画逻辑集中成一段、参数写成顶部常量（`const CONFIG = {...}`），别人复制这一段就能用。
6. **文案用真实感示例**：字幕/标题用像真的口播台词的中文（或英文卡用英文），不要 "Lorem ipsum" 或 "示例文字"。
7. **自验**：写完必须运行 `node scripts/verify-demo.mjs <slug>` 直到 ok=true 且无 warnings，再用 Read 查看 `tools/.verify/<slug>-t0/t1.png` 两张截图，确认视觉上符合卡片描述（不是黑屏/错位/字压字）。
   **瞬时判据要单独截帧验（2026-08-25 加）**：t0/t1 是随机撞上的两个时刻，抓不住"点击那一帧光标有没有压在按钮上"
   这类**只在一帧成立**的判据（x-follow-card 的"鼠标没点到关注上"就是这么漏过去的）。凡是卡里写了
   "同帧发生""点击那一刻""光标落在 X 上"的，用 `node scripts/shot-at.mjs <slug> <t>` 把时钟冻在那个时刻上截图核对；
   收尾状态看着不对时用 `--play` 复核（seek 不重放中间帧，多条 tween 共写一个对象时次序不保证，
   `--play` 才是观众真正看到的画面）。
   **人物不许截断/贴边（2026-08-25 用户定版）**：数字人不能被左右画框切掉任何一部分，也不能贴着左右边框（呼吸边 ≥10px）。**修法是把人物整体往画面中间挪**（改容器定位、给足宽度），**不是缩小人物**——人物的大小是画面语言的一部分，不许为了塞进容器而变小。挪进来之后**人物也不能压住其他内容**（标题、卡片、图表等动效本体）；两头都放不下时调版面（内容让位、收窄内容列宽），不是牺牲人物。verify 工具自动检查截断/贴边并发 warning。**刻意特写/裁剪**（画中画放大、chip 裁切窗等）在裁切容器上加 `data-crop-ok` 豁免，并在卡片"动效范围"里写明这是取景语义。人物容器（.host-wrap/.host-col）定位时留出边距，不要用负 right/left 把人推出画外。
8. **音效 cue（2026-08-24 起）**：每张新卡要在 `demos/_lib/sfx-map.js` 里登记 cue 表——
   `"<slug>": [{ t, name, vol?, dur?, rate? }, ...]`，t 是 speed=1 的 demo 秒，name 取
   `_lib/sfx.js` 的 13 个音色（whoosh/swipe/pop/click/tick/slam/riser/ding/scratch/typekey/paper/ping/lowpad）。
   其中 10 个音色有**真实采样**（2026-08-25 起，源自 video-shotcraft 的 Mixkit 库，
   base64 内嵌在 `_lib/sfx-samples.js`，来源与再生成见 `_lib/sfx/ATTRIBUTION.md`）；
   引擎采样优先、合成兜底，riser/ping/lowpad 仍是纯合成。cue 写法不变。
   采样是异步解码的，引擎会在 `sfx-samples.js` 就位时就抢先解码，并且对"声明过但
   还没解码完"的 `pk:` 采样挂起重试（最多 1s）而不是丢掉——**全采样的卡**（一个合成音
   都没有）否则会整卡无声，2026-08-26 修。
   每卡 2~6 个 cue（连发 tick/typekey 除外），只跟动效命门拍，微动/漂移不配。
   demo 页面零改动——外壳按 GSAP 时钟派发，暂停/慢放/重播/seek 自动同步；
   声音只在主屏（`?embed=1&controls=1`）和独立打开时生效，画廊小窗静音。
   **改 demo 时序后必须同步改 cue 的 t**。

   （历史注：cue 表由库作者的本地配音台工具逐卡调配写回，工具不随库分发；cue 的两个可选字段
   `clip`——只放前 N 秒、末尾 40ms 淡出，长采样配短动效必截——与 `note`——备注配哪个动作，
   引擎忽略——由此而来。）

   **全库定音（2026-08-26 用户定版，当时 80 卡、现 78）**：逐卡重配后 cue 总数
   439 → 269，音量上限压到 0.65，90% 的记数改走真采样。定下来的口味：
   - **少而准**：同一时刻不叠两记（原来"slam+whoosh 同帧"这类一律砍到一记）；
     人名条/纯转场只留 1 记极轻的，或干脆静音（`caret-wipe-transition`、
     `orbit-drift` 是有意的空 cue 表——闭合循环的卡配了声会随循环反复响）。
   - **不要收尾叮当、不要重砸**：`ding`/`slam` 两个音色在全库已清零（音色还在，
     新卡别再用）；转场只留前面的 `riser` 蓄势，落点不配。
   - **语义对位**：打字 = **一记** `pk:text-keyboard` 用 clip 盖住整段（不是逐键梯子）；
     流式输出/进度 = `pk:data-data-load-os`；画线 = `pk:text-marker-pen-line`；
     卡片滑动 = `pk:paper-paper-slide`；弹出 = `pk:ui-pop`；点击/逐项点亮 =
     `pk:ui-ui-click-tone`；计数落定/咬合 = `pk:mech-lock-quick`；冲击 =
     `pk:impact-hit-fast-exciting`；运镜空气声 = `pk:transition-air-whoosh-powerful`
     压到 vol ≤0.3 当底噪。对照表见 `_lib/sfx/ATTRIBUTION.md`。
   - 连发梯子（计数/逐字/逐行）保留原来的 vol/rate 递增，只换音色。

   **制作端桥（2026-08-27 起）**：cue 表不只服务 demo——**做片选了某张卡，它的音效也要跟着上**
   （SKILL.md ④⑤）。`node scripts/sfx_dump.mjs` 把内嵌采样解码成 `remotion/public/sfx/*.mp3`，
   SHOTBOOK 抄 cue（卡内相对秒 → 绝对秒）后在场景里用 `<Audio>` 逐条摆放。

## 配方卡格式（frontmatter + 五节）

```markdown
---
name: <slug>
标题: <中文卡名，2~8 字>
一句话: <视觉上发生什么，一句话说完，含关键时序感>
适用: <口播里的什么时机；什么调性>
时长: <典型总时长与关键节拍>
能量: 低 | 中 | 高
类别: <分类名>
优先级: P0 | P1 | P2
参考: <哪些主播/频道在用，逗号分隔>
---

## 输入类型
| 口播视频 | B-roll 视频 | 图片 |
|---|---|---|
| 可否 + 理由 | 可否 + 理由 | 可否 + 理由 |

## 常用场景
1. <demo 演的那个场景>  2.~4. <其他三个高频场景>

## 意图
为什么口播需要这个动效（解决什么叙事问题），以及做对的命门 2~3 条。

## 动效核心
元素 + 运动 + 时序（帧/毫秒）+ 缓动 + 层级，工程师看完能直接实现。

## 参数表
| 参数 | 典型值 | 调节手感 |（每个参数写"调大/调小会怎样读"）

## 已知坑
最容易做假/做俗的错法，各写一句"为什么一眼假"。

## 复用指引
- HTML/GSAP：demos/<slug>/index.html，改哪些常量即可换文案/换色
- Remotion 移植要点：帧驱动写法、interpolate 对应关系
- 剪辑软件对应物：剪映/AE/CapCut 里叫什么、哪个内置功能可替代
```

「输入类型」与「常用场景」两节（2026-09-05 起新卡必填）：前者三列各写这张卡吃不吃口播人物 / B-roll 视频 / 图片及理由（放在哪一层），
后者四条里第一条就是 demo 演的场景。老卡的输入类型见 `references/taxonomy.md`「输入类型索引」。选卡时这两节与「落位自检」一起进 SHOTBOOK（SKILL.md ④）。

## 视觉基准（中性化契约，2026-08-23 定版）

demo 的使命是**让动效可被无损复用**：其他 agent 复用一张卡时，拿走的应该只是
"这张卡带来的动效"，能以最简单的方式迁移到任何风格、任何尺寸。中性化的另一半在应用侧：
成片开工先按口播稿领域定风格档，卡复制进工程后**按风格档蒙皮**（design-language §0.4）——demo 的皮不是成片的皮。因此：

1. **白舞台默认**：`#stage` 统一白底（demo-shell 默认 #ffffff）。动效本身语义上需要
   非白底才成立时才允许例外（如过曝转场需要深色内容对比、纸面手绘需要纸色），
   例外必须在卡片"动效范围"节里写明理由。
2. **零装饰风格**：demo 里不允许出现与动效无关的风格元素——不加装饰性渐变/网格/
   噪点/暗角/品牌色板。文字用黑 #1d1d1f、辅助灰 #8a8a8a；动效**语义上必需**的颜色
   （荧光笔黄、警示红、高亮色）保留，但只用在动效本体上。

   **产品界面卡例外（2026-08-25 用户定版）**：卡演的是**某个真实产品的界面**时（x-follow-card /
   chat-gpt / claude-code / glass-code-walk 这一类），**必须完全还原该产品的样式**，不做中性化——
   配色、圆角、间距、字体气质、品牌色、标识全部照抄源码（remocn registry 的 `THEMES` + `accentColor`），
   目标是"截图放在真产品旁边分不出来"。理由：这类卡里**产品皮就是内容本身**——观众要一眼认出
   "这是 X 上的某个人""这是 ChatGPT 而不是别的聊天产品""我真的让这个工具干过这个"；
   灰阶化之后卡变成"某个社交卡/某个聊天框/某个终端"，指向性没了，卡的存在理由也就没了
   （chat-gpt 灰阶化后就退成"某个聊天框"，它那五条界面语法特征全部读不出来）。
   **可编辑的是内容**（文案、名字、命令、回答），外观不动。
   这类卡要在"动效范围 · 底色要求"里写明"产品皮 = 内容本身，2026-08-25 用户定版：完全还原产品样式"，
   并在"不属于本卡的"里点明**皮属于内容而不是可换的风格**（与其他卡相反）。
   注意：这不是"可以引品牌资源"——图标仍然一律内联 SVG 自己画，禁外网资源不变。
3. **占位物极简**：口播语境占位（截图/图表等）用最低限度的灰阶线框表达，
   让人看懂"动效作用在什么上"即可，不做拟真质感。
   **主持人例外（2026-08-23 定版）**：`.host-placeholder`（或任意元素加 `data-dh-host`）
   由 demo-shell 自动注入数字人 alpha 视频（`_lib/dh-host.webm`，Safari 用 .mov），
   加载失败自动退回灰阶剪影。数字人是**演示语境素材**，不属于任何卡的动效本体——
   卡片"动效范围"节的"不属于本卡的"默认涵盖它。素材来源与再生成方法见
   references/host-footage.md。
4. 缓动默认 `power2.out` / `power3.out` 起步；夸张弹跳才用 `back.out`/`elastic`。
5. 中文字体栈：`"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif`。
6. 不做 line boil / 定格抖动（用户定版，design-language.md §4）。

## 「动效范围」节（每张卡必填）

配方卡在五节之外**必须**加一节 `## 动效范围`，明确这张卡"带来的动效"边界——
复用者据此知道拿走什么、丢掉什么、改什么：

```markdown
## 动效范围
- 属于本卡的：<动效本体清单——运动、时序、缓动、层级关系，逐条列>
- 不属于本卡的：<demo 里仅作演示语境的部分——占位物、示例文案、具体配色、字体字号>
- 迁移接口：<换风格/换尺寸时改哪些参数——颜色 token、尺寸基准、时长缩放规则>
- 底色要求：<白底即可 / 需要 XX 底色（理由）>
```

## 卡片「落位自检」节（2026-09-05 用户定版）

有目标锚点的卡（强调标注类全部、pip-zoom-box、取景框 / 圈注 / 下划线 / 箭头 / 放大镜）在 `references/cards/<slug>.md` 末尾必须有
「落位自检」节：标注几何由目标实测包围盒反推、留白 16~24 等距、定妆帧核偏差 >8px 返工。适用对象有限制的卡（如 gooey-morph 只用于图）
与有配色纪律的卡（如 chapter-title-card 按章换色）同样写成独立小节。**这些小节是 skill 选卡时的必读项**（SKILL.md ④「选卡必读卡经验」）：
选中即抄进 SHOTBOOK 该镜的自检列，实现后逐条核——写在卡里但没进 SHOTBOOK 等于没写。

<!-- ===== /file: video-talkcraft/references/demo-spec.md ===== -->

<!-- ===== file: video-talkcraft/references/design-language.md ===== -->

# 视频设计语言（默认版式系统 · Apple 范式）

参照 Apple web 设计范式改写为 1080p 视频用的设计语言。
**适用条件：这是"用户没有明确风格要求时"的默认骨架，不是 skill 的强制要求**——
用户点名了风格（综艺感/赛博/纸面手绘/某个品牌的调性…）就按用户的来，整套替换；
本文件的硬约束只剩一条对任何风格都成立的：**替换的也必须是一套完整 token，不允许逐场景随手取色**。
无明确要求时：新片开工先按 **§0 从口播稿判定领域、派生本片风格档**（骨架不变、皮随领域），再按本文件定 token 落成工程里的 `theme.ts`。

## 0. 领域定风格：从口播稿到风格档，再到卡的蒙皮（正主，先于色板）

库里的动效卡是**无风格的中性 UI 呈现**（demo-spec「视觉基准」：白舞台、零装饰、灰阶占位）——这是为了让动效可无损复用，
但也意味着**直接照搬 demo 的皮进成片就是"PPT 贴片"**：一支讲宋代瓷器的片里出现发丝线白卡 + 蓝色 accent 的图表，动效再对也读作错片。
所以开工第一步不是选卡，是**定这支片的领域与风格**，然后每张卡按风格档蒙皮。

### 0.1 判定领域（读完全稿再答，写进 SHOTBOOK §0）
三问：① **讲什么**——主题词、专有名词密度、数据 / 引用 / 案例的比例；② **对谁讲**——受众是同行、大众、学生还是消费者；
③ **什么口吻**——教学、评测、观点、叙事、新闻。领域写成一个词 + 一句依据（"财经 · 全稿 11 个数据点 + 3 次引用财报，口吻是解读"）。
拿不准时按主导段落定；跨领域的片取一个主导领域，另一领域只在相关幕里借它的图表 / 素材语言，不换整片色板。

### 0.2 领域 → 风格档（示例行，不是穷举；同一领域可有多档，选最贴近口吻的）
| 领域 | 底色策略 | accent / 底色倾向 | 字体气质 | 材质 & 卡片造型 | 图表 / 数据语言 | 素材 & 底床气质 | 能量 |
|---|---|---|---|---|---|---|---|
| 科技 · AI · 开发者 | 浅底默认，代码 / 终端用深 tile | 冷蓝或品牌色；深 tile 近黑 | 几何无衬线，数字等宽 | 发丝线卡、圆角 12~16、玻璃 / 深 tile | 极简折线 + 网格淡、`tabular-nums` | 录屏、终端、界面截图 | 中 |
| 财经 · 商业 · 数据解读 | 羊皮纸浅底，或藏蓝深底幕间反差 | 墨蓝 / 深绿；涨跌语义色只进图表 | 无衬线正文 + 衬线大标题（报纸感）可选 | 纸感白卡、表格线、少圆角 | 坐标轴齐全、刻度真、数字等宽、单位后置 | 报表 / K 线 / 新闻截图、城市人流底床 | 低中 |
| 教育 · 科普 · 知识 | 白 / 羊皮纸 | 暖橙或青 | 圆润无衬线 | pastel 底板 chip、手绘圈注、铅笔线 | 图形化优先（点阵比例、示意图、步骤条） | 插图、示意 B-roll、板书感 | 中 |
| 生活 · 消费 · 测评 | 暖白 | 品牌色或暖色 | 中性无衬线 | 白边照片卡 + 唯一投影、圆角 20+ | 评分 / 对比表 / 表盘 | 实拍产品、使用场景 | 中 |
| 人文 · 历史 · 文化 | 羊皮纸 ↔ 深墨底交替 | 朱砂 / 靛青 / 金 | 宋体 / 楷体气质标题，正文无衬线 | 纸纹、墨迹、手写下划线、无投影 | 时间轴、地图、少用现代图表 | 老照片、文物、水墨底床 | 低 |
| 健康 · 医疗 · 心理 | 白 + 淡青 | 青绿 | 圆润无衬线 | 大圆角、少描边、柔和底板 | 简化图示、比例点阵 | 实拍人物柔化底床 | 低 |
| 职场 · 效率 · 方法论 | 羊皮纸 | 蓝或墨黑 | 无衬线 | 清单卡、便签、步骤条 | 流程图、步骤条、勾选 | 录屏、文档截图 | 中 |
| 娱乐 · 游戏 · 泛资讯 | 近黑或高饱和底 | 高饱和撞色 | 粗无衬线 / 斜体 | 硬边 slab、色块、描边卡 | 计数、排行、砸字数字 | 游戏画面、弹幕、梗图 | 高 |

档只给方向，具体值仍按 §1~§4 的 token 纪律落地：一个 accent、一个投影、两档字重、底色交替分幕、运动做减法——**骨架是 Apple 范式，皮是领域的**。
深底主导 / 高饱和底属于偏离浅底默认的选择：在 SHOTBOOK §0 写明领域依据**并经用户确认**后才执行（确认闸保留，用户 2026-09-06 定版；共同创作在 SHOTBOOK 评审时确认，自主模式也要在开工前问一句）；"科技话题"本身不构成深底理由（科技档给的是材质与图形语言，不是"科技 = 黑底"）。

### 0.3 风格档写法（SHOTBOOK §0 第一块，`G0 风格档`）
```
G0 风格档
- 领域：财经 · 解读口吻（依据：11 个数据点 / 3 次引财报 / 受众大众投资者）
- 底色策略：羊皮纸 #f5f5f7 主导；第 3 幕（反转）深底 #0f1e3d
- token：accent #1f4e8c · ink #1d1d1f · dim #7a7a7a · 涨 #248a3d / 跌 #d70015（只进图表）
- 字体：标题 "Source Han Serif" 600 / 正文 PingFang SC 400 / 数字 tabular-nums
- 材质 & 卡：纸感白卡（1px #e0e0e0 描边、圆角 12、无投影）；证据截图白边卡 + 唯一投影
- 图表：坐标轴 + 刻度齐全，网格 #ececf0，折线 3px accent，标记圆点，单位 caption 阶后置
- 素材 / 底床：报表 / 新闻截图；B-roll 用城市人流双色调底床（design §1.2）
- 能量：低中；不做的事：不用 pastel chip、不用手绘圈注（换成红框 + 表格高亮）
```
派生 `theme.ts`（§7）与幕底选型（§1.1）都从这一块出；用户点名了风格时，这一块直接写用户的风格并覆盖领域档。

### 0.4 中性卡蒙皮契约（应用侧，每张选中的卡都过一遍）
`template/cards/<slug>.tsx` 复制进工程后，**按风格档改皮、不改命门**：
- **不动（动效本体）**：时序与缓动、三段式、几何比例与相对位置、运动方向与层级顺序、音效 cue。`scripts/card_lint.py` 的相似度阈值 0.55 就是给蒙皮留的余量——改皮过得了，重写运动才会掉下去。
- **必换（皮）**：颜色 → 全部换成 theme token（demo 的 #0066cc / #e3e3e8 等一律不留）；字体栈与字重 → 风格档；圆角 / 描边 / 投影 / 材质（发丝线卡 ↔ 白边卡 ↔ 纸卡 ↔ 玻璃 / 深 tile）；
  **图表类**的坐标轴、网格、标记形状、数字字体、单位写法；**卡片类**的占位图形换真素材或风格化图形；图标线性 / 面性全片统一。
- **随语义不随风格**：卡自带的语义色（荧光笔黄、涨跌红绿、警示红）不换色相，只按风格档调饱和度档；**产品界面卡**（chat-gpt / claude-code / x-follow-card 这类，皮即内容）不蒙皮（demo-spec 已定）。
- **一致性**：同一片内同类卡共用一套皮——所有卡片一种造型、所有图表一种坐标轴语言、所有 chip 同高同圆角；**视频容器边框一片只用一式**（`theme-frame.tsx` 八式按调性选，§1.3；"一式"指**边框造型**，不指容器的尺寸 / 位置 / 占比——出血全屏、装框、分屏格、底床、多图要按镜轮换，cinematography §4.5 第 9 条），装饰线与装饰字 = 本片 ink；**章节卡四张同一套字体与版式、但每章底色 / accent / motif 不同**（"同族不同章"——一致的是造型语法，轮换的是章色与主题纹样）；蒙皮清单写在 SHOTBOOK 该镜的**蒙皮行**（`卡名 → 改了什么皮`），与版式行并列，实现后抽定妆帧核"像不像这支片的东西"。
- **反例**：中性白卡直接进人文片（贴片感）；每张卡各自留 demo 色（第二强调色）；三张数据卡三种坐标轴；把风格做到运动上（人文片就放慢缓动、娱乐片就加弹跳——能量档只管入场用力与密度，不改卡的时序命门）。

核心气质（从 Apple 范式继承的四条骨架）：
1. **内容即主角，版式退后**——没有装饰性渐变、没有花边框；靠留白和底色切换分段，不靠线条。
   （唯一例外：§1.1 背景菜单的 12 款幕底——浅 `pastel-mesh-flow` / 深 `mesh-flow-dark` 为默认，其余按幕启用。）
2. **全片只有一个强调色**——所有"看这里"信号（关键词、划线、标注、CTA）用同一个 accent。
3. **全系统只有一个投影**——只给"证据素材"（截图/照片/实拍）用，卡片和文字永远不加投影。
4. **底色交替就是章节感**——浅底 ↔ 深底的幕间切换本身是分隔符（对应 env.tsx 的 ACTS 分幕表）。

## 1. 色板

双模式：**默认主导模式 = 浅底**（Apple 的本色：白/羊皮纸 + 墨字 + 安静蓝）。深底只做幕级反差
（金句幕/反转幕/代码演示幕整幕换深 tile）。深底主导或其他底色策略由 **§0 风格档**按领域决定，
在 SHOTBOOK §0 写明领域依据**并经用户确认**——"科技话题"本身不构成深底理由（§0.2）。

| token | 浅底模式 | 深底模式 | 用途 |
|---|---|---|---|
| canvas | `#ffffff` | `#1d1d1f` | 主画布 |
| canvas-alt | `#f5f5f7` 羊皮纸 | `#272729` / `#2a2a2c` | 交替幕底色（相邻幕之间的微阶差） |
| ink | `#1d1d1f` | `#f5f5f7` | 标题与正文 |
| ink-muted | `#7a7a7a` | `#a1a1a6` | 次要信息、来源行 |
| hairline | `#e0e0e0` | `rgba(255,255,255,0.14)` | 卡片 1px 细线（代替投影做层级） |
| **accent** | `#0066cc` | `#2997ff` | **唯一强调色**：关键词换色、划线、标注引线、图表主系列 |
| positive / negative | `#248a3d` / `#d70015` | `#30d158` / `#ff453a` | **只进图表和涨跌标注**，不做版式色 |
| marker | `#FFE949` @60% multiply | 同左（screen 模式） | 只给荧光笔扫词 |

红线：accent 之外不允许出现第二个"看这里"色；语义色出现在正文/标题上即违规。背景层的氛围色（§1.1 幕底团色、`flying-words` 词云的多色相）是氛围不是信号，不计入这条红线——它们只能待在 L6 背景层，前景仍只有一个 accent。
深底模式的底色是 Apple 的**中性近黑**（#272729 系），不是深蓝，且不加装饰网格。
`template/motion-systems/theme.ts` 的深空蓝科技风（#070B14 + 青网格 + 辉光）是 **legacy 变体**，
视觉气质不属于本设计语言——仅当用户点名要科技风时可用，并在 SHOTBOOK §0 声明。

**浅底的"能量"手法**（深底辉光/曝光语法在白底上无效也不 Apple，替换为）：
层级与重音靠底色阶差、发丝线、accent 描边/换色、punch 缩放、唯一投影；纯文字镜的"第二层可看的东西" = G5 线稿示意图（ink 3px 描边 + accent 强调 + 磨砂白板托底，`references/schematic.md`），不是渐变、网格或辉光；
环境层 = 极轻**静态** vignette（`rgba(0,0,0,0.06~0.12)`，属幕底配方）；暗压脉冲与扫光不做（运动减法）；深色代码面板/终端窗按"深 tile 卡片"处理（Apple 允许黑色 video frame），自带层级无需辉光。

浅底两条实测红线：
- **转场白闪在浅底失效**：白底基线亮度 ≈237，再叠 0.34 白闪无处可涨（深底同表有 +29 亮度峰，浅底实测无峰）。
  过曝翻页式在浅底一律反向做**暗压闪**（切点一拍 6~10% 全场变暗 3~4 帧再回弹），或 2~3 帧纸白硬切到 255。
- **dim 件禁止再叠 opacity**：`#7a7a7a` 在白底只有 4.29:1 余量，叠透明度必掉出可读区
  （实测字幕未读词叠 opacity 后 2.06:1）。未读态/来源行/图例一律用 dim **实色**，要更淡就换更深的底不动字。

### 1.1 背景菜单（12 款；代码 `template/motion-systems/backdrop.tsx`）

**默认幕底：浅底 `pastel-mesh-flow`（原静态 pastel mesh 的流动版）/ 深底 `mesh-flow-dark`**。
其余按幕替换、在 SHOTBOOK §0 声明用在哪几幕，禁止镜头级随手换背景。
幕底自带的流动**不是运动系统的一部分**（运动系统只剩相机极缓推拉，cinematography §2）；速度统一 **1.5×**（`speed` prop 默认值），判据是盯字幕 3 秒眼睛不该被背景带走。全部由 `frame / fps` 驱动、零随机，Remotion 逐帧可复现；
GLSL 款需要 `remotion.config.ts` 里 `Config.setChromiumOpenGlRenderer('angle')`（与 three 桥同一条）。
深色渐变进 H.264 会出色带，**每款默认叠一层静态噪点**（`grain` prop，深 .06 / 浅 .09，overlay）。

| kind | 深/浅 | 配方（1920×1080，1.5× 已含在 speed 里） | 使用条件 |
|---|---|---|---|
| **`mesh-flow-dark`** | 深 | 底 `#0a1229`；四色（藏蓝 / 靛 / 青 / 紫，饱和 ≤60%）按 fbm 域扭曲权重混合，GLSL time 系数 .04；最亮处 L ≤35 | **深底默认**。片头 / 品牌 / 通用 |
| `aurora-veil` | 深 | 底 `#05070c`；三条被 fbm 扭曲的横向亮带从顶部垂下（青绿 → 蓝紫），下 60% 压回近黑；形变周期 30s | 科技 / 金句 / 反转幕；标题区放暗部 |
| `beams-grid` | 深 | 底 `#08090d`；透视地面网格（100px、`rgba(255,255,255,.06)`、rotateX 48°、径向遮罩向远处消隐）+ 顶部冷光 `rgba(120,170,255,.18)`；**静态** | 技术 / 数据幕。网格是细密纹理，只放屏幕空间静态层 |
| `spotlight-stage` | 深 | 底 `#101116`；主光 `rgba(41,151,255,.14)` 直径 65% 40s 慢摆 + 副光 `rgba(255,200,150,.05)` 55s + 60 粒悬浮尘埃（1.2~2.2px、亮 .25） | 金句 / 人物幕（现"居中追光"款的升级；光斑圆心跟主体落位） |
| `dot-field-wave` | 深 | 底 `#0b0c11`；36px 间距、3px 点径点阵 `rgba(207,224,255,.2)`，一道斜向亮度波 14s 一过（波峰 .8、点放大到 4px），径向遮罩隐去四角 | 数据 / 技术幕。只放屏幕空间静态层 |
| `orbs-dark` | 深 | 底 `#0b0d14`；三团 blur 70px 光球（蓝 `.55` / 紫 `.45` / 青 `.35`，直径 420~560）各按 30~45s 椭圆轨道绕行 | 片头 / 情绪幕（Apple 发布会式） |
| **`pastel-mesh-flow`** | 浅 | 底 `#fbfbfd`；四团粉彩（蓝 `.42` / 粉 `.38` / 紫 `.30` / 青 `.32`）位置由正弦 + fbm 驱动 35s 换一轮，彩度不变 | **浅底默认**（原 pastel mesh 的流动版；团色是氛围不是信号，"看这里"仍只许 accent） |
| `paper-grain` | 浅 | 底 `#f8f6f1 → #f3f0e8`；纸纹 feTurbulence（opacity .12、multiply）+ 一片 `rgba(255,255,255,.7)` 直径 70% 的窗光 60s 从左上慢移到右上 | 文档 / 人文 / 文字密集幕；窗光不过标题 |
| `grid-spot-light` | 浅 | 底 `#f5f6f8`；细网格 100px `rgba(29,29,31,.055)` 只在光斑附近显影 + 淡蓝柔光 `rgba(120,180,255,.22)` 直径 60% 45s 巡回 | 数据 / 技术幕（浅）。文字密集镜头别用；网格进屏幕空间静态层 |
| `iridescent-sheen` | 浅 | 底 `#fcfcfe`；fbm 驱动的薄膜干涉色（cos 调色板），饱和 30%、幅度 .16，明度钳在 L 86~100 | 品牌 / 设计题材；accent 选深色防撞 |
| `glass-blobs` | 浅 | 底 `#fafafc`；三团高彩色球（`#7aa7ff` / `#ffa3c4` / `#8fe3cf`，blur 40px，28~40s 游走）压在一层 `rgba(255,255,255,.55)` + backdrop-blur 40px 的磨砂玻璃后 | 产品 / 设计 / 轻松题材；玻璃透明度低于 .45 会抢字 |
| `ink-wash` | 浅 | 底 `#f6f3ea` 宣纸 + 纸纹 .10；fbm 云气（墨 `rgba(40,44,52,·)`，alpha ≤ .20）从右向左缓行，time 系数 .025（最慢） | 人文 / 历史 / 国风题材（配 chinese-aesthetics 方向） |

落地：场景整幕 `<Backdrop kind="…" />`（默认 `speed=1.5`、`grain` 开）；`theme.ts` 放两个 token `bg.light = 'pastel-mesh-flow'`、
`bg.dark = 'mesh-flow-dark'`，SHOTBOOK §0 无特别声明的幕按底色深浅引用对应默认。旧的三款（细网格 / 静态 pastel mesh / 居中追光）
分别被 `grid-spot-light` / `pastel-mesh-flow` / `spotlight-stage` 取代。

### 1.2 实拍底床（B-roll 当背景）处理链（正主）

视频素材做低存在感动态背景时**不靠调透明度**（浅底上会洗成灰雾）。环境层参数表：

| 环节 | 参数 | 说明 |
|---|---|---|
| 压暗 + 去饱和 | `brightness .35~.50` + `saturate .5~.7` | 深底默认 .42 / .55；浅底改用同源模糊或白色 scrim .75 |
| 渐变遮罩带 scrim | 文字所在边缘起 `78% → 0`（底部 60~78% 不透明） | 只压文字区；整屏罩 = 又回到"调透明度"。NN/g：30% 黑不够、50% 才够 |
| 运动 | 缩放 ≤0.6%/s 或横移 ≤3px/s，**时长 = 镜头时长** | 只缩放 / 极慢横移，不摇移；底床 : 内容视差 0.5 : 1.0 |
| 双色调（可选） | `grayscale 1 / contrast 1.15 / brightness .62` → 深色 `lighten` 提黑 + 主题色 `multiply .85~.95` 染白 | 先去色再着色；多来源 B-roll 统一气质 |
| 同源模糊（可选） | 前景卡清晰；同一素材 `scale 1.25→1.295 + blur 26 + brightness .45 + saturate .8`，慢放 0.5× | blur ≥20 才读作氛围；底床与前景同步会重影；卡 `bed-echo-blur` |
| 让位 | 前景入场同帧 `.55 → .28 + blur 8px`，0.4s；回来 .55s | 用 brightness 不用 opacity（透出底色会变灰）；对齐 Material 3 scrim .32 / Apple +35% |
| 同起同收 | 底床淡出 0.4s 与文字退场同帧 | 不留"字没了画面还在"的尾巴 |
| 选片 | 慢内容（延时 / 光斑 / 俯拍 / 人流虚化），避开可读文字与正脸 | 原片平均亮度（0~255）≥100 才压得住；循环接缝 0.5s 交叉淡化 |

### 1.3 视频容器边框八式（代码 `template/components/theme-frame.tsx`；2026-09-07 用户定版）

镜头里的视频（录屏 / 单条 B-roll / 引用片段）**不裸贴满幅、不裸放白卡、也不装假播放器**——进度条 / 播放键 / 时间码一律不要
（观众会拿进度对画面，对不上是撒谎，对得上也只是 UI 控件不是设计）。视频区包一层 `<ThemeFrame kind>`：每式都是一个**有出处的物**，
框的语汇替口播交代素材身份。任何卡的视频区都能包（单视频镜必包；bed-echo-blur 前景 / split-60-40-story 左格 / gallery-wall-dolly 三张可包同一式）。

| kind | 物 | 元素 | 装饰接力（起笔后 ≤1.35s 画完静置） | 调性 |
|---|---|---|---|---|
| `browser-retro` | Mac OS 9 铂金窗口 | 条纹标题栏 + 三只方钮、斜面导航钮 + 白地址栏、状态条 + 拖拽纹 | 无 | 科技 / 教程 / 网页录屏 |
| `magazine` | 杂志配图 | 通栏 1px 细线 + 小号字距图注、衬线页码 + 短线，纸面留白当边框 | 细线 scaleX 0.4s → 图注页码淡入 → 短线 | 人文 / 评论 |
| `film` | 35mm 胶片 | 深色胶片带 + 上下齿孔（孔 = 舞台底色）+ 琥珀色片号 | 无 | 纪录 / 引用别人的成片 |
| `polaroid` | 拍立得 | 白卡厚底边 96 + 固定倾斜 −1.5° + 软投影 | 无（宿主落位用 y 24→0，不弹不摆） | 生活 / vlog |
| `blueprint` | 工程图纸 | 内外双线 + 四角十字 + 顶部尺寸线 + 96px 刻度 + 等宽小字（与 G5 线稿同一套墨线） | 外线一笔画 0.6s → 十字 → 尺寸线 → 刻度 → 小字 | 方法论 / 拆解 |
| `laptop` | 笔记本 | 深色屏框圆角 18 + 摄像头点 + 机身底座带中央缺口 | 无 | 桌面录屏 |
| `stamp` | 邮票 | 白色厚边 22 + 四边半圆齿孔（舞台改极浅灰 `#f0f0f2`） | 无 | 轻松 / 文化 |
| `hairline` | 双发丝线 | 画面圆角 12 + 发丝线，外扩 14 一圈淡线 + 四角短标 | 淡线淡入 0.3s → 四角短标依次描出 | 极简 |

分工与纪律：
- **框只管造型 + 自己的装饰接力**；整体入场 / 退场 / 整框极缓推归宿主卡或镜头层（G1 相机 / 让位）——框跟着视频区一起动，不自己动。`at` 传视频区落位起点 +0.5s。
- **一片一式**：同一支片所有带框视频用同一式，式名写进 SHOTBOOK 蒙皮行；换式 = 素材身份乱。
- **框里画面零处理**：不滤镜 / 不缩放 / 不淡入淡出；静图不进框（框说"这是录像"）。
- **皮**：装饰线 / 装饰字 = 本片 ink（`ink` prop）；深底片：浏览器换深灰铂金、杂志 / 图纸 / 双发丝线换亮 hairline、拍立得 / 邮票保留白（它们本来就是白物）、胶片在深底上会消失别选。
- **装饰文字是装饰不是信息**（Untitled / http:// / FIG. 01 / 024 / 24 · KODAK 400 / 768 · SCALE 1 : 1），9~12px 本来就不为读；信息走字幕 / 花字层；`label` / `sub` 可换可空。
- 尺寸：`frameBox(kind, w, h)` 给整体尺寸与视频区偏移，宿主把视频区放到设计坐标上（整体 left = X − x, top = Y − y）；框四边在 action-safe 内、框底边到字幕带 ≥60px（胶片通幅例外，字幕带须在胶片带之外）。
- 反例：在框上加进度条 / 播放键"更像播放器"（已被用户否决）；这镜浏览器下镜胶片；给视频再套 Ken Burns；复古浏览器套本片自己的产品 UI（两层 UI）；拍立得倾斜 >3° 或落下回弹。

## 2. 字阶（1920×1080 基准；竖屏同号沿用，行宽变窄自然换行）

中文 = PingFang SC（Apple 官配中文，与 SF 同族气质）→ fallback Noto Sans SC / 思源黑体；
西文与数字 = SF Pro Display（`system-ui`）；等宽 = SF Mono / Menlo。**数字一律 `font-variant-numeric: tabular-nums`**（滚动计数不跳宽）。

| token | 字号/字重/行高 | 用途 |
|---|---|---|
| hero | 128 / 600 / 1.08 | 全片 1–2 次的英雄大字（钩子数字、金句核心词） |
| display | 88 / 600 / 1.12 | 幕标题、章节卡编号 |
| headline | 64 / 600 / 1.2 | 场景内小标题、图表标题 |
| tagline | 48 / 600 / 1.25 | 卡片标题、人名条主行 |
| body | 44 / 400 / 1.5 | 卡片释义、引言正文 |
| subtitle | 44 / 600 / 1.35 | 字幕（见 §5 专项） |
| caption | 32 / 400 / 1.4 | 标注、图例、头衔行 |
| micro | 24 / 400 / 1.3 | 来源行、法务行（屏幕角落） |

- 字重阶梯 **400 / 600 两档为主**（Apple 的 300/700 留给极特殊时刻：300=气声金句，700=砸字）。500 禁用。
- 西文/数字在 display 以上加 `letter-spacing: -0.02em`（Apple tight）；中文字距 0，不模仿西文负字距。
- 一屏文字层级 ≤3 级；释义超过 2 行就该拆成两拍。
- **hero 造型一屏一个**：同屏多个数字/大字时只有一个上 hero/display 档造型
  （大字号/色块/换色），其余降 body/caption 行内注——三个数字三种 hero 造型互相抢戏读作凌乱。
- **字号按手机验收**：横屏成片缩到 **390px 宽**复看，每行能读才过（桌面全屏预览不是验收标准）；
  排不下时**先删次要文案再考虑字号**，禁孤字行。

## 3. 间距 · 圆角 · 投影

- **间距基数 16px**：16 / 24 / 32 / 48 / 64 / 96 / 160。内容与画布边缘 ≥96px（action-safe），标题类 ≥160px（title-safe）。
- **横屏内容主列 ≤1440px 居中**（Apple 内容锁宽）；满宽只留给全出血素材和背景层。
- **圆角语法**（三档，不混用）：`12` 小件（chip/标签）· `28` 卡片（截图卡/信息卡）· `pill` 行动件（按钮/进度）。全出血幕 = 0。
- **投影只有一个**：`0 12px 60px rgba(0,0,0,0.22)`，只给"落在底上的证据素材"（截图/照片/手机壳）。卡片层级靠 hairline + 底色差，文字永不加投影（字幕描边是可读性手段，不算投影）。深底模式的辉光（glow）属于 L4 动效层，由动效系统管，不写进版式。

## 4. 运动 token（版式的时间维度）

| token | 值 | 说明 |
|---|---|---|
| enter | 0.2–0.8s | 入场；`power3.out` 起步 |
| exit | 0.15–0.5s | 出场永远比入场轻 |
| punch | 5–9 帧 | 重音；scale +0.02~0.04，衰减包络 |
| press | scale 0.95 一拍 | "被点击/盖章"反馈（Apple 全系统微交互的视频版） |
| overlap | 12–16 帧 | 转场交叠（transitions.tsx） |
| camera | `inOutSine` | 相机曲线唯一缓动 |

**禁用两种"做旧"微抖（用户定版偏好）**：手绘线条的 line boil（画完后 8~12fps 换形变帧的"沸腾"）
和贴图元素的 stop-motion 定格抖动（steps 时序随机偏移）一律不做——画完/落定的元素保持干净静置。
手作感由形状本身（歪斜、弧度、白边、胶带、投影）表达；hold 期的"活"只走系统性通道：
相机极缓推拉（Live idle 与环境呼吸不做）。

## 5. 字幕规范（按画幅）

> 版面几何——栅格 / 间距令牌 / 对齐 / 居中 / 字阶最小档 / 碰撞 / 底板配色——的完整规范在 `references/layout.md`；本节只管字幕本身。

| | 横屏 1920×1080（默认） | 竖屏 1080×1920（抖音） |
|---|---|---|
| 位置 | 底部居中，bottom 100px | 底部居中，bottom 350px（避 UI） |
| 宽度 | maxWidth 66%（≈1270px） | maxWidth 90% |
| 字号 | 44 / 600；>24 字降到 38 | 48 / 600；>15 字缩字号 |
| 样式 | 浅底：ink 直排无描边；深底：白字 + 6px 黑描边 | 白字 + 黑描边（整句硬现） |
| 组件 | motion-systems/Subtitles.tsx（素排版） | components 版（整句硬现） |

**素排铁律（正主）**：底部跟读字幕**不加任何动效**——整句硬现、整句硬走，
无淡入淡出、无逐字上色、无 pop、无浮动。唯一例外是 `keyword-pop-highlight` 关键词弹出，
且全片**最多 3 次**，除非用户明确要求更多（组件的 `keywords` prop 内建此上限自检）。

**字幕无标点（正主）**：底部跟读字幕不含任何句读/引号/括号/破折号/省略号——
句号问号一律去掉，长句的语气停顿靠**拆卡**表达（按停顿把一句拆成多张字幕卡，每卡一口气），
问句情绪交给口播语气。唯一例外：数字/型号中间的半角点号（`v0.1.1`、`83.8`）保留。
另：画面文字与字幕不得整句相同——画面文字是 ≤12 字的提炼（cinematography.md §4.5）。

常驻件（logo/吉祥物/进度条/人物角标）：横屏放**左下或右下皆可**（无平台 UI 侵占）；竖屏必须左下（右缘是抖音点赞栏）。
人物角标的下 1/3 带等硬约束以 `host-footage.md` §5 为准。

## 6. Do / Don't

**Do**
- 每幕开工先问"这幕的底色是哪档"——底色切换代替章节分隔线。
- 关键词强调 = accent 换色 + punch，一句最多一个。
- 证据素材（截图）永远带白边卡 + 唯一投影 + 轻微 Ken Burns，像"摆在桌上的实物"。
- 数字用 tabular-nums + hero/display 字阶，单位用 caption 阶后置淡入。
- 每镜全程保留至少一个空象限（排版预算全表见 cinematography.md §4.5）。

**Don't**
- 不出现第二强调色；不给卡片/按钮/文字加投影；不用装饰渐变（氛围来自素材和 env 层）。
- 不在同屏混用两种圆角语法；不让文字压到 action-safe 以外。
- 中文不加负字距；正文不用 300/700。
- 画面文字不整句照抄字幕/口播；同屏不出现第二个 hero 造型的数字/大字。

## 7. 落地：从本文件派生 theme.ts

新工程把 token 物化成代码（浅底模式示例）：

```ts
export const C = {
  bg: '#ffffff', bgAlt: '#f5f5f7', ink: '#1d1d1f', dim: '#7a7a7a',
  hairline: '#e0e0e0', accent: '#0066cc',
  positive: '#248a3d', negative: '#d70015', marker: '#FFE949',
};
export const T = {
  hero: {fontSize: 128, fontWeight: 600, lineHeight: 1.08},
  display: {fontSize: 88, fontWeight: 600, lineHeight: 1.12},
  headline: {fontSize: 64, fontWeight: 600, lineHeight: 1.2},
  tagline: {fontSize: 48, fontWeight: 600, lineHeight: 1.25},
  body: {fontSize: 44, fontWeight: 400, lineHeight: 1.5},
  caption: {fontSize: 32, fontWeight: 400, lineHeight: 1.4},
  micro: {fontSize: 24, fontWeight: 400, lineHeight: 1.3},
};
// 背景资产落成具名 token（配方见 §1.1）；浅底幕默认整幕引用 BG.mesh
export const BG = {mesh: '…§1.1 四团粉彩 radial…', grid: '…', spotlight: '…'};
export const SHADOW_EVIDENCE = '0 12px 60px rgba(0,0,0,0.22)';
export const RADII = {chip: 12, card: 28, pill: 999};
```

env.tsx 的 ACTS 分幕色温表（可选）从本片色板取值；静态 vignette 属幕底配方（浅底 `rgba(0,0,0,0.06~0.12)` 极轻档）。

<!-- ===== /file: video-talkcraft/references/design-language.md ===== -->

<!-- ===== file: video-talkcraft/references/host-footage.md ===== -->

# 人物素材（输入规格 · CPU 抠像 · 人脸安全区 · 与 B-roll 同屏）

**边界**：人物素材（真人录播或数字人成品视频）对本 skill 是**输入**——
录制/生成它的技术（TTS、数字人模型、超分）不属于本 skill。本文只管合成侧：
素材要长什么样、怎么在 CPU 上抠像、怎么定人脸安全区、怎么和 B-roll 同屏摆。

## 1. 输入规格

- **绿幕 mp4**（推荐输入，抠像自己做）或**已抠好的 alpha WebM**（VP9：
  `-c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0`；Safari 场景另备 HEVC alpha `.mov`）。
- 时长必须与最终配音**逐帧对齐**（人物口型对声音）；对不齐的素材先在源头解决，合成侧不做变速。
- **帧率**：人物素材 fps 必须等于成片 fps。不等时**优先把成片 fps 定为素材 fps**
  （动效是生成的，改帧率零成本）；确需保成片帧率则对人物层做光流补帧——
  **禁止靠简单重复帧混入**：25→30 的重复帧让人物每秒卡 5 次，旁边原生帧率的动效丝般顺滑，
  对比之下更扎眼（实测：人物区每 6 帧一次近零帧差、图形区无重复帧）。
  先看 `r_frame_rate` 与 `avg_frame_rate` 是否一致——不一致是 VFR / 丢帧，先 `-fps_mode cfr -r <avg 就近的标准帧率>` 重出，再谈对齐；
  容器标 30 但每 6 帧一次近零差 = 源头已经混入重复帧（真实 25），要回源头重出或 `mpdecimate` 还原，不是 CFR 能修的。
- **时长**与配音逐帧一致（差 >1 帧就是口型漂）。
- 拿到素材先 `ffprobe` 量真实宽高比——**输出尺寸按素材真实比例算几何**，不要按容器/期望值
  （按错比例排版会把人压扁）。
- **以上四条不靠人记：`python3 scripts/preflight.py --media-only --host <素材> --fps <成片> --voice <配音>` 一次断言完**
  （2026-09-06 复盘：本节规则和症状早就写着，仍然在整片母版渲完后才被发现、两轮母版作废——文档没被读的问题不能靠再写文档解决）。
  成片上的对应闸是 `motion_check.py --baseline <素材> --window <t>,<人物区>`：人物区周期性近零帧差直接报"重复帧"，不再误归并发光栅。
- 素材边缘有暗角环/白雾类瑕疵时，处置在**合成几何侧**（可见视频区内缩，v4 实测 ≥3.2% 源宽），不在 key 侧硬抠。

## 2. 抠像（全 CPU，ffmpeg 即可）

绿幕素材三种键控实测排序（deepseek-harness-v4 三轮迭代）：

- **绿优势度键（定版首选）** `A = 255 − clip((G − max(R,B) − bias) × slope)`（bias 6 / slope 24）：
  人全实（黑衣/白 T/溢光皮肤全稳）、背景全透；配 `despill=type=green:mix=0.18` + alpha 1px 羽化
  （boxblur 只作用 alpha 面；素材上到 1024² 时羽化半径同步 ×2）。
- colorkey（RGB 半径）：阈值低了浅绿残留、提高到 0.34 会把溢绿的皮肤啃成半透明——只配快速预览。
- chromakey（UV 距离）：0.28 起吃黑衬衫，窗口窄到不可用。

```bash
# 绿优势度键 → alpha WebM（v4 定版配方；despill mix 只能 0.18 上下，0.5 会把白 T 染粉。
# 首次用在新素材上先裁 3s 样片验证边缘再跑全片）
ffmpeg -i greenscreen.mp4 -vf "format=rgba,\
geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='255-clip((g(X,Y)-max(r(X,Y),b(X,Y))-6)*24,0,255)',\
despill=type=green:mix=0.18:expand=0.1,boxblur=0:0:0:0:1:1" \
  -c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0 -b:v 0 -crf 30 -an host.webm
# Safari 走 HEVC alpha：
ffmpeg -i greenscreen.mp4 -vf "<同上>" \
  -c:v hevc_videotoolbox -allow_sw 1 -alpha_quality 0.7 -q:v 55 -tag:v hvc1 -an host.mov
```

**无绿幕实拍**（候选，首次使用先在 3s 样片上验证边缘质量，均可 CPU 跑）：
macOS 上首选 Vision 人像分割（`VNGeneratePersonSegmentationRequest`，Swift 十几行 + 时序平滑/羽化后处理）；
跨平台用 rembg（isnet/u2net，逐帧慢但稳）或 MediaPipe Selfie Segmentation（快，发丝边一般）。
产出统一转上面的 VP9 alpha WebM 规格。

两条排查经验（别用错方法判断 alpha 在不在）：`ffprobe` 报 `pix_fmt=yuv420p` **不代表没 alpha**
（VP9-in-WebM 的 alpha 在 BlockAdditions 里，看 `stream_tags.alpha_mode`）；
`ffmpeg -pix_fmt rgba` 抽 PNG 也取不到它——**解码必须显式 `-c:v libvpx-vp9`**。

## 3. 人脸定位与安全区（`scripts/face_bbox.py`，CPU）

**人物在场的镜头，布局前必须先拿真实人脸 bbox——不目测、不用亮度阈值猜**（本节是人脸安全区的规则正主）。

```bash
python3 scripts/face_bbox.py public/dh/host.webm face-zone.json   # 每秒采样，OpenCV YuNet（CPU，模型 ~230KB）
```

输出：逐采样帧 face bbox + 全时段**并集 bbox** + 建议安全区（脸框向上外扩 60% 含头发、
四周再加 30px 余量，坐标已换算到素材像素系；合成里再按人物层的摆放几何映射到画布系）。

安全区口径：任何文字/卡片/字幕**及其背景**（卡片底、字幕底条都算）在**任何时刻**不得进入；
人物会移动/换形态时，每个停靠状态各查一次并取并集。主信息面板放人物对侧。

## 4. Remotion 接入

- **`<OffthreadVideo transparent />` 是必须的**：默认 `transparent=false` 按不透明取帧，
  alpha WebM 的透明区会被合成到黑底——成片人物带深色方框。
- 人物素材是**演示语境素材**，不属于任何卡的动效范围；复用配方卡时替换为片子自己的人物素材。
- 换素材（换人/换分辨率）= 人像几何全部重标定：包围盒、脸中心、场景避让、三形态落位。
  几何写成**分数**（相对源宽高），换分辨率零改动（v4 512→1024 实测）。

## 5. 人物与 B-roll 同屏：两条处置（角标规则正主）

**规则**（2026-09-21 改写，优先级从上到下）：某镜头既有 B-roll/截图素材，又有对应这段口播的人物素材时——
1. **默认路：人物降级成角标常驻**（下表 A / B），不占满画幅。B-roll 是这一拍的主角，人物的职责是"证明是这个人在讲"。
2. **三种例外，按语义触发、写进 G0 版式节奏表**：半身（只用于钩子 / 转折 / 收尾镜）、分屏格内（`split-60-40-story` 左格放本人）、
   短暂离场（素材独占 3–6s、≤1 镜、下一镜必回）。例外是"这一镜换一种形态"，不是"这一镜可以没有人"的常态化。
3. **硬底线：不许连续两镜无人**——人一消失口播就成配音 PPT（layout.md §7.1 第 1 条同源）。
逐镜形态怎么换、连用上限见本节末「形态轮换」；单条 B-roll 与形态的搭配见 shot-design.md §2⑦ 七式。

| 路 | 做法 | 用在 |
|---|---|---|
| **A 圆形头像章** | 人物层裁成圆窗 + 缩位到画面一角，走 `host-shrink-to-chip◆`（裁切窗 + 内层 scale 同一进度驱动） | 默认路。素材是绿幕/纯底、或抠不干净时；圆窗边界自己吃掉毛边 |
| **B 分割抠人贴角** | 按 §2 取 alpha，**保留人物真实外形**贴在 B-roll 左下或右下角 | 有手势要看、要"人站在素材前面"的临场感 |

两路共用的硬约束：
- **角标位置死锁**：落定后不漂、不呼吸、不换位（让台的语义是"我不抢戏"）。
- **人必须还在动**：角标里是继续口播的视频，不是静态头像/定格帧。
- **方位必须是下角**：横屏左下/右下皆可，chip 圆心落在画面**下 1/3 带**内
  （1080p 即 y ≥ 720），下缘贴 action-safe（96px）；与字幕冲突时优先换到另一侧下角，
  最多上让一个半径，绝不上浮到中位。竖屏必须左下（右缘是抖音点赞栏）。
- **不许缩小人物去迁就画框**：人被画框切到时，把人整体往画面里挪 / 收窄 B-roll，绝不等比缩小
  （`demo-spec.md`「Demo 硬性要求」第 7 条同一条纪律）。
- **交接错峰三段序**（正主 cinematography.md §4.5 第 8 条）：旧面板全退 → 人物换位 → 新面板才进；B-roll 接位晚人物 0.15s 从对侧进。
- **人物出镜节奏**：片头 Hook 先满幅/半身建立人物（首句～8s）再缩位——0 帧就是角标会弱化人的连接感；
  之后形态切换按 cinematography.md §4.5 布局事件预算（每分钟 2–4 次、语义触发，禁机械往返）。
- **形态轮换（跨镜；2026-09-21 用户定版）**：上面的"死锁"管一镜之内，镜与镜之间人物形态 × 方位要随版式换——
  半身（钩子 / 转折 / 收尾）、角标左下、角标右下、分屏格内（`split-60-40-story` 左格）、抠人贴角、**短暂离场**（素材独占 3–6s，≤1 镜，下一镜必回；连续两镜无人 = 配音 PPT）。
  连续 3 镜同形态同方位 = P1（cinematography.md §4.5 第 9 条）；G0 里写"从 s02 起缩至左下圆章，之后稳定"就是那支片"人物一直在左下角"的来源——
  稳定的是**每一镜内**不漂不换，不是全片一个位置。切换只在镜头边界、仍受布局事件预算与错峰三段序约束；单条 B-roll 与形态的搭配见 shot-design.md §2⑦ 七式。

## 6. demo 侧接入约定

- demo-shell 自动把人物视频注入 `.host-placeholder` 与 `[data-dh-host]` 元素（muted/loop/autoplay），
  加载失败退回灰阶剪影——demo 离线依旧可开。

<!-- ===== /file: video-talkcraft/references/host-footage.md ===== -->

<!-- ===== file: video-talkcraft/references/layout.md ===== -->

# 排版规范：放哪、多大、怎么对齐（口播画面 · 2026-09-05 用户定版）

`cinematography.md` §4.5 的排版预算管的是**放多少**（同屏 ≤3 组、空象限、hero 唯一）；本文管**放哪、多大、怎么对齐**。
起因：2026-09-05 用户审一条成片抓出 10 处缺陷，全是排版——卡片贴边、色块与标题不对齐、取景框没套住字、
独句太小缩在角落、条目字太小且底板同色、图组不居中、间距倒挂（中间空外侧挤）、黑字压到邻列、章节卡每章同一黑。
根因不是某张卡错了，而是 skill 里没有一份"几何规范"。

方法论借自三套版式 skill 的共通范式（guizang-ppt / guizang-social-card / dashiai-ppt）：
**栅格吸附 · 间距令牌 · 字阶 + 最小可读档 · 单强调色 · 同组同造型 · 数值化校验清单 · 别用 margin 硬救、换版式**。
下面全部按 1920×1080 给数；竖屏 1080×1920 的差异只在 §1 安全区与字幕带（design-language §5）。

## 1. 栅格与安全区
- **安全边 96**（四边 action-safe）、**标题边 160**；**字幕带保护区 y ≥ 900**（字幕 bottom 100 + 字高），只放字幕。
- **12 栏栅格**：内容宽 1728（1920 − 2×96），gutter 32，栏宽 114.67；栏线 `x_i = 96 + i × 146.67`（i = 0…12）。
  元素左右边缘**吸附栏线**（容差 ±4px）。常用跨度：全宽 12 / 主列 8 / 侧列 4 / 双列 6+6 / 三列 4+4+4 / 一主两辅 7+5。
- **竖向锚**：中线 y=540、三分线 y=360 / 720。单主体落中线；有字幕时主体组底边 ≤ 860。
- 实现：`debugOverlay` 输入 prop 画出栏线 + 安全区 + 字幕带（交付默认关，review-protocol.md §2）。

## 2. 间距令牌与层级
- 令牌（8 的倍数）：**8 / 16 / 24 / 32 / 48 / 64 / 96 / 160**。不用令牌外的随手数。
- **层级铁律：外边距 ≥ 组间距 ≥ 组内间距**（96 ≥ 48~64 ≥ 16~32）。
  反例：左列标题与右列列表中间空 400px、列表右边离画幅 40px——**间距倒挂**（内大外小），读作"两坨东西各自贴边"。
  修法是整组收进栏格再居中，**不是**改某个 margin。
- 元素离画幅边 ≥ 96；**< 64 即判贴边**（P1）。
- 组内相邻元素等距，≥ 24；标题与其下内容 ≥ 32，章节级标题与内容 ≥ 96。

## 3. 对齐
- 同组元素**左边缘对齐同一栏线**（或右对齐同一栏线），不许各自为政。
- **以字形边缘为准，不以容器盒为准**：色块 / 胶囊 / 图标与文字同组时，色块左边 = 标题首字左边；
  有内 padding 的元素把 padding **反向补偿**（负 margin）。反例："只学一个 AI 工具"标题下的 Codex 色块左边比首字左边多缩 60px。
- **基线对齐**：同一行的图标 / 数字 / 文字对齐基线；数字 `tabular-nums`。
- **标注类几何由目标包围盒实测反推**（框 / 圈 / 下划线 / 箭头 / 放大镜锚点 / 取景框）：
  `getBoundingClientRect` / `measureText`，四边留白 16~24 等距，**不目测**；实现后抽定妆帧核对，偏差 **> 8px 返工**。
  反例：对角角框的左上 L 离首字 80px、右下 L 压到末字下方——框没套住字。
  每张有目标锚点的卡在其 `references/cards/<slug>.md` 有「落位自检」节，选卡时抄进 SHOTBOOK（SKILL.md ④）。

## 4. 居中与配重
- **无人物在场**：主体组的**包围盒**水平居中（不是第一个元素居中）；纵向落中线或上三分线（给字幕带留空）。
  反例：三个色块整体偏右、"截图 + 清单"整组偏右——都是包围盒没居中。
- **有人物在场**（数字人或 B-roll 实拍里的人都算）：主体组放人物对侧，组包围盒中心落在该侧半幅中心（x = 480 或 1440），
  人脸安全区（`scripts/face_bbox.py` 实测）全时刻不入——人脸安全区优先级高于"居中"。三项并列且人在场的版式见 §7.1。
- **双元素组**：宽度比 1:1 或 2:1（黄金比 1.618:1 亦可），间距取组内令牌 32~64，两元素顶边对齐，整组包围盒居中。
- **偏一边的判定**：组包围盒中心与目标中心偏差 **> 48px**（P1）。

## 5. 字阶与可读（补 design-language §2）
| 档 | 字号 | 用途 |
|---|---|---|
| hero | 96~120 | 单句独占一镜、金句、章节名 |
| title | 64~72 | 镜头标题 |
| subtitle | 44 | 底部跟读字幕（素排） |
| body | 40~44 | 列表条目、chip、bullet、卡内正文 |
| caption | 28~32 | 图注、辅助说明 |
| micro | 22~24 | 来源行、时间戳 |

- **最小可读 28**（成片缩到 390px 宽复看仍能读）；**列表条目 / chip / bullet ≥ 40**——
  反例："写代码 / 改项目 / 查问题"三枚约 26px，"太小相当于没有"。
- **单句独占一镜 = hero 级 + 居中 + 底板或描边保可读，但不得覆盖人脸**（2026-09-05 用户补充）。
  画面里有人（数字人 **或 B-roll 实拍里的人**）时，文字及其底板全时刻不入人脸安全区（实测口径 host-footage.md §3）：
  横向仍居中，纵向改取人脸之外的那条三分线（人脸在上半幅就落下三分线 y≈720、在下半幅就落上三分线 y≈360）；
  人脸占满中带时放人物对侧半幅中心（x = 480 或 1440），并把底床在文字区局部压暗保可读。
  反例："会自己动手的新人"缩成 44px 的胶囊贴在左下角——正解是 hero 级落在两张脸之外的上三分线，不是贴角。
- **标题字数 → 字号档**（一行 ≤ 14 个汉字，超了拆行不缩字）：≤6 字 120 / 7~10 字 96 / 两行各 ≤8 字 84 / 两行有 9~12 字 72 / 三行 64。
- 字重两档（design-language）；hero 用 600、title 用 700，**不加粗到 800+**（越大越轻）。
- 同屏 hero : body **≥ 2:1**，没有对比就没有层级。

## 6. 碰撞与溢出
- **任意两个元素的包围盒不得相交**。例外只有三类刻意叠层：标注压在素材上、字幕带、chip 压在 B-roll 上。
- **文字块列宽 ≥ 最长行实测宽 + 2×padding**，文字不越出自己的列。反例：左列四行黑字（"看得到文件 / 实时预览…"）压进右侧列表。
  放不下的处理顺序：**先删字 → 再拆行 → 最后才缩字号**。
- 字幕带（y ≥ 900）内不放任何主体；主体底边 ≤ 860。
- 溢出分档（借自社交卡 skill）：1~40px 微调；40~90 局部收紧；90~160 压标题 / 正文；**> 160 换版式或删内容**，不用 margin 硬救。

## 7. 色与底板
- 强调色只有一个（design-language）。
- **列表 / chips / 条目底板用淡色系区分**：同组 3~6 项各配一个 pastel 底，同组不重复，文字保持墨色：
  蓝 `#E8F0FF` / 粉 `#FFE9F0` / 紫 `#EFE9FF` / 青 `#E6F7F2` / 黄 `#FFF4DC` / 灰 `#F2F2F5`。
  反例：三枚白底同色 chip，读作三个一样的空框。
- **章节标题卡按章轮换配色**：深底 4 套 藏蓝 `#0f1e3d` / 墨绿 `#10261f` / 酒红 `#2b1218` / 炭黑 `#16161a`，
  或浅底 4 套（本片色板派生），编号与章节名用对比色随底切换；**禁止每章同一黑**。
- 深浅底交替分幕（design-language §1）；幕底 12 款见 design-language §1.1（`template/motion-systems/backdrop.tsx`）。

### 7.1 并列句（人物在场时"三件事"怎么摆，2026-09-05 定版）
口播讲"A、B、C"三件并列的事、人还在画面里，是最高频的镜头之一；抖音口播剪辑圈的"抄作业"套路逐帧读出后收成
`parallel-items-with-host` 七式（头顶横排 / 三横条灰转彩 / 竖列虚化底 / 顶部卡堆 / 竖切三分 / 斜切三分 / 背景轮换大字）。三条纪律：
1. **人物永远在场**，形态随版式变（抠像全身 / 小框 / 圆头像 / 虚化成底再补小框）；人一消失口播就成配音 PPT。
2. **三项按口播逐个出现**（0.6s 一项、每项一次入场），不是三张一起淡入；灰转彩 / 背景轮换是同一节奏的两种做法。
3. **标签压在图上且大**：1080p 下卡类 ≥52、全屏切分类 72~80、大字版 168（960 舞台 ×2）——低于条目档等于没有（§5）。
几何按 §4 有人物在场处置：组包围盒相对人物对侧 / 人物上方居中，卡底到头顶 ≥36@960，任何卡与标签不入人脸安全区，头像四周留 ≥40；**一镜一式**。

## 8. 一致性
- 同组元素同一造型类：白边卡 / 描边卡 / 实色卡 **三选一不混**；同组图片统一比例与高度（裁切统一，不各自缩放）。
- 圆角三档、投影一个（design-language §4）；同组 chip 同高同 padding。

## 9. 版式定稿流程与校验清单
1. SHOTBOOK 每镜写一行**版式行**：栏跨度 + 组包围盒 `(x, y, w, h)` + 对齐基准（哪条栏线 / 字形边）+ 各元素字阶。
   数值由实现反读（`getBoundingClientRect`），不目测。
2. 实现后抽定妆帧，开 `debugOverlay`（栏线 + 安全区 + 字幕带），逐项核**九项**：
   ① 贴边（离画幅边 < 64）② 间距倒挂（组内间距 > 外边距）③ 左边缘未吸附栏线 / 未按字形对齐
   ④ 无人物时组包围盒未居中（偏差 > 48）⑤ 标注几何未套住目标（> 8px）⑥ 字号低于档（body 28 / 条目 40 / 独句 hero）
   ⑦ 包围盒相交 ⑧ 同组底板同色 / 章节卡同色 ⑨ 缩到 390 宽不可读。
3. 任一项失败 = **P1**（review-protocol.md §1.4 缺陷分级），修完再渲该段。
4. 独立评审的 rubric 加一行"排版规范九项"，评审材料给带 `debugOverlay` 的定妆帧一份。

## 参考
- guizang-ppt-skill：12 栏栅格吸附、左对齐 + 大留白、单 accent、主标题 : 正文 ≥ 8:1、章节级标题与内容 ≥ 9vh、装饰严格在栅格内不贴边、同组图片同比例同高、"别靠加 margin 硬救"。
- guizang-social-card-skill（github.com/op7418/guizang-social-card-skill）：间距令牌 8/12/16/24/32/40/48/64/80/96/160、最小可读 body 28 / caption 20 / cell 24、
  中文标题字数 → 字号分档、校验清单 R1~R9（溢出 / 页脚碰撞 / 最小字号 / 密度 / 行数上限 / 标题与内容间距 ≥28）、溢出分档处理、360px 缩略图可读测试。
- dashiai-ppt：按信息关系（并列 / 层级 / 对比 / 流程）选版式角色，先定关系再定版式。
- Josef Müller-Brockmann《Grid Systems in Graphic Design》：栅格是约束不是装饰。

<!-- ===== /file: video-talkcraft/references/layout.md ===== -->

<!-- ===== file: video-talkcraft/references/review-protocol.md ===== -->

# 审片评审协议（关卡 2 独立审片 · 关卡 3 规则合规 · 返修纪律 · 审片循环）

读者两类：**制作者**（何时派评审、备什么料、修完怎么复核）与**评审 subagent**（全新上下文，被派时必须先读本文件）。
关卡 1 机器闸的五条命令与评审材料抽帧命令在 `SKILL.md` ⑥⑦，本文不重复。

## 1. 关卡 2：独立审片

### 1.1 独立的定义
- **必须派独立 subagent，不许制作者自评**——做的人对自己的画面有盲区。
- **独立 = 全新上下文**：禁止 fork / 复用制作对话当"评审"，禁止对同一评审做 followup 复审——
  fork 出来的评审继承制作者视角，对照物又是制作者自己写的 SHOTBOOK，形成自证闭环（P0/P1/P2 全零、成片却一身病）。
- 制作者自己的首轮版式过目也委托子代理（给静帧 / 拼图路径，只回文字缺陷清单）——几十张图的图像 token 不进主上下文。

### 1.2 评审材料五件套（缺一不可）
1. **SHOTBOOK + 评审拼图**（`contact_sheet.py` 产物，整版浏览）+ 原帧目录路径（可疑帧回去单张放大）。
2. **原版卡对比帧**——SHOTBOOK 每个 slug 从 `gallery/media/<slug>.mp4` 抽 2 帧，与成片对应镜头帧并排，
   评审逐 slug 判"这是同一张卡的实现吗"（保真不进评审视野就永远查不出来）。
   没有 mp4 的卡（新 clone 上 `gallery/media/` 不在库里）用 `node scripts/verify-demo.mjs <slug>` 产出的
   `tools/.verify/<slug>-t0.png / -t1.png` 代替。
3. **词落点核对表**——beats.json 每条锚点的定妆帧 + 锚字 + 应落时刻，核"该词说出口时画面是否恰好在响应"。
4. **音效可听度报告**——`sfx_check.py --mix` 的输出（评审没有耳朵，机器报告就是它的耳朵）。
5. **语义标注 + 选卡候选表**——`semantics.json`（②-1，逐句 sem / weight）与 `qa/card-candidates.md`（`card_match.py` 产物）+ 各镜**选卡行**，核 §1.3「语义覆盖」：该摆的卡在不在、素材有没有被裸贴。

另附 SHOTBOOK §0 的**设计清单**（背景资产落位表、音效 cue 数、人物形态表），供 §1.5 第三类核对。

### 1.2.5 评审执行纪律（拿得到报告才叫评审，2026-09-06 定版）

- **增量落盘**：评审 subagent 开工先写 `REVIEW.md` 骨架（材料清单 + 空的 P0/P1/P2 三节），之后**每看完一镜追加一行**，不许憋到最终消息一次交付——
  几十张图撑爆上下文时最终消息根本发不出来，2026-09-06 三次派出三次零产出、共 146 分钟蒸发。
  看完最后一镜写**结束行** `## 评审完成 · 已看 N/N 镜`——制作者判"评审做完了"只认这一行（§1.6 WAIT），不认子代理的完成通知。
- **10 分钟无增量即终止重派**：制作者监看 `REVIEW.md` 的 mtime / 行数，10 分钟没长就 kill 换策略（分片、减图），不许等 85 分钟。
  派发 / 等待 / 判活 / 重派在各 harness 上怎么落，见 §1.6 原语表。
- **分片评审**：镜头数 > 8 的片按幕 / 镜头范围拆成 2–3 个评审 subagent（每人 ≤7 镜 + 全局 §0 材料），各写 `REVIEW-<范围>.md`；
  最后一个只做跨幕一致性（蒙皮 / 相机语言 / 人物形态节奏 / **版式轮换**——全片节奏只有看全片的人看得见）。上下文小到撑不爆，也能并行。
- **拿不到报告的处置**：3 次派出仍无落盘报告 → 交付物必须标注「**未获独立评审**」并附三次失败原因，
  **禁止**制作者自评后按"已评审"交付（静默自证 = 关卡 2 形同虚设）。

### 1.3 评审范围与 rubric
按 **可读性 / 构图 / 信息传达 / 质感 / 事实一致 + 保真 / 词落点** 出 `[P0/P1/P2]` 缺陷清单（提醒评审：入场中间态不是缺陷）。
盯的是**成片质量缺陷**，不是规则合规（规则项在关卡 3）：元素重叠 / 覆盖 / 堆积、动效位置不准（标注没落在目标上、
强调错位、元素出画）、画面噪点 / 压缩伪影 / 渲染残影、非有意的抖动或闪烁、文字贴边裁切、**排版凌乱**
（同屏主体组 >3、无空象限的满盘布局、画面文字与字幕整句重复双份、人脸安全区被文字或其背景侵入、多个 hero 造型互相抢戏）。
**风格一致**（对照 SHOTBOOK §0 `G0 风格档` 与各镜**蒙皮行**看定妆帧，design-language §0.4）：卡的 demo 中性皮残留进成片（demo 蓝 accent / 发丝线白卡 / 灰阶占位图形原样出现）、
同类卡两套皮（卡片造型 / 图表坐标轴语言不一）、深浅底策略与风格档不符——都记 P1；评审材料里 SHOTBOOK 的 G0 块与蒙皮行要随五件套一起给。
**语义覆盖**（2026-09-22 起；对照 `semantics.json` 与各镜**选卡行**，材料见 §1.2 第五件）：语义里 自我介绍 / 介绍他人 / 号召 没有对应语义的卡（库里有专设卡族却没用上，不分主句陪衬句）、`数据` 主句标了 `need: 量化` 却没有承载量化的图形卡、素材行声明了 V / 图 / 截图 却被裸贴（没有承接卡——吃素材家族且不是转场结构 / 字幕花字类；单视频镜也没包 ThemeFrame）——记 P1；该镜写了「语义偏离 ← 理由」的不算缺陷。评审要核的是**该摆的东西在不在**，不只是摆上去的对不对——2026-09-21 那支片的自我介绍没上人名条，三份评审都判无缺陷，就是因为 rubric 里缺这一条。
**版式轮换**（2026-09-21 用户反馈"排版太固定"；对照 SHOTBOOK G0 版式节奏表 + 相邻三镜定妆帧连看）：连续 3 镜人物形态 × 方位与素材容器都没变、
同一张呈现卡连用 3 镜或全片 >1/3、同一条 B-roll 相邻复用——记 P1；评语里写得出"又是左下圆章 + 中间方框 + 右边文字"这句即成立（cinematography.md §4.5 第 9 条）。

### 1.4 缺陷分级
- **P0** = 观众必然察觉且伤害理解——事实 / 文字 / 字形错误、不可读、声画错位、元素相撞遮正文、标注指错目标。
- **P1** = 违反硬规则或明显走样——错峰残影、词落点偏差 >0.3s、整镜头音效缺席、与原版卡对比帧明显不符、
  网页证据静态贴屏未拍摄（SKILL.md ③）、排版规范九项任一失败（`layout.md` §9：贴边 / 间距倒挂 / 未对齐 / 未居中 /
  标注未套住 / 字号低于档 / 包围盒相交 / 同组同色 / 390 宽不可读）、中性卡未按风格档蒙皮（design-language §0.4）、
  版式单调（§1.3 版式轮换：连续 3 镜同形态同容器 / 同卡连用 3 镜 / 一卡 >1/3）、
  语义事件未配卡或素材裸贴（§1.3 语义覆盖）。
- **P2** = 质感瑕疵——密度 / 留白 / 样式，记录但不挡验收。

**修完 P0 + P1 才算过关。**

### 1.5 只按句抽帧看不见的三类缺陷（必须给对应材料）
- **短命动效的错位**（标注 / 箭头只活 1~2s，句级抽帧大概率错过）→ 用**动效锚点帧**（每个重音 +0.25s 的定妆帧）
  逐个核"框住 / 指向 / 圈住目标了没有"。
- **抖动 / 闪烁**（时域缺陷，单帧永远看不见）→ 两道并用：`motion_check` 的并发光栅抖动判定
  （只量 ≤12 个 18s 间隔的固定裁剪窗、快速运动窗跳过——它是"并发光栅病"专项闸，不是时域全覆盖，`--anchors` 把锚点也纳入窗）
  + `qa_extract` 对 anchors.json 里 `"burst": true` 的锚点（状态切换 / 高风险）抽连拍三帧对——三帧间只该有设计内的连续运动，
  出现来回振荡、细纹理爬行即缺陷；`--bursts` 全抽只在抖动闸报警需人眼定位病灶时用。
- **设计没落地**（SHOTBOOK §0 计划的背景 / 音效 / 常驻件默默缺席——评审不知道"应该有"就不会报）
  → 把 §1.2 附的设计清单发给评审，逐项做"计划 vs 成片"核对。

### 1.6 派发原语表（harness 无关，2026-09-07）

本协议只用下面六个动词描述评审派发。**动词是契约，表格是翻译**：换 harness 只加一列，§1.1–§1.5 一个字不改。
子代理的全部世界 = 派发包 + 磁盘上的文件——别指望它看得见制作对话、记忆或已加载的 skill。

- **PACKET**（派发包）：一份自足的 prompt = 本文件路径（"被派时必须先读"）+ 五件套路径（§1.2）+ 分片范围 + 报告落盘路径 `REVIEW[-范围].md`。**原样传**，不许摘要转述。
- **DISPATCH**：起一个**全新上下文**的子代理跑 PACKET（§1.1 独立的定义）。
- **FAN-OUT**：分片评审（§1.2.5）= 2–3 个互不依赖的 DISPATCH 同时起。harness 并发上限**只减并行度不减范围**：超上限就分波，不许把两片并成一个评审去凑上限。
- **WAIT**：完成的判据是**落盘的 `REVIEW.md` 出现结束行**（§1.2.5），不是 harness 的完成通知——通知可能丢、可能先于落盘、可能对应一份空产出。收到通知也要去读盘。
- **LIVENESS**：每 2–3 分钟看 `REVIEW.md` 的 mtime / 行数；10 分钟没长 → 终止它，走 RE-DISPATCH（§1.2.5）。
- **RE-DISPATCH**：同一份 PACKET + 一行失败原因 + 换的策略（分片更细 / 减图）再起**新**子代理；累计 3 次无报告 → 标「未获独立评审」交付（§1.2.5）。
  **没有"制作者自己来"这一级降级**——那是关卡 2 形同虚设，不是 fallback。

| 动词 | Claude Code | Codex CLI | 无原生派发（任何 harness） |
|---|---|---|---|
| DISPATCH | `Agent` 工具，`subagent_type: "general-purpose"`；**禁 `fork`**（继承制作上下文 = 自证闭环） | `spawn_agent`，PACKET 随 prompt 传；子代理继承父 cwd，正好共享工程目录 | headless CLI 子进程：PACKET 写成文件，`claude -p "$(cat packet.md)"` / `codex exec` 后台起，stdin 接 /dev/null，stdout 进日志 |
| FAN-OUT | 同一条消息里多个 Agent 调用，各带 `run_in_background: true` | 多个 `spawn_agent`（本身异步） | 多个后台进程 |
| WAIT | 完成通知会自动到，**只当提示**——收到后仍读 `REVIEW.md` 认结束行 | `wait_agent` 收齐全部 id 后同样读盘认结束行 | 轮询 `REVIEW.md`，不以进程退出码为准 |
| LIVENESS / KILL | `TaskStop` 停掉无增量的子代理 | `interrupt_agent` **真正打断它**（卡住的子代理占着并发槽，不打断 RE-DISPATCH 可能起不来；要释放槽位再 `close_agent`），然后才 `spawn_agent` 新上下文 | `kill` 进程 |
| RE-DISPATCH | 新的 Agent 调用；**禁**用 `SendMessage` 对同一评审做 followup 复审（§1.1） | 新的 `spawn_agent`，不复用旧线程 | 新进程 |
| 返修后复审 | 同 DISPATCH：又一个全新上下文 | 同 DISPATCH | 同 DISPATCH |

harness 备注：
- **Codex**：派子代理受策略门控——**需要用户在本会话明确允许委派**，skill 文件里写了不算。没有授权时把一行询问（"评审要派并行子代理，可以吗？"）并进流程里已有的第一次用户停顿，不额外打断；口头允许或 `AGENTS.md` 里的常设授权都算。仍拿不到 → 走第三列 headless，**不许静默降级成自评**。
- **Claude Code**：`fork` 与对同一评审 `SendMessage` 在这里都是禁用原语，不是"更省 token 的选项"。
- 词汇对照：别处文档里"同一条消息里""后台运行"是 Claude Code 说法，按上表换成本 harness 的等价物；`Read` / `Write` / `Bash` 是能力名不是工具名。

## 2. 关卡 3：规则合规

- 按 `cinematography.md` §5 八条逐镜核：静息帧相机在动 / 任意 1s 无全静止 / 每个边界有转场处置且运动连续 /
  锚点量化误差 ≤16.7ms / 一拍一主角、说完让位 / 排版预算达标 / 网页证据无一处静态贴屏 / 字与画同起同收。
- **调试 overlay（slug 标签 / 镜头编号 / 网格线 / 安全区框）禁止出现在交付渲染**——要用就挂 `debugOverlay` 输入 prop，交付默认关。
- **可读性终检**：成片**缩到 390px 宽**（手机上刷到横屏片的实际宽度）复看一遍，每行都要能读——桌面全屏预览不是验收标准；
  排不下时先删次要文案，不缩字号、不留孤字行。

## 3. 返修纪律

- **时间码三段闭环**：用户批注的每个时间码，修改前抽该帧 → 修改后抽同帧 → 最终成片再抽同帧，三张路径写进 REVIEW。
- **状态型动画**（让位 / 换位 / 揭示）的修复必须覆盖**完整受影响区间的并集**（起点 / 中点 / 终点 + 每个边界前后），
  不能用"批注帧已正常"代替整段验收。
- 同一问题**二次返工**时，REVIEW 必须留下"第一次修复为何失效"的记录。
- 返修复核必须给**量测数字**（首次可辨时刻 / 被吞时刻 / 占比像素），"看起来好了"不算数——量化口径是多轮收敛的关键。
- 修复验证**只渲受影响段过闸**（`render_shots.mjs --changed sNN`；freezedetect 单段可跑），不整渲。

## 4. 审片循环制度

首片机器闸全过后，只做 **1 轮**独立审片 → 修完 P0/P1（复核给量测数字，改哪段渲哪段）→ **即交付**，然后把两件事一起摆给用户：
1. 问用户**是否需要继续自动审片和修改**——继续的话每轮仍换全新评审上下文，自动轮次累计封顶 **3 轮**；
   3 轮后仍有未清 P0/P1 就停手，把剩余缺陷清单、每轮修复记录和"为什么没修掉"原样交给用户定夺（无限自审自修不收敛只会烧预算）。
2. **同时打开动效工作台**（命令见 SKILL.md ⑧）并提示：不想跑自动轮次的话可以在工作台里自己微调（文字 / 颜色 / 字号 / 位置 / 变速逐项可视化调，改完直接导出）。

交付物随附本轮审片的遗留 P2 清单——"记录不修"的判断权在用户。

<!-- ===== /file: video-talkcraft/references/review-protocol.md ===== -->

<!-- ===== file: video-talkcraft/references/schematic.md ===== -->

# G5 线稿示意图（纯文字镜的第二层）

> 正主：本文件（规则 + 语义图形词典）；代码 `template/motion-systems/schematic.tsx` + `icons.ts`（`scripts/fetch_icons.py` 生成）；
> 在 SKILL.md ④ 排版预算与 ⑤ 全局系统里各有一条硬规指向这里。2026-09-07 入库。

## 0. 为什么有这一层

用户 2026-09-07 看首版口播片："很多没有放图片素材的镜头就只有文字的动效往上堆，太单一了。"给的参考是一支 275s、**零位图零实拍**却不显单调的解说片（《RAG 与知识库》）。
把它拆开，不单调的机制不在背景，而在这几条（背景星点那一套属于另一种风格档，本库不装）：

1. **每句抽象话配一张线稿示意图**：图标 + 方框 + 箭头 + 小标签。44 个内容镜里 29 镜是"白线简笔图示 + 标签"，纯文字大字只有 8 镜。
   讲"切块"就画一页文档被切成块，讲"绕路"就画两条路，讲"库"就画圆柱。文字只做标签和结论。
2. **文字从不裸放**：每个词都装在容器里（胶囊 / 框 / 色块），容器本身就是一个"物"。
3. **节拍绑定字幕块**：每个字幕块起始帧 ±3 必有一个可见动作（入场 / 变色 / 描画 / 脉冲），平均 1~2s 一次可见变化。
4. **入场词汇少而统一，靠错峰制造密度**：只有淡入上浮 / 滑入 / 缩放 / draw-on 四种，靠 1~2 帧错峰、11 帧灰→强调色变色让同一动作变成一串涟漪。
5. **语义图形代替素材**：文档 = 折角页 + 线条、模型 = 点阵方块、库 = 圆柱、空间 = 网格 + 散点、索引 = 斜切平面——全部 ≤30 行 SVG。
6. **颜色即语义**：强调色 = 当前重点；灰 = 未激活 / 上下文；白（或 ink）= 结构色；语义色只进图表与警示。

它的机位全片静态，运动感全靠 1~5；本库保留 G1 极缓推拉，再加上这一层——**两层都有**。

## 1. 什么时候必须用

- **素材行只有「文」的镜头**（章节卡除外）：层矩阵必须多一行「陪衬图形」——线稿示意图 / 图标 / 连接线 / 卡堆 / 任务卡之一，
  且能一句话说出它和这句口播的关系。`preflight.py` 对没有这一行的纯文镜给 WARN（advisory）。
- 只有一段视频当主体的镜头不属于这里（那是 design-language §1.3 的视频容器边框 `theme-frame.tsx`）；有截图 / 图片的镜头也不属于（那是证据卡 + 标注类卡）。
- 一镜一张图：示意图与文字标题是同一个主体组的两半，不是第四个主体（同屏预算仍 ≤3 组，cinematography §4.5）。

## 2. 词汇（schematic.tsx）

| 件 | 做什么 | 命门 |
|---|---|---|
| `Sketch` | 一张覆盖画幅的透明 SVG 舞台 | 坐标按舞台像素写，竖屏传 width/height |
| `DrawPath` | 任意 path 一笔画（`pathLength=1` + dashoffset），可虚线（mask 揭开）、可闭合后填色 | power2.inOut 近匀速、恒定线宽、画完静置（借 outline-box-title） |
| `DrawIcon` | Iconify lucide 线稿按段接力描画，24→size | 只描边不填充；图标是"物"不是装饰 |
| `Connector` | 二次贝塞尔连接线（bow 弓高），可带箭头 | 线先到、头后长（96% 处才出箭头）；箭尖留白不戳字 |
| `Node` | 圆节点 back.out pop + 标签滞后 2 帧 | accent 实心 = 当前 / 白底 = 普通；被连接线"点亮"后才 pop（借 step-timeline-vertical） |
| `Plate` | 圆角板一笔画一圈（上边中偏左起笔）后填白 | 卡 / 任务卡 / 提示词卡的骨架 |
| `Panel` | 不描画的磨砂白板（深底传 dark），把线稿从模糊底床上托起来 | "文字从不裸放"的容器；alpha .58 |
| `Cross` / `Tick` | 两笔叉（语义色 strike）/ 一笔勾（accent） | 否定 / 确认只用这两种手势，不用 emoji |
| `Traveller` | 沿路径行进的小点（线头跟随物） | 和 DrawPath 同 at/dur 才贴线头 |
| `Label` | SVG 文字淡入上浮 | ≥36px 才能在 390 宽手机上读；30px 以下当装饰 |
| `polyD` | 多点折线 / 平滑折线 d | "绕路 vs 直路"这类路线 |

一律 `abs`（绝对秒）驱动，节拍来自 beats.json 的词锚；零随机、零 ref 量测（seek-safe）。

## 3. 语义图形词典（先写关系一句话，再选形）

| 口播在讲 | 画什么 | 例 |
|---|---|---|
| 文档 / 文章 / 规则 | 折角页 + 2~3 条灰线；多份 = 卡堆（错位 +12,−30） | 「继续堆提示词」= 卡堆叠到五张 → 打叉 → 掉走三张 + 「−3」 |
| 模型 / 系统 / 引擎 | `brain-circuit` / `cpu` + 虚线或细实线环 | 「模型的提升」= 核心环 + 三条卫星线 |
| 对比 / 取舍 / 路径 | 两条路线 A→B（弯路灰虚线 vs 直路 accent） | 「更快 = 绕路更少」 |
| 步骤 / 流程 | 胶囊 + 箭头横排（当前步 accent，其余灰） | 解析 → 切块 → 向量化 → 建索引 |
| 否定 / 别做 | 图标 + 右上角红叉 | 「别只问聊天问题」= 对话框 + 叉 |
| 确认 / 做到 | 清单圆点 + 勾 | 任务卡前两条打勾 |
| 分类 / 几个方向 | 中心 hub 扇出 N 个节点（连接线先画、节点后亮） | 「四个方向」= 速度 / 前端 / 代码 / 写作 |
| 任务 / 复杂事 | 圆角任务卡：标题线 + 清单逐条画出 | 「一个真实的复杂任务」 |
| 库 / 存储 | 圆柱（椭圆盖 + 两侧竖线） | 知识库 / 向量库 |
| 空间 / 相似 / 聚类 | 网格 + 散点 + 高亮圈 | 「去索引里找最近的邻居」 |
| 数量 / 规模 | 数字滚动（`number-counter` 卡）+ 单位 | 「一百万 token」 |
| 时间 / 速度 | 计时器 / 仪表 / 刻度尺 | 「11 分 53 秒」 |
| 边界 / 范围 | 虚线框 + 内部勾 | 「更准判断边界」 |

规则：**motif 是纹样、示意图是物**——章节卡上的主题 motif（chapter-title-card）低不透明度做背景；示意图在主体面，ink 3px 全不透明。

## 4. 节拍与错峰纪律

- **每句至少一个可见变化**：示意图的每一拍都挂在词锚上（画线 / 点亮 / 打叉 / 掉卡），`beat_gap_check` 的空窗答案可以是"示意图在描画"。
- **最后一拍别被边界吞**：章节卡压入 / push-through 出镜前 ≥0.5s 画完（2026-09-07 三镜实测：扇出、第三颗卫星、「−3」徽都被边界吃掉过）。
- 错峰口径：节点 1~2 帧、卡 2 帧、图标各段 0.04~0.08s、连接线 0.18~0.45s；灰→accent 变色 0.3s 本身就是叙事动作，不必再加位移。
- 入场词汇只用四种：淡入上浮 / 滑入 / 缩放 pop / draw-on。不做 glitch、不做抖动、不做呼吸。

## 5. 落位自检（抄进 SHOTBOOK 该镜自检列）

- 关系一句话在 SHOTBOOK 层矩阵里写出来（「G5 …← 讲 X 所以画 Y」），说不出关系的图形删掉。
- 示意图包围盒与文字 / 卡片 / 字幕带不相交，离画幅边 ≥64；hub / 连接线起点在文字包围盒之外（连接线穿字 = P1）。
- 多条连接线**与条目同序**（上→下），不交叉；箭尖留白 14~18px。
- 整组（文字 + 示意图）中心偏离画心 ≤48（layout.md §9 ④）；示意图占右 / 下的空象限，文字组随之左移或上移。
- 一套皮：ink 3px + accent；深底幕全部换 dark token；灰虚线只表示"被否定的路"，不同时拿来当边界线。
- 标签 ≥36px 或承认为装饰；图标 ≥72px；核心图形 ≥ 屏高 20%（v1 实测 150px 的核心在 540 宽拼图上看不见）。

## 6. 可选骨架：常驻 HUD（用户点名才装）

参考片还有一层：顶部章节胶囊（中英双语小字）、章节内步骤追踪条（当前步高亮）、底部细进度条带章名。
它让"再空的镜也有骨架"，但与本库 Apple 范式的"内容即主角、版式退后"相冲，**默认不装**；用户点名要时按 `chapter-progress-list` 卡 + 屏幕空间层实现（不进相机），
并在 SHOTBOOK §0 声明。

## 7. 反例

- 示意图与口播无关（讲速度画了个几何装饰）；四个纯文镜用同一张图。
- 图形做得像图标库贴图：实心、彩色、带阴影——这是插画不是线稿；线稿只描边。
- 示意图抢了文字的戏：核心图 > 屏高 45%、或用了第二强调色。
- 线自己长、点自己亮、没有先后——"线到哪亮哪"是这一层的全部语义。
- 让示意图替代素材：有真实截图 / 录屏时必须用真图（SKILL.md ③ 真图硬规），示意图只补"没有素材的抽象话"。

<!-- ===== /file: video-talkcraft/references/schematic.md ===== -->

<!-- ===== file: video-talkcraft/references/semantic-annotation.md ===== -->

# 语义标注（②-1）—— 让口播稿和卡库说同一套词

2026-09-22 定版。**为什么有这一步**：在此之前，选卡漏斗只有「输入类型」一道过滤（这一镜有没有 B-roll / 图 / 人），
稿子那一侧从来没有被标注过——没人在任何一处写下「这句话在做什么」。于是：

> 「我是万里」被当成又一个论点关键词，配了全库能量最低的文字卡（soft-blur-in），
> 库里 P0 级的 `lower-third-nameplate`（人名条）就在货架上、它的「适用」行明写「也用于自我介绍」，却没人在那一刻查到它。
> 三份独立评审都判这一镜无缺陷——因为评审 rubric 只核「摆上去的东西对不对」（保真 / 蒙皮 / 版式），不核「该摆的东西在不在」。

这不是某一类语义漏了，是**需求侧没有结构化产物**。数据句配文字卡、引用句没给出处、竖屏素材裸贴、长截图静态贴屏，
都会从同一个缺口漏下去。语义标注就是补这个缺口的产物：它让 `card_match.py` 能出候选、`preflight.py` 能查覆盖、评审能对账。

## 产物：工程根 `semantics.json`

```bash
python3 <skill>/scripts/semantic_annotate.py --init          # ② 之后：从 audio/timestamps.json 生成骨架（含词法提示 hint）
#   逐句填 sem / weight / entities / need
python3 <skill>/scripts/semantic_annotate.py --stats         # 校验 + 分布
python3 <skill>/scripts/semantic_annotate.py --sync-shots    # ④ SHOTBOOK 写完后：回填 shot（只动 shot，标注不丢）
```

**顺序是硬的**：② 时间戳 → ②-1 标注（此时还没有分镜，`shot` 允许为空）→ ④ SHOTBOOK → `--sync-shots` 回填 → card_match / preflight。
分镜边界**改过之后**也要重跑 `--sync-shots`：`--check` 会核每句的 `shot` 与它的时间落点是否一致，不一致直接 FAIL（否则覆盖闸会拿错镜头的卡来核这句）。
漏了回填，`card_match` 每镜都是「无 main 句」、preflight 的语义覆盖整段空转（2026-09-22 独立评审 P0-1；现在两处都会直接 FAIL 并点名这一步）。

```json
{"version": 1, "source": {"timestamps": "audio/timestamps.json", "shots": "remotion/shots.json"},
 "sentences": [
  {"i": 59, "t": 113.36, "text": "我是万里", "shot": "s11",
   "sem": ["自我介绍"], "entities": ["万里"], "need": ["身份"], "weight": "main"}
 ]}
```

| 字段 | 含义 | 词表 |
|---|---|---|
| `i` / `t` / `text` | 与 `timestamps.json` 逐句对应（脚本逐字核；改稿或重剪后标注即失效，要重新 `--init`） | — |
| `shot` | 归哪一镜。`--init` 时若已有分镜来源就自动填，否则留空，**④ 之后用 `--sync-shots` 回填**（按 SHOTBOOK 标题的起止秒，或 `shots.json`） | SHOTBOOK / shots.json 的镜头 id |
| `sem` | **这句在做什么**，可多选 | 26 词封闭词表，见 `taxonomy.md`「语义索引」（源头 `scripts/cards_index.py` 的 `VOCAB`） |
| `entities` | 数字带单位 / 人名 / 品牌 / URL / 地点——③ 采素材按这个去找 | 自由文本 |
| `need` | 画面需求 | 证据 / 身份 / 量化 / 对比 / 结构 / 强调 / 无 |
| `weight` | `main` = 主句，**只有主句允许进新元素**；`sub` = 陪衬句，只允许已有元素变化 | main / sub |
| `exempt` | 豁免某条词法硬规，值是理由（≥4 字） | `{"数据": "这里的三千是比喻"}` |

`weight` 这一列同时把「禁止一句一个新元素」（cinematography §4.5）落成了机器可读的东西：
一镜至少一个 `main`（没有 = 新元素没有挂点，脚本 WARN），`sub` 句不配新卡。

## 标注纪律

1. **一张卡只列在它专门服务的语义下**，一句话也只标它真正在做的事。`论点` 是兜底档，别拿它当垃圾桶——
   库里 `论点` 只留 3 张整句卡（soft-blur-in / per-character-rise / alt-block-lines），就是这个用意。
2. **词法粗筛不是判断**。脚本的硬规只有三条（我是/我叫 X → 自我介绍；点赞/订阅/三连 → 号召；数量词 → 数据），
   拦的是系统性漏标；其余十条是 WARN 提示。真正的判断在人。
3. **标注是派生物**。`text` 与时间戳逐字一致是硬规：预剪 → 时间戳 → 标注 → 其后一切，顺序不能反。
4. **`论点` 有占比闸**：超过一半句子标成论点 → WARN。把什么都标成论点等于让覆盖闸全部失效（论点既不在硬规也不在软规里）。
5. **豁免与偏离都要理由**（都是 ≥4 字，两套口径对齐）：句级用 `exempt`（词法硬规误伤时），镜级用 SHOTBOOK 里的
   `- 语义偏离：自我介绍 ← 开场已报身份，s11 不再重复`（列表项或表格行都认、必须有理由；空理由或写成 `<语义>` 占位都不放行，preflight 会 WARN 提示格式）。
   偏离只对**写在该镜正文里的语义**生效：写在别的镜、写了本镜没有的语义、写进「未完成清单」节，都不放行（preflight 会 WARN 点名）。

## 下游怎么用

| 阶段 | 用法 |
|---|---|
| ③ 素材 | 素材购物清单按 `need` / `entities` 生成：`证据` 去截真页、`身份` 要头像 / 账号信息、`量化` 要图表或数据源 |
| ④ SHOTBOOK | `python3 <skill>/scripts/card_match.py --out qa/card-candidates.md` 出每镜候选（语义 × 素材 × 卡索引），每镜写一行 `- 选卡行：<语义> → <卡>、…`；选候选之外的卡，写一行 `- 语义偏离：<语义> ← 理由` |
| ④→⑤ 闸 | `preflight.py`「语义覆盖」段。先逐句核归属：**任何一句的 `shot` 为空或不是本 SHOTBOOK 的镜头 → FAIL**（那些句会被静默跳过，结论就不可信）。再核四条：① **自我介绍 / 介绍他人 / 号召** 没有对应语义的卡 → FAIL（这三类有专设卡族、无替代物；**不分 main / sub**，标成 sub 也算）；② `数据` 主句且 `need` 含 `量化`，却没有能承载数字的卡（数据信息图类，或 `数据` / `强调` / `列举` / `对比` 语义——数字常以条目标签的形式落在并列卡上）→ FAIL；③ 其余 13 个语义（引用 / 对比 / 定义 / 步骤 / 列举 / 时间地点 / 机制 / 选择 / 过程演示 / 空间叙事 / 设问 / 金句 / 章节）→ WARN；④ 素材行声明了 V / 图 / 截图 却没有承接卡 → FAIL。承接卡 = 吃素材家族 + 类别不是转场结构 / 字幕花字 + 不是只承载人物的卡（`host-shrink-to-chip` 的角标窗里装的是讲者不是素材，算承接的话这条闸就只剩「连角标都没有」才触发）；该镜正文出现组件名 `ThemeFrame`、或框词与素材词同行（如「B-roll 视频区包杂志框」）时降为 WARN——光在版式行提一句「人物半身用 magazine 杂志框」不算，那是 G0 给人物容器起的名字（三轮复核 P1-T1）。缺「蒙皮行」的镜不豁免（有素材或硬语义就 FAIL）。写「语义偏离」的放行 |
| ⑦ 审片 | 语义标注 + 候选表进评审材料（review-protocol §1.2 第五件），rubric 多两条 P1：语义事件未配卡、素材裸贴 |

没有 `semantics.json` 时 preflight 退化成对 `script.txt` 的词法兜底（我是 X / 点赞订阅 → 全片无对应语义卡 → WARN），
但逐镜覆盖核不了——**这一步别跳**。

## 库存缺口（2026-09-22 建索引时暴露）

- **设问**：只有 `title-demote-to-label`（问题降格成标签、答案在下方展开）勉强承担，没有专门的「抛出问题不立即回答」卡。
- **号召**：只有 `subscribe-cta` 一张；两张关注卡（`x-follow-card` / `douyin-follow-card`）自己的 md 明写「证明而非号召」，
  它们是 `介绍他人`。抖音关注卡还需要真实账号信息（头像 / 昵称 / 抖音号 / 粉丝数），没有就不做、写进「未完成清单」，别伪造。
- **机制**：只有 `source-converge` 一张（多对一汇聚）。

这些是真实缺口，索引里如实显示「（暂无卡）」，不硬塞——要么补卡，要么在 SHOTBOOK 写偏离理由。

<!-- ===== /file: video-talkcraft/references/semantic-annotation.md ===== -->

<!-- ===== file: video-talkcraft/references/shot-design.md ===== -->

# 镜头分层设计：背景 / 主体 / 文字（实操工作单）

`cinematography.md` 的七层模型是完整词汇表；实际给每个镜头做设计时，先用**三面分层**这个
粗颗粒工作单把每面的内容和动效定下来，再展开成 SHOTBOOK 层矩阵。三面与七层的对应：

| 面 | 含七层中的 | 回答的问题 |
|---|---|---|
| 背景面 | L1 相机 + L5 视差背景 + L6 环境 | 这个镜头的"空间"是什么，它怎么一直活着 |
| 主体面 | L3 主体 + L4 附着 + L5 配角 + L7 遮罩 | 这一拍的唯一主角是谁，谁在配合它 |
| 文字面 | 字幕 + 花字/标注/标签（屏幕空间层） | 听觉信息的视觉对位物在哪 |

**每个镜头三面都必须有分配**（背景面永不缺席——这正是 PPT 感病根 1 的解法）；
写不出某面的动效就写"继承全局系统"（相机极缓推拉），但不许写"无"。

## 1. 各面的动效菜单

### 背景面（选 1 个空间基底 + 相机乐句，环境层自动继承）
- **空间基底**：幕底 12 款（`template/motion-systems/backdrop.tsx`，design-language §1.1；**浅默认 pastel-mesh-flow / 深默认 mesh-flow-dark**，
  另有极光纱 / 光束网格 / 双追光 / 点阵亮波 / 柔光球 / 纸纹窗光 / 网格柔光 / 薄膜虹彩 / 磨砂彩团 / 淡墨云气）/
  纯色幕底（canvas 档）/ 3D 星野或场景（three 桥）/ 全出血素材（Ken Burns 必开）/ **实拍底床**（B-roll 当背景）
- **实拍底床**（B-roll 当背景；处理链与参数表正主 design-language §1.2）：压暗 + 去饱和 + scrim 只压文字区 + 极慢运动（时长 = 镜头时长），
  **不是调透明度**；只有一条素材 / 竖屏素材用同源模糊（卡 `bed-echo-blur`）；前景入场时底床再让一档；人物一律不进底床
- **相机乐句**（shots.ts 一条连续曲线，**只有两式**）：
  极缓推 1.00→1.04~1.06（默认）/ 极缓拉（沉降、冷却、收束）。横移 / 纵向爬行 / 环绕 / dutch 不再作为场景相机动作——
  素材自身要动的（列举传送带、读长图、3D 检视）用运镜卡作用在**素材层**；世界画布长镜头（longtake.tsx，§3.5）是可选范式
- **环境**：分幕色温档位（ACTS 表，可选）；曝光脉冲 / vignette 收紧 / 扫光不做

### 主体面（一拍一主角，接力线写清楚）
- **入场**（0.2–0.8s，比出场用力）：中心 slam（scale 3→1 / 1.8→1 backOut）/ 侧压入让位式 /
  虚→实 rack focus / 描边 draw-on（L7）/ 弹入堆叠（media-pop-in）/ 逐球逐条 stagger
- **hold**（静置，无 idle 微动）：元素落定后不动，画面的活由相机极缓推拉负责；
  附着层的**内容性**运动（代码上滚、指针走动、数字滚动）属于主体本身，照常
- **同起同收**：镜头时长 = 口播句长；底床 / 缓推这类持续运动的 duration 就是镜头时长（**写速率不写固定秒数**：
  缩放 0.5%/s、横移 2.8px/s），文字退场那 0.4s 底床与素材一起收——不许出现"字没了、画面还在空转"的尾巴（GSAP/Remotion 里等最长那条 tween 跑完才结束就是这个坑）
- **配角互动**（L5，每个动作答"配合谁"）：反向运动（环扩张 vs 卡收缩）/ 光束桥接注意力 /
  时间轴/佐证物侧入 / 集体退焦只留主体（Defocus）
- **让位**（新主体锚点 −6f 起，三选按"还回不回来"）：**真退场**（0.15–0.5s 出场后从版面消失，
  本拍后不再回指的元素优先选这个）/ 降权留守（缩 0.92 + 上移 + 暗 −66% + blur 3.2px，`Live demoteAt`——
  留守元素**仍占原槽、计入同屏预算**，新主体不得摆进它的位置；浅底同屏留守 ≤1 组；旧名 retireAt 已 deprecated）/ 划线击落被顶替 / 碎成粒子（转场用）

- **素材只有「文」时，主体面 = 线稿示意图**（G5，`references/schematic.md`）：先写一句"讲 X 所以画 Y"，再从语义图形词典取形（文档 = 折角页、对比 = 两条路、分类 = hub 扇出、否定 = 图标 + 叉、任务 = 清单卡…）；标题与示意图是同一主体组的两半，示意图占空象限。

### 文字面（字幕之外，屏幕空间不进相机）
- **字幕**：位置 / 字号 / 素排铁律 / 无标点全部以 design-language.md §5 为准，全片样式唯一
- **强调字**（作用于标题/金句/独立文字层，不是底部字幕）：关键词 accent 换色 pop /
  花字三重描边逐字揭示（FlowerWord）/ 砸字（SmashWord）/
  字体对比重音（type-contrast-emphasis：换衬线斜体放大）——一句话最多一个强调
- **句法级字卡**（2026-09-05 shotcraft 移植◎，作用于标题 / 主张句，不是字幕）：列举用词槽轮换（`word-slot-cycle`：句干钉死、句尾胶囊连换 N 个短语再收束成整句）/
  主张句先立主语（`lead-word-zoom-assemble`：首词 2.3× 占满再缩回补齐）/ 小节交接（`title-demote-to-label`：标题站稳后缩到左上角当常驻路标，内容在其下生长）/
  改口（`error-retype`：打出错的半句再删掉重打）/ 数字揭晓（`countdown-arc-scatter`：数字弧扫停落成标题首字）/ 利落入场（`split-text-stagger`：逐字裂升 + 基线长出）/
  带图列举（`word-relay-filmstrip`：名词恒定动词接力，左列截图步进一卡）；深底名词科普的背景层可用 `flying-words`（关键词隧道，前景照常静置）
- **标注**：荧光笔扫词（素材上）/ 手绘圈注箭头 / callout 引出线 / 铅笔手绘（PencilDraw）/
  一次扫描点出 N 处（`scanline-annotate◎`，多目标截图）/ 急推特写一拍按住（`crash-zoom-punch◎`，6 帧到位即静，一支片 ≤2 次）/
  准星咬合（`reticle-lock-on◎`：四角从画外扑入、收缩过头再回弹咬住目标，“就是它”的重音）
- **信息件**：人名条 / 章节编号 / 名词解释卡 / 数字滚动——入场走三段式，hold 带浮动

## 2. 镜头类型预设（七型，直接抄再改）

每型给出三面的默认分配；SHOTBOOK 里写明偏离预设的地方即可。

### ① 钩子镜头（片头 5–8s）
- 背景：默认幕底（`pastel-mesh-flow`）或 `grid-spot-light` + 相机全程慢推，结尾加速推向问号/钩子物（转场承接）
- 主体：中心舞台接力（2–3 任主体先后 slam 占中，前任让位），最后一任配集体退焦
- 文字：hero 字阶大字即主体；字幕从第 1 句就在

### ② 论证/叙事镜头（8–18s，最常见）
- 背景：网格或幕底 + 相机分 2–3 段乐句（沉降→跟随→推向证据）
- 主体：标题→徽章→素材卡的接力线；列举用传送带流（持续左漂）不用静态网格
- 文字：关键词 accent pop；点名实体必须有视觉对位物入场

- 论证镜里没有截图 / 实拍可放时，不要用"再多一行大字"补空——补一张与这句话对应的线稿示意图（G5），文字只留标签与结论。

### ③ 数据镜头
- 背景：幕底压暗一档，给图表让对比度；相机慢推向图表主柱/终值
- 主体：chart-grow 逐项生长（stagger=语音列举节奏），关键柱高亮 + punch；数字 NumberRoll ≤26 帧到终值；
  讲"N 个里有 M 个"的比例用点阵比例图 `unit-grid-proportion◎`（100 格可数个体 + 大数字同步计数，比裸百分比直观）；
  讲"多个来源汇到一处"的机制用 `source-converge◎`（多对一动态图解，汇聚完成后结果居中）；
  讲“N 个方案选哪个、选了之后怎样”用 `chip-grid-single-select◎`（单选反黑 + 余项锁位降权 + 算式行）
- 文字：结论行在数据落定后 0.3s 才出（先看到证据再看到判词）；单位 caption 阶后置

### ④ 证据/素材镜头（截图、实拍、聊天记录）
- 背景：幕底 + 相机极缓 Ken Burns（素材自己也带 1→1.04 慢推，两层速度错开）
- 主体：白边卡 + 唯一投影"摆上桌"（轻歪 1–2°）；荧光笔/红线划重点跟朗读同步；放大镜出细节；
  读完文档提炼结论用 `doc-park-left-pill-deal◎`（文档驻留露 35%、右侧慢发牌结论 + 常驻说明行）；推荐一本书 / 一个工具用 `info-card-assemble◎`（信息卡逐字段自建）
- 文字：标注文字勿叠素材文字（白底卡另起）；来源行 micro 阶常驻角落
- 标注几何换算（实战坑）：荧光笔/红框落点 = 原图坐标 × (卡内容宽/原图宽) **+ 卡内边距**——
  白边/padding 漏计会差 1–2 行高直接扫错行；先抽一帧量准再写坐标
- **网页拍摄**：调研中判定可用的网页，成片里禁止静态截图贴屏——它是被镜头"拍"的实物，
  按口播意图选拍法，**一镜一主式**：

  | 口播在说什么 | 拍法 | 卡 |
  |---|---|---|
  | "从头看一遍，重点在这一条"（文档/README/搜索结果/榜单） | **滚**：页面动、相机不动；匀速上滚 ≈10% 页高/s，关键条提前 ~1s 减速、停在视口中线 1~2s，标注预置随页走 | `evidence-scroll-tour◆` |
  | "我带你看这三处"（长落地页多个兴趣点） | **巡**：页面躺在 3D 台上不动、相机挨个停靠，每站 hold 真静止 | `stage-keyframe-tour◇` |
  | "注意看这个数字/按钮/条款" | **放大**：看一眼就撤 → 圆形放大镜（本体压暗 + 连接线回指）；要一直挂着 → 画中画 | `magnifier-detail` / `pip-zoom-box◈` |
  | "就是这句话/这个词" | **划**：整句扫荧光笔、单词划墨线、素材上圈注箭头、区域四角框 | `highlighter-sweep` / `ink-underline◇` / `scribble-annotation` / `corner-bracket-frame◈` |
  | "这张页面有 N 个问题"（逐处点评 3~5 处） | **扫**：扫描线匀速掠过，越过每个目标即弹取景框 + 侧栏标注 + 计数，标注常驻到讲完 | `scanline-annotate◎` |
  | "就是这一行"（一拍按住，全景可以丢） | **撞**：6 帧急推到目标文字块、过冲回收后钉死；与"推"的区别是它是切不是 hold 运动 | `crash-zoom-punch◎` |
  | 一屏页面只是 hold 着讲 | **推**：缓推底噪，origin 咬兴趣点，hold 期不停 | `slow-push-in` |
  | 目标本身在动（光标/正在填的字段） | **跟**：相机锁死移动目标 | `cursor-locked-zoom◇`（配 `cursor-actor-demo◆`） |

  组合纪律：**滚动/巡游段内不弹放大镜、不现场划线**（evidence-scroll-tour 的命门是"页面是唯一动元素"）——
  放大与划线只在停留段或静止取景内做，顺序「滚到 → 停 → 划/放大 → 再滚」；推与滚不叠（读作手抖）；
  同一页面"划"最多 2 处（同屏重音唯一）。坐标全部取采集时 DOM 实测的 `targets.json`
  （broll-sources.md「网页拍摄素材采集」），再按上一条几何公式换算；随页滚动的标注钉在页面坐标系。
  **不用浏览器录屏**——Remotion 在长截图上拍，seek-safe 且能对词锚；录屏帧率不稳、懒加载与粘性头会穿帮。
  一屏装得下、只当配角堆叠的小截图（media-pop-in 多张里的一张）可静态入卡但仍带 Ken Burns，不得是该拍主体。

### ④′ 多素材同屏（两张以上素材同时在场）
多素材的问题不是"怎么摆下"，而是**观众该看哪**。先问一句：能不能顺着讲（每项一张大图轮换，`parallel-items-with-host` ⑦ / MKBHD 实测分屏 0%）——能就不要同屏。
- **排版先定关系**（关系 → 版式 → 卡）：

  | 关系 | 版式 | 卡 |
  |---|---|---|
  | 主次（论点 + 两条佐证） | 一主两辅：主图 55~60% 宽 + 右列两张等大 | `still-layout-relay`（hero-duo） |
  | 并列（三个人 / 三个时期） | 三联竖图 4+4+4 栏 | `still-layout-relay`（triptych） |
  | 对比（前后 / 新旧 / A-B） | 双分屏 + 滑动分割线，两图**必须同构图** | `split-compare-slider` |
  | 两件事来回提及 | 前后叠放 + 焦点接力（一清一糊） | `rack-focus-pair` |
  | 序列 · 三个平级例子 | 照片墙推轨（3D 墙、全景 → 逐张停靠 → 拉回） | `gallery-wall-dolly` |
  | 序列 · 有先后的几站 | 时间线照片带（上下交替、横移逐站 → 拉开看全条） | `timeline-photo-strip` |
  | 列举 ≥5 | 传送带匀速 + 关键项减速 | `filmstrip-conveyor` |
  | 汇聚 → 聚焦（四选一） | 2×2 网格收成一主 + 一列小图 | `grid-to-hero` |
  | 汇聚 → 并列（一叠→五个） | 卡堆扇形展开再铺平 | `stack-fan-out` |
  | 主从（看视频讲要点） | 60/40 分屏：左素材缓推 + 右标题与 pastel chips | `split-60-40-story` |
  | 证据感堆叠 | 歪着叠 | `media-pop-in` |
- **入场有先后有方向**：错峰 80~150ms、同向；主角先落，配角跟进；全组同时同速淡入 = PPT。
- **任一时刻只有一个主角**：焦点接力靠**其余降权**（brightness .55~.6 / scale .985），主角本身只动 3~4%；切换 0.4s，两次之间 ≥1.5s。
- **运镜只做两种**：横向巡览停靠（每站缩放绕当前素材发生）与推入单个再拉回全景；停靠段内部 1→1.03 微推防死。
- **统一外观**：白边 / 圆角 / 唯一投影全组一致；横竖混合统一到同一外框比例（裁切不缩放）。预算不变：同屏主体组 ≤3（一组网格算 1 组）、留一个空象限给字幕、素材内文字不与字幕相撞。
- 几何全部按 `references/layout.md`（组包围盒居中、组内等距 24~32、离画幅边 ≥96@1080p）。

### ⑤ 金句/转折镜头
- 背景：**整幕换底色**（浅↔深反差，章节感来源）+ 色温转档；相机换向（推 → 极缓拉）
- 主体：大字逐行浮现（quote-card），核心词最后落 + punch；其余一切 Defocus
- 文字：这一型文字面即主体面；字幕可暂时隐去（大字本身就是台词）

### ⑥ 收尾镜头
- 背景：星野/纵深空间 + 相机正向 dolly 穿场（或长镜头最后一站后拉）
- 主体：碑文式逐句经过（远→近），符号回收（片头钩子物再现），终句金辉收束
- 文字：CTA/来源信息 micro 阶，谢幕整体淡出

### ⑦ B-roll 镜头（视频素材 + 人物素材同时在场）
- 背景：B-roll 满画幅出血即空间基底（自身运动已经在动，相机只叠极轻慢推，两层速度错开）
- 主体：**B-roll 是这一拍的主角，人物降级成角标常驻**——圆形头像章（`host-shrink-to-chip◆`）或分割抠人贴角，落下角；
  两路选型、方位与全部硬约束（下 1/3 带 / 死锁 / 人要在动 / 三条不许）以 `host-footage.md` §5 为准。
  **角标是默认路不是唯一路**——形态随下表七式逐镜换（半身 / 角标左下 / 角标右下 / 分屏格内 / 短暂离场，host-footage.md §5「形态轮换」）
- **单条 B-roll 的呈现七式（一镜一式、相邻镜不同式、同式全片 ≤1/3；2026-09-21 用户定版："应该不断切换不同的镜头来展示，即使是素材呈现也可以用不同方式"）**：

  | 式 | 什么样 | 人物形态 | 卡 / 件 | 口播在说什么 |
  |---|---|---|---|---|
  | ① 出血全屏 + 角标 | B-roll 满幅当空间基底（`Bed`），标注只落留白区 | 角标左下 / 右下 | `template/components/bed.tsx` + 标注卡 | 素材本身有戏（动作 / 场景），让它说话 |
  | ② 装框 + 单侧文字 | 素材进 `theme-frame` 一式的框，文字在人物对侧 | 角标或半身 | `theme-frame.tsx` + 字卡 | 素材是证据 / 引用，要与文字并置 |
  | ③ 60/40 主从分屏 | 左格素材缓推、右格标题 + chip 逐枚 | 角标；**或左格放人物本人** | `split-60-40-story◉` | "看着它干活边听边记"，要点 ≤4 |
  | ④ 同源模糊底床 | 前景素材白边卡 + 同一条放大模糊当底 | 角标 | `bed-echo-blur◉` | 竖屏素材 / 只有这一条素材 |
  | ⑤ 截帧指认 | `ffmpeg -ss` 取一帧当图，急推 / 锁定 / 圈注其中一处 | 角标或离场 | `crash-zoom-punch◎` / `reticle-lock-on◎` / `corner-bracket-frame◈` | 口播在指素材里的某一处 |
  | ⑥ 多素材编排 | ≥2 条素材（或一条素材多帧）按关系排版，3D 墙 / 时间线带自带运镜 | 角标或离场 | §2④′ 关系表：`still-layout-relay` / `split-compare-slider` / `rack-focus-pair` / `gallery-wall-dolly` / `timeline-photo-strip` / `grid-to-hero` / `filmstrip-conveyor` | 并列 / 对比 / 序列 / 汇聚 |
  | ⑦ 素材短暂独占 | 人物离场 3–6s，素材出血全屏 + 一行标签，下一镜人物回来 | 离场（≤1 镜、下一镜必回） | `Bed` + `slow-push-in` / `sway-parallax` | 情绪或场景句（"想象一下…"），全片 ≤2 次 |

  纪律：相邻两镜不同式；②③ 是"素材 + 文字"最顺手的两式，合起来也不得超过全片 1/2；⑦ 之后连续两镜无人 = 配音 PPT；
  **轮换是换构图不是加运动**——每一式内部仍只有相机极缓推拉。写进 G0 版式节奏表（cinematography.md §4）后再展开逐镜矩阵，preflight 核连用与占比。
- 文字：标注只落在 B-roll 的留白区；角标与字幕不同侧
- 人物出镜节奏与换位错峰：见 `host-footage.md` §5（首句先建立人物再缩位、每分钟 2–4 次语义触发、错峰三段序）
- 人脸安全区：开工先跑 `scripts/face_bbox.py`，口径见 `host-footage.md` §3；主信息面板放人物对侧
- **并列句**（人在场 + 口播讲"三件事"）：用 `parallel-items-with-host` 七式之一（头顶横排 / 三横条灰转彩 / 竖列虚化底 /
  顶部卡堆 / 竖切三分 / 斜切三分 / 背景轮换大字），一镜一式；三条纪律见 layout.md §7.1
- **只有一条素材 / 竖屏素材**：同源模糊底床 `bed-echo-blur`（人物竖屏原片自己当底床也成立）
- **人物常驻 + 道具台**：`host-card-glass-board◎`——左 9:16 人物竖卡、右 3D 玻璃板当道具台，板上道具按口播接力（tile → 连接线 → 结果），同一块板连讲几个道具不换镜；深底是领域皮，浅底换白卡 + 发丝线
- **B-roll 里要指一处**：先截帧（`ffmpeg -ss` 取那一帧当图），再用图类标注卡（`crash-zoom-punch◎` / `reticle-lock-on◎` / `hand-drawn-ellipse◈`）指；
  库里不再有操纵视频时间的标注卡（2026-09-06 用户删 freeze-frame-annotate），一个镜头只能有一个时间操纵者



## 3. 写进 SHOTBOOK 的方法

1. 先给每镜头填三面工作单（三行表：背景面/主体面/文字面 → 内容 + 动效 + 接力线）；
2. 再展开成层矩阵（逐节拍、逐层、答"配合谁"），格式见 cinematography.md §4；
3. 自检：背景面是否全程活着？主体接力线有没有断（某拍无主角/双主角）？文字面强调是否超发（一句>1 个）？
   排版预算过了没（cinematography.md §4.5）？排版规范九项过了没（`references/layout.md` §9）？
   选中的每张卡的「已知坑」「落位自检」抄进自检列了没？
   **字与画同起同收**了没（每镜最后一个退场 = 镜尾，底床 / 缓推的时长 = 镜头时长）？
4. 选卡两道过滤（候选可由 `scripts/card_match.py` 直接算出来，见 `references/semantic-annotation.md`）：先按素材类型——SHOTBOOK 每镜写清输入是**人 / V / 图 / 截图 / 文 / 界 / 场**中的哪几种，到 `references/taxonomy.md`「输入类型索引」挑吃这种输入的卡；
   再按这句口播的语义——到「语义索引」挑专为这种语义（自我介绍 / 数据 / 对比 / 列举 / 引用 / 号召……）而设的卡，同一语义里按 G0 能量档挑档位。两张索引都由 `scripts/cards_index.py` 从卡 frontmatter 生成，带 ◦ 的卡没有可换内容的 prop、改文案要动源码（◉◎ 两批新卡的 md 开头另有「输入类型」表与「常用场景」四条）。
5. 选中的卡按 SHOTBOOK §0 的 `G0 风格档` 写**蒙皮行**（与版式行并列）：`卡名 → 改了什么皮`（颜色 token / 字体 / 圆角与材质 / 图表坐标轴与标记 / 占位图形换什么素材）；
   卡是中性 UI，进片不蒙皮就是贴片——契约与例外见 design-language §0.4。

范例：`shotbook-example.md` 的 S3 就是"③数据镜头"预设 + 偏离项（3D 基底、dutch 僵局感）的写法。

<!-- ===== /file: video-talkcraft/references/shot-design.md ===== -->

<!-- ===== file: video-talkcraft/references/shotbook-example.md ===== -->

# SHOTBOOK — 「$2000 vs 24小时」镜头重设计 v2

> 本件的价值是**层矩阵格式与写法**（意图 / 节拍锚定 / 每行答"配合谁" / 静息期检查）。
> §0 全局系统里的具体数值是设计稿草案，与最终代码有出入（让位 −40%→实际 −66%、深度 0.6/1.3→实际 0.5/1.2、重叠 12–15→实际 12–16）；
> **数值一律以 `cinematography.md`（按可工作代码校正）为准。**
>
> **2026-09-04 用户定版（运动做减法）**：本例 §0 里的相机 x/y/旋转曲线、冲击脉冲、idle 微动、呼吸 vignette / 扫光 /
> 曝光脉冲、dutch 均为历史项目记录，**已不再是要求**——现行规定只保留相机极缓推进 / 拉出 + 让位（cinematography.md §2）。
> 读本例只学层矩阵写法与节拍锚定。

目标：消除 PPT 感。诊断出的四个结构性缺陷 → 四套全局系统 + 逐镜头层矩阵。

节拍真相源：`public/timing.json`（Qwen3-ASR 字级时间戳，强制对齐输出，视为已验证网格）。
30fps，量化误差 ≤16.7ms（口播驱动足够，不宣称 <5ms）。

---

## 0. 全局系统（先于任何场景实现）

### G0 风格档（design-language §0；先于 token，每张卡按它蒙皮）
- 领域：科技 · AI 开发者工具 · 演示口吻（依据：全稿 9 个产品术语 / 4 段终端与代码 / 受众是写代码的人）
- 底色策略：白底主导；代码 / 终端幕整幕深 tile #1d1d1f
- token：accent #0066cc · ink #1d1d1f · dim #7a7a7a · hairline #e0e0e0（涨跌语义色不出现）
- 字体：PingFang SC 600 / 400，数字与代码 SF Mono `tabular-nums`
- 材质 & 卡：发丝线卡（1px hairline、圆角 12、无投影）；证据截图白边卡 + 唯一投影；终端窗为深 tile 卡
- 图表：极简折线 3px accent、网格 #ececf0、坐标轴只留必要刻度
- 素材 / 底床：录屏、终端、界面截图；B-roll 少，不用双色调
- 能量：中；不做的事：不用手绘圈注（换角框 / 取景框），不用 pastel chip（换发丝线 chip）
- 蒙皮行写在各镜层矩阵旁（例：S3 `chart-grow → 网格 #ececf0、柱色 accent 单色、数字 SF Mono`）
- 样板镜：s1_hook（首镜即有人物 + 等式数字动效 + 字幕，能代表全片；⑤-1 先做它、渲有声单镜预览给用户确认，其余镜头占位等确认）
- **版式节奏表**（2026-09-21 起 G0 必附，格式正主 cinematography.md §4；下表按本例 7 镜补写，只示范"人物形态 × 素材容器逐镜在换"）：

  | 镜 | 人物形态·方位 | 素材容器 | 主卡 |
  |---|---|---|---|
  | s1 | 半身·右 | 无（等式大字左栏） | count-badge-title |
  | s2 | 角标·左下 | 装框·中（论文页） | evidence-scroll-tour |
  | s3 | 离场 → 角标·右下 | 3D 数据台 | chart-grow |
  | s4 | 分屏格内（左格本人） | 分屏格（终端录屏） | split-60-40-story |
  | s5 | 半身·左 | 无（红色时钟 hero） | quote-card |
  | s6 | 角标·右下 | 出血全屏（人物照片） | bed + crash-zoom-punch |
  | s7 | 离场 | 长镜头星野 | long-take-world |

### G1 CameraRig（L1，每场景一条连续曲线 + 冲击脉冲）
- 每场景一个 `<CameraRig path={...} impulses={[...]}>` 包裹全部内容。
- path = 全程连续的 scale/x/y/rotate 关键帧（缓动 inOutSine），**任何冲击不得重置慢曲线**（模式4：连续慢层 × 快打点）。
- impulse = 重音词所在帧的 3–6 帧脉冲（scale +0.02~0.04 或 2px shake），叠加在慢曲线上。
- 3D 场景中同一 progress 同时驱动 THREE camera，保证 2D/3D 相机一致。

### G2 Parallax 深度平面（L5×L1，模式8）
- 每场景内容分三层：`<Plane depth={0.6}>` 背景网格、`<Plane depth={1.0}>` 主内容、`<Plane depth={1.3}>` 前景强调物。
- 相机位移 × depth 系数 = 各层位移。网格背景从 MainVideo 静态层改为进 CameraRig 的 depth 0.5 层。

### G3 Idle + Retire（L3/L4 生命周期，模式12：状态绑定）
- 元素状态机：forming → resolved → handing-off → gone，全部是 frame 的纯函数。
- **resolved 期间必须有微动**：`idle(seed, frame)` 确定性 sin 呼吸（scale ±0.5%、y ±3px、glow ±15%）。
- **让位规则**：一个节拍只有一个主体。上一主体在新主体入场帧 −6f 开始 handing-off（缩小 0.92 + 后移 depth + 亮度 −40% + 轻模糊），不再堆积满屏。

### G4 Environment（L6，全程低幅存活）
- 呼吸 vignette（8s 周期 ±6%）+ 12s 斜向扫光，从头到尾不停。
- 分幕色温：Act I 建置(s1–s2) 青金 → Act II 演示(s3–s4) 暖金 → Act III 反转(s5) 红、vignette 收紧 → Act IV 启示(s6–s7) 冷静回暖。
- 重音帧做三段曝光脉冲（rise 2f / plateau 2f / decay 8f）。

### G5 转场（Sequence 重叠 12–15 帧，运动承接）
| 边界 | 类型 | 承接设计 |
|---|---|---|
| s1→s2 | 推穿 | 相机加速推向"？"，模糊升起；s2 从模糊中被拉出（同向） |
| s2→s3 | 推入翻出 | 相机推进论文页占满画面→过曝白；s3 从亮心拉出露出 3D 箱 |
| s3→s4 | 甩镜 | 金色闪光中相机向左whip-pan+运动模糊；s4 同向进入后刹住 |
| s4→s5 | 震切 | 「验证✓通过」绿闪定格 → 3 帧黑 → 红色 24h 时钟已在走（全片唯一硬切，给反转） |
| s5→s6 | 冷却 | 红色淡出、色温转冷，相机从黑缓缓后拉露出陶哲轩 |
| s6→s7 | 粒子溶接 | ≠ 号碎成粒子上飘 → 粒子即 s7 的二十面体星野（物质连续性） |

### G6 字幕升级（**已废弃，勿抄**）
> ⚠️ 本节与 2026-08-27 字幕素排铁律冲突（底部跟读字幕不加任何动效，见 design-language.md §5），
> 仅作历史范例保留结构完整——新片一律素排：整句硬现、整句硬走。

---

## 1. 逐镜头层矩阵

时间均为绝对秒（scene-local 换算在实现层做一次）。

### S1 · 0.00–7.48 · 意图：一个荒谬的等式砸到你脸上
- 素材：人 · 文（等式与数字全是生成图形；本片首镜建立讲述者，不上 B-roll）
- 蒙皮行：count-badge-title → 数字 SF Mono `tabular-nums`、accent #0066cc、不装卡底（等式本身是主体）；保留卡内时序 / 缓动 / 几何比例
钩子场景改为**中心舞台接力**：三个主体先后占据画面中心，而不是同屏排开。

| 节拍 | Layer | 对象 | 动作 | 角色 |
|---|---|---|---|---|
| 0.0 | L1 | 相机 | 全程慢推 1.00→1.06 | 给整场一口气 |
| 0.5 | L3 | "如果我告诉你" | 中心逐字浮现，带轻微追焦 | 首任主体 |
| 1.92 两千美元 | L3' | $2,000 卡 | 中心 slam（scale 3→1, outBack） | 接任主体 |
| 1.92 | L3 | 首句 | 缩小上移 + 变暗（让位） | 交出中心 |
| 1.92 | L4 | 金粒子爆 + 辉光 | 从卡片边缘喷出，随卡片呼吸 | 附着材质 |
| 1.92 | L5 | 细金环 | 反向扩张（卡片收缩时环放大） | 反向运动=深度 |
| 4.24 攻破 | L5 | 光束桥 | 从卡片向右快速 draw | 交接注意力的桥 |
| 4.64 十个 | L3'' | "十个世界级数学难题" | 从右侧压入，卡片压缩左移让位 | 第三任主体 |
| 6.48 你信吗 | L3''' | "你信吗？" | 打点入场 + 相机脉冲 +0.04 | 终任主体 |
| 6.48 | L2 | 其余元素 | 集体退焦 + 变暗 | 光学上只留问号 |
| 6.48 | L6 | vignette | 收 8% | 聚拢视线 |
| 7.1→ | L1/L2 | 相机+模糊 | 加速推向问号，模糊升起 | 转场承接 |

静息期检查：粒子漂 + 相机推 + vignette 呼吸 ≥2 层 ✓

### S2 · 7.48–25.04 · 意图：官宣的分量——从标题到实物证据
- 素材：截图（public/pages/announce/page.png）· 图（public/stills/paper-p1.png）· 人
最长场景，相机分三段乐句。十项难题从"静态网格"改为**传送带流**。

| 节拍 | Layer | 对象 | 动作 | 角色 |
|---|---|---|---|---|
| 7.5 | L1 | 相机 | 段A：慢拉 1.05→1.0 | 从转场余势中沉降 |
| 8.56 OpenAI | L3 | 日期章+标题 | 标题两行先后浮现 | 主体 |
| 11.84 Astra | L3' | Astra 徽章 | scale in + 辉光；标题上移让位 | 接任主体 |
| 16.72 覆盖 | L3'' | 10 张领域卡 | 从右侧按 beat 依次进入，**持续向左漂流**，旧卡渐远渐暗 | 传送带=持续运动 |
| 16.72 | L1 | 相机 | 段B：随卡流轻微右倾平移（滞后 2f） | 视差跟随 |
| 21.04 二百四十九 | L1 | 相机 | 段C：推向论文页 1.0→1.12 | 论文成为主体 |
| 21.04 | L3''' | 论文页 | 从右浮入，页码计数徽章反向旋转入 | 实物证据 |
| 21.04 | L5 | 领域卡流 | 加速左出 + 模糊 | 集体让位 |
| 23.36 Lean | L4 | 绿色认证章 | 单帧 slam 在论文上 + 闪光 + 相机脉冲 | 盖章=打点 |
| 24.4→ | L1 | 相机 | 持续推进论文至满屏过曝 | 转场 |

### S3 · 25.04–43.24 · 意图：一个卡了46年的数字被顶开
- 蒙皮行：chart-grow → 网格 #ececf0、柱色 accent 单色、数字 SF Mono；保留卡内时序 / 缓动 / 几何比例
数字从"左栏文档"改为**叠在 3D 之上的中心主体接力**。

| 节拍 | Layer | 对象 | 动作 | 角色 |
|---|---|---|---|---|
| 25.0 | L1 | 相机(2D+3D同步) | 从亮心拉出 1.15→1.0，接 46s 微轨道环绕 | 转场承接+全场呼吸 |
| 29.20 箱子 | L7 | 线框箱 | 边线 draw-on（mask 旅行） | 取景器即演员 |
| 29.68 塞球 | L3 | 球群 | 逐球 outBounce 落入（保留）+落地小尘光 | 主体 |
| 33.0 | L1 | 相机 | 轨道环绕 15°/10s 不停 | 千维空间感 |
| 36.08 卡在指数 | L3' | 0.5991 大数字 | 中心偏右大字浮现；球群亮度 −25% | 数字接任主体，环境让能量 |
| 38.08 四十六年 | L5 | 1978→2024 时间轴 | 横线 draw + 红章斜落 | 佐证主体 |
| 38.08 | L1 | 相机 | dutch −1.5°（保持不回零） | 僵局的不适感 |
| 41.52 零点六零四四 | L3'' | 0.6044 | **顶替**：0.5991 被划线击落，金色 0.6044 同帧punch入 | 单帧替换=英雄时刻 |
| 41.52 | L4 | 球群材质 | 波浪式转金（保留） | 附着庆祝 |
| 41.52 | L1+L6 | 相机+曝光 | 推击 +0.05 + 三段曝光脉冲 | 多层重音 |
| 42.6→ | L1 | 相机 | 向左 whip-pan + 运动模糊 | 转场 |

英雄时刻层数：L1+L3+L4+L5+L6 = 5 ✓

### S4 · 43.24–56.96 · 意图：两个不同的东西投出同一个影子
| 节拍 | Layer | 对象 | 动作 | 角色 |
|---|---|---|---|---|
| 43.2 | L1 | 相机 | whip 进入后 6f 刹车回稳 | 转场承接 |
| 46.24 孔涅 | L3 | 标题 | 逐字入 | 主体 |
| 48.48 两个群 | L3' | 双 torus knot | 左右对进 + 持续反向自转 | 接任主体（反向=张力） |
| 48.48 | L1 | 相机 | 绕双结轨道 10°/8s | 立体检视 |
| 51.12 冯诺依曼 | L5 | 绿色代数环+光束 | 环自下升起，两结各垂一束光进环 | 「同一影子」具象化 |
| 51.12 | L6 | 环境 | 绿色低幅泛光升起 | 远场照明扩空间 |
| 52.80 三万七千 | L3'' | Lean 代码面板 | 带透视角飞入，**代码行持续上滚** | 主体接力+持续运动 |
| 52.80 | L3' | 双结 | 缩小退后 + 微模糊 | 让位 |
| 55.84 验证通过 | L4 | 绿章 | 单帧 slam + 闪光 + 相机脉冲 | 打点 |
| 56.6→ | — | 全画面 | 绿闪定格 → 3 帧黑 | 震切转场 |

### S5 · 56.96–73.88 · 意图：法医式复查，红色的24小时
全片能量顶点。相机做**纵向爬行**——像逐行读代码。

| 节拍 | Layer | 对象 | 动作 | 角色 |
|---|---|---|---|---|
| 56.96 | L6 | 全场 | 色温转红、vignette 收紧 12% | 反转的空气 |
| 58.08 24小时 | L3 | 时钟 | 指针快扫一整圈 + 红 rim 亮起 | 主体（时间压力） |
| 58.08 | L1 | 相机 | dutch −2° 持续 | 不安 |
| 59.28 剧情反转 | L3' | 标题 | 抖动 slam + 曝光脉冲 + 碎粒散射 | 打点接任 |
| 63.20 追到尾 | L7 | 扫描线 | 沿面板纵向旅行，行随线揭示 | mask 领路 |
| 63.20 | L1 | 相机 | **随扫描线缓慢下移**（滞后 3f） | 跟读代码的眼睛 |
| 66.00 不满足 | L4 | ✗ 标记×2 | 各自单帧 punch + 2px shake | 逐个打击 |
| 66.00 | L5 | 前提条件卡×2 | 从右对位滑入，红边脉动 | 罪证陈列 |
| 72.96 无关 | L3'' | 判词+划线 | 划线 draw；**其余全部沉入近黑** | 终审：只留红字 |
| 73.5→ | L6 | 色温 | 红退、转冷 | 转场冷却 |

### S6 · 73.88–87.44 · 意图：一句早就说过的话，现在听懂了
节奏放慢，用焦点而不是运动讲话。

| 节拍 | Layer | 对象 | 动作 | 角色 |
|---|---|---|---|---|
| 73.9 | L1 | 相机 | 从黑后拉 0.96→1.0，随后全场慢推 | 呼吸复位 |
| 74.72 陶哲轩 | L2+L3 | 照片卡 | 背景保持柔焦，照片由虚转实进入 | rack focus 入场 |
| 76.0 | L3 | 引言 | 逐行浮现（非整块） | 主体 |
| 79.44 严丝合缝 | L5 | 绿色检查卡 | 左入 + ✓ 同窗收束 | 对仗上联 |
| 83.12 真正想问 | L5' | 红色检查卡 | 右入 + ? 持续脉动 | 对仗下联 |
| 84.96 形式正确 | L3' | 两词 | 从两侧滑向中心 | 结论合成 |
| 85.76 不等于 | L3'' | ≠ | 中心 stamp + 相机脉冲；上方内容退后+柔焦 | 唯一焦点 |
| 86.9→ | L4 | ≠ | 碎成金色粒子上飘 | 转场物质 |

### S7 · 87.44–103.0 · 意图：穿过证明的星野，落在一句话上
| 节拍 | Layer | 对象 | 动作 | 角色 |
|---|---|---|---|---|
| 87.4 | L5 | 二十面体星野 | 承接 s6 粒子位置生成 | 溶接完成 |
| 87.4 | L1 | 相机(THREE) | **全程正向 dolly 穿场**，文字挂在不同深度平面上被逐一经过 | 结尾的一镜 |
| 89.20 机器验证 | L3 | 第一句 | 在深度面浮现，经过后退后虚化 | 途经的碑文 |
| 91.28 读懂问题 | L3' | 第二句 | 同上，更近一层 | 递进 |
| 94.16 2000vs24 | L3'' | $2,000 ⚡ 24h | 打点入场 + 曝光脉冲 | 全片符号回收 |
| 98.16 时代 | L3''' | "AI做科研的时代…" | 正面迎来 | 结论上句 |
| 99.84 人类审查 | L3'''' | 金色终句 | punch + 金辉 bloom + 相机沉降刹车 | 英雄收束 |
| 101.5 | L1+L6 | 相机+vignette | 轻微后拉 + vignette 合拢 + 淡出 | 谢幕 |

---

## 2. 未完成 / 未采集清单（必填；preflight 查节存在）

| 项 | 原计划 | 阻塞原因 | 兜底源试过 | 处置 |
|---|---|---|---|---|
| S5 复查段 B-roll（实验室 / 计时器实拍） | V 打底 + 红色时钟叠上 | Pexels / Pixabay "laboratory timer" 命中皆为西式实验室，气质不符 | Mixkit（无合适）、NASA（不相关）、图片降级（Pexels photos 有 2 张可用但为竖构图） | 本片改为纯图形红色 24h 时钟 + 图（竖图走 bed-echo-blur 同源底床）；**这是未完成，不是设计决定** |
| 其余 | 无 | | | |

> 写法纪律：这里每一行都是"想要但没拿到"。拿到了就删行；决定不要了就搬去 §0 写成设计决定 + 依据。两边都不在 = 静默缺口。

## 3. 实现清单（新增共享组件）

1. `src/camera.tsx` — `CameraRig`（path 关键帧 + impulses）、`Plane`（depth 因子）、`useCameraProgress` context
2. `src/life.tsx` — `idle(seed, frame)` 确定性微动、`Retire` 让位包装、状态函数 `stateOf(frame, reveal, handoff)`
3. `src/env.tsx` — `Environment`（分幕色温 + 呼吸 vignette + 扫光 + 曝光脉冲事件表）
4. `MainVideo.tsx` — Sequence 重叠 12–15f，六个转场各自实现；网格背景移入视差层
5. `Subtitles.tsx` — （历史做法，已废弃：现行铁律为素排整句硬现，见 design-language.md §5）
6. 七个场景按矩阵重写（anime.js 时间轴仍按 `msSay` 锚定，冲击帧取锚字起始帧就近整数帧）

验收口径：
- 每个英雄帧数活跃层 4–6，静息帧相机在动（现行口径；旧口径 ≥2 层已废）
- 任意 1 秒抽帧不允许出现「全静止」画面
- 转场处前后镜头运动方向连续（震切除外）
- 量化报告：锚点→帧误差全部 ≤16.7ms（30fps 帧宽之内）

<!-- ===== /file: video-talkcraft/references/shotbook-example.md ===== -->

<!-- ===== file: video-talkcraft/references/taxonomy.md ===== -->

# 口播动效分类体系与卡片总清单

来源五批：① 4 份平台调研（B站中文长视频 / 英文 YouTube / 抖音竖屏短视频 / 模板生态反推；调研原稿为过程资产不随库分发，结论已蒸馏进本文与各卡），
71 条动效条目交叉去重后精选为 19 张调研卡，另按通用纪录片/评测视频语法补 **5 张运镜卡**（静态素材的相机运动）共 24 张
（后按字幕素排铁律删 1 张字幕卡，现存 23）；② 项目实战沉淀的 **8 张实战卡★**
（来自 deepseek-harness demo、ai-math-video、ann_nnng 复刻——生产母本是 template/motion-systems|components
下的 Remotion 组件，同时配 HTML demo；其中运动承接转场六式各自成卡。2026-08-28 定版后
全库各卡的 frontmatter `代码:` 统一指向逐卡自包含 tsx `template/cards/<slug>.tsx`）；③ 2026-08-23 真实视频挖掘：小Lin说·韩股崩盘 + TheAIScaler shorts top10，
13 段分析 208 条观察策展出 **9 张卡（标记◆）**，同时把 13 条变体观察回填进现有卡；
④ 2026-08-24 remocn 项目（Remotion UI 动效注册表）挖掘适配 + 指定搬运 19 张卡（标记◇，后删 1 张现存 **18**；
个别卡"复用指引"里的 `registry/remocn/...` 是该项目的源码路径，仅溯源用，本库不含 registry/ 目录），
其中「界面自己按脚本演戏」的卡当时另立了第 8 个类别「界面剧场」，2026-08-26 用户定版并回**素材呈现**
（它那些同源卡 terminal-typing-log / chat-gpt / claude-code / glass-code-walk / cursor-actor-demo 本来就都在素材呈现里，单卡成类没有意义）；
⑤ 2026-08-25 参考图逐格复刻：用户提供三张动效库 UI 参考图（暖色卡墙 / 深紫卡墙 / 蓝色模板墙），
逐格设计复刻 26 张、经用户审片筛选后留 **20 张卡（标记◈）**（施工书为过程资产，不随库分发）。
⑥ 2026-09-02 社区贡献：douyin-follow-card（外部 PR #6，抖音主页关注卡）。
⑦ 2026-09-05 素材呈现拓展（标记◉）：三题调研（视频底床 / 图片运镜 / 多素材同屏）+ 抖音并列句排版教程逐帧拆解，实验室 47 张原型经用户两轮筛选留 21，按"它是什么"收成 **10 张卡**，2026-09-06 多图巡览停靠拆成照片墙推轨 / 时间线照片带两张 → **11 张**（其余落成规则：实拍底床处理链 design-language §1.2、多素材"关系→版式"表 shot-design §2④′、并列句三纪律 layout §7.1、字与画同起同收）。
⑧ 2026-09-05 video-shotcraft 移植（标记◎）：通读姊妹库 video-shotcraft 的 157 张产品片镜头卡，按四条标准（补口播空白 / 服务讲述不炫产品 / 过运动减法纪律 / 有 Remotion 母本改造成本可控）筛出 18 张做实验室原型，用户定 9 张入库；随后用户点名 14 张再做第二批原型 + 截图里的人物排版 1 张，二审留 10 张入库——合计 19 张◎，2026-09-06 用户删 freeze-frame-annotate 定格圈注、word-relay-filmstrip 改归素材呈现 → **18 张◎**（字幕花字 7 · 强调标注 3 · 数据信息图 3 · 素材呈现 3 · 转场 1 · 人物互动 1）；淘汰理由记在实验室页（过程资产不随库分发）。
共 **7 大类 108 张卡，全部有可播 demo + 自包含 tsx 源码**（各批次数字是入库时的历史记录；2026-08-27 用户定版
删 2 张：word-pop-captions 逐词弹跳字幕——与「底部字幕素排」纪律冲突且再无别的用武之地；
kinetic-center-build 逐词推挤居中）。
优先级：P0 = 跨平台高频、几乎所有头部口播在用；P1 = 某一流派的招牌动作。

通用规律（模板工业共识）：所有口播动效遵循**入场（固定 0.2~0.8s）→ hold（可伸缩）→ 出场（固定 0.15~0.5s）**三段式；
入场永远比出场更用力；同屏重音同一时刻只能有一个。

## 分类

| 类别 | 解决什么问题 | 卡 |
|------|--------------|----|
| 字幕花字 | 静音刷视频时也能接收语音信息与重音 | keyword-pop-highlight, typewriter-reveal, quote-card, type-contrast-emphasis◆, soft-blur-in◇, per-character-rise◇, line-by-line-slide◇, tracking-in◇, slab-punch-title◈, speed-slab-title◈, impact-open-title◈, alt-block-lines◈, outline-box-title◈, count-badge-title◈, quote-bracket-pull◈, word-slot-cycle◎, lead-word-zoom-assemble◎, title-demote-to-label◎, error-retype◎, countdown-arc-scatter◎, flying-words◎, split-text-stagger◎ |
| 强调标注 | 给听觉重音配视觉重音；在素材上指哪看哪 | highlighter-sweep, scribble-annotation, magnifier-detail, callout-line-label, focus-dim-spotlight◆, strike-and-replace◇, ink-underline◇, hand-drawn-ellipse◈, converging-arrows◈, corner-bracket-frame◈, quote-hold-arrow◈, scanline-annotate◎, crash-zoom-punch◎, reticle-lock-on◎ |
| 数据信息图 | 让数字和结论"长"出来而不是贴出来 | number-counter, chart-grow, info-term-card, map-route-pin, line-chart-story-draw◆, ui-prop-theater◆, step-timeline-vertical◈, numbered-step-stack◈, metric-with-sparkline◈, bar-chart-growth◈, number-slab-pop◈, unit-grid-proportion◎, source-converge◎, chip-grid-single-select◎ |
| 素材呈现 | 证据（截图/照片/聊天记录/梗图）的入场仪式感；多素材同屏的排版 × 入场 × 焦点接力；也含「界面按脚本自演」的界面剧场卡 | ui-flow-theater◇, media-pop-in, news-card-desk, **pencil-sketch-draw★**, cursor-actor-demo◆, evidence-scroll-tour◆, motion-blur-slam-in◆, terminal-typing-log◇, chat-message-flow◇, logo-enter◇, chat-gpt◇, claude-code◇, glass-code-walk◇, gooey-morph◇, bed-echo-blur◉, rack-focus-pair◉, still-layout-relay◉, split-compare-slider◉, filmstrip-conveyor◉, grid-to-hero◉, stack-fan-out◉, split-60-40-story◉, gallery-wall-dolly◉, timeline-photo-strip◉, doc-park-left-pill-deal◎, info-card-assemble◎, word-relay-filmstrip◎ |
| 转场结构 | 章节感与节奏切分 | chapter-title-card, shape-wipe-transition, **push-through-transition★**, **overexpose-flip-transition★**, **whip-pan-transition★**, **black-slam-transition★**, **pullback-cool-transition★**, **particle-weld-transition★**, **long-take-world★**, color-slam-beat-card◆, caret-wipe-transition◇, chapter-progress-list◈, line-carry-transition◎ |
| 人物互动 | 真人出镜画面里的信息层与互动引导 | lower-third-nameplate, behind-text-title, subscribe-cta, douyin-follow-card, host-shrink-to-chip◆, x-follow-card◇, chevron-lower-third◈, danmu-bubble-praise◈, parallel-items-with-host◉, host-card-glass-board◎ |
| 运镜 | 静态素材（截图/图片/文档/UI）不死板：相机替素材动起来 | slow-push-in, slow-pull-reveal, tilt-3d-page, sway-parallax, orbit-drift, stage-keyframe-tour◇, cursor-locked-zoom◇, pip-zoom-box◈ |

★ = 实战卡；◆ = 真实视频挖掘卡（第三批）；◇ = remocn 适配卡（第四批，原型是 Remotion 组件，
个别卡「复用指引」里带 `registry/` 源码路径与秒↔帧换算）；◈ = 参考图复刻卡（第五批）；◉ = 素材呈现拓展卡（第七批，2026-09-05）；◎ = video-shotcraft 移植卡（第八批，2026-09-05，「复用指引」里带一行母本溯源）。
这些批次记号只是入库历史，不是分类维度，画廊与配方卡均不展示来源
（2026-08-28 用户定版：卡片 frontmatter 的「参考/复刻」来源字段已删除，画廊来源徽标与按来源搜索一并取消）。
## 输入类型索引（2026-09-05 起，选卡第一道过滤）

SHOTBOOK 每镜先写清输入是哪几种，再在这里挑吃得下的卡。代号：**人** = 口播人物在场（抠像 / 原片，必需或可选）· **V** = B-roll 视频（实拍 / 录屏 / 素材站）· **截图** = 网页 / 界面截图（含长图，与图分开是因为拍法不同：滚 / 巡 / 放大）· **图** = 图片（照片 / 海报）· **界** = 界面自演（无外部素材，卡自带界面）· **文** = 纯文字 / 数据（不吃素材）· **场** = 作用于前后两个场景（转场）。◉ 新卡的 md 开头另有三列表逐项说明。

下表由 `scripts/cards_index.py` 从各卡 frontmatter 的「输入」字段生成（`--write` 重写、`--check` 校验），手改无效；每张卡的真实 props 与图↔视频换法看卡 md「复用指引」。

<!-- gen:by-input start -->
| 输入组合 | 卡（◦ = 没有可换内容的 prop，改文案 / 数据要动 tsx；资源与皮肤类 prop 不算可换内容，见各卡复用指引的 props 行） |
|---|---|
| **图** | filmstrip-conveyor · gallery-wall-dolly · ◦pencil-sketch-draw · rack-focus-pair · split-compare-slider · stack-fan-out · still-layout-relay · timeline-photo-strip |
| **文** | countdown-arc-scatter · error-retype · flying-words · lead-word-zoom-assemble · ◦line-by-line-slide · ◦per-character-rise · ◦soft-blur-in · split-text-stagger · title-demote-to-label · ◦tracking-in · word-slot-cycle · ◦highlighter-sweep · ◦chart-grow · chip-grid-single-select · source-converge · unit-grid-proportion · ◦long-take-world |
| **界** | ◦x-follow-card · ◦glass-code-walk · ◦ui-flow-theater · ◦cursor-locked-zoom |
| **场** | ◦black-slam-transition · ◦caret-wipe-transition · ◦overexpose-flip-transition · ◦particle-weld-transition · ◦pullback-cool-transition · ◦push-through-transition · ◦whip-pan-transition |
| **人(可选) + V** | bed-echo-blur |
| **人(可选) + 图** | ◦gooey-morph · ◦pip-zoom-box |
| **人(必需) + 图** | parallel-items-with-host |
| **人(可选) + 截图** | ◦focus-dim-spotlight · ◦evidence-scroll-tour |
| **人(可选) + 文** | ◦chevron-lower-third · ◦danmu-bubble-praise · ◦lower-third-nameplate · ◦alt-block-lines · ◦count-badge-title · ◦impact-open-title · ◦keyword-pop-highlight · ◦outline-box-title · ◦quote-bracket-pull · ◦quote-card · ◦slab-punch-title · ◦speed-slab-title · ◦type-contrast-emphasis · ◦typewriter-reveal · ◦converging-arrows · ◦corner-bracket-frame · ◦hand-drawn-ellipse · ◦ink-underline · ◦quote-hold-arrow · ◦strike-and-replace · ◦bar-chart-growth · ◦info-term-card · ◦line-chart-story-draw · ◦map-route-pin · ◦metric-with-sparkline · ◦number-counter · ◦number-slab-pop · ◦numbered-step-stack · ◦step-timeline-vertical · ◦chapter-progress-list · ◦chapter-title-card |
| **人(必需) + 文** | ◦behind-text-title |
| **人(可选) + 界** | ◦subscribe-cta · ◦ui-prop-theater · ◦chat-gpt · ◦chat-message-flow · ◦claude-code · ◦cursor-actor-demo · ◦terminal-typing-log |
| **人(可选) + 场** | ◦shape-wipe-transition |
| **V + 图** | grid-to-hero |
| **图 + 截图** | crash-zoom-punch · ◦magnifier-detail · reticle-lock-on · scanline-annotate · ◦scribble-annotation · ◦news-card-desk · ◦orbit-drift · ◦slow-pull-reveal · ◦slow-push-in · ◦stage-keyframe-tour · ◦sway-parallax · ◦tilt-3d-page |
| **图 + 文** | ◦callout-line-label · info-card-assemble · ◦logo-enter |
| **图 + 界** | ◦douyin-follow-card |
| **截图 + 文** | doc-park-left-pill-deal |
| **人(可选) + V + 文** | split-60-40-story |
| **人(可选) + 图 + 截图** | ◦media-pop-in · ◦motion-blur-slam-in |
| **人(必需) + 图 + 文** | ◦host-shrink-to-chip |
| **人(必需) + 文 + 界** | host-card-glass-board |
| **人(可选) + 文 + 场** | ◦color-slam-beat-card |
| **图 + 截图 + 文** | word-relay-filmstrip |
| **图 + 文 + 场** | line-carry-transition |
<!-- gen:by-input end -->

转场选型口诀：镜头边界优先**运动承接六式**（各自一卡，共享
lead/tail 交叠 12~16 帧 + 两侧同向的动量交接纪律，代码同为 `template/motion-systems/transitions.tsx`）——
递进用 push-through，翻页用 overexpose-flip，并列用 whip-pan，最大反转用 black-slam（全片限一次），
收束用 pullback-cool，形态变换用 particle-weld；**一个边界只用一式，一片不要六式全上**（100s 的片 5~7 个边界，
重复用同式比集邮更有风格连贯性）。shape-wipe 是无相机系统时的轻量替代；color-slam-beat-card 是零补间的硬切节拍版；
空间叙事段落用 long-take-world 整段一镜。**图形接力**是第三族（2026-09-05 起）：`line-carry-transition◎` 让 A 镜的一条线自己跑到 B 镜去当容器——
相机六式交接的是动量，它交接的是**图形**；一支片只放一次当招牌转场位，且 A 侧信息要在横移前讲完。

## 语义索引（2026-09-22 起，选卡第二道过滤：这句口播在做什么）

SHOTBOOK 先逐句标语义（词表封闭，定义见下表），再在这里挑**专为这种语义而设**的卡；同一语义里按 G0 能量档挑档位。
由 `scripts/cards_index.py` 从各卡 frontmatter 的「语义」字段生成，手改无效；一张卡只打它专门服务的语义，不打「什么都能配」。

<!-- gen:by-semantic start -->
| 语义 | 定义 | 卡（按能量 低→高；◦ = 内容写死，改文案 / 数据需动 tsx） |
|---|---|---|
| **钩子** | 开场抓注意力的问题 / 反差 / 大数字 | ◦slow-pull-reveal(低) · ◦behind-text-title(中) · ◦count-badge-title(中) · flying-words(中) · ◦number-slab-pop(中) · countdown-arc-scatter(高) · ◦impact-open-title(高) · ◦speed-slab-title(高) |
| **论点** | 一个主张或结论句（没有更具体的类型时归它） | ◦soft-blur-in(低) · ◦alt-block-lines(中) · ◦per-character-rise(中) |
| **例证** | 用实例 / 证据 / 素材支撑上一句 | bed-echo-blur(低) · ◦evidence-scroll-tour(低) · ◦slow-push-in(低) · still-layout-relay(低) · ◦sway-parallax(低) · ◦chat-gpt(中) · ◦chat-message-flow(中) · ◦claude-code(中) · ◦danmu-bubble-praise(中) · filmstrip-conveyor(中) · gallery-wall-dolly(中) · ◦glass-code-walk(中) · ◦gooey-morph(中) · ◦host-shrink-to-chip(中) · info-card-assemble(中) · ◦media-pop-in(中) · ◦news-card-desk(中) · parallel-items-with-host(中) · stack-fan-out(中) · ◦stage-keyframe-tour(中) · ◦terminal-typing-log(中) · ◦tilt-3d-page(中) · word-relay-filmstrip(中) · crash-zoom-punch(高) · ◦motion-blur-slam-in(高) |
| **数据** | 数字、比例、增长、金额出现 | ◦focus-dim-spotlight(低) · unit-grid-proportion(低) · ◦bar-chart-growth(中) · ◦chart-grow(中) · chip-grid-single-select(中) · ◦count-badge-title(中) · ◦line-chart-story-draw(中) · ◦metric-with-sparkline(中) · ◦number-counter(中) · ◦number-slab-pop(中) · countdown-arc-scatter(高) · ◦keyword-pop-highlight(高) |
| **对比** | A vs B、前后、优劣并置 | ◦ink-underline(低) · rack-focus-pair(低) · ◦type-contrast-emphasis(低) · ◦alt-block-lines(中) · ◦chart-grow(中) · chip-grid-single-select(中) · gallery-wall-dolly(中) · grid-to-hero(中) · ◦line-chart-story-draw(中) · split-compare-slider(中) |
| **列举** | 并列几项（清单 / 要点 / 盘点），无先后 | still-layout-relay(低) · ◦alt-block-lines(中) · ◦count-badge-title(中) · filmstrip-conveyor(中) · gallery-wall-dolly(中) · grid-to-hero(中) · ◦line-by-line-slide(中) · ◦media-pop-in(中) · ◦numbered-step-stack(中) · parallel-items-with-host(中) · split-60-40-story(中) · stack-fan-out(中) · title-demote-to-label(中) · word-relay-filmstrip(中) · word-slot-cycle(中) |
| **定义** | 解释一个术语 / 概念是什么 | ◦info-term-card(中) · ◦outline-box-title(中) · ◦pencil-sketch-draw(中) |
| **步骤** | 有先后顺序的流程 / 做法 | ◦cursor-actor-demo(中) · ◦cursor-locked-zoom(中) · host-card-glass-board(中) · ◦line-by-line-slide(中) · ◦long-take-world(中) · ◦map-route-pin(中) · ◦numbered-step-stack(中) · parallel-items-with-host(中) · ◦pencil-sketch-draw(中) · split-60-40-story(中) · ◦step-timeline-vertical(中) · timeline-photo-strip(中) · title-demote-to-label(中) · ◦ui-flow-theater(中) · ◦ui-prop-theater(中) |
| **转折** | 但是 / 然而 / 其实——推翻或修正前文 | error-retype(低) · ◦type-contrast-emphasis(低) · ◦quote-hold-arrow(中) · ◦strike-and-replace(中) · word-slot-cycle(中) · ◦black-slam-transition(高) · lead-word-zoom-assemble(高) · ◦slab-punch-title(高) |
| **设问** | 抛出问题不立即回答 | title-demote-to-label(中) |
| **金句** | 可以单独摘出的总结句 / 名言 | ◦per-character-rise(中) · ◦quote-bracket-pull(中) · ◦quote-card(中) · ◦quote-hold-arrow(中) · split-text-stagger(中) · ◦tracking-in(中) · ◦color-slam-beat-card(高) · lead-word-zoom-assemble(高) |
| **标题** | 片名 / 题眼 / 段落大标题（不是章节翻页） | ◦corner-bracket-frame(低) · ◦behind-text-title(中) · ◦count-badge-title(中) · ◦outline-box-title(中) · split-text-stagger(中) · title-demote-to-label(中) · ◦tracking-in(中) · ◦impact-open-title(高) · lead-word-zoom-assemble(高) · ◦slab-punch-title(高) · ◦speed-slab-title(高) |
| **引用** | 引别人的话或给出处 | bed-echo-blur(低) · ◦chevron-lower-third(低) · ◦evidence-scroll-tour(低) · ◦highlighter-sweep(低) · ◦lower-third-nameplate(低) · ◦chat-message-flow(中) · ◦danmu-bubble-praise(中) · doc-park-left-pill-deal(中) · ◦douyin-follow-card(中) · ◦news-card-desk(中) · ◦quote-bracket-pull(中) · ◦x-follow-card(中) |
| **自我介绍** | 讲者报自己的名字 / 身份 | ◦chevron-lower-third(低) · ◦lower-third-nameplate(低) · ◦logo-enter(中) |
| **介绍他人** | 介绍某个人 / 账号 / 嘉宾 | ◦chevron-lower-third(低) · ◦lower-third-nameplate(低) · ◦douyin-follow-card(中) · ◦x-follow-card(中) |
| **号召** | 关注 / 点赞 / 订阅 / 去做某事 | ◦subscribe-cta(中) |
| **时间地点** | 时间戳、地点、事件坐标 | ◦typewriter-reveal(低) · ◦map-route-pin(中) · timeline-photo-strip(中) |
| **空间叙事** | 在一个连续空间 / 地图 / 长画布里移动讲述 | ◦long-take-world(中) · ◦map-route-pin(中) · ◦stage-keyframe-tour(中) |
| **机制** | 多对一 / 因果 / 流程关系图（讲“怎么运作”） | source-converge(中) |
| **选择** | N 选一、决策、排除 | chip-grid-single-select(中) · grid-to-hero(中) |
| **过程演示** | 界面 / 操作按脚本自演 | ◦chat-gpt(中) · ◦chat-message-flow(中) · ◦claude-code(中) · ◦cursor-actor-demo(中) · ◦cursor-locked-zoom(中) · ◦terminal-typing-log(中) · ◦ui-flow-theater(中) · ◦ui-prop-theater(中) |
| **章节** | 分章 / 翻页 / 进度 | ◦chapter-progress-list(中) · line-carry-transition(中) · title-demote-to-label(中) · ◦chapter-title-card(高) · ◦impact-open-title(高) · ◦overexpose-flip-transition(高) · ◦shape-wipe-transition(高) |
| **转场** | 镜头边界处置（作用于前后两镜） | ◦pullback-cool-transition(低) · ◦caret-wipe-transition(中) · line-carry-transition(中) · ◦long-take-world(中) · ◦particle-weld-transition(中) · ◦push-through-transition(中) · ◦black-slam-transition(高) · ◦chapter-title-card(高) · ◦color-slam-beat-card(高) · ◦overexpose-flip-transition(高) · ◦shape-wipe-transition(高) · ◦whip-pan-transition(高) |
| **强调** | 在素材或文字上指哪看哪 / 划重点 | ◦evidence-scroll-tour(低) · ◦focus-dim-spotlight(低) · ◦highlighter-sweep(低) · ◦ink-underline(低) · still-layout-relay(低) · ◦type-contrast-emphasis(低) · ◦callout-line-label(中) · ◦converging-arrows(中) · ◦glass-code-walk(中) · ◦hand-drawn-ellipse(中) · ◦magnifier-detail(中) · ◦pip-zoom-box(中) · scanline-annotate(中) · ◦scribble-annotation(中) · ◦stage-keyframe-tour(中) · crash-zoom-punch(高) · ◦keyword-pop-highlight(高) · reticle-lock-on(高) |
| **氛围** | 素材当底床不当主体 | ◦orbit-drift(低) · ◦sway-parallax(低) · flying-words(中) · ◦tilt-3d-page(中) |
| **结尾** | 收束 / 谢幕 / 落幕 | ◦logo-enter(中) · ◦quote-card(中) |
<!-- gen:by-semantic end -->

---


以下七类**每卡一行**：`slug` 批次记号 中文名 · P 级 · 能量档 —— 一句话（含与兄弟卡的区分）。
参数 / 命门 / 已知坑 / 落位自检一律看 `references/cards/<slug>.md`（**唯一正主**，本文不再复写），实现看 `template/cards/<slug>.tsx`。
两条全库口径（2026-09-22 审计后定）：**能量档只有 低 / 中 / 高 三档**（判据：低 = 只有淡入 / 解糊 / ≤1.02 缩放 / 小位移；中 = 明确位移、back.out 回弹或 ≥1.05 缩放；高 = 拍击 / 急推 / 整屏变化 / 震动）；
tsx 的 `meta.durationInFrames` = 卡内动画长度 + 0.4s 收尾垫，md「时长」按动画长度写，两者差 0.4s 不是错。例外六张（meta 与动画长度差得更多）：behind-text-title（hold 是循环 idle，meta 3.17s 只是截断）、focus-dim-spotlight（meta 9.17s 比时间表多 1.2s）、media-pop-in（落位后 idle 到 meta 结束，无退场段）、magnifier-detail（无限扫视，meta 3.37s 为截断）、typewriter-reveal（尾垫约 2s）、info-term-card（3.96s 出画后 meta 拖到 6.57s 空台）。

## 字幕花字

> 底部字幕素排铁律（正主 design-language.md §5）：跟读字幕**不加任何动效**、整句硬现；唯一例外 keyword-pop-highlight 且全片 ≤3 次。
> 本类其余各卡的作用对象都是**标题/金句/要点等独立文字层**，不是底部字幕。

- **keyword-pop-highlight** 关键词弹出强调 · P0 · 高 —— 字幕念到关键词时该词带色块弹出回落、画面微震；本类唯一允许作用于底部字幕的动效，每片最多三次。
- **typewriter-reveal** 打字机档案戳 · P1 · 低 —— 等宽字体逐字符敲出时间地点戳，末尾方块光标闪烁，档案调取感；它是标注不是标题，占角落不占中央。
- **quote-card** 金句大字卡 · P1 · 中 —— 金句时刻人物让位，实底板盖屏、多行大字逐行弹出、停留后整卡退场；要仪式感的金句用它，不想遮人物用 quote-bracket-pull。
- **soft-blur-in** ◇ 柔焦淡入 · P1 · 低 —— 整句像被镜头对焦出来，边解糊边淡入、位移先停；本类最低一档能量（与 typewriter-reveal 同档），可以连着上五句都不闹，不能承担强调。
- **per-character-rise** ◇ 逐字升起 · P1 · 中 —— 每个汉字从下方升到位，位移与淡入分走两条缓动、零模糊零缩放；有方向有力道零回弹的整句立起，同类唯一"有劲但不跳"的一档。
- **line-by-line-slide** ◇ 逐行滑入 · P1 · 中 —— 多行要点一行一行从左滑入、读完再向右穿出去；本类唯一的多行要点卡（不带底板），要让位用 quote-card、边讲边挂用本卡。
- **tracking-in** ◇ 字距收拢 · P1 · 中 —— 一行大标题字距从极松收拢、同一条 spring 同时解糊，零回弹长缓收；标题动作（不是字幕），一片限一两次。
- **slab-punch-title** ◈ 重点放大 · P0 · 高 —— 两行标题的重点词坐在斜切色块上，块先从中心撑开、字后硬切砸落；本批标题色块类的基准式，"铺垫 + 结论"对照句专用。
- **speed-slab-title** ◈ 速度块标题 · P1 · 高 —— 副题斜切色块从画外冲入到位、块左缘张开速度线残影随即淡尽，字比块慢半拍在追；同类里唯一带速度语义的一张。
- **impact-open-title** ◈ 冲击开场 · P0 · 高 —— 整句一次砸出、末词延后换强调色再 punch，四角取景框与点阵网格更慢更淡地做衬；开头三秒钩子，全片限一两次。
- **alt-block-lines** ◈ 双色块对句 · P1 · 中 —— 两行对句各坐在贴合色块上、块从左展开把字"刷"出来，同结构反色表达对照；同类唯一的双行对照块式标题，做关系不做强调。
- **outline-box-title** ◈ 描边框标题 · P1 · 中 —— 圆角描边框沿路径一笔画完一圈，闭合后实心 chip 展开、chevron 依次点亮；给结论加框，机器画的框（对照 hand-drawn-ellipse 的手绘线）。
- **count-badge-title** ◈ 数字重音标题 · P1 · 中 —— 数字先单独缩到位并落定换色，量词被它从右缘推出、第二行再跟上；开场承诺条数（"三个方法"），数字是主语，靠先后不靠砸。
- **quote-bracket-pull** ◈ 引号夹句 · P1 · 中 —— 两枚大引号同帧从对角推入夹出引文区，金句在其中错峰淡入、末行荧光笔扫过；不盖底板的金句卡（人物全程在画面里），"被引用"的话用它。

## 强调标注

- **highlighter-sweep** 荧光笔高亮扫过 · P0 · 低 —— 半透明黄色荧光笔从左到右扫过引用文段的关键句，同帧其余文字压暗——给文档里的一整句划重点，跟着朗读走。
- **scribble-annotation** 手绘圈注箭头 · P0 · 中 —— 马克笔质感的圈/下划线/箭头按真实笔顺在素材截图上现场画出，画完干净静置；作用对象是素材而不是文字。
- **magnifier-detail** 局部放大镜 · P1 · 中 —— 截图目标处弹出圆形放大镜落到旁边空白区，本体同步压暗、连接线指回出处，一次回答"在哪"和"是什么"。
- **callout-line-label** 标注引出线 · P1 · 中 —— 目标上圆点亮起、折线向外生长、线端文字标签揭示，三拍严格串行一气呵成；本类唯一带文字标签的引线（给这个东西起个名）。
- **strike-and-replace** ◇ 划线纠错替换 · P1 · 中 —— 语义色横线划穿旧值，新值从同一位置升起顶上来；本类唯一能表达"否定"的一张，划穿的动作本身就是论证。
- **ink-underline** ◇ 墨迹下划线 · P1 · 低 —— 起笔压满、收笔提细的墨色缎带沿关键词下方生长，画完静置；本类唯一有笔压的下划线，比荧光笔轻、比圈注准，作用在句子里的一个词上。
- **hand-drawn-ellipse** ◈ 手绘圈重点 · P0 · 中 —— 一笔逆时针画出的歪椭圆圈住句子里的关键短语，圈画完短语才 punch 一拍；指认单个短语，比双线强、比爆点字克制。
- **converging-arrows** ◈ 双箭头聚焦 · P1 · 中 —— 两支手绘箭头从对角几乎同时画向关键词、箭尖留白不戳字，都到位后词才换色；本类指向性最强的一张（箭头有方向，圈没有）。
- **corner-bracket-frame** ◈ 对角角框 · P1 · 低 —— 左上与右下两个 L 形角框同帧从外侧对角收进来、框先立住再放标题两行；定题用的取景动作（"本集只讲这一件事"），给整块划边界（reticle-lock-on◎ 是四角飞入咬合的锁定版）。
- **quote-hold-arrow** ◈ 金句停留 · P1 · 中 —— 三行金句先全部平淡落地、末行停一拍后才升级高亮并 punch，然后停住；强调整句而不是词，句子自己升级（highlighter-sweep 是笔划过句子）。

## 数据信息图

- **number-counter** 数字滚动计数 · P0 · 中 —— 大号数字从 0 滚到目标值，先快后慢、落定轻弹一拍后单位淡入，变体是逐位滚轮高位先停；展示量级"滚出来"的过程。
- **chart-grow** 图表生长 · P0 · 中 —— 坐标轴先淡入，柱子依次错峰长出、柱顶数字跟着弹出，最高柱高亮并轻 punch；用于逐项列举/对比（整体形状用 bar-chart-growth）。
- **info-term-card** 名词解释悬浮卡 · P1 · 中 —— 说到专业名词时，图标+词条+两行释义的圆角卡从人物对侧滑入，停留期间缓慢上下浮动像悬浮着，念完原路滑出。
- **map-route-pin** 地图路线图钉 · P1 · 中 —— 地图上虚线按叙事顺序从 A 城生长到 B 城，到达瞬间图钉从上方砸下压扁回弹，地名标签从钉侧滑出。
- **step-timeline-vertical** ◈ 竖向步骤线 · P1 · 中 —— 竖线从上往下画，线推到哪节点就在哪弹出、文字跟着淡入，到位后首节点升级成空心环标当前步；用于有先后依赖的流程（并列清单用 numbered-step-stack）。
- **numbered-step-stack** ◈ 编号步骤堆入 · P1 · 中 —— 带编号方块的横条从右侧均匀错峰依次堆入，每枚落定时编号块 punch 一下确认，整组到位后轻微上浮收成一件事；用于并列清单（有先后依赖用 step-timeline-vertical）。
- **metric-with-sparkline** ◈ 数字带趋势 · P0 · 中 —— 大数字滚动与下方小折线同刻起跑，数据点跟线端弹出，数字停住那帧单位和箭头才出现；"一个数 + 它怎么来的"双层信息（孤立数字用 number-slab-pop）。
- **bar-chart-growth** ◈ 柱状增长 · P0 · 中 —— 基线画出后多根柱以密错峰一路升起读作一次连续抬升，最后一根到顶时结论 chip 弹出；讲连续区间趋势的整体形状（不是逐项对比，那用 chart-grow）。
- **number-slab-pop** ◈ 数字弹出 · P0 · 中 —— 实色块先落定，块稳住后巨大整数一次弹出、小数与单位延后淡入、说明行最后上浮；一次弹出的结论感数字（要展示过程用 number-counter / metric-with-sparkline）。

## 素材呈现

> 选卡前先定全片节奏：单条 B-roll 按 shot-design.md §2⑦「七式」选、相邻镜不同式；同一张呈现卡连用 3 镜或全片 >1/3 过不了 preflight（cinematography.md §4.5 第 9 条）。

- **media-pop-in** 素材弹入堆叠 · P0 · 中 —— 截图/照片带白边投影从 80% 回弹到位、随机歪斜层层压角、多张错峰拍上桌，是证据素材"歪着叠"的入场。
- **news-card-desk** 新闻卡片划重点 · P0 · 中 —— 新闻截图包成白色圆角卡片歪着滑上桌，红色下划线等朗读到关键句才扫过，第二张卡压叠上来，卡片全程极缓 Ken Burns。
- **terminal-typing-log** ◇ 终端逐行推进 · P1 · 中 —— 通用终端当证据的 stdout 流水（对照 claude-code◇ 的因果链）：命令逐字符敲、日志成簇蹦出、缓冲区整跳零插值、`...` 行冻结制造悬念。
- **chat-message-flow** ◇ 聊天记录自演 · P0 · 中 —— 把聊天截图从过去式改成现在进行时：我方经输入框逐字打出再上屏、对方先出三点气泡再回，时刻表由文本长度自动生成。
- **logo-enter** ◇ Logo 登场 · P1 · 中 —— 本类唯一的身份标识入场（其余都是证据素材）：圆牌 spring 弹到位、字标推出、描环合拢三拍收尾，落定即终帧不加微动。
- **chat-gpt** ◇ ChatGPT 对话框 · P1 · 中 —— AI 聊天产品自演（单行药丸 + 首屏三件套那一路）：三件套错峰淡入、提示词打进药丸、语音键原地变形成发送键、回答流式吐出，产品皮即内容。
- **claude-code** ◇ 编码智能体终端 · P1 · 中 —— 演因果链而不是 stdout 流水：Claude Code 终端里命令敲入后「工具调用 → 结果 → diff → 结论」逐行蹦出，讲"AI 帮我写代码"用本卡（界面自己生成内容、没有鼠标光标，只有文本光标）。
- **glass-code-walk** ◇ 玻璃代码走读 · P1 · 中 —— 带观众读一小段真实代码，整块都在但同时只有一行是亮的：相机与高亮带同源逐行走读、读完拉回全景，是 cursor-locked-zoom◇ 的逐行浅档。
- **gooey-morph** ◇ 图块拼入 · P1 · 中 —— 素材呈现里的"并列拼"（另两张是歪着叠与同向怼）：几张图各走 L 形路径、起飞不按左右顺序，严丝合缝拼成一条横排，拼完即落点。
- **ui-flow-theater** ◇ 界面流程剧场 · P0 · 中 —— 界面剧场子类的架构母卡，讲完整流程：整套灰阶假面板按一张时刻表自演，光标走位与控件换态共享同一时间源，成功 toast 收尾（只演三四个动作用 cursor-actor-demo◆）。

### 界面剧场子类（整套界面按脚本自演）

同源卡 ui-flow-theater◇ / terminal-typing-log◇ / chat-message-flow◇ / chat-gpt◇ / claude-code◇ / glass-code-walk◇ / cursor-actor-demo◆ 共用下面这套纪律。

产品/工具类口播讲"这个东西怎么用""AI 现在在干什么"时，常见三条路都有硬伤：录屏（光标 12px 看不见、
节奏由手速决定、要脱敏就废了）、截图硬切（丢掉"这一步导致了那一步"的因果）、逐个控件各做动效
（每个控件一条时间线，排到第三个就对不上拍了）。这类卡是第四条路：**把整套界面当一个演员，给它一份剧本**
——界面按脚本时间轴自演，观众看到的是"这一下导致了那一变"的因果链，而制作者只维护一张表。
与本类其余各张的区别在于素材的时态：那些是把已发生的证据**拍上台**（过去式），本子类是让界面**当场演**（现在进行时）；
与「运镜」的区别在于动的是谁：运镜里动的只有相机、界面本身一个像素不改，本子类里相机不动、界面自己换态。

共有纪律（本子类通用）：
- **时间只从一处进入**：一张时刻表（`STEPS` / `FRAGMENTS` / 轮数）是唯一的时间源，
  光标、控件、结果都是它的函数。对齐靠共享常量，不靠两处手数——这是能排到三拍以上还不散架的全部原因。
- **换态是硬切，不是动画**：界面状态变化要一帧到位（`transition: none`）或极短（0.27s 一档全卡共用）。
  给状态变化配过渡就变成"样式在做动画"，观众读不出是哪一下触发的。
- **时刻表按内容长度自动累加**，改文案不用重排时间；各动作时长是**手感常量**（不跟着语速缩放——
  语速快时该减少拍数，而不是加快每一拍）。
- **灰阶中性皮 + 唯一语义色**：控件全部灰阶线框，语义色只留给收尾那一拍（成功 toast / 品牌红那一行）。
  做成某个真实产品的配色，观众开始读平台品牌，且你要为仿真背锅。

## 转场结构

- **chapter-title-card** 章节标题卡 · P0 · 高 —— 段落切换时全屏色块压入，超大章节编号先落位、章节名随后遮罩揭示，短停后同向扫出切回口播；只宣告新一幕开始、不给全片进度；每章一套主题色 + 一个本章相关的线稿 motif。
- **shape-wipe-transition** 色块扫屏转场 · P0 · 高 —— 两三层同色系色块错峰从同一方向扫过全屏，换场藏在遮挡帧里观众看不见切换瞬间；色块是不透明遮挡物，无相机系统时的轻量转场。
- **caret-wipe-transition** ◇ 光标擦除转场 · P1 · 中 —— 一条文本光标从左到右扫过完成换场，走过处新场景沉降解糊、未到处旧场景上浮失焦；本库第一个边界本身有语义（编辑器隐喻）的转场。
- **chapter-progress-list** ◈ 章节进度 · P1 · 中 —— 暗场里章节目录错峰滑入、站定后只高亮当前一条并收合电影角框；本类唯一带进度信息的转场，要给全局位置时用它而非 chapter-title-card。

## 人物互动

- **lower-third-nameplate** 人名条展示牌 · P0 · 低 —— 画面左下色条横向展开、姓名遮罩揭示、头衔跟进的三段接力人名条，停留后反向收回；克制的新闻/访谈感，是"这个人是谁"的最小信息。
- **behind-text-title** 人后大字视差 · P1 · 中 —— 超大标题从人物身后升起、下缘被人物遮挡穿出，hold 期两层反向极缓漂移读出伪 3D 层次；人物层需抠像。
- **subscribe-cta** 多平台关注 CTA · P1 · 中 —— 控件弹入→光标弧线移入→状态翻转+确认动效的关注示范，YouTube 订阅/B站三连/通用关注三式共用一套机制、落地只留一段；用在收尾号召观众去点。
- **x-follow-card** ◇ 关注卡弹出 · P1 · 中 —— X 资料卡弹入后十层内容错峰 blur-in 落位，光标走过去点"关注"、按钮翻转且粉丝数 +1；介绍别人的社会证明道具，对照 subscribe-cta 是"卡而非控件、证明而非号召、中段而非收尾"。
- **douyin-follow-card** 抖音主页关注卡 · P1 · 中 —— 抖音用户主页卡弹入、内容错峰 blur-in、光标点"＋关注"翻转并联动"发私信"，粉丝数静态；x-follow-card 的抖音版，介绍"某人在抖音上"时用。
- **chevron-lower-third** ◈ 动态人名条 · P1 · 低 —— 姓名推出、职称 chip 展开、三枚 chevron 依次点亮收尾的人名条；比 lower-third-nameplate 多一档节目感，正式访谈与纪录片仍用那张。
- **danmu-bubble-praise** ◈ 弹幕气泡 · P1 · 中 —— 四枚评论气泡错峰从两侧飘入、短停后上移淡出，进出交叠且只有一枚强调色；"评论区都在说"的社区共识道具，对照 x-follow-card 的个人档案，本卡是多人即时共识。

## 运镜

静态素材（网页截图/图片/文档/UI 界面）一贴上屏画面就死——观众没有理由把眼睛留在上面。
**网页类证据更进一步：禁止静态贴屏，必须"拍"**——滚 / 巡 / 放大 / 划四种拍法的选型表在
shot-design.md §2④「网页拍摄」，采集规格（全页 2× 长图 + DOM 坐标 JSON）在 broll-sources.md「网页拍摄素材采集」。
前七张卡不改素材一个像素，只让**相机**动（末一张 pip-zoom-box◈ 是例外，见下）：素材满画幅铺在一个"相机层"里，相机层是唯一被 transform 的元素。
选型：**默认用 slow-push-in**（任何静态素材的底噪运镜）；素材信息量大且要揭示规模用 slow-pull-reveal；
把页面当"产品/作品"展示用 tilt-3d-page；素材比画幅宽得多用 sway-parallax；
页面要在屏上停留很久（长讲述）用 orbit-drift；素材超出画幅且要"讲到哪儿镜头停到哪儿"用 stage-keyframe-tour◇；
目标本身在移动（光标/进度点/正被填的字段）用 cursor-locked-zoom◇；
要在保留全景的同时长期展示一个局部用 pip-zoom-box◈（唯一不动整幅画幅的一张）。
**一段素材只用一式**——推着又摇着读作手抖。
2D 两式（推/拉）与 3D 三式可以串联：tilt-3d-page 建立立面姿态 → orbit-drift 接管 hold 期底噪是推荐组合。
前五张都是**单段运动 + hold**（一段一个姿态目标），后两张◇是**多目标寻址**：一个走预设兴趣点路径、
一个锁运行时才知道位置的移动目标——这是"单段运镜"与"路径/跟拍"的分界。

共有纪律（前五张通用，也是与其他类别最大的差别）：

- **相机永不静止**：hold 期必须以主段末速继续走。前五张卡的 ease 都是"末速非零"的自定义曲线
  `p + (1−r)·p²·(1−p)`（起速=平均速、末速=r×平均速），**不能用 `power2.out`**——它末速为零，到位那帧镜头停死。
  例外有两处：tilt-3d-page 的立起段是一次"摆放"动作（有始有终的事件），允许收住；
  **stage-keyframe-tour◇ 与 cursor-locked-zoom◇ 整条反过来**——它们的 hold 必须**真的静止**
  （巡游的信息量在 hold 里、跟拍要留时间让人读完），静止在那两张卡里是功能而不是失误。
- **时长跟着口播走，运动量不跟**：`zoomTo`/`ampRot` 这些是观感常量（换时长不改），时长才是节奏变量。
- **可读性是硬上限**：3D 倾斜 ≤25°（超过远端正文读不了）、摇移 ≤190px/s@960 宽（超过观众扫读跟不上）、
  推进 ≤1.2（超过位图发虚）。3D 卡的透视值 900~1200px——太小读作鱼眼变形，不是空间。
- **3D 三式的投影必须跟着姿态变**：与页面同处 `preserve-3d` 空间（被透视自动压扁）+ 浓度随倾斜加深
  + 位置往倾斜反侧偏移。投影不动 = 页面读作贴纸而不是浮在空间里的实体。
- 素材分辨率 ≥ 画幅 × 最大缩放（1080p 画幅推到 1.15 需 ≥2210px 宽的截图），否则运镜即变糊。

- **slow-push-in** 缓推特写 · P0 · 低 —— 静态素材的默认底噪运镜：相机极缓匀速推向兴趣点、hold 期沿末速续推不停死，Ken Burns 的推镜半边。
- **slow-pull-reveal** 缓拉全貌 · P0 · 低 —— 从局部细节匀速拉远到素材原样满画幅以揭示规模，语义与 slow-push-in 互为反面，一段只能选一个方向。
- **tilt-3d-page** 3D 立面展示 · P1 · 中 —— 正视静置后倾斜成 3D 立面，把页面从"信息"变成"物件"，作品/产品展示或让页面降权为背景道具时用。
- **sway-parallax** 左右摇移 · P1 · 低 —— 素材比画幅宽得多时，镜头在长页前横向匀速扫过并极轻 rotateY 跟随，纵向长页归 evidence-scroll-tour。
- **orbit-drift** 环绕微漂 · P1 · 低 —— 两轴正弦相位错开合成闭合椭圆轨迹的环绕微漂，"镜头呼吸"的高级版、本类唯一可无限持续的运镜，页面要长期停留时用。
- **stage-keyframe-tour** ◇ 长页兴趣点巡游 · P1 · 中 —— 超出画幅的长页躺在 3D 舞台上，相机沿多关键帧路径依次停靠预设兴趣点再拉开全貌；相机动页面不动，与页面自滚的 evidence-scroll-tour 相对。
- **cursor-locked-zoom** ◇ 光标锁定跟拍 · P1 · 中 —— 小屏念长命令的唯一解法：相机锁死在光标上跟拍、镜头由打字进度驱动，目标位置运行时才知道，收尾拉回全景。
- **pip-zoom-box** ◈ 画中画放大 · P1 · 中 —— 取景框带着框内画面飞到侧边定居成画中画，本类唯一保留全景的一张；看一眼就撤用 magnifier-detail，要长期挂着用本卡。

## 实战卡（项目沉淀，详情见各卡文件）

- **pencil-sketch-draw** ★ 铅笔手绘揭示 · P1——铅笔骑在 SVG 路径笔尖当场画图，画完干净静置。来自 ann_nnng 手绘卡片技法复刻。代码 template/cards/pencil-sketch-draw.tsx（自带路径采样，母本 template/components/pencil.tsx）。

**运动承接转场六式 ★**（六张卡，共享同一套纪律与同一份代码）：六式同属"动量交接"家族：相邻 Sequence 交叠 12~16 帧，`ShotFade` 只管像素淡化，方向与加速度全在两侧相机曲线里；
**两侧必须同向**（方向断裂比硬切更糟），**一个边界只用一式**。来自 ai-math-video 全片实战，
代码同为 template/motion-systems/transitions.tsx（CamKey 生成器 + 叠加层）。

- **push-through-transition** ★ 推穿转场 · P0——出场加速推到 1.35x + 升 blur，入场从模糊的 1.16 高位反向沉降。家族基准式（无叠加层、只有 scale 轴），最安全、可反复用。生成器 pushThroughOut + settleIn。
- **overexpose-flip-transition** ★ 过曝翻页转场 · P0——推向证据物至 1.5x + 重音层以切点为锚冲顶（切前 0.26s 升 / 切后 0.42s 落），入场从亮心拉出。**重音极性随底色换**：深底白色径向过曝 0.42~0.55，白底改压暗一拍。生成器 blowoutOut + settleIn(from 1.3) + Overexpose。
- **whip-pan-transition** ★ 横甩转场 · P0——出场沿横轴甩出 + 8px 方向模糊 + 1.4° 微旋，入场从**同方向对侧**滑回、0.35s 刹住 + 二段回稳只收旋转。处理并列关系；交叠最短（≈9 帧，糊帧本身是遮挡）。生成器 whipOut/whipIn（两侧同 dir）。
- **black-slam-transition** ★ 黑震切转场 · P0——出场相机定格一拍（全片唯一静止）+ 重音冲顶 + 最后 1 帧 hardOut 零交叠，入场满亮直切且开场自带运动（三段递减震位 + 从 1.10 后拉刹住）。**全片唯一硬切，限用一次**，留给最大反转。无生成器（出场是"不加键"）。
- **pullback-cool-transition** ★ 后拉冷却转场 · P0——出场相机收住、内容自己沉暗失焦交出画面；入场是全片唯一 scale<1 起步的后拉（0.90→0.99，settle 0.90s 最慢，交叠 16 帧最长）。全 sine 系缓动的呼吸质感，用在情绪收束点。生成器 pullBackIn。
- **particle-weld-transition** ★ 粒子溶接转场 · P0——出场主体碎成粒子向上飘散，入场用**同 seed** 的同一批粒子从下方继续上升、在新主体位置收拢，主体滞后 0.30s 成形。唯一动量在物质而非相机上的一式；语义必须真的是"同一件东西换形态"。组件 Shatter + 两侧同 seed ParticleDrift。
- **long-take-world** ★ 长镜头世界画布 · P1——内容钉在世界坐标，一台相机随讲述连续运镜，useArrive 让内容在镜头到达前成形。代码 template/motion-systems/longtake.tsx（已实战：deepseek-harness-v2 V3 幕）。

## 真实视频挖掘卡（第三批◆，详情见各卡文件）

来源：小Lin说·韩股崩盘（douyin 362s）+ TheAIScaler shorts 播放量 top10。两频道语言差异值得按调性选卡——
**TheAIScaler** = 硬切 + 高饱和纯色底 + 字体对比的高频节拍（平均 1.5~3s 一个视觉事件），信息靠节奏压强；
**小Lin说** = 图表推演 + 聚焦压暗 + 长页证据的推理链，信息靠空间与因果。

- **type-contrast-emphasis** ◆ 字体对比重音 · P0 · 字幕花字——重音词换衬线斜体放大 1.5~2 倍（或换唯一强调色），强调靠字形气质落差而非弹跳；与 keyword-pop-highlight 同句互斥。
- **focus-dim-spotlight** ◆ 聚焦压暗切换 · P0 · 强调标注——讲到哪里哪里亮：目标保持原亮并点亮发光描边，其余压暗 40% 或整页高斯模糊，焦点随口播 0.2s 跳转。
- **line-chart-story-draw** ◆ 折线分段推演 · P0 · 数据信息图——折线不一次画完：新线段从拐点向右生长、标签段完成即弹出，对比虚线从同一拐点岔出第二种未来。
- **ui-prop-theater** ◆ 界面道具剧场 · P1 · 数据信息图——拟物 UI 道具（进度条 + 清单，tsx 无滑杆）的状态按语音节拍分段跳进，界面自己演戏而不是跑 loading；输入是卡内自演的界面（界）。
- **cursor-actor-demo** ◆ 光标演员演示 · P0 · 素材呈现——超大系统光标在卡内自演的 UI 线框上移动-悬停-点击，元素即时响应（控件要活，截图贴不上），一个动作对齐一个口播词。
- **evidence-scroll-tour** ◆ 证据长页慢滚 · P0 · 素材呈现——长截图页作为唯一动元素匀速上滚，预标注随页滚动，讲到关键处减速停留，滚速就是讲述节奏。
- **motion-blur-slam-in** ◆ 模糊甩入急停 · P1 · 素材呈现——素材卡带方向运动模糊从屏外高速飞入、0.2s 内急停落位，模糊由重到清收敛；与 media-pop-in 的 scale 弹跳二选一。
- **color-slam-beat-card** ◆ 纯色硬切节拍卡 · P0 · 转场结构——一帧硬切到高饱和纯色底（零过渡零擦除），色块上大字与素材卡错峰入场，停 1.5~5s 再硬切回，用底色跳变当节拍器。
- **host-shrink-to-chip** ◆ 人物缩位让台 · P1 · 人物互动——图形上台时讲者从全屏 0.4s 缩进角落圆形头像章继续口播，单程不回归（回归由镜头层处理），主角让位但人不消失。

## 素材呈现拓展卡（第七批◉，2026-09-05，详情见各卡文件）

来源：2026-09-04 三题调研（视频底床 / 图片运镜 / 多素材同屏，Vox · Johnny Harris · MKBHD · 小Lin说等拆解 + Material / Apple / NN/g 的 scrim 口径）
+ 抖音 @剪辑李一手 / @剪Bingo子 并列句排版教程逐帧拆解；实验室 47 张原型经用户 2026-09-05 两轮筛选留 21，再按"它到底是什么"收成 10 张卡，其余落成规则
（实拍底床处理链 design-language §1.2 / 多素材"关系→版式"表 shot-design §2④′ / 并列句三纪律 layout §7.1 / 字与画同起同收 cinematography §2 G1、§5.8）。
本批每张卡 md 开头有「输入类型」三列表与「常用场景」四条（选卡时与「落位自检」一起抄进 SHOTBOOK）。

- **parallel-items-with-host** ◉ 并列句排版（人物在场） · P0 · 人物互动——口播讲"A、B、C"三件并列的事而人还在画面里：三项按口播逐个弹出（0.6s 一项）、标签压图且大、人物永远在场（形态随版式变），七式一卡切换（头顶横排 / 三横条灰转彩 / 竖列虚化底 / 顶部卡堆 / 竖切三分 / 斜切三分 / 背景轮换大字），一镜一式。
- **still-layout-relay** ◉ 多图排版 + 焦点接力 · P0 · 素材呈现——一主两辅（主图 57% 宽 + 右列两张等大）或三联竖图，主图先落、其余同向错峰 80~150ms 入场，讲到谁谁亮（其余 brightness .6 / scale .985），接力后全部回位一起退场。
- **split-compare-slider** ◉ 对比双分屏（滑动揭示） · P0 · 素材呈现——两张同构图叠放，分割线与 clip-path 同一进度：1.4s 滑到中线 → 停 → nudge 强调 → 滑到 8% 几乎全露 → 回中；before/after、改造前后、新旧版本。
- **filmstrip-conveyor** ◉ 传送带列举 + 减速停靠 · P1 · 素材呈现——≥5 张接成传送带匀速左行 176px/s，经过中线的按距离连续放大 1.08 提亮，讲到关键一张按位置-时间分段积分减速到 0.25× 停 1.4s 再恢复——速度就是讲述节奏。
- **grid-to-hero** ◉ 网格收成主角 · P1 · 素材呈现——2×2 错峰落位先并列，讲到哪张它 0.8s 长成主图、其余收成一列小图不消失（"从这四个里选的"），Remotion 用 transform（FLIP）。
- **stack-fan-out** ◉ 卡堆扇形展开 · P1 · 素材呈现——五张先叠成一叠 → 0.7s 扇开（±24°、弧心在下方）→ 停 → 0.6s 铺平成一行等距——"这一叠"变成"这五个"；图片专用。
- **split-60-40-story** ◉ 60/40 主从分屏 · P1 · 素材呈现——左 60% 一条素材缓推（时长 = 镜头），右 40% 标题 + 三枚 pastel chip 按口播逐枚弹出；"看着它干活，边听边记要点"，左格 B-roll / 图 / 口播本人均可。
- **bed-echo-blur** ◉ 同源模糊底床 · P0 · 素材呈现——前景素材装白边卡，同一条素材放大 1.25 + blur 26 + brightness .45 慢放 0.5× 铺满当底床，颜色天然统一；竖屏素材放横屏、只有一条素材的镜头的标准答案；输入口播 / B-roll / 图均可。
- **rack-focus-pair** ◉ 焦点接力 · P1 · 素材呈现——两张前后叠放一清一糊（blur 8 / brightness .6），讲到哪张焦点 0.7s 转移过去再转回，被糊的不退场；"A 和 B"来回提及、新旧对照、引用 + 反驳。
- **gallery-wall-dolly** ◉ 照片墙推轨 · P1 · 素材呈现——三张 430×290 挂在 rotateY −12° 的 3D 墙上（深灰径向幕底 + 地面反光），相机全景 z .61 → 逐张推近停靠 z 1.15（移 1.0s + 停 0.9s，缩放绕当前图、其余压暗 .5 + 虚化 3px、当前图内部 1→1.03 微推）→ 拉回全景与字同收；"接下来三个例子一个一个看"、作品集 / 三个方案巡完再比较（平级关系）。
- **timeline-photo-strip** ◉ 时间线照片带 · P1 · 素材呈现——四张 240×160 沿一条时间线上下交替，日期 caption 靠线一侧，相机横移逐站停靠（移 0.9s + 停 1.0s，停靠 z 1.05 让邻站出画、当前站 1.03 亮 / 其余 .7）→ 拉开 z .62 看全条、停 1.2s 再与字同收；成长史 / 版本演进 / 年度回顾（先后关系）。

## video-shotcraft 移植卡（第八批◎，详情见各卡文件）

来源：姊妹库 video-shotcraft（产品宣传片镜头库，157 卡 10 类，全部有 Remotion tsx 母本）通读一遍，按四条标准筛——
① 补口播库空白；② 服务讲述不炫产品（主体能换成口播里的证据 / 数据 / 标题 / 人物）；③ 过运动减法纪律（暗场追光 / 霓虹 / 线条沸腾 / 呼吸同心圆一票否决）；④ 有母本、改造成本可控。
18 张进实验室做原型（本地不进库），用户定 9 张入库；第二批按用户点名再做 14 张 + 截图人物排版 1 张，二审留 10 张。每张卡「复用指引」带一行母本溯源（`video-shotcraft <卡名>`），tsx 以母本为起点改写成本库自包含契约（中文排版 / 浅底色板 / 落定即静）。

- **word-slot-cycle** ◎ 词槽轮换 · P0 · 字幕花字——句干左端锚死不动，句尾深色胶囊每 0.7s 向上翻一格换一个短语（前 8 帧换位、后 13 帧静置读词），胶囊宽随词长插值，上下露 13% 幽灵项；换完 N 个词胶囊上飞、结论带全卡唯一一次过冲落进同一位置。"它能帮你 A / B / C / D"式列举、受众列举、章节预告。
- **lead-word-zoom-assemble** ◎ 首词占满补句 · P1 · 字幕花字——首词 2.3 倍字号独占画面正中并推近 6%，随后一条曲线同时缩回终字号与整行左滑归位（缩回 12 帧 / 左滑 24 帧同缓动），后续词各自被推进槽位（淡入仅 2 帧），落定后上移让副行同窗浮出。一句话主张先立主语、产品名字卡、数字先行、反转句。
- **title-demote-to-label** ◎ 标题降格成标签 · P0 · 字幕花字——章节标题居中解糊显影、站稳 ≥18 帧，单次 inOut 补间 20 帧缩到 0.4 倍飞到左上角落成小节标签常驻，降格进行到 12 帧时内容块已在其下错峰生长（交接无空档）。教程 / 方法论的小节交接、"第 N 点"路标、问答式展开。
- **scanline-annotate** ◎ 扫描线逐处点名 · P1 · 强调标注——一条亮扫描线匀速（零缓动）掠过截图，越过每个目标下缘那一刻取景框 1.75→1 收拢对准 + 7% 对焦确认闪，滞后 5 帧右侧标注淡入，状态行实时计数；触发时刻由 bbox 反算不写死。"这张页面有 N 个问题"逐处点评、评测多功能点、合同 / 财报截图划重点。
- **crash-zoom-punch** ◎ 急推特写 · P1 · 强调标注——全景静置 1s 后 6 帧 ease-in 急推到截图局部（zoom 2.3、中心同步收敛到目标文字块），过冲后 5 帧回收 4.5% 钉死，推进段叠短促 blur；它是一次性的重音（切）不是 hold 期运动。"就是这一行"按住账单 / 条款 / 聊天记录里的那句。
- **unit-grid-proportion** ◎ 点阵比例图 · P0 · 数据信息图——10×10 = 100 格从中心分环长出（每环 4 帧 + 3 帧抖动，只做 opacity + 0.8→1，无位移），再按阅读顺序逐格染成强调色、右侧大数字同步 0→N，图例最后浮出。"每 100 个观众有 37 个划走"、"10 个人里有 7 个"、转化 / 留存率——把比例摊成可数个体（unit chart）。
- **source-converge** ◎ 多源汇聚 · P2 · 数据信息图——四条贝塞尔曲线错峰 0.15s 逐路描出，来源胶囊沿各自真实曲线滑向汇聚点并三段式缩小（前 75% 瘦身、后 25% 掉光），强调色数据包沿线滑行两整周期，吞并瞬间汇聚点脉冲 +12%，曲线反向擦除后结果胶囊与说明行 0.6s 滑到画面中心静止。"N 个来源汇到一处"的工作流、多渠道一个入口、多线索同一结论。
- **line-carry-transition** ◎ 线条接力转场 · P1 · 转场结构——A 镜标题下画出强调色下划线，停一拍后继续向右冲出画面，镜头跟线横移 960px（线生长 = 镜头位移，笔头钉在画面 x≈640 永不出画也永不落后），到位后直角硬拐围出 560×330 的 B 镜画框，闭合帧笔头卸载、B 内容在框内淡入。全片唯一的招牌转场位；相机六式交接动量，它交接图形。
- **error-retype** ◎ 打字改口 · P1 · 字幕花字——句干先在，后半句以打字机节奏打出、停一拍光标闪两下、更快退掉、零犹豫重打新词；三档速度差是戏的全部，光标打删常亮停顿才闪。与 strike-and-replace 的区分：那是空间上划掉，这是时间上的改口。否定式文案、纠正误解、金句反转。
- **countdown-arc-scatter** ◎ 数字弧落标题 · P2 · 字幕花字——相邻递减的数字切向挂在弧上，整盘 96° 扫回 outCubic 急停，停在弧顶的那个数平移到标题首字位同步回正，其余原地失焦散去，标题逐词解糊、末词染强调色。与 count-badge-title 的区分：多出"从一串候选里扫停在这个数"的仪表一拍。时长承诺、数字揭晓标题。
- **flying-words** ◎ 关键词隧道 · P2 · 字幕花字——22 个关键词按黄金角铺在扁椭圆截面上沿 z 轴从远处飞向相机擦身而过（前 1/4 猛亮、中段半透让位、末段拖尾），越近越往画外散、近端糊化，整圈数循环首尾无缝。**背景层**：深底专用（白底失效），前景照常静置。名词科普开场底、能力清单垫底。
- **split-text-stagger** ◎ 逐字裂升 · P2 · 字幕花字——每字在裁切盒内从下方 115% 升起带 约 5% 过冲（back.out(1.2) 极值 ≈1.053）、字间错峰 2 帧，一条基线同步从左长到整行宽——字像从线里长出来。是 per-character-rise 的裁切 + 基线变体，要"版式感"时选它。章节题 / 金句 / 片名。
- **word-relay-filmstrip** ◎ 动词接力胶片 · P1 · 素材呈现——左列等高截图卡深浅相间纵向排列，切词那 12 帧才滚恰好一卡高、其余零位移；右侧衬线两行：名词恒定、动词原位接力（旧词灰化淡出先、新词落位后，不叠影），词块中心 = 当前卡中点，末词换强调色。= word-slot-cycle 的带图版 + 步进胶片。"一个主体 × 多种能力"、作品集 / 案例流。
- **doc-park-left-pill-deal** ◎ 文档驻留发牌 · P1 · 素材呈现——文档满幅先读，然后不淡出而是以左缘为锚 translateX −55% + scale .92 驻留只露约 35%（"来源还在"），右侧按旁白节奏慢发牌三张白底描边药丸（先实后稳带过冲），每张落定后其下说明行逐词加深并常驻，文档全程极慢自动滚动。与 split-60-40-story 的区分：戏在"从读文档到提炼结论"的驻留动作。读报告记三条、文档 / 论文要点、评审意见逐条。
- **info-card-assemble** ◎ 信息卡逐字段自建 · P1 · 素材呈现——一张信息卡像被结构化抽取一样自己长出来：图 → 标题 → 三枚标签 pop → 价格行 → 三行要点逐行揭示（两行被马克底块从左 5 帧刷过）→ 色卡点亮；小件 pop 大件 rise，整卡 3.75s 内缓推 6%。字段间隔的疏密就是信息分组；口播实战按词锚分 3~4 组落。推荐书 / 工具 / 人物的信息卡、结构化抽取类话题。
- **chip-grid-single-select** ◎ 五选一反黑 · P1 · 数据信息图——N 个候选 3+2 居中逐个淡入让观众读题，选中帧 1 帧灰闪当按下 → 5 帧 linear 反黑 + 极轻正弦回弹，其余淡到 18% 但位置锁死；1.5s 后余项归零、黑 chip 上移收窄回中线，下方算式行逐词加深。与灰转彩 / 聚焦压暗的区分：单选 + 因果（"选了它然后怎样"）。方案 / 套餐 / 工具选型、调研结果揭晓、排除法。
- **reticle-lock-on** ◎ 准星咬合 · P2 · 强调标注——四个 L 角从四个画外方向（≥1000px）扑向目标，到位时框比目标大 2.2 倍随即收缩过头到 0.94 再回弹到 1，咬合帧目标白闪 + 标签同帧 back 弹出，之后钉死。与 corner-bracket-frame（原位出现）/ scanline-annotate（扫描线触发）的区分：画外飞入 + 超调咬合，冲击最强。"就是这个按钮 / 这个数字"、踩重拍点名。
- **host-card-glass-board** ◎ 人物竖卡玻璃台 · P1 · 人物互动——左 250×444 竖卡放口播人物（圆角 22、半透白描边、演播室底），右 570×408 玻璃板以左缘为轴 rotateY −18→−10 显影、sheen 扫一次；板上期数小字 → 标题逐字解糊 → 英文字距行，板内道具接力（三步 tile 逐个 pop → 连接线长出带箭头 → 结果胶囊），落定即静。价值是"人一直在、板上换道具"，同一块板连讲几个道具不换镜。深底是领域皮（design-language §0），浅底版换白卡 + 发丝线即成立。讲工作流 / 工具链 / 多步教程、竖屏原片放横屏。

<!-- ===== /file: video-talkcraft/references/taxonomy.md ===== -->
