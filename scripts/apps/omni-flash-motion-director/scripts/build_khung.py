"""Dựng khung neo và ảnh tham chiếu cho Google Flow (Omni Flash) từ logo OPA V4.

Nguồn:
- Dấu đầu bò: logo/OPA-V4-A-Core-*-2000.png (khớp dấu trên PDF trang 3, IoU 0,9964).
- Chữ OPA: flow-omni/nguon/chu-OPA_tu-PDF-trang3.png, tách từ
  "D:/Cowork Minh/OPA/OPA — Biểu tượng 2D V4.pdf" bằng tools/flow-omni/tach_pdf.py.

Chạy từ thư mục gốc dự án:  python tools/flow-omni/build_khung.py
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "flow-omni"
BLUE = (0, 104, 255)
WHITE = (255, 255, 255)
SUPERSAMPLE = 4

# Cụm logo đo trên ảnh trang 3 của PDF (5280 px): dấu và chữ đứng chung đường đáy.
MARK_BOX = (63, 49, 428, 382)
WORD_BOX = (534, 168, 1248, 380)

# Vị trí theo khung. 9:16 đặt tâm giữa vùng an toàn (250 px trên, 420 px dưới).
SPECS = {
    "16x9": {"size": (1920, 1080), "center": (960, 540), "mark_h": 500,
             "lock_mark_h": 323, "bubble_w": 420, "offset": (538, 540),
             "net_mark_h": 300, "net_center": (960, 500), "net_radii": (520, 300), "node_d": 120},
    "9x16": {"size": (1080, 1920), "center": (540, 875), "mark_h": 565,
             "lock_mark_h": 242, "bubble_w": 480, "offset": (540, 1210),
             "net_mark_h": 260, "net_center": (540, 820), "net_radii": (360, 470), "node_d": 120},
}

# Mạng lưới kênh (K07): sáu biểu tượng chung chung, không ảnh người thật (BRAND-SPEC mục 1).
NODES = ("chat", "mail", "person", "bag", "globe", "phone")
NODE_ANGLES = (30, 90, 150, 210, 270, 330)


def load_trim(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    return im.crop(im.getchannel("A").getbbox())


def fit_height(im: Image.Image, h: int) -> Image.Image:
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)


def recolor(im: Image.Image, rgb: tuple[int, int, int]) -> Image.Image:
    solid = Image.new("RGBA", im.size, rgb + (255,))
    solid.putalpha(im.getchannel("A"))
    return solid


MARK = {
    "blue": load_trim(ROOT / "logo/OPA-V4-A-Core-blue-2000.png"),
    "white": load_trim(ROOT / "logo/OPA-V4-A-Core-white-2000.png"),
}
WORD = load_trim(OUT / "nguon/chu-OPA_tu-PDF-trang3.png")


def lockup(mark_h: int, color: str) -> Image.Image:
    s = mark_h / (MARK_BOX[3] - MARK_BOX[1])
    img = Image.new("RGBA", (round((WORD_BOX[2] - MARK_BOX[0]) * s), mark_h), (0, 0, 0, 0))
    img.alpha_composite(fit_height(MARK[color], mark_h), (0, 0))
    word_size = (round((WORD_BOX[2] - WORD_BOX[0]) * s), round((WORD_BOX[3] - WORD_BOX[1]) * s))
    word = recolor(WORD, BLUE if color == "blue" else WHITE).resize(word_size, Image.LANCZOS)
    img.alpha_composite(word, (round((WORD_BOX[0] - MARK_BOX[0]) * s),
                               round((WORD_BOX[1] - MARK_BOX[1]) * s)))
    return img


def chat_bubble(w: int) -> Image.Image:
    """Bong bóng chat phẳng #0068FF, đuôi trái dưới, ba chấm trắng."""
    W, body_h = w * SUPERSAMPLE, round(w * 0.62) * SUPERSAMPLE
    H = round(body_h * 1.25)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, W - 1, body_h), radius=round(body_h * 0.3), fill=BLUE)
    d.polygon([(W * 0.16, body_h - 2), (W * 0.36, body_h - 2), (W * 0.12, H - 1)], fill=BLUE)
    r = body_h * 0.075
    for i in (-1, 0, 1):
        cx, cy = W / 2 + i * W * 0.2, body_h / 2
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=WHITE)
    return img.resize((w, round(H / SUPERSAMPLE)), Image.LANCZOS)


def node_icon(kind: str, d: int) -> Image.Image:
    """Nút tròn trắng, hình xanh phẳng bên trong. Đơn vị u = 1 % đường kính."""
    S = d * SUPERSAMPLE
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    g = ImageDraw.Draw(img)
    g.ellipse((0, 0, S - 1, S - 1), fill=WHITE)
    c, u, w = S / 2, S / 100, round(S * 0.05)
    if kind == "chat":
        g.rounded_rectangle((c - 28 * u, c - 22 * u, c + 28 * u, c + 14 * u), radius=10 * u, fill=BLUE)
        g.polygon([(c - 18 * u, c + 12 * u), (c - 4 * u, c + 12 * u), (c - 22 * u, c + 28 * u)], fill=BLUE)
        for i in (-1, 0, 1):
            g.ellipse((c + i * 14 * u - 4 * u, c - 8 * u, c + i * 14 * u + 4 * u, c), fill=WHITE)
    elif kind == "mail":
        g.rounded_rectangle((c - 28 * u, c - 19 * u, c + 28 * u, c + 19 * u), radius=4 * u, outline=BLUE, width=w)
        g.line([(c - 26 * u, c - 16 * u), (c, c + 4 * u), (c + 26 * u, c - 16 * u)], fill=BLUE, width=w, joint="curve")
    elif kind == "person":
        g.ellipse((c - 12 * u, c - 28 * u, c + 12 * u, c - 4 * u), fill=BLUE)
        g.pieslice((c - 26 * u, c + 2 * u, c + 26 * u, c + 54 * u), 180, 360, fill=BLUE)
    elif kind == "bag":
        g.rounded_rectangle((c - 24 * u, c - 12 * u, c + 24 * u, c + 28 * u), radius=5 * u, fill=BLUE)
        g.arc((c - 13 * u, c - 30 * u, c + 13 * u, c - 4 * u), 180, 360, fill=BLUE, width=w)
    elif kind == "globe":
        g.ellipse((c - 28 * u, c - 28 * u, c + 28 * u, c + 28 * u), outline=BLUE, width=w)
        g.ellipse((c - 12 * u, c - 28 * u, c + 12 * u, c + 28 * u), outline=BLUE, width=w)
        g.line([(c - 28 * u, c), (c + 28 * u, c)], fill=BLUE, width=w)
    elif kind == "phone":
        g.rounded_rectangle((c - 16 * u, c - 30 * u, c + 16 * u, c + 30 * u), radius=6 * u, outline=BLUE, width=w)
        g.ellipse((c - 3 * u, c + 20 * u, c + 3 * u, c + 26 * u), fill=BLUE)
    return img.resize((d, d), Image.LANCZOS)


def network(sp: dict) -> Image.Image:
    """Dấu trắng giữa nền xanh, sáu nút kênh trên một elip, nan nối từ sát dấu ra nút, vòng nối các nút kề.
    Tâm mạng lưới đặt cao hơn tâm khung để chừa dải dưới cho một dòng chữ."""
    size, (cx, cy), (rx, ry), d = sp["size"], sp["net_center"], sp["net_radii"], sp["node_d"]
    mark = fit_height(MARK["white"], sp["net_mark_h"])
    a, b = mark.width / 2 + 18, mark.height / 2 + 18  # elip bao dấu, nan bắt đầu từ đây
    pts = [(cx + rx * math.cos(math.radians(t)), cy + ry * math.sin(math.radians(t))) for t in NODE_ANGLES]
    lines = Image.new("RGBA", (size[0] * SUPERSAMPLE, size[1] * SUPERSAMPLE), (0, 0, 0, 0))
    g = ImageDraw.Draw(lines)
    s = SUPERSAMPLE
    for i, (x, y) in enumerate(pts):
        nx, ny = pts[(i + 1) % len(pts)]
        g.line([(x * s, y * s), (nx * s, ny * s)], fill=WHITE, width=3 * s)
        dx, dy = x - cx, y - cy
        k = 1 / math.hypot(dx / a, dy / b)
        g.line([((cx + dx * k) * s, (cy + dy * k) * s), (x * s, y * s)], fill=WHITE, width=5 * s)
    canvas = Image.new("RGBA", size, BLUE + (255,))
    canvas.alpha_composite(lines.resize(size, Image.LANCZOS))
    place(canvas, mark, (cx, cy))
    for kind, (x, y) in zip(NODES, pts):
        place(canvas, node_icon(kind, d), (round(x), round(y)))
    return canvas.convert("RGB")


def place(canvas: Image.Image, im: Image.Image, center: tuple[int, int]) -> None:
    canvas.alpha_composite(im, (round(center[0] - im.width / 2), round(center[1] - im.height / 2)))


def frame(size: tuple[int, int], bg: tuple[int, int, int],
          item: Image.Image | None = None, center: tuple[int, int] | None = None) -> Image.Image:
    canvas = Image.new("RGBA", size, bg + (255,))
    if item is not None:
        place(canvas, item, center)
    return canvas.convert("RGB")


def build_frames(ratio: str) -> list[tuple[str, Image.Image]]:
    sp = SPECS[ratio]
    size, c = sp["size"], sp["center"]
    return [
        ("K00_nen-trang", frame(size, WHITE)),
        ("K01_dau-bo_nen-trang", frame(size, WHITE, fit_height(MARK["blue"], sp["mark_h"]), c)),
        ("K02_dau-bo-trang_nen-xanh", frame(size, BLUE, fit_height(MARK["white"], sp["mark_h"]), c)),
        ("K03_nen-xanh", frame(size, BLUE)),
        ("K04_logo-chu_nen-trang", frame(size, WHITE, lockup(sp["lock_mark_h"], "blue"), c)),
        ("K05_bong-bong-chat_nen-trang", frame(size, WHITE, chat_bubble(sp["bubble_w"]), c)),
        ("K06_dau-bo-lech_nen-trang",
         frame(size, WHITE, fit_height(MARK["blue"], sp["mark_h"]), sp["offset"])),
        ("K07_mang-luoi-kenh_nen-xanh", network(sp)),
    ]


BLUE_LIGHT = (230, 240, 255)
BLUE_DARK = (0, 60, 153)
BLACK = (10, 10, 10)
ALERT = (229, 72, 77)


def style_board() -> Image.Image:
    """Ảnh tham chiếu phong cách (T04): bảng màu BRAND-SPEC và mẫu giao diện phẳng, không chữ.
    Cho Omni thấy độ dày viền, độ bo góc, cách phối màu; không phải bố cục cảnh."""
    s = SUPERSAMPLE
    W, H = 1600 * s, 1000 * s
    img = Image.new("RGBA", (W, H), WHITE + (255,))
    g = ImageDraw.Draw(img)
    line = 3 * s
    # Hàng mẫu màu: xanh, xanh đậm, xanh nhạt, đen, trắng, chấm cảnh báo nhỏ.
    for i, col in enumerate((BLUE, BLUE_DARK, BLUE_LIGHT, BLACK, WHITE)):
        x, y, r = (760 + i * 150) * s, 140 * s, 55 * s
        g.ellipse((x - r, y - r, x + r, y + r), fill=col, outline=BLUE if col in (BLUE_LIGHT, WHITE) else None, width=line)
    g.ellipse((1510 * s - 18 * s, 140 * s - 18 * s, 1510 * s + 18 * s, 140 * s + 18 * s), fill=ALERT)
    # Bong bóng khách (xanh nhạt, đuôi trái) và bong bóng OPA (xanh, đuôi phải), để trống.
    g.rounded_rectangle((700 * s, 270 * s, 1130 * s, 370 * s), radius=36 * s, fill=BLUE_LIGHT)
    g.polygon([(712 * s, 362 * s), (760 * s, 362 * s), (700 * s, 395 * s)], fill=BLUE_LIGHT)
    g.rounded_rectangle((1060 * s, 400 * s, 1480 * s, 500 * s), radius=36 * s, fill=BLUE)
    g.polygon([(1420 * s, 492 * s), (1468 * s, 492 * s), (1480 * s, 525 * s)], fill=BLUE)
    # Thẻ trắng viền xanh 2 px, hai vạch giữ chỗ xanh nhạt, nút viên thuốc xanh.
    g.rounded_rectangle((700 * s, 570 * s, 1480 * s, 800 * s), radius=28 * s, fill=WHITE, outline=BLUE, width=line)
    g.rounded_rectangle((740 * s, 610 * s, 1200 * s, 638 * s), radius=14 * s, fill=BLUE_LIGHT)
    g.rounded_rectangle((740 * s, 658 * s, 1080 * s, 686 * s), radius=14 * s, fill=BLUE_LIGHT)
    g.rounded_rectangle((740 * s, 722 * s, 960 * s, 770 * s), radius=24 * s, fill=BLUE)
    # Ô nhập: viên thuốc trắng viền xanh + nút gửi tròn xanh.
    g.rounded_rectangle((700 * s, 860 * s, 1380 * s, 940 * s), radius=40 * s, fill=WHITE, outline=BLUE, width=line)
    g.ellipse((1400 * s, 860 * s, 1480 * s, 940 * s), fill=BLUE)
    img = img.resize((1600, 1000), Image.LANCZOS)
    place(img, fit_height(MARK["blue"], 470), (340, 500))
    return img.convert("RGB")


def build_references() -> list[tuple[str, Image.Image]]:
    return [
        ("T01_dau-bo-xanh_nen-trang", frame((1600, 1600), WHITE, fit_height(MARK["blue"], 1100), (800, 800))),
        ("T02_logo-chu-xanh_nen-trang", frame((2400, 1000), WHITE, lockup(560, "blue"), (1200, 500))),
        ("T03_dau-bo-trang_nen-xanh", frame((1600, 1600), BLUE, fit_height(MARK["white"], 1100), (800, 800))),
        ("T04_bang-phong-cach", style_board()),
    ]


def contact_sheet(frames: dict[str, list[tuple[str, Image.Image]]], path: Path) -> None:
    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 18)
    title = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 26)
    gap, tw, th, vw, vh = 24, 400, 225, 180, 320
    width = 4 * tw + 5 * gap
    height = 70 + 2 * (th + 40 + gap) + 40 + vh + 40 + gap
    sheet = Image.new("RGB", (width, height), (242, 244, 247))
    d = ImageDraw.Draw(sheet)
    d.text((gap, 20), "Khung neo cho Omni Flash · 16:9 (trên) và 9:16 (dưới)", fill=(10, 10, 10), font=title)
    for i, (name, im) in enumerate(frames["16x9"]):
        x, y = gap + (i % 4) * (tw + gap), 70 + (i // 4) * (th + 40 + gap)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
        d.rectangle((x - 1, y - 1, x + tw, y + th), outline=(200, 204, 210))
        d.text((x, y + th + 8), name, fill=(10, 10, 10), font=font)
    y = 70 + 2 * (th + 40 + gap) + 20
    count = len(frames["9x16"])
    vgap = (width - count * vw) // (count + 1)
    for i, (name, im) in enumerate(frames["9x16"]):
        x = vgap + i * (vw + vgap)
        sheet.paste(im.resize((vw, vh), Image.LANCZOS), (x, y))
        d.rectangle((x - 1, y - 1, x + vw, y + vh), outline=(200, 204, 210))
        d.text((x, y + vh + 8), name.split("_")[0], fill=(10, 10, 10), font=font)
    sheet.save(path)


def main() -> None:
    frames = {ratio: build_frames(ratio) for ratio in SPECS}
    for ratio, items in frames.items():
        folder = OUT / "khung" / ratio
        folder.mkdir(parents=True, exist_ok=True)
        for name, im in items:
            im.save(folder / f"{name}.png")
    ref_dir = OUT / "tham-chieu"
    ref_dir.mkdir(parents=True, exist_ok=True)
    refs = build_references()
    for name, im in refs:
        im.save(ref_dir / f"{name}.png")
    contact_sheet(frames, OUT / "tong-quan-khung.png")
    print(f"Đã dựng {sum(len(v) for v in frames.values())} khung + {len(refs)} ảnh tham chiếu vào {OUT}")


if __name__ == "__main__":
    main()
