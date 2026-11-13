#!/usr/bin/env python3
"""master_audio — chuẩn hóa âm lượng EBU R128 2-pass & kiểm định QA.

    python3 master_audio.py --input IN.wav --output OUT.wav [--lufs -14] [--tp -1.5]

Gọi scripts/apps/motion-sfx-audio-mastering/scripts/master.py rồi audio/qa_audio.py.
"""
import argparse
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
SKILL_ROOT = Path(__file__).resolve().parents[1]
MASTERING = SKILL_ROOT / "scripts" / "apps" / "motion-sfx-audio-mastering" / "scripts"
VENV_PY = HOME / ".venvs" / "video-skills" / "bin" / "python"


def run_cmd(cmd, check=True):
    print(f"▶ Thực thi: {' '.join(str(c) for c in cmd)}")
    return subprocess.run([str(c) for c in cmd], check=check)


def cmd_master_audio(args):
    master_script = MASTERING / "master.py"
    qa_script = MASTERING / "audio" / "qa_audio.py"
    run_cmd([
        VENV_PY,
        master_script,
        args.input,
        args.output,
        "--lufs",
        str(args.lufs),
        "--tp",
        str(args.tp),
    ])
    if args.qa and qa_script.exists():
        run_cmd([VENV_PY, qa_script, args.output], check=False)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Chuẩn hóa âm lượng EBU R128 2-pass & kiểm định QA")
    parser.add_argument("--input", required=True, help="File WAV đầu vào")
    parser.add_argument("--output", required=True, help="File WAV đầu ra")
    parser.add_argument("--lufs", type=float, default=-14.0, help="Mức LUFS mục tiêu (-14.0 hoặc -16.0)")
    parser.add_argument("--tp", type=float, default=-1.5, help="Mức True Peak tối đa (-1.5 dBTP)")
    parser.add_argument("--qa", action="store_true", default=True, help="Chạy kiểm định qa_audio.py sau khi master")
    sys.exit(cmd_master_audio(parser.parse_args()))


if __name__ == "__main__":
    main()
