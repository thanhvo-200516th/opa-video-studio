"""thlib.editschema — schema `edit/1.1` (chỉ nhãn, không có giây), bộ kiểm
luật dựng (`validate`), đổi edit.json 1.0.0 sang 1.1 (`from_legacy`) và khung
đề xuất cho stage PLAN (`propose`).

Mọi chỉ số từ là nửa mở `[a, b)` vào words.json. Mọi ngưỡng đọc từ rules.json:
`text.*` (độ dài block, số từ hero, nhãn đập, khoảng cách shot, scale) và
`sfx.*` (`stomp_s`, `hook_window_s`, `cut_near_s`).

Quy ước đo (ghi rõ trong stages/PLAN.md):
- độ dài block = `e` của từ cuối − `s` của từ đầu (khoảng lời của block);
- mốc một sự kiện (nhãn đập, cú cắt) = `on` — onset thật S04 của từ;
- shot đầu là khung mở, không phải cú cắt, nên không xét CUT_SNAP.
"""

from __future__ import annotations

from typing import Any, Iterator

import jsonschema

from . import textnorm
from .rules import Rules

SCHEMA_ID = "edit/1.1"

# Biên so sánh số thực: mốc từ trong JSON làm tròn 4 chữ số (Ruling R4).
_TOL = 1e-6
_ONSET_TOL = 1e-3

_COLORS = ["warn", "gold", "ink"]
_STOMP_LIKE = ("stomp", "quote")
_PARTS = ("top", "hero", "bottom")

_RANGE = {
    "type": "array",
    "items": {"type": "integer", "minimum": 0},
    "minItems": 2,
    "maxItems": 2,
}
_RANGE_OR_NULL = {"oneOf": [_RANGE, {"type": "null"}]}
_SCALE = {"type": "number", "minimum": 1.0}
_SHIFT = {"type": "number", "minimum": -0.25, "maximum": 0.25}
_SHIFT_Y = {"type": "number", "minimum": -0.25, "maximum": 0.0}

SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "edit/1.1 — nhãn dựng video talking-head",
    "type": "object",
    "required": ["schema", "hook", "blocks", "steps", "shots", "cta"],
    "additionalProperties": False,
    "properties": {
        "schema": {"const": SCHEMA_ID},
        "hook": {
            "oneOf": [
                {
                    "type": "object",
                    "required": ["text", "color", "hit_word"],
                    "additionalProperties": False,
                    "properties": {
                        "text": {"type": "string", "minLength": 1},
                        "color": {"enum": _COLORS},
                        "hit_word": {"type": ["integer", "null"], "minimum": 0},
                    },
                },
                {"type": "null"},
            ]
        },
        "blocks": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": [
                    "id", "top", "hero", "bottom", "style", "color", "accent",
                    "display", "reveal",
                ],
                "additionalProperties": False,
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "top": _RANGE_OR_NULL,
                    "hero": _RANGE,
                    "bottom": _RANGE_OR_NULL,
                    "style": {"enum": ["script", "stomp", "quote"]},
                    "color": {"enum": [*_COLORS, None]},
                    "accent": {"type": ["integer", "null"], "minimum": 0},
                    "display": {
                        "type": "object",
                        "propertyNames": {"pattern": "^[0-9]+$"},
                        "additionalProperties": {"type": "string"},
                    },
                    "reveal": {"type": "boolean"},
                    "hero_row": {"const": True},
                },
            },
        },
        "steps": {
            "oneOf": [
                {
                    "type": "object",
                    "required": ["title", "items"],
                    "additionalProperties": False,
                    "properties": {
                        "title": {"type": "string", "minLength": 1},
                        "items": {
                            "type": "array",
                            "minItems": 3,
                            "maxItems": 5,
                            "items": {
                                "type": "object",
                                "required": ["range", "label"],
                                "additionalProperties": False,
                                "properties": {
                                    "range": _RANGE,
                                    "label": {"type": "string", "minLength": 1},
                                },
                            },
                        },
                    },
                },
                {"type": "null"},
            ]
        },
        "shots": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["cut_at_word", "s0", "s1"],
                "additionalProperties": False,
                "properties": {
                    "cut_at_word": {"type": "integer", "minimum": 0},
                    "s0": _SCALE,
                    "s1": _SCALE,
                    "x": _SHIFT,
                    "y": _SHIFT_Y,
                },
            },
        },
        "cta": {
            "oneOf": [
                {
                    "type": "object",
                    "required": ["label", "keyword"],
                    "additionalProperties": False,
                    "properties": {
                        "range": _RANGE_OR_NULL,
                        "label": {"type": "string", "minLength": 1},
                        "keyword": {"type": "string", "minLength": 1},
                    },
                },
                {"type": "null"},
            ]
        },
        "broll": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "range", "t_in", "t_out", "media", "prompt", "v", "kind"],
                "additionalProperties": False,
                "properties": {
                    "id": {"type": "string", "pattern": "^B[1-9][0-9]*$"},
                    "range": _RANGE,
                    "t_in": {"type": "number"},
                    "t_out": {"type": "number"},
                    "media": {"enum": ["still", "clip"]},
                    "prompt": {"type": "string"},
                    "v": {"type": "integer", "minimum": 1},
                    "kind": {"const": "example"},
                },
            },
        },
    },
}


# --- tiện ích chung -------------------------------------------------------


def _err(code: str, msg: str, where: str) -> dict:
    return {"code": code, "msg": msg, "where": where}


def _parts(block: dict) -> Iterator[tuple[str, list[int]]]:
    """(tên tầng, range) của các tầng có mặt trong block, theo thứ tự đọc."""
    for name in _PARTS:
        rng = block.get(name)
        if rng:
            yield name, rng


def _block_span(block: dict) -> tuple[int, int]:
    """Chỉ số từ đầu và từ cuối (nửa mở) của cả block."""
    ranges = [rng for _, rng in _parts(block)]
    return min(r[0] for r in ranges), max(r[1] for r in ranges)


def _text(words: list[dict], a: int, b: int) -> str:
    return " ".join(str(w["w"]) for w in words[a:b])


def _dur(words: list[dict], a: int, b: int) -> float:
    """Độ dài lời của đoạn [a, b): e của từ cuối − s của từ đầu."""
    return float(words[b - 1]["e"]) - float(words[a]["s"])


def _pause_dist(t: float, pause_list: list) -> float:
    """Khoảng cách từ thời điểm t tới khoảng ngắt gần nhất (0 nếu nằm trong)."""
    return min(
        (max(float(t0) - t, t - float(t1), 0.0) for t0, t1 in pause_list),
        default=float("inf"),
    )


def _hook_words(edit: dict, words: list[dict], R: Rules) -> set[int]:
    """Các từ do hook hiển thị (được phép vắng mặt trong block): từ trong cửa
    sổ hook có chữ trùng một token của hook.text, cộng chính `hit_word`."""
    hook = edit.get("hook")
    if not hook:
        return set()
    tokens = set(textnorm.norm(hook["text"]))
    window = R.get("sfx.hook_window_s")
    out = set()
    for k, w in enumerate(words):
        shown = set(textnorm.norm(str(w["w"])))
        if shown and shown <= tokens and float(w["on"]) <= window + _TOL:
            out.add(k)
    if hook.get("hit_word") is not None:
        out.add(hook["hit_word"])
    return out


# --- kiểm schema và biên chỉ số ------------------------------------------


def _schema_errors(edit: dict) -> list[dict]:
    validator = jsonschema.Draft202012Validator(SCHEMA)
    errors = []
    for exc in sorted(validator.iter_errors(edit), key=lambda e: list(e.absolute_path)):
        where = "/".join(str(p) for p in exc.absolute_path) or "edit"
        errors.append(_err("SCHEMA", f"sai schema {SCHEMA_ID}: {exc.message}", where))
    return errors


def _bounds_errors(edit: dict, words: list[dict]) -> list[dict]:
    """Chỉ số từ phải nằm trong words.json và range phải không rỗng."""
    n = len(words)
    errors: list[dict] = []

    def check_range(rng, label: str, where: str) -> bool:
        a, b = rng
        if not (0 <= a < b <= n):
            errors.append(_err("SCHEMA", f"{label} [{a}, {b}) ngoài khoảng từ 0–{n}", where))
            return False
        return True

    def check_index(value, label: str, where: str) -> None:
        if not 0 <= value < n:
            errors.append(_err("SCHEMA", f"{label} {value} ngoài khoảng từ 0–{n - 1}", where))

    for block in edit["blocks"]:
        where = block["id"]
        checked = [
            check_range(rng, f"{name} của block {where}", where) for name, rng in _parts(block)
        ]
        if not all(checked):
            continue
        hero = block["hero"]
        if block["accent"] is not None and not 0 <= block["accent"] < hero[1] - hero[0]:
            errors.append(
                _err("SCHEMA", f"accent {block['accent']} của block {where} ngoài hero "
                     f"({hero[1] - hero[0]} từ)", where)
            )
        covered = {i for _, rng in _parts(block) for i in range(*rng)}
        for key in block["display"]:
            if int(key) not in covered:
                errors.append(
                    _err("SCHEMA", f"display có từ {key} không thuộc block {where}", where)
                )

    steps = edit.get("steps")
    if steps:
        for k, item in enumerate(steps["items"]):
            check_range(item["range"], f"range của mục {k + 1}", f"steps.items[{k}]")

    hook = edit.get("hook")
    if hook and hook.get("hit_word") is not None:
        check_index(hook["hit_word"], "hit_word", "hook")

    cta = edit.get("cta")
    if cta and cta.get("range"):
        check_range(cta["range"], "cta.range", "cta")

    for k, shot in enumerate(edit["shots"]):
        check_index(shot["cut_at_word"], "cut_at_word", f"shots[{k}]")

    return errors


# --- các luật dựng --------------------------------------------------------


def _check_blocks(edit: dict, words: list[dict], R: Rules, pauses: dict | None = None) -> list[dict]:
    """BLOCK_LEN (độ dài lời và slot), HERO_WORDS (số từ hero), REVEAL_STYLE."""
    lo, hi = R.get("text.block_min_s"), R.get("text.block_max_s")
    hero_lo, hero_hi = R.get("text.hero_words_min"), R.get("text.hero_words_max")
    errors: list[dict] = []

    blocks = edit["blocks"]
    t_end = _t_end(pauses, R) if pauses else (float(words[-1]["e"]) if words else 0.0)

    # Tìm onset của mục đầu steps nếu có
    steps = edit.get("steps")
    steps_first_on = None
    if steps and steps.get("items"):
        steps_first_on = float(words[steps["items"][0]["range"][0]]["on"])

    for i, block in enumerate(blocks):
        where = block["id"]
        a, b = _block_span(block)
        speech = float(words[b - 1]["e"]) - float(words[a]["on"])
        if i + 1 < len(blocks):
            next_start_on = float(words[_block_span(blocks[i + 1])[0]]["on"])
        elif steps_first_on is not None and steps_first_on >= float(words[a]["on"]):
            next_start_on = steps_first_on
        else:
            next_start_on = t_end

        slot = next_start_on - float(words[a]["on"])
        if speech > hi + _TOL:
            errors.append(_err("BLOCK_LEN", f"block {where} nói {speech:.2f} s — quá {hi:.1f} s (tách đôi)", where))
        if slot < lo - _TOL:
            errors.append(_err("BLOCK_LEN", f"block {where} chỉ ở trên hình {slot:.2f} s — cần ≥ {lo:.1f} s (gộp với block kề)", where))

        hero_n = block["hero"][1] - block["hero"][0]
        if not hero_lo <= hero_n <= hero_hi:
            errors.append(
                _err("HERO_WORDS", f"hero của block {where} có {hero_n} từ — phải "
                     f"{hero_lo}–{hero_hi} từ", where)
            )
        if block["reveal"] and block["style"] != "script":
            errors.append(
                _err("REVEAL_STYLE", f"block {where} bật reveal nhưng style là "
                     f"'{block['style']}' — reveal chỉ dành cho block script", where)
            )
    return errors


def _check_coverage(edit: dict, words: list[dict], R: Rules) -> list[dict]:
    """OVERLAP_OR_GAP: range nối tiếp, không chồng, không bỏ từ (trừ đoạn
    nhường cho steps hoặc hook)."""
    errors: list[dict] = []
    owner: list[str | None] = [None] * len(words)

    def claim(rng, name: str) -> None:
        conflicts: dict[str, int] = {}
        for i in range(*rng):
            if owner[i] is not None:
                conflicts.setdefault(owner[i], i)
            else:
                owner[i] = name
        for other, i in conflicts.items():
            errors.append(
                _err("OVERLAP_OR_GAP", f"từ {i} («{words[i]['w']}») nằm trong cả {other} và "
                     f"{name} — các range không được chồng nhau", name)
            )

    previous_end = -1
    for block in edit["blocks"]:
        where = block["id"]
        parts = list(_parts(block))
        for (name_a, rng_a), (name_b, rng_b) in zip(parts, parts[1:]):
            if rng_a[1] > rng_b[0]:
                errors.append(
                    _err("OVERLAP_OR_GAP", f"trong block {where}, {name_a} và {name_b} không "
                         f"nối tiếp theo thứ tự top → hero → bottom", where)
                )
        start, end = _block_span(block)
        if start < previous_end:
            errors.append(
                _err("OVERLAP_OR_GAP", f"block {where} bắt đầu ở từ {start}, trước block liền "
                     f"trước — các block phải xếp theo thứ tự lời", where)
            )
        previous_end = max(previous_end, end)
        for _, rng in parts:
            claim(rng, where)

    steps = edit.get("steps")
    if steps:
        for k, item in enumerate(steps["items"]):
            claim(item["range"], f"steps.items[{k}]")

    free = _hook_words(edit, words, R)
    missing = [i for i in range(len(words)) if owner[i] is None and i not in free]
    for a, b in _runs(missing):
        errors.append(
            _err("OVERLAP_OR_GAP", f"bỏ từ {a}–{b - 1} («{_text(words, a, b)}») — mọi từ phải "
                 f"thuộc một block, một mục steps hoặc hook", f"words[{a}]")
        )
    return errors


def _check_steps(edit: dict) -> list[dict]:
    """STEPS: các mục của bảng liền nhau, và không block nào bắt đầu trong khoảng bảng
    [từ đầu mục 1, hết mục cuối) — block chen giữa làm thẻ ra trước block đó (R34) nên
    các mục sau không bao giờ hiện."""
    steps = edit.get("steps")
    if not steps:
        return []
    items, errors = steps["items"], []
    for k in range(1, len(items)):
        end, start = items[k - 1]["range"][1], items[k]["range"][0]
        if start != end:
            errors.append(_err("STEPS", f"mục {k} hết ở từ {end} nhưng mục {k + 1} bắt đầu ở từ "
                               f"{start} — các mục phải liền nhau", f"steps.items[{k}]"))
    lo, hi = items[0]["range"][0], items[-1]["range"][1]
    for block in edit["blocks"]:
        start = _block_span(block)[0]
        if lo <= start < hi:
            errors.append(_err("STEPS", f"block {block['id']} bắt đầu ở từ {start}, trong khoảng bảng "
                               f"liệt kê (từ {lo}–{hi - 1}) — không đặt block trong khoảng thời gian "
                               f"của bảng", block["id"]))
    return errors


def _runs(indices: list[int]) -> list[tuple[int, int]]:
    """Gom các chỉ số liên tiếp thành các đoạn nửa mở [a, b)."""
    runs: list[tuple[int, int]] = []
    for i in indices:
        if runs and runs[-1][1] == i:
            runs[-1] = (runs[-1][0], i + 1)
        else:
            runs.append((i, i + 1))
    return runs


def hero_has_cta_keyword(block: dict, words: list[dict], keyword: str) -> bool:
    """S20: hero HIỂN THỊ của block (tính cả `display`) chứa đủ mọi token của
    keyword CTA, so theo tập token `textnorm.norm` (không so chuỗi con: «20
    lần» không chứa «2 LẦN»). Một định nghĩa duy nhất cho validate_edit
    (CTA_KEYWORD_IN_STOMP) và planner (ứng viên stomp XOÁ / S20)."""
    wanted = set(textnorm.norm(keyword))
    shown = " ".join(
        block["display"].get(str(i), str(words[i]["w"])) for i in range(*block["hero"])
    )
    return bool(wanted) and wanted <= set(textnorm.norm(shown))


def _check_stomps(edit: dict, words: list[dict], R: Rules) -> list[dict]:
    """STOMP_SPACING, STOMP_LIKE_MAX, CTA_KEYWORD_IN_STOMP."""
    errors: list[dict] = []
    gap_min = R.get("sfx.stomp_s")
    max_like = R.get("text.max_stomp_like")

    stomp_like = [b for b in edit["blocks"] if b["style"] in _STOMP_LIKE]
    previous = None
    for block in stomp_like:
        onset = float(words[_block_span(block)[0]]["on"])
        if previous is not None and onset - previous[1] < gap_min - _TOL:
            errors.append(
                _err("STOMP_SPACING", f"block {block['id']} cách nhãn đập trước "
                     f"({previous[0]}) {onset - previous[1]:.2f} s — phải ≥ {gap_min:.0f} s",
                     block["id"])
            )
        previous = (block["id"], onset)

    like_count = len(stomp_like) + sum(1 for b in edit["blocks"] if b["reveal"])
    if like_count > max_like:
        errors.append(
            _err("STOMP_LIKE_MAX", f"video có {like_count} nhãn đập (stomp/quote/reveal) — "
                 f"tối đa {max_like}", "blocks")
        )

    cta = edit.get("cta")
    if cta:
        for block in stomp_like:
            if hero_has_cta_keyword(block, words, cta["keyword"]):
                errors.append(
                    _err("CTA_KEYWORD_IN_STOMP", f"hero của block {block['id']} chứa từ khoá "
                         f"CTA «{cta['keyword']}» — đổi block sang script hoặc chọn hero khác "
                         f"(tránh đập hai lần ở CTA)", block["id"])
                )
    return errors


def _check_hook_cta(edit: dict, words: list[dict], R: Rules) -> list[dict]:
    """HIT_WORD (hook), CTA_RANGE, CTA_TEXT (độ dài nhãn/từ khoá pill CTA — B2)."""
    errors: list[dict] = []
    hook = edit.get("hook")
    if hook and hook.get("hit_word") is not None:
        hit = hook["hit_word"]
        in_stomp = any(
            b["style"] == "stomp" and b["hero"][0] <= hit < b["hero"][1] for b in edit["blocks"]
        )
        if not in_stomp:
            errors.append(
                _err("HIT_WORD", f"hit_word {hit} («{words[hit]['w']}») không nằm trong hero "
                     f"của block stomp nào", "hook")
            )
        window = R.get("sfx.hook_window_s")
        onset = float(words[hit]["on"])
        if onset > window + _TOL:
            errors.append(
                _err("HIT_WORD", f"hit_word {hit} («{words[hit]['w']}») nói ở giây {onset:.2f} "
                     f"— hook chỉ đặt trong {window:.1f} s đầu", "hook")
            )

    cta = edit.get("cta")
    if cta is not None and not cta.get("range"):
        errors.append(
            _err("CTA_RANGE", "có cta nhưng thiếu cta.range — phải chỉ ra câu CTA bằng chỉ số "
                 "từ (lời không nói CTA thì bỏ hẳn cta và báo user)", "cta")
        )
    for key in ("label", "keyword") if cta else ():
        limit = R.get(f"text.cta_{key}_max_chars")
        if len(cta[key]) > limit:
            errors.append(_err("CTA_TEXT", f"cta.{key} «{cta[key]}» dài {len(cta[key])} ký tự — tối đa "
                               f"{limit} (pill CTA phải vừa hộp chữ)", f"cta.{key}"))
    return errors


def _t_end(pauses: dict, R: Rules) -> float:
    """S27, cùng định nghĩa với picture._t_end: đầu khoảng ngắt sau từ cuối + end.pad_s,
    không quá độ dài nguồn."""
    lwe = float(pauses["last_word_end"])
    p0 = next((float(p[0]) for p in pauses["pauses"] if float(p[0]) >= lwe - _ONSET_TOL), lwe)
    return min(p0 + R.get("end.pad_s"), float(pauses["duration_s"]))


def _check_tail(edit: dict, words: list[dict], pauses: dict, R: Rules) -> list[dict]:
    """SHOT_GAP ở mép cuối: từ lúc shot cuối bắt đầu (0 s nếu chỉ có shot đầu — R24) tới
    t_end ≤ shot_gap_max_s, trừ shot đẩy vào CTA (cắt ở/sau từ đầu câu CTA)."""
    shots, gap_lo, gap_hi = edit["shots"], R.get("text.shot_gap_min_s"), R.get("text.shot_gap_max_s")
    near = R.get("sfx.cut_near_s")
    pause_list = pauses["pauses"]
    last = len(shots) - 1
    start = float(words[shots[last]["cut_at_word"]]["on"]) if last > 0 else 0.0
    cta = edit.get("cta") or {}
    if last > 0 and cta.get("range") and shots[last]["cut_at_word"] >= cta["range"][0]:
        return []
    tail = _t_end(pauses, R) - start
    if tail <= gap_hi + _TOL:
        return []

    valid_words = [
        j for j, w in enumerate(words)
        if start + gap_lo - _TOL <= float(w["on"]) <= start + gap_hi + _TOL
        and _pause_dist(float(w["on"]), pause_list) <= near + _TOL
    ]
    extra = f" — từ cắt hợp lệ trong cửa sổ: {', '.join(str(j) for j in valid_words)}" if valid_words else ""
    return [_err("SHOT_GAP", f"shot cuối (shot {last}) giữ {tail:.2f} s tới hết video — phải ≤ "
                 f"{gap_hi:.1f} s: thêm cú cắt, hoặc cắt shot cuối ở từ đầu câu CTA{extra}", f"shots[{last}]")]


def _check_shots(edit: dict, words: list[dict], pauses: dict, R: Rules) -> list[dict]:
    """SCALE, SHOT_GAP (cả hai mép video: cú cắt đầu đo từ 0 s — R24 — và _check_tail),
    CUT_SNAP."""
    errors: list[dict] = []
    scale_max, scale_hi = R.get("text.scale_max"), R.get("text.scale_hi")
    hi_left = R.get("text.scale_hi_max_shots")
    gap_lo, gap_hi = R.get("text.shot_gap_min_s"), R.get("text.shot_gap_max_s")
    near = R.get("sfx.cut_near_s")
    pause_list = pauses["pauses"]

    for k, shot in enumerate(edit["shots"]):
        where = f"shots[{k}]"
        scale = max(shot["s0"], shot["s1"])
        if scale > scale_hi + _TOL:
            errors.append(
                _err("SCALE", f"shot {k} phóng tới {scale:.2f} — trần tuyệt đối "
                     f"{scale_hi:.2f}", where)
            )
        elif scale > scale_max + _TOL:
            if hi_left > 0:
                hi_left -= 1
            else:
                errors.append(
                    _err("SCALE", f"shot {k} phóng tới {scale:.2f} — quá {scale_max:.2f} và đã "
                         f"dùng hết {R.get('text.scale_hi_max_shots')} shot được vượt", where)
                )

        word = shot["cut_at_word"]
        onset = float(words[word]["on"])
        if k > 0:
            previous = edit["shots"][k - 1]["cut_at_word"]
            t_prev = float(words[previous]["on"]) if k > 1 else 0.0
            valid_words = [
                j for j, w in enumerate(words)
                if t_prev + gap_lo - _TOL <= float(w["on"]) <= t_prev + gap_hi + _TOL
                and _pause_dist(float(w["on"]), pause_list) <= near + _TOL
            ]
            extra = f" — từ cắt hợp lệ trong cửa sổ: {', '.join(str(j) for j in valid_words)}" if valid_words else ""

            if word <= previous:
                errors.append(
                    _err("SHOT_GAP", f"shot {k} cắt ở từ {word}, không sau cú cắt trước "
                         f"({previous}) — shots phải xếp tăng dần", where)
                )
            else:
                # R24: shot đầu chạy từ t = 0 nên cú cắt thật đầu tiên đo từ 0 s.
                gap = onset - t_prev
                if not gap_lo - _TOL <= gap <= gap_hi + _TOL:
                    errors.append(
                        _err("SHOT_GAP", f"cú cắt {k} cách {'cú trước' if k > 1 else 'đầu video'} "
                             f"{gap:.2f} s — phải {gap_lo:.1f}–{gap_hi:.1f} s{extra}", where)
                    )
            distance = _pause_dist(onset, pause_list)
            if distance > near + _TOL:
                if valid_words:
                    errors.append(
                        _err("CUT_SNAP", f"cú cắt {k} ở từ {word} («{words[word]['w']}») cách "
                             f"khoảng ngắt gần nhất {distance:.2f} s — phải ≤ {near:.1f} s{extra}", where)
                    )
    return errors + _check_tail(edit, words, pauses, R)


def _check_tiers_steps_display(edit: dict, words: list[dict], pauses: dict, R: Rules) -> list[dict]:
    errors: list[dict] = []
    hero_limit = R.get("text.hero_one_row_chars")
    close_min = R.get("text.close_min")
    punct_chars = set('.,;:!?…“”"()[]')

    # 1. TIERS & 3. DISPLAY_PUNCT
    for block in edit["blocks"]:
        where = block["id"]
        # TIERS (R124: hero_row dựng một hàng co cỡ — chỉ giới hạn text.hero_row_max_chars)
        disp = block.get("display") or {}
        hero_text = " ".join(disp.get(str(k), words[k]["w"]) for k in range(block["hero"][0], block["hero"][1]))
        if block.get("hero_row"):
            row_max = R.get("text.hero_row_max_chars")
            if len(hero_text) > row_max:
                errors.append(_err("TIERS", f"block {where} hero một hàng «{hero_text}» dài {len(hero_text)} ký tự — phải ≤ {row_max}", where))
        elif block.get("top") and block.get("bottom"):
            if len(hero_text) > hero_limit:
                errors.append(_err("TIERS", f"block {where} 3 tầng có hero «{hero_text}» dài {len(hero_text)} ký tự — phải ≤ {hero_limit}", where))

        # DISPLAY_PUNCT
        for k_str, val in (block.get("display") or {}).items():
            if any(c in punct_chars for c in val):
                errors.append(_err("DISPLAY_PUNCT", f"display của từ {k_str} trong block {where} chứa dấu câu «{val}»", where))

    # 2. STEPS_SHOT
    steps = edit.get("steps")
    if steps and steps.get("items"):
        on_first = float(words[steps["items"][0]["range"][0]]["on"])
        e_last = float(words[steps["items"][-1]["range"][1] - 1]["e"])
        shots = edit["shots"]
        t_end = _t_end(pauses, R)
        for k, shot in enumerate(shots):
            s_start = float(words[shot["cut_at_word"]]["on"]) if k > 0 else 0.0
            s_end = float(words[shots[k + 1]["cut_at_word"]]["on"]) if k + 1 < len(shots) else t_end
            # Check overlap between [s_start, s_end] and [on_first, e_last]
            if max(s_start, on_first) < min(s_end, e_last) - _TOL:
                scale = min(shot["s0"], shot["s1"])
                if scale < close_min - _TOL:
                    errors.append(_err("STEPS_SHOT", f"shot {k} (cỡ {scale:.2f}) chồng bảng liệt kê — phải ≥ {close_min:.2f}", f"shots[{k}]"))

    return errors


def validate_with_notes(
    edit: dict,
    words: list[dict],
    pauses: dict,
    R: Rules,
    marks: textmarks.Marks | None = None,
    reference: dict | list[dict] | None = None,
    script: str | None = None,
) -> tuple[list[dict], list[dict]]:
    """Kiểm một edit.json 1.1 theo bộ luật; trả về (errors, notes).
    Nếu marks is not None: thêm check_text và dry_lock_errors.
    Chạy apply_waiver theo reference."""
    from . import editrules, segment

    errors = _schema_errors(edit)
    if errors:
        return errors, []
    errors = _bounds_errors(edit, words)
    if errors:
        return errors, []

    base_errors = (
        _check_blocks(edit, words, R, pauses)
        + _check_coverage(edit, words, R)
        + _check_steps(edit)
        + _check_stomps(edit, words, R)
        + _check_hook_cta(edit, words, R)
        + _check_shots(edit, words, pauses, R)
        + _check_tiers_steps_display(edit, words, pauses, R)
    )

    if marks is not None:
        starts = tuple(sorted(
            min(k for rng in (b["top"], b["hero"], b["bottom"]) if rng for k in range(*rng))
            for b in edit.get("blocks", []) if any(b.get(k) for k in ("top", "hero", "bottom"))
        ))
        steps = edit.get("steps")
        steps_first = steps["items"][0]["range"][0] if (steps and steps.get("items")) else None
        ctx = segment.make_ctx(words, pauses, script, R, starts=starts, steps_first=steps_first)
        text_errors = editrules.check_text(edit, ctx)
        dry_errors = editrules.dry_lock_errors(edit, words, pauses, R, script=script)
        base_errors = base_errors + text_errors + dry_errors

    # Bỏ trùng theo khoá (code, where), giữ câu có độ dài lớn hơn
    def _dedup_errors(items: list[dict]) -> list[dict]:
        best: dict[tuple[str, str], dict] = {}
        order: list[tuple[str, str]] = []
        for it in items:
            k = (it.get("code", ""), it.get("where", ""))
            if k not in best:
                best[k] = it
                order.append(k)
            else:
                if len(it.get("msg", "")) > len(best[k].get("msg", "")):
                    best[k] = it
        return [best[k] for k in order]

    base_errors = _dedup_errors(base_errors)

    # Xử lý reference: nếu reference là dict (edit proposal) thì tính errors của nó, nếu là list thì dùng trực tiếp
    ref_errors = None
    if reference is not None:
        if isinstance(reference, dict):
            ref_errors = validate(reference, words, pauses, R, marks=marks, script=script)
        elif isinstance(reference, list):
            ref_errors = reference

    kept, notes = editrules.apply_waiver(base_errors, ref_errors, marks=marks, edit=edit)
    kept = _dedup_errors(kept)
    notes = _dedup_errors(notes)
    return kept, notes


def validate(
    edit: dict,
    words: list[dict],
    pauses: dict,
    R: Rules,
    marks: textmarks.Marks | None = None,
    reference: dict | list[dict] | None = None,
    script: str | None = None,
) -> list[dict]:
    """Kiểm một edit.json 1.1 theo bộ luật; trả về danh sách
    `{"code", "msg", "where"}` (rỗng = ĐẠT). Sai schema hoặc chỉ số vượt số từ
    thì trả về ngay các lỗi đó — các luật sau cần cấu trúc đúng mới đo được."""
    errors, notes = validate_with_notes(
        edit, words, pauses, R, marks=marks, reference=reference, script=script
    )
    validate.last_notes = notes
    return errors



# --- đổi edit.json 1.0.0 sang 1.1 ----------------------------------------


def _word_at(words: list[dict], t: float) -> int:
    """Từ đầu tiên có `s` ≥ t (hết lời thì lấy từ cuối)."""
    return next((k for k, w in enumerate(words) if float(w["s"]) >= t), len(words) - 1)


def from_legacy(legacy: dict, words: list[dict]) -> dict:
    """Đổi edit.json 1.0.0 (có giây) sang schema edit/1.1 (chỉ nhãn): `shots.t`
    và `cta.start` thành chỉ số từ, `fix` thành `display` của block chứa từ đó;
    mọi nhãn khác giữ nguyên. `words` phải là bảng từ mà edit cũ tham chiếu."""
    def copy_range(rng):
        return list(rng) if rng else None

    blocks = []
    for block in legacy["blocks"]:
        blocks.append({
            "id": block["id"],
            "top": copy_range(block.get("top")),
            "hero": list(block["hero"]),
            "bottom": copy_range(block.get("bottom")),
            "style": block.get("style", "script"),
            "color": block.get("color"),
            "accent": block.get("accent"),
            "display": {},
            "reveal": False,
        })

    for key, shown in (legacy.get("fix") or {}).items():
        index = int(key)
        for block in blocks:
            if any(rng[0] <= index < rng[1] for _, rng in _parts(block)):
                block["display"][str(index)] = shown
                break

    hook = legacy.get("hook")
    cta = legacy.get("cta")
    steps = legacy.get("steps")
    return {
        "schema": SCHEMA_ID,
        "hook": (
            {"text": hook["text"], "color": hook.get("color", "gold"), "hit_word": None}
            if hook else None
        ),
        "blocks": blocks,
        "steps": (
            {
                "title": steps["title"],
                "items": [
                    {"range": list(item["range"]), "label": item["label"]}
                    for item in steps["items"]
                ],
            }
            if steps else None
        ),
        "shots": [
            {
                "cut_at_word": _word_at(words, float(shot["t"])),
                "s0": shot["s0"],
                "s1": shot["s1"],
                **({"x": shot["x"]} if "x" in shot else {}),
                **({"y": shot["y"]} if "y" in shot else {}),
            }
            for shot in legacy["shots"]
        ],
        "cta": (
            {
                "range": [_word_at(words, float(cta["start"])), len(words)],
                "label": cta["label"],
                "keyword": cta["keyword"],
            }
            if cta else None
        ),
    }

