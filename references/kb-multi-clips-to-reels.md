# kb-multi-clips-to-reels — toàn văn tài liệu của nguồn `multi-clips-to-reels`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/multi-clips-to-reels/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: multi-clips-to-reels/MODULE.md ===== -->

<!-- master-video-edit: mô-đun nhập 2026-10-29 -->
> **Mô-đun `multi-clips-to-reels`** của `master-video-edit` — kiến thức tham khảo (không chạy công cụ trong file nếu chưa có).
> Thêm gì: Selection and packaging rules for building reels from many raw clips
> Nguồn (USB): `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/AI Video/output/research-integration-20261002/sources/openchatcut/src/agent/skills/multi-clips-to-reels`
> **Khi dùng trên máy Linux này:**
> - remove <widget>/widget-forms steps (internal OpenChatCut chat UI, unavailable to Claude Code)
> - share short-form-selection.md with long-video-to-shorts (merge into one module)
> Công cụ OpenChatCut nhắc trong file (nếu có) chỉ dùng được khi app OpenChatCut mở, qua MCP `openchatcut`; không có thì làm bằng ffmpeg / faster-whisper / FilmCraft.

---
name: multi-clips-to-reels
description: Turn multiple product shots, event footage, travel clips, gameplay moments, UGC/product footage, B-roll, or mixed media into social-ready reels, highlights, recaps, or montage-style short videos from existing project media.
---

# Multi Clips to Reels

Use this workflow when multiple raw clips or assets carry the output. The task is to select, sequence, and package the strongest footage into one or more reels, highlights, recaps, or short videos.

This is a OpenChatCut-native workflow. Use the current project, source assets, asset-frame inspection, AV/script context, and OpenChatCut editing tools. Use the current timeline when it already contains relevant cuts or for final verification; do not depend on timeline screenshots as the primary way to understand raw source clips. Do not depend on external download, transcription, ffmpeg, or auto-crop pipelines unless the user explicitly asks for an external source that is not already in the project.

## Workflow

1. Read the project state before editing. Inventory usable source assets: duration, aspect ratio, visual subject, motion/energy, audio quality, duplicates, current timeline state when relevant, obvious hero shots, and fixed-role assets such as logos, QR codes, product photos, brand screenshots, or supplied audio.
2. Confirm that multiple clips carry the output. If one long source clearly defines the story and other assets are only support, switch to the Long Video to Shorts workflow.
3. Identify the user's starting point:
   - `open_media_reel`: uploaded clips/photos and a loose goal.
   - `script_or_storyboard`: supplied script, timestamps, shot list, scene notes, or exact copy.
   - `asset_pack_promo`: product/event/place assets with logos, screenshots, QR codes, audio, or brand constraints.
   - `highlight_selection`: many clips where the main work is selecting the strongest visual moments.
4. Determine only missing constraints that would change the edit: platform, output count, target duration, audience, style, captions/title text, music, and whether the user wants options or direct creation.
5. If more than one missing constraint remains, ask for them in one `<widget>` after loading `widget-forms`. Use text fields for open-ended fields like premise, audience, product/context, or goals; use single/multi choice fields for bounded choices like platform, count, duration, captions, or music.
6. Assign source assets a possible role: hook, context, proof, demonstration, emotional beat, transition, payoff, end card, logo/QR, product evidence, or audio bed. Do not assume every uploaded clip deserves screen time.
7. Match the planning style to the starting point. For `script_or_storyboard`, preserve the user's scene order, copy, timestamps, and claims while mapping each source asset to the requested shot. For `asset_pack_promo`, lock the product/place/event identity and reserve fixed-role assets for brand, proof, or CTA moments. For `open_media_reel` and `highlight_selection`, select and sequence the strongest moments instead of averaging every asset.
8. Compare possible hooks and sequences using [references/short-form-selection.md](references/short-form-selection.md). Use `read_script` for the speech/script overview, `view_asset_frames` for specific source frames and frame-block analysis to select high points or verify what happens on screen. Select for strength, variety, continuity, and fit to the requested platform.
9. Build a compact sequence plan before heavy editing. For each output include selected assets/ranges, opening hook, shot order, role of each shot, rhythm, target duration, platform treatment, and risks.
10. If the user gave enough constraints and asked to create directly, proceed after stating the plan. If the material is varied or the requested count is high, create or preview the first strongest reel before batching the rest.
11. Edit around a viewer-facing arc: hook, context, escalation or proof, payoff. For a pure highlight reel, the payoff can be the strongest final moment or a satisfying recap beat.
12. Package for the target platform: aspect ratio/crop, title text, styled captions, music/beat sync, light motion graphics, transitions, speed ramps, or zooms only when they improve rhythm or clarity.
13. QA before reporting done: strongest shot first, clear sequence purpose, distinct outputs, no unsupported claims, platform fit, requested count/duration, timeline names, and export readiness.

## Plan Format

When presenting a plan, use this compact shape:

- Clip/reel number/title
- Starting point: `open_media_reel`, `script_or_storyboard`, `asset_pack_promo`, or `highlight_selection`
- Selected source assets or ranges
- Source evidence used, such as `read_script`, source frames, or visual-analysis notes
- Opening hook visual or line
- Shot order and role of each shot
- Rhythm or sequence shape
- Target duration/platform treatment
- Edit notes and risks

When creating clips, report timeline names, durations, packaging applied, assumptions, and what to review first.

## Rules

- Start with the strongest visual or clearest promise. Do not slowly introduce every asset.
- Trim clips aggressively enough to maintain rhythm, but keep enough context for the sequence to make sense.
- Do not evenly sample every asset.
- Do not build a contextless montage when the user needs a clear reel, recap, or highlight.
- Do not repeat visually similar shots unless repetition creates rhythm or comparison.
- Do not use captions/title text to invent unsupported claims.
- Do not let packaging effects hide weak source selection.
- For multiple requested reels or short videos, create distinct angles instead of near-duplicate edits from the same footage.

<!-- ===== /file: multi-clips-to-reels/MODULE.md ===== -->

<!-- ===== file: multi-clips-to-reels/references/short-form-selection.md ===== -->

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

<!-- ===== /file: multi-clips-to-reels/references/short-form-selection.md ===== -->
