"""thlib.prep — phiếu chuẩn bị PREP (spec §7.1): khuôn `prep/prep-<k>.json`, kiểm, tra video
trong các phiếu, và dựng `PREP-SHEET.md` cho user duyệt.

Khuôn một phiếu:
    {"batch": "b01", "videos": [{"n", "status": ok|needs_rerender|needs_input, "reasons": [str],
      "broll_class": none|light|heavy, "assets": [{"desc", "anchor_quote", "kind", "owner":
      agent|user, "due": "YYYY-MM-DD"|null}], "claim_gate": bool, "claim_reasons": [str],
      "note"?: str}]}

Luật ngoài schema (spec §7.1, §7.2): status khác ok phải có lý do; claim_gate phải có lý do;
video `heavy` phải có asset và mọi asset của nó có mô tả + câu neo; video `none` không có asset.

PREP-SHEET in cạnh mỗi video tiêu đề mục v3, dòng đạo diễn, dòng phân loại đã ghép kèm điểm
(Ruling R14): gợi ý sai lộ ra ngay khi tiêu đề lệch nội dung video.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import jsonschema

from . import mapping, scripts_v3

KINDS = ("ai_image", "ai_video", "screen_rec", "real_output", "stock_context", "remotion_card")
_FILE_RE = re.compile(r"prep-([1-9]\d*)\.json")

SCHEMA = {
    "type": "object",
    "required": ["batch", "videos"],
    "additionalProperties": False,
    "properties": {
        "batch": {"type": "string", "minLength": 1},
        "videos": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/video"}},
    },
    "$defs": {
        "asset": {
            "type": "object",
            "required": ["desc", "anchor_quote", "kind", "owner", "due"],
            "additionalProperties": False,
            "properties": {
                "desc": {"type": "string"},
                "anchor_quote": {"type": "string"},
                "kind": {"enum": list(KINDS)},
                "owner": {"enum": ["agent", "user"]},
                "due": {"type": ["string", "null"], "pattern": r"^\d{4}-\d{2}-\d{2}$"},
            },
        },
        "video": {
            "type": "object",
            "required": ["n", "status", "reasons", "broll_class", "assets", "claim_gate", "claim_reasons"],
            "additionalProperties": False,
            "properties": {
                "n": {"type": "integer", "minimum": 1},
                "status": {"enum": ["ok", "needs_rerender", "needs_input"]},
                "reasons": {"type": "array", "items": {"type": "string", "minLength": 1}},
                "broll_class": {"enum": ["none", "light", "heavy"]},
                "assets": {"type": "array", "items": {"$ref": "#/$defs/asset"}},
                "claim_gate": {"type": "boolean"},
                "claim_reasons": {"type": "array", "items": {"type": "string", "minLength": 1}},
                "note": {"type": "string"},
            },
        },
    },
}


def _where(path) -> str:
    return "".join(f"[{p}]" if isinstance(p, int) else f".{p}" for p in path).lstrip(".") or "(gốc)"


def validate(data) -> list[str]:
    """Lỗi của một phiếu (rỗng = đạt). Luật ngoài schema chỉ chấm khi schema đã đạt."""
    errors = [f"{_where(e.absolute_path)}: {e.message}"
              for e in sorted(jsonschema.Draft202012Validator(SCHEMA).iter_errors(data),
                              key=lambda e: list(map(str, e.absolute_path)))]
    if errors:
        return errors
    seen: set[int] = set()
    for i, v in enumerate(data["videos"]):
        at = f"videos[{i}] (video {v['n']})"
        if v["n"] in seen:
            errors.append(f"{at}: video ghi hai lần trong phiếu")
        seen.add(v["n"])
        if v["status"] != "ok" and not v["reasons"]:
            errors.append(f"{at}: status {v['status']} phải kèm reasons (placeholder / motion / lời lệch …)")
        if v["claim_gate"] and not v["claim_reasons"]:
            errors.append(f"{at}: claim_gate true phải kèm claim_reasons")
        if v["broll_class"] == "none" and v["assets"]:
            errors.append(f"{at}: broll_class none thì assets phải rỗng")
        if v["broll_class"] == "heavy":
            if not v["claim_gate"]:
                errors.append(f"{at}: broll_class heavy phải bật claim_gate (R200: B-roll AI chỉ minh hoạ, không làm bằng chứng)")
            if not v["assets"]:
                errors.append(f"{at}: broll_class heavy phải có ít nhất một asset")
            for j, a in enumerate(v["assets"]):
                for key in ("desc", "anchor_quote"):
                    if not a[key].strip():
                        errors.append(f"{at}.assets[{j}]: asset của video heavy phải có {key}")
    return errors


def read(path: Path) -> tuple[dict | None, list[str]]:
    """(phiếu, lỗi) của một file prep; JSON hỏng ⇒ (None, [lỗi])."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, [f"không đọc được {Path(path).name}: {exc}"]
    return data, validate(data)


def load_all(batch_dir: Path) -> dict[int, tuple[dict | None, list[str]]]:
    """{k: (phiếu, lỗi)} của mọi `prep/prep-<k>.json` trong lô, sắp theo k."""
    found = {}
    for p in (Path(batch_dir) / "prep").glob("prep-*.json"):
        m = _FILE_RE.fullmatch(p.name)
        if m:
            found[int(m.group(1))] = read(p)
    return dict(sorted(found.items()))


def valid_videos(preps: dict) -> dict[int, dict]:
    """{n: mục video} từ các phiếu đạt kiểm (phiếu hỏng bị bỏ qua); video có ở nhiều phiếu thì
    phiếu k lớn nhất thắng (phiếu viết sau)."""
    out: dict[int, dict] = {}
    for k, (data, errors) in sorted(preps.items()):
        if data is not None and not errors:
            out.update({v["n"]: {**v, "k": k} for v in data["videos"]})
    return out


def mapping_rows(batch_dir: Path) -> dict[int, dict]:
    """Dòng mapping.csv của lô (intake.py, P0) theo số video; không có file ⇒ {}."""
    path = Path(batch_dir) / "mapping.csv"
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return {int(r["video"].split()[0]): r for r in csv.DictReader(fh)}


APPROVALS_MARK = "## Lời duyệt"                      # mục operator ghi lời user (intake.py tạo khung)
_ENTRY_HEAD = re.compile(r"- .*\b\d{4}-\d{2}-\d{2}\b")  # dòng đầu mục: "- <card/video> — <YYYY-MM-DD>…" (§3)


def approval_notes(batch_dir: Path, k: int) -> list[str]:
    """Các mục dưới "## Lời duyệt" của APPROVALS.md nhắc PREP-<k> (FS-3) — mỗi mục từ một dòng đầu
    mục "- … <YYYY-MM-DD> …" tới trước dòng đầu mục kế tiếp, nên lời user nguyên văn nhiều dòng (kể
    cả dòng gạch đầu "- " không có ngày) vẫn nguyên một mục (consistency-2); không có ⇒ []."""
    path = Path(batch_dir) / "APPROVALS.md"
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if APPROVALS_MARK not in text:
        return []
    entries: list[list[str]] = [[]]
    for line in text.split(APPROVALS_MARK, 1)[1].splitlines():
        if _ENTRY_HEAD.match(line):
            entries.append([])
        entries[-1].append(line)
    about = re.compile(rf"\bPREP-{k}\b")
    return ["\n".join(e).strip() for e in entries if about.search("\n".join(e))]


def load_docs(docs_root: Path) -> dict:
    """Ba tài liệu kịch bản (spec §6.0) để tra tiêu đề và chấm điểm gợi ý."""
    root = Path(docs_root)
    return {"sections": scripts_v3.load_v3(scripts_v3.find_v3_file(root)),
            "director": scripts_v3.load_director(root / scripts_v3.DIRECTOR_FILENAME),
            "eval_rows": scripts_v3.load_eval(root / scripts_v3.EVAL_FILENAME)}


def hint_lines(video: dict, docs: dict) -> list[str]:
    """Ba dòng gợi ý của một video trong batch_manifest: mục v3, dòng đạo diễn, dòng phân loại —
    tiêu đề kèm điểm ghép (R14)."""
    section = docs["sections"].get(video["v3"]) if video.get("v3") is not None else None
    if section is None:
        return ["mục v3: không ghép được", "đạo diễn: không ghép được — PREP tự phán đoán",
                "phân loại: không ghép được — PREP tự phán đoán"]
    d = docs["director"].get(video["director_row"]) if video.get("director_row") is not None else None
    e = next((r for r in docs["eval_rows"] if r["row"] == video.get("eval_row")), None)
    s = mapping.hint_scores(section, d, e)
    lines = ['mục v3 #%02d "%s" — điểm %.2f (mục nhì %.2f)'
             % (video["v3"], section["title"], video["score"], video["second_score"])]
    lines.append('đạo diễn #%02d "%s" — tiêu đề %.2f, lời %.2f'
                 % (video["director_row"], d["title"], s["director_title"], s["director_text"])
                 if d else "đạo diễn: không ghép được — PREP tự phán đoán")
    lines.append('phân loại #%02d "%s" — tiêu đề %.2f; %s; %s'
                 % (e["row"], e["title"], s["eval_title"], e["type"], e["note"] or "không ghi chú")
                 if e else "phân loại: không ghép được — PREP tự phán đoán")
    return lines


def _cell(text: str) -> str:
    return (text or "—").replace("|", "\\|").replace("\n", " ")


def _video_block(v: dict, manifest_v: dict | None, docs: dict) -> list[str]:
    head = "### Video %d — %s · B-roll %s · claim_gate %s" % (
        v["n"], v["status"], v["broll_class"], "có" if v["claim_gate"] else "không")
    out = [head]
    if manifest_v is None:
        out.append("- intake.py: video không có trong batch_manifest.json")
    else:
        flags = "; ".join(manifest_v["reasons"]) or "không cờ"
        out.append(f"- intake.py: {manifest_v['status']} ({flags})")
        out += [f"- gợi ý: {line}" for line in hint_lines(manifest_v, docs)]
    out.append("- lý do trạng thái: " + ("; ".join(v["reasons"]) or "—"))
    out.append("- claim: " + ("; ".join(v["claim_reasons"]) if v["claim_gate"] else "không"))
    if v.get("note"):
        out.append(f"- ghi chú: {v['note']}")
    if not v["assets"]:
        out.append("- asset: không có")
    else:
        out += ["", "| Mô tả | Câu neo | Loại | Ai làm | Hạn |", "|---|---|---|---|---|"]
        out += ["| %s | %s | %s | %s | %s |" % (_cell(a["desc"]), _cell(a["anchor_quote"]), a["kind"],
                                                a["owner"], a["due"] or "—") for a in v["assets"]]
    return out + [""]


def render_sheet(manifest: dict, preps: dict, docs: dict) -> str:
    """PREP-SHEET.md của cả lô từ mọi phiếu (tất định: phiếu theo k, video theo số)."""
    by_n = {v["n"]: v for v in manifest["videos"]}
    lines = [f"# PREP-SHEET — lô {manifest['batch']}", "",
             "Phiếu chuẩn bị cho user duyệt (spec §7). Dòng \"gợi ý\" do máy ghép theo nội dung: "
             "tiêu đề nào không đúng với video thì gợi ý đó sai — bỏ qua nó (Ruling R14).", ""]
    for k, (data, errors) in preps.items():
        if data is None or errors:
            lines += [f"## Phiếu {k} — chưa đạt check_prep", ""]
            continue
        videos = sorted(data["videos"], key=lambda v: v["n"])
        lines += [f"## Phiếu {k} — video {', '.join(str(v['n']) for v in videos)}", ""]
        for v in videos:
            lines += _video_block(v, by_n.get(v["n"]), docs)
    return "\n".join(lines).rstrip() + "\n"
