"""Cắt khoảng lặng tự động cho A-roll người nói: đoạn giữ = phần bù của `silencedetect` trên giọng đã lọc, bỏ tiếng rời
không có lời (thở, va chạm), nới chữ đầu nói nhỏ, đệm 0,07 s trước / 0,09 s sau, gộp khe < 0,12 s, khớp khung hình.
Chạy thật trên THCN 04 (clip 53,6 s → 34,5 s, 12 đoạn) ngày 2026-11-01; sửa lặng đầu video trên THCN 05 ngày 2026-11-03.

    import sys; sys.path.insert(0, str(Path(__file__).resolve().parent))
    from silence_cut import fit_words, load_words, speech_segments, Timeline
    words = load_words(transcript_json)
    segs = speech_segments(voice_wav, words)
    words = fit_words(words, segs)   # chữ Whisper đặt mốc trong khoảng lặng đã cắt → dời về đầu đoạn kế (phụ đề không rơi mất)
    tl = Timeline(segs)          # tl.T0[i], tl.end, tl.seg_of(src), tl.at(src), tl.seg_end(i), tl.end_of(src)

CLI:  python silence_cut.py VOICE.wav --words transcript.json [--noise -35] [--min-silence 0.3] [--max-end GIÂY] [-o segments.json]
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

FFMPEG = shutil.which("ffmpeg") or str(Path.home() / ".local/bin/ffmpeg")
FFPROBE = shutil.which("ffprobe") or str(Path.home() / ".local/bin/ffprobe")


def load_words(path: Path) -> list[dict]:
    """Từ có mốc [{text, start, end}] từ JSON kiểu Scribe ({"words": [... type word]}, của prep-video) hoặc danh sách từ."""
    d = json.loads(Path(path).read_text())
    words = d.get("words", d) if isinstance(d, dict) else d
    return [{"text": w["text"], "start": float(w["start"]), "end": float(w.get("end", float(w["start"]) + 0.2))}
            for w in words if w.get("type", "word") == "word"]


def duration(path: Path) -> float:
    """Độ dài file (giây) theo ffprobe."""
    out = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        raise RuntimeError(f"không đọc được độ dài file: {path}") from None


def silences(voice: Path, noise_db: float = -35, min_silence: float = 0.3, dur: float | None = None) -> list[tuple[float, float]]:
    """[(đầu lặng, cuối lặng)]; lặng chạy tới hết file thì cuối = độ dài file (`dur`, mặc định đo bằng ffprobe), không dùng mốc giả."""
    err = subprocess.run([FFMPEG, "-hide_banner", "-nostdin", "-i", str(voice), "-af", f"silencedetect=n={noise_db}dB:d={min_silence}",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", err)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    if len(en) < len(st):                                                # lặng tới hết file thì không có silence_end
        end = duration(voice) if dur is None else dur
        en += [end] * (len(st) - len(en))
    return list(zip(st, en))


def _sound_onset(a: float, quiet_ends: list[float]) -> float:
    """Đầu vùng có tiếng (ngưỡng thấp) chạy liền vào điểm a: cuối khoảng lặng ngưỡng thấp gần nhất trước a, không có thì 0."""
    return max((e for e in quiet_ends if e <= a + 0.01), default=0.0)


def speech_segments(voice: Path, words: list[dict], noise_db: float = -35, min_silence: float = 0.3, pad_in: float = 0.07,
                    pad_out: float = 0.09, merge_gap: float = 0.12, fps: int | None = 30,
                    max_end: float | None = None) -> list[tuple[float, float]]:
    """[(giây vào, giây ra)] các đoạn có lời, khớp khung (1/fps; fps=None = không làm tròn). Tiếng rời không chạm chữ nào
    (thở, va chạm) bị bỏ. Đoạn cuối kẹp theo độ dài file (và `max_end` nếu có), không bao giờ vượt hết file.
    Lặng đầu 0,28 s của TTS / HeyGen < `min_silence` nên silencedetect không báo: đo lại ở ngưỡng 0,12 s và vào ở cuối lặng đó."""
    dur = min(duration(voice), max_end if max_end is not None else math.inf)
    edges = [0.0] + [v for s in silences(voice, noise_db, min_silence, duration(voice)) for v in s] + [dur]
    speech = [(edges[i], min(edges[i + 1], dur)) for i in range(0, len(edges) - 1, 2)]       # (cuối lặng trước, đầu lặng sau)
    first = min((w["start"] for w in words), default=0.0)
    lead_end = 0.0
    if speech and speech[0][0] <= 0.02:                  # đầu file không báo lặng mà vẫn có lặng ngắn / nhiễu thấp đầu giọng
        lead_end = next((e for s, e in silences(voice, noise_db, 0.12, dur) if s <= 0.02 and e <= 1.0), 0.0)
        if 0 < lead_end < speech[0][1]:
            speech[0] = (lead_end, speech[0][1])
        else:
            lead_end = 0.0
    # chữ đầu nói nhỏ hơn ngưỡng (THCN 04): lùi điểm vào tới chữ đầu, nhưng không sớm hơn chỗ có tiếng thật ở ngưỡng thấp hơn
    # 15 dB — Whisper hay đặt chữ đầu sớm (THCN 05: "Là" 1,84 s, giọng vào 2,23 s → đầu video dư 0,4 s lặng, hình như bị dừng)
    quiet_ends = [e for _, e in silences(voice, noise_db - 15, 0.1, dur)]
    speech = [(min(a, max(first, _sound_onset(a, quiet_ends), lead_end if i == 0 else 0.0)) if a <= first + 0.5 else a, b)
              for i, (a, b) in enumerate(speech)]
    # giữ đoạn có chữ bắt đầu trong đó hoặc chồng lên (Whisper nghe nhầm "Thứ nhất" → "1." đặt mốc trước đoạn — THCN 04)
    keep = [(a, b) for a, b in speech if b > a and any(a - 0.15 <= w["start"] < b or (w["start"] < b and w.get("end", w["start"]) > a)
                                                         for w in words)]
    segs: list[tuple[float, float]] = []
    for a, b in keep:
        a, b = max(0.0, a - pad_in), min(b + pad_out, dur)
        if segs and a - segs[-1][1] < merge_gap:
            segs[-1] = (segs[-1][0], b)
        else:
            segs.append((a, b))
    if fps is None:
        return [(round(a, 3), round(b, 3)) for a, b in segs if a < dur and b > a]
    last = math.floor(dur * fps + 1e-6) / fps            # khung cuối còn nằm trong file
    out = [(round(a * fps) / fps, min(round(b * fps) / fps, last)) for a, b in segs if a < dur]
    return [(a, b) for a, b in out if b > a]


def fit_words(words: list[dict], segs: list[tuple[float, float]], reach: float = 0.6) -> list[dict]:
    """Bản mới của `words`: chữ có mốc vào rơi trong khoảng lặng đã cắt mà đoạn giữ kế tiếp bắt đầu trong `reach` giây → dời mốc
    về đầu đoạn đó (Whisper đặt sớm hơn tiếng thật; THCN 05: "Là" 1,84 → 2,17 s, "dựng" 47,90 → 48,10 s). Không có thì
    chữ đầu bị bộ lọc phụ đề bỏ mất, chữ đặt bằng `Timeline.at()` dài 0 s."""
    out = []
    for w in words:
        s = w["start"]
        nxt = None if any(a <= s < b for a, b in segs) else next((a for a, _ in segs if s < a <= s + reach), None)
        out.append(w if nxt is None else {**w, "start": nxt, "end": max(w.get("end", nxt), nxt + 0.05)})
    return out


class Timeline:
    """Đổi giây nguồn ↔ giây timeline sau khi cắt. Điểm cắt không làm tròn để đoạn sau khít đúng điểm cắt."""

    def __init__(self, segs: list[tuple[float, float]]) -> None:
        self.segs = segs
        self.T0, t = [], 0.0
        for a, b in segs:
            self.T0.append(t)
            t += b - a
        self.end = t

    def seg_of(self, src: float) -> int:
        """Đoạn chứa giây nguồn; rơi vào khoảng lặng đã cắt thì lấy đoạn gần nhất."""
        return min(range(len(self.segs)), key=lambda i: 0 if self.segs[i][0] <= src <= self.segs[i][1]
                   else min(abs(src - self.segs[i][0]), abs(src - self.segs[i][1])))

    def at(self, src: float) -> float:
        """Giây nguồn → giây timeline (kẹp vào đoạn giữ lại gần nhất)."""
        i = self.seg_of(src)
        a, b = self.segs[i]
        return self.T0[i] + min(max(src, a), b) - a

    def seg_end(self, i: int) -> float:
        return self.T0[i] + self.segs[i][1] - self.segs[i][0]

    def end_of(self, src: float) -> float:
        return self.seg_end(self.seg_of(src))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("voice", type=Path, help="giọng đã lọc (WAV) — ví dụ *_voice_clean_14lufs.wav của prep-video")
    ap.add_argument("--words", type=Path, required=True, help="JSON lời có mốc (transcripts/*.json của prep-video)")
    ap.add_argument("--noise", type=float, default=-35, help="ngưỡng lặng dB (mặc định -35)")
    ap.add_argument("--min-silence", type=float, default=0.3, help="khoảng lặng ngắn nhất bị cắt, giây (mặc định 0.3)")
    ap.add_argument("--max-end", type=float, default=None, help="kẹp đoạn cuối không quá giây này (ví dụ độ dài hình)")
    ap.add_argument("-o", "--out", type=Path)
    a = ap.parse_args()
    segs = speech_segments(a.voice, load_words(a.words), a.noise, a.min_silence, max_end=a.max_end)
    tl = Timeline(segs)
    src = segs[-1][1] - segs[0][0] if segs else 0
    print(f"{len(segs)} đoạn · nguồn {src:.1f} s → {tl.end:.2f} s (bỏ {src - tl.end:.1f} s lặng)")
    print(" ".join(f"{x:.2f}-{y:.2f}" for x, y in segs))
    if a.out:
        a.out.write_text(json.dumps({"voice": str(a.voice), "segments": segs, "duration": tl.end}, indent=1))


if __name__ == "__main__":
    main()
