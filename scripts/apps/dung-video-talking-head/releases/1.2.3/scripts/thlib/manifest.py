"""thlib.manifest — MANIFEST.sha256 của một bản release (spec §4.3): sinh (tools/make_manifest.py)
và băm lại từng file để kiểm (lint_rules.py, V1 của verify — C10).

MANIFEST = một dòng "<sha256>  <đường dẫn posix>" cho mỗi file thật sự thuộc release, sắp theo
đường dẫn; bỏ sản phẩm build không commit (`__pycache__`, `node_modules`, `.pytest_cache`,
`*.pyc`) và chính MANIFEST.sha256. `rules.lock` khoá sha của file MANIFEST.

sha của file văn bản (không có byte NUL) tính sau khi đổi CRLF → LF: git `core.autocrlf=true`
checkout thư mục skill thật bằng CRLF còn worktree dev có file LF lẫn CRLF, nên sha phải theo nội
dung chứ không theo kiểu xuống dòng; file nhị phân (WAV, PNG…) băm nguyên byte.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

MANIFEST_NAME = "MANIFEST.sha256"
_SKIP_DIR_NAMES = {"__pycache__", "node_modules", ".pytest_cache"}


def file_sha256(path: Path) -> str:
    """sha256 nội dung `path` (văn bản: CRLF → LF trước khi băm; nhị phân: nguyên byte)."""
    data = Path(path).read_bytes()
    if b"\0" not in data:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def _tracked_paths(release_dir: Path) -> list[str]:
    """Đường dẫn tương đối (posix) của mọi file thuộc release, trừ MANIFEST.sha256 và sản phẩm
    build — sắp theo path."""
    rels = []
    for p in release_dir.rglob("*"):
        if not p.is_file() or p.suffix == ".pyc":
            continue
        rel = p.relative_to(release_dir)
        if rel.name == MANIFEST_NAME or _SKIP_DIR_NAMES & set(rel.parts[:-1]):
            continue
        rels.append(rel.as_posix())
    return sorted(rels)


def build_manifest(release_dir: Path) -> str:
    """Nội dung MANIFEST.sha256: mỗi dòng "<sha256>  <path>", kết thúc bằng dòng mới; rỗng nếu
    release không có file nào."""
    release_dir = Path(release_dir)
    lines = [f"{file_sha256(release_dir / rel)}  {rel}" for rel in _tracked_paths(release_dir)]
    return "".join(f"{line}\n" for line in lines)


def _names(release_dir: Path, rels: list[str], limit: int = 5) -> str:
    shown = ", ".join((release_dir / rel).as_posix() for rel in rels[:limit])
    return shown + (f" (+{len(rels) - limit} file)" if len(rels) > limit else "")


def release_errors(release_dir: Path, locked_sha: str | None) -> list[str]:
    """Kiểm khoá release cho lint_rules.py và V1 (spec §4.3, C10): MANIFEST.sha256 có mặt, sha của
    nó đúng `locked_sha` (rules.lock), và mọi file của release băm lại khớp từng dòng MANIFEST —
    sửa tại chỗ, xoá hay thêm một file mà không sinh lại MANIFEST đều là lệch. Trả danh sách lỗi
    (rỗng = khớp); đường dẫn trong lỗi là tuyệt đối."""
    release_dir = Path(release_dir).absolute()
    path = release_dir / MANIFEST_NAME
    if not path.is_file():
        return [f"thiếu {path.as_posix()} — không kiểm được file nào của bản release"]
    errors = []
    current = file_sha256(path)
    if current != locked_sha:
        errors.append(f"sha {path.as_posix()} lệch rules.lock (đã khoá={locked_sha}, hiện tại={current})")
    listed: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        sha, sep, rel = line.partition("  ")
        if not sep or len(sha) != 64:
            return errors + [f"{path.as_posix()} có dòng sai khuôn: {line[:80]!r}"]
        listed[rel] = sha
    on_disk = _tracked_paths(release_dir)
    changed = [rel for rel in on_disk if rel in listed and file_sha256(release_dir / rel) != listed[rel]]
    missing = sorted(set(listed) - set(on_disk))
    extra = [rel for rel in on_disk if rel not in listed]
    for label, rels in (("sửa sau khi sinh MANIFEST", changed), ("thiếu so với MANIFEST", missing),
                        ("không có trong MANIFEST", extra)):
        if rels:
            errors.append(f"file release {label}: {_names(release_dir, rels)}")
    return errors
