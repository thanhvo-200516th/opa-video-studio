"""verify.py — cổng VERIFY (§11.1): chấm V1–V7 tất định trên một dự án đã BUILD
xong, đọc lại mọi thứ từ đĩa và từ đúng bản release đã khoá (rules.lock), không
tin số BUILD tự báo. Ghi out/verify/VERDICT.json, VERDICT.md, kpi.json.

Dùng: PYTHONIOENCODING=utf-8 python verify.py <project_dir> [--release-root <SKILL>]
      [--card-rules <skill>@<ver>]

`--card-rules` (tuỳ chọn): dòng `RULES:` trích từ thân card (vd
"dung-video-talking-head@1.1.1", Data Contracts "Card body") — nếu truyền vào,
V1 chấm thêm rules.lock khớp card (§11.1 "rules.lock khớp card"); bỏ trống nếu
chạy tay ngoài stage.py/không có card. stage.py (Task 14) là nơi tự đọc
`hermes kanban show` rồi truyền cờ này xuống.

VERDICT.json: {"verdict": "VERIFIED"|"DONE_WITH_CONCERNS"|"REJECTED",
"owner_stage": str|None, "checks": [{"id","ok","msg"}], "concerns": [str]}.
REJECTED khi bất kỳ mã V1–V7 nào FAIL; owner_stage lấy theo mã hỏng đầu tiên
(Mã → owner_stage, §10.5, thlib.verify.OWNER_STAGE). Không mã nào FAIL nhưng có
LOW_DENSITY / LAST_WORD_TIGHT / guess:true / độ khớp < mapping.script_pass /
CONCERN của V7 (chỉ khi ghép contact sheet gặp sự cố cơ học — không tự bịa khi
ghép thành công, verifier model tự xem ảnh sau) thì DONE_WITH_CONCERNS; ngược
lại VERIFIED. Thoát mã 1 khi REJECTED, 0 khi VERIFIED/DONE_WITH_CONCERNS
(VERDICT.json là nguồn quyết định thật, không phải mã thoát).

V7 phần model (§11.1): verifier xem contact_sheet.png, ghi nhận xét (nếu có) vào
out/verify/v7_concern.txt — trong vùng nó được ghi (§10.1) — rồi `stage.py VERIFY
--finalize` gọi `finalize()` gộp nhận xét đó vào VERDICT.json / VERDICT.md / kpi.json
(có nhận xét ⇒ DONE_WITH_CONCERNS).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from thlib import paths, verify

_VERDICT_KEYS = ("verdict", "owner_stage", "checks", "concerns", "info")
V7_CONCERN = Path("out") / "verify" / "v7_concern.txt"   # nhận xét contact sheet của verifier model
V7_PREFIX = "V7 (verifier xem contact sheet): "


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _render_md(result: dict) -> str:
    lines = [f"# VERDICT — {result['verdict']}", ""]
    if result["owner_stage"]:
        lines += [f"- owner_stage: **{result['owner_stage']}**", ""]
    lines += ["| Mã | Kết quả | Chi tiết |", "|---|---|---|"]
    lines += ["| %s | %s | %s |" % (c["id"], "PASS" if c["ok"] else "FAIL", c["msg"].replace("|", "\\|"))
              for c in result["checks"]]
    if result.get("info"):
        lines += ["", "## Ghi chú"] + [f"- {i}" for i in result["info"]]
    lines += ["", "## Concerns"]
    lines += [f"- {c}" for c in result["concerns"]] if result["concerns"] else ["- không có"]
    return "\n".join(lines) + "\n"


def _kpi(project: Path, result: dict) -> dict:
    meta_path = project / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
    return {
        "video": meta.get("video"),
        "verdict": result["verdict"],
        "owner_stage": result["owner_stage"],
        "checks_ok": sum(1 for c in result["checks"] if c["ok"]),
        "checks_total": len(result["checks"]),
        "fail_ids": [c["id"] for c in result["checks"] if not c["ok"]],
        "concerns": result["concerns"],
        "guess_count": meta.get("guess_count"),
        "script_match": meta.get("script_match"),
    }


def finalize(project: Path) -> dict:
    """V7: gộp nhận xét contact sheet của verifier (out/verify/v7_concern.txt, gộp khoảng trắng;
    thiếu hay rỗng = không có) vào VERDICT.json, VERDICT.md, kpi.json — đúng một concern V7,
    thay bản của lần finalize trước. Không REJECTED thì còn concern ⇒ DONE_WITH_CONCERNS, hết
    ⇒ VERIFIED (§11.1). Trả VERDICT mới."""
    project = Path(project)
    out_dir = project / "out" / "verify"
    result = json.loads((out_dir / "VERDICT.json").read_text(encoding="utf-8"))
    note_file = project / V7_CONCERN
    note = " ".join(note_file.read_text(encoding="utf-8").split()) if note_file.is_file() else ""
    concerns = [c for c in result["concerns"] if not c.startswith(V7_PREFIX)] + ([V7_PREFIX + note] if note else [])
    verdict = "REJECTED" if result["verdict"] == "REJECTED" else "DONE_WITH_CONCERNS" if concerns else "VERIFIED"
    result = {**{k: result.get(k, []) for k in _VERDICT_KEYS}, "verdict": verdict, "concerns": concerns}
    _write_json(out_dir / "VERDICT.json", result)
    (out_dir / "VERDICT.md").write_text(_render_md(result), encoding="utf-8")
    _write_json(out_dir / "kpi.json", _kpi(project, result))
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Chấm VERIFY V1–V7 (tất định) trên một dự án đã BUILD")
    ap.add_argument("project", help="Thư mục dự án edit-r<ver> đã BUILD xong")
    ap.add_argument("--release-root", default=str(paths.SKILL),
                    help="Gốc chứa releases/<ver>/scripts để nạp validate_edit/lint_sfx/"
                         "check_text_safe/make_report của đúng bản đã khoá (mặc định %(default)s)")
    ap.add_argument("--card-rules", default=None,
                    help="Dòng RULES: của card (vd dung-video-talking-head@1.1.1) để V1 chấm "
                         "thêm khớp card; bỏ qua chấm này nếu không truyền")
    args = ap.parse_args(argv)
    project = Path(args.project)

    try:
        result = verify.run(project, Path(args.release_root), card_rules=args.card_rules)
    except FileNotFoundError as exc:
        print(f"FAIL: thiếu file đầu vào của verify: {exc.filename or exc}")
        return 1

    out_dir = project / "out" / "verify"
    _write_json(out_dir / "VERDICT.json", {k: result.get(k, []) for k in _VERDICT_KEYS})
    (out_dir / "VERDICT.md").write_text(_render_md(result), encoding="utf-8")
    _write_json(out_dir / "kpi.json", _kpi(project, result))

    reporter_ready = next((c["ok"] for c in result["checks"] if c["id"] == "V6"), False)
    print("VERDICT: %s | checked %d | missing %d | reporter-ready %s"
          % (result["verdict"], len(result["checks"]), result["missing"], "yes" if reporter_ready else "no"))
    for c in result["checks"]:
        print("%-4s %s  %s" % (c["id"], "PASS" if c["ok"] else "FAIL", c["msg"]))
    for note in result["concerns"]:
        print("CONCERN " + note)
    print(f"KẾT QUẢ: đã ghi {out_dir}")
    return 1 if result["verdict"] == "REJECTED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
