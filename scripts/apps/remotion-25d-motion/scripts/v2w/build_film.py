#!/usr/bin/env python3
"""Dựng phim đủ 30 s 16:9 "v2-khong-bo-sot-khach-16x9" (gói NỀN): render câm → (tùy chọn) mã hóa lại x264 tune animation
→ mux NGUYÊN master đã duyệt (−16 LUFS, 30,000 s, lệch 0: không cắt, không fade, không dời) → ffprobe → contact → still
→ chỉ số (khai báo 9,2–9,6; miễn khung CTA cuối) → palette_w (đoạn nối + mảng xám phẳng) trên contact và 6 still kiểm
render PNG không nén từ Remotion (frame cắt từ MP4 lệch màu ở mép do nén 4:2:0, không phải lỗi thiết kế).

Chạy:  python tools/v2w/build_film.py [--skip-render] [--tune-animation] [--no-flow]
  --tune-animation: Remotion render trung gian gần không mất (crf 1), rồi ffmpeg libx264 -preset slow -tune animation
                    -crf 16 (giữ nhãn màu bt709 dải TV như remotion.config.ts): bớt nhấp nháy chữ do nén (tong-ket-test P2).
Đầu ra: out/v2-16x9/film/film-muted.mp4 (+ film-crf1.mp4 khi tune), v2-khong-bo-sot-khach-16x9.mp4 (có âm),
        film_contact.png (mỗi 1 s), stills/film_t<giây>.png (cắt từ MP4), stills/film_png_t<giây>.png (Remotion PNG),
        film_metrics.json/.md.
Remotion chỉ chạy qua tools/remotion_run.py (có khóa). Không shell, không "|".
Exit:  0 mọi bước đạt; 1 chỉ số / palette / ffprobe / mux trượt; 2 thiếu file / bước lỗi.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics  # noqa: E402
import palette_w  # noqa: E402
from build_test import call, check_probe, step, stills, tests_json  # noqa: E402
from contact import sheet  # noqa: E402
from mux_test import MASTER, InputError, MuxError, duration, mux  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT_FILM = ROOT / "out/v2-16x9/film"
NAME = "v2-khong-bo-sot-khach-16x9"
X264_TUNED = ["-c:v", "libx264", "-preset", "slow", "-tune", "animation", "-crf", "16", "-pix_fmt", "yuv420p",
              "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
              "-movflags", "+faststart"]


def film_window() -> dict:
    """Mục `film` của tests.json (scripts/v2w-tests.ts in cùng lúc với 4 test + lab)."""
    data = tests_json()
    if "film" not in data:
        raise InputError("tests.json không có mục film")
    return data["film"]


def render(f: dict, dst: Path, crf: int) -> None:
    step(f"render câm {f['id']} ({f['frames']} frame, crf {crf})")
    call([sys.executable, "tools/remotion_run.py", "render", f["id"], str(dst), "--muted", "--codec=h264",
          "--jpeg-quality=95", f"--crf={crf}", "--gl=angle"], "render")


def reencode(src: Path, dst: Path) -> None:
    step("mã hóa lại x264 -tune animation (crf 16)")
    call([shutil.which("ffmpeg") or "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), *X264_TUNED, str(dst)],
         "ffmpeg tune animation")


def png_stills(f: dict) -> list[Path]:
    """Still kiểm render thẳng từ Remotion (PNG, không nén): bundle một lần rồi still từng frame."""
    bundle = OUT_FILM / "bundle"
    call([sys.executable, "tools/remotion_run.py", "bundle", "--out-dir", str(bundle)], "bundle")
    paths = []
    for s in f["checkStills"]:
        dst = OUT_FILM / "stills" / f"film_png_t{s:.3f}.png"
        dst.parent.mkdir(parents=True, exist_ok=True)
        call([sys.executable, "tools/remotion_run.py", "still", str(bundle), f["id"], str(dst),
              f"--frame={round(s * f['fps'])}"], f"still PNG {s}")
        paths.append(dst)
    return paths


def palette_checks(paths: list[Path]) -> list[str]:
    bad = []
    for p in paths:
        r = palette_w.check_file(p)
        print(palette_w.summary(r))
        bad += [f"palette_w {p.name}: {x}" for x in r["reasons"]]
    return bad


def build(f: dict, skip_render: bool, tune: bool, flow: bool) -> int:
    OUT_FILM.mkdir(parents=True, exist_ok=True)
    muted = OUT_FILM / "film-muted.mp4"
    final = OUT_FILM / f"{NAME}.mp4"
    if not skip_render:
        if tune:
            inter = OUT_FILM / "film-crf1.mp4"
            render(f, inter, 1)
            reencode(inter, muted)
        else:
            render(f, muted, 16)
    if not muted.is_file():
        raise InputError(f"thiếu {muted}")
    step(f"mux nguyên master {MASTER.name} ({duration(MASTER, 'a'):.3f} s, lệch 0)")
    res = mux(muted, MASTER, final)
    step(f"ffprobe (lệch âm/hình {res['delta'] * 1000:.2f} ms)")
    bad = check_probe(final, f["frames"])
    step("contact sheet (mỗi 1 s)")
    contact = sheet(final, f["from"], 1.0, 6, OUT_FILM / "film_contact.png")
    step("still khóa (cắt từ MP4)")
    stills(final, f, OUT_FILM, "film")
    step("chỉ số 30 s")
    r = metrics.run(final, f["from"], [(d["from"], d["to"]) for d in f["declared"]], NAME, flow,
                    OUT_FILM / "film_metrics.json", OUT_FILM / "film_metrics.md",
                    [(d["from"], d["to"]) for d in f["exempt"]])
    step("palette_w trên contact + 6 still kiểm (Remotion PNG)")
    bad += palette_checks([contact] + png_stills(f))
    print(metrics.summary(r))
    for b in bad:
        print(f"  TRƯỢT {b}")
    ok = r["pass"] and not bad
    print(f"[build_film] {NAME}: {'ĐẠT' if ok else 'TRƯỢT'} → {final}")
    return 0 if ok else 1


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Dựng phim đủ 30 s 16:9 (render câm → mux master → đo)")
    ap.add_argument("--skip-render", action="store_true", help="dùng lại film-muted.mp4 đã có")
    ap.add_argument("--tune-animation", action="store_true", help="render crf 1 rồi mã hóa lại x264 -tune animation")
    ap.add_argument("--no-flow", action="store_true")
    a = ap.parse_args()
    try:
        step("cửa sổ phim")
        return build(film_window(), a.skip_render, a.tune_animation, not a.no_flow)
    except (InputError, metrics.InputError) as e:
        print(f"LỖI: {e}", file=sys.stderr)
        return 2
    except MuxError as e:
        print(f"LỖI mux: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
