#!/usr/bin/env python3
"""Dựng một test 16:9 trọn gói (NN §8.5): cửa sổ → render câm → cắt âm + mux → ffprobe → contact → still → chỉ số
→ palette_w trên contact. Đích `lab` (NN §8.8): composition v2w-lab, không âm, thêm kiểm dấu L8b ở 112 px.

Chạy:  python tools/v2w/build_test.py <1|2|3|4|lab> [--skip-render] [--no-flow]   (phim đủ 30 s: build_film.py)
Đầu ra test: out/v2-16x9/tests/test-N-muted.mp4, test-N.wav, test-N.mp4, test-N_contact.png, stills/test-N_t<giây>.png,
        test-N_metrics.json/.md.
Đầu ra lab:  out/v2-16x9/lab/lab-muted.mp4, lab_contact.png, stills/lab_t<giây>.png, lab_metrics.json/.md,
        stills/lab_L8b_mask_f<f>.png + lab_L8b_nomask_f<f>.png (mỗi chữ cái của bản mask phải giữ hàng mực trên/dưới
        và lượng mực như bản không mask: dấu không bị cắt).
Remotion chỉ chạy qua tools/remotion_run.py (có khóa). Không shell, không "|".
Exit:  0 mọi bước đạt; 1 chỉ số / palette / ffprobe / mux / dấu L8b trượt; 2 thiếu file / bước lỗi.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics  # noqa: E402
import palette_w  # noqa: E402
from contact import sheet  # noqa: E402
from mux_test import MASTER, InputError, MuxError, cut_audio, mux  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "out/v2-16x9/tests"
OUT_LAB = ROOT / "out/v2-16x9/lab"
TSX = ROOT / "node_modules/tsx/dist/cli.mjs"
INK_TOL = 0.02  # lượng mực mỗi chữ cái được lệch giữa bản mask và bản không mask


def step(name: str) -> None:
    print(f"[build_test] {name}", flush=True)


def call(cmd: list[str], what: str) -> None:
    if subprocess.run(cmd, cwd=ROOT).returncode != 0:
        raise InputError(f"{what} lỗi")


def tests_json() -> dict:
    """Chạy scripts/v2w-tests.ts (4 test + lab + phim đủ) rồi đọc OUT/tests.json."""
    node = shutil.which("node")
    if not node or not TSX.is_file():
        raise InputError("thiếu node hoặc node_modules/tsx")
    path = OUT / "tests.json"
    call([node, str(TSX), "scripts/v2w-tests.ts", str(path)], "scripts/v2w-tests.ts")
    return json.loads(path.read_text(encoding="utf-8"))


def window(target: str) -> dict:
    """Cửa sổ test N (hoặc lab) từ scripts/v2w-tests.ts."""
    data = tests_json()
    if target == "lab":
        if "lab" not in data:
            raise InputError("tests.json không có mục lab")
        return data["lab"]
    found = [t for t in data["tests"] if str(t["n"]) == target]
    if not found:
        raise InputError(f"không có test {target}")
    return found[0]


def check_probe(mp4: Path, frames: int) -> list[str]:
    r = subprocess.run([shutil.which("ffprobe") or "ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                        "-show_entries", "stream=codec_name,width,height,r_frame_rate,nb_read_frames", "-of", "json", str(mp4)],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        return [f"ffprobe lỗi: {r.stderr.strip()[-300:]}"]
    s = json.loads(r.stdout)["streams"][0]
    want = {"codec_name": "h264", "width": 1920, "height": 1080, "r_frame_rate": "60/1", "nb_read_frames": str(frames)}
    return [f"{k} = {s.get(k)} (cần {v})" for k, v in want.items() if str(s.get(k)) != str(v)]


def stills(mp4: Path, t: dict, out: Path, name: str) -> list[Path]:
    paths = []
    for s in t["keyStills"]:
        idx = round((s - t["from"]) * t["fps"])
        dst = out / "stills" / f"{name}_t{s:.3f}.png"
        dst.parent.mkdir(parents=True, exist_ok=True)
        call([shutil.which("ffmpeg") or "ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-vf", f"select=eq(n\\,{idx})",
              "-fps_mode", "passthrough", "-frames:v", "1", str(dst)], f"cắt still {s}")
        paths.append(dst)
    return paths


def palette_step(png: Path) -> list[str]:
    """NN §8.5 bước 8: palette_w trên ảnh contact."""
    r = palette_w.check_file(png)
    print(palette_w.summary(r))
    return [f"palette_w: {x}" for x in r["reasons"]]


def glyph_runs(rgb: np.ndarray) -> list[tuple[int, int, int]]:
    """Mực đen (mọi kênh < 128; chữ xanh, Bò, nền nhạt không tính) tách theo cụm cột (khe > 2 px) = từng chữ cái kèm dấu.
    Trả (hàng mực trên cùng, hàng dưới cùng, số điểm mực) mỗi cụm."""
    ink = rgb.max(axis=-1) < 128
    cols = np.nonzero(ink.any(axis=0))[0]
    if len(cols) == 0:
        return []
    out = []
    for run in np.split(cols, np.nonzero(np.diff(cols) > 2)[0] + 1):
        sub = ink[:, run[0]:run[-1] + 1]
        rows = np.nonzero(sub.any(axis=1))[0]
        out.append((int(rows[0]), int(rows[-1]), int(sub.sum())))
    return out


def l8b_check(t: dict) -> list[str]:
    """Still L8b (112 px) render 2 lần qua Remotion: dòng chữ mẫu Ầ Ổ Ữ ặ đ có mask và không mask.
    Dấu không bị cắt ⇔ mỗi chữ cái giữ nguyên hàng mực trên/dưới (±1 px) và lượng mực (±2 %). Không so điểm ảnh thô:
    bản mask tách từ thành inline-block nên lệch ngang dưới 1 px so với bản một dòng chữ liền."""
    frame = round(t["l8bStill"] * t["fps"])
    runs = []
    for no_mask in (False, True):
        dst = OUT_LAB / "stills" / f"lab_L8b_{'nomask' if no_mask else 'mask'}_f{frame}.png"
        dst.parent.mkdir(parents=True, exist_ok=True)
        props = json.dumps({"blur": True, "noMask": no_mask}, separators=(",", ":"))
        call([sys.executable, "tools/remotion_run.py", "still", t["id"], str(dst), f"--frame={frame}", f"--props={props}"],
             "still L8b")
        runs.append(glyph_runs(palette_w.load_rgb(dst)))
    masked, plain = runs
    print(f"  L8b f{frame}: chữ cái (trên, dưới, mực) có mask {masked}")
    print(f"  L8b f{frame}: chữ cái (trên, dưới, mực) không mask {plain}")
    if len(masked) != len(plain) or not plain:
        return [f"L8b: số chữ cái khác nhau ({len(masked)} có mask, {len(plain)} không mask)"]
    bad = [i for i, (m, p) in enumerate(zip(masked, plain))
           if abs(m[0] - p[0]) > 1 or abs(m[1] - p[1]) > 1 or abs(m[2] - p[2]) > INK_TOL * p[2]]
    return [f"L8b: chữ cái thứ {i + 1} khác bản không mask (dấu có thể bị cắt)" for i in bad]


def render(t: dict, muted: Path) -> None:
    step(f"render câm {t['id']} ({t['frames']} frame)")
    call([sys.executable, "tools/remotion_run.py", "render", t["id"], str(muted), "--muted", "--codec=h264",
          "--jpeg-quality=95", "--crf=16"], "render")


def finish(name: str, r: dict, bad: list[str]) -> int:
    print(metrics.summary(r))
    for b in bad:
        print(f"  TRƯỢT {b}")
    print(f"[build_test] {name}: {'ĐẠT' if r['pass'] and not bad else 'TRƯỢT'}")
    return 0 if r["pass"] and not bad else 1


def build_test(t: dict, skip_render: bool, flow: bool) -> int:
    n = t["n"]
    muted, wav, final = OUT / f"test-{n}-muted.mp4", OUT / f"test-{n}.wav", OUT / f"test-{n}.mp4"
    if not skip_render:
        render(t, muted)
    if not muted.is_file():
        raise InputError(f"thiếu {muted}")
    step(f"cắt âm [{t['from']}; {t['to']}) s + mux")
    cut_audio(MASTER, t["from"], t["to"], wav)
    res = mux(muted, wav, final)
    step(f"ffprobe (lệch âm/hình {res['delta'] * 1000:.2f} ms)")
    bad = check_probe(final, t["frames"])
    step("contact sheet")
    contact = sheet(final, t["from"], 0.5, 4, OUT / f"test-{n}_contact.png")
    step("still khóa")
    stills(final, t, OUT, f"test-{n}")
    step("chỉ số")
    r = metrics.run(final, t["from"], [(d["from"], d["to"]) for d in t["declared"]], f"test-{n}", flow,
                    OUT / f"test-{n}_metrics.json", OUT / f"test-{n}_metrics.md")
    step("palette_w trên contact")
    bad += palette_step(contact)
    return finish(f"test-{n}", r, bad)


def build_lab(t: dict, skip_render: bool, flow: bool) -> int:
    final = OUT_LAB / "lab-muted.mp4"  # lab không có âm
    if not skip_render:
        render(t, final)
    if not final.is_file():
        raise InputError(f"thiếu {final}")
    step("ffprobe")
    bad = check_probe(final, t["frames"])
    step("contact sheet (mỗi 0,25 s)")
    contact = sheet(final, t["from"], 0.25, 4, OUT_LAB / "lab_contact.png")
    step("still khóa")
    stills(final, t, OUT_LAB, "lab")
    step("chỉ số")
    r = metrics.run(final, t["from"], [(d["from"], d["to"]) for d in t["declared"]], "v2w-lab", flow,
                    OUT_LAB / "lab_metrics.json", OUT_LAB / "lab_metrics.md")
    step("palette_w trên contact")
    bad += palette_step(contact)
    step("dấu L8b ở 112 px: mask so với không mask")
    bad += l8b_check(t)
    return finish("v2w-lab", r, bad)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Dựng test 16:9 trọn gói (hoặc lab của NỀN)")
    ap.add_argument("target", choices=["1", "2", "3", "4", "lab"])
    ap.add_argument("--skip-render", action="store_true", help="dùng lại MP4 câm đã có")
    ap.add_argument("--no-flow", action="store_true")
    a = ap.parse_args()
    try:
        step(f"cửa sổ {a.target}")
        t = window(a.target)
        build = build_lab if a.target == "lab" else build_test
        return build(t, a.skip_render, not a.no_flow)
    except (InputError, metrics.InputError) as e:
        print(f"LỖI: {e}", file=sys.stderr)
        return 2
    except MuxError as e:
        print(f"LỖI mux: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
