"""Kiểm V2, V3 không đổi: dựng lại master V2 và V3 vào thư mục tạm (không ghi đè file dự án) rồi so md5 với build.json đã
giao. Chạy sau mỗi lần sửa module dùng chung (dsp, synth, voices, mixbus, master, sonic_logo, score_v2*, score_v3*).

python -X utf8 tools/audio/score_thumon_regress.py [--keep DIR]
Exit 0 = cả ba file (V2 master, V2 sfx-master, V3 master) trùng md5; 1 = lệch; 2 = thiếu build.json gốc.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build as v2_build  # noqa: E402
import cues_io  # noqa: E402
import score_v3_build as v3_build  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
V2_ID = "v2-khong-bo-sot-khach"
V2_BUILD = ROOT / "out" / V2_ID / "audio" / "build.json"
V3_BUILD = ROOT / "out" / "tmp" / "V3-AM" / "audio" / "build.json"


def md5(path: Path) -> str:
    return hashlib.md5(Path(path).read_bytes()).hexdigest()


def rebuild_v2(d: Path) -> dict:
    sheet = cues_io.load_sheet(V2_ID)
    p = {"cues": cues_io.sheet_path(V2_ID), "audio": d / "audio", "build": d / "audio" / "build.json", "ab": d / "ab",
         "tmp": d / "tmp", "master": d / f"{V2_ID}-master.wav", "sfx_master": d / f"{V2_ID}-sfx-master.wav"}
    v2_build.run_build(sheet, p, v2_build.default_music, v2_build.sheet_logo_variant(sheet), True, False)
    want = json.loads(V2_BUILD.read_text(encoding="utf-8"))["md5"]
    return {"v2 master": (md5(p["master"]), want["master"]), "v2 sfx-master": (md5(p["sfx_master"]), want["sfx_master"])}


def rebuild_v3(d: Path) -> dict:
    keep = dict(v3_build.PATHS), v3_build.ROOT
    try:
        v3_build.PATHS.update({"audio": d / "audio", "build": d / "audio" / "build.json", "preview": d / "preview",
                               "master": d / "v3-ai-audit-master.wav", "sfx_master": d / "audio" / "sfx-master.wav"})
        (d / "audio").mkdir(parents=True, exist_ok=True)
        v3_build.ROOT = d                      # build.json ghi đường master tương đối theo ROOT
        v3_build.run()
        got = md5(v3_build.PATHS["master"])
    finally:
        v3_build.PATHS.clear()
        v3_build.PATHS.update(keep[0])
        v3_build.ROOT = keep[1]
    return {"v3 master": (got, json.loads(V3_BUILD.read_text(encoding="utf-8"))["md5"]["master"])}


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Kiểm V2, V3 dựng lại trùng md5")
    ap.add_argument("--keep", type=Path, help="giữ bản dựng lại ở thư mục này (mặc định: thư mục tạm, xóa sau)")
    a = ap.parse_args(argv)
    for f in (V2_BUILD, V3_BUILD):
        if not f.is_file():
            print(f"LỖI: thiếu {f}")
            return 2
    with tempfile.TemporaryDirectory(prefix="thumon-regress-") as tmp:
        d = a.keep or Path(tmp)
        res = {**rebuild_v2(d / "v2"), **rebuild_v3(d / "v3")}
    ok = all(got == want for got, want in res.values())
    for k, (got, want) in res.items():
        print(f"{'TRÙNG' if got == want else 'LỆCH'} {k}: {got} (đã giao {want})")
    print("V2, V3 không đổi" if ok else "CÓ LỆCH: một module dùng chung đã đổi hành vi")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
