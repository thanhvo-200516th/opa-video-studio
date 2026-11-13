#!/usr/bin/env python3
"""Kiểm bảng màu bản 16:9 có motion blur (NN §8.7, KT §2.6).

Chạy:  python tools/v2w/palette_w.py <png…> [--json]
Luật:
  - Mỗi điểm ảnh phải cách một token HOẶC đoạn thẳng nối hai token ≤ 8/255 (Euclid RGB). Lý do: khử răng cưa và blur
    (T1, T2) trộn hai màu token thành sắc trung gian nằm trên đoạn nối; màu mới (đỏ, lục…) thì nằm xa mọi đoạn.
  - FAIL khi > 2 % điểm ảnh lệch.
  - FAIL khi MẢNG XÁM PHẲNG > 0,5 % khung (blur v2, quyết định chủ dự án 07/10): điểm phẳng (lân cận 3×3 chênh ≤ 6 mỗi
    kênh), trung tính (max − min kênh ≤ 24) và xa mọi token > 16 mức. Vùng blur trộn hai màu token vẫn được miễn ở luật
    đoạn nối; riêng xám phẳng (vạch đen bị kéo thành dải, chữ đen nhòe) là lỗi.
  - WARN (không chặn): vùng phẳng xa token > 4 mức (max kênh), từ 100 điểm trở lên. Ví dụ vệt blur dài, mảng màu lạ nhỏ.
Exit:  0 đạt, 1 có FAIL, 2 lỗi đầu vào.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import maximum_filter, minimum_filter

# 5 token thương hiệu (BRAND-SPEC, src/brand/tokens.ts).
TOKENS_W: dict[str, tuple[int, int, int]] = {
    "blue": (0, 104, 255),
    "black": (10, 10, 10),
    "white": (255, 255, 255),
    "blueLight": (230, 240, 255),
    "blueDark": (0, 60, 153),
}
SEG_TOL = 8.0  # khoảng cách tối đa tới token/đoạn nối (đơn vị 0..255)
FAIL_SHARE = 0.02
FLAT_TOL = 6
FLAT_TOKEN_TOL = 4
WARN_MIN_PX = 100
GRAY_CHROMA = 24  # max − min kênh: trung tính (xám)
GRAY_TOKEN_TOL = 16  # xa mọi token hơn mức này mới là "xám" (không phải viền khử răng cưa sát đen/trắng)
FLAT_GRAY_FAIL = 0.005
BIN = 16
CHUNK = 1 << 20  # điểm ảnh mỗi lượt tính (giữ bộ nhớ vừa phải)

_PTS = np.array(list(TOKENS_W.values()), dtype=np.float32)
_SEGS = [(_PTS[i], _PTS[j]) for i, j in itertools.combinations(range(len(_PTS)), 2)]


def load_rgb(path: Path) -> np.ndarray:
    """Đọc ảnh thành mảng int16 H×W×3 (bỏ alpha)."""
    with Image.open(path) as im:
        return np.asarray(im.convert("RGB"), dtype=np.int16)


def seg_distance(rgb: np.ndarray) -> np.ndarray:
    """Khoảng cách Euclid (0..255) từ mỗi điểm tới đoạn gần nhất trong 10 đoạn nối token (đầu mút = token)."""
    flat = rgb.reshape(-1, 3).astype(np.float32)
    out = np.empty(len(flat), dtype=np.float32)
    for s in range(0, len(flat), CHUNK):
        p = flat[s:s + CHUNK]
        best = np.full(len(p), np.inf, dtype=np.float32)
        for a, b in _SEGS:
            d = b - a
            u = np.clip(((p - a) @ d) / float(d @ d), 0.0, 1.0)
            best = np.minimum(best, np.linalg.norm(p - (a + u[:, None] * d), axis=1))
        out[s:s + CHUNK] = best
    return out.reshape(rgb.shape[:2])


def flat_mask(rgb: np.ndarray) -> np.ndarray:
    """Điểm có cả 8 lân cận chênh ≤ FLAT_TOL mỗi kênh so với nó (như tools/qa/palette.py)."""
    ok = np.ones(rgb.shape[:2], dtype=bool)
    for c in range(3):
        ch = rgb[..., c]
        ok &= (maximum_filter(ch, size=3, mode="nearest") - ch <= FLAT_TOL) & \
              (ch - minimum_filter(ch, size=3, mode="nearest") <= FLAT_TOL)
    return ok


def token_gap(rgb: np.ndarray) -> np.ndarray:
    """Chênh max kênh tới token gần nhất."""
    return np.min(np.max(np.abs(rgb[..., None, :] - _PTS.astype(np.int16)), axis=-1), axis=-1)


def top_colors(vals: np.ndarray, total: int, k: int = 5) -> list[dict]:
    """Màu lạ gặp nhiều nhất (gom ô 16 mức), kèm tỉ lệ khung."""
    if len(vals) == 0:
        return []
    keys = (vals // BIN).astype(np.int32) @ np.array([10000, 100, 1])
    uniq, counts = np.unique(keys, return_counts=True)
    order = np.argsort(-counts)[:k]
    return [{"rgb": [int(round(v)) for v in vals[keys == uniq[i]].mean(axis=0)], "share": round(float(counts[i] / total), 5)}
            for i in order]


def flat_gray_mask(rgb: np.ndarray, flat: np.ndarray | None = None, gap: np.ndarray | None = None) -> np.ndarray:
    """Mảng xám phẳng: phẳng 3×3, trung tính (max − min kênh ≤ GRAY_CHROMA), xa mọi token > GRAY_TOKEN_TOL."""
    flat = flat_mask(rgb) if flat is None else flat
    gap = token_gap(rgb) if gap is None else gap
    chroma = rgb.max(axis=-1) - rgb.min(axis=-1)
    return flat & (chroma <= GRAY_CHROMA) & (gap > GRAY_TOKEN_TOL)


def check_palette_w(rgb: np.ndarray) -> dict:
    """Trả {pass, off_px, off_share, flat_off_px, flat_off_share, flat_gray_px, flat_gray_share, offenders, warns,
    reasons}."""
    total = rgb.shape[0] * rgb.shape[1]
    off = seg_distance(rgb) > SEG_TOL
    off_px = int(off.sum())
    flat = flat_mask(rgb)
    gap = token_gap(rgb)
    flat_off = flat & (gap > FLAT_TOKEN_TOL)
    flat_px = int(flat_off.sum())
    gray = flat_gray_mask(rgb, flat, gap)
    gray_px = int(gray.sum())
    reasons = [f"{off_px / total:.2%} điểm lệch khỏi token/đoạn nối > {SEG_TOL:g} (trần {FAIL_SHARE:.0%})"] \
        if off_px / total > FAIL_SHARE else []
    if gray_px / total > FLAT_GRAY_FAIL:
        reasons.append(f"mảng xám phẳng {gray_px / total:.2%} khung > {FLAT_GRAY_FAIL:.1%}, "
                       f"màu {[c['rgb'] for c in top_colors(rgb[gray], total, 3)]}")
    warns = [f"vùng phẳng xa token: {flat_px / total:.2%} khung, màu {[c['rgb'] for c in top_colors(rgb[flat_off], total, 3)]}"] \
        if flat_px >= WARN_MIN_PX else []
    return {
        "pass": not reasons,
        "off_px": off_px,
        "off_share": round(off_px / total, 5),
        "flat_off_px": flat_px,
        "flat_off_share": round(flat_px / total, 5),
        "flat_gray_px": gray_px,
        "flat_gray_share": round(gray_px / total, 5),
        "offenders": top_colors(rgb[off], total),
        "warns": warns,
        "reasons": reasons,
    }


def check_file(path: Path) -> dict:
    return {"file": str(path), **check_palette_w(load_rgb(path))}


def summary(r: dict) -> str:
    tag = "PASS" if r["pass"] else "FAIL"
    note = "; ".join(r["reasons"]) or f"lệch {r['off_share']:.2%}, xám phẳng {r['flat_gray_share']:.2%}"
    lines = [f"{tag} palette_w {r['file']} {note}"]
    return "\n".join(lines + [f"  WARN {w}" for w in r["warns"]])


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    as_json = "--json" in args
    files = [Path(a) for a in args if a != "--json"]
    if not files:
        print("Cách dùng: palette_w.py <png…> [--json]", file=sys.stderr)
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
