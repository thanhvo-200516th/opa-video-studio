#!/usr/bin/env python3
"""Kiểm các kiểu cảnh minimal_scenes (painting, path_text, path_illus, illus_mid, illus_side, quote_paper) và hàm hỗ trợ fx_gfx / draw_path:
texture ≤ 50 %, đẩy máy 100 → 112 %, nét bị chữ cắt (không đè khối chữ), máy lia, mép loang, màu chữ trên giấy. Ảnh minh hoạ là ảnh PIL giả.
Chạy: ~/.venvs/video-skills/bin/python tests/test_minimal_scenes.py"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import brooks_text as BT  # noqa: E402
import draw_path as DP  # noqa: E402
import fx_gfx as G  # noqa: E402
import minimal_scenes as MS  # noqa: E402
import motion_fx as M  # noqa: E402
import style_profile as sp  # noqa: E402

FPS = 30
PROF = sp.load(name="minimal-edu")
TMP = Path(tempfile.mkdtemp(prefix="minimal_scenes_"))


def fx_new(name: str) -> M.MotionFX:
    return M.MotionFX(TMP / name, fps=FPS, name=name)


def pic(name: str, size=(900, 1200), kind="figure") -> str:
    im = Image.new("RGB", size, (255, 255, 255))
    d = ImageDraw.Draw(im)
    if kind == "figure":
        d.ellipse([size[0] * .25, size[1] * .1, size[0] * .75, size[1] * .5], fill=(30, 70, 200))
        d.rectangle([size[0] * .3, size[1] * .5, size[0] * .7, size[1]], fill=(30, 70, 200))
    else:                                              # "tranh": nền tối, mặt sáng giữa khung, trên / dưới trống
        d.rectangle([0, 0, *size], fill=(40, 30, 24))
        d.ellipse([size[0] * .25, size[1] * .35, size[0] * .75, size[1] * .65], fill=(200, 160, 120))
    p = TMP / f"{name}.png"
    im.save(p)
    return str(p)


def clips(fx, lane: str | None = None, name: str = "") -> list:
    return [c for ln, c in fx.items if (lane is None or ln == lane) and name in c.get("name", "")]


# ---------- fx_gfx / draw_path ----------
def test_gfx_helpers() -> None:
    p = Image.open(G.rough_texture(TMP, "rt", 1, "paint"))
    a = np.asarray(p.convert("RGB"), np.float32)
    assert p.size == (1080, 1920) and 150 < a.mean() < 250 and a.std() > 5, (p.size, a.mean(), a.std())
    assert (np.asarray(Image.open(G.rough_texture(TMP, "rt2", 1, "paint"))) == np.asarray(p)).all(), "cùng seed → cùng ảnh"
    try:
        G.rough_texture(TMP, "x", 0, "lạ")
        raise AssertionError("kind lạ phải lỗi")
    except ValueError:
        pass
    b = np.asarray(Image.open(G.bleed_image(TMP, "bl", pic("fig"), (1080, 1250), ("top", "left", "right"), 170, 3)))[..., 3]
    assert b.shape == (1250, 1080) and b[0].max() < 40 and b[:, 0].max() < 40 and b[700:, 540].min() > 200, "mép trên / trái loang, giữa đặc"
    assert ((b[:200] > 10) & (b[:200] < 245)).mean() > 0.3, "vùng loang phải có nhiều mức alpha"
    assert b[:, -1].max() < 40 and b[-1, 540] > 200, "mép dưới tràn khung"
    s = np.asarray(Image.open(G.side_figure(TMP, "sf", pic("fig2"), "left", (400, 1300))))[..., 3]
    assert s[650, 0] > 150 and s[650, -1] < 40, "hình bên trái: sát mép trái, mép phải loang"
    spec = DP.curve([(0, 0), (500, 100), (900, 500)], 12, head="dot")
    sh = DP.shift(spec, 1080, 0)
    assert DP.hits_canvas(spec) and not DP.hits_canvas(sh) and sh["frames"] == 12
    mov, png = TMP / "c.mov", TMP / "c.png"
    DP.write_with_still(DP.curve([(100, 100), (900, 900)], 6), mov, png, FPS)
    assert mov.stat().st_size > 0 and Image.open(png).size == (1080, 1920) and np.asarray(Image.open(png))[..., 3].max() == 255
    print("ok  fx_gfx / draw_path: texture, mép loang, nét nhiều màn hình")


# ---------- 1. tranh ----------
def test_painting() -> None:
    fx = fx_new("pt")
    img = pic("tranh", kind="painting")
    p = MS.painting(fx, img, 2.0, 3.0)
    tex = clips(fx, "card", "Texture tranh")
    assert len(tex) == 2 and all(c["blend"] == "multiply" and c["opacity"] <= 50 for c in tex), "texture nhiều lớp, multiply, ≤ 50 %"
    dx = [c["motion"]["position"][-1][1][0] - 540 for c in tex]
    assert dx[0] * dx[1] < 0, "hai lớp trôi ngược chiều"
    for c in tex:                                      # trôi suốt cảnh, phóng dư để không lộ mép
        pos = c["motion"]["position"]
        assert len(pos) >= 2 and pos[0][1] != pos[-1][1] and c["motion"]["scale"][0][1] >= 108
    sc = p["motion"]["scale"]
    assert abs(sc[0][1] - 100) < 1e-6 and sc[-1][1] == MS.PUSH_SCALE == 112 and sc[-1][2] == "easeIn", sc
    push = round((sc[-1][0] - next(k[0] for k in sc if k[1] == MS.SLOW_ZOOM)) * FPS)
    assert 8 <= push <= 11, f"đẩy máy {push} khung (~10)"
    assert abs(sc[-1][0] - (3.0 - 1 / FPS)) < 1e-3, "đẩy máy kết thúc ở khung cuối của cảnh"
    for c in tex:                                      # texture đẩy máy cùng tranh
        assert c["motion"]["scale"][-1][1] > c["motion"]["scale"][0][1] * 1.1
    blur = p["effects"][0]
    n = round(blur["params"]["length"][1][0] * FPS)
    assert blur["effect"] == "directional_blur" and blur["params"]["direction"] == 90 and 5 <= n <= 7, (blur, n)
    assert blur["params"]["length"][0][1] > 0 and blur["params"]["length"][-1][1] == 0
    try:
        MS.painting(fx, img, 0, 3, strength=0.6)
        raise AssertionError("texture nướng > 0,5 phải lỗi")
    except ValueError:
        pass
    assert any(c["kind"] == "whoosh" for c in fx.cues)
    assert MS.calm_zone(img) in ("top", "lower"), "mặt nằm giữa khung: chữ ở vùng trên / dưới"
    print("ok  painting: texture 2 lớp ≤ 50 % trôi ngược chiều, đẩy máy 100 → 112 % easeIn, nhoè vào 6 khung")


# ---------- 2. đường + chữ ----------
def make_caption(fx, gfx: Path):
    colors = BT.HeroColors(PROF)

    def caption(group, zone, on_dark, accent, end, **kw):
        items, times = group
        h = next(i for i, s in enumerate(items) if s[0] in "*~")
        words = [s.lstrip("*~") for s in items]
        out = BT.caption_group(words[h], words[:h], words[h + 1:], times, end=end, fps=FPS, style="serif" if items[h][0] == "~" else "sans",
                               on_dark=on_dark, accent=accent, zone=zone, prof=PROF, colors=colors, gfx_dir=gfx, **kw)
        fx.items += out
        return out
    return caption


def test_path_text() -> None:
    fx = fx_new("ptx")
    groups = [(["where you're", "*pursuing"], [1.0, 1.15]), (["because", "*agility", "and the"], [3.2, 3.5, 3.9]),
              (["and the", "~courage"], [5.6, 5.8])]
    r = MS.path_text(fx, make_caption(fx, TMP / "ptx"), 0.0, 7.5, groups, "white", TMP / "ptx", PROF)
    boxes, strokes = r["boxes"], r["strokes"]
    assert len(boxes) == 3 and len(strokes) == 4, (len(boxes), len(strokes))
    for k, box in enumerate(boxes):                    # nét tới từ k dừng cách khối chữ LINE_GAP; nét nối bắt đầu LINE_GAP sau khối chữ
        x0, y0, x1, y1 = box[0] + k * 1080, box[1], box[2] + k * 1080, box[3]
        into, out = np.asarray(DP.smooth(strokes[k])) if k else np.asarray(DP.smooth(strokes[0])), np.asarray(DP.smooth(strokes[k + 1]))
        assert abs(into[-1][1] - (y0 - MS.LINE_GAP)) < 1 and abs(out[0][1] - (y1 + MS.LINE_GAP)) < 1, (k, into[-1], out[0])
        for pts in (into, out):                        # mép nét (bán kính 20 px) không chạm khối chữ
            inside = (pts[:, 0] > x0 - 18) & (pts[:, 0] < x1 + 18) & (pts[:, 1] > y0 - 18) & (pts[:, 1] < y1 + 18)
            assert not inside.any(), f"nét đè khối chữ {k}: {pts[inside][:2]}"
    assert len(r["pans"]) == 2 and r["pans"][0][1] <= r["pans"][1][0], r["pans"]
    for t0, t1 in r["pans"]:
        assert 4 <= round((t1 - t0) * FPS) <= MS.PAN_FRAMES
    texts = clips(fx, "text")
    assert all("position" in c.get("motion", {}) for c in texts if c["at"] < r["pans"][0][0]), "chữ điểm dừng 0 chạy theo máy"
    blur = [c for ln, c in fx.items if any(e["effect"] == "directional_blur" for e in c.get("effects", []))]
    assert blur and all(max(k[1] for k in e["params"]["length"]) == MS.PAN_BLUR for c in blur for e in c["effects"] if e["effect"] == "directional_blur")
    mov = [c for _, c in fx.items if "(vẽ)" in c.get("name", "")]
    still = [c for _, c in fx.items if c.get("name", "").startswith("Đường") and "(vẽ)" not in c["name"]]
    assert len(mov) >= 4 and len(still) >= 4 and all(Path(c["src"]).is_file() for c in mov + still)
    assert sum(1 for c in fx.cues if c["kind"] == "pen") == 4 and sum(1 for c in fx.cues if c["kind"] == "whoosh") == 2
    try:                                               # hai từ quá sát: báo lỗi rõ
        MS.path_text(fx_new("ptx2"), make_caption(fx_new("ptx3"), TMP / "ptx3"), 0.0, 4.0,
                     [(["*một"], [1.0]), (["*hai"], [1.12])], "white", TMP / "ptx2", PROF)
        raise AssertionError("từ sát nhau phải lỗi")
    except ValueError as e:
        assert "khung" in str(e)
    print("ok  path_text: nét dừng cách chữ 40 px, nối tiếp, không đè chữ, 2 lần lia ≤ 12 khung, SFX pen / whoosh")


# ---------- 3. đường + minh hoạ ----------
def test_path_illus() -> None:
    img = pic("minh_hoa")
    fz = fx_new("pz")
    r = MS.path_illus(fz, img, "zigzag", 0.0, 4.5)
    assert r["pan"] and r["stroke"]["head"] == "dot" and r["stroke"]["glow"], r
    pic_c = r["image"]
    t_end = next(c for _, c in fz.items if "Đường minh hoạ (vẽ)" in c["name"])
    assert pic_c["at"] >= t_end["at"] + t_end["dur"] - 1e-6, "minh hoạ hiện khi đường tới nơi"
    assert pic_c["blend"] == "multiply" and pic_c["opacity"][0][1] == 0, "minh hoạ pop vào"
    assert r["pan"][0] >= t_end["at"] and r["pan"][1] <= pic_c["at"], "máy lia xong trước / lúc minh hoạ hiện"
    fr = fx_new("pr")
    r2 = MS.path_illus(fr, img, "rise", 0.0, 4.5)
    pts = np.asarray(r2["stroke"]["points"])
    assert r2["pan"] is None and pts[-1][1] < pts[0][1] - 300, "đường đi lên"
    assert MS.text_zone("path_illus", img, "zigzag") == ("top", True) and MS.text_zone("path_illus", img, "rise") == ("lower", True)
    try:
        MS.path_illus(fx_new("pe"), img, "xoáy", 0, 4)
        raise AssertionError("style lạ phải lỗi")
    except ValueError:
        pass
    print("ok  path_illus: zigzag lia lộ vật, rise đi lên, chấm trắng + quầng, minh hoạ hiện khi đường tới")


# ---------- 4–5. minh hoạ giữa / bên ----------
def test_illus_mid_side() -> None:
    img = pic("fig")
    fx = fx_new("im")
    p = MS.illus_mid(fx, img, 1.0, 5.0)
    pos = p["motion"]["position"]
    assert pos[0][1][1] > pos[1][1][1] + 300 and pos[1][2] == "easeIn" and p["blend"] == "multiply", pos
    assert round(pos[1][0] * FPS) == MS.MID_RISE_FRAMES
    assert any(e["effect"] == "directional_blur" for e in p["effects"]) and clips(fx, "card", "Texture sơn thô")
    assert Image.open(p["src"]).size == (1080, MS.MID_H)
    assert MS.text_zone("illus_mid", img) == ("top", True)
    fl, fr = fx_new("sl"), fx_new("sr")
    a, b = MS.illus_side(fl, img, "left", 0, 4), MS.illus_side(fr, img, "right", 0, 4)
    assert a["motion"]["position"][1][1][0] < 540 < b["motion"]["position"][1][1][0], "hình sát mép đúng bên"
    assert a["motion"]["position"][0][1][0] < 0 < 1080 < b["motion"]["position"][0][1][0], "trượt vào từ ngoài khung"
    assert MS.text_zone("illus_side", img, "left") == ("side_right", True) and MS.text_zone("illus_side", img, "right") == ("side_left", True)
    for z in ("side_left", "side_right"):               # chữ cạnh hình không tràn cột nút phải (x > 890) và không đè hình ~ 400 px
        lo, hi, cx, w = BT.ZONES[z]
        assert cx + w / 2 <= 900 and cx - w / 2 >= 150
    ent = BT.caption_group("vòng", ["một"], [], [1.0, 1.2], end=3.0, fps=FPS, on_dark=False, zone="side_right", prof=PROF)
    assert ent and all(c["position"][0] > 400 for _, c in ent if "position" in c)
    print("ok  illus_mid / illus_side: trồi lên 16 khung, mép loang, hình sát mép đúng bên, vùng chữ phía kia")


# ---------- 6. toàn chữ trên giấy ----------
def test_quote_paper() -> None:
    lines = ["Độ tin cậy tăng lên", "gấp mười lần", "so với video cắt ghép"]
    for bg, want_text in (("white", PROF["text"]["colors"]["on_paper"]), ("blue", PROF["text"]["colors"]["on_dark"])):
        fx = fx_new(f"q_{bg}")
        items = MS.quote_paper(fx, lines, 1, 0.0, 4.0, 0.1, 1.5, bg, TMP / f"q_{bg}", PROF, 400)
        txt = [c for _, c in items if "text" in c]
        assert any(c["text"] == BT.OPEN_Q for c in txt) and any(c["text"] == BT.CLOSE_Q for c in txt), "đủ hai dấu ngoặc kép"
        assert {c["text"] for c in txt} >= {lines[0], lines[1], lines[2]}
        small = next(c for c in txt if c["text"] == lines[0])
        mark = next(c for c in txt if c["text"] == BT.OPEN_Q)
        assert small["color"].upper() == want_text.upper() and mark["color"].upper() == want_text.upper(), (bg, small["color"])
        hero = next(c for c in txt if c["text"] == lines[1])
        assert hero["color"].upper() == (MS.HERO_PAPER_ACCENT if bg == "white" else MS.HERO_BLUE_BG).upper()
        if bg == "white":
            assert not any(e["effect"] == "wonder_glow" for _, c in items for e in c.get("effects", [])), "nền sáng: không glow"
        assert min(c["position"][1] for c in txt) > 700, "khối chữ dời về vùng giữa khung"
        bgc = clips(fx, "gfx_under", "Nền giấy trích dẫn")[0]
        assert Image.open(bgc["src"]).size == (1080, 1920) and clips(fx, "card", "Texture giấy thô")[0]["opacity"] <= 50
    try:
        MS.quote_paper(fx_new("qe"), lines, 1, 0, 4, 0.1, 1.5, "green", TMP, PROF)
        raise AssertionError("bg lạ phải lỗi")
    except ValueError:
        pass
    print("ok  quote_paper: giấy trắng chữ đen + nhấn xanh, giấy xanh chữ trắng + nhấn vàng, đủ ngoặc kép, không glow trên nền sáng")


if __name__ == "__main__":
    for n in [n for n in sorted(globals()) if n.startswith("test_")]:
        globals()[n]()
    print("TẤT CẢ ĐẠT")
