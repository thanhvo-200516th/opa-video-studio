"""QA âm thanh V2 (gói F, KH §3.9 bảng kiểm, TK §7.5).

python tools/audio/qa_audio.py <id> [--wav] [--media <mp4>]
  Mặc định: WAV master + stem; thêm MP4 out/<id>/<id>_9x16.mp4 nếu có. --wav: chỉ WAV.
  Ghi out/<id>/qa/{audio.json, audio.md, wave.png, spectrum.png}.
  #2: tâm I = I đích build.py ghi ở build.json master.target_i (V2 −16, chốt ở Cổng H1), ± 0,3 WAV / ± 0,5 MP4.
  Exit 0 = đạt, 1 = có FAIL, 2 = thiếu file / lỗi đầu vào (kể cả build.json thiếu master.target_i).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import qa_audio_checks as qc  # noqa: E402
import qa_audio_io as qio  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SINGLE_TRIAL = ("8b", "11", "12")
I_TOL_WAV, I_TOL_MP4 = 0.3, 0.5


def layout(root: Path, sid: str) -> dict:
    out = root / "out" / sid
    return {"sheet": root / "src" / "audio" / "cues" / f"{sid}.json",
            "build": out / "audio" / "build.json",
            "music": out / "audio" / "music.wav", "sfx": out / "audio" / "sfx.wav", "mix": out / "audio" / "mix.wav",
            "master": root / "public" / "audio" / f"{sid}-master.wav",
            "sfx_master": root / "public" / "audio" / f"{sid}-sfx-master.wav",
            "media": out / f"{sid}_9x16.mp4", "qa": out / "qa"}


def target_i(build: dict) -> float:
    """I đích của master bản cuối do build.py ghi (chỗ cấu hình duy nhất theo video là build.py)."""
    t = (build.get("master") or {}).get("target_i")
    if t is None:
        raise qio.InputError("build.json thiếu master.target_i (build cũ hoặc --no-master); chạy npm run audio:v2")
    return float(t)


def _vn(v: float) -> str:
    return f"{v:g}".replace("-", "−").replace(".", ",")


def loudness(rows: list, lu: dict, target: float, tol: float, note: str) -> list:
    """Thay dòng I (dòng đầu của qc.loudness_wav/_mp4, tâm cố định −14) bằng tâm = I đích; TP, LRA giữ nguyên."""
    i_row = qc.chk("2", "FAIL", abs(lu["I"] - target) <= tol, lu["I"], f"{_vn(target)} ± {_vn(tol)} LUFS", note)
    return [i_row] + rows[1:]


def wav_checks(p: dict, sheet: dict, build: dict, target: float) -> list:
    master, mix = qio.read_wav(p["master"]), qio.read_wav(p["mix"])
    music, sfx = qio.read_wav(p["music"]), qio.read_wav(p["sfx"])
    lu = qio.ebur128(p["master"])
    checks = loudness(qc.loudness_wav(lu), lu, target, I_TOL_WAV, "WAV master") + [qc.peaks("WAV master", master)]
    if p["sfx_master"].is_file():
        checks.append(qc.peaks("WAV sfx-master", qio.read_wav(p["sfx_master"])))
    checks += qc.clicks({"sfx": sfx, "music": music}, master, qc.junctions(sheet, build))
    checks += qc.silences_wav(sheet, mix, music, master, qio.silencedetect(p["master"]), build)
    checks += qc.alignment(sheet, build, sfx) + qc.end_spans(sheet, build)
    checks += qc.hierarchy(sheet, build, {"mix": mix, "master": master, "sfx": sfx})
    checks += qc.sections(sheet, lu)
    checks.append(qc.bass_balance(master))
    return checks


def media_checks(media: Path, sheet: dict, target: float) -> tuple:
    dur = qio.stream_durations(media)
    if "audio" not in dur or "video" not in dur:
        raise qio.InputError(f"{media}: thiếu dòng audio hoặc video")
    diff_f = abs(dur["audio"] - dur["video"]) * 30.0
    checks = [qc.chk("1", "FAIL", diff_f < 1.0, diff_f, "< 1 f", "lệch thời lượng audio/video MP4")]
    lu = qio.ebur128(media)
    checks += loudness(qc.loudness_mp4(lu), lu, target, I_TOL_MP4, "MP4")
    y = qio.decode_media(media)
    checks.append(qc.peaks("MP4", y))
    checks += qc.silences_mp4(sheet, y)
    off_check, measured = qc.media_offset(sheet, y)
    return checks + [off_check], measured


def summary(checks: list) -> dict:
    fails = [c for c in checks if c["level"] == "FAIL" and not c["pass"]]
    warns = [c for c in checks if c["level"] == "WARN" and not c["pass"]]
    return {"pass": sum(1 for c in checks if c["pass"]), "fail": len(fails), "warn": len(warns)}


def write_md(path: Path, sid: str, report: dict) -> None:
    lines = [f"# QA âm thanh `{sid}`", "", "**CHƯA NGHE BẰNG TAI** — Hùng và Minh phải nghe trên loa điện thoại "
             "và tai nghe trước khi chốt (TK §7.5).", "",
             f"- Tổng: {report['summary']['pass']} đạt, {report['summary']['fail']} FAIL, "
             f"{report['summary']['warn']} WARN",
             f"- Biến thể logo: `{report['logo_variant']}` · tail_end_frame: {report['tail_end_frame']}",
             f"- measured_offset_frames: {report['measured_offset_frames']}",
             f"- Ngưỡng {', '.join(SINGLE_TRIAL)} rút từ một thử nghiệm duy nhất nên chỉ WARN.", "",
             "| # | Mức | Kết quả | Giá trị | Ngưỡng | Ghi chú |", "|---|---|---|---|---|---|"]
    for c in report["checks"]:
        res = "PASS" if c["pass"] else c["level"]
        lines.append(f"| {c['id']} | {c['level']} | {res} | {c['value']} | {c['limit']} | {c['note']} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(root: Path, sid: str, wav_only: bool, media_arg) -> int:
    p = layout(root, sid)
    sheet, build = qio.load_sheet(p["sheet"]), qio.load_build(p["build"])
    target = target_i(build)
    media = Path(media_arg) if media_arg else (p["media"] if p["media"].is_file() and not wav_only else None)
    if media is not None and not media.is_file():
        raise qio.InputError(f"thiếu file: {media}")
    checks = wav_checks(p, sheet, build, target)
    measured = None
    if media is not None:
        mc, measured = media_checks(media, sheet, target)
        checks += mc
    checks += qc.cue_lint(sheet, build) + [qc.ears_note()]
    report = {"id": sid, "checks": checks, "measured_offset_frames": qc.jnum(measured),
              "audio_offset_frames": sheet.get("audioOffsetFrames", 0),
              "audio_offset_new": None if measured is None or abs(measured) < 0.5
              else qc.jnum(float(sheet.get("audioOffsetFrames", 0)) - measured),
              "chua_nghe_bang_tai": True, "single_trial_thresholds": list(SINGLE_TRIAL),
              "logo_variant": build["logo_variant"], "tail_end_frame": build["tail_end_frame"],
              "media": str(media) if media else None, "summary": summary(checks)}
    p["qa"].mkdir(parents=True, exist_ok=True)
    (p["qa"] / "audio.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_md(p["qa"] / "audio.md", sid, report)
    cue_frames = sorted({float(c["f"]) for c in build["cues"]})
    qio.plots(p["master"], p["qa"], cue_frames, int(sheet["totalFrames"]))
    for c in checks:
        res = "PASS" if c["pass"] else c["level"]
        print(f"{res} {c['id']} {c['limit']} {c['value']} {c['note']}".rstrip())
    s = report["summary"]
    print(f"TỔNG: {s['pass']} PASS, {s['fail']} FAIL, {s['warn']} WARN · CHƯA NGHE BẰNG TAI")
    return 1 if s["fail"] else 0


def main(argv=None, root: Path = ROOT) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="QA âm thanh V2")
    ap.add_argument("id")
    ap.add_argument("--wav", action="store_true", help="chỉ kiểm WAV (bỏ MP4)")
    ap.add_argument("--media", help="MP4 đã mux (mặc định out/<id>/<id>_9x16.mp4 nếu có)")
    args = ap.parse_args(argv)
    try:
        return run(Path(root), args.id, args.wav, args.media)
    except (qio.InputError, RuntimeError) as exc:
        print(f"LỖI ĐẦU VÀO: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
