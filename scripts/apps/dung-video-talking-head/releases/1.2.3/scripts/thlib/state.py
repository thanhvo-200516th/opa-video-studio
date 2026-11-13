"""thlib.state — rules.lock (khoá version luật) và STATE.md (chuỗi provenance).

STATE.md chỉ được ghi thêm (append-only) bởi append_state; không hàm nào ở đây
sửa hay xoá dòng cũ. Đây là file duy nhất được phép chứa wall-clock (Global
Constraints §Deterministic).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

from . import manifest, paths

SKILL_NAME = "dung-video-talking-head"
LOCK_FILENAME = "rules.lock"
STATE_FILENAME = "STATE.md"
_HEADER = "| time | stage | task/run | profile | release | files |\n"
_SEP = "|---|---|---|---|---|---|\n"


def sha256_file(p: Path) -> str:
    """SHA-256 (hex đầy đủ) của nội dung file p."""
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sha8(p: Path) -> str:
    """8 ký tự hex đầu của sha256_file(p) — dùng để ghi gọn vào STATE.md."""
    return sha256_file(p)[:8]


def write_lock(project: Path, ver: str) -> dict:
    """Ghi rules.lock ở gốc dự án, khoá skill + version luật đang dùng. sha MANIFEST tính như
    lint_rules/V1 kiểm lại (thlib.manifest.file_sha256, không phụ thuộc CRLF/LF)."""
    path = paths.release_dir(ver) / manifest.MANIFEST_NAME
    manifest_sha256 = manifest.file_sha256(path) if path.exists() else "dev"
    lock = {
        "skill": SKILL_NAME,
        "version": ver,
        "manifest_sha256": manifest_sha256,
    }
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    (project / LOCK_FILENAME).write_text(
        json.dumps(lock, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return lock


def read_lock(project: Path) -> dict:
    """Đọc lại rules.lock đã ghi bởi write_lock."""
    return json.loads((Path(project) / LOCK_FILENAME).read_text(encoding="utf-8"))


def append_state(
    project: Path,
    stage: str,
    task: str,
    run: str,
    profile: str,
    files: list[Path],
) -> str:
    """Nối một dòng provenance vào STATE.md; trả về đúng dòng vừa ghi."""
    project = Path(project)
    lock = read_lock(project)
    release_field = f"{lock['version']}@{lock['manifest_sha256'][:8]}"
    files_field = "; ".join(f"{Path(f).name}={sha8(Path(f))}" for f in files)
    time_field = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    row = (
        f"| {time_field} | {stage} | task={task} run={run} | "
        f"profile={profile} | release={release_field} | {files_field} |"
    )

    state_path = project / STATE_FILENAME
    if not state_path.exists():
        state_path.write_text(_HEADER + _SEP, encoding="utf-8")
    with state_path.open("a", encoding="utf-8") as fh:
        fh.write(row + "\n")
    return row


def read_state(project: Path) -> list[dict]:
    """Đọc STATE.md, parse từng dòng bảng thành dict (bỏ header + dòng phân cách)."""
    state_path = Path(project) / STATE_FILENAME
    if not state_path.exists():
        return []

    rows: list[dict] = []
    lines = state_path.read_text(encoding="utf-8").splitlines()
    for line in lines[2:]:
        line = line.strip()
        if not line:
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) != 6:
            continue
        time_s, stage, task_run, profile_s, release_s, files_s = cols
        task_part, run_part = task_run.split(" ", 1)
        files: dict[str, str] = {}
        if files_s:
            for item in files_s.split(";"):
                item = item.strip()
                if not item:
                    continue
                name, sha = item.split("=", 1)
                files[name.strip()] = sha.strip()
        rows.append(
            {
                "time": time_s,
                "stage": stage,
                "task": task_part.split("=", 1)[1],
                "run": run_part.split("=", 1)[1],
                "profile": profile_s.split("=", 1)[1],
                "release": release_s.split("=", 1)[1],
                "files": files,
            }
        )
    return rows
