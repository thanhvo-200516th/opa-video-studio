"""thlib.scripts_v3 — parser cho ba tài liệu kịch bản (spec §6.0):
`60 kịch bản HeyGen v3` (lời chuẩn), file kịch bản đạo diễn, và file đánh
giá HYBRID/talking-head. Chỉ đọc, không ghi.
"""

from __future__ import annotations

import re
from pathlib import Path

# Tên hai file kịch bản còn lại trong DOCS_ROOT (file v3 tìm bằng find_v3_file).
DIRECTOR_FILENAME = "60-kich-ban-video-ngan-ai-vm-dabest.md"
EVAL_FILENAME = "60-kich-ban-heygen-talking-head.md"

_SECTION_RE = re.compile(r"^## (\d{2})\. (.*)$", re.MULTILINE)
_SCRIPT_RE = re.compile(r"### VIDEO SCRIPT\s*```text\n(.*?)```", re.DOTALL)
_MOTION_RE = re.compile(r"### APPLY CUSTOM MOTION\s*```text\n(.*?)```", re.DOTALL)
_PLACEHOLDER_RE = re.compile(r"\[[A-ZÀ-Ỹ0-9 _/\-]{3,}\]")
_PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n")

_DIRECTOR_RE = re.compile(r"^## Video (\d{2}) — (.*)$", re.MULTILINE)

_EVAL_ROW_RE = re.compile(
    r"^\| (\d{2})(?:–(\d{2}))? \| ([^|]+)\|([^|]+)\|([^|]+)\|([^|]*)\|", re.MULTILINE
)


def find_v3_file(docs_root) -> Path:
    """Tìm file "60 kịch bản HeyGen v3" trong `docs_root`: tên bắt đầu bằng
    "60 k" và có chứa "v3" (phân biệt với hai file "60-kich-ban-..." kia)."""
    for p in Path(docs_root).iterdir():
        if p.name.startswith("60 k") and "v3" in p.name:
            return p
    raise FileNotFoundError(f"Không tìm thấy file v3 trong {docs_root}")


def _section_body(text: str, matches: list[re.Match], i: int) -> str:
    start = matches[i].end()
    end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
    return text[start:end]


def load_v3(path) -> dict[int, dict]:
    """Tách 60 mục của file v3 thành dict theo số mục (n): title, script
    (VIDEO SCRIPT, đã bỏ APPLY CUSTOM MOTION), motion, placeholders,
    paragraphs (các khối không rỗng cách nhau bởi dòng trống)."""
    text = Path(path).read_text(encoding="utf-8")
    matches = list(_SECTION_RE.finditer(text))

    sections: dict[int, dict] = {}
    for i, m in enumerate(matches):
        n = int(m.group(1))
        title = m.group(2).strip()
        body = _section_body(text, matches, i)

        script_m = _SCRIPT_RE.search(body)
        motion_m = _MOTION_RE.search(body)
        script = script_m.group(1).strip() if script_m else ""
        motion = motion_m.group(1).strip() if motion_m else ""

        placeholders = _PLACEHOLDER_RE.findall(script)
        paragraphs = [p.strip() for p in _PARAGRAPH_SPLIT_RE.split(script) if p.strip()]

        sections[n] = {
            "n": n,
            "title": title,
            "script": script,
            "motion": motion,
            "placeholders": placeholders,
            "paragraphs": paragraphs,
        }
    return sections


def load_director(path) -> dict[int, dict]:
    """Tách file kịch bản đạo diễn thành dict theo số mục: title, body
    (nguyên văn giữa hai tiêu đề "## Video NN — ...")."""
    text = Path(path).read_text(encoding="utf-8")
    matches = list(_DIRECTOR_RE.finditer(text))

    sections: dict[int, dict] = {}
    for i, m in enumerate(matches):
        n = int(m.group(1))
        title = m.group(2).strip()
        body = _section_body(text, matches, i).strip()
        sections[n] = {"n": n, "title": title, "body": body}
    return sections


def load_eval(path) -> list[dict]:
    """Đọc bảng đánh giá HYBRID/talking-head; dòng gộp khoảng số (`43–50`)
    được nhân thành một entry cho mỗi số trong khoảng (đầu-cuối bao gồm)."""
    text = Path(path).read_text(encoding="utf-8")

    rows: list[dict] = []
    for m in _EVAL_ROW_RE.finditer(text):
        start = int(m.group(1))
        end = int(m.group(2)) if m.group(2) else start
        title = m.group(3).strip()
        verdict = m.group(4).strip()
        type_ = m.group(5).strip()
        note = m.group(6).strip()
        for row_n in range(start, end + 1):
            rows.append(
                {"row": row_n, "title": title, "verdict": verdict, "type": type_, "note": note}
            )
    return rows
