"""Nhạc nền "OPA Agent × Pancake" (ae/opa-agent, 36 s): hybrid 120 BPM giọng La trưởng, mono 48 kHz, tự tổng hợp 100 %.

Dùng lại nhạc cụ (voices.py), dựng lớp (score_v2_layers.py) và hằng trộn của V2 (score_v2.py) như V3; file này chỉ có
lịch hợp âm theo 5 cảnh và cân mức theo đoạn. Mỗi đoạn nhạc có phách 1 riêng (GRID): cảnh 3 vào ở 13,5 s, cảnh 4 ở
22,0 s, cảnh 5 đáp cùng logo âm thanh ở 30,4 s, nên cú "đáp" luôn rơi đúng phách 1.

Đường năng lượng (LU so với thân):
- 0–5 s hook (đêm): F#m7 → D add9 → Esus4, pad tối + pulse 8, bass tròn; −6,5 → −5.
- 5–12,87 s nỗi đau: pulse 16, bass, kick phách 1–3 rồi 4 phách, hats dâng 11–12,87; −4,5 → −2.
- 12,87 s Bò lao vào: band rút, còn pad E; 13,1 s đĩa sáng bật: lặng tới 13,5 s (SFX swell lấp chỗ).
- 13,5–22 s giải pháp (ngày): thân đầy A add9 → E/G# → F#m7 → D add9 (kick 4 phách, hats, snap); +0,5 → 0.
- 22–29,5 s giải phóng: nhẹ lại, kick nửa nhịp; −2,5. 29,5 s band rút; 29,93–30,4 s lặng (whoosh khung xanh, logo).
- 30,4–36 s CTA: đáp A add9 cùng logo âm thanh; −2,5 → −3; tắt dần 1,5 s, kết đúng 36,0 s.
Xử lý nền theo quy trình 1.2.3 Minh đã duyệt: lọc dưới 100 Hz, −3 dB ở 2 kHz, vào dần 1 s, tắt dần 1,5 s.
Cung năng lượng giữ dải độ to (LRA) ≤ 5 LU như nền 1.2.3. Mức tuyệt đối (15 LU dưới giọng đọc) đặt ở AE bằng gain layer, không đặt ở đây.

Chạy: python tools/audio/score_agent.py <out.wav>
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import dsp
import score_v2 as V2
import score_v2_layers as L
import score_v2_sched as S
import synth
import voices
from dsp import FPS, SR

TOTAL_S = 36.0
BEAT_S = 0.5
BODY_LUFS = V2.BODY_LUFS                       # −20: mức phần thân của stem
GRID = (0.0, 13.5, 22.0, 30.4)                 # phách 1 của từng đoạn nhạc
DIVES = ((12.87, 13.1, 13.5), (29.5, 29.93, 30.4))   # (band rút, lặng, đáp)
FADE_IN_S, FADE_OUT_S = 1.0, 1.5
HP_HZ, DIP_HZ, DIP_DB, DIP_Q = 100.0, 2000.0, -3.0, 1.0
PAD_LP = ((0.0, 700.0), (2.0, 1000.0), (4.0, 1300.0), (5.0, 1400.0), (9.0, 1700.0), (11.0, 2000.0),
          (12.87, 1200.0), (13.5, 2400.0), (22.0, 1800.0), (29.5, 1200.0), (30.4, 2000.0), (34.4, 1400.0))
HAT_RISE, HAT_PATTERN = S.HAT_RISE, S.HAT_PATTERN


def _f(*names: str) -> frozenset[str]:
    return frozenset(names)


BODY = _f("pad", "pulse16", "bass8", "kick4", "hats", "snap")
DIVE = _f("pad")


@dataclass(frozen=True)
class Seg:
    t0: float
    t1: float
    chord: str
    pad: tuple[str, ...]
    bass: str | None
    layers: frozenset[str]          # pad, pulse8, pulse16, bassW, bass4, bass8, kick13, kick4, hats, hatrise, snap
    lu: tuple[float, float] | None  # LU so với thân ở đầu/cuối đoạn; None = giữ gain đoạn trước (đoạn lặn)
    pulse: tuple[float, float] = (2400.0, 1.0)   # LP Hz, gain của pulse


FSM7, DADD9, ESUS4, AADD9 = ("F#3", "A3", "C#4", "E4"), ("D3", "E3", "F#3", "A3"), ("E3", "A3", "B3"), ("A3", "B3", "C#4", "E4")
PLAN = (
    # cảnh 1 · hook
    Seg(0.0, 2.0, "F#m7", FSM7, "F#2", _f("pad", "pulse8"), (-6.5, -6.0), (700.0, 0.5)),
    Seg(2.0, 4.0, "D add9", DADD9, "D2", _f("pad", "pulse8", "bassW"), (-6.0, -5.5), (900.0, 0.6)),
    Seg(4.0, 5.0, "Esus4", ESUS4, "E2", _f("pad", "pulse8", "bassW"), (-5.5, -5.0), (1100.0, 0.7)),
    # cảnh 2 · nỗi đau
    Seg(5.0, 7.0, "F#m7", FSM7, "F#2", _f("pad", "pulse16", "bass4", "kick13"), (-4.5, -4.0), (1200.0, 0.8)),
    Seg(7.0, 9.0, "D add9", DADD9, "D2", _f("pad", "pulse16", "bass8", "kick13"), (-4.0, -3.5), (1500.0, 0.9)),
    Seg(9.0, 11.0, "Bm7", ("D3", "F#3", "A3", "B3"), "B1", _f("pad", "pulse16", "bass8", "kick4", "hats"),
        (-3.0, -2.5), (1800.0, 1.0)),
    Seg(11.0, 12.87, "Esus4", ESUS4, "E2", _f("pad", "pulse16", "bass8", "kick4", "hats", "hatrise"),
        (-2.5, -2.0), (2400.0, 1.0)),
    Seg(12.87, 13.1, "E", ("E3", "G#3", "B3"), None, DIVE, None),
    # cảnh 3 · giải pháp (phách 1 = 13,5)
    Seg(13.5, 15.5, "A add9", AADD9, "A2", BODY, (0.5, 0.0)),
    Seg(15.5, 17.5, "E/G#", ("G#3", "B3", "E4"), "G#2", BODY, (0.0, 0.0)),
    Seg(17.5, 19.5, "F#m7", FSM7, "F#2", BODY, (0.0, 0.0)),
    Seg(19.5, 21.5, "D add9", DADD9, "D2", BODY, (0.0, 0.0)),
    Seg(21.5, 22.0, "Esus4", ESUS4, "E2", _f("pad", "pulse16", "bass8", "kick4", "hats", "hatrise"), (-0.5, 0.0)),
    # cảnh 4 · giải phóng (phách 1 = 22,0)
    Seg(22.0, 24.0, "A add9", AADD9, "A2", _f("pad", "pulse8", "bass4", "kick13"), (-2.5, -2.5), (1600.0, 0.8)),
    Seg(24.0, 26.0, "D add9", DADD9, "D2", _f("pad", "pulse8", "bass4", "kick13"), (-2.5, -2.5), (1600.0, 0.8)),
    Seg(26.0, 28.0, "A/C#", ("A3", "C#4", "E4"), "C#2", _f("pad", "pulse8", "bass4", "kick13", "hats"),
        (-2.5, -2.5), (1800.0, 0.8)),
    Seg(28.0, 29.5, "Esus4", ESUS4, "E2", _f("pad", "pulse8", "bass8", "kick13", "hats", "hatrise"),
        (-2.5, -2.0), (2000.0, 0.9)),
    Seg(29.5, 29.93, "E", ("E3", "G#3", "B3"), None, DIVE, None),
    # cảnh 5 · CTA (phách 1 = 30,4, cùng logo âm thanh)
    Seg(30.4, 32.4, "A add9", ("A3", "C#4", "E4"), "A2", _f("pad", "bass8", "kick4", "hats"), (-2.5, -2.5)),
    Seg(32.4, 34.4, "D add9", DADD9, "D2", _f("pad", "bass8", "kick4", "hats"), (-2.5, -2.5)),
    Seg(34.4, 36.0, "A add9", AADD9, "A2", _f("pad", "bass4"), (-3.0, -3.0)),
)


def _s(t: float) -> int:
    return int(round(t * SR))


def _fr(t: float) -> float:
    return t * FPS


def band_ok(t: float) -> bool:
    """Band (mọi lớp trừ pad) chỉ vang ngoài các đoạn [band rút, đáp)."""
    return not any(d <= t < h for d, _, h in DIVES)


def beat_in_bar(t: float) -> int:
    """Chỉ số phách 0..3 trong ô, tính từ phách 1 của đoạn nhạc chứa t."""
    origin = max(g for g in GRID if g <= t + 1e-9)
    return int(round((t - origin) / BEAT_S)) % 4


# ---------- lịch nốt ----------
def pad_events() -> list[tuple[str, float, float]]:
    """(nốt, f0, f1); nốt chung giữa hai đoạn liền nhau được nối."""
    events: list[list] = []
    open_: dict[str, list] = {}
    last = None
    for seg in PLAN:
        if last != seg.t0:
            open_ = {}
        nxt = {}
        for name in seg.pad:
            ev = open_.get(name) or [name, _fr(seg.t0), 0.0]
            if name not in open_:
                events.append(ev)
            ev[2] = _fr(seg.t1)
            nxt[name] = ev
        open_, last = nxt, seg.t1
    return [tuple(e) for e in events]


def _steps(seg: Seg, step_s: float) -> list[float]:
    k = int(round((seg.t1 - seg.t0) / step_s))
    return [seg.t0 + i * step_s for i in range(k) if band_ok(seg.t0 + i * step_s)]


def pulse_bars() -> list:
    out = []
    for seg in PLAN:
        lay = seg.layers & {"pulse8", "pulse16"}
        if not lay or not seg.bass:
            continue
        step = BEAT_S / (4 if "pulse16" in lay else 2)
        out.append(([_fr(t) for t in _steps(seg, step)], S.note_octave(seg.bass, 2), _fr(step), seg.pulse[0], seg.pulse[1]))
    return out


def bass_notes() -> list[tuple[str, float, float]]:
    out = []
    for seg in PLAN:
        if not seg.bass:
            continue
        lay = seg.layers
        step = BEAT_S / 2 if "bass8" in lay else BEAT_S if "bass4" in lay else \
            (seg.t1 - seg.t0) if "bassW" in lay else None
        if step is not None:
            out += [(seg.bass, _fr(t), _fr(step)) for t in _steps(seg, step)]
    return out


def _beat_hits(want) -> list[float]:
    return [t for seg in PLAN for t in _steps(seg, BEAT_S) if want(seg, beat_in_bar(t))]


def kick_onsets() -> list[float]:
    return [_fr(t) for t in _beat_hits(lambda s, k: "kick4" in s.layers or ("kick13" in s.layers and k in (0, 2)))]


def snap_onsets() -> list[float]:
    return [_fr(t) for t in _beat_hits(lambda s, k: "snap" in s.layers and k in (1, 3))]


def hat_hits() -> list[tuple[float, float]]:
    out = []
    for seg in PLAN:
        if "hats" not in seg.layers:
            continue
        for t in _steps(seg, BEAT_S / 4):
            if "hatrise" in seg.layers:
                v = HAT_RISE[0] + (HAT_RISE[1] - HAT_RISE[0]) * (t - seg.t0) / (seg.t1 - seg.t0)
            else:
                v = HAT_PATTERN[int(round((t - seg.t0) / (BEAT_S / 4))) % 4]
            out.append((_fr(t), v))
    return out


# ---------- dựng ----------
def _layers(seed: str, n: int) -> dict[str, np.ndarray]:
    cutoff = L.pad_cutoff(n, [(_fr(t), hz) for t, hz in PAD_LP])
    hats = [voices.hat(f"{seed}:hat:{k}") for k in range(4)]
    snaps = [voices.snap(f"{seed}:snap:{k}") for k in range(2)]
    kicks = kick_onsets()
    g = V2.GAIN
    return {
        "pad": L.pad_layer(pad_events(), cutoff, n, seed) * g["pad"],
        "pulse": L.pulse_layer(pulse_bars(), n, seed) * g["pulse"],
        "bass": L.bass_layer(bass_notes(), n) * g["bass"],
        "kick": L.hits_layer([voices.kick_soft(synth.ROOT_HZ)], [(f, 1.0) for f in kicks], n) * g["kick"],
        "hats": L.hits_layer(hats, hat_hits(), n) * g["hats"],
        "snap": L.hits_layer(snaps, [(f, 1.0) for f in snap_onsets()], n) * g["snap"],
        "_sc": L.sidechain(kicks, n),
    }


def _gates(n: int) -> tuple[np.ndarray, np.ndarray]:
    """(cửa toàn nhạc, cửa band): lặng tuyệt đối trong [lặng, đáp); band rút từ band rút tới đáp."""
    g, band = np.ones(n), np.ones(n)
    for drop, cut, hit in DIVES:
        a, b = L.fade_to_zero(n, _s(cut), V2._ms(V2.FADE_CUT_MS)), L.fade_to_zero(n, _s(drop), V2._ms(V2.FADE_DROP_MS))
        a[_s(hit):] = 1.0
        b[_s(hit):] = 1.0
        g, band = g * a, band * b
    return g, band


def _shape(n: int) -> tuple[np.ndarray, list[tuple[int, int, float]]]:
    """Hình gain trong đoạn (dB, trung bình 0) và cửa sổ đo (s0, s1, mức đích LUFS)."""
    shape, wins = np.zeros(n), []
    for seg in PLAN:
        if seg.lu is None:
            continue
        s0, s1 = _s(seg.t0), _s(seg.t1)
        lu = np.linspace(seg.lu[0], seg.lu[1], s1 - s0)
        shape[s0:s1] = lu - lu.mean()
        wins.append((s0, s1, BODY_LUFS + float(lu.mean())))
    return shape, wins


def _err(x: np.ndarray, wins) -> np.ndarray:
    err = np.zeros(len(x))
    for s0, s1, target in wins:
        level = dsp.lufs_integrated(x[s0:s1])
        if level < -70.0:
            raise ValueError(f"mẫu {s0}: đoạn không có nhạc để cân mức")
        err[s0:s1] = target - level
    return err


def _hold(g: np.ndarray) -> np.ndarray:
    """Đoạn lặn giữ gain cuối đoạn trước; [lặn, đáp) giữ gain đoạn đáp để làm mượt không lan qua cú đáp."""
    g = g.copy()
    for drop, cut, hit in DIVES:
        g[_s(drop):_s(cut)] = g[_s(drop) - 1]
        g[_s(cut):_s(hit)] = g[_s(hit)]
    return 10 ** (V2._smooth(g, V2._ms(V2.SMOOTH_MS)) / 20)


def render_music(seed: str = "agent-music") -> np.ndarray:
    n = _s(TOTAL_S)
    ly = _layers(seed, n)
    sc = ly["_sc"]
    gate, band = _gates(n)
    pad, pulse, bass = ly["pad"] * sc, ly["pulse"] * sc * band, ly["bass"] * sc * band
    raw = pad + pulse + bass + (ly["kick"] + ly["hats"] + ly["snap"]) * band
    send = pad * V2.SEND["pad"] + pulse * V2.SEND["pulse"]
    fade = V2._ms(V2.FADE_CUT_MS)
    (_, c1, h1), (_, c2, h2) = DIVES
    segs = [(0, _s(c1), _s(c1) - fade, _s(c1)), (_s(h1), _s(c2), _s(c2) - fade, _s(c2)), (_s(h2), n, n, n)]
    ir = dsp.reverb_ir(f"{seed}:bus-ir", dur_s=V2.IR_S, decay=V2.IR_DECAY, lp_fc=V2.IR_LP)

    def mix(g_db: np.ndarray) -> np.ndarray:
        gain = _hold(g_db) * gate
        y = raw * gain + L.bus_wet(send * gain, segs, ir, V2.WET)
        return np.tanh(y * V2.GLUE_DRIVE) / V2.GLUE_DRIVE

    shape, wins = _shape(n)
    g = shape + _err(raw * 10 ** (shape / 20), wins)
    g = g + _err(mix(g), wins)
    return mix(g)


def bed(x: np.ndarray) -> np.ndarray:
    """Xử lý nền dưới giọng: lọc dưới 100 Hz, −3 dB ở 2 kHz, vào dần 1 s, tắt dần 1,5 s kết đúng cuối."""
    y = dsp.peaking(dsp.hp(x, HP_HZ, order=2), DIP_HZ, DIP_DB, DIP_Q)
    k, m = _s(FADE_IN_S), _s(FADE_OUT_S)
    y[:k] *= 0.5 - 0.5 * np.cos(np.pi * np.arange(k) / k)
    y[-m:] *= 0.5 + 0.5 * np.cos(np.pi * (np.arange(m) + 1) / m)
    peak = float(np.max(np.abs(y)))
    return y * (0.89 / peak) if peak > 0.89 else y   # đỉnh mẫu ≤ −1 dBFS


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    out = Path(sys.argv[1])
    y = bed(render_music())
    out.parent.mkdir(parents=True, exist_ok=True)
    dsp.write_wav_f32(out, y)
    print(f"OK {out} · {len(y) / SR:.3f} s · I {dsp.lufs_integrated(y):.1f} LUFS · đỉnh {20 * np.log10(np.max(np.abs(y))):.1f} dBFS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
