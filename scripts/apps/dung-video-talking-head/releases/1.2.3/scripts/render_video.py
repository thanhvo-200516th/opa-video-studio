"""render_video.py — render HÌNH của bản dựng (Remotion, không tiếng) ra out/_video.mp4.

Dùng: PYTHONIOENCODING=utf-8 python render_video.py <project_dir>

Chạy trong thư mục dự án:
  ./node_modules/.bin/remotion render src/index.ts Main out/_video.mp4 --muted
      --concurrency=4 --crf=18
Tiếng không đi qua Remotion (S25): mux.py ghép out/_video.mp4 với public/mix*.wav bằng
ffmpeg. Đây là đường render duy nhất của template 1.1 (template không có `npm run render`).
Thoát mã 1 khi chưa npm install hoặc Remotion lỗi; bản _video.mp4 cũ bị xoá trước khi
render để lần render hỏng không để lại hình cũ cho mux ghép nhầm. Render có trần
thlib.proc.RENDER_TIMEOUT_S: quá hạn thì cả cây process Remotion bị giết, hình dở bị xoá và
script thoát mã thlib.proc.TIMEOUT_EXIT (R47 — stage.py BLOCK transient).
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from check_text_safe import bin_name
from thlib import proc

OUT = "out/_video.mp4"
RENDER_ARGS = ["render", "src/index.ts", "Main", OUT, "--muted", "--concurrency=4", "--crf=18"]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Render hình (không tiếng) của bản dựng ra out/_video.mp4")
    ap.add_argument("project", help="Thư mục dự án edit-r<ver> (đã npm install, có src/data/script.ts)")
    project = Path(ap.parse_args(argv).project)
    remotion = project / "node_modules" / ".bin" / bin_name("remotion")
    if not remotion.exists():
        print(f"FAIL: chưa có {remotion} — chạy npm install trong thư mục dự án")
        return 1
    video = project / OUT
    video.parent.mkdir(parents=True, exist_ok=True)
    video.unlink(missing_ok=True)
    try:
        run = proc.run([str(remotion), *RENDER_ARGS], cwd=project, timeout=proc.RENDER_TIMEOUT_S)
    except subprocess.TimeoutExpired as exc:
        video.unlink(missing_ok=True)
        print(f"QUÁ THỜI GIAN: remotion render quá {exc.timeout:g} s — đã dừng cả cây process, không có {OUT}")
        return proc.TIMEOUT_EXIT
    if run.returncode != 0 or not video.is_file():
        log = (run.stdout or "") + (run.stderr or "")
        if "No frame found at position" in log:
            print("GỢI Ý: Remotion thiếu bộ đệm khung — thường do máy thiếu RAM (kiểm Available/NonPaged pool; khởi động lại máy) — dựng lại sau, không phải lỗi dữ liệu")
        print(f"FAIL: remotion render lỗi (mã {run.returncode}) — không có {OUT}")
        return 1
    print(f"KẾT QUẢ: PASS — đã render hình (không tiếng) {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
