#!/usr/bin/env python3
"""
clean_and_master_voice.py — Open-Source Audio Filtering, De-Noising, EQ & -14 LUFS Mastering Pipeline
Designed for Premiere Pro & FilmCraft (.fcproj) Talking-Head / Short-Form Video Workflows.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile


def find_ffmpeg():
    for cand in ["/home/vmiz/.local/bin/ffmpeg", shutil.which("ffmpeg"), "/usr/bin/ffmpeg"]:
        if cand and os.path.isfile(cand):
            return cand
    raise RuntimeError("Could not find ffmpeg binary.")


def run_FilterChain(ffmpeg_bin, input_path, output_path, mode="studio", target_lufs=-14.0, true_peak=-1.5):
    """
    Applies a multi-stage vocal cleanup and broadcast leveling chain modeled after:
    1. DeepFilterNet / RNNoise (Spectral Noise Floor Reduction via afftdn)
    2. VxStudio VXTone & FabFilter Pro-Q (85Hz HPF, 235Hz boxiness cut, 3.4kHz presence boost, 10.5kHz air shelf)
    3. VxStudio VXSpeechClarity / DiaPro (6.4kHz Sibilance De-Essing band cut)
    4. Master_Me / OptoComp (Smooth vocal compression + EBU R128 Loudnorm to -14 LUFS / -1.5 dBTP)
    """
    # Optional: If DeepFilterNet CLI is installed (Python `deepFilter` or Rust `deep-filter`), run it first on a 48kHz PCM WAV
    deep_filter_bin = shutil.which("deepFilter") or shutil.which("deep-filter")
    work_input = input_path
    tmp_dir = tempfile.mkdtemp(prefix="openaudio_")

    try:
        if deep_filter_bin and mode in ("studio", "heavy"):
            raw_wav = os.path.join(tmp_dir, "raw_48k.wav")
            subprocess.run(
                [ffmpeg_bin, "-y", "-i", input_path, "-vn", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", raw_wav],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            df_dir = os.path.join(tmp_dir, "df")  # bản Rust ghi trùng tên đầu vào → thư mục riêng
            subprocess.run([deep_filter_bin, "-D", raw_wav, "-o", df_dir], check=True)
            for name in ("raw_48k_DeepFilterNet3.wav", "raw_48k.wav"):  # tên ra của bản Python / bản Rust
                if os.path.isfile(os.path.join(df_dir, name)):
                    work_input = os.path.join(df_dir, name)
                    break

        nr_amount = 18 if mode == "heavy" else (12 if mode == "studio" else 6)
        af_chain = (
            f"highpass=f=85:poles=2,"
            f"afftdn=nr={nr_amount}:nf=-42:tn=1,"
            f"equalizer=f=235:t=q:w=2.2:g=-3.8,"
            f"equalizer=f=3400:t=q:w=1.4:g=2.8,"
            f"equalizer=f=6400:t=q:w=3.0:g=-3.5,"
            f"treble=g=2.2:f=10500,"
            f"acompressor=threshold=-18dB:ratio=3.2:attack=10:release=110:makeup=2.5dB,"
            f"loudnorm=I={target_lufs}:TP={true_peak}:LRA=7:print_format=json"
        )

        cmd = [
            ffmpeg_bin, "-y", "-i", work_input,
            "-vn", "-af", af_chain,
            "-ar", "48000", "-c:a", "pcm_s24le",
            output_path
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"FFmpeg audio pipeline failed:\n{proc.stderr[-800:]}")

        # Parse loudnorm stats if present
        m = re.search(r"\{\s*\"input_i\"\s*:.*?\}", proc.stderr, re.S)
        stats = json.loads(m.group(0)) if m else {}
        return stats
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="Clean, filter, EQ and master dialogue audio to -14 LUFS.")
    parser.add_argument("--input", "-i", required=True, help="Input video or audio file")
    parser.add_argument("--output", "-o", required=True, help="Output 48kHz 24-bit WAV file")
    parser.add_argument("--mode", choices=["light", "studio", "heavy"], default="studio", help="Noise reduction & polish intensity")
    parser.add_argument("--lufs", type=float, default=-14.0, help="Target integrated loudness in LUFS (default: -14.0)")
    args = parser.parse_args()

    ffmpeg_bin = find_ffmpeg()
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    stats = run_FilterChain(ffmpeg_bin, args.input, args.output, mode=args.mode, target_lufs=args.lufs)
    print(f"[OK] Saved mastered 48kHz 24-bit audio to: {args.output}")
    if stats:
        print(f"     Loudness: {stats.get('input_i')} -> {stats.get('output_i')} LUFS | True Peak: {stats.get('output_tp')} dBTP")


if __name__ == "__main__":
    main()
