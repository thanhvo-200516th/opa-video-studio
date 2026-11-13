#!/usr/bin/env python3
"""J-1 #5 (v2.6): chữ HOOK sau đầu tự xếp để đọc trọn câu — `FX.fit_hook` (nâng lên / tách 2 dòng / thu cỡ / đặt trước đầu).
Chạy: ~/.venvs/video-skills/bin/python tests/test_hook_fit.py"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion_fx import MotionFX  # noqa: E402
from text_fx import HOOK_HIDE_MAX, HOOK_MIN_SIZE  # noqa: E402

KEYS = ["ÔM HẾT", "MẤT KHÁCH", "CÔNG VIỆC KINH DOANH", "KHÔNG LÀM THẾ NỮA", "BỘ MÁY DOANH NGHIỆP VẬN HÀNH"]


def hidden_of(fx: MotionFX, lines: list, head_top: int, half_w: int) -> float:
    return max(fx.hidden_ratio(fx.width("mx_heavy", s, t), y + fx.ink_bottom("mx_heavy", s, t), head_top, half_w) for t, s, y in lines)


def test_hook_fit() -> None:
    with tempfile.TemporaryDirectory() as td:
        fx = MotionFX(gfx_dir=Path(td), fps=30, name="T")
        short = fx.fit_hook("ÔM HẾT", 190, 420, True, head_top=640)               # đầu thấp, chữ ngắn → giữ nguyên, không cần matte
        assert short["lines"] == [("ÔM HẾT", 190, 420)] and not short["matte"] and short["hidden"] == 0, short
        for head_top in (300, 380, 440, 520, 640):
            for key in KEYS:
                r = fx.fit_hook(key, 190, 420, True, head_top=head_top, half_w=215)
                assert 1 <= len(r["lines"]) <= 2 and "".join(t for t, _, _ in r["lines"]).replace(" ", "") == key.replace(" ", ""), r
                assert all(fx.width("mx_heavy", s, t) <= fx.max_w + 1 for t, s, _ in r["lines"]), r          # vừa vùng chữ 800 px
                if r["matte"]:                                                   # sau đầu chỉ khi đầu che ≤ 20 % bề rộng
                    assert 0 < hidden_of(fx, r["lines"], head_top, 215) <= HOOK_HIDE_MAX + 0.01, (head_top, key, r)
                    assert all(s >= HOOK_MIN_SIZE for _, s, _ in r["lines"]), r
                elif r["hidden"] == 0:                                           # nằm trên đầu: đọc trọn
                    assert hidden_of(fx, r["lines"], head_top, 215) == 0, (head_top, key, r)
                assert r["note"], r
        real = fx.fit_hook("CÔNG VIỆC KINH DOANH", 190, 420, True, head_top=380)   # ca thật OPA05: đầu che giữa «CÔNG VI… DOANH»
        assert not real["matte"] and len(real["lines"]) == 2 and real["lines"][0][1] >= HOOK_MIN_SIZE, real
        two = fx.fit_hook("CÔNG VIỆC KINH DOANH", 190, 420, True, head_top=640)    # còn chỗ trên đầu: tách 2 dòng, không bị che
        assert len(two["lines"]) == 2 and two["hidden"] == 0, two
    print("ok  fit_hook: chữ ngắn giữ nguyên · dài tách 2 dòng / thu cỡ / ra trước đầu · sau đầu chỉ khi che ≤ 20 %")


if __name__ == "__main__":
    test_hook_fit()
    print("TẤT CẢ ĐẠT")
