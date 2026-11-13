"""Ghép font cụm nhấn Fraunces Italic 800 cho After Effects.

Nguồn: đúng 3 file woff2 mà V2 (Remotion, @remotion/google-fonts) đã render — Google Fonts v38,
giấy phép OFL. Mỗi file là font biến thiên chỉ còn trục wght; trình duyệt áp wght=800 khi vẽ.
AE cần một file tĩnh có đủ Latin + tiếng Việt, nên ta cố định wght=800 rồi ghép 3 phần.

Chạy: python -I tools/build_accent_font.py
Ra:   assets/fonts/FrauncesOPA-ExtraBoldItalic.ttf
"""
from pathlib import Path

from fontTools.merge import Merger
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "fonts" / "src"
OUT = ROOT / "assets" / "fonts" / "FrauncesOPA-ExtraBoldItalic.ttf"
PARTS = ["latin", "latin-ext", "vietnamese"]
WGHT = 800

FAMILY = "Fraunces OPA"
STYLE = "ExtraBold Italic"
PS_NAME = "FrauncesOPA-ExtraBoldItalic"


def static_part(name: str) -> Path:
    font = TTFont(SRC / f"fraunces-i800-{name}.woff2")
    font.flavor = None
    static = instantiateVariableFont(font, {"wght": WGHT})
    path = SRC / f"_static-{name}.ttf"
    static.save(path)
    return path


def rename(font: TTFont) -> None:
    names = font["name"]
    names.removeNames(nameID=16)
    names.removeNames(nameID=17)
    for plat, enc, lang in ((3, 1, 0x409), (1, 0, 0)):
        names.setName(f"{FAMILY} ExtraBold", 1, plat, enc, lang)
        names.setName("Italic", 2, plat, enc, lang)
        names.setName(f"{FAMILY} {STYLE}", 4, plat, enc, lang)
        names.setName(PS_NAME, 6, plat, enc, lang)
        names.setName(FAMILY, 16, plat, enc, lang)
        names.setName(STYLE, 17, plat, enc, lang)
        names.setName(f"{PS_NAME}; Fraunces v38 Google Fonts wght {WGHT}", 3, plat, enc, lang)
    os2 = font["OS/2"]
    os2.usWeightClass = WGHT
    os2.fsSelection = (os2.fsSelection | 0x01) & ~0x40 & ~0x20  # ITALIC, bỏ REGULAR/BOLD
    font["head"].macStyle = (font["head"].macStyle | 0x02) & ~0x01


def main() -> None:
    parts = [str(static_part(p)) for p in PARTS]
    merged = Merger().merge(parts)
    rename(merged)
    merged.save(OUT)
    for p in parts:
        Path(p).unlink()
    cmap = TTFont(OUT).getBestCmap()
    print(f"OK {OUT.name}: {len(cmap)} ký tự, U+{min(cmap):04X}–U+{max(cmap):04X}")


if __name__ == "__main__":
    main()
