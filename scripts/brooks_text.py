#!/usr/bin/env python3
"""brooks_text — cụm chữ kiểu Joseph | Video Editing / Arthur Brooks của hồ sơ 'minimal-edu' (references/minimal-edu-style.json).

Chỉ dùng khi hồ sơ bật (profile.json = {"profile": "minimal-edu"}). Mọi số lấy từ file hồ sơ; vùng chữ theo B8 (key_y / cap_y của
text_fx.FX và KEY_ZONE_TOP). Trả `[(lane, clip)]` đúng dạng text_fx.FX.items / dviet_text (lane "text" = từ lớn, "text_low" = chữ nhỏ,
dấu ngoặc kép), chép thẳng vào danh sách items của FX / MotionFX.

    from brooks_text import caption_group, quote_text
    items = caption_group(hero="studs", before=["down", "to"], after=["the"], times=[1.0, 1.1, 1.3, 1.4], end=2.5, fps=30)
    items = caption_group(..., looks=HeroLooks(prof), gfx_dir=work / "gfx")      # chiều sâu: glow / gradient PNG / bóng đổ sâu (3.6.2)

Từ lớn LUÔN do người gọi chỉ định (không đoán theo độ dài). Chữ hiện đúng như nhập (đã bỏ dấu phẩy B13); viết hoa đầu dòng B10 do người gọi
quyết (text_fx.cap_first). Vào: chữ nhỏ 1–3 khung (opacity), từ lớn blur-in 3–6 khung (serif +1), từ lớn thứ hai trễ 2–3 khung. Ra do
text_motion.ensure_motion(..., profile=prof, cuts=[...]) lo.
"""
from __future__ import annotations

import hashlib
import inspect
from pathlib import Path

from PIL import ImageFont

import fx_gfx
import style_profile as sp
import text_fx as tf
from motion_fx import MX_SHADOW, PALETTES
from text_motion import MIN_ENTRY_FRAMES, kinetic_in, kinetic_params, stagger_times

ROOT = Path(__file__).resolve().parent.parent
_FX = inspect.signature(tf.FX.__init__).parameters
MAX_W = _FX["max_w"].default                         # 800: rộng tối đa của vùng chữ B8, căn giữa x = 540
CX = 540
# 3 vùng chữ của hồ sơ (research_zones_typo.md, 1080×1920): (mép trên, mép dưới, tâm x, rộng tối đa). Cấm: y < 260, y > 1440, x > 890 khi y ≥ 720.
ZONES = {"top": (260, 680, 540, 840), "lower": (1180, 1430, 500, 760),
         "mid_left": (720, 1100, 330, 420), "mid_right": (720, 1100, 680, 420), "mid_center": (720, 1100, 500, 760)}
ZONE_ALIAS = {"key": "top", "cap": "lower"}          # tên cũ (B8): khung trên / khung dưới
CHIN_GAP = 30                                        # chữ dưới cằm ≥ 30 px
TOP_CLEAR = 40                                       # vùng trên: còn ≥ 40 px từ chữ tới đỉnh đầu
BLOCK_H = 200                                        # cao ước lượng của một cụm chữ khi chọn vùng
GAP = 10                                             # khe giữa dòng chữ nhỏ và đỉnh mực từ lớn (như text_fx.pair)
PIVOT_Y = 0.33                                       # neo y = baseline − 0,33 × cỡ chữ (≈ giữa chiều cao chữ)
STYLE_BY_WEIGHT = {800: "ExtraBold", 500: "Medium"}  # tên style của bản tĩnh Inter trong assets/fonts
QUOTE_LEFT_PCT = 0.06                                # dấu " mở căn trái x ≈ 6 % (BAO_CAO_TOAN_DIEN §4)
OPEN_Q, CLOSE_Q = "“", "”"
QUOTE_MARK_RATIO = 0.6                               # dấu “ ” ≈ cỡ hero × 0.6 (khi người gọi chỉ định dòng hero)
# quầng wonder_glow của hồ sơ (profile key: text.glow.<mức>), đo bằng khung hình thật (typo_proof/): đủ thấy ở cỡ điện thoại, chữ vẫn nét
GLOW_LEVEL = {"normal": {"radius": 30, "peak": 230, "hold": 110}, "soft": {"radius": 22, "peak": 140, "hold": 60}}
LOOKS = ("glow", "gradient", "shadow_deep", "glow_shadow", "shadow_light")
LIGHT_LOOK = {"glow": "shadow_light", "glow_shadow": "shadow_light", "shadow_deep": "shadow_light"}   # nền sáng: không glow
LIGHT_TAG = "Chữ gradient sáng"                      # tên clip gradient trên nền sáng (edit_rules: không đòi glow)


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


def _span(text: str, at: float, end: float, fps: float) -> tuple[float, float]:
    a, e = _snap(at, fps), _snap(end, fps)
    if e - a < (MIN_ENTRY_FRAMES + 1) / fps - 1e-9:
        raise ValueError(f"'{text}': clip {e - a:.3f}s ngắn hơn kiểu vào tối thiểu {MIN_ENTRY_FRAMES} khung")
    return a, e


def _pivot(M: Meter, role: str, text: str, size: int, x: float, y: float, align: str) -> list[int]:
    """Điểm neo phóng / dời của chữ: giữa mực (x) và giữa chiều cao chữ (y), để scale 90 → 100 % nở quanh chữ, không quanh baseline."""
    cx = {"center": x, "left": x + M.width(role, size, text) / 2, "right": x - M.width(role, size, text) / 2}[align]
    return [round(cx), round(y - PIVOT_Y * size)]


def _clip(M: Meter, role: str, text: str, size: int, x: float, y: float, align: str, color: str, shadow: bool | dict,
          at: float, end: float, fps: float, kin: dict, ov: bool = False) -> dict:
    """Một clip chữ + kiểu vào mượt text_motion.kinetic_in (Y / scale / blur / opacity; ov = vọt 106 % cho từ lớn, không cho số / tiền).
    shadow: True = bóng chuẩn text_fx.SHADOW, dict = bóng chỉ định (kiểu chữ), False = không bóng. Không bao giờ có viền chữ (B2)."""
    a, e = _span(text, at, end, fps)
    spec = M.spec(role)
    c = {"text": text, "at": a, "dur": e - a, "font": spec["family"], "style": M.style(role),
         "size": size, "color": color, "align": align, "position": [round(x), round(y)], "tracking": M.tracking(role),
         "name": f"Chữ · {text[:24]}"}
    if shadow:
        c["shadow"] = dict(tf.SHADOW if shadow is True else shadow)
    kinetic_in(c, fps, kin, ov, _pivot(M, role, text, size, x, y, align))
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


def _with_glow(items: list[tuple[str, dict]], glow: str | None, fps: float, level: str = "soft") -> list[tuple[str, dict]]:
    """B3 (hồ sơ): từ lớn có màu phát sáng (GLOW_LEVEL['soft'] cho chữ màu thường / gradient); level='normal' cho kiểu "glow"
    (GLOW_LEVEL['normal'], quầng thấy rõ ở cỡ điện thoại); bản sao, không sửa đầu vào."""
    if glow is None:
        return items
    g = GLOW_LEVEL[level]
    out = []
    for lane, c in items:
        ramp = min(0.35, max(1 / fps, c["dur"] - 1 / fps))
        fx = {"effect": "wonder_glow", "params": {"threshold": 30, "radius": g["radius"], "use_color": True, "color": glow,
                                                  "intensity": [[0, g["peak"]], [ramp, g["hold"]]]}}
        out.append((lane, {**c, "effects": [*c.get("effects", []), fx]}))
    return out


class HeroLooks:
    """Vòng xoay kiểu chiều sâu của từ lớn (text.hero_looks) + cặp màu gradient (text.gradients), mỗi nền một con đếm.
    `.next(on_dark)` → (kiểu, [màu đầu, màu cuối] | None). Nền sáng: glow / glow_shadow / shadow_deep → shadow_light (không glow)."""

    def __init__(self, prof: dict):
        t = prof["text"]
        self._rot, self._grad = t["hero_looks"], t["gradients"]
        self._i, self._g = {True: 0, False: 0}, {True: 0, False: 0}

    def next(self, on_dark: bool) -> tuple[str, list[str] | None]:
        name = self._rot[self._i[on_dark] % len(self._rot)]
        self._i[on_dark] += 1
        name = name if on_dark else LIGHT_LOOK.get(name, name)
        if name != "gradient":
            return name, None
        pairs = self._grad["dark" if on_dark else "light"]
        self._g[on_dark] += 1
        return name, list(pairs[(self._g[on_dark] - 1) % len(pairs)])


def _pick_look(prof: dict, on_dark: bool, looks: HeroLooks | None, name: str | None, color: str, glow: str | None,
               gfx_dir, stops: list[str] | None = None) -> dict | None:
    """Kiểu chữ đã chốt (dict) hoặc None. `name` chỉ định tay thắng `looks`; nền sáng không glow (glow → shadow_light).
    stops: cặp màu gradient chỉ định (kiểu gradient chỉ định tay); None = cặp đầu của hồ sơ."""
    if name is None and looks is None:
        return None
    if name is None:
        name, stops = looks.next(on_dark)
    elif name not in LOOKS:
        raise ValueError(f"look phải là một trong {LOOKS}")
    elif not on_dark:
        name = LIGHT_LOOK.get(name, name)
    sh = prof["text"]["look_shadows"]
    spec = {"name": name, "stops": None, "glow": None, "level": "normal", "on_dark": on_dark, "gfx_dir": gfx_dir,
            "shadow": {"glow": MX_SHADOW, "glow_shadow": sh["deep"], "shadow_deep": sh["deep"], "shadow_light": sh["light"]}.get(name, False)}
    if name in ("glow", "glow_shadow") and on_dark:
        spec["glow"] = glow or color
    if name == "gradient":
        if gfx_dir is None:
            raise ValueError("look 'gradient' cần gfx_dir (thư mục gfx của work)")
        spec["stops"] = stops or list(prof["text"]["gradients"]["dark" if on_dark else "light"][0])
        spec["level"] = "soft"
        spec["glow"] = (glow_for(prof, spec["stops"][0]) or spec["stops"][0]) if on_dark else None
    return spec


def _gradient_hero(M: Meter, role: str, text: str, size: int, x: float, y: float, align: str, look: dict,
                   at: float, end: float, fps: float, kin: dict, ov: bool) -> tuple[str, dict]:
    """Từ lớn tô gradient: PNG 1080×1920 nền trong suốt (fx_gfx.gradient_text, cùng baseline / cỡ / mép căn như clip chữ) + vào mượt như chữ thường.
    PNG vẽ không giãn chữ (tracking) nên tâm tính theo độ rộng thật của font."""
    font = M.font(role, size)
    w = font.getlength(text)
    cx = {"center": x, "left": x + w / 2, "right": x - w / 2}[align]
    key = hashlib.md5(f"{text}|{role}|{size}|{look['stops']}|{round(cx)}|{round(y)}|{look['on_dark']}".encode()).hexdigest()[:10]
    png = fx_gfx.gradient_text(Path(look["gfx_dir"]), f"hero_grad_{key}", text, font.path, size, round(cx), round(y), look["stops"],
                               shadow=look["on_dark"])
    a, e = _span(text, at, end, fps)
    tag = "Chữ gradient" if look["on_dark"] else LIGHT_TAG
    c = {"src": png, "at": a, "dur": e - a, "name": f"{tag} · {text[:24]}"}
    kinetic_in(c, fps, kin, ov)                  # neo = tâm phần có nét của PNG
    return "text_img", c


def _hero_item(M: Meter, role: str, text: str, size: int, x: float, y: float, align: str, color: str, shadow: bool,
               at: float, end: float, fps: float, kin: dict, look: dict | None, glow: str | None,
               ov: bool = False) -> list[tuple[str, dict]]:
    """Một chữ lớn hoàn chỉnh (clip + glow). look=None: hành vi cũ (bóng chuẩn, glow nhẹ theo `glow`); có look: bóng / glow / gradient theo kiểu."""
    if look is None:
        return _with_glow([("text", _clip(M, role, text, size, x, y, align, color, shadow, at, end, fps, kin, ov))], glow, fps)
    if look["name"] == "gradient":
        item = _gradient_hero(M, role, text, size, x, y, align, look, at, end, fps, kin, ov)
    else:
        item = ("text", _clip(M, role, text, size, x, y, align, color, look["shadow"], at, end, fps, kin, ov))
    return _with_glow([item], look["glow"], fps, look["level"])


def _palette(p: dict, on_dark: bool, accent: bool) -> tuple[str, str, bool]:
    """(màu chữ, màu từ lớn, có bóng). Màu nhấn chỉ trên nền sáng; chữ đen trên giấy không bóng (B2 suy đoán)."""
    col = p["colors"]
    base = col["on_dark"] if on_dark else col["on_paper"]
    use_accent = accent and not (on_dark and col.get("accent_only_on_light", True))
    return base, (col["accent"] if use_accent else base), on_dark


def _sizes(M: Meter, p: dict, hero_role: str, hero_text: str, max_w: float = MAX_W) -> tuple[int, int]:
    """(cỡ từ lớn, cỡ chữ nhỏ): từ lớn thu cho vừa max_w, chữ nhỏ giữ tỉ lệ trong ratio_min..ratio_max."""
    hs = p["size_hero"]
    while hs > 40 and M.width(hero_role, hs, hero_text) > max_w:
        hs -= 2
    lo, hi = -(-hs // p["ratio_max"]), hs / p["ratio_min"]
    return hs, int(max(lo, min(hi, round(hs * p["size_small"] / p["size_hero"]))))


def _small_xs(M: Meter, size: int, before: list[str], after: list[str], left: float, right: float, cx: float = CX,
              max_w: float = MAX_W) -> list[tuple[float, str]]:
    """(x, căn) cho từng chữ nhỏ theo thứ tự đọc: nhóm trước căn trái từ mép trái, nhóm sau căn phải từ mép phải (sandwich)."""
    sp_w = M.advance("small", size, " ")
    adv_b, adv_a = [M.advance("small", size, w) for w in before], [M.advance("small", size, w) for w in after]
    tb, ta = sum(adv_b) + sp_w * max(0, len(before) - 1), sum(adv_a) + sp_w * max(0, len(after) - 1)
    if before and after and tb + ta + sp_w > right - left + 2:
        raise ValueError("chữ nhỏ trước + sau rộng hơn từ lớn: chọn từ lớn dài hơn, bớt chữ nhỏ hoặc tăng span_ratio")
    if max(tb, ta) > max_w:
        raise ValueError(f"chữ nhỏ rộng hơn vùng chữ ({max_w:.0f} px)")
    if not after and tb > right - left:      # chỉ một phía và rộng hơn từ lớn: căn giữa dòng nhỏ, không tràn khỏi khung
        left = cx - tb / 2
    if not before and ta > right - left:
        right = cx + ta / 2
    xs_b, x = [], left
    for a in adv_b:
        xs_b.append((x, "left"))
        x += a + sp_w
    xs_a, x = [], right
    for a in reversed(adv_a):
        xs_a.append((x, "right"))
        x -= a + sp_w
    return xs_b + xs_a[::-1]


def _baselines(M: Meter, band: tuple[float, float], hero_role: str, hs: int, heroes: list[str], ss: int,
               smalls: list[str]) -> tuple[float, float]:
    """(baseline từ lớn, baseline chữ nhỏ): khối chữ (chữ nhỏ + từ lớn) căn giữa theo chiều dọc trong dải `band` = (trên, dưới)."""
    lo, hi = band
    hero_txt = " ".join(heroes)
    top_h = M.ink_top(hero_role, hs, [hero_txt])
    sb = -top_h - GAP - M.ink_bottom("small", ss, smalls) if smalls else 0.0     # baseline chữ nhỏ khi baseline từ lớn = 0
    top = (sb - M.ink_top("small", ss, smalls)) if smalls else -top_h
    height = M.ink_bottom(hero_role, hs, [hero_txt]) - top
    if height > hi - lo:
        raise ValueError(f"cụm chữ không vừa vùng (cao {height:.0f} > {hi - lo:.0f})")
    base = lo + (hi - lo - height) / 2 - top
    return base, (sb + base if smalls else 0.0)


def _hero_clips(M: Meter, role: str, heroes: list[str], hs: int, y: float, color: str, shadow: bool, times: list[float],
                end: float, fps: float, kin: dict, p: dict, look: dict | None = None, glow: str | None = None,
                cx: float = CX, ov: bool = False) -> list[tuple[str, dict]]:
    """Từ lớn (1 clip căn giữa) hoặc cặp 2 từ cạnh nhau theo advance(); từ thứ hai vào trễ second_hero_delay_frames khung.
    Đã gồm glow (`glow` nhẹ khi look=None; theo kiểu khi có look). Gradient: đo bằng font không tracking (khớp PNG)."""
    args = (fps, kin, look, glow, ov)
    if len(heroes) == 1:
        return _hero_item(M, role, heroes[0], hs, cx, y, "center", color, shadow, times[0], end, *args)
    lo, hi = p["second_hero_delay_frames"]
    grad = look is not None and look["name"] == "gradient"
    f = M.font(role, hs)
    left = cx - (f.getlength(" ".join(heroes)) if grad else M.width(role, hs, " ".join(heroes))) / 2
    x2 = left + (f.getlength(heroes[0] + " ") if grad else M.advance(role, hs, heroes[0] + " "))
    at2 = min(max(times[1], times[0] + lo / fps), times[0] + hi / fps)
    return [it for w, x, at in ((heroes[0], left, times[0]), (heroes[1], x2, at2))
            for it in _hero_item(M, role, w, hs, x, y, "left", color, shadow, at, end, *args)]


def _fit(M: Meter, p: dict, role: str, zone: str, band: tuple[float, float], heroes: list[str], before: list[str],
         after: list[str], span: float) -> tuple[int, int, float, float, list[tuple[float, str]]]:
    """(cỡ hero, cỡ nhỏ, baseline hero, baseline nhỏ, vị trí chữ nhỏ). Tự co cho vừa trước khi báo lỗi: không vừa vùng → hero thu 8 px
    (tối thiểu text.auto_fit_min_hero); chữ nhỏ rộng hơn từ lớn → span_ratio +0,1 (tối đa bề ngang của vùng)."""
    _, _, cx, max_w = ZONES[zone]
    floor, size, text = p.get("auto_fit_min_hero", 120), p["size_hero"], " ".join(heroes)
    while True:
        hs, ss = _sizes(M, {**p, "size_hero": size}, role, text, max_w)
        try:
            hb, sb = _baselines(M, band, role, hs, heroes, ss, before + after)
            half = M.width(role, hs, text) / 2 * span
            return hs, ss, hb, sb, _small_xs(M, ss, before, after, cx - half, cx + half, cx, max_w)
        except ValueError as e:
            wide = max_w / M.width(role, hs, text)
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


def zone_band(zone: str, head_top: float | None = None, chin_y: float | None = None) -> tuple[float, float]:
    """Dải y (trên, dưới) dùng được của vùng: 'top' dừng cách đỉnh đầu ≥ TOP_CLEAR; 'lower' bắt đầu dưới cằm ≥ CHIN_GAP."""
    lo, hi = ZONES[ZONE_ALIAS.get(zone, zone)][:2]
    if zone in ("top", "key") and head_top is not None:
        hi = min(hi, head_top - TOP_CLEAR)
    if zone in ("lower", "cap") and chin_y is not None:
        lo = max(lo, chin_y + CHIN_GAP)
    return lo, hi


def pick_zone(beat_index: int, on_aroll: bool, head_top: float | None, chin_y: float | None = None, prev_zone: str | None = None,
              block_h: float = BLOCK_H, face_side: str | None = None) -> str:
    """Vùng chữ cho nhịp thứ `beat_index`. A-roll: mặc định 'lower' (dưới cằm ≥ 30 px), 'top' chỉ khi khoảng trống trên đầu
    ≥ block_h + 40, 'mid_*' (phía xa mặt) chỉ khi biết face_side 'left' | 'right'; xen kẽ theo nhịp. B-roll: xoay top / lower /
    mid_center. Không trùng `prev_zone` khi còn vùng khác vừa; không vùng nào vừa → ValueError."""
    def fits(z: str) -> bool:
        lo, hi = zone_band(z, head_top if on_aroll else None, chin_y if on_aroll else None)
        return hi - lo >= block_h and not (on_aroll and z == "top" and head_top is None)
    if on_aroll:
        order = ["lower", "top"] + ([{"left": "mid_right", "right": "mid_left"}[face_side]] if face_side else [])
    else:
        order = ["top", "lower", "mid_center"]
    ok = [z for z in order if fits(z)]
    if not ok:
        raise ValueError(f"không vùng nào đủ chỗ cho khối cao {block_h:.0f} px (đỉnh đầu {head_top}, cằm {chin_y})")
    k = beat_index % len(ok)
    rot = ok[k:] + ok[:k]
    return next((z for z in rot if z != prev_zone), rot[0])


MONEY_WORDS = {"tiền", "tỷ", "tỉ", "triệu", "nghìn", "ngàn", "đồng", "usd", "vnd", "đô"}      # luôn là tiền
UNIT_WORDS = {"lần", "phần", "trăm"}                                                           # là số khi đứng sau một số
NUMERALS = {"một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín", "mười", "chục", "trăm"}
NUMBER_COLOR = "gold"                                # tên trong hero_rotation_dark: số / tiền = vàng đặc
GLOW_COLOR = "cyan"                                  # glow nền tối khi người gọi không chỉ định màu (trắng + glow trắng bị nhoè, mất nét)
AUTO_GRADIENT = 1                                    # cặp gradient nền tối của kiểu auto (text.gradients.dark[1], xanh lơ → xanh dương: dễ thấy hơn cặp 0)


def _is_num(w: str | None) -> bool:
    w = (w or "").lower()
    return any(ch.isdigit() or ch in "%$€₫" for ch in w) or w in NUMERALS


def is_number_word(word: str, prev: str | None = None) -> bool:
    """Số hoặc tiền (không vọt 106 %, không glow / gradient): có chữ số, %, ký hiệu tiền, từ tiền (MONEY_WORDS), hoặc từ đơn vị
    (UNIT_WORDS: lần …) đứng ngay sau một số."""
    w = _nfc(word).lower()
    return _is_num(w) and w not in NUMERALS or w in MONEY_WORDS or (w in UNIT_WORDS and _is_num(prev))


def auto_look(prof: dict, on_dark: bool, number: bool, serif: bool, key: bool, has_gfx: bool,
              has_colors: bool = False) -> tuple[str, str | None]:
    """(kiểu, màu từ lớn | None) theo khoảnh khắc: số / tiền → màu nhấn đặc + bóng sâu, không glow; từ cảm xúc (serif) → glow ấm (vàng);
    từ khoá mạnh nhất của cảnh (`key`) → gradient (cần gfx_dir); còn lại glow trên nền tối (màu xoay nếu có `colors`, không thì
    GLOW_COLOR), gradient đậm trên nền sáng."""
    col = prof["text"]["colors"]
    named = lambda n: next(e["color"] for e in col["hero_rotation_dark"] if e.get("name") == n)   # noqa: E731
    gold = named(NUMBER_COLOR)
    if number:
        return "shadow_deep", gold if on_dark else col["accent"]
    if key and has_gfx:
        return "gradient", None
    if serif:
        return ("glow", gold) if on_dark else ("shadow_light", col["accent"])
    if on_dark:
        return "glow", None if has_colors else named(GLOW_COLOR)
    return ("gradient", None) if has_gfx else ("shadow_light", None)


def caption_group(hero, before, after, times, end: float, fps: float = 30, style: str = "sans", on_dark: bool = True,
                  accent: bool = False, zone: str = "top", span_ratio: float | None = None, prof: dict | None = None,
                  color: str | None = None, colors: HeroColors | None = None, looks: HeroLooks | str | None = None,
                  look: str | None = None, gfx_dir=None, key: bool = False, band: tuple[float, float] | None = None
                  ) -> list[tuple[str, dict]]:
    """Một cụm chữ ≤ max_words_per_group từ, đúng 1 từ lớn (hoặc cặp 2 từ) do người gọi chỉ định.
    hero: str | [str, str]; before / after: chữ nhỏ trước / sau từ lớn; times: giây bắt đầu của TỪNG từ theo thứ tự đọc
    (before + hero + after), được giãn ≥ 2 khung giữa hai từ liền nhau; end: giây kết thúc cả cụm; style 'sans' (Inter ExtraBold) |
    'serif' (Playfair Bold Italic); on_dark: nền tối (chữ trắng) hay sáng (chữ đen, nhấn #123CE8 nếu accent);
    zone: 'top' | 'lower' | 'mid_left' | 'mid_right' | 'mid_center' (ZONES; 'key' = top, 'cap' = lower); band: (trên, dưới) thu hẹp dải
    y của vùng (zone_band: cằm / đỉnh đầu); span_ratio: bề ngang chữ nhỏ so với từ lớn (mặc định theo hồ sơ);
    color: màu từ lớn chỉ định tay; colors: HeroColors(prof). Từ lớn có màu (không trắng / đen, nền tối) kèm wonder_glow nhẹ (B3).
    Vào mượt text_motion.kinetic_in cho mọi chữ; từ lớn vọt 106 % trừ số / tiền (is_number_word). Ra / giữ do ensure_motion lo.
    looks: HeroLooks(prof) — kiểu kế tiếp của vòng xoay; hoặc "auto" — chọn theo khoảnh khắc (auto_look: số / tiền = vàng đặc + bóng
    sâu; serif = glow vàng; key=True = gradient, mỗi cảnh chỉ nên gọi key=True một lần; còn lại glow nền tối / gradient đậm nền sáng).
    look: chỉ định tay, thắng looks. Nền sáng: không glow. gradient cần gfx_dir. Không looks / look: hành vi cũ."""
    prof = prof or sp.load(name="minimal-edu")
    p = prof["text"]
    zone = ZONE_ALIAS.get(zone, zone)
    heroes = [_nfc(hero)] if isinstance(hero, str) else [_nfc(w) for w in hero]
    before, after = [_nfc(w) for w in before], [_nfc(w) for w in after]
    nb, nh = len(before), len(heroes)
    if not 1 <= nh <= 2 or style not in ("sans", "serif") or zone not in ZONES:
        raise ValueError(f"hero 1–2 từ; style 'sans'|'serif'; zone một trong {sorted(ZONES)}")
    if nb + nh + len(after) > p["max_words_per_group"] or len(times) != nb + nh + len(after):
        raise ValueError(f"cụm ≤ {p['max_words_per_group']} từ và `times` phải có đúng một mốc cho mỗi từ")
    M, role, kin = Meter(prof), "hero_sans" if style == "sans" else "hero_serif", kinetic_params(prof)
    times = stagger_times(times, fps, kin)
    base_c, _, shadow = _palette(p, on_dark, accent)
    words, stops = before + heroes, None
    number = any(is_number_word(w, words[nb + i - 1] if nb + i else None) for i, w in enumerate(heroes))
    if looks == "auto":
        auto_name, auto_c = auto_look(prof, on_dark, number, style == "serif", key, gfx_dir is not None, colors is not None)
        look, color, looks = look or auto_name, color or auto_c, None
        stops = list(p["gradients"]["dark" if on_dark else "light"][AUTO_GRADIENT if on_dark else 0]) if look == "gradient" else None
    hero_c, glow = _hero_color(prof, p, on_dark, accent, color, colors)
    band = band or zone_band(zone)
    cx = ZONES[zone][2]
    hs, ss, hb, sb, xs = _fit(M, p, role, zone, band, heroes, before, after, p["span_ratio"] if span_ratio is None else span_ratio)
    smalls = [("text_low", _clip(M, "small", w, ss, x, sb, al, base_c, shadow, t, end, fps, kin))
              for w, t, (x, al) in zip(before + after, times[:nb] + times[nb + nh:], xs)]
    lk = _pick_look(prof, on_dark, looks, look, hero_c, glow, gfx_dir, stops)
    hero_items = _hero_clips(M, role, heroes, hs, hb, hero_c, shadow, times[nb:nb + nh], end, fps, kin, p, lk, glow, cx, not number)
    return smalls[:nb] + hero_items + smalls[nb:]


def _quote_layout(M: Meter, p: dict, lines: list[str], extra: str | None) -> tuple[int, float, float]:
    """(cỡ chữ, bước dòng, baseline dòng đầu): cỡ thu cho vừa MAX_W và vừa chiều cao khung từ khoá B8; khối căn giữa khung."""
    lo, hi = ZONES["top"][:2]
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
    lo, hi = ZONES["top"][:2]
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
                t_last: float, kin: dict, hero_color: str | None = None,
                glow: str | None = None, look: dict | None = None) -> list[tuple[str, dict]]:
    """quote_text khi người gọi chỉ định dòng chính: dòng đó cỡ hero căn giữa, các dòng khác cỡ nhỏ căn trái, dấu “ ” cỡ hero × 0.6.
    hero_color / glow: màu (và glow nhẹ) của dòng chính — kể cả từ serif cuối nếu nằm trên dòng đó; các dòng khác và dấu ngoặc vẫn trắng.
    look: kiểu chiều sâu (_pick_look) chỉ cho dòng chính."""
    ents = _quote_entries(lines, last_word_serif, hero_index)
    hs, ss, ys = _quote_hero_layout(M, p, ents)
    left, right, white, mk = CX - MAX_W / 2, CX + MAX_W / 2, p["colors"]["on_dark"], round(hs * QUOTE_MARK_RATIO)
    q_w = M.advance("hero_serif", mk, CLOSE_Q)
    sizes = [hs if h else ss for _, _, h in ents]
    top_of = lambda k: ys[k] - M.ink_top(ents[k][0], sizes[k], [ents[k][1]])          # noqa: E731  đỉnh mực của dòng k
    q_ink = M.ink_top("hero_serif", mk, [OPEN_Q])
    items = [("text_low", _clip(M, "hero_serif", OPEN_Q, mk, QUOTE_LEFT_PCT * 1080, top_of(0) + q_ink, "left", white, True, at, end, fps, kin))]
    last = len(ents) - 1
    for k, ((role, text, hero), z, y) in enumerate(zip(ents, sizes, ys)):
        if role == "hero_serif":
            x, al, t0 = right - q_w, "right", t_last
        else:
            x, al, t0 = (CX, "center", at) if hero else (left, "left", at)
        lane = "text" if hero or role == "hero_serif" else "text_low"
        color = hero_color if hero and hero_color else white
        if hero and look:
            items += _hero_item(M, role, text, z, x, y, al, color, True, t0, end, fps, kin, look, glow, True)
            continue
        c = _clip(M, role, text, z, x, y, al, color, True, t0, end, fps, kin, hero or role == "hero_serif")
        items += _with_glow([(lane, c)], glow if hero else None, fps)
    if ents[last][0] == "hero_serif":
        qx = right - q_w
    else:
        w = M.advance(ents[last][0], sizes[last], ents[last][1])
        qx = (CX + w / 2) if ents[last][2] else left + w
    items.append(("text_low", _clip(M, "hero_serif", CLOSE_Q, mk, qx, top_of(last) + q_ink, "left", white, True, t_last, end, fps, kin)))
    return items


def quote_text(lines: list[str], last_word_serif: bool, at: float, dur: float, fps: float = 30, last_at: float | None = None,
               prof: dict | None = None, hero_index: int | None = None, hero_color: str | None = None,
               looks: HeroLooks | None = None, look: str | None = None, gfx_dir=None) -> list[tuple[str, dict]]:
    """Chữ của quote card (nền do fx_gfx dựng): dấu “ căn trái x ≈ 6 % ở đầu dòng 1, các dòng sans trắng căn trái vào vùng chữ B8
    (x 140–940), từ cuối của dòng cuối tách ra serif italic trắng căn phải (last_word_serif) kèm dấu ” cạnh nó.
    at / dur: thời gian cả khối (giây); last_at: lúc từ cuối vào (mặc định at + second_hero_delay_frames[0] khung).
    hero_index (người gọi chỉ định, không đoán): dòng đó cỡ text.size_hero (Inter ExtraBold) căn giữa, các dòng khác cỡ text.size_small,
    dấu “ ” cỡ hero × 0.6 (Playfair). None = mọi dòng cùng một cỡ (dấu ngoặc cỡ size_small).
    hero_color (cần hero_index): màu dòng chính; có màu (không trắng) → glow nhẹ như caption_group.
    looks / look / gfx_dir (cần hero_index): kiểu chiều sâu của dòng chính như caption_group (nền thẻ luôn tối)."""
    prof = prof or sp.load(name="minimal-edu")
    p = prof["text"]
    lines = [_nfc(ln) for ln in lines]
    if hero_index is not None and not 0 <= hero_index < len(lines):
        raise ValueError(f"hero_index {hero_index} ngoài phạm vi {len(lines)} dòng")
    if (hero_color or looks or look) and hero_index is None:
        raise ValueError("hero_color / looks / look cần hero_index (dòng chính do người gọi chỉ định)")
    M, kin = Meter(prof), kinetic_params(prof)
    t_last = at + p["second_hero_delay_frames"][0] / fps if last_at is None else last_at
    if hero_index is not None:
        glow = glow_for(prof, hero_color) if hero_color else None
        lk = _pick_look(prof, True, looks, look, hero_color or p["colors"]["on_dark"], glow, gfx_dir)
        return _quote_hero(M, p, lines, last_word_serif, hero_index, at, at + dur, fps, t_last, kin, hero_color, glow, lk)
    tail = None
    if last_word_serif:
        head, _, tail = lines[-1].rpartition(" ")
        lines = lines[:-1] + ([head] if head else [])
    size, pitch, y0 = _quote_layout(M, p, lines, tail)
    left, right, end, white = (CX - MAX_W / 2), (CX + MAX_W / 2), at + dur, p["colors"]["on_dark"]
    mk = p["size_small"]
    q_open = _clip(M, "hero_serif", OPEN_Q, mk, QUOTE_LEFT_PCT * 1080, y0 - M.ink_top("hero_sans", size, lines) + M.ink_top("hero_serif", mk, [OPEN_Q]),
                   "left", white, True, at, end, fps, kin)
    items = [("text_low", q_open)]
    items += [("text", _clip(M, "hero_sans", ln, size, left, y0 + i * pitch, "left", white, True, at, end, fps, kin))
              for i, ln in enumerate(lines)]
    if tail:
        q_w = M.advance("hero_serif", mk, CLOSE_Q)
        items.append(("text", _clip(M, "hero_serif", tail, size, right - q_w, y0 + len(lines) * pitch, "right", white, True, t_last, end, fps, kin)))
        qx, qy = right - q_w, y0 + len(lines) * pitch
    else:
        qx, qy = left + M.advance("hero_sans", size, lines[-1]), y0 + (len(lines) - 1) * pitch
    items.append(("text_low", _clip(M, "hero_serif", CLOSE_Q, mk, qx, qy, "left", white, True, t_last, end, fps, kin)))
    return items
