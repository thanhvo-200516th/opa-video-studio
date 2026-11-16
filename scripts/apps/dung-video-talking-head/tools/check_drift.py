# -*- coding: utf-8 -*-
"""check_drift.py — kiểm trôi luật M0 trên cây Hermes thật, CHỈ ĐỌC (spec §13.1).

Dùng:
    PYTHONIOENCODING=utf-8 python tools/check_drift.py [--hermes-root <path>]

In một dòng PASS/FAIL cho từng mục 1–9 dưới đây; thoát mã 1 nếu có mục FAIL,
0 nếu toàn bộ PASS. Không sửa, không xoá, không ghi gì lên cây Hermes; mục 8
chỉ gọi hai lệnh đọc của Hermes CLI (`kanban boards list`, `kanban show`), mục 9
chỉ gọi `git --no-optional-locks … status --porcelain` (không ghi index). Chạy
trước mỗi lô và sau mỗi card.

  1. profiles/opa-operator/staging/ (trừ _superseded/): không file *.md|*.py
     nào còn nhắc luật cũ (0.82 / DUCK_DB / OUTPUT_AUDIO_OFFSET).
  2. Không còn thư mục profiles/*/skills/**/dung-video-talking-head (bản chép
     tay của skill, phải sống ở SKILL dùng chung, không nhân bản vào profile).
  3. config.yaml GỐC (<hermes-root>/config.yaml — gateway gốc giữ dispatcher singleton đọc
     kanban.* từ đây, R44): kanban.max_in_progress_per_profile == 1 và kanban.auto_decompose vẫn
     true (D9 — giữ nguyên, không tắt). Giá trị trong profiles/opa-operator/config.yaml chỉ in
     kèm để tham khảo, không đổi PASS/FAIL.
  4. profiles/opa-editor/config.yaml và profiles/opa-verifier/config.yaml:
     auxiliary.background_review.enabled == false.
  5. profiles/opa-operator/config.yaml: command_allowlist không còn entry
     "execute_code" hay entry cho phép chạy script qua cờ -e/-c.
  6. File profiles/opa-operator/skills/claude-import/remotion-best-practices/
     rules/sfx.md đã bị xoá (đã dọn sang skill dùng-video-talking-head).
  7. (spec §13.1 mục 2, R46) profiles/<p>/SOUL.md của opa-operator, opa-editor,
     opa-verifier có MỘT dòng mang cả ba: dấu `dung-video-talking-head@1.1`,
     đường dẫn trong thư mục skill (operator → `dung-video-talking-head/
     releases/<ver>/stages/OPERATOR.md`, editor/verifier → `dung-video-talking-
     head/SKILL.md`; dấu / hay \\ đều được) và chữ `KHÔNG áp dụng` (quy trình
     riêng của SOUL không áp cho card/lô đó). Dòng nguyên văn: OPERATOR.md §M0.
  8. (spec §13.1 mục 4) board vm-heygen-1 đã archive — không còn trong
     `hermes kanban boards list --all --json` (đã `boards rm`) hoặc còn nhưng
     "archived": true — và card t_81a309b2 archive: board không còn thì card đi
     theo board; board còn thì `hermes kanban --board vm-heygen-1 show
     t_81a309b2 --json` phải có task.status == "archived". hermes.exe lấy ở
     <hermes-root>/hermes-agent/venv/Scripts/; bỏ banner CLI in trước JSON.
  9. (FS-8) Thư mục skill đang dùng <hermes-root>/shared-skills/video/
     dung-video-talking-head sạch: `git status --porcelain` rỗng — worker sửa
     được skill (skill_manage, tool file, terminal) mà SKILL.md router không nằm
     trong MANIFEST, nên chỉ git mới bắt được.

Đọc config.yaml bằng PyYAML nếu máy có cài; nếu `import yaml` lỗi (worker cấm
`python -c` nên không tự cài PyYAML tại chỗ được) thì rơi về đọc thô các dòng
`key: value` / `- item` theo thụt đầu dòng — đủ dùng cho vài khoá nông ở trên,
không phải một trình đọc YAML đầy đủ.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    yaml = None
    _HAS_YAML = False

DEFAULT_HERMES_ROOT = "C:/Users/Minh PC/AppData/Local/hermes"

_LEGACY_RULE_RE = re.compile(r"\b0\.82\b|DUCK_DB|OUTPUT_AUDIO_OFFSET")
_ALLOWLIST_EXECUTE_CODE = "execute_code"
_ALLOWLIST_DASH_CE_RE = re.compile(r"-e/-c|-c/-e")

SOUL_MARKER = "dung-video-talking-head@1.1"
SOUL_PRECEDENCE = "KHÔNG áp dụng"                    # R46: con trỏ đè quy trình riêng của SOUL
_SEP = r"[\\/]"
_OPERATOR_MD = "dung-video-talking-head/releases/<ver>/stages/OPERATOR.md"
_SKILL_MD = "dung-video-talking-head/SKILL.md"
_OPERATOR_MD_RE = re.compile(rf"dung-video-talking-head{_SEP}releases{_SEP}[^\\/\s`'\"]+{_SEP}stages{_SEP}OPERATOR\.md")
_SKILL_MD_RE = re.compile(rf"dung-video-talking-head{_SEP}SKILL\.md")
SOUL_POINTERS = {   # profile -> (đường dẫn phải có, mẫu khớp — dấu / hay \ đều được)
    "opa-operator": (_OPERATOR_MD, _OPERATOR_MD_RE),
    "opa-editor": (_SKILL_MD, _SKILL_MD_RE),
    "opa-verifier": (_SKILL_MD, _SKILL_MD_RE),
}
OLD_BOARD, OLD_CARD = "vm-heygen-1", "t_81a309b2"
HERMES_EXE = Path("hermes-agent") / "venv" / "Scripts" / "hermes.exe"
_HERMES_TIMEOUT_S = 120
LIVE_SKILL = Path("shared-skills") / "video" / "dung-video-talking-head"   # skill worker đang dùng (mục 9)
_GIT_TIMEOUT_S = 60


# --------------------------------------------------------------- đọc YAML tối giản


def _scalar(value: str):
    """'true'/'false' -> bool, số nguyên/thực -> int/float, còn lại -> chuỗi
    (bỏ ngoặc kép/đơn nếu có)."""
    if value in ("true", "True"):
        return True
    if value in ("false", "False"):
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value.strip("'\"")


def _parse_minimal_yaml(text: str) -> dict:
    """Đọc thô `key: value` (map lồng nhau qua thụt đầu dòng) và `- item`
    (danh sách, gom vào khoá "__list__" của map cha) — không hiểu flow style
    ({...}/[...]), chuỗi nhiều dòng, hay anchor; chỉ đủ cho các khoá phẳng mà
    check_drift cần (kanban.*, auxiliary.background_review.*, command_allowlist)."""
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if stripped.startswith("- "):
            parent.setdefault("__list__", []).append(stripped[2:].strip())
            continue
        if ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        key, value = key.strip(), value.strip()
        if value == "":
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _scalar(value)
    return root


def _load_yaml(path: Path) -> dict:
    """Đọc một file config.yaml thành dict lồng nhau."""
    text = path.read_text(encoding="utf-8")
    if _HAS_YAML:
        return yaml.safe_load(text) or {}
    return _parse_minimal_yaml(text)


def _load_profile_config(root: Path, profile: str) -> tuple[dict | None, str | None]:
    """Đọc profiles/<profile>/config.yaml; trả (cfg, None), hoặc (None, lý do)
    nếu thiếu file — để mục kiểm báo FAIL rõ ràng thay vì crash."""
    path = root / "profiles" / profile / "config.yaml"
    if not path.is_file():
        return None, f"thiếu {path.relative_to(root)}"
    return _load_yaml(path), None


def _get(cfg: dict, dotted_key: str):
    """Tra khoá lồng nhau kiểu "a.b.c"; trả None nếu thiếu ở bất cứ cấp nào."""
    cur = cfg
    for part in dotted_key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _command_allowlist(cfg: dict) -> list[str]:
    """command_allowlist là một list scalar; PyYAML trả list thẳng, bộ đọc
    thô gom vào "__list__" của dict con."""
    val = cfg.get("command_allowlist") or []
    if isinstance(val, dict):
        val = val.get("__list__", [])
    return [str(item) for item in val]


# --------------------------------------------------------------- 6 mục kiểm


def _check_staging_clean(root: Path) -> tuple[bool, str]:
    staging = root / "profiles" / "opa-operator" / "staging"
    if not staging.is_dir():
        return True, f"không thấy {staging} (bỏ qua)"
    hits = []
    for pattern in ("*.md", "*.py"):
        for f in staging.rglob(pattern):
            if "_superseded" in f.relative_to(staging).parts:
                continue
            text = f.read_text(encoding="utf-8", errors="ignore")
            if _LEGACY_RULE_RE.search(text):
                hits.append(str(f.relative_to(root)))
    if hits:
        return False, "còn dấu vết luật cũ (0.82/DUCK_DB/OUTPUT_AUDIO_OFFSET) ở: " + ", ".join(sorted(hits))
    return True, f"{staging.relative_to(root)} (trừ _superseded/) sạch dấu vết luật cũ"


def _check_no_legacy_skill_dir(root: Path) -> tuple[bool, str]:
    hits = sorted(
        str(p.relative_to(root))
        for p in root.glob("profiles/*/skills/**/dung-video-talking-head")
        if p.is_dir()
    )
    if hits:
        return False, "còn thư mục skill cũ: " + ", ".join(hits)
    return True, "không có profiles/*/skills/**/dung-video-talking-head"


def _check_kanban(root: Path) -> tuple[bool, str]:
    """R44: dispatcher là singleton của gateway gốc, đọc kanban.* từ <hermes-root>/config.yaml lúc
    khởi động — chấm config gốc; bản của opa-operator chỉ in để tham khảo."""
    path = root / "config.yaml"
    if not path.is_file():
        return False, "thiếu config.yaml gốc (gateway gốc giữ dispatcher đọc kanban.* từ đây)"
    cfg = _load_yaml(path)
    max_ipp = _get(cfg, "kanban.max_in_progress_per_profile")
    auto_decompose = _get(cfg, "kanban.auto_decompose")
    ok = max_ipp == 1 and auto_decompose is True
    op_cfg, err = _load_profile_config(root, "opa-operator")
    info = err or f"max_in_progress_per_profile={_get(op_cfg, 'kanban.max_in_progress_per_profile')!r}"
    return ok, (f"config.yaml gốc: kanban.max_in_progress_per_profile={max_ipp!r}, "
                f"kanban.auto_decompose={auto_decompose!r} (tham khảo, không chấm: opa-operator {info})")


def _check_background_review_off(root: Path) -> tuple[bool, str]:
    bad = []
    for profile in ("opa-editor", "opa-verifier"):
        cfg, err = _load_profile_config(root, profile)
        if err:
            bad.append(err)
            continue
        enabled = _get(cfg, "auxiliary.background_review.enabled")
        if enabled is not False:
            bad.append(f"{profile}: auxiliary.background_review.enabled={enabled!r}")
    if bad:
        return False, "; ".join(bad)
    return True, "opa-editor + opa-verifier: auxiliary.background_review.enabled=false"


def _check_allowlist_no_execute(root: Path) -> tuple[bool, str]:
    cfg, err = _load_profile_config(root, "opa-operator")
    if err:
        return False, err
    allowlist = _command_allowlist(cfg)
    bad = [item for item in allowlist
           if item.strip() == _ALLOWLIST_EXECUTE_CODE or _ALLOWLIST_DASH_CE_RE.search(item)]
    if bad:
        return False, "command_allowlist còn: " + ", ".join(bad)
    return True, "command_allowlist không còn execute_code / -e/-c"


def _check_sfx_md_absent(root: Path) -> tuple[bool, str]:
    path = (root / "profiles" / "opa-operator" / "skills" / "claude-import"
            / "remotion-best-practices" / "rules" / "sfx.md")
    if path.exists():
        return False, f"vẫn còn {path}"
    return True, f"đã xoá {path.relative_to(root)}"


def _check_soul_pointers(root: Path) -> tuple[bool, str]:
    bad = []
    for profile, (target, pattern) in SOUL_POINTERS.items():
        path = root / "profiles" / profile / "SOUL.md"
        if not path.is_file():
            bad.append(f"{profile}: thiếu {path.relative_to(root).as_posix()}")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(SOUL_MARKER in ln and pattern.search(ln) and SOUL_PRECEDENCE in ln for ln in text.splitlines()):
            continue
        missing = [need for need, found in ((SOUL_MARKER, SOUL_MARKER in text),
                                            (f"đường dẫn …/{target}", pattern.search(text)),
                                            (SOUL_PRECEDENCE, SOUL_PRECEDENCE in text)) if not found]
        bad.append(f"{profile}: SOUL.md thiếu " + " và ".join(missing) if missing else
                   f"{profile}: SOUL.md có {SOUL_MARKER}, đường dẫn …/{target} và `{SOUL_PRECEDENCE}` "
                   "nhưng không trên cùng một dòng")
    if bad:
        return False, "; ".join(bad)
    return True, (f"SOUL.md của {', '.join(SOUL_POINTERS)} có dòng {SOUL_MARKER} trỏ tới OPERATOR.md / SKILL.md "
                  f"và nói quy trình riêng `{SOUL_PRECEDENCE}`")


def _run_hermes(root: Path, args: list[str]) -> tuple[int, str]:
    """Chạy `hermes kanban <args>` (chỉ lệnh đọc) bằng hermes.exe của cây `root`; trả (mã thoát,
    stdout khi thành công, ngược lại stderr/stdout). Test thay hàm này — không gọi CLI thật."""
    exe = root / HERMES_EXE
    if not exe.is_file():
        return 127, f"không thấy {exe.as_posix()}"
    try:
        proc = subprocess.run([str(exe), "kanban", *args], capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=_HERMES_TIMEOUT_S,
                              env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, f"hermes kanban {' '.join(args)} lỗi: {exc}"
    return proc.returncode, proc.stdout if proc.returncode == 0 else (proc.stderr or proc.stdout)


def _hermes_json(root: Path, args: list[str]):
    """JSON của một lệnh đọc Hermes, bỏ banner CLI in trước JSON (dòng "⚠ …" + dòng thụt lề —
    như thlib.kanban._strip_banner). Lỗi CLI/JSON ⇒ RuntimeError mang nguyên văn lỗi."""
    code, out = _run_hermes(root, args)
    if code != 0:
        raise RuntimeError(f"`hermes kanban {' '.join(args)}` lỗi (mã {code}): {out.strip()[-300:]}")
    lines = out.splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.startswith(("{", "["))), len(lines))
    try:
        return json.loads("\n".join(lines[start:]))
    except json.JSONDecodeError:
        raise RuntimeError(f"`hermes kanban {' '.join(args)}` không in JSON: {out.strip()[-300:]}") from None


def _check_old_board_archived(root: Path) -> tuple[bool, str]:
    try:
        boards = {b.get("slug"): b for b in _hermes_json(root, ["boards", "list", "--all", "--json"])}
        board = boards.get(OLD_BOARD)
        if board is None:
            return True, (f"board {OLD_BOARD} không còn trong `boards list --all` (đã archive vào "
                          f"kanban/boards/_archived/ hoặc xoá) — card {OLD_CARD} đi theo board")
        task = _hermes_json(root, ["--board", OLD_BOARD, "show", OLD_CARD, "--json"]).get("task") or {}
    except RuntimeError as exc:
        return False, str(exc)
    bad = [] if board.get("archived") is True else [f"board {OLD_BOARD} chưa archive"]
    if task.get("status") != "archived":
        bad.append(f"card {OLD_CARD} status={task.get('status')!r}, chưa archive")
    if bad:
        return False, "; ".join(bad)
    return True, f"board {OLD_BOARD} archived=true; card {OLD_CARD} status='archived'"


def _run_git(skill_dir: Path) -> tuple[int, str]:
    """`git --no-optional-locks -C <dir> status --porcelain` — chỉ đọc, không ghi lại index; trả (mã
    thoát, stdout khi thành công, ngược lại stderr/stdout). Test thay hàm này."""
    try:
        proc = subprocess.run(["git", "--no-optional-locks", "-C", str(skill_dir), "status", "--porcelain"],
                              capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=_GIT_TIMEOUT_S)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, f"git status lỗi: {exc}"
    return proc.returncode, proc.stdout if proc.returncode == 0 else (proc.stderr or proc.stdout)


def _check_live_skill_clean(root: Path) -> tuple[bool, str]:
    """FS-8: worker sửa được thư mục skill đang dùng (skill_manage, tool file, terminal) và SKILL.md
    router không nằm trong MANIFEST ⇒ git status của thư mục đó phải rỗng."""
    skill = root / LIVE_SKILL
    if not skill.is_dir():
        return False, f"không thấy thư mục skill đang dùng {skill.as_posix()}"
    code, out = _run_git(skill)
    if code != 0:
        return False, f"`git -C {skill.as_posix()} status --porcelain` lỗi (mã {code}): {out.strip()[-300:]}"
    changed = [ln.strip() for ln in out.splitlines() if ln.strip()]
    if changed:
        return False, (f"{LIVE_SKILL.as_posix()} có {len(changed)} thay đổi chưa commit (worker sửa skill?): "
                       + "; ".join(changed[:10]))
    return True, f"{LIVE_SKILL.as_posix()} sạch (git status --porcelain rỗng)"


_CHECKS = (
    ("1", _check_staging_clean),
    ("2", _check_no_legacy_skill_dir),
    ("3", _check_kanban),
    ("4", _check_background_review_off),
    ("5", _check_allowlist_no_execute),
    ("6", _check_sfx_md_absent),
    ("7", _check_soul_pointers),
    ("8", _check_old_board_archived),
    ("9", _check_live_skill_clean),
)


def check_drift(hermes_root: Path) -> list[dict]:
    """Chạy cả 9 mục trên `hermes_root`; trả luôn đủ 9 phần tử theo thứ tự
    1..9 dạng {"code","ok","msg"} (PASS/FAIL chung cuộc = mọi phần tử "ok")."""
    root = Path(hermes_root)
    results = []
    for code, fn in _CHECKS:
        ok, msg = fn(root)
        results.append({"code": code, "ok": ok, "msg": msg})
    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Kiểm trôi luật M0 trên cây Hermes thật (chỉ đọc)")
    ap.add_argument("--hermes-root", default=DEFAULT_HERMES_ROOT,
                    help="Gốc Hermes cần kiểm (mặc định %(default)s)")
    args = ap.parse_args(argv)

    results = check_drift(Path(args.hermes_root))
    for r in results:
        print("%s %s  %s" % (r["code"], "PASS" if r["ok"] else "FAIL", r["msg"]))
    return 1 if any(not r["ok"] for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
