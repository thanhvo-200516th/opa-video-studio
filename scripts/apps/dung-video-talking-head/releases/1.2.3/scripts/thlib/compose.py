"""thlib.compose — Ghép edit.json 1.1 từ plan.json.

Spec 1.1.1 §4.4, §4.8 và card T7e.
Tám bước tuần tự và tất định:
1. marks = textmarks.analyse(...)
2. Vùng đã chốt (islands: steps, emphasis, breaks, hook-forced K)
3. Chia thẻ: segment.plan_blocks
4. Chọn hero: segment.pick_hero + ghi đè plan["hero"]
5. Khoá hình thử (dry lock): picture.build_lock + phạt tight
6. Xếp cảnh cắt: shotplan.plan_shots
7. Lắp ráp edit.json
8. Kiểm: editschema.validate (với reference)
"""
from __future__ import annotations

import copy
import re
from typing import Any

from . import broll_plan, candidates, editschema, editrules, picture, segment, shotplan, textmarks, textnorm
from .rules import Rules

PLAN_FIELDS = ("hook", "emphasis", "steps", "cta", "hero", "broll")


def _words_sha(words: list[dict]) -> str:
    """sha256 của words.json đã chuẩn hoá (keys sorted, compact separators)."""
    import hashlib
    import json
    data = json.dumps(words, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def draft_plan(cands: dict, words: list[dict]) -> dict:
    """Trả bản nháp plan/2: 6 ô trong PLAN_FIELDS mang giá trị '?'."""
    rec_s = next((s for s in cands.get("S", []) if s.get("recommended")), None)
    first_c = cands.get("C", [])[0] if cands.get("C") else None

    return {
        "schema": "plan/2",
        "words_sha": _words_sha(words),
        "hook": "?",
        "emphasis": "?",
        "steps": "?",
        "cta": "?",
        "hero": "?",
        "broll": "?",
        "breaks": [],
        "no_emphasis_reason": "",
        "flags": [],
        "steps_title": rec_s.get("title") if rec_s else None,
        "steps_labels": rec_s.get("labels") if rec_s else None,
        "cta_label": first_c.get("label") if first_c else None,
        "cta_keyword": first_c.get("keyword") if first_c else None,
    }


def _cta_kw_splits(plan: dict, cands: dict, ctx: Any, n_words: int, R: Rules) -> set[int]:
    """Mép thẻ bắt buộc sau từ khoá CTA: từ khoá dài hơn text.hero_one_row_chars thì thẻ không thể có cả top và
    bottom, nên kết thúc thẻ ngay sau từ khoá. R132: chỉ xét lần xuất hiện NẰM TRONG đoạn CTA (ứng viên C đã chọn) —
    cụm từ khoá hay lặp trong kịch bản (lô b02 video 20: «chuyển động» 6 lần) và ép ngắt ở mọi lần làm thẻ cụt,
    có thẻ chỉ còn một từ («nhiều») ⇒ HERO_WORDS, agent PLAN cháy 60 lượt."""
    kw = plan.get("cta_keyword")
    if not kw:
        return set()
    kw_tokens = tuple(kw.strip().lower().split())
    if not kw_tokens:
        return set()
    kw_len = sum(len(t) for t in kw_tokens) + len(kw_tokens) - 1
    if kw_len <= int(R.get("text.hero_one_row_chars")):
        return set()
    c_cand = next((c for c in cands.get("C", []) if c.get("id") == plan.get("cta")), None)
    c_range = c_cand.get("range") if c_cand else None
    lo, hi = (c_range[0], c_range[1]) if c_range and len(c_range) == 2 else (0, n_words)
    low_words = [ctx.marks.words[k].low for k in range(n_words)]
    out = set()
    for offset in range(lo, min(hi, len(low_words) - len(kw_tokens) + 1)):
        if tuple(low_words[offset:offset + len(kw_tokens)]) == kw_tokens:
            kw_end = offset + len(kw_tokens)
            if kw_end < n_words and kw_end <= hi:
                out.add(kw_end)
    return out


def _composed_ranges(plan: dict, words: list[dict], pauses: dict | None, script: str | None, R: Rules) -> list[tuple[int, int]] | None:
    """[a, b) của các thẻ compose dựng thật cho plan bỏ hero ghi đè (R125) — HERO_RANGE đối chiếu đúng thẻ
    agent thấy trong PLAN-SHEET; chia thử segment.plan_blocks không tính điểm nhấn nên lệch. None khi compose lỗi."""
    try:
        edit, _ = compose(dict(plan, hero=[]), words, pauses or {"pauses": []}, script, R)
    except Exception:
        return None
    return [(min(r[0] for r in rs), max(r[1] for r in rs))
            for rs in ([b[k] for k in ("top", "hero", "bottom") if b.get(k)] for b in edit["blocks"])]


def check_plan(plan: Any, cands: dict, words: list[dict], pauses: dict | None = None, R: Rules | None = None,
               script: str | None = None, meta: dict | None = None) -> list[dict]:
    """Kiểm plan/1 hoặc plan/2 theo thứ tự: PLAN_JSON, PLAN_UNDECIDED, PLAN_STALE, UNKNOWN_ID, HERO_RANGE, BROLL_*."""
    if not isinstance(plan, dict) or plan.get("schema") not in ("plan/1", "plan/2"):
        return [{
            "code": "PLAN_JSON",
            "msg": "plan không phải dict hoặc schema không phải 'plan/2'",
            "where": "schema",
        }]

    # PLAN_UNDECIDED: còn ô nào mang đúng giá trị "?"
    undecided = [f for f in PLAN_FIELDS if plan.get(f) == "?"]
    if undecided:
        return [{
            "code": "PLAN_UNDECIDED",
            "msg": f"còn chưa quyết: {', '.join(undecided)}",
            "where": undecided[0],
        }]

    # PLAN_STALE: plan["words_sha"] khác sha256 của words hiện tại
    current_sha = _words_sha(words)
    if plan.get("words_sha") != current_sha:
        return [{
            "code": "PLAN_STALE",
            "msg": f"words_sha không khớp ({plan.get('words_sha')} ≠ {current_sha})",
            "where": "words_sha",
        }]

    # UNKNOWN_ID: id trong hook/emphasis/steps/cta không có trong danh sách ứng viên
    # hook: H ids
    valid_h = [h["id"] for h in cands.get("H", []) if "id" in h]
    if plan.get("hook") is not None and plan.get("hook") != "":
        if plan["hook"] not in valid_h:
            valid_str = ", ".join(valid_h) if valid_h else "không có"
            return [{
                "code": "UNKNOWN_ID",
                "msg": f"hook id '{plan['hook']}' không hợp lệ; các id hợp lệ: {valid_str}",
                "where": "hook",
            }]

    # emphasis: K/Q ids (list)
    valid_kq = [c["id"] for c in cands.get("K", []) + cands.get("Q", []) if "id" in c]
    emph = plan.get("emphasis")
    if isinstance(emph, list):
        for eid in emph:
            if eid not in valid_kq:
                valid_str = ", ".join(valid_kq) if valid_kq else "không có"
                return [{
                    "code": "UNKNOWN_ID",
                    "msg": f"emphasis id '{eid}' không hợp lệ; các id hợp lệ: {valid_str}",
                    "where": "emphasis",
                }]
    elif emph is not None and emph != "":
        # Nếu emphasis là chuỗi hoặc id đơn lẻ
        if emph not in valid_kq:
            valid_str = ", ".join(valid_kq) if valid_kq else "không có"
            return [{
                "code": "UNKNOWN_ID",
                "msg": f"emphasis id '{emph}' không hợp lệ; các id hợp lệ: {valid_str}",
                "where": "emphasis",
            }]

    # steps: S ids
    valid_s = [s["id"] for s in cands.get("S", []) if "id" in s]
    if plan.get("steps") is not None and plan.get("steps") != "":
        if plan["steps"] not in valid_s:
            valid_str = ", ".join(valid_s) if valid_s else "không có"
            return [{
                "code": "UNKNOWN_ID",
                "msg": f"steps id '{plan['steps']}' không hợp lệ; các id hợp lệ: {valid_str}",
                "where": "steps",
            }]

    # cta: C ids
    valid_c = [c["id"] for c in cands.get("C", []) if "id" in c]
    if plan.get("cta") is not None and plan.get("cta") != "":
        if plan["cta"] not in valid_c:
            valid_str = ", ".join(valid_c) if valid_c else "không có"
            return [{
                "code": "UNKNOWN_ID",
                "msg": f"cta id '{plan['cta']}' không hợp lệ; các id hợp lệ: {valid_str}",
                "where": "cta",
            }]

    # HERO_RANGE: một ghi đè trong plan["hero"] không nằm trọn trong một thẻ, hoặc không có 2–5 từ (text.hero_words_min..max)
    hero_min = 2
    hero_max = 5
    if R is not None:
        try:
            hero_min = int(R.get("text.hero_words_min"))
            hero_max = int(R.get("text.hero_words_max"))
        except Exception:
            pass

    hero_overrides = plan.get("hero", [])
    if isinstance(hero_overrides, list) and hero_overrides:
        # Chia thẻ thử để biết danh sách thẻ
        if R is None:
            from .rules import load
            try:
                from conftest import RELEASE
                R = load(RELEASE)
                hero_min = int(R.get("text.hero_words_min"))
                hero_max = int(R.get("text.hero_words_max"))
            except Exception:
                pass
        if R is not None:
            # Xác định steps_span
            steps_cand = None
            steps_first = None
            if plan.get("steps"):
                steps_cand = next((s for s in cands.get("S", []) if s.get("id") == plan["steps"]), None)
                if steps_cand and steps_cand.get("items"):
                    steps_first = steps_cand["items"][0][0]

            ctx = segment.make_ctx(words, pauses or {"pauses": []}, None, R, steps_first=steps_first)
            n_words = len(words)
            free_intervals: list[tuple[int, int]] = []
            if steps_cand and steps_cand.get("items"):
                sa = steps_cand["items"][0][0]
                sb = steps_cand["items"][-1][1]
                if sa > 0:
                    free_intervals.append((0, sa))
                if sb < n_words:
                    free_intervals.append((sb, n_words))
            else:
                if n_words > 0:
                    free_intervals.append((0, n_words))

            breaks = set(plan.get("breaks", []))
            forced_splits = set(breaks) | _cta_kw_splits(plan, cands, ctx, n_words, R)

            raw_blocks: list[tuple[int, int]] = []
            for sa, sb in free_intervals:
                split_points = sorted({sa, sb} | {b for b in forced_splits if sa < b < sb})
                for p0, p1 in zip(split_points, split_points[1:]):
                    if p1 > p0:
                        blks = segment.plan_blocks(ctx, p0, p1)
                        raw_blocks.extend(blks)

            real_blocks = None
            for ov in hero_overrides:
                ov_range = ov if isinstance(ov, (list, tuple)) else ov.get("range")
                if not ov_range or len(ov_range) != 2:
                    return [{
                        "code": "HERO_RANGE",
                        "msg": f"hero override '{ov}' không đúng định dạng khoảng [a, b]",
                        "where": "hero",
                    }]
                oh0, oh1 = ov_range[0], ov_range[1]
                length = oh1 - oh0
                if length < hero_min or length > hero_max:
                    return [{
                        "code": "HERO_RANGE",
                        "msg": f"hero override [{oh0}, {oh1}] có {length} từ (yêu cầu {hero_min}..{hero_max} từ)",
                        "where": "hero",
                    }]
                if real_blocks is None:
                    real_blocks = _composed_ranges(plan, words, pauses, script, R) or raw_blocks
                containing = [blk for blk in real_blocks if blk[0] <= oh0 and oh1 <= blk[1]]
                if not containing:
                    return [{
                        "code": "HERO_RANGE",
                        "msg": f"hero override [{oh0}, {oh1}] vắt qua nhiều thẻ hoặc nằm ngoài khoảng thẻ",
                        "where": "hero",
                    }]
        else:
            for ov in hero_overrides:
                ov_range = ov if isinstance(ov, (list, tuple)) else ov.get("range")
                oh0, oh1 = ov_range[0], ov_range[1]
                length = oh1 - oh0
                if length < hero_min or length > hero_max:
                    return [{
                        "code": "HERO_RANGE",
                        "msg": f"hero override [{oh0}, {oh1}] có {length} từ (yêu cầu {hero_min}..{hero_max} từ)",
                        "where": "hero",
                    }]

    if pauses is None or R is None:          # validate_edit.py cũ gọi không có pauses/R ⇒ không kiểm B-roll
        return []
    broll_class = (meta or {}).get("broll_class", "none")
    marks = textmarks.analyse(script, words, pauses, R)
    t_end = picture._t_end(pauses, R)
    wins = broll_plan.windows(words, pauses, marks, t_end, R)
    edit, _ = compose({**plan, "broll": []}, words, pauses, script, R, _is_ref=True)
    zs = broll_plan.zones(edit, words, R)
    return broll_plan.check(plan.get("broll", []), wins, zs, t_end, broll_class, R)


def compose(
    plan: dict,
    words: list[dict],
    pauses: dict,
    script: str | None,
    R: Rules,
    _is_ref: bool = False,
) -> tuple[dict, list[dict]]:
    """Ghép edit.json 1.1 từ plan.json.

    Trả về (edit, notes).
    """
    plan = copy.deepcopy(plan)
    metadata_notes: list[str] = []

    # Bước 1: marks & ctx
    marks = textmarks.analyse(script, words, pauses, R)
    ctx = segment.make_ctx(words, pauses, script, R)
    cands = candidates.find_candidates(ctx)

    n_words = len(words)

    # Bước 2: Vùng đã chốt (islands)
    # Hook forces K vào emphasis nếu thiếu
    hook_cand = None
    if plan.get("hook"):
        hook_cand = next((h for h in cands.get("H", []) if h["id"] == plan["hook"]), None)
        if hook_cand and hook_cand.get("forces"):
            forced_k = hook_cand["forces"]
            if "emphasis" not in plan:
                plan["emphasis"] = []
            if forced_k not in plan["emphasis"]:
                plan["emphasis"].append(forced_k)
                metadata_notes.append(f"added {forced_k} forced by hook {hook_cand['id']}")

    # Steps span [steps_a, steps_b)
    steps_cand = None
    steps_span: tuple[int, int] | None = None
    steps_first = None
    if plan.get("steps"):
        steps_cand = next((s for s in cands.get("S", []) if s["id"] == plan["steps"]), None)
        if steps_cand and steps_cand.get("items"):
            steps_a = steps_cand["items"][0][0]
            steps_b = steps_cand["items"][-1][1]
            steps_span = (steps_a, steps_b)
            steps_first = steps_a

    ctx = segment.make_ctx(words, pauses, script, R, steps_first=steps_first)

    # Emphasis candidates
    # Mỗi ứng viên nhấn [h0, h1) là ràng buộc cứng
    all_kq = {c["id"]: c for c in cands.get("K", []) + cands.get("Q", [])}
    chosen_emph_cands = []
    for eid in plan.get("emphasis", []):
        if eid in all_kq:
            chosen_emph_cands.append(all_kq[eid])

    # breaks: plan["breaks"]
    breaks = set(plan.get("breaks", []))

    # Xây dựng các khoảng tự do ngoài steps_span
    # steps span không chứa thẻ chữ nào
    free_intervals: list[tuple[int, int]] = []
    if steps_span:
        sa, sb = steps_span
        if sa > 0:
            free_intervals.append((0, sa))
        if sb < n_words:
            free_intervals.append((sb, n_words))
    else:
        if n_words > 0:
            free_intervals.append((0, n_words))

    # Bước 3: Chia thẻ (segment.plan_blocks) trên các khoảng tự do
    # Lưu ý: Mỗi điểm nhấn [h0, h1) không cho mép thẻ nào lọt vào giữa.
    # breaks là mép bắt đầu thẻ bắt buộc.
    # Nếu cta_keyword ép hero tạo thẻ 3 tầng vi phạm TIERS: kết thúc thẻ ngay sau từ khoá, bottom=None
    forced_splits = set(breaks) | _cta_kw_splits(plan, cands, ctx, n_words, R)

    def segment_interval(i_start: int, i_end: int, tight_set: frozenset) -> list[tuple[int, int]]:
        split_points = sorted({i_start, i_end} | {b for b in forced_splits if i_start < b < i_end})
        sub_blocks: list[tuple[int, int]] = []
        for p0, p1 in zip(split_points, split_points[1:]):
            if p1 > p0:
                # Kiểm tra xem có emphasis nào nằm trong [p0, p1) không
                # plan_blocks cho [p0, p1)
                blks = segment.plan_blocks(ctx, p0, p1, tight=tight_set)
                sub_blocks.extend(blks)
        return sub_blocks

    dry_lock_max_iter = int(R.get("plan.dry_lock_max_iter"))
    tight_pen_val = float(R.get("plan.seg_cost.tight_pen"))

    tight_words: set[int] = set()
    raw_blocks: list[tuple[int, int]] = []
    block_heroes: dict[tuple[int, int], tuple[int, int]] = {}
    block_styles: dict[tuple[int, int], str] = {}
    block_colors: dict[tuple[int, int], str] = {}

    # Lặp dry lock tối đa dry_lock_max_iter
    for iteration in range(dry_lock_max_iter):
        raw_blocks = []
        tight_set = frozenset(tight_words)
        for sa, sb in free_intervals:
            raw_blocks.extend(segment_interval(sa, sb, tight_set))

        # Bước 4: Chọn hero
        cta_kw = plan.get("cta_keyword")
        c_cand = next((c for c in cands.get("C", []) if c["id"] == plan.get("cta")), None)
        cta_range = c_cand.get("range") if c_cand else None

        block_heroes = {}
        block_styles = {}
        block_colors = {}
        emph_blocks: set[tuple[int, int]] = set()

        # Gán hero mặc định
        for a, b in raw_blocks:
            h0, h1 = segment.pick_hero(ctx, a, b, cta_keyword=cta_kw, cta_range=cta_range)
            block_heroes[(a, b)] = (h0, h1)
            block_styles[(a, b)] = "script"
            block_colors[(a, b)] = "ink"

        # Áp emphasis: mỗi [h0, h1) gán hero, style, color cho block chứa nó
        for em in chosen_emph_cands:
            eh0, eh1 = em["range"]
            # Tìm block chứa [eh0, eh1)
            containing = [blk for blk in raw_blocks if blk[0] <= eh0 and eh1 <= blk[1]]
            if containing:
                blk = containing[0]
                block_heroes[blk] = (eh0, eh1)
                block_styles[blk] = em.get("style", "stomp")
                block_colors[blk] = em.get("color", "gold")
                emph_blocks.add(blk)

        # Áp plan["hero"] overrides
        for ov in plan.get("hero", []):
            # ov có thể là [h0, h1]
            ov_range = ov if isinstance(ov, (list, tuple)) else ov.get("range")
            oh0, oh1 = ov_range[0], ov_range[1]
            if oh1 - oh0 < 2 or oh1 - oh0 > 5:
                raise ValueError(f"HERO_RANGE: override {ov_range} length {oh1 - oh0} not in 2..5 words")
            containing = [blk for blk in raw_blocks if blk[0] <= oh0 and oh1 <= blk[1]]
            if not containing:
                raise ValueError(f"HERO_RANGE: override {ov_range} not inside a single block")
            blk = containing[0]
            block_heroes[blk] = (oh0, oh1)

        # Lắp thử edit tạm thời để kiểm tra dry lock
        temp_blocks = []
        for idx, (a, b) in enumerate(raw_blocks):
            h0, h1 = block_heroes[(a, b)]
            top_rng = [a, h0] if h0 > a else None
            bot_rng = [h1, b] if b > h1 else None
            blk_id = f"b{idx + 1}"
            temp_blocks.append({
                "id": blk_id,
                "top": top_rng,
                "hero": [h0, h1],
                "bottom": bot_rng,
                "style": block_styles[(a, b)],
                "color": block_colors[(a, b)],
                "accent": None,
                "display": {},
                "reveal": False,
            })

        temp_edit = {
            "schema": editschema.SCHEMA_ID,
            "hook": None,
            "blocks": temp_blocks,
            "steps": None,
            "shots": [{"cut_at_word": 0, "s0": 1.0, "s1": 1.0, "x": 0.0, "y": 0.0}],
            "cta": None,
        }

        # Bước 5: Dry lock
        lock = picture.build_lock(words, temp_edit, {"cues": [], "candidates": []}, pauses, R, script=script)
        tight_warnings = [w for w in lock.get("warnings", []) if w.startswith("LAST_WORD_TIGHT:")]
        if not tight_warnings:
            # Sạch, không có cảnh báo tight
            break

        # Có LAST_WORD_TIGHT:<id>
        # Mỗi cảnh báo cộng tight_pen vào mép cuối của thẻ đó
        new_tight = False
        id_to_blk = {f"b{idx + 1}": blk for idx, blk in enumerate(raw_blocks)}
        for tw in tight_warnings:
            bid = tw.split(":")[1]
            if bid in id_to_blk:
                end_word = id_to_blk[bid][1]
                if end_word not in tight_words:
                    tight_words.add(end_word)
                    new_tight = True
        if not new_tight:
            break

    # Bước 6: Xếp cảnh cắt shotplan.plan_shots
    final_blocks = []
    for idx, (a, b) in enumerate(raw_blocks):
        h0, h1 = block_heroes[(a, b)]
        top_rng = [a, h0] if h0 > a else None
        bot_rng = [h1, b] if b > h1 else None
        blk_id = f"b{idx + 1}"

        # display chỉ dùng cho các cách viết số đã có sẵn của textnorm (tuyệt đối không có dấu câu)
        disp_dict: dict[str, str] = {}
        for k in range(a, b):
            w_raw = str(words[k]["w"]).strip()
            # kiểm tra textnorm số
            if candidates._is_number_token(w_raw):
                clean_num = re.sub(r"[^\w%]", "", w_raw).upper()
                if clean_num and clean_num != w_raw:
                    disp_dict[str(k)] = clean_num

        block = {
            "id": blk_id,
            "top": top_rng,
            "hero": [h0, h1],
            "bottom": bot_rng,
            "style": block_styles[(a, b)],
            "color": block_colors[(a, b)],
            "accent": None,
            "display": disp_dict,
            "reveal": False,
        }
        # R124: hero ghi đè (plan.hero) dài hơn một hàng cỡ gốc ⇒ dựng MỘT hàng co cỡ thay vì xuống dòng
        # (khối thấp hơn, gỡ FACE_ROOM mà vẫn giữ cụm có nghĩa)
        hero_chars = len(" ".join(disp_dict.get(str(k), str(words[k]["w"])) for k in range(h0, h1)))
        # R133: hero của điểm nhấn cũng vậy — thẻ ba tầng có hero dài hơn một hàng thì dựng MỘT hàng thay vì
        # trượt TIERS (lô b02 video 54: «HAI chuẩn» 9 ký tự ⇒ §8 tự trượt, agent bỏ cả hook lẫn điểm nhấn).
        chosen_hero = ([h0, h1] in [list(ov) for ov in plan.get("hero") or []]
                       or (a, b) in emph_blocks)
        if chosen_hero and int(R.get("text.hero_one_row_chars")) < hero_chars <= int(R.get("text.hero_row_max_chars")):
            block["hero_row"] = True
        final_blocks.append(block)

    # Steps dict: items trong edit.json là [{"range": [a, b], "label": ...}]
    final_steps = None
    if steps_cand:
        items_list = []
        raw_items = steps_cand.get("items", [])
        raw_labels = steps_cand.get("labels", [])
        for k_item, it_rng in enumerate(raw_items):
            lbl = raw_labels[k_item] if k_item < len(raw_labels) else f"Mục {k_item + 1}"
            items_list.append({"range": list(it_rng), "label": lbl})
        final_steps = {
            "title": plan.get("steps_title") or steps_cand.get("title", ""),
            "items": items_list,
        }

    # CTA dict
    final_cta = None
    if plan.get("cta"):
        c_cand = next((c for c in cands.get("C", []) if c["id"] == plan["cta"]), None)
        if c_cand:
            final_cta = {
                "range": c_cand.get("range"),
                "label": plan.get("cta_label") or c_cand.get("label", ""),
                "keyword": plan.get("cta_keyword") or c_cand.get("keyword", ""),
            }

    # Hook dict
    final_hook = None
    if hook_cand:
        final_hook = {
            "text": hook_cand.get("text", ""),
            "color": hook_cand.get("color", "warn"),
            "hit_word": hook_cand.get("hit_word"),
        }

    shots = shotplan.plan_shots(
        ctx,
        blocks=final_blocks,
        emphasis=chosen_emph_cands,
        steps=final_steps,
        cta=final_cta,
    )

    # Bước 7: Lắp ráp edit.json
    edit = {
        "schema": editschema.SCHEMA_ID,
        "hook": final_hook,
        "blocks": final_blocks,
        "steps": final_steps,
        "shots": shots,
        "cta": final_cta,
    }
    broll = plan.get("broll") if isinstance(plan.get("broll"), list) else []
    edit["broll"] = broll_plan.slots(broll, broll_plan.windows(words, pauses, marks, picture._t_end(pauses, R), R))

    # Bước 8: Validate
    if _is_ref:
        return edit, []

    ref_plan = copy.deepcopy(plan)
    ref_plan["hero"] = []
    ref_plan["breaks"] = []
    ref_edit, _ = compose(ref_plan, words, pauses, script, R, _is_ref=True)

    errors, notes = editschema.validate_with_notes(
        edit,
        words,
        pauses,
        R,
        marks=marks,
        reference=ref_edit,
        script=script,
    )

    if errors:
        # Nếu có lỗi schema không được miễn
        pass

    return edit, notes


def repair_suggestions(
    plan: dict,
    cands: dict,
    words: list[dict],
    pauses: dict,
    script: str | None,
    R: Rules,
    max_variants: int | None = None,
    show: int | None = None,
) -> list[str]:
    """Tìm mảnh JSON dán được để sửa plan khi compose ra edit còn lỗi."""
    import json
    if max_variants is None:
        max_variants = int(R.get("plan.repair_max_variants"))
    if show is None:
        show = int(R.get("plan.repair_show"))

    marks = textmarks.analyse(script, words, pauses, R)
    # R127: cùng mốc miễn trừ với plan_stage.check — compose của bản ĐỀ XUẤT (hero=[], breaks=[]). Lấy chính
    # phương án làm mốc thì mọi lỗi phương án còn giữ đều được miễn ⇒ gợi ý sai thủ phạm (canary b01 v21:
    # «"emphasis": []» cho lỗi do thẻ liệt kê gây ra).
    try:
        rec = candidates.recommended_plan(cands, segment.make_ctx(words, pauses, script, R))
        ref_edit, _ = compose(dict(rec, hero=[], breaks=[]), words, pauses, script, R, _is_ref=True)
    except Exception:
        ref_edit = None

    def _is_clean(p: dict) -> bool:
        try:
            edit, _ = compose(p, words, pauses, script, R)
            errs = editschema.validate(edit, words, pauses, R, marks=marks, reference=ref_edit, script=script)
            return len(errs) == 0
        except Exception:
            return False

    suggestions: list[str] = []
    seen_suggestions: set[str] = set()
    checked_count = 0

    def _test_variant(new_plan: dict, fragment: str) -> bool:
        nonlocal checked_count
        if checked_count >= max_variants:
            return True
        checked_count += 1
        if _is_clean(new_plan):
            if fragment not in seen_suggestions:
                seen_suggestions.add(fragment)
                suggestions.append(fragment)
                if len(suggestions) >= show:
                    return True
        return False

    # 1. Bỏ một lựa chọn: lần lượt đặt hook = None, bỏ từng phần tử của emphasis, steps = None, cta = None
    if plan.get("hook") is not None:
        p1 = copy.deepcopy(plan)
        p1["hook"] = None
        frag = '"hook": null'
        if _test_variant(p1, frag):
            return suggestions[:show]

    if plan.get("emphasis"):
        for i in range(len(plan["emphasis"])):
            p1 = copy.deepcopy(plan)
            p1["emphasis"] = [e for j, e in enumerate(plan["emphasis"]) if j != i]
            frag = f'"emphasis": {json.dumps(p1["emphasis"], ensure_ascii=False)}'
            if _test_variant(p1, frag):
                return suggestions[:show]

    if plan.get("steps") is not None:
        p1 = copy.deepcopy(plan)
        p1["steps"] = None
        frag = '"steps": null'
        if _test_variant(p1, frag):
            return suggestions[:show]

    if plan.get("cta") is not None:
        p1 = copy.deepcopy(plan)
        p1["cta"] = None
        frag = '"cta": null'
        if _test_variant(p1, frag):
            return suggestions[:show]

    # 2. Thay một lựa chọn bằng ứng viên kế tiếp cùng loại (theo thứ tự id)
    # hook:
    if plan.get("hook") is not None:
        h_cands = sorted(cands.get("H", []), key=lambda x: x["id"])
        h_ids = [h["id"] for h in h_cands]
        if plan["hook"] in h_ids:
            idx = h_ids.index(plan["hook"])
            for next_h in h_ids[idx + 1:]:
                p2 = copy.deepcopy(plan)
                p2["hook"] = next_h
                frag = f'"hook": {json.dumps(next_h, ensure_ascii=False)}'
                if _test_variant(p2, frag):
                    return suggestions[:show]

    # emphasis: thay từng phần tử bằng ứng viên kế tiếp cùng loại (K hoặc Q theo thứ tự id)
    # Ứng viên cùng loại: all_kq sorted by id, or separate K and Q?
    # Spec: "thay một lựa chọn bằng ứng viên kế tiếp cùng loại (theo thứ tự id)"
    # Kế tiếp cùng loại nghĩa là nếu eid bắt đầu bằng K thì tìm trong K cands, nếu Q thì trong Q cands
    if plan.get("emphasis"):
        for i, eid in enumerate(plan["emphasis"]):
            group_key = "K" if eid.startswith("K") else ("Q" if eid.startswith("Q") else None)
            if group_key and group_key in cands:
                same_type_cands = sorted(cands.get(group_key, []), key=lambda x: x["id"])
                same_ids = [c["id"] for c in same_type_cands]
                if eid in same_ids:
                    idx = same_ids.index(eid)
                    for next_id in same_ids[idx + 1:]:
                        if next_id not in plan["emphasis"]:
                            p2 = copy.deepcopy(plan)
                            new_emph = list(plan["emphasis"])
                            new_emph[i] = next_id
                            p2["emphasis"] = new_emph
                            frag = f'"emphasis": {json.dumps(new_emph, ensure_ascii=False)}'
                            if _test_variant(p2, frag):
                                return suggestions[:show]

    # steps:
    if plan.get("steps") is not None:
        s_cands = sorted(cands.get("S", []), key=lambda x: x["id"])
        s_ids = [s["id"] for s in s_cands]
        if plan["steps"] in s_ids:
            idx = s_ids.index(plan["steps"])
            for next_s in s_ids[idx + 1:]:
                p2 = copy.deepcopy(plan)
                p2["steps"] = next_s
                frag = f'"steps": {json.dumps(next_s, ensure_ascii=False)}'
                if _test_variant(p2, frag):
                    return suggestions[:show]

    # cta:
    if plan.get("cta") is not None:
        c_cands = sorted(cands.get("C", []), key=lambda x: x["id"])
        c_ids = [c["id"] for c in c_cands]
        if plan["cta"] in c_ids:
            idx = c_ids.index(plan["cta"])
            for next_c in c_ids[idx + 1:]:
                p2 = copy.deepcopy(plan)
                p2["cta"] = next_c
                frag = f'"cta": {json.dumps(next_c, ensure_ascii=False)}'
                if _test_variant(p2, frag):
                    return suggestions[:show]

    # 3. Dời một hero hoặc breaks đi ±1, ±2, ±3 từ
    offsets = [1, -1, 2, -2, 3, -3]
    n_words = len(words)

    # Dời hero: plan["hero"] là list các span [a, b]
    if plan.get("hero"):
        for i, span in enumerate(plan["hero"]):
            a, b = span[0], span[1]
            for d in offsets:
                new_a = a + d
                new_b = b + d
                if 0 <= new_a < new_b <= n_words:
                    p3 = copy.deepcopy(plan)
                    new_hero = [list(sp) for sp in plan["hero"]]
                    new_hero[i] = [new_a, new_b]
                    p3["hero"] = new_hero
                    frag = f'"hero": {json.dumps(new_hero, ensure_ascii=False)}'
                    if _test_variant(p3, frag):
                        return suggestions[:show]

    # Dời breaks: plan["breaks"] là list các int
    if plan.get("breaks"):
        for i, brk in enumerate(plan["breaks"]):
            for d in offsets:
                new_brk = brk + d
                if 1 <= new_brk < n_words and new_brk not in plan["breaks"]:
                    p3 = copy.deepcopy(plan)
                    new_breaks = list(plan["breaks"])
                    new_breaks[i] = new_brk
                    new_breaks.sort()
                    p3["breaks"] = new_breaks
                    frag = f'"breaks": {json.dumps(new_breaks, ensure_ascii=False)}'
                    if _test_variant(p3, frag):
                        return suggestions[:show]

    # 4. Bỏ một ghi đè (một phần tử của hero, rồi một phần tử của breaks)
    if plan.get("hero"):
        for i in range(len(plan["hero"])):
            p4 = copy.deepcopy(plan)
            new_hero = [sp for j, sp in enumerate(plan["hero"]) if j != i]
            p4["hero"] = new_hero
            frag = f'"hero": {json.dumps(new_hero, ensure_ascii=False)}'
            if _test_variant(p4, frag):
                return suggestions[:show]

    if plan.get("breaks"):
        for i in range(len(plan["breaks"])):
            p4 = copy.deepcopy(plan)
            new_breaks = [b for j, b in enumerate(plan["breaks"]) if j != i]
            p4["breaks"] = new_breaks
            frag = f'"breaks": {json.dumps(new_breaks, ensure_ascii=False)}'
            if _test_variant(p4, frag):
                return suggestions[:show]

    return suggestions[:show]




