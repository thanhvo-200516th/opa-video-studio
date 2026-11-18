#!/usr/bin/env python3
"""Smoke test aroll_bank.py: 3 manifest giả có câu kêu gọi gần giống → ra bank.json, plans.json, stats.json, approval.md."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def manifest(d: Path, sid: str, hook: str, cta: str) -> Path:
    segs = [{"seq_index": 1, "type": "a-roll", "role_id": "hook", "tts_text": hook, "display_text": hook, "duration_sec": 3},
            {"seq_index": 2, "type": "b-roll", "role_id": "body", "tts_text": "Nội dung riêng của video " + sid, "duration_sec": 4},
            {"seq_index": 3, "type": "a-roll", "role_id": "cta", "tts_text": cta, "display_text": cta, "duration_sec": 4}]
    p = d / sid / "00_storyboard_manifest.json"
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps({"script_id": sid, "segments": segs}, ensure_ascii=False), encoding="utf-8")
    return p


def test_bank_runs() -> None:
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        ms = [manifest(d, f"KB0{i}", f"Bạn có biết điều số {i} không?", "Anh em nào muốn nhận mẫu, cứ bình luận ở dưới.") for i in (1, 2, 3)]
        out = d / "out"
        r = subprocess.run([sys.executable, str(ROOT / "scripts/aroll_bank.py"), *map(str, ms), "--out", str(out)],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-800:]
        for f in ("bank.json", "plans.json", "stats.json", "approval.md"):
            assert (out / f).is_file(), f"thiếu {f}"
        bank = json.loads((out / "bank.json").read_text(encoding="utf-8"))
        assert isinstance(bank, list) and bank, "bank rỗng"


if __name__ == "__main__":
    test_bank_runs()
    print("TẤT CẢ ĐẠT")
