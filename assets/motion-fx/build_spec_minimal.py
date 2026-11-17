#!/usr/bin/env python3
"""MẪU dựng spec hồ sơ minimal-edu cho skill opa-video-studio (SKILL §3 bước 8, sau build_spec_q.py). Chép vào
<thư mục video>/<phiên bản>/work/, CHỈ sửa các dòng / khối `# EDIT:` (GROUPS, HEAD_TOP, SCENE_GFX, CTA_WORD, PAIN), rồi chạy:
    OPA_SKILL_DIR=<thư mục skill> $PY work/build_spec_minimal.py

Bước 8 của §3: chạy build_spec_q.py trước (ra work/<mã>.craft.json + work/words_tl.json), ĐỔI TÊN <mã>.craft.json → <mã>.base.craft.json,
rồi chạy mẫu này. Mẫu lấy V1 / giọng / nhạc của bản nền, dựng lại chữ + đồ hoạ + chuyển cảnh theo hồ sơ minimal-edu.
Đọc : work/<mã>.base.craft.json (đúng 1 file *.base.craft.json) · work/words_tl.json · work/profile.json ({"profile": "minimal-edu"};
      thiếu / sai → dừng) · work/pain.json nếu PAIN trống.
Ghi : work/<mã>.craft.json (spec cuối; levels / lint / audit chạy sau) · <phiên bản>/gfx/ (PNG, .mov đồ hoạ).
Số cảnh = 2 chữ số đầu tên file V1 (thư mục đánh số, "b-roll" trong đường dẫn = B-roll).

GROUPS: mỗi chuỗi = một cụm chữ "nhỏ | nhỏ | *từ lớn sans | nhỏ"; `*` = từ lớn sans, `~` = từ lớn serif (đúng 1 từ lớn mỗi cụm; chữ
  phải khớp tuần tự với lời trong words_tl.json); None = bỏ qua cả cảnh đang tới (cảnh quote toàn chữ do SCENE_GFX dựng).
SCENE_GFX (tuỳ chọn, theo thứ tự cảnh):
  ("polaroid", số_cảnh, giây)                       nền giấy + polaroid khung hình của cảnh, chữ phía trên
  ("arrow", "từ", số_cảnh)                          mũi tên cong vẽ dần từ lời «từ», giữ tới hết cảnh
  ("graph", "từ bắt đầu", số_cảnh, ["từ1", ...])    cảnh đồ thị từ lời «từ bắt đầu» tới hết cảnh, mỗi bậc một từ số liệu
  ("quote", số_cảnh, ["dòng 1", ...], chỉ_số_dòng_nhấn)   thẻ trích dẫn (cảnh toàn chữ)
CTA_WORD: từ lớn trắng trên hộp xanh (box_wipe), None = không có. PAIN: cụm nỗi đau → key_hit (trống = đọc work/pain.json).

# --- VÍ DỤ KB08 (bỏ dấu "# " đầu dòng để dùng; test_build_spec_minimal.py chạy đúng khối này) ---
# HEAD_TOP = 296
# GROUPS = [
#     "Bán | bất động sản | *tiền tỷ",
#     "mà video | chỉ đứng | *chỉ tay", "vào | *bãi đất trống", "lấy gì | *thuyết phục", "nhà đầu tư | *xuống tiền?",
#     "*Tâm lý | nhà đầu tư | cầm tiền tỷ", "*khác hoàn toàn | khách mua hàng lẻ",
#     "Họ cần | nhìn thấy | *vị trí quy hoạch", "và | bài toán | *dòng tiền", "*rõ mồn một | trên màn hình",
#     "chứ | nghe | *nói miệng", "là họ | ~quên ngay",
#     "Cách mình | áp dụng | *hệ thống", "vào làm | *video | bất động sản", "diễn ra | rất | ~mạch lạc",
#     "Ngay khi | giọng nói | nhắc đến | *vị trí", "hệ thống | tự bật | *bản đồ vệ tinh",
#     "*khoanh vùng | khu đất | phát sáng", "và vẽ | *đường kết nối | ra trung tâm",
#     "Tiếp đó | khi phân tích | ~tài chính", "*biểu đồ | vốn tự có", "và | *dòng tiền thuê", "tự động | *bung ra",
#     "khớp | từng | *con số",
#     "Khi | vị trí quy hoạch | được | *khoanh vùng", "và | *bảng tính | ngân hàng | nhảy số", "khớp | từng | ~lời tư vấn",
#     None,  # cảnh 11: quote card
#     "Anh em nào | đang làm | *bất động sản", "hoặc | *tư vấn đầu tư", "muốn | thử áp dụng | *hiệu ứng",
#     "*khoanh bản đồ | và | bảng tính tài chính", "cho | *dự án | đang bán", "cứ nhắn chữ | *Bất Động Sản | ở dưới",
#     "Mình gửi | *mẫu cấu hình | sẵn", "để anh em | thay | *thông số", "vào | ~chạy thử",
# ]
# SCENE_GFX = [("polaroid", 7, 1.6), ("arrow", "vẽ", 8), ("graph", "biểu", 9, ["vốn", "dòng", "bung", "con"]),
#              ("quote", 11, ["Độ tin cậy tăng lên", "gấp mười lần", "so với video cắt ghép"], 1)]
# CTA_WORD = "Bất Động Sản"
# PAIN = ["bãi đất trống", "quên ngay"]
# --- hết ví dụ ---
"""
from __future__ import annotations

import copy
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from types import SimpleNamespace

SKILL = Path(os.environ.get("OPA_SKILL_DIR") or Path(__file__).resolve().parents[2])
if not (SKILL / "scripts/build_kit.py").is_file():
    sys.exit(f"Không thấy skill ở {SKILL}: đặt OPA_SKILL_DIR=<thư mục skill opa-video-studio>")
sys.path.insert(0, str(SKILL / "scripts"))
import brooks_text as BT  # noqa: E402
import draw_path as DP  # noqa: E402
import fx_gfx as G  # noqa: E402
import style_profile as sp  # noqa: E402
import th_transitions as TH  # noqa: E402
from build_kit import clamp_keys, pack, retime_cuts  # noqa: E402
from cut_plan import Cut, plan_cuts_min  # noqa: E402
from motion_fx import MotionFX  # noqa: E402
from sfx_auto import plan_sfx  # noqa: E402
from text_fx import HEAD_TOP as _HEAD_TOP  # noqa: E402
from text_motion import EntranceStyles, ensure_motion  # noqa: E402

# ---------------------------------------------------------------- CHỈ SỬA CÁC DÒNG / KHỐI `# EDIT:`
HEAD_TOP = _HEAD_TOP  # EDIT: đỉnh đầu người nói (px, khung 1080x1920) cho vùng chữ A-roll; đo bằng frame_person.py analyze
GROUPS = [  # EDIT: cụm chữ "nhỏ | nhỏ | *từ lớn", None = bỏ qua cảnh (xem ví dụ KB08 ở đầu file)
]
SCENE_GFX = []  # EDIT: đồ hoạ theo cảnh: ("polaroid", cảnh, giây) · ("arrow", "từ", cảnh) · ("graph", "từ bắt đầu", cảnh, [từ…]) · ("quote", cảnh, [dòng…], chỉ_số_nhấn)
CTA_WORD = None  # EDIT: từ lớn trên hộp xanh (box_wipe), vd "Bất Động Sản"; None = không có
PAIN = []  # EDIT: cụm nỗi đau (key_hit), vd ["bãi đất trống"]; trống = lấy từ work/pain.json
# ---------------------------------------------------------------- hết phần sửa

# Hằng số chung (hồ sơ chưa có khoá riêng; xem COMMON v3.6.3)
POLAROID_POS = [540, 1150]       # profile key: graphics.polaroid_pos
POLAROID_FRAME_OFFSET = 2.4      # profile key: graphics.polaroid_frame_offset (s trong clip nguồn)
ARROW_P0, ARROW_P1 = (230, 1450), (820, 1050)  # profile key: graphics.arrow_path
QUOTE_DY = 400                   # profile key: graphics.quote_dy (dời khối trích dẫn về vùng giữa khung)
QUOTE_HERO_COLOR = "#FFD84D"     # profile key: graphics.quote_hero_color
CTA_BOX_PAD = (80, 50)           # profile key: graphics.cta_box_pad (ngang, dọc)
SPAN_START, LOOK_SPAN_STEP, LOOK_SPAN_MAX = 1.0, 0.1, 1.6   # profile key: text.span_ratio_range
HERO_MIN, HERO_STEP = 120, 8     # profile key: text.size_hero_min / text.size_hero_step

W = Path(__file__).resolve().parent            # <phiên bản>/work
GFX = W.parent / "gfx"
V1_PREFIX, V3_PREFIX, A1_PREFIX, MUSIC_PREFIX = "V1", "V3", "A1", "Nhạc nền"


def norm(s: str) -> str:
    return re.sub(r"[^\w]", "", unicodedata.normalize("NFC", s).lower())


def scene_no(clip: dict) -> int:
    m = re.match(r"\d+", Path(clip["src"]).name)
    if not m:
        sys.exit(f"Tên file V1 không bắt đầu bằng số cảnh: {clip['src']}")
    return int(m.group())


def is_broll(clip: dict) -> bool:
    return "b-roll" in clip["src"]


def load_inputs() -> SimpleNamespace:
    """Nạp bản nền + lời + hồ sơ; cắt cứng V1 (P) và dời điểm cắt về trước chữ đầu (C7)."""
    prof_file = W / "profile.json"
    prof = sp.load(prof_file) if prof_file.is_file() else None
    if not sp.active(prof, "minimal-edu"):
        sys.exit(f'{prof_file} phải là {{"profile": "minimal-edu"}} (hồ sơ minimal-edu) — mẫu này chỉ dành cho hồ sơ đó.')
    bases = sorted(W.glob("*.base.craft.json"))
    if len(bases) != 1:
        sys.exit(f"Cần đúng 1 file {W}/<mã>.base.craft.json (build_spec_q.py ra <mã>.craft.json → đổi tên .base); thấy {len(bases)}.")
    base = json.loads(bases[0].read_text(encoding="utf-8"))
    code = bases[0].name.split(".")[0]
    words = json.loads((W / "words_tl.json").read_text(encoding="utf-8"))
    tracks = base["tracks"]

    def track(prefix):
        return next((t for t in tracks if t["name"].startswith(prefix)), None)
    v1_track, a1, music = track(V1_PREFIX), track(A1_PREFIX), track(MUSIC_PREFIX)
    if not (v1_track and a1 and music):
        sys.exit(f"Bản nền thiếu track {V1_PREFIX} / {A1_PREFIX} / {MUSIC_PREFIX}: có {[t['name'] for t in tracks]}")
    v1 = [{k: v for k, v in c.items() if k not in ("transition_in", "transition_out")} for c in v1_track["clips"]]
    fps = base["fps"]
    v1, moved = retime_cuts(v1, words, fps)
    print("dời điểm cắt (s, ms):", moved)
    sc = {}                                                  # số cảnh → (đầu, cuối) trên timeline
    for c in v1:
        a, b = sc.get(scene_no(c), (c["at"], c["at"] + c["dur"]))
        sc[scene_no(c)] = (min(a, c["at"]), max(b, c["at"] + c["dur"]))
    GFX.mkdir(exist_ok=True)
    return SimpleNamespace(code=code, base=base, words=words, fps=fps, end=base["duration"], prof=prof, v1=v1, sc=sc,
                           cuts=sorted({round(c["at"], 3) for c in v1 if c["at"] > 0}), v3=track(V3_PREFIX), a1=a1, music=music,
                           fx=MotionFX(gfx_dir=GFX, fps=fps, name=f"{code}-minimal"), cues_pain=[], spans=[])


def wt(X, word: str, after: float) -> float:
    """Giây bắt đầu của `word` đầu tiên sau mốc `after` (theo lời trên timeline)."""
    hit = next((w[1] for w in X.words if w[1] >= after - 1e-3 and norm(w[0]) == norm(word)), None)
    if hit is None:
        sys.exit(f"Không thấy từ «{word}» trong lời sau {after:.2f}s (words_tl.json)")
    return hit


def phrase_t(X, phrase: str) -> float:
    """Giây bắt đầu của cụm `phrase` (các từ liền nhau trong lời)."""
    toks = [norm(t) for t in phrase.split()]
    ws = [norm(w[0]) for w in X.words]
    for i in range(len(ws) - len(toks) + 1):
        if ws[i:i + len(toks)] == toks:
            return X.words[i][1]
    sys.exit(f"Không thấy cụm «{phrase}» trong lời (PAIN)")


def scene_span(X, n: int) -> tuple[float, float]:
    if n not in X.sc:
        sys.exit(f"SCENE_GFX: không có cảnh {n} trong V1 (có {sorted(X.sc)})")
    return X.sc[n]


def gfx_spans(X) -> None:
    """Khoảng chữ phải ở vùng trên (hình ở giữa–dưới): polaroid (nền giấy sáng → chữ đen) và đồ thị."""
    for g in SCENE_GFX:
        if g[0] == "polaroid":
            a = scene_span(X, g[1])[0]
            X.spans.append((a, a + g[2], True))
        elif g[0] == "graph":
            a, b = scene_span(X, g[2])
            X.spans.append((round(wt(X, g[1], a) - 0.03, 3), b, False))


def parse_groups(X) -> list:
    """Khớp tuần tự từng cụm với lời → [(items, giây từng từ)]. None = nhảy tới hết cảnh đang tới."""
    ptr, parsed = 0, []
    for g in GROUPS:
        if g is None:
            t0 = X.words[ptr][1]
            end = next((b for a, b in X.sc.values() if a - 0.05 <= t0 < b), None)
            if end is None:
                sys.exit(f"GROUPS: None ở lời «{X.words[ptr][0]}» ({t0:.2f}s) không rơi vào cảnh nào")
            ptr = next(i for i, w in enumerate(X.words) if w[1] >= end - 0.05)
            continue
        items = [s.strip() for s in g.split("|")]
        times = []
        for it in items:
            first = norm(it.lstrip("*~").split()[0])
            while ptr < len(X.words) and norm(X.words[ptr][0]) != first:
                ptr += 1
            if ptr >= len(X.words):
                sys.exit(f"GROUPS: «{g}» không khớp lời (hết lời ở «{it}»)")
            times.append(X.words[ptr][1])
            ptr += len(it.lstrip("*~").split())
        if sum(s[0] in "*~" for s in items) != 1:
            sys.exit(f"GROUPS: «{g}» cần đúng 1 từ lớn (* hoặc ~)")
        parsed.append((items, times))
    return parsed


def pain_list() -> list[str]:
    pain_file = W / "pain.json"
    return PAIN or (json.loads(pain_file.read_text(encoding="utf-8")).get("pain", []) if pain_file.is_file() else [])


def emphasis_at(X, cut: float, win: float = 0.5) -> bool:
    """Điểm cắt rơi ngay trước cụm nỗi đau / từ khoá → nhóm máy quay (punch / whip / spin) trong plan_cuts_min."""
    firsts = {norm(p.split()[0]) for p in pain_list() if p.split()}
    return any(cut - 0.05 <= w[1] <= cut + win and norm(w[0]) in firsts for w in X.words)


def group_fit(X, hero, before, after, times, shrunk, **k):
    """Thu từ lớn / nới chữ nhỏ cho tới khi cụm vừa vùng chữ (caption_group báo ValueError)."""
    pr = copy.deepcopy(X.prof)
    while True:
        try:
            return BT.caption_group(hero, before, after, times, prof=pr, colors=X.colors, looks="auto", gfx_dir=GFX,
                                    entrances=X.entr, **k)
        except ValueError as e:
            if "rộng hơn từ lớn" in str(e) and k.get("span_ratio", SPAN_START) < LOOK_SPAN_MAX:
                k["span_ratio"] = round(k.get("span_ratio", SPAN_START) + LOOK_SPAN_STEP, 2)
                shrunk.append((hero, "span", k["span_ratio"]))
                continue
            if "không vừa vùng" not in str(e) or pr["text"]["size_hero"] <= HERO_MIN:
                sys.exit(f"cụm «{' '.join(before)} *{hero} {' '.join(after)}»: {e}")
            pr["text"]["size_hero"] -= HERO_STEP
            shrunk.append((hero, pr["text"]["size_hero"]))


def captions(X, parsed) -> tuple[list, list]:
    """Chữ cụm: vùng an toàn luân phiên (pick_zone), vùng trên khi đồ thị / polaroid, từ đầu mỗi cảnh = key (gradient)."""
    X.colors = BT.HeroColors(X.prof)
    X.entr = EntranceStyles(X.prof, X.code)          # 6–10 kiểu vào mỗi video, không trùng cụm liền kề
    heroes_at, shrunk, prev_zone, seen = [], [], None, set()
    for k, (items, t) in enumerate(parsed):
        start = t[0]
        nxt = parsed[k + 1][1][0] if k + 1 < len(parsed) else X.end
        end = min(nxt, next((c for c in X.cuts if c > t[-1] + 0.05), X.end))
        h = next(i for i, s in enumerate(items) if s[0] in "*~")
        words = [s.lstrip("*~").rstrip(".,") for s in items]
        c = next(c for c in X.v1 if c["at"] - 1e-3 <= start + 0.01 < c["at"] + c["dur"] - 1e-3)
        sp_hit = next((s for s in X.spans if s[0] <= start < s[1]), None)
        if sp_hit:
            zone = "top"
        else:
            zone = BT.pick_zone(k, not is_broll(c), None if is_broll(c) else HEAD_TOP, prev_zone=prev_zone)
        prev_zone = zone
        sc_n = scene_no(c)
        is_key = sc_n not in seen
        seen.add(sc_n)
        on_paper = bool(sp_hit and sp_hit[2])
        cta = bool(CTA_WORD) and words[h] == CTA_WORD                    # chữ trắng trên hộp xanh
        light = on_paper or (not is_broll(c) and not cta)                 # A-roll: vùng chữ dưới trên áo sáng → chữ đậm màu
        extra = {"color": "#FFFFFF", "look": "shadow_deep"} if cta else {}
        X.fx.items += group_fit(X, words[h], words[:h], words[h + 1:], t, shrunk, end=end, fps=X.fps,
                                style="serif" if items[h][0] == "~" else "sans", on_dark=not light, accent=on_paper,
                                zone=zone, key=is_key and not cta, **extra)
        heroes_at.append(t[h])
    return heroes_at, shrunk


def gfx_polaroid(X, n: int, secs: float) -> None:
    a = scene_span(X, n)[0]
    clip = next(c for c in X.v1 if scene_no(c) == n and abs(c["at"] - a) < 0.2)
    frame = GFX / f"s{n}_frame.jpg"
    off = min(POLAROID_FRAME_OFFSET, max(clip["dur"] - 0.1, 0.0))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(clip["in"] + off), "-i", clip["src"], "-frames:v", "1", str(frame)], check=True)
    X.fx.image(G.paper_bg(GFX, f"paper_s{n}", "white", 3), a, secs, lane="gfx_under", name="Nền giấy polaroid")
    pol = X.fx.image(G.polaroid(GFX, f"polaroid_s{n}", str(frame)), a, secs, lane="card", name="Polaroid")
    pol.setdefault("motion", {}).update({"scale": 100, "position": POLAROID_POS})
    X.fx.polaroid_pop(pol)


def gfx_arrow(X, word: str, n: int) -> None:
    a, b = scene_span(X, n)
    t_draw = wt(X, word, a)
    arr = DP.arrow_curve(p0=ARROW_P0, p1=ARROW_P1)
    mov = DP.write(arr, GFX / f"arrow_s{n}.mov", X.fps)
    clip = X.fx.image(str(mov), t_draw, arr["frames"] / X.fps, lane="gfx_over", name="Mũi tên (vẽ)")
    clip.update({"in": 0.0, "audio": False})
    t_hold = X.fx.snap(t_draw + arr["frames"] / X.fps)
    X.fx.image(str(DP.still(arr, GFX / f"arrow_s{n}.png")), t_hold, b - t_hold, lane="gfx_over", name="Mũi tên")
    X.fx.cues.append({"t": t_draw, "kind": "pen", "why": f"vẽ «{word}»"})


def gfx_graph(X, word: str, n: int, steps: list) -> None:
    a, b = scene_span(X, n)
    start = round(wt(X, word, a) - 0.03, 3)
    X.fx.graph_scene([wt(X, w, start) for w in steps], at=start, dur=b - start)


def gfx_quote(X, n: int, lines: list, hero_index: int) -> None:
    a, b = scene_span(X, n)
    X.fx.image(G.quote_card(GFX, f"quote_s{n}"), a, b - a, lane="gfx_under", name="Quote card")
    t0, t_hero = wt(X, lines[0].split()[0], a - 0.1), wt(X, lines[hero_index].split()[0], a)
    qt = BT.quote_text(lines, False, at=t0, dur=b - t0, fps=X.fps, last_at=t_hero, hero_index=hero_index,
                       hero_color=QUOTE_HERO_COLOR, look="gradient", gfx_dir=GFX)
    for _, qc in qt:                                   # cảnh toàn chữ không có mặt: khối trích dẫn về giữa khung (vùng MID)
        if "src" in qc:                                # PNG gradient toàn khung: dời bằng motion.position
            m = qc.setdefault("motion", {})
            x, y = m.get("position", [540, 960])
            m["position"] = [x, y + QUOTE_DY]
        else:
            qc["position"] = [qc["position"][0], qc["position"][1] + QUOTE_DY]
    X.fx.items += qt
    X.fx.cues.append({"t": t_hero, "kind": "key_hit", "why": f"câu chốt «{lines[hero_index]}»"})


def gfx_cta(X) -> None:
    """Hộp tô xanh lộ dần sau từ lớn CTA."""
    hero = next((c[1] for c in X.fx.items if c[1].get("text") == CTA_WORD), None)
    if hero is None:
        sys.exit(f"CTA_WORD «{CTA_WORD}» không là từ lớn của cụm nào trong GROUPS")
    M = BT.Meter(X.prof)
    bw = round(M.width("hero_sans", hero["size"], hero["text"]) + CTA_BOX_PAD[0])
    top, bot = M.ink_top("hero_sans", hero["size"], [hero["text"]]), M.ink_bottom("hero_sans", hero["size"], [hero["text"]])
    box = X.fx.image(G.box_fill(GFX, "box_cta", min(bw, 1000), round(top + bot + CTA_BOX_PAD[1])), hero["at"] - 0.1,
                     hero["dur"] + 0.1, lane="card", name="Hộp tô CTA")
    box.setdefault("motion", {})["position"] = [540, round(hero["position"][1] - top / 2 + bot / 2)]
    X.fx.box_wipe(box)


def graphics(X) -> None:
    for i, c in enumerate(X.v1):                       # B-roll: giấy + tối rìa + mờ rìa
        if is_broll(c):
            X.fx.broll_paper(c, seed=i)
    kinds = {"polaroid": gfx_polaroid, "arrow": gfx_arrow, "graph": gfx_graph, "quote": gfx_quote}
    for g in SCENE_GFX:
        if g[0] not in kinds:
            sys.exit(f"SCENE_GFX: kiểu lạ «{g[0]}» (có {sorted(kinds)})")
        kinds[g[0]](X, *g[1:])
    if CTA_WORD:
        gfx_cta(X)


def joins(X) -> list:
    """Chuyển cảnh talking-head: plan_cuts_min chọn kiểu theo ngữ cảnh, MotionFX.th_join dựng."""
    quote_at = [X.sc[g[1]][0] for g in SCENE_GFX if g[0] == "quote"]

    def say(t, before):
        return " ".join(w[0] for w in X.words if (t - 2.5 <= w[1] < t if before else t <= w[1] < t + 2.5))
    cut_objs = []
    for prev, nxt in zip(X.v1, X.v1[1:]):
        cut_objs.append(Cut(nxt["at"], (prev["src"], round(prev["in"] + prev["dur"] - 1 / X.fps, 3)), (nxt["src"], round(nxt["in"], 3)),
                            b_kind="broll" if is_broll(nxt) else "aroll", a_kind="broll" if is_broll(prev) else "aroll",
                            before=say(nxt["at"], True), after=say(nxt["at"], False), section=scene_no(prev) != scene_no(nxt),
                            emphasis=emphasis_at(X, nxt["at"])))
    out = []
    for c, prev, nxt in zip(plan_cuts_min(cut_objs, seed=8, rules=X.prof), X.v1, X.v1[1:]):
        k = c.info["join"]
        if any(abs(nxt["at"] - q) < 0.05 for q in quote_at):
            k = "dip_to_paper"                         # cảnh quote che nền: thẻ vào bằng mờ về giấy (không lộ B-roll)
        elif k == "chapter_card_slam":                 # kịch bản không có tiêu đề chương → thẻ trống: đổi kiểu
            k = "blur_dissolve_cut"
        if k == "hard_cut":
            TH.mark(nxt, "hard_cut")
        else:
            try:
                X.fx.th_join(nxt, k, before=prev)
            except ValueError:                         # clip đã có keyframe scale riêng → kiểu thay
                k = "punch_settle" if k != "punch_settle" else "soft_wipe"
                X.fx.th_join(nxt, k, before=prev)
        out.append((round(c.t, 2), k, c.info["kind"]))
    return out


def sfx_plan(X, heroes_at: list) -> list:
    for t in heroes_at[::3]:
        X.fx.cues.append({"t": round(t - 0.02, 3), "kind": "word_click", "why": "từ lớn"})
    pain = pain_list()
    for p in pain:
        X.fx.cues.append({"t": round(phrase_t(X, p) - 0.03, 3), "kind": "key_hit", "why": f"nhấn nỗi đau «{p}»"})
    sfx = plan_sfx(X.fx.cues, [tuple(w) for w in X.words], X.end, name=f"{X.code}-minimal")
    for c in sfx:
        if "mở đầu" in c.get("name", "").lower():
            c["tier"] = "C"
            if c["at"] <= 0.04 and c["dur"] >= 0.32:
                c["dur"] = 0.32
    return sfx


def main() -> int:
    X = load_inputs()
    if not GROUPS:
        sys.exit("GROUPS trống: điền cụm chữ ở khối # EDIT (xem ví dụ KB08 ở đầu file)")
    gfx_spans(X)
    heroes_at, shrunk = captions(X, parse_groups(X))
    graphics(X)
    print("chuyển cảnh:", joins(X))
    sfx = sfx_plan(X, heroes_at)
    print("ensure_motion:", ensure_motion(X.fx.items, X.fps, profile=X.prof, cuts=X.cuts))
    X.fx._motion_done = True
    spec = {"name": f"{X.code} · minimal-edu", "width": 1080, "height": 1920, "fps": X.fps, "duration": X.end,
            "markers": X.base["markers"],
            "tracks": [{"type": "video", "name": "V1 Chuỗi A-Roll & B-Roll (cắt cứng)", "clips": X.v1},
                       *([X.v3] if X.v3 else []), *X.fx.tracks(), X.a1,
                       *[{"type": "audio", "name": f"A{i + 2} SFX" + (" (mở đầu)" if i == 0 else ""), "clips": tr}
                         for i, tr in enumerate(pack(sfx, 6))], X.music]}
    out = W / f"{X.code}.craft.json"
    out.write_text(json.dumps(clamp_keys(spec), ensure_ascii=False, indent=1), encoding="utf-8")
    print("thu nhỏ từ lớn:", shrunk)
    print("wrote", out, len(spec["tracks"]), "tracks,", len(X.fx.items), "FX,", len(sfx), "SFX")
    return 0


if __name__ == "__main__":
    sys.exit(main())
