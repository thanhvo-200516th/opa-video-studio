"""thlib.planner — bộ xếp tiếng SFX tất định (S01–S27, §5.7).

Port từ `prototype/planner_v11.py` (dòng 64–334) thành hàm thuần: mọi trị số
đọc từ `rules.json` (`sfx.*`, `presets.<preset>`), tín hiệu đọc qua
`sfxlib.load_signal` (không còn file .npy), không đụng đĩa và không dùng đồng
hồ — cùng đầu vào cho ra sfx_plan y hệt.

Đầu ra `plan()`:
  * `sfx_plan` (dict) đúng Data Contracts — mọi số thực đã làm tròn 4 số lẻ;
  * `cues_audio` — [{"start_s": float, "samples": np.ndarray}] cho mix.render_stem
    (giữ nguyên độ chính xác, không làm tròn, để đặt mẫu đúng vị trí).
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field

import numpy as np

from . import audio as A
from . import editschema
from . import rules as rules_lib
from .rules import Rules

# Sàn độ dài fade-out khi đuôi khoảng ngắt còn quá ngắn (prototype: 20 ms).
# Đây là chặn kỹ thuật để ramp không rỗng, không phải luật nghe nên không nằm
# trong rules.json.
_FADE_FLOOR_S = 0.02
# Fade-out tuyến tính theo dB chạy tới -60 dB (prototype).
_FADE_FLOOR_DB = -60.0
# Đệm 0,5 s im hai đầu khi đo Mmax phone-K — trùng sfxlib.measure().
_PAD_S = 0.5
# Cửa sổ ngân sách S11 và tên tham số trần tương ứng trong preset.
_BUDGET_WINDOWS = ((5.0, "max_5s"), (10.0, "max_10s"))
# Vai được phép thử post-hit sau từ cuối cụm (S06/S22); CTA đi lối riêng (S20).
_POSTHIT_ROLES = ("hook", "stomp", "reveal")
# Kiểu block sinh ứng viên stomp (S01 hạng 2).
_STOMP_STYLES = ("stomp", "quote")
# Sai số so đỉnh (tránh lệ thuộc dấu phẩy động khi so hai mốc bằng nhau).
_EPS = 1e-9
# Lý do trượt duy nhất dẫn tới quyết định GỘP (S05: một cue mỗi khoảng ngắt).
_MERGED = "S05 khoảng ngắt đã có cue"
# Action override được phép (§10.3); mọi action khác là FAIL.
_OVERRIDE_ACTIONS = ("none", "promote_A")


# ---------------------------------------------------------------- đo lường


def _phoned(x: np.ndarray, R: Rules) -> np.ndarray:
    """Tín hiệu qua bộ lọc loa điện thoại (§5.1, `audio.phone_hpf_*`)."""
    return A.phone(x, R.get("audio.phone_hpf_hz"), R.get("audio.phone_hpf_order"))


def _padded(x: np.ndarray) -> np.ndarray:
    """Đệm im hai đầu để cửa sổ momentary 400 ms ôm trọn cue ngắn."""
    pad = np.zeros(int(_PAD_S * A.SR))
    return np.concatenate([pad, x, pad])


def _mmax_pk(x: np.ndarray, R: Rules) -> float:
    """Mmax phone-K (miền ra quyết định mức, S14)."""
    return float(A.momentary(_phoned(_padded(x), R)).max())


@dataclass
class Ctx:
    """Bối cảnh dựng cue: manifest + tín hiệu + VO_REF + bộ luật + preset.

    Tự đo sẵn Mmax phone-K của từng file (S12 cần để tính hao do fade) và nhớ
    lại các cue đã dựng — `build_cue` là hàm thuần nên nhớ được an toàn.
    """

    manifest: dict
    signals: dict
    vo_ref: dict
    R: Rules
    preset: str
    params: dict = field(init=False)
    tier_db: dict = field(init=False)
    fps: int = field(init=False)
    mmax: dict = field(init=False)
    _cache: dict = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        self.params = self.R.preset(self.preset)
        self.tier_db = self.params["tier_db"]
        self.fps = self.R.get("fps")
        self.mmax = {k: _mmax_pk(self.signals[k], self.R) for k in sorted(self.signals)}


# ---------------------------------------------------------------- dựng cue


def build_cue(ctx: Ctx, file_key: str, mode: str, pause, tier: str, family: str):
    """Dựng thử một cue trên tín hiệu thật trong khoảng ngắt `pause`.

    Theo S05 (thân nằm trong khoảng ngắt), S06 (vị trí đỉnh và frame đồng bộ),
    S12 (cắt pre-roll, fade-in/out) và S14 (mức theo tầng, trần true-peak).
    Trả về `(cue, None)` hoặc `(None, lý do)` — lý do luôn mở đầu bằng mã luật.
    """
    key = (file_key, mode, tuple(pause), tier, family)
    if key not in ctx._cache:
        ctx._cache[key] = _build_cue(ctx, file_key, mode, pause, tier, family)
    cue, why = ctx._cache[key]
    return (dict(cue) if cue is not None else None), why


def _build_cue(ctx: Ctx, file_key: str, mode: str, pause, tier: str, family: str):
    R, sr = ctx.R, A.SR
    meta = ctx.manifest["files"][file_key]
    y = ctx.signals[file_key]
    lag = int(round(meta["lag_ms"] / 1000 * sr))
    attack = meta["attack20_ms"] / 1000.0
    tail = meta["tail30_ms"] / 1000.0

    t0, t1 = pause
    w0 = t0 + R.get("sfx.g0_s")
    w1 = t1 - R.get("sfx.g1_s")
    if w1 - w0 < R.get("sfx.min_window_s"):
        return None, "S05 khoảng ngắt quá ngắn"

    if mode == "pre":
        tail_used = min(tail, max(R.get("sfx.tail_floor_s"),
                                  (w1 - w0) - min(attack, R.get("sfx.attack_cap_s"))))
        frame = math.floor((w1 - tail_used) * ctx.fps + _EPS)
    else:
        frame = math.ceil((w0 + attack) * ctx.fps - _EPS)
    peak = frame / ctx.fps
    if not (w0 <= peak <= w1):
        return None, "S05 frame đỉnh rơi ngoài cửa sổ khoảng ngắt"

    start_keep = max(w0, peak - lag / sr)
    end_keep = min(w1, peak + (len(y) - lag) / sr)
    a = lag - int(round((peak - start_keep) * sr))
    b = lag + int(round((end_keep - peak) * sr))
    seg = y[a:b] * _envelope(R, len(y), a, b, family, peak, tail, end_keep)

    mmax_seg = _mmax_pk(seg, R)
    loss = ctx.mmax[file_key] - mmax_seg
    if loss > R.get("sfx.max_fade_loss_db"):
        return None, "S12 fade làm mất %.1f dB > %.1f dB" % (loss, R.get("sfx.max_fade_loss_db"))

    target_db = ctx.tier_db[tier]
    gain_db = (ctx.vo_ref["phone_k"] + target_db) - mmax_seg
    tp = A.true_peak_db(seg) + gain_db
    short = max(0.0, tp - R.get("sfx.tp_cap_dbtp"))
    if short > R.get("sfx.max_short_db"):
        return None, "S14 cần TP %.1f dBTP, hụt %.1f dB > %.1f dB (file quá nhọn cho tầng %s)" % (
            tp, short, R.get("sfx.max_short_db"), tier)
    gain_db -= short

    return {
        "file": file_key,
        "mode": mode,
        "pause": (float(t0), float(t1)),
        "frame": frame,
        "peak_s": peak,
        "start_s": start_keep,
        "end_s": end_keep,
        "gain_db": gain_db,
        "fade_loss_db": loss,
        "short_db": short,
        "target_db": target_db,
        "samples": seg * 10 ** (gain_db / 20),
    }, None


def _envelope(R: Rules, n_file: int, a: int, b: int, family: str,
              peak: float, tail: float, end_keep: float) -> np.ndarray:
    """Bao fade của đoạn [a, b) (S06 fade-in theo họ, S12 fade-out tuyến tính
    theo dB; chỉ fade-in khi có cắt pre-roll, chỉ fade-out khi đuôi bị cắt)."""
    env = np.ones(b - a)
    fade_in = int(R.get(f"sfx.fade_in_s.{family}") * A.SR)
    if a > 0 and fade_in > 0:
        env[:fade_in] *= np.linspace(0, 1, fade_in)[: len(env[:fade_in])]
    if peak + tail > end_keep - 1e-6 or b < n_file:
        fade_out = R.get("sfx.fade_out_s")
        length = min(fade_out.get(family, fade_out["default"]),
                     max(_FADE_FLOOR_S, end_keep - peak))
        n = int(length * A.SR)
        ramp = 10 ** (np.linspace(0, _FADE_FLOOR_DB, n) / 20)
        env[-n:] *= ramp[: len(env[-n:])]
    return env


# ---------------------------------------------------------------- ứng viên


def _block_start(block: dict) -> int:
    """Từ đầu tiên của block (dòng trên nếu có, không thì dòng hero)."""
    return block["top"][0] if block.get("top") else block["hero"][0]


def _pause_at_onset(pauses, onset: float, tol: float):
    """Khoảng ngắt kết thúc đúng onset thật của từ neo (S07, ±tol)."""
    return next((p for p in pauses if abs(p[1] - onset) <= tol), None)


def _cand(R: Rules, cid: str, role: str, source: str, anchor: int | None,
          last: int | None, at: float, hero_word: int | None = None,
          shot_index: int | None = None) -> dict:
    """Một ứng viên: tầng/hạng lấy từ `sfx.role_tier` / `sfx.role_rank`.
    `hero_word` là neo pre-hit phụ (từ hero đầu của block stomp có dòng trên)."""
    return {
        "id": cid,
        "role": role,
        "tier": R.get("sfx.role_tier")[role],
        "rank": R.get("sfx.role_rank")[role],
        "source": source,
        "anchor_word": anchor,
        "last": last,
        "hero_word": hero_word,
        "at": at,
        "shot_index": shot_index,
        "decision": None,
        "rule": None,
        "tried": [],
        "cue": None,
    }


def candidates(words: list[dict], pauses: dict, edit: dict, R: Rules) -> list[dict]:
    """Sinh ứng viên theo §5.7 bước 2: hook, stomp/quote, reveal, CTA, thẻ
    liệt kê, chuyển đoạn 5a/5b (S02) và cắt zoom. Block stomp lặp keyword CTA
    bị gỡ ngay (S20). B-roll theo spec 1.2.0 §9 (B11)."""
    on = [w["on"] for w in words]
    blocks = edit["blocks"]
    out: list[dict] = []

    brolls = sorted(edit.get("broll") or [], key=lambda s: s["t_in"])

    guard = float(R.get("broll.cut_guard_s"))
    fps = float(R.get("fps"))

    def in_slot(t: float, word_idx: int | None = None) -> bool:
        """Ứng viên section: trong slot (hai mép) hoặc từ neo thuộc slot."""
        return any(s["t_in"] - _EPS <= t <= s["t_out"] + _EPS or
                   (word_idx is not None and s["range"][0] <= word_idx < s["range"][1]) for s in brolls)

    def near_slot(t: float, word_idx: int | None = None) -> bool:
        """Ứng viên cut: thêm vùng đệm g hai phía (khoá hình dời cú cắt đó về t_out ⇒ không có tiếng); rộng hơn 1 frame
        phía trước vì khoá hình có thể dời f_in theo đỉnh cue broll_in."""
        return any(s["t_in"] - guard - 1.0 / fps - _EPS <= t < s["t_out"] + guard - _EPS or
                   (word_idx is not None and s["range"][0] <= word_idx < s["range"][1]) for s in brolls)

    hook = edit.get("hook")
    if hook and hook.get("hit_word") is not None:
        k = hook["hit_word"]
        out.append(_cand(R, "hook@w%d" % k, "hook", "hook", k, _hero_last(blocks, k), on[k]))

    cta = edit.get("cta")
    for bl in blocks:
        hero0, hero1 = bl["hero"]
        if bl.get("style") in _STOMP_STYLES:
            # §5.4: stomp/quote neo ở từ đầu block; từ hero đầu là neo phụ.
            role, anchor = "stomp", _block_start(bl)
        elif bl.get("reveal"):
            role, anchor = "reveal", hero0
        else:
            continue
        cand = _cand(R, bl["id"], role, "block", anchor, hero1 - 1, on[anchor],
                     hero_word=hero0 if role == "stomp" else None)
        # S20: stomp lặp keyword CTA — cùng một định nghĩa với validate_edit.
        if role == "stomp" and cta and editschema.hero_has_cta_keyword(bl, words, cta["keyword"]):
            cand["decision"], cand["rule"] = "XOÁ", "S20"
        out.append(cand)

    if cta:
        k = cta["range"][0]
        out.append(_cand(R, "cta@w%d" % k, "cta", "cta", k, len(words) - 1, on[k]))

    steps = edit.get("steps")
    if steps and steps.get("items"):
        k = steps["items"][0]["range"][0]
        out.append(_cand(R, "card@w%d" % k, "card", "steps", k, k, on[k]))

    # Cú cắt zoom có tiếng: shot i ≥ 1 đổi cỡ ≥ cut_jump so với s1 của shot trước.
    sounding, prev_s1 = [], None
    for i, shot in enumerate(edit["shots"]):
        if prev_s1 is not None and abs(shot["s0"] - prev_s1) >= R.get("sfx.cut_jump") - _EPS:
            sounding.append((i, shot["cut_at_word"]))
        prev_s1 = shot["s1"]

    secs = _section_candidates(words, pauses, blocks, {k for _, k in sounding}, R)
    for c in secs:
        if in_slot(c["at"]):
            c["decision"], c["rule"] = "XOÁ", "B11"
    out += secs

    for i, k in sounding:
        cand = _cand(R, "cut@w%d" % k, "cut", "shots", k, k, on[k], shot_index=i)
        # B11/B12: nếu cú cắt rơi vào bên trong slot B-roll hoặc dời/nuốt bởi B-roll thì xoá
        if near_slot(on[k], k):
            cand["decision"], cand["rule"] = "XOÁ", "B11"
        out.append(cand)

    # B11: ứng viên broll_in cho mỗi slot B-roll có t_in nằm trong một khoảng ngắt
    tol = R.get("audio.onset_mono_gap_s")
    P = [tuple(p) for p in pauses["pauses"]]
    for slot in brolls:
        k = slot["range"][0]
        t_in = slot["t_in"]
        p = next((p for p in P if p[0] - tol <= t_in <= p[1] + tol), None)
        if p is not None:
            # Ứng viên section chưa quyết định có anchor_word == k bị "XOÁ", "B11"
            for c in out:
                if c["role"] == "section" and c["anchor_word"] == k and c["decision"] is None:
                    c["decision"], c["rule"] = "XOÁ", "B11"
            out.append(_cand(R, "broll@w%d" % k, "broll_in", "broll", k, k, on[k]))

    return out


def _hero_last(blocks: list[dict], word: int) -> int:
    """Từ hero cuối của block chứa `word` (mốc post-hit của hook, S22)."""
    for bl in blocks:
        if bl["hero"][0] <= word < bl["hero"][1]:
            return bl["hero"][1] - 1
    return word


def _section_candidates(words, pauses: dict, blocks: list[dict], sounding_cuts: set, R: Rules) -> list[dict]:
    """S02: 5a = ranh giới đoạn văn của vo_script (khoảng ngắt ≥ PAUSE_MIN tầng
    B); 5b = đầu block có khoảng ngắt ≥ `section_pause_s` VÀ cú cắt zoom có tiếng ở
    đúng từ đó (`sounding_cuts`, 1.1.1 P11 — đổi chữ mà không đổi hình thì không kêu,
    như S19). Trùng khoảng ngắt thì gộp, ghi nguồn 5a."""
    P = [tuple(p) for p in pauses["pauses"]]
    tol = R.get("audio.onset_mono_gap_s")   # S07 ±20 ms = đúng bước kẹp đơn điệu S04
    on = [w["on"] for w in words]
    by_pause: dict = {}
    for brk in pauses["designed_breaks"]:
        k = brk["after_word"] + 1
        if brk["kind"] != "paragraph" or k >= len(words):
            continue
        p = _pause_at_onset(P, on[k], tol)
        if p and p[1] - p[0] >= R.get("sfx.pause_min_s")["B"]:
            by_pause.setdefault(p, ("5a", k))
    for k in sorted({_block_start(bl) for bl in blocks}):
        if k == 0 or k not in sounding_cuts:
            continue
        p = _pause_at_onset(P, on[k], tol)
        if p and p[1] - p[0] >= R.get("sfx.section_pause_s") and p not in by_pause:
            by_pause[p] = ("5b", k)
    out = []
    for p in sorted(by_pause):
        source, k = by_pause[p]
        out.append(_cand(R, "section@w%d" % k, "section", source, k, k, on[k]))
    return out


def slots(cand: dict, pauses: dict, words: list[dict], R: Rules) -> list[tuple]:
    """Slot (mode, khoảng ngắt, từ neo) của ứng viên theo §5.7 bước 3.

    pre-hit cho mọi vai, mỗi slot mang từ neo của chính nó (S07 đo lead tới
    từ đó); post-hit cho hook/stomp/reveal; CTA pre-hit rồi post-hit trong
    khoảng ngắt sau từ cuối video (S20); cắt zoom lấy khoảng ngắt có tâm trong
    `cut_near_s` quanh cú cắt. Slot post-hit và slot cắt zoom có neo None
    (không kèm chữ hiện trước lời).
    """
    P = [tuple(p) for p in pauses["pauses"]]
    role = cand["role"]
    pmin = R.get("sfx.pause_min_s")[cand["tier"]]
    long_enough = [p for p in P if p[1] - p[0] >= pmin]

    if role == "cut":
        def off(p):
            return abs((p[0] + p[1]) / 2 - cand["at"])
        near = sorted((p for p in long_enough if off(p) <= R.get("sfx.cut_near_s")),
                      key=lambda p: (off(p), p))
        return [("pre", p, None) for p in near]

    tol = R.get("audio.onset_mono_gap_s")
    on = [w["on"] for w in words]
    out: list[tuple] = []
    for anchor in [cand["anchor_word"], cand["hero_word"]]:
        if anchor is None:
            continue
        p = _pause_at_onset(P, on[anchor], tol)
        if p and p in long_enough and all(p != s[1] for s in out):
            out.append(("pre", p, anchor))

    if role in _POSTHIT_ROLES:
        end = words[cand["last"]]["e"]
        lo, hi = -R.get("sfx.posthit_pre_s"), R.get("sfx.posthit_s")
        out += [("post", p, None) for p in long_enough if lo <= p[0] - end <= hi]
    elif role == "cta":
        end = words[cand["last"]]["e"]
        after = next((p for p in long_enough if p[0] >= end - R.get("sfx.posthit_pre_s")), None)
        if after is not None and all(after != s[1] for s in out):
            out.append(("post", after, None))
    return out


# ---------------------------------------------------------------- phân bổ


@dataclass
class _State:
    """Trạng thái phân bổ: cue đã đặt, khoảng ngắt đã dùng, con trỏ xoay file,
    và (mốc pill, hạng CTA) khi CTA không pre-hit (S20, R23 — xem _reserve_pill)."""

    budget: int
    duration: float
    placed: list = field(default_factory=list)
    used: set = field(default_factory=set)
    rot: dict = field(default_factory=dict)
    pill: tuple | None = None


def _tried(mode: str, pause, file_key: str | None, reason: str) -> dict:
    return {"mode": mode, "pause": [float(pause[0]), float(pause[1])],
            "file": file_key, "reason": reason}


def _rule_of(reason: str) -> str:
    """Mã luật mở đầu mỗi lý do trượt ('S10 đỉnh-đỉnh ...' -> 'S10')."""
    return reason.split(" ", 1)[0]


def _same_wav(ctx: Ctx, a: str, b: str) -> bool:
    """S10 "cùng file" so md5 trong manifest, không so khoá: một WAV có thể đăng ký
    dưới hai khoá (1.1.0: transition-snap ở whoosh/ và air/; từ 1.1.1 L6 cấm trùng md5)."""
    files = ctx.manifest["files"]
    return files[a]["md5"] == files[b]["md5"]


def _spacing_ok(ctx: Ctx, cand: dict, cue: dict, state: _State) -> str | None:
    """Kiểm S10 (khoảng cách, không lặp file liền nhau cùng vai), S11 (ngân
    sách), S20 (vùng im quanh CTA) và S22 (0–hook_window_s tối đa 1 cue tầng A).
    Trả None nếu đặt được."""
    R, preset = ctx.R, ctx.params
    role, tier, t = cand["role"], cand["tier"], cue["peak_s"]
    p2p, aa = R.get("sfx.p2p_s"), R.get("sfx.aa_s")
    stomp_s, same_s = R.get("sfx.stomp_s"), R.get("sfx.same_file_s")
    cta_clear = R.get("sfx.cta_clear_s")
    for x in state.placed:
        gap = abs(x["peak_s"] - t)
        if gap < p2p:
            return "S10 đỉnh-đỉnh < %g s (%s)" % (p2p, x["id"])
        if tier == "A" and x["tier"] == "A" and gap < aa:
            return "S10 A-A < %g s (%s)" % (aa, x["id"])
        if role == "stomp" and x["role"] == "stomp" and gap < stomp_s:
            return "S10 stomp-stomp < %g s (%s)" % (stomp_s, x["id"])
        if _same_wav(ctx, x["file"], cue["file"]) and gap < same_s:
            return "S10 cùng file < %g s (%s)" % (same_s, x["id"])
        if (role == "cta" or x["role"] == "cta") and gap < cta_clear:
            return "S20 vùng im quanh CTA ±%g s (%s)" % (cta_clear, x["id"])
    if state.pill is not None and cand["rank"] > state.pill[1] and abs(t - state.pill[0]) < cta_clear:
        return "S20 vùng im quanh pill CTA ±%g s (pill %.3f s)" % (cta_clear, state.pill[0])

    peaks = sorted([x["peak_s"] for x in state.placed] + [t])
    for width, cap_name in _BUDGET_WINDOWS:
        cap = preset[cap_name]
        if any(sum(1 for u in peaks if s <= u < s + width) > cap for s in peaks):
            return "S11 > %d cue / %g s" % (cap, width)

    if tier == "A":
        max_a = R.get("sfx.max_a")
        if sum(1 for x in state.placed if x["tier"] == "A") >= max_a:
            return "S11 tầng A tối đa %d cue" % max_a
        window = R.get("sfx.hook_window_s")
        if t <= window and any(x["tier"] == "A" and x["peak_s"] <= window for x in state.placed):
            return "S22 0-%g s tối đa 1 cue tầng A" % window

    if role == "cut":
        cuts = [x for x in state.placed if x["role"] == "cut"]
        max_cut = R.get("sfx.max_cut_c")
        if len(cuts) >= max_cut:
            return "S11 cắt zoom tối đa %d cue" % max_cut
        if any(abs(x["shot_index"] - cand["shot_index"]) == 1 for x in cuts):
            return "S11 không đặt trên hai cú cắt liên tiếp"

    if len(state.placed) >= state.budget:
        return "S11 hết ngân sách video (%d cue)" % state.budget

    # S10 "không liền nhau cùng vai": so với cue cùng vai liền trước VÀ liền
    # sau theo đỉnh — phân bổ không theo thứ tự thời gian nên cue mới có thể
    # chen giữa hai cue đã đặt. Luật này chỉ loại file (S17 thử file kế), nên
    # kiểm sau các luật chặn cả slot để lượt thử bị S11/S22 chặn vẫn ghi mã đó.
    same_role = sorted((x for x in state.placed if x["role"] == role), key=lambda x: x["peak_s"])
    before = [x for x in same_role if x["peak_s"] < t][-1:]
    after = [x for x in same_role if x["peak_s"] > t][:1]
    for x in before + after:
        if _same_wav(ctx, x["file"], cue["file"]):
            return "S10 cùng file liền nhau cùng vai (%s)" % x["id"]
    return None


def _file_order(R: Rules, role: str, start: int) -> list[tuple]:
    """Thứ tự file thử cho một slot: (file, họ của file, chỉ số vòng xoay). Họ chính theo
    vòng xoay S17 từ `start`, rồi từng họ trong `sfx.role_fallback[role]` theo thứ tự liệt kê,
    không xoay (chỉ số None) — 1.1.1 P10: CTA rơi về slide khi sparkle đuôi dài trượt S07."""
    family = R.get("sfx.role_family")[role]
    files = R.get("sfx.family_files")[family]
    order = [(files[(start + j) % len(files)], family, (start + j) % len(files)) for j in range(len(files))]
    for fam in R.get("sfx.role_fallback").get(role, []):
        order += [(f, fam, None) for f in R.get("sfx.family_files")[fam]]
    return order


def _try_place(ctx: Ctx, cand: dict, state: _State, pauses: dict, words: list[dict]):
    """Thử mọi slot × file (_file_order) của ứng viên. Trả về
    `(cue, chỉ_số_vòng_xoay | None, danh_sách_đã_thử)`; cue None nghĩa là trượt,
    chỉ số None nghĩa là cue lấy từ họ fallback."""
    R = ctx.R
    role, tier = cand["role"], cand["tier"]
    lead_max = R.get("sfx.lead_max_s")
    tried: list[dict] = []
    for mode, pause, anchor in slots(cand, pauses, words, R):
        if pause in state.used:
            tried.append(_tried(mode, pause, None, _MERGED))
            continue
        for file_key, family, rot_index in _file_order(R, role, state.rot.get(role, 0)):
            cue, why = build_cue(ctx, file_key, mode, pause, tier, family)
            if cue is None:
                tried.append(_tried(mode, pause, file_key, why))
                continue
            # S07: chữ của từ neo CỦA SLOT NÀY không được hiện trước lời quá
            # lead_max. Slot post-hit và cắt zoom không có neo nên miễn kiểm.
            # Lead tuỳ đuôi (tail30) từng file nên loại theo (slot, file), 1.1.1.
            if anchor is not None:
                lead = words[anchor]["on"] - cue["peak_s"]
                if lead > lead_max + _EPS:
                    tried.append(_tried(mode, pause, file_key, "S07 chữ đi trước lời %.0f ms > %.0f ms"
                                        % (1000 * lead, 1000 * lead_max)))
                    continue
            why = _spacing_ok(ctx, cand, cue, state)
            if why:
                tried.append(_tried(mode, pause, file_key, why))
                continue
            return cue, rot_index, tried
    return None, None, tried


def _commit(state: _State, cand: dict, cue: dict, rot_index: int | None) -> None:
    """Chốt cue: nhớ khoảng ngắt đã dùng và đẩy con trỏ xoay file của vai (cue của họ
    fallback — rot_index None — không đẩy)."""
    if rot_index is not None:
        state.rot[cand["role"]] = rot_index + 1
    state.used.add(cue["pause"])
    cue.update(id=cand["id"], role=cand["role"], tier=cand["tier"],
               shot_index=cand["shot_index"])
    state.placed.append(cue)
    cand["decision"], cand["rule"], cand["cue"] = "OK", None, cue


def _reject(cand: dict) -> None:
    """Quyết định khi không có slot nào qua: GỘP nếu khoảng ngắt đã có cue,
    CHỈ CHỮ cho tầng A, BỎ cho tầng B/C (S01, S07). Không có slot nào để thử
    thì mã luật là S07 — riêng CTA là S20 (không pre-hit, không post-hit sau
    từ cuối thì CTA không có tiếng)."""
    if any(t["reason"] == _MERGED for t in cand["tried"]):
        cand["decision"], cand["rule"] = "GỘP", _rule_of(_MERGED)
        return
    cand["decision"] = "CHỈ CHỮ" if cand["tier"] == "A" else "BỎ"
    if cand["tried"]:
        cand["rule"] = _rule_of(cand["tried"][0]["reason"])
    else:
        cand["rule"] = "S20" if cand["role"] == "cta" else "S07"


def merged_into(cand: dict, cues: list[dict], tol: float = 1e-3) -> dict | None:
    """Cue OK đang giữ khoảng ngắt mà ứng viên GỘP `cand` bị gộp vào (S01) —
    lấy slot gộp đầu tiên trong `tried` (thứ tự thử: pre-hit trước). `cues` là
    danh sách cue của sfx_plan; khoảng ngắt so với dung sai `tol` vì số trong
    sfx_plan làm tròn 4 số lẻ (R4). Ứng viên không GỘP thì None."""
    if cand.get("decision") != "GỘP":
        return None
    pause = next((t.get("pause") for t in cand.get("tried") or []
                  if isinstance(t, dict) and t.get("reason") == _MERGED), None)
    if not pause:
        return None
    return next((c for c in cues if c.get("pause") is not None
                 and all(abs(a - b) <= tol for a, b in zip(c["pause"], pause))), None)


def _reserve_pill(cands: list[dict], state: _State) -> None:
    """S20 (R23): CTA đã có quyết định mà không pre-hit (post-hit, BỎ) thì pill hiện ở
    on(cta.range[0]) = `at` của ứng viên CTA, không tiếng — giữ (mốc đó, hạng CTA) để
    _spacing_ok cấm ứng viên hạng dưới có đỉnh trong ±cta_clear_s quanh pill."""
    cta = next((c for c in cands if c["role"] == "cta"), None)
    if state.pill is None and cta is not None and cta["decision"] is not None and not (
            cta["decision"] == "OK" and cta["cue"]["mode"] == "pre"):
        state.pill = (cta["at"], cta["rank"])


def _allocate(ctx: Ctx, cands: list[dict], state: _State, pauses: dict, words: list[dict]) -> None:
    """Phân bổ theo hạng (S01). Trong cùng hạng chọn ứng viên có slot xa các
    cue đã đặt nhất; hoà thì chọn cái sớm hơn (pending đã xếp theo thời gian).
    Xong mỗi hạng thì xét vùng im của pill CTA (_reserve_pill)."""
    ranks = sorted({c["rank"] for c in cands})
    for rank in ranks:
        group = sorted([c for c in cands if c["rank"] == rank], key=lambda c: (c["at"], c["id"]))
        pending = [c for c in group if c["decision"] is None]
        while pending:
            best = None
            for cand in pending:
                cue, rot_index, tried = _try_place(ctx, cand, state, pauses, words)
                if cue is None:
                    continue
                far = min([abs(cue["peak_s"] - x["peak_s"]) for x in state.placed]
                          + [cue["peak_s"], state.duration - cue["peak_s"]])
                if best is None or far > best[0] + _EPS:
                    best = (far, cand, cue, rot_index, tried)
            if best is None:
                for cand in pending:
                    cand["tried"] = _try_place(ctx, cand, state, pauses, words)[2]
                    _reject(cand)
                break
            _, cand, cue, rot_index, tried = best
            cand["tried"] = tried
            _commit(state, cand, cue, rot_index)
            pending.remove(cand)
        _reserve_pill(cands, state)


# ---------------------------------------------------------------- S26 lấp


def _stretches(state: _State, t_start: float, t_end: float) -> list[tuple]:
    """Các đoạn liên tiếp giữa hai đỉnh (kể cả hai đầu), dài nhất trước."""
    pts = [t_start] + sorted(x["peak_s"] for x in state.placed) + [t_end]
    return sorted([(b - a, a, b) for a, b in zip(pts, pts[1:])], reverse=True)


def _gap_fill(ctx: Ctx, edit: dict, state: _State, pauses: dict, words: list[dict],
              overrides) -> list[dict]:
    """S26: đoạn > `max_gap_s` không có cue thì thêm 1 cue tầng C ở đầu block
    gần giữa đoạn nhất, lặp tới khi không lấp thêm được. Override (§10.3) áp
    cho ứng viên lấp ngay khi nó sinh ra: `none` thì bỏ qua, thử chỗ kế."""
    R = ctx.R
    P = [tuple(p) for p in pauses["pauses"]]
    tol = R.get("audio.onset_mono_gap_s")
    on = [w["on"] for w in words]
    starts = [k for k in sorted({_block_start(bl) for bl in edit["blocks"]}) if k > 0]
    margin = R.get("sfx.gapfill_margin_s")
    pmin = R.get("sfx.pause_min_s")["B"]   # S26 nói rõ 250 ms, không theo tầng C
    max_gap = R.get("sfx.max_gap_s")
    made: dict = {}
    while True:
        filled = False
        for length, a, b in _stretches(state, on[0], pauses["last_word_end"]):
            if length <= max_gap:
                break
            mid = (a + b) / 2
            options = []
            for k in starts:
                p = _pause_at_onset(P, on[k], tol)
                if (p is not None and p not in state.used and p[1] - p[0] >= pmin
                        and a + margin <= p[1] <= b - margin):
                    options.append((abs((p[0] + p[1]) / 2 - mid), k))
            for _, k in sorted(options):
                if k not in made:
                    made[k] = _cand(R, "gapfill@w%d" % k, "gapfill", "S26", k, k, on[k])
                    _apply_overrides([made[k]], overrides, R)
                cand = made[k]
                if cand["rule"] == "OVERRIDE":   # §10.3 none: đã bị gỡ, không thử
                    continue
                cue, rot_index, tried = _try_place(ctx, cand, state, pauses, words)
                cand["tried"] = tried
                if cue is None:
                    _reject(cand)
                    continue
                _commit(state, cand, cue, rot_index)
                filled = True
                break
            if filled:
                break
        if not filled:
            break
    return [made[k] for k in sorted(made)]


def _warnings(ctx: Ctx, state: _State, pauses: dict, words: list[dict]) -> list[str]:
    """Cảnh báo sàn mật độ S26 (ghi vào sfx_plan, stage trả DONE_WITH_CONCERNS)."""
    R = ctx.R
    max_gap = R.get("sfx.max_gap_s")
    out = []
    for length, a, b in _stretches(state, words[0]["on"], pauses["last_word_end"]):
        if length <= max_gap:
            break
        out.append("LOW_DENSITY:%.2f-%.2f" % (a, b))
    min_events = R.get("sfx.min_events")
    if len(state.placed) < min_events:
        out.append("LOW_DENSITY:events<%d" % min_events)
    roles = {x["role"] for x in state.placed}
    if "hook" not in roles and "cta" not in roles:
        out.append("LOW_DENSITY:no-hook-no-cta")
    return out


# ---------------------------------------------------------------- kết xuất


def _round(obj, nd: int = 4):
    """Làm tròn mọi số thực ghi ra JSON về `nd` số lẻ (tính tất định)."""
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, (float, np.floating)):
        return round(float(obj), nd)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, dict):
        return {k: _round(v, nd) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_round(v, nd) for v in obj]
    return obj


def _levels(ctx: Ctx, samples: np.ndarray) -> dict:
    """Mức đỉnh của cue đã chỉnh gain so với VO_REF ở ba miền (S14/S23);
    phone-A chỉ để báo cáo (§5.1)."""
    x = _padded(samples)
    phoned = _phoned(x, ctx.R)
    return {
        "phone_k": float(A.momentary(phoned).max()) - ctx.vo_ref["phone_k"],
        "k": float(A.momentary(x).max()) - ctx.vo_ref["k"],
        "phone_a": float(A.a_momentary(phoned).max()) - ctx.vo_ref["phone_a"],
    }


_CUE_KEYS = ("file", "mode", "pause", "frame", "peak_s", "start_s", "end_s",
             "gain_db", "fade_loss_db", "short_db", "target_db", "levels")
_CAND_KEYS = ("id", "role", "tier", "rank", "source", "anchor_word", "decision", "rule",
              "tried", "cue")


def _cue_json(cue: dict, with_id: bool = False) -> dict:
    """Cue theo contract; `with_id` thêm id/role/tier cho danh sách `cues`."""
    out = {"id": cue["id"], "role": cue["role"], "tier": cue["tier"]} if with_id else {}
    out.update({k: cue[k] for k in _CUE_KEYS})
    return out


def _cand_json(cand: dict) -> dict:
    """Ứng viên theo contract (bỏ các khoá chỉ dùng khi phân bổ)."""
    out = {k: cand[k] for k in _CAND_KEYS}
    out["cue"] = _cue_json(cand["cue"]) if cand["cue"] else None
    return out


def _sha_json(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False, default=float).encode("utf-8")
    ).hexdigest()


def _check_override_actions(overrides) -> None:
    """§10.3 "mọi thứ khác là FAIL": action ngoài none | promote_A là lỗi."""
    for ov in overrides or []:
        if ov["action"] not in _OVERRIDE_ACTIONS:
            raise ValueError("override không hợp lệ: %r (chỉ none | promote_A)" % ov["action"])


def _check_override_targets(overrides, cands: list[dict]) -> None:
    """§10.3: target phải là id của một ứng viên — kiểm SAU lượt lấp S26 vì id
    `gapfill@w<k>` chỉ sinh ra lúc đó."""
    ids = {c["id"] for c in cands}
    for ov in overrides or []:
        if ov["target"] not in ids:
            raise ValueError("override trỏ tới ứng viên không có: %r" % ov["target"])


def _apply_overrides(cands: list[dict], overrides, R: Rules) -> None:
    """§10.3: `none` gỡ ứng viên (BỎ / OVERRIDE); `promote_A` nâng lên tầng A
    và hạng của stomp. Override có target chưa có trong `cands` thì để đó
    (có thể là ứng viên lấp S26, sinh sau) — `_check_override_targets` bắt
    target lạ ở cuối."""
    for cand in cands:
        for ov in overrides or []:
            if ov["target"] != cand["id"]:
                continue
            if ov["action"] == "none":
                cand["decision"], cand["rule"] = "BỎ", "OVERRIDE"
            elif ov["action"] == "promote_A":
                cand["tier"], cand["rank"] = "A", R.get("sfx.role_rank.stomp")


def plan(words: list[dict], pauses: dict, edit: dict, overrides, manifest: dict,
         signals: dict, vo_mono: np.ndarray, R: Rules, preset: str):
    """Xếp toàn bộ cue SFX cho một video (§5.7). Trả `(sfx_plan, cues_audio)`.

    `words` là words.json đã có `on`, `pauses` là pauses.json đầy đủ (có
    `designed_breaks`, `vo_ref`, `last_word_end`), `signals` tra theo khoá
    manifest (`family/name`).
    """
    ctx = Ctx(manifest, signals, pauses["vo_ref"], R, preset)
    duration = float(pauses["duration_s"])
    state = _State(budget=rules_lib.per_video_budget(R, preset, duration), duration=duration)

    _check_override_actions(overrides)
    cands = candidates(words, pauses, edit, R)
    _apply_overrides(cands, overrides, R)
    _allocate(ctx, cands, state, pauses, words)
    cands += _gap_fill(ctx, edit, state, pauses, words, overrides)
    _check_override_targets(overrides, cands)

    state.placed.sort(key=lambda c: c["peak_s"])
    for cue in state.placed:
        cue["levels"] = _levels(ctx, cue["samples"])

    ordered = sorted(cands, key=lambda c: (c["rank"], c["at"], c["id"]))
    sfx_plan = _round({
        "rules_version": R.version,
        "preset": preset,
        "vo_ref": dict(pauses["vo_ref"]),
        "budget": state.budget,
        "candidates": [_cand_json(c) for c in ordered],
        "cues": [_cue_json(c, with_id=True) for c in state.placed],
        "warnings": _warnings(ctx, state, pauses, words),
        "inputs_sha256": {
            "words": _sha_json(words),
            "pauses": _sha_json(pauses),
            "edit": _sha_json(edit),
            "overrides": _sha_json(list(overrides or [])),
            "vo": hashlib.sha256(np.ascontiguousarray(vo_mono, dtype=np.float64).tobytes()).hexdigest(),
            "manifest": _sha_json(manifest),
            "rules": R.sha256,
        },
    })
    cues_audio = [{"start_s": float(c["start_s"]), "samples": c["samples"]} for c in state.placed]
    return sfx_plan, cues_audio
