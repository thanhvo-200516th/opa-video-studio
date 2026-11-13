#!/usr/bin/env python3
"""speed_media.py (plan → apply → check) trên hình lavfi 25 fps 108×192, build_kit.choose_speed, matte.py --start/--dur.
Chạy: ~/.venvs/video-skills/bin/python tests/test_speed_media.py"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
import build_kit  # noqa: E402

fails: list[str] = []


def check(ok: bool, label: str, detail: str = "") -> None:
    print(f"[{'OK' if ok else 'LỖI'}] {label}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        fails.append(label)


def sh(cmd: list, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True, timeout=timeout)


def tool(script: str, *args) -> subprocess.CompletedProcess:
    return sh([sys.executable, SCRIPTS / script, *args])


def probe(path: Path, entries: str, stream: str | None = None) -> str:
    sel = ["-select_streams", stream] if stream else []
    return sh(["ffprobe", "-v", "error", *sel, "-show_entries", entries, "-of", "csv=p=0", path]).stdout.strip()


def dur(path: Path) -> float:
    return float(probe(path, "format=duration"))


def make_wav(path: Path, parts: list[str]) -> None:
    args = sum((["-f", "lavfi", "-i", s] for s in parts), [])
    graph = "".join(f"[{i}]aresample=48000,aformat=channel_layouts=mono[a{i}];" for i in range(len(parts)))
    graph += "".join(f"[a{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=0:a=1[o]"
    r = sh(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", graph, "-map", "[o]", path])
    assert r.returncode == 0, r.stderr


def make_aroll(path: Path, wav: Path, d: float) -> None:
    r = sh(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc=s=108x192:r=25:d={d}", "-i", wav,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-shortest", path])
    assert r.returncode == 0, r.stderr


def words(spans: list[tuple[float, float]]) -> dict:
    return {"words": [{"text": f"từ{i}", "start": a, "end": b, "type": "word"} for i, (a, b) in enumerate(spans)]}


def fixture(src: Path) -> Path:
    """2 cảnh A-roll (~25,2 s giữ lại mỗi cảnh, lặng đầu 0,28 s) + 1 cảnh B-roll (hình câm 30 fps + giọng mp3) → giữ ~53 s."""
    src.mkdir(parents=True)
    (src / "transcripts").mkdir()
    lead = "anullsrc=r=48000:cl=mono:d=0.28"
    for name in ("01_a-roll-1", "03_a-roll-2"):
        wav = src / f"{name}.wav"
        make_wav(wav, [lead, "sine=f=300:d=12", "anullsrc=r=48000:cl=mono:d=0.8", "sine=f=330:d=13"])
        make_aroll(src / f"{name}.mp4", wav, 26.08)
        wav.unlink()
        (src / "transcripts" / f"{name}.json").write_text(json.dumps(words([(0.0, 1.0), (1.2, 6.0), (6.2, 12.2), (13.2, 20.0), (20.2, 26.0)])))
    make_wav(src / "02_voice-b-roll-1.wav", [lead, "sine=f=400:d=3"])
    sh(["ffmpeg", "-v", "error", "-y", "-i", src / "02_voice-b-roll-1.wav", "-b:a", "128k", src / "02_voice-b-roll-1.mp3"])
    (src / "02_voice-b-roll-1.wav").unlink()
    sh(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=108x192:r=30:d=3.5", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        src / "02_b-roll-1.mp4"])
    (src / "transcripts" / "02_voice-b-roll-1.json").write_text(json.dumps(words([(0.0, 1.5), (1.6, 3.2)])))
    seg = lambda i, p, t, v, vo: {"seq_index": i, "seq_prefix": p, "type": t, "files": {"video_file": v, "voice_file": vo}}  # noqa: E731
    manifest = src / "00_storyboard_manifest.json"
    manifest.write_text(json.dumps({"segments": [
        seg(1, "01", "a-roll", "01_a-roll-1.mp4", None), seg(2, "02", "b-roll", "02_b-roll-1.mp4", "02_voice-b-roll-1.mp3"),
        seg(3, "03", "a-roll", "03_a-roll-2.mp4", None)]}))
    return manifest


def test_choose_speed() -> None:
    check(build_kit.choose_speed(49.6) == 1.10 and build_kit.choose_speed(48) == 1.05 and build_kit.choose_speed(44) == 1.0,
          "choose_speed(49,6)=1.10 · (48)=1.05 · (44)=1.0")
    if hasattr(build_kit, "at_speed"):           # build_kit.at_speed do bộ mẫu build_spec thêm vào
        got = build_kit.at_speed([(1.0, 2.2)], 1.1)
        check(got == [(0.9, 2.0)], "at_speed([(1.0,2.2)], 1.1) = [(0.9, 2.0)]", str(got))
    else:
        print("[BỎ QUA] build_kit.at_speed chưa có (thuộc bộ mẫu build_spec)")


def test_pipeline(tmp: Path) -> None:
    src = tmp / "src"
    manifest = fixture(src)
    r = tool("transcribe.py", "--manifest", manifest, "--out", src)     # đủ transcript → chỉ báo cache, không nạp mô hình
    check(r.returncode == 0 and "3 đã có (cache), 0 cần bóc" in r.stdout, "transcribe.py: transcript đã có → báo cache, không bóc lại", (r.stderr or r.stdout)[-200:])
    out = tmp / "media"
    plan_json = out / "speed_plan.json"
    r = tool("speed_media.py", "plan", src, "--manifest", manifest, "--transcripts", src / "transcripts", "--out", plan_json)
    check(r.returncode == 0 and plan_json.is_file(), "plan chạy xong, ghi speed_plan.json", (r.stderr or r.stdout)[-300:])
    plan = json.loads(plan_json.read_text())
    sc = plan.get("scenes", [])
    check(plan.get("speed") == 1.1 and plan.get("speed_dir") == "x110" and 49.5 <= plan.get("kept_src_seconds", 0) <= 56,
          "plan: giữ ~53 s → 1.10x / x110", str({k: plan.get(k) for k in ("kept_src_seconds", "speed", "speed_dir")}))
    check([s["seq_prefix"] for s in sc] == ["01", "02", "03"] and all(s["segs"] and s["words"] and s["src_dur"] > 0 for s in sc)
          and sc[1]["voice"] == "02_voice-b-roll-1.mp3" and sc[0]["voice"] is None, "plan: 3 cảnh đủ seq_prefix / video / voice / src_dur / segs / words")
    check(0.15 <= sc[0]["segs"][0][0] <= 0.25 and sc[0]["segs"][-1][1] <= sc[0]["src_dur"] + 1e-6,
          "plan: lặng đầu 0,28 s bị cắt, đoạn cuối ≤ độ dài nguồn", str(sc[0]["segs"]))
    miss = tool("speed_media.py", "plan", src, "--manifest", manifest, "--transcripts", tmp / "khong_co", "--out", tmp / "p2.json")
    check(miss.returncode != 0 and "transcribe.py" in (miss.stdout + miss.stderr), "thiếu transcript → lỗi kèm lệnh transcribe.py", (miss.stdout + miss.stderr)[-200:])

    r = tool("speed_media.py", "apply", src, "--manifest", manifest, "--plan", plan_json, "--out", out, "--jobs", 2)
    x = out / "x110"
    names = ["01_a-roll-1.mp4", "02_b-roll-1.mp4", "02_voice-b-roll-1.mp3", "03_a-roll-2.mp4"]
    check(r.returncode == 0 and all((x / n).is_file() for n in names) and (x / "_speed.json").is_file(),
          "apply 1.10 → media/x110 đủ file + _speed.json", (r.stderr or r.stdout)[-300:])
    a = x / "01_a-roll-1.mp4"
    check(abs(dur(a) - dur(src / "01_a-roll-1.mp4") / 1.1) <= 1 / 30 and probe(a, "stream=r_frame_rate", "v:0") == "30/1"
          and probe(a, "stream=width,height", "v:0") == "108,192", "A-roll: độ dài = gốc / 1.1, 30 fps, giữ kích thước", probe(a, "stream=r_frame_rate", "v:0"))
    check(probe(x / "02_b-roll-1.mp4", "stream=codec_type", "a") == "", "B-roll sau tăng tốc không có luồng tiếng (D2)")
    r = tool("speed_media.py", "check", src, "--manifest", manifest, "--out", out)
    check(r.returncode == 0, "check: 0 lỗi", (r.stdout + r.stderr)[-400:])
    sh(["ffmpeg", "-v", "error", "-y", "-i", src / "02_b-roll-1.mp4", "-c", "copy", x / "02_b-roll-1.mp4"])   # hỏng: để nguyên tốc độ gốc
    r = tool("speed_media.py", "check", src, "--manifest", manifest, "--out", out)
    check(r.returncode == 1, "check: file sai độ dài → thoát 1", (r.stdout + r.stderr)[-300:])

    out2 = tmp / "media1"
    r = tool("speed_media.py", "apply", src, "--manifest", manifest, "--speed", "1.0", "--out", out2)
    check(r.returncode == 0 and "dùng thư mục gốc" in r.stdout and not out2.exists(), "apply 1.0 → không ghi gì, báo dùng thư mục gốc", r.stdout[-200:])
    r = tool("speed_media.py", "apply", src, "--manifest", manifest, "--speed", "1.25", "--out", out2)
    check(r.returncode != 0 and not out2.exists(), "apply 1.25 bị chặn")


def test_matte(tmp: Path) -> None:
    rvm = Path.home() / ".local/bin/rvm-matte"
    if not rvm.is_file() or not (Path.home() / ".local/share/video-ai/RobustVideoMatting").is_dir():
        print("[BỎ QUA] matte --start/--dur: chưa cài rvm-matte")
        return
    src = tmp / "m_src.mp4"
    sh(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=216x384:r=30:d=5", "-c:v", "libx264", "-pix_fmt", "yuv420p", src])
    r = tool("matte.py", "--input", src, "--output", tmp / "m.mov", "--start", "1", "--dur", "2")
    ok = r.returncode == 0 and (tmp / "m.mov").is_file() and abs(dur(tmp / "m.mov") - 2.0) <= 0.1
    check(ok, "matte.py --start 1 --dur 2 → 2 s", (r.stderr or r.stdout)[-300:])


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as t:
        test_choose_speed()
        test_pipeline(Path(t))
        test_matte(Path(t))
    if fails:
        print(f"\nCÓ {len(fails)} LỖI: {', '.join(fails)}")
        sys.exit(1)
    print("\nTẤT CẢ ĐẠT")
