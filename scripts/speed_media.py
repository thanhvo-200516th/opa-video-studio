#!/usr/bin/env python3
"""speed_media — tăng tốc media theo D4 SAU KHI đã cắt hết khoảng lặng: 3 lệnh độc lập, không lệnh nào tự gọi lệnh kia.

  plan  DIR --manifest M --transcripts T [--out media/speed_plan.json] [--speed 1.0|1.05|1.10 | --profile minimal-edu]
        Mỗi cảnh: tiếng = voice_file (B-roll) hoặc tiếng của video_file (A-roll), TRÊN MEDIA GỐC (tốc độ gốc).
        `speech_segments(fps=None)` + `fit_words` + `refine_words` → đoạn giữ + mốc chữ theo giây gốc; tổng giữ lại → `choose_speed`.
        Ghi {kept_src_seconds, speed, speed_dir, scenes:[{seq_prefix, video, voice, src_dur, segs, words}]}.
        Thiếu transcript → báo lệnh `transcribe.py` cần chạy (plan không tự bóc băng).
        --speed ép mức tối đa; --profile minimal-edu lấy mức `speed` của hồ sơ (1.05x), --speed thắng --profile. Cả hai vẫn theo D4:
        video sau tăng tốc < 45 s → 1.0x. Không cờ nào → như cũ (1.10x → 1.05x → 1.0x).
  apply DIR --manifest M [--plan P | --speed 1.10|1.05] [--out media] [--fps 30] [--jobs 2] [--force]
        Tăng tốc cùng một mức cho hình và giọng mọi cảnh → OUT/x110 (hoặc x105), tên file giữ nguyên.
        Mức 1.0 → không ghi gì ("dùng thư mục gốc", D6). Ghi OUT/xNNN/_speed.json.
  check DIR --manifest M [--out media]
        Thoát 1 nếu: độ dài ra lệch > 1 khung so với gốc / tốc độ · lệch hình–tiếng > 1/30 + 0,03 s · không 30 fps ·
        B-roll còn luồng tiếng · khác kích thước gốc.

Mốc timeline = (đoạn / chữ trong plan) chia tốc độ (`build_kit.at_speed`), không cắt file rồi mới tăng tốc (khỏi mã hoá lại lần hai).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_kit import AAC_HQ, ALLOWED_SPEEDS, FFMPEG, MP3_HQ, X264_HQ, choose_speed, refine_words, speed_dir  # noqa: E402
from silence_cut import duration, fit_words, load_words, speech_segments  # noqa: E402
import style_profile  # noqa: E402

PY_CMD = "~/.venvs/video-skills/bin/python"


def fail(msg: str) -> None:
    sys.exit(f"LỖI: {msg}")


def load_segments(manifest: Path) -> list[dict]:
    segs = sorted(json.loads(manifest.read_text(encoding="utf-8")).get("segments", []), key=lambda s: s["seq_index"])
    if not segs:
        fail(f"manifest không có segments: {manifest}")
    return segs


def streams(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate,duration",
                          "-of", "json", str(path)], capture_output=True, text=True).stdout
    info: dict = {}
    for s in json.loads(out or "{}").get("streams", []):
        info.setdefault(s["codec_type"], s)
    return info


# ---------- plan ----------
def pick_speed(kept: float, force: float | None = None, profile: dict | None = None) -> float:
    """Tốc độ của kế hoạch: không ép / không hồ sơ → choose_speed mặc định; có `force` (hoặc profile['speed']) → chỉ thử đúng mức đó,
    không đạt 45 s (D4) thì 1.0."""
    cap = force if force is not None else (profile or {}).get("speed")
    if cap is None:
        return choose_speed(kept)
    if cap not in ALLOWED_SPEEDS:
        raise ValueError(f"tốc độ {cap}x không được phép (D4: chỉ 1.10 / 1.05 / 1.0)")
    return choose_speed(kept, steps=(cap,)) if cap > 1.0 else 1.0


def cmd_plan(a: argparse.Namespace) -> int:
    src, tdir = Path(a.dir), Path(a.transcripts)
    segments = load_segments(Path(a.manifest))
    todo = []
    for s in segments:
        f = s["files"]
        audio = f.get("voice_file") or f["video_file"]
        todo.append((s, audio, tdir / f"{Path(audio).stem}.json"))
    missing = [str(t) for _, _, t in todo if not t.is_file()]
    if missing:
        fail("thiếu transcript (bản gốc, chưa tăng tốc):\n  " + "\n  ".join(missing) +
             f"\nbóc băng bằng: {PY_CMD} scripts/transcribe.py --manifest {a.manifest} --out {tdir.resolve().parent} --language vi")
    scenes, kept = [], 0.0
    for s, audio, tr in todo:
        path = src / audio
        if not path.is_file():
            fail(f"không thấy file {path}")
        words = load_words(tr)
        segs = speech_segments(path, words, fps=None)
        words = refine_words(fit_words(words, segs), str(path))
        kept += sum(b - a_ for a_, b in segs)
        scenes.append({"seq_prefix": s["seq_prefix"], "video": s["files"]["video_file"], "voice": s["files"].get("voice_file"),
                       "src_dur": round(duration(path), 3), "segs": [[a_, b] for a_, b in segs],
                       "words": [{**w, "start": round(w["start"], 3), "end": round(w["end"], 3)} for w in words]})
    speed = pick_speed(kept, a.speed, style_profile.load(name=a.profile) if a.profile else None)
    plan = {"kept_src_seconds": round(kept, 3), "speed": speed, "speed_dir": speed_dir(speed), "scenes": scenes}
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"giữ lại {kept:.2f} s (tốc độ gốc) → {speed}x · {len(scenes)} cảnh · {out}")
    return 0


# ---------- apply ----------
def ffmpeg_cmd(src: Path, dst: Path, f: float, fps: int, kind: str) -> list:
    vf = f"setpts=PTS/{f:.2f},fps={fps}"
    if kind == "voice":
        return [FFMPEG, "-y", "-v", "error", "-nostdin", "-i", src, "-vn", "-af", f"atempo={f:.2f}", *MP3_HQ, dst]
    if kind == "silent":
        return [FFMPEG, "-y", "-v", "error", "-nostdin", "-i", src, "-vf", vf, "-an", *X264_HQ, dst]
    graph = f"[0:v]{vf}[v];[0:a]atempo={f:.2f},aresample=48000:async=1:first_pts=0[a]"
    return [FFMPEG, "-y", "-v", "error", "-nostdin", "-i", src, "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
            *X264_HQ, *AAC_HQ, dst]


def jobs_of(src: Path, segments: list[dict]) -> list[tuple[str, str]]:
    """[(tên file, loại)]: voice = mp3 giọng; silent = hình B-roll (D2, bỏ tiếng); av = A-roll hình + tiếng."""
    out: dict[str, str] = {}
    for s in segments:
        v, vo = s["files"]["video_file"], s["files"].get("voice_file")
        out[v] = "silent" if vo or "audio" not in streams(src / v) else "av"
        if vo:
            out[vo] = "voice"
    return list(out.items())


def cmd_apply(a: argparse.Namespace) -> int:
    src, out = Path(a.dir), Path(a.out)
    plan_path = Path(a.plan) if a.plan else out / "speed_plan.json"
    if a.speed is not None:
        speed = a.speed
    elif plan_path.is_file():
        speed = float(json.loads(plan_path.read_text())["speed"])
    else:
        fail(f"cần --speed hoặc kế hoạch tốc độ ({plan_path}); chạy `speed_media.py plan` trước")
    if speed not in ALLOWED_SPEEDS:
        fail(f"tốc độ {speed}x không được phép (D4: chỉ 1.10 / 1.05, hoặc 1.0 = giữ gốc)")
    if speed == 1.0:
        print("tốc độ 1.0x: dùng thư mục gốc, không tạo media tăng tốc")
        return 0
    dest = out / speed_dir(speed)
    dest.mkdir(parents=True, exist_ok=True)
    todo = jobs_of(src, load_segments(Path(a.manifest)))

    def one(job: tuple[str, str]) -> tuple[str, str]:
        name, kind = job
        if (dest / name).is_file() and not a.force:
            return name, "đã có (bỏ qua, dùng --force để làm lại)"
        r = subprocess.run([str(c) for c in ffmpeg_cmd(src / name, dest / name, speed, a.fps, kind)], capture_output=True, text=True)
        return name, "ok" if r.returncode == 0 else f"LỖI ffmpeg: {r.stderr[-300:]}"

    with ThreadPoolExecutor(max_workers=max(1, a.jobs)) as ex:
        results = list(ex.map(one, todo))
    for name, msg in results:
        print(f"  {name}: {msg}")
    bad = [n for n, m in results if m.startswith("LỖI")]
    meta = {"speed": speed, "fps": a.fps, "files": {n: {"kind": k, "src_dur": round(duration(src / n), 3),
                                                        "out_dur": round(duration(dest / n), 3) if (dest / n).is_file() else None}
                                                    for n, k in todo}}
    (dest / "_speed.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(f"{len(todo) - len(bad)}/{len(todo)} file → {dest}")
    return 1 if bad else 0


# ---------- check ----------
def check_one(src: Path, dst: Path, kind: str, speed: float, fps: int) -> list[str]:
    if not dst.is_file():
        return ["không có file"]
    errs, want = [], duration(src) / speed
    got = duration(dst)
    if abs(got - want) > 1 / fps + (0.03 if kind == "voice" else 0):     # mp3: đệm bộ mã hoá ~ 26 ms
        errs.append(f"độ dài {got:.3f} s, cần {want:.3f} s ± {1 / fps:.3f}")
    info, ref = streams(dst), streams(src)
    if kind == "voice":
        return errs
    v = info.get("video", {})
    if v.get("r_frame_rate") != f"{fps}/1":
        errs.append(f"fps {v.get('r_frame_rate')}, cần {fps}")
    if (v.get("width"), v.get("height")) != (ref.get("video", {}).get("width"), ref.get("video", {}).get("height")):
        errs.append(f"kích thước {v.get('width')}x{v.get('height')} khác gốc")
    if kind == "silent" and "audio" in info:
        errs.append("B-roll còn luồng tiếng (D2)")
    if kind == "av":
        if "audio" not in info:
            errs.append("A-roll mất tiếng")
        else:
            gap = abs(float(v.get("duration", 0)) - float(info["audio"].get("duration", 0)))
            if gap > 1 / 30 + 0.03:
                errs.append(f"lệch hình–tiếng {gap:.3f} s")
    return errs


def cmd_check(a: argparse.Namespace) -> int:
    src, out = Path(a.dir), Path(a.out)
    metas = sorted(out.glob("x*/_speed.json"))
    if not metas:
        plan = out / "speed_plan.json"
        if plan.is_file() and float(json.loads(plan.read_text())["speed"]) == 1.0:
            print("tốc độ 1.0x: dùng thư mục gốc, không có gì để kiểm")
            return 0
        print("LỖI: chưa có media tăng tốc (media/xNNN/_speed.json); chạy `speed_media.py apply` trước")
        return 1
    todo = jobs_of(src, load_segments(Path(a.manifest)))
    fails = 0
    for m in metas:
        speed, fps = json.loads(m.read_text())["speed"], json.loads(m.read_text())["fps"]
        for name, kind in todo:
            errs = check_one(src / name, m.parent / name, kind, speed, fps)
            fails += bool(errs)
            print(f"[{'LỖI' if errs else 'OK'}] {m.parent.name}/{name}" + (f" — {'; '.join(errs)}" if errs else ""))
    print(f"{fails} file lỗi" if fails else "0 lỗi")
    return 1 if fails else 0


def make_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("plan", "apply", "check"):
        p = sub.add_parser(name)
        p.add_argument("dir", help="thư mục media gốc (chứa video_file / voice_file của manifest)")
        p.add_argument("--manifest", required=True, help="00_storyboard_manifest.json")
    sub.choices["plan"].add_argument("--transcripts", required=True, help="thư mục transcript của media gốc (<tên file>.json)")
    sub.choices["plan"].add_argument("--out", default="media/speed_plan.json")
    sub.choices["plan"].add_argument("--speed", type=float, choices=[1.0, 1.05, 1.10], help="ép tốc độ tối đa (D4: <45 s vẫn 1.0)")
    sub.choices["plan"].add_argument("--profile", choices=sorted(style_profile.KNOWN), help="lấy `speed` của hồ sơ (minimal-edu = 1.05)")
    ap_apply = sub.choices["apply"]
    ap_apply.add_argument("--plan", help="speed_plan.json (mặc định OUT/speed_plan.json)")
    ap_apply.add_argument("--speed", type=float, help="ép tốc độ 1.10 / 1.05 / 1.0 (bỏ qua plan)")
    ap_apply.add_argument("--fps", type=int, default=30)
    ap_apply.add_argument("--jobs", type=int, default=2)
    ap_apply.add_argument("--force", action="store_true", help="làm lại file đã có")
    for name in ("apply", "check"):
        sub.choices[name].add_argument("--out", default="media", help="thư mục gốc chứa xNNN (mặc định media)")
    return ap


def main() -> None:
    a = make_parser().parse_args()
    sys.exit({"plan": cmd_plan, "apply": cmd_apply, "check": cmd_check}[a.cmd](a))


if __name__ == "__main__":
    main()
