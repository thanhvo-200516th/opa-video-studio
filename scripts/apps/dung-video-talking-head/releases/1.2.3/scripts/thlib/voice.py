"""thlib.voice — chuỗi giọng vo-clear-1 (S28), khoảng ngắt / onset thật
(S04, §5.1) và VO_REF (S14) trên trục vo-clean.

Phần khoảng ngắt / onset / VO_REF port từ `prototype/planner_v11.py` (dòng
76–98) thành hàm thuần; mọi ngưỡng đọc từ rules.json (`audio.*`, `voice.*`).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from . import audio as A
from .loud import LOUDNORM_LRA, ffmpeg, loudnorm_json, num, peak_stage
from .rules import Rules

# Cửa sổ RMS 100 ms chọn khung "có lời" cho VO_REF (§5.1: RMS100).
_VOICED_WIN_S = 0.1
# Khoảng ngắt cuối coi như chạm hết file nếu kết thúc cách cuối ≤ 50 ms.
_END_TOL_S = 0.05
# Dải tần QA của S28 (Hz), dạng [lo, hi).
_BAND_LOW = (80.0, 250.0)
_BAND_LOWMID = (250.0, 1000.0)
_BAND_PRESENCE = (1000.0, 3500.0)
_HF_FROM_HZ = 4000.0


def clear_chain(R: Rules) -> str:
    """Chuỗi filter ffmpeg vo-clear-1 (S28) đứng trước loudnorm, dựng từ `voice.*`."""
    v = R.get("voice")
    comp = v["comp"]
    parts = [f"highpass=f={num(v['hp_hz'])}", f"lowpass=f={num(v['lp_hz'])}"]
    parts += [f"equalizer=f={num(f)}:t=q:w={num(q)}:g={num(g)}" for f, q, g in v["eq"]]
    parts.append(
        f"acompressor=threshold={num(comp['thr_db'])}dB:ratio={num(comp['ratio'])}"
        f":attack={num(comp['attack_ms'])}:release={num(comp['release_ms'])}"
        f":makeup={num(comp['makeup_db'])}"
    )
    return ",".join(parts)


def _loudnorm(R: Rules, measured: dict | None = None) -> str:
    """Filter loudnorm: lượt đo nếu `measured` là None, ngược lại lượt áp
    tuyến tính với số đo của lượt 1. Cả hai lượt in JSON (print_format=json)
    để đọc số đo và normalization_type."""
    v = R.get("voice")
    base = f"loudnorm=I={num(v['target_lufs'])}:TP={num(v['tp_dbtp'])}:LRA={LOUDNORM_LRA}"
    if measured is not None:
        base += (
            f":measured_I={measured['input_i']}:measured_TP={measured['input_tp']}"
            f":measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}"
            f":offset={measured['target_offset']}:linear=true"
        )
    return base + ":print_format=json"


def _peak_stage(R: Rules, measured_i: float) -> str:
    """Khâu đỉnh trước loudnorm của giọng (Ruling R9): `loud.peak_stage` với I
    và TP đích của S28."""
    v = R.get("voice")
    return peak_stage(v["target_lufs"], v["tp_dbtp"], measured_i)


def _require_linear(stats: dict) -> None:
    """S28 bắt buộc loudnorm tuyến tính. ffmpeg tự rơi về chế độ động (có
    limiter, gain chạy theo thời gian) khi measured_TP + (I đích − measured_I)
    > TP đích hoặc measured_LRA > LRA đích — khi đó ném lỗi, không trả QA."""
    kind = stats.get("normalization_type")
    if kind != "linear":
        raise RuntimeError(
            f"loudnorm lượt 2 chạy chế độ '{kind}', không phải tuyến tính (S28): "
            f"I={stats.get('input_i')} TP={stats.get('input_tp')} LRA={stats.get('input_lra')}"
        )


def _measure(path: Path, R: Rules, pre_filter: str | None = None) -> dict:
    """Đo loudness BS.1770 (I, TP, LRA, ngưỡng) của `path` qua loudnorm,
    có thể đặt `pre_filter` trước (các lượt đo của vo-clear)."""
    af = f"{pre_filter},{_loudnorm(R)}" if pre_filter else _loudnorm(R)
    return loudnorm_json(ffmpeg(["-i", str(path), "-vn", "-af", af, "-f", "null", "-"]))


def _band_db(f: np.ndarray, P: np.ndarray, band: tuple[float, float]) -> float:
    """Công suất dải (dB, tương đối) — hiệu hai dải = chênh công suất."""
    return float(10 * np.log10(max(A.band_frac(f, P, *band), 1e-20)))


def vo_clear(src: Path, out_wav: Path, R: Rules) -> dict:
    """vo-clear-1 (S28): chuỗi lọc + khâu đỉnh + loudnorm 2 lượt tuyến tính
    -> WAV PCM 48 kHz stereo tại `out_wav`. Đo I của chuỗi để đặt khâu đỉnh,
    rồi đo (lượt 1) và áp (lượt 2) loudnorm; lượt 2 lỗi hoặc không tuyến tính
    thì xoá `out_wav` và ném RuntimeError. Trả về QA của file đã ghi:
    lufs/tp_dbtp (BS.1770 stereo, ffmpeg đo lại file ra), tilt_db, low_db,
    voice_hf_ratio, xcorr_ms (độ trễ vo-clean so với nguồn)."""
    chain = clear_chain(R)
    pre = f"{chain},{_peak_stage(R, float(_measure(src, R, chain)['input_i']))}"
    measured = _measure(src, R, pre)
    try:
        _require_linear(loudnorm_json(ffmpeg([
            "-y", "-i", str(src), "-vn", "-af", f"{pre},{_loudnorm(R, measured)}",
            "-ar", str(A.SR), "-ac", "2", "-c:a", "pcm_s16le", str(out_wav),
        ])))
    except RuntimeError:
        out_wav.unlink(missing_ok=True)   # không để lại file sai chuẩn S28
        raise
    out_stats = _measure(out_wav, R)
    clean = A.decode_mono(out_wav)
    f, P = A.spectrum(clean)
    lowmid = _band_db(f, P, _BAND_LOWMID)
    return {
        "lufs": float(out_stats["input_i"]),
        "tp_dbtp": float(out_stats["input_tp"]),
        "tilt_db": _band_db(f, P, _BAND_PRESENCE) - lowmid,
        "low_db": _band_db(f, P, _BAND_LOW) - lowmid,
        "voice_hf_ratio": A.band_frac(f, P, _HF_FROM_HZ, np.inf),
        "xcorr_ms": A.xcorr_lag_ms(A.decode_mono(src), clean),
    }


def find_pauses(vo_mono: np.ndarray, R: Rules) -> list[tuple[float, float]]:
    """Khoảng ngắt [t0, t1] (giây) theo §5.1: RMS20 < pause_rms_db liên tục
    ≥ pause_min_s, trong đó tổng ≥ pause_deep_min_s dưới pause_deep_db."""
    e20 = A.db(A.rms_env(vo_mono, R.get("audio.rms_win_s")))
    deep = e20 < R.get("audio.pause_deep_db")
    min_s = R.get("audio.pause_min_s")
    deep_min_s = R.get("audio.pause_deep_min_s")
    pauses = []
    for a, b in A.runs(e20 < R.get("audio.pause_rms_db")):
        if (b - a) / A.SR >= min_s and deep[a:b].sum() / A.SR >= deep_min_s:
            pauses.append((a / A.SR, b / A.SR))
    return pauses


def correct_onsets(words: list[dict], pauses, R: Rules) -> list[float]:
    """Onset thật S04: mỗi t1 gán cho TỪ SỚM NHẤT có s − onset_pre_s ≤ t1 ≤
    e + onset_post_s, và mỗi từ chỉ nhận một t1 (một-một) — xử lý các pause
    theo thứ tự thời gian, từ đã bị t1 trước nhận thì bỏ qua chứ không ghi
    đè; pause không còn từ nào khớp thì giữ nguyên, không gán onset. Các từ
    khác giữ s whisper; cuối cùng kẹp đơn điệu ≥ onset trước + onset_mono_gap_s."""
    pre = R.get("audio.onset_pre_s")
    post = R.get("audio.onset_post_s")
    gap = R.get("audio.onset_mono_gap_s")
    on = [float(w["s"]) for w in words]
    taken: set[int] = set()
    for _, t1 in sorted(pauses, key=lambda p: p[1]):
        for k, w in enumerate(words):
            if k not in taken and w["s"] - pre <= t1 <= w["e"] + post:
                on[k] = float(t1)
                taken.add(k)
                break
    for k in range(1, len(on)):
        on[k] = max(on[k], on[k - 1] + gap)
    return on


def vo_ref(vo_mono: np.ndarray, R: Rules) -> dict:
    """VO_REF (§5.1, S14): median momentary trên các khung RMS100 >
    voiced_rms100_db, ở ba miền phone-K (quyết định), K và phone-A (báo cáo)."""
    voiced = A.db(A.rms_env(vo_mono, _VOICED_WIN_S)) > R.get("audio.voiced_rms100_db")
    phoned = A.phone(vo_mono, R.get("audio.phone_hpf_hz"), R.get("audio.phone_hpf_order"))
    return {
        "phone_k": float(np.median(A.momentary(phoned)[voiced])),
        "k": float(np.median(A.momentary(vo_mono)[voiced])),
        "phone_a": float(np.median(A.a_momentary(phoned)[voiced])),
    }


def last_word_end(words: list[dict], pauses, dur: float) -> float:
    """Mốc hết lời: đầu khoảng ngắt cuối nếu nó chạy tới hết file (±50 ms),
    ngược lại lấy e whisper của từ cuối."""
    if pauses and pauses[-1][1] >= dur - _END_TOL_S:
        return float(pauses[-1][0])
    return float(words[-1]["e"])
