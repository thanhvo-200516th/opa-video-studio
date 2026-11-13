#!/usr/bin/env python3
"""Phân tích kết quả quét MP4 theo ngưỡng NN §1 (dùng bởi tools/v2w/metrics.py và tests/test_metrics.py).
Hai loại khoảng: declared (lặng khai báo: frame bỏ khỏi ngưỡng, ô 2 s chạm khoảng được tới 30 %) và exempt (miễn hẳn,
ví dụ khung CTA cuối của phim đủ: frame bỏ khỏi mọi ngưỡng, ô không bị luật 30 %)."""
from __future__ import annotations

import math

from scan_video import Scan

TINH_B, TINH_A = 0.005, 0.0004
CUT_SHARE = 0.30
WIN_S = 2.0
LIMIT_WINDOW, LIMIT_DECLARED_WINDOW, LIMIT_TOTAL, LIMIT_RUN_S = 0.15, 0.30, 0.10, 12 / 60
BASELINE_916 = 0.576  # Tĩnh B của bản 9:16 (CĐ)

Span = tuple[float, float]


def hard_cuts(sc: Scan) -> list[int]:
    """Frame có > 30 % điểm đổi so với f − 1, và f − 1, f + 1 đổi < 1/3 mức đó."""
    ch = [s.ch1 for s in sc.stats]
    return [i for i in range(1, len(ch) - 1)
            if ch[i] > CUT_SHARE and ch[i - 1] < ch[i] / 3 and ch[i + 1] < ch[i] / 3]


def window_bounds(times: list[float], fps: float) -> list[tuple[float, float, list[int]]]:
    """Ô 2 s căn giây chẵn của phim; ô ít hơn 1 s gộp vào ô kề (ô trước nếu có, không thì ô sau)."""
    groups: dict[int, list[int]] = {}
    for i, t in enumerate(times):
        groups.setdefault(math.floor(t / WIN_S + 1e-9), []).append(i)
    merged: list[list] = []
    for k, idx in sorted(groups.items()):
        w = [k * WIN_S, (k + 1) * WIN_S, idx]
        short_new = len(idx) < fps
        short_last = bool(merged) and len(merged[-1][2]) < fps
        if merged and (short_new or short_last):
            merged[-1] = [merged[-1][0], w[1], merged[-1][2] + idx]
        else:
            merged.append(w)
    return [(a, b, idx) for a, b, idx in merged]


def longest_run(flags: list[bool]) -> int:
    best = cur = 0
    for f in flags:
        cur = cur + 1 if f else 0
        best = max(best, cur)
    return best


def pct(x: float) -> float:
    return round(100 * x, 2)


def _window(sc: Scan, a: float, b: float, idx: list[int], ctx: dict) -> dict:
    valid, in_decl, in_skip, tinh_b, tinh_a = ctx["valid"], ctx["in_decl"], ctx["in_skip"], ctx["tinh_b"], ctx["tinh_a"]
    ok_idx = [i for i in idx if valid[i] and not ctx["in_exempt"][i]]
    eff = [i for i in ok_idx if not in_skip[i]]
    share_all = sum(tinh_b[i] for i in ok_idx) / max(1, len(ok_idx))
    share_eff = sum(tinh_b[i] for i in eff) / max(1, len(eff))
    touches = any(in_decl[i] for i in idx)
    d50 = sorted(sc.stats[i].disp50 for i in idx)
    return {
        "from": a, "to": b, "frames": len(idx), "tinhB": pct(share_all), "tinhBEff": pct(share_eff),
        "tinhA": sum(tinh_a[i] for i in eff), "meanChanged": pct(sum(sc.stats[i].ch1 for i in idx) / len(idx)),
        "dispP50": round(d50[len(d50) // 2], 2),
        "dispP95": round(max(sc.stats[i].disp95 for i in idx), 2),
        "dispMax": round(max(sc.stats[i].disp_max for i in idx), 2),
        "longestRun": longest_run([tinh_b[i] and not in_skip[i] for i in idx]), "declared": touches,
        "exempt": any(ctx["in_exempt"][i] for i in idx),
        "pass": not (share_eff > LIMIT_WINDOW or (touches and share_all > LIMIT_DECLARED_WINDOW)),
    }


def analyze(sc: Scan, t0: float, declared: list[Span], test: str, exempt: list[Span] | None = None) -> dict:
    """Báo cáo đủ: ô 2 s, cắt cứng, tổng, pass/fails. Frame khai báo/miễn bị loại khỏi ngưỡng nhưng vẫn được báo."""
    fps = sc.fps
    exempt = exempt or []
    times = [t0 + i / fps for i in range(len(sc.stats))]
    valid = [s.ch_lag is not None for s in sc.stats]
    in_decl = [any(a <= t < b for a, b in declared) for t in times]
    in_exempt = [any(a <= t < b for a, b in exempt) for t in times]
    ctx = {
        "valid": valid,
        "in_decl": in_decl,
        "in_exempt": in_exempt,
        "in_skip": [d or e for d, e in zip(in_decl, in_exempt)],
        "tinh_b": [v and s.ch_lag <= TINH_B for s, v in zip(sc.stats, valid)],
        "tinh_a": [v and s.ch_lag <= TINH_A for s, v in zip(sc.stats, valid)],
    }
    in_skip, tinh_b, tinh_a = ctx["in_skip"], ctx["tinh_b"], ctx["tinh_a"]
    windows = [_window(sc, a, b, idx, ctx) for a, b, idx in window_bounds(times, fps)]
    fails = [f"ô [{w['from']:g}; {w['to']:g}) Tĩnh B {w['tinhBEff']} % (cả ô {w['tinhB']} %)" for w in windows if not w["pass"]]
    eff_all = [i for i, v in enumerate(valid) if v and not in_skip[i]]
    total_b = sum(tinh_b[i] for i in eff_all) / max(1, len(eff_all))
    total_a = sum(tinh_a[i] for i in eff_all)
    run_all = longest_run([tb and not d for tb, d in zip(tinh_b, in_skip)])
    run_limit = round(LIMIT_RUN_S * fps)
    cuts = hard_cuts(sc)
    if total_b > LIMIT_TOTAL:
        fails.append(f"cả đoạn Tĩnh B {pct(total_b)} % > {pct(LIMIT_TOTAL)} %")
    if total_a > 0:
        fails.append(f"Tĩnh A {total_a} frame > 0")
    if run_all > run_limit:
        fails.append(f"chuỗi Tĩnh B dài nhất {run_all} f > {run_limit} f")
    if cuts:
        fails.append(f"{len(cuts)} cắt cứng ở frame {cuts}")
    return {
        "test": test, "t0": t0, "fps": fps, "frames": len(sc.stats), "width": sc.width, "height": sc.height,
        "windows": windows,
        "hardCuts": [{"frame": i, "t": round(times[i], 4), "share": pct(sc.stats[i].ch1)} for i in cuts],
        "declared": [{"from": a, "to": b} for a, b in declared],
        "exempt": [{"from": a, "to": b} for a, b in exempt],
        "totals": {"tinhB": pct(total_b), "tinhA": total_a, "longestRun": run_all, "runLimit": run_limit,
                   "maxDisp": round(max(s.disp95 for s in sc.stats), 2),
                   "maxDispRaw": round(max(s.disp_max for s in sc.stats), 2),
                   "meanChanged": pct(sum(s.ch1 for s in sc.stats) / len(sc.stats)),
                   "baseline916TinhB": pct(BASELINE_916)},
        "pass": not fails, "fails": fails, "warns": list(sc.warns),
    }


def markdown(r: dict) -> str:
    t = r["totals"]
    rows = "\n".join(
        f"| [{w['from']:g}; {w['to']:g}) | {w['frames']} | {w['tinhB']} | {w['tinhBEff']} | {w['tinhA']} | {w['meanChanged']} | "
        f"{w['dispP50']} | {w['dispP95']} | {w['dispMax']} | {w['longestRun']} | "
        f"{'khai báo' if w['declared'] else ''}{' miễn' if w.get('exempt') else ''} | "
        f"{'ĐẠT' if w['pass'] else 'TRƯỢT'} |" for w in r["windows"])
    fails = "\n".join(f"- {f}" for f in r["fails"]) or "- (không)"
    warns = "\n".join(f"- {w}" for w in r["warns"]) or "- (không)"
    return (f"# Chỉ số chuyển động {r['test']}\n\n"
            f"{r['frames']} frame · {r['fps']:g} fps · {r['width']}×{r['height']} · t0 {r['t0']:g} s · "
            f"**{'ĐẠT' if r['pass'] else 'TRƯỢT'}**\n\n"
            f"Cả đoạn: Tĩnh B {t['tinhB']} % (9:16: {t['baseline916TinhB']} %) · Tĩnh A {t['tinhA']} · "
            f"chuỗi tĩnh dài nhất {t['longestRun']} f (trần {t['runLimit']}) · độ dời lớn nhất {t['maxDisp']} px/frame "
            f"(P95 điểm bám; max thô {t['maxDispRaw']}) · "
            f"đổi TB {t['meanChanged']} % · cắt cứng {len(r['hardCuts'])}\n\n"
            "| Ô (s) | Frame | Tĩnh B % | Tĩnh B % (bỏ khai báo) | Tĩnh A | Đổi TB % | Dời P50 | Dời P95 | Dời max | "
            "Chuỗi tĩnh | Ghi chú | KQ |\n|---|---|---|---|---|---|---|---|---|---|---|---|\n"
            f"{rows}\n\n## Trượt\n{fails}\n\n## Cảnh báo\n{warns}\n")
