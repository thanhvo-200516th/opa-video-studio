#!/usr/bin/env python3
"""Kiểm style_profile: không có profile.json → None; có → nạp minimal-edu; tên lạ → thoát."""
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import style_profile as sp  # noqa: E402

with tempfile.TemporaryDirectory() as td:
    w = Path(td)
    spec = w / "x.craft.json"; spec.write_text("{}")
    assert sp.load(spec) is None and not sp.active(None, "minimal-edu")
    (w / "profile.json").write_text(json.dumps({"profile": "minimal-edu"}))
    p = sp.load(spec)
    assert sp.active(p, "minimal-edu") and sp.get(p, "text.exit_frames") == 2
    assert sp.get(p, "cuts.hard_cuts_allowed") is True and sp.get(p, "text.zones") == "B8"
    assert sp.get(p, "nope.x", 7) == 7 and sp.load(w)["name"] == "minimal-edu"
    (w / "profile.json").write_text(json.dumps({"profile": "la"}))
    try:
        sp.load(spec); raise AssertionError("phải thoát")
    except SystemExit:
        pass
print("TẤT CẢ ĐẠT")
