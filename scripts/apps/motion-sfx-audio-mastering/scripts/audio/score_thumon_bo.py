"""Giọng Bò OPA cho phim 3D "Thủ môn" — tự tổng hợp 100 %: hơi mũi phì khô, thân đáp trầm 110 → 55 Hz + "tok" sừng khô,
trượt nhám trầm, thở ra dài, chênh vênh ở mép bàn.

Bò là một khối đặc, nặng, làm chủ: không tiếng bò kêu, không squeak / blip / boing / chút chít, không giọng người.
Mỗi hàm trả synth.Clip mono float64, đỉnh −1 dBFS, anchor 0; neo theo cue do score_thumon_sfx.render_cue đặt.
Mọi nhiễu lấy từ dsp.rng_for(seed). Biến thể nghe A/B (CHƯA NGHE BẰNG TAI): land A | B | C.
"""
from __future__ import annotations

import numpy as np

import dsp
from dsp import SR
from synth import Clip

PEAK_DBFS = -1.0
# cú đáp theo độ cao nảy: S ≤ 1,2 cm, M ≈ 1,8 cm, L cú nhảy 10 cm, R lắc tại chỗ, E trượt dừng ở mép bàn
LAND = {  # (thân Hz đầu, tắt s, tok, click)
    "S": (110.0, 0.12, 0.35, 0.22), "M": (112.0, 0.15, 0.40, 0.25), "L": (118.0, 0.22, 0.45, 0.30),
    "R": (105.0, 0.09, 0.22, 0.10), "E": (100.0, 0.16, 0.0, 0.0),
}
LAND_STYLES = ("A", "B", "C")


def _n(dur_s: float) -> int:
    return int(round(dur_s * SR))


def _t(n: int) -> np.ndarray:
    return np.arange(n) / SR


def _finish(x: np.ndarray, tail_ms: float = 15.0) -> np.ndarray:
    """Chuẩn hóa đỉnh −1 dBFS, fade đuôi; attack giữ nguyên."""
    return dsp.peak_norm(dsp.fade_edges(x, 0.0, tail_ms), PEAK_DBFS)


def _decay(n: int, tau_s: float, attack_s: float = 0.0003) -> np.ndarray:
    """Bao tắt mũ e^(−t/τ) với attack tuyến tính ngắn (không click)."""
    t = _t(n)
    a = max(attack_s, 1e-6)
    return np.where(t < a, t / a, np.exp(-(t - a) / max(tau_s, 1e-6)))


def _bell(u0: float, u1: float, n: int) -> np.ndarray:
    """Tốc độ chuẩn hóa của khóa Hermite giữ–giữ: v(u) = 4u(1 − u) (đỉnh 1 ở giữa), lấy đoạn u0 → u1."""
    u = np.linspace(u0, u1, n)
    return 4.0 * u * (1.0 - u)


def tok(seed: str, hz1: float = 1150.0, amp: float = 1.0) -> np.ndarray:
    """"tok" khô của khối cứng: hai sine không hài (1 : 1,55) tắt 12 / 8 ms + nhiễu bp 0,9–2,5 kHz 3 ms. Dài 60 ms."""
    n = _n(0.06)
    x = np.sin(2 * np.pi * hz1 * _t(n)) * _decay(n, 0.012) + 0.6 * np.sin(2 * np.pi * 1.55 * hz1 * _t(n)) * _decay(n, 0.008)
    x += dsp.bp(dsp.noise_white(n, f"{seed}:tok"), 900.0, 2500.0) * _decay(n, 0.003) * 0.25
    return x * amp


# ---------- đáp ----------
def land(cls: str, style: str = "A", seed: str = "land") -> Clip:
    """Thân đáp trầm (glide f0 → f0/2, τ 25 ms) + click (×0,6) + phone layer như thump V2, tắt theo độ cao nảy;
    softclip nhẹ (drive 1,6) cả cú đáp để limiter master bớt ép.
    A: + "tok" sừng khô 40 ms. B: thân nặng hơn (100 → 50 Hz, dài ×1,3), không tok. C: "gỗ đặc" (130 → 65 Hz, ngắn ×0,6,
    tiếng gõ gỗ 640 Hz). E (dừng ở mép bàn): không click, không tok — chỉ thân, vì Bò trượt tới chứ không rơi xuống."""
    if cls not in LAND or style not in LAND_STYLES:
        raise ValueError(f"land: lớp/kiểu không hỗ trợ {cls!r}/{style!r}")
    f0, dec, tok_amp, click_amp = LAND[cls]
    if style == "B":
        f0, dec, tok_amp, click_amp = f0 * 100.0 / 110.0, dec * 1.3, 0.0, click_amp * 0.5
    elif style == "C":
        f0, dec, tok_amp = f0 * 130.0 / 110.0, dec * 0.6, 0.0
    n = _n(dec + 0.25)
    body = dsp.osc_sine(dsp.glide_exp(f0, f0 / 2, 0.025, n), n) * dsp.env_ad(n, 0.001, dec)
    core = dsp.softclip(body, 2.0)
    phone = dsp.phone_layer(body, gain=1.0)
    phone *= (0.6 if style == "B" else 0.8) * np.sqrt(np.mean(core ** 2) / (np.mean(phone ** 2) + 1e-20))
    x = core + phone
    x += dsp.bp(dsp.noise_white(n, f"{seed}:click"), 2000.0, 7000.0) * dsp.env_ad(n, 0.0003, 0.006) * click_amp * 0.6
    if cls == "L":  # cú nhảy cao: thêm khối trầm 55 Hz đi theo
        x += 0.3 * dsp.osc_sine(55.0, n) * dsp.env_ad(n, 0.004, 0.3)
    if tok_amp > 0:
        k = tok(seed, 1150.0 if cls != "L" else 1020.0, tok_amp)
        x[:len(k)] += k
    if style == "C":
        m = _n(0.08)
        wood = np.sin(2 * np.pi * 640.0 * _t(m)) * _decay(m, 0.02) * 0.5
        wood += dsp.bp(dsp.noise_white(m, f"{seed}:wood"), 400.0, 1200.0) * _decay(m, 0.015) * 0.5
        x[:m] += wood
    x = dsp.softclip(x / (np.max(np.abs(x)) + 1e-12), 1.6)       # bớt gai: limiter master ép ít hơn
    return Clip(_finish(x, 20.0), 0)


def push(seed: str = "push") -> Clip:
    """Bật nhảy: thân nén 95 → 60 Hz tắt 70 ms (không click) rồi luồng hơi nâng lên bp 0,3–1,5 kHz 0,16 s."""
    n = _n(0.3)
    body = dsp.softclip(dsp.osc_sine(dsp.glide_exp(95.0, 60.0, 0.02, n), n) * dsp.env_ad(n, 0.001, 0.07), 1.5)
    u = _t(n) / 0.16
    lift = dsp.bp(dsp.noise_white(n, f"{seed}:lift"), 300.0, 1500.0) * np.where(u < 0.6, (u / 0.6) ** 1.5,
                                                                                np.clip(1 - (u - 0.6) / 0.4, 0, 1))
    return Clip(_finish(body + 0.3 * lift, 15.0), 0)


# ---------- sừng ----------
def horn_tok(seed: str = "horn-tok") -> Clip:
    """Bóng đậu ngọn sừng: "tok" khô (1,32 kHz) + thân bóng mềm 520 Hz 25 ms, rồi bóng lắc trên ngọn sừng: ba tiếng
    chạm rất nhỏ ở các lần đảo chiều (lắc 14 rad/s tắt e^(−2,5t): +0,22 / 0,45 / 0,67 s, −15 / −20 / −26 dB)."""
    n = _n(0.85)
    x = np.zeros(n)
    k = tok(seed, 1320.0)
    x[:len(k)] += k
    m = _n(0.08)
    x[:m] += np.sin(2 * np.pi * 520.0 * _t(m)) * _decay(m, 0.025) * 0.5
    for i, (dt, db) in enumerate(((0.224, -15.0), (0.449, -20.0), (0.673, -26.0))):
        s, q = _n(dt), _n(0.03)
        tick = np.sin(2 * np.pi * 900.0 * _t(q)) * _decay(q, 0.006)
        tick += dsp.bp(dsp.noise_white(q, f"{seed}:wob{i}"), 1500.0, 3500.0) * _decay(q, 0.002) * 0.3
        x[s:s + q] += tick * 10 ** (db / 20)
    return Clip(_finish(dsp.lp(x, 6000.0, 2), 20.0), 0)


def flick_tok(seed: str = "flick-tok") -> Clip:
    """Sừng hất bóng: "tok" nhẹ, cao hơn (1,5 kHz) + luồng hơi hp 1,5 kHz tắt 30 ms."""
    n = _n(0.12)
    x = np.zeros(n)
    k = tok(seed, 1500.0, 0.8)
    x[:len(k)] += k
    x += dsp.hp(dsp.noise_white(n, f"{seed}:air"), 1500.0, 2) * _decay(n, 0.03, 0.002) * 0.3
    return Clip(_finish(x, 10.0), 0)


# ---------- hơi thở ----------
def snort_bo(power: float, slow: bool = False, seed: str = "snort") -> Clip:
    """Hơi mũi phì khô từ hai lỗ mũi (hai luồng nhiễu bp lệch 4 ms), dâng 6 ms, tắt (1 − u)², sáng theo lực:
    lp 0,9 + 0,7·lực kHz, thêm luồng áp trầm < 250 Hz và chút hiss khô 2–5 kHz. Lực ≥ 0,9: thêm hơi thứ hai nhỏ ở
    +0,15 s. slow (phì chậm khi dịu lại): một hơi mềm 0,45 s, dâng 80 ms, lp 700 Hz, không hiss."""
    if not 0.0 < power <= 1.0:
        raise ValueError(f"snort_bo: lực {power} ngoài (0, 1]")
    rng = dsp.rng_for(seed)
    dur, att, lp_fc, hiss = (0.45, 0.08, 700.0, 0.0) if slow else (0.10 + 0.06 * power, 0.006, 900.0 + 700.0 * power, 0.12)
    n = _n(dur + 0.3)

    def puff(gain: float, start: int, d: float) -> np.ndarray:
        m = _n(d)
        u = np.arange(m) / m
        a = min(att / d, 0.5)
        env = np.where(u < a, np.sin(0.5 * np.pi * u / a) ** 2, ((1 - u) / (1 - a)) ** 2)
        out = np.zeros(n)
        for j, (lo, hi, off) in enumerate(((500.0, 1300.0, 0), (700.0, 1700.0, _n(0.004)))):   # hai lỗ mũi
            nz = dsp.bp(rng.standard_normal(m + 2400), lo, hi)[2400:]
            seg = dsp.lp(nz, lp_fc, order=4) * env
            e = min(n, start + off + m)
            out[start + off:e] += seg[:e - start - off] * (1.0 if j == 0 else 0.8)
        low = dsp.lp(rng.standard_normal(m + 2400), 250.0, order=4)[2400:] * env * (0.15 if slow else 0.25 * power)
        e = min(n, start + m)
        out[start:e] += low[:e - start] * 4.0
        if hiss:
            hs = dsp.bp(rng.standard_normal(m + 2400), 2000.0, 5000.0)[2400:] * env * hiss
            out[start:e] += hs[:e - start]
        return out * gain

    x = puff(1.0, 0, dur)
    if power >= 0.9 and not slow:
        x += puff(0.45, _n(0.15), dur * 0.7)
    return Clip(_finish(x, 20.0), 0)


def exhale(dur_s: float, seed: str = "exhale", burst: bool = False) -> Clip:
    """Thở ra qua mũi: nhiễu hồng bp, lp quét xuống, nhấn mũi +3 dB, rung rất nhẹ 5 Hz cho có thớ.
    Thường (thở ra dài): bp 0,22–1 kHz, lp 1000 → 450 Hz, nhấn 550 Hz, dâng sin² 0,18 s rồi (1 − u)^1,4 về 0.
    burst (bật xả hơi lúc vùng xanh bung, bản 2): bp 0,3–1,6 kHz, lp 1600 → 600 Hz, nhấn 800 Hz, dâng 30 ms rồi (1 − u)²."""
    n = _n(dur_s)
    lo, hi, lp0, lp1, nasal, a, k = (300.0, 1600.0, 1600.0, 600.0, 800.0, 0.03, 2.0) if burst else         (220.0, 1000.0, 1000.0, 450.0, 550.0, 0.18, 1.4)
    x = dsp.bp(dsp.noise_pink(n, f"{seed}:n"), lo, hi)
    x = dsp.peaking(dsp.sweep_filter(x, [lp0, lp1], [0.0, 1.0], "low"), nasal, 3.0, 1.2)
    t = _t(n)
    env = np.where(t < a, np.sin(0.5 * np.pi * t / a) ** 2, np.clip((t[-1] - t) / (t[-1] - a), 0, 1) ** k)
    x *= env * (1.0 - 0.08 * (0.5 + 0.5 * np.sin(2 * np.pi * 5.0 * t)))
    return Clip(dsp.peak_norm(x, PEAK_DBFS), 0)


def inhale(dur_s: float, seed: str = "inhale") -> Clip:
    """Lấy đà (bản 2): Bò hít hơi qua mũi, nhanh dần rồi nín đúng lúc bật xả. Nhiễu hồng bp 0,3–1,8 kHz, lp mở dần
    700 → 2600 Hz, nhấn mũi +3 dB ở 900 Hz, dâng u^1,8 tới cuối, tắt gọn 6 ms. Neo end = khung bật xả."""
    n = _n(dur_s)
    x = dsp.bp(dsp.noise_pink(n, f"{seed}:n"), 300.0, 1800.0)
    x = dsp.peaking(dsp.sweep_filter(x, [700.0, 2600.0], [0.0, 1.0], "low"), 900.0, 3.0, 1.2)
    u = np.arange(n) / max(n - 1, 1)
    x = dsp.fade_edges(x * u ** 1.8, 2.0, 6.0)
    return Clip(dsp.peak_norm(x, PEAK_DBFS), 0)


def bob(seed: str = "bob") -> Clip:
    """Bò nảy theo phách, chạm đáy đúng phách (bản 2): "tok" nhẹ của khối cứng (1,25 kHz, ×0,5) + thân mềm 95 → 70 Hz
    tắt 60 ms, không click, không sub. Nhỏ, để kick của nhạc gánh phần trầm."""
    n = _n(0.14)
    x = dsp.osc_sine(dsp.glide_exp(95.0, 70.0, 0.02, n), n) * dsp.env_ad(n, 0.002, 0.06) * 0.6
    k = tok(seed, 1250.0, 0.5)
    x[:len(k)] += k
    return Clip(_finish(x, 15.0), 0)


# ---------- trượt, chênh vênh ----------
def slide(dur_s: float, u0: float, u1: float, style: str = "", seed: str = "slide") -> Clip:
    """Ma sát nhám trầm của Bò trượt trên mặt bàn, theo tốc độ khóa Hermite (đoạn u0 → u1 của chuyển động):
    nhiễu bp 180–1400 Hz có hạt (đường bao |lp 35 Hz|), lp theo tốc độ 500 + 1300·v Hz, biên độ v^0,9, thêm ầm < 150 Hz.
    style E: nặng hơn, mài nhiều hạt (trượt dừng ở mép bàn); slow: nhẹ, ít hạt (lùi về chỗ)."""
    n = _n(dur_s)
    v = _bell(u0, u1, n)
    lo, hi, grain_k, rumble = (150.0, 900.0, 0.7, 0.45) if style == "E" else \
        (180.0, 1000.0, 0.35, 0.25) if style == "slow" else (180.0, 1400.0, 0.55, 0.3)
    x = dsp.bp(dsp.noise_white(n, f"{seed}:n"), lo, hi)
    g = np.abs(dsp.lp(dsp.noise_white(n, f"{seed}:g"), 35.0, 2))
    x *= (1.0 - grain_k) + grain_k * g / (np.max(g) + 1e-12)
    x = dsp.filter_curve(x, 500.0 + 1300.0 * v, "low")
    x += dsp.lp(dsp.noise_white(n, f"{seed}:r"), 150.0, 2) * rumble * 3.0
    x *= np.power(np.clip(v, 0.0, 1.0), 0.9)
    x = dsp.fade_edges(x, 4.0, 15.0)
    return Clip(dsp.peak_norm(x, PEAK_DBFS), 0)


def teeter(seed: str = "teeter") -> Clip:
    """Chênh vênh: chạm nhẹ ở mép (900 Hz 6 ms), ầm trầm 120–420 Hz dâng 50 ms tắt 0,25 s, và tiếng cọ mép rất nhỏ
    (bp hẹp quanh 760 Hz, rung ±40 Hz theo nhịp sừng run 8 Hz)."""
    n = _n(0.55)
    t = _t(n)
    groan = dsp.bp(dsp.noise_white(n, f"{seed}:g"), 120.0, 420.0) * dsp.env_ad(n, 0.05, 0.25, 3.0)
    creak = dsp.filter_curve(dsp.noise_white(n, f"{seed}:c"), 760.0 + 40.0 * np.sin(2 * np.pi * 8.0 * t), "band", 0.15)
    creak *= dsp.env_ad(n, 0.04, 0.25, 3.0) * 0.25
    m = _n(0.03)
    contact = np.zeros(n)
    contact[:m] = np.sin(2 * np.pi * 900.0 * _t(m)) * _decay(m, 0.006) * 0.25
    return Clip(_finish(groan + creak + contact, 30.0), 0)
