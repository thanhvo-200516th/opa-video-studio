"""Tự tổng hợp tiếng click chuột (nhấn + nhả) cho cảnh bấm nút; không dùng file âm ngoài.

Nhấn: nhiễu lọc dải 2,5–7 kHz tắt rất nhanh + "tóc" thấp 320 Hz tắt dần; nhả: lớp nhỏ hơn sau 70 ms.
Định dạng giống bộ OPA của V2: WAV PCM 16-bit mono 48 kHz, đệm 0,2 s trước đỉnh, đỉnh −1 dBFS, seed cố định.
Chạy: python -I tools/sfx_click.py  → assets/sfx/click-chuot.wav
"""
import wave
from pathlib import Path

import numpy as np

SR, PRE, TAIL = 48000, 0.2, 0.3
OUT = Path(__file__).resolve().parents[1] / "assets" / "sfx" / "click-chuot.wav"


def band_noise(rng: np.random.Generator, n: int, lo: float, hi: float) -> np.ndarray:
    spec = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    spec[(f < lo) | (f > hi)] = 0
    x = np.fft.irfft(spec, n)
    return x / (np.abs(x).max() + 1e-9)


def hit(rng: np.random.Generator, gain: float) -> np.ndarray:
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    snap = band_noise(rng, n, 2500, 7000) * np.exp(-t / 0.0035)
    thock = np.sin(2 * np.pi * 320 * t) * np.exp(-t / 0.012) * 0.55
    env = np.minimum(1, t / 0.0004)
    return gain * env * (snap + thock)


def main() -> None:
    rng = np.random.default_rng(20261021)
    total = int((PRE + 0.07 + TAIL) * SR)
    y = np.zeros(total)
    a, b = int(PRE * SR), int((PRE + 0.07) * SR)
    press, release = hit(rng, 1.0), hit(rng, 0.45)
    y[a:a + len(press)] += press
    y[b:b + len(release)] += release
    y *= 10 ** (-1 / 20) / np.abs(y).max()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUT), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((y * 32767).astype("<i2").tobytes())
    print("OK", OUT.name, f"{total / SR:.2f} s, đỉnh nhấn ở {PRE:.2f} s")


if __name__ == "__main__":
    main()
