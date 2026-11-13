"""QA âm V3 (v3-ai-audit). Dùng lại phép đo của qa_audio_{io,sig,checks}.py (V2); thêm kiểm riêng V3.

python tools/audio/score_v3_qa.py  → out/tmp/V3-AM/qa/{audio.json, audio.md, wave.png, spectrum.png}
Kiểm: định dạng (48 kHz, mono, 24-bit, đúng 960 000 mẫu); I −16 ± 0,3 LUFS, TP ≤ −2 dBTP (ffmpeg + tự đo
oversample 4×), LRA; không clipping; click tại điểm nối (V2 #4) và đầu/cuối file; khoảng lặng (V2 #5); mỗi cue
đúng mốc ±1 ms (đặt riêng từng cue như trên stem: onset / peak / end / manual) và đo lại trên stem sfx (WARN,
vì cue kề chồng nhau); nhạc vào nhẹ, tăng dần tới 15,0, dừng 17,2. Exit 0 = không FAIL, 1 = có FAIL.
"""
from __future__ import annotations

import json
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
from scipy.signal import resample_poly  # noqa: E402

import mixbus  # noqa: E402
import qa_audio_checks as qc  # noqa: E402
import qa_audio_io as qio  # noqa: E402
import qa_audio_sig as sig  # noqa: E402
import score_v3  # noqa: E402
import score_v3_build as B  # noqa: E402
import score_v3_cues as cues  # noqa: E402
import score_v3_sfx as sfx  # noqa: E402

MS = 48                          # 1 ms = 48 mẫu
N_TOTAL = 960000
QA_DIR = B.TMP / "qa"
EARS = "chưa kiểm (không nghe được)"


def chk(cid: str, level: str, ok: bool, value, limit: str, note: str = "") -> dict:
    return qc.chk(cid, level, ok, value, limit, note)


def fmt_checks(path: Path) -> list:
    with wave.open(str(path)) as w:
        sr, ch, bits, n = w.getframerate(), w.getnchannels(), 8 * w.getsampwidth(), w.getnframes()
    return [chk("F1", "FAIL", (sr, ch, bits) == (48000, 1, 24), [sr, ch, bits], "48000 Hz, mono, 24-bit"),
            chk("F2", "FAIL", n == N_TOTAL, n, f"{N_TOTAL} mẫu (20,000 s)", f"{n / 48000:.6f} s")]


def true_peak_db(x: np.ndarray) -> float:
    return sig.peak_db(resample_poly(x, 4, 1))


def loud_checks(lu: dict, master: np.ndarray) -> list:
    tp4 = true_peak_db(master)
    return [chk("L1", "FAIL", abs(lu["I"] - B.TARGET_I) <= B.I_TOL, lu["I"], "−16 ± 0,3 LUFS", "ffmpeg ebur128"),
            chk("L2", "FAIL", lu["TP"] <= B.TP_MAX, lu["TP"], "≤ −2,0 dBTP", "ffmpeg ebur128 peak=true"),
            chk("L2", "FAIL", tp4 <= B.TP_MAX, tp4, "≤ −2,0 dBTP", "tự đo: oversample 4× (resample_poly)"),
            chk("L3", "WARN", 5.0 <= lu["LRA"] <= 8.0, lu["LRA"], "5–8 LU", "LRA (V2 6,5)")]


def clip_checks(master: np.ndarray, mix: np.ndarray) -> list:
    n_hot = int(np.sum(np.abs(master) >= 0.999))
    return [qc.peaks("WAV master", master),
            chk("3", "FAIL", n_hot == 0, n_hot, "0 mẫu ≥ 0,999", "WAV master: đếm mẫu kịch trần"),
            chk("3", "INFO", True, float(np.max(np.abs(mix))), "—", "mix f32 trước master (đỉnh mẫu)")]


def edge_checks(master: np.ndarray) -> list:
    head = float(np.max(np.abs(master[:3 * MS])))
    tail = sig.peak_db(master[-100 * MS:])
    return [chk("E1", "FAIL", abs(master[0]) < 1e-4, float(abs(master[0])), "|mẫu đầu| < 1e-4", "không click đầu"),
            chk("E1", "INFO", True, head, "—", "đỉnh 3 ms đầu (fade-in 3 ms + nhạc vào 0,3 s)"),
            chk("E2", "FAIL", tail < -60.0, tail, "đỉnh 100 ms cuối < −60 dBFS", "không click cuối, im dần"),
            chk("E2", "FAIL", abs(master[-1]) < 1e-4, float(abs(master[-1])), "|mẫu cuối| < 1e-4")]


def _measure_solo(x: np.ndarray, anchor: str, start: int, end: int, manual_w: int) -> int:
    seg = np.abs(x[start:end])
    top = float(seg.max())
    nz = np.nonzero(seg > 1e-6 * top)[0]
    if anchor == "onset":
        return start + int(nz[0])
    if anchor == "end":
        return start + int(nz[-1])
    if anchor == "manual":
        return start + int(np.argmax(seg[:manual_w]))
    return start + int(np.argmax(seg))


def align_solo(sheet: dict) -> list:
    """Mỗi cue đặt riêng (prep + gain + neo đúng như mixbus.mix_detail), đo neo trên bộ đệm 20 s."""
    out = []
    for ev in sheet["events"]:
        if not ev["sound"]:
            continue
        clip = mixbus.prep_clip(sfx.render_cue(ev, sheet["id"]), ev["kind"])
        buf = np.zeros(N_TOTAL)
        na = mixbus.anchor_sample(ev)
        s, e = mixbus.place_at(buf, clip, na, mixbus.cue_gain_db(clip, ev["gainDb"]))
        pre = int(round(sfx.PRE_S * 48000))
        got = _measure_solo(buf, ev["anchor"], s, e, pre + int(0.12 * 48000) + (na - s - clip.anchor))
        off_ms = (got - na) / MS
        out.append(chk("6", "FAIL", abs(off_ms) <= 1.0, off_ms, "±1 ms",
                       f"{ev['id']} {ev['f'] / 30:.3f} s neo {ev['anchor']}"))
        if ev["anchor"] == "end" and "durF" in ev:
            s_ms = (s - sig.f2s(ev["f"] - ev["durF"])) / MS
            out.append(chk("6e", "FAIL", abs(s_ms) <= 1.0 and e <= sig.f2s(ev["f"]), s_ms, "đầu ±1 ms, kết ≤ mốc",
                           f"{ev['id']} chiếm [{(ev['f'] - ev['durF']) / 30:.3f}, {ev['f'] / 30:.3f}) s"))
    return out


def align_stem(sheet: dict, build: dict, sfx_stem: np.ndarray) -> list:
    """Phép đo #6 của V2 trên stem sfx thật (gộp cue cùng frame), báo bằng ms; WARN vì cue kề chồng nhau."""
    anchors = {e["id"]: e["anchor"] for e in sheet["events"]}
    groups = sig.cue_groups([{"id": c["id"], "f": c["f"], "anchor": anchors[c["id"]]} for c in build["cues"]])
    out = []
    for f, anchor, ids, off in sig.align_groups(sfx_stem, groups):
        ms = None if off is None else off * 1600 / MS
        out.append(chk("6s", "WARN", ms is not None and abs(ms) <= 1.0, "không thấy" if ms is None else ms,
                       "±1 ms", f"stem sfx, cách đo V2: {'+'.join(ids)} {f / 30:.3f} s neo {anchor}"))
    return out


def music_checks(sheet: dict, music: np.ndarray) -> list:
    m = score_v3.marks_of(sheet)
    bars = ((0, 2), (2, 4), (4, 6), (6, 8), (8, 10), (10, 12), (12, 14), (14, 15))
    lv = [qc.jnum(score_v3.dsp.lufs_integrated(music[sig.f2s(a * 30):sig.f2s(b * 30)])) for a, b in bars]
    rising = all(y > x for x, y in zip(lv, lv[1:]))
    after = sig.peak_db(music[sig.f2s((m.stop + score_v3.TAIL_S) * 30):])
    stop_rms = sig.rms_db(music[sig.f2s(m.stop * 30):sig.f2s((m.stop + score_v3.TAIL_S) * 30)])
    return [chk("M1", "FAIL", rising, lv, "LUFS mỗi đoạn 0–15 s tăng dần", "stem nhạc: 0–2, 2–4, …, 14–15 s"),
            chk("M2", "WARN", lv[-1] - lv[0] >= 6.0, lv[-1] - lv[0], "≥ 6 LU", "nhạc vào nhẹ: (14–15 s) − (0–2 s)"),
            chk("M3", "FAIL", after < -120.0, after, "< −120 dBFS (đuôi IIR của bus_eq)", f"stem nhạc sau {m.stop + score_v3.TAIL_S:g} s"),
            chk("M3", "INFO", True, stop_rms, "—", f"RMS đuôi vang bus {m.stop:g}–{m.stop + score_v3.TAIL_S:g} s")]


def lint(sheet: dict, build: dict) -> list:
    want = sorted(r[0] for r in cues.MOC if r[6].get("sound", True))
    got = sorted(c["id"] for c in build["cues"])
    return [chk("13", "FAIL", want == got, len(got), f"{len(want)} cue có âm theo bảng mốc",
                ", ".join(sorted(set(want) ^ set(got))))]


def write_md(report: dict) -> None:
    s = report["summary"]
    lines = [f"# QA âm thanh `{report['id']}`", "", f"**Cảm giác nghe: {EARS}.** Minh nghe trên loa điện thoại và "
             "tai nghe trước khi chốt.", "",
             f"- Tổng: {s['pass']} đạt, {s['fail']} FAIL, {s['warn']} WARN", "",
             "| # | Mức | Kết quả | Giá trị | Ngưỡng | Ghi chú |", "|---|---|---|---|---|---|"]
    for c in report["checks"]:
        lines.append(f"| {c['id']} | {c['level']} | {'PASS' if c['pass'] else c['level']} | {c['value']} | "
                     f"{c['limit']} | {c['note']} |")
    (QA_DIR / "audio.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run() -> int:
    sheet, build = cues.load(), qio.load_build(B.PATHS["build"])
    a = B.PATHS["audio"]
    master, mix = qio.read_wav(B.PATHS["master"]), qio.read_wav(a / "mix.wav")
    music, sfx_stem = qio.read_wav(a / "music.wav"), qio.read_wav(a / "sfx.wav")
    lu = qio.ebur128(B.PATHS["master"])
    checks = fmt_checks(B.PATHS["master"]) + loud_checks(lu, master) + clip_checks(master, mix)
    checks += qc.clicks({"sfx": sfx_stem, "music": music}, master, qc.junctions(sheet, build)) + edge_checks(master)
    checks += qc.silences_wav(sheet, mix, music, master, qio.silencedetect(B.PATHS["master"]), build)
    checks += align_solo(sheet) + align_stem(sheet, build, sfx_stem) + music_checks(sheet, music)
    checks += [qc.bass_balance(master)] + lint(sheet, build)
    checks.append(chk("14", "INFO", True, EARS, "—", "cảm giác nghe"))
    fails = sum(1 for c in checks if c["level"] == "FAIL" and not c["pass"])
    warns = sum(1 for c in checks if c["level"] == "WARN" and not c["pass"])
    report = {"id": sheet["id"], "loudness": {k: lu[k] for k in ("I", "TP", "LRA")}, "checks": checks,
              "summary": {"pass": sum(c["pass"] for c in checks), "fail": fails, "warn": warns}, "nghe": EARS}
    QA_DIR.mkdir(parents=True, exist_ok=True)
    (QA_DIR / "audio.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_md(report)
    qio.plots(B.PATHS["master"], QA_DIR, sorted({float(c["f"]) for c in build["cues"]}), int(sheet["totalFrames"]))
    for c in checks:
        print(f"{'PASS' if c['pass'] else c['level']} {c['id']} {c['limit']} {c['value']} {c['note']}".rstrip())
    print(f"TỔNG: {report['summary']['pass']} PASS, {fails} FAIL, {warns} WARN · nghe: {EARS}")
    return 1 if fails else 0


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        return run()
    except (qio.InputError, RuntimeError, ValueError) as e:
        print(f"LỖI: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
