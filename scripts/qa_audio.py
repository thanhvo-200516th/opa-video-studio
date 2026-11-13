"""Xuất bản trộn âm thanh (WAV) của một .fcproj rồi đo loudness / true peak — file kiểm, không phải bản giao.

    python3 qa_audio.py PROJECT.fcproj OUT.wav        # in: I (LUFS), LRA, true peak; đạt khi −16…−14 LUFS, TP ≤ −1,5
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

_SIB = Path(__file__).resolve().parents[1] / "scripts/apps/craft-handoff/tools"
sys.path.insert(0, str(_SIB))
from craftctl import Craft  # noqa: E402

PRESET = "Waveform Audio 48 kHz 24-bit"


def loudness(wav: Path) -> dict:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(wav), "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    summary = err[err.rfind("Summary:"):]
    get = lambda key: float(re.search(rf"{key}:\s+(-?[\d.]+|-inf)", summary).group(1))  # noqa: E731
    return {"I": get("I"), "LRA": get("LRA"), "TP": get("Peak")}


def main() -> int:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    project, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    with tempfile.TemporaryDirectory() as wd, Craft("filmcraft", Path(wd)) as fc:
        fc.cmd("file.open", {"path": str(project)})
        fc.cmd("export.quick", {"preset": PRESET, "path": str(out), "wait": True})
    m = loudness(out)
    ok = -16.0 <= m["I"] <= -14.0 and m["TP"] <= -1.5
    print(f"{out}  I {m['I']:.1f} LUFS · LRA {m['LRA']:.1f} LU · true peak {m['TP']:.1f} dBTP → {'ĐẠT' if ok else 'CHƯA ĐẠT'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
