"""Chuyển 4 phần mascot Bò OPA (mascot/opa-mascot-parts.svg) sang dữ liệu path cho shape layer AE.

AE lưu path dạng đỉnh + tiếp tuyến tương đối (vertices, inTangents, outTangents). SVG có lệnh L, C, A;
cung A được đổi sang Bézier bậc 3 (mỗi cung ≤ 90°), sai số dưới 0,03 px ở khung 2000 px.

Chạy: python -I tools/svg_to_ae.py  → build/data/mascot_paths.jsxinc
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT.parents[1] / "mascot" / "opa-mascot-parts.svg"
OUT = ROOT / "build" / "data" / "mascot_paths.jsxinc"
TOKEN = re.compile(r"[MLCAZ]|-?\d*\.?\d+(?:e-?\d+)?", re.I)


def arc_to_cubics(p0, rx, ry, phi_deg, large, sweep, p1):
    """Cung SVG (tham số endpoint) → danh sách đoạn cubic [(c1, c2, end)]."""
    if rx == 0 or ry == 0:
        return [(p0, p1, p1)]
    phi = math.radians(phi_deg)
    cp, sp = math.cos(phi), math.sin(phi)
    dx, dy = (p0[0] - p1[0]) / 2, (p0[1] - p1[1]) / 2
    x1p, y1p = cp * dx + sp * dy, -sp * dx + cp * dy
    lam = (x1p / rx) ** 2 + (y1p / ry) ** 2
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    coef = math.sqrt(max(0.0, num / den)) * (-1 if large == sweep else 1)
    cxp, cyp = coef * rx * y1p / ry, -coef * ry * x1p / rx
    cx = cp * cxp - sp * cyp + (p0[0] + p1[0]) / 2
    cy = sp * cxp + cp * cyp + (p0[1] + p1[1]) / 2

    def ang(ux, uy, vx, vy):
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return a

    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and dt > 0:
        dt -= 2 * math.pi
    elif sweep and dt < 0:
        dt += 2 * math.pi
    n = max(1, math.ceil(abs(dt) / (math.pi / 2) - 1e-9))
    step = dt / n
    k = 4 / 3 * math.tan(step / 4)
    segs = []

    def pt(t):
        x, y = rx * math.cos(t), ry * math.sin(t)
        return (cp * x - sp * y + cx, sp * x + cp * y + cy)

    def dpt(t):
        x, y = -rx * math.sin(t), ry * math.cos(t)
        return (cp * x - sp * y, sp * x + cp * y)

    for i in range(n):
        a, b = t1 + i * step, t1 + (i + 1) * step
        pa, pb, da, db = pt(a), pt(b), dpt(a), dpt(b)
        c1 = (pa[0] + k * da[0], pa[1] + k * da[1])
        c2 = (pb[0] - k * db[0], pb[1] - k * db[1])
        segs.append((c1, c2, pb))
    segs[-1] = (segs[-1][0], segs[-1][1], p1)
    return segs


def parse_path(d: str) -> dict:
    toks = TOKEN.findall(d)
    i, cmd = 0, None
    verts, ins, outs = [], [], []
    cur = (0.0, 0.0)

    def num():
        nonlocal i
        v = float(toks[i])
        i += 1
        return v

    def add_vertex(p):
        verts.append(list(p))
        ins.append([0.0, 0.0])
        outs.append([0.0, 0.0])

    def add_cubic(c1, c2, end):
        prev = verts[-1]
        outs[-1] = [c1[0] - prev[0], c1[1] - prev[1]]
        add_vertex(end)
        ins[-1] = [c2[0] - end[0], c2[1] - end[1]]

    closed = False
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t.upper()
            i += 1
            if cmd == "Z":
                closed = True
                continue
        if cmd == "M":
            cur = (num(), num())
            add_vertex(cur)
            cmd = "L"
        elif cmd == "L":
            cur = (num(), num())
            add_vertex(cur)
        elif cmd == "C":
            c1, c2, end = (num(), num()), (num(), num()), (num(), num())
            add_cubic(c1, c2, end)
            cur = end
        elif cmd == "A":
            rx, ry, rot, large, sweep, x, y = num(), num(), num(), int(num()), int(num()), num(), num()
            for c1, c2, end in arc_to_cubics(cur, rx, ry, rot, large, sweep, (x, y)):
                add_cubic(c1, c2, end)
            cur = (x, y)
    # Đỉnh cuối trùng đỉnh đầu (path khép kín) → gộp để AE không có điểm thừa.
    if closed and len(verts) > 1 and math.dist(verts[0], verts[-1]) < 1e-6:
        ins[0] = ins[-1]
        verts.pop(), ins.pop(), outs.pop()
    r = lambda arr: [[round(a, 3), round(b, 3)] for a, b in arr]
    return {"v": r(verts), "i": r(ins), "o": r(outs), "closed": closed}


def main() -> None:
    svg = SVG.read_text(encoding="utf-8")
    parts = {}
    for pid, d in re.findall(r'<path id="([^"]+)"[^>]*?d="([^"]+)"', svg):
        parts[pid] = parse_path(d)
    data = {
        "viewBox": [2000, 2000],
        "bbox": [306.31, 367.33, 1693.69, 1632.8],
        "pivots": {"a-horn-left": [569.16, 901.07], "b-horn-right": [1430.84, 901.07]},
        "parts": parts,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("// Sinh tự động từ mascot/opa-mascot-parts.svg bởi tools/svg_to_ae.py. Không sửa tay.\n"
                   "var MASCOT = " + json.dumps(data, separators=(",", ":")) + ";\n", encoding="utf-8")
    print("OK", OUT.name, {k: len(v["v"]) for k, v in parts.items()})


if __name__ == "__main__":
    main()
