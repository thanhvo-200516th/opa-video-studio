"""Xuất ảnh kiểm (program monitor) ở các mốc giây từ một .fcproj — FilmCraft riêng trên màn hình ảo, không đụng
cửa sổ người dùng.

    python3 qa_frames.py PROJECT.fcproj OUT_DIR FPS t1 t2 ...      # → OUT_DIR/t0012.50.png …
"""
import sys
import tempfile
from pathlib import Path

_SIB = Path(__file__).resolve().parents[1] / "scripts/apps/craft-handoff/tools"
sys.path.insert(0, str(_SIB))
from craftctl import TICKS_PER_SECOND, Craft  # noqa: E402


def main() -> int:
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    project, out_dir, fps = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), float(sys.argv[3])
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as wd, Craft("filmcraft", Path(wd)) as fc:
        fc.cmd("file.open", {"path": str(project)})
        for t in map(float, sys.argv[4:]):
            frame = round(t * fps)
            path = out_dir / f"t{t:07.2f}.png"
            fc.cmd("file.exportFrame", {"path": str(path), "target": "program", "time": int(frame * TICKS_PER_SECOND / fps),
                                        "format": "png"})
            print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
