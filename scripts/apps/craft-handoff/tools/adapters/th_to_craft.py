#!/usr/bin/env python3
"""th_to_craft — a built dung-video-talking-head project (release 1.2.6) -> Craft timeline spec.

    python3 th_to_craft.py PROJECT_DIR OUT.craft.json [--srt OUT.srt]

PROJECT_DIR is VID_ROOT/<n>/edit-r<ver> once BUILD has passed its stem_bed gate: picture_lock.json,
out/sfx_plan.json, rules.lock, public/{master.mp4, vo-clean.wav, sfx_stem.wav}, public/<broll files> and,
when a song was selected, public/bgm_bed.wav. picture_lock.json is the source of truth — the resolved
timings the Remotion template draws (edit.json shots/blocks after SFX snapping, B-roll guards and the
face_safe refit). Geometry, fonts and colours follow template/src of release 1.2.6 (th_text.py); what the
spec cannot express is listed under "unsupported". Stdlib only; ffprobe must be on PATH.
TH_SKILL_ROOT overrides where the skill repo lives. Exit 2 = the project is incomplete (message says why).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # th_text sits next to this file (also under python -I)
import th_text as T  # noqa: E402
from th_text import AdapterError, key, mono, need, rnd  # noqa: E402

SKILL_ROOT = Path(os.environ.get("TH_SKILL_ROOT", "/home/vmiz/.hermes/shared-skills/video/dung-video-talking-head"))
TEMPLATE_RELEASE = "1.2.6"            # th_text mirrors this release's template/src …
SAME_TEMPLATE = ("1.2.5", "1.2.6")    # … which is byte-identical in these releases
W, H, SR = T.W, T.H, 48000
ORIGIN_Y = 0.32 * H                   # Footage.tsx transformOrigin "50% 32%"
KICK, KICK_F = 0.018, 5               # Footage.tsx: +1.8 % scale decaying over the first 5 frames of a cut
FADE_IN_AT = (0.1, 0.3, 0.6)          # SFX fade-in is linear in amplitude: drawn as dB keys at these fractions
GRADE_WHAT = "Grade overlay: vignette, bottom/top dark scrims, 4.5 % film grain"


def _read(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise AdapterError(f"missing {path}") from None
    except json.JSONDecodeError as exc:
        raise AdapterError(f"{path} is not valid JSON: {exc}") from None


def _probe(path: Path) -> dict:
    """{'w', 'h', 'dur' (None for stills)} of a picture or video, via ffprobe."""
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
           "stream=width,height:format=duration", "-of", "json", str(path)]
    try:
        info = json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)
    except FileNotFoundError:
        raise AdapterError("ffprobe not found on PATH (needed to read media sizes)") from None
    except subprocess.CalledProcessError as exc:
        raise AdapterError(f"ffprobe cannot read {path}: {exc.stderr.strip()}") from None
    st = (info.get("streams") or [{}])[0]
    if "width" not in st:
        raise AdapterError(f"no picture stream in {path}")
    dur = info.get("format", {}).get("duration")
    return {"w": st["width"], "h": st["height"], "dur": None if dur in (None, "N/A") else float(dur)}


def _cover(m: dict) -> float:
    """objectFit: cover — frame pixels per source pixel."""
    return max(W / m["w"], H / m["h"])


def _inout(p: float) -> float:        # anim.ts EASE.inOut
    return 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2


# ------------------------------------------------------------------ picture

def _shot_pose(shot: dict, t: float, dur: float, kick: float) -> tuple[float, list]:
    """Footage.tsx `t` s into a shot: (scale incl. cut bump, frame position of the master's centre).
    translate(x%, y%) scale(s) around (540, ORIGIN_Y) == a centre-anchored clip at this position."""
    s = shot["s0"] + (shot["s1"] - shot["s0"]) * _inout(min(1.0, t / dur))
    slack = (s - 1) / 2
    tx, ty = (max(-slack, min(slack, shot.get(a, 0.0))) for a in ("x", "y"))
    st = s + kick
    return st, [rnd(W / 2 + tx * W, 1), rnd(ORIGIN_Y + ty * H + st * (H / 2 - ORIGIN_Y), 1)]


def _aroll(lock: dict, master: str, k: float, end_s: float) -> list:
    """One master clip per shot, source time = timeline time, starting on the first frame Footage.tsx draws
    it (frame / fps >= shot.t — the lock's 4-decimal rounding can land a cut one frame after its SFX peak,
    exactly as in the render)."""
    fps, shots = lock["fps"], lock["shots"]
    edges = [rnd(math.ceil(s["t"] * fps - 1e-6) / fps) for s in shots] + [rnd(end_s)]
    clips = []
    for i, sh in enumerate(shots):
        dur = rnd(edges[i + 1] - edges[i])
        steps = [(0.0, KICK if i else 0.0, None)] + ([(KICK_F / fps, 0.0, None)] if i and dur > KICK_F / fps else [])
        poses = [(t, *_shot_pose(sh, t, dur, kick), e) for t, kick, e in steps + [(dur, 0.0, "bezier")]]
        clips.append({"src": master, "name": f"Shot {i + 1} ({sh['s0']}->{sh['s1']})", "at": rnd(edges[i]),
                      "in": rnd(edges[i]), "dur": rnd(dur), "audio": False,
                      "motion": {"scale": [key(t, rnd(100 * k * s, 3), e) for t, s, _, e in poses],
                                 "position": [key(t, p, e) for t, _, p, e in poses]}})
    return clips


def _broll(lock: dict, pub: Path, unsupported: list) -> list:
    """Broll.tsx: full-frame cutaways. Stills push push[0] -> push[1] (inOut) plus a settle bump; clips
    play from their start, muted, unscaled beyond cover-fit."""
    fps, clips = lock["fps"], []
    for b in lock.get("broll") or []:
        src = need(pub / b["file"], f"B-roll {b['id']}")
        info = _probe(src)
        k, n = _cover(info), b["f_out"] - b["f_in"]
        clip = {"src": str(src), "name": f"{b['id']} {b['media']}", "at": rnd(b["f_in"] / fps), "dur": rnd(n / fps),
                "motion": {"position": [W / 2, H / 2]}}
        if b["media"] == "clip":
            clip.update({"in": 0.0, "audio": False})
            clip["motion"]["scale"] = rnd(100 * k, 3)
            if info["dur"] is not None and info["dur"] + 1e-3 < n / fps:
                unsupported.append({"what": f"B-roll {b['id']}: source {info['dur']:.2f} s is shorter than its "
                                            f"{n / fps:.2f} s slot", "why": "the clip ends early here",
                                    "where": f"{clip['at']} s"})
        else:
            (p0, p1), last, sf = b["push"], max(n - 1, 1), b["settle_f"]

            def sc(f, bump=0.0):
                return rnd(100 * k * (p0 + (p1 - p0) * _inout(min(1.0, f / last)) + bump), 3)
            keys = [key(0, sc(0, b["settle_amp"]))] + ([key(sf / fps, sc(sf))] if 0 < sf < last else [])
            clip["motion"]["scale"] = keys + [key(last / fps, sc(last), "bezier")]
        clips.append(clip)
    return clips


# ------------------------------------------------------------------ sound

def _sfx(plan: dict, rel: Path, R: dict) -> list:
    """One clip per planner cue: the release's prepared WAV, in-point = lag - (peak - start), the planner's
    gain, and its fades (linear in when the pre-roll was cut, dB-linear out when the tail was cut) as gain
    keys. Times are the plan's (rounded to 0.1 ms, i.e. within 2 samples of the stem the skill mixed)."""
    manifest = _read(rel / "sfx_manifest.json")["files"]
    fin, fout = R["sfx"]["fade_in_s"], R["sfx"]["fade_out_s"]
    clips = []
    for c in plan.get("cues", []):
        meta = manifest.get(c["file"])
        if meta is None:
            raise AdapterError(f"SFX cue {c['id']}: {c['file']} is not in {rel / 'sfx_manifest.json'}")
        src = need(rel / meta["path"], f"SFX file of cue {c['id']}")
        with wave.open(str(src)) as wf:
            rate, n_file = wf.getframerate(), wf.getnframes()
        lag = round(meta["lag_ms"] / 1000 * SR)
        a = max(0, lag - round((c["peak_s"] - c["start_s"]) * SR))
        b = lag + round((c["end_s"] - c["peak_s"]) * SR)
        dur, g, fam = c["end_s"] - c["start_s"], rnd(c["gain_db"], 2), c["file"].split("/")[0]
        fi = min(fin.get(fam, 0), dur)
        keys = [key(0, g - 60)] + [key(f * fi, rnd(g + 20 * math.log10(f), 2)) for f in FADE_IN_AT] + [key(fi, g)] \
            if a > 0 and fi > 0 else []
        if c["peak_s"] + meta["tail30_ms"] / 1000 > c["end_s"] - 1e-6 or b < n_file:
            fo = min(fout.get(fam, fout["default"]), max(0.02, c["end_s"] - c["peak_s"]))
            keys += [key(dur - fo, g), key(dur, g - 60)]
        clips.append({"src": str(src), "name": f"{c['role']} {c['id']} ({c['file']})", "at": rnd(c["start_s"]),
                      "in": rnd(a / rate), "dur": rnd(dur), "gain_db": mono(keys) if keys else g})
    return clips


def _bgm_source(rel: Path, video: int | None) -> str | None:
    """Song the bed was rendered from — thlib.mix.select_bgm: selected[video mod N] by `order`."""
    path = rel / "bgm_manifest.json"
    if video is None or not path.is_file():
        return None
    tracks = _read(path)["tracks"]
    chosen = sorted((t["order"], k) for k, t in tracks.items() if t.get("selected") and t.get("content_id_risk") == "none")
    return str((rel / tracks[chosen[video % len(chosen)][1]]["path"]).resolve()) if chosen else None


# ------------------------------------------------------------------ captions, notes, unsupported

def _ts(t: float) -> str:
    ms = round(t * 1000)
    return "%02d:%02d:%02d,%03d" % (ms // 3_600_000, ms // 60_000 % 60, ms // 1000 % 60, ms % 1000)


def _srt(lock: dict, end_s: float) -> str:
    """One cue per subtitle block: first word shown -> block gone (out + exit), never overlapping the next."""
    fps, cues = lock["fps"], []
    for b in lock["blocks"]:
        start = max(0.0, min(w["show"] for w in b["top"] + b["hero"] + b["bottom"]))
        cues.append([start, min(b["out"] + b["exit_f"] / fps, end_s), T.srt_text(b)])
    for cur, nxt in zip(cues, cues[1:]):
        cur[1] = min(cur[1], nxt[0])
    return "".join(f"{i}\n{_ts(s)} --> {_ts(e)}\n{t}\n\n" for i, (s, e, t) in enumerate(cues, 1))


def _unsupported(lock: dict, cut_times: list, ver: str, R: dict) -> list:
    blocks, L = lock["blocks"], R["loudness"]
    ids = lambda pred: ", ".join(b["id"] for b in blocks if pred(b)) or "none"   # noqa: E731
    caps = [f"{b['id']} {w['t']}" for b in blocks if b["style"] == "script" for w in b["hero"] if T.is_caps(w["t"])]
    out = [
        {"what": GRADE_WHAT, "why": "CSS gradients + animated SVG noise (Grade.tsx), no clip/effect for it in the spec; "
                                "render Grade alone as an alpha .mov to add it back", "where": "whole video, above A/B-roll"},
        {"what": "A-roll look: CSS saturate(1.06) contrast(1.06)", "why": "Lumetri parameter names are not part "
                 "of the spec contract", "where": "every A-roll clip"},
        {"what": "Cut flash: 5 px blur over 3 frames + brightness x1.036 at each cut (the 5-frame scale bump IS kept)",
         "why": "3-frame CSS filter flash", "where": "cuts at " + ", ".join(f"{t:.2f}" for t in cut_times) + " s"},
        {"what": "Per-word reveal (opacity + 24/40 px rise + 8/12 px blur over 9 frames from each word's show) and the "
                 "block exit lift/blur", "why": "a text clip animates as one unit: each line fades in at its first "
                 "word, fades out at the block exit", "where": "every subtitle line"},
        {"what": "Script hero gradient #fbf9ff -> #d7ccff -> #b3a4ff sliced per word", "why": "one fill colour per text "
                 "clip (#d7ccff used)", "where": "blocks " + ids(lambda b: b["style"] == "script")},
        {"what": "Hero glow (22 px blurred coloured copy of each word); hook glow (52 px)", "why": "no glow in spec "
                 "text clips (the drop shadow is kept)", "where": "every hero line; hook"},
        {"what": "Accent word colour #5ec8ff", "why": "per-word colour", "where": ids(lambda b: b["accent"] is not None)},
        {"what": "Caps words of a script hero drawn in DT Phudu Black", "why": "one font per text clip",
         "where": ", ".join(caps) or "none"},
        {"what": f"Master bus: 2-pass linear loudnorm to {L['final_lufs']} LUFS with a {L['tp_dbtp']} dBTP true-peak "
                 f"limiter, {R['end']['fade_s']} s fade on the whole mix", "why": "bus processing, not a clip property; "
                 "use export loudnessLufs; the end fade is approximated on the voice clip", "where": "whole mix"}]
    if lock.get("cta"):
        out.append({"what": "CTA pill: translucent gold fill, 2 px gold border, 16 px backdrop blur, shadow, and a "
                            "continuous ±1.5 % pulse", "why": "no shape/background or looping animation in the spec; "
                            "only the two texts are clips", "where": f"{lock['cta']['show']} s to the end"})
    if lock.get("steps"):
        out.append({"what": "Step card panel (dark translucent fill, border, 22 px backdrop blur, shadow), its 0.97->1 "
                            "scale and blur; item numbers in PS Bebas Neue (gold when active)", "why": "no shape in "
                            "the spec; number and label share one text clip",
                    "where": f"{lock['steps']['in']}-{lock['steps']['out']} s"})
    if ver not in SAME_TEMPLATE:
        out.append({"what": f"Text styling of release {ver}", "why": f"fonts/sizes/positions follow the "
                            f"{TEMPLATE_RELEASE} template; this project was built with {ver}", "where": "all text clips"})
    return [u for u in out if u["where"] != "none"]       # drop features this video does not use


def _notes(project: Path, ver: str, mi: dict, k: float, bgm: str | bool | None, L: dict) -> list:
    """`bgm`: source song path (None = unknown), or False when the project has no bed."""
    fonts = sorted(p.name for p in (project / "public" / "fonts").glob("*.[ot]tf"))
    return [
        f"Converted from {project} (release {ver}): times from picture_lock.json, SFX from out/sfx_plan.json.",
        f"motion.scale is % of the clip's own pixels: the {mi['w']}x{mi['h']} master fills the frame at "
        f"{100 * k:.3f} % (shot zoom s -> {100 * k:.3f} * s); positions are frame px, anchors default to the clip "
        "centre unless given. Keyframe easing follows the spec (key-side: easeIn = slow arrival into the key, easeOut = slow departure).",
        "A-roll: the skill never removes footage — each 'cut' is a change of framing on the same master, so every "
        "shot clip has in == at. Its audio is off: A1 is the cleaned voice public/vo-clean.wav.",
        "Captions: captions.srt has one cue per subtitle block (top / hero / bottom lines). The same words are also "
        "text clips on Sub top / Hero / Sub bottom, because the template stacks three differently styled lines "
        "that one caption track cannot reproduce — keep the caption track hidden (and burnCaptions off) or the "
        "text shows twice.",
        "Per-word caption styling was simplified: see 'unsupported' (word-by-word reveal, gradient, glow, accent).",
        "Text sizes and positions are recomputed from the template CSS (fitSize/wordCap, one-row hero rule with "
        "the template glyph tables, bottom-anchored stack); allow a few px of drift. Lines that wrap are split "
        "with \\n at the estimated wrap points and use the app's row spacing. Tracking is 1/1000 em.",
        f"Fonts: Be Vietnam Pro Medium, TF Youth Shandey, DT Phudu Bold/Black, PS Bebas Neue — install from "
        f"{project / 'public' / 'fonts'} ({', '.join(fonts) or 'folder missing'}).",
        "SFX use the release's prepared WAVs with the planner's in-point, gain and fades (gain keys, -60 dB = silent).",
        (f"BGM is the rendered bed public/bgm_bed.wav (looped, HPF, EQ dip, fades and level vs voice baked in); "
         f"source song: {bgm or 'unknown'}." if bgm is not False else
         "No BGM: the skill had no song selected for this video (public/bgm_bed.wav absent)."),
        f"Clip gains are pre-normalisation; export with loudness {L['final_lufs']} LUFS / {L['tp_dbtp']} dBTP.",
    ]


# ------------------------------------------------------------------ assembly

def _lanes(kind: str, name: str, clips: list) -> list:
    """Tracks for `clips`: overlapping clips go to extra lanes "<name> 2", "<name> 3"…; no clips, no track."""
    lanes = []
    for c in sorted(clips, key=lambda c: c["at"]):
        lane = next((ln for ln in lanes if ln[-1]["at"] + ln[-1]["dur"] <= c["at"] + 1e-3), None)   # < 1 frame
        lanes.append([c]) if lane is None else lane.append(c)
    return [{"type": kind, "name": name if i == 0 else f"{name} {i + 1}", "clips": ln} for i, ln in enumerate(lanes)]


# The curve builders tag a key with the easing of the segment that ENDS at it (CSS style). The spec puts
# easing on the key's own sides (Premiere / After Effects): easeIn = slow arrival into the key,
# easeOut = slow departure from it, bezier = both.
_SEG_SIDES = {"easeOut": ("in",), "easeIn": ("out",), "bezier": ("out", "in")}
_SIDE_TAG = {frozenset({"in"}): "easeIn", frozenset({"out"}): "easeOut", frozenset({"in", "out"}): "bezier"}


def _is_keys(v) -> bool:
    return (isinstance(v, list) and bool(v)
            and all(isinstance(k, list) and len(k) in (2, 3) and isinstance(k[0], (int, float)) for k in v))


def _segment_to_sides(keys: list) -> list:
    sides = [set() for _ in keys]
    for i, k in enumerate(keys):
        for side in _SEG_SIDES.get(k[2] if len(k) == 3 else "", ()):
            j = i if side == "in" else i - 1
            if j >= 0:
                sides[j].add(side)
    return [k[:2] + ([_SIDE_TAG[frozenset(s)]] if s else []) for k, s in zip(keys, sides)]


def _key_sides(obj):
    """Every keyframe list under `obj`, converted from segment easing to the spec's key-side easing."""
    if isinstance(obj, dict):
        return {k: _key_sides(v) for k, v in obj.items()}
    if _is_keys(obj):
        return _segment_to_sides(obj)
    if isinstance(obj, list):
        return [_key_sides(v) for v in obj]
    return obj


def default_srt(out: Path) -> Path:
    return out.with_name(out.name.removesuffix(".craft.json").removesuffix(".json") + ".srt")


def convert(project: Path, out: Path, srt: Path | None = None, captions: bool = False) -> dict:
    """Write the spec to `out` and the captions to `srt` (default: next to `out`); return the spec."""
    project, out = project.resolve(), out.resolve()
    srt = (srt or default_srt(out)).resolve()
    ver = _read(project / "rules.lock")["version"]
    rel = SKILL_ROOT / "releases" / ver
    if not rel.is_dir():
        raise AdapterError(f"release {ver} (rules.lock) not found under {SKILL_ROOT / 'releases'}")
    R, lock, plan = _read(rel / "rules.json")["params"], _read(project / "picture_lock.json"), _read(project / "out" / "sfx_plan.json")
    pub = project / "public"
    need(pub / "sfx_stem.wav", "public/sfx_stem.wav (BUILD has not passed its stem_bed gate)")
    master, vo = need(pub / "master.mp4", "master footage"), need(pub / "vo-clean.wav", "clean voice")
    fps, end_s = lock["fps"], lock["duration_f"] / lock["fps"]
    mi = _probe(master)
    if mi["dur"] is not None and mi["dur"] + 1 / fps < end_s:
        raise AdapterError(f"{master} is {mi['dur']:.2f} s but the picture lock needs {end_s:.2f} s")
    k, unsupported = _cover(mi), []
    meta = _read(project / "meta.json") if (project / "meta.json").is_file() else {}
    bed = pub / "bgm_bed.wav"
    ink = T.ink_tables(SKILL_ROOT, TEMPLATE_RELEASE)
    aroll = _aroll(lock, str(master), k, end_s)
    subs = T.subtitles(lock, ink, end_s)
    visual = [("video", "A-roll", aroll), ("video", "B-roll", _broll(lock, pub, unsupported)),
              ("text", "Steps", T.steps(lock["steps"], lock) if lock.get("steps") else []),
              ("text", "Sub top", subs["top"]), ("text", "Hero", subs["hero"]), ("text", "Sub bottom", subs["bottom"]),
              ("text", "Hook", [T.hook(lock["hook"], lock["safe"])] if lock.get("hook") else [])]
    cta = T.cta(lock["cta"], lock, end_s) if lock.get("cta") else []
    fade = R["end"]["fade_s"]
    audio = [("audio", "Voice", [{"src": str(vo), "name": "Voice (vo-clean)", "at": 0.0, "in": 0.0, "dur": rnd(end_s),
                                  "gain_db": [key(end_s - fade, 0), key(end_s, -60)]}]),
             ("audio", "SFX", _sfx(plan, rel, R)),
             ("audio", "BGM", [{"src": str(bed.resolve()), "name": "BGM bed", "at": 0.0, "in": 0.0, "dur": rnd(end_s),
                                "gain_db": 0}] if bed.is_file() else [])]
    tracks = [t for kind, name, clips in visual + [("text", "CTA label", cta[:1]), ("text", "CTA keyword", cta[1:])]
              + audio for t in _lanes(kind, name, clips)]
    bgm = _bgm_source(rel, meta.get("video")) if bed.is_file() else False
    spec = {"name": f"Talking head {meta.get('video', project.parent.name)} (r{ver})", "width": W, "height": H,
            "fps": fps, "sample_rate": SR, "duration": rnd(end_s), "tracks": _key_sides(tracks),
            **({"captions": {"srt": str(srt)}} if captions else {}),
            "notes": _notes(project, ver, mi, k, bgm, R["loudness"])
            + ([] if captions else [f"Phụ đề SRT ở {srt} không gắn vào timeline: chữ đã là text clip theo style "
                                   "của skill; gắn thêm thì chữ hiện hai lần (--captions để gắn)."]),
            "unsupported": unsupported + _unsupported(lock, [c["at"] for c in aroll[1:]], ver, R)}
    out.parent.mkdir(parents=True, exist_ok=True)
    srt.parent.mkdir(parents=True, exist_ok=True)
    srt.write_text(_srt(lock, end_s), encoding="utf-8")
    out.write_text(json.dumps(spec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return spec


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("project", type=Path, help="built project dir (VID_ROOT/<n>/edit-r<ver>)")
    ap.add_argument("out", type=Path, help="spec to write (*.craft.json)")
    ap.add_argument("--srt", type=Path, help="captions to write (default: next to OUT)")
    ap.add_argument("--captions", action="store_true",
                    help="also put the SRT on a caption track (the words are already text clips)")
    args = ap.parse_args(argv)
    try:
        spec = convert(args.project, args.out, args.srt, args.captions)
    except AdapterError as exc:
        print(f"th_to_craft: error: {exc}", file=sys.stderr)
        return 2
    n = {t["name"]: len(t["clips"]) for t in spec["tracks"]}
    print(f"wrote {args.out} — {len(spec['tracks'])} tracks {n}, {len(spec['unsupported'])} unsupported; "
          f"SRT {(args.srt or default_srt(args.out)).resolve()}"
          f"{' (on a caption track)' if 'captions' in spec else ' (not on the timeline)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
