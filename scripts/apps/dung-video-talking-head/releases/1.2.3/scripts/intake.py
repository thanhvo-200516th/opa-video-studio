"""intake.py — P0: ghép nội dung mp4 HeyGen với mục VIDEO SCRIPT v3
(map_videos, spec §6.1), tách vo_script, và ghi batch_manifest.json +
mapping.csv + APPROVALS.md cho một lô. Chỉ chạy script (opa-operator); không
sửa file video, không ghi vào `VID_ROOT/<n>/`.

Dùng:
    PYTHONIOENCODING=utf-8 python intake.py --batch b01 --videos 16,21,27 \
        --transcriber whisper --preset standard --rules 1.2.3
    PYTHONIOENCODING=utf-8 python intake.py --batch scan --all --allow-all --out <thư mục nháp> \
        --transcriber whisper --preset standard --rules 1.2.3
    PYTHONIOENCODING=utf-8 python intake.py --batch b01 --update --videos 31 \
        --transcriber whisper --preset standard --rules 1.2.3

Lô dựng chọn bằng --videos, tối đa `batch.max_videos` video (C5); video trong
`batch.exclude_videos` (D11: 1–2 đã giao) luôn bị loại. `--all` (mọi video trong
VID_ROOT) chỉ chạy kèm `--allow-all` — quét toàn bộ cho Gate 8/dev, bỏ giới hạn số video.
Lô đã có batch_manifest.json thì chỉ chạy lại với `--update` (C6): ghép lại đúng các video
trong --videos (phải đã có trong lô — video mới vào lô sau), giữ nguyên mục của video khác
trong manifest, mapping.csv, vo_script; APPROVALS.md chỉ viết lại phần đầu (canary, mẫu) —
mục "## Lời duyệt" giữ nguyên từng byte (chỉ operator ghi thêm).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from thlib import mapping, paths, rules, scripts_v3


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="P0: ghép nội dung mp4 với mục VIDEO SCRIPT v3")
    p.add_argument("--batch", required=True, help="Tên lô, vd b01")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--videos", help="Danh sách số video cách nhau bằng dấu phẩy, vd 3,4,5")
    group.add_argument("--all", action="store_true",
                       help="Mọi video tìm thấy trong VID_ROOT — chỉ chạy kèm --allow-all")
    p.add_argument("--allow-all", action="store_true",
                   help="Cho phép --all và bỏ giới hạn batch.max_videos (quét toàn bộ cho Gate 8/dev, "
                        "không phải lô dựng)")
    p.add_argument("--update", action="store_true",
                   help="Lô đã có: chỉ ghép lại các video trong --videos, giữ nguyên video khác và mục "
                        "'## Lời duyệt' của APPROVALS.md")
    p.add_argument("--transcriber", required=True, help="whisper | cache:<đường dẫn csv>")
    p.add_argument("--preset", default="standard")
    p.add_argument("--rules", default="1.2.3")
    p.add_argument(
        "--out",
        help="Ghi đè thư mục lô (mặc định VID_ROOT/_batches/<batch>) — test dùng để không "
        "đụng VID_ROOT thật",
    )
    return p.parse_args(argv)


def _batch_dir(args: argparse.Namespace) -> Path:
    return Path(args.out) if args.out else paths.batch_dir(args.batch)


def _read_cache_csv(csv_path: str) -> dict[int, str]:
    """Đọc `heard` từ một CSV quét trước đó (cùng khuôn với mapping.csv /
    audit/video_v3_mapping.csv, utf-8-sig) — dùng cho test và chạy lại."""
    heard: dict[int, str] = {}
    with open(csv_path, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            heard[int(row["video"].split()[0])] = row["heard"]
    return heard


def _transcribe_whisper(videos: list[dict], clip_s: int) -> dict[int, str]:
    """Whisper large-v3 (int8, beam_size=1, không carry-over) trên
    `clip_s` giây đầu mỗi video, qua ffmpeg -> wav 16 kHz mono tạm."""
    from faster_whisper import WhisperModel  # nặng, chỉ nạp khi thật sự chạy

    model = WhisperModel("large-v3", device="cpu", compute_type="int8")
    heard: dict[int, str] = {}
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "clip.wav"
        for v in videos:
            subprocess.run(
                [
                    "ffmpeg", "-v", "error", "-y", "-i", str(v["source"]),
                    "-t", str(clip_s), "-vn", "-ac", "1", "-ar", "16000", str(wav),
                ],
                check=True,
            )
            segs, _ = model.transcribe(
                str(wav), language="vi", beam_size=1, condition_on_previous_text=False
            )
            heard[v["n"]] = " ".join(s.text.strip() for s in segs)
    return heard


def _sample_flags(batch: str, ok_ns: list[int], sample_every: int,
                  keep: int | None = None) -> tuple[int | None, set[int]]:
    """Canary = `keep` (canary cũ của lô khi --update) nếu còn ok, không thì video `ok` số nhỏ
    nhất; mẫu = 1/`sample_every` video `ok` còn lại, chọn bằng sha256(batch+n) % sample_every == 0
    (D5, xác định lại vẫn ra cùng kết quả — không dùng hash() hay ngẫu nhiên)."""
    ok_sorted = sorted(ok_ns)
    if not ok_sorted:
        return None, set()
    canary = keep if keep in ok_sorted else ok_sorted[0]
    samples = {
        n
        for n in ok_sorted
        if n != canary and int(hashlib.sha256(f"{batch}{n}".encode("utf-8")).hexdigest(), 16) % sample_every == 0
    }
    return canary, samples


MAPPING_FIELDS = ["video", "best_v3", "score", "second_v3", "second_score", "motion_score", "v3_title",
                  "flags", "heard"]
APPROVALS_MARK = "## Lời duyệt"


def _video_label(n: int, loose: bool) -> str:
    return f"{n} (file gốc)" if loose else str(n)


def _select(args: argparse.Namespace, R) -> list[dict] | None:
    """Video của lô (None = lỗi đã in ra stderr): --videos hoặc --all --allow-all, luôn bỏ
    batch.exclude_videos (D11), rồi giới hạn batch.max_videos trừ khi --allow-all (C5)."""
    if args.all and not args.allow_all:
        print("--all chọn mọi video trong VID_ROOT; lô dựng dùng --videos (tối đa batch.max_videos video) — "
              "quét toàn bộ cho Gate 8/dev thì thêm --allow-all", file=sys.stderr)
        return None
    all_videos = mapping.list_videos(paths.VID_ROOT)
    if args.all:
        selected = all_videos
    else:
        wanted = {int(x) for x in args.videos.split(",")}
        by_n = {v["n"]: v for v in all_videos}
        missing = sorted(wanted - by_n.keys())
        if missing:
            print(f"Không tìm thấy video số: {missing}", file=sys.stderr)
            return None
        selected = [by_n[n] for n in sorted(wanted)]
    excluded = set(R.get("batch.exclude_videos"))
    dropped = [v["n"] for v in selected if v["n"] in excluded]
    if dropped:
        print(f"Bỏ video {', '.join(map(str, dropped))} (batch.exclude_videos — D11: đã giao, không dựng lại)")
    selected = [v for v in selected if v["n"] not in excluded]
    cap = R.get("batch.max_videos")
    if not selected:
        print("Không còn video nào để lập lô", file=sys.stderr)
        return None
    if len(selected) > cap and not args.allow_all:
        print(f"Lô chọn {len(selected)} video, vượt batch.max_videos = {cap} — chia thành nhiều lô "
              f"(mỗi lô một --batch)", file=sys.stderr)
        return None
    return selected


def _existing(args: argparse.Namespace, out_dir: Path, R) -> dict | None | bool:
    """Manifest cũ khi --update (None = lô mới); False = lỗi đã in ra stderr (C6)."""
    path = out_dir / "batch_manifest.json"
    if not path.is_file():
        if args.update:
            print(f"--update cần lô đã có: không thấy {path.as_posix()}", file=sys.stderr)
            return False
        return None
    if not args.update:
        print(f"Lô {args.batch} đã có {path.as_posix()} — không ghi đè. Ghép lại video đã render lại: thêm "
              "--update --videos <n,...> (chỉ đổi các video đó, giữ nguyên lời duyệt)", file=sys.stderr)
        return False
    if args.all:
        print("--update chỉ dùng với --videos (chỉ ghép lại các video được nêu)", file=sys.stderr)
        return False
    old = json.loads(path.read_text(encoding="utf-8"))
    if (old.get("preset"), old.get("rules_version")) != (args.preset, R.version):
        print(f"Lô {args.batch} dùng preset {old.get('preset')} / rules {old.get('rules_version')}, lệnh ghi "
              f"--preset {args.preset} --rules {R.version}", file=sys.stderr)
        return False
    return old


def _write_mapping(out_dir: Path, rows: list[dict], update: bool) -> None:
    """mapping.csv: dòng của video vừa ghép; --update giữ nguyên dòng của video khác."""
    path, kept = out_dir / "mapping.csv", {}
    if update and path.is_file():
        with path.open(encoding="utf-8-sig", newline="") as fh:
            kept = {int(row["video"].split()[0]): row for row in csv.DictReader(fh)}
    fresh = {
        r["n"]: {
            "video": _video_label(r["n"], r["loose"]),
            "best_v3": f"{r['v3']:02d}", "score": f"{r['score']:.2f}",
            "second_v3": f"{r['second_v3']:02d}", "second_score": f"{r['second_score']:.2f}",
            "motion_score": f"{r['motion_score']:.2f}", "v3_title": r["v3_title"],
            "flags": "; ".join(r["reasons"]), "heard": r["heard"],
        }
        for r in rows
    }
    merged = {**kept, **fresh}
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MAPPING_FIELDS)
        w.writeheader()
        for n in sorted(merged):
            w.writerow(merged[n])


def _write_approvals(out_dir: Path, batch: str, canary: int | None, samples: set[int], sample_every: int) -> None:
    """APPROVALS.md: phần đầu (canary, mẫu D5) sinh lại; mục "## Lời duyệt" của file có sẵn giữ
    nguyên từng byte — chỉ operator ghi thêm vào đó (C6)."""
    path = out_dir / "APPROVALS.md"
    head = "\n".join([
        f"# APPROVALS — batch {batch}",
        "",
        f"- Canary: video {canary}" if canary is not None else "- Canary: (chưa có video ok)",
        "- Mẫu (1/{}): {}".format(
            sample_every,
            ", ".join(f"video {n}" for n in sorted(samples)) if samples else "(rỗng)",
        ),
        "",
        "",
    ])
    if not path.is_file():
        path.write_text(head + APPROVALS_MARK + "\n(operator chép nguyên văn lời duyệt của user vào đây)\n",
                        encoding="utf-8")
        return
    raw, mark = path.read_bytes(), APPROVALS_MARK.encode("utf-8")
    if mark not in raw:
        print(f"CẢNH BÁO: {path.as_posix()} không có mục '{APPROVALS_MARK}' — để nguyên file, operator báo dev",
              file=sys.stderr)
        return
    nl = "\r\n" if b"\r\n" in raw else "\n"
    path.write_bytes(head.replace("\n", nl).encode("utf-8") + mark + raw.split(mark, 1)[1])


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    R = rules.load(args.rules)
    out_dir = _batch_dir(args)
    old = _existing(args, out_dir, R)
    if old is False:
        return 1
    selected = _select(args, R)
    if selected is None:
        return 1
    in_batch = {v["n"] for v in (old or {}).get("videos", [])}
    new = sorted(s["n"] for s in selected if s["n"] not in in_batch)
    if old and new:                                  # thêm video sẽ dời nhóm PREP-<k> của lô đã duyệt
        print(f"--update chỉ ghép lại video đã có trong lô {args.batch}; video {new} chưa có — đưa vào "
              "một lô sau (--batch mới)", file=sys.stderr)
        return 1
    kept = [v for v in (old or {}).get("videos", []) if v["n"] not in {s["n"] for s in selected}]

    sections = scripts_v3.load_v3(scripts_v3.find_v3_file(paths.DOCS_ROOT))
    director = scripts_v3.load_director(paths.DOCS_ROOT / scripts_v3.DIRECTOR_FILENAME)
    eval_rows = scripts_v3.load_eval(paths.DOCS_ROOT / scripts_v3.EVAL_FILENAME)

    clip_s = R.get("mapping.clip_s")
    if args.transcriber == "whisper":
        heard_by_n = _transcribe_whisper(selected, clip_s)
    elif args.transcriber.startswith("cache:"):
        heard_by_n = _read_cache_csv(args.transcriber.split(":", 1)[1])
    else:
        print(f"--transcriber không hợp lệ: {args.transcriber}", file=sys.stderr)
        return 1

    min_score = R.get("mapping.min_score")
    rows = []
    for v in selected:
        n = v["n"]
        heard = heard_by_n.get(n, "")
        m = mapping.match_clip(heard, sections)
        c = mapping.classify(v, m, sections, R)
        v3 = m["v3"]
        section = sections.get(v3, {})

        director_row = mapping.match_director(section, director)
        eval_row = mapping.match_eval(section, director_row, eval_rows)
        eval_type = next((r["type"] for r in eval_rows if r["row"] == eval_row), None)

        vo_script_rel, vo_sha = None, None
        if m["score"] >= min_score:
            vo_script_rel = f"vo_script/{n}.txt"
            vo_sha = hashlib.sha256(section["script"].encode("utf-8")).hexdigest()

        rows.append(
            {
                "n": n, "source": str(v["source"]), "loose": v["loose"], "heard": heard,
                "v3": v3, "v3_title": section.get("title"), "score": m["score"],
                "second_v3": m["second"], "second_score": m["second_score"],
                "motion_score": m["motion_score"], "status": c["status"], "reasons": c["reasons"],
                "director_row": director_row, "eval_row": eval_row, "eval_type": eval_type,
                "vo_script": vo_script_rel, "vo_script_sha256": vo_sha,
            }
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    fresh = []
    for r in rows:
        if r["vo_script"] is not None:
            vo_dir = out_dir / "vo_script"
            vo_dir.mkdir(parents=True, exist_ok=True)
            text = sections[r["v3"]]["script"]
            (vo_dir / f"{r['n']}.txt").write_text(text, encoding="utf-8")
            (vo_dir / f"{r['n']}.txt.sha256").write_text(r["vo_script_sha256"], encoding="utf-8")
        fresh.append(
            {
                "n": r["n"], "source": r["source"], "v3": r["v3"], "v3_title": r["v3_title"],
                "score": r["score"], "second_score": r["second_score"], "status": r["status"],
                "reasons": r["reasons"], "director_row": r["director_row"],
                "eval_row": r["eval_row"], "eval_type": r["eval_type"],
                "vo_script": r["vo_script"], "vo_script_sha256": r["vo_script_sha256"],
            }
        )
    videos = sorted(kept + fresh, key=lambda v: v["n"])
    sample_every = R.get("batch.sample_every")
    keep = next((v["n"] for v in (old or {}).get("videos", []) if v.get("canary")), None)
    canary, samples = _sample_flags(args.batch, [v["n"] for v in videos if v["status"] == "ok"], sample_every,
                                    keep)
    manifest = {
        "batch": args.batch,
        "rules_version": R.version,
        "preset": args.preset,
        "videos": [{**v, "canary": v["n"] == canary, "sample": v["n"] in samples} for v in videos],
    }
    (out_dir / "batch_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _write_mapping(out_dir, rows, args.update)
    _write_approvals(out_dir, args.batch, canary, samples, sample_every)

    done = f"cập nhật video {', '.join(str(r['n']) for r in rows)} trong" if args.update else "ghi"
    print(f"PASS: đã {done} {out_dir} ({len(videos)} video)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
