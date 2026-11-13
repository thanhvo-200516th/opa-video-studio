"""Phép đo tín hiệu cho qa_audio (gói F): click, neo cue, khoảng lặng, RMS, phổ.

Mọi hàm thuần trên mảng numpy mono 48 kHz; mốc frame lấy từ cues/build.json.
"""
import math

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from scipy.signal import butter, sosfilt, welch

SR = 48000
SPF = 1600                      # mẫu/frame @30 fps
WIN_300MS = int(0.3 * SR)       # cửa sổ RMS 300 ms
HOP_100MS = int(0.1 * SR)
CLICK_RADIUS = int(0.005 * SR)  # ±5 ms quanh điểm nối
CLICK_MEDIAN = int(0.010 * SR)  # median trượt 10 ms
CLICK_RATIO = 8.0               # |diff| > 8 × median trượt
CLICK_FLOOR = 0.002             # bước nhỏ hơn ≈ −54 dBFS thì bỏ qua
CLICK_ISOLATION = 3.0           # bước đơn mẫu: lớn hơn 3 × mọi |diff| cách 2–4 mẫu
BG_FROM, BG_TO = 480, 48        # nền cho onset: max |x| từ 10 ms tới 1 ms trước mẫu
SILENT_PEAK_DB = -60.0
NEAR_FAIL_DB, NEAR_TARGET_DB = -35.0, -45.0
PHONE_BAND = (400.0, 8000.0)    # giả lập loa điện thoại (NC §3.4): band-pass Butterworth bậc 4


def f2s(frame: float) -> int:
    return int(round(frame * SPF))


def db(v: float) -> float:
    return 20.0 * math.log10(v) if v > 0 else float("-inf")


def rms_db(x: np.ndarray) -> float:
    return db(float(np.sqrt(np.mean(np.square(x))))) if len(x) else float("-inf")


def peak_db(x: np.ndarray) -> float:
    return db(float(np.max(np.abs(x)))) if len(x) else float("-inf")


# ---------- click (#4) ----------
def find_clicks(x: np.ndarray) -> np.ndarray:
    """Chỉ số mẫu có bước nhảy đơn mẫu: |diff| > 8 × median của CẢ hai nửa cửa sổ 10 ms
    (5 ms trước, 5 ms sau), đủ lớn và cô lập.

    Hai nửa riêng: đầu một tiếng nhiễu (hats) có nửa sau ồn nên không bị bắt; bước nhảy thật
    nổi hơn cả hai phía. Cô lập (so với |diff| cách 2–4 mẫu): transient có dao động (click bp
    của kick, impact) có mẫu kề cũng lớn nên không bị bắt.
    """
    d = np.abs(np.diff(x))
    nb = np.zeros_like(d)
    for k in (2, 3, 4):
        nb[k:] = np.maximum(nb[k:], d[:-k])
        nb[:-k] = np.maximum(nb[:-k], d[k:])
    cand = np.nonzero((d > CLICK_FLOOR) & (d > CLICK_ISOLATION * nb))[0]
    half = CLICK_MEDIAN // 2
    keep = []
    for i in cand:
        left, right = d[max(0, i - half):i], d[i + 1:i + 1 + half]
        lim = max(np.median(left) if len(left) else 0.0, np.median(right) if len(right) else 0.0)
        if d[i] > CLICK_RATIO * lim:
            keep.append(i)
    return np.asarray(keep, dtype=np.int64) + 1


def split_clicks(clicks: np.ndarray, junctions: list) -> tuple:
    """(click gần điểm nối ±5 ms, click khác)."""
    if not len(clicks):
        return [], []
    j = np.sort(np.asarray(junctions, dtype=np.int64))
    near, other = [], []
    for c in clicks:
        k = np.searchsorted(j, c)
        dist = min(abs(c - j[k - 1]) if k > 0 else 1 << 40, abs(j[k] - c) if k < len(j) else 1 << 40)
        (near if dist <= CLICK_RADIUS else other).append(int(c))
    return near, other


# ---------- neo cue (#6, #7) ----------
def measure_anchor(x: np.ndarray, n_exp: int, anchor: str, w: int):
    """Mẫu đo được của neo trong cửa sổ [n_exp − w, n_exp + w]; None khi không có tín hiệu."""
    lo, hi = max(0, n_exp - w), min(len(x), n_exp + w + 1)
    if hi <= lo:
        return None
    seg = np.abs(x[lo:hi])
    top = float(seg.max())
    if top < 1e-6:
        return None
    if anchor in ("peak", "manual"):
        return lo + int(np.argmax(seg))
    if anchor == "end":  # mẫu cuối trên −40 dB so với đỉnh
        return lo + int(np.nonzero(seg >= 0.01 * top)[0][-1])
    # onset = mẫu đầu vượt −20 dB so với đỉnh VÀ gấp đôi nền (max |x| trong 10 ms → 1 ms trước đó),
    # để đuôi của cue trước (sub-drop, sonic logo) không kéo onset về đầu cửa sổ
    w = BG_FROM - BG_TO
    ctx = np.abs(x[max(0, lo - BG_FROM):lo])  # nền thật trước cửa sổ
    padded = np.concatenate([np.zeros(BG_FROM - len(ctx)), ctx, seg])
    bg = sliding_window_view(padded[:len(seg) + w - 1], w).max(axis=1)[:len(seg)]
    hits = np.nonzero((seg >= 0.1 * top) & (seg >= 2.0 * bg))[0]
    return lo + (int(hits[0]) if len(hits) else int(np.argmax(seg)))


def expected_sample(f: float, anchor: str) -> int:
    return f2s(f) - 1 if anchor == "end" else f2s(f)


def cue_groups(cues: list) -> list:
    """Gộp cue cùng frame: [(f, anchor, [id…])], sắp theo f."""
    groups = {}
    for c in sorted(cues, key=lambda c: c["f"]):
        key = round(float(c["f"]), 6)
        if key not in groups:
            groups[key] = (float(c["f"]), c["anchor"], [])
        groups[key][2].append(c["id"])
    return list(groups.values())


def align_groups(sfx: np.ndarray, groups: list) -> list:
    """Mỗi nhóm → (f, anchor, ids, lệch frame hoặc None). Cửa sổ = min(5 f, nửa khoảng tới nhóm kề)."""
    out = []
    fs = [g[0] for g in groups]
    for i, (f, anchor, ids) in enumerate(groups):
        gaps = [abs(f - fs[j]) for j in (i - 1, i + 1) if 0 <= j < len(fs)]
        w_f = min([5.0] + [g / 2 for g in gaps])
        if anchor == "manual":
            w_f = min(w_f, 2.0)  # snort: chỉ xung 1, tránh đỉnh xung 2 (cách 6 f)
        n_exp = expected_sample(f, anchor)
        n = measure_anchor(sfx, n_exp, anchor, int(w_f * SPF))
        out.append((f, anchor, ids, None if n is None else (n - n_exp) / SPF))
    return out


# ---------- khoảng lặng (#5) ----------
def window(x: np.ndarray, f_from: float, f_to: float, shrink_f: float = 0.0) -> np.ndarray:
    return x[max(0, f2s(f_from + shrink_f)):max(0, f2s(f_to - shrink_f))]


def unexpected_silences(found: list, silences: list, total_s: float, music_stop_f) -> list:
    """Khoảng lặng ffmpeg nằm ngoài silent/near/allowed (dung sai 1 f; allowed nhận đầu ≥ from − 10 f;
    near nhận đầu từ music-stop, vì 4 f đầu sau music-stop dành cho đuôi vang)."""
    tol = 1.0 / 30
    ok_ranges = []
    for s in silences:
        a, b = s["from"] / 30, s["to"] / 30
        if s["kind"] == "allowed":
            a -= 10 / 30
        elif s["kind"] == "near" and music_stop_f is not None and music_stop_f <= s["from"]:
            a = music_stop_f / 30
        ok_ranges.append((a - tol, b + tol))
    bad = []
    for start, end in found:
        end = total_s if end is None else end
        if not any(a <= start and end <= b for a, b in ok_ranges):
            bad.append((round(start * 30, 2), round(end * 30, 2)))
    return bad


# ---------- thứ bậc hit (#8–#10) ----------
def rms300_db(x: np.ndarray, f: float) -> float:
    n = f2s(f)
    return rms_db(x[n:n + WIN_300MS])


def crest_db(x: np.ndarray, f: float) -> float:
    n = f2s(f)
    seg = x[n:n + WIN_300MS]
    return peak_db(seg) - rms_db(seg)


def phone(x: np.ndarray) -> np.ndarray:
    """Tín hiệu qua giả lập loa điện thoại: band-pass Butterworth bậc 4, PHONE_BAND."""
    return sosfilt(butter(4, PHONE_BAND, "bandpass", fs=SR, output="sos"), np.asarray(x, dtype=np.float64))


def body_db(x: np.ndarray, f_from: float, f_to: float) -> float:
    """Trung vị RMS 300 ms, bước 100 ms, trên [f_from, f_to)."""
    a, b = f2s(f_from), f2s(f_to)
    vals = [rms_db(x[n:n + WIN_300MS]) for n in range(a, b - WIN_300MS + 1, HOP_100MS)]
    return float(np.median(vals)) if vals else float("-inf")


# ---------- mức section (#11), dải trầm (#12) ----------
def section_lufs(short: list, f_from: float, f_to: float) -> float:
    """Trung bình năng lượng short-term (cửa sổ 3 s) nằm trọn trong section; thiếu thì lấy t trong section."""
    a, b = f_from / 30, f_to / 30
    vals = [s for t, s in short if t - 3.0 >= a - 1e-6 and t <= b + 1e-6 and s > -70]
    if not vals:
        vals = [s for t, s in short if a <= t <= b and s > -70]
    if not vals:
        return float("-inf")
    return 10.0 * math.log10(float(np.mean(np.power(10.0, np.asarray(vals) / 10.0))))


def band_db(x: np.ndarray, lo_hz: float, hi_hz: float) -> float:
    freqs, psd = welch(x, fs=SR, nperseg=16384)
    sel = (freqs >= lo_hz) & (freqs < hi_hz)
    e = float(np.sum(psd[sel]))
    return 10.0 * math.log10(e) if e > 0 else float("-inf")
