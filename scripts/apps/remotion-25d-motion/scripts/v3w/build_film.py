#!/usr/bin/env python3
"""Dựng phim V3 16:9 "v3-ai-audit-16x9" (20 s, 60 fps, 1200 frame) theo mẫu tools/v2w/build_film.py (import hàm, không
sửa file v2w): render câm → (tùy chọn) mã hóa lại x264 tune animation → nếu có master thì mux NGUYÊN master (không cắt,
không fade, không dời) và đo khớp mốc âm ↔ bảng mốc → ffprobe → contact (mỗi 0,25 s và mỗi 1 s) → still khóa (cắt từ MP4
+ PNG Remotion) → chỉ số (miễn khung CTA từ 18,3 s) → palette_v3 (5 token + ALERT) trên contact và still PNG → kiểm số
(tools/v3w/check_v3w.ts: ≤ 9 chữ, chặng camera, lề Bò) → đo ĐỈNH THỊ GIÁC quanh từng cue trên MP4 (tools/v3w/cue_visual.py).

Chạy:  python tools/v3w/build_film.py [--skip-render] [--tune-animation] [--no-flow] [--no-png]
Master: public/audio/v3-ai-audit-master.wav (V3-AM làm). CHƯA CÓ thì chỉ dựng bản câm và báo rõ (không coi là lỗi).
Đầu ra: out/v3-16x9/film-muted.mp4, v3-ai-audit_16x9.mp4 (có âm, khi có master), contact_0.25s.png, contact_1s.png,
        stills/v3_t<giây>.png, stills/v3_png_t<giây>.png, metrics.json/.md, cue_sync.json (khi có master),
        cue_rois.json + cue_visual.json (đỉnh hình chênh frame so với bảng mốc).
Exit:  0 mọi bước đạt; 1 chỉ số / palette / ffprobe / mux / kiểm số trượt; 2 thiếu file / bước lỗi.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/v2w"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics  # noqa: E402
import palette_v3  # noqa: E402
from build_test import call, check_probe, step  # noqa: E402
from contact import sheet  # noqa: E402
from mux_test import InputError, MuxError, duration, mux  # noqa: E402

OUT = ROOT / "out/v3-16x9"
FILM_ID = "v3-ai-audit-16x9"
NAME = "v3-ai-audit_16x9"
FPS = 60
FRAMES = 1200  # 20 s × 60 fps
MASTER = ROOT / "public/audio/v3-ai-audit-master.wav"
EXEMPT = [(18.3, 20.0)]  # khung CTA cuối (bảng mốc: miễn chỉ số đứng yên từ 18,3)
KEY_STILLS = [0.5, 1.6, 2.9, 4.2, 4.7, 5.0, 5.5, 6.1, 6.6, 7.0, 7.5, 8.3, 8.8, 9.05, 9.9, 10.05, 10.15, 10.3, 11.0,
              12.2, 12.6, 13.6, 14.3, 14.9, 15.0, 15.1, 15.6, 16.6, 17.85, 19.5]
PNG_STILLS = [1.6, 7.6, 8.3, 9.1, 10.15, 11.0, 13.6, 15.6, 17.85]
# Bảng mốc âm (giây, cue) — cùng V3_CUES của src/v3w/timing.ts (đỉnh hình đặt đúng các mốc này trong mã).
CUES = [(1.0, "chime-hoi"), (1.5, "tick-accent-1"), (4.0, "thump"), (4.1, "tick-eject"), (4.2, "tick-eject"),
        (4.3, "tick-eject"), (4.4, "tick-eject"), (7.0, "blip-alert-1"), (7.5, "blip-alert-2"), (8.0, "tick-accent-2"),
        (8.75, "snort"), (9.0, "tick-fix"), (10.0, "paper"), (12.5, "tick-num"), (13.0, "tick-num"), (13.5, "tick-num"),
        (14.0, "tick-accent-3"), (15.0, "whoosh-dive"), (15.5, "hit-logo"), (17.8, "tick-cta")]
X264_TUNED = ["-c:v", "libx264", "-preset", "slow", "-tune", "animation", "-crf", "16", "-pix_fmt", "yuv420p",
              "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
              "-movflags", "+faststart"]


def render(dst: Path, crf: int) -> None:
    step(f"render câm {FILM_ID} ({FRAMES} frame, crf {crf})")
    call([sys.executable, "tools/remotion_run.py", "render", FILM_ID, str(dst), "--muted", "--codec=h264",
          "--jpeg-quality=95", f"--crf={crf}", "--gl=angle"], "render")


def reencode(src: Path, dst: Path) -> None:
    step("mã hóa lại x264 -tune animation (crf 16)")
    call([shutil.which("ffmpeg") or "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), *X264_TUNED,
          str(dst)], "ffmpeg tune animation")


def mp4_stills(mp4: Path) -> list[Path]:
    paths = []
    for s in KEY_STILLS:
        dst = OUT / "stills" / f"v3_t{s:.3f}.png"
        dst.parent.mkdir(parents=True, exist_ok=True)
        call([shutil.which("ffmpeg") or "ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-vf",
              f"select=eq(n\\,{round(s * FPS)})", "-fps_mode", "passthrough", "-frames:v", "1", str(dst)], f"cắt still {s}")
        paths.append(dst)
    return paths


def png_stills() -> list[Path]:
    bundle = OUT / "bundle"
    call([sys.executable, "tools/remotion_run.py", "bundle", "--out-dir", str(bundle)], "bundle")
    paths = []
    for s in PNG_STILLS:
        dst = OUT / "stills" / f"v3_png_t{s:.3f}.png"
        call([sys.executable, "tools/remotion_run.py", "still", str(bundle), FILM_ID, str(dst), f"--frame={round(s * FPS)}"],
             f"still PNG {s}")
        paths.append(dst)
    cover = OUT / f"{NAME}_cover.png"
    call([sys.executable, "tools/remotion_run.py", "still", str(bundle), "v3-16x9-cover", str(cover)], "ảnh bìa")
    return paths + [cover]


CUE_CSV = ROOT / "src/audio/cues/v3-ai-audit.csv"
SFX_STEM = ROOT / "out/tmp/V3-AM/audio/sfx-master.wav"


def read_wav_mono(wav: Path) -> np.ndarray:
    r = subprocess.run([shutil.which("ffmpeg") or "ffmpeg", "-v", "error", "-i", str(wav), "-ac", "1", "-ar", "48000",
                        "-f", "f32le", "-"], capture_output=True)
    if r.returncode != 0:
        raise InputError(f"ffmpeg không đọc được {wav}")
    return np.frombuffer(r.stdout, np.float32)


def cue_sync() -> list[dict]:
    """Khớp mốc: (1) hợp đồng — mỗi mốc hình của bảng có đúng một cue cùng giây trong src/audio/cues/v3-ai-audit.csv
    (V3-AM đặt âm theo file này, QA của V3-AM đo ±1 ms trên stem); chênh hợp đồng tính bằng f60, phải 0 (≤ 1).
    (2) đo thêm (chỉ báo): đỉnh |biên độ| của stem sfx trong ±50 ms quanh mốc cho cue neo "peak"."""
    rows = list(csv.DictReader(CUE_CSV.open(encoding="utf-8")))
    stem = read_wav_mono(SFX_STEM) if SFX_STEM.is_file() else None
    out = []
    for t, name in CUES:
        cand = [r for r in rows if r["id"].startswith(name)]
        best = min(cand, key=lambda r: abs(float(r["giay"]) - t)) if cand else None
        if best is None:
            out.append({"t": t, "cue": name, "csv": None, "deltaF60": None, "measuredF60": None, "ok": False})
            continue
        delta = (float(best["giay"]) - t) * FPS
        meas = None
        if stem is not None and best["anchor"] == "peak":
            a, b = int((t - 0.05) * 48000), int((t + 0.05) * 48000)
            k = a + int(np.argmax(np.abs(stem[a:b])))
            meas = round((k / 48000 - t) * FPS, 2)
        out.append({"t": t, "cue": best["id"], "csv": float(best["giay"]), "anchor": best["anchor"], "deltaF60": round(delta, 3),
                    "measuredF60": meas, "ok": abs(delta) <= 1.0})
    return out


def build(skip_render: bool, tune: bool, flow: bool, png: bool) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    muted = OUT / "film-muted.mp4"
    if not skip_render:
        if tune:
            inter = OUT / "film-crf1.mp4"
            render(inter, 1)
            reencode(inter, muted)
        else:
            render(muted, 16)
    if not muted.is_file():
        raise InputError(f"thiếu {muted}")
    bad = check_probe(muted, FRAMES)
    final = muted
    if MASTER.is_file():
        step(f"mux nguyên master {MASTER.name} ({duration(MASTER, 'a'):.3f} s, lệch 0)")
        final = OUT / f"{NAME}.mp4"
        res = mux(muted, MASTER, final)
        print(f"  lệch âm/hình {res['delta'] * 1000:.2f} ms")
        sync = cue_sync()
        (OUT / "cue_sync.json").write_text(json.dumps(sync, ensure_ascii=False, indent=2), encoding="utf-8")
        for c in sync:
            m = "" if c["measuredF60"] is None else f" · đỉnh stem {c['measuredF60']:+.2f} f60"
            d = "thiếu cue" if c["deltaF60"] is None else f"{c['deltaF60']:+.2f} f60"
            print(f"  mốc {c['t']:6.2f} {c['cue']:<15} hợp đồng {d}{m} {'' if c['ok'] else 'LỆCH'}")
        bad += [f"mốc {c['t']} {c['cue']} lệch hợp đồng" for c in sync if not c["ok"]]
    else:
        print(f"[build_film v3] CHƯA CÓ master {MASTER.relative_to(ROOT)} → chỉ dựng bản CÂM (mux sau khi V3-AM giao).")
    step("contact sheet (mỗi 0,25 s và mỗi 1 s)")
    c4 = sheet(final, 0.0, 0.25, 8, OUT / "contact_0.25s.png")
    c1 = sheet(final, 0.0, 1.0, 5, OUT / "contact_1s.png")
    step("still khóa (cắt từ MP4)")
    mp4_stills(final)
    step("chỉ số 20 s (miễn khung CTA 18,3–20)")
    r = metrics.run(final, 0.0, [], FILM_ID, flow, OUT / "metrics.json", OUT / "metrics.md", EXEMPT)
    print(metrics.summary(r))
    step("palette_v3 (5 token + ALERT)")
    for p in [c1] + (png_stills() if png else []):
        pr = palette_v3.check_file(p)
        print(palette_v3.summary(pr))
        bad += [f"palette {p.name}: {x}" for x in pr["reasons"]]
    step("kiểm số (≤ 9 chữ, chặng camera)")
    node = shutil.which("node") or "node"
    if subprocess.run([node, str(ROOT / "node_modules/tsx/dist/cli.mjs"), "tools/v3w/check_v3w.ts", "--json",
                       str(OUT / "check_v3w.json")], cwd=ROOT).returncode != 0:
        bad.append("check_v3w trượt")
    step("đỉnh thị giác quanh cue (đo trên MP4)")
    if subprocess.run([sys.executable, "tools/v3w/cue_visual.py", str(final), "--rois", str(OUT / "cue_rois.json"),
                       "--json", str(OUT / "cue_visual.json")], cwd=ROOT).returncode != 0:
        bad.append("cue_visual: có cue lệch > 1 f60")
    for b in bad:
        print(f"  TRƯỢT {b}")
    ok = r["pass"] and not bad
    print(f"[build_film v3] {NAME}: {'ĐẠT' if ok else 'TRƯỢT'} → {final} (contact {c4.name})")
    return 0 if ok else 1


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Dựng phim V3 16:9 (render câm → mux master nếu có → đo)")
    ap.add_argument("--skip-render", action="store_true", help="dùng lại film-muted.mp4 đã có")
    ap.add_argument("--tune-animation", action="store_true", help="render crf 1 rồi mã hóa lại x264 -tune animation")
    ap.add_argument("--no-flow", action="store_true")
    ap.add_argument("--no-png", action="store_true", help="bỏ still PNG Remotion + ảnh bìa")
    a = ap.parse_args()
    try:
        return build(a.skip_render, a.tune_animation, not a.no_flow, not a.no_png)
    except (InputError, metrics.InputError) as e:
        print(f"LỖI: {e}", file=sys.stderr)
        return 2
    except MuxError as e:
        print(f"LỖI mux: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
