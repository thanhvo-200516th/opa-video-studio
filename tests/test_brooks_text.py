#!/usr/bin/env python3
"""Kiểm brooks_text.py (cụm chữ Brooks: sandwich, tỉ lệ, lịch vào, màu, vùng chữ B8, quote card) và
text_motion.ensure_motion(profile=...) của hồ sơ minimal-edu. Offline.
Chạy: ~/.venvs/video-skills/bin/python tests/test_brooks_text.py"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_profile as sp  # noqa: E402
import text_motion as tm  # noqa: E402
from PIL import ImageFont  # noqa: E402

PROF = sp.load(name="minimal-edu")
FPS = 30
F = 1 / FPS
T = lambda k: PROF["text"][k]  # noqa: E731


def sample_items() -> list:
    """Mẫu cố định cho kiểm không hồi quy (profile=None)."""
    return [
        ("text", {"text": "a", "at": 1.0, "dur": 1.5, "position": [540, 500], "size": 150}),
        ("text_low", {"text": "b", "at": 1.0, "dur": 1.0, "position": [300, 460], "size": 48}),
        ("text", {"text": "c", "at": 2.0, "dur": 1.2, "opacity": [[0, 0], [0.15, 100]]}),
        ("text_top", {"text": "d", "at": 3.0, "dur": 2.0, "transition_out": {"type": "fade"}}),
        ("text", {"text": "e", "at": 4.0, "dur": 0.2}),
        ("card", {"src": "x.png", "at": 0.0, "dur": 3.0}),
    ]


# SHA-256 của kết quả ensure_motion(sample_items(), 30) lúc chưa thêm profile (đo trên mã gốc)
GOLDEN = "ab606c4695ac540c6997a4430cf73858084b91f3949fdb129c7c7c4c4485b8d5"


def digest(items, n) -> str:
    return hashlib.sha256(json.dumps([items, n], sort_keys=True, default=str).encode()).hexdigest()


def test_motion_no_regression() -> None:
    a = sample_items()
    n = tm.ensure_motion(a, 30.0)
    assert digest(a, n) == GOLDEN, "profile=None phải giống hệt bản cũ"
    for prof in (None, {"name": "dviet"}):          # hồ sơ lạ / không bật = như None
        b = sample_items()
        assert tm.ensure_motion(b, 30.0, profile=prof) == n and b == a


def last_key(c, name="opacity"):
    return c[name][-1]


def test_motion_profile() -> None:
    items = [("text", {"text": "x", "at": 2.0, "dur": 1.5}), ("text_low", {"text": "y", "at": 2.0, "dur": 1.5})]
    n = tm.ensure_motion(items, FPS, profile=PROF, cuts=[3.5])
    key, cap = items[0][1], items[1][1]
    exit_f = T("exit_frames")
    end_f = T("end_before_cut_frames")[1]
    assert n["in"] == 2 and n["out"] == 2 and n["trim"] == 2, n
    for c in (key, cap):                              # kết thúc đúng end_before_cut khung trước cắt; ra mờ 2 khung
        assert abs(c["at"] + c["dur"] - (3.5 - end_f * F)) < 1e-6, c["dur"]
        (t1, v1), (t0, v0) = c["opacity"][-1][:2], c["opacity"][-2][:2]
        assert v1 == 0 and abs((t1 - t0) - exit_f * F) < 1e-6, c["opacity"]
        assert all(k[1] == 0 or k[0] < 0.2 for e in c["effects"] if e["effect"] == "gaussian_blur"
                   for k in e["params"]["blurriness"])               # ra không nhoè: blur chỉ ở đầu clip (vào)
    blur = lambda c: next(e for e in c["effects"] if e["effect"] == "gaussian_blur")["params"]["blurriness"]  # noqa: E731
    lo, hi = T("hero_blur_in_frames")[0], T("small_in_frames")
    assert abs(blur(key)[-1][0] - lo * F) < 1e-6 and blur(key)[-1][1] == 0         # chữ chính: khung của hero
    assert hi[0] <= round(blur(cap)[-1][0] * FPS) <= hi[1] and blur(cap)[-1][1] == 0  # chữ phụ: khung của chữ nhỏ
    assert all(k[0] <= blur(c)[-1][0] + 1e-9 for c in (key, cap) for k in c["opacity"][:2])


def test_motion_profile_no_cut_and_own_exit() -> None:
    c = ("text", {"text": "x", "at": 2.0, "dur": 1.5})
    items = [c]
    tm.ensure_motion(items, FPS, profile=PROF)           # không biết điểm cắt → ra ngay cuối clip, dur giữ nguyên
    assert c[1]["dur"] == 1.5 and abs(c[1]["opacity"][-1][0] - 1.5) < 1e-9
    assert abs(c[1]["opacity"][-1][0] - c[1]["opacity"][-2][0] - 2 * F) < 1e-6
    own = ("text", {"text": "d", "at": 3.0, "dur": 2.0, "transition_out": {"type": "fade"}})
    tm.ensure_motion([own], FPS, profile=PROF, cuts=[5.0])   # đã có ra riêng → không cắt dur
    assert own[1]["dur"] == 2.0


# ---------------------------------------------------------------- brooks_text
import brooks_text as bt  # noqa: E402


def meter(font_key: str, size: int):
    spec = PROF["fonts"][font_key]
    path = ROOT / spec["file"] if (ROOT / spec["file"]).exists() else Path.home() / ".local/share/fonts" / spec["file"]
    return ImageFont.truetype(str(path), size)


def ink_w(font_key: str, size: int, text: str, tracking: float) -> float:
    b = meter(font_key, size).getbbox(text, anchor="ls")
    return b[2] - b[0] + tracking / 1000 * size * max(0, len(text) - 1)


def group(**kw):
    base = dict(hero="studs", before=["down", "to"], after=["the"], times=[1.0, 1.1, 1.3, 1.4], end=2.5, fps=FPS)
    base.update(kw)
    return bt.caption_group(**base)


def by_text(items, t):
    return next(c for _, c in items if c["text"] == t)


def test_fonts() -> None:
    for n in ("Inter-ExtraBold.ttf", "Inter-Medium.ttf", "OFL.txt"):
        assert (ROOT / "assets/fonts" / n).is_file(), n
    for key, name in (("hero_sans", "ExtraBold"), ("small", "Medium")):
        assert meter(key, 50).getname() == ("Inter", name), key


def test_sandwich_and_ratio() -> None:
    for hero in ("studs", "kiến thức", "extraordinarily"):
        items = group(hero=hero, before=["down"], after=["to"], times=[1.0, 1.1, 1.3])
        h, l, r = by_text(items, hero), by_text(items, "down"), by_text(items, "to")
        w = ink_w("hero_sans", h["size"], hero, h["tracking"])
        assert w <= 800 + 1, w                                  # vừa rộng ≤ 800 (B8)
        left, right = h["position"][0] - w / 2, h["position"][0] + w / 2
        assert l["align"] == "left" and abs(l["position"][0] - left) <= 2, (l["position"], left)
        assert r["align"] == "right" and abs(r["position"][0] - right) <= 2, (r["position"], right)
        assert l["position"][1] == r["position"][1] < h["position"][1]
        assert T("ratio_min") <= h["size"] / l["size"] <= T("ratio_max"), (h["size"], l["size"])
    items = group(span_ratio=0.75, hero="studs", before=["down"], after=["to"], times=[1.0, 1.1, 1.3])
    h, l = by_text(items, "studs"), by_text(items, "down")
    w = ink_w("hero_sans", h["size"], "studs", h["tracking"])
    assert abs(l["position"][0] - (540 - 0.75 * w / 2)) <= 2
    try:
        group(hero="AI", before=["extraordinarily"], after=["unbelievable"], times=[1, 1.1, 1.2])
        raise AssertionError("chữ nhỏ rộng hơn hero phải báo lỗi")
    except ValueError:
        pass


def test_two_hero_and_multi_small() -> None:
    items = group(hero=["the", "studs"], before=["down", "to"], after=[], times=[1.0, 1.1, 1.3, 1.34], end=2.5)
    h1, h2 = by_text(items, "the"), by_text(items, "studs")
    assert abs((h2["at"] - h1["at"]) * FPS - round((h2["at"] - h1["at"]) * FPS)) < 1e-6   # trên bội số khung
    d = round((h2["at"] - h1["at"]) * FPS)
    assert T("second_hero_delay_frames")[0] <= d <= T("second_hero_delay_frames")[1], d
    a, b = by_text(items, "down"), by_text(items, "to")
    assert a["position"][0] < b["position"][0] and a["align"] == b["align"] == "left"
    assert h1["position"][0] < h2["position"][0] and h1["size"] == h2["size"]
    assert len(group(hero="studs", before=["a", "b"], after=["c", "d"], times=[1, 1.1, 1.2, 1.3, 1.4])) == 5
    try:
        group(hero="studs", before=["a", "b", "c"], after=["d", "e"], times=[1, 1.1, 1.2, 1.3, 1.4, 1.5])
        raise AssertionError("quá 5 từ phải báo lỗi")
    except ValueError:
        pass


def entry_frames(c, kind: str) -> int:
    key = c["effects"][0]["params"]["blurriness"][-1][0] if kind == "hero" else c["opacity"][-1][0]
    return round(key * FPS)


def test_timing() -> None:
    items = group(times=[1.0, 1.1, 1.3, 1.4], end=2.5)
    for t in ("down", "to", "the"):
        c = by_text(items, t)
        assert T("small_in_frames")[0] <= entry_frames(c, "small") <= T("small_in_frames")[1], t
        assert c["opacity"][0] == [0, 0] and c["opacity"][-1][1] == 100 and "effects" not in c
    hero = by_text(items, "studs")
    assert T("hero_blur_in_frames")[0] <= entry_frames(hero, "hero") <= T("hero_blur_in_frames")[1]
    assert abs(hero["at"] - 1.3) < 1e-9 and abs(hero["at"] + hero["dur"] - 2.5) < 1e-9
    assert all(abs(c["at"] * FPS - round(c["at"] * FPS)) < 1e-6 and abs(c["dur"] * FPS - round(c["dur"] * FPS)) < 1e-6
               for _, c in items)
    serif = by_text(group(style="serif"), "studs")
    assert entry_frames(serif, "hero") == entry_frames(hero, "hero") + T("serif_extra_frames")
    assert serif["font"] == "Playfair Display" and serif["style"] == "Bold Italic"
    assert hero["font"] == "Inter" and hero["style"] == "ExtraBold" and hero["tracking"] == PROF["fonts"]["hero_sans"]["tracking"]
    assert by_text(items, "down")["font"] == "Inter" and by_text(items, "down")["style"] == "Medium"
    lanes = {c["text"]: ln for ln, c in items}
    assert lanes["studs"] == "text" and lanes["down"] == "text_low"
    assert [ln for ln, _ in items].count("text") == 1


def test_colors() -> None:
    P = PROF["text"]["colors"]
    hero = lambda **kw: by_text(group(**kw), "studs")  # noqa: E731
    assert hero(on_dark=True)["color"] == P["on_dark"]
    assert hero(on_dark=True, accent=True)["color"] == P["on_dark"]        # nhấn chỉ trên nền sáng
    assert hero(on_dark=False)["color"] == P["on_paper"]
    assert hero(on_dark=False, accent=True)["color"] == P["accent"]
    assert "shadow" in hero(on_dark=True) and "shadow" not in hero(on_dark=False)
    assert by_text(group(on_dark=False, accent=True), "down")["color"] == P["on_paper"]   # chữ nhỏ không nhận màu nhấn


def test_zones() -> None:
    import text_fx as tf
    for zone, (lo, hi) in (("key", (tf.KEY_ZONE_TOP, 680)), ("cap", (1290, 1480))):
        for hero in ("studs", "Tiếng"):
            items = group(hero=hero, zone=zone)
            h = by_text(items, hero)
            top = min(c["position"][1] + meter("hero_sans" if c is h else "small", c["size"]).getbbox(c["text"], anchor="ls")[1]
                      for _, c in items)                                 # đỉnh mực cao nhất của cụm
            assert lo <= top and h["position"][1] <= hi, (zone, top, h["position"])
    assert abs(by_text(group(zone="key"), "studs")["position"][1] - 500) <= 60       # gần baseline key_y
    assert by_text(group(zone="cap"), "studs")["position"][0] == 540
    try:
        group(zone="giữa")
        raise AssertionError("vùng lạ phải báo lỗi")
    except ValueError:
        pass


def test_quote() -> None:
    items = bt.quote_text(["Happiness is not", "a destination", "it is a way of", "life"], last_word_serif=True,
                          at=1.0, dur=3.0, fps=FPS)
    tx = {c["text"]: c for _, c in items}
    assert "“" in tx and "”" in tx and "life" in tx
    last = tx["life"]
    assert last["font"] == "Playfair Display" and last["align"] == "right" and last["color"] == "#FFFFFF"
    assert tx["“"]["align"] == "left" and abs(tx["“"]["position"][0] - 0.06 * 1080) <= 2
    assert tx["”"]["position"][0] == last["position"][0]
    lines = [c for _, c in items if c["font"] == "Inter"]
    assert len(lines) == 3 and len({c["size"] for c in lines}) == 1
    assert [c["position"][1] for c in lines] == sorted(c["position"][1] for c in lines)
    assert max(c["position"][1] for _, c in items) <= 680
    plain = bt.quote_text(["a b", "c d"], last_word_serif=False, at=0, dur=2, fps=FPS)
    assert all(c["font"] != "Playfair Display" for _, c in plain if c["text"] not in ("“", "”"))


def test_quote_hero_line() -> None:
    """hero_index: dòng chính cỡ size_hero (Inter ExtraBold) căn giữa, dòng khác size_small, dấu ngoặc ≈ hero × 0.6 (Playfair)."""
    lines = ["that's what it means to live an", "entrepreneurial", "life"]
    items = bt.quote_text(lines, last_word_serif=True, at=1.0, dur=3.0, fps=FPS, hero_index=1)
    tx = {c["text"]: c for _, c in items}
    hero, first, tail = tx["entrepreneurial"], tx["that’s what it means to live an"], tx["life"]   # ' → ’ khớp FilmCraft
    assert hero["align"] == "center" and hero["position"][0] == 540 and hero["style"] == "ExtraBold"
    assert hero["size"] > 100 and hero["size"] <= T("size_hero")
    assert first["size"] == T("size_small") and first["align"] == "left" and tail["size"] == T("size_small")
    assert tail["font"] == "Playfair Display" and tail["style"] == "Bold Italic"
    for q in (tx["“"], tx["”"]):
        assert q["font"] == "Playfair Display" and abs(q["size"] - 0.6 * hero["size"]) <= 2, q["size"]
    ys = [first["position"][1], hero["position"][1], tail["position"][1]]
    assert ys == sorted(ys) and max(c["position"][1] for _, c in items) <= 680
    assert bt.quote_text(lines, True, 1.0, 3.0, FPS, hero_index=1) == items          # xác định
    try:
        bt.quote_text(lines, True, 1.0, 3.0, FPS, hero_index=5)
    except ValueError:
        pass
    else:
        raise AssertionError("hero_index ngoài phạm vi phải báo lỗi")


def test_apostrophe_matches_filmcraft() -> None:
    """FilmCraft đổi ' thành ’; chữ skill ghi phải là ’ để fc_build kiểm khớp. Chữ tiếng Việt không đổi."""
    items = bt.caption_group(hero="don't", before=["we"], after=["ever"], times=[1.0, 1.1, 1.3], end=2.5, fps=FPS)
    assert "don’t" in {c["text"] for _, c in items} and not any("'" in c["text"] for _, c in items)
    vn = bt.caption_group(hero="Việt", before=[], after=[], times=[1.0], end=2.0, fps=FPS)
    assert vn[0][1]["text"] == "Việt"


def test_fonts_check_helper() -> None:
    """FilmCraft chỉ thấy bản tĩnh Inter-*.ttf trong thư mục font người dùng (không thấy bản biến thiên, không thấy assets/fonts)."""
    import tempfile
    import env_status as es
    with tempfile.TemporaryDirectory() as d:
        dest = Path(d)
        assert set(es.missing_inter_fonts(dest)) == {"Inter-ExtraBold.ttf", "Inter-Medium.ttf"}
        (dest / "Inter-Variable.ttf").write_bytes(b"x")
        assert len(es.missing_inter_fonts(dest)) == 2
        assert sorted(es.install_inter_fonts(dest, refresh=False)) == ["Inter-ExtraBold.ttf", "Inter-Medium.ttf"]
        assert es.missing_inter_fonts(dest) == [] and es.install_inter_fonts(dest, refresh=False) == []


if __name__ == "__main__":
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_")):
        fn()
        print("ok", name)
    print("TẤT CẢ ĐẠT")
