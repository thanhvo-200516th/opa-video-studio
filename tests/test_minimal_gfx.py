#!/usr/bin/env python3
"""Kiểm đồ hoạ hồ sơ minimal-edu (C1–C4): fx_gfx (nền giấy, hộp, quote card, polaroid), draw_path (nét vẽ → ProRes 4444 alpha),
MotionFX (box_wipe, polaroid_pop, relayout_blur, whip_pan, scene_camera, broll_paper, painting_scene, graph_scene)
và không hồi quy: các hàm MotionFX cũ cho cùng kết quả như bản ở HEAD.
Chạy: ~/.venvs/video-skills/bin/python tests/test_minimal_gfx.py"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
import draw_path as DP  # noqa: E402
import fx_gfx as G  # noqa: E402
import motion_fx as M  # noqa: E402
import style_profile as sp  # noqa: E402

PROF = sp.load(name="minimal-edu")
GR = PROF["graphics"]
FPS = 30
TMP = Path(tempfile.mkdtemp(prefix="minimal_gfx_"))


def rgba(p: str) -> np.ndarray:
    return np.asarray(Image.open(p).convert("RGBA"))


def hexrgb(h: str) -> np.ndarray:
    return np.array([int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)])


# ---------- C1: fx_gfx ----------
def test_paper_bg() -> None:
    for kind in ("white", "black", "blue"):
        p = G.paper_bg(TMP, f"bg_{kind}", kind, seed=3)
        im = Image.open(p)
        assert im.size == (1080, 1920), (kind, im.size)
        a = np.asarray(im.convert("RGBA"))
        assert a[..., 3].min() == 255, "nền phải đặc"
        assert a[..., :3].std() > 1.0, "phải có noise"
    white = rgba(G.paper_bg(TMP, "w", "white", seed=1))[..., :3].reshape(-1, 3).mean(0)
    assert np.abs(white - hexrgb(GR["paper_white"])).max() < 20, white
    dark = rgba(G.paper_bg(TMP, "d", "black", seed=1))[..., :3].mean()
    assert dark < 60, dark
    a1, a2 = rgba(G.paper_bg(TMP, "s1", "white", seed=1)), rgba(G.paper_bg(TMP, "s1b", "white", seed=1))
    a3 = rgba(G.paper_bg(TMP, "s2", "white", seed=2))
    assert (a1 == a2).all() and (a1 != a3).any()
    c = a1[..., :3].astype(float).mean(2)            # góc có chấm halftone → độ sáng dao động nhiều hơn giữa khung
    assert c[:200, :200].std() > c[860:1060, 440:640].std()
    try:
        G.paper_bg(TMP, "x", "green")
        raise AssertionError("kind lạ phải lỗi")
    except ValueError:
        pass


def test_box_quote_polaroid() -> None:
    a = rgba(G.box_fill(TMP, "box", 400, 120, GR["accent_line"], 30))
    assert a.shape[:2] == (120, 400) and a[0, 0, 3] == 0 and a[60, 200, 3] == 255
    assert (a[60, 200, :3] == hexrgb(GR["accent_line"])).all()
    q = rgba(G.quote_card(TMP, "quote", GR["quote_card"]["inner"], GR["quote_card"]["outer"]))
    assert q.shape[:2] == (1920, 1080) and q[..., 3].min() == 255
    ctr, cor = q[960, 540, :3].astype(int), q[5, 5, :3].astype(int)
    assert abs(ctr - hexrgb(GR["quote_card"]["inner"])).max() < 12, ctr
    assert abs(cor - hexrgb(GR["quote_card"]["outer"])).max() < 25, cor
    photo = TMP / "photo.png"
    Image.new("RGB", (600, 800), (200, 40, 40)).save(photo)
    p0, p3 = rgba(G.polaroid(TMP, "pol0", str(photo), 0)), rgba(G.polaroid(TMP, "pol3", str(photo), 3))
    h, w = p0.shape[:2]
    assert p0[0, 0, 3] == 0 and p0[h // 2, w // 2, 3] == 255, "góc trong suốt, giữa đặc"
    assert ((p0[..., 3] > 0) & (p0[..., 3] < 255)).sum() > 500, "phải có bóng mờ"
    assert p3.shape != p0.shape, "nghiêng đổi khung"


def test_graph_grid() -> None:
    a = rgba(G.graph_grid(TMP, "grid"))
    assert a.shape[:2] == (1920, 1080) and a[..., 3].max() > 150 and (a[..., 3] == 0).mean() > 0.3


# ---------- C2: draw_path ----------
def alpha_sums(spec: dict) -> list[int]:
    return [int((f[..., 3] > 0).sum()) for f in DP.render_frames(**spec)]


def check_progress(spec: dict, n: int) -> list[int]:
    s = alpha_sums(spec)
    assert len(s) == n, (len(s), n)
    assert s[0] == 0, "khung 0 phải trống"
    assert s[-1] > 0 and all(b >= a for a, b in zip(s, s[1:])), s
    return s


def test_presets() -> None:
    sp_spec = DP.spiral()
    assert sp_spec["frames"] == GR["spiral"]["frames"] == 23
    s = check_progress(sp_spec, 23)
    assert s[len(s) // 2] > s[len(s) // 4] > 0
    ar = DP.arrow_curve()
    assert ar["frames"] in GR["arrow_frames"]
    sa = check_progress(ar, ar["frames"])
    assert sa[-1] > sa[-2], "đầu mũi tên hiện ở khung cuối"
    ln = DP.line([(100, 960), (980, 960)])
    assert ln["frames"] == GR["line_draw_frames"]
    check_progress(ln, 9)
    last = list(DP.render_frames(**ln))[-1]
    thick = int((last[:, 540, 3] > 128).sum())
    want = GR["line_width_ratio"] * 1080
    assert abs(thick - want) <= 3, (thick, want)
    assert tuple(last[960, 540, :3]) == tuple(hexrgb(GR["accent_line"])), last[960, 540]
    check_progress(DP.zigzag((100, 700), (980, 1100)), DP.zigzag((100, 700), (980, 1100))["frames"])
    gc = DP.graph_curve([(100, 1500), (400, 1200), (700, 1000), (980, 500)])
    check_progress(gc, gc["frames"])
    fr = list(DP.render_frames(**gc))
    assert (fr[-1][..., 3] > 0).sum() >= (fr[-2][..., 3] > 0).sum() - 2000   # chấm theo đầu nét
    # đường vẽ xong đúng khung cuối (full), khung kế cuối chưa đủ
    a = alpha_sums(ln)[-2:]
    assert a[0] < a[1]


def ffprobe(path: Path, entry: str, extra: list[str] | None = None) -> str:
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", *(extra or []), "-show_entries", f"stream={entry}",
           "-of", "default=nw=1:nk=1", str(path)]
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip()


def assert_prores_alpha(path: Path) -> None:
    """Ghi bằng `-pix_fmt yuva444p10le`; ffprobe (ffmpeg 8.x) đọc lại ProRes 4444 là yuva444p12le — giống mọi .mov của matte.py."""
    assert ffprobe(path, "codec_name") == "prores" and ffprobe(path, "codec_tag_string") == "ap4h"
    assert ffprobe(path, "pix_fmt") in ("yuva444p10le", "yuva444p12le"), "phải có kênh alpha 4:4:4"


def test_mov() -> None:
    out = TMP / "arrow.mov"
    DP.write(DP.arrow_curve(), out, fps=FPS)
    assert_prores_alpha(out)
    n = DP.arrow_curve()["frames"]
    assert int(ffprobe(out, "nb_read_frames", ["-count_frames"])) == n
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(out), "-pix_fmt", "rgba", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(n, 1920, 1080, 4)
    assert frames[0, ..., 3].max() == 0 and frames[-1, ..., 3].max() > 200
    cli = TMP / "cli.mov"                                  # CLI cùng đường chạy
    subprocess.run([sys.executable, str(SCRIPTS / "draw_path.py"), "line", "--points", "100,960 980,960",
                    "--out", str(cli), "--fps", str(FPS)], check=True, capture_output=True)
    assert int(ffprobe(cli, "nb_read_frames", ["-count_frames"])) == GR["line_draw_frames"]


# ---------- C3: MotionFX ----------
def new_fx() -> M.MotionFX:
    return M.MotionFX(TMP, fps=FPS, name="t")


def key_lists(obj) -> list[list]:
    found = []
    if isinstance(obj, dict):
        for v in obj.values():
            found += key_lists(v)
    elif isinstance(obj, list):
        if obj and all(isinstance(k, list) and len(k) >= 2 and isinstance(k[0], (int, float)) for k in obj):
            found.append(obj)
        for v in obj:
            found += key_lists(v)
    return found


def assert_valid_keys(c: dict) -> None:
    ks = key_lists({k: v for k, v in c.items() if k in ("motion", "opacity", "effects")})
    assert ks, "không có keyframe"
    for keys in ks:
        ts = [k[0] for k in keys]
        assert ts == sorted(ts) and len(set(ts)) == len(ts), ("không tăng chặt", keys)
        assert all(abs(t * FPS - round(t * FPS)) < 0.02 for t in ts), ("lệch lưới khung", keys)
        assert all(t <= c["dur"] + 1e-6 for t in ts), ("quá clip", keys, c["dur"])


def eff(c: dict, name: str) -> dict:
    return next(e["params"] for e in c["effects"] if e["effect"] == name)


def png(name: str, size=(1080, 1920)) -> str:
    p = TMP / f"{name}.png"
    Image.new("RGBA", size, (10, 100, 222, 255)).save(p)
    return str(p)


def test_box_wipe() -> None:
    fx = new_fx()
    c = fx.image(png("box"), 1.0, 2.0)
    assert fx.box_wipe(c) is c
    keys = eff(c, "crop")["right"]
    assert keys[0][1] == 100 and keys[-1][1] == 0
    assert abs(keys[-1][0] - GR["box_wipe_frames"] / FPS) < 1e-3
    assert_valid_keys(c)
    c2 = fx.box_wipe(fx.image(png("box2"), 0, 1), frames=4)
    assert abs(eff(c2, "crop")["right"][-1][0] - 4 / FPS) < 1e-3


def test_polaroid_pop() -> None:
    fx = new_fx()
    c = fx.polaroid_pop(fx.image(png("pol"), 2.0, 1.5), tilt=2.5)
    assert_valid_keys(c)
    assert c["opacity"][0][1] == 0 and c["opacity"][1][1] == 100 and abs(c["opacity"][1][0] - 1 / FPS) < 1e-3, "hiện trong 1 khung"
    sc = c["motion"]["scale"]
    assert abs(sc[0][1] - 100 * GR["polaroid"]["scale_from"]) < 0.01 and sc[-1][1] == 100
    assert GR["polaroid"]["settle_frames"][0] <= round(sc[-1][0] * FPS) <= GR["polaroid"]["settle_frames"][1]
    rot = c["motion"]["rotation"]
    assert abs(rot[-1][1]) == 2.5 and rot[-1][1] == 2.5


def test_relayout_blur() -> None:
    fx = new_fx()
    a, b = fx.image(png("a"), 0, 1), fx.image(png("b"), 0, 1)
    out = fx.relayout_blur([a, b])
    assert out == [a, b]
    for c in (a, b):
        assert_valid_keys(c)
        bl = eff(c, "gaussian_blur")["blurriness"]
        assert bl[0][1] > 0 and bl[-1][1] == 0 and abs(bl[-1][0] - GR["relayout_blur_frames"] / FPS) < 1e-3


def test_whip_pan() -> None:
    fx = new_fx()
    a, b = fx.image(png("wa"), 1.0, 2.0), fx.image(png("wb"), 1.0, 2.0)
    fx.whip_pan([a, b], "up", frames=8)
    for c in (a, b):
        assert_valid_keys(c)
        pos = c["motion"]["position"]
        assert pos[0][1] == [540, 960] and pos[-1][1][0] == 540 and pos[-1][1][1] < 960
        assert round((pos[-1][0] - pos[0][0]) * FPS) == 8
        ln = eff(c, "directional_blur")["length"]
        assert eff(c, "directional_blur")["direction"] == 0, "pan dọc → nhoè dọc"
        peak = max(k[1] for k in ln)
        assert ln[0][1] == 0 and ln[-1][1] == 0 and peak > 0
        assert any(k[1] == peak and 0 < k[0] - pos[0][0] < pos[-1][0] - pos[0][0] for k in ln), "đỉnh nhoè giữa chừng"
    assert a["motion"] == b["motion"]
    try:
        fx.whip_pan([a], "sideways")
        raise AssertionError("hướng lạ phải lỗi")
    except ValueError:
        pass
    h = fx.whip_pan([fx.image(png("wh"), 0, 1)], "left", frames=7)[0]
    assert eff(h, "directional_blur")["direction"] == 90 and h["motion"]["position"][-1][1][0] < 540


def test_scene_camera() -> None:
    fx = new_fx()
    a, b = fx.image(png("ca"), 1.0, 3.0), fx.image(png("cb"), 1.5, 2.5)
    keys = [[1.5, (540, 960), 100], [2.5, (400, 800), 120, "easeIn"], [3.5, (300, 700), 140]]
    fx.scene_camera([a, b], keys)
    for c in (a, b):
        assert_valid_keys(c)
    pa, pb = a["motion"]["position"], b["motion"]["position"]
    assert [k[1] for k in pb] == [[540, 960], [400, 800], [300, 700]]
    assert [round(k[0] * FPS) for k in pb] == [0, 30, 60] and [round(k[0] * FPS) for k in pa] == [15, 45, 75]
    assert a["motion"]["scale"][-1][1] == 140
    c1 = fx.image(png("own"), 0, 2)
    fx.slide_up(c1) if hasattr(fx, "slide_up") else None
    c1["motion"] = {"position": [[0, [540, 900]], [0.5, [540, 960]]]}
    c2 = fx.image(png("own2"), 0, 2)
    try:
        fx.scene_camera([c2, c1], [[0, (540, 960), 100], [1, (500, 900), 110]])
        raise AssertionError("xung đột phải lỗi")
    except ValueError:
        pass
    assert "motion" not in c2, "không sửa dở dang khi lỗi"


def test_broll_paper() -> None:
    fx = new_fx()
    v = fx.image(str(TMP / "clip.mp4"), 2.0, 3.0, lane="gfx_under")
    fx.broll_paper(v)
    names = [e["effect"] for e in v["effects"]]
    assert "vignette" in names and "focus_blur" in names
    papers = [c for ln, c in fx.items if c is not v and c.get("blend") == "multiply"]
    assert len(papers) == 1 and papers[0]["at"] == v["at"] and papers[0]["dur"] == v["dur"]
    assert 20 <= papers[0]["opacity"] <= 45
    assert Image.open(papers[0]["src"]).size == (1080, 1920)


def test_painting_scene() -> None:
    fx = new_fx()
    src = TMP / "paint.png"
    Image.fromarray((np.random.RandomState(0).rand(300, 200, 3) * 255).astype(np.uint8)).save(src)
    try:
        fx.painting_scene(str(src), 1.0, 2.0, texture_strength=0.8)
        raise AssertionError("texture > 0.5 phải lỗi")
    except ValueError:
        pass
    c = fx.painting_scene(str(src), 1.0, 2.0, texture_strength=0.4)
    assert c["src"] != str(src) and Path(c["src"]).exists(), "texture phải được bake vào PNG mới"
    assert Image.open(c["src"]).size == Image.open(src).size
    assert_valid_keys(c)
    d = eff(c, "directional_blur")
    assert d["direction"] == 90
    n = round(d["length"][-1][0] * FPS)
    assert PROF["cuts"]["painting_entry"]["frames"][0] <= n <= PROF["cuts"]["painting_entry"]["frames"][1]
    assert d["length"][0][1] > 0 and d["length"][-1][1] == 0


def test_graph_scene() -> None:
    fx = new_fx()
    words = [2.0, 2.4, 2.9, 3.3]
    cues = fx.graph_scene(words, at=1.5, dur=3.5)
    assert [c["kind"] for c in cues] == ["highlighter"] * 4
    assert [c["t"] for c in cues] == words
    assert all(c in fx.cues for c in cues)
    lanes = {}
    for ln, c in fx.items:
        lanes.setdefault(ln, []).append(c)
        assert_valid_keys(c) if (c.get("effects") or c.get("opacity")) else None
    steps = [c for ln, cs in lanes.items() for c in cs if c["name"].startswith("Bậc")]
    assert len(steps) == 4
    assert [round((c["at"] - 1.5) * FPS) for c in steps] == [round((w - 1.5) * FPS) for w in words]
    axis = [c for cs in lanes.values() for c in cs if c["name"].startswith("Trục L")]
    mov = [c for c in axis if str(c["src"]).endswith(".mov")]
    assert len(mov) == 1 and round(mov[0]["dur"] * FPS) == GR["graph_axis_frames"]
    assert_prores_alpha(Path(mov[0]["src"]))
    assert int(ffprobe(Path(mov[0]["src"]), "nb_read_frames", ["-count_frames"])) == GR["graph_axis_frames"]
    for c in axis:
        assert c["at"] + c["dur"] <= 1.5 + 3.5 + 1e-6


# ---------- không hồi quy ----------
BASELINE = "8e971da"   # opa-video-studio 3.5.1 — bản trước khi thêm hồ sơ minimal-edu


def head_module():
    src = subprocess.run(["git", "show", f"{BASELINE}:scripts/motion_fx.py"], cwd=ROOT, capture_output=True, text=True)
    if src.returncode != 0:
        return None
    p = TMP / "motion_fx_head.py"
    p.write_text(src.stdout, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("motion_fx_head", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def scripted(mod) -> str:
    fx = mod.MotionFX(TMP, fps=FPS, name="reg")
    a = fx.text("Xin chào mọi người", 1.0, 2.0, "sans", 120)
    fx.type_in(a)
    fx.type_out(a)
    fx.wipe_in(fx.text("Quét lộ", 4.0, 1.5, "sans", 100))
    fx.slide_up(fx.text("Trượt", 6.0, 1.5, "sans", 100))
    fx.pop_in(fx.text("Nảy", 8.0, 1.0, "sans", 100))
    fx.asset_3d(png("reg3d"), 9.0, 1.5, anim="pop")
    fx.join(fx.image(png("regj"), 10.0, 1.0), "zoom")
    fx.zoom_through(12.0, fx.image(png("regz1"), 11.0, 1.0), fx.image(png("regz2"), 12.0, 1.0))
    return json.dumps({"tracks": fx.tracks(), "cues": fx.cues}, ensure_ascii=False, sort_keys=True)


def test_no_regression() -> None:
    old = head_module()
    if old is None:   # bản cài (không có .git): phép so chỉ chạy trong repo
        print(f"bỏ qua không-hồi-quy: không có git / commit {BASELINE}")
        return
    assert scripted(old) == scripted(M), "hàm MotionFX cũ đổi kết quả"


if __name__ == "__main__":
    names = [n for n in sorted(globals()) if n.startswith("test_")]
    for n in names:
        globals()[n]()
        print("ok", n)
    print("TẤT CẢ ĐẠT")
