#!/usr/bin/env python3
"""QA hình bằng số cho một video (KH §3.10, NC §4.4).

Chạy:  python tools/qa/visual_qa.py <id> [--media <mp4>] [--out <dir>]
Làm:   contact sheet 5×3 (giữa mỗi ô nhịp), still cỡ thật từ media, palette trên mọi still,
       pops trên media (whitelist = cuts của src/audio/cues/<id>.json), độ rộng Bò ở f280 (WARN).
Ghi:   <out>/qa/visual.json, <out>/qa/visual.md, <out>/contact.png, <out>/stills/ (mặc định <out> = out/<id>).
Media mặc định: out/<id>/<id>_9x16.mp4, không có thì out/<id>/video-muted.mp4.
Exit:  0 đạt, 1 palette hoặc pops FAIL, 2 lỗi đầu vào.
"""
import json
import subprocess
import sys
from pathlib import Path

import palette
import pops
import stills

ROOT = Path(__file__).resolve().parents[2]
CELL = 60  # 1 ô nhịp = 60 f (120 BPM, 30 fps)
CONTACT_VF = "select='eq(mod(n\\,60)\\,30)',scale=216:384,tile=5x3"
# Still soát dấu và khoảnh khắc chính của V2 (KH §3.10, TK §1, §10)
EXTRA_FRAMES = (280, 296, 300, 303, 308, 309, 312, 560, 700, 740, 860, 899)
WIDTH_FRAME = 280
WIDTH_ROWS = (600, 1150)
WIDTH_BASE = 960  # bề rộng vùng an toàn 9:16 (1080 − 120)
WIDTH_RANGE = (0.40, 0.60)
WIDTH_MIN_PX = 2  # cột tính là có Bò khi ≥ 2 điểm blue


def make_contact(media: Path, out_png: Path) -> None:
    """Contact sheet 5×3 ô 216×384 (1080×1152)."""
    out_png.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(media), "-vf", CONTACT_VF,
           "-frames:v", "1", "-fps_mode", "vfr", str(out_png)]
    proc = subprocess.run(cmd, capture_output=True, check=False)
    if proc.returncode != 0 or not out_png.is_file():
        raise RuntimeError(f"contact sheet lỗi: {proc.stderr.decode('utf-8', 'replace')[-400:]}")


def still_frames(n_frames: int) -> list[int]:
    mids = [k * CELL + CELL // 2 for k in range(n_frames // CELL)]
    return sorted({f for f in (*mids, *EXTRA_FRAMES) if f < n_frames})


def mascot_width(png: Path) -> dict | None:
    """Số cột có #0068FF trong y 600–1150, so với 960."""
    rgb = palette.load_rgb(png)
    y0, y1 = WIDTH_ROWS
    if rgb.shape[0] < y1:
        return None
    blue = palette.token_mask(rgb[y0:y1], ["blue"])
    cols = int((blue.sum(axis=0) >= WIDTH_MIN_PX).sum())
    ratio = cols / WIDTH_BASE
    ok = WIDTH_RANGE[0] <= ratio <= WIDTH_RANGE[1]
    return {"frame": WIDTH_FRAME, "cols": cols, "ratio": round(ratio, 3), "level": "PASS" if ok else "WARN"}


def resolve_media(comp_id: str, given: str | None) -> Path | None:
    if given:
        p = Path(given)
        return p if p.is_file() else None
    base = ROOT / "out" / comp_id
    for p in (base / f"{comp_id}_9x16.mp4", base / "video-muted.mp4"):
        if p.is_file():
            return p
    return None


def run(comp_id: str, media: Path, out: Path) -> dict:
    """Chạy toàn bộ QA; trả về báo cáo (dict)."""
    cues = ROOT / "src/audio/cues" / f"{comp_id}.json"
    notes = []
    gray = pops.decode_gray(media)
    if cues.is_file():
        cuts = pops.load_cuts(cues)
    else:
        cuts = []
        notes.append(f"thiếu {cues.relative_to(ROOT)}: pops chạy không whitelist")
    pop_res = pops.analyze(gray, cuts)
    contact = out / "contact.png"
    make_contact(media, contact)
    frames = still_frames(len(gray))
    paths = stills.extract_mp4(media, frames, out / "stills")
    pal = [{"frame": f, **palette.check_file(p)} for f, p in zip(frames, paths)]
    width = mascot_width(out / "stills" / stills.still_name(WIDTH_FRAME)) if WIDTH_FRAME in frames else None
    pal_pass = all(r["pass"] for r in pal)
    return {
        "id": comp_id,
        "media": str(media),
        "frames": len(gray),
        "contact": str(contact),
        "pass": pal_pass and not pop_res["fails"],
        "palette_pass": pal_pass,
        "palette": pal,
        "pops": pop_res,
        "mascot_width": width,
        "cuts": cuts,
        "notes": notes,
    }


def to_markdown(rep: dict) -> str:
    lines = [f"# QA hình: {rep['id']}", "",
             f"- Media: `{rep['media']}` ({rep['frames']} frame)",
             f"- Kết quả: **{'ĐẠT' if rep['pass'] else 'CHƯA ĐẠT'}** (palette {'PASS' if rep['palette_pass'] else 'FAIL'},"
             f" pops {len(rep['pops']['fails'])} FAIL / {len(rep['pops']['warns'])} WARN)",
             f"- Contact sheet: `{rep['contact']}`"]
    w = rep["mascot_width"]
    if w:
        lines.append(f"- Độ rộng Bò f{w['frame']}: {w['cols']} cột = {w['ratio']:.0%} của {WIDTH_BASE} ({w['level']})")
    lines += [f"- Ghi chú: {n}" for n in rep["notes"]]
    lines += ["", "## Palette", "", "| Frame | Kết quả | Phẳng | Xám | Ghi chú |", "|---|---|---|---|---|"]
    for r in rep["palette"]:
        lines.append(f"| f{r['frame']} | {'PASS' if r['pass'] else 'FAIL'} | {r['flat_share']:.1%} | "
                     f"{r['gray_share']:.2%} | {'; '.join(r['reasons'])} |")
    lines += ["", "## Pops", ""]
    items = [("FAIL", i) for i in rep["pops"]["fails"]] + [("WARN", i) for i in rep["pops"]["warns"]]
    lines += [f"- {lvl} {pops.describe(i)}" for lvl, i in items] or ["- Không có"]
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> tuple[str, str | None, str | None]:
    comp_id, media, out = None, None, None
    i = 0
    while i < len(argv):
        arg = argv[i]
        key, _, val = arg.partition("=")
        if key in ("--media", "--out"):
            if not val:
                i += 1
                val = argv[i] if i < len(argv) else ""
            if not val:
                raise ValueError(f"{key} thiếu giá trị")
            media, out = (val, out) if key == "--media" else (media, val)
        elif comp_id is None and not arg.startswith("--"):
            comp_id = arg
        else:
            raise ValueError(f"tham số lạ: {arg}")
        i += 1
    if not comp_id:
        raise ValueError("thiếu <id>")
    return comp_id, media, out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        comp_id, media_arg, out_arg = parse_args(sys.argv[1:])
    except ValueError as e:
        print(f"LỖI: {e}\n{__doc__}", file=sys.stderr)
        return 2
    media = resolve_media(comp_id, media_arg)
    if media is None:
        print(f"Thiếu media cho {comp_id} (--media hoặc out/{comp_id}/{comp_id}_9x16.mp4)", file=sys.stderr)
        return 2
    out = Path(out_arg) if out_arg else ROOT / "out" / comp_id
    try:
        rep = run(comp_id, media, out)
    except RuntimeError as e:
        print(f"LỖI: {e}", file=sys.stderr)
        return 2
    qa_dir = out / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    (qa_dir / "visual.json").write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    (qa_dir / "visual.md").write_text(to_markdown(rep), encoding="utf-8")
    for r in rep["palette"]:
        print(f"{'PASS' if r['pass'] else 'FAIL'} palette f{r['frame']} {'; '.join(r['reasons'])}")
    for item in rep["pops"]["fails"]:
        print(f"FAIL pops {pops.describe(item)}")
    for item in rep["pops"]["warns"]:
        print(f"WARN pops {pops.describe(item)}")
    if rep["mascot_width"]:
        w = rep["mascot_width"]
        print(f"{w['level']} độ rộng Bò f{w['frame']} {w['ratio']:.0%}")
    fails = sum(1 for r in rep["palette"] if not r["pass"]) + len(rep["pops"]["fails"])
    print(f"TỔNG: {fails} FAIL — báo cáo {qa_dir / 'visual.md'}")
    return 0 if rep["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
