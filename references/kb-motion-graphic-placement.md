# kb-motion-graphic-placement — toàn văn tài liệu của nguồn `motion-graphic-placement`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/motion-graphic-placement/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: motion-graphic-placement/MODULE.md ===== -->

<!-- master-video-edit: mô-đun nhập 2026-10-29 -->
> **Mô-đun `motion-graphic-placement`** của `master-video-edit` — kiến thức tham khảo (không chạy công cụ trong file nếu chưa có).
> Thêm gì: MG density per format (3-5s portrait, 5-8s landscape), semantic triggers, no-cover zones
> Nguồn (USB): `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/AI Video/output/research-integration-20261002/sources/openchatcut/src/agent/skills/motion-graphic-placement`
> Công cụ OpenChatCut nhắc trong file (nếu có) chỉ dùng được khi app OpenChatCut mở, qua MCP `openchatcut`; không có thì làm bằng ffmpeg / faster-whisper / FilmCraft.

---
name: motion-graphic-placement
description: Add motion graphics at the right moments without blocking the story. Use when the user wants to enhance talking-head, lecture, tutorial, interview, podcast, or creator videos with motion graphics.
---

# Motion Graphic Placement

Use this skill to plan where motion graphics should appear, what type each one should be, and how to keep them readable, rhythmic, and consistent with the video.

## Goals

- Reinforce important speech moments without covering the speaker or subtitles.
- Match MG type to the semantic function of the line.
- Keep density high enough for retention but sparse enough to avoid fatigue.
- Maintain one visual language across the whole edit.

## Workflow

1. Read project state, transcript, active design style, video aspect ratio, and visible speaker layout.
2. Identify the video structure:
   - hook
   - problem or setup
   - body / proof / steps
   - summary / CTA
3. Decide motion-graphic density:
   - long-form landscape: usually one meaningful MG every 5-8 seconds, tighter in the first 15 seconds
   - short-form portrait: usually one meaningful MG every 3-5 seconds, with stronger rhythm
   - reduce density when the speaker's face, gesture, or screen recording already carries the moment
4. Pick MG types from semantic triggers.
5. Review the plan before generation:
   - no repeated form in a row unless intentionally templated
   - no overlays on face, hands, product focal point, or subtitle area
   - no unnecessary full-screen takeover when a card, strip, badge, or annotation is enough
6. Generate or reuse MGs.
7. Place each MG against the relevant transcript moment.
8. Verify screenshots at target frames and fix anything that blocks content, feels mistimed, or carries template residue.

## Semantic Triggers

| Speech pattern                        | Good MG direction                       |
| ------------------------------------- | --------------------------------------- |
| strong opinion, conclusion, key quote | highlight sentence or quote card        |
| numbers, percentages, prices          | number card, counter, chart, price card |
| steps, lists, sequence                | point list, flow steps, timeline        |
| comparison or choice                  | comparison card, split card, VS card    |
| warning or mistake                    | warning card or caution badge           |
| question, suspense, hook              | question card, hook text                |
| self-intro, guest, role               | name tag or lower-third                 |
| source, screenshot, comment, evidence | source card or annotation               |
| CTA                                   | CTA card                                |

## Placement Rules

- Always inspect the frame before placing an overlay.
- Place MGs away from the speaker's face, hands, active product area, and subtitles.
- Landscape: side cards work well when the speaker is clearly on the opposite side; bottom strips must sit above subtitles.
- Portrait: keep the bottom 15-20% clear for captions and interaction UI.
- Full-screen MGs should be reserved for hooks, chapter transitions, dense data, or moments where the original footage adds little value.
- After a full-screen MG, leave enough breathing room before the next overlay.

## Style And Reuse

- Use the active Design Style when the project has one.
- Same-role MGs should reuse a confirmed template or code structure and change only the content.
- New-role MGs can borrow style, but should not inherit irrelevant template text, charts, labels, or layout.
- After generation, inspect the visual output. If old template text or wrong structure appears, fix the asset instead of trusting props.

## Quality Checks

- Every MG has a reason tied to a speech beat.
- Text can be read at playback size.
- Adjacent MGs vary in form, position, or rhythm.
- No face/subtitle/product obstruction.
- Visual style is consistent but not repetitive.
- The final edit feels clearer, not busier.

<!-- ===== /file: motion-graphic-placement/MODULE.md ===== -->
