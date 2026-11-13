"""thlib.broll_plan — B-roll ở bước PLAN (spec 1.2.0 §4–§6).

- `windows`: chia ô B1..Bn tất định trong từng câu (không phụ thuộc asset hay plan), điểm cắt vào/ra ở
  khoảng ngắt (B06), bỏ ô ở đầu/cuối video (B03).
- `zones`: vùng cấm theo edit.json đã ghép — thẻ nhấn (style ≠ script), thẻ liệt kê, CTA.
- `score` / `recommend`: bản đề xuất tham lam theo điểm (neo PREP, từ chỉ trỏ, số, «ví dụ»).
- `check`: mã BROLL_* của plan.broll (mỗi lỗi có «— Sửa:»).
- `slots`: mục `broll` của edit.json.
"""

from __future__ import annotations

import math
import re

from . import candidates, textmarks, textnorm
from .rules import Rules

MEDIA = ("still", "clip")
DEICTIC = frozenset(("này", "đây", "kia"))
EXAMPLE = (("ví", "dụ"), ("chẳng", "hạn"))
SELF = frozenset(("tôi", "mình"))
BANNED = ("logo", "watermark", "text", "subtitle",
          # 1.2.2 F2 (lô b04): từ làm model ảnh sinh nhãn/chữ, số liệu giả, logo, nhân vật có bản quyền
          "side-by-side", "split screen", "comparison", "label", "labels", "caption", "captions", "annotation", "annotations",
          "notes", "graph", "chart", "metrics", "analytics", "statistics", "engagement", "youtube", "tiktok", "facebook",
          "instagram", "iphone", "macbook", "apple", "samsung", "google", "game character",
          # 1.2.3 F2 (lô b05): từ làm model ảnh sinh chữ trên giấy ghi chú / checklist / màn hình chat
          "note", "checklist", "checklists", "checkbox", "checkboxes", "written", "bullet", "bullets", "handwritten",
          "handwriting", "chat", "chatting", "message", "messages", "messaging", "texting")
_VI = re.compile("[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]", re.IGNORECASE)
_EPS = 1e-6


# ------------------------------------------------ điểm cắt


def _frame(t: float, R: Rules) -> float:
    fps = float(R.get("fps"))
    return round(t * fps) / fps


def _gap(pauses: dict, t0: float, t1: float, R: Rules) -> tuple[float, float] | None:
    """Khoảng ngắt dài nhất nằm trong [t0 − snap; t1 + snap] (giữa hai từ)."""
    snap = float(R.get("broll.pause_snap_s"))
    best = None
    for p0, p1 in pauses["pauses"]:
        if p0 >= t0 - snap and p1 <= t1 + snap and (best is None or p1 - p0 > best[1] - best[0]):
            best = (float(p0), float(p1))
    return best


def _cut(pauses: dict, t0: float, t1: float, fallback: float, R: Rules) -> tuple[float, bool]:
    """(thời điểm cắt, có ở khoảng ngắt thật không)."""
    g = _gap(pauses, t0, t1, R)
    if g and g[1] - g[0] >= float(R.get("broll.cut_pause_min_s")) - _EPS:
        return _frame(g[0] + float(R.get("broll.cut_frac")) * (g[1] - g[0]), R), True
    return _frame(fallback, R), False


def cut_in(words: list[dict], pauses: dict, a: int, R: Rules) -> tuple[float, bool]:
    prev_end = float(words[a - 1]["e"]) if a > 0 else 0.0
    on = float(words[a]["on"])
    return _cut(pauses, prev_end, on, on, R)


def cut_out(words: list[dict], pauses: dict, b: int, R: Rules) -> tuple[float, bool]:
    end = float(words[b - 1]["e"])
    nxt = float(words[b]["on"]) if b < len(words) else float(pauses["duration_s"])
    return _cut(pauses, end, nxt, end, R)


# ------------------------------------------------ ô


def windows(words: list[dict], pauses: dict, marks, t_end: float, R: Rules) -> list[dict]:
    """Các ô B1..Bn (spec §4.1–§4.3, §4.5). Mỗi ô: {id, range [a, b), t_in, t_out, dur, text}."""
    lo, hi = float(R.get("broll.min_s")), float(R.get("broll.still_max_s"))
    head, tail = float(R.get("broll.zone_head_s")), float(R.get("broll.zone_tail_s"))
    out: list[dict] = []
    for s, t in textmarks.sentences(marks):
        a = s
        while a < t:
            ci, _ = cut_in(words, pauses, a, R)
            ends = []
            for b in range(a + 1, t + 1):
                co, at_pause = cut_out(words, pauses, b, R)
                if co - ci > hi + _EPS:
                    break
                ends.append((b, co, at_pause))
            paused = [e for e in ends if e[2] and e[1] - ci >= lo - _EPS]
            pick = paused[-1] if paused else (ends[-1] if ends else None)
            if pick is None or pick[1] - ci < lo - _EPS:
                a += 1
                continue
            b, co, _ = pick
            if ci >= head - _EPS and co <= t_end - tail + _EPS:
                out.append({"range": [a, b], "t_in": round(ci, 3), "t_out": round(co, 3),
                            "dur": round(co - ci, 3), "text": " ".join(str(words[k]["w"]) for k in range(a, b))})
            a = b
    for i, w in enumerate(out, 1):
        w["id"] = f"B{i}"
    return out


# ------------------------------------------------ vùng cấm


def zones(edit: dict, words: list[dict], R: Rules) -> list[tuple[float, float, str]]:
    """Vùng cấm theo edit đã ghép (spec §4.3): [(t0, t1, nhãn)]."""
    lead, hold = float(R.get("broll.zone_lead_s")), float(R.get("broll.steps_hold_s"))
    out: list[tuple[float, float, str]] = []
    for blk in edit.get("blocks") or []:
        if blk.get("style") == "script":
            continue
        rs = [blk[k] for k in ("top", "hero", "bottom") if blk.get(k)]
        if rs:
            a0, b1 = min(r[0] for r in rs), max(r[1] for r in rs)
            out.append((float(words[a0]["on"]), float(words[b1 - 1]["e"]), f"thẻ nhấn {blk['id']}"))
    steps = edit.get("steps")
    if steps and steps.get("items"):
        a0, b1 = steps["items"][0]["range"][0], steps["items"][-1]["range"][1]
        out.append((float(words[a0]["on"]) - lead, float(words[b1 - 1]["e"]) + hold, "thẻ liệt kê"))
    cta = edit.get("cta")
    if cta and cta.get("range"):
        out.append((float(words[cta["range"][0]]["on"]) - lead, math.inf, "CTA"))
    return out


def hit(win: dict, zs: list[tuple[float, float, str]]) -> str | None:
    """Nhãn vùng cấm đầu tiên mà ô giao vào (None = ô dùng được)."""
    for z0, z1, label in zs:
        if win["t_in"] < z1 - _EPS and win["t_out"] > z0 + _EPS:
            return label
    return None


# ------------------------------------------------ điểm và đề xuất


def _tokens(text: str) -> list[str]:
    return textnorm.norm(text)


def score(win: dict, assets: list[dict], R: Rules) -> tuple[int, int | None]:
    """(điểm, chỉ số asset neo | None) — spec §4.4."""
    toks = _tokens(win["text"])
    pts, asset = 0, None
    if toks:
        need = float(R.get("broll.anchor_min"))
        for i, a in enumerate(assets or []):
            anchor = set(_tokens(a.get("anchor_quote") or ""))
            if anchor and sum(1 for t in toks if t in anchor) / len(toks) >= need - _EPS:
                pts, asset = pts + 2, i
                break
    words = [w.lower() for w in win["text"].split()]
    low = [textnorm._clean_word(w) for w in words]
    if any(w in DEICTIC for w in low):
        pts += 1
    if any(candidates._is_number_token(w) for w in words):
        pts += 1
    if any(tuple(low[k:k + 2]) in EXAMPLE for k in range(len(low) - 1)):
        pts += 1
    if low and low[0] in SELF:
        pts -= 1
    return pts, asset


def cover(chosen: list[dict], t_end: float) -> float:
    return sum(w["dur"] for w in chosen) / t_end if t_end > 0 else 0.0


def _close(a: dict, b: dict, gap: float) -> bool:
    return a["t_in"] < b["t_out"] + gap - _EPS and b["t_in"] < a["t_out"] + gap - _EPS


def recommend(wins: list[dict], zs: list, t_end: float, assets: list[dict], broll_class: str,
              R: Rules) -> list[dict]:
    """plan.broll đề xuất (spec §4.6): [{id, media, prompt: "?", v: 1}] theo thời gian.
    Dưới sàn min(cover_min, achievable) ⇒ lấy bộ gom theo thời gian (luôn ≥ sàn)."""
    if broll_class == "none":
        return []
    gap, per = float(R.get("broll.gap_min_s")), float(R.get("broll.per_s"))
    lo, hi = float(R.get("broll.cover_min")), float(R.get("broll.cover_max"))
    cap_n = int(t_end // per)
    scored = {w["id"]: score(w, assets, R)[0] for w in wins}
    pool = sorted((w for w in wins if hit(w, zs) is None), key=lambda w: (-scored[w["id"]], w["t_in"], w["dur"]))
    chosen: list[dict] = []
    for w in pool:
        if cover(chosen, t_end) >= lo - _EPS or len(chosen) >= cap_n:
            break
        if cover(chosen + [w], t_end) > hi + _EPS or any(_close(w, c, gap) for c in chosen):
            continue
        chosen.append(w)
    if cover(chosen, t_end) < min(lo, achievable(wins, zs, t_end, R)) - _EPS:
        chosen = _by_time(wins, zs, t_end, R, stop=lo)   # 1.2.1 F2: tham lam theo điểm dưới sàn (b03 video 11: 22 %)
    chosen.sort(key=lambda w: w["t_in"])
    clip_min = float(R.get("broll.clip_min_s"))
    long_ = [w for w in chosen if w["dur"] >= clip_min - _EPS]
    clip = min(long_, key=lambda w: (-scored[w["id"]], w["t_in"])) if long_ else None
    return [{"id": w["id"], "media": "clip" if w is clip else "still", "prompt": "?", "v": 1} for w in chosen]


def _by_time(wins: list[dict], zs: list, t_end: float, R: Rules, stop: float | None = None) -> list[dict]:
    """Gom ô dùng được theo thời gian (không xét điểm): không vướng vùng, phủ ≤ cover_max, cách ≥ gap_min_s,
    ≤ t_end // per_s ô. stop ⇒ dừng ngay khi phủ đã ≥ stop (1.2.1 F2)."""
    gap, per, hi = float(R.get("broll.gap_min_s")), float(R.get("broll.per_s")), float(R.get("broll.cover_max"))
    chosen: list[dict] = []
    for w in sorted((w for w in wins if hit(w, zs) is None), key=lambda w: w["t_in"]):
        if len(chosen) >= int(t_end // per) or (stop is not None and cover(chosen, t_end) >= stop - _EPS):
            break
        if cover(chosen + [w], t_end) <= hi + _EPS and not any(_close(w, c, gap) for c in chosen):
            chosen.append(w)
    return chosen


def achievable(wins: list[dict], zs: list, t_end: float, R: Rules) -> float:
    """Độ phủ lớn nhất gom được theo thời gian (không xét điểm) — sàn của BROLL_COVER."""
    return cover(_by_time(wins, zs, t_end, R), t_end)


# ------------------------------------------------ kiểm plan.broll


def _err(code: str, msg: str, fix: str, where: str = "broll") -> dict:
    return {"code": code, "msg": f"{msg} — Sửa: {fix}", "where": where}


def prompt_problem(prompt) -> str | None:
    """Lý do prompt không đạt (None = đạt) — spec §6 BROLL_PROMPT."""
    if not isinstance(prompt, str) or not prompt.strip() or prompt.strip() == "?":
        return "chưa viết prompt"
    n = len(prompt.split())
    if n < 8 or n > 60:
        return f"prompt {n} từ (cần 8–60)"
    if _VI.search(prompt):
        return "prompt có chữ tiếng Việt có dấu (cần tiếng Anh)"
    low = prompt.lower()
    bad = [w for w in BANNED if re.search(rf"\b{w}\b", low)]
    if bad:
        return "prompt có từ cấm: " + ", ".join(bad)
    return None


def check(broll, wins: list[dict], zs: list, t_end: float, broll_class: str, R: Rules) -> list[dict]:
    """Lỗi BROLL_* của plan.broll (rỗng = đạt) — spec §6."""
    if broll is None:
        broll = []
    if not isinstance(broll, list) or any(not isinstance(x, dict) for x in broll):
        return [_err("BROLL_UNKNOWN", "«broll» phải là danh sách {id, media, prompt, v}",
                     'viết lại dạng "broll": [{"id": "B3", "media": "still", "prompt": "…", "v": 1}]')]
    if broll_class == "none":
        return [_err("BROLL_FORBIDDEN", "video broll_class none mà plan có B-roll", '"broll": []')] if broll else []
    if not broll:
        return [_err("BROLL_REQUIRED", f"video broll_class {broll_class} phải có B-roll",
                     'chép "broll" của bản đề xuất §8 rồi viết prompt cho từng ô')]
    by_id = {w["id"]: w for w in wins}
    usable = [w["id"] for w in wins if hit(w, zs) is None]
    errors: list[dict] = []
    picked: list[tuple[dict, dict]] = []
    for i, x in enumerate(broll):
        where = f"broll[{i}]"
        w = by_id.get(x.get("id"))
        if w is None:
            errors.append(_err("BROLL_UNKNOWN", f"id «{x.get('id')}» không có trong §B",
                               "dùng id có thật: " + (", ".join(usable) or "không có"), where))
            continue
        label = hit(w, zs)
        if label:
            errors.append(_err("BROLL_ZONE", f"{w['id']} ({w['t_in']:.2f}–{w['t_out']:.2f} s) đè {label}",
                               "chọn ô khác: " + (", ".join(i2 for i2 in usable if i2 != w["id"]) or "không có"), where))
        if x.get("media") not in MEDIA:
            errors.append(_err("BROLL_CLIPS", f"{w['id']}: media «{x.get('media')}» không hợp lệ",
                               'media là "still" hoặc "clip"', where))
        why = prompt_problem(x.get("prompt"))
        if why:
            errors.append(_err("BROLL_PROMPT", f"{w['id']}: {why}",
                               "viết prompt tiếng Anh 8–60 từ tả cảnh minh hoạ đúng câu đang nói, không chữ/logo; app/web viết «a generic unbranded app»; kết quả tả bằng cảm xúc/hành động, không biểu đồ/số liệu; người là người nguyên bản (tuổi, tóc, áo)",
                               where))
        v = x.get("v", 1)
        if not isinstance(v, int) or isinstance(v, bool) or v < 1:
            errors.append(_err("BROLL_UNKNOWN", f"{w['id']}: v phải là số nguyên ≥ 1", '"v": 1', where))
        picked.append((x, w))
    gap = float(R.get("broll.gap_min_s"))
    ws = sorted((w for _, w in picked), key=lambda w: w["t_in"])
    for a, b in zip(ws, ws[1:]):
        if a["id"] == b["id"] or _close(a, b, gap):
            errors.append(_err("BROLL_OVERLAP", f"{a['id']} và {b['id']} chồng nhau hoặc cách < {gap:g} s",
                               f"bỏ {b['id']} hoặc chọn ô xa hơn"))
    clips = [(x, w) for x, w in picked if x.get("media") == "clip"]
    clip_min = float(R.get("broll.clip_min_s"))
    if len(clips) > int(R.get("broll.ai.max_clips")):
        errors.append(_err("BROLL_CLIPS", f"{len(clips)} ô clip", 'để đúng 1 ô "clip", còn lại "still"'))
    for x, w in clips:
        if w["dur"] < clip_min - _EPS:
            errors.append(_err("BROLL_CLIPS", f"{w['id']} dài {w['dur']:.2f} s < {clip_min:g} s mà là clip",
                               f'đổi {w["id"]} thành "still"'))
    uniq = list({w["id"]: w for w in ws}.values())
    got, per = cover(uniq, t_end), float(R.get("broll.per_s"))
    hi = float(R.get("broll.cover_max"))
    floor = min(float(R.get("broll.cover_min")), achievable(wins, zs, t_end, R))
    cap_n = int(t_end // per)
    if got > hi + _EPS or got < floor - _EPS or len(uniq) > cap_n:
        errors.append(_err("BROLL_COVER", f"phủ {got:.0%} với {len(uniq)} ô (cần {floor:.0%}–{hi:.0%}, tối đa {cap_n} ô)",
                           "thêm ô nếu thiếu, bớt ô nếu thừa"))
    return errors


# ------------------------------------------------ edit.json


def slots(broll, wins: list[dict]) -> list[dict]:
    """Mục `broll` của edit.json theo thời gian (id lạ bị bỏ qua) — spec §5."""
    by_id = {w["id"]: w for w in wins}
    out = []
    for x in broll if isinstance(broll, list) else []:
        w = by_id.get(x.get("id")) if isinstance(x, dict) else None
        if w is None:
            continue
        out.append({"id": w["id"], "range": list(w["range"]), "t_in": w["t_in"], "t_out": w["t_out"],
                    "media": x.get("media"), "prompt": x.get("prompt"), "v": x.get("v", 1), "kind": "example"})
    return sorted(out, key=lambda s: s["t_in"])
