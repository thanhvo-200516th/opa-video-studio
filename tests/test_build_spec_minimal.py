#!/usr/bin/env python3
"""Mẫu assets/motion-fx/build_spec_minimal.py (hồ sơ minimal-edu): chạy trên bản sao đầu vào KB08 với khối ví dụ ở đầu file mẫu
→ số track / clip trong ±10 % của kb08.craft.json dựng tay, spec_lint 0 HARD, edit_rules audit 0 LỖI; thiếu profile → dừng rõ ràng.
Chạy: ~/.venvs/video-skills/bin/python tests/test_build_spec_minimal.py"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_profile  # noqa: E402
from edit_rules import audit_spec  # noqa: E402
from spec_lint import lint  # noqa: E402

TEMPLATE = ROOT / "assets/motion-fx/build_spec_minimal.py"
DEMO = Path("/home/vmiz/Thanh/Media/A huy/Kich_ban/30 VID/Danh_Sach_Kich_Ban_6-10/"
            "18_KB08_AI_Lam_Video_Bat_Dong_San_Tu_Khoanh_Vung_Ban_Do_Google_/v_minimal105/work")
INPUTS = ("kb08.base.craft.json", "words_tl.json", "profile.json", "pain.json")
EDIT_RE = re.compile(r"(# -{20,} CHỈ SỬA[^\n]*\n)(.*?)(# -{20,} hết phần sửa\n)", re.S)
EXAMPLE_RE = re.compile(r"# --- VÍ DỤ KB08[^\n]*\n(.*?)# --- hết ví dụ ---", re.S)


def kb08_template() -> str:
    """Mẫu với khối `# EDIT` thay bằng khối ví dụ KB08 (bỏ "# " đầu dòng)."""
    src = TEMPLATE.read_text(encoding="utf-8")
    example = "".join(re.sub(r"^# ?", "", ln, count=1) + "\n" for ln in EXAMPLE_RE.search(src).group(1).splitlines())
    return EDIT_RE.sub(lambda m: m.group(1) + example + m.group(3), src, count=1)


def counts(spec: dict) -> tuple[int, int]:
    return len(spec["tracks"]), sum(len(t["clips"]) for t in spec["tracks"])


def workdir(name: str) -> Path:
    w = Path(tempfile.mkdtemp(prefix="build_minimal_")) / name / "work"
    w.mkdir(parents=True)
    return w


def run(w: Path) -> subprocess.CompletedProcess:
    env = {**os.environ, "OPA_SKILL_DIR": str(ROOT)}
    return subprocess.run([sys.executable, str(w / "build_spec_minimal.py")], capture_output=True, text=True, env=env, timeout=900)


def test_template_on_kb08() -> None:
    w = workdir("v1")
    for f in INPUTS:
        shutil.copy(DEMO / f, w / f)
    (w / "build_spec_minimal.py").write_text(kb08_template(), encoding="utf-8")
    r = run(w)
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-2500:]
    spec = json.loads((w / "kb08.craft.json").read_text(encoding="utf-8"))
    ref = json.loads((DEMO / "kb08.craft.json").read_text(encoding="utf-8"))
    (tn, tc), (rn, rc) = counts(spec), counts(ref)
    assert abs(tn - rn) <= max(1, 0.1 * rn) and abs(tc - rc) <= 0.1 * rc, f"tracks {tn} vs {rn}, clips {tc} vs {rc}"
    words = json.loads((w / "words_tl.json").read_text(encoding="utf-8"))
    hard = [x for x in lint(w / "kb08.craft.json", words) if x["status"] == "HARD"]
    assert not hard, hard
    prof = style_profile.load(w / "kb08.craft.json")
    bad = [x for x in audit_spec(spec, words, ["bãi đất trống", "quên ngay"], profile=prof) if x["status"] == "LỖI"]
    assert not bad, bad
    print(f"ok  KB08: {tn} track / {tc} clip (dựng tay {rn} / {rc}), 0 HARD, 0 LỖI")


def test_requires_minimal_profile() -> None:
    w = workdir("v2")
    for f in INPUTS:
        shutil.copy(DEMO / f, w / f)
    (w / "profile.json").write_text("{}", encoding="utf-8")
    (w / "build_spec_minimal.py").write_text(kb08_template(), encoding="utf-8")
    r = run(w)
    assert r.returncode != 0 and "minimal-edu" in (r.stdout + r.stderr), r.stderr[-800:]
    assert not (w / "kb08.craft.json").exists()
    print("ok  thiếu hồ sơ minimal-edu → dừng, nói rõ lý do")


def test_empty_groups_stops() -> None:
    w = workdir("v3")
    for f in INPUTS:
        shutil.copy(DEMO / f, w / f)
    shutil.copy(TEMPLATE, w / "build_spec_minimal.py")
    r = run(w)
    assert r.returncode != 0 and "GROUPS" in (r.stdout + r.stderr), r.stderr[-800:]
    print("ok  GROUPS trống → dừng, nói rõ lý do")


if __name__ == "__main__":
    if not DEMO.is_dir():
        print(f"bỏ qua: không có đầu vào KB08 ở {DEMO}")
        sys.exit(0)
    for n in [n for n in sorted(globals()) if n.startswith("test_")]:
        globals()[n]()
    print("TẤT CẢ ĐẠT")
