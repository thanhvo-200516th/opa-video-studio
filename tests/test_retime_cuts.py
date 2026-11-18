#!/usr/bin/env python3
"""build_kit.retime_cuts: dời điểm cắt cứng V1 về `lead_frames` khung trước chữ đầu câu. Offline (flen giả, không ffprobe).
Chạy: ~/.venvs/video-skills/bin/python tests/test_retime_cuts.py"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_kit import retime_cuts  # noqa: E402

FPS = 30
LEN = {"a.mp4": 10.0, "b.mp4": 10.0}
flen = LEN.__getitem__


def clips():
    return [{"src": "a.mp4", "at": 0.0, "in": 0.0, "dur": 3.0}, {"src": "b.mp4", "at": 3.0, "in": 2.0, "dur": 4.0}]


def test_moves_to_one_frame_before_word() -> None:
    src = clips()
    out, moved = retime_cuts(src, [("x", 0.5, 0.9), ("mới", 3.2, 3.6)], FPS, flen=flen)
    assert abs(out[1]["at"] - (3.2 - 1 / FPS)) < 1e-3 and abs(out[1]["at"] * FPS - round(out[1]["at"] * FPS)) < 0.01, out[1]["at"]
    assert moved == [(3.0, round((out[1]["at"] - 3.0) * 1000))] and moved[0][1] > 0
    d = out[1]["at"] - 3.0
    assert abs(out[0]["dur"] - (3.0 + d)) < 1e-3 and abs(out[1]["in"] - (2.0 + d)) < 1e-3 and abs(out[1]["dur"] - (4.0 - d)) < 1e-3
    assert abs(out[0]["at"] + out[0]["dur"] - out[1]["at"]) < 1e-3                         # liền mạch, không hở / chồng
    assert abs(out[1]["at"] + out[1]["dur"] - 7.0) < 1e-3                                  # cuối cảnh giữ nguyên


def test_immutable_input() -> None:
    src = clips()
    before = copy.deepcopy(src)
    out, _ = retime_cuts(src, [("mới", 3.2, 3.6)], FPS, flen=flen)
    assert src == before and out is not src and out[0] is not src[0]


def test_lead_frames_and_dict_words() -> None:
    out, moved = retime_cuts(clips(), [{"text": "mới", "start": 3.2, "end": 3.6}], FPS, lead_frames=2, flen=flen)
    assert abs(out[1]["at"] - (3.2 - 2 / FPS)) < 1e-3 and moved


def test_word_before_cut_moves_earlier() -> None:
    out, moved = retime_cuts(clips(), [("mới", 2.97, 3.3)], FPS, flen=flen)             # chữ bắt đầu trước điểm cắt 0,03 s → cắt dời lùi
    assert out[1]["at"] < 3.0 and moved[0][1] < 0 and abs(out[0]["dur"] - out[1]["at"]) < 1e-3


def test_skips() -> None:
    far, m = retime_cuts(clips(), [("mới", 3.6, 4.0)], FPS, flen=flen)                  # chữ cách cắt > 0,4 s
    assert far == clips() and m == []
    none, m = retime_cuts(clips(), [("cũ", 1.0, 1.5)], FPS, flen=flen)                  # không có chữ nào sau điểm cắt
    assert none == clips() and m == []
    neg = [{"src": "a.mp4", "at": 0.0, "in": 0.0, "dur": 3.0}, {"src": "b.mp4", "at": 3.0, "in": 0.05, "dur": 4.0}]
    out, m = retime_cuts(neg, [("mới", 2.9, 3.3)], FPS, flen=flen)                      # in của clip sau sẽ < 0
    assert out == neg and m == []
    tight = [{"src": "a.mp4", "at": 0.0, "in": 7.0, "dur": 3.0}, {"src": "b.mp4", "at": 3.0, "in": 2.0, "dur": 4.0}]
    out, m = retime_cuts(tight, [("mới", 3.2, 3.6)], FPS, flen=flen)                    # đoạn trước vượt hết file a.mp4 (10 s)
    assert out == tight and m == []
    exact, m = retime_cuts(clips(), [("mới", 3.0 + 1 / FPS, 3.5)], FPS, flen=flen)      # đã đúng 1 khung → không dời
    assert exact == clips() and m == []


def test_chain_of_cuts() -> None:
    three = clips() + [{"src": "a.mp4", "at": 7.0, "in": 1.0, "dur": 2.0}]
    out, moved = retime_cuts(three, [("a", 3.2, 3.5), ("b", 7.1, 7.4)], FPS, flen=flen)
    assert len(moved) == 2 and abs(out[2]["at"] - (7.1 - 1 / FPS)) < 1e-3
    assert abs(out[1]["at"] + out[1]["dur"] - out[2]["at"]) < 1e-3                       # clip giữa co / giãn theo cả hai đầu


if __name__ == "__main__":
    fns = sorted((k, v) for k, v in globals().items() if k.startswith("test_"))
    for name, fn in fns:
        fn()
        print("ok", name)
    print(f"TẤT CẢ ĐẠT ({len(fns)} bài kiểm)")
