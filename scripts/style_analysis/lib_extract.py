#!/usr/bin/env python3
"""lib_extract — dựng THƯ VIỆN HIỆU ỨNG từ video mẫu (định dạng: xem references/kb-effect-library.md).

    lib_extract.py segments <video> --out D [--transcript F.json] [--crop X,Y,W,H] [--threshold 10]
        bóc lời (hoặc dùng transcript sẵn) + dò điểm cắt (ffmpeg scdet) → D/segments.json + D/segments.md (đoạn đề xuất).
    lib_extract.py entry <video> --id V01-A03 --t S E --kind K --title "…" --root R --style S [--principle N]
                         [--crop X,Y,W,H] [--still-at S] [--notes TEXT|--notes-file F] [--rebuild TEXT] [--url U] [--author A]
        ghi R/S/<id>/{still.png, strip.jpg, clip.mp4, entry.json, notes.md} + cập nhật R/S/index.json.
    lib_extract.py index --root R --style S      dựng lại index.json từ entry.json và kiểm hợp lệ (mã thoát ≠ 0 nếu có lỗi).

Thư viện nằm NGOÀI skill (mặc định ~/opa-software/opa-video-studio-library, hoặc env OPA_LIBRARY_DIR): clip mẫu là của bên thứ ba.
ffmpeg: env FFMPEG / FFPROBE, không có thì tìm trong PATH.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

KINDS = ("caption", "broll", "painting", "line_text", "line_illus", "quote", "illus_mid", "illus_side",
         "object", "graph", "transition", "text_motion")
ID_RE = re.compile(r"^V\d{2,}-A\d{2,}$")
FILES = ("still", "strip", "clip", "notes")
CLIP_MAX_S = 3.0
STRIP_STEP = 2            # mỗi khung thứ 2
STRIP_MAX = 60            # tối đa số ô; dài hơn thì thưa bước
DIFF_THR = 24             # ngưỡng chênh xám 0-255 để tính là "có chuyển động"
ANALYSIS_W = 360          # độ rộng khung phân tích


def _bin(name: str) -> str:
    return os.environ.get(name.upper()) or shutil.which(name) or name


FF, FP = _bin("ffmpeg"), _bin("ffprobe")


def default_root() -> Path:
    return Path(os.environ.get("OPA_LIBRARY_DIR") or "~/opa-software/opa-video-studio-library").expanduser()


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([str(a) for a in args], capture_output=True, check=True)


def probe(video: Path) -> dict:
    j = json.loads(_run([FP, "-v", "error", "-show_streams", "-show_format", "-of", "json", video]).stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    n, d = (v.get("avg_frame_rate") or v["r_frame_rate"]).split("/")
    return {"w": int(v["width"]), "h": int(v["height"]), "fps": float(n) / float(d), "duration": float(j["format"]["duration"])}


def _crop_vf(crop: tuple | None) -> str:
    return f"crop={crop[2]}:{crop[3]}:{crop[0]}:{crop[1]}," if crop else ""


def _parse_crop(s: str | None) -> tuple | None:
    if not s:
        return None
    p = [int(x) for x in s.replace(":", ",").split(",")]
    if len(p) != 4 or min(p) < 0:
        sys.exit("LỖI: --crop cần X,Y,W,H (số nguyên ≥ 0)")
    return tuple(p)


# ---------------------------------------------------------------- đo
def _gray_frames(video: Path, t0: float, dur: float, crop: tuple | None, cw: int) -> tuple[np.ndarray, float]:
    """Khung xám đã thu nhỏ (n,h,w) cho đoạn [t0, t0+dur]; hệ số phóng về px gốc."""
    aw = min(ANALYSIS_W, cw) // 2 * 2
    vf = f"{_crop_vf(crop)}scale={aw}:-2,format=gray"
    raw = _run([FF, "-v", "error", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", video, "-vf", vf, "-an", "-f", "rawvideo", "-"]).stdout
    h = len(_run([FF, "-v", "error", "-ss", f"{t0:.3f}", "-i", video, "-vf", vf, "-frames:v", "1", "-f", "rawvideo", "-"]).stdout) // aw
    a = np.frombuffer(raw, np.uint8)
    n = len(a) // (aw * h)
    return a[: n * aw * h].reshape(n, h, aw), cw / aw


def _sharpness(fr: np.ndarray) -> np.ndarray:
    f = fr.astype(np.int16)
    return np.abs(np.diff(f, axis=2)).mean(axis=(1, 2)) + np.abs(np.diff(f, axis=1)).mean(axis=(1, 2))


def _motion(fr: np.ndarray, scale: float) -> dict:
    if len(fr) < 2:
        return {"motion_bbox_px": [0, 0, 0, 0], "motion_peak_frame": 0, "motion_settle_frame": 0}
    d = np.abs(np.diff(fr.astype(np.int16), axis=0))
    mask = (d > DIFF_THR).any(axis=0)
    ys, xs = np.where(mask)
    bbox = [0, 0, 0, 0] if not len(xs) else [int(xs.min() * scale), int(ys.min() * scale),
                                              int((xs.max() - xs.min() + 1) * scale), int((ys.max() - ys.min() + 1) * scale)]
    per = (d > DIFF_THR).mean(axis=(1, 2))
    moving = np.where(per > 0.002)[0]
    return {"motion_bbox_px": bbox, "motion_peak_frame": int(per.argmax()) + 1,
            "motion_settle_frame": int(moving.max()) + 2 if len(moving) else 0}


def _dominant(still: Path, k: int = 4) -> list[str]:
    im = Image.open(still).convert("RGB")
    im.thumbnail((120, 120))
    q = im.quantize(colors=6, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()
    cnt = sorted(q.getcolors(), reverse=True)[:k]
    return ["#%02X%02X%02X" % tuple(pal[i * 3:i * 3 + 3]) for _, i in cnt]


# ---------------------------------------------------------------- tạo file mục
def _still(video: Path, t: float, crop: tuple | None, out: Path) -> None:
    _run([FF, "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", video, "-vf", _crop_vf(crop).rstrip(",") or "null", "-frames:v", "1", out])


def _strip(video: Path, t0: float, dur: float, fps: float, crop: tuple | None, out: Path) -> None:
    n = max(1, round(dur * fps))
    step = max(STRIP_STEP, math.ceil(n / STRIP_MAX))
    cw = crop[2] if crop else probe(video)["w"]
    ch = crop[3] if crop else probe(video)["h"]
    tw = 150 if ch >= cw else 240
    cols = 10 if ch >= cw else 6
    with tempfile.TemporaryDirectory() as td:
        vf = f"{_crop_vf(crop)}select='not(mod(n\\,{step}))',scale={tw}:-2"
        _run([FF, "-v", "error", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", video, "-vf", vf, "-fps_mode", "vfr", "-an", Path(td) / "%04d.png"])
        files = sorted(Path(td).glob("*.png"))
        if not files:
            sys.exit("LỖI: không trích được khung cho strip")
        ims = [Image.open(f).convert("RGB") for f in files]
        w, h = ims[0].size
        rows = -(-len(ims) // cols)
        sheet = Image.new("RGB", (cols * w, rows * h), (30, 30, 30))
        dr = ImageDraw.Draw(sheet)
        for i, im in enumerate(ims):
            x, y = (i % cols) * w, (i // cols) * h
            sheet.paste(im, (x, y))
            dr.rectangle([x, y, x + 34, y + 11], fill=(0, 0, 0))
            dr.text((x + 2, y), f"f{i * step}", fill=(255, 230, 0))
        sheet.save(out, quality=85)


def _clip(video: Path, t0: float, dur: float, crop: tuple | None, out: Path) -> None:
    d = min(dur, CLIP_MAX_S)
    pw = probe(video)["w"]
    width = crop[2] if crop else pw
    vf = _crop_vf(crop) + ("scale=720:-2," if width > 720 else "") + "scale=trunc(iw/2)*2:trunc(ih/2)*2"
    _run([FF, "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{d:.3f}", "-i", video, "-vf", vf, "-an",
          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", out])


def _notes_md(e: dict, notes: str, rebuild: str) -> str:
    m, s = e["measures"], e["source"]
    p = f"nguyên tắc {e['principle']}" if e["principle"] else "không thuộc 10 nguyên tắc"
    L = [f"# {e['id']} — {e['title']}", "",
         f"- Loại: `{e['kind']}` ({p}). Nguồn: {s.get('author') or '?'} · {s.get('video')} · {s.get('url') or ''}".rstrip(" ·"),
         f"- Đoạn nguồn: {e['t'][0]:.2f}–{e['t'][1]:.2f} s = {m['frames']} khung @ {m['fps']:g} fps = {m['duration_ms']} ms",
         "", "## Số đo (đo máy)", f"- Khung hình mẫu: {m['frame_px'][0]}×{m['frame_px'][1]} px" + (f" (cắt từ {m['crop']})" if m.get("crop") else ""),
         f"- Vùng chuyển động (bbox, px): x={m['motion_bbox_px'][0]} y={m['motion_bbox_px'][1]} rộng={m['motion_bbox_px'][2]} cao={m['motion_bbox_px'][3]}",
         f"- Chuyển động mạnh nhất ở khung {m['motion_peak_frame']}; yên hẳn sau khung {m['motion_settle_frame']} "
         f"(≈ {round(m['motion_settle_frame'] * 1000 / m['fps'])} ms)",
         f"- Khung mẫu (still) lấy ở {m['still_t']:.2f} s; màu chủ đạo: {' '.join(m['dominant_colors'])}",
         "", "## Chuyện gì xảy ra", notes.strip() or "(chưa mô tả — bổ sung sau khi xem strip.jpg)",
         "", "## Dựng lại trên FilmCraft", rebuild.strip() or "(chưa ghi)", ""]
    return "\n".join(L)


# ---------------------------------------------------------------- entry / index
def entry(video: Path, eid: str, t0: float, t1: float, kind: str, title: str, root: Path, style: str, *,
          principle: int | None = None, crop: tuple | None = None, still_at: float | None = None,
          notes: str = "", rebuild: str = "", source: dict | None = None) -> dict:
    video = Path(video)
    if kind not in KINDS:
        sys.exit(f"LỖI: kind '{kind}' không hợp lệ; chọn một trong {', '.join(KINDS)}")
    if not ID_RE.match(eid):
        sys.exit(f"LỖI: id '{eid}' phải dạng Vxx-Ayy")
    if principle is not None and not 1 <= principle <= 10:
        sys.exit("LỖI: --principle phải 1..10")
    if not t1 > t0 >= 0:
        sys.exit("LỖI: --t cần S < E")
    pr = probe(video)
    fr, scale = _gray_frames(video, t0, t1 - t0, crop, crop[2] if crop else pr["w"])
    still_t = still_at if still_at is not None else t0 + int(_sharpness(fr).argmax()) / pr["fps"]
    d = Path(root).expanduser() / style / eid
    d.mkdir(parents=True, exist_ok=True)
    _still(video, still_t, crop, d / "still.png")
    _strip(video, t0, t1 - t0, pr["fps"], crop, d / "strip.jpg")
    _clip(video, t0, t1 - t0, crop, d / "clip.mp4")
    measures = {"frames": round((t1 - t0) * pr["fps"]), "fps": round(pr["fps"], 3), "duration_ms": round((t1 - t0) * 1000),
                "frame_px": [crop[2], crop[3]] if crop else [pr["w"], pr["h"]], "crop": list(crop) if crop else None,
                "still_t": round(still_t, 3), **_motion(fr, scale), "dominant_colors": _dominant(d / "still.png")}
    e = {"id": eid, "principle": principle, "kind": kind, "title": title, "t": [round(t0, 3), round(t1, 3)],
         "still": f"{eid}/still.png", "strip": f"{eid}/strip.jpg", "clip": f"{eid}/clip.mp4", "notes": f"{eid}/notes.md",
         "measures": measures, "source": source or {"video": video.name, "url": "", "author": ""}}
    (d / "notes.md").write_text(_notes_md(e, notes, rebuild), encoding="utf-8")
    (d / "entry.json").write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
    index(root, style, quiet=True)
    return e


def _check_entry(base: Path, e: dict) -> list[str]:
    eid, errs = e.get("id", "?"), []
    if not ID_RE.match(str(eid)):
        errs.append(f"{eid}: id sai dạng Vxx-Ayy")
    if e.get("kind") not in KINDS:
        errs.append(f"{eid}: kind '{e.get('kind')}' không hợp lệ")
    if e.get("principle") is not None and e.get("principle") not in range(1, 11):
        errs.append(f"{eid}: principle phải 1..10 hoặc null")
    t = e.get("t")
    if not (isinstance(t, list) and len(t) == 2 and t[1] > t[0] >= 0):
        errs.append(f"{eid}: t phải là [bắt đầu, kết thúc] với kết thúc > bắt đầu")
    for k in FILES:
        p = base / str(e.get(k, ""))
        if not p.is_file() or p.stat().st_size == 0:
            errs.append(f"{eid}: thiếu hoặc rỗng {e.get(k) or k}")
    clip = base / str(e.get("clip", ""))
    if clip.is_file() and clip.stat().st_size:
        errs += _check_clip(eid, clip)
    return errs


def _check_clip(eid: str, clip: Path) -> list[str]:
    j = json.loads(_run([FP, "-v", "error", "-show_entries", "stream=codec_type:format=duration", "-of", "json", clip]).stdout)
    errs = []
    if float(j["format"]["duration"]) > CLIP_MAX_S + 0.05:
        errs.append(f"{eid}: clip.mp4 dài hơn {CLIP_MAX_S:g} s")
    if any(s["codec_type"] == "audio" for s in j["streams"]):
        errs.append(f"{eid}: clip.mp4 còn tiếng")
    return errs


def index(root: Path, style: str, quiet: bool = False) -> tuple[int, list[str]]:
    """Dựng lại index.json từ các entry.json hợp lệ; trả (số mục hợp lệ, danh sách lỗi)."""
    base = Path(root).expanduser() / style
    ents, errs = [], []
    for ej in sorted(base.glob("V*-A*/entry.json")):
        try:
            e = json.loads(ej.read_text(encoding="utf-8"))
        except json.JSONDecodeError as ex:
            errs.append(f"{ej.parent.name}: entry.json hỏng ({ex})")
            continue
        if e.get("id") != ej.parent.name:
            errs.append(f"{ej.parent.name}: id trong entry.json là '{e.get('id')}', khác tên thư mục")
            continue
        bad = _check_entry(base, e)
        errs += bad
        if not bad:
            ents.append(e)
    base.mkdir(parents=True, exist_ok=True)
    (base / "index.json").write_text(json.dumps({"style": style, "entries": ents}, ensure_ascii=False, indent=1), encoding="utf-8")
    if not quiet:
        print(f"{style}: {len(ents)} mục hợp lệ" + (f", {len(errs)} lỗi" if errs else ""))
        for x in errs:
            print("LỖI:", x)
    return len(ents), errs


# ---------------------------------------------------------------- segments
def _load_transcribe_one():
    helper = Path(__file__).resolve().parents[1] / "apps" / "video-use" / "helpers" / "transcribe.py"
    spec = importlib.util.spec_from_file_location("video_use_transcribe", helper)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.transcribe_one


def _words(path: Path) -> list[tuple[float, float, str]]:
    """(bắt đầu, kết thúc, chữ) từ transcript kiểu Scribe ({"words": [...]}) hoặc danh sách đoạn [{start,end,text}]."""
    j = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(j, dict):
        return [(w["start"], w["end"], w["text"]) for w in j.get("words", []) if w.get("type", "word") == "word"]
    return [(s["start"], s["end"], s["text"]) for s in j]


def detect_cuts(video: Path, crop: tuple | None, threshold: float) -> list[float]:
    vf = f"{_crop_vf(crop)}scale=270:-2,scdet=threshold={threshold:g}"
    err = subprocess.run([FF, "-hide_banner", "-i", str(video), "-vf", vf, "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    cuts: list[float] = []
    for c in (float(t) for t in re.findall(r"lavfi\.scd\.time:\s*([\d.]+)", err)):
        if not cuts or c - cuts[-1] > 0.1:
            cuts.append(c)
    return cuts


def segments(video: Path, out: Path, transcript: Path | None = None, crop: tuple | None = None,
             threshold: float = 10.0, language: str = "vi") -> list[dict]:
    video, out = Path(video), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    if transcript is None:
        transcript = _load_transcribe_one()(video, out, language=language)
    words = _words(Path(transcript))
    pr = probe(video)
    bounds = [0.0] + detect_cuts(video, crop, threshold) + [pr["duration"]]
    segs = []
    for i, (a, b) in enumerate(zip(bounds, bounds[1:])):
        txt = " ".join(w for s, e, w in words if a - 0.05 <= (s + e) / 2 < b - 0.05)
        segs.append({"idx": i + 1, "t": [round(a, 3), round(b, 3)], "frames": round((b - a) * pr["fps"]),
                     "dur_s": round(b - a, 2), "words": txt})
    (out / "segments.json").write_text(json.dumps(segs, ensure_ascii=False, indent=1), encoding="utf-8")
    rows = ["| # | t (s) | khung | lời |", "|---|---|---|---|"] + [
        f"| {s['idx']} | {s['t'][0]:.2f}–{s['t'][1]:.2f} | {s['frames']} | {s['words']} |" for s in segs]
    (out / "segments.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    return segs


# ---------------------------------------------------------------- CLI
def _source(a, video: Path) -> dict:
    info = video.parent / "video.info.json"
    j = json.loads(info.read_text(encoding="utf-8")) if info.is_file() else {}
    return {"video": a.source_video or video.name, "url": a.url or j.get("webpage_url", ""), "author": a.author or j.get("uploader", "")}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("segments")
    s.add_argument("video", type=Path)
    s.add_argument("--out", type=Path, required=True)
    s.add_argument("--transcript", type=Path)
    s.add_argument("--crop")
    s.add_argument("--threshold", type=float, default=10.0)
    s.add_argument("--language", default="vi")
    e = sub.add_parser("entry")
    e.add_argument("video", type=Path)
    e.add_argument("--id", required=True)
    e.add_argument("--t", type=float, nargs=2, required=True, metavar=("S", "E"))
    e.add_argument("--kind", required=True, choices=KINDS)
    e.add_argument("--principle", type=int)
    e.add_argument("--title", required=True)
    e.add_argument("--root", type=Path, default=default_root())
    e.add_argument("--style", required=True)
    e.add_argument("--crop")
    e.add_argument("--still-at", type=float)
    e.add_argument("--notes", default="")
    e.add_argument("--notes-file", type=Path)
    e.add_argument("--rebuild", default="")
    e.add_argument("--url", default="")
    e.add_argument("--author", default="")
    e.add_argument("--source-video", default="")
    i = sub.add_parser("index")
    i.add_argument("--root", type=Path, default=default_root())
    i.add_argument("--style", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "segments":
        segs = segments(a.video, a.out, a.transcript, _parse_crop(a.crop), a.threshold, a.language)
        print(f"{len(segs)} đoạn → {a.out}/segments.json, segments.md")
        return 0
    if a.cmd == "entry":
        notes = a.notes_file.read_text(encoding="utf-8") if a.notes_file else a.notes
        r = entry(a.video, a.id, a.t[0], a.t[1], a.kind, a.title, a.root, a.style, principle=a.principle, crop=_parse_crop(a.crop),
                  still_at=a.still_at, notes=notes, rebuild=a.rebuild, source=_source(a, a.video))
        print(f"{r['id']} → {a.root}/{a.style}/{r['id']}")
        return 0
    ok, errs = index(a.root, a.style)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
