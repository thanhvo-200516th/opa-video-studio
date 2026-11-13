"""Bảng kiểm qa_audio (gói F, KH §3.9): mỗi hàm trả danh sách check
{id, level, pass, value, limit, note}. level: FAIL (tính exit), WARN, INFO.
"""
import math

import numpy as np

import qa_audio_sig as sig

# Kỳ vọng lint cue (KH §3.4); không phải mốc dựng, chỉ là số đối chiếu
EXPECT_EVENTS, EXPECT_SOUND = 26, 25
EXPECT_TICK_UI = [120, 390, 555, 825]
BODY_BARS = (7, 10)            # phần thân = [b(7), b(10))
HIT_ID, LOGO_ID, THUMP_ID, SONIC_ID = "hit-accent", "hit-logo", "thump", "sonic-logo"
WHOOSH_CHARGE_ID = "whoosh-charge"
OFFSET_IDS = (HIT_ID, LOGO_ID, SONIC_ID)


def jnum(v):
    """Giá trị JSON được: float làm tròn 3 số, vô cực → chuỗi."""
    if isinstance(v, (list, tuple)):
        return [jnum(i) for i in v]
    if isinstance(v, (bool, str)) or v is None:
        return v
    v = float(v)
    return round(v, 3) if math.isfinite(v) else ("-inf" if v < 0 else "inf")


def chk(cid: str, level: str, ok: bool, value, limit: str, note: str = "") -> dict:
    return {"id": cid, "level": level, "pass": bool(ok), "value": jnum(value), "limit": limit, "note": note}


def event_f(sheet: dict, cue_id: str):
    for ev in sheet["events"]:
        if ev["id"] == cue_id:
            return float(ev["f"])
    return None


# ---------- #2, #2b, #3 ----------
def loudness_wav(lu: dict) -> list:
    i, tp, lra = lu["I"], lu["TP"], lu["LRA"]
    return [chk("2", "FAIL", abs(i + 14.0) <= 0.3, i, "−14 ± 0,3 LUFS", "WAV master"),
            chk("2", "FAIL", tp <= -1.5, tp, "≤ −1,5 dBTP", "WAV master"),
            chk("2", "WARN", tp >= -2.5, tp, "≥ −2,5 dBTP", "WAV master: dưới −2,5 = limiter ít làm việc"),
            chk("2b", "WARN", 5.0 <= lra <= 8.0, lra, "5–8 LU", "WAV master")]


def loudness_mp4(lu: dict) -> list:
    return [chk("2", "FAIL", abs(lu["I"] + 14.0) <= 0.5, lu["I"], "−14 ± 0,5 LUFS", "MP4"),
            chk("2", "FAIL", lu["TP"] <= -1.0, lu["TP"], "≤ −1,0 dBTP", "MP4"),
            chk("2b", "WARN", 5.0 <= lu["LRA"] <= 8.0, lu["LRA"], "5–8 LU", "MP4")]


def peaks(name: str, x: np.ndarray) -> dict:
    top = float(np.max(np.abs(x))) if len(x) else 0.0
    return chk("3", "FAIL", top < 0.999, top, "< 0,999", name)


# ---------- #4 ----------
def junctions(sheet: dict, build: dict) -> dict:
    """Điểm nối theo stem chủ: mép clip → sfx; mép khoảng silent và music-stop → nhạc."""
    cue_pts = [int(c["start_sample"]) for c in build["cues"]] + [int(c["end_sample"]) for c in build["cues"]]
    music_pts = [int(build["music_stop_sample"])]
    for s in sheet["silences"]:
        if s["kind"] == "silent":
            music_pts += [sig.f2s(s["from"]), sig.f2s(s["to"])]
    return {"sfx": cue_pts, "music": music_pts}


def _frames(xs: list) -> str:
    return ", ".join(f"f{n / sig.SPF:.2f}" for n in xs[:8])


def clicks(stems: dict, master: np.ndarray, pts: dict) -> list:
    """FAIL: click ±5 ms quanh điểm nối, đo trên stem chủ (stem sfx không có hats nên không báo nhầm).
    WARN: quét cả file master."""
    near = []
    for name in ("sfx", "music"):
        hit, _ = sig.split_clicks(sig.find_clicks(stems[name]), pts[name])
        near += [(name, n) for n in hit]
    whole = sig.find_clicks(master).tolist()
    note = "; ".join(f"{name} {_frames([n])}" for name, n in near[:8])
    return [chk("4", "FAIL", not near, len(near), "0 click tại điểm nối ±5 ms", note),
            chk("4", "WARN", not whole, len(whole), "0 click cả file master", _frames(whole))]


# ---------- #5 ----------
def silences_wav(sheet: dict, mix, music, master, found: list, build: dict) -> list:
    out = []
    for s in sheet["silences"]:
        span = f"[{s['from']}, {s['to']})"
        if s["kind"] == "silent" and s["scope"] == "mix":
            out.append(chk("5", "FAIL", sig.peak_db(sig.window(mix, s["from"], s["to"])) < sig.SILENT_PEAK_DB,
                           sig.peak_db(sig.window(mix, s["from"], s["to"])), "đỉnh < −60 dBFS", f"mix stem {span}"))
            pk = sig.peak_db(sig.window(master, s["from"], s["to"]))
            out.append(chk("5", "WARN", pk < sig.SILENT_PEAK_DB, pk, "đỉnh < −60 dBFS", f"master {span}"))
        elif s["kind"] == "silent" and s["scope"] == "music":
            seg = sig.window(music, s["from"], s["to"])
            out.append(chk("5", "FAIL", bool(np.all(seg == 0.0)), sig.peak_db(seg), "đúng 0", f"stem nhạc {span}"))
        elif s["kind"] == "near":
            r = sig.rms_db(sig.window(master, s["from"], s["to"]))
            out.append(chk("5", "FAIL", r < sig.NEAR_FAIL_DB, r, "RMS < −35 dBFS", f"master {span}"))
            out.append(chk("5", "WARN", r <= sig.NEAR_TARGET_DB, r, "RMS ≤ −45 dBFS (mục tiêu)", f"master {span}"))
    stop = next((m["f"] for m in sheet["marks"] if m["id"] == "music-stop"), None)
    bad = sig.unexpected_silences(found, sheet["silences"], len(master) / sig.SR, stop)
    out.append(chk("5", "FAIL", not bad, [list(b) for b in bad], "không lặng ngoài silent/near/allowed",
                   f"silencedetect −60 dB d 0,1 trên master; tail_end_frame = {build['tail_end_frame']}"))
    return out


def silences_mp4(sheet: dict, y: np.ndarray) -> list:
    out = []
    for s in sheet["silences"]:
        span = f"[{s['from']}+1, {s['to']}−1)"
        if s["kind"] == "silent" and s["scope"] == "mix":
            pk = sig.peak_db(sig.window(y, s["from"], s["to"], 1.0))
            out.append(chk("5", "WARN", pk < sig.SILENT_PEAK_DB, pk, "đỉnh < −60 dBFS", f"MP4 {span}"))
        elif s["kind"] == "near":
            r = sig.rms_db(sig.window(y, s["from"], s["to"], 1.0))
            out.append(chk("5", "WARN", r < sig.NEAR_FAIL_DB, r, "RMS < −35 dBFS", f"MP4 {span}"))
    return out


# ---------- #6, #7 ----------
def alignment(sheet: dict, build: dict, sfx: np.ndarray) -> list:
    anchors = {ev["id"]: ev["anchor"] for ev in sheet["events"]}
    cues = [{"id": c["id"], "f": c["f"], "anchor": anchors.get(c["id"], "onset")} for c in build["cues"]]
    out = []
    for f, anchor, ids, off in sig.align_groups(sfx, sig.cue_groups(cues)):
        ok = off is not None and abs(off) <= 1.0
        out.append(chk("6", "FAIL", ok, "không thấy tín hiệu" if off is None else off, "±1 f",
                       f"{'+'.join(ids)} f{f:g} neo {anchor}"))
    return out


def end_spans(sheet: dict, build: dict) -> list:
    """#6 (vòng sửa đợt 4, S3): cue có âm neo `end` và có durF phải chiếm đúng [f − durF, f) trên stem: đầu clip
    ±1 f quanh f2s(f − durF), mẫu cuối không vượt f2s(f). Bắt clip đặt theo đỉnh (đuôi rơi qua mốc rồi bị cắt)."""
    placed = {c["id"]: c for c in build["cues"]}
    out = []
    for ev in sheet["events"]:
        if not ev["sound"] or ev.get("anchor") != "end" or "durF" not in ev or ev["id"] not in placed:
            continue
        c, f, d = placed[ev["id"]], float(ev["f"]), float(ev["durF"])
        off = (int(c["start_sample"]) - sig.f2s(f - d)) / sig.SPF
        ok = abs(off) <= 1.0 and int(c["end_sample"]) <= sig.f2s(f)
        out.append(chk("6", "FAIL", ok, off, "đầu clip ±1 f, kết ≤ mốc",
                       f"{ev['id']} chiếm [{f - d:g}, {f:g}) theo neo end (end_sample {c['end_sample']})"))
    return out


def media_offset(sheet: dict, y: np.ndarray) -> tuple:
    """(check #7, measured_offset_frames) — trung vị onset_audio(MP4) − f_cue."""
    vals = []
    for cid in OFFSET_IDS:
        f = event_f(sheet, cid)
        if f is None:
            continue
        n = sig.measure_anchor(y, sig.f2s(f), "onset", 5 * sig.SPF)
        if n is not None:
            vals.append((n - sig.f2s(f)) / sig.SPF)
    if not vals:
        return chk("7", "INFO", False, None, "|m| < 0,5 f", "không đo được onset trên MP4"), None
    m = float(np.median(vals))
    cur = float(sheet.get("audioOffsetFrames", 0))
    note = f"AUDIO_OFFSET = {cur:g}"
    if abs(m) >= 0.5:
        note += f"; báo A: AUDIO_OFFSET_mới = AUDIO_OFFSET − measured = {cur - m:.3f}"
    return chk("7", "INFO", abs(m) < 0.5, m, "|m| < 0,5 f", note), m


# ---------- #8–#12 ----------
def _hit_rows(sheet: dict, build: dict, x: np.ndarray, level: str, tag: str) -> list:
    """#8, #9 trên một tín hiệu: RMS 300 ms ở hit/logo so với trung vị phần thân."""
    fh, fl = event_f(sheet, HIT_ID), event_f(sheet, LOGO_ID)
    bar = sheet["barFrames"]
    body = sig.body_db(x, (BODY_BARS[0] - 1) * bar, (BODY_BARS[1] - 1) * bar)
    r300, r735 = sig.rms300_db(x, fh), sig.rms300_db(x, fl)
    need = 2.0 / 3.0 * float(build["hit_gap_design_db"])
    return [chk("8", level, r300 >= body + 4.0, r300 - body, "≥ 4 dB",
                f"{tag}: RMS 300 ms f{fh:g} − thân ({body:.1f} dBFS)"),
            chk("9", level, r735 <= r300 - need and r735 >= body + 2.0, [r300 - r735, r735 - body],
                f"hit − logo ≥ {need:.2f} dB; logo − thân ≥ 2 dB",
                f"{tag}: hit_gap_design_db = {build['hit_gap_design_db']}")]


def _squash_note(build: dict, mix: np.ndarray, master: np.ndarray, f: float) -> str:
    """Mức limiter ép RMS 300 ms tại f: (mix + G) − master; TK §7.5 muốn ≤ 3–4 dB."""
    m = build.get("master") or {}
    if "gain_db" not in m:
        return "chưa có G của master"
    squash = sig.rms300_db(mix, f) + float(m["gain_db"]) - sig.rms300_db(master, f)
    return f"limiter ép RMS 300 ms f{f:g} {squash:.1f} dB"


def hierarchy(sheet: dict, build: dict, sig_by: dict) -> list:
    """Thứ bậc hit. sig_by = {"mix", "master", "sfx"}.
    #8, #9 FAIL trên mix TRƯỚC limiter (thứ bậc thiết kế); cùng phép đo trên master chỉ WARN: với I −14,
    trần 0,79 và thân ≈ I + 2,8 dB, #9 trên master cần crest hit ≤ 3,2 dB (sine là 3,0) nên không đạt được.
    #10 FAIL trên stem sfx (RMS của chính tiếng thump): trên mix/master cửa sổ f240 chứa nhạc đoạn rise
    (−1,5 LU so với thân), khi đó #10 đòi hit hơn thân ~8,5 dB, trái #8 (+4)."""
    fh, fl, ft = event_f(sheet, HIT_ID), event_f(sheet, LOGO_ID), event_f(sheet, THUMP_ID)
    if None in (fh, fl, ft):
        return [chk("8", "FAIL", False, None, "có cue", "thiếu hit-accent/hit-logo/thump trong cues")]
    mix, master, sfx = sig_by["mix"], sig_by["master"], sig_by["sfx"]
    rows = _hit_rows(sheet, build, mix, "FAIL", "mix trước limiter")
    squash = f"{_squash_note(build, mix, master, fh)}; {_squash_note(build, mix, master, fl)}"
    rows += [{**c, "note": f"{c['note']}; {squash}"} for c in _hit_rows(sheet, build, master, "WARN", "master")]
    # 8p, 9p (vòng sửa đợt 4, S1): cùng phép đo trên master qua giả lập loa điện thoại; WARN như bản master
    lo, hi = sig.PHONE_BAND
    rows += [{**c, "id": c["id"] + "p"} for c in
             _hit_rows(sheet, build, sig.phone(master), "WARN", f"master qua giả lập loa điện thoại BP {lo:g}–{hi:g} Hz")]
    s300, s240 = sig.rms300_db(sfx, fh), sig.rms300_db(sfx, ft)
    return rows + [
        chk("8b", "WARN", sig.crest_db(master, fh) >= 8.0, sig.crest_db(master, fh), "≥ 8 dB", f"master: crest f{fh:g}"),
        chk("10", "FAIL", s240 <= s300 - 10.0, s300 - s240, "≥ 10 dB",
            f"stem sfx: RMS f{fh:g} − RMS thump f{ft:g} (master {sig.rms300_db(master, fh) - sig.rms300_db(master, ft):.1f})"),
    ]


def sections(sheet: dict, lu: dict) -> list:
    sec = {s["name"]: s for s in sheet["sections"]}
    if not all(k in sec for k in ("intro", "full", "breath")):
        return [chk("11", "WARN", False, None, "có section", "thiếu intro/full/breath")]
    lv = {k: sig.section_lufs(lu["short"], sec[k]["from"], sec[k]["to"]) for k in ("intro", "full", "breath")}
    di, db_ = lv["full"] - lv["intro"], lv["full"] - lv["breath"]
    return [chk("11", "WARN", 5.0 <= di <= 12.0, di, "5–12 LU", "full − intro (short-term)"),
            chk("11", "WARN", 3.0 <= db_ <= 7.0, db_, "3–7 LU", "full − breath (short-term)")]


def bass_balance(x: np.ndarray) -> dict:
    d = sig.band_db(x, 100.0, 300.0) - sig.band_db(x, 20.0, 60.0)
    return chk("12", "WARN", d >= -6.0, d, "≥ −6 dB", "năng lượng 100–300 Hz − dưới 60 Hz")


# ---------- #13, #14 ----------
def cue_lint(sheet: dict, build: dict) -> list:
    evs = sheet["events"]
    sound_ids = sorted(e["id"] for e in evs if e["sound"])
    built = sorted(c["id"] for c in build["cues"])
    ticks = sorted(float(e["f"]) for e in evs if e["kind"] == "tickUi")
    wc = [e for e in evs if e["id"] == WHOOSH_CHARGE_ID]
    wc_ok = len(wc) == 1 and wc[0]["sound"] and WHOOSH_CHARGE_ID in built
    return [chk("13", "FAIL", len(evs) == EXPECT_EVENTS and len(sound_ids) == EXPECT_SOUND,
                [len(evs), len(sound_ids)], f"{EXPECT_EVENTS} sự kiện, {EXPECT_SOUND} có âm"),
            chk("13", "FAIL", built == sound_ids, len(built), "build.json đặt đúng các cue có âm",
                ", ".join(sorted(set(built) ^ set(sound_ids)))),
            chk("13", "FAIL", ticks == [float(t) for t in EXPECT_TICK_UI], ticks, "tickUi ở 120/390/555/825"),
            chk("13", "FAIL", wc_ok, "ok" if wc_ok else "sai", "whoosh-charge sound: true, có đặt (chốt ở H1)"),
            chk("13", "INFO", True, str(build["logo_variant"]), "a | c", "biến thể logo đọc từ build.json")]


def ears_note() -> dict:
    return chk("14", "INFO", True, "CHƯA NGHE BẰNG TAI", "—",
               "ngưỡng 8b, 11, 12 rút từ một thử nghiệm duy nhất nên chỉ WARN")
