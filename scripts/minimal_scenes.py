#!/usr/bin/env python3
"""minimal_scenes — 6 kiểu cảnh đồ hoạ của hồ sơ minimal-edu còn thiếu so với video mẫu (Joseph | Video Editing), dùng cho
assets/motion-fx/build_spec_minimal.py (SCENE_GFX). Mỗi hàm nhận MotionFX + khoảng thời gian + ảnh (PNG / JPG tuỳ ý; sinh minh hoạ là
bước khác) và ghi clip vào `fx.items`, cue SFX vào `fx.cues`:

    painting     (nguyên tắc 3) tranh + hai lớp texture trôi chậm theo tranh, nhoè ngang lúc vào, đẩy máy 100 → 112 % cuối cảnh
    path_text    (nguyên tắc 4) nền giấy, một đường xanh vẽ liền: chạy tới từ → bị từ "cắt" → nối tiếp sang từ kế, máy lia theo đường
    path_illus   (nguyên tắc 5) đường + chấm trắng dẫn tới minh hoạ: "zigzag" (máy lia lộ vật) | "rise" (đường đi lên chủ thể)
    illus_mid    (nguyên tắc 7) minh hoạ nửa dưới trồi lên giữa, mép loang vào giấy, chữ ở nửa trên
    illus_side   (nguyên tắc 8) hình trừu tượng một bên + chữ bên kia
    quote_paper  (nguyên tắc 6) cảnh toàn chữ trên giấy thô trắng / xanh + hai dấu ngoặc kép

Cảnh nhiều màn hình dùng `World`: mọi lớp có toạ độ "thế giới" (màn hình sx, sy = lệch sx·1080, sy·1920) và một máy ảnh chung lia bằng
keyframe `motion.position` (bezier) + `directional_blur` đỉnh giữa lúc lia — cùng cách whip_pan, nhưng lia được nhiều lần trên cùng lớp.
Số đo chưa có trong hồ sơ ghi "profile key: …" để dời sang references/minimal-edu-style.json khi duyệt mắt xong.
"""
from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

import brooks_text as BT
import draw_path as DP
import fx_gfx as G
import style_profile as sp

W, H = 1080, 1920
# Vùng chữ cạnh hình trừu tượng (nguyên tắc 8): hình chiếm ~ 40 % bề ngang một bên, chữ ở phần còn lại (tránh cột nút phải x > 890).
BT.ZONES.setdefault("side_right", (640, 1300, 650, 500))   # hình bên trái, chữ bên phải
BT.ZONES.setdefault("side_left", (640, 1300, 430, 500))    # hình bên phải, chữ bên trái

# ---- tranh ----
PAINT_BAKED = 0.35                    # profile key: graphics.painting_baked_strength — texture nướng vào tranh (≤ graphics.painting_texture_max)
PAINT_LAYERS = ((30, (46, -34), "paint", 21), (22, (-40, 30), "paper", 22))   # profile key: graphics.painting_layers — (opacity % ≤ 50, trôi px cả cảnh, kind, seed)
LAYER_SCALE = 110                     # profile key: graphics.painting_layer_scale — lớp texture phóng 110 % để trôi không lộ mép
PUSH_SCALE, PUSH_FRAMES = 112, 10     # profile key: graphics.painting_push — đẩy máy 100 → 112 % trong 10 khung cuối (easeIn)
SLOW_ZOOM = 103                       # profile key: graphics.painting_slow_zoom — trước khi đẩy máy, tranh phóng chậm 100 → 103 %
ENTRY_BLUR = 80                       # profile key: graphics.painting_entry_blur — directional_blur 90° lúc vào (giảm về 0 trong 5–7 khung)
# ---- máy lia / nét ----
PAN_FRAMES, PAN_BLUR = 12, 70         # profile key: graphics.path_pan_frames / graphics.path_pan_blur — lia 12 khung, nhoè ngang đỉnh 70
LINE_GAP = 40                         # profile key: graphics.path_text_gap — nét dừng cách khối chữ 40 px (bị chữ "cắt")
PAN_TRIGGER_X = 250                   # profile key: graphics.path_pan_trigger — lia khi đầu nét còn cách mép phải 250 px
ZONE_CYCLE = ("mid_center", "lower")  # profile key: graphics.path_text_zones — vùng chữ xen kẽ giữa các điểm dừng (đủ chỗ trên / dưới cho nét)
STROKE_MIN_FRAMES = 6                 # nét ngắn hơn 6 khung = hai từ sát nhau quá, báo lỗi rõ
# ---- minh hoạ ----
MID_H, MID_FEATHER, MID_RISE_DY, MID_RISE_FRAMES = 1250, 170, 420, 16   # profile key: graphics.illus_mid — cao, độ loang mép, quãng trồi, số khung
SIDE_SIZE, SIDE_FEATHER, SIDE_SLIDE_FRAMES = (400, 1300), 120, 14       # profile key: graphics.illus_side — khung hình, độ loang, số khung trượt vào
TEX_OPACITY = 28                      # profile key: graphics.paper_texture_opacity — lớp texture giấy phủ cảnh minh hoạ / trích dẫn (multiply, ≤ 50)
ILLUS_BOX = {"zigzag": (760, 860), "rise": (640, 700)}   # profile key: graphics.path_illus_box — khung chứa minh hoạ của cảnh đường + minh hoạ
HERO_PAPER_ACCENT, HERO_BLUE_BG = "#123CE8", "#FFD84D"   # màu dòng chính của quote_paper trên giấy trắng / xanh (profile key: text.colors.accent)
KEYED = lambda v: isinstance(v, list) and bool(v) and isinstance(v[0], list)   # noqa: E731  giá trị motion là danh sách keyframe


def _prof() -> dict:
    return sp.load(name="minimal-edu")


def _paper(fx, gfx: Path, kind: str, seed: int, at: float, dur: float, name: str) -> dict:
    return fx.image(G.paper_bg(gfx, f"{name}_{kind}_{seed}", kind, seed), at, dur, lane="gfx_under", name=name)


def _texture(fx, gfx: Path, kind: str, seed: int, at: float, dur: float, opacity: int, drift: tuple, name: str) -> dict:
    """Lớp texture thô phủ multiply, trôi chậm `drift` px suốt `dur` (phóng LAYER_SCALE % để không lộ mép)."""
    if opacity > 50:
        raise ValueError(f"texture {opacity} % vượt 50 % (texture nặng bị chê)")
    c = fx.image(G.rough_texture(gfx, f"{name}_{kind}_{seed}", seed, kind), at, dur, lane="card", name=name)
    c["blend"], c["opacity"] = "multiply", opacity
    c["motion"] = {"scale": LAYER_SCALE, "position": fx._frame_keys(
        [[0, [540, 960]], [dur - 1 / fx.fps, [540 + drift[0], 960 + drift[1]]]], dur)}
    return c


# ============================================================ máy ảnh chung cho cảnh nhiều màn hình
class World:
    """Lớp có toạ độ "thế giới" + một máy ảnh lia bằng keyframe. `add(clip, screen)`: vị trí gốc của clip = motion.position tĩnh (mặc
    định tâm khung) cộng lệch màn hình (sx·1080, sy·1920). `pan(t0, frames, dx, dy)`: máy dời (dx, dy) px. `apply()`: ghi motion.position
    = gốc − vị trí máy cho từng clip (keyframe bezier ở hai đầu mỗi lần lia) và directional_blur đỉnh giữa lúc lia."""

    def __init__(self, fx):
        self.fx, self.layers, self.pans = fx, [], []

    def add(self, clip: dict, screen: tuple = (0, 0)) -> dict:
        pos = clip.get("motion", {}).get("position")
        if KEYED(pos):
            raise ValueError(f"clip «{clip.get('name')}» đã có keyframe motion.position — không thể đưa vào máy ảnh chung")
        bx, by = pos if pos else (540, 960)
        self.layers.append((clip, (bx + screen[0] * W, by + screen[1] * H)))
        return clip

    def pan(self, t0: float, frames: int, dx: float, dy: float = 0.0) -> float:
        """Lia từ giây t0 trong `frames` khung; trả giây kết thúc."""
        t0 = self.fx.snap(t0)
        t1 = round(t0 + frames / self.fx.fps, 4)
        self.pans = sorted([*self.pans, (t0, t1, dx, dy)])
        return t1

    def cam(self, t: float) -> tuple[float, float]:
        """Vị trí máy tại giây t (đang lia: smoothstep, gần đúng bezier)."""
        x = y = 0.0
        for t0, t1, dx, dy in self.pans:
            u = min(1.0, max(0.0, (t - t0) / (t1 - t0)))
            k = u * u * (3 - 2 * u)
            x, y = x + dx * k, y + dy * k
        return x, y

    def _keys(self, c: dict, base: tuple) -> list:
        a, e = c["at"], c["at"] + c["dur"]
        over = [p for p in self.pans if p[1] > a + 1e-6 and p[0] < e - 1e-6]
        marks = sorted({a, e, *[min(max(t, a), e) for p in over for t in p[:2]]})
        pan_t = {t for p in over for t in p[:2]}
        pos = lambda t: [round(base[0] - self.cam(t)[0], 2), round(base[1] - self.cam(t)[1], 2)]   # noqa: E731
        return [[round(t - a, 4), pos(t), *(["bezier"] if t in pan_t else [])] for t in marks]

    def apply(self) -> None:
        fx, vertical = self.fx, any(abs(p[3]) > abs(p[2]) for p in self.pans)
        for c, base in self.layers:
            keys = self._keys(c, base)
            if all(k[1] == keys[0][1] for k in keys):
                if keys[0][1] != [540, 960]:
                    c.setdefault("motion", {})["position"] = keys[0][1]
                continue
            c.setdefault("motion", {})["position"] = fx._frame_keys(keys, c["dur"])
            blur = []
            for t0, t1, _, _ in (p for p in self.pans if p[1] > c["at"] + 1e-6 and p[0] < c["at"] + c["dur"] - 1e-6):
                lo = lambda t: max(0.0, t - c["at"])   # noqa: E731
                blur += [[lo(t0), 0], [lo((t0 + t1) / 2), PAN_BLUR], [lo(t1), 0]]
            if blur:
                fx._fx(c, "directional_blur", {"direction": 0 if vertical else 90, "length": fx._frame_keys(blur, c["dur"])})


def _draw(world: World, gfx: Path, pts, t0: float, t1: float, name: str, hold_to: float, head: str = "none", glow: str | None = None,
          per_seg: int | None = 24, tag_base: str = "stroke") -> dict:
    """Vẽ một nét liền (toạ độ thế giới) từ t0 tới t1 (ease-in-out), rồi giữ nét đủ bằng PNG tới hold_to. Mỗi màn hình nét đi qua có một
    .mov alpha + một PNG tĩnh (cùng toạ độ khung, đặt bằng lệch màn hình). Trả spec để người gọi tính vị trí đầu nét."""
    fx, fps = world.fx, world.fx.fps
    n = round((t1 - t0) * fps)
    if n < STROKE_MIN_FRAMES:
        raise ValueError(f"nét «{name}» chỉ {n} khung (< {STROKE_MIN_FRAMES}): hai từ liền nhau quá sát để vẽ đường nối")
    spec = DP.curve(pts, n, head=head, glow=glow, per_seg=per_seg)
    P = np.asarray(spec["points"])
    for sx in range(int(np.floor(P[:, 0].min() / W)) - 1, int(np.floor(P[:, 0].max() / W)) + 2):
        for sy in range(int(np.floor(P[:, 1].min() / H)) - 1, int(np.floor(P[:, 1].max() / H)) + 2):
            local = DP.shift(spec, sx * W, sy * H)
            if not DP.hits_canvas(local):
                continue
            tag = f"{tag_base}_{sx}_{sy}".replace("-", "m")
            DP.write_with_still(local, gfx / f"{tag}.mov", gfx / f"{tag}.png", fps)
            mov = fx.image(str(gfx / f"{tag}.mov"), t0, n / fps, lane="card", name=f"{name} (vẽ)")
            mov.update({"in": 0.0, "audio": False})
            world.add(mov, (sx, sy))
            t_still = fx.snap(t0 + n / fps)
            if hold_to > t_still + 1e-6:
                world.add(fx.image(str(gfx / f"{tag}.png"), t_still, hold_to - t_still, lane="card", name=name), (sx, sy))
    fx.cues.append({"t": t0, "kind": "pen", "dur": n / fps, "why": name})
    return spec


def _head_time(spec: dict, t0: float, fps: float, x_world: float) -> float:
    """Giây đầu nét (ease-in-out theo độ dài cung, như render_frames) đầu tiên có x ≥ x_world; không tới thì giây cuối."""
    n = spec["frames"]
    u = np.linspace(0, 1, n)
    head = DP.path_points(spec["points"], u * u * (3 - 2 * u))
    hit = np.flatnonzero(head[:, 0] >= x_world)
    return t0 + (int(hit[0]) if hit.size else n - 1) / fps


# ============================================================ khối chữ
def group_box(prof: dict, entries: list) -> tuple[float, float, float, float]:
    """(trái, trên, phải, dưới) mực chữ của các clip chữ `[(lane, clip)]` một cụm — đo bằng font thật (brooks_text.Meter)."""
    M, box = BT.Meter(prof), [1e9, 1e9, -1e9, -1e9]
    for lane, c in entries:
        if "text" not in c:
            continue
        role = "hero_serif" if "Playfair" in c["font"] else ("hero_sans" if lane == "text" else "small")
        w, (x, y) = M.width(role, c["size"], c["text"]), c["position"]
        left = {"center": x - w / 2, "left": x, "right": x - w}[c["align"]]
        top, bot = y - M.ink_top(role, c["size"], [c["text"]]), y + M.ink_bottom(role, c["size"], [c["text"]])
        box = [min(box[0], left), min(box[1], top), max(box[2], left + w), max(box[3], bot)]
    return tuple(box)


# ============================================================ 1. tranh
def calm_zone(img: str, zones: tuple = ("top", "lower", "mid_center")) -> str:
    """Vùng chữ ít chi tiết nhất của ảnh (độ lớn gradient trung bình trong dải y của vùng) — chữ đặt "quanh chủ thể", không đè lên nó."""
    g = np.asarray(ImageOps.fit(Image.open(img).convert("L"), (W // 4, H // 4)), np.float32)
    gy, gx = np.gradient(g)
    energy = np.hypot(gx, gy)
    score = {z: energy[BT.ZONES[z][0] // 4:BT.ZONES[z][1] // 4].mean() * (1.0 if z == zones[0] else 1.1) for z in zones}
    return min(score, key=score.get)


def painting(fx, img: str, at: float, dur: float, gfx_dir=None, strength: float = PAINT_BAKED) -> dict:
    """Tranh phủ khung + texture sơn nướng (≤ graphics.painting_texture_max) + hai lớp texture thô (paint, paper) multiply ≤ 50 % trôi ngược
    chiều nhau, mọi lớp đẩy máy cùng tranh cuối cảnh (scale 100 → 112 % easeIn trong 10 khung) → texture "chạy theo tranh". Vào bằng
    directional_blur ngang 5–7 khung (cuts.painting_entry). Trả clip tranh."""
    prof, fps, gfx = _prof(), fx.fps, Path(gfx_dir or fx.gfx_dir)
    cap = sp.get(prof, "graphics.painting_texture_max")
    if strength > cap:
        raise ValueError(f"texture nướng {strength} vượt graphics.painting_texture_max = {cap}")
    stem = Path(img).stem[:24]
    cover = G.cover_image(gfx, f"paint_cover_{stem}", img)
    pic = fx.image(G.paint_texture(gfx, f"paint_{stem}_{round(strength * 100)}", cover, strength), at, dur, lane="gfx_under", name=f"Tranh · {stem}")
    t_push, t_end = max(dur - PUSH_FRAMES / fps, dur / 2), dur - 1 / fps
    pic["motion"] = {"scale": fx._frame_keys([[0, 100], [t_push, SLOW_ZOOM, "easeOut"], [t_end, PUSH_SCALE, "easeIn"]], dur)}
    entry = sp.get(prof, "cuts.painting_entry")
    n = (entry["frames"][0] + entry["frames"][-1]) // 2
    fx._fx(pic, entry["effect"], {"direction": 90, "length": fx._frame_keys([[0, ENTRY_BLUR], [n / fps, 0, "easeIn"]], dur)})
    for i, (op, drift, kind, seed) in enumerate(PAINT_LAYERS):
        tex = _texture(fx, gfx, kind, seed, at, dur, op, drift, f"Texture tranh {i + 1}")
        tex["motion"]["scale"] = fx._frame_keys([[0, LAYER_SCALE], [t_push, LAYER_SCALE, "easeOut"],
                                                 [t_end, round(LAYER_SCALE * PUSH_SCALE / 100, 2), "easeIn"]], dur)
    fx.cues.append({"t": at, "kind": "whoosh", "why": "tranh vào (nhoè ngang)"})
    fx.cues.append({"t": round(at + t_push, 3), "kind": "whoosh", "why": "đẩy máy lộ tranh"})
    return pic


# ============================================================ 2. đường + chữ
def _stroke_plan(t_h: list, at: float, end: float, fps: float) -> list:
    """[(đầu, cuối)] giây của các nét: nét 0 tới từ đầu, nét k = nối từ k−1 sang k, nét n = đuôi sau từ cuối. Nét tới từ k xong 2 khung
    trước khi từ k hiện (từ "cắt" nét); nét nối bắt đầu 3 khung sau từ trước."""
    f = 1 / fps
    plan = [(max(at, t_h[0] - 0.55), t_h[0] - 2 * f)]
    plan += [(t_h[k] + 3 * f, t_h[k + 1] - 2 * f) for k in range(len(t_h) - 1)]
    plan.append((t_h[-1] + 3 * f, min(t_h[-1] + 0.55, end - 3 * f)))
    return plan


def _stop_points(k: int, box: tuple, cx: float) -> dict:
    """Điểm điều khiển (toạ độ thế giới) của các nét quanh điểm dừng k: `into` (từ trên xuống mép trên khối chữ, dừng cách LINE_GAP) và
    `out` (từ mép dưới khối chữ + LINE_GAP, đi xuống rồi sang phải)."""
    X = k * W
    top, bot = box[1] - LINE_GAP, box[3] + LINE_GAP
    ey = max(120.0, top - 560)
    start = (X - 80, ey)
    into = [start, (X + cx * 0.5, ey + 0.25 * (top - ey)), (X + cx - 30, top - 170), (X + cx, top)]
    return {"top": (X + cx, top), "bot": (X + cx, bot), "into": into,
            "out": [(X + cx, bot), (X + cx + 40, bot + 150), (X + cx + 250, bot + 230)]}


def path_text(fx, caption, at: float, end: float, groups: list, bg: str = "white", gfx_dir=None, prof: dict | None = None) -> dict:
    """Cảnh đường + chữ (nguyên tắc 4). `groups` = [(items "nhỏ | *lớn", giây từng từ)] — mỗi cụm là một điểm dừng, từ lớn là từ "cắt" nét.
    `caption(group, zone, on_dark, accent, end, look=…)` dựng chữ (trả [(lane, clip)]; template dùng group_fit). Mỗi điểm dừng một màn
    hình rộng 1080: nét tới từ → dừng cách khối chữ LINE_GAP → nét nối đi dưới chữ sang màn hình kế, máy lia theo đầu nét lúc đầu nét tới
    gần mép phải. Trả {"boxes": khối chữ từng điểm dừng, "strokes": điểm điều khiển từng nét, "pans": [(t0, t1)]}."""
    prof, fps, dark, gfx = prof or _prof(), fx.fps, bg == "black", Path(gfx_dir or fx.gfx_dir)
    n = len(groups)
    _paper(fx, gfx, bg, 5, at, end - at, "Nền đường + chữ")
    t_h = [times[next(i for i, s in enumerate(items) if s[0] in "*~")] for items, times in groups]
    world, texts, boxes, cxs = World(fx), [], [], []
    for k, grp in enumerate(groups):
        ent = caption(grp, ZONE_CYCLE[k % len(ZONE_CYCLE)], dark, False, end, look="shadow_deep" if dark else "shadow_light")
        hero = next(c for lane, c in ent if lane == "text" and "text" in c)
        boxes.append(group_box(prof, ent))
        cxs.append(hero["position"][0])
        texts.append([c for _, c in ent])
    plan = _stroke_plan(t_h, at, end, fps)
    sp_ = [_stop_points(k, boxes[k], cxs[k]) for k in range(n)]
    pts = {0: sp_[0]["into"]}
    for k in range(n - 1):
        a, b = sp_[k], sp_[k + 1]
        yb = float(np.clip(min((a["bot"][1] + 150 + b["top"][1] - 330) / 2, b["top"][1] - 260), 150, 1780))   # luôn tới từ trên xuống, không cắt ngang chữ nhỏ
        pts[k + 1] = [a["bot"], a["out"][1], (k * W + min(boxes[k][2] + 130, W - 40), a["bot"][1] + 110), ((k + 1) * W + 60, yb), (b["into"][-2][0], max(120.0, b["top"][1] - 230)), b["top"]]
    pts[n] = sp_[-1]["out"]
    pans, hold = [], end
    for i in sorted(pts):
        t0, t1 = plan[i]
        spec = _draw(world, gfx, pts[i], t0, t1, f"Đường {i + 1}", hold, tag_base=f"pt_stroke{i}")
        if 1 <= i <= n - 1:                           # nét nối: máy lia khi đầu nét gần mép phải màn hình i−1
            frames = max(4, min(PAN_FRAMES, round((t1 - t0) * fps / 2)))
            p0 = min(_head_time(spec, t0, fps, i * W - PAN_TRIGGER_X), t1 - (frames + 2) / fps)
            p1 = world.pan(max(p0, t0), frames, W)
            pans.append((max(p0, t0), p1))
            fx.cues.append({"t": max(p0, t0), "kind": "whoosh", "why": f"lia theo đường tới từ {i + 1}"})
            for c in texts[i - 1]:                      # chữ điểm dừng i−1 đã ra khỏi khung: kết thúc ngay sau lúc lia
                c["dur"] = max(round(min(c["at"] + c["dur"], p1 + 4 / fps) - c["at"], 4), 1 / fps)
    for k, group in enumerate(texts):
        for c in group:
            if c["dur"] > 0:
                world.add(c, (k, 0))
    world.apply()
    return {"boxes": boxes, "strokes": [pts[i] for i in sorted(pts)], "pans": pans, "plan": plan}


# ============================================================ 3. đường + minh hoạ
def _contain(gfx: Path, name: str, img: str, box: tuple) -> str:
    """Ảnh co vừa `box` giữ tỉ lệ (không cắt), nền giữ nguyên alpha."""
    im = Image.open(img).convert("RGBA")
    k = min(box[0] / im.width, box[1] / im.height)
    return G._save(im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS), gfx, name)


def _pop(fx, c: dict, frames: int = 8) -> dict:
    """Hiện: opacity 0 → 100 trong 3 khung, scale 92 → 100 % lắng `frames` khung (easeIn), nhoè 14 → 0."""
    fps, base = fx.fps, c.get("motion", {}).get("scale", 100)
    c["opacity"] = fx._frame_keys([[0, 0], [3 / fps, 100]], c["dur"])
    c.setdefault("motion", {})["scale"] = fx._frame_keys([[0, round(base * 0.92, 2)], [frames / fps, base, "easeIn"]], c["dur"])
    fx._fx(c, "gaussian_blur", {"blurriness": fx._frame_keys([[0, 14], [frames * 0.75 / fps, 0, "easeIn"]], c["dur"])})
    fx.cues.append({"t": c["at"], "kind": "pop", "why": "minh hoạ hiện"})
    return c


def path_illus(fx, img: str, style: str, at: float, end: float, gfx_dir=None) -> dict:
    """Đường + chấm trắng dẫn tới minh hoạ (nguyên tắc 5). "zigzag": đường zíc-zắc sang phải, máy lia 640 px lộ vật ở bên phải; "rise":
    đường uốn đi lên tới chủ thể ở nửa trên. Chữ (GROUPS) do template đặt ở vùng trống (text_zone). Trả {"stroke", "image", "pan"}."""
    if style not in ("zigzag", "rise"):
        raise ValueError(f"style lạ: {style} (zigzag | rise)")
    fps, gfx, glow = fx.fps, Path(gfx_dir or fx.gfx_dir), sp.get(_prof(), "graphics.accent_line")
    _paper(fx, gfx, "white", 6, at, end - at, "Nền đường + minh hoạ")
    world = World(fx)
    t0 = fx.snap(at + 6 / fps)
    t1 = fx.snap(min(t0 + float(np.clip(0.55 * (end - at), 0.9, 1.7)), end - 0.5))
    box = ILLUS_BOX[style]
    pic = fx.image(_contain(gfx, f"illus_{style}_{Path(img).stem[:20]}", img, box), t1, end - t1, lane="card", name="Minh hoạ")
    pic["blend"] = "multiply"
    if style == "zigzag":
        pan_dx = 640
        pts = [(90, 1100), (300, 880), (520, 1130), (740, 880), (960, 1130), (1180, 840)]
        pic["motion"] = {"position": [540 + pan_dx, 1280]}
        path, per_seg = DP.rounded_path(pts, 70)[0], None
    else:
        pan_dx = 0
        pts = [(540, 1120), (620, 1000), (470, 880), (560, 760), (540, 720)]
        pic["motion"] = {"position": [540, 720 - box[1] // 2 - 30]}
        path, per_seg = pts, 24
    spec = _draw(world, gfx, path, t0, t1, "Đường minh hoạ", end, head="dot", glow=glow, per_seg=per_seg, tag_base=f"pi_{style}")
    pan = None
    if pan_dx:
        frames = max(4, min(PAN_FRAMES + 2, round((t1 - t0) * fps / 2)))
        p0 = max(t0, min(_head_time(spec, t0, fps, 700), t1 - (frames + 1) / fps))
        pan = (p0, world.pan(p0, frames, pan_dx))
        fx.cues.append({"t": p0, "kind": "whoosh", "why": "lia lộ minh hoạ"})
    world.add(_pop(fx, pic))
    world.apply()
    return {"stroke": spec, "image": pic, "pan": pan}


# ============================================================ 4. minh hoạ giữa  5. minh hoạ bên
def illus_mid(fx, img: str, at: float, end: float, gfx_dir=None) -> dict:
    """Minh hoạ nửa dưới trồi lên giữa trên giấy trắng (nguyên tắc 7): ảnh mép trên / trái / phải loang vào giấy (alpha mềm + nhiễu, blend
    multiply), trồi MID_RISE_DY px trong 16 khung (easeIn) kèm nhoè dọc, rồi phóng chậm 100 → 104 %. Texture sơn thô phủ cả khung. Chữ ở nửa trên."""
    fps, gfx, dur = fx.fps, Path(gfx_dir or fx.gfx_dir), end - at
    _paper(fx, gfx, "white", 8, at, dur, "Nền giấy minh hoạ giữa")
    pic = fx.image(G.bleed_image(gfx, f"mid_{Path(img).stem[:20]}", img, (W, MID_H), ("top", "left", "right"), MID_FEATHER, 8),
                   at, dur, lane="card", name="Minh hoạ giữa")
    pic["blend"] = "multiply"
    y0, n = H - MID_H // 2, MID_RISE_FRAMES / fps
    pic["motion"] = {"position": fx._frame_keys([[0, [540, y0 + MID_RISE_DY]], [n, [540, y0], "easeIn"]], dur),
                     "scale": fx._frame_keys([[0, 100], [dur - 1 / fps, 104]], dur)}
    pic["opacity"] = fx._frame_keys([[0, 0], [5 / fps, 100]], dur)
    fx._fx(pic, "directional_blur", {"direction": 0, "length": fx._frame_keys([[0, 60], [n, 0, "easeIn"]], dur)})
    _texture(fx, gfx, "paint", 23, at, dur, TEX_OPACITY, (30, -20), "Texture sơn thô")
    fx.cues.append({"t": at, "kind": "whoosh", "why": "minh hoạ trồi lên"})
    return pic


def illus_side(fx, img: str, side: str, at: float, end: float, gfx_dir=None) -> dict:
    """Hình trừu tượng một bên (nguyên tắc 8): ảnh SIDE_SIZE sát mép `side`, mép trong loang vào giấy, nướng texture sơn, trượt vào 14 khung
    (easeIn) kèm nhoè ngang rồi trôi chậm 14 px. Chữ ở phía kia (vùng side_right / side_left, xem text_zone)."""
    if side not in ("left", "right"):
        raise ValueError(f"side lạ: {side} (left | right)")
    fps, gfx, dur = fx.fps, Path(gfx_dir or fx.gfx_dir), end - at
    _paper(fx, gfx, "white", 9, at, dur, "Nền giấy minh hoạ bên")
    fig = fx.image(G.side_figure(gfx, f"side_{side}_{Path(img).stem[:20]}", img, side, SIDE_SIZE, SIDE_FEATHER, seed=9),
                   at, dur, lane="card", name="Hình bên")
    fig["blend"] = "multiply"                                    # vùng trắng / mép loang của hình tan vào giấy
    sgn = -1 if side == "left" else 1
    x1 = 540 + sgn * (540 - SIDE_SIZE[0] // 2)                    # tâm khi sát mép
    n = SIDE_SLIDE_FRAMES / fps
    fig["motion"] = {"position": fx._frame_keys([[0, [x1 + sgn * SIDE_SIZE[0], 980]], [n, [x1, 980], "easeIn"],
                                                 [dur - 1 / fps, [x1 - sgn * 14, 980]]], dur)}
    fx._fx(fig, "directional_blur", {"direction": 90, "length": fx._frame_keys([[0, 70], [n, 0, "easeIn"]], dur)})
    _texture(fx, gfx, "paper", 24, at, dur, TEX_OPACITY, (-20, 24), "Texture giấy thô")
    fx.cues.append({"t": at, "kind": "whoosh", "why": "hình bên trượt vào"})
    return fig


# ============================================================ 6. cảnh toàn chữ trên giấy thô
def quote_paper(fx, lines: list, hero_index: int, at: float, end: float, t0: float, t_hero: float, bg: str = "white", gfx_dir=None,
                prof: dict | None = None, dy: float = 0.0, hero_color: str | None = None) -> list:
    """Quote card trên giấy thô (nguyên tắc 6, biến thể): nền giấy trắng (chữ đen, dòng chính xanh nhấn) hoặc xanh cobalt thô (chữ trắng,
    dòng chính vàng), texture giấy phủ multiply, dấu “ ” của brooks_text.quote_text. `dy` dời cả khối (px, về vùng giữa khung)."""
    if bg not in ("white", "blue"):
        raise ValueError(f"bg lạ: {bg} (white | blue)")
    prof, gfx, light = copy.deepcopy(prof or _prof()), Path(gfx_dir or fx.gfx_dir), bg == "white"
    cols = prof["text"]["colors"]
    if light:
        cols["on_dark"] = cols["on_paper"]                       # quote_text vẽ chữ / dấu ngoặc bằng màu on_dark → đổi sang chữ đen
    hero = hero_color or (HERO_PAPER_ACCENT if light else HERO_BLUE_BG)
    _paper(fx, gfx, bg, 11, at, end - at, "Nền giấy trích dẫn")
    _texture(fx, gfx, "paper", 25, at, end - at, TEX_OPACITY, (14, -10), "Texture giấy thô")
    items = BT.quote_text(lines, False, at=t0, dur=end - t0, fps=fx.fps, last_at=t_hero, prof=prof, hero_index=hero_index,
                          hero_color=hero, gfx_dir=gfx)
    shadow = prof["text"]["look_shadows"]["light"]
    for _, c in items:
        if "src" in c:                                           # PNG gradient toàn khung: dời bằng motion.position
            m = c.setdefault("motion", {})
            x, y = m.get("position", [540, 960])
            m["position"] = [x, y + dy]
        else:
            c["position"] = [c["position"][0], c["position"][1] + dy]
        if light:
            c["effects"] = [e for e in c.get("effects", []) if e.get("effect") != "wonder_glow"]
            if "shadow" in c:
                c["shadow"] = dict(shadow)
    fx.items += items
    fx.cues.append({"t": t_hero, "kind": "key_hit", "why": f"câu chốt «{lines[hero_index]}»"})
    return items


# ============================================================ vùng chữ cho template
def text_zone(kind: str, *args) -> tuple[str, bool]:
    """(vùng chữ của GROUPS trong cảnh, nền sáng?) để template đặt chữ trước khi dựng đồ hoạ. args = phần SCENE_GFX sau số cảnh / từ."""
    if kind == "painting":
        return calm_zone(args[0]), False
    if kind == "path_illus":
        return ("top" if args[1] == "zigzag" else "lower"), True
    if kind == "illus_mid":
        return "top", True
    if kind == "illus_side":
        return ("side_right" if args[1] == "left" else "side_left"), True
    raise ValueError(f"kiểu không có chữ GROUPS: {kind}")
