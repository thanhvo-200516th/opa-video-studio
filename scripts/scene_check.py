#!/usr/bin/env python3
"""Kiểm 'hình đến đâu tiếng đến đó' (D14) và 'cảnh chèn bám kịch bản' (D9) giữa manifest và spec .craft.json.

    ~/.venvs/video-skills/bin/python scene_check.py --manifest 00_storyboard_manifest.json --spec work/kb.craft.json \
        [--transcripts transcripts/] [--words WORDS_TL.json] [--tol 0.12] [--tol-transition 0.5] [--review OUT.md] [--json OUT.json]

Kiểm (FAIL → mã thoát 1):
  av_sync — khi tiếng cảnh N đang đọc, hình trên màn hình phải là cảnh N (hình riêng, A-roll, hoặc cảnh chèn của cảnh đó);
            hình cảnh khác chiếm liên tục > --tol-transition = FAIL; tiếng b-roll lệch đầu hình > --tol = FAIL;
            thiếu clip hình / tiếng của cảnh trên timeline = FAIL.
  order   — các cảnh đang đọc xuất hiện đúng thứ tự seq_index.
  broll_h5 — broll_prompt rỗng / «Clip thư viện» = FAIL; chưa đạt lint H5 (tiếng Anh, 8–60 chữ, không chữ/logo) = WARN.
  script_source / broll_h5 trong --json có "scenes": [seq…] = cảnh cần làm lại (→ broll_fix.py).
  script  — b-roll thiếu broll_prompt / display_text; lời đọc trong transcript lệch tts_text (giống < 0,80) = FAIL.
--words: giọng gộp (media/voice/voice_sNN.wav) không khớp tên → khoảng đọc của cảnh suy ra bằng cách gióng tts_text lần lượt
        (theo seq_index, đơn điệu, chịu lệch ASR nhỏ) lên [[chữ, t0, t1], …] theo giờ timeline; không có --words → thiếu clip tiếng = FAIL.
Cảnh chèn (footage không thuộc cảnh nào trong manifest) được phép, chỉ liệt kê (WARN) để người xem đối chiếu lời (D9) qua --review.
Mỗi mục: {"id", "status": OK | FAIL | WARN, "value", "target", "fix"}.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

from broll_fix import core_of, lint_prompt

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm"}
STEP = 0.1                    # lấy mẫu hình ~10 fps
SIM_MIN = 0.80                # độ giống tối thiểu lời đọc vs tts_text
SKIP_RE = re.compile(r"(?<![a-z])(matte|alpha|overlay|mask|gfx|graphic|trans)(?![a-z])")
SPEED_RE = re.compile(r"_x\d{3}$")   # hậu tố tốc độ (x105 / x110 / x115 / x125) bỏ khi so khớp


def stem(path: str) -> str:
    """Tên gốc không thư mục tốc độ, không đuôi, không hậu tố _x115."""
    return SPEED_RE.sub("", Path(path).stem)


def _item(cid: str, status: str, value, target, fix: str = "", scenes: list[int] | None = None) -> dict:
    item = {"id": cid, "status": status, "value": value, "target": target, "fix": fix if status != "OK" else ""}
    if scenes is not None:
        item["scenes"] = scenes       # seq_index các cảnh sai (đưa vào broll_fix.py)
    return item


def _is_footage(track: dict, clip: dict) -> bool:
    src = clip.get("src") or ""
    if track.get("type") != "video" or Path(src).suffix.lower() not in VIDEO_EXT:
        return False
    hay = f"{track.get('name', '')} {clip.get('name', '')} {Path(src).name}".lower()
    return not SKIP_RE.search(hay)


def read_spec(spec: dict) -> tuple[list[dict], list[dict]]:
    """→ (clip hình thật [{ti, t0, t1, stem, src}], clip tiếng [{t0, t1, stem}])."""
    pics, voices = [], []
    for ti, tr in enumerate(spec.get("tracks", [])):
        for c in tr.get("clips", []):
            t0 = float(c.get("at", 0.0))
            t1 = t0 + float(c.get("dur", 0.0))
            if _is_footage(tr, c):
                pics.append({"ti": ti, "t0": t0, "t1": t1, "stem": stem(c["src"]), "src": c["src"]})
            elif tr.get("type") == "audio" and c.get("src"):
                voices.append({"t0": t0, "t1": t1, "stem": stem(c["src"])})
    return pics, voices


def _span(clips: list[dict]) -> tuple[float, float] | None:
    return (min(c["t0"] for c in clips), max(c["t1"] for c in clips)) if clips else None


def align_words(ref: list[str], words: list, pos: int) -> tuple[tuple[float, float], int] | None:
    """Gióng tts_text (ref) lên words[pos:] → ((t0, t1), vị trí kế). Chịu lệch nhỏ; None nếu khớp < 50 % chữ."""
    flat = [((_tokens(w[0]) or [""])[0], i) for i, w in enumerate(words)][pos:pos + int(len(ref) * 1.5) + 10]
    sm = difflib.SequenceMatcher(None, ref, [f[0] for f in flat], autojunk=False)
    blocks = [b for b in sm.get_matching_blocks() if b.size]
    anchors = [b for b in blocks if b.size >= 2] or blocks
    if not anchors or sum(b.size for b in blocks) < 0.5 * len(ref):
        return None
    first, last = flat[anchors[0].b][1], flat[anchors[-1].b + anchors[-1].size - 1][1]
    return (float(words[first][1]), float(words[last][2])), last + 1


def build_scenes(manifest: dict, pics: list[dict], voices: list[dict], words: list | None = None) -> list[dict]:
    """Mỗi cảnh: khoảng đang đọc + khoảng hình + danh sách thiếu (+ nguồn khoảng đọc)."""
    scenes, pos = [], 0
    for s in sorted(manifest.get("segments", []), key=lambda x: x["seq_index"]):
        files = s.get("files") or {}
        vstem = stem(files["video_file"]) if files.get("video_file") else None
        astem = stem(files["voice_file"]) if files.get("voice_file") else None
        mine_pic = [p for p in pics if vstem and p["stem"] == vstem]
        mine_voice = [v for v in voices if astem and v["stem"] == astem]
        pic_span, voice_span = _span(mine_pic), _span(mine_voice)
        missing = []
        if not pic_span:
            missing.append(f"clip hình {files.get('video_file')}")
        if s["type"] == "b-roll" and not voice_span:
            missing.append(f"clip tiếng {files.get('voice_file')}")
        speak, src = (voice_span, "clip tiếng") if s["type"] == "b-roll" else (pic_span, "clip hình")
        if words:                          # mọi cảnh đều tiêu thụ words để cảnh sau gióng đúng chỗ
            hit = align_words(_tokens(s.get("tts_text", "")), words, pos)
            pos = hit[1] if hit else pos
            if not voice_span:             # giọng gộp: khoảng đọc suy từ words
                if hit:
                    speak, src, voice_span = hit[0], "words", hit[0]
                    missing = [m for m in missing if not m.startswith("clip tiếng")]
                else:
                    missing.append("khoảng đọc trong words (không gióng được tts_text)")
        scenes.append({"seg": s, "seq": s["seq_index"], "vstem": vstem, "pic_span": pic_span, "speak_src": src,
                       "voice_span": voice_span, "speak": speak or pic_span, "missing": missing})
    return scenes


def visible_at(pics: list[dict], t: float) -> dict | None:
    live = [p for p in pics if p["t0"] <= t < p["t1"]]
    return max(live, key=lambda p: (p["ti"], p["t0"])) if live else None


def sample_scene(scene: dict, scenes: list[dict], pics: list[dict]) -> tuple[list[tuple], list[dict]]:
    """Lấy mẫu trong khoảng đang đọc → (đoạn lệch [(t0, t1, mô tả)], các lần hiện [{label, t0, t1, cut}])."""
    if not scene["speak"]:
        return [], []
    s0, s1 = scene["speak"]
    n = max(int(round((s1 - s0) / STEP)), 0)
    bad, shown = [], []
    for i in range(n):
        t = s0 + (i + 0.5) * STEP
        owners = {sc["vstem"] for sc in scenes if sc["speak"] and sc["speak"][0] <= t < sc["speak"][1]} | {scene["vstem"]}
        pic = visible_at(pics, t)
        known = {sc["vstem"] for sc in scenes}
        if pic is None:
            label, ok, cut = "(không có hình)", False, False
        elif pic["stem"] in known:
            label, ok, cut = pic["stem"], pic["stem"] in owners, False
        else:
            label, ok, cut = pic["stem"], True, True
        a, b = t - STEP / 2, t + STEP / 2
        if shown and shown[-1]["label"] == label:
            shown[-1]["t1"] = b
        else:
            shown.append({"label": label, "t0": a, "t1": b, "cut": cut, "ok": ok})
        if not ok:
            if bad and bad[-1][2] == label and abs(bad[-1][1] - a) < 1e-6:
                bad[-1] = (bad[-1][0], b, label)
            else:
                bad.append((a, b, label))
    return bad, shown


def _tokens(text: str) -> list[str]:
    t = unicodedata.normalize("NFC", text or "").lower().replace("_", " ")
    return re.sub(r"[^\w\s]", " ", t).split()


def find_transcript(tdir: Path, name: str) -> Path | None:
    cands = [tdir / f"{name}.json"] + [d / f"{name}.json" for d in sorted(tdir.glob("x*")) if d.is_dir()]
    return next((c for c in cands if c.is_file()), None)


def transcript_tokens(path: Path) -> list[str]:
    d = json.loads(path.read_text(encoding="utf-8"))
    words = [w.get("text", "") for w in d.get("words", []) if w.get("type", "word") == "word"]
    return _tokens(" ".join(words) if words else d.get("text", ""))


def check_av_sync(scenes: list[dict], pics: list[dict], tol: float, tol_tr: float) -> tuple[dict, dict, list]:
    problems, cutaways, shown_by_seq = [], [], {}
    for sc in scenes:
        seq = sc["seq"]
        problems += [f"cảnh {seq}: thiếu {m} trên timeline" for m in sc["missing"]]
        if sc["seg"]["type"] == "b-roll" and sc["voice_span"] and sc["pic_span"]:
            d = abs(sc["voice_span"][0] - sc["pic_span"][0])
            if d > tol:
                problems.append(f"cảnh {seq}: tiếng bắt đầu {sc['voice_span'][0]:.2f}s, hình {sc['pic_span'][0]:.2f}s (lệch {d:.2f}s > {tol}s)")
        bad, shown = sample_scene(sc, scenes, pics)
        shown_by_seq[seq] = shown
        for a, b, label in bad:
            if round(b - a, 3) > tol_tr + 1e-9:
                problems.append(f"cảnh {seq}: khi tiếng đọc, hình là «{label}» {a:.2f}–{b:.2f}s ({b - a:.2f}s > {tol_tr}s)")
        cutaways += [f"cảnh {seq}: {x['label']} {x['t0']:.2f}–{x['t1']:.2f}s" for x in shown if x["cut"]]
    av = _item("av_sync", "FAIL" if problems else "OK", "; ".join(problems) or "hình khớp tiếng ở mọi cảnh",
               f"tiếng≈hình ≤ {tol}s; hình cảnh khác ≤ {tol_tr}s",
               "đặt clip hình + tiếng của cảnh N cùng điểm bắt đầu; cảnh chèn phải nằm trong cảnh N và có lời riêng (D14)")
    cut = _item("cutaway", "WARN" if cutaways else "OK", "; ".join(cutaways) or "không có cảnh chèn", "cảnh chèn bám lời (D9)",
                "xem --review: hình chèn phải đúng điều lời kịch bản đang nói (D9)")
    return av, cut, shown_by_seq


def check_order(scenes: list[dict]) -> dict:
    spoken = sorted((sc for sc in scenes if sc["speak"]), key=lambda sc: sc["speak"][0])
    seqs = [sc["seq"] for sc in spoken]
    ok = seqs == sorted(seqs)
    return _item("order", "OK" if ok else "FAIL", "thứ tự đọc: " + " → ".join(map(str, seqs)), "tăng dần theo seq_index",
                 "sắp lại clip trên timeline theo seq_index của manifest")


def check_script(scenes: list[dict], tdir: Path | None) -> list[dict]:
    empty, low, notes = [], [], []
    for sc in scenes:
        s = sc["seg"]
        if s["type"] == "b-roll":
            for key in ("broll_prompt", "display_text"):
                if not (s.get(key) or "").strip():
                    empty.append(f"cảnh {sc['seq']}: {key} rỗng")
        if tdir is None:
            continue
        files = s.get("files") or {}
        name = stem(files.get("voice_file") or files.get("video_file") or "")
        tp = find_transcript(tdir, name) if name else None
        if tp is None:
            notes.append(f"cảnh {sc['seq']}: không thấy transcript {name}.json")
            continue
        ref, got = _tokens(s.get("tts_text", "")), transcript_tokens(tp)
        sim = difflib.SequenceMatcher(None, ref, got, autojunk=False).ratio() if ref or got else 1.0
        if sim < SIM_MIN:
            low.append(f"cảnh {sc['seq']}: lời đọc giống tts_text {sim:.2f} < {SIM_MIN:.2f}")
    items = [_item("script", "FAIL" if empty or low else "OK", "; ".join(empty + low) or "kịch bản đủ và khớp lời đọc",
                   f"broll_prompt + display_text không rỗng; giống ≥ {SIM_MIN:.2f}",
                   "bổ sung broll_prompt / display_text trong manifest; đọc lại hoặc sửa tts_text cho khớp giọng")]
    if notes:
        items.append(_item("script_transcript", "WARN", "; ".join(notes), "có transcript cho mỗi cảnh", "chạy lại bước transcribe"))
    return items


LIB_ID = re.compile(r"\b([A-Z]{2,4}\d{2,3})_B\d{2}")   # tên cảnh thư viện: KB07_B02_…, OPA05_B01_…


def check_source(manifest: dict, scenes: list[dict], pics: list[dict]) -> dict:
    """D9: cảnh thư viện ghi mã kịch bản khác (trong prompt hoặc tên file hình) = FAIL."""
    own = str(manifest.get("script_id") or "").upper()
    bad, seqs = [], []
    for sc in scenes:
        sp = sc["speak"] or (0.0, 0.0)
        texts = [sc["seg"].get("broll_prompt") or "", *(c["stem"] for c in pics if c["t0"] < sp[1] and c["t1"] > sp[0])]
        ids = sorted({m.upper() for t in texts for m in LIB_ID.findall(t)} - {own})
        if own and ids:
            bad.append(f"cảnh {sc['seq']}: dùng cảnh của {', '.join(ids)}")
            seqs.append(sc["seq"])
    return _item("script_source", "FAIL" if bad else "OK", "; ".join(bad) or "chỉ cảnh của chính kịch bản",
                 f"chỉ cảnh của {own or 'chính kịch bản'}", "tạo B-roll mới từ lời của chính cảnh (H5), không mượn cảnh kịch bản khác "
                 "(broll_fix.py plan → prepare → render_muse_broll.py --shot → verify)", scenes=seqs)


def check_broll_h5(scenes: list[dict]) -> dict:
    """H5: prompt B-roll rỗng / 'Clip thư viện' = FAIL; prompt chưa đạt lint H5 (tiếng Anh, 8–60 chữ, không chữ/logo…) = WARN."""
    fail, warn = [], []
    for sc in scenes:
        s = sc["seg"]
        if s["type"] != "b-roll":
            continue
        prompt = (s.get("broll_prompt") or "").strip()
        if not prompt or prompt.lower().startswith("clip thư viện"):
            fail.append((sc["seq"], "rỗng" if not prompt else "là mã «Clip thư viện», không phải prompt mô tả cảnh"))
            continue
        problems = lint_prompt(core_of(prompt))
        if problems:
            warn.append((sc["seq"], "; ".join(problems)))
    seqs = [q for q, _ in fail + warn]
    value = "; ".join(f"cảnh {q}: {m}" for q, m in fail + warn) or "prompt B-roll đạt H5"
    return _item("broll_h5", "FAIL" if fail else "WARN" if warn else "OK", value, "prompt B-roll tiếng Anh mô tả đúng lời cảnh (H5)",
                 "viết lại prompt từ lời của cảnh rồi chạy broll_fix.py lint / prepare", scenes=sorted(seqs))


def _fmt_range(r) -> str:
    return f"{r[0]:.2f}–{r[1]:.2f}s" if r else "—"


def review_md(scenes: list[dict], shown_by_seq: dict) -> str:
    def cell(x: str, n: int) -> str:
        x = (x or "").replace("|", "/").replace("\n", " ")
        return x if len(x) <= n else x[:n - 1] + "…"
    rows = ["| seq | loại | timeline | lời kịch bản | prompt | hình hiện (gồm cảnh chèn) |", "|---|---|---|---|---|---|"]
    for sc in scenes:
        s = sc["seg"]
        vis = "; ".join(f"{'**chèn** ' if x['cut'] else ''}{x['label']} {x['t0']:.2f}–{x['t1']:.2f}s" for x in shown_by_seq.get(sc["seq"], []))
        rows.append(f"| {sc['seq']} | {s['type']} | {_fmt_range(sc['speak'])} ({sc['speak_src']}) | {cell(s.get('display_text'), 120)} | "
                    f"{cell(s.get('broll_prompt'), 80)} | {vis or '—'} |")
    return "# Đối chiếu hình – lời từng cảnh\n\nMắt người kiểm: hình hiện có đúng điều lời đang nói không (D9, D14).\n\n" + "\n".join(rows) + "\n"


def run_checks(manifest: dict, spec: dict, tdir: Path | None = None, tol: float = 0.12, tol_tr: float = 0.5,
               words: list | None = None) -> tuple[list[dict], str]:
    pics, voices = read_spec(spec)
    scenes = build_scenes(manifest, pics, voices, words)
    av, cut, shown = check_av_sync(scenes, pics, tol, tol_tr)
    return [av, check_order(scenes), *check_script(scenes, tdir), check_source(manifest, scenes, pics),
            check_broll_h5(scenes), cut], review_md(scenes, shown)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--transcripts")
    ap.add_argument("--words", help="words_tl.json [[chữ, t0, t1], …] theo giờ timeline (giọng gộp)")
    ap.add_argument("--tol", type=float, default=0.12, help="lệch đầu tiếng–hình b-roll tối đa (giây)")
    ap.add_argument("--tol-transition", type=float, default=0.5, help="hình cảnh khác chiếm tối đa (giây) quanh điểm chuyển")
    ap.add_argument("--review")
    ap.add_argument("--json")
    a = ap.parse_args()
    try:
        manifest = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
        spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
        words = json.loads(Path(a.words).read_text(encoding="utf-8")) if a.words else None
    except (OSError, ValueError) as e:
        print(f"[SCENE FAIL] đọc đầu vào: {e}", file=sys.stderr)
        return 2
    items, review = run_checks(manifest, spec, Path(a.transcripts) if a.transcripts else None, a.tol, a.tol_transition, words)
    for r in items:
        print(f"[SCENE {r['status']:<4}] {r['id']:<18} {r['value']}" + (f"  → {r['fix']}" if r["fix"] else ""))
    if a.review:
        Path(a.review).write_text(review, encoding="utf-8")
    if a.json:
        Path(a.json).write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    return 1 if any(r["status"] == "FAIL" for r in items) else 0


if __name__ == "__main__":
    sys.exit(main())
