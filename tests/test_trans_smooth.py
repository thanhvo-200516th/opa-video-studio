#!/usr/bin/env python3
"""Chuyển cảnh mượt 3.6.3: chuyển động chồng hai phía điểm cắt (th_transitions._overlap / camera_continue / card_swipe có `before`),
easing bezier cho lớp phủ, thời lượng dài hơn, và cut_plan.plan_cuts_min không dùng kiểu nặng khi cắt giữa câu. Offline.
Chạy: ~/.venvs/video-skills/bin/python tests/test_trans_smooth.py"""
from __future__ import annotations

import sys

import test_th_transitions as T      # noqa: E402  (cũng thay cp.frame bằng bản giả, dựng clip mẫu)

TH, cp, fb = T.TH, T.cp, T.fb
SMOOTH_KINDS = sorted(set(TH.SMOOTH) | {"camera_continue"})
FPS = 30


def scale_at(clip: dict, fr: int) -> float:
    sc = clip.get("motion", {}).get("scale", 100)
    if not isinstance(sc, list):
        return sc
    return TH._scale_fn(clip)(fr / FPS)


def test_both_sides_move_and_validate() -> None:
    for kind in SMOOTH_KINDS:
        if kind == "smoke_veil" and not TH.SMOKE_SRC.exists():
            continue
        fx, (before, after) = T.fresh(), T.clips()
        fx.th_join(after, kind, before=before)
        T.validate(fx, before, after)
        nb, na = round(before["dur"] * FPS), round(after["dur"] * FPS)
        assert scale_at(after, 0) > 100.5 and abs(scale_at(after, na - 1) - 100) < 1e-6, (kind, "đầu cảnh sau")
        assert scale_at(before, nb - 1) > 100.5 and scale_at(before, nb - 12) == 100, (kind, "đuôi cảnh trước")
        # không giật: mỗi khung scale đổi ≤ 3 (đầu) / 4 (đuôi) điểm % và đầu cảnh sau không tăng
        head = [scale_at(after, i) for i in range(14)]
        assert all(0 <= a - b <= 3.0 for a, b in zip(head, head[1:])), (kind, head)
        tail = [scale_at(before, nb - 8 + i) for i in range(8)]
        assert all(0 <= b - a <= 4.0 for a, b in zip(tail, tail[1:])), (kind, tail)
        no_before = T.clips()[1]
        T.fresh().th_join(no_before, kind)                        # không `before` vẫn chạy (chỉ đầu cảnh sau)
        assert scale_at(no_before, 0) > 100.5, kind


def test_overlap_keeps_existing_zoom() -> None:
    fx, (before, after) = T.fresh(), T.clips()
    before["motion"] = {"scale": [[0, 100], [2.9667, 112]]}
    after["motion"] = {"scale": [[0, 100], [2.9667, 110]]}
    base_b, base_a = TH._scale_fn(before), TH._scale_fn(after)
    fx.th_join(after, "punch_settle", before=before)
    for c in (before, after):
        ts = [k[0] for k in c["motion"]["scale"]]
        assert ts == sorted(set(ts)) and ts[-1] < c["dur"], ts
    assert abs(scale_at(after, 60) - base_a(60 / FPS)) < 0.05 and abs(scale_at(before, 40) - base_b(40 / FPS)) < 0.05
    assert abs(scale_at(after, 0) - 110) < 0.05                    # 100 % × 1.10
    assert scale_at(before, 89) > base_b(89 / FPS) * 1.04          # đuôi phóng thêm ~5 %


def test_camera_continue_pans_same_direction() -> None:
    fx, (before, after) = T.fresh(), T.clips()
    fx.th_join(after, "camera_continue", before=before)
    xo = [k[1][0] for k in before["motion"]["position"]]
    xi = [k[1][0] for k in after["motion"]["position"]]
    assert xo[-1] < 540 - 10 and xi[0] > 540 + 10, (xo[-1], xi[0])      # đuôi trôi trái, đầu cảnh sau vào từ phải rồi cũng trôi trái
    assert all(a >= b for a, b in zip(xi, xi[1:])) and all(a >= b for a, b in zip(xo[-7:], xo[-6:]))
    assert max(abs(v - 540) for v in xo + xi) <= TH.PAN_PX + 1e-6 <= (TH.PAN_SCALE - 1) * 540, "dịch quá headroom → hở viền"
    for c in (before, after):
        assert any(e["effect"] == "directional_blur" for e in c["effects"]), c["name"]
    assert after["transition_in"]["effect"] == "cross_dissolve" and "camera_continue" in TH.KEYED_TH
    keyed = T.clips()[1]
    keyed["motion"] = {"position": [[0, [540, 960]], [1, [560, 960]]]}
    T.fresh().th_join(keyed, "camera_continue")                    # position keyframe riêng: bỏ phần dịch, không lỗi
    assert keyed["motion"]["position"] == [[0, [540, 960]], [1, [560, 960]]]


def test_overlays_use_bezier_not_linear() -> None:
    for kind in ("dip_to_paper", "paper_rip", "smoke_veil", "chapter_card_slam"):
        if kind == "smoke_veil" and not TH.SMOKE_SRC.exists():
            continue
        fx, (_, after) = T.fresh(), T.clips()
        fx.th_join(after, kind)
        for _, c in fx.items:
            assert all(len(k) > 2 and k[2] == "bezier" for k in c["opacity"]), (kind, c["opacity"])


def test_durations_longer_and_capped() -> None:
    visible = [k for k in cp.POOL_MIN if k not in ("punch_settle", "morph_smooth", "drift_reset") and k not in TH.ENERGY]   # năng động: nhanh có chủ đích
    for k in visible:
        assert TH.TH_FRAMES[k] >= 12, (k, TH.TH_FRAMES[k])
    assert TH.TH_FRAMES["morph_smooth"] >= 8 and TH.TH_FRAMES["punch_settle"] >= 12
    assert TH.TH_FRAMES["blur_dissolve_cut"] >= 16 and TH.TH_FRAMES["luma_fade_soft"] >= 16
    for k, n in TH.TH_FRAMES.items():
        assert n <= (TH.MAX_FRAMES_DISSOLVE if k in TH.DISSOLVE_OK else TH.MAX_FRAMES), (k, n)


def test_card_swipe_push_out_tail() -> None:
    fx, (before, after) = T.fresh(), T.clips()
    fx.th_join(after, "card_swipe", before=before)
    tail = [c for _, c in fx.items if c["name"].startswith("Đuôi cảnh trước")]
    assert len(tail) == 1 and tail[0]["in"] == before["in"] + before["dur"] and tail[0]["at"] == after["at"]
    assert tail[0]["motion"]["position"][0][1] == [540, 960] and tail[0]["motion"]["position"][-1][1][0] < -400
    assert tail[0]["motion"]["position"][-1][0] == after["motion"]["position"][-1][0]     # cùng nhịp với thẻ
    T.validate(fx, before, after)
    fx2, (b2, a2) = T.fresh(), T.clips()
    b2["in"] = 5.9                                               # nguồn 6 s: hết hình sau điểm cắt → không dựng đuôi
    fx2.th_join(a2, "card_swipe", before=b2)
    assert not fx2.items


def test_routing_no_heavy_mid_sentence() -> None:
    mid = lambda **kw: [cp.Cut(t=2.0 * i, a=("A.mp4", 1.0), b=("A.mp4", 3.0), before="đang nói dở", after="x", **kw) for i in range(24)]  # noqa: E731
    for seed in T.SEEDS:
        for cuts in (mid(), mid(b_kind="broll"), T.mixed(30)):
            plan = cp.plan_cuts_min(cuts, seed)
            for c in plan:
                if cp._mid_sentence(c):
                    assert c.info["join"] not in TH.HEAVY_TH, (seed, c.t, c.info["join"], c.before)
        heavy_ok = cp.plan_cuts_min(T.uniform("Câu xong."), seed)         # hết câu thì kiểu nặng vẫn dùng được
        assert {c.info["join"] for c in heavy_ok} & TH.HEAVY_TH, seed
    assert not cp._mid_sentence(cp.Cut(t=0, a=("a", 0), b=("b", 0)))     # chưa biết lời trước → không chặn
    assert not cp._mid_sentence(cp.Cut(t=0, a=("a", 0), b=("b", 0), before="đang nói dở", section=True))


def test_routing_mid_sentence_rotation_still_ok() -> None:
    for seed in T.SEEDS:
        plan = cp.plan_cuts_min(T.uniform("đang nói dở"), seed)
        T.check_rotation(plan)
        assert not {c.info["join"] for c in plan} & TH.HEAVY_TH, seed


if __name__ == "__main__":
    T.make_video()
    for name in [n for n in sorted(globals()) if n.startswith("test_")]:
        globals()[name]()
        print("ok", name)
    print("TẤT CẢ ĐẠT")
