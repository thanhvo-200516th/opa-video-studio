# Tach chu OPA tu trang 3 PDF + do do khop dau bo sach voi dau trong PDF
import sys
import numpy as np
from PIL import Image
page, clean_png, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
im = np.asarray(Image.open(page).convert("RGB")).astype(np.float32)

def alpha_from_blue(rgb):
    # nen trang R=255, xanh #0068FF R=0 -> alpha = 1 - R/255
    a = 1.0 - rgb[..., 0] / 255.0
    a[a < 0.06] = 0; a[a > 0.94] = 1
    return a

# --- cum logo nen sang (o tren phai trang 3)
x0, y0 = 3300, 650
lock = im[y0:1150, x0:4700]
a = alpha_from_blue(lock)
cols = np.where(a.max(axis=0) > 0.5)[0]
# tim khe trong giua dau bo va chu
gaps = np.where(np.diff(cols) > 40)[0]
mark_x1 = cols[gaps[0]] + 1; word_x0 = cols[gaps[0] + 1]
def bbox(m):
    ys, xs = np.where(m > 0.5); return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
mb = bbox(a[:, :mark_x1]); wb = bbox(a[:, word_x0:]); wb = (wb[0] + word_x0, wb[1], wb[2] + word_x0, wb[3])
print("lockup mark bbox", mb, "word bbox", wb)
pad = 4
wa = a[wb[1]-pad:wb[3]+pad, wb[0]-pad:wb[2]+pad]
rgba = np.zeros(wa.shape + (4,), np.uint8); rgba[..., :3] = (0, 104, 255); rgba[..., 3] = (wa * 255).round()
Image.fromarray(rgba, "RGBA").save(f"{out_dir}/chu-OPA_tu-PDF-trang3.png")
open(f"{out_dir}/lockup-hinh-hoc.txt", "w").write(
    f"mark_bbox {tuple(map(int, mb))}\nword_bbox {tuple(map(int, wb))}\npad {pad}\n")

# --- do khop dau bo: dau lon o the trai trang 3
big = alpha_from_blue(im[550:2450, 300:2700])
bb = bbox(big); pm = big[bb[1]:bb[3], bb[0]:bb[2]] > 0.5
cl = np.asarray(Image.open(clean_png).convert("RGBA"))[..., 3]
cb = bbox(cl / 255.0)
cm = Image.fromarray(cl[cb[1]:cb[3], cb[0]:cb[2]]).resize((pm.shape[1], pm.shape[0]), Image.LANCZOS)
cm = np.asarray(cm) > 127
iou = (pm & cm).sum() / (pm | cm).sum()
print("PDF mark px", pm.shape, "ti le W/H pdf", pm.shape[1] / pm.shape[0], "sach", (cb[2]-cb[0]) / (cb[3]-cb[1]))
print("IoU dau sach vs PDF:", round(float(iou), 4), "| lech px:", int((pm ^ cm).sum()))
