"""Nhạc V2 "Không bỏ sót khách": hybrid 120 BPM, 30 s, mono 48 kHz, tự tổng hợp 100 % (TK §7.1, KH §3.9).

Sắp xếp lớp (pad / pulse / bass / kick / hats / snap / pluck / stab, sidechain từ kick, vang bus) tham khảo
kinetic-reel template/music/score.mjs (MIT, © 2026 tuzhechen2005), viết lại bằng Python với nhạc cụ của voices.py.
Mọi frame lấy từ sheet (sections, marks, silences); nhịp từ beatFrames/barFrames. Lịch nốt ở score_v2_sched.py,
dựng lớp ở score_v2_layers.py.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import dsp
import score_v2_layers as L
import score_v2_sched as S
import synth
import voices
from dsp import SR

BODY_LUFS = -20.0   # mức phần thân (0 LU), trùng REF của mixbus (E) nên E gần như không phải cân lại


@dataclass(frozen=True)
class BarPlan:
    bar: int                  # 1..15
    chord: str                # "Am", "Fmaj7", "Dm7", "G", "Esus4>E", "A add9", "E/G#", "F#m7", "D add9", "A/C#", "Esus4", ""
    bass: tuple[str, ...]     # rỗng = không bass
    pad: tuple[str, ...]      # mọi nốt ≥ MIDI 48; "X>Y": nốt cuối thay nốt thứ 2 từ mark esus-to-e
    layers: frozenset[str]    # trong {"pad","pulse8","pulse16","bass4","bass8","kick13","kick4","hats","snap","pluck"}


_BODY = ("pad", "pulse16", "bass8", "kick4", "hats", "snap")
_PLAN = (  # ô, hợp âm, bass, pad, lớp (bass có mà không bass4/bass8 = nốt tròn)
    (1, "Am", (), ("A3", "C4", "E4"), ("pad",)),
    (2, "Fmaj7", ("F2",), ("F3", "A3", "C4", "E4"), ("pad", "pulse8", "pluck")),
    (3, "Dm7", ("D2",), ("D3", "F3", "A3", "C4"), ("pad", "pulse8", "bass4")),
    (4, "G", ("G2",), ("G3", "B3", "D4"), ("pad", "pulse8", "bass8", "kick13")),
    (5, "Esus4>E", ("E2",), ("E3", "A3", "B3", "G#3"), ("pad", "pulse16", "bass8", "kick4", "hats")),
    (6, "A add9", ("A2",), ("A3", "B3", "C#4", "E4"), _BODY),
    (7, "E/G#", ("G#2",), ("G#3", "B3", "E4"), _BODY),
    (8, "F#m7", ("F#2",), ("F#3", "A3", "C#4", "E4"), _BODY),
    (9, "D add9", ("D2",), ("D3", "E3", "F#3", "A3"), _BODY),
    (10, "A/C#", ("C#2",), ("A3", "C#4", "E4"), _BODY),
    (11, "D add9", ("D2",), ("D3", "E3", "F#3", "A3"), ("pad", "pulse8")),
    (12, "Esus4", ("E2",), ("E3", "A3", "B3"), ("pad", "pulse8")),
    (13, "", (), (), ()),
    (14, "", (), (), ()),
    (15, "", (), (), ()),
)

# Mức LU so với phần thân ở đầu/cuối ô (TK §7.1), LP Hz và gain của pulse trong ô
BAR_MIX = {
    1: (-6.0, -6.0, 0.0, 0.0), 2: (-5.0, -5.0, 900.0, 0.5), 3: (-4.0, -4.0, 1200.0, 0.8),
    4: (-2.5, -2.5, 1600.0, 0.9), 5: (-1.5, -1.0, 3000.0, 1.0), 6: (2.5, 2.5, 2400.0, 1.0),
    7: (0.0, 0.0, 2400.0, 1.0), 8: (0.0, 0.0, 2400.0, 1.0), 9: (0.0, 0.0, 2400.0, 1.0),
    10: (-0.5, -0.5, 2400.0, 1.0), 11: (-4.5, -4.5, 1000.0, 0.8), 12: (-4.5, -4.5, 1000.0, 0.8),
}
PAD_LP_NIGHT = 700.0                                    # trước mark pad-open
PAD_LP = {"intro": 1400.0, "build": 1400.0, "rise": 1400.0, "full": 2200.0, "breath": 1400.0}
# Cân lớp (RMS phần thân so với pad): bass ≈ 0, kick ≈ −3, pulse ≈ −7, snap ≈ −14, hats ≈ −20 dB
GAIN = {"pad": 1.0, "pulse": 0.45, "bass": 0.55, "kick": 1.2, "hats": 5.0, "snap": 2.0, "brass": 0.6}
PLUCK_UNDER_PAD_DB = -12.0                              # motif nằm dưới pad 12 dB (RMS 100 ms đầu)
SEND = {"pad": 1.0, "pluck": 1.0, "brass": 1.0, "pulse": 0.3}
WET, IR_S, IR_DECAY, IR_LP = 0.18, 1.2, 4.5, 4000.0
FADE_CUT_MS, FADE_DROP_MS, FADE_STOP_MS, SMOOTH_MS = 4.0, 5.0, 8.0, 20.0
GLUE_DRIVE = 1.6
TAIL_PAD, TAIL_PAD_LU, TAIL_PAD_LP = ("A3", "B3", "C#4", "E4"), -9.0, 1400.0   # chỉ bản A/B


def chord_plan() -> list[BarPlan]:
    """15 ô đúng TK §7.1; ô 13–15 không band."""
    return [BarPlan(b, c, tuple(bs), tuple(pd), frozenset(ly)) for b, c, bs, pd, ly in _PLAN]


def brass_events(sheet: dict) -> list[tuple[float, float]]:
    """(frame, giây giữ) của brass stab trong nhạc, từ marks brass-stab."""
    return [(m["f"], m["durS"]) for m in S.marks(sheet, "brass-stab")]


def _ms(ms: float) -> int:
    return int(round(ms * SR / 1000))


def _smooth(x: np.ndarray, w: int) -> np.ndarray:
    """Trung bình trượt căn giữa (cumsum, đệm mép)."""
    h = w // 2
    ext = np.concatenate([np.full(h, x[0]), x, np.full(w - h, x[-1])])
    c = np.concatenate([[0.0], np.cumsum(ext)])
    return (c[w:w + len(x)] - c[:len(x)]) / w


def _layers(sheet: dict, tl: S.Timeline, seed: str, n: int) -> dict[str, np.ndarray]:
    plan = chord_plan()
    steps = [(0.0, PAD_LP_NIGHT), (tl.pad_open, PAD_LP["intro"])]
    steps += [(a, PAD_LP[name]) for name, a, _ in tl.sections if name in PAD_LP and name != "intro"]
    cutoff = L.pad_cutoff(n, sorted(steps))
    hats = [voices.hat(f"{seed}:hat:{k}") for k in range(4)]
    snaps = [voices.snap(f"{seed}:snap:{k}") for k in range(2)]
    kicks = S.kick_onsets(plan, tl)
    motif = [(m["f"], m["note"]) for m in S.marks(sheet, "motif")]
    return {
        "pad": L.pad_layer(S.pad_events(plan, tl), cutoff, n, seed) * GAIN["pad"],
        "pulse": L.pulse_layer(S.pulse_bars(plan, tl, BAR_MIX), n, seed) * GAIN["pulse"],
        "bass": L.bass_layer(S.bass_notes(plan, tl), n) * GAIN["bass"],
        "kick": L.hits_layer([voices.kick_soft(synth.ROOT_HZ)], [(f, 1.0) for f in kicks], n) * GAIN["kick"],
        "hats": L.hits_layer(hats, S.hat_hits(plan, tl), n) * GAIN["hats"],
        "snap": L.hits_layer(snaps, [(f, 1.0) for f in S.snap_onsets(plan, tl)], n) * GAIN["snap"],
        "pluck": L.pluck_layer(motif, n, seed),
        "brass": L.brass_layer(brass_events(sheet), n, seed) * GAIN["brass"],
        "_sc": L.sidechain(kicks, n),
        "_motif": np.array([dsp.f2s(f) for f, _ in motif], dtype=np.int64),
    }


def _pluck_gain(pad: np.ndarray, pluck: np.ndarray, onsets: np.ndarray) -> float:
    """Gain để RMS 100 ms đầu của pluck thấp hơn pad cùng cửa sổ PLUCK_UNDER_PAD_DB."""
    if len(onsets) == 0:
        return 0.0
    w = _ms(100)
    pd = np.concatenate([pad[s:s + w] for s in onsets])
    pk = np.concatenate([pluck[s:s + w] for s in onsets])
    return 10 ** ((dsp.rms_db(pd) + PLUCK_UNDER_PAD_DB - dsp.rms_db(pk)) / 20)


def _bar_shape(tl: S.Timeline, n: int) -> tuple[np.ndarray, list[tuple[int, int, int, float]]]:
    """Hình gain trong ô (dB, trung bình 0 trên cửa sổ đo) và cửa sổ đo (s0, s1, hết đo, mức đích LUFS).

    Ô chứa band-drop chỉ đo tới band-drop. Mức đích = BODY_LUFS + LU trung bình của ô trên cửa sổ đo.
    """
    shape = np.zeros(n)
    wins = []
    for bar, (lu0, lu1, _, _) in BAR_MIX.items():
        f0, f1 = S.bar_span(tl, bar)
        s0, s1 = dsp.f2s(f0), dsp.f2s(f1)
        meas = dsp.f2s(tl.drop) if f0 < tl.drop < f1 else s1
        lu = np.linspace(lu0, lu1, s1 - s0)
        mean_lu = float(np.mean(lu[:meas - s0]))
        shape[s0:s1] = lu - mean_lu
        wins.append((s0, s1, meas, BODY_LUFS + mean_lu))
    return shape, wins


def _bar_err(x: np.ndarray, wins) -> np.ndarray:
    """Sai số mức (dB) theo ô: đích − loudness đo trên cửa sổ; ngoài các ô = 0."""
    err = np.zeros(len(x))
    for s0, s1, meas, target in wins:
        level = dsp.lufs_integrated(x[s0:meas])
        if level < -70.0:
            raise ValueError(f"mẫu {s0}: ô không có nhạc để cân mức")
        err[s0:s1] = target - level
    return err


def _smooth_gain(g: np.ndarray, tl: S.Timeline) -> np.ndarray:
    """Làm mượt 20 ms; trong khoảng lặng giữ mức ô sau để không làm mượt đè lên phách HIT."""
    g = g.copy()
    hit = dsp.f2s(tl.hit)
    g[dsp.f2s(tl.cut):hit] = g[hit]
    return 10 ** (_smooth(g, _ms(SMOOTH_MS)) / 20)


def _gates(tl: S.Timeline, n: int) -> tuple[np.ndarray, np.ndarray]:
    """(cửa toàn nhạc, cửa band). Lặng [music-cut, HIT) = 0 tuyệt đối; band rút ở band-drop; dừng ở music-stop."""
    cut, hit = dsp.f2s(tl.cut), dsp.f2s(tl.hit)
    g = L.fade_to_zero(n, cut, _ms(FADE_CUT_MS))
    g[hit:] = 1.0
    g *= L.fade_to_zero(n, dsp.f2s(tl.stop), _ms(FADE_STOP_MS))
    band = L.fade_to_zero(n, dsp.f2s(tl.drop), _ms(FADE_DROP_MS))
    band[hit:] = 1.0
    return g, band


def _tail_pad(tl: S.Timeline, n: int, seed: str) -> np.ndarray:
    """Pad A add9 ở −9 LU từ LOGO tới hết (chỉ bản A/B)."""
    s0 = dsp.f2s(tl.logo)
    x = voices.pad(list(TAIL_PAD), n - s0, TAIL_PAD_LP, f"{seed}:tail-pad")
    x = dsp.fade_edges(x, 0.0, 10.0)
    x *= 10 ** ((BODY_LUFS + TAIL_PAD_LU - dsp.lufs_integrated(x)) / 20)
    out = np.zeros(n)
    out[s0:] = x
    return out


def render_music(sheet: dict, seed: str = "v2-music", tail_pad: bool = False) -> np.ndarray:
    """Stem nhạc dài đúng totalFrames·SPF mẫu.

    Lặng: dry và wet = 0 trên [music-cut, HIT) (fade 4 ms kết đúng tại music-cut). band-drop: band fade 5 ms, còn pad.
    music-stop: dry fade 8 ms kết tại mark; vang bus tắt hẳn ở đầu khoảng near. Không nhạc trong section logo
    (trừ tail_pad).
    """
    tl = S.timeline(sheet)
    n = tl.total * dsp.SPF
    ly = _layers(sheet, tl, seed, n)
    sc = ly["_sc"]
    gate, band = _gates(tl, n)
    pluck = ly["pluck"] * sc * _pluck_gain(ly["pad"], ly["pluck"], ly["_motif"])
    pad, pulse, bass = ly["pad"] * sc, ly["pulse"] * sc * band, ly["bass"] * sc * band
    raw = pad + pulse + bass + pluck + (ly["kick"] + ly["hats"] + ly["snap"] + ly["brass"]) * band
    send = pad * SEND["pad"] + pluck * SEND["pluck"] + ly["brass"] * band * SEND["brass"] + pulse * SEND["pulse"]
    cut, hit, stop = dsp.f2s(tl.cut), dsp.f2s(tl.hit), dsp.f2s(tl.stop)
    segs = [(0, cut, cut - _ms(FADE_CUT_MS), cut), (hit, stop, stop, dsp.f2s(tl.tail_end))]
    ir = dsp.reverb_ir(f"{seed}:bus-ir", dur_s=IR_S, decay=IR_DECAY, lp_fc=IR_LP)

    def mix(g_db: np.ndarray) -> np.ndarray:
        gain = _smooth_gain(g_db, tl) * gate
        y = raw * gain + L.bus_wet(send * gain, segs, ir, WET)
        return np.tanh(y * GLUE_DRIVE) / GLUE_DRIVE   # keo bus: lợi 1 ở mức nhỏ, mềm đỉnh kick để limiter master nén ít

    # cân mức 2 lượt: lượt 1 trên dry, lượt 2 trên bản đã có vang bus
    shape, wins = _bar_shape(tl, n)
    g = shape + _bar_err(raw * 10 ** (shape / 20), wins)
    g = g + _bar_err(mix(g), wins)
    out = mix(g)
    peak = float(np.max(np.abs(out)))
    if peak > 0.98:   # chặn trần an toàn (trước pad đuôi để phần trước LOGO giống hệt bản A/B)
        out = out * (0.98 / peak)
    if tail_pad:
        out = out + _tail_pad(tl, n, seed)
    return out
