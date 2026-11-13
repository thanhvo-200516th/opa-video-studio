"""Các luật chữ mở rộng cho edit schema (T6-1)."""
from __future__ import annotations

from . import segment, textmarks


def _err(code: str, msg: str, where: str) -> dict:
    return {"code": code, "msg": msg, "where": where}


def check_text(edit: dict, ctx: segment.Ctx) -> list[dict]:
    """Kiểm tra các quy tắc chữ trên toàn bộ bản edit theo context segment."""
    errors: list[dict] = []
    blocks = edit.get("blocks", [])

    for block in blocks:
        bid = block["id"]
        # Xác định min/max+1 của các chỉ số trong top+hero+bottom
        ranges = [block[k] for k in ("top", "hero", "bottom") if block.get(k)]
        if not ranges:
            continue
        a = min(r[0] for r in ranges)
        b = max(r[1] for r in ranges)

        # 1. Gọi segment.block_violations(ctx, a, b)
        for code, detail in segment.block_violations(ctx, a, b):
            errors.append(_err(code, f"block {bid}: {detail}", bid))

        # 2. Kiểm thêm ở hai biên trong thẻ (cuối top → đầu hero, cuối hero → đầu bottom)
        # mỗi biên chỉ báo một lần, ở block kết thúc tại biên đó; where = id block (thêm tên dòng nếu là lỗi biên dòng)
        lines = []
        if block.get("top"):
            lines.append(("top", block["top"]))
        if block.get("hero"):
            lines.append(("hero", block["hero"]))
        if block.get("bottom"):
            lines.append(("bottom", block["bottom"]))

        # 2. SENTENCE_IN_LINE: kiểm tra bên trong từng dòng (top, hero, bottom) nếu có ngắt câu (lvl >= 3)
        for line_name, (l0, l1) in lines:
            for k in range(l0, l1 - 1):
                if ctx.marks.words[k].lvl >= 3:
                    errors.append(_err("SENTENCE_IN_LINE", f"«{ctx.words[k]['w']}|{ctx.words[k + 1]['w']}»", f"{bid} {line_name}"))

        # 3. Kiểm ở các biên giữa các dòng trong thẻ (cuối top → đầu hero, cuối hero → đầu bottom)
        for i in range(len(lines) - 1):
            line_name, (l0, l1) = lines[i]
            next_name, (r0, r1) = lines[i + 1]
            edge_k = l1 - 1
            next_k = r0
            where_line = f"{bid} {line_name}"

            # COMPOUND_SPLIT nếu biên là cặp dính hoặc từ sau là trail
            is_glued = (ctx.marks.words[edge_k].lvl == 0 and textmarks.glued(ctx.marks, ctx.lex, edge_k))
            is_trail = textmarks.is_trail(ctx.marks, ctx.lex, next_k)
            if is_glued or is_trail:
                errors.append(_err("COMPOUND_SPLIT", f"«{ctx.words[edge_k]['w']}|{ctx.words[next_k]['w']}»", where_line))

        # 3. LINE_END_LEAD khi dòng hero kết thúc bằng từ dẫn mà block còn dòng bottom
        if block.get("hero") and block.get("bottom"):
            hero_end = block["hero"][1] - 1
            if ctx.marks.words[hero_end].lvl == 0 and textmarks.is_lead(ctx.marks, ctx.lex, hero_end):
                errors.append(_err("LINE_END_LEAD", f"«{ctx.words[hero_end]['w']}»", f"{bid} hero"))

        # 4. HERO_NO_CONTENT khi dòng hero không có từ nội dung nào
        # (dùng textmarks.weight/is_function; từ VIẾT HOA tính là nội dung)
        if block.get("hero"):
            h0, h1 = block["hero"]
            has_content = False
            for k in range(h0, h1):
                m = ctx.marks.words[k]
                if textmarks.is_caps(m.core):
                    has_content = True
                    break
                if not textmarks.is_function(ctx.marks, ctx.lex, k):
                    has_content = True
                    break
            if not has_content:
                errors.append(_err("HERO_NO_CONTENT", f"dòng hero không có từ nội dung nào", f"{bid} hero"))

    return errors


def dry_lock_errors(edit: dict, words: list[dict], pauses: dict, R, script: str | None = None) -> list[dict]:
    """LAST_WORD_TIGHT lấy từ khoá hình dựng với kế hoạch SFX RỖNG (đã kiểm: kết quả bằng
    đúng khoá dựng với kế hoạch thật trên canary)."""
    from . import picture
    lock = picture.build_lock(words, edit, {"cues": []}, pauses, R, script=script)
    return [
        {"code": "LAST_WORD_TIGHT", "msg": f"từ cuối block {w.split(':')[1]} không kịp đọc", "where": w.split(":")[1]}
        for w in lock.get("warnings", []) if w.startswith("LAST_WORD_TIGHT:")
    ]


WAIVABLE = {
    "SENTENCE_IN_LINE", "SENTENCE_INSIDE_BLOCK", "QUOTE_SPLIT", "COMPOUND_SPLIT",
    "LINE_END_LEAD", "HERO_NO_CONTENT", "BLOCK_LEN", "LAST_WORD_TIGHT"
}


def apply_waiver(errors: list[dict], reference_errors: list[dict] | None,
                 marks: textmarks.Marks | None = None,
                 edit: dict | None = None) -> tuple[list[dict], list[dict]]:
    """Trả (errors, notes). reference_errors = lỗi của BẢN ĐỀ XUẤT do code sinh (không chỉnh tay).
    None ⇒ không miễn gì (chế độ --legacy và test tay)."""
    if reference_errors is None:
        return list(errors), []

    # Xây dựng mapping từ block id (where) sang sent id nếu có marks và edit
    block_sent: dict[str, int] = {}
    if marks is not None and edit is not None and hasattr(marks, "words"):
        for block in edit.get("blocks", []):
            bid = block.get("id")
            ranges = [block[k] for k in ("top", "hero", "bottom") if block.get(k)]
            if ranges and bid:
                a = min(r[0] for r in ranges)
                if 0 <= a < len(marks.words):
                    block_sent[bid] = marks.words[a].sent

    def _err_key(e: dict) -> tuple[str, object]:
        code = e.get("code", "")
        where = e.get("where", "")
        # Nếu where bắt đầu bằng id block (vd 'b01' hoặc 'b01 hero')
        bid = str(where).split()[0] if where else ""
        if bid in block_sent:
            return (code, block_sent[bid])
        return (code, where)

    # Đếm quota từ reference_errors
    from collections import Counter
    ref_counts = Counter(_err_key(r) for r in reference_errors)

    kept: list[dict] = []
    notes: list[dict] = []

    for e in errors:
        code = e.get("code", "")
        key = _err_key(e)
        if code in WAIVABLE and ref_counts.get(key, 0) > 0:
            ref_counts[key] -= 1
            note_item = dict(e)
            note_item["note"] = "không tránh được — bản đề xuất cũng vậy"
            notes.append(note_item)
        else:
            kept.append(e)

    return kept, notes

