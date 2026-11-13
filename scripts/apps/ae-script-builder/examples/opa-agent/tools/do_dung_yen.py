"""Đo khung đứng yên của MP4: chênh lệch trung bình giữa hai khung liền nhau (ảnh xám 192×108).

Một khung "đứng yên" khi chênh lệch < NGUONG (mức xám 0–255). Báo % khung đứng yên trong từng ô 2 s,
ô vượt 15 % bị đánh dấu (chỉ số chống "nhàm" Minh chốt). Kèm đỉnh chuyển động để soát nhịp không vọt.
Chạy: python -I tools/do_dung_yen.py out/review/KHUNG-36s_v08.mp4
"""
import subprocess
import sys

W, H, FPS, NGUONG, O_GIAY, TRAN = 192, 108, 30, 0.25, 2, 15.0


def frames(path: str):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={W}:{H}:flags=area,format=gray", "-f", "rawvideo", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    size = W * H
    while True:
        buf = proc.stdout.read(size)
        if len(buf) < size:
            break
        yield buf
    proc.wait()


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    diffs, prev = [], None
    for f in frames(sys.argv[1]):
        if prev is not None:
            diffs.append(sum(abs(a - b) for a, b in zip(f, prev)) / len(f))
        prev = f
    n = O_GIAY * FPS
    print(f"{len(diffs) + 1} khung · ngưỡng đứng yên {NGUONG} mức xám · ô {O_GIAY} s · trần {TRAN:g} %")
    bad = 0
    for k in range(0, len(diffs), n):
        win = diffs[k:k + n]
        still = 100 * sum(d < NGUONG for d in win) / len(win)
        mark = "  ← VƯỢT" if still > TRAN else ""
        bad += still > TRAN
        print(f"{k / FPS:5.1f}–{(k + len(win)) / FPS:5.1f} s: đứng yên {still:5.1f} %, chuyển động TB {sum(win) / len(win):5.2f}, đỉnh {max(win):6.2f}{mark}")
    print(f"KẾT QUẢ: {bad} ô vượt trần" + ("" if bad else " (đạt)"))


if __name__ == "__main__":
    main()
