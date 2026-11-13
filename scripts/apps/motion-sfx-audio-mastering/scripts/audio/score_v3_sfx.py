"""SFX mới của V3 và bộ dựng cue V3 (dispatch) — tự tổng hợp, mềm, cùng giọng thương hiệu V2.

Âm mới: chime-hoi, tick-eject, scan, blip-alert, tick-fix, paper, tick-num, tick-accent. Âm giống V2 (thump, snort,
whoosh, riser, hit, subdrop, tickUi, sonicLogo) gọi thẳng synth.render_cue / sonic_logo.sonic_logo của V2.
Cấm như V2: taiko, timpani, braam, còi báo động, SFX meme. Cao độ theo hợp âm A trưởng của nhạc V3.

Căn neo: mọi clip có PRE 5 ms lặng ở đầu (fade-in 3 ms của mixbus.prep_clip không chạm attack). Neo `peak` =
argmax|x| tính trên clip ĐÃ qua mixbus.prep_clip (đúng mẫu sẽ nằm trên stem); `onset` = mẫu đầu sau PRE;
`end` = mẫu cuối (như V2); `manual` (snort) = đỉnh xung 1.
"""
from __future__ import annotations

import numpy as np

import dsp
import mixbus
import sonic_logo
import synth
from dsp import SR
from synth import Clip

PRE_S = 0.005
PEAK_DBFS = synth.PEAK_DBFS


def _n(dur_s: float) -> int:
    return int(round(dur_s * SR))


def _finish(x: np.ndarray, tail_ms: float = 15.0) -> np.ndarray:
    return dsp.peak_norm(dsp.fade_edges(x, 0.0, tail_ms), PEAK_DBFS)


def _add(buf: np.ndarray, start: int, x: np.ndarray, gain: float = 1.0) -> None:
    e = min(len(buf), start + len(x))
    buf[start:e] += x[:e - start] * gain


def _partials(f0, n: int, parts, attack_s: float) -> np.ndarray:
    """Tổng sine (tỉ lệ, biên độ, decay s); f0 số hoặc mảng tần số tức thời."""
    x = np.zeros(n)
    for ratio, amp, dec in parts:
        x += amp * dsp.osc_sine(np.asarray(f0) * ratio, n) * dsp.env_ad(n, attack_s, dec)
    return x


def _click(seed: str, n: int, lo: float, hi: float, dec_s: float, amp: float) -> np.ndarray:
    return dsp.bp(dsp.noise_white(n, seed), lo, hi) * dsp.env_ad(n, 0.0002, dec_s) * amp


# ---------- âm mới ----------
def chime_hoi(seed: str = "chime-hoi") -> Clip:
    """Chuông hỏi nhỏ: nốt láy A5 (0,4) rồi E6 vút nhẹ từ −1 bán cung (40 ms) như ngữ điệu hỏi; bội âm chuông
    1 / 2 / 3 / 4,16, decay 0,9 s; LP 7 kHz. Đỉnh = nốt E6."""
    n, lead = _n(1.1), _n(0.07)
    bell = ((1.0, 1.0, 0.9), (2.0, 0.3, 0.45), (3.0, 0.12, 0.25), (4.16, 0.06, 0.12))
    x = np.zeros(n)
    _add(x, 0, _partials(dsp.hz("A5"), lead + _n(0.3), bell, 0.0015) * dsp.env_ad(lead + _n(0.3), 0.0015, 0.25), 0.4)
    m = n - lead
    t = np.arange(m) / SR
    f = dsp.hz("E6") * 2.0 ** (-np.exp(-t / 0.013) / 12.0)
    _add(x, lead, _partials(f, m, bell, 0.0015))
    return Clip(_finish(dsp.lp(dsp.hp(x, 300.0, 2), 7000.0, 2), 30.0), 0)


def tick_eject(note: str, seed: str = "tick-eject") -> Clip:
    """Tiếng 'bóc' khối bật ra: sine vút lên từ −4 bán cung (τ 3 ms), decay 70 ms, + H2 0,2 + click bp 2–6 kHz."""
    n = _n(0.15)
    t = np.arange(n) / SR
    f = dsp.hz(note) * 2.0 ** (-4.0 * np.exp(-t / 0.003) / 12.0)
    x = _partials(f, n, ((1.0, 1.0, 0.07), (2.0, 0.2, 0.03)), 0.0008)
    x += _click(seed, n, 2000.0, 6000.0, 0.002, 0.25)
    return Clip(_finish(dsp.lp(x, 5000.0, 2), 10.0), 0)


def scan(dur_s: float, seed: str = "scan") -> Clip:
    """Quét nhẹ dải cao: nhiễu hồng bp quét 2,5 → 6,5 → 4 kHz (q 0,8 oct), HP 2 kHz, rung biên độ 8 Hz (1/16 ở
    120 BPM) sâu 0,25; bao vào cosine 0,3 s, ra cosine 0,4 s về đúng 0 ở mẫu cuối. Dài đúng dur_s."""
    n = _n(dur_s)
    x = dsp.sweep_filter(dsp.noise_pink(n, seed), [2500.0, 6500.0, 4000.0], [0.0, 0.7, 1.0], "band", q_oct=0.8)
    x = dsp.hp(x, 2000.0, 2)
    t = np.arange(n) / SR
    x *= 1.0 - 0.25 * (0.5 - 0.5 * np.cos(2 * np.pi * 8.0 * t))
    env = np.ones(n)
    a, r = _n(0.3), _n(0.4)
    env[:a] = 0.5 - 0.5 * np.cos(np.pi * np.arange(a) / a)
    env[n - r:] = 0.5 + 0.5 * np.cos(np.pi * (np.arange(r) + 1) / r)
    env *= 0.85 + 0.15 * np.sin(np.pi * t / dur_s)      # phồng nhẹ ở giữa đường quét
    return Clip(dsp.peak_norm(x * env, PEAK_DBFS), 0)


_BLIP = {"1": ("A5", "F#5"), "2": ("F#5", "D5")}


def blip_alert(variant: str, seed: str = "blip") -> Clip:
    """Cảnh báo mềm 'u-ồ': sine trượt xuống quãng 3 (τ 20 ms), attack 4 ms, decay 160 ms, H2 0,25 + H3 0,1,
    LP 3 kHz. Không còi, không lặp. (1) A5 → F#5, (2) F#5 → D5 (hợp âm D add9)."""
    if variant not in _BLIP:
        raise ValueError(f"blip_alert: biến thể không hỗ trợ {variant!r}")
    hi, lo = (dsp.hz(nm) for nm in _BLIP[variant])
    n = _n(0.3)
    f = dsp.glide_exp(hi, lo, 0.02, n)
    x = _partials(f, n, ((1.0, 1.0, 0.16), (2.0, 0.25, 0.1), (3.0, 0.1, 0.06)), 0.004)
    return Clip(_finish(dsp.lp(x, 3000.0, 2), 20.0), 0)


def tick_fix(seed: str = "tick-fix") -> Clip:
    """Tiếng 'khóa' hai nhịp: lẫy nhỏ (click bp 3–8 kHz + sine 2,4 kHz, 0,5) rồi 45 ms sau chốt (sine 900 → 600 Hz
    τ 5 ms, thân 220 Hz decay 70 ms, click bp 1,5–5 kHz) kèm 'ting' A6 nhỏ decay 180 ms. Đỉnh = nhịp chốt."""
    n, d = _n(0.35), _n(0.045)
    x = np.zeros(n)
    m1 = _n(0.03)
    latch = _click(f"{seed}:a", m1, 3000.0, 8000.0, 0.0015, 0.6) + \
        dsp.osc_sine(2400.0, m1) * dsp.env_ad(m1, 0.0003, 0.008) * 0.5
    _add(x, 0, latch, 0.5)
    m2 = n - d
    t = np.arange(m2) / SR
    bolt = dsp.osc_sine(600.0 + 300.0 * np.exp(-t / 0.005), m2) * dsp.env_ad(m2, 0.0005, 0.04)
    body = dsp.osc_sine(220.0, m2) * dsp.env_ad(m2, 0.001, 0.07) * 0.6
    ting = dsp.osc_sine(dsp.hz("A6"), m2) * dsp.env_ad(m2, 0.001, 0.18) * 0.22
    _add(x, d, bolt + body + ting + _click(f"{seed}:b", m2, 1500.0, 5000.0, 0.003, 0.7))
    return Clip(_finish(dsp.lp(x, 9000.0, 2), 20.0), 0)


def paper(seed: str = "paper") -> Clip:
    """Giấy trượt: nhiễu trắng bp 1,2–7 kHz, LP quét 7 → 3 kHz (ma sát chậm dần), hạt nhám từ nhiễu LP 60 Hz;
    bao sin² dâng 0,14 s rồi (1 − t)^1,5 về 0 ở 0,6 s. Neo onset = đầu tiếng trượt."""
    n = _n(0.6)
    x = dsp.bp(dsp.noise_white(n, f"{seed}:n"), 1200.0, 7000.0)
    x = dsp.sweep_filter(x, [7000.0, 3000.0], [0.0, 1.0], "low")
    grain = np.abs(dsp.lp(dsp.noise_white(n, f"{seed}:g"), 60.0, 2))
    x *= 0.55 + 0.45 * grain / (np.max(grain) + 1e-12)
    t = np.arange(n) / SR
    a = 0.14
    env = np.where(t < a, np.sin(0.5 * np.pi * t / a) ** 2, ((t[-1] - t) / (t[-1] - a)) ** 1.5)
    return Clip(dsp.peak_norm(x * env, PEAK_DBFS), 0)


def tick_num(note: str, seed: str = "tick-num") -> Clip:
    """Tick gỗ kiểu marimba: sine (decay 180 ms) + bội 3,93 (0,35; 30 ms) + click dùi bp 1,5–4 kHz 2 ms."""
    n = _n(0.25)
    x = _partials(dsp.hz(note), n, ((1.0, 1.0, 0.18), (3.93, 0.35, 0.03)), 0.001)
    x += _click(seed, n, 1500.0, 4000.0, 0.002, 0.2)
    return Clip(_finish(dsp.lp(x, 6000.0, 2), 15.0), 0)


def tick_accent(note: str, seed: str = "tick-accent") -> Clip:
    """Khối nhấn quét: vệt 'xẹt' nhiễu HP 3 kHz dâng (t/T)² trong 60 ms (0,22) kết vào tick sine + H2 0,15
    decay 30 ms, click bp 2–6 kHz 3 ms. Đỉnh = tick."""
    sw, n = _n(0.06), _n(0.16)
    x = np.zeros(n)
    swish = dsp.hp(dsp.noise_white(sw, f"{seed}:sw"), 3000.0, 2) * (np.arange(sw) / sw) ** 2
    _add(x, 0, swish, 0.22)
    m = n - sw
    tick = _partials(dsp.hz(note), m, ((1.0, 1.0, 0.03), (2.0, 0.15, 0.015)), 0.0005)
    _add(x, sw, tick + _click(seed, m, 2000.0, 6000.0, 0.003, 0.4))
    return Clip(_finish(x, 8.0), 0)


# ---------- dispatch ----------
NEW_KINDS = ("chime", "tickEject", "scan", "blip", "tickFix", "paper", "tickNum", "tickAccent")


def _new(ev: dict, seed: str) -> Clip:
    kind, var = ev["kind"], ev.get("variant")
    if kind == "chime":
        return chime_hoi(seed)
    if kind == "tickEject":
        return tick_eject(var or "A5", seed)
    if kind == "scan":
        return scan(float(ev["durF"]) / dsp.FPS, seed)
    if kind == "blip":
        return blip_alert(var or "1", seed)
    if kind == "tickFix":
        return tick_fix(seed)
    if kind == "paper":
        return paper(seed)
    if kind == "tickNum":
        return tick_num(var or "A5", seed)
    return tick_accent(var or "E6", seed)


def raw_clip(ev: dict, sheet_id: str) -> Clip:
    """Clip gốc (chưa đệm PRE): kind mới → hàm ở trên; sonicLogo → sonic_logo V2; còn lại → synth.render_cue V2."""
    seed = f"{sheet_id}:{ev['id']}"
    if ev["kind"] in NEW_KINDS:
        return _new(ev, seed)
    if ev["kind"] == "sonicLogo":
        return sonic_logo.sonic_logo(ev.get("variant", "a"), seed=seed)
    return synth.render_cue(ev, sheet_id)


def render_cue(ev: dict, sheet_id: str) -> Clip:
    """Clip đặt được bằng mixbus: neo theo ev['anchor'] (xem docstring module)."""
    clip = raw_clip(ev, sheet_id)
    anchor = ev["anchor"]
    if anchor == "end":
        return Clip(clip.x, len(clip.x) - 1)
    pre = _n(PRE_S)
    x = np.concatenate([np.zeros(pre), clip.x])
    if anchor == "onset":
        return Clip(x, pre)
    prepped = np.abs(mixbus.prep_clip(Clip(x, 0), ev["kind"]).x)
    if anchor == "manual":   # snort: đỉnh xung 1 (V2 đặt clip.anchor trong xung 1)
        w = _n(0.12)
        return Clip(x, pre + int(np.argmax(prepped[pre:pre + w])))
    return Clip(x, int(np.argmax(prepped)))


def make_render(sheet_id: str):
    return lambda ev: render_cue(ev, sheet_id)
