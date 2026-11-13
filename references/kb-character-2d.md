# kb-character-2d — toàn văn tài liệu của nguồn `character-2d`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/character-2d/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: character-2d/MODULE.md ===== -->

<!-- master-video-edit: mô-đun nhập 2026-10-29 -->
> **Mô-đun `character-2d`** — gộp 4 skill OpenMontage về hoạt hình nhân vật 2D (rig, pose, diễn bằng GSAP theo frame, QA). Kiến thức tham khảo; bỏ qua tên file/schema riêng của OpenMontage.


---

## svg-character-animation

> Nguồn: `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Remotion/research/vendors/OpenMontage/.agents/skills/svg-character-animation`

---
name: svg-character-animation
description: Animate SVG character rigs with GSAP, CSS transforms, Remotion frame control, and HyperFrames-compatible browser previews.
license: MIT
---

# SVG Character Animation

Use this skill when animating character rigs made from SVG parts.

## Runtime Rules

- Animate transforms (`x`, `y`, `scale`, `rotation`) rather than layout.
- Use timelines for multi-part acting beats.
- For SVG elements, use stable pivots (`svgOrigin` or correctly scoped
  transform origins).
- In Remotion, do not let GSAP advance with `requestAnimationFrame`; drive a
  paused timeline from the current frame.

## Browser Pattern

```js
gsap.set("#arm_right", { svgOrigin: "390 310" });
const tl = gsap.timeline({ defaults: { ease: "power2.inOut" } });
tl.to("#head", { rotation: -8, duration: 0.2 })
  .to("#arm_right", { rotation: 35, duration: 0.4 }, "<");
```

## Remotion Pattern

```tsx
const frame = useCurrentFrame();
const progress = frame / durationInFrames;
timeline.progress(progress);
```

## HyperFrames Pattern

Use HTML/SVG/GSAP components with deterministic timelines and validate via the
HyperFrames CLI before final render.

## Quality Checklist

- Parts stay connected at pivots during motion.
- Blinks, gaze, and mouth shapes are separate enough to read.
- Pose holds are long enough to communicate emotion.
- Frame sampling shows meaningful deltas, not frozen animation.

## Sources

- GSAP core transform properties and SVG handling:
  https://gsap.com/docs/v3/GSAP/CorePlugins/CSS/
- GSAP timelines and sequencing:
  https://gsap.com/docs/v3/GSAP/Timeline/
- Remotion `useCurrentFrame`:
  https://www.remotion.dev/docs/use-current-frame


---

## character-rigging

> Nguồn: `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Remotion/research/vendors/OpenMontage/.agents/skills/character-rigging`

---
name: character-rigging
description: Build data-driven 2D character rigs for local animation: parts, pivots, layers, constraints, views, and reusable rig packages.
license: MIT
---

# Character Rigging

Use this skill when building OpenMontage `rig_plan` artifacts or renderer input
for local 2D character animation.

## Proven Patterns

- Keep runtime code generic; make each character a data package.
- Split characters into independently transformable parts.
- Define pivots in the same coordinate space as the artwork.
- Store constraints on moving parts to prevent impossible rotations.
- Keep layer order explicit; do not rely on SVG source order after generation.
- Start with one view and add views only when the shot list requires them.

## Rig Package

```json
{
  "character_id": "mouse",
  "rig_type": "svg_rig",
  "parts": [
    { "id": "body", "kind": "torso", "layer": 10 },
    { "id": "head", "kind": "head", "layer": 30, "parent": "body" },
    { "id": "arm_right", "kind": "limb", "layer": 40, "parent": "body" }
  ],
  "joints": {
    "head": { "pivot": [320, 180], "rotation": [-20, 20] },
    "arm_right": { "pivot": [390, 310], "rotation": [-70, 95] }
  }
}
```

## Quality Checklist

- Every moving part has a pivot.
- Every child part has a parent where hierarchy matters.
- Mouth shapes are separate assets or separate path groups.
- Eyes and pupils are separate when gaze needs to change.
- Props are separate if the character touches or carries them.

## Sources

- SVG transform-origin behavior is browser-defined and can be sensitive to
  coordinate space; prefer explicit SVG-coordinate pivots when using GSAP
  `svgOrigin`: https://gsap.com/docs/v3/GSAP/CorePlugins/CSS/
- Remotion animations must be frame-driven and deterministic via current frame:
  https://www.remotion.dev/docs/use-current-frame


---

## character-animation-qa

> Nguồn: `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Remotion/research/vendors/OpenMontage/.agents/skills/character-animation-qa`

---
name: character-animation-qa
description: Review local character animation with schema checks, Playwright browser previews, frame sampling, and FFmpeg/ffprobe final output checks.
license: MIT
---

# Character Animation QA

Use this skill before presenting a character-animation preview or final render.

## Review Layers

1. Schema validation: character design, rig plan, pose library, action timeline.
2. Static asset checks: referenced parts and backgrounds exist.
3. Browser preview: load the preview, capture screenshots, collect console errors.
4. Motion check: compare sampled frames for non-trivial differences.
5. Final MP4 check: ffprobe metadata, duration, resolution, audio, frame samples.
6. Agent visual review: inspect sampled frames for detached limbs, bad layers,
   off-frame characters, unreadable expressions, broken text.

## Playwright Pattern

```ts
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
await page.goto(previewUrl, { waitUntil: "networkidle" });
await page.screenshot({ path: "preview.png" });
```

## Pass/Revise/Fail

- `pass`: technical checks pass, acting is readable.
- `revise`: fixable rig/timeline issue.
- `fail`: missing assets, blank render, runtime failure, or wrong runtime.

## Sources

- Playwright screenshots:
  https://playwright.dev/docs/screenshots
- Playwright page navigation:
  https://playwright.dev/docs/api/class-page#page-goto
- FFmpeg/ffprobe should be used for final media probing:
  https://ffmpeg.org/ffprobe.html


---

## pose-library-design

> Nguồn: `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Remotion/research/vendors/OpenMontage/.agents/skills/pose-library-design`

---
name: pose-library-design
description: Design reusable 2D character pose libraries, action cycles, and expression states for data-driven animation.
license: MIT
---

# Pose Library Design

Use this skill when producing `pose_library` artifacts.

## Pose Categories

- Neutral: idle, breathe, listening.
- Attention: look_up, look_down, look_left, look_right.
- Emotion: happy, sad, surprised, worried, determined.
- Action: reach, point, hold, jump, flap, walk_contact, walk_passing.
- Mouth: closed, small_o, wide_open, smile, frown, phoneme-ish shapes.

## Acting Pattern

Use timed pose sequences:

```text
anticipation -> action -> hold -> settle
```

Do not continuously animate every part. Holds make the acting readable.

## Pose Data Pattern

```json
{
  "pose": "surprised",
  "parts": {
    "head": { "rotation": -6, "y": -4 },
    "pupil_left": { "x": 4, "y": -6 },
    "mouth": "small_o"
  },
  "hold_frames": 18,
  "transition": "back.out"
}
```

## Quality Checklist

- Required emotions have poses.
- Required actions have poses or cycles.
- Reused cycles have contact and passing poses.
- Poses name only changed parts; defaults come from the rig.

## Sources

- GSAP timeline sequencing for readable multi-step poses:
  https://gsap.com/docs/v3/GSAP/Timeline/
- Remotion interpolation for frame-based transitions:
  https://www.remotion.dev/docs/interpolate
- Remotion spring for natural motion:
  https://www.remotion.dev/docs/spring

<!-- ===== /file: character-2d/MODULE.md ===== -->
