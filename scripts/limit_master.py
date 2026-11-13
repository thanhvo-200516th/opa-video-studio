#!/usr/bin/env python3
"""limit_master — gắn hoặc cập nhật hard_limiter vào kênh master (strip "Mix") của .fcproj.

Để bản trộn không vượt true peak (mặc định −2,2 dB để đảm bảo inter-sample True Peak luôn <= -1.5 dBTP).
Sửa trực tiếp JSON trong < 0.05s, dùng hàm main() của fc_fast_patch.py.

    python3 limit_master.py PROJECT.fcproj [--max -2.2]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fc_fast_patch  # noqa: E402


def cmd_limit_master(args):
    sys.argv = ["fc_fast_patch.py", str(Path(args.project).resolve()), "--limiter-max", str(args.max)]
    return fc_fast_patch.main()


def main():
    parser = argparse.ArgumentParser(description="Gắn hard_limiter −2,2 dB vào master của project FilmCraft (.fcproj)")
    parser.add_argument("project")
    parser.add_argument("--max", type=float, default=-2.2)
    sys.exit(cmd_limit_master(parser.parse_args()))


if __name__ == "__main__":
    main()
