#!/usr/bin/env python3
"""
script-aroll-broll-analyzer: render_heygen_aroll.py

Đọc file `prompts_heygen_aroll.json` trong Thư mục con kịch bản (hoặc toàn bộ Thư mục tổng)
và gọi trực tiếp API HeyGen (Avatar IV / v3 / v2) để tạo các phân đoạn video A-Roll:
  - Đầu ra: `<STT>_a-roll-<N>.mp4` (VD: `01_a-roll-1.mp4`, `06_a-roll-2.mp4`) đã có sẵn Hình + Tiếng khớp khẩu hình.
  - Tự động bỏ qua các shot đánh dấu `🎥 QUAY THẬT` (`live_shoot`).
  - Tự động kiểm tra câu thoại tiếng Việt (`tts_text`) không còn số / ký hiệu `%`, `/` gây đọc sai.
  - Mặc định chạy ở chế độ `DRY-RUN` (xem trước danh sách shot & câu thoại, KHÔNG tốn Credit HeyGen).
    Thêm cờ `--yes` để thực sự gọi API HeyGen và tải file `.mp4` về đúng Thư mục con.

Cấu hình API Key:
  - Đặt biến môi trường `HEYGEN_API_KEY` (hoặc `HEYGEN_KEY`), HOẶC
  - Lưu trong file `~/.config/heygen/env` (dạng `HEYGEN_API_KEY=sk_...`).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ENV_FILE = Path.home() / ".config/heygen/env"
HEYGEN_BASE = os.environ.get("HEYGEN_API_BASE", "https://api.heygen.com").rstrip("/")

# ── PRESET MẶC ĐỊNH KÊNH ANH HUY (CÓ THỂ GHI ĐÈ QUA CLI / ENV) ──────────────
DEFAULT_AVATAR_ID = os.environ.get("HEYGEN_AVATAR_ID", "761364fad106369de1c3ada3994aee9c")
DEFAULT_VOICE_ID = os.environ.get("HEYGEN_VOICE_ID", "09bed03ed2984542836268ac73ffc18c")
DEFAULT_ASPECT_RATIO = "9:16"
DEFAULT_RESOLUTION = "1080p"
DEFAULT_FIT = "cover"
DEFAULT_EXPRESSIVENESS = "medium"
DEFAULT_MOTION_PROMPT = (
    "A composed business executive speaking directly to camera: natural head turns, "
    "steady eye contact, calm confident posture, subtle shoulder and torso movement "
    "in time with speech."
)


def load_heygen_key() -> str:
    """Đọc API Key của HeyGen từ biến môi trường hoặc ~/.config/heygen/env."""
    cfg: Dict[str, str] = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line_s = line.strip()
            if "=" in line_s and not line_s.startswith("#"):
                k, v = line_s.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    key = (
        os.environ.get("HEYGEN_API_KEY")
        or os.environ.get("HEYGEN_KEY")
        or cfg.get("HEYGEN_API_KEY")
        or cfg.get("HEYGEN_KEY")
        or ""
    ).strip()
    return key


def audit_tts_text(text: str) -> List[str]:
    """Kiểm tra câu thoại gửi HeyGen xem còn số hoặc ký hiệu dễ đọc sai không."""
    issues = []
    if re.search(r"\d", text):
        nums = re.findall(r"\d+(?:[.,:/]\d+)?%?", text)
        issues.append(f"Còn chữ số chưa viết thành chữ: {nums}")
    if "%" in text:
        issues.append("Còn ký hiệu '%' (nên đổi thành 'phần trăm')")
    if "/" in text:
        issues.append("Còn dấu '/' (nên viết thành chữ hoặc tách câu)")
    return issues


def api_request(method: str, path: str, key: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = f"{HEYGEN_BASE}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {
        "X-Api-Key": key,
        "Accept": "application/json",
    }
    if data is not None:
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")[:600]
        raise RuntimeError(f"HeyGen API {method} {path} -> HTTP {e.code}: {err_body}") from e


def submit_heygen_video(
    key: str,
    title: str,
    script_text: str,
    avatar_id: str,
    voice_id: str,
    aspect_ratio: str,
    resolution: str,
    motion_prompt: str,
    api_version: str = "v3",
) -> str:
    """Gửi yêu cầu tạo video A-Roll lên HeyGen v3 (hoặc v2 fallback) và trả về video_id."""
    if api_version == "v2":
        dim = {"width": 1080, "height": 1920} if aspect_ratio == "9:16" else {"width": 1920, "height": 1080}
        if resolution == "720p":
            dim = {"width": 720, "height": 1280} if aspect_ratio == "9:16" else {"width": 1280, "height": 720}
        payload_v2 = {
            "title": title,
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": avatar_id,
                        "avatar_style": "normal",
                    },
                    "voice": {
                        "type": "text",
                        "input_text": script_text,
                        "voice_id": voice_id,
                    },
                }
            ],
            "dimension": dim,
        }
        res = api_request("POST", "/v2/video/generate", key, payload_v2)
        vid = (res.get("data") or {}).get("video_id")
        if not vid:
            raise RuntimeError(f"HeyGen v2 không trả về video_id: {res}")
        return vid

    payload_v3 = {
        "title": title,
        "type": "avatar",
        "avatar_id": avatar_id,
        "voice_id": voice_id,
        "script": script_text,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "fit": DEFAULT_FIT,
    }
    if motion_prompt:
        payload_v3["motion_prompt"] = motion_prompt
    res = api_request("POST", "/v3/videos", key, payload_v3)
    vid = (res.get("data") or {}).get("video_id")
    if not vid:
        raise RuntimeError(f"HeyGen v3 không trả về video_id: {res}")
    return vid


def poll_and_download_heygen(
    key: str,
    video_id: str,
    out_path: Path,
    api_version: str = "v3",
    poll_interval: int = 15,
    timeout_sec: int = 1800,
) -> Dict[str, Any]:
    """Chờ HeyGen render xong, tải về file .mp4 và xoá metadata."""
    start = time.time()
    while time.time() - start < timeout_sec:
        if api_version == "v2":
            res = api_request("GET", f"/v1/video_status.get?video_id={video_id}", key)
        else:
            res = api_request("GET", f"/v3/videos/{video_id}", key)

        data = res.get("data") or {}
        status = data.get("status", "unknown")
        elapsed = int(time.time() - start)
        print(f"    [{elapsed:>4d}s] video_id={video_id} -> status={status}", flush=True)

        if status == "completed":
            video_url = data.get("video_url")
            if not video_url:
                raise RuntimeError(f"HeyGen báo completed nhưng thiếu video_url: {data}")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = out_path.with_suffix(".raw.mp4")
            urllib.request.urlretrieve(video_url, tmp_path)
            # Xoá sạch metadata (strip-media-metadata) và remux faststart
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-v",
                    "error",
                    "-i",
                    str(tmp_path),
                    "-map_metadata",
                    "-1",
                    "-c",
                    "copy",
                    "-movflags",
                    "+faststart",
                    str(out_path),
                ],
                check=True,
            )
            tmp_path.unlink(missing_ok=True)
            return data

        if status in ("failed", "error", "canceled", "cancelled"):
            raise RuntimeError(f"HeyGen render thất bại ({status}): {data.get('error')}")

        time.sleep(poll_interval)

    raise TimeoutError(f"Quá thời gian chờ {timeout_sec}s cho video_id={video_id}")


def discover_subfolders(target: Path, filter_id: Optional[str] = None) -> List[Path]:
    """Tìm danh sách Thư mục con có chứa `prompts_heygen_aroll.json`."""
    if (target / "prompts_heygen_aroll.json").exists():
        return [target]
    subs = sorted(p.parent for p in target.glob("*/prompts_heygen_aroll.json"))
    if filter_id:
        fid = filter_id.strip().upper()
        subs = [s for s in subs if fid in s.name.upper()]
    return subs


def collect_aroll_jobs(
    subfolders: List[Path],
    shot_filter: Optional[str] = None,
    force: bool = False,
) -> List[Tuple[Path, Dict[str, Any]]]:
    """Gom danh sách các phân đoạn A-Roll cần render qua HeyGen."""
    jobs: List[Tuple[Path, Dict[str, Any]]] = []
    for sub in subfolders:
        aroll_file = sub / "prompts_heygen_aroll.json"
        if not aroll_file.exists():
            continue
        items = json.loads(aroll_file.read_text(encoding="utf-8"))
        # Kiểm tra thêm trong 00_storyboard_manifest.json để chắc chắn không gọi HeyGen cho shot live_shoot
        live_shoot_files = set()
        manifest_file = sub / "00_storyboard_manifest.json"
        if manifest_file.exists():
            mdata = json.loads(manifest_file.read_text(encoding="utf-8"))
            for seg in mdata.get("segments", []):
                routing = seg.get("api_routing") or {}
                if routing.get("video_generator") == "live_shoot":
                    vf = (seg.get("files") or {}).get("video_file")
                    if vf:
                        live_shoot_files.add(vf)

        for item in items:
            out_name = item.get("output_file", "")
            role_id = item.get("role_id", "")
            if out_name in live_shoot_files or item.get("video_generator") == "live_shoot":
                continue
            if shot_filter:
                sf = shot_filter.strip().lower()
                if sf not in out_name.lower() and sf != role_id.lower():
                    continue
            out_path = sub / out_name
            if out_path.exists() and out_path.stat().st_size > 10_000 and not force:
                continue
            jobs.append((sub, item))
    return jobs


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Tạo video A-Roll từ prompts_heygen_aroll.json bằng API HeyGen."
    )
    ap.add_argument(
        "target_dir",
        type=Path,
        help="Đường dẫn Thư mục con của 1 kịch bản HOẶC Thư mục tổng chứa nhiều kịch bản",
    )
    ap.add_argument("--filter-id", type=str, default=None, help="Chỉ lọc theo mã kịch bản (VD: XM01, KB10)")
    ap.add_argument("--shot", type=str, default=None, help="Chỉ chạy 1 shot cụ thể (VD: a-roll-2 hoặc 06_a-roll-2.mp4)")
    ap.add_argument("--avatar-id", type=str, default=DEFAULT_AVATAR_ID, help="HeyGen Avatar ID")
    ap.add_argument("--voice-id", type=str, default=DEFAULT_VOICE_ID, help="HeyGen Voice ID")
    ap.add_argument("--aspect-ratio", type=str, default=DEFAULT_ASPECT_RATIO, choices=["9:16", "16:9", "1:1"])
    ap.add_argument("--resolution", type=str, default=DEFAULT_RESOLUTION, choices=["720p", "1080p"])
    ap.add_argument("--motion-prompt", type=str, default=DEFAULT_MOTION_PROMPT, help="Motion prompt cho Avatar IV")
    ap.add_argument("--api-version", type=str, default="v3", choices=["v3", "v2"], help="HeyGen endpoint version")
    ap.add_argument("--force", action="store_true", help="Render đè cả những file .mp4 đã tồn tại")
    ap.add_argument(
        "--yes",
        action="store_true",
        help="Xác nhận gọi API HeyGen thật (tốn Credit). Nếu không truyền --yes, script chỉ chạy DRY-RUN.",
    )
    args = ap.parse_args()

    if not args.target_dir.exists():
        print(f"[ERROR] Đường dẫn không tồn tại: {args.target_dir}")
        return 1

    subfolders = discover_subfolders(args.target_dir, filter_id=args.filter_id)
    if not subfolders:
        print(f"[ERROR] Không tìm thấy prompts_heygen_aroll.json trong: {args.target_dir}")
        return 1

    jobs = collect_aroll_jobs(subfolders, shot_filter=args.shot, force=args.force)
    total_dur = round(sum(float(item.get("duration_hint_sec", 3.5)) for _, item in jobs), 1)

    print("=" * 80)
    print(f"🎬 HEYGEN A-ROLL GENERATOR — {len(jobs)} PHÂN ĐOẠN CẦN RENDER (~{total_dur}s)")
    print(f"   Avatar ID : {args.avatar_id}")
    print(f"   Voice ID  : {args.voice_id}")
    print(f"   Định dạng : {args.aspect_ratio} @ {args.resolution} ({args.api_version})")
    print("=" * 80)

    if not jobs:
        print("✅ Tất cả các phân đoạn A-Roll (HeyGen) đã được render hoặc không có shot nào khớp bộ lọc.")
        return 0

    warnings_count = 0
    for idx, (sub, item) in enumerate(jobs, start=1):
        tts = item.get("tts_text", "").strip()
        issues = audit_tts_text(tts)
        print(
            f"[{idx:02d}/{len(jobs):02d}] {sub.name}/{item['output_file']} "
            f"({item.get('role_id')} · ~{item.get('duration_hint_sec', 0)}s)"
        )
        print(f"        TTS: \"{tts}\"")
        if issues:
            warnings_count += len(issues)
            for iss in issues:
                print(f"        ⚠️ CẢNH BÁO TTS: {iss}")

    if not args.yes:
        print("-" * 80)
        print(
            f"[DRY-RUN] Chưa gọi API HeyGen (0 Credit tiêu tốn). "
            f"Tổng cộng {len(jobs)} shot (~{total_dur}s), {warnings_count} cảnh báo TTS."
        )
        print("👉 Để thực sự gọi API HeyGen và tải video A-Roll về thư mục con, hãy thêm cờ `--yes`.")
        return 0

    key = load_heygen_key()
    if not key:
        print(
            f"[ERROR] Thiếu HEYGEN_API_KEY / HEYGEN_KEY trong biến môi trường hoặc {ENV_FILE}."
        )
        return 1

    success_count = 0
    for idx, (sub, item) in enumerate(jobs, start=1):
        out_file = sub / item["output_file"]
        title = f"{sub.name}_{Path(item['output_file']).stem}"
        tts = item.get("tts_text", "").strip()
        print(f"\n🚀 [{idx:02d}/{len(jobs):02d}] Đang gửi HeyGen: {sub.name}/{item['output_file']} ...")
        try:
            vid = submit_heygen_video(
                key=key,
                title=title,
                script_text=tts,
                avatar_id=args.avatar_id,
                voice_id=args.voice_id,
                aspect_ratio=args.aspect_ratio,
                resolution=args.resolution,
                motion_prompt=args.motion_prompt,
                api_version=args.api_version,
            )
            print(f"    Đã tạo task HeyGen: video_id={vid}")
            meta = poll_and_download_heygen(
                key=key,
                video_id=vid,
                out_path=out_file,
                api_version=args.api_version,
            )
            size_mb = out_file.stat().st_size / (1024 * 1024)
            print(f"    ✅ Đã lưu: {out_file} ({size_mb:.2f} MB)")
            success_count += 1

            # Ghi nhật ký vào thư mục con
            log_path = sub / "heygen_render_log.json"
            logs = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
            logs.append(
                {
                    "output_file": item["output_file"],
                    "role_id": item.get("role_id"),
                    "video_id": vid,
                    "duration_sec": meta.get("duration"),
                    "timestamp": int(time.time()),
                }
            )
            log_path.write_text(json.dumps(logs, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as exc:
            print(f"    ❌ LỖI ở {sub.name}/{item['output_file']}: {exc}")
            return 1

    print("=" * 80)
    print(f"🎉 HOÀN TẤT HEYGEN A-ROLL: {success_count}/{len(jobs)} file .mp4 đã lưu vào Thư mục con!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
