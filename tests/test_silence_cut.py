#!/usr/bin/env python3
"""silence_cut.speech_segments: lặng đầu 0,28 s của TTS / HeyGen, kẹp theo độ dài file, fps=None, --max-end.
Chạy: ~/.venvs/video-skills/bin/python tests/test_silence_cut.py"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from silence_cut import speech_segments  # noqa: E402

fails: list[str] = []


def check(ok: bool, label: str, detail: str = "") -> None:
    print(f"[{'OK' if ok else 'LỖI'}] {label}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        fails.append(label)


def wav(path: Path, parts: list[str]) -> Path:
    """Nối các nguồn lavfi (đã ghi sẵn thời lượng) thành WAV mono 48 kHz."""
    args = sum((["-f", "lavfi", "-i", src] for src in parts), [])
    graph = "".join(f"[{i}]aresample=48000,aformat=channel_layouts=mono[a{i}];" for i in range(len(parts)))
    graph += "".join(f"[a{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=0:a=1[o]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", graph, "-map", "[o]", str(path)], check=True, timeout=60)
    return path


def dur(path: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                                capture_output=True, text=True, check=True).stdout)


TONE = "sine=f=300:d=1.5"
FIRST_AT_0 = [{"text": "một", "start": 0.0, "end": 1.2}]       # Whisper báo chữ đầu ở 0,0 dù giọng vào 0,28 s


def test_lead_in(tmp: Path) -> None:
    digital = wav(tmp / "digital.wav", ["anullsrc=r=48000:cl=mono:d=0.28", TONE])
    noise = wav(tmp / "noise.wav", ["anoisesrc=d=0.28:c=white:a=0.005:r=48000", TONE])   # ≈ −46 dB: dưới ngưỡng −35
    for name, f in (("lặng số 0,28 s", digital), ("nhiễu −45 dB 0,28 s", noise)):
        segs = speech_segments(f, FIRST_AT_0)
        check(bool(segs) and 0.15 <= segs[0][0] <= 0.25, f"lead-in {name}: đoạn đầu vào 0,15–0,25 s", str(segs))


def test_tone_from_zero(tmp: Path) -> None:
    f = wav(tmp / "tone0.wav", [TONE, "anullsrc=r=48000:cl=mono:d=1", TONE])
    segs = speech_segments(f, [{"text": "a", "start": 0.0, "end": 1.4}, {"text": "b", "start": 2.5, "end": 3.9}])
    check(len(segs) == 2 and segs[0][0] == 0.0, "tiếng vào từ 0,0 → giữ 0,0 (không cắt nhầm)", str(segs))


def test_clamp_to_duration(tmp: Path) -> None:
    f = wav(tmp / "endspeech.wav", ["anullsrc=r=48000:cl=mono:d=0.5", "sine=f=300:d=1.0"])
    d = dur(f)
    segs = speech_segments(f, [{"text": "a", "start": 0.55, "end": 1.4}])
    check(bool(segs) and segs[-1][1] <= d and segs[-1][1] < 100, "file kết thúc bằng tiếng: đoạn cuối ≤ độ dài file, không 99999",
          f"{segs} dur={d}")
    segs_none = speech_segments(f, [{"text": "a", "start": 0.55, "end": 1.4}], fps=None)
    check(bool(segs_none) and segs_none[-1][1] <= d + 1e-6, "fps=None: không làm tròn khung, vẫn ≤ độ dài file", str(segs_none))
    segs_cap = speech_segments(f, [{"text": "a", "start": 0.55, "end": 1.4}], max_end=1.2)
    check(bool(segs_cap) and segs_cap[-1][1] <= 1.2, "max_end=1,2 kẹp đoạn cuối", str(segs_cap))
    tail_sil = wav(tmp / "endsil.wav", [TONE, "anullsrc=r=48000:cl=mono:d=2"])
    segs_sil = speech_segments(tail_sil, [{"text": "a", "start": 0.0, "end": 1.4}])
    check(len(segs_sil) == 1 and segs_sil[0][1] < 2.0, "lặng tới hết file: không sinh đoạn rỗng", str(segs_sil))


def test_cli_max_end(tmp: Path) -> None:
    f = wav(tmp / "cli.wav", ["anullsrc=r=48000:cl=mono:d=0.5", "sine=f=300:d=3.0"])
    words = tmp / "w.json"
    words.write_text(json.dumps([{"text": "a", "start": 0.55, "end": 3.0}]))
    out = tmp / "o.json"
    r = subprocess.run([sys.executable, str(ROOT / "scripts/silence_cut.py"), str(f), "--words", str(words), "--max-end", "2.0",
                        "-o", str(out)], capture_output=True, text=True, timeout=60)
    segs = json.loads(out.read_text())["segments"] if r.returncode == 0 else []
    check(r.returncode == 0 and bool(segs) and segs[-1][1] <= 2.0, "CLI --max-end 2.0", (r.stderr or str(segs))[-200:])


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        test_lead_in(tmp)
        test_tone_from_zero(tmp)
        test_clamp_to_duration(tmp)
        test_cli_max_end(tmp)
    if fails:
        print(f"\nCÓ {len(fails)} LỖI: {', '.join(fails)}")
        sys.exit(1)
    print("\nTẤT CẢ ĐẠT")
