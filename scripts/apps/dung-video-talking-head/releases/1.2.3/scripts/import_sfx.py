# -*- coding: utf-8 -*-
"""scripts/import_sfx.py — Nhập 11 file SFX đã cấp phép (Mixkit), đo hình
bao/dải tần rồi ghi releases/<ver>/sfx/<family>/<name>.wav + sfx_manifest.json.

Nguồn: `pack:` = SKILL/legacy/1.0.0/assets/sfx/<orig> (pack 1.0.0, R3; legacy/ theo R36);
`lib:` = SFX_LIB/sfx/<orig> (video-shotcraft, chỉ đọc). `source_url` lấy từ
dòng chứa tên file trong ATTRIBUTION.md tương ứng (URL .mp3 đầu tiên trên dòng
đó). Từ chối file thiếu source_url, hoặc trùng md5 (đã chuẩn hoá WAV) với bất kỳ
file nào khác của release, dù khác family (S13 1.1.1: md5 duy nhất toàn release).

Chạy: PYTHONIOENCODING=utf-8 python releases/1.1.1/scripts/import_sfx.py --rules 1.1.1
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from thlib import audio, paths, rules, sfxlib

LICENSE = "Mixkit SFX Free License"
LICENSE_CHECKED_AT = "2026-09-11"

# manifest key -> (origin, đường dẫn gốc dưới sfx/ của kho tương ứng)
MAPPING: dict[str, tuple[str, str]] = {
    "impact/hit-blow": ("pack", "impact/hit-blow.mp3"),
    "impact/hit-weak": ("lib", "impact/hit-weak.mp3"),
    "sparkle/sparkle-wand": ("lib", "light/sparkle-wand.mp3"),
    "sparkle/sparkle-touch": ("pack", "light/sparkle-touch.mp3"),
    "slide/paper-slice-quick": ("lib", "paper/paper-slice-quick.mp3"),
    "slide/glass-plate-slide": ("lib", "glass/glass-plate-slide.mp3"),
    "whoosh/transition-soft": ("lib", "transition/transition-soft.mp3"),
    "whoosh/wind-swoosh-short": ("lib", "transition/wind-swoosh-short.mp3"),
    # Q2 (user 2026-09-15): whoosh thứ ba, Mixkit 2627 (ATTRIBUTION dòng 65).
    "whoosh/zoom-swipe-fast": ("lib", "camera/zoom-swipe-fast.mp3"),
    "air/sweep-short": ("pack", "transition/sweep-short.mp3"),
    # transition-snap (74 % > 4 kHz) chỉ còn ở air — 1.1.1 gỡ bản trùng md5 ở whoosh.
    "air/transition-snap": ("lib", "transition/transition-snap.mp3"),
}

_URL_RE = re.compile(r"https://\S+?\.mp3")


def _find_source_url(attribution_path: Path, basename: str) -> str | None:
    """Tìm dòng trong ATTRIBUTION.md chứa `basename` -> lấy URL .mp3 đầu tiên."""
    text = attribution_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if basename in line:
            m = _URL_RE.search(line)
            if m:
                return m.group(0)
    return None


def import_sfx(ver: str) -> dict:
    """Nhập toàn bộ MAPPING theo bộ luật `ver`, ghi WAV + sfx_manifest.json,
    trả về manifest dict đã ghi."""
    R = rules.load(ver)
    rel = paths.release_dir(ver)
    pack = paths.SKILL / "legacy" / "1.0.0" / "assets"
    pack_attribution = pack / "ATTRIBUTION.md"
    lib_attribution = paths.SFX_LIB / "ATTRIBUTION.md"

    files: dict[str, dict] = {}
    seen: dict[str, str] = {}   # md5 -> khoá manifest, trên cả release

    for key, (origin, orig) in MAPPING.items():
        family, name = key.split("/")
        if origin == "pack":
            src = pack / "sfx" / orig
            attribution = pack_attribution
        else:
            src = paths.SFX_LIB / "sfx" / orig
            attribution = lib_attribution

        if not src.exists():
            raise SystemExit(f"Từ chối {key}: không tìm thấy file nguồn {src}")

        basename = Path(orig).name
        source_url = _find_source_url(attribution, basename)
        if not source_url:
            raise SystemExit(
                f"Từ chối {key}: không tìm thấy source_url cho '{basename}' trong {attribution}"
            )

        y = sfxlib.prepare(src)
        meta = sfxlib.measure(y)

        out_path = rel / "sfx" / family / f"{name}.wav"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        audio.write_wav(out_path, y)
        md5 = hashlib.md5(out_path.read_bytes()).hexdigest()

        if md5 in seen:
            raise SystemExit(
                f"Từ chối {key}: md5 trùng '{seen[md5]}' (md5 phải duy nhất trên cả release)"
            )
        seen[md5] = key

        entry = {
            "path": f"sfx/{family}/{name}.wav",
            "md5": md5,
            "origin": origin,
            "source_url": source_url,
            "license": LICENSE,
            "license_checked_at": LICENSE_CHECKED_AT,
            **meta,
        }

        ok, why = sfxlib.role_ok(entry, family, R)
        if not ok:
            print(f"CẢNH BÁO: {key} không đạt family_constraints['{family}']: {why}")

        files[key] = entry

    manifest = {"files": files}
    manifest_path = rel / "sfx_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Đã nhập {len(files)} file SFX -> {manifest_path}")
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser(description="Nhập SFX đã cấp phép + đo + ghi sfx_manifest.json")
    ap.add_argument("--rules", required=True, help="Phiên bản bộ luật, ví dụ 1.1.1")
    args = ap.parse_args()
    import_sfx(args.rules)


if __name__ == "__main__":
    main()
