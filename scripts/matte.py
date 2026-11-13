#!/usr/bin/env python3
"""matte — tách nền người nói sang ProRes 4444 Alpha (làm Text Behind Subject) bằng rvm-matte.

    python3 matte.py --input VIDEO --output OUT.mov [--downsample 0.25] [--start GIÂY] [--dur GIÂY]

`--start` / `--dur`: chỉ tách đoạn cần (cắt ra file tạm X264_HQ rồi mới rvm-matte); nên chạy trên media ĐÃ tăng tốc
(media/x110), độ dài .mov ra = `--dur`.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

HOME = Path.home()


def run_cmd(cmd, check=True):
    print(f"▶ Thực thi: {' '.join(str(c) for c in cmd)}")
    return subprocess.run([str(c) for c in cmd], check=check)


def cmd_matte(args):
    rvm_bin = HOME / ".local" / "bin" / "rvm-matte"
    # rvm-matte lỗi khi nhận đường dẫn tương đối (đo 2026-11-01) → luôn truyền đường dẫn tuyệt đối
    src = Path(args.input).resolve()
    if args.start is None and args.dur is None:
        return run_cmd([rvm_bin, src, Path(args.output).resolve(), str(args.downsample)]).returncode
    from build_kit import AAC_HQ, X264_HQ     # chỉ cần khi cắt đoạn
    with tempfile.TemporaryDirectory() as tmp:
        part = Path(tmp) / "doan.mp4"
        trim = ["-ss", str(args.start)] if args.start is not None else []
        trim += ["-t", str(args.dur)] if args.dur is not None else []
        run_cmd(["ffmpeg", "-y", "-v", "error", "-nostdin", *trim, "-i", src, "-map", "0:v:0", "-map", "0:a?", *X264_HQ, *AAC_HQ, part])
        return run_cmd([rvm_bin, part, Path(args.output).resolve(), str(args.downsample)]).returncode


def main():
    parser = argparse.ArgumentParser(description="Tách nền người nói sang ProRes 4444 Alpha (làm Text Behind Subject)")
    parser.add_argument("--input", required=True, help="Video đầu vào")
    parser.add_argument("--output", required=True, help="File .mov ProRes 4444 đầu ra")
    parser.add_argument("--downsample", type=float, default=0.25, help="Tỉ lệ downsample (0.25 cho 1080p)")
    parser.add_argument("--start", type=float, default=None, help="Giây bắt đầu đoạn cần tách (mặc định từ đầu)")
    parser.add_argument("--dur", type=float, default=None, help="Độ dài đoạn cần tách, giây (mặc định tới hết)")
    sys.exit(cmd_matte(parser.parse_args()))


if __name__ == "__main__":
    main()
