"""Ước cao độ các âm có nốt: 3 đỉnh phổ mạnh nhất trong đoạn ngay sau đỉnh âm, đổi ra tên nốt. cao_do.py file1 file2 ..."""
import subprocess
import sys

import numpy as np
from scipy.signal import find_peaks

SR = 48000
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note(f: float) -> str:
    m = 69 + 12 * np.log2(f / 440.0)
    k = int(round(m))
    return f"{NOTES[k % 12]}{k // 12 - 1}{'+' if m - k > 0.15 else '-' if m - k < -0.15 else ''}"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    for path in sys.argv[1:]:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                             capture_output=True).stdout
        x = np.frombuffer(raw, np.float32).astype(np.float64)
        k = int(np.argmax(np.abs(x)))
        seg = x[k:k + int(0.25 * SR)]
        if len(seg) < 2048:
            seg = np.pad(seg, (0, 2048 - len(seg)))
        spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), n=1 << 16))
        fr = np.fft.rfftfreq(1 << 16, 1 / SR)
        band = (fr > 60) & (fr < 6000)
        pk, _ = find_peaks(spec * band, distance=40)
        top = sorted(pk, key=lambda i: -spec[i])[:4]
        ref = spec[top[0]] if top else 1
        desc = ", ".join(f"{note(fr[i])} {fr[i]:.0f}Hz {20 * np.log10(spec[i] / ref):+.0f}dB" for i in sorted(top, key=lambda i: fr[i]))
        print(f"{path.split('/')[-1][:40]:40s} {desc}")


if __name__ == "__main__":
    main()
