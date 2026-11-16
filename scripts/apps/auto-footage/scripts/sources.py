"""Nguồn footage / ảnh ngoài → ứng viên cùng dạng:
{source, type (video|image), id, title, thumb, page, w, h, duration, files [(w, h, url)], license, author, score}.
Key đọc ở ~/.config/footage/env; không in key, không đưa URL có key vào thông báo lỗi.
"""
from __future__ import annotations

import html
import os
import re
from pathlib import Path
from urllib.parse import quote

import media

ENV = Path.home() / ".config/footage/env"
LICENSE = {"pexels": "Pexels License — miễn phí, dùng thương mại, không bắt ghi nguồn",
           "pixabay": "Pixabay Content License — miễn phí, dùng thương mại, không bắt ghi nguồn",
           "mixkit": "Mixkit Stock Video Free License — dùng thương mại, không bắt ghi nguồn"}
STOP = {"a", "an", "the", "of", "in", "on", "at", "to", "with", "and", "or", "for", "from", "by", "is", "are", "his", "her",
        "their", "close", "up", "shot", "view", "person", "people", "man", "woman", "someone", "front", "while", "into"}


def keys() -> dict:
    cfg = {}
    if ENV.exists():
        for line in ENV.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return {k: os.environ.get(k, cfg.get(k, "")) for k in ("PEXELS_API_KEY", "PIXABAY_API_KEY")}


def pexels(query: str, orient: str, key: str, per_page: int = 15) -> list[dict]:
    url = f"https://api.pexels.com/videos/search?query={quote(query)}&per_page={per_page}"
    if orient in ("portrait", "landscape"):
        url += f"&orientation={orient}"
    out = []
    for v in media.http_json(url, {"Authorization": key}).get("videos", []):
        files = [(f["width"], f["height"], f["link"]) for f in v.get("video_files", [])
                 if f.get("file_type") == "video/mp4" and f.get("width") and f.get("link")]
        name = re.sub(r"-\d+/?$", "", v.get("url", "").rstrip("/").split("/")[-1]).replace("-", " ")
        out.append({"source": "pexels", "type": "video", "id": str(v["id"]), "title": name or query, "thumb": v.get("image"), "page": v.get("url", ""),
                    "w": v.get("width", 0), "h": v.get("height", 0), "duration": float(v.get("duration") or 0), "files": files,
                    "license": LICENSE["pexels"], "author": (v.get("user") or {}).get("name", ""), "score": 0.0})
    return out


def pixabay(query: str, key: str, per_page: int = 20) -> list[dict]:
    url = f"https://pixabay.com/api/videos/?key={key}&q={quote(query)}&per_page={per_page}&safesearch=true"
    out = []
    for h in media.http_json(url).get("hits", []):
        vids = h.get("videos") or {}
        files = [(x["width"], x["height"], x["url"]) for x in vids.values() if x.get("url") and x.get("width")]
        big = vids.get("large") or vids.get("medium") or {}
        thumb = (vids.get("medium") or {}).get("thumbnail") or big.get("thumbnail") or (
            f"https://i.vimeocdn.com/video/{h['picture_id']}_640x360.jpg" if h.get("picture_id") else None)
        out.append({"source": "pixabay", "type": "video", "id": str(h["id"]), "title": h.get("tags", query), "thumb": thumb, "page": h.get("pageURL", ""),
                    "w": big.get("width", 0), "h": big.get("height", 0), "duration": float(h.get("duration") or 0), "files": files,
                    "license": LICENSE["pixabay"], "author": h.get("user", ""), "score": 0.0})
    return out


def mixkit_tags(query: str, n: int = 2) -> list[str]:
    words = [w for w in re.findall(r"[a-z]+", query.lower()) if len(w) > 2 and w not in STOP]
    return list(dict.fromkeys(words))[:n]


def mixkit(tags: list[str]) -> list[dict]:
    """Mixkit không có API: đọc trang /free-stock-video/<từ>/ (24 clip / trang). Thời lượng chưa biết trước khi tải."""
    out, seen = [], set()
    for tag in tags:
        page = media.http_get(f"https://mixkit.co/free-stock-video/{quote(tag)}/").decode("utf-8", "replace")
        for blk in page.split('data-algolia-analytics-object-id="video-')[1:]:
            m = re.match(r"(\d+)", blk)
            if not m or m.group(1) in seen:
                continue
            vid = m.group(1)
            seen.add(vid)
            title = re.search(r'overlay-video-title">\s*(.*?)\s*</span>', blk, re.S)
            size = re.search(r'class="item-grid-video-player__thumb"[^>]*width="(\d+)" height="(\d+)"', blk)
            href = re.search(r'href="(/free-stock-video/[^"]+)"', blk)
            w, h = (int(size.group(1)), int(size.group(2))) if size else (16, 9)
            base = f"https://assets.mixkit.co/videos/{vid}/{vid}"
            out.append({"source": "mixkit", "type": "video", "id": vid, "title": html.unescape(title.group(1)).strip(" .") if title else tag,
                        "thumb": f"{base}-thumb-360-0.jpg", "page": f"https://mixkit.co{href.group(1)}" if href else "",
                        "w": w, "h": h, "duration": 0.0, "files": [(0, 1080, f"{base}-1080.mp4"), (0, 720, f"{base}-720.mp4")],
                        "license": LICENSE["mixkit"], "author": "Mixkit", "score": 0.0})
    return out


def pexels_photos(query: str, orient: str, key: str, per_page: int = 15) -> list[dict]:
    """Ảnh Pexels (API /v1/search). Bản tải: ảnh gốc qua CDN giới hạn cạnh dài 2560."""
    url = f"https://api.pexels.com/v1/search?query={quote(query)}&per_page={per_page}"
    if orient in ("portrait", "landscape"):
        url += f"&orientation={orient}"
    out = []
    for ph in media.http_json(url, {"Authorization": key}).get("photos", []):
        src, w, h = ph.get("src") or {}, ph.get("width", 0), ph.get("height", 0)
        if not src.get("original"):
            continue
        side = "h" if h >= w else "w"
        out.append({"source": "pexels", "type": "image", "id": str(ph["id"]), "title": ph.get("alt") or query, "thumb": src.get("medium"),
                    "page": ph.get("url", ""), "w": w, "h": h, "duration": 0.0,
                    "files": [(w, h, f"{src['original']}?auto=compress&cs=tinysrgb&{side}=2560")],
                    "license": LICENSE["pexels"], "author": ph.get("photographer", ""), "score": 0.0})
    return out


def pixabay_photos(query: str, orient: str, key: str, per_page: int = 20) -> list[dict]:
    """Ảnh Pixabay (API /api/, image_type=photo). Bản tải: largeImageURL (cạnh dài 1280)."""
    o = {"portrait": "vertical", "landscape": "horizontal"}.get(orient, "all")
    url = f"https://pixabay.com/api/?key={key}&q={quote(query)}&image_type=photo&orientation={o}&per_page={per_page}&safesearch=true"
    out = []
    for h in media.http_json(url).get("hits", []):
        if not h.get("largeImageURL"):
            continue
        out.append({"source": "pixabay", "type": "image", "id": str(h["id"]), "title": h.get("tags", query),
                    "thumb": h.get("webformatURL") or h.get("previewURL"), "page": h.get("pageURL", ""),
                    "w": h.get("imageWidth", 0), "h": h.get("imageHeight", 0), "duration": 0.0,
                    "files": [(h.get("imageWidth", 0), h.get("imageHeight", 0), h["largeImageURL"])],
                    "license": LICENSE["pixabay"], "author": h.get("user", ""), "score": 0.0})
    return out


def best_file(files: list[tuple]) -> list[str]:
    """URL theo thứ tự nên thử: cạnh ngắn gần 1080 nhất (≤ 2160), rồi tới các bản khác."""
    def key(f):
        w, h, _ = f
        short = min(w, h) if w and h else (h or w or 0)
        return (short > 2160, abs(short - 1080))
    return [f[2] for f in sorted(files, key=key)]
