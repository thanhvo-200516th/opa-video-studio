"""Cue sheet phim 3D "Thủ môn" BẢN 2 (thu-mon): adapter events.json → src/audio/cues/thu-mon.{json,csv}, schema 2 như V3.

Bản 2 (Minh duyệt hướng 21/10/2026): nhịp đều 120 BPM (phách 0,5 s, lưới gốc 0,0 s), mọi cú hứng đúng phách, không khựng.
Cue sheet bản 1 lưu ở src/audio/cues/thu-mon.ban1.{json,csv} (mốc events.ban1.json, không dùng nữa).

Nguồn mốc (một nguồn chung cho hình và âm):
  - film3d/films/thu-mon/out/events.json: fps 60, sự kiện (id, t, frame, kind, strength) + bảng BEATS.
    Timeline đổi thì xuất lại: python -I tools/film3d/render.py job film3d/films/thu-mon/jobs/events.json
  - MOTION / SLIDES: chuyển động không nằm trong EVENTS (Bò trượt, rung báo tin, tua đêm, lấy đà, tràn xanh, cú cắt), chép
    từ film3d/films/thu-mon/timeline.js. --check soát lại từng đoạn chữ nguồn (TIMELINE_ANCHORS).
  - THESIS: mốc lớp chữ lane R (src/film3d/thuMonPlan.ts): gạch "Bỏ sót khách" 11,50 → 11,767; khối nhấn "Không bỏ sót
    khách" quét 12,00 → 12,28. ENDCARD: "OPA" khóa 16,600 s, nút CTA bật 19,176 → đỉnh 19,456 (như bản 1).
Quy ước: f30 = f60 / 2 (schema 2 khóa 30 fps; 1 f60 = 800 mẫu). Mốc giây đổi ra khung 60 như Math.round của JS.
  - Va chạm (neo peak): đỉnh = khung hình + 1 f60 (16,7 ms).
  - Whoosh, riser, trượt, hít vào (neo end): kết đúng khung chuyển động kết thúc.
  - Hơi thở, phì, rung (neo onset): bắt đầu đúng khung. Cắt nhạc, hit logo: đúng khung.

python -X utf8 tools/audio/score_thumon_cues.py [--check]
  Ghi src/audio/cues/thu-mon.json + .csv (LF). --check: dựng trong bộ nhớ, so với JSON + CSV đang có và soát timeline.js,
  thuMonPlan.ts; khác → in chỗ lệch đầu tiên, exit 1, không ghi. Exit 2 = lỗi đầu vào (thiếu file, JSON hỏng, events.json cũ
  hơn timeline.js, loại sự kiện lạ, sheet sai schema).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cues_io  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SHEET_ID = "thu-mon"
FILM = ROOT / "film3d" / "films" / "thu-mon"
EVENTS_JSON = FILM / "out" / "events.json"
TIMELINE_JS = FILM / "timeline.js"
PLAN_TS = ROOT / "src" / "film3d" / "thuMonPlan.ts"
TOTAL_S = 21.0
CSV_HEADER = ["id", "f", "giay", "mau", "kind", "variant", "anchor", "gainDb", "sound"]

# kind mới (bộ tổng hợp ở score_thumon_sfx.py / score_thumon_bo.py); kind V2 dùng lại: ping, tickUi, whoosh, riser, swell,
# hit, subdrop, sonicLogo, musicStop
THUMON_KINDS = {"bed", "pop", "catch", "save", "card", "tickCard", "tickRow", "snortBo", "land", "push", "hornTok",
                "flickTok", "slide", "exhale", "teeter", "ffSweep", "cta", "buzz", "bob", "inhale", "strike"}
THUMON_SECTIONS = {"dawn", "dive", "thesis", "bridge"}
THUMON_MARKS = {"downbeat", "hold", "music-resume", "pad-release"}
SOUND_EVENT_KINDS = {"appear", "launch", "catch", "card", "snort", "land", "jump", "bob", "ff", "strike"}
MARK_ONLY_KINDS = {"ff-end", "dawn", "flood", "lock"}      # thành mốc nhạc / chuyển động, không có cue riêng

# ---------- chuyển động ngoài EVENTS (giây, chép từ timeline.js; --check soát chuỗi nguồn) ----------
MOTION = {
    "buzz": (0.12, 0.12),              # tin đầu rung báo tin: từ appear + 0,12 s, tắt đúng lúc bay (launch)
    "ff-scroll": (8.10, 9.70),         # cột tin trên điện thoại cuộn đều: glide(ffStart − 0,1, ffEnd + 0,1, 0,3)
    "ff-rows": 12,                     # bảng CRM đếm thêm 12 dòng đều trong ffStart → ffEnd (tick mỗi dòng, +1 f60)
    "windup": (14.50, 14.85),          # lấy đà: hít hơi, ngửa đầu, nhổm lên nhanh dần rồi bật xả đúng lúc tràn xanh
    "flood": (14.85, 15.35),           # vùng xanh tràn từ lòng O (3,2·easeIn((t − flood) / 0,5))
    "slide-lock": (15.10, 15.98),      # Bò trượt về chỗ khóa (dolly-zoom; swell phủ, không cue riêng)
    "dawn": (9.68, 10.65),             # đêm → ngày đều (dayMix tuyến tính BEATS.dawn → BEATS.day): phòng sáng dần, ù tắt
    "cut": (16.00, 16.00),             # cắt sang end card 2D (DURATION của phần 3D)
}
# Bò trượt tới chỗ hứng (khóa Hermite giữ–giữ của boX): variant "u0:u1" là đoạn của tốc độ v(u) = 4u(1 − u)
SLIDES = {
    "slide-1": (2.40, 2.85, -17, "trượt trái đón tin 1"),
    "slide-2": (3.85, 4.30, -17, "trượt phải đón tin 2"),
    "slide-3": (4.90, 5.30, -18, "trượt về đón tin 3"),
    "slide-4": (5.62, 5.88, -18, "nhích phải đón tin 4–6"),
    "slide-5": (7.20, 7.70, -18, "trượt về chỗ, quay sang bảng CRM"),
}
JUMP_LAND_T = 6.80                     # JUMP_END: cú nhảy 9 cm hứng tin 5 trên không; cú đáp duy nhất có tiếng thân
THESIS = {"strike": 11.50, "strikeEnd": 11.50 + 8 / 30, "accent": 12.00, "accentEnd": 12.28, "l8bIn": 11.75}
ENDCARD = {"logo": 16.600, "tagLock": 17.120, "ctaStart": 19.176, "ctaPeak": 19.456, "ctaStill": 19.600, "end": 21.0}

TIMELINE_ANCHORS = (
    ("DURATION 16,0", "export const DURATION = 16.0;"),
    ("tin đầu hiện 0,50 s trước khi bay", "{ id: 'b1', launch: BEATS.launch1, entry: 2.88, land: BEATS.catch1, appear: 0.50 }"),
    ("rung báo tin", "const wiggle = b.appear ? ring(t, t0 + 0.12, 9, 5, 4) * (1 - ramp(t, b.launch - 0.12, b.launch)) : 0;"),
    ("CRM đếm 12 dòng lúc tua",
     "return 2 + arrivals + Math.floor(clamp01((t - BEATS.ffStart) / (BEATS.ffEnd - BEATS.ffStart)) * 12);"),
    ("cột tin cuộn lúc tua", "+ 10 * glide(t, BEATS.ffStart - 0.1, BEATS.ffEnd + 0.1, 0.3);"),
    ("lấy đà 14,50 → tràn",
     "const windup = (t) => (t <= BEATS.flood ? easeIn((t - 14.50) / (BEATS.flood - 14.50)) : 1 - easeOut((t - BEATS.flood) / 0.25));"),
    ("nhảy 9 cm", "hop(t, BEATS.jump, JUMP_END, 0.09)"),
    ("JUMP_END 6,80", "const JUMP_END = 6.80;"),
    ("nảy hứng 0,6 cm", "BOBS.reduce((a, c) => a + hop(t, c - 0.10, c + 0.10, 0.006), 0)"),
    ("nảy theo phách", "export const DAY_BOBS = [12.00, 12.50, 13.00, 13.50, 14.00, 14.50];"),
    ("vùng xanh 0,5 s", "3.2 * easeIn((t - BEATS.flood) / 0.5)"),
    ("trời sáng đều", "dayMix: clamp01((t - BEATS.dawn) / (BEATS.day - BEATS.dawn)),"),
    ("BRIDGE_SLIDE 15,10", "const BRIDGE_SLIDE = 15.10;"),
    ("boX 1", "[0, HOME], [2.40, HOME, true], [2.85, 0.00, true],"),
    ("boX 2", "[3.85, 0.00, true], [4.30, 0.09, true],"),
    ("boX 3", "[4.90, 0.09, true], [5.30, 0.03, true],"),
    ("boX 4", "[5.62, 0.03, true], [5.88, 0.06, true],"),
    ("boX 5", "[7.20, 0.06, true], [7.70, HOME, true], [DURATION, HOME],"),
)
PLAN_ANCHORS = (
    ("end card 21 s, LOGO 16,6", "export const THU_MON = { END: 21, ENDCARD: 16, LOGO: 16.6 } as const;"),
    ("gạch 11,50", "const STRIKE_AT = 11.5;"),
    ("khối nhấn một phách sau cú gạch", "LOCK: STRIKE_AT + (T3.LOCK - T3.STRIKE),"),
)

# ---------- thiết kế theo sự kiện ----------
POP_NOTE = {"b1": "E4", "b7": "A4"}            # chỉ tin đầu (sau rung báo tin) và tin buổi sáng có tiếng "bụp" lúc bay
CATCH_NOTE = {"b1": "A4", "b2": "C5", "b3": "E5", "b4": "G5", "b5": "A5", "b6": "B5", "b7": "G#5"}   # leo theo hợp âm;
CATCH_GAIN = {"b7": -5}                        # b7: dẫn G#5 về A add9 của câu chốt (12,00); còn lại −7 (V2 tickCatch −6)
# ping trầm (A3 / E4) nằm đúng dải pad, pulse: mức từng tin để nổi trên nhạc ≈ +3 dB, sàn +2 dB (QA "P": qua EQ bus như
# trong mix, dải 150 Hz–2 kHz, 105 ms quanh đỉnh). Tin nhắn tới là ý chính của phim (điều phối 21/10).
PING_GAIN = {"b1": -10, "b2": -9, "b3": -5, "b4": -6.5, "b5": -6, "b6": -6.5, "b7": -4}
CARD_TICK_GAP = 3                              # f60: thẻ tới CRM cách cú khác ≤ 50 ms thì bỏ tick thẻ
SNORT_GAIN = {1.0: -6, 0.9: -7, 0.8: -8, 0.75: -8, 0.6: -10}


class InputError(Exception):
    """Lỗi đầu vào → exit 2."""


def f60(t: float) -> int:
    """Giây → khung 60 fps, làm tròn như Math.round của JS (events.json): nửa khung làm tròn lên, không kiểu ngân hàng."""
    return int(math.floor(t * 60 + 0.5))


def f30(frame60: float) -> float | int:
    """Khung 60 → khung 30 của schema 2; số nguyên khi tròn."""
    v = round(frame60 / 2, 6)
    return int(v) if float(v).is_integer() else v


def dur30(t0: float, t1: float) -> float | int:
    return f30((t1 - t0) * 60)


def md5_file(path: Path) -> str:
    return hashlib.md5(Path(path).read_bytes()).hexdigest()


def load_events(path: Path = EVENTS_JSON) -> dict:
    """Đọc events.json; kiểm fps, khung = Math.round(t·60), id duy nhất."""
    if not Path(path).is_file():
        raise InputError(f"thiếu {path}")
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise InputError(f"{path}: JSON hỏng ({e})") from e
    if data.get("fps") != 60:
        raise InputError(f"{path}: fps {data.get('fps')} ≠ 60")
    seen = set()
    for e in data.get("events", []):
        if e["id"] in seen:
            raise InputError(f"{path}: trùng id {e['id']}")
        seen.add(e["id"])
        if e["frame"] != f60(e["t"]):
            raise InputError(f"{path}: {e['id']} frame {e['frame']} ≠ round({e['t']}·60)")
    return data


def beats_problems(data: dict, timeline_js: Path = TIMELINE_JS) -> list[str]:
    """events.json phải cùng đợt với timeline.js: mọi số trong `export const BEATS = {…}` bằng bảng beats của events.json."""
    if not Path(timeline_js).is_file():
        return [f"thiếu {timeline_js}"]
    m = re.search(r"export const BEATS = \{(.*?)\};", Path(timeline_js).read_text(encoding="utf-8"), re.S)
    if not m:
        return [f"{Path(timeline_js).name}: không thấy `export const BEATS = {{…}};`"]
    src = {k: float(v) for k, v in re.findall(r"(\w+):\s*(-?\d+(?:\.\d+)?)", m.group(1))}
    have = data.get("beats", {})
    bad = [f"{k} timeline {v:g} ≠ events.json {have.get(k)}" for k, v in src.items()
           if not isinstance(have.get(k), (int, float)) or abs(have[k] - v) > 1e-9]
    return [f"events.json cũ hơn timeline.js (xuất lại events): {'; '.join(bad)}"] if bad else []


def anchor_problems(timeline_js: Path = TIMELINE_JS, plan_ts: Path = PLAN_TS) -> list[str]:
    """Đoạn chữ nguồn của MOTION / SLIDES / THESIS / ENDCARD còn nguyên trong timeline.js, thuMonPlan.ts không."""
    out = []
    for path, anchors in ((timeline_js, TIMELINE_ANCHORS), (plan_ts, PLAN_ANCHORS)):
        if not Path(path).is_file():
            out.append(f"thiếu {path}")
            continue
        text = Path(path).read_text(encoding="utf-8")
        out += [f"{Path(path).name} đổi ở chỗ «{label}»: không còn `{snip}`" for label, snip in anchors if snip not in text]
    return out


# ---------- dựng cue ----------
def _cue(cid: str, frame60: float, kind: str, anchor: str, gain: float, variant: str | None = None,
         note: str = "", **extra) -> dict:
    ev = {"id": cid, "f": f30(frame60), "kind": kind}
    if variant is not None:
        ev["variant"] = variant
    ev.update({"anchor": anchor, "gainDb": gain})
    ev.update(extra)
    if note:
        ev["note"] = note
    ev["sound"] = True
    return ev


def _impact(cid: str, frame60: int, kind: str, gain: float, variant: str | None, src: str, **extra) -> dict:
    """Va chạm: đỉnh = khung hình + 1 f60."""
    return _cue(cid, frame60 + 1, kind, "peak", gain, variant, f"{src}: khung {frame60} + 1 f60", **extra)


def _ends(cid: str, span: tuple[float, float], kind: str, gain: float, variant: str | None, src: str,
          **extra) -> dict:
    """Whoosh / riser / trượt / hít vào: kết đúng khung cuối chuyển động; dài theo chuyển động (durF)."""
    t0, t1 = span
    return _cue(cid, f60(t1), kind, "end", gain, variant, f"{src}: {t0:.2f} → kết {t1:.2f} s",
                durF=dur30(t0, t1), **extra)


def _bubble_cues(ev: dict, nth: dict, busy: set[int]) -> list[dict]:
    """Tin nhắn: hiện trên màn hình (ping V2, tin đầu thêm rung báo tin), bay ra (chỉ b1, b7 có "bụp"), lọt khe (tick hứng
    phương án A), thẻ tới bảng CRM (tick thẻ; bỏ khi trùng ≤ CARD_TICK_GAP f60 một cú khác)."""
    b, kind = ev["id"].split("-")
    fr, k = ev["frame"], nth.get(ev["id"], 0)
    if kind == "appear":
        gain = PING_GAIN.get(b, -6 if k % 2 else -6.5)
        out = [_impact(f"ping-{b}", fr, "ping", gain, "night", f"{ev['id']}: tin hiện trên màn hình")]
        return out
    if kind == "launch":
        if b not in POP_NOTE:
            return []
        return [_impact(f"pop-{b}", fr, "pop", -10 if b == "b1" else -9, POP_NOTE[b], f"{ev['id']}: tin bay ra")]
    if kind == "catch":
        ring = "/ring" if float(ev.get("strength", 0.7)) >= 1.0 else ""      # tin ở lại lòng O: ngân dài
        return [_impact(f"catch-{b}", fr, "catch", CATCH_GAIN.get(b, -7), CATCH_NOTE[b] + ring, ev["id"])]
    if kind == "card":
        if any(abs(fr - x) <= CARD_TICK_GAP for x in busy):
            return []
        return [_impact(f"tick-card-{b}", fr, "tickCard", -15 if k % 2 else -14, "E6", f"{ev['id']} (thẻ tới CRM)")]
    raise InputError(f"sự kiện tin nhắn lạ: {ev['id']}")


def _bo_cues(ev: dict, beats: dict) -> list[dict]:
    kind, fr = ev["kind"], ev["frame"]
    if kind == "snort":
        p = float(ev.get("strength", 1.0))
        return [_cue(ev["id"], fr, "snortBo", "onset", SNORT_GAIN.get(p, -8), f"{p:g}",
                     f"{ev['id']}: khung {fr}, hạt phì bắt đầu")]
    if kind == "land":
        if abs(ev["t"] - JUMP_LAND_T) > 1e-6:      # nảy 0,6 cm sau mỗi cú hứng: không tiếng thân riêng (tick hứng đã có)
            return []
        return [_impact(ev["id"], fr, "land", -5, "L", f"{ev['id']}: đáp sau cú nhảy 9 cm")]
    if kind == "jump":
        return [_impact("jump-push", fr, "push", -12, None, "jump: bật nhảy")]
    if kind == "bob":
        k = int(ev["id"].split("-")[1])
        return [_impact(ev["id"], fr, "bob", -16 if k % 2 else -15, None, f"{ev['id']}: Bò nảy chạm đáy đúng phách")]
    if kind == "strike":
        return [_ends("strike", (THESIS["strike"], THESIS["strikeEnd"]), "strike", -15, None, "gạch \"Bỏ sót khách\""),
                _impact("tick-thesis", f60(THESIS["accent"]), "tickUi", -12, "E6",
                        "khối nhấn \"Không bỏ sót khách\" quét 12,00 (V2 tick-thesis + brass-stab)")]
    if kind == "ff":
        a, end = MOTION["ff-scroll"][0], beats["ffEnd"]
        return [_cue("ff-sweep", f60(end), "ffSweep", "manual", -11, f"{MOTION['ff-rows']}:{ev['t'] - a:.3f}:{end - ev['t']:.3f}",
                     f"tua cả đêm {a:.2f} → {end:.2f} s (cột tin cuộn, đồng hồ tua), tick mỗi dòng CRM đếm lên",
                     durF=dur30(a, end))]
    if kind in MARK_ONLY_KINDS:
        return []
    raise InputError(f"events.json: kind lạ {kind!r} ({ev['id']}): thêm cách xử lý vào score_thumon_cues.py")


def _motion_cues(data: dict) -> list[dict]:
    m, beats = MOTION, data["beats"]
    b1 = next(e for e in data["events"] if e["id"] == "b1-appear")
    b1l = next(e for e in data["events"] if e["id"] == "b1-launch")
    w0, w1 = m["windup"]
    out = [
        _cue("room", 0, "bed", "onset", -37, "room", "tiếng phòng đêm → sáng, tắt ở cú cắt 16,00 s",
             durF=dur30(0.0, m["cut"][0])),
        _cue("hum", 0, "bed", "onset", -25, "hum", "ù màn hình (họ A2), tắt dần khi trời sáng",
             durF=dur30(0.0, beats["day"])),
        _ends("buzz-b1", (b1["t"] + m["buzz"][0], b1l["t"]), "buzz", -16, None, "tin đầu rung báo tin"),
        _ends("inhale", (w0, w1), "inhale", -11, None, "lấy đà: Bò hít hơi, nhổm lên nhanh dần"),
        _ends("riser", (w0, w1), "riser", -8, None, "riser vào cú tràn xanh"),
        _cue("exhale-flood", f60(m["flood"][0]), "exhale", "onset", -10, "burst",
             "bật xả hơi đúng lúc vùng xanh bung", durF=dur30(0.0, 0.5)),
        _ends("whoosh-flood", m["flood"], "whoosh", -6, "windup", "vùng xanh tràn khung", peakPos=0.25),
        _ends("swell", (ENDCARD["logo"] - 1.0, ENDCARD["logo"]), "swell", -6, None,
              "swell A add9 nối cú cắt 16,00 vào logo 16,60 (không lặng, không dừng nhịp)"),
    ]
    return out + [_slide_cue(cid) for cid in SLIDES]


def _slide_cue(cid: str) -> dict:
    t0, t1, gain, why = SLIDES[cid]
    return _ends(cid, (t0, t1), "slide", gain, "0.000:1.000", why)


def _logo_cues() -> list[dict]:
    lf = f60(ENDCARD["logo"])
    peak = f60(ENDCARD["ctaPeak"])
    lead = dur30(ENDCARD["ctaStart"], ENDCARD["ctaPeak"])
    return [
        _cue("music-cut-2d", f60(MOTION["cut"][0]), "musicStop", "onset", 0, None, "cắt nhạc đúng cú cắt 16,00 s"),
        _cue("hit-logo", lf, "hit", "onset", -2, "logo", "\"OPA\" khóa 16,600 s (lane R)", duckDb=3),
        _cue("subdrop-logo", lf, "subdrop", "onset", -2, "logo", "về 55 Hz", durF=30),
        _cue("sonic-logo", lf, "sonicLogo", "onset", 2, "a",
             "E5–A4–C#5 như V2, V3; onset nốt đầu; +2 (V3 −1) để logo hơn thân đoạn đuổi như V2, V3"),
        _cue("cta", peak + 1, "cta", "manual", -12, None,
             f"nút CTA bật {ENDCARD['ctaStart']:.3f} → đỉnh {ENDCARD['ctaPeak']:.3f} s (+1 f60); neo = tick",
             durF=lead),
    ]


def build_events(data: dict) -> list[dict]:
    evs = data["events"]
    beats = data["beats"]
    if (beats["dawn"], beats["day"]) != MOTION["dawn"]:
        raise InputError(f"MOTION dawn {MOTION['dawn']} ≠ BEATS dawn/day ({beats['dawn']}, {beats['day']}): sửa bảng MOTION")
    nth: dict[str, int] = {}
    for kind in ("appear", "card"):
        for i, e in enumerate(e for e in evs if e["kind"] == kind):
            nth[e["id"]] = i
    busy = {e["frame"] for e in evs if e["kind"] in ("appear", "launch", "catch", "jump")} | {f60(JUMP_LAND_T)}
    out: list[dict] = []
    for e in evs:
        if e["kind"] in ("appear", "launch", "catch", "card"):
            out += _bubble_cues(e, nth, busy)
        elif e["kind"] in SOUND_EVENT_KINDS | MARK_ONLY_KINDS:
            out += _bo_cues(e, data["beats"])
        else:
            raise InputError(f"events.json: kind lạ {e['kind']!r} ({e['id']}): thêm cách xử lý vào score_thumon_cues.py")
    out += _motion_cues(data) + _logo_cues()
    for e in out:
        if e["kind"] == "musicStop":
            e["sound"] = False
    return sorted(out, key=lambda e: (e["f"], e["id"]))


def build_sheet(data: dict, sources: str) -> dict:
    """Sheet schema 2 (30 fps) từ events.json bản 2. Mọi frame là khung 30 (f60 / 2)."""
    m, total, beats = MOTION, f30(f60(TOTAL_S)), data["beats"]
    sec = lambda a, b, name: {"name": name, "from": f30(f60(a)), "to": f30(f60(b))}  # noqa: E731
    sections = [sec(0, 2.0, "intro"), sec(2.0, 6.0, "build"), sec(6.0, 10.0, "full"), sec(10.0, 12.0, "dawn"),
                sec(12.0, beats["flood"], "thesis"), sec(beats["flood"], m["cut"][0], "dive"),
                sec(m["cut"][0], ENDCARD["logo"], "bridge"), sec(ENDCARD["logo"], TOTAL_S, "logo")]
    mk = lambda mid, t, note, **kw: {"id": mid, "f": f30(f60(t)), **kw, "note": note}  # noqa: E731
    marks = [mk("downbeat", 0.0, "lưới nhịp 120 BPM gốc 0,0 s: mọi cú hứng đúng phách"),
             mk("pad-open", 10.0, f"sáng ra: D add9, pad mở lọc (trời sáng đều {beats['dawn']:.2f} → {beats['day']:.2f} s)"
                .replace(".", ",")),
             mk("brass-stab", THESIS["accent"], "A add9", durS=0.5),
             mk("music-cut", m["cut"][0], "cắt sang end card 2D; swell nối vào logo"),
             mk("music-resume", ENDCARD["logo"], "logo: A add9 ngân"),
             mk("pad-release", 18.80, "A add9 nhả tự nhiên, tắt trước 21,0 s")]
    span = lambda a, b, kind, scope, why: {"from": f30(f60(a)), "to": f30(f60(b)), "kind": kind,  # noqa: E731
                                           "scope": scope, "reason": why}
    silences = [span(m["cut"][0] + 0.25, ENDCARD["logo"], "silent", "music", "nhạc đúng 0 sau đuôi vang 0,25 s (swell nối)"),
                span(20.30, TOTAL_S, "allowed", "mix", "khung CTA đứng yên, đuôi A add9 tắt tự nhiên")]
    return {
        "schema": 2, "id": SHEET_ID, "fps": 30, "bpm": 120, "beatFrames": 15, "barFrames": 60,
        "totalFrames": total, "sampleRate": 48000, "audioOffsetFrames": 0,
        "sections": sections,
        "keys": [{"f": 0, "root": "A", "mode": "minor"}, {"f": f30(f60(10.0)), "root": "A", "mode": "major"}],
        "marks": sorted(marks, key=lambda x: x["f"]), "events": build_events(data), "silences": silences,
        "cuts": [{"from": f30(f60(m["flood"][0])), "to": f30(f60(m["flood"][1])), "kind": "flood"},
                 {"from": f30(f60(m["cut"][0])), "to": f30(f60(m["cut"][0])) + 0.5, "kind": "match"}],
        "generatedBy": f"tools/audio/score_thumon_cues.py bản 2 ({sources})",
    }


def validate(sheet: dict) -> dict:
    """cues_io.validate_sheet của V2 với tập kind / section / mark nới cho phim này (không sửa cues_io)."""
    with mock.patch.multiple(cues_io, KINDS=cues_io.KINDS | THUMON_KINDS,
                             SECTION_NAMES=cues_io.SECTION_NAMES | THUMON_SECTIONS,
                             MARK_IDS=cues_io.MARK_IDS | THUMON_MARKS):
        return cues_io.validate_sheet(sheet, SHEET_ID)


def load(cues_dir: Path | None = None) -> dict:
    """Đọc src/audio/cues/thu-mon.json và kiểm."""
    path = cues_io.sheet_path(SHEET_ID, cues_dir)
    if not path.is_file():
        raise InputError(f"thiếu {path}; chạy python -X utf8 tools/audio/score_thumon_cues.py")
    return validate(json.loads(path.read_text(encoding="utf-8")))


def to_json(sheet: dict) -> str:
    return json.dumps(sheet, ensure_ascii=False, indent=2) + "\n"


def to_csv(sheet: dict) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(CSV_HEADER)
    for e in sheet["events"]:
        w.writerow([e["id"], e["f"], f"{e['f'] / 30:.3f}", round(e["f"] * 1600), e["kind"], e.get("variant", ""),
                    e["anchor"], e["gainDb"], "true" if e["sound"] else "false"])
    return buf.getvalue()


def sources_md5(events_path: Path = EVENTS_JSON) -> str:
    """md5 của mọi nguồn mốc: đổi bất kỳ file nào → --check báo lệch → chạy lại adapter và dựng lại âm."""
    return ", ".join(f"{Path(p).name} md5 {md5_file(p)}" for p in (events_path, TIMELINE_JS, PLAN_TS))


def make(events_path: Path = EVENTS_JSON) -> dict:
    data = load_events(events_path)
    stale = beats_problems(data)
    if stale:
        raise InputError("; ".join(stale))
    return validate(build_sheet(data, sources_md5(events_path)))


def first_diff(want: str, have: str) -> str:
    a, b = want.splitlines(), have.splitlines()
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return f"dòng {i + 1}: cần «{x.strip()}» nhưng có «{y.strip()}»"
    if len(a) == len(b):
        return "chỉ khác ký tự xuống dòng (cần LF)"
    return f"số dòng {len(a)} ≠ {len(b)}"


def check(sheet: dict, cues_dir: Path | None = None) -> list[str]:
    """Danh sách chỗ lệch (rỗng = khớp): timeline.js/thuMonPlan.ts + JSON + CSV trên đĩa."""
    probs = anchor_problems()
    jpath = cues_io.sheet_path(SHEET_ID, cues_dir)
    for path, want in ((jpath, to_json(sheet)), (jpath.with_suffix(".csv"), to_csv(sheet))):
        if not path.is_file():
            probs.append(f"thiếu {path}")
            continue
        have = path.read_bytes().decode("utf-8")      # so đúng từng byte (LF), không dịch xuống dòng
        if have != want:
            probs.append(f"{path.name} lệch events.json/adapter: {first_diff(want, have)}")
    return probs


def write(sheet: dict, cues_dir: Path | None = None) -> tuple[Path, Path]:
    jpath = cues_io.sheet_path(SHEET_ID, cues_dir)
    jpath.parent.mkdir(parents=True, exist_ok=True)
    jpath.write_bytes(to_json(sheet).encode("utf-8"))        # LF trên mọi máy: md5 không đổi theo hệ điều hành
    cpath = jpath.with_suffix(".csv")
    cpath.write_bytes(to_csv(sheet).encode("utf-8"))
    return jpath, cpath


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Cue sheet phim 3D Thủ môn bản 2 từ events.json")
    ap.add_argument("--check", action="store_true", help="so với JSON + CSV đang có và soát timeline.js; không ghi")
    a = ap.parse_args(argv)
    try:
        sheet = make()
        return run_check(sheet) if a.check else run_write(sheet)
    except (InputError, ValueError, KeyError, TypeError, OSError, StopIteration) as e:
        print(f"LỖI: {e}")
        return 2


def run_check(sheet: dict) -> int:
    probs = check(sheet)
    for p in probs:
        print(f"LỆCH: {p}")
    if probs:
        print("→ chạy lại: python -X utf8 tools/audio/score_thumon_cues.py (rồi dựng lại âm)")
        return 1
    print(f"khớp: {len(sheet['events'])} cue, events.json / timeline.js / thuMonPlan.ts đúng bản đã dùng")
    return 0


def run_write(sheet: dict) -> int:
    probs = anchor_problems()
    for p in probs:
        print(f"CẢNH BÁO: {p}")
    if probs:
        print("LỖI: cập nhật MOTION / SLIDES / THESIS / ENDCARD trong score_thumon_cues.py theo timeline.js trước khi ghi")
        return 1
    jpath, cpath = write(sheet)
    print(f"đã ghi {jpath} và {cpath.name}: {len(sheet['events'])} sự kiện, "
          f"{sum(e['sound'] for e in sheet['events'])} có âm")
    return 0


if __name__ == "__main__":
    sys.exit(main())
