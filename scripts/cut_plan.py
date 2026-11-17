"""Phân tích từng điểm cắt TRƯỚC khi chọn chuyển cảnh (người dùng chốt 2026-11-04 sau demo Motion FX:
dải dọc nối hai đoạn A-roll cùng khung trông như hình vỡ).

    from cut_plan import Cut, plan_cuts, plan_table
    cuts = [Cut(t=4.53, a=(aroll, 7.99), b=(aroll, 11.40), b_kind="aroll", before="…quay cảnh gì.", after="Sau nửa năm…")]
    plan = plan_cuts(cuts)            # thêm sim, loại điểm cắt, kiểu chuyển cảnh đề xuất, lý do
    print(plan_table(plan))           # bảng markdown để người dùng xem trước khi dựng

Luật (đo từ 28 reel mẫu, references/motion-fx.md mục "Phân tích điểm cắt"):
- Jump cut cùng khung (sim ≥ 0,80, hoặc cùng file A-roll và sim ≥ 0,3) giữa câu → zoom blur 4–5 khung + đổi punch 100 ↔ 112%; KHÔNG dải dọc / ô lưới
  (mỗi dải lộ một khuôn mặt lệch → trông như lỗi hình).
- Jump cut cùng khung sang câu / ý mới → zoom_through / panel_wipe / flash_shake / spin_zoom / light_leak / light_sweep…;
  đổi phần lớn → split_slide / rgb_glitch / film_burn / spin / glass / whip; luôn chọn cái chưa dùng ở 2 điểm cắt gần
  nhất (bảng OPTIONS).
- Vào B-roll (khác cảnh) → ô lưới nếu B-roll tương phản, dải dọc nếu B-roll sáng / phẳng; + flash_burst ở chỗ nối.
- Ra B-roll về người nói → light_leak / zoom.
- Đổi cảnh thật (sim < 0,5) → film_burn / flash_burst.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np

import th_transitions as TH
from style_profile import get as _sp_get, load as _sp_load

FF = "ffmpeg"
W, H = 72, 128


@dataclass
class Cut:
    t: float                                  # giây trên timeline
    a: tuple[str, float]                      # (file, giây nguồn) khung cuối trước điểm cắt
    b: tuple[str, float]                      # (file, giây nguồn) khung đầu sau điểm cắt
    b_kind: str = "aroll"                     # aroll | broll
    a_kind: str = "aroll"
    before: str = ""                          # lời ngay trước điểm cắt
    after: str = ""                           # lời ngay sau
    section: bool = False                     # đổi phần lớn (tiêu đề mới, điều kiện mới…)
    info: dict = field(default_factory=dict)


@lru_cache(maxsize=1024)          # plan_cuts_best chạy lại plan_cuts nhiều lần trên cùng các khung
def frame(src: str, t: float) -> np.ndarray:
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{max(0.0, t):.3f}", "-i", src, "-frames:v", "1",
                          "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).astype(np.float32).reshape(H, W) if len(raw) == W * H else np.zeros((H, W))


def similarity(x: np.ndarray, y: np.ndarray) -> float:
    """Tương quan chuẩn hoá hai khung xám nhỏ (1 = giống hệt bố cục)."""
    x, y = x - x.mean(), y - y.mean()
    return float((x * y).sum() / (np.sqrt((x * x).sum() * (y * y).sum()) + 1e-6))


def contrast(x: np.ndarray) -> tuple[float, float]:
    return float(x.mean()), float(x.std())


def _sentence_break(before: str) -> bool:
    return before.rstrip().endswith((".", "?", "!", ":"))


# Lựa chọn theo loại điểm cắt (ưu tiên trước); chọn cái chưa dùng ở 2 điểm cắt gần nhất để không đơn điệu.
# Tên khớp motion_fx (áp bằng fx.cut_fx): overlay TNEDIT (TRANS) = flash_burst / film_burn / light_leak / film_roll / glitch;
# ghép sáng tạo (COMBO_KINDS) = flash_shake / rgb_glitch / spin_zoom / light_sweep / travel / glass / liquid / slice /
# spring / spin + dựng bằng keyframe zoom_through / panel_wipe / split_slide (lần 10: "sáng tạo hơn" — ưu tiên đầu bảng);
# chuyển cảnh FilmCraft đơn (JOINS) = zoom / slide / whip. Người dùng 2026-11-04 (lần 9): "chuyển cảnh cần sáng tạo hơn".
OPTIONS = {
    "jump · giữa câu": ["zoom + punch"],
    # jump cut giữa câu / sau dấu phẩy (video nói liền, cắt khoảng lặng — Huy OPA 2: 31/34 điểm cắt): cứ 3 lần thì 1 lần
    # chuyển cảnh nhẹ trong bảng này, còn lại zoom + punch — tránh 30 lần zoom giống nhau mà không dồn hiệu ứng lớn mỗi 2 s
    "jump · sau dấu phẩy": ["slice", "light_sweep", "spin_zoom", "spring"],
    # Rule 2 (người dùng chốt 2026-11-11): flash / flicker bị lặp quá nhiều (10 video KB: 57,6 % điểm cắt) → mỗi bảng xếp
    # theo ngữ cảnh, họ nháy sáng (FLASHY) xuống cuối; _pick chọn cái ÍT DÙNG NHẤT, không lặp trong 4 điểm cắt, FLASHY ≤ 20 %.
    # câu mới, cùng khung: chuyển động nhẹ đẩy nhịp nói
    "jump cut · câu mới": ["zoom_through", "slice", "spin_zoom", "light_sweep", "spring", "panel_wipe", "travel",
                           "light_leak", "film_roll", "flash_shake", "shutter", "flicker"],
    # sang phần mới: chuyển cảnh lớn, "mở chương"
    "jump cut · đổi phần": ["split_slide", "rgb_glitch", "glass", "film_burn", "spin", "whip", "liquid", "panel_wipe",
                            "flash_burst", "flicker"],
    "ra B-roll": ["zoom", "light_leak", "slide", "whip", "shutter"],   # B-roll là lớp phủ: chỉ overlay / chuyển cảnh ra của nó
    # bố cục khác hẳn: lớp phủ che chỗ nối
    "đổi cảnh": ["panel_wipe", "liquid", "travel", "film_burn", "glass", "rgb_glitch", "flash_shake", "shutter", "flicker"],
    # bố cục khác vừa: trượt / chém / xuyên
    "đổi góc gần": ["slice", "zoom_through", "travel", "slide", "spring", "spin_zoom", "flash_burst", "shutter", "flicker"],
}
# Kiểu hợp phong cách năng động (th_transitions: impact_shake / pop_in / neon_wipe / mosaic_pixel / vhs_rewind): chỉ vào bảng khi
# plan_cuts(energetic=True) — mặc định giữ nguyên kết quả cũ.
OPTIONS_E = {
    "jump cut · câu mới": ["impact_shake", "pop_in", "neon_wipe"],
    "jump cut · đổi phần": ["mosaic_pixel", "vhs_rewind"],
    "đổi cảnh": ["neon_wipe", "mosaic_pixel"],
    "đổi góc gần": ["pop_in", "impact_shake"],
}
FLASHY = {"flash_burst", "flash_shake", "shutter", "flicker", "vhs_rewind"}   # họ nháy sáng / nhấp nháy (Rule 2: hạn chế)
MAX_FLASHY_SHARE = 0.2      # tối đa 20 % điểm cắt dùng họ nháy sáng
FLASHY_GAP = 3              # hai lần nháy sáng cách nhau ít nhất 3 điểm cắt
RECENT_N = 4                # không lặp cùng chuyển cảnh trong 4 điểm cắt gần nhất
SFX_OF = {"flash_burst": "flash hit (thump + màn trập) đúng khung trắng", "film_burn": "tiếng có sẵn trong file film burn",
          "light_leak": "swell / whoosh ánh sáng ở khung sáng nhất", "film_roll": "máy chiếu phim", "glitch": "glitch ngắn",
          "zoom + punch": "whoosh nhẹ", "zoom": "whoosh", "slide": "whoosh", "whip": "boom trầm trước 0,25 s + whoosh",
          "flash_shake": "flash hit đúng khung trắng (rung máy theo sau)", "rgb_glitch": "glitch ngắn đúng khung nhiễu",
          "spin_zoom": "whoosh căn giữa cú xoay", "light_sweep": "swell ánh sáng khi vệt quét qua giữa khung",
          "travel": "whoosh căn giữa cú lao", "glass": "whoosh căn giữa", "liquid": "whoosh căn giữa",
          "slice": "whoosh căn giữa cú chém", "spring": "whoosh căn giữa cú nảy", "spin": "whoosh căn giữa cú xoay",
          "zoom_through": "whoosh tăng dần, đỉnh đúng khung cắt", "panel_wipe": "2 whoosh: tấm vào (đỉnh khi phủ kín) · tấm ra",
          "split_slide": "whoosh khi hai nửa khung trượt ra",
          "flicker": "glitch ngắn đúng khung nháy đầu", "shutter": "tiếng màn trập máy ảnh đúng khung trắng",
          # kiểu talking-head (th_transitions): "—" = không thêm tiếng
          "hard_cut": "—", "j_cut_return": "— (hình vào trước lời 10 khung, tiếng giữ nguyên)", "morph_smooth": "—",
          "punch_settle": "swish nhẹ (paper)", "drift_reset": "—", "blur_dissolve_cut": "swish nhẹ (paper)",
          "soft_wipe": "swish nhẹ (paper)", "dip_to_paper": "—", "camera_continue": "whoosh", "paper_rip": "tiếng giấy rách (paper) đúng khung cắt",
          "card_swipe": "whoosh", "luma_fade_soft": "—", "clock_wipe_step": "pop", "smoke_veil": "swell nhẹ (leak)",
          "iris_round_focus": "pop", "impact_shake": "boom_pre + key_hit", "chapter_card_slam": "key_hit khi thẻ đập vào",
          "page_peel_in": "pop", "pop_in": "pop", "neon_wipe": "whoosh", "mosaic_pixel": "data_beep",
          "vhs_rewind": "glitch ngắn"}


def _pick(options: list[str], recent: list[str], used: dict | None = None, n_done: int = 0, seed: int = 0) -> str:
    """Chọn chuyển cảnh hợp ngữ cảnh: bỏ cái đã dùng trong RECENT_N điểm cắt gần nhất; họ nháy sáng chỉ khi còn hạn mức
    (≤ MAX_FLASHY_SHARE số điểm cắt, cách nhau ≥ FLASHY_GAP); trong số còn lại lấy cái ít dùng nhất (luân phiên),
    hoà thì theo thứ tự ưu tiên ngữ cảnh, lệch vòng theo `seed` (sổ luân phiên) để mỗi video một thứ tự."""
    used = used if used is not None else {}
    flashy_n = sum(v for k, v in used.items() if k in FLASHY)
    flash_ok = (flashy_n + 1) <= MAX_FLASHY_SHARE * (n_done + 1) + 1e-9 and not (set(recent[-(FLASHY_GAP - 1):]) & FLASHY)
    ok = [o for o in options if o not in recent and (o not in FLASHY or flash_ok)]
    if not ok:
        ok = [o for o in options if o not in FLASHY] or options
    n = len(options)
    return min(ok, key=lambda o: (used.get(o, 0), (options.index(o) - seed) % n if seed else options.index(o)))


def plan_cuts(cuts: list[Cut], seed: int = 0, energetic: bool = False) -> list[Cut]:
    """energetic=True: thêm các kiểu hợp phong cách năng động (OPTIONS_E) vào cuối từng bảng."""
    opts = lambda k: OPTIONS[k] + (OPTIONS_E.get(k, []) if energetic else [])      # noqa: E731
    recent: list[str] = []
    used: dict[str, int] = {}
    recent_all: list[str] = []
    comma_n = 0
    for c in cuts:
        fa, fb = frame(*c.a), frame(*c.b)
        sim = similarity(fa, fb)
        mean_b, std_b = contrast(fb)
        brk = _sentence_break(c.before)
        same = sim >= 0.8 or (c.a[0] == c.b[0] and c.a_kind == c.b_kind == "aroll" and sim >= 0.3)
        # cùng file A-roll = cùng máy, cùng khung (người nói cử động / zoom dần làm sim chỉ ~0,6)
        if c.b_kind == "broll" and c.a_kind != "broll":
            kind = "vào B-roll"
            reveal = "grid_reveal" if std_b >= 45 and mean_b <= 185 else "strip_reveal"
            seam = _pick(["flash_burst", "light_leak"], recent, used, len(recent_all), seed)   # flash cũng chịu hạn mức Rule 2
            rec = f"{reveal} + {seam}"
            why = (f"cảnh khác hẳn (sim {sim:.2f}); B-roll {'tương phản' if reveal == 'grid_reveal' else 'sáng/phẳng'} "
                   f"(TB {mean_b:.0f}, lệch {std_b:.0f}) → {'ô lưới' if reveal == 'grid_reveal' else 'dải dọc'} lộ cảnh mới, {seam} ở chỗ nối")
            sfx = "click mỗi ô / dải + " + ("flash hit" if seam == "flash_burst" else SFX_OF["light_leak"])
        elif c.a_kind == "broll" and c.b_kind != "broll":
            kind = "ra B-roll"
            rec = _pick(opts(kind), recent, used, len(recent_all), seed)
            why, sfx = "về lại người nói: overlay nhẹ / zoom ngắn", SFX_OF[rec]
        elif same:
            kind = "jump cut · đổi phần" if c.section else ("jump cut · câu mới" if brk else "jump · giữa câu")
            if kind == "jump · giữa câu":                  # mọi jump cut giữa câu: 3 lần thì 1 lần chuyển cảnh nhẹ
                comma_n += 1
                if c.before.rstrip().endswith(","):
                    kind = "jump · sau dấu phẩy"
                light = OPTIONS["jump · sau dấu phẩy"]          # xoay vòng riêng (2 lần trước luôn là zoom → _pick chỉ ra slice)
                rec = light[(comma_n // 3 - 1) % len(light)] if comma_n % 3 == 0 else "zoom + punch"
            else:
                rec = _pick(opts(kind), recent, used, len(recent_all), seed)
            why = (f"cùng khung (sim {sim:.2f}), " + ("sang phần mới" if c.section else "hết câu trước" if brk else "câu đang nói dở")
                   + f" → {rec}; không dải/ô (lộ mặt lệch)")
            sfx = SFX_OF[rec]
        elif sim < 0.5:
            kind = "đổi cảnh"
            rec = _pick(opts(kind), recent, used, len(recent_all), seed)
            why, sfx = f"bố cục khác hẳn (sim {sim:.2f}) → overlay che chỗ nối", SFX_OF[rec]
        else:
            kind = "đổi góc gần"
            rec = _pick(opts(kind), recent, used, len(recent_all), seed)
            why, sfx = f"bố cục khác vừa (sim {sim:.2f})", SFX_OF[rec]
        c.info = {"sim": round(sim, 2), "kind": kind, "join": rec, "why": why, "sfx": sfx,
                  "b_mean": round(mean_b), "b_std": round(std_b)}
        last = rec.split(" + ")[-1]
        recent_all.append(last)
        used[last] = used.get(last, 0) + 1
        recent = recent_all[-RECENT_N:]
    return cuts


MIN_KINDS = 6               # ≥ 6 kiểu chuyển cảnh khác nhau mỗi video (Rule 2)


def _violations(plan: list[Cut]) -> tuple[int, int, int]:
    """(số lần lặp liền kề, 1 nếu nháy sáng > 20 %, 1 nếu < 6 kiểu) — càng nhỏ càng tốt."""
    joins = [c.info["join"] for c in plan]
    flashy = sum(1 for j in joins if any(p in FLASHY for p in j.split(" + ")))
    return (sum(1 for a, b in zip(joins, joins[1:]) if a == b), int(flashy > MAX_FLASHY_SHARE * len(joins) + 1e-9),
            int(len(set(joins)) < min(MIN_KINDS, len(joins))))


def plan_cuts_best(cuts: list[Cut], seed: int = 0, tries: int = 8, energetic: bool = False) -> list[Cut]:
    """plan_cuts với các hạt seed, seed+1, … (tối đa `tries`) rồi giữ bản không lặp liền kề, nháy sáng ≤ 20 %, ≥ 6 kiểu
    (cùng mức vi phạm thấp nhất nếu không bản nào đủ). Điền c.info của `cuts` theo bản tốt nhất."""
    best = None
    for k in range(tries):
        plan = plan_cuts(cuts, seed + k, energetic)
        v = _violations(plan)
        if best is None or v < best[0]:
            best = (v, [dict(c.info) for c in plan])
        if v == (0, 0, 0):
            break
    for c, info in zip(cuts, best[1]):
        c.info = info
    return cuts


# ---------- hồ sơ minimal-edu: xoay vòng chuyển cảnh thay cho "cắt cứng 80 %" (th_transitions) ----------
# Ngữ cảnh giống plan_cuts; "jump · sau dấu phẩy" gộp vào "giữa câu". hard_cut / j_cut_return = cắt cứng (≤ 40 %, ≤ 2 liền).
OPTIONS_MIN = {
    "jump · giữa câu": ["punch_settle", "drift_reset", "morph_smooth", "camera_continue", "hard_cut"],
    "jump cut · câu mới": ["j_cut_return", "hard_cut", "soft_wipe", "luma_fade_soft", "clock_wipe_step"],
    "jump cut · đổi phần": ["dip_to_paper", "paper_rip", "smoke_veil", "chapter_card_slam", "blur_dissolve_cut", "clock_wipe_step"],
    "vào B-roll": ["card_swipe", "page_peel_in", "soft_wipe", "blur_dissolve_cut"],
    "ra B-roll": ["iris_round_focus", "soft_wipe", "luma_fade_soft", "dip_to_paper"],
    "đổi cảnh": ["dip_to_paper", "blur_dissolve_cut", "luma_fade_soft", "clock_wipe_step", "chapter_card_slam"],
    "đổi góc gần": ["camera_continue", "soft_wipe", "blur_dissolve_cut", "punch_settle"],
}
# dùng được ở mọi ngữ cảnh: bể dự phòng khi bảng ngữ cảnh hết lượt (đủ 6 kiểu, mỗi kiểu ≤ 20 %)
POOL_MIN = ["punch_settle", "drift_reset", "morph_smooth", "camera_continue", "blur_dissolve_cut", "soft_wipe", "luma_fade_soft",
            "clock_wipe_step", "dip_to_paper", "iris_round_focus"]
MIN_DEFAULTS = {"max_hard_cut_share": 0.4, "max_hard_in_row": 2, "min_distinct_transitions": 6, "max_kind_share": 0.2,
                "no_repeat_within": 3, "max_flashy_share": 0.0}


def _context(c: Cut, sim: float) -> str:
    if c.b_kind == "broll" and c.a_kind != "broll":
        return "vào B-roll"
    if c.a_kind == "broll" and c.b_kind != "broll":
        return "ra B-roll"
    if sim >= 0.8 or (c.a[0] == c.b[0] and c.a_kind == c.b_kind == "aroll" and sim >= 0.3):
        return "jump cut · đổi phần" if c.section else ("jump cut · câu mới" if _sentence_break(c.before) else "jump · giữa câu")
    return "đổi cảnh" if sim < 0.5 else "đổi góc gần"


def _min_limits(rules: dict | None, n: int) -> dict:
    g = lambda k: _sp_get(rules, f"cuts.{k}", MIN_DEFAULTS[k])                         # noqa: E731
    return {"hard": int(g("max_hard_cut_share") * n + 1e-9), "row": g("max_hard_in_row"), "kinds": g("min_distinct_transitions"),
            "kind_cap": max(1, int(g("max_kind_share") * n + 1e-9)), "gap": g("no_repeat_within"),
            "flashy": int(g("max_flashy_share") * n + 1e-9)}


def _allowed(k: str, st: dict, lim: dict, level: int) -> bool:
    """level 0 = mọi luật; 1 = bỏ trần 20 % / kiểu; 2 = bỏ thêm không lặp trong N điểm cắt và 1 lần / video."""
    if k in TH.HARD_KINDS:
        return st["hard"] < lim["hard"] and st["run"] < lim["row"]
    if k in FLASHY and st["flashy"] >= lim["flashy"]:
        return False
    if level >= 2:
        return True
    if k in st["recent"][-lim["gap"]:] or (k in TH.ONE_PER_VIDEO and st["count"].get(k)):
        return False
    return level >= 1 or st["count"].get(k, 0) < lim["kind_cap"]


def _pick_min(opts: list[str], st: dict, lim: dict, left: int, seed: int) -> str:
    """Kiểu ít dùng nhất trong bảng ngữ cảnh (lệch vòng theo seed); hết thì lấy từ POOL_MIN; sắp hết điểm cắt mà chưa đủ số kiểu
    (`min_distinct_transitions`) thì chỉ nhận kiểu chưa dùng."""
    need_new = lim["kinds"] - len(st["distinct"]) >= left
    n = len(opts)
    for level in (0, 1, 2):
        for pool in (opts, [k for k in POOL_MIN if k not in opts]):
            ok = [k for k in pool if _allowed(k, st, lim, level) and not (need_new and (k in TH.HARD_KINDS or k in st["distinct"]))]
            if ok:
                return min(ok, key=lambda k: (st["count"].get(k, 0), (pool.index(k) - seed) % len(pool) if seed else pool.index(k)))
        if need_new and level == 2:
            need_new = False                                   # hết kiểu mới thì thôi, chọn bất kỳ
    return min(POOL_MIN, key=lambda k: st["count"].get(k, 0))


def plan_cuts_min(cuts: list[Cut], seed: int = 0, rules: dict | None = None) -> list[Cut]:
    """Bản plan_cuts cho hồ sơ minimal-edu. `rules` = hồ sơ phong cách (style_profile.load(name="minimal-edu")); số trong
    rules["cuts"] (max_hard_cut_share 0,4 · max_hard_in_row 2 · min_distinct_transitions 6 · max_kind_share 0,2 ·
    no_repeat_within 3 · max_flashy_share 0), thiếu thì dùng MIN_DEFAULTS. Điền c.info như plan_cuts (+ "frames", "lead_s")."""
    lim = _min_limits(rules, len(cuts))
    st = {"hard": 0, "run": 0, "flashy": 0, "recent": [], "count": {}, "distinct": set()}
    for i, c in enumerate(cuts):
        fa, fb = frame(*c.a), frame(*c.b)
        sim = similarity(fa, fb)
        mean_b, std_b = contrast(fb)
        ctx = _context(c, sim)
        rec = _pick_min(OPTIONS_MIN[ctx], st, lim, len(cuts) - i, seed)
        hard = rec in TH.HARD_KINDS
        st["hard"] += hard
        st["run"] = st["run"] + 1 if hard else 0
        st["flashy"] += rec in FLASHY
        st["count"][rec] = st["count"].get(rec, 0) + 1
        st["recent"].append(rec)
        if not hard:
            st["distinct"].add(rec)
        c.info = {"sim": round(sim, 2), "kind": ctx, "join": rec, "why": f"hồ sơ minimal-edu, {ctx} (sim {sim:.2f}) → {rec}",
                  "sfx": SFX_OF[rec], "b_mean": round(mean_b), "b_std": round(std_b), "frames": TH.TH_FRAMES.get(rec, 0)}
        if rec == "j_cut_return":
            c.info["lead_s"] = round(TH.J_LEAD_FRAMES / 30, 4)
    return cuts


TABLE_HEAD = ["Giây", "Cảnh", "Chữ chính", "Chuyển cảnh", "Zoom", "Nỗi đau", "SFX", "Lý do"]   # cột C3 (SKILL §3 bước 9)


def plan_table(cuts: list[Cut], ctx: list[dict] | None = None) -> str:
    """Bảng điểm cắt cho người dùng duyệt (C3): Giây | Cảnh | Chữ chính | Chuyển cảnh | Zoom | Nỗi đau | SFX | Lý do.
    `ctx` (tuỳ chọn, cùng thứ tự `cuts`) = [{"scene": "A-roll 1 → B-roll 1", "key": "chữ chính đang hiện", "zoom": "…", "pain": "…"}];
    thiếu thì ghi «—»."""
    rows = ["| " + " | ".join(TABLE_HEAD) + " |", "|---|---|---|---|---|---|---|---|"]
    for n, c in enumerate(cuts):
        i, x = c.info, (ctx[n] if ctx else {})
        words = f" · «{c.before[-28:]}» → «{c.after[:28]}»" if c.before or c.after else ""
        rows.append(f"| {c.t:.2f} | {x.get('scene') or '—'} | {x.get('key') or '—'} | **{i['join']}** | {x.get('zoom') or '—'} | "
                    f"{x.get('pain') or '—'} | {i['sfx']} | {i['kind']} (giống {i['sim']:.2f}): {i['why']}{words} |")
    return "\n".join(rows)
