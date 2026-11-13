# Craft timeline spec (`*.craft.json`)

One JSON file describes the edit. `tools/fc_build.py` turns it into a FilmCraft project (`.fcproj`),
`tools/ec_build.py` into an EffectCraft project (`.ecproj`). Both builders drive the real app through
its control port, so the saved project is written by the app itself and opens with every track, clip,
keyframe, text and effect editable.

## Top level

```json
{
  "name": "KB03 Tu duy AI",          // sequence / comp name
  "width": 1080, "height": 1920,     // frame size (px)
  "fps": 25,                         // timeline frame rate
  "sample_rate": 48000,              // optional, default 48000
  "duration": 30.0,                  // optional; default = end of the last clip
  "tracks": [ ... ],                 // bottom → top for video, A1 → An for audio
  "captions": {"srt": "/abs/subs.srt"},          // optional
  "markers": [{"at": 3.0, "name": "Beat 2", "comment": ""}],  // optional
  "notes": ["..."],                  // optional, free text for whoever opens the project
  "unsupported": [{"what": "...", "why": "...", "where": "..."}]   // optional: what the source edit
                                     // had that the spec could not carry; builders copy it to the report
}
```

All paths are absolute. All times are **seconds**. `at` is where the clip starts on the timeline;
key times inside a clip are **relative to the clip start**.

## Tracks

```json
{"type": "video", "name": "V1 A-roll", "clips": [ ... ]}
{"type": "text",  "name": "V3 Title",  "clips": [ ... ]}   // FilmCraft: graphic clips; EffectCraft: text layers
{"type": "audio", "name": "A2 SFX",    "clips": [ ... ]}
```

Video and text tracks share one stack in list order: the first visual track is V1 (bottom), the next
sits above it. Audio tracks are A1, A2… in list order. A video clip that carries sound puts it on the
first audio track unless the clip says `"audio_track": "A3"` or `"audio": false`.

## Clips

Media clip (video, image or audio track):

```json
{
  "src": "/abs/a-roll.mp4",
  "at": 0.0,            // timeline start
  "in": 12.4,           // source in point, default 0
  "dur": 4.0,           // default: rest of the source (stills: 5 s)
  "name": "Hook",       // optional clip name
  "speed": 100,         // optional, percent
  "gain_db": -6,        // optional, audio
  "audio": true,        // optional, false = video only
  "motion": {"scale": 100, "position": [540, 960], "rotation": 0, "anchor": [540, 960]},
  "opacity": 100,
  "blend": "normal",    // optional: normal|screen|multiply|add|overlay
  "effects": [{"effect": "gaussian_blur", "params": {"blurriness": 0}}],
  "preset": "[DViet] Flash Out",                 // optional, FilmCraft preset name
  "transition_in":  {"effect": "cross_dissolve", "frames": 8},
  "transition_out": {"effect": "cross_dissolve", "frames": 8}
}
```

Text clip (text track):

```json
{
  "text": "Tư duy AI", "at": 1.0, "dur": 2.5,
  "font": "Be Vietnam Pro", "style": "ExtraBold", "size": 120,
  "color": "#FFFFFF", "align": "center",               // left|center|right
  "position": [540, 700],                              // alignment point of the first baseline
  "stroke": {"color": "#000000", "width": 6},          // optional
  "shadow": {"color": "#000000", "opacity": 60, "blur": 12, "distance": 0},   // optional
  "tracking": 0, "leading": 0,
  "motion": {...}, "opacity": ..., "effects": [...], "transition_in": {...}
}
```

## Animated values

Any number, `[x, y]` or colour above can be a keyframe list instead of a constant:

```json
"scale": [[0, 100], [0.4, 112, "bezier"], [3.6, 112], [4.0, 100]]
"position": [[0, [540, 1100], "easeOut"], [0.5, [540, 960], "easeIn"]]
"opacity": [[0, 0], [0.25, 100], [2.25, 100], [2.5, 0]]
```

Each key is `[time, value, interpolation?]`; interpolation is `linear` (default), `bezier`,
`easeIn`, `easeOut`, `hold`, with the Premiere / After Effects meaning on the key it sits on:
`easeIn` slows the arrival **into** that key, `easeOut` slows the departure **from** it, `bezier`
eases both sides, `hold` keeps the value until the next key. To make a move settle softly, put
`easeIn` on the key where it lands (an `easeOut` on a clip's last key does nothing).
Units follow the apps: scale in %, rotation in degrees, opacity 0–100, position/anchor in frame
pixels with (0, 0) top-left. A text clip's `motion.scale` scales around its `anchor`, which defaults
to the frame centre — set `anchor` to the text `position` for a pop in place.

## Timing rules the builders apply

- Times snap to whole frames (half-up): 4.5 s at 25 fps lands on 4.52 s.
- Clips on one track must not overlap. A clip without `dur` that would run into the next clip on its
  track is trimmed to that clip's start and the report warns. Give overlapping sounds (an SFX tail
  under the next cue) their own track instead.
- A video clip's sound cannot land on an audio track that already has clips at that time — the build
  stops with an error; give it `"audio_track"` or `"audio": false`.
- Not expressible yet: caption style / language (FilmCraft imports the SRT with its default style),
  marker colours. Fonts the app does not have are substituted and reported as warnings.

## Effects

`effect` is the FilmCraft effect id (`effects.list` in FilmCraft, e.g. `gaussian_blur`, `lumetri`,
`drop_shadow`, `rounded_crop`, `grow`, `shrink`, `lowpass`). `params` uses that effect's parameter
names; any param can be animated as above. `ec_build.py` maps the ids it knows to EffectCraft effects
(see `references/effect-map.md`) and reports the ones it cannot map instead of dropping them silently.

## What does not belong in a spec

- A finished render of the whole video as one clip. The point is an editable timeline: cuts, zooms,
  text, SFX and overlays each stay their own clip.
- Graphics that only code can draw (Remotion / HyperFrames / Manim scenes) as one flattened layer
  over the footage. Render each graphic element with alpha (ProRes 4444 `.mov` or PNG sequence) and
  give it its own clip and track, timed where it appears.
