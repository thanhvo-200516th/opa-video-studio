#!/usr/bin/env python3
"""Điểm gọi Remotion duy nhất của dự án, có khóa toàn cục (KH §3.1).

Chạy:  python tools/remotion_run.py <still|render|compositions|bundle> <tham số Remotion...>
Khóa:  thư mục out/.remotion.lock + owner.txt (dòng 1 = pid, rồi lệnh, giờ). Không bao giờ chạy Remotion song song.
Exit:  mã thoát của Remotion; 2 = thiếu node/CLI; 3 = chờ khóa quá 45 phút.
"""
import ctypes
import os
import shutil
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "node_modules/@remotion/cli/remotion-cli.js"
LOCK = ROOT / "out/.remotion.lock"
OWNER = LOCK / "owner.txt"
STALE_S = 120  # khóa thiếu/hỏng owner.txt cũ hơn 2 phút thì coi là khóa chết
WAIT_S = 10
MAX_WAIT_S = 45 * 60
STILL_ACTIVE = 259
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


def log(msg: str) -> None:
    # Ghi ra stderr để không lẫn vào stdout của Remotion (ví dụ `compositions > file`).
    print(f"[remotion_run] {msg}", file=sys.stderr, flush=True)


def pid_alive(pid: int) -> bool:
    """Còn sống ⇔ OpenProcess mở được và mã thoát = STILL_ACTIVE. Không dùng os.kill (trên Windows là TerminateProcess)."""
    k32 = ctypes.windll.kernel32
    k32.OpenProcess.restype = wintypes.HANDLE
    k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    k32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    k32.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return False
    try:
        code = wintypes.DWORD()
        return bool(k32.GetExitCodeProcess(handle, ctypes.byref(code))) and code.value == STILL_ACTIVE
    finally:
        k32.CloseHandle(handle)


def read_owner() -> tuple[int | None, str]:
    try:
        text = OWNER.read_text(encoding="utf-8")
    except OSError:
        return None, ""
    first = text.splitlines()[0].strip() if text.strip() else ""
    return (int(first) if first.isdigit() else None), text


def try_acquire(argv: list[str]) -> bool:
    try:
        os.mkdir(LOCK)
    except FileExistsError:
        return False
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    OWNER.write_text(f"{os.getpid()}\n{' '.join(argv)}\n{stamp}\n", encoding="utf-8")
    return True


def lock_is_dead() -> bool:
    pid, text = read_owner()
    if pid is not None:
        dead = not pid_alive(pid)
    else:
        try:
            dead = time.time() - LOCK.stat().st_mtime > STALE_S
        except OSError:
            return False  # khóa vừa bị nhả, thử chiếm lại ở vòng sau
    if dead:
        log(f"khóa cũ đã chết, xóa và chiếm lại. owner.txt:\n{text or '(thiếu/hỏng)'}")
        shutil.rmtree(LOCK, ignore_errors=True)
    return dead


def acquire(argv: list[str]) -> None:
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    started = time.time()
    last_note = started - 60  # in thông báo ngay lần chờ đầu, rồi mỗi phút
    while not try_acquire(argv):
        if lock_is_dead():
            continue
        now = time.time()
        if now - started > MAX_WAIT_S:
            log(f"chờ khóa quá 45 phút, bỏ. owner.txt:\n{read_owner()[1]}")
            sys.exit(3)
        if now - last_note >= 60:
            log(f"đang chờ khóa ({int(now - started)} s). owner.txt:\n{read_owner()[1]}")
            last_note = now
        time.sleep(WAIT_S)


def release() -> None:
    pid, _ = read_owner()
    if pid == os.getpid():
        shutil.rmtree(LOCK, ignore_errors=True)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    argv = sys.argv[1:]
    node = shutil.which("node")
    if not node:
        log("không tìm thấy `node` trên PATH")
        return 2
    if not CLI.is_file():
        log(f"thiếu Remotion CLI: {CLI} (chạy npm i)")
        return 2
    if not argv:
        log("thiếu lệnh: still | render | compositions | bundle ...")
        return 2
    acquire(argv)
    try:
        return subprocess.run([node, str(CLI), *argv], cwd=ROOT).returncode
    finally:
        release()


if __name__ == "__main__":
    sys.exit(main())
