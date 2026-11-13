#!/usr/bin/env python3
"""Kiểm bảng màu trên ảnh (KH §3.10, NC §4.4).

Chạy:  python tools/qa/palette.py <png…> [--json]
Luật:  chỉ xét vùng phẳng (lân cận 3×3 chênh mỗi kênh ≤ 6 so với tâm).
  - Mọi màu phẳng chiếm > 2 % khung phải nằm trong ±4 của một token.
  - Xám phẳng (R≈G≈B, 30–225) > 0,5 % khung → FAIL.
  - Có vùng phẳng ≈ #171717 (đen bị nâng, lỗi dải màu) → FAIL.
Exit:  0 đạt, 1 có FAIL, 2 lỗi đầu vào.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import maximum_filter, minimum_filter

# Token (RGB). blue có thêm (0,103,255): H.264 hay làm lệch 1 mức.
TOKENS: dict[str, tuple[tuple[int, int, int], ...]] = {
    "blue": ((0, 104, 255), (0, 103, 255)),
    "black": ((10, 10, 10),),
    "white": ((255, 255, 255),),
    "blueLight": ((230, 240, 255),),
    "blueDark": ((0, 60, 153),),
}
TOL = 4  # ±4 mỗi kênh
FLAT_TOL = 6  # vùng phẳng: lân cận 3×3 chênh ≤ 6
BIG_SHARE = 0.02  # màu > 2 % khung phải là token
GRAY_SHARE = 0.005  # xám phẳng > 0,5 % → FAIL
GRAY_RANGE = (30, 225)
GRAY_SPREAD = 8  # R≈G≈B: max − min kênh ≤ 8
RAISED_BLACK = (23, 23, 23)  # #171717
RAISED_MIN_PX = 100  # bỏ qua vài điểm nhiễu lẻ
BIN = 16  # gom màu lạ theo ô 16 mức mỗi kênh


def load_rgb(path: Path) -> np.ndarray:
    """Đọc ảnh thành mảng int16 H×W×3 (bỏ alpha)."""
    with Image.open(path) as im:
        return np.asarray(im.convert("RGB"), dtype=np.int16)


def near(rgb: np.ndarray, ref: tuple[int, int, int], tol: int = TOL) -> np.ndarray:
    """Mặt nạ điểm trong ±tol mỗi kênh của `ref`."""
    return np.all(np.abs(rgb - np.array(ref, dtype=np.int16)) <= tol, axis=-1)


def token_mask(rgb: np.ndarray, names: list[str], tol: int = TOL) -> np.ndarray:
    """Hợp mặt nạ của nhiều token (ví dụ blue+blueDark)."""
    mask = np.zeros(rgb.shape[:2], dtype=bool)
    for name in names:
        for ref in TOKENS[name]:
            mask |= near(rgb, ref, tol)
    return mask


def flat_mask(rgb: np.ndarray) -> np.ndarray:
    """Điểm có cả 8 lân cận chênh ≤ FLAT_TOL mỗi kênh so với nó."""
    ok = np.ones(rgb.shape[:2], dtype=bool)
    for c in range(3):
        ch = rgb[..., c]
        hi = maximum_filter(ch, size=3, mode="nearest")
        lo = minimum_filter(ch, size=3, mode="nearest")
        ok &= (hi - ch <= FLAT_TOL) & (ch - lo <= FLAT_TOL)
    return ok


def check_palette(rgb: np.ndarray) -> dict:
    """Trả về {pass, flat_share, gray_share, raised_black_px, offenders:[{rgb, share}]}."""
    total = rgb.shape[0] * rgb.shape[1]
    flat = flat_mask(rgb)
    on_token = token_mask(rgb, list(TOKENS))
    odd = flat & ~on_token
    offenders = []
    if odd.any():
        vals = rgb[odd]
        q = (vals // BIN).astype(np.int32)
        keys = q[:, 0] * 10000 + q[:, 1] * 100 + q[:, 2]
        uniq, counts = np.unique(keys, return_counts=True)
        for key, cnt in zip(uniq, counts):
            if cnt / total > BIG_SHARE:
                sel = vals[keys == key]
                mean = [int(round(v)) for v in sel.mean(axis=0)]
                offenders.append({"rgb": mean, "share": round(float(cnt / total), 4)})
    spread = rgb.max(axis=-1) - rgb.min(axis=-1)
    level = rgb.mean(axis=-1)
    gray = flat & (spread <= GRAY_SPREAD) & (level >= GRAY_RANGE[0]) & (level <= GRAY_RANGE[1])
    gray_share = float(gray.sum() / total)
    raised = int((flat & near(rgb, RAISED_BLACK)).sum())
    reasons = []
    if offenders:
        reasons.append("màu phẳng > 2 % ngoài token: " + ", ".join(f"{o['rgb']} {o['share']:.1%}" for o in offenders))
    if gray_share > GRAY_SHARE:
        reasons.append(f"xám phẳng {gray_share:.2%} > 0,5 %")
    if raised >= RAISED_MIN_PX:
        reasons.append(f"có ≈ #171717 ({raised} điểm)")
    return {
        "pass": not reasons,
        "flat_share": round(float(flat.sum() / total), 4),
        "gray_share": round(gray_share, 5),
        "raised_black_px": raised,
        "offenders": offenders,
        "reasons": reasons,
    }


def check_file(path: Path) -> dict:
    return {"file": str(path), **check_palette(load_rgb(path))}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    as_json = "--json" in args
    files = [Path(a) for a in args if a != "--json"]
    if not files:
        print("Cách dùng: palette.py <png…> [--json]", file=sys.stderr)
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
            tag = "PASS" if r["pass"] else "FAIL"
            note = "; ".join(r["reasons"]) or f"phẳng {r['flat_share']:.1%}, xám {r['gray_share']:.2%}"
            print(f"{tag} palette {r['file']} {note}")
        fails = sum(1 for r in results if not r["pass"])
        print(f"TỔNG: {len(results) - fails} PASS, {fails} FAIL")
    return 1 if any(not r["pass"] for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
