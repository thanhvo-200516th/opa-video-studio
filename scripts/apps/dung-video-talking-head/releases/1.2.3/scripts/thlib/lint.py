"""thlib.lint — lint SFX độc lập L1–L14 (§5.8): trước mux L1–L10, L12–L14
(`run_pre_mux`), sau mux + social L11 (`run_post_mux`, code ở thlib.lint_post).

Lint không tin số trong sfx_plan (§5.7 bước 9): thân cue là đoạn mẫu khác 0
trên STEM, mẫu đầu / đỉnh / mức phone-K / true peak / đuôi −30 dB đo lại trên
thân đó; khung có tiếng và VO_REF đo lại trên vo-clean; khoảng ngắt lấy từ
pauses.json; md5 của WAV trên đĩa đối chiếu manifest. sfx_plan chỉ cho biết
mỗi cue TỰ NHẬN là gì (id, vai, tầng, file, frame, mục tiêu, hụt TP) — lint
đối chiếu lời tự nhận đó với số đo và với luật.

Mỗi mã trả đúng một kết quả {"code", "ok", "msg", "frame"}: nhiều vi phạm thì
gộp vào msg, frame là frame của vi phạm đầu tiên có mốc thời gian. WARN
LOW_DENSITY (S26) ghi vào msg của L4, không làm ok=false. Mốc thời gian so với
ngưỡng luật tính bằng frame (các ngưỡng đều là bội số của 1/fps), nên lint
không bao giờ khắt khe hơn planner ở biên. Luật nêu ở hai nơi được chấm dưới
đúng mã planner ghi: vùng im ±1 s quanh CTA ở L7 (S20), ≤ 1 cue A trong
0–3,5 s ở L8 (S22).
"""

from __future__ import annotations

import hashlib
import json
import math
import unicodedata
from dataclasses import dataclass, field

import numpy as np
from scipy.ndimage import uniform_filter1d

from . import audio as A
from . import mix, paths, planner, sfxlib, voice
from . import rules as rules_lib
from .rules import Rules

TOL = 1e-3             # Ruling R4: số thực trong sfx_plan / pauses.json làm tròn 4 số lẻ
_LEVEL_TOL_DB = 0.3    # Ruling R5: |phone-K đo − (mục tiêu tầng − hụt TP)|
_TP_TOL_DB = 0.01      # sai số đo true peak (stem ghi WAV 16-bit rồi đọc lại)
_FADE_TOL_DB = 0.1     # MmaxPK manifest làm tròn 2 số lẻ + lượng tử 16-bit
_PAD_S = 0.5           # đệm im hai đầu khi đo Mmax phone-K — trùng sfxlib.measure()
_SHORT_TERM_S = 3.0    # cửa sổ short-term BS.1771 / EBU Tech 3341 (S-max của S18, S29)
_WINDOWS = ((5.0, "max_5s"), (10.0, "max_10s"))   # cửa sổ ngân sách S11 → trần trong preset
_MSG_MAX = 6           # msg chỉ liệt kê bấy nhiêu vi phạm đầu

LEGACY_FPS = 30        # fps của bảng SFX 1.0.0 (cột `from` trong script.ts)
# Ghi chú cue cũ → vai 1.1 (so trên phần trước dấu ':'; thứ tự là ưu tiên).
_LEGACY_ROLES = (("hook", "hook"), ("chữ đập", "stomp"), ("hero", "hero_script"),
                 ("bảng", "card"), ("mục", "list_item"), ("CTA", "cta"), ("cắt", "cut"))

_PLAN_KEYS = ("rules_version", "preset", "vo_ref", "budget", "candidates", "cues", "warnings",
              "inputs_sha256")
_CAND_KEYS = ("id", "role", "tier", "rank", "source", "anchor_word", "decision", "rule", "tried", "cue")
_CUE_KEYS = ("file", "mode", "pause", "frame", "peak_s", "start_s", "end_s", "gain_db",
             "fade_loss_db", "short_db", "target_db", "levels")
_TRIED_KEYS = ("mode", "pause", "file", "reason")
_LEVEL_KEYS = ("phone_k", "k", "phone_a")
_INPUT_KEYS = ("words", "pauses", "edit", "overrides", "vo", "manifest", "rules")
_DECISIONS = ("OK", "GỘP", "CHỈ CHỮ", "BỎ", "XOÁ")
_BLOCK_ROLES = ("stomp", "reveal")   # vai có chữ block đồng bộ theo đỉnh (S08)


# ---------------------------------------------------------------- tiện ích


def _result(code: str, bad: list, ok_msg: str, warns=()) -> dict:
    """Gộp các vi phạm [(msg, frame)] của một mã thành một dòng kết quả."""
    msg, frame = ok_msg, None
    if bad:
        msg = "; ".join(m for m, _ in bad[:_MSG_MAX])
        if len(bad) > _MSG_MAX:
            msg += " … (+%d vi phạm nữa)" % (len(bad) - _MSG_MAX)
        frame = next((f for _, f in bad if f is not None), None)
    if warns:
        msg += " | WARN " + "; ".join(warns)
    return {"code": code, "ok": not bad, "msg": msg, "frame": frame}


def _num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _cands(plan: dict) -> list:
    got = plan.get("candidates")
    return got if isinstance(got, list) else []


def plan_json(plan: dict) -> str:
    """sfx_plan ở dạng JSON chuẩn (khoá xếp, không khoảng trắng) — BUILD ghi đúng
    chuỗi này ra out/sfx_plan.json nên sha của file bằng plan_sha256."""
    return json.dumps(plan, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def plan_sha256(plan: dict) -> str:
    """sha256 của sfx_plan ở dạng JSON chuẩn (plan_json) — không phụ thuộc cách
    file được ghi ra đĩa (S21, L10)."""
    return hashlib.sha256(plan_json(plan).encode("utf-8")).hexdigest()


def _stereo(x) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    return x if x.ndim == 2 else np.stack([x, x], axis=1)


def _short_term_max(x) -> float:
    """S-max: short-term (3 s) lớn nhất, BS.1770 nhiều kênh (tổng công suất kênh, R10)."""
    kx = A.kweight(_stereo(x).T)
    power = uniform_filter1d(kx * kx, size=int(_SHORT_TERM_S * A.SR), axis=-1, mode="constant")
    return float(-0.691 + 10 * np.log10(max(float(power.sum(axis=0).max()), 1e-20)))


def _nonzero_runs(x: np.ndarray, R: Rules, spans=()) -> list[tuple[int, int]]:
    """Thân tiếng: các đoạn [a, b) mẫu khác 0; hai đoạn cách nhau ≤ một cửa sổ
    RMS (audio.rms_win_s) thì gộp. `spans` (R130): khoảng mẫu [a, b) của từng cue trong plan —
    các đoạn nằm trọn trong cùng một khoảng cũng gộp: stem int16 làm fade vào rất nhỏ của file SFX
    về 0 lâu hơn một cửa sổ RMS (lô b01 video 60: mẩu 2 ms rồi 73 ms im) chứ không phải tiếng lạ."""
    nz = np.flatnonzero(x)
    if len(nz) == 0:
        return []
    cut = np.flatnonzero(np.diff(nz) > int(round(R.get("audio.rms_win_s") * A.SR)))
    runs = list(zip(np.concatenate([nz[:1], nz[cut + 1]]).tolist(),
                    (np.concatenate([nz[cut], nz[-1:]]) + 1).tolist()))
    merged: list[tuple[int, int]] = []
    for a, b in runs:
        if merged and any(s0 <= merged[-1][0] and b <= s1 for s0, s1 in spans):
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    return merged


# ---------------------------------------------------------------- đo lại


@dataclass
class _Body:
    """Một thân tiếng trên stem: mẫu [a, b) và số đo lại của nó."""

    a: int
    b: int
    pause: tuple | None      # khoảng ngắt chứa trọn thân
    voiced: int              # số mẫu khác 0 trên khung có tiếng
    peak_db: float           # đỉnh RMS20 của thân (dBFS)
    off_db: float            # RMS20 của stem tại t1 − g1 (0 nếu không có khoảng ngắt)
    peak_s: float            # đỉnh đo (argmax đường bao 5 ms — cùng định nghĩa lag của manifest)
    mmax_pk: float           # Mmax phone-K tuyệt đối
    tp: float                # true peak (dBTP)
    act30: list              # vùng RMS20 ≥ đỉnh + l6_rel_db (S09)
    cues: list = field(default_factory=list)   # chỉ số cue (trong _Scene.cues) có đỉnh ở đây


@dataclass
class _Scene:
    """Số đo dùng chung cho các mã trước mux."""

    plan: dict
    cues: list               # cue của plan (có id, đỉnh là số), xếp theo đỉnh
    owner: list              # chỉ số thân chứa đỉnh của từng cue (None nếu stem im)
    bodies: list
    R: Rules
    preset: str
    pauses: dict             # pauses.json
    vo_ref_pk: float         # VO_REF phone-K đo lại trên vo-clean
    speech_start: float      # khung có tiếng đầu tiên của vo-clean (s)

    @property
    def fps(self) -> int:
        return self.R.get("fps")


def _mmax_pk(x: np.ndarray, R: Rules) -> float:
    """Mmax phone-K (§5.1) của đoạn x, đệm im hai đầu như sfxlib.measure()."""
    pad = np.zeros(int(_PAD_S * A.SR))
    phoned = A.phone(np.concatenate([pad, x, pad]), R.get("audio.phone_hpf_hz"),
                     R.get("audio.phone_hpf_order"))
    return float(A.momentary(phoned).max())


def _measure_body(stem, env, voiced, a, b, P, R) -> _Body:
    x, m = stem[a:b], float(env[a:b].max())
    pause = next((p for p in P if p[0] - TOL <= a / A.SR and b / A.SR <= p[1] + TOL), None)
    off = 0.0
    if pause is not None:
        j = min(len(env) - 1, max(0, int(round((pause[1] - R.get("sfx.g1_s")) * A.SR))))
        off = float(A.db(env[j]))
    env5 = np.convolve(np.abs(x), np.ones(sfxlib._ENV5_WIN) / sfxlib._ENV5_WIN, mode="same")
    thr = m * 10 ** (R.get("sfx.l6_rel_db") / 20)
    return _Body(a=a, b=b, pause=pause, voiced=int(np.count_nonzero(voiced[a:b] & (x != 0))),
                 peak_db=float(A.db(m)), off_db=off, peak_s=(a + int(np.argmax(env5))) / A.SR,
                 mmax_pk=_mmax_pk(x, R), tp=A.true_peak_db(x),
                 act30=[(a + i0, a + i1) for i0, i1 in A.runs(env[a:b] >= thr)])


def _scene(plan, stem, vo_mono, pauses, R, preset) -> _Scene:
    stem = np.asarray(stem, dtype=float)
    raw = plan.get("cues") if isinstance(plan.get("cues"), list) else []
    cues = sorted((c for c in raw if isinstance(c, dict) and isinstance(c.get("id"), str)
                   and _num(c.get("peak_s"))), key=lambda c: c["peak_s"])
    win = R.get("audio.rms_win_s")
    voiced = A.db(A.rms_env(vo_mono, win)) > R.get("audio.pause_rms_db")
    on_stem = np.pad(voiced[: len(stem)], (0, max(0, len(stem) - len(voiced))))
    env = A.rms_env(stem, win)
    P = [tuple(p) for p in pauses["pauses"]]
    tol = int(round(TOL * A.SR))
    spans = [(int(round(c["start_s"] * A.SR)) - tol, int(round(c["end_s"] * A.SR)) + tol)
             for c in cues if _num(c.get("start_s")) and _num(c.get("end_s"))]
    bodies = [_measure_body(stem, env, on_stem, a, b, P, R) for a, b in _nonzero_runs(stem, R, spans)]
    owner = []
    for i, c in enumerate(cues):
        n = int(round(c["peak_s"] * A.SR))
        owner.append(next((k for k, bd in enumerate(bodies) if bd.a <= n < bd.b), None))
        if owner[-1] is not None:
            bodies[owner[-1]].cues.append(i)
    first = np.flatnonzero(voiced)
    return _Scene(plan=plan, cues=cues, owner=owner, bodies=bodies, R=R, preset=preset, pauses=pauses,
                  vo_ref_pk=voice.vo_ref(vo_mono, R)["phone_k"],
                  speech_start=first[0] / A.SR if len(first) else 0.0)


def _fr(S: _Scene, t: float) -> int:
    """Frame gần nhất của mốc t (đỉnh cue đặt đúng k/fps)."""
    return max(0, int(round(t * S.fps)))


def _single(S: _Scene, i: int) -> _Body | None:
    """Thân riêng của cue thứ i (None khi stem im ở đỉnh hoặc thân dính cue khác)."""
    bi = S.owner[i]
    return S.bodies[bi] if bi is not None and len(S.bodies[bi].cues) == 1 else None


# ---------------------------------------------------------------- L1–L4


def _l1(S: _Scene) -> dict:
    """S05: thân nằm trọn trong đúng một khoảng ngắt đủ dài, mẫu đầu ≥ t0 + g0,
    RMS20 tại t1 − g1 ≤ max(sàn, đỉnh thân + l6_rel_db), 0 mẫu trên khung có
    tiếng, tối đa 1 cue mỗi khoảng ngắt; mọi tiếng trên stem phải có cue."""
    R = S.R
    g0, g1, pmin = R.get("sfx.g0_s"), R.get("sfx.g1_s"), R.get("sfx.pause_min_s")
    floor, rel = R.get("sfx.l6_floor_dbfs"), R.get("sfx.l6_rel_db")
    bad = [("%s: stem không có tiếng tại đỉnh %.3f s" % (c["id"], c["peak_s"]), _fr(S, c["peak_s"]))
           for c, bi in zip(S.cues, S.owner) if bi is None]
    used: dict = {}
    for body in S.bodies:
        t_a, t_b = body.a / A.SR, body.b / A.SR
        f, p = _fr(S, t_a), body.pause
        name = "+".join(S.cues[i]["id"] for i in body.cues) or "tiếng %.3f–%.3f s" % (t_a, t_b)
        if len(body.cues) != 1:
            bad.append(("%s: %s" % (name, "nhiều cue dính một thân" if body.cues
                                    else "có trên stem nhưng plan không có cue"), f))
        if body.voiced:
            bad.append(("%s: %d mẫu cue trên khung có tiếng" % (name, body.voiced), f))
        if p is None:
            bad.append(("%s: thân %.3f–%.3f s không nằm trọn trong khoảng ngắt nào"
                        % (name, t_a, t_b), f))
            continue
        if p in used:
            bad.append(("%s: chung khoảng ngắt %.3f–%.3f với %s" % (name, p[0], p[1], used[p]), f))
        used.setdefault(p, name)
        need = max([pmin.get(S.cues[i].get("tier"), min(pmin.values())) for i in body.cues]
                   or [min(pmin.values())])
        if p[1] - p[0] < need - TOL:
            bad.append(("%s: khoảng ngắt %.0f ms < %.0f ms"
                        % (name, 1000 * (p[1] - p[0]), 1000 * need), f))
        if t_a < p[0] + g0 - TOL:
            bad.append(("%s: mẫu đầu sau t0 %.1f ms < %.0f ms"
                        % (name, 1000 * (t_a - p[0]), 1000 * g0), f))
        limit = max(floor, body.peak_db + rel)
        if body.off_db > limit:
            bad.append(("%s: RMS20 tại t1 − %.0f ms = %.1f dBFS > %.1f dBFS"
                        % (name, 1000 * g1, body.off_db, limit), _fr(S, p[1] - g1)))
    return _result("L1", bad, "%d cue: thân nằm trọn trong khoảng ngắt, tắt trước t1 − %.0f ms, "
                   "0 mẫu đè lời" % (len(S.cues), 1000 * g1))


def _l2(S: _Scene) -> dict:
    """S09: tối đa 1 SFX tại mọi thời điểm, đuôi tính tới −30 dB (cùng ngưỡng
    tương đối với S05, sfx.l6_rel_db): vùng RMS20 ≥ đỉnh thân − 30 dB nào chứa
    đỉnh của ≥ 2 cue là chồng lớp."""
    peaks = [int(round(c["peak_s"] * A.SR)) for c in S.cues]
    bad = []
    for body in S.bodies:
        for i0, i1 in body.act30:
            ids = [c["id"] for c, n in zip(S.cues, peaks) if i0 <= n < i1]
            if len(ids) > 1:
                bad.append(("%d SFX cùng kêu ở %.3f–%.3f s: %s"
                            % (len(ids), i0 / A.SR, i1 / A.SR, ", ".join(ids)), _fr(S, i0 / A.SR)))
    return _result("L2", bad, "tối đa 1 SFX tại mọi thời điểm (đuôi tính tới %g dB)"
                   % S.R.get("sfx.l6_rel_db"))


def _l3(S: _Scene, manifest: dict) -> dict:
    """S10: đỉnh–đỉnh, A↔A, stomp↔stomp, cùng file ≥ same_file_s và không lặp
    file liền nhau trong cùng vai (±1 s quanh CTA: L7). "Cùng file" so md5 của
    manifest (một WAV có thể mang hai khoá, vd transition-snap của 1.1.0 ở whoosh/ và air/);
    khoá không có trong manifest thì so chính khoá (L6 báo file lạ)."""
    R, files = S.R, manifest.get("files", {})

    def wav(c: dict):
        return (files.get(c.get("file")) or {}).get("md5") or c.get("file")
    pairs = (("đỉnh–đỉnh", "sfx.p2p_s", lambda c, x: True),
             ("A↔A", "sfx.aa_s", lambda c, x: c.get("tier") == "A" == x.get("tier")),
             ("stomp↔stomp", "sfx.stomp_s", lambda c, x: c.get("role") == "stomp" == x.get("role")),
             ("cùng file", "sfx.same_file_s", lambda c, x: wav(c) == wav(x)))
    bad = []
    for i, c in enumerate(S.cues):
        for x in S.cues[i + 1:]:
            gap = _fr(S, x["peak_s"]) - _fr(S, c["peak_s"])
            for label, key, applies in pairs:
                if applies(c, x) and gap < R.get(key) * S.fps - 1e-9:
                    bad.append(("%s %s–%s %.0f ms < %.0f ms" % (
                        label, c["id"], x["id"], 1000 * gap / S.fps, 1000 * R.get(key)), _fr(S, x["peak_s"])))
    prev: dict = {}
    for c in S.cues:
        last = prev.get(c.get("role"))
        if last is not None and wav(last) == wav(c):
            bad.append(("S10 %s lặp file %s của %s liền trước cùng vai"
                        % (c["id"], c.get("file"), last["id"]), _fr(S, c["peak_s"])))
        prev[c.get("role")] = c
    return _result("L3", bad, "khoảng cách S10 đạt cho %d cue" % len(S.cues))


def _shot_index(lock, frame: int, fps: int):
    """Chỉ số shot trong picture_lock có mốc cắt ở đúng frame (cú cắt snap đỉnh)."""
    shots = (lock or {}).get("shots") or []
    return next((i for i, s in enumerate(shots)
                 if _num(s.get("t")) and round(s["t"] * fps) == frame), None)


def _l4(S: _Scene, lock) -> dict:
    """S11/S26: ngân sách PER_VIDEO = ceil(k × giây / 10), cửa sổ 5 s / 10 s,
    MAX_A, cắt zoom ≤ max_cut_c và không ở hai cú cắt liên tiếp (shot trong
    picture_lock); WARN LOW_DENSITY (không làm FAIL)."""
    R, fps = S.R, S.fps
    params = R.preset(S.preset)
    budget = rules_lib.per_video_budget(R, S.preset, float(S.pauses["duration_s"]))
    frames = [_fr(S, c["peak_s"]) for c in S.cues]
    bad = []
    if len(S.cues) > budget:
        bad.append(("%d cue > ngân sách %d = ceil(%g × %.2f s / 10)"
                    % (len(S.cues), budget, params["k_per10"], S.pauses["duration_s"]), None))
    if S.plan.get("budget") != budget:
        bad.append(("budget trong plan (%s) khác công thức (%d)" % (S.plan.get("budget"), budget), None))
    for width, cap_name in _WINDOWS:
        for s in frames:
            n = sum(1 for u in frames if s <= u < s + width * fps - 1e-9)
            if n > params[cap_name]:
                bad.append(("%d cue trong %g s từ %.3f s > %d"
                            % (n, width, s / fps, params[cap_name]), s))
                break
    n_a = sum(1 for c in S.cues if c.get("tier") == "A")
    if n_a > R.get("sfx.max_a"):
        bad.append(("%d cue tầng A > %d" % (n_a, R.get("sfx.max_a")), None))
    cuts = [(c, f) for c, f in zip(S.cues, frames) if c.get("role") == "cut"]
    if len(cuts) > R.get("sfx.max_cut_c"):
        bad.append(("%d cue cắt zoom > %d" % (len(cuts), R.get("sfx.max_cut_c")), cuts[-1][1]))
    shot = [_shot_index(lock, f - R.get("sfx.sync_frame.cut"), fps) for _, f in cuts]
    for (c, f), i in zip(cuts, shot):
        if i is not None and i + 1 in shot:
            bad.append(("%s: cue trên hai cú cắt liên tiếp (shot %d, %d)" % (c["id"], i, i + 1), f))
    return _result("L4", bad, "%d/%d cue, cửa sổ 5 s ≤ %d, 10 s ≤ %d, tầng A %d/%d, cắt zoom %d/%d"
                   % (len(S.cues), budget, params["max_5s"], params["max_10s"], n_a, R.get("sfx.max_a"),
                      len(cuts), R.get("sfx.max_cut_c")), _low_density(S))


def _low_density(S: _Scene) -> list[str]:
    """S26: đoạn > max_gap_s không cue (từ lúc bắt đầu có lời tới hết lời),
    < min_events cue, thiếu cả hook lẫn CTA."""
    R = S.R
    pts = [S.speech_start] + [c["peak_s"] for c in S.cues] + [S.pauses["last_word_end"]]
    out = ["LOW_DENSITY:%.2f-%.2f" % (a, b) for a, b in zip(pts, pts[1:])
           if b - a > R.get("sfx.max_gap_s")]
    if len(S.cues) < R.get("sfx.min_events"):
        out.append("LOW_DENSITY:events<%d" % R.get("sfx.min_events"))
    if not {c.get("role") for c in S.cues} & {"hook", "cta"}:
        out.append("LOW_DENSITY:no-hook-no-cta")
    return out


# ---------------------------------------------------------------- L5–L9


def _l5(S: _Scene, manifest: dict) -> dict:
    """S14/S12 (Ruling R5): mục tiêu tầng đúng preset; hụt TP ≤ max_short_db;
    |phone-K đo trên stem − VO_REF − (mục tiêu − hụt)| ≤ 0,3 dB; TP cue ≤ trần;
    hao do fade (MmaxPK file gốc + gain − Mmax thân) ≤ max_fade_loss_db."""
    R = S.R
    tier_db, files = R.preset(S.preset)["tier_db"], manifest.get("files", {})
    cap, max_short, max_loss = (R.get("sfx.tp_cap_dbtp"), R.get("sfx.max_short_db"),
                                R.get("sfx.max_fade_loss_db"))
    bad = []
    for i, c in enumerate(S.cues):
        f, cid, tier, short = _fr(S, c["peak_s"]), c["id"], c.get("tier"), c.get("short_db")
        if tier not in tier_db:
            bad.append(("%s: tầng %r không có mức mục tiêu" % (cid, tier), f))
            continue
        target = tier_db[tier]
        if c.get("target_db") != target:
            bad.append(("%s: target_db %s ≠ %+.1f dB của tầng %s"
                        % (cid, c.get("target_db"), target, tier), f))
        if not _num(short) or not 0 <= short <= max_short + 1e-9:
            bad.append(("%s: hụt TP %s ngoài 0–%g dB" % (cid, short, max_short), f))
            continue
        body = _single(S, i)
        if body is None:
            bad.append(("%s: không đo được mức riêng trên stem" % cid, f))
            continue
        rel = body.mmax_pk - S.vo_ref_pk
        if abs(rel - (target - short)) > _LEVEL_TOL_DB:
            bad.append(("%s: phone-K đo %+.2f dB, cần %+.2f (mục tiêu %+.1f − hụt %.2f) ±%g"
                        % (cid, rel, target - short, target, short, _LEVEL_TOL_DB), f))
        if body.tp > cap + _TP_TOL_DB:
            bad.append(("%s: true peak %.2f dBTP > %.1f" % (cid, body.tp, cap), f))
        meta = files.get(c.get("file"))
        if meta is not None and _num(c.get("gain_db")):
            loss = meta["MmaxPK"] + c["gain_db"] - body.mmax_pk
            if loss > max_loss + _FADE_TOL_DB:
                bad.append(("%s: fade làm mất %.2f dB > %g dB" % (cid, loss, max_loss), f))
    return _result("L5", bad, "%d cue: mức phone-K đúng mục tiêu tầng (±%g dB), TP ≤ %g dBTP, "
                   "fade mất ≤ %g dB" % (len(S.cues), _LEVEL_TOL_DB, cap, max_loss))


def _md5_bad(meta: dict, R: Rules) -> str | None:
    """md5 của WAV trên đĩa (release) so với manifest; None là khớp."""
    path = paths.release_dir(R.version) / meta.get("path", "")
    if not path.is_file():
        return "không thấy file %s" % meta.get("path")
    got = hashlib.md5(path.read_bytes()).hexdigest()
    return None if got == meta.get("md5") else "md5 trên đĩa %s… ≠ manifest" % got[:8]


def _l6(S: _Scene, manifest: dict) -> dict:
    """S13/S16/S03: file có trong manifest, md5 khớp đĩa và không trùng với mục nào
    khác trên cả release (1.1.1), license đã biết, thuộc danh sách file của họ tiếng
    ứng với vai hoặc của một họ fallback (`sfx.role_fallback`, 1.1.1 P10) và đạt ràng
    buộc đo (gồm <250 Hz ≤ 50 %) của đúng họ đang giữ file đó."""
    R, files = S.R, manifest.get("files", {})
    role_family, family_files = R.get("sfx.role_family"), R.get("sfx.family_files")
    fallback = R.get("sfx.role_fallback")
    bad, seen, md5_bad = [], {}, {}
    for key in sorted(files):
        first = seen.setdefault(files[key].get("md5"), key)
        if first != key:
            bad.append(("%s trùng md5 với %s" % (key, first), None))
    for c in S.cues:
        key, f, cid = c.get("file"), _fr(S, c["peak_s"]), c["id"]
        meta = files.get(key)
        if meta is None:
            bad.append(("%s: file %s không có trong manifest" % (cid, key), f))
            continue
        if key not in md5_bad:
            md5_bad[key] = _md5_bad(meta, R)
        if md5_bad[key]:
            bad.append(("%s: %s %s" % (cid, key, md5_bad[key]), f))
        if not meta.get("source_url") or str(meta.get("license", "")).strip().lower() in ("", "unknown"):
            bad.append(("%s: %s chưa rõ license" % (cid, key), f))
        family = role_family.get(c.get("role"))
        if family is None:
            bad.append(("%s: vai %r không có họ tiếng" % (cid, c.get("role")), f))
            continue
        allowed = [family] + list(fallback.get(c.get("role"), []))
        holder = next((fam for fam in allowed if key in family_files[fam]), None)
        if holder is None:
            bad.append(("%s: file %s ngoài danh sách họ %s" % (cid, key, " | ".join(allowed)), f))
        family = holder or family
        ok, why = sfxlib.role_ok(meta, family, R)
        if not ok:
            bad.append(("%s: %s không đạt ràng buộc họ %s (%s)"
                        % (cid, key, family, ", ".join(why)), f))
    return _result("L6", bad, "%d cue: file trong manifest, md5 khớp, license rõ, đúng họ tiếng"
                   % len(S.cues))


def _pill_zone_bad(S: _Scene, lock) -> list:
    """S20 (R23): CTA không pre-hit (post-hit hay không có cue) thì pill hiện không tiếng ở
    picture_lock.cta.show — cue hạng dưới CTA (hạng lấy ở ứng viên, không có thì theo vai)
    không được có đỉnh trong ±cta_clear_s quanh mốc đó. Mirror của planner._reserve_pill."""
    pill = (lock or {}).get("cta") or {}
    if not _num(pill.get("show")) or any(c.get("role") == "cta" and c.get("mode") == "pre" for c in S.cues):
        return []
    role_rank, clear = S.R.get("sfx.role_rank"), S.R.get("sfx.cta_clear_s")
    cands = [c for c in _cands(S.plan) if isinstance(c, dict)]
    rank = {c.get("id"): c.get("rank") for c in cands if _num(c.get("rank"))}
    cta_rank = next((c["rank"] for c in cands if c.get("role") == "cta" and _num(c.get("rank"))),
                    role_rank["cta"])
    bad = []
    for x in S.cues:
        r = rank.get(x["id"], role_rank.get(x.get("role")))
        if _num(r) and r > cta_rank and abs(x["peak_s"] - pill["show"]) < clear - TOL:
            bad.append(("%s cách pill CTA không tiếng (hiện %.3f s) %.0f ms < ±%.0f ms" % (
                x["id"], pill["show"], 1000 * abs(x["peak_s"] - pill["show"]), 1000 * clear),
                _fr(S, x["peak_s"])))
    return bad


def _l7(S: _Scene, lock) -> dict:
    """S20: ≤ 1 cue CTA tầng B; ±cta_clear_s không có cue khác; pre-hit thì
    trước khi hết lời, post-hit thì trong khoảng ngắt sau từ cuối (S27); CTA không
    pre-hit thì vùng im quanh pill (_pill_zone_bad)."""
    R, lwe = S.R, S.pauses["last_word_end"]
    ctas = [(i, c) for i, c in enumerate(S.cues) if c.get("role") == "cta"]
    bad = _pill_zone_bad(S, lock)
    if len(ctas) > 1:
        bad.append(("%d cue CTA (tối đa 1)" % len(ctas), _fr(S, ctas[1][1]["peak_s"])))
    for i, c in ctas:
        f = _fr(S, c["peak_s"])
        if c.get("tier") != "B":
            bad.append(("%s: tầng %r, CTA phải tầng B" % (c["id"], c.get("tier")), f))
        for x in S.cues:
            if x is not c and abs(_fr(S, x["peak_s"]) - f) < R.get("sfx.cta_clear_s") * S.fps - 1e-9:
                bad.append(("%s cách CTA %s %.0f ms < ±%.0f ms" % (x["id"], c["id"], 1000 * abs(
                    x["peak_s"] - c["peak_s"]), 1000 * R.get("sfx.cta_clear_s")), _fr(S, x["peak_s"])))
        body = _single(S, i)
        p = body.pause if body is not None else None   # khoảng ngắt đo được, không lấy lời khai
        if c.get("mode") == "post":
            if p is None or p[0] < lwe - R.get("sfx.posthit_pre_s") - TOL:
                bad.append(("%s: post-hit không nằm trong khoảng ngắt sau từ cuối" % c["id"], f))
        elif c.get("mode") == "pre":
            if p is None or p[1] > lwe + TOL:
                bad.append(("%s: pre-hit phải ở khoảng ngắt trước từ neo" % c["id"], f))
        else:
            bad.append(("%s: mode %r (chỉ pre | post)" % (c["id"], c.get("mode")), f))
    return _result("L7", bad, "CTA: %d cue tầng B, ±%g s im" % (len(ctas), R.get("sfx.cta_clear_s")))


def _l8(S: _Scene) -> dict:
    """S22 (phần tiếng): ≤ 1 cue hook, tầng A, pre-hit hoặc post-hit; pre-hit
    có đỉnh trong 0–hook_window_s; 0–hook_window_s tối đa 1 cue tầng A."""
    R = S.R
    win, win_f = R.get("sfx.hook_window_s"), R.get("sfx.hook_window_s") * S.fps + 1e-9
    hooks = [c for c in S.cues if c.get("role") == "hook"]
    bad = []
    if len(hooks) > 1:
        bad.append(("%d cue hook (tối đa 1)" % len(hooks), _fr(S, hooks[1]["peak_s"])))
    for c in hooks:
        f = _fr(S, c["peak_s"])
        if c.get("tier") != "A":
            bad.append(("%s: tầng %r, hook phải tầng A" % (c["id"], c.get("tier")), f))
        if c.get("mode") not in ("pre", "post"):
            bad.append(("%s: mode %r (chỉ pre | post)" % (c["id"], c.get("mode")), f))
        elif c["mode"] == "pre" and f > win_f:
            bad.append(("%s: pre-hit ở %.3f s > %g s" % (c["id"], c["peak_s"], win), f))
    early = [c for c in S.cues if c.get("tier") == "A" and _fr(S, c["peak_s"]) <= win_f]
    if len(early) > 1:
        bad.append(("%d cue tầng A trong 0–%g s: %s"
                    % (len(early), win, ", ".join(c["id"] for c in early)), _fr(S, early[1]["peak_s"])))
    return _result("L8", bad, "hook: %d cue tầng A, 0–%g s ≤ 1 cue A" % (len(hooks), win))


def _block_hosts(S: _Scene) -> dict:
    """id block → cue mà top + hero của block phải đồng bộ theo (S08): cue
    stomp/reveal OK của chính block, hoặc (Ruling R22) cue OK đã GỘP ứng viên
    stomp/reveal của block vì chung khoảng ngắt (vd. cue hook nuốt block đập)."""
    hosts = {c["id"]: c for c in S.cues if c.get("role") in _BLOCK_ROLES}
    for cand in _cands(S.plan):
        if isinstance(cand, dict) and cand.get("role") in _BLOCK_ROLES and cand.get("id") not in hosts:
            host = planner.merged_into(cand, S.cues, TOL)
            if host is not None:
                hosts[cand["id"]] = host
    return hosts


def _block_bad(bid: str, host: dict, lock: dict, sync: dict, fps: int) -> str | None:
    """S08: block `bid` synced và mọi chữ top + hero hiện ở đỉnh cue `host` −
    sync_frame.block/fps. None là khớp."""
    want = host["peak_s"] - sync["block"] / fps
    via = "" if host["id"] == bid else " (GỘP vào %s)" % host["id"]
    blk = next((b for b in lock.get("blocks") or [] if b.get("id") == bid), None)
    if blk is None or not blk.get("synced"):
        return "picture_lock không có block %s đồng bộ%s" % (bid, via)
    shows = [w.get("show") for w in (blk.get("top") or []) + (blk.get("hero") or [])]
    if not shows or any(not _num(s) or abs(s - want) > TOL for s in shows):
        return "top+hero hiện ở %s, cần %.4f s%s" % (sorted({s for s in shows if _num(s)}), want, via)
    return None


def _display_bad(c: dict, lock: dict, sync: dict, fps: int) -> str | None:
    """S08: mốc hiển thị của thẻ, pill CTA pre-hit (R23) và cú cắt có tiếng
    trong picture_lock phải bằng đỉnh − SYNC_FRAME/fps (chữ block: _block_bad).
    None là khớp (hoặc vai không có hình đồng bộ)."""
    role, peak = c.get("role"), c["peak_s"]
    if role == "card":
        got, want = (lock.get("steps") or {}).get("in"), peak - sync["card"] / fps
        if not _num(got) or abs(got - want) > TOL:
            return "thẻ vào ở %s, cần %.4f s" % (got, want)
    elif role == "cta" and c.get("mode") == "pre":   # S20: CTA post-hit thì pill không có tiếng
        got, want = (lock.get("cta") or {}).get("show"), peak - sync["cta_pill"] / fps
        if not _num(got) or abs(got - want) > TOL:
            return "pill CTA hiện ở %s, cần %.4f s" % (got, want)
    elif role == "cut":
        want = peak - sync["cut"] / fps
        if not any(_num(s.get("t")) and abs(s["t"] - want) <= TOL for s in lock.get("shots") or []):
            return "không có cú cắt ở %.4f s" % want
    elif role == "broll_in":
        want = peak - sync["broll_in"] / fps
        if not any(abs(b["f_in"] / fps - want) <= TOL for b in lock.get("broll") or []):
            return "B-roll không vào ở %.4f s" % want
    return None


def _l9(S: _Scene, lock) -> dict:
    """S08/S24: đỉnh khai trong plan đúng k/fps; đỉnh đo trên stem lệch frame
    k trong −early/+late frame; display_s trong picture_lock khớp; block
    synced phải có cue để đồng bộ — cue stomp/reveal của chính nó hoặc cue OK
    đã GỘP ứng viên của nó (R22)."""
    R, fps, lock = S.R, S.fps, lock or {}
    sync = R.get("sfx.sync_frame")
    early, late = R.get("sfx.sync_tol_f.early"), R.get("sfx.sync_tol_f.late")
    bad = []
    for i, c in enumerate(S.cues):
        k = c.get("frame")
        if not isinstance(k, int) or abs(c["peak_s"] - k / fps) > TOL:
            bad.append(("%s: đỉnh %.4f s không nằm đúng frame %s/%d" % (c["id"], c["peak_s"], k, fps),
                        _fr(S, c["peak_s"])))
            continue
        body = _single(S, i)
        if body is not None and not -early <= (body.peak_s - k / fps) * fps <= late:
            bad.append(("%s: đỉnh đo trên stem lệch %+.2f f so với frame %d (cho phép −%d/+%d)"
                        % (c["id"], (body.peak_s - k / fps) * fps, k, early, late), k))
        why = _display_bad(c, lock, sync, fps)
        if why:
            bad.append(("%s: %s" % (c["id"], why), k))
    hosts = _block_hosts(S)
    for bid, host in hosts.items():
        why = _block_bad(bid, host, lock, sync, fps)
        if why:
            bad.append(("%s: %s" % (bid, why), _fr(S, host["peak_s"])))
    for blk in lock.get("blocks") or []:
        if blk.get("synced") and blk.get("id") not in hosts:
            bad.append(("block %s đánh dấu synced nhưng không có cue (hình phải giữ mốc của chính nó)"
                        % blk.get("id"), None))
    return _result("L9", bad, "%d cue: đỉnh đúng frame đồng bộ, display_s khớp picture_lock"
                   % len(S.cues))


# ---------------------------------------------------------------- L10, L12–L14


def _l10(plan: dict, expected_sha: str | None) -> dict:
    """S21: sha256 của sfx_plan bằng sha của output planner chạy lại."""
    if expected_sha is None:
        return {"code": "L10", "ok": True, "frame": None,
                "msg": "BỎ QUA: không có expected_sha (sha output planner chạy lại) — "
                       "lint_sfx.py và BUILD luôn truyền"}
    got = plan_sha256(plan)
    bad = [] if got == expected_sha else [
        ("sha256 sfx_plan %s… ≠ output planner %s… (đặt tay hoặc plan cũ)"
         % (got[:12], expected_sha[:12]), None)]
    return _result("L10", bad, "sfx_plan khớp output planner (%s…)" % got[:12])


def _l12(bed, vo_mono: np.ndarray, R: Rules) -> dict:
    """S29: integrated của bed = giọng + bgm.rel_lu (±bgm.tol_lu) và S-max(bed)
    ≤ I(bed) + bgm.smax_over_i_lu — đo BS.1770 hai kênh (R10) trên đoạn bed có
    tiếng, giọng đo trên cùng đoạn và phát ra hai kênh. 1.1.1 (P12), trên các cửa sổ
    short-term không fade của bed (mix.bed_windows): LRA của bed ≤ bgm.lra_max_lu, và trên
    mọi cửa sổ có lời (short-term của giọng qua cổng Tech 3342) giọng − bed ≥ bgm.st_floor_lu."""
    if bed is None:
        return _result("L12", [], "không có nhạc nền")
    st = _stereo(bed)
    nz = np.flatnonzero(np.any(st != 0, axis=1))
    if len(nz) == 0:
        return _result("L12", [("bgm_bed toàn im", None)], "")
    n = int(nz[-1]) + 1
    vo = _stereo(vo_mono[:n])
    i_bed, smax = A.integrated_lufs(st[:n]), _short_term_max(st[:n])
    want = A.integrated_lufs(vo) + R.get("bgm.rel_lu")
    bad = []
    if abs(i_bed - want) > R.get("bgm.tol_lu"):
        bad.append(("bed %.2f LUFS, cần %.2f (giọng %+g LU) ±%g LU"
                    % (i_bed, want, R.get("bgm.rel_lu"), R.get("bgm.tol_lu")), None))
    if smax > i_bed + R.get("bgm.smax_over_i_lu"):
        bad.append(("S-max bed %.2f > I %.2f + %g LU" % (smax, i_bed, R.get("bgm.smax_over_i_lu")), None))
    win = mix.bed_windows(0.0, n / A.SR, R)
    bst, vst = A.short_term(st[:n])[win], A.short_term(vo)[win]
    lra = A.lra(bst)
    if lra > R.get("bgm.lra_max_lu"):
        bad.append(("LRA bed %.1f LU > %g LU (nhạc nền to dần/nhỏ dần)" % (lra, R.get("bgm.lra_max_lu")), None))
    measured = mix.speech_floor(bed, vo_mono, R)       # cùng phép đo BUILD dùng để chọn offset (R129)
    floor, t = measured if measured else (None, None)
    if floor is not None and floor < R.get("bgm.st_floor_lu"):
        bad.append(("lời − nền %.1f LU < %g LU ở cửa sổ %.1f–%.1f s"
                    % (floor, R.get("bgm.st_floor_lu"), t, t + A.ST_WIN_S), int(round(t * R.get("fps")))))
    msg = "bed %.2f LUFS (đích %.2f), S-max %.2f, LRA %.1f LU" % (i_bed, want, smax, lra)
    if floor is not None:
        msg += ", lời − nền ≥ %.1f LU" % floor
    return _result("L12", bad, msg)


def _l13(S: _Scene) -> dict:
    """S19: không cue nào (và ứng viên của nó) gắn sự kiện thuộc
    sfx.never_sound hay vai không có tầng tiếng; không thân tiếng nào nằm trên
    khung có tiếng (mọi cue đè lời)."""
    never, allowed = set(S.R.get("sfx.never_sound")), set(S.R.get("sfx.role_tier"))
    ok_role = {c.get("id"): c.get("role") for c in _cands(S.plan)
               if isinstance(c, dict) and c.get("decision") == "OK"}
    bad = []
    for c in S.cues:
        f = _fr(S, c["peak_s"])
        for role in sorted({c.get("role"), ok_role.get(c["id"], c.get("role"))}, key=str):
            if role in never:
                bad.append(("%s: sự kiện %s không bao giờ có tiếng" % (c["id"], role), f))
            elif role not in allowed:
                bad.append(("%s: vai %r không được có tiếng" % (c["id"], role), f))
    for body in S.bodies:
        if body.voiced:
            name = "+".join(S.cues[i]["id"] for i in body.cues) or "tiếng ngoài plan"
            bad.append(("%s: đè lời (%d mẫu trên khung có tiếng)" % (name, body.voiced),
                        _fr(S, body.a / A.SR)))
    return _result("L13", bad, "không cue nào thuộc NEVER_SOUND hay đè lời")


def _cand_bad(c: dict) -> list[str]:
    """S23: một ứng viên đủ quyết định, mã luật, slot đã thử, mức 3 miền."""
    miss = [k for k in _CAND_KEYS if k not in c]
    if miss:
        return ["%s thiếu %s" % (c.get("id"), ", ".join(miss))]
    out = []
    if c["decision"] not in _DECISIONS:
        out.append("%s: quyết định %r lạ" % (c["id"], c["decision"]))
    if c["decision"] == "OK":
        cue = c["cue"] if isinstance(c["cue"], dict) else {}
        levels = cue.get("levels") if isinstance(cue.get("levels"), dict) else {}
        miss = [k for k in _CUE_KEYS if k not in cue] + [
            "levels.%s" % k for k in _LEVEL_KEYS if not _num(levels.get(k))]
        if miss:
            out.append("%s: cue thiếu %s" % (c["id"], ", ".join(miss)))
    elif c["cue"] is not None or not c["rule"]:
        out.append("%s: %s phải có mã luật và không có cue" % (c["id"], c["decision"]))
    if not isinstance(c["tried"], list) or any(
            not isinstance(t, dict) or any(k not in t for k in _TRIED_KEYS) for t in c["tried"]):
        out.append("%s: slot đã thử sai dạng" % c["id"])
    return out


def _l14(plan: dict, R: Rules, preset: str) -> dict:
    """S23: sfx_plan đủ khoá; đúng version luật và preset; mọi ứng viên có
    quyết định, mã luật, slot đã thử, mức 3 miền; `cues` đúng bằng cue của các
    ứng viên OK (kèm id/vai/tầng) xếp theo đỉnh; đủ sha đầu vào."""
    bad = [("sfx_plan thiếu %s" % k, None) for k in _PLAN_KEYS if k not in plan]
    if plan.get("rules_version") != R.version:
        bad.append(("rules_version %r ≠ %s" % (plan.get("rules_version"), R.version), None))
    if plan.get("preset") != preset:
        bad.append(("preset %r ≠ %s" % (plan.get("preset"), preset), None))
    cands = _cands(plan)
    ids = [c.get("id") for c in cands if isinstance(c, dict)]
    if len(ids) != len(cands) or len(set(ids)) != len(ids):
        bad.append(("ứng viên trùng id hoặc sai dạng", None))
    for c in cands:
        bad += [(m, None) for m in (_cand_bad(c) if isinstance(c, dict) else [])]
    ok = [c for c in cands if isinstance(c, dict) and c.get("decision") == "OK"
          and isinstance(c.get("cue"), dict) and _num(c["cue"].get("peak_s"))]
    expect = sorted(({"id": c["id"], "role": c["role"], "tier": c["tier"], **c["cue"]} for c in ok),
                    key=lambda c: c["peak_s"])
    if plan.get("cues") != expect:
        bad.append(("cues lệch cue của các ứng viên OK", None))
    inputs = plan.get("inputs_sha256") if isinstance(plan.get("inputs_sha256"), dict) else {}
    miss = [k for k in _INPUT_KEYS if not inputs.get(k)]
    if miss:
        bad.append(("inputs_sha256 thiếu %s" % ", ".join(miss), None))
    return _result("L14", bad, "sfx_plan đủ %d ứng viên, quyết định, slot đã thử, mã luật, mức 3 miền"
                   % len(cands))


def run_pre_mux(plan: dict, stem, vo_mono, bed, pauses: dict, picture_lock: dict, manifest: dict,
                R: Rules, preset: str, expected_sha: str | None = None) -> list[dict]:
    """Chấm L1–L10, L12–L14 trước mux. `stem`, `vo_mono` mono trên trục
    vo-clean 48 kHz; `bed` [n] | [n, 2] | None; `pauses` = pauses.json;
    `expected_sha` = plan_sha256(output planner chạy lại trên cùng đầu vào)."""
    vo_mono = np.asarray(vo_mono, dtype=float)
    S = _scene(plan, stem, vo_mono, pauses, R, preset)
    return [_l1(S), _l2(S), _l3(S, manifest), _l4(S, picture_lock), _l5(S, manifest), _l6(S, manifest),
            _l7(S, picture_lock), _l8(S), _l9(S, picture_lock), _l10(plan, expected_sha),
            _l12(bed, vo_mono, R), _l13(S), _l14(plan, R, preset)]


def run_post_mux(project, R: Rules) -> list[dict]:
    """L11 (S25/S18/S27) trên bản xuất của `project` sau mux + social — code ở
    thlib.lint_post (nhập muộn: lint_post dùng các hàm đo của module này)."""
    from .lint_post import run_post_mux as post
    return post(project, R)



# ---------------------------------------------------------------- bảng cue 1.0.0


def _legacy_role(note: str) -> str:
    """Vai 1.1 của một cue 1.0.0, đọc từ phần ghi chú trước dấu ':'."""
    head = unicodedata.normalize("NFC", note.split(":", 1)[0])
    for pattern, role in _LEGACY_ROLES:
        if unicodedata.normalize("NFC", pattern) in head:
            return role
    raise ValueError("Không nhận ra vai của cue cũ: %r" % note)


def old_cues_to_plan(old_cues: list[dict], pauses: dict, manifest_or_files: dict) -> dict:
    """Đổi bảng SFX 1.0.0 (script.ts: from/target/src/volume/note) sang dạng
    sfx_plan để lint chấm được (fixture 25 cue cũ của video 02).

    File = src bỏ tiền tố 'sfx/'; lag tra trong `manifest_or_files` (một
    manifest {"files": …} hoặc thẳng {file: số đo có lag_ms}); đỉnh =
    from/LEGACY_FPS + lag; vai lấy từ ghi chú; 1.0.0 không có tầng, mode,
    mục tiêu hay mức 3 miền nên các trường đó để None."""
    files = manifest_or_files.get("files", manifest_or_files)
    P = [tuple(p) for p in pauses["pauses"]]
    cands = []
    for i, old in enumerate(old_cues):
        key = old["src"].removeprefix("sfx/")
        start = old["from"] / LEGACY_FPS
        peak = start + files[key]["lag_ms"] / 1000
        pause = next((p for p in P if p[0] <= peak <= p[1]), None)
        cue = {"file": key, "mode": None, "pause": list(pause) if pause else None,
               "frame": int(round(peak * LEGACY_FPS)), "peak_s": round(peak, 4),
               "start_s": round(start, 4), "end_s": None,
               "gain_db": round(20 * math.log10(old["volume"]), 4), "fade_loss_db": None,
               "short_db": None, "target_db": None, "levels": None}
        cands.append({"id": "old%02d" % (i + 1), "role": _legacy_role(old["note"]), "tier": None,
                      "rank": None, "source": "legacy", "anchor_word": None, "decision": "OK",
                      "rule": None, "tried": [], "cue": cue})
    cues = sorted(({"id": c["id"], "role": c["role"], "tier": c["tier"], **c["cue"]} for c in cands),
                  key=lambda c: c["peak_s"])
    return {"rules_version": "1.0.0", "preset": None, "vo_ref": pauses.get("vo_ref"), "budget": None,
            "candidates": cands, "cues": cues, "warnings": [], "inputs_sha256": {}}
