"""Đo từng file âm trong một kho SFX để chọn và đặt mức: ghi ra CSV.

Mỗi file (giải mã 48 kHz; file mono nhân đôi nguyên mức ra 2 kênh — đúng như AE phát, đo trên bản render 22/10;
không dùng `-ac 2` của ffmpeg vì nó chia −3 dB mỗi kênh):
- dur: thời lượng (s); eff: độ dài hiệu dụng (đoạn trên −40 dB so với đỉnh); onset: lúc âm bắt đầu (s)
- peak_s: thời điểm biên độ lớn nhất (s) — để căn đỉnh âm vào khoảnh khắc hình
- peak_dbfs: đỉnh mẫu; tp_dbtp: đỉnh thật (lấy mẫu ×4, BS.1770-4 phụ lục 2)
- m_max: độ to tức thời lớn nhất (cửa sổ 400 ms, LUFS); i_lufs: độ to tích hợp có cổng (−70 LUFS, −10 LU)
- centroid: trọng tâm phổ (Hz) — âm càng "sáng" càng cao
Độ to theo ITU-R BS.1770-4 (lọc K ở 48 kHz). File ngắn hơn 400 ms được đệm im lặng tới 400 ms.
Chạy: python -I tools/phan_tich_sfx.py "<thư mục kho>" <out.csv>
"""
import csv
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from scipy.signal import lfilter, resample_poly

SR = 48000
EXT = {".wav", ".mp3", ".ogg"}
# Lọc K (BS.1770-4) cho 48 kHz: tầng 1 kệ cao, tầng 2 thông cao RLB.
K1 = ([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585])
K2 = ([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621])


def decode(path: Path) -> np.ndarray:
    ch = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=channels",
                         "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout.strip()
    ch = int(ch) if ch.isdigit() else 1
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ar", str(SR), "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    x = x[:len(x) // ch * ch].reshape(-1, ch).astype(np.float64)
    return np.repeat(x, 2, axis=1) if ch == 1 else x[:, :2]


def db(x: float) -> float:
    return float(20 * np.log10(x)) if x > 0 else -200.0


def loudness(x: np.ndarray) -> tuple:
    """(độ to tức thời lớn nhất, độ to tích hợp có cổng) theo BS.1770-4."""
    n400 = int(0.4 * SR)
    if len(x) < n400:
        x = np.vstack([x, np.zeros((n400 - len(x), 2))])
    y = lfilter(*K2, lfilter(*K1, x, axis=0), axis=0)
    p = np.cumsum(np.vstack([np.zeros((1, 2)), y ** 2]), axis=0)
    step = int(0.1 * SR)
    starts = np.arange(0, len(y) - n400 + 1, step)
    ms = ((p[starts + n400] - p[starts]) / n400).sum(axis=1)
    lk = -0.691 + 10 * np.log10(np.maximum(ms, 1e-20))
    m_max = float(lk.max())
    gated = ms[lk > -70]
    if not len(gated):
        return m_max, -200.0
    rel = -0.691 + 10 * np.log10(gated.mean()) - 10
    g2 = gated[-0.691 + 10 * np.log10(gated) > rel]
    return m_max, float(-0.691 + 10 * np.log10(g2.mean()))


def measure(path: Path, root: Path) -> dict:
    x = decode(path)
    row = {"file": path.relative_to(root).as_posix(), "nhom": path.relative_to(root).parts[0]}
    if not len(x):
        return {**row, "loi": "giải mã rỗng"}
    mono = np.abs(x).max(axis=1)
    pk = float(mono.max())
    above = np.nonzero(mono > pk * 10 ** (-40 / 20))[0]
    tp = max(float(np.abs(resample_poly(x[:, c], 4, 1)).max()) for c in range(2))
    spec = np.abs(np.fft.rfft(x.mean(axis=1))) ** 2
    freqs = np.fft.rfftfreq(len(x), 1 / SR)
    m_max, i_lufs = loudness(x)
    return {**row, "dur": round(len(x) / SR, 3), "eff": round((above[-1] - above[0]) / SR, 3),
            "onset": round(above[0] / SR, 3), "peak_s": round(int(np.argmax(mono)) / SR, 3),
            "peak_dbfs": round(db(pk), 1), "tp_dbtp": round(db(tp), 1), "m_max": round(m_max, 1),
            "i_lufs": round(i_lufs, 1), "centroid": int((spec * freqs).sum() / max(spec.sum(), 1e-20)), "loi": ""}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
    files = sorted(p for p in root.rglob("*") if p.suffix.lower() in EXT)
    with ThreadPoolExecutor(max_workers=8) as ex:
        rows = list(ex.map(lambda p: measure(p, root), files))
    keys = ["file", "nhom", "dur", "eff", "onset", "peak_s", "peak_dbfs", "tp_dbtp", "m_max", "i_lufs", "centroid", "loi"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in keys})
    bad = [r for r in rows if r.get("loi")]
    print(f"OK {len(rows)} file → {out} · lỗi giải mã {len(bad)}")


if __name__ == "__main__":
    main()
