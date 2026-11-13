#!/usr/bin/env python3
"""Contact sheet cho MP4 test 16:9 (NN §8.5 bước 6): một ô mỗi `--every` giây (mặc định 0,5 s = 1 phách),
ô 480×270, nhãn "t = giây toàn phim · f60".

Chạy:  python tools/v2w/contact.py <mp4> --t0 7.5 [--every 0.5] [--cols 4] --out <png>
Exit:  0 xong, 2 lỗi đầu vào / ffmpeg.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scan_video import InputError, _exe, probe  # noqa: E402

TILE_W, TILE_H, LABEL_H = 480, 270, 28


def grab(video: Path, frames: list[int]) -> list[np.ndarray]:
    """Lấy đúng các frame chỉ số `frames` (đã sắp) ở cỡ ô, RGB."""
    expr = "+".join(f"eq(n\\,{f})" for f in frames)
    cmd = [_exe("ffmpeg"), "-v", "error", "-i", str(video), "-vf", f"select={expr},scale={TILE_W}:{TILE_H}:flags=area",
           "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        raise InputError(f"ffmpeg lỗi: {r.stderr.decode('utf-8', 'replace')[-400:]}")
    size = TILE_W * TILE_H * 3
    return [np.frombuffer(r.stdout[i * size:(i + 1) * size], np.uint8).reshape(TILE_H, TILE_W, 3)
            for i in range(len(r.stdout) // size)]


def sheet(video: Path, t0: float, every: float, cols: int, out: Path) -> Path:
    info = probe(video)
    fps = info["fps"]
    count = int(subprocess.run([_exe("ffprobe"), "-v", "error", "-count_frames", "-select_streams", "v:0",
                                "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(video)],
                               capture_output=True, text=True).stdout.strip() or 0)
    if count <= 0:
        raise InputError(f"không đọc được số frame của {video}")
    step = max(1, round(every * fps))
    frames = list(range(0, count, step))
    tiles = grab(video, frames)
    rows = (len(tiles) + cols - 1) // cols
    img = Image.new("RGB", (cols * TILE_W, rows * (TILE_H + LABEL_H)), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=18)
    for k, (f, tile) in enumerate(zip(frames, tiles)):
        x, y = (k % cols) * TILE_W, (k // cols) * (TILE_H + LABEL_H)
        img.paste(Image.fromarray(tile), (x, y + LABEL_H))
        t = t0 + f / fps
        draw.text((x + 8, y + 4), f"t = {t:.3f} s · f60 {round(t * 60)}", fill=(10, 10, 10), font=font)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Contact sheet MP4 test 16:9")
    ap.add_argument("video", type=Path)
    ap.add_argument("--t0", type=float, default=0.0)
    ap.add_argument("--every", type=float, default=0.5)
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    try:
        if not a.video.is_file():
            raise InputError(f"không có file {a.video}")
        print(f"OK {sheet(a.video, a.t0, a.every, a.cols, a.out)}")
    except InputError as e:
        print(f"LỖI: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
