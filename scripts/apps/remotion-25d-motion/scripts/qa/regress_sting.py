#!/usr/bin/env python3
"""Hồi quy pixel cho file dùng chung (KH §0.2, §3.10).

Chạy:  python tools/qa/regress_sting.py [--out <dir>]   (mặc định out/regress/current)
Render lại đúng các mốc WP0 đã chụp (sting 180 f, motions f331–405, type-test, still outro
mascot-sting-1x1 / 16x9 ở f150 và f179) qua remotion_run.py, rồi so với out/regress/baseline:
mọi ảnh max diff ≤ 1 và số điểm ảnh khác ≤ 0,01 %.
Exit:  0 đạt, 1 có FAIL (kể cả render lỗi, thiếu ảnh), 2 thiếu mốc baseline.
"""
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "tools/remotion_run.py"
BASELINE = ROOT / "out/regress/baseline"
DEFAULT_OUT = ROOT / "out/regress/current"
MAX_DIFF = 1
MAX_SHARE = 0.0001  # 0,01 %


@dataclass(frozen=True)
class Job:
    target: str  # đường dẫn tương đối trong baseline/out (thư mục PNG hoặc file PNG)
    args: tuple[str, ...]  # tham số remotion_run.py; "{dst}" thay bằng đích tuyệt đối
    is_dir: bool = False


# Đúng các lệnh chụp mốc của WP0 (KH §4 WP0 bước 3), chỉ đổi thư mục đích.
JOBS: tuple[Job, ...] = (
    Job("sting", ("render", "mascot-sting", "{dst}", "--sequence", "--image-format=png"), True),
    Job("motions", ("render", "mascot-motions", "{dst}", "--sequence", "--image-format=png", "--frames=331-405"), True),
    Job("type-test.png", ("still", "type-test", "{dst}")),
    Job("sting-1x1-f150.png", ("still", "mascot-sting-1x1", "{dst}", "--frame=150")),
    Job("sting-1x1-f179.png", ("still", "mascot-sting-1x1", "{dst}", "--frame=179")),
    Job("sting-16x9-f150.png", ("still", "mascot-sting-16x9", "{dst}", "--frame=150")),
    Job("sting-16x9-f179.png", ("still", "mascot-sting-16x9", "{dst}", "--frame=179")),
)


def render(job: Job, out: Path) -> int:
    """Xóa đầu ra cũ của job rồi render lại; trả mã thoát."""
    dst = out / job.target
    if job.is_dir:
        dst.mkdir(parents=True, exist_ok=True)
        for old in dst.glob("*.png"):
            old.unlink()
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.unlink(missing_ok=True)
    args = [a.replace("{dst}", str(dst)) for a in job.args]
    return subprocess.run([sys.executable, str(RUNNER), *args], cwd=ROOT, check=False).returncode


def compare_images(a: Path, b: Path) -> dict:
    """So hai PNG (RGBA). Trả {ok, max, share, note}."""
    with Image.open(a) as ia, Image.open(b) as ib:
        x = np.asarray(ia.convert("RGBA"), dtype=np.int16)
        y = np.asarray(ib.convert("RGBA"), dtype=np.int16)
    if x.shape != y.shape:
        return {"ok": False, "max": -1, "share": 1.0, "note": f"khác cỡ {x.shape} ≠ {y.shape}"}
    diff = np.abs(x - y)
    worst = int(diff.max())
    share = float((diff.max(axis=-1) > 0).mean())
    return {"ok": worst <= MAX_DIFF and share <= MAX_SHARE, "max": worst, "share": share, "note": ""}


def pairs(job: Job, out: Path) -> list[tuple[str, Path, Path | None]]:
    """(tên, ảnh mốc, ảnh hiện tại hoặc None nếu thiếu)."""
    base, cur = BASELINE / job.target, out / job.target
    if not job.is_dir:
        return [(job.target, base, cur if cur.is_file() else None)]
    names = sorted(p.name for p in base.glob("*.png"))
    return [(f"{job.target}/{n}", base / n, (cur / n) if (cur / n).is_file() else None) for n in names]


def check_job(job: Job, out: Path) -> list[str]:
    """Trả danh sách dòng FAIL của job (rỗng = đạt)."""
    fails = []
    for name, base, cur in pairs(job, out):
        if cur is None:
            fails.append(f"FAIL {name} thiếu ảnh hiện tại")
            continue
        r = compare_images(base, cur)
        if not r["ok"]:
            fails.append(f"FAIL {name} max diff {r['max']}, khác {r['share']:.4%} {r['note']}".rstrip())
    if job.is_dir:
        extra = {p.name for p in (out / job.target).glob("*.png")} - {p.name for p in (BASELINE / job.target).glob("*.png")}
        fails += [f"FAIL {job.target}/{n} thừa so với mốc" for n in sorted(extra)]
    return fails


def baseline_missing() -> list[str]:
    miss = []
    for job in JOBS:
        p = BASELINE / job.target
        if (job.is_dir and not any(p.glob("*.png"))) or (not job.is_dir and not p.is_file()):
            miss.append(job.target)
    return miss


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    out = DEFAULT_OUT
    if args:
        if len(args) != 2 or args[0] != "--out":
            print("Cách dùng: regress_sting.py [--out <dir>]", file=sys.stderr)
            return 2
        out = Path(args[1]).resolve()
    miss = baseline_missing()
    if miss:
        print(f"Thiếu mốc baseline: {', '.join(miss)} (chạy WP0 bước 3)", file=sys.stderr)
        return 2
    n_fail = 0
    for job in JOBS:
        code = render(job, out)
        if code != 0:
            print(f"FAIL {job.target} render lỗi (exit {code})")
            n_fail += 1
            continue
        fails = check_job(job, out)
        count = len(pairs(job, out))
        if fails:
            for line in fails[:10]:
                print(line)
            if len(fails) > 10:
                print(f"… còn {len(fails) - 10} dòng FAIL")
            n_fail += 1
        else:
            print(f"PASS {job.target} {count} ảnh trùng mốc (max diff ≤ {MAX_DIFF}, khác ≤ 0,01 %)")
    print(f"TỔNG: {len(JOBS) - n_fail} PASS, {n_fail} FAIL")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
