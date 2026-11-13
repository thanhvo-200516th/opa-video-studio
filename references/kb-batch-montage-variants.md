# kb-batch-montage-variants — toàn văn tài liệu của nguồn `batch-montage-variants`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/batch-montage-variants/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: batch-montage-variants/MODULE.md ===== -->

<!-- master-video-edit: mô-đun nhập 2026-10-29 -->
> **Mô-đun `batch-montage-variants`** của `master-video-edit` — kiến thức tham khảo (không chạy công cụ trong file nếu chưa có).
> Thêm gì: Variation matrix + dedup budget for N structurally distinct cuts from one pool
> Nguồn (USB): `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/AI Video/output/research-integration-20261002/sources/openchatcut/src/agent/skills/batch-montage-variants`
> **Khi dùng trên máy Linux này:**
> - remove <widget>/widget-forms steps (internal OpenChatCut chat UI, unavailable to Claude Code)
> - repoint sibling refs (multi-clips-to-reels, long-video-to-shorts) to module paths
> Công cụ OpenChatCut nhắc trong file (nếu có) chỉ dùng được khi app OpenChatCut mở, qua MCP `openchatcut`; không có thì làm bằng ffmpeg / faster-whisper / FilmCraft.

---
name: batch-montage-variants
description: |
  Turn one pool of existing project media into a batch of distinct, publishable montage cuts instead of a single hero edit.
  Use for batch montage, one-source-many-outputs, 一源多出, 批量混剪, 批量出片, 矩阵号, 多账号分发, variant batches, deduped cuts, 去重变体, 防搬运, or when the user asks for N different versions of the same footage.
---

# Batch Montage Variants

Use this workflow when the user wants **many** finished cuts from the same media pool — matrix accounts, A/B hook testing, platform variants, or daily batch output. Each output must satisfy the agreed mode: structural differentiation, a controlled hook test, or a platform adaptation.

This is an OpenChatCut-native workflow. Use the current project, source assets, asset-frame inspection, AV/script context, and built-in editing tools. Editing imported media requires no external service. Use external sources or processing pipelines only when explicitly requested by the user.

## When to switch workflows

- One hero edit from many clips → **Multi Clips to Reels**. Do not use this skill to make a single cut.
- One long source defining a story → **Long Video to Shorts**.
- N distinct outputs from a shared pool → this skill.

Tell the user when you switch, and say why.

## Workflow

1. Read the project state before editing. Inventory the source pool: clip count, usable duration, aspect ratio, visual subjects, motion/energy, audio quality, and duplicates.
2. Confirm the user wants more than one output and the pool supports the selected mode. Do not pad a distinct-cut batch with near-duplicates; controlled tests and platform adaptations may intentionally reuse an edit.
3. Fix the batch contract before cutting — mode (distinct cuts, controlled hook test, or platform adaptations), count, target duration, platform, audience, language, and music bed. If more than one is missing, ask in one `<widget>` after loading `widget-forms`.
4. Score every source asset for reuse headroom before planning. See [references/variation-matrix.md](references/variation-matrix.md). Reserve distinct hooks where the mode requires them; shared end cards and intentional shared bodies are allowed.
5. Build the **variation matrix** before editing. For distinct cuts, plan different hooks and structural changes. For controlled hook tests, change only the hook and keep the body fixed. For platform adaptations, retain the approved content and adapt presentation. See [references/variation-matrix.md](references/variation-matrix.md).
6. Plan the dedup budget with [references/dedup-rules.md](references/dedup-rules.md). Decide up front which dimensions carry the differentiation, and record the minimum separation each pair of cuts must clear.
7. Get the matrix approved before cutting the whole batch. Show the plan as a table: cut number, hook, order signature, rhythm, duration, packaging, and the dimension that makes it different from every other cut in the batch.
8. Cut the first variant end to end and verify it renders and exports before batching the rest. Do not generate eight timelines that share one unverified mistake.
9. Cut remaining variants from the approved matrix. Reuse picks and trims according to the approved mode; distinct cuts and hook tests need different openings, while platform adaptations may share them.
10. Name timelines so the batch is auditable: `<topic>-v<NN>-<hook-label>`, consistent across the batch.
11. QA each cut individually **and** the batch as a set. See [references/dedup-rules.md](references/dedup-rules.md) for the pairwise checks.
12. Report per-cut timeline names, durations, the differentiation dimension for each, and which pair is the most similar — that is the pair the user should review first.

## Plan Format

Present the batch as one table, not prose:

| # | Hook asset | Order signature | Rhythm | Duration | Packaging | Differs by |
|---|---|---|---|---|---|---|
| v01 | clip_07 (product in hand) | A-C-E-B | fast-cut, 1.2s avg | 28s | bold captions + beat cuts | hook + order |
| v02 | clip_12 (before/after) | C-A-B-E | slow open, ramp | 34s | minimal captions + zoom | hook + rhythm |

- Total outputs, platform, shared vs distinct music bed
- Source pool size and reuse headroom
- Dedup budget and minimum separation
- Risks: thin pool, single-use assets, near-duplicate pairs

## Rules

- Distinct cuts and hook tests need different opening three seconds. Platform adaptations may share an opening and must be labeled as adaptations, not distinct edits.
- For distinct cuts, differentiate on **structure** before decoration. Styling changes alone do not establish structural differentiation; these checks do not guarantee a platform's duplicate-detection outcome.
- Do not pad a thin pool into N cuts. Report the honest maximum and ask.
- Distinct cuts and hook tests need different hooks; platform adaptations may reuse the same approved hook.
- Keep one variable dominant per cut. When everything differs slightly, nothing reads as different.
- Batch output is not permission to lower the bar: each cut must stand alone as publishable.
- Do not use captions or titles to invent claims the footage does not support, in any variant.
- Report the most-similar pair explicitly. Hiding it defeats the point of the batch.

<!-- ===== /file: batch-montage-variants/MODULE.md ===== -->

<!-- ===== file: batch-montage-variants/references/dedup-rules.md ===== -->

# Dedup Rules and Batch QA

These editorial checks compare the batch as a set. They do not guarantee a platform's duplicate-detection outcome. Select the batch mode before applying them.

## 1. Why structural dedup, not decorative dedup

For distinct-cut batches, mirror, speed change, color grade, caption restyle and music swap alone do not establish structural differentiation. Compare:

- Different source footage in the opening and in the majority of shots
- Different event order — the sequence of what happens, not how it is dressed
- Different edit rhythm, which changes the perceived pacing signature
- Different duration at a meaningful scale

Treat a distinct-cut plan built only from decorative changes as insufficient. Controlled hook tests and platform adaptations intentionally preserve content and follow their own contract.

## 2. Pairwise checks

For `controlled-hook-test`, verify different openings and an otherwise unchanged body, order, duration, rhythm, music and packaging. Record the intentional shared content; high overlap is expected and is not a failure.

For `platform-adaptation`, verify the approved content is preserved and each target's aspect ratio, safe areas, captions and duration requirements are met. Shared openings and bodies are allowed.

For distinct cuts, run these on every pair in the batch. N cuts means N*(N-1)/2 pairs; for large
batches, at minimum check every cut against the cut it most resembles.

Use the following as editorial planning targets, subject to the approved matrix:

1. **Opening** — no shared source frames in the first 3 seconds.
2. **Overlap budget** — target shared source seconds divided by the shorter cut's duration under **40%**. Higher overlap needs review against the agreed contract; it is not a platform classification.
3. **Order signature** — the first 5 shots differ in at least 2 adjacent pairs.
4. **Rhythm** — average shot length differs by 1.5x, or the shape inverts.
5. **Duration** — differs by at least 15%, unless the platform fixes length.

Record the distinct-cut result as an editorial similarity verdict: `distinct`, `borderline`, or `near-duplicate`. For the other modes, report `controlled-hook-test` or `platform-adaptation` and whether its contract passed; do not apply the distinct-cut thresholds.

## 3. What to do with each verdict

| Verdict | Action |
|---|---|
| `distinct` | Ship. |
| `borderline` | Ship only if the user accepts the risk, and flag the specific pair in the report. |
| `near-duplicate` | Do not ship both. Re-cut one on a different dimension, or drop it and tell the user the pool would not support the requested count. |

Never silently ship a `near-duplicate` pair. The whole point of the batch is
that the outputs are genuinely different; a hidden duplicate is worse than a
smaller batch because it fails later, after publishing.

## 4. Per-cut QA (still required)

The batch check does not replace individual review. For each cut:

- Opens on the strongest available visual, not a logo or a slow establish
- Sequence has a purpose: hook, context, escalation/proof, payoff
- Captions and titles state only what the footage supports
- Platform treatment correct: aspect ratio, safe areas, duration
- Exports cleanly

## 5. Report format

Report the batch as a set, not as N independent successes:

```
Batch: <topic> — <N> cuts, <platform>
Music: shared bed <name> | distinct beds per cut

v01 <name>  28s  differs by: hook + order
v02 <name>  34s  differs by: hook + rhythm
...

Most similar pair: v03 / v05 — borderline (overlap 38%, order differs in 2 pairs)
Review first: v03 and v05, then v01 (hook test baseline)
```

Always name the most similar pair. If the user only has time to check two
files, they should check the two that might be duplicates — that is the pair
most likely to cause a problem, and hiding it defeats the purpose of the
check.

<!-- ===== /file: batch-montage-variants/references/dedup-rules.md ===== -->

<!-- ===== file: batch-montage-variants/references/variation-matrix.md ===== -->

# Variation Matrix

The variation matrix is the batch plan. It exists so differentiation is designed
before cutting, not discovered afterward when two timelines already look alike.

## 1. Score reuse headroom first

For distinct-cut planning, classify every source asset with the reuse rules below. Controlled hook tests may repeat every body shot in its original position. Platform adaptations may reuse the entire approved edit, including its hook.

| Class | Meaning | Planning rule |
|---|---|---|
| `single-use` | Only works in one position: logo end card, QR code, one spoken punchline, a reveal that only makes sense once | May appear in many cuts, but never as the hook of more than one |
| `positional` | Works in one role: establishing wide, product close-up, reaction shot | May repeat across cuts, but not in the same slot |
| `flexible` | Works anywhere: B-roll texture, ambient motion, cutaway | Free to reuse; carries no differentiation |

For distinct cuts and hook tests, check how many usable different openings the pool supports. This does not limit the number of platform adaptations of one approved edit.

## 2. The five differentiation dimensions

Ranked by how much they actually change viewer and platform perception:

1. **Hook asset** (strongest) — the first 3 seconds. Different source clip, different visual subject.
2. **Shot order** — the sequence signature. `A-C-E-B` vs `C-A-B-E`.
3. **Rhythm** — average shot length and its shape over time (slow open → ramp, constant fast, front-loaded then settle).
4. **Packaging** — captions style, motion graphics, transitions, crops, speed ramps.
5. **Music bed** (weakest alone) — a different track changes mood but barely changes perceived content.

Rules of thumb for distinct cuts only (not controlled hook tests or platform adaptations):

- Dimensions 4 and 5 alone do **not** constitute a distinct variant. A recut with new music and new caption styling is the same video.
- Dimensions 1 and 2 alone are sufficient, even with identical packaging.
- Aim for 2+ changed dimensions per pair, with at least one from 1–3.

## 3. Minimum separation budget

For distinct-cut batches, use these as planning targets agreed with the user, not platform detection rules. Controlled hook tests and platform adaptations use the mode-specific checks below instead.

| Dimension | Minimum separation between any two cuts |
|---|---|
| Opening 3s | Different source asset, no shared frames |
| Shot order | At least 2 adjacent-pair differences in the first 5 shots |
| Rhythm | At least 1.5x difference in average shot length, **or** an inverted shape (one ramps up, one settles down) |
| Duration | At least 15% difference, unless platform rules force a fixed length |
| Music | Distinct track, or explicitly shared by user request |

When a distinct-cut pair misses the agreed targets, revise the plan or report the shortfall before cutting.

## 4. Choosing the dominant variable

Pick one dimension to carry the batch and let the others support it:

- **Hook testing**: only the opening changes; body, order after the hook, duration, rhythm, music and packaging stay fixed. Do not apply distinct-cut overlap, order, rhythm or duration thresholds. Report `controlled-hook-test` and identify the intentional shared body.
- **Matrix accounts / 多账号分发**: hook, order, and rhythm all change. Packaging may stay consistent as a brand signature.
- **Platform variants**: content structure stays fixed; duration, aspect ratio, caption placement, and safe-area treatment adapt to each platform. Shared openings and bodies are allowed. Report `platform-adaptation`; do not apply distinct-cut separation thresholds.

A batch with no dominant variable reads as noise. State which mode you are in
before cutting.

## 5. Capacity check

Check whether the actual source ranges can support N cuts under the selected mode and agreed separation targets. Distinct cuts and hook tests need enough usable openings; hook tests may intentionally reuse the full body. Platform adaptations can reuse the same edit. Do not infer a numeric capacity from total footage duration alone.

If the pool cannot support the requested plan, report the specific shortage and offer fewer cuts or more source media. Switching to controlled tests or platform adaptations changes the batch contract and must be explicit.

## 6. Naming

`<topic>-v<NN>-<hook-label>`, zero-padded, consistent across the batch.
Examples: `summer-drop-v01-unbox`, `summer-drop-v02-beforeafter`.

Auditable naming is what makes the batch reviewable later — the reviewer should
be able to tell from the timeline name which dimension each cut was testing.

<!-- ===== /file: batch-montage-variants/references/variation-matrix.md ===== -->
