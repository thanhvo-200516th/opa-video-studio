#!/usr/bin/env python3
"""Tái tạo các lỗi lô KB cũ và kiểm spec_lint bắt đúng mã. Chạy: ~/.venvs/video-skills/bin/python tests/test_spec_lint.py"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from spec_lint import lint  # noqa: E402
from vn_numbers import expand_tokens, read_number  # noqa: E402


def make_media(d: Path) -> tuple[Path, Path]:
    v, a = d / "v.mp4", d / "sfx.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=black:s=108x192:d=4", "-r", "30", str(v)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=d=0.5", str(a)], check=True)
    return v, a


def good_spec(v: Path, a: Path) -> dict:
    return {"name": "KB99", "fps": 30, "width": 108, "height": 192, "duration": 4.0, "tracks": [
        {"type": "video", "name": "V1", "clips": [{"src": str(v), "at": 0.0, "in": 0.0, "dur": 4.0,
                                                   "motion": {"scale": [[0.0, 100, "linear"], [3.9, 110, "linear"]]}}]},
        {"type": "text", "name": "text 1", "clips": [{"text": "HOOK", "at": 0.2, "dur": 1.5,
                                                      "effects": [{"effect": "glow", "params": {"amount": [[0, 0], [0.3, 80]]}}]}]},
        {"type": "audio", "name": "A1 Giọng", "clips": [{"src": str(v), "at": 0.0, "in": 0.0, "dur": 4.0}]},
        {"type": "audio", "name": "A2 SFX (mở đầu)", "clips": [{"src": str(a), "at": 0.0, "in": 0.0, "dur": 0.32, "name": "SFX MỞ ĐẦU"}]},
    ]}


WORDS = [["Tại", 0.1, 0.3], ["sao", 0.32, 0.5], ["anh", 0.6, 0.8]]


def status(res: list[dict], cid: str) -> str:
    return next(r["status"] for r in res if r["id"] == cid)


def run(spec: dict, d: Path, words=WORDS, name: str = "kb99.craft.json") -> list[dict]:
    p = d / name
    p.write_text(json.dumps(spec, ensure_ascii=False))
    return lint(p, words)


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        v, a = make_media(d)
        base = good_spec(v, a)
        res = run(base, d)
        assert not [r for r in res if r["status"] != "OK"], [r for r in res if r["status"] != "OK"]

        cases = []
        s = copy.deepcopy(base); s["tracks"][1]["clips"][0]["effects"][0]["params"]["amount"] = [[0, 0], [0.3, 80], [0.3, 0]]
        cases.append(("keys_not_increasing", "HARD", s, WORDS))          # KB07: wonder_glow trùng mốc 0.3
        s = copy.deepcopy(base); s["tracks"][3]["clips"][0]["dur"] = 0.9
        cases.append(("clip_past_file_end", "HARD", s, WORDS))           # KB08: SFX ngắn hơn dur
        s = copy.deepcopy(base); s["tracks"][3]["clips"][0]["src"] = str(d / "khong_co.wav")
        cases.append(("media_missing", "HARD", s, WORDS))
        s = copy.deepcopy(base); s["tracks"][1]["clips"][0]["at"] = 2.0
        cases.append(("hook_text_late", "SOFT", s, WORDS))
        cases.append(("hook_first_word_late", "SOFT", base, [["Tại", 0.7, 0.9]]))
        cases.append(("dead_air", "SOFT", base, WORDS + [["em", 1.8, 2.0]]))
        s = copy.deepcopy(base); s["tracks"][0]["clips"][0]["dur"] = 3.6
        cases.append(("picture_ends_before_voice", "SOFT", s, WORDS))
        cases.append(("black_tail", "SOFT", s, WORDS))
        s = copy.deepcopy(base); s["tracks"][3]["clips"] = []
        cases.append(("opening_sfx", "SOFT", s, WORDS))
        s = copy.deepcopy(base); s["width"], s["height"] = 1080, 1920
        cases.append(("low_res_source", "SOFT", s, WORDS))            # Rule 3: nguồn 108x192 trên khung 1080x1920
        for cid, want, spec, words in cases:
            got = status(run(spec, d, words), cid)
            assert got == want, f"{cid}: muốn {want}, được {got}"
            print(f"ok  {cid:<26} → {want}")
        assert status(run(base, d, name="xm02_90phantram_boxo.craft.json"), "craft_name") == "SOFT"
        print("ok  craft_name                 → SOFT")

    assert read_number("90%") == ["chín", "mươi", "phần", "trăm"]
    assert read_number("21") == ["hai", "mươi", "mốt"]
    assert read_number("105") == ["một", "trăm", "lẻ", "năm"]
    assert read_number("50.000") == ["năm", "mươi", "nghìn"]
    assert read_number("20tr") == ["hai", "mươi", "triệu"]
    assert expand_tokens(["ngàn"]) == ["nghìn"]
    print("ok  vn_numbers")
    print("TẤT CẢ ĐẠT")


if __name__ == "__main__":
    main()
