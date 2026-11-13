"""Lọc biến thiên theo khối, mang trạng thái zi qua khối (phần tách của dsp.py; dùng qua `import dsp`).

Port sweep_filter từ $WORK/sound-research/synth.py; hệ số biquad tính vector hóa (RBJ, Q = 1/√2).
"""
from __future__ import annotations

import numpy as np
from scipy.signal import sosfilt

SR = 48000


def _freq_arr(freq, n: int) -> np.ndarray:
    f = np.asarray(freq, dtype=np.float64)
    if f.ndim == 0:
        return np.full(n, float(f))
    if len(f) != n:
        raise ValueError(f"mảng tần số dài {len(f)} khác n = {n}")
    return f

def _biquad_sos(fc: np.ndarray, kind: str) -> np.ndarray:
    """Hệ số biquad Butterworth bậc 2 (RBJ, Q = 1/√2) cho mảng fc → (m, 6)."""
    w0 = 2 * np.pi * np.clip(fc, 20.0, 0.45 * SR) / SR
    c, al = np.cos(w0), np.sin(w0) / np.sqrt(2.0)
    a0 = 1 + al
    if kind == "low":
        b = np.stack([(1 - c) / 2, 1 - c, (1 - c) / 2], axis=1)
    else:
        b = np.stack([(1 + c) / 2, -(1 + c), (1 + c) / 2], axis=1)
    a = np.stack([a0, -2 * c, 1 - al], axis=1)
    return np.concatenate([b / a0[:, None], a / a0[:, None]], axis=1)


def _block_filter(x, fc_blocks: np.ndarray, kind: str, q_oct: float, block: int) -> np.ndarray:
    """Lọc từng khối với fc riêng; trạng thái zi mang qua khối (không zipper)."""
    x = np.asarray(x, dtype=np.float64)
    if kind == "band":
        lo, hi = fc_blocks * 2 ** (-q_oct / 2), fc_blocks * 2 ** (q_oct / 2)
        sos = np.stack([_biquad_sos(lo, "high"), _biquad_sos(hi, "low")], axis=1)
    elif kind in ("low", "high"):
        sos = _biquad_sos(fc_blocks, kind)[:, None, :]
    else:
        raise ValueError(f"kind lọc không hợp lệ: {kind!r}")
    y = np.empty_like(x)
    zi = np.zeros((sos.shape[1], 2))
    for k, i in enumerate(range(0, len(x), block)):
        y[i:i + block], zi = sosfilt(sos[k], x[i:i + block], zi=zi)
    return y


def sweep_filter(x, f_points: list[float], t_points: list[float], kind: str = "band",
                 q_oct: float = 1.0, block: int = 64) -> np.ndarray:
    """Tần số nội suy mũ qua các điểm (t theo tỉ lệ 0..1 độ dài); kind band/low/high."""
    n = len(x)
    centers = (np.arange(0, n, block) + block / 2) / max(n, 1)
    fc = np.exp(np.interp(centers, t_points, np.log(np.asarray(f_points, dtype=np.float64))))
    return _block_filter(x, fc, kind, q_oct, block)


def filter_curve(x, fc, kind: str = "low", q_oct: float = 1.0, block: int = 64) -> np.ndarray:
    """Lọc theo đường fc mỗi mẫu (mảng dài len(x)); lấy fc ở đầu mỗi khối."""
    fc = _freq_arr(fc, len(x))
    return _block_filter(x, fc[::block].copy(), kind, q_oct, block)


def lp_env(x, f_start: float, f_peak: float, attack_s: float, decay_s: float, f_sustain: float,
           block: int = 64) -> np.ndarray:
    """LP bậc 2 có đường bao: f_start → f_peak (attack, mũ), rồi về f_sustain (gần hết ở decay_s)."""
    t = np.arange(0, len(x), block) / SR
    a = max(attack_s, 1e-6)
    up = np.log(f_start) + (np.log(f_peak) - np.log(f_start)) * np.clip(t / a, 0, 1)
    down = np.log(f_sustain) + (np.log(f_peak) - np.log(f_sustain)) * np.exp(-4.0 * (t - a) / max(decay_s, 1e-6))
    fc = np.exp(np.where(t < a, up, down))
    return _block_filter(x, fc, "low", 1.0, block)
