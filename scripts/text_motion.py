"""Rule 4 (người dùng chốt 2026-11-11): không để chữ tĩnh — mọi lớp chữ có vào, giữ và ra chuyển động mượt.

Thông số đo từ @__dviet (video 7706183278461570356 + 4 video kênh, 2026-11-11, khung @24 fps quy ra giây):
  - Vào "soft_in": KHÔNG nảy / phóng — mờ nhoè thành nét. Chữ chính 7 khung (0,29 s): opacity 0 → 15 → 65 → 88 → 100 %
    ở khung 0/1/3/5/7, blur 22 → 9 → 3 → 0 (ease-out giữa bậc 2 và bậc 3). Dòng nối / phụ đề 4 khung (0,17 s).
  - Giữ: kênh chỉ trôi ≤ 1,4 % (gần như đứng). Người dùng muốn "không tĩnh" → phóng chậm đều 100 → 103 % (chữ chính) /
    101,5 % (phụ đề) suốt lúc giữ, anchor tại chữ, không nảy; dưới ngưỡng gây giật, vẫn thấy chữ "thở".
  - Ra "soft_out": opacity 100 → 0 + blur 0 → 12 trong 4 khung (0,13 s), kết thúc đúng cuối clip (đúng điểm cắt).
Chỉ BỔ SUNG phần còn thiếu: clip đã có kiểu vào riêng (slam, type, glow_in…) giữ nguyên kiểu vào; đã có chuyển động lúc giữ
thì không thêm; đã có transition_out / mờ ra thì không thêm ra.

    from text_motion import ensure_motion
    n = ensure_motion(items, fps)        # items = [(lane, clip)] của FX / MotionFX — sửa clip tại chỗ
"""
from __future__ import annotations

TEXT_LANES = {"text", "text_top", "text_low", "text_img"}
KEY_LANES = {"text", "text_top", "text_img"}          # chữ chính / tiêu đề; text_low = phụ đề, dòng nối
SOFT_IN_KEY = ([(0.0, 0), (0.042, 15), (0.125, 65), (0.208, 88), (0.292, 100)],
               [(0.0, 22), (0.125, 9), (0.208, 3), (0.292, 0)])
SOFT_IN_CAP = ([(0.0, 0), (0.042, 40), (0.083, 75), (0.167, 100)], [(0.0, 14), (0.167, 0)])
SOFT_OUT_S, OUT_BLUR = 0.13, 12
HOLD_SCALE = {"key": 103.0, "cap": 101.5}
ENTRANCE_WINDOW = 0.35      # có key trong 0,35 s đầu = đã có kiểu vào
MIN_HOLD_S = 0.6            # clip ngắn hơn: chỉ vào / ra, không thêm phóng giữ
MIN_CLIP_S = 0.3            # clip ngắn hơn (khung đổi font, chữ chớp…) giữ nguyên: hiệu ứng cố ý tức thời, thêm key sẽ trùng mốc
SKIP_KEYS = ("src", "text", "name", "font", "style", "color", "shadow", "position", "align", "tracking", "size")


def _key_times(obj) -> list[float]:
    out: list[float] = []
    if isinstance(obj, dict):
        for v in obj.values():
            out += _key_times(v)
    elif isinstance(obj, list):
        if obj and all(isinstance(x, (list, tuple)) and x and isinstance(x[0], (int, float)) and not isinstance(x[0], bool)
                       for x in obj) and len(obj) >= 2:
            out += [float(x[0]) for x in obj]
        else:
            for v in obj:
                out += _key_times(v)
    return out


def _key_spans(obj) -> list[list[float]]:
    """Mốc thời gian của từng chuỗi keyframe riêng (mỗi thuộc tính / tham số một chuỗi)."""
    out: list[list[float]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k not in SKIP_KEYS and k != "transition_out":
                out += _key_spans(v)
    elif isinstance(obj, list):
        if len(obj) >= 2 and all(isinstance(x, (list, tuple)) and x and isinstance(x[0], (int, float))
                                 and not isinstance(x[0], bool) for x in obj):
            out.append([float(x[0]) for x in obj])
        else:
            for v in obj:
                out += _key_spans(v)
    return out


def has_hold_motion(c: dict, t0: float, t1: float) -> bool:
    """Có chuỗi key chuyển động (motion / effect hình học, không tính mờ / nhoè vào-ra) trải ≥ 60 % đoạn giữ t0..t1."""
    src = {"motion": c.get("motion"), "effects": [e for e in c.get("effects", []) if e.get("effect") != "gaussian_blur"]}
    need = 0.6 * max(1e-3, t1 - t0)
    return any(min(k) <= t0 + 0.35 and max(k) >= t1 - 0.35 and max(k) - min(k) >= need for k in _key_spans(src))


def _anim_times(c: dict) -> list[float]:
    return _key_times({k: v for k, v in c.items() if k not in SKIP_KEYS and k != "transition_out"})


def _effect(c: dict, name: str) -> dict | None:
    return next((e for e in c.get("effects", []) if e.get("effect") == name), None)


def _png_center(src: str) -> list[float] | None:
    """Tâm phần có nét của ảnh chữ PNG khung đầy (text_img) — để phóng quanh chữ, không quanh tâm khung."""
    try:
        from PIL import Image
        with Image.open(src) as im:
            box = im.getchannel("A").getbbox() if "A" in im.getbands() else None
        return [(box[0] + box[2]) / 2, (box[1] + box[3]) / 2] if box else None
    except Exception:  # noqa: BLE001 — không đọc được ảnh thì dùng tâm khung
        return None


def _anchor(c: dict) -> list[float]:
    pos = c.get("position")
    if isinstance(pos, (list, tuple)) and len(pos) == 2 and all(isinstance(v, (int, float)) for v in pos):
        return [float(pos[0]), float(pos[1])]
    if str(c.get("src", "")).lower().endswith(".png"):
        return _png_center(c["src"]) or [540.0, 960.0]
    return [540.0, 960.0]


def soft_in(c: dict, lane: str) -> None:
    op, bl = SOFT_IN_KEY if lane in KEY_LANES else SOFT_IN_CAP
    end = max(1e-3, c["dur"] - 1e-3)
    c["opacity"] = [[min(t, end), v] for t, v in op]
    c.setdefault("effects", []).append({"effect": "gaussian_blur",
                                        "params": {"blurriness": [[min(t, end), v] + (["easeIn"] if i else []) for i, (t, v) in enumerate(bl)]}})


def hold_drift(c: dict, lane: str, t0: float, t1: float) -> None:
    peak = HOLD_SCALE["key" if lane in KEY_LANES else "cap"]
    ax = _anchor(c)
    t1 = min(round(t1, 3), c["dur"])                 # làm tròn không được vượt cuối clip (fc_build chặn key quá cuối)
    t0 = min(round(t0, 3), t1 - 1e-3)
    fx = {"effect": "transform", "params": {"anchor": ax, "position": ax, "uniform_scale": True,
                                            "scale_height": [[t0, 100.0], [t1, peak, "linear"]]}}
    effects = c.setdefault("effects", [])
    mi = next((i for i, e in enumerate(effects) if e.get("effect") == "track_matte"), None)
    effects.insert(len(effects) if mi is None else mi, fx)   # phóng TRƯỚC track matte: chữ sau người vẫn khớp viền người


def soft_out(c: dict) -> None:
    d = c["dur"]
    t0 = max(0.0, d - SOFT_OUT_S)
    op = c.get("opacity")
    if isinstance(op, list) and op and isinstance(op[0], (list, tuple)):
        keep = [k for k in op if k[0] < t0 - 1e-3]
        last = keep[-1][1] if keep else 100
        c["opacity"] = keep + [[t0, last], [d, 0]]
    else:
        c["opacity"] = [[0, op if isinstance(op, (int, float)) else 100], [t0, op if isinstance(op, (int, float)) else 100], [d, 0]]
    blur = _effect(c, "gaussian_blur")
    if blur and isinstance(blur["params"].get("blurriness"), list):
        ks = [k for k in blur["params"]["blurriness"] if k[0] < t0 - 1e-3]
        blur["params"]["blurriness"] = ks + [[t0, 0], [d, OUT_BLUR]]
    else:
        c.setdefault("effects", []).append({"effect": "gaussian_blur", "params": {"blurriness": [[0, 0], [t0, 0], [d, OUT_BLUR]]}})


def ensure_motion(items: list[tuple[str, dict]], fps: float = 30.0) -> dict:
    """Bổ sung vào / giữ / ra cho mọi clip chữ còn thiếu. Trả số clip được thêm từng phần."""
    n = {"in": 0, "hold": 0, "out": 0, "text": 0}
    for lane, c in items:
        if lane not in TEXT_LANES or c.get("dur", 0) < MIN_CLIP_S:
            continue
        n["text"] += 1
        d = c["dur"]
        ts = _anim_times(c)
        if not any(t <= ENTRANCE_WINDOW for t in ts):
            soft_in(c, lane)
            n["in"] += 1
            ts = _anim_times(c)
        in_end = max([t for t in ts if t <= ENTRANCE_WINDOW + 0.25] or [0.0])
        op = c.get("opacity")
        fades_out = (isinstance(op, list) and len(op) >= 2 and isinstance(op[-1], (list, tuple))
                     and op[-1][0] >= d - 0.3 and op[-1][1] <= 5)        # key cuối là mờ về ~0 ở cuối clip
        has_out = bool(c.get("transition_out")) or fades_out
        out_start = d if has_out else d - SOFT_OUT_S
        if d >= MIN_HOLD_S and out_start - in_end > 0.2 and not has_hold_motion(c, in_end, out_start):
            hold_drift(c, lane, in_end, out_start)
            n["hold"] += 1
        if not has_out:
            soft_out(c)
            n["out"] += 1
    return n


def static_report(tracks: list[dict], fps: float = 30.0) -> dict:
    """Đếm clip chữ tĩnh trên spec đã dựng (cho bộ kiểm): không có kiểu vào, hoặc đứng yên suốt lúc giữ."""
    total = no_in = flat = 0
    for t in tracks:
        lane = t.get("name", "").rsplit(" ", 1)[0]
        if lane not in TEXT_LANES:
            continue
        for c in t.get("clips", []):
            if c.get("dur", 0) < MIN_HOLD_S:
                continue
            total += 1
            ts = _anim_times(c)
            if not any(t_ <= ENTRANCE_WINDOW for t_ in ts):
                no_in += 1
            if not has_hold_motion(c, min(0.6, c["dur"] / 3), c["dur"] - SOFT_OUT_S):
                flat += 1                  # không có chuyển động trải suốt lúc giữ = chữ đứng yên
    return {"total": total, "no_entrance": no_in, "static_hold": flat}
