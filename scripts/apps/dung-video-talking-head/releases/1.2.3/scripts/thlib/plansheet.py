"""PLAN-SHEET 9 mục cho agent PLAN.
Sinh tài liệu Markdown duy nhất để agent đọc và điền plan.json.
"""
from __future__ import annotations

import json
from typing import Any

from . import textmarks


def _section_0_how_to() -> list[str]:
    """§0 Cách làm — đúng 5 dòng."""
    return [
        "## §0 Cách làm",
        "1. Đọc sheet này và xem kịch bản, các ứng viên cùng bảng thẻ đề xuất.",
        "2. Điền 6 ô ? trong plan.json (đồng ý bản đề xuất thì chép nguyên khối §8).",
        "3. Chạy đúng lệnh --check mà dòng NEXT của stage đã in (stage PLAN --check --task <id>).",
        "4. PASS thì đóng card; FAIL thì làm theo dòng Sửa:.",
        "5. Lặp lại tối đa 3 vòng để hoàn thiện.",
    ]


def _section_1_script_by_sentence(marks: Any, words: list[dict]) -> list[str]:
    """§1 Kịch bản theo câu, mỗi câu một dòng, kèm chỉ số từ đầu/cuối."""
    lines = ["## §1 Kịch bản theo câu"]
    sents = textmarks.sentences(marks)
    for a, b in sents:
        sent_words = [words[i]["w"] for i in range(a, b)]
        text = " ".join(sent_words)
        lines.append(f"[{a}–{b - 1}] {text}")
    return lines


def _format_block_row(b: dict, words: list[dict], marks: Any, shots: list[dict], notes: list[dict], R: Any) -> str:
    bid = b.get("id", "")
    ranges = [b[k] for k in ("top", "hero", "bottom") if b.get(k)]
    b_start = min(r[0] for r in ranges)
    b_end = max(r[1] for r in ranges)
    block_range = (b_start, b_end)

    t0 = float(words[b_start]["on"])
    t1 = float(words[b_end - 1]["e"])
    dur = t1 - t0

    # text shown
    parts = []
    style = b.get("style", "script")
    if b.get("top"):
        top_str = " ".join(textmarks.shown(marks, block_range, k, "script") for k in range(*b["top"]))
        parts.append(top_str)
    if b.get("hero"):
        hero_str = " ".join(textmarks.shown(marks, block_range, k, style) for k in range(*b["hero"]))
        parts.append(f"«{hero_str}»")
    if b.get("bottom"):
        bot_str = " ".join(textmarks.shown(marks, block_range, k, "script") for k in range(*b["bottom"]))
        parts.append(bot_str)
    shown_text = " / ".join(parts)

    # shot scale: W or C
    # Cỡ cảnh ở §2: W (toàn) khi max(s0, s1) < text.close_min (1.14), ngược lại C (cận).
    # Cảnh của một thẻ = shot có cut_at_word lớn nhất mà <= chỉ số từ đầu thẻ.
    close_min = float(R.get("text.close_min"))

    matching_shot = None
    for s in shots:
        cut_at = s.get("cut_at_word", 0)
        if cut_at <= b_start:
            if matching_shot is None or cut_at >= matching_shot.get("cut_at_word", 0):
                matching_shot = s

    scale_label = "W"
    if matching_shot is not None:
        s0 = float(matching_shot.get("s0", 1.0))
        s1 = float(matching_shot.get("s1", 1.0))
        if max(s0, s1) >= close_min:
            scale_label = "C"

    # Cảnh báo ⚠: thẻ có GHI CHÚ trong notes hoặc cặp từ lạ / ngoặc bị cắt
    warn = False
    for n in notes:
        where = str(n.get("where", ""))
        if where == bid or where.startswith(bid + " ") or where.startswith(f"blocks[{bid}]"):
            warn = True
            break

    warn_str = " ⚠" if warn else ""
    return f"{bid}{warn_str} | [{b_start},{b_end}) | {dur:.2f}s | {shown_text} | {scale_label}"


def _section_2_blocks_table(edit: dict, words: list[dict], marks: Any, R: Any, notes: Any = ()) -> list[str]:
    """§2 Bảng thẻ đề xuất."""
    lines = ["## §2 Bảng thẻ đề xuất"]
    shots = edit.get("shots", [])

    for b in edit.get("blocks", []):
        row = _format_block_row(b, words, marks, shots, list(notes), R)
        lines.append(row)
        # Các phương án thay thế nếu có
        alts = b.get("alts", [])
        for alt in alts[:2]:
            lines.append(f"  alt: {alt}")
    return lines


def _section_3_hook_window(words: list[dict], R: Any) -> list[str]:
    """§3 Cửa sổ hook — mọi từ có onset <= sfx.hook_window_s."""
    lines = ["## §3 Cửa sổ hook"]
    hook_win = float(R.get("sfx.hook_window_s"))
    items = []
    for k, w in enumerate(words):
        onset = float(w["on"])
        if onset <= hook_win:
            items.append(f"{k}:{w['w']} ({onset:.2f}s)")
    lines.append(", ".join(items))
    return lines


def _section_4_cands_h(cands: dict, words: list[dict]) -> list[str]:
    """§4 Ứng viên H — mỗi ứng viên một dòng: id | [a,b) | chữ | lý do | thuộc tính riêng."""
    lines = ["## §4 Ứng viên H"]
    for h in cands.get("H", []):
        hid = h.get("id", "")
        rng = h.get("range", [])
        r_str = f"[{rng[0]},{rng[1]})" if rng else ""
        text = h.get("text", "")
        why = h.get("why", "")
        color = h.get("color", "")
        forces = f"forces={h.get('forces')}" if h.get("forces") else ""
        props = ", ".join(p for p in (color, forces) if p)
        lines.append(f"{hid} | {r_str} | {text} | {why} | {props}")
    return lines


def _section_5_cands_kqv(cands: dict, words: list[dict], R: Any) -> list[str]:
    """§5 Ứng viên K/Q/V (ghi rõ xung đột khoảng cách sfx.stomp_s nếu có)."""
    lines = ["## §5 Ứng viên K/Q/V"]
    stomp_s = float(R.get("sfx.stomp_s"))

    kq_cands = cands.get("K", []) + cands.get("Q", [])
    all_kqv = kq_cands + cands.get("V", [])
    for idx, c in enumerate(all_kqv):
        cid = c.get("id", "")
        rng = c.get("range", [])
        r_str = f"[{rng[0]},{rng[1]})" if rng else ""
        text = c.get("text", "")
        why = c.get("why", "")
        rank = f"rank={c.get('rank')}" if "rank" in c else ""
        onset = float(c.get("onset", 0.0))

        # Check khoảng cách: chỉ tính giữa K và Q với nhau. V không in phần xung đột.
        if cid.startswith("V"):
            props = rank
        else:
            conflicts = []
            for other in kq_cands:
                if other["id"] != cid and "onset" in other:
                    other_onset = float(other["onset"])
                    diff = abs(onset - other_onset)
                    if diff < stomp_s:
                        conflicts.append(f"{other['id']} ({diff:.1f}s < {stomp_s}s)")
            conflict_str = f"xung đột: {', '.join(conflicts)}" if conflicts else ""
            props = ", ".join(p for p in (rank, conflict_str) if p)
        lines.append(f"{cid} | {r_str} | {text} | {why} | {props}" if props else f"{cid} | {r_str} | {text} | {why}")
    return lines


def _section_6_cands_s(cands: dict, words: list[dict]) -> list[str]:
    """§6 Ứng viên S — mỗi ứng viên một dòng."""
    lines = ["## §6 Ứng viên S"]
    for s in cands.get("S", []):
        sid = s.get("id", "")
        rng = s.get("range", [])
        r_str = f"[{rng[0]},{rng[1]})" if rng else ""
        title = s.get("title", "")
        why = "danh sách liệt kê"
        rec = "đề xuất" if s.get("recommended") else "không đề xuất"
        labels = "; ".join(s.get("labels", []))
        props = f"{rec}, tiêu đề: {title}, nhãn: [{labels}]"
        lines.append(f"{sid} | {r_str} | {title} | {why} | {props}")
    return lines


def _section_7_cands_c(cands: dict, words: list[dict]) -> list[str]:
    """§7 Ứng viên C — mỗi ứng viên một dòng."""
    lines = ["## §7 Ứng viên C"]
    for c in cands.get("C", []):
        cid = c.get("id", "")
        rng = c.get("range", [])
        r_str = f"[{rng[0]},{rng[1]})" if rng else ""
        label = c.get("label", "")
        kw = c.get("keyword", "")
        text = f"{label} {kw}"
        why = "lời kêu gọi hành động CTA"
        props = f"label={label}, keyword={kw}"
        lines.append(f"{cid} | {r_str} | {text} | {why} | {props}")
    return lines


def _section_b_broll(broll: dict) -> list[str]:
    """§B Ô B-roll (spec 1.2.0 §4.6, §B)."""
    cls = broll.get("class", "none")
    pct = lambda x: f"{round(x * 100)} %"
    num = lambda x: f"{x:g}".replace(".", ",")
    lines = [
        f"## §B Ô B-roll (video {cls}; phủ cần {round(broll['floor'] * 100)}–{pct(broll['cover_max'])} "
        f"(đề xuất §8 phủ {pct(broll['rec_cover'])}), tối đa {broll['cap_n']} ô, cách nhau ≥ {num(broll['gap'])} s; "
        f"tối đa {broll['max_clips']} clip)",
        "| id | thời gian | dài | câu | dùng được | điểm | neo PREP |",
    ]
    for r in broll.get("rows", []):
        rid = r["id"]
        t_str = f"{r['t_in']:.2f}–{r['t_out']:.2f} s"
        dur_str = f"{r['dur']:.2f} s"
        text = r["text"]
        usable = "có" if r["zone"] is None else f"vướng {r['zone']}"
        score = r["score"]
        if r["asset"] is not None:
            a_idx = r["asset"]
            assets = broll.get("assets", [])
            desc = assets[a_idx].get("desc", "") if a_idx < len(assets) else ""
            prep_str = f"#{a_idx} «{desc}»"
        else:
            prep_str = "—"
        lines.append(f"| {rid} | {t_str} | {dur_str} | {text} | {usable} | {score} | {prep_str} |")

    recs = broll.get("recommended", [])
    rec_str = ", ".join(recs) if recs else "không"
    lines.append(f"Đề xuất: {rec_str}.")
    lines.append("Cách viết prompt (mỗi ô đã chọn): TIẾNG ANH, 8–60 từ, tả CẢNH minh hoạ đúng câu đang nói — người/vật, hành động, bối cảnh, ánh sáng.")
    lines.append("Đừng viết chữ trên hình, logo, watermark, tên thương hiệu hay \"no text\" (code tự thêm câu phong cách). Ảnh AI chỉ minh hoạ, KHÔNG")
    lines.append("làm bằng chứng cho con số hay kết quả thật. \"clip\" chỉ cho ô quan trọng nhất (≥ 2 s).")
    lines.append("Nhiều ô nói về CÙNG một sản phẩm/đối tượng ⇒ chọn một cụm mô tả cụ thể (tả cả dáng + màu, vd «a smartwatch with a square black case and black sport band») và chép NGUYÊN cụm đó vào prompt mọi ô ấy; không viết tên hãng/thiết bị có thương hiệu — viết «a smartphone», «a laptop».")

    for i, a in enumerate(broll.get("assets", [])):
        kind = a.get("kind", "")
        desc = a.get("desc", "")
        anchor = a.get("anchor_quote", "")
        lines.append(f"#{i} {kind} — {desc} — neo: «{anchor}»")

    return lines


def _section_8_paste_json(plan: dict, cands: dict, words: list[dict], R: Any) -> list[str]:
    """§8 Khối JSON dán được và 7 việc phải quyết."""
    lines = ["## §8 Khối JSON dán được và 7 việc phải quyết"]
    # Chuẩn hoá plan hợp lệ cho check_plan
    from .compose import draft_plan
    # Nếu plan là recommended plan (hoặc đã điền), ta lấy các giá trị điền được
    # Đảm bảo có schema plan/2 và words_sha
    # steps_labels: lấy labels của ứng viên S đang chọn; không có thẻ liệt kê thì mới null
    chosen_s_id = plan.get("steps")
    s_cands = cands.get("S", [])
    s_obj = next((s for s in s_cands if s.get("id") == chosen_s_id), None) if chosen_s_id else None
    steps_labels = plan.get("steps_labels")
    if steps_labels is None and s_obj:
        steps_labels = s_obj.get("labels")

    out_plan = {
        "schema": "plan/2",
        "words_sha": plan.get("words_sha") or draft_plan({}, words)["words_sha"],
        "hook": plan.get("hook"),
        "emphasis": plan.get("emphasis", []),
        "steps": plan.get("steps"),
        "cta": plan.get("cta"),
        "hero": plan.get("hero", []),
        "breaks": plan.get("breaks", []),
        "no_emphasis_reason": plan.get("no_emphasis_reason", ""),
        "flags": plan.get("flags", []),
        "steps_title": plan.get("steps_title") or (s_obj.get("title") if s_obj else None),
        "steps_labels": steps_labels,
        "cta_label": plan.get("cta_label"),
        "cta_keyword": plan.get("cta_keyword"),
        "broll": plan.get("broll", []),
    }
    json_str = json.dumps(out_plan, ensure_ascii=False, indent=2)
    lines.append("```json")
    lines.extend(json_str.split("\n"))
    lines.append("```")

    lines.append("7 việc phải quyết:")
    emph_min_s = float(R.get("plan.emphasis_min_video_s"))
    lines.append("1. hook: chọn ứng viên H hoặc null.")
    lines.append(f"2. điểm nhấn emphasis: video ≥ {emph_min_s:.1f}s thì cần ≥ 1 điểm nhấn, hoặc ghi lý do vào no_emphasis_reason.")
    lines.append("3. thẻ liệt kê steps: chỉ chọn ứng viên S ghi «đề xuất» (kèm tiêu đề và nhãn); S «không đề xuất» "
                 "thì để null — thẻ chỉ hiện 3 dòng (Q1), chọn vào thường làm thẻ khác quá ngắn hoặc đè mặt.")
    lines.append("4. CTA: chọn ứng viên C hoặc null.")
    lines.append("5. cột HERO: thay hero yếu bằng phương án đã liệt kê.")
    lines.append("6. đọc lại mạch chữ: chỗ nào còn gợn thì ghi vào flags.")
    lines.append("7. B-roll: giữ các ô đề xuất trong \"broll\" (hoặc đổi id theo §B), thay MỌI \"prompt\": \"?\" bằng prompt tiếng Anh; video không có §B thì để \"broll\": [].")
    return lines


def render_sheet(
    cands: dict,
    plan: dict,
    edit: dict,
    words: list[dict],
    marks: Any,
    R: Any,
    notes: Any = (),
    broll: dict | None = None,
) -> str:
    """Dựng chuỗi Markdown (kèm mục §B nếu broll != None)."""
    lines: list[str] = []
    lines.extend(_section_0_how_to())
    lines.extend(_section_1_script_by_sentence(marks, words))
    lines.extend(_section_2_blocks_table(edit, words, marks, R, notes=notes))
    lines.extend(_section_3_hook_window(words, R))
    lines.extend(_section_4_cands_h(cands, words))
    lines.extend(_section_5_cands_kqv(cands, words, R))
    lines.extend(_section_6_cands_s(cands, words))
    lines.extend(_section_7_cands_c(cands, words))
    if broll:
        lines.extend(_section_b_broll(broll))
    lines.extend(_section_8_paste_json(plan, cands, words, R))
    return "\n".join(lines)
