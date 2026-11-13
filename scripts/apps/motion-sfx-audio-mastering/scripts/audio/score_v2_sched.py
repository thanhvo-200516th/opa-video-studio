"""Lịch nốt của nhạc V2 (phần tách của score_v2.py).

Mọi frame lấy từ sheet: sections, marks, silences, beatFrames, barFrames. Không gõ frame trong file này;
hằng số ở đây tính theo ô / phách / phần phách. Đầu ra là danh sách sự kiện theo frame (float, không làm tròn).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_NOTE_RE = re.compile(r"^([A-G]#?)(-?\d+)$")


@dataclass(frozen=True)
class Timeline:
    """Mốc của nhạc đọc từ cues.json (frame)."""
    total: int
    bar: float
    beat: float
    hit: float        # section full bắt đầu (HIT #1)
    cut: float        # mark music-cut (đầu khoảng lặng)
    drop: float       # mark band-drop
    esus: float       # mark esus-to-e
    pad_open: float   # mark pad-open
    stop: float       # mark music-stop
    tail_end: float   # đầu khoảng near (đuôi vang bus phải tắt từ đây)
    logo: float       # section logo bắt đầu
    kick_rest: tuple[float, float]
    sections: tuple[tuple[str, float, float], ...]


def _one_mark(sheet: dict, mid: str) -> dict:
    found = [m for m in sheet["marks"] if m["id"] == mid]
    if len(found) != 1:
        raise ValueError(f"sheet: cần đúng 1 mark {mid!r}, có {len(found)}")
    return found[0]


def marks(sheet: dict, mid: str) -> list[dict]:
    """Mọi mark cùng id, sắp theo f."""
    return sorted((m for m in sheet["marks"] if m["id"] == mid), key=lambda m: m["f"])


def section(sheet: dict, name: str) -> tuple[float, float]:
    for s in sheet["sections"]:
        if s["name"] == name:
            return float(s["from"]), float(s["to"])
    raise ValueError(f"sheet: thiếu section {name!r}")


def timeline(sheet: dict) -> Timeline:
    """Đọc mốc nhạc từ sheet; thiếu mốc → ValueError."""
    near = [s for s in sheet["silences"] if s["kind"] == "near"]
    if len(near) != 1:
        raise ValueError("sheet: cần đúng 1 silence kind near")
    rest = _one_mark(sheet, "kick-rest")
    if "to" not in rest:
        raise ValueError("sheet: mark kick-rest thiếu 'to'")
    return Timeline(
        total=int(sheet["totalFrames"]), bar=float(sheet["barFrames"]), beat=float(sheet["beatFrames"]),
        hit=section(sheet, "full")[0], cut=float(_one_mark(sheet, "music-cut")["f"]),
        drop=float(_one_mark(sheet, "band-drop")["f"]), esus=float(_one_mark(sheet, "esus-to-e")["f"]),
        pad_open=float(_one_mark(sheet, "pad-open")["f"]), stop=float(_one_mark(sheet, "music-stop")["f"]),
        tail_end=float(near[0]["from"]), logo=section(sheet, "logo")[0],
        kick_rest=(float(rest["f"]), float(rest["to"])),
        sections=tuple((s["name"], float(s["from"]), float(s["to"])) for s in sheet["sections"]),
    )


def section_at(tl: Timeline, f: float) -> str:
    for name, a, b in tl.sections:
        if a <= f < b:
            return name
    return ""


def bar_span(tl: Timeline, bar: int) -> tuple[float, float]:
    """Ô `bar` (1..15) → [f0, f1)."""
    return (bar - 1) * tl.bar, bar * tl.bar


def band_ok(tl: Timeline, f: float) -> bool:
    """Band (mọi lớp trừ pad) được vang: trước band-drop, hoặc từ HIT tới music-stop."""
    return f < tl.drop or tl.hit <= f < tl.stop


def note_octave(note: str, octaves: int) -> str:
    """'F2' + 2 bát độ → 'F4'."""
    m = _NOTE_RE.match(note)
    if not m:
        raise ValueError(f"tên nốt không hợp lệ: {note!r}")
    return f"{m.group(1)}{int(m.group(2)) + octaves}"


# ---------- pad ----------
def _pad_segments(plan, tl: Timeline) -> list[tuple[float, float, tuple[str, ...]]]:
    """Đoạn pad theo ô. Ô kết ở music-cut nếu cắt ngang. Hợp âm 'X>Y': nốt cuối thay nốt thứ 2 từ esus-to-e."""
    segs = []
    for p in plan:
        if not p.pad:
            continue
        f0, f1 = bar_span(tl, p.bar)
        if f0 < tl.cut < f1:
            f1 = tl.cut
        f1 = min(f1, tl.stop)
        if ">" in p.chord:
            before = p.pad[:-1]
            after = (p.pad[0], p.pad[-1]) + p.pad[2:-1]
            if not f0 < tl.esus < f1:
                raise ValueError(f"ô {p.bar}: esus-to-e {tl.esus} ngoài ô")
            segs += [(f0, tl.esus, before), (tl.esus, f1, after)]
        else:
            segs.append((f0, f1, p.pad))
    return segs


def pad_events(plan, tl: Timeline) -> list[tuple[str, float, float]]:
    """Nốt pad (tên, f0, f1); nốt chung giữa hai đoạn liền nhau được nối (không đánh lại)."""
    events: list[list] = []
    open_: dict[str, list] = {}
    last_end = None
    for f0, f1, notes in _pad_segments(plan, tl):
        if last_end != f0:
            open_ = {}
        nxt = {}
        for name in notes:
            ev = open_.get(name)
            if ev is None:
                ev = [name, f0, f1]
                events.append(ev)
            ev[2] = f1
            nxt[name] = ev
        open_, last_end = nxt, f1
    return [(n, a, b) for n, a, b in events]


# ---------- band ----------
def pulse_bars(plan, tl: Timeline, bar_mix: dict) -> list[tuple[list[float], str, float, float, float]]:
    """Mỗi ô có pulse: (onset các bước, nốt, độ dài bước frame, LP Hz, gain)."""
    out = []
    for p in plan:
        lay = p.layers & {"pulse8", "pulse16"}
        if not lay or not p.bass:
            continue
        step = tl.beat / (4 if "pulse16" in lay else 2)
        f0, f1 = bar_span(tl, p.bar)
        steps = [f0 + k * step for k in range(int(round(tl.bar / step)))]
        steps = [f for f in steps if band_ok(tl, f)]
        _, _, lp_hz, gain = bar_mix[p.bar]
        out.append((steps, note_octave(p.bass[0], 2), step, lp_hz, gain))
    return out


def bass_notes(plan, tl: Timeline) -> list[tuple[str, float, float]]:
    """(nốt, onset, dài frame). bass4 = đen, bass8 = móc đơn, không lớp bass = tròn cả ô."""
    out = []
    for p in plan:
        if not p.bass:
            continue
        f0, f1 = bar_span(tl, p.bar)
        if "bass8" in p.layers:
            step = tl.beat / 2
        elif "bass4" in p.layers:
            step = tl.beat
        else:
            step = tl.bar
        for k in range(int(round(tl.bar / step))):
            f = f0 + k * step
            if band_ok(tl, f):
                out.append((p.bass[0], f, step))
    return out


def kick_onsets(plan, tl: Timeline) -> list[float]:
    """kick13 = phách 1 và 3; kick4 = 4 phách. Bỏ kick trong kick-rest."""
    out = []
    for p in plan:
        beats = (0, 2) if "kick13" in p.layers else (0, 1, 2, 3) if "kick4" in p.layers else ()
        f0, _ = bar_span(tl, p.bar)
        for k in beats:
            f = f0 + k * tl.beat
            if band_ok(tl, f) and not tl.kick_rest[0] <= f < tl.kick_rest[1]:
                out.append(f)
    return out


HAT_PATTERN = (0.45, 0.2, 0.8, 0.2)   # vận tốc 1/16 trong một phách (phần thân)
HAT_RISE = (0.25, 1.0)                # đoạn rise: 1/16 tăng dần


def hat_hits(plan, tl: Timeline) -> list[tuple[float, float]]:
    """(onset, vận tốc) của hats 1/16."""
    out = []
    for p in plan:
        if "hats" not in p.layers:
            continue
        f0, f1 = bar_span(tl, p.bar)
        step = tl.beat / 4
        rise = section_at(tl, f0) == "rise"
        for k in range(int(round(tl.bar / step))):
            f = f0 + k * step
            if not band_ok(tl, f):
                continue
            if rise:
                q = (f - f0) / max(tl.drop - f0, 1.0)
                v = HAT_RISE[0] + (HAT_RISE[1] - HAT_RISE[0]) * min(q, 1.0)
            else:
                v = HAT_PATTERN[k % 4]
            out.append((f, v))
    return out


def snap_onsets(plan, tl: Timeline) -> list[float]:
    """Snap phách 2 và 4."""
    out = []
    for p in plan:
        if "snap" in p.layers:
            f0, _ = bar_span(tl, p.bar)
            out += [f0 + k * tl.beat for k in (1, 3) if band_ok(tl, f0 + k * tl.beat)]
    return out
