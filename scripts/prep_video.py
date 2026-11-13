#!/usr/bin/env python3
"""prep_video — lọc ồn giọng nói AI (-14 LUFS) + bóc băng từng từ.

    python3 prep_video.py --input VIDEO_HOAC_AUDIO [--workdir ./prep_out] [--mode light|studio|heavy] [--skip-transcribe]
"""
import argparse
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
SKILL_ROOT = Path(__file__).resolve().parents[1]
APPS = SKILL_ROOT / "scripts" / "apps"
VENV_PY = HOME / ".venvs" / "video-skills" / "bin" / "python"
CLEAN_SCRIPT = APPS / "dviet-viral-text-audio-edit" / "scripts" / "clean_and_master_voice.py"
TRANSCRIBE_SCRIPT = APPS / "video-use" / "helpers" / "transcribe.py"


def run_cmd(cmd, check=True):
    print(f"▶ Thực thi: {' '.join(str(c) for c in cmd)}")
    return subprocess.run([str(c) for c in cmd], check=check)


def cmd_prep_video(args):
    workdir = Path(args.workdir).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    input_path = Path(args.input).resolve()
    stem = input_path.stem

    cleaned_wav = workdir / f"{stem}_voice_clean_14lufs.wav"
    run_cmd([
        VENV_PY,
        CLEAN_SCRIPT,
        "--input",
        input_path,
        "--output",
        cleaned_wav,
        "--mode",
        args.mode,
    ])

    if not args.skip_transcribe:
        # faster-whisper large-v3-turbo trên GPU (rơi về CPU), giải mã bằng ffmpeg; ra JSON kiểu Scribe có mốc từng từ.
        # (Script cũ motion-sfx-audio-mastering/scripts/transcribe.py cần 2 tham số, model large-v3 chưa có trong cache
        #  và vướng PyAV của venv — lỗi bị nuốt; đã thay 2026-10-29.)
        print("\n📝 Đang bóc băng lấy mốc thời gian từng từ (Word-level Timestamps)...")
        run_cmd([VENV_PY, TRANSCRIBE_SCRIPT, cleaned_wav, "--edit-dir", workdir, "--language", "vi"])
        print(f"   Transcript: {workdir / 'transcripts' / (cleaned_wav.stem + '.json')}")

    print(f"\n✅ Hoàn tất tiền xử lý! File voice sạch (-14 LUFS): {cleaned_wav}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Lọc ồn giọng nói AI (-14 LUFS) + Bóc băng từ khóa")
    parser.add_argument("--input", required=True, help="Đường dẫn file video hoặc audio đầu vào")
    parser.add_argument("--workdir", default="./prep_out", help="Thư mục lưu kết quả")
    parser.add_argument("--mode", default="studio", choices=["light", "studio", "heavy"])
    parser.add_argument("--skip-transcribe", action="store_true", help="Bỏ qua bước bóc băng")
    sys.exit(cmd_prep_video(parser.parse_args()))


if __name__ == "__main__":
    main()
