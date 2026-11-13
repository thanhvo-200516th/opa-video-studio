# -*- coding: utf-8 -*-
"""scripts/import_bgm.py — Nhập 1 bài nhạc nền (S29, §5.6): đổi sang WAV
48 kHz stereo tại releases/<ver>/bgm/<id>.wav, đo integrated LUFS (BS.1770
nhiều kênh, R10), ghi/cập nhật bgm_manifest.json.

Điểm loop (`loop_s`) = cuối vùng nhạc chính: khối momentary 400 ms cuối cùng
còn ≥ integrated − 10 LU (gate tương đối BS.1770) — bỏ đoạn outro nhỏ dần và
đuôi im để mix.bgm_bed lặp không rơi vào khoảng lặng. WAV lưu đã cắt tại điểm
loop, nên bgm_bed lặp ở cuối mảng chính là lặp tại điểm loop.

`content_id_risk` là "none" chỉ khi truyền --content-id-none (người nhập đã
kiểm), ngược lại "unknown" và mix.select_bgm bỏ qua bài đó.

Chạy: PYTHONIOENCODING=utf-8 python releases/1.1.1/scripts/import_bgm.py --rules 1.1.1 \
    --add <file> --id <id> --url <source_url> --license "<license>" \
    [--content-id-none] [--select --order k]
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
from pathlib import Path

import numpy as np

from thlib import audio, paths

_ID_RE = re.compile(r"[a-z0-9][a-z0-9-]*")
# Gate tương đối BS.1770: khối thấp hơn integrated quá 10 LU không tính là nội dung.
_REL_GATE_LU = 10.0


def _loop_end(x: np.ndarray) -> int:
    """Điểm loop (số mẫu) của bài [n, 2]: hết khối momentary cuối còn ≥
    integrated − 10 LU (đo trên bản hạ mono, chỉ so tương đối nên đủ)."""
    mono = x.mean(axis=1)
    loud = np.where(audio.momentary(mono) >= audio.integrated_lufs(mono) - _REL_GATE_LU)[0]
    if len(loud) == 0:
        raise SystemExit("Từ chối: bài nguồn im lặng, không có vùng nhạc để lặp")
    return int(loud[-1]) + 1


def _read_manifest(path: Path) -> dict:
    """bgm_manifest.json hiện có, hoặc manifest rỗng nếu chưa có."""
    if not path.exists():
        return {"tracks": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def add_track(rel: Path, src: Path, track_id: str, url: str, license_name: str,
              content_id_none: bool, select: bool, order: int | None) -> dict:
    """Nhập `src` vào release `rel` dưới khoá `track_id`, ghi WAV + cập nhật
    bgm_manifest.json (thay entry cùng id nếu đã có). Trả entry đã ghi.
    Từ chối (SystemExit) id sai dạng, URL nguồn không phải https, license
    rỗng, --select thiếu --order, file nguồn không có, md5 trùng bài khác."""
    if not _ID_RE.fullmatch(track_id):
        raise SystemExit(f"Từ chối: id '{track_id}' chỉ được gồm a-z, 0-9, '-'")
    if not url.startswith("https://"):
        raise SystemExit(f"Từ chối {track_id}: source_url phải là URL https, nhận '{url}'")
    if not license_name.strip():
        raise SystemExit(f"Từ chối {track_id}: thiếu license")
    if select and order is None:
        raise SystemExit(f"Từ chối {track_id}: --select cần kèm --order")
    if not Path(src).exists():
        raise SystemExit(f"Từ chối {track_id}: không tìm thấy file nguồn {src}")

    x = audio.decode(src)
    y = x[: _loop_end(x)]
    out_path = rel / "bgm" / f"{track_id}.wav"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    part = out_path.with_name(out_path.name + ".part")   # chỉ thay WAV cũ khi nhập thành công
    audio.write_wav(part, y)
    md5 = hashlib.md5(part.read_bytes()).hexdigest()

    manifest_path = rel / "bgm_manifest.json"
    tracks = _read_manifest(manifest_path)["tracks"]
    twin = next((k for k, t in tracks.items() if t["md5"] == md5 and k != track_id), None)
    if twin:
        part.unlink()
        raise SystemExit(f"Từ chối {track_id}: md5 trùng bài '{twin}' đã có trong manifest")
    part.replace(out_path)

    entry = {
        "path": f"bgm/{track_id}.wav",
        "md5": md5,
        "source_url": url,
        "license": license_name,
        "license_checked_at": datetime.date.today().isoformat(),
        "content_id_risk": "none" if content_id_none else "unknown",
        "lufs": round(audio.integrated_lufs(y), 2),
        "loop_s": round(len(y) / audio.SR, 4),
        "selected": select,
        "order": order if select else None,
    }
    merged = {**tracks, track_id: entry}
    manifest_path.write_text(
        json.dumps({"tracks": {k: merged[k] for k in sorted(merged)}}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    if select and not content_id_none:
        print(f"CẢNH BÁO: {track_id} được chọn nhưng content_id_risk=unknown -> select_bgm sẽ bỏ qua")
    print(f"Đã nhập {track_id}: {entry['lufs']} LUFS, loop tại {entry['loop_s']} s -> {out_path}")
    return entry


def main() -> None:
    ap = argparse.ArgumentParser(description="Nhập 1 bài nhạc nền + đo + ghi bgm_manifest.json")
    ap.add_argument("--rules", required=True, help="Phiên bản bộ luật, ví dụ 1.1.1")
    ap.add_argument("--add", required=True, type=Path, help="File nhạc nguồn (mp3/wav/...)")
    ap.add_argument("--id", required=True, help="Khoá bài trong manifest, ví dụ cat-walk")
    ap.add_argument("--url", required=True, help="URL nguồn của bài (https)")
    ap.add_argument("--license", required=True, help="Tên giấy phép, ví dụ Mixkit Stock Music Free License")
    ap.add_argument("--content-id-none", action="store_true",
                    help="Đã kiểm: bài không dính Content ID (bắt buộc để select_bgm dùng bài)")
    ap.add_argument("--select", action="store_true", help="User đã chọn bài này (BGM-SELECT)")
    ap.add_argument("--order", type=int, help="Thứ tự xoay vòng của bài đã chọn")
    args = ap.parse_args()
    rel = paths.release_dir(args.rules)
    if not rel.is_dir():
        raise SystemExit(f"Không có release {args.rules} tại {rel}")
    add_track(rel, args.add, args.id, args.url, args.license, args.content_id_none,
              args.select, args.order)


if __name__ == "__main__":
    main()
