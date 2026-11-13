"""Bộ điều khiển render phim 3D (film3d): Chrome headless KHÔNG nối CDP, trang tự render và đẩy khung qua WebSocket.

Dùng:
  python -I tools/film3d/render.py job film3d/films/<id>/jobs/<job>.json
  python -I tools/film3d/render.py serve            # xem film.html?t=... bằng trình duyệt thường
  python -I tools/film3d/render.py compose <clip.mkv> <lớp phủ.mov> <ra.mp4> [--timecode]
      Ghép lớp chữ + end card Remotion (ProRes 4444, alpha thẳng) lên phần 3D (FFV1), trộn trong RGB, mã hóa H.264 một lần.
      Phần 3D ngắn hơn lớp phủ thì giữ khung cuối (end card đục nên không lộ). --timecode: in giờ phim góc dưới phải (bản duyệt).

Job (JSON, đường dẫn tương đối tính từ thư mục film3d/):
  {"page": "films/look-test/film.html", "kind": "stills" | "clip" | "shape", "out": "films/look-test/out/<tên>", ...}
  stills: "items": [{"id", ...tham số cảnh..., "spp", "mask": true}]
  clip:   tham số cảnh + "f0", "f1", "fps", "spp", "maskFrames": [..]  -> <out>/clip.mkv (FFV1) + <out>/clip.mp4
  shape:  "thick", "size", "samples"                                   -> <out>/coverage.png
  events: (không tham số)                                               -> <out>/events.json (EVENTS, BEATS của timeline, cho âm)
  boxes:  "f0", "f1"                                                    -> <out>/boxes.json (khung chiếu Bò + từng sừng mỗi khung)

Luật máy này (docs/film3d/phuong-an-phim-3d.md mục 7.1): ép GPU rời; tin đầu phải báo GPU có "NVIDIA", không thì dừng;
bản Chrome đầu và cuối phải trùng.
"""
from __future__ import annotations

import base64
import hashlib
import http.server
import json
import mimetypes
import os
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
FILM3D = ROOT / "film3d"
CHROME = "/usr/bin/google-chrome"
GPU_FLAGS = ["--use-angle=gl", "--enable-gpu", "--ignore-gpu-blocklist"]
BASE_FLAGS = ["--headless", "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--disable-sync",
              "--disable-background-networking", "--disable-component-update", "--disable-default-apps", "--no-pings",
              "--disable-features=Translate,OptimizationHints,MediaRouter,DialMediaRouteProvider,AutofillServerCommunication",
              "--disable-background-timer-throttling", "--disable-renderer-backgrounding",
              "--disable-backgrounding-occluded-windows", "--force-color-profile=srgb", "--mute-audio", "--hide-scrollbars",
              "--window-size=1920,1080"]
X264 = ["-c:v", "libx264", "-preset", "slow", "-profile:v", "high", "-b:v", "25M", "-maxrate", "30M", "-bufsize", "50M",
        "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
        "-color_range", "tv", "-movflags", "+faststart"]
RGB2YUV = ("scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p,"
           "setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709")
FFV1 = ["-c:v", "ffv1", "-level", "3", "-pix_fmt", "bgr0", "-slices", "24", "-g", "1"]
# giờ phim theo số khung (HH:MM:SS:khung 60 fps): khung 960 hiện đúng 00:00:16:00, không lệch làm tròn như %{pts}
TIMECODE = ("drawtext=fontfile=film3d/vendor/fonts/BeVietnamPro-Medium.ttf:timecode='00\\:00\\:00\\:00':rate=60:fontsize=26:"
            "fontcolor=white@0.9:box=1:boxcolor=black@0.45:boxborderw=8:x=w-tw-28:y=h-th-24")
mimetypes.add_type("font/ttf", ".ttf")


class RenderError(RuntimeError):
    pass


# ---------------------------------------------------------------- HTTP: chỉ phục vụ file trong film3d/
class _Static(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    disable_nagle_algorithm = True

    def log_message(self, *args) -> None:  # im lặng
        pass

    def do_GET(self) -> None:
        rel = self.path.split("?", 1)[0].lstrip("/")
        f = (FILM3D / rel).resolve()
        if FILM3D.resolve() not in f.parents or not f.is_file():
            self.send_response(404); self.send_header("Content-Length", "0"); self.end_headers(); return
        data = f.read_bytes()
        ctype = "text/javascript" if f.suffix in (".js", ".mjs") else (mimetypes.guess_type(str(f))[0] or "application/octet-stream")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)


class _QuietServer(http.server.ThreadingHTTPServer):
    def handle_error(self, request, client_address) -> None:  # Chrome bị đóng khi còn kết nối keep-alive: bỏ qua
        if not isinstance(sys.exc_info()[1], (ConnectionResetError, ConnectionAbortedError, BrokenPipeError)):
            super().handle_error(request, client_address)


def start_http(port: int = 0) -> tuple[http.server.ThreadingHTTPServer, str]:
    srv = _QuietServer(("127.0.0.1", port), _Static)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


# ---------------------------------------------------------------- WebSocket: nhận tin [u32 dài header][header JSON][dữ liệu]
def _recv_exact(conn: socket.socket, n: int) -> bytearray:
    buf = bytearray(n)
    mv, got = memoryview(buf), 0
    while got < n:
        k = conn.recv_into(mv[got:], n - got)
        if k == 0:
            raise EOFError
        got += k
    return buf


def start_ws(on_message) -> tuple[socket.socket, str]:
    """Sink RFC 6455 tối giản (stdlib + numpy). Mỗi tin trọn vẹn -> on_message(header: dict, payload: memoryview); trả 'ok'."""
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8 << 20)
    srv.bind(("127.0.0.1", 0)); srv.listen(2)

    def handle(c: socket.socket) -> None:
        c.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        req = b""
        while b"\r\n\r\n" not in req:
            req += c.recv(4096)
        key = next(ln.split(":", 1)[1].strip() for ln in req.decode().split("\r\n") if ln.lower().startswith("sec-websocket-key"))
        acc = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
        c.sendall(("HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                   f"Sec-WebSocket-Accept: {acc}\r\n\r\n").encode())
        parts: list[bytearray] = []
        try:
            while True:
                hdr = _recv_exact(c, 2)
                fin, op, ln = hdr[0] & 0x80, hdr[0] & 0x0F, hdr[1] & 0x7F
                if ln == 126:
                    ln = struct.unpack(">H", _recv_exact(c, 2))[0]
                elif ln == 127:
                    ln = struct.unpack(">Q", _recv_exact(c, 8))[0]
                mask = bytes(_recv_exact(c, 4))
                payload = _recv_exact(c, ln)
                if op == 0x8:
                    return
                n4 = ln // 4
                if n4:
                    a32 = np.frombuffer(payload, np.uint32, n4)
                    a32 ^= np.frombuffer(mask, np.uint32)[0]
                for i in range(n4 * 4, ln):
                    payload[i] ^= mask[i & 3]
                parts.append(payload)
                if not fin:  # Chrome chia tin lớn thành nhiều mảnh: ghép đủ rồi mới xử lý
                    continue
                msg = parts[0] if len(parts) == 1 else bytearray(b"".join(parts))
                parts = []
                hlen = struct.unpack("<I", msg[:4])[0]
                header = json.loads(bytes(msg[4:4 + hlen]).decode("utf-8"))
                on_message(header, memoryview(msg)[4 + hlen:])
                c.sendall(b"\x81\x02ok")
        except (EOFError, OSError):
            return

    def serve() -> None:
        while True:
            try:
                c, _ = srv.accept()
            except OSError:
                return
            threading.Thread(target=handle, args=(c,), daemon=True).start()

    threading.Thread(target=serve, daemon=True).start()
    return srv, f"ws://127.0.0.1:{srv.getsockname()[1]}"


# ---------------------------------------------------------------- Chạy một job
class Job:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.spec = json.loads(path.read_text(encoding="utf-8"))
        self.out = FILM3D / self.spec["out"]
        self.out.mkdir(parents=True, exist_ok=True)
        self.meta: dict = {"job": str(path.relative_to(FILM3D)), "frames": 0, "logs": []}
        self.done = threading.Event()
        self.error: str | None = None
        self.ffmpeg: subprocess.Popen | None = None

    # -- tin từ trang
    def on_message(self, h: dict, data: memoryview) -> None:
        kind = h.get("type")
        if kind == "hello":
            self.meta.update(renderer=h.get("renderer"), uaStart=h.get("ua"), three=h.get("three"))
            if "NVIDIA" not in (h.get("renderer") or ""):
                self.fail(f"GPU sai: {h.get('renderer')!r} (phải là NVIDIA RTX). Kiểm cờ {GPU_FLAGS}.")
        elif kind == "frame":
            self._frame(h, data)
        elif kind == "mask":
            arr = np.frombuffer(data, np.uint8).reshape(h["h"], h["w"], 2)
            img = np.zeros((h["h"], h["w"], 3), np.uint8)
            img[..., :2] = arr
            Image.fromarray(img).save(self.out / f"{h['id']}.mask.png")
        elif kind == "coverage":
            arr = np.frombuffer(data, np.uint8).reshape(h["h"], h["w"])
            Image.fromarray(arr).save(self.out / "coverage.png")
            self.meta["coverage"] = {k: v for k, v in h.items() if k not in ("type",)}
        elif kind in ("events", "boxes"):
            (self.out / f"{kind}.json").write_text(json.dumps(h["data"], ensure_ascii=False, indent=1), encoding="utf-8")
        elif kind == "log":
            self.meta["logs"].append(h.get("msg"))
        elif kind == "error":
            self.fail(f"lỗi trong trang: {h.get('msg')}")
        elif kind == "done":
            self.meta.update(uaEnd=h.get("ua"), pageStats=h.get("stats"))
            self.done.set()

    def _frame(self, h: dict, data: memoryview) -> None:
        self.meta["frames"] += 1
        if self.spec["kind"] == "clip":
            if self.ffmpeg is None:
                mkv = self.out / "clip.mkv"
                self.ffmpeg = subprocess.Popen(
                    ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba",
                     "-s", f"{h['w']}x{h['h']}", "-r", str(self.spec.get("fps", 60)), "-i", "-", *FFV1, str(mkv)],
                    stdin=subprocess.PIPE)
            self.ffmpeg.stdin.write(data)
            if "cfg" in h:   # khung có mặt nạ: màu Bò cần đo (qa.py video đọc)
                (self.out / f"{h['id']}.json").write_text(json.dumps({"cfg": h["cfg"]}, ensure_ascii=False), encoding="utf-8")
        else:
            arr = np.frombuffer(data, np.uint8).reshape(h["h"], h["w"], 4)
            Image.fromarray(np.ascontiguousarray(arr[..., :3])).save(self.out / f"{h['id']}.png")
            info = {k: v for k, v in h.items() if k not in ("type", "w", "h")}
            (self.out / f"{h['id']}.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")

    def fail(self, msg: str) -> None:
        self.error = msg
        self.done.set()

    # -- chạy
    def run(self, timeout_s: float = 900) -> dict:
        ws, ws_url = start_ws(self.on_message)
        http_srv, base = start_http()
        job_url = self.path.relative_to(FILM3D).as_posix()
        url = f"{base}/{self.spec['page']}?job=/{job_url}&ws={ws_url}"
        profile = tempfile.mkdtemp(prefix="film3d-chrome-")
        cmd = [CHROME, *BASE_FLAGS, *GPU_FLAGS, f"--user-data-dir={profile}", url]
        t0 = time.perf_counter()
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        try:
            if not self.done.wait(timeout_s):
                self.error = self.error or f"hết giờ sau {timeout_s} s (khung đã nhận: {self.meta['frames']})"
        finally:
            try:  # cả cây tiến trình Chrome (tương đương taskkill /T /F trên Windows)
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                proc.wait(timeout=20)
            except subprocess.TimeoutExpired:
                pass
            http_srv.shutdown(); ws.close()
        self.meta["wallS"] = round(time.perf_counter() - t0, 2)
        if self.ffmpeg is not None:
            self.ffmpeg.stdin.close()
            self.meta["ffmpegRc"] = self.ffmpeg.wait(timeout=600)
        if self.error is None and self.meta.get("uaStart") != self.meta.get("uaEnd"):
            self.error = f"bản Chrome đổi giữa chừng: {self.meta.get('uaStart')} -> {self.meta.get('uaEnd')}"
        if self.error is None and self.spec["kind"] == "clip":
            self._encode()
        self.meta["error"] = self.error
        (self.out / "render-meta.json").write_text(json.dumps(self.meta, ensure_ascii=False, indent=1), encoding="utf-8")
        return self.meta

    def _encode(self) -> None:
        mkv, mp4 = self.out / "clip.mkv", self.out / "clip.mp4"
        t0 = time.perf_counter()
        rc = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(mkv), "-vf", RGB2YUV,
                             "-r", str(self.spec.get("fps", 60)), *X264, str(mp4)]).returncode
        self.meta.update(encodeS=round(time.perf_counter() - t0, 2), encodeRc=rc)
        if rc != 0:
            self.error = f"ffmpeg mã hóa H.264 lỗi (rc={rc})"


def compose(base: Path, overlay: Path, out: Path, timecode: bool) -> int:
    # Mốc giờ của cả hai nguồn đặt lại = số khung / 60 trên thang 1/60 s: clip.mkv (Matroska) làm tròn mốc theo mili giây,
    # overlay chọn khung lớp chữ theo mốc nên cứ ~3 khung lặp 1 khung chữ (chữ giật), end card lệch dần.
    graph = ("[0:v]settb=1/60,setpts=N,format=gbrp,tpad=stop=-1:stop_mode=clone[b];"
             "[1:v]settb=1/60,setpts=N,scale=in_color_matrix=bt709:in_range=tv:flags=accurate_rnd+full_chroma_int,format=gbrap[o];"
             f"[b][o]overlay=format=gbrp:alpha=straight:shortest=1,{RGB2YUV}" + (f",{TIMECODE}" if timecode else ""))
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(base.resolve()), "-i", str(overlay.resolve()),
           "-filter_complex", graph, "-r", "60", *X264, str(out.resolve())]
    return subprocess.run(cmd, cwd=ROOT).returncode   # cwd = gốc dự án: đường dẫn phông của TIMECODE là tương đối


def main(argv: list[str]) -> int:
    if len(argv) >= 5 and argv[1] == "compose":
        return compose(Path(argv[2]), Path(argv[3]), Path(argv[4]), "--timecode" in argv)
    if len(argv) >= 2 and argv[1] == "serve":
        srv, base = start_http(8765)
        print(f"Đang phục vụ {FILM3D} tại {base}  (Ctrl+C để dừng)")
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            srv.shutdown()
        return 0
    if len(argv) < 3 or argv[1] != "job":
        print(__doc__)
        return 2
    path = (ROOT / argv[2]).resolve() if not Path(argv[2]).is_absolute() else Path(argv[2])
    meta = Job(path).run()
    print(json.dumps({k: v for k, v in meta.items() if k != "logs"}, ensure_ascii=False))
    if meta.get("logs"):
        print("log trang:", *meta["logs"][-8:], sep="\n  ")
    return 0 if meta.get("error") is None else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
