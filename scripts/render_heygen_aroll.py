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

Nhiều góc quay (look): mỗi shot có thể mang `avatar_id` (= look id) trong prompts_heygen_aroll.json;
`--looks looks.json --assign auto` tự chia look cho shot chưa có (xem heygen_looks.py).
Ngân hàng A-roll dùng lại: `--bank bank.json` render mỗi câu một lần vào bank/<bank_id>.mp4,
rồi `link bank.json <thư mục tổng>` chép/symlink vào từng thư mục video theo `bank_id` trong prompts.

Cấu hình API Key (KHÔNG bao giờ ghi ra file/log):
  - Biến môi trường `HEYGEN_API_KEY`, HOẶC `--key-file <file>` do người dùng đưa lúc chạy.
"""
import argparse
import shutil
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import heygen_looks  # noqa: E402
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


def load_heygen_key(key_file: Optional[Path] = None) -> str:
    """Khoá API: --key-file hoặc biến môi trường HEYGEN_API_KEY (không đọc nơi nào khác)."""
    return heygen_looks.load_key(key_file)


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
    engine: Optional[str] = None,
    background: Any = None,
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
    if engine:
        payload_v3["engine"] = engine
    if background:
        payload_v3["background"] = background
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




# ── NHIỀU GÓC (LOOK) ────────────────────────────────────────────────────────
def auto_assign(subfolders: List[Path], look_ids: List[str], n_angles: int = 3) -> Dict[Tuple[str, str], str]:
    """Chia look cho MỌI shot A-roll (kể cả shot đã render, để kết quả không đổi khi chạy lại/resume),
    cân bằng cả lô nhiều video. Khoá: (tên thư mục video, output_file)."""
    counts: Dict[str, int] = {}
    out: Dict[Tuple[str, str], str] = {}
    for sub in subfolders:
        items = [it for _, it in collect_aroll_jobs([sub], force=True)]
        seq = heygen_looks.pick_for_video(len(items), look_ids, counts, n_angles)
        for it, lid in zip(items, seq):
            out[(sub.name, it["output_file"])] = lid
    return out


def resolve_jobs(
    jobs: List[Tuple[Path, Dict[str, Any]]],
    default_avatar: str,
    looks_by_id: Dict[str, Dict[str, Any]],
    assign: Optional[Dict[Tuple[str, str], str]] = None,
    engine: Optional[str] = None,
    background: Any = None,
) -> List[Tuple[Path, Dict[str, Any]]]:
    """Điền avatar_id (look) / engine / background cho từng job. Ưu tiên: avatar_id trong JSON > assign auto > --avatar-id."""
    resolved = []
    for sub, item in jobs:
        it = dict(item)
        aid = it.get("avatar_id") or it.get("look_id") or (assign or {}).get((sub.name, it.get("output_file", ""))) or default_avatar
        it["avatar_id"] = aid
        it["engine"] = heygen_looks.choose_engine(looks_by_id.get(aid, {}), engine)
        it["background"] = it.get("background") or background
        resolved.append((sub, it))
    return resolved


def print_estimate(jobs: List[Tuple[Path, Dict[str, Any]]], usd_per_min: Optional[float], credits_per_min: Optional[float]) -> None:
    """Bảng giây theo look; thêm cột tiền/credit chỉ khi người dùng truyền đơn giá (mặc định: không biết -> chỉ in giây)."""
    rows: Dict[str, List[float]] = {}
    for _, it in jobs:
        r = rows.setdefault(it["avatar_id"], [0, 0.0])
        r[0] += 1
        r[1] += float(it.get("duration_hint_sec", 3.5))
    head = f"{'look (avatar_id)':<36}{'shot':>6}{'giây':>9}"
    head += f"{'USD':>9}" if usd_per_min is not None else ""
    head += f"{'credit':>9}" if credits_per_min is not None else ""
    print("ƯỚC LƯỢNG (giây × đơn giá):\n" + head)
    tot_n, tot_s = 0, 0.0
    for aid, (n, sec) in sorted(rows.items()):
        line = f"{aid:<36}{int(n):>6}{sec:>9.1f}"
        line += f"{sec / 60 * usd_per_min:>9.2f}" if usd_per_min is not None else ""
        line += f"{sec / 60 * credits_per_min:>9.2f}" if credits_per_min is not None else ""
        print(line)
        tot_n, tot_s = tot_n + int(n), tot_s + sec
    tot = f"{'TỔNG':<36}{tot_n:>6}{tot_s:>9.1f}"
    tot += f"{tot_s / 60 * usd_per_min:>9.2f}" if usd_per_min is not None else ""
    tot += f"{tot_s / 60 * credits_per_min:>9.2f}" if credits_per_min is not None else ""
    print(tot)
    if usd_per_min is None and credits_per_min is None:
        print("(Chưa có đơn giá: truyền --usd-per-min / --credits-per-min để tính tiền; chỉ in tổng giây.)")


# ── NGÂN HÀNG A-ROLL DÙNG LẠI ───────────────────────────────────────────────
def load_bank(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = data.get("bank") if isinstance(data, dict) else data
    for r in rows or []:
        if not r.get("bank_id") or not r.get("text"):
            raise ValueError(f"Dòng bank thiếu bank_id/text: {r}")
    return list(rows or [])


def bank_jobs(bank: List[Dict[str, Any]], bank_dir: Path, force: bool = False) -> List[Tuple[Path, Dict[str, Any]]]:
    """Mỗi câu trong bank render ĐÚNG MỘT lần thành bank/<bank_id>.mp4 (bỏ qua nếu đã có, trừ --force)."""
    jobs = []
    for r in bank:
        out = bank_dir / f"{r['bank_id']}.mp4"
        if out.exists() and out.stat().st_size > 10_000 and not force:
            continue
        item = {"output_file": out.name, "role_id": r["bank_id"], "tts_text": r["text"],
                "avatar_id": r.get("look_id") or None, "duration_hint_sec": r.get("duration_hint_sec", 3.5)}
        jobs.append((bank_dir, item))
    return jobs


def link_bank(bank: List[Dict[str, Any]], root: Path, bank_dir: Path, symlink: bool = False, force: bool = False) -> List[str]:
    """Đưa bank/<bank_id>.mp4 vào từng thư mục video thành <STT>_a-roll-<N>.mp4 theo `bank_id` trong prompts_heygen_aroll.json.
    Trả về danh sách thông báo (linked / skip / missing)."""
    by_id = {r["bank_id"]: r for r in bank}
    msgs: List[str] = []
    for sub in discover_subfolders(root):
        for item in json.loads((sub / "prompts_heygen_aroll.json").read_text(encoding="utf-8")):
            bid = item.get("bank_id")
            if bid is None:
                continue
            tag = f"{sub.name}/{item.get('output_file')}"
            used = [u.upper() for u in by_id.get(bid, {}).get("used_in") or []]
            if bid not in by_id:
                msgs.append(f"missing-bank {tag}: bank_id={bid} không có trong bank.json")
            elif used and not any(u in sub.name.upper() for u in used):
                msgs.append(f"skip {tag}: {bid} không khai báo used_in cho video này")
            elif not (bank_dir / f"{bid}.mp4").exists():
                msgs.append(f"missing-file {tag}: chưa render bank/{bid}.mp4")
            else:
                msgs.append(_link_one(bank_dir / f"{bid}.mp4", sub / item["output_file"], symlink, force, tag))
    return msgs


def _link_one(src: Path, dst: Path, symlink: bool, force: bool, tag: str) -> str:
    if (dst.exists() or dst.is_symlink()) and not force:
        return f"skip {tag}: đã có (dùng --force để ghi đè)"
    dst.unlink(missing_ok=True)
    if symlink:
        dst.symlink_to(src.resolve())
    else:
        shutil.copyfile(src, dst)
    return f"linked {tag} <- {src.name}"


def link_main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="render_heygen_aroll.py link", description="Chép/symlink A-roll từ bank vào thư mục video.")
    ap.add_argument("bank", type=Path, help="bank.json")
    ap.add_argument("root", type=Path, help="Thư mục tổng chứa các thư mục video (có prompts_heygen_aroll.json)")
    ap.add_argument("--bank-dir", type=Path, default=None, help="Mặc định: <thư mục bank.json>/bank")
    ap.add_argument("--symlink", action="store_true", help="Symlink thay vì chép")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    msgs = link_bank(load_bank(a.bank), a.root, a.bank_dir or a.bank.parent / "bank", a.symlink, a.force)
    print("\n".join(msgs) or "Không có shot nào mang bank_id.")
    return 1 if any(m.startswith("missing") for m in msgs) else 0


# ── RENDER ──────────────────────────────────────────────────────────────────
def render_job(key: str, sub: Path, item: Dict[str, Any], args: argparse.Namespace) -> None:
    out_file = sub / item["output_file"]
    title = f"{sub.name}_{Path(item['output_file']).stem}"
    vid = submit_heygen_video(
        key=key, title=title, script_text=item.get("tts_text", "").strip(), avatar_id=item["avatar_id"],
        voice_id=args.voice_id, aspect_ratio=args.aspect_ratio, resolution=args.resolution,
        motion_prompt=args.motion_prompt, api_version=args.api_version,
        engine=item.get("engine"), background=item.get("background"),
    )
    print(f"    Đã tạo task HeyGen: video_id={vid}")
    meta = poll_and_download_heygen(key=key, video_id=vid, out_path=out_file, api_version=args.api_version)
    print(f"    ✅ Đã lưu: {out_file} ({out_file.stat().st_size / (1024 * 1024):.2f} MB)")
    log_path = sub / "heygen_render_log.json"
    logs = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
    logs.append({"output_file": item["output_file"], "role_id": item.get("role_id"), "avatar_id": item["avatar_id"],
                 "video_id": vid, "duration_sec": meta.get("duration"), "timestamp": int(time.time())})
    log_path.write_text(json.dumps(logs, ensure_ascii=False, indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Tạo video A-Roll từ prompts_heygen_aroll.json bằng API HeyGen (xem thêm: `link`).")
    ap.add_argument("target_dir", type=Path, nargs="?", default=None,
                    help="Thư mục con của 1 kịch bản HOẶC Thư mục tổng (bỏ trống khi dùng --bank)")
    ap.add_argument("--filter-id", type=str, default=None, help="Chỉ lọc theo mã kịch bản (VD: XM01, KB10)")
    ap.add_argument("--shot", type=str, default=None, help="Chỉ chạy 1 shot cụ thể (VD: a-roll-2 hoặc 06_a-roll-2.mp4)")
    ap.add_argument("--avatar-id", type=str, default=DEFAULT_AVATAR_ID, help="HeyGen Avatar/Look ID mặc định (khi shot không có avatar_id)")
    ap.add_argument("--looks", type=Path, default=None, help="looks.json từ heygen_looks.py list")
    ap.add_argument("--assign", choices=["auto"], default=None, help="auto: tự chia look trong --looks cho shot chưa có avatar_id")
    ap.add_argument("--angles", type=int, default=3, help="Số góc mỗi video khi --assign auto (2-4)")
    ap.add_argument("--engine", type=str, default=None, help="Engine ưu tiên; chỉ gửi nếu look hỗ trợ, nếu không chọn engine look hỗ trợ")
    ap.add_argument("--background", type=str, default=None, help="Nền (màu/URL) gửi kèm; hoặc đặt `background` từng shot trong JSON")
    ap.add_argument("--bank", type=Path, default=None, help="bank.json: render mỗi câu một lần vào bank/<bank_id>.mp4")
    ap.add_argument("--bank-dir", type=Path, default=None, help="Mặc định: <thư mục bank.json>/bank")
    ap.add_argument("--estimate", action="store_true", help="In bảng tổng giây (× đơn giá nếu có) rồi thoát, không gọi API")
    ap.add_argument("--usd-per-min", type=float, default=None, help="Đơn giá USD/phút (mặc định chưa biết)")
    ap.add_argument("--credits-per-min", type=float, default=None, help="Đơn giá credit/phút (mặc định chưa biết)")
    ap.add_argument("--key-file", type=Path, default=None, help="File chứa khoá API (nếu không dùng HEYGEN_API_KEY)")
    ap.add_argument("--voice-id", type=str, default=DEFAULT_VOICE_ID, help="HeyGen Voice ID")
    ap.add_argument("--aspect-ratio", type=str, default=DEFAULT_ASPECT_RATIO, choices=["9:16", "16:9", "1:1"])
    ap.add_argument("--resolution", type=str, default=DEFAULT_RESOLUTION, choices=["720p", "1080p"])
    ap.add_argument("--motion-prompt", type=str, default=DEFAULT_MOTION_PROMPT, help="Motion prompt cho Avatar IV")
    ap.add_argument("--api-version", type=str, default="v3", choices=["v3", "v2"], help="HeyGen endpoint version")
    ap.add_argument("--force", action="store_true", help="Render đè cả những file .mp4 đã tồn tại")
    ap.add_argument("--yes", action="store_true", help="Xác nhận gọi API HeyGen thật (tốn Credit). Không có --yes: chỉ DRY-RUN.")
    return ap


def plan_jobs(args: argparse.Namespace) -> Optional[List[Tuple[Path, Dict[str, Any]]]]:
    """Gom job (đã điền look/engine). None nếu đầu vào sai (đã in lỗi)."""
    looks = heygen_looks.load_looks(args.looks) if args.looks else []
    by_id = {lk["id"]: lk for lk in looks}
    if args.bank:
        bank_dir = args.bank_dir or args.bank.parent / "bank"
        jobs = bank_jobs(load_bank(args.bank), bank_dir, args.force)
        return resolve_jobs(jobs, args.avatar_id, by_id, None, args.engine, args.background)
    if not args.target_dir or not args.target_dir.exists():
        print(f"[ERROR] Đường dẫn không tồn tại: {args.target_dir}")
        return None
    subs = discover_subfolders(args.target_dir, filter_id=args.filter_id)
    if not subs:
        print(f"[ERROR] Không tìm thấy prompts_heygen_aroll.json trong: {args.target_dir}")
        return None
    assign = None
    if args.assign == "auto":
        if not looks:
            print("[ERROR] --assign auto cần --looks looks.json")
            return None
        assign = auto_assign(subs, [lk["id"] for lk in looks], args.angles)
    jobs = collect_aroll_jobs(subs, shot_filter=args.shot, force=args.force)
    return resolve_jobs(jobs, args.avatar_id, by_id, assign, args.engine, args.background)


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "link":
        return link_main(argv[1:])
    args = build_parser().parse_args(argv)
    jobs = plan_jobs(args)
    if jobs is None:
        return 1
    total_dur = round(sum(float(it.get("duration_hint_sec", 3.5)) for _, it in jobs), 1)
    print("=" * 80)
    print(f"🎬 HEYGEN A-ROLL GENERATOR — {len(jobs)} PHÂN ĐOẠN CẦN RENDER (~{total_dur}s)")
    print(f"   Voice ID  : {args.voice_id}\n   Định dạng : {args.aspect_ratio} @ {args.resolution} ({args.api_version})")
    print("=" * 80)
    if not jobs:
        print("✅ Tất cả các phân đoạn A-Roll (HeyGen) đã được render hoặc không có shot nào khớp bộ lọc.")
        return 0
    warnings_count = 0
    for idx, (sub, item) in enumerate(jobs, start=1):
        tts = item.get("tts_text", "").strip()
        issues = audit_tts_text(tts)
        warnings_count += len(issues)
        print(f"[{idx:02d}/{len(jobs):02d}] {sub.name}/{item['output_file']} ({item.get('role_id')} · ~{item.get('duration_hint_sec', 0)}s)")
        print(f"        look: {item['avatar_id']}  engine: {item.get('engine') or 'mặc định'}")
        print(f"        TTS: \"{tts}\"")
        for iss in issues:
            print(f"        ⚠️ CẢNH BÁO TTS: {iss}")
    if args.estimate:
        print_estimate(jobs, args.usd_per_min, args.credits_per_min)
        return 0
    if not args.yes:
        print("-" * 80)
        print(f"[DRY-RUN] Chưa gọi API HeyGen (0 Credit tiêu tốn). Tổng cộng {len(jobs)} shot (~{total_dur}s), {warnings_count} cảnh báo TTS.")
        print("👉 Để thực sự gọi API HeyGen và tải video A-Roll về, hãy thêm cờ `--yes`.")
        return 0
    key = load_heygen_key(args.key_file)
    if not key:
        print("[ERROR] Thiếu HEYGEN_API_KEY (biến môi trường) hoặc --key-file.")
        return 1
    done = 0
    for idx, (sub, item) in enumerate(jobs, start=1):
        print(f"\n🚀 [{idx:02d}/{len(jobs):02d}] Đang gửi HeyGen: {sub.name}/{item['output_file']} ...")
        try:
            render_job(key, sub, item, args)
            done += 1
        except Exception as exc:
            print(f"    ❌ LỖI ở {sub.name}/{item['output_file']}: {exc}")
            return 1
    print("=" * 80)
    print(f"🎉 HOÀN TẤT HEYGEN A-ROLL: {done}/{len(jobs)} file .mp4 đã lưu!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
