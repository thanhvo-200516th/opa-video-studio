"""Sonic logo OPA (TK §7.4, KH §3.9). Synth brass mềm của voices.brass; KHÔNG pad, KHÔNG sub (sub là sub-drop #2).

(a) E5 (0) – A4 (½ phách) – C#5 (1 phách, giữ 1,2 s) + từ 1 phách brass C#4–E4–B4. (c) quãng 5 A3 → E4.
Attack 40 ms; LP đóng 2400 → 900 Hz trong 2 s; vang IR 2 s wet 22 %; nhả ở 1,7 s, đuôi tự nhiên ≈ 1,87 s
(< −60 dBFS ở ≈ 3,57 s, tức ≈ f842 khi đặt ở f735: lấp tới cửa sổ allowed − 10 f của QA #5, tắt trước f846).
Clip dài 3,7 s, fade 50 ms cuối chỉ là an toàn. anchor 0 = onset nốt đầu.
"""
from __future__ import annotations

import numpy as np

import dsp
import synth
import voices
from dsp import SR
from synth import Clip

BEAT_S = 0.5                    # 120 BPM (beatFrames 15 / 30 fps)
GATE_SHORT_S = 0.22             # nốt ½ phách, ngắt nhẹ trước nốt sau
HOLD_S = 1.2                    # C#5 giữ 1,2 s
ATTACK_S = 0.04
LP_FROM, LP_TO, LP_CLOSE_S = 2400.0, 900.0, 2.0
IR_S, IR_DECAY, WET = 2.0, 2.0, 0.22   # decay 2,0: đuôi tắt ≈ f842 (decay 4,0 tắt ≈ f818 → lặng lạ trước 840)
CLIP_S, FADE_S = 3.7, 0.05      # nhả 1,7 s + đuôi ≤ 2,0 s; fade cuối chỉ là an toàn (đuôi đã < −60 dBFS)
REF_LUFS = -20.0                # REF của mixbus (E), chỉ dùng cho logo_stem để nghe

# (nốt, bắt đầu s, giữ s)
MELODY = {
    "a": (("E5", 0.0, GATE_SHORT_S), ("A4", BEAT_S / 2, GATE_SHORT_S), ("C#5", BEAT_S, HOLD_S),
          ("C#4", BEAT_S, HOLD_S), ("E4", BEAT_S, HOLD_S), ("B4", BEAT_S, HOLD_S)),
    "c": (("A3", 0.0, GATE_SHORT_S), ("E4", BEAT_S / 2, BEAT_S / 2 + HOLD_S)),
}


def sonic_logo(variant: str = "a", seed: str = "sonic-logo") -> Clip:
    """Clip sonic logo (a) hoặc (c), đỉnh −1 dBFS, anchor 0."""
    if variant not in MELODY:
        raise ValueError(f"sonic_logo: biến thể không hỗ trợ {variant!r}")
    n = int(round(CLIP_S * SR))
    x = voices.brass(list(MELODY[variant]), attack_s=ATTACK_S, seed=f"{seed}:brass")
    x = np.concatenate([x, np.zeros(max(0, n - len(x)))])[:n]
    x = dsp.sweep_filter(x, [LP_FROM, LP_TO, LP_TO], [0.0, LP_CLOSE_S / CLIP_S, 1.0], "low")
    x = dsp.reverb(x, dsp.reverb_ir(f"{seed}:ir", dur_s=IR_S, decay=IR_DECAY, lp_fc=5000.0), WET)[:n]
    x = dsp.fade_edges(x, 0.0, FADE_S * 1000)
    return Clip(dsp.peak_norm(x, synth.PEAK_DBFS), 0)


def logo_stem(variant: str, sheet: dict) -> np.ndarray:
    """hit-logo + subdrop-logo + sonic logo theo gainDb tương đối của cue (gain = REF + gainDb − momentary max).

    Để nghe, xấp xỉ: seed theo quy ước render_cue (f"{id sheet}:{id cue}"), đỉnh chuẩn −1 dBFS.
    """
    sid = sheet["id"]
    ev = {e["id"]: e for e in sheet["events"]}
    missing = [k for k in ("hit-logo", "subdrop-logo", "sonic-logo") if k not in ev]
    if missing:
        raise ValueError(f"logo_stem: sheet thiếu cue {missing}")
    parts = [(synth.render_cue(ev["hit-logo"], sid), ev["hit-logo"]),
             (synth.render_cue(ev["subdrop-logo"], sid), ev["subdrop-logo"]),
             (sonic_logo(variant, f"{sid}:sonic-logo"), ev["sonic-logo"])]
    f0 = min(e["f"] for _, e in parts)
    starts = [dsp.f2s(e["f"] - f0) - c.anchor for c, e in parts]
    base = -min(starts)
    out = np.zeros(base + max(s + len(c.x) for (c, _), s in zip(parts, starts)))
    for (c, e), s in zip(parts, starts):
        g = 10 ** ((REF_LUFS + e["gainDb"] - dsp.momentary_max(c.x)) / 20)
        out[base + s:base + s + len(c.x)] += c.x * g
    return dsp.peak_norm(out, synth.PEAK_DBFS)
