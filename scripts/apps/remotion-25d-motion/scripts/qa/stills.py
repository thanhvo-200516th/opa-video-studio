#!/usr/bin/env python3
"""Xuất still cỡ thật (KH §3.10).

Chạy:
  python tools/qa/stills.py <id> --source=remotion|mp4 --frames=N,N,… --out=<dir> [--props=<file>] [--media=<mp4>]
Ghi <dir>/fNNN.png.
  remotion: `remotion_run.py bundle` một lần vào out/.bundle rồi `still out/.bundle <id> …`;
            bundle lỗi thì gọi `still <id> …` thường.
  mp4:      ffmpeg select=eq(n\\,N) (mặc định --media = out/<id>/<id>_9x16.mp4).
Exit: 0 đạt, 1 lỗi khi xuất, 2 lỗi đầu vào.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "tools/remotion_run.py"
BUNDLE = ROOT / "out/.bundle"


def still_name(frame: int) -> str:
    return f"f{frame:03d}.png"


def remotion(args: list[str]) -> int:
    """Gọi Remotion qua remotion_run.py (có khóa toàn cục)."""
    return subprocess.run([sys.executable, str(RUNNER), *args], cwd=ROOT, check=False).returncode


def bundle() -> bool:
    """Bundle một lần vào out/.bundle; True khi thành công."""
    return remotion(["bundle", f"--out-dir={BUNDLE}"]) == 0 and (BUNDLE / "index.html").is_file()


def render_remotion(comp_id: str, frames: list[int], out_dir: Path, props: Path | None = None) -> list[Path]:
    """Render still từng frame bằng Remotion; ném RuntimeError nếu có frame lỗi."""
    out_dir.mkdir(parents=True, exist_ok=True)
    serve = [str(BUNDLE)] if bundle() else []
    if not serve:
        print("[stills] bundle lỗi, gọi still trực tiếp từ entry point", file=sys.stderr)
    extra = [f"--props={props.resolve()}"] if props else []
    paths = []
    for n in frames:
        png = out_dir.resolve() / still_name(n)
        code = remotion(["still", *serve, comp_id, str(png), f"--frame={n}", *extra])
        if code != 0 or not png.is_file():
            raise RuntimeError(f"still {comp_id} f{n} lỗi (exit {code})")
        paths.append(png)
    return paths


def extract_mp4(mp4: Path, frames: list[int], out_dir: Path) -> list[Path]:
    """Lấy các frame (đánh số từ 0) từ MP4 trong một lần giải mã."""
    out_dir.mkdir(parents=True, exist_ok=True)
    order = sorted(set(frames))
    expr = "+".join(f"eq(n\\,{n})" for n in order)
    with tempfile.TemporaryDirectory() as tmp:
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-vf", f"select={expr}",
               "-fps_mode", "passthrough", str(Path(tmp) / "s_%04d.png")]
        proc = subprocess.run(cmd, capture_output=True, check=False)
        got = sorted(Path(tmp).glob("s_*.png"))
        if proc.returncode != 0 or len(got) != len(order):
            err = proc.stderr.decode("utf-8", "replace")[-400:]
            raise RuntimeError(f"ffmpeg lấy {len(got)}/{len(order)} frame từ {mp4}: {err}")
        paths = {}
        for n, src in zip(order, got):
            dst = out_dir / still_name(n)
            shutil.move(str(src), dst)
            paths[n] = dst
    return [paths[n] for n in frames]


def parse_opts(argv: list[str]) -> dict:
    opts = {"id": None, "source": None, "frames": None, "out": None, "props": None, "media": None}
    for arg in argv:
        if arg.startswith("--") and "=" in arg:
            key, val = arg[2:].split("=", 1)
            if key not in opts:
                raise ValueError(f"tham số lạ: {arg}")
            opts[key] = val
        elif opts["id"] is None:
            opts["id"] = arg
        else:
            raise ValueError(f"tham số lạ: {arg}")
    if not (opts["id"] and opts["source"] in ("remotion", "mp4") and opts["frames"] and opts["out"]):
        raise ValueError("thiếu <id>, --source=remotion|mp4, --frames hoặc --out")
    opts["frames"] = [int(x) for x in opts["frames"].split(",") if x.strip()]
    return opts


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        o = parse_opts(sys.argv[1:])
    except ValueError as e:
        print(f"LỖI: {e}\n{__doc__}", file=sys.stderr)
        return 2
    out_dir = Path(o["out"])
    try:
        if o["source"] == "mp4":
            media = Path(o["media"]) if o["media"] else ROOT / "out" / o["id"] / f"{o['id']}_9x16.mp4"
            if not media.is_file():
                print(f"Thiếu media: {media}", file=sys.stderr)
                return 2
            paths = extract_mp4(media, o["frames"], out_dir)
        else:
            props = Path(o["props"]) if o["props"] else None
            if props and not props.is_file():
                print(f"Thiếu props: {props}", file=sys.stderr)
                return 2
            paths = render_remotion(o["id"], o["frames"], out_dir, props)
    except RuntimeError as e:
        print(f"FAIL {e}", file=sys.stderr)
        return 1
    for p in paths:
        print(f"OK {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
