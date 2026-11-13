#!/usr/bin/env python3
"""studio_plate — dựng nền studio 1080x1920 (luật D12) từ ảnh phòng KHÔNG NGƯỜI do người dùng gửi.

    ~/.venvs/video-skills/bin/python studio_plate.py fit REF.png OUT.png [--flip]          # phòng trống: cắt viền bo góc, phóng, làm mờ nhẹ, thêm hạt
    ~/.venvs/video-skills/bin/python studio_plate.py nochair REF.png OUT.png [--flip]       # phòng podcast ghế bành: xoá ghế, giữ rèm / cây / mic / thảm
    ~/.venvs/video-skills/bin/python studio_plate.py curtain REF.png OUT.png [--flip]       # lấy dải rèm phía trên một ảnh có người (chỉ phần rèm)
    ~/.venvs/video-skills/bin/python studio_plate.py dark OUT.png                           # nền tối đồng nhất có quầng sáng giữa (ảnh studio tối)

`nochair` dùng đa giác ghế đo trên ảnh mẫu `Nen_Background/Phong_Studio_Podcast/ref/phong_podcast_ghe_banh.png` (213x402 sau khi cắt 9 px viền):
tường kéo dài từ nếp rèm phía trên ghế, thảm nội suy từ thảm xung quanh + hạt thảm lấy từ vùng sạch bên dưới. Ảnh mẫu rất nhỏ (~240 px) nên nền mềm,
phù hợp nền mờ phía sau người. Nền tạo từ code thuần (gradient + bokeh + lá giả) bị chê "phèn" 2026-11-12 — không dùng nữa.
"""
import sys

import cv2
import numpy as np

W, H = 1080, 1920
POLY = np.array([(8, 238), (25, 222), (60, 211), (110, 205), (150, 208), (176, 220), (180, 245), (178, 285), (172, 318), (160, 332),
                 (160, 347), (120, 357), (60, 352), (36, 338), (24, 310), (14, 285)], np.int32)
GRAIN = np.random.default_rng(7)


def _crop(im: np.ndarray) -> np.ndarray:
    h, w = im.shape[:2]
    return im[9:h - 9, 9:w - 9].copy()


def _finish(img: np.ndarray, flip: bool, blur: float = 2.5) -> np.ndarray:
    h, w = img.shape[:2]
    big = cv2.resize(img, (W, int(h * W / w)), interpolation=cv2.INTER_CUBIC)
    if big.shape[0] < H:
        big = cv2.copyMakeBorder(big, 0, H - big.shape[0], 0, 0, cv2.BORDER_REPLICATE)
    big = cv2.GaussianBlur(big[:H], (0, 0), blur)
    if flip:
        big = np.ascontiguousarray(big[:, ::-1])
    return np.clip(big.astype(np.float32) + GRAIN.normal(0, 2.0, (H, W))[..., None], 0, 255).astype(np.uint8)


def nochair(im: np.ndarray) -> np.ndarray:
    h, w = im.shape[:2]
    yc = 296
    m = np.zeros((h, w), np.uint8)
    cv2.fillPoly(m, [POLY], 255)
    m = cv2.dilate(m, np.ones((7, 7), np.uint8))
    f = im.astype(np.float32).copy()
    for x in range(w):
        col = np.where(m[:, x] > 0)[0]
        if not len(col):
            continue
        yt = int(col.min())
        ref = im[150:156, x].astype(np.float32).mean(0) if 88 <= x <= 132 else im[max(0, yt - 7):max(1, yt - 3), x].astype(np.float32).mean(0)
        for y in col:
            if y < yc:
                f[y, x] = ref * (1 + 0.35 * (y - yt) / max(1, yc - yt))
    f = cv2.GaussianBlur(f, (0, 0), sigmaX=0.8, sigmaY=3.0)
    mw = m.copy()
    mw[yc:] = 0
    mfw = cv2.GaussianBlur(mw.astype(np.float32) / 255, (0, 0), 2.5)[..., None]
    wall = (im.astype(np.float32) * (1 - mfw) + f * mfw).astype(np.uint8)
    mc = m.copy()
    mc[:yc] = 0
    ref = wall.copy()
    ref[mc > 0] = 0
    smooth = cv2.GaussianBlur(ref.astype(np.float32), (0, 0), 14) / (cv2.GaussianBlur((mc == 0).astype(np.float32), (0, 0), 14)[..., None] + 1e-3)
    tex = np.roll(im.astype(np.float32) - cv2.GaussianBlur(im.astype(np.float32), (0, 0), 2.5), -62, axis=0)
    mf = cv2.GaussianBlur(mc.astype(np.float32) / 255, (0, 0), 3.2)[..., None]
    return np.clip(wall.astype(np.float32) * (1 - mf) + (smooth * 0.97 + tex * 0.5) * mf, 0, 255).astype(np.uint8)


def curtain(im: np.ndarray) -> np.ndarray:
    gh, gw = im.shape[:2]
    band = im[int(gh * 0.045):int(gh * 0.245), int(gw * 0.04):int(gw * 0.96)]
    c = cv2.resize(band, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    c = 0.45 * cv2.GaussianBlur(c, (0, 0), sigmaX=3.5, sigmaY=20) + 0.55 * cv2.GaussianBlur(c, (0, 0), 40)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    glow = np.exp(-(((xx - W / 2) / 700) ** 2 + ((yy - H * 0.5) / 900) ** 2))[..., None]
    return np.clip(c * (0.8 + 0.5 * glow) * (1 - 0.2 * (yy / H)[..., None] ** 2) * np.array([1.0, 1.05, 1.1], np.float32), 0, 255).astype(np.uint8)


def dark() -> np.ndarray:
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    sp = np.exp(-(((xx - W * 0.5) / 520) ** 2 + ((yy - H * 0.42) / 760) ** 2))[..., None]
    d = np.ones((H, W, 3), np.float32) * np.array([34, 33, 32], np.float32)
    return np.clip(d * (0.35 + 0.85 * sp) + sp * np.array([6, 4, 2], np.float32), 0, 255).astype(np.uint8)


def main() -> None:
    mode = sys.argv[1]
    flip = "--flip" in sys.argv
    args = [a for a in sys.argv[2:] if a != "--flip"]
    if mode == "dark":
        out = _finish(dark(), flip, 0.1)
        cv2.imwrite(args[0], out)
        return
    im = cv2.imread(args[0])
    if mode == "fit":
        out = _finish(_crop(im), flip)
    elif mode == "nochair":
        out = _finish(nochair(_crop(im)), flip)
    elif mode == "curtain":
        out = np.clip(curtain(im).astype(np.float32) + GRAIN.normal(0, 2.0, (H, W))[..., None], 0, 255).astype(np.uint8)
        out = np.ascontiguousarray(out[:, ::-1]) if flip else out
    else:
        raise SystemExit(__doc__)
    cv2.imwrite(args[1], out)


if __name__ == "__main__":
    main()
