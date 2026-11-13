"""thlib.sfxlib — chuẩn bị & đo file SFX, đọc sfx_manifest.json, kiểm ràng buộc
family (`sfx.family_constraints` trong rules.json).

Port từ `prototype/measure_files.py` (D:/MMO/Van Minh AI/docs/specs/2026-09-11-
rulebook-evidence/prototype/), tách làm 2 bước: `prepare()` (decode + chuẩn hoá
mức) và `measure()` (đo hình bao/dải tần/độ to) để `import_sfx.py` có thể ghi
WAV đã chuẩn hoá trước khi đo.
"""

from __future__ import annotations

import json

import numpy as np
from scipy.io import wavfile
from scipy.signal import find_peaks

from . import audio, paths

_ENV5_WIN = 240  # ~5 ms tại 48 kHz — khớp prototype/measure_files.py::shape


def prepare(path) -> np.ndarray:
    """Chuẩn hoá 1 file SFX: giải mã mono (L+R)/2 -> HPF 120 Hz bậc 2 -> đỉnh -1 dBFS."""
    x = audio.decode_mono(path)
    y = audio.hpf(x, 120.0, 2)
    peak = np.abs(y).max()
    if peak > 0:
        y = y / peak * 10 ** (-1 / 20)
    return y


def _shape(y: np.ndarray) -> dict:
    """Đo hình bao (attack/pre/tail/số đợt onset) quanh đỉnh biên độ."""
    e20 = audio.rms_env(y, 0.02)
    m = e20.max()
    env5 = np.convolve(np.abs(y), np.ones(_ENV5_WIN) / _ENV5_WIN, mode="same")
    ip = int(np.argmax(env5))
    i20 = np.where(e20 >= m * 10 ** (-20 / 20))[0]
    i30 = np.where(e20 >= m * 10 ** (-30 / 20))[0]
    i40 = np.where(e20 >= m * 10 ** (-40 / 20))[0]
    edb = audio.db(e20 / m)
    pk, _ = find_peaks(edb, height=-10, prominence=6, distance=int(0.06 * audio.SR))
    return {
        "lag_ms": round(ip / audio.SR * 1000),
        "attack20_ms": round((ip - i20[0]) / audio.SR * 1000),
        "pre30_ms": round((ip - i30[0]) / audio.SR * 1000),
        "tail30_ms": round((i30[-1] + 1 - ip) / audio.SR * 1000),
        "tail40_ms": round((i40[-1] + 1 - ip) / audio.SR * 1000),
        "onsets": int(len(pk)),
    }


def measure(y: np.ndarray) -> dict:
    """Đo đầy đủ 1 tín hiệu SFX đã prepare(): hình bao + dải tần + Mmax K/phone-K/crest.

    Các trường trả về khớp `sfx_manifest.json` (trừ path/md5/origin/license*):
    lag_ms, attack20_ms, pre30_ms, tail30_ms, tail40_ms, onsets, lt250, b250_1k,
    b1_4k, gt4k, MmaxK, MmaxPK, crestPK.
    """
    s = _shape(y)
    f, P = audio.spectrum(y)
    pad = np.concatenate([np.zeros(audio.SR // 2), y, np.zeros(audio.SR // 2)])
    s.update({
        "lt250": round(100 * audio.band_frac(f, P, 0, 250), 1),
        "b250_1k": round(100 * audio.band_frac(f, P, 250, 1000), 1),
        "b1_4k": round(100 * audio.band_frac(f, P, 1000, 4000), 1),
        "gt4k": round(100 * audio.band_frac(f, P, 4000, 24000), 1),
        "MmaxK": round(float(audio.momentary(pad).max()), 2),
        "MmaxPK": round(float(audio.phone_k(pad).max()), 2),
    })
    s["crestPK"] = round(-1.0 - s["MmaxPK"], 2)
    return s


def load_manifest(ver: str) -> dict:
    """Nạp sfx_manifest.json của bản `ver`."""
    p = paths.release_dir(ver) / "sfx_manifest.json"
    return json.loads(p.read_text(encoding="utf-8"))


def load_signal(ver: str, key: str) -> np.ndarray:
    """Đọc WAV của 1 mục manifest (`ver`/`key`), trả về mono float64 trong [-1, 1]."""
    manifest = load_manifest(ver)
    rel_path = manifest["files"][key]["path"]
    _sr, pcm = wavfile.read(str(paths.release_dir(ver) / rel_path))
    return pcm.astype(np.float64) / 32767.0


def role_ok(meta: dict, family: str, R) -> tuple[bool, list[str]]:
    """Kiểm `meta` (kết quả measure(), hoặc 1 mục manifest) theo
    `sfx.family_constraints.<family>` của bộ luật `R`. Trả về (đạt?, [lý do fail])."""
    constraints = R.get(f"sfx.family_constraints.{family}")
    reasons = []
    for cname, limit in constraints.items():
        if cname.endswith("_max"):
            field = cname[: -len("_max")]
            if meta[field] > limit:
                reasons.append(f"{field}={meta[field]} > {cname}={limit}")
        elif cname.endswith("_min"):
            field = cname[: -len("_min")]
            if meta[field] < limit:
                reasons.append(f"{field}={meta[field]} < {cname}={limit}")
    return (len(reasons) == 0, reasons)
