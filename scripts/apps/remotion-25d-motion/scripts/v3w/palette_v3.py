#!/usr/bin/env python3
"""Kiểm bảng màu V3: đúng luật của tools/v2w/palette_w.py (import, không sửa) nhưng cộng token đỏ cảnh báo ALERT #E5484D
(Minh chốt 11/10, chỉ cho dấu "rò khách"). Bảng token và 15 đoạn nối được dựng lại khi nạp module này.
Thêm: tỉ lệ điểm ALERT (≤ 8/255 quanh #E5484D) mỗi ảnh, để soát ALERT không thành mảng lớn (luật: không làm nền lớn).

Chạy:  python tools/v3w/palette_v3.py <png…> [--json]
Exit:  0 đạt, 1 có FAIL, 2 lỗi đầu vào.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "v2w"))
import palette_w  # noqa: E402

ALERT_RGB = (229, 72, 77)
ALERT_MAX_SHARE = 0.02  # ALERT là dấu nhỏ: > 2 % khung là lạm dụng

TOKENS_V3 = {**palette_w.TOKENS_W, "alert": ALERT_RGB}
palette_w._PTS = np.array(list(TOKENS_V3.values()), dtype=np.float32)  # noqa: SLF001 — dựng lại bảng token
palette_w._SEGS = [(palette_w._PTS[i], palette_w._PTS[j])  # noqa: SLF001
                   for i, j in itertools.combinations(range(len(palette_w._PTS)), 2)]


def check_file(path: Path) -> dict:
    rgb = palette_w.load_rgb(path)
    r = {"file": str(path), **palette_w.check_palette_w(rgb)}
    near = np.max(np.abs(rgb - np.array(ALERT_RGB, dtype=np.int16)), axis=-1) <= 8
    share = float(near.mean())
    r["alert_share"] = round(share, 5)
    if share > ALERT_MAX_SHARE:
        r["reasons"].append(f"ALERT chiếm {share:.2%} khung > {ALERT_MAX_SHARE:.0%} (chỉ được là dấu nhỏ)")
        r["pass"] = False
    return r


def summary(r: dict) -> str:
    return palette_w.summary(r) + f" · ALERT {r['alert_share']:.3%}"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    as_json = "--json" in args
    files = [Path(a) for a in args if a != "--json"]
    if not files:
        print("Cách dùng: palette_v3.py <png…> [--json]", file=sys.stderr)
        return 2
    missing = [str(f) for f in files if not f.is_file()]
    if missing:
        print(f"Thiếu file: {', '.join(missing)}", file=sys.stderr)
        return 2
    results = [check_file(f) for f in files]
    if as_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(summary(r))
        fails = sum(1 for r in results if not r["pass"])
        print(f"TỔNG: {len(results) - fails} PASS, {fails} FAIL")
    return 1 if any(not r["pass"] for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
