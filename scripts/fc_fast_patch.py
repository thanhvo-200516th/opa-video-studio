#!/usr/bin/env python3
"""fc_fast_patch.py — Sửa trực tiếp thông số trong file .fcproj (< 0.05 giây) không cần chạy lại fc_build.py.

Hỗ trợ sửa tức thì ở Tầng 8 (khi người dùng yêu cầu dịch chữ, đổi cỡ chữ, đổi màu, chỉnh scale B-roll,
tăng/giảm âm lượng hoặc chỉnh ngưỡng Master Hard Limiter) trên cấu trúc JSON gốc của FilmCraft 0.13.

Ví dụ:
    # 1. Chỉnh Master Hard Limiter về -2.2 dB trong 0.03s:
    python3 fc_fast_patch.py PROJECT.fcproj --limiter-max -2.2

    # 2. Hạ chữ sau đầu ở Hook xuống y=715 và đổi cỡ chữ 205:
    python3 fc_fast_patch.py PROJECT.fcproj --clip "CHỈ MẤT 30 GIÂY" --y 715 --size 205

    # 3. Dịch toàn bộ phụ đề trên track V18 lên 20px (dy = -20):
    python3 fc_fast_patch.py PROJECT.fcproj --track V18 --dy -20

    # 4. Đổi scale cho clip trên track V3 (B-roll):
    python3 fc_fast_patch.py PROJECT.fcproj --track V3 --scale 156.9
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


def hex_to_rgba(hex_str: str) -> list[float]:
    h = hex_str.lstrip("#")
    if len(h) == 6:
        r, g, b = int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0
        return [round(r, 4), round(g, 4), round(b, 4), 1.0]
    if len(h) == 8:
        r, g, b, a = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4, 6))
        return [round(r, 4), round(g, 4), round(b, 4), round(a, 4)]
    raise ValueError(f"Màu hex không hợp lệ: {hex_str}")


def _patch_vec2(param_obj: dict, x: float | None, y: float | None, dx: float | None, dy: float | None) -> None:
    vec = param_obj.get("value", {}).get("Vec2")
    if vec:
        if x is not None:
            vec["x"] = float(x)
        if y is not None:
            vec["y"] = float(y)
        if dx is not None:
            vec["x"] = round(float(vec["x"]) + float(dx), 2)
        if dy is not None:
            vec["y"] = round(float(vec["y"]) + float(dy), 2)
    for kf in param_obj.get("keyframes") or []:
        kvec = kf.get("value", {}).get("Vec2")
        if kvec:
            if x is not None:
                kvec["x"] = float(x)
            if y is not None:
                kvec["y"] = float(y)
            if dx is not None:
                kvec["x"] = round(float(kvec["x"]) + float(dx), 2)
            if dy is not None:
                kvec["y"] = round(float(kvec["y"]) + float(dy), 2)


def _patch_float(param_obj: dict, val: float | None, delta: float | None) -> None:
    v = param_obj.get("value")
    old_base = v.get("Float") if isinstance(v, dict) else None
    if isinstance(v, dict) and "Float" in v:
        if val is not None:
            v["Float"] = float(val)
        if delta is not None:
            v["Float"] = round(float(v["Float"]) + float(delta), 3)
    for kf in param_obj.get("keyframes") or []:
        kv = kf.get("value")
        if isinstance(kv, dict) and "Float" in kv:
            if val is not None:
                if old_base and old_base > 0:
                    kv["Float"] = round(float(kv["Float"]) * (float(val) / float(old_base)), 3)
                else:
                    kv["Float"] = float(val)
            if delta is not None:
                kv["Float"] = round(float(kv["Float"]) + float(delta), 3)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("project", help="Đường dẫn tới file .fcproj")
    ap.add_argument("--limiter-max", type=float, default=None, help="Đặt hoặc cập nhật ngưỡng hard_limiter trên Master (VD: -2.2)")
    ap.add_argument("--track", default=None, help="Lọc theo nhãn track (VD: V3, V18, A2)")
    ap.add_argument("--clip", default=None, help="Lọc theo chuỗi con trong tên clip (VD: 'CHỈ MẤT 30 GIÂY')")
    ap.add_argument("--x", type=float, default=None, help="Đặt toạ độ X mới")
    ap.add_argument("--y", type=float, default=None, help="Đặt toạ độ Y mới")
    ap.add_argument("--dx", type=float, default=None, help="Cộng thêm độ lệch X")
    ap.add_argument("--dy", type=float, default=None, help="Cộng thêm độ lệch Y")
    ap.add_argument("--scale", type=float, default=None, help="Đặt % scale mới (tự nhân tỉ lệ các keyframe nếu có)")
    ap.add_argument("--size", type=float, default=None, help="Đặt cỡ chữ mới cho graphic_text")
    ap.add_argument("--color", default=None, help="Đặt màu chữ mới (#RRGGBB)")
    ap.add_argument("--text", default=None, help="Đặt nội dung chữ mới cho graphic_text")
    ap.add_argument("--gain-db", type=float, default=None, help="Đặt mức gain_db mới cho clip")
    ap.add_argument("--dgain-db", type=float, default=None, help="Cộng/trừ thêm dB vào gain hiện tại của clip")
    args = ap.parse_args()

    t0 = time.perf_counter()
    proj_path = Path(args.project).resolve()
    data = json.loads(proj_path.read_text(encoding="utf-8"))
    items = data["project"]["items"]
    seq = next(i["kind"]["Sequence"] for i in items.values() if "Sequence" in i.get("kind", {}))

    patched_count = 0

    # 1. Master Hard Limiter
    if args.limiter_max is not None:
        mfx = seq.setdefault("master_effects", [])
        lim = next((e for e in mfx if e.get("effect") == "hard_limiter"), None)
        if lim is None:
            mfx.append({
                "effect": "hard_limiter",
                "enabled": True,
                "params": {
                    "boost": {"value": {"Float": 0.0}},
                    "lookahead": {"value": {"Float": 7.0}},
                    "max": {"value": {"Float": float(args.limiter_max)}},
                    "release": {"value": {"Float": 100.0}},
                },
            })
        else:
            lim["params"]["max"]["value"]["Float"] = float(args.limiter_max)
        patched_count += 1

    # 2. Track / Clip modifications
    has_clip_op = any(
        v is not None
        for v in (args.x, args.y, args.dx, args.dy, args.scale, args.size, args.color, args.text, args.gain_db, args.dgain_db)
    )
    if has_clip_op:
        all_tracks = (
            [(f"V{i + 1}", tr) for i, tr in enumerate(seq.get("video_tracks", []))]
            + [(f"A{i + 1}", tr) for i, tr in enumerate(seq.get("audio_tracks", []))]
        )
        for label, tr in all_tracks:
            if args.track and label.upper() != args.track.upper():
                continue
            for it in tr.get("items", []):
                cname = it.get("name") or ""
                if args.clip and args.clip.lower() not in cname.lower():
                    continue
                fx_map = {e.get("effect"): e.get("params", {}) for e in it.get("effects", [])}
                gt = fx_map.get("graphic_text")
                mo = fx_map.get("motion")
                vol = fx_map.get("volume")

                if any(v is not None for v in (args.x, args.y, args.dx, args.dy)):
                    target_pos = gt.get("position") if (gt and "position" in gt) else (mo.get("position") if mo else None)
                    if target_pos:
                        _patch_vec2(target_pos, args.x, args.y, args.dx, args.dy)
                if args.scale is not None and mo and "scale" in mo:
                    _patch_float(mo["scale"], args.scale, None)
                if args.size is not None and gt and "size" in gt:
                    _patch_float(gt["size"], args.size, None)
                if args.color is not None and gt and "fill_color" in gt:
                    gt["fill_color"]["value"]["Color"] = hex_to_rgba(args.color)
                if args.text is not None and gt and "text" in gt:
                    gt["text"]["value"]["Text"] = args.text
                if args.gain_db is not None or args.dgain_db is not None:
                    if vol and "level" in vol:
                        _patch_float(vol["level"], args.gain_db, args.dgain_db)
                    if "gain_db" in it:
                        if args.gain_db is not None:
                            it["gain_db"] = float(args.gain_db)
                        if args.dgain_db is not None:
                            it["gain_db"] = round(float(it.get("gain_db", 0.0)) + float(args.dgain_db), 2)
                patched_count += 1

    proj_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    elapsed_ms = (time.perf_counter() - t0) * 1000
    print(f"⚡ fc_fast_patch: Đã cập nhật {patched_count} mục trong {proj_path.name} ({elapsed_ms:.1f} ms)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
