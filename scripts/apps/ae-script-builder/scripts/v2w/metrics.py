#!/usr/bin/env python3
"""Đo chuyển động trên MP4 bản 16:9 (NN §1, §8.7).

Chạy:  python tools/v2w/metrics.py <mp4> [--t0 7.5] [--declared 9.2:9.6 ...] [--exempt 28.333:30 ...]
                                    [--json out.json] [--md out.md] [--test test-2] [--no-flow]
Cách đo: giải mã về xám 960×540 (ffmpeg, pipe, đọc từng frame). Điểm ảnh "đổi" khi lệch > 6 mức.
  Tĩnh B = frame có ≤ 0,5 % điểm đổi so với f − lag (lag = fps/30, tức 1/30 s); Tĩnh A = ≤ 0,04 %.
  Cắt cứng = > 30 % điểm đổi so với f − 1, đồng thời f − 1 và f + 1 đổi < 1/3 mức đó.
  Ô 2 s căn theo giây chẵn của PHIM (t = t0 + i/fps); ô ngắn hơn 1 s gộp vào ô kề.
  Độ dời: bám điểm góc f − 1 → f (Lucas–Kanade tháp, kiểm xuôi–ngược < 1 px; xem scan_video.py vì sao không Farneback),
    px khung GỐC mỗi frame: dispP50 = trung vị (theo frame) của trung vị; dispP95 = lớn nhất (theo frame) của phân vị 95
    = "độ dời lớn nhất mỗi frame" (totals.maxDisp); dispMax = lớn nhất thô (có thể là vật nhỏ bay nhanh). Chỉ báo.
Ngưỡng FAIL: ô có Tĩnh B > 15 % (ô chạm khoảng khai báo: frame khai báo bị loại, và cả ô ≤ 30 %); cả đoạn > 10 %;
  Tĩnh A > 0; chuỗi Tĩnh B > 12 f60 (0,2 s); cắt cứng > 0. Frame khai báo vẫn được báo.
  --exempt: khoảng miễn hẳn (khung CTA cuối của phim đủ, NN §1): frame bỏ khỏi mọi ngưỡng, ô không bị luật 30 %.
  Phim đủ 30 s (1800 frame) chạy được nguyên: quét giữ số liệu từng frame, không giữ ảnh.
Exit:  0 đạt, 1 trượt ngưỡng, 2 lỗi đầu vào (thiếu file, ffmpeg/ffprobe lỗi).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from metrics_core import Span, analyze, markdown  # noqa: E402
from scan_video import InputError, scan  # noqa: E402


def parse_span(text: str) -> Span:
    try:
        a, b = (float(x) for x in text.split(":"))
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"khoảng khai báo sai: {text} (dạng a:b)") from e
    if not a < b:
        raise argparse.ArgumentTypeError(f"khoảng khai báo sai: {text} (cần a < b)")
    return a, b


def run(video: Path, t0: float, declared: list[Span], test: str, flow: bool = True,
        json_out: Path | None = None, md_out: Path | None = None, exempt: list[Span] | None = None) -> dict:
    """Quét + phân tích + ghi file. Ném InputError khi đầu vào hỏng."""
    if not video.is_file():
        raise InputError(f"không có file {video}")
    r = analyze(scan(video, flow=flow), t0, declared, test or video.stem, exempt or [])
    for p, text in ((json_out, json.dumps(r, ensure_ascii=False, indent=2)), (md_out, markdown(r))):
        if p:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
    return r


def summary(r: dict) -> str:
    t = r["totals"]
    lines = [f"{r['test']}: Tĩnh B {t['tinhB']} % · Tĩnh A {t['tinhA']} · chuỗi {t['longestRun']} f · "
             f"dời max {t['maxDisp']} px/f · cắt cứng {len(r['hardCuts'])} → {'ĐẠT' if r['pass'] else 'TRƯỢT'}"]
    lines += [f"  [{w['from']:g}; {w['to']:g}) Tĩnh B {w['tinhB']} % (bỏ khai báo {w['tinhBEff']} %) · dời P50/P95/max "
              f"{w['dispP50']}/{w['dispP95']}/{w['dispMax']} · chuỗi {w['longestRun']} {'ĐẠT' if w['pass'] else 'TRƯỢT'}"
              for w in r["windows"]]
    lines += [f"  TRƯỢT: {f}" for f in r["fails"]] + [f"  {w}" for w in r["warns"]]
    return "\n".join(lines)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Đo % frame đứng yên theo ô 2 s và độ dời mỗi frame trên MP4")
    ap.add_argument("video", type=Path)
    ap.add_argument("--t0", type=float, default=0.0, help="giây toàn phim của frame 0")
    ap.add_argument("--declared", type=parse_span, action="append", default=[], help="khoảng khai báo a:b (giây phim)")
    ap.add_argument("--exempt", type=parse_span, action="append", default=[], help="khoảng miễn hẳn a:b (giây phim)")
    ap.add_argument("--test", default="", help="tên hiển thị")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--md", type=Path)
    ap.add_argument("--no-flow", action="store_true")
    a = ap.parse_args()
    try:
        r = run(a.video, a.t0, a.declared, a.test, not a.no_flow, a.json, a.md, a.exempt)
    except InputError as e:
        print(f"LỖI: {e}", file=sys.stderr)
        return 2
    print(summary(r))
    return 0 if r["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
