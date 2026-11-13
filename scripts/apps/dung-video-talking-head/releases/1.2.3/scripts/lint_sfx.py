"""lint_sfx.py — lint SFX độc lập L1–L14 của một dự án (§5.8, §5.7 bước 9).

Dùng: PYTHONIOENCODING=utf-8 python lint_sfx.py <project_dir> [--post-mux]

Đọc lại mọi thứ từ đĩa: rules.lock → rules.json; words.json, pauses.json,
edit.json, overrides.json (không có = không override), meta.json (preset),
picture_lock.json, out/sfx_plan.json; public/vo-clean.wav, public/sfx_stem.wav,
public/bgm_bed.wav (nếu có); sfx_manifest.json + WAV của release. Chạy lại
planner trên cùng đầu vào để có sha so với sfx_plan (L10), chấm L1–L10,
L12–L14. Chế độ do cờ quyết định, không đoán từ file có sẵn trong out/:
  - không cờ (BUILD trước mux): không đụng tới out/*.mp4 — bản xuất cũ của
    lần build trước không chặn lần build lại;
  - --post-mux (BUILD sau mux, VERIFY): chấm thêm L11; thiếu bản xuất nào
    (out/final*.mp4, public/mix*.wav) là L11 FAIL.
Ghi out/sfx_lint.json, in một dòng mỗi mã, thoát mã 1 khi có mã FAIL
(WARN LOW_DENSITY không làm FAIL).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from thlib import audio, lint, planner, rules, sfxlib


def _load(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def lint_project(project: Path, post_mux: bool = False) -> list[dict]:
    """Chấm lint của dự án `project` (L11 chỉ khi `post_mux`); trả danh sách kết quả."""
    project = Path(project)
    R = rules.load(project=project)
    meta = _load(project / "meta.json") if (project / "meta.json").exists() else {}
    preset = meta.get("preset") or R.get("default_preset")
    overrides_path = project / "overrides.json"
    overrides = _load(overrides_path) if overrides_path.exists() else []
    words, pauses, edit, lock, plan = (_load(project / f) for f in (
        "words.json", "pauses.json", "edit.json", "picture_lock.json", "out/sfx_plan.json"))

    manifest = sfxlib.load_manifest(R.version)
    signals = {k: sfxlib.load_signal(R.version, k) for k in manifest["files"]}
    vo = audio.decode_mono(project / "public" / "vo-clean.wav")
    stem = audio.decode_mono(project / "public" / "sfx_stem.wav")
    bed_path = project / "public" / "bgm_bed.wav"
    bed = audio.decode(bed_path) if bed_path.exists() else None

    fresh, _ = planner.plan(words, pauses, edit, overrides, manifest, signals, vo, R, preset)
    results = lint.run_pre_mux(plan, stem, vo, bed, pauses, lock, manifest, R, preset,
                               expected_sha=lint.plan_sha256(fresh))
    if post_mux:
        results += lint.run_post_mux(project, R)
    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Lint SFX độc lập L1–L14 (đo lại từ stem và vo-clean)")
    ap.add_argument("project", help="Thư mục dự án edit-r<ver>")
    ap.add_argument("--post-mux", action="store_true",
                    help="BUILD sau mux và VERIFY: chấm thêm L11; thiếu bản xuất nào là L11 FAIL")
    args = ap.parse_args(argv)
    project = Path(args.project)

    try:
        results = lint_project(project, post_mux=args.post_mux)
    except FileNotFoundError as exc:
        print(f"FAIL: thiếu file đầu vào của lint: {exc.filename or exc}")
        return 1
    out = project / "out" / "sfx_lint.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for r in results:
        where = "" if r["frame"] is None else " f%d" % r["frame"]
        print("%-4s %s%s  %s" % (r["code"], "PASS" if r["ok"] else "FAIL", where, r["msg"]))
    failed = [r["code"] for r in results if not r["ok"]]
    print("KẾT QUẢ: " + ("FAIL " + ", ".join(failed) if failed else "PASS") + f" — đã ghi {out}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
