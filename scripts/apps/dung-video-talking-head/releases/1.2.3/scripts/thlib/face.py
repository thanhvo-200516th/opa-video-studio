"""thlib.face — track mặt người dẫn ở INTAKE (spec 1.1.1 §8.1, R61).

Venv Hermes có OpenCV 5.0 không còn bộ phát hiện Haar, nên module này tự chạy Viola-Jones bằng
numpy trên cascade vendored `data/haarcascade_frontalface_default.xml` (bản của OpenCV 4.13), chỉ
dùng `cv2.resize` và `cv2.integral` — port của prototype design111/mouthsafe/nphaar2.py:
- master.mp4 → ffmpeg `fps=25,scale=270:480:flags=area`, gray; toạ độ ra × 1080/270 = 4;
- lô 16 khung; tỉ lệ 5.6·1.06^k (k = 0..7); bước 2 px; chuẩn hoá phương sai trên ô trong 22×22;
- gộp: trung vị các hit, giữ hit trong 0.2·w quanh nó, lấy trung bình; ít hơn 3 hit là hụt.

`face.json` (schema face/1) do INTAKE ghi một lần; hụt không bao giờ được lấp; BUILD và VERIFY chỉ
đọc, không track lại. Cổng INTAKE "mặt" (FACE_TRACK, BLOCK capability, owner dev) là `gate`.
"""

from __future__ import annotations

import functools
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import NamedTuple

import cv2
import numpy as np

from . import manifest, paths, proc, state

SCHEMA = "face/1"
FPS = 25                  # face/1: mọi khung 25 fps của master (nguồn HeyGen 25 fps)
OUT_W = 1080              # bề ngang khung ra 1080×1920 — toạ độ face.json theo khung này
BATCH = 16                # số khung mỗi bước numpy; chỉ đổi tốc độ, không đổi kết quả
DECODE_TIMEOUT_S = 600    # trần ffmpeg giải mã master (R47)
FACE_JSON = "face.json"


class Cascade(NamedTuple):
    """Cascade Haar đã nạp: cửa sổ win×win, feats[i] = [(x, y, w, h, trọng số)], stages =
    [(ngưỡng stage, [(feature i, ngưỡng node, lá trái, lá phải)])]."""
    win: int
    feats: list
    stages: list


def load_cascade(path: Path) -> Cascade:
    """Đọc cascade dạng XML mới của OpenCV (stump: một node, hai lá)."""
    root = ET.parse(path).getroot().find("cascade")
    feats = [[(int(x), int(y), int(w), int(h), float(wt)) for x, y, w, h, wt in
              (r.text.split() for r in f.find("rects"))] for f in root.find("features")]
    stages = []
    for st in root.find("stages"):
        weak = []
        for wc in st.find("weakClassifiers"):
            node, leaf = wc.find("internalNodes").text.split(), wc.find("leafValues").text.split()
            weak.append((int(node[2]), float(node[3]), float(leaf[0]), float(leaf[1])))
        stages.append((float(st.find("stageThreshold").text), weak))
    return Cascade(int(root.find("width").text), feats, stages)


@functools.lru_cache(maxsize=2)
def _cascade(path: str) -> Cascade:
    return load_cascade(Path(path))


def cascade_path(R) -> Path:
    return paths.release_dir(R.version) / R.get("face.cascade")


def _rect(I: np.ndarray, base: np.ndarray, stride: np.ndarray, x: int, y: int, w: int, h: int) -> np.ndarray:
    a = base + y * stride + x
    return I[a + h * stride + w] - I[a + w] - I[a + h * stride] + I[a]


def _windows(frames, win: int, scales: list[float], step: int):
    """Mọi tỉ lệ của mọi khung chung một bộ đệm tích phân phẳng: (tích phân, tích phân bình phương,
    khung, tỉ lệ, gốc, bước hàng, x, y) của từng cửa sổ."""
    bufs, sqs, cols, off = [], [], [], 0
    for fi, g in enumerate(frames):
        H0, W0 = g.shape
        for s in scales:
            w, h = int(round(W0 / s)), int(round(H0 / s))
            img = cv2.resize(g, (w, h), interpolation=cv2.INTER_LINEAR).astype(np.float64)
            ii, sq = cv2.integral(img, sdepth=cv2.CV_64F), cv2.integral(img * img, sdepth=cv2.CV_64F)
            ys, xs = np.mgrid[0:h - win:step, 0:w - win:step]
            ys, xs = ys.ravel(), xs.ravel()
            stride = ii.shape[1]
            cols.append((np.full(len(xs), fi), np.full(len(xs), s), off + ys * stride + xs,
                         np.full(len(xs), stride), xs, ys))
            bufs.append(ii.ravel())
            sqs.append(sq.ravel())
            off += ii.size
    fidx, scale, base, stride, xs, ys = (np.concatenate(c) for c in zip(*cols))
    return (np.concatenate(bufs), np.concatenate(sqs), fidx, scale, base.astype(np.int64),
            stride.astype(np.int64), xs, ys)


def detect_batch(frames, casc: Cascade, scales: list[float], step: int) -> list[np.ndarray]:
    """Hit thô [x, y, w, h] (toạ độ khung làm việc) của từng khung: mỗi weak classifier là một bước
    numpy trên mọi cửa sổ còn sống của cả lô."""
    I, Q, fidx, scale, base, stride, xs, ys = _windows(frames, casc.win, scales, step)
    inner = casc.win - 2
    vs, vq = _rect(I, base, stride, 1, 1, inner, inner), _rect(Q, base, stride, 1, 1, inner, inner)
    nf = inner * inner * vq - vs * vs
    nf = np.where(nf > 0, np.sqrt(np.maximum(nf, 0)), 1.0)
    idx = np.arange(len(base))
    for thr, weak in casc.stages:
        b, st, n = base[idx], stride[idx], nf[idx]
        total = np.zeros(len(idx))
        for fi, t, lv, rv in weak:
            val = np.zeros(len(idx))
            for x, y, w, h, wt in casc.feats[fi]:
                val += wt * _rect(I, b, st, x, y, w, h)
            total += np.where(val / n < t, lv, rv)
        idx = idx[total >= thr]
        if not len(idx):
            break
    out = [[] for _ in range(len(frames))]
    for k in idx:
        s = scale[k]
        out[int(fidx[k])].append([xs[k] * s, ys[k] * s, casc.win * s, casc.win * s])
    return [np.array(h, float).reshape(-1, 4) for h in out]


def group(hits: np.ndarray, min_hits: int, cluster_frac: float) -> np.ndarray | None:
    """Hộp mặt của một khung: trung vị các hit, giữ hit cách nó ≤ cluster_frac·w ở cả bốn cạnh,
    lấy trung bình; ít hơn min_hits hit (hoặc không hit nào gần trung vị) là hụt."""
    if len(hits) < min_hits:
        return None
    c = np.median(hits, axis=0)
    near = hits[np.all(np.abs(hits - c) <= cluster_frac * c[2], axis=1)]
    return near.mean(axis=0) if len(near) else None


def boxes(frames, R) -> list[list[float] | None]:
    """[x, y, w, h] (px khung ra 1080×1920, 2 số lẻ) hay None cho từng khung gray work_px."""
    casc = _cascade(str(cascade_path(R)))
    sc = R.get("face.scales")
    scales = [sc["start"] * sc["ratio"] ** k for k in range(sc["count"])]
    step, min_hits, frac = R.get("face.step_px"), R.get("face.min_hits"), R.get("face.cluster_frac")
    k = OUT_W / R.get("face.work_px")[0]
    out = []
    for a in range(0, len(frames), BATCH):
        for hits in detect_batch(frames[a:a + BATCH], casc, scales, step):
            b = group(hits, min_hits, frac)
            out.append(None if b is None else [round(float(k * v), 2) for v in b])
    return out


def decode(video: Path, work_px: list[int]) -> np.ndarray:
    """Mọi khung 25 fps của `video`, gray, thu về work_px bằng ffmpeg area: mảng (n, H, W) uint8."""
    W, H = work_px
    run = proc.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps={FPS},scale={W}:{H}:flags=area",
                    "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True, timeout=DECODE_TIMEOUT_S)
    n = len(run.stdout) // (W * H)
    if run.returncode or not n:
        err = run.stderr.decode("utf-8", "replace").strip()[-300:]
        raise RuntimeError(f"ffmpeg không giải mã được {Path(video).as_posix()} để track mặt: {err}")
    return np.frombuffer(run.stdout[: n * W * H], np.uint8).reshape(n, H, W)


def stats(rows: list[list], fps: float) -> dict:
    """{miss_frac, max_gap_s (chuỗi hụt liền dài nhất), h_med (trung vị chiều cao mặt, None nếu hụt hết)}."""
    hs = [r[4] for r in rows if r[1] is not None]
    longest = run = 0
    for r in rows:
        run = run + 1 if r[1] is None else 0
        longest = max(longest, run)
    return {"miss_frac": round((len(rows) - len(hs)) / len(rows), 4), "max_gap_s": round(longest / fps, 3),
            "h_med": round(float(np.median(hs)), 2) if hs else None}


def track(video: Path, R) -> dict:
    """Nội dung face.json (face/1) của `video`: một dòng [t, x, y, w, h] mỗi khung, hụt là null."""
    work_px = list(R.get("face.work_px"))
    rows = [[round(k / FPS, 2)] + (b if b is not None else [None] * 4)
            for k, b in enumerate(boxes(decode(video, work_px), R))]
    return {"schema": SCHEMA, "source_sha256": state.sha256_file(video),
            "cascade_sha256": manifest.file_sha256(cascade_path(R)), "fps": FPS, "work_px": work_px,
            "rows": rows, "stats": stats(rows, FPS)}


def dumps(doc: dict) -> str:
    """face.json dạng gọn một dòng (LF) — cùng đầu vào ⇒ cùng byte."""
    return json.dumps(doc, separators=(",", ":")) + "\n"


def intake(project: Path, R) -> dict:
    """INTAKE (§8.1): track public/master.mp4 của dự án, ghi face.json, trả nội dung của nó."""
    master = Path(project) / "public" / "master.mp4"
    if not master.is_file():
        raise RuntimeError(f"thiếu {master.as_posix()} — scaffold chưa dựng master để track mặt")
    doc = track(master, R)
    (Path(project) / FACE_JSON).write_bytes(dumps(doc).encode("utf-8"))
    return doc


def gate(doc: dict, R) -> tuple[bool, str]:
    """Cổng INTAKE "mặt": (đạt, chi tiết). Chặn khi hụt > face.max_miss_frac khung, chuỗi hụt liền >
    face.max_gap_s, hay trung vị chiều cao mặt ngoài face.height_px."""
    st, rows = doc["stats"], doc["rows"]
    max_miss, max_gap, (lo, hi) = R.get("face.max_miss_frac"), R.get("face.max_gap_s"), R.get("face.height_px")
    bad = []
    if st["miss_frac"] > max_miss:
        bad.append("hụt %.1f %% khung > %g %%" % (100 * st["miss_frac"], 100 * max_miss))
    if st["max_gap_s"] > max_gap:
        bad.append("hụt liền %.2f s > %g s" % (st["max_gap_s"], max_gap))
    if st["h_med"] is None:
        bad.append("không thấy mặt ở khung nào")
    elif not lo <= st["h_med"] <= hi:
        bad.append("mặt cao %.0f px ngoài [%g, %g]" % (st["h_med"], lo, hi))
    if bad:
        return False, "; ".join(bad) + f" — dev xem {FACE_JSON} (người dẫn mới hay khung hình khác bản đã đo?)"
    found = sum(1 for r in rows if r[1] is not None)
    return True, "%d/%d khung có mặt, hụt liền dài nhất %.2f s, mặt cao %.0f px" % (
        found, len(rows), st["max_gap_s"], st["h_med"])
