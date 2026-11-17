#!/usr/bin/env python3
"""Chuyển cảnh talking-head 3.6.2 (th_transitions + cut_plan.plan_cuts_min): mọi kiểu mới cho clip hợp lệ với fc_build.validate,
id FilmCraft có trong danh mục, giấy rách khớp hai nửa, bộ xoay vòng minimal-edu đủ luật với 5 seed, planner mặc định không đổi.
Offline (ffmpeg chỉ để tạo 1 clip mẫu). Chạy: ~/.venvs/video-skills/bin/python tests/test_th_transitions.py"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/apps/craft-handoff/tools"))
import cut_plan as cp  # noqa: E402
import fc_build as fb  # noqa: E402
import fx_gfx as G  # noqa: E402
import motion_fx as M  # noqa: E402
import th_transitions as TH  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="th_trans_"))
VID = TMP / "src.mp4"
CATALOG = json.loads((ROOT / "assets/motion-fx/sfx_catalog.json").read_text(encoding="utf-8"))["kinds"]
KB_IDS = set(re.findall(r"^- `(\w+)` — ", (ROOT / "references/kb-master-video-edit.md").read_text(encoding="utf-8"), re.M))
SEEDS = range(5)


def make_video() -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=gray:s=1080x1920:r=30:d=6",
                    "-pix_fmt", "yuv420p", str(VID)], check=True)


def clips() -> tuple[dict, dict]:
    base = {"src": str(VID), "audio": False}
    return ({**base, "at": 0.0, "dur": 3.0, "in": 0.0, "name": "A"}, {**base, "at": 3.0, "dur": 3.0, "in": 1.0, "name": "B"})


def fresh() -> M.MotionFX:
    return M.MotionFX(gfx_dir=TMP / "gfx", fps=30, name="T")


def validate(fx: M.MotionFX, before: dict, after: dict) -> None:
    spec = {"name": "t", "width": 1080, "height": 1920, "fps": 30,
            "tracks": [{"type": "video", "name": "V1", "clips": [before, after]}, *fx.tracks()]}
    fb.validate(spec)                                           # ném SpecError nếu khoá / giá trị clip sai


# ---------- th_transitions ----------
def test_each_kind_valid_keys() -> None:
    assert len(TH.TH_KINDS) >= 16
    for kind in sorted(TH.TH_KINDS):
        if kind == "smoke_veil" and not TH.SMOKE_SRC.exists():
            continue                                            # máy không có thư viện TNEDIT
        fx, (before, after) = fresh(), clips()
        out = fx.join(after, kind)
        assert out is after, kind
        validate(fx, before, after)
        assert all(c["kind"] in CATALOG or c["kind"] == "own_audio" for c in fx.cues), (kind, [c["kind"] for c in fx.cues])
        lead = 0.6 if kind in ("light_leak", "film_burn") else 0.35        # overlay TNEDIT: khung sáng nhất cách đầu clip 0,4 s
        assert all(c["t"] >= after["at"] - lead and c.get("max_pre", 0) <= lead for c in fx.cues), (kind, fx.cues)
        quiet = fresh()
        quiet.th_join(clips()[1], kind, cue_sfx=False)
        assert not quiet.cues, kind


def test_filmcraft_ids_in_catalog() -> None:
    assert KB_IDS >= {"morph_cut", "blur_dissolve", "clock_wipe", "iris_round", "cross_dissolve"}, "đọc sai danh mục"
    for kind, (eff, frames, sfx) in TH.TH_JOINS.items():
        assert eff in KB_IDS, (kind, eff)
        assert 1 <= frames <= TH.MAX_FRAMES_DISSOLVE and all(s in CATALOG for s in sfx), kind
    for kind in TH.TH_KINDS:
        n = TH.TH_FRAMES[kind]
        assert n <= (TH.MAX_FRAMES_DISSOLVE if kind in TH.DISSOLVE_OK else TH.MAX_FRAMES), (kind, n)
    fx, (_, after) = fresh(), clips()
    fx.th_join(after, "dip_to_paper", black=True)
    assert after["transition_in"]["effect"] == "dip_to_black" and "dip_to_black" in KB_IDS and not fx.items


def test_catalog_paper_kind() -> None:
    p = CATALOG["paper"]
    assert p["tier"] == "soft" and p["files"] and all(f.startswith("HMC:01_vut_gio_chuyen_canh/") for f in p["files"]), p


def test_overlays_inside_clip() -> None:
    """Keyframe cuối nằm trong clip: _frame_keys sẽ gộp khoá vượt khung cuối vào khoá trước (làm mất cú dịch)."""
    for kind in ("dip_to_paper", "paper_rip", "chapter_card_slam"):
        fx, (_, after) = fresh(), clips()
        fx.th_join(after, kind)
        assert fx.items, kind
        for _, c in fx.items:
            ks = c["opacity"] if isinstance(c.get("opacity"), list) else c["motion"]["scale"]
            assert 0 < len(ks) >= 2 and ks[-1][0] < c["dur"], (kind, ks)
    fx, (_, after) = fresh(), clips()
    fx.th_join(after, "paper_rip")
    mo = {h: next(c["motion"] for _, c in fx.items if f"rách {h}" in c["name"]) for h in ("top", "bottom")}
    assert mo["top"]["rotation"][-1][1] == 9 and mo["bottom"]["rotation"][-1][1] == -6 and len(fx.items) == 2
    assert mo["top"]["position"][-1][1][1] < 0 and mo["bottom"]["position"][-1][1][1] > 1920


def test_drift_reset_alternates_and_guards() -> None:
    fx = fresh()
    ends = []
    for _ in range(2):
        c = clips()[1]
        fx.join(c, "drift_reset")
        ends.append(c["motion"]["position"][-1][1][0] - 540)
        assert c["motion"]["scale"][0][1] == 100 and c["motion"]["scale"][-1][1] == 105
    assert ends[0] == -ends[1] != 0, ends
    keyed = clips()[1]
    keyed["motion"] = {"scale": [[0, 100], [1, 110]]}
    try:
        fx.join(keyed, "drift_reset")
    except ValueError:
        return
    raise AssertionError("drift_reset phải báo lỗi khi clip đã có keyframe scale")


def test_punch_settle_and_card_swipe() -> None:
    fx, (_, after) = fresh(), clips()
    fx.join(after, "punch_settle")
    assert after["motion"]["scale"][0][1] == 110 and after["motion"]["scale"][-1][1] == 100
    fx2, (_, b2) = fresh(), clips()
    fx2.join(b2, "card_swipe")
    assert [e["effect"] for e in b2["effects"]] == ["directional_blur", "rounded_crop", "drop_shadow"]
    assert b2["motion"]["scale"][0][1] > 92 and b2["motion"]["scale"][-1][1] == 92
    assert b2["motion"]["position"][0][1][0] > 1080 and b2["motion"]["position"][-1][1] == [540, 960]


def test_j_cut_time_and_chapter_text() -> None:
    assert TH.j_cut_time(5.0) == round(5.0 - 10 / 30, 4)
    fx, (_, after) = fresh(), clips()
    out = fx.th_join(after, "j_cut_return")
    assert out is after and "transition_in" not in after and not fx.cues and not fx.items
    fx = fresh()
    fx.th_join(clips()[1], "chapter_card_slam", text="Bước 3")
    assert any(c.get("text") == "Bước 3" for _, c in fx.items)


def test_torn_paper_halves_fit() -> None:
    top = np.asarray(Image.open(G.torn_paper(TMP / "gfx", "tt", "top", 2)))[..., 3] > 0
    bot = np.asarray(Image.open(G.torn_paper(TMP / "gfx", "tb", "bottom", 2)))[..., 3] > 0
    assert top.shape == (1920, 1080) and not (top & bot).any()
    assert 0.45 < top.mean() < 0.55 and 0.45 < bot.mean() < 0.55
    # đường rách gồ ghề (không phải một đường thẳng)
    edge = top.sum(axis=0)
    assert edge.max() - edge.min() > 40, "mép rách phải gồ ghề"
    try:
        G.torn_paper(TMP / "gfx", "bad", "left", 0)
    except ValueError:
        return
    raise AssertionError("half lạ phải báo lỗi")


# ---------- cut_plan ----------
_ARR: dict = {}


def stub_frame(src: str, t: float) -> np.ndarray:
    if src not in _ARR:
        _ARR[src] = np.random.RandomState(sum(map(ord, src))).rand(cp.H, cp.W).astype(np.float32) * 255
    return _ARR[src]


cp.frame = stub_frame


def mixed(n: int = 20) -> list[cp.Cut]:
    cuts = []
    for i in range(n):
        bk, ak = ("broll" if i in (4, 11) else "aroll"), ("broll" if i in (5, 12) else "aroll")
        a_src = "B1.mp4" if ak == "broll" else "A.mp4"
        b_src = "B1.mp4" if bk == "broll" else ("C.mp4" if i in (8, 15) else "A.mp4")
        before = "Câu xong." if i % 3 == 1 else ("Một ý, " if i % 5 == 0 else "đang nói dở")
        cuts.append(cp.Cut(t=2.0 * i, a=(a_src, 1.0), b=(b_src, 3.0), a_kind=ak, b_kind=bk, before=before, after="x",
                           section=i in (8, 16)))
    return cuts


def uniform(before: str, section: bool = False, n: int = 20) -> list[cp.Cut]:
    return [cp.Cut(t=2.0 * i, a=("A.mp4", 1.0), b=("A.mp4", 3.0), before=before, after="x", section=section) for i in range(n)]


def check_rotation(plan: list[cp.Cut], share: float = 0.4, row: int = 2, kinds: int = 6, kind_share: float = 0.2, gap: int = 3) -> None:
    joins = [c.info["join"] for c in plan]
    n = len(joins)
    hard = [j in TH.HARD_KINDS for j in joins]
    assert sum(hard) <= share * n + 1e-9, ("cắt cứng", joins)
    run = 0
    for h in hard:
        run = run + 1 if h else 0
        assert run <= row, ("cắt cứng liền", joins)
    soft = [j for j in joins if j not in TH.HARD_KINDS]
    assert len(set(soft)) >= kinds, ("thiếu kiểu", sorted(set(soft)))
    assert max(soft.count(k) for k in set(soft)) <= kind_share * n + 1e-9, ("kiểu quá 20 %", joins)
    for i, j in enumerate(joins):
        assert j in TH.HARD_KINDS or j not in joins[max(0, i - gap):i], ("lặp trong 3 điểm cắt", i, joins)
        assert TH.TH_FRAMES.get(j, 0) <= (TH.MAX_FRAMES_DISSOLVE if j in TH.DISSOLVE_OK else TH.MAX_FRAMES), j
        assert j in cp.SFX_OF and plan[i].info["sfx"], j
    for k in TH.ONE_PER_VIDEO:
        assert joins.count(k) <= 1, (k, joins)


def test_planner_rotation_mixed() -> None:
    for seed in SEEDS:
        plan = cp.plan_cuts_min(mixed(), seed)
        check_rotation(plan)
        assert {c.info["join"] for c in plan} & TH.TH_KINDS, seed


def test_planner_rotation_worst_cases() -> None:
    for seed in SEEDS:
        for cuts in (uniform("đang nói dở"), uniform("Câu xong."), uniform("Câu xong.", section=True)):
            check_rotation(cp.plan_cuts_min(cuts, seed))


def test_planner_reads_rules() -> None:
    no_hard = {"cuts": {"max_hard_cut_share": 0.0}}
    for seed in SEEDS:
        plan = cp.plan_cuts_min(mixed(), seed, no_hard)
        assert not any(c.info["join"] in TH.HARD_KINDS for c in plan), seed
        loose = cp.plan_cuts_min(uniform("Câu xong."), seed, {"cuts": {"max_hard_cut_share": 0.8, "max_hard_in_row": 4}})
        check_rotation(loose, share=0.8, row=4)
    j = [c for c in cp.plan_cuts_min(uniform("Câu xong."), 0) if c.info["join"] == "j_cut_return"]
    assert j and all(c.info["lead_s"] == round(10 / 30, 4) for c in j)


def test_minimal_edu_profile_loads() -> None:
    import style_profile as sp
    plan = cp.plan_cuts_min(mixed(), 1, sp.load(name="minimal-edu"))
    assert len(plan) == 20 and all(c.info["join"] in cp.SFX_OF for c in plan)


# ---------- planner mặc định không đổi (ghi từ HEAD trước khi sửa) ----------
EXPECT_SEED3 = ['zoom + punch', 'light_sweep', 'zoom + punch', 'slice', 'grid_reveal + light_leak', 'whip', 'zoom + punch', 'spring',
                'film_burn', 'zoom + punch', 'panel_wipe', 'grid_reveal + flash_burst', 'zoom', 'travel', 'light_sweep', 'glass', 'spin',
                'zoom + punch', 'zoom + punch', 'film_roll']
EXPECT_SEED0 = ['zoom + punch', 'zoom_through', 'zoom + punch', 'slice', 'grid_reveal + flash_burst', 'zoom', 'zoom + punch', 'spin_zoom',
                'panel_wipe', 'zoom + punch', 'light_sweep', 'grid_reveal + light_leak', 'slide', 'spring', 'light_sweep', 'liquid',
                'split_slide', 'zoom + punch', 'zoom + punch', 'travel']


def test_default_planner_unchanged() -> None:
    assert [c.info["join"] for c in cp.plan_cuts(mixed(), seed=3)] == EXPECT_SEED3
    assert [c.info["join"] for c in cp.plan_cuts(mixed(), seed=0)] == EXPECT_SEED0


def test_energetic_options_opt_in() -> None:
    plan = cp.plan_cuts(mixed(40), seed=1, energetic=True)
    joins = {c.info["join"].split(" + ")[-1] for c in plan}
    assert joins & {"impact_shake", "pop_in", "neon_wipe", "mosaic_pixel", "vhs_rewind"}, joins
    assert all(c.info["join"] in cp.SFX_OF or c.info["join"].startswith(("grid_reveal", "strip_reveal")) for c in plan)
    plain = {c.info["join"].split(" + ")[-1] for c in cp.plan_cuts(mixed(40), seed=1)}
    assert not plain & {"impact_shake", "pop_in", "neon_wipe", "mosaic_pixel", "vhs_rewind"}, plain
    best = cp.plan_cuts_best(mixed(40), seed=1, energetic=True)
    assert len(best) == 40


if __name__ == "__main__":
    make_video()
    for name in [n for n in sorted(globals()) if n.startswith("test_")]:
        globals()[name]()
        print("ok", name)
    print("TẤT CẢ ĐẠT")
