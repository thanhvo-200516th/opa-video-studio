#!/usr/bin/env python3
"""C2 (v2.5): phụ đề liên tiếp không chồng nhau — mờ dần (cross_dissolve, tâm ở cuối clip) kéo dài thêm OUT_FADE/2 khung
sau cuối clip, nên cụm ra bằng mờ dần phải kết thúc sớm đúng chừng đó; spec_lint có mục SOFT `caption_overlap`; ảnh bìa A6.
Chạy: ~/.venvs/video-skills/bin/python tests/test_captions_overlap.py"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import motion_fx  # noqa: E402
from edit_rules import audit_spec  # noqa: E402
from motion_fx import OUT_FADE, MotionFX  # noqa: E402
from spec_lint import check_caption_overlap  # noqa: E402

FPS = 30
HALF = OUT_FADE / 2 / FPS


def words(n_sent: int = 4, per: int = 6, step: float = 0.35) -> list[tuple[str, float]]:
    """Lời liền mạch: các câu nối nhau không có khoảng lặng (trường hợp cụm sau vào ngay sau cụm trước)."""
    out, t = [], 0.0
    for s in range(n_sent):
        for i in range(per):
            out.append((f"từ{s}{i}" + ("." if i == per - 1 else ""), round(t, 3)))
            t += step
    return out


def text_low_groups(fx: MotionFX) -> list[list[dict]]:
    """Gom các clip text_low theo giờ kết thúc (hai dòng của một cụm kết thúc cùng lúc)."""
    clips = [c for lane, c in fx.items if lane == "text_low"]
    by_end: dict[float, list[dict]] = {}
    for c in clips:
        by_end.setdefault(round(c["at"] + c["dur"], 3), []).append(c)
    return [by_end[k] for k in sorted(by_end)]


def test_no_overlap() -> None:
    with tempfile.TemporaryDirectory() as td:
        fx = MotionFX(gfx_dir=Path(td), fps=FPS, name="T")
        w = words()
        fx.captions2(w, w[-1][1] + 0.4, style="mont", entrance="blur")
        groups = text_low_groups(fx)
        assert len(groups) >= 3, len(groups)
        checked = 0
        for g1, g2 in zip(groups, groups[1:]):
            faded = [c for c in g1 if c.get("transition_out")]
            if not faded:
                continue
            end = g1[0]["at"] + g1[0]["dur"]
            frames = faded[0]["transition_out"]["frames"]
            nxt = min(c["at"] for c in g2)
            assert end + frames / 2 / FPS <= nxt + 1e-6, f"chồng {end + frames / 2 / FPS - nxt:.3f} s: {end} → {nxt}"
            checked += 1
        assert checked >= 2, "không có cụm nào ra bằng mờ dần để kiểm"
    print("ok  C2: cụm ra bằng mờ dần kết thúc sớm OUT_FADE/2 khung → không chồng cụm sau")


def test_replace_directly_keeps_length() -> None:
    """Cụm sau thay thẳng (không mờ) giữ nguyên: kết thúc ở nextstart − 0,05, không bị rút thêm."""
    with tempfile.TemporaryDirectory() as td:
        fx = MotionFX(gfx_dir=Path(td), fps=FPS, name="T")
        w = [(f"w{i}" + ("," if i % 5 == 4 else ""), round(i * 0.3, 3)) for i in range(15)]   # chỉ dấu phẩy, không hết câu
        fx.captions2(w, 5.0, style="mont", entrance="blur")
        groups = text_low_groups(fx)
        silent = [g for g in groups if not any(c.get("transition_out") for c in g)]
        assert silent, "phải có cụm thay thẳng (không mờ)"
        for g1, g2 in zip(groups, groups[1:]):
            if not any(c.get("transition_out") for c in g1):
                end, nxt = g1[0]["at"] + g1[0]["dur"], min(c["at"] for c in g2)
                assert abs(nxt - end - 0.05) < 0.04 or nxt - end <= 0.1, (end, nxt)
    print("ok  C2: cụm thay thẳng không bị rút ngắn")


def test_per_row_calls() -> None:
    """J-1 #7: build_spec_q gọi captions2 TỪNG HÀNG với end = giờ vào của hàng sau; cụm cuối mỗi hàng ra bằng mờ dần
    cũng phải kết thúc sớm OUT_FADE/2 khung (trước v2.6 nó kết thúc đúng giờ hàng sau vào → chồng, 5 chỗ ở bản chạy thử 2)."""
    w = words(n_sent=4, per=12, step=0.3)
    rows = [w[i:i + 12] for i in range(0, len(w), 12)]                  # hàng 12 từ, không dấu câu giữa hàng → ranh giới hàng giữa câu
    rows = [[(a.rstrip("."), t) for a, t in r] for r in rows]
    with tempfile.TemporaryDirectory() as td:
        fx = MotionFX(gfx_dir=Path(td), fps=FPS, name="T")
        for i, r in enumerate(rows):
            fx.captions2(r, rows[i + 1][0][1] - 0.04 if i + 1 < len(rows) else w[-1][1] + 0.5, style="mont", entrance="blur")
        clips = [("FX · text_low 1", c) for lane, c in fx.items if lane == "text_low"]
        spec = {"fps": FPS, "duration": 20, "tracks": [{"type": "text", "name": "FX · text_low 1", "clips": [c for _, c in clips]}]}
        r = check_caption_overlap(spec, clips)[0]
        assert r["status"] == "OK", r
    print("ok  C2 v2.6: gọi captions2 từng hàng → 0 caption_overlap ở chỗ nối hàng")


def spec_with(clips: list[dict]) -> dict:
    return {"fps": FPS, "duration": 6, "tracks": [{"type": "text", "name": "FX · text_low 1", "clips": clips}]}


def test_lint_soft() -> None:
    f = {"effect": "cross_dissolve", "frames": OUT_FADE}
    bad = spec_with([{"text": "a", "at": 0.0, "dur": 1.0, "transition_out": f}, {"text": "b", "at": 1.05, "dur": 1.0}])
    r = check_caption_overlap(bad, [(t["name"], c) for t in bad["tracks"] for c in t["clips"]])[0]
    assert r["id"] == "caption_overlap" and r["status"] == "SOFT", r
    good = spec_with([{"text": "a", "at": 0.0, "dur": 1.0, "transition_out": f}, {"text": "b", "at": 1.2, "dur": 1.0}])
    r = check_caption_overlap(good, [(t["name"], c) for t in good["tracks"] for c in t["clips"]])[0]
    assert r["status"] == "OK", r
    two_lines = spec_with([{"text": "a", "at": 0.0, "dur": 1.0, "transition_out": f},
                           {"text": "a2", "at": 0.15, "dur": 0.85, "transition_out": f}])      # hai dòng của cùng một cụm
    r = check_caption_overlap(two_lines, [(t["name"], c) for t in two_lines["tracks"] for c in t["clips"]])[0]
    assert r["status"] == "OK", r
    print("ok  C2: spec_lint caption_overlap SOFT khi chồng, OK khi đủ chỗ, không nhầm hai dòng cùng cụm")


def test_cover() -> None:
    with tempfile.TemporaryDirectory() as td:
        fx = MotionFX(gfx_dir=Path(td), fps=FPS, name="T")
        c = fx.cover("/tmp/cover.png")
        assert c["name"].startswith("Ảnh bìa") and abs(c["dur"] - 0.3) < 1e-6 and c["at"] == 0.0, c
        op = {round(k[0], 2): k[1] for k in c["opacity"]}
        assert op == {0.0: 100, 0.2: 100, 0.28: 0}, c["opacity"]
        spec = {"fps": FPS, "duration": 5, "tracks": [{"type": "video", "name": "FX · gfx_over 1", "clips": [c]}]}
        r = {x["rule"]: x["status"] for x in audit_spec(spec)}
        assert r["Ảnh bìa ≤ 0,3 s đầu video"] == "OK", r
    assert "cover" in motion_fx.MotionFX.__dict__
    print("ok  C6: MotionFX.cover 0,3 s, mờ hết ở 0,28 s, audit A6 đạt")


if __name__ == "__main__":
    test_no_overlap()
    test_replace_directly_keeps_length()
    test_per_row_calls()
    test_lint_soft()
    test_cover()
    print("TẤT CẢ ĐẠT")
