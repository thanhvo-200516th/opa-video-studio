"""Ghép master vào video câm (gói E, KH §3.9 CLI âm, NC §3.5 bước 6).

python tools/audio/mux.py <id> [--video <mp4>] [--out <mp4>] [--audio <wav>] [--build <json>]
  1) tsx scripts/export-cues.ts <id> --check và md5 cues = build.json md5.cues; lệch → exit 2.
  2) Mặc định: out/<id>/video-muted.mp4 → out/<id>/<id>_9x16.mp4 (master) và _9x16_sfx-only.mp4 (chỉ SFX),
     chép cues.csv và LICENSES.md vào out/<id>/. Có --out: chỉ ghép một bản master vào đường đó.
  --audio / --build: thay WAV / build.json mặc định (để thử với dữ liệu giả).
  Áp audioOffsetFrames bằng -itsoffset (dương = audio trễ hơn hình). ffprobe: lệch thời lượng a/v < 1 f.
  Exit 0 = đạt, 1 = ffmpeg lỗi hoặc lệch thời lượng, 2 = lỗi đầu vào / thiếu file / cues lệch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FPS = 30
MSG_STALE = "cues khác timeline/khác lần build, chạy lại npm run audio:v2"


class InputError(Exception):
    """Lỗi đầu vào → exit 2."""


def _which(name: str) -> str:
    exe = shutil.which(name)
    if not exe:
        raise InputError(f"không thấy {name} trên PATH")
    return exe


def check_cues(sheet_id: str, cues_json: Path, build_json: Path) -> None:
    """export-cues --check (node + cli của tsx, danh sách tham số, không shell) rồi so md5 với build.json."""
    cli = ROOT / "node_modules" / "tsx" / "dist" / "cli.mjs"
    if not cli.is_file():
        raise InputError(f"thiếu {cli}")
    r = subprocess.run([_which("node"), str(cli), "scripts/export-cues.ts", sheet_id, "--check"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise InputError(f"{MSG_STALE}\n{(r.stdout + r.stderr).strip()[-600:]}")
    if not build_json.is_file():
        raise InputError(f"thiếu {build_json}; chạy npm run audio:v2")
    want = json.loads(build_json.read_text(encoding="utf-8")).get("md5", {}).get("cues")
    have = hashlib.md5(cues_json.read_bytes()).hexdigest()
    if want != have:
        raise InputError(f"{MSG_STALE} (md5 {have} ≠ build.json {want})")


def offset_frames(cues_json: Path) -> float:
    return float(json.loads(cues_json.read_text(encoding="utf-8"))["audioOffsetFrames"])


def mux_one(video: Path, audio: Path, out: Path, off_frames: float) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [_which("ffmpeg"), "-hide_banner", "-nostats", "-loglevel", "error", "-y", "-i", str(video),
           "-itsoffset", f"{off_frames / FPS:.6f}", "-i", str(audio),
           "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ac", "2",
           "-movflags", "+faststart", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg mux lỗi ({r.returncode}): {r.stderr.strip()[-800:]}")


def av_durations(path: Path) -> dict:
    """ffprobe → {"video": s, "audio": s} (duration của từng luồng)."""
    cmd = [_which("ffprobe"), "-v", "error", "-show_entries", "stream=codec_type,duration", "-of", "json", str(path)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"ffprobe lỗi: {r.stderr.strip()}")
    out = {}
    for s in json.loads(r.stdout).get("streams", []):
        if s.get("codec_type") in ("video", "audio") and "duration" in s:
            out.setdefault(s["codec_type"], float(s["duration"]))
    if set(out) != {"video", "audio"}:
        raise RuntimeError(f"{path}: thiếu luồng video hoặc audio ({out})")
    return out


def check_sync(path: Path) -> bool:
    d = av_durations(path)
    diff = abs(d["audio"] - d["video"])
    ok = diff < 1.0 / FPS
    print(f"{'PASS' if ok else 'FAIL'} lệch thời lượng a/v {diff * FPS:.3f} f "
          f"(video {d['video']:.4f} s, audio {d['audio']:.4f} s) {path.name}")
    return ok


def run(a: argparse.Namespace) -> int:
    sid = a.sheet_id
    out_dir = ROOT / "out" / sid
    cues_json = ROOT / "src" / "audio" / "cues" / f"{sid}.json"
    build_json = Path(a.build) if a.build else out_dir / "audio" / "build.json"
    video = Path(a.video) if a.video else out_dir / "video-muted.mp4"
    master = Path(a.audio) if a.audio else ROOT / "public" / "audio" / f"{sid}-master.wav"
    for f in (cues_json, video, master):
        if not f.is_file():
            raise InputError(f"thiếu {f}")
    check_cues(sid, cues_json, build_json)
    off = offset_frames(cues_json)
    jobs = [(master, Path(a.out))] if a.out else [(master, out_dir / f"{sid}_9x16.mp4")]
    if not a.out:
        sfx = ROOT / "public" / "audio" / f"{sid}-sfx-master.wav"
        if not sfx.is_file():
            raise InputError(f"thiếu {sfx}")
        jobs.append((sfx, out_dir / f"{sid}_9x16_sfx-only.mp4"))
    ok = True
    for audio, out in jobs:
        mux_one(video, audio, out, off)
        ok = check_sync(out) and ok
    if not a.out:
        shutil.copyfile(ROOT / "src" / "audio" / "cues" / f"{sid}.csv", out_dir / "cues.csv")
        shutil.copyfile(ROOT / "public" / "audio" / "LICENSES.md", out_dir / "LICENSES.md")
    print(f"audioOffsetFrames {off:g}; {'đạt' if ok else 'CÓ FAIL'}")
    return 0 if ok else 1


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Ghép master vào video câm (gói E)")
    ap.add_argument("sheet_id")
    ap.add_argument("--video")
    ap.add_argument("--out")
    ap.add_argument("--audio")
    ap.add_argument("--build")
    a = ap.parse_args()
    try:
        return run(a)
    except (InputError, OSError) as e:
        print(f"LỖI: {e}")
        return 2
    except RuntimeError as e:
        print(f"LỖI: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
