#!/usr/bin/env python3
"""Chiều sâu cho từ lớn của hồ sơ minimal-edu (3.6.2): brooks_text.HeroLooks (glow / gradient PNG / bóng đổ sâu), nền sáng không glow,
luật edit_rules cho gradient PNG. Offline.
Chạy: ~/.venvs/video-skills/bin/python tests/test_minimal_looks.py"""
from __future__ import annotations

import copy
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import brooks_text as bt  # noqa: E402
import edit_rules  # noqa: E402
import style_profile as sp  # noqa: E402
from motion_fx import MX_SHADOW  # noqa: E402
import text_motion as tm  # noqa: E402

PROF = sp.load(name="minimal-edu")
T = PROF["text"]
GFX = Path(tempfile.mkdtemp(prefix="looks_"))
BAD_FAMILIES = {"orange", "pink", "green"}


def group(**kw):
    base = dict(hero="studs", before=["down", "to"], after=["the"], times=[1.0, 1.1, 1.3, 1.4], end=2.5, fps=30, gfx_dir=GFX)
    base.update(kw)
    return bt.caption_group(**base)


def hero(items, t="studs"):
    return next((lane, c) for lane, c in items if c.get("text", c.get("name", "")).endswith(t) and lane in ("text", "text_img"))


def glow_of(c):
    return next((e for e in c.get("effects", []) if e["effect"] == "wonder_glow"), None)


def test_rotation_cycles() -> None:
    hl = bt.HeroLooks(PROF)
    got = [hl.next(True)[0] for _ in range(len(T["hero_looks"]) * 2)]
    assert got == T["hero_looks"] * 2 and set(got) == {"glow", "gradient", "shadow_deep", "glow_shadow"}, got
    hl = bt.HeroLooks(PROF)
    pairs = [hl.next(True)[1] for _ in range(len(T["hero_looks"]))]
    assert [p for p in pairs if p] == T["gradients"]["dark"][:2], pairs             # mỗi lần gradient lấy cặp màu kế tiếp
    light = bt.HeroLooks(PROF)
    names = [light.next(False)[0] for _ in range(len(T["hero_looks"]))]
    assert set(names) == {"gradient", "shadow_light"}, names                         # nền sáng: không glow
    h = bt.HeroLooks(PROF)
    kinds = [hero(group(looks=h))[0] for _ in range(len(T["hero_looks"]))]
    assert kinds.count("text_img") == 2 and kinds.count("text") == 4, kinds          # gradient là PNG, còn lại là clip chữ


def test_profile_colours_valid() -> None:
    for stops in T["gradients"]["dark"] + T["gradients"]["light"]:
        assert 2 <= len(stops) <= 3
        for c in stops:
            assert edit_rules.color_family(c) not in BAD_FAMILIES, c                  # B3: không cam / hồng / xanh lá
    for stops in T["gradients"]["light"]:                                             # nền giấy #E8E8F0: đủ đậm
        assert all((edit_rules._luminance("#E8E8F0") + 0.05) / (edit_rules._luminance(c) + 0.05) >= 4.5 for c in stops), stops


def test_gradient_png_and_clip() -> None:
    _, c = hero(group(look="gradient", hero="Tiền Ếỵ"), "Tiền Ếỵ")
    im = Image.open(c["src"])
    assert im.size == (1080, 1920) and im.mode == "RGBA" and im.getchannel("A").getbbox(), im
    assert Path(c["src"]).parent == GFX
    items = group(look="gradient")
    lane, c = hero(items)
    assert lane == "text_img" and c["dur"] > 0 and c["opacity"][0] == [0, 0] and c["opacity"][-1][1] == 100
    blur = c["effects"][0]
    assert blur["effect"] == "gaussian_blur" and blur["params"]["blurriness"][0] == [0, tm.KIN["blur_from"]] and blur["params"]["blurriness"][1][1] == 0
    assert [e["effect"] for e in c["effects"]] == ["gaussian_blur", "transform", "wonder_glow"]   # PNG gradient cũng vào mượt
    assert glow_of(c) and glow_of(c)["params"]["radius"] == bt.GLOW_LEVEL["soft"]["radius"]    # gradient: glow nhẹ
    plain = hero(group())[1]
    assert (c["at"], c["dur"]) == (plain["at"], plain["dur"])                                # cùng thời gian với clip chữ
    bbox = Image.open(c["src"]).getchannel("A").getbbox()
    assert abs((bbox[0] + bbox[2]) / 2 - plain["position"][0]) < 25, (bbox, plain["position"])   # đúng tâm
    assert bbox[3] > plain["position"][1] - 5 and bbox[3] < plain["position"][1] + plain["size"] * 0.35   # baseline ≈ vị trí clip chữ
    try:
        group(look="gradient", gfx_dir=None)
        raise AssertionError("gradient thiếu gfx_dir phải báo lỗi")
    except ValueError:
        pass
    two = group(look="gradient", hero=["the", "studs"], before=["down"], after=[], times=[1.0, 1.1, 1.3])
    assert [lane for lane, _ in two if lane == "text_img"] == ["text_img", "text_img"]    # cặp 2 từ: 2 PNG, từ hai trễ
    assert two[2][1]["at"] > two[1][1]["at"]


def test_gradient_rendered_colours() -> None:
    _, c = hero(group(look="gradient"))
    im = Image.open(c["src"]).convert("RGBA")
    x0, y0, x1, y1 = im.getchannel("A").getbbox()
    row = [im.getpixel((x, (y0 + y1) // 2)) for x in range(x0 + 4, x1 - 4)]
    solid = [p for p in row if p[3] == 255]
    assert solid and solid[0][:3] != solid[-1][:3], "gradient phải đổi màu từ trái sang phải"


def test_shadow_deep_no_outline() -> None:
    for name in ("shadow_deep", "glow_shadow", "glow"):
        lane, c = hero(group(look=name))
        assert lane == "text" and "stroke" not in c and "outline" not in c and not any(k in c for k in ("stroke", "outline", "border")), c
        assert "stroke" not in c.get("shadow", {}) and set(c["shadow"]) <= {"color", "opacity", "blur", "distance", "angle", "size"}
    sd = hero(group(look="shadow_deep"))[1]
    assert sd["shadow"] == T["look_shadows"]["deep"] and sd["shadow"]["opacity"] >= 80 and sd["shadow"]["blur"] >= 16
    assert glow_of(sd) is None                                                              # chỉ bóng, không glow
    gs = hero(group(look="glow_shadow"))[1]
    assert glow_of(gs) and gs["shadow"] == T["look_shadows"]["deep"]


def test_glow_normal_level() -> None:
    c = hero(group(look="glow", color="#19C6F5"))[1]
    g = glow_of(c)["params"]
    assert g["radius"] == bt.GLOW_LEVEL["normal"]["radius"] and g["intensity"][0][1] == bt.GLOW_LEVEL["normal"]["peak"] and g["intensity"][1][1] == bt.GLOW_LEVEL["normal"]["hold"], g
    assert c["shadow"] == MX_SHADOW
    white = hero(group(look="glow", color="#FFFFFF"))[1]
    assert glow_of(white), "chữ trắng + kiểu glow vẫn phát sáng"
    eff = [e["effect"] for e in c["effects"]]
    assert eff == ["gaussian_blur", "transform", "wonder_glow"], eff                       # blur-in + dời / phóng, glow ở sau cùng


def test_light_background_no_glow() -> None:
    for name in ("glow", "glow_shadow", "shadow_deep"):
        lane, c = hero(group(look=name, on_dark=False))
        assert lane == "text" and glow_of(c) is None, name
        assert c["shadow"] == T["look_shadows"]["light"] and c["shadow"]["opacity"] < 50
    hl = bt.HeroLooks(PROF)
    for _ in range(len(T["hero_looks"])):
        lane, c = hero(group(looks=hl, on_dark=False, colors=bt.HeroColors(PROF)), "studs")
        assert glow_of(c) is None, c
        if lane == "text_img":
            assert c["name"].startswith(bt.LIGHT_TAG) and bt.LIGHT_TAG == edit_rules.LIGHT_GRADIENT_TAG
    dark_stops = T["gradients"]["light"]
    assert hero(group(look="gradient", on_dark=False))[1]["name"].startswith(bt.LIGHT_TAG) and dark_stops


def test_explicit_look_overrides() -> None:
    hl = bt.HeroLooks(PROF)
    c = hero(group(looks=hl, look="shadow_deep"))[1]
    assert c["shadow"] == T["look_shadows"]["deep"] and hl.next(True)[0] == T["hero_looks"][0]   # look chỉ định tay không tiêu vòng xoay
    try:
        group(look="stroke")
        raise AssertionError("look lạ phải báo lỗi")
    except ValueError:
        pass


def test_default_unchanged() -> None:
    items = group(gfx_dir=None)
    h = hero(items)[1]
    assert h["shadow"] == __import__("text_fx").SHADOW and glow_of(h) is None
    assert group(gfx_dir=None) == bt.caption_group(hero="studs", before=["down", "to"], after=["the"], times=[1.0, 1.1, 1.3, 1.4], end=2.5, fps=30)


def test_input_not_mutated() -> None:
    before = copy.deepcopy(PROF)
    group(looks=bt.HeroLooks(PROF), colors=bt.HeroColors(PROF))
    group(look="gradient")
    assert PROF == before


def test_quote_hero_line_look() -> None:
    lines = ["Tâm lý nhà đầu tư", "khác hẳn", "khách lẻ"]
    items = bt.quote_text(lines, False, 1.0, 3.0, hero_index=1, look="gradient", gfx_dir=GFX)
    lanes = [lane for lane, _ in items]
    assert lanes.count("text_img") == 1
    g = next(c for lane, c in items if lane == "text_img")
    assert "khác hẳn" in g["name"] and Image.open(g["src"]).size == (1080, 1920)
    assert all(c.get("color") == "#FFFFFF" for lane, c in items if lane != "text_img" and c["text"] != "khác hẳn")   # dòng khác vẫn trắng
    sd = bt.quote_text(lines, False, 1.0, 3.0, hero_index=1, look="shadow_deep")
    assert next(c for _, c in sd if c["text"] == "khác hẳn")["shadow"] == T["look_shadows"]["deep"]
    try:
        bt.quote_text(lines, False, 1.0, 3.0, look="glow")
        raise AssertionError("look không có hero_index phải báo lỗi")
    except ValueError:
        pass


def test_edit_rules_gradient_png() -> None:
    def audit(clips_text, clips_img):
        spec = {"fps": 30, "duration": 4.0, "tracks": [{"type": "video", "name": "V1", "clips": [{"src": "a.mp4", "at": 0, "dur": 4}]},
                                                       {"type": "text", "name": "text 1", "clips": clips_text},
                                                       {"type": "video", "name": "text_img 1", "clips": clips_img}]}
        res = edit_rules.audit_spec(spec, profile=PROF)
        return {r["rule"]: r["status"] for r in res}

    small = {"text": "to", "font": "Inter", "at": 1.0, "dur": 1.0, "color": "#FFFFFF"}
    serif = {"text": "a", "font": "Playfair Display", "at": 1.0, "dur": 1.0, "color": "#FFFFFF"}
    items = group(look="gradient")
    png = hero(items)[1]
    st = audit([small, serif], [png])
    assert st["Chữ chính có phát sáng"] == "OK" and st["Font 2-3 mỗi video (P8)"] == "OK", st        # PNG gradient không làm tăng số font
    nog = {k: v for k, v in png.items() if k != "effects"}
    assert audit([small, serif], [nog])["Chữ chính có phát sáng"] == "CẢNH BÁO"                        # PNG màu trên nền tối không glow bị bắt
    lp = hero(group(look="gradient", on_dark=False))[1]
    assert glow_of(lp) is None and audit([small, serif], [lp])["Chữ chính có phát sáng"] == "OK"      # gradient nền sáng: không đòi glow
    assert audit([small, serif], [])["Font 2-3 mỗi video (P8)"] == "OK"


if __name__ == "__main__":
    fns = sorted((k, v) for k, v in globals().items() if k.startswith("test_"))
    for name, fn in fns:
        fn()
        print("ok", name)
    print(f"TẤT CẢ ĐẠT ({len(fns)} bài kiểm)")
