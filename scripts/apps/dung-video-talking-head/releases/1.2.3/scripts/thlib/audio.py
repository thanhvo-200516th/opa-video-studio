"""thlib.audio — thư viện đo & xử lý âm thanh dùng chung cho toàn bộ skill.

Port từ `prototype/vlib.py` (D:/MMO/Van Minh AI/docs/specs/2026-09-11-rulebook-
evidence/prototype/vlib.py), hệ số K-weighting là BS.1770 ở 48 kHz (KB1/KA1/
KB2/KA2). `phone()` ở đây KHÔNG có low-pass mặc định (khác bản prototype gốc
có `lpf=12000.0`) — đúng theo task brief 1.1.
"""

from __future__ import annotations

import subprocess

import numpy as np
from scipy.io import wavfile
from scipy.ndimage import uniform_filter1d
from scipy.signal import bilinear, butter, lfilter, resample_poly, sosfilt

SR = 48000

# Hệ số K-weighting theo BS.1770 (48 kHz): tầng shelf tần số cao (1) rồi
# tầng highpass (2).
KB1 = [1.53512485958697, -2.69169618940638, 1.19839281085285]
KA1 = [1.0, -1.69065929318241, 0.73248077421585]
KB2 = [1.0, -2.0, 1.0]
KA2 = [1.0, -1.99004745483398, 0.99007225036621]

# Short-term và LRA theo EBU Tech 3341/3342: cửa sổ 3 s, bước 0,1 s (hằng của chuẩn, như
# block 400 ms của integrated_lufs).
ST_WIN_S = 3.0
ST_HOP_S = 0.1


def decode(path, ch: int = 2) -> np.ndarray:
    """Giải mã file media qua ffmpeg thành PCM float64 [n, ch] ở SR=48kHz."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", str(ch), "-ar", str(SR),
         "-f", "f32le", "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64).reshape(-1, ch)


def channel_count(path) -> int:
    """Số kênh của luồng audio đầu tiên trong `path` (ffprobe)."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
         "stream=channels", "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    return int(out.split()[0])


def decode_mono(path) -> np.ndarray:
    """Giải mã theo đúng số kênh gốc rồi hạ mono: (L+R)/2 (trung bình mọi
    kênh) cho nguồn nhiều kênh (S04), giữ nguyên mẫu cho nguồn mono. Không
    nhờ ffmpeg nâng mono lên stereo (`-ac 2`) — swresample nâng mono→stereo
    ở mức −3 dB (ma trận tâm 0,707) nên sẽ hụt mức nếu nguồn là mono."""
    ch = channel_count(path)
    x = decode(path, ch)
    return x[:, 0] if ch == 1 else x.mean(axis=1)


def write_wav(path, x: np.ndarray, sr: int = SR) -> None:
    """Ghi WAV PCM 16-bit; x là mono [n] hoặc stereo [n, 2], clip về [-1, 1]."""
    clipped = np.clip(x, -1.0, 1.0)
    pcm16 = (clipped * 32767.0).astype(np.int16)
    wavfile.write(str(path), sr, pcm16)


def db(v) -> np.ndarray:
    """Đổi biên độ tuyến tính sang dBFS (sàn -240 dB để tránh log(0))."""
    return 20 * np.log10(np.maximum(np.asarray(v, dtype=float), 1e-12))


def rms_env(x: np.ndarray, win_s: float) -> np.ndarray:
    """Đường bao RMS trượt theo cửa sổ win_s giây."""
    w = max(1, int(round(win_s * SR)))
    return np.sqrt(np.maximum(uniform_filter1d(x * x, size=w, mode="constant"), 0))


def kweight(x: np.ndarray) -> np.ndarray:
    """Lọc K-weighting BS.1770 (shelf cao tần rồi highpass)."""
    return lfilter(KB2, KA2, lfilter(KB1, KA1, x))


def momentary(x: np.ndarray) -> np.ndarray:
    """Độ to tức thời kiểu LUFS (cửa sổ 400 ms) từ tín hiệu đã K-weight."""
    kx = kweight(x)
    ms = uniform_filter1d(kx * kx, size=int(0.4 * SR), mode="constant")
    return -0.691 + 10 * np.log10(np.maximum(ms, 1e-20))


def a_weight(x: np.ndarray) -> np.ndarray:
    """A-weighting (IEC 61672) — proxy thô cho mức nghe 40-phon / loa nhỏ."""
    f1, f2, f3, f4 = 20.598997, 107.65265, 737.86223, 12194.217
    a1000 = 1.9997
    nums = [(2 * np.pi * f4) ** 2 * (10 ** (a1000 / 20)), 0, 0, 0, 0]
    dens = np.polymul([1, 4 * np.pi * f4, (2 * np.pi * f4) ** 2], [1, 4 * np.pi * f1, (2 * np.pi * f1) ** 2])
    dens = np.polymul(np.polymul(dens, [1, 2 * np.pi * f3]), [1, 2 * np.pi * f2])
    b, a = bilinear(nums, dens, SR)
    return lfilter(b, a, x)


def a_momentary(x: np.ndarray) -> np.ndarray:
    """Độ to tức thời (400 ms) trên tín hiệu đã A-weight."""
    ax = a_weight(x)
    ms = uniform_filter1d(ax * ax, size=int(0.4 * SR), mode="constant")
    return 10 * np.log10(np.maximum(ms, 1e-20))


def hpf(x: np.ndarray, fc: float = 120.0, order: int = 2) -> np.ndarray:
    """Highpass Butterworth bậc order, tần số cắt fc."""
    return sosfilt(butter(order, fc, btype="highpass", fs=SR, output="sos"), x)


def phone(x: np.ndarray, hpf: float = 300.0, order: int = 4) -> np.ndarray:
    """Mô phỏng loa điện thoại: chỉ highpass dốc (mặc định 300 Hz, bậc 4),
    KHÔNG lowpass (khác bản prototype gốc). Tham số `hpf` là tần số cắt (Hz),
    trùng tên với hàm hpf() ở trên nhưng không xung đột vì phone() tự áp
    bộ lọc sos, không gọi lại hàm đó."""
    sos = butter(order, hpf, btype="highpass", fs=SR, output="sos")
    return sosfilt(sos, x)


def phone_k(x: np.ndarray) -> np.ndarray:
    """Độ to (K-weight) của tín hiệu sau khi qua phone()."""
    return momentary(phone(x))


def phone_a(x: np.ndarray) -> np.ndarray:
    """Độ to (A-weight) của tín hiệu sau khi qua phone()."""
    return a_momentary(phone(x))


def true_peak_db(x: np.ndarray) -> float:
    """Ước lượng true peak bằng oversample 4x (resample_poly) rồi lấy đỉnh."""
    up = resample_poly(x, 4, 1)
    return float(db(np.abs(up).max()))


def spectrum(x: np.ndarray):
    """Phổ công suất trung bình theo cửa sổ Hann 4096 mẫu, hop 1024."""
    n, hop = 4096, 1024
    if len(x) < n:
        x = np.pad(x, (0, n - len(x)))
    fr = np.lib.stride_tricks.sliding_window_view(x, n)[::hop]
    P = (np.abs(np.fft.rfft(fr * np.hanning(n), axis=1)) ** 2).sum(axis=0)
    return np.fft.rfftfreq(n, 1 / SR), P


def band_frac(f: np.ndarray, P: np.ndarray, lo: float, hi: float) -> float:
    """Tỉ lệ năng lượng phổ P nằm trong dải tần [lo, hi)."""
    return float(P[(f >= lo) & (f < hi)].sum() / P.sum())


def runs(mask: np.ndarray) -> list[tuple[int, int]]:
    """Danh sách các đoạn [a, b) liên tục mà mask khác 0."""
    d = np.diff(mask.astype(np.int8), prepend=0, append=0)
    return list(zip(np.where(d == 1)[0].tolist(), np.where(d == -1)[0].tolist()))


def integrated_lufs(x: np.ndarray) -> float:
    """Độ to tích hợp theo BS.1770: block 400 ms, hop 100 ms (75% overlap),
    gate tuyệt đối -70 LUFS rồi gate tương đối -10 LU quanh trung bình đã gate.
    x mono [n] hoặc stereo [n, 2]: công suất block = tổng công suất hai kênh
    (G = 1,0 cho L/R — Ruling R10, khớp ffmpeg ebur128)."""
    kx = kweight(np.atleast_2d(np.asarray(x, dtype=float).T))   # [c, n]
    block = int(0.4 * SR)
    hop = int(0.1 * SR)
    if kx.shape[1] < block:
        kx = np.pad(kx, ((0, 0), (0, block - kx.shape[1])))
    n_blocks = 1 + (kx.shape[1] - block) // hop
    powers = np.empty(n_blocks)
    for i in range(n_blocks):
        seg = kx[:, i * hop: i * hop + block]
        powers[i] = np.mean(seg * seg, axis=1).sum()

    def loudness(p):
        return -0.691 + 10 * np.log10(np.maximum(p, 1e-20))

    gated_abs = powers[loudness(powers) >= -70.0]
    if len(gated_abs) == 0:
        return float(loudness(1e-20))
    rel_threshold = loudness(np.mean(gated_abs)) - 10.0
    gated_rel = gated_abs[loudness(gated_abs) >= rel_threshold]
    if len(gated_rel) == 0:
        gated_rel = gated_abs
    return float(loudness(np.mean(gated_rel)))


def short_term(x: np.ndarray) -> np.ndarray:
    """Độ to short-term (EBU Tech 3341/3342: cửa sổ ST_WIN_S) của x mono [n] hoặc nhiều
    kênh [n, c], công suất = tổng công suất các kênh (BS.1770, R10). Phần tử k là cửa sổ
    [k·ST_HOP_S, k·ST_HOP_S + ST_WIN_S); chỉ các cửa sổ nằm trọn trong x."""
    kx = kweight(np.atleast_2d(np.asarray(x, dtype=float).T))   # [c, n]
    win, hop = int(round(ST_WIN_S * SR)), int(round(ST_HOP_S * SR))
    if kx.shape[1] < win:
        return np.empty(0)
    cs = np.concatenate([[0.0], np.cumsum((kx * kx).sum(axis=0))])
    starts = np.arange(0, kx.shape[1] - win + 1, hop)
    power = (cs[starts + win] - cs[starts]) / win
    return -0.691 + 10 * np.log10(np.maximum(power, 1e-20))


def lra_gate(st: np.ndarray) -> np.ndarray:
    """Mặt nạ cửa sổ short-term qua hai cổng của EBU Tech 3342: tuyệt đối −70 LUFS, rồi
    tương đối −20 LU dưới độ to (trung bình công suất) của các cửa sổ đã qua cổng tuyệt đối."""
    st = np.asarray(st, dtype=float)
    keep = st >= -70.0
    if not keep.any():
        return keep
    rel = -0.691 + 10 * np.log10(np.mean(10 ** ((st[keep] + 0.691) / 10))) - 20.0
    return keep & (st >= rel)


def lra(st: np.ndarray) -> float:
    """Loudness range (EBU Tech 3342): phân vị 95 − phân vị 10 (numpy tuyến tính) của các
    cửa sổ short-term qua lra_gate; không còn cửa sổ nào thì 0."""
    st = np.asarray(st, dtype=float)
    kept = st[lra_gate(st)]
    if len(kept) == 0:
        return 0.0
    return float(np.percentile(kept, 95) - np.percentile(kept, 10))


def match_at(window: np.ndarray, seg: np.ndarray) -> int:
    """Vị trí (mẫu) trong `window` nơi `seg` khớp nhất: tương quan chéo chuẩn hoá theo năng lượng từng đoạn
    của window (R217, lô b04 video 22 — tương quan thô bị kéo về chỗ giọng to hơn cue, báo lệch giả +8,7 f)."""
    from scipy.signal import correlate
    num = correlate(window, seg, mode="valid", method="fft")
    cs = np.concatenate(([0.0], np.cumsum(np.asarray(window, dtype=float) ** 2)))
    energy = np.sqrt(np.maximum(cs[len(seg):] - cs[:-len(seg)], 0.0))
    return int(np.argmax(num / np.maximum(energy, 1e-12)))


def xcorr_lag_ms(a: np.ndarray, b: np.ndarray, max_ms: float = 200.0) -> float:
    """Độ trễ (ms) của b so với a bằng cross-correlation qua FFT, giới hạn
    tìm kiếm trong ±max_ms. Dương nghĩa là b đến sau a."""
    n = len(a) + len(b) - 1
    nfft = 1 << (n - 1).bit_length()
    fa = np.fft.rfft(a, nfft)
    fb = np.fft.rfft(b, nfft)
    corr = np.fft.irfft(fb * np.conj(fa), nfft)
    max_lag = int(round(max_ms * SR / 1000))
    lags = np.concatenate([np.arange(0, max_lag + 1), np.arange(-max_lag, 0)])
    vals = corr[lags]
    best = lags[np.argmax(vals)]
    return float(best) * 1000.0 / SR
