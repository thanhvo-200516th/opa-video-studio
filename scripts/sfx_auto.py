"""Tự chọn và đặt SFX theo hiệu ứng chữ, chuyển cảnh và giọng nói (2026-11-04).

    from sfx_auto import plan_sfx
    clips = plan_sfx(fx.cues, words, end=END, name="THCN08")      # words = [(chữ, giây bắt đầu, giây kết thúc)]
    tracks = [{"type": "audio", "name": f"SFX {i+1}", "clips": c} for i, c in enumerate(pack(clips, 4))]

Luật (references/motion-fx.md, mục SFX):
- `kind` của cue → nhóm file trong assets/motion-fx/sfx_catalog.json; chọn lần lượt, không lặp file khi còn file khác,
  cùng file chỉ dùng lại khi cách ≥ 6 s (rules.md mục 3). Mỗi click trong một chùm (ô lưới, dải, từng từ, cắt nhanh)
  là một file khác (người dùng chốt 2026-11-04 lần 10 — trước đó cả chùm chung một file như mẫu 1cho).
- Mức đỉnh theo tầng (big / mid / soft) và theo giọng: đang nói thì nhỏ hơn ~5 dB so với lúc ngừng.
- Hai cue cách nhau < 0,06 s: giữ cue tầng cao hơn (một khoảnh khắc hình = một tiếng chính).
- `type`, `pen`, `charge`, `riser` cắt theo độ dài hiệu ứng (`dur`) và giảm dần 0,08 s.
- SFX mở đầu khung 0 (rules.md mục 7): một cặp trong `opening`, chọn theo tên video để mỗi video một kiểu.
"""
from __future__ import annotations

import json
import os
import subprocess
import zlib
from pathlib import Path

from build_kit import sfx_clip, sfx_info

CATALOG = Path(__file__).resolve().parent.parent / "assets/motion-fx/sfx_catalog.json"
TIER_RANK = {"big": 3, "mid": 2, "soft": 1}
REUSE_GAP = 6.0


def _load(catalog: Path = CATALOG) -> dict:
    c = json.loads(catalog.read_text())
    tnedit_env = os.environ.get("TNEDIT_DIR")
    home_str = str(Path.home()) + "/"
    roots = {}
    for k, v in c["roots"].items():
        if tnedit_env and "/Thanh/Media/TNEDIT" in v:
            v = v.split("/Thanh/Media/TNEDIT", 1)[0]
            v = tnedit_env + c["roots"][k].split("/Thanh/Media/TNEDIT", 1)[1]
        elif v.startswith("/home/vmiz/"):
            v = home_str + v[len("/home/vmiz/"):]
        roots[k] = v

    def path(ref: str) -> str:
        if ref.startswith("/"):
            return ref
        k, rel = ref.split(":", 1)
        return str(Path(roots[k]) / rel)

    c["_path"] = path
    return c


AUDIO_CACHE = Path.home() / ".cache/master-video-edit/sfx_from_video"


def audio_of(src: str) -> str:
    """FilmCraft không cho file video lên track âm thanh → tách tiếng ra WAV 48 kHz (-1.2 dB chống clipping đỉnh 0 dBFS)."""
    if not src.lower().endswith((".mp4", ".mov", ".mkv", ".webm", ".m4v")):
        return src
    AUDIO_CACHE.mkdir(parents=True, exist_ok=True)
    out = AUDIO_CACHE / (Path(src).stem[:55] + "_norm.wav")
    if not out.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-af", "volume=-1.2dB", "-ac", "2", "-ar", "48000", str(out)], check=True)
    return str(out)


def seg_peak_db(src: str, s_in: float, dur: float) -> float:
    """Đỉnh (dBFS) của đúng đoạn dùng — file overlay dài có chỗ vỡ ở đoạn khác, đo cả file sẽ đặt mức sai."""
    import numpy as np
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{s_in:.3f}", "-t", f"{dur:.3f}", "-i", src, "-f", "s16le",
                          "-ac", "1", "-ar", "48000", "-"], capture_output=True, check=True).stdout
    x = np.abs(np.frombuffer(pcm, np.int16).astype(np.float32) / 32768)
    return float(20 * np.log10(max(float(x.max()) if len(x) else 0.0, 1e-6)))


def voice_active(t: float, words: list[tuple], pad: float = 0.08) -> bool:
    return any(s - pad <= t <= e + pad for _, s, e in words)


def _thin(cues: list[dict], kinds: dict) -> tuple[list[dict], list[str]]:
    """Bỏ cue không có trong catalog; hai cue sát nhau (< 0,06 s) giữ cái tầng cao hơn."""
    skipped = sorted({q["kind"] for q in cues if q["kind"] not in kinds})
    cs = sorted((q for q in cues if q["kind"] in kinds), key=lambda q: q["t"] + kinds[q["kind"]].get("offset", 0))
    # tiếng nền và các lớp tiếng chuyển cảnh (hút vào + hit + màn trập…) luôn giữ — trước đây hit bị loại vì trùng mốc
    beds = [q for q in cs if kinds[q["kind"]].get("bed") or kinds[q["kind"]].get("transition")]
    cs = [q for q in cs if not (kinds[q["kind"]].get("bed") or kinds[q["kind"]].get("transition"))]
    keep: list[dict] = []
    for q in cs:
        t = q["t"] + kinds[q["kind"]].get("offset", 0)
        prev = keep[-1] if keep else None
        if prev and abs(t - (prev["t"] + kinds[prev["kind"]].get("offset", 0))) < 0.06:
            if TIER_RANK[kinds[q["kind"]]["tier"]] > TIER_RANK[kinds[prev["kind"]]["tier"]]:
                keep[-1] = q
            continue
        keep.append(q)
    return sorted(keep + beds, key=lambda q: q["t"]), skipped


def _pick(kind: str, t: float, files: list[str], last_used: dict, cursor: dict) -> str:
    """File kế tiếp trong nhóm; tránh file đã dùng trong REUSE_GAP giây."""
    n = len(files)
    for k in range(n):                       # ưu tiên file chưa dùng lần nào trong video (luật không lặp take cả video)
        f = files[(cursor.get(kind, 0) + k) % n]
        if f not in last_used:
            cursor[kind] = (cursor.get(kind, 0) + k + 1) % n
            return f
    for k in range(n):
        f = files[(cursor.get(kind, 0) + k) % n]
        if t - last_used.get(f, -1e9) >= REUSE_GAP:
            cursor[kind] = (cursor.get(kind, 0) + k + 1) % n
            return f
    f = min(files, key=lambda x: last_used.get(x, -1e9))
    return f


def duck(base_db: float, times: list[float], end: float, depth: float = -5.0, pre: float = 0.15,
         post: float = 0.45) -> list:
    """Keyframe gain cho nhạc nền: hạ `depth` dB quanh mỗi điểm chuyển cảnh để tiếng chuyển cảnh nổi lên."""
    keys = [[0, base_db]]
    for t in sorted(times):
        a, b = max(0.0, t - pre), min(end, t + post)
        if a <= keys[-1][0] + 0.05:
            continue
        keys += [[round(a - 0.05, 3), base_db], [round(a, 3), base_db + depth], [round(b, 3), base_db + depth],
                 [round(min(end, b + 0.2), 3), base_db]]
    if keys[-1][0] < end - 0.85:
        keys += [[round(end - 0.8, 3), base_db], [round(end, 3), -45]]
    elif keys[-1][0] < end - 1e-3:
        keys.append([round(end, 3), -45])
    else:
        keys[-1] = [round(end, 3), -45]
    return keys


def plan_sfx(cues: list[dict], words: list[tuple], end: float, name: str, opening: bool = True,
             catalog: Path = CATALOG, gain_offset: float = 0.0, opening_pair: int | None = None) -> list[dict]:
    """Trả list clip SFX cho spec craft-handoff. words = [(chữ, start, end)] trên timeline (để biết lúc đang nói)."""
    c = _load(catalog)
    kinds, path, levels = c["kinds"], c["_path"], c["levels"]
    own = [q for q in cues if q.get("src")]                  # tiếng có sẵn trong overlay (film burn…): khớp hình sẵn
    cues, skipped = _thin([q for q in cues if not q.get("src")], kinds)
    if skipped:
        print("sfx_auto: bỏ qua kind không có trong catalog:", ", ".join(skipped))
    last_used: dict = {}
    cursor: dict = {}
    out: list[dict] = []
    if opening:
        pairs = c["opening"]["pairs"]
        # opening_pair: chỉ số do sổ luân phiên (rotation.py) cấp cho cả lô; không có → theo tên video như cũ
        pair = pairs[(zlib.crc32(name.encode()) if opening_pair is None else opening_pair) % len(pairs)]
        for i, ref in enumerate(pair):
            p = path(ref)
            clip = sfx_clip("MỞ ĐẦU", p, 0.0, "onset", -9 + gain_offset, max_dur=0.35 if i == 0 else 0.6, end=end)
            clip["at"] = 0.0
            clip["name"] = f"SFX MỞ ĐẦU · {Path(p).stem[:24]}"
            out.append(clip)
            last_used[p] = 0.0
    for q in own:
        speaking = voice_active(q["t"] + q["dur"] / 2, words)
        src = audio_of(q["src"])
        g = round(levels["transition"][0 if speaking else 1] + gain_offset - seg_peak_db(src, q["in"], q["dur"]), 1)
        out.append({"src": src, "at": round(q["t"], 4), "in": round(q["in"], 3), "dur": round(min(q["dur"], end - q["t"]), 3),
                    "gain_db": g, "name": f"SFX {q.get('why', 'overlay')[:30]}"})
    for q in cues:
        k = kinds[q["kind"]]
        t = max(0.0, q["t"] + k.get("offset", 0))
        if opening and t < 0.3:
            continue                                   # khung đầu đã có SFX mở đầu
        cand_files = [path(f) for f in k["files"]]
        if all(f in last_used for f in cand_files) and q["kind"] in ("grid_click", "bar_click", "word_click", "pop"):
            cand_files += [path(f) for f in kinds["word_click"]["files"] if path(f) not in cand_files]
        p = _pick(q["kind"], t, cand_files, last_used, cursor)   # mỗi click một file khác
        speaking = voice_active(t, words)
        lv = levels["transition"] if k.get("transition") else levels[k["tier"]]
        peak = lv[0 if speaking else 1] + gain_offset
        max_dur = k.get("max_dur")
        if k.get("trim") and q.get("dur"):
            max_dur = max(0.12, q["dur"] + 0.1)
        src_in = None
        max_pre = q.get("max_pre", k.get("max_pre"))
        if max_pre is not None and k["align"] == "peak":         # không cho tiếng vang trước khi hình bắt đầu
            info = sfx_info(p)
            if info["peak_t"] - info["lead"] > max_pre:
                src_in = round(info["peak_t"] - max_pre, 3)
        clip = sfx_clip(q["kind"], p, t, k["align"], peak, max_dur=max_dur, end=end, src_in=src_in)
        if src_in is not None:                                   # vào giữa tiếng: lên nhanh 2 khung, khỏi 'bụp'
            g0 = clip["gain_db"] if not isinstance(clip["gain_db"], list) else clip["gain_db"][0][1]
            clip["gain_db"] = [[0, -30], [min(0.066, clip["dur"] / 3), g0], *([[clip["dur"], g0]] if not isinstance(clip["gain_db"], list) else clip["gain_db"][1:])]
        if (max_dur and not isinstance(clip["gain_db"], list) and clip["dur"] >= max_dur - 1e-3
                and sfx_info(p)["tail"] > max_dur):
            g = clip["gain_db"]
            fade = min(0.08, clip["dur"] * 0.5)          # ≥ 1 khung giữa các key, nếu không fc_build gộp key
            if clip["dur"] - fade >= 1 / 30:
                clip["gain_db"] = [[0, g], [round(clip["dur"] - fade, 3), g], [clip["dur"], -40]]
        clip["name"] = f"SFX {q['kind']} · {q.get('why', '')[:22]}"
        out.append(clip)
        last_used[p] = t
        if k.get("with"):                              # lớp chồng cùng mốc (flash = thump + màn trập)
            kw = kinds[k["with"]]
            p2 = _pick(k["with"], t, [path(f) for f in kw["files"]], last_used, cursor)
            c2 = sfx_clip(k["with"], p2, t, kw["align"], levels[kw["tier"]][0 if speaking else 1] + gain_offset,
                          max_dur=kw.get("max_dur"), end=end)
            c2["name"] = f"SFX {k['with']} · lớp của {q['kind']}"
            out.append(c2)
            last_used[p2] = t
    # Đảm bảo tuyệt đối không trùng (src, in) sau khi snap về frame 30fps (tránh lỗi repeated_takes ở audit-sfx)
    seen_takes: set[tuple[str, int]] = set()
    dedup_out: list[dict] = []
    for cl in out:
        key = (cl["src"].casefold(), round(float(cl.get("in", 0.0)) * 30))
        if key in seen_takes:
            continue
        seen_takes.add(key)
        dedup_out.append(cl)
    return dedup_out
