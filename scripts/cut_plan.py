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
FLASHY = {"flash_burst", "flash_shake", "shutter", "flicker"}   # họ nháy sáng / nhấp nháy (Rule 2: hạn chế)
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
          "flicker": "glitch ngắn đúng khung nháy đầu", "shutter": "tiếng màn trập máy ảnh đúng khung trắng"}


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


def plan_cuts(cuts: list[Cut], seed: int = 0) -> list[Cut]:
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
            rec = _pick(OPTIONS[kind], recent, used, len(recent_all), seed)
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
                rec = _pick(OPTIONS[kind], recent, used, len(recent_all), seed)
            why = (f"cùng khung (sim {sim:.2f}), " + ("sang phần mới" if c.section else "hết câu trước" if brk else "câu đang nói dở")
                   + f" → {rec}; không dải/ô (lộ mặt lệch)")
            sfx = SFX_OF[rec]
        elif sim < 0.5:
            kind = "đổi cảnh"
            rec = _pick(OPTIONS[kind], recent, used, len(recent_all), seed)
            why, sfx = f"bố cục khác hẳn (sim {sim:.2f}) → overlay che chỗ nối", SFX_OF[rec]
        else:
            kind = "đổi góc gần"
            rec = _pick(OPTIONS[kind], recent, used, len(recent_all), seed)
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


def plan_cuts_best(cuts: list[Cut], seed: int = 0, tries: int = 8) -> list[Cut]:
    """plan_cuts với các hạt seed, seed+1, … (tối đa `tries`) rồi giữ bản không lặp liền kề, nháy sáng ≤ 20 %, ≥ 6 kiểu
    (cùng mức vi phạm thấp nhất nếu không bản nào đủ). Điền c.info của `cuts` theo bản tốt nhất."""
    best = None
    for k in range(tries):
        plan = plan_cuts(cuts, seed + k)
        v = _violations(plan)
        if best is None or v < best[0]:
            best = (v, [dict(c.info) for c in plan])
        if v == (0, 0, 0):
            break
    for c, info in zip(cuts, best[1]):
        c.info = info
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
