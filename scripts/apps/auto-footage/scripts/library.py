"""Chỉ mục CLIP của kho B-roll trên máy (TNEDIT/06_B-Roll): video 3 khung / clip, ảnh 1 embedding / ảnh;
cập nhật tăng dần theo đường dẫn + mtime."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

import media

EXT = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
EXT_IMG = {".jpg", ".jpeg", ".png", ".webp"}
SKIP_DIRS = {".footage_index", "_Tim_Footage"}


class Library:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.dir = root / ".footage_index"
        self.files: list[dict] = []
        self.emb = np.zeros((0, 512), np.float32)
        self.owner = np.zeros(0, int)
        if (self.dir / "index.json").exists():
            self.files = json.loads((self.dir / "index.json").read_text())["files"]
            z = np.load(self.dir / "index.npz")
            self.emb, self.owner = z["emb"], z["owner"]

    def scan(self) -> list[Path]:
        def skip(p: Path) -> bool:              # chỉ mục, kết quả dự án, đoạn trung gian của clip nối (<tên>_doan/), file đang tải
            parts = p.relative_to(self.root).parts
            return bool(SKIP_DIRS & set(parts)) or any(x.endswith("_doan") for x in parts[:-1]) or p.name.endswith(".part")
        return sorted(p for p in self.root.rglob("*") if p.suffix.lower() in EXT | EXT_IMG and p.is_file() and not skip(p))

    def update(self, ranker, log=print) -> int:
        """Thêm clip mới / đổi, bỏ clip đã xoá. Trả số clip vừa lập chỉ mục."""
        old = {f["path"]: (i, f) for i, f in enumerate(self.files)}
        files, embs, owner, n_new = [], [], [], 0
        for p in self.scan():
            mtime = round(p.stat().st_mtime, 1)
            hit = old.get(str(p))
            if hit and hit[1]["mtime"] == mtime:
                e = self.emb[self.owner == hit[0]]
                info = {"type": "video", **hit[1]}
            elif p.suffix.lower() in EXT_IMG:
                try:
                    with Image.open(p) as im:
                        im.load()
                        info = {"path": str(p), "mtime": mtime, "type": "image", "w": im.width, "h": im.height, "duration": 0.0}
                        ims = [im.convert("RGB")]
                except Exception:  # noqa: BLE001
                    log(f"  bỏ qua (ảnh hỏng): {p.name}")
                    continue
                e = ranker.images(ims)
                n_new += 1
            else:
                info = {"path": str(p), "mtime": mtime, "type": "video", **{k: v for k, v in media.probe(p).items() if k != "audio"}}
                ims = media.frames(p, info["duration"]) if info["duration"] > 0 else []
                if not ims:
                    log(f"  bỏ qua (không đọc được khung): {p.name}")
                    continue
                e = ranker.images(ims)
                n_new += 1
            owner += [len(files)] * len(e)
            embs.append(e)
            files.append(info)
        self.files, self.owner = files, np.array(owner, int)
        self.emb = np.concatenate(embs).astype(np.float32) if embs else np.zeros((0, 512), np.float32)
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / "index.json").write_text(json.dumps({"files": files}, ensure_ascii=False, indent=0))
        np.savez(self.dir / "index.npz", emb=self.emb, owner=self.owner)
        return n_new

    def owned_ids(self) -> set[str]:
        """Mã số cuối tên file (FTG_…_14763.mp4 → "14763") — để bỏ clip nguồn ngoài mà kho đã có."""
        return {Path(f["path"]).stem.rsplit("_", 1)[-1] for f in self.files if Path(f["path"]).stem.rsplit("_", 1)[-1].isdigit()}

    def search(self, q: np.ndarray, top: int = 10, kind: str = "video") -> list[dict]:
        """q (Q, D) → clip (kind="video") hoặc ảnh (kind="image") trong kho; điểm = (max + trung bình) trên câu tìm × khung."""
        if not len(self.emb):
            return []
        s = (self.emb @ q.T).max(axis=1)
        peak = np.full(len(self.files), -1.0)
        np.maximum.at(peak, self.owner, s)
        mean = np.bincount(self.owner, s, len(self.files)) / np.maximum(np.bincount(self.owner, minlength=len(self.files)), 1)
        best = (peak + mean) / 2          # cả clip phải hợp, không chỉ một khung tình cờ giống (ngang thang ảnh xem trước 1 khung)
        best[[f.get("type", "video") != kind for f in self.files]] = -9
        out = []
        for i in np.argsort(-best)[:top]:
            if best[i] < -1:
                break
            f = self.files[i]
            p = Path(f["path"])
            out.append({"source": "local", "type": kind, "id": p.stem, "title": p.stem, "thumb": None, "page": str(p), "w": f["w"], "h": f["h"],
                        "duration": f["duration"], "files": [], "path": str(p), "license": "kho TNEDIT (xem _nguon.json / README)",
                        "author": "", "score": float(best[i])})
        return out
