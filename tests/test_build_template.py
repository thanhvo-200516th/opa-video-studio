#!/usr/bin/env python3
"""v2.5 (C1 C3 C4 C5 C7 C8): mẫu dựng build_spec_q.py + at_speed / script_words, plan_cuts_best, rotation cut_seed,
edit_rules audit --manifest/--pain + chi tiết D1, contact_sheet --full, qa_sync mốc cắt tự động.
Chạy: ~/.venvs/video-skills/bin/python tests/test_build_template.py"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import cut_plan  # noqa: E402
import contact_sheet  # noqa: E402
import rotation  # noqa: E402
from build_kit import at_speed, script_words  # noqa: E402
from edit_rules import audit_spec  # noqa: E402
from spec_lint import lint  # noqa: E402

TEMPLATE = ROOT / "assets/motion-fx/build_spec_q.py"
FFMPEG = ["ffmpeg", "-v", "error", "-y"]


def test_at_speed() -> None:
    assert at_speed([(1.0, 2.2)], 1.1) == [(0.9, 2.0)], at_speed([(1.0, 2.2)], 1.1)
    assert at_speed([(1.0, 2.2)], 1.0) == [(1.0, 2.2)]
    w = at_speed([{"text": "a", "start": 1.1, "end": 2.2}], 1.1)
    assert w == [{"text": "a", "start": 1.0, "end": 2.0}], w
    print("ok  at_speed: cặp (a, b) chia tốc độ rồi bám khung; từ giữ khoá khác, chia start / end")


def test_script_words() -> None:
    words = [{"text": t, "start": s, "end": s + 0.3} for t, s in [("một", 0.2), ("hai", 0.6), ("ba", 1.0), ("bốn", 3.2), ("năm", 3.6)]]
    segs = [(0.1, 1.5), (3.0, 4.2)]
    out = script_words(["một", "hai", "ba", "bốn", "năm"], words, segs, [0.0, 1.4])
    assert [o[0] for o in out] == ["một", "hai", "ba", "bốn", "năm"], out
    assert abs(out[3][1] - (1.4 + 0.2)) < 0.02 and out[0][1] == 0.1, out           # bốn: 3.2 − 3.0 + t0 của đoạn 2
    assert all(b - a >= 0.08 - 1e-6 for _, a, b in out) and all(x[1] <= y[1] + 1e-6 for x, y in zip(out, out[1:]))
    gap = script_words(["một", "x", "hai"], [{"text": "một", "start": 0.2, "end": 0.4}, {"text": "hai", "start": 3.4, "end": 3.6}],
                       segs, [0.0, 1.4])                                               # chữ "x" rơi vào khoảng cắt → không rớt
    assert len(gap) == 3, gap
    print("ok  script_words: chữ theo kịch bản, mốc theo timeline, không rớt chữ trong khoảng cắt")


def test_plan_cuts_best() -> None:
    import numpy as np

    def fake_frame(src: str, t: float):
        rng = np.random.default_rng(zlib.crc32(f"{src}{round(t, 2)}".encode()))
        return rng.random((cut_plan.H, cut_plan.W)).astype(np.float32) * 255

    real = cut_plan.frame
    cut_plan.frame = fake_frame
    try:
        cuts = [cut_plan.Cut(t=2.0 * i, a=(f"a{i}.mp4", 1.0), b=(f"b{i}.mp4", 0.0), before="câu một.", after="câu hai") for i in range(1, 25)]
        plan = cut_plan.plan_cuts_best(cuts, seed=3, tries=8)
    finally:
        cut_plan.frame = real
    joins = [c.info["join"] for c in plan]
    assert all(x != y for x, y in zip(joins, joins[1:])), joins
    flashy = sum(1 for j in joins if any(m in j for m in cut_plan.FLASHY))
    assert flashy <= 0.2 * len(joins) + 1e-9, (flashy, joins)
    assert len(set(joins)) >= 6, set(joins)
    print(f"ok  plan_cuts_best: 24 điểm cắt · {len(set(joins))} kiểu · nháy sáng {flashy} · không lặp liền")


def test_rotation_cut_seed() -> None:
    with tempfile.TemporaryDirectory() as td:
        led = rotation.plan(Path(td), ["OPA05"])
        v = led["videos"][0]
        assert v["cut_seed"] == zlib.crc32(b"cutOPA05") % 997, v
        assert rotation.entry(Path(td), "OPA05")["cut_seed"] == v["cut_seed"]
    print("ok  rotation: sổ cấp cut_seed = crc32('cut'+tên) % 997")


def test_rotation_out() -> None:
    """J-1 #2: `plan <video dir> <MÃ> --out <O>` ghi sổ vào O, KHÔNG ghi vào thư mục video; entry() tìm ở O trước."""
    with tempfile.TemporaryDirectory() as td:
        v, o = Path(td) / "05_OPA05", Path(td) / "05_OPA05" / "v4"
        v.mkdir()
        r = subprocess.run([sys.executable, str(ROOT / "scripts/rotation.py"), "plan", str(v), "OPA05", "--out", str(o)],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        assert (o / "rotation.json").is_file() and not (v / "rotation.json").exists(), list(v.rglob("*"))
        assert rotation.entry(v, "OPA05") is None                         # không có sổ ở V
        e = rotation.entry(v, "OPA05", out=o)
        assert e and e["video"] == "OPA05" and e["cut_seed"] == zlib.crc32(b"cutOPA05") % 997, e
        again = rotation.plan(o, ["OPA05"])                               # chạy lại giữ ô đã cấp
        assert len(again["videos"]) == 1
        (Path(td) / "lo").mkdir()
        r2 = subprocess.run([sys.executable, str(ROOT / "scripts/rotation.py"), "plan", str(Path(td) / "lo"), "A1", "A2"],
                            capture_output=True, text=True)               # lô: mặc định không đổi (sổ ở thư mục gốc lô)
        assert r2.returncode == 0 and (Path(td) / "lo" / "rotation.json").is_file(), r2.stdout + r2.stderr
    print("ok  rotation --out: sổ nằm trong O, entry() tìm O trước, V không bị ghi")


def test_edit_rules_pain() -> None:
    words = [["Mình", 0.2], ["bị", 0.5], ["gãy", 1.0], ["gánh", 1.3], ["rồi", 1.6]]
    spec = {"fps": 30, "duration": 4, "tracks": [
        {"type": "video", "name": "V1 chính", "clips": [{"src": "x.mp4", "at": 0, "dur": 4, "name": "A-roll 1",
                                                        "motion": {"scale": [[0, 100], [4, 110]]}}]},
        {"type": "text", "name": "FX · text_top 1", "clips": [{"text": "GÃY GÁNH", "at": 0.9, "dur": 1.5}]}]}
    base = {r["rule"]: r for r in audit_spec(spec, words)}
    assert base["Từ khoá nỗi đau được nhấn"]["status"] == "CHƯA KIỂM", base["Từ khoá nỗi đau được nhấn"]
    custom = {r["rule"]: r for r in audit_spec(spec, words, extra_pain=["gãy gánh"])}
    assert custom["Từ khoá nỗi đau được nhấn"]["status"] == "OK", custom["Từ khoá nỗi đau được nhấn"]
    # D1: chi tiết đoạn nói trơ có mốc đầu / cuối và lời
    d1 = custom["Nhiều B-roll / footage"]["detail"]
    assert "0.0–4.0 s" in d1 and "Mình" in d1, d1
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "s.craft.json").write_text(json.dumps(spec, ensure_ascii=False))
        (d / "w.json").write_text(json.dumps(words, ensure_ascii=False))
        (d / "m.json").write_text(json.dumps({"segments": [{"keywords": [], "pain_keywords": ["gãy gánh"]}]}))
        run = lambda *extra: subprocess.run([sys.executable, str(ROOT / "scripts/edit_rules.py"), "audit", str(d / "s.craft.json"),  # noqa: E731
                                             "--words", str(d / "w.json"), *extra], capture_output=True, text=True)
        assert re.search(r"\[CHƯA KIỂM\s*\] Từ khoá nỗi đau", run().stdout), run().stdout
        for extra in (["--pain", "gãy gánh"], ["--manifest", str(d / "m.json")]):
            r = run(*extra)
            assert re.search(r"\[OK\s*\] Từ khoá nỗi đau được nhấn", r.stdout), r.stdout + r.stderr
        (d / "pain.json").write_text(json.dumps({"pain": ["gãy gánh"]}, ensure_ascii=False))   # J-1 #6: pain.json cạnh spec
        r = run()
        assert re.search(r"\[OK\s*\] Từ khoá nỗi đau được nhấn", r.stdout), r.stdout + r.stderr
        m = re.search(r"Tổng: (\d+) LỖI · (\d+) CẢNH BÁO · (\d+) CHƯA KIỂM", r.stdout)
        assert m and int(m.group(3)) == r.stdout.count("[CHƯA KIỂM") == 1 and int(m.group(1)) == r.stdout.count("[LỖI") == 1, r.stdout
    print("ok  edit_rules audit --pain / --manifest / pain.json: cụm riêng → OK; D1 in mốc đoạn trơ; dòng Tổng")


def test_contact_sheet_full() -> None:
    def keyed(at: float, dur: float, kt: float | None, name: str, lane: str = "text_top 1") -> dict:
        c = {"text": name, "at": at, "dur": dur}
        if kt is not None:
            c["opacity"] = [[0, 0], [kt, 100], [dur, 0]]
        return c

    caps = [keyed(round(0.2 + 0.25 * i, 2), 0.6, None, f"cap{i}") for i in range(60)]
    keys = [keyed(1.0, 2.0, 0.3, "K1"), keyed(5.0, 2.0, None, "K2"), keyed(9.0, 1.0, 0.9, "K3")]     # K3: key 0,9 > 0,6·dur → 0,45 s
    spec = {"fps": 30, "duration": 20.0, "tracks": [
        {"type": "video", "name": "V1", "clips": [{"src": "x", "at": 0.0, "dur": 10}, {"src": "x", "at": 10.0, "dur": 10}]},
        {"type": "text", "name": "FX · text_low 1", "clips": caps},
        {"type": "text", "name": "FX · text_top 1", "clips": keys}]}
    assert len(contact_sheet.plan_times(spec)) <= 24
    full = contact_sheet.plan_times(spec, full=True)
    ts = [t for t, _ in full]
    assert len(ts) <= 40 and all(b - a >= 0.3 - 1e-6 for a, b in zip(ts, ts[1:])), (len(ts), ts)
    for c in keys:
        assert any(c["at"] < t <= c["at"] + c["dur"] for t in ts), c
    assert any(abs(t - (1.0 + 0.3 + 1 / 30)) < 0.011 for t in ts), ts               # K1: sau key vào cuối + 1 khung
    assert any(abs(t - 5.45) < 0.011 for t in ts) and any(abs(t - 9.45) < 0.011 for t in ts), ts   # không key / key muộn: +0,45 s
    n_caps = sum(1 for _, lab in full if lab.startswith("phụ đề"))
    assert 0 < n_caps < 60, n_caps                                                    # phụ đề bị thưa trước, chữ chính giữ đủ
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "s.craft.json"
        p.write_text(json.dumps(spec))
        r = subprocess.run([sys.executable, str(ROOT / "scripts/contact_sheet.py"), "times", str(p), "--full"], capture_output=True, text=True)
        assert r.returncode == 0 and len(r.stdout.split()) == len(ts), r.stdout + r.stderr
    print(f"ok  contact_sheet --full: {len(ts)} khung (≤ 40), mỗi chữ chính một khung sau lúc vào, phụ đề thưa còn {n_caps}")


def test_qa_sync_cut_times() -> None:
    import qa_sync
    spec = {"tracks": [{"type": "video", "name": "V1", "clips": [{"at": 0.0}, {"at": 2.5}, {"at": 7.0}]}]}
    assert qa_sync.cut_times(spec) == [2.5, 7.0]
    print("ok  qa_sync: mốc cắt tự động = đầu các clip V1 trừ clip đầu")


# ---------------------------------------------------------------- mẫu dựng
def make_fixture(root: Path) -> Path:
    src = root / "01_TST01_test"
    xd = src / "v3" / "media" / "x110"
    (src / "v3" / "work").mkdir(parents=True)
    xd.mkdir(parents=True)
    run = lambda *a: subprocess.run([*FFMPEG, *a], check=True)    # noqa: E731
    run("-f", "lavfi", "-i", "testsrc=s=108x192:r=30:d=7", "-f", "lavfi", "-i", "sine=d=7", "-shortest",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(xd / "01_a-roll-1.mp4"))
    run("-f", "lavfi", "-i", "mandelbrot=s=108x192:r=30", "-t", "7", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(xd / "02_b-roll-1.mp4"))
    run("-f", "lavfi", "-i", "sine=f=220:d=7", str(xd / "02_voice-b-roll-1.mp3"))
    run("-f", "lavfi", "-i", "sine=f=330:d=90", str(root / "bgm.mp3"))

    t1 = "Mình từng mất khách vì ôm hết mọi thứ vào người. Giờ khác rồi.".split()
    t2 = "Hệ thống chạy trơn tru cả ngày lẫn đêm.".split()
    w1 = [{"text": t, "start": round(0.3 + 0.4 * i, 3), "end": round(0.65 + 0.4 * i, 3)} for i, t in enumerate(t1)]
    w2 = [{"text": t, "start": round(0.2 + 0.45 * i, 3), "end": round(0.55 + 0.45 * i, 3)} for i, t in enumerate(t2)]
    manifest = {"script_id": "TST01", "slug": "01_TST01_test", "segments": [
        {"seq_prefix": "01", "role_id": "a-roll-1", "type": "a-roll", "display_text": " ".join(t1), "keywords": [],
         "pain_keywords": [], "files": {"video_file": "01_a-roll-1.mp4", "voice_file": None}},
        {"seq_prefix": "02", "role_id": "b-roll-1", "type": "b-roll", "display_text": " ".join(t2), "keywords": [],
         "pain_keywords": ["trơn tru"], "files": {"video_file": "02_b-roll-1.mp4", "voice_file": "02_voice-b-roll-1.mp3"}}]}
    (src / "00_storyboard_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False))
    plan = {"kept_src_seconds": 8.1, "speed": 1.1, "speed_dir": "x110", "scenes": [
        {"seq_prefix": "01", "video": "01_a-roll-1.mp4", "voice": None, "src_dur": 6.0,
         "segs": [[0.1, 2.6], [3.0, 5.6]], "words": w1},
        {"seq_prefix": "02", "video": "02_b-roll-1.mp4", "voice": "02_voice-b-roll-1.mp3", "src_dur": 6.0,
         "segs": [[0.1, 3.9]], "words": w2}]}
    (src / "v3" / "media" / "speed_plan.json").write_text(json.dumps(plan, ensure_ascii=False))
    return src


def edit_template(text: str, music: Path, head_top: int | None = None) -> str:
    """Việc người dùng làm: chỉ sửa các dòng / khối có `# EDIT:`."""
    if head_top is not None:
        text = re.sub(r"^HEAD_TOP = .*# EDIT.*$", f"HEAD_TOP = {head_top}  # EDIT: đỉnh đầu", text, flags=re.M)
    text = re.sub(r"^MUSIC = .*# EDIT.*$", f"MUSIC = Path({str(music)!r})  # EDIT: nhạc nền", text, flags=re.M)
    text = re.sub(r"^EXTRA_PAIN = .*# EDIT.*$", 'EXTRA_PAIN = ["ôm hết mọi thứ"]  # EDIT: nỗi đau riêng', text, flags=re.M)
    keys = ("KEY_SPECS = [  # EDIT: khối chữ chính\n"
            "    (0, 'Mình từng', 'MẤT KHÁCH', None, 'mất khách', 'gold'),\n"
            "    (0, 'Giờ', 'KHÁC RỒI', None, 'khác rồi', 'cyan'),\n"
            "    (1, 'Hệ thống', 'CHẠY TRƠN TRU', None, 'trơn tru', 'mint'),\n]\n")
    return re.sub(r"^KEY_SPECS = \[.*?^\]\n", lambda _: keys, text, flags=re.M | re.S)


def test_template() -> None:
    assert TEMPLATE.is_file(), TEMPLATE
    body = TEMPLATE.read_text(encoding="utf-8")
    assert "caption_band" not in body and "SHADE_BOTTOM" not in body and ".claude/skills" not in body
    assert body.count("# EDIT:") >= 3
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        src = make_fixture(root)
        script = src / "v3/work/build_spec_q.py"
        script.write_text(edit_template(body, root / "bgm.mp3"), encoding="utf-8")
        assert script.read_text().count("MẤT KHÁCH") == 1
        r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, env={**__import__("os").environ, "OPA_SKILL_DIR": str(ROOT)})
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-2500:]
        w = src / "v3/work"
        spec_p = w / "tst01.craft.json"
        assert spec_p.is_file() and (w / "words_tl.json").is_file() and (w / "transition_plan.md").is_file(), list(w.iterdir())
        spec = json.loads(spec_p.read_text())
        v1 = next(t for t in spec["tracks"] if t["type"] == "video")
        a1 = next(t for t in spec["tracks"] if t["type"] == "audio")
        assert v1["name"].startswith("V1") and a1["name"].startswith("A1"), (v1["name"], a1["name"])
        assert len(v1["clips"]) == len(a1["clips"]) == 3, (len(v1["clips"]), len(a1["clips"]))
        for v, a in zip(v1["clips"], a1["clips"]):
            assert abs(v["at"] - a["at"]) < 1e-6 and abs(v["dur"] - a["dur"]) < 1e-6, (v, a)
        assert abs(v1["clips"][-1]["at"] + v1["clips"][-1]["dur"] - spec["duration"]) < 0.02
        assert v1["clips"][0]["src"].endswith("x110/01_a-roll-1.mp4") and v1["clips"][2]["name"].startswith("B-roll")
        names = " ".join(c.get("name", "") for t in spec["tracks"] for c in t["clips"]).lower()
        assert "dải tối dưới" not in names and "dải tối sau phụ đề" not in names
        words = json.loads((w / "words_tl.json").read_text())
        assert len(words) == 14 + 9, len(words)
        for hit in ("mất khách", "ôm hết mọi thứ", "trơn tru"):
            assert hit in r.stdout, (hit, r.stdout[-800:])
        res = lint(spec_p, words)
        hard = [x for x in res if x["status"] == "HARD"]
        assert not hard, hard
        co = next(x for x in res if x["id"] == "caption_overlap")      # J-1 #7: nhiều hàng phụ đề, không chồng ở chỗ nối hàng
        assert co["status"] == "OK", co
        cut_ts = [c["at"] for c in v1["clips"][1:]]                        # v2.7: chữ chính kết thúc đúng điểm cắt (SKILL §11)
        for t in spec["tracks"]:
            for c in t["clips"]:
                if str(c.get("name", "")).startswith("Từ khoá"):
                    assert not any(c["at"] + 0.05 < ct < c["at"] + c["dur"] - 1 / 30 - 1e-6 for ct in cut_ts), (c["name"], c["at"], c["dur"], cut_ts)
        plan_md = (w / "transition_plan.md").read_text(encoding="utf-8")   # J-1 #8: cột C3
        assert "| Giây | Cảnh | Chữ chính | Chuyển cảnh | Zoom | Nỗi đau | SFX | Lý do |" in plan_md, plan_md[:400]
        assert len([x for x in plan_md.splitlines() if x.startswith("| ")]) == 1 + 2, plan_md   # tiêu đề + 2 điểm cắt
        pain = json.loads((w / "pain.json").read_text(encoding="utf-8"))          # J-1 #6
        assert {"ôm hết mọi thứ", "trơn tru"} <= set(pain["pain"]) and pain["hits"], pain
        assert "Mã video" in r.stdout and "TST01" in r.stdout, r.stdout[:600]       # J-1 #2: in MÃ (script_id)
        assert "rotation.py plan" in r.stdout and "--out" in r.stdout, r.stdout[:600]   # chưa có sổ → in lệnh
        au = subprocess.run([sys.executable, str(ROOT / "scripts/edit_rules.py"), "audit", str(spec_p), "--words", str(w / "words_tl.json")],
                            capture_output=True, text=True)
        assert re.search(r"Tổng: \d+ LỖI · \d+ CẢNH BÁO · \d+ CHƯA KIỂM", au.stdout), au.stdout + au.stderr
        assert not re.search(r"\[CHƯA KIỂM\s*\] Từ khoá nỗi đau", au.stdout), au.stdout     # pain.json cạnh spec
    print("ok  build_spec_q: 2 cảnh → V1 / A1 khớp, không caption_band, spec_lint 0 HARD, nỗi đau gồm EXTRA_PAIN + manifest")


def test_behind_person_offset() -> None:
    """J-1 #3: matte tách từ giây S (`matte.py --start S`) → `in` của clip matte = in V1 − S (không âm)."""
    import motion_fx
    with tempfile.TemporaryDirectory() as td:
        fx = motion_fx.MotionFX(gfx_dir=Path(td), fps=30, name="T")
        v1 = [{"src": "a.mp4", "at": 0.0, "in": 3.0, "dur": 4.0}]
        block = lambda: [{"at": 1.0, "dur": 1.5, "_role": "mx_heavy", "text": "X"}]    # noqa: E731
        assert fx.behind_person(block(), v1, "m.mov")[0]["in"] == 4.0
        assert fx.behind_person(block(), v1, "m.mov", matte_offset=2.0)[0]["in"] == 2.0
        assert fx.behind_person(block(), v1, "m.mov", matte_offset=9.0)[0]["in"] == 0.0
    print("ok  behind_person matte_offset: in = in V1 + lệch − S, không âm")


def run_template(src: Path, root: Path, head_top: int | None = None) -> subprocess.CompletedProcess:
    script = src / "v3/work/build_spec_q.py"
    script.write_text(edit_template(TEMPLATE.read_text(encoding="utf-8"), root / "bgm.mp3", head_top), encoding="utf-8")
    return subprocess.run([sys.executable, str(script)], capture_output=True, text=True, env={**__import__("os").environ, "OPA_SKILL_DIR": str(ROOT)})


def test_template_matte() -> None:
    """J-1 #3 + #5: hook chạm đầu → in lệnh matte.py đủ --start/--dur khi thiếu matte; có matte (đặt tên _s<S>) thì dùng, `in` trừ S."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        src = make_fixture(root)
        r = run_template(src, root, head_top=420)
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-2500:]
        spec_p = src / "v3/work/tst01.craft.json"
        names = [t["name"] for t in json.loads(spec_p.read_text())["tracks"]]
        assert not any(n.startswith("V2") for n in names), names                  # chưa có matte → không có lớp người
        m = re.search(r"matte\.py --input (\S+) --output (\S+) --start ([\d.]+) --dur ([\d.]+)", r.stdout)
        assert m and "person_alpha_s" in m.group(2) and "Chữ hook" in r.stdout, r.stdout[:1500]
        start, length = float(m.group(3)), float(m.group(4))
        assert start > 0 and length > 1.0, (start, length)
        subprocess.run([*FFMPEG, "-f", "lavfi", "-i", "testsrc=s=108x192:r=30", "-t", str(length), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        m.group(2)], check=True)                                   # giả lập kết quả matte.py (chỉ cần đúng tên + độ dài)
        r = run_template(src, root, head_top=420)
        assert r.returncode == 0 and "matte.py" not in r.stdout, r.stdout[-1500:] + r.stderr[-2500:]
        spec = json.loads(spec_p.read_text())
        v1 = next(t for t in spec["tracks"] if t["name"].startswith("V1"))["clips"]
        v2 = next(t for t in spec["tracks"] if t["name"].startswith("V2"))["clips"]
        assert v2 and v2[0]["src"] == m.group(2), v2
        v_in = next(v["in"] + (v2[0]["at"] - v["at"]) for v in v1 if v["at"] <= v2[0]["at"] < v["at"] + v["dur"])
        assert abs(v2[0]["in"] - (v_in - start)) < 0.02, (v2[0]["in"], v_in, start)
    print("ok  template: thiếu matte → in lệnh matte.py --start/--dur; có matte _s<S> → V2 dùng, in = in V1 − S")


if __name__ == "__main__":
    test_at_speed()
    test_script_words()
    test_plan_cuts_best()
    test_rotation_cut_seed()
    test_rotation_out()
    test_behind_person_offset()
    test_template_matte()
    test_edit_rules_pain()
    test_contact_sheet_full()
    test_qa_sync_cut_times()
    test_template()
    print("TẤT CẢ ĐẠT")
