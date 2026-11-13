"""Dựng âm V2: stem f32, build.json, master bản cuối, bản chỉ SFX, bản A/B (gói E, KH §3.9 CLI âm).

python tools/audio/build.py <id> [--logo a|c] [--no-master] [--ab] [--target-i <LUFS>]
  Stem → out/<id>/audio/{music,sfx,mix}.wav + build.json. Master → public/audio/<id>-master.wav, <id>-sfx-master.wav.
  I đích của master bản cuối: target_i_for(<id>) (một chỗ duy nhất theo video; V2 −16 LUFS, chốt ở Cổng H1;
    video khác −14), ghi vào build.json master.target_i để qa_audio đọc.
  --no-master: không master lại; giữ khối master của build.json cũ nếu cùng cues + biến thể logo + I đích.
  --ab: thêm out/<id>/audio-ab/{logo-c,hit-logo-3db,whoosh-windup,pad-tail}.wav qua cùng G (+ ab.json).
  --target-i T: thêm bản so sánh out/<id>/audio-ab/master-<|T|>lufs.wav (mix.wav, cùng chuỗi, I đích T; V2 dùng
    −14) và đo nén RMS 300 ms ở hit/logo của master bản cuối và bản này vào ab.json (khóa loudness_ab).
    Master bản cuối không bị ghi lại bởi tùy chọn này.
  Exit 0 = đạt, 1 = master ngoài ngưỡng (I ± 0,3; TP > −1,5), 2 = lỗi đầu vào / thiếu file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

import cues_io  # noqa: E402
import dsp  # noqa: E402
import master as mst  # noqa: E402
import mixbus  # noqa: E402
import qa_audio_sig as sig  # noqa: E402
import synth  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
I_DEFAULT = -14.0                                  # TK §7.5, cho video chưa chốt mức riêng
I_TARGET_BY_ID = {"v2-khong-bo-sot-khach": -16.0}  # Cổng H1 07/10: "giữ độ đập" (KH mục E.4 (e), hướng 1)
I_TOL = 0.3
TARGET_I_RANGE = (-24.0, -10.0)
TP_FAIL, TP_WARN = -1.5, -2.5
TAIL_DB = -60.0
AB_NAMES = ("logo-c", "hit-logo-3db", "whoosh-windup", "pad-tail")
ID_HIT, ID_LOGO, ID_SONIC = "hit-accent", "hit-logo", "sonic-logo"
LOUD_KEY = "loudness_ab"
LOUD_NOTE = ("Bản so sánh mức master (KH mục E.4 (e)): cùng mix.wav, cùng chuỗi limiter trần 0,79, chỉ đổi I "
             "đích; I đích càng cao limiter càng ép hit. Nghe so với master bản cuối sau khi bù bản nhỏ hơn đúng "
             "chênh I (−16 so với −14: +2 dB). gr_rms300_db = RMS 300 ms từ frame hit/logo của (mix + G) − master, "
             "cùng phép đo qa_audio #8/#9; TK §7.5 muốn ≤ 3–4 dB. Master bản cuối theo target_i_for của build.py "
             "(V2 −16 LUFS, chốt ở Cổng H1), không bị ghi lại.")


def target_i_for(sheet_id: str) -> float:
    """I đích (LUFS) của master bản cuối: chỗ cấu hình duy nhất theo video."""
    return I_TARGET_BY_ID.get(sheet_id, I_DEFAULT)


def paths_for(sheet_id: str, root: Path = ROOT) -> dict:
    out = root / "out" / sheet_id
    return {"cues": root / "src" / "audio" / "cues" / f"{sheet_id}.json", "audio": out / "audio",
            "build": out / "audio" / "build.json", "ab": out / "audio-ab", "tmp": root / "out" / "tmp" / "e",
            "master": root / "public" / "audio" / f"{sheet_id}-master.wav",
            "sfx_master": root / "public" / "audio" / f"{sheet_id}-sfx-master.wav"}


def make_render(sheet_id: str, logo_variant: str) -> Callable[[dict], object]:
    """sonicLogo → sonic_logo của D2 (biến thể theo cờ); mọi kind khác → synth.render_cue."""
    def render(ev: dict):
        if ev["kind"] == "sonicLogo":
            import sonic_logo  # D2; nạp muộn để test đơn vị không cần D2
            return sonic_logo.sonic_logo(logo_variant, seed=f"{sheet_id}:{ev['id']}")
        return synth.render_cue(ev, sheet_id)
    return render


def default_music(sheet: dict, tail_pad: bool = False) -> np.ndarray:
    import score_v2  # D2
    return score_v2.render_music(sheet, tail_pad=tail_pad)


def md5_file(path: Path) -> str | None:
    p = Path(path)
    return hashlib.md5(p.read_bytes()).hexdigest() if p.is_file() else None


def tail_end_frame(mix: np.ndarray, sheet: dict) -> int:
    """Frame đầu tiên sau LOGO mà đỉnh mix trong frame < −60 dBFS (đo); không có → totalFrames."""
    logo = next(e["f"] for e in sheet["events"] if e["id"] == ID_LOGO)
    spf, lim = dsp.f2s(1), 10 ** (TAIL_DB / 20)
    for f in range(int(np.floor(logo)) + 1, int(sheet["totalFrames"])):
        if np.max(np.abs(mix[f * spf:(f + 1) * spf])) < lim:
            return f
    return int(sheet["totalFrames"])


def music_stop_sample(sheet: dict) -> int:
    return dsp.f2s(next(m["f"] for m in sheet["marks"] if m["id"] == "music-stop"))


def sheet_logo_variant(sheet: dict) -> str:
    return next(e.get("variant", "a") for e in sheet["events"] if e["id"] == ID_SONIC)


def _read_json(path: Path) -> dict | None:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _merge_json(path: Path, patch: dict) -> None:
    """Ghi các khóa của patch, giữ các khóa khác đã có trong file."""
    _write_json(path, {**(_read_json(path) or {}), **patch})


def _rel(path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return Path(path).as_posix()


def check_master(m: dict, target_i: float) -> tuple[bool, list[str]]:
    """Mức chung E/F: |I − đích| ≤ 0,3; TP > −1,5 FAIL; TP < −2,5 chỉ WARN."""
    ok, msgs = True, []
    if abs(m["I"] - target_i) > I_TOL:
        ok = False
        msgs.append(f"FAIL I {m['I']} ngoài {target_i} ± {I_TOL}")
    if m["TP"] > TP_FAIL:
        ok = False
        msgs.append(f"FAIL TP {m['TP']} > {TP_FAIL} dBTP")
    elif m["TP"] < TP_WARN:
        msgs.append(f"WARN TP {m['TP']} < {TP_WARN} dBTP (limiter ít làm việc, không hỏng)")
    return ok, msgs


def write_ab(sheet: dict, p: dict, music: np.ndarray, music_fn: Callable, gain_db: float, logo: str) -> dict:
    """4 bản A/B qua cùng chuỗi master G; trả thông tin từng bản."""
    info = {}
    for name in AB_NAMES:
        mus = music_fn(sheet, tail_pad=True) if name == "pad-tail" else music
        render = make_render(sheet["id"], "c" if name == "logo-c" else logo)
        ab = name if name in mixbus.AB_EVENTS else None
        stems, _ = mixbus.mix_detail(sheet, mus, render, ab)
        tmp = p["tmp"] / "ab" / f"{name}-mix.wav"
        dsp.write_wav_f32(tmp, stems["mix"])
        mst.apply_chain(tmp, p["ab"] / f"{name}.wav", gain_db)
        info[name] = {"logo_variant": "c" if name == "logo-c" else logo,
                      "hit_gap_design_db": mixbus.hit_gap_db(mixbus.events_for(sheet, ab)),
                      "tail_end_frame": tail_end_frame(stems["mix"], sheet)}
    _merge_json(p["ab"] / "ab.json", {"gain_db": gain_db, "variants": info})
    return info


def gain_reduction_db(mix: np.ndarray, out: np.ndarray, gain_db: float, f: float) -> float:
    """Mức limiter ép RMS 300 ms từ frame f: (mix + G) − master (cùng phép đo qa_audio #8/#9)."""
    return round(sig.rms300_db(mix, f) + gain_db - sig.rms300_db(out, f), 2)


def loud_ab_path(p: dict, target_i: float) -> Path:
    return p["ab"] / f"master-{abs(target_i):g}lufs.wav"


def _loud_entry(path: Path, m: dict, target_i: float, mix: np.ndarray, frames: list) -> dict:
    out = dsp.read_wav(path)
    return {"file": _rel(path), "md5": md5_file(path), "target_i": target_i,
            **{k: m[k] for k in ("I", "TP", "LRA", "gain_db")},
            "gr_rms300_db": {f"f{f:g}": gain_reduction_db(mix, out, float(m["gain_db"]), f) for f in frames}}


def write_loud_ab(sheet: dict, p: dict, rec: dict, target_i: float) -> tuple[bool, dict]:
    """Bản so sánh mức: master mix.wav với I đích target_i vào audio-ab/ (master bản cuối không đụng);
    đo nén ở hit và logo cho master bản cuối (G, I đích trong rec) và bản này; gộp vào ab.json, giữ mục cũ."""
    out = loud_ab_path(p, target_i)
    m = mst.master(p["audio"] / "mix.wav", out, target_i=target_i)
    ok, msgs = check_master(m, target_i)
    for s in msgs:
        print(s)
    mix = dsp.read_wav(p["audio"] / "mix.wav")
    frames = [e["f"] for e in sheet["events"] if e["id"] in (ID_HIT, ID_LOGO)]
    info = {"note": LOUD_NOTE, "masters": {
        p["master"].stem: _loud_entry(p["master"], rec["master"], rec["master"]["target_i"], mix, frames),
        out.stem: _loud_entry(out, m, target_i, mix, frames)}}
    _merge_json(p["ab"] / "ab.json", {LOUD_KEY: info})
    return ok, info


def run_build(sheet: dict, p: dict, music_fn: Callable, logo: str, do_master: bool, do_ab: bool,
              loud_i: float | None = None) -> int:
    """Lõi build (CLI và thử nghiệm đều gọi). Trả mã thoát."""
    sid = sheet["id"]
    target = target_i_for(sid)
    music = music_fn(sheet, tail_pad=False)
    stems, placed = mixbus.mix_detail(sheet, music, make_render(sid, logo))
    for k in ("music", "sfx", "mix"):
        dsp.write_wav_f32(p["audio"] / f"{k}.wav", stems[k])
    md5_cues = md5_file(p["cues"])
    rec = {"ref_lufs": mixbus.REF_LUFS, "logo_variant": logo,
           "hit_gap_design_db": mixbus.hit_gap_db(mixbus.events_for(sheet)),
           "cues": placed, "silences": sheet["silences"], "sections": sheet["sections"],
           "music_stop_sample": music_stop_sample(sheet), "tail_end_frame": tail_end_frame(stems["mix"], sheet),
           "master": None, "md5": {"master": None, "sfx_master": None, "cues": md5_cues}}
    code = 0
    if do_master:
        m = mst.master(p["audio"] / "mix.wav", p["master"], target_i=target)
        mst.apply_chain(p["audio"] / "sfx.wav", p["sfx_master"], m["gain_db"])
        rec["master"] = {"target_i": target, **{k: m[k] for k in ("I", "TP", "LRA", "gain_db")}}
        rec["md5"].update(master=md5_file(p["master"]), sfx_master=md5_file(p["sfx_master"]))
        ok, msgs = check_master(m, target)
        for s in msgs:
            print(s)
        code = 0 if ok else 1
        print(f"master: I {m['I']} LUFS (đích {target:g}), TP {m['TP']} dBTP, LRA {m['LRA']} LU, "
              f"G {m['gain_db']} dB, {m['passes']} lượt")
    else:
        prev = _read_json(p["build"]) or {}
        same = prev.get("md5", {}).get("cues") == md5_cues and prev.get("logo_variant") == logo
        if same and (prev.get("master") or {}).get("target_i") == target:
            rec["master"] = prev["master"]
            rec["md5"].update(master=prev["md5"].get("master"), sfx_master=prev["md5"].get("sfx_master"))
    _write_json(p["build"], rec)
    print(f"stem: {p['audio']} ({len(placed)} cue, logo {logo}, tail_end_frame {rec['tail_end_frame']})")
    if do_ab:
        if not rec["master"]:
            print("LỖI: --ab cần G của master (chạy npm run audio:v2 trước)")
            return 2
        write_ab(sheet, p, music, music_fn, float(rec["master"]["gain_db"]), logo)
        print(f"A/B: {p['ab']} ({', '.join(AB_NAMES)})")
    if loud_i is not None:
        if not rec["master"] or not p["master"].is_file():
            print("LỖI: --target-i cần master bản cuối cùng cues (chạy npm run audio:v2 trước)")
            return 2
        ok, info = write_loud_ab(sheet, p, rec, loud_i)
        code = max(code, 0 if ok else 1)
        for name, e in info["masters"].items():
            gr = ", ".join(f"{k} {v} dB" for k, v in e["gr_rms300_db"].items())
            print(f"{name}: I {e['I']} LUFS, TP {e['TP']} dBTP, G {e['gain_db']} dB; limiter ép RMS 300 ms {gr}")
    return code


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Dựng âm V2 (gói E)")
    ap.add_argument("sheet_id")
    ap.add_argument("--logo", choices=("a", "c"), default=None)
    ap.add_argument("--no-master", action="store_true")
    ap.add_argument("--ab", action="store_true")
    ap.add_argument("--target-i", type=float, default=None)
    a = ap.parse_args()
    if a.target_i is not None and not TARGET_I_RANGE[0] <= a.target_i <= TARGET_I_RANGE[1]:
        print(f"LỖI: --target-i {a.target_i} ngoài [{TARGET_I_RANGE[0]}, {TARGET_I_RANGE[1]}] LUFS")
        return 2
    try:
        sheet = cues_io.load_sheet(a.sheet_id)
    except ValueError as e:
        print(f"LỖI cues: {e}")
        return 2
    try:
        return run_build(sheet, paths_for(a.sheet_id), default_music, a.logo or sheet_logo_variant(sheet),
                         not a.no_master, a.ab, a.target_i)
    except ImportError as e:
        print(f"LỖI: thiếu module của gói khác ({e}); cần score_v2.py / sonic_logo.py (D2)")
        return 2
    except (ValueError, RuntimeError) as e:
        print(f"LỖI: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
