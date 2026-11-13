"""Transcribe a video locally with faster-whisper (no API key, nothing uploaded).

master-video-edit port (2026-10-29): the original uploaded audio to ElevenLabs Scribe. This version runs
faster-whisper large-v3-turbo on this machine and writes the same Scribe-shaped JSON
({"language_code", "text", "words": [{"text", "start", "end", "type": "word"|"spacing", "speaker_id"}]})
to <edit_dir>/transcripts/<video_stem>.json, so pack_transcripts.py / timeline_view.py work unchanged.
No diarization: every word gets speaker_id "speaker_0".

Run with the venv that has faster-whisper:
    ~/.venvs/video-skills/bin/python helpers/transcribe.py <video_path> [--edit-dir DIR] [--language vi]

Cached: if the output file already exists, transcription is skipped.
"""

from __future__ import annotations

import argparse
import ctypes
import glob
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import numpy as np

MODEL = os.environ.get("WHISPER_MODEL", "mobiuslabsgmbh/faster-whisper-large-v3-turbo")
FFMPEG = "/home/vmiz/.local/bin/ffmpeg" if Path("/home/vmiz/.local/bin/ffmpeg").exists() else "ffmpeg"
# CUDA libraries that already exist on this machine inside other tools' venvs (the video-skills venv lacks them)
CUDA_LIB_GLOBS = [
    "~/.local/share/uv/tools/resemble-enhance/lib/python3*/site-packages/nvidia/cublas/lib/libcublasLt.so.12",
    "~/.local/share/uv/tools/resemble-enhance/lib/python3*/site-packages/nvidia/cublas/lib/libcublas.so.12",
    "~/.local/share/uv/tools/audio-separator/lib/python3*/site-packages/nvidia/cudnn/lib/libcudnn*.so.9",
]
_model = None
_lock = threading.Lock()


def load_api_key() -> None:
    """Kept for transcribe_batch.py compatibility — local transcription needs no key."""
    return None


def _preload_cuda() -> None:
    for pattern in CUDA_LIB_GLOBS:
        for lib in sorted(glob.glob(os.path.expanduser(pattern))):
            try:
                ctypes.CDLL(lib, mode=ctypes.RTLD_GLOBAL)
            except OSError:
                pass


def _get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _preload_cuda()
        try:
            _model = WhisperModel(MODEL, device="cuda", compute_type="int8_float16")
        except Exception as e:  # no GPU / missing libs / out of memory → CPU
            print(f"  cuda unavailable ({e}); using CPU", flush=True)
            _model = WhisperModel(MODEL, device="cpu", compute_type="int8")
    return _model


def load_audio(video_path: Path) -> np.ndarray:
    pcm = subprocess.run([FFMPEG, "-v", "error", "-i", str(video_path), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0


def call_whisper(video_path: Path, language: str | None = None) -> dict:
    audio = load_audio(video_path)
    with _lock:                       # one GPU model shared by the batch threads
        segments, info = _get_model().transcribe(audio, language=language, word_timestamps=True, vad_filter=True, beam_size=5)
        segments = list(segments)
    words: list[dict] = []
    for seg in segments:
        for w in seg.words or []:
            if words:
                words.append({"text": " ", "start": words[-1]["end"], "end": round(w.start, 3), "type": "spacing", "speaker_id": "speaker_0"})
            words.append({"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3), "type": "word",
                          "speaker_id": "speaker_0", "logprob": round(w.probability, 3)})
    return {"language_code": info.language, "language_probability": round(info.language_probability, 3),
            "text": " ".join(s.text.strip() for s in segments), "words": words, "engine": f"faster-whisper:{MODEL}"}


def transcribe_one(
    video: Path,
    edit_dir: Path,
    api_key: str | None = None,
    language: str | None = None,
    num_speakers: int | None = None,
    verbose: bool = True,
) -> Path:
    """Transcribe a single video. Returns path to transcript JSON (cached if it exists).
    api_key / num_speakers are accepted for compatibility and ignored."""
    transcripts_dir = edit_dir / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    out_path = transcripts_dir / f"{video.stem}.json"
    if out_path.exists():
        if verbose:
            print(f"cached: {out_path.name}")
        return out_path
    if verbose:
        print(f"  transcribing {video.name} locally", flush=True)
    t0 = time.time()
    payload = call_whisper(video, language)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    if verbose:
        n = sum(1 for w in payload["words"] if w["type"] == "word")
        print(f"  saved: {out_path.name} ({out_path.stat().st_size / 1024:.1f} KB) in {time.time() - t0:.1f}s — words: {n}")
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(description="Transcribe a video locally with faster-whisper")
    ap.add_argument("video", type=Path, help="Path to video file")
    ap.add_argument("--edit-dir", type=Path, default=None, help="Edit output directory (default: <video_parent>/edit)")
    ap.add_argument("--language", type=str, default=None, help="ISO language code (e.g. 'vi'). Omit to auto-detect.")
    ap.add_argument("--num-speakers", type=int, default=None, help="Ignored (no diarization locally).")
    args = ap.parse_args()
    video = args.video.resolve()
    if not video.exists():
        sys.exit(f"video not found: {video}")
    edit_dir = (args.edit_dir or (video.parent / "edit")).resolve()
    transcribe_one(video=video, edit_dir=edit_dir, language=args.language)


if __name__ == "__main__":
    main()
