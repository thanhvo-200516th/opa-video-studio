"""Đo một clip Omni Flash theo thông số của prompt (P01…): khung hình, nền, màu, nhịp, điểm neo, âm. Đo, không đoán.

  python -I tools/flow-omni/do_clip.py <clip.mp4> flow-omni/do/P01.json [--out <thư mục>]

Ra (mặc định flow-omni/do/<tên clip>/): BAO-CAO.md, so-lieu.json, do-thi.png, khung-moc.png, cuoi-vs-khung-neo.png.
Ngưỡng lấy từ mục 10 của PROMPT-PACK-OMNI-FLASH.md (hằng TOL dưới đây).

Cách đo chính:
- Logo = điểm ảnh cách màu logo < 80 (RGB). Màu "lạ" = điểm ảnh cách đoạn thẳng nền → logo > 45, tức không phải
  nền, logo hay viền khử răng cưa giữa hai màu đó (bắt glow, bóng đổ, gradient, màu thêm).
- Scale đầu chữ U: chỉ dùng phần dưới 45 % chiều cao dấu (không có sừng). Tìm s sao cho diện tích phần đáy
  cao 0,45 × H × s bằng s² lần diện tích tương ứng ở khung neo cuối (chia đôi). Số ra đã gồm cả máy đẩy.
- Sừng: diện tích logo trong hai dải mép ngoài (13 % bề rộng mỗi bên), nửa trên dấu, so với khung neo cuối.
  Gần đúng quanh lúc đầu vượt đà (đầu to lấn vào dải).
- Âm: mốc đánh = mức RMS 5 ms tăng > 8 dB trong 20 ms và vượt −45 dBFS; cao độ = đỉnh FFT 150–5000 Hz
  khi độ phẳng phổ < 0,2 (âm có nốt).
- Đứng yên: dùng nguyên thước của dự án tools/v2w/metrics.py (Tĩnh B theo ô 2 s, ngưỡng cả đoạn ≤ 10 %),
  là thước đã dùng khi V2 bị chê "nhàm". Khoảng "exempt" trong spec (khung chốt logo) được miễn như khung CTA.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import matplotlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import binary_erosion

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
FLOW = ROOT / "flow-omni"
sys.path.insert(0, str(ROOT / "tools" / "v2w"))
import metrics as v2metrics  # noqa: E402
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
TOL = {"time_s": 0.2, "scale_pct": 3.0, "rgb": 3, "foreign_pct": 0.05, "anchor_pct": 2.0}
MAX_W = 1280  # đo ở tối đa 1280 px ngang: mọi số theo %, đủ chính xác và nhanh


def hex_rgb(h: str) -> np.ndarray:
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.int16)


def probe(clip: Path) -> dict:
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(clip)],
                                  capture_output=True, text=True, check=True).stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    num, den = map(int, v["avg_frame_rate"].split("/"))
    return {"w": v["width"], "h": v["height"], "fps": num / den, "duration": float(j["format"]["duration"]),
            "codec": v["codec_name"], "pix_fmt": v.get("pix_fmt"),
            "color": {k: v.get(k, "?") for k in ("color_range", "color_space", "color_transfer", "color_primaries")},
            "audio": None if a is None else {"codec": a["codec_name"], "rate": int(a["sample_rate"]), "channels": a["channels"]}}


def read_frames(clip: Path, info: dict, w: int, h: int):
    """Giải mã mọi khung về RGB w×h. Clip không khai màu thì coi là bt709 dải TV (như video HD thường gặp)."""
    c = info["color"]
    src = []
    if c["color_space"] in ("?", "unknown"):
        src.append("in_color_matrix=bt709")
    if c["color_range"] in ("?", "unknown"):
        src.append("in_range=tv")
    vf = f"scale={w}:{h}" + (":" + ":".join(src) if src else "") + ":flags=area"
    p = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(clip), "-vf", vf,
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = w * h * 3
    try:
        while len(buf := p.stdout.read(n)) == n:
            yield np.frombuffer(buf, np.uint8).reshape(h, w, 3)
    finally:
        p.kill()
        p.stdout.close()
        p.wait()


def logo_mask(img: np.ndarray, logo: np.ndarray) -> np.ndarray:
    return np.sqrt(((img.astype(np.int32) - logo) ** 2).sum(-1)) < 80


def bbox(mask: np.ndarray) -> tuple[int, int, int, int] | None:
    rows, cols = np.where(mask.sum(1) >= 2)[0], np.where(mask.sum(0) >= 2)[0]
    if len(rows) == 0 or len(cols) == 0:
        return None
    return int(cols[0]), int(rows[0]), int(cols[-1]) + 1, int(rows[-1]) + 1


def head_scale(mask: np.ndarray, y1: int, ref_h: float, ref_a45: float) -> float:
    """Scale đầu chữ U neo đáy: nghiệm của diện tích(phần đáy cao 0,45·H·s) = s²·diện tích tương ứng ở khung neo."""
    rows = mask.sum(1).astype(np.float64)

    def f(s: float) -> float:
        top = max(0, int(round(y1 - 0.45 * ref_h * s)))
        return rows[top:y1].sum() - s * s * ref_a45

    lo, hi = 0.05, 1.5
    if f(lo) <= 0:
        return 0.0
    for _ in range(30):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
    return (lo + hi) / 2


def curve(keys: list, t: np.ndarray) -> np.ndarray:
    """Giá trị đích theo keyframe [giây, giá trị, kiểu ease đi vào mốc này]."""
    out = np.full_like(t, float(keys[0][1]))
    for (t0, v0, _), (t1, v1, ease) in zip(keys, keys[1:]):
        x = np.clip((t - t0) / (t1 - t0), 0, 1)
        k = {"linear": x, "ease-out": 1 - (1 - x) ** 3, "ease-in": x ** 3,
             "ease-in-out": x * x * (3 - 2 * x)}.get(ease, x)
        out = np.where(t >= t0, v0 + (v1 - v0) * k, out)
    out[t < keys[0][0]] = 0 if keys[0][2] == "hold" else keys[0][1]
    return out


def analyse_video(clip: Path, spec: dict, info: dict) -> tuple[dict, dict]:
    w = min(MAX_W, info["w"])
    h = int(round(info["h"] * w / info["w"] / 2) * 2)
    bg, logo = hex_rgb(spec["bg"]), hex_rgb(spec["logo"])
    ref = np.asarray(Image.open(FLOW / spec["last_frame"]).convert("RGB").resize((w, h), Image.LANCZOS))
    rmask = logo_mask(ref, logo)
    rx0, ry0, rx1, ry1 = bbox(rmask)
    ref_h, ref_w = ry1 - ry0, rx1 - rx0
    ref_a45 = rmask[int(round(ry1 - 0.45 * ref_h)):ry1].sum()
    horn_zone = np.zeros_like(rmask)
    band = int(0.13 * ref_w)
    horn_zone[:ry0 + int(0.45 * ref_h), rx0 - band:rx0 + band] = True
    horn_zone[:ry0 + int(0.45 * ref_h), rx1 - band:rx1 + band] = True
    ref_horn = (rmask & horn_zone).sum()
    seg = (logo - bg).astype(np.float32)
    want = {round(float(t), 2) for t in [0.0] + [k[0] for k in spec.get("head_scale", [])]
            + list(spec.get("horns", {}).values()) + [c["t"] for c in spec.get("sfx", [])]}
    rows, keep = [], {}
    for i, f in enumerate(read_frames(clip, info, w, h)):
        t = i / info["fps"]
        fi = f.astype(np.int16)
        ring = np.concatenate([fi[:6].reshape(-1, 3), fi[-6:].reshape(-1, 3), fi[:, :6].reshape(-1, 3), fi[:, -6:].reshape(-1, 3)])
        corners = [fi[:16, :16], fi[:16, -16:], fi[-16:, :16], fi[-16:, -16:]]
        rel = (fi - bg).astype(np.float32)
        tt = np.clip(rel @ seg / (seg @ seg), 0, 1)
        foreign = np.sqrt(((rel - tt[..., None] * seg) ** 2).sum(-1)) > 45
        m = logo_mask(f, logo)
        b = bbox(m)
        core = binary_erosion(m, iterations=2)
        row = {"t": round(t, 4), "bg": np.median(ring, 0).astype(int).tolist(),
               "bg_dev": int(max(np.abs(c.reshape(-1, 3).mean(0) - bg).max() for c in corners)),
               "foreign_pct": round(float(foreign.mean() * 100), 3), "area": int(m.sum()),
               "foreign_rgb": np.median(f[foreign], 0).astype(int).tolist() if foreign.sum() > 50 else None,
               "logo_rgb": np.median(f[core], 0).astype(int).tolist() if core.sum() > 200 else None,
               "bbox": b, "head_pct": None, "horn_pct": round(float((m & horn_zone).sum() / ref_horn * 100), 1)}
        if b and m.sum() > 0.005 * rmask.sum():
            row["head_pct"] = round(head_scale(m, b[3], ref_h, ref_a45) * 100, 2)
        rows.append(row)
        if any(abs(t - x) < 0.5 / info["fps"] for x in want):
            keep[round(t, 2)] = f.copy()
        last = f
    keep["cuoi"] = last
    geo = {"w": w, "h": h, "ref_bbox": [rx0, ry0, rx1, ry1], "ref": ref, "rmask": rmask}
    return {"rows": rows, "geo": geo}, keep


def analyse_audio(clip: Path, spec: dict, fps: float) -> dict | None:
    rate = 48000
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(clip), "-vn", "-ac", "1", "-ar", str(rate), "-f", "f32le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    if len(x) < rate // 10:
        return None
    hop = rate // 200
    n = len(x) // hop
    db = 20 * np.log10(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    onsets, i = [], 4
    while i < n:
        if db[i] > -45 and db[i] - db[i - 4:i].min() > 8:
            seg = x[i * hop + rate // 100: i * hop + rate // 100 + 4096]
            note = None
            if len(seg) == 4096:
                spec_mag = np.abs(np.fft.rfft(seg * np.hanning(4096)))
                fr = np.fft.rfftfreq(4096, 1 / rate)
                sel = (fr > 150) & (fr < 8000)
                p = spec_mag[sel] ** 2 + 1e-18
                flat = float(np.exp(np.log(p).mean()) / p.mean())
                band = (fr > 150) & (fr < 5000)
                f0 = float(fr[band][np.argmax(spec_mag[band])])
                if flat < 0.2:
                    midi = 69 + 12 * np.log2(f0 / 440)
                    r = int(round(midi))
                    note = {"name": f"{NOTES[r % 12]}{r // 12 - 1}", "hz": round(f0, 1), "cents": int(round((midi - r) * 100))}
            onsets.append({"t": round(i * hop / rate, 3), "peak_db": round(float(db[i:i + 20].max()), 1), "note": note})
            i += 16
        else:
            i += 1
    frame_ms = 1000 / fps
    cues = []
    for c in spec.get("sfx", []):
        near = min(onsets, key=lambda o: abs(o["t"] - c["t"]), default=None)
        hit = near if near and abs(near["t"] - c["t"]) <= 0.25 else None
        cues.append({**c, "found": hit, "dt_ms": None if hit is None else int(round((hit["t"] - c["t"]) * 1000)),
                     "on_beat": bool(hit and abs(hit["t"] - c["t"]) * 1000 <= frame_ms),
                     "note_ok": bool(hit and hit["note"] and hit["note"]["name"] == c["note"])})
    used = {id(c["found"]) for c in cues if c["found"]}
    quiet = np.ones(n, bool)
    for o in onsets:
        a = int(o["t"] * 200)
        quiet[max(0, a - 10):a + 100] = False
    ebu = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(clip), "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    li = re.findall(r"I:\s+(-?[\d.]+) LUFS", ebu)
    tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", ebu)
    return {"onsets": onsets, "cues": cues, "extra": [o for o in onsets if id(o) not in used],
            "bed_db": round(float(np.median(db[quiet])), 1) if quiet.any() else None,
            "lufs": float(li[-1]) if li else None, "true_peak": float(tp[-1]) if tp else None, "db": db.tolist()}


def summarise(spec: dict, info: dict, v: dict) -> dict:
    rows, geo = v["rows"], v["geo"]
    t = np.array([r["t"] for r in rows])
    head = np.array([np.nan if r["head_pct"] is None else r["head_pct"] for r in rows])
    cam = curve(spec["camera_scale"], t) / 100
    want = curve(spec["head_scale"], t) * cam
    s = {"frames": len(rows)}
    shown = np.where(~np.isnan(head))[0]
    s["appear_s"] = float(t[shown[0]]) if len(shown) else None
    win = (t >= spec["head_scale"][0][0]) & (t <= spec["head_scale"][-1][0] + 0.6) & ~np.isnan(head)
    if win.any():
        k = np.where(win)[0][np.argmax(head[win])]
        s["peak"] = {"t": float(t[k]), "pct": float(head[k])}
        after = win & (t > t[k]) & (t <= t[k] + 0.6)
        if after.any():
            j = np.where(after)[0][np.argmin(head[after])]
            s["dip"] = {"t": float(t[j]), "pct": float(head[j])}
        ok = np.abs(head - want) <= TOL["scale_pct"]
        tail = np.where(~ok & (t > t[k]))[0]
        s["settle_s"] = float(t[tail[-1] + 1]) if len(tail) and tail[-1] + 1 < len(t) else (float(t[k]) if not len(tail) else None)
    k_end = [r["head_pct"] for r in rows[-3:] if r["head_pct"]]
    s["end_head_pct"] = float(np.mean(k_end)) if k_end else None
    gp = [i for i in range(len(t)) if t[i] >= spec["head_scale"][-1][0] + 0.3 and not np.isnan(head[i])]
    if len(gp) > 5:
        slope, icpt = np.polyfit(t[gp], head[gp], 1)
        s["push_pct_per_s"] = round(float(slope), 3)
        s["push_pct_per_s_want"] = round((spec["camera_scale"][-1][1] - spec["camera_scale"][0][1]) / (spec["camera_scale"][-1][0] - spec["camera_scale"][0][0]), 3)
    horn = np.array([r["horn_pct"] for r in rows]) / (cam / cam[-1]) ** 2  # bỏ phần diện tích do máy đẩy
    s["horn_adj"] = horn.round(1).tolist()
    for lab, lvl in (("horn50_s", 50), ("horn95_s", 95)):
        idx = np.where(horn >= lvl)[0]
        s[lab] = float(t[idx[0]]) if len(idx) else None
    rx0, ry0, rx1, ry1 = geo["ref_bbox"]
    cy = geo["h"] / 2
    rel_cam = cam / cam[-1]  # khung neo cuối ứng với cỡ máy ở cuối clip
    drift = [abs(r["bbox"][3] - (cy + (ry1 - cy) * c)) for r, c in zip(rows, rel_cam)
             if r["bbox"] and r["head_pct"] and r["t"] >= (s["appear_s"] or 0) + 0.05]
    s["anchor_drift_pct"] = round(float(max(drift) / (ry1 - ry0) * 100), 2) if drift else None
    s["bg_dev_max"] = int(max(r["bg_dev"] for r in rows))
    s["bg_dev_t"] = float(t[int(np.argmax([r["bg_dev"] for r in rows]))])
    kf = int(np.argmax([r["foreign_pct"] for r in rows]))
    s["foreign_max_pct"] = float(rows[kf]["foreign_pct"])
    s["foreign_t"] = float(t[kf])
    s["foreign_rgb"] = rows[kf]["foreign_rgb"]
    cols = np.array([r["logo_rgb"] for r in rows if r["logo_rgb"]])
    if len(cols):
        s["logo_rgb_median"] = np.median(cols, 0).astype(int).tolist()
        s["logo_rgb_maxdev"] = int(np.abs(cols - hex_rgb(spec["logo"])).max())
    s["want"] = want.tolist()
    return s


def compare_last(last: np.ndarray, geo: dict, logo: np.ndarray) -> dict:
    m = logo_mask(last, logo)
    r = geo["rmask"]
    b, rb = bbox(m), geo["ref_bbox"]
    out = {"iou": round(float((m & r).sum() / max(1, (m | r).sum())), 4),
           "mean_abs_diff": round(float(np.abs(last.astype(int) - geo["ref"].astype(int)).mean()), 2)}
    if b:
        out["center_dx_px"] = round((b[0] + b[2] - rb[0] - rb[2]) / 2, 1)
        out["center_dy_px"] = round((b[1] + b[3] - rb[1] - rb[3]) / 2, 1)
        out["height_pct"] = round((b[3] - b[1]) / (rb[3] - rb[1]) * 100, 2)
    return out


def sheet(keep: dict, path: Path) -> None:
    items = [(k, v) for k, v in keep.items() if k != "cuoi"]
    tw = 320
    th = int(tw * next(iter(keep.values())).shape[0] / next(iter(keep.values())).shape[1])
    cols = 4
    rows = (len(items) + cols - 1) // cols
    img = Image.new("RGB", (cols * tw + (cols + 1) * 10, rows * (th + 30) + 10), (242, 244, 247))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 16)
    for i, (k, f) in enumerate(sorted(items)):
        x, y = 10 + (i % cols) * (tw + 10), 10 + (i // cols) * (th + 30)
        img.paste(Image.fromarray(f).resize((tw, th), Image.LANCZOS), (x, y))
        d.text((x, y + th + 5), f"{k:.2f} s", fill=(10, 10, 10), font=font)
    img.save(path)


def last_vs_ref(last: np.ndarray, ref: np.ndarray, path: Path) -> None:
    diff = np.clip(np.abs(last.astype(int) - ref.astype(int)) * 4, 0, 255).astype(np.uint8)
    w = 480
    parts = [Image.fromarray(a).resize((w, int(w * a.shape[0] / a.shape[1])), Image.LANCZOS) for a in (last, ref, diff)]
    img = Image.new("RGB", (3 * w + 40, parts[0].height + 40), (242, 244, 247))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 16)
    for i, (p, lab) in enumerate(zip(parts, ("Khung cuối của clip", "Khung neo", "Chênh lệch × 4"))):
        img.paste(p, (10 + i * (w + 10), 30))
        d.text((10 + i * (w + 10), 6), lab, fill=(10, 10, 10), font=font)
    img.save(path)


def plot(spec: dict, v: dict, s: dict, a: dict | None, path: Path) -> None:
    rows = v["rows"]
    t = np.array([r["t"] for r in rows])
    fig, ax = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    ax[0].plot(t, [np.nan if r["head_pct"] is None else r["head_pct"] for r in rows], label="Scale đầu chữ U đo được (%)")
    ax[0].plot(t, s["want"], "--", label="Đích theo keyframe × máy đẩy (%)")
    ax[0].plot(t, s["horn_adj"], label="Sừng hiện (% so khung neo, đã trừ máy đẩy)")
    for k in spec["head_scale"]:
        ax[0].axvline(k[0], color="grey", lw=0.6)
    ax[0].set_ylim(0, 130)
    ax[0].legend(loc="lower right", fontsize=8)
    ax[1].plot(t, [r["bg_dev"] for r in rows], label="Nền lệch tối đa ở 4 góc (mức RGB)")
    ax[1].plot(t, [r["foreign_pct"] * 10 for r in rows], label="Màu lạ (% khung × 10)")
    ax[1].axhline(TOL["rgb"], color="red", lw=0.6)
    ax[1].legend(loc="upper right", fontsize=8)
    if a:
        ta = np.arange(len(a["db"])) / 200
        ax[2].plot(ta, a["db"], lw=0.6, label="Mức âm RMS 5 ms (dBFS)")
        for o in a["onsets"]:
            ax[2].plot(o["t"], o["peak_db"], "o", color="black", ms=4)
        for c in spec.get("sfx", []):
            ax[2].axvline(c["t"], color="green", ls="--", lw=0.8)
            ax[2].text(c["t"], -5, c["note"], color="green", fontsize=8)
        ax[2].set_ylim(-80, 0)
        ax[2].legend(loc="lower right", fontsize=8)
    ax[2].set_xlabel("giây")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def verdict(ok: bool | None) -> str:
    return "—" if ok is None else ("Đạt" if ok else "**Chưa đạt**")


def report(clip: Path, spec: dict, info: dict, s: dict, last: dict, a: dict | None, still: dict) -> str:
    asp = info["w"] / info["h"]
    want_asp = spec["aspect"][0] / spec["aspect"][1]
    cam_at = lambda x: float(curve(spec["camera_scale"], np.array([x]))[0])  # noqa: E731
    frgb = "" if not s["foreign_rgb"] else f", màu trung vị {tuple(s['foreign_rgb'])}"
    L = [f"# Đo clip `{clip.name}` theo {spec['shot']}", "",
         f"Clip: {info['w']}×{info['h']}, {info['fps']:.3f} fps, {info['duration']:.2f} s, {info['codec']} {info['pix_fmt']}; "
         f"khai màu {info['color']}. Âm: {info['audio']}.", "",
         "| Mục | Đo được | Đích | Kết luận |", "|---|---|---|---|",
         f"| Tỉ lệ khung | {asp:.4f} | {want_asp:.4f} | {verdict(abs(asp - want_asp) < 0.01)} |",
         f"| Thời lượng | {info['duration']:.2f} s | {spec['duration']:.2f} s | {verdict(abs(info['duration'] - spec['duration']) <= TOL['time_s'])} |",
         f"| Nền lệch tối đa (4 góc) | {s['bg_dev_max']} mức RGB lúc {s['bg_dev_t']:.2f} s | ≤ {TOL['rgb']} | {verdict(s['bg_dev_max'] <= TOL['rgb'])} |",
         f"| Màu lạ (glow, bóng, gradient, màu thêm) | {s['foreign_max_pct']:.3f} % khung lúc {s['foreign_t']:.2f} s{frgb} | "
         f"≤ {TOL['foreign_pct']} % | {verdict(s['foreign_max_pct'] <= TOL['foreign_pct'])} |"]
    if "logo_rgb_median" in s:
        L.append(f"| Màu logo (trung vị) | {tuple(s['logo_rgb_median'])}, lệch tối đa {s['logo_rgb_maxdev']} | {spec['logo']} | {verdict(s['logo_rgb_maxdev'] <= TOL['rgb'])} |")
    if s.get("appear_s") is not None:
        L.append(f"| Đầu chữ U xuất hiện | {s['appear_s']:.2f} s | {spec['head_scale'][0][0]:.2f} s | {verdict(abs(s['appear_s'] - spec['head_scale'][0][0]) <= TOL['time_s'])} |")
    if "peak" in s:
        tp, top = max(((k[0], k[1]) for k in spec["head_scale"]), key=lambda k: k[1])
        vp = top * cam_at(tp) / 100
        L.append(f"| Đỉnh vượt đà | {s['peak']['pct']:.1f} % lúc {s['peak']['t']:.2f} s | {vp:.1f} % lúc {tp:.2f} s | "
                 f"{verdict(abs(s['peak']['pct'] - vp) <= TOL['scale_pct'] and abs(s['peak']['t'] - tp) <= TOL['time_s'])} |")
    if "dip" in s:
        L.append(f"| Đáy hụt | {s['dip']['pct']:.1f} % lúc {s['dip']['t']:.2f} s | theo keyframe | (xem đồ thị) |")
    if s.get("settle_s") is not None:
        tset = spec["head_scale"][-1][0]
        L.append(f"| Bám đường đích (±{TOL['scale_pct']:.0f} %) từ | {s['settle_s']:.2f} s | {tset:.2f} s | {verdict(s['settle_s'] <= tset + TOL['time_s'])} |")
    if s.get("push_pct_per_s") is not None:
        L.append(f"| Máy đẩy sau khi đứng | {s['push_pct_per_s']:+.2f} %/s | {s['push_pct_per_s_want']:+.2f} %/s | "
                 f"{verdict(abs(s['push_pct_per_s'] - s['push_pct_per_s_want']) <= 0.4)} |")
    if "horns" in spec:
        L.append(f"| Sừng hiện 50 % / 95 % | {s['horn50_s']} s / {s['horn95_s']} s | bắt đầu {spec['horns']['start']:.2f} s, đủ {spec['horns']['full']:.2f} s | "
                 f"{verdict(s['horn95_s'] is not None and s['horn95_s'] <= spec['horns']['full'] + TOL['time_s'])} |")
    L.append(f"| Điểm neo đáy giữa (đáy dấu lệch tối đa) | {s['anchor_drift_pct']} % chiều cao dấu | ≤ {TOL['anchor_pct']} % | "
             f"{verdict(s['anchor_drift_pct'] is not None and s['anchor_drift_pct'] <= TOL['anchor_pct'])} |")
    tb = still["totals"]["tinhB"]
    ex = "" if not spec.get("exempt") else f" (miễn {spec['exempt']} s)"
    L.append(f"| Khung đứng yên, thước V2 (Tĩnh B){ex} | {tb} % | ≤ {spec['static_max'] * 100:.0f} % | {verdict(tb <= spec['static_max'] * 100)} |")
    centered = "center_dx_px" in last and abs(last["center_dx_px"]) <= 2 and abs(last["center_dy_px"]) <= 2
    L.append(f"| Khung cuối so khung neo | IoU {last['iou']}, lệch tâm ({last.get('center_dx_px')}, {last.get('center_dy_px')}) px, "
             f"cao {last.get('height_pct')} % | IoU ≥ 0,98, lệch ≤ 2 px | {verdict(last['iou'] >= 0.98 and centered)} |")
    L += ["", "## Âm", ""]
    if a is None:
        L.append("Clip không có âm.")
    else:
        L += [f"Độ to cả clip {a['lufs']} LUFS, đỉnh {a['true_peak']} dBFS. Mức nền giữa các âm (trung vị) {a['bed_db']} dBFS "
              "(trên −50 dBFS là có tiếng ù, tiếng phòng hoặc nhạc nền).", "",
              "| Âm theo prompt | Mốc đích | Mốc đo | Lệch | Nốt đích | Nốt đo | Mức |", "|---|---|---|---|---|---|---|"]
        for c in a["cues"]:
            f = c["found"]
            if f is None:
                L.append(f"| {c['what']} | {c['t']:.2f} s | không thấy | — | {c['note']} | — | — |")
                continue
            beat = "trong 1 khung" if c["on_beat"] else "**lệch nhịp**"
            note = "không có nốt" if not f["note"] else f"{f['note']['name']} ({f['note']['cents']:+d} cent)"
            if f["note"] and not c["note_ok"]:
                note += " **khác**"
            L.append(f"| {c['what']} | {c['t']:.2f} s | {f['t']:.3f} s | {c['dt_ms']:+d} ms ({beat}) | "
                     f"{c['note']} | {note} | {f['peak_db']} dBFS |")
        if a["extra"]:
            L += ["", "Âm thừa (không có trong prompt): " + ", ".join(
                f"{o['t']:.2f} s{'' if not o['note'] else ' ' + o['note']['name']} ({o['peak_db']} dBFS)" for o in a["extra"])]
    L += ["", "## Đứng yên theo ô 2 s (thước V2)", "", "```", v2metrics.summary(still), "```",
          "", "Ảnh kèm: `do-thi.png` (đường cong đo và đích), `khung-moc.png` (khung tại các mốc), `cuoi-vs-khung-neo.png`."]
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("clip", type=Path)
    ap.add_argument("spec", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    out = args.out or (FLOW / "do" / args.clip.stem)
    out.mkdir(parents=True, exist_ok=True)
    info = probe(args.clip)
    v, keep = analyse_video(args.clip, spec, info)
    s = summarise(spec, info, v)
    last = compare_last(keep["cuoi"], v["geo"], hex_rgb(spec["logo"]))
    a = analyse_audio(args.clip, spec, info["fps"]) if info["audio"] else None
    still = v2metrics.run(args.clip, 0.0, [], spec["shot"], exempt=[tuple(x) for x in spec.get("exempt", [])])
    sheet(keep, out / "khung-moc.png")
    last_vs_ref(keep["cuoi"], v["geo"]["ref"], out / "cuoi-vs-khung-neo.png")
    plot(spec, v, s, a, out / "do-thi.png")
    (out / "BAO-CAO.md").write_text(report(args.clip, spec, info, s, last, a, still), encoding="utf-8")
    dump = {"info": info, "summary": {k: x for k, x in s.items() if k not in ("want", "horn_adj")}, "last": last,
            "audio": None if a is None else {k: x for k, x in a.items() if k != "db"},
            "still": {"totals": still["totals"], "windows": still["windows"], "fails": still["fails"]}, "frames": v["rows"]}
    (out / "so-lieu.json").write_text(json.dumps(dump, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(f"Đã đo {len(v['rows'])} khung -> {out}")


if __name__ == "__main__":
    main()
