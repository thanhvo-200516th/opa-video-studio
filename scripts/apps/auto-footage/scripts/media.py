"""Tải file, đo, chuẩn hoá video (H.264 30fps BT.709, bỏ tiếng, xoá metadata) / ảnh (JPEG không EXIF), ảnh động
(zoom chậm), lấy khung, vẽ bảng ảnh."""
from __future__ import annotations

import io
import json
import re
import shutil
import subprocess
import time
import unicodedata
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FFMPEG = shutil.which("ffmpeg") or "/home/vmiz/.local/bin/ffmpeg"
FFPROBE = shutil.which("ffprobe") or "/home/vmiz/.local/bin/ffprobe"
UA = "Mozilla/5.0 (X11; Linux x86_64) auto-footage/1.0"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp"}
# mã hoá giao: H.264, không tiếng, không metadata, bỏ SEI x264 (dấu phần mềm) và thẻ encoder
ENC = ["-an", "-sn", "-dn", "-map_metadata", "-1", "-map_chapters", "-1", "-r", "30", "-c:v", "libx264", "-preset", "veryfast",
       "-crf", "18", "-pix_fmt", "yuv420p", "-fflags", "+bitexact", "-flags:v", "+bitexact", "-bsf:v", "filter_units=remove_types=6",
       "-metadata:s:v:0", "encoder=", "-metadata:s:v:0", "handler_name=Video", "-movflags", "+faststart"]
BT709 = "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709"


def http_get(url: str, headers: dict | None = None, timeout: int = 30, tries: int = 3) -> bytes:
    last = None
    for n in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001 — thử lại rồi báo lỗi gốc
            last = e
            time.sleep(1.5 * (n + 1))
    raise RuntimeError(f"tải lỗi {url.split('?')[0]}: {last}")


def http_json(url: str, headers: dict | None = None) -> dict:
    return json.loads(http_get(url, headers))


def download(url: str, out: Path, headers: dict | None = None) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f, 1 << 20)
    tmp.rename(out)
    return out


def probe(path: Path) -> dict:
    out = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                          "-of", "json", str(path)], capture_output=True, text=True).stdout
    d = json.loads(out or "{}")
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    return {"w": v.get("width", 0), "h": v.get("height", 0), "duration": float(d.get("format", {}).get("duration", 0) or 0),
            "audio": any(s.get("codec_type") == "audio" for s in d.get("streams", []))}


def normalize(src: Path, out: Path) -> Path:
    """H.264 30fps BT.709, không tiếng, xoá metadata; cạnh ngắn tối đa 1080 (4K → 1080p)."""
    out.parent.mkdir(parents=True, exist_ok=True)
    vf = f"scale=w='if(lt(iw,ih),min(iw,1080),-2)':h='if(lt(iw,ih),-2,min(ih,1080))',{BT709}"
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(src), "-vf", vf, *ENC, str(out)], check=True)
    return out


def normalize_image(src: Path, out: Path, max_side: int = 2560) -> Path:
    """Ảnh → JPEG/PNG theo đuôi `out`, RGB, cạnh dài ≤ max_side, không EXIF / XMP / chú thích."""
    out.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = im.convert("RGB")
        im.thumbnail((max_side, max_side), Image.LANCZOS)
        clean = Image.new("RGB", im.size)
        clean.paste(im)
        if out.suffix.lower() == ".png":
            clean.save(out, optimize=True)
        else:
            clean.save(out, quality=92, optimize=True)
    return out


def ken_burns(img: Path, out: Path, seconds: float = 5.0, zoom: float = 1.12, size: tuple = (1080, 1920), fps: int = 30) -> Path:
    """Ảnh tĩnh → clip zoom chậm (phủ kín khung 9:16, cắt giữa) — B-roll động không tốn lượt Muse."""
    w, h = size
    n = round(seconds * fps)
    vf = (f"scale={w * 2}:{h * 2}:force_original_aspect_ratio=increase,crop={w * 2}:{h * 2},"
          f"zoompan=z='1+({zoom}-1)*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={w}x{h}:fps={fps},{BT709}")
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([FFMPEG, "-v", "error", "-y", "-loop", "1", "-i", str(img), "-vf", vf, "-frames:v", str(n), *ENC, str(out)], check=True)
    return out


def last_frame(path: Path, out_png: Path) -> Path:
    """Khung cuối cùng của video → PNG (đọc 0,5 s cuối, ghi đè tới khung sau chót)."""
    subprocess.run([FFMPEG, "-v", "error", "-y", "-sseof", "-0.5", "-i", str(path), "-map_metadata", "-1", "-update", "1",
                    str(out_png)], check=True)
    return out_png


def concat_xfade(parts: list[Path], out: Path, fade: float = 0.2, total: float | None = None) -> Path:
    """Nối các đoạn video bằng chuyển mờ `fade` giây ở mỗi mối (đưa về cùng cỡ đoạn đầu, 30fps), cắt còn `total` giây."""
    sizes = [probe(p) for p in parts]
    w, h = sizes[0]["w"], sizes[0]["h"]
    prep = [f"[{i}:v]scale={w}:{h},fps=30,format=yuv420p,settb=AVTB[s{i}]" for i in range(len(parts))]
    chain, last, t = [], "s0", sizes[0]["duration"]
    for i in range(1, len(parts)):
        chain.append(f"[{last}][s{i}]xfade=transition=fade:duration={fade}:offset={t - fade:.3f}[x{i}]")
        last, t = f"x{i}", t + sizes[i]["duration"] - fade
    graph = ";".join(prep + chain + [f"[{last}]{BT709}[out]"])
    cmd = [FFMPEG, "-v", "error", "-y", *sum((["-i", str(p)] for p in parts), []), "-filter_complex", graph, "-map", "[out]"]
    if total:
        cmd += ["-t", f"{total:.3f}"]
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(cmd + ENC + [str(out)], check=True)
    return out


def frame(path: Path, t: float, width: int = 320) -> Image.Image | None:
    if path.suffix.lower() in IMG_EXT:
        with Image.open(path) as im:
            im = im.convert("RGB")
            im.thumbnail((width, width * 4))
            return im
    png = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{max(0.0, t):.2f}", "-i", str(path), "-frames:v", "1",
                          "-vf", f"scale={width}:-2", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    return Image.open(io.BytesIO(png)).convert("RGB") if png else None


def frames(path: Path, duration: float, fracs=(0.1, 0.5, 0.9), width: int = 320) -> list[Image.Image]:
    return [im for im in (frame(path, duration * f, width) for f in fracs) if im is not None]


def slug(text: str, n: int = 48) -> str:
    """Tiếng Việt → ASCII_Viet_Hoa_Dau_Tu cho tên file."""
    t = unicodedata.normalize("NFD", text.replace("đ", "d").replace("Đ", "D"))
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    words = re.findall(r"[A-Za-z0-9]+", t)
    return "_".join(w[:1].upper() + w[1:] for w in words)[:n].rstrip("_") or "Clip"


def _wrap(d: ImageDraw.ImageDraw, text: str, font, width: int, lines: int) -> list[str]:
    out, cur = [], ""
    for w in text.split():
        t = f"{cur} {w}".strip()
        if d.textlength(t, font=font) <= width:
            cur = t
        else:
            out.append(cur)
            cur = w
    out.append(cur)
    if len(out) > lines:
        out = out[:lines]
        out[-1] = out[-1].rstrip(" ,.") + "…"
    return out


def contact_sheet(blocks: list[tuple[str, str, list[tuple[Image.Image | None, str, bool]]]], out: Path,
                  per_row: int = 2, tile: int = 250) -> Path:
    """blocks = [(tiêu đề cảnh, dòng phụ, [(ảnh, chú thích, đang chọn?)…])] → bảng ảnh `per_row` cảnh mỗi hàng."""
    big, mid, small = ImageFont.truetype(FONT, 26), ImageFont.truetype(FONT, 19), ImageFont.truetype(FONT, 18)
    th, gap, pad = round(tile * 16 / 9), 12, 28
    cols = max((len(b[2]) for b in blocks), default=1)
    bw = cols * tile + (cols - 1) * gap
    head = 34 + 2 * 26 + 8
    bh = head + th + 58                      # chú thích tối đa 2 dòng
    rows = (len(blocks) + per_row - 1) // per_row
    sheet = Image.new("RGB", (per_row * bw + (per_row + 1) * pad, rows * (bh + pad) + pad), (22, 22, 22))
    d = ImageDraw.Draw(sheet)
    for n, (title, sub, cells) in enumerate(blocks):
        x0, y0 = pad + (n % per_row) * (bw + pad), pad + (n // per_row) * (bh + pad)
        d.text((x0, y0), title, font=big, fill=(255, 210, 60))
        for k, line in enumerate(_wrap(d, sub, mid, bw, 2)):
            d.text((x0, y0 + 36 + k * 26), line, font=mid, fill=(200, 200, 200))
        for c, (im, cap, chosen) in enumerate(cells):
            x, y = x0 + c * (tile + gap), y0 + head
            box = Image.new("RGB", (tile, th), (0, 0, 0))
            if im is not None:
                im = im.copy()
                im.thumbnail((tile, th))
                box.paste(im, ((tile - im.width) // 2, (th - im.height) // 2))
            sheet.paste(box, (x, y))
            if chosen:
                d.rectangle([x - 4, y - 4, x + tile + 3, y + th + 3], outline=(255, 210, 60), width=4)
            for k, line in enumerate(_wrap(d, cap, small, tile, 2)):
                d.text((x, y + th + 8 + k * 22), line, font=small, fill=(255, 210, 60) if chosen else (235, 235, 235))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=88)
    return out
