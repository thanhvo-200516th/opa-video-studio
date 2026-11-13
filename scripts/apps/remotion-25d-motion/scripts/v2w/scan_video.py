#!/usr/bin/env python3
"""Quét MP4 cho tools/v2w/metrics.py: giải mã xám 960×540 qua pipe ffmpeg, đổi điểm ảnh so với f − 1 và f − lag,
độ dời mỗi frame bằng bám điểm góc (OpenCV goodFeaturesToTrack + Lucas–Kanade tháp, kiểm xuôi–ngược < 1 px).

Vì sao không Farneback (NN §8.7 đề xuất): trên đồ họa phẳng + chữ, Farneback cho ngoại lai ~300 px/frame ở chỗ thật
chỉ ~20 px; LK có kiểm xuôi–ngược đo whip 181,5 px/f60 so với camera thật 186 (đo trên test 1, 07/10/2026).
Không ngưỡng, không báo cáo (xem metrics_core.py).
"""
from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

try:
    import cv2  # type: ignore
except ImportError:  # OpenCV không bắt buộc: thiếu thì bỏ độ dời và ghi WARN
    cv2 = None

PROC_W, PROC_H = 960, 540
DIFF_LEVEL = 6
FB_MAX_PX = 1.0  # sai số xuôi–ngược tối đa (px khung xử lý)
LK = {"winSize": (21, 21), "maxLevel": 5, "criteria": (3, 30, 0.01)}  # 3 = EPS | COUNT
FEATURES = {"maxCorners": 600, "qualityLevel": 0.01, "minDistance": 8, "blockSize": 7}


class InputError(Exception):
    """Lỗi đầu vào → exit 2."""


def _exe(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise InputError(f"không thấy {name} trên PATH")
    return path


def probe(video: Path) -> dict:
    """width, height, fps (số thực) của luồng hình đầu tiên."""
    r = subprocess.run([_exe("ffprobe"), "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,r_frame_rate", "-of", "json", str(video)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise InputError(f"ffprobe lỗi: {r.stderr.strip()[-400:]}")
    s = json.loads(r.stdout)["streams"][0]
    num, den = (int(x) for x in s["r_frame_rate"].split("/"))
    return {"width": int(s["width"]), "height": int(s["height"]), "fps": num / den}


def frames_gray(video: Path):
    """Sinh từng frame xám PROC_W×PROC_H (uint8) qua pipe ffmpeg."""
    cmd = [_exe("ffmpeg"), "-v", "error", "-i", str(video), "-vf", f"scale={PROC_W}:{PROC_H}:flags=area,format=gray",
           "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    size = PROC_W * PROC_H
    assert proc.stdout is not None
    while True:
        buf = proc.stdout.read(size)
        if len(buf) < size:
            break
        yield np.frombuffer(buf, dtype=np.uint8).reshape(PROC_H, PROC_W)
    proc.stdout.close()
    err = ""
    if proc.stderr:
        err = proc.stderr.read().decode("utf-8", "replace")
        proc.stderr.close()
    if proc.wait() != 0:
        raise InputError(f"ffmpeg giải mã lỗi: {err.strip()[-400:]}")


def changed_share(a: np.ndarray, b: np.ndarray) -> float:
    return float((np.abs(a.astype(np.int16) - b.astype(np.int16)) > DIFF_LEVEL).mean())


def displacement(prev: np.ndarray, cur: np.ndarray) -> np.ndarray:
    """Độ dời (px khung xử lý) của các điểm góc bám được và qua kiểm xuôi–ngược."""
    pts = cv2.goodFeaturesToTrack(prev, **FEATURES)
    if pts is None:
        return np.zeros(0)
    nxt, st, _ = cv2.calcOpticalFlowPyrLK(prev, cur, pts, None, **LK)
    back, st2, _ = cv2.calcOpticalFlowPyrLK(cur, prev, nxt, None, **LK)
    fb = np.hypot(*(back - pts).reshape(-1, 2).T)
    ok = (st.ravel() == 1) & (st2.ravel() == 1) & (fb < FB_MAX_PX)
    return np.hypot(*(nxt - pts).reshape(-1, 2)[ok].T)


@dataclass
class FrameStat:
    ch1: float = 0.0  # tỉ lệ điểm đổi so với f − 1
    ch_lag: float | None = None  # so với f − lag (None: chưa đủ frame)
    disp50: float = 0.0  # px khung GỐC mỗi frame: trung vị, phân vị 95, lớn nhất của điểm bám được
    disp95: float = 0.0
    disp_max: float = 0.0
    tracks: int = 0


@dataclass
class Scan:
    fps: float
    width: int
    height: int
    stats: list[FrameStat] = field(default_factory=list)
    warns: list[str] = field(default_factory=list)


def scan(video: Path, flow: bool = True) -> Scan:
    info = probe(video)
    fps = info["fps"]
    lag = max(1, round(fps / 30))
    out = Scan(fps=fps, width=info["width"], height=info["height"])
    use_flow = flow and cv2 is not None
    if flow and cv2 is None:
        out.warns.append("WARN: không có OpenCV, bỏ đo độ dời")
    to_src = info["width"] / PROC_W
    hist: list[np.ndarray] = []
    for g in frames_gray(video):
        st = FrameStat()
        if hist:
            st.ch1 = changed_share(g, hist[-1])
        if len(hist) >= lag:
            st.ch_lag = changed_share(g, hist[-lag])
        if use_flow and hist and st.ch1 > 0:
            d = displacement(hist[-1], g) * to_src
            if d.size:
                st.disp50, st.disp95, st.disp_max = float(np.median(d)), float(np.percentile(d, 95)), float(d.max())
                st.tracks = int(d.size)
        hist = (hist + [g])[-lag:]
        out.stats.append(st)
    if len(out.stats) < 3:
        raise InputError(f"video quá ngắn ({len(out.stats)} frame)")
    return out
