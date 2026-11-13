"""Cắt vùng chân Bò (theo mặt nạ) từ các ảnh tĩnh để soát bóng tiếp xúc và mép khối ở độ phân giải gốc.

  python -I tools/film3d/crop_base.py <thư mục có <id>.png + <id>.mask.png> <ảnh ra> [id ...]
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image


def crop_base(folder: Path, fid: str, w: int = 720, h: int = 320) -> Image.Image:
    img = Image.open(folder / f"{fid}.png").convert("RGB")
    mask = np.asarray(Image.open(folder / f"{fid}.mask.png").convert("RGB"))[..., 0] > 128
    ys, xs = np.nonzero(mask)
    cx, by = int(xs.mean()), int(ys.max())
    left = min(max(cx - w // 2, 0), img.width - w)
    top = min(max(by - h + 90, 0), img.height - h)
    return img.crop((left, top, left + w, top + h))


def main(argv: list[str]) -> int:
    folder, out = Path(argv[1]), Path(argv[2])
    ids = argv[3:] or sorted(p.name[: -len(".mask.png")] for p in folder.glob("*.mask.png"))
    tiles = [crop_base(folder, i) for i in ids]
    sheet = Image.new("RGB", (tiles[0].width, sum(t.height + 6 for t in tiles)), (255, 255, 255))
    y = 0
    for t in tiles:
        sheet.paste(t, (0, y)); y += t.height + 6
    sheet.save(out)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
