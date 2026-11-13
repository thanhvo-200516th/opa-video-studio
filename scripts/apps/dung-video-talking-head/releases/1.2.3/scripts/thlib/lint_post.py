"""thlib.lint_post — L11 của lint SFX độc lập (§5.8): chấm bản xuất SAU mux +
social, đọc lại từ đĩa của dự án (S25/S18/S27).

Gọi qua `thlib.lint.run_post_mux(project, R)` (API của Task 10); tách file vì
L11 làm việc trên file đã xuất (mp4, wav, JSON) chứ không trên mảng như
L1–L10, L12–L14. Stem đọc bằng `audio.decode_mono` (giữ đúng mức file mono);
mức tuyệt đối đo BS.1770 hai kênh (R10).
"""

from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

import numpy as np

from . import audio as A
from .lint import TOL, _TP_TOL_DB, _nonzero_runs, _result, _short_term_max
from .rules import Rules

_CUE_SEARCH_F = 12     # tìm lại cue trên final trong ±12 f quanh chỗ của nó (như mux.py, Task 12)
_END_WIN_S, _END_SILENT_DBFS = 0.001, -50.0       # S27: 1 ms cuối của mix đã fade về im
_FINALS = ("final.mp4", "final-nobgm.mp4", "final-social.mp4")
_MIXES = ("mix.wav", "mix-nobgm.wav")             # mix đã chuẩn hoá BUILD ghi ở public/ trước mux


def _read_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _sample_rate(path: Path) -> int:
    """Tần số lấy mẫu của luồng audio đầu tiên (ffprobe)."""
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
                          "stream=sample_rate", "-of", "default=nw=1:nk=1", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return int(out.split()[0])


def _video_frames(path: Path) -> int:
    """Số packet (frame) của luồng hình đầu tiên (ffprobe -count_packets)."""
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                          "stream=nb_read_packets", "-of", "default=nw=1:nk=1", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return int(out.split()[0])


def _cue_offset_f(seg: np.ndarray, track: np.ndarray, a: int, fps: int) -> float:
    """Độ lệch (frame) của đoạn cue `seg` (ở mẫu a trên stem) khi tìm lại trên
    `track` trong ±_CUE_SEARCH_F frame; dương = final trễ."""
    w = int(_CUE_SEARCH_F * A.SR / fps)
    lo = max(0, a - w)
    window = track[lo: a + len(seg) + w]
    if len(window) < len(seg):
        return math.inf
    return (lo + A.match_at(window, seg) - a) * fps / A.SR   # R217: chuẩn hoá (thô bị giọng to kéo lệch)


def _sync(pub: Path, finals: dict, mixes: dict, plan: dict, R: Rules) -> list:
    """S25: xcorr(final, mix) ≤ xcorr_max_ms; mỗi cue của stem tìm lại trên
    final lệch trong −early/+late frame."""
    fps, bad = R.get("fps"), []
    for wav, mp4 in (("mix.wav", "final.mp4"), ("mix-nobgm.wav", "final-nobgm.mp4")):
        if mp4 in finals and wav in mixes:
            lag = A.xcorr_lag_ms(mixes[wav].mean(axis=1), finals[mp4].mean(axis=1))
            if abs(lag) > R.get("xcorr_max_ms"):
                bad.append(("xcorr %s↔%s %+.2f ms > ±%g ms"
                            % (wav, mp4, lag, R.get("xcorr_max_ms")), None))
    if "final.mp4" not in finals:
        return bad
    stem, track = A.decode_mono(pub / "sfx_stem.wav"), finals["final.mp4"].mean(axis=1)
    bodies = _nonzero_runs(stem, R)
    early, late = R.get("sfx.sync_tol_f.early"), R.get("sfx.sync_tol_f.late")
    for c in plan.get("cues") or []:
        n, f = int(round(c["peak_s"] * A.SR)), int(round(c["peak_s"] * fps))
        ab = next(((a, b) for a, b in bodies if a <= n < b), None)
        if ab is None:
            bad.append(("%s: không thấy cue trên sfx_stem.wav" % c["id"], f))
            continue
        off = _cue_offset_f(stem[ab[0]: ab[1]], track, ab[0], fps)
        if not -early <= off <= late:
            bad.append(("%s: trên final lệch %+.2f f (cho phép −%d/+%d)"
                        % (c["id"], off, early, late), f))
    return bad


def _loudness(pub: Path, out_dir: Path, finals: dict, R: Rules) -> list:
    """S18: I final/nobgm −16 và social −14 (±tol, BS.1770 hai kênh — R10),
    TP ≤ tp_dbtp, S-max ≤ I + smax_over_i_lu, social 48 kHz; trước chuẩn
    hoá: SFX làm tăng I ≤ sfx_di_max_lu, M-max(giọng + stem) ≤ M-max giọng +
    mmax_over_vo_lu."""
    L, bad = R.get("loudness"), []
    for name, target in (("final.mp4", L["final_lufs"]), ("final-nobgm.mp4", L["final_lufs"]),
                         ("final-social.mp4", L["social_lufs"])):
        if name not in finals:
            continue
        x = finals[name]
        i, smax = A.integrated_lufs(x), _short_term_max(x)
        tp = max(A.true_peak_db(x[:, ch]) for ch in range(x.shape[1]))
        if abs(i - target) > L["tol_lu"]:
            bad.append(("%s: %.2f LUFS, cần %g ±%g" % (name, i, target, L["tol_lu"]), None))
        if tp > L["tp_dbtp"] + _TP_TOL_DB:
            bad.append(("%s: TP %.2f dBTP > %g" % (name, tp, L["tp_dbtp"]), None))
        if smax > i + L["smax_over_i_lu"]:
            bad.append(("%s: S-max %.2f > I %.2f + %g LU" % (name, smax, i, L["smax_over_i_lu"]), None))
    if "final-social.mp4" in finals and _sample_rate(out_dir / "final-social.mp4") != A.SR:
        bad.append(("final-social.mp4 không phải %d Hz" % A.SR, None))
    vo, stem = A.decode_mono(pub / "vo-clean.wav"), A.decode_mono(pub / "sfx_stem.wav")
    n = min(len(vo), len(stem))
    both = vo[:n] + stem[:n]
    di = A.integrated_lufs(both) - A.integrated_lufs(vo[:n])
    dm = float(A.momentary(both).max() - A.momentary(vo[:n]).max())
    if di > L["sfx_di_max_lu"]:
        bad.append(("SFX làm tăng I %.2f LU > %g" % (di, L["sfx_di_max_lu"]), None))
    if dm > L["mmax_over_vo_lu"]:
        bad.append(("M-max giọng+SFX hơn giọng %.2f LU > %g" % (dm, L["mmax_over_vo_lu"]), None))
    return bad


def _ending(project: Path, finals: dict, mixes: dict, plan: dict, R: Rules) -> list:
    """S27: t_end = đầu khoảng ngắt sau từ cuối + end.pad_s (≤ độ dài nguồn);
    bản xuất có đúng duration_f frame hình (P8, spec 1.1.1 §9.5) và tiếng dài duration_f
    (±1 f); sau từ cuối chỉ có cue CTA post-hit; mix / mix-nobgm đã fade về im ở cuối."""
    fps = R.get("fps")
    pauses, lock = _read_json(project / "pauses.json"), _read_json(project / "picture_lock.json")
    lwe = pauses["last_word_end"]
    p0 = next((p[0] for p in pauses["pauses"] if p[0] >= lwe - TOL), lwe)
    want = min(p0 + R.get("end.pad_s"), pauses["duration_s"])
    bad = []
    if abs(lock["t_end"] - want) > 1 / fps:
        bad.append(("t_end %.3f s, cần %.3f s (khoảng ngắt sau từ cuối + %g s)"
                    % (lock["t_end"], want, R.get("end.pad_s")), None))
    for name, x in finals.items():
        frames = _video_frames(project / "out" / name)
        if frames != lock["duration_f"]:
            bad.append(("%s có %d frame hình ≠ duration_f %d" % (name, frames, lock["duration_f"]), None))
        if abs(len(x) / A.SR - lock["duration_f"] / fps) > 1 / fps:
            bad.append(("%s dài %.3f s ≠ %d f" % (name, len(x) / A.SR, lock["duration_f"]), None))
    for c in plan.get("cues") or []:
        if c["peak_s"] > lwe + TOL and not (c.get("role") == "cta" and c.get("mode") == "post"):
            bad.append(("%s: cue mới sau từ cuối" % c["id"], int(round(c["peak_s"] * fps))))
    for wav, x in mixes.items():
        tail = x[-int(_END_WIN_S * A.SR):]
        if len(tail) and float(A.db(np.abs(tail).max())) > _END_SILENT_DBFS:
            bad.append(("%s không fade về im ở cuối" % wav, None))
    return bad


def run_post_mux(project, R: Rules) -> list[dict]:
    """L11 trên bản xuất của `project`: đủ 3 bản xuất, xcorr + cue −1/+2 f,
    loudness, phần kết. Thiếu bản xuất hay mix nào là một vi phạm L11 (mux
    chưa chạy / hỏng), không phải lỗi chương trình. Trả [kết quả L11]."""
    project = Path(project)
    out_dir, pub = project / "out", project / "public"
    finals = {f: A.decode(out_dir / f) for f in _FINALS if (out_dir / f).is_file()}
    mixes = {w: A.decode(pub / w) for w in _MIXES if (pub / w).is_file()}
    plan = _read_json(out_dir / "sfx_plan.json")
    bad = [("thiếu bản xuất out/%s" % f, None) for f in _FINALS if f not in finals]
    bad += [("thiếu bản xuất public/%s" % w, None) for w in _MIXES if w not in mixes]
    bad += _sync(pub, finals, mixes, plan, R) + _loudness(pub, out_dir, finals, R)
    bad += _ending(project, finals, mixes, plan, R)
    return [_result("L11", bad, "đủ %d bản xuất; xcorr, cue −1/+2 f, loudness và phần kết đạt"
                    % len(_FINALS))]
