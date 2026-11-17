#!/usr/bin/env python3
"""A-roll bank planner: measure overlap across scripts, then plan shared A-roll shots per video.

usage: aroll_bank.py MANIFEST.json [MANIFEST.json ...] --out DIR [--mode script|library]
         [--library library.json] [--looks 5] [--reuse-max 3] [--max-slots 4] [--tps 4.2]
Input manifests = 00_storyboard_manifest.json (segments[].type/tts_text/beat_name/duration_sec/api_routing).
--mode script (default): script text is NEVER rewritten. Only lines identical across scripts (accent-free, case-free)
  share one render; every other A-roll keeps its own line. All A-roll shots are planned (--max-slots/--library ignored).
--mode library: proposes generic library lines (2-4 slots per video); every slot is flagged requires_rewrite=true
  and needs the user's approval before any render.
Every slot lists original_text (the script's line), bank_text (the line to render) and requires_rewrite; used_in.seq_index
is the A-roll segment's real seq_index in that manifest. live_shoot segments are real footage: never banked,
listed under "quay thật" in stats.json / approval.md.
Duplicate script_id: the first path wins. Read-only on inputs; writes bank.json, plans.json,
stats.json, approval.md under --out.
"""
import argparse
import itertools
import json
import math
import re
import statistics
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROLES = ("hook", "turn", "punch", "cta")
SLOT_ROLES = {2: ("hook", "cta"), 3: ("hook", "turn", "cta"), 4: ("hook", "turn", "punch", "cta")}
NEAR_THRESHOLDS = (0.8, 0.6, 0.45)  # natural-duplicate similarity levels reported
LIGHT_REWRITE = 0.35  # word-edit ratio below which a line is a "light rewrite" of a bank line
VERTICALS = (("tai_chinh", r"tai chinh|dau tu|chung khoan"),
             ("bat_dong_san", r"bat dong san"),
             ("ban_hang", r"ban hang|kinh doanh|sale"))
PLACEHOLDER_SEC = {"hook": 3.5, "turn": 3.0, "punch": 4.0, "cta": 6.0}  # duration of a not-yet-written line
KW_CTA = re.compile(r"chữ\s+(.+?)\s+(?:xuống dưới|ở dưới|bên dưới)", re.I)


# ---------- text helpers ----------
def norm_tokens(text):
    t = text.lower().replace("đ", "d")
    t = "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]+", " ", t).split()


def split_sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+", text) if s.strip()]


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 0.0


def char_ngrams(tokens, n=4):
    s = " ".join(tokens)
    return {s[i:i + n] for i in range(len(s) - n + 1)}


def similarity(ta, tb):
    """Mean of word-token Jaccard and char-4-gram Jaccard on accent-free tokens."""
    return (jaccard(ta, tb) + jaccard(char_ngrams(ta), char_ngrams(tb))) / 2


def edit_ratio(ta, tb):
    """Word-level Levenshtein distance / max length (0 = identical wording)."""
    prev = list(range(len(tb) + 1))
    for i, x in enumerate(ta, 1):
        cur = [i]
        for j, y in enumerate(tb, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1] / max(len(ta), len(tb), 1)


# ---------- loading ----------
def role_of(seg, pos, count):
    if pos == 0:
        return "hook"
    if pos == count - 1:
        return "cta"
    beat = norm_tokens(seg.get("beat_name") or "")
    return "punch" if {"chung", "diem", "nhan"} & set(beat) else "turn"


def is_live_shoot(seg):
    """Segment quay thật (người dùng tự quay): không render HeyGen, không vào bank."""
    return bool(seg.get("live_shoot")) or (seg.get("api_routing") or {}).get("video_generator") == "live_shoot"


def load_videos(paths):
    videos, skipped = {}, []
    for p in paths:
        d = json.loads(Path(p).read_text(encoding="utf-8"))
        sid = d.get("script_id") or Path(p).parent.name
        if sid in videos:
            skipped.append({"script_id": sid, "path": str(p), "kept": videos[sid]["path"]})
            continue
        arolls = [s for s in d["segments"] if s["type"] == "a-roll"]
        units = [{"seq_index": s["seq_index"], "role": role_of(s, i, len(arolls)),
                  "text": s["tts_text"], "tokens": norm_tokens(s["tts_text"]),
                  "dur": s["duration_sec"]} for i, s in enumerate(arolls) if not is_live_shoot(s)]
        live = [{"seq_index": s["seq_index"], "text": s.get("tts_text", ""), "dur": s.get("duration_sec", 0)}
                for s in arolls if is_live_shoot(s)]
        videos[sid] = {"script_id": sid, "path": str(p), "title": d.get("title", ""),
                       "ratio_mode": d.get("ratio_mode", ""), "units": units, "live": live,
                       "total_sec": sum(s["duration_sec"] for s in d["segments"]),
                       "vertical": detect_vertical(d.get("title", "") + " " + " ".join(u["text"] for u in units if u["role"] == "cta"))}
    return list(videos.values()), skipped


def detect_vertical(text):
    """Vertical from title + CTA text; ambiguous or no hit -> "any"."""
    toks = " ".join(norm_tokens(text))
    hits = sorted(((len(re.findall(rx, toks)), name) for name, rx in VERTICALS), reverse=True)
    return hits[0][1] if hits[0][0] >= 1 and hits[0][0] > hits[1][0] else "any"


# ---------- measurement ----------
def cross_pairs(items):
    """items: [(script_id, text, tokens)] -> sorted [(sim, a, b)] over different scripts."""
    out = [(similarity(a[2], b[2]), a, b) for a, b in itertools.combinations(items, 2) if a[0] != b[0]]
    return sorted(out, key=lambda r: -r[0])


def pair_stats(pairs):
    sims = [p[0] for p in pairs]
    return {"pairs": len(pairs), "max_sim": round(max(sims), 3) if sims else 0,
            "mean_sim": round(statistics.mean(sims), 3) if sims else 0,
            "exact_dup_pairs": sum(1 for p in pairs if p[1][2] == p[2][2]),
            **{f"sim_ge_{t}": sum(1 for s in sims if s >= t) for t in NEAR_THRESHOLDS}}


def families(units):
    """Template families: same first 3 accent-free words (>=3 members), + keyword-CTA / pinned-CTA counts."""
    heads = Counter(" ".join(u["tokens"][:3]) for u in units)
    fam = {h: n for h, n in heads.most_common() if n >= 3}
    cta = [u for u in units if u["role"] == "cta"]
    return {"opening_families(>=3)": fam,
            "cta_total": len(cta),
            "cta_with_comment_keyword": sum(1 for u in cta if KW_CTA.search(u["text"])),
            "cta_pinned_dau_kenh": sum(1 for u in cta if re.search(r"đầu kênh|ghim", u["text"], re.I)),
            "distinct_keywords": sorted({m.group(1) for u in cta for m in [KW_CTA.search(u["text"])] if m})}


def measure(videos):
    units = [dict(u, script_id=v["script_id"]) for v in videos for u in v["units"]]
    seg_items = [(u["script_id"], u["text"], u["tokens"]) for u in units]
    sent_items = [(u["script_id"], s, norm_tokens(s)) for u in units for s in split_sentences(u["text"])]
    seg_pairs, sent_pairs = cross_pairs(seg_items), cross_pairs(sent_items)
    top = [{"sim": round(s, 2), "a": f"{a[0]}: {a[1][:80]}", "b": f"{b[0]}: {b[1][:80]}"}
           for s, a, b in seg_pairs[:8]]
    return {"videos": len(videos), "aroll_segments": len(units), "aroll_sentences": len(sent_items),
            "aroll_per_video": dict(Counter(len(v["units"]) for v in videos)),
            "role_counts": dict(Counter(u["role"] for u in units)),
            "aroll_sec_manifest": round(sum(u["dur"] for u in units), 1),
            "segment_level": pair_stats(seg_pairs), "sentence_level": pair_stats(sent_pairs),
            "top_segment_pairs": top, "templates": families(units)}


# ---------- planning ----------
def n_slots(video, max_slots):
    return max(2, min(max_slots, len(video["units"]))) if video["units"] else 0


def load_library(path):
    lines = json.loads(Path(path).read_text(encoding="utf-8"))["lines"]
    for ln in lines:
        ln["tokens"] = norm_tokens(ln["text"])
    return lines


def new_entry(line, role, bank, look, tps):
    text = line["text"] if line else None
    toks = line["tokens"] if line else []
    entry = {"bank_id": f"B{len(bank) + 1:02d}", "lib_id": line["id"] if line else None,
             "text": text or f"<TO WRITE: generic {role} line>", "role": role, "look_slot": look,
             "vertical": line["vertical"] if line else "any", "kw": line.get("kw") if line else None,
             "dur": round(len(toks) / tps, 1) if toks else PLACEHOLDER_SEC[role], "used_in": [],
             "requires_rewrite": True}
    entry["bank_text"] = entry["text"]
    bank.append(entry)
    return entry


def next_look(bank, prev_look, looks, used_looks):
    """Round-robin look for a new bank entry: differs from prev shot, prefers looks unused in this video."""
    start = len(bank)
    cands = [(start + k) % looks + 1 for k in range(looks)]
    cands = [c for c in cands if c != prev_look]
    return next((c for c in cands if c not in used_looks), cands[0])


def pick(role, vertical, bank, library, prev_look, used_looks, used_ids, reuse_max, looks, tps):
    """Pack-first: reuse an open entry with spare capacity, else open next library line, else a TO-WRITE line."""
    fits = lambda v: v == vertical or v == "any"
    ok = lambda e: (e["role"] == role and e["bank_id"] not in used_ids and len(e["used_in"]) < reuse_max
                    and e["look_slot"] != prev_look and fits(e["vertical"]))
    open_c = sorted((e for e in bank if ok(e)),
                    key=lambda e: (e["vertical"] != vertical, e["look_slot"] in used_looks, -len(e["used_in"])))
    if open_c:
        return open_c[0]
    opened = {e["lib_id"] for e in bank}
    pool = sorted((ln for ln in library if ln["role"] == role and ln["id"] not in opened and fits(ln["vertical"])),
                  key=lambda ln: ln["vertical"] != vertical)
    return new_entry(pool[0] if pool else None, role, bank, next_look(bank, prev_look, looks, used_looks), tps)


def match_units(roles, units):
    """Mỗi slot thư viện -> A-roll gốc cùng vai trước, phần dư ghép theo thứ tự; không có -> None."""
    free, out = list(units), [None] * len(roles)
    for i, role in enumerate(roles):
        hit = next((u for u in free if u["role"] == role), None)
        if hit:
            out[i] = hit
            free.remove(hit)
    for i in range(len(roles)):
        if out[i] is None and free:
            out[i] = free.pop(0)
    return out


def _slot(i, role, e, unit):
    return {"slot": i + 1, "seq_index": unit["seq_index"] if unit else None, "role": role, "bank_id": e["bank_id"],
            "look_slot": e["look_slot"], "original_text": unit["text"] if unit else None, "bank_text": e["bank_text"],
            "requires_rewrite": e["requires_rewrite"], "dur": e["dur"]}


def _plan_doc(video, slots, used_looks):
    return {"script_id": video["script_id"], "vertical": video["vertical"], "slots": slots,
            "live_shoot": [l["seq_index"] for l in video["live"]],
            "distinct_looks": len(used_looks), "aroll_sec": round(sum(s["dur"] for s in slots), 1)}


def plan_video(video, bank, library, looks, reuse_max, max_slots, tps):
    """Chế độ library: câu chung từ thư viện, MỌI slot requires_rewrite=true (người dùng duyệt)."""
    roles = SLOT_ROLES.get(n_slots(video, max_slots), ())
    prev, used_looks, used_ids, slots = None, set(), set(), []
    for i, (role, unit) in enumerate(zip(roles, match_units(roles, video["units"]))):
        e = pick(role, video["vertical"], bank, library, prev, used_looks, used_ids, reuse_max, looks, tps)
        e["used_in"].append({"script_id": video["script_id"], "seq_index": unit["seq_index"] if unit else None})
        used_ids.add(e["bank_id"])
        used_looks.add(e["look_slot"])
        prev = e["look_slot"]
        slots.append(_slot(i, role, e, unit))
    return _plan_doc(video, slots, used_looks)


def plan_video_script(video, bank, looks, reuse_max):
    """Chế độ script: giữ nguyên lời kịch bản; chỉ gộp câu y hệt giữa các script (cùng chuẩn hoá không dấu)."""
    prev, used_looks, used_ids, slots = None, set(), set(), []
    for i, u in enumerate(video["units"]):
        key = tuple(u["tokens"])
        e = next((e for e in bank if e["_key"] == key and e["bank_id"] not in used_ids
                  and len(e["used_in"]) < reuse_max and e["look_slot"] != prev), None)
        if e is None:
            e = {"bank_id": f"B{len(bank) + 1:02d}", "lib_id": None, "text": u["text"], "bank_text": u["text"], "role": u["role"],
                 "look_slot": next_look(bank, prev, looks, used_looks), "vertical": video["vertical"], "kw": None,
                 "dur": u["dur"], "used_in": [], "requires_rewrite": False, "_key": key}
            bank.append(e)
        e["used_in"].append({"script_id": video["script_id"], "seq_index": u["seq_index"]})
        used_ids.add(e["bank_id"])
        used_looks.add(e["look_slot"])
        prev = e["look_slot"]
        slots.append(_slot(i, u["role"], e, u))
    return _plan_doc(video, slots, used_looks)


def rewrite_cost(videos, library):
    """Per role: word-edit ratio from each original A-roll line to its closest library line (0 = already identical)."""
    per_role = defaultdict(list)
    for v in videos:
        for u in v["units"]:
            cands = [ln for ln in library if ln["role"] == u["role"]]
            if cands:
                per_role[u["role"]].append(min(edit_ratio(u["tokens"], c["tokens"]) for c in cands))
    return {r: {"n": len(x), "mean_edit_ratio": round(statistics.mean(x), 2),
                "light_rewrite(<=%.2f)" % LIGHT_REWRITE: sum(1 for k in x if k <= LIGHT_REWRITE),
                "identical": sum(1 for k in x if k == 0)} for r, x in per_role.items()}


def scale_table(reuse_max):
    rows = []
    for n, s, r in itertools.product((30, 40, 50), (2, 3, 4), (2, reuse_max)):
        rows.append({"videos": n, "slots_per_video": s, "reuse": r, "min_renders": math.ceil(n * s / r)})
    return rows


def run_plan(videos, library, looks, reuse_max, max_slots, tps, mode="script"):
    bank = []
    if mode == "script":
        plans = [plan_video_script(v, bank, looks, reuse_max) for v in videos]
    else:
        plans = [plan_video(v, bank, library, looks, reuse_max, max_slots, tps) for v in videos]
    return bank, plans


def live_stats(videos):
    """"quay thật": segment live_shoot — footage thật, không nằm trong A-roll render."""
    items = [{"script_id": v["script_id"], "seq_index": l["seq_index"], "dur": l["dur"], "text": l["text"][:80]}
             for v in videos for l in v["live"]]
    return {"shots": len(items), "sec": round(sum(i["dur"] for i in items), 1), "list": items}


def stats(videos, bank, plans, meas, library, looks, reuse_max, tps, mode="script"):
    uses = [len(e["used_in"]) for e in bank]
    total_slots = sum(len(p["slots"]) for p in plans)
    base_sec = meas["aroll_sec_manifest"]
    bank_sec = sum(e["dur"] for e in bank)
    airtime = sum(p["aroll_sec"] for p in plans)
    to_write = [e for e in bank if e["lib_id"] is None and mode == "library"]
    sec_by_look = Counter()
    for e in bank:
        sec_by_look[e["look_slot"]] += e["dur"]
    return {"mode": mode, "videos": len(videos), "slots_total": total_slots,
            "slots_requiring_rewrite": sum(1 for p in plans for x in p["slots"] if x["requires_rewrite"]),
            "baseline_aroll_renders": meas["aroll_segments"], "planned_renders": len(bank),
            "renders_saved": meas["aroll_segments"] - len(bank),
            "bank_by_role": dict(Counter(e["role"] for e in bank)),
            "lines_to_write_beyond_library": dict(Counter(e["role"] for e in to_write)),
            "reuse_hist": dict(sorted(Counter(uses).items())), "avg_uses_per_render": round(statistics.mean(uses), 2) if uses else 0,
            "slots_served_by_library_lines_pct": round(100 * sum(len(e["used_in"]) for e in bank if e["lib_id"]) / total_slots, 1) if total_slots else 0,
            "heygen_jobs_if_packed_90s_per_look": sum(math.ceil(t / 90) for t in sec_by_look.values()), "baseline_aroll_sec": base_sec,
            "planned_render_sec": round(bank_sec, 1), "planned_airtime_sec": round(airtime, 1),
            "render_sec_saved_pct": round(100 * (1 - bank_sec / base_sec), 1) if base_sec else 0,
            "slots_per_video": dict(Counter(len(p["slots"]) for p in plans)),
            "distinct_looks_per_video": dict(Counter(p["distinct_looks"] for p in plans)),
            "consecutive_same_look": sum(1 for p in plans for a, b in zip(p["slots"], p["slots"][1:]) if a["look_slot"] == b["look_slot"]),
            "keywords_needing_lead_magnet": sorted({e["kw"] for e in bank if e["kw"]}),
            "rewrite_cost_vs_library": rewrite_cost(videos, library),
            "min_renders_scale_table": scale_table(reuse_max), "params": {"looks": looks, "reuse_max": reuse_max, "tps": tps}}


# ---------- output ----------
def approval_md(meas, st, bank, plans, skipped, live):
    m, s = meas, st
    out = ["# A-roll bank — bảng duyệt\n",
           f"- Video: **{s['videos']}**, A-roll hiện có: **{m['aroll_segments']}** shot ({m['aroll_sentences']} câu, {m['aroll_sec_manifest']} s)",
           f"- Trùng lặp tự nhiên giữa các kịch bản (khác script): cấp shot max sim = **{m['segment_level']['max_sim']}**, "
           f"trùng y hệt = **{m['segment_level']['exact_dup_pairs']}**, sim ≥ 0.6 = **{m['segment_level']['sim_ge_0.6']}**; "
           f"cấp câu: trùng y hệt = **{m['sentence_level']['exact_dup_pairs']}**, sim ≥ 0.6 = **{m['sentence_level']['sim_ge_0.6']}**",
           f"- Kế hoạch: **{s['planned_renders']} render** (hiện {m['aroll_segments']}), tái dùng TB **{s['avg_uses_per_render']}** lần/render, "
           f"giây render {s['planned_render_sec']} s vs {m['aroll_sec_manifest']} s hiện tại ({s['render_sec_saved_pct']} % ít hơn)\n",
           f"- Chế độ: **{s['mode']}** — " + ("giữ nguyên lời kịch bản, chỉ gộp câu y hệt" if s["mode"] == "script"
                                          else "câu chung từ thư viện, MỌI slot cần người duyệt viết lại (requires_rewrite)"),
           f"- Quay thật (live_shoot, không render HeyGen): **{live['shots']}** shot, {live['sec']} s\n",
           "## 1. Ngân hàng A-roll (cần duyệt câu chữ)\n",
           "| ID | Vai | Look | Vertical | s | Dùng trong (script#seq) | Cần viết lại | Câu render |", "|---|---|---|---|---|---|---|---|"]
    for e in bank:
        used = ", ".join(f"{u['script_id']}#{u['seq_index']}" for u in e["used_in"])
        out.append(f"| {e['bank_id']} | {e['role']} | {e['look_slot']} | {e['vertical']} | {e['dur']} | {used} | "
                   f"{'có' if e['requires_rewrite'] else 'không'} | {e['bank_text']} |")
    out += ["\n## 2. Kế hoạch từng video (mỗi shot khác look shot trước)\n", "| Script | Vertical | Shot (vai:ID:look) |", "|---|---|---|"]
    for p in plans:
        out.append(f"| {p['script_id']} | {p['vertical']} | " + " → ".join(f"{x['role']}:{x['bank_id']}:L{x['look_slot']}" for x in p["slots"]) + " |")
    if live["list"]:
        out += ["\n## Quay thật (người dùng tự quay, không render)\n"] + [f"- {i['script_id']} #{i['seq_index']} ({i['dur']} s): {i['text']}" for i in live["list"]]
    out += ["\n## 3. Cần quyết định\n",
            f"- Từ khoá bình luận phải khớp quà thật: {', '.join(s['keywords_needing_lead_magnet']) or '(không)'}",
            f"- Slot cần người duyệt viết lại: {s['slots_requiring_rewrite']}/{s['slots_total']}",
            f"- Câu còn phải viết thêm ngoài thư viện: {s['lines_to_write_beyond_library'] or 'không'}",
            f"- Hook/CTA chung chung làm giảm tính riêng của hook: tiêu đề chữ trên màn + B-roll voice-over phải mang chủ đề riêng.",
            f"- Script trùng id bị bỏ: {len(skipped)}"]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifests", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mode", choices=("script", "library"), default="script",
                    help="script (mặc định): giữ lời kịch bản, chỉ gộp câu y hệt; library: câu chung từ thư viện, mọi slot requires_rewrite")
    ap.add_argument("--library", default=str(Path(__file__).resolve().parent.parent / "references" / "aroll-bank-library.json"))
    ap.add_argument("--looks", type=int, default=5)
    ap.add_argument("--reuse-max", type=int, default=3)
    ap.add_argument("--max-slots", type=int, default=4)
    ap.add_argument("--tps", type=float, default=4.2, help="spoken tokens per second")
    a = ap.parse_args()
    videos, skipped = load_videos(a.manifests)
    library = load_library(a.library) if a.mode == "library" else []
    meas = measure(videos)
    bank, plans = run_plan(videos, library, a.looks, a.reuse_max, a.max_slots, a.tps, a.mode)
    st = stats(videos, bank, plans, meas, library, a.looks, a.reuse_max, a.tps, a.mode)
    live = live_stats(videos)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    keep = ("bank_id", "text", "bank_text", "requires_rewrite", "role", "look_slot", "used_in", "dur", "vertical", "kw", "lib_id")
    (out / "bank.json").write_text(json.dumps([{k: e[k] for k in keep} for e in bank], ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "plans.json").write_text(json.dumps(plans, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "stats.json").write_text(json.dumps({"measure": meas, "plan": st, "quay thật": live, "skipped_duplicates": skipped}, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "approval.md").write_text(approval_md(meas, st, bank, plans, skipped, live), encoding="utf-8")
    print(json.dumps({"mode": a.mode, "quay_that": live["shots"], "videos": st["videos"], "baseline_renders": meas["aroll_segments"], "planned_renders": st["planned_renders"],
                      "avg_uses": st["avg_uses_per_render"], "to_write": st["lines_to_write_beyond_library"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
