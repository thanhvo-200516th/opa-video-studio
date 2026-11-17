#!/usr/bin/env python3
"""Luật dựng chốt 2026-11-06: từ khoá nỗi đau, zoom in/out và bộ kiểm tự động trên spec `.craft.json`.

1. `find_pain_in_text` / `find_pain_in_words`: dò từ khoá NỖI ĐAU trong lời (ưu tiên số 1 khi đặt chữ chính và zoom).
2. `zoom_keys`: keyframe zoom in / zoom out cho đoạn nói dài và cú punch ở từ khoá nỗi đau.
3. `audit_spec` (CLI `edit_rules.py audit spec.craft.json [--words words.json] [--manifest M.json] [--pain "a,b"]`; đọc thêm pain.json cạnh spec; dòng cuối `Tổng: N LỖI · M CẢNH BÁO · K CHƯA KIỂM`): đo các luật bằng số liệu trong spec:
   font 4-6; màu chữ phụ; chữ chính phát sáng; mọi điểm cắt có chuyển cảnh; họ chuyển cảnh ưu tiên; zoom ở đoạn
   nói dài; B-roll / footage đủ dày; từ khoá nỗi đau được nhấn.

Con số ghi `# NGƯỠNG` do skill đề xuất (người dùng chưa chốt số): sửa ở đầu file, không sửa rải rác.
Quy ước tên để bộ kiểm nhận ra: clip B-roll / footage đặt tên bắt đầu bằng "B-roll" hoặc "Footage".
"""
from __future__ import annotations

import re
import argparse
import colorsys
import json
import sys
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------- 1. Từ khoá nỗi đau
PAIN_LEXICON = [
    "mất khách", "mất tiền", "mất thời gian", "tốn thời gian", "tốn tiền", "tốn công", "tốn kém", "đốt tiền",
    "không có khách", "không ra đơn", "không biết bắt đầu", "không biết làm", "không biết", "không có thời gian",
    "không hiệu quả", "không ai xem", "không ai mua", "bế tắc", "kiệt sức", "quá tải", "áp lực", "căng thẳng",
    "thất bại", "sai lầm", "lãng phí", "phá sản", "thua lỗ", "thua", "lỗ", "nợ", "chán nản", "bỏ cuộc",
    "mệt mỏi", "khó khăn", "chậm", "trễ", "rủi ro", "bị lừa", "mất", "tốn", "burnout", "stress", "deadline",
    "bỏ tiền túi", "vứt xó", "xa rời thực tế", "tự bơi", "bị ngợp", "chỉ đạo trên mây",
    "đốt ba mươi triệu", "đốt 30 triệu", "mất một nửa đơn hàng", "chậm quá năm phút", "chậm quá 5 phút", "ngại lên hình", "ngâm tin nhắn", "khách rời đi", "ăn mòn lợi nhuận", "sưu tầm công cụ", "loạn não", "rò rỉ từng ngày", "phần mềm rời rạc", "doanh nghiệp thất bại", "quy trình rác", "đống rác nhanh hơn", "nói lan man", "thông điệp rối rắm", "tiền lương vô ích", "nghiện cảm giác", "toát mồ hôi", "việc vẫn tắc",
    "3 giây đã lướt qua", "ba giây đã lướt qua", "văn mẫu công nghiệp", "đơ cứng", "thiếu sức sống", "viết ngô nghê", "sáo rỗng",
    "không biết một chữ", "tốn cả trăm triệu", "mất cả tháng trời", "không có lửa",
    "tốn gần 200 triệu", "tốn gần hai trăm triệu", "bạn ấy xin nghỉ", "dạy lại từ con số 0", "dạy lại từ con số không", "mất trắng quy trình", "quay cuồng",
    "phình quỹ lương", "tuyển thêm người", "dựng thủ công", "cồng kềnh",
    "chờ suốt hai ngày", "chờ suốt 2 ngày", "sai chính tả", "lệch tông màu",
    "khá thô", "thiếu tự nhiên", "câu lệnh chung chung", "hỗn độn", "mày mò lại từ đầu",
    "ngồi nói chay", "lướt qua ngay", "công cốc", "vẽ thủ công", "hết cả ngày",
    "điên đầu nhất", "chờ nó chạy lại", "chat đi chat lại", "đốt sạch hạn mức",
    "hàng trăm lần thử sai", "đè lên mặt", "lặp lại lỗi cũ", "vài tuần loay hoay",
]
# NGƯỠNG
MIN_FONTS, MAX_FONTS = 4, 6          # số font family chữ trong 1 video (luật 2026-11-06)
LONG_TALK_S = 4.0                    # đoạn A-roll liền dài hơn mức này phải có zoom động
MAX_AROLL_ONLY_S = 8.0               # đoạn nói liền không có B-roll / footage dài nhất cho phép
MIN_BROLL_SHARE = 0.25               # B-roll + footage chiếm tối thiểu bao nhiêu thời lượng
# Rule 2 (người dùng chốt 2026-11-11): bỏ luật "≥ 40 % họ flash" — flash / flicker lặp quá nhiều. Thay bằng đa dạng:
MAX_FLASHY_SHARE = 0.25              # tối đa 25 % điểm cắt có nháy sáng / nhấp nháy (planner nhắm 20 %, +B-roll flash)
MIN_DISTINCT_TRANSITIONS = 6         # tối thiểu 6 kiểu chuyển cảnh khác nhau mỗi video
FLASHY_MARKS = ("flash", "flicker", "shutter", "strobe")
MAX_STATIC_TEXT_SHARE = 0.05         # Rule 4: tối đa 5 % lớp chữ đứng yên lúc giữ
MAX_COVER_S = 0.3                    # luật A6 (2026-11-11): ảnh bìa chỉ 0,2–0,3 s đầu video
CAPTION_BAND_MARKS = ("dải tối dưới", "dải tối sau phụ đề", "dải tối vùng phụ đề")   # luật B15: không dải tối dưới chữ phụ
PAIN_WINDOW = (-0.3, 1.5)            # chữ chính và zoom phải rơi trong khoảng này quanh từ khoá nỗi đau
MAX_REAL_FOOTAGE_SHARE = 0.05        # D15: footage thật tối đa 5 % thời lượng B-roll
MIN_REAL_FOOTAGE_SHARE = 0.02        # D15: mục tiêu 2–5 % khi có footage thật (hoặc 100 % Google Flow)
MAX_BROLL_USES_PER_VIDEO = 2         # D8: mỗi clip B-roll tối đa 2 lần trong 1 video
VALID_BROLL_SOURCES = {"flow", "real_footage", "stock", "muse"}


def _norm(s: str) -> str:
    return unicodedata.normalize("NFC", s).lower()


def find_pain_in_text(text: str, extra: list[str] | None = None) -> list[str]:
    """Các cụm nỗi đau trong `text`, theo thứ tự xuất hiện; cụm nằm trong cụm dài hơn thì bỏ."""
    t = _norm(text)
    hits: list[tuple[int, int, str]] = []
    for p in sorted(set(PAIN_LEXICON) | set(extra or []), key=len, reverse=True):
        start = 0
        while (i := t.find(_norm(p), start)) != -1:
            j = i + len(p)
            whole = (i == 0 or not t[i - 1].isalnum()) and (j == len(t) or not t[j].isalnum())
            if whole and not any(a <= i and j <= b for a, b, _ in hits):
                hits.append((i, j, p))
            start = j
    return [p for _, _, p in sorted(hits)]


def find_pain_in_words(words: list, extra: list[str] | None = None) -> list[dict]:
    """`words` = [(chữ, giây_bắt_đầu, ...)] trên timeline -> [{"phrase", "t", "word_index"}]."""
    toks = [_norm(str(w[0])).strip(".,;:!?…\"'()") for w in words]
    out: list[dict] = []
    used: set[int] = set()
    for p in sorted(set(PAIN_LEXICON) | set(extra or []), key=lambda s: -len(s.split())):
        pw = _norm(p).split()
        n = len(pw)
        for i in range(len(toks) - n + 1):
            if toks[i:i + n] == pw and not used & set(range(i, i + n)):
                used.update(range(i, i + n))
                out.append({"phrase": p, "t": float(words[i][1]), "word_index": i})
    return sorted(out, key=lambda d: d["t"])


# ---------------------------------------------------------------- 2. Zoom in / zoom out
def zoom_keys(dur: float, pains: list[float] | tuple = (), base: float = 100.0, push: float = 110.0,
              punch: float = 118.0, period: float = 3.2, fps: int = 30) -> list[list]:
    """Keyframe `scale` (giây từ đầu clip) cho clip nói: zoom in rồi zoom out luân phiên mỗi `period` giây,
    cộng cú punch-in nhanh rồi trả về ở mỗi giây nỗi đau trong `pains`. Luôn nằm trong [base, punch].
    Dùng cho `clip["motion"]["scale"]`; đặt `anchor` / `position` ở tâm mặt riêng."""
    f = 1 / fps
    low = base + 0.35 * (push - base)            # zoom out không về hẳn 100% để không lộ nhịp máy
    keys: list[tuple[float, float, str]] = [(0.0, base, "linear")]
    t, going_in = 0.0, True
    while t + period < dur - f:
        t += period
        keys.append((round(t, 3), push if going_in else low, "easeOut" if going_in else "easeIn"))
        going_in = not going_in
    keys.append((round(dur, 3), push if going_in else low, "linear"))

    def at(x: float) -> float:
        for (t0, v0, _), (t1, v1, _) in zip(keys, keys[1:]):
            if t0 <= x <= t1:
                return v0 + (v1 - v0) * (0 if t1 == t0 else (x - t0) / (t1 - t0))
        return keys[-1][1]

    for p in sorted(x for x in pains if 0.2 <= x <= dur - 0.2):
        a, b = p - 0.12, p + 0.9
        v_a, v_b = at(a), at(b)
        keys = [k for k in keys if not (a - f <= k[0] <= b + f)]
        keys += [(round(a, 3), v_a, "linear"), (round(p + 0.03, 3), punch, "easeOut"), (round(b, 3), v_b, "easeIn")]
    keys.sort(key=lambda k: k[0])
    clean: list[list] = []
    for t_, v, itp in keys:
        if clean and t_ - clean[-1][0] < f * 0.99:
            continue
        clean.append([t_, round(max(base, min(punch, v)), 2), itp])
    return clean


# ---------------------------------------------------------------- 3. Bộ kiểm trên spec
def color_family(c: str | None) -> str | None:
    """Họ màu của `#RRGGBB`: white / grey / red / orange / gold / green / mint / cyan / blue / purple / pink."""
    if not isinstance(c, str) or not c.startswith("#") or len(c) not in (7, 9):
        return None
    r, g, b = (int(c[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h *= 360
    if s < 0.12:
        return "white" if v > 0.6 else "grey"
    if 250 <= h < 345:                           # tím nhạt #D6CCFF vẫn là tím
        return "purple" if h < 300 else "pink"
    if h >= 345 or h < 12:
        return "red" if s >= 0.35 else "white"
    if h < 40:
        return "orange" if s >= 0.35 else "white"
    if h < 70:
        return "gold" if s >= 0.35 else "white"
    if h < 150:
        return "green"
    if h < 180:
        return "mint"
    if h < 215:
        return "cyan"
    return "blue"


GLOW_IDS = {"wonder_glow", "glow", "outer_glow"}


def _lane(track_name: str) -> str:
    parts = track_name.replace("FX ·", "").split()
    return parts[0] if parts else ""


def _has_glow(c: dict) -> bool:
    return any(e.get("effect") in GLOW_IDS for e in c.get("effects", []))


def _scale_animated(c: dict) -> bool:
    sc = (c.get("motion") or {}).get("scale")
    if isinstance(sc, list) and len(sc) >= 2:
        return True
    return any(e.get("effect") == "transform" and isinstance(e["params"].get("scale_height"), list)
               for e in c.get("effects", []))


def _trans_name(clip_name: str) -> str:
    """'Chuyển cảnh flash_burst #3' → 'flash_burst'; 'Tấm màu 1 #4' → 'panel_wipe'."""
    n = re.sub(r"\s*#\d+$", "", clip_name.replace("Chuyển cảnh ", "")).strip()
    return "panel_wipe" if n.startswith("Tấm màu") else n


def _is_broll_clip(track: dict, clip: dict) -> bool:
    if track.get("type") != "video":
        return False
    tn = track.get("name", "")
    if tn.startswith(("trans", "text", "Ảnh bìa", "band", "V2", "V3", "V4")):
        return False
    if clip.get("name", "").lower().startswith(("b-roll", "footage")) or clip.get("broll_source") or tn.startswith("gfx_under"):
        return True
    src = str(clip.get("src") or "")
    if Path(src).suffix.lower() in (".mp4", ".mov", ".mkv", ".webm"):
        fn = Path(src).name.lower()
        return "b-roll" in fn or fn.startswith(("footage", "ftg_", "stock_")) or "06_b-roll" in src.lower()
    return False


def _canon_broll_src(src: str, fallback: str = "") -> str:
    s = str(src or "").replace("\\", "/")
    if not s:
        return fallback.strip().lower()
    s = re.sub(r"/x(?:105|110|115|125)(?=/)", "", s)
    p = Path(s)
    stem = re.sub(r"_x\d{3}$", "", p.stem)
    return str(p.with_name(stem + p.suffix)).lower()


def _origin_from_path(src: str) -> str:
    s = unicodedata.normalize("NFC", str(src or "")).lower().replace("\\", "/")
    fn = Path(s).name
    if "_google_raw" in s or "/flow/" in s:
        return "flow"
    if any(k in s for k in ("04_footage", "soucre thô", "source_tho", "footage_studio")) or re.search(r"(?:^|[/_-])c00(?:\d+|xx)", s) or "img_" in fn:
        return "real_footage"
    if any(k in s for k in ("06_b-roll", "stock_theo_chu_de", "mixkit", "pexels", "pixabay", "ftg_", "stock_")):
        return "stock"
    return "unknown"


def _classify_broll(clip: dict, manifest: dict | None = None, broll_sources: dict | None = None) -> str:
    explicit = str(clip.get("broll_source") or "").strip().lower()
    if explicit in VALID_BROLL_SOURCES:
        return explicit
    src = str(clip.get("src") or "")
    if broll_sources and src:
        fname = Path(src).name
        canon_fname = re.sub(r"_x\d{3}(?=\.[^.]+$)", "", fname)
        entry = broll_sources.get(fname) or broll_sources.get(canon_fname)
        if isinstance(entry, dict):
            esrc = str(entry.get("source") or "").strip().lower()
            if esrc in VALID_BROLL_SOURCES:
                return esrc
            if entry.get("raw"):
                inferred = _origin_from_path(str(entry["raw"]))
                if inferred != "unknown":
                    return inferred
    if manifest and src:
        cstem = re.sub(r"_x\d{3}$", "", Path(src).stem).lower()
        vg_map = {
            "flow": "flow", "google_flow": "flow", "google-flow": "flow", "omni-flash": "flow",
            "real_footage": "real_footage", "live_shoot": "real_footage",
            "stock": "stock", "muse": "muse", "muse_api": "muse",
        }
        for seg in manifest.get("segments", []):
            vf = (seg.get("files") or {}).get("video_file") or ""
            if vf and re.sub(r"_x\d{3}$", "", Path(vf).stem).lower() == cstem:
                msrc = str(seg.get("broll_source") or "").strip().lower()
                if msrc in VALID_BROLL_SOURCES:
                    return msrc
                vg = str((seg.get("api_routing") or {}).get("video_generator") or "").strip().lower()
                if vg in vg_map:
                    return vg_map[vg]
    return _origin_from_path(src)


def _union_dur(intervals: list[tuple[float, float]]) -> float:
    total, last = 0.0, None
    for a, b in sorted(intervals):
        if b <= a:
            continue
        if last is None or a >= last:
            total += b - a
            last = b
        elif b > last:
            total += b - last
            last = b
    return total


def audit_spec(spec: dict, words: list | None = None, extra_pain: list[str] | None = None,
               manifest: dict | None = None, broll_sources: dict | None = None) -> list[dict]:
    """Đo các luật dựng trên spec; trả [{"rule", "status": OK | CẢNH BÁO | LỖI | CHƯA KIỂM, "detail"}].
    extra_pain = cụm nỗi đau riêng của kịch bản (ngoài từ điển) — vd manifest.keywords / pain_keywords."""
    res: list[dict] = []
    tracks = spec.get("tracks", [])
    clips = [(t.get("name", ""), c) for t in tracks for c in t.get("clips", [])]

    def add(rule: str, status: str, detail: str) -> None:
        res.append({"rule": rule, "status": status, "detail": detail})

    # Font 4-6
    fams: dict[str, int] = {}
    for _, c in clips:
        if c.get("font"):
            fams[c["font"]] = fams.get(c["font"], 0) + 1
    n = len(fams)
    add("Font 4-6 mỗi video", "OK" if MIN_FONTS <= n <= MAX_FONTS else "LỖI",
        f"{n} font: " + ", ".join(f"{k} x{v}" for k, v in sorted(fams.items(), key=lambda x: -x[1]))
        + " (chữ vẽ thành PNG như từ khoá template không đếm được)")

    # Màu chữ phụ + chữ chính phát sáng
    bad_cap, glow_ok_cap, key_no_glow, key_n = [], 0, [], 0
    for tn, c in clips:
        lane = _lane(tn)
        if lane == "text_img":                      # từ khoá template: PNG, kiểm phát sáng
            key_n += 1
            if not _has_glow(c):
                key_no_glow.append(c.get("name", "?")[:22])
            continue
        if "text" not in c:
            continue
        fam = color_family(c.get("color"))
        if lane == "text_low":
            if fam in ("orange", "pink", "purple", "red"):
                if _has_glow(c):
                    glow_ok_cap += 1
                else:
                    bad_cap.append(f"{c['text'][:18]} ({fam})")
        elif lane in ("text_top", "text"):
            key_n += 1
            if fam != "white" and not _has_glow(c):
                key_no_glow.append(c["text"][:18])
    add("Chữ phụ: không cam / hồng / tím / đỏ trừ khi phát sáng", "LỖI" if bad_cap else "OK",
        ("; ".join(bad_cap[:6]) if bad_cap else "không có dòng phụ vi phạm")
        + (f" ({glow_ok_cap} dòng dùng màu đó và đã phát sáng)" if glow_ok_cap else ""))
    add("Chữ chính có phát sáng", "CẢNH BÁO" if key_no_glow else "OK",
        f"{key_n} khối chính" + (f"; thiếu phát sáng: {', '.join(key_no_glow[:6])}" if key_no_glow else "; đều có"))

    # Điểm cắt có chuyển cảnh, họ ưu tiên, zoom động
    v1 = next((t for t in tracks if t.get("type") == "video" and t.get("name", "").startswith("V1")), None)
    cuts: list[tuple[float, dict, dict]] = []
    if v1:
        cl = sorted(v1.get("clips", []), key=lambda c: c["at"])
        cuts = [(b["at"], a, b) for a, b in zip(cl, cl[1:])]
    overlays = [c for tn, c in clips if tn.startswith(("FX · trans", "trans "))]   # MotionFX đặt lớp phủ ở "trans N"
    uncovered, kinds, primary = [], [], []
    for t, a, b in cuts:
        tin, tout = b.get("transition_in"), a.get("transition_out")
        near = [c for c in overlays if c["at"] - 0.45 <= t <= c["at"] + c["dur"] + 0.45]
        keyed = any(e.get("effect") == "transform" and isinstance(e["params"].get("scale_height"), list)
                    for e in a.get("effects", []) + b.get("effects", []))
        if not (tin or tout or near or keyed):
            uncovered.append(round(t, 2))
        kinds += [x["effect"] for x in (tin, tout) if x]
        kinds += [c.get("name", "").replace("Chuyển cảnh ", "").strip() for c in near]
        kinds += ["zoom_through"] if keyed else []
        names = [_trans_name(c.get("name", "")) for c in near]                           # kiểu chính của điểm cắt
        primary.append((names[0] if names else (tin or {}).get("effect") or ("zoom_through" if keyed else (tout or {}).get("effect"))) or "?")
    if not cuts:
        add("Mọi điểm cắt có chuyển cảnh", "CHƯA KIỂM", "không tìm thấy track V1 có từ 2 clip")
    else:
        add("Mọi điểm cắt có chuyển cảnh", "LỖI" if uncovered else "OK",
            f"{len(cuts)} điểm cắt trên V1" + (f"; thiếu ở {uncovered[:8]} s" if uncovered else "; đều có"))
    if primary:
        flashy = sum(1 for k in primary if any(m in k.lower() for m in FLASHY_MARKS))
        share, distinct = flashy / len(primary), len(set(primary))
        adjacent = sum(1 for x, y in zip(primary, primary[1:]) if x == y)
        bad = share > MAX_FLASHY_SHARE or distinct < min(MIN_DISTINCT_TRANSITIONS, len(primary)) or adjacent
        add("Chuyển cảnh đa dạng (flash / flicker ≤ 25 %, ≥ 6 kiểu, không lặp liền)", "CẢNH BÁO" if bad else "OK",
            f"nháy sáng {flashy}/{len(primary)} = {share:.0%} · {distinct} kiểu · lặp liền {adjacent}; dùng: "
            + ", ".join(sorted(set(primary))[:12]))
    if v1:
        long_c = [c for c in v1["clips"] if c["dur"] >= LONG_TALK_S      # chỉ đoạn người nói, không tính B-roll / footage
                  and not c.get("name", "").lower().startswith(("b-roll", "footage"))]
        flat = [round(c["at"], 1) for c in long_c if not _scale_animated(c)]
        add("Zoom in / out ở đoạn nói dài", "CẢNH BÁO" if flat else "OK",
            f"{len(long_c)} đoạn >= {LONG_TALK_S:.0f} s" + (f"; đứng yên ở {flat[:8]} s" if flat else "; đều có zoom động"))

    # B-roll / footage
    end = spec.get("duration") or max((c["at"] + c["dur"] for _, c in clips), default=0)
    broll_items = [(t, c) for t in tracks for c in t.get("clips", []) if _is_broll_clip(t, c)]
    br = sorted(((c["at"], c["at"] + c["dur"]) for _, c in broll_items))
    covered, last, worst = 0.0, 0.0, (0.0, 0.0)
    for a, b in br + [(end, end)]:
        worst = max(worst, (a - last, last))
        covered += max(0.0, b - max(a, last))
        last = max(last, b)
    share = covered / end if end else 0
    ok = br and share >= MIN_BROLL_SHARE and worst[0] <= MAX_AROLL_ONLY_S
    w0, w1 = worst[1], worst[1] + worst[0]
    said = " ".join(str(w[0]) for w in (words or []) if w0 - 1e-3 <= float(w[1]) < w1)   # lời nói trong đoạn trơ dài nhất
    add("Nhiều B-roll / footage", "OK" if ok else "CẢNH BÁO",
        f"{len(br)} cảnh = {share:.0%} thời lượng (ngưỡng >= {MIN_BROLL_SHARE:.0%}); đoạn nói liền dài nhất "
        f"{worst[0]:.1f} s ({w0:.1f}–{w1:.1f} s" + (f": «{said[:90]}»" if said else "") + f", ngưỡng <= {MAX_AROLL_ONLY_S:.0f} s)")

    # D8: mỗi clip B-roll tối đa 2 lần trong 1 video
    if not broll_items:
        add("Mỗi clip B-roll tối đa 2 lần trong 1 video", "OK", "chưa có B-roll trong spec")
    else:
        by_src: dict[str, list[tuple[float, float]]] = {}
        for _, c in broll_items:
            key = _canon_broll_src(c.get("src", ""), c.get("name", ""))
            by_src.setdefault(key, []).append((float(c["at"]), float(c["at"]) + float(c["dur"])))
        over_uses = []
        for key, segs in sorted(by_src.items()):
            merged: list[list[float]] = []
            for a, b in sorted(segs):
                if merged and a <= merged[-1][1] + 0.15:
                    merged[-1][1] = max(merged[-1][1], b)
                else:
                    merged.append([a, b])
            if len(merged) > MAX_BROLL_USES_PER_VIDEO:
                over_uses.append(f"{Path(key).name or key} x{len(merged)}")
        add("Mỗi clip B-roll tối đa 2 lần trong 1 video", "LỖI" if over_uses else "OK",
            ("vượt quá 2 lần: " + ", ".join(over_uses[:6])) if over_uses else f"{len(by_src)} clip B-roll, đều ≤ {MAX_BROLL_USES_PER_VIDEO} lần")

    # D15: B-roll Google Flow mặc định (100%); footage thật ≤ 5 %
    total_broll = _union_dur([(float(c["at"]), float(c["at"]) + float(c["dur"])) for _, c in broll_items])
    if total_broll <= 0:
        add("B-roll Google Flow mặc định (100%); footage thật ≤ 5 %", "OK", "chưa có B-roll trong spec")
    else:
        by_cat: dict[str, list[tuple[float, float]]] = {k: [] for k in ("flow", "real_footage", "stock", "muse", "unknown")}
        for _, c in broll_items:
            cat = _classify_broll(c, manifest=manifest, broll_sources=broll_sources)
            by_cat.setdefault(cat, []).append((float(c["at"]), float(c["at"]) + float(c["dur"])))
        durs = {k: _union_dur(v) for k, v in by_cat.items()}
        real_share = durs["real_footage"] / total_broll
        flow_share = durs["flow"] / total_broll
        if real_share > MAX_REAL_FOOTAGE_SHARE + 1e-9 or durs["stock"] > 0 or durs["muse"] > 0:
            status_d15 = "LỖI"
        elif durs["unknown"] > 0:
            status_d15 = "CẢNH BÁO"
        else:
            status_d15 = "OK"
        parts = [f"Flow {flow_share:.0%} ({durs['flow']:.1f} s)",
                 f"footage thật {real_share:.1%} ({durs['real_footage']:.1f} s, ≤ {MAX_REAL_FOOTAGE_SHARE:.0%})"]
        if durs["stock"] > 0:
            parts.append(f"stock {durs['stock']:.1f} s (cấm)")
        if durs["muse"] > 0:
            parts.append(f"muse {durs['muse']:.1f} s (cấm mặc định)")
        if durs["unknown"] > 0:
            parts.append(f"chưa rõ nguồn {durs['unknown']:.1f} s")
        elif 0 < real_share < MIN_REAL_FOOTAGE_SHARE:
            parts.append(f"mục tiêu khi dùng footage thật {MIN_REAL_FOOTAGE_SHARE:.0%}–{MAX_REAL_FOOTAGE_SHARE:.0%}")
        add("B-roll Google Flow mặc định (100%); footage thật ≤ 5 %", status_d15,
            f"tổng {total_broll:.1f} s: " + " · ".join(parts))

    # Từ khoá nỗi đau
    if words is None:
        add("Từ khoá nỗi đau được nhấn", "CHƯA KIỂM", "thiếu --words: danh sách [chữ, giây] trên timeline")
    else:
        hits = find_pain_in_words(words, extra_pain)
        keys = [c for tn, c in clips if _lane(tn) in ("text_top", "text_img", "text")]
        zooms = [c for _, c in clips if _scale_animated(c)]
        miss = []
        for h in hits:
            lo, hi = h["t"] + PAIN_WINDOW[0], h["t"] + PAIN_WINDOW[1]
            hit_t = any(c["at"] <= hi and c["at"] + c["dur"] >= lo for c in keys)
            hit_z = any(c["at"] <= hi and c["at"] + c["dur"] >= lo for c in zooms)
            if not (hit_t and hit_z):
                why = " + ".join(x for x, ok_ in (("thiếu chữ chính", hit_t), ("thiếu zoom", hit_z)) if not ok_)
                miss.append(f"«{h['phrase']}» {h['t']:.1f}s ({why})")
        if not hits:
            add("Từ khoá nỗi đau được nhấn", "CHƯA KIỂM", "lời không có từ nào trong từ điển nỗi đau: kiểm lại từ điển")
        else:
            add("Từ khoá nỗi đau được nhấn", "CẢNH BÁO" if miss else "OK",
                f"{len(hits)} từ khoá nỗi đau" + (f"; chưa đủ chữ + zoom: {'; '.join(miss[:5])}" if miss else "; đều có chữ chính + zoom"))
    # Rule 4 (2026-11-11): chữ không tĩnh — mọi lớp chữ có kiểu vào và chuyển động lúc giữ (text_motion)
    from text_motion import static_report
    sr = static_report(tracks, float(spec.get("fps", 30)))
    if sr["total"]:
        flat_share = sr["static_hold"] / sr["total"]
        add("Chữ có chuyển động (vào + giữ, không tĩnh)",
            "CẢNH BÁO" if sr["no_entrance"] or flat_share > MAX_STATIC_TEXT_SHARE else "OK",
            f"{sr['total']} lớp chữ · thiếu kiểu vào {sr['no_entrance']} · đứng yên lúc giữ {sr['static_hold']} "
            f"({flat_share:.0%}, ngưỡng {MAX_STATIC_TEXT_SHARE:.0%})")
    # B15 (2026-11-11): không dải tối dưới chữ phụ · A6: ảnh bìa ≤ 0,3 s
    bands = [c.get("name", tn) for tn, c in clips
             if any(m in (tn + " " + c.get("name", "")).lower() for m in CAPTION_BAND_MARKS)]
    add("Không dải tối dưới chữ phụ", "CẢNH BÁO" if bands else "OK",
        "không có" if not bands else f"{len(bands)} lớp dải tối dưới phụ đề: bỏ (luật B15)")
    covers = [c for tn, c in clips if tn.lower().startswith("ảnh bìa") or c.get("name", "").lower() == "ảnh bìa"]
    long_cov = [round(c["dur"], 2) for c in covers if c["dur"] > MAX_COVER_S + 1e-3]
    if covers:
        add("Ảnh bìa ≤ 0,3 s đầu video", "CẢNH BÁO" if long_cov else "OK",
            f"ảnh bìa {', '.join(str(round(c['dur'], 2)) for c in covers)} s" + (" — rút về 0,2–0,3 s (luật A6)" if long_cov else ""))
    # B13: chữ hiện trên hình không có dấu phẩy (trừ dấu phẩy thập phân giữa hai số)
    comma = [str(c["text"])[:24] for _, c in clips if re.search(r"(?<!\d),|,(?!\d)", str(c.get("text", "")))]
    add("Chữ trên hình không có dấu phẩy", "OK" if not comma else "LỖI",
        "không có" if not comma else f"{len(comma)} chữ còn dấu phẩy: " + "; ".join(comma[:4])
        + " (chữ vẽ thành PNG như từ khoá template không kiểm được qua spec)")

    return res


def _cli() -> int:
    ap = argparse.ArgumentParser(description="Luật dựng 2026-11-06: nỗi đau, zoom, bộ kiểm spec")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("audit", help="đo các luật dựng trên spec .craft.json")
    a.add_argument("spec")
    a.add_argument("--words", help="JSON [[chữ, giây_timeline], ...] để kiểm từ khoá nỗi đau")
    a.add_argument("--manifest", help="00_storyboard_manifest.json: lấy keywords + pain_keywords làm nỗi đau riêng "
                                      "(cộng pain.json cạnh spec nếu có — build_spec_q ghi EXTRA_PAIN + keywords đã dùng)")
    a.add_argument("--pain", help="cụm nỗi đau riêng, phân tách bằng dấu phẩy: \"gãy gánh,chạm trần\"")
    a.add_argument("--json", action="store_true")
    p = sub.add_parser("pain", help="dò từ khoá nỗi đau trong một câu")
    p.add_argument("text")
    args = ap.parse_args()
    if args.cmd == "pain":
        print(json.dumps(find_pain_in_text(args.text), ensure_ascii=False))
        return 0
    spec_path = Path(args.spec).resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    words = json.loads(Path(args.words).read_text(encoding="utf-8")) if args.words else None
    extra = [x.strip() for x in (args.pain or "").split(",") if x.strip()]
    search_dirs = list(spec_path.parents[:3])
    manifest_data = None
    if args.manifest:
        manifest_data = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        for seg in manifest_data.get("segments", []):
            extra += [*(seg.get("keywords") or []), *(seg.get("pain_keywords") or [])]
    else:
        for d in search_dirs:
            mp = d / "00_storyboard_manifest.json"
            if mp.is_file():
                manifest_data = json.loads(mp.read_text(encoding="utf-8"))
                break
    broll_sources = None
    for d in search_dirs:
        sp = d / "_broll_sources.json"
        if sp.is_file():
            broll_sources = json.loads(sp.read_text(encoding="utf-8"))
            break
    pain_file = spec_path.parent / "pain.json"      # build_spec_q ghi cạnh spec: E1 khỏi quên --pain
    if pain_file.is_file():
        extra += [str(x) for x in json.loads(pain_file.read_text(encoding="utf-8")).get("pain", [])]
    res = audit_spec(spec, words, sorted(set(extra)) or None, manifest=manifest_data, broll_sources=broll_sources)
    count = {k: sum(1 for r in res if r["status"] == k) for k in ("LỖI", "CẢNH BÁO", "CHƯA KIỂM")}
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        for r in res:
            print(f"[{r['status']:<9}] {r['rule']:<62} {r['detail']}")
        if pain_file.is_file():
            print(f"(nỗi đau: đọc thêm {pain_file})")
        print(f"Tổng: {count['LỖI']} LỖI · {count['CẢNH BÁO']} CẢNH BÁO · {count['CHƯA KIỂM']} CHƯA KIỂM")
    return 1 if count["LỖI"] else 0


if __name__ == "__main__":
    sys.exit(_cli())
