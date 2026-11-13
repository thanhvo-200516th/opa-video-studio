"""Đo loudness BS.1770-4 ở 48 kHz, mono (phần tách của dsp.py; dùng qua `import dsp`)."""
from __future__ import annotations

import numpy as np
from scipy.signal import lfilter

SR = 48000
_SHELF_B = [1.53512485958697, -2.69169618940638, 1.19839281085285]
_SHELF_A = [1.0, -1.69065929318241, 0.73248077421585]
_RLB_B = [1.0, -2.0, 1.0]
_RLB_A = [1.0, -1.99004745483398, 0.99007225036621]
_FLOOR = -200.0  # LUFS cho cửa sổ im lặng tuyệt đối


def k_weight(x) -> np.ndarray:
    """Lọc K (shelf + RLB)."""
    return lfilter(_RLB_B, _RLB_A, lfilter(_SHELF_B, _SHELF_A, np.asarray(x, dtype=np.float64)))


def _window_power(x, win: int, hop: int) -> np.ndarray:
    """Công suất trung bình K-weighted của các cửa sổ [i, i + win), bước hop; ngắn hơn win thì đệm 0."""
    z = k_weight(x) ** 2
    if len(z) < win:
        z = np.concatenate([z, np.zeros(win - len(z))])
    c = np.concatenate([[0.0], np.cumsum(z)])
    starts = np.arange(0, len(z) - win + 1, hop)
    return (c[starts + win] - c[starts]) / win


def _lufs(p) -> np.ndarray:
    p = np.asarray(p, dtype=np.float64)
    return np.where(p > 0, -0.691 + 10 * np.log10(np.maximum(p, 1e-30)), _FLOOR)


def lufs_integrated(x) -> float:
    """Loudness tích hợp: khối 400 ms chồng 75 %, cổng tuyệt đối −70, cổng tương đối −10."""
    p = _window_power(x, int(0.4 * SR), int(0.1 * SR))
    l_ = _lufs(p)
    g = p[l_ > -70.0]
    if len(g) == 0:
        return float(_FLOOR)
    rel = float(_lufs(np.mean(g))) - 10.0
    g2 = p[(l_ > -70.0) & (l_ > rel)]
    return float(_lufs(np.mean(g2))) if len(g2) else float(_FLOOR)


def momentary_max(x) -> float:
    """Momentary max: cửa sổ 400 ms, bước 10 ms."""
    return float(np.max(_lufs(_window_power(x, int(0.4 * SR), int(0.01 * SR)))))


def short_term(x, hop_s: float = 0.1) -> np.ndarray:
    """Short-term: cửa sổ 3 s, bước hop_s; phần tử k ứng cửa sổ bắt đầu ở k·hop_s."""
    return _lufs(_window_power(x, 3 * SR, max(1, int(round(hop_s * SR)))))
