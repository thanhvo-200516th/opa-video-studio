#!/usr/bin/env python3
"""Trang duyệt một video (học từ ghost-editor approval_sheet.plan_frames): khung ở các mốc người xem cảm nhận nhất.

Mốc: 0 s (mở đầu) · 0,5 s · 1,5 s (hook) · mỗi điểm cắt V1 + 0,12 s · 0,2 s trước khi hết. Gộp mốc cách nhau < 0,3 s,
tối đa 24 khung.

    python contact_sheet.py times spec.craft.json [--full] [--out times.txt]   # in các mốc; --out ghi ra tệp (v2.6)
                                                       # → fc_fast_qa.py --times-file times.txt (chạy được trong bash lẫn zsh)
    python contact_sheet.py sheet spec.craft.json qa_frames out.jpg [--full]   # ghép khung fc_fast_qa đã xuất thành 1 ảnh

--full (v2.5): thêm MỖI lớp chữ một khung ở lúc chữ đã vào xong (at + settle; settle = key vào cuối cùng ≤ min(1,2 s, 0,6·dur) + 1 khung,
không có key thì 0,45 s) để xem hết chữ trên hình. Tối đa 40 khung, cách nhau ≥ 0,3 s; quá thì thưa phụ đề trước, rồi mới thưa điểm cắt.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

AFTER_CUT = 0.12
MERGE = 0.3
MAX_FRAMES = 24
FULL_MAX = 40
SETTLE_DEFAULT, SETTLE_CAP = 0.45, 1.2
THUMB_W, THUMB_H, COLS, LABEL_H = 216, 384, 6, 34
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def plan_times(spec: dict, full: bool = False) -> list[tuple[float, str]]:
    if full:
        return _plan_full(spec)
    end = float(spec["duration"])
    v1 = next(t for t in spec["tracks"] if t.get("type") == "video")
    cuts = sorted({round(c["at"], 3) for c in v1["clips"] if c["at"] > 0.05})
    fixed = [(0.0, "mở đầu"), (0.5, "0,5 s"), (1.5, "hook 1,5 s")]
    cut_t = [(round(t + AFTER_CUT, 2), f"cắt {i + 1}") for i, t in enumerate(cuts)]
    tail = [(round(max(0.0, end - 0.2), 2), "cuối")]
    room = MAX_FRAMES - len(fixed) - len(tail)
    if len(cut_t) > room:                                  # quá nhiều điểm cắt: lấy đều
        cut_t = [cut_t[round(i * (len(cut_t) - 1) / (room - 1))] for i in range(room)]
    out: list[tuple[float, str]] = []
    for t, lab in sorted(fixed + cut_t + tail):
        if t < end and (not out or t - out[-1][0] >= MERGE):
            out.append((t, lab))
    return out


def _entrance_keys(c: dict) -> list[float]:
    """Mốc mọi keyframe (opacity, motion, tham số effect) của clip."""
    def walk(o):
        if isinstance(o, list) and o and all(isinstance(k, (list, tuple)) and len(k) >= 2 and isinstance(k[0], (int, float)) for k in o):
            yield from (float(k[0]) for k in o)
        elif isinstance(o, dict):
            for v in o.values():
                yield from walk(v)
        elif isinstance(o, list):
            for v in o:
                yield from walk(v)
    return list(walk({k: v for k, v in c.items() if k in ("opacity", "motion", "effects")}))


def settle_time(c: dict, fps: float = 30.0) -> float:
    """Giây (so với `at`) chữ đã vào xong: key cuối ≤ min(1,2 s, 0,6·dur) + 1 khung; không có key → 0,45 s; không vượt hết clip."""
    lim = min(SETTLE_CAP, 0.6 * c["dur"])
    ks = [k for k in _entrance_keys(c) if 0 < k <= lim]
    return min(max(ks) + 1 / fps if ks else SETTLE_DEFAULT, max(c["dur"] - 1 / fps, 0.0))


def _plan_full(spec: dict) -> list[tuple[float, str]]:
    end, fps = float(spec["duration"]), float(spec.get("fps", 30))
    v1 = next(t for t in spec["tracks"] if t.get("type") == "video")
    groups: dict[str, list[tuple[float, str]]] = {"fixed": [(0.0, "mở đầu"), (round(max(0.0, end - 0.2), 2), "cuối")],
                                                  "key": [], "cut": [], "cap": []}
    groups["cut"] = [(round(c["at"] + AFTER_CUT, 2), "cắt") for c in v1["clips"] if c["at"] > 0.05]
    for t in spec["tracks"]:
        name = t.get("name", "")
        lane = name.replace("FX ·", "").split()[0] if name.replace("FX ·", "").split() else ""
        if t.get("type") != "text" and not lane.startswith("text_img"):
            continue
        for c in t["clips"]:
            at = round(c["at"] + settle_time(c, fps), 2)
            if at < end:
                groups["cap" if lane == "text_low" else "key"].append((at, "phụ đề" if lane == "text_low" else "chữ chính"))
    kept: list[tuple[float, str]] = []
    for kind in ("fixed", "key", "cut", "cap"):
        ok: list[tuple[float, str]] = []
        for t, lab in sorted(groups[kind]):
            if t < end and all(abs(t - k) >= MERGE - 1e-9 for k, _ in kept + ok):
                ok.append((t, lab))
        room = max(0, FULL_MAX - len(kept))
        if len(ok) > room:                                 # thưa đều: phụ đề trước, rồi điểm cắt
            ok = [ok[round(i * (len(ok) - 1) / (room - 1))] for i in range(room)] if room > 1 else ok[:room]
        kept += ok
    return sorted(kept)


def sheet(spec: dict, frames: Path, out: Path, title: str = "", full: bool = False) -> Path:
    times = plan_times(spec, full)
    rows = (len(times) + COLS - 1) // COLS
    head = 48
    img = Image.new("RGB", (COLS * THUMB_W, head + rows * (THUMB_H + LABEL_H)), (18, 18, 20))
    d = ImageDraw.Draw(img)
    big, small = ImageFont.truetype(FONT, 24), ImageFont.truetype(FONT, 18)
    d.text((12, 10), title or spec.get("name", "")[:90], font=big, fill=(255, 255, 255))
    for i, (t, lab) in enumerate(times):
        x, y = (i % COLS) * THUMB_W, head + (i // COLS) * (THUMB_H + LABEL_H)
        f = frames / f"t{t:07.2f}.png"
        if f.is_file():
            img.paste(Image.open(f).convert("RGB").resize((THUMB_W, THUMB_H)), (x, y))
        else:
            d.text((x + 10, y + THUMB_H // 2), "thiếu khung", font=small, fill=(255, 90, 90))
        d.text((x + 8, y + THUMB_H + 6), f"{t:.2f}s · {lab}", font=small, fill=(255, 210, 60))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, quality=88)
    return out


def main() -> int:
    full = "--full" in sys.argv
    argv = [a for a in sys.argv[1:] if a != "--full"]
    out_file = None
    if "--out" in argv and argv.index("--out") + 1 < len(argv) and argv[0] == "times":
        i = argv.index("--out")
        out_file = Path(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    args = argv
    if len(args) < 2 or args[0] not in ("times", "sheet"):
        print(__doc__)
        return 2
    spec = json.loads(Path(args[1]).read_text(encoding="utf-8"))
    if args[0] == "times":
        text = " ".join(f"{t:.2f}" for t, _ in plan_times(spec, full))
        if out_file:
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(text + "\n", encoding="utf-8")
            print(f"{len(text.split())} mốc → {out_file}")
        else:
            print(text)
    else:
        print(sheet(spec, Path(args[2]), Path(args[3]), full=full))
    return 0


if __name__ == "__main__":
    sys.exit(main())
