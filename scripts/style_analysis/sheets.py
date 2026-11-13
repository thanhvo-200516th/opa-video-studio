"""Ảnh lưới: 1 khung/giây, nhãn thời gian, 4 cột x 3 hàng (12 giây/ảnh). sheets/<id>_NN.jpg"""
import os, subprocess, sys, glob, json
from PIL import Image, ImageDraw, ImageFont
vid_dir, out_dir, fps = sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
FF = "/home/vmiz/.local/bin/ffmpeg"
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
W, H, C, R = 300, 533, 4, 3
for f in sorted(glob.glob(os.path.join(vid_dir, "*.mp4"))):
    vid = os.path.basename(f)[:-4]; tmp = os.path.join(out_dir, "_f_" + vid); os.makedirs(tmp, exist_ok=True)
    subprocess.run([FF, "-v", "error", "-y", "-i", f, "-vf", f"fps={fps},scale={W}:{H}", os.path.join(tmp, "%04d.jpg")], check=True)
    frames = sorted(glob.glob(os.path.join(tmp, "*.jpg")))
    per = C * R
    for si in range(0, len(frames), per):
        sheet = Image.new("RGB", (C * W, R * (H + 28)), (40, 40, 40)); d = ImageDraw.Draw(sheet)
        for k, fp in enumerate(frames[si:si + per]):
            x, y = (k % C) * W, (k // C) * (H + 28)
            sheet.paste(Image.open(fp), (x, y + 28))
            t = (si + k) / fps + 0.5 / fps
            d.text((x + 6, y + 2), f"t={t:.1f}s", fill=(255, 230, 0), font=font)
        sheet.save(os.path.join(out_dir, f"{vid}_{si // per + 1:02d}.jpg"), quality=85)
    for fp in frames: os.remove(fp)
    os.rmdir(tmp)
    print(vid, len(frames), "frames ->", -(-len(frames) // per), "sheets")
