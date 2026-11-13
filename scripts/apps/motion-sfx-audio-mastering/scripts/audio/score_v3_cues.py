"""Cue sheet V3 "Khám sức khỏe AI" (v3-ai-audit), 20 s, cùng schema 2 của V2.

Nguồn: bảng mốc chốt trong docs/v3-16x9/v3-thiet-ke.md (cột "Âm (cue)"). Mốc tính bằng GIÂY ở bảng
MOC bên dưới, đổi ra frame 30 fps (f = giây × 30) như V2: hình 60 fps đọc f/30 ra giây.

python tools/audio/score_v3_cues.py  → ghi src/audio/cues/v3-ai-audit.json + .csv
Kiểm sheet bằng chính cues_io.validate_sheet của V2, chỉ nới tập kind / section / mark cho V3
(không sửa file V2).
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cues_io  # noqa: E402

SHEET_ID = "v3-ai-audit"
FPS = 30
TOTAL_S = 20.0
GENERATED_BY = "tools/audio/score_v3_cues.py (bảng mốc chốt docs/v3-16x9/v3-thiet-ke.md)"

# kind mới của V3 (bộ tổng hợp ở score_v3_sfx.py); kind V2 dùng lại bộ tổng hợp của synth.py / sonic_logo.py
V3_KINDS = {"chime", "tickEject", "scan", "blip", "tickFix", "paper", "tickNum", "tickAccent"}
V3_SECTIONS = {"dive", "land"}
V3_MARKS = set()

# (id, giây, kind, variant, anchor, gainDb, phụ) — anchor: onset | peak | end | manual (như V2)
MOC = (
    ("chime-hoi", 1.00, "chime", None, "peak", -12, {}),
    ("tick-accent-1", 1.50, "tickAccent", "E6", "peak", -12, {}),
    ("whoosh-windup", 3.95, "whoosh", "windup", "end", -6, {"durF": 13.5,
                                                            "note": "lấy đà 3,50 → kết 3,95"}),
    ("thump", 4.00, "thump", None, "peak", -6, {}),
    ("tick-eject-1", 4.00, "tickEject", "C#5", "peak", -14, {}),
    ("tick-eject-2", 4.10, "tickEject", "E5", "peak", -14, {}),
    ("tick-eject-3", 4.20, "tickEject", "F#5", "peak", -14, {}),
    ("tick-eject-4", 4.30, "tickEject", "A5", "peak", -14, {}),
    ("tick-eject-5", 4.40, "tickEject", "C#6", "peak", -14, {}),
    ("scan", 5.00, "scan", None, "onset", -15, {"durF": 60, "note": "kéo dài 5,00 → 7,00"}),
    ("blip-alert-1", 7.00, "blip", "1", "peak", -10, {}),
    ("blip-alert-2", 7.50, "blip", "2", "peak", -10, {}),
    ("tick-accent-2", 8.00, "tickAccent", "E6", "peak", -12, {}),
    ("snort", 8.75, "snort", None, "manual", -8, {"note": "neo = đỉnh xung 1 (như V2)"}),
    ("tick-fix", 9.00, "tickFix", None, "peak", -9, {"note": "neo = đỉnh tiếng chốt khóa (nhịp 2)"}),
    ("whoosh-gather", 10.00, "whoosh", "cut", "peak", -6, {"durF": 12.5, "peakPos": 0.6,
                                                           "note": "bắt đầu 9,75, đỉnh 10,00"}),
    ("paper", 10.00, "paper", None, "onset", -10, {"note": "giấy trượt bắt đầu ở mốc, đỉnh sau ≈ 0,14 s"}),
    ("tick-num-1", 12.50, "tickNum", "A5", "peak", -11, {}),
    ("tick-num-2", 13.00, "tickNum", "C#6", "peak", -11, {}),
    ("tick-num-3", 13.50, "tickNum", "E6", "peak", -11, {}),
    ("tick-accent-3", 14.00, "tickAccent", "E6", "peak", -12, {}),
    ("riser", 15.00, "riser", None, "end", -4, {"durF": 7.5, "note": "14,75 → kết 15,00"}),
    ("whoosh-dive", 15.00, "whoosh", "cut", "peak", -2, {"durF": 9, "peakPos": 0.6}),
    ("hit-logo", 15.50, "hit", "logo", "onset", -3, {"duckDb": 4,
                                                     "note": "onset = transient; đỉnh mẫu (sóng sub) trễ ≈ 31 ms"}),
    ("subdrop-logo", 15.50, "subdrop", "logo", "onset", -3, {"durF": 30}),
    ("sonic-logo", 15.50, "sonicLogo", "a", "onset", -1, {"note": "E5–A4–C#5 như V2; onset nốt đầu"}),
    ("music-stop", 17.20, "musicStop", None, "onset", 0, {"sound": False}),
    ("tick-cta", 17.80, "tickUi", "E6", "peak", -12, {}),
)

# mốc nhạc (giây): mọi lịch nốt và cửa của score_v3.py đọc từ đây qua sheet
SECTIONS = (("intro", 0.0, 4.0), ("build", 4.0, 10.0), ("full", 10.0, 15.0), ("dive", 15.0, 15.4),
            ("silence", 15.4, 15.5), ("land", 15.5, 17.2), ("logo", 17.2, 20.0))
MARKS = (
    {"id": "pad-open", "s": 2.0, "note": "pad mở lọc 700 → 1100 Hz"},
    {"id": "motif", "s": 2.0, "note": "E5"}, {"id": "motif", "s": 2.25, "note": "A4"},
    {"id": "motif", "s": 2.5, "note": "B4"},
    {"id": "band-drop", "s": 15.0, "note": "lặn: band rút, còn pad"},
    {"id": "music-cut", "s": 15.4, "note": "cắt mọi thứ, fade 4 ms"},
    {"id": "music-stop", "s": 17.2, "note": "nhạc dừng, fade 8 ms; chỉ còn đuôi sonic logo"},
)
SILENCES = (
    (15.4, 15.5, "silent", "mix", "lặng 0,1 s trước cú logo"),
    (15.4, 15.5, "silent", "music", "như trên, kiểm trên stem nhạc"),
    (18.0, 20.0, "allowed", "mix", "khung CTA im dần, đuôi sonic logo tắt ≈ 19,1 s"),
)
CUTS = ((4.0, 4.1, "match"), (10.0, 10.1, "match"), (15.0, 15.5, "flood"))


def fr(sec: float) -> float | int:
    """Giây → frame 30 fps; số nguyên khi tròn."""
    f = round(sec * FPS, 6)
    return int(f) if float(f).is_integer() else f


def _event(row) -> dict:
    cid, sec, kind, variant, anchor, gain, extra = row
    ev = {"id": cid, "f": fr(sec), "kind": kind}
    if variant is not None:
        ev["variant"] = variant
    ev.update({"anchor": anchor, "gainDb": gain})
    ev.update({k: v for k, v in extra.items() if k != "sound"})
    ev["sound"] = extra.get("sound", True)
    return ev


def build_sheet() -> dict:
    events = sorted((_event(r) for r in MOC), key=lambda e: e["f"])
    marks = []
    for m in MARKS:
        mk = {"id": m["id"], "f": fr(m["s"])}
        if "note" in m:
            mk["note"] = m["note"]
        marks.append(mk)
    return {
        "schema": 2, "id": SHEET_ID, "fps": FPS, "bpm": 120, "beatFrames": 15, "barFrames": 60,
        "totalFrames": fr(TOTAL_S), "sampleRate": 48000, "audioOffsetFrames": 0,
        "sections": [{"name": n, "from": fr(a), "to": fr(b)} for n, a, b in SECTIONS],
        "keys": [{"f": 0, "root": "A", "mode": "major"}],
        "marks": marks, "events": events,
        "silences": [{"from": fr(a), "to": fr(b), "kind": k, "scope": sc, "reason": r} for a, b, k, sc, r in SILENCES],
        "cuts": [{"from": fr(a), "to": fr(b), "kind": k} for a, b, k in CUTS],
        "generatedBy": GENERATED_BY,
    }


def validate(sheet: dict) -> dict:
    """cues_io.validate_sheet của V2 với tập kind / section / mark nới cho V3."""
    with mock.patch.multiple(cues_io, KINDS=cues_io.KINDS | V3_KINDS,
                             SECTION_NAMES=cues_io.SECTION_NAMES | V3_SECTIONS,
                             MARK_IDS=cues_io.MARK_IDS | V3_MARKS):
        return cues_io.validate_sheet(sheet, SHEET_ID)


def load() -> dict:
    """Đọc src/audio/cues/v3-ai-audit.json và kiểm."""
    path = cues_io.sheet_path(SHEET_ID)
    return validate(json.loads(path.read_text(encoding="utf-8")))


def write(sheet: dict) -> tuple[Path, Path]:
    jpath = cues_io.sheet_path(SHEET_ID)
    jpath.parent.mkdir(parents=True, exist_ok=True)
    jpath.write_text(json.dumps(sheet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cpath = jpath.with_suffix(".csv")
    with open(cpath, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["id", "f", "giay", "mau", "kind", "variant", "anchor", "gainDb", "sound"])
        for e in sheet["events"]:
            w.writerow([e["id"], e["f"], f"{e['f'] / FPS:.3f}", round(e["f"] * 1600), e["kind"],
                        e.get("variant", ""), e["anchor"], e["gainDb"], "true" if e["sound"] else "false"])
    return jpath, cpath


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    sheet = validate(build_sheet())
    jpath, cpath = write(sheet)
    print(f"đã ghi {jpath} và {cpath.name}: {len(sheet['events'])} sự kiện, "
          f"{sum(e['sound'] for e in sheet['events'])} có âm")
    return 0


if __name__ == "__main__":
    sys.exit(main())
