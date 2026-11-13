# kb-kinetic-typography — toàn văn tài liệu của nguồn `kinetic-typography`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/kinetic-typography/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: kinetic-typography/SKILL.md ===== -->

---
name: kinetic-typography
description: This skill should be used when the user asks to "animate a headline", "make a kinetic typography video", "do a split-text reveal", "stagger text by character/word/line", "make a lyric or caption video", "animate a variable font weight", "put text on a path", or "create an animated title card". Covers reveal techniques in CSS, GSAP SplitText, Framer Motion, and Remotion.
version: 0.1.0
---

# Typography in Motion

Animate text expressively: splitting copy into lines/words/characters, staggering reveals, masking, blurring, morphing weight, and running text along a path. Produces runnable code for the web (CSS, GSAP, Framer Motion) and video (Remotion), plus an After Effects expression approach.

## When to use

- Headline / tagline entrances and animated title cards.
- Lyric videos, caption/subtitle reveals, kinetic-typography pieces.
- Variable-font animation (weight, width, slant, optical size).
- Text-on-path, text stroke draw-on, and per-character morph effects.

## Core workflow

### 1. Get static typography right first

Motion cannot rescue bad type. Before animating, lock line-height (1.1-1.2 for display headlines, 1.4-1.6 for body), tracking (tighten display by -1% to -3%, e.g. `letter-spacing: -0.02em`), alignment, and weight. Then split and animate.

### 2. Choose split granularity

- **By line** — calmest, most premium; best for multi-line paragraphs and elegant headlines.
- **By word** — energetic, good for taglines and lyric hits.
- **By character** — most kinetic/playful; risk of feeling busy on long copy. Reserve for short strings.

Tools: `SplitType` or GSAP `SplitText` on the web; `.split('')` / `.split(' ')` plus `interpolate` in Remotion; `motion` staggered children in Framer Motion.

Critical accessibility note: splitting into per-character spans destroys the text for screen readers and breaks copy-paste. Always set `aria-label` on the container with the full string and `aria-hidden="true"` on the split fragments.

### 3. Apply a reveal technique

The four workhorse reveals:

- **Mask / clip reveal (most robust)** — wrap each line in `overflow: hidden`; animate the child from `translateY(100%)` to `0`. The text wipes up from a hidden baseline. No blur artifacts, GPU-cheap, the industry-standard headline reveal.
- **Blur-in** — animate `filter: blur(12px) -> blur(0)` with `opacity 0 -> 1`. Soft, premium, "focus-pull" feel. Costlier to render; keep blur radius modest and prefer short durations.
- **Clip-path wipe** — animate `clip-path: inset(0 100% 0 0)` to `inset(0 0 0 0)` for a directional reveal without moving the glyphs.
- **Character stagger** — split to chars, fade/translate each with a 20-40ms offset.

### 4. Apply principle-correct timing

Inline essentials (so this skill stands alone):
- Enter with ease-out: `cubic-bezier(0.16, 1, 0.3, 1)` (easeOutExpo) feels premium.
- Per-fragment duration 400-600ms.
- Stagger: lines 60-100ms, words 40-70ms, characters 20-40ms apart.
- Cap total reveal near ~800ms; for long strings, reduce per-char offset or switch to word/line granularity.

### 5. Mask-reveal, copy-paste (vanilla CSS + JS line split)

```html
<h1 class="reveal" aria-label="Designed for motion">Designed for motion</h1>
```

```css
.reveal .line { overflow: hidden; }
.reveal .line > span {
  display: inline-block;
  transform: translateY(110%);
  animation: rise 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.reveal .line:nth-child(2) > span { animation-delay: 0.08s; }
.reveal .line:nth-child(3) > span { animation-delay: 0.16s; }
@keyframes rise { to { transform: translateY(0); } }
```

### 6. Variable-font weight animation

```css
@keyframes thicken {
  from { font-variation-settings: "wght" 200; }
  to   { font-variation-settings: "wght" 800; }
}
.headline {
  font-family: "Inter var", sans-serif;
  animation: thicken 0.8s cubic-bezier(0.65, 0, 0.35, 1) forwards;
}
```

Animate `font-variation-settings` (covers any axis: `wght`, `wdth`, `slnt`, `opsz`, plus custom axes), not `font-weight`, to hit non-standard values and to interpolate smoothly. Confirm the loaded font is actually a variable font and the axis range (e.g. wght 100-900) before animating, or the value clamps silently.

## Deliver & verify (standalone HTML)

> **Packaged helper** (`scripts/`): `scripts/seek-shot.sh anim.html 0 1.5 3` freezes the `?t=N` harness and screenshots each moment; `scripts/contact-sheet.sh sheet.png frame-*.png` tiles them for one-glance review. See `scripts/README.md`.

For a web text reveal / kinetic-title deliverable, ship **one `.html` file that opens directly in a browser** — no build step. One file is the right tier for a headline, title card, or single reveal.

**Output contract:**
- One `.html` file: markup with `aria-label` on the container, the reveal in inline `<style>` (or one inline GSAP `<script>` from CDN).
- One animation driver — a CSS `@keyframes` reveal, or a single GSAP timeline; not both.
- Include the freeze harness below so any moment can be screenshotted deterministically.
- Split AFTER `document.fonts.ready` so line breaks are correct in the frozen frame.

**Freeze harness — pin a frame for screenshots.**

```html
<script>
  const t = new URLSearchParams(location.search).get("t");
  if (t !== null) {
    // CSS @keyframes reveal:
    document.querySelectorAll(".reveal *").forEach(el => {
      el.style.animationDelay = (-parseFloat(t)) + "s";
      el.style.animationPlayState = "paused";
    });
    // GSAP timeline instead? → tl.pause(); tl.seek(parseFloat(t));
  }
  window.__ready = true;                                          // ready signal for headless wait
</script>
```

**Verify loop — render → freeze → screenshot → check:**
1. Open the file frozen at start / mid / end: `…/type.html?t=0`, `?t=<dur/2>`, `?t=<dur>`.
2. Screenshot each frozen frame.
3. Check **fidelity** (matches the brief) and **artifacts** — clipped glyphs/descenders, masks that don't fully hide the baseline, FOUC or wrong line breaks before fonts load, blur fringing.

```bash
npx playwright screenshot --wait-for-timeout=500 "file://$PWD/type.html?t=0.4" frame-mid.png
```

**Before you finish:**
1. Opens standalone in a browser — no console errors, no missing CDN/font.
2. One reveal driver; `?t=N` freezes the exact frame correctly.
3. Screenshotted at start / mid / end — no clipped glyphs, no FOUC, line breaks correct.
4. `prefers-reduced-motion` honored (text shown in final state, no motion).
5. `aria-label` on the container; split fragments `aria-hidden` — copy and screen-reader text intact.

## Quick reference

| Effect | Core CSS / approach |
|---|---|
| Mask up reveal | parent `overflow:hidden`; child `translateY(110%)->0` |
| Blur in | `filter: blur(12px)->0` + opacity |
| Directional wipe | `clip-path: inset(0 100% 0 0)->inset(0)` |
| Char stagger | split chars, 20-40ms offset, fade+rise |
| Variable weight | animate `font-variation-settings:"wght" a->b` |
| Text on path | SVG `<textPath href="#curve">` |
| Stroke draw-on | SVG text as path, animate `stroke-dashoffset` |

## Text on a path (SVG)

```html
<svg viewBox="0 0 600 200">
  <path id="curve" d="M20,150 Q300,20 580,150" fill="none" />
  <text font-size="42" fill="#fff">
    <textPath href="#curve" startOffset="0%">Follow the curve</textPath>
  </text>
</svg>
```

Animate the `startOffset` attribute (`0%` -> `100%`) to scroll text along the path, or animate the path `d` to make text flow on a morphing curve.

## Reference files

- `references/reveal-recipes.md` — copy-paste reveal cookbook: mask/blur/clip/char-stagger in CSS, GSAP SplitText timelines, Framer Motion staggered variants, Remotion per-character interpolation, variable-font keyframes, and a screen-reader-safe split helper.

<!-- craft-handoff:start -->
## Mở và sửa tiếp trong FilmCraft / EffectCraft

Khi user muốn sửa tiếp trong FilmCraft hoặc EffectCraft, không giao một MP4 phẳng: viết timeline spec rồi dùng skill `craft-handoff` dựng project gốc (`.fcproj` / `.ecproj`) có đủ track, clip, keyframe, chữ, effect và SFX. Với skill này: mỗi cảnh một clip (nền trong suốt nếu phủ lên nền khác); tiêu đề ít chuyển động → text clip gốc; cần chỉnh chuyển động từng ký tự → EffectCraft qua `ae-script-builder`. Chi tiết: `craft-handoff/references/skills-map.md`.
<!-- craft-handoff:end -->

<!-- ===== /file: kinetic-typography/SKILL.md ===== -->

<!-- ===== file: kinetic-typography/README.md ===== -->



<!-- ===== /file: kinetic-typography/README.md ===== -->

<!-- ===== file: kinetic-typography/references/reveal-recipes.md ===== -->

# Text reveal recipes (copy-paste)

Runnable cookbook across CSS, GSAP, Framer Motion, and Remotion. All timings follow ease-out enters (`cubic-bezier(0.16, 1, 0.3, 1)`) with line/word/char stagger of 60-100 / 40-70 / 20-40 ms.

Accessibility rule for every per-fragment split: put the full string in `aria-label` on the container and `aria-hidden="true"` on the fragments.

---

## 1. CSS-only mask reveal (no JS split, pre-wrapped lines)

```html
<h1 class="mask-reveal" aria-label="Built for speed">
  <span class="line"><span aria-hidden="true">Built for</span></span>
  <span class="line"><span aria-hidden="true">speed</span></span>
</h1>
```

```css
.mask-reveal .line { display: block; overflow: hidden; }
.mask-reveal .line > span {
  display: inline-block;
  transform: translateY(110%);
  animation: maskRise 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.mask-reveal .line:nth-child(1) > span { animation-delay: 0s;   }
.mask-reveal .line:nth-child(2) > span { animation-delay: 0.08s; }
@keyframes maskRise { to { transform: translateY(0); } }
```

## 2. CSS blur-in (premium focus-pull)

```css
.blur-in {
  opacity: 0;
  filter: blur(12px);
  animation: blurIn 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes blurIn {
  to { opacity: 1; filter: blur(0); }
}
```

## 3. CSS clip-path directional wipe

```css
.wipe {
  clip-path: inset(0 100% 0 0);          /* fully clipped from the right */
  animation: wipe 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes wipe { to { clip-path: inset(0 0 0 0); } }
```

## 4. Character stagger with vanilla JS split (screen-reader safe)

```js
function splitChars(el) {
  const text = el.textContent;
  el.setAttribute('aria-label', text);
  el.textContent = '';
  [...text].forEach((ch, i) => {
    const span = document.createElement('span');
    span.textContent = ch === ' ' ? ' ' : ch;
    span.setAttribute('aria-hidden', 'true');
    span.style.display = 'inline-block';
    span.style.animationDelay = `${i * 0.03}s`; // 30ms per char
    span.className = 'char';
    el.appendChild(span);
  });
}
document.querySelectorAll('.stagger').forEach(splitChars);
```

```css
.char {
  opacity: 0;
  transform: translateY(0.4em);
  animation: charIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes charIn { to { opacity: 1; transform: translateY(0); } }
```

---

## 5. GSAP SplitText (requires GSAP 3.13+, SplitText now free)

```js
import gsap from "gsap";
import { SplitText } from "gsap/SplitText";
gsap.registerPlugin(SplitText);

const split = new SplitText(".headline", { type: "lines,words,chars" });

gsap.from(split.chars, {
  yPercent: 110,
  opacity: 0,
  duration: 0.6,
  ease: "expo.out",
  stagger: 0.03,          // 30ms per char
});

// Mask reveal by lines (wrap lines so overflow hides them)
const splitLines = new SplitText(".headline", {
  type: "lines",
  linesClass: "split-line",
  mask: "lines",          // SplitText auto-creates overflow:hidden wrappers
});
gsap.from(splitLines.lines, {
  yPercent: 100,
  duration: 0.8,
  ease: "expo.out",
  stagger: 0.1,
});

// Always revert when done to restore the original DOM (and accessibility)
// split.revert();
```

GSAP eases worth knowing: `expo.out`, `power4.out`, `back.out(1.7)` (overshoot), `elastic.out(1, 0.3)` (bouncy).

---

## 6. Framer Motion staggered words/chars

```jsx
import { motion } from "framer-motion";

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.04, delayChildren: 0.1 } },
};
const child = {
  hidden: { y: "110%", opacity: 0 },
  show: {
    y: "0%",
    opacity: 1,
    transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] },
  },
};

export function Headline({ text }) {
  return (
    <motion.h1
      aria-label={text}
      variants={container}
      initial="hidden"
      animate="show"
      style={{ display: "flex", flexWrap: "wrap", overflow: "hidden" }}
    >
      {text.split(" ").map((word, i) => (
        <span key={i} style={{ overflow: "hidden", marginRight: "0.25em" }}>
          <motion.span aria-hidden variants={child} style={{ display: "inline-block" }}>
            {word}
          </motion.span>
        </span>
      ))}
    </motion.h1>
  );
}
```

---

## 7. Remotion per-character reveal

```jsx
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

export const KineticText = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <h1 aria-label={text} style={{ display: "flex", overflow: "hidden" }}>
      {text.split("").map((char, i) => {
        const delay = i * 2; // 2 frames per char ≈ 33ms at 60fps
        const progress = spring({
          frame: frame - delay,
          fps,
          config: { damping: 200, stiffness: 200, mass: 0.5 },
        });
        const y = interpolate(progress, [0, 1], [110, 0]);
        return (
          <span
            key={i}
            aria-hidden
            style={{
              display: "inline-block",
              transform: `translateY(${y}%)`,
              opacity: progress,
              whiteSpace: "pre",
            }}
          >
            {char}
          </span>
        );
      })}
    </h1>
  );
};
```

---

## 8. Variable-font weight + width animation (CSS)

```css
@keyframes flex {
  0%   { font-variation-settings: "wght" 200, "wdth" 75; }
  100% { font-variation-settings: "wght" 800, "wdth" 125; }
}
.variable {
  font-family: "Roboto Flex", sans-serif;  /* must be a variable font */
  animation: flex 1.2s cubic-bezier(0.65, 0, 0.35, 1) infinite alternate;
}
```

Per-character weight wave (JS, drives a CSS var):

```js
const chars = document.querySelectorAll('.wave .char');
function tick(t) {
  chars.forEach((c, i) => {
    const w = 400 + Math.sin(t / 400 + i * 0.5) * 350; // 50..750
    c.style.fontVariationSettings = `"wght" ${w.toFixed(0)}`;
  });
  requestAnimationFrame(tick);
}
requestAnimationFrame(tick);
```

---

## 9. SVG stroke draw-on (outline text)

Convert text to outlines in a vector tool (or use a stroked font path), then:

```css
.draw-text path {
  fill: transparent;
  stroke: #fff;
  stroke-width: 2;
  stroke-dasharray: 1000;
  stroke-dashoffset: 1000;
  animation: draw 2s ease forwards;
}
@keyframes draw { to { stroke-dashoffset: 0; } }
```

---

## 10. After Effects expression (per-char delay via index)

On a text layer's position or opacity, using a Text Animator is the native path, but for code-driven control attach this opacity expression with a slider for stagger:

```javascript
// On opacity; "Delay" slider in seconds-per-char
d = thisComp.layer("Controller").effect("Delay")("Slider");
start = inPoint + textIndex * d;   // textIndex via per-character animator
ease(time, start, start + 0.4, 0, 100);
```

In practice prefer AE's Range Selector + offset animator for character stagger; reserve expressions for data-driven or non-linear orderings.

---
Reveal type by line, word, or char with the right rhythm and the words perform. Built by **[iart.ai](https://iart.ai/?utm_source=github&utm_medium=readme&utm_campaign=kinetic-typography-skills&utm_content=skill_footer&utm_term=kinetic-typography)** — the AI motion agent for editable, on-brand motion graphics.

<!-- ===== /file: kinetic-typography/references/reveal-recipes.md ===== -->

<!-- ===== file: kinetic-typography/scripts/README.md ===== -->

# `scripts/` — verify-loop toolkit

Deterministic helpers the agent **calls** instead of hand-rolling, to close every skill's
*deliver-and-verify* loop: freeze a moment, see start/mid/end at a glance, and assert the
encoded file's real spec. Small, dependency-light, tier-matched.

| Script | Tier | What it does |
|---|---|---|
| `seek-shot.sh` | **Light** (standalone HTML) | Drives the page's `?t=N` seek harness and screenshots each frozen moment. |
| `contact-sheet.sh` | any | Tiles the frames side-by-side into one image (start \| mid \| end) for one-glance review. |
| `probe-mp4.sh` | **Heavy** (Remotion / Manim) | Reads + asserts the MP4's real resolution / codec / fps / duration. |

## Usage by tier

**Light — standalone HTML** (`?t=N` harness): freeze, shoot, tile.
```bash
scripts/seek-shot.sh anim.html 0 1.5 3        # → frame-0.png frame-1.5.png frame-3.png
scripts/contact-sheet.sh sheet.png frame-*.png
# inspect sheet.png: matches the brief? clipped text / off-canvas / FOUC?
```

**Heavy — Remotion**: render stills with the *real* shipped props, tile, then assert the MP4.
```bash
npx remotion still Short out/f-hook.png --frame=10 --props='{...}'
npx remotion still Short out/f-mid.png  --frame=N  --props='{...}'
npx remotion still Short out/f-end.png  --frame=L  --props='{...}'
scripts/contact-sheet.sh sheet.png out/f-hook.png out/f-mid.png out/f-end.png
npx remotion render Short out/short.mp4 --props='{...}'
scripts/probe-mp4.sh out/short.mp4 1080x1920 30      # vertical short contract
```

**Heavy — Manim**: save the last frame (`-s`) / a range (`-n a,b`), tile, assert.
```bash
manim -s -ql scene.py MyScene                        # media/images/.../MyScene.png
scripts/probe-mp4.sh media/videos/scene/480p15/MyScene.mp4
```

## Requirements
- `seek-shot.sh` → `npx` + Playwright Chromium (`npx playwright install chromium` once).
- `contact-sheet.sh` / `probe-mp4.sh` → `ffmpeg` / `ffprobe`.

All three are POSIX `bash`; run them from the project where your deliverable lives.

<!-- ===== /file: kinetic-typography/scripts/README.md ===== -->
