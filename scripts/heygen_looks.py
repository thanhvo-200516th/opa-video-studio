#!/usr/bin/env python3
"""heygen_looks.py: liệt kê "look" (góc quay) của avatar HeyGen v3 và chia look cho các shot A-roll.

  list --group <group_id> | --all [--out looks.json] [--key-file F]   (gọi mạng, cần HEYGEN_API_KEY hoặc --key-file)
  pick --looks looks.json --videos KB08=3,KB09=2 [--angles 3] [--out assign.json]   (offline, không cần key)

Khoá API CHỈ lấy từ biến môi trường HEYGEN_API_KEY hoặc --key-file do người dùng đưa lúc chạy; không bao giờ ghi ra file/log.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

HEYGEN_BASE = os.environ.get("HEYGEN_API_BASE", "https://api.heygen.com").rstrip("/")
MIN_ANGLES, MAX_ANGLES = 2, 4      # mỗi video dùng 2-4 góc
MAX_PAGES = 50                     # chặn vòng lặp phân trang vô hạn


def load_key(key_file: Optional[Path] = None) -> str:
    """Khoá từ --key-file (một dòng khoá, hoặc HEYGEN_API_KEY=...) rồi tới biến môi trường HEYGEN_API_KEY."""
    if key_file:
        text = Path(key_file).expanduser().read_text(encoding="utf-8")
        for line in text.splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if "=" in s and s.split("=", 1)[0].strip() == "HEYGEN_API_KEY":
                return s.split("=", 1)[1].strip().strip('"').strip("'")
            if "=" not in s:
                return s
        return ""
    return os.environ.get("HEYGEN_API_KEY", "").strip()


def http_get_json(path: str, key: str) -> Dict[str, Any]:
    req = urllib.request.Request(f"{HEYGEN_BASE}{path}", headers={"X-Api-Key": key, "Accept": "application/json"}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HeyGen API GET {path} -> HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:300]}") from e


def normalize_look(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": raw.get("id") or raw.get("look_id") or "",
        "name": raw.get("name") or "",
        "group_id": raw.get("group_id") or raw.get("avatar_group_id") or "",
        "preview_image_url": raw.get("preview_image_url") or raw.get("preview_url") or "",
        "engines": list(raw.get("supported_api_engines") or raw.get("engines") or []),
    }


def fetch_looks(key: str, group_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """GET /v3/avatars/looks[?group_id=...], theo con trỏ trang nếu có."""
    looks: List[Dict[str, Any]] = []
    token = None
    for _ in range(MAX_PAGES):
        q = {}
        if group_id:
            q["group_id"] = group_id
        if token:
            q["token"] = token
        res = http_get_json("/v3/avatars/looks" + (f"?{urllib.parse.urlencode(q)}" if q else ""), key)
        data = res.get("data")
        rows = data if isinstance(data, list) else (data or {}).get("looks") or res.get("looks") or []
        looks.extend(normalize_look(r) for r in rows if isinstance(r, dict))
        token = res.get("next_token") or (data.get("next_token") if isinstance(data, dict) else None)
        if not token or not res.get("has_more", True):
            break
    return [lk for lk in looks if lk["id"]]


def save_looks(looks: List[Dict[str, Any]], out: Path) -> None:
    out.write_text(json.dumps({"looks": looks}, ensure_ascii=False, indent=2), encoding="utf-8")


def load_looks(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = data.get("looks") if isinstance(data, dict) else data
    return [normalize_look(r) for r in rows or []]


def choose_engine(look: Dict[str, Any], preferred: Optional[str] = None) -> Optional[str]:
    """Trả engine để gửi kèm, hoặc None (để HeyGen dùng mặc định). Chỉ gửi engine look hỗ trợ."""
    engines = look.get("engines") or []
    if not engines:
        return preferred                     # chưa biết look hỗ trợ gì: chỉ gửi khi người dùng chỉ định rõ
    if preferred in engines:
        return preferred
    return None if preferred is None and "avatar_iv" in engines else engines[0]


def clamp_angles(n_angles: int, n_looks: int) -> int:
    return max(1, min(max(MIN_ANGLES, min(n_angles, MAX_ANGLES)), n_looks))


def pick_for_video(n_shots: int, look_ids: List[str], counts: Dict[str, int], n_angles: int = 3) -> List[str]:
    """Gán look cho n_shots shot A-roll của MỘT video: dùng ít góc nhất đã dùng trước (cân bằng cả lô),
    không để hai shot A-roll liền nhau cùng look (trừ khi chỉ có 1 look). Cập nhật `counts` tại chỗ."""
    if not look_ids:
        raise ValueError("Không có look nào để chia")
    order = {lid: i for i, lid in enumerate(look_ids)}
    k = clamp_angles(n_angles, len(look_ids))
    angles = sorted(look_ids, key=lambda lid: (counts.get(lid, 0), order[lid]))[:k]
    out: List[str] = []
    for _ in range(n_shots):
        cands = [a for a in angles if not out or a != out[-1]] or angles
        best = min(cands, key=lambda a: (counts.get(a, 0), order[a]))
        out.append(best)
        counts[best] = counts.get(best, 0) + 1
    return out


def pick_batch(videos: Dict[str, int], look_ids: List[str], n_angles: int = 3,
               counts: Optional[Dict[str, int]] = None) -> Dict[str, List[str]]:
    """Nhiều video: {tên video: số shot A-roll} -> {tên video: [look_id theo thứ tự shot]}, cân bằng số lần dùng mỗi look."""
    cnt = dict(counts or {})
    return {name: pick_for_video(n, look_ids, cnt, n_angles) for name, n in videos.items()}


def cmd_list(args: argparse.Namespace) -> int:
    key = load_key(args.key_file)
    if not key:
        print("[ERROR] Thiếu HEYGEN_API_KEY (biến môi trường) hoặc --key-file.")
        return 1
    looks = fetch_looks(key, None if args.all else args.group)
    for lk in looks:
        print(f"{lk['id']}  {lk['name']}  {lk['preview_image_url']}  engines={','.join(lk['engines']) or '?'}")
    save_looks(looks, args.out)
    print(f"{len(looks)} look -> {args.out}")
    return 0


def parse_videos(spec: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for part in spec.split(","):
        name, _, n = part.partition("=")
        out[name.strip()] = int(n)
    return out


def cmd_pick(args: argparse.Namespace) -> int:
    ids = [lk["id"] for lk in load_looks(args.looks)]
    res = pick_batch(parse_videos(args.videos), ids, args.angles)
    for name, seq in res.items():
        print(f"{name}: {' '.join(seq)}")
    if args.out:
        args.out.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Look (góc quay) HeyGen: liệt kê và chia cho shot A-roll.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list", help="Liệt kê look, ghi looks.json")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--group", help="avatar group id")
    g.add_argument("--all", action="store_true", help="mọi look của tài khoản")
    p.add_argument("--out", type=Path, default=Path("looks.json"))
    p.add_argument("--key-file", type=Path, default=None)
    p.set_defaults(fn=cmd_list)
    q = sub.add_parser("pick", help="Chia look cho shot A-roll (offline)")
    q.add_argument("--looks", type=Path, required=True)
    q.add_argument("--videos", required=True, help="VD: KB08=3,KB09=2 (số shot A-roll mỗi video)")
    q.add_argument("--angles", type=int, default=3, help="số góc mỗi video (2-4)")
    q.add_argument("--out", type=Path, default=None)
    q.set_defaults(fn=cmd_pick)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
