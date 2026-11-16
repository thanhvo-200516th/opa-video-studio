"""CLIP (open_clip ViT-B-32 laion2b) — embed câu tìm / ảnh để chấm mức hợp giữa footage và cảnh.

Chạy trong ~/.venvs/footage (torch CPU). Nạp model một lần, embed theo lô; embedding ảnh xem trước nguồn ngoài được
cache trên đĩa theo URL để chạy lại không tải / tính lại.
"""
from __future__ import annotations

import hashlib
import io
import os
from pathlib import Path

import numpy as np
from PIL import Image

MODEL, PRETRAINED = "ViT-B-32", "laion2b_s34b_b79k"
CACHE = Path.home() / ".cache/auto-footage"


class Ranker:
    def __init__(self) -> None:
        import open_clip
        import torch

        torch.set_num_threads(max(1, (os.cpu_count() or 4) - 1))
        self.torch = torch
        os.environ.setdefault("HF_HUB_OFFLINE", "1")              # model đã có trong cache → khỏi gọi mạng
        try:
            self.model, _, self.pre = open_clip.create_model_and_transforms(MODEL, pretrained=PRETRAINED)
        except Exception:  # noqa: BLE001 — lần đầu chưa có model: tải
            os.environ["HF_HUB_OFFLINE"] = "0"
            self.model, _, self.pre = open_clip.create_model_and_transforms(MODEL, pretrained=PRETRAINED)
        self.model.eval()
        self.tok = open_clip.get_tokenizer(MODEL)
        CACHE.mkdir(parents=True, exist_ok=True)
        self._disk = CACHE / "thumb_emb.npz"
        self._cache: dict[str, np.ndarray] = dict(np.load(self._disk)) if self._disk.exists() else {}

    def text(self, queries: list[str]) -> np.ndarray:
        with self.torch.no_grad():
            e = self.model.encode_text(self.tok(queries)).float().numpy()
        return e / np.linalg.norm(e, axis=1, keepdims=True)

    def images(self, imgs: list[Image.Image], batch: int = 32) -> np.ndarray:
        out = []
        for i in range(0, len(imgs), batch):
            x = self.torch.stack([self.pre(im.convert("RGB")) for im in imgs[i:i + batch]])
            with self.torch.no_grad():
                out.append(self.model.encode_image(x).float().numpy())
        e = np.concatenate(out) if out else np.zeros((0, 512), np.float32)
        return e / np.maximum(np.linalg.norm(e, axis=1, keepdims=True), 1e-9)

    def thumbs(self, items: list[tuple[str, bytes | None]]) -> np.ndarray:
        """items = [(khoá cache, bytes ảnh hoặc None nếu đã cache)] → embedding theo đúng thứ tự (ảnh hỏng → vector 0)."""
        todo = [(k, b) for k, b in items if self._key(k) not in self._cache and b]
        imgs, keys = [], []
        for k, b in todo:
            try:
                imgs.append(Image.open(io.BytesIO(b)))
                keys.append(k)
            except Exception:  # noqa: BLE001 — ảnh xem trước hỏng thì coi như không có
                continue
        for k, e in zip(keys, self.images(imgs)):
            self._cache[self._key(k)] = e
        if keys:
            np.savez(self._disk, **self._cache)
        return np.stack([self._cache.get(self._key(k), np.zeros(512, np.float32)) for k, _ in items]) if items else np.zeros((0, 512))

    def cached(self, key: str) -> bool:
        return self._key(key) in self._cache

    @staticmethod
    def _key(k: str) -> str:
        return hashlib.sha1(k.encode()).hexdigest()


def best_score(q: np.ndarray, e: np.ndarray) -> np.ndarray:
    """q: (Q, D) câu tìm; e: (N, D) ảnh → điểm mỗi ảnh = max cosine trên các câu tìm."""
    if len(e) == 0:
        return np.zeros(0)
    return (e @ q.T).max(axis=1)
