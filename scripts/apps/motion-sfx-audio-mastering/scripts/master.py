"""Master âm của file giao (A.10 của master prompt): loudnorm hai lượt, chỉ nhận chế độ linear. Chạy từ thư mục dự án:

  python master.py <raw.mp4> <file giao.mp4> [--I -16 --TP -2.5] [--voice assets/video/aroll.mp4]

- Lượt 1 đo. Linear chỉ khả thi khi input_tp + (I − input_i) ≤ TP; không thì loudnorm tự nén động mà không báo.
- Không khả thi: in 8 điểm true peak cao nhất của bản raw (oversample 4×, cửa sổ 50 ms), kèm đỉnh giọng của --voice cùng
  cửa sổ, rồi thoát mã 2 mà không ghi file. Đỉnh cao hơn giọng nhiều là SFX/nhạc cần hạ; đỉnh sát giọng ở mọi nơi là
  ca sát biên: hạ I khoảng 0,1 và ghi lý do (B8: mix −1.69 dBTP vì tick trùng đỉnh giọng → hạ tick và whoosh, render
  lại; lần sau thiếu đúng làm tròn → master ở I −16.1, file giao đo −16.0 LUFS).
- Khả thi: lượt 2 (hình chép nguyên, tiếng AAC 256k 48 kHz), kiểm "normalization_type": "linear", rồi đo file giao bằng
  ebur128 (I, true peak, LRA). TP đặt thấp hơn mục tiêu brief 0,5 dB vì AAC làm true peak tăng.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
TP_SR = 192000   # 4× oversampling of 48 kHz, as for a true-peak meter


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def loudnorm_json(text):
    blocks = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", text, re.S)
    if not blocks:
        raise SystemExit("không đọc được JSON của loudnorm")
    return json.loads(blocks[-1])


def pcm(path):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(path), "-vn", "-ac", "2", "-ar", str(TP_SR),
                          "-af", "aresample=resampler=soxr", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.abs(np.frombuffer(raw, dtype=np.float32).reshape(-1, 2)).max(axis=1)


def hotspots(raw, voice, n=8, win=0.05, gap=0.3):
    """Print the n loudest 50 ms windows (true peak dBTP), at least gap seconds apart, with the voice peak there."""
    a = pcm(raw)
    v = pcm(voice) if voice and pathlib.Path(voice).is_file() else None
    k = int(win * TP_SR)
    m = len(a) // k
    blk = a[: m * k].reshape(m, k).max(axis=1)
    picked = []
    print("điểm true peak cao nhất (giây, dBTP của bản raw, đỉnh giọng cùng cửa sổ):")
    for i in np.argsort(blk)[::-1]:
        t = i * win
        if any(abs(t - p) < gap for p in picked):
            continue
        picked.append(t)
        note = ""
        if v is not None and (i + 1) * k <= len(v):
            note = f"  giọng {20 * np.log10(v[i * k:(i + 1) * k].max() + 1e-12):6.2f}"
        print(f"  {t:7.2f}  {20 * np.log10(blk[i] + 1e-12):6.2f}{note}")
        if len(picked) == n:
            break


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw")
    ap.add_argument("out")
    ap.add_argument("--I", type=float, default=-16.0)
    ap.add_argument("--TP", type=float, default=-2.5)
    ap.add_argument("--voice", default="assets/video/aroll.mp4")
    a = ap.parse_args()
    p1 = run(["ffmpeg", "-nostdin", "-hide_banner", "-i", a.raw, "-vn", "-af",
              f"loudnorm=I={a.I}:TP={a.TP}:LRA=50:print_format=json", "-f", "null", "-"])
    m = loudnorm_json(p1.stderr)
    print("lượt 1:", {k: m[k] for k in ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")})
    need = float(m["input_tp"]) + (a.I - float(m["input_i"]))
    print(f"điều kiện linear: input_tp + (I - input_i) = {need:.2f} <= TP {a.TP} ? {'có' if need <= a.TP else 'KHÔNG'}")
    if need > a.TP:
        hotspots(a.raw, a.voice)
        print("linear không khả thi: hạ SFX/nhạc ở các điểm trên rồi render lại, hoặc hạ I và ghi lý do (A.10)")
        if need - a.TP < 0.05:
            print(f"sát biên ({need - a.TP:+.3f} dB): hạ I đi 0,1 (--I {a.I - 0.1:g}) là đủ; ghi lý do vào BRIEF")
        return 2
    af = (f"loudnorm=I={a.I}:TP={a.TP}:LRA=50:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:"
          f"linear=true:print_format=json,aresample=48000")
    p2 = run(["ffmpeg", "-nostdin", "-hide_banner", "-y", "-i", a.raw, "-map", "0:v", "-map", "0:a", "-c:v", "copy",
              "-af", af, "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", a.out])
    if p2.returncode:
        print(p2.stderr[-2000:])
        pathlib.Path(a.out).unlink(missing_ok=True)
        return 2
    m2 = loudnorm_json(p2.stderr)
    print("lượt 2 normalization_type:", m2.get("normalization_type"))
    if m2.get("normalization_type") != "linear":
        pathlib.Path(a.out).unlink(missing_ok=True)
        print("lượt 2 KHÔNG linear: loudnorm đã nén động; đã xóa file vừa ghi")
        return 2
    p3 = run(["ffmpeg", "-nostdin", "-hide_banner", "-i", a.out, "-vn", "-filter_complex", "ebur128=peak=true", "-f", "null", "-"])
    summ = p3.stderr[p3.stderr.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", summ)
    tp = re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ)
    lra = re.search(r"LRA:\s+(-?[\d.]+) LU", summ)
    print(f"file giao: I {i.group(1) if i else '?'} LUFS, true peak {tp.group(1) if tp else '?'} dBTP, "
          f"LRA {lra.group(1) if lra else '?'} LU")
    return 0


if __name__ == "__main__":
    sys.exit(main())
