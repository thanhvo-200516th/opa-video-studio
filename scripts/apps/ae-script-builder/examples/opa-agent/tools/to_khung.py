"""Ghép tờ "khung đã hiện đủ" 5 cảnh (ảnh trích từ MP4 bản dựng) có nhãn tiếng Việt.

Chạy: python -I tools/to_khung.py out/review v05
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = "/home/vmiz/Thanh/Media/TNEDIT/01_Font/Google_Fonts_PR/BeVietnamPro-Bold.ttf"
LABELS = {
    "S1": "Cảnh 1 · 0–5 s · Hook (khung 3,5 s)",
    "S2": "Cảnh 2 · 5–13,5 s · Nỗi đau (khung 12,0 s)",
    "S3": "Cảnh 3 · 13,5–22 s · Giải pháp (khung 20,6 s)",
    "S4": "Cảnh 4 · 22–30 s · Giải phóng (khung 28,4 s)",
    "S5": "Cảnh 5 · 30–36 s · CTA (khung 35,6 s)",
}


def main() -> None:
    folder, ver = Path(sys.argv[1]), sys.argv[2]
    tw, th, pad, bar = 960, 540, 16, 54
    sheet = Image.new("RGB", (pad + 2 * (tw + pad), pad + 3 * (th + bar + pad)), (226, 232, 240))
    font = ImageFont.truetype(FONT, 28)
    d = ImageDraw.Draw(sheet)
    for k, key in enumerate(LABELS):
        img = Image.open(folder / f"hero_{key}_{ver}.png").convert("RGB").resize((tw, th), Image.LANCZOS)
        col, row = k % 2, k // 2
        x, y = pad + col * (tw + pad), pad + row * (th + bar + pad)
        d.text((x + 4, y + 10), LABELS[key], font=font, fill=(10, 10, 10))
        sheet.paste(img, (x, y + bar))
    out = folder / f"KHUNG-HIEN-DU_{ver}.png"
    sheet.save(out)
    print("OK", out)


if __name__ == "__main__":
    main()
