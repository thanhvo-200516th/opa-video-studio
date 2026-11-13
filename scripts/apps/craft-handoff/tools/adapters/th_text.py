"""th_text — text clips of the dung-video-talking-head template (release 1.2.6) for th_to_craft.

Ports the layout maths of template/src/comp/{Subtitle,Hook,Cta,StepList}.tsx + theme.ts + anim.ts so
each line lands where the browser drew it: same font sizes (fitSize / wordCap / one-row hero rule with
the template's own glyph tables from src/ink.ts), same bottom-anchored flex stack, same colours. Line
metrics of the fonts were read once with fontTools and are kept as constants. Also holds the small
keyframe helpers th_to_craft shares. Stdlib only.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

W, H = 1080, 1920                     # theme.ts
REVEAL_F, CARD_IN_F, CARD_OUT_F, ITEM_F, POP_F = 9, 10, 8, 9, 12   # Subtitle / StepList / Cta frames
NAMED = {"warn": "#ff5d73", "gold": "#ffcf6b", "ink": "#ffffff"}   # theme.ts NAMED
HERO_MID = "#d7ccff"                  # middle stop of Subtitle.tsx RAMP (script hero gradient)
# Subtitle.tsx per face: fitSize (base, ideal chars, min), WORD_EM, lineHeight, rowGap, DESC, column gap (em)
FIT = {"script": (149, 15, 88), "stomp": (176, 12, 98), "small": (54, 24, 38)}
WORD_EM = {"small": 0.83, "script": 0.83, "stomp": 0.66}
LINE_H = {"small": 1.24, "script": 1.5, "stomp": 1.15}
ROW_GAP = {"small": 0.06, "script": 0.02, "stomp": 0.02}
DESC = {"small": 0.04, "script": 0.07, "stomp": 0.0}
GAP_EM = {"small": 0.3, "script": 0.24, "stomp": 0.24}
HERO_LS_EM, HERO_ROW_FIT, BLOCK_GAP = -0.015, 0.9, 10
FACE_FONT = {"small": ("Be Vietnam Pro", "Medium"), "script": ("TF Youth Shandey", "Regular"),
             "stomp": ("DT Phudu", "Black")}
# (ascent, descent) em as Chrome lays the fonts out (hhea, or OS/2 typo when USE_TYPO_METRICS is set)
METRICS = {"Be Vietnam Pro": (1.0, 0.265), "TF Youth Shandey": (1.176, 0.42), "DT Phudu": (0.9, 0.18),
           "PS Bebas Neue": (0.9, 0.3)}
SMALL_EM = 0.58                       # mean advance of Be Vietnam Pro Medium (ink.ts has no table for it)
SHADOW = {"small": {"color": "#000000", "opacity": 75, "blur": 16, "distance": 3},
          "hero": {"color": "#000000", "opacity": 80, "blur": 22, "distance": 8},
          "hook": {"color": "#000000", "opacity": 70, "blur": 90, "distance": 20},
          "item": {"color": "#000000", "opacity": 60, "blur": 20, "distance": 4}}
# StepList.tsx card (px): border 1 + padding 34 + title row (Bebas 34, line 40.8) + 22 margin above the
# items, padding 40 + border 1 below; an item row = 12 + 12 padding + baseline-aligned Bebas 54 / DT Phudu
# Bold 58 (lh 1.1) = 92.98 tall, its baseline 64.78 below the row top.
ITEMS_TOP, CARD_BOTTOM, ITEM_H, ITEM_BASE = 1 + 34 + 40.8 + 22, 40 + 1, 92.98, 64.78
TITLE_BASE = 1 + 34 + 0.9 * 34


class AdapterError(Exception):
    """The project is not a finished dung-video-talking-head BUILD; the message names what is missing."""


def need(path: Path, what: str) -> Path:
    if not path.is_file():
        raise AdapterError(f"missing {what}: {path}")
    return path.resolve()


def rnd(x, nd=4):
    return round(float(x), nd)


def key(t, v, ease=None) -> list:
    """[time, value, interpolation?] — the tag describes the segment that ends at this key (CSS style);
    th_to_craft._key_sides turns it into the spec's key-side easing before writing the spec."""
    return [rnd(t), v] + ([ease] if ease else [])


def mono(keys: list) -> list:
    """Keys with strictly increasing times (a later key at the same time replaces the earlier one)."""
    out = []
    for k in keys:
        if out and k[0] <= out[-1][0] + 1e-6:
            out[-1] = k
        else:
            out.append(k)
    return out


def opacity(dur: float, fin: float, fade_at: float | None = None) -> list:
    """Fade in over `fin` s (outCubic ~ easeOut); linear fade out from `fade_at` to the clip end."""
    keys = [key(0, 0), key(min(fin, dur), 100, "easeOut")]
    if fade_at is not None and fade_at < dur - 1e-6:
        keys += [key(max(fade_at, min(fin, dur)), 100), key(dur, 0)]
    return mono(keys)


# ------------------------------------------------------------------ Subtitle.tsx

def ink_tables(skill_root: Path, release: str) -> dict:
    """ADV / INK glyph tables (em) of the hero fonts, parsed from the template's src/ink.ts."""
    path = need(skill_root / "releases" / release / "template" / "src" / "ink.ts", "template glyph table")
    src, out = path.read_text(encoding="utf-8"), {}
    for name in ("ADV", "INK"):
        m = re.search(r"export const %s\b[^=]*= (\{.*?\n\});" % name, src, re.S)
        if not m:
            raise AdapterError(f"{path}: table {name} not found")
        out[name] = json.loads(m.group(1))
    return out


def is_caps(t: str) -> bool:
    letters = [c for c in t if c.lower() != c.upper()]
    return len(letters) >= 2 and all(c == c.upper() for c in letters)


def _wface(face: str, t: str) -> str:
    """Caps words inside a script hero are drawn with the stomp face (DT Phudu Black)."""
    return "stomp" if face == "script" and is_caps(t) else face


def _glyph(face: str, t: str) -> str:
    return unicodedata.normalize("NFC", t.upper() if face == "stomp" else t)


def _pad(ink: dict, face: str, unit: str) -> float:
    """Glyph overhang (em) padded on both ends of a word or glue group (padEm)."""
    def side(t, lr):
        f = _wface(face, t)
        return 0.0 if f == "small" else ink["INK"][f][lr].get(_glyph(f, t)[0 if lr == "l" else -1], 0.0)
    ws = unit.split(" ")
    return side(ws[0], "l") + side(ws[-1], "r")


def _groups(words: list) -> list:
    out = []
    for i, w in enumerate(words):
        if i and words[i - 1].get("glue"):
            out[-1].append(i)
        else:
            out.append([i])
    return out


def _units(words: list) -> list:
    return [" ".join(words[i]["t"] for i in g) for g in _groups(words)]


def _keep(words: list, face: str, ink: dict, max_w: float) -> list:
    """Drop the glue of groups too wide even at the face's minimum size (keep)."""
    wide = set()
    for g in _groups(words):
        s = " ".join(words[i]["t"] for i in g)
        if (len(s) * WORD_EM[face] + _pad(ink, face, s)) * FIT[face][2] > max_w:
            wide.update(g)
    return [{**w, "glue": False} if i in wide else w for i, w in enumerate(words)]


def _fit(text: str, face: str) -> float:
    base, ideal, lo = FIT[face]
    return max(lo, min(base, base * ideal / max(len(text), 1)))


def _capped(words: list, face: str, size: float, ink: dict, max_w: float) -> float:
    units = _units(words)
    return min(size, max_w / (WORD_EM[face] * max(1, *map(len, units)) + max(_pad(ink, face, u) for u in units)))


def _em(text: str, face: str, ink: dict) -> float:
    """Width (em at size 1) of words on one row; hero faces = rowEm with the template's advances."""
    ws = text.split(" ")
    if face == "small":
        return SMALL_EM * sum(map(len, ws)) + GAP_EM["small"] * (len(ws) - 1)
    total = sum(sum(ink["ADV"][f].get(c, WORD_EM[f]) + HERO_LS_EM for c in _glyph(f, t)) + _pad(ink, face, t)
                for t in ws for f in [_wface(face, t)])
    return total + GAP_EM[face] * (len(ws) - 1)


def hero_words(block: dict) -> list:
    """Hero words as drawn: “quotes” around a quote-style hero."""
    ws = block["hero"]
    if block["style"] != "quote":
        return ws
    return [{**w, "t": ("“" if i == 0 else "") + w["t"] + ("”" if i == len(ws) - 1 else "")} for i, w in enumerate(ws)]


def _rows(words: list, face: str, size: float, ink: dict, max_w: float, nowrap: bool) -> list:
    """Greedy flex-wrap of the line's units into rows no wider than max_w."""
    rows, width, gap = [], 0.0, GAP_EM[face] * size
    for u in _units(words):
        uw = _em(u, face, ink) * size
        if rows and (nowrap or width + gap + uw <= max_w):
            rows[-1], width = rows[-1] + " " + u, width + gap + uw
        else:
            rows, width = rows + [u], uw
    return rows


def _stack(block: dict, ink: dict, safe: dict) -> list:
    """Lines of a block (face, size, rows, first-baseline y), stacked bottom-up from H - sub_bottom_px."""
    max_w = safe["sub_max_w"]
    face = "script" if block["style"] == "script" else "stomp"
    hero = _keep(hero_words(block), face, ink, max_w)
    fitted = _capped(hero, face, _fit(" ".join(w["t"] for w in block["hero"]), face), ink, max_w)
    row = HERO_ROW_FIT * max_w / _em(" ".join(w["t"] for w in hero), face, ink)
    one_row = bool(block.get("hero_row")) or (face == "script" and row >= FIT[face][2])
    lines = [("hero", face, hero, min(fitted, row) if one_row else fitted, one_row)]
    for name in ("top", "bottom"):
        if block[name]:
            ws = _keep(block[name], "small", ink, max_w)
            line = (name, "small", ws, _capped(ws, "small", _fit(" ".join(w["t"] for w in ws), "small"), ink, max_w), False)
            lines.insert(0, line) if name == "top" else lines.append(line)
    y, out = H - safe["sub_bottom_px"], []
    for j in range(len(lines) - 1, -1, -1):
        name, f, ws, size, nowrap = lines[j]
        rows, lh = _rows(ws, f, size, ink, max_w, nowrap), LINE_H[f] * size
        top = y - len(rows) * lh - (len(rows) - 1) * ROW_GAP[f] * size - (DESC[f] * size if j == len(lines) - 1 else 0)
        asc, desc = METRICS[FACE_FONT[f][0]]
        out.insert(0, {"line": name, "face": f, "words": ws, "size": size, "rows": rows,
                       "baseline": top + (lh + (asc - desc) * size) / 2})
        y = top - BLOCK_GAP
    return out


def subtitles(lock: dict, ink: dict, end_s: float) -> dict:
    """Text clips of every subtitle line, keyed "top" / "hero" / "bottom". A line starts at its first
    word's show time, holds to the block's out and fades over exit_f frames (the last block holds)."""
    fps, out = lock["fps"], {"top": [], "hero": [], "bottom": []}
    for b in lock["blocks"]:
        end = min(b["out"] + b["exit_f"] / fps, end_s)
        for ln in _stack(b, ink, lock["safe"]):
            at, f, hero = max(0.0, min(w["show"] for w in ln["words"])), ln["face"], ln["line"] == "hero"
            text = "\n".join(ln["rows"])
            color = NAMED["ink"] if f == "small" else NAMED[b["color"] or "ink"] if f == "stomp" else HERO_MID
            out[ln["line"]].append({
                "text": text.upper() if f == "stomp" else text, "name": f"{b['id']} {ln['line']}",
                "at": rnd(at), "dur": rnd(end - at), "font": FACE_FONT[f][0], "style": FACE_FONT[f][1],
                "size": rnd(ln["size"], 1), "color": color, "align": "center",
                "position": [W / 2, rnd(ln["baseline"], 1)], "shadow": SHADOW["hero" if hero else "small"],
                "tracking": round(HERO_LS_EM * 1000) if hero else 0,
                "opacity": opacity(end - at, REVEAL_F / fps, b["out"] - at)})
    return out


def srt_text(block: dict) -> str:
    """Caption text of a block: its lines top / hero / bottom, the hero as drawn (quotes, stomp in caps)."""
    hero = " ".join(w["t"] for w in hero_words(block))
    lines = [" ".join(w["t"] for w in block["top"]), hero if block["style"] == "script" else hero.upper(),
             " ".join(w["t"] for w in block["bottom"])]
    return "\n".join(ln for ln in lines if ln)


# ------------------------------------------------------------------ Hook.tsx, Cta.tsx, StepList.tsx

def _bebas_em(text: str) -> float:   # anim.ts bebasEm
    return sum(0.16 if c == " " else 0.21 if c in "Ii.,:;!'" else 0.59 if c in "MWmw%@" else 0.43 for c in text)


def hook(hk: dict, safe: dict) -> dict:
    """Bebas title centred 120 px above the middle: enter 0..land (x1.34 -> 1, rise 60 px, unblur),
    push x1.05 to out, exit to end (x0.58, drop 420 px, fade, blur 16)."""
    size = min(460, safe["sub_max_w"] / (1.05 * _bebas_em(hk["text"])))
    cy = (H - 240) / 2
    asc, desc = METRICS["PS Bebas Neue"]

    def keys(a, b, c, d):
        return [key(0, a), key(hk["land"], b, "easeOut"), key(hk["out"], c, "bezier"), key(hk["end"], d, "easeIn")]
    return {"text": hk["text"], "name": "Hook", "at": 0.0, "dur": hk["end"], "font": "PS Bebas Neue",
            "style": "Regular", "size": rnd(size, 1), "color": NAMED[hk["color"]], "align": "center",
            "position": [W / 2, rnd(cy + (asc - desc) / 2 * size, 1)], "shadow": SHADOW["hook"],
            "motion": {"anchor": [W / 2, cy], "scale": keys(134, 100, 105, rnd(105 * 0.58, 1)),
                       "position": keys([W / 2, cy + 60], [W / 2, cy], [W / 2, cy], [W / 2, cy + 420])},
            "opacity": keys(0, 100, 100, 0),
            "effects": [{"effect": "gaussian_blur", "params": {"blurriness": keys(26, 0, 0, 16)}}]}


def cta(c: dict, lock: dict, end_s: float) -> list:
    """Pill at the top of the text box: [👇][label, Be Vietnam Pro][KEYWORD, Bebas gold], 18 px gaps. Pops in
    with outBack over 12 frames (peak x1.0838 at 57.6 %, opaque from 36.4 %) and stays to the end."""
    lab, kw, fps, safe = c["label"], c["keyword"], lock["fps"], lock["safe"]
    k = min(1, (safe["sub_max_w"] / (1.084 * 1.015) - 120)
            / (1.3 * 44 + 0.82 * len(lab) * 40 + (_bebas_em(kw) + 0.1 * len(kw)) * 52))
    s_lab, s_kw, emoji = 40 * k, 52 * k, 1.3 * 44 * k
    w_lab, w_kw = _em(lab, "small", {}) * s_lab, (_bebas_em(kw) + 0.1 * len(kw)) * s_kw
    lab_right = W / 2 - (120 + emoji + w_lab + w_kw) / 2 + 2 + 40 + emoji + 18 + w_lab
    cy = rnd(safe["text_y_min"] + 40 + 2 + 20 + max(1.265 * s_lab, 1.2 * s_kw) / 2, 1)
    pop = POP_F / fps
    shared = {"at": rnd(c["show"]), "dur": rnd(end_s - c["show"]),
              "motion": {"anchor": [W / 2, cy], "position": [key(0, [W / 2, cy + 40]), key(pop, [W / 2, cy], "easeOut")],
                         "scale": [key(0, 0), key(0.576 * pop, 108.4, "easeOut"), key(pop, 100, "bezier")]},
              "opacity": [key(0, 0), key(0.364 * pop, 100, "easeOut")]}
    return [{**shared, "text": "👇 " + lab, "name": "CTA label", "font": "Be Vietnam Pro", "style": "Medium",
             "size": rnd(s_lab, 1), "color": "#ffffff", "align": "right",
             "position": [rnd(lab_right, 1), rnd(cy + 0.3675 * s_lab, 1)]},
            {**shared, "text": kw, "name": "CTA keyword", "font": "PS Bebas Neue", "style": "Regular",
             "size": rnd(s_kw, 1), "color": NAMED["gold"], "align": "left", "tracking": 100,
             "position": [rnd(lab_right + 18, 1), rnd(cy + 0.3 * s_kw, 1)]}]


def steps(st: dict, lock: dict) -> list:
    """Card bottom-anchored on the text box: the title, then one clip per item ("01  label") that slides in
    46 px at its show time and drops to 46 % opacity when the next item starts; all fade out together."""
    fps, safe, items = lock["fps"], lock["safe"], st["items"]
    top = H - safe["sub_bottom_px"] - CARD_BOTTOM - ITEMS_TOP - len(items) * ITEM_H
    x, end, c = (W - safe["sub_max_w"]) / 2 + 41, st["out"] + CARD_OUT_F / fps, [W / 2, H / 2]

    def move(at, dx, dy, t_in):          # enter offset (dx, dy) -> 0; card exit lifts 26 px
        return {"anchor": c, "position": mono([key(0, [c[0] + dx, c[1] + dy]), key(t_in, c, "easeOut"),
                                               key(st["out"] - at, c), key(end - at, [c[0], c[1] - 26])])}
    clips = [{"text": st["title"], "name": "Steps title", "at": rnd(st["in"]), "dur": rnd(end - st["in"]),
              "font": "PS Bebas Neue", "style": "Regular", "size": 34, "color": NAMED["gold"], "align": "left",
              "tracking": 160, "position": [x, rnd(top + TITLE_BASE, 1)], "motion": move(st["in"], 0, 36, CARD_IN_F / fps),
              "opacity": opacity(end - st["in"], CARD_IN_F / fps, st["out"] - st["in"])}]
    for i, it in enumerate(items):
        at = it["show"]
        nxt = items[i + 1]["show"] - at if i + 1 < len(items) else None
        op = [key(0, 0), key(ITEM_F / fps, 100, "easeOut")]
        if nxt is not None:              # 1-frame step to 46 %: convention-free stand-in for a hold key
            op += [key(nxt - 1 / fps, 100), key(nxt, 46)]
        op += [key(st["out"] - at, 46 if nxt is not None else 100), key(end - at, 0)]
        clips.append({"text": f"0{i + 1}  {it['label']}", "name": f"Step {i + 1}", "at": rnd(at),
                      "dur": rnd(end - at), "font": "DT Phudu", "style": "Bold", "size": 58, "color": "#ffffff",
                      "align": "left", "position": [x, rnd(top + ITEMS_TOP + i * ITEM_H + ITEM_BASE, 1)],
                      "shadow": SHADOW["item"], "motion": move(at, 46, 0, ITEM_F / fps), "opacity": mono(op)})
    return clips
