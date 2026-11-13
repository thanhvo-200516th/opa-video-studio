"""Trộn V2: đặt SFX theo neo, cân gain theo REF, duck theo cue, EQ bus, khoảng lặng (gói E, KH §3.4, §3.9).

Thứ tự (TK §7.5): nhạc cân REF trên section full → SFX theo neo + gain → duck → bus_eq
→ apply_silences (mix scope "mix", stem nhạc scope "music") → fade-in đầu file 3 ms.
Mọi frame lấy từ sheet (cues.json); không gõ frame trong file này.
"""
from __future__ import annotations

from typing import Callable

import numpy as np

import cues_io
import dsp
from dsp import SR, f2s
from synth import Clip

REF_LUFS = -20.0
SMALL_KINDS = {"ping", "tickUi", "tickCatch", "snort"}   # low-shelf −2,6 dB dưới 90 Hz (≈ −45 % năng lượng)
SMALL_SHELF_HZ, SMALL_SHELF_DB = 90.0, -2.6
KEEP_ATTACK_KINDS = {"hit"}        # impact giữ nguyên attack (không fade-in)
CLIP_FADE_MS = 3.0                 # fade mỗi clip 2–5 ms
FILE_FADE_IN_MS = 3.0
SILENCE_RAMP_MS = 3.0
DUCK_ATTACK_F = 4                  # ramp cosine 4 f kết đúng tại neo
DUCK_HOLD_F = 10                   # giữ tới f + 10
DUCK_RELEASE_N = 9600              # nhả cosine 200 ms
AB_HIT_GAP_DB = 3.0                # A/B: hit logo chỉ thấp hơn hit húc 3 dB
AB_EVENTS = ("whoosh-windup", "hit-logo-3db")
ID_HIT, ID_LOGO, ID_CHARGE = "hit-accent", "hit-logo", "whoosh-charge"


# ---------- đặt clip ----------
def anchor_sample(event: dict) -> int:
    """Mẫu đặt neo: round(f·1600); riêng neo `end` lùi 1 mẫu (clip kết đúng tại biên frame f)."""
    n0 = f2s(event["f"])
    return n0 - 1 if event["anchor"] == "end" else n0


def place_at(bus: np.ndarray, clip, n_anchor: int, gain_db: float) -> tuple[int, int]:
    """Cộng clip·gain vào bus (tại chỗ) sao cho clip.x[clip.anchor] rơi ở n_anchor.
    Cắt phần ra ngoài mép bus. Trả (đầu, cuối) của đoạn đã ghi, cuối là mẫu sau cùng + 1."""
    start = n_anchor - int(clip.anchor)
    s, e = max(start, 0), min(start + len(clip.x), len(bus))
    if e > s:
        bus[s:e] += np.asarray(clip.x[s - start:e - start], dtype=np.float64) * 10 ** (gain_db / 20)
    return s, max(e, s)


def place(bus: np.ndarray, clip, frame: float, gain_db: float) -> tuple[int, int]:
    """Mẫu anchor = f2s(frame); cắt ở mép bus; trả (đầu, cuối)."""
    return place_at(bus, clip, f2s(frame), gain_db)


def cue_gain_db(clip, gain_db: float, ref_lufs: float = REF_LUFS) -> float:
    """Gain (dB) để momentary max của clip = ref + gainDb."""
    return ref_lufs + gain_db - dsp.momentary_max(clip.x)


def prep_clip(clip, kind: str) -> Clip:
    """Bản sao đã vệ sinh: shelf cho SFX nhỏ, fade 3 ms hai đầu (hit giữ attack)."""
    x = np.asarray(clip.x, dtype=np.float64)
    if kind in SMALL_KINDS:
        x = dsp.low_shelf(x, SMALL_SHELF_HZ, SMALL_SHELF_DB)
    x = dsp.fade_edges(x, 0.0 if kind in KEEP_ATTACK_KINDS else CLIP_FADE_MS, CLIP_FADE_MS)
    return Clip(x, int(clip.anchor))


# ---------- duck, EQ, lặng ----------
def duck_curve(n: int, events: list[dict]) -> np.ndarray:
    """Đường gain nhạc (dB, ≤ 0) dài n. Event có duckDb, neo n0 = f2s(f): ramp cosine trên
    [n0 − f2s(4), n0) đạt −duckDb đúng tại n0; giữ tới f2s(f + 10); nhả cosine về 0 trong 9600 mẫu."""
    g = np.zeros(n)
    idx = np.arange(n)
    for ev in events:
        depth = float(ev.get("duckDb", 0.0))
        if depth <= 0:
            continue
        if depth > cues_io.MAX_DUCK_DB:
            raise ValueError(f"duck: {ev['id']} duckDb {depth} > {cues_io.MAX_DUCK_DB:g}")
        n0 = f2s(ev["f"])
        na, n1 = n0 - f2s(DUCK_ATTACK_F), f2s(ev["f"] + DUCK_HOLD_F)
        c = np.zeros(n)
        m = (idx >= na) & (idx < n0)
        c[m] = -depth * 0.5 * (1 - np.cos(np.pi * (idx[m] - na) / (n0 - na)))
        c[(idx >= n0) & (idx < n1)] = -depth
        m = (idx >= n1) & (idx < n1 + DUCK_RELEASE_N)
        c[m] = -depth * 0.5 * (1 + np.cos(np.pi * (idx[m] - n1) / DUCK_RELEASE_N))
        g = np.minimum(g, c)
    return g


def apply_silences(x: np.ndarray, silences: list[dict], scope: str) -> np.ndarray:
    """Bản sao: loại silent đúng scope = 0 tuyệt đối trên [f2s(from), f2s(to)); ramp cosine 3 ms
    kết đúng tại from (nằm ngoài cửa sổ). Không đụng near/allowed."""
    y = np.array(x, dtype=np.float64, copy=True)
    nr = int(round(SILENCE_RAMP_MS * SR / 1000))
    for s in silences:
        if s["kind"] != "silent" or s["scope"] != scope:
            continue
        s0, s1 = f2s(s["from"]), f2s(s["to"])
        r0 = max(s0 - nr, 0)
        k = np.arange(s0 - r0)
        y[r0:s0] *= 0.5 + 0.5 * np.cos(np.pi * (k + 1 + (nr - (s0 - r0))) / nr)
        y[s0:s1] = 0.0
    return y


def bus_eq(x: np.ndarray) -> np.ndarray:
    """HPF 25 Hz bậc 4 + peaking −2 dB @ 250 Hz Q1."""
    return dsp.peaking(dsp.hp(np.asarray(x, dtype=np.float64), 25.0, 4), 250.0, -2.0, 1.0)


# ---------- dựng ----------
def _event_by_id(events: list[dict], cid: str) -> dict:
    for e in events:
        if e["id"] == cid:
            return e
    raise ValueError(f"sheet thiếu cue '{cid}'")


def events_for(sheet: dict, ab: str | None = None) -> list[dict]:
    """Bản sao các event sẽ đặt. ab: None | "whoosh-windup" (bật whoosh-charge, giữ f/durF/neo/gainDb)
    | "hit-logo-3db" (hit-logo = hit-accent − 3 dB)."""
    if ab not in (None, *AB_EVENTS):
        raise ValueError(f"mix: ab {ab!r} không hỗ trợ (chỉ {AB_EVENTS})")
    evs = [dict(e) for e in sheet["events"]]
    if ab == "whoosh-windup":
        _event_by_id(evs, ID_CHARGE)["sound"] = True
    if ab == "hit-logo-3db":
        _event_by_id(evs, ID_LOGO)["gainDb"] = _event_by_id(evs, ID_HIT)["gainDb"] - AB_HIT_GAP_DB
    return [e for e in evs if e["sound"]]


def hit_gap_db(events: list[dict]) -> float:
    """gainDb(hit-accent) − gainDb(hit-logo) của bộ event đã dùng."""
    return float(_event_by_id(events, ID_HIT)["gainDb"] - _event_by_id(events, ID_LOGO)["gainDb"])


def _section(sheet: dict, name: str) -> dict:
    for s in sheet["sections"]:
        if s["name"] == name:
            return s
    raise ValueError(f"sheet thiếu section '{name}'")


def music_to_ref(sheet: dict, music: np.ndarray, ref_lufs: float = REF_LUFS) -> np.ndarray:
    """Cân nhạc để loudness tích hợp trên section full = ref."""
    full = _section(sheet, "full")
    lu = dsp.lufs_integrated(music[f2s(full["from"]):f2s(full["to"])])
    if lu < -70.0:
        raise ValueError(f"nhạc gần như câm trong section full ({lu:.1f} LUFS)")
    return np.asarray(music, dtype=np.float64) * 10 ** ((ref_lufs - lu) / 20)


def mix_detail(sheet: dict, music: np.ndarray, render: Callable[[dict], object],
               ab: str | None = None) -> tuple[dict[str, np.ndarray], list[dict]]:
    """Như mix() nhưng trả thêm danh sách vị trí đặt từng cue (cho build.json)."""
    n = int(sheet["totalFrames"]) * f2s(1)
    if len(music) != n:
        raise ValueError(f"nhạc dài {len(music)} mẫu ≠ totalFrames·SPF = {n}")
    events = events_for(sheet, ab)
    sfx = np.zeros(n)
    placed = []
    for ev in events:
        clip = prep_clip(render(ev), ev["kind"])
        mm = dsp.momentary_max(clip.x)
        gain = cue_gain_db(clip, ev["gainDb"])
        na = anchor_sample(ev)
        s, e = place_at(sfx, clip, na, gain)
        placed.append({"id": ev["id"], "f": ev["f"], "kind": ev["kind"], "start_sample": s, "end_sample": e,
                       "anchor_sample": na, "gain_db": round(gain, 4), "clip_momentary_max": round(mm, 4)})
    duck = 10 ** (duck_curve(n, events) / 20)
    music_eq = bus_eq(music_to_ref(sheet, music) * duck)
    sfx_eq = bus_eq(sfx)
    sil = sheet["silences"]
    out = {"music": apply_silences(music_eq, sil, "music"),
           "sfx": apply_silences(sfx_eq, sil, "mix"),
           "mix": apply_silences(music_eq + sfx_eq, sil, "mix")}
    return {k: dsp.fade_edges(v, FILE_FADE_IN_MS, 0.0) for k, v in out.items()}, placed


def mix(sheet: dict, music: np.ndarray, render: Callable[[dict], object],
        ab: str | None = None) -> dict[str, np.ndarray]:
    """{"music","sfx","mix"}, mỗi stem đúng totalFrames·SPF mẫu."""
    return mix_detail(sheet, music, render, ab)[0]
