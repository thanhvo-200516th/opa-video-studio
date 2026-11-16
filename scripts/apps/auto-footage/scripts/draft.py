"""Khung scenes.json từ lời đã bóc (transcript.json của `footage.py transcribe`) hoặc file kịch bản (.txt/.md).

Gộp câu thành cảnh ~4–8,5 s (kịch bản: ~15–35 chữ / cảnh), câu mở ý liệt kê ("Thứ hai, …", "Bước 3") luôn sang cảnh mới;
điền id, mốc, lời; để trống query / muse_prompt cho agent viết
(`run` báo lỗi nếu còn trống query).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

LIST_START = re.compile(r"^(thứ (nhất|hai|ba|tư|năm|sáu)|(một|hai|ba|bốn|năm)\s*[,.:]|\d+\s*[.,:)]|đầu tiên|tiếp theo|"
                        r"cuối cùng|bước (\d+|một|hai|ba))", re.I)
EMPTY = {"query": "", "alt_queries": [], "category": "", "mixkit_tags": [], "min_dur": 3, "muse": "auto", "muse_prompt": ""}


def from_segments(segs: list[dict], min_len: float = 4.0, max_len: float = 8.5) -> list[dict]:
    scenes, cur = [], None
    for sg in segs:
        new_item = bool(LIST_START.match(sg["text"].strip()))         # "Thứ hai, …" → mỗi ý liệt kê một cảnh
        if cur and (new_item or cur["t"][1] - cur["t"][0] >= min_len or sg["end"] - cur["t"][0] > max_len):
            scenes.append(cur)
            cur = None
        if cur is None:
            cur = {"t": [round(sg["start"], 2), round(sg["end"], 2)], "text": sg["text"].strip()}
        else:
            cur["t"][1] = round(sg["end"], 2)
            cur["text"] += " " + sg["text"].strip()
    if cur:
        scenes.append(cur)
    return scenes


def from_text(text: str, min_words: int = 15, max_words: int = 35) -> list[dict]:
    text = re.sub(r"^#.*$", "", text, flags=re.M)                       # bỏ tiêu đề markdown
    sents = [s.strip() for s in re.split(r"(?<=[.!?…])\s+|\n+", text) if len(s.strip().split()) >= 2]
    scenes, cur = [], []
    for s in sents:
        n = sum(len(x.split()) for x in cur)
        if cur and (n >= min_words or n + len(s.split()) > max_words):
            scenes.append({"t": None, "text": " ".join(cur)})
            cur = []
        cur.append(s)
    if cur:
        scenes.append({"t": None, "text": " ".join(cur)})
    return scenes


def draft(src: Path, project: str) -> dict:
    if src.suffix == ".json":
        d = json.loads(src.read_text())
        scenes, video = from_segments(d["segments"]), d.get("video")
    else:
        scenes, video = from_text(src.read_text()), None
    out = {"project": project, "orientation": "portrait", **({"video": video} if video else {}),
           "scenes": [{"id": i, **s, **EMPTY} for i, s in enumerate(scenes, 1)]}
    return out
