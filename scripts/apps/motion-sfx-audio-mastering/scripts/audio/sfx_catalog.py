#!/usr/bin/env python3
"""Lập danh mục đo được cho một thư viện SFX (wav/mp3/ogg): mỗi file một dòng số đo để chọn âm theo chuyển động.

Chạy:  python -X utf8 tools/audio/sfx_catalog.py <thư mục thư viện> <file CSV ra> [--jobs 12]
Số đo (giải mã bằng ffmpeg về 48 kHz, giữ số kênh gốc tối đa 2):
  dur_s · peak_dbfs (đỉnh mẫu) · tp_dbtp (đỉnh thật, lấy mẫu dư 4 lần) · lufs_i (tích hợp BS.1770, cổng −70/−10)
  · lufs_mmax (momentary max, cửa sổ 400 ms) · lead_ms (lặng trước khi tiếng lên tới −50 dB dưới đỉnh: phải trừ khi đặt
  đúng khung) · attack_ms (từ lúc lên tới đỉnh) · tail_ms (từ đỉnh tới khi tắt còn −40 dB) · centroid_hz (độ sáng)
  · low/mid/high (tỉ lệ năng lượng < 150 Hz / 300–2000 Hz / > 4 kHz: điện thoại cắt phần < ~200 Hz).
Exit: 0 xong, 2 lỗi đầu vào.
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from scipy.signal import resample_poly

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dsp_loud import lufs_integrated, momentary_max  # noqa: E402

SR = 48000
EXTS = {".wav", ".mp3", ".ogg"}
FIELDS = ["path", "group", "name", "src_sr", "src_ch", "dur_s", "peak_dbfs", "tp_dbtp", "lufs_i", "lufs_mmax",
          "lead_ms", "attack_ms", "tail_ms", "centroid_hz", "low", "mid", "high", "error"]


def probe(path: Path) -> tuple[int, int]:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=sample_rate,channels",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout.strip().split(",")
    return (int(out[0]), int(out[1])) if len(out) == 2 and out[0].isdigit() else (0, 0)


def decode(path: Path, ch: int) -> np.ndarray:
    """→ mảng (n, ch) float32 ở 48 kHz."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", str(ch), "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch)


def db(x: float) -> float:
    return float(20 * np.log10(max(x, 1e-12)))


def measure(path: Path, root: Path) -> dict:
    rel = path.relative_to(root).as_posix()
    row = {"path": rel, "group": rel.split("/")[0] if "/" in rel else "", "name": path.stem}
    try:
        sr0, ch0 = probe(path)
        ch = 2 if ch0 >= 2 else 1
        x = decode(path, ch)
        if len(x) == 0:
            raise ValueError("không giải mã được")
        mono = x.mean(axis=1).astype(np.float64)
        a = np.abs(x).max(axis=1)
        peak = float(a.max())
        ipk = int(a.argmax())
        tp = max(float(np.abs(resample_poly(x[:, c].astype(np.float64), 4, 1)).max()) for c in range(ch))
        on = np.nonzero(a >= peak * 10 ** (-50 / 20))[0]
        lead = int(on[0]) if len(on) else 0
        alive = np.nonzero(a >= peak * 10 ** (-40 / 20))[0]
        end = int(alive[-1]) if len(alive) else ipk
        # BS.1770 cho nhiều kênh: cộng công suất các kênh (L, R hệ số 1) — xấp xỉ bằng đo kênh tổng có bù 3 dB khi stereo
        li = lufs_integrated(mono) + (3.0103 if ch == 2 else 0.0)
        lm = momentary_max(mono) + (3.0103 if ch == 2 else 0.0)
        seg = mono[lead:end + 1] if end > lead else mono
        spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2 if len(seg) > 16 else np.zeros(2)
        f = np.fft.rfftfreq(len(seg), 1 / SR) if len(seg) > 16 else np.zeros(2)
        tot = float(spec.sum()) or 1.0
        row.update(src_sr=sr0, src_ch=ch0, dur_s=round(len(x) / SR, 3), peak_dbfs=round(db(peak), 2), tp_dbtp=round(db(tp), 2),
                   lufs_i=round(li, 1), lufs_mmax=round(lm, 1), lead_ms=round(lead / SR * 1000, 1),
                   attack_ms=round((ipk - lead) / SR * 1000, 1), tail_ms=round((end - ipk) / SR * 1000, 1),
                   centroid_hz=round(float((f * spec).sum() / tot)), low=round(float(spec[f < 150].sum() / tot), 3),
                   mid=round(float(spec[(f >= 300) & (f <= 2000)].sum() / tot), 3), high=round(float(spec[f > 4000].sum() / tot), 3),
                   error="")
    except Exception as e:  # noqa: BLE001 — ghi lỗi vào dòng, không dừng cả danh mục
        row["error"] = str(e)[:120]
    return row


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--jobs", type=int, default=12)
    a = ap.parse_args(argv)
    if not a.root.is_dir():
        print(f"không thấy thư mục {a.root}", file=sys.stderr)
        return 2
    files = sorted(p for p in a.root.rglob("*") if p.suffix.lower() in EXTS)
    with ThreadPoolExecutor(a.jobs) as ex:
        rows = list(ex.map(lambda p: measure(p, a.root), files))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    bad = sum(1 for r in rows if r.get("error"))
    print(f"{len(rows)} file → {a.out} ({bad} lỗi)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
