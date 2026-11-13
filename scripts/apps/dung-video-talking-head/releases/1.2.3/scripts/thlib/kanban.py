"""thlib.kanban — vỏ gọi Hermes CLI (`hermes kanban`) và khuôn thân card con trỏ.

Hai phần:
- `show`, `boards`, `create`: gọi hermes.exe ở process con, bỏ các dòng banner "⚠ … gateway …" mà CLI
  in trước JSON, rồi parse JSON. `create(..., dry_run=True)` không gọi CLI: trả lệnh sẽ chạy
  và một id giả `<khoá idempotency>` để card con tham chiếu.
- `format_body`, `parse_body`: thân card ba dòng (Data Contracts "Card body") do make_cards.py
  sinh và stage.py đọc lại. Lệch mẫu ⇒ CardError — stage.py block với lý do "card ngoài mẫu"
  (spec §10.2).
"""

from __future__ import annotations

import json
import os
import re
import subprocess

from . import state

HB = "C:/Users/Minh PC/AppData/Local/hermes/hermes-agent/venv/Scripts/hermes.exe"
STAGES = ("INTAKE", "PLAN", "BUILD", "VERIFY")      # 4 card mỗi video, đúng thứ tự chạy
_ERR_TAIL = 800                                     # số ký tự cuối của stderr đưa vào lỗi

_LINE1 = re.compile(r"VIDEO: (\d+(?:,\d+)*)\s+STAGE: (PREP-[1-9]\d*|%s)\s+RULES: %s@(\d+\.\d+\.\d+)"
                    % ("|".join(STAGES), re.escape(state.SKILL_NAME)))
_LINE2 = re.compile(r"PRESET: ([a-z]+)\s+ATTEMPT: a([1-9]\d*)")
_LINE3 = re.compile(r"BATCH: ([A-Za-z0-9_-]+)")


class KanbanError(RuntimeError):
    """Hermes CLI thoát mã ≠ 0 hoặc không in ra JSON đọc được."""


class CardError(ValueError):
    """Thân card không đúng khuôn ba dòng (card ngoài mẫu)."""


_BOARD_PINS = ("HERMES_KANBAN_DB", "HERMES_KANBAN_WORKSPACES_ROOT")   # env dispatcher gắn cho worker


def _run(argv: list[str]) -> subprocess.CompletedProcess:
    """Runner duy nhất gọi CLI thật — test thay hàm này, không bao giờ tạo card thật. Lệnh có --board
    bỏ HERMES_KANBAN_DB / HERMES_KANBAN_WORKSPACES_ROOT khỏi env: Hermes ưu tiên hai biến đó hơn
    --board, nên chạy trong env của worker sẽ ghi lạc vào board của worker (FS-9)."""
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    if "--board" in argv:
        env = {k: v for k, v in env.items() if k not in _BOARD_PINS}
    return subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)


def _strip_banner(text: str) -> str:
    """Bỏ banner CLI (dòng "⚠ A previous `hermes update` … gateways" và các dòng thụt lề đi kèm):
    stdout có JSON thì giữ từ dòng đầu tiên mở JSON ('{' hoặc '[' ở cột 0); không có JSON (stderr
    lỗi, vd. "no such task: <id>") thì chỉ bỏ các dòng banner."""
    lines = text.splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.startswith(("{", "["))), None)
    if start is not None:
        return "\n".join(lines[start:])
    kept, banner = [], False
    for ln in lines:
        banner = ln.startswith("⚠") or (banner and ln[:1].isspace())
        if not banner:
            kept.append(ln)
    return "\n".join(kept)


def _call_json(args: list[str]):
    proc = _run([HB, "kanban", *args])
    if proc.returncode != 0:
        err = _strip_banner(proc.stderr or "").strip() or proc.stdout or ""
        raise KanbanError("hermes kanban %s thoát mã %d: %s"
                          % (" ".join(args[:3]), proc.returncode, err[-_ERR_TAIL:]))
    text = _strip_banner(proc.stdout)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise KanbanError(f"hermes kanban {' '.join(args[:3])} không in JSON: {proc.stdout[-_ERR_TAIL:]}") from exc


def _board(board: str | None) -> list[str]:
    return ["--board", board] if board else []


def show(task_id: str, board: str | None) -> dict:
    """`hermes kanban [--board B] show <id> --json` → {"task": {…, "body"}, "parents", "children", …}."""
    return _call_json([*_board(board), "show", task_id, "--json"])


def boards() -> list[dict]:
    """`hermes kanban boards list --json` → [{"slug", "name", "archived", …}] (board chưa archive)."""
    return _call_json(["boards", "list", "--json"])


def create(board: str | None, title: str, body: str, assignee: str, parents: list[str],
           workspace: str | None, idem: str, skills: list[str], runtime: str | None,
           retries: int | None, goal_turns: int | None, model: str | None = None,
           initial_status: str | None = None, dry_run: bool = False) -> str | dict:
    """Tạo một card; trả id Hermes (hoặc id của card sẵn có cùng khoá idempotency). Cờ nào
    None/0 thì bỏ hẳn (card duyệt của user không có ngân sách, skill, workspace). goal_turns > 0
    ⇒ `--goal --goal-max-turns N` (Hermes bỏ qua goal-max-turns nếu thiếu --goal).
    `retries` = số lần thử lại SAU lần đầu (rules budgets.<stage>.retries); Hermes
    `--max-retries N` ngắt ở lần hỏng thứ N nên truyền retries + 1 (C2); None ⇒ bỏ cờ."""
    args = [*_board(board), "create", title, "--body", body, "--assignee", assignee]
    for parent in parents:
        args += ["--parent", parent]
    if workspace:
        args += ["--workspace", workspace]
    args += ["--idempotency-key", idem]
    for skill in skills:
        args += ["--skill", skill]
    if runtime:
        args += ["--max-runtime", runtime]
    if retries is not None:
        args += ["--max-retries", str(retries + 1)]
    if goal_turns:
        args += ["--goal", "--goal-max-turns", str(goal_turns)]
    if model:
        args += ["--model", model]
    if initial_status:
        args += ["--initial-status", initial_status]
    args.append("--json")
    if dry_run:
        return {"argv": [HB, "kanban", *args], "id": f"<{idem}>"}
    return _call_json(args)["id"]


def format_body(videos: list[int], stage: str, ver: str, preset: str, attempt: int, batch: str) -> str:
    """Thân card con trỏ ba dòng. `stage` là INTAKE/PLAN/BUILD/VERIFY hoặc PREP-<k>."""
    return (f"VIDEO: {','.join(str(n) for n in videos)}   STAGE: {stage}   "
            f"RULES: {state.SKILL_NAME}@{ver}\n"
            f"PRESET: {preset}   ATTEMPT: a{attempt}\n"
            f"BATCH: {batch}")


def parse_body(body: str) -> dict:
    """Đọc thân card → {"videos", "stage" (PREP|INTAKE|…), "prep_k" (int|None), "ver", "preset",
    "attempt", "batch"}. Ném CardError khi lệch khuôn: không đúng 3 dòng, sai skill, stage lạ,
    card stage video mà ghi nhiều video."""
    lines = [ln.strip() for ln in body.strip().splitlines()]
    if len(lines) != 3:
        raise CardError(f"thân card phải đúng 3 dòng, đang có {len(lines)}")
    m1, m2, m3 = _LINE1.fullmatch(lines[0]), _LINE2.fullmatch(lines[1]), _LINE3.fullmatch(lines[2])
    for m, line in ((m1, lines[0]), (m2, lines[1]), (m3, lines[2])):
        if m is None:
            raise CardError(f"dòng lệch mẫu: {line!r}")
    videos = [int(x) for x in m1.group(1).split(",")]
    stage = m1.group(2)
    prep_k = int(stage.split("-", 1)[1]) if stage.startswith("PREP-") else None
    if prep_k is None and len(videos) != 1:
        raise CardError(f"card {stage} chỉ được ghi một video, đang ghi {m1.group(1)}")
    return {"videos": videos, "stage": "PREP" if prep_k else stage, "prep_k": prep_k,
            "ver": m1.group(3), "preset": m2.group(1), "attempt": int(m2.group(2)),
            "batch": m3.group(1)}
