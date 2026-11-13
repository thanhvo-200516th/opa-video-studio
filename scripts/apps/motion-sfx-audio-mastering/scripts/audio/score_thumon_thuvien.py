#!/usr/bin/env python3
"""Âm phim "Thủ môn" bản 2 bằng thư viện SFX (D:/Vibe Coding/Motion Claude/sfx) thay cho SFX tổng hợp.

python -X utf8 tools/audio/score_thumon_thuvien.py [--target-i -16] [--video <mp4 hình>] [--out <mp4 ra>]
  1) Mốc, neo (peak / onset / end) và gainDb lấy nguyên từ cue sheet đã duyệt src/audio/cues/thu-mon.json;
     nguồn âm, dịch cao độ (st), lớp phụ lấy từ src/audio/cues/thu-mon.thuvien.json.
  2) Mỗi âm: giải mã 48 kHz mono → dịch cao độ bằng đổi tốc độ (âm ngắn, dài/ngắn đi theo) → low-shelf cho âm nhỏ
     → fade 3 ms → gain để momentary max = −20 LUFS + gainDb (quy ước mixbus) → đặt sao cho điểm neo rơi đúng mẫu.
  3) Bus SFX qua bus_eq (HPF 25 Hz, −2 dB @ 250 Hz) + nhạc nền = stem nhạc đã duyệt → master tới target I
     (limiter trần −2 dBFS) → mux vào hình (chép luồng hình, AAC 320k 2 kênh).
Ra: film3d/films/thu-mon/out/g6-am/thu-vien/{sfx.wav, mix.wav, master.wav, bao-cao.json} (+ MP4 nếu có --out).
Exit: 0 xong, 2 lỗi đầu vào (thiếu file, cue lạ).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, resample_poly, sosfilt, sosfiltfilt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools" / "v2w"))
import dsp  # noqa: E402
import master as mst  # noqa: E402
from dsp_loud import k_weight, lufs_integrated, momentary_max, short_term  # noqa: E402
from mixbus import bus_eq  # noqa: E402

SR = dsp.SR
REF_LUFS = -20.0
SHEET = ROOT / "src/audio/cues/thu-mon.json"
MAP = ROOT / "src/audio/cues/thu-mon.thuvien.json"
OUT = ROOT / "film3d/films/thu-mon/out/g6-am/thu-vien"
SMALL_KINDS = {"ping", "catch", "tickCard", "tickUi", "snortBo", "bob"}   # low-shelf −2,6 dB dưới 90 Hz như mixbus
KEEP_ATTACK = {"hit", "subdrop"}


class InputError(Exception):
    pass


def load(path: Path) -> np.ndarray:
    if not path.is_file():
        raise InputError(f"thiếu file âm: {path}")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    if len(x) == 0:
        raise InputError(f"không giải mã được: {path}")
    return x


def shift(x: np.ndarray, st: float) -> np.ndarray:
    """Dịch cao độ st nửa cung bằng đổi tốc độ (âm ngắn: dài/ngắn đi theo tỉ lệ 2^(−st/12))."""
    if abs(st) < 1e-6:
        return x
    r = Fraction(2 ** (-st / 12)).limit_denominator(2000)
    return resample_poly(x, r.numerator, r.denominator)


def dsp_k(x: np.ndarray) -> np.ndarray:
    """Công suất K-weighted từng mẫu (để đo momentary của nhạc ở bất kỳ đoạn nào)."""
    return k_weight(x) ** 2


def anchor_index(x: np.ndarray, anchor: str) -> int:
    a = np.abs(x)
    pk = float(a.max())
    if anchor == "peak":
        return int(a.argmax())
    if anchor == "onset":
        return int(np.nonzero(a >= pk * 10 ** (-50 / 20))[0][0])
    if anchor == "end":
        return int(np.nonzero(a >= pk * 10 ** (-40 / 20))[0][-1]) + 1
    raise InputError(f"neo lạ: {anchor}")


def prep(x: np.ndarray, kind: str) -> np.ndarray:
    if kind in SMALL_KINDS:
        x = dsp.low_shelf(x, 90.0, -2.6)
    return dsp.fade_edges(x, 0.0 if kind in KEEP_ATTACK else 3.0, 10.0)


def place(bus: np.ndarray, x: np.ndarray, n_anchor: int, i_anchor: int, gain_db: float) -> tuple[int, int]:
    start = n_anchor - i_anchor
    s, e = max(start, 0), min(start + len(x), len(bus))
    if e > s:
        bus[s:e] += x[s - start:e - start] * 10 ** (gain_db / 20)
    return s, e


def phone_check(wav: Path) -> dict:
    """Giả lập loa điện thoại (HPF 500 Hz bậc 4 + LPF 8 kHz bậc 2): momentary max của logo (16,5–18,0 s)
    so với thân đoạn đuổi (5,0–7,5 s). Đạt khi logo ≥ đoạn đuổi (nghiên cứu: logo phải nổi trên loa điện thoại)."""
    _, x = wavfile.read(wav)
    x = x.astype(np.float64) / (2 ** 31 if x.dtype == np.int32 else 1.0)
    y = sosfilt(butter(2, 8000, "lowpass", fs=SR, output="sos"), sosfilt(butter(4, 500, "highpass", fs=SR, output="sos"), x))
    seg = lambda a, b: momentary_max(y[int(a * SR):int(b * SR)])  # noqa: E731
    logo, chase = seg(16.5, 18.0), seg(5.0, 7.5)
    return {"logo_mmax": round(logo, 1), "chase_mmax": round(chase, 1), "logo_minus_chase": round(logo - chase, 1), "pass": logo >= chase}


def mux_ch(video: Path, wav: Path, out: Path, ch_db: float) -> dict:
    """Ghép master mono vào hình (chép hình), ra stereo hai kênh bằng nhau, mỗi kênh ch_db so với mono.
    −3,01 dB = như `-ac 2` của bản đã duyệt (I của MP4 = I của master); −1,01 dB = cộng +2 dB ở bước stereo, sau limiter
    (nghiên cứu: −14 LUFS cho mạng xã hội mà không ép limiter thêm). Trả số đo trên chính MP4."""
    gl = 10 ** (ch_db / 20)
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video), "-i", str(wav), "-map", "0:v:0",
                    "-map", "1:a:0", "-c:v", "copy", "-af", f"pan=stereo|c0={gl:.6f}*c0|c1={gl:.6f}*c0", "-c:a", "aac",
                    "-b:a", "320k", "-aac_pns", "0", "-movflags", "+faststart", str(out)], check=True)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(out), "-map", "0:a:0", "-af", "pan=mono|c0=c0",
                          "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    left = np.frombuffer(raw, np.float32).astype(np.float64)
    m = mst.ebur128(out)
    return {"file": str(out), "I": m["I"], "TP": m["TP"], "LRA": m["LRA"],
            "max_short_term": round(float(np.max(short_term(left, 0.1))) + 3.0103, 1)}


def build(target_i: float) -> dict:
    sheet = json.loads(SHEET.read_text(encoding="utf-8"))
    cmap = json.loads(MAP.read_text(encoding="utf-8"))
    lib = Path(cmap["library"])
    sr, music = wavfile.read(ROOT / cmap["music"])
    if sr != SR:
        raise InputError(f"stem nhạc {sr} Hz, cần {SR}")
    music = music.astype(np.float64)
    n = len(music)
    bus = np.zeros(n)
    cache: dict[str, np.ndarray] = {}
    report = []

    km = dsp_k(music)
    # mức theo nhạc, theo nhóm: số = LU so với momentary của nhạc tại mốc (cả dải; whoosh/riser/swell);
    # {"band": [lo, hi], "db": x} = âm to hơn nhạc x dB trong dải [lo, hi] Hz, cửa sổ 105 ms quanh đỉnh của âm
    # (tick, ping, chạm: tai nghe theo dải của chính âm đó); nhóm không có trong levels = quy ước REF của cue sheet.
    rel = cmap.get("levels", {})

    def music_m(n0: int, i_anchor: int) -> float:
        """Momentary (K, LUFS) của nhạc trong 400 ms quanh điểm neo."""
        s = max(n0 - min(i_anchor, int(0.1 * SR)), 0)
        e = min(s + int(0.4 * SR), n)
        return -0.691 + 10 * np.log10(max(float(km[s:e].mean()), 1e-12))

    def inband_db(x: np.ndarray, n_anchor: int, i_anchor: int, band: list[float]) -> float:
        """dB của âm (gain 0) so với nhạc trong dải band, cửa sổ −30…+75 ms quanh đỉnh của âm đặt đúng chỗ."""
        start = n_anchor - i_anchor
        n_pk = start + int(np.abs(x).argmax())
        w0, w1, pad = int(0.03 * SR), int(0.075 * SR), int(0.05 * SR)
        s, e = max(n_pk - w0 - pad, 0), min(n_pk + w1 + pad, n)
        seg = np.zeros(e - s)
        a0, a1 = max(start, s), min(start + len(x), e)
        if a1 > a0:
            seg[a0 - s:a1 - s] = x[a0 - start:a1 - start]
        sos = butter(4, band, btype="band", fs=SR, output="sos")
        cb, mb = sosfiltfilt(sos, seg), sosfiltfilt(sos, music[s:e])
        core = slice(max(n_pk - w0 - s, 0), n_pk + w1 - s)
        return float(10 * np.log10(max(np.mean(cb[core] ** 2), 1e-20) / max(np.mean(mb[core] ** 2), 1e-20)))

    def put(cid: str, kind: str, f: float, anchor: str, gain_db: float, spec: dict) -> None:
        if spec["file"] not in cache:
            cache[spec["file"]] = load(lib / spec["file"])
        x = prep(shift(cache[spec["file"]], float(spec.get("st", 0.0))), kind)
        n_anchor = dsp.f2s(f + float(spec.get("fOffset", 0.0))) - (1 if anchor == "end" else 0)
        i_anchor = anchor_index(x, anchor)
        group = spec.get("group", kind)
        mm = music_m(n_anchor, i_anchor)
        lv = rel.get(group)
        band = lv["band"] if isinstance(lv, dict) else spec.get("band", [300.0, 4000.0])
        d0 = inband_db(x, n_anchor, i_anchor, band)          # âm ở gain 0 so với nhạc, trong dải
        trim = float(spec.get("trimDb", 0.0))
        if isinstance(lv, dict):
            g = float(lv["db"]) + trim - d0
        elif lv is not None:
            g = mm + float(lv) + trim - momentary_max(x)
        else:
            g = REF_LUFS + gain_db + trim - momentary_max(x)
        g = min(g, float(cmap.get("maxMmax", 0.0)) - momentary_max(x))
        s, e = place(bus, x, n_anchor, i_anchor, g)
        report.append({"id": cid, "kind": kind, "group": group, "t": round(n_anchor / SR, 4), "anchor": anchor,
                       "gainDb": gain_db, "applied_db": round(g, 2), "mmax_lufs": round(momentary_max(x) + g, 1),
                       "music_m": round(mm, 1), "rel_lu": round(momentary_max(x) + g - mm, 1),
                       "band": band, "inband_db": round(d0 + g, 1), "file": spec["file"],
                       "st": spec.get("st", 0), "span_s": [round(s / SR, 3), round(e / SR, 3)]})

    known = {ev["id"]: ev for ev in sheet["events"]}
    for cid in cmap["cues"]:
        if cid not in known:
            raise InputError(f"cue '{cid}' không có trong cue sheet đã duyệt")
    for ev in sheet["events"]:
        if not ev.get("sound", True):        # cue không có tiếng trong bản đã duyệt (vd. cắt nhạc 16,0 s)
            continue
        spec = cmap["cues"].get(ev["id"])
        if spec is None:
            raise InputError(f"cue '{ev['id']}' của cue sheet chưa được chọn âm trong {MAP.name}")
        if spec.get("sound") is False:
            continue
        anchor = spec.get("anchor", ev["anchor"])
        if anchor == "manual":
            raise InputError(f"cue '{ev['id']}': neo 'manual' phải ghi rõ neo trong {MAP.name}")
        put(ev["id"], ev["kind"], float(ev["f"]), anchor, float(spec.get("gainDb", ev["gainDb"])), spec)
    for ex in cmap.get("extra", []):
        rep = ex.get("repeat", {"n": 1, "everyF": 0})
        for k in range(int(rep["n"])):
            put(ex["id"] + (f"-{k + 1}" if rep["n"] > 1 else ""), ex.get("kind", "extra"), float(ex["f"]) + k * float(rep["everyF"]),
                ex["anchor"], float(ex["gainDb"]), ex)

    sfx = bus_eq(bus)
    mix = music + sfx
    OUT.mkdir(parents=True, exist_ok=True)
    for name, x in (("sfx", sfx), ("mix", mix)):
        wavfile.write(OUT / f"{name}.wav", SR, x.astype(np.float32))
    res = mst.master(OUT / "mix.wav", OUT / "master.wav", target_i)
    # cân nhạc / SFX: short-term 3 s mỗi 0,5 s (chỉ chỗ có cả hai)
    st_m, st_s = short_term(music, 0.5), short_term(sfx, 0.5)
    k = min(len(st_m), len(st_s))
    both = [(i * 0.5, float(st_s[i] - st_m[i])) for i in range(k) if st_m[i] > -60 and st_s[i] > -60]
    out = {"target_i": target_i, "master": res, "music_lufs_i": round(lufs_integrated(music), 1),
           "sfx_lufs_i": round(lufs_integrated(sfx), 1), "sfx_minus_music_st": [[round(t, 1), round(d, 1)] for t, d in both],
           "phone": phone_check(OUT / "master.wav"), "cues": report}
    (OUT / "bao-cao.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-i", type=float, default=-16.0, help="I của master mono (limiter trần −2 dBFS)")
    ap.add_argument("--video", type=Path, help="MP4 hình để ghép âm (chép luồng hình)")
    ap.add_argument("--out", type=Path, help="MP4 ra, bản −16 LUFS (như bản đã duyệt, để nghe so công bằng)")
    ap.add_argument("--out-14", type=Path, help="MP4 ra, bản −14 LUFS cho mạng xã hội (+2 dB ở bước stereo)")
    a = ap.parse_args(argv)
    try:
        r = build(a.target_i)
    except InputError as e:
        print(f"LỖI: {e}", file=sys.stderr)
        return 2
    m = r["master"]
    print(f"master mono: I {m['I']} LUFS · TP {m['TP']} dBTP · LRA {m['LRA']} LU · gain {m['gain_db']} dB · {len(r['cues'])} âm đặt")
    print(f"nhạc I {r['music_lufs_i']} · SFX I {r['sfx_lufs_i']} (trước master) · loa điện thoại: {r['phone']}")
    mp4 = {}
    if a.video and a.out:
        mp4["-16"] = mux_ch(a.video, OUT / "master.wav", a.out, -3.0103)
    if a.video and a.out_14:
        mp4["-14"] = mux_ch(a.video, OUT / "master.wav", a.out_14, -1.0103)
    for k, v in mp4.items():
        print(f"MP4 {k}: I {v['I']} LUFS · TP {v['TP']} dBTP · LRA {v['LRA']} · max short-term {v['max_short_term']} · {v['file']}")
    if mp4:
        rep = json.loads((OUT / "bao-cao.json").read_text(encoding="utf-8"))
        rep["mp4"] = mp4
        (OUT / "bao-cao.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
