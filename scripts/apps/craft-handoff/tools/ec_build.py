#!/usr/bin/env python3
"""ec_build — build a native EffectCraft project (.ecproj) from a craft timeline spec (*.craft.json).

    python3 ec_build.py SPEC.craft.json OUT.ecproj [--report REPORT.json] [--frames N] [--workdir DIR]

Spec: references/timeline-spec.md. Effect / interpolation mapping: references/effect-map.md.
A private EffectCraft instance (tools/craftctl.py, its own config folder) does the work:
  probe  — import every source; duration, size and sound come from the app itself
  build  — one comp, every clip its own layer; tools/ec_build.js executes the plan made here
  save   — file.saveAs OUT
  verify — re-open OUT in a fresh instance, read the comp back, compare it with the plan, optional QA stills.
Exit 0 = verified, 1 = the re-opened project differs from the plan, 2 = invalid spec or app error.
Env: CRAFT_DISPLAY (X display of the private instance), CRAFT_BIN_DIR.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import sys
import tempfile
import textwrap
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from craftctl import Craft, CraftError  # noqa: E402

JS_FILE = TOOLS / "ec_build.js"
# spec interpolation written on a key -> (incoming side, outgoing side) of that After Effects key
INTERP_SIDES = {"linear": ("linear", "linear"), "bezier": ("ease", "ease"), "easeIn": ("ease", "linear"),
                "easeOut": ("linear", "ease"), "hold": ("linear", "hold")}
BLENDS = {"normal", "screen", "multiply", "add", "overlay"}
ALIGNS = {"left", "center", "right"}
TRANSITIONS = {"cross_dissolve"}
STILL_SECONDS = 5.0
SILENT_DB = -192.0
FALLBACK_FONT = "Inter"                      # bundled with EffectCraft
CAPTION_STYLE = {"font": "Be Vietnam Pro", "style": "Bold", "size": 64, "color": "#FFFFFF",
                 "align": "center", "stroke": {"color": "#000000", "width": 4}}
CAPTION_Y = 0.75                             # caption baseline, fraction of the frame height
CAPTION_MAX_W = 0.9                          # captions wrap / shrink to this fraction of the frame width
CAPTION_CHAR_EM = 0.5                        # average glyph width of sentence-case text (em), for wrapping
QA_SCALE = 0.5
WEIGHTS = {"thin": 100, "extralight": 200, "light": 300, "regular": 400, "medium": 500, "semibold": 600,
           "bold": 700, "extrabold": 800, "black": 900}
LUMETRI = {**{k: f"basicCorrection/tone/{k}" for k in ("exposure", "contrast", "highlights", "shadows", "whites",
                                                         "blacks")},
           "temperature": "basicCorrection/whiteBalance/temperature", "tint": "basicCorrection/whiteBalance/tint",
           "saturation": "basicCorrection/saturation", "faded_film": "creative/adjustments/fadedFilm",
           "sharpen": "creative/adjustments/sharpen", "vibrance": "creative/adjustments/vibrance",
           "shadow_tint": "creative/adjustments/shadowTint", "highlight_tint": "creative/adjustments/highlightTint",
           **{f"vignette_{k}": f"vignette/vignette{k.title()}" for k in ("amount", "midpoint", "roundness", "feather")}}
# FilmCraft effect id -> (EffectCraft effect id, {FilmCraft param: EffectCraft param id from effect.list})
EFFECTS = {"gaussian_blur": ("ec.blur.gaussian", {"blurriness": "blurriness"}),
           "directional_blur": ("ec.blur.directional", {"direction": "direction", "length": "length"}),
           "lumetri": ("ec.color.lumetri", LUMETRI),
           "drop_shadow": ("ec.perspective.dropshadow", {k: k for k in ("color", "opacity", "direction", "distance",
                                                                         "softness")})}
SWITCHES = {"lumetri": {"basic_on", "creative_on", "vignette_on", "curves_on", "wheels_on", "hsl_on"}}
CROP_PARAMS = {"left", "right", "top", "bottom", "radius", "border", "border_color"}
STROKE_FX, STROKE_PARAMS = "ec.generate.stroke", ("path", "color", "brushSize")   # rounded_crop border


class SpecError(ValueError):
    """The spec is invalid; the message says where and why."""


# ---------------------------------------------------------------- pure helpers

def frame(t: float, fps: float) -> int:
    return math.floor(t * fps + 0.5)


def snap(t: float, fps: float) -> float:
    """Seconds -> the nearest frame boundary (EffectCraft snaps layer times to frames)."""
    return frame(t, fps) / fps


def is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def is_xy(v) -> bool:
    return isinstance(v, list) and len(v) == 2 and all(is_num(c) for c in v)


def is_keyed(v) -> bool:
    """A keyframe list [[t, v, interp?], ...] rather than a constant."""
    return isinstance(v, list) and len(v) > 0 and all(isinstance(k, list) for k in v)


def first_value(v):
    return v[0][1] if is_keyed(v) else v


def rgb(c) -> list:
    if isinstance(c, str) and re.fullmatch(r"#?[0-9a-fA-F]{6}", c.strip()):
        h = c.strip().lstrip("#")
        return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    if isinstance(c, list) and len(c) in (3, 4) and all(is_num(x) for x in c):
        return [float(x) for x in c[:3]]
    raise SpecError(f"bad colour {c!r} (want #RRGGBB or [r, g, b(, a)] in 0..1)")


def rgba(c) -> list:
    return rgb(c) + [float(c[3]) if isinstance(c, list) and len(c) == 4 else 1.0]


def as_scale(v) -> list:
    return [v, v] if is_num(v) else list(v)


def to_keys(keys: list, at: float, fps: float, conv=lambda v: v, where: str = "value", notes=None) -> list:
    """Spec keys (clip-relative s) -> plan keys (comp s, AE in/out sides). EffectCraft keys sit on whole
    frames: of several keys inside one frame the first stays, the last moves to the next frame and the
    ones between are dropped (a 10 ms fade becomes a one-frame fade); this is noted in `notes`."""
    out, spilled, crowded = [], False, 0
    for k in keys:
        ins, outs = INTERP_SIDES[k[2] if len(k) > 2 else "linear"]
        f, last = frame(at + k[0], fps), frame(out[-1]["t"], fps) if out else None
        if out and f <= last:
            crowded += 1
            if spilled:
                out.pop()
            f, spilled = (last if spilled else last + 1), True
        else:
            spilled = False
        out.append({"t": f / fps, "v": conv(k[1]), "in": ins, "out": outs})
    if crowded and notes is not None:
        notes.append(f"{where}: {crowded} key(s) closer than one frame — merged onto whole frames")
    return out


def animated(value, at: float, fps: float, conv=lambda v: v, where: str = "value", notes=None) -> dict:
    return {"keys": to_keys(value, at, fps, conv, where, notes)} if is_keyed(value) else {"value": conv(value)}


def srt_seconds(s: str) -> float:
    m = re.search(r"(\d+):(\d{1,2}):(\d{1,2})[,.](\d{1,3})", s)
    if not m:
        raise SpecError(f"bad SRT time {s.strip()!r}")
    h, mi, se, ms = m.groups()
    return int(h) * 3600 + int(mi) * 60 + int(se) + int(ms.ljust(3, "0")) / 1000


def parse_srt(text: str) -> list:
    """SRT text -> [(start s, end s, text)]; tags like <i> are dropped, line breaks kept."""
    cues, norm = [], text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n").strip()
    for block in re.split(r"\n\s*\n", norm) if norm else []:
        lines = [ln.strip() for ln in block.split("\n")]
        arrow = next((i for i, ln in enumerate(lines) if "-->" in ln), None)
        if arrow is None:
            raise SpecError(f"SRT block without a time line: {block[:40]!r}")
        start, end = (srt_seconds(s) for s in lines[arrow].split("-->"))
        if end <= start:
            raise SpecError(f"SRT cue {lines[arrow]!r} ends before it starts")
        body = re.sub(r"</?[^>]+>", "", "\n".join(ln for ln in lines[arrow + 1:] if ln))
        if body:
            cues.append((start, end, body))
    return cues


def style_weight(style: str) -> int:
    return WEIGHTS.get(re.sub(r"[\s-]|italic", "", style.lower()) or "regular", 400)


def resolve_font(family: str, style: str, families: list) -> tuple:
    """(family, style, why-not-exact | None) EffectCraft will draw, from text.fonts families."""
    by_name = {f["family"].lower(): f for f in families}
    fam, why = by_name.get(family.lower()), None
    if fam is None:
        fam, why = by_name.get(FALLBACK_FONT.lower()) or families[0], f"family {family!r} is not installed"
    exact = next((s for s in fam["styles"] if s.lower() == style.lower()), None)
    if exact:
        return fam["family"], exact, why
    italic = "italic" in style.lower()
    pool = [s for s in fam["styles"] if ("italic" in s.lower()) == italic] or fam["styles"]
    best = min(pool, key=lambda s: abs(style_weight(s) - style_weight(style)))
    return fam["family"], best, why or f"style {style!r} of {family!r} is not installed"


def index_effects(effect_list: list) -> dict:
    """effect.list -> {effect id: {param id: (1-based leaf index, param)}}; JS walks the leaves in this order."""
    return {e["id"]: {p["id"]: (i + 1, p) for i, p in enumerate(e["params"])} for e in effect_list}


def rounded_rect(x0: float, y0: float, x1: float, y1: float, r: float) -> dict:
    """Closed AE mask path (vertices + tangents) of a rectangle with corner radius r."""
    if r <= 0:
        z = [[0, 0]] * 4
        return {"vertices": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]], "inTangents": z, "outTangents": z}
    k = 0.5523 * r
    v = [[x0 + r, y0], [x1 - r, y0], [x1, y0 + r], [x1, y1 - r], [x1 - r, y1], [x0 + r, y1], [x0, y1 - r], [x0, y0 + r]]
    i = [[-k, 0], [0, 0], [0, -k], [0, 0], [k, 0], [0, 0], [0, k], [0, 0]]
    o = [[0, 0], [k, 0], [0, 0], [0, k], [0, 0], [-k, 0], [0, 0], [0, -k]]
    return {"vertices": v, "inTangents": i, "outTangents": o}


# ---------------------------------------------------------------- validation

def check_anim(v, where: str, shape=None) -> list:
    """shape: 1 = number, 2 = [x, y], 'scale' = number or [x, y], None = anything."""
    ok = {1: is_num, 2: is_xy, "scale": lambda x: is_num(x) or is_xy(x)}.get(shape, lambda x: True)
    if not is_keyed(v):
        return [] if ok(v) else [f"{where}: bad value {v!r}"]
    errs, last = [], -1.0
    for k in v:
        if not (2 <= len(k) <= 3 and is_num(k[0]) and 0 <= k[0] and k[0] > last and ok(k[1])):
            errs.append(f"{where}: bad key {k!r} (want [time >= 0 and increasing, value, interpolation?])")
        elif len(k) == 3 and k[2] not in INTERP_SIDES:
            errs.append(f"{where}: interpolation {k[2]!r} is not one of {', '.join(INTERP_SIDES)}")
        else:
            last = k[0]
    return errs


def check_clip(c, kind: str, where: str) -> list:
    if not isinstance(c, dict):
        return [f"{where}: a clip must be an object"]
    src, motion, effects = c.get("src"), c.get("motion", {}), c.get("effects", [])
    absolute = isinstance(src, str) and src.startswith("/")
    rules = [(is_num(c.get("at")) and c["at"] >= 0, "'at' (timeline start, s >= 0) is required"),
             ("dur" not in c or (is_num(c["dur"]) and c["dur"] > 0), "'dur' must be > 0 seconds"),
             (c.get("blend", "normal") in BLENDS, f"blend must be one of {', '.join(sorted(BLENDS))}"),
             (isinstance(motion, dict), "'motion' must be an object"),
             (isinstance(effects, list), "'effects' must be a list")] + ([
                 (isinstance(c.get("text"), str) and c["text"].strip(), "'text' is required on a text track"),
                 (c.get("align", "center") in ALIGNS, "align must be left, center or right")] if kind == "text" else [
                 (absolute, "'src' must be an absolute path"),
                 (not absolute or Path(src).is_file(), f"source file not found: {src}"),
                 (is_num(c.get("in", 0)) and c.get("in", 0) >= 0, "'in' must be >= 0 seconds"),
                 (is_num(c.get("speed", 100)) and c.get("speed", 100) > 0, "'speed' must be a positive percent")])
    rules += [(c.get(s) is None or (isinstance(c[s], dict) and isinstance(c[s].get("effect"), str) and isinstance(
        c[s].get("frames"), int) and c[s]["frames"] > 0), f"{s} wants {{'effect': id, 'frames': n > 0}}")
              for s in ("transition_in", "transition_out")]
    errs = [f"{where}: {msg}" for ok, msg in rules if not ok]
    anims = [("opacity", c.get("opacity", 100), 1), ("gain_db", c.get("gain_db", 0), 1)]
    if kind == "text":
        anims += [("position", c.get("position", [0, 0]), 2), ("size", c.get("size", 100), 1)]
    anims += [(f"motion.{k}", motion[k], s) for k, s in (("scale", "scale"), ("position", 2), ("anchor", 2),
                                                          ("rotation", 1)) if isinstance(motion, dict) and k in motion]
    for fx in effects if isinstance(effects, list) else []:
        if isinstance(fx, dict) and isinstance(fx.get("effect"), str) and isinstance(fx.get("params", {}), dict):
            anims += [(f"{fx['effect']}.{k}", v, None) for k, v in fx.get("params", {}).items()]
        else:
            errs.append(f"{where}: effects entries want {{'effect': id, 'params': {{...}}}}")
    return errs + [e for name, v, shape in anims for e in check_anim(v, f"{where} {name}", shape)]


def validate(spec) -> list:
    """Every problem in the spec as a readable message; [] = valid."""
    if not isinstance(spec, dict):
        return ["the spec must be a JSON object"]
    tracks, cap = spec.get("tracks"), spec.get("captions")
    srt = cap.get("srt") if isinstance(cap, dict) else None
    rules = [(isinstance(spec.get("name"), str) and spec["name"].strip(), "name: a non-empty string is required"),
             (all(isinstance(spec.get(k), int) and spec[k] > 0 for k in ("width", "height")),
              "width, height: positive integers (px) are required"),
             (is_num(spec.get("fps")) and spec["fps"] > 0, "fps: a positive number is required"),
             ("duration" not in spec or (is_num(spec["duration"]) and spec["duration"] > 0), "duration: must be > 0 s"),
             (isinstance(tracks, list) and tracks, "tracks: a non-empty list is required"),
             (cap is None or (isinstance(srt, str) and srt.startswith("/") and Path(srt).is_file()),
              f"captions.srt: an existing absolute .srt path is required (got {srt!r})")]
    rules += [(isinstance(m, dict) and is_num(m.get("at")) and m["at"] >= 0, f"markers[{i}]: 'at' (s >= 0) is required")
              for i, m in enumerate(spec.get("markers", []))]
    errs = [msg for ok, msg in rules if not ok]
    for ti, tr in enumerate(tracks if isinstance(tracks, list) else []):
        where = f"tracks[{ti}] {tr.get('name', '')!r}" if isinstance(tr, dict) else f"tracks[{ti}]"
        if not (isinstance(tr, dict) and tr.get("type") in ("video", "text", "audio")
                and isinstance(tr.get("clips"), list)):
            errs.append(f"{where}: want {{'type': video|text|audio, 'clips': [...]}}")
            continue
        for ci, c in enumerate(tr["clips"]):
            name = c.get("name") if isinstance(c, dict) else None
            errs += check_clip(c, tr["type"], f"{where} clip {ci + 1}" + (f" ({name})" if name else ""))
        timed = sorted((c["at"], c.get("dur"), i) for i, c in enumerate(tr["clips"])
                       if isinstance(c, dict) and is_num(c.get("at")))
        errs += [f"{where}: clip {a[2] + 1} overlaps clip {b[2] + 1} (a track holds one clip at a time)"
                 for a, b in zip(timed, timed[1:]) if b[0] == a[0] or (is_num(a[1]) and a[0] + a[1] > b[0] + 1e-6)]
    return errs


# ---------------------------------------------------------------- plan (spec + what the app reported)

class Plan:
    """Turns the spec into concrete layers (bottom -> top) for ec_build.js, collecting notes on the way."""

    def __init__(self, spec: dict, media: dict, families: list, fx_params: dict):
        self.spec, self.media, self.families, self.fx_params = spec, media, families, fx_params
        self.fps, self.w, self.h = spec["fps"], spec["width"], spec["height"]
        # adapters (tools/adapters) pass on what they could not express: top-level `unsupported` and `notes`
        passed = [u if isinstance(u, str) else f"{u.get('where', 'spec')}: {u.get('what')} — {u.get('why')}"
                  for u in spec.get("unsupported", [])]
        self.notes = {"unsupported": passed, "approximations": [], "warnings": [], "fonts": {},
                      "spec": spec.get("notes", [])}

    def note(self, kind: str, where: str, what: str, why: str) -> None:
        self.notes[kind].append(f"{where}: {what} — {why}")

    def anim(self, value, at: float, conv=lambda v: v, where: str = "value") -> dict:
        return animated(value, at, self.fps, conv, where, self.notes["approximations"])

    def make(self, cues: list) -> dict:
        visual, audio = [], []
        for ti, track in enumerate(self.spec["tracks"]):
            clips = sorted(track["clips"], key=lambda c: c["at"])
            nexts = [c["at"] for c in clips[1:]] + [None]
            rows = [self.clip_layer(c, track, ti % 16 + 1, nxt) for c, nxt in zip(clips, nexts)]
            if track["type"] != "audio":
                self.dissolve_handles(rows, clips)
            (audio if track["type"] == "audio" else visual).append(rows)
        label = len(self.spec["tracks"]) % 16 + 1
        caps = [self.caption_layer(i, cue, label) for i, cue in enumerate(cues)]
        layers = [L for rows in reversed(audio) for L in rows] + [L for rows in visual for L in rows] + caps
        duration = snap(self.spec.get("duration", max((L["out"] for L in layers), default=1.0)), self.fps)
        self.notes["warnings"] += [f"{L['name']}: ends at {L['out']:.2f}s, after the comp end ({duration}s)"
                                   for L in layers if L["out"] > duration + 1e-6]
        markers = [{"time": snap(m["at"], self.fps), "comment": m.get("name", "") + (
            f": {m['comment']}" if m.get("comment") else "")} for m in self.spec.get("markers", [])]
        comp = {"name": self.spec["name"], "width": self.w, "height": self.h, "fps": self.fps, "duration": duration}
        return {"comp": comp, "layers": layers, "markers": markers}

    def clip_layer(self, c: dict, track: dict, label: int, next_at=None) -> dict:
        tname = track.get("name", track["type"])
        where = f"{tname} / {c.get('name') or c.get('text') or Path(c['src']).name}".replace("\n", " ")
        fit = (lambda natural: self.fit(natural, c["at"], next_at, where)) if "dur" not in c else None
        L = self.text_layer(c, where, fit) if track["type"] == "text" else self.media_layer(c, track, where, fit)
        L.update(comment=tname, label=label, masks=[])
        L["props"] = self.transform(c, L, where) + L["props"]
        L["effects"] += self.effects(c, L, where)
        if c.get("blend", "normal") != "normal":
            L["blend"] = c["blend"]
        return L

    def fit(self, natural: float, at: float, next_at, where: str) -> float:
        """A clip without 'dur' runs its natural length, but never over the next clip on its track."""
        if next_at is None or natural <= next_at - at + 1e-6:
            return natural
        self.notes["warnings"].append(f"{where}: runs {natural:.2f}s but the next clip on its track starts "
                                      f"{next_at - at:.2f}s later; trimmed to {next_at - at:.2f}s")
        return next_at - at

    def media_layer(self, c: dict, track: dict, where: str, fit) -> dict:
        info, fps, speed = self.media[c["src"]], self.fps, c.get("speed", 100)
        stretch, src_in, at = 10000.0 / speed, snap(c.get("in", 0), fps), snap(c["at"], fps)
        if (track["type"] == "audio" and info["still"]) or (track["type"] == "video" and not info["hasVideo"]):
            raise SpecError(f"{where}: {c['src']} does not belong on a {track['type']} track")
        natural = STILL_SECONDS if info["still"] else (info["duration"] - src_in) * speed / 100
        out = snap(c["at"] + (fit(natural) if fit else c["dur"]), fps)      # the end point snaps on its own
        dur = out - at
        if not info["still"] and src_in + dur * speed / 100 > info["duration"] + 0.5 / fps:
            raise SpecError(f"{where}: needs {dur * speed / 100:.2f}s of source from {src_in}s, "
                            f"but the file is {info['duration']:.2f}s long")
        L = {"kind": "audio" if track["type"] == "audio" else "footage", "item": info["id"], "src": c["src"],
             "name": c.get("name") or Path(c["src"]).name, "stretch": stretch, "in": at, "out": out,
             "start": snap(at - src_in * stretch / 100, fps), "size": [info["width"], info["height"]],
             "has_audio": info["hasAudio"] and c.get("audio") is not False, "props": [], "effects": []}
        if L["kind"] == "audio" and info["hasVideo"]:
            L["video"] = False
        if c.get("audio") is False:
            L["audio"] = False
        if "gain_db" in c:
            L["props"].append({"path": "levels", **self.anim(c["gain_db"], at, as_scale, f"{where} gain_db")})
        return L

    def first(self, v, where: str, what: str):
        if is_keyed(v):
            self.note("unsupported", where, f"animated {what}", "a text layer keeps one value; the first key is used")
        return first_value(v)

    def text_layer(self, c: dict, where: str, fit) -> dict:
        at, family, style = snap(c["at"], self.fps), c.get("font", FALLBACK_FONT), c.get("style", "Regular")
        fam, sty, why = resolve_font(family, style, self.families)
        self.notes["fonts"][f"{family} {style}"] = {"used": f"{fam} {sty}", "fallback": why is not None, "why": why}
        text = {"str": c["text"].replace("\n", "\r"), "font": fam, "style": sty,
                "size": self.first(c.get("size", 100), where, "size"),
                "fill": rgb(self.first(c.get("color", "#FFFFFF"), where, "color")), "stroke": None,
                "align": c.get("align", "center"), "tracking": c.get("tracking", 0), "leading": c.get("leading", 0)}
        stroke = c.get("stroke") or {}
        if self.first(stroke.get("width", 0), where, "stroke width") > 0:
            # AE strokes are centred on the outline and drawn under the fill: double it to show `width` outside
            text["stroke"] = {"color": rgb(self.first(stroke.get("color", "#000000"), where, "stroke colour")),
                              "width": 2 * first_value(stroke["width"])}
        L = {"kind": "text", "text": text, "name": c.get("name") or c["text"].replace("\n", " ")[:60],
             "stretch": 100, "start": at, "in": at, "has_audio": False,
             "out": snap(c["at"] + (fit(STILL_SECONDS) if fit else c["dur"]), self.fps),
             "position": c.get("position", [self.w / 2, self.h / 2]), "props": [], "effects": []}
        sh = c.get("shadow")
        if sh:
            params = {"color": sh.get("color", "#000000"), "opacity": sh.get("opacity", 60),
                      "softness": sh.get("blur", 0), "distance": sh.get("distance", 0)}
            L["effects"].append(self.map_effect("drop_shadow", params, at, where))
        return L

    def caption_layer(self, i: int, cue: tuple, label: int) -> dict:
        """One text layer per cue: wrapped to the frame, its last line on the caption baseline."""
        start, end, body = cue
        style = {**CAPTION_STYLE, "position": [self.w / 2, self.h * CAPTION_Y],
                 **{k: v for k, v in self.spec["captions"].items() if k != "srt"}}
        size = first_value(style["size"])
        width = max(8, int(self.w * CAPTION_MAX_W / (CAPTION_CHAR_EM * size)))
        lines = [w for ln in body.split("\n") for w in textwrap.wrap(ln, width) or [""]]
        if is_xy(style["position"]):
            lead = style.get("leading") or 1.2 * size
            style["position"] = [style["position"][0], style["position"][1] - (len(lines) - 1) * lead]
        clip = {**style, "text": "\n".join(lines), "at": start, "dur": end - start,
                "name": f"CC {i + 1:02d} {' '.join(lines)}"[:60]}
        track = {"type": "text", "name": f"captions {Path(self.spec['captions']['srt']).name}"}
        L = self.clip_layer(clip, track, label)
        L["text"]["maxWidth"], L["caption"] = self.w * CAPTION_MAX_W, True
        return L

    def transform(self, c: dict, L: dict, where: str) -> list:
        motion, opacity = dict(c.get("motion") or {}), c.get("opacity")
        pos = L.pop("position", None)            # a text clip's own position
        if pos is not None:
            motion.setdefault("position", pos)
        props = [{"path": k, **self.anim(motion[k], L["in"], as_scale if k == "scale" else (lambda v: v),
                                         f"{where} motion.{k}")}
                 for k in ("anchor", "position", "scale", "rotation") if k in motion]
        fade = self.transition(c, opacity, L, where)
        if fade or opacity is not None:
            props.append(fade or {"path": "opacity", **self.anim(opacity, L["in"], where=f"{where} opacity")})
        return props

    def transition(self, c: dict, opacity, L: dict, where: str):
        sides = {s: c[s] for s in ("transition_in", "transition_out") if c.get(s)}
        for s, t in list(sides.items()):
            if t["effect"] not in TRANSITIONS:
                self.note("unsupported", where, f"{s} {t['effect']}", "only cross_dissolve maps (to opacity keys)")
                del sides[s]
        if sides and is_keyed(opacity):
            self.note("unsupported", where, "transition", "the clip animates its own opacity; transition skipped")
        if not sides or is_keyed(opacity):
            return None
        base, dur = 100 if opacity is None else opacity, L["out"] - L["in"]
        n = {s: t["frames"] / self.fps for s, t in sides.items()}
        if sum(n.values()) > dur + 1e-6:
            raise SpecError(f"{where}: transitions ({sum(n.values()):.2f}s) are longer than the clip ({dur:.2f}s)")
        keys = ([[0, 0], [n["transition_in"], base]] if "transition_in" in n else []) + (
            [[dur - n["transition_out"], base], [dur, 0]] if "transition_out" in n else [])
        if len(keys) == 4 and keys[1][0] >= keys[2][0]:
            del keys[2]
        L["fade_in"] = sides.get("transition_in", {}).get("frames", 0)
        return {"path": "opacity", "keys": to_keys(keys, L["in"], self.fps, where=f"{where} transition")}

    def dissolve_handles(self, rows: list, clips: list) -> None:
        """Cross dissolve: the clip before keeps playing under the fade-in; its sound still cuts at the cut."""
        for prev, cur, pclip in zip(rows, rows[1:], clips):
            n, cut = cur.get("fade_in", 0) / self.fps, prev["out"]
            if not n or abs(cut - cur["in"]) > 0.5 / self.fps or pclip.get("transition_out"):
                continue
            where, info = f"{prev['comment']} / {prev['name']}", self.media.get(prev.get("src"), {"still": True})
            needs = (cut + n - prev["start"]) * 100 / prev["stretch"]
            if not info["still"] and needs > info["duration"] + 0.5 / self.fps:
                self.note("approximations", where, "cross dissolve", "no source left; fades over the layers below")
                continue
            prev["out"] = snap(cut + n, self.fps)
            self.note("approximations", where, "cross dissolve",
                      f"out point extended {cur['fade_in']} frames under '{cur['name']}', which fades in over it")
            lv = next((p for p in prev["props"] if p["path"] == "levels"), {"path": "levels", "value": [0, 0]})
            if prev["has_audio"] and "keys" in lv:
                self.note("approximations", where, "cross dissolve sound", "gain is animated; the handle stays audible")
            elif prev["has_audio"]:
                last = snap(cut - 1 / self.fps, self.fps)
                lv["keys"] = [{"t": last, "v": lv.pop("value"), "in": "linear", "out": "hold"},
                              {"t": cut, "v": [SILENT_DB, SILENT_DB], "in": "linear", "out": "linear"}]
                prev["props"] = [p for p in prev["props"] if p["path"] != "levels"] + [lv]

    def effects(self, c: dict, L: dict, where: str) -> list:
        out = []
        for fx in c.get("effects", []):
            fid, params = fx["effect"], fx.get("params", {})
            if fid == "rounded_crop" and L["kind"] == "footage":
                out += self.rounded_crop(params, L, where)
            elif fid in EFFECTS:
                out.append(self.map_effect(fid, params, L["in"], where))
            else:
                why = "write it as the clip's motion / opacity" if fid in ("motion", "opacity") else \
                    "no EffectCraft mapping (references/effect-map.md)"
                self.note("unsupported", where, f"effect {fid}", why)
        return out

    def map_effect(self, fid: str, params: dict, at: float, where: str) -> dict:
        ec_id, pmap = EFFECTS[fid]
        out = []
        for name, v in params.items():
            if name in SWITCHES.get(fid, ()):
                if v is False:
                    self.note("unsupported", where, f"{fid}.{name}=false", "EffectCraft has no section switch; applied")
            elif name not in pmap:
                self.note("unsupported", where, f"{fid}.{name}", "parameter has no EffectCraft equivalent")
            else:
                out.append(self.fx_param(ec_id, pmap[name], v, at, f"{where} {fid}.{name}"))
        return {"ec": ec_id, "fc": fid, "params": out}

    def fx_param(self, ec_id: str, pid: str, value, at: float, where: str) -> dict:
        index, p = self.fx_params[ec_id][pid]
        conv = {"color": rgba, "enum": lambda v: v + 1, "bool": lambda v: 1 if v else 0}.get(p["type"], lambda v: v)
        return {"index": index, "name": p["name"], **self.anim(value, at, conv, where)}

    def rounded_crop(self, params: dict, L: dict, where: str) -> list:
        p = {k: self.first(v, where, f"rounded_crop.{k}") for k, v in params.items()}
        for k in sorted(set(p) - CROP_PARAMS):
            self.note("unsupported", where, f"rounded_crop.{k}", "parameter has no EffectCraft equivalent")
        (w, h), border = L["size"], p.get("border", 0)
        x0, x1 = w * p.get("left", 0) / 100, w * (1 - p.get("right", 0) / 100)
        y0, y1 = h * p.get("top", 0) / 100, h * (1 - p.get("bottom", 0) / 100)
        r = max(0, min(p.get("radius", 0), (x1 - x0) / 2, (y1 - y0) / 2))
        L["masks"].append({"name": "rounded_crop", **rounded_rect(x0, y0, x1, y1, r)})
        self.note("approximations", where, "rounded_crop", "rounded-rectangle mask, crop in % of the source size"
                  + ("; border = Stroke effect on the mask" if border > 0 else ""))
        values = dict(zip(STROKE_PARAMS, (len(L["masks"]), p.get("border_color", "#FFFFFF"), border)))
        return [{"ec": STROKE_FX, "fc": "rounded_crop", "params": [
            self.fx_param(STROKE_FX, k, v, L["in"], where) for k, v in values.items()]}] if border > 0 else []


# ---------------------------------------------------------------- verification (plan vs. the re-opened project)

def plan_sig(L: dict, fps: float) -> dict:
    """What the plan promises for one layer, in the shape ec_build.js `dump` reads back (times in frames)."""
    gain = next((q["value"][0] for q in L["props"] if q["path"] == "levels" and "value" in q), 0.0)
    keyed_gain = any(q["path"] == "levels" and "keys" in q for q in L["props"])
    return {"name": L["name"], "kind": L["kind"], "caption": bool(L.get("caption")),
            **{k: frame(L[k], fps) for k in ("in", "out", "start")},
            "keys": {q["path"]: [frame(k["t"], fps) for k in q["keys"]] for q in L["props"] if "keys" in q},
            "effect_keys": [sum(len(q.get("keys", [])) for q in fx["params"]) for fx in L["effects"]],
            "masks": len(L["masks"]), "src": L.get("src"), "sound": L["has_audio"],
            "text": [L["text"][k] for k in ("str", "font", "style")] if L["kind"] == "text" else None,
            "gain": round(gain, 2) if L["has_audio"] and not keyed_gain else None}


def counts(sigs: list, markers: list) -> dict:
    return {"layers": len(sigs), **{k: sum(s["kind"] == k for s in sigs) for k in ("footage", "text", "audio")},
            "captions": sum(s["caption"] for s in sigs),
            "keyframes": sum(len(v) for s in sigs for v in s["keys"].values())
            + sum(sum(s["effect_keys"]) for s in sigs),
            "effects": sum(len(s["effect_keys"]) for s in sigs), "masks": sum(s["masks"] for s in sigs),
            "markers": len(markers)}


def compare(plan: dict, dump: dict) -> tuple:
    """(mismatch messages, expected counts, found counts)."""
    c, f = plan["comp"], dump["comp"]
    fps = c["fps"]
    bad = [f"comp {k}: {f[k]!r}, expected {c[k]!r}" for k in ("name", "width", "height") if f[k] != c[k]]
    if abs(f["fps"] - fps) > 1e-3 or frame(f["duration"], fps) != frame(c["duration"], fps):
        bad.append(f"comp: {f['fps']} fps / {f['duration']}s, expected {fps} fps / {c['duration']}s")
    if dump["comps"] != 1:
        bad.append(f"the project has {dump['comps']} compositions, expected 1")
    want, got = [plan_sig(L, fps) for L in plan["layers"]], dump["layers"][::-1]   # the comp lists the top first
    j = 0                                 # match in stacking order (bottom -> top) by name and kind
    for a in want:
        k = next((k for k in range(j, len(got)) if (got[k]["name"], got[k]["kind"]) == (a["name"], a["kind"])), None)
        if k is None:
            bad.append(f"layer '{a['name']}' ({a['kind']}) is missing or out of stacking order")
            continue
        bad += [f"unexpected layer '{g['name']}'" for g in got[j:k]]
        bad += [f"layer '{a['name']}': {key} {got[k][key]!r}, expected {v!r}"
                for key, v in a.items() if v != got[k][key]]
        j = k + 1
    bad += [f"unexpected layer '{g['name']}'" for g in got[j:]]
    mk = [[(frame(m["time"], fps), m["comment"]) for m in sorted(ms, key=lambda m: m["time"])]
          for ms in (plan["markers"], dump["markers"])]
    if mk[0] != mk[1]:
        bad.append(f"markers (frame, comment) {mk[1]}, expected {mk[0]}")
    expected, found = counts(want, plan["markers"]), counts(got, dump["markers"])
    return bad + ([f"counts {found}, expected {expected}"] if expected != found else []), expected, found


# ---------------------------------------------------------------- driving the app

def run_js(app: Craft, mode: str, args: dict):
    code = (f"var MODE = {json.dumps(mode)};\nvar ARGS = {json.dumps(args, ensure_ascii=False)};\n"
            + JS_FILE.read_text(encoding="utf-8"))
    res = app.cmd("script.run", {"code": code, "name": f"ec_build {mode}"})
    if not res or not res.get("ok"):
        err = (res or {}).get("error") or {}
        raise CraftError(f"EffectCraft script '{mode}' failed: {err.get('message')} (line {err.get('line')})")
    return json.loads(res["result"])


def load_spec(path: str) -> tuple:
    try:
        spec = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as e:
        raise SpecError(f"cannot read {path}: {e}") from e
    except json.JSONDecodeError as e:
        raise SpecError(f"{path}: invalid JSON at line {e.lineno} column {e.colno}: {e.msg}") from e
    errs = validate(spec)
    if errs:
        raise SpecError("invalid spec:\n  " + "\n  ".join(errs))
    cues = parse_srt(Path(spec["captions"]["srt"]).read_text(encoding="utf-8")) if spec.get("captions") else []
    return spec, cues


def build_project(spec: dict, cues: list, out: Path, workdir: Path) -> tuple:
    media = sorted({c["src"] for t in spec["tracks"] if t["type"] != "text" for c in t["clips"]})
    with Craft("effectcraft", workdir / "build") as app:
        probe = run_js(app, "probe", {"media": media})
        fx = index_effects(app.cmd("effect.list"))
        needed = [(ec, p) for ec, pm in EFFECTS.values() for p in pm.values()] + [(STROKE_FX, p) for p in STROKE_PARAMS]
        stale = [f"{ec}/{p}" for ec, p in needed if p not in fx.get(ec, {})]
        if stale:
            raise CraftError(f"the effect map does not match this EffectCraft (missing {stale}); see effect-map.md")
        planner = Plan(spec, probe, app.cmd("text.fonts")["families"], fx)
        plan = planner.make(cues)
        planner.notes["warnings"] += run_js(app, "build", plan)["notes"]
        app.cmd("file.saveAs", {"path": str(out)})
    return plan, planner.notes


def verify_project(plan: dict, out: Path, workdir: Path, frames: int, still_dir: Path) -> tuple:
    """Re-open the saved project in a fresh instance (fresh config), read it back, optionally save stills."""
    c, stills = plan["comp"], []
    with Craft("effectcraft", workdir / "verify") as app:
        app.cmd("file.open", {"path": str(out)})
        dump = run_js(app, "dump", {"comp": c["name"]})
        if frames > 0:
            app.cmd("comp.open", {"comp": c["name"]})
        for i in range(max(frames, 0)):
            t = snap(c["duration"] * (i + 0.5) / frames, c["fps"])
            stills.append(str(still_dir / f"{out.stem}_qa{i + 1:02d}_{t:06.2f}s.png"))
            app.cmd("comp.saveFrameAs", {"path": stills[-1], "time": t, "scale": QA_SCALE})
    return dump, stills


def make_report(spec_path: str, out: Path, plan: dict, notes: dict, dump: dict, stills: list) -> dict:
    mismatches, expected, found = compare(plan, dump)
    fps = dump["comp"]["fps"]
    return {"ok": not mismatches, "spec": str(Path(spec_path).resolve()), "project": str(out), "comp": dump["comp"],
            "counts": {"expected": expected, "found": found}, "mismatches": mismatches,
            "unsupported": notes["unsupported"], "notes": notes["spec"], "approximations": notes["approximations"],
            "warnings": notes["warnings"], "fonts": [{"requested": k, **v} for k, v in notes["fonts"].items()],
            "qa_frames": stills,
            "layers": [{"index": d["index"], "name": d["name"], "kind": d["kind"], "in": round(d["in"] / fps, 3),
                        "out": round(d["out"] / fps, 3), "keys": {k: len(v) for k, v in d["keys"].items()},
                        "effects": d["effects"], "masks": d["masks"]} for d in dump["layers"]]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build an EffectCraft .ecproj from a craft timeline spec.")
    ap.add_argument("spec", help="timeline spec (*.craft.json)")
    ap.add_argument("out", help="project to write (.ecproj)")
    ap.add_argument("--report", help="write the verification report (JSON) here")
    ap.add_argument("--frames", type=int, default=0, help="save N QA stills of the re-opened project")
    ap.add_argument("--workdir", help="app config + logs (default: a temp dir, removed after a clean run)")
    a = ap.parse_args(argv)
    out = Path(a.out).resolve()
    if out.suffix != ".ecproj":
        ap.error("OUT must end in .ecproj")
    report_path = Path(a.report).resolve() if a.report else None
    workdir = Path(a.workdir).resolve() if a.workdir else Path(tempfile.mkdtemp(prefix="ec_build_"))
    try:
        spec, cues = load_spec(a.spec)
        still_dir = (report_path or out).parent
        for d in (out.parent, still_dir):
            d.mkdir(parents=True, exist_ok=True)
        plan, notes = build_project(spec, cues, out, workdir)
        dump, stills = verify_project(plan, out, workdir, a.frames, still_dir)
    except (SpecError, CraftError) as e:
        print(f"ec_build: {e}" + (f"\n  app logs: {workdir}" if isinstance(e, CraftError) else ""), file=sys.stderr)
        return 2
    report = make_report(a.spec, out, plan, notes, dump, stills)
    if report_path:
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"ec_build: {'verified' if report['ok'] else 'MISMATCH'} {out}\n  found {report['counts']['found']}")
    for line in report["mismatches"] + [f"unsupported: {u}" for u in notes["unsupported"]]:
        print(f"  {line}")
    if not a.workdir and report["ok"]:
        shutil.rmtree(workdir, ignore_errors=True)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
