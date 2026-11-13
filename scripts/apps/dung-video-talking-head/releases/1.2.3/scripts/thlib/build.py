"""thlib.build — stage BUILD (§5.7 bước 7–9; S18, S25, S29): từ words/pauses/edit (INTAKE +
PLAN đã xong) tới ba bản xuất, out/QA.json và out/EDITOR-REPORT.md.

Thứ tự cổng (Ruling R27), dừng ở cổng hỏng đầu tiên:
  planner → picture_lock (+ src/data/script.ts) → text_safe → stem_bed → lint_pre_mux
  (L1–L10, L12–L14) → mix → render (hình, --muted) → mux → lint_post_mux (L11) → report.

- planner chạy đúng như lint_sfx.py (JSON đọc lại từ đĩa, overrides.json không có = [],
  vo = audio.decode_mono(public/vo-clean.wav)) để lint ở process khác ra cùng sha (S21,
  L10); out/sfx_plan.json ghi đúng chuỗi lint.plan_json mà plan_sha256 băm.
- lint chấm đúng những gì đã nằm trên đĩa (sfx_plan.json, sfx_stem.wav, bgm_bed.wav,
  picture_lock.json) với expected_sha = sha output planner (L10 không bao giờ BỎ QUA); mix
  trộn đúng các file đó. out/sfx_lint.json cùng dạng lint_sfx.py ghi (sau mux thêm L11).
- chưa chọn nhạc nền (mix.select_bgm → None, trước gate 9): không có bed, bgm_bed.wav của
  lần trước bị xoá; mix.wav và mix-nobgm.wav cùng tiếng, cả hai vẫn được ghi.
- mix.wav / mix-nobgm.wav: vòng R35 dùng chung với social (mix.loudnorm_encoded) — loudnorm 2
  lượt tuyến tính về loudness.final_lufs (limiter true-peak, trần đầu TP đích − 0,5 dB), mã hoá
  AAC thử đúng như mux.py (out/_raw-*.m4a, xoá sau), TP bản thử còn vượt loudness.tp_dbtp thì hạ
  trần rồi làm lại, tối đa loud.TP_TRIES lần; mix thô ghi float (không cắt đỉnh) ở out/_raw-*.wav
  rồi xoá. Bản ghi vòng (số lần, trần cuối) ghi ở out/mix_loudness.json — mux.py chép vào QA.json
  của final / final-nobgm. Cổng 'loudness mix' (S18): I lệch quá tol_lu, TP của WAV vượt đích hay
  bản AAC thử vẫn vượt sau lần cuối ⇒ cổng mix FAIL, trước khi render.
- cảnh báo của khoá hình (LAST_WORD_TIGHT, R31) không dừng BUILD — make_report ghi ra.
- text_safe, render, mux, report là script của release, chạy ở process con. Script thoát mã 2
  (check_text_safe: thiếu node_modules/font, lock hỏng, Remotion lỗi) hay lỗi chương trình ⇒
  kết quả mang tool_error = True (owner dev); mã 1 của text_safe là chữ tràn thật (B3).
- quá thời gian (R47): render_video.py có trần proc.RENDER_TIMEOUT_S ở đây (thlib.proc giết cả
  cây); script thoát mã proc.TIMEOUT_EXIT (still/render bên trong quá hạn) cũng vậy ⇒
  subprocess.TimeoutExpired đi thẳng qua `run` (không phải cổng hỏng) để stage.py BLOCK transient.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import traceback
from functools import partial
from pathlib import Path

import numpy as np
from scipy.io import wavfile

from . import audio as A
from . import broll, lint, loud, mix, paths, picture, planner, proc, sfxlib
from .rules import Rules

SCRIPTS = Path(__file__).resolve().parents[1]    # releases/<ver>/scripts
_LOG_TAIL = 20                                   # số dòng cuối của log script con in ra khi hỏng
_TOOL_EXIT = 2                                   # script của release thoát mã 2 = lỗi công cụ (B3)
SCRIPT_TIMEOUT_S = {"render_video.py": proc.RENDER_TIMEOUT_S}   # R47; text-safe: từng still tự có trần


class BuildError(Exception):
    """Một cổng BUILD không đạt (lint FAIL, script của release thoát mã ≠ 0)."""


class ToolError(BuildError):
    """Cổng hỏng vì công cụ, không vì nội dung: script của release thoát mã 2 (vd
    check_text_safe thiếu node_modules/font, Remotion lỗi) — lỗi skill/máy, owner dev (B3)."""


class AutoHero(Exception):
    """1.2.2 F1: face_safe đã tự áp hero một hàng vào plan.json ⇒ run() dựng lại từ cổng planner."""
    def __init__(self, round_no: int, heroes: list[list[int]]):
        super().__init__(f"tự áp hero một hàng: {json.dumps(heroes)} (vòng {round_no})")
        self.round_no, self.heroes = round_no, heroes



def _read(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: Path, obj) -> Path:
    """JSON thụt lề 2 như lint_sfx.py ghi sfx_lint.json (cùng nội dung ⇒ cùng byte)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _script(project: Path, name: str) -> str:
    """Chạy script `name` của release với đối số <project> ở process con; trả log. Mã thoát
    ≠ 0 ⇒ BuildError kèm các dòng cuối của log (mã 2 ⇒ ToolError); quá SCRIPT_TIMEOUT_S hoặc mã
    proc.TIMEOUT_EXIT ⇒ subprocess.TimeoutExpired (R47)."""
    run = proc.run([sys.executable, str(SCRIPTS / name), str(project)], capture_output=True,
                   text=True, encoding="utf-8", errors="replace",
                   env={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=SCRIPT_TIMEOUT_S.get(name))
    log = (run.stdout + run.stderr).strip()
    if run.returncode != 0:
        tail = "\n".join(log.splitlines()[-_LOG_TAIL:])
        if run.returncode == proc.TIMEOUT_EXIT:
            raise subprocess.TimeoutExpired([name], None, output=tail)
        err = ToolError if run.returncode == _TOOL_EXIT else BuildError
        raise err("%s thoát mã %d:\n%s" % (name, run.returncode, tail))
    return log


def _last_line(log: str) -> str:
    return log.splitlines()[-1] if log else ""


def _require_ok(results: list[dict]) -> None:
    """Có mã lint FAIL ⇒ BuildError liệt kê từng mã (kèm frame vi phạm đầu tiên)."""
    bad = ["%s FAIL%s: %s" % (r["code"], "" if r["frame"] is None else " f%d" % r["frame"], r["msg"])
           for r in results if not r["ok"]]
    if bad:
        raise BuildError("; ".join(bad))


def planner_inputs(project: Path, R: Rules) -> dict:
    """Đầu vào planner, đọc đúng như lint_sfx.py: words/pauses/edit.json, overrides.json
    (không có = []), manifest + tín hiệu SFX của release, vo = decode_mono(vo-clean.wav)."""
    overrides = project / "overrides.json"
    manifest = sfxlib.load_manifest(R.version)
    return {
        "words": _read(project / "words.json"),
        "pauses": _read(project / "pauses.json"),
        "edit": _read(project / "edit.json"),
        "overrides": _read(overrides) if overrides.exists() else [],
        "manifest": manifest,
        "signals": {k: sfxlib.load_signal(R.version, k) for k in manifest["files"]},
        "vo": A.decode_mono(project / "public" / "vo-clean.wav"),
    }


def _layers(project: Path):
    """(stem mono, bed [n, 2] | None) đọc lại từ đĩa — lint và mix dùng đúng file đã ghi."""
    bed = project / "public" / "bgm_bed.wav"
    return A.decode_mono(project / "public" / "sfx_stem.wav"), (A.decode(bed) if bed.exists() else None)


# ------------------------------------------------ các cổng
# Mỗi cổng nhận trạng thái s (dict), trả (khoá mới cho s, file đã ghi, ghi chú in ra).


def _broll_assets(s: dict):
    edit = _read(s["project"] / "edit.json")
    if not edit.get("broll"):
        return {"broll_assets": []}, [], "không có B-roll"
    try:
        res = broll.run(s["project"], edit, s["R"])
    except (broll.BrollGenError, broll.BrollFlatError) as exc:
        raise BuildError(str(exc)) from None
    pub = s["project"] / "public"
    files = [pub / e["file"] for e in res["assets"]] + [pub / "broll" / broll.ASSETS, pub / "broll" / broll.ATTRIBUTION]
    note = "%d asset (%s)" % (len(res["assets"]), ", ".join(f"{e['id']}={e['media']}" for e in res["assets"]))
    if res["warnings"]:
        note += "; cảnh báo: " + "; ".join(res["warnings"])
    return {"broll_assets": res["assets"]}, files, note


def _planner(s: dict):
    inp = planner_inputs(s["project"], s["R"])
    plan, cues_audio = planner.plan(inp["words"], inp["pauses"], inp["edit"], inp["overrides"],
                                    inp["manifest"], inp["signals"], inp["vo"], s["R"], s["preset"])
    path = s["project"] / "out" / "sfx_plan.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(lint.plan_json(plan).encode("utf-8"))
    note = "%d cue OK / %d ứng viên, ngân sách %d" % (len(plan["cues"]), len(plan["candidates"]),
                                                      plan["budget"])
    return {**inp, "plan": plan, "cues_audio": cues_audio, "sha": lint.plan_sha256(plan)}, [path], note


def _picture_lock(s: dict):
    vo = (s["project"] / "vo_script.txt")
    lock = picture.build_lock(s["words"], s["edit"], s["plan"], s["pauses"], s["R"],
                              script=vo.read_text(encoding="utf-8") if vo.is_file() else None,
                              assets=s.get("broll_assets"))
    ts = s["project"] / "src" / "data" / "script.ts"
    files = [_write_json(s["project"] / "picture_lock.json", lock), ts]
    picture.write_script_ts(lock, ts)
    note = "%d f, %d block; cảnh báo: %s" % (lock["duration_f"], len(lock["blocks"]),
                                             ", ".join(lock["warnings"]) or "không có")
    return {"lock": lock}, files, note


def _text_safe(s: dict):
    log = _script(s["project"], "check_text_safe.py")
    return {}, [s["project"] / "out" / "safe" / "text_safe.json"], _last_line(log)


MERGED_PREFIX = "GỘP SẴN — dán THAY đúng các ô này trong plan.json (đã gộp mọi «Sửa:» với plan hiện tại, đã chạy thử --check)"


def _plan_passes(project: Path, R, plan: dict) -> bool:
    """plan qua đủ các bước PLAN --check — chạy trên bản sao đầu vào PLAN (words/pauses/vo_script) trong thư
    mục tạm, không ghi đè edit.json của lần dựng này."""
    import shutil
    import tempfile
    from . import plan_stage
    with tempfile.TemporaryDirectory(prefix="face_room_") as tmp:
        tmp = Path(tmp)
        # R207 (1.2.0): meta.json mang broll_class — thiếu nó thì check coi video là none và mọi gợi ý của plan có B-roll
        # trượt BROLL_FORBIDDEN ⇒ FACE_ROOM «không có gợi ý tự động» (lô b03 video 4, e2e video 2 B-roll).
        for name in ("words.json", "pauses.json", "vo_script.txt", "meta.json"):
            if (project / name).exists():
                shutil.copy(project / name, tmp / name)
        (tmp / "plan.json").write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
        verdict, _, _ = plan_stage.check(tmp, R)
    return verdict == "PASS"


def _face_room_lines(project: Path, R, res: dict) -> list[str]:
    """FACE_ROOM cho MỌI lớp còn bị đè, nối trên một dòng («; »), theo thứ tự thời gian — để agent PLAN
    sửa hết trong một vòng. Mỗi lớp: khung đầu–cuối, mức đè lớn nhất, gợi ý dán được — thẻ chữ lấy mép dòng
    để tách hoặc hero một hàng (R124) — chỉ in gợi ý đã chạy thử qua PLAN --check trên plan.json hiện tại
    (không có plan.json thì không gợi ý); thẻ liệt kê gợi ý bỏ thẻ; viên CTA không có gợi ý tự động."""
    from . import facesafe, segment
    edit_path = project / "edit.json"
    edit_blocks = {b["id"]: b for b in _read(edit_path)["blocks"]} if edit_path.exists() else {}
    plan = _read(project / "plan.json") if (project / "plan.json").exists() else None
    hero_add: list[list[int]] = []
    breaks_add: list[int] = []
    drop_steps = False
    ctx = None
    by_layer: dict[str, list[dict]] = {}
    for v in res["violations"]:
        by_layer.setdefault(v["layer"], []).append(v)
    lines = []
    for lid, mine in sorted(by_layer.items(), key=lambda kv: min(v["frame"] for v in kv[1])):
        k = mine[0]["shot"]
        s0, s1, _ = res["shots"][k]["fitted"]
        label = "toàn" if max(s0, s1) < float(R.get("text.close_min")) else "cận"
        best_break = hero_span = other = None
        if lid in edit_blocks:
            if ctx is None:
                script_path = project / "vo_script.txt"
                script = script_path.read_text(encoding="utf-8") if script_path.exists() else None
                ctx = segment.make_ctx(_read(project / "words.json"), _read(project / "pauses.json"), script, R)
            best_break, hero = facesafe.room_suggestions(edit_blocks[lid], ctx, R) if plan else (None, None)
            if hero and not _plan_passes(project, R, {**plan, "hero": list(plan.get("hero") or []) + [list(hero)]}):
                hero = None
            if hero:
                hero_span, best_break = f"[{hero[0]}, {hero[1]}]", None   # có hero một hàng thì không gợi ý tách
                hero_add.append(list(hero))
            elif best_break is not None and not _plan_passes(
                    project, R, {**plan, "breaks": sorted(set(plan.get("breaks") or []) | {best_break})}):
                best_break = None
            elif best_break is not None:
                breaks_add.append(best_break)
        elif lid == "steps":
            other = '"steps": null'
            drop_steps = plan is not None
        lines.append(facesafe.face_room_error(
            lid, max(v["overlap_px"] for v in mine), k, s0, s1,
            min(v["frame"] for v in mine), max(v["frame"] for v in mine),
            best_break, hero_span, shot_label=label, other_fix=other))
    # R131: agent PLAN dán «"hero": [[a, b]]» THAY cả mảng (canary b01 v51 PLAN a5 mất hai hero của vòng trước) ⇒
    # in thêm một dòng mảng đầy đủ = plan hiện tại + mọi gợi ý, đã chạy thử --check, để dán thay.
    if plan is not None and (hero_add or breaks_add or drop_steps):
        merged, fields = dict(plan), []
        if hero_add:
            merged["hero"] = list(plan.get("hero") or []) + hero_add
            fields.append('"hero": ' + json.dumps(merged["hero"]))
        if breaks_add:
            merged["breaks"] = sorted(set(plan.get("breaks") or []) | set(breaks_add))
            fields.append('"breaks": ' + json.dumps(merged["breaks"]))
        if drop_steps:
            merged["steps"] = None
            fields.append('"steps": null')
        if _plan_passes(project, R, merged):
            lines.append(f"{MERGED_PREFIX}: " + ", ".join(fields))
    return lines


AUTO_HERO_MAX = 2   # 1.2.2 F1: số vòng BUILD tự áp hero một hàng tối đa trong một lần BUILD


def _auto_hero_plan(project: Path, R, res: dict) -> tuple[dict, list[list[int]]] | None:
    """1.2.2 F1: (plan gộp, hero thêm) khi MỌI lớp vi phạm là thẻ chữ có gợi ý hero một hàng qua PLAN --check và plan gộp
    cũng qua --check; còn lại None (để PLAN xử lý như cũ)."""
    from . import facesafe, segment
    if not (project / "plan.json").exists() or not (project / "edit.json").exists():
        return None
    plan = _read(project / "plan.json")
    blocks = {b["id"]: b for b in _read(project / "edit.json")["blocks"]}
    script_path = project / "vo_script.txt"
    script = script_path.read_text(encoding="utf-8") if script_path.exists() else None
    ctx = segment.make_ctx(_read(project / "words.json"), _read(project / "pauses.json"), script, R)
    heroes: list[list[int]] = []
    for lid in dict.fromkeys(v["layer"] for v in res["violations"]):
        if lid not in blocks:
            return None
        _, hero = facesafe.room_suggestions(blocks[lid], ctx, R)
        if not hero or not _plan_passes(project, R, {**plan, "hero": list(plan.get("hero") or []) + [list(hero)]}):
            return None
        heroes.append(list(hero))
    merged = {**plan, "hero": list(plan.get("hero") or []) + heroes}
    return (merged, heroes) if _plan_passes(project, R, merged) else None



def _face_safe(s: dict):
    from . import facesafe
    project, R = s["project"], s["R"]
    face_path = project / "face.json"
    if not face_path.exists():
        return {}, [], "bỏ qua (không có face.json)"
    face_rows = _read(face_path)["rows"]         # face.json = {schema, …, rows, stats}; fit/bands cần đúng mảng rows
    lock_path = project / "picture_lock.json"
    lock = _read(lock_path)

    # Mặt nạ từng lớp: ảnh dò TextOnly của check_text_safe, gắn theo ĐÚNG id lớp ghi trong text_safe.json
    # (fit tra mặt nạ theo id lớp; gắn theo tên file "f69" thì không lớp nào được kiểm mà vẫn PASS).
    masks = {}
    probes_path = project / "out" / "safe" / "text_safe.json"
    if probes_path.exists():
        for probe in _read(probes_path):
            if probe.get("layer") and (probe.get("face_png") or probe.get("png")):
                # 1.2.1 F1: lớp hiện lúc tít hook còn trên hình dùng ảnh dò không hook (face_png) — tít hook miễn luật mặt;
                # đọc ảnh có hook thì tít bị tính là chữ của thẻ đầu (b03 video 6/12/13 phải bỏ hook).
                masks[probe["layer"]] = facesafe.read_alpha_from_file(project / (probe.get("face_png") or probe["png"]))

    res = facesafe.fit(lock, face_rows, R, masks=masks)
    # Ghi ngược picture_lock và script.ts
    lock["shots"] = res["new_lock_shots"]
    ts = project / "src" / "data" / "script.ts"
    files = [_write_json(lock_path, lock), ts]
    picture.write_script_ts(lock, ts)

    # Ghi out/safe/face_safe.json
    out_face_safe = project / "out" / "safe" / "face_safe.json"
    out_face_safe.parent.mkdir(parents=True, exist_ok=True)
    report_data = {
        "verdict": "FAIL" if res["violations"] else "PASS",
        "shots": res["shots"],
        "layers": res["layers"],
        "violations": res["violations"]
    }
    _write_json(out_face_safe, report_data)
    files.append(out_face_safe)

    # Lần thử PLAN sau không đọc được lý do block của BUILD ⇒ ghi các dòng FACE_ROOM ra file để
    # plan_stage.write_draft đưa lên đầu PLAN-SHEET.md (mục §0b), kèm bản sao plan.json vừa dựng — PLAN gộp
    # «Sửa:» vào đúng plan đó (không phải §8) thì sửa của các vòng trước được giữ; PASS thì xoá file cũ.
    room_path = project / "out" / "safe" / "face_room.txt"
    room_plan = project / "out" / "safe" / "face_room_plan.json"
    if res["violations"]:
        round_no = int(s.get("auto_hero_round", 0)) + 1
        auto = _auto_hero_plan(project, R, res) if round_no <= AUTO_HERO_MAX else None
        if auto is not None:
            from . import plan_stage
            merged, heroes = auto
            backup = project / "out" / "safe" / "plan_before_autohero.json"
            if not backup.exists():
                backup.write_bytes((project / "plan.json").read_bytes())
            (project / "plan.json").write_text(json.dumps(merged, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            verdict, _, _ = plan_stage.check(project, R)          # ghi lại edit.json từ plan gộp
            if verdict == "PASS":
                raise AutoHero(round_no, heroes)
            (project / "plan.json").write_bytes(backup.read_bytes())   # không qua ⇒ trả plan cũ, FAIL như cũ
            plan_stage.check(project, R)
        lines = _face_room_lines(project, R, res)
        room_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        if (project / "plan.json").exists():
            room_plan.write_bytes((project / "plan.json").read_bytes())
        raise BuildError("; ".join(lines))
    for stale in (room_path, room_plan):
        if stale.exists():
            stale.unlink()

    n_changed = sum(1 for s_info in res["shots"] if s_info["lever"] != "C0" or s_info["fitted"][2] != 0.0)
    note = f"{len(res['shots'])} shot, {n_changed} shot điều chỉnh scale/y, {len(res['layers'])} lớp chữ đã kiểm"
    return {"lock": lock}, files, note


def _stem_bed(s: dict):
    project, R, vo = s["project"], s["R"], s["vo"]
    stem, bed = project / "public" / "sfx_stem.wav", project / "public" / "bgm_bed.wav"
    A.write_wav(stem, mix.render_stem(s["cues_audio"], len(vo)))
    key = mix.select_bgm(R.version, _read(project / "meta.json")["video"])
    if key is None:
        bed.unlink(missing_ok=True)
        return {}, [stem], "không có nhạc nền (chưa chọn bài)"
    rel = paths.release_dir(R.version)
    track = A.decode(rel / _read(rel / "bgm_manifest.json")["tracks"][key]["path"])
    # P12 + R129: bài bắt đầu ở LRA nhỏ nhất mà lời vẫn trên nền ≥ bgm.st_floor_lu (sàn L12)
    offset, lra = mix.bgm_offset(track, s["lock"]["t_end"], R, vo_mono=vo)
    A.write_wav(bed, mix.bgm_bed(track, vo, s["lock"]["t_end"], R, offset_s=offset))
    return {}, [stem, bed], "nhạc nền %s từ %.1f s, LRA %.1f LU" % (key, offset, lra)


def _lint_pre_mux(s: dict):
    project = s["project"]
    stem, bed = _layers(project)
    results = lint.run_pre_mux(_read(project / "out" / "sfx_plan.json"), stem, s["vo"], bed, s["pauses"],
                               _read(project / "picture_lock.json"), s["manifest"], s["R"], s["preset"],
                               expected_sha=s["sha"])
    path = _write_json(project / "out" / "sfx_lint.json", results)
    _require_ok(results)
    warns = [r["msg"].split("| WARN ", 1)[1] for r in results if "| WARN " in r["msg"]]
    note = "%d mã PASS" % len(results) + (" — WARN " + "; ".join(warns) if warns else "")
    return {"pre": results}, [path], note


def _aac_trial(wav: Path, trial: Path) -> Path:
    """encode của vòng R35 ở cổng mix: mã hoá AAC `wav` đúng như mux.py (loud.AAC_ARGS) ra bản
    thử `trial` — TP bản thử = TP bản xuất mux ghép từ `wav`."""
    loud.ffmpeg(["-y", "-i", str(wav), *loud.AAC_ARGS, str(trial)])
    return trial


def _mix(s: dict):
    project, R = s["project"], s["R"]
    L = R.get("loudness")
    vo = A.decode(project / "public" / "vo-clean.wav")
    stem, bed = _layers(project)
    files, notes, loops = [], [], {}
    for name, layer in (("mix.wav", bed), ("mix-nobgm.wav", None)):
        raw, dst = project / "out" / ("_raw-" + name), project / "public" / name
        trial = raw.with_suffix(".m4a")
        wavfile.write(str(raw), A.SR, mix.mixdown(vo, stem, layer, s["lock"]["t_end"], R).astype(np.float32))
        try:
            got = mix.loudnorm_encoded(raw, dst, L["final_lufs"], L["tp_dbtp"],
                                       partial(_aac_trial, trial=trial))
        except mix.TruePeakError as exc:           # bản AAC thử vẫn vượt sau lần cuối
            got = exc.record
        finally:
            raw.unlink(missing_ok=True)
            trial.unlink(missing_ok=True)
        note = "%s %.2f LUFS / TP %.2f, AAC thử TP %.2f (trần %.2f dBTP, lần %d)" % (
            name, got["lufs"], got["tp_dbtp"], got["encoded_tp_dbtp"], got["ceiling_dbtp"], got["attempts"])
        if (abs(got["lufs"] - L["final_lufs"]) > L["tol_lu"]
                or max(got["tp_dbtp"], got["encoded_tp_dbtp"]) > L["tp_dbtp"]):
            raise BuildError("%s — cần %g ±%g LUFS, TP ≤ %g (S18)" % (note, L["final_lufs"], L["tol_lu"],
                                                                      L["tp_dbtp"]))
        files.append(dst)
        notes.append(note)
        loops[name] = {"attempts": got["attempts"], "ceiling_dbtp": got["ceiling_dbtp"]}
    files.append(_write_json(project / "out" / "mix_loudness.json", loops))
    return {}, files, "; ".join(notes)


def _render(s: dict):
    log = _script(s["project"], "render_video.py")
    return {}, [s["project"] / "out" / "_video.mp4"], _last_line(log)


def _mux(s: dict):
    log = _script(s["project"], "mux.py")
    out = s["project"] / "out"
    return {}, [out / "final.mp4", out / "final-nobgm.mp4", out / "final-social.mp4", out / "QA.json"], \
        _last_line(log)


def _lint_post_mux(s: dict):
    post = lint.run_post_mux(s["project"], s["R"])
    path = _write_json(s["project"] / "out" / "sfx_lint.json", s["pre"] + post)
    _require_ok(post)
    return {}, [path], post[0]["msg"]


def _report(s: dict):
    log = _script(s["project"], "make_report.py")
    return {}, [s["project"] / "out" / "EDITOR-REPORT.md"], _last_line(log)


_STEPS = (("broll_assets", _broll_assets), ("planner", _planner), ("picture_lock", _picture_lock), ("text_safe", _text_safe),
          ("face_safe", _face_safe),
          ("stem_bed", _stem_bed), ("lint_pre_mux", _lint_pre_mux), ("mix", _mix), ("render", _render),
          ("mux", _mux), ("lint_post_mux", _lint_post_mux), ("report", _report))
GATES = tuple(gate for gate, _ in _STEPS)


def _result(failed_gate: str | None, written: list[Path], tool_error: bool = False, msg: str = "") -> dict:
    return {"ok": failed_gate is None, "failed_gate": failed_gate, "tool_error": tool_error, "msg": msg,
            "artifacts": [p.as_posix() for p in dict.fromkeys(written)]}


def run(project: Path, R: Rules, preset: str, on_replan=None, auto_hero_round: int = 0) -> dict:
    """BUILD dự án `project` với bộ luật R và preset. In một dòng mỗi cổng; dừng ở cổng hỏng
    đầu tiên. Trả {"ok", "failed_gate": tên cổng | None, "tool_error": cổng hỏng vì công cụ
    (ToolError hay lỗi chương trình — owner dev, B3) chứ không vì nội dung, "artifacts": file
    các cổng đã đạt ghi ra, theo thứ tự ghi (đường dẫn POSIX)}.
    R221: `on_replan(files)` có thì khi face_safe tự áp hero, gọi nó với [plan.json, edit.json] (stage.py ghi dòng PLAN) rồi
    thoát sớm với "auto_hero": True — lần chạy BUILD sau đi trọn trong 420 s; `auto_hero_round` = số vòng đã tự áp trước đó."""
    s = {"project": Path(project), "R": R, "preset": preset, "auto_hero_round": auto_hero_round}
    written: list[Path] = []
    i = 0
    while i < len(_STEPS):
        gate, step = _STEPS[i]
        try:
            new, files, note = step(s)
        except AutoHero as exc:                      # 1.2.2 F1: plan.json đã gộp hero một hàng ⇒ dựng lại từ planner
            print("BUILD %-13s TỰ ÁP — %s" % (gate, exc))
            # V5 (verify): edit.json phải khớp một dòng STATE.md ⇒ ghi plan/edit mới vào artifact của BUILD
            replanned = [s["project"] / "plan.json", s["project"] / "edit.json"]
            if on_replan is not None:                # R221: stage.py ghi dòng PLAN rồi agent chạy lại BUILD
                on_replan(replanned)
                return {**_result(gate, written + replanned, msg=str(exc)), "auto_hero": True}
            s = {**s, "auto_hero_round": exc.round_no}
            written += replanned
            i = GATES.index("planner")
            continue
        except subprocess.TimeoutExpired:            # R47: treo, không phải cổng hỏng — stage.py BLOCK transient
            print("BUILD %-13s QUÁ THỜI GIAN" % gate)
            raise
        except BuildError as exc:
            print("BUILD %-13s FAIL — %s" % (gate, exc))
            return _result(gate, written, isinstance(exc, ToolError), msg=str(exc))
        except Exception:      # lỗi chương trình (ffmpeg, đầu vào hỏng…): in đủ traceback cho dev
            print("BUILD %-13s LỖI — %s" % (gate, traceback.format_exc().rstrip()))
            return _result(gate, written, True)
        s = {**s, **new}
        written += files
        print("BUILD %-13s PASS — %s" % (gate, note))
        i += 1
    return _result(None, written)
