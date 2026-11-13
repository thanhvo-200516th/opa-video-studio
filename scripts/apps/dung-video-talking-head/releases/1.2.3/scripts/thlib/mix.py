"""thlib.mix — stem SFX, lớp nhạc nền S29, trộn S25 và loudnorm 2 lượt
tuyến tính S18, tất cả trên trục vo-clean 48 kHz; vòng mã hoá–đo–hạ trần R35 dùng
chung cho ba bản xuất (loudnorm_encoded).

Mức tuyệt đối (bed so với giọng, loudnorm) đo theo BS.1770 nhiều kênh —
Ruling R10: mỗi lớp đo đúng như khi phát ra hai kênh (mono = dual-mono), vì
`integrated_lufs` của bản hạ mono đọc thấp hơn ffmpeg 3–6 dB.
"""

from __future__ import annotations

import json
import math
from collections.abc import Callable
from pathlib import Path

import numpy as np
from scipy.signal import lfilter

from . import audio as A
from . import paths
from .loud import (LIMIT_MARGIN_DB, LOUDNORM_LRA, TP_OVERSAMPLE, TP_STEP_DB, TP_TRIES, ffmpeg,
                   loudnorm_json, num, peak_stage)
from .rules import Rules

# Bước nhỏ nhất ffmpeg in cho LRA (LU) — xem _loudnorm.
_MIN_MEASURED_LRA = 0.01


def _n(t_s: float) -> int:
    """Giây -> số mẫu trên trục 48 kHz."""
    return int(round(t_s * A.SR))


def _stereo(x: np.ndarray) -> np.ndarray:
    """Lớp như khi phát ra hai kênh: mono [n] -> dual-mono [n, 2]."""
    x = np.asarray(x, dtype=float)
    return x if x.ndim == 2 else np.stack([x, x], axis=1)


def _played_lufs(x: np.ndarray) -> float:
    """Integrated LUFS của lớp khi phát hai kênh (R10)."""
    return A.integrated_lufs(_stereo(x))


def render_stem(cues_audio: list[dict], n_samples: int) -> np.ndarray:
    """Stem SFX mono float64 dài `n_samples`: mỗi cue {start_s, samples} đặt
    đúng mẫu round(start_s × 48k) (như prototype `place`), cue chồng thì cộng,
    phần trước 0 hoặc sau cuối trục bị cắt."""
    stem = np.zeros(n_samples)
    for cue in cues_audio:
        x = np.asarray(cue["samples"], dtype=float)
        n0 = _n(cue["start_s"])
        if n0 < 0:
            x, n0 = x[-n0:], 0
        x = x[: max(0, n_samples - n0)]
        stem[n0: n0 + len(x)] += x
    return stem


def _loop(track: np.ndarray, n: int, xfade: int) -> np.ndarray:
    """Nối lặp `track` cho đủ `n` mẫu; mỗi mối nối crossfade đẳng công suất
    (sin/cos) `xfade` mẫu để mức không hụt ở chỗ nối."""
    if len(track) >= n:
        return track[:n]
    if len(track) <= xfade:
        raise ValueError(f"Bài nền {len(track)} mẫu ngắn hơn crossfade {xfade} mẫu")
    ramp = np.linspace(0.0, np.pi / 2, xfade).reshape((-1,) + (1,) * (track.ndim - 1))
    out = track
    while len(out) < n:
        seam = out[-xfade:] * np.cos(ramp) + track[:xfade] * np.sin(ramp)
        out = np.concatenate([out[:-xfade], seam, track[xfade:]])
    return out[:n]


def _peaking(f0: float, q: float, gain_db: float) -> tuple[np.ndarray, np.ndarray]:
    """Biquad peaking EQ (RBJ cookbook, cùng dạng `equalizer t=q` của ffmpeg)."""
    amp = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / A.SR
    alpha = np.sin(w0) / (2 * q)
    b = np.array([1 + alpha * amp, -2 * np.cos(w0), 1 - alpha * amp])
    a = np.array([1 + alpha / amp, -2 * np.cos(w0), 1 - alpha / amp])
    return b / a[0], a / a[0]


def _fades(n: int, R: Rules) -> np.ndarray:
    """Bao tuyến tính dài n: vào 0 -> 1 trong fade_in_s từ mẫu 0, ra 1 -> 0
    trong fade_out_s, mẫu cuối (t_end) bằng 0."""
    i = np.arange(n)
    fade_in = np.minimum(1.0, i / _n(R.get("bgm.fade_in_s")))
    fade_out = np.minimum(1.0, (n - 1 - i) / _n(R.get("bgm.fade_out_s")))
    return fade_in * fade_out


def _bed_chain(x: np.ndarray, R: Rules) -> np.ndarray:
    """Chuỗi lọc của bed (S29): HPF hpf_hz rồi EQ khoét eq_db quanh eq_hz (Q eq_q)."""
    x = A.hpf(x.T, R.get("bgm.hpf_hz")).T
    return lfilter(*_peaking(R.get("bgm.eq_hz"), R.get("bgm.eq_q"), R.get("bgm.eq_db")), x.T).T


def bed_windows(t0_s: float, t_end_s: float, R: Rules) -> slice:
    """Chỉ số các cửa sổ short-term (audio.short_term, bắt đầu ở k × ST_HOP_S) nằm trọn trong
    phần không fade của bed bắt đầu ở t0_s: [t0 + fade_in_s, t0 + t_end − fade_out_s]."""
    hop, win = A.ST_HOP_S, A.ST_WIN_S
    lo = math.ceil((t0_s + R.get("bgm.fade_in_s")) / hop - 1e-6)
    hi = math.floor((t0_s + t_end_s - R.get("bgm.fade_out_s") - win) / hop + 1e-6)
    return slice(lo, max(lo, hi + 1))


def bgm_lras(track: np.ndarray, t_end_s: float, R: Rules) -> list[tuple[float, float]]:
    """[(offset giây, LRA của bed)] cho mọi offset bắt đầu bài trên lưới bgm.offset_step_s
    mà bài còn đủ dài tới t_end (1.1.1 P12). LRA = audio.lra trên các cửa sổ short-term của
    bài đã qua chuỗi lọc bed, nằm trong phần không fade (bed_windows) — đúng các cửa sổ
    L12 đo trên bed. Bài ngắn hơn t_end: chỉ offset 0, đo trên bài đã lặp như bgm_bed."""
    track = np.asarray(track, dtype=float)
    n_end, step = _n(t_end_s), R.get("bgm.offset_step_s")
    if len(track) < n_end:
        track = _loop(track, n_end, _n(R.get("bgm.loop_xfade_s")))
    st = A.short_term(_bed_chain(track, R))
    count = int((len(track) - n_end) / (step * A.SR) + 1e-9) + 1
    return [(step * k, A.lra(st[bed_windows(step * k, t_end_s, R)])) for k in range(count)]


def speech_floor(bed: np.ndarray, vo_mono: np.ndarray, R: Rules) -> tuple[float, float] | None:
    """S29 1.1.1 — phép đo sàn của lint L12: (min giọng − bed LU, giây đầu cửa sổ đó) trên các cửa sổ short-term
    không fade của bed (bed_windows, tính tới mẫu khác 0 cuối) có lời (cổng Tech 3342 trên giọng), cả hai phát ra
    hai kênh. None khi bed toàn im hoặc không có cửa sổ lời."""
    st = _stereo(bed)
    nz = np.flatnonzero(np.any(st != 0, axis=1))
    if len(nz) == 0:
        return None
    n = int(nz[-1]) + 1
    win = bed_windows(0.0, n / A.SR, R)
    bst, vst = A.short_term(st[:n])[win], A.short_term(_stereo(vo_mono[:n]))[win]
    speech = A.lra_gate(vst)
    if not speech.any():
        return None
    diff = np.where(speech, vst - bst, np.inf)
    k = int(np.argmin(diff))
    return float(diff[k]), (win.start + k) * A.ST_HOP_S


def bgm_offset(track: np.ndarray, t_end_s: float, R: Rules,
               vo_mono: np.ndarray | None = None) -> tuple[float, float]:
    """S29 1.1.1 (P12): offset bắt đầu bài cho bed có LRA nhỏ nhất (bgm_lras); hoà (làm tròn
    1e-6 LU) thì lấy offset nhỏ nhất. Trả (offset giây, LRA LU). Chỉ phụ thuộc mẫu của bài,
    t_end, bộ luật và — khi truyền `vo_mono` (BUILD, R129) — giọng: xét offset theo LRA tăng dần
    (tới bgm.lra_max_lu), lấy offset đầu tiên mà bed đặt ở đó giữ lời − nền ≥ bgm.st_floor_lu trên
    mọi cửa sổ có lời (speech_floor, đúng phép đo L12); không offset nào đạt thì offset LRA nhỏ nhất
    (L12 sẽ báo)."""
    grid = sorted(bgm_lras(track, t_end_s, R), key=lambda ol: (round(ol[1], 6), ol[0]))
    if vo_mono is not None:
        for off, lra in grid:
            if lra > R.get("bgm.lra_max_lu"):
                break
            floor = speech_floor(bgm_bed(track, vo_mono, t_end_s, R, offset_s=off), vo_mono, R)
            if floor is None or floor[0] >= R.get("bgm.st_floor_lu"):
                return off, lra
    return grid[0]


def bgm_bed(track: np.ndarray, vo_mono: np.ndarray, t_end_s: float, R: Rules,
            offset_s: float = 0.0) -> np.ndarray:
    """Lớp nhạc nền S29 trên trục vo-clean: bài lấy từ mẫu round(offset_s × 48k) (1.1.1,
    bgm_offset; 0 = y hệt 1.1.0), lặp bài (crossfade loop_xfade_s) tới t_end, HPF hpf_hz,
    EQ khoét eq_db quanh eq_hz (Q eq_q), fade vào/ra, rồi đặt mức sao cho integrated(bed) =
    integrated(giọng tới t_end) + rel_lu (đo sau EQ + fade, R10). Trả mảng cùng số kênh với
    `track`, dài max(len(vo_mono), t_end); sau t_end toàn 0."""
    track = np.asarray(track, dtype=float)[_n(offset_s):]
    n_end = _n(t_end_s)
    x = _loop(track, n_end, _n(R.get("bgm.loop_xfade_s")))
    x = _bed_chain(x, R)
    x = x * _fades(n_end, R).reshape((-1,) + (1,) * (x.ndim - 1))
    gain_db = _played_lufs(vo_mono[:n_end]) + R.get("bgm.rel_lu") - _played_lufs(x)
    bed = np.zeros((max(len(vo_mono), n_end),) + track.shape[1:])
    bed[:n_end] = x * 10 ** (gain_db / 20)
    return bed


def _fit(x: np.ndarray, n: int) -> np.ndarray:
    """Lớp dạng hai kênh [n, 2]: cắt bớt hoặc đệm 0 cho đủ n mẫu."""
    x = _stereo(x)[:n]
    return np.pad(x, ((0, n - len(x)), (0, 0)))


def mixdown(vo_stereo: np.ndarray, stem: np.ndarray, bed: np.ndarray | None,
            t_end_s: float, R: Rules) -> np.ndarray:
    """mix = giọng + stem + bed (S25; bed None = mix-nobgm), cắt tại t_end,
    fade tuyến tính end.fade_s ở cuối (mẫu cuối = 0). Trả [n, 2] float64."""
    n = _n(t_end_s)
    out = sum(_fit(x, n) for x in (vo_stereo, stem, bed) if x is not None)
    fade = _n(R.get("end.fade_s"))
    return out * np.concatenate([np.ones(n - fade), np.linspace(1.0, 0.0, fade)])[:, None]


def _loudnorm(target_lufs: float, tp_dbtp: float, measured: dict | None = None) -> str:
    """Filter loudnorm: lượt đo nếu `measured` là None, ngược lại lượt áp
    tuyến tính với số đo của lượt 1; cả hai in JSON."""
    base = f"loudnorm=I={num(target_lufs)}:TP={num(tp_dbtp)}:LRA={LOUDNORM_LRA}"
    if measured is not None:
        # ffmpeg coi measured_LRA = 0 là "chưa đo" và khi đó không chạy tuyến
        # tính; tín hiệu tĩnh đo ra LRA 0,00 nên truyền bước nhỏ nhất 0,01.
        lra = max(float(measured["input_lra"]), _MIN_MEASURED_LRA)
        base += (
            f":measured_I={measured['input_i']}:measured_TP={measured['input_tp']}"
            f":measured_LRA={num(lra)}:measured_thresh={measured['input_thresh']}"
            f":offset={measured['target_offset']}:linear=true"
        )
    return base + ":print_format=json"


def _measure(path: Path, target_lufs: float, tp_dbtp: float, pre_filter: str | None = None) -> dict:
    """Số đo BS.1770 (I, TP, LRA, ngưỡng) của file qua loudnorm (lượt đo), có
    thể đặt `pre_filter` trước (khâu đỉnh)."""
    af = _loudnorm(target_lufs, tp_dbtp)
    if pre_filter:
        af = f"{pre_filter},{af}"
    return loudnorm_json(ffmpeg(["-i", str(path), "-vn", "-af", af, "-f", "null", "-"]))


def loudnorm_file(in_wav, out_wav, target_lufs: float, tp_dbtp: float,
                  margin_db: float = LIMIT_MARGIN_DB, oversample: int = 1) -> dict:
    """S18 (Ruling R19): khâu đỉnh rồi loudnorm 2 lượt tuyến tính `in_wav` ->
    WAV PCM 48 kHz `out_wav`. Đo I của file vào để đặt khâu đỉnh (gain về I
    đích + limiter ở trần TP đích − `margin_db`, mặc định 0,5 dB như chuỗi giọng
    R9; `oversample` > 1 = limiter true-peak, xem loud.peak_stage), rồi đo (lượt
    1) và áp (lượt 2) loudnorm. ffmpeg vẫn rơi về chế độ động (gain chạy theo
    thời gian) khi không đạt được đích bằng gain cố định -> xoá `out_wav` và
    ném RuntimeError. Trả số đo ffmpeg của file vào (input_*, trước khâu đỉnh)
    và của file đã ghi (lufs, tp_dbtp)."""
    in_wav, out_wav = Path(in_wav), Path(out_wav)
    raw = _measure(in_wav, target_lufs, tp_dbtp)
    pre = peak_stage(target_lufs, tp_dbtp, float(raw["input_i"]), margin_db, oversample)
    measured = _measure(in_wav, target_lufs, tp_dbtp, pre)
    af = f"{pre},{_loudnorm(target_lufs, tp_dbtp, measured)}"
    stats = loudnorm_json(ffmpeg([
        "-y", "-i", str(in_wav), "-vn", "-af", af,
        "-ar", str(A.SR), "-c:a", "pcm_s16le", str(out_wav),
    ]))
    if stats.get("normalization_type") != "linear":
        out_wav.unlink(missing_ok=True)   # không để lại file sai chuẩn S18
        raise RuntimeError(
            f"loudnorm lượt 2 chạy chế độ '{stats.get('normalization_type')}', không phải "
            f"tuyến tính (S18): I={measured['input_i']} TP={measured['input_tp']} "
            f"LRA={measured['input_lra']}"
        )
    out = _measure(out_wav, target_lufs, tp_dbtp)
    return {
        "input_lufs": float(raw["input_i"]),
        "input_tp_dbtp": float(raw["input_tp"]),
        "lufs": float(out["input_i"]),
        "tp_dbtp": float(out["input_tp"]),
    }


class TruePeakError(RuntimeError):
    """R35: bản đã mã hoá vẫn vượt TP sau TP_TRIES lần hạ trần; `record` = bản ghi lần cuối
    (dạng kết quả loudnorm_encoded; file của lần cuối để lại cho cổng chấm)."""

    def __init__(self, message: str, record: dict):
        super().__init__(message)
        self.record = record


def encoded_tp(path) -> float:
    """True peak (dBTP, kênh lớn nhất) của tiếng đã mã hoá trong `path`, đo như L11."""
    x = A.decode(path)
    return max(A.true_peak_db(x[:, ch]) for ch in range(x.shape[1]))


def loudnorm_encoded(src, wav, target_lufs: float, tp_dbtp: float, encode: Callable[[Path], Path]) -> dict:
    """Vòng R35 dùng chung của ba bản xuất: loudnorm_file `src` -> `wav` (limiter true-peak
    TP_OVERSAMPLE×, trần đầu = TP đích − LIMIT_MARGIN_DB), `encode(wav)` mã hoá AAC và trả file đã
    mã hoá, đo TP của file đó như L11; còn vượt `tp_dbtp` thì hạ trần đúng phần vượt + TP_STEP_DB
    rồi làm lại, tối đa TP_TRIES lần — lần cuối vẫn vượt ⇒ TruePeakError. Trả số đo loudnorm_file
    của `wav` + "attempts" (số lần đã làm), "ceiling_dbtp" (trần limiter lần cuối),
    "encoded_tp_dbtp" (TP bản mã hoá lần cuối)."""
    wav, margin = Path(wav), LIMIT_MARGIN_DB
    for attempt in range(1, TP_TRIES + 1):
        got = loudnorm_file(src, wav, target_lufs, tp_dbtp, margin, TP_OVERSAMPLE)
        tp = encoded_tp(encode(wav))
        record = {**got, "attempts": attempt, "ceiling_dbtp": round(tp_dbtp - margin, 3),
                  "encoded_tp_dbtp": tp}
        if tp <= tp_dbtp:
            return record
        margin += tp - tp_dbtp + TP_STEP_DB
    raise TruePeakError("%s: TP bản mã hoá %.2f dBTP > %g sau %d lần (trần limiter %.2f dBTP, R35)"
                        % (wav.name, tp, tp_dbtp, TP_TRIES, record["ceiling_dbtp"]), record)


def select_bgm(ver: str, video_n: int) -> str | None:
    """S29: bài nền tất định của video số `video_n` = selected[video_n mod N],
    xếp theo `order`, chỉ tính bài `content_id_risk: none`. Chưa chọn bài nào
    -> None (BUILD hiểu là không có nhạc nền, không phải lỗi)."""
    manifest_path = paths.release_dir(ver) / "bgm_manifest.json"
    tracks = json.loads(manifest_path.read_text(encoding="utf-8"))["tracks"]
    chosen = sorted((t["order"], key) for key, t in tracks.items()
                    if t.get("selected") and t.get("content_id_risk") == "none")
    return chosen[video_n % len(chosen)][1] if chosen else None
