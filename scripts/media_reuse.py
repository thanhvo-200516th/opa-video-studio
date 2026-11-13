#!/usr/bin/env python3
"""Kiểm dùng lại cảnh chèn (B-roll) và cảnh quay thật trên nhiều video (luật D8–D10, người dùng chốt 2026-11-11).

  D8  mỗi cảnh B-roll xuất hiện TỐI ĐA 1 lần trong một video, và dùng cho TỐI ĐA 2 video khác nhau
  D9  B-roll phải đúng nội dung kịch bản: không dùng cảnh làm cho kịch bản khác (tên thư viện KBxx_Byy / OPAxx_…)
  D10 mỗi clip trong `Source/soucre thô` xuất hiện TỐI ĐA 2 lần trên toàn bộ các video

Nhận diện clip bằng dấu vân tay hình (3 khung 16x16 xám) nên bắt được cả bản đã mã hoá lại / tăng tốc.

    python media_reuse.py audit "<thư mục chứa video>" [...] [--json]      # quét mọi work/*.craft.json mới nhất
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np

LIB_DIRS = [Path("/home/vmiz/Thanh/Media/A huy/B-roll")]
SOURCE_RAW = Path("/home/vmiz/Thanh/Media/A huy/Source/soucre thô")
MAX_VIDEOS_PER_BROLL = 2
MAX_PER_VIDEO = 1
MAX_RAW_USES = 2
SAME = 0.05                      # đo 2026-11-11: cùng clip (kể cả mã hoá lại / 1.15x) ≤ 0,003; clip khác nhau ≥ 0,149
SAME_RAW = 0.005                 # cảnh quay thật cùng người cùng phòng giống nhau (0,011–0,025) → ngưỡng chặt, lấy cái gần nhất
CODE_RX = re.compile(r"(?:^|_)((?:KB|OPA|XM|THCN)\d+)(?:_|$)")
SKIP_TRACK = ("trans", "text", "Ảnh bìa", "band", "V2", "V3", "V4")


def _dur(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


@lru_cache(maxsize=None)
def fingerprint(path: str) -> np.ndarray | None:
    """3 khung (25 / 50 / 75 % thời lượng) thu 16x16 xám, chuẩn hoá trừ trung bình — so được bản mã hoá lại / tăng tốc."""
    d = _dur(Path(path))
    if d <= 0:
        return None
    out = []
    for f in (0.25, 0.5, 0.75):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{d * f:.2f}", "-i", path, "-frames:v", "1",
                              "-vf", "scale=16:16,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
        if len(raw) != 256:
            return None
        a = np.frombuffer(raw, np.uint8).astype(np.float32)
        out.append((a - a.mean()) / (a.std() + 1e-6))
    return np.concatenate(out)


def distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.abs(a - b)) / 4)


def code_of(name: str) -> str | None:
    m = CODE_RX.search(Path(name).stem)
    return m.group(1) if m else None


def library_index() -> list[tuple[str, str, np.ndarray]]:
    idx = []
    for d in LIB_DIRS:
        for p in sorted(d.glob("*.mp4")):
            fp = fingerprint(str(p))
            if fp is not None:
                idx.append((p.name, code_of(p.name) or "?", fp))
    return idx


def raw_index() -> list[tuple[str, float]]:
    return [(str(p), _dur(p)) for p in sorted(SOURCE_RAW.rglob("*")) if p.suffix.lower() in (".mp4", ".mov")]


def latest_spec(video_dir: Path) -> Path | None:
    specs = sorted((video_dir / "work").glob("*.craft.json"), key=lambda p: p.stat().st_mtime)
    return specs[-1] if specs else None


def resolve(src: str) -> str:
    """Spec cũ trỏ vào vị trí trước khi sắp xếp lại thư mục (A huy/30 VID → A huy/Kich_ban/30 VID)."""
    if Path(src).exists():
        return src
    alt = src.replace("/A huy/", "/A huy/Kich_ban/", 1)
    return alt if Path(alt).exists() else src


def uses_of(spec: dict) -> list[dict]:
    """Mỗi lần xuất hiện B-roll (V1 cảnh B-roll + lớp gfx_under), gộp các đoạn liền nhau / chồng nhau cùng file."""
    raw = []
    for t in spec.get("tracks", []):
        tn = t.get("name", "")
        if t.get("type") != "video" or tn.startswith(SKIP_TRACK):
            continue
        for c in t.get("clips", []):
            src, nm = resolve(c.get("src", "")), c.get("name", "")
            is_b = tn.startswith("gfx_under") or "b-roll" in Path(src).name.lower() or nm.lower().startswith("b-roll")
            if src and is_b and Path(src).suffix.lower() in (".mp4", ".mov"):
                raw.append({"src": src, "at": c["at"], "end": c["at"] + c["dur"]})
    raw.sort(key=lambda u: (u["src"], u["at"]))
    merged: list[dict] = []
    for u in raw:
        if merged and merged[-1]["src"] == u["src"] and u["at"] <= merged[-1]["end"] + 0.15:
            merged[-1]["end"] = max(merged[-1]["end"], u["end"])
        else:
            merged.append(dict(u))
    return merged


def live_files(video_dir: Path) -> list[Path]:
    m = video_dir / "00_storyboard_manifest.json"
    if not m.is_file():
        return []
    out = []
    for s in json.loads(m.read_text(encoding="utf-8"))["segments"]:
        if s.get("type") == "a-roll" and (s.get("api_routing") or {}).get("video_generator") == "live_shoot":
            p = video_dir / f"{s['seq_prefix']}_a-roll-{s['role_index']}.mp4"
            if p.exists():
                out.append(p)
    return out


def audit(roots: list[Path]) -> dict:
    lib = library_index()
    raws = raw_index()
    videos = sorted({p.parent.parent for r in roots for p in r.rglob("work/*.craft.json")})
    groups: list[dict] = []           # mỗi clip duy nhất (theo vân tay): {fp, name, origin, uses: [(video, at)]}
    raw_uses: dict[str, list[str]] = {}
    for v in videos:
        spec_p = latest_spec(v)
        if not spec_p:
            continue
        vcode = code_of(v.name) or v.name
        spec = json.loads(spec_p.read_text(encoding="utf-8"))
        for u in uses_of(spec):
            fp = fingerprint(u["src"])
            if fp is None:
                continue
            g = next((g for g in groups if distance(g["fp"], fp) <= SAME), None)
            if g is None:
                origin = next((c for n, c, f in lib if distance(f, fp) <= SAME), None) or code_of(Path(u["src"]).name)
                g = {"fp": fp, "name": Path(u["src"]).name, "origin": origin, "uses": []}
                groups.append(g)
            g["uses"].append((vcode, round(u["at"], 2)))
        for lf in live_files(v):
            d, fp = _dur(lf), fingerprint(str(lf))
            if fp is None:
                continue
            cands = [(distance(rf, fp), rp) for rp, rd in raws if abs(rd - d) <= 0.5
                     for rf in [fingerprint(rp)] if rf is not None]
            if cands and min(cands)[0] <= SAME_RAW:
                raw_uses.setdefault(min(cands)[1], []).append(f"{vcode}:{lf.name}")
    viol = []
    for g in groups:
        per = {}
        for vc, at in g["uses"]:
            per.setdefault(vc, []).append(at)
        for vc, ats in per.items():
            if len(ats) > MAX_PER_VIDEO:
                viol.append({"rule": "D8", "detail": f"{g['name']} xuất hiện {len(ats)} lần trong {vc} ({ats})"})
            if g["origin"] and g["origin"] != vc:
                viol.append({"rule": "D9", "detail": f"{vc} dùng cảnh của {g['origin']}: {g['name']} ở {ats} s"})
        if len(per) > MAX_VIDEOS_PER_BROLL:
            viol.append({"rule": "D8", "detail": f"{g['name']} dùng cho {len(per)} video: {', '.join(sorted(per))}"})
    for rp, vs in raw_uses.items():
        if len(vs) > MAX_RAW_USES:
            viol.append({"rule": "D10", "detail": f"{Path(rp).name} (soucre thô) dùng {len(vs)} lần: {', '.join(vs)}"})
    return {"videos": len(videos), "broll_clips": len(groups),
            "raw_uses": {Path(k).name: v for k, v in raw_uses.items()}, "violations": viol}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("audit")
    a.add_argument("roots", nargs="+")
    a.add_argument("--json", action="store_true")
    args = ap.parse_args()
    res = audit([Path(r) for r in args.roots])
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        print(f"{res['videos']} video · {res['broll_clips']} cảnh B-roll khác nhau · clip soucre thô dùng: {res['raw_uses']}")
        for v in res["violations"]:
            print(f"[{v['rule']}] {v['detail']}")
        print("ĐẠT" if not res["violations"] else f"{len(res['violations'])} vi phạm")
    return 1 if res["violations"] else 0


if __name__ == "__main__":
    sys.exit(main())
