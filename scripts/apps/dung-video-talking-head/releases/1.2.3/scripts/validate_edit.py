"""validate_edit.py — cổng của stage PLAN: kiểm edit.json theo luật edit/1.1.

Dùng:
    PYTHONIOENCODING=utf-8 python validate_edit.py <project_dir>
    PYTHONIOENCODING=utf-8 python validate_edit.py <project_dir> --legacy <edit.json 1.0.0>
    PYTHONIOENCODING=utf-8 python validate_edit.py <project_dir> --plan <plan.json>

Đọc rules.lock (khoá version luật), words.json, pauses.json và edit.json của
dự án. Chế độ --legacy đổi một edit.json 1.0.0 (có giây) sang schema 1.1 rồi
kiểm bản đã đổi — chỉ số từ của file cũ phải ứng với words.json của dự án.
In từng lỗi theo mã (xem stages/PLAN.md) và thoát mã 1 khi còn lỗi.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from thlib import editschema, rules


def _load(path: Path) -> dict | list:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run(project: Path, legacy: str | None = None) -> tuple[str, list[dict]]:
    """Trả về (tên file đã kiểm, danh sách lỗi)."""
    name, errors, notes = run_with_notes(project, legacy)
    run.last_notes = notes
    return name, errors


def run_with_notes(project: Path, legacy: str | None = None) -> tuple[str, list[dict], list[dict]]:
    """Trả về (tên file đã kiểm, danh sách lỗi, danh sách ghi chú)."""
    project = Path(project)
    R = rules.load(project=project)
    words = _load(project / "words.json")
    pauses = _load(project / "pauses.json")

    script_path = project / "vo_script.txt"
    script = script_path.read_text(encoding="utf-8") if script_path.exists() else None

    if legacy:
        name = f"{Path(legacy).name} (đã đổi sang {editschema.SCHEMA_ID})"
        edit = editschema.from_legacy(_load(legacy), words)
        marks = None
        reference = None
    else:
        name = "edit.json"
        edit = _load(project / "edit.json")
        from thlib import textmarks
        marks = textmarks.analyse(script, words, pauses, R) if script is not None else None
        # Đọc propose_edit.json làm reference nếu có
        propose_path = project / "propose_edit.json"
        reference = (editschema.validate(_load(propose_path), words, pauses, R, marks=marks, script=script)
                     if propose_path.exists() else None)

    errors, notes = editschema.validate_with_notes(
        edit, words, pauses, R, marks=marks, reference=reference, script=script
    )
    return name, errors, notes


def run_plan(project: Path, plan_path: str) -> tuple[str, list[dict], list[dict]]:
    """--plan: ghép edit từ plan.json bằng compose rồi kiểm; miễn trừ theo bản đề xuất (hero=[], breaks=[])."""
    from thlib import compose, plan_stage
    project = Path(project)
    R = rules.load(project=project)
    inp = plan_stage.plan_inputs(project, R)
    words, pauses, script, marks = inp["words"], inp["pauses"], inp["script"], inp["marks"]
    plan = _load(plan_path)
    name = f"{Path(plan_path).name} (ghép bằng compose)"
    plan_errors = compose.check_plan(plan, inp["cands"], words)
    if plan_errors:
        return name, plan_errors, []
    edit, _ = compose.compose(plan, words, pauses, script, R)
    ref_edit, _ = compose.compose({**plan, "hero": [], "breaks": []}, words, pauses, script, R)
    reference = editschema.validate(ref_edit, words, pauses, R, marks=marks, script=script)
    errors, notes = editschema.validate_with_notes(
        edit, words, pauses, R, marks=marks, reference=reference, script=script
    )
    return name, errors, notes


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Kiểm edit.json theo luật edit/1.1")
    ap.add_argument(
        "project", help="Thư mục dự án (rules.lock, words.json, pauses.json, edit.json)"
    )
    ap.add_argument("--legacy", help="Kiểm một edit.json 1.0.0 sau khi đổi sang 1.1")
    ap.add_argument("--plan", help="Ghép edit từ plan.json bằng compose rồi kiểm (không cần edit.json)")
    args = ap.parse_args(argv)

    if args.plan:
        name, errors, notes = run_plan(Path(args.project), args.plan)
    else:
        name, errors, notes = run_with_notes(Path(args.project), args.legacy)
    if notes:
        for n in notes:
            print(f"GHI CHÚ: {n['code']:<17} {n['where']:<14} {n['msg']} ({n.get('note', '')})")

    if not errors:
        print(f"ĐẠT: {name} không vi phạm luật nào")
        return 0

    print(f"FAIL: {name} có {len(errors)} lỗi")
    for e in errors:
        print(f"  {e['code']:<21} {e['where']:<14} {e['msg']}")
    counts = Counter(e["code"] for e in errors)
    print("Tổng: " + ", ".join(f"{code} x{n}" for code, n in sorted(counts.items())))
    return 1




if __name__ == "__main__":
    raise SystemExit(main())
