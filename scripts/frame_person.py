#!/usr/bin/env python3
"""Rule 5 (người dùng chốt 2026-11-11): phông SÁNG phía sau người + người nằm trong 2/3 DƯỚI khung.

Đỉnh đầu ở đường 1/3 trên (y ≈ 640 trên khung 1080x1920); 1/3 trên là nền sáng để đặt chữ chính (vùng y 240–680).
Chỉ áp cho clip QUAY THẬT (`live_shoot` trong manifest) — KHÔNG áp cho avatar HeyGen (người dùng chốt 2026-11-11):
  - green   phông xanh (soucre thô)  → tách người (rvm-matte) + ghép lên phòng làm việc sáng, làm mờ
  - dark    quay thật nền tối        → như trên
  - bright  nền đã sáng                → chỉ chỉnh khung (phóng + cắt, tối đa SCALE_MAX để không mờ)

    python frame_person.py analyze clip.mp4 [...]          # đo: loại nền, độ sáng, đỉnh đầu, kế hoạch
    python frame_person.py fix clip.mp4 out.mp4 [--bg anh.png]
    from frame_person import analyze, plan, reframe_vf

Nền sáng: mọi ảnh trong NEN_DIR (luân phiên theo tên clip); thư mục trống thì tự vẽ nền dự phòng (phòng sáng mờ).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_kit import AAC_HQ, X264_HQ  # noqa: E402

W, H = 1080, 1920
HEAD_TARGET = H // 3              # đỉnh đầu ở đường 1/3 trên
HEAD_TOL = 60                     # lệch ±60 px vẫn đạt
SCALE_MAX = 1.35                  # chỉ chỉnh khung (không tách nền) tối đa 135 % — hơn nữa là mờ (Rule 3)
BRIGHT_LUMA = 150                 # nền trung bình ≥ 150 / 255 = sáng
GREEN_RATIO = 0.35                # ≥ 35 % điểm ảnh nền xanh lá rõ = phông xanh
BG_BLUR = 18                      # độ nhoè nền thay vào (phòng làm việc sáng, mờ)
MODEL = HERE.parent / "assets/models/face_detection_yunet_2023mar.onnx"   # OpenCV Zoo YuNet (MIT)
NEN_DIR = Path("/home/vmiz/Thanh/Media/TNEDIT/07_Assets/Nen_Background/Phong_Lam_Viec_Sang")
FALLBACK_BG = NEN_DIR / "_du_phong_phong_sang_mo.png"


def _frames(path: Path, n: int = 9) -> list[np.ndarray]:
    cap = cv2.VideoCapture(str(path))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    out = []
    for i in range(n):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(total * (i + 0.5) / n))
        ok, f = cap.read()
        if ok:
            out.append(f)
    cap.release()
    return out


def _face(img: np.ndarray, det) -> tuple[float, float, float, float] | None:
    h, w = img.shape[:2]
    det.setInputSize((w, h))
    _, faces = det.detect(img)
    if faces is None or not len(faces):
        return None
    x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])[:4]
    return float(x), float(y), float(fw), float(fh)


ROTS = {0: None, 90: cv2.ROTATE_90_CLOCKWISE, 270: cv2.ROTATE_90_COUNTERCLOCKWISE}
TRANSPOSE = {0: "", 90: "transpose=1,", 270: "transpose=2,"}   # ffmpeg: 1 = xoay 90° chiều kim đồng hồ


def cover_k(w0: int, h0: int) -> float:
    """Hệ số phóng để nguồn PHỦ KÍN khung dọc 1080x1920 (nguồn ngang 4K → cắt hai bên quanh mặt)."""
    return max(W / w0, H / h0)


def analyze(path: str | Path) -> dict:
    """Đo trên ~9 khung: hướng xoay, loại nền (green / bright / dark), độ sáng nền, đỉnh đầu & tâm mặt quy về khung
    1080x1920 phủ kín. Clip quay xoay ngang (phông xanh soucre thô) được thử 0° / 90° / 270°, lấy hướng thấy mặt."""
    path = Path(path)
    raw = _frames(path)
    if not raw:
        return {"file": str(path), "error": "không đọc được khung"}
    best = (-1, 0, raw)
    for rot, code in ROTS.items():
        fr = raw if code is None else [cv2.rotate(f, code) for f in raw]
        h_, w_ = fr[0].shape[:2]
        d_ = cv2.FaceDetectorYN.create(str(MODEL), "", (w_, h_), 0.6, 0.3, 5000)
        n = sum(1 for f in fr[::2] if _face(f, d_))
        if n > best[0]:
            best = (n, rot, fr)
        if rot == 0 and n >= 2:                       # đứng thẳng đã thấy mặt: không thử xoay
            break
    _, rot, frames = best
    h0, w0 = frames[0].shape[:2]
    k = cover_k(w0, h0)
    det = cv2.FaceDetectorYN.create(str(MODEL), "", (w0, h0), 0.6, 0.3, 5000)
    tops, chins, lumas, greens, xs = [], [], [], [], []
    for f in frames:
        fc = _face(f, det)
        mask = np.ones(f.shape[:2], bool)
        if fc:
            x, y, fw, fh = fc
            top = max(0.0, y - 0.45 * fh)              # tóc / đỉnh đầu ≈ 0,45 chiều cao mặt trên khung mặt
            tops.append(top * k); chins.append((y + fh) * k); xs.append((x + fw / 2) * k)
            x0, x1 = int(max(0, x - 1.3 * fw)), int(min(w0, x + 2.3 * fw))
            mask[int(top):, x0:x1] = False             # bỏ vùng người (từ đầu xuống, rộng ~3,6 mặt)
        bg = f[mask] if mask.any() else f.reshape(-1, 3)
        b, g, r = bg[:, 0].astype(int), bg[:, 1].astype(int), bg[:, 2].astype(int)
        lumas.append(float((0.114 * b + 0.587 * g + 0.299 * r).mean()))
        greens.append(float(((g > r + 25) & (g > b + 25)).mean()))
    res = {"file": str(path), "src_size": [w0, h0], "rotate": rot, "faces": len(tops),
           "bg_luma": round(float(np.median(lumas)), 1), "green_ratio": round(float(np.median(greens)), 3)}
    res["kind"] = "green" if res["green_ratio"] >= GREEN_RATIO else ("bright" if res["bg_luma"] >= BRIGHT_LUMA else "dark")
    if tops:
        res.update({"head_top": round(float(np.median(tops))), "chin": round(float(np.median(chins))),
                    "face_cx": round(float(np.median(xs)))})
    return res


def plan(a: dict) -> dict:
    """Quyết định: ok (đã đạt) · reframe (phóng + cắt, nền giữ) · composite (tách người, ghép nền sáng)."""
    if "head_top" not in a:
        return {"action": "skip", "why": "không thấy mặt người"}
    ht = a["head_top"]
    if a["kind"] != "bright":
        s = (H - HEAD_TARGET) / max(1.0, H - ht)       # đầu ở 1/3, thân chạm đáy khung
        return {"action": "composite", "scale": round(s, 3), "dy": round(HEAD_TARGET - s * ht),
                "why": f"nền {'phông xanh' if a['kind'] == 'green' else 'tối'} (sáng {a['bg_luma']}) → ghép phòng làm việc sáng"}
    if abs(ht - HEAD_TARGET) <= HEAD_TOL:
        return {"action": "ok", "why": f"nền sáng, đỉnh đầu y={ht} đã ở 1/3 trên"}
    s = HEAD_TARGET / ht if ht < HEAD_TARGET else (H - HEAD_TARGET) / (H - ht)
    s = max(1.0, s)
    if s > SCALE_MAX:
        s2 = (H - HEAD_TARGET) / max(1.0, H - ht)
        return {"action": "composite", "scale": round(s2, 3), "dy": round(HEAD_TARGET - s2 * ht),
                "why": f"cần phóng {s:.2f}× (> {SCALE_MAX}) — tách người, ghép nền sáng thay vì phóng mờ"}
    crop_y = min(max(0.0, s * ht - HEAD_TARGET), H * s - H)
    return {"action": "reframe", "scale": round(s, 3), "crop_y": round(crop_y),
            "why": f"nền sáng, đỉnh đầu y={ht} → phóng {s:.2f}× đưa về y≈{HEAD_TARGET}"}


def reframe_vf(a: dict, p: dict) -> str:
    """Bộ lọc ffmpeg đưa khung về 1080x1920 với người ở 2/3 dưới (chỉ cho action reframe / ok)."""
    w0, h0 = a["src_size"]
    k = cover_k(w0, h0)
    s = p.get("scale", 1.0) if p["action"] == "reframe" else 1.0
    sw, sh = round(w0 * k * s / 2) * 2, round(h0 * k * s / 2) * 2
    cx = a.get("face_cx", sw / s / 2) * s
    x = int(min(max(0, cx - W / 2), sw - W))
    y = int(p.get("crop_y", (sh - H) / 2)) if p["action"] == "reframe" else int((sh - H) / 2)
    return f"{TRANSPOSE[a.get('rotate', 0)]}scale={sw}:{sh}:flags=lanczos,crop={W}:{H}:{x}:{min(max(0, y), sh - H)}"


def fallback_bg() -> Path:
    """Nền dự phòng: phòng làm việc sáng, mờ (tường trắng ấm, vệt cửa sổ, cây xanh, bàn gỗ sáng) — khi chưa có ảnh thật."""
    if FALLBACK_BG.is_file():
        return FALLBACK_BG
    NEN_DIR.mkdir(parents=True, exist_ok=True)
    y = np.linspace(0, 1, H)[:, None]
    img = np.zeros((H, W, 3), np.float32)
    img[:] = (238, 241, 245)                                         # BGR trắng ấm
    img += (y * np.array([-18, -14, -8]))[..., None].transpose(0, 2, 1).reshape(H, 1, 3)
    cv2.rectangle(img, (640, 180), (1040, 1150), (252, 252, 250), -1)   # cửa sổ sáng
    cv2.rectangle(img, (0, 1330), (W, H), (150, 186, 214), -1)          # bàn gỗ sồi sáng
    cv2.ellipse(img, (150, 980), (150, 260), 0, 0, 360, (120, 170, 120), -1)   # chậu cây
    cv2.rectangle(img, (60, 420), (420, 520), (200, 214, 226), -1)      # kệ gỗ
    img = cv2.GaussianBlur(img, (0, 0), 45)
    cv2.imwrite(str(FALLBACK_BG), np.clip(img, 0, 255).astype(np.uint8))
    return FALLBACK_BG


def pick_bg(name: str) -> Path:
    imgs = sorted(p for p in NEN_DIR.glob("*") if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
                  and not p.name.startswith("_"))
    return imgs[zlib.crc32(name.encode()) % len(imgs)] if imgs else fallback_bg()


def _run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"{Path(cmd[0]).name} lỗi {r.returncode}: {(r.stderr or r.stdout)[-500:]}")


def fix(src: str | Path, out: str | Path, bg: str | Path | None = None, a: dict | None = None) -> dict:
    """Xuất bản đúng Rule 5 (1080x1920, CRF 12, giữ tiếng). Trả kết quả đo + kế hoạch đã áp."""
    src, out = Path(src), Path(out)
    a = a or analyze(src)
    p = plan(a)
    out.parent.mkdir(parents=True, exist_ok=True)
    if p["action"] in ("ok", "reframe", "skip"):
        vf = (reframe_vf(a, p) if "src_size" in a and p["action"] != "skip"     # không thấy mặt: phủ kín + cắt giữa, không ép giãn
              else f"{TRANSPOSE[a.get('rotate', 0)]}scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}")
        _run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf", vf + ",fps=30", "-map", "0:v", "-map", "0:a?",
              *X264_HQ, *AAC_HQ, str(out)])
        return {**a, **p, "out": str(out)}
    bgp = Path(bg) if bg else pick_bg(src.stem)
    with tempfile.TemporaryDirectory() as td:
        w0, h0 = a["src_size"]
        k = cover_k(w0, h0)
        ww, wh = round(w0 * k / 2) * 2, round(h0 * k / 2) * 2
        work, alpha = Path(td) / "work.mp4", Path(td) / "person.mov"
        # xoay + thu về khổ khung dọc trước khi tách nền: 4K đưa thẳng vào rvm-matte hết bộ nhớ GPU 8 GB (đo 2026-11-11)
        _run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-an", "-vf",
              f"{TRANSPOSE[a.get('rotate', 0)]}scale={ww}:{wh}:flags=lanczos", *X264_HQ, str(work)])
        import fcntl
        with open("/tmp/kb_gpu.lock", "w") as lk:                      # chung khoá GPU với run_kb_v2152 (tách nền lần lượt)
            fcntl.flock(lk, fcntl.LOCK_EX)
            _run([str(Path.home() / ".local/bin/rvm-matte"), str(work), str(alpha), "0.25"])   # ProRes 4444 có alpha
        s = p["scale"]
        fw, fh = round(ww * s / 2) * 2, round(wh * s / 2) * 2
        x = round(W / 2 - a.get("face_cx", W / 2) * s)
        fg = f"[1:v]scale={fw}:{fh}:flags=lanczos,format=yuva444p[fg]"
        back = f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},gblur=sigma={BG_BLUR},format=yuv444p[bg]"
        graph = f"{back};{fg};[bg][fg]overlay=x={x}:y={p['dy']}:shortest=1,format=yuv420p,fps=30[v]"
        _run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(bgp), "-i", str(alpha), "-i", str(src),
              "-filter_complex", graph, "-map", "[v]", "-map", "2:a?", "-shortest", *X264_HQ, *AAC_HQ, str(out)])
    return {**a, **p, "bg": str(bgp), "out": str(out)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    an = sub.add_parser("analyze"); an.add_argument("clips", nargs="+")
    fx = sub.add_parser("fix"); fx.add_argument("src"); fx.add_argument("out"); fx.add_argument("--bg")
    a = ap.parse_args()
    if a.cmd == "analyze":
        for c in a.clips:
            r = analyze(c)
            print(json.dumps({**r, "plan": plan(r)}, ensure_ascii=False))
    else:
        print(json.dumps(fix(a.src, a.out, a.bg), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
