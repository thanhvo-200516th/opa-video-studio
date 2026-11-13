"""Nhạc V3 "Khám sức khỏe AI": hybrid 120 BPM, 20 s, mono 48 kHz, tự tổng hợp 100 %.

Dùng lại nguyên nhạc cụ (voices.py), dựng lớp (score_v2_layers.py) và hằng trộn của V2 (score_v2.py) bằng import;
file này chỉ có lịch hợp âm / lớp riêng của V3 và cân mức theo đoạn. Mốc (band-drop, music-cut, music-stop,
section full / land, motif) đọc từ sheet v3-ai-audit.json.

Đường năng lượng: pad + nhịp nhẹ ở 0,0 → thêm bass, kick ở 4,0 → kick 4 phách, hats ở 8,0 → thân đầy 10–15 s,
hats dâng 14–15 → lặn 15,0 (band rút, còn pad) → lặng 15,4–15,5 → đáp A add9 cùng cú logo 15,5 → dừng 17,2.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import dsp
import score_v2 as V2
import score_v2_layers as L
import score_v2_sched as S
import synth
import voices
from dsp import FPS, SR

BODY_LUFS = V2.BODY_LUFS          # −20, trùng REF của mixbus
BEAT_S = 0.5
FADE_IN_S = 0.3                   # nhạc vào nhẹ ở 0,0
TAIL_S = 0.3                      # đuôi vang bus sau music-stop
PAD_LP_STEPS = ((0.0, 700.0), (2.0, 1100.0), (4.0, 1400.0), (10.0, 2000.0), (14.0, 2400.0),
                (15.0, 1000.0), (15.5, 1400.0))
HAT_RISE = S.HAT_RISE
HAT_PATTERN = S.HAT_PATTERN
BODY = frozenset({"pad", "pulse16", "bass8", "kick4", "hats", "snap"})


@dataclass(frozen=True)
class Seg:
    t0: float
    t1: float
    chord: str
    pad: tuple[str, ...]
    bass: str | None
    layers: frozenset[str]          # pad, pulse8, pulse16, bassW, bass4, bass8, kick13, kick4, hats, hatrise, snap
    lu: tuple[float, float] | None  # LU so với thân ở đầu/cuối đoạn; None = giữ gain đoạn trước (lặn)
    pulse: tuple[float, float] = (2400.0, 1.0)   # LP Hz, gain của pulse


def _f(*names: str) -> frozenset[str]:
    return frozenset(names)


PLAN = (
    Seg(0.0, 2.0, "D add9", ("D3", "E3", "F#3", "A3"), "D2", _f("pad", "pulse8"), (-10.0, -8.5), (700.0, 0.5)),
    Seg(2.0, 4.0, "Esus4", ("E3", "A3", "B3"), "E2", _f("pad", "pulse8", "bassW"), (-8.0, -7.0), (900.0, 0.6)),
    Seg(4.0, 6.0, "F#m7", ("F#3", "A3", "C#4", "E4"), "F#2", _f("pad", "pulse8", "bass4", "kick13"),
        (-6.0, -5.5), (1200.0, 0.8)),
    Seg(6.0, 8.0, "D add9", ("D3", "E3", "F#3", "A3"), "D2", _f("pad", "pulse16", "bass8", "kick13"),
        (-5.0, -4.5), (1600.0, 0.9)),
    Seg(8.0, 9.0, "Bm7", ("D3", "F#3", "A3", "B3"), "B1", _f("pad", "pulse16", "bass8", "kick4", "hats"),
        (-3.5, -3.0), (2000.0, 1.0)),
    Seg(9.0, 10.0, "E7", ("E3", "G#3", "B3", "D4"), "E2", _f("pad", "pulse16", "bass8", "kick4", "hats"),
        (-3.0, -2.5), (2000.0, 1.0)),
    Seg(10.0, 12.0, "A add9", ("A3", "B3", "C#4", "E4"), "A2", BODY, (-0.5, -0.5)),
    Seg(12.0, 14.0, "F#m7", ("F#3", "A3", "C#4", "E4"), "F#2", BODY, (0.0, 0.0)),
    Seg(14.0, 15.0, "Esus4", ("E3", "A3", "B3"), "E2", BODY | {"hatrise"}, (0.5, 1.5), (3000.0, 1.0)),
    Seg(15.0, 15.4, "E", ("E3", "G#3", "B3"), None, _f("pad"), None),
    Seg(15.5, 17.2, "A add9", ("A3", "C#4", "E4"), "A2", _f("pad", "bass8", "kick4", "hats"), (-3.0, -3.0)),
)


@dataclass(frozen=True)
class Marks:
    drop: float     # giây
    cut: float
    hit: float      # section land bắt đầu (cú logo)
    stop: float
    motif: tuple[tuple[float, str], ...]


def _mark(sheet: dict, mid: str) -> float:
    found = S.marks(sheet, mid)
    if len(found) != 1:
        raise ValueError(f"sheet: cần đúng 1 mark {mid!r}, có {len(found)}")
    return found[0]["f"] / FPS


def marks_of(sheet: dict) -> Marks:
    """Mốc nhạc từ sheet; kiểm khớp với PLAN (đoạn lặn / đáp)."""
    m = Marks(drop=_mark(sheet, "band-drop"), cut=_mark(sheet, "music-cut"),
              hit=S.section(sheet, "land")[0] / FPS, stop=_mark(sheet, "music-stop"),
              motif=tuple((x["f"] / FPS, x["note"]) for x in S.marks(sheet, "motif")))
    dive, land = PLAN[-2], PLAN[-1]
    if (dive.t0, dive.t1, land.t0, land.t1) != (m.drop, m.cut, m.hit, m.stop):
        raise ValueError(f"PLAN lệch sheet: lặn {dive.t0}–{dive.t1}, đáp {land.t0}–{land.t1} so với {m}")
    return m


def _s(t: float) -> int:
    return int(round(t * SR))


def _fr(t: float) -> float:
    return t * FPS


def band_ok(m: Marks, t: float) -> bool:
    return t < m.drop or m.hit <= t < m.stop


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


def _steps(seg: Seg, step_s: float, m: Marks) -> list[float]:
    k = int(round((seg.t1 - seg.t0) / step_s))
    return [seg.t0 + i * step_s for i in range(k) if band_ok(m, seg.t0 + i * step_s)]


def pulse_bars(m: Marks) -> list:
    out = []
    for seg in PLAN:
        lay = seg.layers & {"pulse8", "pulse16"}
        if not lay or not seg.bass:
            continue
        step = BEAT_S / (4 if "pulse16" in lay else 2)
        steps = [_fr(t) for t in _steps(seg, step, m)]
        out.append((steps, S.note_octave(seg.bass, 2), _fr(step), seg.pulse[0], seg.pulse[1]))
    return out


def bass_notes(m: Marks) -> list[tuple[str, float, float]]:
    out = []
    for seg in PLAN:
        if not seg.bass:
            continue
        lay = seg.layers
        step = BEAT_S / 2 if "bass8" in lay else BEAT_S if "bass4" in lay else \
            (seg.t1 - seg.t0) if "bassW" in lay else None
        if step is None:
            continue
        out += [(seg.bass, _fr(t), _fr(step)) for t in _steps(seg, step, m)]
    return out


def _beat_hits(m: Marks, want) -> list[float]:
    """Phách (giây) mà want(seg, chỉ số phách trong ô 4 phách) đúng."""
    out = []
    for seg in PLAN:
        for t in _steps(seg, BEAT_S, m):
            if want(seg, int(round(t / BEAT_S)) % 4):
                out.append(t)
    return out


def kick_onsets(m: Marks) -> list[float]:
    return [_fr(t) for t in _beat_hits(m, lambda s, k: "kick4" in s.layers or ("kick13" in s.layers and k in (0, 2)))]


def snap_onsets(m: Marks) -> list[float]:
    return [_fr(t) for t in _beat_hits(m, lambda s, k: "snap" in s.layers and k in (1, 3))]


def hat_hits(m: Marks) -> list[tuple[float, float]]:
    out = []
    for seg in PLAN:
        if "hats" not in seg.layers:
            continue
        for i, t in enumerate(_steps(seg, BEAT_S / 4, m)):
            if "hatrise" in seg.layers:
                q = (t - seg.t0) / (seg.t1 - seg.t0)
                v = HAT_RISE[0] + (HAT_RISE[1] - HAT_RISE[0]) * q
            else:
                v = HAT_PATTERN[int(round((t - seg.t0) / (BEAT_S / 4))) % 4]
            out.append((_fr(t), v))
    return out


# ---------- dựng ----------
def _layers(m: Marks, seed: str, n: int) -> dict[str, np.ndarray]:
    steps = [(_fr(t), hz) for t, hz in PAD_LP_STEPS]
    cutoff = L.pad_cutoff(n, steps)
    hats = [voices.hat(f"{seed}:hat:{k}") for k in range(4)]
    snaps = [voices.snap(f"{seed}:snap:{k}") for k in range(2)]
    kicks = kick_onsets(m)
    motif = [(_fr(t), note) for t, note in m.motif]
    g = V2.GAIN
    return {
        "pad": L.pad_layer(pad_events(), cutoff, n, seed) * g["pad"],
        "pulse": L.pulse_layer(pulse_bars(m), n, seed) * g["pulse"],
        "bass": L.bass_layer(bass_notes(m), n) * g["bass"],
        "kick": L.hits_layer([voices.kick_soft(synth.ROOT_HZ)], [(f, 1.0) for f in kicks], n) * g["kick"],
        "hats": L.hits_layer(hats, hat_hits(m), n) * g["hats"],
        "snap": L.hits_layer(snaps, [(f, 1.0) for f in snap_onsets(m)], n) * g["snap"],
        "pluck": L.pluck_layer(motif, n, seed),
        "_sc": L.sidechain(kicks, n),
        "_motif": np.array([dsp.f2s(f) for f, _ in motif], dtype=np.int64),
    }


def _gates(m: Marks, n: int) -> tuple[np.ndarray, np.ndarray]:
    """(cửa toàn nhạc, cửa band). Vào nhẹ FADE_IN_S; [cut, hit) = 0; band rút ở drop; dừng ở stop."""
    cut, hit = _s(m.cut), _s(m.hit)
    g = L.fade_to_zero(n, cut, V2._ms(V2.FADE_CUT_MS))
    g[hit:] = 1.0
    g *= L.fade_to_zero(n, _s(m.stop), V2._ms(V2.FADE_STOP_MS))
    k = _s(FADE_IN_S)
    g[:k] *= 0.5 - 0.5 * np.cos(np.pi * np.arange(k) / k)
    band = L.fade_to_zero(n, _s(m.drop), V2._ms(V2.FADE_DROP_MS))
    band[hit:] = 1.0
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


def _hold(g: np.ndarray, m: Marks) -> np.ndarray:
    """Đoạn lặn giữ gain cuối đoạn trước; [cut, hit) và sau stop giữ gain kề để làm mượt không lan qua cú logo."""
    g = g.copy()
    d0, cut, hit, stop = _s(m.drop), _s(m.cut), _s(m.hit), _s(m.stop)
    g[d0:cut] = g[d0 - 1]
    g[cut:hit] = g[hit]
    g[stop:] = g[stop - 1]
    return 10 ** (V2._smooth(g, V2._ms(V2.SMOOTH_MS)) / 20)


def render_music(sheet: dict, seed: str = "v3-music") -> np.ndarray:
    """Stem nhạc dài đúng totalFrames·SPF mẫu; [music-cut, cú logo) = 0 tuyệt đối, sau music-stop chỉ còn đuôi vang
    bus TAIL_S rồi 0."""
    m = marks_of(sheet)
    n = int(sheet["totalFrames"]) * dsp.SPF
    ly = _layers(m, seed, n)
    sc = ly["_sc"]
    gate, band = _gates(m, n)
    pluck = ly["pluck"] * sc * V2._pluck_gain(ly["pad"], ly["pluck"], ly["_motif"])
    pad, pulse, bass = ly["pad"] * sc, ly["pulse"] * sc * band, ly["bass"] * sc * band
    raw = pad + pulse + bass + pluck * band + (ly["kick"] + ly["hats"] + ly["snap"]) * band
    send = pad * V2.SEND["pad"] + pluck * band * V2.SEND["pluck"] + pulse * V2.SEND["pulse"]
    cut, hit, stop = _s(m.cut), _s(m.hit), _s(m.stop)
    segs = [(0, cut, cut - V2._ms(V2.FADE_CUT_MS), cut), (hit, stop, stop, stop + _s(TAIL_S))]
    ir = dsp.reverb_ir(f"{seed}:bus-ir", dur_s=V2.IR_S, decay=V2.IR_DECAY, lp_fc=V2.IR_LP)

    def mix(g_db: np.ndarray) -> np.ndarray:
        gain = _hold(g_db, m) * gate
        y = raw * gain + L.bus_wet(send * gain, segs, ir, V2.WET)
        return np.tanh(y * V2.GLUE_DRIVE) / V2.GLUE_DRIVE

    shape, wins = _shape(n)
    g = shape + _err(raw * 10 ** (shape / 20), wins)
    g = g + _err(mix(g), wins)
    out = mix(g)
    peak = float(np.max(np.abs(out)))
    return out * (0.98 / peak) if peak > 0.98 else out
