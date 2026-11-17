#!/usr/bin/env python3
"""Kiểm đồ thị chuyển động liền mạch (brief G): rounded_path / progress_curve / graph_track (draw_path) và
MotionFX.graph_scene = MỘT nét .mov do bóng sáng vẽ + camera bám bóng (không còn bậc lộ bằng crop).
Chạy: ~/.venvs/video-skills/bin/python tests/test_graph_motion.py"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import draw_path as DP  # noqa: E402
import motion_fx as M  # noqa: E402

FPS = 30
TMP = Path(tempfile.mkdtemp(prefix="graph_motion_"))
WORDS, AT, DUR = [2.0, 2.4, 2.9, 3.3], 1.5, 3.5


def test_rounded_path() -> None:
    pts, marks = DP.rounded_path([(0, 0), (100, 0), (100, -100), (200, -100)], 30)
    assert marks[0] == 0 and abs(marks[-1] - 1) < 1e-6 and marks == sorted(marks) and len(marks) == 4
    assert np.abs(pts - np.array([100, 0])).sum(1).min() > 5, "góc đã bo, không đi qua đỉnh"


def test_progress_curve() -> None:
    times, arcs = [1.0, 1.5, 2.1, 2.6], [0.0, 0.3, 0.7, 1.0]
    t = np.arange(0.5, 3.0, 1 / FPS)
    p = DP.progress_curve(times, arcs, t)
    assert (np.diff(p) >= -1e-12).all() and p[0] == 0 and p[-1] == 1
    for ti, ai in zip(times, arcs):
        assert abs(DP.progress_curve(times, arcs, [ti])[0] - ai) < 1e-9
    act = np.diff(p[(t >= 1.0) & (t <= 2.6)])
    assert act.min() > 0.15 * act.mean(), "không có khung đứng yên giữa các mốc"
    for bad in (([1, 1], [0, 1]), ([1, 2], [1, 0])):
        try:
            DP.progress_curve(*bad, [1.5])
            raise AssertionError("mốc sai phải lỗi")
        except ValueError:
            pass


def stair_track(words=WORDS, at=AT, end=AT + DUR):
    """Chạy graph_scene thật để lấy clip đường đồ thị (thời điểm bắt đầu)."""
    fx = M.MotionFX(TMP, fps=FPS, name="tp")
    fx.graph_scene(words, at, end - at)
    return fx


def test_head_displacement_smooth() -> None:
    fx = stair_track()
    c = next(c for _, c in fx.items if c["name"].startswith("Đường đồ thị"))
    geom = (*M.GRAPH_GEOM["origin"], *M.GRAPH_GEOM["size"])
    pts, marks = DP.rounded_path(M._stair_points(geom, 4), M.GRAPH_ROUND * min(geom[2], geom[3] * 0.85) / 4)
    t_s = c["at"]
    t = np.array([t_s + f / FPS for f in range(round(c["dur"] * FPS))])
    gap = (WORDS[-1] - WORDS[0]) / 3
    t_end = max(WORDS[-1] + 2 / FPS, min(WORDS[-1] + gap, AT + DUR - 2 / FPS))
    prog = DP.progress_curve([*WORDS, t_end], [marks[2 * i] for i in range(4)] + [1.0], t)
    head = DP.path_points(pts, prog)
    moving = (t >= WORDS[0]) & (t <= t_end)
    disp = np.hypot(*np.diff(head[moving], axis=0).T)
    med = np.median(disp)
    assert disp.max() <= 3 * med, (disp.max(), med)
    assert disp.min() >= 0.15 * med, (disp.min(), med)
    assert (np.diff(prog) >= 0).all()
    for w, i in zip(WORDS, range(4)):                         # tới chân bậc i đúng từ i
        k = int(round((w - t_s) * FPS))
        assert abs(prog[k] - marks[2 * i]) < 0.02, (w, prog[k], marks[2 * i])


def ffprobe(path: str, entry: str, extra: list[str] | None = None) -> str:
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", *(extra or []), "-show_entries", f"stream={entry}",
           "-of", "default=nw=1:nk=1", path]
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip()


def test_graph_scene_single_curve() -> None:
    fx = M.MotionFX(TMP, fps=FPS, name="gs")
    cues = fx.graph_scene(WORDS, at=AT, dur=DUR)
    assert [c["t"] for c in cues] == WORDS and all(c["kind"] == "highlighter" for c in cues)
    clips = [c for _, c in fx.items]
    assert not [c for c in clips if c["name"].startswith("Bậc")], "không còn bậc rời"
    curve = [c for c in clips if c["name"].startswith("Đường đồ thị")]
    assert len(curve) == 1 and curve[0]["src"].endswith(".mov")
    assert curve[0]["at"] + curve[0]["dur"] <= AT + DUR + 1e-6 and curve[0]["at"] <= WORDS[0]
    n = round(curve[0]["dur"] * FPS)
    assert ffprobe(curve[0]["src"], "codec_tag_string") == "ap4h"
    assert int(ffprobe(curve[0]["src"], "nb_read_frames", ["-count_frames"])) == n
    cam = [c for c in clips if c["name"].startswith(("Lưới đồ thị", "Trục L")) or c in curve]
    assert len(cam) == 4
    for c in cam:
        sc, pos = c["motion"]["scale"], c["motion"]["position"]
        ts = [k[0] for k in pos]
        assert ts == sorted(ts) and len(set(ts)) == len(ts) and ts[-1] <= c["dur"] + 1e-6
        assert all(abs(t * FPS - round(t * FPS)) < 0.02 for t in ts)
        assert 100 <= min(k[1] for k in sc) and max(k[1] for k in sc) <= M.GRAPH_ZOOM + 1e-6
        assert all(b[1] >= a[1] for a, b in zip(sc, sc[1:])), "scale tăng đều"
        for t, (x, y), s in [(k[0], k[1], sc[min(i, len(sc) - 1)][1]) for i, k in enumerate(pos)]:
            assert abs(x - 540) <= (s / 100 - 1) * 540 and abs(y - 960) <= (s / 100 - 1) * 960, "không lộ mép lớp"
    bg = next(c for c in clips if c["name"].startswith("Nền đồ thị"))
    assert "motion" not in bg


def test_rendered_ball() -> None:
    """Khung thật: bóng trắng tại đầu nét, quầng xanh; khung đầu đã có bóng ở gốc, chưa có nét."""
    pts, marks = DP.rounded_path([(150, 1550), (500, 1550), (500, 1200)], 40)
    prog = np.concatenate([np.zeros(3), np.linspace(0, 1, 12)])
    fr = list(DP.render_frames(**DP.graph_track(pts, prog)))
    f0, fl = fr[0], fr[-1]
    assert f0[1550, 150, 3] > 200 and tuple(f0[1550, 150, :3]) == (255, 255, 255)
    assert f0[1550, 400, 3] == 0, "chưa có nét"
    assert tuple(fl[1200, 500, :3]) == (255, 255, 255)
    blue = fl[1550, 320]
    assert blue[3] == 255 and blue[2] > blue[0], "nét xanh"
    assert fl[1200, 500 + 110, 3] > 20, "quầng sáng quanh bóng"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
