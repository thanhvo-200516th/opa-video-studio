#!/usr/bin/env python3
"""Kiểm lib_extract: segments (cắt cảnh + lời), entry (still/strip/clip/entry.json/notes.md + index), index (kiểm hợp lệ)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "style_analysis"))
import lib_extract as le  # noqa: E402

FF = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
assert FF, "cần ffmpeg"


def make_video(path: Path) -> None:
    """2 s, 30 fps, 320x240: 1 s đầu nền đỏ có ô trắng chạy ngang, 1 s sau nền xanh tĩnh. Có âm thanh để thử bỏ tiếng."""
    subprocess.run([FF, "-v", "error", "-y",
                    "-f", "lavfi", "-i", "color=c=red:s=320x240:r=30:d=1",
                    "-f", "lavfi", "-i", "color=c=white:s=40x40:r=30:d=1",
                    "-f", "lavfi", "-i", "color=c=blue:s=320x240:r=30:d=1",
                    "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
                    "-filter_complex", "[0:v][1:v]overlay=x='t*200':y=100[a];[a][2:v]concat=n=2:v=1:a=0[v]", "-map", "[v]", "-map", "3:a",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(path)], check=True)


with tempfile.TemporaryDirectory() as td:
    w = Path(td)
    vid = w / "ref.mp4"
    make_video(vid)

    # --- segments: cắt tại ~1,0 s, lời gắn vào đúng đoạn
    tr = w / "tr.json"
    tr.write_text(json.dumps({"words": [
        {"text": "xin", "start": 0.1, "end": 0.3, "type": "word"}, {"text": " ", "start": 0.3, "end": 0.35, "type": "spacing"},
        {"text": "chào", "start": 0.35, "end": 0.6, "type": "word"}, {"text": "tạm", "start": 1.2, "end": 1.4, "type": "word"}]}))
    out = w / "seg"
    segs = le.segments(vid, out, transcript=tr)
    assert len(segs) == 2, segs
    assert abs(segs[0]["t"][1] - 1.0) < 0.1, segs
    assert segs[0]["words"] == "xin chào" and segs[1]["words"] == "tạm", segs
    assert (out / "segments.json").is_file() and (out / "segments.md").is_file()
    # định dạng danh sách đoạn (transcript.json kiểu Whisper cũ) cũng đọc được
    tr2 = w / "tr2.json"
    tr2.write_text(json.dumps([{"start": 0.0, "end": 0.9, "text": "một hai"}, {"start": 1.1, "end": 1.9, "text": "ba"}]))
    assert [s["words"] for s in le.segments(vid, w / "seg2", transcript=tr2)] == ["một hai", "ba"]

    # --- entry
    root = w / "lib"
    e = le.entry(vid, "V01-A01", 0.0, 1.0, "text_motion", "Ô trắng chạy ngang", root, "minimal-edu",
                 principle=1, source={"video": "ref.mp4", "url": "http://x", "author": "tester"}, notes="Mô tả thử.", rebuild="Dùng text_fx")
    d = root / "minimal-edu" / "V01-A01"
    for f in ("still.png", "strip.jpg", "clip.mp4", "entry.json", "notes.md"):
        assert (d / f).is_file(), f
    m = e["measures"]
    assert m["frames"] == 30 and m["fps"] == 30 and m["duration_ms"] == 1000, m
    assert m["motion_bbox_px"][2] > 100 and m["motion_bbox_px"][3] < 120, m          # ô trắng chạy ngang: bbox rộng, thấp
    assert m["dominant_colors"] and m["dominant_colors"][0].startswith("#"), m
    probe = subprocess.run([shutil.which("ffprobe") or "ffprobe", "-v", "error", "-show_entries", "stream=codec_type:format=duration",
                            "-of", "json", str(d / "clip.mp4")], capture_output=True, text=True, check=True).stdout
    pj = json.loads(probe)
    assert [s["codec_type"] for s in pj["streams"]] == ["video"] and float(pj["format"]["duration"]) <= 3.05, pj
    notes = (d / "notes.md").read_text(encoding="utf-8")
    assert "Mô tả thử." in notes and "text_fx" in notes and "30" in notes, notes
    idx = json.loads((root / "minimal-edu" / "index.json").read_text())
    assert idx["style"] == "minimal-edu" and [x["id"] for x in idx["entries"]] == ["V01-A01"]
    assert idx["entries"][0]["still"] == "V01-A01/still.png" and idx["entries"][0]["principle"] == 1

    # entry dài hơn 3 s: clip bị cắt ≤ 3 s; crop áp dụng cho still/clip
    e2 = le.entry(vid, "V01-A02", 1.0, 2.0, "transition", "Cắt cứng đỏ-xanh", root, "minimal-edu", crop=(0, 0, 160, 120))
    assert e2["measures"]["crop"] == [0, 0, 160, 120]
    from PIL import Image
    assert Image.open(root / "minimal-edu" / "V01-A02" / "still.png").size == (160, 120)

    # --- index: hợp lệ
    ok, errs = le.index(root, "minimal-edu")
    assert ok == 2 and not errs, (ok, errs)
    # thiếu file / kind sai → lỗi, không nuốt
    (root / "minimal-edu" / "V01-A02" / "strip.jpg").unlink()
    ok, errs = le.index(root, "minimal-edu")
    assert ok == 1 and any("strip.jpg" in x for x in errs), (ok, errs)
    # CLI trả mã thoát khác 0 khi có lỗi
    r = subprocess.run([sys.executable, str(Path(le.__file__)), "index", "--root", str(root), "--style", "minimal-edu"],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "strip.jpg" in (r.stdout + r.stderr)
    for bad in ("nope",):
        try:
            le.entry(vid, "V01-A09", 0, 1, bad, "x", root, "minimal-edu")
            raise AssertionError("kind sai phải bị từ chối")
        except SystemExit:
            pass

# không còn đường dẫn ffmpeg cứng trong style_analysis
for f in (Path(le.__file__).parent).glob("*"):
    if f.suffix in (".py", ".sh"):
        assert "/home/vmiz/.local/bin" not in f.read_text(encoding="utf-8"), f
print("TẤT CẢ ĐẠT")
