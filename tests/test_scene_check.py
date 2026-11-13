#!/usr/bin/env python3
"""Kiểm scene_check bắt đúng D14 (hình–tiếng cùng cảnh) và D9 (bám kịch bản). Chạy: ~/.venvs/video-skills/bin/python tests/test_scene_check.py"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scene_check import run_checks, stem  # noqa: E402

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "scene_check.py"
TTS = ["Ngày trước mình ôm hết mọi việc vào người", "Những cú ngã dạy mình một sự thật phũ phàng", "Nên mình dựng hệ thống đội ngũ chuyên trách"]


def seg(i: int, typ: str, tts: str, prompt: str | None = "cảnh minh hoạ") -> dict:
    role = f"{typ}-{i}"
    return {"seq_index": i, "type": typ, "role_id": role, "display_text": tts, "tts_text": tts,
            "broll_prompt": prompt if typ == "b-roll" else None,
            "files": {"video_file": f"{i:02d}_{role}.mp4", "voice_file": f"{i:02d}_voice-{role}.mp3" if typ == "b-roll" else None}}


def vclip(name: str, at: float, dur: float, speed: str = "x115") -> dict:
    return {"src": f"/m/{speed}/{name}", "at": at, "in": 0.0, "dur": dur, "audio": False}


def aclip(name: str, at: float, dur: float) -> dict:
    return {"src": f"/m/x115/{name}", "at": at, "in": 0.0, "dur": dur}


def good() -> tuple[dict, dict]:
    manifest = {"segments": [seg(1, "a-roll", TTS[0]), seg(2, "b-roll", TTS[1]), seg(3, "b-roll", TTS[2])]}
    spec = {"tracks": [
        {"type": "video", "name": "V1", "clips": [vclip("01_a-roll-1.mp4", 0, 5), vclip("02_b-roll-2.mp4", 5, 6),
                                                   vclip("03_b-roll-3.mp4", 11, 4)]},
        {"type": "video", "name": "V2 Người tách nền (Track Matte)", "clips": [vclip("person_alpha_hook_x115.mov", 0, 2.5)]},
        {"type": "video", "name": "gfx", "clips": [{"src": "/m/gfx/kw_3.png", "at": 0.2, "dur": 2.3}]},
        {"type": "text", "name": "text 1", "clips": [{"text": "HOOK", "at": 0, "dur": 1}]},
        {"type": "audio", "name": "A1 Giọng", "clips": [aclip("02_voice-b-roll-2.mp3", 5, 6), aclip("03_voice-b-roll-3.mp3", 11, 4)]},
    ]}
    return manifest, spec


def status(items: list[dict], cid: str) -> str:
    return next(r["status"] for r in items if r["id"] == cid)


def detail(items: list[dict], cid: str) -> str:
    return next(r["value"] for r in items if r["id"] == cid)


def write_transcript(d: Path, name: str, text: str) -> None:
    (d / f"{name}.json").write_text(json.dumps({"text": text, "words": [{"text": w, "type": "word"} for w in text.split()]}), encoding="utf-8")


def timeline_words(lines: list[tuple[float, str]]) -> list[list]:
    """[[chữ, t0, t1], …] giả lập: mỗi chữ 0,3 s, bắt đầu từ mốc của từng câu."""
    return [[w, t0 + 0.3 * i, t0 + 0.3 * i + 0.25] for t0, line in lines for i, w in enumerate(line.split())]


def main() -> None:
    assert stem("/a/x125/02_b-roll-1_x115.mp4") == "02_b-roll-1" and stem("x115/02_b-roll-1.mp4") == "02_b-roll-1"

    manifest, spec = good()
    items, review = run_checks(manifest, spec)
    assert [status(items, c) for c in ("av_sync", "order", "script", "cutaway")] == ["OK"] * 4, items
    assert "| 2 | b-roll |" in review
    print("ok  pass case                  → av_sync/order/script OK")

    m, s = copy.deepcopy(manifest), copy.deepcopy(spec)
    s["tracks"][-1]["clips"][0]["at"] = 5.5   # tiếng cảnh 2 muộn 0,5 s so với hình
    items, _ = run_checks(m, s)
    assert status(items, "av_sync") == "FAIL" and "lệch" in detail(items, "av_sync")
    print("ok  voice offset > tol         → FAIL")

    m, s = copy.deepcopy(manifest), copy.deepcopy(spec)
    s["tracks"][0]["clips"][1] = vclip("02_b-roll-2.mp4", 5, 2)             # hình cảnh 2 chỉ 2 s
    s["tracks"][0]["clips"].insert(2, vclip("03_b-roll-3.mp4", 7, 4))       # hình cảnh 3 chiếm lúc tiếng cảnh 2 đọc
    items, _ = run_checks(m, s)
    assert status(items, "av_sync") == "FAIL" and "03_b-roll-3" in detail(items, "av_sync")
    print("ok  other scene's picture      → FAIL")

    m, s = copy.deepcopy(manifest), copy.deepcopy(spec)
    s["tracks"][0]["clips"][1] = vclip("02_b-roll-2.mp4", 5.3, 5.7)         # hình cảnh 1 kéo dài 0,3 s sang lúc cảnh 2 đọc
    s["tracks"][0]["clips"][0] = vclip("01_a-roll-1.mp4", 0, 5.3)
    items, _ = run_checks(m, s)
    assert status(items, "av_sync") == "FAIL" and "lệch" in detail(items, "av_sync")   # chỉ lệch đầu hình–tiếng 0,3 s > tol
    s["tracks"][0]["clips"][1] = vclip("02_b-roll-2.mp4", 5.0, 6)
    s["tracks"][0]["clips"][0] = vclip("01_a-roll-1.mp4", 0, 5.3)           # A-roll nằm dưới b-roll: topmost vẫn là cảnh 2
    items, _ = run_checks(m, s)
    assert status(items, "av_sync") == "OK", detail(items, "av_sync")
    print("ok  short transition           → OK")

    m, s = copy.deepcopy(manifest), copy.deepcopy(spec)
    s["tracks"][-1]["clips"] = [aclip("03_voice-b-roll-3.mp3", 5, 4), aclip("02_voice-b-roll-2.mp3", 11, 6)]
    s["tracks"][0]["clips"] = [vclip("01_a-roll-1.mp4", 0, 5), vclip("03_b-roll-3.mp4", 5, 4), vclip("02_b-roll-2.mp4", 11, 6)]
    items, _ = run_checks(m, s)
    assert status(items, "order") == "FAIL" and status(items, "av_sync") == "OK"
    print("ok  out-of-order               → order FAIL")

    m, s = copy.deepcopy(manifest), copy.deepcopy(spec)
    m["segments"][1]["broll_prompt"] = "  "
    items, _ = run_checks(m, s)
    assert status(items, "script") == "FAIL" and "broll_prompt" in detail(items, "script")
    print("ok  empty prompt               → FAIL")

    m, s = copy.deepcopy(manifest), copy.deepcopy(spec)
    del s["tracks"][-1]["clips"][1]            # thiếu clip tiếng cảnh 3
    items, _ = run_checks(m, s)
    assert status(items, "av_sync") == "FAIL" and "thiếu" in detail(items, "av_sync")
    print("ok  missing voice clip         → FAIL")

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        for i, t in enumerate(TTS[1:], start=2):
            write_transcript(d, f"{i:02d}_voice-b-roll-{i}", t)
        write_transcript(d, "01_a-roll-1", TTS[0])
        items, _ = run_checks(manifest, spec, d)
        assert status(items, "script") == "OK", detail(items, "script")
        write_transcript(d, "03_voice-b-roll-3", "hoàn toàn khác biệt nội dung được đọc lên ở đây")
        items, _ = run_checks(manifest, spec, d)
        assert status(items, "script") == "FAIL" and "cảnh 3" in detail(items, "script")
        print("ok  transcript mismatch        → FAIL")

        m, s = copy.deepcopy(manifest), copy.deepcopy(spec)
        s["tracks"][0]["clips"].append({"src": "/other/Thu_vien/KB07_Go_May.mp4", "at": 7, "dur": 2, "audio": False})
        s["tracks"].insert(1, {"type": "video", "name": "V1b chèn", "clips": [{"src": "/other/Thu_vien/KB07_Go_May.mp4", "at": 7, "dur": 2}]})
        items, review = run_checks(m, s)
        assert status(items, "av_sync") == "OK" and status(items, "cutaway") == "WARN"
        assert "KB07_Go_May" in detail(items, "cutaway") and "**chèn** KB07_Go_May" in review
        print("ok  unmapped cutaway allowed   → av_sync OK, cutaway WARN")

        mp, sp, out = d / "m.json", d / "s.craft.json", d / "r.md"
        mp.write_text(json.dumps(manifest), encoding="utf-8")
        sp.write_text(json.dumps(spec), encoding="utf-8")
        r = subprocess.run([sys.executable, str(SCRIPT), "--manifest", str(mp), "--spec", str(sp), "--review", str(out)],
                           capture_output=True, text=True)
        assert r.returncode == 0 and out.is_file(), r.stdout + r.stderr
        bad = copy.deepcopy(spec)
        bad["tracks"][-1]["clips"][0]["at"] = 6.0
        sp.write_text(json.dumps(bad), encoding="utf-8")
        r = subprocess.run([sys.executable, str(SCRIPT), "--manifest", str(mp), "--spec", str(sp)], capture_output=True, text=True)
        assert r.returncode == 1 and "FAIL" in r.stdout, r.stdout + r.stderr
        print("ok  CLI exit codes             → 0 / 1")

    # --words: giọng gộp (voice_sNN.wav) → suy khoảng đọc bằng gióng tts_text lên words theo giờ timeline
    merged = copy.deepcopy(spec)
    merged["tracks"][-1]["clips"] = [{"src": f"/m/voice/voice_s0{i}.wav", "at": a0, "dur": d} for i, (a0, d) in enumerate([(0, 5), (5, 6), (11, 4)])]
    items, _ = run_checks(manifest, merged)
    assert status(items, "av_sync") == "FAIL" and "thiếu clip tiếng" in detail(items, "av_sync")
    words = timeline_words([(0.0, TTS[0]), (5.0, TTS[1]), (11.0, TTS[2])])
    words.insert(3, ["ừ", 0.9, 1.0])            # chữ thừa do ASR
    words[12] = ["dậy", *words[12][1:]]          # chữ sai do ASR
    items, review = run_checks(manifest, merged, words=words)
    assert [status(items, c) for c in ("av_sync", "order")] == ["OK", "OK"], detail(items, "av_sync")
    assert "5.00–" in review and "(words)" in review
    shifted = copy.deepcopy(merged)
    shifted["tracks"][0]["clips"][1:] = [vclip("02_b-roll-2.mp4", 5.8, 5.2), vclip("03_b-roll-3.mp4", 11, 4)]   # hình trễ 0,8 s so với giọng
    shifted["tracks"][0]["clips"].insert(1, vclip("01_a-roll-1.mp4", 5, 0.8))
    items, _ = run_checks(manifest, shifted, words=words)
    assert status(items, "av_sync") == "FAIL" and "cảnh 2" in detail(items, "av_sync")
    print("ok  --words merged voice       → pass + misaligned FAIL")

    # D9: cảnh thư viện của kịch bản khác (lỗi cũ OPA01–05 dùng cảnh KB01–KB10) = FAIL; cảnh của chính kịch bản = OK
    m, sp = good()
    m["script_id"] = "OPA05"
    m["segments"][1]["broll_prompt"] = "Clip thư viện: KB07_B02_21s-30s_Kho_Broll.mp4 (Pure visual)"
    items, _ = run_checks(m, sp)
    assert status(items, "script_source") == "FAIL" and "cảnh 2" in detail(items, "script_source"), items
    m["segments"][1]["broll_prompt"] = "Clip thư viện: OPA05_B02_Kho.mp4"
    items, _ = run_checks(m, sp)
    assert status(items, "script_source") == "OK", items
    print("ok  cảnh của kịch bản khác      → FAIL (D9)")

    # C1 (v2.5): script_source nêu danh sách cảnh sai; broll_h5 FAIL khi prompt rỗng / "Clip thư viện", WARN khi chưa đạt lint H5
    m, sp = good()
    m["script_id"] = "OPA05"
    m["segments"][1]["broll_prompt"] = "Clip thư viện: KB07_B02_Kho.mp4 (Pure visual)"
    m["segments"][2]["broll_prompt"] = "Clip thư viện: KB09_B03_Do_Hoa.mp4 (Pure visual)"
    items, _ = run_checks(m, sp)
    src = next(r for r in items if r["id"] == "script_source")
    assert src["status"] == "FAIL" and src["scenes"] == [2, 3], src
    h5 = next(r for r in items if r["id"] == "broll_h5")
    assert h5["status"] == "FAIL" and h5["scenes"] == [2, 3], h5
    m["segments"][1]["broll_prompt"] = "Slow push-in on a young Vietnamese engineering team in a bright modern office, colleagues leaning in around a desk. Warm daylight (Pure visual footage/motion only, NO text)"
    m["segments"][2]["broll_prompt"] = "cảnh minh hoạ"
    items, _ = run_checks(m, sp)
    h5 = next(r for r in items if r["id"] == "broll_h5")
    assert h5["status"] == "WARN" and h5["scenes"] == [3], h5          # tiếng Việt → chỉ WARN
    m["segments"][2]["broll_prompt"] = "Medium shot of a relaxed Vietnamese business owner shaking hands with the founder in a bright meeting room. Warm daylight"
    items, _ = run_checks(m, sp)
    assert status(items, "broll_h5") == "OK" and status(items, "script_source") == "OK", items
    with tempfile.TemporaryDirectory() as td:
        mp, sj, oj = Path(td) / "m.json", Path(td) / "s.json", Path(td) / "o.json"
        m["segments"][1]["broll_prompt"] = "Clip thư viện: KB07_B02_Kho.mp4"
        mp.write_text(json.dumps(m), encoding="utf-8")
        sj.write_text(json.dumps(sp), encoding="utf-8")
        r = subprocess.run([sys.executable, str(SCRIPT), "--manifest", str(mp), "--spec", str(sj), "--json", str(oj)], capture_output=True, text=True)
        out = json.loads(oj.read_text(encoding="utf-8"))
        assert r.returncode == 1 and next(x for x in out if x["id"] == "script_source")["scenes"] == [2], r.stdout
    print("ok  broll_h5 + scenes[] trong JSON → FAIL/WARN/OK")

    print("TẤT CẢ ĐẠT")


if __name__ == "__main__":
    main()
