#!/usr/bin/env python3
"""Bắt chớp, bước nhảy lạ và khung đứng yên trên video (KH §3.10, NC §4.4).

Chạy:  python tools/qa/pops.py <mp4> --cues <json> [--still-ok A-B,C-D]
Đo:    d(a,b) = trung bình |chênh| ảnh xám 108×192 (thang 0–255).
  FAIL "chớp" ở f: d(f−1,f) và d(f,f+1) cùng > 3 × trung vị (±15 f) và > 4,
         nhưng d(f−1,f+1) < 1/3 hai giá trị đó; ngoài `cuts` của cues ±2 f.
  WARN bước nhảy một phía (> ngưỡng như trên) ngoài whitelist.
  WARN khung đứng yên (diff < 0,01) > 30 f ngoài các khoảng đứng yên có chủ đích.
Exit:  0 đạt, 1 có FAIL, 2 lỗi đầu vào.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

W, H = 108, 192
MED_RADIUS = 15
MED_FACTOR = 3.0
MIN_JUMP = 4.0
RETURN_RATIO = 1 / 3
CUT_PAD = 2
STILL_EPS = 0.01
STILL_MAX = 30
# Khoảng được đứng yên của V2 (TK §1): STILL [SNORT_END, CHARGE_AT) và khung CTA [CTA_LOCK, hết).
# cues.json không chứa hai mốc này nên ghi ở đây; đổi bằng --still-ok.
STILL_OK_V2: tuple[tuple[int, int], ...] = ((276, 288), (825, 900))


def decode_gray(mp4: Path) -> np.ndarray:
    """Giải mã toàn bộ video thành mảng (N, 192, 108) float32."""
    cmd = ["ffmpeg", "-v", "error", "-i", str(mp4), "-fps_mode", "passthrough",
           "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    proc = subprocess.run(cmd, capture_output=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg lỗi: {proc.stderr.decode('utf-8', 'replace')[-500:]}")
    raw = np.frombuffer(proc.stdout, dtype=np.uint8)
    n = raw.size // (W * H)
    return raw[: n * W * H].reshape(n, H, W).astype(np.float32)


def load_cuts(cues_path: Path) -> list[tuple[int, int]]:
    data = json.loads(cues_path.read_text(encoding="utf-8"))
    return [(int(c["from"]), int(c["to"])) for c in data.get("cuts", [])]


def whitelisted(f: int, cuts: list[tuple[int, int]]) -> bool:
    """f nằm trong [from − 2, to − 1 + 2] của một cut."""
    return any(a - CUT_PAD <= f <= b - 1 + CUT_PAD for a, b in cuts)


def in_ranges(f: int, ranges: tuple[tuple[int, int], ...]) -> bool:
    return any(a <= f < b for a, b in ranges)


def analyze(frames: np.ndarray, cuts: list[tuple[int, int]],
            still_ok: tuple[tuple[int, int], ...] = STILL_OK_V2) -> dict:
    """Phân tích mảng ảnh xám. Trả {frames, fails:[…], warns:[…]}."""
    n = len(frames)
    d1 = np.zeros(n, dtype=np.float64)  # d1[f] = d(f−1, f)
    for f in range(1, n):
        d1[f] = float(np.abs(frames[f] - frames[f - 1]).mean())

    def thr(f: int) -> float:
        lo, hi = max(1, f - MED_RADIUS), min(n - 1, f + MED_RADIUS)
        med = float(np.median(d1[lo : hi + 1])) if hi >= lo else 0.0
        return max(MED_FACTOR * med, MIN_JUMP)

    fails, warns = [], []
    flashes: set[int] = set()
    for f in range(1, n - 1):
        a, b, t = float(d1[f]), float(d1[f + 1]), thr(f)
        if a > t and b > t:
            c = float(np.abs(frames[f + 1] - frames[f - 1]).mean())
            if c < RETURN_RATIO * min(a, b):
                flashes.add(f)
                if not whitelisted(f, cuts):
                    fails.append({"frame": f, "kind": "chop", "d_prev": round(a, 2),
                                  "d_next": round(b, 2), "d_skip": round(c, 2)})
    for f in range(1, n):
        if f in flashes or (f - 1) in flashes or whitelisted(f, cuts):
            continue
        if d1[f] > thr(f):
            warns.append({"frame": f, "kind": "nhay", "d": round(float(d1[f]), 2)})
    run_start = None
    for f in range(1, n + 1):
        still = f < n and d1[f] < STILL_EPS and not in_ranges(f, still_ok)
        if still and run_start is None:
            run_start = f
        elif not still and run_start is not None:
            if f - run_start > STILL_MAX:
                warns.append({"frame": run_start, "kind": "dung-yen", "to": f, "len": f - run_start})
            run_start = None
    return {"frames": n, "fails": fails, "warns": warns}


def run(mp4: Path, cues: Path, still_ok: tuple[tuple[int, int], ...] = STILL_OK_V2) -> dict:
    return analyze(decode_gray(mp4), load_cuts(cues), still_ok)


def describe(item: dict) -> str:
    if item["kind"] == "chop":
        return f"chớp f{item['frame']} d(f−1,f)={item['d_prev']} d(f,f+1)={item['d_next']} d(f−1,f+1)={item['d_skip']}"
    if item["kind"] == "nhay":
        return f"bước nhảy một phía f{item['frame']} d={item['d']}"
    return f"đứng yên f{item['frame']}–f{item['to'] - 1} ({item['len']} f)"


def parse_ranges(raw: str) -> tuple[tuple[int, int], ...]:
    out = []
    for part in filter(None, raw.split(",")):
        a, b = part.split("-")
        out.append((int(a), int(b)))
    return tuple(out)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    try:
        mp4 = Path(args[0])
        cues = Path(args[args.index("--cues") + 1])
        still_ok = parse_ranges(args[args.index("--still-ok") + 1]) if "--still-ok" in args else STILL_OK_V2
    except (IndexError, ValueError):
        print("Cách dùng: pops.py <mp4> --cues <json> [--still-ok A-B,C-D]", file=sys.stderr)
        return 2
    for p in (mp4, cues):
        if not p.is_file():
            print(f"Thiếu file: {p}", file=sys.stderr)
            return 2
    res = run(mp4, cues, still_ok)
    for item in res["fails"]:
        print(f"FAIL {describe(item)}")
    for item in res["warns"]:
        print(f"WARN {describe(item)}")
    print(f"TỔNG: {res['frames']} frame, {len(res['fails'])} FAIL, {len(res['warns'])} WARN")
    return 1 if res["fails"] else 0


if __name__ == "__main__":
    sys.exit(main())
