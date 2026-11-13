#!/usr/bin/env python3
"""v2.8 qa_sync mọi nhịp: chữ vào (đo từ keyframe vào), punch nỗi đau, SFX mở đầu + sfx_shift áp mọi loại. Không mở FilmCraft.
Chạy: ~/.venvs/video-skills/bin/python tests/test_qa_beats.py"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
import qa_sync  # noqa: E402
import sfx_shift  # noqa: E402

fails: list[str] = []
FPS = 30.0


def check(ok: bool, label: str, detail: str = "") -> None:
    print(f"[{'OK' if ok else 'LỖI'}] {label}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        fails.append(label)


def make_wav(path: Path, burst_at: float, dur: float = 1.5, burst: float = 0.01) -> None:
    """WAV 48 kHz: nền rất nhỏ, một cú nổ ngắn tại burst_at (đỉnh ≈ đầu cú nổ)."""
    t = np.arange(int(dur * 48000)) / 48000
    x = 0.001 * np.sin(2 * np.pi * 300 * t)
    m = (t >= burst_at) & (t < burst_at + burst)
    x[m] = 0.8 * np.sin(2 * np.pi * 800 * t[m])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", "48000", "-ac", "1", "-i", "-", str(path)],
                   input=(x * 32767).astype(np.int16).tobytes(), check=True)


def sfx(d: Path, name: str, at: float, burst_at: float, label: str) -> dict:
    """Clip SFX có đỉnh tại at + burst_at."""
    w = d / f"{label}.wav"
    make_wav(w, burst_at)
    return {"src": str(w), "at": at, "in": 0.0, "dur": 1.0, "name": name}


def make_spec(d: Path) -> dict:
    v1 = {"type": "video", "name": "V1", "clips": [
        {"at": 0.0, "dur": 10.0, "src": "a", "name": "A-roll"},
        # punch 1: phóng 103 → 118 trong [10.40, 10.55] (giữa 10.475); punch 2 [11.0, 11.15] không có SFX; zoom chậm 100 → 110 trong 3 s
        {"at": 10.0, "dur": 4.0, "src": "b", "name": "B-roll",
         "motion": {"scale": [[0, 100], [0.4, 103], [0.55, 118], [0.99, 105], [1.15, 118], [3.9, 110]]}},
        {"at": 14.0, "dur": 4.0, "src": "c", "name": "Zoom chậm", "motion": {"scale": [[0, 100], [3.0, 110]]}}]}
    text = {"type": "text", "name": "text 1", "clips": [
        {"text": "kinh doanh hay", "at": 2.0, "dur": 1.0, "name": "Chữ · kinh doanh hay #1"},            # phụ đề cùng chữ, mốc 2,0
        {"text": "Gõ thử", "at": 6.0, "dur": 1.0, "name": "Chữ · Gõ thử #2",
         "effects": [{"effect": "crop", "params": {"right": [[0.0, 100.0, "hold"], [0.1, 60.0, "hold"], [0.3, 0.0]]}}]}]}
    img = {"type": "video", "name": "text_img 1", "clips": [
        {"at": 2.2, "dur": 1.0, "src": "k1", "name": "Từ khoá · KINH DOANH #3", "opacity": [[0, 0], [0.08, 100]]},
        {"at": 4.0, "dur": 1.0, "src": "k2", "name": "Từ khoá · ÔM HẾT #4"}]}
    ev = [
        sfx(d, "SFX MỞ ĐẦU · tốt", 0.0, 0.0, "open1"),
        sfx(d, "SFX key_hit · từ khoá «KINH DOANH»", 2.0, 0.25, "k1"),   # đỉnh 2,25: chữ khoá hiện 2,2 → +0,05 ĐẠT (caption 2,0 không được chọn)
        sfx(d, "SFX key_hit · từ khoá «ÔM HẾT»", 3.6, 0.1, "k2"),         # đỉnh 3,7: chữ hiện 4,0 → −0,3 sớm → LỆCH + CHẶN, dời +0,34
        sfx(d, "SFX pen · nét bút «Gõ thử»", 6.0, 0.25, "pen"),          # chữ nhìn thấy từ 6,1 (crop hold) → tiếng bắt đầu ≈ 6,25: +0,15 muộn → LỆCH
        sfx(d, "SFX key_hit · nhấn nỗi đau «chạm trần»", 10.0, 0.5, "pain"),  # đỉnh 10,5 gần giữa 10,475 → ĐẠT
        sfx(d, "SFX whoosh · chuyển cảnh zoom", 9.8, 0.2, "wh"),          # chuyển cảnh: không vào nhịp chữ
        sfx(d, "SFX key_hit · từ khoá «KHÔNG CÓ CHỮ NÀY»", 8.0, 0.0, "orph")]
    return {"name": "t", "duration": 20.0, "fps": 30, "tracks": [v1, text, img,
                                                                    {"type": "audio", "name": "A2 SFX (mở đầu)", "clips": ev}]}


def test_classify_and_visible() -> None:
    cases = {"SFX MỞ ĐẦU · x": "open", "SFX key_hit · nhấn nỗi đau «chạm trầ": "pain", "SFX key_hit · từ khoá «A»": "text",
             "SFX pen · nét bút «x»": "text", "SFX word_click · từ «x»": "text", "SFX whoosh · chuyển cảnh zoom": "cut",
             "SFX tiếng có sẵn của film_burn": "cut", "SFX leak · chuyển cảnh light_swee": "cut", "SFX shutter · lớp": "cut"}
    check(all(qa_sync.beat_of(k) == v for k, v in cases.items()), "beat_of phân loại tên SFX",
          str({k: qa_sync.beat_of(k) for k in cases}))
    check(qa_sync.visible_start({"opacity": [[0, 0], [0.12, 100]]}) == 0.0, "visible_start: opacity dốc từ 0 → bắt đầu tại keyframe 0")
    check(qa_sync.visible_start({"opacity": [[0, 0, "hold"], [0.2, 100]]}) == 0.2, "visible_start: opacity hold 0 → hiện ở keyframe sau")
    check(qa_sync.visible_start({"opacity": [[0, 40], [0.1, 100]]}) == 0.0, "visible_start: opacity đầu > 0 → 0")
    c = {"effects": [{"effect": "crop", "params": {"right": [[0.0, 100.0, "hold"], [0.0667, 75.0, "hold"], [0.3, 0.0]]}}]}
    check(abs(qa_sync.visible_start(c) - 0.0667) < 1e-9, "visible_start: crop phải 100 hold → hiện ở keyframe đầu tiên < 100")
    c["opacity"] = [[0, 0], [0.5, 100]]
    check(abs(qa_sync.visible_start(c) - 0.0667) < 1e-9, "visible_start: lấy muộn nhất của opacity và crop")


def test_punch_and_layers(d: Path) -> None:
    spec = make_spec(d)
    pb = qa_sync.punch_beats(spec)
    check(len(pb) == 2 and abs(pb[0]["t0"] - 10.4) < 1e-6 and abs(pb[0]["t1"] - 10.55) < 1e-6,
          "punch_beats: 2 cú phóng, bỏ zoom chậm 3 s", str(pb))
    lay = {l["clip"]: l for l in qa_sync.text_layers(spec)}
    check(abs(lay["Từ khoá · KINH DOANH #3"]["t_vis"] - 2.2) < 1e-9 and abs(lay["Chữ · Gõ thử #2"]["t_vis"] - 6.1) < 1e-6,
          "text_layers: mốc khung đầu tiên nhìn thấy", str({k: v["t_vis"] for k, v in lay.items()}))


def test_measure_beats(d: Path) -> None:
    spec = make_spec(d)
    rows = qa_sync.measure_beats(spec, FPS)
    by = {(r["event"] or {}).get("name", r["clip"]): r for r in rows}
    check({r["beat"] for r in rows} == {"open", "text", "punch"}, "measure_beats: mở đầu / chữ / punch, không có chuyển cảnh")
    o = by["SFX MỞ ĐẦU · tốt"]
    check(o["status"] == "ĐẠT", "mở đầu: tiếng bắt đầu ở khung 0 → ĐẠT", str(o["audio"]))
    k1 = by["SFX key_hit · từ khoá «KINH DOANH»"]
    check(k1["clip"].startswith("Từ khoá") and k1["status"] == "ĐẠT", "key_hit gắn lớp « Từ khoá », không gắn phụ đề cùng chữ; đỉnh +0,05 → ĐẠT",
          f"{k1['clip']} {k1['status']} d={k1['d']}")
    k2 = by["SFX key_hit · từ khoá «ÔM HẾT»"]
    check(k2["status"] == "LỆCH" and k2["block"] and 0.30 <= k2["shift"] <= 0.38,
          "key_hit sớm hơn chữ 0,3 s → LỆCH + CHẶN, dời ≈ +0,34", str((k2["status"], k2["block"], k2["shift"], k2["d"])))
    pen = by["SFX pen · nét bút «Gõ thử»"]
    check(pen["status"] == "LỆCH" and not pen["block"] and abs(pen["ref"] - 6.1) < 1e-6 and -0.2 <= pen["shift"] <= -0.08,
          "pen đo lúc bắt đầu tiếng, mốc chữ = keyframe crop đầu tiên; muộn 0,15 s → LỆCH, KHÔNG chặn, dời ≈ −0,11",
          str((pen["status"], pen["ref"], pen["shift"], pen["d"])))
    orph = by["SFX key_hit · từ khoá «KHÔNG CÓ CHỮ NÀY»"]
    check(orph["status"] == "KHÔNG MỐC" and orph["ok"] and orph["shift"] is None, "SFX chữ không có lớp chữ → KHÔNG MỐC, không phải LỆCH")
    pain = by["SFX key_hit · nhấn nỗi đau «chạm trần»"]
    check(pain["status"] == "ĐẠT" and abs(pain["ref"] - 10.475) < 1e-6, "nhấn nỗi đau: đỉnh ở giữa đoạn phóng → ĐẠT", str((pain["status"], pain["ref"], pain["d"])))
    nosfx = [r for r in rows if r["beat"] == "punch" and r["event"] is None]
    check(len(nosfx) == 1 and nosfx[0]["status"] == "KHÔNG SFX" and nosfx[0]["ok"], "punch thứ hai không SFX → KHÔNG SFX (không lỗi)")
    # tiếng muộn so với punch: đỉnh 10,60 (giữa 10,475) → LỆCH, dời ≈ −0,125, không chặn
    late = qa_sync.judge_punch(10.4, 10.55, {"a_peak": 10.60, "a_start": 10.59, "level": -6}, FPS)
    check(late["status"] == "LỆCH" and not late["block"] and abs(late["shift"] + 0.125) < 1e-6, "judge_punch: muộn 0,125 s → LỆCH, dời −0,125")
    early = qa_sync.judge_punch(10.4, 10.55, {"a_peak": 10.2, "a_start": 10.19, "level": -6}, FPS)
    check(early["block"], "judge_punch: tiếng sớm hơn đoạn phóng > 0,1 s → CHẶN")
    # cắt: đỉnh khớp nhưng phần dạo đầu của file nghe thấy sớm hơn hình 0,21 s → không dời, mà cắt đầu file
    pre = qa_sync.judge(44.73, 44.73, {"a_peak": 44.73, "a_start": 44.52, "level": -6}, FPS)
    check(pre["status"] == "LỆCH" and pre["shift"] is None and abs(pre["trim"] - 0.11) < 1e-6, "judge: đỉnh khớp, dạo đầu sớm > 0,1 s → trim 0,11 (không dời)", str(pre))
    ev = {"track": "A2 SFX", "at": 44.523, "name": "n", "src": "s"}
    sh_trim = qa_sync.shifts_of([{"beat": "cut", "clip": "V1", "event": ev, **pre}])
    check(sh_trim == [{"beat": "cut", "clip": "V1", "track": "A2 SFX", "at": 44.523, "name": "n", "src": "s", "trim": 0.11}], "shifts_of: ghi trim khi không có shift", str(sh_trim))
    check(not qa_sync.judge_open({"a_peak": 0.3, "a_start": 0.2, "level": -6}, 0.0, FPS)["ok"], "judge_open: lặng đầu 0,2 s → LỆCH")
    counts = qa_sync.count_by_beat(rows)
    check(counts["text"]["n"] == 4 and counts["text"]["LỆCH"] == 2 and counts["text"]["khác"] == 1 and counts["text"]["CHẶN"] == 1,
          "count_by_beat: chữ 4 mục · 2 LỆCH · 1 CHẶN · 1 không mốc", str(counts))
    sh = qa_sync.shifts_of(rows)
    check({s["beat"] for s in sh} == {"text"} and len(sh) == 2 and all("clip" in s and "src" in s for s in sh),
          "shifts_of: ghi beat + clip hình cho các mục LỆCH", str(sh))


def test_sfx_shift_all_beats(d: Path) -> None:
    spec = make_spec(d)
    clips = spec["tracks"][3]["clips"]
    clips[0]["at"], clips[0]["gain_db"] = 0.0, [[0, -10], [0.3, -10], [0.6, -30]]
    sh = [{"beat": "text", "clip": "x", "track": "A2 SFX (mở đầu)", "at": 3.6, "name": clips[2]["name"], "src": clips[2]["src"], "shift": 0.34},
          {"beat": "open", "clip": "khung 0–1", "track": "A2 SFX (mở đầu)", "at": 0.0, "name": clips[0]["name"], "src": clips[0]["src"], "shift": -0.2}]
    new, done, missing = sfx_shift.apply_shifts(spec, sh)
    n = new["tracks"][3]["clips"]
    check(not missing and abs(n[2]["at"] - 3.94) < 1e-6, "sfx_shift: dời SFX chữ +0,34", str(done))
    check(n[0]["at"] == 0.0 and abs(n[0]["in"] - 0.2) < 1e-6 and abs(n[0]["dur"] - 0.8) < 1e-6,
          "sfx_shift: mở đầu dời sớm → cắt 0,2 s đầu file (in +0,2, dur −0,2)", str(n[0]))
    check(n[0]["gain_db"][0] == [0, -10.0] and n[0]["gain_db"][-1] == [0.4, -30.0], "sfx_shift: keyframe gain dịch theo phần cắt", str(n[0]["gain_db"]))
    check(all("[text]" in x or "[open]" in x for x in done), "sfx_shift: dòng báo có loại nhịp", str(done))
    tr = sfx_shift.apply_shifts(spec, [{"beat": "cut", "track": "A2 SFX (mở đầu)", "at": 3.6, "name": "n", "src": clips[2]["src"], "trim": 0.11}])[0]["tracks"][3]["clips"][2]
    check(abs(tr["at"] - 3.71) < 1e-6 and abs(tr["in"] - 0.11) < 1e-6 and abs(tr["dur"] - 0.89) < 1e-6, "sfx_shift: trim cắt đầu file, at và in cùng +0,11", str(tr))
    check(spec["tracks"][3]["clips"][2]["at"] == 3.6, "sfx_shift không sửa spec gốc")
    ov = {"tracks": [{"type": "audio", "name": "A2 SFX", "clips": [{"at": 1.0, "dur": 1.0}, {"at": 1.5, "dur": 1.0}]}]}
    check(len(sfx_shift.overlaps(ov)) == 1, "overlaps: đúng 1 cặp chồng")


with tempfile.TemporaryDirectory() as t:
    test_classify_and_visible()
    for fn in (test_punch_and_layers, test_measure_beats, test_sfx_shift_all_beats):
        sub = Path(t) / fn.__name__
        sub.mkdir()
        fn(sub)

print("\nTẤT CẢ ĐẠT" if not fails else f"\n{len(fails)} LỖI: {fails}")
sys.exit(1 if fails else 0)
