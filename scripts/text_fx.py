"""Thư viện 24 hiệu ứng chữ kiểu @__dviet → clip cho timeline spec của craft-handoff (FilmCraft).

Dùng:
    import sys; sys.path.insert(0, "<skill>/scripts")
    from text_fx import FX
    fx = FX(gfx_dir=work / "gfx", accent="#F3C60F")
    fx.pair("có chủ đích", "để dựng", at=1.2, dur=1.4)
    fx.word_captions([("mỗi", 3.0), ("vết", 3.3), ("cắt", 3.5)], end=4.6)
    spec["tracks"] = [v1_aroll_track, *fx.tracks(), *audio_tracks]   # tracks() xếp lớp sẵn, không chồng clip
    fx.cues  # gợi ý SFX: [{"t", "kind", "why"}] — tự chọn file và đặt (kênh mẫu không gắn SFX cho mọi chữ)

Mọi thời gian tính bằng giây trên timeline; toạ độ trên khung 1080×1920. Mỗi hàm hiệu ứng trả về list clip đã thêm.
Trạng thái kiểm thật trên FilmCraft ghi ở references/text-fx.md (skill master-video-edit).
"""
from __future__ import annotations

import math
import re
import unicodedata
from pathlib import Path

from PIL import ImageFont

import fx_gfx as G

FONTS_DIR = Path.home() / ".local/share/fonts"
# vai trò → (family, style trong FilmCraft, file để đo)
FONTS = {
    "cap": ("SF Pro Display", "Medium", FONTS_DIR / "apple-fonts/SF-Pro-Display-Medium.otf"),
    "semi": ("SF Pro Display", "Semibold", FONTS_DIR / "apple-fonts/SF-Pro-Display-Semibold.otf"),
    "bold": ("SF Pro Display", "Bold", FONTS_DIR / "apple-fonts/SF-Pro-Display-Bold.otf"),
    "sans": ("SF Pro Display", "Heavy", FONTS_DIR / "apple-fonts/SF-Pro-Display-Heavy.otf"),
    "sans_it": ("SF Pro Display", "Heavy Italic", FONTS_DIR / "apple-fonts/SF-Pro-Display-HeavyItalic.otf"),
    "serif": ("Playfair Display", "Bold Italic", FONTS_DIR / "PlayfairDisplay-BoldItalic.ttf"),
    "serif_reg": ("Playfair Display", "Regular", FONTS_DIR / "PlayfairDisplay-Variable.ttf"),
    "script": ("Great Vibes", "Regular", FONTS_DIR / "GreatVibes-Regular.ttf"),
    "num": ("Montserrat", "Black", FONTS_DIR / "Montserrat_Static/Montserrat-Black.otf"),
    "condensed": ("Bebas Neue", "Regular", FONTS_DIR / "BebasNeue-Regular.ttf"),
}
TRACKING = {"cap": -20, "semi": -20, "bold": -30, "sans": -40, "sans_it": -35, "serif": -10, "serif_reg": 0,
            "script": 0, "num": -40, "condensed": 10}
WHITE = "#FFFFFF"
SHADOW = {"color": "#000000", "opacity": 60, "blur": 10, "distance": 4}
STRONG_SHADOW = {"color": "#000000", "opacity": 85, "blur": 14, "distance": 3}   # phụ đề trên áo/nền sáng (THCN 03)
GLOW = {"effect": "wonder_glow", "params": {"threshold": 40, "radius": 22, "intensity": 85}}
# lớp từ dưới lên: (tên lane, loại track)
LANES = [("gfx_under", "video"), ("card", "video"), ("text_behind", "text"), ("matte", "video"),
         ("text_low", "text"), ("text", "text"), ("text_img", "video"), ("text_top", "text"), ("gfx_over", "video")]


_COMMA = re.compile(r"(?<!\d),|,(?!\d)")


def no_commas(s: str) -> str:
    """Luật B13 (người dùng chốt 2026-11-10): chữ hiện trên hình không có dấu phẩy; dấu phẩy thập phân giữa hai số (2,5) giữ nguyên."""
    return _COMMA.sub("", s)


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", no_commas(s))   # mọi chữ hiện trên hình (đo bề rộng, clip chữ, PNG) đi qua đây


def cap_first(s: str) -> str:
    """Viết hoa chữ cái đầu dòng (luật người dùng), kể cả dòng bắt đầu bằng số."""
    s = nfc(s)
    i = next((k for k, ch in enumerate(s) if ch.isalpha()), None)
    return s if i is None else s[:i] + s[i].upper() + s[i + 1:]


KEY_ZONE_TOP = 240       # mép trên khung từ khoá (2 vùng chữ, references/rules.md mục 2)
HEAD_TOP = 380           # đỉnh đầu người nói (px, khung 1080x1920): HeyGen ~ 380; quay thật theo Rule 5 ~ 640
HEAD_HALF_W = 215        # nửa bề rộng đầu (tóc + mặt) ở zoom 100–110 %
HOOK_HIDE_MAX = 0.20     # chữ hook sau đầu: tối đa 20 % bề rộng dòng bị đầu che (hơn → khó đọc trọn câu)
HOOK_MIN_SIZE = 100      # cỡ nhỏ nhất khi thu / tách dòng hook


class FX:
    def __init__(self, gfx_dir: Path, fps: int = 30, accent: str = "#F3C60F", key_y: int = 500, cap_y: int = 1400,
                 max_w: int = 800, cap_case: bool = True):
        # 2 vùng chữ người dùng chốt 2026-11-03 (references/rules.md mục 2): khung trên y 240–680 cho từ khoá,
        # khung dưới y 1290–1480 cho phụ đề, rộng ≤ 800 px căn giữa — tránh giao diện TikTok bên phải và ở đáy
        self.gfx_dir, self.fps, self.accent = Path(gfx_dir), fps, accent
        self.key_y, self.cap_y, self.max_w, self.cap_case = key_y, cap_y, max_w, cap_case
        self.items: list[tuple[str, dict]] = []
        self.cues: list[dict] = []
        self._fonts: dict = {}
        self._n = 0

    # ---------- đo chữ ----------
    def font(self, role: str, size: int):
        k = (role, size)
        if k not in self._fonts:
            self._fonts[k] = ImageFont.truetype(str(FONTS[role][2]), size)
        return self._fonts[k]

    def width(self, role: str, size: int, text: str) -> float:
        box = self.font(role, size).getbbox(nfc(text), anchor="ls")
        return box[2] - box[0] + TRACKING[role] / 1000 * size * max(0, len(text) - 1)

    def advance(self, role: str, size: int, text: str) -> float:
        return self.font(role, size).getlength(nfc(text)) + TRACKING[role] / 1000 * size * len(text)

    def ink_top(self, role: str, size: int, text: str) -> float:
        """Khoảng từ baseline lên đỉnh mực (gồm dấu tiếng Việt), số dương."""
        return -self.font(role, size).getbbox(nfc(text), anchor="ls")[1]

    def ink_bottom(self, role: str, size: int, text: str) -> float:
        """Khoảng từ baseline xuống đáy mực (dấu nặng, chân chữ g/y), số dương."""
        return self.font(role, size).getbbox(nfc(text), anchor="ls")[3]

    def mark_below(self, role: str, size: int, text: str) -> float:
        """Đáy mực của các chữ mang dấu nặng (ạ, ệ, ự…); 0 nếu không có. Chân chữ g/p/y không tính."""
        marks = [ch for ch in nfc(text) if "\u0323" in unicodedata.normalize("NFD", ch)]
        return max((self.ink_bottom(role, size, ch) for ch in marks), default=0)

    def fit(self, role: str, size: int, text: str, max_w: float | None = None) -> int:
        lim = max_w or self.max_w
        while size > 40 and self.width(role, size, text) > lim:
            size -= 2
        return size

    @staticmethod
    def hidden_ratio(width: float, bottom: float, head_top: int = HEAD_TOP, half_w: int = HEAD_HALF_W) -> float:
        """Phần bề rộng một dòng chữ bị đầu che (0–1). Đầu = mũ bán nguyệt đỉnh ở `head_top`, nửa rộng `half_w`;
        đáy dòng chữ ở `bottom` — càng chui sâu vào đầu càng bị che rộng; dòng nằm trên đỉnh đầu thì không bị che."""
        d = min(bottom - head_top, half_w)
        if d <= 0:
            return 0.0
        hw = half_w * math.sqrt(1 - (1 - d / half_w) ** 2)
        return min(1.0, 2 * hw / max(width, 1.0))

    def fit_hook(self, key: str, size: int = 190, y: int = 420, lead: bool = True, head_top: int = HEAD_TOP,
                 half_w: int = HEAD_HALF_W, hide_max: float = HOOK_HIDE_MAX, min_size: int = HOOK_MIN_SIZE) -> dict:
        """Xếp chữ chính HOOK (SAU đầu người) sao cho đọc được trọn câu: giữ cỡ / vị trí đã cho nếu đầu che ≤ `hide_max`
        bề rộng; không thì NÂNG lên (tới mép vùng chữ), rồi TÁCH 2 dòng, rồi THU cỡ (≥ min_size) — thử lần lượt từ cỡ lớn xuống.
        Hết cách → để chữ đặt TRƯỚC đầu (matte=False, đọc trọn, đè mặt) thay vì bị che.
        Trả {"lines": [(chữ, cỡ, baseline y)], "matte": cần Track Matte hay không, "hidden": tỉ lệ che tệ nhất, "note": giải thích}.
        keyword_tpl(lead, dòng, script, y=baseline, size=cỡ) dựng từng dòng (từ dẫn ở dòng 1, chữ viết tay ở dòng cuối)."""
        key = no_commas(key)
        words = key.split()
        splits: list[list[str]] = [[key]]
        if len(words) >= 2:                                        # tách 2 dòng cân nhất theo bề rộng
            k = min(range(1, len(words)), key=lambda i: abs(self.width("mx_heavy", 100, " ".join(words[:i]))
                                                          - self.width("mx_heavy", 100, " ".join(words[i:]))))
            splits.append([" ".join(words[:k]), " ".join(words[k:])])

        def measure(lines: list[str], sz: int, y0: int) -> tuple[float, int]:
            gap = round(sz * 1.05)
            worst = max(self.hidden_ratio(self.width("mx_heavy", sz, t), y0 + i * gap + self.ink_bottom("mx_heavy", sz, t),
                                          head_top, half_w) for i, t in enumerate(lines))
            return worst, gap

        def top_of(lines: list[str], sz: int, y0: int) -> float:
            lead_h = round(0.36 * sz * 0.8) + 16 if lead else 0
            return y0 - self.ink_top("mx_heavy", sz, lines[0]) - lead_h

        floor = min(KEY_ZONE_TOP, top_of(splits[0], self.fit("mx_heavy", size, key), y))   # không bắt hook mặc định tụt khỏi vùng chữ
        for sz in range(size, min_size - 1, -10):
            for lines in splits:
                if any(self.fit("mx_heavy", sz, t) < sz for t in lines):       # dòng rộng quá max_w ở cỡ này → thử cỡ / cách tách khác
                    continue
                for y0 in range(y, int(floor), -10):
                    if top_of(lines, sz, y0) < floor:
                        break
                    hidden, gap = measure(lines, sz, y0)
                    if hidden <= hide_max + 1e-9:
                        moved = ("nâng lên " + str(y - y0) + " px, ") if y0 != y else ""
                        how = (f"{len(lines)} dòng, " if len(lines) > 1 else "") + (f"cỡ {sz}" if sz != size else "giữ cỡ")
                        return {"lines": [(t, sz, y0 + i * gap) for i, t in enumerate(lines)], "matte": hidden > 0,
                                "hidden": round(hidden, 2), "note": f"{moved}{how}; đầu che {hidden:.0%} bề rộng"}
        one = self.fit("mx_heavy", size, key)                      # hết chỗ sau đầu: đặt TRƯỚC đầu — 1 dòng nếu còn đủ to, không thì 2 dòng
        lines, sz = [key], one
        if one < min_size + 10 and len(splits) > 1:
            lines = splits[1]
            sz = min(min(self.fit("mx_heavy", size, t) for t in lines), 150)
        hidden, gap = measure(lines, sz, y)
        note = (f"không còn chỗ sau đầu (sẽ bị che {hidden:.0%}) → đặt TRƯỚC đầu để đọc trọn câu"
                + (f"; chữ dài ({len(key)} ký tự), nên rút ngắn" if sz < min_size else ""))
        return {"lines": [(t, sz, y + i * gap) for i, t in enumerate(lines)], "matte": False, "hidden": round(hidden, 2), "note": note}

    def snap(self, t: float) -> float:
        return round(t * self.fps) / self.fps

    def _name(self, s: str) -> str:
        self._n += 1
        return f"{s} #{self._n}"

    # ---------- clip cơ bản ----------
    def text(self, text: str, at: float, dur: float, role: str = "sans", size: int = 120, x: float = 540,
             y: float | None = None, align: str = "center", color: str = WHITE, lane: str = "text",
             case: bool | None = None, shadow: dict | None = SHADOW, name: str | None = None) -> dict:
        """Một clip chữ (graphic_text). `y` = baseline dòng đầu. Tự thu cỡ cho vừa max_w khi căn giữa."""
        if (self.cap_case if case is None else case) and role not in ("num",):
            text = cap_first(text)
        if align == "center":
            size = self.fit(role, size, text)
        at, end = self.snap(at), self.snap(at + dur)
        fam, style, _ = FONTS[role]
        c = {"text": nfc(text), "at": at, "dur": end - at, "font": fam, "style": style, "size": size, "color": color,
             "align": align, "position": [round(x), round(self.key_y if y is None else y)], "tracking": TRACKING[role],
             "name": name or self._name(f"Chữ · {text[:24]}")}
        if shadow:
            c["shadow"] = dict(shadow)
        c["_role"] = role
        self.items.append((lane, c))
        return c

    def image(self, src: str, at: float, dur: float, lane: str = "gfx_over", name: str = "VFX") -> dict:
        at, end = self.snap(at), self.snap(at + dur)
        c = {"src": src, "at": at, "dur": end - at, "name": self._name(name)}
        self.items.append((lane, c))
        return c

    def center_y(self, c: dict) -> int:
        """Tâm thị giác của khối chữ (để phóng/xoay tại chỗ)."""
        return round(c["position"][1] - c["size"] * 0.36)

    def _fx(self, c: dict, effect: str, params: dict) -> dict:
        c.setdefault("effects", []).append({"effect": effect, "params": params})
        return c

    def _k(self, c: dict, t: float) -> float:
        """Nén mốc keyframe vào trong clip ngắn."""
        return min(t, max(1 / self.fps, c["dur"] - 1 / self.fps))

    # ---------- kiểu vào / ra (sửa clip tại chỗ, trả lại clip) ----------
    def blur_in(self, c: dict, d: float = 0.2, blur: float = 24) -> dict:
        """Blur-in chuẩn kênh: 0,17–0,25 s, opacity đủ ở 60% thời lượng."""
        c["opacity"] = [[0, 0], [self._k(c, d * 0.6), 100]]
        return self._fx(c, "gaussian_blur", {"blurriness": [[0, blur], [self._k(c, d), 0, "easeIn"]]})

    def grey_in(self, c: dict, d: float = 0.2, blur: float = 14) -> dict:
        """Hiện xám ~50% trong 2–3 khung rồi sáng lên trắng (fade xám → trắng)."""
        k = min(1.0, (c["dur"] - 1 / self.fps) / d)
        c["opacity"] = [[0, 0], [1 / self.fps * k, 50], [0.5 * d * k, 55], [d * k, 100, "easeIn"]]
        return self._fx(c, "gaussian_blur", {"blurriness": [[0, blur], [0.85 * d * k, 0, "easeIn"]]})

    def color_in(self, c: dict, from_color: str = "#A855F7", d: float = 0.4) -> dict:
        """Vào bằng màu (tím/hồng mờ) rồi chuyển trắng."""
        final = c["color"]
        c["color"] = [[0, from_color], [self._k(c, d), final, "easeIn"]]
        c["opacity"] = [[0, 40], [self._k(c, d * 0.6), 100]]
        return self._fx(c, "gaussian_blur", {"blurriness": [[0, 10], [self._k(c, d * 0.8), 0]]})

    def nudge(self, c: dict, frm: float = 95) -> dict:
        cy = self.center_y(c)
        c["motion"] = {"anchor": [c["position"][0], cy], "position": [c["position"][0], cy],
                       "scale": [[0, frm], [self._k(c, 0.22), 100, "easeIn"]]}
        return c

    def slide_up(self, c: dict, dy: float = 270, d: float = 0.42) -> dict:
        """"Máy phát nhạc 3": trượt từ thấp hơn ~14% khung lên, ease-out, nhoè dọc, sáng nhẹ ở cuối."""
        c["motion"] = {"position": [[0, [540, 960 + dy]], [self._k(c, d), [540, 960], "easeIn"]]}
        c["opacity"] = [[0, 30], [self._k(c, d * 0.6), 100]]
        self._fx(c, "directional_blur", {"direction": 0, "length": [[0, 40], [self._k(c, d), 0, "easeIn"]]})
        return self._fx(c, "gaussian_blur", {"blurriness": [[0, 12], [self._k(c, d * 0.8), 0, "easeIn"]]})

    def slide_down(self, c: dict, dy: float = 220, d: float = 0.33) -> dict:
        c["motion"] = {"position": [[0, [540, 960 - dy]], [self._k(c, d), [540, 960], "easeIn"]]}
        c["opacity"] = [[0, 40], [self._k(c, 0.1), 100]]
        return self._fx(c, "directional_blur", {"direction": 0, "length": [[0, 80], [self._k(c, d), 0, "easeIn"]]})

    def script_in(self, c: dict, d: float = 0.3, dx: float = 70, rot: float = -6) -> dict:
        x, cy = c["position"][0], self.center_y(c)
        c["motion"] = {"anchor": [x, cy], "rotation": rot, "position": [[0, [x + dx, cy]], [self._k(c, d), [x, cy], "easeIn"]]}
        c["opacity"] = [[0, 0], [self._k(c, d * 0.5), 100]]
        return self._fx(c, "gaussian_blur", {"blurriness": [[0, 30], [self._k(c, d), 0, "easeIn"]]})

    def glow(self, c: dict, ramp: float | None = None, intensity: float = 85) -> dict:
        p = dict(GLOW["params"], intensity=intensity)
        if ramp:
            p["intensity"] = [[0, 0], [self._k(c, ramp), intensity * 1.4, "easeIn"]]
        return self._fx(c, "wonder_glow", p)

    def flip3d_in(self, c: dict, d: float = 0.36) -> dict:
        c["opacity"] = [[0, 0], [self._k(c, 0.08), 100]]
        return self._fx(c, "rotate_3d", {"rot_x": [[0, -85], [self._k(c, d), 0, "easeIn"]], "perspective": 60})

    def whip_out(self, c: dict, d: float = 0.24) -> dict:
        x, cy = c["position"][0], self.center_y(c)
        t0 = max(0, c["dur"] - d)
        c["motion"] = {"anchor": [x, cy], "position": [[t0, [x, cy], "easeOut"], [c["dur"], [x - 1300, cy]]]}
        return self._fx(c, "directional_blur", {"direction": 90, "length": [[t0, 0], [c["dur"], 80]]})

    # ---------- B1–B24 ----------
    def pair(self, big: str, small: str, at: float, dur: float, big_role: str = "serif", color: str | None = None,
             size: int = 150, small_size: int = 48, below: str | None = None, y: int | None = None, glow: bool = True) -> list:
        """B1 Cặp lớn–nhỏ: chữ nhỏ vào trước 0,08 s (fade), chữ lớn blur-in + trượt xuống 0,25 s, ra cắt cứng."""
        y = y or self.key_y
        col = color or (self.accent if big_role in ("serif", "script") else WHITE)
        b = self.text(big, at + 0.08, dur - 0.08, big_role, size, y=y, color=col)
        self.blur_in(b, 0.25, 30)
        b["motion"] = {"position": [[0, [540, 950]], [self._k(b, 0.25), [540, 960], "easeIn"]]}
        if glow and col != WHITE:
            self.glow(b)
        bw = self.width(big_role, b["size"], b["text"])
        # chữ nhỏ nằm trên đỉnh mực của chữ lớn (dấu chồng như "ẵ", "Ầ" cao hơn 0,78 cỡ chữ → không được đè dấu)
        sy = min(y - b["size"] * 0.78, y - self.ink_top(big_role, b["size"], b["text"]) - 10)
        s = self.text(small, at, dur, "cap", small_size, x=540 - bw / 2 + 10, y=sy, align="left", lane="text_low")
        s["opacity"] = [[0, 0], [0.1, 100]]
        out = [b, s]
        if below:
            s2 = self.text(below, at + 0.3, dur - 0.3, "cap", small_size, x=540 + bw / 2 - 10, y=y + small_size * 1.25,
                           align="right", lane="text_low")
            s2["opacity"] = [[0, 0], [0.1, 100]]
            out.append(s2)
        self.cues.append({"t": b["at"], "kind": "nhịp nhạc (snare) hoặc không SFX", "why": "chữ lớn vào"})
        return out

    def swap_big(self, small: str, bigs: list[tuple[str, float]], end: float, role: str = "sans", size: int = 110,
                 y: int | None = None) -> list:
        """B2 Từ lớn thay liên tục trên chữ nhỏ đứng yên; đổi bằng cắt cứng + fade 0,1 s."""
        y = y or self.key_y
        out = [self.text(small, bigs[0][1], end - bigs[0][1], "semi", 56, y=y + 70, lane="text_low")]
        for i, (w, t) in enumerate(bigs):
            e = bigs[i + 1][1] if i + 1 < len(bigs) else end
            c = self.text(w, t, e - t, role, size, y=y)
            c["opacity"] = [[0, 0], [self._k(c, 0.1), 100]]
            out.append(c)
        return out

    def stack3(self, top: str, mid: str, low: str, at: float, dur: float, y: int | None = None, readable: bool = False) -> list:
        """B3 Chồng 3 tầng (serif nhỏ / sans Heavy rất to / serif nghiêng màu nhấn), blur-in lệch 0,08 s.
        readable=True → B4: đáy chữ to mờ dần (crop + feather) để tầng nghiêng đọc rõ."""
        auto = y is None
        y = y or self.key_y
        mid_t = cap_first(mid) if self.cap_case else mid
        below = self.mark_below("sans", self.fit("sans", 165, mid_t), mid_t)
        lo_off = 62                                     # tầng nghiêng đè chân chữ to (kiểu kênh)
        if below:                                       # chữ to có dấu nặng: tầng nghiêng xuống dưới dấu, nâng cả khối
            lo_off = max(62, round(below + self.ink_top("serif", 95, cap_first(low) if self.cap_case else low) + 6))
            y -= lo_off - 62                            # đáy khối giữ chỗ cũ, không lấn xuống mặt
        if auto:                                        # tầng trên không lòi khỏi khung từ khoá (khối bị nâng vì dấu nặng)
            size, top_t = self.fit("sans", 165, mid_t), cap_first(top) if self.cap_case else top
            top_ink = min(y - size * 0.78, y - self.ink_top("sans", size, mid_t) - 8) - self.ink_top("serif_reg", 60, top_t)
            y += max(0, round(KEY_ZONE_TOP + 10 - top_ink))
        m = self.text(mid, at + 0.08, dur - 0.08, "sans", 165, y=y)
        mw = self.width("sans", m["size"], m["text"])
        top_y = min(y - m["size"] * 0.78, y - self.ink_top("sans", m["size"], m["text"]) - 8)
        t = self.text(top, at, dur, "serif_reg", 60, x=540 - mw / 2, y=top_y, align="left", lane="text_low")
        lo = self.text(low, at + 0.16, dur - 0.16, "serif", 95, x=540 + mw / 2, y=y + lo_off, align="right", color=self.accent,
                       lane="text_top")
        for c in (t, m, lo):
            self.blur_in(c, 0.25, 30)
        if readable:                                    # cắt dưới chân chữ to + feather dài; luôn chừa dấu nặng
            cut = round((1920 - (y + max(m["size"] * 0.16, below + 6))) / 1920 * 100, 1)
            self._fx(m, "crop", {"bottom": cut, "feather": 80})
        return [t, m, lo]

    def script_accent(self, word: str, at: float, dur: float, over: dict | None = None, size: int = 96,
                      color: str = WHITE, glow: bool = True, dy: int = 0) -> dict:
        """B5 Chữ viết tay phát sáng chéo trên-phải từ khoá `over`, chỉ chạm góc (không đè dấu)."""
        sw = self.width("script", size, word)
        if over:
            ow = self.width(over["_role"], over["size"], over["text"])
            x = min(1040 - sw / 2, over["position"][0] + ow / 2 - sw / 2 + 40)
            y = over["position"][1] - self.ink_top(over["_role"], over["size"], over["text"]) - 8 + dy
        else:
            x, y = 560, self.key_y + dy
        c = self.text(word, at, dur, "script", size, x=x, y=y, color=color, lane="text_top", case=False)
        self.script_in(c)
        if glow:
            self.glow(c)
        self.cues.append({"t": c["at"] + 0.04, "kind": "lấp lánh nhỏ (tuỳ chọn)", "why": "chữ viết tay phát sáng"})
        return c

    def script_swap(self, small: str, words: list[tuple[str, float]], end: float, size: int = 110, y: int | None = None) -> list:
        """B6 Từ viết tay thay nhau dưới chữ nhỏ đứng yên; từ cũ nhoè ra, từ mới blur-in, chồng 0,3 s."""
        y = y or self.key_y
        out = [self.text(small, words[0][1], end - words[0][1], "semi", 54, y=y - size * 0.75, lane="text_low")]
        for i, (w, t) in enumerate(words):
            e = (words[i + 1][1] + 0.3) if i + 1 < len(words) else end
            c = self.text(w, t, e - t, "script", size, y=y, lane="text_top" if i % 2 else "text", case=False)
            self.blur_in(c, 0.25, 26)
            if i + 1 < len(words):
                c["opacity"] = c["opacity"] + [[c["dur"] - 0.3, 100], [c["dur"], 0]]
            out.append(c)
        return out

    def number_hook(self, num: str, word: str, at: float, dur: float, small_words: list[tuple[str, float]] = (),
                    bookmark_at: float | None = None, y: int | None = None) -> list:
        """B7 Số khổng lồ màu nhấn + từ trắng Heavy Italic; dòng nhỏ từng từ; bookmark xám → màu nhấn khi bấm."""
        y = y or self.key_y
        nsz, wsz = 230, 110
        nw, ww = self.width("num", nsz, num), self.width("sans_it", wsz, word)
        x0 = 540 - (nw + 20 + ww) / 2
        n = self.text(num, at, dur, "num", nsz, x=x0, y=y + 40, align="left", color=self.accent)
        w = self.text(word, at + 0.05, dur - 0.05, "sans_it", wsz, x=x0 + nw + 20, y=y + 10, align="left")
        for c in (n, w):
            self.blur_in(c, 0.28, 24)
            self.nudge(c, 92)
        out = [n, w]
        x = x0 + nw + 24
        for word_, t in small_words:
            s = self.text(word_, t, at + dur - t, "cap", 46, x=x, y=y + 80, align="left", lane="text_low", case=False)
            s["opacity"] = [[0, 0], [self._k(s, 0.07), 100]]
            x += self.advance("cap", 46, word_ + " ")
            out.append(s)
        if bookmark_at is not None:
            bx, by = round(x0 + nw + 20 + ww + 30), round(y - 80)
            g = G.bookmark(self.gfx_dir, "bookmark_xam", bx, by, 70, "#888888", cursor=True)
            gy = G.bookmark(self.gfx_dir, "bookmark_nhan", bx, by, 70, self.accent, cursor=True)
            self.image(g, at + 0.2, bookmark_at - at - 0.2, name="Bookmark xám")
            self.image(gy, bookmark_at, at + dur - bookmark_at, name="Bookmark màu nhấn")
            self.cues.append({"t": bookmark_at, "kind": "click chuột", "why": "con trỏ bấm bookmark"})
        return out

    def slide_up_text(self, text: str, at: float, dur: float, role: str = "sans", size: int = 125, y: int | None = None,
                      color: str = WHITE) -> dict:
        """B8 Chữ trượt lên mượt (tương đương CapCut "Máy phát nhạc 3", tạo xước = 0)."""
        c = self.text(text, at, dur, role, size, y=y, color=color)
        self.slide_up(c)
        self.glow(c, intensity=40)
        self.cues.append({"t": c["at"] + 0.1, "kind": "whoosh ngắn (tuỳ chọn)", "why": "chữ trượt vào"})
        return c

    def swing3d(self, text: str, at: float, dur: float, size: int = 125, y: int | None = None, period: float = 1.6) -> dict:
        """B9 Giả 3D: xoay trục Y qua lại, có phối cảnh + bóng đổ (đếm là 1 lần 3D theo luật nhịp dựng)."""
        c = self.text(text, at, dur, "sans", size, y=y, shadow={"color": "#000000", "opacity": 70, "blur": 14, "distance": 14})
        keys, t, sgn = [], 0.0, -1
        while t <= c["dur"] + 1e-6:
            keys.append([round(t, 3), 22 * sgn, "bezier"])
            t += period / 2
            sgn *= -1
        c["opacity"] = [[0, 0], [self._k(c, 0.1), 100]]
        return self._fx(c, "rotate_3d", {"rot_y": keys, "rot_x": 6, "perspective": 60})

    def slide_down_text(self, text: str, at: float, dur: float, role: str = "serif", size: int = 190, y: int = 300,
                        color: str | None = None) -> dict:
        """B10 Chữ trượt từ trên xuống kèm nhoè chuyển động dọc, 0,33 s."""
        c = self.text(text, at, dur, role, size, y=y, color=color or self.accent)
        self.slide_down(c)
        if c["color"] != WHITE:
            self.glow(c)
        return c

    def word_captions(self, words: list[tuple[str, float]], end: float, y: int | None = None, size: int = 66,
                      max_w: int = 700, chunk: int = 4, mode: str = "grey", shadow: dict | None = SHADOW) -> list:
        """B11 Phụ đề hiện thêm từng chữ theo lời (mỗi chữ một clip), cụm ≤ `chunk` chữ, không tách số khỏi đơn vị.
        words = [(chữ, giây bắt đầu nói)] theo thứ tự; mode "grey" (xám→trắng) hoặc "color" (tím→trắng).
        Nền sau phụ đề sáng (áo trắng, tường sáng) → shadow=STRONG_SHADOW."""
        y = y or self.cap_y
        groups, cur = [], []
        for w, t in words:
            cur.append((w, t))
            if len(cur) >= chunk or w.endswith((".", ",", "?", "!")):
                groups.append(cur)
                cur = []
        if cur:
            groups.append(cur)
        for i in range(len(groups) - 1):               # "3 | giây" → kéo số sang cụm sau
            if groups[i][-1][0][0].isdigit() and len(groups[i]) > 1:
                groups[i + 1].insert(0, groups[i].pop())
        out = []
        for gi, g in enumerate(groups):
            g_end = groups[gi + 1][0][1] if gi + 1 < len(groups) else end
            toks = [w for w, _ in g]
            if self.cap_case:
                toks[0] = cap_first(toks[0])
            line = " ".join(toks)
            sz = size
            while sz > 48 and self.width("cap", sz, line) > max_w:
                sz -= 2
            x = 540 - self.width("cap", sz, line) / 2
            for j, (w, (_, t)) in enumerate(zip(toks, g)):
                t = max(0.0, min(max(t - 0.03, g[0][1] - 0.03), g_end - 0.1))   # hiện sớm 1 khung, không âm
                if g_end - t >= 0.06:
                    c = self.text(w, t, g_end - t, "cap", sz, x=x, y=y, align="left", lane="text_low", case=False, shadow=shadow)
                    (self.grey_in(c) if mode == "grey" else self.color_in(c, "#A855F7", 0.25))
                    c["_slot"] = j
                    out.append(c)
                x += self.advance("cap", sz, w + " ")
        return out

    def behind_head(self, text: str, at: float, dur: float, matte_src: str, matte_in: float = 0.0, y: int | None = None,
                    size: int = 400, role: str = "condensed", halo: str | None = None, head_top: int | None = None) -> list:
        """B12 Chữ HOA rất lớn nằm sau đầu: chữ ở lane text_behind, lớp người có alpha (ProRes 4444 từ
        `matte.py`) ở lane matte phía trên. Đáy chữ mờ dần (crop feather).
        head_top = y đỉnh đầu đo trên khung → chữ đặt để đầu che ~30% phần dưới chữ (khuyên dùng thay vì đoán y)."""
        if y is None:
            y = (head_top + round(size * 0.22)) if head_top else 760
        if role == "condensed" and not all(ord(ch) < 128 for ch in text):
            role = "sans"                                # Bebas Neue không có dấu tiếng Việt
        c = self.text(text, at, dur, role, size, y=y, lane="text_behind", case=False,
                      shadow={"color": halo or "#000000", "opacity": 60 if halo else 40, "blur": 30, "distance": 0})
        self.blur_in(c, 0.4, 30)
        c["motion"] = {"position": [[0, [540, 930]], [self._k(c, 0.4), [540, 960], "easeIn"]]}
        self._fx(c, "crop", {"bottom": round((1920 - y - 10) / 1920 * 100, 1), "feather": 90})
        m = {"src": matte_src, "at": c["at"], "in": matte_in, "dur": c["dur"], "audio": False, "name": self._name("Người tách nền (che chữ)")}
        self.items.append(("matte", m))
        return [c, m]

    def wall_text(self, main: str, script: str | None, at: float, dur: float, x: int = 640, y: int = 330,
                  size: int = 200, rot_y: float = -24, rot_z: float = -6, exit_smear: bool = True) -> list:
        """B13 Chữ HOA gắn lên tường: nghiêng phối cảnh (rotate_3d) + bóng rơi xuống tường, fade xám→trắng,
        ra bằng nhoè + vệt. Đặt sớm hơn lời ~0,3 s."""
        sh = {"color": "#000000", "opacity": 55, "blur": 18, "distance": 14}
        m = self.text(main, at, dur, "sans", size, x=x, y=y, shadow=sh, case=False)
        self.grey_in(m, 0.25, 8)
        self._fx(m, "rotate_3d", {"rot_y": rot_y, "rot_z": rot_z, "perspective": 55})
        out = [m]
        if script:
            s = self.text(script, at + 0.3, dur - 0.3, "script", round(size * 0.6), x=x + 120, y=y + round(size * 0.45),
                          lane="text_top", case=False, shadow=sh)
            self.grey_in(s, 0.25, 8)
            self._fx(s, "rotate_3d", {"rot_y": rot_y, "rot_z": rot_z, "perspective": 55})
            out.append(s)
        if exit_smear:
            for c in out:
                t0 = max(0, c["dur"] - 0.3)
                c["opacity"] = c["opacity"] + [[t0, 100], [c["dur"], 0]]
                self._fx(c, "directional_blur", {"direction": 90, "length": [[t0, 0], [c["dur"], 60]]})
        return out

    def tilt_text(self, text: str, at: float, dur: float, x: int, y: int, deg: float = -15, size: int = 50) -> dict:
        """B14a Chữ nhỏ xoay theo đường cong vật thể (chân mày, cạnh bàn…)."""
        c = self.text(text, at, dur, "semi", size, x=x, y=y, case=False)
        c["motion"] = {"anchor": [x, y - size // 3], "position": [x, y - size // 3], "rotation": deg}
        c["opacity"] = [[0, 0], [self._k(c, 0.08), 100]]
        return c

    def punch_overflow(self, word: str, at: float, dur: float, punch_at: float, small: str | None = None,
                       x: int = 720, y: int = 1280, scale: float = 140, origin: tuple = (700, 1400)) -> list:
        """B14b Chữ nghiêng màu nhấn lớn bị phóng tràn khung cùng cú punch-in của hình (áp cùng keyframe
        `motion.scale` 100→`scale` tại `punch_at` lên clip A-roll để khớp)."""
        c = self.text(word, at, dur, "serif", 190, x=x, y=y, color=self.accent, case=False)
        self.slide_up(c, dy=120, d=0.4)
        p = punch_at - c["at"]
        c["motion"] = {"anchor": list(origin), "position": [[0, [origin[0], origin[1] + 120]], [self._k(c, 0.4), list(origin), "easeIn"]],
                       "scale": [[0, 100], [p, 100, "hold"], [p + 0.15, scale, "easeIn"]]}
        out = [c]
        if small:
            s = self.text(small, at - 0.15, dur + 0.15, "cap", 46, x=x - 260, y=y - 190, align="left", lane="text_low", case=False)
            s["opacity"] = [[0, 0], [0.1, 100]]
            out.append(s)
        return out

    def glow_text(self, text: str, at: float, dur: float, role: str = "serif", size: int = 130, y: int | None = None) -> dict:
        """B15 Chữ phát sáng ("Phát sáng 2"): lộ ra rồi glow mạnh dần ~0,5 s (wonder_glow)."""
        c = self.text(text, at, dur, role, size, y=y, case=False)
        self.blur_in(c, 0.3, 20)
        return self.glow(c, ramp=0.6, intensity=100)

    def dreamy_blur(self, text: str, at: float, dur: float, size: int = 120, y: int | None = None, axis: str = "Vertical") -> dict:
        """B16 Chữ mờ ảo: nhoè một chiều 25 → ~2 trong 0,5 s, còn đuôi mờ nhẹ."""
        c = self.text(text, at, dur, "serif", size, y=y, case=False)
        c["opacity"] = [[0, 40], [self._k(c, 0.5), 100]]
        return self._fx(c, "gaussian_blur", {"blurriness": [[0, 25], [self._k(c, 0.5), 3, "easeIn"]], "dimensions": axis})

    def overlay_text(self, text: str, at: float, dur: float, size: int = 130, y: int = 1100) -> list:
        """B17 Chữ hoà vào cảnh: blend Overlay (vân áo/màu cảnh xuyên qua chữ) + một bản glow mờ bên dưới.
        Vào bằng vệt kéo dọc 3 khung. Đặt trên vùng có chi tiết (áo, tường); nền tối quá thì chữ gần như biến mất."""
        g = self.text(text, at, dur, "sans", size, y=y, lane="text_low", case=False, shadow=None)
        g["opacity"] = [[0, 0], [self._k(g, 0.15), 35]]
        self._fx(g, "gaussian_blur", {"blurriness": 12})
        c = self.text(text, at, dur, "sans", size, y=y, case=False, shadow=None)
        c["blend"] = "overlay"
        cy = self.center_y(c)
        c["motion"] = {"anchor": [540, cy], "position": [540, cy], "scale": [[0, 100], [self._k(c, 0.25), 100]]}
        c["opacity"] = [[0, 20], [self._k(c, 0.1), 60], [self._k(c, 0.3), 100]]
        self._fx(c, "directional_blur", {"direction": 0, "length": [[0, 60], [self._k(c, 0.3), 0, "easeIn"]]})
        return [g, c]

    def gradient_word(self, text: str, at: float, dur: float, colors: list[str], role: str = "serif", size: int = 150,
                      y: int | None = None, angle: float = 90) -> dict:
        """B18 Chữ gradient (điểm xuyết 1 từ cảm xúc) — vẽ PNG bằng PIL rồi blur-in; sửa chữ = sửa lời gọi."""
        y = y or self.key_y
        p = G.gradient_text(self.gfx_dir, f"gradient_{len(self.items)}", nfc(text), str(FONTS[role][2]), size, 540, y, colors, angle)
        c = self.image(p, at, dur, lane="text_img", name=f"Chữ gradient · {text}")
        c["opacity"] = [[0, 0], [self._k(c, 0.2), 100]]
        c["effects"] = [{"effect": "gaussian_blur", "params": {"blurriness": [[0, 20], [self._k(c, 0.33), 0, "easeIn"]]}}]
        return c

    def typed_box(self, text: str, at: float, dur: float, under: str | None = None, size: int = 110,
                  y: int | None = None, frames: int = 14) -> list:
        """B19 Gõ chữ trong khung chọn kiểu phần mềm dựng (chuyển cảnh typewriter + PNG khung 8 tay nắm)."""
        y = (y or self.key_y) - 25
        c = self.text(text, at, dur, "bold", size, y=y)
        c["transition_in"] = {"effect": "typewriter", "frames": frames}
        cy, w = self.center_y(c), round(self.width("bold", c["size"], c["text"]) + 80)
        p = G.select_box(self.gfx_dir, f"select_box_{len(self.items)}", 540, cy + 4, w, round(c["size"] * 1.25))
        b = self.image(p, at, dur, lane="gfx_under", name="Khung chọn chữ")
        b["opacity"] = [[0, 0], [self._k(b, 0.06), 100]]
        out = [c, b]
        if under:
            u = self.text(under, at, dur, "sans", 95, y=y + round(c["size"] * 1.1), lane="text_low")
            out.append(u)
        self.cues.append({"t": c["at"], "kind": "gõ phím ngắn", "why": "chữ gõ trong khung"})
        return out

    def glass_pill(self, text: str, at: float, dur: float, y: int = 330, fill: str = "#3E7F69", frames: int = 24) -> dict:
        """B20 Pill kính lộ dần trái → phải (chuyển cảnh linear_wipe)."""
        p = G.pill(self.gfx_dir, f"pill_{len(self.items)}", nfc(text), str(FONTS["cap"][2]), 540, y, 40, fill)
        c = self.image(p, at, dur, lane="gfx_over", name=f"Pill · {text}")
        c["transition_in"] = {"effect": "linear_wipe", "frames": frames}
        return c

    def ui_card(self, src: str, at: float, dur: float, src_in: float = 0.0, label: str | None = None,
                w: int = 1000, src_w: int = 1920, center: tuple = (540, 1060), threed: bool = False) -> list:
        """B21 Thẻ video bo góc viền màu nhấn phóng 82→100% + nhoè (hoặc xoay 3D khi threed=True), nhãn màu nhấn
        đè mép dưới. Nền mờ phía sau nên làm riêng ở track B-roll (bản sao clip + gaussian_blur 60)."""
        s = round(w / src_w * 100, 2)
        c = {"src": src, "at": self.snap(at), "in": src_in, "dur": self.snap(at + dur) - self.snap(at), "audio": False,
             "name": self._name("Thẻ UI"), "motion": {"position": list(center), "scale": [[0, round(s * 0.82, 2)], [0.28, s, "easeIn"]]},
             "opacity": [[0, 0], [0.12, 100]],
             "effects": [{"effect": "rounded_crop", "params": {"radius": round(36 * src_w / w), "border": 6 * src_w / w,
                                                               "border_color": self.accent}},
                         {"effect": "drop_shadow", "params": {"opacity": 70, "distance": 16, "softness": 50}}]}
        if threed:
            c["effects"].append({"effect": "rotate_3d", "params": {"rot_y": [[0, -70], [0.45, 0, "easeIn"]], "perspective": 60}})
        else:
            c["effects"].append({"effect": "gaussian_blur", "params": {"blurriness": [[0, 20], [0.28, 0, "easeIn"]]}})
        self.items.append(("card", c))
        out = [c]
        if label:
            h = w * 9 / 16
            lb_y = round(center[1] + h / 2 + self.ink_top("sans", 60, label) + 19)   # dưới mép thẻ + viền (đã kiểm THCN 03)
            lb = self.text(label, at + 0.1, dur - 0.1, "sans", 60, y=lb_y, color=self.accent, case=False)
            self.blur_in(lb, 0.17, 20)
            out.append(lb)
        self.cues.append({"t": c["at"] + 0.1, "kind": "whoosh/swish", "why": "thẻ trượt vào"})
        return out

    def cta_save(self, at: float, dur: float, big: str = "Lưu lại", top: str = "nhớ", tail: list[tuple[str, float]] = (),
                 click_at: float | None = None, y: int | None = None, color: str = "#D7A21A") -> list:
        """B22 CTA "Lưu lại" viết tay màu nhấn + "nhớ" nhỏ + dòng nhỏ từng từ + bookmark xám → màu khi con trỏ bấm."""
        y = y or self.key_y
        b = self.text(big, at + 0.08, dur - 0.08, "script", 200, y=y, color=color, lane="text", case=False)
        self.slide_up(b, dy=40, d=0.35)
        bw = self.width("script", b["size"], b["text"])
        t = self.text(top, at, dur, "cap", 44, x=540 + bw / 2 - 10, y=y - 150, align="right", lane="text_low", case=False)
        t["opacity"] = [[0, 0], [0.1, 100]]
        out = [b, t]
        x = 540 - bw / 2 + 20
        for w, tt in tail:
            s = self.text(w, tt, at + dur - tt, "cap", 44, x=x, y=y + 70, align="left", lane="text_low", case=False)
            s["opacity"] = [[0, 0], [self._k(s, 0.08), 100]]
            x += self.advance("cap", 44, w + " ")
            out.append(s)
        click_at = click_at if click_at is not None else at + 0.6
        bx, by = round(540 + bw / 2 + 20), round(y - 120)
        g = G.bookmark(self.gfx_dir, "cta_bookmark_xam", bx, by, 64, "#888888", cursor=True)
        gy = G.bookmark(self.gfx_dir, "cta_bookmark_nhan", bx, by, 64, color, cursor=True)
        self.image(g, at + 0.3, click_at - at - 0.3, name="Bookmark xám")
        self.image(gy, click_at, at + dur - click_at, name="Bookmark màu nhấn")
        self.cues.append({"t": click_at, "kind": "click chuột", "why": "bấm lưu"})
        return out

    def strike_word(self, text: str, at: float, dur: float, strike_at: float, small: str | None = None,
                    y: int | None = None, color: str = "#E8203A") -> list:
        """B23a Gạch ngang phát sáng cho từ bị phủ định: vạch PNG + chuyển cảnh linear_wipe (trái → phải)."""
        y = y or self.key_y
        c = self.text(text, at, dur, "serif", 120, y=y, case=False)
        self.grey_in(c)
        cy, w = self.center_y(c), round(self.width("serif", c["size"], c["text"]) + 40)
        p = G.strike_bar(self.gfx_dir, f"strike_{len(self.items)}", 540, cy + 8, w, color)
        s = self.image(p, strike_at, at + dur - strike_at, name="Vạch gạch chữ")
        s["transition_in"] = {"effect": "linear_wipe", "frames": max(3, round(0.3 * self.fps))}
        out = [c, s]
        if small:
            out.append(self.text(small, at, dur, "cap", 46, y=y - round(c["size"] * 0.95), lane="text_low", case=False))
        self.cues.append({"t": strike_at, "kind": "scratch / gạch bút", "why": "gạch chữ"})
        return out

    def font_flip(self, word: str, at: float, step: float = 0.5, roles: tuple = ("sans", "serif", "script", "num", "serif_reg"),
                  size: int = 150, y: int | None = None) -> list:
        """B23b Một từ đổi font liên tục (minh hoạ "font chữ"), mỗi kiểu 0,4–0,6 s, cắt cứng."""
        out = []
        for i, r in enumerate(roles):
            out.append(self.text(word, at + i * step, step, r, size, y=y, case=False, lane="text"))
        return out

    def flicker_text(self, text: str, at: float, dur: float, flicker: float = 0.5, size: int = 170, y: int | None = None) -> dict:
        """B23c Chữ chớp: bật/tắt mỗi 2 khung trong `flicker` giây đầu (opacity hold), rồi đứng yên."""
        c = self.text(text, at, dur, "sans", size, y=y, case=False)
        step = 2 / self.fps
        keys, t, on = [], 0.0, True
        while t < min(flicker, c["dur"]):
            keys.append([round(t, 4), 100 if on else 0, "hold"])
            t += step
            on = not on
        if t < c["dur"] - 1 / self.fps:
            keys.append([round(t, 4), 100, "hold"])
        c["opacity"] = keys
        self.cues.append({"t": c["at"], "kind": "glitch/click ngắn", "why": "chữ chớp"})
        return c

    def curved_caption(self, text: str, at: float, dur: float, cx: int = 540, cy: int = 700, radius: int = 230,
                       size: int = 40, ring: bool = True) -> dict:
        """B23d Chữ chạy theo cung tròn dưới khung tròn/avatar — PNG (FilmCraft chưa có chữ theo đường cong)."""
        p = G.curved_text(self.gfx_dir, f"curved_{len(self.items)}", nfc(text), str(FONTS["cap"][2]), size, cx, cy, radius, ring=ring)
        c = self.image(p, at, dur, lane="text_img", name=f"Chữ cong · {text[:20]}")
        c["opacity"] = [[0, 0], [self._k(c, 0.25), 100]]
        return c

    def tutorial_layout(self, title: str, at: float, dur: float, captions: list[tuple[str, float]] = (),
                        keywords: list[tuple[str, float]] = (), title_y: int = 330, cap_y: int = 1330,
                        key_color: str = "#1E9E2A") -> list:
        """B24 Chữ trên cảnh quay màn hình: tiêu đề bước Heavy Italic có glow ở trên; phụ đề 2–4 từ ở mép dưới
        khung quay; từ khoá xanh lá ngay dưới, hiện đúng lúc con trỏ bấm menu."""
        t = self.text(title, at, dur, "sans_it", 120, y=title_y)
        self.blur_in(t, 0.25, 20)
        self.glow(t, intensity=70)
        out = [t]
        for i, (txt, tt) in enumerate(captions):
            e = captions[i + 1][1] if i + 1 < len(captions) else at + dur
            out.append(self.text(txt, tt, e - tt, "cap", 48, y=cap_y, lane="text_low", case=False))
        for i, (txt, tt) in enumerate(keywords):
            e = keywords[i + 1][1] if i + 1 < len(keywords) else at + dur
            out.append(self.text(txt, tt, e - tt, "sans_it", 60, y=cap_y + 70, color=key_color, lane="text_top", case=False))
        return out

    # ---------- xếp track ----------
    def tracks(self, prefix: str = "") -> list[dict]:
        """Xếp mọi clip vào track theo lớp (LANES, dưới → trên), mỗi lớp tách nhiều track khi clip chồng thời gian."""
        out = []
        for lane, kind in LANES:
            clips = sorted((c for ln, c in self.items if ln == lane), key=lambda c: c["at"])
            rows: list[list[dict]] = []
            for c in clips:
                for row in rows:
                    if row[-1]["at"] + row[-1]["dur"] <= c["at"] + 1e-6:
                        row.append(c)
                        break
                else:
                    rows.append([c])
            for i, row in enumerate(rows):
                clean = [{k: v for k, v in c.items() if not k.startswith("_")} for c in row]
                out.append({"type": kind, "name": f"{prefix}{lane} {i + 1}", "clips": clean})
        return out
