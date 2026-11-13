#!/usr/bin/env python3
"""Đo ĐỈNH THỊ GIÁC quanh từng cue của V3 trên MP4 (không chỉ so mốc trong mã): đọc ROI từ tools/v3w/cue_rois.ts, giải mã
MP4 ở 960×540 (một lượt, ffmpeg pipe), đếm điểm màu token trong ROI mỗi frame rồi tìm frame đỉnh theo cách đo của ROI.
Chênh = frame đỉnh − frame cue (f60). |chênh| ≤ 1 f60 là khớp (hợp đồng ±1 f60 với V3-AM); ROI có `accept` dùng khoảng
nhận riêng (thở phì: đỉnh phồng trong 8,75–8,80 theo lead).

Chạy:  python tools/v3w/cue_visual.py <mp4> [--rois out.json] [--json kết_quả.json]
Exit:  0 mọi cue khớp, 1 có cue lệch > 1 f60, 2 lỗi đầu vào.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
FPS = 60
HALF = 2  # giải mã 960×540
COLORS = {
    "white": lambda f: (f[..., 0] > 225) & (f[..., 1] > 225) & (f[..., 2] > 225),
    "blue": lambda f: (f[..., 0] < 50) & (f[..., 1] > 80) & (f[..., 1] < 135) & (f[..., 2] > 215),
    "red": lambda f: (f[..., 0] > 190) & (f[..., 1] < 120) & (f[..., 2] < 130),
}
TOL = 1.0


def make_rois(path: Path) -> dict:
    node = shutil.which("node") or "node"
    r = subprocess.run([node, str(ROOT / "node_modules/tsx/dist/cli.mjs"), "tools/v3w/cue_rois.ts", str(path)], cwd=ROOT)
    if r.returncode != 0:
        raise SystemExit(2)
    return json.loads(path.read_text(encoding="utf-8"))


def frames(mp4: Path):
    cmd = [shutil.which("ffmpeg") or "ffmpeg", "-v", "error", "-i", str(mp4), "-vf", "scale=960:540:flags=area",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    size = 960 * 540 * 3
    n = 0
    while True:
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        yield n, np.frombuffer(buf, np.uint8).reshape(540, 960, 3)
        n += 1
    p.wait()


def measure(mp4: Path, rois: list[dict]) -> dict[str, dict[int, float]]:
    """Mỗi ROI: {frame: giá trị} trong cửa sổ (số điểm màu, hoặc độ thay đổi trung bình cho kiểu diff)."""
    out: dict[str, dict[int, float]] = {r["cue"]: {} for r in rois}
    prev: dict[str, np.ndarray] = {}
    for n, f in frames(mp4):
        t = n / FPS
        for r in rois:
            a, b = r["win"]
            if not (a - 2 / FPS <= t <= b):
                continue
            x0, y0, x1, y1 = (max(0, int(v / HALF)) for v in r["box"])
            x1, y1 = min(960, x1), min(540, y1)
            crop = f[y0:y1, x0:x1].astype(np.int16)
            if r["kind"] == "diff":
                g = crop.mean(axis=2)
                if r["cue"] in prev and prev[r["cue"]].shape == g.shape:
                    out[r["cue"]][n] = float(np.abs(g - prev[r["cue"]]).mean())
                prev[r["cue"]] = g
            else:
                out[r["cue"]][n] = float(COLORS[r["color"]](crop).sum())
    return out


def peak(r: dict, series: dict[int, float]) -> int | None:
    a, b = round(r["win"][0] * FPS), round(r["win"][1] * FPS)
    ns = [n for n in sorted(series) if a <= n <= b]
    if not ns:
        return None
    v = np.array([series[n] for n in ns], dtype=float)
    if r.get("norm"):
        s = r["norm"]["s"]
        v = v / np.array([s[min(len(s) - 1, max(0, n - r["norm"]["from"]))] ** 2 for n in ns])
    kind = r["kind"]
    if kind in ("max", "diff"):
        return ns[int(np.argmax(v))]
    if kind == "min":
        return ns[int(np.argmin(v))]
    if kind == "bump":  # đỉnh bướu sau khi trừ xu hướng tuyến tính của cửa sổ (thở idle, đổi zoom chậm)
        trend = np.linspace(v[0], v[-1], len(v))
        return ns[int(np.argmax(v - trend))]
    if kind == "rise":
        d = np.diff(v, prepend=v[0])
        return ns[int(np.argmax(d))]
    base = v[0]
    if kind == "onset":
        hit = [n for n, x in zip(ns, v) if x > base + max(30, 0.02 * (v.max() - base))]
        return hit[0] if hit else None
    if kind == "drop":
        thr = 0.005 * 960 * 540
        hit = [n for n, x in zip(ns, v) if x < thr]
        return hit[0] if hit else None
    return None


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Đo đỉnh thị giác quanh cue V3 trên MP4")
    ap.add_argument("mp4", type=Path)
    ap.add_argument("--rois", type=Path, default=ROOT / "out/v3-16x9/cue_rois.json")
    ap.add_argument("--json", type=Path, default=ROOT / "out/v3-16x9/cue_visual.json")
    a = ap.parse_args()
    if not a.mp4.is_file():
        print(f"LỖI: không có {a.mp4}", file=sys.stderr)
        return 2
    spec = make_rois(a.rois)
    series = measure(a.mp4, spec["rois"])
    rows = []
    for r in spec["rois"]:
        pk = peak(r, series[r["cue"]])
        d = None if pk is None else pk - round(r["t"] * FPS)
        lo, hi = r.get("accept", [-TOL, TOL])
        rows.append({"cue": r["cue"], "t": r["t"], "kind": r["kind"], "peakF60": pk, "deltaF60": d, "accept": [lo, hi],
                     "ok": d is not None and lo <= d <= hi, "source": "video"})
    for an in spec["analytic"]:
        d = round((an["peak"] - an["t"]) * FPS, 2)
        info = bool(an.get("info"))
        rows.append({"cue": an["cue"], "t": an["t"], "kind": "info" if info else "analytic", "peakF60": round(an["peak"] * FPS, 2),
                     "deltaF60": d, "ok": info or abs(d) <= TOL, "source": "code", "note": an["note"]})
    a.json.parent.mkdir(parents=True, exist_ok=True)
    a.json.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    for x in rows:
        d = "—" if x["deltaF60"] is None else f"{x['deltaF60']:+g}"
        print(f"  {x['t']:6.2f} {x['cue']:<22} {x['kind']:<8} đỉnh f{x['peakF60']} → chênh {d} f60 "
              f"{'' if x['ok'] else 'LỆCH'} ({x['source']})")
    bad = [x for x in rows if not x["ok"]]
    print(f"[cue_visual] {len(rows) - len(bad)}/{len(rows)} khớp ±{TOL:g} f60")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
