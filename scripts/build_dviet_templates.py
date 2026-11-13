#!/usr/bin/env python3
"""build_dviet_templates — tạo bộ template chữ FilmCraft "[DViet v2]" khung 1080x1920 từ dviet-style.json.

    ~/.venvs/video-skills/bin/python build_dviet_templates.py OUT_DIR [--background still_or_clip]

Cách làm: dviet_text.py sinh các khối chữ → scripts/apps/craft-handoff/tools/fc_build.py cho FilmCraft dựng thật (một FilmCraft
riêng trên màn hình ảo) → lấy tham số graphic_text FilmCraft đã lưu → ghép mỗi khối thành một .fcgt có ô chỉnh
chữ/màu → vẽ ảnh xem trước bằng graphics.template.thumbnail. Chép .fcgt vào
~/.local/share/filmcraft/Graphics Templates/ để dùng (FilmCraft đang mở cần mở lại mới thấy).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CRAFT_TOOLS = HERE / "apps" / "craft-handoff" / "tools"
TICKS = 254_016_000_000
DUR = 5.0
TEMPLATES = [   # (id, tên, sự kiện mẫu — chữ mẫu do skill tự đặt)
    ("caption", "Phụ đề ngực 1–3 từ", {"role": "caption", "text": "chữ phụ đề"}),
    ("pair", "Cặp chữ nối + từ khoá serif", {"role": "pair", "small": "chữ nối", "big": "từ khoá"}),
    ("stack3", "Chồng 3 tầng", {"role": "stack3", "small": "dòng nhỏ", "big": "chữ lớn", "accent": "chữ nhấn"}),
    ("number", "Số lớn mở đầu danh sách", {"role": "number", "num": "3", "noun": "điều", "context": "nên biết"}),
    ("header", "Tiêu đề phần", {"role": "header", "label": "bước một", "big": "tiêu đề", "sub": "chú thích"}),
    ("cta", "CTA lưu lại", {"role": "cta", "text": "Lưu lại"}),
]


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"LỖI khi chạy {' '.join(cmd[:2])}…\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")


def graphic_layers(fcproj: Path) -> list[dict]:
    found: list[dict] = []

    def walk(o):
        if isinstance(o, dict):
            if o.get("effect") == "graphic_text" and "params" in o:
                found.append(o)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(json.loads(fcproj.read_text(encoding="utf-8")))
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--background", help="ảnh/clip nền cho ảnh kiểm (mặc định nền xám)")
    a = ap.parse_args()
    out = Path(a.out_dir).resolve()
    work = out / "_build"
    work.mkdir(parents=True, exist_ok=True)
    events = {"events": [dict(ev, at=i * DUR, dur=DUR) for i, (_, _, ev) in enumerate(TEMPLATES)]}
    (work / "events.json").write_text(json.dumps(events, ensure_ascii=False), encoding="utf-8")
    run([sys.executable, str(HERE / "dviet_text.py"), str(work / "events.json"), "-o", str(work / "text.json")])
    tracks = json.loads((work / "text.json").read_text(encoding="utf-8"))["tracks"]
    bg = a.background
    if not bg:
        bg = str(work / "bg.png")
        run(["/home/vmiz/.local/bin/ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x6b6b6b:s=1080x1920", "-frames:v", "1", bg])
    spec = {"name": "DViet v2 templates", "width": 1080, "height": 1920, "fps": 30, "duration": DUR * len(TEMPLATES),
            "tracks": [{"type": "video", "name": "V1 nền", "clips": [{"src": bg, "at": 0, "dur": DUR * len(TEMPLATES), "audio": False}]}] + tracks}
    (work / "spec.craft.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    run(["python3", "-I", str(CRAFT_TOOLS / "fc_build.py"), str(work / "spec.craft.json"), str(work / "templates.fcproj"),
         "--report", str(work / "report.json"), "--frames", str(len(TEMPLATES)), "--workdir", str(work / "fc")])
    layers = graphic_layers(work / "templates.fcproj")
    style = json.loads((HERE.parent / "references" / "dviet-style.json").read_text(encoding="utf-8"))
    written = []
    for i, (tid, name, ev) in enumerate(TEMPLATES):
        texts = [v for k, v in ev.items() if k not in ("role",)]
        mine = [l for l in layers if l["params"]["text"]["value"]["Text"] in texts]
        mine.sort(key=lambda l: texts.index(l["params"]["text"]["value"]["Text"]))
        tpl_layers, controls = [], []
        for uid, l in enumerate(mine, 1):
            p = dict(l["params"])
            p.pop("opacity", None)
            tpl_layers.append({"effect": "graphic_text", "enabled": True, "params": p, "layer": {"uid": uid}})
            controls.append({"id": f"text{uid}", "name": f"Chữ {uid}", "kind": "text", "layer": uid, "param": "text"})
            if p["fill_color"]["value"]["Color"][:3] != [1.0, 1.0, 1.0]:
                controls.append({"id": f"color{uid}", "name": f"Màu nhấn {uid}", "kind": "color", "layer": uid, "param": "fill_color"})
        fcgt = {"format": "filmcraft.graphicsTemplate", "version": 1, "id": f"user:dviet-v2-{tid}",
                "name": f"[DViet v2] {name}", "category": "Titles",
                "description": "Style @__dviet đo từ 17 video (2026-10-29), khung dọc 1080x1920, font đủ dấu tiếng Việt. "
                               "Animation vào (blur-in 0,17 s) đặt bằng keyframe — xem master-video-edit/references/dviet-style-guide.md.",
                "author": "master-video-edit", "license": "CC0", "tags": ["dviet", "v2", "9x16", tid],
                "canvas": [style["canvas"]["w"], style["canvas"]["h"]], "duration": int(DUR * TICKS),
                "layers": tpl_layers, "graphic": {"intro": 0, "outro": 0, "designIn": 0, "designDuration": 0}, "controls": controls}
        path = out / f"dviet-v2-{tid}.fcgt"
        path.write_text(json.dumps(fcgt, ensure_ascii=False, indent=2), encoding="utf-8")
        written.append((path, len(tpl_layers)))
    thumbs = out / "_thumbs"
    thumbs.mkdir(exist_ok=True)
    sys.path.insert(0, str(CRAFT_TOOLS))
    from craftctl import Craft  # noqa: E402
    with Craft("filmcraft", work / "fc_thumb") as fc:
        for path, _ in written:
            fc.cmd("graphics.template.thumbnail", {"template": str(path), "width": 360, "path": str(thumbs / (path.stem + ".png"))})
    for path, n in written:
        print(f"{path.name}: {n} lớp, ảnh xem trước {thumbs / (path.stem + '.png')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
