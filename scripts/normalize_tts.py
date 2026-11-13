#!/usr/bin/env python3
"""normalize_tts — chuẩn hóa nhanh câu thoại tiếng Việt sang dạng chữ cho TTS (HeyGen / ElevenLabs).

    python3 normalize_tts.py "Làm 1 video tốn 4% token!"

Dùng hàm normalize_vi_tts của analyze_and_scaffold.py.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_and_scaffold import normalize_vi_tts  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Chuẩn hóa nhanh câu thoại tiếng Việt sang dạng chữ cho TTS (HeyGen / ElevenLabs)")
    parser.add_argument("text", help="Câu thoại cần chuẩn hóa")
    args = parser.parse_args()
    print(normalize_vi_tts(args.text))
    sys.exit(0)


if __name__ == "__main__":
    main()
