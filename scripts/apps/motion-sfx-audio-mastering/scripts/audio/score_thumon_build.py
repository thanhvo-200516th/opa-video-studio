"""Dựng âm phim 3D "Thủ môn" BẢN 2 (thu-mon): stem, master, build.json; mux khi có bản hình.

python -X utf8 tools/audio/score_thumon_build.py [--video MP4 --out MP4] [--mux-only --video MP4 --out MP4]
  0) Cue sheet phải khớp events.json + timeline.js (score_thumon_cues --check); lệch → exit 2.
  1) Nhạc (score_thumon_music) + SFX (score_thumon_sfx) trộn bằng mixbus.mix_detail của V2 (REF −20 LUFS, neo, duck,
     EQ bus, khoảng lặng) → film3d/films/thu-mon/out/g6-am/ban2/stem/{music,sfx,mix}.wav (f32).
  2) Master bằng master.master của V2 (volume G → 192 kHz → alimiter → 48 kHz), I −16 LUFS, trần 0,775 như V3 →
     out/g6-am/ban2/thu-mon-master.wav: 48 kHz, mono, pcm_s24le, đúng 1 008 000 mẫu (21,000 s). Bản chỉ SFX qua cùng G.
  3) build.json: md5 events.json / cues / master, số đo master, vị trí từng cue.
  4) Chỉ mux khi truyền --video và --out (quy ước tools/v2w/mux_test.mux: hình copy, AAC 320k, -aac_pns 0, -ac 2,
     +faststart; ghi file tạm, đạt mới thay). Không có bản hình mặc định: hình bản 2 do lead gửi.
  --mux-only --video --out: chỉ mux master đang có (kiểm md5 cues + events.json + master = build.json, lệch → exit 2).
  Đầu ra bản 1 (đã giao 19/10) giữ nguyên ở out/g6-am/ (không bị ghi đè).
Exit 0 = đạt, 1 = master ngoài ngưỡng hoặc mux lệch thời lượng, 2 = lỗi đầu vào.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "v2w"))

import numpy as np  # noqa: E402

import dsp  # noqa: E402
import master as mst  # noqa: E402
import mixbus  # noqa: E402
import score_thumon_cues as C  # noqa: E402
import score_thumon_music as music_mod  # noqa: E402
import score_thumon_sfx as sfx  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
TARGET_I, I_TOL, TP_MAX = -16.0, 0.3, -2.0      # Minh chốt −16 LUFS như V2, V3
LIMIT = 0.775                                    # trần limiter của V3 (≈ −2,2 dBFS)
N_TOTAL = 1_008_000                              # 21,000 s × 48 kHz
OUT = C.FILM / "out" / "g6-am" / "ban2"
PATHS = {"stem": OUT / "stem", "build": OUT / "build.json", "master": OUT / "thu-mon-master.wav",
         "sfx_master": OUT / "stem" / "sfx-master.wav", "qa": OUT / "qa", "ab": C.FILM / "out" / "g6-am" / "ab"}
GROUPS = {  # bus solo (trước master): nhóm SFX theo kind
    "giong-bo": {"snortBo", "land", "push", "hornTok", "flickTok", "slide", "exhale", "teeter", "bob", "inhale"},
    "hung": {"catch", "save"},
    "the-gioi": {"ping", "buzz", "pop", "card", "tickCard", "tickRow", "ffSweep", "strike", "tickUi", "cta"},
    "chuyen-canh": {"whoosh", "riser", "swell"},
    "logo": {"hit", "subdrop", "sonicLogo"},
    "nen": {"bed"},
}


class InputError(Exception):
    """Lỗi đầu vào → exit 2."""


def md5(path: Path) -> str:
    return hashlib.md5(Path(path).read_bytes()).hexdigest()


def rel(path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return Path(path).as_posix()


def with_overrides(sheet: dict, overrides: dict | None) -> dict:
    """Bản sao sheet, ghi đè trường của cue theo id: {"land-3": {"variant": "L/B"}} (cho bộ A/B)."""
    if not overrides:
        return sheet
    unknown = set(overrides) - {e["id"] for e in sheet["events"]}
    if unknown:
        raise ValueError(f"ghi đè cue không có trong sheet: {sorted(unknown)}")
    events = [{**e, **overrides.get(e["id"], {})} for e in sheet["events"]]
    return {**sheet, "events": events}


def render_stems(sheet: dict, music: np.ndarray | None = None, overrides: dict | None = None):
    """(stems {"music","sfx","mix"}, placed) qua mixbus.mix_detail của V2; nhạc dựng lại nếu không truyền."""
    if music is None:
        music = music_mod.render_music(sheet)
    return mixbus.mix_detail(with_overrides(sheet, overrides), music, sfx.make_render(sheet["id"]))


def sfx_group_stems(sheet: dict) -> dict[str, np.ndarray]:
    """Stem SFX tách theo nhóm, đặt và xử lý đúng như mixbus.mix_detail làm với stem sfx (prep, gain, neo, bus_eq,
    khoảng lặng phạm vi mix, fade-in 3 ms); tổng các nhóm = stem sfx."""
    n = int(sheet["totalFrames"]) * dsp.SPF
    render = sfx.make_render(sheet["id"])
    out = {}
    for name, kinds in GROUPS.items():
        bus = np.zeros(n)
        for ev in mixbus.events_for(sheet):
            if ev["kind"] in kinds:
                clip = mixbus.prep_clip(render(ev), ev["kind"])
                mixbus.place_at(bus, clip, mixbus.anchor_sample(ev), mixbus.cue_gain_db(clip, ev["gainDb"]))
        y = mixbus.apply_silences(mixbus.bus_eq(bus), sheet["silences"], "mix")
        out[name] = dsp.fade_edges(y, mixbus.FILE_FADE_IN_MS, 0.0)
    return out


def tail_end_frame(mix: np.ndarray, sheet: dict, db: float = -60.0) -> float:
    """Khung 30 đầu tiên sau logo mà từ đó tới hết file đỉnh mix < db (đo)."""
    logo = next(e["f"] for e in sheet["events"] if e["id"] == "hit-logo")
    lim, spf = 10 ** (db / 20), dsp.SPF
    loud = np.nonzero(np.abs(mix[dsp.f2s(logo):]) >= lim)[0]
    return float(sheet["totalFrames"]) if not len(loud) else round((dsp.f2s(logo) + loud[-1] + 1) / spf, 3)


def check_master(m: dict) -> list[str]:
    msgs = []
    if abs(m["I"] - TARGET_I) > I_TOL:
        msgs.append(f"FAIL I {m['I']} ngoài {TARGET_I} ± {I_TOL}")
    if m["TP"] > TP_MAX:
        msgs.append(f"FAIL TP {m['TP']} > {TP_MAX} dBTP")
    return msgs


def require_fresh_cues() -> dict:
    sheet = C.make()
    probs = C.check(sheet)
    if probs:
        raise InputError("cue sheet lệch events.json / timeline.js:\n  " + "\n  ".join(probs)
                         + "\n→ chạy python -X utf8 tools/audio/score_thumon_cues.py")
    return C.load()


def source_md5() -> dict:
    return {"cues": md5(C.cues_io.sheet_path(C.SHEET_ID)), "events": md5(C.EVENTS_JSON)}


def build(sheet: dict) -> dict:
    """Bước 1–3. Trả bản ghi build.json. md5 nguồn lấy TRƯỚC khi dựng: sửa nguồn giữa chừng thì lần mux sau từ chối."""
    src = source_md5()
    stems, placed = render_stems(sheet)
    for k in ("music", "sfx", "mix"):
        dsp.write_wav_f32(PATHS["stem"] / f"{k}.wav", stems[k])
    m = mst.master(PATHS["stem"] / "mix.wav", PATHS["master"], target_i=TARGET_I, limit=LIMIT)
    mst.apply_chain(PATHS["stem"] / "sfx.wav", PATHS["sfx_master"], m["gain_db"], LIMIT)
    cut2 = [x for x in sheet["marks"] if x["id"] == "music-cut"][-1]["f"]
    rec = {"id": sheet["id"], "ref_lufs": mixbus.REF_LUFS, "logo_variant": "a", "hit_gap_design_db": None,
           "cues": placed, "silences": sheet["silences"], "sections": sheet["sections"],
           "music_stop_sample": dsp.f2s(cut2), "tail_end_frame": tail_end_frame(stems["mix"], sheet),
           "master": {"target_i": TARGET_I, "limit": LIMIT, **{k: m[k] for k in ("I", "TP", "LRA", "gain_db")},
                      "passes": m["passes"], "file": rel(PATHS["master"])},
           "md5": {"master": md5(PATHS["master"]), "sfx_master": md5(PATHS["sfx_master"]), **src},
           "mp4": {}}
    PATHS["build"].parent.mkdir(parents=True, exist_ok=True)
    PATHS["build"].write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"master: {PATHS['master']}")
    print(f"  I {m['I']} LUFS (đích {TARGET_I:g}), TP {m['TP']} dBTP, LRA {m['LRA']} LU, G {m['gain_db']} dB, "
          f"{m['passes']} lượt; {len(placed)} cue; đuôi < −60 dBFS từ khung30 {rec['tail_end_frame']}")
    return rec


def load_build() -> dict:
    if not PATHS["build"].is_file():
        raise InputError(f"thiếu {PATHS['build']}; chạy score_thumon_build.py trước")
    return json.loads(PATHS["build"].read_text(encoding="utf-8"))


def require_same_md5(rec: dict) -> None:
    """Mux / QA / A/B từ chối khi cue sheet, events.json hoặc master đổi sau lần dựng ghi trong build.json."""
    if not PATHS["master"].is_file():
        raise InputError(f"thiếu {PATHS['master']}; chạy score_thumon_build.py")
    have = {**source_md5(), "master": md5(PATHS["master"])}
    bad = [k for k, v in have.items() if rec["md5"].get(k) != v]
    if bad:
        raise InputError(f"md5 {', '.join(bad)} khác build.json: dựng lại âm (score_thumon_build.py)")


def mux_jobs(video: Path | None, out: Path | None) -> list[tuple[Path, Path]]:
    """Một việc mux; bản 2 không có bản hình mặc định nên --video và --out luôn đi cùng nhau."""
    if not (video and out):
        raise InputError("mux cần cả --video <bản hình bản 2> và --out <MP4 ra>")
    return [(Path(video), Path(out))]


def mux_all(rec: dict, jobs: list[tuple[Path, Path]]) -> bool:
    from mux_test import InputError as MuxInput, MuxError, mux   # quy ước mux của dự án (tools/v2w)
    ok = True
    for video, out in jobs:
        if not video.is_file():
            raise InputError(f"thiếu bản hình {video}")
        tmp = out.with_name(out.stem + ".dang-mux.mp4")         # mux vào file tạm, đạt mới thay file giao
        try:
            res = mux(video, PATHS["master"], tmp)
        except MuxInput as e:
            tmp.unlink(missing_ok=True)
            raise InputError(str(e)) from e
        except MuxError as e:
            tmp.unlink(missing_ok=True)
            print(f"FAIL mux {out.name}: {e} (giữ nguyên file cũ)")
            ok = False
            continue
        os.replace(tmp, out)
        rec["mp4"][out.name] = {"file": rel(out), "video": rel(video), "video_md5": md5(video), "md5": md5(out),
                                "video_s": res["video"], "audio_s": res["audio"], "delta_ms": round(res["delta"] * 1000, 3)}
        print(f"mux: {out} · hình {res['video']:.4f} s · âm {res['audio']:.4f} s · lệch {res['delta'] * 1000:.2f} ms")
    PATHS["build"].write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ok


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Dựng âm phim 3D Thủ môn (G6)")
    ap.add_argument("--no-mux", action="store_true", help="(giữ cho tương thích: không có --video thì đã không mux)")
    ap.add_argument("--mux-only", action="store_true")
    ap.add_argument("--video", type=Path)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    try:
        require_fresh_cues()
        if a.mux_only:
            rec = load_build()
            require_same_md5(rec)
            return 0 if mux_all(rec, mux_jobs(a.video, a.out)) else 1
        jobs = mux_jobs(a.video, a.out) if (a.video or a.out) else []
        rec = build(C.load())
        msgs = check_master(rec["master"])
        for s in msgs:
            print(s)
        if msgs:
            print("không mux: master ngoài ngưỡng")
            return 1
        if not jobs:
            print("chưa mux (chưa có bản hình bản 2): khi có hình chạy lại với --mux-only --video <MP4> --out <MP4>")
            return 0
        return 0 if mux_all(rec, jobs) else 1
    except (InputError, C.InputError) as e:
        print(f"LỖI: {e}")
        return 2
    except (ValueError, KeyError, TypeError, RuntimeError, OSError) as e:
        print(f"LỖI: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
