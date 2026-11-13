"""Cân giọng cho đều giữa các clip và giữa các câu (người dùng chốt 2026-11-05 lần 12: có lúc thu nhỏ, lúc thu to, lúc
ngoài trời, lúc trong nhà → giọng phải đồng đều).

    from voice_level import level_segments, report
    wavs = level_segments([(src, s_in, dur, "A1"), ...], out_dir)       # mỗi đoạn một WAV đã cân, đặt lên A1 với gain 0
    print(report(wavs, phrases))                                          # LUFS từng đoạn + độ lệch giữa các câu

Chuỗi xử lý mỗi đoạn (ffmpeg, ~1 s / đoạn): lọc ù / xì (highpass 80 Hz, lowpass 14 kHz) → giảm ồn nhẹ (`afftdn`) → san
câu to / câu nhỏ trong cùng đoạn (`speechnorm`) → nén nhẹ → đo LUFS rồi bù đúng số dB về cùng mức (mặc định −16 LUFS).
Không dùng `loudnorm` một lượt: với đoạn ngắn 2–6 s nó làm lệch nặng hơn (đo THCN 07: 1,6 → 6,9 LU).
Đạt khi các đoạn lệch nhau ≤ 1,5 LU và các câu lệch nhau ≤ 3 LU (đo bằng `report`). Phòng ồn nặng: lọc
`scripts/apps/dviet-viral-text-audio-edit/scripts/clean_and_master_voice.py` trước (chậm hơn nhiều).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

CHAIN = ("highpass=f=80,lowpass=f=14000,afftdn=nf=-25,speechnorm=e=4:r=0.0005:l=1,"
         "acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=2")
DECLICK = 0.01           # giây fade vào / ra mỗi đoạn giọng


def lufs(path: str | Path, s: float = 0.0, d: float | None = None) -> float:
    cmd = ["ffmpeg", "-hide_banner", "-ss", f"{s:.3f}"] + (["-t", f"{d:.3f}"] if d else []) + \
          ["-i", str(path), "-af", "ebur128", "-f", "null", "-"]
    e = subprocess.run(cmd, capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s*(-?[\d.]+) LUFS", e)[-1])


def level(src: str | Path, s_in: float, dur: float, out: Path, target: float = -16.0) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".pre.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s_in:.3f}", "-t", f"{dur:.3f}", "-i", str(src),
                    "-af", CHAIN, "-ar", "48000", "-ac", "2", str(tmp)], check=True)   # 2 kênh: WAV mono đo −16 nhưng phát ra to thêm 3 dB
    g = target - lufs(tmp)
    # khử click 10 ms đầu / cuối mỗi đoạn (ghost-editor transitions.py: nối giọng cắt thẳng gây "tách")
    real = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(tmp)],
                                capture_output=True, text=True).stdout.strip() or dur)   # đoạn có thể ngắn hơn dur ở cuối file
    fade = f"afade=t=in:d={DECLICK},afade=t=out:st={max(0.0, real - DECLICK):.3f}:d={DECLICK}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af", f"volume={g:.2f}dB,{fade}", str(out)], check=True)
    tmp.unlink()
    return out


def level_segments(segs: list[tuple], out_dir: Path, target: float = -16.0) -> list[Path]:
    """segs = [(file nguồn, giây vào, độ dài, tên)] → WAV đã cân (bắt đầu ở 0 = giây vào của nguồn)."""
    return [level(src, s_in, dur, Path(out_dir) / f"voice_{name}.wav", target) for src, s_in, dur, name in segs]


def report(wavs: list[Path], phrases: list[tuple[int, float, float]] | None = None) -> str:
    """phrases = [(chỉ số wav, giây bắt đầu trong wav, độ dài)] — từng câu để đo độ lệch giữa các câu."""
    seg = [lufs(w) for w in wavs]
    lines = [f"đoạn: {', '.join(f'{v:.1f}' for v in seg)} LUFS · lệch {max(seg) - min(seg):.1f} LU"]
    if phrases:
        ph = [lufs(wavs[i], s, d) for i, s, d in phrases if d >= 0.6]
        lines.append(f"câu: {len(ph)} câu, {min(ph):.1f} … {max(ph):.1f} LUFS · lệch {max(ph) - min(ph):.1f} LU")
    return "\n".join(lines)
