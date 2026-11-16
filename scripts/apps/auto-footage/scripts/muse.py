"""Tạo B-roll bằng Muse (muse2api local, chuẩn OpenAI): ảnh 9:16 → video khung đầu = ảnh đó.

Khoá đọc ở MUSE_BASE_URL / MUSE_API_KEY hoặc ~/.config/muse/env. Không đổi sang dịch vụ trả phí khi Muse lỗi.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

import media

ENV = Path.home() / ".config/muse/env"
DONE, FAILED = {"succeeded", "completed"}, {"failed", "error", "cancelled", "interrupted", "expired"}
SUFFIX = ", photorealistic stock footage, natural light, vertical 9:16 composition, no text, no watermark, no logo"


class MuseError(RuntimeError):
    pass


def config() -> tuple[str, str]:
    cfg = {}
    if ENV.exists():
        for line in ENV.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip()
    base = os.environ.get("MUSE_BASE_URL", cfg.get("MUSE_BASE_URL", "")).rstrip("/")
    key = os.environ.get("MUSE_API_KEY", cfg.get("MUSE_API_KEY", ""))
    if not base or not key:
        raise MuseError(f"thiếu MUSE_BASE_URL / MUSE_API_KEY ({ENV})")
    return base, key


def ready() -> bool:
    try:
        base, _ = config()
        root = base.rsplit("/v1", 1)[0]
        return json.loads(media.http_get(f"{root}/readyz", timeout=5, tries=1)).get("ready", False)
    except Exception:  # noqa: BLE001
        return False


def _call(method: str, url: str, key: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None, method=method,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise MuseError(f"Muse {method} → HTTP {e.code}: {e.read().decode(errors='replace')[:300]}") from e


def _wait(url: str, key: str, timeout_s: int) -> dict:
    start = time.time()
    while time.time() - start < timeout_s:
        task = _call("GET", url, key)
        if task.get("status") in DONE:
            return task
        if task.get("status") in FAILED:
            raise MuseError(f"Muse task {task.get('status')}: {task.get('error')}")
        time.sleep(5)
    raise MuseError(f"Muse quá {timeout_s}s chưa xong")


def _result_url(task: dict) -> str:
    res = task.get("result") or {}
    url = res.get("url") or ((res.get("data") or [{}])[0].get("url"))
    if not url:
        raise MuseError("Muse không trả URL kết quả")
    return url


def _fetch(url: str, key: str, out: Path) -> Path:
    raw = out.with_name(out.stem + ".muse" + (Path(url.split("?")[0]).suffix or ".bin"))
    media.download(url, raw, {"Authorization": f"Bearer {key}"})
    return raw


def _data_url(path: str) -> str:
    mime = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(Path(path).read_bytes()).decode()


def full_prompt(prompt: str) -> str:
    return prompt.rstrip(". ") + SUFFIX


def generate_image(prompt: str, out_png: Path, refs: list[str] | None = None, timeout_s: int = 900) -> Path:
    """Ảnh 9:16 → PNG sạch metadata. refs: ≤ 4 ảnh tham chiếu (ví dụ khung mặt người nói) để giữ đúng nhân vật."""
    base, key = config()
    body = {"model": "muse-image", "prompt": full_prompt(prompt), "size": "9:16", "async": True}
    if refs:
        body["image"] = [_data_url(r) for r in refs[:4]]
    task = _call("POST", f"{base}/images/generations", key, body)
    raw = _fetch(_result_url(_wait(f"{base}/images/generations/{task['id']}", key, timeout_s)), key, out_png)
    media.normalize_image(raw, out_png)
    raw.unlink()
    return out_png


def generate_video(prompt: str, first_frame: Path, out_mp4: Path, seconds: int = 5, timeout_s: int = 900, attempt: int = 0) -> Path:
    """Video 9:16 `seconds` giây đi từ ảnh khung đầu → chuẩn hoá (bỏ tiếng Muse, xoá metadata).
    Muse trả lại video cũ khi prompt trùng (bỏ qua ảnh — đo 2026-11-02: đoạn 6 trùng từng byte đoạn 2) → gắn dấu riêng theo ảnh
    khung đầu (+ lần thử) vào prompt."""
    base, key = config()
    tag = hashlib.sha1(Path(first_frame).read_bytes()).hexdigest()[:8] + (f"-{attempt}" if attempt else "")
    task = _call("POST", f"{base}/videos", key, {"model": "muse-video", "prompt": f"{full_prompt(prompt)} (shot {tag})", "size": "9:16",
                                                  "seconds": seconds, "image": _data_url(str(first_frame))})
    raw = _fetch(_result_url(_wait(f"{base}/videos/{task['id']}", key, timeout_s)), key, out_mp4)
    media.normalize(raw, out_mp4)
    raw.unlink()
    return out_mp4
