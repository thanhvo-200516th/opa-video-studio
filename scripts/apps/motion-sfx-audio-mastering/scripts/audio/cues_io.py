"""Đọc và kiểm cues.json schema 2 (gói E, KH §3.4, §3.9).

load_sheet(id) đọc src/audio/cues/<id>.json, kiểm khóa, kiểu, enum, khoảng frame, id duy nhất,
thứ tự theo f, marks hợp lệ. Lỗi → ValueError nêu tên trường.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CUES_DIR = ROOT / "src" / "audio" / "cues"

_NUM = (int, float)
SHEET_KEYS = {"schema": int, "id": str, "fps": int, "bpm": int, "beatFrames": int, "barFrames": int,
              "totalFrames": int, "sampleRate": int, "audioOffsetFrames": _NUM, "sections": list,
              "keys": list, "marks": list, "events": list, "silences": list, "cuts": list, "generatedBy": str}
FIXED = {"schema": 2, "fps": 30, "bpm": 120, "beatFrames": 15, "barFrames": 60, "sampleRate": 48000}
KINDS = {"ping", "whoosh", "tickUi", "thump", "riser", "snort", "hit", "subdrop", "tickCatch", "swell",
         "musicStop", "sonicLogo"}
ANCHORS = {"onset", "peak", "end", "manual"}
SECTION_NAMES = {"intro", "build", "rise", "silence", "full", "breath", "stop", "logo"}
MARK_IDS = {"pad-open", "motif", "esus-to-e", "band-drop", "music-cut", "brass-stab", "kick-rest", "music-stop"}
SILENCE_KINDS = {"silent", "near", "allowed"}
SCOPES = {"mix", "music"}
CUT_KINDS = {"hard", "flood", "match"}
MAX_DUCK_DB = 6.0

EVENT_REQ = {"id": str, "f": _NUM, "kind": str, "anchor": str, "gainDb": _NUM, "sound": bool}
EVENT_OPT = {"variant": str, "durF": _NUM, "peakPos": _NUM, "duckDb": _NUM, "offgrid": bool, "note": str}
MARK_REQ = {"id": str, "f": _NUM}
MARK_OPT = {"to": _NUM, "note": str, "durS": _NUM}
SECTION_REQ = {"name": str, "from": _NUM, "to": _NUM}
KEY_REQ = {"f": _NUM, "root": str, "mode": str}
SILENCE_REQ = {"from": _NUM, "to": _NUM, "kind": str, "scope": str, "reason": str}
CUT_REQ = {"from": _NUM, "to": _NUM, "kind": str}


def _is(v, t) -> bool:
    """isinstance nhưng bool không được tính là số."""
    if isinstance(v, bool) and t is not bool:
        return False
    return isinstance(v, t)


def _fields(obj, where: str, req: dict, opt: dict | None = None) -> None:
    """Kiểm khóa bắt buộc, khóa lạ và kiểu."""
    if not isinstance(obj, dict):
        raise ValueError(f"{where}: phải là object")
    opt = opt or {}
    for k, t in req.items():
        if k not in obj:
            raise ValueError(f"{where}: thiếu khóa '{k}'")
        if not _is(obj[k], t):
            raise ValueError(f"{where}.{k}: sai kiểu ({type(obj[k]).__name__})")
    for k, v in obj.items():
        if k in req:
            continue
        if k not in opt:
            raise ValueError(f"{where}: khóa lạ '{k}'")
        if not _is(v, opt[k]):
            raise ValueError(f"{where}.{k}: sai kiểu ({type(v).__name__})")


def _enum(v, allowed: set, where: str) -> None:
    if v not in allowed:
        raise ValueError(f"{where}: {v!r} không thuộc {sorted(allowed)}")


def _span(obj: dict, where: str, total: int) -> None:
    if not 0 <= obj["from"] < obj["to"] <= total:
        raise ValueError(f"{where}: khoảng [{obj['from']}, {obj['to']}) sai (cần 0 ≤ from < to ≤ {total})")


def _check_events(events: list, total: int) -> None:
    seen: set = set()
    prev = None
    for i, e in enumerate(events):
        w = f"events[{i}]"
        _fields(e, w, EVENT_REQ, EVENT_OPT)
        _enum(e["kind"], KINDS, f"{w}.kind")
        _enum(e["anchor"], ANCHORS, f"{w}.anchor")
        if e["id"] in seen:
            raise ValueError(f"{w}.id: trùng '{e['id']}'")
        seen.add(e["id"])
        if not 0 <= e["f"] <= total:
            raise ValueError(f"{w}.f: {e['f']} ngoài [0, {total}]")
        if prev is not None and e["f"] < prev:
            raise ValueError(f"{w}.f: {e['f']} < {prev}, events chưa sắp theo f")
        prev = e["f"]
        if "durF" in e and e["durF"] <= 0:
            raise ValueError(f"{w}.durF: phải > 0")
        if "peakPos" in e and not 0 < e["peakPos"] < 1:
            raise ValueError(f"{w}.peakPos: phải trong (0, 1)")
        if "duckDb" in e and not 0 <= e["duckDb"] <= MAX_DUCK_DB:
            raise ValueError(f"{w}.duckDb: phải trong [0, {MAX_DUCK_DB:g}]")


def _check_marks(marks: list, total: int) -> None:
    for i, m in enumerate(marks):
        w = f"marks[{i}]"
        _fields(m, w, MARK_REQ, MARK_OPT)
        _enum(m["id"], MARK_IDS, f"{w}.id")
        if not 0 <= m["f"] <= total:
            raise ValueError(f"{w}.f: {m['f']} ngoài [0, {total}]")
        if "to" in m and not m["f"] < m["to"] <= total:
            raise ValueError(f"{w}.to: phải trong ({m['f']}, {total}]")
        if "durS" in m and m["durS"] <= 0:
            raise ValueError(f"{w}.durS: phải > 0")


def _check_sections(sections: list, total: int) -> None:
    pos = 0
    for i, s in enumerate(sections):
        w = f"sections[{i}]"
        _fields(s, w, SECTION_REQ)
        _enum(s["name"], SECTION_NAMES, f"{w}.name")
        _span(s, w, total)
        if s["from"] != pos:
            raise ValueError(f"{w}.from: {s['from']} ≠ {pos}, sections phải liền nhau từ 0")
        pos = s["to"]
    if pos != total:
        raise ValueError(f"sections: phủ tới {pos} ≠ totalFrames {total}")
    if "full" not in {s["name"] for s in sections}:
        raise ValueError("sections: thiếu section 'full' (cần để cân REF)")


def validate_sheet(sheet, sheet_id: str | None = None) -> dict:
    """Kiểm một sheet đã parse; trả lại chính nó nếu hợp lệ."""
    _fields(sheet, "cues", SHEET_KEYS)
    for k, v in FIXED.items():
        if sheet[k] != v:
            raise ValueError(f"cues.{k}: {sheet[k]!r} ≠ {v!r}")
    if sheet_id is not None and sheet["id"] != sheet_id:
        raise ValueError(f"cues.id: {sheet['id']!r} ≠ {sheet_id!r}")
    total = sheet["totalFrames"]
    if total <= 0:
        raise ValueError("cues.totalFrames: phải > 0")
    _check_sections(sheet["sections"], total)
    for i, k in enumerate(sheet["keys"]):
        _fields(k, f"keys[{i}]", KEY_REQ)
        _enum(k["root"], {"A"}, f"keys[{i}].root")
        _enum(k["mode"], {"minor", "major"}, f"keys[{i}].mode")
    _check_marks(sheet["marks"], total)
    _check_events(sheet["events"], total)
    for i, s in enumerate(sheet["silences"]):
        _fields(s, f"silences[{i}]", SILENCE_REQ)
        _enum(s["kind"], SILENCE_KINDS, f"silences[{i}].kind")
        _enum(s["scope"], SCOPES, f"silences[{i}].scope")
        _span(s, f"silences[{i}]", total)
    for i, c in enumerate(sheet["cuts"]):
        _fields(c, f"cuts[{i}]", CUT_REQ)
        _enum(c["kind"], CUT_KINDS, f"cuts[{i}].kind")
        _span(c, f"cuts[{i}]", total)
    return sheet


def sheet_path(sheet_id: str, cues_dir: Path | None = None) -> Path:
    return Path(cues_dir or CUES_DIR) / f"{sheet_id}.json"


def load_sheet(sheet_id: str, cues_dir: Path | None = None) -> dict:
    """Đọc src/audio/cues/<id>.json (hoặc cues_dir) và kiểm schema 2."""
    path = sheet_path(sheet_id, cues_dir)
    if not path.is_file():
        raise ValueError(f"không thấy {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"{path}: JSON hỏng ({e})") from e
    return validate_sheet(data, sheet_id)


def sound_events(sheet: dict) -> list[dict]:
    """Bản sao các event có `sound: true`, giữ thứ tự."""
    return [dict(e) for e in sheet["events"] if e["sound"]]
