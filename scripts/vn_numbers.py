"""Đọc số thành chữ tiếng Việt để khớp cụm từ giữa kịch bản và lời Whisper.

Whisper hay ghi số bằng chữ số ("90", "50.000", "20tr", "90%"), kịch bản / HeyGen ghi bằng chữ ("chín mươi").
Đưa cả hai phía về chữ rồi mới so khớp:

    from vn_numbers import expand_tokens
    expand_tokens(["giảm", "90%", "chi", "phí"])  # ['giảm', 'chín', 'mươi', 'phần', 'trăm', 'chi', 'phí']
"""
from __future__ import annotations

import re

DIGITS = "không một hai ba bốn năm sáu bảy tám chín".split()
UNITS = [(10 ** 9, "tỷ"), (10 ** 6, "triệu"), (10 ** 3, "nghìn")]
SUFFIX = {"%": ["phần", "trăm"], "k": ["nghìn"], "tr": ["triệu"], "triệu": ["triệu"], "ty": ["tỷ"], "tỷ": ["tỷ"], "x": ["lần"]}
# biến thể đọc số → một dạng chuẩn (cả hai phía đều qua đây)
VARIANT = {"ngàn": "nghìn", "linh": "lẻ", "tỉ": "tỷ"}
NUM_RX = re.compile(r"^(\d{1,3}(?:[.,]\d{3})+|\d+(?:[.,]\d+)?)(%|k|tr|triệu|ty|tỷ|x)?$", re.I)


def _under_1000(n: int, full: bool) -> list[str]:
    """0..999; full=True khi đứng sau một hàng lớn hơn (đọc đủ 'không trăm', 'lẻ')."""
    h, t, u = n // 100, (n // 10) % 10, n % 10
    out: list[str] = []
    if h or full:
        out += [DIGITS[h], "trăm"]
    if t == 0:
        if u and (h or full):
            out.append("lẻ")
        if u:
            out.append(DIGITS[u])
        return out
    out += ["mười"] if t == 1 else [DIGITS[t], "mươi"]
    if u == 1:
        out.append("một" if t == 1 else "mốt")
    elif u == 5:
        out.append("lăm")
    elif u:
        out.append(DIGITS[u])
    return out


def read_int(n: int) -> list[str]:
    if n == 0:
        return ["không"]
    out: list[str] = []
    started = False
    for size, name in UNITS:
        q, n = divmod(n, size)
        if q:
            out += read_int(q) if q >= 1000 else _under_1000(q, started)
            out.append(name)
            started = True
    if n:
        out += _under_1000(n, started)
    return out


def read_number(tok: str) -> list[str] | None:
    """'90%' → ['chín','mươi','phần','trăm']; '50.000' → ['năm','mươi','nghìn']; không phải số → None."""
    m = NUM_RX.match(tok.strip())
    if not m:
        return None
    body, suf = m.group(1), (m.group(2) or "").lower()
    if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", body):             # 50.000 / 1,000,000 = phân cách hàng nghìn
        words = read_int(int(re.sub(r"[.,]", "", body)))
    elif re.search(r"[.,]", body):                                # 1,5 / 2.5 = số thập phân
        a, b = re.split(r"[.,]", body)
        words = read_int(int(a)) + ["phẩy"] + [DIGITS[int(c)] for c in b]
    else:
        words = read_int(int(body))
    return words + SUFFIX.get(suf, [])


def expand_tokens(tokens: list[str]) -> list[str]:
    """Mỗi token số → các từ đọc số; mọi token qua chuẩn hoá biến thể (ngàn → nghìn …)."""
    out: list[str] = []
    for t in tokens:
        out += read_number(t) or [t]
    return [VARIANT.get(t, t) for t in out]
