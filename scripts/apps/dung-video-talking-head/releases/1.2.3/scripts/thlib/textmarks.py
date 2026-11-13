"""thlib.textmarks — cấu trúc chữ của lời chuẩn (spec 1.1.1 §3.1; R57): dấu câu, mức ngắt, câu,
đoạn, ngoặc kép, danh sách — dựng lại từ `vo_script.txt` bằng đúng tokeniser của align, nên
`words.json` giữ nguyên hợp đồng; cộng chính sách hiển thị dấu câu duy nhất `shown()` (P6, D4)
và các helper đọc từ điển `data/text_vi.json` (§3.2; R55). Module thuần: không ghi gì.

Tách token (giống `align._display_words`): mỗi `\\S+` của NFC(script).strip(); token chỉ gồm dấu
câu cuối (vd "...", " ?", " ,") không thành từ (align bỏ nó) mà gắn vào `tail` của từ trước;
còn lại token = pre + core + post với pre = ngoặc mở đầu token, post = dấu câu/ngoặc đóng cuối
token. ("–" rời không phải dấu câu cuối nên align giữ nó làm một từ — ví dụ "–" của §3.1 không
áp dụng.) Bất biến: (pre + core + post).rstrip(",.!?…:;") == words[k]["w"] — lệch là ToolError.
Lệch có chủ đích so với §3.1:
- "gắn vào post": `tail` để riêng để `post` luôn là đuôi của chính token align; mọi chỗ đọc dấu
  (mức ngắt, đoạn phẩy, `shown`, và người gọi ngoài module) đọc `punct(m)` = post + tail; `shown`
  chỉ bỏ dấu chấm/lửng của tail khi post đã kết câu ("hình. ..." hiện "hình.", không "hình....").
- cuối block `shown` giữ ? ! và mọi ngoặc đóng thật (” » " ’ )) chứ không chỉ ”: ngoặc mở
  tương ứng đã hiện ở `pre`, bỏ ngoặc đóng sẽ để lại «(» lẻ.
- `find_lists`: xem docstring của `_list_in` (dự phòng khi không có từ đầu mục, chặn cắt giữa
  cụm từ, dừng ở mệnh đề có chủ ngữ).

Mức ngắt sau từ k (`lvl`): 0 không có; 1 dấu phẩy, ngoặc đóng, hoặc từ sau mở ngoặc; 2 `:` `;`;
3 `. ? ! …` hoặc `:` ngay trước ngoặc kép mở; 4 xuống đoạn, `...`/`…` có chủ đích
(align.designed_breaks) hoặc từ cuối. Chế độ chỉ-ASR (script None): 3 nếu khoảng ngắt theo sau
≥ sfx.section_pause_s, 1 nếu ≥ audio.pause_min_s, từ cuối 4; không có câu (mọi từ sent = 0,
`sentences` trả một khoảng cả bài — không kiểm/mã nào dựa trên câu đoán từ khoảng lặng) và không
có câu trích dẫn.
"""

from __future__ import annotations

import bisect
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from . import align, paths

TRAIL = align._TRAILING_PUNCT                 # ",.!?…:;" — align cắt đúng các dấu này
_QUOTE_OPEN = "“«\""
_QUOTE_CLOSE = "”»\""
_OPEN = _QUOTE_OPEN + "‘(["                  # ký tự mở được tách vào `pre`
_CLOSE = _QUOTE_CLOSE + "’)]"                # ký tự đóng được tách vào `post`
_BRACKETS = "[]"                              # placeholder [TIN MỚI] — không bao giờ hiện
_SENTENCE_END = ".?!…"
_CLAUSE = ":;"
_SHOW_AT_BLOCK_END = "?!" + _QUOTE_CLOSE + "’)"   # cuối block chỉ còn ? ! và ngoặc đóng thật
_CONNECTORS = ("và", "hoặc", "hay")          # nối mục cuối của danh sách (§3.1 find_lists)
# Cấu trúc, không phải ngưỡng chỉnh được (nên không là lá rules): danh sách liệt kê cần ≥ 3 mục —
# "A và B" chỉ là một cặp (PLAN-real lists_of `len(items) >= 3`).
_MIN_LIST_ITEMS = 3
_PLURAL = ("các", "những")                    # «các bác», «những người» — đứng trước đại từ chủ ngữ
NEGATION = ("không", "chưa", "đừng")         # §3.1 weight: phủ định mang nghĩa
_NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)*%?")


@dataclass(frozen=True)
class Mark:
    """Một từ hiển thị: ngoặc mở `pre`, chữ `core`, dấu cuối của chính token `post`, token dấu
    câu rời theo sau `tail` (hiện như post, trừ chấm/lửng thừa sau một post đã kết câu), mức
    ngắt sau từ `lvl`, mở/đóng ngoặc kép, chỉ số câu
    `sent`, chỉ số đoạn `para`, `low` = core viết thường.
    Người gọi đọc dấu sau từ bằng `punct(m)` (post + tail), không đọc `post` trần: «ảnh , video»
    và «không ?» có dấu nằm ở `tail` (§3.1 gộp nó vào post — xem docstring module)."""

    pre: str
    core: str
    post: str
    tail: str
    lvl: int
    q_open: bool
    q_close: bool
    sent: int
    para: int
    low: str


@dataclass(frozen=True)
class Marks:
    """Dấu của cả bài: từng từ, các câu trích dẫn [mở, đóng + 1), và cờ có vo_script."""

    words: tuple[Mark, ...]
    quotes: tuple[tuple[int, int], ...]
    from_script: bool

    def __len__(self) -> int:
        return len(self.words)


@dataclass(frozen=True)
class WordList:
    """Danh sách liệt kê trong một câu (P3): phần dẫn `lead`, các mục `items` [a, b)."""

    lead: tuple[int, int]
    items: tuple[tuple[int, int], ...]
    sent: int


@dataclass(frozen=True)
class Lexicon:
    """data/text_vi.json đã nạp: các danh sách đóng và cặp âm tiết không tách ("a b")."""

    leads: frozenset
    trails: frozenset
    function: frozenset
    pronouns: frozenset
    warn: frozenset
    quantity: frozenset
    units: frozenset
    cta_verbs: frozenset
    pairs: frozenset


# --- tách token -------------------------------------------------------------------------------


def _split(raw: str) -> tuple[str, str, str]:
    pre = raw[:len(raw) - len(raw.lstrip(_OPEN))]
    rest = raw[len(pre):]
    core = rest.rstrip(TRAIL + _CLOSE)
    return pre, core, rest[len(core):]


def _tokens(text: str) -> list[dict]:
    """Từ hiển thị của `text` (đã NFC + strip) với pre/core/post/tail, theo đúng align."""
    out: list[dict] = []
    for m in align._WORD_RE.finditer(text):
        raw = m.group()
        if not raw.rstrip(TRAIL):
            if out:
                out[-1]["tail"] += raw
            continue
        pre, core, post = _split(raw)
        out.append({"pre": pre, "core": core, "post": post, "tail": ""})
    return out


def punct(m) -> str:
    """Dấu câu sau chữ của một từ: đuôi token (`post`) + token dấu rời theo sau (`tail`).
    Mọi chỗ hỏi "sau từ này có dấu gì" (phẩy/hai chấm cuối đoạn, …) phải đọc qua hàm này."""
    return m.post + m.tail


def _level(tok: dict, nxt: dict | None, brk: str | None) -> int:
    punct = tok["post"] + tok["tail"]
    if nxt is None or brk is not None:
        return 4
    if any(c in _SENTENCE_END for c in punct) or (":" in punct and _opens_quote(nxt["pre"])):
        return 3
    if any(c in _CLAUSE for c in punct):
        return 2
    if "," in punct or any(c in _CLOSE for c in punct) or nxt["pre"]:
        return 1
    return 0


def _opens_quote(pre: str) -> bool:
    return any(c in _QUOTE_OPEN for c in pre)


def _closes_quote(post: str) -> bool:
    return any(c in _QUOTE_CLOSE for c in post)


def _freeze(toks: list[dict], lvls: list[int], paras: list[int], from_script: bool) -> Marks:
    words, quotes, open_k, sent = [], [], None, 0
    for k, (t, lvl, para) in enumerate(zip(toks, lvls, paras)):
        q_open, q_close = _opens_quote(t["pre"]), _closes_quote(t["post"])
        if q_open:
            open_k = k
        if q_close and open_k is not None:
            quotes.append((open_k, k + 1))
            open_k = None
        words.append(Mark(t["pre"], t["core"], t["post"], t["tail"], lvl, q_open, q_close, sent,
                          para, t["core"].lower()))
        if lvl >= 3 and from_script:      # chỉ-ASR: không có câu (§3.1)
            sent += 1
    return Marks(tuple(words), tuple(quotes), from_script)


def script_marks(script: str) -> Marks:
    """Dấu của một lời chuẩn (không cần words.json) — dùng cho corpus/từ điển và `analyse`."""
    text = unicodedata.normalize("NFC", script).strip()
    toks = _tokens(text)
    stub = [{"w": (t["pre"] + t["core"] + t["post"]).rstrip(TRAIL)} for t in toks]
    breaks = align.designed_breaks(text, stub)
    brk = {b["after_word"]: b["kind"] for b in breaks}
    # từ tập, không từ `brk`: xuống đoạn rồi "..." mở đoạn sau cùng rơi sau một từ
    para_after = {b["after_word"] for b in breaks if b["kind"] == "paragraph"}
    n = len(toks)
    lvls = [_level(t, toks[k + 1] if k + 1 < n else None, brk.get(k)) for k, t in enumerate(toks)]
    paras, para = [], 0
    for k in range(n):
        paras.append(para)
        para += k in para_after
    return _freeze(toks, lvls, paras, True)


def _pause_after(words: list[dict], pauses: dict, tol: float) -> dict[int, float]:
    """Khoảng ngắt theo sau từ k: khoảng [t0, t1] mà t1 là onset (±tol) của từ k + 1 — lấy từ
    đầu tiên khớp (onset S04 kẹp đơn điệu nên hai từ liền có thể cách nhau đúng tol)."""
    ons = [float(w.get("on", w["s"])) for w in words]
    out: dict[int, float] = {}
    for t0, t1 in pauses.get("pauses", []):
        j = bisect.bisect_left(ons, float(t1) - tol)
        if 0 < j < len(ons) and abs(ons[j] - float(t1)) <= tol:
            out[j - 1] = max(out.get(j - 1, 0.0), float(t1) - float(t0))
    return out


def _asr_marks(words: list[dict], pauses: dict, R) -> Marks:
    section, short = R.get("sfx.section_pause_s"), R.get("audio.pause_min_s")
    gaps = _pause_after(words, pauses, R.get("audio.onset_mono_gap_s"))
    n = len(words)
    lvls = []
    for k in range(n):
        g = gaps.get(k, 0.0)
        lvls.append(4 if k == n - 1 else 3 if g >= section else 1 if g >= short else 0)
    toks = [{"pre": "", "core": str(w["w"]), "post": "", "tail": ""} for w in words]
    return _freeze(toks, lvls, [0] * n, False)


def _tool_error(msg: str):
    from .build import ToolError          # muộn: build → picture → textmarks (tránh vòng import)
    return ToolError(msg)


def analyse(script: str | None, words: list[dict], pauses: dict, R) -> Marks:
    """Dấu của bài: từ vo_script nếu có (kiểm bất biến với words.json), không thì theo khoảng
    ngắt (chế độ chỉ-ASR)."""
    if script is None:
        return _asr_marks(words, pauses, R)
    marks = script_marks(script)
    if len(marks) != len(words):
        raise _tool_error(f"vo_script có {len(marks)} từ nhưng words.json có {len(words)} — "
                          "words.json không phải kết quả align của vo_script này")
    for k, (m, w) in enumerate(zip(marks.words, words)):
        if (m.pre + m.core + m.post).rstrip(TRAIL) != w["w"]:
            raise _tool_error(f"từ {k}: vo_script «{m.pre}{m.core}{m.post}» ≠ words.json "
                              f"«{w['w']}» — chạy lại INTAKE (align) trên đúng vo_script")
    return marks


def sentences(marks: Marks) -> tuple[tuple[int, int], ...]:
    """Các câu [a, b): cắt sau mỗi từ có mức ngắt ≥ 3. Chế độ chỉ-ASR không có câu: cả bài là
    một khoảng (mức 3 ở đó chỉ là khoảng lặng dài, không phải ranh giới câu)."""
    if not marks.from_script:
        return ((0, len(marks)),) if len(marks) else ()
    out, start = [], 0
    for k, m in enumerate(marks.words):
        if m.lvl >= 3 or k == len(marks) - 1:
            out.append((start, k + 1))
            start = k + 1
    return tuple(out)


# --- danh sách liệt kê ------------------------------------------------------------------------


def _segments(marks: Marks, a: int, b: int) -> list[tuple[int, int]]:
    segs, start = [], a
    for k in range(a, b):
        if k == b - 1 or any(c in ",:" for c in punct(marks.words[k])):
            segs.append((start, k + 1))
            start = k + 1
    return segs


def _connectors(marks: Marks, seg: tuple[int, int], first_ok: bool) -> list[int]:
    """Từ nối của đoạn phẩy, còn ít nhất một từ sau nó trong đoạn (từ cuối câu "… rất hay." là
    tính từ «hay», không nối mục nào); đứng đầu đoạn chỉ tính khi `first_ok` — đoạn cuối câu
    «…, và C» (mục cuối là cả đoạn)."""
    start = seg[0] if first_ok else seg[0] + 1
    return [k for k in range(start, seg[1] - 1) if marks.words[k].low in _CONNECTORS]


def _item_words(marks: Marks, r: tuple[int, int]) -> int:
    return r[1] - r[0] - (marks.words[r[0]].low in _CONNECTORS)


def _subject_led(marks: Marks, lex: Lexicon, r: tuple[int, int]) -> bool:
    """Mục mở bằng đại từ chủ ngữ (sau từ nối và các/những nếu có): một mệnh đề mới, không phải
    một mục liệt kê («các bác cần …», «tôi tạo …»)."""
    w = marks.words[r[0]:r[1]]
    i = int(w[0].low in _CONNECTORS)
    i += i + 1 < len(w) and w[i].low in _PLURAL
    return i < len(w) and not is_caps(w[i].core) and w[i].low in lex.pronouns


def _splits_unit(marks: Marks, lex: Lexicon, k: int) -> bool:
    """Cắt trước từ k (k ≥ 1) tách một cụm: cặp dính (`glued`) hoặc ngay sau từ dẫn không dấu."""
    return glued(marks, lex, k - 1) or (marks.words[k - 1].lvl == 0 and is_lead(marks, lex, k - 1))


def _list_in(marks: Marks, lex: Lexicon, segs: list, si: int, max_words: int,
             sent: int) -> WordList | None:
    """Danh sách kết thúc ở đoạn phẩy `si` (có từ nối; «…, và C» thì mục cuối là cả đoạn, dù
    trong đoạn còn từ nối khác). Lùi về các đoạn trước, mỗi đoạn một mục (không giới hạn số mục:
    mỗi mục đã bị chặn bởi `max_words`), tới đoạn kết bằng «:» (thành phần dẫn) hoặc đầu câu.
    Không có «:» dẫn thì danh sách không vượt qua mệnh đề có chủ ngữ (`_subject_led`): nó bắt
    đầu ở mục có chủ ngữ cuối cùng («…, các bác cần A và B» chỉ còn 2 mục → không phải danh
    sách; «…, tôi tạo A, B và C» → mục 1 cắt trong đoạn «tôi tạo A»).
    Mục 1 bắt đầu ở lần xuất hiện cuối của từ đầu của BẤT KỲ mục sau nào (PLAN-real lists_of,
    rộng hơn "item 2's head" của §3.1; v16 cho cùng kết quả). Lệch/thêm so với §3.1:
    - không có từ đầu nào: đoán lùi từ cuối đoạn một độ dài = trung vị độ dài các mục sau, và
      chỉ nhận khi còn phần dẫn trong đoạn — mục 1 trùm cả đoạn thì không có bằng chứng nó là
      mục («Lỗi hai, chữ hoặc logo…», «Ngày thứ ba, thêm A và B» là cụm đề/trạng ngữ đầu câu);
    - chỗ cắt không bao giờ tách một cụm (`_splits_unit`) và mục 1 không mở bằng từ nối: lùi về
      đầu cụm («Nó có hình|ảnh» → «hình ảnh»; «chủ thể|và mục tiêu» → «chủ thể và mục tiêu»);
      mục 1 khi đó quá `max_words` thì bỏ cả danh sách."""
    low = [m.low for m in marks.words]
    s0, s1 = segs[si]
    cs = _connectors(marks, segs[si], si == len(segs) - 1)
    items = [(s0, s1)] if cs[0] == s0 else [(s0, cs[-1]), (cs[-1], s1)]
    j = si - 1
    while j >= 0 and ":" not in punct(marks.words[segs[j][1] - 1]):
        items.insert(0, segs[j])
        j -= 1
    colon_lead = segs[j] if j >= 0 else None
    subj = [i for i, r in enumerate(items) if _subject_led(marks, lex, r)]
    if subj and colon_lead is None:
        items = items[subj[-1]:]
    if len(items) < _MIN_LIST_ITEMS:
        return None
    heads = {low[r[0] + (low[r[0]] in _CONNECTORS)] for r in items[1:]}
    f0, f1 = items[0]
    cut = next((k for k in range(f1 - 1, f0 - 1, -1) if low[k] in heads), None)
    guessed = cut is None and colon_lead is None
    if colon_lead:
        cut = f0
    elif cut is None:
        cut = max(f0, f1 - sorted(r[1] - r[0] for r in items[1:])[(len(items) - 2) // 2])
    while cut > f0 and (low[cut] in _CONNECTORS or _splits_unit(marks, lex, cut)):
        cut -= 1
    items[0] = (cut, f1)
    if (guessed and cut == f0) or any(_item_words(marks, r) > max_words for r in items):
        return None
    return WordList(colon_lead or (f0, cut), tuple(items), sent)


def find_lists(marks: Marks, max_words: int, lex: Lexicon) -> tuple[WordList, ...]:
    """Danh sách trong từng câu: các đoạn phẩy mà mục cuối mở bằng và/hoặc/hay, mỗi mục
    ≤ `max_words` từ (không tính từ nối) — `max_words` = rules plan.list_item_max_words; `lex`
    (bắt buộc: không có nó thì không biết cụm nào không được cắt) = `load_lexicon(R)`."""
    out = []
    for a, b in sentences(marks):
        segs = _segments(marks, a, b)
        for si in range(len(segs) - 1, 0, -1):
            if _connectors(marks, segs[si], si == len(segs) - 1):
                found = _list_in(marks, lex, segs, si, max_words, marks.words[a].sent)
                if found:
                    out.append(found)
                break
    return tuple(out)


# --- chính sách hiển thị (P6, D4) -------------------------------------------------------------


def shown(marks: Marks, block_range, k: int, style: str, display: str | None = None) -> str:
    """Chữ hiện của từ k trong block [a, b): `display` (nếu có) hoặc core, gắn lại dấu theo đúng
    một chính sách — trong block giữ , ; : ? ! (cả ở cuối dòng trong) và . … của câu kết thúc
    trong block; cuối block chỉ còn ? ! và ngoặc đóng thật; ngoặc kép đúng chỗ kịch bản có;
    `style` "quote" (hero trích dẫn — Subtitle.tsx tự thêm “ ”) bỏ ngoặc kép của chính nó;
    [ ] không bao giờ hiện. Gọi với style của block cho từ hero, "script" cho dòng trên/dưới."""
    m = marks.words[k]
    drop = _BRACKETS + (_QUOTE_OPEN + _QUOTE_CLOSE if style == "quote" else "")
    ended = any(c in _SENTENCE_END for c in m.post)
    post = m.post + (_strip(m.tail, ".…") if ended else m.tail)   # "hình. ..." → "hình."
    if k == block_range[1] - 1:
        post = "".join(c for c in post if c in _SHOW_AT_BLOCK_END)
    base = m.core if display is None else display
    return _strip(m.pre, drop) + base + _strip(post, drop)


def _strip(s: str, chars: str) -> str:
    return "".join(c for c in s if c not in chars)


# --- từ điển (data/text_vi.json) --------------------------------------------------------------


def read_lexicon(path) -> Lexicon:
    """Nạp text_vi.json ở `path`."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return Lexicon(**{f: frozenset(raw[f]) for f in Lexicon.__dataclass_fields__})


def load_lexicon(R) -> Lexicon:
    """Từ điển của bản luật R: releases/<ver>/<plan.lexicon>."""
    return read_lexicon(paths.release_dir(R.version) / R.get("plan.lexicon"))


def is_number(core: str) -> bool:
    return bool(_NUMBER_RE.fullmatch(core))


def is_caps(core: str) -> bool:
    """Từ viết HOA toàn bộ, ≥ 2 chữ cái (UGC, THOẠI, AI; không tính «Ở» đầu câu)."""
    return core.isupper() and sum(ch.isalpha() for ch in core) >= 2


def _run_token(core: str) -> bool:
    return is_caps(core) or is_number(core)


def glued(marks: Marks, lex: Lexicon, k: int) -> bool:
    """Ranh giới sau từ k không có dấu và cặp "low[k] low[k+1]" thuộc `pairs`, hoặc hai từ cùng
    nằm trong một chuỗi ≥ 2 từ HOA/số (5 TÀI SẢN, UGC THOẠI)."""
    if k + 1 >= len(marks) or marks.words[k].lvl:
        return False
    a, b = marks.words[k], marks.words[k + 1]
    return f"{a.low} {b.low}" in lex.pairs or (_run_token(a.core) and _run_token(b.core))


def is_lead(marks: Marks, lex: Lexicon, k: int) -> bool:
    """Từ dẫn (gắn với từ sau): không kết dòng/block trên nó khi không có dấu."""
    return marks.words[k].low in lex.leads


def is_trail(marks: Marks, lex: Lexicon, k: int) -> bool:
    """Từ đuôi (gắn với từ trước): không mở dòng/block bằng nó khi không có dấu."""
    return marks.words[k].low in lex.trails


def is_function(marks: Marks, lex: Lexicon, k: int) -> bool:
    """Hư từ — trừ từ HOA ("AI" là nội dung; "ai" = who là hư từ)."""
    m = marks.words[k]
    return not is_caps(m.core) and m.low in lex.function


def weight(marks: Marks, lex: Lexicon, k: int, W) -> float:
    """Trọng số nội dung của từ k cho chọn hero; `W` = rules plan.hero (content, keyword,
    negation, function): số và từ HOA ≥ 2 chữ = keyword ("AI" = content), không/chưa/đừng =
    negation, hư từ = function, còn lại content."""
    m = marks.words[k]
    if m.core == "AI":
        return W["content"]
    if is_number(m.core) or is_caps(m.core):
        return W["keyword"]
    if m.low in NEGATION:
        return W["negation"]
    return W["function"] if is_function(marks, lex, k) else W["content"]
