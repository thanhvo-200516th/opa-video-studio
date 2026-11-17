#!/usr/bin/env python3
"""Chữ chính đa màu của hồ sơ minimal-edu (brooks_text.HeroColors, glow B3), tự co cho vừa (_fit), quote_text(hero_color),
luật edit_rules 'chữ màu ⇒ glow'. Offline.
Chạy: ~/.venvs/video-skills/bin/python tests/test_minimal_colors.py"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import brooks_text as bt  # noqa: E402
import edit_rules  # noqa: E402
import style_profile as sp  # noqa: E402
from motion_fx import GLOW, PALETTES  # noqa: E402

PROF = sp.load(name="minimal-edu")
COL = PROF["text"]["colors"]
BAD_FAMILIES = {"orange", "pink", "green"}            # B3: không cam / hồng / xanh lá
PAPER = "#E8E8F0"


def group(**kw):
    base = dict(hero="studs", before=["down", "to"], after=["the"], times=[1.0, 1.1, 1.3, 1.4], end=2.5, fps=30)
    base.update(kw)
    return bt.caption_group(**base)


def by_text(items, t):
    return next(c for _, c in items if c["text"] == t)


def glow_of(c):
    return next((e for e in c.get("effects", []) if e["effect"] == "wonder_glow"), None)


def lum(h: str) -> float:
    return edit_rules._luminance(h)


def test_rotation_alternates() -> None:
    for on_dark, key in ((True, "hero_rotation_dark"), (False, "hero_rotation_light")):
        rot = [e["color"] for e in COL[key]]
        assert len(set(rot)) == len(rot) >= 5, rot
        hc = bt.HeroColors(PROF)
        got = [hc.next(on_dark)[0] for _ in range(len(rot) * 2 + 1)]
        assert got == (rot * 3)[:len(got)], got                                    # đúng thứ tự, xoay vòng
        assert all(a != b for a, b in zip(got, got[1:])), got                      # không lặp liền
    hc = bt.HeroColors(PROF)
    assert hc.next(True)[0] != hc.next(False)[0] and hc.next(True)[0] == COL["hero_rotation_dark"][1]["color"]   # mỗi nền một con đếm
    seen = [by_text(group(colors=bt.HeroColors(PROF)), "studs")["color"] for _ in range(3)]
    assert seen == [COL["hero_rotation_dark"][0]["color"]] * 3                       # HeroColors mới → luôn bắt đầu từ màu đầu


def test_caption_group_rotates() -> None:
    hc = bt.HeroColors(PROF)
    cols = [by_text(group(colors=hc), "studs")["color"] for _ in range(4)]
    assert cols == [e["color"] for e in COL["hero_rotation_dark"][:4]], cols


def test_no_forbidden_hue_and_contrast() -> None:
    for key in ("hero_rotation_dark", "hero_rotation_light"):
        for e in COL[key]:
            fam = edit_rules.color_family(e["color"])
            assert fam not in BAD_FAMILIES, (e, fam)
            if "name" in e:
                assert e["name"] in PALETTES and edit_rules.color_family(PALETTES[e["name"]]["glow"]) not in BAD_FAMILIES, e
    assert not {e["name"] for e in COL["hero_rotation_dark"]} & {"fire", "coral", "pink", "lime"}
    for e in COL["hero_rotation_light"]:                                              # tương phản ≥ 4,5 : 1 trên giấy
        ratio = (lum(PAPER) + 0.05) / (lum(e["color"]) + 0.05)
        assert ratio >= 4.5, (e, round(ratio, 2))
    for e in COL["hero_rotation_dark"]:                                               # và đủ sáng trên nền tối
        assert (lum(e["color"]) + 0.05) / 0.05 >= 7, e


def test_coloured_hero_has_glow() -> None:
    soft = GLOW["soft"]
    for e in COL["hero_rotation_dark"]:
        h = by_text(group(color=e["color"]), "studs")
        g = glow_of(h)
        if e["name"] == "white":
            assert g is None, "trắng không phát sáng"
            continue
        p = g["params"]
        assert p["color"] == PALETTES[e["name"]]["glow"] and p["radius"] == soft["radius"], p
        assert p["intensity"][0] == [0, soft["peak"]] and p["intensity"][1][1] == soft["hold"], p
        assert 0 < p["intensity"][1][0] <= h["dur"], p
    assert glow_of(by_text(group(color="#FFFFFF"), "studs")) is None
    assert glow_of(by_text(group(on_dark=False), "studs")) is None                    # đen trên giấy: không glow
    assert glow_of(by_text(group(on_dark=False, color="#123CE8"), "studs")) is None  # màu đậm trên giấy: không glow
    two = group(hero=["the", "studs"], before=["down"], after=[], times=[1.0, 1.1, 1.3], color="#19C6F5")
    assert glow_of(by_text(two, "the")) and glow_of(by_text(two, "studs"))           # cặp 2 từ: cả hai cùng glow
    assert glow_of(by_text(group(color="#FF3FA4"), "studs"))["params"]["color"] == "#FF3FA4"   # màu lạ chỉ định tay: glow chính nó


def test_small_words_unchanged() -> None:
    hc = bt.HeroColors(PROF)
    for _ in range(3):
        items = group(colors=hc)
        for w in ("down", "to", "the"):
            c = by_text(items, w)
            assert c["color"] == COL["on_dark"] and glow_of(c) is None, c
    for _ in range(3):
        items = group(colors=hc, on_dark=False)
        for w in ("down", "to", "the"):
            assert by_text(items, w)["color"] == COL["on_paper"]
        assert "shadow" not in by_text(items, "studs")
    plain = group()                                                                    # không colors / color: hành vi cũ
    assert by_text(plain, "studs")["color"] == COL["on_dark"] and glow_of(by_text(plain, "studs")) is None
    assert by_text(group(on_dark=False, accent=True, colors=hc), "studs")["color"] == COL["accent"]   # accent trên giấy thắng vòng xoay


def test_input_not_mutated() -> None:
    before = copy.deepcopy(PROF)
    group(color="#19C6F5", zone="cap", hero="Ếỵ")
    assert PROF == before


def test_auto_fit_shrinks() -> None:
    kw = dict(hero="Ếỵ", before=["a"], after=["b"], times=[1.0, 1.1, 1.2], zone="cap")
    strict = copy.deepcopy(PROF)
    strict["text"]["auto_fit_min_hero"] = PROF["text"]["size_hero"]                  # tắt co: phải báo lỗi như cũ
    try:
        bt.caption_group(end=2.5, prof=strict, **kw)
        raise AssertionError("cần lỗi 'không vừa vùng' khi tắt tự co")
    except ValueError as e:
        assert "không vừa vùng" in str(e)
    items = bt.caption_group(end=2.5, **kw)                                           # mặc định: co thay vì báo lỗi
    h = by_text(items, "Ếỵ")
    assert PROF["text"]["auto_fit_min_hero"] <= h["size"] < PROF["text"]["size_hero"], h["size"]
    assert (PROF["text"]["size_hero"] - h["size"]) % 8 == 0 and h["position"][1] <= 1480
    floor = copy.deepcopy(PROF)
    floor["text"]["auto_fit_min_hero"] = 150                                          # sàn cao hơn mức cần co → vẫn báo lỗi
    try:
        bt.caption_group(end=2.5, prof=floor, **kw)
        raise AssertionError("dưới sàn co phải báo lỗi")
    except ValueError as e:
        assert "không vừa vùng" in str(e)


def test_span_widens() -> None:
    kw = dict(hero="AI", before=["extraordinarily"], after=["unbelievable"], times=[1.0, 1.1, 1.2], end=2.5)
    items = bt.caption_group(**kw)                                                    # trước đây: ValueError 'rộng hơn từ lớn'
    h, l, r = by_text(items, "AI"), by_text(items, "extraordinarily"), by_text(items, "unbelievable")
    assert r["position"][0] - l["position"][0] > 0 and r["position"][0] - l["position"][0] <= bt.MAX_W + 2
    assert l["position"][0] >= 540 - bt.MAX_W / 2 - 2 and r["position"][0] <= 540 + bt.MAX_W / 2 + 2     # trong B8 800 px
    assert h["size"] == PROF["text"]["size_hero"]                                     # span nới, hero không co
    try:
        bt.caption_group(hero="AI", before=["extraordinarily", "international"], after=["unbelievable"], times=[1, 1.1, 1.2, 1.3], end=2.5)
        raise AssertionError("nới tới 800 px vẫn không vừa phải báo lỗi")
    except ValueError as e:
        assert "rộng hơn" in str(e)


def test_quote_hero_color() -> None:
    lines = ["Tâm lý nhà đầu tư", "khác hẳn", "khách lẻ"]
    items = bt.quote_text(lines, False, 1.0, 3.0, hero_index=1, hero_color="#19C6F5")
    hero = by_text(items, "khác hẳn")
    assert hero["color"] == "#19C6F5" and glow_of(hero)["params"]["color"] == PALETTES["cyan"]["glow"]
    for c in (by_text(items, "Tâm lý nhà đầu tư"), by_text(items, "khách lẻ"), by_text(items, bt.OPEN_Q), by_text(items, bt.CLOSE_Q)):
        assert c["color"] == COL["on_dark"] and glow_of(c) is None, c
    plain = bt.quote_text(lines, False, 1.0, 3.0, hero_index=1)
    assert by_text(plain, "khác hẳn")["color"] == COL["on_dark"] and not glow_of(by_text(plain, "khác hẳn"))
    try:
        bt.quote_text(lines, False, 1.0, 3.0, hero_color="#19C6F5")
        raise AssertionError("hero_color không có hero_index phải báo lỗi")
    except ValueError:
        pass


def test_edit_rules_glow() -> None:
    def spec(color, glow):
        c = {"text": "tiền", "font": "Inter", "at": 1.0, "dur": 1.0, "color": color}
        if glow:
            c["effects"] = [{"effect": "wonder_glow", "params": {}}]
        return {"fps": 30, "duration": 4.0, "tracks": [{"type": "video", "name": "V1", "clips": [{"src": "a.mp4", "at": 0, "dur": 4}]},
                                                       {"type": "text", "name": "text 1", "clips": [c]}]}

    def status(color, glow):
        res = edit_rules.audit_spec(spec(color, glow), profile=PROF)
        return next(r for r in res if r["rule"] == "Chữ chính có phát sáng")["status"]

    assert status("#FFD84D", False) == "CẢNH BÁO", "chữ vàng không glow phải bị bắt"
    assert status("#19C6F5", False) == "CẢNH BÁO" and status("#18E0A8", False) == "CẢNH BÁO"
    assert status("#FFD84D", True) == "OK"
    assert status("#FFFFFF", False) == "OK" and status("#111111", False) == "OK"      # trắng / đen không glow
    assert status("#123CE8", False) == "OK"                                           # màu đậm trên giấy
    group_items = [by_text(group(color=e["color"]), "studs") for e in COL["hero_rotation_dark"]]
    for c in group_items:                                                             # chữ do brooks_text dựng luôn qua luật
        assert status(c["color"], bool(glow_of(c))) == "OK", c["color"]


if __name__ == "__main__":
    fns = sorted((k, v) for k, v in globals().items() if k.startswith("test_"))
    for name, fn in fns:
        fn()
        print("ok", name)
    print(f"TẤT CẢ ĐẠT ({len(fns)} bài kiểm)")
