"""thlib.broll — bước BUILD `broll_assets` (spec 1.2.0 §7): tạo (hoặc lấy lại từ bộ đệm) ảnh/clip AI cho mọi
slot `edit.json → broll`, hậu kỳ về khung 1080×1920, ghi `public/broll/assets.json` + `ATTRIBUTION.md`.

- Ảnh: `ag/nano-banana` qua `POST /v1/images/generations` (b64_json JPEG). Clip: `xai/grok-imagine-video` qua
  `POST /v1/videos/generations` → hỏi `GET /v1/videos/<id>` tới `status: done` → tải `video.url`.
- Key chỉ đọc từ env NINEROUTER_API_KEY — không in, không ghi (thông điệp lỗi không bao giờ chứa key).
- Bộ đệm: khoá = sha256(model | prompt gửi đi | v | WxH [| retry]); entry cùng khoá + file còn + sha khớp ⇒ dùng lại.
- Clip lỗi ⇒ ảnh tĩnh cùng prompt, cảnh báo BROLL_CLIP_FALLBACK:<id> (không chặn).
- Ảnh không tạo được ⇒ BrollGenError («BROLL_GEN …», chủ OPERATOR); ảnh phẳng hai lần ⇒ BrollFlatError («BROLL_FLAT …», chủ PLAN).
- Test tiêm client giả qua tham số `client` hoặc `CLIENT_FACTORY` — test không bao giờ gọi mạng.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

import numpy as np
from PIL import Image

from .rules import Rules

ASSETS = "assets.json"
ATTRIBUTION = "ATTRIBUTION.md"
_RETRY_SLEEP_S = (5, 15)


class BrollGenError(Exception):
    """Không tạo được ảnh (mạng, hạn mức, thiếu key) — chủ OPERATOR."""


class BrollFlatError(Exception):
    """Ảnh phẳng (lệch chuẩn độ sáng thấp) cả sau một lần tạo lại — chủ PLAN (đổi prompt)."""


class HttpError(Exception):
    def __init__(self, code: int | None, msg: str):
        super().__init__(f"{code if code is not None else 'mạng'} {msg}")
        self.code = code


# ------------------------------------------------ client 9router


class NineRouter:
    def __init__(self, R: Rules, key: str | None = None, base_url: str | None = None, sleep=time.sleep):
        self.R = R
        self.key = key if key is not None else os.environ.get("NINEROUTER_API_KEY", "")
        self.base = (base_url or os.environ.get("NINEROUTER_BASE_URL") or R.get("broll.ai.base_url")).rstrip("/")
        self.sleep = sleep

    def _once(self, method: str, url: str, payload: dict | None, auth: bool) -> tuple[int, bytes]:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Content-Type": "application/json"}
        if auth:
            headers["Authorization"] = f"Bearer {self.key}"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        timeout = float(self.R.get("broll.ai.http_timeout_s"))
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def _call(self, method: str, path_or_url: str, payload: dict | None = None, auth: bool = True) -> tuple[int, bytes]:
        """Gọi có thử lại: 5xx / lỗi mạng / hết giờ thử lại 2 lần (nghỉ 5 s, 15 s); 4xx trả về ngay."""
        if auth and not self.key:
            raise HttpError(None, "thiếu env NINEROUTER_API_KEY")
        url = path_or_url if path_or_url.startswith("http") else self.base + path_or_url
        last = None
        for attempt in range(len(_RETRY_SLEEP_S) + 1):
            try:
                code, body = self._once(method, url, payload, auth)
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last = HttpError(None, type(exc).__name__)
            else:
                if code < 500:
                    return code, body
                last = HttpError(code, _first_line(body))
            if attempt < len(_RETRY_SLEEP_S):
                self.sleep(_RETRY_SLEEP_S[attempt])
        raise last

    def still(self, prompt: str) -> bytes:
        code, body = self._call("POST", "/images/generations",
                                {"model": self.R.get("broll.ai.still_model"), "prompt": prompt, "n": 1})
        if code != 200:
            raise HttpError(code, _first_line(body))
        try:
            return base64.b64decode(json.loads(body)["data"][0]["b64_json"])
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise HttpError(code, f"phản hồi ảnh không đọc được ({type(exc).__name__})") from None

    def clip(self, prompt: str) -> bytes:
        payload = {"model": self.R.get("broll.ai.clip_model"), "prompt": prompt, **self.R.get("broll.ai.clip_params")}
        code, body = self._call("POST", "/videos/generations", payload)
        if code != 200:
            raise HttpError(code, _first_line(body))
        rid = json.loads(body).get("request_id")
        if not rid:
            raise HttpError(code, "không có request_id")
        every, limit = float(self.R.get("broll.ai.poll_every_s")), float(self.R.get("broll.ai.poll_timeout_s"))
        waited = 0.0
        while waited <= limit:
            self.sleep(every)
            waited += every
            code, body = self._call("GET", f"/videos/{rid}")
            if code not in (200, 202):
                raise HttpError(code, _first_line(body))
            job = json.loads(body)
            status = job.get("status")
            if status == "done":
                url = (job.get("video") or {}).get("url")
                if not url:
                    raise HttpError(code, "clip xong nhưng không có url")
                code, data = self._call("GET", url, auth=False)
                if code != 200:
                    raise HttpError(code, "tải clip lỗi")
                return data
            if status not in ("pending", "processing", None):
                raise HttpError(code, f"clip {status}")
        raise HttpError(None, f"clip chưa xong sau {limit:g} s")


def _first_line(body: bytes) -> str:
    try:
        msg = json.loads(body).get("error", {}).get("message") or ""
    except (ValueError, AttributeError):
        msg = body.decode("utf-8", "replace")
    return " ".join(str(msg).split())[:160]


class FakeDirClient:
    """Client giả đọc still.jpg và clip.mp4 từ thư mục TH_BROLL_FAKE_DIR (phục vụ test subprocess / e2e)."""
    def __init__(self, fake_dir: Path):
        self.fake_dir = Path(fake_dir)

    def still(self, prompt: str) -> bytes:
        p = self.fake_dir / "still.jpg"
        if not p.is_file():
            raise HttpError(None, f"Fake still file not found: {p}")
        return p.read_bytes()

    def clip(self, prompt: str) -> bytes:
        p = self.fake_dir / "clip.mp4"
        if not p.is_file():
            raise HttpError(None, f"Fake clip file not found: {p}")
        return p.read_bytes()


def default_client_factory(R: Rules):
    fake_dir = os.environ.get("TH_BROLL_FAKE_DIR")
    if fake_dir:
        return FakeDirClient(Path(fake_dir))
    return NineRouter(R)


CLIENT_FACTORY = default_client_factory


# ------------------------------------------------ hậu kỳ


def _trim_uniform_borders(img: "Image.Image", min_px: int = 8, std_max: float = 3.0, jump: float = 30.0) -> "Image.Image":
    """1.2.2 F3 (lô b04 v12 B4 viền trắng 47+48 px): cắt dải đều ở mép — ≥ min_px hàng/cột liền mép, mỗi hàng std < std_max và
    trung bình > 240 hoặc < 12, và min_px hàng/cột ngay sau dải lệch trung bình dải > jump (đột ngột). Nền tự nhiên liền mạch giữ nguyên."""
    g = np.asarray(img.convert("L"), dtype=np.float32)

    def band(lines: np.ndarray) -> int:
        n = 0
        for row in lines:
            m = float(row.mean())
            if row.std() < std_max and (m > 240 or m < 12):
                n += 1
            else:
                break
        if n < min_px or n + min_px > len(lines):
            return 0
        return n if abs(float(lines[n:n + min_px].mean()) - float(lines[:n].mean())) > jump else 0

    top, bottom = band(g), band(g[::-1])
    left, right = band(g.T), band(g.T[::-1])
    if not (top or bottom or left or right):
        return img
    return img.crop((left, top, img.width - right, img.height - bottom))


def _still_file(raw: bytes, out: Path, R: Rules) -> tuple[int, int, float]:
    """Phủ khung out_w×out_h (lanczos, cắt giữa), JPG chất lượng jpg_q. Trả (w, h, lệch chuẩn độ sáng)."""
    W, H = int(R.get("broll.out_w")), int(R.get("broll.out_h"))
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    img = _trim_uniform_borders(img)
    k = max(W / img.width, H / img.height)
    img = img.resize((max(W, round(img.width * k)), max(H, round(img.height * k))), Image.LANCZOS)
    x, y = (img.width - W) // 2, (img.height - H) // 2
    img = img.crop((x, y, x + W, y + H))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "JPEG", quality=int(R.get("broll.jpg_q")))
    return W, H, float(np.asarray(img.convert("L"), dtype=np.float32).std())



def _clip_file(raw: bytes, out: Path, seconds: float, R: Rules) -> tuple[int, int, float]:
    """1080×1920, 30 fps, H.264 CRF clip_crf, yuv420p, không tiếng, cắt còn `seconds`. Trả (w, h, độ dài)."""
    W, H = int(R.get("broll.out_w")), int(R.get("broll.out_h"))
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "src.mp4"
        src.write_bytes(raw)
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},fps={int(R.get('broll.clip_fps'))}"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-t", f"{seconds:.3f}", "-vf", vf,
                        "-c:v", "libx264", "-crf", str(int(R.get("broll.clip_crf"))), "-pix_fmt", "yuv420p", "-an",
                        str(out)], check=True, capture_output=True, text=True, timeout=300)
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)],
                           check=True, capture_output=True, text=True, timeout=60)
    return W, H, round(float(probe.stdout.strip()), 3)


# ------------------------------------------------ bước BUILD


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cache_key(model: str, sent: str, v: int, R: Rules, retry: bool = False) -> str:
    size = f"{int(R.get('broll.out_w'))}x{int(R.get('broll.out_h'))}"
    return hashlib.sha256(f"{model}|{sent}|{v}|{size}{'|retry' if retry else ''}".encode("utf-8")).hexdigest()


def file_name(slot_id: str, v: int, media: str) -> str:
    return f"broll/br{int(slot_id[1:]):02d}_v{v}.{'mp4' if media == 'clip' else 'jpg'}"


def _reuse(entry: dict | None, public: Path) -> bool:
    return bool(entry) and (public / entry["file"]).is_file() and _sha(public / entry["file"]) == entry["sha256"]


def run(project: Path, edit: dict, R: Rules, client=None) -> dict:
    """Asset cho mọi slot của edit['broll']. Trả {"assets": [entry…] theo thời gian, "warnings": [...]}."""
    project = Path(project)
    public = project / "public"
    manifest = public / "broll" / ASSETS
    old = json.loads(manifest.read_text(encoding="utf-8")) if manifest.is_file() else {"assets": []}
    by_key = {e["key"]: e for e in old.get("assets", [])}
    client = client or CLIENT_FACTORY(R)
    suffix = str(R.get("broll.style_suffix"))
    flat_min = float(R.get("broll.flat_std_min"))
    assets, warnings = [], []
    for slot in sorted(edit.get("broll") or [], key=lambda s: s["t_in"]):
        sid, v = slot["id"], int(slot.get("v", 1))
        sent = f"{slot['prompt'].strip()} {suffix}"
        entry = None
        if slot["media"] == "clip":
            model = str(R.get("broll.ai.clip_model"))
            key = cache_key(model, sent, v, R)
            entry = by_key.get(key) if _reuse(by_key.get(key), public) else None
            if entry is None:
                seconds = round(slot["t_out"] - slot["t_in"] + 0.5, 3)
                reason: str | None = None
                try:
                    raw = client.clip(sent)
                    rel = file_name(sid, v, "clip")
                    w, h, dur = _clip_file(raw, public / rel, seconds, R)
                    entry = {"id": sid, "file": rel, "media": "clip", "model": model, "prompt": slot["prompt"], "v": v,
                             "key": key, "sha256": _sha(public / rel), "w": w, "h": h, "dur_s": dur,
                             "status": "delivered", "fallback": False, "fallback_reason": None, "created": date.today().isoformat()}
                except (HttpError, subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError) as exc:
                    reason = str(exc)[:80]
                    warnings.append(f"BROLL_CLIP_FALLBACK:{sid}: {exc}")
        if entry is None:
            entry = _still(client, slot, sent, v, R, public, by_key, flat_min, fallback_reason=reason if slot["media"] == "clip" else None)
        assets.append({**entry, "id": sid})
    out = {"schema": "assets/1", "ai_disclosure": bool(assets), "assets": assets}
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    lines = ["# ATTRIBUTION — B-roll", ""] + [
        f"- `{e['file']}` — {e['model']}, {e['created']}, AI-generated, minh hoạ (không phải bằng chứng)" for e in assets]
    (public / "broll" / ATTRIBUTION).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"assets": assets, "warnings": warnings}


def _still(client, slot: dict, sent: str, v: int, R: Rules, public: Path, by_key: dict, flat_min: float,
           fallback_reason: str | None) -> dict:
    sid = slot["id"]
    model = str(R.get("broll.ai.still_model"))
    rel = file_name(sid, v, "still")
    for retry in (False, True):
        key = cache_key(model, sent, v, R, retry)
        if _reuse(by_key.get(key), public):
            return {**by_key[key], "fallback": fallback_reason is not None, "fallback_reason": fallback_reason}
        try:
            raw = client.still(sent)
        except HttpError as exc:
            raise BrollGenError(f"BROLL_GEN {sid}: {exc}") from None
        w, h, std = _still_file(raw, public / rel, R)
        if std >= flat_min:
            return {"id": sid, "file": rel, "media": "still", "model": model, "prompt": slot["prompt"], "v": v,
                    "key": key, "sha256": _sha(public / rel), "w": w, "h": h, "dur_s": None, "status": "delivered",
                    "fallback": fallback_reason is not None, "fallback_reason": fallback_reason,
                    "created": date.today().isoformat()}
    raise BrollFlatError(f"BROLL_FLAT {sid}: ảnh phẳng (lệch chuẩn độ sáng {std:.1f} < {flat_min:g}) cả sau khi tạo lại "
                         f"— Sửa: viết lại prompt của {sid} (cảnh có chủ thể, ánh sáng, chiều sâu) hoặc tăng \"v\"")
