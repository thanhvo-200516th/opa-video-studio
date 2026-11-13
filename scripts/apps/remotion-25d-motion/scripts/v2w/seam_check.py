#!/usr/bin/env python3
"""Kiểm mối nối của phim đủ 16:9 bằng ảnh (README v2w §16): ở mỗi mối nối t, render still frame round(t·60) của
composition phim hai lần, ép cảnh trao (props only = out) và cảnh nhận (only = in); hai ảnh phải gần như trùng nhau.

Chạy:  python tools/v2w/seam_check.py [--seams 7.5,14,22.5] [--out out/v2-16x9/film/seams] [--offset 0]
  --offset k: so frame round(t·60) + k (k âm: frame cuối của cảnh trao trước mối nối).
Đo: tỉ lệ điểm ảnh lệch > 6 mức (max kênh) và lệch trung bình. ĐẠT khi tỉ lệ ≤ 0,5 % (= ngưỡng Tĩnh B: mắt không thấy
nhảy). Ghi <out>/seam_<t>_T<out>.png, _T<in>.png, _diff.png (điểm lệch tô đen trên nền trắng) và seams.json.
Remotion chỉ chạy qua tools/remotion_run.py (bundle một lần rồi still từ bundle).
Exit:  0 mọi mối nối đạt; 1 có mối nối lệch; 2 lỗi đầu vào / render.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_test import call, tests_json  # noqa: E402
from mux_test import InputError  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DIFF_LEVEL = 6
PASS_SHARE = 0.005


def still(bundle: Path, comp: str, frame: int, only: int, dst: Path) -> np.ndarray:
    props = json.dumps({"guides": False, "blur": True, "only": only}, separators=(",", ":"))
    call([sys.executable, "tools/remotion_run.py", "still", str(bundle), comp, str(dst), f"--frame={frame}",
          f"--props={props}"], f"still {comp} f{frame} only={only}")
    with Image.open(dst) as im:
        return np.asarray(im.convert("RGB"), dtype=np.int16)


def compare(a: np.ndarray, b: np.ndarray) -> dict:
    d = np.abs(a - b).max(axis=-1)
    return {"share": float((d > DIFF_LEVEL).mean()), "mean": float(np.abs(a - b).mean()), "max": int(d.max()), "mask": d > DIFF_LEVEL}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="So frame hai phía mỗi mối nối của phim đủ")
    ap.add_argument("--seams", help="giây, phân cách bằng dấu phẩy (mặc định: mọi mối nối của film/filmPlan.ts)")
    ap.add_argument("--out", type=Path, default=ROOT / "out/v2-16x9/film/seams")
    ap.add_argument("--offset", type=int, default=0)
    a = ap.parse_args()
    try:
        film = tests_json()["film"]
        seams = film["seams"]
        if a.seams:
            want = {round(float(x), 3) for x in a.seams.split(",")}
            seams = [s for s in seams if round(s["t"], 3) in want]
        if not seams:
            raise InputError("không có mối nối nào để kiểm")
        a.out.mkdir(parents=True, exist_ok=True)
        bundle = a.out / "bundle"
        call([sys.executable, "tools/remotion_run.py", "bundle", "--out-dir", str(bundle)], "bundle")
        rows = []
        for s in seams:
            frame = round(s["t"] * film["fps"]) + a.offset
            tag = f"seam_{s['t']:.3f}_f{frame}"
            ia = still(bundle, film["id"], frame, s["out"], a.out / f"{tag}_T{s['out']}.png")
            ib = still(bundle, film["id"], frame, s["in"], a.out / f"{tag}_T{s['in']}.png")
            r = compare(ia, ib)
            Image.fromarray(np.where(r.pop("mask"), 0, 255).astype(np.uint8)).save(a.out / f"{tag}_diff.png")
            r.update({"t": s["t"], "frame": frame, "out": s["out"], "in": s["in"], "pass": r["share"] <= PASS_SHARE})
            rows.append(r)
            print(f"{'ĐẠT' if r['pass'] else 'LỆCH'} mối nối {s['t']} s f{frame} T{s['out']} → T{s['in']}: "
                  f"{r['share']:.2%} điểm lệch > {DIFF_LEVEL} mức (trần {PASS_SHARE:.1%}), lệch TB {r['mean']:.2f}, max {r['max']}")
        (a.out / "seams.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        return 0 if all(r["pass"] for r in rows) else 1
    except InputError as e:
        print(f"LỖI: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
