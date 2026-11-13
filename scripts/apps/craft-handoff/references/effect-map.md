# FilmCraft → EffectCraft mapping (`tools/ec_build.py`)

A spec names effects by their **FilmCraft id** and FilmCraft parameter names (timeline-spec.md).
`ec_build.py` turns the ids below into EffectCraft effects. Anything else lands in the report's
`unsupported` list as `where: what — why`. Nothing is dropped silently.

How a parameter is addressed: EffectCraft's `effect.list` gives every effect's parameters in order
(ids like `basicCorrection/tone/exposure`). ec_build.js walks the effect's leaf properties in that
same order and checks the display name before setting a value. At start-up the builder checks that
every id in this table still exists in the running EffectCraft, and stops with a clear error if one
is missing. Popup values are zero-based in the spec and become one-based in JS. Colours `#RRGGBB` or
`[r, g, b(, a)]` (0–1) become RGBA. Any parameter can be a keyframe list (see the interpolation table
at the end).

## Effects

| FilmCraft id | FilmCraft param | EffectCraft effect (id · AE matchName) | EffectCraft param | Notes |
|---|---|---|---|---|
| `gaussian_blur` | `blurriness` | Gaussian Blur (`ec.blur.gaussian` · `ADBE Gaussian Blur 2`) | `blurriness` | 1:1 (px). Other params → unsupported. |
| `directional_blur` | `direction`, `length` | Directional Blur (`ec.blur.directional` · `ADBE Motion Blur`) | `direction`, `length` | 1:1. |
| `lumetri` | `exposure` `contrast` `highlights` `shadows` `whites` `blacks` | Lumetri Color (`ec.color.lumetri` · `ADBE Lumetri`) | `basicCorrection/tone/<same>` | 1:1, same ranges (exposure −5…5 stops, the rest −100…100). |
| `lumetri` | `temperature`, `tint` | Lumetri Color | `basicCorrection/whiteBalance/<same>` | 1:1. |
| `lumetri` | `saturation` | Lumetri Color | `basicCorrection/saturation` | 1:1 (100 = unchanged, 0…200). |
| `lumetri` | `faded_film` `sharpen` `vibrance` `shadow_tint` `highlight_tint` | Lumetri Color | `creative/adjustments/fadedFilm` … `shadowTint` `highlightTint` | 1:1; tints are colours. |
| `lumetri` | `vignette_amount` `_midpoint` `_roundness` `_feather` | Lumetri Color | `vignette/vignetteAmount` … | 1:1. |
| `lumetri` | `basic_on` `creative_on` `vignette_on` `curves_on` `wheels_on` `hsl_on` | — | — | EffectCraft Lumetri has no section switches. `true` is ignored; `false` → unsupported (the section's values are still applied). |
| `lumetri` | `look_lut`, `look_intensity`, curves, wheels, HSL | — | — | → unsupported (FilmCraft's built-in LUT names have no EffectCraft equivalent). |
| `drop_shadow` | `color` `opacity` `direction` `distance` `softness` | Drop Shadow (`ec.perspective.dropshadow` · `ADBE Drop Shadow`) | same names | 1:1. Both apps default to 50 % / 135° / 5 px / softness 0. |
| `rounded_crop` | `left` `right` `top` `bottom` `radius` | layer **mask** (rounded-rectangle Bezier path) | — | **Approximated.** Crop values are taken as % of the source size, radius in source px. Static only: animated values keep their first key and are reported. Other params (e.g. `feather`) → unsupported. |
| `rounded_crop` | `border`, `border_color` | Stroke (`ec.generate.stroke` · `ADBE Stroke`) on that mask | `brushSize` = border, `color` | **Approximated:** the stroke is centred on the mask edge, not inside it. |
| `motion`, `opacity` (as effects) | — | — | — | → unsupported: write them as the clip's `motion` / `opacity` keys (below). |
| `grow`, `shrink`, `move` | — | — | — | → unsupported. Their timing semantics are FilmCraft-internal; express the move as `motion` keys instead. |
| `lowpass` and other audio effects | — | (EffectCraft has High-Low Pass `ec.audio.highlowpass`) | — | → unsupported until FilmCraft's parameter names are confirmed. |
| anything else | — | — | — | → unsupported. |

## Clip properties (not effects)

| Spec | EffectCraft | Notes |
|---|---|---|
| `motion.position` / `anchor` / `scale` / `rotation` | Transform › Position / Anchor Point / Scale / Rotation | Frame px, top-left origin. Anchor is in the source's own px; the default is the source centre, as in both apps. Scale `n` → `[n, n]`. |
| `opacity` | Transform › Opacity | 0–100. |
| `blend` | layer blending mode | normal / screen / multiply / add / overlay. |
| `speed` | layer Stretch = 100 × 100 / speed | `startTime = at − in × stretch / 100`. Checked with a 200 % clip against the source frame. |
| `gain_db` (constant or keys) | Audio › Audio Levels `[dB, dB]` | Keys become Audio Levels keys. |
| `audio: false` | layer audio switch off | A video file on an audio track has its video switch off. |
| `transition_in` / `transition_out` `cross_dissolve` | Opacity keys 0 → value over `frames` | **Approximated.** For `transition_in`, the clip just before it on the same track (if it ends at the cut and has source left) is extended `frames` under it, so the result is a real dissolve. Its sound is cut at the original out point with two Audio Levels keys (hold, then −192 dB). Clips that animate their own opacity skip the transition (reported). Other transition ids → unsupported. |
| text `font` + `style` | TextDocument font family + style | Resolved against `text.fonts`. A missing style takes the closest weight; a missing family falls back to Inter (bundled). Every fallback goes to the report's `fonts`. |
| text `stroke.width` | stroke width × 2, fill over stroke | AE strokes are centred on the outline. Doubling shows `width` px outside the glyph, like FilmCraft's outer stroke. |
| text `shadow` {color, opacity, blur, distance} | Drop Shadow effect | blur → softness. |
| text `size`, `color`, stroke (animated) | first key only | → unsupported. A text layer has one style unless Source Text is keyed. |
| text `position` | layer position (anchor 0,0 = first baseline at the alignment point) | Same meaning as the spec. |
| captions SRT | one text layer per cue, above every track | Wrapped at ~0.9 × frame width (0.5 em per glyph estimate), last line on the baseline at 75 % of the height. Style keys in `captions` (font, style, size, color, position, stroke…) override the default (Be Vietnam Pro Bold 64, white, 4 px black outer stroke). EffectCraft also shrinks a cue that is still too wide; the font-size change goes to warnings. |
| markers | comp markers | Comment = `name` (`: comment` appended). |
| top-level `unsupported` / `notes` (adapters) | report `unsupported` / `notes` | Passed through so the user hears about them. |

## Keyframe interpolation

The interpolation written on a key describes **that key** (Premiere / AE meaning, same as fc_build.py):

| Spec | AE key in-side | AE key out-side |
|---|---|---|
| `linear` (default) | linear | linear |
| `bezier` | Easy Ease (speed 0, influence 33.3 %) | Easy Ease |
| `easeIn` — slow arrival at this key | Easy Ease | linear |
| `easeOut` — slow departure from this key | linear | Easy Ease |
| `hold` | linear | hold (value stays until the next key) |

So `easeOut` on a clip's last key has no visible effect. EffectCraft keys sit on whole frames. Key
times are clip-relative and rounded to the nearest frame. When several keys fall inside one frame
(e.g. a 10 ms SFX fade), the first stays, the last moves to the next frame and the ones between are
dropped. That case is reported under `approximations`.
