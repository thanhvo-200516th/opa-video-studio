"""Thư viện DSP thuần numpy/scipy cho V2 (KH §3.9, TK §7).

Quy ước: mono float64, SR 48000, 1 frame = 1600 mẫu. Tần số biến thiên luôn tích phân pha.
Không có rng toàn cục: mọi nhiễu lấy từ rng_for(seed).
Đo loudness nằm ở dsp_loud.py, lọc biến thiên theo khối ở dsp_sweep.py; cả hai re-export ở đây.
Port từ $WORK/sound-research/synth.py (sweep_filter giữ zi qua các khối).
"""
from __future__ import annotations

import hashlib
import os
import re

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, lfilter, sosfilt

SR = 48000
FPS = 30
SPF = 1600

_NOTE_RE = re.compile(r"^([A-Ga-g])([#b]?)(-?\d+)$")
_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


# ---------- thời gian, seed, cao độ ----------
def f2s(frame: float) -> int:
    """Frame (có thể lẻ) → chỉ số mẫu."""
    return int(round(frame * SPF))


def rng_for(seed: str) -> np.random.Generator:
    """Generator riêng cho mỗi seed (sha256 → số nguyên)."""
    h = hashlib.sha256(seed.encode("utf-8")).digest()
    return np.random.default_rng(int.from_bytes(h[:8], "big"))


def midi(note: str) -> int:
    """'C3' = 48, 'A4' = 69."""
    m = _NOTE_RE.match(note.strip())
    if not m:
        raise ValueError(f"tên nốt không hợp lệ: {note!r}")
    letter, acc, octave = m.groups()
    pc = _PC[letter.upper()] + (1 if acc == "#" else -1 if acc == "b" else 0)
    return 12 * (int(octave) + 1) + pc


def hz(note: str) -> float:
    """12-TET, A4 = 440 Hz."""
    return 440.0 * 2.0 ** ((midi(note) - 69) / 12.0)


# ---------- dao động ----------
def _freq_arr(freq, n: int) -> np.ndarray:
    f = np.asarray(freq, dtype=np.float64)
    if f.ndim == 0:
        return np.full(n, float(f))
    if len(f) != n:
        raise ValueError(f"mảng tần số dài {len(f)} khác n = {n}")
    return f


def _phase_cycles(freq, n: int) -> np.ndarray:
    """Pha (đơn vị vòng) tích phân từ tần số, mẫu đầu = 0."""
    f = _freq_arr(freq, n)
    ph = np.empty(n)
    if n:
        ph[0] = 0.0
        ph[1:] = np.cumsum(f[:-1]) / SR
    return ph


def osc_sine(freq, n: int, phase0: float = 0.0) -> np.ndarray:
    """Sine, pha = phase0 + 2π·cumsum(f)/SR."""
    return np.sin(phase0 + 2.0 * np.pi * _phase_cycles(freq, n))


def _poly_blep(t: np.ndarray, dt: np.ndarray) -> np.ndarray:
    """Hiệu chỉnh polyBLEP quanh điểm nhảy (t ∈ [0,1))."""
    out = np.zeros_like(t)
    lo = t < dt
    x = t[lo] / dt[lo]
    out[lo] = x + x - x * x - 1.0
    hi = t > 1.0 - dt
    x = (t[hi] - 1.0) / dt[hi]
    out[hi] = x * x + x + x + 1.0
    return out


def osc_saw(freq, n: int) -> np.ndarray:
    """Saw polyBLEP (−1..1)."""
    dt = np.clip(_freq_arr(freq, n) / SR, 1e-9, 0.5)
    t = np.mod(_phase_cycles(freq, n), 1.0)
    return 2.0 * t - 1.0 - _poly_blep(t, dt)


def osc_square(freq, n: int) -> np.ndarray:
    """Square polyBLEP (−1..1), duty 50 %."""
    dt = np.clip(_freq_arr(freq, n) / SR, 1e-9, 0.5)
    t = np.mod(_phase_cycles(freq, n), 1.0)
    naive = np.where(t < 0.5, 1.0, -1.0)
    return naive + _poly_blep(t, dt) - _poly_blep(np.mod(t + 0.5, 1.0), dt)


def glide_exp(f_start: float, f_end: float, tau_s: float, n: int) -> np.ndarray:
    """f(t) = f_end + (f_start − f_end)·e^(−t/τ)."""
    t = np.arange(n) / SR
    return f_end + (f_start - f_end) * np.exp(-t / max(tau_s, 1e-9))


# ---------- đường bao ----------
def env_ad(n: int, attack_s: float, decay_s: float, curve: float = 4.0) -> np.ndarray:
    """Attack tuyến tính, decay mũ: tại attack + decay còn e^(−curve)."""
    t = np.arange(n) / SR
    a = max(attack_s, 1e-6)
    return np.where(t < a, t / a, np.exp(-(t - a) * curve / max(decay_s, 1e-6)))


def env_adsr(n: int, a_s: float, d_s: float, s_level: float, r_s: float, gate_s: float) -> np.ndarray:
    """A tuyến tính → D mũ về s_level → giữ tới gate → R về đúng 0 (cong (1−x)^3)."""
    t = np.arange(n) / SR
    a, d, r = max(a_s, 1e-6), max(d_s, 1e-6), max(r_s, 1e-6)
    k = 1.0 - np.exp(-5.0)
    dec = 1.0 - (1.0 - s_level) * (1.0 - np.exp(-5.0 * np.minimum((t - a) / d, 1.0))) / k
    on = np.where(t < a, t / a, dec)
    # mức tại lúc nhả
    ta = gate_s
    lvl = ta / a if ta < a else 1.0 - (1.0 - s_level) * (1.0 - np.exp(-5.0 * min((ta - a) / d, 1.0))) / k
    x = np.clip((t - gate_s) / r, 0.0, 1.0)
    rel = lvl * (1.0 - x) ** 3
    return np.where(t < gate_s, on, rel)


# ---------- nhiễu ----------
def noise_white(n: int, seed: str) -> np.ndarray:
    return rng_for(seed).standard_normal(n)


def noise_pink(n: int, seed: str) -> np.ndarray:
    """Nhiễu hồng (bộ lọc Paul Kellet 3 cực), chuẩn hóa std = 1."""
    w = noise_white(n + 4800, seed)
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1.0, -2.494956002, 2.017265875, -0.522189400]
    y = lfilter(b, a, w)[4800:]  # bỏ đoạn quá độ đầu
    return y / (np.std(y) + 1e-12)


# ---------- lọc tĩnh ----------
def _nyq_clip(f: float) -> float:
    return float(min(max(f, 1.0), 0.49 * SR))


def lp(x, fc, order=4) -> np.ndarray:
    return sosfilt(butter(order, _nyq_clip(fc), "low", fs=SR, output="sos"), x)


def hp(x, fc, order=4) -> np.ndarray:
    return sosfilt(butter(order, _nyq_clip(fc), "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2) -> np.ndarray:
    return sosfilt(butter(order, [_nyq_clip(lo), _nyq_clip(hi)], "band", fs=SR, output="sos"), x)


def peaking(x, f0: float, gain_db: float, q: float) -> np.ndarray:
    """EQ peaking (RBJ)."""
    a_ = 10 ** (gain_db / 40.0)
    w0 = 2 * np.pi * f0 / SR
    al = np.sin(w0) / (2 * q)
    c = np.cos(w0)
    b = [1 + al * a_, -2 * c, 1 - al * a_]
    a = [1 + al / a_, -2 * c, 1 - al / a_]
    return lfilter(np.array(b) / a[0], np.array(a) / a[0], x)


def low_shelf(x, f0: float, gain_db: float) -> np.ndarray:
    """Low shelf (RBJ, S = 1)."""
    a_ = 10 ** (gain_db / 40.0)
    w0 = 2 * np.pi * f0 / SR
    c, s = np.cos(w0), np.sin(w0)
    al = s / 2 * np.sqrt(2.0)
    sa = 2 * np.sqrt(a_) * al
    b = [a_ * ((a_ + 1) - (a_ - 1) * c + sa), 2 * a_ * ((a_ - 1) - (a_ + 1) * c), a_ * ((a_ + 1) - (a_ - 1) * c - sa)]
    a = [(a_ + 1) + (a_ - 1) * c + sa, -2 * ((a_ - 1) + (a_ + 1) * c), (a_ + 1) + (a_ - 1) * c - sa]
    return lfilter(np.array(b) / a[0], np.array(a) / a[0], x)


# ---------- bão hòa, vang, mép ----------
def softclip(x, drive: float) -> np.ndarray:
    return np.tanh(np.asarray(x) * drive) / np.tanh(drive)


def phone_layer(x, drive=10.0, lo=250.0, hi=2500.0, gain=1.2) -> np.ndarray:
    """Hài bậc cao cho loa điện thoại: tanh(x·drive) → bp lo–hi × gain."""
    return bp(np.tanh(np.asarray(x) * drive), lo, hi) * gain


def reverb_ir(seed: str, dur_s=1.5, decay=3.5, lp_fc=5000.0) -> np.ndarray:
    """IR tự sinh: nhiễu trắng × e^(−decay·t), lọc thấp, năng lượng = 1."""
    n = int(round(dur_s * SR))
    t = np.arange(n) / SR
    ir = lp(noise_white(n, seed) * np.exp(-t * decay), lp_fc)
    ir[0] = 0.0
    ir *= np.linspace(1.0, 0.0, n) ** 0.5  # ép về 0 ở cuối IR
    return ir / np.sqrt(np.sum(ir ** 2) + 1e-20)


def reverb(x, ir, wet: float) -> np.ndarray:
    """dry·(1 − wet) + (x ∗ ir)·wet; dài len(x) + len(ir) − 1 (giữ đuôi)."""
    x = np.asarray(x, dtype=np.float64)
    w = fftconvolve(x, ir)
    dry = np.concatenate([x, np.zeros(len(ir) - 1)])
    return dry * (1.0 - wet) + w * wet


def fade_edges(x, in_ms=3.0, out_ms=10.0) -> np.ndarray:
    """Fade cosine hai đầu; trả bản sao."""
    y = np.array(x, dtype=np.float64, copy=True)
    ni, no = min(int(round(in_ms * SR / 1000)), len(y)), min(int(round(out_ms * SR / 1000)), len(y))
    if ni > 0:
        y[:ni] *= 0.5 - 0.5 * np.cos(np.pi * np.arange(ni) / ni)
    if no > 0:
        y[len(y) - no:] *= 0.5 + 0.5 * np.cos(np.pi * (np.arange(no) + 1) / no)
    return y


def peak_norm(x, peak_dbfs=-1.0) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    return x / (np.max(np.abs(x)) + 1e-20) * 10 ** (peak_dbfs / 20)


def rms_db(x) -> float:
    x = np.asarray(x, dtype=np.float64)
    return float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)) if len(x) else -240.0


# ---------- file ----------
def write_wav_f32(path, x) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(str(path))), exist_ok=True)
    wavfile.write(str(path), SR, np.asarray(x, dtype=np.float32))


def read_wav(path) -> np.ndarray:
    """Đọc WAV → mono float64 (−1..1). SR khác 48 kHz → ValueError."""
    sr, d = wavfile.read(str(path))
    if sr != SR:
        raise ValueError(f"{path}: SR {sr} khác {SR}")
    if d.dtype == np.int16:
        x = d / 32768.0
    elif d.dtype == np.int32:  # scipy đọc 24/32-bit vào int32 căn trái
        x = d / 2147483648.0
    elif d.dtype == np.uint8:
        x = (d.astype(np.float64) - 128.0) / 128.0
    else:
        x = d.astype(np.float64)
    return x.mean(axis=1) if x.ndim == 2 else np.asarray(x, dtype=np.float64)


from dsp_loud import k_weight, lufs_integrated, momentary_max, short_term  # noqa: E402,F401
from dsp_sweep import _biquad_sos, filter_curve, lp_env, sweep_filter  # noqa: E402,F401
