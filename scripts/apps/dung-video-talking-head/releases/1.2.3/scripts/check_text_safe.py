"""check_text_safe.py — cổng text-safe của BUILD (B14): chữ và mọi lớp phủ
(phụ đề, thẻ liệt kê, tít hook, pill CTA) nằm trọn trong hộp safe zone.

Dùng: PYTHONIOENCODING=utf-8 python check_text_safe.py <project_dir>

Đọc rules.lock → rules.json (safe_zone) và picture_lock.json của dự án; render
ảnh PNG nền trong suốt của composition TextOnly (chỉ lớp chữ, không nền,
không footage) ở các frame dò:
  - mỗi block: show cuối cùng + 12 f (mọi chữ của block đã hiện xong), nhưng không
    quá ⌊out·fps⌋ — frame cuối block còn hiện đủ, trước lúc thẻ vào hay block sau
    hiện (Ruling R33);
  - giữa khoảng thẻ liệt kê (in … out);
  - pill CTA: show + 20 f;
  - tít hook: land, và ⌊out·fps⌋ — đỉnh đẩy ×1,05, trước khi thoát (B1).
Lệnh render: `./node_modules/.bin/remotion still src/index.ts TextOnly
out/safe/f<N>.png --frame=<N> --image-format=png --props={"probe":true}` (chạy
trong thư mục dự án). Prop probe chỉ tắt trang trí (quầng, bóng đổ/bóng chữ,
box-shadow, backdrop-filter — Ruling R26); blur và opacity chuyển động vẫn giữ, vì
chữ lên hình đúng như vậy (Ruling R29) — cổng đo nét chữ và nền/viền thẻ, pill.
Alpha tách bằng `ffmpeg -vf alphaextract`; điểm ảnh alpha > 0 ngoài hộp
text_x_min..text_x_max × text_y_min..text_y_max là FAIL (B14).
Ghi out/safe/text_safe.json, in một dòng mỗi frame, thoát mã 1 khi có frame FAIL
(owner: PLAN hoặc template). Lỗi công cụ — thiếu/hỏng rules.lock hay picture_lock.json,
chưa npm install, thiếu font của template (Fonts.tsx sẽ render tiếp bằng font dự
phòng), Remotion/Chrome/ffmpeg lỗi — thoát mã 2 (owner dev, B3), không ghi báo cáo;
text_safe.json của lần chạy trước bị xoá ngay đầu mỗi lần chạy. Mỗi still có trần
thlib.proc.STILL_TIMEOUT_S; quá hạn thì cả cây process Remotion bị giết và script thoát mã
thlib.proc.TIMEOUT_EXIT (R47 — stage.py BLOCK transient).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import struct
import subprocess
from pathlib import Path

import numpy as np

from thlib import proc, rules

_SETTLE_F = 12   # block: chữ cuối đã hiện xong (REVEAL 9 f) + đệm
_CTA_F = 20      # pill CTA đã bật xong (POP 12 f) + đệm
_OUT_DIR = Path("out") / "safe"
_PROBE_PROPS = '--props={"probe":true}'   # R26/R29: TextOnly không trang trí, vẫn blur chuyển động
_PROBE_NOHOOK_PROPS = '--props={"probe":true,"hook":false}'
_TOOL_EXIT = 2   # B3: lỗi công cụ (owner dev), khác mã 1 của chữ tràn thật
_FONT_REF = re.compile(r'"(fonts/[^"]+)"')   # file font trong FACES của src/fonts.tsx


def bin_name(tool: str) -> str:
    """Tên file trong node_modules/.bin: trên Windows là bản .cmd."""
    return tool + ".cmd" if os.name == "nt" else tool


def probe_frames(lock: dict) -> list[int]:
    """Frame dò (đã xếp, không trùng, kẹp trong [0, duration_f − 1])."""
    fps, last = lock["fps"], lock["duration_f"] - 1
    # R33: out làm tròn 4 số lẻ nên cộng 1e-6 trước khi lấy phần nguyên
    frames = {min(int(round(max(w["show"] for w in b["top"] + b["hero"] + b["bottom"]) * fps)) + _SETTLE_F,
                  math.floor(b["out"] * fps + 1e-6))
              for b in lock["blocks"]}
    if lock.get("steps"):
        frames.add(int(round((lock["steps"]["in"] + lock["steps"]["out"]) / 2 * fps)))
    if lock.get("cta"):
        frames.add(int(round(lock["cta"]["show"] * fps)) + _CTA_F)
    if lock.get("hook"):
        frames.add(int(round(lock["hook"]["land"] * fps)))
        frames.add(math.floor(lock["hook"]["out"] * fps))   # B1: đỉnh đẩy ×1,05, trước khi thoát
    return sorted({min(max(f, 0), last) for f in frames})


def outside(alpha: np.ndarray, safe: dict) -> dict:
    """Số điểm ảnh alpha > 0 ngoài hộp chữ và khung bao của chúng [x0, y0, x1, y1]."""
    mask = alpha > 0
    mask[safe["text_y_min"]:safe["text_y_max"], safe["text_x_min"]:safe["text_x_max"]] = False
    ys, xs = np.nonzero(mask)
    if not len(xs):
        return {"count": 0, "box": None}
    return {"count": int(len(xs)), "box": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]}


def read_alpha(png: Path) -> np.ndarray:
    """Kênh alpha [H, W] uint8 của một PNG (ffmpeg alphaextract)."""
    png = Path(png)
    width, height = struct.unpack(">II", png.read_bytes()[16:24])   # IHDR
    run = subprocess.run(["ffmpeg", "-v", "error", "-i", str(png), "-vf", "alphaextract",
                          "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True)
    if run.returncode != 0:
        raise ValueError("không tách được alpha của %s (TextOnly phải render nền trong suốt): %s"
                         % (png.name, run.stderr.decode("utf-8", "replace").strip()[-300:]))
    return np.frombuffer(run.stdout, dtype=np.uint8).reshape(height, width)


def render_still(project: Path, frame: int, props: str = _PROBE_PROPS, name_suffix: str = "") -> Path:
    """Render frame `frame` của composition TextOnly thành out/safe/f<N><suffix>.png."""
    fname = f"f{frame}{name_suffix}.png"
    rel = (_OUT_DIR / fname).as_posix()
    remotion = project / "node_modules" / ".bin" / bin_name("remotion")
    run = proc.run([str(remotion), "still", "src/index.ts", "TextOnly", rel, "--frame=%d" % frame,
                    "--image-format=png", props], cwd=project, capture_output=True, text=True,
                   encoding="utf-8", errors="replace", timeout=proc.STILL_TIMEOUT_S)
    if run.returncode != 0:
        raise RuntimeError("remotion still frame %d lỗi: %s" % (frame, (run.stderr or run.stdout)[-500:]))
    return project / rel


def require_tools(project: Path) -> None:
    """B3: Remotion của dự án (npm install) và mọi font template nạp (src/fonts.tsx) phải có
    trên đĩa — thiếu font thì Fonts.tsx vẫn render bằng font dự phòng và phép đo sai."""
    remotion = project / "node_modules" / ".bin" / bin_name("remotion")
    if not remotion.is_file():
        raise FileNotFoundError(f"chưa có {remotion.as_posix()} — dự án chưa npm install")
    faces = _FONT_REF.findall((project / "src" / "fonts.tsx").read_text(encoding="utf-8"))
    if not faces:
        raise ValueError("không đọc được danh sách font trong src/fonts.tsx")
    missing = [f for f in faces if not (project / "public" / f).is_file()]
    if missing:
        raise FileNotFoundError("thiếu font của template trong public/: " + ", ".join(missing))


def run(project) -> list[dict]:
    """Dò mọi frame của dự án; trả [{"frame", "ok", "count", "box", "png", "layer", "face_png"}]. Lỗi công cụ
    (xem require_tools, lock hỏng, Remotion/ffmpeg lỗi) ném ngoại lệ."""
    project = Path(project)
    safe = rules.load(project=project).get("safe_zone")
    lock = json.loads((project / "picture_lock.json").read_text(encoding="utf-8"))
    frames = probe_frames(lock)
    require_tools(project)
    (project / _OUT_DIR).mkdir(parents=True, exist_ok=True)

    fps = lock.get("fps", 30)
    hook_end_f = int(round(lock["hook"]["end"] * fps)) if lock.get("hook") else -1

    # Ánh xạ probe_f -> id của lớp
    frame_to_layer: dict[int, str] = {}
    for b in lock.get("blocks", []):
        ws = b["top"] + b["hero"] + b["bottom"]
        pf = min(int(round(max(w["show"] for w in ws) * fps)) + _SETTLE_F,
                 math.floor(b["out"] * fps + 1e-6))
        frame_to_layer[min(max(pf, 0), lock["duration_f"] - 1)] = b["id"]
    if lock.get("steps"):
        pf = int(round((lock["steps"]["in"] + lock["steps"]["out"]) / 2 * fps))
        frame_to_layer[min(max(pf, 0), lock["duration_f"] - 1)] = "steps"
    if lock.get("cta"):
        pf = int(round(lock["cta"]["show"] * fps)) + _CTA_F
        frame_to_layer[min(max(pf, 0), lock["duration_f"] - 1)] = "cta"
    if lock.get("hook"):
        f_land = min(max(int(round(lock["hook"]["land"] * fps)), 0), lock["duration_f"] - 1)
        f_out = min(max(math.floor(lock["hook"]["out"] * fps), 0), lock["duration_f"] - 1)
        frame_to_layer[f_land] = "hook"
        frame_to_layer[f_out] = "hook"

    results = []
    for frame in frames:
        got = outside(read_alpha(render_still(project, frame)), safe)
        layer_id = frame_to_layer.get(frame)
        face_png = None
        if frame <= hook_end_f and layer_id != "hook":
            render_still(project, frame, props=_PROBE_NOHOOK_PROPS, name_suffix="_face")
            face_png = (_OUT_DIR / ("f%d_face.png" % frame)).as_posix()

        entry = {
            "frame": frame,
            "ok": got["count"] == 0,
            **got,
            "png": (_OUT_DIR / ("f%d.png" % frame)).as_posix(),
            "layer": layer_id,
            "face_png": face_png,
        }
        results.append(entry)
    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Cổng text-safe B14: chữ nằm trong hộp safe zone")
    ap.add_argument("project", help="Thư mục dự án edit-r<ver> (đã npm install, có picture_lock.json)")
    project = Path(ap.parse_args(argv).project)
    out = project / _OUT_DIR / "text_safe.json"
    out.unlink(missing_ok=True)                  # B3: không để báo cáo cũ trỏ nhầm
    try:
        results = run(project)
    except subprocess.TimeoutExpired as exc:     # R47: treo, không phải hỏng — cả cây đã bị giết
        print("QUÁ THỜI GIAN: remotion still quá %g s — đã dừng cả cây process" % exc.timeout)
        return proc.TIMEOUT_EXIT
    except Exception as exc:                     # B3: mọi lỗi ở đây là công cụ hỏng, không phải chữ tràn
        where = getattr(exc, "filename", None)
        print("LỖI CÔNG CỤ (không phải chữ tràn — owner dev): %s: %s%s"
              % (type(exc).__name__, exc, f" ({where})" if where else ""))
        return _TOOL_EXIT
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    safe = rules.load(project=project).get("safe_zone")
    box = "x %d–%d, y %d–%d" % (safe["text_x_min"], safe["text_x_max"], safe["text_y_min"], safe["text_y_max"])
    for r in results:
        if r["ok"]:
            print("f%-5d PASS  chữ nằm trong hộp %s" % (r["frame"], box))
        else:
            x0, y0, x1, y1 = r["box"]
            print("f%-5d FAIL  %d điểm ảnh alpha > 0 ngoài hộp %s (vùng lỗi x %d–%d, y %d–%d) — %s"
                  % (r["frame"], r["count"], box, x0, x1, y0, y1, r["png"]))
    failed = [r["frame"] for r in results if not r["ok"]]
    verdict = "FAIL " + ", ".join("f%d" % f for f in failed) if failed else "PASS"
    print("KẾT QUẢ: %s — %d frame dò, đã ghi %s" % (verdict, len(results), out))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
