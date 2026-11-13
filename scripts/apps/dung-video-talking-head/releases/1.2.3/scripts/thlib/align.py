"""thlib.align — căn lời chuẩn (vo_script) với mốc từ whisper (spec §6.2) và
map nhịp ngắt có chủ đích (`...`/`…`, xuống đoạn) sang index từ hiển thị (§6.3).

Chữ hiển thị = chữ trong vo_script; whisper chỉ cho thời gian. So khớp trên
token đã chuẩn hoá (`textnorm.norm_tokens`), mỗi token mang danh sách chỉ số
từ nguồn (đếm theo `text.split()`) nên map ngược về từ hiển thị chính xác, kể
cả khi nhiều từ số được gộp thành một token ("hai mươi" -> "20").
"""

from __future__ import annotations

import bisect
import difflib
import re
import unicodedata

from . import textnorm

_TRAILING_PUNCT = ",.!?…:;"
_WORD_RE = re.compile(r"\S+")
_PARAGRAPH_RE = re.compile(r"\n\s*\n")
_ELLIPSIS_RE = re.compile(r"\.{3,}|…+")


def _display_words(text: str) -> list[tuple[int, str, int]]:
    """(chỉ số từ nguồn, chữ hiển thị, vị trí ký tự đầu) của từng từ hiển thị:
    từ cách nhau bởi khoảng trắng, cắt dấu câu cuối; từ rỗng sau khi cắt (vd
    token "...") bị bỏ nhưng vẫn chiếm một chỉ số nguồn như trong norm_tokens."""
    out = []
    for src_i, m in enumerate(_WORD_RE.finditer(text)):
        shown = m.group().rstrip(_TRAILING_PUNCT)
        if shown:
            out.append((src_i, shown, m.start()))
    return out


def _whisper_tokens(whisper_words: list[dict]) -> tuple[list[str], list[tuple[float, float]]]:
    """Token chuẩn hoá của lời whisper và khoảng (s, e) của từng token — token
    gộp nhiều từ whisper lấy từ s đầu tới e cuối."""
    parts: list[str] = []
    owner: list[int] = []
    for k, w in enumerate(whisper_words):
        for part in str(w["w"]).split():
            parts.append(part)
            owner.append(k)
    tokens = textnorm.norm_tokens(" ".join(parts))
    spans = []
    for _, idx in tokens:
        ks = [owner[p] for p in idx]
        spans.append((
            min(float(whisper_words[k]["s"]) for k in ks),
            max(float(whisper_words[k]["e"]) for k in ks),
        ))
    return [tok for tok, _ in tokens], spans


def _split_span(s: float, e: float, n: int) -> list[tuple[float, float]]:
    """Chia đều [s, e] cho n từ (n = 1 giữ nguyên s, e)."""
    edges = [s + (e - s) * k / n for k in range(n + 1)]
    edges[0], edges[-1] = s, e
    return list(zip(edges[:-1], edges[1:]))


def _fill_unmatched(times: list, first_s: float, last_e: float) -> list[tuple[float, float]]:
    """Nội suy tuyến tính các từ chưa có mốc giữa e của từ khớp trước và s của
    từ khớp sau; đầu/cuối bài thì dùng s đầu / e cuối của whisper. Mép trái
    kẹp ≤ mép phải để s luôn không giảm khi whisper chồng mốc."""
    out = list(times)
    n = len(out)
    k = 0
    while k < n:
        if out[k] is not None:
            k += 1
            continue
        j = k
        while j < n and out[j] is None:
            j += 1
        prev_e = out[k - 1][1] if k > 0 else first_s
        next_s = out[j][0] if j < n else max(last_e, prev_e)
        left = min(prev_e, next_s)
        out[k:j] = _split_span(left, next_s, j - k)
        k = j
    return out


def align(script_text: str, whisper_words: list[dict]) -> dict:
    """Căn vo_script với từ whisper. Trả về {"words": [{i, w, s, e, src,
    guess}], "score", "guess_count"}: từ khớp nhận mốc whisper (token số gộp
    chia đều khoảng cho các từ nguồn), từ không khớp được nội suy và vẫn
    `guess=False` (script là chuẩn; guess dành cho chế độ chỉ-ASR). `on`
    (onset thật S04) do voice.correct_onsets bổ sung sau."""
    text = unicodedata.normalize("NFC", script_text)
    disp = _display_words(text)
    pos = {src_i: k for k, (src_i, _, _) in enumerate(disp)}
    s_tokens = textnorm.norm_tokens(text)
    w_tokens, w_spans = _whisper_tokens(whisper_words)

    sm = difflib.SequenceMatcher(a=[tok for tok, _ in s_tokens], b=w_tokens, autojunk=False)
    times: list = [None] * len(disp)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            continue
        for i, j in zip(range(i1, i2), range(j1, j2)):
            src = s_tokens[i][1]
            for src_i, span in zip(src, _split_span(*w_spans[j], len(src))):
                times[pos[src_i]] = span

    first_s = min((s for s, _ in w_spans), default=0.0)
    last_e = max((e for _, e in w_spans), default=first_s)
    times = _fill_unmatched(times, first_s, last_e)
    words = [
        {"i": k, "w": shown, "s": s, "e": e, "src": "script", "guess": False}
        for k, ((_, shown, _), (s, e)) in enumerate(zip(disp, times))
    ]
    return {
        "words": words,
        "score": sm.ratio(),
        "guess_count": sum(1 for w in words if w["guess"]),
    }


def designed_breaks(script_text: str, words: list[dict]) -> list[dict]:
    """Nhịp ngắt có chủ đích (§6.3): mỗi ranh giới đoạn (dòng trống) và mỗi
    `...`/`…` -> {"after_word": index từ hiển thị cuối cùng đứng trước nó,
    "kind": "paragraph"|"ellipsis"}, theo thứ tự trong văn bản. `words` phải
    là từ hiển thị của chính `script_text` (kết quả align)."""
    text = unicodedata.normalize("NFC", script_text).strip()
    disp = _display_words(text)
    if [shown for _, shown, _ in disp] != [w["w"] for w in words]:
        raise ValueError(
            f"words ({len(words)} từ) không phải từ hiển thị của vo_script này "
            f"({len(disp)} từ) — hãy chạy align trên đúng vo_script"
        )
    starts = [start for _, _, start in disp]
    found = []
    for kind, pattern in (("ellipsis", _ELLIPSIS_RE), ("paragraph", _PARAGRAPH_RE)):
        for m in pattern.finditer(text):
            k = bisect.bisect_left(starts, m.start()) - 1
            if k >= 0:
                found.append((m.start(), k, kind))
    return [{"after_word": k, "kind": kind} for _, k, kind in sorted(found)]
