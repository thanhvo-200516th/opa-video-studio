"""lint_rules.py — kiểm rules.lock + rules.json của một dự án dựng video.

Dùng: PYTHONIOENCODING=utf-8 python lint_rules.py <project_dir>

Thoát mã 1 khi: rules.lock thiếu version; bản release lệch khoá (C10,
thlib.manifest.release_errors) — thiếu MANIFEST.sha256, sha MANIFEST khác
rules.lock, hoặc một file của release băm lại khác dòng MANIFEST của nó (sửa tại
chỗ mà không sinh lại MANIFEST; nên lint ngay sau khi scaffold ghi lock mới vẫn
có nghĩa); rules.json sai rules.schema.json; hoặc rules.json có lá (giá trị
trong params) thiếu entry tương ứng trong sources.
"""

from __future__ import annotations

import sys
from pathlib import Path

import jsonschema

from thlib import manifest, paths, rules, state


def lint(project: Path) -> list[str]:
    """Kiểm dự án `project`; trả về danh sách lỗi (rỗng = PASS)."""
    project = Path(project)
    errors: list[str] = []

    try:
        lock = state.read_lock(project)
    except FileNotFoundError:
        errors.append(f"Thiếu {state.LOCK_FILENAME} ở {project}")
        return errors

    ver = lock.get("version")
    if not ver:
        errors.append(f"{state.LOCK_FILENAME} thiếu version")
        return errors

    errors += [f"Bản release {ver}: {e}"
               for e in manifest.release_errors(paths.release_dir(ver), lock.get("manifest_sha256"))]

    try:
        R = rules.load(ver)
    except FileNotFoundError:
        errors.append(f"Không tìm thấy rules.json cho bản {ver}")
        return errors

    try:
        rules.validate(R.raw)
    except jsonschema.exceptions.ValidationError as exc:
        errors.append(f"rules.json sai schema: {exc.message} (tại {list(exc.path)})")

    missing = rules.leaves_without_source(R.raw)
    if missing:
        errors.append(
            f"rules.json thiếu sources cho {len(missing)} lá: {', '.join(missing[:10])}"
        )

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Dùng: lint_rules.py <project_dir>")
        return 1

    errors = lint(Path(sys.argv[1]))
    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return 1

    print("PASS: rules.lock + rules.json hợp lệ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
