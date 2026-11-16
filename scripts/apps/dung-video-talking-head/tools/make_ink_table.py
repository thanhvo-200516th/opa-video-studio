# -*- coding: utf-8 -*-
"""make_ink_table.py — sinh `releases/<ver>/template/src/ink.ts` (spec 1.1.1 §7.1 b, R65): phần nét
chữ thò ra ngoài hộp chữ ở mép phải (r) / trái (l) của từng ký tự, theo em, cho hai font hero:
  - script = BeVietnamPro-BlackItalic.ttf;
  - stomp  = DTPhudu-Black.otf, tra bằng chữ HOA (Subtitle.tsx in hoa hero stomp/quote).
Subtitle.tsx đệm ô từ hero bằng l của ký tự đầu và r của ký tự cuối, nên hộp của từ chứa trọn nét
(D2 — background-clip:text chỉ tô trong hộp; B14 đo nét thật).

  r = (xMax − advance)/upm − letter-spacing hero (đọc từ Subtitle.tsx, −0,015 em: trình duyệt cộng
      letter-spacing cả sau ký tự cuối nên hộp hụt thêm 0,015 em) + text.ink_margin_em
  l = −xMin/upm + text.ink_margin_em
Làm tròn lên 0,001; chỉ ghi số > 0 (đã gồm lề), trên bộ 235 ký tự cố định:
ASCII 0x21–0x7E, 67 chữ có dấu tiếng Việt × 2 kiểu chữ, và “”‘’…–—. Ký tự font không có thì bỏ
(trình duyệt vẽ bằng font dự phòng — B14 vẫn là chốt chặn).

Công cụ dev (fontTools của Python hệ thống — không có trong venv Hermes; runtime chỉ đọc ink.ts).
Đổi font, letter-spacing hay text.ink_margin_em thì chạy lại; test_ink_table_matches_fonts (chậm)
báo khi quên.

Dùng: PYTHONIOENCODING=utf-8 python tools/make_ink_table.py [--ver 1.1.1] [--font-pack DIR]
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
DEFAULT_VERSION = "1.1.1"
FONT_PACK = Path("D:/MMO/Font/Cinematic fonts pack")       # bộ font 1.0.0 (R17) — như stage.FONTS
SCRIPT_REL = "Font Việt hóa cinematic/Be_Vietnam_Pro/Be_Vietnam_Pro/BeVietnamPro-BlackItalic.ttf"
STOMP_REL = "DT-Phudu/Fonts Files/DTPhudu-Black.otf"
SCRIPT_FONT = FONT_PACK / SCRIPT_REL
STOMP_FONT = FONT_PACK / STOMP_REL
HEAD = "// TỰ SINH bởi tools/make_ink_table.py — đừng sửa tay\n"

_VI = "àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ"
CHARSET = "".join(map(chr, range(0x21, 0x7F))) + _VI + _VI.upper() + "“”‘’…–—"


def _up(x: float) -> float:
    """Làm tròn lên lưới 0,001 (bỏ sai số dấu phẩy động)."""
    return math.ceil(round(x * 1000, 6)) / 1000


def letter_spacing_em(subtitle_tsx: Path) -> float | None:
    """letter-spacing (em) của dòng hero trong Subtitle.tsx (`letterSpacing: hero ? "-0.015em"`); None
    khi không thấy mẫu."""
    text = Path(subtitle_tsx).read_text(encoding="utf-8")
    m = re.search(r'letterSpacing: hero \? "(-?[\d.]+)em"', text)
    return float(m.group(1)) if m else None


def _glyphs(font_path: Path):
    """(upm, typo ascent, [(ký tự, xMin, xMax, yMax, advance)]) — mọi ký tự của CHARSET font có nét."""
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.ttLib import TTFont

    font = TTFont(str(font_path))
    cmap, gs, hmtx = font.getBestCmap(), font.getGlyphSet(), font["hmtx"]
    out = []
    for ch in CHARSET:
        name = cmap.get(ord(ch))
        if name is None:
            continue
        pen = BoundsPen(gs)
        gs[name].draw(pen)
        if pen.bounds is not None:
            x0, _, x1, y1 = pen.bounds
            out.append((ch, x0, x1, y1, hmtx[name][0]))
    return font["head"].unitsPerEm, font["OS/2"].sTypoAscender, out


def overhangs(font_path: Path, letter_spacing: float, margin: float, upper: bool = False) -> dict:
    """{"l": {...}, "r": {...}} phần thò (em, đã cộng lề) của ký tự thò > 0; `upper`: khoá bằng chữ
    HOA (mọi ký tự của CHARSET đưa về chữ hoa rồi mới đo)."""
    upm, _, glyphs = _glyphs(font_path)
    keep = {ch.upper() for ch in CHARSET} if upper else set(CHARSET)
    r, l = {}, {}
    for ch, x0, x1, _, adv in glyphs:
        if ch not in keep:
            continue
        right, left = _up((x1 - adv) / upm - letter_spacing + margin), _up(-x0 / upm + margin)
        if right > 0:
            r[ch] = right
        if left > 0:
            l[ch] = left
    return {"l": l, "r": r}


def advances(font_path: Path, upper: bool = False) -> dict:
    """{ký tự: advance (em, làm tròn lên 0,001)} trên CHARSET — R124: Subtitle.tsx tính bề rộng hero dựng một
    hàng (hero_row) bằng advance thật thay vì đếm ký tự (chữ HOA script rộng gấp rưỡi chữ thường).
    `upper`: như overhangs."""
    from fontTools.ttLib import TTFont

    font = TTFont(str(font_path))
    cmap, hmtx, upm = font.getBestCmap(), font["hmtx"], font["head"].unitsPerEm
    keep = {ch.upper() for ch in CHARSET} if upper else set(CHARSET)
    return {ch: _up(hmtx[cmap[ord(ch)]][0] / upm) for ch in keep if ord(ch) in cmap}


def top_overhang_em(font_path: Path) -> float:
    """Nét cao nhất vượt typo ascent (em) trên CHARSET — lề sơn GLYPH_PAD_EM phải phủ cả phần này."""
    upm, ascent, glyphs = _glyphs(font_path)
    return (max(g[3] for g in glyphs) - ascent) / upm


def build(script_font: Path, stomp_font: Path, letter_spacing: float, margin: float) -> str:
    """Nội dung src/ink.ts (tất định: khoá sắp theo mã ký tự)."""
    table = {"script": overhangs(script_font, letter_spacing, margin),
             "stomp": overhangs(stomp_font, letter_spacing, margin, upper=True)}
    body = json.dumps(table, ensure_ascii=False, sort_keys=True, indent=1)
    adv = json.dumps({"script": advances(script_font), "stomp": advances(stomp_font, upper=True)},
                     ensure_ascii=False, sort_keys=True, indent=1)
    return (HEAD
            + "// Advance (em) của từng ký tự hero — script và stomp (tra chữ HOA). Subtitle.tsx tính bề rộng hero\n"
            + "// dựng một hàng (hero_row, R124).\n"
            + 'export const ADV: Record<"script" | "stomp", Record<string, number>> = ' + adv + ";\n"
            + "// Phần nét chữ thò khỏi hộp chữ (em) ở mép trái (l) / phải (r) của ký tự — hero script\n"
            + "// (BeVietnamPro-BlackItalic) và stomp (DTPhudu-Black, tra chữ HOA); đã gồm letter-spacing\n"
            + "// hero và text.ink_margin_em. Subtitle.tsx đệm ô từ hero bằng các số này (D2, R65).\n"
            + 'export const INK: Record<"script" | "stomp", { l: Record<string, number>; r: Record<string, number> }> = '
            + body + ";\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sinh template/src/ink.ts từ font hero (D2, R65)")
    ap.add_argument("--ver", default=DEFAULT_VERSION, help="Số bản release, vd 1.1.1")
    ap.add_argument("--font-pack", default=str(FONT_PACK), help="Thư mục bộ font 1.0.0")
    args = ap.parse_args(argv)
    rel = SKILL / "releases" / args.ver
    pack = Path(args.font_pack)
    for font in (pack / SCRIPT_REL, pack / STOMP_REL):
        if not font.is_file():
            print(f"FAIL: không thấy font {font}")
            return 1
    rules = json.loads((rel / "rules.json").read_text(encoding="utf-8"))
    margin = rules["params"]["text"]["ink_margin_em"]
    spacing = letter_spacing_em(rel / "template" / "src" / "comp" / "Subtitle.tsx")
    if spacing is None:
        print("FAIL: không tìm thấy letterSpacing hero trong Subtitle.tsx")
        return 1
    out = rel / "template" / "src" / "ink.ts"
    out.write_text(build(pack / SCRIPT_REL, pack / STOMP_REL, spacing, margin), encoding="utf-8")
    print(f"PASS: đã ghi {out} (letter-spacing {spacing} em, lề {margin} em)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
