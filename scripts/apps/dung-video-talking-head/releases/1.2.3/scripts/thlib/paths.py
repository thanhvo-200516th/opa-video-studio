"""thlib.paths — đường dẫn gốc của skill và của dự án dựng video.

Ruling R3: SKILL không hard-code, mà suy ra từ vị trí file này. File này nằm ở
SKILL/releases/1.1.1/scripts/thlib/paths.py nên đi lên 4 cấp thư mục là gốc SKILL
(bỏ qua thlib, scripts, 1.1.1, releases). Nhờ vậy repo có thể nằm ở bất cứ đâu
(worktree kiểm thử hay skill thật) mà code không cần sửa.
"""

from __future__ import annotations

import os
from pathlib import Path

SKILL: Path = Path(__file__).resolve().parents[4]

VID_ROOT: Path = Path(os.environ.get("TH_VID_ROOT", "D:/MMO/Van Minh AI/Vid Heygen"))
DOCS_ROOT: Path = Path(os.environ.get("TH_DOCS_ROOT", "D:/MMO/Van Minh AI"))
SFX_LIB: Path = Path(
    os.environ.get("TH_SFX_LIB", "D:/Vibe Coding/AI Video/video-shotcraft/assets/audio")
)


def release_dir(ver: str) -> Path:
    """Thư mục chứa luật + code của một bản release: SKILL/releases/<ver>."""
    return SKILL / "releases" / ver


def project_dir(n: int, ver: str) -> Path:
    """Thư mục dựng video số n theo bản luật ver: VID_ROOT/<n>/edit-r<ver>."""
    return VID_ROOT / str(n) / f"edit-r{ver}"


def batch_dir(b: str) -> Path:
    """Thư mục của một lô duyệt: VID_ROOT/_batches/<b>."""
    return VID_ROOT / "_batches" / b
