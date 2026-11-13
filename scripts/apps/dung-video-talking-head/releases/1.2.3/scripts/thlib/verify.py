"""thlib.verify — stage VERIFY (§11.1): chấm V1–V7 tất định trên một dự án đã
BUILD xong. Không tin số BUILD tự báo: mỗi mã đọc lại từ đĩa, và validate_edit /
lint_sfx / check_text_safe / make_report được nạp bằng importlib từ đúng bản
release đã khoá (`rules.lock`), tại `release_root` truyền vào — không assume
co-located với module này (spec §4.3 "chặn các kênh trôi"). Cách ly hiện tại
mới ở mức: nếu `release_root` khác gốc thlib đang chạy, `_load_release_modules`
FAIL rõ ràng thay vì âm thầm chấm nhầm bản (xem docstring hàm đó) — cách ly đa-
release triệt để (sys.modules) còn cần quyết định controller trước khi có bản
release thứ hai.

V1  rules.lock khớp MANIFEST của `release_root` và mọi file của release băm lại
    khớp từng dòng MANIFEST (C10, thlib.manifest.release_errors); không có bản skill che trong
    `profiles/*/skills/**/dung-video-talking-head` (đường quét cố định, chỉ đọc);
    nếu `run()`/CLI được truyền `card_rules` (dòng `RULES: <skill>@<ver>` đọc từ
    thân card, Data Contracts "Card body") thì còn chấm khớp với rules.lock —
    spec §11.1 "rules.lock khớp card". `verify.py`'s CLI interface (Task 13
    brief) không tự đọc card; tham số này để trống (bỏ qua chấm) khi không ai
    truyền vào, và stage.py (Task 14) sẽ là nơi trích `RULES:` từ
    `hermes kanban show` rồi truyền xuống — fix cho finding "V1 không chấm
    khớp card" (fix round 2).
V2  chạy lại validate_edit, lint_sfx (pre-mux + --post-mux L11, luôn kèm
    expected_sha vì lint_sfx.lint_project chạy lại planner), check_text_safe —
    cả ba từ bản release đã khoá.
V3  xcorr(final, mix) và lệch từng cue đọc lại từ out/QA.json (mux.py đã đo);
    mức từng cue so với sfx_plan dùng lại kết quả L5 mà V2 vừa chấm (Ruling R5:
    |đo − (mục tiêu − hụt)| ≤ 0,3 dB, hụt ≤ sfx.max_short_db) — không đo dB
    lần hai.
V4  đo lại loudness S18 (BS.1770 hai kênh) trên final/nobgm/social từ đĩa, đối
    chiếu rules.loudness rồi đối chiếu QA.json (Ruling R35: outputs[...].lufs/
    tp_dbtp) để bắt file đã bị thay hoặc xoá sau mux.
V5  mỗi artifact có schema trong Data Contracts (words/pauses/meta.json của
    INTAKE, edit.json của PLAN, picture_lock/sfx_plan.json của BUILD) có sha8
    hiện tại khớp một dòng nào đó trong STATE.md — chuỗi provenance (§4.2, §10.4).
V6  EDITOR-REPORT.md đủ mọi mục của make_report.SECTIONS; out/PATCHES.md (nếu
    có) rỗng.
V7  ghép out/verify/contact_sheet.png (ffmpeg tile 4×3 = 12 khung từ final.mp4);
    V7 không bao giờ tự FAIL (đúng "chỉ được ghi CONCERN", §11.1). Việc ghép
    thành công KHÔNG tự bịa một CONCERN placeholder nữa (fix round 2 — trước
    đây mọi lần chạy sạch đều bị nhét một CONCERN giả nên không dự án nào đạt
    VERIFIED được): "verifier model xem ảnh rồi điền nhận xét" là việc opa-
    verifier tự làm SAU khi verify.py chạy xong — ghi vào out/verify/v7_concern.txt
    rồi chạy `stage.py VERIFY --finalize` (verify.finalize gộp vào VERDICT, kpi ⇒
    DONE_WITH_CONCERNS), không phải việc run() tự mô phỏng. Hai lỗi cơ học thật sự
    (thiếu out/final.mp4; ffmpeg ghép lỗi) vẫn sinh CONCERN thật ngay, vì đó là
    điều verify.py biết chắc ngay lúc chạy.

REJECTED khi bất kỳ mã nào FAIL; owner_stage lấy theo mã hỏng ĐẦU TIÊN theo thứ
tự V1..V7 (Mã → owner_stage, §10.5). Không mã nào FAIL: DONE_WITH_CONCERNS khi
có LOW_DENSITY (sfx_plan.warnings), LAST_WORD_TIGHT (picture_lock.warnings,
Ruling R31), guess_count > 0, script_match < mapping.script_pass, hoặc CONCERN
của V7 khi ghép contact sheet gặp sự cố cơ học — nếu không thì VERIFIED.
"""

from __future__ import annotations

import importlib.util
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

from . import audio as A
from . import loud
from . import manifest
from . import state
from . import rules as rules_mod
from .rules import Rules

# Đường quét bản skill che (D, chỉ đọc) — cố định, không phụ thuộc release_root.
SHADOW_ROOT = Path("C:/Users/Minh PC/AppData/Local/hermes")
SHADOW_GLOB = "profiles/*/skills/**/dung-video-talking-head"

_RELEASE_MODULES = ("validate_edit", "lint_sfx", "check_text_safe", "make_report")

# Gốc thlib mà CHÍNH module này (thlib.verify) đang chạy — suy từ __file__ như
# thlib.paths.SKILL (đi lên 4 cấp từ releases/<ver>/scripts/thlib/verify.py, Ruling
# R3). Dùng để phát hiện khi `release_root` trỏ tới một cây khác — xem
# _load_release_modules().
_OWN_SKILL_ROOT = Path(__file__).resolve().parents[4]

# Mã lỗi/lint -> owner_stage (§10.5 "Mã → owner_stage"). B01–B21 là B-roll (phát
# hành 1.2.0; B13/B14 đã có từ 1.1.0 qua text-safe) — check_v8 trong 1.2.0 chấm
# B-roll: B20 (chủ PLAN khi thiếu B-roll dù broll_class != none), BUILD khi thiếu
# asset / sha lệch / lock lệch / render không đổi hình.
OWNER_STAGE: dict[str, str] = {
    "S04": "INTAKE", "S28": "INTAKE", "S25-xcorr-source": "INTAKE", "script-match": "INTAKE",
    **{f"L{i}": "BUILD" for i in range(1, 15)},
    "validate_edit": "PLAN", "B21": "PLAN",
    "B13": "PLAN", "B14": "PLAN", "text-safe": "PLAN",
    **{f"B{i:02d}": "B1" for i in range(1, 13)},
    **{f"B{i:02d}": "B2" for i in range(15, 20)},
    "B20": "PLAN",
}
# V1: khoá/manifest lệch, bản skill che, hay card khai RULES lệch rules.lock
# (card sai bản) đều là sự cố hạ tầng/dispatch, không thuộc một stage biên tập
# nào trong bảng trên — gán "dev" (người sửa môi trường/skill/card sinh sai).
V1_OWNER = "dev"
# V5: mỗi artifact có schema trong Data Contracts thuộc về stage đã ghi nó.
V5_ARTIFACT_OWNER: dict[str, str] = {
    "words.json": "INTAKE", "pauses.json": "INTAKE", "meta.json": "INTAKE",
    "face.json": "INTAKE",                                   # track mặt (1.1.1 §8.1)
    "edit.json": "PLAN",
    "picture_lock.json": "BUILD", "sfx_plan.json": "BUILD",
}
V5_RELPATH: dict[str, Path] = {"sfx_plan.json": Path("out") / "sfx_plan.json"}  # còn lại ở gốc dự án

_TP_TOL_DB = 0.01      # sai số đo true peak lặp lại (giống thlib.lint._TP_TOL_DB)
_QA_TOL_DB = 0.05      # QA.json làm tròn 2 số lẻ; lệch quá mức này là QA.json không còn khớp file
CONTACT_TILE = (4, 3)  # 4x3 = 12 khung hình (V7)
_CHECK_IDS = ("V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8")


def _read(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_release_modules(release_root: Path, version: str) -> dict:
    """Nạp validate_edit/lint_sfx/check_text_safe/make_report đúng bản
    `release_root/releases/<version>/scripts` bằng importlib (không `import
    tên` trực tiếp, để không lỡ lấy nhầm bản co-located với module này khi
    release_root là một cây khác — spec §4.3).

    Giới hạn đã biết (chưa xử lý được, cần quyết định controller trước khi có
    bản release thứ hai): một khi gói `thlib` đã bị cache trong sys.modules
    (do chính module thlib.verify này `from . import audio` v.v. ở đầu file),
    bốn script nạp động ở trên vẫn `from thlib import ...` ra đúng cache đó,
    bất kể `release_root` trỏ đi đâu — cách ly triệt để đòi hỏi giữ sys.modules
    bị hoán đổi suốt vòng đời gọi các mod này (kể cả import trễ bên trong, vd
    `thlib.lint.run_post_mux`'s `from .lint_post import ...`), không chỉ lúc
    nạp. Thay vì âm thầm chấm sai bản khi release_root khác gốc đang chạy, hàm
    này FAIL rõ ràng ngay tại đây."""
    release_root = Path(release_root).resolve()
    if release_root != _OWN_SKILL_ROOT:
        raise RuntimeError(
            "release_root=%s khác gốc thlib đang chạy (%s): _load_release_modules "
            "chưa cách ly được sys.modules['thlib'] khỏi tiến trình này (xem docstring "
            "hàm), nên không thể an toàn nạp một bản release khác — chặn lại thay vì "
            "âm thầm chấm nhầm mã của gốc đang chạy." % (release_root, _OWN_SKILL_ROOT))
    scripts_dir = release_root / "releases" / version / "scripts"
    added = str(scripts_dir) not in sys.path
    if added:
        sys.path.insert(0, str(scripts_dir))
    try:
        mods = {}
        for name in _RELEASE_MODULES:
            spec = importlib.util.spec_from_file_location(f"_th_verify_{name}", scripts_dir / f"{name}.py")
            mod = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = mod
            spec.loader.exec_module(mod)
            mods[name] = mod
        return mods
    finally:
        if added:
            sys.path.remove(str(scripts_dir))


def _probe_duration_s(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                          "default=nw=1:nk=1", str(path)], capture_output=True, text=True, check=True).stdout
    return float(out.strip())


# ---------------------------------------------------------------- V1


def check_v1(project: Path, release_root: Path, lock: dict, card_rules: str | None = None) -> dict:
    """`card_rules` = dòng `RULES: <skill>@<ver>` đọc từ thân card (Data
    Contracts "Card body"), do người gọi (stage.py, Task 14) truyền xuống sau
    khi tự đọc `hermes kanban show`. `None` (mặc định — CLI `verify.py` gọi
    tay không có card) bỏ qua chấm khớp card, không FAIL: `verify.py` tự nó
    không có đường đọc card (Task 13 brief's CLI interface), việc khớp card chỉ
    chấm được khi có ai đó truyền vào."""
    problems = []
    if lock.get("skill") != state.SKILL_NAME:
        problems.append(f"rules.lock.skill={lock.get('skill')!r} ≠ {state.SKILL_NAME!r}")
    version = lock.get("version")
    if not version:
        problems.append("rules.lock thiếu version")
    else:                        # C10: băm lại từng file release so với MANIFEST, không chỉ sha MANIFEST
        problems += manifest.release_errors(Path(release_root) / "releases" / version,
                                            lock.get("manifest_sha256"))
    card_checked = card_rules is not None
    if card_checked:
        expected_rules = f"{lock.get('skill')}@{version}"
        if card_rules != expected_rules:
            problems.append(f"card RULES={card_rules!r} ≠ rules.lock {expected_rules!r}")
    shadows = sorted(p.as_posix() for p in SHADOW_ROOT.glob(SHADOW_GLOB)) if SHADOW_ROOT.is_dir() else []
    if shadows:
        problems.append("bản skill che trong profile: " + "; ".join(shadows))
    ok = not problems
    if ok:
        card_note = "khớp card" if card_checked else "card không được cung cấp — bỏ qua chấm khớp card"
        msg = f"rules.lock {version} khớp MANIFEST và từng file release; {card_note}; không có bản skill che"
    else:
        msg = "; ".join(problems)
    if (project / "plan.json").is_file() and (project / "edit.json").is_file():
        drift = plan_drift(project, rules_mod.load(project=project))
        if drift:
            return {"ok": False, "owner_stage": "PLAN", "missing": 0, "msg": drift}

    return {"ok": ok, "msg": msg, "owner_stage": None if ok else V1_OWNER, "missing": 0}


# ---------------------------------------------------------------- V2


def check_v2(project: Path, mods: dict) -> dict:
    problems: list[tuple[str, str]] = []
    lint_results: list[dict] = []
    missing = 0

    try:
        _, edit_errors = mods["validate_edit"].run(project)
    except Exception as exc:      # edit.json hỏng JSON / thiếu file: coi là FAIL của validate_edit
        problems.append((OWNER_STAGE["validate_edit"], f"validate_edit lỗi: {exc}"))
    else:
        if edit_errors:
            problems.append((OWNER_STAGE["validate_edit"], "validate_edit: %d lỗi (vd %s %s)"
                             % (len(edit_errors), edit_errors[0]["code"], edit_errors[0]["msg"])))

    try:
        lint_results = mods["lint_sfx"].lint_project(project, post_mux=True)
    except FileNotFoundError as exc:
        missing_name = Path(exc.filename).name if exc.filename else str(exc)
        owner = V5_ARTIFACT_OWNER.get(missing_name, "BUILD")   # đoán stage từ tên file thiếu
        problems.append((owner, f"lint_sfx: thiếu {exc.filename or exc}"))
        missing += 1
    else:
        bad = [r for r in lint_results if not r["ok"]]
        if bad:
            owner = sorted({OWNER_STAGE.get(r["code"], "BUILD") for r in bad})[0]
            problems.append((owner, "lint_sfx FAIL: " + "; ".join(r["code"] for r in bad)))

    safe_results: list[dict] | None = None
    try:
        safe_results = mods["check_text_safe"].run(project)
    except subprocess.TimeoutExpired:   # R47: still treo quá trần — không chấm, stage.py BLOCK transient
        raise
    except Exception as exc:      # B3: công cụ hỏng (Remotion/Chrome, node_modules, font, lock) — lỗi skill
        problems.append(("BUILD", f"check_text_safe lỗi công cụ (không phải chữ tràn): {exc!r}"))
    else:
        bad_safe = [r for r in safe_results if not r["ok"]]
        if bad_safe:
            problems.append((OWNER_STAGE["text-safe"], "text-safe FAIL %d frame: %s"
                             % (len(bad_safe), ", ".join("f%d" % r["frame"] for r in bad_safe))))

    ok = not problems
    if ok:
        msg = ("validate_edit đạt; lint_sfx %d mã PASS; text-safe %d frame PASS"
               % (len(lint_results), len(safe_results or [])))
    else:
        msg = "; ".join(m for _, m in problems)
    return {"ok": ok, "msg": msg, "owner_stage": None if ok else problems[0][0],
            "lint_results": lint_results, "missing": missing}


# ---------------------------------------------------------------- V3


def check_v3(project: Path, R: Rules, lint_results: list[dict]) -> dict:
    qa_path = project / "out" / "QA.json"
    if not qa_path.is_file():
        return {"ok": False, "msg": "thiếu out/QA.json", "owner_stage": "BUILD", "missing": 1}
    qa = _read(qa_path)
    problems = []
    xmax = R.get("xcorr_max_ms")
    if abs(qa.get("xcorr_ms", math.inf)) > xmax:
        problems.append("xcorr %.3f ms > ±%g ms" % (qa["xcorr_ms"], xmax))
    early, late = R.get("sfx.sync_tol_f.early"), R.get("sfx.sync_tol_f.late")
    bad_cues = [c for c in qa.get("cues", []) if not (-early <= c["offset_f"] <= late)]
    if bad_cues:
        problems.append("cue lệch ngoài −%d/+%d f: %s" % (early, late, ", ".join(c["id"] for c in bad_cues)))
    l5 = next((r for r in lint_results if r["code"] == "L5"), None)
    if l5 is None:
        problems.append("thiếu kết quả L5 để đối chiếu mức với sfx_plan")
    elif not l5["ok"]:
        problems.append("L5 (mức so với sfx_plan, Ruling R5) FAIL: " + l5["msg"])
    ok = not problems
    msg = ("xcorr %+.3f ms (≤ ±%g), %d cue trong −%d/+%d f, mức khớp sfx_plan (L5, Ruling R5)"
           % (qa["xcorr_ms"], xmax, len(qa.get("cues", [])), early, late)) if ok else "; ".join(problems)
    return {"ok": ok, "msg": msg, "owner_stage": None if ok else "BUILD", "missing": 0}


# ---------------------------------------------------------------- V4

_OUTPUT_TARGETS = (("final.mp4", "final_lufs"), ("final-nobgm.mp4", "final_lufs"),
                   ("final-social.mp4", "social_lufs"))


def check_v4(project: Path, R: Rules) -> dict:
    L = R.get("loudness")
    qa_path = project / "out" / "QA.json"
    qa_outputs = _read(qa_path).get("outputs", {}) if qa_path.is_file() else {}
    problems, missing = [], 0
    for name, key in _OUTPUT_TARGETS:
        path = project / "out" / name
        if not path.is_file():
            problems.append(f"thiếu bản xuất out/{name}")
            missing += 1
            continue
        x = A.decode(path)
        lufs = round(A.integrated_lufs(x), 2)
        tp = round(max(A.true_peak_db(x[:, ch]) for ch in range(x.shape[1])), 2)
        target = L[key]
        if abs(lufs - target) > L["tol_lu"]:
            problems.append("%s: %.2f LUFS, cần %g ±%g (S18)" % (name, lufs, target, L["tol_lu"]))
        if tp > L["tp_dbtp"] + _TP_TOL_DB:
            problems.append("%s: TP %.2f dBTP > %g" % (name, tp, L["tp_dbtp"]))
        rec = qa_outputs.get(name)
        if rec is None:
            problems.append(f"{name}: QA.json thiếu bản ghi outputs (Ruling R35)")
        elif abs(lufs - rec["lufs"]) > _QA_TOL_DB or abs(tp - rec["tp_dbtp"]) > _QA_TOL_DB:
            problems.append("%s: đo lại %.2f/%.2f lệch QA.json %.2f/%.2f"
                            % (name, lufs, tp, rec["lufs"], rec["tp_dbtp"]))
    ok = not problems
    msg = ("3 bản xuất đúng " + ", ".join(f"{n}={L[k]:g}±{L['tol_lu']:g} LUFS" for n, k in _OUTPUT_TARGETS)
           ) if ok else "; ".join(problems)
    return {"ok": ok, "msg": msg, "owner_stage": None if ok else "BUILD", "missing": missing}


# ---------------------------------------------------------------- V5


def check_v5(project: Path) -> dict:
    rows = state.read_state(project)
    problems, missing, owner = [], 0, None
    for name, stage in V5_ARTIFACT_OWNER.items():
        path = project / V5_RELPATH.get(name, Path(name))
        if not path.is_file():
            problems.append(f"thiếu {name}")
            missing += 1
            owner = owner or stage
            continue
        sha8 = state.sha8(path)
        if not any(row["files"].get(name) == sha8 for row in rows):
            problems.append(f"{name} sha8={sha8} không khớp dòng STATE.md nào")
            owner = owner or stage
    ok = not problems
    msg = f"{len(V5_ARTIFACT_OWNER)} artifact khớp STATE.md" if ok else "; ".join(problems)
    return {"ok": ok, "msg": msg, "owner_stage": owner, "missing": missing}


# ---------------------------------------------------------------- V6


def check_v6(project: Path, make_report_mod) -> dict:
    report_path = project / "out" / "EDITOR-REPORT.md"
    if not report_path.is_file():
        return {"ok": False, "msg": "thiếu out/EDITOR-REPORT.md", "owner_stage": "BUILD", "missing": 1}
    have = [ln for ln in report_path.read_text(encoding="utf-8").splitlines() if ln.startswith("## ")]
    missing_sections = [s for s in make_report_mod.SECTIONS if s not in have]
    patches = project / "out" / "PATCHES.md"
    patches_dirty = patches.is_file() and bool(patches.read_text(encoding="utf-8").strip())
    problems = []
    if missing_sections:
        problems.append("thiếu mục: " + ", ".join(missing_sections))
    if patches_dirty:
        problems.append("PATCHES.md còn nội dung chưa áp dụng")
    ok = not problems
    msg = (f"đủ {len(make_report_mod.SECTIONS)} mục, PATCHES rỗng" if ok else "; ".join(problems))
    return {"ok": ok, "msg": msg, "owner_stage": None if ok else "BUILD", "missing": 0}


# ---------------------------------------------------------------- V7


def check_v7(project: Path) -> dict:
    """Ghép contact sheet — phần TẤT ĐỊNH duy nhất của V7 mà script này biết
    làm. "Model xem contact sheet; chỉ được ghi CONCERN" (spec §11.1) là việc
    opa-verifier tự làm sau khi verify.py chạy xong (§9 bảng stage), không có
    model nào chạy bên trong verify.py để tự sinh nhận xét thật — nên nhánh
    thành công KHÔNG bịa một CONCERN placeholder nữa (fix round 2: bịa placeholder
    ở mọi lần chạy khiến DONE_WITH_CONCERNS trở thành bắt buộc vĩnh viễn, không
    dự án sạch nào đạt VERIFIED được). Hai nhánh lỗi cơ học dưới đây (thiếu
    final.mp4; ffmpeg lỗi) là CONCERN THẬT — verify.py biết chắc ngay lúc chạy,
    khác với nhận xét hình ảnh mà chỉ model mới đánh giá được.
    1.2.0: Khi picture_lock['broll'] có slot, các khung được chọn = khung giữa MỖI slot
    + các khung chia đều cho phần còn lại, tổng vẫn = 12 khung, sắp theo thời gian."""
    out_dir = project / "out" / "verify"
    out_dir.mkdir(parents=True, exist_ok=True)
    sheet = out_dir / "contact_sheet.png"
    video = project / "out" / "final.mp4"
    if not video.is_file():
        return {"ok": True, "msg": "không có out/final.mp4 để ghép contact sheet",
                "concern": "V7: chưa có out/final.mp4 — verifier model chưa xem được contact sheet",
                "missing": 1}
    cols, rows = CONTACT_TILE
    n = cols * rows
    duration_s = _probe_duration_s(video)
    lock_file = project / "picture_lock.json"
    lock = _read(lock_file) if lock_file.is_file() else {}
    broll_slots = lock.get("broll") or []

    try:
        if not broll_slots:
            loud.ffmpeg(["-y", "-i", str(video), "-vf",
                         f"fps={n}/{duration_s:.6f},scale=320:-2,tile={cols}x{rows}",
                         "-frames:v", "1", str(sheet)])
        else:
            fps = float(lock.get("fps") or 30.0)
            mid_times = []
            for s in broll_slots:
                t_mid = (s["f_in"] + s["f_out"]) / (2.0 * fps)
                mid_times.append(min(max(0.0, t_mid), max(0.0, duration_s - 0.05)))
            
            k = len(mid_times)
            rem = max(0, n - k)
            if rem > 0:
                rem_times = [duration_s * (i + 0.5) / rem for i in range(rem)]
            else:
                rem_times = []
            
            all_times = sorted(mid_times + rem_times)[:n]
            with tempfile.TemporaryDirectory() as tmp_d:
                tmp_dir = Path(tmp_d)
                for idx, t_sec in enumerate(all_times):
                    frame_path = tmp_dir / f"f_{idx:02d}.png"
                    loud.ffmpeg(["-y", "-ss", f"{t_sec:.3f}", "-i", str(video),
                                 "-vf", "scale=320:-2", "-frames:v", "1", str(frame_path)])
                # Ghép tile từ các ảnh đã trích
                loud.ffmpeg(["-y", "-i", str(tmp_dir / "f_%02d.png"),
                             "-vf", f"tile={cols}x{rows}", "-frames:v", "1", str(sheet)])

    except RuntimeError as exc:
        return {"ok": True, "msg": f"ghép contact sheet lỗi: {exc}",
                "concern": "V7: ghép contact_sheet.png lỗi — dev xem lại (không chặn VERIFY)", "missing": 0}
    return {"ok": True, "msg": f"đã ghi {sheet.as_posix()} ({n} khung {cols}x{rows}) — verifier model xem, "
                                "ghi nhận xét vào out/verify/v7_concern.txt nếu có, stage.py VERIFY --finalize gộp "
                                "vào VERDICT (verify.py không tự bịa)",
            "missing": 0}


# ---------------------------------------------------------------- V8


def _frame_gray(video: Path, time_s: float) -> np.ndarray:
    """Trích một khung tại time_s, thu về 270x480 gray (uint8 numpy array)."""
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{time_s:.3f}", "-i", str(video),
           "-vf", "scale=270:480,format=gray", "-frames:v", "1", "-f", "rawvideo", "-"]
    res = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(res.stdout, dtype=np.uint8)


def check_v8(project: Path, R: Rules) -> dict:
    """V8 B-roll (spec 1.2.0 §11):
    FAIL PLAN: meta.broll_class != 'none' mà edit['broll'] rỗng (B20).
    FAIL BUILD:
      - slot của edit không có entry assets.json;
      - file của entry không có;
      - sha256 file != entry;
      - id/frame của picture_lock['broll'] không khớp edit:
          f_out == round(t_out * fps),
          f_in <= round(t_in * fps) và cách <= 1 s;
      - khung giữa slot của out/final.mp4 gần như trùng khung cùng thời điểm của public/master.mp4:
          tách mỗi bên 1 khung (270x480 xám), trung bình |Δ| <= broll.render_diff_min (20)
          => 'B-roll <id> không lên hình'.
    CONCERN:
      - entry fallback true => 'B-roll <id>: clip lỗi (<fallback_reason>), đã dùng ảnh tĩnh'
        (hoặc 'B-roll <id>: clip lỗi, đã dùng ảnh tĩnh' nếu không có fallback_reason);
      - meta.broll_class == 'heavy' => liệt kê asset owner == 'user' của meta.broll_assets
        là 'cảnh thật còn thiếu (R200: AI chỉ minh hoạ)'.
    Video broll_class 'none' và không có slot => V8 PASS 'không có B-roll'."""
    meta_file = project / "meta.json"
    meta = _read(meta_file) if meta_file.is_file() else {}
    broll_class = meta.get("broll_class", "none")

    edit_file = project / "edit.json"
    edit = _read(edit_file) if edit_file.is_file() else {}
    edit_slots = edit.get("broll") or []

    # 1. Kiểm broll_class vs edit.broll
    if broll_class != "none" and not edit_slots:
        return {"ok": False, "owner_stage": "PLAN", "missing": 0,
                "msg": f"B20: video broll_class {broll_class} mà edit.broll rỗng"}

    if broll_class == "none" and not edit_slots:
        return {"ok": True, "owner_stage": None, "missing": 0, "msg": "không có B-roll"}

    # 2. Đọc assets.json và picture_lock.json
    assets_file = project / "public" / "broll" / "assets.json"
    if not assets_file.is_file():
        return {"ok": False, "owner_stage": "BUILD", "missing": 1,
                "msg": "thiếu public/broll/assets.json"}
    assets_data = _read(assets_file)
    assets_list = assets_data.get("assets") or []
    assets_by_id = {a.get("id"): a for a in assets_list}

    lock_file = project / "picture_lock.json"
    if not lock_file.is_file():
        return {"ok": False, "owner_stage": "BUILD", "missing": 1,
                "msg": "thiếu picture_lock.json"}
    lock = _read(lock_file)
    lock_slots = lock.get("broll") or []
    lock_by_id = {s.get("id"): s for s in lock_slots}

    fps = float(R.get("fps") or 30.0)
    final_video = project / "out" / "final.mp4"
    master_video = project / "public" / "master.mp4"

    if not final_video.is_file():
        return {"ok": False, "owner_stage": "BUILD", "missing": 1,
                "msg": "thiếu out/final.mp4"}
    if not master_video.is_file():
        return {"ok": False, "owner_stage": "BUILD", "missing": 1,
                "msg": "thiếu public/master.mp4"}

    render_diff_min = float(R.get("broll.render_diff_min") or 20.0)
    concerns: list[str] = []

    import hashlib

    for s in edit_slots:
        sid = s["id"]
        if sid not in assets_by_id:
            return {"ok": False, "owner_stage": "BUILD", "missing": 1,
                    "msg": f"assets.json thiếu entry cho slot B-roll {sid}"}
        entry = assets_by_id[sid]
        asset_rel = entry.get("file")
        if not asset_rel:
            return {"ok": False, "owner_stage": "BUILD", "missing": 1,
                    "msg": f"entry {sid} trong assets.json không có trường file"}
        asset_file = project / "public" / asset_rel
        if not asset_file.is_file():
            return {"ok": False, "owner_stage": "BUILD", "missing": 1,
                    "msg": f"file {asset_rel} của B-roll {sid} không tồn tại"}
        
        file_sha = hashlib.sha256(asset_file.read_bytes()).hexdigest()
        if file_sha != entry.get("sha256"):
            return {"ok": False, "owner_stage": "BUILD", "missing": 0,
                    "msg": f"sha256 file {asset_rel} ({file_sha}) không khớp entry assets.json ({entry.get('sha256')})"}

        if sid not in lock_by_id:
            return {"ok": False, "owner_stage": "BUILD", "missing": 0,
                    "msg": f"picture_lock.broll thiếu slot {sid}"}
        ls = lock_by_id[sid]
        expected_f_out = int(round(s["t_out"] * fps))
        expected_f_in_nom = int(round(s["t_in"] * fps))
        if ls["f_out"] != expected_f_out:
            return {"ok": False, "owner_stage": "BUILD", "missing": 0,
                    "msg": f"picture_lock slot {sid} f_out ({ls['f_out']}) != round(t_out*fps) ({expected_f_out})"}
        # f_in bám đỉnh cue broll_in (T6) có thể SỚM hoặc MUỘN hơn round(t_in·fps) trong cùng khoảng ngắt (cue pre-hit
        # sát trước từ neo) — chỉ đòi lệch ≤ 1 s và vẫn trước f_out (controller sửa spec §11, 2026-09-23).
        if not (abs(ls["f_in"] - expected_f_in_nom) <= int(round(fps)) and ls["f_in"] < ls["f_out"]):
            return {"ok": False, "owner_stage": "BUILD", "missing": 0,
                    "msg": f"picture_lock slot {sid} f_in ({ls['f_in']}) lệch round(t_in*fps) ({expected_f_in_nom}) quá 1 s "
                           f"hoặc không trước f_out ({ls['f_out']})"}

        # So sánh khung giữa
        t_mid = (s["t_in"] + s["t_out"]) / 2.0
        try:
            fg = _frame_gray(final_video, t_mid)
            mg = _frame_gray(master_video, t_mid)
            if len(fg) != 270 * 480 or len(mg) != 270 * 480:
                raise ValueError("kích thước khung trích xuất không đúng")
            mean_diff = float(np.mean(np.abs(fg.astype(np.float32) - mg.astype(np.float32))))
        except Exception as exc:
            return {"ok": False, "owner_stage": "BUILD", "missing": 0,
                    "msg": f"lỗi khi so sánh khung hình B-roll {sid}: {exc}"}

        if mean_diff <= render_diff_min:
            return {"ok": False, "owner_stage": "BUILD", "missing": 0,
                    "msg": f"B-roll {sid} không lên hình (trung bình |Δ| = {mean_diff:.2f} <= {render_diff_min:g})"}

        if entry.get("fallback"):
            concerns.append(f"B-roll {sid}: clip lỗi ({entry['fallback_reason']}), đã dùng ảnh tĩnh" if entry.get("fallback_reason") else f"B-roll {sid}: clip lỗi, đã dùng ảnh tĩnh")

    if broll_class == "heavy":
        user_assets = [a.get("desc") or a.get("anchor_quote") or "asset"
                       for a in meta.get("broll_assets", [])
                       if a.get("owner") == "user"]
        if user_assets:
            concerns.append(f"cảnh thật còn thiếu (R200: AI chỉ minh hoạ): {', '.join(user_assets)}")

    res = {"ok": True, "owner_stage": None, "missing": 0,
           "msg": f"đủ {len(edit_slots)} slot B-roll hợp lệ, khớp assets và picture_lock, đã lên hình"}
    if concerns:
        res["concerns"] = concerns
    return res


# ---------------------------------------------------------------- điều phối


def face_gate_errors(project: Path) -> list[str]:
    """Lớp chặn thứ hai cho cổng mặt BUILD `face_safe` (spec 1.1.1 §8.3). Dự án có face.json và có ảnh dò chữ
    mang id lớp thì face_safe.json phải tồn tại, phải đã kiểm ít nhất một lớp, và verdict phải PASS — canary
    v16 từng lọt qua mọi cổng vì mặt nạ gắn sai khoá nên cổng mặt PASS mà không kiểm lớp nào."""
    project = Path(project)
    probes_path = project / "out" / "safe" / "text_safe.json"
    if not (project / "face.json").is_file() or not probes_path.is_file():
        return []
    n_probes = sum(1 for e in _read(probes_path) if e.get("layer"))
    if not n_probes:
        return []
    report_path = project / "out" / "safe" / "face_safe.json"
    if not report_path.is_file():
        return [f"FACE_SAFE: thiếu {report_path.as_posix()} dù có {n_probes} ảnh dò chữ"]
    report = _read(report_path)
    if not report.get("layers"):
        return [f"FACE_SAFE: cổng mặt không kiểm lớp chữ nào dù có {n_probes} ảnh dò mang id lớp"]
    if report.get("verdict") != "PASS":
        return [f"FACE_SAFE: verdict {report.get('verdict')} — {len(report.get('violations', []))} khung chữ đè vùng mặt"]
    return []


def plan_drift(project: Path, R) -> str | None:
    """PLAN_DRIFT: ghép lại edit.json từ plan.json bằng compose; khác bản trên đĩa ⇒ có người sửa tay edit.json."""
    from thlib import compose, plan_stage
    inp = plan_stage.plan_inputs(project, R)
    rebuilt, _ = compose.compose(_read(Path(project) / "plan.json"), inp["words"], inp["pauses"], inp["script"], R)
    if rebuilt != _read(Path(project) / "edit.json"):
        return "PLAN_DRIFT: edit.json khác bản ghép lại từ plan.json — có người sửa tay edit.json"
    return None


def plan_notes(project: Path, R) -> tuple[list[str], list[str]]:
    """(info, concerns) về plan.json cho VERDICT: plan trùng đề xuất của code là INFO (không phải
    concern); script lạ trong thư mục video là CONCERN (không REJECT — video đã dựng xong)."""
    info: list[str] = []
    concerns: list[str] = []
    if not (Path(project) / "plan.json").is_file():
        return info, concerns
    from thlib import candidates, plan_stage
    inp = plan_stage.plan_inputs(project, R)
    plan = _read(Path(project) / "plan.json")
    default = candidates.recommended_plan(inp["cands"], inp["ctx"])
    keys = ("hook", "emphasis", "steps", "cta", "hero", "breaks")
    if all(plan.get(k) == default.get(k) for k in keys):
        info.append("PLAN giữ nguyên đề xuất của code")
    strays = plan_stage._find_stray_scripts(project)
    if strays:
        concerns.append("STRAY_SCRIPT: còn script lạ trong thư mục video — " + ", ".join(strays))
    return info, concerns


def run(project: Path, release_root: Path, card_rules: str | None = None) -> dict:
    """Chấm V1–V7 của `project`; trả {"verdict","owner_stage","checks","concerns",
    "missing"}. Không ghi file (CLI verify.py ghi VERDICT.json/.md, kpi.json).
    `card_rules`: dòng `RULES: <skill>@<ver>` của card, nếu có ai truyền vào
    (xem `check_v1`) — mặc định `None`, bỏ qua chấm khớp card."""
    project, release_root = Path(project), Path(release_root)
    try:
        lock = state.read_lock(project)
        R = rules_mod.load(project=project)
    except FileNotFoundError as exc:
        checks = [{"id": cid, "ok": False, "msg": f"không đọc được rules.lock/rules.json: {exc}"}
                  for cid in _CHECK_IDS]
        return {"verdict": "REJECTED", "owner_stage": V1_OWNER, "checks": checks, "concerns": [], "missing": 1, "info": []}

    mods = _load_release_modules(release_root, lock["version"])
    checks: list[dict] = []
    concerns: list[str] = []
    state_box = {"owner_stage": None, "missing": 0}

    def _run_check(cid: str, fn, *args) -> dict:
        try:
            result = fn(*args)
        except subprocess.TimeoutExpired:   # R47: quá thời gian không phải FAIL của check
            raise
        except Exception as exc:      # lỗi chương trình không lường trước: FAIL, không crash verify.py
            result = {"ok": False, "msg": f"lỗi khi chấm {cid}: {exc!r}", "owner_stage": None, "missing": 0}
        checks.append({"id": cid, "ok": result["ok"], "msg": result["msg"]})
        state_box["missing"] += result.get("missing", 0)
        if not result["ok"] and state_box["owner_stage"] is None:
            state_box["owner_stage"] = result.get("owner_stage")
        return result

    _run_check("V1", check_v1, project, release_root, lock, card_rules)
    v2 = _run_check("V2", check_v2, project, mods)
    _run_check("V3", check_v3, project, R, v2.get("lint_results", []))
    _run_check("V4", check_v4, project, R)
    _run_check("V5", check_v5, project)
    _run_check("V6", check_v6, project, mods["make_report"])
    v7 = _run_check("V7", check_v7, project)
    if v7.get("concern"):
        concerns.append(v7["concern"])
    v8 = _run_check("V8", check_v8, project, R)
    if v8.get("concerns"):
        concerns.extend(v8["concerns"])

    missing_total = state_box["missing"]
    face_errors = face_gate_errors(project)
    if face_errors and not any(not c["ok"] for c in checks):
        return {"verdict": "REJECTED", "owner_stage": "BUILD", "checks": checks,
                "concerns": concerns + face_errors, "missing": missing_total, "info": []}
    if any(not c["ok"] for c in checks):
        return {"verdict": "REJECTED", "owner_stage": state_box["owner_stage"], "checks": checks,
                "concerns": concerns, "missing": missing_total, "info": []}

    plan = _read(project / "out" / "sfx_plan.json") if (project / "out" / "sfx_plan.json").is_file() else {}
    lock_json = _read(project / "picture_lock.json") if (project / "picture_lock.json").is_file() else {}
    meta = _read(project / "meta.json") if (project / "meta.json").is_file() else {}

    if any(str(w).startswith("LOW_DENSITY") for w in plan.get("warnings", [])):
        concerns.append("LOW_DENSITY (S26): sfx_plan.warnings có cảnh báo mật độ thấp")
    tight = [w for w in (lock_json.get("warnings") or []) if str(w).startswith("LAST_WORD_TIGHT")]
    if tight:
        concerns.append("Khoá hình (Ruling R31): " + ", ".join(tight))
    guess_count = meta.get("guess_count") or 0
    if guess_count > 0:
        concerns.append(f"{guess_count} từ đoán (words.json có guess:true)")
    script_pass = R.get("mapping.script_pass")
    match = meta.get("script_match")
    if match is not None and match < script_pass:
        concerns.append(f"độ khớp vo_script {match:.4f} < ngưỡng {script_pass:g} (mapping.script_pass)")

    info, plan_concerns = plan_notes(project, R)
    concerns.extend(plan_concerns)

    verdict = "DONE_WITH_CONCERNS" if concerns else "VERIFIED"
    return {"verdict": verdict, "owner_stage": None, "checks": checks, "concerns": concerns,
            "missing": missing_total, "info": info}
