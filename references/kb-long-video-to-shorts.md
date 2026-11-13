# kb-long-video-to-shorts — toàn văn tài liệu của nguồn `long-video-to-shorts`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/long-video-to-shorts/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: long-video-to-shorts/MODULE.md ===== -->

<!-- master-video-edit: mô-đun nhập 2026-10-29 -->
> **Mô-đun `long-video-to-shorts`** của `master-video-edit` — kiến thức tham khảo (không chạy công cụ trong file nếu chưa có).
> Thêm gì: Standalone-moment selection and scoring for cutting long videos into shorts
> Nguồn (USB): `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/AI Video/output/research-integration-20261002/sources/openchatcut/src/agent/skills/long-video-to-shorts`
> **Khi dùng trên máy Linux này:**
> - remove <widget>/widget-forms steps (internal OpenChatCut chat UI, unavailable to Claude Code)
> - references/short-form-selection.md duplicated in multi-clips-to-reels; keep one copy
> Công cụ OpenChatCut nhắc trong file (nếu có) chỉ dùng được khi app OpenChatCut mở, qua MCP `openchatcut`; không có thì làm bằng ffmpeg / faster-whisper / FilmCraft.

---
name: long-video-to-shorts
description: Cut one long podcast, interview, course, livestream, or other source video into social-ready shorts, reels, highlights, or clip timelines from existing project media. Use when the user asks to cut a long video into Shorts, Reels, TikToks, Xiaohongshu posts, best moments, highlights, or multiple clips.
---

# Long Video to Shorts

Use this workflow when one long source video carries the output. Supporting clips may exist, but the short-form story comes from selecting self-contained moments inside the long source.

This is a OpenChatCut-native workflow. Use the current project, assets, transcript, timeline, and OpenChatCut editing tools. Do not depend on external download, transcription, ffmpeg, or auto-crop pipelines unless the user explicitly asks for an external source that is not already in the project.

## Workflow

1. Read the project state before editing. Identify the primary long video, duration, language, speakers, current timeline, transcript readiness, visual descriptions, and aspect ratio.
2. Confirm that one long source carries the output. If the project is mainly multiple raw clips with no dominant long source, switch to the Multi Clips to Reels workflow.
3. Determine only missing constraints that would change the edit: platform, clip count, target duration, audience, style, captions/title text, music, and whether the user wants options or direct creation.
4. If more than one missing constraint remains, ask for them in one `<widget>` after loading `widget-forms`. Use text fields for open-ended fields like topic, spoken language, audience, or goals; use single/multi choice fields for bounded choices like platform, count, duration, captions, or music.
5. Use transcript ranges when available. If transcription is unavailable or unreliable, inspect visual/audio content and ask only for missing context that changes selection.
6. Scan for moments that can stand alone: clear setup, hook, claim, proof, emotional turn, lesson, conflict, demonstration, or payoff. Read [references/short-form-selection.md](references/short-form-selection.md) when scoring or comparing candidates.
7. Build a compact candidate plan before heavy editing. For each output include source range, opening hook, why it stands alone, payoff, target duration, platform treatment, and risks.
8. If the user gave enough constraints and asked to create directly, proceed after stating the plan. If the source is very long, the request is vague, or the requested count is high, create or preview the first strongest clip before batching the rest.
9. Cut on clean word, phrase, action, or beat boundaries. Tighten filler, false starts, repeated attempts, and dead time only when meaning and tone stay intact.
10. Package for the target platform: aspect ratio/crop, title text, styled captions, music, light motion graphics, zooms, speed changes, or transitions only when they support the selected moment.
11. QA before reporting done: hook in first seconds, clear payoff, standalone clarity, no misleading title, clean boundaries, platform fit, requested count/duration, timeline names, and export readiness.

## Plan Format

When presenting a plan, use this compact shape:

- Clip number/title
- Source range
- Opening hook
- Why it stands alone
- Payoff or viewer value
- Target duration/platform treatment
- Edit notes and risks

When creating clips, report timeline names, durations, packaging applied, assumptions, and what to review first.

## Rules

- Preserve claims, speaker intent, context, and causality. Do not make the speaker appear to say something they did not mean.
- Prefer the smallest range that preserves setup, meaning, and payoff.
- Do not summarize the whole long source evenly.
- Do not choose a quotable line if it needs missing context to make sense.
- Do not use misleading title text to compensate for a weak moment.
- Do not pad with weak clips just to hit the requested count.
- Do not treat a full talking-head polish request as Long Video to Shorts unless the user asks for shorts, clips, highlights, or cutdowns.
- Do not batch many shorts blindly. If the style is not established, create or preview the first strong clip before repeating it.

<!-- ===== /file: long-video-to-shorts/MODULE.md ===== -->

<!-- ===== file: long-video-to-shorts/references/short-form-selection.md ===== -->

# Short-Form Candidate Selection

Use this guide to compare transcript moments from one long source and visual sequences assembled from multiple clips. Score source strength before adding captions, music, transitions, or other packaging.

## 1. Record candidate evidence

Create one row per candidate and use stable IDs so another pass can reproduce the ranking.

| Field | Long-source moment | Multi-clip sequence |
| --- | --- | --- |
| Candidate ID | Source asset + start/end range | Ordered asset IDs + ranges |
| Direct evidence | Exact transcript line, speaker turn, action, or audio beat | Observed subject, action, motion, reaction, composition, or audio beat |
| Proposed arc | Hook → setup/proof → payoff within the range | Hook shot → context/proof shots → payoff shot |
| Boundary evidence | Complete phrase, breath, pause, reaction, or action | Entry/exit motion, beat, action completion, or natural transition |
| Constraints | Requested audience, duration, format, tone, and purpose | Requested audience, duration, format, tone, and purpose |
| Risks | Missing context, weak audio, misleading implication, safety/privacy, crop, or rights concern | Continuity, unsupported claim, duplicate footage, safety/privacy, crop, or rights concern |

Write observations as facts. Label interpretations as assumptions and verify them before editing. Never infer a claim, identity, relationship, result, or chronology that the source does not support.

## 2. Check the candidate arc

A viable candidate should answer these questions from its own selected material:

- **Standalone clarity:** Can a new viewer understand the subject, action, or claim without the surrounding source?
- **Hook:** Does the opening create immediate curiosity, tension, surprise, relevance, or visual interest?
- **Payoff:** Does the selection deliver an answer, proof, reveal, emotional turn, lesson, result, or satisfying final beat?
- **Context integrity:** Does trimming preserve the speaker's meaning, event order, cause and effect, and user-supplied claims?
- **Visual strength:** Is there a readable subject, meaningful action, expressive reaction, useful detail, or purposeful composition?
- **Platform fit:** Does the material suit the user's requested duration, format, audience, tone, and viewing conditions without relying on assumed platform conventions?
- **Redundancy:** Is it meaningfully different from stronger candidates in topic, claim, action, framing, energy, or payoff?
- **Clean boundaries:** Can it start and end without clipped speech, incomplete action, abrupt context loss, or accidental dead air?

For speech-led moments, visuals may support rather than lead. For visual sequences, meaning may come from shot order and audio rather than dialogue. Do not penalize either form merely for lacking the other's evidence type.

## 3. Score reproducibly

Score each factor from `0` to `4` using the same evidence pass:

- `0` — absent, unusable, or contradicted by the source
- `1` — weak; major repair or outside explanation required
- `2` — workable; clear limitations remain
- `3` — strong; minor editing is enough
- `4` — exceptional; immediately legible and well supported

| Factor | Weight | Scoring question |
| --- | ---: | --- |
| Standalone clarity | 18 | Does the selected material explain itself? |
| Hook | 16 | Is the first usable beat compelling? |
| Payoff | 14 | Is there a concrete, satisfying destination? |
| Context integrity | 14 | Will the cut preserve meaning and chronology? |
| Visual strength | 12 | Are the selected images/actions readable and purposeful? |
| Platform fit | 10 | Does it fit the user's stated delivery constraints? |
| Clean boundaries | 8 | Are there natural, editable start and end points? |
| Distinctiveness | 8 | Does it add value beyond higher-ranked candidates? |

Calculate:

`base score = sum(factor rating × factor weight) ÷ 4`

The base score is out of `100`. Keep the individual ratings and one evidence note per factor; a total without notes is not reproducible.

Apply only evidence-based deductions after the base score:

| Deduction | Range | Use when |
| --- | ---: | --- |
| Correctable risk | `-1` to `-10` | A crop, audio, pacing, continuity, or boundary issue is real but repairable |
| Redundancy | `-1` to `-12` | A higher-ranked candidate already delivers substantially the same value |

`final score = base score - deductions`

Do not deduct twice for the same weakness. Rank by final score, then break ties in this order: context integrity, standalone clarity, hook, payoff, visual strength. Preserve the original candidate IDs and scores when re-ranking after user feedback.

## 4. Reject before ranking

Reject a candidate rather than trying to rescue it with packaging when any of these are true:

- It changes or obscures the source meaning, chronology, speaker intent, or user-provided claim.
- It requires invented context, unsupported title text, or an unverified factual claim to make sense.
- It lacks a usable opening, understandable middle, or payoff after reasonable trimming.
- Speech or action is irreparably clipped, inaudible, visually unreadable, or missing the evidence needed for the proposed arc.
- Safety, privacy, consent, rights, or sensitive-content concerns cannot be resolved within the user's instructions and available project evidence.
- It is materially weaker than and redundant with a stronger candidate.
- It cannot meet the user's stated duration or format without breaking context integrity.

A rejected candidate receives a reason, not a score. Do not lower the threshold merely to reach a requested count.

## 5. Select and sequence

1. Inventory broadly enough to find competing hooks and payoffs; do not score only the first plausible moment.
2. Remove rejected candidates.
3. Score the remaining candidates in one pass with the same constraints and evidence standard.
4. Rank by final score and apply the tie-break order.
5. Review the tentative set for variety across subject, claim, action, framing, energy, and payoff; apply redundancy deductions and re-rank.
6. Record the selected source ranges, opening beat, arc, expected duration, treatment constraints, and unresolved risks.

## 6. Prove the first clip before batching

When style is not established, material is varied, the source is very long, or the requested count is high, create or preview the highest-ranked candidate first. Verify that its hook, clarity, payoff, boundaries, crop, pacing, and packaging work in the actual timeline. Use that confirmed treatment as the batch reference, then process the remaining ranked candidates. If the first clip exposes a scoring assumption or treatment problem, update the rubric notes and re-rank before batching; do not repeat the flaw across outputs.

<!-- ===== /file: long-video-to-shorts/references/short-form-selection.md ===== -->
