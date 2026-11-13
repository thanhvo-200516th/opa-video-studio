#!/usr/bin/env python3
"""Dò điểm ảnh theo token (KH §3.10, §3.12).

Chạy:
  python tools/qa/probe.py <png> <spec>… [--same <png1> <png2> x0,y0,x1,y1]…
Spec:
  x,y=token                     điểm (x, y) trong ±4 mỗi kênh của token
  x0,y0,x1,y1=token:ge:N        số điểm trong ±4 của token, vùng nửa mở [x0,x1)×[y0,y1), ≥ N
  x0,y0,x1,y1=token:le:N        như trên, ≤ N
  token có thể là hợp `a+b` (đếm tổng). Token: blue, black, white, blueLight, blueDark.
  --same p1 p2 x0,y0,x1,y1      mọi điểm trong vùng chênh ≤ 2 mỗi kênh
Không dùng `>=` `<=` `|`: cmd.exe hiểu là chuyển hướng / ống.
Ảnh có alpha < 255 trong vùng dò → FAIL "ảnh trong suốt".
Exit: 0 đạt, 1 có FAIL, 2 lỗi đầu vào.
"""
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from palette import TOKENS, token_mask

SAME_TOL = 2
ALPHA_MSG = "ảnh trong suốt: thiếu nền (Background chưa vẽ?)"
POINT_RE = re.compile(r"^(\d+),(\d+)=([A-Za-z+]+)$")
BOX_RE = re.compile(r"^(\d+),(\d+),(\d+),(\d+)=([A-Za-z+]+):(ge|le):(\d+)$")
RECT_RE = re.compile(r"^(\d+),(\d+),(\d+),(\d+)$")


class SpecError(ValueError):
    """Spec sai cú pháp hoặc ra ngoài ảnh (exit 2)."""


@dataclass(frozen=True)
class Result:
    ok: bool
    text: str


def load_rgba(path: Path) -> np.ndarray:
    if not path.is_file():
        raise SpecError(f"thiếu file: {path}")
    with Image.open(path) as im:
        return np.asarray(im.convert("RGBA"), dtype=np.int16)


def parse_tokens(raw: str) -> list[str]:
    names = raw.split("+")
    bad = [n for n in names if n not in TOKENS]
    if bad:
        raise SpecError(f"token lạ: {', '.join(bad)} (có: {', '.join(TOKENS)})")
    return names


def check_box(img: np.ndarray, x0: int, y0: int, x1: int, y1: int) -> np.ndarray:
    h, w = img.shape[:2]
    if not (0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h):
        raise SpecError(f"vùng {x0},{y0},{x1},{y1} ngoài ảnh {w}×{h}")
    return img[y0:y1, x0:x1]


def has_alpha(region: np.ndarray) -> bool:
    return bool((region[..., 3] < 255).any())


def probe_spec(img: np.ndarray, name: str, spec: str) -> Result:
    """Kiểm một spec trên ảnh RGBA đã đọc."""
    m = POINT_RE.match(spec)
    if m:
        x, y = int(m[1]), int(m[2])
        region = check_box(img, x, y, x + 1, y + 1)
        if has_alpha(region):
            return Result(False, f"FAIL {name} {spec} {ALPHA_MSG}")
        rgb = region[..., :3]
        ok = bool(token_mask(rgb, parse_tokens(m[3])).all())
        px = tuple(int(v) for v in rgb[0, 0])
        return Result(ok, f"{'PASS' if ok else 'FAIL'} {name} {spec} rgb={px}")
    m = BOX_RE.match(spec)
    if m:
        x0, y0, x1, y1 = (int(m[i]) for i in range(1, 5))
        region = check_box(img, x0, y0, x1, y1)
        if has_alpha(region):
            return Result(False, f"FAIL {name} {spec} {ALPHA_MSG}")
        count = int(token_mask(region[..., :3], parse_tokens(m[5])).sum())
        limit = int(m[7])
        ok = count >= limit if m[6] == "ge" else count <= limit
        return Result(ok, f"{'PASS' if ok else 'FAIL'} {name} {spec} đếm={count}")
    raise SpecError(f"spec sai cú pháp: {spec!r} (dạng x,y=token | x0,y0,x1,y1=token:ge:N | …:le:N)")


def probe_same(p1: Path, p2: Path, rect: str) -> Result:
    m = RECT_RE.match(rect)
    if not m:
        raise SpecError(f"vùng --same sai cú pháp: {rect!r}")
    x0, y0, x1, y1 = (int(m[i]) for i in range(1, 5))
    a = check_box(load_rgba(p1), x0, y0, x1, y1)
    b = check_box(load_rgba(p2), x0, y0, x1, y1)
    label = f"--same {p1.name} {p2.name} {rect}"
    if has_alpha(a) or has_alpha(b):
        return Result(False, f"FAIL {label} {ALPHA_MSG}")
    diff = np.abs(a[..., :3] - b[..., :3])
    worst = int(diff.max())
    n_bad = int((diff.max(axis=-1) > SAME_TOL).sum())
    ok = worst <= SAME_TOL
    return Result(ok, f"{'PASS' if ok else 'FAIL'} {label} chênh max={worst} số điểm > {SAME_TOL}: {n_bad}")


def run(argv: list[str]) -> list[Result]:
    """Chạy toàn bộ dòng lệnh; ném SpecError khi đầu vào sai."""
    results: list[Result] = []
    img = None
    name = ""
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--same":
            if len(argv) - i < 4:
                raise SpecError("--same cần <png1> <png2> x0,y0,x1,y1")
            results.append(probe_same(Path(argv[i + 1]), Path(argv[i + 2]), argv[i + 3]))
            i += 4
            continue
        if "=" not in arg:
            img = load_rgba(Path(arg))
            name = Path(arg).name
        elif img is None:
            raise SpecError(f"spec {arg!r} đứng trước tên ảnh")
        else:
            results.append(probe_spec(img, name, arg))
        i += 1
    if not results:
        raise SpecError("không có spec nào")
    return results


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        results = run(sys.argv[1:])
    except SpecError as e:
        print(f"LỖI: {e}", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        return 2
    for r in results:
        print(r.text)
    fails = sum(1 for r in results if not r.ok)
    print(f"TỔNG: {len(results) - fails} PASS, {fails} FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
