#!/usr/bin/env python3
"""Kiểm plan_to_minimal.py: plan_export.json (+ words_tl.json) → minimal_plan.json {groups, scene_gfx, cta_word, pain} theo mẫu build_spec_minimal.py. Offline.
Chạy: ~/.venvs/video-skills/bin/python tests/test_plan_to_minimal.py"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import plan_doc as pd  # noqa: E402
import plan_to_minimal as pm  # noqa: E402
from test_plan_doc import export_of, synth_words, write_words  # noqa: E402

TEXT = ["Bán bất động sản tiền tỷ mà video chỉ đứng chỉ tay vào bãi đất trống.",           # cảnh 1 (a-roll)
        "Độ tin cậy tăng lên gấp mười lần so với video cắt ghép cũ kỹ.",                  # cảnh 2 (quote)
        "Họ cần nhìn thấy vị trí quy hoạch và 300 triệu dòng tiền rõ mồn một trên màn hình.",  # cảnh 3 (graph)
        "Cứ nhắn chữ Bất Động Sản ở dưới, mình gửi mẫu cấu hình sẵn."]                    # cảnh 4 (CTA)


def fixture(td: Path) -> tuple[Path, Path, list]:
    w = td / "ver" / "work"
    words = synth_words([(t, 0.4) for s in TEXT for t in s.split()])
    write_words(w, words)
    segs = [{"seq_prefix": f"{i + 1:02d}", "role_id": f"a-roll-{i}", "type": "a-roll", "display_text": s, "files": {"video_file": f"{i + 1:02d}_a.mp4"}}
            for i, s in enumerate(TEXT)]
    man = td / "m.json"
    man.write_text(json.dumps({"script_id": "X", "segments": segs}), encoding="utf-8")
    pd.main(["build", str(w), "--manifest", str(man), "--out", str(w / "p.html")])
    return w, man, words


def pick_export(w: Path, picks: dict[int, tuple[str, dict | None]], notes: dict[int, str] | None = None) -> None:
    """picks: {nhịp: (A|B|C, gfx)}."""
    draft = json.loads((w / "plan_draft.json").read_text(encoding="utf-8"))
    ex = export_of(draft, {k: v[0] for k, v in picks.items()})
    for b in ex["beats"]:
        b["scene_no"] = next(x["scene_no"] for x in draft["beats"] if x["beat"] == b["beat"])
        b["gfx"] = (picks.get(b["beat"]) or (None, None))[1]
        if notes and b["beat"] in notes:
            b["note"] = notes[b["beat"]]
    (w / "plan_export.json").write_text(json.dumps(ex, ensure_ascii=False), encoding="utf-8")


def test_convert() -> None:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        w, _, words = fixture(td)
        draft = json.loads((w / "plan_draft.json").read_text(encoding="utf-8"))
        by_scene = {}
        for b in draft["beats"]:
            by_scene.setdefault(b["scene_no"], []).append(b["beat"])
        assert sorted(by_scene) == [1, 2, 3, 4], by_scene
        b1, bq, bg, bc = by_scene[1][0], by_scene[2][0], by_scene[3][0], by_scene[4][-1]
        img = td / "tranh.png"
        img.write_bytes(b"png")
        pick_export(w, {
            b1: ("B", None),                                                                    # B → từ lớn serif ~
            bq: ("C", {"kind": "quote_paper", "scene": 2, "lines": ["Độ tin cậy", "gấp mười lần", "so với video cắt ghép"], "hero": 1, "bg": "white"}),
            bg: ("C", {"kind": "graph", "word": "vị", "scene": 3, "words": ["300", "dòng"]}),
            bc: ("A", None),
        }, notes={bc: "CTA của video"})
        (w / "pain.json").write_text(json.dumps({"pain": ["bãi đất trống"]}), encoding="utf-8")
        plan, review, warns = pm.convert(w)
        groups = plan["groups"]
        assert set(plan) == {"groups", "scene_gfx", "cta_word", "pain"} and plan["pain"] == ["bãi đất trống"]
        # None đúng một lần cho cảnh quote, và đứng giữa cụm cảnh 1 / cảnh 3; cụm khớp tuần tự với lời
        assert groups.count(None) == 1 and groups.index(None) > 0 and groups[groups.index(None) - 1] and groups[groups.index(None) + 1], groups
        assert pm.check_groups(groups, words) == [] and not [x for x in warns if "không khớp" in x], warns
        for g in filter(None, groups):
            items = [s.strip() for s in g.split("|")]
            assert sum(s[0] in "*~" for s in items) == 1 and all(len(s.lstrip("*~").split()) <= 7 for s in items), g
            assert 1 <= len(g.replace("|", " ").replace("*", "").replace("~", "").split()) <= pm.CHUNK_MAX_WORDS + 1, g
        flat = " ".join(re.sub(r"[|*~]", " ", g) for g in groups if g).split()
        spoken = [pd.norm(t) for t in " ".join([TEXT[0], TEXT[2], TEXT[3]]).split()]
        assert [pd.norm(t) for t in flat] == spoken, "cụm phải phủ hết lời của các cảnh không phải quote"
        assert any(g and "~" in g for g in groups) and any(g and "*" in g for g in groups), "B → ~ serif, A / tự động → * sans"
        # scene_gfx theo giờ, đúng thứ tự trường của kiểu
        assert plan["scene_gfx"] == [["quote_paper", 2, ["Độ tin cậy", "gấp mười lần", "so với video cắt ghép"], 1, "white"],
                                     ["graph", "vị", 3, ["300", "dòng"]]], plan["scene_gfx"]
        assert plan["cta_word"] and plan["cta_word"] in " ".join(g for g in groups if g), plan["cta_word"]   # từ lớn của nhịp CTA (đúng hoa thường)
        # từ lớn tự chọn được đánh dấu; từ lớn do người dùng chọn (B / A) thì không
        assert any(r["auto"] for r in review) and any(not r["auto"] for r in review)
        assert sum(1 for r in review if r["beat"] == b1 and not r["auto"]) == 1, [r for r in review if r["beat"] == b1]
        sc = pm.summary(json.loads((w / "plan_export.json").read_text())["beats"], review, groups)
        assert "quote_paper" in sc and "tự chọn" in sc and "cụm chữ" in sc, sc
        # ảnh thiếu → cảnh báo
        pick_export(w, {b1: ("C", {"kind": "painting", "word": "Bán", "image": str(td / "khong.png"), "secs": 3.0})})
        assert any("không thấy ảnh" in x for x in pm.convert(w)[2])
        pick_export(w, {b1: ("C", {"kind": "painting", "word": "Bán", "image": str(img), "secs": 3.0})})
        assert pm.convert(w)[0]["scene_gfx"] == [["painting", "Bán", str(img), 3.0]]
    print("ok  plan_to_minimal: cụm phủ hết lời, None cho cảnh quote, B → ~, scene_gfx đúng thứ tự trường, CTA, pain, từ lớn tự chọn đánh dấu")


def test_user_hero_and_auto() -> None:
    words = synth_words([(t, 0.3) for t in "Họ cần nhìn thấy vị trí quy hoạch và dòng tiền, rõ mồn một.".split()])
    beat = {"beat": 1, "t0": 0.0, "t1": 99.0, "scene": 0, "choice": {"ref": "stay", "kind": "stay", "scene_type": "aroll"},
            "key": {"text": "VỊ TRÍ QUY HOẠCH", "phrase": "vị trí quy hoạch", "palette": "gold", "lead": None, "script": None}}
    groups, review = pm.build_groups(words, [beat])
    assert any("*vị trí quy hoạch" in g for g in groups), groups                   # cụm người dùng đánh dấu giữ nguyên chữ gốc, một từ lớn nhiều từ
    assert [r["auto"] for r in review if r["hero"] == "vị trí quy hoạch"] == [False]
    assert any(r["auto"] for r in review) or len(groups) == 1
    assert pm.check_groups(groups, words) == []
    # chưa chọn → toàn tự động, vẫn đủ một từ lớn mỗi cụm
    groups2, review2 = pm.build_groups(words, [{**beat, "choice": None, "key": None}])
    assert groups2 and all(r["auto"] for r in review2) and pm.check_groups(groups2, words) == []
    print("ok  plan_to_minimal: từ lớn người dùng chọn giữ nguyên (không đánh dấu), phần còn lại tự chọn và đánh dấu")


def test_cta_and_cli() -> None:
    groups = ["Cứ nhắn chữ | *Bất Động Sản | ở dưới", "~chạy thử"]
    beats = [{"beat": 1, "note": "", "key": None}]
    assert pm.find_cta(beats, groups, "bất động sản") == ("Bất Động Sản", None)          # trả đúng chuỗi trong groups (mẫu so sánh hoa thường)
    word, warn = pm.find_cta(beats, groups, "Không có")
    assert word == "Không có" and warn and "không là từ lớn" in warn
    assert pm.find_cta(beats, groups, None) == (None, None)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        w, _, _ = fixture(td)
        r = subprocess.run([sys.executable, str(ROOT / "scripts/plan_to_minimal.py"), str(w)], capture_output=True, text=True)
        assert r.returncode != 0 and "plan_export.json" in (r.stderr + r.stdout), "thiếu plan_export.json → dừng, chỉ cách làm"
        pick_export(w, {1: ("A", None)})
        r = subprocess.run([sys.executable, str(ROOT / "scripts/plan_to_minimal.py"), str(w), "--cta", "chữ"], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        out = json.loads((w / "minimal_plan.json").read_text(encoding="utf-8"))
        assert out["groups"] and out["scene_gfx"] == [] and out["pain"] == [] and "cụm chữ" in r.stdout and "nhịp" in r.stdout
        assert (w / "minimal_plan_review.json").is_file()
    print("ok  plan_to_minimal: CTA khớp từ lớn / cảnh báo khi lạc; CLI in bảng tóm tắt, thiếu plan_export → dừng")


if __name__ == "__main__":
    test_convert()
    test_user_hero_and_auto()
    test_cta_and_cli()
    print("TẤT CẢ ĐẠT")
