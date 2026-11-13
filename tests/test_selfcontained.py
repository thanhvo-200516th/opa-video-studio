#!/usr/bin/env python3
"""Kiểm scripts/ tự chứa: không đường dẫn sang skill khác, không master_pipeline, các CLI tách ra chạy --help được.
Chạy: ~/.venvs/video-skills/bin/python tests/test_selfcontained.py"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FORBIDDEN = (".claude/skills", ".gemini/", ".agents/skills", "master_pipeline")
CLIS = ("env_status", "prep_video", "matte", "facecam", "audit_sfx", "limit_master", "master_audio", "normalize_tts",
        "transcribe", "speed_media", "silence_cut")
OLD_SKILL = ".claude/skills/master-video-edit"          # skill cũ: lõi (scripts/, assets/) không được trỏ tới
ASSET_SUFFIXES = {".py", ".json", ".md", ".html", ".js", ".mjs", ".sh", ".txt"}

fails: list[str] = []


def check(ok: bool, label: str, detail: str = "") -> None:
    print(f"[{'OK' if ok else 'LỖI'}] {label}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        fails.append(label)


def test_no_foreign_paths() -> None:
    files = sorted([*SCRIPTS.glob("*.py"), *(SCRIPTS / "style_analysis").glob("*")])
    hits = []
    for f in files:
        if not f.is_file():
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        hits += [f"{f.relative_to(ROOT)}: {w}" for w in FORBIDDEN if w in text]
    check(not hits, f"không đường dẫn ngoài skill / master_pipeline trong {len(files)} file", "; ".join(hits[:5]))


def test_no_old_skill_path() -> None:
    """scripts/ (trừ apps/ bản chép nguyên gốc) và assets/ không chứa đường dẫn tới skill cũ master-video-edit."""
    files = [f for d in (SCRIPTS, ROOT / "assets") for f in d.rglob("*")
             if f.is_file() and f.suffix in ASSET_SUFFIXES and "apps" not in f.relative_to(d).parts and "node_modules" not in f.parts]
    hits = [str(f.relative_to(ROOT)) for f in files if OLD_SKILL in f.read_text(encoding="utf-8", errors="replace")]
    check(not hits, f"không có `{OLD_SKILL}` trong {len(files)} file scripts/ + assets/", "; ".join(hits[:6]))


def test_cli_help() -> None:
    for name in CLIS:
        path = SCRIPTS / f"{name}.py"
        if not path.is_file():
            check(False, f"{name}.py --help", "không có file")
            continue
        r = subprocess.run([sys.executable, str(path), "--help"], capture_output=True, text=True, timeout=60)
        check(r.returncode == 0, f"{name}.py --help thoát 0", (r.stderr or r.stdout)[-200:])


def test_normalize_tts() -> None:
    r = subprocess.run([sys.executable, str(SCRIPTS / "normalize_tts.py"), "Làm 1 video tốn 4% token!"],
                       capture_output=True, text=True, timeout=60)
    check(r.returncode == 0 and "%" not in r.stdout and r.stdout.strip() != "", "normalize_tts.py chuẩn hóa câu thoại", r.stderr[-200:] or r.stdout)


if __name__ == "__main__":
    test_no_foreign_paths()
    test_no_old_skill_path()
    test_cli_help()
    test_normalize_tts()
    if fails:
        print(f"\nCÓ {len(fails)} LỖI: {', '.join(fails)}")
        sys.exit(1)
    print("\nTẤT CẢ ĐẠT")
