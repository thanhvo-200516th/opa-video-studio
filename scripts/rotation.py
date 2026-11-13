#!/usr/bin/env python3
"""Sổ luân phiên cho cả lô video (học từ ghost-editor components.py: nhớ các video trước đã dùng gì, không lặp).

Trước đây mỗi video tự chọn bằng crc32(tên) → 30 video lặp mỗi cặp SFX mở đầu ~5 lần. Sổ này cấp cho từng video:
  opening_pair  — chỉ số cặp SFX mở đầu trong sfx_catalog.json (không lặp trong WINDOW video liên tiếp)
  key_seed      — hạt giống bộ 10–15 kiểu vào của chữ chính (kiểu đầu tiên không lặp, các bộ ít trùng nhau)
  accent_start  — màu chữ chính bắt đầu (lệch vòng PALETTES của gen_build_spec)
  cut_seed      — hạt giống chọn chuyển cảnh (plan_cuts_best); sổ cũ không có thì build_spec_q dùng crc32("cut"+mã) % 997
Bất biến thương hiệu (font, glow, màu phụ đề, luật chuyển cảnh) KHÔNG xoay.

    python rotation.py plan  "<thư mục gốc lô>" KB06 KB07 …     # cấp ô cho video chưa có (giữ ô đã cấp)
    python rotation.py check "<thư mục gốc lô>"                 # kiểm lặp trong cửa sổ, mã thoát 1 nếu lặp
    python rotation.py show  "<thư mục gốc lô>"
    python rotation.py plan  "<thư mục video>" OPA05 --out "<O>" # MỘT video: sổ ghi vào O (thư mục phiên bản), thư mục video chỉ ĐỌC
MÃ = `script_id` trong 00_storyboard_manifest.json (vd OPA05, KHÔNG phải mã KB trong ví dụ); build_spec_q in MÃ khi chạy.
Sổ: <thư mục gốc>/rotation.json (hoặc O/rotation.json khi có --out). build_spec_q tìm ở O trước, rồi thư mục video và 3 cấp cha;
gen_build_spec.py tìm sổ này ở thư mục cha của thư mục video.
"""
from __future__ import annotations

import json
import random
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from motion_fx import KEY_KINDS_PER_VIDEO, KEY_POOL  # noqa: E402

WINDOW = 5                 # không lặp cặp SFX mở đầu / kiểu chữ chính đầu tiên trong 5 video liên tiếp
ACCENTS = 4                # số bảng màu xoay vòng của chữ chính trong gen_build_spec (PALETTES)
SEED_TRIES = 400
CATALOG = HERE.parent / "assets/motion-fx/sfx_catalog.json"
LEDGER = "rotation.json"


def key_kinds(seed: int) -> list[str]:
    """Đúng cách MotionFX chọn bộ kiểu chữ chính từ một hạt giống."""
    rnd = random.Random(seed)
    return rnd.sample(KEY_POOL, rnd.randint(*KEY_KINDS_PER_VIDEO))


def n_pairs() -> int:
    return len(json.loads(CATALOG.read_text(encoding="utf-8"))["opening"]["pairs"])


def load(root: Path) -> dict:
    p = root / LEDGER
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {"window": WINDOW, "videos": []}


def _least_recent(pool: int, history: list[int], salt: str) -> int:
    """Ô dùng lâu nhất chưa lặp; hoà thì lệch theo tên video để lô khác không ra cùng thứ tự."""
    last = {v: i for i, v in enumerate(history)}
    off = zlib.crc32(salt.encode()) % pool
    return min(range(pool), key=lambda v: (last.get(v, -1), (v - off) % pool))


def _pick_seed(recent: list[dict], salt: str) -> int:
    banned_first = {r["key_kinds"][0] for r in recent}
    seen = [set(r["key_kinds"][:3]) for r in recent]
    base = zlib.crc32(salt.encode())
    best = None
    for k in range(SEED_TRIES):
        seed = (base + k * 7919) % 2 ** 31
        kinds = key_kinds(seed)
        if kinds[0] in banned_first:
            continue
        overlap = sum(len(set(kinds[:3]) & s) for s in seen)
        if best is None or overlap < best[0]:
            best = (overlap, seed)
            if overlap == 0:
                break
    return best[1] if best else base % 2 ** 31


def plan(root: Path, videos: list[str], out: Path | None = None) -> dict:
    """Cấp ô cho `videos`. `out` (nếu có) = thư mục ghi sổ (tạo nếu chưa có), thay cho `root`."""
    root = out or root
    if out:
        root.mkdir(parents=True, exist_ok=True)
    led = load(root)
    w = led.get("window", WINDOW)
    have = {v["video"] for v in led["videos"]}
    pairs = n_pairs()
    for name in videos:
        if name in have:
            continue
        recent = led["videos"][-(w - 1):] if w > 1 else []
        seed = _pick_seed(recent, name)
        led["videos"].append({
            "video": name,
            "opening_pair": _least_recent(pairs, [v["opening_pair"] for v in led["videos"]], name),
            "key_seed": seed,
            "key_kinds": key_kinds(seed),
            "accent_start": _least_recent(ACCENTS, [v["accent_start"] for v in led["videos"]], name),
            "cut_seed": zlib.crc32(("cut" + name).encode()) % 997,   # hạt giống chọn chuyển cảnh (cut_plan.plan_cuts_best)
        })
        have.add(name)
    (root / LEDGER).write_text(json.dumps(led, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return led


def check(led: dict) -> list[str]:
    w, vs, bad = led.get("window", WINDOW), led["videos"], []
    for i, v in enumerate(vs):
        for u in vs[max(0, i - w + 1):i]:
            if u["opening_pair"] == v["opening_pair"]:
                bad.append(f"{v['video']}: cặp SFX mở đầu {v['opening_pair']} trùng {u['video']} (trong {w} video)")
            if u["key_kinds"][0] == v["key_kinds"][0]:
                bad.append(f"{v['video']}: kiểu chữ chính đầu «{v['key_kinds'][0]}» trùng {u['video']} (trong {w} video)")
    return bad


def entry(root_or_kb: Path, video: str, out: Path | None = None) -> dict | None:
    """Ô đã cấp cho video: tìm sổ ở `out` (thư mục phiên bản O) trước, rồi thư mục này và tối đa 3 cấp cha."""
    for d in [*([out] if out else []), root_or_kb, *list(root_or_kb.parents)[:3]]:
        if (d / LEDGER).is_file():
            return next((v for v in load(d)["videos"] if v["video"] == video), None)
    return None


def main() -> int:
    if len(sys.argv) < 3 or sys.argv[1] not in ("plan", "check", "show"):
        print(__doc__)
        return 2
    root, args, out = Path(sys.argv[2]), sys.argv[3:], None
    if "--out" in args:
        i = args.index("--out")
        if i + 1 >= len(args):
            print("--out cần một thư mục")
            return 2
        out, args = Path(args[i + 1]), args[:i] + args[i + 2:]
    if out and sys.argv[1] != "plan":
        print("--out chỉ dùng với `plan`; `check` / `show` đọc thư mục gốc (hoặc O) truyền ở vị trí thứ hai")
        return 2
    led = plan(root, args, out) if sys.argv[1] == "plan" else load(root)
    if sys.argv[1] in ("plan", "show"):
        if out:
            print(f"Sổ: {out / LEDGER}")
        for v in led["videos"]:
            print(f"{v['video']:<8} SFX mở đầu #{v['opening_pair']:<2} · màu bắt đầu {v['accent_start']} · "
                  f"chữ chính: {', '.join(v['key_kinds'][:3])} … ({len(v['key_kinds'])} kiểu)")
    bad = check(led)
    for b in bad:
        print("LẶP:", b)
    print(f"{len(led['videos'])} video · cửa sổ {led.get('window', WINDOW)} · {'ĐẠT' if not bad else f'{len(bad)} chỗ lặp'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
