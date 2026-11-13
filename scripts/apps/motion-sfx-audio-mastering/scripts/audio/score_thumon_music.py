"""Nhạc phim 3D "Thủ môn" BẢN 2: 120 BPM đều (phách 0,5 s, lưới gốc 0,0 s), La thứ → La trưởng, mono 48 kHz, tự tổng hợp
100 % bằng nhạc cụ của voices.py.

Dùng lại nguyên dựng lớp (score_v2_layers.py) và hằng trộn của V2 (score_v2.py) bằng import; file này chỉ có lịch hợp âm,
lớp và mức theo đoạn của phim. Mốc (downbeat, music-cut, music-resume, pad-open, pad-release, brass-stab) đọc từ sheet
thu-mon.json; PLAN phải khớp sheet (lệch → ValueError).

Bản 2 không còn chỗ khựng hay dừng nhịp: nhịp chạy liền từ 0,0 tới cú cắt 16,00, mọi cú hứng rơi đúng phách.
Đường năng lượng: đêm (pad Am lọc tối, pulse 1/8 rất nhỏ giữ nhịp) → 2,0 bass 1/4 + kick phách 1, 3 → 4,0 Fmaj7: pulse 1/16,
kick 4 phách, hats → 6,0 G: đầy (snap) → 8,0 tua cả đêm F | G, hats dâng → 10,0 sáng ra D add9 (La trưởng, ấm, sáng) →
11,5 cú gạch: E → 12,0 câu chốt "Không bỏ sót khách": A add9 + kèn stab (như V2 tick-thesis + brass-stab) → 14,0 Esus4,
hats dâng, lấy đà → 14,85 vùng xanh bung: E (sus giải về trưởng), nhịp đầy tới cú cắt 16,00 → swell (SFX) nối vào logo
16,60: A add9 ngân, nhả tự nhiên từ 18,80, tắt trước 21,0 s (không fade-out).
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
STEP16 = BEAT_S / 4
FADE_IN_S = 0.3
TAIL_CUT_S = 0.25                 # đuôi vang bus sau cú cắt 16,00 (swell của SFX nối tiếp tới logo)
TAIL_PAD = {"lp": 1400.0, "lp_end": 450.0, "tau": 0.30}   # A add9 sau logo: nhả mũ τ 0,30 s, lọc khép dần
STAB_CHORD = {"Am": ("A3", "C4", "E4"), "E": ("E3", "G#3", "B3"), "A add9": ("A3", "C#4", "E4", "B4")}
STAB_GAIN = 0.45
BODY = frozenset({"pad", "pulse16", "bass8", "kick4", "hats", "snap"})
GAIN = {**V2.GAIN, "kick": 1.0, "snap": 1.6}   # kick, snap nhẹ hơn V2 (1,2 / 2,0): bớt gai cho limiter
FLOOD_T = 891 / 60                # khung hình vùng xanh bung (14,85 s), như events.json


@dataclass(frozen=True)
class Seg:
    t0: float
    t1: float
    chord: str
    pad: tuple[str, ...]
    bass: str | None                # nốt gốc (pulse = bass + 2 bát độ); chỉ chơi bass khi có lớp bass*
    layers: frozenset[str]          # pad, pulse8, pulse16, bass4, bass8, kick13, kick4, hats, hatrise, snap, tail
    lu: tuple[float, float]         # LU so với thân ở đầu/cuối đoạn
    pulse: tuple[float, float] = (2400.0, 1.0)


def _f(*names: str) -> frozenset[str]:
    return frozenset(names)


PLAN = (
    Seg(0.00, 2.00, "Am", ("A3", "C4", "E4"), "A2", _f("pad", "pulse8"), (-13.0, -11.0), (700.0, 0.45)),
    Seg(2.00, 4.00, "Am", ("A3", "C4", "E4"), "A2", _f("pad", "pulse8", "bass4", "kick13"), (-7.0, -6.0),
        (1100.0, 0.7)),
    Seg(4.00, 6.00, "Fmaj7", ("F3", "A3", "C4", "E4"), "F2", _f("pad", "pulse16", "bass8", "kick4", "hats"),
        (-3.5, -3.0), (1600.0, 0.9)),
    Seg(6.00, 8.00, "G", ("G3", "B3", "D4"), "G2", BODY, (-1.5, -1.0), (2000.0, 1.0)),
    Seg(8.00, 9.00, "F", ("F3", "A3", "C4"), "F2", BODY, (-0.5, 0.0), (2200.0, 1.0)),
    Seg(9.00, 10.00, "G", ("G3", "B3", "D4"), "G2", BODY | {"hatrise"}, (0.0, 0.5), (2600.0, 1.0)),
    Seg(10.00, 11.50, "D add9", ("D3", "E3", "F#3", "A3"), "D2", BODY, (-1.0, -0.5), (2400.0, 1.0)),
    Seg(11.50, 12.00, "E", ("E3", "G#3", "B3"), "E2", BODY, (0.0, 0.0), (2600.0, 1.0)),
    Seg(12.00, 14.00, "A add9", ("A3", "B3", "C#4", "E4"), "A2", BODY, (0.5, 0.5), (2600.0, 1.0)),
    Seg(14.00, FLOOD_T, "Esus4", ("E3", "A3", "B3"), "E2", BODY | {"hatrise"}, (0.5, 1.5), (3000.0, 1.0)),
    Seg(FLOOD_T, 16.00, "E", ("E3", "G#3", "B3"), "E2", BODY, (1.5, 1.5), (3000.0, 1.0)),
    Seg(16.60, 21.00, "A add9", ("A3", "B3", "C#4", "E4"), None, _f("tail"), (-10.5, -10.5)),
)
PAD_LP_STEPS = ((0.0, 650.0), (2.0, 1000.0), (4.0, 1500.0), (6.0, 2000.0), (8.0, 2200.0), (10.0, 2400.0),
                (12.0, 2600.0), (14.85, 2800.0))


@dataclass(frozen=True)
class Marks:
    downbeat: float
    cut: float                      # cắt sang end card 2D
    resume: float                   # logo
    release: float
    stabs: tuple[tuple[float, str, float], ...]


def _one(sheet: dict, mid: str) -> float:
    found = S.marks(sheet, mid)
    if len(found) != 1:
        raise ValueError(f"sheet: cần đúng 1 mark {mid!r}, có {len(found)}")
    return found[0]["f"] / FPS


def marks_of(sheet: dict) -> Marks:
    """Mốc nhạc từ sheet; kiểm PLAN khớp (gốc lưới, sáng ra, câu chốt, cú cắt, logo)."""
    m = Marks(downbeat=_one(sheet, "downbeat"), cut=_one(sheet, "music-cut"), resume=_one(sheet, "music-resume"),
              release=_one(sheet, "pad-release"),
              stabs=tuple((x["f"] / FPS, x["note"], float(x["durS"])) for x in S.marks(sheet, "brass-stab")))
    pairs = (("downbeat", PLAN[0].t0, m.downbeat), ("cắt", PLAN[-2].t1, m.cut), ("logo", PLAN[-1].t0, m.resume),
             ("pad-open", PLAN[6].t0, _one(sheet, "pad-open")),
             ("brass-stab câu chốt", PLAN[8].t0, m.stabs[0][0] if m.stabs else -1.0))
    bad = [f"{k}: PLAN {a:g} ≠ sheet {b:g}" for k, a, b in pairs if abs(a - b) > 1e-6]
    if bad:
        raise ValueError(f"PLAN lệch sheet: {'; '.join(bad)}")
    return m


def _s(t: float) -> int:
    return int(round(t * SR))


def _fr(t: float) -> float:
    return t * FPS


def grid(m: Marks, t0: float, t1: float, step: float) -> list[float]:
    """Điểm lưới (giây) trong [t0, t1), lưới gốc ở downbeat."""
    k0 = int(np.ceil(round((t0 - m.downbeat) / step, 9)))
    out, k = [], k0
    while True:
        t = round(m.downbeat + k * step, 9)
        if t >= t1 - 1e-9:
            return out
        out.append(t)
        k += 1


def _beat_idx(m: Marks, t: float) -> int:
    return int(round((t - m.downbeat) / BEAT_S)) % 4


# ---------- lịch nốt ----------
def pad_events() -> list[tuple[str, float, float]]:
    """(nốt, f0, f1) frame 30; nốt chung giữa hai đoạn liền nhau được nối; lớp tail làm riêng."""
    events: list[list] = []
    open_: dict[str, list] = {}
    last = None
    for seg in PLAN:
        if "pad" not in seg.layers:
            open_, last = {}, None
            continue
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


def pulse_bars(m: Marks) -> list:
    out = []
    for seg in PLAN:
        lay = seg.layers & {"pulse8", "pulse16"}
        if not lay or not seg.bass:
            continue
        step = BEAT_S / (4 if "pulse16" in lay else 2)
        steps = [_fr(t) for t in grid(m, seg.t0, seg.t1, step)]
        out.append((steps, S.note_octave(seg.bass, 2), _fr(step), seg.pulse[0], seg.pulse[1]))
    return out


def bass_notes(m: Marks) -> list[tuple[str, float, float]]:
    out = []
    for seg in PLAN:
        if not seg.bass:
            continue
        if "bass8" in seg.layers:
            out += [(seg.bass, _fr(t), _fr(BEAT_S / 2)) for t in grid(m, seg.t0, seg.t1, BEAT_S / 2)]
        elif "bass4" in seg.layers:
            out += [(seg.bass, _fr(t), _fr(BEAT_S)) for t in grid(m, seg.t0, seg.t1, BEAT_S)]
        elif "bassW" in seg.layers:
            out.append((seg.bass, _fr(seg.t0), _fr(seg.t1 - seg.t0)))
    return out


def kick_onsets(m: Marks) -> list[float]:
    out = []
    for seg in PLAN:
        for t in grid(m, seg.t0, seg.t1, BEAT_S):
            if "kick4" in seg.layers or ("kick13" in seg.layers and _beat_idx(m, t) in (0, 2)):
                out.append(_fr(t))
    return out


def snap_onsets(m: Marks) -> list[float]:
    return [_fr(t) for seg in PLAN if "snap" in seg.layers for t in grid(m, seg.t0, seg.t1, BEAT_S)
            if _beat_idx(m, t) in (1, 3)]


def hat_hits(m: Marks) -> list[tuple[float, float]]:
    out = []
    for seg in PLAN:
        if "hats" not in seg.layers:
            continue
        for t in grid(m, seg.t0, seg.t1, STEP16):
            if "hatrise" in seg.layers:
                q = (t - seg.t0) / (seg.t1 - seg.t0)
                v = S.HAT_RISE[0] + (S.HAT_RISE[1] - S.HAT_RISE[0]) * q
            else:
                v = S.HAT_PATTERN[int(round((t - m.downbeat) / STEP16)) % 4]
            out.append((_fr(t), v))
    return out


# ---------- lớp ----------
def stab_layer(m: Marks, n: int, seed: str) -> np.ndarray:
    """Kèn stab (voices.brass, attack 10 ms) ở các mark brass-stab (bản 2: A add9 đúng câu chốt 12,00, như V2)."""
    out = np.zeros(n)
    for k, (t, chord, dur) in enumerate(m.stabs):
        x = voices.brass([(nm, 0.0, dur) for nm in STAB_CHORD[chord]], attack_s=0.01, seed=f"{seed}:stab:{k}")
        L.add_at(out, _s(t), x)
    return out * STAB_GAIN


def tail_layer(m: Marks, n: int, seed: str) -> np.ndarray:
    """A add9 ngân từ logo: pad lọc 1,4 kHz, giữ tới pad-release rồi nhả mũ τ 0,30 s, lọc khép dần về 450 Hz (−60 dBFS ≈ 20,35 s,
    mẫu cuối < −80 dBFS: tắt tự nhiên đúng lúc hết phim, không fade-out)."""
    seg = PLAN[-1]
    s0, sr = _s(seg.t0), _s(m.release)
    k = n - s0
    t = np.arange(k) / SR
    rel = t >= (sr - s0) / SR
    tr = np.where(rel, t - (sr - s0) / SR, 0.0)
    cutoff = np.where(rel, TAIL_PAD["lp_end"] + (TAIL_PAD["lp"] - TAIL_PAD["lp_end"]) * np.exp(-tr / 0.6), TAIL_PAD["lp"])
    x = voices.pad(list(seg.pad), k, cutoff, f"{seed}:tail")
    x *= np.where(rel, np.exp(-tr / TAIL_PAD["tau"]), 1.0)
    out = np.zeros(n)
    out[s0:] = x * L.PAD_NOTE_GAIN * len(seg.pad)       # cùng tỉ lệ với pad_layer (mỗi nốt × PAD_NOTE_GAIN)
    return out


def _layers(m: Marks, seed: str, n: int) -> dict[str, np.ndarray]:
    cutoff = L.pad_cutoff(n, [(_fr(t), hz) for t, hz in PAD_LP_STEPS])
    kicks = kick_onsets(m)
    g = GAIN
    return {
        "pad": L.pad_layer(pad_events(), cutoff, n, seed) * g["pad"],
        "tail": tail_layer(m, n, seed) * g["pad"],
        "pulse": L.pulse_layer(pulse_bars(m), n, seed) * g["pulse"],
        "bass": L.bass_layer(bass_notes(m), n) * g["bass"],
        "kick": L.hits_layer([voices.kick_soft(synth.ROOT_HZ)], [(f, 1.0) for f in kicks], n) * g["kick"],
        "hats": L.hits_layer([voices.hat(f"{seed}:hat:{k}") for k in range(4)], hat_hits(m), n) * g["hats"],
        "snap": L.hits_layer([voices.snap(f"{seed}:snap:{k}") for k in range(2)],
                             [(f, 1.0) for f in snap_onsets(m)], n) * g["snap"],
        "stab": stab_layer(m, n, seed) * g["brass"],
        "_sc": L.sidechain(kicks, n),
    }


def _gate(m: Marks, n: int) -> np.ndarray:
    """Cửa toàn nhạc: vào nhẹ 0,3 s; [cắt, logo) = 0 (fade 4 ms kết đúng mốc cắt). Không có chỗ dừng nào khác."""
    g = L.fade_to_zero(n, _s(m.cut), V2._ms(V2.FADE_CUT_MS))
    g[_s(m.resume):] = 1.0
    k = _s(FADE_IN_S)
    g[:k] *= 0.5 - 0.5 * np.cos(np.pi * np.arange(k) / k)
    return g


def _shape(n: int, m: Marks) -> tuple[np.ndarray, list[tuple[int, int, int, float]]]:
    """Hình gain trong đoạn (dB, trung bình 0) và cửa sổ (s0, hết áp gain, hết đo, mức đích LUFS). Đoạn tail đo phần
    giữ (tới pad-release) nhưng áp cùng gain cho cả phần nhả, để đuôi tắt đúng đường mũ đã thiết kế."""
    shape, wins = np.zeros(n), []
    for seg in PLAN:
        s0, s1 = _s(seg.t0), min(_s(seg.t1), n)
        lu = np.linspace(seg.lu[0], seg.lu[1], s1 - s0)
        shape[s0:s1] = lu - lu.mean()
        meas = _s(m.release) if "tail" in seg.layers else s1
        wins.append((s0, s1, meas, BODY_LUFS + float(lu.mean())))
    return shape, wins


def _err(x: np.ndarray, wins) -> np.ndarray:
    err = np.zeros(len(x))
    for s0, s1, meas, target in wins:
        level = dsp.lufs_integrated(x[s0:meas])
        if level < -70.0:
            raise ValueError(f"mẫu {s0}: đoạn không có nhạc để cân mức")
        err[s0:s1] = target - level
    return err


def _hold(g: np.ndarray, m: Marks) -> np.ndarray:
    """Khoảng cắt giữ gain của logo (làm mượt không lan qua mốc nối lại)."""
    g = g.copy()
    g[_s(m.cut):_s(m.resume)] = g[_s(m.resume)]
    return 10 ** (V2._smooth(g, V2._ms(V2.SMOOTH_MS)) / 20)


def render_music(sheet: dict, seed: str = "thumon-music") -> np.ndarray:
    """Stem nhạc dài đúng totalFrames·SPF mẫu; sau cú cắt chỉ còn đuôi vang bus (TAIL_CUT_S) rồi 0 tuyệt đối tới logo."""
    m = marks_of(sheet)
    n = int(sheet["totalFrames"]) * dsp.SPF
    ly = _layers(m, seed, n)
    sc = ly["_sc"]
    gate = _gate(m, n)
    pad, pulse, bass = ly["pad"] * sc, ly["pulse"] * sc, ly["bass"] * sc
    raw = pad + ly["tail"] + pulse + bass + ly["kick"] + ly["hats"] + ly["snap"] + ly["stab"]
    send = (pad + ly["tail"]) * V2.SEND["pad"] + pulse * V2.SEND["pulse"] + ly["stab"] * V2.SEND["brass"]
    cut, resume = _s(m.cut), _s(m.resume)
    segs = [(0, cut, cut - V2._ms(V2.FADE_CUT_MS), _s(m.cut + TAIL_CUT_S)), (resume, n, n, n)]
    ir = dsp.reverb_ir(f"{seed}:bus-ir", dur_s=V2.IR_S, decay=V2.IR_DECAY, lp_fc=V2.IR_LP)

    def mix(g_db: np.ndarray) -> np.ndarray:
        gain = _hold(g_db, m) * gate
        y = raw * gain + L.bus_wet(send * gain, segs, ir, V2.WET)
        return np.tanh(y * V2.GLUE_DRIVE) / V2.GLUE_DRIVE

    shape, wins = _shape(n, m)
    g = shape + _err(raw * 10 ** (shape / 20), wins)
    g = g + _err(mix(g), wins)
    out = mix(g)
    peak = float(np.max(np.abs(out)))
    return out * (0.98 / peak) if peak > 0.98 else out
