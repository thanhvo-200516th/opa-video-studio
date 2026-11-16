#!/usr/bin/env python3
"""broll_from_video.py — Phân tích video / transcript → kế hoạch B-Roll chuẩn D1/E2 → kiểm prompt H5 cho Google Flow.

Chạy:
    PY=~/.venvs/video-skills/bin/python
    $PY scripts/broll_from_video.py analyze --transcript transcript.json --out work_dir
    $PY scripts/broll_from_video.py analyze --video aroll_raw.mp4 --out work_dir
    $PY scripts/broll_from_video.py check-prompts --plan work_dir/broll_plan.json --prompts prompts.json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import broll_fix as bf  # noqa: E402
import edit_rules as er  # noqa: E402

PAUSE_SPLIT_SEC = 0.45
DEFAULT_MIN_SEG = 3.0
DEFAULT_MAX_SEG = 10.0
DEFAULT_MIN_COVERAGE = er.MIN_BROLL_SHARE   # 0.25 (Luật D1)
MAX_AROLL_RUN_SEC = er.MAX_AROLL_ONLY_S    # 8.0  (Luật D1)
LONG_TALK_SEC = er.LONG_TALK_S             # 4.0  (Luật D1)

ACTION_CUES = (
    "ví dụ", "thực tế", "kết quả", "văn phòng", "bàn làm việc", "nhân viên",
    "đội ngũ", "khách hàng", "quy trình", "sản phẩm", "hệ thống", "công việc",
    "buổi sáng", "ban đêm", "ngồi", "làm việc", "gõ", "kiểm tra", "chạy",
    "tìm", "viết", "xây", "tạo", "tăng", "giảm", "tiết kiệm", "hiệu quả",
    "cửa hàng", "quán", "kho", "xưởng", "màn hình", "báo cáo", "doanh thu",
    "đơn hàng", "tin nhắn", "thời gian", "chi phí", "tự động", "thủ công",
)
CTA_CUES = (
    "follow", "theo dõi", "bình luận", "comment", "nhắn tin", "inbox",
    "đăng ký", "lưu lại", "chia sẻ", "link", "liên hệ", "bấm vào",
    "hãy thử", "đừng quên", "kết nối",
)
SENTENCE_END_RE = re.compile(r"[.?!…]+[\"'”’)\]]*$")
CLAUSE_END_RE = re.compile(r"[,;:]+[\"'”’)\]]*$")


def _norm_lower(text: str) -> str:
    return unicodedata.normalize("NFC", text or "").lower()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _transcribe_video(video_path: Path, out_dir: Path, language: str = "vi") -> Path:
    helper = SCRIPTS_DIR / "apps" / "video-use" / "helpers" / "transcribe.py"
    if not helper.is_file():
        raise FileNotFoundError(f"Không thấy helper transcribe: {helper}")
    spec = importlib.util.spec_from_file_location("video_use_transcribe", helper)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Không nạp được helper transcribe: {helper}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.transcribe_one(video_path, out_dir.resolve(), language=language)


def extract_words(transcript: dict[str, Any]) -> list[dict[str, Any]]:
    """Chuẩn hoá danh sách từ có timestamp từ JSON Scribe hoặc Whisper."""
    raw_words = transcript.get("words")
    words: list[dict[str, Any]] = []
    if isinstance(raw_words, list) and raw_words:
        for w in raw_words:
            if not isinstance(w, dict):
                continue
            wtype = w.get("type", "word")
            text = str(w.get("text") or "").strip()
            if wtype != "word" or not text:
                continue
            start = float(w.get("start") or 0.0)
            end = max(float(w.get("end") or start), start + 0.05)
            words.append({"text": text, "start": round(start, 3), "end": round(end, 3)})
    elif isinstance(transcript.get("segments"), list):
        for seg in transcript["segments"]:
            if not isinstance(seg, dict):
                continue
            seg_words = seg.get("words")
            if isinstance(seg_words, list) and seg_words:
                for w in seg_words:
                    text = str(w.get("word") or w.get("text") or "").strip()
                    if not text:
                        continue
                    start = float(w.get("start") or seg.get("start") or 0.0)
                    end = max(float(w.get("end") or start), start + 0.05)
                    words.append({"text": text, "start": round(start, 3), "end": round(end, 3)})
            else:
                tokens = str(seg.get("text") or "").split()
                if not tokens:
                    continue
                s0 = float(seg.get("start") or 0.0)
                s1 = max(float(seg.get("end") or s0), s0 + 0.1 * len(tokens))
                step = (s1 - s0) / len(tokens)
                for idx, tok in enumerate(tokens):
                    words.append({
                        "text": tok,
                        "start": round(s0 + idx * step, 3),
                        "end": round(s0 + (idx + 1) * step, 3),
                    })
    if not words:
        raise ValueError("Transcript không có từ nào có word timestamps.")
    words.sort(key=lambda x: (x["start"], x["end"]))
    return words


def _make_span(word_slice: list[dict[str, Any]]) -> dict[str, Any]:
    text = " ".join(w["text"] for w in word_slice).strip()
    start = round(float(word_slice[0]["start"]), 3)
    end = round(float(word_slice[-1]["end"]), 3)
    return {
        "words": word_slice,
        "text": text,
        "start": start,
        "end": end,
        "dur": round(max(0.05, end - start), 3),
        "ends_sentence": bool(SENTENCE_END_RE.search(word_slice[-1]["text"])),
    }


def _split_oversized_words(word_slice: list[dict[str, Any]], max_dur: float) -> list[dict[str, Any]]:
    """Tách lát từ quá dài thành các cụm <= max_dur tại dấu phẩy hoặc khoảng hở lớn nhất."""
    if not word_slice:
        return []
    span = _make_span(word_slice)
    if span["dur"] <= max_dur or len(word_slice) == 1:
        return [span]

    best_idx = None
    best_score = -1.0
    t0 = word_slice[0]["start"]
    t1 = word_slice[-1]["end"]
    mid = (t0 + t1) / 2.0
    for idx in range(1, len(word_slice)):
        left_dur = word_slice[idx - 1]["end"] - t0
        right_dur = t1 - word_slice[idx]["start"]
        if left_dur < 1.2 or right_dur < 1.2:
            continue
        gap = max(0.0, word_slice[idx]["start"] - word_slice[idx - 1]["end"])
        comma = 1.0 if CLAUSE_END_RE.search(word_slice[idx - 1]["text"]) else 0.0
        balance = 1.0 - abs(((t0 + left_dur) - mid) / max(0.1, (t1 - t0) / 2.0))
        score = gap * 4.0 + comma * 2.5 + balance
        if left_dur <= max_dur and score > best_score:
            best_score = score
            best_idx = idx
    if best_idx is None:
        for idx in range(1, len(word_slice)):
            if word_slice[idx - 1]["end"] - t0 <= max_dur:
                best_idx = idx
        if best_idx is None:
            best_idx = max(1, len(word_slice) // 2)

    return (
        _split_oversized_words(word_slice[:best_idx], max_dur)
        + _split_oversized_words(word_slice[best_idx:], max_dur)
    )


def build_blocks(
    words: list[dict[str, Any]],
    min_seg: float = DEFAULT_MIN_SEG,
    max_seg: float = DEFAULT_MAX_SEG,
    pause_split: float = PAUSE_SPLIT_SEC,
) -> list[dict[str, Any]]:
    """Gom các từ transcript thành các block ý nghĩa [min_seg, max_seg], tách ở câu / khoảng lặng."""
    if min_seg <= 0 or max_seg < min_seg:
        raise ValueError("Yêu cầu 0 < min_seg <= max_seg.")

    # Bước 1: tách thành mệnh đề nguyên tử tại .?! hoặc khoảng lặng > pause_split
    clauses: list[dict[str, Any]] = []
    cur: list[dict[str, Any]] = []
    for idx, w in enumerate(words):
        cur.append(w)
        is_last = idx == len(words) - 1
        gap = 0.0 if is_last else max(0.0, words[idx + 1]["start"] - w["end"])
        if is_last or SENTENCE_END_RE.search(w["text"]) or gap > pause_split:
            clauses.extend(_split_oversized_words(cur, max_seg))
            cur = []

    if not clauses:
        return []

    # Bước 2: gộp các mệnh đề ngắn thành block hợp lý (giữ block 0 làm hook <= 7.5s)
    blocks: list[dict[str, Any]] = []
    acc = clauses[0]
    for nxt in clauses[1:]:
        is_hook = len(blocks) == 0
        eff_max = min(max_seg, 7.5) if is_hook else max_seg
        merged_dur = nxt["end"] - acc["start"]
        gap = max(0.0, nxt["start"] - acc["end"])

        if acc["dur"] < min_seg and merged_dur <= eff_max:
            acc = _make_span(acc["words"] + nxt["words"])
            continue

        if acc["dur"] >= min_seg:
            if acc["ends_sentence"] or gap > pause_split or acc["dur"] >= 5.0 or merged_dur > eff_max:
                blocks.append(acc)
                acc = nxt
            else:
                acc = _make_span(acc["words"] + nxt["words"])
        else:
            blocks.append(acc)
            acc = nxt
    blocks.append(acc)

    # Bước 3: nếu block cuối quá vụn (< 2.0s), gộp vào block trước nếu không vượt max_seg
    if len(blocks) >= 2 and blocks[-1]["dur"] < min(min_seg, 2.0):
        merged_last = blocks[-1]["end"] - blocks[-2]["start"]
        limit = min(max_seg, 7.5) if len(blocks) == 2 else max_seg
        if merged_last <= limit:
            prev = blocks[-2]
            last = blocks[-1]
            blocks[-2] = _make_span(prev["words"] + last["words"])
            blocks.pop()

    return blocks


def _find_cues(text: str, cues: tuple[str, ...]) -> list[str]:
    norm = _norm_lower(text)
    hits = []
    for c in cues:
        if re.search(rf"(?<!\w){re.escape(c)}(?!\w)", norm):
            hits.append(c)
    return hits


def _score_block(block: dict[str, Any], idx: int, total_blocks: int) -> dict[str, Any]:
    text = block["text"]
    dur = block["dur"]
    pain_hits = er.find_pain_in_text(text)
    action_hits = _find_cues(text, ACTION_CUES)
    cta_hits = _find_cues(text, CTA_CUES)

    score = dur * 2.0
    if dur >= LONG_TALK_SEC:
        score += 15.0
    score += 35.0 * len(pain_hits)
    score += 10.0 * min(len(action_hits), 3)
    if idx == 0:
        score -= 1000.0
    if total_blocks >= 3 and idx == total_blocks - 1 and (cta_hits or dur <= 4.5):
        score -= 50.0

    return {
        "pain_hits": pain_hits,
        "action_hits": action_hits,
        "cta_hits": cta_hits,
        "score": round(score, 2),
    }


def _max_aroll_run(blocks: list[dict[str, Any]], roles: list[str]) -> tuple[float, list[int]]:
    worst_span = 0.0
    worst_run: list[int] = []
    cur_run: list[int] = []
    for idx, role in enumerate(roles):
        if role == "A-ROLL":
            cur_run.append(idx)
        else:
            if cur_run:
                span = blocks[cur_run[-1]]["end"] - blocks[cur_run[0]]["start"]
                if span > worst_span:
                    worst_span, worst_run = span, list(cur_run)
                cur_run = []
    if cur_run:
        span = blocks[cur_run[-1]]["end"] - blocks[cur_run[0]]["start"]
        if span > worst_span:
            worst_span, worst_run = span, list(cur_run)
    return round(worst_span, 3), worst_run


def _prompt_draft_hint(text: str, meta: dict[str, Any]) -> str:
    pain = meta["pain_hits"]
    if pain:
        focus = f"hành động minh hoạ nỗi đau '{pain[0]}' (tránh chữ/số/biểu đồ/logo/UI)"
    elif meta["action_hits"]:
        focus = f"cảnh thực tế minh hoạ '{', '.join(meta['action_hits'][:2])}' bám sát anchor_quote"
    else:
        focus = "hành động/bối cảnh cụ thể minh hoạ đúng anchor_quote"
    return (
        f"Khung H5 (8–60 từ tiếng Anh, không dấu, không đuôi NO text): "
        f"[Vietnamese subject / over-the-shoulder / hands only] + [{focus}] + "
        f"[bối cảnh thật, màn hình/giấy nếu có phải out of focus hoặc blank] + "
        f"[ánh sáng tự nhiên/ấm] + [1 chuyển động máy mượt: slow push-in / tracking]."
    )


def _aroll_reason(idx: int, total: int, meta: dict[str, Any], dur: float) -> str:
    if idx == 0:
        return f"Hook mở đầu ({dur:.2f}s) — giữ mặt người nói để bắt nhịp 0–3s đầu."
    if total >= 3 and idx == total - 1 and meta["cta_hits"]:
        return f"Chốt CTA cuối video ({', '.join(meta['cta_hits'][:2])}) — giữ mặt người nói."
    return f"Giữ nhịp A-Roll đối thoại ({dur:.2f}s ≤ {MAX_AROLL_RUN_SEC:.0f}s nói trơ tối đa)."


def _broll_reason(meta: dict[str, Any], dur: float, broke_long_aroll: bool, for_coverage: bool) -> str:
    parts = []
    if meta["pain_hits"]:
        parts.append(f"Luật E2: chứa từ khoá nỗi đau ({', '.join(meta['pain_hits'][:2])})")
    if broke_long_aroll or dur > MAX_AROLL_RUN_SEC:
        parts.append(f"Luật D1: ngắt đoạn nói trơ để không vượt {MAX_AROLL_RUN_SEC:.0f}s")
    elif dur >= LONG_TALK_SEC:
        parts.append(f"Đoạn nói dài {dur:.2f}s ≥ {LONG_TALK_SEC:.0f}s")
    if meta["action_hits"]:
        parts.append(f"có bối cảnh/hành động ({', '.join(meta['action_hits'][:2])})")
    if for_coverage and not parts:
        parts.append("Luật D1: đảm bảo tỷ lệ B-Roll ≥ 25% thời lượng")
    elif for_coverage:
        parts.append("đạt độ phủ B-Roll ≥ 25%")
    return "; ".join(parts) if parts else "Chèn B-Roll giữ nhịp hình."


def plan_broll(
    blocks: list[dict[str, Any]],
    min_coverage: float = DEFAULT_MIN_COVERAGE,
    outputs: int = 2,
) -> dict[str, Any]:
    """Chấm điểm & chọn slot B-ROLL đảm bảo Luật D1 (không A-roll > 8s, B-roll >= min_coverage) và E2."""
    n = len(blocks)
    if n == 0:
        raise ValueError("Không có block nào để lập kế hoạch.")

    metas = [_score_block(b, i, n) for i, b in enumerate(blocks)]
    roles = ["A-ROLL"] * n
    broke_long = [False] * n
    for_cov = [False] * n

    # Pass 1: Cắt mọi chuỗi A-ROLL liên tiếp có span > MAX_AROLL_RUN_SEC (8.0s)
    while True:
        worst_span, worst_run = _max_aroll_run(blocks, roles)
        if worst_span <= MAX_AROLL_RUN_SEC or not worst_run:
            break
        candidates = [i for i in worst_run if i != 0] or worst_run
        pick = max(candidates, key=lambda i: metas[i]["score"])
        roles[pick] = "B-ROLL"
        broke_long[pick] = True

    total_video_dur = round(max(blocks[-1]["end"], sum(b["dur"] for b in blocks)), 3)
    total_spoken_dur = round(sum(b["dur"] for b in blocks), 3)

    def current_broll_dur() -> float:
        return sum(blocks[i]["dur"] for i, r in enumerate(roles) if r == "B-ROLL")

    # Pass 2: Ưu tiên các block chứa từ khoá nỗi đau (E2) nếu chưa quá dày và không kề B-roll
    pain_candidates = sorted(
        (i for i in range(1, n) if roles[i] == "A-ROLL" and metas[i]["pain_hits"]),
        key=lambda i: metas[i]["score"],
        reverse=True,
    )
    for i in pain_candidates:
        if i == n - 1 and metas[i]["cta_hits"]:
            continue
        adj_broll = (i > 0 and roles[i - 1] == "B-ROLL") or (i + 1 < n and roles[i + 1] == "B-ROLL")
        if adj_broll:
            continue
        if (current_broll_dur() + blocks[i]["dur"]) / max(0.1, total_video_dur) <= 0.60:
            roles[i] = "B-ROLL"

    # Pass 3: Đảm bảo tổng thời lượng B-Roll / video_duration >= min_coverage (mặc định 25%)
    while current_broll_dur() / max(0.1, total_video_dur) < min_coverage:
        avail = [i for i in range(n) if roles[i] == "A-ROLL"]
        if not avail:
            break
        non_hook_non_adj = [
            i for i in avail
            if i != 0 and not (i > 0 and roles[i - 1] == "B-ROLL") and not (i + 1 < n and roles[i + 1] == "B-ROLL")
        ]
        pool = non_hook_non_adj or [i for i in avail if i != 0] or avail
        pick = max(pool, key=lambda i: metas[i]["score"])
        roles[pick] = "B-ROLL"
        for_cov[pick] = True

    # Xây danh sách slots chuẩn
    slots: list[dict[str, Any]] = []
    aroll_idx = 0
    broll_idx = 0
    total_credits = 0
    aroll_dur = 0.0
    broll_dur = 0.0

    for i, (b, role, meta) in enumerate(zip(blocks, roles, metas)):
        slot_id = i + 1
        seq_prefix = f"{slot_id:02d}"
        vlen = round(b["dur"], 3)
        if role == "B-ROLL":
            broll_idx += 1
            role_id = f"b-roll-{broll_idx}"
            fsec = bf.flow_seconds(vlen)
            fcred = bf.flow_credits(fsec, outputs=outputs)
            total_credits += fcred
            broll_dur += vlen
            reason = _broll_reason(meta, vlen, broke_long[i], for_cov[i])
            if vlen + bf.VOICE_PAD > bf.FLOW_MAX_SEC:
                reason += f" (lưu ý: vượt {bf.FLOW_MAX_SEC}s tối đa của Flow, nên tách 2 cảnh chèn)"
            hint = _prompt_draft_hint(b["text"], meta)
        else:
            aroll_idx += 1
            role_id = f"a-roll-{aroll_idx}"
            fsec = 0
            fcred = 0
            aroll_dur += vlen
            reason = _aroll_reason(i, n, meta, vlen)
            hint = ""

        slots.append({
            "slot_id": slot_id,
            "seq_prefix": seq_prefix,
            "role": role,
            "role_id": role_id,
            "start": b["start"],
            "end": b["end"],
            "voice_len": vlen,
            "flow_seconds": fsec,
            "flow_credits_x2": fcred,
            "anchor_quote": b["text"],
            "pain_keywords": meta["pain_hits"],
            "score": meta["score"],
            "reason": reason,
            "prompt_draft_hint": hint,
        })

    max_run_after, _ = _max_aroll_run(blocks, roles)
    broll_pct = round((broll_dur / total_video_dur) * 100.0, 2) if total_video_dur > 0 else 0.0
    aroll_pct = round((aroll_dur / total_video_dur) * 100.0, 2) if total_video_dur > 0 else 0.0

    return {
        "video_duration": total_video_dur,
        "spoken_duration": total_spoken_dur,
        "aroll_duration": round(aroll_dur, 3),
        "broll_duration": round(broll_dur, 3),
        "aroll_pct": aroll_pct,
        "broll_pct": broll_pct,
        "target_broll_pct": round(min_coverage * 100.0, 1),
        "max_aroll_run_sec": max_run_after,
        "outputs": outputs,
        "total_credits_x2": total_credits,
        "broll_slots_count": broll_idx,
        "slots": slots,
    }


def render_plan_markdown(plan: dict[str, Any]) -> str:
    """Xuất bảng phân tích B-Roll dễ đọc cho người dùng và AI agent."""
    lines = [
        "# Kế hoạch chèn B-Roll từ Video (chuẩn D1 / E2 / H5)",
        "",
        f"- **Tổng thời lượng video:** `{plan['video_duration']:.2f} s` (thoại thực `{plan['spoken_duration']:.2f} s`)",
        f"- **Độ phủ B-Roll:** `{plan['broll_duration']:.2f} s` (**{plan['broll_pct']:.1f}%**, mục tiêu ≥ **{plan['target_broll_pct']:.1f}%**) · "
        f"**{plan['broll_slots_count']}** cảnh B-Roll",
        f"- **Đoạn A-Roll nói trơ dài nhất:** `{plan['max_aroll_run_sec']:.2f} s` (Luật D1: ≤ `{MAX_AROLL_RUN_SEC:.1f} s`)",
        f"- **Dự toán Google Flow (x{plan.get('outputs', 2)} bản 720p + nâng 1080p 1 bản chọn):** **{plan['total_credits_x2']} tín dụng**",
        "",
        "## Danh sách Slot trên Timeline",
        "",
        "| Slot | Vai trò | Thời gian (s) | Voice (s) | Flow (s) | Tín dụng | anchor_quote | Lý do |",
        "|---:|---|---:|---:|---:|---:|---|---|",
    ]
    for s in plan["slots"]:
        flow_col = f"{s['flow_seconds']}s" if s["role"] == "B-ROLL" else "—"
        cred_col = str(s["flow_credits_x2"]) if s["role"] == "B-ROLL" else "0"
        quote = s["anchor_quote"].replace("|", "\\|")
        reason = s["reason"].replace("|", "\\|")
        lines.append(
            f"| `{s['seq_prefix']}` (`{s['slot_id']}`) | **{s['role']}** (`{s['role_id']}`) | "
            f"{s['start']:.2f}–{s['end']:.2f} | {s['voice_len']:.2f} | {flow_col} | {cred_col} | {quote} | {reason} |"
        )

    broll_slots = [s for s in plan["slots"] if s["role"] == "B-ROLL"]
    if broll_slots:
        lines.extend(["", "## Gợi ý viết Prompt chuẩn H5 cho các slot B-Roll", ""])
        for s in broll_slots:
            lines.append(f"### Slot {s['slot_id']} (`{s['seq_prefix']}_{s['role_id']}.mp4`, Flow `{s['flow_seconds']}s`, `{s['flow_credits_x2']}` tín dụng)")
            lines.append(f"- **anchor_quote:** \"{s['anchor_quote']}\"")
            lines.append(f"- **Gợi ý khung H5:** {s['prompt_draft_hint']}")
            lines.append("")
    return "\n".join(lines) + "\n"


def _resolve_analyze_outputs(out_arg: Path) -> tuple[Path, Path, Path]:
    if out_arg.suffix.lower() == ".json":
        return out_arg.parent, out_arg, out_arg.with_suffix(".md")
    return out_arg, out_arg / "broll_plan.json", out_arg / "broll_plan.md"


def cmd_analyze(args: argparse.Namespace) -> int:
    work_dir, json_path, md_path = _resolve_analyze_outputs(Path(args.out))
    work_dir.mkdir(parents=True, exist_ok=True)

    if args.video:
        video_path = Path(args.video)
        if not video_path.is_file():
            print(f"[ANALYZE FAIL] Không thấy file video: {video_path}", file=sys.stderr)
            return 2
        transcript_path = _transcribe_video(video_path, work_dir, language=args.language)
    else:
        transcript_path = Path(args.transcript)
        if not transcript_path.is_file():
            print(f"[ANALYZE FAIL] Không thấy file transcript: {transcript_path}", file=sys.stderr)
            return 2

    try:
        transcript = _load_json(transcript_path)
        words = extract_words(transcript)
        blocks = build_blocks(words, min_seg=args.min_seg, max_seg=args.max_seg)
        plan = plan_broll(blocks, min_coverage=args.min_coverage, outputs=args.outputs)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as e:
        print(f"[ANALYZE FAIL] {e}", file=sys.stderr)
        return 2

    plan["source_transcript"] = str(transcript_path)
    _save_json(json_path, plan)
    md_path.write_text(render_plan_markdown(plan), encoding="utf-8")

    print(
        f"[PLAN OK] {len(plan['slots'])} slots ({plan['broll_slots_count']} B-ROLL, "
        f"{plan['broll_pct']:.1f}% ≥ {plan['target_broll_pct']:.1f}%), "
        f"max A-roll {plan['max_aroll_run_sec']:.2f}s, "
        f"tổng Flow x{plan['outputs']}: {plan['total_credits_x2']} tín dụng"
    )
    print(f"  JSON: {json_path}")
    print(f"  MD  : {md_path}")
    return 0


def check_prompts_against_plan(
    plan: dict[str, Any],
    prompts: list[dict[str, Any]],
    outputs: int | None = None,
) -> tuple[list[str], dict[str, Any]]:
    """Kiểm từng prompt ứng với anchor_quote của slot B-ROLL trong plan qua broll_fix.lint_prompt."""
    slots = plan.get("slots")
    if not isinstance(slots, list):
        raise ValueError("Plan thiếu danh sách slots.")
    if not isinstance(prompts, list):
        raise ValueError("File prompts phải là danh sách JSON [{slot_id, prompt, anchor_quote}, …].")

    out_count = outputs if outputs is not None else int(plan.get("outputs") or 2)
    broll_by_id = {int(s["slot_id"]): s for s in slots if s.get("role") == "B-ROLL"}
    all_by_id = {int(s["slot_id"]): s for s in slots}

    problems: list[str] = []
    seen_ids: set[int] = set()
    jobs: list[dict[str, Any]] = []
    total_secs = 0
    total_credits = 0

    for idx, entry in enumerate(prompts):
        if not isinstance(entry, dict):
            problems.append(f"mục {idx}: không phải object JSON")
            continue
        raw_id = entry.get("slot_id") if entry.get("slot_id") is not None else entry.get("seq")
        if raw_id is None:
            problems.append(f"mục {idx}: thiếu slot_id")
            continue
        try:
            sid = int(raw_id)
        except (TypeError, ValueError):
            problems.append(f"mục {idx}: slot_id không hợp lệ ({raw_id})")
            continue

        if sid not in all_by_id:
            problems.append(f"slot {sid}: không tồn tại trong broll_plan.json")
            continue
        if sid not in broll_by_id:
            problems.append(f"slot {sid}: là A-ROLL, không phải B-ROLL")
            continue
        if sid in seen_ids:
            problems.append(f"slot {sid}: bị trùng prompt")
            continue
        seen_ids.add(sid)

        slot = broll_by_id[sid]
        core = bf.core_of(str(entry.get("prompt") or ""))
        if str(entry.get("prompt") or "") != core:
            problems.append(f"slot {sid}: không nối đuôi '(Pure visual…)' khi gửi Google Flow")
        errs = bf.lint_prompt(core, tts_text=slot.get("anchor_quote", ""), anchor=entry.get("anchor_quote"))
        if errs:
            problems.extend(f"slot {sid}: {err}" for err in errs)
            continue

        fsec = bf.flow_seconds(float(slot.get("voice_len") or 4.0))
        fcred = bf.flow_credits(fsec, outputs=out_count)
        total_secs += fsec
        total_credits += fcred
        jobs.append({
            "slot_id": sid,
            "seq_prefix": slot["seq_prefix"],
            "role_id": slot["role_id"],
            "file_stem": f"{slot['seq_prefix']}_{slot['role_id']}",
            "start": slot["start"],
            "end": slot["end"],
            "voice_len": slot["voice_len"],
            "duration_seconds": fsec,
            "outputs": out_count,
            "credits": fcred,
            "model": "omni-flash",
            "aspect_ratio": "9:16",
            "upscale": "1080p",
            "anchor_quote": entry.get("anchor_quote"),
            "prompt": core,
        })

    for sid in sorted(broll_by_id):
        if sid not in seen_ids:
            problems.append(f"slot {sid}: thiếu prompt cho cảnh B-ROLL ({broll_by_id[sid]['role_id']})")

    jobs.sort(key=lambda j: j["slot_id"])
    ready = {
        "outputs": out_count,
        "total_jobs": len(jobs),
        "total_flow_seconds": total_secs,
        "total_credits": total_credits,
        "jobs": jobs,
    }
    return problems, ready


def cmd_check_prompts(args: argparse.Namespace) -> int:
    plan_path = Path(args.plan)
    prompts_path = Path(args.prompts)
    try:
        plan = _load_json(plan_path)
        prompts = _load_json(prompts_path)
        problems, ready = check_prompts_against_plan(plan, prompts, outputs=args.outputs)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as e:
        print(f"[H5 ERROR] đọc đầu vào: {e}", file=sys.stderr)
        return 2

    if problems:
        for p in problems:
            print(f"[H5 FAIL] {p}")
        print(f"{len(problems)} lỗi H5 — sửa prompt rồi chạy lại check-prompts.")
        return 1

    out_path = Path(args.out) if args.out else prompts_path.with_name(f"{prompts_path.stem}.flow_ready.json")
    _save_json(out_path, ready)
    print(
        f"[H5 OK] {ready['total_jobs']} prompt đạt chuẩn · "
        f"tổng thời lượng Flow: {ready['total_flow_seconds']}s · "
        f"tổng tín dụng (x{ready['outputs']}): {ready['total_credits']} tín dụng"
    )
    print(f"  Flow-ready JSON: {out_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Phân tích video/transcript tìm điểm chèn B-Roll & kiểm prompt H5 cho Google Flow.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_an = sub.add_parser("analyze", help="Phân tích transcript hoặc video thô → broll_plan.json & broll_plan.md")
    src = p_an.add_mutually_exclusive_group(required=True)
    src.add_argument("--transcript", help="Đường dẫn transcript JSON (Scribe/Whisper có word timestamps)")
    src.add_argument("--video", help="Đường dẫn file video thô (tự bóc bằng faster-whisper)")
    p_an.add_argument("--out", required=True, help="Thư mục đầu ra hoặc đường dẫn file .json")
    p_an.add_argument("--min-seg", type=float, default=DEFAULT_MIN_SEG, help="Độ dài tối thiểu mỗi block (mặc định 3.0s)")
    p_an.add_argument("--max-seg", type=float, default=DEFAULT_MAX_SEG, help="Độ dài tối đa mỗi block (mặc định 10.0s)")
    p_an.add_argument("--min-coverage", type=float, default=DEFAULT_MIN_COVERAGE, help="Tỷ lệ B-Roll tối thiểu (mặc định 0.25)")
    p_an.add_argument("--outputs", type=int, default=2, help="Số bản Flow dự toán mỗi cảnh (mặc định 2)")
    p_an.add_argument("--language", default="vi", help="Ngôn ngữ bóc băng khi truyền --video (mặc định vi)")
    p_an.set_defaults(fn=cmd_analyze)

    p_cp = sub.add_parser("check-prompts", help="Kiểm prompt H5 khớp anchor_quote và tính tín dụng Flow thực tế")
    p_cp.add_argument("--plan", required=True, help="Đường dẫn broll_plan.json")
    p_cp.add_argument("--prompts", required=True, help="Đường dẫn prompts.json")
    p_cp.add_argument("--out", help="Đường dẫn file Flow-ready JSON đầu ra")
    p_cp.add_argument("--outputs", type=int, default=None, help="Ghi đè số bản Flow mỗi cảnh (mặc định theo plan)")
    p_cp.set_defaults(fn=cmd_check_prompts)
    return ap


def main() -> int:
    ap = build_parser()
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
