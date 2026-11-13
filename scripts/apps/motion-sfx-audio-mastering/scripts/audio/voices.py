"""Nhạc cụ tổng hợp cho nhạc V2 (TK §7.1, KH §3.9). Mảng float64 mono, chưa chuẩn hóa mức.

Giới hạn cứng: pad mọi nốt ≥ MIDI 48; brass không nốt dưới E3, ≤ 2 saw/giọng, không glide, không vibrato;
bass chỉ B1–A2. Không supersaw (≥ 3 saw lệch tông một giọng).
"""
from __future__ import annotations

import numpy as np

import dsp
from dsp import SR

PAD_MIN_MIDI = 48          # C3
BRASS_MIN_MIDI = 52        # E3
BASS_RANGE = (35, 45)      # B1..A2
BRASS_RELEASE_S = 0.15     # nhả sau gate mỗi nốt brass


def _n(dur_s: float) -> int:
    return int(round(dur_s * SR))


def _cents(c: float) -> float:
    return 2.0 ** (c / 1200.0)


def _saw_offset(f: float, n: int, rng: np.random.Generator) -> np.ndarray:
    """Saw tần số cố định, pha đầu ngẫu nhiên theo seed (bỏ k mẫu đầu)."""
    k = int(rng.integers(0, max(1, int(SR / f))))
    return dsp.osc_saw(f, n + k)[k:]


def pad(notes: list[str], n: int, cutoff_hz, seed: str) -> np.ndarray:
    """2 saw ±6 cent mỗi nốt, LP bậc 2 (cutoff số hoặc mảng dài n), attack 250 ms."""
    for name in notes:
        if dsp.midi(name) < PAD_MIN_MIDI:
            raise ValueError(f"pad: nốt {name} dưới MIDI {PAD_MIN_MIDI}")
    rng = dsp.rng_for(seed)
    x = np.zeros(n)
    for name in notes:
        f = dsp.hz(name)
        for c in (-6.0, 6.0):
            x += _saw_offset(f * _cents(c), n, rng)
    x /= max(1, 2 * len(notes))
    if np.ndim(cutoff_hz) == 0:
        y = dsp.lp(x, float(cutoff_hz), order=2)
    else:
        y = dsp.filter_curve(x, cutoff_hz, "low")
    att = np.minimum(np.arange(n) / (0.25 * SR), 1.0)
    return y * att


def pulse(note: str, dur_s: float, seed: str) -> np.ndarray:
    """1 saw + square thấp 1 bát độ −10 dB; LP bao 2 kHz → 600 Hz (decay 120 ms)."""
    n = _n(dur_s)
    rng = dsp.rng_for(seed)
    f = dsp.hz(note)
    x = _saw_offset(f, n, rng) + 10 ** (-10 / 20) * dsp.osc_square(f / 2, n)
    y = dsp.lp_env(x, 2000.0, 2000.0, 0.0, 0.12, 600.0)
    gate = max(dur_s - 0.015, 0.003)
    return y * dsp.env_adsr(n, 0.003, 0.12, 0.7, 0.015, gate) * 0.7


def bass(note: str, dur_s: float) -> np.ndarray:
    """sine + 0,35·H2 + 0,2·H3, tanh 1,5, + phone layer bp 120–600 Hz. Chỉ B1–A2."""
    m = dsp.midi(note)
    if not BASS_RANGE[0] <= m <= BASS_RANGE[1]:
        raise ValueError(f"bass: nốt {note} ngoài B1–A2")
    n = _n(dur_s)
    f = dsp.hz(note)
    x = dsp.osc_sine(f, n) + 0.35 * dsp.osc_sine(2 * f, n) + 0.2 * dsp.osc_sine(3 * f, n)
    x = dsp.softclip(x * 0.65, 1.5)
    x = x + dsp.phone_layer(x, lo=120.0, hi=600.0, gain=0.35)
    gate = max(dur_s - 0.02, 0.005)
    return x * dsp.env_adsr(n, 0.005, 0.2, 0.85, 0.02, gate) * 0.8


def kick_soft(root_hz: float = 55.0) -> np.ndarray:
    """Sine 2,5·root → root (τ 25 ms), decay 280 ms, click bp 3 kHz 4 ms, phone layer."""
    n = _n(0.36)
    body = dsp.osc_sine(dsp.glide_exp(2.5 * root_hz, root_hz, 0.025, n), n) * dsp.env_ad(n, 0.001, 0.28)
    click = dsp.bp(dsp.noise_white(n, "kick-soft"), 2400.0, 3800.0) * dsp.env_ad(n, 0.0003, 0.004) * 0.25
    x = body + click + dsp.phone_layer(body, gain=0.45)
    return dsp.fade_edges(x, 0.0, 10.0) * 0.9


def hat(seed: str) -> np.ndarray:
    """Nhiễu HP 7 kHz, decay 25 ms, −18 dB."""
    n = _n(0.06)
    x = dsp.hp(dsp.noise_white(n, seed), 7000.0) * dsp.env_ad(n, 0.0005, 0.025)
    return dsp.peak_norm(dsp.fade_edges(x, 0.0, 5.0), -18.0)


def snap(seed: str) -> np.ndarray:
    """Nhiễu bp 1,2–4 kHz decay 70 ms + sine 190 Hz decay 40 ms (thay clap)."""
    n = _n(0.12)
    nz = dsp.bp(dsp.noise_white(n, seed), 1200.0, 4000.0) * dsp.env_ad(n, 0.001, 0.07)
    tone = dsp.osc_sine(190.0, n) * dsp.env_ad(n, 0.001, 0.04)
    return dsp.fade_edges(dsp.peak_norm(nz + 0.6 * tone, -6.0), 0.0, 8.0)


def pluck(note: str, seed: str) -> np.ndarray:
    """Saw lọc 2 kHz, decay 250 ms (motif ô 2)."""
    n = _n(0.4)
    x = dsp.lp(_saw_offset(dsp.hz(note), n, dsp.rng_for(seed)), 2000.0, order=2)
    return dsp.fade_edges(x * dsp.env_ad(n, 0.002, 0.25), 0.0, 10.0) * 0.8


def _brass_voice(f: float, start: int, gate: int, attack_s: float, total: int, rng) -> np.ndarray:
    """Một giọng brass: 2 saw ±4 cent + square −1 bát độ −12 dB, LP bao, tanh 1,5."""
    n = gate + _n(BRASS_RELEASE_S)
    x = (_saw_offset(f * _cents(-4), n, rng) + _saw_offset(f * _cents(4), n, rng)) / 2
    x = x + 10 ** (-12 / 20) * dsp.osc_square(f / 2, n)
    x = dsp.lp_env(x, 500.0, 2400.0, 0.07, 0.4, 1200.0)
    x = dsp.softclip(x * dsp.env_adsr(n, attack_s, 0.3, 0.85, BRASS_RELEASE_S, gate / SR), 1.5)
    out = np.zeros(total)
    end = min(total, start + n)
    out[start:end] = x[:end - start]
    return out


def brass(notes: list[tuple[str, float, float]], attack_s: float = 0.07, seed: str = "brass") -> np.ndarray:
    """Synth brass mềm. notes = [(tên, bắt đầu s, dài gate s)]. Mảng dài max(bắt đầu + dài) + 0,15 s nhả.

    Mỗi nốt có LP bao 500 → 2400 Hz (attack 70 ms, decay 400 ms về 1200 Hz) tính từ lúc nốt bắt đầu.
    Nốt dưới E3 → ValueError. Tổng các giọng × 0,5 (chưa chuẩn hóa).
    """
    if not notes:
        raise ValueError("brass: danh sách nốt rỗng")
    for name, start, dur in notes:
        if dsp.midi(name) < BRASS_MIN_MIDI:
            raise ValueError(f"brass: nốt {name} dưới E3")
        if start < 0 or dur <= 0:
            raise ValueError(f"brass: nốt {name} có thời điểm/độ dài không hợp lệ")
    total = _n(max(s + d for _, s, d in notes) + BRASS_RELEASE_S)
    rng = dsp.rng_for(seed)
    out = np.zeros(total)
    for name, start, dur in notes:
        out += _brass_voice(dsp.hz(name), _n(start), _n(dur), attack_s, total, rng)
    return out * 0.5
