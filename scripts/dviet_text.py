#!/usr/bin/env python3
"""dviet_text — đổi danh sách câu chữ có vai trò thành các track chữ (timeline spec của craft-handoff)
theo token style @__dviet (references/dviet-style.json).

    ~/.venvs/video-skills/bin/python dviet_text.py events.json -o text_tracks.json [--accent yellow_bright|#HEX]

events.json:
{
  "accent": "yellow_bright",            // tên trong palette.accents hoặc mã #HEX (mặc định yellow_bright)
  "events": [
    {"role": "caption", "text": "với hiệu ứng", "at": 5.0, "dur": 1.2},
    {"role": "keyword", "text": "giống hệt nhau", "at": 5.6, "dur": 0.8},
    {"role": "pair",    "small": "tạo ra", "big": "chuyển động", "at": 6.2, "dur": 1.5},
    {"role": "stack3",  "small": "kỹ thuật", "big": "chồng chữ", "accent": "dễ đọc", "at": 8.0, "dur": 2.0},
    {"role": "number",  "num": "3", "noun": "hiệu ứng", "context": "nên lưu lại", "at": 0.2, "dur": 2.6},
    {"role": "header",  "label": "bước một", "big": "tách nền", "sub": "trong FilmCraft", "at": 12.0, "dur": 4.0},
    {"role": "cta",     "text": "Lưu lại", "at": 40.0, "dur": 2.0}
  ]
}
"case": "sentence" (mặc định, theo luật người dùng: viết hoa chữ cái đầu mỗi dòng hiển thị) hoặc "lower"
(giữ nguyên chữ như nhập, kiểu chữ thường của kênh — chỉ khi người dùng cho phép).
Mọi vai trò nhận thêm "y_pct" (tâm khối chữ, % chiều cao khung). "chest_y_pct" ở cấp trên dời cả cụm chữ vùng ngực
(mặc định 52 = khung kiểu dviet, mặt ở 1/3 trên); footage mặt thấp hơn thì đặt = vị trí cằm + 4.

Ra: {"tracks": [T1 Phụ đề, T2 Chữ nhỏ, T3 Chữ lớn, T4 Chữ nhấn]} — chép vào "tracks" của spec, đặt trên
track video; muốn chữ sau người thì thêm track người đã tách nền (ProRes 4444) phía trên T3.
Chữ vào bằng blur-in/fade theo token, ra bằng cắt cứng (đúng kiểu kênh). Text được chuẩn hoá NFC.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import unicodedata
from pathlib import Path

from PIL import ImageFont

HERE = Path(__file__).resolve().parent
STYLE = HERE.parent / "references" / "dviet-style.json"
TRACKS = ("T1 Phụ đề", "T2 Chữ nhỏ", "T3 Chữ lớn", "T4 Chữ nhấn")
STAGGER = 0.07          # chữ phụ vào trễ hơn chữ chính (s)


class Typo:
    """Font + đo bề rộng chữ bằng file font thật."""

    def __init__(self, style: dict):
        self.style = style
        self._cache: dict = {}

    def font(self, key: str, size: float):
        spec = self.style["fonts"][key]
        ck = (key, round(size))
        if ck not in self._cache:
            f = ImageFont.truetype(os.path.expanduser(spec["file"]), max(1, round(size)))
            if "Variable" in spec["file"]:
                f.set_variation_by_name(spec["style"])
            self._cache[ck] = f
        return self._cache[ck]

    def ink(self, key: str, size: float, text: str) -> tuple[float, float, float, float]:
        """Khung mực (trái, trên, phải, dưới) tính từ điểm gốc trái-baseline; trên < 0. Có cả dấu tiếng Việt."""
        return self.font(key, size).getbbox(nfc(text), anchor="ls")

    def width(self, key: str, size: float, text: str) -> float:
        box = self.ink(key, size, text)
        return box[2] - box[0]


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", str(s))


TEXT_KEYS = ("text", "small", "big", "accent", "noun", "context", "label", "sub")


def sentence_case(s: str) -> str:
    """Viết hoa chữ cái đầu tiên của dòng (giữ nguyên phần còn lại)."""
    s = nfc(s)
    for i, ch in enumerate(s):
        if ch.isalpha():
            return s[:i] + ch.upper() + s[i + 1:]
    return s


def anim(kind: str, style: dict) -> dict:
    """Keyframe vào cho một clip chữ (thời gian tính từ đầu clip)."""
    a = style["animations"]
    if kind == "fade":
        d = a["fade"]["dur"]
        return {"opacity": [[0, 0], [d, 100, "easeIn"]]}
    if kind == "slide_up_blur":
        s = a["slide_up_blur"]
        return {"opacity": [[0, 0], [s["dur"] * 0.6, 100]],
                "effects": [{"effect": "gaussian_blur", "params": {"blurriness": [[0, s["gaussian_blur_from"]], [s["dur"], 0, "easeIn"]]}}],
                "_slide": s["slide_px"], "_slide_dur": s["dur"]}
    b = a["blur_in"]
    return {"opacity": [[0, 0], [b["dur"] * 0.6, 100]],
            "effects": [{"effect": "gaussian_blur", "params": {"blurriness": [[0, b["gaussian_blur_from"]], [b["dur"], 0, "easeIn"]]}}]}


def clip(style: dict, typo: Typo, tier: str, text: str, at: float, dur: float, x: float, baseline: float,
         color: str | None = None, align: str = "center", size: float | None = None) -> dict:
    t = style["tiers"][tier]
    f = style["fonts"][t["font"]]
    sz = size or t["size"]
    track_key = "big_sans" if t["font"].startswith("sans_bold") or t["font"].startswith("sans_heavy") else \
        "serif" if t["font"] == "serif_italic" else "caption"
    c = {"text": nfc(text), "at": round(at, 3), "dur": round(dur, 3), "font": f["family"], "style": f["style"],
         "size": round(sz), "color": color or style["palette"]["text"], "align": align,
         "position": [round(x), round(baseline)], "tracking": style["tracking"].get(track_key, 0),
         "shadow": {k: style["shadow"][k] for k in ("color", "opacity", "blur", "distance")}}
    a = anim(t.get("anim_in", "blur_in"), style)
    slide = a.pop("_slide", 0)
    slide_dur = a.pop("_slide_dur", 0)
    c.update(a)
    if slide:
        c["motion"] = {"position": [[0, [540, 960 + slide]], [slide_dur, [540, 960], "easeIn"]]}
    return c


def resolve_accent(style: dict, name: str | None) -> str:
    acc = style["palette"]["accents"]
    if not name:
        return acc["yellow_bright"]
    return name if name.startswith("#") else acc[name]


GAP = 6                 # khe tối thiểu giữa hai dòng chữ (px) — không bao giờ đè lên dấu


def layout(ev: dict, style: dict, typo: Typo, accent: str) -> list[tuple[int, dict]]:
    """Trả về [(chỉ số track, clip)] cho một sự kiện. Xếp theo khung mực thật để dòng phụ không đè dấu dòng chính."""
    role, at, dur = ev["role"], float(ev["at"]), float(ev["dur"])
    T = style["tiers"]
    default_y = {"header": T["header_big"].get("y_pct", 25), "pair": 55, "stack3": 55, "keyword": 55}.get(role, T.get(role, {}).get("y_pct", 52))
    if role != "header" and ev.get("_chest_y_pct") is not None:      # dời cụm chữ vùng ngực theo footage
        default_y = float(ev["_chest_y_pct"]) + (default_y - 52)
    cy = style["canvas"]["h"] * float(ev.get("y_pct", default_y)) / 100
    cx = style["canvas"]["w"] / 2
    F = lambda tier: T[tier]["font"]
    S = lambda tier: T[tier]["size"]

    def mid_baseline(tier: str, text: str) -> float:          # baseline để tâm khối mực nằm ở cy
        _, top, _, bot = typo.ink(F(tier), S(tier), text)
        return cy - (top + bot) / 2

    def above(tier: str, text: str, ink_top_of_lower: float) -> float:   # baseline để đáy mực sát trên
        return ink_top_of_lower - GAP - typo.ink(F(tier), S(tier), text)[3]

    def below(tier: str, text: str, ink_bottom_of_upper: float) -> float:  # baseline để đỉnh mực sát dưới
        return ink_bottom_of_upper + GAP - typo.ink(F(tier), S(tier), text)[1]

    out: list[tuple[int, dict]] = []
    if role == "caption":
        out.append((0, clip(style, typo, "caption", ev["text"], at, dur, cx, mid_baseline("caption", ev["text"]))))
    elif role == "pair":                     # chữ nhỏ trên-trái + từ khoá serif nghiêng màu nhấn
        b = mid_baseline("keyword_serif", ev["big"])
        l, t, r, _ = typo.ink(F("keyword_serif"), S("keyword_serif"), ev["big"])
        w = r - l
        out.append((3, clip(style, typo, "keyword_serif", ev["big"], at, dur, cx, b, accent)))
        out.append((1, clip(style, typo, "context_small", ev["small"], at + STAGGER, dur - STAGGER,
                            cx - w / 2, above("context_small", ev["small"], b + t), align="left")))
    elif role == "stack3":                   # nhỏ / rất lớn sans / nhấn serif lệch phải ở dưới
        b = mid_baseline("keyword_sans", ev["big"])
        l, t, r, bot = typo.ink(F("keyword_sans"), S("keyword_sans"), ev["big"])
        out.append((2, clip(style, typo, "keyword_sans", ev["big"], at, dur, cx, b)))
        out.append((1, clip(style, typo, "context_small", ev["small"], at + STAGGER, dur - STAGGER,
                            cx, above("context_small", ev["small"], b + t))))
        out.append((3, clip(style, typo, "keyword_serif", ev["accent"], at + 2 * STAGGER, dur - 2 * STAGGER,
                            cx + (r - l) * 0.12, below("keyword_serif", ev["accent"], b + max(bot, 0) * 0.4), accent)))
    elif role == "number":                   # số lớn màu nhấn bên trái, danh từ đè nhẹ mép phải số, ngữ cảnh dưới danh từ
        n_l, n_t, n_r, n_b = typo.ink(F("number"), S("number"), ev["num"])
        w_n = n_r - n_l
        w_noun = typo.width(F("keyword_sans"), S("keyword_sans"), ev["noun"])
        left = cx - (w_n * 0.85 + w_noun) / 2
        bn = cy - (n_t + n_b) / 2
        out.append((2, clip(style, typo, "number", ev["num"], at, dur, left - n_l, bn, accent, align="left")))
        noun_x = left + w_n * 0.85
        noun_b = bn + n_t * 0.35
        out.append((3, clip(style, typo, "keyword_sans", ev["noun"], at + STAGGER, dur - STAGGER, noun_x, noun_b, align="left")))
        if ev.get("context"):
            nb = typo.ink(F("keyword_sans"), S("keyword_sans"), ev["noun"])[3]
            out.append((1, clip(style, typo, "context_small", ev["context"], at + 2 * STAGGER, dur - 2 * STAGGER,
                                noun_x, below("context_small", ev["context"], noun_b + nb), align="left")))
    elif role == "header":                   # nhãn nhỏ trên-trái / chữ lớn / phụ đề serif dưới-phải
        b = mid_baseline("header_big", ev["big"])
        l, t, r, bot = typo.ink(F("header_big"), S("header_big"), ev["big"])
        out.append((2, clip(style, typo, "header_big", ev["big"], at, dur, cx, b)))
        out.append((1, clip(style, typo, "header_label", ev["label"], at + STAGGER, dur - STAGGER,
                            cx - (r - l) / 2, above("header_label", ev["label"], b + t), align="left")))
        if ev.get("sub"):
            out.append((3, clip(style, typo, "header_sub", ev["sub"], at + 2 * STAGGER, dur - 2 * STAGGER,
                                cx + (r - l) / 2, below("header_sub", ev["sub"], b + bot), accent, align="right")))
    elif role == "keyword":                  # một từ khoá serif nghiêng màu nhấn đứng riêng (đúng lúc được nói)
        out.append((3, clip(style, typo, "keyword_serif", ev["text"], at, dur, cx, mid_baseline("keyword_serif", ev["text"]), accent)))
    elif role == "cta":
        out.append((3, clip(style, typo, "cta", ev["text"], at, dur, cx, mid_baseline("cta", ev["text"]),
                            accent)))
    else:
        raise ValueError(f"vai trò không hỗ trợ: {role}")
    return out


def build(events: dict, style: dict, accent_name: str | None) -> dict:
    typo = Typo(style)
    accent = resolve_accent(style, accent_name or events.get("accent"))
    tracks = [{"type": "text", "name": n, "clips": []} for n in TRACKS]
    chest = events.get("chest_y_pct")
    for ev in sorted(events["events"], key=lambda e: e["at"]):
        ev = dict(ev, _chest_y_pct=chest)
        if events.get("case", "sentence") == "sentence":       # viết hoa TRƯỚC khi đo khung mực (chữ hoa cao hơn)
            ev.update({k: sentence_case(ev[k]) for k in TEXT_KEYS if isinstance(ev.get(k), str)})
        for idx, c in layout(ev, style, typo, accent):
            tracks[idx]["clips"].append(c)
    for t in tracks:                      # cùng track không được chồng thời gian: cắt clip trước
        cl = t["clips"]
        for a, b in zip(cl, cl[1:]):
            if a["at"] + a["dur"] > b["at"]:
                a["dur"] = round(max(0.05, b["at"] - a["at"]), 3)
    return {"tracks": [t for t in tracks if t["clips"]]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("events")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--accent")
    ap.add_argument("--style", default=str(STYLE))
    a = ap.parse_args()
    style = json.loads(Path(a.style).read_text(encoding="utf-8"))
    events = json.loads(Path(a.events).read_text(encoding="utf-8"))
    try:
        out = build(events, style, a.accent)
    except (KeyError, ValueError) as e:
        print(f"LỖI: {e}", file=sys.stderr)
        return 2
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    n = sum(len(t["clips"]) for t in out["tracks"])
    print(f"{n} clip chữ trên {len(out['tracks'])} track → {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
