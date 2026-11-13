"""Tờ contact có nhãn giờ từ MP4: một ô mỗi BUOC giây, 6 ô một hàng (ảnh bàn giao).

Chạy: python -I tools/to_contact.py <mp4> <png> [bước giây, mặc định 1]
"""
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

FONT = "/home/vmiz/Thanh/Media/TNEDIT/01_Font/Google_Fonts_PR/BeVietnamPro-Bold.ttf"
TW, TH, COLS, PAD, BAR = 480, 270, 6, 8, 34


def main() -> None:
    src, out = sys.argv[1], sys.argv[2]
    step = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                               capture_output=True, text=True).stdout.strip())
    times = [round(k * step, 3) for k in range(int(dur / step + 1e-6))]
    rows = (len(times) + COLS - 1) // COLS
    sheet = Image.new("RGB", (PAD + COLS * (TW + PAD), PAD + rows * (TH + BAR + PAD)), (226, 232, 240))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(FONT, 20)
    for k, t in enumerate(times):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", src, "-frames:v", "1", "-vf",
                              f"scale={TW}:{TH}:flags=area,format=rgb24", "-f", "rawvideo", "-"], capture_output=True).stdout
        img = Image.frombytes("RGB", (TW, TH), raw)
        x, y = PAD + (k % COLS) * (TW + PAD), PAD + (k // COLS) * (TH + BAR + PAD)
        d.text((x + 2, y + 6), f"{t:.1f} s · khung {round(t * 30)}".replace(".", ","), font=font, fill=(10, 10, 10))
        sheet.paste(img, (x, y + BAR))
    sheet.save(out)
    print("OK", out, len(times), "ô")


if __name__ == "__main__":
    main()
