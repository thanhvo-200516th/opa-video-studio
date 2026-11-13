"""Nhập/xuất cho qa_audio (gói F): loader JSON riêng, đọc WAV/MP4, gọi ffmpeg/ffprobe, vẽ hình.

Không import code của D/E (KH §3.9). Loudness đo bằng ffmpeg ebur128.
"""
import json
import re
import subprocess
from pathlib import Path

import numpy as np
from scipy.io import wavfile

SR = 48000
FPS = 30


class InputError(Exception):
    """Thiếu file hoặc sai khóa đầu vào → CLI exit 2."""


SHEET_KEYS = ("schema", "id", "fps", "totalFrames", "sampleRate", "barFrames", "beatFrames",
              "events", "silences", "sections", "marks")
EVENT_KEYS = ("id", "f", "kind", "anchor", "gainDb", "sound")
SILENCE_KEYS = ("from", "to", "kind", "scope")
BUILD_KEYS = ("cues", "silences", "music_stop_sample", "tail_end_frame", "hit_gap_design_db",
              "logo_variant", "master")
BUILD_CUE_KEYS = ("id", "f", "kind", "start_sample", "end_sample", "anchor_sample")


def load_json(path: Path) -> dict:
    if not Path(path).is_file():
        raise InputError(f"thiếu file: {path}")
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        raise InputError(f"JSON hỏng: {path}: {exc}") from exc


def _need(obj: dict, keys, where: str) -> None:
    for k in keys:
        if k not in obj:
            raise InputError(f"{where}: thiếu khóa '{k}'")


def load_sheet(path: Path) -> dict:
    """Đọc cues.json schema 2, chỉ kiểm khóa cần cho QA."""
    sheet = load_json(path)
    _need(sheet, SHEET_KEYS, str(path))
    if sheet["schema"] != 2 or sheet["sampleRate"] != SR or sheet["fps"] != FPS:
        raise InputError(f"{path}: cần schema 2, 48000 Hz, 30 fps")
    for i, ev in enumerate(sheet["events"]):
        _need(ev, EVENT_KEYS, f"{path}: events[{i}]")
    for i, sil in enumerate(sheet["silences"]):
        _need(sil, SILENCE_KEYS, f"{path}: silences[{i}]")
    return sheet


def load_build(path: Path) -> dict:
    build = load_json(path)
    _need(build, BUILD_KEYS, str(path))
    for i, cue in enumerate(build["cues"]):
        _need(cue, BUILD_CUE_KEYS, f"{path}: cues[{i}]")
    return build


def read_wav(path: Path) -> np.ndarray:
    """WAV mono float64 (float32, PCM 16/24/32 đều được; nhiều kênh → trung bình)."""
    if not Path(path).is_file():
        raise InputError(f"thiếu file: {path}")
    sr, x = wavfile.read(str(path))
    if sr != SR:
        raise InputError(f"{path}: sample rate {sr}, cần {SR}")
    if x.dtype == np.int16:
        y = x.astype(np.float64) / 32768.0
    elif x.dtype == np.int32:  # scipy đọc 24-bit dạng int32 dồn trái
        y = x.astype(np.float64) / 2147483648.0
    elif x.dtype == np.uint8:
        y = (x.astype(np.float64) - 128.0) / 128.0
    else:
        y = x.astype(np.float64)
    return y.mean(axis=1) if y.ndim == 2 else y


def _run(cmd: list, binary: bool = False) -> subprocess.CompletedProcess:
    try:
        res = subprocess.run(cmd, capture_output=True, text=not binary,
                             encoding=None if binary else "utf-8",
                             errors=None if binary else "replace")
    except FileNotFoundError as exc:
        raise InputError(f"không chạy được {cmd[0]} (cần ffmpeg/ffprobe trên PATH)") from exc
    if res.returncode != 0:
        err = res.stderr if not binary else res.stderr.decode("utf-8", "replace")
        raise RuntimeError(f"{cmd[0]} lỗi {res.returncode}: {err[-600:]}")
    return res


def _num(tok: str) -> float:
    return float("-inf") if tok.strip() in ("-inf", "-nan", "nan") else float(tok)


def ebur128(path: Path) -> dict:
    """ffmpeg ebur128=peak=true → {I, LRA, TP, short: [(t_s, S_lufs)]}."""
    res = _run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
                "-af", "ebur128=peak=true", "-f", "null", "-"])
    text = res.stderr
    cut = text.rfind("Summary:")
    if cut < 0:
        raise RuntimeError(f"ebur128 không có Summary cho {path}")
    summ = text[cut:]
    num = r"(-?inf|-?[\d.]+)"
    out = {}
    for key, pat in (("I", r"I:\s*" + num + r"\s*LUFS"), ("LRA", r"LRA:\s*" + num + r"\s*LU"),
                     ("TP", r"Peak:\s*" + num + r"\s*dBFS")):
        m = re.search(pat, summ)
        if not m:
            raise RuntimeError(f"ebur128 thiếu {key} cho {path}")
        out[key] = _num(m.group(1))
    frames = re.findall(r"t:\s*([\d.]+)\s+TARGET.*?S:\s*(-?inf|-?[\d.]+)", text[:cut])
    out["short"] = [(float(t), _num(s)) for t, s in frames]
    return out


def silencedetect(path: Path, noise_db: float = -60.0, dur_s: float = 0.1) -> list:
    """Danh sách (đầu_s, cuối_s); khoảng chạy tới hết file có cuối = None."""
    res = _run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
                "-af", f"silencedetect=noise={noise_db}dB:d={dur_s}", "-f", "null", "-"])
    out, start = [], None
    for line in res.stderr.splitlines():
        m = re.search(r"silence_start:\s*(-?[\d.e+-]+)", line)
        if m:
            start = max(0.0, float(m.group(1)))
            continue
        m = re.search(r"silence_end:\s*(-?[\d.e+-]+)", line)
        if m and start is not None:
            out.append((start, float(m.group(1))))
            start = None
    if start is not None:
        out.append((start, None))
    return out


def decode_media(path: Path) -> np.ndarray:
    """Audio của MP4 → mono 48 kHz, mẫu 0 = thời điểm 0 của dòng thời gian (tôn trọng start_time)."""
    if not Path(path).is_file():
        raise InputError(f"thiếu file: {path}")
    res = _run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-af", "aresample=async=1:first_pts=0",
                "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], binary=True)
    return np.frombuffer(res.stdout, dtype="<f4").astype(np.float64)


def stream_durations(path: Path) -> dict:
    """ffprobe → {'video': giây, 'audio': giây} (thời điểm kết = start_time + duration)."""
    res = _run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration,start_time",
                "-of", "json", str(path)])
    out = {}
    for st in json.loads(res.stdout).get("streams", []):
        kind = st.get("codec_type")
        if kind in ("video", "audio") and kind not in out and st.get("duration") not in (None, "N/A"):
            start = st.get("start_time")
            start = float(start) if start not in (None, "N/A") else 0.0
            out[kind] = start + float(st["duration"])
    return out


def _draw_cues(png: Path, cue_frames: list, total_frames: int) -> None:
    from PIL import Image, ImageDraw
    img = Image.open(png).convert("RGB")
    draw = ImageDraw.Draw(img)
    w, h = img.size
    for f in cue_frames:
        x = int(round(f / total_frames * (w - 1)))
        draw.line([(x, 0), (x, h - 1)], fill=(10, 10, 10), width=1)
    img.save(png)


def plots(master: Path, out_dir: Path, cue_frames: list, total_frames: int) -> list:
    """wave.png (showwavespic) và spectrum.png (showspectrumpic) có vạch cue."""
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = (("wave.png", "showwavespic=s=1800x300:colors=0x0068FF"),
            ("spectrum.png", "showspectrumpic=s=1800x512:legend=0:scale=log"))
    made = []
    for name, filt in jobs:
        png = out_dir / name
        _run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", str(master), "-lavfi", filt,
              "-frames:v", "1", str(png)])
        _draw_cues(png, cue_frames, total_frames)
        made.append(png)
    return made
