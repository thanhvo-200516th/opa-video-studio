"""make_report.py — out/EDITOR-REPORT.md của BUILD (S23: sfx_plan và sfx_lint chép vào report).

Dùng: PYTHONIOENCODING=utf-8 python make_report.py <project_dir>

Đọc rules.lock → rules.json (ngưỡng), meta.json, words.json, picture_lock.json,
out/sfx_plan.json, out/sfx_lint.json, out/QA.json; ghi đúng các mục SECTIONS theo thứ tự:
đường dẫn; loudness ba bản xuất; đồng bộ (xcorr, lệch từng cue); bảng sfx_plan (mọi ứng
viên: id, vai, tầng, quyết định, luật, đỉnh, file, mức 3 miền); kết quả lint; lời chuẩn
(độ khớp, mọi từ guess); cảnh báo — của sfx_plan và của khoá hình (LAST_WORD_TIGHT,
display_shift_s từng từ, Ruling R31) cạnh nhau; claim gate; B-roll. Chỉ trình bày số đã
có, không đo lại. Thoát mã 1 khi thiếu file đầu vào.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from thlib import rules

SECTIONS = ("## Đường dẫn", "## PLAN", "## Loudness", "## Đồng bộ", "## SFX", "## Lint", "## Lời chuẩn",
            "## Cảnh báo", "## Claim gate", "## B-roll")
_OUTPUTS = (("final.mp4", "final_lufs", "bản chính"),
            ("final-nobgm.mp4", "final_lufs", "không nhạc nền — để gắn nhạc trend trên app"),
            ("final-social.mp4", "social_lufs", "bản mạng xã hội"))


def _read(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _cell(v) -> str:
    """Ô bảng markdown: None -> '—', '|' thoát để không vỡ cột."""
    return "—" if v is None else str(v).replace("|", "\\|")


def _row(*cells) -> str:
    return "| " + " | ".join(_cell(c) for c in cells) + " |"


def _table(head: tuple, rows: list) -> list[str]:
    return [_row(*head), "|" + "---|" * len(head), *rows]


def _paths(project: Path) -> list[str]:
    bed = (project / "public" / "bgm_bed.wav").exists()
    lines = [f"- Dự án: `{project.resolve().as_posix()}`"]
    for name, _, what in _OUTPUTS:
        lines.append(f"- `out/{name}` — {what}")
    lines.append("- Nhạc nền: " + ("có (`public/bgm_bed.wav`)" if bed else
                                   "không có — chưa chọn bài (gate 9); final.mp4 cùng tiếng final-nobgm.mp4"))
    lines.append("- Dữ liệu: `out/sfx_plan.json`, `out/sfx_lint.json`, `out/QA.json`, `picture_lock.json`")
    return lines


def _loudness(qa: dict, R) -> list[str]:
    L, rows = R.get("loudness"), []
    for name, key, _ in _OUTPUTS:
        got = qa["outputs"][name]
        rows.append(_row(name, "%.2f" % got["lufs"], "%.2f" % got["tp_dbtp"], "%.3f" % got["duration_s"],
                         got["attempts"], "%.2f" % got["ceiling_dbtp"],
                         "%g ±%g LUFS, TP ≤ %g" % (L[key], L["tol_lu"], L["tp_dbtp"])))
    note = ("- Limiter true-peak; TP đo trên bản đã mã hoá AAC, còn vượt thì hạ trần limiter rồi làm lại "
            "(R35). Social làm từ mix.wav lossless.")
    return _table(("Bản xuất", "LUFS", "TP (dBTP)", "Độ dài (s)", "Lần", "Trần limiter (dBTP)", "Đích"),
                  rows) + ["", note]


def _sync(qa: dict, R) -> list[str]:
    early, late = R.get("sfx.sync_tol_f.early"), R.get("sfx.sync_tol_f.late")
    lines = ["- xcorr(mix.wav, final.mp4): %+.3f ms (cho phép ±%g ms)"
             % (qa["xcorr_ms"], R.get("xcorr_max_ms")),
             f"- Lệch cue trên final.mp4 so với chỗ đã xếp (cho phép −{early}/+{late} f):", ""]
    rows = [_row(c["id"], c["role"], c["frame"], "%+.2f" % c["offset_f"]) for c in qa["cues"]]
    return lines + _table(("Cue", "Vai", "Frame", "Lệch (f)"), rows)


def _levels(cue: dict | None) -> str | None:
    if not cue:
        return None
    lv = cue["levels"]
    return "%.2f / %.2f / %.2f" % (lv["phone_k"], lv["k"], lv["phone_a"])


def _sfx(plan: dict) -> list[str]:
    ok = sum(1 for c in plan["candidates"] if c["decision"] == "OK")
    lines = [f"- Preset {plan['preset']}, ngân sách {plan['budget']} cue; {ok} cue OK / "
             f"{len(plan['candidates'])} ứng viên. Mức = đỉnh phone-K / K / phone-A so với VO_REF (dB).", ""]
    rows = [_row(c["id"], c["role"], c["tier"], c["decision"], c["rule"],
                 "%.4f s / f%d" % (c["cue"]["peak_s"], c["cue"]["frame"]) if c["cue"] else None,
                 c["cue"]["file"] if c["cue"] else None, _levels(c["cue"]))
            for c in plan["candidates"]]
    return lines + _table(("id", "Vai", "Tầng", "Quyết định", "Luật", "Đỉnh", "File", "Mức"), rows)


def _lint(results: list[dict]) -> list[str]:
    rows = [_row(r["code"], "PASS" if r["ok"] else "FAIL", r["frame"], r["msg"]) for r in results]
    return _table(("Mã", "Kết quả", "Frame", "Chi tiết"), rows)


def _script(meta: dict, words: list[dict], R) -> list[str]:
    match, need = meta.get("script_match"), R.get("mapping.script_pass")
    score = "—" if match is None else "%.4f" % match
    verdict = "—" if match is None else ("đạt" if match >= need else "DƯỚI NGƯỠNG — CONCERN")
    guesses = [w for w in words if w.get("guess")]
    lines = [f"- Độ khớp vo_script ↔ whisper: {score} (ngưỡng {need:g}) — {verdict}",
             f"- Từ đoán (guess: true): {len(guesses)}" + ("" if guesses else " — không có")]
    lines += ["  - #%d «%s» %.2f–%.2f s" % (w["i"], w["w"], w["s"], w["e"]) for w in guesses]
    return lines


def _plan(project: Path, R) -> list[str]:
    path = project / "plan.json"
    if not path.is_file():
        return ["- không có plan.json (dự án dựng bằng bản cũ)"]
    from thlib import compose, plan_stage
    plan = _read(path)
    inp = plan_stage.plan_inputs(project, R)
    _, notes = compose.compose(plan, inp["words"], inp["pauses"], inp["script"], R)
    picks = [f"hook={_cell(plan.get('hook'))}", f"emphasis={_cell(plan.get('emphasis'))}",
             f"steps={_cell(plan.get('steps'))}", f"cta={_cell(plan.get('cta'))}"]
    lines = ["- lựa chọn: " + ", ".join(picks), f"- số GHI CHÚ: {len(notes)}"]
    lines += [f"  - {n['code']} {n['where']}: {n['msg']}" for n in notes]
    if plan.get("flags"):
        lines += ["- flags của agent:"] + [f"  - {f}" for f in plan["flags"]]
    return lines


def _warnings(plan: dict, lock: dict) -> list[str]:
    shifts = [(b["id"], w) for b in lock["blocks"] for w in b["top"] + b["hero"] + b["bottom"]
              if "display_shift_s" in w]
    lines = ["- SFX (sfx_plan.warnings): " + (", ".join(plan["warnings"]) or "không có"),
             "- Khoá hình (picture_lock.warnings): " + (", ".join(lock.get("warnings") or []) or "không có"),
             "- Dời mốc hiện chữ (display_shift_s, R31):" + ("" if shifts else " không có")]
    lines += ["  - %s «%s» %+.3f s" % (bid, w["t"], w["display_shift_s"]) for bid, w in shifts]
    return lines


def _broll(meta: dict, edit: dict, project: Path) -> list[str]:
    broll_class = meta.get("broll_class")
    lines = [f"- broll_class: {_cell(broll_class)}"]
    slots = edit.get("broll") or []
    if not slots:
        return lines

    assets_file = project / "public" / "broll" / "assets.json"
    assets_data = _read(assets_file) if assets_file.is_file() else {}
    assets_map = {a.get("id"): a for a in assets_data.get("assets", [])}

    rows = []
    for s in slots:
        sid = s.get("id")
        entry = assets_map.get(sid, {})
        t_str = "%.3f–%.3f s" % (s.get("t_in", 0.0), s.get("t_out", 0.0))
        media = entry.get("media") or s.get("media")
        model = entry.get("model") or "—"
        prompt = s.get("prompt") or entry.get("prompt") or "—"
        f_name = entry.get("file") or "—"
        note = "ảnh thay clip" if entry.get("fallback") else "—"
        rows.append(_row(sid, t_str, media, model, prompt, f_name, note))

    table = _table(("id", "thời gian", "media", "model", "prompt", "file", "ghi chú"), rows)
    lines.append("")
    lines.extend(table)
    lines.append("")
    lines.append("- Bật nhãn nội dung AI khi đăng (TikTok / YouTube) — hình B-roll do AI tạo, chỉ minh hoạ.")

    if broll_class == "heavy":
        user_assets = [a.get("desc") or a.get("anchor_quote") or "asset"
                       for a in meta.get("broll_assets", [])
                       if a.get("owner") == "user"]
        if user_assets:
            lines.append(f"- Cảnh thật còn thiếu: {', '.join(user_assets)}")

    return lines


def render(project: Path) -> str:
    """Nội dung EDITOR-REPORT.md của `project`."""
    project = Path(project)
    R = rules.load(project=project)
    meta, words, lock = (_read(project / f) for f in ("meta.json", "words.json", "picture_lock.json"))
    plan, results, qa = (_read(project / "out" / f) for f in ("sfx_plan.json", "sfx_lint.json", "QA.json"))
    edit = _read(project / "edit.json") if (project / "edit.json").is_file() else {}
    claim = meta.get("claim_gate")
    body = {
        "## Đường dẫn": _paths(project),
        "## PLAN": _plan(project, R),
        "## Loudness": _loudness(qa, R),
        "## Đồng bộ": _sync(qa, R),
        "## SFX": _sfx(plan),
        "## Lint": _lint(results),
        "## Lời chuẩn": _script(meta, words, R),
        "## Cảnh báo": _warnings(plan, lock),
        "## Claim gate": ["- claim_gate: " + ("**có** — dựng xong nhưng không đăng trước khi user xác nhận"
                                             if claim else "không")],
        "## B-roll": _broll(meta, edit, project),
    }
    head = (f"# EDITOR-REPORT — video {_cell(meta.get('video'))} "
            f"(dung-video-talking-head@{R.version}, preset {plan['preset']})")
    lines = [head]
    for section in SECTIONS:
        lines += ["", section, "", *body[section]]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Ghi out/EDITOR-REPORT.md của bản dựng")
    ap.add_argument("project", help="Thư mục dự án edit-r<ver> (đã mux, có out/QA.json và out/sfx_lint.json)")
    project = Path(ap.parse_args(argv).project)
    try:
        text = render(project)
    except FileNotFoundError as exc:
        print(f"FAIL: thiếu file đầu vào của report: {exc.filename or exc}")
        return 1
    path = project / "out" / "EDITOR-REPORT.md"
    path.write_text(text, encoding="utf-8")
    print(f"KẾT QUẢ: đã ghi {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
