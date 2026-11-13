#!/usr/bin/env python3
"""
script-aroll-broll-analyzer: render_muse_broll.py

Đọc file `prompts_muse_veo_broll.json` trong Thư mục con kịch bản (hoặc toàn bộ Thư mục tổng)
và gọi trực tiếp API của Muse (`muse2api` chuẩn OpenAI qua `MUSE_BASE_URL` & `MUSE_API_KEY`)
để tạo các phân đoạn video trám cảnh B-Roll:
  - Đầu ra: `<STT>_b-roll-<M>.mp4` (VD: `02_b-roll-1.mp4`, `03_b-roll-2.mp4`) lưu thẳng vào Thư mục con.
  - RULE BẮT BUỘC:
    1. Chỉ tạo video minh họa / motion thuần hình ảnh.
    2. TUYỆT ĐỐI KHÔNG CÓ VOICE (`-an` xoá sạch rãnh âm thanh khi chuẩn hóa H.264).
    3. TUYỆT ĐỐI KHÔNG CÓ TEXT / PHỤ ĐỀ / WATERMARK.
    4. Xoá sạch metadata (`-map_metadata -1`) và chuẩn hóa 1080x1920 @ 30fps BT.709.

Cấu hình API Muse:
  - Đọc từ biến môi trường `MUSE_BASE_URL` và `MUSE_API_KEY`, HOẶC
  - Đọc từ file `~/.config/muse/env`.

Luật v2.5: prompt chưa đạt H5 (tiếng Anh, 8–60 chữ, không chữ/logo…, vd. «Clip thư viện: …») bị TỪ CHỐI trước khi gọi API;
`--shot` khớp chính xác (tên file, tên không đuôi hoặc role_id); thời lượng xin = ceil(tiếng đi cặp + 0,3 s), 2–10 s;
Muse /readyz lỗi = dừng (D3), không có đường thay thế trả phí. Làm lại cảnh sai kịch bản: xem broll_fix.py.
"""
import argparse
import base64
import hashlib
import json
import mimetypes
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from broll_fix import core_of, lint_prompt, request_seconds, voice_len_of

ENV_FILE = Path.home() / ".config/muse/env"
DONE_STATUSES = {"succeeded", "completed"}
FAILED_STATUSES = {"failed", "error", "cancelled", "interrupted", "expired"}

BROLL_STRICT_SUFFIX_EN = (
    "Pure visual footage/motion only, vertical 9:16 (1080x1920), photorealistic, "
    "NO text, NO subtitles, NO captions, NO UI text, NO watermark, muted / NO voice."
)


def load_muse_config() -> Tuple[str, str]:
    """Đọc MUSE_BASE_URL và MUSE_API_KEY từ biến môi trường hoặc ~/.config/muse/env."""
    cfg: Dict[str, str] = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line_s = line.strip()
            if "=" in line_s and not line_s.startswith("#"):
                k, v = line_s.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    base = os.environ.get("MUSE_BASE_URL", cfg.get("MUSE_BASE_URL", "")).rstrip("/")
    key = os.environ.get("MUSE_API_KEY", cfg.get("MUSE_API_KEY", "")).strip()
    if not base or not key:
        raise RuntimeError(
            f"Thiếu cấu hình MUSE_BASE_URL hoặc MUSE_API_KEY (trong biến môi trường hoặc {ENV_FILE})"
        )
    return base, key


def check_muse_ready(base: str) -> bool:
    """Kiểm tra endpoint /readyz của muse2api trước khi gửi job."""
    root = base.rsplit("/v1", 1)[0]
    try:
        with urllib.request.urlopen(f"{root}/readyz", timeout=8) as r:
            data = json.load(r)
            return bool(data.get("ready", True))
    except Exception:
        return False


def muse_call(
    method: str,
    url: str,
    key: str,
    body: Optional[Dict[str, Any]] = None,
    timeout: int = 90,
) -> Dict[str, Any]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"Muse {method} {url} -> HTTP {e.code}: {err}") from e


def muse_wait(poll_url: str, key: str, timeout_s: int = 900) -> Dict[str, Any]:
    start = time.time()
    while time.time() - start < timeout_s:
        task = muse_call("GET", poll_url, key)
        status = task.get("status")
        if status in DONE_STATUSES:
            return task
        if status in FAILED_STATUSES:
            raise RuntimeError(f"Muse task {task.get('id')} thất bại ({status}): {task.get('error')}")
        time.sleep(5)
    raise TimeoutError(f"Muse task quá {timeout_s}s chưa xong: {poll_url}")


def extract_result_url(task: Dict[str, Any]) -> str:
    res = task.get("result") or {}
    if res.get("url"):
        return res["url"]
    items = res.get("data") or []
    if items and items[0].get("url"):
        return items[0]["url"]
    raise RuntimeError(f"Muse task không trả về URL kết quả: {json.dumps(task)[:400]}")


def file_to_data_url(path: Path) -> str:
    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def download_raw_file(url: str, key: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=300) as r:
        dest.write_bytes(r.read())
    return dest


def normalize_broll_video(raw_video: Path, out_video: Path, aspect_ratio: str = "9:16") -> None:
    """
    Chuẩn hóa video B-Roll:
      - Tỷ lệ 9:16 (1080x1920) hoặc 16:9 (1920x1080), 30fps, H.264 BT.709.
      - Xoá toàn bộ âm thanh (-an) để đảm bảo TUYỆT ĐỐI KHÔNG CÓ VOICE.
      - Xoá toàn bộ metadata (-map_metadata -1).
    """
    w, h = (1080, 1920) if aspect_ratio == "9:16" else (1920, 1080)
    vf = (
        f"scale={w}:{h}:force_original_aspect_ratio=increase,"
        f"crop={w}:{h},setsar=1,fps=30,format=yuv420p"
    )
    out_video.parent.mkdir(parents=True, exist_ok=True)
    tmp_out = out_video.with_suffix(".norm.mp4")
    cmd = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-i",
        str(raw_video),
        "-vf",
        vf,
        "-an",
        "-map_metadata",
        "-1",
        "-c:v",
        "libx264",
        "-preset",
        "slow",
        "-crf",
        "12",          # Rule 3 (2026-11-11): ưu tiên chất lượng — CRF 12 slow thay 18 medium
        "-color_primaries",
        "bt709",
        "-color_trc",
        "bt709",
        "-colorspace",
        "bt709",
        "-movflags",
        "+faststart",
        str(tmp_out),
    ]
    subprocess.run(cmd, check=True)
    tmp_out.replace(out_video)


def generate_single_broll(
    base: str,
    key: str,
    prompt_text: str,
    out_video: Path,
    duration_sec: float = 5.0,
    aspect_ratio: str = "9:16",
    mode: str = "image-to-video",
    ref_images: Optional[List[Path]] = None,
    timeout_s: int = 900,
) -> Dict[str, Any]:
    """
    Tạo 1 phân đoạn video B-Roll từ Muse API:
      - Nếu mode == 'image-to-video': tạo ảnh khung đầu 9:16 qua `muse-image` -> tạo video từ ảnh qua `muse-video`.
      - Nếu mode == 'direct-video': tạo thẳng video qua `muse-video`.
    """
    clean_prompt = prompt_text.strip()
    if "NO text" not in clean_prompt and "NO voice" not in clean_prompt:
        clean_prompt = f"{clean_prompt} ({BROLL_STRICT_SUFFIX_EN})"

    # Gắn mã băm ngắn để tránh muse2api trả lại clip trùng trong cache khi prompt gần giống nhau
    shot_tag = hashlib.sha1(f"{out_video}_{clean_prompt}".encode("utf-8")).hexdigest()[:6]
    work_dir = out_video.parent / ".muse_work"
    work_dir.mkdir(parents=True, exist_ok=True)

    first_frame_path: Optional[Path] = None
    image_task_id: Optional[str] = None

    if mode == "image-to-video":
        img_body: Dict[str, Any] = {
            "model": "muse-image",
            "prompt": clean_prompt,
            "size": aspect_ratio,
            "async": True,
        }
        if ref_images:
            img_body["image"] = [file_to_data_url(p) for p in ref_images[:4] if p.exists()]
        img_task = muse_call("POST", f"{base}/images/generations", key, img_body)
        image_task_id = img_task.get("id")
        img_done = muse_wait(f"{base}/images/generations/{image_task_id}", key, timeout_s=timeout_s)
        img_url = extract_result_url(img_done)

        raw_img = work_dir / f"{out_video.stem}_raw_frame"
        download_raw_file(img_url, key, raw_img)
        first_frame_path = work_dir / f"{out_video.stem}_first.png"
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(raw_img), str(first_frame_path)],
            check=True,
        )
        raw_img.unlink(missing_ok=True)

    clamped_seconds = max(2, min(10, int(round(duration_sec))))
    vid_body: Dict[str, Any] = {
        "model": "muse-video",
        "prompt": f"{clean_prompt} (shot {shot_tag})",
        "size": aspect_ratio,
        "seconds": clamped_seconds,
    }
    if first_frame_path and first_frame_path.exists():
        vid_body["image"] = file_to_data_url(first_frame_path)

    vid_task = muse_call("POST", f"{base}/videos", key, vid_body)
    video_task_id = vid_task.get("id")
    vid_done = muse_wait(f"{base}/videos/{video_task_id}", key, timeout_s=timeout_s)
    vid_url = extract_result_url(vid_done)

    raw_vid = work_dir / f"{out_video.stem}.raw.mp4"
    download_raw_file(vid_url, key, raw_vid)
    normalize_broll_video(raw_vid, out_video, aspect_ratio=aspect_ratio)
    raw_vid.unlink(missing_ok=True)

    return {
        "output_file": out_video.name,
        "mode": mode,
        "image_task_id": image_task_id,
        "video_task_id": video_task_id,
        "target_seconds": duration_sec,
        "muse_seconds": clamped_seconds,
        "timestamp": int(time.time()),
    }


def discover_subfolders(target: Path, filter_id: Optional[str] = None) -> List[Path]:
    if (target / "prompts_muse_veo_broll.json").exists():
        return [target]
    subs = sorted(p.parent for p in target.glob("*/prompts_muse_veo_broll.json"))
    if filter_id:
        fid = filter_id.strip().upper()
        subs = [s for s in subs if fid in s.name.upper()]
    return subs


def collect_broll_jobs(
    subfolders: List[Path],
    shot_filter: Optional[str] = None,
    force: bool = False,
) -> List[Tuple[Path, Dict[str, Any]]]:
    jobs: List[Tuple[Path, Dict[str, Any]]] = []
    for sub in subfolders:
        broll_file = sub / "prompts_muse_veo_broll.json"
        if not broll_file.exists():
            continue
        items = json.loads(broll_file.read_text(encoding="utf-8"))
        for item in items:
            out_name = item.get("output_file", "")
            role_id = item.get("role_id", "")
            if shot_filter:
                sf = shot_filter.strip().lower()
                if sf not in {out_name.lower(), Path(out_name).stem.lower(), role_id.lower()}:
                    continue
            out_path = sub / out_name
            if out_path.exists() and out_path.stat().st_size > 10_000 and not force:
                continue
            jobs.append((sub, item))
    return jobs


def job_seconds(sub: Path, item: Dict[str, Any]) -> int:
    """Giây xin Muse = ceil(tiếng đi cặp + 0,3 s) kẹp 2–10; không có file tiếng → duration_target_sec."""
    return request_seconds(voice_len_of(sub / item["paired_voice_file"]) if item.get("paired_voice_file") else 0.0,
                           float(item.get("duration_target_sec", 4.0)))


def h5_problems(jobs: List[Tuple[Path, Dict[str, Any]]]) -> List[str]:
    """Các job có prompt chưa đạt H5 (lint lõi prompt; prompt_core nếu có)."""
    out = []
    for sub, item in jobs:
        core = item.get("prompt_core") or core_of(item.get("prompt_full") or item.get("prompt_vi") or "")
        out += [f"{sub.name}/{item.get('output_file')}: {p}" for p in lint_prompt(core)]
    return out


def muse_ready_or_stop(base: str) -> bool:
    if check_muse_ready(base):
        return True
    print("[D3] Muse /readyz chưa sẵn sàng. Dừng, báo người dùng; KHÔNG chuyển sang dịch vụ trả phí khác.")
    return False


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Tạo video B-Roll (KHÔNG VOICE, KHÔNG TEXT) bằng API Muse từ prompts_muse_veo_broll.json."
    )
    ap.add_argument(
        "target_dir",
        nargs="?",
        type=Path,
        default=None,
        help="Thư mục con của 1 kịch bản HOẶC Thư mục tổng chứa nhiều kịch bản",
    )
    ap.add_argument("--prompt", type=str, default=None, help="Tạo lẻ 1 clip B-Roll từ câu prompt trực tiếp")
    ap.add_argument("-o", "--out", type=Path, default=None, help="Đường dẫn file .mp4 đầu ra khi dùng --prompt")
    ap.add_argument("--seconds", type=float, default=5.0, help="Thời lượng giây khi dùng --prompt (mặc định: 5s)")
    ap.add_argument("--filter-id", type=str, default=None, help="Chỉ lọc theo mã kịch bản (VD: XM01, KB10)")
    ap.add_argument("--shot", type=str, default=None, help="Chỉ chạy 1 shot cụ thể (VD: b-roll-1 hoặc 02_b-roll-1.mp4)")
    ap.add_argument(
        "--mode",
        type=str,
        default="image-to-video",
        choices=["image-to-video", "direct-video"],
        help="Chế độ tạo B-Roll trên Muse: image-to-video (tạo ảnh 9:16 rồi chuyển động) hoặc direct-video",
    )
    ap.add_argument("--aspect-ratio", type=str, default="9:16", choices=["9:16", "16:9", "1:1"])
    ap.add_argument("--ref", nargs="+", type=Path, default=[], help="Ảnh tham chiếu nhân vật/sản phẩm (tối đa 4 ảnh)")
    ap.add_argument("--timeout", type=int, default=900, help="Thời gian chờ tối đa mỗi job (giây)")
    ap.add_argument("--force", action="store_true", help="Render đè cả những file .mp4 đã tồn tại")
    ap.add_argument("--dry-run", action="store_true", help="Chỉ in danh sách các cảnh B-Roll sẽ tạo, không gọi API")
    args = ap.parse_args()

    # Chế độ 1: Tạo lẻ 1 clip B-Roll từ --prompt và -o
    if args.prompt:
        if not args.out:
            print("[ERROR] Khi dùng --prompt cần chỉ rõ đường dẫn file đầu ra qua `-o <file.mp4>`.")
            return 1
        if args.dry_run:
            print(f"[DRY-RUN] Muse B-Roll ({args.mode}, {args.aspect_ratio}, {args.seconds}s) -> {args.out}")
            print(f"          Prompt: {args.prompt}")
            return 0
        base, key = load_muse_config()
        if not muse_ready_or_stop(base):
            return 1
        meta = generate_single_broll(
            base=base,
            key=key,
            prompt_text=args.prompt,
            out_video=args.out,
            duration_sec=args.seconds,
            aspect_ratio=args.aspect_ratio,
            mode=args.mode,
            ref_images=args.ref,
            timeout_s=args.timeout,
        )
        print(f"✅ Đã tạo B-Roll (KHÔNG VOICE, KHÔNG TEXT): {args.out} ({meta})")
        return 0

    # Chế độ 2: Chạy theo Thư mục con / Thư mục tổng có prompts_muse_veo_broll.json
    if not args.target_dir or not args.target_dir.exists():
        print(f"[ERROR] Cần truyền đường dẫn Thư mục con hoặc Thư mục tổng hợp lệ: {args.target_dir}")
        return 1

    subfolders = discover_subfolders(args.target_dir, filter_id=args.filter_id)
    if not subfolders:
        print(f"[ERROR] Không tìm thấy prompts_muse_veo_broll.json trong: {args.target_dir}")
        return 1

    jobs = collect_broll_jobs(subfolders, shot_filter=args.shot, force=args.force)
    total_dur = round(sum(job_seconds(sub, item) for sub, item in jobs), 1)

    print("=" * 80)
    print(f"🎞️ MUSE B-ROLL GENERATOR — {len(jobs)} PHÂN ĐOẠN CẦN RENDER (~{total_dur}s)")
    print(f"   Chế độ tạo : {args.mode} ({args.aspect_ratio})")
    print("   Rule khóa  : KHÔNG VOICE (-an), KHÔNG TEXT / PHỤ ĐỀ / WATERMARK, H.264 30fps BT.709")
    print("=" * 80)

    bad = h5_problems(jobs)
    if bad:
        for b in bad:
            print(f"[H5 FAIL] {b}")
        print("Từ chối render: viết lại prompt tiếng Anh từ lời của cảnh (broll_fix.py plan → lint → prepare). Không gọi API.")
        return 1

    if not jobs:
        print("✅ Tất cả các phân đoạn B-Roll đã được render hoặc không có shot nào khớp bộ lọc.")
        return 0

    for idx, (sub, item) in enumerate(jobs, start=1):
        p_vi = item.get("prompt_vi") or item.get("prompt_full") or ""
        print(
            f"[{idx:02d}/{len(jobs):02d}] {sub.name}/{item['output_file']} "
            f"({item.get('role_id')} · ~{job_seconds(sub, item)}s · Đi cặp: {item.get('paired_voice_file')})"
        )
        print(f"        Prompt: {p_vi[:140]}{'...' if len(p_vi) > 140 else ''}")

    if args.dry_run:
        print("-" * 80)
        print(f"[DRY-RUN] Đã liệt kê {len(jobs)} phân đoạn B-Roll (~{total_dur}s). Bỏ `--dry-run` để chạy thật.")
        return 0

    base, key = load_muse_config()
    if not muse_ready_or_stop(base):
        return 1

    success_count = 0
    for idx, (sub, item) in enumerate(jobs, start=1):
        out_file = sub / item["output_file"]
        prompt_full = item.get("prompt_full") or item.get("prompt_vi") or ""
        dur = job_seconds(sub, item)
        ar = (item.get("rules") or {}).get("aspect_ratio") or args.aspect_ratio

        print(f"\n🚀 [{idx:02d}/{len(jobs):02d}] Đang tạo B-Roll qua Muse ({args.mode}): {sub.name}/{item['output_file']} ...")
        try:
            meta = generate_single_broll(
                base=base,
                key=key,
                prompt_text=prompt_full,
                out_video=out_file,
                duration_sec=dur,
                aspect_ratio=ar,
                mode=args.mode,
                ref_images=args.ref,
                timeout_s=args.timeout,
            )
            size_mb = out_file.stat().st_size / (1024 * 1024)
            print(f"    ✅ Đã lưu B-Roll câm chuẩn H.264: {out_file} ({size_mb:.2f} MB)")
            success_count += 1

            log_path = sub / "muse_render_log.json"
            logs = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
            meta["role_id"] = item.get("role_id")
            logs.append(meta)
            log_path.write_text(json.dumps(logs, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as exc:
            print(f"    ❌ LỖI ở {sub.name}/{item['output_file']}: {exc}")
            return 1

    print("=" * 80)
    print(f"🎉 HOÀN TẤT MUSE B-ROLL: {success_count}/{len(jobs)} file .mp4 đã lưu vào Thư mục con!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
