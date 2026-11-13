"""check_prep.py — cổng của stage PREP (spec §7.1): kiểm một phiếu `prep/prep-<k>.json`.

Dùng:
    PYTHONIOENCODING=utf-8 python check_prep.py <đường dẫn prep-<k>.json>

Kiểm theo khuôn phiếu (thlib.prep.SCHEMA): mọi video có status và broll_class; mọi asset của
video `heavy` có mô tả (desc) và câu neo (anchor_quote); status khác ok và claim_gate phải có lý
do. In từng lỗi, thoát mã 1 khi còn lỗi.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from thlib import prep


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Kiểm phiếu PREP theo khuôn spec §7.1")
    ap.add_argument("prep_json", help="Đường dẫn prep-<k>.json")
    args = ap.parse_args(argv)

    data, errors = prep.read(Path(args.prep_json))
    if errors:
        print(f"FAIL: {Path(args.prep_json).name} có {len(errors)} lỗi")
        for e in errors:
            print(f"  {e}")
        return 1
    print(f"PASS: {Path(args.prep_json).name} đúng khuôn ({len(data['videos'])} video)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
