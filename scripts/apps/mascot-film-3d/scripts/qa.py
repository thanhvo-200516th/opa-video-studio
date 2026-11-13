"""Kiểm tự động cho phim 3D (film3d). Đo, không đoán.

  python -I tools/film3d/qa.py shape <coverage.png>
      Đúng hình: so ảnh phủ chính diện (render orthographic) với alpha của logo PNG gốc 2000 px.
      Đạt khi IoU >= 0,999 và lệch viền tối đa <= 1 px.
  python -I tools/film3d/qa.py brand <thư mục> [--color blue|white]
      Màu Bò trên mọi <id>.png có <id>.mask.png: mặt trước (pháp tuyến vật z > 0,92, co vào 3 px).
      Đạt khi trung vị ΔE2000 <= 2 (2–3: sửa nếu kéo dài > 0,5 s; > 3: hỏng).
  python -I tools/film3d/qa.py video <mp4> <thư mục mặt nạ> [--color ...]
      Như brand nhưng đo trên các khung đã giải mã của file video (sau khi ghép), khớp theo tên fNNNN.mask.png.
  python -I tools/film3d/qa.py lock <khung 3D cuối.png> <khung 2D đầu end card.png>
      Cầu 3D -> 2D: bóng Bò trắng trên nền #0068FF (kênh R làm độ phủ) của hai khung kề nhau quanh cú cắt.
      Đạt khi lệch viền tối đa <= 2 px.
  python -I tools/film3d/qa.py boxes <boxes.json> [--allow 6.75:7.42,...]
      Cắt mép (thang kiểm loại F nấc 3): các đoạn ngọn sừng hoặc Bò ra ngoài khung, từ render.py job kind "boxes".
      Đạt khi mọi đoạn nằm trong một khoảng --allow (cận cố ý, storyboard có ghi).
  python -I tools/film3d/qa.py text <phần 3D.mkv> <lớp phủ.mov> [--step 6]
      Chữ Remotion trên nền 3D: trong khung bao vùng chữ (nới 16 px), nền 3D xấu nhất (phân vị 99,5 với chữ trắng,
      0,5 với chữ đen) so với màu chữ theo tương phản WCAG. Đạt khi >= 4,5:1 ở mọi khung có chữ.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation, binary_erosion
from scipy.spatial import cKDTree
from skimage.color import deltaE_ciede2000, rgb2lab
from skimage.measure import find_contours

ROOT = Path(__file__).resolve().parents[2]
LOGO_PNG = ROOT / "logo" / "OPA-V4-A-Core-blue-2000.png"
TARGET = {"blue": (0, 104, 255), "white": (255, 255, 255)}  # #0068FF đo trên MP4 dự án ra (0,103,255)


def shape_check(cov: np.ndarray, ref: np.ndarray) -> dict:
    a, b = cov >= 0.5, ref >= 0.5
    iou = float((a & b).sum() / (a | b).sum())
    ca, cb = np.vstack(find_contours(cov, 0.5)), np.vstack(find_contours(ref, 0.5))
    d = np.concatenate([cKDTree(cb).query(ca)[0], cKDTree(ca).query(cb)[0]])
    return {"IoU": round(iou, 5), "edgeMaxPx": round(float(d.max()), 3), "edgeP99Px": round(float(np.percentile(d, 99)), 3),
            "edgeMeanPx": round(float(d.mean()), 3), "pass": bool(iou >= 0.999 and d.max() <= 1.0)}


def _lab(rgb: np.ndarray) -> np.ndarray:
    return rgb2lab(rgb.reshape(-1, 1, 3).astype(np.float64) / 255.0).reshape(-1, 3)


def brand_stats(frame: np.ndarray, mask: np.ndarray, color: str) -> dict:
    """frame: HxWx3 uint8; mask: HxWx(>=2) uint8 (R = Bò, G = pháp tuyến vật z * 0,5 + 0,5)."""
    target = np.array(TARGET[color], np.float64)
    body = binary_erosion(mask[..., 0] > 250, iterations=3)
    front = body & (mask[..., 1] > 0.96 * 255)
    side = body & (mask[..., 1] < 0.75 * 255)
    out: dict = {}
    for name, m in (("front", front), ("side", side)):
        if m.sum() < 50:
            out[name] = None
            continue
        px = frame[m].astype(np.float64)
        med = np.median(px, 0)
        de_px = deltaE_ciede2000(_lab(px), np.repeat(_lab(target[None]), len(px), 0))
        out[name] = {"px": int(m.sum()), "medianRGB": [int(round(v)) for v in med],
                     "hex": "#%02X%02X%02X" % tuple(int(round(v)) for v in med),
                     "dE00median": round(float(deltaE_ciede2000(_lab(med[None]), _lab(target[None]))[0]), 2),
                     "dE00p90": round(float(np.percentile(de_px, 90)), 2),
                     "within4": round(float((np.abs(px - target).max(1) <= 4).mean()), 3)}
    f = out["front"]
    out["verdict"] = "chưa đo" if f is None else ("đạt" if f["dE00median"] <= 2 else ("cần sửa" if f["dE00median"] <= 3 else "hỏng"))
    # Nền ngay sau Bò: vòng 6–20 px quanh bóng Bò. Luật cảnh đêm (Minh 19/10): Bò xanh chỉ đứng trước nền sáng.
    whole = mask[..., 0] > 128
    ring = binary_dilation(whole, iterations=20) & ~binary_dilation(whole, iterations=6)
    if ring.sum() > 0:
        luma = frame[ring].astype(np.float64) @ np.array([0.2126, 0.7152, 0.0722]) / 255.0
        out["ringLuma"] = {"median": round(float(np.median(luma)), 3), "p10": round(float(np.percentile(luma, 10)), 3)}
    return out


def _load_mask(p: Path) -> np.ndarray:
    return np.asarray(Image.open(p).convert("RGB"))


def cmd_shape(cov_png: Path) -> dict:
    cov = np.asarray(Image.open(cov_png).convert("L")).astype(np.float64) / 255.0
    ref = np.asarray(Image.open(LOGO_PNG).convert("RGBA"))[..., 3].astype(np.float64) / 255.0
    return shape_check(cov, ref)


def cmd_brand(folder: Path, color: str) -> dict:
    res = {}
    for mp in sorted(folder.glob("*.mask.png")):
        fid = mp.name[: -len(".mask.png")]
        fp = folder / f"{fid}.png"
        if not fp.exists():
            continue
        meta_p = folder / f"{fid}.json"
        c = color
        if meta_p.exists():
            c = json.loads(meta_p.read_text(encoding="utf-8")).get("cfg", {}).get("color", color)
        res[fid] = brand_stats(np.asarray(Image.open(fp).convert("RGB")), _load_mask(mp), c)
    return res


def cmd_lock(a_png: Path, b_png: Path) -> dict:
    cov = [np.asarray(Image.open(p).convert("RGB"))[..., 0].astype(np.float64) / 255.0 for p in (a_png, b_png)]
    res = shape_check(*cov)
    res["pass"] = bool(res["edgeMaxPx"] <= 2.0)
    for name, c in zip(("bbox3D", "bbox2D"), cov):
        ys, xs = np.nonzero(c >= 0.5)
        res[name] = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    return res


def _spans(flags: list[bool], frames: list[int], fps: int) -> list[tuple[float, float]]:
    """Các đoạn liền (giây, [từ; tới)) có cờ bật."""
    spans, start = [], None
    for f, on in zip(frames, flags):
        if on and start is None:
            start = f
        elif not on and start is not None:
            spans.append((start / fps, f / fps))
            start = None
    if start is not None:
        spans.append((start / fps, (frames[-1] + 1) / fps))
    return spans


def cmd_boxes(path: Path, allow: list[tuple[float, float]], horn_margin: float = 24.0) -> dict:
    """Ngọn sừng phải cách mép khung >= horn_margin px (chạm mép trông như bị cắt); thân Bò chỉ báo khi ra ngoài khung."""
    d = json.loads(path.read_text(encoding="utf-8"))
    w, h, fps, rows = d["w"], d["h"], d["fps"], d["rows"]
    frames = [r["f"] for r in rows]
    res: dict = {}
    for key in ("hornL", "hornR", "bo"):
        m = horn_margin if key != "bo" else 0.0
        out = [r[key][0] < m or r[key][1] < m or r[key][2] > w - m or r[key][3] > h - m for r in rows]
        res[key] = [{"from": round(a, 3), "to": round(b, 3), "allowed": any(x <= a and b <= y for x, y in allow)}
                    for a, b in _spans(out, frames, fps)]
    res["pass"] = all(s["allowed"] for k in ("hornL", "hornR", "bo") for s in res[k])
    return res


def _frames(src: Path, step: int, pix: str, w: int = 1920, h: int = 1080):
    """Giải mã mỗi `step` khung qua ống ffmpeg: (số khung, mảng HxWxC uint8)."""
    c = 4 if pix == "rgba" else 3
    p = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(src), "-vf",
                          f"select=not(mod(n\\,{step})),scale=in_color_matrix=bt709:in_range=tv", "-vsync", "0",
                          "-f", "rawvideo", "-pix_fmt", pix, "-"], stdout=subprocess.PIPE)
    try:
        n = 0
        while len(buf := p.stdout.read(w * h * c)) == w * h * c:
            yield n * step, np.frombuffer(buf, np.uint8).reshape(h, w, c)
            n += 1
    finally:   # dừng giữa chừng (nguồn kia hết trước): tắt ffmpeg, không để nó báo vỡ ống
        p.kill()
        p.stdout.close()
        p.wait()


def _lum(rgb: np.ndarray) -> np.ndarray:
    """Độ chói tương đối WCAG của các điểm sRGB (Nx3 uint8)."""
    c = rgb.astype(np.float64) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return c @ np.array([0.2126, 0.7152, 0.0722])


def cmd_text(base: Path, overlay: Path, step: int) -> dict:
    res = {}
    gb, go = _frames(base, step, "rgb24"), _frames(overlay, step, "rgba")
    try:
        for (f, bg), (_, ov) in zip(gb, go):
            _text_frame(res, f, bg, ov)
    finally:
        gb.close()
        go.close()
    return res


def _text_frame(res: dict, f: int, bg: np.ndarray, ov: np.ndarray) -> None:
    a = ov[..., 3]
    if (a > 0).mean() > 0.5 or not (a > 230).any():   # end card đục, hoặc khung không có chữ
        return
    ys, xs = np.nonzero(a > 0)
    y0, y1, x0, x1 = max(int(ys.min()) - 16, 0), int(ys.max()) + 17, max(int(xs.min()) - 16, 0), int(xs.max()) + 17
    lb = _lum(bg[y0:y1, x0:x1].reshape(-1, 3))
    lt = float(np.median(_lum(ov[a > 230][:, :3])))
    white = lt > 0.5
    worst = float(np.percentile(lb, 99.5 if white else 0.5))
    hi, lo = (lt, worst) if white else (worst, lt)
    contrast = (hi + 0.05) / (lo + 0.05)
    res[f"f{f:04d}"] = {"text": "trắng" if white else "đen", "box": [x0, y0, x1, y1], "bgMedian": round(float(np.median(lb)), 3),
                        "bgWorst": round(worst, 3), "contrast": round(contrast, 2), "pass": bool(contrast >= 4.5)}


def cmd_video(mp4: Path, mask_dir: Path, color: str) -> dict:
    res = {}
    for mp in sorted(mask_dir.glob("f*.mask.png")):
        f = int(mp.name[1:5])
        raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(mp4), "-vf", f"select=eq(n\\,{f})",
                              "-vsync", "0", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True, check=True).stdout
        mask = _load_mask(mp)
        h, w = mask.shape[:2]
        if len(raw) != h * w * 3:
            res[f"f{f:04d}"] = {"error": f"giải mã ra {len(raw)} byte, cần {h * w * 3}"}
            continue
        meta_p = mask_dir / f"f{f:04d}.json"   # màu Bò của khung này nếu job clip có ghi (Bò trắng ở cầu)
        c = json.loads(meta_p.read_text(encoding="utf-8")).get("cfg", {}).get("color", color) if meta_p.exists() else color
        res[f"f{f:04d}"] = brand_stats(np.frombuffer(raw, np.uint8).reshape(h, w, 3), mask, c)
    return res


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    color = argv[argv.index("--color") + 1] if "--color" in argv else "blue"
    if argv[1] == "shape":
        res = cmd_shape(Path(argv[2]))
    elif argv[1] == "brand":
        res = cmd_brand(Path(argv[2]), color)
    elif argv[1] == "video":
        res = cmd_video(Path(argv[2]), Path(argv[3]), color)
    elif argv[1] == "lock":
        res = cmd_lock(Path(argv[2]), Path(argv[3]))
    elif argv[1] == "boxes":
        allow = [tuple(float(v) for v in s.split(":")) for s in argv[argv.index("--allow") + 1].split(",")] if "--allow" in argv else []
        res = cmd_boxes(Path(argv[2]), allow)
    elif argv[1] == "text":
        res = cmd_text(Path(argv[2]), Path(argv[3]), int(argv[argv.index("--step") + 1]) if "--step" in argv else 6)
        if "--table" in argv:
            for k, v in res.items():
                print(f"{k}  chữ {v['text']:5s} nền giữa {v['bgMedian']:.3f} xấu nhất {v['bgWorst']:.3f}  "
                      f"tương phản {v['contrast']:>6.2f}:1  {'đạt' if v['pass'] else 'TRƯỢT'}")
            bad = [k for k, v in res.items() if not v["pass"]]
            print(f"{len(res)} khung có chữ; thấp nhất {min(v['contrast'] for v in res.values()):.2f}:1; trượt {len(bad)} {bad[:8]}")
            return 0 if not bad else 1
    else:
        print(__doc__)
        return 2
    if "--table" in argv and argv[1] in ("brand", "video"):
        for k, v in res.items():
            f, s = v.get("front"), v.get("side")
            fs = f"{f['hex']}  ΔE {f['dE00median']:>5}  p90 {f['dE00p90']:>5}  ±4 {f['within4']:>5}" if f else "-"
            ring = v.get("ringLuma")
            rs = f" | nền sau Bò {ring['median']:.2f} (p10 {ring['p10']:.2f})" if ring else ""
            print(f"{k:20s} trước {fs} | bên {s['hex'] if s else '-'}{rs} | {v.get('verdict', v.get('error'))}")
    else:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
