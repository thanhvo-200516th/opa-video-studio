"""Candidate extraction for H (hook), K (emphasis/stomp), Q (quote), V (designed break reveal),
S (steps list card), C (call to action), and recommended_plan.
Part of 1.1.1 edit plan.
"""

from __future__ import annotations
import re
from typing import Any, Dict, List, Optional, Tuple

from . import textmarks, textnorm


def _is_number_token(w: str) -> bool:
    """Từ là chữ số, dấu %, hoặc số viết bằng chữ (dùng textnorm).
    Loại trừ 'một', 'không', và 'thứ N'.
    """
    clean = textnorm._clean_word(w)
    if not clean:
        return False
    if clean in ("một", "không"):
        return False
    if clean.startswith("thứ"):
        return False
    if "%" in clean:
        return True
    if re.search(r"\d", clean):
        return True
    tokens = textnorm.norm(clean)
    if tokens and tokens[0] != "không" and (re.search(r"\d", tokens[0]) or "%" in tokens[0]):
        return True
    return False


def _has_warn(ctx: Any, a: int, b: int) -> bool:
    """Kiểm tra câu hoặc đoạn chứa từ warn."""
    warn_set = ctx.lex.warn
    for k in range(a, b):
        m = ctx.marks.words[k]
        if m.low in warn_set:
            return True
    return False


def _find_h_candidates(ctx: Any) -> List[Dict[str, Any]]:
    candidates = []
    window = float(ctx.R.get("sfx.hook_window_s"))
    max_chars = int(ctx.R.get("text.hook_max_chars"))
    sents = textmarks.sentences(ctx.marks)

    w_to_sent = {}
    for s_start, s_end in sents:
        for k in range(s_start, s_end):
            w_to_sent[k] = (s_start, s_end)

    n_words = len(ctx.words)
    for k in range(n_words):
        w = ctx.words[k]
        onset = float(w["on"])
        if onset > window:
            continue

        raw_word = str(w["w"])
        if k > 0 and ctx.marks.words[k - 1].low == "thứ":
            continue
        if not _is_number_token(raw_word):
            continue

        hit_word = k
        disp_first = raw_word.strip()
        disp_text = disp_first.upper()
        cand_range = [k, k + 1]

        if k + 1 < n_words and ctx.marks.words[k].lvl == 0:
            next_word = str(ctx.words[k + 1]["w"]).strip()
            comb = f"{disp_first} {next_word}".upper()
            if len(comb) <= max_chars:
                disp_text = comb
                cand_range = [k, k + 2]

        s_rng = w_to_sent.get(k, (k, min(k + 1, n_words)))
        color = "warn" if _has_warn(ctx, s_rng[0], s_rng[1]) else "gold"

        candidates.append({
            "range": cand_range,
            "hit_word": hit_word,
            "text": disp_text,
            "color": color,
            "why": f"hook số tại giây {onset:.2f}",
            "onset": onset,
        })

    candidates.sort(key=lambda x: x["onset"])
    for idx, c in enumerate(candidates, 1):
        c["id"] = f"H{idx}"
    return candidates


def _find_lists_ranges(ctx: Any) -> List[Tuple[int, int]]:
    """Tìm các khoảng của thẻ liệt kê (để loại trừ K/Q)."""
    max_words = int(ctx.R.get("plan.list_item_max_words"))
    wlists = textmarks.find_lists(ctx.marks, max_words, ctx.lex)
    ranges = []
    for wl in wlists:
        ranges.append(wl.lead)
        for it in wl.items:
            ranges.append(it)
    return ranges


def _find_kq_candidates(ctx: Any, cta_range: Optional[Tuple[int, int]] = None, cta_keyword: Optional[str] = None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    k_candidates = []
    q_candidates = []

    hero_max = int(ctx.R.get("text.hero_words_max"))
    short_sent_max = int(ctx.R.get("plan.short_sentence_words"))
    sents = textmarks.sentences(ctx.marks)

    w_to_sent = {}
    for s_start, s_end in sents:
        for k in range(s_start, s_end):
            w_to_sent[k] = (s_start, s_end)

    list_ranges = _find_lists_ranges(ctx)

    kw_norm = set(textnorm.norm(cta_keyword)) if cta_keyword else set()

    def is_excluded(rng: Tuple[int, int], text: str) -> bool:
        if cta_range and not (rng[1] <= cta_range[0] or rng[0] >= cta_range[1]):
            return True
        for lr in list_ranges:
            if not (rng[1] <= lr[0] or rng[0] >= lr[1]):
                return True
        norm_t = set(textnorm.norm(text))
        if kw_norm and kw_norm <= norm_t:
            return True
        for cv in ctx.lex.cta_verbs:
            if set(textnorm.norm(cv)) <= norm_t:
                return True
        return False

    n_words = len(ctx.words)

    # 1. Đoạn trong ngoặc kép dài <= text.hero_words_max => Q, rank 2
    for q0, q1 in ctx.marks.quotes:
        length = q1 - q0
        if 1 <= length <= hero_max:
            text = " ".join(ctx.words[i]["w"] for i in range(q0, q1))
            if not is_excluded((q0, q1), text):
                s_rng = w_to_sent.get(q0, (q0, q1))
                color = "warn" if _has_warn(ctx, s_rng[0], s_rng[1]) else "gold"
                onset = float(ctx.words[q0]["on"])
                q_candidates.append({
                    "range": [q0, q1],
                    "text": text,
                    "color": color,
                    "rank": 2,
                    "style": "quote",
                    "why": "đoạn trong ngoặc kép",
                    "onset": onset,
                })

    raw_k = []
    seen_ranges = set()

    qty_set = ctx.lex.quantity
    unit_set = ctx.lex.units

    # Rank 1: Chứa chữ số hoặc lượng + đơn vị
    for k in range(n_words):
        m = ctx.marks.words[k]
        is_num = _is_number_token(ctx.words[k]["w"])
        is_qty = m.low in qty_set

        if (is_num or is_qty) and k + 1 < n_words:
            m_next = ctx.marks.words[k + 1]
            if m_next.low in unit_set or is_num:
                rng = (k, k + 2)
                text = " ".join(ctx.words[i]["w"] for i in range(*rng))
                if rng not in seen_ranges and not is_excluded(rng, text):
                    s_rng = w_to_sent.get(k, rng)
                    color = "warn" if _has_warn(ctx, s_rng[0], s_rng[1]) else "gold"
                    raw_k.append({
                        "range": list(rng),
                        "text": text,
                        "color": color,
                        "rank": 1,
                        "why": "chứa chữ số hoặc lượng + đơn vị",
                        "onset": float(ctx.words[k]["on"]),
                    })
                    seen_ranges.add(rng)

    # Rank 3: cả một câu dài <= plan.short_sentence_words từ
    for s_start, s_end in sents:
        length = s_end - s_start
        if 2 <= length <= 4 and length <= short_sent_max:
            rng = (s_start, s_end)
            text = " ".join(ctx.words[i]["w"] for i in range(*rng))
            if rng not in seen_ranges and not is_excluded(rng, text):
                color = "warn" if _has_warn(ctx, s_start, s_end) else "gold"
                raw_k.append({
                    "range": list(rng),
                    "text": text,
                    "color": color,
                    "rank": 3,
                    "why": f"cả câu ngắn {length} từ",
                    "onset": float(ctx.words[s_start]["on"]),
                })
                seen_ranges.add(rng)

    # Rank 4: phần thuyết (rheme) kết thúc đoạn văn thứ nhất
    para0_end = next((k + 1 for k, m in enumerate(ctx.marks.words) if m.para == 0 and (k + 1 == n_words or ctx.marks.words[k + 1].para > 0)), None)
    if para0_end is not None:
        last_sent_para0 = next(((s_start, s_end) for s_start, s_end in sents if s_end == para0_end), None)
        if last_sent_para0 is not None:
            for span_len in (2, 3, 4):
                rheme_start = para0_end - span_len
                if rheme_start >= last_sent_para0[0]:
                    rng = (rheme_start, para0_end)
                    text = " ".join(ctx.words[i]["w"] for i in range(*rng))
                    if span_len == 2 and rng not in seen_ranges and not is_excluded(rng, text):
                        color = "warn" if _has_warn(ctx, last_sent_para0[0], last_sent_para0[1]) else "gold"
                        raw_k.append({
                            "range": list(rng),
                            "text": text,
                            "color": color,
                            "rank": 4,
                            "why": "phần thuyết kết thúc đoạn văn thứ nhất",
                            "onset": float(ctx.words[rheme_start]["on"]),
                        })
                        seen_ranges.add(rng)

    raw_k.sort(key=lambda x: x["onset"])
    for idx, k_cand in enumerate(raw_k, 1):
        k_cand["id"] = f"K{idx}"
        k_candidates.append(k_cand)

    q_candidates.sort(key=lambda x: x["onset"])
    for idx, q_cand in enumerate(q_candidates, 1):
        q_cand["id"] = f"Q{idx}"

    return k_candidates, q_candidates


def _find_v_candidates(ctx: Any) -> List[Dict[str, Any]]:
    v_candidates = []
    if not ctx.pauses or "designed_breaks" not in ctx.pauses:
        return v_candidates

    breaks = ctx.pauses["designed_breaks"]
    n_words = len(ctx.words)
    sents = textmarks.sentences(ctx.marks)

    w_to_sent = {}
    for s_start, s_end in sents:
        for k in range(s_start, s_end):
            w_to_sent[k] = (s_start, s_end)

    raw_v = []
    for br in breaks:
        after_w = br.get("after_word")
        if after_w is None or after_w + 1 >= n_words:
            continue
        start_w = after_w + 1
        s_rng = w_to_sent.get(start_w, (start_w, min(start_w + 2, n_words)))
        end_w = min(start_w + 3, s_rng[1], n_words)
        if end_w <= start_w:
            end_w = min(start_w + 1, n_words)

        text = " ".join(ctx.words[i]["w"] for i in range(start_w, end_w))
        onset = float(ctx.words[start_w]["on"])
        raw_v.append({
            "range": [start_w, end_w],
            "text": text,
            "why": f"khối chữ sau {br.get('kind', 'break')}",
            "onset": onset,
        })

    raw_v.sort(key=lambda x: x["onset"])
    for idx, v_cand in enumerate(raw_v, 1):
        v_cand["id"] = f"V{idx}"
        v_candidates.append(v_cand)

    return v_candidates


_WEAK_WORDS = frozenset({
    "có", "là", "gồm", "cần", "thường", "sẽ", "được", "phải", "nên",
    "đã", "đang", "đến", "mang", "với", "cho", "của", "tại", "ở", "vào",
    "ra", "thì", "mà", "như", "hay", "và", "hoặc"
})


def _build_steps_title(lead_words: List[str], ctx: Any, max_chars: int) -> str:
    """Xây tiêu đề thẻ liệt kê:
    - dạng «<N> <DANH TỪ>» khi câu dẫn có nêu số lượng;
    - còn lại: cụm danh từ của câu dẫn, cắt bỏ các từ yếu ở đuôi (có/là/gồm/cần/thường/sẽ …), VIẾT HOA TOÀN BỘ, <= max_chars.
    """
    n_lead = len(lead_words)
    # Check if lead specifies quantity: e.g. "ba bước", "5 yếu tố", etc.
    for i in range(n_lead - 1):
        w_curr = lead_words[i].strip()
        w_next = lead_words[i + 1].strip()
        is_num = _is_number_token(w_curr) or (ctx.marks.words[i].low in ctx.lex.quantity if i < len(ctx.marks.words) else False)
        if is_num:
            # Check unit or noun
            norm_next = textnorm._clean_word(w_next).lower()
            if norm_next in ctx.lex.units:
                title = f"{w_curr} {w_next}".upper()
                if len(title) <= max_chars:
                    return title

    # Fallback: trim weak words from the tail
    trimmed = list(lead_words)
    while trimmed:
        last_clean = textnorm._clean_word(trimmed[-1]).lower()
        if last_clean in _WEAK_WORDS:
            trimmed.pop()
        else:
            break

    title = " ".join(trimmed).upper()
    if len(title) > max_chars:
        # truncate words to fit max_chars
        words = title.split()
        while words and len(" ".join(words)) > max_chars:
            words.pop()
        title = " ".join(words)
    return title


def _find_s_candidates(ctx: Any, cta_start: Optional[int] = None) -> List[Dict[str, Any]]:
    """Luật loại S (thẻ liệt kê):
    - Lấy danh sách bằng find_lists (đã có trong repo) — nhận danh sách có 3–5 mục,
      mỗi nhãn ≤ plan.steps_label_max_chars (26), và kết thúc trước đoạn CTA.
    - Nhãn = chữ của mục, viết hoa chữ đầu, bỏ từ «và»/«hoặc» đứng đầu.
    - Tiêu đề:
      - dạng «<N> <DANH TỪ>» khi câu dẫn có nêu số lượng;
      - còn lại: cụm danh từ của câu dẫn, cắt bỏ các từ yếu ở đuôi (có/là/gồm/cần/thường/sẽ …),
        VIẾT HOA TOÀN BỘ, ≤ plan.steps_title_max_chars (30).
    - Được đề xuất khi danh sách có đánh số, hoặc song song (mọi mục cùng từ đầu tiên).
    - Quyết định Q1 của user: thẻ chỉ hiện 3 dòng ⇒ chỉ danh sách đúng 3 mục mới được đề xuất.
      Danh sách 4–5 mục vẫn liệt kê nhưng không đề xuất.
    """
    s_candidates = []
    max_words = int(ctx.R.get("plan.list_item_max_words"))

    label_max_chars = int(ctx.R.get("plan.steps_label_max_chars"))

    title_max_chars = int(ctx.R.get("plan.steps_title_max_chars"))

    wlists = textmarks.find_lists(ctx.marks, max_words, ctx.lex)

    raw_s = []
    for wl in wlists:
        items = wl.items
        if not (3 <= len(items) <= 5):
            continue

        # Kết thúc trước đoạn CTA
        last_item_end = items[-1][1]
        if cta_start is not None and last_item_end > cta_start:
            continue

        # Nhãn = chữ của mục, viết hoa chữ đầu, bỏ từ «và»/«hoặc» đứng đầu
        labels = []
        labels_ok = True
        first_words = []
        is_numbered = True

        for it_idx, (it0, it1) in enumerate(items):
            it_words = [ctx.words[i]["w"] for i in range(it0, it1)]
            if not it_words:
                labels_ok = False
                break
            first_w_low = textnorm._clean_word(it_words[0]).lower()
            if first_w_low in ("và", "hoặc", "hay"):
                it_words = it_words[1:]
            if not it_words:
                labels_ok = False
                break

            cleaned_first = textnorm._clean_word(it_words[0]).lower()
            first_words.append(cleaned_first)

            raw_label = " ".join(it_words).strip()
            # Bỏ dấu phẩy, chấm cuối nếu có
            raw_label = raw_label.rstrip(",;:.!?…")
            label = raw_label[:1].upper() + raw_label[1:] if raw_label else ""
            if len(label) > label_max_chars:
                labels_ok = False
                break
            labels.append(label)

            # Check numbering: 1., 2., một, hai, thứ nhất...
            if not (_is_number_token(it_words[0]) or cleaned_first in ("một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín", "mười", "thứ")):
                is_numbered = False

        if not labels_ok:
            continue

        # Song song: mọi mục cùng từ đầu tiên
        is_parallel = (len(set(first_words)) == 1) if first_words else False

        # Tiêu đề
        lead_words = [ctx.words[i]["w"] for i in range(wl.lead[0], wl.lead[1])]
        title = _build_steps_title(lead_words, ctx, title_max_chars)

        # Đề xuất: (đánh số hoặc song song) VÀ đúng 3 mục
        recommended = bool((is_numbered or is_parallel) and len(items) == 3)

        onset = float(ctx.words[items[0][0]]["on"])
        raw_s.append({
            "range": [wl.lead[0], items[-1][1]],
            "lead": list(wl.lead),
            "items": [list(it) for it in items],
            "labels": labels,
            "title": title,
            "recommended": recommended,
            "onset": onset,
        })

    raw_s.sort(key=lambda x: x["onset"])
    for idx, s_cand in enumerate(raw_s, 1):
        s_cand["id"] = f"S{idx}"
        s_candidates.append(s_cand)

    return s_candidates


def find_cta_from_marks(marks: Any, lex: Any, kw_max_chars: int = 16) -> List[Dict[str, Any]]:
    """Dò CTA trực tiếp từ marks và lexicon (không cần words.json/timing)."""
    sents = textmarks.sentences(marks)
    if not sents:
        return []

    n_words = len(marks.words)
    last_para = marks.words[-1].para if n_words > 0 else 0

    last_para_sents = [s for s in sents if marks.words[s[0]].para == last_para]
    if not last_para_sents:
        last_para_sents = [sents[-1]]

    raw_c = []
    for s_start, s_end in last_para_sents:
        sent_marks = [marks.words[i] for i in range(s_start, s_end)]
        sent_words = [m.pre + m.core + m.post for m in sent_marks]
        sent_lows = [m.low for m in sent_marks]

        # Tìm động từ CTA
        cta_verb_found = None
        v_idx = -1
        for cv in lex.cta_verbs:
            cv_tokens = cv.split()
            cv_len = len(cv_tokens)
            for i in range(len(sent_lows) - cv_len + 1):
                if sent_lows[i:i + cv_len] == cv_tokens:
                    cta_verb_found = cv
                    v_idx = i + cv_len
                    break
            if cta_verb_found:
                break

        if not cta_verb_found or v_idx >= len(sent_words):
            continue

        # Chuỗi VIẾT HOA hoặc chữ số theo sau
        kw_tokens = []
        curr = v_idx
        while curr < len(sent_words):
            raw_orig = sent_marks[curr].core
            if not raw_orig:
                break
            is_cap = textmarks.is_caps(raw_orig)
            is_num = bool(re.search(r"\d", raw_orig))
            if is_cap or is_num:
                kw_tokens.append(raw_orig)
                curr += 1
            else:
                break

        if not kw_tokens:
            continue

        # Riêng «AI» đứng một mình thì loại
        if len(kw_tokens) == 1 and kw_tokens[0] == "AI":
            continue

        keyword = " ".join(kw_tokens).strip()
        if len(keyword) > kw_max_chars:
            continue

        label = cta_verb_found[:1].upper() + cta_verb_found[1:]
        raw_c.append({
            "range": [s_start, s_end],
            "label": label,
            "keyword": keyword,
        })

    for idx, c_cand in enumerate(raw_c, 1):
        c_cand["id"] = f"C{idx}"
    return raw_c


def _find_c_candidates(ctx: Any) -> List[Dict[str, Any]]:
    """Luật loại C (CTA):
    - Trong đoạn văn cuối: một động từ CTA theo sau là một chuỗi VIẾT HOA hoặc chữ số dài ≤ text.cta_keyword_max_chars.
      Riêng «AI» đứng một mình thì loại.
    - Khoảng chạy từ đầu câu đó tới từ cuối cùng.
    """
    kw_max_chars = int(ctx.R.get("text.cta_keyword_max_chars"))

    cands = find_cta_from_marks(ctx.marks, ctx.lex, kw_max_chars=kw_max_chars)
    for c in cands:
        s_start = c["range"][0]
        c["onset"] = float(ctx.words[s_start]["on"])
    cands.sort(key=lambda x: x["onset"])
    for idx, c in enumerate(cands, 1):
        c["id"] = f"C{idx}"
    return cands


def find_candidates(ctx: Any) -> Dict[str, List[Dict[str, Any]]]:
    """Find candidate elements H, K, Q, V, S, C from segment context.
    Returns:
        dict with keys "H", "K", "Q", "V", "S", "C".
    """
    c_list = _find_c_candidates(ctx)
    cta_range = tuple(c_list[0]["range"]) if c_list else None
    cta_start = cta_range[0] if cta_range else None
    cta_kw = c_list[0].get("keyword") if c_list else None

    k_list, q_list = _find_kq_candidates(ctx, cta_range=cta_range, cta_keyword=cta_kw)
    h_list = _find_h_candidates(ctx)
    v_list = _find_v_candidates(ctx)
    s_list = _find_s_candidates(ctx, cta_start=cta_start)

    for h in h_list:
        hit = h["hit_word"]
        forced_k = None
        for k_cand in k_list:
            if k_cand["range"][0] <= hit < k_cand["range"][1]:
                forced_k = k_cand["id"]
                break
        h["forces"] = forced_k

    return {
        "H": h_list,
        "K": k_list,
        "Q": q_list,
        "V": v_list,
        "S": s_list,
        "C": c_list,
    }


def recommended_plan(cands: Dict[str, List[Dict[str, Any]]], ctx: Any) -> Dict[str, Any]:
    """Trả {hook, emphasis, steps, steps_title, cta, cta_label, cta_keyword, hero: [], breaks: []}:
    - hook = H tốt nhất (không có H => None).
    - emphasis = các ứng viên K/Q theo hạng, cách nhau >= sfx.stomp_s (8 s), tối đa plan.emphasis_default_max (2).
      Ứng viên hạng 4 chỉ được lấp chỗ khi số ứng viên hạng 1–3 ít hơn mức tối đa.
    - Chọn H thì ép K mà nó trỏ (forces) vào emphasis.
    - steps = ứng viên S được đề xuất (nếu có); cta = C1.
    """
    stomp_gap = float(ctx.R.get("sfx.stomp_s"))

    max_emphasis = int(ctx.R.get("plan.emphasis_default_max"))

    # Hook
    best_h = cands["H"][0] if cands.get("H") else None

    # Forced K from H
    forced_k_id = best_h.get("forces") if best_h else None

    # Pool candidates for emphasis: K and Q
    all_kq = []
    k_map = {}
    for k in cands.get("K", []):
        all_kq.append(k)
        k_map[k["id"]] = k
    for q in cands.get("Q", []):
        all_kq.append(q)

    # Separate candidates rank 1-3 vs rank 4
    rank_123 = [c for c in all_kq if c.get("rank", 1) in (1, 2, 3)]
    rank_4 = [c for c in all_kq if c.get("rank", 1) == 4]

    # Sort each by rank ascending, then onset ascending
    rank_123.sort(key=lambda x: (x.get("rank", 1), x.get("onset", 0.0)))
    rank_4.sort(key=lambda x: (x.get("rank", 1), x.get("onset", 0.0)))

    chosen_emphasis = []

    def can_add(cand: Dict[str, Any]) -> bool:
        for ch in chosen_emphasis:
            if abs(cand["onset"] - ch["onset"]) < stomp_gap:
                return False
        return True

    # If forced K exists, it must be included first
    if forced_k_id and forced_k_id in k_map:
        forced_k = k_map[forced_k_id]
        chosen_emphasis.append(forced_k)

    # Fill from rank 1-3
    for cand in rank_123:
        if len(chosen_emphasis) >= max_emphasis:
            break
        if cand["id"] in [c["id"] for c in chosen_emphasis]:
            continue
        if can_add(cand):
            chosen_emphasis.append(cand)

    # Rank 4 only fills gap when rank 1-3 is less than max
    if len(chosen_emphasis) < max_emphasis:
        for cand in rank_4:
            if len(chosen_emphasis) >= max_emphasis:
                break
            if cand["id"] in [c["id"] for c in chosen_emphasis]:
                continue
            if can_add(cand):
                chosen_emphasis.append(cand)

    # Sort chosen emphasis by onset time
    chosen_emphasis.sort(key=lambda x: x["onset"])

    # R133: HIT_WORD — từ chốt của hook phải nằm trong hero của một thẻ stomp (điểm nhấn). Không ứng viên K/Q nào
    # chứa nó (lô b02 video 54: hook «BẢY NGÀY» chốt ở từ 1, mọi K bắt đầu từ từ 21) ⇒ bản đề xuất bỏ hook, nếu
    # không chính §8 trượt --check và agent PLAN phải tự gỡ (bỏ luôn cả điểm nhấn).
    if best_h is not None and best_h.get("hit_word") is not None:
        hit = best_h["hit_word"]
        if not any(c["range"][0] <= hit < c["range"][1] for c in chosen_emphasis):
            extra = next((c for c in rank_123 + rank_4
                          if c["range"][0] <= hit < c["range"][1] and can_add(c)), None)
            if extra is not None and len(chosen_emphasis) < max_emphasis:
                chosen_emphasis.append(extra)
                chosen_emphasis.sort(key=lambda x: x["onset"])
            else:
                best_h = None

    # Steps
    rec_s = next((s for s in cands.get("S", []) if s.get("recommended")), None)

    # CTA
    first_c = cands["C"][0] if cands.get("C") else None

    return {
        "hook": best_h["id"] if best_h else None,
        "emphasis": [c["id"] for c in chosen_emphasis],
        "steps": rec_s["id"] if rec_s else None,
        "steps_title": rec_s["title"] if rec_s else None,
        "cta": first_c["id"] if first_c else None,
        "cta_label": first_c["label"] if first_c else None,
        "cta_keyword": first_c["keyword"] if first_c else None,
        "hero": [],
        "breaks": [],
        "broll": [],
    }
