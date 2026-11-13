#!/usr/bin/env python3
"""Cắt âm theo GIÂY từ master đã duyệt rồi ghép vào MP4 câm (NN §8.5 bước 3–5).

Chạy:  python tools/v2w/mux_test.py --video <muted.mp4> --from 7.5 --to 14.0 --out <test.mp4>
                                     [--wav <đoạn.wav>] [--master public/audio/v2-khong-bo-sot-khach-master.wav]
  1) Cắt: atrim theo mẫu [from, to), asetpts, fade 10 ms hai đầu chống click (chỉ cho clip test), pcm_s16le 48 kHz.
  2) Mux: -map 0:v:0 -map 1:a:0, hình copy, âm AAC 320k stereo, +faststart.
  3) ffprobe: |thời lượng âm − hình| < 1/60 s.
Mọi lệnh gọi bằng danh sách tham số (không shell, không vướng "|").
Exit:  0 đạt, 1 ffmpeg lỗi hoặc lệch thời lượng, 2 lỗi đầu vào.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "public/audio/v2-khong-bo-sot-khach-master.wav"
FADE_S = 0.01
SR = 48000
TOL_S = 1 / 60


class InputError(Exception):
    """Lỗi đầu vào → exit 2."""


class MuxError(Exception):
    """ffmpeg lỗi hoặc lệch thời lượng → exit 1."""


def exe(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise InputError(f"không thấy {name} trên PATH")
    return path


def _run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise MuxError(f"{Path(cmd[0]).name} lỗi ({r.returncode}): {r.stderr.strip()[-600:]}")


def duration(path: Path, stream: str) -> float:
    """Thời lượng (giây) của luồng 'v' hoặc 'a' đầu tiên."""
    r = subprocess.run([exe("ffprobe"), "-v", "error", "-select_streams", f"{stream}:0", "-show_entries",
                        "stream=duration", "-of", "json", str(path)], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise InputError(f"ffprobe lỗi với {path}: {r.stderr.strip()[-300:]}")
    streams = json.loads(r.stdout).get("streams", [])
    if not streams or "duration" not in streams[0]:
        raise InputError(f"{path} không có luồng {stream}")
    return float(streams[0]["duration"])


def cut_audio(master: Path, start: float, end: float, wav: Path) -> Path:
    """Đoạn [start, end) giây của master → WAV 48 kHz 16 bit, fade 10 ms hai đầu."""
    if not master.is_file():
        raise InputError(f"thiếu master {master}")
    if not 0 <= start < end:
        raise InputError(f"khoảng cắt sai: {start} → {end}")
    total = duration(master, "a")
    if end > total + 1e-6:
        raise InputError(f"đoạn cắt vượt master ({end} > {total:.3f} s)")
    span = end - start
    af = (f"atrim=start={start}:end={end},asetpts=PTS-STARTPTS,"
          f"afade=t=in:st=0:d={FADE_S},afade=t=out:st={span - FADE_S:.6f}:d={FADE_S}")
    wav.parent.mkdir(parents=True, exist_ok=True)
    _run([exe("ffmpeg"), "-hide_banner", "-nostats", "-loglevel", "error", "-y", "-i", str(master), "-af", af,
          "-c:a", "pcm_s16le", "-ar", str(SR), str(wav)])
    return wav


def mux(video: Path, wav: Path, out: Path) -> dict:
    """Ghép âm vào hình (hình copy). Trả {video, audio, delta} (giây); lệch ≥ 1/60 s → MuxError.
    -aac_pns 0: tắt thay nhiễu cảm quan của bộ mã AAC, để master mono ra hai kênh trùng nhau (rà chéo Q5-V3: |L−R| 0,249 → 0,0005)."""
    if not video.is_file():
        raise InputError(f"thiếu video {video}")
    out.parent.mkdir(parents=True, exist_ok=True)
    _run([exe("ffmpeg"), "-hide_banner", "-nostats", "-loglevel", "error", "-y", "-i", str(video), "-i", str(wav),
          "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-aac_pns", "0", "-ac", "2",
          "-movflags", "+faststart", str(out)])
    v, a = duration(out, "v"), duration(out, "a")
    res = {"video": v, "audio": a, "delta": abs(a - v)}
    if res["delta"] >= TOL_S:
        raise MuxError(f"lệch thời lượng âm/hình {res['delta'] * 1000:.1f} ms ≥ {TOL_S * 1000:.1f} ms ({a:.4f} / {v:.4f} s)")
    return res


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Cắt âm master theo giây rồi mux vào MP4 câm")
    ap.add_argument("--video", type=Path, required=True)
    ap.add_argument("--from", dest="start", type=float, required=True, help="giây toàn phim bắt đầu")
    ap.add_argument("--to", dest="end", type=float, required=True, help="giây toàn phim kết thúc")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--wav", type=Path, help="nơi ghi đoạn WAV (mặc định cạnh --out)")
    ap.add_argument("--master", type=Path, default=MASTER)
    a = ap.parse_args()
    wav = a.wav or a.out.with_suffix(".wav")
    try:
        cut_audio(a.master, a.start, a.end, wav)
        res = mux(a.video, wav, a.out)
    except InputError as e:
        print(f"LỖI đầu vào: {e}", file=sys.stderr)
        return 2
    except MuxError as e:
        print(f"LỖI: {e}", file=sys.stderr)
        return 1
    print(f"OK {a.out} · hình {res['video']:.4f} s · âm {res['audio']:.4f} s · lệch {res['delta'] * 1000:.2f} ms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
