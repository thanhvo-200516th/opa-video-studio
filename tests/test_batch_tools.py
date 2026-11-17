#!/usr/bin/env python3
"""rotation / contact_sheet / batch_report. Chạy: ~/.venvs/video-skills/bin/python tests/test_batch_tools.py"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import batch_report  # noqa: E402
import contact_sheet  # noqa: E402
import rotation  # noqa: E402


def test_rotation(d: Path) -> None:
    names = [f"KB{i:02d}" for i in range(6, 36)]
    led = rotation.plan(d, names)
    assert len(led["videos"]) == 30 and not rotation.check(led), rotation.check(led)
    again = rotation.plan(d, names)                         # chạy lại không đổi ô đã cấp
    assert [v["key_seed"] for v in again["videos"]] == [v["key_seed"] for v in led["videos"]]
    v = rotation.entry(d / "Danh_Sach" / "KB10_x", "KB10")  # tìm sổ ở thư mục cha
    assert v and v["video"] == "KB10"
    assert rotation.key_kinds(v["key_seed"]) == v["key_kinds"]
    bad = {"window": 5, "videos": [dict(led["videos"][0]), dict(led["videos"][1], opening_pair=led["videos"][0]["opening_pair"])]}
    assert any("cặp SFX mở đầu" in b for b in rotation.check(bad))
    print("ok  rotation: 30 video không lặp trong 5 · chạy lại giữ nguyên · bắt được lặp")


def test_contact() -> None:
    clips = [{"at": round(t, 2), "dur": 1.0} for t in [0.0, 0.1, 2.0, 2.2, 4.0] + [5 + i * 0.5 for i in range(40)]]
    spec = {"duration": 30.0, "tracks": [{"type": "video", "clips": clips}]}
    ts = contact_sheet.plan_times(spec)
    times = [t for t, _ in ts]
    assert times[0] == 0.0 and ts[-1][1] == "cuối" and len(ts) <= contact_sheet.MAX_FRAMES
    assert all(b - a >= contact_sheet.MERGE - 1e-9 for a, b in zip(times, times[1:]))
    assert any(lab.startswith("hook") for _, lab in ts)
    print(f"ok  contact_sheet: {len(ts)} khung · cách nhau ≥ {contact_sheet.MERGE} s · có mở đầu / hook / cuối")


def test_report(d: Path) -> None:
    b = d / "lo"
    for name, qa, build in (("KB01_ok", "I = -15.1 LUFS · LRA = 1 LU · True Peak = -2.2 dBTP", True),
                            ("KB02_to", "I = -12.0 LUFS · LRA = 1 LU · True Peak = -2.2 dBTP", True),
                            ("KB03_lint", "I = -15.0 LUFS · LRA = 1 LU · True Peak = -2.0 dBTP", True)):
        (b / name / "work").mkdir(parents=True)
        t = {"build_ok": build, "qa_audio": qa, "qa_sfx": "→ ĐẠT ✅", "lint_soft": ["dead_air: 3.1s"] if "lint" in name else [],
             "audit_loi": [], "duration_video": 40, "toc_do": 1.25, "tong_giay": 70}
        (b / name / "work/timing_v2.15.4.json").write_text(json.dumps(t, ensure_ascii=False))
    (b / "KB04_gate" / "work").mkdir(parents=True)
    rows = [{"video": "KB04_gate", "stage": "build_spec", "status": "ok", "secs": 1, "fail_code": ""},
            {"video": "KB04_gate", "stage": "gate", "status": "fail", "secs": 0, "fail_code": "keys_not_increasing"}]
    (b / "batch.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    _, res = batch_report.report(b)
    got = {r["video"]: r["status"] for r in res}
    assert got == {"KB01_ok": "PASS", "KB02_to": "HOLD", "KB03_lint": "WARN", "KB04_gate": "HOLD"}, got
    print("ok  batch_report: PASS / HOLD (LUFS −12) / WARN (lint) / HOLD (cổng chặn)")


def test_report_reuse(d: Path) -> None:
    import subprocess
    import media_reuse as mr

    b = d / "lo_reuse"
    clip = d / "shared_broll.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "mandelbrot=s=108x192:r=30", "-t", "1",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(clip)], check=True)
    for name in ("KB01_a", "KB02_b", "KB03_c"):
        (b / name / "work").mkdir(parents=True)
        t = {"build_ok": True, "qa_audio": "I = -15.0 LUFS · LRA = 1 LU · True Peak = -2.0 dBTP", "qa_sfx": "→ ĐẠT ✅",
             "lint_soft": [], "audit_loi": [], "duration_video": 40, "toc_do": 1.1, "tong_giay": 40}
        (b / name / "work/timing_v2.15.4.json").write_text(json.dumps(t, ensure_ascii=False))
        # KB01_a: 2 lần (đạt); KB02_b: 1 lần (đạt); KB03_c: 3 lần (vượt MAX_PER_VIDEO=2) + cả 3 video dùng cùng clip (>2 video)
        ats = [0, 3] if name == "KB01_a" else ([0] if name == "KB02_b" else [0, 3, 6])
        spec = {"tracks": [{"type": "video", "name": "V1", "clips": [{"src": str(clip), "at": x, "dur": 1, "name": "B-roll 1"} for x in ats]}]}
        (b / name / f"work/{name.lower()}.craft.json").write_text(json.dumps(spec))
    old_lib, old_raw = list(mr.LIB_DIRS), mr.SOURCE_RAW
    mr.LIB_DIRS[:] = []
    mr.SOURCE_RAW = d / "_no_raw"
    mr.fingerprint.cache_clear()
    try:
        md, res = batch_report.report(b, [b])
    finally:
        mr.LIB_DIRS[:] = old_lib
        mr.SOURCE_RAW = old_raw
    got = {r["video"]: r["status"] for r in res}
    assert all(st == "WARN" for st in got.values()), (got, md)
    assert any("D8:" in w and "3 lần" in w for r in res if r["video"] == "KB03_c" for w in r["why"]), res
    print("ok  batch_report + media_reuse D8: > 2/video hoặc > 2 video → WARN (không HOLD)")


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        test_rotation(d)
        test_contact()
        test_report(d)
        test_report_reuse(d)
    print("TẤT CẢ ĐẠT")


if __name__ == "__main__":
    main()
