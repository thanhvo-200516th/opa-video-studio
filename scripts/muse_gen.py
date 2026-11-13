#!/usr/bin/env python3
"""Tạo ảnh / video B-roll qua Muse (muse2api local, chuẩn OpenAI).

    muse_gen.py image "prompt" -o broll.png [--size 16:9] [--ref a.jpg ...] [--transparent]
    muse_gen.py video "prompt" -o broll.mp4 [--size 9:16] [--seconds 5] [--first-frame a.png]

Khoá đọc từ biến môi trường MUSE_BASE_URL / MUSE_API_KEY, không có thì từ ~/.config/muse/env.
Size và thời lượng chỉ là gợi ý ghép vào prompt (muse2api) — luôn kiểm lại file ra.
"""
import argparse
import base64
import json
import mimetypes
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ENV_FILE = Path.home() / ".config/muse/env"
DONE = {"succeeded", "completed"}
FAILED = {"failed", "error", "cancelled", "interrupted", "expired"}


def load_config():
    cfg = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip()
    base = os.environ.get("MUSE_BASE_URL", cfg.get("MUSE_BASE_URL", "")).rstrip("/")
    key = os.environ.get("MUSE_API_KEY", cfg.get("MUSE_API_KEY", ""))
    if not base or not key:
        sys.exit(f"Thiếu MUSE_BASE_URL / MUSE_API_KEY (env hoặc {ENV_FILE})")
    return base, key


def call(method, url, key, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Muse {method} {url} → HTTP {e.code}: {e.read().decode(errors='replace')[:500]}")


def data_url(path):
    mime = mimetypes.guess_type(path)[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(Path(path).read_bytes()).decode()}"


def wait(poll_url, key, timeout_s):
    start = time.time()
    while time.time() - start < timeout_s:
        task = call("GET", poll_url, key)
        status = task.get("status")
        if status in DONE:
            return task
        if status in FAILED:
            sys.exit(f"Muse task {task.get('id')} {status}: {task.get('error')}")
        time.sleep(5)
    sys.exit(f"Muse task quá {timeout_s}s chưa xong: {poll_url}")


def result_url(task):
    res = task.get("result") or {}
    if res.get("url"):
        return res["url"]
    items = res.get("data") or []
    if items and items[0].get("url"):
        return items[0]["url"]
    sys.exit(f"Muse task không có URL kết quả: {json.dumps(task)[:500]}")


def download(url, key, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    src_ext = Path(url.split("?")[0]).suffix.lower()
    raw = out if src_ext == out.suffix.lower() else out.with_name(out.stem + ".muse" + src_ext)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=300) as r:
        raw.write_bytes(r.read())
    if raw != out:  # ví dụ .webp → .png để FilmCraft/Premiere nhận
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), str(out)], check=True)
        raw.unlink()
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=width,height:format=duration",
         "-of", "default=nw=1", str(out)], capture_output=True, text=True).stdout.split()
    print(f"{out}  {' '.join(probe)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kind", choices=["image", "video"])
    ap.add_argument("prompt")
    ap.add_argument("-o", "--out", required=True, type=Path)
    ap.add_argument("--size", help="tỉ lệ khung: 16:9, 9:16, 1:1 (mặc định: image 16:9, video 9:16)")
    ap.add_argument("--ref", nargs="+", default=[], help="ảnh: tối đa 4 ảnh tham chiếu")
    ap.add_argument("--transparent", action="store_true", help="ảnh: tách nền ra PNG RGBA")
    ap.add_argument("--seconds", type=int, default=5, help="video: 1-60 giây")
    ap.add_argument("--first-frame", help="video: ảnh khung đầu")
    ap.add_argument("--timeout", type=int, default=900, help="giây chờ tối đa")
    a = ap.parse_args()
    base, key = load_config()

    if a.kind == "image":
        body = {"model": "muse-image", "prompt": a.prompt, "size": a.size or "16:9", "async": True}
        if a.ref:
            body["image"] = [data_url(p) for p in a.ref[:4]]
        if a.transparent:
            body["background"] = "transparent"
        task = call("POST", f"{base}/images/generations", key, body)
        task = wait(f"{base}/images/generations/{task['id']}", key, a.timeout)
    else:
        body = {"model": "muse-video", "prompt": a.prompt, "size": a.size or "9:16", "seconds": a.seconds}
        if a.first_frame:
            body["image"] = data_url(a.first_frame)
        task = call("POST", f"{base}/videos", key, body)
        task = wait(f"{base}/videos/{task['id']}", key, a.timeout)
    download(result_url(task), key, a.out)


if __name__ == "__main__":
    main()
