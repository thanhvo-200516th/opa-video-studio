#!/usr/bin/env python3
"""plan_to_minimal — plan_export.json (người duyệt đã chọn A / B / C từng nhịp) → <W>/minimal_plan.json cho mẫu build_spec_minimal.py.

    plan_to_minimal.py <W> [--cta "Từ CTA"] [--manifest <V>/00_storyboard_manifest.json]
Đọc : <W>/plan_export.json (plan_doc.py export) · <W>/words_tl.json · <W>/pain.json (tuỳ chọn, {"pain": [...]}).
Ghi : <W>/minimal_plan.json = {"groups": [str|null], "scene_gfx": [[...]], "cta_word": str|null, "pain": [str]} (mẫu tự nạp khi có file)
      <W>/minimal_plan_review.json = các từ lớn TỰ CHỌN (độ dài lớn nhất) cần người duyệt lại. In bảng tóm tắt.

Quy ước:
  · mọi nhịp (trừ cảnh thẻ trích dẫn) đều có cụm chữ "nhỏ | nhỏ | *từ lớn" phủ HẾT lời của nhịp (mẫu khớp tuần tự, None nhảy tới hết cảnh).
  · từ lớn = cụm người dùng đã chọn ở A (`*` sans) / B (`~` serif); cụm khác, hoặc nhịp chưa chọn / chọn C → đoạn nội dung dài nhất ≤ 3 tiếng (đánh dấu «tự chọn»).
  · C kiểu quote / quote_paper → cả cảnh là thẻ toàn chữ: ghi None một lần cho cảnh đó, không sinh cụm chữ.
  · scene_gfx = [kind, <các trường của kind theo thứ tự plan_doc.GFX_KINDS>] sắp theo giờ nhịp.
  · cta_word: --cta, hoặc nhịp có ghi chú chứa "CTA" (lấy từ lớn của nhịp đó); phải là từ lớn của một cụm.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plan_doc as pd  # noqa: E402

CHUNK_MAX_WORDS, CHUNK_MIN_WORDS = 7, 4     # profile key: captions.group_max_words / group_min_words (chưa có trong hồ sơ — hằng tạm; đơn vị = tiếng)
ITEM_WORDS, HERO_MAX_WORDS = 3, 3            # profile key: captions.item_max_words / captions.hero_max_words (tiếng tối đa mỗi mục nhỏ / từ lớn tự chọn)
QUOTE_KINDS = ("quote", "quote_paper")


def strip_punct(tok: str) -> str:
    return re.sub(r"[^\w\s%]", "", tok)


def beat_tokens(words: list[tuple[str, float, float]], b: dict) -> list[str]:
    """Từ của nhịp: bắt đầu trong [t0, t1) — khớp cách plan_doc chia nhịp (nhịp đầu t0 = 0)."""
    return [w[0] for w in words if b["t0"] - 1e-3 <= w[1] < b["t1"] - 1e-3]


def find_span(toks: list[str], phrase: str) -> tuple[int, int] | None:
    ptoks = pd.norm(phrase).split()
    n = len(ptoks)
    for i in range(len(toks) - n + 1):
        if n and [pd.norm(t) for t in toks[i:i + n]] == ptoks:
            return i, i + n - 1
    return None


def atoms_of(toks: list[str], hero: tuple[int, int] | None) -> list[dict]:
    """Chuỗi nguyên tử {text, user, n, clause}: từ lẻ, riêng cụm từ lớn người dùng chọn là một nguyên tử."""
    out, i = [], 0
    while i < len(toks):
        if hero and i == hero[0]:
            seg = toks[hero[0]:hero[1] + 1]
            out.append({"text": " ".join(t for t in map(strip_punct, seg) if t), "user": True, "n": len(seg),
                        "clause": seg[-1].endswith(pd.SENTENCE_END + pd.CLAUSE_END)})
            i = hero[1] + 1
            continue
        if (t := strip_punct(toks[i])):
            out.append({"text": t, "user": False, "n": 1, "clause": toks[i].endswith(pd.SENTENCE_END + pd.CLAUSE_END)})
        i += 1
    return out


def chunk_atoms(atoms: list[dict]) -> list[list[dict]]:
    """Cắt nhịp thành cụm ≥ CHUNK_MIN_WORDS tiếng, ≤ CHUNK_MAX_WORDS: đóng ở dấu câu / trước từ phụ (tiếng Việt: mỗi từ words_tl là MỘT tiếng)."""
    chunks, cur, count = [], [], 0
    for i, a in enumerate(atoms):
        cur.append(a)
        count += a["n"]
        nxt = atoms[i + 1] if i + 1 < len(atoms) else None
        if nxt and (count + nxt["n"] > CHUNK_MAX_WORDS or (count >= CHUNK_MIN_WORDS and (a["clause"] or pd.norm(nxt["text"]) in pd.STOP))):
            chunks.append(cur)
            cur, count = [], 0
    if cur:
        if chunks and sum(a["n"] for a in cur) < CHUNK_MIN_WORDS - 1:
            chunks[-1].extend(cur)                       # đuôi quá ngắn → gộp vào cụm trước
        else:
            chunks.append(cur)
    return chunks


def auto_hero(chunk: list[dict]) -> tuple[int, int]:
    """Đoạn nguyên tử làm từ lớn: đoạn dài nhất các tiếng không phải từ phụ (hoà → đoạn sau), tối đa HERO_MAX_WORDS tiếng cuối đoạn;
    toàn từ phụ → tiếng cuối."""
    runs, a = [], None
    for i, at in enumerate(chunk + [{"text": "và"}]):
        if pd.norm(at["text"]) in pd.STOP:
            if a is not None:
                runs.append((a, i - 1))
            a = None
        elif a is None:
            a = i
    if not runs:
        return len(chunk) - 1, len(chunk) - 1
    h0, h1 = max(runs, key=lambda r: (r[1] - r[0], r[0]))
    return max(h0, h1 - HERO_MAX_WORDS + 1), h1


def _items(atoms: list[dict]) -> list[str]:
    return [" ".join(a["text"] for a in atoms[i:i + ITEM_WORDS]) for i in range(0, len(atoms), ITEM_WORDS)]


def chunk_to_group(chunk: list[dict], marker: str) -> tuple[str, str, bool]:
    """(chuỗi nhóm, từ lớn, tự_chọn?)."""
    u = next((i for i, a in enumerate(chunk) if a["user"]), None)
    auto = u is None
    h0, h1 = auto_hero(chunk) if auto else (u, u)
    hero = " ".join(a["text"] for a in chunk[h0:h1 + 1])
    return " | ".join(_items(chunk[:h0]) + [marker + hero] + _items(chunk[h1 + 1:])), hero, auto


def build_groups(words: list[tuple[str, float, float]], beats: list[dict]) -> tuple[list, list[dict]]:
    """(groups, review) — review = [{beat, hero, auto}] cho mọi cụm."""
    quote_scenes = {b["scene"] for b in beats if b.get("choice") and (b.get("gfx") or {}).get("kind") in QUOTE_KINDS}
    groups: list = []
    review: list[dict] = []
    seen_quote: set[int] = set()
    for b in sorted(beats, key=lambda x: x["t0"]):
        if b["scene"] in quote_scenes:
            if b["scene"] not in seen_quote:
                groups.append(None)
                seen_quote.add(b["scene"])
            continue
        toks = beat_tokens(words, b)
        ch, key = b.get("choice") or {}, b.get("key")
        hero = find_span(toks, key["phrase"]) if key and ch.get("kind") in ("stay", "keyword") else None
        marker = "~" if ch.get("kind") == "keyword" else "*"
        for chunk in chunk_atoms(atoms_of(toks, hero)):
            g, h, auto = chunk_to_group(chunk, marker)
            groups.append(g)
            review.append({"beat": b["beat"], "hero": h, "auto": auto})
    return groups, review


def check_groups(groups: list, words: list[tuple[str, float, float]]) -> list[str]:
    """Khớp tuần tự giống mẫu (bỏ qua None): báo cụm không khớp lời."""
    ptr, errs = 0, []
    for g in (g for g in groups if g):
        for it in (s.strip() for s in g.split("|")):
            first = pd.norm(it.lstrip("*~").split()[0])
            while ptr < len(words) and pd.norm(words[ptr][0]) != first:
                ptr += 1
            if ptr >= len(words):
                return errs + [f"cụm «{g}» không khớp lời"]
            ptr += len(it.lstrip("*~").split())
    return errs


def gfx_tuple(g: dict) -> list:
    return [g["kind"]] + [g[f["k"]] for f in pd.GFX_KINDS[g["kind"]]["fields"]]


def build_scene_gfx(beats: list[dict]) -> tuple[list[list], list[str]]:
    """([tuple…] theo giờ, cảnh báo thiếu ảnh)."""
    out, warns = [], []
    for b in sorted(beats, key=lambda x: x["t0"]):
        g = b.get("gfx")
        if not (b.get("choice") and g):
            continue
        for f in pd.GFX_KINDS[g["kind"]]["fields"]:
            if f["t"] == "image" and not Path(g[f["k"]]).expanduser().is_file():
                warns.append(f"nhịp {b['beat']} ({g['kind']}): không thấy ảnh {g[f['k']]}")
        out.append(gfx_tuple(g))
    return out, warns


def find_cta(beats: list[dict], groups: list, cta: str | None) -> tuple[str | None, str | None]:
    """(cta_word, cảnh báo). Trả đúng chuỗi từ lớn trong groups (mẫu so sánh phân biệt hoa thường)."""
    if cta is None:
        hit = next((b for b in beats if re.search(r"\bcta\b", b.get("note") or "", re.I) and b.get("key")), None)
        cta = hit["key"]["text"] if hit else None
    if not cta:
        return None, None
    heroes = [s.strip()[1:] for g in groups if g for s in g.split("|") if s.strip()[:1] in "*~"]
    match = next((h for h in heroes if pd.norm(h) == pd.norm(cta)), None)
    return (match, None) if match else (cta, f"CTA «{cta}» không là từ lớn của cụm nào — sửa --cta hoặc đánh dấu từ đó ở A / B")


def load_pain(w: Path) -> list[str]:
    f = w / "pain.json"
    return [str(x) for x in json.loads(f.read_text(encoding="utf-8")).get("pain", [])] if f.is_file() else []


def summary(beats: list[dict], review: list[dict], groups: list) -> str:
    rows = ["nhịp  giờ            chọn  nội dung"]
    for b in sorted(beats, key=lambda x: x["t0"]):
        ch, g = b.get("choice"), b.get("gfx")
        pick = {"stay": "A", "keyword": "B", "broll": "C", "gfx": "C"}.get(ch["kind"], "?") if ch else "-"
        what = (f"đồ hoạ {g['kind']}" if g else "") or ("(chưa chọn → cụm tự động)" if not ch else "")
        heroes = [f"{r['hero']}{' (tự chọn)' if r['auto'] else ''}" for r in review if r["beat"] == b["beat"]]
        rows.append(f"{b['beat']:>4}  {b['t0']:5.1f}–{b['t1']:5.1f} s   {pick}    " + (what + " · " if what else "") + ("từ lớn: " + ", ".join(heroes) if heroes else "cảnh thẻ trích dẫn"))
    return "\n".join(rows) + f"\n{sum(1 for g in groups if g)} cụm chữ · {sum(1 for r in review if r['auto'])} từ lớn tự chọn cần duyệt"


def convert(w: Path, cta: str | None = None) -> tuple[dict, list[dict], list[str]]:
    exp_f = w / "plan_export.json"
    if not exp_f.is_file():
        raise SystemExit(f"Không thấy {exp_f}: chạy plan_doc.py export <file tải về> {w}")
    beats = json.loads(exp_f.read_text(encoding="utf-8")).get("beats", [])
    words = pd.load_words(w)
    groups, review = build_groups(words, beats)
    scene_gfx, warns = build_scene_gfx(beats)
    warns += [f"{e}" for e in check_groups(groups, words)]
    cta_word, cta_warn = find_cta(beats, groups, cta)
    warns += [cta_warn] if cta_warn else []
    plan = {"groups": groups, "scene_gfx": scene_gfx, "cta_word": cta_word, "pain": load_pain(w)}
    return plan, review, warns


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("work", type=Path)
    ap.add_argument("--cta", help="từ lớn làm CTA (hộp xanh), vd «Bất Động Sản»")
    a = ap.parse_args(argv)
    plan, review, warns = convert(a.work, a.cta)
    beats = json.loads((a.work / "plan_export.json").read_text(encoding="utf-8"))["beats"]
    (a.work / "minimal_plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    (a.work / "minimal_plan_review.json").write_text(json.dumps([r for r in review if r["auto"]], ensure_ascii=False, indent=1), encoding="utf-8")
    print(summary(beats, review, plan["groups"]))
    print(f"scene_gfx: {len(plan['scene_gfx'])} · cta_word: {plan['cta_word']!r} · pain: {plan['pain']}")
    for m in warns:
        print(f"[cảnh báo] {m}", file=sys.stderr)
    print(f"Đã ghi {a.work / 'minimal_plan.json'} (+ minimal_plan_review.json). Chạy tiếp build_spec_minimal.py — mẫu tự nạp file này.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
