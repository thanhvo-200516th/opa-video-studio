#!/usr/bin/env python3
"""brooks_text — cụm chữ kiểu Joseph | Video Editing / Arthur Brooks của hồ sơ 'minimal-edu' (references/minimal-edu-style.json).

Chỉ dùng khi hồ sơ bật (profile.json = {"profile": "minimal-edu"}). Mọi số lấy từ file hồ sơ; vùng chữ theo B8 (key_y / cap_y của
text_fx.FX và KEY_ZONE_TOP). Trả `[(lane, clip)]` đúng dạng text_fx.FX.items / dviet_text (lane "text" = từ lớn, "text_low" = chữ nhỏ,
dấu ngoặc kép), chép thẳng vào danh sách items của FX / MotionFX.

    from brooks_text import caption_group, quote_text
    items = caption_group(hero="studs", before=["down", "to"], after=["the"], times=[1.0, 1.1, 1.3, 1.4], end=2.5, fps=30)

Từ lớn LUÔN do người gọi chỉ định (không đoán theo độ dài). Chữ hiện đúng như nhập (đã bỏ dấu phẩy B13); viết hoa đầu dòng B10 do người gọi
quyết (text_fx.cap_first). Vào: chữ nhỏ 1–3 khung (opacity), từ lớn blur-in 3–6 khung (serif +1), từ lớn thứ hai trễ 2–3 khung. Ra do
text_motion.ensure_motion(..., profile=prof, cuts=[...]) lo.
"""
from __future__ import annotations

import inspect
from pathlib import Path

from PIL import ImageFont

import style_profile as sp
import text_fx as tf
from motion_fx import GLOW, PALETTES
from text_motion import profile_in_frames

ROOT = Path(__file__).resolve().parent.parent
_FX = inspect.signature(tf.FX.__init__).parameters
MAX_W = _FX["max_w"].default                         # 800: rộng tối đa của vùng chữ B8, căn giữa x = 540
CX = 540
# vùng chữ B8: (mép trên mực, baseline thấp nhất, baseline mặc định) — khung trên y 240–680 (key_y), khung dưới y 1290–1480 (cap_y)
ZONES = {"key": (tf.KEY_ZONE_TOP, 680, _FX["key_y"].default), "cap": (1290, 1480, _FX["cap_y"].default)}
GAP = 10                                             # khe giữa dòng chữ nhỏ và đỉnh mực từ lớn (như text_fx.pair)
BLUR_FROM = 24                                       # blur-in của từ lớn: 24 → 0
STYLE_BY_WEIGHT = {800: "ExtraBold", 500: "Medium"}  # tên style của bản tĩnh Inter trong assets/fonts
QUOTE_LEFT_PCT = 0.06                                # dấu " mở căn trái x ≈ 6 % (BAO_CAO_TOAN_DIEN §4)
OPEN_Q, CLOSE_Q = "“", "”"
QUOTE_MARK_RATIO = 0.6                               # dấu “ ” ≈ cỡ hero × 0.6 (khi người gọi chỉ định dòng hero)


class Meter:
    """Đo chữ bằng file font thật của hồ sơ; role = hero_sans | hero_serif | small."""

    def __init__(self, prof: dict):
        self.fonts, self._cache = prof["fonts"], {}

    def spec(self, role: str) -> dict:
        return self.fonts[role]

    def tracking(self, role: str) -> float:
        return self.spec(role).get("tracking", tf.TRACKING["serif"])

    def style(self, role: str) -> str:
        s = self.spec(role)
        return s.get("style") or STYLE_BY_WEIGHT[s["weight"]]

    def font(self, role: str, size: int):
        k = (role, size)
        if k not in self._cache:
            f = Path(self.spec(role)["file"])
            path = ROOT / f if (ROOT / f).is_file() else tf.FONTS_DIR / f.name      # Playfair nằm ở thư mục font hệ thống
            self._cache[k] = ImageFont.truetype(str(path), size)
        return self._cache[k]

    def box(self, role: str, size: int, text: str):
        return self.font(role, size).getbbox(text, anchor="ls")        # (trái, trên, phải, dưới) từ gốc trái-baseline

    def width(self, role: str, size: int, text: str) -> float:
        b = self.box(role, size, text)
        return b[2] - b[0] + self.tracking(role) / 1000 * size * max(0, len(text) - 1)

    def advance(self, role: str, size: int, text: str) -> float:
        return self.font(role, size).getlength(text) + self.tracking(role) / 1000 * size * len(text)

    def ink_top(self, role: str, size: int, texts: list[str]) -> float:
        return max(-self.box(role, size, t)[1] for t in texts)

    def ink_bottom(self, role: str, size: int, texts: list[str]) -> float:
        return max(self.box(role, size, t)[3] for t in texts)


def _nfc(s: str) -> str:
    """tf.nfc + dấu nháy đơn thẳng ' → ’ (U+2019): FilmCraft tự đổi ' thành ’ nên fc_build chỉ khớp chữ spec khi spec đã viết ’."""
    return tf.nfc(s).replace("'", "’")


def _snap(t: float, fps: float) -> float:
    return round(t * fps) / fps


def _clip(M: Meter, role: str, text: str, size: int, x: float, y: float, align: str, color: str, shadow: bool,
          at: float, end: float, fps: float, frames: int, blur: bool) -> dict:
    """Một clip chữ + kiểu vào `frames` khung: blur=False → chỉ opacity (chữ nhỏ); blur=True → opacity + gaussian_blur (từ lớn)."""
    a, e = _snap(at, fps), _snap(end, fps)
    if e - a < (frames + 1) / fps - 1e-9:
        raise ValueError(f"'{text}': clip {e - a:.3f}s ngắn hơn kiểu vào {frames} khung")
    spec = M.spec(role)
    c = {"text": text, "at": a, "dur": e - a, "font": spec["family"], "style": M.style(role),
         "size": size, "color": color, "align": align, "position": [round(x), round(y)], "tracking": M.tracking(role),
         "name": f"Chữ · {text[:24]}"}
    if shadow:
        c["shadow"] = dict(tf.SHADOW)
    t_op = (max(1, round(0.6 * frames)) if blur else frames) / fps
    c["opacity"] = [[0, 0], [t_op, 100]]
    if blur:
        c["effects"] = [{"effect": "gaussian_blur", "params": {"blurriness": [[0, BLUR_FROM], [frames / fps, 0, "easeIn"]]}}]
    return c


class HeroColors:
    """Vòng xoay màu từ lớn của hồ sơ (text.colors.hero_rotation_dark / _light), mỗi nền một con đếm. `.next(on_dark)` → (màu, màu glow | None).
    Glow chỉ cho chữ màu trên nền tối (bảng motion_fx.PALETTES theo `name`); trắng / chữ trên nền giấy không phát sáng."""

    def __init__(self, prof: dict):
        col = prof["text"]["colors"]
        self._rot = {True: col["hero_rotation_dark"], False: col["hero_rotation_light"]}
        self._i = {True: 0, False: 0}

    def next(self, on_dark: bool) -> tuple[str, str | None]:
        rot = self._rot[on_dark]
        e = rot[self._i[on_dark] % len(rot)]
        self._i[on_dark] += 1
        return e["color"], _glow_of(e, on_dark)


def _glow_of(entry: dict, on_dark: bool) -> str | None:
    name = entry.get("name")
    return PALETTES[name]["glow"] if on_dark and name in PALETTES and name != "white" else None


def glow_for(prof: dict, color: str, on_dark: bool = True) -> str | None:
    """Màu glow của một màu chữ chính chỉ định tay: trắng / đen / nền giấy → None; màu có trong vòng xoay → theo vòng; màu lạ trên nền tối → chính nó."""
    col = prof["text"]["colors"]
    if not on_dark or color.upper() in (col["on_dark"].upper(), col["on_paper"].upper()):
        return None
    hit = next((e for e in col["hero_rotation_dark"] if e["color"].upper() == color.upper()), None)
    return _glow_of(hit, True) if hit else color


def _with_glow(items: list[tuple[str, dict]], glow: str | None, fps: float) -> list[tuple[str, dict]]:
    """B3 (hồ sơ): từ lớn có màu phát sáng NHẸ (motion_fx.GLOW['soft'], khoá như MotionFX.key_glow); bản sao, không sửa đầu vào."""
    if glow is None:
        return items
    g = GLOW["soft"]
    out = []
    for lane, c in items:
        ramp = min(0.35, max(1 / fps, c["dur"] - 1 / fps))
        fx = {"effect": "wonder_glow", "params": {"threshold": 30, "radius": g["radius"], "use_color": True, "color": glow,
                                                  "intensity": [[0, g["peak"]], [ramp, g["hold"]]]}}
        out.append((lane, {**c, "effects": [*c.get("effects", []), fx]}))
    return out


def _palette(p: dict, on_dark: bool, accent: bool) -> tuple[str, str, bool]:
    """(màu chữ, màu từ lớn, có bóng). Màu nhấn chỉ trên nền sáng; chữ đen trên giấy không bóng (B2 suy đoán)."""
    col = p["colors"]
    base = col["on_dark"] if on_dark else col["on_paper"]
    use_accent = accent and not (on_dark and col.get("accent_only_on_light", True))
    return base, (col["accent"] if use_accent else base), on_dark


def _sizes(M: Meter, p: dict, hero_role: str, hero_text: str) -> tuple[int, int]:
    """(cỡ từ lớn, cỡ chữ nhỏ): từ lớn thu cho vừa MAX_W, chữ nhỏ giữ tỉ lệ trong ratio_min..ratio_max."""
    hs = p["size_hero"]
    while hs > 40 and M.width(hero_role, hs, hero_text) > MAX_W:
        hs -= 2
    lo, hi = -(-hs // p["ratio_max"]), hs / p["ratio_min"]
    return hs, int(max(lo, min(hi, round(hs * p["size_small"] / p["size_hero"]))))


def _small_xs(M: Meter, size: int, before: list[str], after: list[str], left: float, right: float) -> list[tuple[float, str]]:
    """(x, căn) cho từng chữ nhỏ theo thứ tự đọc: nhóm trước căn trái từ mép trái, nhóm sau căn phải từ mép phải (sandwich)."""
    sp_w = M.advance("small", size, " ")
    adv_b, adv_a = [M.advance("small", size, w) for w in before], [M.advance("small", size, w) for w in after]
    tb, ta = sum(adv_b) + sp_w * max(0, len(before) - 1), sum(adv_a) + sp_w * max(0, len(after) - 1)
    if before and after and tb + ta + sp_w > right - left + 2:
        raise ValueError("chữ nhỏ trước + sau rộng hơn từ lớn: chọn từ lớn dài hơn, bớt chữ nhỏ hoặc tăng span_ratio")
    if max(tb, ta) > MAX_W:
        raise ValueError("chữ nhỏ rộng hơn vùng chữ B8 (800 px)")
    xs_b, x = [], left
    for a in adv_b:
        xs_b.append((x, "left"))
        x += a + sp_w
    xs_a, x = [], right
    for a in reversed(adv_a):
        xs_a.append((x, "right"))
        x -= a + sp_w
    return xs_b + xs_a[::-1]


def _baselines(M: Meter, zone: str, hero_role: str, hs: int, heroes: list[str], ss: int, smalls: list[str]) -> tuple[float, float]:
    """(baseline từ lớn, baseline chữ nhỏ) trong vùng chữ B8: baseline mặc định key_y / cap_y, dời xuống nếu đỉnh mực < mép trên vùng."""
    lo, hi, y0 = ZONES[zone]
    hero_txt = " ".join(heroes)
    top_h = M.ink_top(hero_role, hs, [hero_txt])
    sbase = y0 - top_h - GAP - M.ink_bottom("small", ss, smalls) if smalls else None
    top = (sbase - M.ink_top("small", ss, smalls)) if smalls else y0 - top_h
    base = y0 + max(0.0, lo - top)
    if base > hi:
        raise ValueError(f"cụm chữ không vừa vùng '{zone}' (baseline {base:.0f} > {hi})")
    return base, (sbase + (base - y0) if smalls else 0.0)


def _hero_clips(M: Meter, role: str, heroes: list[str], hs: int, y: float, color: str, shadow: bool, times: list[float],
                end: float, fps: float, frames: int, p: dict) -> list[tuple[str, dict]]:
    """Từ lớn (1 clip căn giữa) hoặc cặp 2 từ cạnh nhau theo advance(); từ thứ hai vào trễ second_hero_delay_frames khung."""
    if len(heroes) == 1:
        return [("text", _clip(M, role, heroes[0], hs, CX, y, "center", color, shadow, times[0], end, fps, frames, True))]
    lo, hi = p["second_hero_delay_frames"]
    left = CX - M.width(role, hs, " ".join(heroes)) / 2
    at2 = min(max(times[1], times[0] + lo / fps), times[0] + hi / fps)
    return [("text", _clip(M, role, w, hs, x, y, "left", color, shadow, at, end, fps, frames, True))
            for w, x, at in ((heroes[0], left, times[0]), (heroes[1], left + M.advance(role, hs, heroes[0] + " "), at2))]


def _fit(M: Meter, p: dict, role: str, zone: str, heroes: list[str], before: list[str], after: list[str],
         span: float) -> tuple[int, int, float, float, list[tuple[float, str]]]:
    """(cỡ hero, cỡ nhỏ, baseline hero, baseline nhỏ, vị trí chữ nhỏ). Tự co cho vừa trước khi báo lỗi: không vừa vùng → hero thu 8 px
    (tối thiểu text.auto_fit_min_hero); chữ nhỏ rộng hơn từ lớn → span_ratio +0,1 (tối đa bề ngang B8 800 px)."""
    floor, size, text = p.get("auto_fit_min_hero", 120), p["size_hero"], " ".join(heroes)
    while True:
        hs, ss = _sizes(M, {**p, "size_hero": size}, role, text)
        try:
            hb, sb = _baselines(M, zone, role, hs, heroes, ss, before + after)
            half = M.width(role, hs, text) / 2 * span
            return hs, ss, hb, sb, _small_xs(M, ss, before, after, CX - half, CX + half)
        except ValueError as e:
            wide = MAX_W / M.width(role, hs, text)
            if "không vừa vùng" in str(e) and size > floor:
                size = max(floor, size - 8)
            elif "rộng hơn từ lớn" in str(e) and min(span + 0.1, wide) > span + 1e-9:
                span = min(span + 0.1, wide)
            else:
                raise


def _hero_color(prof: dict, p: dict, on_dark: bool, accent: bool, color: str | None, colors: HeroColors | None) -> tuple[str, str | None]:
    """(màu từ lớn, màu glow | None): màu chỉ định > vòng xoay `colors` > màu nhấn / màu gốc của hồ sơ (không glow)."""
    if color:
        return color, glow_for(prof, color, on_dark)
    if colors is not None and not (accent and not on_dark):
        return colors.next(on_dark)
    return _palette(p, on_dark, accent)[1], None


def caption_group(hero, before, after, times, end: float, fps: float = 30, style: str = "sans", on_dark: bool = True,
                  accent: bool = False, zone: str = "key", span_ratio: float | None = None, prof: dict | None = None,
                  color: str | None = None, colors: HeroColors | None = None) -> list[tuple[str, dict]]:
    """Một cụm chữ ≤ max_words_per_group từ, đúng 1 từ lớn (hoặc cặp 2 từ) do người gọi chỉ định.
    hero: str | [str, str]; before / after: chữ nhỏ trước / sau từ lớn; times: giây bắt đầu của TỪNG từ theo thứ tự đọc
    (before + hero + after); end: giây kết thúc cả cụm; style 'sans' (Inter ExtraBold) | 'serif' (Playfair Bold Italic);
    on_dark: nền tối (chữ trắng) hay sáng (chữ đen, nhấn #123CE8 nếu accent); zone 'key' | 'cap' (vùng chữ B8);
    span_ratio: bề ngang chữ nhỏ so với từ lớn (mặc định theo hồ sơ, đo = 1,0; Figma ghi 0,75);
    color: màu từ lớn chỉ định tay (chữ nhỏ vẫn trắng / đen); colors: HeroColors(prof) — khi color=None lấy màu kế tiếp. Từ lớn có màu
    (không trắng / đen, nền tối) kèm wonder_glow nhẹ (B3). Vùng chật / chữ nhỏ quá rộng: tự co (xem _fit) rồi mới báo lỗi."""
    prof = prof or sp.load(name="minimal-edu")
    p = prof["text"]
    heroes = [_nfc(hero)] if isinstance(hero, str) else [_nfc(w) for w in hero]
    before, after = [_nfc(w) for w in before], [_nfc(w) for w in after]
    nb, nh = len(before), len(heroes)
    if not 1 <= nh <= 2 or style not in ("sans", "serif") or zone not in ZONES:
        raise ValueError("hero 1–2 từ; style 'sans'|'serif'; zone 'key'|'cap'")
    if nb + nh + len(after) > p["max_words_per_group"] or len(times) != nb + nh + len(after):
        raise ValueError(f"cụm ≤ {p['max_words_per_group']} từ và `times` phải có đúng một mốc cho mỗi từ")
    M, role = Meter(prof), "hero_sans" if style == "sans" else "hero_serif"
    f_small, f_hero = profile_in_frames(prof)
    f_hero += p["serif_extra_frames"] if style == "serif" else 0
    base_c, _, shadow = _palette(p, on_dark, accent)
    hero_c, glow = _hero_color(prof, p, on_dark, accent, color, colors)
    hs, ss, hb, sb, xs = _fit(M, p, role, zone, heroes, before, after, p["span_ratio"] if span_ratio is None else span_ratio)
    smalls = [("text_low", _clip(M, "small", w, ss, x, sb, al, base_c, shadow, t, end, fps, f_small, False))
              for w, t, (x, al) in zip(before + after, times[:nb] + times[nb + nh:], xs)]
    hero_items = _hero_clips(M, role, heroes, hs, hb, hero_c, shadow, times[nb:nb + nh], end, fps, f_hero, p)
    return smalls[:nb] + _with_glow(hero_items, glow, fps) + smalls[nb:]


def _quote_layout(M: Meter, p: dict, lines: list[str], extra: str | None) -> tuple[int, float, float]:
    """(cỡ chữ, bước dòng, baseline dòng đầu): cỡ thu cho vừa MAX_W và vừa chiều cao khung từ khoá B8; khối căn giữa khung."""
    lo, hi, _ = ZONES["key"]
    size = p["size_hero"]
    while True:
        wide = max(M.width("hero_sans", size, ln) for ln in lines)
        f = M.font("hero_sans", size)
        pitch = sum(f.getmetrics())                       # ascent + descent thật của font
        n = len(lines) + (1 if extra else 0)
        top, bot = M.ink_top("hero_sans", size, lines), M.ink_bottom("hero_sans", size, lines)
        height = (n - 1) * pitch + top + bot
        if (wide <= MAX_W and height <= hi - lo) or size <= 40:
            return size, pitch, lo + (hi - lo - height) / 2 + top
        size -= 2


def _quote_entries(lines: list[str], last_word_serif: bool, hero_index: int | None) -> list[tuple[str, str, bool]]:
    """(vai trò font, chữ, là cỡ hero) theo thứ tự đọc; từ cuối của dòng cuối tách thành dòng serif riêng (cùng cỡ với dòng đó)."""
    out = []
    for i, ln in enumerate(lines):
        hero = i == hero_index
        if last_word_serif and i == len(lines) - 1:
            head, _, tail = ln.rpartition(" ")
            if head:
                out.append(("hero_sans" if hero else "small", head, hero))
            out.append(("hero_serif", tail, hero))
        else:
            out.append(("hero_sans" if hero else "small", ln, hero))
    return out


def _quote_hero_layout(M: Meter, p: dict, ents: list[tuple[str, str, bool]]) -> tuple[int, int, list[float]]:
    """(cỡ hero, cỡ nhỏ, baseline từng dòng): cỡ nhỏ = size_small (chỉ thu khi một dòng nhỏ vượt MAX_W), cỡ hero thu từ size_hero cho
    vừa MAX_W và chiều cao khung từ khoá B8; khối căn giữa khung."""
    lo, hi, _ = ZONES["key"]
    hs, ss = p["size_hero"], p["size_small"]
    while ss > 20 and any(M.width(r, ss, t) > MAX_W for r, t, h in ents if not h):
        ss -= 2
    while True:
        sizes = [hs if h else ss for _, _, h in ents]
        fits = all(M.width(r, z, t) <= MAX_W for (r, t, _), z in zip(ents, sizes))
        tops = [M.ink_top(r, z, [t]) for (r, t, _), z in zip(ents, sizes)]
        bases = [0.0]
        for k in range(1, len(ents)):
            bases.append(bases[-1] + 0.25 * sizes[k - 1] + GAP + tops[k])
        height = bases[-1] + M.ink_bottom(ents[-1][0], sizes[-1], [ents[-1][1]]) - (bases[0] - tops[0])
        if (fits and height <= hi - lo) or hs <= 40:
            y0 = lo + (hi - lo - height) / 2 + tops[0]
            return hs, ss, [y0 + b for b in bases]
        hs -= 2


def _quote_hero(M: Meter, p: dict, lines: list[str], last_word_serif: bool, hero_index: int, at: float, end: float, fps: float,
                t_last: float, frames: tuple[int, int], hero_color: str | None = None,
                glow: str | None = None) -> list[tuple[str, dict]]:
    """quote_text khi người gọi chỉ định dòng chính: dòng đó cỡ hero căn giữa, các dòng khác cỡ nhỏ căn trái, dấu “ ” cỡ hero × 0.6.
    hero_color / glow: màu (và glow nhẹ) của dòng chính — kể cả từ serif cuối nếu nằm trên dòng đó; các dòng khác và dấu ngoặc vẫn trắng."""
    f_small, f_hero = frames
    ents = _quote_entries(lines, last_word_serif, hero_index)
    hs, ss, ys = _quote_hero_layout(M, p, ents)
    left, right, white, mk = CX - MAX_W / 2, CX + MAX_W / 2, p["colors"]["on_dark"], round(hs * QUOTE_MARK_RATIO)
    q_w = M.advance("hero_serif", mk, CLOSE_Q)
    sizes = [hs if h else ss for _, _, h in ents]
    top_of = lambda k: ys[k] - M.ink_top(ents[k][0], sizes[k], [ents[k][1]])          # noqa: E731  đỉnh mực của dòng k
    q_ink = M.ink_top("hero_serif", mk, [OPEN_Q])
    items = [("text_low", _clip(M, "hero_serif", OPEN_Q, mk, QUOTE_LEFT_PCT * 1080, top_of(0) + q_ink, "left", white, True, at, end, fps, f_small, False))]
    last = len(ents) - 1
    for k, ((role, text, hero), z, y) in enumerate(zip(ents, sizes, ys)):
        if role == "hero_serif":
            x, al, t0, fr = right - q_w, "right", t_last, f_hero + p["serif_extra_frames"]
        else:
            x, al, t0, fr = (CX, "center", at, f_hero) if hero else (left, "left", at, f_small if not hero else f_hero)
        lane = "text" if hero or role == "hero_serif" else "text_low"
        c = _clip(M, role, text, z, x, y, al, hero_color if hero and hero_color else white, True, t0, end, fps, fr, hero or role == "hero_serif")
        items += _with_glow([(lane, c)], glow if hero else None, fps)
    if ents[last][0] == "hero_serif":
        qx = right - q_w
    else:
        w = M.advance(ents[last][0], sizes[last], ents[last][1])
        qx = (CX + w / 2) if ents[last][2] else left + w
    items.append(("text_low", _clip(M, "hero_serif", CLOSE_Q, mk, qx, top_of(last) + q_ink, "left", white, True, t_last, end, fps, f_small, False)))
    return items


def quote_text(lines: list[str], last_word_serif: bool, at: float, dur: float, fps: float = 30, last_at: float | None = None,
               prof: dict | None = None, hero_index: int | None = None, hero_color: str | None = None) -> list[tuple[str, dict]]:
    """Chữ của quote card (nền do fx_gfx dựng): dấu “ căn trái x ≈ 6 % ở đầu dòng 1, các dòng sans trắng căn trái vào vùng chữ B8
    (x 140–940), từ cuối của dòng cuối tách ra serif italic trắng căn phải (last_word_serif) kèm dấu ” cạnh nó.
    at / dur: thời gian cả khối (giây); last_at: lúc từ cuối vào (mặc định at + second_hero_delay_frames[0] khung).
    hero_index (người gọi chỉ định, không đoán): dòng đó cỡ text.size_hero (Inter ExtraBold) căn giữa, các dòng khác cỡ text.size_small,
    dấu “ ” cỡ hero × 0.6 (Playfair). None = mọi dòng cùng một cỡ (dấu ngoặc cỡ size_small).
    hero_color (cần hero_index): màu dòng chính; có màu (không trắng) → glow nhẹ như caption_group."""
    prof = prof or sp.load(name="minimal-edu")
    p = prof["text"]
    lines = [_nfc(ln) for ln in lines]
    if hero_index is not None and not 0 <= hero_index < len(lines):
        raise ValueError(f"hero_index {hero_index} ngoài phạm vi {len(lines)} dòng")
    if hero_color and hero_index is None:
        raise ValueError("hero_color cần hero_index (dòng chính do người gọi chỉ định)")
    M, frames = Meter(prof), profile_in_frames(prof)
    f_small, f_hero = frames
    t_last = at + p["second_hero_delay_frames"][0] / fps if last_at is None else last_at
    if hero_index is not None:
        glow = glow_for(prof, hero_color) if hero_color else None
        return _quote_hero(M, p, lines, last_word_serif, hero_index, at, at + dur, fps, t_last, frames, hero_color, glow)
    tail = None
    if last_word_serif:
        head, _, tail = lines[-1].rpartition(" ")
        lines = lines[:-1] + ([head] if head else [])
    size, pitch, y0 = _quote_layout(M, p, lines, tail)
    left, right, end, white = (CX - MAX_W / 2), (CX + MAX_W / 2), at + dur, p["colors"]["on_dark"]
    mk = p["size_small"]
    q_open = _clip(M, "hero_serif", OPEN_Q, mk, QUOTE_LEFT_PCT * 1080, y0 - M.ink_top("hero_sans", size, lines) + M.ink_top("hero_serif", mk, [OPEN_Q]),
                   "left", white, True, at, end, fps, f_small, False)
    items = [("text_low", q_open)]
    items += [("text", _clip(M, "hero_sans", ln, size, left, y0 + i * pitch, "left", white, True, at, end, fps, f_hero, True))
              for i, ln in enumerate(lines)]
    if tail:
        q_w = M.advance("hero_serif", mk, CLOSE_Q)
        items.append(("text", _clip(M, "hero_serif", tail, size, right - q_w, y0 + len(lines) * pitch, "right", white, True, t_last, end, fps,
                                    f_hero + p["serif_extra_frames"], True)))
        qx, qy = right - q_w, y0 + len(lines) * pitch
    else:
        qx, qy = left + M.advance("hero_sans", size, lines[-1]), y0 + (len(lines) - 1) * pitch
    items.append(("text_low", _clip(M, "hero_serif", CLOSE_Q, mk, qx, qy, "left", white, True, t_last, end, fps, f_small, False)))
    return items
