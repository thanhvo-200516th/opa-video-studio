"""Lưu clip / ảnh đã chọn vào kho: tải + chuẩn hoá nguồn ngoài, Muse tạo ảnh / video, ảnh động; ghi `_nguon.json`."""
from __future__ import annotations

import datetime as dt
import json
import os
import tempfile
from pathlib import Path

from PIL import Image

import media
import sources

ROOT = Path(os.environ.get("AUTO_FOOTAGE_ROOT", "/home/vmiz/Thanh/Media/TNEDIT/06_B-Roll"))
DEST = {("pexels", "video"): "Stock_Theo_Chu_De_Pexels", ("pixabay", "video"): "Stock_Theo_Chu_De_Pixabay",
        ("mixkit", "video"): "Stock_Theo_Chu_De_Mixkit",
        ("pexels", "image"): "Anh_Theo_Chu_De_Pexels", ("pixabay", "image"): "Anh_Theo_Chu_De_Pixabay"}
MUSE_LICENSE = "Tạo bằng Muse (AI)"


def note(folder: Path, name: str, info: dict) -> None:
    p = folder / "_nguon.json"
    d = json.loads(p.read_text()) if p.exists() else {}
    d[name] = info
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1))


def measure(path: Path) -> dict:
    if path.suffix.lower() in media.IMG_EXT:
        with Image.open(path) as im:
            return {"w": im.width, "h": im.height, "duration": 0.0}
    info = media.probe(path)
    return {"w": info["w"], "h": info["h"], "duration": info["duration"]}


def save_remote(c: dict, category: str, project: str) -> dict:
    """Tải bản đầy đủ của ứng viên nguồn ngoài → chuẩn hoá → kho theo nguồn; đã có cùng mã thì dùng lại."""
    kind = c.get("type", "video")
    folder = ROOT / DEST[(c["source"], kind)]
    ext, prefix = (".mp4", "FTG") if kind == "video" else (".jpg", "IMG")
    out = folder / f"{prefix}_{category}_{media.slug(c['title'], 40)}_{c['id']}{ext}"
    if not out.exists():
        same = list(folder.glob(f"*_{c['id']}{ext}"))
        if same:
            out = same[0]
        else:
            with tempfile.TemporaryDirectory() as td:
                raw, err = None, None
                for url in sources.best_file(c["files"]):
                    try:
                        raw = media.download(url, Path(td) / ("raw" + (".mp4" if kind == "video" else ".img")))
                        break
                    except Exception as e:  # noqa: BLE001
                        err = e
                if raw is None:
                    raise RuntimeError(f"không tải được {c['source']} {c['id']}: {err}")
                (media.normalize if kind == "video" else media.normalize_image)(raw, out)
            note(folder, out.name, {"source": c["source"], "type": kind, "id": c["id"], "page": c["page"], "author": c["author"],
                                    "license": c["license"], "title": c["title"], "project": project,
                                    "date": dt.date.today().isoformat()})
    return {**c, "path": str(out), **measure(out)}


def muse_base(project: str, scene: dict) -> Path:
    """Tên chung cho ảnh (.png) và video (.mp4) Muse của một cảnh — cảnh "both" dùng chung một ảnh."""
    sid = str(scene.get("base_id", scene["id"]))
    tag = f"{int(sid):02d}" if sid.isdigit() else media.slug(sid, 12)
    return ROOT / "AI_Muse" / project / f"canh{tag}_{media.slug(scene.get('category') or scene['query'], 40)}"


def _pick(path: Path, prompt: str) -> dict:
    return {"source": "muse", "type": "video" if path.suffix == ".mp4" else "image", "id": path.stem, "title": prompt[:60],
            "page": "", "path": str(path), **measure(path), "license": MUSE_LICENSE, "author": "Muse", "score": None,
            "rank_score": None, "files": []}


CHAIN_OVER = 10        # video Muse dài hơn mức này → nối nhiều đoạn (một video dài liền thì bối cảnh trôi)


def muse_make(scene: dict, project: str, refs: list[str], video: bool, seconds: int = 5, log=print) -> dict:
    """Muse: ảnh 9:16 (luôn) → video từ ảnh đó (khi video=True); > 10 s thì nối đoạn 5–10 s giữ bối cảnh
    (`chain: false` để tạo một video liền). Đã có file thì dùng lại (xoá file để tạo lại)."""
    import muse
    base = muse_base(project, scene)
    png, mp4 = base.with_suffix(".png"), base.with_suffix(".mp4")
    meta = {"source": "muse", "prompt": muse.full_prompt(scene["muse_prompt"]), "refs": refs, "project": project,
            "date": dt.date.today().isoformat(), "license": MUSE_LICENSE}
    if png.exists():
        log(f"  Muse cảnh {scene['id']}: dùng lại {png.name}")
    else:
        muse.generate_image(scene["muse_prompt"], png, refs=refs)
        note(png.parent, png.name, {**meta, "type": "image"})
    out = {"image": _pick(png, scene["muse_prompt"]), "video": None}
    if video:
        if mp4.exists():
            log(f"  Muse cảnh {scene['id']}: dùng lại {mp4.name}")
        elif seconds > CHAIN_OVER and scene.get("chain", True):
            import chain
            log(f"  Muse cảnh {scene['id']}: {seconds} s = nối đoạn {chain.plan_segments(seconds, int(scene.get('seg_seconds', 8)))} s")
            info = chain.muse_chain(scene["muse_prompt"], png, mp4, seconds, int(scene.get("seg_seconds", 8)),
                                    scene.get("muse_steps"), static=scene.get("camera", "static") == "static", log=log)
            note(mp4.parent, mp4.name, {**meta, "type": "video", "first_frame": str(png), "seconds": seconds, "chain": info})
        else:
            muse.generate_video(scene["muse_prompt"], png, mp4, seconds=seconds)
            note(mp4.parent, mp4.name, {**meta, "type": "video", "first_frame": str(png), "seconds": seconds})
        out["video"] = _pick(mp4, scene["muse_prompt"])
    return out


def animate(pick: dict, project: str, seconds: float = 5.0) -> str:
    """Ảnh đã chọn → clip zoom chậm 9:16 trong `_Tim_Footage/<dự án>/anh_dong/` (không tốn lượt Muse)."""
    out = ROOT / "_Tim_Footage" / project / "anh_dong" / f"{Path(pick['path']).stem}_dong.mp4"
    if not out.exists():
        media.ken_burns(Path(pick["path"]), out, seconds=seconds)
    return str(out)
