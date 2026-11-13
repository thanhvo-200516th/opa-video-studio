"""Dựng từng lớp nhạc V2 thành mảng dài n mẫu (phần tách của score_v2.py). Chưa cân mức section.

Nhạc cụ lấy từ voices.py (D1), không chép lại. Vị trí nhận bằng frame (float), đổi mẫu bằng dsp.f2s.
"""
from __future__ import annotations

import numpy as np

import dsp
import voices
from dsp import SR

PAD_RELEASE_S = 0.3          # nhả mỗi nốt pad (chồng lên attack 250 ms của nốt sau)
PAD_NOTE_GAIN = 0.35
SC_DEPTH, SC_TAU_S, SC_ATTACK_S = 0.55, 0.14, 0.004   # sidechain từ kick (TK §7.1)
BRASS_STAB = ("A3", "C#4", "E4", "B4")                 # A add9, mọi nốt ≥ E3
PULSE_TAIL_S = 0.3


def add_at(buf: np.ndarray, start: int, x: np.ndarray, gain: float = 1.0) -> None:
    """Cộng x vào buf từ mẫu start, cắt ở hai mép (buf là bộ đệm cục bộ của lớp)."""
    a, b = max(start, 0), min(start + len(x), len(buf))
    if b > a:
        buf[a:b] += x[a - start:b - start] * gain


def _cos_out(n: int) -> np.ndarray:
    return 0.5 + 0.5 * np.cos(np.pi * (np.arange(n) + 1) / max(n, 1))


# ---------- pad ----------
def pad_cutoff(n: int, steps: list[tuple[float, float]], ramp_s: float = 0.2) -> np.ndarray:
    """Đường cắt LP của pad: bậc thang (frame bắt đầu, Hz), mỗi bậc trượt mũ trong ramp_s (nhân quả)."""
    logf = np.full(n, np.log(steps[0][1]))
    for f, hz in steps[1:]:
        logf[dsp.f2s(f):] = np.log(hz)
    w = max(1, int(round(ramp_s * SR)))
    c = np.concatenate([[0.0], np.cumsum(np.concatenate([np.full(w, logf[0]), logf]))])
    return np.exp((c[w + 1:] - c[1:-w]) / w)   # trung bình trượt về phía trước: y[i] = mean(logf[i−w+1..i])


def pad_layer(events: list[tuple[str, float, float]], cutoff: np.ndarray, n: int, seed: str) -> np.ndarray:
    """Mỗi nốt một giọng voices.pad (attack 250 ms), nhả cosine PAD_RELEASE_S sau f1."""
    out = np.zeros(n)
    rel = int(round(PAD_RELEASE_S * SR))
    for k, (name, f0, f1) in enumerate(events):
        s0, s1 = dsp.f2s(f0), dsp.f2s(f1)
        m = min(s1 - s0 + rel, n - s0)
        x = voices.pad([name], m, cutoff[s0:s0 + m], f"{seed}:pad:{k}:{name}")
        r = m - (s1 - s0)
        if r > 0:
            x[-r:] *= _cos_out(rel)[:r]
        add_at(out, s0, x, PAD_NOTE_GAIN)
    return out


# ---------- band ----------
def pulse_layer(bars, n: int, seed: str) -> np.ndarray:
    """bars: (onset frame, nốt, bước frame, LP Hz, gain). LP tĩnh theo ô trên bộ đệm ô + đuôi."""
    out = np.zeros(n)
    cache: dict[tuple[str, float], np.ndarray] = {}
    for steps, note, step, lp_hz, gain in bars:
        if not steps:
            continue
        key = (note, step)
        if key not in cache:
            cache[key] = voices.pulse(note, step / dsp.FPS, f"{seed}:pulse:{note}:{step}")
        s0 = dsp.f2s(steps[0])
        buf = np.zeros(dsp.f2s(steps[-1] + step) - s0 + int(PULSE_TAIL_S * SR))
        for k, f in enumerate(steps):
            add_at(buf, dsp.f2s(f) - s0, cache[key], 1.0 if k % 2 == 0 else 0.8)
        add_at(out, s0, dsp.lp(buf, lp_hz, order=2), gain)
    return out


def bass_layer(notes: list[tuple[str, float, float]], n: int) -> np.ndarray:
    """notes: (nốt, onset frame, dài frame)."""
    out = np.zeros(n)
    cache: dict[tuple[str, float], np.ndarray] = {}
    for name, f, dur in notes:
        key = (name, dur)
        if key not in cache:
            cache[key] = voices.bass(name, dur / dsp.FPS)
        add_at(out, dsp.f2s(f), cache[key])
    return out


def hits_layer(clips: list[np.ndarray], hits: list[tuple[float, float]], n: int) -> np.ndarray:
    """Đặt các clip (xoay vòng) tại (onset frame, vận tốc)."""
    out = np.zeros(n)
    for k, (f, v) in enumerate(hits):
        add_at(out, dsp.f2s(f), clips[k % len(clips)], v)
    return out


def pluck_layer(motif: list[tuple[float, str]], n: int, seed: str) -> np.ndarray:
    """Motif pluck ở các mark (frame, nốt)."""
    out = np.zeros(n)
    for k, (f, note) in enumerate(motif):
        add_at(out, dsp.f2s(f), voices.pluck(note, f"{seed}:pluck:{k}"))
    return out


def brass_layer(stabs: list[tuple[float, float]], n: int, seed: str) -> np.ndarray:
    """Brass stab A add9 tại (frame, giây giữ) — brass chỉ vang ở các mark brass-stab."""
    out = np.zeros(n)
    for k, (f, dur_s) in enumerate(stabs):
        x = voices.brass([(nm, 0.0, dur_s) for nm in BRASS_STAB], seed=f"{seed}:brass:{k}")
        add_at(out, dsp.f2s(f), x)
    return out


def sidechain(kicks: list[float], n: int) -> np.ndarray:
    """Hệ số nhân 1 − depth·a(t)·e^(−t/τ) theo kick gần nhất (lấy mức nén sâu nhất); attack 4 ms tránh click."""
    duck = np.zeros(n)
    m = int(round(6 * SC_TAU_S * SR))
    t = np.arange(m) / SR
    shape = SC_DEPTH * np.minimum(t / SC_ATTACK_S, 1.0) * np.exp(-np.maximum(t - SC_ATTACK_S, 0) / SC_TAU_S)
    for f in kicks:
        s = dsp.f2s(f)
        e = min(s + m, n)
        duck[s:e] = np.maximum(duck[s:e], shape[:e - s])
    return 1.0 - duck


# ---------- cửa (gate) và vang bus ----------
def fade_to_zero(n: int, end: int, fade: int) -> np.ndarray:
    """1 trước end − fade, cosine về 0 kết đúng tại end, 0 từ end."""
    g = np.ones(n)
    a = max(end - fade, 0)
    g[a:end] = _cos_out(fade)[fade - (end - a):]
    g[end:] = 0.0
    return g


def bus_wet(send: np.ndarray, segments: list[tuple[int, int, int, int]], ir: np.ndarray, wet: float) -> np.ndarray:
    """Vang bus theo từng đoạn độc lập: (đầu, cuối nguồn, đầu fade đuôi, hết đuôi). Ngoài đoạn = 0 tuyệt đối."""
    n = len(send)
    out = np.zeros(n)
    for a, b, fade_from, tail_end in segments:
        w = dsp.reverb(send[a:b], ir, 1.0)[: tail_end - a] * wet
        if len(w) < tail_end - a:
            w = np.concatenate([w, np.zeros(tail_end - a - len(w))])
        k = fade_from - a
        w[k:] *= _cos_out(len(w) - k)
        out[a:tail_end] += w
    return out
