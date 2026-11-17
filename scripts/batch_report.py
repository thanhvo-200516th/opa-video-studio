#!/usr/bin/env python3
"""Một bảng cho cả lô (học từ ghost-editor finals.py HARD set): mỗi video PASS / WARN / HOLD kèm lý do và trang duyệt.

    python batch_report.py "<thư mục lô>" [--out <file.md>]

Đọc <video>/work/timing_v*.json (run_kb_v2152.py ghi) và <thư mục lô>/batch.jsonl.
HOLD (không giao): lần chạy cuối hỏng ở một bước, build lỗi, LUFS ngoài −16…−14, True Peak > −1,5 dBTP, QA SFX không đạt.
WARN: có mục lint SOFT hoặc audit chưa OK. Người duyệt chỉ cần mở FilmCraft cho video HOLD / WARN.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

LUFS_LO, LUFS_HI, TP_MAX = -16.2, -13.8, -1.5     # luật F3 (−16…−14 LUFS, ≤ −1,5 dBTP), dung sai 0,2 LU


def last_runs(ledger: Path) -> dict[str, list[dict]]:
    """Các dòng của lần chạy gần nhất mỗi video (một bước lặp lại = lần chạy mới)."""
    runs: dict[str, list[dict]] = {}
    if not ledger.is_file():
        return runs
    for ln in ledger.read_text(encoding="utf-8").splitlines():
        r = json.loads(ln)
        cur = runs.setdefault(r["video"], [])
        if any(x["stage"] == r["stage"] for x in cur):
            cur.clear()
        cur.append(r)
    return runs


def judge(video: Path, run: list[dict]) -> dict:
    tf = sorted(video.glob("work/timing_v*.json"), key=lambda p: p.stat().st_mtime)
    t = json.loads(tf[-1].read_text(encoding="utf-8")) if tf else {}
    hold, warn = [], []
    fail = next((r for r in run if r["status"] == "fail"), None)
    if fail:
        hold.append(f"hỏng ở {fail['stage']}: {fail['fail_code'][:120]}")
    if not t:
        hold.append("chưa có timing (chưa chạy run_kb)")
    elif not fail:
        if not t.get("build_ok"):
            hold.append(f"build lỗi {t.get('build_mismatches')}")
        m = re.search(r"I = (-?[\d.]+) LUFS.*True Peak = (-?[\d.]+) dBTP", t.get("qa_audio", ""))
        if not m:
            hold.append("thiếu đo loudness")
        else:
            i, tp = float(m.group(1)), float(m.group(2))
            if not LUFS_LO <= i <= LUFS_HI:
                hold.append(f"LUFS {i}")
            if tp > TP_MAX:
                hold.append(f"True Peak {tp}")
        if "ĐẠT" not in t.get("qa_sfx", ""):
            hold.append("QA SFX không đạt")
        warn += t.get("lint_soft", [])
        warn += [t["canh_bao_khung"]] if t.get("canh_bao_khung") else []
        warn += [re.sub(r"\s+", " ", x)[:80] for x in t.get("audit_loi", [])]
    status = "HOLD" if hold else "WARN" if warn else "PASS"
    return {"video": video.name, "status": status, "dur": t.get("duration_video"), "speed": t.get("toc_do"),
            "secs": t.get("tong_giay"), "why": hold or warn, "contact": t.get("contact")}


def apply_reuse(rows: list[dict], roots: list[Path]) -> list[str]:
    """Luật D8–D10 (media_reuse): D9 cảnh lệch kịch bản → HOLD; D8 / D10 dùng lại quá mức → WARN. Trả danh sách vi phạm."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from media_reuse import audit, code_of
    viol = audit(roots)["violations"]
    for r in rows:
        vc = code_of(r["video"]) or r["video"]
        mine = [v for v in viol if re.search(rf"\b{re.escape(vc)}\b", v["detail"])]
        if not mine:
            continue
        hold = [f"{v['rule']}: {v['detail']}" for v in mine if v["rule"] == "D9"]
        warn = [f"{v['rule']}: {v['detail']}" for v in mine if v["rule"] != "D9"]
        if hold:
            r["status"] = "HOLD"
            r["why"] = hold + (r["why"] if isinstance(r["why"], list) else [])
        elif warn and r["status"] == "PASS":
            r["status"] = "WARN"
            r["why"] = warn
        elif warn:
            r["why"] = list(r["why"]) + warn
    return [f"[{v['rule']}] {v['detail']}" for v in viol]


def report(batch: Path, reuse_roots: list[Path] | None = None) -> tuple[str, list[dict]]:
    runs = last_runs(batch / "batch.jsonl")
    vids = sorted(p for p in batch.iterdir() if p.is_dir() and (p / "work").is_dir())
    rows = [judge(v, runs.get(v.name, [])) for v in vids]
    reuse = apply_reuse(rows, reuse_roots) if reuse_roots else []
    n = {s: sum(r["status"] == s for r in rows) for s in ("PASS", "WARN", "HOLD")}
    out = [f"# Báo cáo lô {batch.name}", "",
           f"**{len(rows)} video** · PASS {n['PASS']} · WARN {n['WARN']} · HOLD {n['HOLD']} — chỉ mở FilmCraft cho WARN / HOLD.", "",
           "| Video | Trạng thái | Thời lượng | Tốc độ | Dựng (s) | Lý do | Trang duyệt |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        why = "; ".join(r["why"])[:220].replace("|", "/") or "–"
        link = f"[contact.jpg]({Path(r['contact']).relative_to(batch)})" if r["contact"] else "–"
        out.append(f"| {r['video'][:40]} | **{r['status']}** | {r['dur'] or '–'} s | {r['speed'] or '–'}x | {r['secs'] or '–'} | {why} | {link} |")
    if reuse:
        out += ["", f"## Dùng lại cảnh (D8 / D9 / D10) — {len(reuse)} vi phạm", ""] + [f"- {x}" for x in reuse[:60]]
    return "\n".join(out) + "\n", rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("batch")
    ap.add_argument("--out")
    ap.add_argument("--reuse-root", action="append", help="thư mục quét dùng lại cảnh (D8–D10); mặc định = thư mục cha của lô")
    ap.add_argument("--no-reuse", action="store_true")
    a = ap.parse_args()
    batch = Path(a.batch)
    roots = None if a.no_reuse else [Path(x) for x in (a.reuse_root or [str(batch.parent)])]
    md, rows = report(batch, roots)
    out = Path(a.out) if a.out else batch / "BAO_CAO_LO.md"
    out.write_text(md, encoding="utf-8")
    print(md)
    print(out)
    return 1 if any(r["status"] == "HOLD" for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
