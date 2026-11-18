#!/usr/bin/env python3
"""Typography chuyển động mượt của hồ sơ minimal-edu (3.6.3): kinetic_in / hold / exit, stagger, không vọt cho số / tiền,
vùng chữ + pick_zone, chọn glow / gradient theo khoảnh khắc (looks="auto"). Offline.
Chạy: ~/.venvs/video-skills/bin/python tests/test_kinetic_text.py"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import brooks_text as bt  # noqa: E402
import style_profile as sp  # noqa: E402
import text_motion as tm  # noqa: E402

PROF = sp.load(name="minimal-edu")
KIN = tm.kinetic_params(PROF)
FPS = 30
F = 1 / FPS
GFX = Path(tempfile.mkdtemp(prefix="kin_"))


def group(**kw):
    base = dict(hero="studs", before=["down", "to"], after=["the"], times=[1.0, 1.1, 1.3, 1.4], end=2.5, fps=FPS, gfx_dir=GFX)
    base.update(kw)
    return bt.caption_group(**base)


def hero_of(items, text="studs"):
    return next((lane, c) for lane, c in items if c.get("text", c.get("name", "")).endswith(text) and lane in ("text", "text_img"))


def fx(c, name):
    return next(e for e in c["effects"] if e["effect"] == name)["params"]


def frames(keys) -> list[int]:
    return [round(k[0] * FPS) for k in keys]


def test_entrance_keys_match_spec() -> None:
    """Vào 10 khung: Y +48 → 0 (easeIn), scale 90 → 100, blur 12 → 0 trong 6 khung đầu, opacity 0 → 100 trong 4 khung đầu."""
    c = by = group()[0][1]                                  # chữ nhỏ "down"
    assert (KIN["in_frames"], KIN["dy"], KIN["scale_from"], KIN["blur_from"], KIN["blur_frames"], KIN["opacity_frames"]) == (10, 48, 90, 12, 6, 4)
    assert c["opacity"][0] == [0, 0] and frames(c["opacity"]) == [0, 4] and c["opacity"][1][1] == 100
    blur = fx(c, "gaussian_blur")["blurriness"]
    assert [k[1] for k in blur] == [12, 0] and frames(blur) == [0, 6] and blur[1][2] == "easeIn"
    tf = fx(c, "transform")
    ax, ay = tf["anchor"]
    assert tf["uniform_scale"] is True and tf["position"][0] == [0, [ax, ay + 48]] and tf["position"][1][1:] == [[ax, ay], "easeIn"]
    assert frames(tf["position"]) == [0, 10]
    assert [k[1] for k in tf["scale_height"]] == [90, 100] and frames(tf["scale_height"]) == [0, 10] and tf["scale_height"][1][2] == "easeIn"
    assert by["align"] == "left" and 0 < ax < 1080 and 0 < ay < by["position"][1]            # neo giữa chữ, trên baseline


def test_hero_overshoot_and_numbers() -> None:
    """Từ lớn vọt 106 % rồi lắng sau 12 khung; số / tiền / '%' / 'lần' sau số thì không vọt."""
    sc = fx(hero_of(group())[1], "transform")["scale_height"]
    assert [k[1] for k in sc] == [90, 106, 100] and frames(sc) == [0, 6, 12] and sc[1][2] == "bezier" and sc[2][2] == "easeIn", sc
    for word, before in (("5", ["gần"]), ("12%", []), ("tỷ", ["5"]), ("tiền", []), ("lần", ["3"]), ("2026", []), ("triệu", ["200"])):
        w = hero_of(group(hero=word, before=before, after=[], times=[1.0] * (len(before) + 1)), word)[1]
        assert [k[1] for k in fx(w, "transform")["scale_height"]] == [90, 100], word
    for word, before in (("lần", ["rất"]), ("studs", []), ("kiến thức", [])):                                    # từ thường vẫn vọt
        w = hero_of(group(hero=word, before=before, after=[], times=[1.0] * (len(before) + 1)), word)[1]
        assert 106 in [k[1] for k in fx(w, "transform")["scale_height"]], word
    assert bt.is_number_word("5") and bt.is_number_word("tiền") and bt.is_number_word("lần", "3") and not bt.is_number_word("lần", "rất")
    assert not bt.is_number_word("studs") and not bt.is_number_word("một") and bt.is_number_word("%")


def test_stagger() -> None:
    got = tm.stagger_times([1.0] * 4, FPS, KIN)
    assert [round((b - a) * FPS) for a, b in zip(got, got[1:])] == [2, 2, 2]
    assert tm.stagger_times([1.0, 1.2, 1.5], FPS, KIN) == [1.0, 1.2, 1.5]
    assert round((max(tm.stagger_times([1.0] * 9, FPS, KIN)) - 1.0) * FPS) == 8              # trần 8 khung
    ats = [round(c["at"] * FPS) for _, c in group(times=[1.0, 1.0, 1.0, 1.0])]
    assert ats == [30, 32, 34, 36], ats


def test_hold_and_exit_via_ensure_motion() -> None:
    items = group()
    n = tm.ensure_motion(items, FPS, profile=PROF, cuts=[2.5 + 2 * F])
    assert n["out"] == 4 and n["hold"] == 4 and n["in"] == 0, n                              # đã có kiểu vào từ caption_group
    for _, c in items:
        d = c["dur"]
        assert abs(c["at"] + d - 2.5) < 1e-6                                                 # kết thúc 2 khung trước điểm cắt
        tf = fx(c, "transform")
        sc = tf["scale_height"]
        assert sc[-1][1] == KIN["hold_scale"] and abs(sc[-1][0] - (d - 5 * F)) < 1e-6        # phóng chậm 100 → 103 suốt lúc giữ
        pos = tf["position"]
        assert abs(pos[-1][0] - d) < 1e-6 and pos[-1][1][1] == tf["anchor"][1] - 24 and pos[-2][2] == "easeOut"
        assert c["opacity"][-1] == [d, 0] and c["opacity"][-2][2] == "easeOut" and abs(c["opacity"][-1][0] - c["opacity"][-2][0] - 5 * F) < 1e-6
        b = fx(c, "gaussian_blur")["blurriness"]
        assert b[-1] == [d, 6] and b[-2][1] == 0 and b[-2][2] == "easeOut"
        times = [k[0] for ks in (c["opacity"], b, pos, sc) for k in ks]
        assert max(times) <= d + 1e-9
    short = [("text", {"text": "x", "at": 1.0, "dur": 0.4, "position": [540, 500]})]           # clip ngắn: vẫn mốc tăng dần, không vượt cuối
    tm.ensure_motion(short, FPS, profile=PROF)
    c = short[0][1]
    for ks in (c["opacity"], fx(c, "gaussian_blur")["blurriness"], fx(c, "transform")["position"]):
        assert all(a[0] < b[0] for a, b in zip(ks, ks[1:])) and ks[-1][0] <= c["dur"] + 1e-9, ks
    assert [e["effect"] for e in c["effects"]].count("transform") == 1


def test_one_physics_set() -> None:
    """Mọi chữ trong cụm dùng cùng đường cong / thời lượng; chỉ stagger (`at`) và từ lớn vọt khác nhau."""
    sigs = set()
    for _, c in group():
        tf = fx(c, "transform")
        sigs.add((tuple(k[2] for k in tf["position"][1:]), tuple(frames(tf["position"])), tuple(fx(c, "gaussian_blur")["blurriness"][1][1:]),
                  tuple(frames(c["opacity"]))))
    assert len(sigs) == 1, sigs


def test_ensure_motion_foreign_clip() -> None:
    """Clip chữ không qua caption_group (không có vào) được thêm đủ vào / giữ / ra; clip đã có ra riêng giữ nguyên."""
    items = [("text", {"text": "a", "at": 1.0, "dur": 2.0, "position": [540, 500], "size": 120})]
    n = tm.ensure_motion(items, FPS, profile=PROF)
    assert n["in"] == n["hold"] == n["out"] == 1, n
    own = [("text", {"text": "b", "at": 1.0, "dur": 2.0, "transition_out": {"type": "fade"}})]
    n = tm.ensure_motion(own, FPS, profile=PROF)
    assert n["out"] == 0 and "transition_out" in own[0][1]


# ---------------------------------------------------------------------------- vùng chữ
def test_pick_zone_aroll() -> None:
    pz = bt.pick_zone
    assert pz(0, True, 300, chin_y=1000) == "lower" and pz(1, True, 300, chin_y=1000, prev_zone="lower") == "lower"   # đầu cao: TOP không vừa
    assert [pz(i, True, 560, chin_y=1000) for i in range(4)] == ["lower", "top", "lower", "top"]                         # xen kẽ khi cả hai vừa
    seq, prev = [], None
    for i in range(6):
        prev = pz(i, True, 560, chin_y=1000, prev_zone=prev)
        seq.append(prev)
    assert all(a != b for a, b in zip(seq, seq[1:])), seq
    assert pz(0, True, 300, chin_y=1200) == "lower"                                         # lower còn 1230–1430 = 200
    try:
        pz(0, True, 300, chin_y=1300)                                                       # lower còn 100, top không vừa
        raise AssertionError("không vùng nào vừa phải báo lỗi")
    except ValueError:
        pass
    assert bt.zone_band("lower", chin_y=1300) == (1330, 1430) and bt.zone_band("lower")[0] == 1180      # ≥ 30 px dưới cằm
    assert bt.zone_band("top", head_top=560) == (260, 520) and bt.zone_band("top", head_top=900)[1] == 680
    assert pz(0, True, 300, chin_y=1000, face_side="right", block_h=200) == "lower"
    assert {pz(i, True, 300, chin_y=1000, face_side="right") for i in range(4)} == {"lower", "mid_left"}  # xa mặt (mặt bên phải)
    assert {pz(i, True, 300, chin_y=1000, face_side="left") for i in range(4)} == {"lower", "mid_right"}


def test_pick_zone_broll_rotates() -> None:
    seq, prev = [], None
    for i in range(9):
        prev = bt.pick_zone(i, False, None, prev_zone=prev)
        seq.append(prev)
    assert set(seq) == {"top", "lower", "mid_center"} and all(a != b for a, b in zip(seq, seq[1:])), seq
    assert seq[:3] == ["top", "lower", "mid_center"]


def ink_span(items) -> tuple[float, float]:
    """(đỉnh mực cao nhất, đáy mực thấp nhất) của cụm, đo bằng font thật."""
    M = bt.Meter(PROF)
    role = lambda c: "small" if c["font"] == "Inter" and c["style"] == "Medium" else "hero_sans"   # noqa: E731
    return (min(c["position"][1] - M.ink_top(role(c), c["size"], [c["text"]]) for _, c in items),
            max(c["position"][1] + M.ink_bottom(role(c), c["size"], [c["text"]]) for _, c in items))


def test_zone_bounds_with_band() -> None:
    """caption_group theo dải đã chọn (cằm / đỉnh đầu): mực nằm trong dải; mọi vùng nằm ngoài dải cấm (y < 260, y > 1440, x > 890 khi y ≥ 720)."""
    for zone, kw in (("lower", dict(chin_y=1230)), ("top", dict(head_top=560))):
        lo, hi = bt.zone_band(zone, **kw)
        top, bot = ink_span(group(zone=zone, band=(lo, hi)))
        assert lo - 1 <= top and bot <= hi + 1, (zone, top, bot, lo, hi)
    for zone in bt.ZONES:
        top, bot = ink_span(group(zone=zone))
        lo, hi, cx, w = bt.ZONES[zone]
        assert 260 <= top and bot <= 1440 and lo - 1 <= top and bot <= hi + 1, (zone, top, bot)
        assert cx - w / 2 >= 90 and (hi <= 680 or cx + w / 2 <= 890), zone


# ---------------------------------------------------------------------------- glow / gradient theo khoảnh khắc
def glow_of(c):
    return next((e for e in c.get("effects", []) if e["effect"] == "wonder_glow"), None)


def test_auto_numbers_solid() -> None:
    gold = next(e["color"] for e in PROF["text"]["colors"]["hero_rotation_dark"] if e["name"] == "gold")
    for word, before in (("5", ["gần"]), ("tỷ", ["5"]), ("tiền", []), ("30%", [])):
        lane, c = hero_of(group(hero=word, before=before, after=[], times=[1.0] * (len(before) + 1), looks="auto", key=True), word)
        assert lane == "text" and c["color"] == gold and glow_of(c) is None, (word, c["color"])
        assert c["shadow"] == PROF["text"]["look_shadows"]["deep"]                           # bóng sâu mềm, không viền
        assert [k[1] for k in fx(c, "transform")["scale_height"]] == [90, 100]               # số / tiền: không vọt, không gradient dù key=True
    lane, c = hero_of(group(hero="tiền", before=[], after=[], times=[1.0], looks="auto", on_dark=False), "tiền")
    assert glow_of(c) is None and c["color"] == PROF["text"]["colors"]["accent"]


def test_auto_emotion_key_default() -> None:
    gold_glow = bt.PALETTES["gold"]["glow"]
    lane, c = hero_of(group(style="serif", looks="auto"))
    assert lane == "text" and c["font"] == "Playfair Display" and glow_of(c)["params"]["color"] == gold_glow, c      # cảm xúc / serif: glow ấm
    assert glow_of(c)["params"]["radius"] == bt.GLOW_LEVEL["normal"]["radius"]
    lane, c = hero_of(group(looks="auto", key=True))
    assert lane == "text_img" and c["src"].endswith(".png")                                   # từ khoá mạnh nhất: gradient
    assert [e["effect"] for e in c["effects"]] == ["gaussian_blur", "transform", "wonder_glow"]
    lane, c = hero_of(group(looks="auto"))
    assert lane == "text" and glow_of(c)["params"]["radius"] == bt.GLOW_LEVEL["normal"]["radius"]     # còn lại: glow trên nền tối
    lane, c = hero_of(group(looks="auto", on_dark=False))
    assert lane == "text_img" and glow_of(c) is None and c["name"].startswith(bt.LIGHT_TAG)   # nền sáng: gradient đậm, không glow
    lane, c = hero_of(group(looks="auto", on_dark=False, gfx_dir=None))
    assert lane == "text" and glow_of(c) is None and c["shadow"] == PROF["text"]["look_shadows"]["light"]
    lane, c = hero_of(group(looks="auto", key=True, gfx_dir=None))
    assert lane == "text" and glow_of(c)                                                      # không có gfx_dir: không gradient, glow
    n_grad = sum(1 for lane, _ in group(looks="auto", key=True) if lane == "text_img")
    assert n_grad == 1                                                                        # tối đa một gradient mỗi cụm
    assert group(looks="auto", color="#19C6F5")[2][1]["color"] == "#19C6F5"                  # màu chỉ định tay vẫn thắng
    forced = hero_of(group(looks="auto", look="shadow_deep"))[1]
    assert forced["shadow"] == PROF["text"]["look_shadows"]["deep"] and glow_of(forced) is None   # look tay thắng auto


def test_glow_level_visible() -> None:
    g, s = bt.GLOW_LEVEL["normal"], bt.GLOW_LEVEL["soft"]
    assert g["radius"] >= 30 and g["peak"] >= 200 and g["hold"] >= 100                      # đo khung hình thật (typo_proof): quầng thấy rõ
    assert s["radius"] >= 20 and s["hold"] >= 50 and g["peak"] > g["hold"] and s["peak"] > s["hold"]


def test_short_clip_hold_motion() -> None:
    """Clip ngắn (0,6–0,95 s, cửa sổ giữ < min_hold_frames) vẫn có chuỗi key phóng chậm nối từ cuối vào tới đầu ra → bộ kiểm không báo đứng yên."""
    for end in (1.6, 1.7, 1.8, 1.9, 1.95, 2.0):
        items = group(times=[1.0, 1.0, 1.0, 1.0], end=end)   # stagger: clip dài 0,6–1,0 s
        tm.ensure_motion(items, FPS, profile=PROF)
        tracks = [{"name": f"{lane} {i}", "clips": [c]} for i, (lane, c) in enumerate(items)]
        rep = tm.static_report(tracks, FPS)
        assert rep["total"] and rep["static_hold"] == 0, (end, rep)
        for _, c in items:
            sk = fx(c, "transform")["scale_height"]
            assert all(a[0] < b[0] for a, b in zip(sk, sk[1:])) and sk[-1][0] <= c["dur"] + 1e-9, sk
            assert max(v[1] for v in sk) <= max(KIN["overshoot"], KIN["hold_scale"]), sk              # nhẹ: không vượt hold_scale / vọt
    for dur in (0.6, 0.633, 0.667, 0.7, 0.9, 0.95):                                          # clip dựng tay (kiểu vào của ensure_motion)
        own = [("text", {"text": "x", "at": 1.0, "dur": dur, "position": [540, 500], "size": 120})]
        tm.ensure_motion(own, FPS, profile=PROF)
        assert tm.static_report([{"name": "text 1", "clips": [own[0][1]]}], FPS)["static_hold"] == 0, dur
    # kiểu vào có chuỗi position dài (typewriter_soft…) khiến cửa sổ giữ chỉ còn ~2 khung: vẫn phải có chuỗi key trải qua lúc giữ
    pos = [[0, [540, 510]], [0.2, [540, 500], "easeIn"], [0.4, [540, 500]]]
    odd = [("text_low", {"text": "y", "at": 1.0, "dur": 0.633, "position": [540, 500], "size": 90, "opacity": [[0, 0], [0.1, 100]],
                         "effects": [{"effect": "transform", "params": {"anchor": [540, 500], "position": pos, "uniform_scale": True, "scale_height": 100.0}}]})]
    tm.ensure_motion(odd, FPS, profile=PROF)
    assert tm.static_report([{"name": "text_low 1", "clips": [odd[0][1]]}], FPS)["static_hold"] == 0


def test_default_non_profile_unchanged() -> None:
    """Không hồ sơ → ensure_motion giữ nguyên bản cũ (soft_in / hold_drift / soft_out)."""
    items = [("text", {"text": "a", "at": 1.0, "dur": 1.5, "position": [540, 500], "size": 150})]
    n = tm.ensure_motion(items, FPS)
    c = items[0][1]
    assert n == {"in": 1, "hold": 1, "out": 1, "text": 1}
    assert c["opacity"][0] == [0, 0] and abs(c["opacity"][-1][0] - 1.5) < 1e-9 and "kinetic" not in str(c)
    assert fx(c, "transform")["scale_height"][-1][1] == tm.HOLD_SCALE["key"]


if __name__ == "__main__":
    fns = sorted((k, v) for k, v in globals().items() if k.startswith("test_"))
    for name, fn in fns:
        fn()
        print("ok", name)
    print(f"TẤT CẢ ĐẠT ({len(fns)} bài kiểm)")
