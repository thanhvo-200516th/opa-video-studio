"""Clip Muse dài giữ bối cảnh: nối nhiều đoạn 5–10 s, khung cuối đoạn trước làm khung đầu đoạn sau.

Đo 2026-11-02: một video Muse 30–60 s liền thì bối cảnh trôi (đạo cụ / góc máy / cửa sổ đổi dần); 10 s thì liền mạch.
Các đoạn tạo lần lượt (đoạn sau cần khung cuối đoạn trước) → ~1,5–2,3 phút / đoạn. Đoạn đã có thì dùng lại.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path

import numpy as np
from PIL import Image

import media

# Đo 2026-11-02: prompt có chuyển động máy (push-in…) làm bối cảnh trôi cả khi nối đoạn — máy vào cận rồi lùi ra thì Muse vẽ lại
# xung quanh. Clip nối giữ máy đứng yên, chỉ chủ thể cử động.
STATIC = (" Locked-off static camera on a tripod, the framing stays exactly the same for the whole shot, "
          "only natural subject movement")
CONTINUE = (" Continuous shot continuing exactly from the first frame: same person, same clothes, same room, "
            "same props, same lighting and color, no scene change")


def plan_segments(total: float, seg: int = 8, fade: float = 0.2, lo: int = 5, hi: int = 10) -> list[int]:
    """Độ dài (giây, số nguyên trong [lo, hi]) từng đoạn sao cho tổng trừ phần chồng chuyển mờ ≥ total."""
    seg = min(max(seg, lo), hi)
    n = max(1, math.ceil((total - fade) / (seg - fade)))
    each = min(max(math.ceil((total + (n - 1) * fade) / n), lo), hi)
    return [each] * n


def seam_diff(a: Path, b_video: Path) -> float:
    """Độ lệch trung bình (0–255) giữa khung cuối đoạn trước và khung đầu đoạn sau — đo mối nối."""
    first = media.frame(b_video, 0.0, 160)
    with Image.open(a) as im:
        last = im.convert("RGB").resize(first.size)
    return round(float(np.abs(np.asarray(last, np.float32) - np.asarray(first, np.float32)).mean()), 1)


SEAM_MAX = 20.0          # lệch mối nối (0–255) quá mức này = Muse không bám khung đầu → tạo lại
RETRIES = 2


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _segment(text: str, frame_in: Path, part: Path, sec: int, seen: set, log, check_seam: bool = True) -> tuple[float, int]:
    """Tạo một đoạn; trùng đoạn trước hoặc lệch mối nối > SEAM_MAX thì tạo lại (tối đa RETRIES lần), giữ bản khớp nhất.
    Đoạn 1 không kiểm lệch (ảnh khung đầu không nằm trong clip — Muse thường lệch ảnh ~20–28/255 mà không thành mối nối)."""
    import muse
    best = None
    for attempt in range(RETRIES + 1):
        tmp = part.with_name(f"{part.stem}_thu{attempt}.mp4")
        muse.generate_video(text, frame_in, tmp, seconds=sec, attempt=attempt)
        dup, diff = _md5(tmp) in seen, seam_diff(frame_in, tmp)
        score = diff + (1000 if dup else 0)
        if best is None or score < best[0]:
            if best:
                best[1].unlink()
            best = (score, tmp, diff)
        else:
            tmp.unlink()
        if not dup and (not check_seam or diff <= SEAM_MAX):
            break
        log(f"      lần {attempt + 1}: {'trùng đoạn trước' if dup else f'lệch mối nối {diff}'} → tạo lại")
    best[1].rename(part)
    seen.add(_md5(part))
    return best[2], attempt + 1


def muse_chain(prompt: str, first_png: Path, out_mp4: Path, total: float, seg: int = 8, steps: list[str] | None = None,
               fade: float = 0.2, static: bool = True, log=print) -> dict:
    """Ảnh khung đầu → n đoạn Muse nối tiếp → `out_mp4` dài `total` giây. steps: prompt riêng từng đoạn (thiếu thì lặp cái cuối).
    Mỗi đoạn kiểm ngay: trùng / không bám khung đầu thì tạo lại."""
    lens = plan_segments(total, seg, fade)
    work = out_mp4.with_name(out_mp4.stem + "_doan")
    work.mkdir(parents=True, exist_ok=True)
    parts, seams, tries, seen, frame_in = [], [], [], set(), first_png
    for i, sec in enumerate(lens, 1):
        part = work / f"doan{i:02d}_{sec}s.mp4"
        text = ((steps[min(i - 1, len(steps) - 1)] if steps else prompt) + (CONTINUE if i > 1 else "") + (STATIC if static else "")
                + f" Part {i} of {len(lens)}.")
        if part.exists():
            log(f"    đoạn {i}/{len(lens)}: dùng lại {part.name}")
            diff, n = seam_diff(frame_in, part), 0
            seen.add(_md5(part))
        else:
            log(f"    đoạn {i}/{len(lens)}: Muse {sec} s…")
            diff, n = _segment(text, frame_in, part, sec, seen, log, check_seam=i > 1)
        seams.append(diff)
        tries.append(n)
        parts.append(part)
        frame_in = media.last_frame(part, work / f"doan{i:02d}_cuoi.png")
    media.concat_xfade(parts, out_mp4, fade, total)
    log(f"    nối {len(parts)} đoạn {lens} → {out_mp4.name}; lệch khung đầu từng đoạn (0–255): {seams}; số lần tạo: {tries}")
    return {"segments": lens, "fade": fade, "static": static, "seam_diff": seams, "tries": tries, "parts_dir": str(work)}
