#!/usr/bin/env python3
"""Làm lại B-roll sai kịch bản (D9) bằng Muse theo luật H5/D3/D8: kiểm → sao lưu → viết prompt → render → xác minh.

    PY=~/.venvs/video-skills/bin/python
    $PY broll_fix.py ready                                        # chỉ GET /readyz; chưa sẵn sàng → báo D3, mã thoát 1, KHÔNG dùng dịch vụ khác
    $PY broll_fix.py plan    <thư mục kịch bản> [--speed 1.10] [--engine muse|flow] [--outputs 2]   # cảnh B-roll + giây cần xin (+ tín dụng Flow)
    $PY broll_fix.py lint    <thư mục> --prompts broll_new_prompts.json
    $PY broll_fix.py prepare <thư mục> --prompts broll_new_prompts.json [--source muse|flow] [--keep-clips] [--dry-run] [--backup-root DIR]
                                                                  # --keep-clips: tạo lại cảnh xong → ghi prompt cuối, giữ clip
    $PY broll_fix.py mcp-jobs <thư mục> --inspect inspect.json [--speed 1.10] [--versions 2] [--scenes 3,4]
                                                                  # in MỘT danh sách JSON đối số flow_generate_video (D-b) cho từng cảnh B-roll; inspect.json = kết quả flow_inspect_account
    $PY broll_fix.py verify  <thư mục> --scenes 3,4,5 [--speed 1.10] [--out-dir DIR]
    $PY broll_fix.py normalize <file tải về> <thư mục>/NN_b-roll-M.mp4 [--mark flow]   # clip tạo ngoài Muse (Google Flow…) → chuẩn skill

mcp-jobs (3.5.1): prompt = lõi prompt đã lưu bởi `prepare --source flow` (không đuôi), giây = flow_seconds như `plan --engine flow`; durationSeconds / outputs / aspectRatio / model / upscale
chỉ lấy giá trị inspect liệt kê (thiếu → ui-default / highest_available / bỏ durationSeconds + `_note`); x2 không được Flow cho phép → tách `--versions` job outputs=1 (fileName …_v1, …_v2).
inspect.json thiếu / hỏng → mã thoát 2.

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
from datetime import datetime, timezone
import json
import math
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from pathlib import Path

MIN_WORDS, MAX_WORDS = 8, 95
MAX_MUSE_SEC, MIN_MUSE_SEC = 10, 2
VOICE_PAD = 0.3                    # xin dài hơn tiếng 0,3 s
HOLD_MAX = 0.3                     # được giữ khung cuối tối đa 0,3 s
SUFFIX_MARK = " (Pure visual"      # phần đuôi cố định BROLL_STRICT_SUFFIX_EN nối sau lõi prompt
SHEET_PCTS = (0.10, 0.30, 0.50, 0.70, 0.90)
BACKUP_ROOT = Path.home() / ".cache" / "opa-video-studio" / "backup"

LAYER_KEYS = ("l1_shot_subject", "l2_action_script", "l3_environment", "l4_optics_realism", "l5_camera_motion")

BANNED_RE = re.compile(
    r"\b(?:texts?|captions?|subtitles?|signs?|logos?|numbers?|charts?|dashboards?|ui|chat|apps?|labels?|posters?"
    r"|brands?|brand names?"
    r"|notes?|checklists?|checkbox(?:es)?|written|bullets?|handwritten|handwriting"
    r"|chatting|messages?|messaging|texting"
    r"|side-by-side|comparison|graphs?|metrics|analytics|statistics|engagement"
    r"|youtube|tiktok|facebook|instagram|iphone|macbook|apple|samsung|google)\b|writing on paper",
    re.I,
)
ANTI_SLOP_WORDS = (
    "stunning", "breathtaking", "hyper-detailed", "hyperdetailed",
    "8k masterpiece", "4k masterpiece", "photorealistic masterpiece",
    "8k", "4k", "masterpiece", "magical", "very realistic",
    "ultra-realistic", "ultra realistic", "photorealistic",
    "award-winning", "best quality",
)
ANTI_SLOP_RE = re.compile(
    r"(?<!\w)(?:" + "|".join(re.escape(w) for w in sorted(ANTI_SLOP_WORDS, key=len, reverse=True)) + r")(?!\w)",
    re.I,
)
PLASTIC_AI_WORDS = (
    "3d render", "cgi", "unreal engine", "octanerender", "octane", "blender render",
    "glowing prism", "amber prism", "frosted-glass gears", "hologram", "holographic",
    "cyberpunk", "neon cyber", "futuristic glowing", "glowing nodes", "floating icons",
    "pipeline rail", "parallel steel tracks", "sci-fi", "plastic sheen", "porcelain skin",
    "rubbery", "energy core",
)
PLASTIC_AI_RE = re.compile(
    r"(?<!\w)(?:" + "|".join(re.escape(w) for w in sorted(PLASTIC_AI_WORDS, key=len, reverse=True)) + r")(?!\w)",
    re.I,
)
WEIGHT_SYNTAX_RE = re.compile(r"\([^()]+:\s*\d+(?:\.\d+)?\)|(?<!\w)\w+::\s*-?\d+(?:\.\d+)?")
NEGATIVE_TAIL_RE = re.compile(r"\b(?:no texts?|no subtitles?|no watermarks?|no logos?)\b", re.I)
CAMERA_MOTION_RE = re.compile(
    r"\b(?:dolly|push[- ]in|pull[- ]back|tracking|orbit|pan|whip[- ]pan|whip[- ]tilt|"
    r"tilt|handheld|static|tripod|drift|arc|crane|zoom|gimbal|steadicam)\b",
    re.I,
)
REALISM_CUE_RE = re.compile(
    r"(?<!\w)(?:35mm|50mm|24mm|85mm|documentary|handheld|film grain|grain|"
    r"shallow depth of field|shallow focus|window light|daylight|overcast|"
    r"tungsten|warm lamp|natural light|skin texture|micro-pores|pores|"
    r"flyaway|matte|cotton|linen|wooden|ceramic|desaturated|candid|"
    r"f/(?:\d+(?:\.\d+)?)?)(?!\w)",
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


def assemble_layered_prompt(layers: dict) -> str:
    """Ghép 5 tầng H5 (L1..L5) thành chuỗi prompt tiếng Anh liền mạch."""
    if not isinstance(layers, dict):
        raise ValueError("layers phải là object JSON gồm 5 khoá L1..L5")
    parts: list[str] = []
    for k in LAYER_KEYS:
        val = layers.get(k)
        if isinstance(val, str) and val.strip():
            parts.append(val.strip())
    if not parts:
        return ""
    out = parts[0]
    for p in parts[1:]:
        if out.endswith((".", "!", "?")):
            out = f"{out} {p}"
        else:
            out = f"{out.rstrip(',;')}, {p}"
    if not out.endswith((".", "!", "?")):
        out += "."
    return out


def resolve_entry_prompt(entry: dict) -> str:
    """Lấy prompt từ trường `prompt`, hoặc tự ghép từ `layers` nếu chưa ghi `prompt`."""
    raw = str(entry.get("prompt") or "").strip()
    if raw:
        return raw
    layers = entry.get("layers")
    if isinstance(layers, dict):
        return assemble_layered_prompt(layers)
    return ""


def _lint_layers(layers: dict) -> list[str]:
    if not isinstance(layers, dict):
        return ["layers phải là object JSON gồm 5 khoá L1..L5"]
    problems: list[str] = []
    missing = [k for k in LAYER_KEYS if not isinstance(layers.get(k), str) or not layers[k].strip()]
    if missing:
        problems.append("layers thiếu hoặc rỗng: " + ", ".join(missing))
    diacritics = [k for k in LAYER_KEYS if isinstance(layers.get(k), str) and layers[k].strip() and has_diacritics(layers[k])]
    if diacritics:
        problems.append("layers có dấu tiếng Việt: " + ", ".join(diacritics))
    return problems


def lint_prompt(
    core: str,
    tts_text: str | None = None,
    anchor: str | None = None,
    *,
    strict_layers: bool = False,
    layers: dict | None = None,
) -> list[str]:
    """Luật H5 cho lõi prompt B-roll → danh sách lỗi (rỗng = đạt)."""
    core = (core or "").strip()
    if not core and isinstance(layers, dict):
        core = assemble_layered_prompt(layers)
    if not core:
        problems = ["prompt rỗng"]
        if layers is not None:
            problems.extend(_lint_layers(layers))
        return problems
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
    anti_slop = sorted({m.group(0).lower() for m in ANTI_SLOP_RE.finditer(core)})
    if anti_slop:
        problems.append("chứa từ sáo rỗng (Anti-Slop): " + ", ".join(anti_slop))
    plastic = sorted({m.group(0).lower() for m in PLASTIC_AI_RE.finditer(core)})
    if plastic:
        problems.append("chứa từ khoá CGI/nhựa lộ AI: " + ", ".join(plastic))
    weights = [m.group(0) for m in WEIGHT_SYNTAX_RE.finditer(core)]
    if weights:
        problems.append("chứa cú pháp trọng số CLIP (cấm): " + ", ".join(weights[:3]))
    neg_tail = sorted({m.group(0).lower() for m in NEGATIVE_TAIL_RE.finditer(core)})
    if neg_tail:
        problems.append("chứa cụm phủ định (no text/logo/watermark — Flow dễ hiểu ngược): " + ", ".join(neg_tail))
    if SCREEN_RE.search(core) and not SCREEN_OK_RE.search(core):
        problems.append("có màn hình / laptop / bảng / giấy nhưng không ghi out of frame / out of focus / blurred / blank")
    if PERSON_RE.search(core) and "vietnamese" not in core.lower():
        problems.append("có người nhưng chưa ghi Vietnamese (kênh Việt — không ghi thì AI ra người phương Tây)")
    if MULTI_SHOT_RE.search(core):
        problems.append("nhiều cảnh / ghi chú hậu kỳ trong một clip (transition, cut, montage, PiP, overlay) — một clip một cảnh liền")
    if SPEAKER_RE.search(core) and not FACELESS_RE.search(core):
        problems.append("có founder / người nói nhưng không giấu mặt (from behind / over the shoulder / hands / silhouette)")
    if layers is not None:
        problems.extend(_lint_layers(layers))
    if strict_layers:
        if not CAMERA_MOTION_RE.search(core):
            problems.append("thiếu chuyển động camera rõ ràng (dolly, push-in, pull-back, tracking, orbit, pan, tilt, handheld, static, tripod, drift, arc, crane)")
        if not REALISM_CUE_RE.search(core):
            problems.append("thiếu chỉ dấu quang học / chất liệu đời thực chống nhựa (35mm, 50mm, shallow depth of field, window light, daylight, film grain, skin texture, wooden, matte, cotton)")
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


def lint_new(folder: Path, new: list[dict], *, strict_layers: bool = True) -> list[str]:
    segs, out = segments(folder), []
    for e in new:
        seg = segs.get(e.get("seq"))
        if seg is None:
            out.append(f"cảnh {e.get('seq')}: không có b-roll này trong manifest")
            continue
        if "script_beat_vi" in e:
            beat = e["script_beat_vi"]
            if not isinstance(beat, str) or not beat.strip():
                out.append(f"cảnh {e['seq']}: script_beat_vi phải là chuỗi không rỗng")
        layers = e.get("layers")
        core = resolve_entry_prompt(e)
        out += [
            f"cảnh {e['seq']}: {p}"
            for p in lint_prompt(
                core,
                seg.get("tts_text", ""),
                e.get("anchor_quote"),
                strict_layers=strict_layers,
                layers=layers,
            )
        ]
    return out


def cmd_lint(args) -> int:
    strict = not getattr(args, "no_strict_layers", False)
    try:
        problems = lint_new(Path(args.folder), _read_new(Path(args.prompts)), strict_layers=strict)
    except (OSError, ValueError, KeyError) as e:
        print(f"[BROLL FAIL] đọc đầu vào: {e}", file=sys.stderr)
        return 2
    for p in problems:
        print(f"[H5 FAIL] {p}")
    print("[H5 OK] mọi prompt đạt" if not problems else f"{len(problems)} lỗi H5")
    return 1 if problems else 0


# ---------------------------------------------------------------- prepare
# ---------------------------------------------------------------- mcp-jobs (D-b)
OMNI_12_FLASH_RE = re.compile(r"omni.*1[.-]2.*flash", re.I)
OMNI_FLASH_RE = re.compile(r"omni.*flash", re.I)
NOTE_NO_DURATION = "duration not settable — check length after download"


def _as_int(v) -> int | None:
    """Số nguyên từ 8 / '8' / '8s' / 'x2' / {'id': ...}; không đọc được → None."""
    if isinstance(v, dict):
        v = v.get("id", v.get("value", v.get("label")))
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return int(v)
    m = re.search(r"\d+", str(v or ""))
    return int(m.group()) if m else None


def _video_list(insp: dict, *path: str) -> list:
    """insp[path0][path1]… nếu là list; thiếu / sai kiểu → [] (coi như không liệt kê)."""
    cur = insp
    for key in path:
        cur = cur.get(key) if isinstance(cur, dict) else None
    return cur if isinstance(cur, list) else []


def _opt_text(v) -> tuple[str, str]:
    """(id, label) của một phần tử inspect: chuỗi hoặc {id, label}."""
    if isinstance(v, dict):
        return str(v.get("id") or ""), str(v.get("label") or "")
    return str(v), str(v)


def pick_video_model(insp: dict) -> str:
    models = [_opt_text(m) for m in _video_list(insp, "models", "video")]
    for rx in (OMNI_12_FLASH_RE, OMNI_FLASH_RE):
        for mid, label in models:
            if mid and (rx.search(mid) or rx.search(label)):
                return mid
    return "ui-default"


def pick_duration(secs: int, listed: list[int]) -> int | None:
    if secs in listed:
        return secs
    bigger = [d for d in listed if d >= secs]
    return min(bigger) if bigger else None


def mcp_job_args(insp: dict, name: str, out_dir: Path, prompt: str, secs: int, versions: int) -> list[dict]:
    """Đối số flow_generate_video cho một cảnh: một job outputs=versions nếu Flow cho, ngược lại `versions` job outputs=1."""
    ratios = [str(x) for x in _video_list(insp, "aspectRatiosByMedia", "video")]
    counts = [n for n in map(_as_int, _video_list(insp, "outputCountsByMedia", "video")) if n is not None]
    durations = [n for n in map(_as_int, _video_list(insp, "visibleDurations")) if n is not None]
    upscales = [_opt_text(u)[0].lower() for u in _video_list(insp, "availableUpscales")]
    base = {"prompt": prompt, "outputDirectory": str(out_dir), "aspectRatio": "9:16" if "9:16" in ratios else "ui-default",
            "model": pick_video_model(insp)}
    dur = pick_duration(secs, durations)
    if dur is not None:
        base["durationSeconds"] = dur
    else:
        base["_note"] = NOTE_NO_DURATION
    tail = {"upscale": "1080p" if "1080p" in upscales else "highest_available", "download": True,
            "referenceFiles": [], "confirmCreditSpend": True}
    if versions <= 1 or versions in counts:
        return [{**base, "fileName": f"{name}_raw", "outputs": max(1, versions), **tail}]
    return [{**base, "fileName": f"{name}_raw_v{i}", "outputs": 1, **tail} for i in range(1, versions + 1)]


def cmd_mcp_jobs(args) -> int:
    folder = Path(args.folder)
    try:
        insp = _load(Path(args.inspect))
        if not isinstance(insp, dict):
            raise ValueError("phải là một object JSON (kết quả flow_inspect_account)")
    except (OSError, ValueError) as e:
        print(f"[BROLL FAIL] không đọc được file inspect {args.inspect}: {e}. Chạy flow_inspect_account rồi lưu kết quả JSON vào file này.", file=sys.stderr)
        return 2
    try:
        segs = segments(folder)
        prompts = {i.get("seq_index"): i for i in _load(folder / "prompts_muse_veo_broll.json")}
    except (OSError, ValueError, KeyError) as e:
        print(f"[BROLL FAIL] đọc manifest / prompts trong {folder}: {e}", file=sys.stderr)
        return 2
    wanted = None
    if args.scenes:
        try:
            wanted = [int(x) for x in args.scenes.split(",") if x.strip()]
        except ValueError:
            print(f"[BROLL FAIL] --scenes phải là các seq_index cách nhau dấu phẩy, nhận '{args.scenes}'", file=sys.stderr)
            return 2
        unknown = [q for q in wanted if q not in segs]
        if unknown:
            print(f"[BROLL FAIL] không có cảnh B-roll {unknown}", file=sys.stderr)
            return 2
    jobs: list[dict] = []
    for seq in (wanted if wanted is not None else sorted(segs)):
        seg, item = segs[seq], prompts.get(seq) or {}
        prompt = (item.get("prompt_core") or core_of(item.get("prompt_full") or "")
                  or seg.get("visual_direction") or core_of(seg.get("broll_prompt") or "")).strip()
        stem = Path((seg.get("files") or {}).get("video_file") or f"{seg.get('seq_prefix', f'{seq:02d}')}_{seg['role_id']}.mp4").stem
        secs = flow_seconds(voice_len(folder, seg), float(seg.get("duration_sec") or 4.0))
        jobs += mcp_job_args(insp, stem, folder / "_google_raw", prompt, secs, args.versions)
    print(json.dumps(jobs, ensure_ascii=False, indent=2))
    return 0


def _backup_dir(root: Path, folder: Path) -> Path:
    base = root / time.strftime("%Y-%m-%d") / folder.name
    return base if not base.exists() else base.with_name(f"{base.name}_{time.strftime('%H%M%S')}")


def _stale_files(folder: Path, video_file: str) -> list[Path]:
    stem = Path(video_file).stem
    rx = re.compile(rf"^{re.escape(stem)}(_x\d{{3}})?\.[A-Za-z0-9]+$")
    found = [folder / video_file] if (folder / video_file).exists() else []
    found += [p for d in sorted((folder / "media").glob("x*")) if d.is_dir() for p in sorted(d.iterdir()) if rx.match(p.name)]
    return found


def build_item(old: dict, entry: dict, voice: float, backup: Path, source: str = "flow") -> dict:
    import render_muse_broll as rmb
    core = resolve_entry_prompt(entry)
    fallback = float(old.get("duration_target_sec", 4.0))
    flow = source == "flow"
    item = {k: v for k, v in old.items() if k != "prompt_vi"}
    item.update({"prompt_core": core, "prompt_full": core if flow else f"{core} ({rmb.BROLL_STRICT_SUFFIX_EN})",
                 "anchor_quote": entry["anchor_quote"],
                 "duration_target_sec": flow_seconds(voice, fallback) if flow else request_seconds(voice, fallback),
                 "source": source, "regen_of": old.get("prompt_full") or old.get("prompt_vi"), "backup": str(backup)})
    if isinstance(entry.get("layers"), dict):
        item["layers"] = entry["layers"]
    else:
        item.pop("layers", None)
    if isinstance(entry.get("script_beat_vi"), str) and entry["script_beat_vi"].strip():
        item["script_beat_vi"] = entry["script_beat_vi"].strip()
    else:
        item.pop("script_beat_vi", None)
    return item


def cmd_prepare(args) -> int:
    folder = Path(args.folder)
    strict = not getattr(args, "no_strict_layers", False)
    try:
        new = _read_new(Path(args.prompts))
        problems = lint_new(folder, new, strict_layers=strict)
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
        resolved = resolve_entry_prompt(e)
        new_seg = {**s, "broll_prompt": full_by_seq[s["seq_index"]], "visual_direction": resolved,
                   "broll_source": args.source, "regen_history": hist}
        if isinstance(e.get("layers"), dict):
            new_seg["broll_layers"] = e["layers"]
        else:
            new_seg.pop("broll_layers", None)
        if isinstance(e.get("script_beat_vi"), str) and e["script_beat_vi"].strip():
            new_seg["script_beat_vi"] = e["script_beat_vi"].strip()
        else:
            new_seg.pop("script_beat_vi", None)
        new_segments.append(new_seg)
    _save(prompts_p, new_items)
    _save(manifest_p, {**manifest, "segments": new_segments})
    if md_p.exists():
        text = md_p.read_text(encoding="utf-8")
        for seq, old in old_vd.items():
            if old and old in text:
                text = text.replace(old, resolve_entry_prompt(by_seq[seq]))
        md_p.write_text(text, encoding="utf-8")
    nxt = ("tạo trong Google Flow theo references/flow-broll.md, rồi normalize (--mark flow khi bản tải về có dấu)" if args.source == "flow"
           else "render_muse_broll.py <thư mục> --shot <NN_b-roll-M.mp4> cho từng cảnh")
    print(f"Đã cập nhật prompts_muse_veo_broll.json + manifest (nguồn {args.source}). Kế tiếp: {nxt}.")
    return 0


# ---------------------------------------------------------------- verify
MARKS = {"flow": "delogo=x=845:y=1685:w=110:h=110"}   # dấu ngôi sao Google Flow, toạ độ trên khung 1080x1920
BROLL_SOURCES = ("flow", "real_footage", "stock", "muse")


def infer_broll_source(raw: Path, mark: str | None = None, source: str | None = None) -> str:
    """Suy nguồn B-roll khi `normalize` không truyền `--source`."""
    if source:
        return source
    raw_l = unicodedata.normalize("NFC", str(raw)).lower().replace("\\", "/")
    fname_l = Path(raw_l).name
    if mark == "flow" or "_google_raw" in raw_l or "/flow/" in raw_l:
        return "flow"
    if any(k in raw_l for k in ("06_b-roll", "stock_theo_chu_de", "mixkit", "pexels", "pixabay", "/ftg_")) or fname_l.startswith("ftg_"):
        return "stock"
    if any(k in raw_l for k in ("soucre thô", "source_tho", "04_footage", "footage_studio", "_studio.mp4")):
        return "real_footage"
    return "unknown"


def _record_broll_source(raw: Path, out: Path, kind: str, mark: str | None) -> None:
    src_file = out.parent / "_broll_sources.json"
    try:
        data = _load(src_file) if src_file.is_file() else {}
        if not isinstance(data, dict):
            data = {}
    except (OSError, ValueError):
        data = {}
    data[out.name] = {
        "source": kind,
        "raw": str(raw),
        "mark": mark,
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    _save(src_file, data)
    man_file = out.parent / "00_storyboard_manifest.json"
    if man_file.is_file() and kind != "unknown":
        try:
            man = _load(man_file)
            changed = False
            for seg in man.get("segments", []):
                vf = (seg.get("files") or {}).get("video_file") or ""
                if vf and Path(vf).name == out.name and seg.get("broll_source") != kind:
                    seg["broll_source"] = kind
                    changed = True
            if changed:
                _save(man_file, man)
        except (OSError, ValueError):
            pass


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


def normalize(raw: str | Path, out: str | Path, mark: str | None = None, source: str | None = None) -> int:
    raw, out = Path(raw), Path(out)
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
    if mark:
        filters.append(MARKS[mark])
    filters.append("setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709")
    vf = ",".join(filters)
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-an", "-vf", vf, "-c:v", "libx264", "-crf", "12", "-preset", "slow",
           "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-movflags", "+faststart", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if r.returncode != 0 or not out.is_file():
        print(f"LỖI ffmpeg: {r.stderr.strip()[-400:]}")
        return 1
    kind = infer_broll_source(raw, mark=mark, source=source)
    _record_broll_source(raw, out, kind, mark)
    notes = [x for x in (trimmed, f"đã xoá dấu {mark}" if mark else None, f"nguồn {kind}") if x]
    suffix = f", {', '.join(notes)}" if notes else ""
    print(f"OK {out.name}: 1080x1920 30 fps, không tiếng{suffix} ({duration_of(out):.2f} s)")
    return 0


def cmd_normalize(args) -> int:
    return normalize(args.raw, args.out, mark=getattr(args, "mark", None), source=getattr(args, "source", None))


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
    p.add_argument("--engine", choices=("muse", "flow"), default="flow")
    p.add_argument("--outputs", type=int, default=2, help="số bản Flow mỗi cảnh (x1–x4), mặc định x2")
    p.set_defaults(fn=cmd_plan)
    p = sub.add_parser("mcp-jobs")
    p.add_argument("folder")
    p.add_argument("--inspect", required=True, help="JSON kết quả flow_inspect_account")
    p.add_argument("--speed", type=float, default=1.10)
    p.add_argument("--versions", type=int, default=2, help="số bản mỗi cảnh, mặc định 2")
    p.add_argument("--scenes", help="seq_index cách nhau dấu phẩy; mặc định mọi cảnh B-roll")
    p.set_defaults(fn=cmd_mcp_jobs)
    p = sub.add_parser("lint")
    p.add_argument("folder")
    p.add_argument("--prompts", required=True)
    p.add_argument("--no-strict-layers", action="store_true",
                   help="tắt kiểm tra bắt buộc camera motion và chỉ dấu quang học/chất liệu đời thực")
    p.set_defaults(fn=cmd_lint)
    p = sub.add_parser("prepare")
    p.add_argument("folder")
    p.add_argument("--prompts", required=True)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--source", choices=("muse", "flow"), default="flow")
    p.add_argument("--keep-clips", action="store_true",
                   help="chỉ ghi prompt cuối vào manifest / prompts (sau khi đã tạo lại cảnh), không chuyển clip đang dùng")
    p.add_argument("--no-strict-layers", action="store_true",
                   help="tắt kiểm tra bắt buộc camera motion và chỉ dấu quang học/chất liệu đời thực")
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
    p.add_argument("--source", choices=BROLL_SOURCES, default=None)
    p.set_defaults(fn=cmd_normalize)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
