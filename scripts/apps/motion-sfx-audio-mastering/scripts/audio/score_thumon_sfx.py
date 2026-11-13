"""SFX thế giới và bộ dựng cue (dispatch) của phim 3D "Thủ môn" — tự tổng hợp 100 %, không sample, không giọng.

Âm mới: pop (bong bóng "bụp" ra khỏi kính), catch (tick hứng, mỗi lần một cao độ), save (cú cứu ở mép bàn), card ("bạch"
thẻ rời lòng O), tickCard (thẻ tới CRM), tickRow (dòng CRM lúc tua), ffSweep (tua cả đêm), cta (nút CTA bật), bed (tiếng
phòng, ù màn hình). Giọng Bò ở score_thumon_bo.py. Kind V2 (whoosh, riser, swell, hit, subdrop) gọi synth.render_cue,
sonicLogo gọi sonic_logo.sonic_logo: giống hệt V2, V3. Cấm: squeak, blip, boing, chút chít, marimba, music-box, tiếng bò.

variant = "tham số chính[/cờ…]": cờ A | B | C là kiểu nghe A/B (CHƯA NGHE BẰNG TAI), "ring" = ngân dài, "slow", "E".
Căn neo như score_v3_sfx: clip có PRE 5 ms lặng ở đầu; peak = argmax|x| trên clip ĐÃ qua mixbus.prep_clip; onset = mẫu
đầu sau PRE; end = mẫu cuối; manual = điểm hàm khai (cta: đỉnh tick).
"""
from __future__ import annotations

import numpy as np

import dsp
import mixbus
import score_thumon_bo as bo
import score_thumon_cues as C
import sonic_logo
import synth
from dsp import SR
from synth import Clip

PRE_S = 0.005
CARD_FLY_S = 0.40                # bản 1: thẻ bay 0,40 s (tiếng "bạch" card chỉ dùng ở bản 1)
PEAK_DBFS = -1.0
STYLES = ("A", "B", "C")
_n, _t, _decay, _finish = bo._n, bo._t, bo._decay, bo._finish


FLAGS = frozenset(STYLES) | {"ring", "slow", "E"}


def parse_variant(variant: str | None, default_main: str = "") -> tuple[str, tuple[str, ...], str]:
    """'C#5/ring/B' → ('C#5', ('ring', 'B'), 'B'); kiểu mặc định A. Cờ lạ hoặc hai kiểu A/B/C cùng lúc → ValueError
    (cờ giữ thứ tự viết, không dùng set: kết quả không phụ thuộc thứ tự băm)."""
    parts = (variant or default_main).split("/")
    flags = tuple(parts[1:])
    unknown = [f for f in flags if f not in FLAGS]
    styles = [f for f in flags if f in STYLES]
    if unknown or len(styles) > 1:
        raise ValueError(f"variant {variant!r}: cờ lạ {unknown} hoặc nhiều kiểu {styles}")
    return parts[0] or default_main, flags, styles[0] if styles else "A"


def _smoothstep(t: np.ndarray, a: float, b: float) -> np.ndarray:
    u = np.clip((t - a) / (b - a), 0.0, 1.0)
    return u * u * (3 - 2 * u)


# ---------- bong bóng, hứng ----------
def pop(note: str, seed: str = "pop") -> Clip:
    """Bong bóng "bụp" ra khỏi kính: "tunk" kính trầm (sine nốt, vào cao +4 bán cung τ 4 ms, tắt τ 14 ms, không ngân)
    + bội kính 2,76× tắt 6 ms + luồng hơi bp 250–1200 Hz 8 ms + "tik" kính bp 3–5 kHz 1 ms; lp 4,5 kHz."""
    n = _n(0.16)
    t = _t(n)
    f = dsp.hz(note) * 2.0 ** (4.0 * np.exp(-t / 0.004) / 12.0)
    x = dsp.osc_sine(f, n) * _decay(n, 0.014, 0.0006)
    x += dsp.osc_sine(f * 2.76, n) * _decay(n, 0.006) * 0.25
    x += dsp.bp(dsp.noise_white(n, f"{seed}:air"), 250.0, 1200.0) * _decay(n, 0.008, 0.001) * 0.5
    x += dsp.bp(dsp.noise_white(n, f"{seed}:tik"), 3000.0, 5000.0) * _decay(n, 0.0007) * 0.35
    return Clip(_finish(dsp.lp(x, 4500.0, 2), 10.0), 0)


def _tick_core(f0: float, dec_s: float, seed: str) -> np.ndarray:
    """Tick hứng khô: sine vào cao +2 bán cung (τ 3 ms), tắt e^−4 ở dec_s, H2 0,12, click bp 1,5–5 kHz 3 ms (×0,18:
    nửa V2, bớt gai), và thân bóng chạm đáy lòng O (sine 190 Hz tắt 30 ms)."""
    n = _n(dec_s + 0.08)
    t = _t(n)
    x = dsp.osc_sine(f0 * 2.0 ** (2.0 * np.exp(-t / 0.003) / 12.0), n) * dsp.env_ad(n, 0.0008, dec_s)
    x += dsp.osc_sine(2 * f0, n) * dsp.env_ad(n, 0.0008, dec_s / 2) * 0.12
    x += dsp.bp(dsp.noise_white(n, f"{seed}:click"), 1500.0, 5000.0) * dsp.env_ad(n, 0.0002, 0.003) * 0.18
    x += dsp.osc_sine(190.0, n) * _decay(n, 0.03, 0.0008) * 0.3
    return x


def catch(note: str, style: str = "A", ring: bool = False, seed: str = "catch") -> Clip:
    """Tick hứng khi bóng rơi xuống đáy lòng O, rồi một chạm nảy rất nhỏ ở +143 ms (−16 dB, bóng nảy |sin 22t|).
    A: tick khô một nốt, tắt 85 ms (thang leo theo nhịp căng). B: thêm tiếng "tock" rỗng của lòng O (380 → 330 Hz, 22 ms).
    C: như A (adapter / A/B ép mọi lần về A4). ring: ngân 0,18 s và thêm bội 3× nhỏ (bóng sáng xanh ở lại lòng O)."""
    f0 = dsp.hz(note)
    dec = 0.18 if ring else 0.085
    n = _n(0.42)
    x = np.zeros(n)
    core = _tick_core(f0, dec, seed)
    x[:len(core)] += core
    if style == "B":
        m = _n(0.08)
        x[:m] += dsp.osc_sine(dsp.glide_exp(380.0, 330.0, 0.01, m), m) * _decay(m, 0.022, 0.0008) * 0.5
        x[:m] += dsp.bp(dsp.noise_white(m, f"{seed}:hollow"), 300.0, 900.0) * _decay(m, 0.004) * 0.3
    if ring:
        x += dsp.osc_sine(3 * f0, n) * dsp.env_ad(n, 0.002, 0.3) * 0.08
    s = _n(0.143)
    b = _tick_core(f0, 0.03, f"{seed}:nay")
    e = min(n, s + len(b))
    x[s:e] += b[:e - s] * 10 ** (-16 / 20)
    return Clip(_finish(x, 20.0), 0)


def save(style: str = "A", seed: str = "save") -> Clip:
    """Cú cứu thua ở mép bàn (bóng b7), tiếng khác hẳn tick hứng.
    A: "thock" nặng (160 → 80 Hz, τ 12 ms, tắt 0,14 s, softclip) + click + chuông quãng 5 E5 + B5 (tắt 0,32 s, hết
    trước cú khựng 9,42) vào sau 8 ms.
    B: cú húc như V2 (impact accent + sub-drop 0,6 s) + sừng rung tắt 3 nhịp (8 Hz).
    C: tối giản: một tick sáng E6 ngân 0,25 s."""
    if style == "B":
        hit = synth.impact("accent", synth.ROOT_HZ, f"{seed}:hit").x
        sub = synth.sub_drop("accent", synth.ROOT_HZ, 0.6, f"{seed}:sub").x
        x = hit.copy()
        x[:len(sub)] += 0.7 * sub
        for i, db in enumerate((-12.0, -17.0, -22.0)):
            k = bo.tok(f"{seed}:rung{i}", 1150.0) * 10 ** (db / 20)
            s = _n(0.125 * (i + 1))
            x[s:s + len(k)] += k
        return Clip(_finish(x, 30.0), 0)
    if style == "C":
        return catch("E6", "A", True, seed)
    n = _n(0.8)
    body = dsp.osc_sine(dsp.glide_exp(160.0, 80.0, 0.012, n), n) * dsp.env_ad(n, 0.001, 0.14)
    core = dsp.softclip(body, 2.0)
    phone = dsp.phone_layer(body, gain=1.0)
    x = core + phone * 0.6 * np.sqrt(np.mean(core ** 2) / (np.mean(phone ** 2) + 1e-20))
    x += dsp.bp(dsp.noise_white(n, f"{seed}:click"), 1000.0, 4000.0) * dsp.env_ad(n, 0.0003, 0.005) * 0.4
    d = _n(0.008)
    m = n - d
    chime = np.zeros(m)
    for note in ("E5", "B5"):
        for cents in (-2.0, 2.0):
            chime += dsp.osc_sine(dsp.hz(note) * 2 ** (cents / 1200), m) * dsp.env_ad(m, 0.002, 0.32)
    x[d:] += chime * 0.18
    return Clip(_finish(x, 30.0), 0)


# ---------- thẻ khách, CRM ----------
def card(seed: str = "card") -> Clip:
    """"bạch" như giấy dày lúc bóng hóa thẻ rời lòng O: nhiễu bp 0,8–3 kHz 20 ms + thân 120 Hz 30 ms, nhịp vỗ thứ hai
    nhỏ ở +22 ms; rồi tiếng thẻ bay rất nhỏ (bp 1,5–6 kHz, lp quét 6 → 2,5 kHz) mạnh nhất lúc rời và nhỏ dần tới bảng
    CRM trong 0,40 s, theo tốc độ thẻ bay ease-out của hình."""
    n = _n(0.45)
    t = _t(n)
    x = np.zeros(n)
    for i, (start, g) in enumerate(((0.0, 1.0), (0.022, 0.35))):
        s, m = _n(start), _n(0.06)
        flap = dsp.bp(dsp.noise_white(m, f"{seed}:flap{i}"), 800.0, 3000.0) * dsp.env_ad(m, 0.0004, 0.02)
        flap += dsp.osc_sine(120.0, m) * dsp.env_ad(m, 0.001, 0.03) * 0.5
        x[s:s + m] += flap * g
    swish = dsp.sweep_filter(dsp.bp(dsp.noise_white(n, f"{seed}:fly"), 1500.0, 6000.0), [6000.0, 2500.0],
                             [0.0, 1.0], "low")
    env = np.minimum(t / 0.02, 1.0) * np.clip(1.0 - t / CARD_FLY_S, 0.0, 1.0) ** 1.5   # thẻ bay ease-out: nhanh rồi chậm
    x += swish * env * 0.15
    return Clip(_finish(x, 20.0), 0)


def tick_card(note: str = "E6", seed: str = "tick-card") -> Clip:
    """Thẻ tới bảng CRM, thành một dòng: tick như tickUi V2 (sine AD 0,5 / 25 ms + H2 0,15 + click bp 2–6 kHz 4 ms)
    + tiếng "khớp" vào dòng (sine 300 Hz tắt 15 ms)."""
    n = _n(0.09)
    x = dsp.osc_sine(dsp.hz(note), n) * dsp.env_ad(n, 0.0005, 0.025)
    x += dsp.osc_sine(2 * dsp.hz(note), n) * dsp.env_ad(n, 0.0005, 0.012) * 0.15
    x += dsp.bp(dsp.noise_white(n, f"{seed}:click"), 2000.0, 6000.0) * dsp.env_ad(n, 0.0002, 0.004) * 0.35
    x += dsp.osc_sine(300.0, n) * _decay(n, 0.015, 0.0008) * 0.2
    return Clip(_finish(x, 8.0), 0)


def tick_row(note: str = "E6", seed: str = "tick-row") -> Clip:
    """Dòng CRM hiện ra lúc tua cả đêm: tick nhỏ hơn, ngắn hơn (sine AD 0,4 / 15 ms + click bp 2,5–7 kHz 2 ms)."""
    n = _n(0.06)
    x = dsp.osc_sine(dsp.hz(note), n) * dsp.env_ad(n, 0.0004, 0.015)
    x += dsp.bp(dsp.noise_white(n, f"{seed}:click"), 2500.0, 7000.0) * dsp.env_ad(n, 0.0002, 0.002) * 0.3
    return Clip(_finish(x, 6.0), 0)


def ff_sweep(dur_s: float, seed: str = "ff") -> Clip:
    """Tua cả đêm 22:59 → 07:00: tiếng quét kiểu tua nhanh — nhiễu hồng bp quét 500 → 3500 Hz, rung kim đồng hồ
    quay nhanh dần 12 → 30 Hz (sâu 0,45), tiếng vù sine E4 → E6 rất nhỏ; dâng u^1,3 rồi dừng gọn 25 ms ở 07:00.
    Không phải tape stop (tăng tốc, không hãm), không Shepard (một lượt lên)."""
    n = _n(dur_s)
    t = _t(n)
    u = t / dur_s
    whirr = dsp.sweep_filter(dsp.noise_pink(n, f"{seed}:n"), [500.0, 3500.0], [0.0, 1.0], "band", q_oct=1.0)
    rate = 12.0 + 18.0 * u ** 1.5
    am = 1.0 - 0.45 * (0.5 + 0.5 * np.cos(2 * np.pi * np.cumsum(rate) / SR))
    f = dsp.hz("E4") * 4.0 ** u
    whine = (dsp.osc_sine(f, n) + 0.3 * dsp.osc_sine(2 * f, n)) * 0.08
    x = (whirr / (np.std(whirr) + 1e-12) * 0.25 * am + whine) * u ** 1.3
    r = _n(0.025)
    x[-r:] *= 0.5 + 0.5 * np.cos(np.pi * (np.arange(r) + 1) / r)
    return Clip(dsp.peak_norm(x, PEAK_DBFS), 0)


def ff_rows(rows: int, offset_s: float, span_s: float, seed: str = "ff") -> Clip:
    """Tua cả đêm bản 2 (cột tin cuộn đều, bảng CRM đếm lên, đồng hồ tua 22:51 → 07:00): tiếng vù nhiễu hồng bp 600 → 2800 Hz
    theo tốc độ cuộn (dâng 0,3 s, chạy đều, hạ 0,25 s cuối), rung nhẹ theo nhịp dòng; + một tick nhỏ (E6 / A6 xen, mức
    xen 1 / 0,75) cho mỗi dòng CRM hiện ra ở offset + span·k/rows (+1 f60). Clip dài offset + span + 0,12 s;
    anchor = mốc offset + span (đồng hồ tới 07:00, dòng cuối)."""
    end = offset_s + span_s
    n = _n(end + 0.12)
    t = _t(n)
    whirr = dsp.sweep_filter(dsp.noise_pink(n, f"{seed}:n"), [600.0, 2800.0, 1800.0], [0.0, 0.7, 1.0], "band", q_oct=1.0)
    vel = np.clip(t / 0.3, 0, 1) * np.clip((end - t) / 0.25, 0, 1)
    rate = rows / span_s
    x = whirr / (np.std(whirr) + 1e-12) * 0.18 * vel * (1.0 - 0.3 * (0.5 + 0.5 * np.cos(2 * np.pi * rate * t)))
    for k in range(1, rows + 1):
        tick = tick_row("E6" if k % 2 else "A6", f"{seed}:row{k}").x * (1.0 if k % 2 else 0.75)
        s = _n(offset_s + span_s * k / rows + 1 / 60)
        e = min(n, s + len(tick))
        x[s:e] += tick[:e - s] * 0.55
    x = dsp.fade_edges(x, 3.0, 10.0)
    return Clip(dsp.peak_norm(x, PEAK_DBFS), _n(end))


def buzz(dur_s: float, seed: str = "buzz") -> Clip:
    """Tin đầu rung báo tin trên màn hình (bản 2): động cơ rung trầm 170 Hz (hài 2, 3, bão hòa nhẹ) + chút lạch cạch bp
    0,4–1,6 kHz, lp 1,2 kHz; mạnh theo cú lắc của tin (e^(−4t), lắc 5 Hz), tắt dần 0,12 s cuối đúng lúc tin bay."""
    n = _n(dur_s)
    t = _t(n)
    f = 170.0
    motor = np.tanh(1.5 * (dsp.osc_sine(f, n) + 0.5 * dsp.osc_sine(2 * f, n) + 0.25 * dsp.osc_sine(3 * f, n)))
    rattle = dsp.bp(dsp.noise_white(n, f"{seed}:rattle"), 400.0, 1600.0) * 0.15
    env = np.exp(-4.0 * t) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 5.0 * t))) * np.clip((dur_s - t) / 0.12, 0, 1)
    x = dsp.lp(motor + rattle, 1200.0, 2) * env
    return Clip(dsp.peak_norm(dsp.fade_edges(x, 4.0, 3.0), PEAK_DBFS), 0)


def strike(dur_s: float, seed: str = "strike") -> Clip:
    """Nét gạch "Bỏ sót khách" (bản 2): tiếng nét bút quét — nhiễu trắng bp quét 2,5 → 6 kHz (q 1,2 oct) theo nét chạy,
    hạt nhám nhẹ; dâng 15 ms, giữ, tắt 20 ms ở cuối nét. Neo end = khung nét gạch xong."""
    n = _n(dur_s)
    x = dsp.sweep_filter(dsp.noise_white(n, f"{seed}:n"), [2500.0, 6000.0], [0.0, 1.0], "band", q_oct=1.2)
    g = np.abs(dsp.lp(dsp.noise_white(n, f"{seed}:g"), 90.0, 2))
    x *= 0.7 + 0.3 * g / (np.max(g) + 1e-12)
    u = np.arange(n) / max(n - 1, 1)
    x *= 0.8 + 0.2 * u
    return Clip(dsp.peak_norm(dsp.fade_edges(x, 15.0, 20.0), PEAK_DBFS), 0)


def cta_pop(lead_s: float, seed: str = "cta") -> Clip:
    """Nút CTA bật: luồng hơi hp 2,5 kHz dâng (t/T)² trong lead_s (từ lúc nút bắt đầu bật) kết vào tick quãng 5 E6 + B6
    (sine AD 1 / 60 ms, H2 0,1, click bp 2–6 kHz 3 ms) đúng đỉnh nút. anchor = đỉnh tick."""
    lead = _n(lead_s)
    m = _n(0.12)
    x = np.zeros(lead + m)
    u = np.arange(lead) / max(lead, 1)
    x[:lead] = dsp.hp(dsp.noise_white(lead, f"{seed}:lift"), 2500.0, 2) * u ** 2 * 0.2
    tick = np.zeros(m)
    for note in ("E6", "B6"):
        tick += dsp.osc_sine(dsp.hz(note), m) * dsp.env_ad(m, 0.001, 0.06) * 0.5
        tick += dsp.osc_sine(2 * dsp.hz(note), m) * dsp.env_ad(m, 0.001, 0.03) * 0.05
    tick += dsp.bp(dsp.noise_white(m, f"{seed}:click"), 2000.0, 6000.0) * dsp.env_ad(m, 0.0002, 0.003) * 0.3
    x[lead:] += tick
    x = _finish(x, 15.0)
    return Clip(x, lead + int(np.argmax(np.abs(x[lead:lead + _n(0.01)]))))


# ---------- nền ----------
def dawn_mix(t: np.ndarray) -> np.ndarray:
    """Đêm → ngày đúng như hình: dayMix = clamp01((t − dawn) / (day − dawn)) của timeline.js (đều, tuyến tính)."""
    a, b = C.MOTION["dawn"]
    return np.clip((t - a) / (b - a), 0.0, 1.0)


def bed_room(dur_s: float, seed: str = "room") -> Clip:
    """Tiếng phòng rất nhỏ: nhiễu hồng lp 650 Hz, hp 45 Hz (đêm) chuyển dần sang phòng sáng thoáng hơn (lp 1,1 kHz)
    theo đúng đường trời sáng của hình (dawn_mix); trôi ±0,7 dB rất chậm (0,13 Hz); vào 0,4 s. Kết ở cú cắt 2D."""
    n = _n(dur_s)
    t = _t(n)
    night = dsp.hp(dsp.lp(dsp.noise_pink(n, f"{seed}:night"), 650.0, 2), 45.0, 2)
    day = dsp.hp(dsp.lp(dsp.noise_pink(n, f"{seed}:day"), 1100.0, 2), 60.0, 2)
    k = dawn_mix(t)
    x = night * (1 - k) + day * k * 0.9
    x *= (1.0 + 0.08 * np.sin(2 * np.pi * 0.13 * t + 1.0)) * np.minimum(t / 0.4, 1.0)
    return Clip(dsp.peak_norm(x, PEAK_DBFS), 0)


HUM_PARTIALS = ((110.0, 0.35), (220.0, 1.0), (330.0, 0.5), (440.0, 0.22), (660.0, 0.12))   # chỉ A và E: hợp mọi hợp âm
HUM_DUCK = (2.0, 2.5)          # bass + kick vào ở ô 2 (score_thumon_music PLAN): ù màn hình lùi xuống


def bed_hum(dur_s: float, seed: str = "hum") -> Clip:
    """Tiếng ù màn hình điện thoại khổng lồ ban đêm: hài 1, 2, 3, 4, 6 của A2 (110 Hz: chỉ nốt A và E, không C#) + bản lệch 0,4 Hz cho
    phách chậm, chút rè saw lp 1,2 kHz, hiss 3–6 kHz rất nhỏ. Mức: rõ ở đêm mở đầu, nhỏ đi khi bass và kick vào
    (HUM_DUCK), nhỏ dần đều theo trời sáng (dawn_mix) và tắt hẳn đúng lúc ngày lên (BEATS.day)."""
    n = _n(dur_s)
    t = _t(n)
    x = np.zeros(n)
    for f, a in HUM_PARTIALS:
        x += a * (dsp.osc_sine(f, n) + 0.5 * dsp.osc_sine(f + 0.4, n, 1.3))
    x += dsp.lp(dsp.osc_saw(110.0, n), 1200.0, 2) * 0.06
    x += dsp.bp(dsp.noise_white(n, f"{seed}:hiss"), 3000.0, 6000.0) * 0.015
    lvl = (1.0 - 0.55 * _smoothstep(t, *HUM_DUCK)) * (1.0 - dawn_mix(t))
    x *= lvl * (1.0 + 0.1 * np.sin(2 * np.pi * 0.25 * t)) * np.minimum(t / 0.6, 1.0)
    return Clip(dsp.peak_norm(x, PEAK_DBFS), 0)


# ---------- dispatch ----------
NEW_KINDS = ("bed", "pop", "catch", "save", "card", "tickCard", "tickRow", "ffSweep", "cta", "snortBo", "land",
             "push", "hornTok", "flickTok", "slide", "exhale", "teeter", "buzz", "bob", "inhale", "strike")


def _dur(ev: dict) -> float:
    if "durF" not in ev:
        raise ValueError(f"cue {ev['id']}: thiếu durF")
    return float(ev["durF"]) / dsp.FPS


def _new(ev: dict, seed: str) -> Clip:
    kind = ev["kind"]
    main, flags, style = parse_variant(ev.get("variant"))
    if kind == "bed":
        return bed_hum(_dur(ev), seed) if main == "hum" else bed_room(_dur(ev), seed)
    if kind == "pop":
        return pop(main or "E4", seed)
    if kind == "catch":
        return catch("A4" if style == "C" else main or "A4", style, "ring" in flags, seed)
    if kind == "save":
        return save(main if main in STYLES else style, seed)
    if kind == "card":
        return card(seed)
    if kind == "tickCard":
        return tick_card(main or "E6", seed)
    if kind == "tickRow":
        return tick_row(main or "E6", seed)
    if kind == "ffSweep":
        if ":" in main:                              # bản 2: "dòng:offset:span" → tick mỗi dòng CRM, neo manual
            rows, off, span = main.split(":")
            return ff_rows(int(rows), float(off), float(span), seed)
        return ff_sweep(_dur(ev), seed)
    if kind == "cta":
        return cta_pop(_dur(ev), seed)
    if kind == "snortBo":
        return bo.snort_bo(float(main), "slow" in flags, seed)
    if kind == "land":
        return bo.land(main, style, seed)
    if kind == "push":
        return bo.push(seed)
    if kind == "hornTok":
        return bo.horn_tok(seed)
    if kind == "flickTok":
        return bo.flick_tok(seed)
    if kind == "slide":
        u0, u1 = (float(v) for v in main.split(":"))
        return bo.slide(_dur(ev), u0, u1, next((f for f in flags if f in ("E", "slow")), ""), seed)
    if kind == "exhale":
        return bo.exhale(_dur(ev), seed, burst=main == "burst")
    if kind == "inhale":
        return bo.inhale(_dur(ev), seed)
    if kind == "bob":
        return bo.bob(seed)
    if kind == "buzz":
        return buzz(_dur(ev), seed)
    if kind == "strike":
        return strike(_dur(ev), seed)
    if kind == "teeter":
        return bo.teeter(seed)
    raise ValueError(f"render: kind {kind!r} không hỗ trợ (cue {ev['id']})")


def raw_clip(ev: dict, sheet_id: str) -> Clip:
    """Clip gốc (chưa đệm PRE): kind mới → hàm ở trên / score_thumon_bo; sonicLogo → sonic_logo V2; còn lại → synth V2."""
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
    if anchor == "manual":
        return Clip(x, pre + int(clip.anchor))
    prepped = np.abs(mixbus.prep_clip(Clip(x, 0), ev["kind"]).x)
    return Clip(x, int(np.argmax(prepped)))


def make_render(sheet_id: str):
    return lambda ev: render_cue(ev, sheet_id)
