"""Hàm dùng chung khi viết build_spec.py cho timeline FilmCraft (rút từ THCN 01–03, trước đây chép tay qua từng video).

    import sys; sys.path.insert(0, str(Path(__file__).resolve().parent))
    from build_kit import sfx_clip, pack, beat_grid, on_beat, align_words

CLI:  python build_kit.py beats NHẠC.mp3 …     # BPM, chu kỳ phách, pha
      python build_kit.py sfx FILE …           # lead / đỉnh / mức đỉnh / độ dài của SFX
"""
from __future__ import annotations

import re
import difflib
import shutil
import subprocess
import sys
import unicodedata
from functools import lru_cache
from pathlib import Path

import numpy as np

FFMPEG = shutil.which("ffmpeg") or str(Path.home() / ".local/bin/ffmpeg")


# ---------- SFX ----------
@lru_cache(None)
def sfx_info(path: str) -> dict:
    """Đo SFX: khoảng lặng đầu (lead), thời điểm đỉnh, mức đỉnh (dBFS), độ dài, điểm hết tiếng (tail)."""
    pcm = subprocess.run([FFMPEG, "-v", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", "48000", "-"],
                         capture_output=True, check=True).stdout
    x = np.abs(np.frombuffer(pcm, np.int16).astype(np.float32) / 32768)
    peak = float(x.max()) or 1e-9
    win = 480                                    # bao 10 ms
    env = np.array([x[i:i + win].max() for i in range(0, len(x), win)])
    above = np.nonzero(env > peak * 10 ** (-30 / 20))[0]
    lead = above[0] * 0.01 if len(above) else 0.0
    tail = (above[-1] + 1) * 0.01 if len(above) else len(x) / 48000
    # đỉnh theo độ to nghe được (RMS 10 ms làm mượt 50 ms), không theo mẫu lớn nhất: whoosh dài có tiếng tách nhỏ đầu file
    # → căn sai 0,3–0,4 s (qa_sync Huy OPA 2, 2026-11-05)
    rms = np.array([np.sqrt(np.mean(x[i:i + win] ** 2)) for i in range(0, len(x), win)])
    rms = np.convolve(np.pad(rms, 2, mode="edge"), np.ones(5) / 5, mode="valid") if len(rms) >= 5 else rms   # mép không kéo lệch
    return {"lead": round(float(lead), 3), "peak_t": round(int(np.argmax(rms)) * 0.01, 3),
            "peak_db": round(20 * float(np.log10(peak)), 1), "dur": round(len(x) / 48000, 3), "tail": round(float(tail), 3)}


def sfx_clip(tag: str, path, cue_t: float, align: str, peak_target: float, max_dur: float | None = None,
             end: float | None = None, src_in: float | None = None) -> dict:
    """Clip SFX cho spec: align="peak" → đỉnh tiếng rơi đúng cue_t, "onset" → tiếng bắt đầu ở cue_t.
    peak_target = mức đỉnh mong muốn (dBFS) → gain_db. end = độ dài video: cắt đuôi vượt video và giảm dần 0,25 s."""
    info = sfx_info(str(path))
    s_in = info["lead"] if src_in is None else src_in
    at = cue_t - max(0.0, info["peak_t"] - s_in) if align == "peak" else cue_t
    if at < 0:
        s_in, at = s_in - at, 0.0
    natural = min(info["dur"], info["tail"] + 0.3) - s_in
    dur = natural if max_dur is None else min(natural, max_dur)
    if end is not None:
        dur = min(dur, end - at)
    g = round(peak_target - float(info["peak_db"]), 1)
    dur = round(dur, 3)                          # key fade dùng đúng độ dài trả về (không vượt cuối clip)
    if end is not None and at + dur >= end - 1e-3 and dur < natural - 0.01:
        g = [[0, g], [max(0.0, dur - 0.25), g], [dur, -40]]
    return {"src": str(path), "at": round(at, 4), "in": round(s_in, 3), "dur": round(dur, 3),
            "gain_db": g, "name": f"SFX {tag} · {Path(path).stem[:28]}"}


def pack(clips: list, n: int) -> list:
    """Xếp clip (SFX…) vào n track không chồng nhau, sớm trước; thiếu track thì dừng với lỗi."""
    tracks = [[] for _ in range(n)]
    for c in sorted(clips, key=lambda c: c["at"]):
        for tr in tracks:
            if not tr or tr[-1]["at"] + tr[-1]["dur"] <= c["at"] + 1e-6:   # cùng ngưỡng với fc_build _check_overlaps
                tr.append(c)
                break
        else:
            raise SystemExit(f"thiếu track cho {c['name']} @ {c['at']}")
    return tracks


# ---------- nhịp nhạc ----------
def _onset_env(path: str, start: float, dur: float, sr: int = 22050, hop: int = 256, n: int = 1024):
    pcm = subprocess.run([FFMPEG, "-v", "error", "-ss", str(start), "-t", str(dur), "-i", path, "-f", "s16le", "-ac", "1",
                          "-ar", str(sr), "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    win = np.hanning(n)
    spec = np.array([np.abs(np.fft.rfft(x[i:i + n] * win)) for i in range(0, len(x) - n, hop)])
    flux = np.maximum(0, np.diff(np.log1p(spec * 10), axis=0)).sum(1)
    flux = flux - np.convolve(flux, np.ones(16) / 16, "same")
    return np.maximum(flux, 0), sr / hop


def beat_grid(path: str, start: float = 0.0, dur: float = 75.0):
    """(BPM, chu kỳ phách s, pha s, độ rõ 0–1, đường bao). Vào nhạc ở `in` = pha → phách rơi ở k·chu kỳ trên timeline."""
    env, fps = _onset_env(path, start, dur)
    ac = np.correlate(env, env, "full")[len(env) - 1:]
    lags = np.arange(len(ac)) / fps
    lag = int(np.argmax(ac * ((lags > 60 / 180) & (lags < 60 / 70))))
    phase = int(np.argmax([env[p::lag].sum() for p in range(lag)])) / fps
    return 60 / (lag / fps), lag / fps, phase, float(ac[lag] / ac[0]), env


def on_beat(t: float, period: float, floor: float = 0.0) -> float:
    """Kéo mốc chữ lớn vào phách gần nhất nếu phách sớm hơn ≤ 0,15 s hoặc trễ hơn ≤ 0,06 s; không sớm hơn floor
    (điểm cắt của đoạn)."""
    b = round(t / period) * period
    return max(floor, round(b, 4)) if -0.15 <= b - t <= 0.06 else t


# ---------- phụ đề ----------
def _norm(s: str) -> str:
    return unicodedata.normalize("NFC", s.lower().strip(" ,.“”!?"))


def align_words(toks: list[str], cands: list[dict]) -> list[float]:
    """Khớp chữ phụ đề (chính tả theo kịch bản) với từ Whisper [{text, start}] bằng difflib → giây bắt đầu từng chữ;
    chữ không khớp thì nội suy giữa hai chữ khớp gần nhất (đầu/cuối: cách 0,18 s)."""
    times: list = [None] * len(toks)
    sm = difflib.SequenceMatcher(None, [_norm(t) for t in toks], [_norm(w["text"]) for w in cands], autojunk=False)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            times[a + k] = cands[b + k]["start"]
    known = [k for k, t in enumerate(times) if t is not None]
    if not known:
        return times
    for k in range(len(times)):
        if times[k] is None:
            p = max((kk for kk in known if kk < k), default=None)
            q = min((kk for kk in known if kk > k), default=None)
            if p is not None and q is not None:
                times[k] = times[p] + (times[q] - times[p]) * (k - p) / (q - p)
            elif p is not None:
                times[k] = times[p] + 0.18 * (k - p)
            else:
                times[k] = times[q] - 0.18 * (q - k)
    return times


def refine_words(words: list[dict], audio: str, offset: float = 0.0, sr: int = 16000) -> list[dict]:
    """Căn lại mốc bắt đầu từng từ của Whisper theo tiếng thật (2026-11-05, THCN 07: chữ lệch giọng).

    Đo trên THCN 07: từ đầu mỗi đoạn sau khoảng lặng, Whisper turbo đặt sớm hơn tiếng thật 0,18–0,29 s.
    - Từ sau khoảng lặng ≥ 0,25 s: mốc = chỗ năng lượng vượt nền + 18 dB đầu tiên trong [−0,1; +0,5] s.
    - Từ giữa câu: mỗi chữ tiếng Việt là một âm tiết có một điểm bật năng lượng (spectral flux) → kéo về điểm bật gần nhất
      trong ±0,2 s. Giữ thứ tự, các từ cách nhau ≥ 0,06 s. words = [{"text", "start", "end"}] theo giây của `audio` + offset.
    """
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", str(audio), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                                     capture_output=True, check=True).stdout, np.float32)
    hop, n = sr // 100, 512
    if len(x) < n * 2:
        return [dict(w) for w in words]
    fr = np.lib.stride_tricks.sliding_window_view(np.pad(x, (n // 2, n // 2)), n)[::hop] * np.hanning(n)
    mag = np.log1p(np.abs(np.fft.rfft(fr, axis=1)) * 50)
    flux = np.r_[0, np.maximum(0, np.diff(mag, axis=0)).sum(1)]
    db = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
    floor = np.percentile(db, 10)
    peaks = [i for i in range(1, len(flux) - 1) if flux[i] >= flux[i - 1] and flux[i] > flux[i + 1]
             and flux[i] > np.percentile(flux, 60)]
    out, last = [], -1.0
    for i, w in enumerate(words):
        t = w["start"] - offset
        gap = t - ((words[i - 1]["end"] - offset) if i else -1.0)
        if gap >= 0.25:
            i0, i1 = int(max(0.0, t - 0.1) * 100), int((t + 0.5) * 100)
            new = next(((i0 + j) / 100 for j in range(max(0, i1 - i0)) if i0 + j < len(db) and db[i0 + j] > floor + 18), t)
        else:
            near = [p / 100 for p in peaks if abs(p / 100 - t) <= 0.2]
            new = min(near, key=lambda p: abs(p - t)) if near else t
        new = max(new, last + 0.06)
        last = new
        out.append({**w, "start": round(new + offset, 3)})
    for i in range(len(out) - 1):
        out[i]["end"] = round(min(out[i]["end"], out[i + 1]["start"]) if out[i]["end"] > out[i]["start"] else out[i + 1]["start"], 3)
    return out


def broll_scale(w: int, h: int, cw: int = 1080, ch: int = 1920, overscan: float = 1.02) -> float:
    """Tính % scale chuẩn cho mọi kích thước B-roll (dọc 704×1248, 1080×1920 hay ngang 1920×1080) để phủ kín khung
    mà không bao giờ bị viền đen 2 bên hoặc trên dưới trên FilmCraft."""
    cover_px = max(cw / w, ch / h) * 100.0 * overscan
    cover_fitw = max(cw / w, ch / h) / (cw / w) * 100.0 * overscan
    return round(max(cover_px, cover_fitw), 2)


def clamp_keys(spec: dict) -> dict:
    """Kẹp mọi keyframe nằm gọn trong thời lượng clip và bỏ clip ngắn hơn 1 khung (rút từ HanhTrinhMoi_OPA2_MotionFX)."""
    fps = float(spec.get("fps", 30))

    def fix(v, d):
        if not (isinstance(v, list) and v and isinstance(v[0], list)):
            return v
        end = int(d * 1000) / 1000 - 0.001
        keep = [k for k in v if k[0] <= end]
        if len(keep) < len(v):
            keep.append([end, v[-1][1], *v[-1][2:]])
        return keep

    for tr in spec.get("tracks", []):
        tr["clips"] = [c for c in tr.get("clips", []) if c.get("dur", 0) >= 1 / fps]
        for c in tr["clips"]:
            g = c.get("gain_db")
            if isinstance(g, list):
                g = fix(g, c["dur"])
                mono = []
                for k in g:
                    if not mono or k[0] > mono[-1][0] + 1e-3:
                        mono.append(k)
                c["gain_db"] = mono if len(mono) > 1 else mono[0][1]
            for e in c.get("effects", []):
                e["params"] = {k: fix(v, c["dur"]) for k, v in e.get("params", {}).items()}
            if "opacity" in c:
                c["opacity"] = fix(c["opacity"], c["dur"])
            for k, v in list((c.get("motion") or {}).items()):
                c["motion"][k] = fix(v, c["dur"])
    return spec


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("beats", "sfx"):
        sys.exit(__doc__)
    for p in sys.argv[2:]:
        if sys.argv[1] == "beats":
            bpm, per, ph, cl, _ = beat_grid(p)
            print(f"{bpm:6.1f} BPM  chu kỳ {per:.3f}s  pha {ph:.3f}s  độ rõ {cl:.2f}  {Path(p).name}")
        else:
            print(sfx_info(p), Path(p).name)


_NUM_FRAG = re.compile(r"^[.,]\d{3}$")
_ONE_UNITS = {"video", "bài", "ngày", "tháng", "tuần", "phút", "giây", "lần", "người", "kênh", "tỷ", "triệu", "nghìn", "ngàn", "trăm", "năm"}


def tidy_words(words: list[tuple]) -> list[tuple]:
    """Chữ phụ đề từ lời Whisper: dính mảnh số bị tách ("300" + ".000" → "300.000", để không ngắt dòng giữa số)
    và đổi «một» + đơn vị đếm → "1" (một video → 1 video). Chỉ dùng cho phụ đề; mốc tìm cụm vẫn theo lời gốc."""
    out: list[tuple] = []
    for t, s, e in words:
        if out and _NUM_FRAG.match(t) and re.search(r"\d$", out[-1][0]):
            out[-1] = (out[-1][0] + t, out[-1][1], e)
            continue
        out.append((t, s, e))
    # tên riêng đọc theo âm tiết (HeyGen / Whisper) → chữ gọn trên hình: «Ô Pê A» → OPA, «Hây Gen» → HeyGen
    BRAND = [(("ô", "pê", "a"), "OPA"), (("hây", "gen"), "HeyGen")]
    merged: list[tuple] = []
    i = 0
    while i < len(out):
        hit = None
        for seq, rep in BRAND:
            n = len(seq)
            if tuple(x[0].lower().strip(".,?!:;") for x in out[i:i + n]) == seq:
                tail = out[i + n - 1][0][len(out[i + n - 1][0].rstrip(".,?!:;")):]
                hit = (n, (rep + tail, out[i][1], out[i + n - 1][2]))
                break
        if hit:
            merged.append(hit[1])
            i += hit[0]
        else:
            merged.append(out[i])
            i += 1
    out = merged
    for i, (t, s, e) in enumerate(out):
        core = t.rstrip(".,?!:;")
        if core.lower() == "một" and i + 1 < len(out) and out[i + 1][0].lower().strip(".,?!:;") in _ONE_UNITS:
            out[i] = ("1" + t[len(core):], s, e)
    return out


# ---------- tăng tốc: mốc theo tốc độ gốc → mốc trên media đã tăng tốc (v2.5) ----------
def at_speed(items: list, f: float, fps: int = 30) -> list:
    """Chia mốc cho tốc độ f. Cặp (a, b) → bám khung `fps` MỘT lần (a/f, b/f); từ {"text", "start", "end"} → start / end chia f
    (làm tròn 1 ms, giữ khoá khác). Dùng cho segs và words của `media/speed_plan.json` (giây theo bản gốc)."""
    out = []
    for it in items:
        if isinstance(it, dict):
            out.append({**it, "start": round(it["start"] / f, 3), "end": round(it["end"] / f, 3)})
        else:
            out.append(tuple(round(x / f * fps) / fps for x in it))
    return out


def script_words(toks: list[str], words: list[dict], segs: list[tuple], t0s: list[float], fps: int = 30) -> list[tuple]:
    """Chữ phụ đề của MỘT cảnh theo kịch bản (B10): [(chữ, bắt đầu, kết thúc)] trên timeline.
    toks = chữ kịch bản; words = lời Whisper [{text, start}] cùng thời gian với segs (đã at_speed); segs = [(a, b)] các đoạn giữ;
    t0s = giờ timeline bắt đầu từng đoạn (độ dài đoạn = b − a bám khung, như V1). Chữ rơi vào khoảng đã cắt dồn về đầu đoạn kế."""
    starts = align_words(toks, words)
    out = []
    for j, (tok, s) in enumerate(zip(toks, starts)):
        k = next((i for i, (_, b) in enumerate(segs) if s < b - 0.02), len(segs) - 1)
        a, b = segs[k]
        d = round(round((b - a) * fps) / fps, 3)
        nxt = starts[j + 1] if j + 1 < len(starts) else b
        tl_s = round(t0s[k] + max(0.0, s - a), 3)
        tl_e = round(min(t0s[k] + d, t0s[k] + max(0.08, min(nxt, b) - a)), 3)
        out.append((tok, tl_s, max(tl_e, round(tl_s + 0.08, 3))))
    return out


# ---------- cắt cứng: dời điểm cắt V1 về sát chữ đầu câu (C7, hồ sơ minimal-edu) ----------
@lru_cache(None)
def file_len(src: str) -> float:
    """Độ dài file media (giây) bằng ffprobe."""
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                                capture_output=True, text=True, check=True).stdout)


def _start(w) -> float:
    return float(w["start"] if isinstance(w, dict) else w[1])


def retime_cuts(v1_clips: list[dict], words: list, fps: float, lead_frames: int = 1, flen=None) -> tuple[list[dict], list[tuple[float, int]]]:
    """Cắt cứng không có overlay che: dời MỖI điểm cắt của V1 về đúng `lead_frames` khung trước chữ đầu tiên bắt đầu ≥ cắt − 0,04 s (C7: 0–67 ms).
    words = [(chữ, bắt đầu, …)] hoặc [{"start": …}] theo giờ timeline; flen(src) → độ dài file (mặc định ffprobe).
    Bỏ qua điểm cắt nếu chữ cách > 0,4 s, nếu `in` của clip sau xuống < 0, hoặc đoạn trước (in + dur) vượt hết file.
    Trả (clip mới, [(điểm cắt cũ, ms dời)]) — danh sách clip là bản sao, đầu vào không bị sửa."""
    flen = flen or (lambda src: file_len(str(src)))
    out, moved = [dict(c) for c in v1_clips], []
    for i in range(1, len(out)):
        prev, nxt = out[i - 1], out[i]
        cut = nxt["at"]
        w = next((_start(w) for w in words if _start(w) >= cut - 0.04), None)
        if w is None or w - cut > 0.4:
            continue
        new = round(round((w - lead_frames / fps) * fps) / fps, 4)
        if new > w:
            new -= 1 / fps
        d = round(new - cut, 4)
        if abs(d) < 1e-3 or nxt["in"] + d < 0 or prev["in"] + prev["dur"] + d > flen(prev["src"]) - 1e-3:
            continue
        out[i - 1] = {**prev, "dur": round(prev["dur"] + d, 4)}
        out[i] = {**nxt, "at": round(new, 4), "in": round(nxt["in"] + d, 4), "dur": round(nxt["dur"] - d, 4)}
        moved.append((round(cut, 2), round(d * 1000)))
    return out, moved


# Luật D4 (người dùng chốt 2026-11-13): chỉ được tăng tốc 1.10x hoặc 1.05x — BỎ HẲN 1.25x / 1.15x;
# video < 45 s không tăng tốc, và tăng tốc không được đẩy video xuống dưới 45 s.
SPEED_STEPS, SPEED_MIN_RESULT_S = (1.1, 1.05), 45.0
ALLOWED_SPEEDS = (1.0, *SPEED_STEPS)


def choose_speed(total_src_seconds: float, steps: tuple = SPEED_STEPS, min_result: float = SPEED_MIN_RESULT_S) -> float:
    """Mức cao nhất trong `steps` (1.10x → 1.05x) mà video sau tăng tốc vẫn ≥ `min_result` giây (45 s); không mức nào đạt
    thì giữ 1.0x. `total_src_seconds` = tổng độ dài các đoạn giữ lại, tính theo tốc độ gốc."""
    for s in steps:
        if round(total_src_seconds / s, 3) >= min_result:  # làm tròn mili-giây: 49,5 s / 1,1 = 45 s đúng ngưỡng
            return s
    return 1.0


def speed_dir(speed: float) -> str:
    """Thư mục media / transcript theo tốc độ: 1.1 → 'x110' (mỗi tốc độ một thư mục, không dùng nhầm bản cũ x125 / x115)."""
    if speed not in ALLOWED_SPEEDS:
        raise ValueError(f"tốc độ {speed}x không được phép (chỉ {ALLOWED_SPEEDS})")
    return f"x{round(speed * 100)}"


# Rule 3 (2026-11-11): ưu tiên chất lượng vào / ra — giữ nguyên độ phân giải gốc, không scale khi chỉ đổi tốc độ / cắt,
# x264 CRF 12 preset slow (gần như không mất), gắn đúng hệ màu BT.709, AAC 320 kbps 48 kHz.
X264_HQ = ["-c:v", "libx264", "-crf", "12", "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-movflags", "+faststart"]
AAC_HQ = ["-c:a", "aac", "-b:a", "320k", "-ar", "48000"]
MP3_HQ = ["-c:a", "libmp3lame", "-b:a", "320k"]
EXPORT_CRF = 14            # FilmCraft xuất MP4 giao (chỉ khi được yêu cầu)
