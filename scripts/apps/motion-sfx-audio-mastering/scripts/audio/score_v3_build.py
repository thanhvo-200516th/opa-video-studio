"""Dựng âm V3 (v3-ai-audit): stem, master, build.json, file nghe thử.

python tools/audio/score_v3_build.py
  Cue  : src/audio/cues/v3-ai-audit.json (sinh bằng score_v3_cues.py)
  Stem : out/tmp/V3-AM/audio/{music,sfx,mix}.wav + build.json (+ sfx-master.wav)
  Master: public/audio/v3-ai-audit-master.wav — 48 kHz, mono, pcm_s24le, đúng 960 000 mẫu (20,000 s)
  Nghe thử: out/tmp/V3-AM/preview/{sfx-kit.wav, logo-14-20s.wav, sfx-kit.txt}
Trộn bằng mixbus.mix_detail của V2, master bằng master.master của V2 (I −16 LUFS), trần limiter hạ còn
0,775 (≈ −2,2 dBFS) để true peak ≤ −2 dBTP có dư. Exit 0 = đạt, 1 = master ngoài ngưỡng, 2 = lỗi đầu vào.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

import dsp  # noqa: E402
import master as mst  # noqa: E402
import mixbus  # noqa: E402
import score_v3  # noqa: E402
import score_v3_cues as cues  # noqa: E402
import score_v3_sfx as sfx  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
TARGET_I, I_TOL, TP_MAX = -16.0, 0.3, -2.0
LIMIT = 0.775
TMP = ROOT / "out" / "tmp" / "V3-AM"
PATHS = {"audio": TMP / "audio", "build": TMP / "audio" / "build.json", "preview": TMP / "preview",
         "cues": ROOT / "src" / "audio" / "cues" / f"{cues.SHEET_ID}.json",
         "master": ROOT / "public" / "audio" / f"{cues.SHEET_ID}-master.wav",
         "sfx_master": TMP / "audio" / "sfx-master.wav"}
KIT_GAP_S = 0.45


def md5(path: Path) -> str:
    return hashlib.md5(Path(path).read_bytes()).hexdigest()


def write_preview(sheet: dict) -> None:
    """Bộ nghe thử: mỗi âm mới (và âm V2 dùng lại) một lần, cách KIT_GAP_S, theo gain cue; + đoạn 14–20 s master."""
    out, rows, parts = PATHS["preview"], [], []
    seen = set()
    t = 0.3
    for ev in sheet["events"]:
        if not ev["sound"]:
            continue
        key = (ev["kind"], ev.get("variant"))
        if key in seen and ev["kind"] not in ("tickEject", "tickNum"):
            continue
        seen.add(key)
        clip = mixbus.prep_clip(sfx.render_cue(ev, sheet["id"]), ev["kind"])
        g = 10 ** (mixbus.cue_gain_db(clip, ev["gainDb"]) / 20)
        parts.append((t, clip.x * g))
        rows.append(f"{t:6.2f} s  {ev['id']:<15} {ev['kind']}/{ev.get('variant', '')} gainDb {ev['gainDb']}")
        t += len(clip.x) / dsp.SR + KIT_GAP_S
    kit = np.zeros(int((t + 0.3) * dsp.SR))
    for t0, x in parts:
        s = int(t0 * dsp.SR)
        kit[s:s + len(x)] += x
    kit = dsp.peak_norm(kit, -3.0)
    dsp.write_wav_f32(out / "sfx-kit.wav", kit)
    (out / "sfx-kit.txt").write_text("Bộ nghe thử SFX V3 (đỉnh chuẩn −3 dBFS, giữ tương quan gain cue)\n"
                                     + "\n".join(rows) + "\n", encoding="utf-8")
    m = dsp.read_wav(PATHS["master"])
    dsp.write_wav_f32(out / "logo-14-20s.wav", dsp.fade_edges(m[14 * dsp.SR:], 5.0, 0.0))


def run() -> int:
    sheet = cues.load()
    sid = sheet["id"]
    music = score_v3.render_music(sheet)
    stems, placed = mixbus.mix_detail(sheet, music, sfx.make_render(sid))
    for k in ("music", "sfx", "mix"):
        dsp.write_wav_f32(PATHS["audio"] / f"{k}.wav", stems[k])
    m = mst.master(PATHS["audio"] / "mix.wav", PATHS["master"], target_i=TARGET_I, limit=LIMIT)
    mst.apply_chain(PATHS["audio"] / "sfx.wav", PATHS["sfx_master"], m["gain_db"], LIMIT)
    rec = {"id": sid, "ref_lufs": mixbus.REF_LUFS, "logo_variant": "a", "hit_gap_design_db": None,
           "cues": placed, "silences": sheet["silences"], "sections": sheet["sections"],
           "music_stop_sample": dsp.f2s(next(x["f"] for x in sheet["marks"] if x["id"] == "music-stop")),
           "tail_end_frame": None,
           "master": {"target_i": TARGET_I, "limit": LIMIT, **{k: m[k] for k in ("I", "TP", "LRA", "gain_db")},
                      "passes": m["passes"], "file": PATHS["master"].relative_to(ROOT).as_posix()},
           "md5": {"master": md5(PATHS["master"]), "cues": md5(PATHS["cues"])}}
    PATHS["build"].write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_preview(sheet)
    print(f"master: {PATHS['master']}")
    print(f"  I {m['I']} LUFS (đích {TARGET_I:g}), TP {m['TP']} dBTP, LRA {m['LRA']} LU, G {m['gain_db']} dB, "
          f"{m['passes']} lượt; {len(placed)} cue")
    ok = abs(m["I"] - TARGET_I) <= I_TOL and m["TP"] <= TP_MAX
    if not ok:
        print("FAIL: master ngoài ngưỡng (I ± 0,3 hoặc TP > −2 dBTP)")
    return 0 if ok else 1


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        return run()
    except (ValueError, RuntimeError, OSError) as e:
        print(f"LỖI: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
