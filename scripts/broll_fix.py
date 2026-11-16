#!/usr/bin/env python3
"""Làm lại B-roll sai kịch bản (D9) bằng Muse theo luật H5/D3/D8: kiểm → sao lưu → viết prompt → render → xác minh.

    PY=~/.venvs/video-skills/bin/python
    $PY broll_fix.py ready                                        # chỉ GET /readyz; chưa sẵn sàng → báo D3, mã thoát 1, KHÔNG dùng dịch vụ khác
    $PY broll_fix.py plan    <thư mục kịch bản> [--speed 1.10] [--engine muse|flow] [--outputs 2]   # cảnh B-roll + giây cần xin (+ tín dụng Flow)
    $PY broll_fix.py lint    <thư mục> --prompts broll_new_prompts.json
    $PY broll_fix.py prepare <thư mục> --prompts broll_new_prompts.json [--source muse|flow] [--keep-clips] [--dry-run] [--backup-root DIR]
                                                                  # --keep-clips: tạo lại cảnh xong → ghi prompt cuối, giữ clip
    $PY broll_fix.py verify  <thư mục> --scenes 3,4,5 [--speed 1.10] [--out-dir DIR]
    $PY broll_fix.py normalize <file tải về> <thư mục>/NN_b-roll-M.mp4 [--mark flow]   # clip tạo ngoài Muse (Google Flow…) → chuẩn skill

normalize (v2.8+): 1080x1920, 30 fps, KHÔNG tiếng, x264 CRF 12 BT.709; tự cắt viền trắng/đen/đồng màu ≥ 2 % từ khung đầu (1.2.2 F3: `trim_uniform_borders`) trước khi scale; `--mark flow` xoá dấu ngôi sao của Google Flow ở góc dưới phải
(đo trên khung 1080x1920: x≈860–940, y≈1700–1780) bằng `delogo`. Chạy sau `prepare` (file cũ đã được sao lưu), trước `verify`.

broll_new_prompts.json = [{"seq": 3, "prompt": "<câu tiếng Anh H5>", "anchor_quote": "<đoạn nguyên văn của tts_text>"}, …]
Không gọi API nào ngoại trừ `ready` (GET /readyz). Bước render do `render_muse_broll.py <thư mục> --shot NN_b-roll-M.mp4` làm.

lint (H5 + 1.2.2–1.2.3 F2): lõi prompt 8–60 chữ tiếng Anh, không dấu tiếng Việt; cấm text/caption/subtitle/sign/logo/number/chart/dashboard/UI/chat/app/
brand/label/poster/"writing on paper"/notes/checklist/checkbox/written/bullet/handwritten/handwriting/chatting/message/messaging/texting/side-by-side/comparison/graph/metrics/analytics/statistics/engagement/tên nền tảng & hãng (youtube/tiktok/facebook/instagram/iphone/macbook/apple/samsung/google); màn hình / laptop / tivi / bảng trắng / giấy tờ chỉ khi ghi out of frame / out of focus / blurred / blank
("angled away", "soft glow" KHÔNG đủ: Flow 2026-11-13 vẫn vẽ logo DELL, dashboard); founder / CEO / người nói / narrator chỉ khi không lộ mặt
(from behind, over the shoulder, hands, silhouette, face out of frame) — không có ảnh tham chiếu thì AI vẽ người lạ (A4); một clip một cảnh liền
(cấm transition from/to, cut to, montage, PiP, overlay — mô hình tách đôi clip / vẽ ghi chú hậu kỳ); có người → ghi "Vietnamese";
anchor_quote nằm trong tts_text.
Flow (D3, references/flow-broll.md): Omni 1.2 Flash 720p, 3–15 s, 3 tín dụng/s (11–15 s: 6/s), nâng 1080p miễn phí ≤ 10 s (1/s phần vượt).
verify: 1080x1920 30 fps, không có tiếng, đủ dài so với tiếng, khác mọi clip thư viện + B-roll khác (media_reuse.SAME),
         ghi qa/broll_check_sheet.jpg (10/30/50/70/90 %) — người làm PHẢI xem ảnh này (chữ/logo/đúng lời) rồi ghi lại.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from pathlib import Path

MIN_WORDS, MAX_WORDS = 8, 60
MAX_MUSE_SEC, MIN_MUSE_SEC = 10, 2
VOICE_PAD = 0.3                    # xin dài hơn tiếng 0,3 s
HOLD_MAX = 0.3                     # được giữ khung cuối tối đa 0,3 s
SUFFIX_MARK = " (Pure visual"      # phần đuôi cố định BROLL_STRICT_SUFFIX_EN nối sau lõi prompt
SHEET_PCTS = (0.10, 0.30, 0.50, 0.70, 0.90)
BACKUP_ROOT = Path.home() / ".cache" / "opa-video-studio" / "backup"

BANNED_RE = re.compile(
    r"\b(?:texts?|captions?|subtitles?|signs?|logos?|numbers?|charts?|dashboards?|ui|chat|apps?|labels?|posters?"
    r"|brands?|brand names?"
    r"|notes?|checklists?|checkbox(?:es)?|written|bullets?|handwritten|handwriting"
    r"|chatting|messages?|messaging|texting"
    r"|side-by-side|comparison|graphs?|metrics|analytics|statistics|engagement"
    r"|youtube|tiktok|facebook|instagram|iphone|macbook|apple|samsung|google)\b|writing on paper",
    re.I,
)
SCREEN_RE = re.compile(r"\b(?:screens?|monitors?|laptops?|computers?|tablets?|phones?|tvs?|televisions?|displays?|whiteboards?|"
                       r"documents?|papers?|notebooks?|newspapers?)\b", re.I)
SCREEN_OK_RE = re.compile(r"\b(?:out of frame|out of focus|blurred|defocused|blank)\b", re.I)
SPEAKER_RE = re.compile(r"\b(?:founders?|ceos?|narrators?|speakers?|presenters?|hosts?)\b", re.I)
FACELESS_RE = re.compile(r"\b(?:from behind|back view|over[- ]the[- ]shoulder|silhouetted?|hands? only|face out of frame|"
                         r"face not visible|cropped (?:at|below) the (?:chin|shoulders))\b", re.I)
PERSON_RE = re.compile(r"\b(?:man|men|woman|women|person|people|guy|boy|girl|couple|family|colleagues?|team|crew|staff|crowd|"
                       r"engineers?|designers?|customers?|clients?|owners?|founders?|investors?|chefs?|cooks?|workers?|students?|"
                       r"diners?|buyers?|agents?|brokers?|creators?|entrepreneurs?|businessman|businesswoman)\b", re.I)
MULTI_SHOT_RE = re.compile(r"\b(?:transitions?(?:ing)? (?:from|to|into)|cuts? (?:to|between)|montage|split[- ]screen|"
                           r"before[- ]and[- ]after|picture[- ]in[- ]picture|pip|overlay)\b", re.I)
FLOW_MIN_SEC, FLOW_MAX_SEC, FLOW_BASE_SEC = 3, 15, 10   # Omni 1.2 Flash trên gói Pro (thanh trượt 3–15 s)
FLOW_RATE, FLOW_RATE_LONG = 3, 6                         # tín dụng / giây ở 720p: ≤ 10 s, phần 11–15 s


def _norm(text: str) -> str:
    t = unicodedata.normalize("NFC", text or "").lower().replace("_", " ")
    return " ".join(re.sub(r"[^\w\s]", " ", t).split())


def has_diacritics(text: str) -> bool:
    nfd = unicodedata.normalize("NFD", text or "")
    return "đ" in text.lower() or any(unicodedata.combining(c) for c in nfd)


def core_of(prompt_full: str) -> str:
    """Bỏ đuôi '(Pure visual footage …)' còn lõi mô tả cảnh."""
    s = (prompt_full or "").strip()
    i = s.find(SUFFIX_MARK)
    return (s[:i] if i >= 0 else s).strip()


def lint_prompt(core: str, tts_text: str | None = None, anchor: str | None = None) -> list[str]:
    """Luật H5 cho lõi prompt B-roll → danh sách lỗi (rỗng = đạt)."""
    core = (core or "").strip()
    if not core:
        return ["prompt rỗng"]
    problems = []
    if core.lower().startswith("clip thư viện"):
        problems.append("là mã clip thư viện, không phải prompt mô tả cảnh")
    if has_diacritics(core):
        problems.append("có dấu tiếng Việt (H5: prompt tiếng Anh)")
    n = len(core.split())
    if not MIN_WORDS <= n <= MAX_WORDS:
        problems.append(f"{n} chữ, cần {MIN_WORDS}–{MAX_WORDS}")
    banned = sorted({m.group(0).lower() for m in BANNED_RE.finditer(core)})
    if banned:
        problems.append("chứa từ cấm: " + ", ".join(banned))
    if SCREEN_RE.search(core) and not SCREEN_OK_RE.search(core):
        problems.append("có màn hình / laptop / bảng / giấy nhưng không ghi out of frame / out of focus / blurred / blank")
    if PERSON_RE.search(core) and "vietnamese" not in core.lower():
        problems.append("có người nhưng chưa ghi Vietnamese (kênh Việt — không ghi thì AI ra người phương Tây)")
    if MULTI_SHOT_RE.search(core):
        problems.append("nhiều cảnh / ghi chú hậu kỳ trong một clip (transition, cut, montage, PiP, overlay) — một clip một cảnh liền")
    if SPEAKER_RE.search(core) and not FACELESS_RE.search(core):
        problems.append("có founder / người nói nhưng không giấu mặt (from behind / over the shoulder / hands / silhouette)")
    if tts_text is not None:
        a = _norm(anchor or "")
        if not a:
            problems.append("thiếu anchor_quote")
        elif a not in _norm(tts_text):
            problems.append("anchor_quote không nằm trong tts_text")
    return problems


def request_seconds(voice_len: float | None, fallback: float = 4.0) -> int:
    """Giây xin Muse: ceil(tiếng + 0,3), kẹp 2–10 (Muse tối đa 10 s)."""
    base = fallback if not voice_len else voice_len + VOICE_PAD
    return max(MIN_MUSE_SEC, min(MAX_MUSE_SEC, math.ceil(base - 1e-9)))


def flow_seconds(voice_len: float | None, fallback: float = 4.0) -> int:
    """Giây đặt trên thanh trượt Flow: ceil(tiếng + 0,3), kẹp 3–15."""
    base = fallback if not voice_len else voice_len + VOICE_PAD
    return max(FLOW_MIN_SEC, min(FLOW_MAX_SEC, math.ceil(base - 1e-9)))


def flow_credits(secs: int, outputs: int = 2) -> int:
    """Tín dụng Flow: mỗi bản tạo (720p) + nâng 1080p cho bản được chọn (miễn phí ≤ 10 s, 1/s phần vượt)."""
    extra = max(0, secs - FLOW_BASE_SEC)
    gen = min(secs, FLOW_BASE_SEC) * FLOW_RATE + extra * FLOW_RATE_LONG
    return outputs * gen + extra


def probe(path: Path) -> dict:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,avg_frame_rate",
                        "-show_entries", "format=duration", "-of", "json", str(path)], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except ValueError:
        return {}


def duration_of(path: Path) -> float:
    try:
        return float(probe(path).get("format", {}).get("duration") or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def segments(folder: Path) -> dict[int, dict]:
    m = _load(folder / "00_storyboard_manifest.json")
    return {s["seq_index"]: s for s in m["segments"] if s.get("type") == "b-roll"}


def voice_len_of(path: Path) -> float:
    return duration_of(path) if path.is_file() else 0.0


def voice_len(folder: Path, seg: dict) -> float:
    vf = (seg.get("files") or {}).get("voice_file")
    return duration_of(folder / vf) if vf and (folder / vf).is_file() else 0.0


# ---------------------------------------------------------------- ready / plan / lint
def cmd_ready(_args) -> int:
    import render_muse_broll as rmb
    try:
        base, _key = rmb.load_muse_config()
    except RuntimeError as e:
        print(f"[D3] {e}. Dừng, báo người dùng; không dùng dịch vụ trả phí khác.")
        return 1
    if not rmb.check_muse_ready(base):
        print("[D3] Muse /readyz chưa sẵn sàng. Dừng, báo người dùng; KHÔNG chuyển sang dịch vụ trả phí khác.")
        return 1
    print("[READY] Muse /readyz đã sẵn sàng.")
    return 0


def _status_of(seg: dict) -> str:
    core = core_of(seg.get("broll_prompt") or "")
    p = lint_prompt(core)
    return "OK" if not p else ("FAIL: " + "; ".join(p))


def cmd_plan(args) -> int:
    folder = Path(args.folder)
    flow, total = args.engine == "flow", 0
    for seq, seg in sorted(segments(folder).items()):
        v = voice_len(folder, seg)
        clip = folder / (seg.get("files") or {}).get("video_file", "")
        cl = duration_of(clip) if clip.is_file() else 0.0
        fallback = float(seg.get("duration_sec") or 4.0)
        if flow:
            req = flow_seconds(v, fallback)
            cost = flow_credits(req, args.outputs)
            total += cost
            ask = f"Flow {req}s x{args.outputs} = {cost} tín dụng"
            short = v + VOICE_PAD > FLOW_MAX_SEC
        else:
            req = request_seconds(v, fallback)
            ask = f"xin Muse {req}s"
            short = v + VOICE_PAD > MAX_MUSE_SEC
        print(f"cảnh {seq} ({seg['role_id']}): tiếng {v:.2f}s → {v / args.speed:.2f}s ở {args.speed}x · clip hiện {cl:.2f}s · "
              f"{ask} → {req / args.speed:.2f}s sau tăng tốc" + (" (vượt mức tối đa: tách 2 cảnh chèn)" if short else ""))
        print(f"    prompt hiện tại: {_status_of(seg)}")
        print(f"    tts_text: {seg.get('tts_text', '')}")
    if flow:
        print(f"Tổng Flow (mọi cảnh B-roll, x{args.outputs}): {total} tín dụng — so với số dư trên Flow trước khi tạo; thiếu thì báo, KHÔNG mua (D3).")
    return 0


def _read_new(path: Path) -> list[dict]:
    data = _load(path)
    if not isinstance(data, list):
        raise ValueError("file prompts phải là danh sách [{seq, prompt, anchor_quote}, …]")
    return data


def lint_new(folder: Path, new: list[dict]) -> list[str]:
    segs, out = segments(folder), []
    for e in new:
        seg = segs.get(e.get("seq"))
        if seg is None:
            out.append(f"cảnh {e.get('seq')}: không có b-roll này trong manifest")
            continue
        out += [f"cảnh {e['seq']}: {p}" for p in lint_prompt(e.get("prompt", ""), seg.get("tts_text", ""), e.get("anchor_quote"))]
    return out


def cmd_lint(args) -> int:
    try:
        problems = lint_new(Path(args.folder), _read_new(Path(args.prompts)))
    except (OSError, ValueError, KeyError) as e:
        print(f"[BROLL FAIL] đọc đầu vào: {e}", file=sys.stderr)
        return 2
    for p in problems:
        print(f"[H5 FAIL] {p}")
    print("[H5 OK] mọi prompt đạt" if not problems else f"{len(problems)} lỗi H5")
    return 1 if problems else 0


# ---------------------------------------------------------------- prepare
def _backup_dir(root: Path, folder: Path) -> Path:
    base = root / time.strftime("%Y-%m-%d") / folder.name
    return base if not base.exists() else base.with_name(f"{base.name}_{time.strftime('%H%M%S')}")


def _stale_files(folder: Path, video_file: str) -> list[Path]:
    stem = Path(video_file).stem
    rx = re.compile(rf"^{re.escape(stem)}(_x\d{{3}})?\.[A-Za-z0-9]+$")
    found = [folder / video_file] if (folder / video_file).exists() else []
    found += [p for d in sorted((folder / "media").glob("x*")) if d.is_dir() for p in sorted(d.iterdir()) if rx.match(p.name)]
    return found


def build_item(old: dict, entry: dict, voice: float, backup: Path, source: str = "muse") -> dict:
    import render_muse_broll as rmb
    core = entry["prompt"].strip()
    fallback = float(old.get("duration_target_sec", 4.0))
    flow = source == "flow"
    item = {k: v for k, v in old.items() if k != "prompt_vi"}
    item.update({"prompt_core": core, "prompt_full": core if flow else f"{core} ({rmb.BROLL_STRICT_SUFFIX_EN})",
                 "anchor_quote": entry["anchor_quote"],
                 "duration_target_sec": flow_seconds(voice, fallback) if flow else request_seconds(voice, fallback),
                 "source": source, "regen_of": old.get("prompt_full") or old.get("prompt_vi"), "backup": str(backup)})
    return item


def cmd_prepare(args) -> int:
    folder = Path(args.folder)
    try:
        new = _read_new(Path(args.prompts))
        problems = lint_new(folder, new)
    except (OSError, ValueError, KeyError) as e:
        print(f"[BROLL FAIL] đọc đầu vào: {e}", file=sys.stderr)
        return 2
    if problems:
        for p in problems:
            print(f"[H5 FAIL] {p}")
        print("Không sao lưu / không sửa gì. Sửa prompt rồi chạy lại.")
        return 1
    manifest_p, prompts_p, md_p = folder / "00_storyboard_manifest.json", folder / "prompts_muse_veo_broll.json", folder / "00_BANG_PHAN_CANH.md"
    manifest, items = _load(manifest_p), _load(prompts_p)
    backup = _backup_dir(Path(args.backup_root), folder)
    segs = segments(folder)
    missing = [e["seq"] for e in new if not any(i.get("seq_index") == e["seq"] for i in items)]
    if missing:
        print(f"[BROLL FAIL] prompts_muse_veo_broll.json không có cảnh {missing}", file=sys.stderr)
        return 2
    moves = {e["seq"]: [] if args.keep_clips else _stale_files(folder, segs[e["seq"]]["files"]["video_file"]) for e in new}
    print(f"{'[DRY-RUN] ' if args.dry_run else ''}sao lưu vào {backup}")
    for seq, files in moves.items():
        print(f"  cảnh {seq}: chuyển {len(files)} file cũ " + ", ".join(p.name for p in files))
    if args.dry_run:
        return 0
    backup.mkdir(parents=True, exist_ok=True)
    for p in (manifest_p, prompts_p, md_p):
        if p.exists():
            shutil.copy2(p, backup / p.name)
    for files in moves.values():
        for p in files:
            dest = backup / p.relative_to(folder)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(dest))
    by_seq = {e["seq"]: e for e in new}
    today = time.strftime("%Y-%m-%d")
    new_items = [build_item(i, by_seq[i["seq_index"]], voice_len(folder, segs[i["seq_index"]]), backup, args.source)
                 if i.get("seq_index") in by_seq else i for i in items]
    full_by_seq = {i["seq_index"]: i["prompt_full"] for i in new_items if i.get("seq_index") in by_seq}
    old_vd = {s: segs[s].get("visual_direction") for s in by_seq}
    new_segments = []
    for s in manifest["segments"]:
        e = by_seq.get(s["seq_index"]) if s.get("type") == "b-roll" else None
        if e is None:
            new_segments.append(s)
            continue
        hist = list(s.get("regen_history") or []) + [{"date": today, "reason": "D9 cảnh thư viện kịch bản khác → tạo mới từ lời cảnh (H5)",
                                                       "old_prompt": s.get("broll_prompt"), "backup": str(backup)}]
        new_segments.append({**s, "broll_prompt": full_by_seq[s["seq_index"]], "visual_direction": e["prompt"].strip(),
                             "broll_source": args.source, "regen_history": hist})
    _save(prompts_p, new_items)
    _save(manifest_p, {**manifest, "segments": new_segments})
    if md_p.exists():
        text = md_p.read_text(encoding="utf-8")
        for seq, old in old_vd.items():
            if old and old in text:
                text = text.replace(old, by_seq[seq]["prompt"].strip())
        md_p.write_text(text, encoding="utf-8")
    nxt = ("tạo trong Google Flow theo references/flow-broll.md, rồi normalize (--mark flow khi bản tải về có dấu)" if args.source == "flow"
           else "render_muse_broll.py <thư mục> --shot <NN_b-roll-M.mp4> cho từng cảnh")
    print(f"Đã cập nhật prompts_muse_veo_broll.json + manifest (nguồn {args.source}). Kế tiếp: {nxt}.")
    return 0


# ---------------------------------------------------------------- verify
MARKS = {"flow": "delogo=x=845:y=1685:w=110:h=110"}   # dấu ngôi sao Google Flow, toạ độ trên khung 1080x1920


def border_crop_box(img, min_px: int = 8, std_max: float = 3.0, jump: float = 30.0,
                    min_frac: float = 0.02) -> tuple[int, int, int, int]:
    """Dò dải viền trắng/đen/đồng màu ở 4 mép (1.2.2 F3). Trả hộp crop (x0, y0, x1, y1); viền < min_frac (2 %) thì giữ nguyên."""
    import numpy as np

    rgb = np.asarray(img.convert("RGB"), dtype=np.float32)

    def band(lines: "np.ndarray") -> int:
        dim = len(lines)
        ref = lines[0].mean(axis=0)
        n = 0
        for row in lines:
            if float(row.std(axis=0).max()) < std_max and float(np.abs(row.mean(axis=0) - ref).max()) < max(std_max * 2.0, 6.0):
                n += 1
            else:
                break
        if n < min_px or n < dim * min_frac or n + min_px > dim or n > dim * 0.25:
            return 0
        border_rgb = lines[:n].mean(axis=(0, 1))
        next_block = lines[n:n + min_px]
        edge_diff = float(np.abs(next_block - border_rgb).max(axis=-1).mean())
        return n if edge_diff > jump else 0

    top, bottom = band(rgb), band(rgb[::-1])
    side = rgb.transpose(1, 0, 2)
    left, right = band(side), band(side[::-1])
    return (left, top, img.width - right, img.height - bottom)


def trim_uniform_borders(img, min_px: int = 8, std_max: float = 3.0, jump: float = 30.0,
                         min_frac: float = 0.02):
    """Cắt viền trắng/đen/đồng màu quanh khung hình (1.2.2 F3); giữ nguyên khi không có viền hoặc viền < min_frac (2 %)."""
    box = border_crop_box(img, min_px=min_px, std_max=std_max, jump=jump, min_frac=min_frac)
    if box == (0, 0, img.width, img.height):
        return img
    return img.crop(box)


def _first_frame(path: Path):
    import io
    from PIL import Image

    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                       capture_output=True)
    if r.returncode != 0 or not r.stdout:
        return None
    try:
        return Image.open(io.BytesIO(r.stdout)).convert("RGB")
    except OSError:
        return None


def cmd_normalize(args) -> int:
    raw, out = Path(args.raw), Path(args.out)
    if not raw.is_file():
        print(f"LỖI: không thấy {raw}")
        return 1
    vs = next((x for x in probe(raw).get("streams", []) if x.get("codec_type") == "video"), {})
    if int(vs.get("width") or 0) < 1080:
        print(f"CẢNH BÁO: bản tải về {vs.get('width')}x{vs.get('height')} < 1080 — Flow: tải lại mục '1080p Đã tăng độ phân giải' (miễn phí ≤ 10 s)")
    filters = []
    first = _first_frame(raw)
    trimmed = None
    if first is not None:
        x0, y0, x1, y1 = border_crop_box(first)
        if (x0, y0, x1, y1) != (0, 0, first.width, first.height):
            cw, ch = x1 - x0, y1 - y0
            filters.append(f"crop={cw}:{ch}:{x0}:{y0}")
            trimmed = f"đã cắt viền ({first.width}x{first.height} → {cw}x{ch})"
    filters.append("scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,fps=30")
    if args.mark:
        filters.append(MARKS[args.mark])
    filters.append("setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709")
    vf = ",".join(filters)
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-an", "-vf", vf, "-c:v", "libx264", "-crf", "12", "-preset", "slow",
           "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-movflags", "+faststart", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if r.returncode != 0 or not out.is_file():
        print(f"LỖI ffmpeg: {r.stderr.strip()[-400:]}")
        return 1
    notes = [x for x in (trimmed, f"đã xoá dấu {args.mark}" if args.mark else None) if x]
    suffix = f", {', '.join(notes)}" if notes else ""
    print(f"OK {out.name}: 1080x1920 30 fps, không tiếng{suffix} ({duration_of(out):.2f} s)")
    return 0


def _frame(path: Path, t: float):
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(path), "-frames:v", "1", "-vf", "scale=216:384",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(384, 216, 3) if len(raw) == 216 * 384 * 3 else None


def contact_sheet(rows: list[tuple[int, Path, float]], out: Path) -> list[str]:
    """Mỗi cảnh một hàng 5 khung → out (jpg). Trả cảnh báo heuristic 'có thể có chữ' (yếu, chỉ WARN)."""
    import numpy as np
    from PIL import Image
    warn, lines = [], []
    for seq, path, dur in rows:
        frames = [_frame(path, max(dur * p - 0.05, 0.0)) for p in SHEET_PCTS]
        frames = [f if f is not None else np.zeros((384, 216, 3), np.uint8) for f in frames]
        lines.append(np.concatenate(frames, axis=1))
        for f in frames:
            g = f.mean(axis=2)
            edge = (np.abs(np.diff(g, axis=1))[:-1] > 60) | (np.abs(np.diff(g, axis=0))[:, :-1] > 60)
            if edge.mean() > 0.12 and f"cảnh {seq}" not in warn:
                warn.append(f"cảnh {seq}")
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.concatenate(lines, axis=0)).save(out, quality=88)
    return warn


def check_clip(path: Path, voice: float, speed: float) -> list[tuple[str, str]]:
    info = probe(path)
    streams = info.get("streams", [])
    vs = next((s for s in streams if s.get("codec_type") == "video"), {})
    dur = float(info.get("format", {}).get("duration") or 0.0)
    out = []
    ok = (vs.get("width"), vs.get("height")) == (1080, 1920)
    out.append(("OK" if ok else "FAIL", f"kích thước {vs.get('width')}x{vs.get('height')} (cần 1080x1920)"))
    num, _, den = str(vs.get("avg_frame_rate", "0/1")).partition("/")
    fps = float(num) / float(den or 1) if float(den or 1) else 0.0
    out.append(("OK" if abs(fps - 30) < 0.01 else "FAIL", f"{fps:.2f} fps (cần 30)"))
    has_audio = any(s.get("codec_type") == "audio" for s in streams)
    out.append(("FAIL" if has_audio else "OK", "có rãnh tiếng (cần câm)" if has_audio else "không có tiếng"))
    nums = f"clip {dur:.2f}s / tiếng {voice:.2f}s → sau {speed}x: clip {dur / speed:.2f}s / tiếng {voice / speed:.2f}s"
    if dur >= voice + 0.1:
        out.append(("OK", nums))
    elif dur + HOLD_MAX >= voice:
        out.append(("WARN", nums + f" — hụt, giữ khung cuối ≤ {HOLD_MAX}s hoặc làm lại 1 lần"))
    else:
        out.append(("FAIL", nums + " — ngắn hơn tiếng quá 0,3s, làm lại"))
    return out


def cmd_verify(args) -> int:
    import media_reuse as mr
    folder, out_dir = Path(args.folder), Path(args.out_dir) if args.out_dir else Path(args.folder) / "qa"
    try:
        wanted = [int(x) for x in args.scenes.split(",") if x.strip()]
        segs = segments(folder)
        picked = [(s, segs[s]) for s in wanted]
    except (KeyError, ValueError, OSError) as e:
        print(f"[BROLL FAIL] đọc đầu vào / cảnh không có: {e}", file=sys.stderr)
        return 2
    lib = mr.library_index()
    fails, rows = 0, []
    files = {s: folder / seg["files"]["video_file"] for s, seg in picked}
    for seq, seg in picked:
        path = files[seq]
        if not path.is_file():
            print(f"[FAIL] cảnh {seq}: thiếu {path.name}")
            fails += 1
            continue
        results = check_clip(path, voice_len(folder, seg), args.speed)
        fp = mr.fingerprint(str(path))
        if fp is None:
            results.append(("FAIL", "không lấy được dấu vân tay hình"))
        else:
            others = [(n, f) for n, _c, f in lib] + [(p.name, mr.fingerprint(str(p))) for p in sorted(folder.glob("*_b-roll-*.mp4")) if p != path]
            same = [n for n, f in others if f is not None and mr.distance(f, fp) <= mr.SAME]
            results.append(("FAIL", "trùng clip thư viện / B-roll khác: " + ", ".join(same)) if same else ("OK", "khác mọi clip thư viện và B-roll khác"))
        for st, msg in results:
            print(f"[{st:<4}] cảnh {seq} ({path.name}): {msg}")
            fails += st == "FAIL"
        rows.append((seq, path, duration_of(path)))
    if rows:
        sheet = out_dir / "broll_check_sheet.jpg"
        warn = contact_sheet(rows, sheet)
        print(f"[INFO] ảnh kiểm: {sheet} — hàng theo thứ tự cảnh {[r[0] for r in rows]}, cột 10/30/50/70/90 %.")
        print("[VIỆC BẮT BUỘC] mở ảnh này bằng mắt, ghi lại từng cảnh: hình đúng lời? có chữ/logo không? (không có OCR)")
        if warn:
            print(f"[WARN] heuristic cạnh sắc dày (có thể có chữ/chi tiết nhỏ): {', '.join(warn)} — nhìn kỹ")
    print("ĐẠT" if not fails else f"{fails} lỗi")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ready").set_defaults(fn=cmd_ready)
    p = sub.add_parser("plan")
    p.add_argument("folder")
    p.add_argument("--speed", type=float, default=1.10)
    p.add_argument("--engine", choices=("muse", "flow"), default="muse")
    p.add_argument("--outputs", type=int, default=2, help="số bản Flow mỗi cảnh (x1–x4), mặc định x2")
    p.set_defaults(fn=cmd_plan)
    p = sub.add_parser("lint")
    p.add_argument("folder")
    p.add_argument("--prompts", required=True)
    p.set_defaults(fn=cmd_lint)
    p = sub.add_parser("prepare")
    p.add_argument("folder")
    p.add_argument("--prompts", required=True)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--source", choices=("muse", "flow"), default="muse")
    p.add_argument("--keep-clips", action="store_true",
                   help="chỉ ghi prompt cuối vào manifest / prompts (sau khi đã tạo lại cảnh), không chuyển clip đang dùng")
    p.add_argument("--backup-root", default=str(BACKUP_ROOT))
    p.set_defaults(fn=cmd_prepare)
    p = sub.add_parser("verify")
    p.add_argument("folder")
    p.add_argument("--scenes", required=True, help="seq_index, cách nhau dấu phẩy (VD: 3,4,5)")
    p.add_argument("--speed", type=float, default=1.10)
    p.add_argument("--out-dir")
    p.set_defaults(fn=cmd_verify)
    p = sub.add_parser("normalize")
    p.add_argument("raw")
    p.add_argument("out")
    p.add_argument("--mark", choices=sorted(MARKS), default=None)
    p.set_defaults(fn=cmd_normalize)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
