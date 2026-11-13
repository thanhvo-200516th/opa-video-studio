"""Thay dải tối PNG bằng Color Matte + mask Opacity chữ nhật mềm — cách người dùng làm mẫu 2026-11-05 (lần 13):
Color Matte → Opacity → mask chữ nhật phủ mép trên → Mask Feather / Mask Opacity / Mask Expansion; màu đen (hoặc màu khác).
Chỉnh tay được ngay trong Effect Controls (khác PNG dải tối cố định).

    python3 fc_matte_band.py PROJECT.fcproj [--replace "Dải tối trên"] [--color "#000000"] [--feather 868.8]
                             [--mask-opacity 59.2] [--expansion 213.1] [--rect -60,-50,1140,115]

Mặc định = bảng thông số người dùng chốt (ảnh Effect Controls 2026-11-05): feather 868,8 · mask opacity 59,2 % ·
expansion 213,1 · khung mask phủ mép trên (y −50 → 115 trên khung 1080×1920, tràn hai bên). Sửa thẳng file project rồi lưu;
in tên clip mới để `open_in_app.py --select` chọn sẵn.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

_SIB = Path(__file__).resolve().parents[1] / "scripts/apps/craft-handoff/tools"
sys.path.insert(0, str(_SIB))
from craftctl import TICKS_PER_SECOND, Craft  # noqa: E402

NAME = "Dải tối trên · Color Matte"


def apply(project: Path, replace: str = "Dải tối trên", color: str = "#000000", feather: float = 868.8,
          mask_opacity: float = 59.2, expansion: float = 213.1, rect: tuple = (-60, -50, 1140, 115)) -> str:
    with tempfile.TemporaryDirectory() as wd, Craft("filmcraft", Path(wd)) as fc:
        fc.cmd("file.open", {"path": str(project)})
        seq = fc.cmd("sequence.inspect")
        hit = next(((f"V{ti + 1}", it) for ti, tr in enumerate(seq["video"]) for it in tr["items"]
                    if it.get("name") == replace), None)
        if hit is None:
            raise SystemExit(f"không thấy clip «{replace}» trong {project.name}")
        track, old = hit
        fc.cmd("edit.clear", {"clips": [old["clip"]]})
        res = fc.cmd("file.newColorMatte", {"color": color, "seconds": old["duration"] / TICKS_PER_SECOND})
        item = res.get("item") if isinstance(res, dict) else res
        clip = fc.cmd("timeline.place", {"item": item, "track": track, "time": old["start"], "sourceIn": 0,
                                         "duration": old["duration"]})["clips"][0]
        fc.cmd("clip.rename", {"clip": clip, "name": NAME})
        x0, y0, x1, y1 = rect
        fc.cmd("masks.add", {"clip": clip, "effect": "opacity", "shape": "rectangle",
                             "path": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]})
        fc.cmd("masks.set", {"clip": clip, "effect": "opacity", "feather": feather, "opacity": mask_opacity,
                             "expansion": expansion})
        fc.cmd("file.saveAs", {"path": str(project)})
    return NAME


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("project")
    ap.add_argument("--replace", default="Dải tối trên")
    ap.add_argument("--color", default="#000000")
    ap.add_argument("--feather", type=float, default=868.8)
    ap.add_argument("--mask-opacity", type=float, default=59.2)
    ap.add_argument("--expansion", type=float, default=213.1)
    ap.add_argument("--rect", default="-60,-50,1140,115")
    a = ap.parse_args()
    name = apply(Path(a.project).resolve(), a.replace, a.color, a.feather, a.mask_opacity, a.expansion,
                 tuple(float(v) for v in a.rect.split(",")))
    print(name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
