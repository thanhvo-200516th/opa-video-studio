# kb-motion-presets-vi — toàn văn tài liệu của nguồn `motion-presets-vi`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/motion-presets-vi/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: motion-presets-vi/MODULE.md ===== -->

<!-- master-video-edit: mô-đun nhập 2026-10-29 -->
> **Mô-đun `motion-presets-vi`** của `master-video-edit` — kiến thức tham khảo (không chạy công cụ trong file nếu chưa có).
> Thêm gì: Vietnamese diacritic rules for Remotion text (NFC/grapheme split, line-height 1.3, letter-spacing)
> Nguồn (USB): `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Media Super Powers/tmp-taw-video/skills/motion-presets-vi`
> **Khi dùng trên máy Linux này:**
> - remove or implement the CharFade/LineReveal/Typewriter/ShakeEmphasis/HighlightMarker catalog
> - copy demo/claude-3-reasons/src/motion-presets-vi/{normalize.ts,WordStagger.tsx,index.ts} as the real code
> - drop the '@/motion-presets-vi' alias and scene-coder agent refs
> Công cụ OpenChatCut nhắc trong file (nếu có) chỉ dùng được khi app OpenChatCut mở, qua MCP `openchatcut`; không có thì làm bằng ffmpeg / faster-whisper / FilmCraft.

---
name: motion-presets-vi
description: >
  Library of kinetic typography motion presets that handle Vietnamese diacritics
  correctly. Generic motion libraries break on stacked marks (ầ, ố, ữ, ặ) because
  letterforms include combining characters. This skill provides ready-to-use Remotion
  components: per-char fade, word-stagger, line-reveal, typewriter, shake-emphasis,
  highlight-marker — each tested with full Vietnamese alphabet (84 letters with marks).
  Used by scene-coder agent when format is kinetic-typography or any scene with prominent text.
  Trigger phrases (EN + VN): "motion text", "kinetic typography", "text animation",
  "chu chay", "chu xuat hien", "hoat hinh chu", "text dau tieng viet".
allowed-tools: Read, Write, Edit
---

# motion-presets-vi

Drop-in Remotion components for Vietnamese-aware text animation. The pure-React presets handle Unicode normalization (NFC) so marks animate WITH their base letter, not separately — solving the most common bug where "ầ" splits into "a" + "̂" + "̀" with each animating independently.

## Available presets (drop-in components)

Each is an exported component you import from `@/motion-presets-vi`. Inputs: `text` + timing props. Output: a `<Sequence>` you place inside a scene.

### 1. `<CharFade text="..." />`

Each character fades in 1 by 1, ~33ms apart. Diacritics stay attached to base letter.

```tsx
<CharFade text="Xin chào, đây là kit làm video" delayPerChar={2} />
```

Internally: `Array.from(text.normalize('NFC'))` keeps "đ" as 1 char, "ầ" as 1 char.

### 2. `<WordStagger text="..." />`

Words slide up + fade in, 80ms stagger. Best for headlines.

```tsx
<WordStagger text="Học AI dễ hơn anh nghĩ" stagger={5} />
```

### 3. `<LineReveal lines={[...]} />`

Multi-line reveal, top to bottom, with mask wipe. Great for quotes.

```tsx
<LineReveal lines={["Đừng đợi cảm hứng,", "ngồi xuống và làm."]} />
```

### 4. `<Typewriter text="..." />`

Mono-spaced char-by-char like cursor typing. **Important**: skips animation on combining marks so "ô" types as 1 keystroke not 2.

```tsx
<Typewriter text="$ npm install remotion" cps={20} />
```

### 5. `<ShakeEmphasis text="..." word="..." />`

The `word` argument is shaken (4px amplitude, 8Hz) when reached, rest of text static.

```tsx
<ShakeEmphasis text="Đây là điều quan trọng nhất" word="quan trọng" />
```

### 6. `<HighlightMarker text="..." word="..." color="#fbbf24" />`

Yellow-marker swipes under the named word at midpoint. The marker SVG path adapts to the rendered text width — works with VN diacritics that make some lines taller (ổ vs o).

```tsx
<HighlightMarker text="Đầu tư cho bản thân là đầu tư tốt nhất" word="bản thân" color="#fbbf24" />
```

## Vietnamese diacritic gotchas (engineering notes)

When `scene-coder` writes new motion components from scratch, follow these rules:

### 1. Always normalize text to NFC

```tsx
const chars = Array.from(text.normalize('NFC'));
```

NFC ("Composed") merges base + combining marks into single codepoints when possible. Without this, "ầ" (U+0061 U+0302 U+0300) becomes 3 array entries instead of 1 (U+1EA7).

### 2. But also handle the irreducible cases

Some VN sequences only exist as base + combining (no precomposed form), e.g. when using vi-VN keyboards that output decomposed by default. Detect with:

```tsx
const isCombining = (cp: number) => cp >= 0x0300 && cp <= 0x036F;
```

Group with previous char before animating.

### 3. Font choice matters

Stick to fonts with full VN coverage:
- **Be Vietnam Pro** (open-source, designed for VN — primary recommendation)
- **Inter** (good VN support since v3.19)
- **Noto Sans Vietnamese** (Google fallback)
- AVOID: Roboto (incomplete dấu nặng on uppercase), Helvetica (no built-in VN), Times New Roman web fallback (broken stacking)

Load via `@remotion/google-fonts/BeVietnamPro`:

```tsx
import { loadFont } from '@remotion/google-fonts/BeVietnamPro';
const { fontFamily } = loadFont();
```

### 4. Line height for stacked marks

VN with both tone mark + circumflex (ầ, ố, ữ) is taller than English equivalent. Use `lineHeight: 1.3` minimum to prevent clipping.

```tsx
<div style={{ fontFamily, lineHeight: 1.3, fontSize: 96 }}>
  {text}
</div>
```

### 5. Letter-spacing nuance

Tight letter-spacing (`-0.02em`) collapses dấu hỏi/ngã into adjacent characters. Default to `0` or positive for headline VN text.

## Generating new presets — checklist for scene-coder

When you need a motion not in the library, write it WITH these gates:

1. ✅ Test with: `"đường về nhà ngắn lại sau mỗi mùa thu vàng ươm những giấc mộng"` (covers đ, ờ, ề, ề, ặ, ấ, ỗ, ấ, ầ, ố, ơ, ư, ơ, ư, ữ, ấ, ộ).
2. ✅ Render at full kinetic speed (each char ≤ 100ms) — confirm marks don't detach mid-animation.
3. ✅ Render at common font sizes (32, 64, 96, 128) — confirm dấu nặng (.) doesn't get clipped.
4. ✅ Test with `lineHeight: 1.0` — should NOT clip but if it does, document that preset needs ≥ 1.3.

## File outputs

When invoked, this skill writes to `src/motion-presets-vi/`:

```
src/motion-presets-vi/
├── index.ts                    # exports all presets
├── CharFade.tsx
├── WordStagger.tsx
├── LineReveal.tsx
├── Typewriter.tsx
├── ShakeEmphasis.tsx
├── HighlightMarker.tsx
├── lib/
│   ├── normalize.ts            # NFC normalize + combining-mark grouping
│   └── easing.ts               # tuned easing curves for VN text rhythm
```

(Stub files written on first invoke. Full implementations in v0.2.)

## When NOT to use this skill

- Logo animation, icon motion → use `scene-presets` instead (no text-specific concerns).
- English-only content → can use any generic motion lib; this is overkill but won't break.
- Heavy 3D / particle effects → out of scope; consider Manim fallback or After Effects export.

<!-- ===== /file: motion-presets-vi/MODULE.md ===== -->
