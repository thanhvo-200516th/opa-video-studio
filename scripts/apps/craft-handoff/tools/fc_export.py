#!/usr/bin/env python3
"""fc_export — mở một project FilmCraft (.fcproj) trên màn hình ảo và xuất ra file video (mặc định MP4 H.264).

Dùng cho chế độ server / job API: không có người duyệt nên bản dựng được xuất tự động.
Làm tay trên máy vẫn giữ luật "không tự xuất MP4" — chỉ chạy công cụ này khi được yêu cầu hoặc khi chạy theo job.

    python fc_export.py PROJECT.fcproj OUT.mp4 [--format h264] [--lufs -14] [--crf 20]

Env: CRAFT_DISPLAY, CRAFT_BIN_DIR, CRAFT_X_SERVER (Xephyr | Xvfb) — xem craftctl.py.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from craftctl import Craft, CraftError  # noqa: E402


def export(project: Path, out: Path, fmt: str = "h264", lufs: float | None = None, crf: int | None = None,
           workdir: Path | None = None) -> dict:
    project, out = project.resolve(), out.resolve()
    if not project.exists():
        raise CraftError(f"không có project {project}")
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = workdir or Path(tempfile.mkdtemp(prefix="fc_export-"))
    params: dict = {"path": str(out), "format": fmt, "wait": True}
    if lufs is not None:
        params["loudnessLufs"] = lufs
    if crf is not None:
        params["bitrateMode"], params["crf"] = "crf", crf
    try:
        with Craft("filmcraft", tmp) as fc:
            fc.cmd("file.open", {"path": str(project)})
            result = fc.cmd("export.quick", params)
    finally:
        if workdir is None:
            shutil.rmtree(tmp, ignore_errors=True)
    if not out.exists() or out.stat().st_size == 0:
        raise CraftError(f"FilmCraft báo xong nhưng không có file {out}: {result}")
    return {"out": str(out), "bytes": out.stat().st_size, "result": result}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Xuất video từ project FilmCraft (.fcproj).")
    ap.add_argument("project")
    ap.add_argument("out")
    ap.add_argument("--format", default="h264")
    ap.add_argument("--lufs", type=float, help="chuẩn hoá loudness khi xuất, vd -14")
    ap.add_argument("--crf", type=int)
    a = ap.parse_args(argv)
    try:
        print(json.dumps(export(Path(a.project), Path(a.out), a.format, a.lufs, a.crf), ensure_ascii=False))
    except CraftError as exc:
        print(f"fc_export: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
