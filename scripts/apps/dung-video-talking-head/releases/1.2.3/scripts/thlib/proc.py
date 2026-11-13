"""thlib.proc — process con nặng có trần thời gian (R47, FS-2/FS-13).

`run` như `subprocess.run` nhưng bắt buộc `timeout`: quá hạn thì giết CẢ CÂY process (Windows
`taskkill /T /F` — remotion.cmd, `npm` qua shell chạy node/Chrome là cháu của process con;
`subprocess.run` chỉ giết con, và trên Windows còn treo chờ ống stdout mà cháu vẫn giữ) rồi ném
`subprocess.TimeoutExpired`. stage.py đổi lỗi đó thành BLOCK transient. Script của release gọi ở
process con (check_text_safe.py, render_video.py) thoát mã TIMEOUT_EXIT khi quá hạn để build.py
nhận ra.
"""

from __future__ import annotations

import os
import signal
import subprocess

TIMEOUT_EXIT = 3                                     # mã thoát "quá thời gian" của script release
STILL_TIMEOUT_S = 180                                # một `remotion still` của check_text_safe
RENDER_TIMEOUT_S = 1200                              # `remotion render` hình của render_video.py


def _kill_tree(proc: subprocess.Popen) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
    else:
        try:
            os.killpg(proc.pid, signal.SIGKILL)       # Popen(start_new_session=True) ⇒ pgid = pid
        except ProcessLookupError:
            pass
    proc.kill()                                      # con đã chết thì lệnh này không làm gì


def run(args, *, timeout: float | None, check: bool = False, capture_output: bool = False,
        **kwargs) -> subprocess.CompletedProcess:
    """`subprocess.run(args, timeout=…, check=…, capture_output=…, **kwargs)`; quá `timeout` giây
    ⇒ giết cả cây process của lệnh rồi ném subprocess.TimeoutExpired (kèm log đã đọc được).
    timeout None = không trần (chỉ khi lệnh con tự có trần, vd check_text_safe.py)."""
    if capture_output:
        kwargs = {**kwargs, "stdout": subprocess.PIPE, "stderr": subprocess.PIPE}
    if os.name != "nt":
        kwargs = {**kwargs, "start_new_session": True}
    with subprocess.Popen(args, **kwargs) as proc:
        try:
            out, err = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            _kill_tree(proc)
            out, err = proc.communicate()
            raise subprocess.TimeoutExpired(args, timeout, output=out, stderr=err) from None
    if check and proc.returncode:
        raise subprocess.CalledProcessError(proc.returncode, args, output=out, stderr=err)
    return subprocess.CompletedProcess(args, proc.returncode, out, err)
