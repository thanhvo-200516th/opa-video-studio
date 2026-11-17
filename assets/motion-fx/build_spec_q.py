#!/usr/bin/env python3
"""MẪU dựng spec cho skill opa-video-studio (SKILL §3 bước 7–8). Chép vào <thư mục video>/<phiên bản>/work/, CHỈ sửa các dòng
`# EDIT:` (KEY_SPECS, MUSIC, EXTRA_PAIN), rồi chạy:  OPA_SKILL_DIR=<thư mục skill> $PY work/build_spec_q.py

Đọc : <phiên bản>/media/speed_plan.json (do `speed_media.py plan` ghi) · 00_storyboard_manifest.json (thư mục đánh số, chỉ đọc) ·
      sổ rotation.json nếu có (key_seed, opening_pair, cut_seed; tìm ở <phiên bản>/ trước — `rotation.py plan <thư mục video> <MÃ> --out <phiên bản>`) ·
      media đã tăng tốc ở media/<speed_dir>/ (1.0x → thư mục đánh số) · media/person_alpha*.mov nếu có (matte, xem HEAD_TOP).
      work/plan_export.json (plan_doc.py export) — CHỈ khi KEY_SPECS trống: sinh KEY_SPECS từ đó; KEY_SPECS trống và không có file → chỉ ghi words_tl.json rồi thoát.
Ghi : work/<mã>.craft.json · work/words_tl.json · work/transition_plan.md (cột C3) · work/pain.json (nỗi đau đã dùng; edit_rules audit tự đọc)
      (không whisper, không dựng, không lint — việc của các bước sau).
MÃ = `script_id` trong manifest (in ra khi chạy).

KEY_SPECS — cách chọn (chữ chính, B8/B10/C5):
  · Số khối ≈ 1 mỗi 5–6 s video (52 s → 9–10 khối); khối đầu (chỉ số 0) là HOOK trong ~2 s đầu; mỗi cảnh ≥ 1 khối nếu cảnh dài > 5 s.
  · Chữ chính = 1–3 từ LẤY TỪ LỜI (B10: đúng chữ kịch bản); cụm trong lời (cột 5) là mốc giờ — nên là từ nhấn / nỗi đau.
  · Từ dẫn (cột 2) 1–3 từ ngay trước cụm; None nếu lời không có chỗ dẫn.
  · Màu (cột 6) xoay gold → red → cyan → mint, không 2 khối liền nhau cùng màu; red dành cho nỗi đau.
  · Chữ viết tay (cột 4) mặc định None; chỉ viết khi có chữ thứ hai ngắn (≤ 2 từ) bổ nghĩa, tối đa 1 khối mỗi 3 khối.
  · HOOK sau đầu: chữ ngắn (≤ ~12 ký tự là gọn; dài hơn mẫu tự tách 2 dòng / thu cỡ / đặt trước đầu, xem dòng «Chữ hook» khi chạy).

Luật: D4 tốc độ theo plan · D14 giọng từng cảnh dưới hình cảnh đó · B10 chữ phụ đề lấy từ kịch bản (Whisper chỉ căn giờ) ·
      B15 không dải tối dưới chữ phụ · F3 mức âm do `audio_levels.py plan` đặt sau (đọc work/<mã>.craft.json → <mã>.levels.craft.json).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unicodedata
import zlib
from pathlib import Path

SKILL = Path(os.environ.get("OPA_SKILL_DIR") or Path(__file__).resolve().parents[2])
if not (SKILL / "scripts/build_kit.py").is_file():
    sys.exit(f"Không thấy skill ở {SKILL}: đặt OPA_SKILL_DIR=<thư mục skill opa-video-studio>")
sys.path.insert(0, str(SKILL / "scripts"))
from build_kit import at_speed, clamp_keys, pack, script_words, tidy_words  # noqa: E402
from cut_plan import Cut, plan_cuts_best, plan_table  # noqa: E402
from edit_rules import find_pain_in_words, zoom_keys  # noqa: E402
from motion_fx import TNEDIT_DIR, MotionFX  # noqa: E402
from rotation import entry as rotation_entry  # noqa: E402
from text_fx import HEAD_HALF_W as _HALF_W, HEAD_TOP as _HEAD_TOP  # noqa: E402
from sfx_auto import duck, plan_sfx  # noqa: E402
from voice_level import level_segments  # noqa: E402

# ---------------------------------------------------------------- CHỈ SỬA CÁC DÒNG / KHỐI `# EDIT:`
MUSIC = TNEDIT_DIR / "08_Nhac_Nen/BGM_Thu_Vien_PR/BGM_Cinematic_Story_Vastness_184.mp3"  # EDIT: nhạc nền
HEAD_TOP = _HEAD_TOP  # EDIT: đỉnh đầu người nói (px, khung 1080x1920) để xếp chữ HOOK: HeyGen ~ 380 (mặc định), quay thật Rule 5 ~ 640; đo bằng frame_person.py analyze
HEAD_HALF_W = _HALF_W  # EDIT: nửa bề rộng đầu (px), mặc định 215
EXTRA_PAIN = []  # EDIT: cụm nỗi đau riêng của kịch bản (ngoài từ điển + keywords / pain_keywords của manifest), vd ["gãy gánh"]
KEY_SPECS = [  # EDIT: (chỉ số cảnh từ 0, từ dẫn, CHỮ CHÍNH, chữ viết tay hoặc None, cụm trong lời, bảng màu gold|red|cyan|mint)
    # (0, "Mỗi lần bắt đầu", "CÔNG VIỆC KINH DOANH", None, "công việc kinh doanh", "gold"),
]
# ---------------------------------------------------------------- hết phần sửa

W = Path(__file__).resolve().parent            # <phiên bản>/work
OUT = W.parent
SRC = OUT.parent                                # thư mục đánh số (chỉ ĐỌC)
FPS, KEY_Y, CAP_Y = 30, 500, 1440
BASE, PUSH, PUNCH, FACE = 100.0, 110.0, 118.0, [540, 960]

MANIFEST = json.loads((SRC / "00_storyboard_manifest.json").read_text(encoding="utf-8"))
_BROLL_SOURCES_PATH = SRC / "_broll_sources.json"
BROLL_SOURCES = json.loads(_BROLL_SOURCES_PATH.read_text(encoding="utf-8")) if _BROLL_SOURCES_PATH.is_file() else {}
PLAN = json.loads((OUT / "media/speed_plan.json").read_text(encoding="utf-8"))
SPEED = PLAN["speed"]
MEDIA = OUT / "media" / PLAN["speed_dir"] if SPEED != 1.0 else SRC
CODE, NAME = MANIFEST["script_id"], MANIFEST.get("slug", MANIFEST["script_id"])
ROT = rotation_entry(SRC, CODE, out=OUT) or {}
SHADE_TOP = TNEDIT_DIR / "07_Assets/Gradient_Vignette_9x16/top_shade_dark_text_zone_1080x1920.png"
MATTE_RE = re.compile(r"^person_alpha(?:_s(\d+(?:\.\d+)?))?\.mov$")


def find_matte() -> tuple[Path | None, float]:
    """person_alpha.mov (tách cả file) hoặc person_alpha_s<S>.mov (tách từ giây S của media đã tăng tốc: `matte.py --start S`)."""
    for p in sorted((OUT / "media").glob("person_alpha*.mov")):
        m = MATTE_RE.match(p.name)
        if m:
            return p, float(m.group(1) or 0.0)
    return None, 0.0


MATTE, MATTE_S = find_matte()                    # có file phủ đủ đoạn hook → chữ hook đặt SAU đầu người (bước 5)


def norm(s: str) -> str:
    return re.sub(r"[^\w\s]", "", unicodedata.normalize("NFC", s).lower()).strip()


def snap(t: float) -> float:
    return round(t * FPS) / FPS


def probe_dur(path: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                                capture_output=True, text=True, check=True).stdout.strip())


def hook_matte_plan(v1: list[dict], t0: float, dur: float) -> tuple[Path | None, float, float]:
    """(nguồn, giây bắt đầu, độ dài) trong media ĐÃ tăng tốc mà matte phải phủ cho khối hook [t0, t0+dur), đệm 0,5 s hai đầu.
    `in` của clip matte = `in` clip V1 − start (behind_person(matte_offset=start))."""
    over = [v for v in v1 if v["at"] < t0 + dur - 1e-6 and v["at"] + v["dur"] > t0 + 1e-6]
    if not over:
        return None, 0.0, 0.0
    src = over[0]["src"]
    same = [v for v in over if v["src"] == src]
    lo = min(v["in"] + max(0.0, t0 - v["at"]) for v in same)
    hi = max(v["in"] + min(t0 + dur, v["at"] + v["dur"]) - v["at"] for v in same)
    start = max(0.0, lo - 0.5)
    return Path(src), round(start, 2), round(min(hi + 0.5, probe_dur(Path(src))) - start, 2)


def print_matte_cmd(why: str, src: Path, start: float, length: float) -> None:
    out = OUT / "media" / f"person_alpha_s{start:.2f}.mov"
    print(f"[matte] {why}. Tách người (chạy một lần, rồi chạy lại build_spec.py; thiếu thì hook đặt TRƯỚC đầu):\n"
          f"  {sys.executable} {SKILL}/scripts/matte.py --input {src} --output {out} --start {start:.2f} --dur {length:.2f}\n"
          f"  --start / --dur tính bằng GIÂY của media đã tăng tốc ({src.parent.name}), đã đệm 0,5 s; clip matte bắt đầu ở giây {start:.2f} "
          f"của file gốc nên `in` = in V1 − {start:.2f} (build_spec đọc số này từ tên file _s{start:.2f}).")


def broll_source_of(seg: dict, video_name: str) -> str:
    """Xác định nguồn B-roll (flow | real_footage | stock | muse | unknown) từ _broll_sources.json / manifest / _google_raw."""
    valid = {"flow", "real_footage", "stock", "muse"}
    vname = Path(video_name).name
    entry = BROLL_SOURCES.get(vname) or BROLL_SOURCES.get(video_name) or {}
    if isinstance(entry, dict) and str(entry.get("source") or "").lower() in valid:
        return str(entry["source"]).lower()
    seg_src = str(seg.get("broll_source") or "").strip().lower()
    if seg_src in valid:
        return seg_src
    google_raw = SRC / "_google_raw"
    if google_raw.is_dir():
        stem = Path(vname).stem
        if any(p.is_file() and (p.stem == stem or p.stem.startswith(stem + "_")) for p in google_raw.iterdir()):
            return "flow"
    vg = str((seg.get("api_routing") or {}).get("video_generator") or "").strip().lower()
    vg_map = {
        "flow": "flow", "google_flow": "flow", "google-flow": "flow", "omni-flash": "flow",
        "real_footage": "real_footage", "live_shoot": "real_footage",
        "stock": "stock",
        "muse": "muse", "muse_api": "muse",
    }
    return vg_map.get(vg, "unknown")


def specs_from_plan_export(words_tl: list, raw: list[dict]) -> list[tuple]:
    """KEY_SPECS trống + có work/plan_export.json (plan_doc.py export) → hàng KEY_SPECS cùng định dạng; in ra để chép vào khối `# EDIT:`."""
    f = W / "plan_export.json"
    if not f.is_file():
        return []
    from plan_doc import key_specs_from_export
    scene_at = lambda t: next((r["scene"] for r in reversed(raw) if r["t0"] <= t + 1e-3), 0)   # noqa: E731
    rows, unsupported = key_specs_from_export(json.loads(f.read_text(encoding="utf-8")), words_tl, scene_at)
    print(f"KEY_SPECS trống → lấy {len(rows)} khối từ {f.name} (chép vào khối `# EDIT:` nếu muốn sửa tay):")
    print("\n".join(f"    {r!r}," for r in rows))
    for u in unsupported:
        print(f"[chưa hỗ trợ] {u} — không có chữ chính; xử lý ở khâu B-roll / đồ hoạ")
    return rows


def main() -> int:
    print(f"Mã video (script_id trong manifest): {CODE}")
    print(f"Sổ luân phiên: SFX mở đầu #{ROT['opening_pair']} · key_seed {ROT['key_seed']}" if ROT else
          f"Chưa có sổ luân phiên cho {CODE} → SFX mở đầu / kiểu chữ theo crc32 mặc định. Cấp sổ (ghi vào {OUT}, không ghi vào {SRC}):\n"
          f"  {sys.executable} {SKILL}/scripts/rotation.py plan {SRC} {CODE} --out {OUT}")
    by_prefix = {s["seq_prefix"]: s for s in MANIFEST["segments"]}
    scenes = [{**sc, "seg": by_prefix[sc["seq_prefix"]], "segs": at_speed(sc["segs"], SPEED, FPS), "words": at_speed(sc["words"], SPEED, FPS),
               "toks": by_prefix[sc["seq_prefix"]]["display_text"].split()} for sc in PLAN["scenes"]]
    print(f"D4: {SPEED}x · media {MEDIA} · giữ lại {PLAN['kept_src_seconds']:.2f} s (bản gốc)")

    # ---- 1. Đoạn V1 / A1 + mốc chữ theo kịch bản ----
    RAW: list[dict] = []
    words_tl: list[tuple[str, float, float]] = []
    t_acc = 0.0
    for si, sc in enumerate(scenes):
        t0s = []
        for k, (a, b) in enumerate(sc["segs"]):
            d = round(snap(b - a), 3)
            t0s.append(round(t_acc, 3))
            RAW.append({"scene": si, "video": MEDIA / sc["video"], "voice": MEDIA / (sc["voice"] or sc["video"]), "a": a, "d": d, "t0": t0s[-1],
                        "id": f"s{len(RAW):02d}", "role": sc["seg"]["role_id"], "broll": sc["seg"]["type"] == "b-roll",
                        "broll_source": broll_source_of(sc["seg"], sc["video"]) if sc["seg"]["type"] == "b-roll" else None})
            t_acc = round(t_acc + d, 3)
        words_tl += script_words(sc["toks"], sc["words"], sc["segs"], t0s, FPS)
    END = round(t_acc, 3)
    (W / "words_tl.json").write_text(json.dumps(words_tl, ensure_ascii=False, indent=1), encoding="utf-8")
    T0 = [r["t0"] for r in RAW]
    key_specs = KEY_SPECS or specs_from_plan_export(words_tl, RAW)
    if not key_specs:
        print(f"Đã ghi {W / 'words_tl.json'} ({len(words_tl)} từ). KEY_SPECS trống: điền các khối chữ chính (dòng `# EDIT:`), "
              f"hoặc `plan_doc.py build {W} --manifest {SRC / '00_storyboard_manifest.json'}` → duyệt plan → `plan_doc.py export` rồi chạy lại")
        return 0

    def find_word_time(phrase: str, scene: int) -> float:
        toks, n = norm(phrase).split(), len(norm(phrase).split())
        lo = min(r["t0"] for r in RAW if r["scene"] == scene)
        hi = max(r["t0"] + r["d"] for r in RAW if r["scene"] == scene)
        for i in range(len(words_tl) - n + 1):
            if lo - 1e-3 <= words_tl[i][1] < hi and [norm(words_tl[j][0]) for j in range(i, i + n)] == toks:
                return words_tl[i][1]
        raise SystemExit(f"KEY_SPECS: không thấy cụm «{phrase}» trong lời cảnh {scene}")

    # E1: nỗi đau = từ điển + keywords / pain_keywords của manifest + EXTRA_PAIN
    pain_extra = sorted({*EXTRA_PAIN, *(p for s in MANIFEST["segments"] for p in [*(s.get("keywords") or []), *(s.get("pain_keywords") or [])])})
    pain_hits = find_pain_in_words(words_tl, pain_extra)
    pain_times = [p["t"] for p in pain_hits]
    print(f"Nỗi đau: {[(p['phrase'], round(p['t'], 2)) for p in pain_hits]}")
    (W / "pain.json").write_text(json.dumps({"script_id": CODE, "pain": pain_extra, "extra_pain": list(EXTRA_PAIN),
                                             "hits": [{"phrase": p["phrase"], "t": round(p["t"], 3)} for p in pain_hits]},
                                            ensure_ascii=False, indent=1), encoding="utf-8")

    v1, jobs = [], []
    for r in RAW:
        local = [round(pt - r["t0"], 3) for pt in pain_times if r["t0"] <= pt <= r["t0"] + r["d"]]
        zk = zoom_keys(r["d"], pains=local, base=BASE, push=PUSH, punch=PUNCH, period=3.0, fps=FPS)
        clip = {"src": str(r["video"]), "at": r["t0"], "in": round(r["a"], 3), "dur": r["d"], "audio": False,
                "name": f"{'B-roll' if r['broll'] else 'A-roll'} {r['role'].split('-')[-1]} · {r['id']}",
                "motion": {"scale": zk, "anchor": FACE, "position": FACE}}
        if r["broll"]:
            clip["broll_source"] = r["broll_source"]
        v1.append(clip)
        jobs.append((str(r["voice"]), r["a"], r["d"], r["id"]))
    voice_dir = OUT / "media/voice"
    voice_dir.mkdir(parents=True, exist_ok=True)
    a1 = [{"src": str(w), "at": RAW[i]["t0"], "in": 0.0, "dur": RAW[i]["d"], "name": f"Giọng {i + 1:02d} ({RAW[i]['id']})", "gain_db": 0.0}
          for i, w in enumerate(level_segments(jobs, voice_dir))]

    # ---- 2. Bảng điểm cắt → chuyển cảnh (cut_seed của sổ luân phiên) ----
    def around(t: float, before: bool, n: int = 4) -> str:
        ws = [x for x, s, _ in words_tl if (s < t if before else s >= t)]
        return " ".join(ws[-n:] if before else ws[:n])

    cuts = [Cut(T0[i], (str(RAW[i - 1]["video"]), round(RAW[i - 1]["a"] + RAW[i - 1]["d"] - 1 / FPS, 3)), (str(RAW[i]["video"]), round(RAW[i]["a"], 3)),
                before=around(T0[i], True), after=around(T0[i], False), section=RAW[i]["scene"] != RAW[i - 1]["scene"])
            for i in range(1, len(RAW))]
    plan = plan_cuts_best(cuts, seed=ROT.get("cut_seed", zlib.crc32(("cut" + CODE).encode()) % 997))

    gfx = OUT / "media/gfx"
    gfx.mkdir(parents=True, exist_ok=True)
    fx = MotionFX(gfx_dir=gfx, fps=FPS, accent="#FFC414", key_y=KEY_Y, cap_y=CAP_Y, name=NAME, key_seed=ROT.get("key_seed"))
    used: dict[str, int] = {}
    for c in plan:
        i, j = T0.index(c.t), c.info["join"]
        if j == "zoom + punch":
            fx.join(v1[i], "zoom", cue_sfx=True)
        elif j in ("flicker", "shutter"):
            fx.join(v1[i], j, cue_sfx=True)
        else:
            fx.cut_fx(c.t, j, v1[i], variant=used.get(j, 0), clip_before=v1[i - 1])
        used[j] = used.get(j, 0) + 1

    # ---- 3. Chữ chính (chữ lấy từ kịch bản — B10) ----
    entries = [(lead, key, script, find_word_time(phrase, sc_i), pal) for sc_i, lead, key, script, phrase, pal in key_specs]
    matte_clips: list[dict] = []
    key_spans: list[tuple[float, float, str]] = []
    n3d = 0
    def end_at_cut(t0: float, dur: float) -> tuple[float, float]:
        """SKILL §11: chữ chính kết thúc đúng điểm cắt kế tiếp (FilmCraft đặt chuyển cảnh giữa điểm cắt), không lố sang cảnh sau.
        Còn < 0,8 s tới điểm cắt thì vào sớm hơn (không đè khối trước) để vẫn đủ 0,8 s đọc."""
        nc = min((c for c in T0 if c > t0 + 0.05), default=None)
        if nc is None or t0 + dur <= nc:
            return t0, dur
        if nc - t0 < 0.8:
            t0 = max(key_spans[-1][1] if key_spans else 0.0, round(nc - 0.8, 3), 0.0)
        return t0, round(nc - t0, 3)

    for n, (lead, key, script, kt, pal) in enumerate(entries):
        t0 = max(0.0, round(kt - 0.15, 3))
        nxt = round(entries[n + 1][3] - 0.20, 3) if n + 1 < len(entries) else END
        t0, dur = end_at_cut(t0, round(max(1.4, min(nxt - t0, 2.5)), 3))
        ent = None                                                   # kiểu vào theo bộ key_seed của video (C5: ≤ 4 khối 3D)
        if n == 0 or (n % 4 == 0 and n3d < 4):
            ent, n3d = ("flip3d" if n3d % 2 == 0 else "swing_in"), n3d + 1
        if n == 0:                                                   # HOOK: xếp để đọc trọn câu, sau đầu người (B9) khi che ≤ 20 %
            lay = fx.fit_hook(key, size=190, y=420, lead=bool(lead), head_top=HEAD_TOP, half_w=HEAD_HALF_W)
            print(f"Chữ hook «{key}»: {lay['note']}")
            use_matte = lay["matte"]
            if use_matte:
                src, start, length = hook_matte_plan(v1, t0, dur)
                if MATTE and src:
                    cov = MATTE_S + probe_dur(MATTE) - 0.1                     # hết matte thì hook cũng hết (không khung chưa tách)
                    need_hi = start + length - 0.5
                    if start + 0.5 < MATTE_S - 0.02:
                        print_matte_cmd(f"matte hiện có ({MATTE.name}) bắt đầu muộn hơn đoạn hook", src, start, length)
                        use_matte = False
                    elif need_hi > cov + 1e-6:
                        dur = round(dur - (need_hi - cov), 3)
                        if dur < 1.0:
                            print_matte_cmd(f"matte hiện có ({MATTE.name}) không phủ hết đoạn hook", src, start, length)
                            use_matte = False
                            t0, dur = end_at_cut(t0, round(max(1.4, min(nxt - t0, 2.5)), 3))
                elif src:
                    print_matte_cmd("chữ hook cần nằm SAU đầu người nhưng chưa có matte", src, start, length)
                    use_matte = False
            block = []
            for k, (text, size, y) in enumerate(lay["lines"]):
                n_cue = len(fx.cues)
                block += fx.keyword_tpl(lead if k == 0 else None, text, script if k == len(lay["lines"]) - 1 else None,
                                        at=t0, dur=dur, palette=pal, y=y, size=size, entrance=ent)
                del fx.cues[n_cue + 1 if k == 0 else n_cue:]                   # hook nhiều dòng: một cú key_hit cho cả khối
            if use_matte:                                            # Track Matte với lớp người tách nền (offset = giây bắt đầu của matte)
                matte_clips += fx.behind_person(block, v1, str(MATTE), matte_track="Video 2", matte_offset=MATTE_S)
        else:
            block = fx.keyword_tpl(lead, key, script, at=t0, dur=dur, palette=pal, entrance=ent)
        key_spans.append((t0, round(t0 + dur, 3), key))
        for c in block:
            if "text" in c and not any(e.get("effect") == "wonder_glow" for e in c.get("effects", [])):
                fx.key_glow(c, pal, soft=True)
    for p in pain_hits:   # E1: SFX nhấn, bỏ nếu đã có key_hit trong ±0,35 s (tránh hai SFX chồng đỉnh)
        if not any(q["kind"] == "key_hit" and abs(q["t"] - p["t"]) < 0.35 for q in fx.cues):
            fx.cues.append({"t": max(0.0, round(p["t"] - 0.03, 3)), "kind": "key_hit", "why": f"nhấn nỗi đau «{p['phrase']}»"})

    # ---- bảng điểm cắt cho người dùng duyệt (C3: Giây | Cảnh | Chữ chính | Chuyển cảnh | Zoom | Nỗi đau | SFX | Lý do) ----
    def cut_ctx(c: Cut) -> dict:
        i = T0.index(c.t)
        name = lambda k: v1[k]["name"].split(" · ")[0]                                              # noqa: E731
        keys = [k for a, b, k in key_spans if a <= c.t < b]
        zs = [kf[1] for kf in v1[i]["motion"]["scale"]]
        pains = sorted({p["phrase"] for p in pain_hits if c.t - 0.5 <= p["t"] <= c.t + 1.5})
        same = RAW[i]["scene"] == RAW[i - 1]["scene"]
        return {"scene": f"{RAW[i - 1]['scene'] + 1}{'' if same else ' → ' + str(RAW[i]['scene'] + 1)}: {name(i - 1)} → {name(i)}",
                "key": " / ".join(keys) or "—", "zoom": f"{round(zs[0])}% → {round(max(zs))}%", "pain": ", ".join(pains) or "—"}

    table = plan_table(plan, [cut_ctx(c) for c in plan])
    (W / "transition_plan.md").write_text(f"# {CODE} — Bảng điểm cắt → Chuyển cảnh\n\n" + table + "\n", encoding="utf-8")
    print(table)

    # ---- 4. Phụ đề 2 dòng (B5), không dải tối dưới (B15) ----
    rows, cur = [], []
    for tok, s, _ in tidy_words(words_tl):
        cur.append((tok, s))
        if tok.endswith((".", "?", "!")) or len(cur) >= 12:
            rows.append(cur)
            cur = []
    rows += [cur] if cur else []
    for i, r in enumerate(rows):
        fx.captions2(r, rows[i + 1][0][1] - 0.04 if i + 1 < len(rows) else END, y=CAP_Y)

    # ---- 5. SFX (F1, F2) + nhạc nền (mức do audio_levels.py plan đặt lại) ----
    sp = [q for q in fx.cues if q["kind"] == "sparkle"]
    fx.cues = [q for q in fx.cues if q["kind"] != "sparkle" or sp.index(q) % 2 == 0]
    sfx = plan_sfx(fx.cues, words_tl, END, name=NAME, opening_pair=ROT.get("opening_pair"))
    for c in sfx:
        if "mở đầu" in c.get("name", "").lower():
            c["tier"] = "C"                                          # cặp mở đầu chồng ở khung 0: mỗi tiếng −12 để tổng đỉnh vẫn ≤ −8 dBFS
            if c["at"] <= 0.04 and c["dur"] >= 0.32:
                c["dur"] = 0.32
    ebur = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(MUSIC), "-t", "60", "-af", "ebur128", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    g_bgm = round(-22.5 - float(re.findall(r"I:\s*(-?[\d.]+) LUFS", ebur)[-1]), 1)
    music = [{"src": str(MUSIC), "at": 0.0, "in": 0.0, "dur": END, "name": f"Nhạc nền {MUSIC.stem[:28]} (ducking ở điểm cắt)",
              "gain_db": duck(g_bgm, sorted({round(c.t, 2) for c in plan}), END)}]

    video_tracks = [{"type": "video", "name": "V1 Chuỗi A-Roll & B-Roll chính (Zoom động + Punch nỗi đau)", "clips": v1}]
    if matte_clips:
        video_tracks.append({"type": "video", "name": "V2 Người tách nền (che chữ Hook — Track Matte)", "clips": matte_clips})
    if SHADE_TOP.is_file():
        video_tracks.append({"type": "video", "name": "V3 Dải tối vùng chữ trên", "clips": [{"src": str(SHADE_TOP), "at": 0.0, "dur": END, "name": "Dải tối trên"}]})
    spec = {
        "name": f"{CODE} · bản nháp · opa-video-studio", "width": 1080, "height": 1920, "fps": FPS, "duration": END,
        "markers": [{"at": 0.0, "name": "SFX MỞ ĐẦU", "comment": "Whoosh + Hit mở đầu 0.32s tại khung 0 (F1)"}],
        "tracks": [*video_tracks, *fx.tracks(),
                   {"type": "audio", "name": "A1 Giọng chuẩn hoá", "clips": a1},
                   *[{"type": "audio", "name": f"A{i + 2} SFX" + (" (mở đầu)" if i == 0 else ""), "clips": tr} for i, tr in enumerate(pack(sfx, 6))],
                   {"type": "audio", "name": "Nhạc nền", "clips": music}],
    }
    spec = clamp_keys(spec)
    out_path = W / f"{CODE.lower()}.craft.json"
    out_path.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Đã xuất {out_path} · {END:.2f}s · {len(RAW)} đoạn V1 · {len(fx.items)} clip FX · {len(sfx)} SFX · {len(spec['tracks'])} tracks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
