#!/usr/bin/env python3
"""Đa dạng kiểu vào của chữ minimal-edu (3.6.4): thư viện ≥ 8 kiểu, EntranceStyles xoay 6–10 kiểu theo tên video,
không trùng kiểu cụm liền kề, số / tiền không vọt, mọi key đến đều ease (không linear), 8–14 khung. Offline.
Chạy: ~/.venvs/video-skills/bin/python tests/test_text_variety.py"""
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
FPS = 30
GFX = Path(tempfile.mkdtemp(prefix="var_"))


def group(**kw):
    base = dict(hero="studs", before=["down", "to"], after=["the"], times=[1.0, 1.1, 1.3, 1.4], end=2.5, fps=FPS, gfx_dir=GFX)
    base.update(kw)
    return bt.caption_group(**base)


def all_keys(c: dict):
    """Mọi chuỗi key trong clip: (tên, keys)."""
    out = [("opacity", c["opacity"])]
    if isinstance(c.get("tracking"), list):
        out.append(("tracking", c["tracking"]))
    for e in c.get("effects", []):
        for k, v in e["params"].items():
            if isinstance(v, list) and v and isinstance(v[0], list) and isinstance(v[0][0], (int, float)):
                out.append((f"{e['effect']}.{k}", v))
    return out


def test_library_size() -> None:
    assert len(tm.ENTRANCES) >= 8 and len(set(tm.ENTRANCES)) == len(tm.ENTRANCES)
    for need in ("slide_up_blur", "drop_bounce", "scale_pop", "mask_reveal_up", "wipe_left", "tracking_expand", "rotate_in", "blur_zoom"):
        assert need in tm.ENTRANCES, need


def test_every_style_eases_and_duration() -> None:
    """Mỗi kiểu: key đến easeIn / bezier (không linear), mốc cuối của vào trong 8–14 khung, thời gian tăng dần, chữ lớn nhỏ đều vào được."""
    for st in tm.ENTRANCES:
        for lane, c in group(entrance=st):
            last = 0
            for name, ks in all_keys(c):
                ts = [k[0] for k in ks]
                assert ts == sorted(set(ts)), (st, name, ks)
                if name != "opacity":                                                             # mờ 3–4 khung đầu: linear là đủ
                    assert all(len(k) > 2 and k[2] in ("easeIn", "bezier", "hold") for k in ks[1:]), (st, name, ks)
                if name != "opacity":
                    last = max(last, round(ts[-1] * FPS))
            assert 8 <= last <= 14, (st, last)


def test_default_unchanged() -> None:
    """Không entrances / entrance → kiểu mặc định như 3.6.3 (slide_up_blur + vọt 106 % cho từ lớn)."""
    a = [(lane, c) for lane, c in group()]
    b = [(lane, c) for lane, c in group(entrance="slide_up_blur")]
    assert a[0][1]["effects"] == b[0][1]["effects"] and a[0][1]["opacity"] == b[0][1]["opacity"]


def test_rotator_rules() -> None:
    for seed in ("kb08", "kb09", "một video khác", "x"):
        E = tm.EntranceStyles(PROF, seed)
        assert tm.ENTRANCE_MIN_STYLES <= len(E.styles) <= tm.ENTRANCE_MAX_STYLES, E.styles
        assert sum(s in tm.NUMBER_SAFE for s in E.styles) >= 4
        assert tm.EntranceStyles(PROF, seed).styles == E.styles                                   # cùng tên video → cùng bộ
        last_h = last_s = None
        used_h, used_s = [], []
        for i in range(40):
            h, s = E.pick("hero", number=i % 5 == 4), E.pick("small")
            assert h != last_h and s != last_s, (seed, i, h, s)
            assert h != "typewriter_soft"                                                         # chỉ chữ nhỏ
            if i % 5 == 4:
                assert h in tm.NUMBER_SAFE, h
            last_h, last_s = h, s
            used_h.append(h)
            used_s.append(s)
        assert len(set(used_h)) >= 5 and len(set(used_s)) >= 5, (seed, set(used_h), set(used_s))
    assert len({tm.EntranceStyles(PROF, f"video {i}").styles for i in range(12)}) >= 6            # tên video khác → bộ khác


def test_png_avoids_tracking() -> None:
    E = tm.EntranceStyles(PROF, "png")
    assert all(E.pick("hero", png=True) not in tm.NO_PNG for _ in range(30))
    c = {"src": "x.png", "at": 0, "dur": 2.0, "name": "g"}
    assert tm.entrance_in(c, FPS, "tracking_expand") == "blur_zoom" and "tracking" not in c


def test_caption_group_rotation_and_numbers() -> None:
    E = tm.EntranceStyles(PROF, "kb-test")
    seen, prev = [], None
    for i in range(12):
        items = group(entrances=E, hero="5" if i % 3 == 2 else "studs", before=[] if i % 3 == 2 else ["down", "to"], after=[],
                      times=[1.0] if i % 3 == 2 else [1.0, 1.1, 1.3])
        hero = next(c for lane, c in items if c.get("text") in ("5", "studs"))
        sig = tuple(sorted(e["effect"] for e in hero["effects"]))
        seen.append(sig)
        if i % 3 == 2:                                                                            # số: không vọt
            tf = next(e for e in hero["effects"] if e["effect"] == "transform")["params"]["scale_height"]
            assert not isinstance(tf, list) or max(k[1] for k in tf) <= 100, tf
    assert len(set(seen)) >= 3, seen


def test_forced_entrance_and_validation() -> None:
    mask = group(entrance="mask_reveal_up")
    for _, c in mask:
        crop = next(e for e in c["effects"] if e["effect"] == "crop")["params"]
        assert crop["bottom"][0][1] > 0 and crop["bottom"][-1][1] == 0
    wipe = group(entrance="wipe_left")
    for _, c in wipe:
        crop = next(e for e in c["effects"] if e["effect"] == "crop")["params"]
        assert crop["right"][0][1] > crop["right"][1][1] > 0 and crop["right"][-1][1] == 0
    tr = group(entrance="tracking_expand")[0][1]
    assert tr["tracking"][0][1] < tr["tracking"][-1][1] and tr["tracking"][-1][1] == bt.Meter(PROF).tracking("small")
    try:
        group(entrance="nope")
        raise AssertionError("phải báo lỗi")
    except ValueError:
        pass


def test_typewriter_fast_stagger() -> None:
    """Chữ nhỏ typewriter_soft: mỗi từ trễ 1 khung (không phải 2)."""
    class Fixed(tm.EntranceStyles):
        def pick(self, kind="hero", number=False, png=False):
            return "typewriter_soft" if kind == "small" else "blur_zoom"
    items = group(entrances=Fixed(PROF, "x"), times=[1.0] * 4)
    assert [round(c["at"] * FPS) for _, c in items] == [30, 31, 32, 33]


def test_hold_exit_still_apply() -> None:
    """Mọi kiểu vẫn nhận hold / exit của ensure_motion: opacity cuối 0 ở cuối clip, không key vượt cuối clip."""
    for st in tm.ENTRANCES:
        items = group(entrance=st)
        n = tm.ensure_motion(items, FPS, profile=PROF)
        assert n["in"] == 0 and n["out"] == len(items), (st, n)
        for _, c in items:
            assert c["opacity"][-1] == [c["dur"], 0], st
            for name, ks in all_keys(c):
                assert ks[-1][0] <= c["dur"] + 1e-9 and all(a[0] < b[0] for a, b in zip(ks, ks[1:])), (st, name, ks)


def test_short_clip_compresses() -> None:
    for st in tm.ENTRANCES:
        c = {"text": "x", "at": 1.0, "dur": 0.2, "position": [540, 500], "size": 100}
        tm.entrance_in(c, FPS, st, geo={"x0": 500, "x1": 580, "base": 520, "size": 100}, idx=1)
        for name, ks in all_keys(c):
            assert ks[-1][0] <= c["dur"] + 1e-9 and all(a[0] < b[0] for a, b in zip(ks, ks[1:])), (st, name, ks)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print("ok", fn.__name__)
    print(f"TẤT CẢ ĐẠT ({len(fns)} bài kiểm)")
