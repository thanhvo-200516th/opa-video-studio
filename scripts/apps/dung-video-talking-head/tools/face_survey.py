# -*- coding: utf-8 -*-
"""face_survey.py — công cụ dev cho track mặt INTAKE (spec 1.1.1 §8.1, T9). Không chạy lúc runtime.

  survey  : chạy thlib.face.track trên từng video nguồn Vid Heygen/<n>/<n>.mp4 (chỉ đọc), in một dòng
            JSON mỗi video (khung, tỉ lệ hụt, hụt liền dài nhất, trung vị chiều cao mặt, cổng «mặt»,
            giây) rồi dòng tổng — căn cứ của face.max_miss_frac / max_gap_s / height_px.
  fixture : sinh tests/fixtures/face/v<n>_* từ master.mp4 của một video: face.json đầy đủ, 6 khung
            gray work_px (PNG), hộp golden của detector numpy trên đúng các khung đó, và hộp oracle
            của OpenCV 4.13 CascadeClassifier (chỉ có ở Python hệ thống, venv Hermes cv2 5.0 không có)
            trên cùng khung giải mã 540×960 — test so đường miệng hai bên.

Dùng: PYTHONIOENCODING=utf-8 python tools/face_survey.py survey [--videos 2 16 ...]
      PYTHONIOENCODING=utf-8 python tools/face_survey.py fixture --video 16 \
          --master "D:/MMO/Van Minh AI/Vid Heygen/16/edit-r1.1.0/public/master.mp4" --out tests/fixtures/face
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
DEFAULT_VERSION = "1.1.1"
_SCRIPTS = SKILL / "releases" / DEFAULT_VERSION / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

from thlib import face, paths, rules  # noqa: E402

N_FRAMES = 6                                   # số khung fixture mỗi video (§12.1)
CV2_PX = (540, 960)                            # khung oracle OpenCV (như design111/mouthsafe/haar_track.py)
CV2_PARAMS = {"scaleFactor": 1.05, "minNeighbors": 6, "minSize": [120, 120]}


def survey(videos: list[int] | None, R) -> int:
    root = paths.VID_ROOT
    dirs = sorted((p for p in root.iterdir() if p.name.isdigit()), key=lambda p: int(p.name))
    rows, heights = [], []
    for d in dirs:
        src = d / f"{d.name}.mp4"
        if (videos and int(d.name) not in videos) or not src.is_file():
            continue
        t0 = time.perf_counter()
        doc = face.track(src, R)
        ok, msg = face.gate(doc, R)
        st = doc["stats"]
        found = sum(1 for r in doc["rows"] if r[1] is not None)
        rows.append((len(doc["rows"]), found))
        if st["h_med"] is not None:
            heights.append(st["h_med"])
        print(json.dumps({"video": int(d.name), "frames": len(doc["rows"]), "found": found, **st, "gate": ok,
                          "msg": msg, "sec": round(time.perf_counter() - t0, 1)}, ensure_ascii=False), flush=True)
    if rows:
        print(json.dumps({"videos": len(rows), "frames": sum(n for n, _ in rows), "found": sum(f for _, f in rows),
                          "h_med_min": min(heights, default=None), "h_med_max": max(heights, default=None)}))
    return 0


def _cv2_boxes(master: Path, picks: list[int], R) -> tuple[str, list]:
    import cv2
    frames = face.decode(master, list(CV2_PX))
    cc = cv2.CascadeClassifier(str(face.cascade_path(R)))
    k = face.OUT_W / CV2_PX[0]
    out = []
    for i in picks:
        found = cc.detectMultiScale(frames[i], scaleFactor=CV2_PARAMS["scaleFactor"],
                                    minNeighbors=CV2_PARAMS["minNeighbors"], minSize=tuple(CV2_PARAMS["minSize"]))
        out.append([round(k * float(v), 2) for v in max(found, key=lambda b: b[2] * b[3])] if len(found) else None)
    return f"OpenCV {cv2.__version__} CascadeClassifier haarcascade_frontalface_default.xml", out


def fixture(video: int, master: Path, out: Path, R) -> int:
    doc = face.track(master, R)
    rows = doc["rows"]
    frames = face.decode(master, doc["work_px"])
    picks = []
    for target in (round(i * (len(rows) - 1) / (N_FRAMES - 1)) for i in range(N_FRAMES)):
        k = target
        while rows[k][1] is None:                   # khung fixture phải có mặt (hụt thì lùi một khung)
            k -= 1
        picks.append(k)
    fdir = out / f"v{video}_frames"
    fdir.mkdir(parents=True, exist_ok=True)
    names = [f"f{k:04d}" for k in picks]
    for name, k in zip(names, picks):
        Image.fromarray(frames[k], "L").save(fdir / f"{name}.png")
    loaded = [np.asarray(Image.open(fdir / f"{n}.png").convert("L")) for n in names]
    golden = face.boxes(loaded, R)
    tool, cv = _cv2_boxes(master, picks, R)
    (out / f"v{video}_face.json").write_bytes(face.dumps(doc).encode("utf-8"))
    (out / f"v{video}_golden_boxes.json").write_bytes((json.dumps(golden) + "\n").encode("utf-8"))
    ref = {"tool": tool, "decode": f"ffmpeg fps={face.FPS},scale={CV2_PX[0]}:{CV2_PX[1]}:flags=area gray",
           "params": CV2_PARAMS, "coords": "px khung ra 1080×1920", "frames": names, "boxes": cv}
    (out / f"v{video}_cv2_boxes.json").write_bytes((json.dumps(ref, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    for name, g, c in zip(names, golden, cv):
        d = None if g is None or c is None else round(abs((g[1] + 0.87 * g[3]) - (c[1] + 0.87 * c[3])), 1)
        print(f"{name}: numpy {g} | cv2 {c} | lệch đường miệng {d} px")
    print(f"PASS: v{video} {len(rows)} khung, {doc['stats']} → {out.as_posix()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Survey / fixture track mặt INTAKE (thlib.face)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("survey")
    s.add_argument("--videos", type=int, nargs="*")
    f = sub.add_parser("fixture")
    f.add_argument("--video", type=int, required=True)
    f.add_argument("--master", type=Path, required=True)
    f.add_argument("--out", type=Path, default=SKILL / "tests" / "fixtures" / "face")
    args = ap.parse_args(argv)
    R = rules.load(DEFAULT_VERSION)
    if args.cmd == "survey":
        return survey(args.videos, R)
    return fixture(args.video, args.master, args.out, R)


if __name__ == "__main__":
    raise SystemExit(main())
