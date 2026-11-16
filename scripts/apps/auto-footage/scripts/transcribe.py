"""Bóc lời video người nói → câu có mốc (để agent chia cảnh). Chạy bằng ~/.venvs/video-skills (faster-whisper).

    python transcribe.py VIDEO OUT_DIR [--prompt "kịch bản gợi ý"]   → OUT_DIR/transcript.json + transcript.txt
GPU: mượn libcublas / cudnn có sẵn trong venv công cụ khác; không có thì chạy CPU.
"""
import argparse
import ctypes
import glob
import json
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np

MODEL = os.environ.get("WHISPER_MODEL", "mobiuslabsgmbh/faster-whisper-large-v3-turbo")
CUDA_LIBS = ["~/.local/share/uv/tools/resemble-enhance/lib/python3*/site-packages/nvidia/cublas/lib/libcublasLt.so.12",
             "~/.local/share/uv/tools/resemble-enhance/lib/python3*/site-packages/nvidia/cublas/lib/libcublas.so.12",
             "~/.local/share/uv/tools/audio-separator/lib/python3*/site-packages/nvidia/cudnn/lib/libcudnn*.so.9"]


def model():
    from faster_whisper import WhisperModel
    for pat in CUDA_LIBS:
        for lib in sorted(glob.glob(os.path.expanduser(pat))):
            try:
                ctypes.CDLL(lib, mode=ctypes.RTLD_GLOBAL)
            except OSError:
                pass
    try:
        return WhisperModel(MODEL, device="cuda", compute_type="int8_float16")
    except Exception:  # noqa: BLE001 — không GPU / thiếu thư viện → CPU
        return WhisperModel(MODEL, device="cpu", compute_type="int8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--prompt", default=None)
    a = ap.parse_args()
    ff = shutil.which("ffmpeg") or "/home/vmiz/.local/bin/ffmpeg"
    pcm = subprocess.run([ff, "-v", "error", "-i", str(a.video), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    segs, _ = model().transcribe(audio, language="vi", vad_filter=True, beam_size=5, initial_prompt=a.prompt)
    rows = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()} for s in segs]
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "transcript.json").write_text(json.dumps({"video": str(a.video), "segments": rows}, ensure_ascii=False, indent=1))
    lines = [f"[{r['start']:6.2f}–{r['end']:6.2f}] {r['text']}" for r in rows]
    (a.out / "transcript.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
