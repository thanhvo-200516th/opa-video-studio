#!/usr/bin/env python3
"""open_in_app — mở project cho người dùng xem/sửa tiếp trong cửa sổ thật (không điều khiển tiếp, không đóng app).

    python3 open_in_app.py PROJECT.ecproj [PROJECT2.ecproj …] [--display :0]
    python3 open_in_app.py PROJECT.fcproj [--display :0]

EffectCraft không nhận đường dẫn ở dòng lệnh: mỗi project mở một EffectCraft riêng có cổng điều khiển, gửi `file.open`
rồi mở comp đầu tiên, sau đó chỉ ngắt kết nối — app chạy tiếp như người dùng tự mở (dùng cấu hình thật của người dùng).
FilmCraft nhận đường dẫn trực tiếp (`filmcraft --no-recover <file>`). Mỗi app tách khỏi phiên này (setsid) nên không
tắt theo terminal. Không đụng cửa sổ đang mở sẵn của người dùng.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import socket
import subprocess
import sys
import time
from pathlib import Path

BIN = Path("/home/vmiz/.local/bin")


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def rpc(sock_file, sock, token: str, n: int, command: str, params: dict) -> dict:
    msg = {"id": n, "token": token, "method": "engine.execute", "params": {"command": command, "params": params}}
    sock.sendall((json.dumps(msg, ensure_ascii=False) + "\n").encode())
    reply = json.loads(sock_file.readline())
    if not reply.get("ok"):
        raise RuntimeError(f"{command}: {reply.get('error')}")
    return reply.get("result") or {}


def open_effectcraft(project: Path, display: str) -> int:
    port, token = free_port(), secrets.token_hex(24)
    env = {**os.environ, "DISPLAY": display, "EFFECTCRAFT_CONTROL_TOKEN": token}
    log = open(project.with_suffix(".open.log"), "w")
    proc = subprocess.Popen([str(BIN / "effectcraft"), "--control", str(port)], env=env, stdin=subprocess.DEVNULL,
                            stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    deadline = time.monotonic() + 60
    while True:
        if proc.poll() is not None:
            raise RuntimeError(f"EffectCraft thoát khi khởi động — xem {log.name}")
        try:
            sock = socket.create_connection(("127.0.0.1", port), timeout=300)
            break
        except OSError:
            if time.monotonic() > deadline:
                raise RuntimeError("cổng điều khiển EffectCraft không mở")
            time.sleep(0.3)
    f = sock.makefile("r", encoding="utf-8")
    rpc(f, sock, token, 1, "file.open", {"path": str(project)})
    summary = rpc(f, sock, token, 2, "project.summary", {})
    comps = [i for i in summary.get("items", []) if i.get("type") in ("comp", "composition")] if isinstance(summary, dict) else []
    if comps:
        rpc(f, sock, token, 3, "comp.open", {"comp": comps[0].get("name") or comps[0].get("id")})
    sock.close()                                   # chỉ ngắt điều khiển; app chạy tiếp
    print(f"EffectCraft (pid {proc.pid}) đã mở {project.name}" + (f", comp {comps[0].get('name')}" if comps else ""))
    return proc.pid


def open_filmcraft(project: Path, display: str, select: str | None = None) -> int:
    """select = tên clip cần chọn sẵn (Effect Controls hiện đúng clip đó, mở sẵn mask Opacity nếu có)."""
    if not select:
        proc = subprocess.Popen([str(BIN / "filmcraft"), "--no-recover", str(project)], env={**os.environ, "DISPLAY": display},
                                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                start_new_session=True)
        print(f"FilmCraft (pid {proc.pid}) đang mở {project.name}")
        return proc.pid
    port, token = free_port(), secrets.token_hex(32)
    env = {**os.environ, "DISPLAY": display, "FILMCRAFT_CONTROL_TOKEN": token}
    proc = subprocess.Popen([str(BIN / "filmcraft"), "--control", str(port), "--no-recover", str(project)], env=env,
                            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            start_new_session=True)
    deadline = time.monotonic() + 90
    while True:
        try:
            sock = socket.create_connection(("127.0.0.1", port), timeout=300)
            break
        except OSError:
            if proc.poll() is not None or time.monotonic() > deadline:
                raise RuntimeError("FilmCraft không mở cổng điều khiển")
            time.sleep(0.3)
    f, n, hit = sock.makefile("r", encoding="utf-8"), 0, None
    while hit is None and time.monotonic() < deadline:           # chờ project nạp xong
        n += 1
        try:
            seq = rpc(f, sock, token, n, "sequence.inspect", {})
            hit = next((it for tr in seq.get("video", []) for it in tr["items"] if it.get("name") == select), None)
        except RuntimeError:
            pass
        if hit is None:
            time.sleep(0.5)
    if hit:
        rpc(f, sock, token, n + 1, "timeline.select", {"clips": [hit["clip"]], "add": False, "toggle": False})
        for k, (cmd, prm) in enumerate([("effects.select", {"clip": hit["clip"], "effect": "opacity"}),
                                        ("masks.select", {"clip": hit["clip"], "effect": "opacity", "mask": 0})]):
            try:
                rpc(f, sock, token, n + 2 + k, cmd, prm)
            except RuntimeError:
                pass
    sock.close()                                       # chỉ ngắt điều khiển; app chạy tiếp
    print(f"FilmCraft (pid {proc.pid}) đang mở {project.name}" + (f", đã chọn «{select}»" if hit else f" (không thấy «{select}»)"))
    return proc.pid


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("projects", nargs="+")
    ap.add_argument("--display", default=":0")
    ap.add_argument("--select", help="FilmCraft: tên clip cần chọn sẵn để Effect Controls hiện thông số")
    a = ap.parse_args()
    for p in map(lambda x: Path(x).resolve(), a.projects):
        if not p.is_file():
            print(f"LỖI: không có {p}", file=sys.stderr)
            return 2
        if p.suffix == ".ecproj":
            open_effectcraft(p, a.display)
        else:
            open_filmcraft(p, a.display, a.select)
    return 0


if __name__ == "__main__":
    sys.exit(main())
