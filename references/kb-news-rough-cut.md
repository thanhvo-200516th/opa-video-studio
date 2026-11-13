# kb-news-rough-cut — toàn văn tài liệu của nguồn `news-rough-cut`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/news-rough-cut/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: news-rough-cut/MODULE.md ===== -->

<!-- master-video-edit: mô-đun nhập 2026-10-29 -->
> **Mô-đun `news-rough-cut`** của `master-video-edit` — kiến thức tham khảo (không chạy công cụ trong file nếu chưa có).
> Thêm gì: Factual news rough-cut keep/delete rules, sentence-boundary speech cuts, no added audio
> Nguồn (USB): `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/AI Video/output/research-integration-20261002/sources/openchatcut/src/agent/skills/news-rough-cut`
> **Khi dùng trên máy Linux này:**
> - Chinese text: translate/summarize
> - drop the 'OpenChatCut tool mapping' section or map it to FilmCraft/ffmpeg
> Công cụ OpenChatCut nhắc trong file (nếu có) chỉ dùng được khi app OpenChatCut mở, qua MCP `openchatcut`; không có thì làm bằng ffmpeg / faster-whisper / FilmCraft.

---
name: news-rough-cut
description: 新闻素材智能粗剪——把新闻素材粗剪为一条内容完整、逻辑清晰、节奏紧凑的新闻短视频。Use when the user asks to 粗剪新闻、新闻剪辑、把新闻素材剪成短视频、智能粗剪、news rough cut、编辑新闻视频, or provides news footage (发布会/采访/现场/监控素材) to be cut into a factual news short. Never add music, voiceover, or sound effects.
---

# News Rough Cut（新闻智能粗剪）

把新闻素材粗剪为一条内容完整、逻辑清晰、节奏紧凑的新闻短视频。忠实于原始素材，不加任何外部声音，保持客观、正式、紧凑、清晰的信息型新闻风格。

This is an OpenChatCut-native workflow. Use the current project's assets, transcript, word-level editing, timeline, and editing tools. Do not depend on external download or transcode pipelines.

## 工作流总览

1. **完整分析素材**（剪辑前必做）：识别素材中的新闻事件、核心话题、关键人物、重要结论及有效画面，再确定剪辑主线和成片时长。使用 `read_project`、`transcribe_track`、`view_timeline_frames` 逐段核对素材内容。
2. **话题分析与时长确定**：判断素材包含多少个话题，区分核心话题与次要内容。
3. **内容组织**：开头直接呈现最重要的新闻结果/核心结论/最新进展/关键现场画面，不铺垫。
4. **剪辑执行**：按保留/删除规则筛选，讲话按语义完整切割。
5. **音频只保留目标新闻素材原声**：开始编辑前只把用户明确指定/选中的新闻素材及其原始现场声列入允许来源；未明确指定时只采用活动时间线上已存在的新闻画面与现场声。媒体池里的 BGM、音效、配音、旁白和其他未选素材即使早已存在，也不得进入允许来源。
6. **终检**：逐段回放核对事实忠实、讲话语义完整、剪切点衔接自然。

## 话题分析与时长确定

- 原则上一条成片只围绕**一条核心新闻主线**展开。
- 若素材中存在多个相互独立的话题，优先选择**新闻价值最高、信息最完整、画面最充分**的话题进行剪辑；**不要将无关话题强行拼接**在同一条视频中。
- 成片时长不做固定限制，根据以下因素自动确定：
  - 核心新闻的信息量；
  - 有效人物讲话的长度；
  - 事件发展阶段和最新进展；
  - 关键现场画面的数量；
  - 保证新闻语义完整所需要的时长。
- 信息较少时应**缩短成片**，避免为了延长时长加入无关内容；信息较多时可以适当延长，**不能为了压缩时长而剪断人物讲话、遗漏关键事实或破坏新闻逻辑**。

## 内容组织逻辑

成片开头直接呈现最重要的新闻结果、核心结论、最新进展或关键现场画面，不使用冗长铺垫。整体按照以下逻辑组织：

1. 发生了什么；
2. 目前有哪些最新进展；
3. 最终结果、后续影响或相关回应。

若新闻事件尚未结束，应以**当前已经确认的最新进展收尾**，不得自行推测结果。

## 内容保留规则

优先保留以下内容：

- 新闻事件的核心事实；
- 时间、地点、人物和事件结果；
- 最新进展及权威回应；
- 重要人物具有实际信息量的讲话；
- 新闻现场、采访、发布会、监控画面及相关有效素材；
- 能够直接说明事件经过、结果或影响的关键画面。

所有保留内容必须服务于核心新闻主线。

## 内容删除规则

删除以下内容：

- 广告和商业推广；
- 节目宣传、频道包装及片头片尾；
- 主持人寒暄和无信息量的串场；
- 重复表述和重复画面；
- 无效停顿、口头语及明显空白；
- 与核心事件无关的冗长背景；
- 不影响新闻理解的次要内容；
- 无法验证、表意模糊或容易造成误解的片段。

## 人物讲话剪辑规则

- 人物讲话必须保持**语义完整**。
- 优先在以下位置切割：
  - 一个完整句子结束后；
  - 人物自然停顿处；
  - 讲话内容发生明显转折处；
  - 镜头自然转场处。
- **不得**从一句话中间强行切断，**不得**只保留部分表述导致原意改变，**不得**将不同时间、不同语境下的讲话错误拼接。
- 若一段讲话较长，可删除其中重复、空泛或无关的句子，但保留下来的内容必须能够**独立表达完整意思**。
- 使用词级编辑工具（文字稿）按词删改，保证落点落在完整句子边界。

## 事实与逻辑要求

剪辑必须忠于原始新闻素材，不得：

- 改变人物讲话原意；
- 夸大或弱化事实；
- 将不同事件错误关联；
- 通过镜头拼接制造虚假因果关系；
- 将推测性内容表达为确定事实；
- 使用与新闻事件不对应的画面误导观众；
- 为追求节奏而删除必要的前因后果。

## 音频要求

- **不得新增**任何背景音乐、配音、旁白、音效、转场音效或其他外部声音。
- 只保留原始素材中与新闻内容直接相关的人声和必要的现场声音。
- 删除广告音乐、节目包装音乐以及与核心新闻无关的声音。
- 处理剪切点时应保证原始人声衔接自然，避免突然截断、重叠、爆音或明显音量跳变（用 `edit_item` 的 fadeInSeconds/fadeOutSeconds 微调剪切点即可，不用加音乐）。

## 整体风格

- 客观、正式、紧凑、清晰的信息型新闻风格。
- 剪辑节奏由新闻内容决定，不刻意追求固定时长或高频切镜。
- 保证每一个保留片段都有明确的信息价值，在内容完整的前提下提高信息密度。
- 不添加花字/滤镜/转场特效；可用基础叠化避免硬切，但以新闻克制为原则。

## OpenChatCut 工具对应

- `read_project` / `read_timeline`：先读工程与时间线状态，按上述范围记录允许来源的 `sourceAssetId` 与 `src`；禁止把媒体池全部资产自动列入。
- `transcribe_track` + 文字稿词级编辑：讲话语义完整切割、删口头语/重复。
- `view_timeline_frames`：核对画面内容与关键现场。
- `edit_item`（trim / ripple delete / fade）与 `split_item`（split）：按保留/删除规则剪辑并处理剪切点衔接。
- `edit_track`：需要多轨整理时创建、调整或收紧人声轨与现场声轨。
- 输出前再次 `read_project`，确认所有最终 `video` / `audio` 项均来自允许来源，且没有 BGM、音效、配音或旁白，再用预览/导出预检核对时长与内容完整性。

## 参考文件

- 执行成片时遵循固定的确定性流程与强制性验收清单，见 [references/deterministic-execution-and-acceptance.md](references/deterministic-execution-and-acceptance.md)：环境检查 → 素材解析 → 生成单条编辑方案 → 一次性执行 → 逐项终检验收（至少 1 个视频轨片段、成片后无新增外部音频、讲话语义完整、剪切点衔接自然）。

<!-- ===== /file: news-rough-cut/MODULE.md ===== -->

<!-- ===== file: news-rough-cut/references/deterministic-execution-and-acceptance.md ===== -->

# News Rough Cut — 确定性执行模板与验收清单

> OpenChatCut-native 参考。借鉴了行业确定性剪辑工作流的通用做法（环境检查 → 素材解析 → 生成单条确定性编辑方案 → 一次性执行 → 强制验收）。
> 符合本技能 SKILL.md 的规则：忠实原素材、不加任何外部声音、讲话按语义完整切割、新闻客观克制的风格。

## 一、执行顺序（固定序列，不要跳步）

1. **环境与素材检查（前置，必做）**
   - 用 `read_project` / `read_timeline` 确认当前工程与时间线存在、存在目标素材片段。
   - 建立允许来源清单：只记录用户明确指定/选中的新闻素材及其原始现场声的 `sourceAssetId` 与 `src`；未明确指定时，只纳入活动时间线上已存在的新闻画面与现场声。媒体池里的 BGM、SFX、配音、旁白和其他未选素材一律不纳入。
   - 用 `transcribe_track` 拿词级文字稿；若某轨不可转写，先解决素材可达性，再继续。
   - 用 `view_timeline_frames` 核对关键画面与素材内容。
   - 前置不通过 → 停下并报告缺什么，不要假装完成。

2. **素材解析与主题判定**
   - 识别：新闻事件 / 核心话题 / 关键人物 / 重要结论 / 有效画面。
   - 判定话题数量：一条成片只围绕一条核心新闻主线；多话题时选新闻价值最高、信息最完整、画面最充分者。
   - 确定成片时长上限（由信息量与有效讲话长度决定，不设死板固定值）。

3. **生成编辑方案（先规划，后动手）**
   - 按「保留 / 删除」规则产出**一个明确的编辑计划**：要保的片段（含句边界）、要删的口头语/重复/广告、要微调的剪切点。
   - 原则：开头直给结论/最新进展/关键画面；讲话只在完整句结束/自然停顿/明显转折/镜头转场处切割。
   - 这一步产出"确定性方案"，不是让用户在每一步都拍板——方案一次成型。

4. **一次性执行**
   - 用 `edit_item` 的批量更新/删除落成 trim、ripple delete 与 fade；需要切开片段时调用 `split_item`。
   - 讲话切割必须落在完整句子边界（用词级文字稿保证）。
   - **不新增**任何 BGM / 旁白 / 音效 / 转场音效；不得从媒体池添加允许来源清单之外的 `video` / `audio`，即使该资产在编辑前已存在。

5. **终检验收（强制性，见下）**
   - 再次 `read_project`，逐项比对所有最终 `video` / `audio` 的 `sourceAssetId` / `src` 与允许来源清单；同一允许来源的 trim、split、move 合法，任何未选来源（包括新增视频中携带的声音）均不合法。
   - 逐段回放核对：事实忠实、讲话语义完整、剪切点衔接自然、无爆音/突兀截断。

## 二、强制验收清单（成片必经，逐项过）

| 验收项 | 判定 | 不通过时 |
|---|---|---|
| 工程存在且可读取 | `read_project` 成功返回当前活动工程 | 停止，报告工程读取失败原因 |
| 至少 1 个视频轨片段 | 时间线上有被保留的画面片段 | 说明无有效画面，未成片 |
| 成片长度与信息量匹配 | 没有为凑时长硬加无关内容；也没有为压缩剪断讲话/关键事实 | 重新平衡时长与内容 |
| 开头直给核心 | 首段是结论/最新进展/关键画面，无冗长铺垫 | 调整开头 |
| 讲话语义完整 | 每段保留讲话都能独立表达完整意思，无"一句话中间切断" | 修正切割点 |
| 无外部声音 | 所有最终 `video` / `audio` 均属于用户选定的新闻素材/原始现场声允许来源；媒体池中原有但未选的 BGM、SFX、配音、旁白也不得使用 | 移除未选来源片段并重新验收 |
| 剪切点衔接 | 无突兀截断、重叠、明显音量跳变；可用 fadeInSeconds/fadeOutSeconds 微调 | 加 1-2 帧淡入淡出 |
| 事实与逻辑 | 不改变原意、不夸大弱化、不错误关联、不把推测当事实、不用错配画面 | 回退到原素材重剪 |

## 三、与 SKILL.md 工具对应

- `read_project` / `read_timeline`、`transcribe_track`、`view_timeline_frames`、`edit_item`（trim / ripple delete / fade）、`split_item`、`edit_track`。
- 验收里的"无新增音频"必须以首次建立的选定素材允许来源与最终 `read_project` 做比对，不能把整个媒体池当作基线，也不能按 audio 轨片段数量判断。

## 四、失败恢复

- 任一验收项不通过 → 回退到「生成编辑方案」步骤重新规划（并非从头，而是定位到违反规则的环节）。
- 若时间线被改坏，允许引用项目的撤销/历史回到执行前状态再重跑。
- 全部验收通过后，才报告"成片完成"并给出成片时长、保留片段数、剪切点数量等可复核结果。

<!-- ===== /file: news-rough-cut/references/deterministic-execution-and-acceptance.md ===== -->
