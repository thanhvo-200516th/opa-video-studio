"""collect_kpi.py — operator gom KPI một lô và lập danh sách video gửi user duyệt (spec §10.4,
§11.2, §11.3, §13.4; C8).

Dùng:
    PYTHONIOENCODING=utf-8 python collect_kpi.py --batch b01 [--prune-node-modules]

Với mỗi video trong _batches/<b>/batch_manifest.json có VID_ROOT/<n>/edit-r<ver>/out/verify/kpi.json:
ghi một dòng vào _batches/<b>/kpi.jsonl = kpi.json + batch, canary (chuỗi canary trong cards.json),
sample (mẫu 1/5 của batch_manifest.json, như APPROVALS.md), claim_gate (meta.json). Chạy lại thì
ghi đè cả file từ kpi.json hiện tại — không nhân đôi. In rồi mỗi video operator phải gửi user
(D5): canary, mẫu, mọi DONE_WITH_CONCERNS, mọi claim_gate — kèm đường dẫn final.mp4 và VERDICT.md;
video REJECTED và video chưa có kpi.json được liệt kê riêng (không gửi user).
--prune-node-modules (cuối lô, sau khi user duyệt xong mọi video D5): xoá node_modules của video
VERIFIED / DONE_WITH_CONCERNS — thư mục cài lại được, không đụng file nào khác.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from make_cards import registered_canary
from thlib import paths

DONE = ("VERIFIED", "DONE_WITH_CONCERNS")


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _review_reasons(line: dict) -> list[str]:
    """Lý do gửi user duyệt video này (D5, §11.2); rỗng = không cần gửi."""
    if line["verdict"] not in DONE:
        return []
    return [label for flag, label in ((line["canary"], "canary (duyệt ở APPROVE-CANARY)"),
                                      (line["sample"], "mẫu 1/5"),
                                      (line["verdict"] == "DONE_WITH_CONCERNS", "DONE_WITH_CONCERNS"),
                                      (line["claim_gate"], "claim_gate — không đăng trước khi user xác nhận"))
            if flag]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Gom kpi.json của một lô vào kpi.jsonl, in danh sách gửi user (D5)")
    ap.add_argument("--batch", required=True, help="Tên lô, vd b01")
    ap.add_argument("--prune-node-modules", action="store_true",
                    help="Cuối lô: xoá node_modules của video VERIFIED / DONE_WITH_CONCERNS (§13.4)")
    args = ap.parse_args(argv)

    batch = paths.batch_dir(args.batch)
    mpath = batch / "batch_manifest.json"
    if not mpath.is_file():
        print(f"FAIL: không có {mpath.as_posix()} — lô chưa qua intake.py")
        return 1
    manifest = _read(mpath)
    reg = _read(batch / "cards.json") if (batch / "cards.json").is_file() else {"cards": {}}
    canary = registered_canary(reg, args.batch)
    lines, pending = [], []
    for v in sorted(manifest["videos"], key=lambda v: v["n"]):
        project = paths.project_dir(v["n"], manifest["rules_version"])
        kpi = project / "out" / "verify" / "kpi.json"
        if not kpi.is_file():
            pending.append(f"video {v['n']} ({v['status']}): chưa có {kpi.as_posix()}")
            continue
        meta = _read(project / "meta.json") if (project / "meta.json").is_file() else {}
        lines.append({"batch": args.batch, **_read(kpi), "video": v["n"], "canary": v["n"] == canary,
                      "sample": bool(v.get("sample")), "claim_gate": bool(meta.get("claim_gate"))})
    out = batch / "kpi.jsonl"
    out.write_text("".join(json.dumps(ln, ensure_ascii=False) + "\n" for ln in lines), encoding="utf-8")

    sent = 0
    for ln in lines:
        project = paths.project_dir(ln["video"], manifest["rules_version"])
        reasons = _review_reasons(ln)
        if reasons:
            sent += 1
            print(f"GỬI USER: video {ln['video']} — {'; '.join(reasons)} — "
                  f"{(project / 'out' / 'final.mp4').as_posix()} + {(project / 'out' / 'verify' / 'VERDICT.md').as_posix()}")
        elif ln["verdict"] not in DONE:
            print(f"KHÔNG GỬI: video {ln['video']} {ln['verdict']} (owner_stage {ln['owner_stage']}) — mở lần thử "
                  "mới theo OPERATOR.md §4")
        if args.prune_node_modules and ln["verdict"] in DONE and (project / "node_modules").is_dir():
            shutil.rmtree(project / "node_modules")
            print(f"đã xoá {(project / 'node_modules').as_posix()}")
    for p in pending:
        print(f"CHƯA VERIFY: {p}")
    print(f"PASS: ghi {out.as_posix()} ({len(lines)} video); gửi user {sent} video")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # operator có thể quên PYTHONIOENCODING
    raise SystemExit(main())
