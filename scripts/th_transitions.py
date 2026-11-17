"""Chuyển cảnh talking-head (3.6.2): các kiểu mới cho hồ sơ minimal-edu, thay cho "cắt cứng 80 %".

    fx.join(clip_after, "soft_wipe")                    # clip_after = clip ngay sau điểm cắt; clip_after["at"] = điểm cắt
    fx.th_join(clip_after, "paper_rip", cue_sfx=True)   # như join, nhận thêm tham số riêng (vd text= cho chapter_card_slam)

Bảng TH_JOINS dùng `transition_in` có sẵn của FilmCraft (spec chỉ nhận {effect, frames}: tham số của chuyển cảnh nằm ở mặc
định của FilmCraft — blur 40, feather 300, tâm iris / clock = giữa khung, góc page_peel = dưới phải, hướng push cố định).
Các kiểu còn lại dựng bằng keyframe / PNG (dip_to_paper: dip_to_color mặc định ĐỎ nên không dùng được cho giấy trắng).
Mỗi hàm sửa `clip` tại chỗ, đẩy lớp phủ vào `fx.items` và SFX vào `fx.cues` (kind "paper" mới trong sfx_catalog.json).
"""
from __future__ import annotations

from pathlib import Path

# kiểu → (id chuyển cảnh FilmCraft, số khung, SFX). Số khung ≤ 12 (hoà tan ≤ 18); SFX nhẹ ("paper" = swish tầng soft).
TH_JOINS = {
    "morph_smooth": ("morph_cut", 5, []),
    "blur_dissolve_cut": ("blur_dissolve", 8, ["paper"]),
    "soft_wipe": ("soft_wipe", 9, ["paper"]),
    "luma_fade_soft": ("luma_fade", 10, []),
    "clock_wipe_step": ("clock_wipe", 10, ["pop"]),
    "iris_round_focus": ("iris_round", 10, ["pop"]),
    "camera_continue": ("push", 7, ["whoosh"]),
    "page_peel_in": ("page_peel", 12, ["pop"]),               # 3D: tính vào hạn mức 3D (remix_rules.THREE_D_TR)
    # nhóm hợp phong cách năng động (E-fit, catalog mục A/C)
    "pop_in": ("pop_motion", 8, ["pop"]),
    "neon_wipe": ("neon_wipe", 8, ["whoosh"]),
    "mosaic_pixel": ("mosaic_transition", 8, ["data_beep"]),
}
KEYED_TH = {"punch_settle": 10, "drift_reset": 0, "j_cut_return": 0, "dip_to_paper": 10, "paper_rip": 12, "card_swipe": 9,
            "smoke_veil": 18, "impact_shake": 8, "chapter_card_slam": 12, "vhs_rewind": 9}
TH_KINDS = set(TH_JOINS) | set(KEYED_TH)
TH_FRAMES = {**{k: v[1] for k, v in TH_JOINS.items()}, **KEYED_TH}   # số khung chuyển cảnh (chapter_card_slam: 6 vào + 6 ra)
DISSOLVE_OK = {"smoke_veil"}                       # được tới 18 khung; còn lại ≤ 12
HARD_KINDS = {"hard_cut", "j_cut_return"}          # j_cut_return = cắt cứng có dẫn hình trước lời 10 khung
FLASHY_TH = {"vhs_rewind"}                         # nháy bán phần (rgb_split + vhs_damage): chịu hạn mức nháy sáng
ONE_PER_VIDEO = {"paper_rip", "smoke_veil", "page_peel_in", "ink_matte_reveal"}   # giấy rách / khói / mực / 3D: ≤ 1 lần mỗi video
J_LEAD_FRAMES = 10
PRO_DIR = Path.home() / "Thanh/Media/TNEDIT/05_Hieu_Ung_Chuyen_Canh/Overlay_Video/PR_Overlays"
SMOKE_SRC = PRO_DIR / "OVL_Smoke_Matte_white_smoke_with_black_background_1960.mp4"


def _keyed(v) -> bool:
    return isinstance(v, list) and bool(v) and isinstance(v[0], list)


def _last(fx, c: dict) -> float:
    """Giây của khung cuối clip: keyframe cuối phải nằm trong clip (fx._frame_keys gộp khoá vượt khung cuối vào khoá trước)."""
    return (round(c["dur"] * fx.fps) - 1) / fx.fps


def _tin(clip: dict, effect: str, frames: int) -> dict:
    clip["transition_in"] = {"effect": effect, "frames": frames}
    return clip


def _cue(fx, on: bool, t: float, kind: str, max_pre: float, why: str) -> None:
    if on:
        fx.cues.append({"t": t, "kind": kind, "max_pre": round(max_pre, 3), "why": why})


def j_cut_time(speech_t: float, fps: int = 30) -> float:
    """Điểm cắt của j_cut_return: hình người nói vào TRƯỚC chữ đầu câu `speech_t` 10 khung (tiếng không đổi)."""
    return round(speech_t - J_LEAD_FRAMES / fps, 4)


def _simple(fx, clip: dict, kind: str, cue_sfx: bool) -> dict:
    eff, frames, sfx = TH_JOINS[kind]
    _tin(clip, eff, frames)
    for s in sfx:                                   # chuyển cảnh căn giữa điểm cắt: tiếng chỉ vào từ nửa đầu của nó
        _cue(fx, cue_sfx, clip["at"], s, frames / 2 / fx.fps + 0.02, f"chuyển cảnh {kind}")
    return clip


def punch_settle(fx, clip: dict, cue_sfx: bool = True) -> dict:
    """Ngược với zoom + punch: cảnh sau vào 110 → 100 % trong 10 khung (easeIn), nhoè 6 → 0 trong 2 khung. Giữ scale có sẵn dạng keyframe."""
    mo = clip.setdefault("motion", {})
    if not _keyed(mo.get("scale")):
        base = mo.get("scale", 100)
        mo["scale"] = fx._frame_keys([[0, round(base * 1.1, 2)], [10 / fx.fps, base, "easeIn"]], clip["dur"])
    fx._fx(clip, "gaussian_blur", {"blurriness": fx._frame_keys([[0, 6], [2 / fx.fps, 0, "easeIn"]], clip["dur"])})
    _cue(fx, cue_sfx, clip["at"], "paper", 0.12, "punch_settle")
    return clip


def drift_reset(fx, clip: dict, cue_sfx: bool = True) -> dict:
    """Mỗi đoạn trôi chậm 100 → 105 % kèm dịch ngang 14 px, về lại ở điểm cắt kế; hướng dịch đảo chiều mỗi lần gọi."""
    mo = clip.get("motion", {})
    if _keyed(mo.get("scale")):
        raise ValueError(f"clip «{clip.get('name')}» đã có keyframe motion.scale riêng — xung đột với drift_reset")
    x, y = fx._pos_of(clip)
    sign = 1 if fx.th_state["drift"] % 2 == 0 else -1
    fx.th_state["drift"] += 1
    base = mo.get("scale", 100)
    clip.setdefault("motion", {}).update({
        "scale": fx._frame_keys([[0, base], [_last(fx, clip), round(base * 1.05, 2)]], clip["dur"]),
        "position": fx._frame_keys([[0, [x, y]], [_last(fx, clip), [x + sign * 14, y]]], clip["dur"])})
    return clip


def j_cut_return(fx, clip: dict, cue_sfx: bool = True) -> dict:
    """Cắt cứng, không thêm gì lên clip: phần "J" nằm ở điểm cắt (xem j_cut_time) và tiếng giữ nguyên."""
    return clip


def dip_to_paper(fx, clip: dict, cue_sfx: bool = True, black: bool = False) -> dict:
    """Chìm vào giấy trắng (PNG paper_bg, opacity 0 → 100 → 0 trong 10 khung, điểm cắt nằm dưới) hoặc `black`: dip_to_black."""
    if black:
        return _tin(clip, "dip_to_black", 10)
    import fx_gfx as G
    p = fx.image(G.paper_bg(fx.gfx_dir, "dip_paper", "white", 0), clip["at"] - 5 / fx.fps, 10 / fx.fps, lane="trans", name="Dip giấy")
    p["opacity"] = fx._frame_keys([[0, 0], [5 / fx.fps, 100], [_last(fx, p), 0]], p["dur"])
    return _tin(clip, "cross_dissolve", 1)


def paper_rip(fx, clip: dict, cue_sfx: bool = True, seed: int = 0) -> dict:
    """Hai nửa giấy rách mép phủ khung (2 khung), điểm cắt nằm dưới, rồi trượt tách ra: nửa trên +9° lên, nửa dưới −6° xuống (12 khung)."""
    import fx_gfx as G
    n, at = 12 / fx.fps, clip["at"] - 4 / fx.fps
    for half, rot, dy in (("top", 9, -1250), ("bottom", -6, 1250)):
        c = fx.image(G.torn_paper(fx.gfx_dir, f"torn_{half}_{seed}", half, seed), at, n, lane="trans", name=f"Giấy rách {half}")
        c["opacity"] = fx._frame_keys([[0, 0], [2 / fx.fps, 100]], c["dur"])
        c["motion"] = {"position": fx._frame_keys([[0, [540, 960]], [4 / fx.fps, [540, 960]], [_last(fx, c), [540, 960 + dy], "easeIn"]], c["dur"]),
                       "rotation": fx._frame_keys([[0, 0], [4 / fx.fps, 0], [_last(fx, c), rot, "easeIn"]], c["dur"])}
    _cue(fx, cue_sfx, clip["at"], "paper", 4 / fx.fps, "paper_rip")
    return _tin(clip, "cross_dissolve", 1)


def card_swipe(fx, clip: dict, cue_sfx: bool = True, scale: float = 92) -> dict:
    """B-roll thành thẻ bo góc có bóng, trượt từ phải vào 9 khung (easeIn) rồi nằm yên ở `scale` %."""
    x, y = fx._pos_of(clip)
    clip.setdefault("motion", {}).update({
        "scale": scale, "position": fx._frame_keys([[0, [x + 1100, y]], [9 / fx.fps, [x, y], "easeIn"]], clip["dur"])})
    fx._fx(clip, "rounded_crop", {"radius": 36, "border": 6, "border_color": "#FAFAFA"})
    fx._fx(clip, "drop_shadow", {"opacity": 55, "distance": 14, "softness": 40})
    _cue(fx, cue_sfx, clip["at"], "whoosh", 9 / 2 / fx.fps + 0.02, "card_swipe")
    return clip


def smoke_veil(fx, clip: dict, cue_sfx: bool = True) -> dict:
    """Khói trắng (OVL_Smoke_Matte, blend screen) mờ 0 → 70 → 0 trong 18 khung phủ điểm cắt, cross_dissolve 6 khung bên dưới."""
    n = 18 / fx.fps
    c = fx.image(str(SMOKE_SRC), clip["at"] - n / 2, n, lane="trans", name="Màn khói")
    c.update({"in": 1.0, "audio": False, "blend": "screen", "motion": {"rotation": 90, "scale": 177.8}})
    c["opacity"] = fx._frame_keys([[0, 0], [n / 2, 70], [_last(fx, c), 0]], c["dur"])
    _cue(fx, cue_sfx, clip["at"], "leak", n / 2, "smoke_veil")
    return _tin(clip, "cross_dissolve", 6)


def impact_shake(fx, clip: dict, cue_sfx: bool = True) -> dict:
    """Rung máy 28 → 0 (không loé trắng như flash_shake): camera_shake zoom 4, nhoè 40; cho câu chốt / từ khoá."""
    fx._fx(clip, "camera_shake", {"amount": [[0, 28], [fx._k(clip, 0.35), 0]], "rotation": 1.5, "zoom": 4, "frequency": 9,
                                  "complexity": 3, "motion_blur": 40})
    _cue(fx, cue_sfx, clip["at"], "boom_pre", 0.1, "impact_shake")
    _cue(fx, cue_sfx, clip["at"], "key_hit", 0.05, "impact_shake")
    return clip


def vhs_rewind(fx, clip: dict, cue_sfx: bool = True) -> dict:
    """vhs_damage 9 khung + rgb_split 30 → 0 (cho "lỗi" / nhớ lại)."""
    _tin(clip, "vhs_damage", 9)
    fx._fx(clip, "rgb_split", {"mode": "Linear", "amount": [[0, 30], [fx._k(clip, 0.22), 0]], "angle": 0})
    _cue(fx, cue_sfx, clip["at"], "glitch", 9 / 2 / fx.fps + 0.02, "vhs_rewind")
    return clip


def chapter_card_slam(fx, clip: dict, cue_sfx: bool = True, text: str | None = None) -> dict:
    """Thẻ giấy phủ khung 24 khung (vào 6 · giữ 12 · ra 6, scale 108 → 100 % easeIn), điểm cắt nằm dưới thẻ; `text` ("2.", "Bước 3")
    đặt giữa thẻ."""
    import fx_gfx as G
    from style_profile import get as sp_get, load as sp_load
    f, at = fx.fps, clip["at"] - 9 / fx.fps
    card = fx.image(G.paper_bg(fx.gfx_dir, "chapter_paper", "white", 0), at, 24 / f, lane="trans", name="Thẻ chương")
    opa = [[0, 0], [3 / f, 100], [18 / f, 100], [23 / f, 0]]
    card["opacity"] = fx._frame_keys(opa, card["dur"])
    card["motion"] = {"scale": fx._frame_keys([[0, 108], [6 / f, 100, "easeIn"]], card["dur"])}
    if text:
        ink = sp_get(sp_load(name="minimal-edu"), "text.colors.on_paper", "#111111")
        t = fx.text(text, at, 24 / f, role="mx_heavy", size=260, y=1010, color=ink, shadow=None, name=f"Chữ chương {text}")
        t["opacity"] = fx._frame_keys(opa, t["dur"])
    _cue(fx, cue_sfx, at + 3 / f, "key_hit", 0.05, "chapter_card_slam")
    return _tin(clip, "cross_dissolve", 1)


_KEYED_FN = {"punch_settle": punch_settle, "drift_reset": drift_reset, "j_cut_return": j_cut_return, "dip_to_paper": dip_to_paper,
             "paper_rip": paper_rip, "card_swipe": card_swipe, "smoke_veil": smoke_veil, "impact_shake": impact_shake,
             "vhs_rewind": vhs_rewind, "chapter_card_slam": chapter_card_slam}


JOIN_MARK = " ⇢ "                                   # tên clip "… ⇢ <kiểu>": dấu cho edit_rules (FilmCraft không nhận khoá lạ)


def mark(clip: dict, kind: str) -> dict:
    """Ghi kiểu chuyển cảnh vào tên clip sau điểm cắt (thay dấu cũ nếu có); "hard_cut" cũng ghi được."""
    clip["name"] = clip.get("name", "").split(JOIN_MARK)[0] + JOIN_MARK + kind
    return clip


def join_kind(clip: dict) -> str | None:
    name = clip.get("name", "")
    return name.rsplit(JOIN_MARK, 1)[1] if JOIN_MARK in name else None


def th_join(fx, clip: dict, kind: str, cue_sfx: bool = True, **opts) -> dict:
    """Gắn chuyển cảnh `kind` (TH_KINDS) vào đầu `clip` (clip sau điểm cắt); `opts` = tham số riêng của kiểu."""
    if kind not in TH_KINDS:
        raise ValueError(f"kiểu chuyển cảnh lạ: {kind} (có: {', '.join(sorted(TH_KINDS))})")
    mark(clip, kind)
    if kind in TH_JOINS:
        return _simple(fx, clip, kind, cue_sfx)
    return _KEYED_FN[kind](fx, clip, cue_sfx, **opts)
