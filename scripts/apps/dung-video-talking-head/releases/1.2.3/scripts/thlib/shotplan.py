"""thlib.shotplan — Xếp cảnh cắt (shot planning) theo quy hoạch động (DP).

Spec 1.1.1 §4.7, sửa lỗi G11-1.
"""
from __future__ import annotations

import math
from typing import Any

from . import editschema


_TOL = 1e-6


def _pause_dist(t: float, pauses: list) -> float:
    return min(
        (max(float(t0) - t, t - float(t1), 0.0) for t0, t1 in pauses),
        default=float("inf"),
    )


def plan_shots(
    ctx: Any,
    blocks: list[dict],
    emphasis: list[dict] | None = None,
    steps: dict | None = None,
    cta: dict | None = None,
) -> list[dict]:
    """Lập danh sách shot cho video theo quy hoạch động (DP).

    Trả về list dict shot:
    {"cut_at_word": int, "s0": float, "s1": float, "x": 0.0, "y": 0.0}
    """
    R = ctx.R
    W = ctx.words
    n = len(W)
    if n == 0:
        raise RuntimeError("SHOT_INFEASIBLE: words is empty")

    on = [float(w["on"]) for w in W]
    pauses = getattr(ctx, "pauses", None)
    if pauses is None:
        # Nếu ctx không có pauses, thử lấy từ marks hoặc thuộc tính khác
        pauses_list = getattr(getattr(ctx, "marks", None), "pauses", None)
        if pauses_list is None:
            # Fallback nếu marks chứa pause list
            pauses_list = []
    else:
        pauses_list = pauses.get("pauses", []) if isinstance(pauses, dict) else pauses

    gap_lo = float(R.get("text.shot_gap_min_s"))
    gap_hi = float(R.get("text.shot_gap_max_s"))
    near = float(R.get("sfx.cut_near_s"))
    ideal_gap_s = float(R.get("plan.shot.ideal_gap_s"))
    gap_weight = float(R.get("plan.shot.gap_weight"))
    block_start_bonus = float(R.get("plan.shot.block_start_bonus"))
    sentence_start_bonus = float(R.get("plan.shot.sentence_start_bonus"))
    emphasis_start_bonus = float(R.get("plan.shot.emphasis_start_bonus"))
    cta_push_bonus = float(R.get("plan.shot.cta_push_bonus"))
    forced_cost = float(R.get("plan.shot.forced_off_pause_cost"))

    same_scale_pen = float(R.get("plan.shot.same_scale_pen"))
    two_row_close_pen = float(R.get("plan.shot.two_row_close_pen"))
    two_row_chars = int(R.get("plan.shot.two_row_chars"))

    scale_wide = [float(x) for x in R.get("plan.shot.wide")]
    scale_close = [float(x) for x in R.get("plan.shot.close")]
    scale_steps = [float(x) for x in R.get("plan.shot.steps")]
    scale_cta = [float(x) for x in R.get("plan.shot.cta_push")]

    t_end = float(ctx.t_end)

    # Tập các mốc quan trọng để thưởng
    block_starts = set()
    for b in blocks:
        rngs = [b[k] for k in ("top", "hero", "bottom") if b.get(k)]
        if rngs:
            block_starts.add(min(r[0] for r in rngs))

    sent_starts = set()
    if hasattr(ctx, "marks") and hasattr(ctx.marks, "words"):
        for k, mw in enumerate(ctx.marks.words):
            if getattr(mw, "lvl", 0) >= 3 and k + 1 < n:
                sent_starts.add(k + 1)
        if n > 0:
            sent_starts.add(0)

    emph_starts = set()
    if emphasis:
        for em in emphasis:
            if "range" in em:
                emph_starts.add(em["range"][0])
            elif "start" in em:
                emph_starts.add(em["start"])

    cta_start = None
    if cta and cta.get("range"):
        cta_start = cta["range"][0]

    # Xác định snap-valid cho từng từ k >= 1
    # Node 0 luôn là shot mở đầu (t=0)
    snap_valid = [False] * n
    pause_dists = [0.0] * n
    for k in range(1, n):
        d = _pause_dist(on[k], pauses_list)
        pause_dists[k] = d
        if d <= near + _TOL:
            snap_valid[k] = True

    # Tìm đường đi ngắn nhất (cắt word indices)
    # best[k] = (cost, off_pause_count, prev_node)
    # Ta muốn cực tiểu hóa cost, với cost phạt forced_off_pause_cost cho cú cắt lệch
    # Chú ý luật off-pause:
    # "Từ lệch khoảng ngắt chỉ thành nút khi trong cửa sổ [t_prev + shot_gap_min_s, t_prev + shot_gap_max_s]
    #  không còn nút hợp lệ nào; nút kiểu đó chịu phạt plan.shot.forced_off_pause_cost."

    # DP DAG theo từ: từ 0 tới terminal nodes
    # best state tại node c: (total_cost, prev_node, is_forced)
    # Vì điều kiện forced phụ thuộc vào prev p:
    # Với một cặp (p, c):
    # tp = on[p] if p != 0 else 0.0
    # g = on[c] - tp
    # g phải trong [gap_lo - _TOL, gap_hi + _TOL]
    # Nếu snap_valid[c]:
    #   hợp lệ
    # Nếu not snap_valid[c]:
    #   chỉ hợp lệ nếu KHÔNG có từ s nào có snap_valid[s] và gap_lo - _TOL <= on[s] - tp <= gap_hi + _TOL!

    best: dict[int, tuple[float, int | None, bool]] = {0: (0.0, None, False)}
    # Duyệt các ứng viên c từ 1 đến n-1
    for c in range(1, n):
        tc = on[c]
        opts = []
        is_snap = snap_valid[c]

        # Kiểm tra mọi p đã đến được
        for p, (prev_cost, _, _) in list(best.items()):
            tp = on[p] if p != 0 else 0.0
            g = tc - tp
            if not (gap_lo - _TOL <= g <= gap_hi + _TOL):
                continue

            if is_snap:
                # Node hợp lệ
                node_cost = (
                    pause_dists[c] / near
                    + gap_weight * abs(g - ideal_gap_s)
                    - (block_start_bonus if c in block_starts else 0.0)
                    - (sentence_start_bonus if c in sent_starts else 0.0)
                    - (emphasis_start_bonus if c in emph_starts else 0.0)
                )
                opts.append((prev_cost + node_cost, p, False))
            else:
                # Kiểm tra trong [tp + gap_lo, tp + gap_hi] có từ snap-valid nào không
                has_snap_in_window = any(
                    snap_valid[s]
                    for s in range(1, n)
                    if gap_lo - _TOL <= on[s] - tp <= gap_hi + _TOL
                )
                if not has_snap_in_window:
                    # Được phép làm forced off-pause node
                    # Block start được ưu tiên giữa các forced off-pause
                    pref_bonus = block_start_bonus if c in block_starts else 0.0
                    node_cost = (
                        forced_cost
                        + pause_dists[c] / near
                        + gap_weight * abs(g - ideal_gap_s)
                        - pref_bonus
                        - (sentence_start_bonus if c in sent_starts else 0.0)
                        - (emphasis_start_bonus if c in emph_starts else 0.0)
                    )
                    opts.append((prev_cost + node_cost, p, True))

        if opts:
            best[c] = min(opts, key=lambda x: x[0])

    # Tìm terminal node:
    # "nút cách t_end không quá 4 giây, hoặc nút từ cta.range[0] trở đi; nút đúng đầu CTA được thưởng cta_push_bonus."
    terminals = []
    for c, (cost, prev, is_f) in best.items():
        tc = on[c] if c != 0 else 0.0
        is_term = False
        cta_bonus = 0.0
        if t_end - tc <= gap_hi + _TOL:
            is_term = True
        if cta_start is not None and c >= cta_start:
            is_term = True
            if c == cta_start:
                cta_bonus = cta_push_bonus

        if is_term:
            terminals.append((cost - cta_bonus, c))

    if not terminals:
        raise RuntimeError("SHOT_INFEASIBLE: no feasible shot cut sequence found")

    _, end_node = min(terminals, key=lambda x: x[0])

    # Reconstruct cuts
    cuts = []
    curr = end_node
    while curr is not None:
        cuts.append(curr)
        curr = best[curr][1]
    cuts.reverse()

    # DP cỡ cảnh (Scales DP)
    # 2 trạng thái: W (wide) và C (close)
    # Thẻ hero > two_row_chars (12) ký tự:
    # "phạt two_row_close_pen cho thẻ có hero dài hơn two_row_chars (12) ký tự mà mở đầu trong cảnh cận"
    # "mọi shot chồng lấn khoảng thẻ liệt kê ép về plan.shot.steps [1.18,1.22]"
    # "shot CTA dùng plan.shot.cta_push [1.06,1.20]"

    # Xác định các block có hero > 12 ký tự
    two_row_block_starts = set()
    for b in blocks:
        hero_rng = b.get("hero")
        if hero_rng:
            h_words = [W[k]["w"] for k in range(hero_rng[0], hero_rng[1])]
            # tính độ dài ký tự hiển thị (tính cả display nếu có)
            disp = b.get("display") or {}
            h_text = " ".join(disp.get(str(k), W[k]["w"]) for k in range(hero_rng[0], hero_rng[1]))
            if len(h_text) > two_row_chars:
                b_start = min(b[k][0] for k in ("top", "hero", "bottom") if b.get(k))
                two_row_block_starts.add(b_start)

    # Khoảng thẻ liệt kê steps: [on(first item), e(last item)]
    steps_span = None
    if steps and steps.get("items"):
        s_on = float(W[steps["items"][0]["range"][0]]["on"])
        s_e = float(W[steps["items"][-1]["range"][1] - 1]["e"])
        steps_span = (s_on, s_e)

    num_shots = len(cuts)
    shot_spans = []
    for i in range(num_shots):
        t0 = on[cuts[i]] if i > 0 else 0.0
        t1 = on[cuts[i + 1]] if i + 1 < num_shots else t_end
        shot_spans.append((t0, t1))

    # DP chọn state cho từng shot i = 0..num_shots-1
    # state: 0 (Wide), 1 (Close)
    # Nếu shot là CTA shot: ép về cta_push
    # Nếu shot chồng lấn steps: ép về steps
    # Ngược lại: DP giữa W và C
    dp_best = [{0: (0.0, None), 1: (0.0, None)}]

    for i in range(num_shots):
        t0, t1 = shot_spans[i]
        c_word = cuts[i]
        next_word = cuts[i + 1] if i + 1 < num_shots else n

        # Số block 2-row bắt đầu trong shot i
        two_row_count = sum(
            1 for bs in two_row_block_starts
            if c_word <= bs < next_word
        )

        row = {}
        for s in (0, 1): # 0: Wide, 1: Close
            cost_s = (two_row_close_pen * two_row_count) if s == 1 else 0.0
            if i == 0:
                row[s] = (cost_s, None)
            else:
                opts = []
                for prev_s in (0, 1):
                    pen = same_scale_pen if prev_s == s else 0.0
                    opts.append((dp_best[i - 1][prev_s][0] + pen + cost_s, prev_s))
                row[s] = min(opts, key=lambda x: x[0])
        dp_best.append(row)

    # Backtrack
    last_state = min((0, 1), key=lambda s: dp_best[num_shots][s][0])
    chosen_states = []
    curr_s = last_state
    for i in range(num_shots, 0, -1):
        chosen_states.append(curr_s)
        curr_s = dp_best[i][curr_s][1]
    chosen_states.reverse()

    shots = []
    for i, (cut_w, state) in enumerate(zip(cuts, chosen_states)):
        t0, t1 = shot_spans[i]
        # Kiểm tra CTA shot: từ cta_start trở đi hoặc shot cuối nếu cta_start
        is_cta_shot = (cta_start is not None and cut_w >= cta_start)
        # Kiểm tra steps overlap:
        is_steps_shot = False
        if steps_span:
            if max(t0, steps_span[0]) < min(t1, steps_span[1]) - _TOL:
                is_steps_shot = True

        if is_cta_shot:
            s0, s1 = scale_cta[0], scale_cta[1]
        elif is_steps_shot:
            s0, s1 = scale_steps[0], scale_steps[1]
        elif state == 1:
            s0, s1 = scale_close[0], scale_close[1]
        else:
            s0, s1 = scale_wide[0], scale_wide[1]

        shots.append({
            "cut_at_word": cut_w,
            "s0": s0,
            "s1": s1,
            "x": 0.0,
            "y": 0.0,
        })

    return shots
