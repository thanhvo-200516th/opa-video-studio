#!/usr/bin/env python3
"""Kiểm A1 (build_spec_q: KEY_SPECS trống → ghi words_tl.json rồi thoát sạch; có plan_export.json → sinh KEY_SPECS),
A2 (plan_doc.py build / export) và A3 (suggest: stay | show | close). Offline.
Chạy: ~/.venvs/video-skills/bin/python tests/test_plan_doc.py"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import plan_doc as pd  # noqa: E402
from test_build_template import TEMPLATE, make_fixture  # noqa: E402

ENV = {**os.environ, "OPA_SKILL_DIR": str(ROOT)}


# ---------------------------------------------------------------- A3
def test_suggest() -> None:
    cases = [
        ("Hôm nay mình giới thiệu kiểu dựng tối giản.", False, False, "stay"),     # giới thiệu kiểu mới
        ("Khái niệm này gọi là sự chú ý có chủ đích.", False, False, "stay"),
        ("Chi tiết nhỏ nhưng quan trọng.", True, False, "stay"),                    # is_new_item
        ("Công ty có 300 nhân viên và doanh thu 5 triệu đô.", False, False, "show"),  # số
        ("Ông Brooks đứng trước bức tranh cũ ở Hà Nội.", False, False, "show"),     # người / vật / nơi
        ("Chúng tôi đi qua Paris vào mùa đông.", False, False, "show"),            # danh từ riêng giữa câu
        ("Có những lúc nỗi buồn khiến ta cô đơn.", False, False, "close"),         # cảm xúc
        ("Và đó là cuộc sống.", False, True, "close"),                             # nhịp cuối
        ("Mọi thứ cứ thế diễn ra.", False, False, "stay"),                         # mặc định
    ]
    for text, new, last, want in cases:
        got = pd.suggest(text, new, last)
        assert got == want, (text, got, want)
    assert pd.suggest("Ông ấy khóc.", False, False) == "close"                      # cảm xúc thắng mô tả
    assert pd.suggest("Ông có 3 người.", True, False) == "stay"                     # mục mới thắng mô tả
    label, why = pd.explain("Có 5 người.", False, False)
    assert label == "show" and why, (label, why)
    print("ok  suggest: giới thiệu → stay · mô tả số/người/nơi → show · cảm xúc/kết → close")


# ---------------------------------------------------------------- A2
def synth_words(spec: list[tuple[str, float]]) -> list[tuple[str, float, float]]:
    """spec = [(chữ, độ dài giây)] liền nhau."""
    out, t = [], 0.3
    for tok, d in spec:
        out.append((tok, round(t, 3), round(t + d - 0.05, 3)))
        t += d
    return out


def test_split_beats() -> None:
    sent = lambda n, end: [(f"w{i}", 0.5) for i in range(n - 1)] + [(f"w{n}{end}", 0.5)]   # noqa: E731
    # 2 câu 4 s + câu 1,5 s + câu 5 s: câu ngắn gộp, mỗi nhịp 3–6 s hoặc cụt gộp vào trước
    words = synth_words(sent(8, ".") + sent(3, ".") + sent(10, "."))
    whole = [{"scene": 0, "first": 0, "last": len(words) - 1, "type": "a-roll", "video": None, "role": None}]
    spans = pd.split_beats(words, whole)
    assert spans[0][0] == 0 and spans[-1][1] == len(words) - 1
    assert all(a2 == b1 + 1 for (_, b1), (a2, _) in zip(spans, spans[1:])), spans     # liền mạch, không rớt từ
    durs = [words[b][2] - words[a][1] for a, b in spans]
    assert all(d <= pd.BEAT_MAX_S + 0.6 for d in durs), durs
    assert all(d >= pd.BEAT_MIN_S - 0.6 for d in durs), durs
    assert words[spans[0][1]][0].endswith("."), spans                                 # đóng nhịp ở cuối câu
    # ranh giới cảnh luôn cắt nhịp, dù chưa tới 3 s
    two = [{"scene": 0, "first": 0, "last": 3, "type": "a-roll", "video": None, "role": None},
           {"scene": 1, "first": 4, "last": 9, "type": "b-roll", "video": "x.mp4", "role": None}]
    sp = pd.split_beats(synth_words([(f"a{i}", 0.4) for i in range(10)]), two)
    assert any(b == 3 for _, b in sp) and any(a == 4 for a, _ in sp), sp
    # một câu dài không dấu chấm vẫn bị chặn ở ~6 s
    long = synth_words([(f"a{i}", 0.5) for i in range(30)])
    sp = pd.split_beats(long, [{**whole[0], "last": 29}])
    assert len(sp) >= 2 and all(long[b][2] - long[a][1] <= pd.BEAT_MAX_S + 0.6 for a, b in sp), sp
    print("ok  split_beats: cuối câu, ranh giới cảnh, giới hạn 6 s, không rớt từ")


def write_words(w: Path, words: list) -> None:
    w.mkdir(parents=True, exist_ok=True)
    (w / "words_tl.json").write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")


def sample_words() -> list[tuple[str, float, float]]:
    text = ("Hôm nay mình giới thiệu kiểu dựng mới. Ông Brooks đứng trước bức tranh cũ ở Hà Nội và nhìn rất lâu. "
            "Có những lúc nỗi buồn khiến ta cô đơn. Và đó là cuộc sống.")
    return synth_words([(t, 0.45) for t in text.split()])


def embedded(html: str) -> dict:
    m = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S)
    assert m, "không có khối dữ liệu"
    return json.loads(m.group(1).replace("<\\/", "</"))


def test_build_html() -> None:
    with tempfile.TemporaryDirectory() as td:
        w = Path(td) / "ver" / "work"
        write_words(w, sample_words())
        out = w / "edit_plan.html"
        assert pd.main(["build", str(w), "--out", str(out)]) == 0
        html = out.read_text(encoding="utf-8")
        draft = json.loads((w / "plan_draft.json").read_text(encoding="utf-8"))
        assert html.lstrip().startswith("<!DOCTYPE html>") and html.rstrip().endswith("</html>")
        assert not re.search(r"""(?:src|href)=["']?(?:https?:)?//""", html) and "<link" not in html and "@import" not in html, "phải offline"
        assert "localStorage" in html and "Xuất JSON" in html and "Copy Plan" in html and "Gợi ý" in html
        data = embedded(html)
        assert data["beats"] == draft["beats"] and len(data["beats"]) >= 2
        for b in data["beats"]:
            assert [o["id"] for o in b["options"]] == ["A", "B", "C"], b["options"]
            assert b["t0"] < b["t1"] and b["text"] and b["suggest"] in "ABC" and b["words"]
            a, bb, c = b["options"]
            assert a["kind"] == "stay" and a["scene_type"] == "aroll" and a["key"] and a["key"]["phrase"]
            assert bb["kind"] == "keyword" and bb["scene_type"] == "overlay" and bb["key"]
            assert c["scene_type"] == "cutaway" and c["key"] is None
            assert a["key"]["palette"] != bb["key"]["palette"]
        assert data["beats"][0]["t0"] == 0.0 and data["beats"][-1]["suggest"] == "B"     # nhịp cuối → close → B
        assert data["beats"][0]["suggest"] == "A"                                          # nhịp đầu → giữ mặt
        assert all(abs(b1["t1"] - b2["t0"]) < 1e-6 for b1, b2 in zip(data["beats"], data["beats"][1:]))
        for b in data["beats"]:                                                            # chữ chính lấy từ lời (B10), không vắt qua dấu câu
            assert not re.search(r"[.?!,;:]\s", " ".join(o["key"]["text"] for o in b["options"][:2])), b["options"]
            for o in b["options"][:2]:
                assert pd.find_phrase(pd.load_words(w), o["key"]["phrase"], b["t0"], b["t1"]) is not None, (b["beat"], o["key"])
    print("ok  plan_doc build: HTML offline, N nhịp × 3 phương án, gợi ý chỉ là badge, chữ chính nằm trong lời")


def test_build_manifest_broll() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        w = root / "ver" / "work"
        words = synth_words([(f"t{i}", 0.5) for i in range(10)])
        write_words(w, words)
        man = {"script_id": "X", "segments": [
            {"seq_prefix": "01", "role_id": "a-roll-1", "type": "a-roll", "display_text": "t0 t1 t2 t3 t4", "files": {"video_file": "01_a.mp4"}},
            {"seq_prefix": "02", "role_id": "b-roll-1", "type": "b-roll", "display_text": "t5 t6 t7 t8 t9", "files": {"video_file": "02_b.mp4"}}]}
        (root / "m.json").write_text(json.dumps(man))
        pd.main(["build", str(w), "--manifest", str(root / "m.json"), "--out", str(w / "p.html")])
        beats = json.loads((w / "plan_draft.json").read_text())["beats"]
        assert [b["scene"] for b in beats] == [0, 1], [(b["scene"], b["t0"]) for b in beats]
        c = beats[1]["options"][2]
        assert c["kind"] == "broll" and c["ref"] == "02_b.mp4" and beats[1]["suggest"] == "C", beats[1]
        assert beats[0]["options"][2]["kind"] == "gfx"
    print("ok  plan_doc build --manifest: ranh giới cảnh, phương án C = B-roll của manifest / đồ hoạ")


def export_of(draft: dict, picks: dict[int, str]) -> dict:
    out = []
    for b in draft["beats"]:
        o = next((o for o in b["options"] if o["id"] == picks.get(b["beat"])), None)
        out.append({"beat": b["beat"], "t0": b["t0"], "t1": b["t1"], "scene": b["scene"], "phrase": o["key"]["phrase"] if o and o["key"] else "",
                    "choice": {"ref": o["ref"], "kind": o["kind"], "scene_type": o["scene_type"]} if o else None,
                    "key": o["key"] if o else None, "note": "", "broll_note": "" if o and not o["key"] else None})
    return {"version": 1, "beats": out}


def test_export() -> None:
    with tempfile.TemporaryDirectory() as td:
        w = Path(td) / "ver" / "work"
        write_words(w, sample_words())
        pd.main(["build", str(w), "--out", str(w / "p.html")])
        draft = json.loads((w / "plan_draft.json").read_text())
        good = export_of(draft, {1: "A", 2: "B", 3: "C"})
        f = Path(td) / "dl.json"
        f.write_text(json.dumps(good))
        assert pd.main(["export", str(f), str(w)]) == 0
        saved = json.loads((w / "plan_export.json").read_text())
        assert len(saved["beats"]) == len(draft["beats"]) and saved["beats"][0]["choice"]["kind"] == "stay"
        assert saved["beats"][-1]["choice"] is None                                         # chưa chọn giữ nguyên null
        for bad_key, patch in {"phrase": {"phrase": "không có trong lời"}, "palette": {"palette": "pink"}, "text": {"text": " "}}.items():
            bad = json.loads(json.dumps(good))
            bad["beats"][0]["key"] = {**bad["beats"][0]["key"], **patch}
            f.write_text(json.dumps(bad))
            (w / "plan_export.json").unlink(missing_ok=True)
            try:
                pd.main(["export", str(f), str(w)])
            except SystemExit as e:
                assert "không hợp lệ" in str(e), e
            else:
                raise AssertionError(f"export phải từ chối {bad_key}")
            assert not (w / "plan_export.json").exists()
        bad = json.loads(json.dumps(good))
        bad["beats"][2]["choice"]["kind"] = "foo"
        f.write_text(json.dumps(bad))
        try:
            pd.main(["export", str(f), str(w)])
        except SystemExit:
            pass
        else:
            raise AssertionError("kind lạ phải bị từ chối")
    print("ok  plan_doc export: ghi plan_export.json; từ chối cụm ngoài lời / palette lạ / kind lạ")


# ---------------------------------------------------------------- A1
def prepare(root: Path, with_keys: bool) -> tuple[Path, Path]:
    """Chép mẫu build_spec_q.py vào work của fixture; chỉ sửa MUSIC (và KEY_SPECS nếu with_keys)."""
    src = make_fixture(root)
    body = TEMPLATE.read_text(encoding="utf-8")
    body = re.sub(r"^MUSIC = .*# EDIT.*$", f"MUSIC = Path({str(root / 'bgm.mp3')!r})  # EDIT: nhạc nền", body, flags=re.M)
    if with_keys:
        keys = "KEY_SPECS = [  # EDIT: khối chữ chính\n    (0, 'Mình từng', 'MẤT KHÁCH', None, 'mất khách', 'gold'),\n]\n"
        body = re.sub(r"^KEY_SPECS = \[.*?^\]\n", lambda _: keys, body, flags=re.M | re.S)
    script = src / "v3/work/build_spec_q.py"
    script.write_text(body, encoding="utf-8")
    return src, script


def run(script: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script)], capture_output=True, text=True, env=ENV)


def test_empty_key_specs_writes_words() -> None:
    with tempfile.TemporaryDirectory() as td:
        src, script = prepare(Path(td), with_keys=False)
        r = run(script)
        w = src / "v3/work"
        assert r.returncode == 0, r.stdout[-800:] + r.stderr[-1500:]
        assert (w / "words_tl.json").is_file() and len(json.loads((w / "words_tl.json").read_text())) == 23
        assert not (w / "tst01.craft.json").exists(), "chưa có KEY_SPECS thì không dựng spec"
        assert "words_tl.json" in r.stdout and "KEY_SPECS trống" in r.stdout and "plan_doc.py" in r.stdout, r.stdout
    print("ok  build_spec_q: KEY_SPECS trống → ghi words_tl.json, thoát 0 kèm hướng dẫn, không dựng spec")


def test_key_specs_from_plan_export() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        src, script = prepare(root, with_keys=False)
        w = src / "v3/work"
        assert run(script).returncode == 0
        pd.main(["build", str(w), "--manifest", str(src / "00_storyboard_manifest.json"), "--out", str(w / "edit_plan.html")])
        draft = json.loads((w / "plan_draft.json").read_text())
        assert [b["scene"] for b in draft["beats"]] == sorted(b["scene"] for b in draft["beats"]) and draft["beats"][-1]["scene"] == 1
        picks = {b["beat"]: ("A" if i % 2 == 0 else "C") for i, b in enumerate(draft["beats"])}
        f = root / "dl.json"
        f.write_text(json.dumps(export_of(draft, picks)))
        assert pd.main(["export", str(f), str(w)]) == 0
        r = run(script)
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-2500:]
        assert "plan_export.json" in r.stdout and "(0, " in r.stdout or "(1, " in r.stdout, r.stdout[:1200]
        spec = json.loads((w / "tst01.craft.json").read_text())
        texts = {c["text"] for t in spec["tracks"] for c in t["clips"] if "text" in c}
        expect = {b["key"]["text"] for b in json.loads((w / "plan_export.json").read_text())["beats"] if b["key"]}
        assert expect and all(any(e.lower() in t.lower() for t in texts) for e in expect), (expect, texts)
        assert re.search(r"\[chưa hỗ trợ\] nhịp \d+ \((?:gfx|broll)\)", r.stdout), r.stdout
        # KHÔNG hồi quy: KEY_SPECS điền tay → plan_export.json bị bỏ qua, spec không đổi
        (w / "tst01.craft.json").unlink()
        script.write_text(re.sub(r"^KEY_SPECS = \[.*?^\]\n",
                                 lambda _: "KEY_SPECS = [  # EDIT: khối\n    (0, 'Mình từng', 'MẤT KHÁCH', None, 'mất khách', 'gold'),\n]\n",
                                 script.read_text(encoding="utf-8"), flags=re.M | re.S), encoding="utf-8")
        assert run(script).returncode == 0
        with_export = (w / "tst01.craft.json").read_bytes()
        (w / "plan_export.json").unlink()
        (w / "tst01.craft.json").unlink()
        assert run(script).returncode == 0
        assert (w / "tst01.craft.json").read_bytes() == with_export, "KEY_SPECS có sẵn thì plan_export.json không được ảnh hưởng"
    print("ok  build_spec_q: KEY_SPECS trống + plan_export.json → khối chữ chính đúng lựa chọn; KEY_SPECS điền tay → bất biến")


if __name__ == "__main__":
    test_suggest()
    test_split_beats()
    test_build_html()
    test_build_manifest_broll()
    test_export()
    test_empty_key_specs_writes_words()
    test_key_specs_from_plan_export()
    print("TẤT CẢ ĐẠT")
