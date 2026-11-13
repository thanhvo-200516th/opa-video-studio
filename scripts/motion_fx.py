"""Motion FX: chữ, chuyển cảnh và gợi ý SFX theo các reel mẫu (Newbie Edit, 1cho.mejia, Fauzaib…) — 2026-11-04.

Mở rộng `text_fx.FX` (giữ nguyên 24 hiệu ứng @__dviet) bằng:
  chữ:        type_in / type_out, caption2, keyword_tpl, collage, word_pop, label_quote
  chuyển cảnh: join (flash / zoom / whip / glitch / leak / slide), strip_reveal, grid_reveal, leak_overlay, cut_burst
  SFX:        mỗi hàm ghi `self.cues` = [{"t", "kind", "dur"?, "why"}] với `kind` thuộc assets/motion-fx/sfx_catalog.json
              → `sfx_auto.plan_sfx(fx.cues, words, end, name)` chọn file, căn mốc, chỉnh mức theo giọng.

Số đo và lúc nên dùng: references/motion-fx.md. Toạ độ khung 1080×1920, thời gian là giây trên timeline.
"""
from __future__ import annotations

import random
import unicodedata
import os
import zlib
from pathlib import Path

TNEDIT_DIR = Path(os.environ.get("TNEDIT_DIR", str(Path.home() / "Thanh/Media/TNEDIT")))

import fx_gfx as G
import text_fx as _T
from text_fx import FONTS, FX, SHADOW, TRACKING, nfc, no_commas
from text_motion import ensure_motion

# Thêm 2 lớp ngay trên gfx_under (B-roll, dải, ô lưới): "band" = dải tối sau phụ đề, "trans" = overlay chuyển cảnh.
# Thứ tự dưới → trên: video / B-roll → dải tối → flash / leak / burn → chữ (dải tối nằm trên overlay làm flash ở vùng
# phụ đề tối đi, qa_sync báo lệch 2026-11-04). Lớp trống không sinh track nên FX cũ không đổi.
if ("band", "video") not in _T.LANES:
    _i = _T.LANES.index(("gfx_under", "video")) + 1
    _T.LANES[_i:_i] = [("band", "video"), ("trans", "video")]

FD = Path.home() / ".local/share/fonts"
FONTS.update({
    "mx_heavy": ("Montserrat", "ExtraBold", FD / "Montserrat_Static/Montserrat-ExtraBold.ttf"),
    "mx_med": ("Montserrat", "Medium", FD / "Montserrat_Static/Montserrat-Medium.ttf"),
    "mx_it": ("Montserrat", "SemiBold Italic", FD / "Montserrat_Static/Montserrat-SemiBoldItalic.ttf"),
    "mx_heavy_it": ("Montserrat", "ExtraBold Italic", FD / "Montserrat_Static/Montserrat-ExtraBoldItalic.ttf"),
    "pen": ("MTD Houstoner Script", "Regular", FD / "motion-fx/MTD Houstoner Script.otf"),
    "brush": ("SVN-Nexa Rush Script", "Regular", FD / "motion-fx/SVN-Nexa Rush Script.ttf"),
    "grotesk": ("SVN-Helvetica Neue", "Bold", FD / "motion-fx/SVN-Helvetica Neue Bold.ttf"),
    "grotesk_light": ("SVN-Helvetica Neue Light", "Regular", FD / "motion-fx/SVN-Helvetica Neue Light.ttf"),
    "anton": ("Anton", "Regular", FD / "Anton-Regular.ttf"),
    # chữ viết tay điệu cho dòng 2 phụ đề (người dùng 2026-11-04 lần 10); Flamingo / Beloved: phương án thay, đủ dấu Việt
    "cap_script": ("SVN-Mercury Script", "Bold", FD / "motion-fx/SVN-Mercury Script Bold.otf"),
    "flamingo": ("SVN-Flamingo Script", "Regular", FD / "motion-fx/SVN-Flamingo Script.otf"),
    "beloved": ("SVN-Beloved", "Regular", FD / "motion-fx/SVN-Beloved.otf"),
    # chữ viết tay MẢNH kiểu copperplate như @prodby.viet (lần 11): TF Whispers nằm trong bộ font Việt hoá ProdByViet
    "thin_script": ("TF Whispers", "Regular", FD / "motion-fx/TF-Whispers-xsaha0.ttf"),
    "pinyon": ("Pinyon Script", "Regular", FD / "motion-fx/PinyonScript-Regular.ttf"),
    # font hiện đại cho các đoạn không viết tay (máy không có UTM — thay bằng SF Pro Display / Be Vietnam Pro)
    "sf_bold": ("SF Pro Display", "Bold", FD / "apple-fonts/SF-Pro-Display-Bold.otf"),
    "sf_light_it": ("SF Pro Display", "Light Italic", FD / "apple-fonts/SF-Pro-Display-LightItalic.otf"),
    "bevn_xbold": ("Be Vietnam Pro", "ExtraBold", FD / "motion-fx/BeVietnamPro-ExtraBold.ttf"),
    "bevn_light_it": ("Be Vietnam Pro", "Light Italic", FD / "motion-fx/BeVietnamPro-LightItalic.ttf"),
})
TRACKING.update({"mx_heavy": -30, "mx_med": -10, "mx_it": -20, "mx_heavy_it": -30, "pen": 0, "brush": 0,
                 "grotesk": -35, "grotesk_light": -20, "anton": 0, "cap_script": 0, "flamingo": 0, "beloved": 0,
                 "thin_script": 0, "pinyon": 0, "sf_bold": -20, "sf_light_it": -10, "bevn_xbold": -25, "bevn_light_it": -10})
SCRIPT_ROLES = {"pen", "brush", "script", "cap_script", "flamingo", "beloved", "thin_script", "pinyon"}
# Phụ đề 2 dòng (dòng 1 trắng, dòng 2 vàng) — PHÂN TẦNG THEO ĐOẠN (người dùng chốt 2026-11-04 lần 11, mẫu @prodby.viet):
# mỗi đoạn 3–5 nhịp nói (cụm phụ đề) một kiểu font, xoay vòng CAPTION_STYLE_ROTATION; đoạn "script" chỉ ≤ SCRIPT_PER_SEGMENT
# cụm có dòng viết tay MẢNH (cộng chữ viết tay của từ khoá vẫn ≤ 4 trong 3–5 nhịp), cụm còn lại của đoạn về "mont".
# Không dùng viết tay quá nhiều. scale = cỡ dòng 2 so với dòng 1 (chữ viết tay x-height thấp nên to hơn).
CAPTION_STYLES = {
    "script": {"top": "mx_heavy", "bottom": "thin_script", "scale": 1.35},   # Montserrat + viết tay mảnh
    "mont": {"top": "mx_heavy", "bottom": "mx_heavy_it", "scale": 0.9},      # toàn Montserrat
    "bevn": {"top": "bevn_xbold", "bottom": "bevn_light_it", "scale": 0.95},  # font Việt hiện đại (thay UTM)
    "sf": {"top": "sf_bold", "bottom": "sf_light_it", "scale": 0.95},        # hiện đại mảnh (SF Pro như prodby)
    "script_bold": {"top": "mx_heavy", "bottom": "cap_script", "scale": 1.15},  # viết tay đậm (bản lần 10, không mặc định)
}
CAPTION_STYLE_ROTATION = ["script", "mont", "bevn", "script", "sf", "mont"]
# KIỂU XUẤT HIỆN (người dùng chốt 2026-11-05 lần 12): dùng đa dạng các kiểu chữ vào đã dạy (@__dviet, Newbie, 1cho…),
# không lặp một kiểu ở 2 lần liền nhau. Phụ đề xoay CAP_ENTRANCES theo từng cụm; chữ chính xoay KEY_ENTRANCES và LUÔN có
# điểm nhấn (phát sáng + kiểu vào mạnh: đập vào, nở ra, nhấp nháy…). "word" = hiện từng từ đúng lúc nói.
# Lần 15 (người dùng chốt 2026-11-05): 7 kiểu mạnh (đập vào, loé sáng…) KHÔNG hợp cho chữ phụ. Chữ phụ mặc định 7 kiểu nhẹ:
# gõ từng ký tự · từng từ nảy + click · gõ trong khung chọn · blur-in · hiện từng chữ khớp lời · quét lộ · từ viết tay thay nhau.
# Lần 17 (người dùng cho thử): gõ từng ký tự · phát sáng dâng lên · blur-in · nhấp nháy · đổi font liên tục · hiện từng chữ
# khớp lời. (Bộ lần 15 — từng từ nảy + click, khung chọn, quét lộ, viết tay thay nhau — vẫn gọi được qua entrance=…)
# Người dùng giữ bộ này (lần 18) nhưng "giảm nhấp nháy cho đỡ chói mắt": nhấp nháy chỉ 1 lần / 11 cụm, kiểu dịu (flicker_in).
CAP_ENTRANCES = ["type", "glow_rise", "blur", "flicker", "font_flip", "word", "type", "glow_rise", "blur", "font_flip", "word"]
LABEL_ENTRANCES = ["type", "glow_rise", "blur"]             # nhãn / từ dẫn ngắn (không nhấp nháy)
FLIP_ROLES = ["anton", "pen", "sf_light_it", "bevn_xbold"]  # đổi font liên tục: mỗi font 2 khung rồi về font chính
# Chữ chính: mỗi video dùng 10–15 kiểu (chọn theo tên video) trong bộ 24 kiểu của skill + các kiểu ghép (lần 15).
# flip3d / swing_in là 3D — tính vào 3–4 lần 3D mỗi video.
KEY_POOL = ["slam", "burst", "flicker", "pop", "glow_in", "fly", "drop", "slide_up", "slide_down", "type", "grey",
            "blur", "nudge", "dreamy", "wipe", "flip3d", "swing_in"]
KEY_KINDS_PER_VIDEO = (10, 15)
SCRIPT_PER_SEGMENT = 3
SEGMENT_MIN, SEGMENT_MAX = 3, 5
# Chữ KHÔNG viền (người dùng chốt 2026-11-04). Nổi bằng bóng đen mềm lệch dưới-phải như @magentx.ai (đo: lệch 4–6 px,
# nhoè ~10 px, đậm 70–80%); thêm độ lan (size) để dòng màu không chìm trên áo / tường sáng.
# Chữ key (từ khoá to) phát sáng cùng màu (wonder_glow) + bóng sẵn trong PNG; chữ phụ (phụ đề, từ dẫn, nhãn, viết tay)
# chỉ đổ bóng NHẸ — người dùng chốt 2026-11-04 (lần 5).
MX_SHADOW = {"color": "#000000", "opacity": 55, "blur": 8, "distance": 3, "angle": 135, "size": 0}
CAP_SHADOW = {"color": "#000000", "opacity": 75, "blur": 10, "distance": 3, "angle": 135, "size": 2}   # phụ đề: tương phản hơn
SCRIPT_SHADOW = {"color": "#000000", "opacity": 55, "blur": 7, "distance": 3, "angle": 135, "size": 0}
# dòng 2 phụ đề (vàng, mọi kiểu font): vàng sáng kém trắng + nét viết tay / Light mảnh → bóng đậm, lan rộng (QA lần 10–11:
# dòng vàng Montserrat với bóng CAP_SHADOW chỉ 3,4 : 1 trên áo xám)
CAP_SCRIPT_SHADOW = {"color": "#000000", "opacity": 100, "blur": 12, "distance": 3, "angle": 135, "size": 7}
CAP_CPS = 7                                    # phụ đề gõ ~7 ký tự/s (22 → 16 → 12 → 9 vẫn bị chê nhanh, 2026-11-04)
OUT_FADE = 8                                   # chữ ra = mờ dần 8 khung; KHÔNG xoá ngược ("chạy ra rồi thu vào", bị bỏ)
OVERLAY_DIR = TNEDIT_DIR / "05_Hieu_Ung_Chuyen_Canh/Overlay_Video"
OVERLAYS = {  # (file, giây vào ở đoạn sáng nhất — đo độ sáng 2026-11-04). Video ngang 16:9, vệt sáng nằm ở 2 mép
    # → xoay 90° rồi phóng 177,8% cho vừa khung dọc (phóng phủ 267% thì mất hết vệt sáng); blend Add
    "leak": (OVERLAY_DIR / "PR_Overlays/OVL_LightLeak_Swipe_black_background_with_blurred_light_refl_46237.mp4", 6.4),
    "flare": (OVERLAY_DIR / "PR_Overlays/OVL_FilmBurn_Flash_sunlight_flare_overlay_48494.mp4", 2.0),
    "burn": (OVERLAY_DIR / "Lorus_Film_Burn/Overlay 4K film burn transition SOUND EFFECTS ( Casey Neistat Style ).mp4", 5.6),
}
# Chuyển cảnh ghép sáng tạo dùng chuyển cảnh FilmCraft (flash_shake / rgb_glitch xử lý riêng trong combo()):
# phần tử thứ 4 (nếu có) = dời mốc tiếng so với điểm cắt, đo qa_sync Huy OPA 2: spring mạnh nhất trước cắt 0,1 s,
# spin_zoom tiếng ra sớm 0,1 s
COMBOS = {"spin_zoom": ("motion_camera", 8, ["whoosh"], 0.08), "light_sweep": ("light_sweep", 10, ["leak"]),
          "travel": ("travel_motion", 8, ["whoosh"]), "glass": ("glass", 8, ["whoosh"]),
          "liquid": ("liquid_distortion", 10, ["whoosh"]), "slice": ("slice", 8, ["whoosh"]),
          "spring": ("spring_motion", 10, ["whoosh"], -0.08), "spin": ("spin_motion", 8, ["whoosh"])}
# Dựng bằng keyframe trên clip trước / sau điểm cắt (người dùng 2026-11-04 lần 10: "chuyển cảnh sáng tạo hơn"):
# zoom_through (phóng vút vào → nảy ra), panel_wipe (3 tấm màu quét chéo), split_slide (khung tách đôi trượt ra)
KEYED = {"zoom_through", "panel_wipe", "split_slide"}
COMBO_KINDS = set(COMBOS) | {"flash_shake", "rgb_glitch"} | KEYED
PANEL_COLORS = ["#FFFFFF", "#FFC414", "#111111"]          # tấm cuối (trên cùng) phủ kín khung đúng lúc cắt
# kiểu nối điểm cắt → (hiệu ứng FilmCraft, số khung, SFX)
JOINS = {"flash": ("flash", 4, ["flash_hit"]), "zoom": ("zoom_blur", 5, ["whoosh"]),
         "whip": ("whip", 4, ["boom_pre", "whoosh"]), "glitch": ("glitch", 4, ["glitch"]),
         "leak": ("light_leak", 8, ["leak"]), "slide": ("push", 6, ["whoosh"]), "cross_zoom": ("cross_zoom", 5, ["whoosh"]),
         # 2026-11-06: họ chuyển cảnh ưu tiên — nháy (flicker) và màn trập máy ảnh (flash ngắn + tiếng shutter)
         "flicker": ("flicker", 6, ["glitch"]), "shutter": ("flash", 3, ["shutter"])}
# Bảng màu đo từ mẫu (Newbie Edit 9 reel, Fauzaib) — mỗi khối chữ một bảng, xoay vòng (người dùng muốn nhiều màu, 2026-11-04):
# key = gradient dọc [sáng, đậm] của từ khoá, glow cùng tông, script = chữ viết tay tương phản, cap = dòng 2 caption
# (bản bão hoà đậm như magentx — màu pastel chìm trên áo / tường sáng, 2026-11-04)
PALETTES = {
    "cyan": {"key": ["#B8F8FF", "#19E6F0"], "glow": "#19E6F0", "script": "#FCCB2B", "cap": "#19C6F5"},
    "gold": {"key": ["#FFF3B0", "#FFC414"], "glow": "#FFC414", "script": "#FFFFFF", "cap": "#FFC414"},
    "fire": {"key": ["#FFC27A", "#FF3D2E"], "glow": "#FF5A2B", "script": "#FCCB2B", "cap": "#FF7A1A"},
    "lime": {"key": ["#F7EC5A", "#6CE40C"], "glow": "#8CF02A", "script": "#DCCC7E", "cap": "#7EE01A"},
    "coral": {"key": ["#FFD9CC", "#F06C54"], "glow": "#F06C54", "script": "#FFFFFF", "cap": "#FF6A4D"},
    "pink": {"key": ["#FFC2EC", "#FF3FA4"], "glow": "#FF3FA4", "script": "#FFE66D", "cap": "#FF3FA4"},
    "red": {"key": ["#FF5A5A", "#D9140F"], "glow": "#E01E1E", "script": "#FFD84D", "cap": "#FF3B30"},   # đỏ thuần, không ngả cam/hồng
    "mint": {"key": ["#C9FFF0", "#14D9A0"], "glow": "#14D9A0", "script": "#FFD84D", "cap": "#18E0A8"},
    "blue": {"key": ["#A8CCFF", "#2F6BFF"], "glow": "#3D7BFF", "script": "#FFFFFF", "cap": "#9FD4FF"},
    "white": {"key": ["#FFFFFF", "#D9E6F5"], "glow": "#EAF4FF", "script": "#FFC414", "cap": "#FFFFFF"},
    "violet": {"key": ["#DCD2FF", "#8C6CFF"], "glow": "#8C6CFF", "script": "#FFFFFF", "cap": "#D6CCFF"},
}
# Phát sáng chữ key (người dùng chốt 2026-11-04 lần 9): mọi chữ key phát sáng cùng màu; vàng / trắng chỉ "siêu nhẹ".
GLOW = {"normal": {"radius": 20, "peak": 170, "hold": 70}, "soft": {"radius": 12, "peak": 55, "hold": 20}}
SOFT_GLOW = {"gold", "white"}
# Hồng, cam, xanh lá: không dùng; nếu buộc dùng (gọi tên bảng) thì chữ PHẢI phát sáng — kể cả chữ phụ.
GLOW_REQUIRED = {"fire", "coral", "pink", "lime"}
# 2026-11-06: chữ PHỤ không dùng cam / hồng / tím; nếu dùng một trong 3 màu đó thì phải phát sáng NHẸ (soft glow).
CAP_GLOW_REQUIRED = GLOW_REQUIRED | {"violet"}
# Người dùng chốt 2026-11-04 (lần 5–6): chữ dùng xanh lam (cyan), xanh ngọc (mint), xanh dương (blue), trắng, vàng, đỏ.
# Không cam / hồng / chanh (vẫn có trong PALETTES, không nằm trong vòng xoay). Phụ đề phía dưới KHÔNG dùng đỏ — đỏ chỉ cho key.
DEFAULT_ROTATION = ["gold", "cyan", "red", "gold", "violet", "blue", "mint", "white"]   # chữ key (đa dạng, không hồng/cam/xanh lá)
# Phụ đề: dòng 1 trắng + dòng 2 vàng song song ở mọi cụm (người dùng chốt 2026-11-04 lần 8; xanh trên áo sáng bị chìm)
# lần 12: phụ đề đa màu, trừ cam / hồng. Màu dòng phụ phải SÁNG (độ chói tương đối ≥ 0,45): đỏ #FF3B30 (3,0 : 1 trên áo
# trắng), xanh dương #5B9BFF và tím #B9A6FF (chìm trên áo / timeline tím) bị loại khi đo THCN 07 — tím, xanh dương dùng bản sáng.
CAPTION_ROTATION = ["mint", "gold", "cyan", "mint", "blue", "gold", "cyan"]   # lần 17: thêm xanh ngọc, đổi màu MỖI CỤM                                                  # dòng 2 phụ đề luôn vàng
VFX_DIR = TNEDIT_DIR / "03_VFX"
# Chuyển cảnh bằng overlay TNEDIT: khung sáng nhất (đo độ sáng từng khung 2026-11-04) đặt trúng điểm cắt, SFX căn đỉnh vào
# đúng khung đó. Overlay nằm DƯỚI lớp chữ (light leak từng làm chìm chữ) nhưng trên dải tối. variants = [(giây vào, giây sáng nhất)]. audio=True: dùng chính tiếng trong file (film burn Lorus có SFX khớp
# từng lần loé: loé 3,37–3,70 ↔ tiếng 3,54; 10,23–10,50 ↔ 10,32). Overlay nằm trên cùng (gfx_over) nên che cả dải tối.
TRANS = {
    "flash_burst": {"src": VFX_DIR / "Halo_Backlight_Flash/OVL_Flash_Out_Burst_60fps.mp4", "variants": [(0.0, 0.0)],
                    "dur": 0.75, "rotate": False, "blend": "add", "sfx": ["flash_hit"]},   # hình đổi tức thời: không tiếng hút trước
    "film_burn": {"src": OVERLAY_DIR / "Lorus_Film_Burn/Overlay 4K film burn transition SOUND EFFECTS ( Casey Neistat Style ).mp4",
                  # (vào, sáng nhất, độ trễ tiếng so với khung sáng — đo từng đoạn; 7,55 bỏ vì trễ 0,23 s)
                  "variants": [(10.05, 10.43, -0.04), (19.05, 19.44, -0.02), (24.5, 24.82, 0.04), (3.2, 3.5, 0.11)], "dur": 0.8,
                  "rotate": True, "blend": "screen", "audio": True},
    "light_leak": {"src": VFX_DIR / "Overlay_Video_PR/FTG_Overlay_LightLeaks_blurred_light_leaks_spin_on_a_black_backgroun_46236.mp4",
                   "variants": [(23.15, 23.57), (7.75, 8.13), (5.05, 5.4)], "dur": 0.85, "rotate": True, "blend": "add",
                   "boost": 20, "opacity": 80, "sfx": ["suck_in", "leak"]},      # boost 45 / 1,1 s làm mờ hẳn chữ (QA 2026-11-04)
    "glitch": {"src": VFX_DIR / "Overlay_Video_PR/FTG_Overlay_Glitch_screen_with_static_and_pixel_noise_4111.mp4",
               "variants": [(5.33, 5.43), (9.3, 9.4), (0.47, 0.57)], "dur": 0.23, "rotate": True, "blend": "screen",
               "opacity": 70, "sfx": ["glitch"], "v1": ("glitch", 4)},
    "film_roll": {"src": VFX_DIR / "Overlay_Video_PR/FTG_Overlay_Glitch_vintage_film_roll_effect_with_countdown_4421.mp4",
                  "variants": [(6.7, 7.0), (0.7, 0.97), (2.0, 2.27)], "dur": 0.6, "rotate": True, "blend": "screen",
                  "sfx": ["film"]},
}


def lighten(hex_: str, amt: float = 0.45) -> str:
    """Màu sáng hơn cùng tông (đầu kia của gradient từ khoá)."""
    h = hex_.lstrip("#")
    rgb = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(c + (255 - c) * amt):02X}" for c in rgb)


def _stacked_marks(text: str) -> bool:
    """Có chữ mang 2 dấu chồng phía trên (ầ, ể, ỗ…) → cần giãn dòng ≥ 1,28 × cỡ (rules.md mục 2)."""
    return any(sum(unicodedata.combining(m) > 0 and m != "\u0323" for m in unicodedata.normalize("NFD", ch)) >= 2
               for ch in nfc(text))


class MotionFX(FX):
    ALLOW_CAPTION_BAND = False      # luật B15 (2026-11-11): không dải tối dưới chữ phụ
    def __init__(self, *args, palettes: list[str] | None = None, name: str = "", key_seed: int | None = None, **kwargs):
        """palettes = thứ tự bảng màu xoay vòng (tên trong PALETTES); mặc định DEFAULT_ROTATION (vàng chủ đạo)."""
        super().__init__(*args, **kwargs)
        self.palettes = list(palettes or DEFAULT_ROTATION)
        self._pi = 0
        self._ci = 0
        self.cap_styles = list(CAPTION_STYLE_ROTATION)
        self._cs_i = self._cs_n = self._cs_script = 0      # đoạn phụ đề đang chạy: chỉ số kiểu · số cụm · số cụm viết tay
        self.cap_style_log: list[tuple[float, str]] = []    # (giây, kiểu) từng cụm — để kiểm luật phân tầng
        self._ent = {"cap": 0, "key": 0}
        self._ent_last = {"cap": None, "key": None}
        self._fly_side = 1
        self._lead_i = 0
        # mỗi video một bộ 10–15 kiểu cho chữ chính; key_seed do sổ luân phiên cấp, không có → theo tên video
        rnd = random.Random(zlib.crc32(name.encode()) if key_seed is None else key_seed)
        self.key_kinds = rnd.sample(KEY_POOL, rnd.randint(*KEY_KINDS_PER_VIDEO))
        self.entrance_log: list[tuple[float, str, str]] = []  # (giây, nhóm, kiểu vào) — để kiểm luật đa dạng

    def tracks(self, prefix: str = "") -> list[dict]:
        """Rule 4 (2026-11-11): trước khi xếp track, mọi lớp chữ được bổ sung vào / giữ / ra chuyển động (text_motion)."""
        if not getattr(self, "_motion_done", False):
            self.motion_stats = ensure_motion(self.items, self.fps)
            self._motion_done = True
        return super().tracks(prefix)

    def text(self, *args, **kwargs) -> dict:
        """Mọi chữ Motion FX mặc định bóng kiểu magentx (không viền)."""
        kwargs.setdefault("shadow", MX_SHADOW)
        return super().text(*args, **kwargs)

    def key_glow(self, c: dict, name: str, ramp: float = 0.35, soft: bool | None = None) -> dict:
        """Phát sáng chữ key theo bảng màu: thường hoặc siêu nhẹ (vàng, trắng). soft=True ép mức nhẹ (chữ phụ)."""
        g = GLOW["soft" if (name in SOFT_GLOW if soft is None else soft) else "normal"]
        return self._fx(c, "wonder_glow", {"threshold": 30, "radius": g["radius"], "use_color": True,
                                           "color": PALETTES[name]["glow"],
                                           "intensity": [[0, g["peak"]], [self._k(c, ramp), g["hold"]]]})

    def _pal_name(self, pal: dict) -> str:
        return next(k for k, v in PALETTES.items() if v is pal)

    def cap_pal(self) -> dict:
        """Bảng màu kế tiếp cho phụ đề (CAPTION_ROTATION — không đỏ)."""
        p = PALETTES[CAPTION_ROTATION[self._ci % len(CAPTION_ROTATION)]]
        self._ci += 1
        return p

    def pal(self, name: str | None = None) -> dict:
        """Bảng màu theo tên, hoặc bảng kế tiếp trong vòng xoay."""
        if name:
            return PALETTES[name]
        p = PALETTES[self.palettes[self._pi % len(self.palettes)]]
        self._pi += 1
        return p

    # ---------- kiểu vào / ra ----------
    def _keys_for(self, text: str, role: str, size: int, x0: float, t0: float, frames: int, reverse: bool,
                  hold: bool = True) -> list:
        """Key cho `crop.right`: mỗi khung lộ thêm (hoặc bớt) số ký tự theo bề rộng thật đo bằng PIL.
        hold=False → lộ mượt theo bề rộng (nét bút viết tay)."""
        keys, last = [], None
        w = self.advance(role, size, text)
        for f in range(frames + 1):
            if hold:
                k = -(-len(text) * f // frames)                   # ceil: số ký tự đã hiện
                k = len(text) - k if reverse else k
                done, px = k >= len(text), (self.advance(role, size, text[:k]) if k else 0)
            else:
                u = f / frames
                u = 1 - u if reverse else u
                done, px = u >= 1, w * u
            right = round(min(100.0, max(0.0, 0.0 if done else 100 - (x0 + px) / 10.8)), 2)
            if right != last:
                keys.append([round(t0 + f / self.fps, 4), right, "hold" if hold else "linear"])
                last = right
        return keys

    def _type_keys(self, c: dict, t0: float, frames: int, reverse: bool) -> list:
        text, role, size = c["text"], c["_role"], c["size"]
        x0 = c["position"][0] - (self.width(role, size, text) / 2 if c.get("align", "center") == "center" else 0)
        return self._keys_for(text, role, size, x0, t0, frames, reverse, hold=role not in SCRIPT_ROLES)

    def _crop_right(self, c: dict) -> dict:
        eff = next((e for e in c.get("effects", []) if e["effect"] == "crop" and "right" in e["params"]), None)
        if eff is None:
            eff = {"effect": "crop", "params": {"right": []}}
            c.setdefault("effects", []).insert(0, eff)
        return eff["params"]

    def type_in(self, c: dict, cps: float = 22, blur: float = 10, glow_flash: bool = False, cue: bool = True) -> dict:
        """Gõ từng ký tự + mờ → nét (Newbie 9/9): `crop.right` giữ khung theo bề rộng từng ký tự (FilmCraft
        `typewriter` quét cả khung theo lưới và vẽ con trỏ trắng — không dùng), blur 10 → 0 trong 8 khung.
        cue=False cho phụ đề chạy theo lời: mẫu có giọng không gắn tiếng gõ cho phụ đề."""
        n = max(3, min(36, round(len(c["text"]) / cps * self.fps), round(c["dur"] * self.fps * 0.8)))    # gõ xong trước 80% thời gian hiện
        prm = self._crop_right(c)
        prm["right"] = self._type_keys(c, 0.0, n, reverse=False) + [k for k in prm["right"] if k[0] > n / self.fps]
        self._fx(c, "gaussian_blur", {"blurriness": [[0, blur], [self._k(c, 8 / self.fps), 0, "easeIn"]]})
        if glow_flash:
            self._fx(c, "wonder_glow", {"threshold": 40, "radius": 20, "intensity": [[0, 150], [self._k(c, 0.3), 45]]})
        if cue:
            self.cues.append({"t": c["at"], "kind": "type", "dur": n / self.fps, "why": f"gõ chữ «{c['text'][:20]}»"})
        return c

    def type_out(self, c: dict, frames: int = 9, cue: bool = True) -> dict:
        """Xoá ngược từng ký tự ở cuối clip (8–10 khung), cùng cơ chế `crop.right`."""
        prm = self._crop_right(c)
        last_in = max((k[0] for k in prm["right"]), default=0.0)
        frames = max(2, min(frames, round((c["dur"] - last_in) * self.fps) - 2))
        t0 = round((c["dur"] * self.fps - frames - 1)) / self.fps
        if frames < 2 or t0 <= last_in:
            return c
        prm["right"] = [k for k in prm["right"] if k[0] < t0] + self._type_keys(c, t0, frames, reverse=True)
        if not prm["right"] or prm["right"][0][0] > 0:
            prm["right"].insert(0, [0, 0.0, "hold"])
        if cue:
            self.cues.append({"t": c["at"] + t0, "kind": "untype", "why": "xoá chữ"})
        return c

    def pen_in(self, c: dict, frames: int = 14, cue: bool = True) -> dict:
        """Chữ viết tay lộ mượt trái → phải đúng bề rộng chữ (như nét bút, Newbie 0,3–0,5 s)."""
        prm = self._crop_right(c)
        prm["right"] = self._type_keys(c, 0.0, frames, reverse=False)
        if cue:
            self.cues.append({"t": c["at"], "kind": "pen", "dur": frames / self.fps, "why": f"nét bút «{c['text'][:16]}»"})
        return c

    def wipe_in(self, c: dict, frames: int = 12, kind: str | None = "pen") -> dict:
        """Lộ trái → phải (chữ viết tay, PNG từ khoá)."""
        c["transition_in"] = {"effect": "linear_wipe", "frames": frames}
        if kind:
            self.cues.append({"t": c["at"], "kind": kind, "dur": frames / self.fps, "why": "chữ lộ trái → phải"})
        return c

    def fade_out(self, c: dict, frames: int = 6) -> dict:
        c["transition_out"] = {"effect": "cross_dissolve", "frames": frames}
        return c

    # ---------- kiểu xuất hiện (lần 12) ----------
    def next_entrance(self, group: str) -> str:
        """Kiểu vào kế tiếp cho nhóm "cap" (chữ phụ) / "key" (chữ chính): xoay vòng, không trùng lần trước."""
        pool = CAP_ENTRANCES if group == "cap" else self.key_kinds
        e = pool[self._ent[group] % len(pool)]
        if e == self._ent_last[group]:
            self._ent[group] += 1
            e = pool[self._ent[group] % len(pool)]
        self._ent[group] += 1
        self._ent_last[group] = e
        return e

    def _mid(self, c: dict, anchor: tuple | None = None) -> tuple:
        return tuple(anchor) if anchor else (c["position"][0], self.center_y(c))

    def word_in(self, c: dict, times: list[float] | None = None, step: float = 0.16) -> dict:
        """Hiện từng từ (@__dviet B11): `crop.right` giữ khung ở cuối mỗi từ; times = giây (trong clip) từng từ được nói."""
        text, role, size = c["text"], c["_role"], c["size"]
        x0 = c["position"][0] - (self.width(role, size, text) / 2 if c.get("align", "center") == "center" else 0)
        ends = [i for i, ch in enumerate(text) if ch == " "] + [len(text)]
        times = list(times or [])[:len(ends)]
        times += [(times[-1] if times else 0.0) + step * (k + 1) for k in range(len(ends) - len(times))]
        keys, last = [], None
        if times and times[0] > 1 / self.fps:            # dòng chưa được nói tới thì chưa hiện (khớp lời, lần 16)
            keys.append([0.0, 100.0, "hold"])
            last = 100.0
        for k, (e, t) in enumerate(zip(ends, times)):
            t = max(0.0, t) if k == 0 else min(max(t, (keys[-1][0] if keys else 0) + 1 / self.fps), c["dur"] * 0.8)
            right = 0.0 if e >= len(text) else round(max(0.0, 100 - (x0 + self.advance(role, size, text[:e])) / 10.8), 2)
            if right != last:
                keys.append([round(t, 4), right, "hold"])
                last = right
        self._crop_right(c)["right"] = self._mono(keys, c["dur"])
        return self._fx(c, "gaussian_blur", {"blurriness": [[0, 6], [self._k(c, 4 / self.fps), 0]]})

    def pop_in(self, c: dict, anchor: tuple | None = None, frm: float = 40) -> dict:
        """Nảy lên: 40 → 112 → 100%."""
        x, cy = self._mid(c, anchor)
        c["motion"] = {"anchor": [x, cy], "position": [x, cy],
                       "scale": [[0, frm], [self._k(c, 0.16), 112, "easeIn"], [self._k(c, 0.27), 100, "easeIn"]]}
        c["opacity"] = [[0, 0], [self._k(c, 0.06), 100]]
        return c

    def slam_in(self, c: dict, anchor: tuple | None = None) -> dict:
        """Đập vào: 190 → 96 → 100% trong 0,22 s, nhoè khi lao tới."""
        x, cy = self._mid(c, anchor)
        c["motion"] = {"anchor": [x, cy], "position": [x, cy],
                       "scale": [[0, 190], [self._k(c, 0.14), 96, "easeIn"], [self._k(c, 0.22), 100]]}
        c["opacity"] = [[0, 0], [self._k(c, 0.04), 100]]
        return self._fx(c, "gaussian_blur", {"blurriness": [[0, 14], [self._k(c, 0.12), 0, "easeIn"]]})

    def burst_in(self, c: dict, anchor: tuple | None = None) -> dict:
        """Nở ra: 70 → 100% mềm + mờ → nét."""
        x, cy = self._mid(c, anchor)
        c["motion"] = {"anchor": [x, cy], "position": [x, cy], "scale": [[0, 70], [self._k(c, 0.3), 100, "easeIn"]]}
        c["opacity"] = [[0, 0], [self._k(c, 0.1), 100]]
        return self._fx(c, "gaussian_blur", {"blurriness": [[0, 10], [self._k(c, 0.25), 0, "easeIn"]]})

    def flicker_in(self, c: dict) -> dict:
        """Nhấp nháy dịu khi vào: hiện, chùng một lần xuống 60 % rồi đứng (3 khung). Bản cũ tắt gần hẳn 2 lần (15 % / 30 %)
        bị chê chói mắt (lần 18)."""
        f = 1 / self.fps
        c["opacity"] = [[0, 0, "hold"], [f, 100], [self._k(c, 2 * f), 60], [self._k(c, 3 * f), 100]]
        return c

    def fly_in(self, c: dict, side: int | None = None, dx: float = 900) -> dict:
        """Bay từ ngoài khung vào (trái / phải luân phiên), nhoè ngang."""
        if side is None:
            side, self._fly_side = self._fly_side, -self._fly_side
        c["motion"] = {"position": [[0, [540 + side * dx, 960]], [self._k(c, 0.28), [540, 960], "easeIn"]]}
        c["opacity"] = [[0, 0], [self._k(c, 0.08), 100]]
        return self._fx(c, "directional_blur", {"direction": 90, "length": [[0, 70], [self._k(c, 0.28), 0, "easeIn"]]})

    def drop_in(self, c: dict, dy: float = 160) -> dict:
        """Rơi từ trên xuống, nảy nhẹ khi chạm."""
        c["motion"] = {"position": [[0, [540, 960 - dy]], [self._k(c, 0.2), [540, 972], "easeIn"],
                                    [self._k(c, 0.3), [540, 960], "easeIn"]]}
        c["opacity"] = [[0, 0], [self._k(c, 0.08), 100]]
        return self._fx(c, "directional_blur", {"direction": 0, "length": [[0, 40], [self._k(c, 0.2), 0, "easeIn"]]})

    def glow_in(self, c: dict, anchor: tuple | None = None) -> dict:
        """Loé sáng khi vào: sáng gắt 80 → 0 trong 0,3 s + phóng nhẹ 92 → 100%."""
        x, cy = self._mid(c, anchor)
        c["motion"] = {"anchor": [x, cy], "position": [x, cy], "scale": [[0, 92], [self._k(c, 0.3), 100, "easeIn"]]}
        c["opacity"] = [[0, 0], [self._k(c, 0.08), 100]]
        return self._fx(c, "brightness_contrast", {"brightness": [[0, 80], [self._k(c, 0.3), 0, "easeIn"]], "contrast": 0})

    def wipe_reveal(self, c: dict, d: float = 0.35) -> dict:
        """Quét lộ trái → phải mượt (crop.right theo bề rộng thật), không dùng chuyển cảnh."""
        text, role, size = c["text"], c["_role"], c["size"]
        x0 = c["position"][0] - (self.width(role, size, text) / 2 if c.get("align", "center") == "center" else 0)
        frames = max(4, min(round(d * self.fps), round(c["dur"] * self.fps * 0.6)))
        self._crop_right(c)["right"] = self._keys_for(text, role, size, x0, 0.0, frames, False, hold=False)
        return c

    def _mono(self, keys: list, dur: float) -> list:
        """Keyframe tăng dần, trong clip (≤ dur − 1 khung); trùng / lùi thời gian thì gộp vào key trước (giữ giá trị sau)."""
        f, out = 1 / self.fps, []
        for k in keys:
            t = round(min(max(0.0, k[0]), dur - f), 4)
            if out and t <= out[-1][0] + 1e-6:
                out[-1] = [out[-1][0], *k[1:]]
            else:
                out.append([t, *k[1:]])
        return out

    def _word_spans(self, c: dict, times: list[float]) -> list[tuple[int, int, float, float]]:
        """(chỉ số ký tự đầu, cuối, giây bắt đầu nói, giây từ kế) cho từng từ của clip chữ."""
        text, idx, spans = c["text"], 0, []
        words = text.split(" ")
        ts = list(times)[:len(words)]
        ts += [(ts[-1] if ts else 0.0) + 0.25 * (k + 1) for k in range(len(words) - len(ts))]
        for k, w in enumerate(words):
            nxt = ts[k + 1] if k + 1 < len(words) else ts[k] + max(0.2, len(w) / 12)
            spans.append((idx, idx + len(w), max(0.0, ts[k]), max(ts[k] + 1 / self.fps, nxt)))
            idx += len(w) + 1
        return spans

    def _right_at(self, c: dict, i: int) -> float:
        text, role, size = c["text"], c["_role"], c["size"]
        x0 = c["position"][0] - (self.width(role, size, text) / 2 if c.get("align", "center") == "center" else 0)
        return 0.0 if i >= len(text) else round(max(0.0, 100 - (x0 + self.advance(role, size, text[:i])) / 10.8), 2)

    def type_sync(self, c: dict, times: list[float], hold: bool = True) -> dict:
        """Gõ từng ký tự THEO LỜI (lần 16 — người dùng: chữ chưa khớp giọng): mỗi từ gõ trong lúc nó được nói (≥ 12 ký tự/s),
        dòng chưa được nói tới thì chưa hiện. hold=False (chữ viết tay): lộ mượt như nét bút."""
        f, keys, last = 1 / self.fps, [], None
        end = c["dur"] * 0.95
        for a, b, t0, t1 in self._word_spans(c, times):
            span = min(t1 - t0, (b - a) / 12)
            for j in range(1, b - a + 1):
                t = round(min(end, t0 + span * (j - 1) / max(1, b - a)) * self.fps) / self.fps
                r = self._right_at(c, a + j if a + j < b else (b + 1 if b < len(c["text"]) else len(c["text"])))
                if keys and t <= keys[-1][0] + 1e-6:
                    keys[-1][1] = r                   # nhiều ký tự trong cùng khung: giữ giá trị sau cùng
                elif r != last:
                    keys.append([round(t, 4), r, "hold" if hold else "linear"])
                last = keys[-1][1] if keys else r
        if keys and keys[0][0] > f:
            keys.insert(0, [0.0, 100.0, "hold"])
        self._crop_right(c)["right"] = self._mono(keys, c["dur"])
        return self._fx(c, "gaussian_blur", {"blurriness": [[0, 6], [self._k(c, 4 * f), 0]]})

    def wipe_sync(self, c: dict, times: list[float]) -> dict:
        """Quét lộ THEO LỜI: mép quét chạy đều theo mốc từng từ (mượt, không giữ khung)."""
        spans = self._word_spans(c, times)
        keys = [[0.0, 100.0, "hold"]] if spans[0][2] > 1 / self.fps else []
        for a, b, t0, t1 in spans:
            keys.append([round(t0, 4), self._right_at(c, a), "linear"])
        keys.append([round(min(c["dur"] * 0.95, spans[-1][3]), 4), 0.0, "linear"])
        out = []
        for k in keys:                                 # thời gian tăng dần, cách nhau ≥ 1 khung
            if out and k[0] <= out[-1][0] + 1 / self.fps - 1e-6:
                k = [round(out[-1][0] + 1 / self.fps, 4), *k[1:]]
            out.append(k)
        self._crop_right(c)["right"] = self._mono(out, c["dur"])
        return c

    def word_pop_in(self, c: dict, times: list[float] | None = None, click: bool = True) -> dict:
        """Từng từ nảy + click: hiện từng từ đúng lúc nói, mỗi từ cả dòng nảy nhẹ 96 → 100% và một tiếng click."""
        self.word_in(c, times)
        x, cy = c["position"][0], self.center_y(c)
        keys = [k[0] for k in self._crop_right(c)["right"]]
        f2 = 2 / self.fps
        sc = []
        for t in keys:
            if t + f2 < c["dur"] and (not sc or t >= sc[-1][0] + 1 / self.fps):   # từ quá sát nhau: bỏ cú nảy chồng
                sc += [[round(t, 4), 96], [round(t + f2, 4), 100]]
        if sc:
            c["motion"] = {"anchor": [x, cy], "position": [x, cy], "scale": sc}
        if click:
            for t in keys:
                self.cues.append({"t": c["at"] + t, "kind": "word_click", "why": f"từ nảy «{c['text'][:16]}»"})
        return c

    def nudge_in(self, c: dict, anchor: tuple | None = None) -> dict:
        x, cy = self._mid(c, anchor)
        c["motion"] = {"anchor": [x, cy], "position": [x, cy], "scale": [[0, 94], [self._k(c, 0.25), 100, "easeIn"]]}
        c["opacity"] = [[0, 0], [self._k(c, 0.1), 100]]
        return c

    def dreamy_in(self, c: dict) -> dict:
        """Mờ ảo (B16): nhoè dọc 25 → 2 trong 0,5 s."""
        c["opacity"] = [[0, 30], [self._k(c, 0.4), 100]]
        return self._fx(c, "gaussian_blur", {"blurriness": [[0, 25], [self._k(c, 0.5), 2, "easeIn"]], "dimensions": "Vertical"})

    def swing_in(self, c: dict) -> dict:
        """Xoay giả 3D vào (B9): trục Y 70° → 0 trong 0,35 s, có phối cảnh (tính là 1 lần 3D)."""
        c["opacity"] = [[0, 0], [self._k(c, 0.08), 100]]
        return self._fx(c, "rotate_3d", {"rot_y": [[0, 70], [self._k(c, 0.35), 0, "easeIn"]], "perspective": 60})

    def glow_rise(self, c: dict) -> dict:
        """Phát sáng dâng lên (B8): chữ hiện trong 0,12 s, quầng sáng cùng màu dâng 0 → 120 trong 0,35 s rồi lắng về 40."""
        c["opacity"] = [[0, 0], [self._k(c, 0.12), 100]]
        return self._fx(c, "wonder_glow", {"threshold": 30, "radius": 16, "use_color": True, "color": c.get("color", "#FFFFFF"),
                                           "intensity": [[0, 0], [self._k(c, 0.35), 120, "easeIn"], [self._k(c, 0.8), 40]]})

    def enter(self, c: dict, kind: str, anchor: tuple | None = None, word_times: list | None = None,
              cps: float = 7, cue: bool = False) -> dict:
        """Áp kiểu vào theo tên (CAP_ENTRANCES / KEY_ENTRANCES)."""
        if kind == "type":
            return self.type_in(c, cps=cps, cue=cue)
        if kind == "word":
            return self.word_in(c, word_times)
        if kind == "blur":
            return self.blur_in(c, 0.22, 18)
        if kind == "slide_up":
            return self.slide_up(c, dy=110, d=0.32)
        if kind == "pop":
            return self.pop_in(c, anchor)
        if kind == "slam":
            return self.slam_in(c, anchor)
        if kind == "burst":
            return self.burst_in(c, anchor)
        if kind == "flicker":
            return self.flicker_in(c)
        if kind == "fly":
            return self.fly_in(c)
        if kind == "drop":
            return self.drop_in(c)
        if kind == "glow_in":
            return self.glow_in(c, anchor)
        if kind == "glow_rise":
            return self.glow_rise(c)
        if kind == "grey":
            return self.grey_in(c, 0.24)
        if kind == "wipe":
            return self.wipe_reveal(c)
        if kind == "word_pop":
            return self.word_pop_in(c, word_times)
        if kind == "slide_down":
            return self.slide_down(c, dy=120, d=0.3)
        if kind == "nudge":
            return self.nudge_in(c, anchor)
        if kind == "dreamy":
            return self.dreamy_in(c)
        if kind == "flip3d":
            return self.flip3d_in(c)
        if kind == "swing_in":
            return self.swing_in(c)
        raise ValueError(f"kiểu vào lạ: {kind}")

    # ---------- chữ sau người (lần 19: "chữ đè lên mặt → cho text ra đằng sau và phóng to") ----------
    @staticmethod
    def _retime(v, off: float, d: float):
        """Keyframe của clip gốc → clip con bắt đầu muộn hơn `off` giây, dài `d` giây."""
        if not (isinstance(v, list) and v and isinstance(v[0], list)):
            return v
        keep = [[round(k[0] - off, 4), *k[1:]] for k in v if off - 1e-6 <= k[0] <= off + d + 1e-6]
        if keep:
            return keep
        before = [k for k in v if k[0] <= off]
        return (before[-1] if before else v[0])[1]

    def behind_person(self, block: list, v1: list, matte_src: str, matte_track: str = "Video 2", matte_offset: float = 0.0) -> list:
        """Đưa khối từ khoá ra SAU người bằng Track Matte (đảo alpha): chữ vẫn ở lớp trên cùng (không bị dải tối làm mờ) nhưng
        bị ẩn chỗ có người. Trả về clip người tách nền (ProRes 4444 từ `matte.py`, cùng khung với nguồn V1),
        khớp src / motion / transform / chuyển cảnh của từng clip V1 — người gọi đặt chúng thành track `matte_track`
        (ngay trên V1, dưới các dải tối → người vẫn tối như hình gốc). Từ dẫn (chữ nhỏ phía trên) giữ nguyên phía trước.
        `matte_offset` = giây của nguồn V1 mà file matte bắt đầu (`matte.py --start S` → S): `in` của clip matte = in V1 − S."""
        t0 = min(c["at"] for c in block)
        t1 = max(c["at"] + c["dur"] for c in block)
        tm = {"effect": "track_matte", "params": {"matte": matte_track, "composite": "Matte Alpha", "reverse": True}}
        for c in block:
            if c.get("_role") != "mx_med":                     # không che từ dẫn
                c.setdefault("effects", []).append(dict(tm, params=dict(tm["params"])))
        out = []
        for v in v1:
            a, b = max(t0, v["at"]), min(t1, v["at"] + v["dur"])
            if b - a < 1 / self.fps:
                continue
            off = a - v["at"]
            m = {"src": matte_src, "at": round(a, 4), "in": round(max(0.0, v.get("in", 0.0) + off - matte_offset), 4), "dur": round(b - a, 4),
                 "audio": False, "name": f"Người tách nền (che chữ) {len(out) + 1}"}
            if v.get("motion"):
                m["motion"] = {k: self._retime(val, off, b - a) for k, val in v["motion"].items()}
            fxs = [{"effect": e["effect"], "params": {k: self._retime(val, off, b - a) for k, val in e["params"].items()}}
                   for e in v.get("effects", []) if e["effect"] in ("transform", "camera_shake", "rgb_split")]
            if fxs:
                m["effects"] = fxs
            if abs(a - v["at"]) < 1e-3 and v.get("transition_in"):        # ranh giới trùng điểm cắt → cùng chuyển cảnh
                m["transition_in"] = dict(v["transition_in"])
            out.append(m)
        return out

    # ---------- chữ ----------
    def next_cap_style(self, ends_sentence: bool) -> str:
        """Kiểu phụ đề cho cụm kế tiếp: đoạn 3–5 cụm một kiểu (đổi ở cuối câu khi đã ≥ 3 cụm, bắt buộc đổi ở cụm thứ 5);
        đoạn "script" chỉ cho SCRIPT_PER_SEGMENT cụm đầu viết tay mảnh, các cụm sau về "mont"."""
        name = self.cap_styles[self._cs_i % len(self.cap_styles)]
        style = name
        if name == "script":                         # cửa sổ trượt 5 nhịp ≤ 3 cụm viết tay (kể cả "từ viết tay thay nhau")
            recent = [k for _, k in self.cap_style_log[-4:]].count("script")
            style = "script" if self._cs_script < SCRIPT_PER_SEGMENT and recent < SCRIPT_PER_SEGMENT else "mont"
            self._cs_script += style == "script"
        self._cs_n += 1
        if self._cs_n >= SEGMENT_MAX or (self._cs_n >= SEGMENT_MIN and ends_sentence):
            self._cs_i, self._cs_n, self._cs_script = self._cs_i + 1, 0, 0
        return style

    def caption2(self, top: str, bottom: str, at: float, dur: float, color: str | None = None, y: int | None = None,
                 size: int = 86, out: bool = True, sfx: bool = True, bottom_role: str | None = None,
                 style: str = "script", entrance: str | None = None, word_times: tuple | None = None) -> list:
        """M1 Caption 2 dòng chồng (Newbie): dòng 1 trắng, dòng 2 vàng; font theo `style` (CAPTION_STYLES — captions2 tự
        xoay mỗi đoạn 3–5 cụm), dòng 2 sát chân dòng 1 nhưng không đè dấu nặng; không viền — bóng đen lệch dưới-phải có độ lan (kiểu magentx,
        người dùng chốt 2026-11-04); gõ ~7 ký tự/s (CAP_CPS), mờ dần OUT_FADE khi out=True."""
        y = y or self.cap_y
        entrance = entrance or self.next_entrance("cap")       # gọi lẻ cũng xoay kiểu vào
        st = CAPTION_STYLES[style]
        r1, r2 = st["top"], bottom_role or st["bottom"]
        scale = st["scale"] if not bottom_role else (CAPTION_STYLES["script"]["scale"] if r2 in SCRIPT_ROLES else 0.9)
        if entrance == "script_swap" and r2 not in SCRIPT_ROLES:   # từ viết tay thay nhau: dòng 2 luôn là viết tay mảnh
            if [k for _, k in self.cap_style_log[-4:]].count("script") >= SCRIPT_PER_SEGMENT:
                entrance = "blur"                                    # giữ luật ≤ 3 cụm viết tay trong 5 nhịp (lần 11)
            else:
                r2, scale = "thin_script", CAPTION_STYLES["script"]["scale"]
        if r2 in SCRIPT_ROLES:                               # dòng viết tay to hơn → nâng cả khối để vẫn trong vùng phụ đề
            y -= round(0.45 * size)
        a = self.text(top, at, dur, r1, size, y=y, lane="text_low", shadow=CAP_SHADOW)
        s2 = round(a["size"] * scale)
        gap = self.ink_top(r2, s2, bottom) + self.mark_below(r1, a["size"], a["text"]) + 2
        if not self.mark_below(r1, a["size"], a["text"]):
            gap -= 0.12 * s2                                     # chạm nhẹ chân dòng trên như mẫu
        if _stacked_marks(bottom) and r2 not in SCRIPT_ROLES:   # chữ viết tay: gap đo theo nét thật đã đủ, giãn 1,28× làm rơi khỏi vùng
            gap = max(gap, 1.28 * s2)
        wt0 = word_times or (None, None)                  # mốc từng từ, giây tính từ `at` (cả 2 dòng)
        off2 = 0.15
        if wt0[1]:                                         # dòng 2 hiện khi bắt đầu nói tới nó (khớp lời, lần 16)
            off2 = min(max(0.15, wt0[1][0] - 0.05), max(0.15, dur - 0.5))
        b = self.text(bottom, at + off2, dur - off2, r2, s2, y=round(y + gap), color=color or self.cap_pal()["cap"],
                      lane="text_low", case=False, shadow=CAP_SCRIPT_SHADOW)
        self.cap_style_log.append((round(at, 2), "script" if r2 in SCRIPT_ROLES else style))
        forced = next((n for n in CAP_GLOW_REQUIRED if PALETTES[n]["cap"].lower() == b["color"].lower()), None)
        if forced:                                       # chữ phụ cam / hồng / tím / xanh lá: buộc phát sáng NHẸ
            self.key_glow(b, forced, soft=True)
        wt = (wt0[0], [t - off2 for t in wt0[1]] if wt0[1] else None)
        self.entrance_log.append((round(at, 2), "cap", entrance))
        extra: list = []
        if entrance == "box":                            # gõ trong khung chọn (B19, không dùng transition typewriter)
            if wt[0] and wt[1]:
                self.type_sync(a, wt[0])
                self.type_sync(b, wt[1], hold=r2 not in SCRIPT_ROLES)
            else:
                self.type_in(a, cps=CAP_CPS, cue=sfx)
                self.type_in(b, cps=CAP_CPS, cue=False)
            cy, w = self.center_y(a), round(self.width(r1, a["size"], a["text"]) + 70)
            p = G.select_box(self.gfx_dir, f"select_box_{len(self.items)}", 540, cy + 4, w, round(a["size"] * 1.3))
            bx = self.image(p, at, dur, lane="trans", name="Khung chọn chữ")
            bx["opacity"] = [[0, 0], [self._k(bx, 0.06), 100]]
            extra.append(self.fade_out(bx, OUT_FADE) if out else bx)
        elif entrance == "script_swap":                  # từ viết tay thay nhau (B6) ở dòng 2, dòng 1 blur-in
            self.blur_in(a, 0.22, 18)
            words, t_end = b["text"].split(), b["dur"]
            if t_end / max(1, len(words)) < 0.3:          # không đủ chỗ cho mỗi từ ≥ 0,3 s → cả dòng viết tay lộ như nét bút
                self.type_in(b, cps=CAP_CPS, cue=False)
                if out:
                    self.fade_out(b, OUT_FADE)
                    self.fade_out(a, OUT_FADE)
                return [a, b]
            self.items.remove(("text_low", b))
            ts = [max(0.0, t) for t in list(wt[1] or [])[:len(words)]]
            if len(ts) < len(words) or ts[0] > 0.4 * t_end or any(y - x < 0.3 for x, y in zip(ts, ts[1:])):
                ts = [k * t_end / len(words) for k in range(len(words))]   # lời quá dồn (THCN 07: 0,1 s/từ) → chia đều
            for k, (wd, t) in enumerate(zip(words, ts)):
                e = min(t_end, ts[k + 1] + 0.15) if k + 1 < len(words) else t_end
                if e - t < 2 / self.fps:
                    continue
                c = self.text(wd, b["at"] + t, e - t, r2, b["size"], y=b["position"][1], color=b["color"], lane="text_low",
                              case=False, shadow=CAP_SCRIPT_SHADOW)
                self.blur_in(c, 0.2, 20)
                if k + 1 < len(words):
                    c["transition_out"] = {"effect": "cross_dissolve", "frames": 4}
                elif out:
                    self.fade_out(c, OUT_FADE)
                extra.append(c)
            if out:
                self.fade_out(a, OUT_FADE)
            return [a, *extra]
        elif entrance == "font_flip":                    # đổi font liên tục (B23b) ở dòng 1, dòng 2 blur-in khi được nói
            f2 = 2 / self.fps
            for i, r in enumerate(FLIP_ROLES):
                extra.append(self.text(a["text"], a["at"] + i * f2, f2, r, a["size"], y=a["position"][1], color=a["color"],
                                       lane="text_low", case=False, shadow=CAP_SHADOW))
            shift = len(FLIP_ROLES) * f2
            a["at"], a["dur"] = round(a["at"] + shift, 4), round(a["dur"] - shift, 4)
            self.blur_in(b, 0.2, 14)
        elif entrance == "word_pop":                     # từng từ nảy; click chỉ ở dòng 1 (2 dòng cùng click quá dày)
            self.word_pop_in(a, wt[0])
            self.word_pop_in(b, wt[1], click=False)
        elif entrance in ("type", "wipe") and wt[0] and wt[1]:   # gõ / quét lộ chạy theo lời (lần 16)
            sync = self.type_sync if entrance == "type" else self.wipe_sync
            sync(a, wt[0])
            if entrance == "type":
                self.type_sync(b, wt[1], hold=r2 not in SCRIPT_ROLES)
            else:
                self.wipe_sync(b, wt[1])
        else:
            self.enter(a, entrance, word_times=wt[0], cps=CAP_CPS, cue=sfx and entrance == "type")
            if r2 in SCRIPT_ROLES and entrance in ("type", "word"):   # viết tay: lộ mượt như nét bút, theo lời
                self.type_sync(b, wt[1], hold=False) if wt[1] else self.type_in(b, cps=CAP_CPS, cue=False)
            else:
                self.enter(b, entrance, word_times=wt[1], cps=CAP_CPS)
        if out:
            self.fade_out(b, OUT_FADE)
            self.fade_out(a, OUT_FADE)
        return [a, b, *extra]

    def captions2(self, words: list[tuple[str, float]], end: float, max_words: int = 5, y: int | None = None,
                  color: str | None = None, skip: list[tuple[float, float]] = (), bottom_role: str | None = None,
                  style: str | None = None, entrance: str | None = None) -> list:
        """Phụ đề cả câu bằng caption2: cụm ≤ max_words từ (ngắt ở dấu câu), nửa đầu dòng trắng, nửa sau dòng màu
        (mặc định một bảng màu cho cả câu, câu sau đổi bảng). Không gắn SFX (mẫu có giọng không tick cho phụ đề).
        skip = [(từ, đến)] khoảng đang dùng word_pop / chữ khác."""
        fixed_color = color                               # lần 17: không truyền màu → mỗi cụm một màu (CAPTION_ROTATION)
        groups, cur = [], []
        for w, t in words:
            if any(a <= t < b for a, b in skip):
                continue
            cur.append((w, t))
            if len(cur) >= max_words or w.endswith((".", ",", "?", "!")):
                groups.append(cur)
                cur = []
        if cur:
            groups.append(cur)
        merged = []                                    # cụm hiện < 1,8 s thì gộp với cụm sau (≤ 8 từ): ít lần đổi chữ hơn
        for g in groups:
            if merged and len(merged[-1]) + len(g) <= 8 and g[0][1] - merged[-1][0][1] < 1.8 \
                    and not merged[-1][-1][0].endswith((".", "?", "!")):
                merged[-1] = merged[-1] + g
            else:
                merged.append(g)
        groups = merged
        out = []
        for gi, g in enumerate(groups):
            g_end = min(max(0.0, groups[gi + 1][0][1] - 0.05) if gi + 1 < len(groups) else end, end)   # hết đúng lúc cụm sau vào (không chồng)
            g_end = next((a for a, b in skip if g[0][1] < a < g_end), g_end)
            if len(g) < 2 or g_end - g[0][1] < 0.4:
                continue
            k = (len(g) + 1) // 2
            top = no_commas(" ".join(w for w, _ in g[:k]).rstrip(",."))
            bottom = no_commas(" ".join(w for w, _ in g[k:]).rstrip(",."))
            at = max(0.0, g[0][1] - 0.05)
            nxt = groups[gi + 1][0][1] if gi + 1 < len(groups) else None
            # cụm sau thay thẳng (đỡ rối mắt); chỉ mờ dần ở cuối câu / trước khoảng trống
            last = nxt is None or nxt - g_end > 0.2 or g[-1][0].endswith((".", "?", "!"))
            if last:                                         # mờ dần tâm ở cuối clip kéo thêm OUT_FADE/2 khung → kết thúc sớm chừng đó
                g_end -= OUT_FADE / 2 / self.fps             # (v2.5 C2: không chồng cụm sau; cụm thay thẳng giữ nguyên)
                if nxt is None:                              # v2.6: cụm CUỐI của lần gọi: mẫu dựng gọi captions2 TỪNG HÀNG với end = giờ vào
                    g_end -= 0.05                            # của hàng sau (cụm đầu hàng sau vào sớm 0,05 s) → chừa thêm 0,05 s như giữa các cụm
            st = style or self.next_cap_style(ends_sentence=g[-1][0].endswith((".", "?", "!")) or nxt is None)
            if any(ch.isdigit() for ch in bottom) and CAPTION_STYLES[st]["bottom"] in ("thin_script", "cap_script"):
                st = "mont"                                  # số trong font viết tay khó đọc (0 giống 9): dòng có số dùng Montserrat
            ent = entrance or self.next_entrance("cap")
            wt = ([t - at for _, t in g[:k]], [t - at for _, t in g[k:]])
            out += self.caption2(top, bottom, at, g_end - at, color=fixed_color or self.cap_pal()["cap"], y=y, sfx=False, out=last,
                                 bottom_role=bottom_role,
                                 style=st, entrance=ent, word_times=wt)
        return out

    def keyword_tpl(self, lead: str | None, key: str, script: str | None, at: float, dur: float,
                    palette: str | None = None, y: int | None = None, size: int = 150, entrance: str | None = None) -> list:
        """M2 Từ khoá kiểu template (Newbie): từ dẫn nhỏ gõ vào → 0,2 s sau từ khoá to gradient (bảng màu) gõ từng
        ký tự, loé trắng ký tự đầu + glow cùng tông → chữ viết tay màu tương phản lộ như nét bút, vào sau cùng;
        giữ (lấp lánh) → mờ dần (không xoá ngược). SFX: tick gõ · hit khi từ khoá rơi · nét bút · lấp lánh khi giữ ≥ 1,4 s."""
        y = y or self.key_y
        lead, key, script = (no_commas(x) if x else x for x in (lead, key, script))   # B13: không dấu phẩy trên hình
        pal = self.pal(palette)
        size = self.fit("mx_heavy", size, key)
        kt = nfc(key)
        p = G.gradient_text(self.gfx_dir, f"kw_{len(self.items)}", kt, str(FONTS["mx_heavy"][2]), size, 540, y, pal["key"], 0)
        k = self.image(p, at + 0.2, dur - 0.2, lane="text_img", name=f"Từ khoá · {key}")
        x0 = 540 - self.width("mx_heavy", size, kt) / 2
        ent = entrance or self.next_entrance("key")                 # lần 12: kiểu vào xoay vòng, luôn kèm phát sáng
        self.entrance_log.append((round(at, 2), "key", ent))
        if ent in ("type", "wipe"):                                 # gõ từng ký tự / quét lộ mượt (cần bề rộng chữ thật)
            n_in = max(12, min(45, round(len(kt) / 6 * self.fps))) if ent == "type" else 11
            k["effects"] = [{"effect": "crop", "params": {"right": self._keys_for(kt, "mx_heavy", size, x0, 0.0, n_in, False,
                                                                                   hold=ent == "type")}}]
            self._fx(k, "gaussian_blur", {"blurriness": [[0, 12], [self._k(k, 8 / self.fps), 0, "easeIn"]]})
        else:
            self.enter(k, ent, anchor=(540, y - 0.36 * size))
        self.fade_out(k, OUT_FADE)                                  # ra: mờ dần, không xoá ngược
        self.key_glow(k, self._pal_name(pal))
        self.cues.append({"t": k["at"], "kind": "key_hit", "why": f"từ khoá «{key}»"})
        out = [k]
        if lead:
            ly = round(y - self.ink_top("mx_heavy", size, key) - 16)
            ld = self.text(lead, at, dur, "mx_med", round(size * 0.36), y=ly, lane="text", shadow=CAP_SHADOW)
            if ent == "type":
                self.type_in(ld, cps=7)
            else:                                               # từ dẫn = chữ phụ: gõ / blur / quét lộ xoay vòng (lần 15)
                self.enter(ld, LABEL_ENTRANCES[self._lead_i % len(LABEL_ENTRANCES)], cps=7)
                self._lead_i += 1
            out.append(self.fade_out(ld, OUT_FADE))
        if script:
            ss = round(size * 0.78)
            sy = round(y + self.mark_below("mx_heavy", size, key) + self.ink_top("pen", ss, script) * 0.5)
            sx = 540 + self.width("mx_heavy", size, key) * 0.18
            s = self.text(script, at + 0.45, dur - 0.45, "pen", ss, x=sx, y=sy, color=pal["script"], lane="text_top",
                          case=False, shadow=SCRIPT_SHADOW)
            self.pen_in(s, 30)
            self.fade_out(s, OUT_FADE)
            out.append(s)
            if s["dur"] - 30 / self.fps >= 1.4:
                self.cues.append({"t": s["at"] + 30 / self.fps + 0.1, "kind": "sparkle", "why": f"giữ «{key}» phát sáng"})
        return out

    def collage(self, parts: list[tuple], end: float, y: int | None = None, color: str | None = None,
                palette: str | None = None) -> list:
        """M3 Ghép nhiều font theo cụm lời (Fauzaib): parts = [(chữ, giây, role, cỡ)], dòng sau dưới dòng trước;
        chữ viết tay to đè lên dòng trên ~20% (không chạm dấu dòng trên). Mỗi phần blur-in 0,12 s đúng lúc nói; giữ tới `end`."""
        y = y or self.key_y
        cpal = self.pal(palette)
        color = color or cpal["key"][1]
        out, base, prev = [], y, None
        big = max(parts, key=lambda p: p[3])
        for text, t, role, size in parts:
            if prev:
                pr, ps, ptxt = prev
                if role in SCRIPT_ROLES:
                    base += round(self.ink_bottom(pr, ps, ptxt) + self.ink_top(role, size, text) * 0.8)
                else:
                    base += round(self.mark_below(pr, ps, ptxt) + self.ink_top(role, size, text) + 0.22 * size)
            c = self.text(text, t, end - t, role, size, y=base, case=role not in SCRIPT_ROLES,
                          color=color if role in SCRIPT_ROLES else "#FFFFFF",
                          lane="text_top" if role in SCRIPT_ROLES else "text")
            self.blur_in(c, 0.12, 16)
            if role in SCRIPT_ROLES and (text, t, role, size) == big:
                self.key_glow(c, self._pal_name(cpal))           # chữ lớn = chữ key → phát sáng
            out.append(c)
            prev = (role, c["size"], c["text"])
        self.cues.append({"t": big[1], "kind": "key_hit", "why": f"chữ lớn «{big[0]}»"})
        return out

    def word_pop(self, words: list[tuple[str, float]], end: float, y: int | None = None, role: str = "grotesk",
                 size: int = 64, per_line: int = 3, click: bool = True) -> list:
        """M4 Hiện từng từ, mỗi từ một click (1cho outro / liệt kê): ≤ per_line từ / dòng, căn giữa,
        mỗi từ phóng 85 → 100% trong 2 khung. Muốn đều nhịp: mốc cách nhau 0,2 s."""
        y = y or self.cap_y
        out = []
        lines = [words[i:i + per_line] for i in range(0, len(words), per_line)]
        for li, line in enumerate(lines):
            l_end = lines[li + 1][0][1] if li + 1 < len(lines) else end
            txt = " ".join(w for w, _ in line)
            x = 540 - self.width(role, size, txt) / 2
            for w, t in line:
                c = self.text(w, t, l_end - t, role, size, x=x, y=y, align="left", lane="text_low", case=False)
                c["motion"] = {"anchor": [x + self.width(role, size, w) / 2, y - size * 0.35],
                               "position": [x + self.width(role, size, w) / 2, y - size * 0.35],
                               "scale": [[0, 85], [self._k(c, 2 / self.fps), 100]]}
                out.append(c)
                if click:
                    self.cues.append({"t": t, "kind": "word_click", "group": f"words@{words[0][1]:.2f}", "why": f"từ «{w}»"})
                x += self.advance(role, size, w + " ")
        return out

    def caption_band(self, at: float, dur: float, strength: float = 0.5, y0: int | None = None, y1: int | None = None,
                     fade: float = 0.0) -> dict:
        """Dải tối mềm sau vùng phụ đề. TẮT từ 2026-11-11 (luật B15, người dùng chốt: không để dải tối bên dưới chữ phụ) —
        trả None, không thêm clip; phụ đề nổi bằng bóng đen mềm. Chỉ bật lại khi người dùng yêu cầu: MotionFX.ALLOW_CAPTION_BAND = True."""
        if not self.ALLOW_CAPTION_BAND:
            return None
        y0 = y0 or self.cap_y - 110
        y1 = y1 or self.cap_y + 150                      # phủ cả dòng 2 viết tay (thấp hơn dòng nghiêng cũ ~60 px)
        p = G.caption_band(self.gfx_dir, f"caption_band_{y0}_{y1}_{round(strength * 100)}", y0, y1, strength)
        c = self.image(p, at, dur, lane="band", name="Dải tối sau phụ đề")
        if fade:
            c["opacity"] = [[0, 0], [self._k(c, fade), 100], [max(self._k(c, fade), c["dur"] - fade), 100], [c["dur"], 0]]
        return c

    def cover(self, png: str) -> dict:
        """Ảnh bìa (A6): 0,3 s đầu video, đủ tới 0,2 s, mờ hết ở 0,28 s. Chỉ làm khi người dùng yêu cầu (mặc định KHÔNG có ảnh bìa)."""
        c = self.image(png, 0.0, 0.3, lane="gfx_over", name="Ảnh bìa")
        c["name"] = "Ảnh bìa"                              # audit A6 nhận bằng đúng tên này
        c["opacity"] = [[0, 100], [0.2, 100], [0.28, 0]]
        return c

    def label_quote(self, text: str, at: float, dur: float, y: int = 290, size: int = 46,
                    entrance: str | None = None) -> dict:
        """M5 Nhãn in hoa trong ngoặc kép ở trên (1cho), ra cắt cứng. Kiểu vào: xoay CAP_ENTRANCES (chữ phụ, lần 14)."""
        c = self.text(f"“{text.upper()}”", at, dur, "grotesk", size, y=y, case=False, shadow=MX_SHADOW)
        ent = entrance or LABEL_ENTRANCES[self._lead_i % len(LABEL_ENTRANCES)]
        self._lead_i += 1
        return self.enter(c, ent, cps=9)

    # ---------- chuyển cảnh ----------
    def join(self, clip: dict, kind: str = "flash", cue_sfx: bool = True) -> dict:
        """Gắn chuyển cảnh vào đầu `clip` (clip sau điểm cắt trên V1/B-roll) + SFX tương ứng.
        kind: flash | zoom | whip | glitch | leak | slide | cross_zoom (bảng JOINS)."""
        eff, frames, sfx = JOINS[kind]
        clip["transition_in"] = {"effect": eff, "frames": frames}
        if cue_sfx:                                    # chuyển cảnh căn giữa điểm cắt: tiếng chỉ được vào từ nửa đầu của nó
            for s in sfx:
                self.cues.append({"t": clip["at"], "kind": s, "max_pre": frames / 2 / self.fps + 0.02,
                                  "why": f"chuyển cảnh {kind}"})
        return clip

    def transition(self, cut: float, kind: str, clip_after: dict | None = None, variant: int = 0) -> dict:
        """T0 Chuyển cảnh overlay TNEDIT (bảng TRANS): khung sáng nhất trúng `cut`, SFX căn đỉnh vào đó (hoặc tiếng có sẵn
        trong file). clip_after = clip ngay sau điểm cắt trên V1 / B-roll → gắn chuyển cảnh nền ngắn (luật: mọi điểm cắt
        có chuyển cảnh) — overlay che nó."""
        t = TRANS[kind]
        s_in, peak, *rest = t["variants"][variant % len(t["variants"])]
        lag = rest[0] if rest else 0.0                    # tiếng trong file trễ hơn hình bao nhiêu → bù lại
        pre = peak - s_in
        at = cut - pre - (1 / self.fps if pre == 0 else 0)
        c = self.image(str(t["src"]), at, t["dur"], lane="trans", name=f"Chuyển cảnh {kind}")   # trên dải tối, dưới chữ
        c.update({"in": round(s_in, 3), "audio": False, "blend": t["blend"]})
        if t.get("rotate"):
            c["motion"] = {"rotation": 90, "scale": 177.8}
        top = t.get("opacity", 100)
        fade = 2 / self.fps
        c["opacity"] = ([[0, 0], [fade / 2, top], [c["dur"] - fade, top], [c["dur"], 0]] if pre == 0 else
                        [[0, 0], [min(pre * 0.6, 0.2), top], [c["dur"] - fade, top], [c["dur"], 0]])
        if t.get("boost"):
            c["effects"] = [{"effect": "brightness_contrast", "params": {"brightness": t["boost"], "contrast": 20}}]
        if t.get("audio"):
            self.cues.append({"t": at, "kind": "own_audio", "src": str(t["src"]), "in": max(0.0, s_in + lag), "dur": t["dur"],
                              "why": f"tiếng có sẵn của {kind}"})
        for k in t.get("sfx", []):                     # tiếng không bắt đầu trước khi overlay hiện (đo bản xuất 2026-11-04)
            self.cues.append({"t": cut, "kind": k, "max_pre": pre + 1 / self.fps, "why": f"chuyển cảnh {kind}"})
        if clip_after is not None:
            eff, fr = t.get("v1", ("cross_dissolve", 2))
            clip_after["transition_in"] = {"effect": eff, "frames": fr}
        return c

    def _end_motion(self, clip: dict) -> dict:
        """Motion tĩnh bằng trạng thái cuối của clip (để lớp chồng khớp đúng khung đang hiện)."""
        mo = {k: (v[-1][1] if isinstance(v, list) and v and isinstance(v[0], list) else v)
              for k, v in (clip.get("motion") or {}).items()}
        return mo

    def zoom_through(self, cut: float, clip_before: dict, clip_after: dict, pre: float = 0.2, post: float = 0.3) -> dict:
        """Phóng vút vào (100 → 175% trong `pre` giây, tăng tốc, nhoè chuyển động) → cắt → cảnh sau 170 → 96 → 100% (nảy)."""
        blur = {"uniform_scale": True, "shutter_override": True, "shutter_angle": 360}
        d = clip_before["dur"]
        self._fx(clip_before, "transform", {**blur, "scale_height": [[max(0.0, d - pre), 100, "easeOut"], [d, 175]]})
        self._fx(clip_after, "transform", {**blur, "scale_height": [[0, 170], [self._k(clip_after, post * 0.6), 96, "easeIn"],
                                                                  [self._k(clip_after, post), 100, "easeIn"]]})
        clip_after["transition_in"] = {"effect": "zoom_blur", "frames": 4}
        # đỉnh hình đo được 0–0,07 s sau điểm cắt (cú nảy) → đỉnh whoosh +0,05 s (THCN 07 lệch −0,11 s khi đặt đúng cut)
        self.cues.append({"t": cut + 0.05, "kind": "whoosh", "max_pre": pre + 0.07, "why": "zoom xuyên"})
        return clip_after

    def panel_wipe(self, cut: float, colors: list[str] | None = None, travel: float = 0.18, hold: float = 2 / 30,
                   step_f: int = 2, tilt: float = -8.0) -> list:
        """3 tấm màu đặc nghiêng quét từ dưới lên, cách nhau `step_f` khung; tấm cuối phủ kín khung đúng `cut` trong
        `hold` giây (điểm cắt nằm dưới tấm) rồi cả bộ quét tiếp lên trên. Lane `trans`: dưới chữ, trên dải tối."""
        colors = colors or PANEL_COLORS
        out, n = [], len(colors)
        for i, col in enumerate(colors):
            at = self.snap(cut - travel - (n - 1 - i) * step_f / self.fps)
            p = G.solid_panel(self.gfx_dir, f"panel_{col.lstrip('#')}", col)
            c = self.image(p, at, 2 * travel + hold, lane="trans", name=f"Tấm màu {i + 1}")
            c["motion"] = {"rotation": tilt, "scale": 130,
                           # đi đều (không ease): ease làm tấm đen gần như đứng yên ~0,27 s — như tối sập (QA lần 10)
                           "position": [[0, [540, 3400]], [travel, [540, 960]], [travel + hold, [540, 960]],
                                        [c["dur"], [540, -1480]]]}
            out.append(c)
        # khung đổi mạnh nhất = tấm đầu (trắng) lướt qua giữa khung, không phải lúc tấm cuối phủ kín (qa_sync lần 10)
        self.cues.append({"t": out[0]["at"] + travel * 0.8, "kind": "whoosh", "max_pre": travel * 0.8, "why": "tấm màu quét vào"})
        # (bỏ whoosh lúc tấm quét ra: to hơn tiếng vào → đỉnh tiếng lệch +0,31 s so với khung đổi mạnh nhất, Huy OPA 2)
        return out

    def split_slide(self, cut: float, clip_before: dict, clip_after: dict, dur: float = 0.3) -> list:
        """Khung trước tách đôi trái / phải trượt ra hai bên (tăng tốc + nhoè ngang), lộ cảnh sau nảy 108 → 100%."""
        mo = self._end_motion(clip_before)
        px, py = mo.get("position", [540, 960])
        src_in = clip_before.get("in", 0.0) + clip_before["dur"]
        out = []
        for side, dx in (("left", -1), ("right", 1)):
            crop = {"left": 50 if side == "right" else 0, "right": 50 if side == "left" else 0}
            c = self._sub(clip_before["src"], src_in, cut, dur, crop, mo, 0, f"Tách đôi {side}")
            c["motion"] = {**mo, "position": [[0, [px, py], "easeOut"], [c["dur"], [px + dx * 1150, py]]]}
            self._fx(c, "directional_blur", {"direction": 90, "length": [[0, 0], [c["dur"], 90]]})
            out.append(c)
        self._fx(clip_after, "transform", {"uniform_scale": True, "scale_height": [[0, 108], [self._k(clip_after, 0.35), 100, "easeIn"]]})
        clip_after["transition_in"] = {"effect": "cross_dissolve", "frames": 1}
        # khung đổi mạnh nhất là ngay khung cắt (vết tách + cảnh sau nảy) → đỉnh whoosh ở đó, không vang trước
        self.cues.append({"t": cut, "kind": "whoosh", "max_pre": 0.03, "why": "khung tách đôi"})
        return out

    def combo(self, cut: float, kind: str, clip_after: dict, variant: int = 0, clip_before: dict | None = None) -> dict:
        """Chuyển cảnh ghép sáng tạo (COMBOS) — mỗi kiểu một cảm giác, SFX tấn công đúng khung đổi:
        flash_shake (flash burst + rung máy + phóng 108→100%), rgb_glitch (nhiễu + tách RGB tắt dần), spin_zoom (máy
        quay xoay + zoom), light_sweep (vệt sáng quét), travel (lao vào + motion blur), glass (kính vỡ), liquid (méo lỏng)."""
        if kind == "flash_shake":
            self.transition(cut, "flash_burst", clip_after=clip_after, variant=variant)
            mo = dict(clip_after.get("motion") or {})
            base = mo.get("scale", 100)
            base = base[0][1] if isinstance(base, list) else base
            if not isinstance(mo.get("scale"), list):                 # giữ push-in có sẵn, chỉ thêm cú phóng khi tĩnh
                mo["scale"] = [[0, base * 1.08], [self._k(clip_after, 0.25), base, "easeOut"]]
                clip_after["motion"] = mo
            self._fx(clip_after, "camera_shake", {"amount": [[0, 28], [self._k(clip_after, 0.35), 0]], "rotation": 1.5,
                                                  "zoom": 4, "frequency": 9, "complexity": 3, "motion_blur": 40})
            return clip_after
        if kind in ("zoom_through", "split_slide") and clip_before is None:
            kind = "spin_zoom"                                      # cần clip trước điểm cắt
        if kind == "zoom_through":
            return self.zoom_through(cut, clip_before, clip_after)
        if kind == "split_slide":
            self.split_slide(cut, clip_before, clip_after)
            return clip_after
        if kind == "panel_wipe":
            self.panel_wipe(cut)
            clip_after["transition_in"] = {"effect": "cross_dissolve", "frames": 1}
            return clip_after
        if kind == "rgb_glitch":
            self.transition(cut, "glitch", clip_after=clip_after, variant=variant)
            self._fx(clip_after, "rgb_split", {"mode": "Linear", "amount": [[0, 45], [self._k(clip_after, 0.22), 0]],
                                               "angle": 0})
            return clip_after
        eff, frames, sfx, *rest = COMBOS[kind]
        off = rest[0] if rest else 0.0
        clip_after["transition_in"] = {"effect": eff, "frames": frames}
        for k in sfx:
            # tiếng không vào trước hình: dời mốc sớm (off < 0) thì bớt đầu tiếng tương ứng (spring Huy OPA 2: sớm 0,12 s)
            self.cues.append({"t": cut + off, "kind": k, "max_pre": max(0.04, frames / 2 / self.fps + 0.02 + off),
                              "why": f"chuyển cảnh {kind}"})
        return clip_after

    def cut_fx(self, cut: float, kind: str, clip_after: dict, variant: int = 0, clip_before: dict | None = None):
        """Áp đúng kiểu chuyển cảnh mà cut_plan chọn: overlay TNEDIT (TRANS) · ghép sáng tạo (COMBO_KINDS) · JOINS.
        "zoom + punch": chỉ gắn zoom blur — đổi punch 100 ↔ 112% (cần tâm mặt) do build_spec làm; "vào B-roll" gọi
        grid_reveal / strip_reveal riêng (xem assets/motion-fx/example_build_spec.py)."""
        if kind == "zoom + punch":
            return self.join(clip_after, "zoom")
        if kind in TRANS:
            return self.transition(cut, kind, clip_after=clip_after, variant=variant)
        if kind in COMBO_KINDS:
            return self.combo(cut, kind, clip_after, variant=variant, clip_before=clip_before)
        return self.join(clip_after, kind)

    def _sub(self, src: str, src_in: float, at: float, dur: float, crop: dict, motion: dict | None, white_f: int,
             name: str) -> dict:
        c = self.image(src, at, dur, lane="gfx_under", name=name)
        c.update({"in": max(0.0, round(src_in, 3)), "audio": False})
        if motion:
            c["motion"] = dict(motion)
        self._fx(c, "crop", crop)
        if white_f:
            self._fx(c, "levels", {"out_black": [[0, 235], [self._k(c, white_f / self.fps), 0]]})
        return c

    def strip_reveal(self, src: str, src_in: float, cut: float, n: int = 4, step_f: int = 5, flash_f: int = 2,
                     width: float = 12.0, motion: dict | None = None, seed: int = 0, charge: bool = True) -> list:
        """T1 Dải dọc lộ dần (1cho 7/9): n dải của cảnh sau bật ra mỗi `step_f` khung trước `cut`, mỗi dải nháy trắng
        `flash_f` khung; ở `cut` cảnh sau lên V1 — gọi thêm join(clip_sau, "flash"). src_in = giây nguồn tại `cut`."""
        rnd = random.Random(seed)
        slots = list(range(int(100 // width)))
        rnd.shuffle(slots)
        xs = sorted(slots[:n], key=lambda _: rnd.random())
        out = []
        for i, sl in enumerate(xs):
            at = self.snap(cut - (n - i) * step_f / self.fps)
            left = sl * width + rnd.uniform(0, max(0.0, 100 - width * len(slots)))
            crop = {"left": round(left, 2), "right": round(100 - left - width, 2), "top": 7.5, "bottom": 7.5}
            out.append(self._sub(src, src_in - (cut - at), at, cut - at, crop, motion, flash_f, f"Dải dọc {i + 1}"))
            self.cues.append({"t": at, "kind": "bar_click", "group": f"strip@{cut:.2f}", "why": f"dải dọc {i + 1}"})
        if charge:
            self.cues.append({"t": out[0]["at"] - 0.15, "kind": "charge", "dur": cut - out[0]["at"] + 0.15,
                              "why": "nạp trước dải dọc"})
        return out

    def grid_reveal(self, src: str, src_in: float, cut: float, rows: int = 3, cols: int = 3, step: float = 0.07,
                    white_f: int = 3, motion: dict | None = None, seed: int = 1) -> list:
        """T2 Ô lưới lộ dần (1cho): rows×cols ô của cảnh sau bật ra lần lượt (ô giữa trước), mỗi ô trắng `white_f`
        khung rồi hiện hình; ô cuối chạm `cut` — gọi thêm join(clip_sau, "flash") hoặc để cắt thẳng."""
        cells = [(r, c) for r in range(rows) for c in range(cols)]
        mid = (rows // 2, cols // 2)
        rest = [x for x in cells if x != mid]
        random.Random(seed).shuffle(rest)
        order, out = [mid] + rest, []
        for i, (r, c) in enumerate(order):
            at = self.snap(cut - (len(order) - i) * step)
            crop = {"left": round(c * 100 / cols, 2), "right": round(100 - (c + 1) * 100 / cols, 2),
                    "top": round(r * 100 / rows, 2), "bottom": round(100 - (r + 1) * 100 / rows, 2)}
            out.append(self._sub(src, src_in - (cut - at), at, cut - at, crop, motion, white_f, f"Ô lưới {r + 1}.{c + 1}"))
            self.cues.append({"t": at, "kind": "grid_click", "group": f"grid@{cut:.2f}", "why": f"ô lưới {r + 1}.{c + 1}"})
        return out

    def leak_overlay(self, cut: float, kind: str = "leak", dur: float = 0.9) -> dict:
        """T3 Light leak / film burn (video TNEDIT, nền đen, blend Add) căn giữa điểm cắt, che chỗ nối. Video gốc tối
        (độ sáng TB 15–45/255) nên dùng Add + tăng sáng; kind: leak | flare | burn (film burn kiểu Casey Neistat)."""
        src, src_in = OVERLAYS[kind]
        c = self.image(str(src), cut - dur / 2, dur, lane="trans", name=f"Overlay {kind}")
        c.update({"in": src_in, "audio": False, "blend": "add", "motion": {"rotation": 90, "scale": 177.8},
                  "effects": [{"effect": "brightness_contrast", "params": {"brightness": 40, "contrast": 20}}],
                  "opacity": [[0, 0], [self._k(c, dur * 0.35), 100], [self._k(c, dur * 0.65), 100], [c["dur"], 0]]})
        self.cues.append({"t": c["at"], "kind": "leak", "why": f"overlay {kind}"})
        return c

    def cut_burst(self, shots: list[tuple[str, float]], start: float, first: float = 0.46, last: float = 0.17,
                  motion: dict | None = None) -> tuple[list, float]:
        """T4 Chuỗi cắt tăng tốc (Lens Distortions): shots = [(file, giây vào)], độ dài rút dần first → last,
        click mỗi lần cắt, riser bên dưới, hit ở cuối. Trả (clip, giây kết thúc) — clip sau nên join "flash"."""
        n, t, out = len(shots), self.snap(start), []
        for i, (src, s_in) in enumerate(shots):
            d = self.snap(first + (last - first) * i / max(1, n - 1)) or 1 / self.fps
            c = self.image(src, t, d, lane="gfx_under", name=f"Cắt nhanh {i + 1}")
            c.update({"in": s_in, "audio": False})
            if motion:
                c["motion"] = dict(motion)
            out.append(c)
            self.cues.append({"t": t, "kind": "bar_click", "group": f"burst@{start:.2f}", "why": f"cắt nhanh {i + 1}"})
            t = self.snap(t + d)
        self.cues.append({"t": start, "kind": "riser", "dur": t - start, "why": "dồn trước chuỗi cắt"})
        self.transition(t, "flash_burst")                                 # hit cuối có flash burst thật trên hình
        return out, t
