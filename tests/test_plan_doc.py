#!/usr/bin/env python3
"""Kiểm A1 (build_spec_q: KEY_SPECS trống → ghi words_tl.json rồi thoát sạch; có plan_export.json → sinh KEY_SPECS),
A2 (plan_doc.py build / export) và A3 (suggest: stay | show | close). Offline.
Chạy: ~/.venvs/video-skills/bin/python tests/test_plan_doc.py"""
from __future__ import annotations

import json
import os
import re
import shutil
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


# ---------------------------------------------------------------- B (minimal): meaning, gfx, library
def build_in(td: str, extra: list[str] | None = None, words: list | None = None) -> tuple[Path, dict, str]:
    w = Path(td) / "ver" / "work"
    write_words(w, words or sample_words())
    out = w / "p.html"
    assert pd.main(["build", str(w), "--out", str(out), *(extra or [])]) == 0
    return w, json.loads((w / "plan_draft.json").read_text(encoding="utf-8")), out.read_text(encoding="utf-8")


def test_meaning_suggestion() -> None:
    with tempfile.TemporaryDirectory() as td:
        _, base, _ = build_in(td)
        n = len(base["beats"])
        assert all(b["suggest_by"] == "keywords" and b["meaning"] is None for b in base["beats"])
        labels = ["number_data", "process_steps", "emotion", "describe_person", "story", "describe_object", "conclusion", "intro_new_concept"]
        mf = Path(td) / "beats_meaning.json"
        mf.write_text(json.dumps([{"beat": i + 1, "label": labels[i], "why": f"vì {i}"} for i in range(min(n, 2))]))   # chỉ 2 nhịp đầu
        _, d, _ = build_in(td, ["--meaning", str(mf)])
        assert (d["beats"][0]["suggest"], d["beats"][0]["gfx_kind"], d["beats"][0]["suggest_by"]) == ("C", "graph", "meaning"), d["beats"][0]
        assert (d["beats"][1]["suggest"], d["beats"][1]["gfx_kind"]) == ("C", "path_illus") and "vì 1" in d["beats"][1]["suggest_why"]
        assert all(b["suggest_by"] == "keywords" for b in d["beats"][2:]), "nhịp không có nhãn → quay về từ khoá"
        assert d["beats"][2]["suggest"] == base["beats"][2]["suggest"]
        # mọi nhãn đều có ánh xạ; emotion → B, intro → A, conclusion → C quote_paper
        assert {pd.MEANING_MAP[k][0] for k in ("emotion", "intro_new_concept")} == {"B", "A"} and pd.MEANING_MAP["conclusion"] == ("C", "quote_paper")
        assert set(pd.MEANING_MAP) == set(labels) and all(k in pd.GFX_KINDS for _, k in pd.MEANING_MAP.values() if k)
        for bad in ([{"beat": 1, "label": "tùy tiện"}], [{"beat": 99, "label": "emotion"}], {"x": 1}):
            mf.write_text(json.dumps(bad))
            try:
                pd.main(["build", str(Path(td) / "ver" / "work"), "--meaning", str(mf), "--out", str(Path(td) / "x.html")])
            except SystemExit as e:
                assert str(e) and "Traceback" not in str(e)
            else:
                raise AssertionError(f"meaning hỏng phải bị từ chối: {bad}")
        mf.write_text(json.dumps({"beats": [{"beat": 1, "label": "emotion"}]}))                            # dạng {"beats": [...]} cũng nhận
        assert build_in(td, ["--meaning", str(mf)])[1]["beats"][0]["suggest"] == "B"
    print("ok  plan_doc --meaning: nhãn nghĩa → gợi ý A/B/C + kiểu đồ hoạ; thiếu nhãn → từ khoá; file sai → dừng rõ ràng")


def test_gfx_block_and_validation() -> None:
    with tempfile.TemporaryDirectory() as td:
        w, d, html = build_in(td)
        assert d["gfx_kinds"].keys() >= {"polaroid", "arrow", "graph", "quote", "cutaway", "painting", "path_text", "path_illus", "illus_mid",
                                         "illus_side", "quote_paper"}
        assert "gfxBlock" in html and 'id="data"' in html
        b = d["beats"][1]
        assert b["options"][2]["gfx"] is True and b["gfx_defaults"]["word"] and b["gfx_defaults"]["scene"] == 1 and b["gfx_defaults"]["lines"]
        assert b["options"][1]["kind"] == "keyword" and "serif" in b["options"][1]["desc"] and "sans" in b["options"][0]["desc"]
        words = pd.load_words(w)
        base = {"beat": 2, "t0": b["t0"], "t1": b["t1"]}
        w0 = b["gfx_defaults"]["word"]
        good = {"kind": "graph", "word": w0, "scene": 1, "words": ["300", "5"]}
        assert pd.validate_gfx(good, base, words) == []
        for bad in ({**good, "kind": "lạ"}, {**good, "words": []}, {**good, "scene": 0}, {**good, "word": "không-có-trong-lời"},
                    {"kind": "quote", "scene": 1, "lines": ["a", "b"], "hero": 2}, {"kind": "illus_side", "word": w0, "image": "x.png", "side": "up"},
                    {"kind": "painting", "word": w0, "image": "", "secs": 3}, {"kind": "polaroid", "scene": 1, "secs": -1}):
            assert pd.validate_gfx(bad, base, words), bad
        assert pd.validate_gfx({"kind": "path_illus", "word": w0, "image": "a.png", "style": "zigzag"}, base, words) == []
        # export nhận gfx hợp lệ, từ chối gfx lạc chỗ
        ex = export_of(d, {1: "A", 2: "C"})
        ex["beats"][1]["gfx"] = good
        f = Path(td) / "dl.json"
        f.write_text(json.dumps(ex))
        assert pd.main(["export", str(f), str(w)]) == 0
        assert json.loads((w / "plan_export.json").read_text())["beats"][1]["gfx"]["kind"] == "graph"
        ex["beats"][0]["gfx"] = good
        f.write_text(json.dumps(ex))
        try:
            pd.main(["export", str(f), str(w)])
        except SystemExit as e:
            assert "gfx" in str(e)
        else:
            raise AssertionError("gfx trên phương án A phải bị từ chối")
    print("ok  plan_doc: phương án C có ô chọn kiểu đồ hoạ + trường; export kiểm gfx (kind / trường / từ trong lời / hero)")


def make_library(root: Path) -> Path:
    from PIL import Image
    style = root / "minimal-edu"
    entries = []
    for i, (kind, pr) in enumerate([("caption", 1), ("text_motion", None), ("graph", 10), ("painting", 3), ("object", 9), ("quote", 6)]):
        eid = f"V01-A{i:02d}"
        (style / eid).mkdir(parents=True)
        Image.effect_noise((900, 1600), 90).convert("RGB").save(style / eid / "still.png")      # nhiễu → JPEG khó nén, thử giới hạn 30 KB
        entries.append({"id": eid, "principle": pr, "kind": kind, "title": f"mẫu {kind}", "t": [0, 1], "still": f"{eid}/still.png"})
    (style / "index.json").write_text(json.dumps({"style": "minimal-edu", "entries": entries}))
    return root


def test_library_previews() -> None:
    try:
        import PIL  # noqa: F401
    except ImportError:
        print("bỏ qua test_library_previews: không có PIL")
        return
    with tempfile.TemporaryDirectory() as td:
        lib_root = make_library(Path(td) / "lib")
        _, d, html = build_in(td, ["--library", str(lib_root)])
        lib = d["library"]
        assert lib and set(lib) >= {"items", "A", "B", "gfx"}
        assert lib["A"] and lib["B"] and lib["gfx"]["graph"] and lib["gfx"]["painting"] and lib["gfx"]["polaroid"] and lib["gfx"]["quote_paper"]
        assert not lib["gfx"]["illus_mid"], "không có entry khớp → để trống, không bịa"
        for it in lib["items"].values():
            assert it["img"].startswith("data:image/jpeg;base64,") and len(it["img"]) * 3 // 4 <= pd.THUMB_MAX_BYTES + 300, len(it["img"])
        assert "SEEN IN THE REELS" in html and not re.search(r"""(?:src|href)=["']?(?:https?:)?//""", html)
        # env OPA_LIBRARY_DIR
        old = os.environ.get("OPA_LIBRARY_DIR")
        os.environ["OPA_LIBRARY_DIR"] = str(lib_root)
        try:
            assert build_in(td)[1]["library"]["items"]
        finally:
            os.environ.pop("OPA_LIBRARY_DIR", None) if old is None else os.environ.__setitem__("OPA_LIBRARY_DIR", old)
        os.environ["OPA_LIBRARY_DIR"] = str(Path(td) / "khong-co")
        try:
            assert build_in(td)[1]["library"] is None, "không có thư viện → build vẫn chạy"
        finally:
            os.environ.pop("OPA_LIBRARY_DIR")
    print("ok  plan_doc: thư viện hiệu ứng → ảnh nhỏ ≤ 30 KB nhúng base64 theo kind / nguyên tắc; không có thư viện → bỏ qua")


def test_html_runs_in_browser() -> None:
    """Chạy JS thật (playwright + Chrome có sẵn): chọn C, đổi kiểu, điền trường, xuất JSON → plan_export hợp lệ. Bỏ qua nếu không có trình duyệt."""
    try:
        from playwright.sync_api import sync_playwright
        import PIL  # noqa: F401
    except ImportError:
        print("bỏ qua test_html_runs_in_browser: thiếu playwright / PIL")
        return
    with tempfile.TemporaryDirectory() as td:
        lib_root = make_library(Path(td) / "lib")
        w, d, _ = build_in(td, ["--library", str(lib_root)])
        try:
            with sync_playwright() as p:
                chrome = next((c for c in (shutil.which("google-chrome"), shutil.which("chromium")) if c), None)
                br = p.chromium.launch(executable_path=chrome) if chrome else p.chromium.launch()
                pg = br.new_page()
                errors: list[str] = []
                pg.on("pageerror", lambda e: errors.append(str(e)))
                pg.goto((w / "p.html").as_uri())
                assert pg.locator("h4:text('SEEN IN THE REELS')").count() >= 2
                pg.locator(".beat").nth(1).locator("button:text('Chọn phương án này')").nth(2).click()      # chọn C của nhịp 2
                card = pg.locator(".beat").nth(1)
                card.locator(".gfx select").first.select_option("graph")
                card.locator(".gfx input[type=text]").nth(2).fill("300, 5 triệu")
                with pg.expect_download() as dl:
                    pg.click("#bExport")
                out = Path(td) / "dl.json"
                dl.value.save_as(out)
                br.close()
        except Exception as e:                                           # không có Chrome / sandbox → không phải lỗi mã
            if "Executable doesn't exist" in str(e) or "launch" in str(e).lower():
                print("bỏ qua test_html_runs_in_browser:", str(e)[:80])
                return
            raise
        assert not errors, errors
        data = json.loads(out.read_text())
        c2 = data["beats"][1]
        assert c2["choice"]["kind"] == "gfx" and c2["gfx"]["kind"] == "graph" and c2["gfx"]["words"] == ["300", "5 triệu"], c2
        assert c2["scene_no"] == 1 and data["beats"][0]["gfx"] is None
        assert pd.main(["export", str(out), str(w)]) == 0, "file JS xuất ra phải qua kiểm của export"
    print("ok  plan_doc HTML (trình duyệt thật): chọn C → chọn kiểu graph → điền trường → xuất JSON → export chấp nhận")


if __name__ == "__main__":
    test_suggest()
    test_split_beats()
    test_build_html()
    test_build_manifest_broll()
    test_export()
    test_empty_key_specs_writes_words()
    test_key_specs_from_plan_export()
    test_meaning_suggestion()
    test_gfx_block_and_validation()
    test_library_previews()
    test_html_runs_in_browser()
    print("TẤT CẢ ĐẠT")
