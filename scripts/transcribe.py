#!/usr/bin/env python3
"""transcribe — bóc lời từng từ (faster-whisper large-v3-turbo, GPU rơi về CPU int8) cho media GỐC của manifest.

    python3 transcribe.py --manifest 00_storyboard_manifest.json --out OUT [--language vi] [--files 01_a-roll-1.mp4 …] [--dir MEDIA]

Mỗi cảnh: giọng = voice_file (B-roll), không có thì tiếng của video_file (A-roll). Ra OUT/transcripts/<tên file>.json (JSON kiểu Scribe);
file đã có thì bỏ qua (cache). Chạy trên media ĐÃ tăng tốc là sai: `speed_media.py plan` cần transcript tốc độ gốc.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HELPER = Path(__file__).resolve().parent / "apps" / "video-use" / "helpers" / "transcribe.py"


def load_transcribe_one():
    spec = importlib.util.spec_from_file_location("video_use_transcribe", HELPER)     # trùng tên `transcribe` với chính file này
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.transcribe_one


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True, help="thư mục đầu ra; transcript nằm ở OUT/transcripts/")
    ap.add_argument("--language", default="vi")
    ap.add_argument("--files", nargs="*", help="chỉ các file này (tên file hoặc tên không đuôi)")
    ap.add_argument("--dir", type=Path, help="thư mục media gốc (mặc định: thư mục chứa manifest)")
    a = ap.parse_args()
    src = (a.dir or a.manifest.parent).resolve()
    names = []
    for s in sorted(json.loads(a.manifest.read_text(encoding="utf-8"))["segments"], key=lambda s: s["seq_index"]):
        n = s["files"].get("voice_file") or s["files"]["video_file"]
        if n not in names and (not a.files or n in a.files or Path(n).stem in a.files):
            names.append(n)
    if not names:
        sys.exit("LỖI: không có file nào để bóc băng (kiểm --files / manifest)")
    todo = [n for n in names if not (a.out / "transcripts" / f"{Path(n).stem}.json").is_file()]
    print(f"{len(names)} file: {len(names) - len(todo)} đã có (cache), {len(todo)} cần bóc")
    transcribe_one = load_transcribe_one() if todo else None
    for n in todo:
        if not (src / n).is_file():
            sys.exit(f"LỖI: không thấy {src / n}")
        transcribe_one(src / n, a.out.resolve(), language=a.language)
    return 0


if __name__ == "__main__":
    sys.exit(main())
