"""SFX V2 theo TK §7.2 và §7.4 (KH §3.9). Mỗi hàm trả Clip mono float64, đỉnh −1 dBFS, seed riêng.

Port từ $WORK/sound-research/{synth.py, impact_v2.py}; đã bỏ hằng 30/32/38 Hz (dùng root_hz),
bỏ LFO của riser, bỏ rng toàn cục. Cấm: braam, Shepard, supersaw, taiko, tape stop, glitch, tiếng bò.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import dsp
import voices
from dsp import FPS, SR

ROOT_HZ = 55.0
PEAK_DBFS = -1.0


@dataclass(frozen=True)
class Clip:
    x: np.ndarray   # mono float64, đỉnh ≤ 1
    anchor: int     # mẫu đặt trùng frame cue (onset = 0, peak = argmax|x|, end = len − 1, manual do hàm khai)


def _n(dur_s: float) -> int:
    return int(round(dur_s * SR))


def _finish(x: np.ndarray, tail_ms: float = 10.0) -> np.ndarray:
    """Chuẩn hóa đỉnh, fade đuôi (đầu giữ nguyên attack)."""
    return dsp.peak_norm(dsp.fade_edges(x, 0.0, tail_ms), PEAK_DBFS)


def _pitch_env_sine(f0: float, semis: float, env_s: float, n: int) -> np.ndarray:
    """Sine bắt đầu cao hơn f0 `semis` bán cung, về f0 sau ≈ env_s (mũ, τ = env_s/3)."""
    t = np.arange(n) / SR
    f = f0 * 2.0 ** (semis * np.exp(-t / (env_s / 3.0)) / 12.0)
    return dsp.osc_sine(f, n)


# ---------- SFX nhỏ ----------
def ping(seed: str, variant: str = "night") -> Clip:
    """Tick trầm, đục: sine A3 hoặc E4 (theo seed), pitch-env +3 bán cung 15 ms, click lp 1,5 kHz 3 ms, decay 150 ms, lp 2 kHz."""
    if variant != "night":
        raise ValueError(f"ping: biến thể không hỗ trợ {variant!r}")
    rng = dsp.rng_for(seed)
    note = ("A3", "E4")[int(rng.integers(0, 2))]
    n = _n(0.3)
    tone = _pitch_env_sine(dsp.hz(note), 3.0, 0.015, n) * dsp.env_ad(n, 0.001, 0.15)
    click = dsp.lp(rng.standard_normal(n), 1500.0) * dsp.env_ad(n, 0.0002, 0.003) * 0.5
    return Clip(_finish(dsp.lp(tone + click, 2000.0), 15.0), 0)


def tick_ui(note: str = "E6", seed: str = "tick-ui") -> Clip:
    """sine AD(0,5 ms; 20 ms) + bp nhiễu 2–6 kHz AD(0,2 ms; 4 ms)·0,4."""
    n = _n(0.06)
    tone = dsp.osc_sine(dsp.hz(note), n) * dsp.env_ad(n, 0.0005, 0.02)
    nz = dsp.bp(dsp.noise_white(n, seed), 2000.0, 6000.0) * dsp.env_ad(n, 0.0002, 0.004) * 0.4
    return Clip(_finish(tone + nz, 5.0), 0)


def tick_catch(note: str = "A4", seed: str = "tick-catch") -> Clip:
    """Một cao độ: pitch-env +2 bán cung 8 ms, click khô, decay ≤ 90 ms (−40 dB trước 90 ms)."""
    n = _n(0.12)
    tone = _pitch_env_sine(dsp.hz(note), 2.0, 0.008, n) * dsp.env_ad(n, 0.0008, 0.06)
    click = dsp.bp(dsp.noise_white(n, seed), 1500.0, 5000.0) * dsp.env_ad(n, 0.0002, 0.003) * 0.3
    return Clip(_finish(tone + click, 10.0), 0)


def thump(seed: str = "thump") -> Clip:
    """Body sine 110 → 55 Hz (τ 25 ms), decay 220 ms, tanh 2, click 8 ms, phone layer ×0,8. Không sub-drop."""
    n = _n(0.4)
    body = dsp.osc_sine(dsp.glide_exp(110.0, 55.0, 0.025, n), n) * dsp.env_ad(n, 0.001, 0.22)
    click = dsp.bp(dsp.noise_white(n, seed), 2000.0, 7000.0) * dsp.env_ad(n, 0.0003, 0.008) * 0.3
    core = dsp.softclip(body, 2.0)
    phone = dsp.phone_layer(body, gain=1.0)
    phone *= 0.8 * np.sqrt(np.mean(core ** 2) / (np.mean(phone ** 2) + 1e-20))  # ×0,8 theo RMS của body
    return Clip(_finish(core + click + phone, 15.0), 0)


def snort(seed: str = "snort") -> Clip:
    """2 xung nhiễu lp ≤ 1,5 kHz, mỗi xung 0,12 s, cách 0,08 s (đầu tới đầu 0,2 s), khô. anchor = đỉnh xung 1."""
    w, gap = _n(0.12), _n(0.08)
    n = 2 * w + gap + _n(0.02)
    rng = dsp.rng_for(seed)
    x = np.zeros(n)
    for k, start in enumerate((0, w + gap)):
        t = np.arange(w) / w
        env = np.sin(np.pi * t ** 0.6) ** 2      # dâng nhanh, tắt êm, = 0 ở hai mép
        nz = dsp.lp(rng.standard_normal(w + 2400), 1000.0, order=6)[2400:]
        x[start:start + w] += nz * env * (1.0 if k == 0 else 0.8)
    x = dsp.peak_norm(x, PEAK_DBFS)
    return Clip(x, int(np.argmax(np.abs(x[:w]))))


# ---------- SFX lớn ----------
def riser(dur_s: float, seed: str = "riser") -> Clip:
    """Nhiễu hồng bp quét mũ 300 → 8000 Hz (mang zi), biên độ p^2,2, không LFO, fade cuối 4 ms. anchor = len − 1."""
    n = _n(dur_s)
    x = dsp.sweep_filter(dsp.noise_pink(n, seed), [300.0, 8000.0], [0.0, 1.0], "band", q_oct=1.5)
    p = np.arange(n) / max(n - 1, 1)
    x = dsp.peak_norm(dsp.fade_edges(x * p ** 2.2, 0.0, 4.0), PEAK_DBFS)
    return Clip(x, n - 1)


_WHOOSH = {
    "cut-light": ([600.0, 4000.0, 1500.0], 400.0),
    "cut": ([300.0, 3000.0, 600.0], None),
    "windup": ([150.0, 1200.0, 400.0], None),
}


def whoosh(variant: str, dur_s: float, peak_pos: float, seed: str = "whoosh") -> Clip:
    """Nhiễu hồng bp quét 3 điểm, đỉnh ở peak_pos. anchor = argmax (ép rơi trong ±1 ms quanh peak_pos)."""
    if variant not in _WHOOSH:
        raise ValueError(f"whoosh: biến thể không hỗ trợ {variant!r}")
    if not 0.05 < peak_pos < 0.95:
        raise ValueError(f"whoosh: peak_pos {peak_pos} ngoài (0,05; 0,95)")
    fpts, hp_fc = _WHOOSH[variant]
    n = _n(dur_s)
    x = dsp.sweep_filter(dsp.noise_pink(n, seed), fpts, [0.0, peak_pos, 1.0], "band", q_oct=1.2)
    if hp_fc:
        x = dsp.hp(x, hp_fc)
    tt = np.arange(n) / max(n - 1, 1)
    env = np.where(tt < peak_pos, (tt / peak_pos) ** 2.5, ((1 - tt) / (1 - peak_pos)) ** 1.5)
    x = x * env
    # ép đỉnh tuyệt đối vào cửa sổ ±1 ms quanh peak_pos (kẹp vài mẫu nhiễu vượt ở ngoài)
    k, w = int(round(peak_pos * (n - 1))), _n(0.001)
    m = float(np.max(np.abs(x[k - w:k + w + 1])))
    outside = np.ones(n, dtype=bool)
    outside[k - w:k + w + 1] = False
    x[outside] = np.clip(x[outside], -0.97 * m, 0.97 * m)
    x = dsp.peak_norm(dsp.fade_edges(x, 0.0, 3.0), PEAK_DBFS)
    return Clip(x, int(np.argmax(np.abs(x))))


SWELL_CHORD = ("E3", "A3", "B3", "C#4", "E4")   # A add9, voicing thấp hơn logo


def swell(dur_s: float, seed: str = "swell") -> Clip:
    """reverse(reverb(brass A add9, wet 1, IR 2 s)) tính từ đỉnh vang, lấy dur_s cuối, khô, fade 5 ms. anchor = len − 1."""
    n = _n(dur_s)
    # nguồn ngắn (gate 60 ms, attack 5 ms) để đỉnh swell nằm sát điểm kết
    src = voices.brass([(nm, 0.0, 0.06) for nm in SWELL_CHORD], attack_s=0.005, seed=f"{seed}:brass")
    wet = dsp.reverb(src, dsp.reverb_ir(f"{seed}:ir", dur_s=2.0, decay=2.5, lp_fc=6000.0), 1.0)
    # bỏ đoạn vang đang dâng trước đỉnh bao (10 ms RMS) để swell kết đúng lúc to nhất
    k = int(np.argmax(np.convolve(wet[:_n(0.3)] ** 2, np.ones(_n(0.01)), "same")))
    wet = wet[k:][::-1]
    if len(wet) < n:
        raise ValueError(f"swell: dur_s {dur_s} dài hơn đuôi vang")
    x = dsp.peak_norm(dsp.fade_edges(wet[-n:], 0.0, 5.0), PEAK_DBFS)
    return Clip(x, n - 1)


def _sub_freq(variant: str, root_hz: float, n: int) -> np.ndarray:
    """Tần số tức thời của sub-drop: accent root + root·e^(−4t), logo root + root/2·e^(−4t)."""
    t = np.arange(n) / SR
    depth = {"accent": 1.0, "logo": 0.5}[variant]
    return root_hz + root_hz * depth * np.exp(-4.0 * t)


# Hit #1 nghe được trên loa điện thoại (vòng sửa đợt 4, S1): phone layer của accent dời vào dải loa điện thoại
# 400–4000 Hz và mạnh hơn (×6,0 thay ×1,2), rồi softclip cả hit (tanh, drive 4) trước vang để limiter master bớt ép.
# Đo trên master −16 (giả lập BP 400 Hz–8 kHz bậc 4): hit − thân 0,4 → 4,5 dB, hit − logo 0,1 → 4,1 dB;
# full-band hit − thân 3,9 → 3,8 dB, crest f300 7,3 → 7,5 dB, limiter ép f300 4,15 → 3,7 dB. Logo giữ nguyên.
ACCENT_PHONE = {"lo": 400.0, "hi": 4000.0, "gain": 6.0}
ACCENT_DRIVE = 4.0


def impact(variant: str = "accent", root_hz: float = ROOT_HZ, seed: str = "impact") -> Clip:
    """Hit theo NC 3.2: sub 1,5·root → root, body 220 → 110 Hz, click, crack (accent), phone layer, IR 1,5 s wet 18 %.
    Accent: phone layer bp 400–4000 Hz ×6 và softclip drive 4 cả hit (S1). anchor 0."""
    if variant not in ("accent", "logo"):
        raise ValueError(f"impact: biến thể không hỗ trợ {variant!r}")
    logo = variant == "logo"
    n = _n(2.0)
    rng = dsp.rng_for(seed)
    sub = dsp.osc_sine(dsp.glide_exp(1.5 * root_hz, root_hz, 0.08, n), n) * dsp.env_ad(n, 0.002, 1.6)
    body_raw = dsp.osc_sine(dsp.glide_exp(220.0, 110.0, 0.03, n), n) * dsp.env_ad(n, 0.001, 0.5 if logo else 0.35, 5.0)
    body = dsp.softclip(body_raw, 2.0 if logo else 3.0)
    click = dsp.bp(rng.standard_normal(n), 3000.0, 8000.0) * dsp.env_ad(n, 0.0005, 0.012, 5.0)
    click *= 0.35 * (10 ** (-6 / 20) if logo else 1.0)
    phone = dsp.phone_layer(sub + body_raw) if logo else dsp.phone_layer(sub + body_raw, **ACCENT_PHONE)
    x = 0.75 * sub + 0.7 * body + click + phone
    if not logo:
        x = x + dsp.lp(rng.standard_normal(n), 1800.0) * dsp.env_ad(n, 0.001, 0.08, 5.0) * 0.8
        x = dsp.softclip(x / np.max(np.abs(x)), ACCENT_DRIVE)
    x = dsp.reverb(x, dsp.reverb_ir(f"{seed}:ir", dur_s=1.5, decay=3.5, lp_fc=5000.0), 0.18)
    return Clip(_finish(x, 30.0), 0)


def sub_drop(variant: str = "accent", root_hz: float = ROOT_HZ, dur_s: float | None = None,
             seed: str = "subdrop") -> Clip:
    """Sub-drop: accent f = root + root·e^(−4t) (1,2 s), logo f = root + root/2·e^(−4t) (1,0 s); bao e^(−2,2t); phone layer. anchor 0."""
    if variant not in ("accent", "logo"):
        raise ValueError(f"sub_drop: biến thể không hỗ trợ {variant!r}")
    d = dur_s if dur_s is not None else (1.2 if variant == "accent" else 1.0)
    n = _n(d)
    s = dsp.osc_sine(_sub_freq(variant, root_hz, n), n) * np.exp(-2.2 * np.arange(n) / SR)
    x = s + dsp.phone_layer(s, gain=0.8)
    return Clip(_finish(x, 30.0), 0)


# ---------- dispatch ----------
def _dur(event: dict) -> float:
    if "durF" not in event:
        raise ValueError(f"cue {event.get('id')}: thiếu durF")
    return float(event["durF"]) / FPS


def render_cue(event: dict, sheet_id: str) -> Clip:
    """Dựng clip cho một cue (kể cả cue sound: false). sonicLogo / musicStop → ValueError.
    Cue neo `end`: anchor = len − 1 (clip kết đúng tại frame cue), kể cả whoosh vốn neo đỉnh (vòng sửa đợt 4, S3:
    whoosh-charge từng bị đặt theo đỉnh, 40 % đuôi rơi vào khoảng lặng [292, 300) và bị xóa)."""
    clip = _render(event, sheet_id)
    return Clip(clip.x, len(clip.x) - 1) if event.get("anchor") == "end" else clip


def _render(event: dict, sheet_id: str) -> Clip:
    kind, var = event.get("kind"), event.get("variant")
    seed = f"{sheet_id}:{event['id']}"
    if kind == "ping":
        return ping(seed, var or "night")
    if kind == "tickUi":
        return tick_ui(var or "E6", seed)
    if kind == "tickCatch":
        return tick_catch(var or "A4", seed)
    if kind == "thump":
        return thump(seed)
    if kind == "snort":
        return snort(seed)
    if kind == "riser":
        return riser(_dur(event), seed)
    if kind == "whoosh":
        return whoosh(var or "cut", _dur(event), float(event.get("peakPos", 0.6)), seed)
    if kind == "swell":
        return swell(_dur(event), seed)
    if kind == "hit":
        return impact(var or "accent", ROOT_HZ, seed)
    if kind == "subdrop":
        return sub_drop(var or "accent", ROOT_HZ, _dur(event) if "durF" in event else None, seed)
    raise ValueError(f"render_cue: kind {kind!r} không dựng bằng synth (cue {event['id']})")
