"""thlib/plan_stage.py — sinh bản nháp và phép kiểm của stage PLAN (schema plan/1)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import broll_plan, candidates, compose, editschema, picture, plansheet, rules, segment, textmarks


def plan_inputs(project: Path | str, R: Any) -> dict:
    """{"words", "pauses", "script", "marks", "ctx", "cands", "meta"} — đọc và dựng một lần, dùng cho cả write_draft và check."""
    proj = Path(project)
    words = json.loads((proj / "words.json").read_text(encoding="utf-8"))
    pauses = json.loads((proj / "pauses.json").read_text(encoding="utf-8"))
    script_path = proj / "vo_script.txt"
    script = script_path.read_text(encoding="utf-8") if script_path.is_file() else None
    meta_path = proj / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}

    marks = textmarks.analyse(script, words, pauses, R)
    ctx = segment.make_ctx(words, pauses, script, R)
    cands = candidates.find_candidates(ctx)

    return {
        "words": words,
        "pauses": pauses,
        "script": script,
        "marks": marks,
        "ctx": ctx,
        "cands": cands,
        "meta": meta,
    }


def recommended(inp: dict, R: Any) -> dict:
    """Plan đề xuất đầy đủ (plan/2): recommended_plan + broll đề xuất theo meta.broll_class (spec 1.2.0 §4.6)."""
    words, pauses, script = inp["words"], inp["pauses"], inp["script"]
    rec = {**compose.draft_plan(inp["cands"], words), **candidates.recommended_plan(inp["cands"], inp["ctx"])}
    meta = inp.get("meta") or {}
    cls = meta.get("broll_class", "none")
    rec["broll"] = []
    if cls != "none":
        edit, _ = compose.compose({**rec, "broll": []}, words, pauses, script, R, _is_ref=True)
        t_end = picture._t_end(pauses, R)
        wins = broll_plan.windows(words, pauses, inp["marks"], t_end, R)
        rec["broll"] = broll_plan.recommend(wins, broll_plan.zones(edit, words, R), t_end,
                                            meta.get("broll_assets") or [], cls, R)
    return rec


def broll_table(inp: dict, rec: dict, R: Any) -> dict | None:
    """Dữ liệu mục §B của PLAN-SHEET (None khi broll_class none)."""
    meta = inp.get("meta") or {}
    cls = meta.get("broll_class", "none")
    if cls == "none":
        return None
    words, pauses, script = inp["words"], inp["pauses"], inp["script"]
    edit, _ = compose.compose({**rec, "broll": []}, words, pauses, script, R, _is_ref=True)
    t_end = picture._t_end(pauses, R)
    zs = broll_plan.zones(edit, words, R)
    assets = meta.get("broll_assets") or []
    wins = broll_plan.windows(words, pauses, inp["marks"], t_end, R)
    rows = []
    for w in wins:
        pts, asset = broll_plan.score(w, assets, R)
        rows.append({**w, "zone": broll_plan.hit(w, zs), "score": pts, "asset": asset})
    rec_ids = {x["id"] for x in rec.get("broll") or []}
    return {
        "class": cls,
        "rows": rows,
        "assets": assets,
        "t_end": t_end,
        "recommended": [x["id"] for x in rec.get("broll") or []],
        "floor": min(float(R.get("broll.cover_min")), broll_plan.achievable(wins, zs, t_end, R)),
        "cover_max": float(R.get("broll.cover_max")),
        "cap_n": int(t_end // float(R.get("broll.per_s"))),
        "gap": float(R.get("broll.gap_min_s")),
        "max_clips": int(R.get("broll.ai.max_clips")),
        "rec_cover": broll_plan.cover([w for w in wins if w["id"] in rec_ids], t_end),
    }


def write_draft(project: Path | str, R: Any) -> dict:
    """Ghi 3 file vào project: propose_edit.json (compose của bản đề xuất),
    plan.json (bản nháp của draft_plan — 6 ô "?"), PLAN-SHEET.md (render_sheet, truyền notes của compose).
    Trả metadata để stage in ra.
    """
    proj = Path(project)
    inp = plan_inputs(proj, R)
    words = inp["words"]
    pauses = inp["pauses"]
    script = inp["script"]
    marks = inp["marks"]
    ctx = inp["ctx"]
    cands = inp["cands"]

    rec_plan = recommended(inp, R)
    propose_edit, notes = compose.compose(rec_plan, words, pauses, script, R)

    # 1. propose_edit.json
    (proj / "propose_edit.json").write_text(
        json.dumps(propose_edit, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 2. plan.json — bản nháp 6 ô "?"; sau FACE_ROOM thì nạp sẵn plan của lần BUILD bị chặn (BUILD lưu ở
    # out/safe/face_room_plan.json) để sửa của các vòng trước không mất khi agent điền lại ô "?" theo §8.
    d_plan = compose.draft_plan(cands, words)
    room = proj / "out" / "safe" / "face_room.txt"
    room_lines = [l for l in room.read_text(encoding="utf-8").splitlines() if l.strip()] if room.exists() else []
    built_path = proj / "out" / "safe" / "face_room_plan.json"
    built = json.loads(built_path.read_text(encoding="utf-8")) if room_lines and built_path.exists() else None
    if built is not None and built.get("words_sha") != d_plan["words_sha"]:
        room_lines, built = [], None      # lời đã đổi sau lần BUILD đó ⇒ chỉ số từ trong FACE_ROOM không còn đúng
    (proj / "plan.json").write_text(
        json.dumps(built if built is not None else d_plan, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 3. PLAN-SHEET.md
    sheet_md = plansheet.render_sheet(cands, rec_plan, propose_edit, words, marks, R, notes=notes, broll=broll_table(inp, rec_plan, R))
    if room_lines:
        merge = ("GỘP các mảnh sau «Sửa:» dưới đây vào plan.json (breaks/hero là mảng: nối thêm phần tử; "
                 "\"steps\": null nghĩa là bỏ thẻ liệt kê — ghi đúng null, không đổi thành id).")
        if built is not None:
            how = ("BUILD đã chặn vì chữ đè vùng mặt. plan.json ĐÃ NẠP SẴN plan của lần BUILD bị chặn (khối JSON "
                   "cuối mục này — gồm mọi sửa của các vòng trước, không còn ô \"?\"); KHÔNG chép §8 hay điền lại "
                   "ô nào theo §8. Có dòng «GỘP SẴN» thì chỉ dán THAY đúng các ô trong dòng đó (mảng đầy đủ, đã gộp "
                   f"mọi «Sửa:» và chạy thử --check) — không tự gộp tay. Không có dòng đó thì {merge}")
        else:
            how = (f"BUILD đã chặn vì chữ đè vùng mặt. Chép khối §8 rồi {merge} Chép nguyên §8 không sửa là "
                   "dựng lại đúng bản đã bị chặn.")
        sheet_md = "\n".join([
            "## §0b Lỗi mặt từ BUILD lần trước — PHẢI sửa trước khi chạy --check",
            how,
            *[f"- {line}" for line in room_lines],
            *(["", "```json", json.dumps(built, ensure_ascii=False, indent=2), "```"] if built is not None else []),
        ]) + "\n\n" + sheet_md
    (proj / "PLAN-SHEET.md").write_text(sheet_md, encoding="utf-8")

    return {
        "propose": (proj / "propose_edit.json").as_posix(),
        "plan": (proj / "plan.json").as_posix(),
        "sheet": (proj / "PLAN-SHEET.md").as_posix(),
        "n_blocks": len(propose_edit.get("blocks", [])),
        "n_shots": len(propose_edit.get("shots", [])),
    }


def _find_stray_scripts(project_path: Path) -> list[str]:
    """Script lạ (*.py, *.ps1, *.sh, *.bat, *.cmd) dưới Vid Heygen/<n>/ — thứ agent có thể đã tự viết.
    Bỏ qua MỌI thư mục node_modules, ở bất kỳ độ sâu nào: `npm install` trên Windows sinh hàng trăm shim
    .cmd/.ps1 trong node_modules/.bin và agent không bao giờ viết vào đó. Cắt tỉa ngay khi duyệt (không đi
    xuyên vào) vì node_modules có hàng chục nghìn file. Bỏ qua thêm src/ của thư mục dựng edit-r*.
    """
    import os
    # project_path thường là Vid Heygen/<n>/edit-r<ver> hoặc Vid Heygen/<n>
    video_dir = project_path.parent if project_path.name.startswith("edit-r") else project_path
    exts = {".py", ".ps1", ".sh", ".bat", ".cmd"}
    strays: list[str] = []
    for root, dirs, files in os.walk(video_dir):
        here = Path(root)
        dirs[:] = [d for d in dirs
                   if d != "node_modules" and not (d == "src" and here.name.startswith("edit-r"))]
        strays += [(here / f).resolve().as_posix() for f in files if Path(f).suffix.lower() in exts]
    return sorted(strays)


def check(project: Path | str, R: Any) -> tuple[str, list[dict], dict]:
    """Chạy đúng bảy bước kiểm theo thứ tự.
    Bước nào FAIL thì dừng luôn, không chạy bước sau.
    Trả về ("PASS" | "FAIL", errors, metadata).
    """
    proj = Path(project)
    inp = plan_inputs(proj, R)
    words = inp["words"]
    pauses = inp["pauses"]
    script = inp["script"]
    marks = inp["marks"]
    ctx = inp["ctx"]
    cands = inp["cands"]

    # Bước 1: STRAY_SCRIPT
    strays = _find_stray_scripts(proj)
    if strays:
        errors = [
            {
                "code": "STRAY_SCRIPT",
                "where": "project",
                "msg": f"phát hiện script lạ không được phép: {', '.join(strays)}",
            }
        ]
        return "FAIL", errors, {}

    # Bước 2: Đọc plan.json; JSON hỏng => PLAN_JSON kèm dòng và cột
    plan_file = proj / "plan.json"
    if not plan_file.is_file():
        errors = [
            {
                "code": "PLAN_JSON",
                "where": "plan.json",
                "msg": f"không tìm thấy file {plan_file.as_posix()}",
            }
        ]
        return "FAIL", errors, {}

    content = plan_file.read_text(encoding="utf-8")
    try:
        plan = json.loads(content)
    except json.JSONDecodeError as exc:
        errors = [
            {
                "code": "PLAN_JSON",
                "where": f"dòng {exc.lineno}, cột {exc.colno}",
                "msg": f"JSON hỏng tại dòng {exc.lineno} cột {exc.colno}: {exc.msg}",
            }
        ]
        return "FAIL", errors, {}

    # Bước 3: check_plan phần PLAN_JSON, PLAN_UNDECIDED, PLAN_STALE
    all_plan_errs = compose.check_plan(plan, cands, words, pauses=pauses, R=R, script=script, meta=inp.get("meta"))
    step3_errs = [e for e in all_plan_errs if e.get("code") in ("PLAN_JSON", "PLAN_UNDECIDED", "PLAN_STALE")]
    if step3_errs:
        return "FAIL", step3_errs, {}

    # Bước 4: check_plan phần UNKNOWN_ID, HERO_RANGE
    step4_errs = [e for e in all_plan_errs if e.get("code") in ("UNKNOWN_ID", "HERO_RANGE")]
    if step4_errs:
        # Gắn gợi ý sửa nếu có
        suggestions = compose.repair_suggestions(plan, cands, words, pauses, script, R)
        if suggestions:
            fix_str = f" | Sửa: {suggestions[0]}"
            for se in step4_errs:
                se["msg"] = se["msg"] + fix_str
        return "FAIL", step4_errs, {}

    # Bước 4b: check_plan phần BROLL_*
    broll_errs = [e for e in all_plan_errs if e.get("code", "").startswith("BROLL_")]
    if broll_errs:
        return "FAIL", broll_errs, {}

    # Bước 5: compose(plan, ...) -> ghi edit.json
    try:
        edit, compose_notes = compose.compose(plan, words, pauses, script, R)
    except Exception as exc:
        errors = [
            {
                "code": "COMPOSE_ERROR",
                "where": "compose",
                "msg": f"Lỗi trong compose: {exc}",
            }
        ]
        return "FAIL", errors, {}

    (proj / "edit.json").write_text(
        json.dumps(edit, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Bước 6: validate + miễn trừ: reference = compose(plan đề xuất với hero=[], breaks=[])
    rec_plan = recommended(inp, R)
    ref_plan = dict(rec_plan, hero=[], breaks=[])
    ref_edit, _ = compose.compose(ref_plan, words, pauses, script, R, _is_ref=True)

    val_errors, val_notes = editschema.validate_with_notes(
        edit, words, pauses, R, marks=marks, reference=ref_edit, script=script
    )
    if val_errors:
        # Gắn thêm gợi ý sửa vào msg nếu có từ repair_suggestions
        suggestions = compose.repair_suggestions(plan, cands, words, pauses, script, R)
        if suggestions:
            fix_str = f" | Sửa: {suggestions[0]}"
            for ve in val_errors:
                ve["msg"] = ve["msg"] + fix_str
        return "FAIL", val_errors, {}

    # Bước 7: NO_EMPHASIS
    # video dài ≥ R.get("plan.emphasis_min_video_s") (30 giây) mà hook là null,
    # emphasis rỗng, vẫn còn ứng viên K/Q/H, và no_emphasis_reason rỗng ⇒ FAIL
    concerns: list[str] = []
    min_video_s = float(R.get("plan.emphasis_min_video_s"))

    duration_s = 0.0
    if words:
        duration_s = float(words[-1]["e"]) - float(words[0]["on"])

    has_remaining_cands = bool(cands.get("K") or cands.get("Q") or cands.get("H"))
    hook_is_null = plan.get("hook") is None
    emphasis_is_empty = not plan.get("emphasis")
    reason = (plan.get("no_emphasis_reason") or "").strip()

    if duration_s >= min_video_s and hook_is_null and emphasis_is_empty and has_remaining_cands:
        all_ids = [c["id"] for c in cands.get("H", []) + cands.get("K", []) + cands.get("Q", []) if "id" in c]
        if not reason:
            errors = [
                {
                    "code": "NO_EMPHASIS",
                    "where": "emphasis",
                    "msg": f"video dài {duration_s:.1f}s nhưng không có hook hay emphasis; các ứng viên còn bỏ: {', '.join(all_ids)}",
                }
            ]
            return "FAIL", errors, {}
        else:
            concerns.append(f"Video không có emphasis: {reason}")

    # Khi PASS
    # metadata gồm đúng các khoá: picks, plan_default, n_blocks, n_emphasis, n_notes, steps, hook, cta, off_pause_cuts, concerns.
    # plan_default = True khi plan.json trùng bản đề xuất của code (agent đồng ý nguyên khối §8).
    plan_default = (plan == rec_plan)

    picks = {
        "hook": plan.get("hook"),
        "emphasis": plan.get("emphasis", []),
        "steps": plan.get("steps"),
        "cta": plan.get("cta"),
    }

    n_blocks = len(edit.get("blocks", []))
    n_emphasis = len(plan.get("emphasis", []))
    n_notes = len(compose_notes) + len(val_notes)
    steps = plan.get("steps")
    hook = plan.get("hook")
    cta = plan.get("cta")

    # off_pause_cuts
    off_pause_cuts = 0
    pause_ranges = [(float(p[0]), float(p[1])) for p in pauses.get("pauses", [])]
    for s in edit.get("shots", []):
        cut_t = float(s.get("t", 0.0))
        # kiểm tra cut_t có nằm ngoài mọi pause
        in_pause = any(pa[0] <= cut_t <= pa[1] for pa in pause_ranges)
        if not in_pause:
            off_pause_cuts += 1

    metadata = {
        "picks": picks,
        "plan_default": plan_default,
        "n_blocks": n_blocks,
        "n_emphasis": n_emphasis,
        "n_notes": n_notes,
        "steps": steps,
        "hook": hook,
        "cta": cta,
        "off_pause_cuts": off_pause_cuts,
        "concerns": concerns,
    }

    return "PASS", [], metadata
