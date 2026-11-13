"""QA âm phim 3D "Thủ môn" (G6). Dùng lại phép đo qa_audio_{io,sig,checks} của V2; thêm kiểm riêng của phim.

python -X utf8 tools/audio/score_thumon_qa.py [--no-mp4]
  → film3d/films/thu-mon/out/g6-am/ban2/qa/{audio.json, audio.md, sync.json, wave.png, spectrum.png, pho-cue.png}
Nhóm kiểm áp được cho phim này (mã giữ như V2/V3):
  F1 F2  định dạng: 48 kHz, mono, 24-bit, đúng 1 008 000 mẫu (21,000 s)
  L1 L2 L3  I −16 ± 0,3 LUFS; TP ≤ −2 dBTP (ffmpeg + tự đo oversample 4×); LRA 5–8 LU (WARN)
  3  không kịch trần · 4 click tại điểm nối (V2 #4, thêm mốc cắt / nối nhạc) · E1 E2 đầu / cuối file (V3)
  5  khoảng lặng khai báo (V2 #5) · 6 neo ±1 ms khi đặt riêng (V3) · 6s neo trên stem sfx (WARN: cue chồng)
  S  đồng bộ va chạm +1 f60: trung vị 16,7 ± 2 ms; từng tiếng 8–25 ms; < 0 hoặc > 33 ms FAIL (cue chồng: WARN)
  G  limiter: ép RMS 300 ms ở cú lớn ≤ 3 dB (WARN > 3, FAIL > 4); ép tối đa cửa sổ 5 ms (WARN > 3)
  B  bus solo trước master (I, TP, PLR); PLR mix ≤ 14,5 dB (WARN); đoạn hành động nhạc − SFX ≤ 2 LU (WARN)
  P  mỗi tiếng ping báo tin nổi trên nhạc ≥ 2 dB: qua EQ bus như trong mix, RMS 105 ms quanh đỉnh, cùng dải 150 Hz–2 kHz
     (FAIL); ghi thêm cả dải và so với mọi tiếng khác
  O  ≤ 3 onset SFX mỗi 250 ms (cue cùng khung tính một) (WARN); hai tiếng liền cùng kind không giống hệt (FAIL)
  11 mức đoạn (đêm không lặng chết, đuôi tự nhiên tới 21 s) · 9 logo nổi hơn thân đoạn đuổi (V2 #9, cả loa điện thoại)
  12 cân trầm (V2) · 13 lint cue · 14 CHƯA NGHE BẰNG TAI
  1 2 7  MP4: lệch thời lượng a/v, I ± 0,5 / TP / LRA, âm MP4 thẳng hàng master (V2 #7 phỏng theo), đồng bộ trên MP4 (INFO)
Exit 0 = không FAIL, 1 = có FAIL, 2 = lỗi đầu vào.
"""
from __future__ import annotations

import argparse
import json
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

import dsp  # noqa: E402
import mixbus  # noqa: E402
import qa_audio_checks as qc  # noqa: E402
import qa_audio_io as qio  # noqa: E402
import qa_audio_sig as sig  # noqa: E402
import score_thumon_build as B  # noqa: E402
import score_thumon_cues as C  # noqa: E402
import score_thumon_meas as M  # noqa: E402
import score_thumon_plot as P  # noqa: E402
import score_thumon_sfx as SFX  # noqa: E402

EARS = "CHƯA NGHE BẰNG TAI"
MS = 48
BIG_HITS = ("land-4", "catch-b6", "catch-b7", "tick-thesis", "exhale-flood", "hit-logo")
PING_MIN_DB = 2.0                 # điều phối 21/10: tin nhắn tới là ý chính của phim
chk = qc.chk


def action_span(sheet: dict) -> tuple[float, float]:
    """Đoạn hành động (bản 2): đầu section build (bass, kick vào, hứng tin) → hết section full (tua đêm xong), giây."""
    sec = {s["name"]: s for s in sheet["sections"]}
    return sec["build"]["from"] / 30, sec["full"]["to"] / 30


def fmt_checks(path: Path) -> list:
    with wave.open(str(path)) as w:
        sr, ch, bits, n = w.getframerate(), w.getnchannels(), 8 * w.getsampwidth(), w.getnframes()
    return [chk("F1", "FAIL", (sr, ch, bits) == (48000, 1, 24), [sr, ch, bits], "48000 Hz, mono, 24-bit"),
            chk("F2", "FAIL", n == B.N_TOTAL, n, f"{B.N_TOTAL} mẫu (21,000 s)", f"{n / 48000:.6f} s")]


def loud_checks(lu: dict, master: np.ndarray) -> list:
    tp4 = M.true_peak_db(master)
    return [chk("L1", "FAIL", abs(lu["I"] - B.TARGET_I) <= B.I_TOL, lu["I"], "−16 ± 0,3 LUFS", "WAV, ffmpeg ebur128"),
            chk("L2", "FAIL", lu["TP"] <= B.TP_MAX, lu["TP"], "≤ −2,0 dBTP", "WAV, ffmpeg ebur128 peak=true"),
            chk("L2", "FAIL", tp4 <= B.TP_MAX, tp4, "≤ −2,0 dBTP", "WAV, tự đo oversample 4×"),
            chk("L3", "WARN", 5.0 <= lu["LRA"] <= 8.0, lu["LRA"], "5–8 LU", "WAV (V2, V3: 6,5)")]


def edge_checks(master: np.ndarray) -> list:
    tail = sig.peak_db(master[-100 * MS:])
    return [chk("E1", "FAIL", abs(master[0]) < 1e-4, float(abs(master[0])), "|mẫu đầu| < 1e-4", "không click đầu"),
            chk("E2", "FAIL", tail < -60.0, tail, "đỉnh 100 ms cuối < −60 dBFS", "đuôi tắt tự nhiên, không cắt"),
            chk("E2", "FAIL", abs(master[-1]) < 1e-4, float(abs(master[-1])), "|mẫu cuối| < 1e-4")]


def music_junctions(sheet: dict, build: dict) -> dict:
    pts = qc.junctions(sheet, build)
    pts["music"] = pts["music"] + [sig.f2s(m["f"]) for m in sheet["marks"]
                                   if m["id"] in ("music-cut", "music-resume", "band-drop")]
    return pts


def _measure_solo(x: np.ndarray, ev: dict, s: int, e: int, na: int) -> int:
    """Neo đo được trên bộ đệm đặt riêng. onset: mẫu đầu vượt 1e-6 đỉnh; peak: argmax; end: mẫu cuối của clip đã đặt
    (đuôi fade cosine về đúng 0 nên đo theo ngưỡng sẽ sớm vài trăm µs); manual: cta = đỉnh tick (argmax), tua đêm = đỉnh
    tick dòng CRM cuối (tìm trong 40 ms sau mốc) − 1 f60 (tick đặt +1 f60 sau dòng hiện)."""
    seg = np.abs(x[s:e])
    if ev["anchor"] == "onset":
        return s + int(np.nonzero(seg > 1e-6 * seg.max())[0][0])
    if ev["anchor"] == "end":
        return e - 1
    if ev["anchor"] == "manual" and ev["kind"] == "ffSweep":
        w = np.abs(x[na:na + 40 * MS])
        return na + int(np.argmax(w)) - int(round(48000 / 60))
    return s + int(np.argmax(seg))


def align_solo(sheet: dict, render) -> list:
    """Mỗi cue đặt riêng (prep + gain + neo như mixbus.mix_detail): neo đo được so với mốc, ±1 ms."""
    out = []
    n = int(sheet["totalFrames"]) * dsp.SPF
    for ev in sheet["events"]:
        if not ev["sound"] or ev["kind"] == "bed":
            continue
        clip = mixbus.prep_clip(render(ev), ev["kind"])
        buf = np.zeros(n)
        na = mixbus.anchor_sample(ev)
        s, e = mixbus.place_at(buf, clip, na, mixbus.cue_gain_db(clip, ev["gainDb"]))
        got = _measure_solo(buf, ev, s, e, na)
        off = (got - na) / MS
        out.append(chk("6", "FAIL", abs(off) <= 1.0, off, "±1 ms", f"{ev['id']} {ev['f'] / 30:.3f} s neo {ev['anchor']}"))
    return out


def align_stem(sheet: dict, build: dict, sfx_stem: np.ndarray) -> list:
    """Cách đo #6 của V2 trên stem sfx thật (cue cùng khung gộp một). Một dòng tổng: cue chồng nhau làm lệch phép đo
    (nhất là neo end của whoosh/trượt), nên chỉ WARN; neo chuẩn đã kiểm ở #6 (đặt riêng)."""
    anchors = {e["id"]: ("peak" if e["anchor"] == "manual" else e["anchor"]) for e in sheet["events"]}
    cues = [{"id": c["id"], "f": c["f"], "anchor": anchors[c["id"]]} for c in build["cues"]
            if c["id"] not in ("room", "hum")]
    res = sig.align_groups(sfx_stem, sig.cue_groups(cues))
    off = [(ids, None if o is None else o * dsp.SPF / MS) for _, _, ids, o in res]
    bad = [f"{'+'.join(ids)} {'—' if ms is None else f'{ms:+.1f}'} ms" for ids, ms in off if ms is None or abs(ms) > 1.0]
    return [chk("6s", "WARN", not bad, f"{len(res) - len(bad)}/{len(res)}", "±1 ms",
                "stem sfx, cách đo V2 (cue chồng làm lệch phép đo): " + ("; ".join(bad) or "—"))]


def sync_checks(rows: list) -> list:
    out = []
    missing = [f"{r['id']} ({k})" for r in rows for k in ("solo", "sfx") if r[k] is None]
    out.append(chk("S", "FAIL", not missing, len(missing), "0 cue va chạm vắng tiếng",
                   ", ".join(missing) or "mọi cue va chạm có đỉnh trong [−1, +4] f60"))
    n_ev = sum(r["nguon"] == "events.json" for r in rows)
    out.append(chk("S", "INFO", True, f"{n_ev}/{len(rows)}", "—",
                   "cue có khung hình lấy thẳng từ events.json (còn lại: dòng CRM, nút CTA suy từ sheet)"))
    for key, lvl in (("solo", "FAIL"), ("sfx", "FAIL"), ("master", "INFO")):
        s = M.sync_summary(rows, key, clean_only=key != "solo")
        ok = s["median_ms"] is not None and abs(s["median_ms"] - M.TARGET_MS) <= M.TARGET_TOL
        out.append(chk("S", lvl, ok, s["median_ms"], "trung vị 16,7 ± 2 ms",
                       f"{key}: {s['n']} va chạm{' không chồng' if key != 'solo' else ''}, "
                       f"[{s.get('min_ms')}, {s.get('max_ms')}] ms, {s.get('in_8_25')} trong 8–25 ms"))
    for r in rows:
        v = r["sfx"]
        if v is None:
            continue
        bad = v < M.EACH_FAIL[0] or v > M.EACH_FAIL[1]
        off_ok = M.EACH_OK[0] <= v <= M.EACH_OK[1]
        if not off_ok:
            lvl = "WARN" if r["overlap"] else ("FAIL" if bad else "WARN")
            out.append(chk("S", lvl, False, v, "8–25 ms (FAIL < 0 / > 33)",
                           f"stem sfx {r['id']} {r['t']:.3f} s; chồng với {', '.join(r['overlap']) or '—'}"))
    return out


def limiter_checks(sheet: dict, mix: np.ndarray, master: np.ndarray, g: float) -> tuple[list, dict]:
    t_of = {e["id"]: float(e["f"]) / 30 for e in sheet["events"]}
    rows = {cid: M.gr_rms300_db(mix, master, g, t_of[cid] - 0.01) for cid in BIG_HITS}
    mx, at = M.gr_max_5ms(mix, master, g)
    lag = M.align_lag(mix * 10 ** (g / 20), master, 10.2, 11.8)
    out = [chk("G", "FAIL" if v > 4 else "WARN", v <= 3.0, v, "≤ 3 dB (FAIL > 4)", f"ép RMS 300 ms ở {cid}")
           for cid, v in rows.items()]
    out += [chk("G", "WARN", mx <= 3.0, mx, "≤ 3 dB (lane A; V2 7,3, V3 6,4)", f"ép tối đa cửa sổ 5 ms, lúc {at} s"),
            chk("G", "INFO", lag == 0, lag, "0 mẫu", "master thẳng hàng với mix + G (tương quan chéo 10,2–11,8 s)")]
    return out, {"gr_rms300_db": rows, "gr_max_5ms_db": mx, "gr_max_at_s": at, "lag_samples": lag}


def bus_checks(sheet: dict, stems: dict, g: float) -> tuple[list, list]:
    groups = B.sfx_group_stems(sheet)
    rows = [M.bus_row("nhạc", stems["music"], g), M.bus_row("sfx (tổng)", stems["sfx"], g),
            M.bus_row("mix (trước master)", stems["mix"], g)] + [M.bus_row(k, v, g) for k, v in groups.items()]
    plr = rows[2]["PLR"]
    a, b = action_span(sheet)
    mus, sfx = M.window_lufs(stems["music"], a, b), M.window_lufs(stems["sfx"], a, b)
    out = [chk("B", "WARN", plr <= 14.5, plr, "≤ 14,5 dB (lane A: thì ép tối đa ≤ 3 dB)", "PLR mix trước master"),
           chk("B", "WARN", mus - sfx <= 2.0, round(mus - sfx, 2), "≤ 2 LU (lane A)",
               f"đoạn hành động {a:.2f}–{b:.2f} s: nhạc {mus} LUFS, SFX {sfx} LUFS")]
    return out, rows


def ping_checks(sheet: dict, render, music: np.ndarray, mix: np.ndarray) -> tuple[list, list]:
    """Mỗi tiếng ping (tin nhắn hiện) đặt riêng, qua EQ bus như trong mix, so với stem nhạc (đã qua EQ bus): trong dải của
    ping (FAIL dưới +2 dB), cả dải, và so với mọi tiếng khác của mix (mix − ping)."""
    out, rows = [], []
    for ev in (e for e in sheet["events"] if e["kind"] == "ping" and e["sound"]):
        x = mixbus.bus_eq(M.solo(sheet, ev, render))
        r = {"id": ev["id"], "t": round(float(ev["f"]) / 30, 3), "gainDb": ev["gainDb"],
             "band_db": M.over_music_db(x, music), "full_db": M.over_music_db(x, music, None),
             "vs_rest_db": M.over_music_db(x, mix - x)}
        rows.append(r)
        out.append(chk("P", "FAIL", r["band_db"] >= PING_MIN_DB, r["band_db"], f"≥ +{PING_MIN_DB:g} dB so với nhạc",
                       f"{ev['id']} {r['t']:.3f} s (gain {ev['gainDb']:g}): dải 150 Hz–2 kHz; cả dải {r['full_db']:+.1f} dB; "
                       f"so với mọi tiếng khác {r['vs_rest_db']:+.1f} dB"))
    return out, rows


def density_checks(sheet: dict, render) -> list:
    grouped = {**sheet, "events": []}
    seen = set()
    for e in sheet["events"]:                       # cue cùng khung (va chạm kép) tính là một onset
        key = (e["f"], e["kind"] in M.ONSET_KINDS)
        if key in seen and e["kind"] in M.ONSET_KINDS:
            continue
        seen.add(key)
        grouped["events"].append(e)
    worst, crowded = M.onset_density(grouped)
    pairs = M.same_kind_pairs(sheet, render)
    twins = [f"{p['a']}={p['b']}" for p in pairs if p["giong_het"]]
    return [chk("O", "WARN", worst <= 3, worst, "≤ 3 onset / 250 ms",
                "; ".join(f"{t} s: {'+'.join(ids)}" for t, ids in crowded) or "—"),
            chk("O", "FAIL", not twins, len(pairs), "hai tiếng liền cùng kind không giống hệt",
                ", ".join(twins) or f"{len(pairs)} cặp liền nhau đều khác seed")]


def section_checks(sheet: dict, master: np.ndarray, build: dict) -> tuple[list, dict]:
    lv = {s["name"]: M.window_lufs(master, s["from"] / 30, s["to"] / 30) for s in sheet["sections"]}
    loud = np.nonzero(np.abs(master) >= 10 ** (-60 / 20))[0]
    tail_s = round((loud[-1] + 1) / 48000, 3)
    out = [chk("11", "WARN", lv["intro"] >= -36.0, lv["intro"], "≥ −36 LUFS", "đêm mở đầu không lặng chết"),
           chk("11", "WARN", lv["full"] - lv["intro"] >= 6.0, round(lv["full"] - lv["intro"], 2), "≥ 6 LU",
               "đuổi bắt − đêm"),
           chk("11", "WARN", lv["thesis"] - lv["dawn"] >= 0.0, round(lv["thesis"] - lv["dawn"], 2), "≥ 0 LU",
               "câu chốt không nhỏ hơn đoạn sáng ra"),
           chk("11", "WARN", 20.0 <= tail_s <= 21.0, tail_s, "20,0–21,0 s",
               "mẫu cuối còn ≥ −60 dBFS trên master (đuôi tự nhiên tới gần 21 s)"),
           chk("11", "INFO", True, "; ".join(f"{k} {v:g}" for k, v in lv.items()), "—", "LUFS master theo đoạn")]
    return out, {"lufs_by_section": lv, "tail_last_above_-60dBFS_s": tail_s}


def hierarchy_checks(sheet: dict, mix: np.ndarray, master: np.ndarray) -> list:
    """V2 #9 phỏng theo phim này: RMS 300 ms ở cú logo − thân đoạn đuổi (trung vị RMS 300 ms trên section full).
    Đo trên mix trước limiter, master và master qua giả lập loa điện thoại (BP 400 Hz–8 kHz). Mốc tham chiếu đo cùng
    cách trên master đã giao: V2 +1,5 / +0,4 (điện thoại), V3 +1,6 / −0,7."""
    full = next(x for x in sheet["sections"] if x["name"] == "full")
    logo = next(e["f"] for e in sheet["events"] if e["id"] == "hit-logo")
    out = []
    for tag, x, lim, lvl in (("mix trước limiter", mix, 1.0, "WARN"), ("master", master, 1.0, "WARN"),
                             ("master qua loa điện thoại", sig.phone(master), -1.0, "WARN")):
        d = sig.rms300_db(x, logo) - sig.body_db(x, full["from"], full["to"])
        out.append(chk("9", lvl, d >= lim, d, f"≥ {lim:+g} dB", f"{tag}: logo − thân đoạn đuổi (V2 +1,5 / V3 +1,6 trên master)"))
    return out


def lint(sheet: dict, build: dict) -> list:
    want = sorted(e["id"] for e in sheet["events"] if e["sound"])
    got = sorted(c["id"] for c in build["cues"])
    return [chk("13", "FAIL", want == got, len(got), f"{len(want)} cue có âm đều được đặt",
                ", ".join(sorted(set(want) ^ set(got))))]


def _num2(v: float | None) -> str:
    return "—" if v is None else f"{v:.2f}"


def offset_check(sheet: dict, y: np.ndarray, master: np.ndarray, tag: str) -> tuple[dict, float | None, int]:
    """V2 #7 phỏng theo bản 2: âm MP4 phải thẳng hàng master WAV (tương quan chéo, ≤ 1 ms). Onset logo kiểu V2 đo trên cả
    MP4 và master: swell nối vào logo làm phép đo này bắt muộn như nhau trên cả hai, nên chỉ so hai số với nhau."""
    _, measured = qc.media_offset(sheet, y)
    _, ref = qc.media_offset(sheet, master)
    lag = M.align_lag(master, y, 1.0, 20.0)
    same = measured is not None and ref is not None and abs(measured - ref) < 0.5
    return (chk("7", "FAIL", abs(lag) <= MS and same, lag, "MP4 thẳng hàng master (≤ 48 mẫu = 1 ms)",
                f"{tag}: tương quan chéo MP4–master {lag} mẫu; onset logo kiểu V2: MP4 {_num2(measured)} f, "
                f"master {_num2(ref)} f (swell nối vào logo làm phép đo bắt muộn như nhau, không phải lệch)"),
            measured, lag)


def mp4_checks(sheet: dict, mp4: Path, render, frames: dict, build: dict, master: np.ndarray) -> tuple[list, dict]:
    rec = (build.get("mp4") or {}).get(mp4.name, {})
    fresh = rec.get("md5") == B.md5(mp4)
    dur = qio.stream_durations(mp4)
    diff_ms = abs(dur["audio"] - dur["video"]) * 1000
    lu = qio.ebur128(mp4)
    y = qio.decode_media(mp4)
    off_row, measured, lag = offset_check(sheet, y, master, mp4.name)
    rows = M.sync_table(sheet, render, {"mp4": y}, frames)
    s = M.sync_summary(rows, "mp4", clean_only=True)
    tag = mp4.name
    out = [chk("1", "FAIL", fresh, "khớp" if fresh else "khác", "md5 = build.json",
               f"{tag}: đúng bản mux từ master này (không thì chạy score_thumon_build.py --mux-only)"),
           chk("1", "FAIL", diff_ms < 1000 / 60, round(diff_ms, 3), "< 16,7 ms", f"{tag}: lệch thời lượng a/v"),
           chk("2", "FAIL", abs(lu["I"] - B.TARGET_I) <= 0.5, lu["I"], "−16 ± 0,5 LUFS", tag),
           chk("2", "FAIL" if lu["TP"] > -1.0 else "WARN", lu["TP"] <= -2.0, lu["TP"], "≤ −2,0 dBTP (FAIL > −1,0)", tag),
           chk("2b", "WARN", 5.0 <= lu["LRA"] <= 8.0, lu["LRA"], "5–8 LU", tag),
           off_row,
           chk("S", "INFO", s["median_ms"] is not None and abs(s["median_ms"] - M.TARGET_MS) <= M.TARGET_TOL,
               s["median_ms"], "trung vị 16,7 ± 2 ms", f"{tag}: {s['n']} va chạm không chồng, đỉnh trên âm MP4")]
    return out, {"file": B.rel(mp4), "I": lu["I"], "TP": lu["TP"], "LRA": lu["LRA"], "av_diff_ms": round(diff_ms, 3),
                 "offset_frames_30": qc.jnum(measured), "lag_vs_master_samples": lag, "sync_median_ms": s["median_ms"]}


def write_md(report: dict, path: Path) -> None:
    s = report["summary"]
    lines = [f"# QA âm thanh `{report['id']}` (G6)", "", f"**{EARS}.** Minh nghe trên loa điện thoại và tai nghe "
             "trước khi chốt.", "", f"- Tổng: {s['pass']} đạt, {s['fail']} FAIL, {s['warn']} WARN",
             f"- Master: I {report['loudness']['I']} LUFS, TP {report['loudness']['TP']} dBTP, "
             f"LRA {report['loudness']['LRA']} LU, G {report['master']['gain_db']} dB",
             "", "| # | Mức | Kết quả | Giá trị | Ngưỡng | Ghi chú |", "|---|---|---|---|---|---|"]
    for c in report["checks"]:
        lines.append(f"| {c['id']} | {c['level']} | {'PASS' if c['pass'] else c['level']} | {c['value']} | "
                     f"{c['limit']} | {c['note']} |")
    lines += ["", "## Bus solo trước master", "", "| Bus | I (LUFS) | TP (dBTP) | PLR (dB) | I + G (thang master) |",
              "|---|---|---|---|---|"]
    lines += [f"| {r['bus']} | {r['I']} | {r['TP']} | {r['PLR']} | {r['I_master_scale']} |" for r in report["bus_solo"]]
    lines += ["", "## Tiếng ping so với nhạc (RMS 105 ms quanh đỉnh ping)", "",
              "| Ping | Giây | Gain | Dải 150 Hz–2 kHz (dB) | Cả dải (dB) | So với mọi tiếng khác (dB) |",
              "|---|---|---|---|---|---|"]
    lines += [f"| {r['id']} | {r['t']:.3f} | {r['gainDb']:g} | {r['band_db']:+.1f} | {r['full_db']:+.1f} | "
              f"{r['vs_rest_db']:+.1f} |" for r in report["ping_vs_music"]]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(do_mp4: bool) -> int:
    sheet, build = C.load(), qio.load_build(B.PATHS["build"])
    stale = C.check(C.make())
    if stale:
        raise qio.InputError("cue sheet cũ so với events.json / timeline.js: " + "; ".join(stale))
    B.require_same_md5(build)                      # stem, master phải đúng bản dựng từ cue sheet + events.json này
    frames = M.event_frames(C.load_events())
    render = SFX.make_render(sheet["id"])
    st = B.PATHS["stem"]
    stems = {k: qio.read_wav(st / f"{k}.wav") for k in ("music", "sfx", "mix")}
    master = qio.read_wav(B.PATHS["master"])
    g = float(build["master"]["gain_db"])
    lu = qio.ebur128(B.PATHS["master"])
    checks = fmt_checks(B.PATHS["master"]) + loud_checks(lu, master) + [qc.peaks("WAV master", master)]
    checks += qc.clicks({"sfx": stems["sfx"], "music": stems["music"]}, master, music_junctions(sheet, build))
    checks += edge_checks(master)
    checks += qc.silences_wav(sheet, stems["mix"], stems["music"], master, qio.silencedetect(B.PATHS["master"]), build)
    checks += align_solo(sheet, render) + align_stem(sheet, build, stems["sfx"])
    rows = M.sync_table(sheet, render, {"sfx": stems["sfx"], "master": master}, frames)
    checks += sync_checks(rows)
    gr_checks, gr = limiter_checks(sheet, stems["mix"], master, g)
    bus_c, bus_rows = bus_checks(sheet, stems, g)
    sec_c, sec = section_checks(sheet, master, build)
    ping_c, ping_rows = ping_checks(sheet, render, stems["music"], stems["mix"])
    checks += gr_checks + bus_c + ping_c + density_checks(sheet, render) + sec_c
    checks += hierarchy_checks(sheet, stems["mix"], master)
    checks += [qc.bass_balance(master)] + lint(sheet, build)
    mp4s = {}
    if do_mp4:                                       # chỉ các MP4 đã mux từ master này (ghi trong build.json)
        for rec in (build.get("mp4") or {}).values():
            path = B.ROOT / rec["file"]
            if path.is_file():
                c, info = mp4_checks(sheet, path, render, frames, build, master)
                checks += c
                mp4s[path.name] = info
    checks.append(chk("14", "INFO", True, EARS, "—", "cảm giác nghe: Opus không nghe được"))
    fails = sum(1 for c in checks if c["level"] == "FAIL" and not c["pass"])
    warns = sum(1 for c in checks if c["level"] == "WARN" and not c["pass"])
    report = {"id": sheet["id"], "nghe": EARS, "loudness": {k: lu[k] for k in ("I", "TP", "LRA")},
              "master": build["master"], "limiter": gr, "bus_solo": bus_rows, "ping_vs_music": ping_rows,
              "sections": sec, "mp4": mp4s,
              "sync": {k: M.sync_summary(rows, k, clean_only=k != "solo") for k in ("solo", "sfx", "master")},
              "checks": checks, "summary": {"pass": sum(c["pass"] for c in checks), "fail": fails, "warn": warns}}
    qa = B.PATHS["qa"]
    qa.mkdir(parents=True, exist_ok=True)
    (qa / "audio.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (qa / "sync.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    write_md(report, qa / "audio.md")
    qio.plots(B.PATHS["master"], qa, sorted({float(c["f"]) for c in build["cues"]}), int(sheet["totalFrames"]))
    P.spectrogram_png(master, sheet, B.GROUPS, qa / "pho-cue.png")
    for c in checks:
        print(f"{'PASS' if c['pass'] else c['level']} {c['id']} {c['limit']} {c['value']} {c['note']}".rstrip())
    print(f"TỔNG: {report['summary']['pass']} PASS, {fails} FAIL, {warns} WARN · {EARS}")
    return 1 if fails else 0


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="QA âm phim 3D Thủ môn (G6)")
    ap.add_argument("--no-mp4", action="store_true")
    a = ap.parse_args(argv)
    try:
        return run(not a.no_mp4)
    except (qio.InputError, C.InputError, B.InputError, RuntimeError, ValueError, KeyError, IndexError, OSError,
            wave.Error) as e:
        print(f"LỖI: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
