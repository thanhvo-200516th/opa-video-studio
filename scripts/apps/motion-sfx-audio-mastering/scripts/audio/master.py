"""Master V2 bằng ffmpeg, cách 1 của NC §3.5 (không loudnorm) — gói E, KH §3.9.

Chuỗi: volume=G → 192 kHz → alimiter trần 0,79 → 48 kHz → đúng số mẫu của file vào → pcm_s24le mono.
Vòng lặp G chỉ nhắm I; TP không phải điều kiện dừng (người gọi kiểm TP).
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from scipy.io import wavfile

SR = 48000
LIMIT = 0.79                       # ≈ −2,0 dBFS
STOP_TOL_LU = 0.1                  # dừng khi |I − đích| ≤ 0,1 (dư so với ± 0,3)
_NUM = r"(-?(?:\d+(?:\.\d+)?|inf))"


def _ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if not exe:
        raise RuntimeError("không thấy ffmpeg trên PATH (cần bản winget)")
    return exe


def _wav_len(path: Path) -> int:
    _, d = wavfile.read(str(path), mmap=True)
    return int(d.shape[0])


def chain_filter(gain_db: float, n_samples: int, limit: float = LIMIT) -> str:
    return (f"volume={gain_db:.4f}dB,aresample=192000,"
            f"alimiter=limit={limit}:attack=1:release=60:level=disabled:latency=1,"
            f"aresample={SR},apad,atrim=end_sample={n_samples}")


def apply_chain(in_wav: Path, out_wav: Path, gain_db: float, limit: float = LIMIT) -> None:
    """Cùng chuỗi lọc master (dùng cho bản chỉ SFX và bản A/B). Ghi pcm_s24le mono 48 kHz, cùng số mẫu."""
    in_wav, out_wav = Path(in_wav), Path(out_wav)
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    cmd = [_ffmpeg(), "-hide_banner", "-nostats", "-loglevel", "error", "-y", "-i", str(in_wav),
           "-af", chain_filter(gain_db, _wav_len(in_wav), limit),
           "-c:a", "pcm_s24le", "-ac", "1", "-ar", str(SR),
           "-fflags", "+bitexact", "-flags:a", "+bitexact", str(out_wav)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg master lỗi ({r.returncode}): {r.stderr.strip()[-800:]}")


def parse_ebur128(text: str) -> dict:
    """Lấy I, LRA, TP từ khối Summary của ffmpeg ebur128=peak=true."""
    tail = text[text.rfind("Summary:"):] if "Summary:" in text else ""
    out = {}
    for key, pat in (("I", rf"\bI:\s*{_NUM}\s*LUFS"), ("LRA", rf"\bLRA:\s*{_NUM}\s*LU\b"),
                     ("TP", rf"\bPeak:\s*{_NUM}\s*dBFS")):
        m = re.search(pat, tail)
        if not m:
            raise ValueError(f"ebur128: không đọc được {key} trong Summary")
        out[key] = float(m.group(1))
    return out


def ebur128(path: Path) -> dict:
    """ffmpeg ebur128=peak=true → {I, LRA, TP}."""
    cmd = [_ffmpeg(), "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg ebur128 lỗi ({r.returncode}): {r.stderr.strip()[-800:]}")
    return parse_ebur128(r.stderr)


def master(mix_wav: Path, out_wav: Path, target_i: float, limit: float = LIMIT,
           max_passes: int = 4) -> dict:
    """Lặp G tới khi I ≈ target_i (dừng ở |ΔI| ≤ 0,1 hoặc hết max_passes). Trả {I, TP, LRA, gain_db, passes}.
    target_i không có mặc định: I đích theo video lấy từ build.target_i_for."""
    src = ebur128(Path(mix_wav))
    if src["I"] < -70.0:
        raise ValueError(f"{mix_wav}: gần như câm (I = {src['I']})")
    gain = target_i - src["I"]
    res: dict = {}
    for k in range(1, max_passes + 1):
        apply_chain(Path(mix_wav), Path(out_wav), gain, limit)
        res = {**ebur128(Path(out_wav)), "gain_db": round(gain, 4), "passes": k}
        err = target_i - res["I"]
        if abs(err) <= STOP_TOL_LU:
            break
        if k < max_passes:
            gain += err
    return res
