#!/usr/bin/env python3
"""draw_path — vẽ nét (xoắn ốc, mũi tên cong, đường, zig-zag, đường đồ thị + chấm) từng khung một → ProRes 4444 alpha.

FilmCraft spec không có shape / mask / trim-path, nên nét vẽ đi qua .mov alpha như matte.py (cùng bộ mã hoá
`prores_ks -profile:v 4444 -pix_fmt yuva444p10le`) và nằm trong timeline như một clip video bình thường.
Mỗi preset trả một `spec` (dict) cho `render_frames(**spec)` / `write(spec, out, fps)`; số khung = spec["frames"],
khung 0 trống, khung cuối đủ nét (+ đầu mũi tên). Màu và số đo lấy từ references/minimal-edu-style.json.

    python3 draw_path.py spiral --out spiral.mov [--cx 540 --cy 960 --r 400 --fps 30]
    python3 draw_path.py arrow  --out arrow.mov  [--p0 220,1500 --p1 820,1000]
    python3 draw_path.py line   --points "100,960 980,960" --out line.mov
    python3 draw_path.py zigzag --p0 100,700 --p1 980,1100 --out zz.mov
    python3 draw_path.py graph  --points "100,1500 400,1200 700,1000 980,500" --out graph.mov
Thêm `--still X.png` để ghi luôn khung cuối ra PNG.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Iterator

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from style_profile import get, load  # noqa: E402

W, H = 1080, 1920
SHIFT = 4                                  # cv2 vẽ toạ độ con 1/16 px
HAND_WIDTH_RATIO = 0.025                   # nét tay (xoắn, mũi tên, zig-zag, đồ thị) ≈ 2,5 % W (đo từ mẫu; chưa có trong JSON)
HAND_JITTER = 0.15                         # run tay nhẹ: biên độ = 15 % bề dày nét


def _g(key: str):
    return get(load(name="minimal-edu"), f"graphics.{key}")


def _hex(h: str) -> np.ndarray:
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


# ---------- hình học ----------
def resample(pts, step: float = 2.0) -> np.ndarray:
    """Chia đều theo độ dài cung (bước ~step px) để tiến độ vẽ = tỉ lệ độ dài cung."""
    p = np.asarray(pts, dtype=np.float32)
    seg = np.hypot(*np.diff(p, axis=0).T)
    s = np.concatenate([[0], np.cumsum(seg)])
    n = max(2, int(s[-1] / step) + 1)
    t = np.linspace(0, s[-1], n)
    return np.stack([np.interp(t, s, p[:, 0]), np.interp(t, s, p[:, 1])], 1)


def smooth(pts, per_seg: int = 24) -> np.ndarray:
    """Catmull-Rom qua các điểm điều khiển (đường đồ thị mượt)."""
    p = np.asarray(pts, dtype=np.float32)
    q = np.vstack([p[0], p, p[-1]])
    out = []
    for i in range(len(p) - 1):
        p0, p1, p2, p3 = q[i], q[i + 1], q[i + 2], q[i + 3]
        for t in np.linspace(0, 1, per_seg, endpoint=False):
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(p[-1])
    return np.asarray(out, dtype=np.float32)


def _wobble(pts: np.ndarray, amp: float, seed: int) -> np.ndarray:
    """Run tay: dịch mềm (nhiễu thưa nội suy) theo cả hai trục; hai đầu giữ nguyên."""
    if amp <= 0:
        return pts
    rng = np.random.default_rng(seed)
    k = max(3, len(pts) // 30)
    xs = np.linspace(0, len(pts) - 1, k)
    off = np.stack([np.interp(np.arange(len(pts)), xs, rng.normal(0, amp, k)) for _ in range(2)], 1)
    off[0] = off[-1] = 0
    return pts + off


def _ease(kind: str, u: float) -> float:
    if kind == "linear":
        return u
    if kind == "ease_out":
        return 1 - (1 - u) ** 3
    if kind == "ease_in_out":
        return u * u * (3 - 2 * u)
    raise ValueError(f"easing lạ: {kind} (linear | ease_out | ease_in_out)")


# ---------- vẽ ----------
def _polyline(mask: np.ndarray, pts: np.ndarray, width: float) -> None:
    import cv2
    q = np.round(pts * (1 << SHIFT)).astype(np.int32)
    t = max(1, round(width) - 1)                            # cv2 AA vẽ dày t+1 px
    cv2.polylines(mask, [q], False, 255, thickness=t, lineType=cv2.LINE_AA, shift=SHIFT)
    for x, y in (q[0], q[-1]):                              # đầu tròn
        cv2.circle(mask, (int(x), int(y)), round((t + 1) / 2 * (1 << SHIFT)), 255, -1, cv2.LINE_AA, SHIFT)


def _arrow_head(mask: np.ndarray, pts: np.ndarray, width: float) -> None:
    tip = pts[-1]
    back = pts[max(0, len(pts) - 1 - 12)]
    ang = np.arctan2(tip[1] - back[1], tip[0] - back[0])
    ln = width * 3.2
    for da in (np.radians(150), np.radians(-150)):
        end = tip + ln * np.array([np.cos(ang + da), np.sin(ang + da)])
        _polyline(mask, np.array([tip, end]), width)


def _over(prem: np.ndarray, alpha: np.ndarray, mask: np.ndarray, color: np.ndarray) -> None:
    a = mask.astype(np.float32)[..., None] / 255
    prem *= 1 - a
    prem += color * a
    alpha *= 1 - a[..., 0]
    alpha += a[..., 0]


def _compose(stroke: np.ndarray, dot: np.ndarray | None, color: np.ndarray, glow: np.ndarray | None,
             width: float, dot_color: np.ndarray) -> np.ndarray:
    import cv2
    prem, alpha = np.zeros((H, W, 3), np.float32), np.zeros((H, W), np.float32)
    if glow is not None:
        both = stroke if dot is None else np.maximum(stroke, dot)
        halo = cv2.GaussianBlur(both, (0, 0), max(2.0, width * 0.6))
        _over(prem, alpha, np.clip(halo.astype(np.float32) * 1.4, 0, 255).astype(np.uint8), glow)
    _over(prem, alpha, stroke, color)
    if dot is not None:
        _over(prem, alpha, dot, dot_color)
    out = np.zeros((H, W, 4), np.uint8)
    nz = alpha > 0
    out[..., :3][nz] = np.clip(prem[nz] / alpha[nz][:, None], 0, 255).astype(np.uint8)
    out[..., 3] = np.round(alpha * 255).astype(np.uint8)
    return out


def render_frames(points, frames: int, width: float, color: str, glow: str | None = None, head: str = "none",
                  easing: str = "ease_out", jitter: float = 0.0, seed: int = 0, dot_color: str = "#FFFFFF") -> Iterator[np.ndarray]:
    """Sinh `frames` khung RGBA (H×W×4 uint8, alpha thẳng). Khung 0 trống, khung cuối đủ nét; head: none | arrow (chỉ hiện
    ở khung cuối) | dot (chấm bám đầu nét, có quầng nếu glow)."""
    if frames < 2:
        raise ValueError("frames phải ≥ 2 (khung 0 trống + ít nhất 1 khung vẽ)")
    if head not in ("none", "arrow", "dot"):
        raise ValueError(f"head lạ: {head}")
    pts = _wobble(resample(points), jitter * width, seed)
    col, gcol = _hex(color), (_hex(glow) if glow else None)
    for f in range(frames):
        p = _ease(easing, f / (frames - 1))
        n = round(p * (len(pts) - 1))
        if f == 0 or n < 1:
            yield np.zeros((H, W, 4), np.uint8)
            continue
        part = pts[: n + 1]
        stroke, dot = np.zeros((H, W), np.uint8), None
        _polyline(stroke, part, width)
        if head == "arrow" and f == frames - 1:
            _arrow_head(stroke, part, width)
        if head == "dot":
            dot = np.zeros((H, W), np.uint8)
            _polyline(dot, part[-1:].repeat(2, 0), width * 1.7)
        yield _compose(stroke, dot, col, gcol, width, _hex(dot_color))


def write(spec: dict, out: str | Path, fps: int = 30) -> Path:
    """Ghi ProRes 4444 alpha (cùng bộ mã hoá rvm-matte / matte.py): prores_ks -profile:v 4444 -pix_fmt yuva444p10le."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-framerate", str(fps), "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for fr in render_frames(**spec):
            proc.stdin.write(fr.tobytes())
    finally:
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError(f"ffmpeg ghi {out} lỗi")
    return out


def still(spec: dict, out_png: str | Path) -> Path:
    """Khung cuối (nét đủ) ra PNG RGBA 1080×1920 — cho lớp tĩnh nối sau .mov hoặc lớp lộ bằng crop."""
    from PIL import Image
    last = None
    for last in render_frames(**spec):
        pass
    out = Path(out_png)
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(last, "RGBA").save(out)
    return out


# ---------- preset ----------
def _line_w() -> float:
    return _g("line_width_ratio") * W


def spiral(cx: float = 540, cy: float = 960, r_max: float = 400, turns: float | None = None, frames: int | None = None,
           seed: int = 1) -> dict:
    """Xoắn ốc Archimedes vẽ từ tâm: ~4,2 vòng, 23 khung, ease-out theo độ dài cung, run tay, quầng sáng."""
    turns = turns or _g("spiral")["turns"]
    th = np.linspace(0, turns * 2 * np.pi, 1200)
    r = r_max * th / th[-1]
    pts = np.stack([cx + r * np.cos(th), cy + r * np.sin(th)], 1)
    w = HAND_WIDTH_RATIO * W
    return dict(points=pts, frames=frames or _g("spiral")["frames"], width=w, color=_g("accent_spiral"),
                glow=_g("spiral_glow"), head="none", easing="ease_out", jitter=HAND_JITTER, seed=seed)


def arrow_curve(p0=(220, 1500), p1=(820, 1000), bend: float = 0.35, frames: int | None = None, seed: int = 2) -> dict:
    """Mũi tên cong (Bezier bậc 2) vẽ 3–4 khung; đầu mũi tên chỉ hiện ở khung cuối."""
    a, b = np.array(p0, np.float32), np.array(p1, np.float32)
    d = b - a
    ctrl = (a + b) / 2 + bend * np.array([-d[1], d[0]])
    t = np.linspace(0, 1, 200)[:, None]
    pts = (1 - t) ** 2 * a + 2 * (1 - t) * t * ctrl + t ** 2 * b
    return dict(points=pts, frames=frames or _g("arrow_frames")[-1], width=HAND_WIDTH_RATIO * W, color=_g("accent_line"),
                glow=None, head="arrow", easing="ease_out", jitter=HAND_JITTER, seed=seed)


def line(points, frames: int | None = None, easing: str = "linear") -> dict:
    """Đường gấp khúc dày line_width_ratio·W, vẽ 9 khung (đều)."""
    return dict(points=np.asarray(points, np.float32), frames=frames or _g("line_draw_frames"), width=_line_w(),
                color=_g("accent_line"), glow=None, head="none", easing=easing, jitter=0.0, seed=0)


def zigzag(p0, p1, n: int = 5, amp: float = 60, frames: int | None = None, seed: int = 3) -> dict:
    """Zig-zag n nhịp từ p0 tới p1 (nét gạch chân nguệch ngoạc)."""
    a, b = np.array(p0, np.float32), np.array(p1, np.float32)
    d = (b - a) / max(1e-6, np.hypot(*(b - a)))
    nrm = np.array([-d[1], d[0]])
    pts = [a] + [a + (b - a) * (i + 0.5) / n + nrm * amp * (1 if i % 2 == 0 else -1) for i in range(n)] + [b]
    return dict(points=np.array(pts), frames=frames or _g("line_draw_frames"), width=HAND_WIDTH_RATIO * W,
                color=_g("accent_line"), glow=None, head="none", easing="linear", jitter=HAND_JITTER, seed=seed)


def graph_curve(points, frames: int | None = None) -> dict:
    """Đường đồ thị mượt qua các điểm, chấm trắng có quầng chạy ở đầu nét; thời lượng = graph_axis_frames."""
    return dict(points=smooth(points), frames=frames or _g("graph_axis_frames"), width=HAND_WIDTH_RATIO * W,
                color=_g("accent_line"), glow=_g("accent_line"), head="dot", easing="linear", jitter=0.0, seed=0)


# ---------- CLI ----------
def _xy(s: str) -> tuple[float, float]:
    x, y = s.split(",")
    return float(x), float(y)


def _build(a: argparse.Namespace) -> dict:
    fr = {"frames": a.frames}
    if a.cmd == "spiral":
        return spiral(a.cx, a.cy, a.r, **fr)
    if a.cmd == "arrow":
        return arrow_curve(a.p0, a.p1, **fr)
    if a.cmd == "zigzag":
        return zigzag(a.p0, a.p1, **fr)
    pts = [_xy(s) for s in a.points.split()]
    return line(pts, **fr) if a.cmd == "line" else graph_curve(pts, **fr)


def main() -> None:
    ap = argparse.ArgumentParser(description="Vẽ nét từng khung → ProRes 4444 alpha")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("spiral", "arrow", "line", "zigzag", "graph"):
        s = sub.add_parser(name)
        s.add_argument("--out", required=True)
        s.add_argument("--fps", type=int, default=30)
        s.add_argument("--frames", type=int, default=None, help="mặc định theo hồ sơ")
        s.add_argument("--still", default=None, help="ghi thêm khung cuối ra PNG")
        if name in ("line", "graph"):
            s.add_argument("--points", required=True, help='"x,y x,y …"')
        if name in ("arrow", "zigzag"):
            s.add_argument("--p0", type=_xy, default=(220, 1500) if name == "arrow" else (100, 700))
            s.add_argument("--p1", type=_xy, default=(820, 1000) if name == "arrow" else (980, 1100))
        if name == "spiral":
            s.add_argument("--cx", type=float, default=540)
            s.add_argument("--cy", type=float, default=960)
            s.add_argument("--r", type=float, default=400)
    a = ap.parse_args()
    spec = _build(a)
    print(write(spec, a.out, a.fps), spec["frames"], "khung")
    if a.still:
        print(still(spec, a.still))


if __name__ == "__main__":
    main()
