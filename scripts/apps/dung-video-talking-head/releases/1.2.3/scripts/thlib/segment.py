"""Đo và bắt lỗi cấp thẻ, dùng chung cho bộ ghép (compose) và bộ kiểm (validate)."""
from __future__ import annotations

import bisect
from dataclasses import dataclass
from . import textmarks, textnorm

_ONSET_TOL = 1e-3
_DET = frozenset({"các", "những", "một", "mỗi", "mọi", "cái", "chiếc"})


def _t_end(pauses: dict, R) -> float:
    """S27: đầu khoảng ngắt sau từ cuối + end.pad_s, không quá độ dài nguồn."""
    lwe = float(pauses.get("last_word_end", 0.0))
    p0 = next((float(p[0]) for p in pauses.get("pauses", []) if float(p[0]) >= lwe - _ONSET_TOL), lwe)
    return min(p0 + float(R.get("end.pad_s")), float(pauses.get("duration_s", lwe)))


@dataclass(frozen=True)
class Ctx:
    words: list          # words.json (có "on", "e", "w")
    marks: object        # textmarks.Marks
    lex: object          # textmarks.Lexicon
    R: object            # Rules
    t_end: float         # mốc hết lời
    starts: tuple = ()   # các chỉ số bắt đầu thẻ (đã sắp xếp) — để tính slot
    steps_first: int | None = None   # chỉ số từ đầu tiên của thẻ liệt kê, nếu có
    pauses: dict | None = None


def make_ctx(words: list, pauses: dict, script: str | None, R, starts: tuple = (), steps_first: int | None = None) -> Ctx:
    marks = textmarks.analyse(script, words, pauses, R)
    lex = textmarks.load_lexicon(R)
    t_end = _t_end(pauses, R)
    return Ctx(
        words=words,
        marks=marks,
        lex=lex,
        R=R,
        t_end=t_end,
        starts=tuple(sorted(starts)),
        steps_first=steps_first,
        pauses=pauses,
    )


def speech(ctx: Ctx, a: int, b: int) -> float:
    """words[b-1]["e"] - words[a]["on"]"""
    if b <= a:
        return 0.0
    return float(ctx.words[b - 1]["e"]) - float(ctx.words[a]["on"])


def next_on(ctx: Ctx, b: int) -> float:
    """onset của chỉ số bắt đầu thẻ kế tiếp >= b; nếu không có thì steps_first; cuối cùng là t_end"""
    idx = bisect.bisect_left(ctx.starts, b)
    if idx < len(ctx.starts):
        return float(ctx.words[ctx.starts[idx]]["on"])
    if ctx.steps_first is not None and ctx.steps_first >= b:
        return float(ctx.words[ctx.steps_first]["on"])
    return float(ctx.t_end)


def slot(ctx: Ctx, a: int, b: int) -> float:
    """next_on(ctx, b) - words[a]["on"]"""
    if b <= a:
        return 0.0
    return next_on(ctx, b) - float(ctx.words[a]["on"])


def block_violations(ctx: Ctx, a: int, b: int) -> list[tuple[str, str]]:
    """Trả các cặp (mã, chi tiết) vi phạm cấp thẻ [a, b)."""
    violations: list[tuple[str, str]] = []
    if b <= a:
        return violations

    n_words = len(ctx.words)
    min_s = float(ctx.R.get("text.block_min_s"))
    max_s = float(ctx.R.get("text.block_max_s"))

    # 1. COMPOUND_SPLIT
    if b < n_words:
        is_glued = (ctx.marks.words[b - 1].lvl == 0 and textmarks.glued(ctx.marks, ctx.lex, b - 1))
        is_trail = textmarks.is_trail(ctx.marks, ctx.lex, b)
        if is_glued or is_trail:
            violations.append(("COMPOUND_SPLIT", f"«{ctx.words[b - 1]['w']}|{ctx.words[b]['w']}»"))

    # 2. SENTENCE_INSIDE_BLOCK
    sents = textmarks.sentences(ctx.marks)
    a_is_sent_start = any(s_start == a for s_start, s_end in sents)
    a_sent = next(((s_start, s_end) for s_start, s_end in sents if s_start == a), None)

    for s_start, s_end in sents:
        if a < s_start < b:
            if s_end > b:
                is_exception = False
                if a_is_sent_start and a_sent is not None:
                    if slot(ctx, a, a_sent[1]) < min_s:
                        is_exception = True
                if not is_exception:
                    violations.append(("SENTENCE_INSIDE_BLOCK", f"({s_start})"))

    # 3. QUOTE_SPLIT
    for q0, q1 in ctx.marks.quotes:
        if speech(ctx, q0, q1) <= max_s:
            if (q0 < a < q1) or (q0 < b < q1):
                violations.append(("QUOTE_SPLIT", f"[{q0},{q1})"))

    # 4. LINE_END_LEAD
    if ctx.marks.words[b - 1].lvl == 0 and textmarks.is_lead(ctx.marks, ctx.lex, b - 1):
        violations.append(("LINE_END_LEAD", f"«{ctx.words[b - 1]['w']}»"))

    # 5. BLOCK_WORDS (R132): mọi thẻ đều dựng một dòng hero 2–5 từ (text.hero_words_min..max), nên thẻ ít hơn
    # hero_words_min từ không dựng được — lô b02 video 20: thẻ b19 một từ «nhiều» ⇒ HERO_WORDS, agent PLAN cháy 60 lượt.
    if b - a < int(ctx.R.get("text.hero_words_min")):
        violations.append(("BLOCK_WORDS", f"{b - a} từ < {int(ctx.R.get('text.hero_words_min'))} từ"))

    # 6. BLOCK_LEN
    s_slot = slot(ctx, a, b)
    s_speech = speech(ctx, a, b)
    tol = 1e-4
    if s_slot < min_s - tol:
        violations.append(("BLOCK_LEN", f"slot {s_slot:.2f} s < {min_s:.1f} s"))
    elif s_speech > max_s + tol:
        violations.append(("BLOCK_LEN", f"speech {s_speech:.2f} s > {max_s:.1f} s"))

    return violations


_SEVERITY = (
    "COMPOUND_SPLIT",
    "SENTENCE_IN_LINE",
    "SENTENCE_INSIDE_BLOCK",
    "QUOTE_SPLIT",
    "LINE_END_LEAD",
    "BLOCK_LEN",
)


def _cost_block(ctx: Ctx, a: int, b: int, tight: frozenset = frozenset()) -> float:
    """Tính điểm phạt/giá của một thẻ [a, b). Giá càng nhỏ càng tốt."""
    min_s = float(ctx.R.get("text.block_min_s"))
    max_s = float(ctx.R.get("text.block_max_s"))
    sp = speech(ctx, a, b)
    s_slot = slot(ctx, a, b)

    cost = 0.0

    viols = block_violations(ctx, a, b)
    for code, _ in viols:
        if code in _SEVERITY or code == "BLOCK_WORDS":
            # BLOCK_WORDS nặng như BLOCK_LEN (không chèn vào _SEVERITY: thứ tự đó định trọng số mọi mã khác)
            rank = _SEVERITY.index("BLOCK_LEN" if code == "BLOCK_WORDS" else code)
            weight = 10.0 ** (3 * (6 - rank))
            if code == "BLOCK_LEN":
                vuot = 0.0
                if s_slot < min_s:
                    vuot = min_s - s_slot
                elif sp > max_s:
                    vuot = sp - max_s
                weight *= (1.0 + vuot / 0.1)
            cost += weight

    cfg = ctx.R.get("plan.seg_cost") if hasattr(ctx.R, "get") else {}
    if not isinstance(cfg, dict):
        cfg = {}
    len_dev_w = float(cfg.get("len_dev", 1.0))
    clause_cut_w = float(cfg.get("clause_cut", 20.0))
    long_clause_cut_w = float(cfg.get("long_clause_cut", 3.0))
    comma_end_w = float(cfg.get("comma_end", 1.0))
    colon_end_w = float(cfg.get("colon_end", 0.5))
    sentence_merge_w = float(cfg.get("sentence_merge", 30.0))
    tight_pen_w = float(cfg.get("tight_pen", 10.0))

    cost += len_dev_w * abs(sp - (min_s + max_s) / 2.0)

    for k in range(a, b - 1):
        if ctx.marks.words[k].lvl >= 3:
            cost += sentence_merge_w

    if b < len(ctx.words):
        lvl = ctx.marks.words[b - 1].lvl
        if lvl == 1:
            cost += comma_end_w
        elif lvl == 2:
            cost += colon_end_w
        elif lvl >= 3:
            pass
        elif lvl == 0:
            ca = b - 1
            while ca > 0 and ctx.marks.words[ca - 1].lvl == 0:
                ca -= 1
            cb = b
            while cb < len(ctx.words) and ctx.marks.words[cb - 1].lvl == 0:
                cb += 1
            if speech(ctx, ca, cb) <= max_s:
                cost += clause_cut_w
            else:
                cost += long_clause_cut_w

    if a in tight:
        cost += tight_pen_w

    return cost


def plan_blocks(ctx: Ctx, a0: int, b0: int, tight: frozenset = frozenset()) -> tuple[tuple[int, int], ...]:
    """Quy hoạch động tìm dãy thẻ tối ưu [a0, b0)."""
    if b0 <= a0:
        return ()

    max_s = float(ctx.R.get("text.block_max_s"))
    extra_s = float(ctx.R.get("plan.dp_window_extra_s"))
    window_max_sp = max_s + extra_s

    dp = {b0: (0.0, -1)}

    for i in range(b0 - 1, a0 - 1, -1):
        best_cost = float("inf")
        best_next = -1
        for j in range(i + 1, b0 + 1):
            sp = speech(ctx, i, j)
            if j > i + 1 and sp > window_max_sp:
                break
            step_c = _cost_block(ctx, i, j, tight)
            total_c = step_c + dp[j][0]
            tol = 1e-9
            if total_c < best_cost - tol:
                best_cost = total_c
                best_next = j

        if best_next == -1:
            best_next = i + 1
            best_cost = _cost_block(ctx, i, i + 1, tight) + dp[i + 1][0]

        dp[i] = (best_cost, best_next)

    res = []
    curr = a0
    while curr < b0:
        nxt = dp[curr][1]
        res.append((curr, nxt))
        curr = nxt
    return tuple(res)


def _list_ok(marks, h0: int, h1: int) -> bool:
    cuts = [k for k in range(h0, h1 - 1) if marks.words[k].lvl >= 1]
    edges = [h0 - 1] + cuts + [h1 - 1]
    return bool(cuts) and all(1 <= y - x <= 2 for x, y in zip(edges, edges[1:]))


def _has_content(marks, lex, k: int) -> bool:
    m = marks.words[k]
    if textmarks.is_caps(m.core):
        return True
    return not textmarks.is_function(marks, lex, k)


def pick_hero(
    ctx: Ctx,
    a: int,
    b: int,
    cta_keyword: str | None = None,
    cta_range: tuple[int, int] | list[int] | None = None,
    max_chars: int | None = None,
) -> tuple[int, int]:
    """Chọn từ in to (hero) cho thẻ [a, b). `max_chars` (R124, gợi ý FACE_ROOM): chỉ xét hero hiện ≤ max_chars
    ký tự và bỏ ràng buộc TIERS — hero đó dựng một hàng co cỡ (edit.json hero_row), không xuống dòng."""
    if b <= a:
        return (a, b)

    hero_min = int(ctx.R.get("text.hero_words_min"))
    hero_max = int(ctx.R.get("text.hero_words_max"))
    hero_one_row_chars = int(ctx.R.get("text.hero_one_row_chars"))
    hero_chars_soft = float(ctx.R.get("plan.hero_chars_soft"))
    side_chars_soft = float(ctx.R.get("plan.side_chars_soft"))
    W = ctx.R.get("plan.hero") or {}

    # 1. Nếu thẻ nằm trong vùng CTA (cta_range), hoặc không truyền cta_range (test gọi pick_hero với cta_keyword)
    in_cta_zone = False
    if cta_range and len(cta_range) == 2:
        c_start, c_end = cta_range[0], cta_range[1]
        if not (b <= c_start or a >= c_end):
            in_cta_zone = True
    elif cta_range is None and cta_keyword:
        # Nếu không truyền cta_range mà có cta_keyword (tương thích ngược cho các unit test gọi trực tiếp pick_hero với cta_keyword)
        # thì coi là in_cta_zone = True
        in_cta_zone = True

    # 1. Nếu có từ khoá CTA
    if cta_keyword:
        kw_tokens = tuple(cta_keyword.strip().lower().split())
        if kw_tokens:
            low_words = [ctx.marks.words[k].low for k in range(a, b)]
            for offset in range(len(low_words) - len(kw_tokens) + 1):
                if tuple(low_words[offset:offset + len(kw_tokens)]) == kw_tokens:
                    # Trong vùng CTA (hoặc khi cta_range không truyền): ép hero
                    if in_cta_zone:
                        h0 = a + offset
                        h1 = a + offset + len(kw_tokens)
                        # Nếu chuỗi từ khoá là 1 từ: mở rộng sang trái để gộp cả động từ CTA (ví dụ «Bình luận <TỪ KHOÁ>» -> 3 từ)
                        # hoặc nếu ngắn hơn hero_words_min thì mở rộng sang trái
                        if len(kw_tokens) < 2:
                            # Cấu trúc: mở sang trái gộp động từ (thường là 2 từ "Bình luận")
                            # Mở sang trái tối đa đến đầu thẻ hoặc 2 từ động từ
                            while h0 > a and (h1 - h0) < 3:
                                h0 -= 1
                        while (h1 - h0) < hero_min and h0 > a:
                            h0 -= 1
                        while (h1 - h0) < hero_min and h1 < b:
                            h1 += 1
                        return (h0, h1)

    # Chuẩn hoá token từ khoá CTA cho điều kiện loại (S20 ngoài vùng CTA)
    kw_norm_set = set(textnorm.norm(cta_keyword)) if cta_keyword else set()

    inner_lvl3 = [k for k in range(a, b - 1) if ctx.marks.words[k].lvl >= 3]

    candidates = []
    has_any_content = False

    for h0 in range(a, b):
        for h1 in range(h0 + hero_min, min(b, h0 + hero_max) + 1):
            cuts = [k for k in (h0 - 1, h1 - 1) if a <= k < b - 1]

            # Ràng buộc cứng 1: SENTENCE_IN_LINE
            if any(k not in cuts for k in inner_lvl3):
                continue

            # Ràng buộc cứng 2: mép dòng rơi vào glued hoặc trước trail
            glued_or_trail = False
            for k in cuts:
                if ctx.marks.words[k].lvl == 0 and textmarks.glued(ctx.marks, ctx.lex, k):
                    glued_or_trail = True
                    break
                if textmarks.is_trail(ctx.marks, ctx.lex, k + 1):
                    glued_or_trail = True
                    break
            if glued_or_trail:
                continue

            # Ràng buộc cứng 3: hero kết thúc bằng từ dẫn khi có bottom
            if h1 < b and ctx.marks.words[h1 - 1].lvl == 0 and textmarks.is_lead(ctx.marks, ctx.lex, h1 - 1):
                continue

            # Ràng buộc cứng 4: cắt ngang quotes
            cross_quote = False
            for q0, q1 in ctx.marks.quotes:
                # Nếu một phần của quote nằm trong [h0, h1) và một phần nằm ngoài [h0, h1)
                # Tức là [h0, h1) giao với [q0, q1) nhưng [h0, h1) không chứa trọn [q0, q1)
                # và [q0, q1) không chứa trọn [h0, h1)?
                # Khoan: "Đoạn cắt ngang mép một đoạn trích (marks.quotes) mà không chứa trọn đoạn trích đó."
                # Đoạn ở đây là hero [h0, h1).
                # Đoạn [h0, h1) cắt ngang mép quote [q0, q1): tức là mép quote q0 hoặc q1 nằm lọt BÊN TRONG (h0, h1)!
                if (h0 < q0 < h1) or (h0 < q1 < h1):
                    cross_quote = True
                    break
            if cross_quote:
                continue

            # Ràng buộc cứng 5: TIERS (cả top và bottom khác rỗng và hero_shown > hero_one_row_chars)
            hero_shown = " ".join(textmarks.shown(ctx.marks, (a, b), k, "script") for k in range(h0, h1))
            if max_chars is not None:
                if len(hero_shown) > max_chars:
                    continue
            elif h0 > a and h1 < b and len(hero_shown) > hero_one_row_chars:
                continue

            # Ràng buộc cứng: S20 ngoài vùng CTA — mọi đoạn có chữ hiển thị trùng từ khoá bị loại thẳng
            if kw_norm_set and not in_cta_zone:
                hero_norm = set(textnorm.norm(hero_shown))
                if kw_norm_set <= hero_norm:
                    continue

            content_cnt = sum(1 for k in range(h0, h1) if _has_content(ctx.marks, ctx.lex, k))
            if content_cnt > 0:
                has_any_content = True

            candidates.append((h0, h1, content_cnt, hero_shown, cuts))

    # Ràng buộc cứng 6: không có từ nội dung nào trong khi còn ứng viên khác có
    valid_cands = []
    for h0, h1, content_cnt, hero_shown, cuts in candidates:
        if has_any_content and content_cnt == 0:
            continue
        valid_cands.append((h0, h1, hero_shown, cuts))

    if not valid_cands:
        # Fallback nếu không có ứng viên nào thoả ràng buộc cứng
        fallback_h1 = min(b, a + hero_min)
        return (a, fallback_h1)

    best_score = float("-inf")
    best_pick = None

    def _line_chars(x: int, y: int) -> int:
        if y <= x:
            return 0
        return len(" ".join(ctx.marks.words[k].core for k in range(x, y)))

    for h0, h1, hero_shown, cuts in valid_cands:
        sc = sum(textmarks.weight(ctx.marks, ctx.lex, k, W) for k in range(h0, h1))
        pen = 0.0

        # phrase_edge: -1.0 cho mỗi mép lvl == 0 nằm giữa hai từ nội dung
        for k in cuts:
            if ctx.marks.words[k].lvl == 0 and not textmarks.is_function(ctx.marks, ctx.lex, k) and not textmarks.is_function(ctx.marks, ctx.lex, k + 1):
                pen += float(W.get("phrase_edge", 1.0))

        # det_top_end: -2 nếu dòng top kết bằng từ hạn định
        if h0 > a and ctx.marks.words[h0 - 1].lvl == 0 and ctx.marks.words[h0 - 1].low in _DET:
            pen += float(W.get("det_top_end", 2.0))

        # pronoun_end: -1 nếu hero kết bằng đại từ
        if ctx.marks.words[h1 - 1].lvl == 0 and ctx.marks.words[h1 - 1].low in ctx.lex.pronouns:
            pen += float(W.get("pronoun_end", 1.0))

        # func_start: -0.5 nếu hero mở đầu bằng từ chức năng
        if textmarks.is_function(ctx.marks, ctx.lex, h0):
            pen += float(W.get("func_start", 0.5))

        # inner_punct: -0.8 cho mỗi dấu câu nằm bên trong hero
        inner_p_count = sum(1 for k in range(h0, h1 - 1) if ctx.marks.words[k].lvl >= 1 and not _list_ok(ctx.marks, h0, h1))
        pen += float(W.get("inner_punct", 0.8)) * inner_p_count

        # per_word: -0.15 mỗi từ
        pen += float(W.get("per_word", 0.15)) * (h1 - h0)

        # hero_char_over: -0.5 mỗi ký tự vượt plan.hero_chars_soft
        c_hero = _line_chars(h0, h1)
        if c_hero > hero_chars_soft:
            pen += float(W.get("hero_char_over", 0.5)) * (c_hero - hero_chars_soft)

        # side_char_over: -0.3 mỗi ký tự vượt plan.side_chars_soft trên dòng top hoặc bottom
        for x, y in ((a, h0), (h1, b)):
            c_side = _line_chars(x, y)
            if c_side > side_chars_soft:
                pen += float(W.get("side_char_over", 0.3)) * (c_side - side_chars_soft)

        # end_bonus: +0.7 nếu hero kết ở lvl >= 1 hoặc đúng cuối thẻ
        bonus = 0.0
        if ctx.marks.words[h1 - 1].lvl >= 1 or h1 == b:
            bonus = float(W.get("end_bonus", 0.7))

        score = sc - pen + bonus
        key = (round(score, 6), h1, -h0)

        if best_pick is None or key > best_score:
            best_score = key
            best_pick = (h0, h1)

    return best_pick
