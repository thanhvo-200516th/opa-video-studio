#!/usr/bin/env python3
"""Bảng kế hoạch cả lô — DUYỆT 1, trước khi tốn credit HeyGen / Muse (mỗi video một dòng).

    python batch_plan.py "<thư mục lô>" [--out <file.md>]

Đọc <video>/00_storyboard_manifest.json + sổ luân phiên rotation.json (rotation.py plan). Mỗi video: câu hook,
từ chốt từng nhịp (landing_word), nhãn trung thực, ô luân phiên. Cờ cảnh báo:
  - nhịp có tầng đạo diễn nhưng thiếu landing_word / truth;
  - prompt B-roll có chữ số (Muse dễ vẽ số liệu bịa — số chỉ hiện bằng chữ dựng từ kịch bản);
  - chưa có ô luân phiên.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rotation  # noqa: E402

PALETTES = ["gold", "red", "cyan", "mint"]          # vòng màu chữ chính của gen_build_spec.py (accent_start = chỉ số bắt đầu)
SFX_CATALOG = rotation.CATALOG
# chữ số là thông số quay, không phải số liệu: 3D, 45 độ, 9:16, (2) đánh số, 18% (PiP)
# số liệu thật (Muse dễ vẽ sai): có đơn vị / tỉ lệ, hoặc từ 2 chữ số; đếm vật thể "1 clip", "3 ô" không tính
DATA_NUM = re.compile(r"\d+(?:[.,/]\d+)*\s*(?:%|[KkM]\b|triệu(?:/\w+)?|tỷ|nghìn|ngàn|views?|lượt\s+\w+|điểm|đ\b|\$)|\b\d{2,}(?:[.,]\d+)*\b(?:\s+\w+)?")
TECH_NUM = re.compile(r"\b\d+D\b|\d+\s*(?:độ|-?degree)|\d+:\d+|\(\d\)|\d+%\s*\(PiP\)|\b\d{3,4}x\d{3,4}\b", re.I)


def video_id(folder: str) -> str:
    m = re.search(r"(?:^|_)(KB\d+|OPA\d+|THCN\d+)(?:_|$)", folder)
    return m.group(1) if m else folder[:12]


def plan_row(video: Path, pairs: list) -> dict:
    man = json.loads((video / "00_storyboard_manifest.json").read_text(encoding="utf-8"))
    segs = man["segments"]
    vid = video_id(video.name)
    rot = rotation.entry(video.parent, vid)
    flags = []
    if any(s.get("belief") or s.get("landing_word") for s in segs):
        miss = [s["seq_prefix"] for s in segs if not (s.get("landing_word") and s.get("truth"))]
        if miss:
            flags.append(f"thiếu từ chốt / nhãn trung thực ở nhịp {', '.join(miss)}")
    nums = []
    for s in segs:
        if s.get("type") != "b-roll":
            continue
        hits = DATA_NUM.findall(TECH_NUM.sub("", (s.get("broll_prompt") or "").split("(Pure visual")[0]))
        if hits:
            nums.append(f"{s['seq_prefix']} «{'», «'.join(hits[:2])}»")
    if nums:
        flags.append("prompt B-roll có số liệu (Muse dễ vẽ sai — để số cho chữ dựng): " + "; ".join(nums))
    if not rot:
        flags.append("chưa có ô luân phiên (chạy rotation.py plan)")
    slots = "–"
    if rot:
        a, b = pairs[rot["opening_pair"] % len(pairs)]
        slots = (f"SFX mở đầu #{rot['opening_pair']} ({Path(a).stem[:18]} + {Path(b).stem[:18]}) · màu đầu "
                 f"{PALETTES[rot['accent_start'] % len(PALETTES)]} · chữ chính {', '.join(rot['key_kinds'][:3])}")
    landing = [f"{s['landing_word']}" + (f" [{s['truth']}]" if s.get("truth") else "") for s in segs if s.get("landing_word")]
    return {"video": vid, "title": man.get("title", video.name), "secs": round(sum(s.get("duration_sec", 0) for s in segs), 1),
            "n": len(segs), "hook": (segs[0].get("display_text") or "")[:90], "landing": landing, "slots": slots, "flags": flags}


def build(batch: Path) -> tuple[str, list[dict]]:
    pairs = json.loads(SFX_CATALOG.read_text(encoding="utf-8"))["opening"]["pairs"]
    vids = sorted(p for p in batch.iterdir() if (p / "00_storyboard_manifest.json").is_file())
    rows = [plan_row(v, pairs) for v in vids]
    out = [f"# Kế hoạch lô {batch.name} — DUYỆT trước khi tạo media", "",
           f"**{len(rows)} video** · {sum(bool(r['flags']) for r in rows)} video có cờ cần xem. "
           "Duyệt: câu hook, từ chốt, ô luân phiên. Font, glow, màu phụ đề, luật chuyển cảnh là bất biến — không xoay.", ""]
    for r in rows:
        out += [f"## {r['video']} · {r['title'][:80]}",
                f"- **Hook:** {r['hook']}",
                f"- **Nhịp:** {r['n']} · ~{r['secs']} s ở 1.0x",
                f"- **Từ chốt:** {' · '.join(r['landing']) if r['landing'] else '(chưa ghi — gen_build_spec tự chọn cụm dài nhất)'}",
                f"- **Luân phiên:** {r['slots']}"]
        out += [f"- ⚠️ {f}" for f in r["flags"]]
        out.append("")
    return "\n".join(out), rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("batch")
    ap.add_argument("--out")
    a = ap.parse_args()
    batch = Path(a.batch)
    md, rows = build(batch)
    out = Path(a.out) if a.out else batch / "BANG_KE_HOACH_LO.md"
    out.write_text(md + "\n", encoding="utf-8")
    print(md)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
