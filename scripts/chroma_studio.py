#!/usr/bin/env python3
"""chroma_studio — tách phông xanh từ clip GỐC (4K ngang) → xoay 9:16 → phóng nhân vật → ghép nền studio (luật D11, D12).

    ~/.venvs/video-skills/bin/python chroma_studio.py SRC.MP4 OUT.mp4 PLATE.png DUR [speed=1.0] [zoom=1.3] [start=0.2]

- SRC: file gốc phông xanh trong `Source/soucre thô/soucre 2/C00xx.MP4` (KHÔNG dùng `Footage_SoucreTho_*_Keyed.mp4`: người đã dính nền B-roll mờ,
  tách lại ra cánh tay bị cắt, viền trắng, ghế trong suốt — lỗi đo ngày 2026-11-12).
- Matte = độ xanh trội g − max(r, b): alpha = 1 − clip((d − 3) / 17); giữ thành phần liên thông lớn nhất (bỏ tường, kẹp phông);
  co 1 px + làm mờ 1 px; khử ám xanh g = min(g, max(r, b)). KHÔNG lấp lỗ trong thân (lấp lỗ làm lộ vệt xanh giữa tay và ghế).
- Phóng quanh đỉnh đầu: đầu ở 36 % chiều cao, người nằm ở 2/3 dưới. DUR theo thời lượng bản Keyed cũ (hoặc media cần thay): tốc độ
  speed ≤ (độ dài gốc − 0,3) / DUR (video gốc ngắn thì giảm speed, nhỏ nhất 1.0). Luật D4 (2026-11-13): speed chỉ 1.0 / 1.05 / 1.10,
  mặc định 1.0; video < 45 s giữ 1.0 (lấy đúng tốc độ của cả video, `build_kit.choose_speed`).
- Chạy dưới `flock /tmp/gpu.lock` khi có nhiều tiến trình; ffmpeg đọc phải có stdin=DEVNULL (nếu không sẽ nuốt dữ liệu heredoc).
"""
import subprocess
import sys

import cv2
import numpy as np

W, H, FPS = 1080, 1920, 30
ALLOWED_SPEEDS = (1.0, 1.05, 1.1)  # luật D4 (2026-11-13), cùng giá trị build_kit.ALLOWED_SPEEDS


def main() -> None:
    src, out, bg, dur = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
    speed = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
    if speed not in ALLOWED_SPEEDS:
        sys.exit(f"chroma_studio: tốc độ {speed}x không được phép (luật D4: chỉ {ALLOWED_SPEEDS})")
    zoom = float(sys.argv[6]) if len(sys.argv) > 6 else 1.3
    start = float(sys.argv[7]) if len(sys.argv) > 7 else 0.2
    n_frames = int(round(dur * FPS))
    plate = cv2.resize(cv2.imread(bg), (W, H)).astype(np.float32)
    vf = f"setpts=PTS/{speed},fps={FPS},transpose=1,scale={W}:{H}:flags=lanczos"
    rd = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(start), "-i", src, "-an", "-vf", vf, "-frames:v", str(n_frames),
                           "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE, stdin=subprocess.DEVNULL)
    wr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p", "-colorspace", "bt709",
                           "-color_primaries", "bt709", "-color_trc", "bt709", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    m0, n = None, 0
    while True:
        buf = rd.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        f = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32)
        b, g, r = f[..., 0], f[..., 1], f[..., 2]
        a = 1 - np.clip((g - np.maximum(r, b) - 3) / 17, 0, 1)
        sure = cv2.morphologyEx((a > 0.5).astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        n_lab, lab, st, _ = cv2.connectedComponentsWithStats(sure, connectivity=8)
        if n_lab > 1:
            big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
            a = a * cv2.dilate((lab == big).astype(np.uint8), np.ones((9, 9), np.uint8))
        a = cv2.GaussianBlur(cv2.erode(a, np.ones((3, 3), np.uint8)), (0, 0), 1.0)
        f2 = np.stack([b, np.minimum(g, np.maximum(r, b)), r], -1)
        ys, xs = np.where(a > 0.5)
        top_y = int(ys.min()) if len(ys) else int(H * 0.4)
        cx = int(np.median(xs)) if len(xs) else W // 2
        if m0 is None:                                          # khoá phép phóng theo khung đầu để không rung
            m0 = cv2.getRotationMatrix2D((float(cx), float(top_y)), 0, zoom)
            m0[0, 2] += W / 2 - cx
            m0[1, 2] += int(H * 0.36) - top_y
        f3 = cv2.warpAffine(f2, m0, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
        a3 = np.clip(cv2.warpAffine(a, m0, (W, H), flags=cv2.INTER_LINEAR, borderValue=0), 0, 1)[..., None]
        wr.stdin.write(np.clip(f3 * a3 + plate * (1 - a3), 0, 255).astype(np.uint8).tobytes())
        n += 1
    wr.stdin.close()
    wr.wait()
    rd.wait()
    print("frames", n)


if __name__ == "__main__":
    main()
