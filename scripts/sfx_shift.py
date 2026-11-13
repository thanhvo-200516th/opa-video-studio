#!/usr/bin/env python3
"""sfx_shift.py — dời SFX trong spec theo danh sách của qa_sync (v2.8: mọi loại nhịp), ghi spec MỚI (không sửa spec gốc).

    python3 sfx_shift.py SPEC.levels.craft.json SHIFTS.json OUT.craft.json
    SHIFTS.json = qa_sync ghi ở OUT_DIR/sfx_shifts.json: [{"beat","clip","track","at","src","name","shift" | "trim"}…];
    beat = cut | text | punch | open (chỉ để báo cáo; cách sửa giống nhau); shift > 0 = dời muộn hơn (giây);
    trim = bỏ bấy nhiêu giây đầu file, đỉnh tiếng giữ nguyên (at và in cùng tăng).

Khớp clip theo (rãnh, at ±2 ms, src). Kẹp: không dời tới trước 0 s, không để clip vượt hết video; riêng clip đã ở đầu video
(at ≤ 0,05 s) mà phải dời sớm thì cắt phần đầu file (`in` tăng, `dur` giảm, keyframe gain dịch theo) — dùng cho SFX mở đầu
có lặng đầu. Thoát 1 nếu có mục không khớp clip nào (spec đã đổi sau khi đo → chạy lại qa_sync). Cảnh báo (không lỗi) khi hai SFX cùng rãnh chồng nhau sau khi dời. Sau đó: fc_build_fast
spec mới → qa_sync lại.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import numpy as np

AT_TOL = 0.002
HEAD_AT = 0.05             # s: clip có at ≤ mức này = SFX mở đầu


def _trim_head(clip: dict, x: float) -> None:
    """Bỏ x giây đầu của clip (at giữ nguyên): in += x, dur -= x, keyframe gain_db dịch −x (giữ giá trị tại 0)."""
    x = min(x, clip["dur"] - 0.05)
    g = clip.get("gain_db")
    if isinstance(g, list):
        ks = sorted((float(k[0]), float(k[1])) for k in g)
        v0 = float(np.interp(x, [k[0] for k in ks], [k[1] for k in ks]))
        clip["gain_db"] = [[0, round(v0, 3)]] + [[round(t - x, 4), v] for t, v in ks if t > x]
    clip["in"] = round(float(clip.get("in", 0)) + x, 4)
    clip["dur"] = round(clip["dur"] - x, 4)


def overlaps(spec: dict) -> list[str]:
    """Các cặp SFX cùng rãnh chồng nhau (> 1 ms) — sau khi dời có thể sinh ra."""
    out = []
    for t in spec["tracks"]:
        if t.get("type") == "audio" and "SFX" in t.get("name", ""):
            cs = sorted(t["clips"], key=lambda c: c["at"])
            out += [f"{t['name']} · {a['at']:.3f}+{a['dur']:.2f} chồng {b['at']:.3f}" for a, b in zip(cs, cs[1:])
                    if a["at"] + a["dur"] > b["at"] + 0.001]
    return out


def apply_shifts(spec: dict, shifts: list[dict]) -> tuple[dict, list[str], list[str]]:
    """(spec mới, các dòng đã dời, các mục không khớp). Không đổi spec đầu vào."""
    out = copy.deepcopy(spec)
    end = float(out["duration"])
    done: list[str] = []
    missing: list[str] = []
    for sh in shifts:
        clip = next((c for t in out["tracks"] if t.get("name") == sh["track"] for c in t["clips"]
                     if abs(c["at"] - sh["at"]) <= AT_TOL and c.get("src") == sh["src"]), None)
        if clip is None:
            missing.append(f"{sh['track']} · {sh['at']:.3f} s · {sh.get('name', '')}")
            continue
        cut = float(sh.get("trim", 0.0))                  # bỏ đầu file, đỉnh tiếng giữ nguyên: at và in cùng + cut
        want = clip["at"] + float(sh.get("shift", 0.0)) + cut
        trim = cut or (-want if want < 0 and clip["at"] <= HEAD_AT else 0.0)   # chỉ clip đã ở đầu video mới cắt đầu file khi dời sớm
        new_at = want if cut else min(max(0.0, want), max(0.0, end - clip["dur"]))
        done.append(f"[{sh.get('beat', '?')}] {sh['track']} · {clip['at']:.3f} → {new_at:.3f} s ({new_at - clip['at']:+.3f})"
                    f"{f' · cắt đầu {trim:.3f} s' if trim else ''} · {sh.get('name', '')}")
        clip["at"] = round(new_at, 4)
        if trim:
            _trim_head(clip, trim)
    return out, done, missing


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    shifts = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    out_path = Path(sys.argv[3])
    if out_path.resolve() == Path(sys.argv[1]).resolve():
        print("LỖI: tệp ra trùng spec gốc — ghi sang tên mới.")
        return 2
    new, done, missing = apply_shifts(spec, shifts)
    out_path.write_text(json.dumps(new, ensure_ascii=False), encoding="utf-8")
    print("\n".join(f"dời  {d}" for d in done) or "không có SFX nào cần dời")
    for m in missing:
        print(f"LỖI không khớp clip nào: {m}")
    for o in overlaps(new):
        print(f"CẢNH BÁO chồng nhau: {o}")
    print(f"→ {out_path} ({len(done)} dời · {len(missing)} không khớp). Dựng lại bằng fc_build_fast rồi chạy lại qa_sync.")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
