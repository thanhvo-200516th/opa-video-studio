"""Đồ hoạ PNG 1080×1920 trong suốt cho các hiệu ứng chữ cần hình (vẽ bằng PIL, dấu tiếng Việt đúng).

Mọi hàm ghi file vào `out_dir` và trả về đường dẫn tuyệt đối (str). Toạ độ theo khung 1080×1920.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
WHITE, DARK = (255, 255, 255, 255), (18, 18, 18, 255)


def _canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def _rgba(hex_: str, a: int = 255) -> tuple:
    h = hex_.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def _save(im: Image.Image, out_dir: Path, name: str) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"{name}.png"
    im.save(p)
    return str(p.resolve())


def select_box(out_dir: Path, name: str, cx: int, cy: int, w: int, h: int) -> str:
    """Khung chọn chữ kiểu phần mềm dựng: viền mảnh + 8 tay nắm vuông + chấm xoay phía dưới (B19)."""
    im, d = _canvas()
    x0, y0, x1, y1 = cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2
    d.rectangle([x0, y0, x1, y1], outline=(255, 255, 255, 235), width=3)
    for hx in (x0, cx, x1):
        for hy in (y0, cy, y1):
            if (hx, hy) != (cx, cy):
                d.rectangle([hx - 9, hy - 9, hx + 9, hy + 9], fill=WHITE, outline=DARK, width=2)
    d.line([cx, y1 + 9, cx, y1 + 30], fill=(255, 255, 255, 200), width=3)
    d.ellipse([cx - 7, y1 + 30, cx + 7, y1 + 44], fill=WHITE, outline=DARK, width=2)
    return _save(im, out_dir, name)


def strike_bar(out_dir: Path, name: str, cx: int, cy: int, w: int, color: str = "#E8203A", thick: int = 10,
               glow: bool = True) -> str:
    """Vạch gạch ngang chữ (B23 phủ định); glow cùng màu nếu glow=True."""
    im, d = _canvas()
    d.rounded_rectangle([cx - w // 2, cy - thick // 2, cx + w // 2, cy + thick // 2], radius=thick // 2, fill=_rgba(color))
    if glow:
        g = im.filter(ImageFilter.GaussianBlur(10))
        im = Image.alpha_composite(g, im)
    return _save(im, out_dir, name)


def bookmark(out_dir: Path, name: str, x: int, y: int, size: int = 70, fill: str = "#888888", cursor: bool = False) -> str:
    """Icon bookmark (xám hoặc màu nhấn) + con trỏ chuột tuỳ chọn, góc trên-trái tại (x, y) (B7, B22)."""
    im, d = _canvas()
    w, h = size, round(size * 1.3)
    d.polygon([(x, y), (x + w, y), (x + w, y + h), (x + w / 2, y + h * 0.72), (x, y + h)], fill=_rgba(fill), outline=WHITE)
    if cursor:
        cx, cy, s = x + w * 0.6, y + h * 0.55, size / 70
        pts = [(0, 0), (40, 28), (21, 31), (31, 54), (22, 58), (12, 35), (0, 48)]
        d.polygon([(cx + px * s, cy + py * s) for px, py in pts], fill=WHITE, outline=(0, 0, 0, 255))
    return _save(im, out_dir, name)


def pill(out_dir: Path, name: str, text: str, font_file: str, cx: int, cy: int, size: int = 40,
         fill: str = "#3E7F69", alpha: int = 150, icon: str = "") -> str:
    """Pill kính bo tròn bán trong suốt chứa chữ trắng (B20). Lộ dần bằng chuyển cảnh linear_wipe."""
    im, d = _canvas()
    f = ImageFont.truetype(font_file, size)
    tw = d.textlength(text, font=f)
    pad = size * 0.7
    w = tw + pad * 2 + (size * 1.2 if icon else 0)
    h = size * 1.8
    x0, y0 = cx - w / 2, cy - h / 2
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=h / 2, fill=_rgba(fill, alpha), outline=(200, 240, 225, 110), width=2)
    d.text((x0 + pad, cy), text, font=f, fill=WHITE, anchor="lm")
    if icon:
        d.text((x0 + w - pad * 0.6, cy), icon, font=f, fill=WHITE, anchor="rm")
    return _save(im, out_dir, name)


def gradient_text(out_dir: Path, name: str, text: str, font_file: str, size: int, cx: int, baseline: int,
                  colors: list[str], angle: float = 90, shadow: bool = True) -> str:
    """Chữ tô gradient (B18) — vẽ thành PNG để đúng màu và dấu; colors 2–3 mã hex, angle 90 = ngang, 0 = dọc."""
    f = ImageFont.truetype(font_file, size)
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.text((cx, baseline), text, font=f, fill=255, anchor="ms")
    box = mask.getbbox() or (0, 0, W, H)
    grad = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(grad)
    x0, y0, x1, y1 = box
    n = len(colors) - 1
    horizontal = abs(math.cos(math.radians(angle))) < 0.5
    span = (x1 - x0) if horizontal else (y1 - y0)
    for i in range(max(1, span)):
        t = i / max(1, span - 1)
        k = min(n - 1, int(t * n))
        u = t * n - k
        c0, c1 = _rgba(colors[k]), _rgba(colors[k + 1])
        col = tuple(round(c0[j] + (c1[j] - c0[j]) * u) for j in range(4))
        if horizontal:
            gd.line([(x0 + i, 0), (x0 + i, H)], fill=col)
        else:
            gd.line([(0, y0 + i), (W, y0 + i)], fill=col)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sh.putalpha(mask.point(lambda v: v * 0.55))
        sh = sh.filter(ImageFilter.GaussianBlur(8))
        out = Image.alpha_composite(out, sh.transform((W, H), Image.AFFINE, (1, 0, 0, 0, 1, -6)))
    grad.putalpha(mask)
    return _save(Image.alpha_composite(out, grad), out_dir, name)


def curved_text(out_dir: Path, name: str, text: str, font_file: str, size: int, cx: int, cy: int, radius: int,
                start_deg: float = 200, end_deg: float = 340, ring: bool = True, ring_color: str = "#D9B8FF") -> str:
    """Chữ chạy theo cung tròn dưới một vòng tròn (B23 chữ cong). Góc tính theo độ, 0° = bên phải, chiều kim đồng hồ."""
    im, d = _canvas()
    f = ImageFont.truetype(font_file, size)
    if ring:
        r0 = radius - size * 1.4
        d.ellipse([cx - r0, cy - r0, cx + r0, cy + r0], outline=_rgba(ring_color), width=6)
    total = sum(d.textlength(ch, font=f) for ch in text)
    arc = math.radians(end_deg - start_deg)
    scale = (radius * arc) / max(1, total)
    ang = math.radians(start_deg)
    for ch in text:
        cw = d.textlength(ch, font=f) * scale
        mid = ang + (cw / 2) / radius
        tile = Image.new("RGBA", (size * 3, size * 3), (0, 0, 0, 0))
        ImageDraw.Draw(tile).text((size * 1.5, size * 1.5), ch, font=f, fill=WHITE, anchor="mm")
        tile = tile.rotate(math.degrees(mid) - 270, resample=Image.BICUBIC)   # đỉnh chữ hướng về tâm vòng
        x, y = cx + radius * math.cos(mid), cy - radius * math.sin(mid)        # góc toán học → toạ độ màn hình
        im.alpha_composite(tile, (round(x - size * 1.5), round(y - size * 1.5)))
        ang += cw / radius
    return _save(im, out_dir, name)


def caption_band(out_dir: Path, name: str, y0: int, y1: int, strength: float = 0.5, feather: int = 110) -> str:
    """Dải tối mềm ngay sau vùng phụ đề (y0–y1): đậm `strength` ở giữa, mờ dần `feather` px trên/dưới và về hai mép
    — tăng tương phản phụ đề mà không phủ cả khung (vignette đáy chỉ đậm 15–27% ở vùng phụ đề, 2026-11-04)."""
    import numpy as np
    ys = np.arange(H, dtype=np.float32)
    v = np.clip(np.minimum((ys - (y0 - feather)) / feather, ((y1 + feather) - ys) / feather), 0, 1)
    xs = np.arange(W, dtype=np.float32)
    h = np.clip(np.minimum(xs / 160, (W - xs) / 160), 0, 1) * 0.35 + 0.65       # mép trái/phải nhạt hơn 35%
    alpha = (np.outer(v * v * (3 - 2 * v), h) * 255 * strength).astype(np.uint8)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    im.putalpha(Image.fromarray(alpha, "L"))
    return _save(im, out_dir, name)


def solid_panel(out_dir: Path, name: str, color: str) -> str:
    """Tấm màu đặc phủ kín khung (chuyển cảnh panel_wipe)."""
    return _save(Image.new("RGBA", (W, H), _rgba(color)), out_dir, name)


# ---------- hồ sơ minimal-edu (C1): nền giấy, hộp tô, quote card, polaroid, lưới đồ thị ----------
# Màu / số đo lấy từ references/minimal-edu-style.json (style_profile); hàm chỉ chạy khi được gọi — hồ sơ tắt thì không ai gọi.
def _prof() -> dict:
    from style_profile import load
    return load(name="minimal-edu")


def _gfx(key: str):
    return _prof()["graphics"][key]


def _rgb(hex_: str):
    import numpy as np
    return np.array(_rgba(hex_)[:3], dtype=np.float32)


def _smooth_noise(rng, cells: tuple[int, int]):
    """Mây mềm: nhiễu độ phân giải thấp phóng bicubic lên khung 1080×1920, giá trị ~[-1, 1]."""
    import numpy as np
    small = Image.fromarray((rng.random(cells[::-1]) * 255).astype(np.uint8), "L")
    return (np.asarray(small.resize((W, H), Image.BICUBIC), dtype=np.float32) - 127.5) / 127.5


def _halftone(pitch: int = 16, reach: float = 0.42):
    """Mặt nạ chấm halftone lưới xoay 45°, chấm to dần về 4 góc (0 → 1), mép chấm mềm 1 px."""
    import numpy as np
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    u, v = (xs + ys) / 1.4142, (ys - xs) / 1.4142
    cu, cv = (np.floor(u / pitch) + 0.5) * pitch, (np.floor(v / pitch) + 0.5) * pitch
    d = np.hypot(u - cu, v - cv)
    dc = np.minimum.reduce([np.hypot(xs - x, ys - y) for x in (0, W) for y in (0, H)])
    r = pitch * 0.62 * np.clip(1 - dc / (reach * W), 0, 1)
    return np.clip(r - d + 0.5, 0, 1)


def paper_bg(out_dir: Path, name: str, kind: str = "white", seed: int = 0) -> str:
    """Nền 1080×1920 đặc: kind 'white' (giấy #E8E8F0, chấm halftone dày ở góc) | 'black' (nền đen noise) | 'blue' (cobalt
    vải thô). Noise hạt + mây mềm + chấm halftone ở góc; cùng seed → cùng ảnh."""
    import numpy as np
    prof = _prof()
    base = {"white": prof["graphics"]["paper_white"], "black": prof["text"]["colors"]["on_paper"],
            "blue": prof["text"]["colors"]["accent"]}.get(kind)
    if base is None:
        raise ValueError(f"kind nền lạ: {kind} (chỉ white | black | blue)")
    rng = np.random.default_rng(seed)
    light = kind == "white"
    grain = rng.normal(0, 5.0 if light else 4.0, (H, W, 1)).astype(np.float32)
    if kind == "blue":                                     # vải thô: sợi ngang + dọc
        grain += (_smooth_noise(rng, (540, 1))[..., None] + _smooth_noise(rng, (1, 960))[..., None]) * 3.0
    cloud = _smooth_noise(rng, (6, 10))[..., None] * (7.0 if light else 5.0)
    dots = _halftone()[..., None]
    shade = dots * (-0.16 * _rgb(base) if light else 26.0)
    img = np.clip(_rgb(base) + grain + cloud + shade, 0, 255).astype(np.uint8)
    return _save(Image.fromarray(img, "RGB").convert("RGBA"), out_dir, name)


def torn_paper(out_dir: Path, name: str, half: str = "top", seed: int = 0) -> str:
    """Nửa giấy rách 1080×1920 (chuyển cảnh paper_rip): nền `paper_bg` trắng giữ phần trên ('top') hoặc dưới ('bottom') của đường rách
    quanh y = 960 (sóng chậm ±70 px + răng cưa 5 px); mép có dải xơ giấy sáng ~9 px, lỗ lác đác. Cùng seed → hai nửa khớp nhau."""
    import numpy as np
    if half not in ("top", "bottom"):
        raise ValueError(f"half lạ: {half} (top | bottom)")
    rgba = np.asarray(Image.open(paper_bg(out_dir, f"{name}_src", "white", seed)).convert("RGBA"), dtype=np.float32)
    rng = np.random.default_rng(seed + 11)
    line = H / 2 + np.interp(np.arange(W), np.linspace(0, W, 14), rng.uniform(-70, 70, 14)) + rng.normal(0, 5, W)
    ys = np.arange(H, dtype=np.float32)[:, None]
    inside = (line[None, :] - ys) if half == "top" else (ys - line[None, :])      # > 0: phía được giữ lại
    edge = np.clip(1 - inside / 9.0, 0, 1) * (inside > 0)
    rgba[..., :3] = rgba[..., :3] * (1 - 0.75 * edge[..., None]) + 255 * 0.75 * edge[..., None]
    rgba[..., 3] = np.where((inside > 0) & ~((edge > 0.5) & (rng.random((H, W)) > 0.8)), 255, 0)
    return _save(Image.fromarray(rgba.astype(np.uint8), "RGBA"), out_dir, name)


def box_fill(out_dir: Path, name: str, w: int, h: int, color: str | None = None, radius: int = 24) -> str:
    """Hộp bo góc tô đặc kích thước w×h (khít, không phải khung 1080×1920) — đặt bằng motion.position, lộ bằng box_wipe."""
    k = 4                                                  # siêu mẫu 4× cho mép bo mượt
    big = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    ImageDraw.Draw(big).rounded_rectangle([0, 0, w * k - 1, h * k - 1], radius=radius * k, fill=_rgba(color or _gfx("accent_line")))
    return _save(big.resize((w, h), Image.LANCZOS), out_dir, name)


def quote_card(out_dir: Path, name: str, inner: str | None = None, outer: str | None = None) -> str:
    """Nền thẻ trích dẫn 1080×1920: gradient radial, tâm `inner` → góc `outer` (đầu sáng chưa xác nhận — giả định tâm sáng)."""
    import numpy as np
    qc = _gfx("quote_card")
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    t = np.clip(np.hypot((xs - W / 2) / (W / 2), (ys - H / 2) / (H / 2)) / 1.4142, 0, 1)[..., None]
    c0, c1 = _rgb(inner or qc["inner"]), _rgb(outer or qc["outer"])
    return _save(Image.fromarray((c0 + (c1 - c0) * t).astype(np.uint8), "RGB").convert("RGBA"), out_dir, name)


def polaroid(out_dir: Path, name: str, photo_path: str, tilt: float = 0.0, width: int = 760) -> str:
    """Khung polaroid (viền trắng, đáy dày) quanh ảnh vuông cắt giữa, bóng đổ mềm, nền trong suốt. tilt = độ nghiêng nướng
    vào PNG (0 nếu để polaroid_pop xoay bằng keyframe)."""
    border, strip, pad = 36, 150, 90
    inner = width - 2 * border
    photo = Image.open(photo_path).convert("RGB")
    s = min(photo.size)
    photo = photo.crop(((photo.width - s) // 2, (photo.height - s) // 2, (photo.width + s) // 2, (photo.height + s) // 2))
    frame = Image.new("RGBA", (width, border + inner + strip), (246, 244, 238, 255))
    frame.paste(photo.resize((inner, inner), Image.LANCZOS), (border, border))
    card = Image.new("RGBA", (frame.width + 2 * pad, frame.height + 2 * pad), (0, 0, 0, 0))
    shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 120), (pad, pad + 18, pad + frame.width, pad + 18 + frame.height))
    card = Image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(20)), card)
    card.alpha_composite(frame, (pad, pad))
    if tilt:
        card = card.rotate(tilt, resample=Image.BICUBIC, expand=True)
    return _save(card, out_dir, name)


def graph_grid(out_dir: Path, name: str, step: int = 120) -> str:
    """Lưới trắng mảnh phát sáng (đồ thị trên nền tối), trong suốt 1080×1920."""
    im, d = _canvas()
    for x in range(step // 2, W, step):
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 190), width=2)
    for y in range(step // 2, H, step):
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 190), width=2)
    return _save(Image.alpha_composite(im.filter(ImageFilter.GaussianBlur(5)), im), out_dir, name)


def paint_texture(out_dir: Path, name: str, src: str, strength: float) -> str:
    """Nướng texture sơn / vải vào ảnh tranh (dính ảnh nên "chạy theo tranh"). strength 0–1, tối đa
    graphics.painting_texture_max (0,5: bản nặng bị chê). Giữ nguyên kích thước và kênh alpha."""
    import numpy as np
    cap = _gfx("painting_texture_max")
    if not 0 <= strength <= cap:
        raise ValueError(f"texture_strength {strength} ngoài 0–{cap} (texture sơn nặng bị chê)")
    im = Image.open(src).convert("RGBA")
    rng = np.random.default_rng(zlib_seed(src))
    w, h = im.size
    fine = rng.normal(0, 1, (h, w)).astype(np.float32)
    coarse = np.asarray(Image.fromarray((rng.random((max(2, h // 24), max(2, w // 24))) * 255).astype(np.uint8), "L")
                        .resize((w, h), Image.BICUBIC), dtype=np.float32) / 127.5 - 1
    tex = (0.6 * np.clip(fine, -2, 2) / 2 + 0.4 * coarse)[..., None]
    a = np.asarray(im, dtype=np.float32)
    a[..., :3] = np.clip(a[..., :3] + tex * strength * 70, 0, 255)
    return _save(Image.fromarray(a.astype(np.uint8), "RGBA"), out_dir, name)


def zlib_seed(s: str) -> int:
    import zlib
    return zlib.crc32(s.encode())


# ---------- cảnh minimal-edu thêm (v3.6.6): tranh trôi texture, minh hoạ loang mép, hình bên ----------
# Số đo chưa có trong hồ sơ (ghi chú profile key); đã chỉnh bằng khung hình thật trong .handoff/v366/scene_proof/.
ROUGH_MEAN = {"paper": 214.0, "paint": 206.0}   # profile key: graphics.rough_texture_mean — độ sáng nền texture (multiply)
ROUGH_AMP = {"paper": (16.0, 12.0, 14.0, 0.0), "paint": (26.0, 20.0, 10.0, 22.0)}   # profile key: graphics.rough_texture_amp — mây thô, mây vừa, hạt, vệt cọ


def cover_image(out_dir: Path, name: str, src: str, size: tuple[int, int] = (W, H)) -> str:
    """Cắt giữa + phóng cho phủ kín `size` (mặc định cả khung 1080×1920); giữ kênh alpha nếu ảnh có."""
    im = Image.open(src).convert("RGBA")
    k = max(size[0] / im.width, size[1] / im.height)
    im = im.resize((max(size[0], round(im.width * k)), max(size[1], round(im.height * k))), Image.LANCZOS)
    x, y = (im.width - size[0]) // 2, (im.height - size[1]) // 2
    return _save(im.crop((x, y, x + size[0], y + size[1])), out_dir, name)


def rough_texture(out_dir: Path, name: str, seed: int = 0, kind: str = "paper") -> str:
    """Lớp texture thô 1080×1920 đặc, sáng (~210/255) để phủ bằng blend multiply ≤ 50 %: mây thô + mây vừa + hạt, kind 'paint'
    thêm vệt cọ dọc. Trôi chậm bằng motion.position (cảnh tranh: hai lớp trôi ngược chiều, phóng ≥ 108 % để không lộ mép)."""
    import numpy as np
    if kind not in ROUGH_MEAN:
        raise ValueError(f"kind texture lạ: {kind} (chỉ {sorted(ROUGH_MEAN)})")
    rng = np.random.default_rng(seed)
    a_coarse, a_mid, a_grain, a_streak = ROUGH_AMP[kind]
    v = ROUGH_MEAN[kind] + _smooth_noise(rng, (5, 9)) * a_coarse + _smooth_noise(rng, (16, 28)) * a_mid
    v = v + rng.normal(0, 1, (H, W)).astype(np.float32) * a_grain / 2
    if a_streak:
        v = v + _smooth_noise(rng, (60, 3)) * a_streak * 0.6 + _smooth_noise(rng, (120, 6)) * a_streak * 0.4
    g = np.clip(v, 0, 255).astype(np.uint8)
    return _save(Image.fromarray(np.stack([g, g, g], -1), "RGB").convert("RGBA"), out_dir, name)


def _edge_alpha(size: tuple[int, int], edges: tuple, feather: int, seed: int):
    """Alpha 0..1 mềm ở các mép `edges` (top|bottom|left|right): khoảng cách tới mép / feather, nhiễu thấp tần làm mép loang như
    sơn thấm giấy (không thẳng), một lớp hạt mịn làm mép lốm đốm."""
    import numpy as np
    w, h = size
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    dist = {"top": ys, "bottom": h - 1 - ys, "left": xs, "right": w - 1 - xs}
    rng = np.random.default_rng(seed)
    nz = np.asarray(Image.fromarray((rng.random((max(2, h // 22), max(2, w // 22))) * 255).astype(np.uint8), "L")
                    .resize((w, h), Image.BICUBIC), dtype=np.float32) / 255 - 0.5
    grain = np.asarray(Image.fromarray((rng.random((h // 4, w // 4)) * 255).astype(np.uint8), "L").resize((w, h), Image.BILINEAR),
                       dtype=np.float32) / 255 - 0.5
    a = np.ones((h, w), np.float32)
    for e in edges:
        t = np.clip((dist[e] - feather * 0.3 * (nz * 0.9 + 0.5 + grain * 0.3)) / (feather * 0.7), 0, 1)   # 0 đúng ở mép, ranh giới loang lệch vào trong
        a = np.minimum(a, t * t * (3 - 2 * t))
    return a


def bleed_image(out_dir: Path, name: str, src: str, size: tuple[int, int] = (W, 1250), edges: tuple = ("top", "left", "right"),
                feather: int = 170, seed: int = 0) -> str:
    """Minh hoạ loang vào giấy (nguyên tắc 7): ảnh phủ kín `size`, nền alpha mềm + nhiễu ở các mép `edges` (mép khác tràn khung).
    Đặt lên giấy bằng blend multiply thì vùng trắng của tranh tan vào giấy."""
    import numpy as np
    base = Image.open(cover_image(out_dir, f"{name}_cover", src, size)).convert("RGBA")
    a = _edge_alpha(size, edges, feather, seed) * (np.asarray(base)[..., 3] / 255)
    base.putalpha(Image.fromarray((a * 255).astype(np.uint8), "L"))
    return _save(base, out_dir, name)


def side_figure(out_dir: Path, name: str, src: str, side: str = "left", size: tuple[int, int] = (620, 1300), feather: int = 110,
                strength: float = 0.3, seed: int = 0) -> str:
    """Hình trừu tượng một bên (nguyên tắc 8): ảnh phủ kín `size`, mép phía trong loang vào giấy, mép ngoài sát cạnh khung, nướng texture
    sơn `strength` (≤ graphics.painting_texture_max)."""
    if side not in ("left", "right"):
        raise ValueError(f"side lạ: {side} (left | right)")
    inner = "right" if side == "left" else "left"
    img = Image.open(bleed_image(out_dir, f"{name}_bleed", src, size, ("top", "bottom", inner), feather, seed))
    tmp = _save(img, out_dir, f"{name}_pre")
    return _save(Image.open(paint_texture(out_dir, f"{name}_tx", tmp, strength)), out_dir, name)
