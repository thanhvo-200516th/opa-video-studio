"""Phép đo riêng của phim 3D "Thủ môn" (G6): đồng bộ va chạm +1 f60, mức ép limiter, bus solo, mật độ onset, mức đoạn.

Hàm thuần trên mảng numpy mono 48 kHz (trừ true_peak_db dùng resample_poly). Mốc lấy từ cue sheet thu-mon.json:
khung hình của một cue va chạm = 2·f30 − 1 (adapter đặt đỉnh ở khung + 1 f60).
"""
from __future__ import annotations

import numpy as np
from scipy.signal import resample_poly

import dsp
import mixbus
import qa_audio_sig as sig

SR = 48000
F60 = SR / 60                     # 800 mẫu
WIN = (-1, 4)                     # cửa sổ tìm đỉnh quanh khung hình, đơn vị f60 (lane A)
TARGET_MS, TARGET_TOL = 1000 / 60, 2.0
EACH_OK = (8.0, 25.0)             # từng tiếng: đạt
EACH_FAIL = (0.0, 33.0)           # từng tiếng: < 0 hoặc > 33 ms là FAIL
IMPACT_KINDS = {"ping", "pop", "catch", "save", "card", "tickCard", "tickRow", "tickUi", "land", "push", "hornTok",
                "flickTok", "bob", "cta"}
ONSET_KINDS = IMPACT_KINDS | {"snortBo", "teeter", "buzz", "exhale"}


def db(v: float) -> float:
    return 20 * np.log10(v) if v > 0 else float("-inf")


def true_peak_db(x: np.ndarray) -> float:
    """Đỉnh thật xấp xỉ: oversample 4× (resample_poly), như score_v3_qa."""
    return sig.peak_db(resample_poly(np.asarray(x, dtype=np.float64), 4, 1))


# ---------- đồng bộ ----------
def event_frames(events: dict, card_flight_f60: int = 24) -> dict[str, int]:
    """Khung hình (f60) của từng cue va chạm lấy THẲNG từ events.json (độc lập với phép đổi f30 của adapter), theo quy
    ước tên: ping-bX ← bX-appear, pop-bX ← bX-launch, catch/save-bX ← bX-catch, land-k ← land-k, bob-k ← bob-k,
    tick-card-bX ← bX-card, card-bX ← bX-card − bay (bản 1), jump-push / horn-tok / flick-tok ← BEATS. Dòng CRM, khối nhấn
    câu chốt và nút CTA không có trong events.json."""
    fr = {e["id"]: e["frame"] for e in events["events"]}
    out = {}
    for eid, f in fr.items():
        b, _, kind = eid.partition("-")
        if kind == "appear":
            out[f"ping-{b}"] = f
        elif kind == "launch":
            out[f"pop-{b}"] = f
        elif kind == "catch":
            out[f"catch-{b}"] = out[f"save-{b}"] = f
        elif kind == "card":
            out[f"tick-card-{b}"], out[f"card-{b}"] = f, f - card_flight_f60
        elif b in ("land", "bob"):
            out[eid] = f
    beats = events.get("beats", {})
    for cid, key in (("jump-push", "jump"), ("horn-tok", "hornLand"), ("flick-tok", "flick")):
        if key in beats:
            out[cid] = int(np.floor(beats[key] * 60 + 0.5))
    return out


def impact_cues(sheet: dict, frames: dict[str, int] | None = None) -> list[dict]:
    """Cue va chạm có âm, kèm khung hình (f60) và cờ chồng (cue va chạm khác cách ≤ 4 f60). Khung lấy từ frames
    (events.json) khi có, không thì suy từ sheet (2·f30 − 1); trường "nguon" ghi nguồn đã dùng."""
    frames = frames or {}
    out = [dict(e, frame60=frames[e["id"]] if e["id"] in frames else round(2 * float(e["f"]) - 1),
                nguon="events.json" if e["id"] in frames else "sheet")
           for e in sheet["events"] if e["sound"] and e["kind"] in IMPACT_KINDS]
    for e in out:
        e["overlap"] = [o["id"] for o in out if o is not e and abs(o["frame60"] - e["frame60"]) <= WIN[1]]
    return out


def peak_offset_ms(x: np.ndarray, frame60: int) -> float | None:
    """Đỉnh |x| trong [khung − 1, khung + 4] f60 so với thời điểm khung hình, ms; None khi không có tín hiệu."""
    n0 = int(round(frame60 * F60))
    lo, hi = max(0, n0 + int(WIN[0] * F60)), min(len(x), n0 + int(WIN[1] * F60) + 1)
    seg = np.abs(x[lo:hi])
    if not len(seg) or seg.max() < 1e-7:
        return None
    return (lo + int(np.argmax(seg)) - n0) * 1000 / SR


def solo(sheet: dict, ev: dict, render) -> np.ndarray:
    """Một cue đặt riêng trên bộ đệm cả phim (prep + gain + neo đúng như mixbus.mix_detail)."""
    buf = np.zeros(int(sheet["totalFrames"]) * dsp.SPF)
    clip = mixbus.prep_clip(render(ev), ev["kind"])
    mixbus.place_at(buf, clip, mixbus.anchor_sample(ev), mixbus.cue_gain_db(clip, ev["gainDb"]))
    return buf


def sync_table(sheet: dict, render, signals: dict[str, np.ndarray], frames: dict[str, int] | None = None) -> list[dict]:
    """Mỗi cue va chạm: lệch đỉnh (ms) đặt riêng + trên từng tín hiệu trong signals (stem sfx, master, MP4…),
    so với khung hình lấy từ events.json (frames) khi có."""
    rows = []
    for e in impact_cues(sheet, frames):
        row = {"id": e["id"], "kind": e["kind"], "frame60": e["frame60"], "nguon": e["nguon"],
               "t": round(e["frame60"] / 60, 4), "overlap": e["overlap"],
               "solo": peak_offset_ms(solo(sheet, e, render), e["frame60"])}
        row.update({k: peak_offset_ms(x, e["frame60"]) for k, x in signals.items()})
        rows.append(row)
    return rows


def sync_summary(rows: list[dict], key: str, clean_only: bool = False) -> dict:
    vals = [r[key] for r in rows if r[key] is not None and (not clean_only or not r["overlap"])]
    if not vals:
        return {"n": 0, "median_ms": None}
    v = np.asarray(vals)
    return {"n": len(vals), "median_ms": round(float(np.median(v)), 2), "min_ms": round(float(v.min()), 2),
            "max_ms": round(float(v.max()), 2), "in_8_25": int(np.sum((v >= EACH_OK[0]) & (v <= EACH_OK[1]))),
            "fail": int(np.sum((v < EACH_FAIL[0]) | (v > EACH_FAIL[1])))}


# ---------- limiter ----------
def gr_rms300_db(mix: np.ndarray, master: np.ndarray, gain_db: float, t: float) -> float:
    """Mức ép RMS 300 ms từ t: (mix + G) − master (cùng phép đo build.gain_reduction_db / qa_audio #8, #9)."""
    n = int(round(t * SR))
    w = int(0.3 * SR)
    return round(sig.rms_db(mix[n:n + w]) + gain_db - sig.rms_db(master[n:n + w]), 2)


def gr_max_5ms(mix: np.ndarray, master: np.ndarray, gain_db: float, floor_db: float = -40.0) -> tuple[float, float]:
    """Ép tối đa theo cửa sổ RMS 5 ms (lane A): (dB, giây). Bỏ cửa sổ có mix + G dưới floor_db."""
    w = int(0.005 * SR)
    k = min(len(mix), len(master)) // w
    ri = np.sqrt(np.mean((mix[:k * w] * 10 ** (gain_db / 20)).reshape(k, w) ** 2, axis=1))
    ro = np.sqrt(np.mean(master[:k * w].reshape(k, w) ** 2, axis=1))
    gr = 20 * np.log10((ri + 1e-12) / (ro + 1e-12))
    gr[20 * np.log10(ri + 1e-12) < floor_db] = 0.0
    i = int(np.argmax(gr))
    return round(float(gr[i]), 2), round(i * w / SR, 3)


def align_lag(a: np.ndarray, b: np.ndarray, t0: float, t1: float, max_lag: int = 200) -> int:
    """Độ trễ (mẫu) của b so với a trong [t0, t1) theo tương quan chéo (master so với mix + G)."""
    s0, s1 = int(t0 * SR), int(t1 * SR)
    ref = a[s0 + max_lag:s1 - max_lag]
    c = np.correlate(b[s0:s1], ref, "valid")
    return int(np.argmax(c)) - max_lag


# ---------- bus ----------
def bus_row(name: str, x: np.ndarray, gain_db: float) -> dict:
    """I, TP (4×), PLR = TP − I của một bus trước master; I + G = mức ở thang master (chưa qua limiter)."""
    i = dsp.lufs_integrated(x)
    tp = true_peak_db(x)
    ok = i > -70
    return {"bus": name, "I": round(i, 2) if ok else None, "TP": round(tp, 2) if np.isfinite(tp) else None,
            "PLR": round(tp - i, 2) if ok else None, "I_master_scale": round(i + gain_db, 2) if ok else None}


def window_lufs(x: np.ndarray, t0: float, t1: float) -> float:
    return round(dsp.lufs_integrated(x[int(t0 * SR):int(t1 * SR)]), 2)


# ---------- một tiếng so với nhạc ----------
PING_BAND = (150.0, 2000.0)       # dải của tiếng ping: A3 / E4 (+3 bán cung lúc vào), click lp 1,5 kHz, lp 2 kHz
PING_WIN = (0.005, 0.100)         # trước / sau đỉnh, giây (ping tắt −23 dB sau 100 ms)


def over_music_db(cue: np.ndarray, music: np.ndarray, band: tuple[float, float] | None = PING_BAND,
                  win: tuple[float, float] = PING_WIN) -> float:
    """Một tiếng đặt riêng (bộ đệm cả phim, như solo) hơn nhạc bao nhiêu dB: RMS trong cùng cửa sổ quanh đỉnh của tiếng,
    cả hai lọc cùng dải (band=None: cả dải). Lọc trên đoạn đệm thêm 0,1 s hai bên cho bộ lọc ổn định."""
    pk = int(np.argmax(np.abs(cue)))
    a, b = pk - int(win[0] * SR), pk + int(win[1] * SR)
    lo, hi = max(0, a - int(0.1 * SR)), min(len(cue), b + int(0.1 * SR))

    def level(x: np.ndarray) -> float:
        y = x[lo:hi] if band is None else dsp.bp(x[lo:hi], *band)
        return sig.rms_db(y[a - lo:b - lo])
    return round(level(cue) - level(music), 2)


# ---------- mật độ, lặp ----------
def onset_density(sheet: dict, win_s: float = 0.25) -> tuple[int, list[tuple[float, list[str]]]]:
    """Số onset SFX (va chạm + hơi phì + chênh vênh) nhiều nhất trong một cửa sổ win_s, và các cửa sổ > 3."""
    ons = sorted((float(e["f"]) / 30, e["id"]) for e in sheet["events"] if e["sound"] and e["kind"] in ONSET_KINDS)
    worst, crowded = 0, []
    for i, (t, _) in enumerate(ons):
        grp = [cid for u, cid in ons[i:] if u - t < win_s - 1e-9]
        worst = max(worst, len(grp))
        if len(grp) > 3:
            crowded.append((round(t, 3), grp))
    return worst, crowded


def same_kind_pairs(sheet: dict, render) -> list[dict]:
    """Hai cue liền nhau cùng kind: khác seed (id) luôn đúng; báo thêm khác cao độ/variant, khác mức, và clip có
    giống hệt nhau không (np.array_equal)."""
    evs = [e for e in sheet["events"] if e["sound"] and e["kind"] not in ("bed",)]
    last: dict[str, dict] = {}
    out = []
    for e in evs:
        p = last.get(e["kind"])
        if p is not None:
            a, b = render(p).x, render(e).x
            same = len(a) == len(b) and bool(np.array_equal(a, b))
            out.append({"a": p["id"], "b": e["id"], "kind": e["kind"], "variant_khac": p.get("variant") != e.get("variant"),
                        "muc_khac": p["gainDb"] != e["gainDb"], "giong_het": same})
        last[e["kind"]] = e
    return out


# ---------- mô tả một tiếng (bộ A/B) ----------
def centroid_hz(x: np.ndarray) -> float:
    """Trọng tâm phổ (Hz) của cả clip."""
    p = np.abs(np.fft.rfft(np.asarray(x, dtype=np.float64))) ** 2
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return round(float(np.sum(f * p) / (np.sum(p) + 1e-20)), 1)


def decay_ms(x: np.ndarray, db_down: float = 40.0) -> float:
    """Từ đỉnh tới lúc bao RMS 2 ms tụt db_down dB lần cuối (ms)."""
    w = int(0.002 * SR)
    env = np.sqrt(np.convolve(np.asarray(x, dtype=np.float64) ** 2, np.ones(w) / w, "same"))
    i0 = int(np.argmax(env))
    above = np.nonzero(env[i0:] >= env[i0] * 10 ** (-db_down / 20))[0]
    return round(float(above[-1]) * 1000 / SR, 1)


def describe(x: np.ndarray) -> dict:
    x = np.asarray(x, dtype=np.float64)
    return {"trong_tam_hz": centroid_hz(x), "tat_40db_ms": decay_ms(x),
            "crest_db": round(sig.peak_db(x) - sig.rms_db(x[np.abs(x) > 1e-6]), 1)}
