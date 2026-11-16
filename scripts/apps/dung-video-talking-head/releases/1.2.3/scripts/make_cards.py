"""make_cards.py — sinh card con trỏ của một lô trên board Hermes, hai phase (spec §7.2, §9, §10.2; C1).

Dùng:
    PYTHONIOENCODING=utf-8 python make_cards.py --batch b01 --board vm-heygen-b01 [--check | --dry-run]
    PYTHONIOENCODING=utf-8 python make_cards.py --batch b01 --board vm-heygen-b01 --phase videos [--check | --dry-run]
    PYTHONIOENCODING=utf-8 python make_cards.py --batch b01 --board vm-heygen-b01 --retry <n>:<STAGE>
    PYTHONIOENCODING=utf-8 python make_cards.py --batch b01 --board vm-heygen-b01 --retry PREP-<k>

Phase `prep` (mặc định, P0) chỉ tạo PREP-<k> (opa-editor, ≤ batch.prep_videos_per_card video) →
APPROVE-PREP-<k> (user). Phase `videos` chạy sau khi user duyệt và operator complete mọi
APPROVE-PREP-<k>: đọc các phiếu prep/prep-<k>.json đã duyệt (đủ mọi nhóm, đạt check_prep; status
trong phiếu đè status của intake.py), chọn canary trong các video `ok` (video intake.py đánh canary
nếu vẫn ok, không thì video ok số nhỏ nhất), rồi tạo theo thứ tự cha trước con:
  canary: INTAKE (cha: APPROVE-PREP của nó) → PLAN → BUILD → VERIFY → APPROVE-CANARY (user) →
  mỗi video ok còn lại: INTAKE (cha: APPROVE-PREP của nó + APPROVE-CANARY) → PLAN → BUILD → VERIFY.
Video needs_* không có card nào. Khoá idempotency vmh-<n>-<stage>-a<k>.
Card duyệt giao cho `user`, status mặc định (Ruling R28: dispatcher không chạy assignee không phải
profile); operator chỉ complete sau khi chép nguyên văn lời duyệt của user. Ngân sách và cờ lấy
từ rules.budgets (retries = số lần thử lại sau lần đầu ⇒ Hermes --max-retries retries + 1, C2);
PLAN từ lần thử thứ hai chạy --model <models.plan_a2>.

Sổ card `_batches/<b>/cards.json` ({"board", "cards": {khoá: {"id", "kind", "video", "attempt",
"parents"}}}, parents = khoá cha) ghi sau mỗi card tạo xong: chạy lại chỉ tạo card chưa có trong sổ
(không dựng lại card đã archive), và FAIL khi card đã tạo có cha khác kế hoạch (vd phiếu duyệt đổi
canary sau phase videos); `--retry` mở lần thử kế tiếp cho một stage và các stage sau nó, cha tra
trong sổ, rồi in việc của operator (nối lại card duyệt, rồi archive card cũ). --check và --dry-run
không gọi Hermes, không ghi sổ; cả hai kiểm kế hoạch card, --dry-run in nguyên lệnh hermes của
từng card. Phase videos thật hỏi Hermes trạng thái mọi APPROVE-PREP-<k> trước khi tạo card.
Chạy thật (không --check/--dry-run) in `VID_ROOT: …` rồi hỏi `hermes kanban boards list --json`
trước tiên: board chưa có ⇒ FAIL kèm đúng lệnh `hermes kanban boards create …` (R44); TH_VID_ROOT
đang đặt ⇒ FAIL trừ khi có --allow-th-vid-root (FS-9).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from thlib import kanban, paths, prep, rules, state

SCRIPTS = Path(__file__).resolve().parent
VERSION = SCRIPTS.parent.name
REGISTRY = "cards.json"
USER = "user"                                        # Ruling R28
ASSIGNEE = {"PREP": "opa-editor", "INTAKE": "opa-editor", "PLAN": "opa-editor", "BUILD": "opa-editor",
            "VERIFY": "opa-verifier"}
_RETRY_RE = re.compile(r"(\d+):(%s)|PREP-([1-9]\d*)" % "|".join(kanban.STAGES))
PHASES = ("prep", "videos")                          # C1: P0 | sau khi mọi APPROVE-PREP complete


def _key(subject, stage: str, attempt: int) -> str:
    return f"vmh-{subject}-{stage.lower()}-a{attempt}"


def _approve_prep_key(batch: str, k: int) -> str:
    return _key(batch, f"approve-prep-{k}", 1)


def _approve_canary_key(batch: str) -> str:
    return _key(batch, "approve-canary", 1)


def _work_card(R, manifest: dict, kind: str, videos: list[int], token: str, attempt: int,
               parents: list[str], subject, title: str, workspace: Path) -> dict:
    b = R.get(f"budgets.{kind}")
    return {"key": _key(subject, token, attempt), "kind": kind, "video": videos[0] if kind != "PREP" else None,
            "attempt": attempt, "title": title + (f" a{attempt}" if attempt > 1 else ""),
            "body": kanban.format_body(videos, token, manifest["rules_version"], manifest["preset"], attempt,
                                       manifest["batch"]),
            "assignee": ASSIGNEE[kind], "parents": parents, "workspace": f"dir:{workspace.as_posix()}",
            "skills": [state.SKILL_NAME], "runtime": b["runtime"], "retries": b["retries"],
            "goal_turns": b["goal_turns"], "initial_status": None,
            "model": R.get("models.plan_a2") if kind == "PLAN" and attempt >= 2 else None}


def _prep_card(R, manifest: dict, k: int, videos: list[int], attempt: int = 1) -> dict:
    b = manifest["batch"]
    return _work_card(R, manifest, "PREP", videos, f"PREP-{k}", attempt, [], b, f"[vmh-{b}] PREP-{k}",
                      paths.batch_dir(b))


def _video_card(R, manifest: dict, n: int, stage: str, attempt: int, parents: list[str]) -> dict:
    return _work_card(R, manifest, stage, [n], stage, attempt, parents, n, f"[vmh-{n:02d}] {stage}",
                      paths.VID_ROOT / str(n))


def _approval_card(key: str, kind: str, title: str, body: str, parents: list[str]) -> dict:
    return {"key": key, "kind": kind, "video": None, "attempt": 1, "title": title, "body": body,
            "assignee": USER, "parents": parents, "workspace": None, "skills": [], "runtime": None,
            "retries": None, "goal_turns": 0, "initial_status": None, "model": None}


def _chain(R, manifest: dict, n: int, stages, attempts: dict, parents: list[str]) -> list[dict]:
    """Chuỗi card của video n qua `stages` (cha của card đầu = `parents`)."""
    cards = []
    for stage in stages:
        cards.append(_video_card(R, manifest, n, stage, attempts[stage], parents))
        parents = [cards[-1]["key"]]
    return cards


def _groups(manifest: dict, R) -> list[list[int]]:
    ns = sorted(v["n"] for v in manifest["videos"])
    per = R.get("batch.prep_videos_per_card")
    return [ns[i:i + per] for i in range(0, len(ns), per)]


def _statuses(manifest: dict, preps: dict) -> dict[int, str]:
    """status của từng video: phiếu PREP đạt khuôn đè status của intake.py (phiếu k sau thắng)."""
    override = {v["n"]: v["status"] for _, data in sorted(preps.items()) for v in data["videos"]}
    return {v["n"]: override.get(v["n"], v["status"]) for v in manifest["videos"]}


def _canary(manifest: dict, ok: list[int], registered: int | None = None) -> int | None:
    """Video canary: canary đã có chuỗi card (sổ) nếu còn ok — video vào lô sau phase videos không
    đổi canary; rồi video intake.py đánh canary nếu còn ok; không thì video ok số nhỏ nhất."""
    if registered in ok:
        return registered
    flagged = next((v["n"] for v in manifest["videos"] if v.get("canary") and v["n"] in ok), None)
    return flagged if flagged is not None else (min(ok) if ok else None)


def _prep_cards(R, manifest: dict) -> list[dict]:
    """Phase prep (P0): PREP-<k> → APPROVE-PREP-<k> của từng nhóm video."""
    b, cards = manifest["batch"], []
    for k, g in enumerate(_groups(manifest, R), 1):
        pc = _prep_card(R, manifest, k, g)
        body = (f"Chờ user duyệt phiếu PREP-{k} của lô {b} (video {', '.join(map(str, g))}): "
                f"{(paths.batch_dir(b) / 'PREP-SHEET.md').as_posix()}\n"
                "Operator: chép nguyên văn lời duyệt của user vào comment card này và vào APPROVALS.md, "
                "rồi mới complete. Không agent nào chạy card này.")
        cards += [pc, _approval_card(_approve_prep_key(b, k), "APPROVE-PREP", f"[vmh-{b}] APPROVE-PREP-{k}",
                                     body, [pc["key"]])]
    return cards


def plan_cards(manifest: dict, preps: dict, R, phase: str, reg: dict | None = None) -> list[dict]:
    """Kế hoạch card của một phase, theo thứ tự tạo. Phase videos: `preps` = {k: phiếu đã duyệt,
    đạt khuôn}; canary chọn trong các video ok theo phiếu (canary đã có trong sổ `reg` được giữ);
    card đầu tiên là INTAKE của canary."""
    if phase == "prep":
        return _prep_cards(R, manifest)
    b = manifest["batch"]
    k_of = {n: k for k, g in enumerate(_groups(manifest, R), 1) for n in g}
    ok = sorted(n for n, s in _statuses(manifest, preps).items() if s == "ok")
    canary = _canary(manifest, ok, registered_canary(reg, b) if reg else None)
    if canary is None:
        return []
    first = dict.fromkeys(kanban.STAGES, 1)
    chain = _chain(R, manifest, canary, kanban.STAGES, first, [_approve_prep_key(b, k_of[canary])])
    project = paths.project_dir(canary, manifest["rules_version"])
    body = (f"Chờ user duyệt video canary {canary} của lô {b}: {(project / 'out' / 'final.mp4').as_posix()} và "
            f"{(project / 'out' / 'verify' / 'VERDICT.md').as_posix()}\n"
            "Operator: chép nguyên văn lời duyệt của user vào comment card này và vào APPROVALS.md, rồi mới "
            "complete — các video còn lại của lô chỉ chạy sau card này.")
    approve = _approval_card(_approve_canary_key(b), "APPROVE-CANARY", f"[vmh-{b}] APPROVE-CANARY", body,
                             [chain[-1]["key"]])
    cards = chain + [approve]
    for n in ok:
        if n != canary:
            cards += _chain(R, manifest, n, kanban.STAGES, first,
                            [_approve_prep_key(b, k_of[n]), approve["key"]])
    return cards


def approved_prep_errors(manifest: dict, loaded: dict, R, reg: dict) -> list[str]:
    """Phase videos cần APPROVE-PREP-<k> của mọi nhóm trong sổ card (phase prep đã chạy) và phiếu
    prep-<k>.json đạt check_prep, ghi đúng video của nhóm."""
    errors = []
    for k, g in enumerate(_groups(manifest, R), 1):
        if _approve_prep_key(manifest["batch"], k) not in reg["cards"]:
            errors.append(f"sổ card chưa có APPROVE-PREP-{k} — chạy make_cards.py phase prep trước")
        data, errs = loaded.get(k, (None, ["chưa có file — PREP-%d chưa xong" % k]))
        if errs:
            errors.append(f"prep-{k}.json chưa đạt check_prep: {'; '.join(errs)}")
        elif sorted(v["n"] for v in data["videos"]) != g:
            errors.append(f"prep-{k}.json ghi video {sorted(v['n'] for v in data['videos'])}, nhóm PREP-{k} là {g}")
    return errors


def check_plan(cards: list[dict], manifest: dict, preps: dict, R, phase: str, reg: dict) -> list[str]:
    """Lỗi của kế hoạch card một phase (rỗng = đạt): đầu vào, khoá, thứ tự cha–con (cha có sẵn
    trong sổ `reg` cũng được), card đã tạo phải có đúng cha của kế hoạch, thân card; phase prep:
    phiếu PREP phủ mọi video; phase videos: đủ 4 card cho mỗi video ok, không card nào cho video khác."""
    errors = []
    if manifest.get("rules_version") != VERSION:
        errors.append(f"batch_manifest.json ghi rules_version {manifest.get('rules_version')}, "
                      f"make_cards.py thuộc bản {VERSION}")
    if manifest.get("preset") not in R.get("presets"):
        errors.append(f"preset {manifest.get('preset')!r} không có trong rules.json")
    seen, bodies = [], {}
    for c in cards:
        if c["key"] in seen:
            errors.append(f"khoá trùng {c['key']}")
        errors += [f"{c['key']}: cha {p} chưa được tạo trước (phase prep chạy trước phase videos)"
                   for p in c["parents"] if p not in seen and p not in reg["cards"]]
        seen.append(c["key"])
        made = reg["cards"].get(c["key"])
        if made is not None and made.get("parents") != c["parents"]:
            errors.append(f"{c['key']} đã tạo ({made['id']}) với cha {made.get('parents')}, kế hoạch nay cần cha "
                          f"{c['parents']} — phiếu duyệt đổi sau khi tạo card; operator hỏi dev, không tự sửa")
        if c["assignee"] != USER:
            try:
                body = kanban.parse_body(c["body"])
            except kanban.CardError as exc:
                errors.append(f"{c['key']}: {exc}")
                continue
            bodies[c["key"]] = body
            if (body["batch"], body["attempt"]) != (manifest["batch"], c["attempt"]):
                errors.append(f"{c['key']}: thân card lệch lô/lần thử")
    if phase == "prep":
        grouped = sorted(n for c in cards if c["kind"] == "PREP" for n in bodies.get(c["key"], {}).get("videos", []))
        if grouped != sorted(v["n"] for v in manifest["videos"]):
            errors.append(f"phiếu PREP phủ video {grouped}, lô có {sorted(v['n'] for v in manifest['videos'])}")
        return errors
    for n, s in _statuses(manifest, preps).items():
        stages = [c["kind"] for c in cards if c["video"] == n]
        want = list(kanban.STAGES) if s == "ok" else []
        if stages != want:
            errors.append(f"video {n} ({s}): card {stages}, cần {want}")
    return errors


# ------------------------------------------------------------------ sổ card, --retry


def _load_registry(batch: Path, board: str) -> tuple[dict, str | None]:
    path = batch / REGISTRY
    reg = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"board": board, "cards": {}}
    err = None if reg["board"] == board else f"lô này đã tạo card trên board {reg['board']}, không phải {board}"
    return reg, err


def _save_registry(batch: Path, reg: dict) -> None:
    (batch / REGISTRY).write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8")


def _latest(reg: dict, kind: str, video: int | None = None) -> tuple[str, dict] | None:
    found = [(k, e) for k, e in reg["cards"].items() if e["kind"] == kind and e["video"] == video]
    return max(found, key=lambda ke: ke[1]["attempt"]) if found else None


def registered_canary(reg: dict, batch: str) -> int | None:
    """Video canary đã có chuỗi card: video của cha APPROVE-CANARY trong sổ (None = chưa có phase videos)."""
    entry = reg["cards"].get(_approve_canary_key(batch))
    parent = reg["cards"].get(entry["parents"][0]) if entry and entry.get("parents") else None
    return parent["video"] if parent else None


def board_error(board: str, batch: str) -> str | None:
    """R44 (MF-3): board của lô phải có sẵn — make_cards không tạo board; thiếu ⇒ lỗi kèm đúng lệnh tạo."""
    try:
        slugs = {b.get("slug") for b in kanban.boards()}
    except kanban.KanbanError as exc:
        return f"không đọc được danh sách board: {exc}"
    if board in slugs:
        return None
    return (f"board {board} chưa có — operator tạo board rồi chạy lại lệnh này: "
            f'hermes kanban boards create {board} --name "Van Minh AI · HeyGen {batch}"')


def _unapproved(manifest: dict, R, reg: dict, board: str) -> list[str]:
    """APPROVE-PREP-<k> chưa complete trên board (hỏi Hermes) — phase videos chỉ chạy sau lời duyệt."""
    bad = []
    for k in range(1, len(_groups(manifest, R)) + 1):
        tid = reg["cards"][_approve_prep_key(manifest["batch"], k)]["id"]
        status = kanban.show(tid, board)["task"]["status"]
        if status != "done":
            bad.append(f"APPROVE-PREP-{k} ({tid}) đang {status} — chờ user duyệt, operator complete rồi chạy lại")
    return bad


def retry_cards(spec: str, manifest: dict, R, reg: dict, board: str) -> tuple[list[dict], list[str]]:
    """Card của lần thử kế tiếp + việc của operator. `spec` = "<n>:<STAGE>" hoặc "PREP-<k>"."""
    m = _RETRY_RE.fullmatch(spec)
    if m is None:
        raise ValueError(f"--retry {spec!r} sai mẫu (<n>:<STAGE> hoặc PREP-<k>)")
    b, hb = manifest["batch"], f"hermes kanban --board {board}"
    groups = _groups(manifest, R)
    if m.group(3):
        k = int(m.group(3))
        prefix = f"vmh-{b}-prep-{k}-a"
        tried = [e for key, e in reg["cards"].items() if key.startswith(prefix)]
        if not tried or k > len(groups):
            raise ValueError(f"sổ card chưa có PREP-{k}")
        last = max(tried, key=lambda e: e["attempt"])
        cards, olds = [_prep_card(R, manifest, k, groups[k - 1], last["attempt"] + 1)], [last["id"]]
        dependent = reg["cards"].get(_approve_prep_key(b, k))
    else:
        n, stage = int(m.group(1)), m.group(2)
        stages = kanban.STAGES[kanban.STAGES.index(stage):]
        olds, attempts = [], {}
        for s in stages:
            last = _latest(reg, s, n)
            if last is None:
                raise ValueError(f"sổ card chưa có card {s} của video {n}")
            olds.append(last[1]["id"])
            attempts[s] = last[1]["attempt"] + 1
        is_canary = n == registered_canary(reg, b)
        if stage == "INTAKE":
            k = next(k for k, g in enumerate(groups, 1) if n in g)
            parents = [_approve_prep_key(b, k)] + ([] if is_canary else [_approve_canary_key(b)])
        else:
            parents = [_latest(reg, kanban.STAGES[kanban.STAGES.index(stage) - 1], n)[0]]
        cards = _chain(R, manifest, n, stages, attempts, parents)
        dependent = reg["cards"].get(_approve_canary_key(b)) if is_canary else None
    # FS-11: nối lại card duyệt TRƯỚC khi archive (card cha đã archive tính là xong ⇒ card duyệt / card
    # con cũ sẽ sang ready), archive từ cuối chuỗi về đầu.
    todo = []
    if dependent is not None:
        todo += [f"nối card duyệt vào card mới: {hb} link {{new}} {dependent['id']}",
                 f"gỡ nối card cũ: {hb} unlink {olds[-1]} {dependent['id']}"]
    todo.append(f"archive card cũ (từ cuối chuỗi về đầu): {hb} archive {' '.join(reversed(olds))}")
    return cards, todo


# ------------------------------------------------------------------ CLI


def _materialize(cards: list[dict], board: str, reg: dict, batch: Path, dry_run: bool) -> dict[str, str]:
    """Tạo (hoặc in lệnh tạo) các card chưa có trong sổ; trả {khoá: id}."""
    ids = {key: e["id"] for key, e in reg["cards"].items()}
    for c in cards:
        if c["key"] in ids:
            print(f"  có sẵn  {c['key']:<30} {ids[c['key']]}")
            continue
        got = kanban.create(board, c["title"], c["body"], c["assignee"], [ids.get(p, f"<{p}>") for p in c["parents"]],
                            c["workspace"], c["key"], c["skills"], c["runtime"], c["retries"], c["goal_turns"],
                            c["model"], c["initial_status"], dry_run=dry_run)
        if dry_run:
            ids[c["key"]] = got["id"]
            print("  " + subprocess.list2cmdline(got["argv"]))
            continue
        ids[c["key"]] = got
        reg["cards"][c["key"]] = {"id": got, "kind": c["kind"], "video": c["video"], "attempt": c["attempt"],
                                  "parents": c["parents"]}
        _save_registry(batch, reg)
        print(f"  tạo     {c['key']:<30} {got}")
    return ids


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sinh card con trỏ của một lô trên board Hermes")
    ap.add_argument("--batch", required=True, help="Tên lô, vd b01")
    ap.add_argument("--board", required=True, help="Board Hermes, vd vm-heygen-b01")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Kiểm kế hoạch card và in bảng, không tạo gì")
    mode.add_argument("--dry-run", action="store_true", help="In nguyên lệnh hermes của từng card, không tạo gì")
    ap.add_argument("--phase", choices=PHASES, default="prep",
                    help="prep (P0, mặc định): PREP-<k> + APPROVE-PREP-<k>; videos: sau khi mọi APPROVE-PREP "
                         "complete — canary, APPROVE-CANARY và chuỗi 4 card của từng video ok")
    ap.add_argument("--retry", help="Mở lần thử kế tiếp: <n>:<STAGE> (stage đó và các stage sau) hoặc PREP-<k>")
    ap.add_argument("--allow-th-vid-root", action="store_true",
                    help="Cho chạy thật khi TH_VID_ROOT đang đặt (mặc định FAIL — FS-9)")
    args = ap.parse_args(argv)

    if not (args.check or args.dry_run):             # R44: chạy thật — in VID_ROOT, board phải có sẵn
        print(f"VID_ROOT: {paths.VID_ROOT.as_posix()}")
        if os.environ.get("TH_VID_ROOT") and not args.allow_th_vid_root:     # FS-9
            print("FAIL: TH_VID_ROOT đang đặt (còn sót từ lần chạy nháp?) — card thật sẽ trỏ workspace và sổ card "
                  "vào VID_ROOT ở trên; bỏ biến đó (unset TH_VID_ROOT) rồi chạy lại, hoặc thêm --allow-th-vid-root "
                  "nếu cố ý")
            return 1
        err = board_error(args.board, args.batch)
        if err:
            print(f"FAIL: {err}")
            return 1
    batch = paths.batch_dir(args.batch)
    mpath = batch / "batch_manifest.json"
    if not mpath.is_file():
        print(f"FAIL: không có {mpath.as_posix()} — chạy intake.py (P0) trước")
        return 1
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    R = rules.load(VERSION)
    loaded = prep.load_all(batch)
    preps = {k: data for k, (data, errs) in loaded.items() if not errs}
    reg, reg_err = _load_registry(batch, args.board)
    errors = [reg_err] if reg_err else []
    if manifest.get("batch") != args.batch:
        errors.append(f"batch_manifest.json ghi lô {manifest.get('batch')!r}, lệnh chạy --batch {args.batch}")
    phase = "prep" if args.retry else args.phase     # --retry tự tra sổ card; chỉ kiểm kế hoạch phase prep
    if phase == "videos":
        errors += approved_prep_errors(manifest, loaded, R, reg)
    todo = []
    cards = plan_cards(manifest, preps, R, phase, reg)
    errors += check_plan(cards, manifest, preps, R, phase, reg)
    if args.retry and not errors:
        try:
            cards, todo = retry_cards(args.retry, manifest, R, reg, args.board)
        except ValueError as exc:
            errors.append(str(exc))
    if phase == "videos" and not errors and not (args.check or args.dry_run):
        try:
            errors += _unapproved(manifest, R, reg, args.board)
        except (KeyError, kanban.KanbanError) as exc:
            errors.append(f"không kiểm được APPROVE-PREP trên board {args.board}: {exc}")
    if errors:
        print(f"FAIL: kế hoạch card lô {args.batch} có {len(errors)} lỗi")
        for e in errors:
            print(f"  {e}")
        return 1

    canary = cards[0]["video"] if phase == "videos" and cards else None
    if phase == "videos":
        print(f"canary: video {canary}" if canary is not None else "không có video ok — không có card video nào")
    if args.check:
        for c in cards:
            mark = f" (có sẵn {reg['cards'][c['key']]['id']})" if c["key"] in reg["cards"] else ""
            print(f"  {c['key']:<30} {c['title']:<26} {c['assignee']:<13} cha: {', '.join(c['parents']) or '—'}{mark}")
        print(f"PASS: kế hoạch {len(cards)} card (phase {phase}) cho lô {args.batch} trên board {args.board}")
        return 0
    try:
        ids = _materialize(cards, args.board, reg, batch, args.dry_run)
    except kanban.KanbanError as exc:
        print(f"FAIL: {exc} — chạy lại lệnh này để tạo nốt (card đã tạo nằm trong {REGISTRY})")
        return 1
    if todo:
        print("Việc của operator:")
        for line in todo:
            print("  - " + line.replace("{new}", ids[cards[-1]["key"]]))
    print(f"PASS: {'in lệnh' if args.dry_run else 'đã có'} {len(cards)} card cho lô {args.batch} trên board {args.board}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # operator có thể quên PYTHONIOENCODING
    raise SystemExit(main())
