#!/usr/bin/env python3
"""Chuyển cảnh năng động 3.6.4 cho talking-head minimal-edu: nháy sáng (flash_cut / double_flash / flicker_cut), nhóm máy quay
(zoom_punch_in / zoom_punch_out / whip_pan / spin_roll / lens_warp / impact_shake / rgb_split_cut), rò sáng + cháy phim
(light_leak / film_burn) — hợp lệ với fc_build.validate, chuyển động hai phía (before=), SFX trong catalog, và bộ xoay vòng
cut_plan.plan_cuts_min: nháy sáng ≤ 20 % cách ≥ 3 điểm cắt, cắt cứng ≤ 25 %, ≥ 8 kiểu, nhóm máy quay ở jump cut cùng khung.
Offline. Chạy: ~/.venvs/video-skills/bin/python tests/test_trans_energetic.py"""
from __future__ import annotations

import test_th_transitions as T      # noqa: E402  (cũng thay cp.frame bằng bản giả, dựng clip mẫu)

TH, cp = T.TH, T.cp
FPS = 30
FLASH = ["flash_cut", "double_flash", "flicker_cut"]
CAMERA = ["zoom_punch_in", "zoom_punch_out", "whip_pan", "spin_roll", "lens_warp", "impact_shake"]
NEW = FLASH + CAMERA + ["rgb_split_cut", "light_leak", "film_burn"]
STRICT = dict(share=0.25, kinds=8)


def kind_ok(kind: str) -> bool:
    return kind not in ("light_leak", "film_burn") or TH.trans_ready(kind)       # máy không có thư viện TNEDIT


def scale_at(clip: dict, fr: int) -> float:
    sc = clip.get("motion", {}).get("scale", 100)
    return TH._scale_fn(clip)(fr / FPS) if isinstance(sc, list) else sc


def test_kinds_registered() -> None:
    for k in NEW:
        assert k in TH.TH_KINDS and k in TH.TH_FRAMES and k in cp.SFX_OF, k
    assert set(FLASH) <= TH.FLASHY_TH and set(FLASH) <= cp.FLASHY and "vhs_rewind" in TH.FLASHY_TH
    assert not set(CAMERA) & TH.FLASHY_TH
    assert {"light_leak", "film_burn"} <= TH.HEAVY_TH                  # phủ khung: không dùng khi cắt giữa câu
    assert len(TH.TH_KINDS) >= 30


def test_each_new_kind_valid_and_two_sided() -> None:
    for kind in NEW:
        if not kind_ok(kind):
            continue
        fx, (before, after) = T.fresh(), T.clips()
        out = fx.join(after, kind, before=before)
        assert out is after, kind
        T.validate(fx, before, after)
        assert all(c["kind"] in T.CATALOG or c["kind"] == "own_audio" for c in fx.cues), (kind, fx.cues)
        assert fx.cues, kind
        nb, na = round(before["dur"] * FPS), round(after["dur"] * FPS)
        assert scale_at(after, 0) > 100.5 and abs(scale_at(after, na - 1) - 100) < 1e-6, (kind, "đầu cảnh sau")
        if kind not in ("light_leak", "film_burn"):                    # hai kiểu rò sáng: đuôi cảnh trước chỉ phóng nhẹ khi có `before`
            assert scale_at(before, nb - 1) > 100.5, (kind, "đuôi cảnh trước")
        quiet = T.fresh()
        quiet.th_join(T.clips()[1], kind, cue_sfx=False)
        assert not quiet.cues, kind
        T.fresh().th_join(T.clips()[1], kind)                          # không `before` vẫn chạy


def test_flash_overlays_peak_on_cut() -> None:
    for kind in FLASH:
        fx, (before, after) = T.fresh(), T.clips()
        fx.th_join(after, kind, before=before)
        flashes = [c for _, c in fx.items if c.get("opacity")]
        assert flashes, kind
        c = flashes[0]
        ks = c["opacity"]
        assert ks[0][1] == 0 and ks[-1][1] == 0 and ks[-1][0] < c["dur"], (kind, ks)
        cut_t = after["at"] - c["at"]                                   # giây của khung cắt trong overlay
        near = [k for k in ks if abs(k[0] - cut_t) <= 1 / FPS + 1e-6]
        assert near and max(k[1] for k in near) >= 80, (kind, cut_t, ks)   # đỉnh trắng phủ khung cắt
        assert c["at"] < after["at"] < c["at"] + c["dur"], kind
    fx, (_, after) = T.fresh(), T.clips()
    fx.th_join(after, "double_flash")
    ops = [k[1] for k in fx.items[0][1]["opacity"]]
    peaks = [i for i in range(1, len(ops) - 1) if ops[i] >= ops[i - 1] and ops[i] > ops[i + 1] and ops[i] >= 50]
    assert len(peaks) == 2, ops


def test_camera_kinds_move_clip() -> None:
    fx, (before, after) = T.fresh(), T.clips()
    fx.th_join(after, "whip_pan", before=before)
    xo = [k[1][0] for k in before["motion"]["position"]]
    xi = [k[1][0] for k in after["motion"]["position"]]
    assert abs(xo[-1] - 540) > 20 and abs(xi[0] - 540) > 20 and (xo[-1] - 540) * (xi[0] - 540) < 0, (xo[-1], xi[0])   # đuôi trôi, đầu đến từ phía đối diện
    assert max(abs(v - 540) for v in xo + xi) <= (scale_at(after, 0) / 100 - 1) * 540 + 1e-6, "dịch quá headroom → hở viền"
    assert any(e["effect"] == "directional_blur" for e in after["effects"])
    fx, (before, after) = T.fresh(), T.clips()
    fx.th_join(after, "spin_roll", before=before)
    ro, ri = before["motion"]["rotation"], after["motion"]["rotation"]
    assert ro[-1][1] * ri[0][1] < 0 and ri[-1][1] == 0, (ro, ri)
    na = round(after["dur"] * FPS)
    for fr, k in enumerate(ri[:10]):                                    # xoay đủ nhỏ để scale che hết góc: s ≥ cosθ + (H/W)·sinθ
        import math
        th = math.radians(abs(k[1]))
        assert scale_at(after, round(k[0] * FPS)) / 100 >= math.cos(th) + 1920 / 1080 * math.sin(th) - 1e-3, (fr, k)
    assert scale_at(after, na - 1) == 100
    fx, (before, after) = T.fresh(), T.clips()
    fx.th_join(after, "lens_warp", before=before)
    assert any(e["effect"] == "lens_distortion" for e in after["effects"] + before["effects"])
    fx, (before, after) = T.fresh(), T.clips()
    fx.th_join(after, "impact_shake", before=before)
    assert any(e["effect"] == "camera_shake" for e in after["effects"]) and scale_at(before, 89) > 100.5


def test_direction_alternates() -> None:
    fx = T.fresh()
    first = []
    for _ in range(2):
        b, a = T.clips()
        fx.th_join(a, "whip_pan", before=b)
        first.append(a["motion"]["position"][0][1][0] - 540)
    assert first[0] * first[1] < 0, first


def test_existing_zoom_kept() -> None:
    fx, (before, after) = T.fresh(), T.clips()
    after["motion"] = {"scale": [[0, 100], [2.9667, 110]]}
    base = TH._scale_fn(after)
    fx.th_join(after, "zoom_punch_in", before=before)
    assert abs(scale_at(after, 60) - base(60 / FPS)) < 0.05 and scale_at(after, 0) > 110
    keyed = T.clips()[1]
    keyed["motion"] = {"rotation": [[0, 0], [1, 3]], "position": [[0, [540, 960]], [1, [560, 960]]]}
    for kind in ("spin_roll", "whip_pan"):
        T.fresh().th_join(dict(keyed), kind)                           # đã có keyframe riêng: bỏ phần dịch / xoay, không lỗi


def test_light_leak_and_film_burn() -> None:
    if not (TH.trans_ready("light_leak") and TH.trans_ready("film_burn")):
        return
    for kind in ("light_leak", "film_burn"):
        fx, (before, after) = T.fresh(), T.clips()
        fx.th_join(after, kind, before=before)
        assert len(fx.items) == 1 and fx.items[0][1]["name"].startswith("Chuyển cảnh " + kind), kind
        assert after["name"].endswith(TH.JOIN_MARK + kind)
    fx = T.fresh()
    names = set()
    for _ in range(3):
        b, a = T.clips()
        fx.th_join(a, "light_leak", before=b)
        names.add(fx.items[-1][1]["in"])
    assert len(names) == 3, "mỗi lần một biến thể khác"


def test_th_join_via_motionfx_join_and_cut_fx() -> None:
    fx, (before, after) = T.fresh(), T.clips()
    fx.cut_fx(after["at"], "whip_pan", after, clip_before=before)       # đường cut_fx truyền clip_before cho kiểu talking-head
    assert before["motion"]["position"] and after["name"].endswith("whip_pan")


# ---------- planner ----------
def check_energetic(plan: list[cp.Cut], share: float = 0.25, kinds: int = 8, flashy: float = 0.2) -> None:
    T.check_rotation(plan, share=share, kinds=kinds)
    joins = [c.info["join"] for c in plan]
    n = len(joins)
    idx = [i for i, j in enumerate(joins) if j in cp.FLASHY]
    assert len(idx) <= flashy * n + 1e-9, ("nháy sáng > 20 %", joins)
    assert all(b - a >= cp.FLASHY_GAP for a, b in zip(idx, idx[1:])), ("nháy sáng sát nhau", idx, joins)
    soft = {j for j in joins if j not in TH.HARD_KINDS}
    assert soft & (set(CAMERA) | {"camera_continue", "punch_settle"}), ("thiếu nhóm máy quay", sorted(soft))


def test_planner_energetic_rotation() -> None:
    for seed in T.SEEDS:
        for cuts in (T.mixed(24), T.uniform("đang nói dở", n=24), T.uniform("Câu xong.", n=24), T.uniform("Câu xong.", True, 24)):
            check_energetic(cp.plan_cuts_min(cuts, seed))


def test_planner_uses_new_kinds_and_mixes_families() -> None:
    seen: set[str] = set()
    for seed in T.SEEDS:
        for cuts in (T.mixed(30), T.uniform("Câu xong.", n=30), T.uniform("Câu xong.", True, 30), T.uniform("đang nói dở", n=30)):
            seen |= {c.info["join"] for c in cp.plan_cuts_min(cuts, seed)}
    assert set(FLASH) & seen and set(CAMERA) & seen, sorted(seen)
    assert {"light_leak", "film_burn"} & seen and "rgb_split_cut" in seen, sorted(seen)
    assert len(seen & TH.TH_KINDS) >= 22, sorted(seen)


def test_leaks_only_at_topic_change() -> None:
    for seed in T.SEEDS:
        plan = cp.plan_cuts_min(T.uniform("Câu xong.", n=30), seed)
        for c in plan:
            if c.info["join"] in ("light_leak", "film_burn"):
                assert c.info["kind"] in ("jump cut · đổi phần", "đổi cảnh", "vào B-roll", "ra B-roll"), (c.t, c.info)
        sec = cp.plan_cuts_min(T.uniform("Câu xong.", True, 30), seed)
        assert {"light_leak", "film_burn"} & {c.info["join"] for c in sec}, seed


def test_emphasis_context() -> None:
    cuts = [cp.Cut(t=2.0 * i, a=("A.mp4", 1.0), b=("A.mp4", 3.0), before="đang nói dở", after="x", emphasis=True) for i in range(24)]
    for seed in T.SEEDS:
        plan = cp.plan_cuts_min(cuts, seed)
        assert all(c.info["kind"] == "jump · nhấn" for c in plan)
        T.check_rotation(plan, share=0.25, kinds=8)
        assert {c.info["join"] for c in plan} & set(CAMERA), seed
    plain = cp.plan_cuts_min(T.uniform("đang nói dở", n=24), 0)         # không đánh dấu nhấn: ngữ cảnh cũ
    assert all(c.info["kind"] == "jump · giữa câu" for c in plain)


def test_defaults_and_profile_keys() -> None:
    d = cp.MIN_DEFAULTS
    assert d["max_flashy_share"] == 0.2 and d["max_hard_cut_share"] == 0.25 and d["min_distinct_transitions"] == 8
    zero = cp.plan_cuts_min(T.uniform("Câu xong.", n=30), 1, {"cuts": {"max_flashy_share": 0.0}})
    assert not {c.info["join"] for c in zero} & cp.FLASHY                # hồ sơ cũ (JSON 0.0) vẫn không nháy sáng


if __name__ == "__main__":
    T.make_video()
    for name in [n for n in sorted(globals()) if n.startswith("test_")]:
        globals()[name]()
        print("ok", name)
    print("TẤT CẢ ĐẠT")
