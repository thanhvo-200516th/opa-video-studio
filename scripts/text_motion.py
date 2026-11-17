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

Hồ sơ tuỳ chọn 'minimal-edu' (references/minimal-edu-style.json, chỉ khi profile.json bật): ensure_motion(items, fps,
profile=prof, cuts=[...]) — vào ngắn theo khung của chữ chính / chữ nhỏ, ra = mờ `exit_frames` khung (không nhoè), và
clip kết thúc `end_before_cut_frames` khung trước điểm cắt gần cuối clip (chỉ rút ngắn). profile=None → như cũ.
"""
from __future__ import annotations

from style_profile import active, get

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
CUT_SNAP_S = 0.25           # hồ sơ: điểm cắt cách cuối clip ≤ 0,25 s (về phía trước) thì clip kết thúc theo điểm cắt đó
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


def profile_in_frames(prof: dict) -> tuple[int, int]:
    """(khung vào chữ nhỏ, khung vào chữ chính) của hồ sơ: chữ nhỏ = giữa dải, chữ chính = đầu dải (Brooks: chủ yếu 3 khung)."""
    lo, hi = get(prof, "text.small_in_frames", [1, 3])
    return round((lo + hi) / 2), get(prof, "text.hero_blur_in_frames", [3, 6])[0]


def soft_in_frames(c: dict, n: int, fps: float, blur_from: float = 22) -> None:
    """Vào ngắn n khung: opacity 0 → 100 trong ~60 % thời gian, nhoè blur_from → 0 đúng n khung (mốc nằm trên bội số khung)."""
    end = max(1e-3, c["dur"] - 1e-3)
    t_op, t_bl = min(max(1, round(0.6 * n)) / fps, end), min(n / fps, end)
    c["opacity"] = [[0, 0], [t_op, 100]]
    c.setdefault("effects", []).append({"effect": "gaussian_blur", "params": {"blurriness": [[0, blur_from], [t_bl, 0, "easeIn"]]}})


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


def soft_out(c: dict, out_s: float = SOFT_OUT_S, blur: float | None = OUT_BLUR) -> None:
    """Ra: opacity 100 → 0 trong out_s; blur=None → chỉ mờ, không nhoè (hồ sơ minimal-edu)."""
    d = c["dur"]
    t0 = max(0.0, d - out_s)
    op = c.get("opacity")
    if isinstance(op, list) and op and isinstance(op[0], (list, tuple)):
        keep = [k for k in op if k[0] < t0 - 1e-3]
        last = keep[-1][1] if keep else 100
        c["opacity"] = keep + [[t0, last], [d, 0]]
    else:
        c["opacity"] = [[0, op if isinstance(op, (int, float)) else 100], [t0, op if isinstance(op, (int, float)) else 100], [d, 0]]
    if blur is None:
        return
    fx = _effect(c, "gaussian_blur")
    if fx and isinstance(fx["params"].get("blurriness"), list):
        ks = [k for k in fx["params"]["blurriness"] if k[0] < t0 - 1e-3]
        fx["params"]["blurriness"] = ks + [[t0, 0], [d, blur]]
    else:
        c.setdefault("effects", []).append({"effect": "gaussian_blur", "params": {"blurriness": [[0, 0], [t0, 0], [d, blur]]}})


def _has_out(c: dict) -> bool:
    """Clip đã có kiểu ra riêng: transition_out, hoặc key opacity cuối là mờ về ~0 ở cuối clip."""
    d, op = c["dur"], c.get("opacity")
    fades_out = (isinstance(op, list) and len(op) >= 2 and isinstance(op[-1], (list, tuple))
                 and op[-1][0] >= d - 0.3 and op[-1][1] <= 5)        # key cuối là mờ về ~0 ở cuối clip
    return bool(c.get("transition_out")) or fades_out


def _trim_to_cut(c: dict, cuts: list[float], fps: float, frames: int) -> bool:
    """Hồ sơ: clip kết thúc `frames` khung trước điểm cắt gần cuối clip (cắt trong [cuối − CUT_SNAP_S, cuối]). Chỉ rút ngắn,
    và bỏ qua nếu clip còn key chuyển động nằm sau điểm kết thúc mới (không để key vượt cuối clip)."""
    end = c["at"] + c["dur"]
    cut = next((t for t in sorted(cuts) if end - CUT_SNAP_S <= t <= end + 1e-6), None)
    new_end = None if cut is None else round((cut - frames / fps) * fps) / fps
    if new_end is None or new_end >= end - 1e-6 or new_end - c["at"] < MIN_CLIP_S:
        return False
    if any(t > new_end - c["at"] + 1e-6 for t in _anim_times(c)):
        return False
    c["dur"] = round(new_end - c["at"], 6)
    return True


def ensure_motion(items: list[tuple[str, dict]], fps: float = 30.0, profile: dict | None = None,
                  cuts: list[float] | None = None) -> dict:
    """Bổ sung vào / giữ / ra cho mọi clip chữ còn thiếu. Trả số clip được thêm từng phần.
    profile = hồ sơ 'minimal-edu' đã nạp (style_profile.load) → vào ngắn theo khung, ra mờ `exit_frames` khung, cắt clip theo `cuts`
    (mốc điểm cắt trên timeline, giây); hồ sơ khác / None → hành vi cũ."""
    prof = profile if active(profile, "minimal-edu") else None
    n = {"in": 0, "hold": 0, "out": 0, "text": 0}
    if prof:
        n["trim"] = 0
        f_small, f_hero = profile_in_frames(prof)
        out_s = get(prof, "text.exit_frames", 2) / fps
        end_f = get(prof, "text.end_before_cut_frames", [0, 2])[1]
    for lane, c in items:
        if lane not in TEXT_LANES or c.get("dur", 0) < MIN_CLIP_S:
            continue
        n["text"] += 1
        if prof and cuts and not _has_out(c) and _trim_to_cut(c, cuts, fps, end_f):
            n["trim"] += 1
        d = c["dur"]
        ts = _anim_times(c)
        if not any(t <= ENTRANCE_WINDOW for t in ts):
            if prof:
                soft_in_frames(c, f_hero if lane in KEY_LANES else f_small, fps, 22 if lane in KEY_LANES else 14)
            else:
                soft_in(c, lane)
            n["in"] += 1
            ts = _anim_times(c)
        in_end = max([t for t in ts if t <= ENTRANCE_WINDOW + 0.25] or [0.0])
        has_out = _has_out(c)
        out_start = d if has_out else d - (out_s if prof else SOFT_OUT_S)
        if d >= MIN_HOLD_S and out_start - in_end > 0.2 and not has_hold_motion(c, in_end, out_start):
            hold_drift(c, lane, in_end, out_start)
            n["hold"] += 1
        if not has_out:
            soft_out(c, out_s, None) if prof else soft_out(c)
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
