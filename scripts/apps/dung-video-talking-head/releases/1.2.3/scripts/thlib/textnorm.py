"""thlib.textnorm — chuẩn hoá văn bản tiếng Việt để so khớp script/whisper
(spec §6.2): NFC, chữ thường, bỏ dấu câu (trừ `%`), số tiếng Việt -> chữ số,
`phần trăm`/`90 %` -> `90%`.
"""

from __future__ import annotations

import difflib
import re
import unicodedata

# Số đơn vị 0-9 (spec §6.2): nhiều cách đọc cùng một chữ số.
_UNIT_DIGITS: dict[str, int] = {
    "không": 0,
    "một": 1,
    "mốt": 1,
    "hai": 2,
    "ba": 3,
    "bốn": 4,
    "tư": 4,
    "năm": 5,
    "lăm": 5,
    "nhăm": 5,
    "sáu": 6,
    "bảy": 7,
    "tám": 8,
    "chín": 9,
}
_THOUSAND_WORDS = {"nghìn", "ngàn"}
_HUNDRED_WORDS = {"trăm"}
_ZERO_FILLER_WORDS = {"linh", "lẻ"}  # chục = 0, ví dụ "một trăm linh năm" = 105

# Từ vựng số dùng để dò đoạn liên tiếp (maximal run) cần gộp thành một token số.
_NUMBER_VOCAB = (
    set(_UNIT_DIGITS)
    | {"mười", "mươi"}
    | _HUNDRED_WORDS
    | _THOUSAND_WORDS
    | _ZERO_FILLER_WORDS
)

# "tư", "lẻ", "linh" cũng là từ tiếng Việt thông thường (đầu tư, tư duy,
# riêng lẻ, linh hồn...) không mang nghĩa số trong đa số câu. Chỉ coi chúng
# là số khi chúng NỐI TIẾP một từ số khác đã mở đoạn (vd "hai mươi tư"=24,
# "một trăm linh năm"=105) — không cho chúng tự mở một đoạn số mới.
_AMBIGUOUS_NUMBER_WORDS = {"tư", "lẻ", "linh"}
_NUMBER_VOCAB_START = _NUMBER_VOCAB - _AMBIGUOUS_NUMBER_WORDS

_STRIP_RE = re.compile(r"[^\w%]+", re.UNICODE)
_DIGITS_RE = re.compile(r"^\d+$")


def _clean_word(word: str) -> str:
    """Chữ thường, bỏ toàn bộ dấu câu, chỉ giữ chữ/số/`%`."""
    return _STRIP_RE.sub("", word.lower())


def _parse_number_words(words: list[str]) -> tuple[int, int]:
    """Đổi phần ĐẦU của `words` khớp ngữ pháp số tiếng Việt thành số nguyên:
    [<đơn vị> nghìn/ngàn] [<đơn vị> trăm [linh/lẻ <đơn vị>]]
    [mười <đơn vị>? | <đơn vị> mươi <đơn vị>? | <đơn vị>].
    Trả về `(giá trị, số từ đã dùng)` — người gọi phải tự lặp lại trên phần
    còn dư của run (nếu có) thay vì coi cả run là một số duy nhất, để không
    gán nhầm chỉ số của phần dư (vd một enumerator câu sau) vào token đã ghép."""
    i, n = 0, len(words)
    total = 0

    if i + 1 < n and words[i] in _UNIT_DIGITS and words[i + 1] in _THOUSAND_WORDS:
        total += _UNIT_DIGITS[words[i]] * 1000
        i += 2

    if i + 1 < n and words[i] in _UNIT_DIGITS and words[i + 1] in _HUNDRED_WORDS:
        total += _UNIT_DIGITS[words[i]] * 100
        i += 2
        if i + 1 < n and words[i] in _ZERO_FILLER_WORDS and words[i + 1] in _UNIT_DIGITS:
            return total + _UNIT_DIGITS[words[i + 1]], i + 2

    if i < n and words[i] == "mười":
        total += 10
        i += 1
        if i < n and words[i] in _UNIT_DIGITS:
            total += _UNIT_DIGITS[words[i]]
            i += 1
    elif i + 1 < n and words[i] in _UNIT_DIGITS and words[i + 1] == "mươi":
        total += _UNIT_DIGITS[words[i]] * 10
        i += 2
        if i < n and words[i] in _UNIT_DIGITS:
            total += _UNIT_DIGITS[words[i]]
            i += 1
    elif i < n and words[i] in _UNIT_DIGITS:
        total += _UNIT_DIGITS[words[i]]
        i += 1

    return total, i


def _merge_percent_pair(tokens: list[tuple[str, list[int]]]) -> list[tuple[str, list[int]]]:
    """Gộp cặp từ liền nhau "phần" "trăm" thành một token ký hiệu "%"."""
    out: list[tuple[str, list[int]]] = []
    i = 0
    while i < len(tokens):
        w, idx = tokens[i]
        if w == "phần" and i + 1 < len(tokens) and tokens[i + 1][0] == "trăm":
            out.append(("%", idx + tokens[i + 1][1]))
            i += 2
        else:
            out.append((w, idx))
            i += 1
    return out


def _merge_number_words(tokens: list[tuple[str, list[int]]]) -> list[tuple[str, list[int]]]:
    """Gộp mỗi đoạn liên tiếp thuộc từ vựng số thành (một hoặc nhiều) token
    chữ số. Một đoạn (run) chỉ được MỞ bằng một từ số không mơ hồ
    (`_NUMBER_VOCAB_START`); "tư"/"lẻ"/"linh" chỉ được coi là số khi nối
    tiếp một đoạn đã mở, để không biến các từ tiếng Việt thường (đầu tư,
    tư duy, riêng lẻ...) thành chữ số. Trong một đoạn, `_parse_number_words`
    có thể chỉ dùng hết một PHẦN — phần dư (vd một câu mới bắt đầu bằng số
    thứ tự ngay sau từ số kết câu trước) được lặp lại xử lý tiếp thay vì bị
    gộp nhầm vào token đầu."""
    out: list[tuple[str, list[int]]] = []
    i = 0
    while i < len(tokens):
        if tokens[i][0] in _NUMBER_VOCAB_START:
            j = i
            while j < len(tokens) and tokens[j][0] in _NUMBER_VOCAB:
                j += 1
            run = tokens[i:j]
            p = 0
            while p < len(run):
                value, consumed = _parse_number_words([w for w, _ in run[p:]])
                if consumed == 0:
                    out.append(run[p])
                    p += 1
                else:
                    chunk = run[p : p + consumed]
                    merged_idx = [k for _, idx in chunk for k in idx]
                    out.append((str(value), merged_idx))
                    p += consumed
            i = j
        else:
            out.append(tokens[i])
            i += 1
    return out


def _attach_percent(tokens: list[tuple[str, list[int]]]) -> list[tuple[str, list[int]]]:
    """Gộp `<số> %` liền nhau thành một token `<số>%`."""
    out: list[tuple[str, list[int]]] = []
    i = 0
    while i < len(tokens):
        w, idx = tokens[i]
        if _DIGITS_RE.match(w) and i + 1 < len(tokens) and tokens[i + 1][0] == "%":
            out.append((w + "%", idx + tokens[i + 1][1]))
            i += 2
        else:
            out.append((w, idx))
            i += 1
    return out


def norm_tokens(text: str) -> list[tuple[str, list[int]]]:
    """Chuẩn hoá `text` thành danh sách (token, [chỉ số từ nguồn]) theo spec
    §6.2. Chỉ số từ nguồn là vị trí (đếm từ 0) của các từ cách nhau bởi
    khoảng trắng trong `text` gốc mà token đó gộp lại."""
    words = unicodedata.normalize("NFC", text).split()
    cleaned = [(_clean_word(w), [i]) for i, w in enumerate(words)]
    cleaned = [(w, idx) for w, idx in cleaned if w]

    cleaned = _merge_percent_pair(cleaned)
    cleaned = _merge_number_words(cleaned)
    cleaned = _attach_percent(cleaned)
    return cleaned


def norm(text: str) -> list[str]:
    """Chỉ lấy phần chữ của norm_tokens (bỏ chỉ số từ nguồn)."""
    return [tok for tok, _ in norm_tokens(text)]


def similarity(a_tokens: list[str], b_tokens: list[str]) -> float:
    """Độ khớp difflib giữa hai danh sách token đã chuẩn hoá (autojunk=False)."""
    return difflib.SequenceMatcher(a=a_tokens, b=b_tokens, autojunk=False).ratio()
