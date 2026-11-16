#!/usr/bin/env python3
"""CLI tool for training, measuring, iterating, and linting video editing skills.

Subcommands:
    probe       Measure video(s) via ffprobe, scdet, ebur128 and generate contact sheets.
    scaffold    Generate a new portable video-editing skill from a preset or profile.
    feedback    Log round feedback (optional screenshot) and persist config overrides.
    lint-skill  Validate structure, ease-in-out, face_safe_zone, nested SKILL.md, and portability.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

SKILL_ROOT = Path(__file__).resolve().parent.parent
PRESETS_DIR = SKILL_ROOT / "references" / "presets"
TEMPLATES_DIR = SKILL_ROOT / "templates"

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}
TEXT_SCAN_EXTS = {".md", ".json", ".html", ".css", ".js", ".ts", ".tsx", ".jsx", ".txt", ".yaml", ".yml"}

# Portability regexes: catch Windows drive paths (e.g. D:\Kho_SFX, C:/Users), UNC paths, and personal Unix homes
PORTABILITY_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("windows_drive_path", re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:(?:\\\\|\\|/)")),
    ("personal_home_path", re.compile(r"(?:/Users/|/home/)[A-Za-z0-9_.-]+")),
    ("unc_network_path", re.compile(r"(?:^|[\s\"'])\\\\[A-Za-z0-9_.-]+\\")),
]


def _run_cmd(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def _load_font(size: int) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    ]
    for path in candidates:
        if Path(path).is_file():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _parse_fps(rate_str: str | None) -> float:
    if not rate_str or rate_str == "0/0":
        return 0.0
    if "/" in rate_str:
        num, den = rate_str.split("/", 1)
        try:
            d = float(den)
            return round(float(num) / d, 3) if d else 0.0
        except ValueError:
            return 0.0
    try:
        return round(float(rate_str), 3)
    except ValueError:
        return 0.0


def _classify_orientation(w: int, h: int) -> tuple[str, str]:
    if w <= 0 or h <= 0:
        return "unknown", "unknown"
    ratio = w / h
    if abs(ratio - (9 / 16)) < 0.08:
        return "9:16", "vertical"
    if abs(ratio - (16 / 9)) < 0.08:
        return "16:9", "horizontal"
    if abs(ratio - 1.0) < 0.08:
        return "1:1", "square"
    g = math.gcd(w, h)
    return f"{w // g}:{h // g}", "vertical" if h > w else "horizontal"


def _probe_single_video(
    video_path: Path,
    out_dir: Path,
    fps: float,
    make_sheets: bool,
    scdet_threshold: float,
) -> dict[str, Any]:
    ffprobe_res = _run_cmd(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(video_path),
        ]
    )
    if ffprobe_res.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {video_path}: {ffprobe_res.stderr.strip()}")

    meta = json.loads(ffprobe_res.stdout or "{}")
    streams = meta.get("streams", [])
    fmt = meta.get("format", {})

    v_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    a_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if v_stream is None:
        raise RuntimeError(f"No video stream found in {video_path}")

    width = int(v_stream.get("width", 0))
    height = int(v_stream.get("height", 0))
    duration = float(fmt.get("duration") or v_stream.get("duration") or 0.0)
    video_fps = _parse_fps(v_stream.get("avg_frame_rate") or v_stream.get("r_frame_rate"))
    aspect_ratio, orientation = _classify_orientation(width, height)

    # Scene change detection via ffmpeg scdet
    scdet_res = _run_cmd(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-i",
            str(video_path),
            "-vf",
            f"scdet=threshold={scdet_threshold}",
            "-f",
            "null",
            "-",
        ]
    )
    cut_times: list[float] = []
    for line in scdet_res.stderr.splitlines():
        if "lavfi.scd.time:" in line:
            m = re.search(r"lavfi\.scd\.time:\s*([0-9]+(?:\.[0-9]+)?)", line)
            if m:
                t = round(float(m.group(1)), 3)
                if 0.05 < t < max(0.0, duration - 0.05):
                    if not cut_times or (t - cut_times[-1]) >= 0.25:
                        cut_times.append(t)

    # Compute shot durations
    boundaries = [0.0, *cut_times, round(duration, 3)]
    shots = [round(boundaries[i + 1] - boundaries[i], 3) for i in range(len(boundaries) - 1) if boundaries[i + 1] > boundaries[i]]
    median_shot = round(statistics.median(shots), 3) if shots else round(duration, 3)
    cuts_per_10s = round((len(cut_times) / duration) * 10.0, 2) if duration > 0 else 0.0

    # Loudness measurement via ebur128
    audio_info: dict[str, Any] = {"has_audio": a_stream is not None}
    if a_stream is not None:
        audio_info["codec"] = a_stream.get("codec_name")
        audio_info["sample_rate"] = int(a_stream.get("sample_rate") or 0)
        audio_info["channels"] = int(a_stream.get("channels") or 0)
        ebur_res = _run_cmd(
            [
                "ffmpeg",
                "-hide_banner",
                "-nostdin",
                "-i",
                str(video_path),
                "-vn",
                "-af",
                "ebur128=peak=true",
                "-f",
                "null",
                "-",
            ]
        )
        err = ebur_res.stderr
        summary = err[err.rfind("Summary:") :] if "Summary:" in err else err
        for key, out_key in [("I", "integrated_lufs"), ("LRA", "lra_lu"), ("Peak", "true_peak_dbfs")]:
            m = re.search(rf"{key}:\s+(-?[\d.]+|-inf)", summary)
            if m:
                val = m.group(1)
                audio_info[out_key] = None if "inf" in val else float(val)

    sheet_path: Path | None = None
    frame_count = 0
    if make_sheets and duration > 0:
        sheet_path, frame_count = _build_contact_sheet(
            video_path=video_path,
            out_dir=out_dir,
            fps=fps,
            duration=duration,
            width=width,
            height=height,
            cuts_per_10s=cuts_per_10s,
            lufs=audio_info.get("integrated_lufs"),
        )

    return {
        "file_name": video_path.name,
        "duration_sec": round(duration, 3),
        "width": width,
        "height": height,
        "aspect_ratio": aspect_ratio,
        "orientation": orientation,
        "fps": video_fps,
        "video_codec": v_stream.get("codec_name"),
        "pacing": {
            "cut_count": len(cut_times),
            "cut_timestamps_sec": cut_times,
            "cuts_per_10s": cuts_per_10s,
            "median_shot_sec": median_shot,
            "max_shot_sec": max(shots) if shots else round(duration, 3),
            "shot_count": len(shots),
        },
        "audio": audio_info,
        "contact_sheet": sheet_path.name if sheet_path else None,
        "contact_sheet_frames": frame_count,
    }


def _build_contact_sheet(
    video_path: Path,
    out_dir: Path,
    fps: float,
    duration: float,
    width: int,
    height: int,
    cuts_per_10s: float,
    lufs: float | None,
) -> tuple[Path, int]:
    max_frames = 36
    effective_fps = fps if duration * fps <= max_frames else max(0.1, max_frames / duration)
    with tempfile.TemporaryDirectory(prefix="vst_frames_") as tmp:
        tmp_dir = Path(tmp)
        pattern = str(tmp_dir / "frame_%04d.png")
        res = _run_cmd(
            [
                "ffmpeg",
                "-hide_banner",
                "-nostdin",
                "-y",
                "-i",
                str(video_path),
                "-vf",
                f"fps={effective_fps:.4f}",
                "-frames:v",
                str(max_frames),
                pattern,
            ]
        )
        if res.returncode != 0:
            raise RuntimeError(f"ffmpeg frame extraction failed: {res.stderr.strip()}")
        frames = sorted(tmp_dir.glob("frame_*.png"))
        if not frames:
            raise RuntimeError(f"No frames extracted from {video_path}")

        cols = 6 if len(frames) >= 6 else len(frames)
        rows = math.ceil(len(frames) / cols)
        thumb_w = 220
        thumb_h = max(124, min(390, round(thumb_w * (height / width)))) if width > 0 and height > 0 else 220
        label_h = 28
        header_h = 44

        canvas = Image.new("RGB", (cols * thumb_w, header_h + rows * (thumb_h + label_h)), (16, 20, 28))
        draw = ImageDraw.Draw(canvas)
        head_font = _load_font(18)
        small_font = _load_font(14)

        lufs_str = f"{lufs:.1f} LUFS" if lufs is not None else "no-audio"
        header = f"{video_path.name} | {width}x{height} | {duration:.1f}s | {cuts_per_10s:.1f} cuts/10s | {lufs_str}"
        draw.text((12, 12), header[:120], font=head_font, fill=(248, 250, 252))

        for idx, frame_file in enumerate(frames):
            col = idx % cols
            row = idx // cols
            x = col * thumb_w
            y = header_h + row * (thumb_h + label_h)
            with Image.open(frame_file) as im:
                resized = im.convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                canvas.paste(resized, (x, y))
            ts = idx / effective_fps
            draw.text((x + 8, y + thumb_h + 6), f"t={ts:.2f}s", font=small_font, fill=(250, 204, 21))

        out_path = out_dir / f"{video_path.stem}_contact_sheet.jpg"
        canvas.save(out_path, quality=88)
        return out_path, len(frames)


def cmd_probe(args: argparse.Namespace) -> int:
    target = Path(args.input).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve()
    if not target.exists():
        print(f"[ERROR] Input not found: {target}", file=sys.stderr)
        return 1

    if target.is_file():
        videos = [target]
    else:
        videos = sorted(p for p in target.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXTS)

    if not videos:
        print(f"[ERROR] No supported video files found in: {target}", file=sys.stderr)
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)
    results = [
        _probe_single_video(
            video_path=v,
            out_dir=out_dir,
            fps=args.fps,
            make_sheets=not args.no_sheets,
            scdet_threshold=args.scdet_threshold,
        )
        for v in videos
    ]

    sample_strategy = "exact_clone_1_video" if len(results) == 1 else "common_pattern_multi_video"
    avg_cuts_10s = round(statistics.mean(r["pacing"]["cuts_per_10s"] for r in results), 2)
    avg_median_shot = round(statistics.mean(r["pacing"]["median_shot_sec"] for r in results), 3)
    lufs_vals = [r["audio"]["integrated_lufs"] for r in results if r["audio"].get("integrated_lufs") is not None]
    avg_lufs = round(statistics.mean(lufs_vals), 2) if lufs_vals else None

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sample_count": len(results),
        "sample_strategy": sample_strategy,
        "aggregate": {
            "avg_cuts_per_10s": avg_cuts_10s,
            "avg_median_shot_sec": avg_median_shot,
            "avg_integrated_lufs": avg_lufs,
            "primary_resolution": [results[0]["width"], results[0]["height"]],
            "primary_aspect_ratio": results[0]["aspect_ratio"],
        },
        "videos": results,
    }

    report_path = out_dir / "probe_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    summary_lines = [
        "# Video Sample Probe Summary",
        "",
        f"- **Sample count:** {len(results)} (`{sample_strategy}`)",
        f"- **Avg cuts / 10s:** {avg_cuts_10s}",
        f"- **Avg median shot:** {avg_median_shot}s",
        f"- **Avg integrated loudness:** {f'{avg_lufs} LUFS' if avg_lufs is not None else 'N/A'}",
        "",
        "## Per-video measurements",
        "",
        "| File | Resolution | Aspect | Duration | Cuts | Cuts/10s | Median Shot | Integrated LUFS | Contact Sheet |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        lufs_cell = f"{r['audio']['integrated_lufs']:.1f}" if r["audio"].get("integrated_lufs") is not None else "N/A"
        sheet_cell = r["contact_sheet"] or "none"
        summary_lines.append(
            f"| {r['file_name']} | {r['width']}x{r['height']} | {r['aspect_ratio']} | "
            f"{r['duration_sec']:.2f}s | {r['pacing']['cut_count']} | {r['pacing']['cuts_per_10s']:.2f} | "
            f"{r['pacing']['median_shot_sec']:.2f}s | {lufs_cell} | {sheet_cell} |"
        )
    summary_lines.extend(
        [
            "",
            "## 9-Axis Visual Inspection Checklist (AI + Contact Sheet)",
            "",
            "1. **Nhịp dựng:** Đối chiếu `cuts/10s` và vị trí đổi UI/zoom trên contact sheet.",
            "2. **Typography:** Font family, word-by-word timing, màu highlight từ khoá, cỡ chữ đọc khi tắt tiếng.",
            "3. **Animation Text:** Đường cong `ease-in-out` (cấm `linear`), kiểm tra tốc độ đọc (`text_speed_scale`).",
            "4. **Fake Camera:** Zoom in/out mượt trong 10 giây đầu.",
            "5. **Motion Graphics & UI Elements:** Icon, glass card, orbit nodes — xác nhận không đè mặt.",
            "6. **Face-Safe Zone:** Khung vùng mặt người nói (`x_range`, `y_range`).",
            "7. **Transitions:** Flash cam / wipe / punch zoom tại điểm cắt.",
            "8. **Audio & SFX:** Nhạc dưới giọng (-17..-22 LU), SFX nhấn theo nhịp UI.",
            "9. **Portability:** Toàn bộ tài nguyên đóng gói tương đối trong `assets/` và `templates/`.",
            "",
        ]
    )
    (out_dir / "probe_summary.md").write_text("\n".join(summary_lines), encoding="utf-8")

    print(json.dumps({"status": "ok", "report": str(report_path), "sample_count": len(results)}, ensure_ascii=False))
    return 0


def _slugify_skill_name(raw: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", raw.strip().lower()).strip("-_")
    if not slug:
        raise ValueError(f"Invalid skill name: {raw!r}")
    return slug


def _build_scaffold_skill_md(skill_name: str, cfg: dict[str, Any]) -> str:
    engine = cfg.get("engine", "hyperframes")
    easing = cfg.get("motion", {}).get("easing", cfg.get("easing", "ease-in-out"))
    speed_scale = cfg.get("motion", {}).get("text_speed_scale", cfg.get("text_speed_scale", 1.2))
    hook_sec = cfg.get("hook", {}).get("hook_window_sec", cfg.get("hook_window_sec", 10))
    fsz = cfg.get("face_safe_zone", {})
    return f"""---
name: {skill_name}
description: Skill dựng video tự động theo style đã train ({engine}) — 1-Prompt Production với kinetic typography, ease-in-out, fake camera 10s đầu và bảo vệ face-safe zone.
---

# {skill_name}

Skill này được sinh tự động bởi `video-style-trainer`. Mọi thông số dựng nằm tập trung trong `config.json` (tương đối, portable 100%).

## 1-Prompt Production Workflow

Khi người dùng gửi video thô kèm 1 câu lệnh ngắn:
1. Đọc toàn bộ thông số từ `config.json` và `references/style-spec.md`.
2. Render/dựng trên engine **`{engine}`** theo template trong `templates/`.
3. Tuân thủ tuyệt đối các ràng buộc sau (không cần người dùng nhắc lại):
   - **Easing:** Bắt buộc `{easing}` cho mọi keyframe chữ, UI element và fake camera (**cấm `linear`**).
   - **Tốc độ chữ (`text_speed_scale`):** `{speed_scale}` — đủ chậm để người xem đọc kịp trên điện thoại khi **tắt tiếng (Chữ = Âm thanh)**.
   - **Hook {hook_sec} giây đầu:** Bật `fake_camera` zoom in/out mượt theo `ease-in-out` để giữ chân người xem.
   - **Face-Safe Zone:** `x_range={fsz.get("x_range", [0.22, 0.78])}`, `y_range={fsz.get("y_range", [0.16, 0.56])}` — tuyệt đối không đặt chữ hoặc UI card đè lên khuôn mặt.
   - **Portability:** Chỉ dùng tài nguyên tương đối trong `assets/` và `templates/`.

## Cấu trúc nội bộ

- `config.json` — Nguồn chân lý duy nhất cho mọi tham số dựng (tự động cập nhật sau mỗi round feedback).
- `references/style-spec.md` — Đặc tả 9 trục kỹ thuật của style.
- `references/feedback-log.md` — Nhật ký các vòng hiệu chỉnh & screenshot tham chiếu.
- `templates/` — Template dựng cho `{engine}`.
- `assets/` — Fonts & SFX đóng gói kèm skill.
"""


def _build_style_spec_md(skill_name: str, cfg: dict[str, Any], probe_data: dict[str, Any] | None) -> str:
    lines = [
        f"# Style Specification — {skill_name}",
        "",
        f"- **Engine:** `{cfg.get('engine', 'hyperframes')}`",
        f"- **Resolution:** `{cfg.get('resolution', [1080, 1920])}` (`{cfg.get('aspect_ratio', '9:16')}`)",
        f"- **Easing:** `{cfg.get('motion', {}).get('easing', 'ease-in-out')}` (forbid linear: `{cfg.get('motion', {}).get('forbid_linear', True)}`)",
        f"- **Text Speed Scale:** `{cfg.get('motion', {}).get('text_speed_scale', 1.2)}`",
        f"- **Hook Window:** `{cfg.get('hook', {}).get('hook_window_sec', 10)}s` (`fake_camera={cfg.get('hook', {}).get('fake_camera', True)}`)",
        f"- **Face-Safe Zone:** `x={cfg.get('face_safe_zone', {}).get('x_range')}`, `y={cfg.get('face_safe_zone', {}).get('y_range')}`",
        "",
        "## 9 Trục kỹ thuật cốt lõi",
        "",
        "1. Nhịp dựng (Pacing & Cuts/10s)",
        "2. Typography (Word-by-word + Keyword Highlight + Mobile-Mute Readability)",
        "3. Animation Text (`ease-in-out`, `text_speed_scale`)",
        "4. Fake Camera (Zoom in/out trong 10 giây đầu)",
        "5. Motion Graphics & UI Elements (Icon, Glass Card, Orbit Nodes)",
        "6. Face-Safe Zone (Không đè khuôn mặt người nói)",
        "7. Transitions (Flash cam, Wipe, Punch zoom)",
        "8. Audio & SFX (BGM -17..-22 LU dưới giọng, SFX nhấn nhịp UI)",
        "9. Portable Packaging (Đường dẫn tương đối 100%)",
        "",
    ]
    if probe_data:
        agg = probe_data.get("aggregate", {})
        lines.extend(
            [
                "## Số đo baseline từ video mẫu",
                "",
                f"- Sample count: `{probe_data.get('sample_count')}` (`{probe_data.get('sample_strategy')}`)",
                f"- Avg cuts/10s: `{agg.get('avg_cuts_per_10s')}`",
                f"- Avg median shot: `{agg.get('avg_median_shot_sec')}s`",
                f"- Avg integrated loudness: `{agg.get('avg_integrated_lufs')} LUFS`",
                "",
            ]
        )
    return "\n".join(lines)


def _write_engine_templates(skill_dir: Path, engine: str, cfg: dict[str, Any]) -> None:
    tmpl_out = skill_dir / "templates"
    tmpl_out.mkdir(parents=True, exist_ok=True)
    if engine == "hyperframes":
        src_tmpl = TEMPLATES_DIR / "hyperframes-talking-head-ui"
        if src_tmpl.is_dir():
            for item in src_tmpl.iterdir():
                if item.is_file():
                    shutil.copy2(item, tmpl_out / item.name)
        # Keep templates/edit.config.json synchronized with config.json
        edit_cfg = {
            "template_id": "hyperframes-talking-head-ui",
            "engine": "hyperframes",
            "aspect_ratio": cfg.get("aspect_ratio", "9:16"),
            "resolution": cfg.get("resolution", [1080, 1920]),
            "fps": cfg.get("fps", 30),
            "easing": cfg.get("motion", {}).get("easing", "ease-in-out"),
            "text_speed_scale": cfg.get("motion", {}).get("text_speed_scale", 1.2),
            "hook_window_sec": cfg.get("hook", {}).get("hook_window_sec", 10),
            "motion": cfg.get("motion", {}),
            "hook": cfg.get("hook", {}),
            "fake_camera": cfg.get("fake_camera", {}),
            "typography": cfg.get("typography", {}),
            "face_safe_zone": cfg.get("face_safe_zone", {}),
            "media": {
                "talking_head_src": "../assets/talking-head.mp4",
                "bgm_src": "../assets/sfx/bgm.mp3",
                "ui_sfx_src": "../assets/sfx/pop.wav",
            },
        }
        (tmpl_out / "edit.config.json").write_text(json.dumps(edit_cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    elif engine == "remotion":
        (tmpl_out / "edit.config.json").write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tsx = """// Portable Remotion Starter Template generated by video-style-trainer
// All keyframes MUST use Easing.inOut(Easing.ease) (no linear motion).
import config from "./edit.config.json";

export const TALKING_HEAD_STYLE_CONFIG = config;
"""
        (tmpl_out / "TalkingHeadStyle.tsx").write_text(tsx, encoding="utf-8")
    else:
        # filmcraft
        (tmpl_out / "edit.config.json").write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        fc = {
            "engine": "filmcraft",
            "portable": True,
            "easing": cfg.get("motion", {}).get("easing", "ease-in-out"),
            "face_safe_zone": cfg.get("face_safe_zone", {}),
            "hook_window_sec": cfg.get("hook", {}).get("hook_window_sec", 10),
            "assets_dir": "../assets",
        }
        (tmpl_out / "blueprint.fcproj.json").write_text(json.dumps(fc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def cmd_scaffold(args: argparse.Namespace) -> int:
    skill_name = _slugify_skill_name(args.skill_name)
    out_root = Path(args.out).expanduser().resolve()
    skill_dir = out_root / skill_name

    if args.profile:
        profile_path = Path(args.profile).expanduser().resolve()
        if not profile_path.is_file():
            print(f"[ERROR] Profile JSON not found: {profile_path}", file=sys.stderr)
            return 1
        cfg = json.loads(profile_path.read_text(encoding="utf-8"))
    else:
        preset_file = PRESETS_DIR / f"{args.preset}.json"
        if not preset_file.is_file():
            print(f"[ERROR] Preset not found: {preset_file}", file=sys.stderr)
            return 1
        cfg = json.loads(preset_file.read_text(encoding="utf-8"))

    probe_data: dict[str, Any] | None = None
    if args.probe:
        probe_path = Path(args.probe).expanduser().resolve()
        if not probe_path.is_file():
            print(f"[ERROR] Probe report not found: {probe_path}", file=sys.stderr)
            return 1
        probe_data = json.loads(probe_path.read_text(encoding="utf-8"))
        cfg["measured_baseline"] = probe_data.get("aggregate", {})

    engine = args.engine or cfg.get("engine", "hyperframes")
    cfg["skill_name"] = skill_name
    cfg["engine"] = engine
    cfg["version"] = cfg.get("version", "0.1.0")
    cfg["feedback_rounds"] = 0

    (skill_dir / "references" / "feedback_shots").mkdir(parents=True, exist_ok=True)
    (skill_dir / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    (skill_dir / "assets" / "sfx").mkdir(parents=True, exist_ok=True)

    (skill_dir / "references" / "feedback_shots" / ".gitkeep").write_text("", encoding="utf-8")
    (skill_dir / "assets" / "fonts" / ".gitkeep").write_text("", encoding="utf-8")
    (skill_dir / "assets" / "sfx" / ".gitkeep").write_text("", encoding="utf-8")
    (skill_dir / "assets" / "README.md").write_text(
        "# Portable Assets\n\nĐặt font (`.ttf`/`.otf`) vào `assets/fonts/` và SFX/BGM vào `assets/sfx/`.\n"
        "Luôn tham chiếu bằng đường dẫn tương đối (`assets/...`) để skill chạy được trên mọi máy.\n",
        encoding="utf-8",
    )

    (skill_dir / "config.json").write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(_build_scaffold_skill_md(skill_name, cfg), encoding="utf-8")
    (skill_dir / "references" / "style-spec.md").write_text(
        _build_style_spec_md(skill_name, cfg, probe_data), encoding="utf-8"
    )
    (skill_dir / "references" / "feedback-log.md").write_text(
        f"# Feedback Log — {skill_name}\n\n"
        "Ghi lại toàn bộ các vòng thử mù & hiệu chỉnh (Round 1 → Round 4) để mọi video sau tự động kế thừa.\n",
        encoding="utf-8",
    )

    _write_engine_templates(skill_dir, engine, cfg)

    print(json.dumps({"status": "ok", "skill_dir": str(skill_dir), "engine": engine}, ensure_ascii=False))
    return 0


def _parse_typed_value(raw: str) -> Any:
    low = raw.strip().lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if low == "null" or low == "none":
        return None
    if (raw.startswith("[") and raw.endswith("]")) or (raw.startswith("{") and raw.endswith("}")):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
    try:
        if "." in raw or "e" in low:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw


def _set_nested(cfg: dict[str, Any], dotted_key: str, val: Any) -> tuple[Any, Any]:
    parts = [p.strip() for p in dotted_key.split(".") if p.strip()]
    if not parts:
        raise ValueError(f"Invalid key path: {dotted_key!r}")
    cur: dict[str, Any] = cfg
    for part in parts[:-1]:
        nxt = cur.get(part)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[part] = nxt
        cur = nxt
    leaf = parts[-1]
    old = cur.get(leaf)
    cur[leaf] = val

    # Keep top-level mirrors synced when nested canonical keys change
    mirror_map = {
        "motion.easing": "easing",
        "motion.text_speed_scale": "text_speed_scale",
        "hook.hook_window_sec": "hook_window_sec",
    }
    if dotted_key in mirror_map and mirror_map[dotted_key] in cfg:
        cfg[mirror_map[dotted_key]] = val
    elif dotted_key == "hook.fake_camera" and isinstance(val, bool) and isinstance(cfg.get("fake_camera"), dict):
        cfg["fake_camera"]["enabled"] = val

    return old, val


def cmd_feedback(args: argparse.Namespace) -> int:
    skill_dir = Path(args.skill_dir).expanduser().resolve()
    cfg_path = skill_dir / "config.json"
    log_path = skill_dir / "references" / "feedback-log.md"

    if not cfg_path.is_file():
        print(f"[ERROR] config.json not found in {skill_dir}", file=sys.stderr)
        return 1

    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    changes: list[tuple[str, Any, Any]] = []

    for item in args.set or []:
        if "=" not in item:
            print(f"[ERROR] --set expects key=val, got: {item!r}", file=sys.stderr)
            return 1
        key, raw_val = item.split("=", 1)
        typed_val = _parse_typed_value(raw_val)
        old_val, new_val = _set_nested(cfg, key.strip(), typed_val)
        changes.append((key.strip(), old_val, new_val))

    cfg["feedback_rounds"] = max(int(cfg.get("feedback_rounds", 0)), int(args.round))
    cfg_path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Sync templates/edit.config.json if present
    edit_cfg_path = skill_dir / "templates" / "edit.config.json"
    if edit_cfg_path.is_file():
        edit_cfg = json.loads(edit_cfg_path.read_text(encoding="utf-8"))
        for k in ("easing", "text_speed_scale", "hook_window_sec", "motion", "hook", "fake_camera", "typography", "face_safe_zone"):
            if k in cfg:
                edit_cfg[k] = cfg[k]
        edit_cfg_path.write_text(json.dumps(edit_cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    rel_shot: str | None = None
    if args.screenshot:
        src_shot = Path(args.screenshot).expanduser().resolve()
        if not src_shot.is_file():
            print(f"[ERROR] Screenshot file not found: {src_shot}", file=sys.stderr)
            return 1
        shots_dir = skill_dir / "references" / "feedback_shots"
        shots_dir.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", src_shot.name)
        dest_name = f"round_{args.round}_{safe_name}"
        dest_shot = shots_dir / dest_name
        shutil.copy2(src_shot, dest_shot)
        rel_shot = f"references/feedback_shots/{dest_name}"

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry_lines = [
        "",
        f"## Round {args.round} ({timestamp})",
        "",
        f"- **Feedback:** {args.note}",
    ]
    if rel_shot:
        entry_lines.append(f"- **Screenshot:** `{rel_shot}`")
    if changes:
        entry_lines.append("- **Config updates persisted:**")
        for key, old_val, new_val in changes:
            entry_lines.append(f"  - `{key}`: `{json.dumps(old_val, ensure_ascii=False)}` -> `{json.dumps(new_val, ensure_ascii=False)}`")
    else:
        entry_lines.append("- **Config updates persisted:** _(none)_")

    log_path.parent.mkdir(parents=True, exist_ok=True)
    existing = log_path.read_text(encoding="utf-8") if log_path.is_file() else "# Feedback Log\n"
    log_path.write_text(existing.rstrip() + "\n" + "\n".join(entry_lines) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "ok",
                "round": args.round,
                "changes": [{"key": k, "old": o, "new": n} for k, o, n in changes],
                "screenshot": rel_shot,
            },
            ensure_ascii=False,
        )
    )
    return 0


def _validate_frontmatter(skill_md_path: Path) -> tuple[bool, str]:
    text = skill_md_path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return False, "Missing YAML frontmatter opening '---'"
    end_idx = text.find("\n---", 4)
    if end_idx == -1:
        return False, "Missing YAML frontmatter closing '---'"
    fm = text[4:end_idx]
    has_name = bool(re.search(r"^name:\s*\S+", fm, re.MULTILINE))
    has_desc = bool(re.search(r"^description:\s*\S+", fm, re.MULTILINE))
    if not (has_name and has_desc):
        return False, "Frontmatter must declare non-empty 'name' and 'description'"
    return True, "Valid SKILL.md frontmatter (name + description)"


def cmd_lint_skill(args: argparse.Namespace) -> int:
    skill_dir = Path(args.skill_dir).expanduser().resolve()
    checks: list[dict[str, Any]] = []

    def add_check(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": passed, "detail": detail})

    if not skill_dir.is_dir():
        print(f"[FAIL] Skill directory not found: {skill_dir}", file=sys.stderr)
        return 1

    # 1. Required structure
    required = [
        skill_dir / "SKILL.md",
        skill_dir / "config.json",
        skill_dir / "references" / "style-spec.md",
        skill_dir / "references" / "feedback-log.md",
    ]
    missing = [str(p.relative_to(skill_dir)) for p in required if not p.is_file()]
    add_check("required_files", len(missing) == 0, "All required files present" if not missing else f"Missing: {missing}")

    # 2. SKILL.md frontmatter + nested SKILL.md check
    skill_md = skill_dir / "SKILL.md"
    if skill_md.is_file():
        ok_fm, msg_fm = _validate_frontmatter(skill_md)
        add_check("skill_md_frontmatter", ok_fm, msg_fm)
    else:
        add_check("skill_md_frontmatter", False, "SKILL.md missing")

    nested_skill_mds = [
        str(p.relative_to(skill_dir))
        for p in skill_dir.rglob("SKILL.md")
        if p.resolve() != skill_md.resolve()
    ]
    add_check(
        "nested_skill_md",
        len(nested_skill_mds) == 0,
        "No unintended nested SKILL.md in subdirectories"
        if not nested_skill_mds
        else f"Found nested SKILL.md: {nested_skill_mds}",
    )

    # 3. Config rules: ease-in-out + face_safe_zone + hook
    cfg_path = skill_dir / "config.json"
    if cfg_path.is_file():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            cfg = {}
            add_check("config_json_valid", False, f"Invalid JSON: {exc}")
        else:
            add_check("config_json_valid", True, "config.json parsed cleanly")

        easing = str(cfg.get("motion", {}).get("easing") or cfg.get("easing") or "").lower()
        is_ease_in_out = "ease-in-out" in easing or "cubic-bezier(0.42" in easing
        add_check(
            "ease_in_out",
            is_ease_in_out and easing != "linear",
            f"motion.easing='{easing}'" if is_ease_in_out else f"Expected ease-in-out, got '{easing}'",
        )

        fsz = cfg.get("face_safe_zone")
        has_fsz = (
            isinstance(fsz, dict)
            and fsz.get("enabled") is True
            and isinstance(fsz.get("x_range"), list)
            and len(fsz["x_range"]) == 2
            and isinstance(fsz.get("y_range"), list)
            and len(fsz["y_range"]) == 2
        )
        add_check(
            "face_safe_zone",
            has_fsz,
            f"face_safe_zone enabled x={fsz.get('x_range')} y={fsz.get('y_range')}"
            if has_fsz
            else "Missing or disabled face_safe_zone configuration",
        )
    else:
        add_check("config_json_valid", False, "config.json missing")
        add_check("ease_in_out", False, "config.json missing")
        add_check("face_safe_zone", False, "config.json missing")

    # 4. Portability scan across SKILL.md, config.json, references/, templates/
    violations: list[str] = []
    scan_targets = [skill_dir / "SKILL.md", skill_dir / "config.json"]
    for sub in ("references", "templates"):
        sub_dir = skill_dir / sub
        if sub_dir.is_dir():
            scan_targets.extend(sorted(p for p in sub_dir.rglob("*") if p.is_file()))

    for path in scan_targets:
        if not path.is_file() or path.suffix.lower() not in TEXT_SCAN_EXTS:
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(skill_dir)
        for line_no, line in enumerate(content.splitlines(), start=1):
            for label, pat in PORTABILITY_PATTERNS:
                m = pat.search(line)
                if m:
                    violations.append(f"{rel}:{line_no} [{label}] -> {m.group(0)}")

    add_check(
        "portability",
        len(violations) == 0,
        "Zero hardcoded personal/OS paths across SKILL.md, config.json, references/, templates/"
        if not violations
        else f"Hardcoded paths found: {violations}",
    )

    all_passed = all(c["passed"] for c in checks)
    if args.json:
        print(json.dumps({"passed": all_passed, "checks": checks}, indent=2, ensure_ascii=False))
    else:
        for c in checks:
            tag = "PASS" if c["passed"] else "FAIL"
            print(f"[{tag}] {c['check']}: {c['detail']}")
        print(f"RESULT: {'PASS' if all_passed else 'FAIL'}")

    return 0 if all_passed else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="style_trainer.py",
        description="Train, measure, iterate, and lint video editing skills (Thơ EDITOR 5-Phase + 4-Round workflow).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_probe = sub.add_parser("probe", help="Measure video sample(s) and build contact sheet(s).")
    p_probe.add_argument("input", help="Path to a video file or directory of videos.")
    p_probe.add_argument("--out", required=True, help="Output directory for probe_report.json and contact sheets.")
    p_probe.add_argument("--fps", type=float, default=1.0, help="Frame sampling FPS for contact sheet (default: 1.0).")
    p_probe.add_argument("--no-sheets", action="store_true", help="Skip generating contact sheet images.")
    p_probe.add_argument("--scdet-threshold", type=float, default=10.0, help="ffmpeg scdet threshold (default: 10.0).")
    p_probe.set_defaults(func=cmd_probe)

    p_scaf = sub.add_parser("scaffold", help="Scaffold a new portable video-editing skill.")
    p_scaf.add_argument("skill_name", help="Name of the new skill to generate.")
    p_scaf.add_argument("--out", required=True, help="Parent output directory where <skill_name>/ will be created.")
    p_scaf.add_argument("--preset", default="talking-head-ui-hyperframes", help="Preset name in references/presets/.")
    p_scaf.add_argument("--profile", help="Optional custom JSON profile path (overrides --preset).")
    p_scaf.add_argument("--engine", choices=["hyperframes", "remotion", "filmcraft"], help="Target editing engine.")
    p_scaf.add_argument("--probe", help="Optional probe_report.json to seed baseline metrics.")
    p_scaf.set_defaults(func=cmd_scaffold)

    p_fb = sub.add_parser("feedback", help="Record round feedback, copy screenshot, and update config.json.")
    p_fb.add_argument("skill_dir", help="Path to the trained skill directory.")
    p_fb.add_argument("--round", type=int, required=True, help="Feedback round number (e.g. 1, 2, 3, 4).")
    p_fb.add_argument("--note", required=True, help="Feedback description.")
    p_fb.add_argument("--screenshot", help="Optional screenshot path showing layout/position issue.")
    p_fb.add_argument("--set", action="append", default=[], help="Update config parameter (e.g. motion.text_speed_scale=1.2).")
    p_fb.set_defaults(func=cmd_feedback)

    p_lint = sub.add_parser("lint-skill", help="Validate skill structure, rules, and portability.")
    p_lint.add_argument("skill_dir", help="Path to the skill directory to validate.")
    p_lint.add_argument("--json", action="store_true", help="Output structured JSON report.")
    p_lint.set_defaults(func=cmd_lint_skill)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
