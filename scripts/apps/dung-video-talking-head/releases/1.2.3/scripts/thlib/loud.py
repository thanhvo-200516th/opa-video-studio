"""thlib.loud — phần dùng chung của loudnorm 2 lượt tuyến tính qua ffmpeg: chạy
ffmpeg, đọc JSON loudnorm, khâu đỉnh trước loudnorm. Dùng cho chuỗi giọng S28
(voice.py, Ruling R9) và bản final / nobgm / social S18 (mix.py, Ruling R19; bản xuất
theo Ruling R35: limiter true-peak + vòng mã hoá–đo–hạ trần, mix.loudnorm_encoded).
"""

from __future__ import annotations

import json
import re
import subprocess

from .audio import SR

# loudnorm: S18/S28 chỉ chốt I và TP; LRA đích giữ 11 LU như task brief.
LOUDNORM_LRA = 11
# Trần limiter trước loudnorm = TP đích − biên này (dB). Sau chuỗi S28, 56/58
# video HeyGen có TP − I = 14,0–16,3 dB, quá mức loudnorm tuyến tính chịu được
# (TP đích − I đích = 14 dB). Biên phủ true-peak vượt mẫu + I mất do limiter
# (đo trên 58 video: TP vượt ≈ 0, I mất ≤ 0,08 LU, còn ≥ 0,42 dB tới ngưỡng).
# Mix giọng video 2 + 4 bài nền (R19): I mất ≤ 0,19 LU ở social −14, TP ra ≤ −1,67.
LIMIT_MARGIN_DB = 0.5
# Limiter true-peak của final / nobgm (build.py) và social (mux.py): SFX nhiều cao tần vọt
# đỉnh giữa hai mẫu mà limiter theo mẫu không thấy (true peak BS.1770 đo ở 4×).
TP_OVERSAMPLE = 4
# Bộ mã tiếng của ba bản xuất (mux.py); cổng mix của BUILD mã hoá thử bằng đúng tham số này.
AAC_ARGS = ("-c:a", "aac", "-b:a", "192k", "-ar", str(SR))
# Vòng R35 của ba bản xuất (mix.loudnorm_encoded): bộ mã aac còn vọt TP sau mã hoá (+0,1…+0,4 dB
# một thế hệ AAC, đo trên 6 dự án) ⇒ TP bản đã mã hoá còn vượt đích thì hạ trần limiter đúng phần
# vượt + TP_STEP_DB rồi làm lại, tối đa TP_TRIES lần.
TP_TRIES = 3
TP_STEP_DB = 0.1

_JSON_BLOCK_RE = re.compile(r"\{[^{}]*\}")


def num(value) -> str:
    """Số gọn cho tham số ffmpeg: 110 -> '110', -6.0 -> '-6', 3.5 -> '3.5'."""
    return f"{value:g}"


def peak_stage(target_lufs: float, tp_dbtp: float, measured_i: float,
               margin_db: float = LIMIT_MARGIN_DB, oversample: int = 1) -> str:
    """Khâu đỉnh trước loudnorm: đưa tín hiệu có I = `measured_i` về I đích rồi
    limiter lookahead (mặc định attack 5 ms, release 50 ms) ở trần TP đích −
    `margin_db`, để lượt áp giữ được chế độ tuyến tính. latency=true bù trễ lookahead
    (giữ xcorr); level=false tắt tự nâng mức đầu ra lên trần. `oversample` > 1: limiter
    chạy ở SR × oversample rồi hạ về SR, nên chặn cả đỉnh giữa hai mẫu (true peak
    BS.1770 đo ở 4×) — bản final / nobgm / social cần (TP_OVERSAMPLE) vì cú đập SFX nhiều
    cao tần vọt đỉnh giữa hai mẫu."""
    limit = 10 ** ((tp_dbtp - margin_db) / 20)
    stage = (f"volume={num(target_lufs - measured_i)}dB,"
             f"alimiter=limit={num(limit)}:level=false:latency=true")
    if oversample > 1:
        stage = f"aresample={SR * oversample},{stage},aresample={SR}"
    return stage


def ffmpeg(args: list[str]) -> str:
    """Chạy ffmpeg, trả về stderr (nơi loudnorm in JSON); lỗi thì ném
    RuntimeError kèm đoạn cuối log để người đọc biết vì sao."""
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg lỗi (mã {proc.returncode}): {proc.stderr[-800:]}")
    return proc.stderr


def loudnorm_json(stderr: str) -> dict:
    """Khối JSON cuối cùng loudnorm in ra stderr khi print_format=json."""
    for block in reversed(_JSON_BLOCK_RE.findall(stderr)):
        try:
            stats = json.loads(block)
        except json.JSONDecodeError:
            continue
        if "input_i" in stats:
            return stats
    raise RuntimeError("Không tìm thấy khối JSON của loudnorm trong log ffmpeg")
