"""stage.py — lối vào duy nhất của mỗi card con trỏ (spec §10.2): đọc thân card, khoá video,
chạy đúng một stage, ghi STATE.md, in giao thức 4 dòng.

Dùng (lệnh đầu tiên của mọi card):
    PYTHONIOENCODING=utf-8 python <skill>/releases/<ver>/scripts/stage.py <STAGE> --task <id card>
        [--check | --finalize] [--project <dir>] [--card-file <txt>]

<STAGE> ∈ PREP INTAKE PLAN BUILD VERIFY. `--check` chỉ cho PREP (check_prep + PREP-SHEET.md) và
PLAN (validate_edit); `--finalize` chỉ cho VERIFY — lượt 2 gộp nhận xét contact sheet của verifier
(out/verify/v7_concern.txt, V7) vào VERDICT. Id card = --task (worker lấy từ câu "work kanban task
<id>": Hermes xoá $HERMES_KANBAN_TASK/RUN_ID khỏi mọi lệnh terminal của worker, R42) hoặc
$HERMES_KANBAN_TASK (test/chạy tay); thân card đọc bằng `hermes kanban show <id> --json` (board
$HERMES_KANBAN_BOARD), run = run chưa kết thúc trong kết quả show; hoặc từ --card-file khi chạy
tay/kiểm thử (id "local" nếu không có --task). Không có id, hay id sai (sai khuôn t_<8 hex>, board
không có, hoặc trong worker không có run mở của $HERMES_PROFILE) ⇒ FAIL kèm lệnh chạy lại. Dự án mặc định
VID_ROOT/<n>/edit-r<ver>. Stage video giữ khoá VID_ROOT/<n>/.stage.lock (bận ⇒ BLOCK ngay);
whisper (INTAKE), BUILD và VERIFY (render stills của V2) giữ thêm khoá toàn máy
VID_ROOT/_batches/.heavy.lock (chờ tối đa HEAVY_WAIT_S, §10.6). Stage đạt thì nối một dòng
STATE.md (sha8 từng file đã ghi).

4 dòng cuối stdout luôn là:
    RESULT: PASS | FAIL | BLOCK
    NEXT: <việc tiếp theo>
    SUMMARY: <một câu, không có chữ số>
    METADATA: <JSON một dòng>
PASS = stage xong; FAIL = agent sửa file của chính mình rồi chạy lại (PREP/PLAN --check);
BLOCK = dừng card: gọi kanban_block với đúng kind và reason in ở NEXT — kind luôn là loại Hermes
nhận, giữ nguyên nguyên nhân (C3). Không card nào chạy goal mode (R43): stage.py gác việc complete —
chỉ NEXT của PASS cuối stage dặn gọi tool kanban_complete (summary = dòng SUMMARY; PREP/PLAN: dòng
"ĐẠT: …" + "RESULT: PASS"; metadata = JSON dòng METADATA); FAIL/BLOCK dặn không complete.
Mã thoát 0 / 1 / 2.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field
from pathlib import Path

import lint_rules
import verify
from check_text_safe import bin_name
from thlib import align, build, face, kanban, paths, plan_stage, prep, proc, rules, scripts_v3, state, voice
from thlib import audio as A

try:
    import msvcrt
except ImportError:                                  # ngoài Windows: khoá bằng flock
    msvcrt = None
    import fcntl

SCRIPTS = Path(__file__).resolve().parent            # releases/<ver>/scripts
REL = SCRIPTS.parent                                 # releases/<ver>
VERSION = REL.name
STAGE_NAMES = ("PREP", *kanban.STAGES)
HEAVY_WAIT_S = 600          # chờ khoá máy (whisper/render của card khác) tối đa 10 phút rồi BLOCK
LOCK_POLL_S = 2.0
PLAN_MAX_ROUNDS = 3         # §9, §10.5: validate_edit FAIL sau 3 vòng ⇒ block needs_input
PLAN_CHECKS = "plan_checks.json"                     # số vòng FAIL của PLAN --check, theo card
_TP_TOL_DB = 0.01           # sai số đo true peak lặp lại (như thlib.lint)
_TAIL = 1200                # số ký tự cuối của log lỗi process con đưa vào lý do block
_TRAILING_PUNCT = ",.!?…:;"                          # chế độ chỉ ASR: bỏ dấu câu cuối từ
# R47 — trần thời gian của process con nặng trong scaffold (quá hạn ⇒ thlib.proc giết cả cây,
# BLOCK transient); render/still của BUILD, VERIFY ở thlib.proc.
MASTER_TIMEOUT_S = 600      # ffmpeg mã hoá master
NPM_TIMEOUT_S = 900         # npm install của template
BROWSER_TIMEOUT_S = 900     # `remotion browser ensure` — tải Chrome headless một lần, ngoài khoá máy (FS-13)

WHISPER = {"model": "large-v3", "compute_type": "int8", "beam_size": 5}
FONT_PACK = Path("D:/MMO/Font/Cinematic fonts pack")
FONTS = {   # tên đích (fonts.tsx) ← đường dẫn trong font pack (bộ font 1.0.0, R17)
    "BeVietnamPro-Medium.ttf": "Font Việt hóa cinematic/Be_Vietnam_Pro/Be_Vietnam_Pro/BeVietnamPro-Medium.ttf",
    "BeVietnamPro-Bold.ttf": "Font Việt hóa cinematic/Be_Vietnam_Pro/Be_Vietnam_Pro/BeVietnamPro-Bold.ttf",
    "BeVietnamPro-Black.ttf": "Font Việt hóa cinematic/Be_Vietnam_Pro/Be_Vietnam_Pro/BeVietnamPro-Black.ttf",
    "BeVietnamPro-BlackItalic.ttf":
        "Font Việt hóa cinematic/Be_Vietnam_Pro/Be_Vietnam_Pro/BeVietnamPro-BlackItalic.ttf",
    "DTPhudu-Bold.otf": "DT-Phudu/Fonts Files/DTPhudu-Bold.otf",
    "DTPhudu-Black.otf": "DT-Phudu/Fonts Files/DTPhudu-Black.otf",
    "BebasNeue.otf": "Font Việt hóa cinematic/PS-Bebas-Neue-Regular-V1.1.otf",
    "Merolat.ttf": "Font Việt hóa cinematic/TF-Merolat-bs2kh4.ttf",
    "HeyMonday.ttf": "Font Việt hóa cinematic/TF-Hey-Monday-i0dzoo.ttf",
}
# master 1620×2880 (dư 1,5× để phóng không vỡ) — đúng lệnh ffmpeg của new_project.py 1.0.0
MASTER_ARGS = ["-vf", "scale=1620:2880:force_original_aspect_ratio=increase:flags=lanczos,crop=1620:2880",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-g", "30",
               "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]

SUMMARY = {   # câu SUMMARY mặc định khi BLOCK — không chứa chữ số (§10.2)
    "transient": "Card dừng vì video hoặc máy đang bận việc khác; operator chạy lại sau.",
    "needs_input": "Card dừng vì thiếu đầu vào hoặc cần user hay operator quyết định.",
    "capability": "Card dừng vì lỗi skill hoặc lỗi máy; cần dev xem trước khi chạy lại.",
}
CARD_SUMMARY = "Card dừng vì thân card không đúng mẫu hoặc không đọc được; operator cần xem lại card."
# C3 — loại block Hermes nhận (kanban_db.VALID_BLOCK_KINDS). Card tạo với --goal chỉ block được
# dependency | needs_input (tools/kanban_tools.py); R43 bỏ goal mode (budgets goal_turns = 0 mọi
# stage) nên GOAL_STAGES rỗng và mọi stage in đúng nguyên nhân (khoá bận ⇒ transient).
GOAL_STAGES: tuple[str, ...] = ()
GOAL_BLOCK_KINDS = ("dependency", "needs_input")
NO_COMPLETE = "Không complete card."                 # đầu NEXT của FAIL/BLOCK (R43, FS-5)


@dataclass
class Outcome:
    result: str                                      # PASS | FAIL | BLOCK
    next: str
    summary: str
    meta: dict = field(default_factory=dict)


class Block(Exception):
    """Dừng card. kind (nguyên nhân) ∈ transient | needs_input | capability (§10.5) — loại Hermes;
    card goal đổi sang loại nó được phép bằng `hermes_kind` khi in."""

    def __init__(self, kind: str, detail: str, summary: str | None = None, meta: dict | None = None):
        super().__init__(detail)
        self.kind, self.detail = kind, detail
        self.summary, self.meta = summary or SUMMARY[kind], meta or {}


def _card_error(detail: str) -> Block:
    """Thân card sai mẫu / không đọc được ⇒ needs_input (Hermes không có loại 'card', C3)."""
    return Block("needs_input", detail, CARD_SUMMARY)


TASK_ID = re.compile(r"t_[0-9a-f]{8}")               # id Hermes: "t_" + token_hex(4) (kanban_db)


class WrongTask(Exception):
    """--task không phải card worker này đang chạy (sai khuôn, board không có, hay không có run mở
    của $HERMES_PROFILE) ⇒ FAIL kèm lệnh chạy lại như khi thiếu id, không BLOCK: tool kanban_block
    luôn chặn card của chính worker nên block vì gõ nhầm id sẽ khoá card thật (R42)."""


def hermes_kind(stage: str, cause: str) -> str:
    """Loại block in cho worker: card goal (GOAL_STAGES — rỗng từ R43) chỉ dependency | needs_input
    — khoá bận ⇒ dependency, lỗi skill/máy ⇒ needs_input; card khác giữ nguyên nguyên nhân (C3)."""
    if stage in GOAL_STAGES and cause not in GOAL_BLOCK_KINDS:
        return "dependency" if cause == "transient" else "needs_input"
    return cause


def _blocked(stage: str, b: Block) -> Outcome:
    """Outcome BLOCK: NEXT ghi đúng kind cho kanban_block; reason giữ nguyên nhân cho operator/dev."""
    kind = hermes_kind(stage, b.kind)
    return Outcome("BLOCK", f'Block card: gọi kanban_block với kind="{kind}" và reason="{b.kind}: {b.detail}". '
                            "Không tự sửa file, không unblock.", b.summary, {"block": kind, "cause": b.kind, **b.meta})


class LockBusy(RuntimeError):
    """Khoá đang do process khác giữ."""


# ------------------------------------------------------------------ khoá


def _try_lock(fh) -> None:
    fh.seek(0)
    if msvcrt:
        msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def _unlock(fh) -> None:
    fh.seek(0)
    if msvcrt:
        msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


@contextmanager
def file_lock(path: Path, wait_s: float = 0.0):
    """Khoá độc quyền của hệ điều hành trên file `path` (tạo nếu chưa có). HĐH tự nhả khi process
    chết, nên card bị giết giữa chừng không để lại khoá treo. Bận quá `wait_s` giây ⇒ LockBusy."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + wait_s
    with open(path, "a+b") as fh:
        while True:
            try:
                _try_lock(fh)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise LockBusy(str(path)) from None
                time.sleep(LOCK_POLL_S)
        try:
            yield
        finally:
            _unlock(fh)


@contextmanager
def _heavy():
    """Khoá toàn máy quanh whisper và render (§10.6)."""
    lock = paths.VID_ROOT / "_batches" / ".heavy.lock"
    with ExitStack() as stack:
        try:
            stack.enter_context(file_lock(lock, HEAVY_WAIT_S))
        except LockBusy:
            raise Block("transient", f"khoá máy {lock.as_posix()} bận quá lâu (whisper/render của card khác)") from None
        yield


# ------------------------------------------------------------------ card, STATE, giao thức


def _open_run(shown: dict) -> dict | None:
    """Run đang chạy của card trong `hermes kanban show --json` (runs[].ended_at rỗng), None nếu không có."""
    runs = [r for r in shown.get("runs") or [] if isinstance(r, dict) and r.get("ended_at") is None]
    return runs[-1] if runs else None


def _read_card(card_file: str | None, task: str | None) -> dict:
    """Thân card đã parse + danh tính của lượt chạy: "task", "run", "profile" (dòng STATE.md, bộ
    đếm vòng PLAN) và "rerun" (cờ để lệnh in ở NEXT chép nguyên văn được)."""
    run = profile = None
    if card_file:
        try:
            body = Path(card_file).read_text(encoding="utf-8")
        except OSError as exc:
            raise _card_error(f"không đọc được --card-file: {exc}") from None
        rerun = [f'--card-file "{Path(card_file).absolute().as_posix()}"'] + (["--task", task] if task else [])
    else:
        if not TASK_ID.fullmatch(task):
            raise WrongTask(f"id card {task!r} sai khuôn (id Hermes là t_ và 8 chữ hex)")
        try:
            shown = kanban.show(task, os.environ.get("HERMES_KANBAN_BOARD") or None)
            body = shown["task"]["body"] or ""
        except kanban.KanbanError as exc:
            if "no such task" in str(exc):
                raise WrongTask(f"board không có card {task}") from None
            raise _card_error(f"không đọc được card {task}: {exc}") from None
        except (KeyError, TypeError) as exc:
            raise _card_error(f"không đọc được card {task}: {exc}") from None
        opened = _open_run(shown)
        if os.environ.get("HERMES_DELEGATED_CHILD_CONTEXT") == "1":     # lệnh terminal của worker Hermes
            me = (os.environ.get("HERMES_PROFILE") or "").strip().lower()
            if opened is None or str(opened.get("profile") or "").strip().lower() != me:
                raise WrongTask(f"card {task} không có lượt chạy đang mở của {me or '$HERMES_PROFILE'} "
                                "(id card cha hay card khác?)")
        if opened is not None:
            run, profile = opened.get("id"), opened.get("profile")
        rerun = ["--task", task]
    try:
        card = kanban.parse_body(body)
    except kanban.CardError as exc:
        raise _card_error(f"card ngoài mẫu — {exc}") from None
    if run is None:
        run = os.environ.get("HERMES_KANBAN_RUN_ID") or "0"
    return {**card, "task": task or "local", "run": str(run),
            "profile": profile or os.environ.get("HERMES_PROFILE") or "local", "rerun": rerun}


def _append(project: Path, card: dict, stage_name: str, files: list[Path]) -> None:
    state.append_state(project, stage_name, card["task"], card["run"], card["profile"], files)


def _require_rows(project: Path, owners: dict[str, str]) -> None:
    """Mỗi file đầu vào phải khớp sha8 với một dòng STATE.md của stage chủ nó (§10.4)."""
    rows = state.read_state(project)
    bad = []
    for name, owner in owners.items():
        path = project / name
        if not path.is_file():
            bad.append(f"thiếu {path.as_posix()}")
            continue
        sha = state.sha8(path)
        if not any(r["stage"] == owner and r["files"].get(name) == sha for r in rows):
            bad.append(f"{path.as_posix()} không khớp dòng nào của {owner} trong "
                       f"{(project / state.STATE_FILENAME).as_posix()}")
    if bad:
        raise Block("needs_input", "đầu vào chưa qua stage chủ của nó: " + "; ".join(bad))


def _lint_rules(project: Path) -> None:
    """Spec §4.3 + C10: rules.lock khớp release và từng file release khớp MANIFEST (INTAKE sau
    scaffold, PLAN, BUILD; VERIFY qua V1) — lệch là lỗi skill ⇒ BLOCK capability (dev)."""
    problems = lint_rules.lint(project)
    if problems:
        raise Block("capability", "lint_rules FAIL: " + "; ".join(problems))


def _read(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: Path, obj) -> None:
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def _tail(exc: Exception) -> str:
    extra = getattr(exc, "stderr", None) or getattr(exc, "output", None) or ""
    return (f"{exc} {extra}".strip())[-_TAIL:]


def _one_line(text: str) -> str:
    return " ".join(str(text).split())


def _timed_out(exc: subprocess.TimeoutExpired) -> str:
    """Lý do block khi một process con nặng quá trần thời gian (R47)."""
    cmd = exc.cmd if isinstance(exc.cmd, str) else " ".join(map(str, exc.cmd))
    limit = f"{exc.timeout:g} s" if exc.timeout else "trần thời gian"
    log = exc.output.decode("utf-8", "replace") if isinstance(exc.output, bytes) else exc.output or ""
    return (f"lệnh {_one_line(cmd)[:200]} chạy quá {limit} nên đã bị dừng cùng mọi process con"
            + (f" — log cuối: {_one_line(log)[-300:]}" if log.strip() else ""))


TASK_HINT = '<id trong câu "work kanban task …">'


def _cmd(card: dict | None, *args: str) -> str:
    """Lệnh chạy lại stage.py để agent chép nguyên văn — đường dẫn skill có dấu cách nên có ngoặc;
    luôn kèm --task <id> (hoặc --card-file khi chạy tay) của card đang chạy (R42)."""
    ident = card["rerun"] if card else ["--task", TASK_HINT]
    return f'python "{(SCRIPTS / "stage.py").as_posix()}" ' + " ".join([*args, *ident])


def _complete(summary: str = "dòng SUMMARY") -> str:
    """Cách complete card sau PASS cuối stage (R43, FS-5) — stage.py là cổng duy nhất cho complete."""
    return (f"gọi tool kanban_complete (không dùng lệnh terminal) với summary = {summary} (chép nguyên văn) "
            "và metadata = JSON của dòng METADATA (chép nguyên văn)")


PASS_SUMMARY = 'dòng "ĐẠT: …" in ở trên và dòng "RESULT: PASS"'     # PREP/PLAN --check


def _emit(out: Outcome, ctx: dict) -> int:
    meta = {**ctx, "result": out.result, **out.meta}
    print(f"RESULT: {out.result}")
    print(f"NEXT: {_one_line(out.next if out.result == 'PASS' else f'{NO_COMPLETE} {out.next}')}")
    print(f"SUMMARY: {_one_line(out.summary)}")
    print("METADATA: " + json.dumps(meta, ensure_ascii=False, separators=(",", ":"), default=str))
    sys.stdout.flush()
    return {"PASS": 0, "FAIL": 1, "BLOCK": 2}[out.result]


# ------------------------------------------------------------------ PREP


def _manifest(batch: Path) -> dict:
    path = batch / "batch_manifest.json"
    if not path.is_file():
        raise Block("needs_input", f"không có {path.as_posix()} — chạy intake.py (P0) cho lô trước")
    return _read(path)


def _prep(card: dict, check: bool) -> Outcome:
    batch = paths.batch_dir(card["batch"])
    manifest = _manifest(batch)
    by_n = {v["n"]: v for v in manifest["videos"]}
    unknown = [n for n in card["videos"] if n not in by_n]
    if unknown:
        raise _card_error(f"card ngoài mẫu — video {unknown} không có trong "
                          f"{(batch / 'batch_manifest.json').as_posix()}")
    out, docs = batch / "prep" / f"prep-{card['prep_k']}.json", prep.load_docs(paths.DOCS_ROOT)
    if check:
        return _prep_check(card, batch, manifest, docs, out)
    guide = (REL / "stages" / "PREP.md").as_posix()
    print(f"PREP-{card['prep_k']} — lô {card['batch']} — video {', '.join(map(str, card['videos']))}")
    print(f"Hướng dẫn: {guide}")
    print(f"mapping.csv: {(batch / 'mapping.csv').as_posix()}")
    print(f"Kịch bản đạo diễn: {(paths.DOCS_ROOT / scripts_v3.DIRECTOR_FILENAME).as_posix()}")
    print(f"Phân loại HYBRID/talking: {(paths.DOCS_ROOT / scripts_v3.EVAL_FILENAME).as_posix()}")
    print(f"Ghi phiếu vào: {out.as_posix()}")
    k, notes = card["prep_k"], prep.approval_notes(batch, card["prep_k"])      # FS-3
    print(f"Lời user về PREP-{k} ({(batch / 'APPROVALS.md').as_posix()}, mục \"{prep.APPROVALS_MARK}\"):")
    for line in "\n".join(notes).splitlines() or ["(chưa có)"]:
        print(f"  {line}")
    rows = prep.mapping_rows(batch)
    for n in card["videos"]:
        v, r = by_n[n], rows.get(n)
        print(f"\nVideo {n} — intake.py: {v['status']} ({'; '.join(v['reasons']) or 'không cờ'})")
        print("  lời chuẩn: " + ((batch / v["vo_script"]).as_posix() if v.get("vo_script")
                                 else "không có (chưa ghép được mục v3)"))
        if r:
            print(f"  mapping.csv: mục {r['best_v3']} ({r['score']}), mục nhì {r['second_v3']} "
                  f"({r['second_score']}), motion {r['motion_score']}, cờ: {r['flags'] or '—'}")
            print(f"  whisper nghe đầu video: \"{r['heard']}\"")
        for line in prep.hint_lines(v, docs):
            print(f"  gợi ý: {line}")
    retry = "" if card["attempt"] == 1 else f"Lần thử a{card['attempt']}: " + (
        f"sửa phiếu theo lời user về PREP-{k} in ở trên. " if notes
        else f"APPROVALS.md chưa có mục nào về PREP-{k}; làm lại phiếu theo PREP.md. ")
    return Outcome("PASS", f"Chưa complete card. {retry}Đọc {guide} và các file lời chuẩn ở trên, viết "
                           f"{out.as_posix()}, rồi chạy: " + _cmd(card, "PREP", "--check"),
                   "Đã in đầu vào của phiếu PREP; agent phân loại từng video rồi kiểm phiếu.",
                   {"prep_file": out.as_posix()})


def _prep_check(card: dict, batch: Path, manifest: dict, docs: dict, out: Path) -> Outcome:
    """check_prep trên phiếu của card + khớp lô và bộ video của card, rồi dựng PREP-SHEET.md."""
    k, check_cmd = card["prep_k"], _cmd(card, "PREP", "--check")
    if not out.is_file():
        return Outcome("FAIL", f"Chưa có {out.as_posix()} — viết phiếu theo {(REL / 'stages' / 'PREP.md').as_posix()} "
                               f"rồi chạy: {check_cmd}",
                       "Chưa có phiếu PREP, agent cần viết phiếu rồi kiểm lại.")
    data, errors = prep.read(out)
    if not errors:
        if data["batch"] != card["batch"]:
            errors.append(f"batch {data['batch']!r} khác lô của card {card['batch']!r}")
        got, want = sorted(v["n"] for v in data["videos"]), sorted(card["videos"])
        if got != want:
            errors.append(f"phiếu ghi video {got}, card giao video {want}")
    if errors:
        print(f"FAIL: {out.as_posix()} có {len(errors)} lỗi")
        for e in errors:
            print(f"  {e}")
        return Outcome("FAIL", f"Sửa đúng các lỗi in ở trên trong {out.as_posix()}, rồi chạy: {check_cmd}",
                       "Phiếu PREP còn lỗi khuôn, agent cần sửa rồi kiểm lại.", {"errors": len(errors)})
    sheet = batch / "PREP-SHEET.md"
    sheet.write_text(prep.render_sheet(manifest, prep.load_all(batch), docs), encoding="utf-8")
    print(f"ĐẠT: {out.as_posix()}; đã ghi {sheet.as_posix()}")
    return Outcome("PASS", f"Card PREP-{k} xong — {_complete(PASS_SUMMARY)}; operator gửi {sheet.as_posix()} cho "
                           f"user duyệt ở card APPROVE-PREP-{k}.",
                   "Phiếu PREP đạt khuôn, PREP-SHEET đã sẵn sàng cho user duyệt.",
                   {"prep_file": out.as_posix(), "sheet": sheet.as_posix()})


# ------------------------------------------------------------------ INTAKE


def scaffold(project: Path, source: Path, ver: str) -> None:
    """Dự án dựng từ template của release, như new_project.py 1.0.0: chép template (không đụng
    node_modules đã cài), bộ font đã kiểm dấu (R17), rules.lock, master 1620×2880 (mã hoá ra file
    tạm rồi mới đổi tên — có master.mp4 là đủ, chạy lại thì bỏ qua), npm install, rồi
    `remotion browser ensure` để BUILD không tải trình duyệt trong lúc giữ khoá máy (FS-13).
    Mỗi lệnh có trần thời gian (R47): quá hạn ⇒ subprocess.TimeoutExpired."""
    project = Path(project)
    missing = [rel for rel in FONTS.values() if not (FONT_PACK / rel).is_file()]
    if missing:
        raise RuntimeError(f"thiếu font trong {FONT_PACK.as_posix()}: " + ", ".join(missing))
    shutil.copytree(paths.release_dir(ver) / "template", project, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("node_modules"))
    fonts = project / "public" / "fonts"
    fonts.mkdir(parents=True, exist_ok=True)
    for dst, rel in FONTS.items():
        shutil.copy2(FONT_PACK / rel, fonts / dst)
    state.write_lock(project, ver)
    master = project / "public" / "master.mp4"
    if not master.is_file():
        tmp = master.with_name("_master.tmp.mp4")
        proc.run(["ffmpeg", "-v", "error", "-y", "-i", str(source), *MASTER_ARGS, str(tmp)],
                 check=True, capture_output=True, text=True, encoding="utf-8", errors="replace",
                 timeout=MASTER_TIMEOUT_S)
        tmp.replace(master)
    proc.run("npm install --no-audit --no-fund", cwd=project, shell=True, check=True,
             capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=NPM_TIMEOUT_S)
    proc.run([str(project / "node_modules" / ".bin" / bin_name("remotion")), "browser", "ensure"], cwd=project,
             check=True, capture_output=True, text=True, encoding="utf-8", errors="replace",
             timeout=BROWSER_TIMEOUT_S)


def transcribe_vo(wav: Path) -> list[dict]:
    """Whisper large-v3 (CPU int8, word_timestamps, vad_filter, beam 5) trên vo-clean → [{w, s, e}]."""
    from faster_whisper import WhisperModel          # nặng, chỉ nạp khi thật sự chạy
    model = WhisperModel(WHISPER["model"], device="cpu", compute_type=WHISPER["compute_type"])
    segs, _ = model.transcribe(str(wav), language="vi", word_timestamps=True, vad_filter=True,
                               beam_size=WHISPER["beam_size"], condition_on_previous_text=False)
    return [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)}
            for s in segs for w in (s.words or []) if w.word.strip()]


def _asr_words(heard: list[dict]) -> list[dict]:
    """Chế độ chỉ ASR (không có vo_script, §6.2): chữ = lời whisper, mọi từ guess:true."""
    kept = [(w["w"].rstrip(_TRAILING_PUNCT), w) for w in heard]
    return [{"i": k, "w": text, "s": w["s"], "e": w["e"], "src": "asr", "guess": True}
            for k, (text, w) in enumerate((t, w) for t, w in kept if t)]


def intake_core(project: Path, source: Path, R, n: int, preset: str, script: str | None,
                transcribe, prep_entry: dict) -> dict:
    """INTAKE lõi sau scaffold (§6.4): vo-clean.wav (S28), vo_script.txt, `transcribe(wav)` →
    [{w, s, e}], căn chữ, onset S04, khoảng ngắt, VO_REF, nhịp ngắt có chủ đích; ghi words.json,
    pauses.json, meta.json đúng Data Contracts, rồi track mặt một lần → face.json (1.1.1 §8.1).
    Trả {"qa", "heard", "words", "pauses", "meta", "face"}."""
    project, pub = Path(project), Path(project) / "public"
    qa = voice.vo_clear(Path(source), pub / "vo-clean.wav", R)
    heard = transcribe(pub / "vo-clean.wav")
    if not heard:
        raise Block("needs_input", f"whisper không nghe được từ nào trong {pub / 'vo-clean.wav'}")
    vo = A.decode_mono(pub / "vo-clean.wav")
    found = voice.find_pauses(vo, R)
    dur = len(vo) / A.SR
    if script is None:
        words, score, breaks = _asr_words(heard), None, []
    else:
        al = align.align(script, heard)
        words, score = al["words"], al["score"]
        breaks = align.designed_breaks(script, words)
        with open(project / "vo_script.txt", "w", encoding="utf-8", newline="\n") as fh:
            fh.write(script)                         # LF ⇒ sha file = sha lời trong batch_manifest
    words = [{**w, "on": on} for w, on in zip(words, voice.correct_onsets(words, found, R))]
    pauses = {"pauses": [[t0, t1] for t0, t1 in found], "designed_breaks": breaks,
              "vo_ref": voice.vo_ref(vo, R), "duration_s": dur,
              "last_word_end": voice.last_word_end(words, found, dur)}
    meta = {"video": n, "source": Path(source).as_posix(), "duration_s": dur, "rules_version": R.version,
            "preset": preset,
            "vo_script_sha256": state.sha256_file(project / "vo_script.txt") if script is not None else None,
            "script_match": score, "guess_count": sum(1 for w in words if w["guess"]),
            "voice_hf_ratio": qa["voice_hf_ratio"],
            "vo_qa": {k: qa[k] for k in ("tilt_db", "low_db", "lufs", "tp_dbtp")},
            "xcorr_ms": qa["xcorr_ms"], "broll_class": prep_entry["broll_class"],
            "broll_assets": prep_entry.get("assets") or [],
            "claim_gate": prep_entry["claim_gate"]}
    for name, obj in (("words.json", words), ("pauses.json", pauses), ("meta.json", meta)):
        _write_json(project / name, obj)
    return {"qa": qa, "heard": heard, "words": words, "pauses": pauses, "meta": meta,
            "face": face.intake(project, R)}


def _intake_gates(res: dict, R) -> list[tuple[str, bool, str]]:
    """(tên cổng, đạt, chi tiết) theo thứ tự chặn: QA vo-clean (S28, capability) → onset đơn điệu
    (S04, capability) → track mặt "mặt" (FACE_TRACK 1.1.1 §8.1, capability) → độ khớp lời chuẩn
    (needs_input)."""
    qa, V = res["qa"], R.get("voice")
    bad = []
    if abs(qa["lufs"] - V["target_lufs"]) > V["tol_lu"]:
        bad.append("I %.2f LUFS, cần %g ±%g" % (qa["lufs"], V["target_lufs"], V["tol_lu"]))
    if qa["tp_dbtp"] > V["tp_dbtp"] + _TP_TOL_DB:
        bad.append("TP %.2f dBTP > %g" % (qa["tp_dbtp"], V["tp_dbtp"]))
    if qa["tilt_db"] < V["tilt_min_db"]:
        bad.append("tilt %.2f dB < %g" % (qa["tilt_db"], V["tilt_min_db"]))
    if qa["low_db"] > V["low_max_db"]:
        bad.append("80–250 Hz %.2f dB > %g" % (qa["low_db"], V["low_max_db"]))
    if abs(qa["xcorr_ms"]) > V["xcorr_max_ms"]:
        bad.append("xcorr %.3f ms > %g" % (qa["xcorr_ms"], V["xcorr_max_ms"]))
    qa_msg = "; ".join(bad) or "I %.2f LUFS, TP %.2f dBTP, tilt %.2f dB, 80–250 Hz %.2f dB, xcorr %.3f ms" % (
        qa["lufs"], qa["tp_dbtp"], qa["tilt_db"], qa["low_db"], qa["xcorr_ms"])
    gap, on = R.get("audio.onset_mono_gap_s"), [w["on"] for w in res["words"]]
    jumps = [k for k in range(1, len(on)) if on[k] < on[k - 1] + gap - 1e-9]
    score, lo = res["meta"]["script_match"], R.get("mapping.script_min")
    match_ok = score is None or score >= lo
    match_msg = ("không có vo_script — chế độ chỉ ASR" if score is None else
                 "%.4f (PASS ≥ %g, CONCERN ≥ %g)" % (score, R.get("mapping.script_pass"), lo))
    return [("QA vo-clean (S28)", not bad, qa_msg),
            ("onset đơn điệu (S04)", not jumps, f"từ lùi mốc: {jumps[:10]}" if jumps else f"{len(on)} từ"),
            ("mặt (FACE_TRACK)", *face.gate(res["face"], R)),
            ("độ khớp lời chuẩn (§6.2)", match_ok, match_msg)]


def _asr_report(project: Path, res: dict, gates: list) -> Path:
    meta, pauses = res["meta"], res["pauses"]
    kinds = [b["kind"] for b in pauses["designed_breaks"]]
    guesses = [f"{w['i']}:{w['w']}" for w in res["words"] if w["guess"]]
    lines = [f"# ASR_REPORT — video {meta['video']}", "",
             f"- Nguồn: {meta['source']}",
             "- Whisper %s (%s, word_timestamps, vad_filter, beam %d) trên public/vo-clean.wav: %d từ"
             % (WHISPER["model"], WHISPER["compute_type"], WHISPER["beam_size"], len(res["heard"])),
             f"- Lời chuẩn: vo_script.txt, {len(res['words'])} từ hiển thị" if meta["script_match"] is not None
             else "- Lời chuẩn: không có — chế độ chỉ ASR, mọi từ guess:true (§6.2)",
             f"- Từ đoán (guess): {meta['guess_count']}" + (f" — {', '.join(guesses[:40])}" if guesses else ""),
             "- Khoảng ngắt: %d; nhịp ngắt có chủ đích: %d đoạn, %d dấu ba chấm"
             % (len(pauses["pauses"]), kinds.count("paragraph"), kinds.count("ellipsis")),
             "", "## Cổng INTAKE", "", "| Cổng | Kết quả | Chi tiết |", "|---|---|---|"]
    lines += [f"| {name} | {'PASS' if ok else 'FAIL'} | {msg} |" for name, ok, msg in gates]
    lines += ["", "## Lời whisper nghe được", "", " ".join(w["w"] for w in res["heard"]), ""]
    path = project / "ASR_REPORT.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _vo_script(batch: Path, video: dict, card: dict) -> str | None:
    """Lời chuẩn của video trong lô (None = ngoài 60 mục, chế độ chỉ ASR); lời bị sửa sau P0 ⇒ BLOCK
    kèm đúng lệnh an toàn (C6): intake --update chỉ video này (lời nghe lấy lại từ mapping.csv của
    lô), rồi make_cards --retry mở lần thử INTAKE mới — không chạy lại intake cả lô."""
    if not video.get("vo_script"):
        return None
    path = batch / video["vo_script"]
    if not path.is_file():
        raise Block("needs_input", f"thiếu lời chuẩn vo_script {path.as_posix()}")
    text = path.read_text(encoding="utf-8")
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != video.get("vo_script_sha256"):
        n, board = video["n"], os.environ.get("HERMES_KANBAN_BOARD") or "<board>"
        update = (f'python "{(SCRIPTS / "intake.py").as_posix()}" --batch {card["batch"]} --update --videos {n} '
                  f'--transcriber "cache:{(batch / "mapping.csv").as_posix()}" --preset {card["preset"]} '
                  f'--rules {card["ver"]}')
        retry = (f'python "{(SCRIPTS / "make_cards.py").as_posix()}" --batch {card["batch"]} --board {board} '
                 f"--retry {n}:INTAKE")
        raise Block("needs_input", f"vo_script {path.as_posix()} không khớp sha256 trong "
                                   f"{(batch / 'batch_manifest.json').as_posix()} (lời chuẩn bị sửa sau P0) — "
                                   f"operator hỏi user; user xác nhận lời chuẩn trong kịch bản v3 thì chạy đúng: "
                                   f"PYTHONIOENCODING=utf-8 {update} — rồi mở lần thử mới: {retry}")
    return text


def _intake(card: dict, project: Path, R, check: bool) -> Outcome:
    n, batch = card["videos"][0], paths.batch_dir(card["batch"])
    video = next((v for v in _manifest(batch)["videos"] if v["n"] == n), None)
    if video is None:
        raise Block("needs_input", f"video {n} không có trong {(batch / 'batch_manifest.json').as_posix()}")
    entry = prep.valid_videos(prep.load_all(batch)).get(n)
    if entry is None:
        raise Block("needs_input", f"chưa có phiếu PREP hợp lệ ghi video {n} ({(batch / 'prep').as_posix()}) — "
                                   "chạy PREP và chờ user duyệt")
    if entry["status"] != "ok":
        raise Block("needs_input", f"phiếu PREP-{entry['k']} ghi video {n} là {entry['status']} "
                                   f"({'; '.join(entry['reasons'])}) — chờ user xử lý")
    script = _vo_script(batch, video, card)
    source = Path(video["source"])
    if not source.is_file():
        raise Block("needs_input", f"không thấy video nguồn {source.as_posix()}")
    try:
        scaffold(project, source, VERSION)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        raise Block("capability", f"scaffold dự án lỗi: {_tail(exc)}") from None
    _lint_rules(project)                             # lock vừa ghi — lint vẫn băm lại file release (C10)

    def transcribe(wav: Path) -> list[dict]:
        with _heavy():
            return transcribe_vo(wav)
    try:
        res = intake_core(project, source, R, n, card["preset"], script, transcribe, entry)
    except RuntimeError as exc:                      # vd vo_clear: loudnorm không tuyến tính (S28)
        raise Block("capability", f"INTAKE lõi lỗi: {_tail(exc)}") from None
    gates = _intake_gates(res, R)
    report = _asr_report(project, res, gates)
    meta = res["meta"]
    info = {"script_match": meta["script_match"], "guess_count": meta["guess_count"],
            "words": len(res["words"]), "pauses": len(res["pauses"]["pauses"]), "xcorr_ms": meta["xcorr_ms"]}
    for name, ok, msg in gates:
        if not ok:
            kind = "needs_input" if name.startswith("độ khớp") else "capability"
            raise Block(kind, f"INTAKE FAIL cổng {name}: {msg} — xem {report.as_posix()}", meta=info)
    files = [project / f for f in ("words.json", "pauses.json", "meta.json", "face.json", "vo_script.txt",
                                   "ASR_REPORT.md")]
    _append(project, card, "INTAKE", [f for f in files if f.is_file()] + [project / "public" / "vo-clean.wav"])
    concern = meta["script_match"] is None or meta["script_match"] < R.get("mapping.script_pass") \
        or meta["guess_count"] > 0
    summary = ("INTAKE xong nhưng lời nghe được lệch lời chuẩn hoặc có từ đoán; VERIFY sẽ ghi CONCERN để user xem."
               if concern else "INTAKE xong: giọng sạch, lời chuẩn đã căn mốc và khoảng ngắt sẵn sàng cho PLAN.")
    return Outcome("PASS", f"Card INTAKE xong — {_complete()}; card PLAN của video này chạy tiếp.",
                   summary, {**info, "concern": concern})


# ------------------------------------------------------------------ PLAN, BUILD, VERIFY

_INTAKE_OWNED = dict.fromkeys(("words.json", "pauses.json", "meta.json", "face.json"), "INTAKE")


def _plan_fail_round(project: Path, task: str) -> int:
    """Đếm vòng PLAN --check FAIL theo id card `task` (card a2 là card khác nên đếm lại từ đầu)."""
    path = project / PLAN_CHECKS
    counts = _read(path) if path.is_file() else {}
    counts = {**counts, task: counts.get(task, 0) + 1}
    _write_json(path, counts)
    return counts[task]


def _plan(card: dict, project: Path, R, check: bool) -> Outcome:
    _require_rows(project, _INTAKE_OWNED)
    _lint_rules(project)
    guide = (REL / "stages" / "PLAN.md").as_posix()
    if check:
        return _plan_check(card, project, R, guide)
    meta = plan_stage.write_draft(project, R)
    sheet, plan = (project / "PLAN-SHEET.md").as_posix(), (project / "plan.json").as_posix()
    _append(project, card, "PLAN", [project / "propose_edit.json"])
    print(f"Sheet: {sheet}")
    print(f"Hướng dẫn: {guide}")
    return Outcome("PASS", f"Đọc {sheet}, điền 6 mục '?' trong {plan} (đồng ý đề xuất thì chép khối §8), "
                           f"rồi chạy: {_cmd(card, 'PLAN', '--check')}. Không sửa edit.json, không viết script."
                           + (" BUILD lần trước chặn FACE_ROOM — sửa theo mục §0b ở đầu PLAN-SHEET.md trước."
                              if (project / "out" / "safe" / "face_room.txt").exists() else ""),
                   "Đã sinh PLAN-SHEET.md và plan.json nháp; agent chọn trong plan.json rồi kiểm.",
                   meta)


def _plan_check(card: dict, project: Path, R, guide: str) -> Outcome:
    """plan_stage.check trên plan.json; đạt ⇒ dòng STATE PLAN; FAIL lần thứ PLAN_MAX_ROUNDS ⇒ BLOCK."""
    check_cmd, plan = _cmd(card, "PLAN", "--check"), (project / "plan.json").as_posix()
    sheet = (project / "PLAN-SHEET.md").as_posix()
    if not (project / "plan.json").is_file():
        stray = project.parent / "plan.json"         # C7: ghi theo đường dẫn tương đối từ cwd Vid Heygen/<n>
        moved = (f"Có file {stray.as_posix()} nằm ngoài thư mục dự án (ghi nhầm theo đường dẫn tương đối) — "
                 f"chuyển nó thành {plan}. " if stray.is_file() else "")
        return Outcome("FAIL", f"Chưa có {plan}. {moved}Đọc {sheet}, điền 6 mục '?' trong {plan} "
                               f"(đúng đường dẫn tuyệt đối này), rồi chạy: {check_cmd}",
                       "Chưa có plan.json, agent cần điền rồi kiểm lại.")
    verdict, errors, meta = plan_stage.check(project, R)
    if verdict == "PASS":
        print(f"ĐẠT: {plan} hợp lệ, edit.json đã ghép lại từ plan.json")
        _append(project, card, "PLAN", [project / "plan.json", project / "edit.json"])
        return Outcome("PASS", f"Card PLAN xong — {_complete(PASS_SUMMARY)}; card BUILD của video này chạy tiếp.",
                       "plan.json hợp lệ, edit.json ghép từ plan.json, sẵn sàng cho BUILD.", meta)
    print(f"FAIL: {plan} có {len(errors)} lỗi")
    for e in errors:
        print(f"  {e['code']:<16} | {e['where']:<12} | {e['msg']}")
    codes = sorted({e["code"] for e in errors})
    rounds = _plan_fail_round(project, card["task"])
    info = {"errors": len(errors), "codes": codes, "round": rounds}
    if rounds >= PLAN_MAX_ROUNDS:
        raise Block("needs_input", f"plan.json vẫn FAIL sau {rounds} vòng ({', '.join(codes)}) — chép nguyên văn "
                                   "danh sách lỗi vào comment; operator mở PLAN lần thử mới với model mạnh hơn",
                    "Card dừng vì plan.json vẫn sai sau số vòng sửa cho phép; operator mở lần thử mới.", info)
    return Outcome("FAIL", f"Sửa {plan}: dán đúng dòng 'Sửa:' ở trên (bảng mã trong {guide}), rồi chạy: {check_cmd} "
                           f"(còn {PLAN_MAX_ROUNDS - rounds} vòng)",
                   "plan.json còn lỗi, agent cần sửa rồi kiểm lại.", info)


def _build(card: dict, project: Path, R, check: bool) -> Outcome:
    _require_rows(project, {**_INTAKE_OWNED, "edit.json": "PLAN"})
    _lint_rules(project)
    preset = _read(project / "meta.json").get("preset")
    if preset != card["preset"]:
        raise _card_error(f"card ngoài mẫu — card ghi PRESET {card['preset']} nhưng "
                          f"{(project / 'meta.json').as_posix()} ghi {preset}")
    # R221: dòng PLAN do chính card BUILD này ghi = số vòng BUILD đã tự áp hero (giới hạn AUTO_HERO_MAX qua các lần chạy lại)
    prior = sum(1 for r in state.read_state(project) if r["stage"] == "PLAN" and r["task"] == card.get("task"))
    with _heavy():
        result = build.run(project, R, preset, on_replan=lambda files: _append(project, card, "PLAN", files),
                           auto_hero_round=prior)
    gate = result["failed_gate"]
    if result.get("auto_hero"):                                # R221: đã ghi dòng PLAN ⇒ agent chạy lại BUILD (≤ 420 s mỗi lần)
        return Outcome("FAIL", f"BUILD đã {result.get('msg')} vào plan.json và ghi dòng PLAN trong STATE.md — chạy lại đúng "
                               f"lệnh: {_cmd(card, 'BUILD')}",
                       "BUILD tự áp hero một hàng; agent chạy lại BUILD.", {"failed_gate": gate, "auto_hero": True})
    if gate == "text_safe" and not result.get("tool_error"):    # B3: lỗi công cụ ⇒ capability bên dưới
        raise Block("needs_input", "BUILD dừng ở cổng text_safe (chữ ra ngoài vùng an toàn) — owner PLAN hoặc "
                                   f"template; operator xem {(project / 'out' / 'safe' / 'text_safe.json').as_posix()}",
                    "Card dừng vì chữ ra ngoài vùng an toàn; operator chuyển cho PLAN hoặc dev.",
                    {"failed_gate": gate})
    if gate == "face_safe" and not result.get("tool_error"):   # FACE_ROOM: chữ đè vùng mặt — việc của PLAN
        video = card["videos"][0]
        raise Block("needs_input", f"BUILD dừng ở cổng face_safe (chữ đè vùng mặt, FACE_ROOM) — owner PLAN: "
                                   f"operator chạy make_cards.py … --retry {video}:PLAN; lần thử PLAN đó đọc "
                                   f"{(project / 'out' / 'safe' / 'face_room.txt').as_posix()} ở mục §0b của PLAN-SHEET.md",
                    "Card dừng vì chữ đè vùng mặt; operator mở lại PLAN để chọn lại thẻ/hero theo gợi ý FACE_ROOM.",
                    {"failed_gate": gate})
    if gate == "broll_assets" and not result.get("tool_error"):
        msg = result.get("msg") or ""
        if msg.startswith("BROLL_FLAT"):
            video = card["videos"][0]
            raise Block("needs_input", f"BUILD dừng ở cổng broll_assets — {msg} — owner PLAN: operator chạy make_cards.py … "
                                       f"--retry {video}:PLAN; lần thử PLAN đó đổi prompt hoặc tăng \"v\" của ô bị báo",
                        "Card dừng vì ảnh B-roll bị phẳng; operator mở lại PLAN để đổi prompt.", {"failed_gate": gate})
        raise Block("needs_input", f"BUILD dừng ở cổng broll_assets — {msg} — operator: kiểm mạng/hạn mức 9router rồi mở lại "
                                   "BUILD (asset đã tạo giữ trong bộ đệm, không tốn lại)",
                    "Card dừng vì không tạo được ảnh B-roll (mạng/hạn mức); operator xử lý rồi chạy lại.", {"failed_gate": gate})
    if gate is not None:
        raise Block("capability", f"BUILD dừng ở cổng {gate} (lỗi skill, log ở trên) — dev xem, video chờ",
                    meta={"failed_gate": gate})
    files = [Path(a) for a in result["artifacts"] if Path(a).is_file()]
    _append(project, card, "BUILD", files)
    return Outcome("PASS", f"Card BUILD xong — {_complete()}; card VERIFY của video này chạy tiếp.",
                   "BUILD xong: đủ ba bản xuất, lint âm thanh và loudness đều đạt.", {"artifacts": len(files)})


def _verdict(project: Path) -> tuple[dict, dict]:
    """(VERDICT.json, info METADATA) của VERIFY; REJECTED ⇒ BLOCK needs_input chỉ owner_stage."""
    out = project / "out" / "verify"
    v = _read(out / "VERDICT.json")
    info = {"verdict": v["verdict"], "owner_stage": v["owner_stage"], "concerns": len(v["concerns"])}
    if v["verdict"] == "REJECTED":
        raise Block("needs_input", f"VERIFY REJECTED, owner_stage {v['owner_stage']} — operator mở card mới cho stage "
                                   f"đó (xem {(out / 'VERDICT.md').as_posix()})",
                    "Card dừng vì video chưa đạt kiểm tra; operator mở lần thử mới cho stage được chỉ ra.", info)
    return v, info


def _append_verify(project: Path, card: dict) -> None:
    out = project / "out" / "verify"
    files = [out / f for f in ("VERDICT.json", "VERDICT.md", "kpi.json", "contact_sheet.png")]
    _append(project, card, "VERIFY", [f for f in files + [project / verify.V7_CONCERN] if f.is_file()])


def _verify(card: dict, project: Path, R, check: bool) -> Outcome:
    """Lượt 1: chấm V1–V7 tất định (verify.py), rồi NEXT bảo verifier xem contact sheet, ghi nhận xét
    vào out/verify/v7_concern.txt nếu có và chạy VERIFY --finalize (V7, §11.1)."""
    if not (project / state.LOCK_FILENAME).is_file():
        raise Block("needs_input", f"chưa có {(project / state.LOCK_FILENAME).as_posix()} — video chưa qua INTAKE")
    note = project.absolute() / verify.V7_CONCERN
    note.unlink(missing_ok=True)                     # nhận xét của lượt VERIFY trước không được gộp nhầm
    with _heavy():                                   # §10.6: V2 render stills (check_text_safe) như BUILD
        rc = verify.main([str(project), "--card-rules", f"{state.SKILL_NAME}@{card['ver']}"])
    out = project.absolute() / "out" / "verify"
    if not (out / "VERDICT.json").is_file():
        raise Block("capability", f"verify.py không ghi {(out / 'VERDICT.json').as_posix()} (mã thoát {rc})")
    _, info = _verdict(project)
    _append_verify(project, card)
    return Outcome("PASS", f"Mở {(out / 'contact_sheet.png').as_posix()} xem các khung hình. Thấy vấn đề thì ghi nhận "
                           f"xét (một đoạn, chỉ ghi, không sửa gì khác) vào {note.as_posix()}; không thấy gì thì không "
                           "tạo file đó. Tool xem ảnh báo lỗi hoặc không nhìn thấy ảnh thì ghi đúng một dòng "
                           f"`không xem được contact sheet: <lỗi>` vào {note.as_posix()} (VERDICT thành "
                           f"DONE_WITH_CONCERNS). Rồi chạy: {_cmd(card, 'VERIFY', '--finalize')} — chưa complete card "
                           "trước lệnh này.",
                   "Đã chấm tất định; verifier xem contact sheet rồi chốt kết luận bằng lệnh finalize.", info)


def _verify_finalize(card: dict, project: Path, R, check: bool) -> Outcome:
    """Lượt 2 (V7): gộp nhận xét contact sheet (out/verify/v7_concern.txt) vào VERDICT.json/.md và
    kpi.json — có nhận xét ⇒ DONE_WITH_CONCERNS — rồi ghi dòng STATE VERIFY."""
    verdict_file = project / "out" / "verify" / "VERDICT.json"
    if not verdict_file.is_file():
        raise Block("needs_input", f"chưa có {verdict_file.as_posix()} — chạy {_cmd(card, 'VERIFY')} trước --finalize")
    verify.finalize(project)
    v, info = _verdict(project)
    _append_verify(project, card)
    summary = ("VERIFY xong: video đạt mọi kiểm tra tất định." if v["verdict"] == "VERIFIED"
               else "VERIFY xong nhưng có điểm cần user xem trước khi đăng.")
    return Outcome("PASS", f"Card VERIFY xong — {_complete()}.", summary,
                   {**info, "v7_concern": (project / verify.V7_CONCERN).is_file()})


_HANDLERS = {"INTAKE": _intake, "PLAN": _plan, "BUILD": _build, "VERIFY": _verify}


# ------------------------------------------------------------------ điều phối


def _dispatch(args, ctx: dict) -> Outcome:
    task = args.task or os.environ.get("HERMES_KANBAN_TASK") or None
    flags = [f for f, on in (("--check", args.check), ("--finalize", args.finalize)) if on]
    if not task and not args.card_file:              # R42: không đoán id (không `hermes kanban list`)
        return Outcome("FAIL", "stage.py chưa biết id card — chạy lại: " + _cmd(None, args.stage, *flags),
                       "Lệnh stage.py thiếu id card, cần chạy lại kèm id trong câu giao việc.")
    try:
        card = _read_card(args.card_file, task)
    except WrongTask as exc:
        return Outcome("FAIL", f"{exc} — chạy lại: " + _cmd(None, args.stage, *flags),
                       "Id card trong lệnh stage.py không phải card đang chạy, cần chạy lại đúng id trong câu giao việc.")
    ctx.update(task=card["task"], videos=card["videos"], batch=card["batch"], attempt=card["attempt"])
    card_stage = f"PREP-{card['prep_k']}" if card["prep_k"] else card["stage"]
    if card["stage"] != args.stage:                   # lỗi của lệnh, không phải của card ⇒ FAIL, không BLOCK
        return Outcome("FAIL", f"card ghi STAGE {card_stage}, lệnh vừa chạy {args.stage} — chạy lại: "
                       + _cmd(card, card["stage"]), "Lệnh stage.py sai tên stage, cần chạy lại đúng stage của card.")
    if card["ver"] != VERSION:
        raise _card_error(f"card ngoài mẫu — card ghi RULES @{card['ver']} nhưng stage.py thuộc bản {VERSION}")
    R = rules.load(VERSION)
    if card["preset"] not in R.get("presets"):
        raise _card_error(f"card ngoài mẫu — preset {card['preset']!r} không có trong {(REL / 'rules.json').as_posix()}")
    if args.check and args.stage not in ("PREP", "PLAN"):
        return Outcome("FAIL", "Cờ --check chỉ dùng cho PREP và PLAN — chạy lại: " + _cmd(card, args.stage),
                       "Lệnh chạy sai cờ, cần chạy lại đúng lệnh.")
    if args.finalize and args.stage != "VERIFY":
        return Outcome("FAIL", "Cờ --finalize chỉ dùng cho VERIFY — chạy lại: " + _cmd(card, args.stage),
                       "Lệnh chạy sai cờ, cần chạy lại đúng lệnh.")
    if args.stage == "PREP":
        return _prep(card, args.check)
    n = card["videos"][0]
    ctx["video"] = n
    project = (Path(args.project) if args.project else paths.project_dir(n, VERSION)).absolute()   # C7
    ctx["project"] = project.as_posix()
    lock = project.parent / ".stage.lock"
    with ExitStack() as stack:
        try:
            stack.enter_context(file_lock(lock))
        except LockBusy:
            raise Block("transient", f"video {n} đang có stage khác chạy (khoá {lock.as_posix()})") from None
        handler = _verify_finalize if args.finalize else _HANDLERS[args.stage]
        return handler(card, project, R, args.check)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Chạy đúng một stage của card con trỏ (spec §10.2)")
    ap.add_argument("stage", choices=STAGE_NAMES)
    ap.add_argument("--task", help='Id card (t_…) trong câu "work kanban task <id>" — mặc định $HERMES_KANBAN_TASK')
    ap.add_argument("--check", action="store_true", help="PREP: kiểm phiếu + PREP-SHEET; PLAN: validate_edit")
    ap.add_argument("--finalize", action="store_true",
                    help="VERIFY: gộp nhận xét contact sheet (out/verify/v7_concern.txt) vào VERDICT rồi chốt")
    ap.add_argument("--project", help="Thư mục dự án (mặc định VID_ROOT/<n>/edit-r<ver>)")
    ap.add_argument("--card-file", help="Đọc thân card từ file thay vì hermes kanban show")
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and re.fullmatch(r"(?i)(prep)(-\d+)?|intake|plan|build|verify", argv[0]):
        argv[0] = argv[0].split("-")[0].upper()          # card "STAGE: PREP-<k>" ⇒ PREP; chữ thường vẫn nhận
    try:
        args = ap.parse_args(argv)
    except SystemExit as exc:
        if not exc.code:
            return 0
        given = next((argv[i + 1] for i, a in enumerate(argv[:-1]) if a == "--task"), None)
        return _emit(Outcome("FAIL", "Lệnh stage.py sai cú pháp — chạy: "
                             + _cmd({"rerun": ["--task", given]} if given else None, "STAGE")
                             + ' — thay STAGE bằng chữ sau "STAGE:" của card (PREP-1 ⇒ PREP; INTAKE, PLAN, BUILD, VERIFY giữ nguyên)',
                             "Lệnh chạy sai cú pháp, cần chạy lại đúng lệnh."), {"stage": None})
    ctx = {"stage": args.stage, "check": args.check, "finalize": args.finalize, "release": VERSION}
    try:
        out = _dispatch(args, ctx)
    except Block as b:
        out = _blocked(args.stage, b)
    except subprocess.TimeoutExpired as exc:         # R47: thlib.proc đã giết cả cây process; khoá đã nhả
        out = _blocked(args.stage, Block("transient", _timed_out(exc)))
    except Exception:                                # lỗi chương trình: in traceback cho dev, vẫn giữ giao thức
        traceback.print_exc(file=sys.stdout)
        out = _blocked(args.stage, Block("capability", "stage.py gặp lỗi chương trình (traceback ở trên)"))
    return _emit(out, ctx)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # worker Hermes không đặt PYTHONIOENCODING
    raise SystemExit(main())
