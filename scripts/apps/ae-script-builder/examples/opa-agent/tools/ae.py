"""Dựng và render project After Effects "OPA Agent × Pancake" mà không đụng phiên AE đang mở.

- build: gộp build/*.jsx thành một file, chép project trống (tools/seed) ra file đích, mở phiên AE
  headless riêng (AfterFX.exe -noui -m -s, giống cách aerender tự mở engine) để chạy script, đọc báo cáo.
- render: gọi aerender (luôn chạy engine riêng) ra MP4 H.264 hoặc ảnh TIFF→PNG.

Ví dụ:
  python -I tools/ae.py build
  python -I tools/ae.py render --comp OPA_AGENT_MASTER_16x9 --start 0 --end 149 --out out/sample.mp4
  python -I tools/ae.py stills --comp S1_MO_DAU --frames 20,60,100 --outdir out/stills
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
AE_DIR = Path(r"C:\Program Files\Adobe\Adobe After Effects 2026\Support Files")
AFX = AE_DIR / "AfterFX.exe"
AERENDER = AE_DIR / "aerender.exe"
SEED = ROOT / "tools" / "seed" / "empty-ae26.aep"
DEFAULT_TARGET = ROOT / "project" / "OPA-Agent-Pancake_v01.aep"
BUNDLE_ORDER = ["lib.jsx", "data/mascot_paths.jsxinc", "data/am_thanh_cues.jsxinc", "scenes/*.jsx", "main.jsx"]


def fwd(p: Path) -> str:
    return str(p).replace("\\", "/")


def bundle() -> Path:
    parts = []
    for pat in BUNDLE_ORDER:
        files = sorted(BUILD.glob(pat)) if "*" in pat else [BUILD / pat]
        for f in files:
            parts.append(f"// ===== {f.relative_to(BUILD).as_posix()} =====\n" + f.read_text(encoding="utf-8"))
    out = BUILD / "_bundle.jsx"
    out.write_text("\n".join(parts), encoding="utf-8")
    return out


def build(target: Path, timeout: int) -> int:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        backup = target.with_suffix(f".bak-{time.strftime('%H%M%S')}.aep")
        shutil.move(target, backup)
        print(f"Bản cũ chuyển sang {backup.name}")
    shutil.copyfile(SEED, target)
    report = BUILD / "_report.json"
    report.unlink(missing_ok=True)
    b = bundle()
    loader = (
        "if (!(app.project && (app.project.file || app.project.numItems))) { "
        f"var OPA_ARGS = {{target: '{fwd(target)}', report: '{fwd(report)}', sfx: '{fwd(ROOT / 'assets' / 'sfx')}'}}; "
        f"var f = new File('{fwd(b)}'); f.encoding = 'UTF-8'; f.open('r'); var s = f.read(); f.close(); eval(s); }}"
    )
    t0 = time.time()
    proc = subprocess.Popen([str(AFX), "-noui", "-m", "-s", loader])
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        print(f"HẾT GIỜ {timeout} s: đã dừng phiên AE headless")
        return 2
    print(f"AE headless xong sau {time.time() - t0:.1f} s")
    if not report.exists():
        print("KHÔNG có báo cáo: script không chạy hoặc chết giữa chừng")
        return 3
    rep = json.loads(report.read_text(encoding="utf-8"))
    print(f"Lưu: {rep.get('saved')} · {rep.get('seconds')} s · {len(rep.get('comps', []))} comp · "
          f"{rep.get('expressionCount')} expression")
    for key in ("errors", "expressionErrors", "warnings"):
        for line in rep.get(key) or []:
            print(f"[{key}] {line}")
    return 1 if rep.get("errors") or rep.get("expressionErrors") else 0


def aerender(args: list[str], log: Path) -> int:
    with log.open("w", encoding="utf-8", errors="replace") as fh:
        proc = subprocess.run([str(AERENDER), *args], stdout=fh, stderr=subprocess.STDOUT)
    text = log.read_text(encoding="utf-8", errors="replace")
    bad = [l for l in text.splitlines() if "ERROR" in l.upper() and "PROGRESS" not in l.upper()]
    for l in bad[:10]:
        print("[aerender]", l)
    return proc.returncode if not bad else 1


def render(project: Path, comp: str, start: int, end: int, out: Path) -> int:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.unlink(missing_ok=True)
    t0 = time.time()
    code = aerender(["-project", str(project), "-comp", comp, "-s", str(start), "-e", str(end),
                     "-RStemplate", "Best Settings", "-OMtemplate", "H.264 - Match Render Settings - 40 Mbps",
                     "-output", str(out)], out.with_suffix(".aerender.log"))
    print(f"render {comp} f{start}-{end} → {out.name}: mã {code}, {time.time() - t0:.1f} s, "
          f"tồn tại={out.exists()} {out.stat().st_size if out.exists() else 0} byte")
    return code


def stills(project: Path, comp: str, frames: list[int], outdir: Path) -> int:
    outdir.mkdir(parents=True, exist_ok=True)
    # aerender không ghi được chuỗi ảnh vào đường dẫn có dấu cách ("Minh PC", "Vibe Coding"): render TIFF vào
    # thư mục tạm không dấu cách, rồi ffmpeg đổi ra PNG ở outdir.
    tmp = Path(tempfile.mkdtemp(prefix="ae_stills_", dir=os.environ.get("PUBLIC", r"C:\Users\Public")))
    code_all = 0
    for f in frames:
        for old in tmp.glob("*.tif"):
            old.unlink()
        code = aerender(["-project", str(project), "-comp", comp, "-s", str(f), "-e", str(f),
                         "-RStemplate", "Best Settings", "-OMtemplate", "TIFF Sequence with Alpha",
                         "-output", str(tmp / "f_[#####].tif")], outdir / "_still.aerender.log")
        tifs = sorted(tmp.glob("*.tif"))
        png = outdir / f"{comp}_f{f:04d}.png"
        if tifs:
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tifs[0]), str(png)], check=False)
        print(f"still {comp} f{f} → {png.name}: mã {code}, png={png.exists()}")
        code_all |= code
    shutil.rmtree(tmp, ignore_errors=True)
    return code_all


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    b.add_argument("--timeout", type=int, default=600)
    r = sub.add_parser("render")
    r.add_argument("--project", type=Path, default=DEFAULT_TARGET)
    r.add_argument("--comp", required=True)
    r.add_argument("--start", type=int, required=True)
    r.add_argument("--end", type=int, required=True)
    r.add_argument("--out", type=Path, required=True)
    s = sub.add_parser("stills")
    s.add_argument("--project", type=Path, default=DEFAULT_TARGET)
    s.add_argument("--comp", required=True)
    s.add_argument("--frames", required=True)
    s.add_argument("--outdir", type=Path, required=True)
    a = ap.parse_args()
    if a.cmd == "build":
        return build(a.target.resolve(), a.timeout)
    if a.cmd == "render":
        return render(a.project.resolve(), a.comp, a.start, a.end, a.out.resolve())
    return stills(a.project.resolve(), a.comp, [int(x) for x in a.frames.split(",")], a.outdir.resolve())


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
