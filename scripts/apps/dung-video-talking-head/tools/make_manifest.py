# -*- coding: utf-8 -*-
"""make_manifest.py — sinh `releases/<ver>/MANIFEST.sha256` (spec §4.3): sha256
từng file thật sự thuộc bản release, sắp theo đường dẫn. `rules.lock` khoá qua
sha của chính file này (`thlib.state.write_lock`), còn `lint_rules.py` và
`verify.py` (V1) băm lại từng file so với từng dòng MANIFEST (C10) — nên sửa
một file release mà không chạy lại lệnh này là FAIL.

Quy tắc băm và danh sách bỏ qua nằm ở `thlib.manifest` của release (cùng mã
lint_rules/V1 dùng để kiểm lại); script này chỉ ghi file.

Dùng: PYTHONIOENCODING=utf-8 python tools/make_manifest.py [--ver 1.2.3]
(tools/ — công cụ dev, Hermes không liệt kê thư mục này cho worker; Ruling R36)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
DEFAULT_VERSION = "1.2.3"
_SCRIPTS = SKILL / "releases" / DEFAULT_VERSION / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from thlib.manifest import MANIFEST_NAME, build_manifest  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sinh MANIFEST.sha256 cho một bản release")
    ap.add_argument("--ver", default=DEFAULT_VERSION, help="Số bản release, vd 1.1.1")
    ap.add_argument(
        "--release-dir",
        help="Ghi đè thư mục release (mặc định SKILL/releases/<ver>) — test dùng để không "
        "đụng release thật",
    )
    args = ap.parse_args(argv)

    release_dir = Path(args.release_dir) if args.release_dir else SKILL / "releases" / args.ver
    if not release_dir.is_dir():
        print(f"Không tìm thấy {release_dir}")
        return 1

    manifest = build_manifest(release_dir)
    (release_dir / MANIFEST_NAME).write_text(manifest, encoding="utf-8")
    print(f"PASS: đã ghi {release_dir / MANIFEST_NAME} ({len(manifest.splitlines())} file)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
