"""thlib.facesafe — chiếu khung mặt người dẫn, khớp khung FACE_FIT và kiểm FACE_ROOM (spec 1.1.1 §8.2, §8.3).

Module này cung cấp:
- bands(face_rows, f, R): hộp miệng và mắt tại khung hình f (toạ độ gốc 1080×1920);
- shot_at(shots, f): chỉ số shot k tại khung f;
- project(shots, f, X, Y): chiếu toạ độ nguồn (X, Y) sang toạ độ màn hình ra;
- layers(lock, R): danh sách các lớp chữ/phủ kèm khung hình xuất hiện, ảnh dò và biên nhả;
- fit(lock, face_rows, R, masks=None): khớp tỉ lệ s0, s1 và dịch trục y cho từng shot;
- check(project_dir, lock, face_rows, R): kiểm tra toàn bộ video đè mặt;
- face_room_error(layer_id, px, k, s0, s1, f0, f1, ctx, a, b): định dạng lỗi FACE_ROOM.
"""

from __future__ import annotations

import math
import struct
import subprocess
from pathlib import Path
from typing import Any

import numpy as np


def in_out(p: float) -> float:
    """Easing inOut: khớp EASE.inOut của template src/anim.ts."""
    p = min(1.0, max(0.0, float(p)))
    if p < 0.5:
        return 4.0 * p * p * p
    return 1.0 - math.pow(-2.0 * p + 2.0, 3) / 2.0


def in_cubic(t: float) -> float:
    """Easing inCubic: khớp EASE.inCubic của template src/anim.ts."""
    t = min(1.0, max(0.0, float(t)))
    return t * t * t


def bands(face_rows: list[list[Any]], f: int, R: Any) -> dict[str, tuple[float, float, float, float]] | None:
    """Hộp miệng và mắt {"mouth": (x0, y0, x1, y1), "eyes": (...)} tại khung hình ra f (toạ độ 1080×1920).

    - Mỗi mép hộp lấy trung vị trượt face.smooth_frames (5) mẫu trên các hàng dò được.
    - Lấy bao (envelope: min/max) trên mọi hàng có |t_src − t| <= face.window_s (0.2 s).
    - mouth = face.mouth_box [0.25, 0.70, 0.75, 0.90]; eyes = face.eye_box [0.10, 0.30, 0.90, 0.50].
    - Trả về None nếu không có hàng dò được nào trong cửa sổ window_s quanh t.
    """
    smooth_n = int(R.get("face.smooth_frames"))
    window_s = float(R.get("face.window_s"))
    mouth_rel = list(R.get("face.mouth_box"))
    eye_rel = list(R.get("face.eye_box"))

    t_out = f / 30.0

    valid_rows = [(r[0], float(r[1]), float(r[2]), float(r[3]), float(r[4]))
                  for r in face_rows if r[1] is not None]
    if not valid_rows:
        return None

    in_window = [r for r in valid_rows if abs(r[0] - t_out) <= window_s + 1e-9]
    if not in_window:
        return None

    boxes = np.array([[r[1], r[2], r[3], r[4]] for r in valid_rows], dtype=float)
    x0_raw = boxes[:, 0]
    y0_raw = boxes[:, 1]
    x1_raw = boxes[:, 0] + boxes[:, 2]
    y1_raw = boxes[:, 1] + boxes[:, 3]

    half = smooth_n // 2
    n = len(valid_rows)

    def smooth(arr: np.ndarray) -> np.ndarray:
        out = np.empty_like(arr)
        for i in range(n):
            lo = max(0, i - half)
            hi = min(n, i + half + 1)
            out[i] = float(np.median(arr[lo:hi]))
        return out

    x0_sm = smooth(x0_raw)
    y0_sm = smooth(y0_raw)
    x1_sm = smooth(x1_raw)
    y1_sm = smooth(y1_raw)

    win_indices = [i for i, r in enumerate(valid_rows) if abs(r[0] - t_out) <= window_s + 1e-9]
    face_x0 = float(np.min(x0_sm[win_indices]))
    face_y0 = float(np.min(y0_sm[win_indices]))
    face_x1 = float(np.max(x1_sm[win_indices]))
    face_y1 = float(np.max(y1_sm[win_indices]))

    fw = face_x1 - face_x0
    fh = face_y1 - face_y0

    mouth = (
        face_x0 + mouth_rel[0] * fw,
        face_y0 + mouth_rel[1] * fh,
        face_x0 + mouth_rel[2] * fw,
        face_y0 + mouth_rel[3] * fh,
    )
    eyes = (
        face_x0 + eye_rel[0] * fw,
        face_y0 + eye_rel[1] * fh,
        face_x0 + eye_rel[2] * fw,
        face_y0 + eye_rel[3] * fh,
    )
    return {"mouth": mouth, "eyes": eyes}


def shot_at(shots: list[dict[str, Any]], f: int) -> int:
    """Chỉ số k lớn nhất có f/30 >= t_k; 0 nếu trước shot 1."""
    t = f / 30.0
    for k in range(len(shots) - 1, -1, -1):
        if t >= shots[k]["t"] - 1e-9:
            return k
    return 0


def frames_of_shot(shots: list[dict[str, Any]], k: int, dur_f: int) -> range:
    """Các khung thuộc shot k đúng như shot_at / Footage.tsx chọn (t_k ≤ f/30 < t_k+1). Mốc cắt thường lẻ khung
    (vd 28,7088 s = f861,26): f861 còn thuộc shot trước — làm tròn mốc thì fit gán nhầm khung đó cho shot sau."""
    f0 = math.ceil(shots[k]["t"] * 30.0 - 30e-9) if k > 0 else 0
    f1 = math.ceil(shots[k + 1]["t"] * 30.0 - 30e-9) if k + 1 < len(shots) else dur_f
    return range(max(0, f0), min(f1, dur_f))


def project(shots: list[dict[str, Any]], f: int, X: float, Y: float, duration_s: float | None = None) -> tuple[float, float]:
    """Chiếu toạ độ nguồn (X, Y) sang toạ độ đầu ra, khớp từng phép tính với Footage.tsx."""
    t = f / 30.0
    k = shot_at(shots, f)
    shot = shots[k]

    if k + 1 < len(shots):
        nxt_t = shots[k + 1]["t"]
    else:
        nxt_t = duration_s if duration_s is not None else shot["t"] + 1.0

    dur = nxt_t - shot["t"]
    p = min(1.0, max(0.0, (t - shot["t"]) / dur)) if dur > 1e-9 else 0.0
    scale = shot["s0"] + (shot["s1"] - shot["s0"]) * in_out(p)

    cut_f = f - round(shot["t"] * 30.0) if k > 0 else -1
    kick = (1.0 - cut_f / 5.0) * 0.018 if 0 <= cut_f < 5 and k > 0 else 0.0

    slack = (scale - 1.0) / 2.0
    shot_x = float(shot.get("x", 0.0))
    shot_y = float(shot.get("y", 0.0))
    dx = min(slack, max(-slack, shot_x)) * 1080.0
    dy = min(slack, max(-slack, shot_y)) * 1920.0

    total_scale = scale + kick
    X_prime = 540.0 + total_scale * (X - 540.0) + dx
    Y_prime = 614.4 + total_scale * (Y - 614.4) + dy
    return X_prime, Y_prime


def layers(lock: dict[str, Any], R: Any) -> list[dict[str, Any]]:
    """Cửa sổ hiện hình và biên nhả của từng lớp: [{"id", "kind", "frames": (f0, f1), "probe_f", "allow"}]."""
    fps = lock.get("fps", 30)
    dur_f = lock.get("duration_f", 0)
    settle_f = 12
    cta_f = 20

    exempt = set(R.get("face.exempt"))
    pill_pop = float(R.get("face.pill_pop_px"))
    exit_allow = R.get("face.exit_allow")

    block_rise = float(exit_allow.get("block", {}).get("rise_px", 20))
    block_blur = float(exit_allow.get("block", {}).get("blur_px", 12))
    steps_rise = float(exit_allow.get("steps", {}).get("rise_px", 26))
    steps_blur = float(exit_allow.get("steps", {}).get("blur_px", 16))

    res: list[dict[str, Any]] = []

    # Block layers
    for b in lock.get("blocks", []):
        ws = b.get("top", []) + b.get("hero", []) + b.get("bottom", [])
        if not ws:
            continue
        first_show = min(w["show"] for w in ws)
        last_show = max(w["show"] for w in ws)
        out_s = b["out"]
        exit_f = b.get("exit_f", 6)

        f0 = max(0, math.ceil(first_show * fps) - 2)
        f1 = min(dur_f - 1, math.floor(out_s * fps) + exit_f)

        probe_f = min(int(round(last_show * fps)) + settle_f, math.floor(out_s * fps + 1e-6))
        probe_f = min(max(probe_f, 0), dur_f - 1)

        def make_block_allow(o_s: float, ef: int, r_px: float, b_px: float):
            def allow_fn(f: int) -> float:
                out_f = o_s * fps
                if f <= out_f or ef <= 0:
                    return 0.0
                q = min(1.0, max(0.0, (f - out_f) / ef))
                return r_px * in_cubic(q) + b_px * q
            return allow_fn

        res.append({
            "id": b["id"],
            "kind": "block",
            "frames": (f0, f1),
            "probe_f": probe_f,
            "allow": make_block_allow(out_s, exit_f, block_rise, block_blur),
        })

    # Steps layer
    if lock.get("steps"):
        st = lock["steps"]
        in_s = st["in"]
        out_s = st["out"]
        f0 = max(0, int(round(in_s * fps)))
        f1 = min(dur_f - 1, int(round(out_s * fps)) + 8)
        probe_f = int(round((in_s + out_s) / 2.0 * fps))
        probe_f = min(max(probe_f, 0), dur_f - 1)

        def make_steps_allow(o_s: float, r_px: float, b_px: float):
            def allow_fn(f: int) -> float:
                out_f = o_s * fps
                if f <= out_f:
                    return 0.0
                q = min(1.0, max(0.0, (f - out_f) / 8.0))
                return r_px * q + b_px * q
            return allow_fn

        res.append({
            "id": "steps",
            "kind": "steps",
            "frames": (f0, f1),
            "probe_f": probe_f,
            "allow": make_steps_allow(out_s, steps_rise, steps_blur),
        })

    # CTA pill layer
    if lock.get("cta"):
        cta = lock["cta"]
        show_s = cta["show"]
        f0 = max(0, int(round(show_s * fps)))
        f1 = dur_f - 1
        probe_f = min(int(round(show_s * fps)) + cta_f, dur_f - 1)

        res.append({
            "id": "cta",
            "kind": "cta",
            "frames": (f0, f1),
            "probe_f": probe_f,
            "allow": lambda f: pill_pop,
        })

    # Hook layer
    if lock.get("hook"):
        hk = lock["hook"]
        land_s = hk.get("land", 0.34)
        out_s = hk.get("out", 1.08)
        end_s = hk.get("end", 1.5)
        probe_f = math.floor(out_s * fps)
        probe_f = min(max(probe_f, 0), dur_f - 1)

        res.append({
            "id": "hook",
            "kind": "hook",
            "frames": (0, min(dur_f - 1, int(round(end_s * fps)))),
            "probe_f": probe_f,
            "allow": lambda f: 0.0,
            "exempt": "hook" in exempt,
        })

    return res


def ceil4(x: float) -> float:
    """Làm tròn lên ở 4 chữ số thập phân (bước 0.0001)."""
    return math.ceil(x * 10000.0) / 10000.0


def read_alpha_from_file(png: Path) -> np.ndarray:
    """Đọc kênh alpha từ file PNG."""
    png = Path(png)
    width, height = struct.unpack(">II", png.read_bytes()[16:24])
    run = subprocess.run(["ffmpeg", "-v", "error", "-i", str(png), "-vf", "alphaextract",
                          "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True)
    if run.returncode != 0:
        raise ValueError("Không tách được alpha: %s" % run.stderr.decode("utf-8", "replace"))
    return np.frombuffer(run.stdout, dtype=np.uint8).reshape(height, width)


def _top_in_columns(alpha: np.ndarray, left: float, right: float, row_from: float) -> float | None:
    """Hàng trên cùng có alpha > 0 trong dải cột [left, right], chỉ xét từ hàng `row_from` trở xuống.
    Điểm ảnh nằm phía trên `row_from` (vd viên CTA trên trán lọt vào ảnh dò của thẻ cuối) bị bỏ qua."""
    h, w = alpha.shape
    c0, c1 = max(0, int(math.floor(left))), min(w - 1, int(math.ceil(right)))
    r0 = max(0, int(math.floor(row_from)))
    if c0 > c1 or r0 >= h:
        return None
    rows = np.flatnonzero(alpha[r0:, c0:c1 + 1].any(axis=1))
    return float(r0 + rows[0]) if rows.size else None


def _covered(lock: dict[str, Any]) -> set[int]:
    """Tập các khung hình bị B-roll che: b['f_in'] <= f < b['f_out']."""
    covered = set()
    for b in lock.get("broll") or []:
        for f in range(int(b.get("f_in", 0)), int(b.get("f_out", 0))):
            covered.add(f)
    return covered


def fit(lock: dict[str, Any], face_rows: list[list[Any]], R: Any, masks: dict[str, np.ndarray] | None = None) -> dict[str, Any]:
    """Khớp tỉ lệ và dịch y cho từng shot theo spec 1.1.1 §8.3.

    Luật miệng: FAIL khi điểm ảnh alpha > 0 của một lớp đang hiện (không phải hook, không phải viên CTA)
    nằm trong hộp miệng nới `face.margin_px` — chỉ xét điểm ảnh từ mép trên hộp miệng trở xuống, trong các
    cột miệng. Viên CTA chỉ so với sàn mắt: mép trên hộp mắt phải ≥ max(face.eye_top_min_px, đáy viên + lề).
    Trả thêm `layers`: mỗi lớp đã kiểm một dòng {id, min_gap_px, worst_frame} (âm = đè)."""
    fps = lock.get("fps", 30)
    shots = [dict(s) for s in lock["shots"]]
    n_shots = len(shots)
    dur_f = lock["duration_f"]
    dur_s = dur_f / fps
    all_layers = layers(lock, R)
    covered_f = _covered(lock)
    margin_px = float(R.get("face.margin_px"))
    cap_floor = float(R.get("face.cap_floor"))
    bump_max = float(R.get("face.bump_max"))
    scale_step = float(R.get("face.scale_step"))
    close_min = float(R.get("text.close_min"))
    cut_jump = float(R.get("sfx.cut_jump"))
    eye_top_min_px = float(R.get("face.eye_top_min_px"))

    layer_masks = masks or {}
    layer_info: dict[str, dict[str, Any]] = {}
    for ly in all_layers:
        alpha = layer_masks.get(ly["id"])
        if alpha is None:
            continue
        ys = np.flatnonzero(alpha.any(axis=1))
        if not ys.size:
            continue
        y1 = int(ys[-1])
        if ly["id"] == "cta":
            # Ảnh dò chụp mọi lớp chữ đang hiện; viên CTA là khối trên cùng, tách phụ đề bên dưới bằng hàng
            # trống ⇒ đáy viên là cuối dải hàng liền đầu tiên (không phải đáy phụ đề).
            gaps = np.flatnonzero(np.diff(ys) > 1)
            y1 = int(ys[gaps[0]]) if gaps.size else y1
        layer_info[ly["id"]] = {"y0": int(ys[0]), "y1": y1, "alpha": alpha}

    band_cache: dict[int, Any] = {}

    def band_at(f: int):
        if f not in band_cache:
            band_cache[f] = bands(face_rows, f, R)
        return band_cache[f]

    def visible(f: int, kind: str | None = None):
        for ly in all_layers:
            if ly.get("exempt") or ly["id"] == "hook" or ly["id"] not in layer_info:
                continue
            if kind == "cta" and ly["id"] != "cta":
                continue
            if kind == "text" and ly["id"] == "cta":
                continue
            if ly["frames"][0] <= f <= ly["frames"][1]:
                yield ly

    def mouth_box(temp_shots, f, b_f):
        mx0, my0, mx1, my1 = b_f["mouth"]
        _, my0_p = project(temp_shots, f, 540.0, my0, duration_s=dur_s)
        _, my1_p = project(temp_shots, f, 540.0, my1, duration_s=dur_s)
        mx0_p, _ = project(temp_shots, f, mx0, 614.4, duration_s=dur_s)
        mx1_p, _ = project(temp_shots, f, mx1, 614.4, duration_s=dur_s)
        return (min(mx0_p, mx1_p) - margin_px, my0_p - margin_px,
                max(mx0_p, mx1_p) + margin_px, my1_p + margin_px)

    def mouth_overlap(ly, f, box):
        """> 0 = số px lớp đè vào hộp miệng đã nới lề; None = không có điểm ảnh nào dưới mép trên hộp."""
        left, top, right, bottom = box
        text_top = _top_in_columns(layer_info[ly["id"]]["alpha"], left, right, top)
        if text_top is None:
            return None
        return bottom - text_top - ly["allow"](f)

    def eye_floor_overlap(temp_shots, f, b_f):
        """> 0 = số px mép trên hộp mắt nằm trên sàn cho phép lúc viên CTA hiện."""
        _, eye_top = project(temp_shots, f, 540.0, b_f["eyes"][1], duration_s=dur_s)
        pill_bottom = layer_info["cta"]["y1"] + margin_px
        return max(eye_top_min_px, pill_bottom) - eye_top

    fitted_shots = []
    all_violations = []
    layer_report: dict[str, tuple[float, int]] = {}

    for k in range(n_shots):
        orig_s0 = shots[k]["s0"]
        orig_s1 = shots[k]["s1"]

        # Cắt kề
        has_prev_cut = (k > 0)
        has_next_cut = (k < n_shots - 1)
        orig_jump_prev = (abs(orig_s0 - shots[k - 1]["s1"]) >= cut_jump) if has_prev_cut else None
        orig_jump_next = (abs(shots[k + 1]["s0"] - orig_s1) >= cut_jump) if has_next_cut else None

        # Tập ứng viên: C0, CAP(d), BUMP(d)
        cands: list[tuple[float, float, str]] = [(orig_s0, orig_s1, "C0")]
        d = scale_step
        while orig_s1 - d >= max(orig_s0, cap_floor) - 1e-9:
            cands.append((orig_s0, round(orig_s1 - d, 4), f"CAP({d:.2f})"))
            d += scale_step
        if max(orig_s0, orig_s1) < close_min - 1e-9:
            d = scale_step
            while d <= min(bump_max, orig_s1 - orig_s0) + 1e-9:
                cands.append((round(orig_s0 + d, 4), orig_s1, f"BUMP({d:.2f})"))
                d += scale_step

        # Loại ứng viên làm đổi kết luận |ds| >= cut_jump ở cắt kề (giữ nguyên tập cú cắt có SFX)
        valid_cands = []
        for s0_c, s1_c, lever in cands:
            if has_prev_cut and (abs(s0_c - shots[k - 1]["s1"]) >= cut_jump) != orig_jump_prev:
                continue
            if has_next_cut and (abs(shots[k + 1]["s0"] - s1_c) >= cut_jump) != orig_jump_next:
                continue
            valid_cands.append((s0_c, s1_c, lever))

        shot_frames = list(frames_of_shot(shots, k, dur_f))

        winning_cand = None
        best_c0_res = None

        for cand_idx, (s0_c, s1_c, lever) in enumerate(valid_cands):
            temp_shot = dict(shots[k], s0=s0_c, s1=s1_c, y=0.0)
            temp_shots = list(shots)
            temp_shots[k] = temp_shot

            # need ở y = 0: số px phải nâng khung để mọi lớp chữ rời hộp miệng
            max_need = 0.0
            for f in shot_frames:
                if f in covered_f:
                    continue
                b_f = band_at(f)
                if not b_f:
                    continue
                box = mouth_box(temp_shots, f, b_f)
                for ly in visible(f, "text"):
                    need = mouth_overlap(ly, f, box)
                    if need is not None and need > max_need:
                        max_need = need

            slack = (max(s0_c, s1_c) - 1.0) / 2.0
            y_cand = min(0.0, max(-slack, -ceil4(max_need / 1920.0))) if max_need > 0 else 0.0

            # Trần mắt (dạng đóng): nâng khung không được đẩy mắt lên quá sàn lúc viên CTA hiện
            for f in shot_frames:
                if f in covered_f:
                    continue
                b_f = band_at(f)
                if not b_f:
                    continue
                pill_on = "cta" in layer_info and any(True for _ in visible(f, "cta"))
                req_eye_top = max(eye_top_min_px, (layer_info["cta"]["y1"] + margin_px) if pill_on else 0.0)
                temp_shot["y"] = 0.0
                _, eye_top_0 = project(temp_shots, f, 540.0, b_f["eyes"][1], duration_s=dur_s)
                needed_y_for_eye = (req_eye_top - eye_top_0) / 1920.0
                if needed_y_for_eye > y_cand:
                    y_cand = min(0.0, max(-slack, ceil4(needed_y_for_eye)))

            # Kiểm ở (s0_c, s1_c, y_cand)
            temp_shot["y"] = y_cand
            cand_violations = []
            cand_gaps: dict[str, tuple[float, int]] = {}
            for f in shot_frames:
                if f in covered_f:
                    continue
                b_f = band_at(f)
                if not b_f:
                    continue
                box = mouth_box(temp_shots, f, b_f)
                for ly in visible(f):
                    if ly["id"] == "cta":
                        diff = eye_floor_overlap(temp_shots, f, b_f)
                    else:
                        diff = mouth_overlap(ly, f, box)
                        if diff is None:
                            continue
                    gap = -diff
                    if ly["id"] not in cand_gaps or gap < cand_gaps[ly["id"]][0]:
                        cand_gaps[ly["id"]] = (gap, f)
                    if diff > 1e-4:
                        cand_violations.append({"layer": ly["id"], "shot": k, "frame": f,
                                                "overlap_px": round(diff, 1)})

            res_cand = {"k": k, "base": [orig_s0, orig_s1], "fitted": [s0_c, s1_c, round(y_cand, 4)],
                        "lever": lever, "violations": cand_violations, "gaps": cand_gaps}
            if cand_idx == 0:
                best_c0_res = res_cand
            if not cand_violations:
                winning_cand = res_cand
                break

        final_choice = winning_cand or best_c0_res
        shots[k]["s0"], shots[k]["s1"], shots[k]["y"] = final_choice["fitted"]
        fitted_shots.append({"k": k, "base": final_choice["base"], "fitted": final_choice["fitted"],
                             "lever": final_choice["lever"]})
        all_violations.extend(final_choice["violations"])
        for lid, (gap, f) in final_choice["gaps"].items():
            if lid not in layer_report or gap < layer_report[lid][0]:
                layer_report[lid] = (gap, f)

    return {
        "shots": fitted_shots,
        "violations": all_violations,
        "layers": [{"id": lid, "min_gap_px": round(gap, 1), "worst_frame": f}
                   for lid, (gap, f) in sorted(layer_report.items(), key=lambda kv: kv[1][0])],
        "new_lock_shots": shots,
    }


def room_suggestions(block: dict[str, Any], ctx: Any, R: Any) -> tuple[int | None, tuple[int, int] | None]:
    """Ứng viên sửa FACE_ROOM cho một thẻ edit.json: (breaks, hero) — build._face_room_lines còn chạy thử
    PLAN --check từng ứng viên trước khi in.

    hero (R124): giữ cụm có nghĩa, dựng MỘT hàng. Hero hiện tại dài hơn text.hero_one_row_chars (≤
    text.hero_row_max_chars) và chưa là hero_row ⇒ gợi ý chính nó (ghi đè cùng khoảng thì compose đánh dấu
    hero_row). Còn lại ⇒ segment.pick_hero với max_chars = hero_row_max_chars nếu khác hero hiện tại.
    breaks: mép dòng thật bên trong thẻ gần giữa thẻ nhất — tách thì mỗi thẻ con bớt tầng."""
    from . import segment
    ranges = [block[key] for key in ("top", "hero", "bottom") if block.get(key)]
    if not ranges:
        return None, None
    a, b = min(r[0] for r in ranges), max(r[1] for r in ranges)
    edges = sorted({r[1] for r in ranges if a < r[1] < b})
    best_break = min(edges, key=lambda e: (abs(e - (a + b) / 2), e)) if edges else None

    h0, h1 = block["hero"]
    disp = block.get("display") or {}
    chars = len(" ".join(disp.get(str(k), str(ctx.words[k]["w"])) for k in range(h0, h1)))
    row_max = int(R.get("text.hero_row_max_chars"))
    if not block.get("hero_row") and int(R.get("text.hero_one_row_chars")) < chars <= row_max:
        return best_break, (h0, h1)
    pick = tuple(segment.pick_hero(ctx, a, b, max_chars=row_max))
    return best_break, (pick if pick != (h0, h1) else None)


def face_room_error(layer_id: str, px: float, k: int, s0: float, s1: float,
                    f0: int, f1: int, best_break_k: int | None = None,
                    hero_span: str | None = None, shot_label: str = "toàn",
                    other_fix: str | None = None) -> str:
    """Format nguyên văn thông báo FACE_ROOM; chỉ in phương án có thật (không in "breaks": [] rỗng).
    Hero đứng trước: giữ cụm có nghĩa, dựng một hàng (R124)."""
    fixes = []
    if hero_span:
        fixes.append(f'"hero": [{hero_span}] (một hàng)')
    if best_break_k is not None:
        fixes.append(f'"breaks": [{best_break_k}]')
    if other_fix:
        fixes.append(other_fix)
    fix = " hoặc ".join(fixes) if fixes else "không có gợi ý tự động — xem bảng mã trong PLAN.md"
    return (f'FACE_ROOM {layer_id} che miệng {int(round(px))} px ở shot {k} '
            f'({shot_label} {s0:.2f}→{s1:.2f}, f{f0}–f{f1}) — Sửa: {fix}')
