"""thlib.rules — nạp rules.json theo version (hoặc theo rules.lock của dự án),
kiểm schema, tra giá trị bằng đường dẫn chấm, và ngân sách SFX mỗi video.

rules.json là dữ liệu (không phải code): mọi trị số đo/luật nằm trong
`params`, mỗi lá (giá trị không phải object) có một entry tương ứng trong
`sources` ghi nhãn căn cứ (spec §5.2/§8.2) và độ tin cậy.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jsonschema

from . import paths, state


@dataclass(frozen=True)
class Rules:
    """Bộ luật đã nạp: raw đầy đủ (dict), version, sha256 của rules.json."""

    raw: dict
    version: str
    sha256: str

    def get(self, dotted: str) -> Any:
        """Tra `params` theo đường dẫn chấm, ví dụ 'sfx.p2p_s'. Ném KeyError
        kèm đường dẫn nếu không tìm thấy."""
        node: Any = self.raw["params"]
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                raise KeyError(dotted)
            node = node[part]
        return node

    def preset(self, name: str) -> dict:
        """Tham số của preset `name` (params.presets.<name>)."""
        return self.get(f"presets.{name}")


def _rules_path(ver: str) -> Path:
    return paths.release_dir(ver) / "rules.json"


def _schema_path(ver: str) -> Path:
    return paths.release_dir(ver) / "rules.schema.json"


def load(ver: str | None = None, project: Path | None = None) -> Rules:
    """Nạp rules.json của bản `ver`; nếu truyền `project`, version lấy từ
    rules.lock của dự án đó (bỏ qua `ver`)."""
    if project is not None:
        ver = state.read_lock(project)["version"]
    if ver is None:
        raise ValueError("rules.load cần truyền ver hoặc project")

    rules_file = _rules_path(ver)
    raw = json.loads(rules_file.read_text(encoding="utf-8"))
    sha256 = hashlib.sha256(rules_file.read_bytes()).hexdigest()
    return Rules(raw=raw, version=raw["version"], sha256=sha256)


def _iter_leaves(node: Any, prefix: str = ""):
    """Duyệt đệ quy `params`, sinh đường dẫn chấm tới từng lá (object thì đi
    tiếp; list/số/chuỗi là lá, không đi tiếp)."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _iter_leaves(value, f"{prefix}.{key}" if prefix else key)
    else:
        yield prefix


def leaves_without_source(raw: dict) -> list[str]:
    """Đường dẫn lá trong `params` chưa có entry tương ứng trong `sources`."""
    sources = raw.get("sources", {})
    return [p for p in _iter_leaves(raw["params"]) if p not in sources]


def validate(raw: dict) -> None:
    """Kiểm `raw` theo rules.schema.json của đúng version; ném lỗi nếu sai."""
    schema = json.loads(_schema_path(raw["version"]).read_text(encoding="utf-8"))
    jsonschema.validate(raw, schema)


def per_video_budget(rules_obj: Rules, preset_name: str, duration_s: float) -> int:
    """PER_VIDEO = ceil(k × giây / 10) theo S11 (§5.3)."""
    k = rules_obj.preset(preset_name)["k_per10"]
    return math.ceil(k * duration_s / 10)
