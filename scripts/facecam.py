#!/usr/bin/env python3
"""facecam — chạy lệnh của FacecamMaxxing (list, track, words, check, render) qua scripts/apps/facecammaxxing/scripts/fcm.py.

    python3 facecam.py list | track … | words … | check … | render …
"""
import argparse
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
SKILL_ROOT = Path(__file__).resolve().parents[1]
APPS = SKILL_ROOT / "scripts" / "apps"
VENV_PY = HOME / ".venvs" / "video-skills" / "bin" / "python"
FCM_PY = APPS / "facecammaxxing" / ".venv" / "bin" / "python"
FCM_SCRIPT = APPS / "facecammaxxing" / "scripts" / "fcm.py"


def run_cmd(cmd, check=True):
    print(f"▶ Thực thi: {' '.join(str(c) for c in cmd)}")
    return subprocess.run([str(c) for c in cmd], check=check)


def cmd_facecam(args):
    py_bin = FCM_PY if FCM_PY.exists() else VENV_PY
    run_cmd([py_bin, FCM_SCRIPT, *args.fcm_args])
    return 0


def main():
    parser = argparse.ArgumentParser(description="Chạy lệnh của FacecamMaxxing (list, track, words, check, render)")
    parser.add_argument("fcm_args", nargs=argparse.REMAINDER, help="Tham số truyền cho fcm.py")
    sys.exit(cmd_facecam(parser.parse_args()))


if __name__ == "__main__":
    main()
