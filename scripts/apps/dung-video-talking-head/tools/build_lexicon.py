# -*- coding: utf-8 -*-
"""build_lexicon.py — dựng từ điển tiếng Việt vendored của release (spec 1.1.1 §3.2; Ruling R55):
`releases/1.1.1/data/text_vi.json` = các danh sách đóng (leads, trails, function, pronouns, warn,
quantity, units, cta_verbs) + các cặp âm tiết không được tách ("a b", nhãn K).

Quy trình (công cụ dev — Python hệ thống hoặc venv, không chạy lúc dựng video):
1. `extract` ghi tools/lexicon/pairs_review.tsv: mọi cặp từ liền nhau KHÔNG có dấu câu/ngoặc ở giữa
   trong 60 mục VIDEO SCRIPT (thlib.scripts_v3; tách token bằng thlib.textmarks = đúng tokeniser
   của align; bỏ mọi từ trong placeholder [IN HOA]), mỗi dòng: số lần, PMI nếu ≥ 4 (chỉ gợi ý cho
   người duyệt), 3 ngữ cảnh ±3 từ, nhãn lượt A, lượt B và nhãn cuối (đọc từ pass_a/pass_b/
   adjudicated.tsv). Cùng lúc ghi syllables_review.tsv: mọi âm tiết với lớp LEAD/TRAIL/FN/C theo
   các danh sách đóng bên dưới (bảng duyệt âm tiết).
2. Hai phiên Claude dev gán nhãn độc lập (pass_a.tsv, pass_b.tsv; cột pair, label) với cùng một
   lời dặn: "K nếu trong đa số ngữ cảnh hai âm tiết là một từ, tên riêng hay cụm cố định; phân vân
   → K"; S = tách được. `--diff` liệt kê bất đồng; lượt ba phân xử từng dòng vào adjudicated.tsv
   (pair, count, label_a, label_b, label, reason — reason bắt buộc khi A ≠ B).
3. `--emit` ghi text_vi.json: pairs = mọi dòng K của adjudicated.tsv; danh sách đóng lấy từ đây.
4. `--delta <vo_script>` liệt kê các cặp của một lời mới/đã điền (vd mục 31–38 có placeholder)
   chưa có trong adjudicated.tsv — cần duyệt rồi thêm vào hai lượt + phân xử.

Cặp thiếu trong từ điển = tách được (fail-open). Không ship bảng PMI/cohesion (R55).

Đối chiếu với bằng chứng (lexicon111/, 4.563 cặp): bản trích này ra 4.562 cặp và 830 âm tiết. Lệch
đúng một cặp, «hợp đơn» (S), từ bên trong placeholder [TRƯỜNG HỢP ĐƠN GIẢN] (mục 31 của file v3) — bản bằng
chứng chỉ bỏ các token chứa ngoặc, bản này bỏ cả placeholder. Dòng đó được giữ trong
adjudicated.tsv (vô hại vì là S; `--diff` in nó ở "dòng adjudicated ngoài corpus", test_lexicon
ghim tập dòng ngoài corpus). Không lọc pairs theo corpus vì bước 4 (`--delta`) cố ý thêm cặp của lời
mới, vốn nằm ngoài corpus. Con số "khoảng 4.605 cặp / 831 âm tiết" của spec §3.2 là ước lượng từ bản
nháp trước; âm tiết duy nhất chỉ xuất hiện trong placeholder là «nghề».

Dùng: PYTHONIOENCODING=utf-8 python tools/build_lexicon.py extract|--diff|--emit [--v3 FILE]
      PYTHONIOENCODING=utf-8 python tools/build_lexicon.py --delta <vo_script.txt>
(tools/ — Hermes không liệt kê thư mục này cho worker; Ruling R36)
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
import unicodedata
from collections import Counter
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
DEFAULT_VERSION = "1.1.1"
_SCRIPTS = SKILL / "releases" / DEFAULT_VERSION / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from thlib import paths, scripts_v3, textmarks  # noqa: E402

LEXDIR = SKILL / "tools" / "lexicon"
OUT_JSON = SKILL / "releases" / DEFAULT_VERSION / "data" / "text_vi.json"
SECTIONS = "VIDEO SCRIPT"
PMI_HINT = 4.0          # spec §3.2: cột gợi ý PMI ≥ 4
N_CONTEXTS = 3          # spec §3.2: 3 ngữ cảnh ±3 từ
CONTEXT_WORDS = 3

# --- danh sách đóng (spec §3.2; giữ bảo thủ — mỗi từ thêm có nguồn) -------------------------------
# leads — gắn với từ sau (không kết dòng/block trên nó khi không có dấu): định từ, lượng từ, giới từ,
# liên từ, trợ từ trước động từ, số từ.
#   seed: design111/judge_blocking/canary_rules.py LEADS (thiết kế blocking, "seed is blocking's list")
_LEADS_SEED = ("các những một mỗi mọi cái chiếc cả tất của cho với trong vào từ đến tới về theo bằng ở "
               "tại qua như giữa và hoặc hay nhưng mà thì nếu vì nên để khi là rằng do bởi đã đang sẽ "
               "vẫn cũng chỉ rất hãy đừng chưa không bị")
#   số từ: design111/minimal/pmin.py LEADS (spec §3.2 "numerals")
_NUMERALS = "hai ba bốn năm sáu bảy tám chín mười"
#   duyệt âm tiết (syllables_review.tsv, 2026-09-15): giới từ trên/sau/trước (sau khi, trước khi,
#   trên nền), lượng từ vài/từng (vài phút, từng bước; "tôi từng mất"), phó từ mức độ trước tính từ
#   càng/khá (càng dễ, khá tốt — «quá» không thêm vì hay đứng sau: "đẹp quá").
_LEADS_REVIEW = "trên sau trước vài từng càng khá"
# trails — gắn với từ trước (không mở dòng/block bằng nó): nguyên văn spec §3.2.
_TRAILS = "nhé nha ạ thôi đâu nữa hơn nhất lắm"
# pronouns — design111/minimal/pmin.py FUNC dòng 1 ("ai" thường = who; "AI" viết hoa là nội dung).
_PRONOUNS = "tôi bạn mình nó họ ta chúng bác anh chị em ai"
# chỉ định từ — pmin.py FUNC dòng 2 (spec §3.2 "demonstratives"; chỉ vào function, không thành list riêng)
_DEMONSTRATIVES = "này đó kia ấy nào đây"
# function = leads ∪ trails ∪ pronouns ∪ demonstratives ∪ bộ này (nguyên văn spec §3.2)
_FUNCTION_EXTRA = "có được là thế vậy gì sao rồi còn lại ra lên xuống phải thường luôn mới"
# warn — design111/accents.py WARNW (hero màu cảnh báo; «brochure» theo đúng seed)
_WARN = "không đừng sai giả lỗi mất tốn chưa khó xấu dở brochure"
# quantity — design111/accents.py NUMW
_QUANTITY = "vài nhiều mười trăm nghìn"
# units — design111/cands.py UNITS + duyệt âm tiết: bài, độ (đứng ngay sau một số trong corpus)
_UNITS = "lần giây phút ngày bước lỗi cách tầng góc thứ ảnh video câu phần dòng tài bài độ"
# cta_verbs — design111/cands.py CTA_VERBS (động từ trước từ khoá HOA của CTA)
_CTA_VERBS = ("bình luận", "comment", "nhắn", "hashtag", "gõ")


def _norm(s: str) -> str:
    return unicodedata.normalize("NFC", s).strip().lower()


def _words(s: str) -> set[str]:
    return {_norm(w) for w in s.split()}


def closed_lists() -> dict[str, list[str]]:
    """Các danh sách đóng của text_vi.json — NFC, chữ thường, sắp xếp, không trùng."""
    leads = _words(_LEADS_SEED) | _words(_NUMERALS) | _words(_LEADS_REVIEW)
    trails, pronouns = _words(_TRAILS), _words(_PRONOUNS)
    function = leads | trails | pronouns | _words(_DEMONSTRATIVES) | _words(_FUNCTION_EXTRA)
    lists = {"leads": leads, "trails": trails, "function": function, "pronouns": pronouns,
             "warn": _words(_WARN), "quantity": _words(_QUANTITY), "units": _words(_UNITS),
             "cta_verbs": {_norm(v) for v in _CTA_VERBS}}
    return {k: sorted(v) for k, v in lists.items()}


# --- corpus -----------------------------------------------------------------------------------


def load_sections(v3: str | None) -> dict[int, dict]:
    path = Path(v3) if v3 else scripts_v3.find_v3_file(paths.DOCS_ROOT)
    return scripts_v3.load_v3(path)


def corpus_sha(sections: dict[int, dict]) -> str:
    """sha256 của 60 mục VIDEO SCRIPT: "## NN\\n<script NFC>\\n" nối theo số mục."""
    text = "".join(f"## {n:02d}\n{unicodedata.normalize('NFC', sections[n]['script'])}\n"
                   for n in sorted(sections))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _placeholder(marks) -> list[bool]:
    """Từ nằm trong một placeholder [IN HOA] (từ '[' tới ']')."""
    out, inside = [], False
    for m in marks.words:
        inside = inside or "[" in m.pre
        out.append(inside)
        if "]" in m.post:
            inside = False
    return out


def _token(m) -> str:
    return m.pre + m.core + m.post + (" " + m.tail if m.tail else "")


def _context(marks, a: int, b: int, label: str) -> str:
    lo, hi = max(0, a - CONTEXT_WORDS), min(len(marks), b + CONTEXT_WORDS)
    return f"{label}: " + " ".join(_token(m) for m in marks.words[lo:hi])


def _scan(text: str):
    """(marks, cặp) của một lời: cặp = (k, "low[k] low[k+1]") với ranh giới không dấu, ngoài
    placeholder."""
    marks = textmarks.script_marks(text)
    ph = _placeholder(marks)
    pairs = [(k, f"{marks.words[k].low} {marks.words[k + 1].low}") for k in range(len(marks) - 1)
             if marks.words[k].lvl == 0 and not ph[k] and not ph[k + 1]]
    return marks, ph, pairs


def _tally(items) -> dict[str, dict]:
    """[(key, context)] → {key: {count, contexts ≤ 3}} sắp theo (−count, key)."""
    count, ctx = Counter(), {}
    for key, c in items:
        count[key] += 1
        ctx.setdefault(key, [])
        if len(ctx[key]) < N_CONTEXTS:
            ctx[key].append(c)
    return {k: {"count": count[k], "contexts": ctx[k]} for k in sorted(count, key=lambda x: (-count[x], x))}


def corpus_pairs(sections: dict[int, dict]) -> dict[str, dict]:
    """Mọi cặp không dấu của 60 mục VIDEO SCRIPT: {pair: {count, contexts}}."""
    items = []
    for n in sorted(sections):
        marks, _, pairs = _scan(sections[n]["script"])
        items += [(p, _context(marks, k, k + 2, f"#{n}")) for k, p in pairs]
    return _tally(items)


def corpus_syllables(sections: dict[int, dict]) -> dict[str, dict]:
    """Mọi âm tiết (chữ thường, ngoài placeholder) của 60 mục: {syllable: {count, contexts}}."""
    items = []
    for n in sorted(sections):
        marks, ph, _ = _scan(sections[n]["script"])
        items += [(m.low, _context(marks, k, k + 1, f"#{n}")) for k, m in enumerate(marks.words)
                  if not ph[k] and m.low]
    return _tally(items)


# --- nhãn -------------------------------------------------------------------------------------


def _read(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE))


def read_labels(lexdir: Path) -> tuple[dict, dict, dict]:
    """(nhãn lượt A, nhãn lượt B, dòng adjudicated theo pair)."""
    a = {_norm(r["pair"]): r["label"].strip() for r in _read(Path(lexdir) / "pass_a.tsv")}
    b = {_norm(r["pair"]): r["label"].strip() for r in _read(Path(lexdir) / "pass_b.tsv")}
    adj = {_norm(r["pair"]): r for r in _read(Path(lexdir) / "adjudicated.tsv")}
    return a, b, adj


def _pmi(pair: str, count: int, uni: Counter, total: int) -> str:
    x, y = pair.split(" ")
    pmi = math.log2(count * total / (uni[x] * uni[y]))
    return f"{pmi:.1f}" if pmi >= PMI_HINT else ""


def _tsv(header: list[str], rows) -> str:
    return "".join("\t".join(map(str, r)) + "\n" for r in [header, *rows])


def _syllable_class(s: str, lists: dict) -> str:
    for cls, key in (("LEAD", "leads"), ("TRAIL", "trails"), ("FN", "function")):
        if s in lists[key]:
            return cls
    return "C"


def review_texts(sections: dict[int, dict], lexdir: Path) -> tuple[str, str]:
    """Nội dung pairs_review.tsv và syllables_review.tsv (extract ghi đúng hai chuỗi này)."""
    pairs, syl = corpus_pairs(sections), corpus_syllables(sections)
    uni = Counter({s: v["count"] for s, v in syl.items()})
    total = sum(uni.values())
    a, b, adj = read_labels(lexdir)
    prow = [(p, v["count"], _pmi(p, v["count"], uni, total), " || ".join(v["contexts"]),
             a.get(p, ""), b.get(p, ""), adj.get(p, {}).get("label", "")) for p, v in pairs.items()]
    lists = closed_lists()
    tags = ("pronouns", "warn", "quantity", "units")
    srow = [(s, v["count"], _syllable_class(s, lists),
             ",".join(t for t in tags if s in lists[t]), " || ".join(v["contexts"]))
            for s, v in syl.items()]
    return (_tsv(["pair", "count", "pmi4", "contexts", "label_a", "label_b", "label"], prow),
            _tsv(["syllable", "count", "class", "lists", "contexts"], srow))


def build_json(sections: dict[int, dict], lexdir: Path) -> dict:
    """Nội dung text_vi.json: phiên bản, sha corpus, danh sách đóng, cặp K đã phân xử."""
    _, _, adj = read_labels(lexdir)
    return {"version": DEFAULT_VERSION,
            "corpus": {"sections": SECTIONS, "sha256": corpus_sha(sections)},
            **closed_lists(),
            "pairs": sorted(p for p, r in adj.items() if r["label"].strip() == "K")}


def json_text(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=1) + "\n"


def diff(sections: dict[int, dict], lexdir: Path) -> tuple[list[str], int]:
    """Báo cáo nhãn: bất đồng A/B (kèm nhãn cuối + lý do), cặp corpus chưa đủ nhãn, dòng thừa."""
    pairs = corpus_pairs(sections)
    a, b, adj = read_labels(lexdir)
    lines = ["pair\tA\tB\tlabel\treason"]
    unresolved = []
    for p in pairs:
        final = adj.get(p, {})
        if a.get(p) != b.get(p):
            lines.append(f"{p}\t{a.get(p, '-')}\t{b.get(p, '-')}\t{final.get('label', '-')}\t"
                         f"{final.get('reason', '')}")
        if (a.get(p) not in ("K", "S") or b.get(p) not in ("K", "S")
                or final.get("label") not in ("K", "S")
                or (a.get(p) != b.get(p) and not final.get("reason", "").strip())):
            unresolved.append(p)
    stale = sorted(set(adj) - set(pairs))
    n_dis = len(lines) - 1
    lines.append(f"corpus {len(pairs)} cặp; A/B bất đồng {n_dis}; chưa đủ nhãn/lý do "
                 f"{len(unresolved)}; dòng adjudicated ngoài corpus {len(stale)}"
                 + (f" ({', '.join(stale)})" if stale else ""))
    lines += [f"CHƯA XONG\t{p}" for p in unresolved]
    return lines, 1 if unresolved else 0


def delta(text: str, lexdir: Path) -> list[tuple[str, int, str]]:
    """Cặp không dấu của một lời chưa có trong adjudicated.tsv: (pair, số lần, ngữ cảnh đầu)."""
    _, _, adj = read_labels(lexdir)
    marks, _, pairs = _scan(text)
    tally = _tally((p, _context(marks, k, k + 2, "vo")) for k, p in pairs if p not in adj)
    return [(p, v["count"], v["contexts"][0]) for p, v in tally.items()]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Dựng từ điển text_vi.json (spec 1.1.1 §3.2)")
    ap.add_argument("cmd", nargs="?", choices=["extract"], help="ghi pairs_review/syllables_review")
    ap.add_argument("--diff", action="store_true", help="liệt kê bất đồng A/B và cặp thiếu nhãn")
    ap.add_argument("--emit", action="store_true", help="ghi releases/<ver>/data/text_vi.json")
    ap.add_argument("--delta", metavar="VO_SCRIPT", help="cặp của một lời chưa được duyệt")
    ap.add_argument("--v3", help="file '60 kịch bản HeyGen v3' (mặc định tìm trong DOCS_ROOT)")
    ap.add_argument("--dir", default=str(LEXDIR), help="thư mục TSV (mặc định tools/lexicon)")
    ap.add_argument("--out", default=str(OUT_JSON), help="đường ghi text_vi.json")
    args = ap.parse_args(argv)
    lexdir = Path(args.dir)
    if args.delta:
        rows = delta(Path(args.delta).read_text(encoding="utf-8"), lexdir)
        for p, c, ctx in rows:
            print(f"{p}\t{c}\t{ctx}")
        print(f"NOTE: {len(rows)} cặp chưa duyệt trong {args.delta}")
        return 0
    if not (args.cmd or args.diff or args.emit):
        ap.error("chọn một lệnh: extract, --diff, --emit hoặc --delta")
    sections = load_sections(args.v3)
    if args.cmd == "extract":
        pairs_tsv, syllables_tsv = review_texts(sections, lexdir)
        (lexdir / "pairs_review.tsv").write_text(pairs_tsv, encoding="utf-8", newline="\n")
        (lexdir / "syllables_review.tsv").write_text(syllables_tsv, encoding="utf-8", newline="\n")
        print(f"PASS: {len(pairs_tsv.splitlines()) - 1} cặp, "
              f"{len(syllables_tsv.splitlines()) - 1} âm tiết → {lexdir}")
    rc = 0
    if args.diff:
        lines, rc = diff(sections, lexdir)
        print("\n".join(lines))
    if args.emit:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json_text(build_json(sections, lexdir)), encoding="utf-8", newline="\n")
        print(f"PASS: đã ghi {out}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
