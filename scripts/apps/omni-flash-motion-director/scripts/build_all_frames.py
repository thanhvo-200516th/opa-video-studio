# -*- coding: utf-8 -*-
"""
Script tổng hợp toàn bộ hệ thống Ảnh, Character Sheet & Storyboard Sản Xuất cho Kịch Bản Số 1 (VIDEO 01 - Ads #1 - 36s):
1. `00_CHARACTER_SHEET_BO_OPA`:
   - `CS01_BO_OPA_CHARACTER_RIG_SHEET.png` (Chuẩn hình học, 4 phần tách, Anchor Points không chồng lấp, 5 Poses)
   - `CS02_REF_BO_OPA_XANH_NEN_TRANG.png`
   - `CS03_REF_BO_OPA_TRANG_NEN_XANH.png`
   - `CS04_COMPONENT_3_BO_PHAN_BO_OPA_SACH.png`
   - `CS05_CHU_SHOP_CHARACTER_SHEET.png`
2. `00_STORYBOARD_SAN_XUAT` (Bộ Storyboard Đạo Diễn & Sản Xuất Video chỉnh chu):
   - `SB00_MASTER_DIRECTOR_STORYBOARD_30_FRAMES.png` (Toàn bộ 30 khung chuyển động từ 00:00 -> 00:36s + VO + SFX + AE Keyframe)
   - `SB01_STORYBOARD_PHAN_1_HOOK_VA_NOI_DAU.png` (Chi tiết Scene 1 & Scene 2 kèm Motion Arrows, VO, TOS, SFX, Camera, Keyframes)
   - `SB02_STORYBOARD_PHAN_2_GIAI_PHAP_BO_OPA_CHAT_3D_5_PILLS.png` (Chi tiết Scene 3A & Scene 3B kèm Motion Arrows)
   - `SB03_STORYBOARD_PHAN_3_GIAI_PHONG_VA_OUTRO_CTA.png` (Chi tiết Scene 4 & Scene 5 kèm Motion Arrows)
3. 6 Thư mục Timeline (`SCENE_01` -> `SCENE_05`):
   - `00_MASTER_BAO_QUAT_5s.png` (Ảnh bao quát 5s gộp 5 nhịp motion + 4 ảnh thành phần + thông số AE)
   - `F01_FIRST_FRAME_t0.0s.png` (Frame đầu 16:9 sạch cho Omni Flash)
   - `M02_MOTION_STEP_t1.25s.png` (Bước motion 2 16:9 sạch)
   - `M03_MOTION_STEP_t2.50s.png` (Bước motion 3 16:9 sạch)
   - `M04_MOTION_STEP_t3.75s.png` (Bước motion 4 16:9 sạch)
   - `F05_LAST_FRAME_t5.0s.png` (Frame cuối / Bao quát đích 16:9 sạch cho Omni Flash)
   - `F05_LAST_FRAME_CO_CHU_AE.png` (Bản đầy đủ Typography Tiếng Việt chuẩn After Effects)
   - `C01..C04_COMPONENT_*.png` (Các ảnh thành phần tách lẻ để nạp làm Reference/Ingredient vào Omni Flash)
"""

import json
import math
import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import resvg_py

ROOT = Path(r"/media/vmiz/Over Powers/THÀNH V/Motion Omi")
ASSETS = ROOT / "ASSETS"
OUT_DIR = ROOT / "ẢNH"
OUT_DIR.mkdir(parents=True, exist_ok=True)

AI_SCENE1_SRC = Path(r"C:\Users\Minh PC\.gemini\antigravity\brain\82b3e12e-06ba-465a-bf8c-3c4ddfcd9f3a\chu_shop_scene1_qua_tai_base_png_1792817695035.jpg")
AI_SCENE4_SRC = Path(r"C:\Users\Minh PC\.gemini\antigravity\brain\82b3e12e-06ba-465a-bf8c-3c4ddfcd9f3a\chu_shop_scene4_thanh_thoi_base_png_1792817718427.jpg")

AI_DIR = OUT_DIR / "00_NGUON_AI_CHU_SHOP"
AI_DIR.mkdir(parents=True, exist_ok=True)
if AI_SCENE1_SRC.exists():
    Image.open(AI_SCENE1_SRC).convert("RGB").resize((1920, 1080), Image.LANCZOS).save(AI_DIR / "chu_shop_scene1_qua_tai_base.png")
if AI_SCENE4_SRC.exists():
    Image.open(AI_SCENE4_SRC).convert("RGB").resize((1920, 1080), Image.LANCZOS).save(AI_DIR / "chu_shop_scene4_thanh_thoi_base.png")

FONT_BOLD_PATH = str(ASSETS / "FONTS" / "BeVietnamPro-ExtraBold.ttf")
FONT_MED_PATH = str(ASSETS / "FONTS" / "BeVietnamPro-Medium.ttf")
FONT_ACCENT_PATH = str(ASSETS / "FONTS" / "FrauncesOPA-ExtraBoldItalic.ttf")

def get_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", size)

# Màu chuẩn BRAND-SPEC.md + Template 5.aep
C_BLUE = (0, 104, 255)          # #0068FF - Xanh OPA chủ đạo
C_BLUE_COBALT = (30, 64, 255)   # #1E40FF - Xanh Cobalt UI
C_BLUE_GLOW = (38, 144, 255)    # #2690FF - Viền sáng EdgeGlow
C_BLUE_DARK = (0, 60, 153)      # #003C99 - Xanh đậm
C_BLUE_LIGHT = (230, 240, 255)  # #E6F0FF - Xanh nhạt
C_NAVY_BG = (10, 20, 46)        # #0A142E - Nền tối UI
C_NAVY_DEEP = (6, 12, 28)       # #060C1C - Nền đêm quá tải
C_WHITE = (255, 255, 255)       # #FFFFFF
C_DAY_BG = (244, 247, 255)      # #F4F7FF
C_BLACK = (10, 10, 10)          # #0A0A0A
C_ALERT = (229, 72, 77)         # #E5484D - Đỏ cảnh báo
C_ORANGE_MSG = (255, 122, 48)   # Cam Pancake
C_GREEN_OK = (16, 185, 129)     # #10B981 - Tích xanh thành công
C_GOLD = (255, 195, 50)         # Vàng chỉ dẫn Motion

GEO = json.loads((ASSETS / "MASCOT_GOC" / "geometry.json").read_text(encoding="utf-8"))
WORD_PNG = Image.open(ASSETS / "MASCOT_GOC" / "chu-OPA_tu-PDF-trang3.png").convert("RGBA")
WORD_PNG = WORD_PNG.crop(WORD_PNG.getchannel("A").getbbox())

def render_bo_opa_svg(height: int, color_hex: str = "#0068FF",
                      head_rot: float = 0.0,
                      horn_l_rot: float = 0.0,
                      horn_r_rot: float = 0.0,
                      part_mode: str = "full") -> Image.Image:
    muzzle_d = GEO["muzzle"]
    hl_d = GEO["hornLeft"]
    hr_d = GEO["hornRight"]
    pl = GEO["hornSpine"]["left"]["pivot"]
    pr = GEO["hornSpine"]["right"]["pivot"]

    parts_svg = []
    if part_mode in ("full", "muzzle"):
        parts_svg.append(f'<path d="{muzzle_d}" fill="{color_hex}"/>')
    if part_mode in ("full", "horn_l", "horns"):
        parts_svg.append(f'<path d="{hl_d}" fill="{color_hex}" transform="rotate({horn_l_rot} {pl[0]} {pl[1]})"/>')
    if part_mode in ("full", "horn_r", "horns"):
        parts_svg.append(f'<path d="{hr_d}" fill="{color_hex}" transform="rotate({horn_r_rot} {pr[0]} {pr[1]})"/>')
    if part_mode == "parts_colored":
        parts_svg.append(f'<path d="{hl_d}" fill="#2690FF" transform="rotate({horn_l_rot} {pl[0]} {pl[1]})"/>')
        parts_svg.append(f'<path d="{hr_d}" fill="#003C99" transform="rotate({horn_r_rot} {pr[0]} {pr[1]})"/>')
        parts_svg.append(f'<path d="{muzzle_d}" fill="#0068FF"/>')
        parts_svg.append(f'<path d="{GEO["nostrilGap"]}" fill="#E5484D" fill-opacity="0.55"/>')

    inner = "\n".join(parts_svg)
    svg_str = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="200 260 1600 1480" width="{height}" height="{height}">
      <g transform="rotate({head_rot} 1000 1632.8)">
        {inner}
      </g>
    </svg>'''
    png_bytes = resvg_py.svg_to_bytes(svg_string=svg_str, width=height, height=height)
    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")

def paste_center(canvas: Image.Image, item: Image.Image, center: tuple[int, int]):
    x = int(round(center[0] - item.width / 2))
    y = int(round(center[1] - item.height / 2))
    if item.mode == "RGBA":
        canvas.alpha_composite(item, (x, y))
    else:
        canvas.paste(item, (x, y))

def draw_anchor_crosshair(draw: ImageDraw.ImageDraw, pos: tuple[int, int], color=(229, 72, 77),
                          r=12, label: str = "", align: str = "right"):
    x, y = pos
    draw.ellipse((x - r, y - r, x + r, y + r), outline=color, width=3)
    draw.line((x - r - 6, y, x + r + 6, y), fill=color, width=3)
    draw.line((x, y - r - 6, x, y + r + 6), fill=color, width=3)
    if label:
        f = get_font(FONT_BOLD_PATH, 15)
        bbox = draw.textbbox((0, 0), label, font=f)
        tw = bbox[2] - bbox[0]
        if align == "left":
            bx0 = x - r - 18 - tw
            bx1 = x - r - 4
        elif align == "bottom":
            bx0 = x - tw // 2 - 8
            bx1 = x + tw // 2 + 8
            y = y + r + 22
        else:
            bx0 = x + r + 6
            bx1 = x + r + 20 + tw
        draw.rounded_rectangle((bx0, y - 14, bx1, y + 14), radius=6, fill=(10, 20, 46, 235), outline=color, width=2)
        draw.text((bx0 + 7, y - 10), label, fill=C_WHITE, font=f)

def draw_motion_arrow(draw: ImageDraw.ImageDraw, p0: tuple[int, int], p1: tuple[int, int],
                      color=(255, 195, 50), width: int = 4, label: str = ""):
    """Vẽ mũi tên chỉ hướng chuyển động (Motion Vector Arrow) trên Storyboard."""
    x0, y0 = p0
    x1, y1 = p1
    draw.line((x0, y0, x1, y1), fill=color, width=width)
    ang = math.atan2(y1 - y0, x1 - x0)
    head_len = 14
    p_left = (x1 - head_len * math.cos(ang - 0.45), y1 - head_len * math.sin(ang - 0.45))
    p_right = (x1 - head_len * math.cos(ang + 0.45), y1 - head_len * math.sin(ang + 0.45))
    draw.polygon([(x1, y1), p_left, p_right], fill=color)
    if label:
        f = get_font(FONT_BOLD_PATH, 13)
        mx, my = (x0 + x1) // 2, (y0 + y1) // 2 - 14
        bb = draw.textbbox((0, 0), label, font=f)
        tw = bb[2] - bb[0]
        draw.rounded_rectangle((mx - tw // 2 - 6, my - 10, mx + tw // 2 + 6, my + 12), radius=5, fill=(10, 20, 46, 230), outline=color, width=1)
        draw.text((mx - tw // 2, my - 8), label, fill=color, font=f)

def make_chat_bubble(w: int, h: int, tail_side: str = "left", bg_color=C_BLUE,
                     bars: int = 2, has_icon: str = "", text_lines: list[str] | None = None,
                     text_color=C_WHITE) -> Image.Image:
    S = 2
    W, H = w * S, h * S
    tail_h = int(22 * S)
    img = Image.new("RGBA", (W, H + tail_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rad = int(min(W, H) * 0.28)
    d.rounded_rectangle((0, 0, W - 1, H - 1), radius=rad, fill=bg_color + (255,))
    if tail_side == "left":
        d.polygon([(int(W * 0.10), H - 4), (int(W * 0.24), H - 4), (int(W * 0.05), H + tail_h - 1)], fill=bg_color + (255,))
    elif tail_side == "right":
        d.polygon([(int(W * 0.76), H - 4), (int(W * 0.90), H - 4), (int(W * 0.95), H + tail_h - 1)], fill=bg_color + (255,))

    pad_x = int(24 * S)
    if has_icon == "bell":
        r = int(16 * S)
        cx, cy = pad_x + r, H // 2
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=C_WHITE + (255,))
        d.polygon([(cx, cy - r // 2), (cx - r // 2, cy + r // 3), (cx + r // 2, cy + r // 3)], fill=bg_color + (255,))
        pad_x += r * 2 + int(14 * S)
    elif has_icon == "dots":
        for i in (-1, 0, 1):
            cx = W // 2 + i * int(26 * S)
            cy = H // 2
            r = int(8 * S)
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=C_WHITE + (255,))
        return img.resize((w, h + 22), Image.LANCZOS)

    if text_lines:
        f = get_font(FONT_MED_PATH, int(19 * S))
        ty = int(18 * S)
        for line in text_lines:
            d.text((pad_x, ty), line, fill=text_color + (255,), font=f)
            ty += int(26 * S)
    else:
        bar_col = (255, 255, 255, 210) if bg_color in (C_BLUE, C_BLUE_COBALT, C_ORANGE_MSG, C_ALERT) else (160, 180, 215, 255)
        bar_h = int(12 * S)
        start_y = (H - (bars * bar_h + (bars - 1) * int(12 * S))) // 2
        for i in range(bars):
            bw = int((W - pad_x - 28 * S) * (0.88 if i == 0 else 0.62))
            by = start_y + i * int(24 * S)
            d.rounded_rectangle((pad_x, by, pad_x + bw, by + bar_h), radius=bar_h // 2, fill=bar_col)

    return img.resize((w, h + 22), Image.LANCZOS)

def make_wall_clock(diameter: int, minute_deg: float, hour_deg: float, alert_glow: bool = False) -> Image.Image:
    S = 2
    D = diameter * S
    pad = 24 * S
    img = Image.new("RGBA", (D + pad * 2, D + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = D // 2 + pad
    r = D // 2
    if alert_glow:
        for gr in range(r + 18 * S, r, -4 * S):
            alpha = int(45 * (1 - (gr - r) / (18 * S)))
            d.ellipse((cx - gr, cy - gr, cx + gr, cy + gr), fill=C_ALERT + (alpha,))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(18, 32, 62, 245), outline=C_BLUE_GLOW if not alert_glow else C_ALERT, width=5 * S)
    for idx in range(12):
        ang = math.radians(idx * 30 - 90)
        r_in = r * (0.78 if idx % 3 == 0 else 0.85)
        r_out = r * 0.92
        d.line((cx + r_in * math.cos(ang), cy + r_in * math.sin(ang),
                cx + r_out * math.cos(ang), cy + r_out * math.sin(ang)),
               fill=(180, 205, 245, 220), width=(4 if idx % 3 == 0 else 2) * S)
    if minute_deg > 60:
        for trail in range(1, 6):
            tang = math.radians(minute_deg - trail * 18 - 90)
            d.line((cx, cy, cx + r * 0.72 * math.cos(tang), cy + r * 0.72 * math.sin(tang)),
                   fill=C_ALERT + (int(110 - trail * 18),), width=4 * S)
    hang = math.radians(hour_deg - 90)
    mang = math.radians(minute_deg - 90)
    d.line((cx, cy, cx + r * 0.48 * math.cos(hang), cy + r * 0.48 * math.sin(hang)), fill=C_WHITE + (255,), width=6 * S)
    d.line((cx, cy, cx + r * 0.74 * math.cos(mang), cy + r * 0.74 * math.sin(mang)), fill=(C_ALERT if alert_glow else C_BLUE_GLOW) + (255,), width=5 * S)
    d.ellipse((cx - 8 * S, cy - 8 * S, cx + 8 * S, cy + 8 * S), fill=C_WHITE + (255,))
    return img.resize((diameter + 48, diameter + 48), Image.LANCZOS)


# ==============================================================================
# BƯỚC 1: TẠO CHARACTER & RIG SHEET CHO BÒ OPA (`00_CHARACTER_SHEET_BO_OPA`)
# ==============================================================================
def build_character_sheets():
    cs_dir = OUT_DIR / "00_CHARACTER_SHEET_BO_OPA"
    cs_dir.mkdir(parents=True, exist_ok=True)

    c_white = Image.new("RGBA", (1600, 1600), C_WHITE + (255,))
    paste_center(c_white, render_bo_opa_svg(1050, "#0068FF"), (800, 800))
    c_white.convert("RGB").save(cs_dir / "CS02_REF_BO_OPA_XANH_NEN_TRANG.png")

    c_blue = Image.new("RGBA", (1600, 1600), C_BLUE + (255,))
    paste_center(c_blue, render_bo_opa_svg(1050, "#FFFFFF"), (800, 800))
    c_blue.convert("RGB").save(cs_dir / "CS03_REF_BO_OPA_TRANG_NEN_XANH.png")

    c_parts = Image.new("RGBA", (1920, 1080), C_WHITE + (255,))
    paste_center(c_parts, render_bo_opa_svg(560, "#0068FF", part_mode="horn_l"), (420, 480))
    paste_center(c_parts, render_bo_opa_svg(620, "#0068FF", part_mode="muzzle"), (960, 560))
    paste_center(c_parts, render_bo_opa_svg(560, "#0068FF", part_mode="horn_r"), (1500, 480))
    c_parts.convert("RGB").save(cs_dir / "CS04_COMPONENT_3_BO_PHAN_BO_OPA_SACH.png")

    sheet = Image.new("RGBA", (2400, 1400), (245, 248, 255, 255))
    d = ImageDraw.Draw(sheet)
    f_h1 = get_font(FONT_BOLD_PATH, 34)
    f_h2 = get_font(FONT_BOLD_PATH, 24)
    f_b = get_font(FONT_MED_PATH, 19)
    f_sm = get_font(FONT_MED_PATH, 16)

    d.rounded_rectangle((30, 24, 2370, 104), radius=18, fill=C_NAVY_BG)
    d.text((60, 44), "OPA AGENT — CHARACTER & MECHANICAL RIG SHEET: MASCOT BÒ OPA (V4 · A · O CORE)", fill=C_WHITE, font=f_h1)
    d.text((1780, 50), "CHUẨN HÌNH HỌC & ANCHOR POINT AE", fill=C_BLUE_GLOW, font=f_h2)

    # Khung 1
    d.rounded_rectangle((30, 124, 780, 740), radius=20, fill=C_WHITE, outline=(210, 220, 240), width=3)
    d.text((55, 145), "1. BẢN GỐC (MASTER SILHOUETTE LOCK)", fill=C_NAVY_BG, font=f_h2)
    d.rounded_rectangle((55, 195, 395, 535), radius=16, fill=(244, 247, 255), outline=C_BLUE, width=2)
    paste_center(sheet, render_bo_opa_svg(280, "#0068FF"), (225, 365))
    d.text((95, 548), "Nền sáng -> Bò Xanh #0068FF", fill=C_NAVY_BG, font=f_sm)

    d.rounded_rectangle((415, 195, 755, 535), radius=16, fill=C_BLUE)
    paste_center(sheet, render_bo_opa_svg(280, "#FFFFFF"), (585, 365))
    d.text((455, 548), "Nền xanh/tối -> Bò Trắng #FFFFFF", fill=C_NAVY_BG, font=f_sm)

    rules = [
        "• TUYỆT ĐỐI KHÔNG vẽ thêm mắt, mũi, miệng, tai hay chân.",
        "• Giữ nguyên vòng tròn trắng chữ O ở tâm dưới [50%, 64.7%].",
        "• Scale đồng nhất 2 trục [S%, S%] — Cấm Squash & Stretch.",
        "• Gọi là 'OPA Bull Mark / HERO' trong prompt để tránh AI bịa mặt."
    ]
    ry = 590
    for rline in rules:
        d.text((55, ry), rline, fill=C_ALERT if "TUYỆT ĐỐI" in rline else C_NAVY_BG, font=f_sm)
        ry += 32

    # Khung 2: Giải phẫu 4 Phần & Điểm Neo (Anchor Points không chồng lấp)
    d.rounded_rectangle((805, 124, 1620, 740), radius=20, fill=C_WHITE, outline=(210, 220, 240), width=3)
    d.text((830, 145), "2. TÁCH LAYER & ĐIỂM NEO (AE ANCHOR POINTS)", fill=C_NAVY_BG, font=f_h2)
    rig_img = render_bo_opa_svg(440, "#0068FF", part_mode="parts_colored")
    paste_center(sheet, rig_img, (1212, 415))
    draw_anchor_crosshair(d, (1212, 588), C_ALERT, 11, "A1: Đáy U_HEAD [50%, 100%]", align="right")
    draw_anchor_crosshair(d, (1092, 388), (255, 140, 0), 10, "A2: HORN_L [22.6%, 42.1%]", align="left")
    draw_anchor_crosshair(d, (1332, 388), (255, 140, 0), 10, "A3: HORN_R [77.4%, 42.1%]", align="right")
    draw_anchor_crosshair(d, (1212, 478), C_GREEN_OK, 10, "A4: Tâm O [50%, 64.7%]", align="right")
    d.text((830, 665), "• (a) a-horn-left  • (b) b-horn-right  • (c) c-muzzle (chữ U)  • (d) d-nostril-gap (khe trán)", fill=C_NAVY_BG, font=f_sm)
    d.text((830, 695), "• Chân sừng chìm trong thân chữ U để khi xoay ±40° không bị hở khe nối.", fill=C_BLUE_DARK, font=f_sm)

    # Khung 3: Bảng Màu Token & Thông Số Hình Học PDF
    d.rounded_rectangle((1645, 124, 2370, 740), radius=20, fill=C_WHITE, outline=(210, 220, 240), width=3)
    d.text((1670, 145), "3. BRAND TOKENS & TỶ LỆ VÀNG (1.618)", fill=C_NAVY_BG, font=f_h2)
    swatches = [
        (C_BLUE, "#0068FF", "Blue (Chủ đạo)"),
        (C_BLUE_COBALT, "#1E40FF", "Cobalt UI Glow"),
        (C_BLUE_DARK, "#003C99", "Blue Dark (Nền đêm)"),
        (C_BLUE_LIGHT, "#E6F0FF", "Blue Light (Nền phụ)"),
        (C_NAVY_BG, "#0A142E", "Navy Workspace"),
        (C_ALERT, "#E5484D", "Alert Badge (Chỉ chấm nhỏ)")
    ]
    sy = 200
    for col, hex_code, desc in swatches:
        d.rounded_rectangle((1670, sy, 1740, sy + 44), radius=10, fill=col, outline=C_BLUE if col == C_BLUE_LIGHT else None, width=2)
        d.text((1758, sy + 10), f"{hex_code} — {desc}", fill=C_NAVY_BG, font=f_b)
        sy += 60
    geo_specs = [
        "Thông số dựng từ PDF V4 (khung 1000u):",
        "• Độ rộng thân U: W = 520 u",
        "• Độ dày nét: t = 99.311 u",
        "• Khe trán: g = W / 1.618^3 = 122.755 u",
        "• Bo ngoài R = 2t | Bo trong r = t (đồng tâm)",
        "• Khía vai sừng: 125.0° (sai số <= 0.76 px)"
    ]
    gy = 565
    for gline in geo_specs:
        d.text((1670, gy), gline, fill=C_NAVY_BG, font=f_sm)
        gy += 26

    # Khung 4: 5 Tư thế diễn xuất
    d.rounded_rectangle((30, 765, 2370, 1375), radius=20, fill=C_WHITE, outline=(210, 220, 240), width=3)
    d.text((55, 785), "4. 5 TƯ THẾ DIỄN XUẤT CHUẨN TRONG VIDEO (KEYFRAME POSES CHO OMNI FLASH & AFTER EFFECTS)", fill=C_NAVY_BG, font=f_h2)

    poses = [
        ("POSE 1: REVEAL SPRING POP", "Scale: 0% -> 112% -> 95% -> 100%\nSừng mở: -40° -> +6° -> 0° (trễ 0.08s)", 0.0, -32.0, 32.0, 0.88),
        ("POSE 2: IDLE BREATHING", "Scale đều: 100% <-> 103% (chu kỳ 2.4s)\nSừng nhịp nhẹ: ±2° đối xứng", 0.0, -2.0, 2.0, 1.0),
        ("POSE 3: CHARGE ANTICIPATION", "Nghiêng lùi lấy đà: Rotation -8°\nPosition X lùi -20px (0.15s đầu Scene 3)", -8.0, -8.0, 4.0, 0.96),
        ("POSE 4: CHARGE LUNGE (HÚC)", "Lao tới: Rotation +6° | Pos X +60px\nSừng vươn +5°, quét mở khung Chat 3D", 6.0, 6.0, -6.0, 1.06),
        ("POSE 5: LOCKUP & SNORT PUFF", "Về 0° chuẩn | Phì 2 cụm hạt xanh từ khe trán\nTrượt sang trái X=34% ghép chữ OPA AGENT", 0.0, 0.0, 0.0, 1.0)
    ]
    pw = 440
    for idx, (ptitle, pdesc, hrot, hlr, hrr, sc) in enumerate(poses):
        px = 55 + idx * (pw + 18)
        py = 835
        d.rounded_rectangle((px, py, px + pw, 1345), radius=16, fill=(244, 247, 255), outline=(195, 210, 238), width=2)
        d.rounded_rectangle((px, py, px + pw, py + 48), radius=16, fill=C_NAVY_BG)
        d.text((px + 18, py + 12), ptitle, fill=C_WHITE, font=f_sm)
        bo_im = render_bo_opa_svg(int(270 * sc), "#0068FF", head_rot=hrot, horn_l_rot=hlr, horn_r_rot=hrr)
        paste_center(sheet, bo_im, (px + pw // 2, py + 215))
        if idx == 4:
            for dx, dy, pr in [(-35, -95, 10), (-55, -125, 7), (35, -95, 10), (55, -125, 7)]:
                cx, cy = px + pw // 2 + dx, py + 215 + dy
                d.ellipse((cx - pr, cy - pr, cx + pr, cy + pr), fill=C_BLUE_GLOW)
        draw_anchor_crosshair(d, (px + pw // 2, py + 315), C_ALERT, 8)
        dy_text = py + 385
        for line in pdesc.split("\n"):
            d.text((px + 16, dy_text), line, fill=C_NAVY_BG, font=f_sm)
            dy_text += 28

    sheet.convert("RGB").save(cs_dir / "CS01_BO_OPA_CHARACTER_RIG_SHEET.png")

    if (AI_DIR / "chu_shop_scene1_qua_tai_base.png").exists() and (AI_DIR / "chu_shop_scene4_thanh_thoi_base.png").exists():
        s1_im = Image.open(AI_DIR / "chu_shop_scene1_qua_tai_base.png").resize((1120, 630), Image.LANCZOS)
        s4_im = Image.open(AI_DIR / "chu_shop_scene4_thanh_thoi_base.png").resize((1120, 630), Image.LANCZOS)
        cs_shop = Image.new("RGB", (2360, 860), (245, 248, 255))
        ds = ImageDraw.Draw(cs_shop)
        ds.rounded_rectangle((30, 20, 2330, 95), radius=16, fill=C_NAVY_BG)
        ds.text((55, 38), "CHARACTER SHEET PHỤ: NHÂN VẬT CHỦ SHOP PANCAKE (ĐỐI LẬP TRƯỚC & SAU KHI DÙNG OPA AGENT)", fill=C_WHITE, font=f_h1)
        cs_shop.paste(s1_im, (40, 120))
        cs_shop.paste(s4_im, (1200, 120))
        ds.text((40, 765), "TRẠNG THÁI 1 (SCENE 1 - 00:00–00:05): Quay lưng quá tải đêm muộn | Anchor cổ [50%, 62%] | Nền #0A142E", fill=C_NAVY_BG, font=f_b)
        ds.text((1200, 765), "TRẠNG THÁI 2 (SCENE 4 - 00:22–00:30): Thảnh thơi mỉm cười ban ngày | Dang rộng 2 tay +18° | Nền #F4F7FF", fill=C_BLUE_DARK, font=f_b)
        cs_shop.save(cs_dir / "CS05_CHU_SHOP_CHARACTER_SHEET.png")


# ==============================================================================
# HÀM TẠO BẢNG MASTER BAO QUÁT 5s CHO TỪNG SCENE (`00_MASTER_BAO_QUAT_5s.png`)
# ==============================================================================
def build_master_storyboard_sheet(scene_dir: Path, scene_code: str, scene_title: str,
                                  time_range: str, frames_list: list[tuple[str, str, Image.Image]],
                                  components_list: list[tuple[str, str, Image.Image]],
                                  ae_params_lines: list[str]):
    W, H = 2480, 1620
    sheet = Image.new("RGB", (W, H), (14, 24, 52))
    d = ImageDraw.Draw(sheet)
    f_h1 = get_font(FONT_BOLD_PATH, 30)
    f_h2 = get_font(FONT_BOLD_PATH, 22)
    f_b = get_font(FONT_MED_PATH, 17)
    f_sm = get_font(FONT_MED_PATH, 14)

    d.rounded_rectangle((28, 22, W - 28, 102), radius=16, fill=(24, 42, 86), outline=C_BLUE_GLOW, width=2)
    d.text((52, 36), f"[ẢNH BAO QUÁT 5 GIÂY] {scene_code} ({time_range}) — {scene_title}", fill=C_WHITE, font=f_h1)
    d.text((52, 72), "Cấu trúc chuẩn Omni Flash: [F01: FIRST FRAME] -> [M02..M04: 3 BƯỚC MOTION TRUNG GIAN] -> [F05: LAST FRAME / ẢNH ĐÍCH]", fill=(160, 205, 255), font=f_b)

    d.text((40, 118), "A. CHUỖI 5 FRAME CHUYỂN ĐỘNG TRONG 5 GIÂY (1 TẤM BAO QUÁT 5s = 5 NHỊP MOTION):", fill=C_BLUE_GLOW, font=f_h2)
    fw, fh = 456, 256
    gap = 24
    for idx, (fcode, fdesc, fim) in enumerate(frames_list):
        fx = 40 + idx * (fw + gap)
        fy = 154
        is_end_or_start = (idx == 0 or idx == len(frames_list) - 1)
        border_col = C_GREEN_OK if idx == 0 else (C_ALERT if idx == len(frames_list) - 1 else C_BLUE_GLOW)
        d.rounded_rectangle((fx - 4, fy - 4, fx + fw + 4, fy + fh + 74), radius=12, fill=(20, 34, 68), outline=border_col, width=3 if is_end_or_start else 2)
        thumb = fim.convert("RGB").resize((fw, fh), Image.LANCZOS)
        sheet.paste(thumb, (fx, fy))
        tag = "[FIRST FRAME]" if idx == 0 else ("[LAST FRAME / ĐÍCH]" if idx == len(frames_list) - 1 else f"[MOTION {idx+1}/5]")
        d.text((fx + 10, fy + fh + 8), f"{tag} {fcode}", fill=border_col, font=f_b)
        d.text((fx + 10, fy + fh + 34), fdesc, fill=C_WHITE, font=f_sm)

    d.text((40, 510), "B. ẢNH BAO QUÁT ĐÍCH (TARGET MASTER COMPOSITION - F05):", fill=C_GREEN_OK, font=f_h2)
    big_w, big_h = 960, 540
    big_im = frames_list[-1][2].convert("RGB").resize((big_w, big_h), Image.LANCZOS)
    d.rounded_rectangle((36, 546, 40 + big_w + 4, 550 + big_h + 4), radius=14, outline=C_GREEN_OK, width=3)
    sheet.paste(big_im, (40, 550))

    d.text((1030, 510), "C. CÁC ẢNH THÀNH PHẦN (COMPONENT INGREDIENTS TÁCH LẺ CHO OMNI FLASH):", fill=(255, 195, 60), font=f_h2)
    cw, ch = 335, 206
    for idx, (ccode, cdesc, cim) in enumerate(components_list[:4]):
        col = idx % 2
        row = idx // 2
        cx = 1030 + col * (cw + 26)
        cy = 550 + row * (ch + 66)
        d.rounded_rectangle((cx - 3, cy - 3, cx + cw + 3, cy + ch + 48), radius=12, fill=(22, 36, 72), outline=(255, 195, 60), width=2)
        comp_card = Image.new("RGBA", (cw, ch), (240, 245, 255, 255))
        scale_r = min((cw - 24) / max(1, cim.width), (ch - 24) / max(1, cim.height))
        resized_c = cim.resize((max(1, int(cim.width * scale_r)), max(1, int(cim.height * scale_r))), Image.LANCZOS)
        paste_center(comp_card, resized_c, (cw // 2, ch // 2))
        sheet.paste(comp_card.convert("RGB"), (cx, cy))
        d.text((cx + 8, cy + ch + 6), f"[COMPONENT] {ccode}", fill=(255, 195, 60), font=f_sm)
        d.text((cx + 8, cy + ch + 25), cdesc, fill=C_WHITE, font=f_sm)

    d.rounded_rectangle((1760, 550, W - 40, 1094), radius=14, fill=(20, 34, 68), outline=C_BLUE_GLOW, width=2)
    d.text((1784, 568), "D. THÔNG SỐ AFTER EFFECTS & MOTION:", fill=C_BLUE_GLOW, font=f_h2)
    ay = 610
    for line in ae_params_lines:
        d.text((1784, ay), line, fill=C_WHITE, font=f_sm)
        ay += 30

    d.rounded_rectangle((40, 1125, W - 40, H - 30), radius=16, fill=(20, 34, 68), outline=(120, 170, 255), width=2)
    d.text((64, 1145), "E. CÁCH NẠP BỘ ẢNH NÀY VÀO GOOGLE OMNI FLASH (FLOW) ĐỂ TẠO CHUYỂN ĐỘNG:", fill=(140, 210, 255), font=f_h2)
    guide_lines = [
        "1. Ô [FIRST FRAME / KHUNG ĐẦU]: Nạp file `F01_FIRST_FRAME_t0.0s.png` (Trạng thái khởi đầu tại giây 0.00s).",
        "2. Ô [LAST FRAME / KHUNG CUỐI]: Nạp file `F05_LAST_FRAME_t5.0s.png` (Bố cục đích hoàn chỉnh ở cuối 5s — giữ vai trò khóa đích).",
        "3. Ô [INGREDIENTS / REFERENCE IMAGES]: Nạp các file `C01..C04_COMPONENT_*.png` để AI nhận diện đúng từng vật thể thành phần cần di chuyển.",
        "4. Ô [PROMPT]: Dán Prompt chuyển động của Scene này (đã chỉ định rõ chuyển động từ F01 qua M02->M03->M04 tới F05, khóa Anchor Point, Scale, Position, Rotation).",
        "5. HẬU KỲ AFTER EFFECTS: Đối chiếu với `F05_LAST_FRAME_CO_CHU_AE.png` để đặt lớp chữ Tiếng Việt sắc nét 4K (`Be Vietnam Pro` + `Fraunces Italic 800`)."
    ]
    gy = 1188
    for gl in guide_lines:
        d.text((64, gy), gl, fill=C_WHITE, font=f_b)
        gy += 36

    sheet.save(scene_dir / "00_MASTER_BAO_QUAT_5s.png")


# ==============================================================================
# DỰNG 6 PHÂN ĐOẠN SCENE 01 -> SCENE 05
# ==============================================================================
def build_scene_01():
    sdir = OUT_DIR / "SCENE_01_00s-05s_HOOK_QUA_TAI"
    sdir.mkdir(parents=True, exist_ok=True)
    base_bg = Image.open(AI_DIR / "chu_shop_scene1_qua_tai_base.png").convert("RGBA")

    comp_clock_fast = make_wall_clock(220, minute_deg=300, hour_deg=150, alert_glow=True)
    comp_bubble_blue = make_chat_bubble(280, 96, tail_side="left", bg_color=C_BLUE, bars=2, has_icon="bell")
    comp_bubble_orange = make_chat_bubble(260, 92, tail_side="right", bg_color=C_ORANGE_MSG, bars=2, has_icon="bell")
    comp_badge_overload = Image.new("RGBA", (180, 76), (0, 0, 0, 0))
    db = ImageDraw.Draw(comp_badge_overload)
    db.rounded_rectangle((0, 0, 179, 75), radius=38, fill=C_ALERT + (255,), outline=C_WHITE + (255,), width=4)
    db.ellipse((28, 22, 60, 54), fill=C_WHITE + (255,))
    db.rounded_rectangle((74, 28, 152, 48), radius=10, fill=C_WHITE + (255,))

    comp_clock_fast.save(sdir / "C01_COMPONENT_DONG_HO_QUAY_NHANH.png")
    comp_bubble_blue.save(sdir / "C02_COMPONENT_BONG_BONG_MESSENGER.png")
    comp_bubble_orange.save(sdir / "C03_COMPONENT_BONG_BONG_PANCAKE.png")
    comp_badge_overload.save(sdir / "C04_COMPONENT_HUY_HIEU_CANH_BAO_DO.png")

    bubble_specs = [
        (760, 620, "left", C_BLUE, 280, 92),
        (1340, 610, "right", C_ORANGE_MSG, 270, 90),
        (710, 490, "left", C_ORANGE_MSG, 290, 94),
        (1390, 480, "right", C_BLUE, 285, 92),
        (820, 370, "left", C_BLUE, 275, 90),
        (1280, 360, "right", C_ALERT, 270, 90),
        (640, 390, "left", C_BLUE_COBALT, 255, 86),
        (1470, 585, "right", C_ORANGE_MSG, 260, 88),
    ]

    def render_s1_frame(step_idx: int, with_ae_text: bool = False) -> Image.Image:
        zoom = 1.0 + step_idx * 0.015
        w, h = 1920, 1080
        crop_w, crop_h = int(w / zoom), int(h / zoom)
        cx, cy = w // 2 + step_idx * 8, h // 2 - step_idx * 4
        x0 = max(0, min(w - crop_w, cx - crop_w // 2))
        y0 = max(0, min(h - crop_h, cy - crop_h // 2))
        canvas = base_bg.crop((x0, y0, x0 + crop_w, y0 + crop_h)).resize((w, h), Image.LANCZOS)
        if step_idx > 0:
            dark = Image.new("RGBA", (w, h), (4, 8, 22, int(step_idx * 22)))
            canvas.alpha_composite(dark)

        m_deg = step_idx * 270
        h_deg = 60 + step_idx * 22.5
        clk = make_wall_clock(210, minute_deg=m_deg, hour_deg=h_deg, alert_glow=(step_idx >= 2))
        paste_center(canvas, clk, (1480, 285))

        counts = [0, 2, 4, 6, 8][step_idx]
        for b_i in range(counts):
            bx, by, tside, bcol, bw, bh = bubble_specs[b_i]
            sc = 1.08 if b_i == counts - 1 and step_idx < 4 else 1.0
            bub = make_chat_bubble(int(bw * sc), int(bh * sc), tail_side=tside, bg_color=bcol, bars=2, has_icon="bell")
            paste_center(canvas, bub, (bx, by))

        if step_idx >= 3:
            paste_center(canvas, comp_badge_overload, (1085, 555))

        if with_ae_text:
            d = ImageDraw.Draw(canvas)
            d.rounded_rectangle((180, 48, 1740, 205), radius=24, fill=(10, 20, 46, 230), outline=C_BLUE_GLOW, width=3)
            f1 = get_font(FONT_BOLD_PATH, 46)
            f2 = get_font(FONT_MED_PATH, 34)
            d.text((460, 68), "BẠN MẤT BAO NHIÊU THỜI GIAN", fill=C_WHITE, font=f1)
            d.text((370, 134), "Để trả lời khách và lên đơn trên Pancake mỗi ngày?", fill=(165, 210, 255), font=f2)
        return canvas

    f01, m02, m03, m04, f05, f05_ae = (
        render_s1_frame(0), render_s1_frame(1), render_s1_frame(2),
        render_s1_frame(3), render_s1_frame(4, False), render_s1_frame(4, True)
    )
    f01.convert("RGB").save(sdir / "F01_FIRST_FRAME_t0.0s.png")
    m02.convert("RGB").save(sdir / "M02_MOTION_STEP_t1.25s.png")
    m03.convert("RGB").save(sdir / "M03_MOTION_STEP_t2.50s.png")
    m04.convert("RGB").save(sdir / "M04_MOTION_STEP_t3.75s.png")
    f05.convert("RGB").save(sdir / "F05_LAST_FRAME_t5.0s.png")
    f05_ae.convert("RGB").save(sdir / "F05_LAST_FRAME_CO_CHU_AE.png")

    build_master_storyboard_sheet(
        sdir, "SCENE 01", "HOOK: CHỦ SHOP QUÁ TẢI & ĐỒNG HỒ QUAY + BÃO TIN NHẮN", "00:00 – 00:05 (5.0s)",
        [
            ("F01 (0.00s)", "Khởi đầu: Chủ shop trước laptop, 0 bubble", f01),
            ("M02 (1.25s)", "Đồng hồ quay +270°, 2 bubble nảy (108%)", m02),
            ("M03 (2.50s)", "Đồng hồ +540° phát đỏ, 4 bubble vây quanh", m03),
            ("M04 (3.75s)", "Đồng hồ +810°, 6 bubble + Huy hiệu đỏ", m04),
            ("F05 (5.00s)", "Đích: 8 bubble ngập màn hình, phòng tối dần", f05),
        ],
        [
            ("C01_CLOCK", "Đồng hồ treo tường (Anchor: Tâm trục kim)", comp_clock_fast),
            ("C02_MSG_BLUE", "Bong bóng Messenger (Anchor: Đuôi trái)", comp_bubble_blue),
            ("C03_MSG_ORANGE", "Bong bóng Pancake (Anchor: Đuôi phải)", comp_bubble_orange),
            ("C04_ALERT_BADGE", "Huy hiệu quá tải đỏ (Scale 0->115->100%)", comp_badge_overload),
        ],
        [
            "• CAM_Null: Scale 96% -> 104% (Linear Push-in)",
            "• WALL_CLOCK: Anchor [76%, 26%]",
            "  - Kim phút: Rotation 0° -> +1080° (3 vòng)",
            "  - Kim giờ: Rotation 60° -> +150°",
            "  - Easing: In 40% / Out 85%",
            "• MSG_BUBBLES_01..08:",
            "  - Anchor Point: Đuôi bong bóng [0%, 100%]",
            "  - Scale Spring: 0% -> 108% -> 100% (10 frames)",
            "  - Rotation: -6° -> +2° -> 0°",
            "  - Stagger: 0.25s / bubble (khớp 120 BPM)",
            "• SHOP_OWNER: Nghiêng đầu -5° -> +4°",
            "• SFX: fast-forward-whirr + pop-bubble A4/C#5/E5"
        ]
    )


def build_scene_02():
    sdir = OUT_DIR / "SCENE_02_05s-11s_XOAY_SAU_NOI_DAU"
    sdir.mkdir(parents=True, exist_ok=True)

    comp_chat_row = Image.new("RGBA", (680, 96), (0, 0, 0, 0))
    dr = ImageDraw.Draw(comp_chat_row)
    dr.rounded_rectangle((0, 0, 679, 95), radius=18, fill=(22, 38, 76, 255), outline=C_ALERT + (220,), width=2)
    dr.ellipse((20, 20, 76, 76), fill=C_BLUE_COBALT)
    dr.ellipse((62, 16, 82, 36), fill=C_ALERT)
    dr.rounded_rectangle((100, 24, 420, 42), radius=9, fill=C_WHITE)
    dr.rounded_rectangle((100, 56, 560, 72), radius=8, fill=(140, 165, 210))
    dr.rounded_rectangle((590, 28, 656, 66), radius=14, fill=C_ALERT)
    comp_chat_row.save(sdir / "C01_COMPONENT_HANG_TIN_NHAN_CHO_REP.png")

    comp_bell_badge = Image.new("RGBA", (220, 96), (0, 0, 0, 0))
    dbb = ImageDraw.Draw(comp_bell_badge)
    dbb.rounded_rectangle((0, 0, 219, 95), radius=48, fill=C_ALERT, outline=C_WHITE, width=4)
    dbb.ellipse((26, 22, 78, 74), fill=C_WHITE)
    dbb.rounded_rectangle((96, 30, 190, 66), radius=14, fill=C_WHITE)
    comp_bell_badge.save(sdir / "C02_COMPONENT_HUY_HIEU_99_PLUS.png")

    comp_pos_manual = Image.new("RGBA", (740, 440), (0, 0, 0, 0))
    dp = ImageDraw.Draw(comp_pos_manual)
    dp.rounded_rectangle((0, 0, 739, 439), radius=24, fill=(18, 30, 60, 255), outline=(90, 120, 180), width=3)
    dp.rounded_rectangle((0, 0, 739, 64), radius=24, fill=(30, 48, 92, 255))
    for i in range(3):
        dp.ellipse((28 + i * 24, 22, 44 + i * 24, 38), fill=C_ALERT if i == 0 else C_BLUE_GLOW)
    for r_i in range(4):
        ry = 92 + r_i * 78
        dp.rounded_rectangle((28, ry, 210, ry + 48), radius=10, fill=(32, 50, 92))
        dp.rounded_rectangle((228, ry, 708, ry + 48), radius=10, fill=(10, 18, 38), outline=C_ALERT if r_i == 2 else (65, 95, 150), width=2)
        if r_i < 2:
            dp.rounded_rectangle((246, ry + 16, 520, ry + 32), radius=8, fill=(130, 155, 200))
        elif r_i == 2:
            dp.rounded_rectangle((246, ry + 16, 390, ry + 32), radius=8, fill=C_ALERT)
            dp.line((402, ry + 10, 402, ry + 38), fill=C_WHITE, width=4)
    comp_pos_manual.save(sdir / "C03_COMPONENT_BANG_NHAP_POS_THU_CONG.png")

    comp_pain_pill = Image.new("RGBA", (740, 74), (0, 0, 0, 0))
    dpp = ImageDraw.Draw(comp_pain_pill)
    dpp.rounded_rectangle((0, 0, 739, 73), radius=37, fill=(26, 40, 78, 240), outline=C_ALERT, width=3)
    dpp.ellipse((20, 17, 56, 53), fill=C_ALERT)
    dpp.rounded_rectangle((78, 26, 540, 48), radius=11, fill=(215, 225, 245))
    comp_pain_pill.save(sdir / "C04_COMPONENT_THANH_NOI_DAU_GLASS.png")

    def render_s2_frame(step_idx: int, with_ae_text: bool = False) -> Image.Image:
        w, h = 1920, 1080
        canvas = Image.new("RGBA", (w, h), C_NAVY_DEEP + (255,))
        d = ImageDraw.Draw(canvas)
        for gx in range(0, w, 80):
            d.line((gx, 0, gx, h), fill=(18, 32, 66, 90), width=1)
        for gy in range(0, h, 80):
            d.line((0, gy, w, gy), fill=(18, 32, 66, 90), width=1)
        for gr in range(460, 60, -40):
            d.ellipse((480 - gr, 540 - gr, 480 + gr, 540 + gr), fill=(229, 72, 77, int(6 + step_idx * 2)))

        inbox_w, inbox_h = 780, 860
        ix, iy = 90, 110
        d.rounded_rectangle((ix, iy, ix + inbox_w, iy + inbox_h), radius=28, fill=(14, 24, 52, 250), outline=(60, 95, 165), width=3)
        d.rounded_rectangle((ix, iy, ix + inbox_w, iy + 78), radius=28, fill=(24, 42, 86, 255))
        for i in range(3):
            d.ellipse((ix + 28 + i * 24, iy + 28, ix + 44 + i * 24, iy + 44), fill=C_ALERT if i == 0 else C_BLUE_GLOW)

        row_count = [3, 4, 5, 6, 7][step_idx]
        chat_samples = [
            "Khách FB • Còn váy lụa size M không shop ơi?",
            "Khách IG • Giá bao nhiêu vậy ạ? Ship Hà Nội mấy ngày?",
            "Khách FB • Check bill chuyển khoản giúp em với!",
            "Khách Zalo • Sao nhắn từ tối qua chưa thấy shop rep?",
            "Khách FB • Đổi địa chỉ nhận hàng giúp chị nhé!",
            "Khách Shopee • Đặt 2 chiếc có được freeship không?",
            "Khách FB • Shop ơi tư vấn gấp giúp em mẫu mới!"
        ]
        for r_i in range(min(row_count, 6)):
            ry = iy + 104 + r_i * 120
            paste_center(canvas, comp_chat_row, (ix + inbox_w // 2, ry + 48))
            if with_ae_text:
                f_row = get_font(FONT_MED_PATH, 21)
                d.rounded_rectangle((ix + 145, ry + 18, ix + 615, ry + 78), radius=8, fill=(22, 38, 76))
                d.text((ix + 150, ry + 32), chat_samples[(r_i + step_idx) % len(chat_samples)], fill=C_WHITE, font=f_row)

        if step_idx >= 1:
            sc_b = 1.12 if step_idx == 1 else (1.06 if step_idx == 3 else 1.0)
            b_im = comp_bell_badge.resize((int(190 * sc_b), int(82 * sc_b)), Image.LANCZOS)
            paste_center(canvas, b_im, (ix + inbox_w - 40, iy + 36))
            if with_ae_text:
                f_b = get_font(FONT_BOLD_PATH, 30)
                d.rounded_rectangle((ix + inbox_w - 60, iy + 14, ix + inbox_w + 35, iy + 58), radius=14, fill=C_ALERT)
                d.text((ix + inbox_w - 52, iy + 18), f"{28 + step_idx * 24}+", fill=C_WHITE, font=f_b)

        pain_texts = [
            "Hàng chục cuộc chat bỏ dở",
            "Trả lời lặp đi lặp lại",
            "Lên đơn POS thủ công"
        ]
        pills_shown = [0, 1, 2, 3, 3][step_idx]
        for p_i in range(pills_shown):
            py = 135 + p_i * 96
            paste_center(canvas, comp_pain_pill, (1410, py + 37))
            if with_ae_text:
                d.rounded_rectangle((1110, py + 14, 1740, py + 60), radius=12, fill=(26, 40, 78))
                d.text((1120, py + 18), pain_texts[p_i], fill=C_WHITE, font=get_font(FONT_BOLD_PATH, 28))

        if step_idx >= 1:
            reveal_ratio = [0.0, 0.45, 0.85, 1.0, 1.0][step_idx]
            pw = int(comp_pos_manual.width * reveal_ratio)
            ph = int(comp_pos_manual.height * reveal_ratio)
            pos_crop = comp_pos_manual.crop((0, 0, max(1, pw), max(1, ph)))
            canvas.alpha_composite(pos_crop, (1040, 470))
            if with_ae_text and step_idx >= 2:
                f_pos = get_font(FONT_MED_PATH, 20)
                d.text((1140, 488), "PANCAKE POS — Tạo đơn thủ công (Copy-Paste)", fill=C_WHITE, font=f_pos)

        if step_idx >= 3:
            vig = Image.new("RGBA", (w, h), (2, 5, 15, 35 if step_idx == 3 else 70))
            canvas.alpha_composite(vig)

        return canvas

    f01, m02, m03, m04, f05, f05_ae = (
        render_s2_frame(0), render_s2_frame(1), render_s2_frame(2),
        render_s2_frame(3), render_s2_frame(4, False), render_s2_frame(4, True)
    )
    f01.convert("RGB").save(sdir / "F01_FIRST_FRAME_t0.0s.png")
    m02.convert("RGB").save(sdir / "M02_MOTION_STEP_t1.25s.png")
    m03.convert("RGB").save(sdir / "M03_MOTION_STEP_t2.50s.png")
    m04.convert("RGB").save(sdir / "M04_MOTION_STEP_t3.75s.png")
    f05.convert("RGB").save(sdir / "F05_LAST_FRAME_t5.0s.png")
    f05_ae.convert("RGB").save(sdir / "F05_LAST_FRAME_CO_CHU_AE.png")

    build_master_storyboard_sheet(
        sdir, "SCENE 02", "XOÁY SÂU NỖI ĐAU: HỘP THƯ QUÁ TẢI & LÊN ĐƠN POS THỦ CÔNG", "00:05 – 00:11 (6.0s / Block 5s)",
        [
            ("F01 (0.00s)", "Hộp thư Pancake mở, 3 cuộc chat chờ rep", f01),
            ("M02 (1.25s)", "Cuộn chat +1 bậc, nổ Badge đỏ, mở Form POS 45%", m02),
            ("M03 (2.50s)", "Cuộn chat +2 bậc, Pill nỗi đau #2, Form POS 85%", m03),
            ("M04 (3.75s)", "Đủ 3 Pill nỗi đau, con trỏ nhấp nháy nhập tay", m04),
            ("F05 (5.00s)", "Đích: Inbox ngập đỏ 99+, không gian tối dần", f05),
        ],
        [
            ("C01_CHAT_ROW", "Dòng hội thoại chờ rep (Step-scroll ΔY)", comp_chat_row),
            ("C02_BADGE_99", "Huy hiệu cảnh báo đỏ (Scale Pop + Shake)", comp_bell_badge),
            ("C03_POS_FORM", "Bảng POS nhập tay (Anchor: Top-Left [0,0])", comp_pos_manual),
            ("C04_PAIN_PILL", "Thanh Glass Pill nỗi đau (Slide-in X)", comp_pain_pill),
        ],
        [
            "• ChatList_Scroll_Null: Step-scroll ΔY = -120px",
            "  mỗi 0.50s (khớp nhịp 120 BPM)",
            "• Badge_99Plus: Anchor Tâm [44%, 20%]",
            "  - Scale: 0% -> 115% -> 95% -> 100%",
            "  - Slider Control đếm số tự động",
            "• Manual_POS_Card: Anchor Đỉnh-Trái [54%, 38%]",
            "  - Mask Wipe 0% -> 100% (Rule R10: Out 15.2%/In 100%)",
            "• 3 Pain-Point Pills: Trượt ngang X +8% -> 0%",
            "  cách nhau 0.75s",
            "• Dark Vignette: Opacity 0% -> 65% cuối cảnh"
        ]
    )


def build_scene_03a():
    sdir = OUT_DIR / "SCENE_03A_11s-16s_BO_OPA_VA_CHAT_3D"
    sdir.mkdir(parents=True, exist_ok=True)

    comp_bo_charge = render_bo_opa_svg(420, "#0068FF", head_rot=6.0, horn_l_rot=5.0, horn_r_rot=-5.0)
    comp_bo_charge.save(sdir / "C01_COMPONENT_BO_OPA_CHARGE.png")

    def make_05_scene_chat_card(step_state: int, with_text: bool = False) -> Image.Image:
        cw, ch = 780, 760
        card = Image.new("RGBA", (cw + 40, ch + 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(card)
        d.rounded_rectangle((28, 30, cw + 28, ch + 30), radius=34, fill=(0, 40, 120, 95))
        d.rounded_rectangle((16, 16, cw + 24, ch + 24), radius=34, fill=C_BLUE_GLOW + (190,))
        d.rounded_rectangle((20, 20, cw + 20, ch + 20), radius=30, fill=C_WHITE + (255,), outline=C_BLUE, width=4)

        d.rounded_rectangle((20, 20, cw + 20, 110), radius=30, fill=(238, 244, 255, 255))
        bo_mini = render_bo_opa_svg(64, "#0068FF")
        paste_center(card, bo_mini, (72, 65))
        d.ellipse((92, 78, 108, 94), fill=C_GREEN_OK, outline=C_WHITE, width=2)
        if with_text:
            d.text((120, 42), "OPA Agent • AI Bán Hàng Pancake", fill=C_NAVY_BG, font=get_font(FONT_BOLD_PATH, 22))
            d.text((120, 72), "Đang đồng bộ tồn kho Pancake POS trực tiếp", fill=C_BLUE, font=get_font(FONT_MED_PATH, 16))
        else:
            d.rounded_rectangle((120, 46, 420, 64), radius=9, fill=C_BLUE)
            d.rounded_rectangle((120, 74, 320, 88), radius=7, fill=(160, 185, 225))

        if step_state >= 1:
            txt_c = ["Shop ơi mẫu áo sơ mi trắng size M", "còn hàng không ạ? Giá bao nhiêu?"] if with_text else None
            b_cust = make_chat_bubble(540, 110, tail_side="left", bg_color=C_BLUE_LIGHT, bars=2, text_lines=txt_c, text_color=C_NAVY_BG)
            card.alpha_composite(b_cust, (55, 145))

        if step_state == 2:
            b_dots = make_chat_bubble(160, 74, tail_side="right", bg_color=C_BLUE, has_icon="dots")
            card.alpha_composite(b_dots, (585, 295))

        if step_state >= 3:
            txt_opa = ["Dạ mẫu sơ mi trắng size M còn 06 chiếc tại kho,", "giá ưu đãi 159.000đ ạ! Em lên đơn POS ngay nhé!"] if with_text else None
            b_opa = make_chat_bubble(580, 122, tail_side="right", bg_color=C_BLUE, bars=2, text_lines=txt_opa, text_color=C_WHITE)
            card.alpha_composite(b_opa, (175, 290))

            pos_y = 465
            d.rounded_rectangle((55, pos_y, cw - 15, pos_y + 255), radius=22, fill=(236, 253, 245, 255), outline=C_GREEN_OK, width=3)
            d.rounded_rectangle((55, pos_y, cw - 15, pos_y + 58), radius=22, fill=C_GREEN_OK + (255,))
            d.ellipse((78, pos_y + 12, 114, pos_y + 48), fill=C_WHITE)
            d.line((88, pos_y + 30, 96, pos_y + 38, 108, pos_y + 22), fill=C_GREEN_OK, width=4)
            if with_text:
                d.text((128, pos_y + 16), "ĐÃ TỰ ĐỘNG TẠO ĐƠN TRÊN PANCAKE POS (#PK8921)", fill=C_WHITE, font=get_font(FONT_BOLD_PATH, 20))
                d.text((82, pos_y + 82), "• Sản phẩm: Áo sơ mi trắng — Size M (SL: 01)", fill=C_NAVY_BG, font=get_font(FONT_MED_PATH, 20))
                d.text((82, pos_y + 122), "• Giá bán đồng bộ POS: 159.000đ (Đã trừ tồn kho)", fill=C_NAVY_BG, font=get_font(FONT_MED_PATH, 20))
                d.text((82, pos_y + 162), "• Trạng thái: Chờ giao vận — 0 giây nhập liệu tay", fill=C_GREEN_OK, font=get_font(FONT_BOLD_PATH, 20))
            else:
                d.rounded_rectangle((132, pos_y + 20, 560, pos_y + 40), radius=10, fill=C_WHITE)
                for l_i, lw in enumerate([480, 410, 520]):
                    ly = pos_y + 88 + l_i * 46
                    d.ellipse((82, ly, 106, ly + 24), fill=C_GREEN_OK)
                    d.rounded_rectangle((124, ly + 4, 124 + lw, ly + 22), radius=9, fill=(140, 195, 170) if l_i < 2 else C_GREEN_OK)

        return card

    comp_card_clean = make_05_scene_chat_card(3, with_text=False)
    comp_card_clean.save(sdir / "C02_COMPONENT_KHUNG_CHAT_3D_05_SCENE.png")
    make_chat_bubble(180, 82, tail_side="right", bg_color=C_BLUE, has_icon="dots").save(sdir / "C03_COMPONENT_BA_CHAM_TYPING.png")
    comp_pos_sync = comp_card_clean.crop((45, 455, 780, 735))
    comp_pos_sync.save(sdir / "C04_COMPONENT_THE_CHOT_DON_POS_XANH.png")

    def render_s3a_frame(step_idx: int, with_ae_text: bool = False) -> Image.Image:
        w, h = 1920, 1080
        canvas = Image.new("RGBA", (w, h), (11, 24, 58, 255))
        d = ImageDraw.Draw(canvas)
        glow_r = [900, 760, 680, 650, 650][step_idx]
        for r in range(glow_r, 80, -45):
            alpha = int(18 * (1 - r / glow_r))
            d.ellipse((540 - r, 540 - r, 540 + r, 540 + r), fill=C_BLUE_COBALT + (alpha,))

        if step_idx == 0:
            d.polygon([(0, 0), (880, 0), (620, h), (0, h)], fill=(0, 104, 255, 95))
            bo_hero = render_bo_opa_svg(380, "#FFFFFF", head_rot=-8.0, horn_l_rot=-25.0, horn_r_rot=25.0)
            paste_center(canvas, bo_hero, (520, 520))
        else:
            h_rot = 6.0 if step_idx == 1 else 0.0
            bo_badge = render_bo_opa_svg(190, "#FFFFFF", head_rot=h_rot)
            paste_center(canvas, bo_badge, (175, 165))

            card_im = make_05_scene_chat_card(step_idx - 1, with_text=with_ae_text)
            horiz_persp = [1.0, 0.86, 0.94, 0.98, 1.0][step_idx]
            cw_new = int(card_im.width * horiz_persp)
            card_persp = card_im.resize((cw_new, card_im.height), Image.LANCZOS)
            paste_center(canvas, card_persp, (540, 565))

        if with_ae_text and step_idx >= 2:
            f_title = get_font(FONT_BOLD_PATH, 40)
            f_sub = get_font(FONT_MED_PATH, 28)
            d.text((980, 130), "GIẢI PHÁP ĐỘT PHÁ TỪ OPA AGENT", fill=C_BLUE_GLOW, font=f_sub)
            d.text((980, 185), "Tự trả lời khách đúng tồn kho", fill=C_WHITE, font=f_title)
            d.text((980, 245), "& Chốt đơn thẳng vào Pancake POS!", fill=C_WHITE, font=f_title)

        return canvas

    f01, m02, m03, m04, f05, f05_ae = (
        render_s3a_frame(0), render_s3a_frame(1), render_s3a_frame(2),
        render_s3a_frame(3), render_s3a_frame(4, False), render_s3a_frame(4, True)
    )
    f01.convert("RGB").save(sdir / "F01_FIRST_FRAME_t0.0s.png")
    m02.convert("RGB").save(sdir / "M02_MOTION_STEP_t1.25s.png")
    m03.convert("RGB").save(sdir / "M03_MOTION_STEP_t2.50s.png")
    m04.convert("RGB").save(sdir / "M04_MOTION_STEP_t3.75s.png")
    f05.convert("RGB").save(sdir / "F05_LAST_FRAME_t5.0s.png")
    f05_ae.convert("RGB").save(sdir / "F05_LAST_FRAME_CO_CHU_AE.png")

    build_master_storyboard_sheet(
        sdir, "SCENE 03A", "GIẢI PHÁP PHẦN 1: BÒ OPA HÚC MỞ MÀN & KHUNG CHAT 3D (05_Scene) TỰ CHỐT ĐƠN", "00:11 – 00:16 (5.0s)",
        [
            ("F01 (0.00s)", "Whoosh sáng xanh + Bò OPA lấy đà (-8°)", f01),
            ("M02 (1.25s)", "Bò húc (+6°), Card 3D xoay vào (Y-Rot +32°)", m02),
            ("M03 (2.50s)", "Card xoay phẳng dần + Tin nhắn khách nổ", m03),
            ("M04 (3.75s)", "3 chấm Typing sóng sin bên phải", m04),
            ("F05 (5.00s)", "Đích: OPA báo giá 159k + Đẩy đơn POS #PK8921", f05),
        ],
        [
            ("C01_BO_CHARGE", "Bò OPA tư thế Charge (Anchor: Đáy U_HEAD)", comp_bo_charge),
            ("C02_CHAT_05", "Khung Chat 3D 05_Scene (Viền EdgeGlow xanh)", comp_card_clean),
            ("C03_TYPING", "Bong bóng 3 chấm Typing (Sine wave 0.08s)", Image.open(sdir / "C03_COMPONENT_BA_CHAM_TYPING.png")),
            ("C04_POS_SYNC", "Thẻ tự chốt đơn POS #PK8921 (Mask Wipe R10)", comp_pos_sync),
        ],
        [
            "• MASCOT_OPA_BULL: Anchor Đáy [50%, 100%]",
            "  - Scale: 0% -> 112% -> 95% -> 100% (22f)",
            "  - Charge Rotation: -8° -> +6° -> -3° -> 0°",
            "• CHAT_CARD_05_LEFT (Giống ảnh chụp 00:19:03):",
            "  - Anchor: Tâm thẻ trái [28%, 56%]",
            "  - 3D Y-Rotation: +32° -> +4° (24 frames)",
            "  - 3D X-Rotation: +6° -> 0°",
            "  - EdgeGlow Trim Paths: 0% -> 100%",
            "• BUBBLE_CUSTOMER & BUBBLE_OPA:",
            "  - Scale: 0% -> 108% -> 100% từ đuôi bubble",
            "• POS_SYNC_CARD: Mask Wipe Out 15.2% / In 100%"
        ]
    )


def build_scene_03b():
    sdir = OUT_DIR / "SCENE_03B_16s-22s_SPLIT_SCREEN_5_PILLS"
    sdir.mkdir(parents=True, exist_ok=True)

    pill_configs = [
        ("PILL_01_TON_KHO", "Tự trả lời đúng tồn kho POS", "chat_box"),
        ("PILL_02_CHOT_DON", "Tự chốt đơn vào Pancake POS", "pkg_bolt"),
        ("PILL_03_CHECK_BILL", "Xác minh chuyển khoản bằng ảnh", "bill_shield"),
        ("PILL_04_NHAC_GIO", "Nhắc khách bỏ giỏ trong 24h", "clock_cart"),
        ("PILL_05_TIEP_QUAN", "Nhân viên tiếp quản bất cứ lúc nào", "hand_headset"),
    ]

    def make_feature_pill(idx: int, active_glow: bool = False, with_text: bool = False) -> Image.Image:
        pw, ph = 820, 108
        img = Image.new("RGBA", (pw + 24, ph + 24), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        if active_glow:
            d.rounded_rectangle((4, 4, pw + 20, ph + 20), radius=58, fill=C_BLUE_GLOW + (180,))
        d.rounded_rectangle((12, 12, pw + 12, ph + 12), radius=54, fill=C_WHITE + (255,),
                            outline=C_BLUE_GLOW if active_glow else C_BLUE, width=5 if active_glow else 3)
        icx, icy, ir = 68, 12 + ph // 2, 38
        d.ellipse((icx - ir, icy - ir, icx + ir, icy + ir), fill=C_BLUE if not active_glow else C_BLUE_COBALT)
        kind = pill_configs[idx][2]
        if kind == "chat_box":
            d.rounded_rectangle((icx - 20, icy - 16, icx + 20, icy + 10), radius=8, fill=C_WHITE)
            d.polygon([(icx - 10, icy + 10), (icx, icy + 10), (icx - 16, icy + 22)], fill=C_WHITE)
        elif kind == "pkg_bolt":
            d.rounded_rectangle((icx - 18, icy - 18, icx + 18, icy + 18), radius=5, outline=C_WHITE, width=4)
            d.line((icx - 18, icy - 4, icx + 18, icy - 4), fill=C_WHITE, width=3)
            d.line((icx, icy - 18, icx, icy + 18), fill=C_WHITE, width=3)
        elif kind == "bill_shield":
            d.rounded_rectangle((icx - 16, icy - 20, icx + 16, icy + 20), radius=4, fill=C_WHITE)
            d.line((icx - 8, icy, icx - 2, icy + 8, icx + 10, icy - 8), fill=C_GREEN_OK, width=4)
        elif kind == "clock_cart":
            d.ellipse((icx - 20, icy - 20, icx + 20, icy + 20), outline=C_WHITE, width=4)
            d.line((icx, icy, icx, icy - 12), fill=C_WHITE, width=4)
            d.line((icx, icy, icx + 10, icy + 4), fill=C_WHITE, width=4)
        else:
            d.arc((icx - 20, icy - 20, icx + 20, icy + 16), 180, 360, fill=C_WHITE, width=5)
            d.rounded_rectangle((icx - 22, icy - 4, icx - 12, icy + 14), radius=4, fill=C_WHITE)
            d.rounded_rectangle((icx + 12, icy - 4, icx + 22, icy + 14), radius=4, fill=C_WHITE)

        if with_text:
            f_p = get_font(FONT_BOLD_PATH, 28)
            d.text((130, 12 + 32), pill_configs[idx][1], fill=C_NAVY_BG, font=f_p)
        else:
            bar_w = [480, 440, 520, 430, 510][idx]
            d.rounded_rectangle((132, icy - 14, 132 + bar_w, icy + 14), radius=14, fill=(195, 212, 242))
            d.ellipse((pw - 42, icy - 16, pw - 10, icy + 16), fill=C_GREEN_OK if active_glow else C_BLUE_LIGHT)
        return img

    make_feature_pill(0, active_glow=False, with_text=False).save(sdir / "C01_COMPONENT_PILL_01_TON_KHO.png")
    make_feature_pill(1, active_glow=True, with_text=False).save(sdir / "C02_COMPONENT_PILL_02_CHOT_DON_GLOW.png")
    make_feature_pill(2, active_glow=False, with_text=False).save(sdir / "C03_COMPONENT_PILL_03_CHECK_BILL.png")
    make_feature_pill(4, active_glow=False, with_text=False).save(sdir / "C04_COMPONENT_PILL_05_TIEP_QUAN.png")

    left_card_clean = Image.open(OUT_DIR / "SCENE_03A_11s-16s_BO_OPA_VA_CHAT_3D" / "C02_COMPONENT_KHUNG_CHAT_3D_05_SCENE.png")

    def render_s3b_frame(step_idx: int, with_ae_text: bool = False) -> Image.Image:
        w, h = 1920, 1080
        canvas = Image.new("RGBA", (w, h), (11, 24, 58, 255))
        d = ImageDraw.Draw(canvas)
        for r in range(720, 80, -50):
            d.ellipse((480 - r, 540 - r, 480 + r, 540 + r), fill=C_BLUE_COBALT + (int(14 * (1 - r / 720)),))

        paste_center(canvas, render_bo_opa_svg(170, "#FFFFFF"), (165, 155))
        paste_center(canvas, left_card_clean.resize((760, 740), Image.LANCZOS), (510, 565))

        if with_ae_text:
            d.text((980, 95), "Chỉ 1 kết nối — OPA tự động hóa toàn bộ", fill=C_BLUE_GLOW, font=get_font(FONT_BOLD_PATH, 30))
            d.text((980, 138), "quy trình bán hàng trên Pancake:", fill=C_WHITE, font=get_font(FONT_BOLD_PATH, 34))
        else:
            d.rounded_rectangle((980, 105, 1680, 132), radius=13, fill=C_BLUE_GLOW)
            d.rounded_rectangle((980, 148, 1520, 174), radius=13, fill=C_WHITE)

        num_pills = [1, 2, 4, 5, 5][step_idx]
        for p_i in range(num_pills):
            py = 255 + p_i * 135
            is_glow = (step_idx == 4 and p_i in (1, 2)) or (p_i == num_pills - 1 and step_idx < 4)
            sc = 1.06 if (p_i == num_pills - 1 and step_idx < 4) else 1.0
            pill_im = make_feature_pill(p_i, active_glow=is_glow, with_text=with_ae_text)
            if sc != 1.0:
                pill_im = pill_im.resize((int(pill_im.width * sc), int(pill_im.height * sc)), Image.LANCZOS)
            paste_center(canvas, pill_im, (1400, py))

        if with_ae_text and step_idx >= 3:
            d.text((1260, 915), "Và nhiều hơn thế nữa!", fill=C_BLUE_GLOW, font=get_font(FONT_ACCENT_PATH, 32))

        return canvas

    f01, m02, m03, m04, f05, f05_ae = (
        render_s3b_frame(0), render_s3b_frame(1), render_s3b_frame(2),
        render_s3b_frame(3), render_s3b_frame(4, False), render_s3b_frame(4, True)
    )
    f01.convert("RGB").save(sdir / "F01_FIRST_FRAME_t0.0s.png")
    m02.convert("RGB").save(sdir / "M02_MOTION_STEP_t1.25s.png")
    m03.convert("RGB").save(sdir / "M03_MOTION_STEP_t2.50s.png")
    m04.convert("RGB").save(sdir / "M04_MOTION_STEP_t3.75s.png")
    f05.convert("RGB").save(sdir / "F05_LAST_FRAME_t5.0s.png")
    f05_ae.convert("RGB").save(sdir / "F05_LAST_FRAME_CO_CHU_AE.png")

    build_master_storyboard_sheet(
        sdir, "SCENE 03B", "GIẢI PHÁP PHẦN 2: SPLIT-SCREEN & 5 PILL TÍNH NĂNG NẢY THEO NHỊP 120 BPM", "00:16 – 00:22 (6.0s / Block 5s)",
        [
            ("F01 (0.00s)", "Trái: Chat+POS | Phải: Pill #1 nảy (108%)", f01),
            ("M02 (1.25s)", "Pill #2 (Tự chốt đơn POS) nảy đúng phách", m02),
            ("M03 (2.50s)", "Pill #3 & #4 nảy liên tiếp (stagger 0.50s)", m03),
            ("M04 (3.75s)", "Pill #5 (Nhân viên tiếp quản) hoàn tất cột phải", m04),
            ("F05 (5.00s)", "Đích: Khung sáng Glow Selector (H15) quét dọc", f05),
        ],
        [
            ("C01_PILL_01", "Pill 1: Tồn kho POS (Anchor: Tâm Icon trái)", Image.open(sdir / "C01_COMPONENT_PILL_01_TON_KHO.png")),
            ("C02_PILL_02_GLOW", "Pill 2 + Viền sáng Selection Frame (H15)", Image.open(sdir / "C02_COMPONENT_PILL_02_CHOT_DON_GLOW.png")),
            ("C03_PILL_03", "Pill 3: Xác minh bill chuyển khoản", Image.open(sdir / "C03_COMPONENT_PILL_03_CHECK_BILL.png")),
            ("C04_PILL_05", "Pill 5: Nhân viên tiếp quản bất cứ lúc nào", Image.open(sdir / "C04_COMPONENT_PILL_05_TIEP_QUAN.png")),
        ],
        [
            "• 05_Scene_Button01..05 (5 Feature Pills):",
            "  - Anchor Point: Tâm vòng tròn Icon trái [54%, Y_i]",
            "  - Scale Pop: 0% -> 108% -> 100% (12 frames)",
            "  - Position X: +80px -> 0px (Rule R10)",
            "  - Stagger: 0.50s (15f @ 30fps, khớp 120 BPM)",
            "  - Expression: sourceRectAtTime() tự co giãn",
            "• GLOW_SELECTOR_FRAME (Cơ chế H15 o ping.mp4):",
            "  - Trượt dọc Y từ Pill 1 -> Pill 5 (Out 75%/In 75%)",
            "• SFX: ui-wood-marimba-tick (A5 -> C#6 -> E6)"
        ]
    )


def build_scene_04():
    sdir = OUT_DIR / "SCENE_04_22s-30s_GIAI_PHONG_SUC_LAO_DONG"
    sdir.mkdir(parents=True, exist_ok=True)
    base_s4 = Image.open(AI_DIR / "chu_shop_scene4_thanh_thoi_base.png").convert("RGBA")

    relief_texts = [
        "Không cần tạo App Facebook phức tạp",
        "Không cần gõ lại một câu hỏi hàng trăm lần",
        "Không cần copy-paste từng SĐT, địa chỉ vào POS"
    ]

    def make_relief_card(idx: int, state: str = "checked", with_text: bool = False) -> Image.Image:
        cw, ch = 720, 116
        img = Image.new("RGBA", (cw + 24, ch + 24), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((16, 18, cw + 16, ch + 18), radius=32, fill=(0, 60, 153, 35))
        border_c = C_GREEN_OK if state == "checked" else C_ALERT
        d.rounded_rectangle((12, 12, cw + 12, ch + 12), radius=30, fill=C_WHITE + (255,), outline=border_c, width=4)

        icx, icy, ir = 70, 12 + ch // 2, 36
        if state == "strike":
            d.ellipse((icx - ir, icy - ir, icx + ir, icy + ir), fill=(240, 242, 248), outline=C_ALERT, width=4)
            d.rounded_rectangle((icx - 18, icy - 14, icx + 18, icy + 14), radius=4, fill=(160, 170, 190))
            d.line((icx - 26, icy + 26, icx + 26, icy - 26), fill=C_ALERT, width=7)
        else:
            d.ellipse((icx - ir, icy - ir, icx + ir, icy + ir), fill=C_GREEN_OK)
            d.line((icx - 18, icy + 2, icx - 4, icy + 16, icx + 20, icy - 14), fill=C_WHITE, width=7)

        if with_text:
            f_t = get_font(FONT_BOLD_PATH, 22)
            d.text((124, icy - 15), relief_texts[idx], fill=C_NAVY_BG, font=f_t)
        else:
            bw = [470, 510, 540][idx]
            d.rounded_rectangle((128, icy - 18, 128 + bw, icy - 2), radius=8, fill=(185, 205, 235))
            d.rounded_rectangle((128, icy + 8, 128 + int(bw * 0.65), icy + 22), radius=7, fill=(210, 224, 245))
            if state == "strike":
                d.line((124, icy + 2, 128 + bw, icy + 2), fill=C_ALERT, width=5)
        return img

    make_relief_card(0, state="strike", with_text=False).save(sdir / "C01_COMPONENT_THE_GACH_BO_THAO_TAC_CU.png")
    make_relief_card(0, state="checked", with_text=False).save(sdir / "C02_COMPONENT_THE_TICH_XANH_01.png")
    make_relief_card(1, state="checked", with_text=False).save(sdir / "C03_COMPONENT_THE_TICH_XANH_02.png")
    make_relief_card(2, state="checked", with_text=False).save(sdir / "C04_COMPONENT_THE_TICH_XANH_03.png")

    card_positions = [
        (440, 325),
        (1480, 325),
        (960, 140)
    ]

    def render_s4_frame(step_idx: int, with_ae_text: bool = False) -> Image.Image:
        canvas = base_s4.copy()
        bo_lap = render_bo_opa_svg(95, "#0068FF")
        paste_center(canvas, bo_lap, (1145, 665))

        cards_state = [
            [],
            [(0, "checked", 1.06)],
            [(0, "checked", 1.0), (1, "checked", 1.06)],
            [(0, "checked", 1.0), (1, "checked", 1.0), (2, "strike", 1.04)],
            [(0, "checked", 1.0), (1, "checked", 1.0), (2, "checked", 1.0)],
        ][step_idx]

        for c_idx, c_st, sc in cards_state:
            cim = make_relief_card(c_idx, state=c_st, with_text=with_ae_text)
            if sc != 1.0:
                cim = cim.resize((int(cim.width * sc), int(cim.height * sc)), Image.LANCZOS)
            paste_center(canvas, cim, card_positions[c_idx])

        return canvas

    f01, m02, m03, m04, f05, f05_ae = (
        render_s4_frame(0), render_s4_frame(1), render_s4_frame(2),
        render_s4_frame(3), render_s4_frame(4, False), render_s4_frame(4, True)
    )
    f01.convert("RGB").save(sdir / "F01_FIRST_FRAME_t0.0s.png")
    m02.convert("RGB").save(sdir / "M02_MOTION_STEP_t1.25s.png")
    m03.convert("RGB").save(sdir / "M03_MOTION_STEP_t2.50s.png")
    m04.convert("RGB").save(sdir / "M04_MOTION_STEP_t3.75s.png")
    f05.convert("RGB").save(sdir / "F05_LAST_FRAME_t5.0s.png")
    f05_ae.convert("RGB").save(sdir / "F05_LAST_FRAME_CO_CHU_AE.png")

    build_master_storyboard_sheet(
        sdir, "SCENE 04", "GIẢI PHÓNG SỨC LAO ĐỘNG: CHỦ SHOP THẢNH THƠI & 3 TÍCH XANH ✅", "00:22 – 00:30 (8.0s / Block 5s)",
        [
            ("F01 (0.00s)", "Chủ shop mỉm cười dang rộng 2 tay, Bò OPA trực laptop", f01),
            ("M02 (1.25s)", "Thẻ #1 (Trái) nảy lên & bật Tích xanh ✅ (106%)", m02),
            ("M03 (2.50s)", "Thẻ #2 (Phải) nảy lên & bật Tích xanh ✅", m03),
            ("M04 (3.75s)", "Thẻ #3 (Đỉnh) gạch chéo đỏ thao tác Copy-Paste", m04),
            ("F05 (5.00s)", "Đích: Cả 3 thẻ bật Tích xanh ✅ nổi quanh chủ shop", f05),
        ],
        [
            ("C01_STRIKE_CARD", "Thẻ gạch bỏ thao tác cũ (Trim Paths 0->100%)", Image.open(sdir / "C01_COMPONENT_THE_GACH_BO_THAO_TAC_CU.png")),
            ("C02_CHECK_CARD_1", "Thẻ Tích xanh #1: Không cần tạo App FB", Image.open(sdir / "C02_COMPONENT_THE_TICH_XANH_01.png")),
            ("C03_CHECK_CARD_2", "Thẻ Tích xanh #2: Không gõ lặp lại 100 lần", Image.open(sdir / "C03_COMPONENT_THE_TICH_XANH_02.png")),
            ("C04_CHECK_CARD_3", "Thẻ Tích xanh #3: Không copy-paste SĐT/ĐC", Image.open(sdir / "C04_COMPONENT_THE_TICH_XANH_03.png")),
        ],
        [
            "• SHOP_OWNER_RELAXED: Anchor Đáy lưng [50%, 74%]",
            "  - Ngả ghế thư giãn: Rotation 0° -> -4°",
            "  - Dang 2 tay: Shoulder Rotation +18°",
            "• RELIEF_CARDS_01..03:",
            "  - Vị trí vòng cung: (23%, 30%), (77%, 30%), (50%, 13%)",
            "  - Scale Pop: 0% -> 108% -> 100% (stagger 1.25s)",
            "  - Gạch đỏ Trim Paths: 0% -> 100% (0.25s)",
            "  - Checkmark ✅: Scale 0% -> 115% -> 95% -> 100%",
            "• SFX: scratch_005.ogg -> uisfx-minimal-success.wav"
        ]
    )


def build_scene_05():
    sdir = OUT_DIR / "SCENE_05_30s-36s_OUTRO_CTA_LOCKUP"
    sdir.mkdir(parents=True, exist_ok=True)

    comp_bo_outro = render_bo_opa_svg(460, "#0068FF")
    comp_bo_outro.save(sdir / "C01_COMPONENT_BO_OPA_OUTRO.png")

    w_ratio = 260 / WORD_PNG.height
    comp_word_opa = Image.new("RGBA", (int(WORD_PNG.width * w_ratio), 260), C_BLUE + (255,))
    comp_word_opa.putalpha(WORD_PNG.resize((int(WORD_PNG.width * w_ratio), 260), Image.LANCZOS).getchannel("A"))
    comp_word_opa.save(sdir / "C02_COMPONENT_CHU_OPA_WORDMARK.png")

    def make_cta_pill(width_px: int, scale_f: float = 1.0, ripple: bool = False, with_text: bool = False) -> Image.Image:
        h_px = 116
        W_c, H_c = 1180, 240
        img = Image.new("RGBA", (W_c, H_c), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        cx, cy = W_c // 2, H_c // 2
        w_cur = int(width_px * scale_f)
        h_cur = int(h_px * scale_f)
        if ripple:
            for rr_w, rr_h, a in [(w_cur + 90, h_cur + 60, 95), (w_cur + 170, h_cur + 110, 45)]:
                d.rounded_rectangle((cx - rr_w // 2, cy - rr_h // 2, cx + rr_w // 2, cy + rr_h // 2),
                                    radius=rr_h // 2, outline=C_BLUE_GLOW + (a,), width=5)
        d.rounded_rectangle((cx - w_cur // 2, cy - h_cur // 2 + 14, cx + w_cur // 2, cy + h_cur // 2 + 14),
                            radius=h_cur // 2, fill=(0, 104, 255, 65))
        d.rounded_rectangle((cx - w_cur // 2, cy - h_cur // 2, cx + w_cur // 2, cy + h_cur // 2),
                            radius=h_cur // 2, fill=C_BLUE + (255,), outline=C_BLUE_GLOW + (255,), width=3)
        if width_px >= 400:
            ir = int(34 * scale_f)
            icx = cx - w_cur // 2 + int(62 * scale_f)
            d.ellipse((icx - ir, cy - ir, icx + ir, cy + ir), fill=C_WHITE)
            d.polygon([(icx - 8, cy - 12), (icx + 14, cy), (icx - 8, cy + 12)], fill=C_BLUE)
            if with_text:
                f_cta = get_font(FONT_BOLD_PATH, int(31 * scale_f))
                d.text((icx + ir + 24, cy - int(20 * scale_f)), "Thử miễn phí ngay: chat.overpowers.agency", fill=C_WHITE, font=f_cta)
            else:
                bar_w = int(w_cur * 0.68)
                d.rounded_rectangle((icx + ir + 28, cy - 14, icx + ir + 28 + bar_w, cy + 14), radius=14, fill=C_WHITE)
        return img

    make_cta_pill(920, 1.0, ripple=False, with_text=False).save(sdir / "C03_COMPONENT_NUT_CTA_PILL.png")

    def make_cursor(scale_f: float = 1.0) -> Image.Image:
        S = int(110 * scale_f)
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        pts = [(8, 8), (8, int(S * 0.78)), (int(S * 0.30), int(S * 0.60)),
               (int(S * 0.46), int(S * 0.92)), (int(S * 0.60), int(S * 0.85)),
               (int(S * 0.44), int(S * 0.53)), (int(S * 0.72), int(S * 0.53))]
        d.polygon(pts, fill=C_NAVY_BG, outline=C_WHITE, width=5)
        return img

    make_cursor(1.0).save(sdir / "C04_COMPONENT_TRO_CHUOT_CLICK.png")

    def render_s5_frame(step_idx: int, with_ae_text: bool = False) -> Image.Image:
        w, h = 1920, 1080
        canvas = Image.new("RGBA", (w, h), (246, 249, 255, 255))
        d = ImageDraw.Draw(canvas)
        for r in range(680, 80, -50):
            d.ellipse((960 - r, 460 - r, 960 + r, 460 + r), fill=(215, 232, 255, int(18 * (1 - r / 680))))

        if step_idx == 0:
            bo_im = render_bo_opa_svg(520, "#0068FF", head_rot=-5.0, horn_l_rot=-28.0, horn_r_rot=28.0)
            paste_center(canvas, bo_im, (960, 440))
        elif step_idx == 1:
            bo_im = render_bo_opa_svg(480, "#0068FF", head_rot=0.0, horn_l_rot=0.0, horn_r_rot=0.0)
            paste_center(canvas, bo_im, (960, 440))
        else:
            bo_im = render_bo_opa_svg(350, "#0068FF")
            paste_center(canvas, bo_im, (660, 380))
            paste_center(canvas, comp_word_opa, (1140, 395))

            if with_ae_text:
                d.text((510, 565), "OPA Agent — AI bán hàng cho shop dùng Pancake", fill=C_NAVY_BG, font=get_font(FONT_BOLD_PATH, 38))
            else:
                d.rounded_rectangle((560, 575, 1360, 605), radius=15, fill=(190, 210, 242))

            if step_idx == 2:
                cta_im = make_cta_pill(320, 1.0, ripple=False, with_text=False)
                paste_center(canvas, cta_im, (960, 790))
                paste_center(canvas, make_cursor(1.0), (1480, 940))
            elif step_idx == 3:
                cta_im = make_cta_pill(920, 0.94, ripple=True, with_text=with_ae_text)
                paste_center(canvas, cta_im, (960, 790))
                paste_center(canvas, make_cursor(0.88), (1160, 825))
            else:
                cta_im = make_cta_pill(920, 1.0, ripple=True, with_text=with_ae_text)
                paste_center(canvas, cta_im, (960, 790))
                paste_center(canvas, make_cursor(1.0), (1185, 835))

        return canvas

    f01, m02, m03, m04, f05, f05_ae = (
        render_s5_frame(0), render_s5_frame(1), render_s5_frame(2),
        render_s5_frame(3), render_s5_frame(4, False), render_s5_frame(4, True)
    )
    f01.convert("RGB").save(sdir / "F01_FIRST_FRAME_t0.0s.png")
    m02.convert("RGB").save(sdir / "M02_MOTION_STEP_t1.25s.png")
    m03.convert("RGB").save(sdir / "M03_MOTION_STEP_t2.50s.png")
    m04.convert("RGB").save(sdir / "M04_MOTION_STEP_t3.75s.png")
    f05.convert("RGB").save(sdir / "F05_LAST_FRAME_t5.0s.png")
    f05_ae.convert("RGB").save(sdir / "F05_LAST_FRAME_CO_CHU_AE.png")

    build_master_storyboard_sheet(
        sdir, "SCENE 05", "OUTRO & CTA: BÒ OPA + LOGO LOCKUP & CLICK CHAT.OVERPOWERS.AGENCY", "00:30 – 00:36 (6.0s / Block 5s)",
        [
            ("F01 (0.00s)", "Bò OPA bật lên từ đáy U_HEAD (112%, sừng -28°)", f01),
            ("M02 (1.25s)", "Bò OPA khóa dáng chuẩn 100% giữa khung", m02),
            ("M03 (2.50s)", "Bò trượt sang trái (X=34%) lộ chữ OPA + Nút CTA nở", m03),
            ("M04 (3.75s)", "Chuột lướt tới Click: CTA lún 94% + Sóng Ripple", m04),
            ("F05 (5.00s)", "Đích: Lockup OPA + CTA chat.overpowers.agency", f05),
        ],
        [
            ("C01_BO_OPA", "Bò OPA xanh chuẩn V4 (Anchor: Đáy [50%, 100%])", comp_bo_outro),
            ("C02_WORD_OPA", "Chữ OPA gốc trang 3 PDF (Track-matte slide)", comp_word_opa),
            ("C03_CTA_PILL", "Nút CTA Pill (Morph Rect [116,116] -> [920,116])", Image.open(sdir / "C03_COMPONENT_NUT_CTA_PILL.png")),
            ("C04_CURSOR", "Trỏ chuột Vector (Anchor: Đỉnh mũi nhọn [0,0])", Image.open(sdir / "C04_COMPONENT_TRO_CHUOT_CLICK.png")),
        ],
        [
            "• OPA_BULL_MARK (Chuẩn KET-LUAN-VA-PROMPT-SUA.md):",
            "  - Anchor U_HEAD: Đáy giữa [50%, 100%]",
            "  - Scale: 0% -> 112% -> 95% -> 100% (0.60s)",
            "  - Sừng HORN_L/R: -40° -> +6° -> 0° (lệch 0.08s)",
            "  - Lockup Slide (1.25s–2.00s): X 50% -> 34%, Scale 72%",
            "• CTA_PILL_BUTTON: Anchor Tâm [50%, 74%]",
            "  - Nở ngang: Rect [116,116] -> [920,116] (R10)",
            "  - Click (3.50s): Scale 100% -> 94% -> 103% -> 100%",
            "• MOUSE_CURSOR: Đường cong Bézier + Click",
            "• SFX: click-chuot.wav + opa-sonic-logo-c.wav"
        ]
    )


# ==============================================================================
# BƯỚC 2: HỆ THỐNG STORYBOARD SẢN XUẤT CHUYÊN NGHIỆP (`00_STORYBOARD_SAN_XUAT`)
# ==============================================================================
def build_production_storyboards():
    sb_dir = OUT_DIR / "00_STORYBOARD_SAN_XUAT"
    sb_dir.mkdir(parents=True, exist_ok=True)

    f_h1 = get_font(FONT_BOLD_PATH, 32)
    f_h2 = get_font(FONT_BOLD_PATH, 22)
    f_b = get_font(FONT_MED_PATH, 16)
    f_sm = get_font(FONT_MED_PATH, 14)

    scenes_meta = [
        {
            "id": "SCENE 01",
            "folder": "SCENE_01_00s-05s_HOOK_QUA_TAI",
            "tc": "00:00 – 00:05 (5.0s)",
            "title": "HOOK: CHỦ SHOP QUÁ TẢI & ĐỒNG HỒ QUAY VÙ VÙ",
            "vo": "VO: \"Bạn mất bao nhiêu thời gian mỗi ngày để trả lời tin nhắn và lên đơn cho khách trên Pancake?\"",
            "tos": "TOS: BẠN MẤT BAO NHIÊU THỜI GIAN / để trả lời khách và lên đơn trên Pancake mỗi ngày?",
            "sfx": "SFX: fast-forward-whirr-sweep.wav + 8x pop-bubble (A4/C#5/E5) | BGM: 120 BPM căng thẳng",
            "cam": "CAMERA & AE: CAM_Null Push-in 96%->104% | Đồng hồ Anchor Tâm [76%,26%] Rot 0°->+1080° | 8 Bubbles Anchor Đuôi Scale 0->108->100%",
            "arrows": [((345, 65), (370, 88), "Rot +1080°"), ((190, 145), (170, 95), "Pop 108%"), ((315, 145), (335, 95), "Stagger 0.25s")]
        },
        {
            "id": "SCENE 02",
            "folder": "SCENE_02_05s-11s_XOAY_SAU_NOI_DAU",
            "tc": "00:05 – 00:11 (6.0s)",
            "title": "XOÁY SÂU NỖI ĐAU: HỘP THƯ 99+ & NHẬP ĐƠN POS THỦ CÔNG",
            "vo": "VO: \"Hãy thử tưởng tượng bạn quản lý nhiều trang bán hàng, mất hàng tiếng trả lời lặp lại giá, size, rồi nhập tay từng đơn...\"",
            "tos": "TOS: • Hàng chục cuộc chat bỏ dở  • Trả lời lặp đi lặp lại  • Lên đơn POS thủ công",
            "sfx": "SFX: ui-soft-ping-night.wav + ui-alert-soft-low.wav + uisfx-minimal-typing.wav",
            "cam": "CAMERA & AE: ChatList Step-scroll ΔY=-120px/0.5s | Badge 99+ Scale 0->115->100% | POS Form Wipe từ Anchor Top-Left [54%,38%] (Rule R10)",
            "arrows": [((110, 65), (110, 195), "Scroll ΔY"), ((380, 55), (305, 55), "Slide-in X"), ((265, 130), (395, 210), "Wipe R10")]
        },
        {
            "id": "SCENE 03A",
            "folder": "SCENE_03A_11s-16s_BO_OPA_VA_CHAT_3D",
            "tc": "00:11 – 00:16 (5.0s)",
            "title": "GIẢI PHÁP PHẦN 1: BÒ OPA HÚC MỞ MÀN & KHUNG CHAT 3D TỰ CHỐT ĐƠN",
            "vo": "VO: \"Giờ đây, chỉ với một lần kết nối, bạn đã có thể tự động hóa từ khâu tư vấn sản phẩm, kiểm tra tồn kho...\"",
            "tos": "TOS: GIẢI PHÁP ĐỘT PHÁ TỪ OPA AGENT — Tự trả lời khách theo tồn kho & Chốt đơn POS (#PK8921)",
            "sfx": "SFX: whoosh-cut-fast.wav + foley-snort-puff.wav + ui-card-snap-dock.wav + uisfx-minimal-success.wav",
            "cam": "CAMERA & AE: Bò OPA Charge (-8° -> +6° -> 0° quanh đáy U_HEAD) | Card 05_Scene 3D Y-Rot +32°->+4° + EdgeGlow | POS Card Mask Wipe",
            "arrows": [((45, 45), (90, 45), "Charge +6°"), ((140, 125), (210, 125), "3D Y-Rot 32°->4°"), ((145, 165), (145, 225), "POS Sync")]
        },
        {
            "id": "SCENE 03B",
            "folder": "SCENE_03B_16s-22s_SPLIT_SCREEN_5_PILLS",
            "tc": "00:16 – 00:22 (6.0s)",
            "title": "GIẢI PHÁP PHẦN 2: SPLIT-SCREEN & 5 PILL TÍNH NĂNG NẢY THEO NHỊP 120 BPM",
            "vo": "VO: \"...đến chốt đơn thẳng vào Pancake POS với OPA Agent!\"",
            "tos": "TOS: Chỉ 1 kết nối — 5 Pill: Tồn kho POS | Tự chốt đơn POS | Xác minh bill | Nhắc giỏ 24h | Nhân viên tiếp quản",
            "sfx": "SFX: 5x ui-wood-marimba-tick.wav (A5 -> C#6 -> E6) + ui-swish-accent-tick.wav | BGM: 120 BPM sôi động",
            "cam": "CAMERA & AE: 5 Feature Pills (05_Scene_Button02) Anchor Tâm Icon Trái [54%,Y_i] Scale 0->108->100% Stagger 0.50s | Glow Selector H15 quét dọc",
            "arrows": [((270, 75), (370, 75), "Pop 0.5s"), ((335, 65), (335, 215), "H15 Glow Sweep")]
        },
        {
            "id": "SCENE 04",
            "folder": "SCENE_04_22s-30s_GIAI_PHONG_SUC_LAO_DONG",
            "tc": "00:22 – 00:30 (8.0s)",
            "title": "GIẢI PHÓNG SỨC LAO ĐỘNG: CHỦ SHOP THẢNH THƠI & 3 TÍCH XANH ✅",
            "vo": "VO: \"Bạn không cần phải tạo App Facebook, không cần gõ lại từng câu trả lời quen thuộc, cũng không cần copy từng SĐT, địa chỉ...\"",
            "tos": "TOS: ✅ Không cần tạo App FB  |  ✅ Không cần gõ lại câu hỏi 100 lần  |  ✅ Không cần copy-paste SĐT, địa chỉ vào POS",
            "sfx": "SFX: 3x scratch_005.ogg (gạch bỏ) -> 3x catch-bright-ring.wav (bật tích xanh) | BGM: Sáng, thư giãn",
            "cam": "CAMERA & AE: Chủ shop ngả ghế -4°, dang rộng 2 tay +18° | 3 Thẻ gạch đỏ Trim Paths 0->100% rồi nổ Checkmark ✅ Scale 0->115->95->100%",
            "arrows": [((185, 165), (105, 145), "Tay +18°"), ((285, 165), (365, 145), "Tay +18°"), ((235, 65), (235, 38), "Pop ✅ 115%")]
        },
        {
            "id": "SCENE 05",
            "folder": "SCENE_05_30s-36s_OUTRO_CTA_LOCKUP",
            "tc": "00:30 – 00:36 (6.0s)",
            "title": "OUTRO & CTA: BÒ OPA + LOGO LOCKUP & CLICK CHAT.OVERPOWERS.AGENCY",
            "vo": "VO: \"OPA Agent — OPA lo phần trả lời, shop lo phần bán! Trải nghiệm miễn phí ngay tại chat.overpowers.agency.\"",
            "tos": "TOS: OPA Agent — AI bán hàng cho shop dùng Pancake  |  👉 Thử miễn phí ngay: chat.overpowers.agency",
            "sfx": "SFX: click-chuot.wav (tại 33.5s) + opa-sonic-logo-c.wav + sonic-logo-brass-chord.wav (-14 LUFS)",
            "cam": "CAMERA & AE: Bò OPA Reveal 0->112->95->100% -> Trượt trái X=50%->34% lộ chữ OPA | CTA Morph Rect [116,116]->[920,116] | Chuột Click 94% + Ripple",
            "arrows": [((235, 95), (160, 95), "Slide X 34%"), ((235, 195), (345, 195), "Morph Pill"), ((395, 235), (285, 200), "Click Arc")]
        }
    ]

    # 1. Tạo `SB00_MASTER_DIRECTOR_STORYBOARD_30_FRAMES.png` (Toàn bộ 6 cảnh x 5 khung = 30 khung + Kịch bản & Thông số)
    W0, H0 = 2640, 2260
    sb0 = Image.new("RGB", (W0, H0), (10, 18, 40))
    d0 = ImageDraw.Draw(sb0)
    d0.rounded_rectangle((28, 20, W0 - 28, 96), radius=16, fill=(22, 38, 78), outline=C_BLUE_GLOW, width=2)
    d0.text((52, 34), "MASTER PRODUCTION STORYBOARD (30 FRAMES / 36s) — VIDEO 01: OPA AGENT CHO PANCAKE POS", fill=C_WHITE, font=f_h1)
    d0.text((52, 70), "Bảng phân cảnh đạo diễn kết hợp Google Omni Flash (First Frame -> 3 Motion Steps -> Last Frame + Components) & After Effects (Final_4k 3840x2160)", fill=(165, 210, 255), font=f_b)

    row_h = 345
    fw, fh = 316, 178
    for s_idx, sm in enumerate(scenes_meta):
        ry = 116 + s_idx * row_h
        d0.rounded_rectangle((28, ry, W0 - 28, ry + row_h - 14), radius=14, fill=(16, 28, 60), outline=(55, 90, 160), width=2)
        # Cột thông tin kịch bản bên trái (w=880)
        d0.rounded_rectangle((42, ry + 14, 910, ry + row_h - 28), radius=12, fill=(22, 38, 78), outline=C_BLUE_GLOW, width=2)
        d0.text((58, ry + 26), f"{sm['id']} | {sm['tc']} — {sm['title']}", fill=C_GOLD, font=f_h2)
        d0.text((58, ry + 64), sm["vo"][:98] + ("..." if len(sm["vo"]) > 98 else ""), fill=C_WHITE, font=f_b)
        if len(sm["vo"]) > 98:
            d0.text((58, ry + 88), sm["vo"][98:], fill=C_WHITE, font=f_b)
        d0.text((58, ry + 124), sm["tos"], fill=(150, 220, 255), font=f_sm)
        d0.text((58, ry + 158), sm["sfx"], fill=(120, 240, 180), font=f_sm)
        d0.text((58, ry + 192), sm["cam"][:105], fill=(255, 200, 120), font=f_sm)
        if len(sm["cam"]) > 105:
            d0.text((58, ry + 216), sm["cam"][105:], fill=(255, 200, 120), font=f_sm)

        # 5 khung hình F01 -> M02 -> M03 -> M04 -> F05 bên phải
        sfolder = OUT_DIR / sm["folder"]
        fnames = [
            ("F01 [FIRST]", "0.00s", "F01_FIRST_FRAME_t0.0s.png"),
            ("M02 [STEP 2]", "1.25s", "M02_MOTION_STEP_t1.25s.png"),
            ("M03 [STEP 3]", "2.50s", "M03_MOTION_STEP_t2.50s.png"),
            ("M04 [STEP 4]", "3.75s", "M04_MOTION_STEP_t3.75s.png"),
            ("F05 [LAST+AE]", "5.00s", "F05_LAST_FRAME_CO_CHU_AE.png"),
        ]
        for f_i, (flabel, ftc, ffile) in enumerate(fnames):
            fx = 935 + f_i * (fw + 18)
            fy = ry + 22
            bcol = C_GREEN_OK if f_i == 0 else (C_ALERT if f_i == 4 else C_BLUE_GLOW)
            d0.rounded_rectangle((fx - 3, fy - 3, fx + fw + 3, fy + fh + 42), radius=10, fill=(12, 22, 48), outline=bcol, width=2)
            im_thumb = Image.open(sfolder / ffile).convert("RGB").resize((fw, fh), Image.LANCZOS)
            sb0.paste(im_thumb, (fx, fy))
            d0.text((fx + 8, fy + fh + 8), f"{flabel} ({ftc})", fill=bcol, font=f_b)

            # Vẽ mũi tên nối giữa các khung
            if f_i < 4:
                ax0 = fx + fw + 3
                ay0 = fy + fh // 2
                d0.line((ax0, ay0, ax0 + 14, ay0), fill=C_GOLD, width=3)

    sb0.save(sb_dir / "SB00_MASTER_DIRECTOR_STORYBOARD_30_FRAMES.png")
    sb0.save(OUT_DIR / "00_TONG_QUAN_TOAN_BO_KICH_BAN_01.png")

    # 2. Tạo 3 Trang Storyboard Chi Tiết (`SB01`, `SB02`, `SB03` — mỗi trang 2 phân cảnh lớn + Motion Arrows trực quan)
    pairs = [
        ("SB01_STORYBOARD_PHAN_1_HOOK_VA_NOI_DAU.png", "STORYBOARD CHI TIẾT PHẦN 1 (00:00 – 00:11): HOOK QUÁ TẢI & XOÁY SÂU NỖI ĐAU", [0, 1]),
        ("SB02_STORYBOARD_PHAN_2_GIAI_PHAP_BO_OPA_CHAT_3D_5_PILLS.png", "STORYBOARD CHI TIẾT PHẦN 2 (00:11 – 00:22): BÒ OPA + KHUNG CHAT 3D (05_Scene) & 5 FEATURE PILLS", [2, 3]),
        ("SB03_STORYBOARD_PHAN_3_GIAI_PHONG_VA_OUTRO_CTA.png", "STORYBOARD CHI TIẾT PHẦN 3 (00:22 – 00:36): GIẢI PHÓNG SỨC LAO ĐỘNG & OUTRO CTA LOCKUP", [4, 5]),
    ]

    for out_name, page_title, idxs in pairs:
        Wp, Hp = 2560, 1680
        page = Image.new("RGB", (Wp, Hp), (12, 22, 46))
        dp = ImageDraw.Draw(page)
        dp.rounded_rectangle((28, 20, Wp - 28, 96), radius=16, fill=(24, 42, 86), outline=C_BLUE_GLOW, width=2)
        dp.text((52, 40), page_title, fill=C_WHITE, font=f_h1)

        for local_i, s_idx in enumerate(idxs):
            sm = scenes_meta[s_idx]
            sfolder = OUT_DIR / sm["folder"]
            by = 118 + local_i * 765
            dp.rounded_rectangle((28, by, Wp - 28, by + 740), radius=18, fill=(18, 32, 66), outline=C_BLUE_GLOW, width=2)

            # Tiêu đề Scene
            dp.rounded_rectangle((46, by + 16, Wp - 46, by + 68), radius=12, fill=(28, 48, 96))
            dp.text((66, by + 28), f"{sm['id']} ({sm['tc']}) — {sm['title']}", fill=C_GOLD, font=f_h2)

            # 5 khung lớn (464 x 261) có vẽ Motion Vector Arrows trực tiếp lên khung M03 & F05
            pw, ph = 468, 263
            files_5 = [
                ("F01 [FIRST FRAME - 0.00s]", "Khóa khung đầu trên Omni Flash", "F01_FIRST_FRAME_t0.0s.png"),
                ("M02 [MOTION 2/5 - 1.25s]", "Bắt đầu gia tốc (Out Influence 15.2%)", "M02_MOTION_STEP_t1.25s.png"),
                ("M03 [MOTION 3/5 - 2.50s]", "Cao trào chuyển động + Hướng Vector", "M03_MOTION_STEP_t2.50s.png"),
                ("M04 [MOTION 4/5 - 3.75s]", "Giảm chấn lò xo (Overshoot -> Settle)", "M04_MOTION_STEP_t3.75s.png"),
                ("F05 [LAST FRAME - 5.00s]", "Khóa khung đích + Lớp chữ AE", "F05_LAST_FRAME_CO_CHU_AE.png"),
            ]
            for f_i, (fhead, fsub, fn) in enumerate(files_5):
                fx = 48 + f_i * (pw + 26)
                fy = by + 86
                bcol = C_GREEN_OK if f_i == 0 else (C_ALERT if f_i == 4 else C_BLUE_GLOW)
                dp.rounded_rectangle((fx - 3, fy - 3, fx + pw + 3, fy + ph + 56), radius=12, fill=(12, 22, 48), outline=bcol, width=3 if f_i in (0, 4) else 2)
                panel_im = Image.open(sfolder / fn).convert("RGB").resize((pw, ph), Image.LANCZOS)
                page.paste(panel_im, (fx, fy))
                # Vẽ mũi tên chỉ hướng chuyển động (Motion Vector Arrows) lên khung giữa (M03)
                if f_i == 2:
                    for p_start, p_end, alabel in sm["arrows"]:
                        draw_motion_arrow(dp, (fx + p_start[0], fy + p_start[1]), (fx + p_end[0], fy + p_end[1]), C_GOLD, 4, alabel)
                dp.text((fx + 10, fy + ph + 8), fhead, fill=bcol, font=f_b)
                dp.text((fx + 10, fy + ph + 32), fsub, fill=C_WHITE, font=f_sm)

            # Hàng dưới của mỗi Scene: Bảng kịch bản thu âm (VO, TOS, SFX) + 4 Ảnh Thành Phần (Components)
            dp.rounded_rectangle((48, by + 422, 1380, by + 720), radius=14, fill=(14, 24, 52), outline=(80, 125, 205), width=2)
            dp.text((68, by + 438), "THÔNG TIN SẢN XUẤT (VOICE-OVER / TEXT ON SCREEN / SFX / AE MOTION CONTROL):", fill=C_BLUE_GLOW, font=f_h2)
            dp.text((68, by + 478), sm["vo"], fill=C_WHITE, font=f_b)
            dp.text((68, by + 518), sm["tos"], fill=(155, 220, 255), font=f_b)
            dp.text((68, by + 558), sm["sfx"], fill=(120, 240, 180), font=f_b)
            dp.text((68, by + 598), sm["cam"], fill=(255, 205, 110), font=f_b)
            dp.text((68, by + 642), "-> Quy tắc Omni Flash: Nạp F01 vào [First Frame], F05 (bản không chữ) vào [Last Frame], C01..C04 vào [Ingredients].", fill=C_GOLD, font=f_b)

            # 4 ô Component bên phải dưới
            dp.rounded_rectangle((1405, by + 422, Wp - 48, by + 720), radius=14, fill=(14, 24, 52), outline=C_GOLD, width=2)
            dp.text((1425, by + 438), "CÁC ẢNH THÀNH PHẦN (COMPONENT INGREDIENTS):", fill=C_GOLD, font=f_h2)
            comp_files = sorted(sfolder.glob("C0*_COMPONENT_*.png"))[:4]
            for c_i, cf in enumerate(comp_files):
                cx = 1425 + c_i * 265
                cy = by + 478
                cw_box, ch_box = 248, 185
                ccard = Image.new("RGBA", (cw_box, ch_box), (240, 245, 255, 255))
                cim = Image.open(cf).convert("RGBA")
                sr = min((cw_box - 20) / max(1, cim.width), (ch_box - 20) / max(1, cim.height))
                paste_center(ccard, cim.resize((max(1, int(cim.width * sr)), max(1, int(cim.height * sr))), Image.LANCZOS), (cw_box // 2, ch_box // 2))
                page.paste(ccard.convert("RGB"), (cx, cy))
                dp.rounded_rectangle((cx - 2, cy - 2, cx + cw_box + 2, cy + ch_box + 34), radius=8, outline=C_GOLD, width=2)
                dp.text((cx + 6, cy + ch_box + 8), cf.stem[:26], fill=C_WHITE, font=f_sm)

        page.save(sb_dir / out_name)


if __name__ == "__main__":
    print("1. Updating Character & Rig Sheets...")
    build_character_sheets()
    print("2. Building 6 Timeline Scene Packs...")
    build_scene_01()
    build_scene_02()
    build_scene_03a()
    build_scene_03b()
    build_scene_04()
    build_scene_05()
    print("3. Building Production Storyboard Pack (SB00 -> SB03)...")
    build_production_storyboards()
    print("COMPLETED ALL STORYBOARDS & SCENE PACKS!")
