#!/usr/bin/env python3
"""auto-footage — tìm hoặc tạo B-roll (video cảnh chèn / ảnh) cho từng cảnh của video / kịch bản.

    F=~/.venvs/footage/bin/python; S=~/.claude/skills/auto-footage/scripts
    $F $S/footage.py transcribe VIDEO --out DIR [--prompt "kịch bản"]   # lời có mốc để chia cảnh
    $F $S/footage.py draft DIR/transcript.json|kich_ban.txt --project X -o scenes.json   # khung cảnh, agent điền query
    $F $S/footage.py index                                             # cập nhật chỉ mục CLIP kho 06_B-Roll (video + ảnh)
    $F $S/footage.py search "bored man in front of a laptop" [--kind image] [--sources local,pexels,pixabay,mixkit]
    $F $S/footage.py run scenes.json                                   # tìm / tạo, tải, chuẩn hoá, picks.json + sheet + review
    $F $S/footage.py make "mô tả tiếng Anh" --kind image|video|both [--n 2] [--project X] [--ref mat.jpg] [--animate]
                     [--seconds 30 [--seg 8] [--steps "đoạn 1" "đoạn 2" …] [--no-chain]]   # > 10 s: nối đoạn giữ bối cảnh
    $F $S/footage.py pick picks.json --scene 3 --alt 2                 # đổi lựa chọn của cảnh 3 sang số 2
    $F $S/footage.py render picks.json                                 # vẽ lại sheet.jpg + review.html
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch  # noqa: E402
import media  # noqa: E402
import review  # noqa: E402
import sources  # noqa: E402

ROOT = fetch.ROOT
THRESHOLD = 0.27            # ViT-B-32 (đã cộng điểm thưởng): đúng nghĩa đo được ≥ 0,28, lạc nghĩa ~0,24–0,25 → dưới mức này tạo bằng Muse
ALL_SOURCES = ("local", "pexels", "pixabay", "mixkit")
KINDS = ("video", "image", "both")
VS_PY = Path.home() / ".venvs/video-skills/bin/python"


def log(*a) -> None:
    print(*a, flush=True)


# ---------- chọn ----------
def orientation(c: dict) -> str:
    return "portrait" if c.get("h", 0) > c.get("w", 0) else "landscape"


def select(cands: list[dict], want: str = "portrait", min_dur: float = 3.0, n: int = 3, used: set | None = None) -> list[dict]:
    """Điểm CLIP + 0,01 đúng hướng khung + 0,01 đã có trong kho; clip ngắn hơn min_dur −0,05; đã được chọn cho cảnh trước −0,03
    (để các cảnh không lặp cùng một clip). Bỏ trùng."""
    seen, ranked = set(), []
    for c in cands:
        k = (c["source"], c["id"])
        if k in seen:
            continue
        seen.add(k)
        s = c["score"] + (0.01 if want in ("any", orientation(c)) else 0) + (0.01 if c["source"] == "local" else 0)
        if c.get("duration") and c["duration"] < min_dur:
            s -= 0.05
        if used and k in used:
            s -= 0.03
        ranked.append({**c, "rank_score": round(s, 4)})
    return sorted(ranked, key=lambda c: -c["rank_score"])[:n]


def need_muse(picks: list[dict], mode: str) -> bool:
    return mode == "always" or (mode != "never" and (not picks or picks[0]["rank_score"] < THRESHOLD))


# ---------- scenes.json ----------
def load_scenes(path: Path) -> dict:
    cfg = json.loads(path.read_text())
    errs = [] if cfg.get("project") else ["thiếu 'project'"]
    scenes = cfg.get("scenes") or []
    if not scenes:
        errs.append("thiếu 'scenes'")
    out = []
    for i, s in enumerate(scenes, 1):
        s.setdefault("id", i)
        sid = s["id"]
        kind = s.get("kind", cfg.get("kind", "video"))
        if not s.get("query"):
            errs.append(f"cảnh {sid}: thiếu 'query' (tiếng Anh, tả hình)")
        if kind not in KINDS:
            errs.append(f"cảnh {sid}: 'kind' phải là video | image | both")
        if s.get("muse", "auto") not in ("auto", "always", "never"):
            errs.append(f"cảnh {sid}: 'muse' phải là auto | always | never")
        if s.get("muse") == "always" and not s.get("muse_prompt"):
            errs.append(f"cảnh {sid}: muse=always cần 'muse_prompt'")
        if not 1 <= int(s.get("seconds", 5)) <= 600:
            errs.append(f"cảnh {sid}: 'seconds' (độ dài video Muse) 1–600")
        if not s.get("chain", True) and int(s.get("seconds", 5)) > 60:
            errs.append(f"cảnh {sid}: video Muse liền (chain: false) tối đa 60 s")
        if not 5 <= int(s.get("seg_seconds", 8)) <= 10:
            errs.append(f"cảnh {sid}: 'seg_seconds' (độ dài mỗi đoạn khi nối) 5–10")
        if s.get("muse_steps") is not None and not (isinstance(s["muse_steps"], list) and all(isinstance(x, str) for x in s["muse_steps"])):
            errs.append(f"cảnh {sid}: 'muse_steps' phải là danh sách câu mô tả từng đoạn")
        refs = s.get("muse_ref", cfg.get("muse_ref", []))
        bad = [r for r in refs if not Path(r).is_file()]
        if len(refs) > 4 or bad:
            errs.append(f"cảnh {sid}: muse_ref tối đa 4 ảnh có thật ({', '.join(bad) or 'quá 4'})")
        s["muse_ref"] = refs
        if kind == "both":                       # một cảnh → cảnh video + cảnh ảnh "<id>-anh" (Muse dùng chung một ảnh)
            out += [{**s, "kind": "video", "base_id": sid}, {**s, "kind": "image", "id": f"{sid}-anh", "base_id": sid}]
        else:
            out.append({**s, "kind": kind})
    if errs:
        raise SystemExit("scenes.json lỗi:\n  " + "\n  ".join(errs))
    cfg.setdefault("orientation", "portrait")
    cfg["scenes"] = out
    return cfg


# ---------- tìm ----------
class Finder:
    def __init__(self, use: tuple = ALL_SOURCES) -> None:
        from clip_rank import Ranker
        from library import Library
        self.ranker = Ranker()
        self.lib = Library(ROOT)
        self.keys = sources.keys()
        self.use = list(use)
        self.warn: list[str] = []
        for src, k in (("pexels", "PEXELS_API_KEY"), ("pixabay", "PIXABAY_API_KEY")):
            if src in self.use and not self.keys[k]:
                self.use.remove(src)
                self.warn.append(f"{src}: chưa có {k} trong {sources.ENV} → bỏ qua nguồn này")

    def remote(self, query: str, want: str, tags: list[str] | None, kind: str = "video") -> tuple[list[dict], list[str]]:
        k = self.keys
        if kind == "image":                       # Mixkit không có ảnh
            calls = {"pexels": (sources.pexels_photos, query, want, k["PEXELS_API_KEY"]),
                     "pixabay": (sources.pixabay_photos, query, want, k["PIXABAY_API_KEY"])}
        else:
            calls = {"pexels": (sources.pexels, query, want, k["PEXELS_API_KEY"]),
                     "pixabay": (sources.pixabay, query, k["PIXABAY_API_KEY"]),
                     "mixkit": (sources.mixkit, tags or sources.mixkit_tags(query))}
        out, errs = [], []
        with ThreadPoolExecutor(3) as ex:
            jobs = {name: ex.submit(fn, *args) for name, (fn, *args) in calls.items() if name in self.use}
            for name, fut in jobs.items():
                try:
                    out += fut.result()
                except Exception as e:  # noqa: BLE001 — một nguồn lỗi không dừng cả lượt
                    errs.append(f"{name}: {e}")
        return out, errs

    def find(self, queries: list[str], want: str = "portrait", tags: list[str] | None = None, kind: str = "video",
             top_local: int = 8) -> tuple[list, list]:
        from clip_rank import best_score
        q = self.ranker.text(queries)
        cands = self.lib.search(q, top_local, kind) if "local" in self.use else []
        remote, errs = self.remote(queries[0], want, tags, kind)
        owned = self.lib.owned_ids()
        remote = [c for c in remote if c["id"] not in owned and c.get("thumb")]   # kho đã có → dùng bản trong kho
        if remote:
            def get(c):
                return c["thumb"], (None if self.ranker.cached(c["thumb"]) else _safe_get(c["thumb"]))
            with ThreadPoolExecutor(8) as ex:
                items = list(ex.map(get, remote))
            for c, s in zip(remote, best_score(q, self.ranker.thumbs(items))):
                c["score"] = float(s)
            cands += remote
        return cands, errs


def _safe_get(url: str) -> bytes | None:
    try:
        return media.http_get(url, timeout=20, tries=2)
    except Exception:  # noqa: BLE001
        return None


def _muse_ready() -> bool:
    import muse
    return muse.ready()


# ---------- Muse + ảnh động (dùng chung cho run và make) ----------
def run_muse(rows: list[dict], project: str) -> None:
    """rows: [{"scene", "picks", "errors"}] cần Muse. Gộp theo ảnh chung (cảnh "both") → 1 việc / ảnh, 2 việc song song."""
    if not _muse_ready():
        for r in rows:
            r["errors"].append("muse: dịch vụ không sẵn sàng — chưa tạo")
        return
    groups: dict[Path, list[dict]] = {}
    for r in rows:
        groups.setdefault(fetch.muse_base(project, r["scene"]), []).append(r)
    log(f"Muse tạo {len(groups)} ảnh ({sum(1 for r in rows if r['scene']['kind'] == 'video')} thành video, ~1–2 phút / video)…")

    def job(rs):
        s = rs[0]["scene"]
        return fetch.muse_make(s, project, s["muse_ref"], any(r["scene"]["kind"] == "video" for r in rs),
                               int(s.get("seconds", 5)), log)
    with ThreadPoolExecutor(2) as ex:
        futs = [(rs, ex.submit(job, rs)) for rs in groups.values()]
        for rs, fut in futs:
            try:
                made = fut.result()
            except Exception as e:  # noqa: BLE001
                for r in rs:
                    r["errors"].append(f"muse: {e}")
                continue
            for r in rs:
                m = made[r["scene"]["kind"]]
                r["picks"] = [m, *[p for p in r["picks"] if p.get("path") != m["path"]]][:3]


def add_animation(rows: list[dict], project: str) -> None:
    for r in rows:
        s = r["scene"]
        if s["kind"] == "image" and s.get("animate") and r["picks"]:
            try:
                r["picks"][0]["anim"] = fetch.animate(r["picks"][0], project, float(s.get("anim_seconds", 5)))
            except Exception as e:  # noqa: BLE001
                r["errors"].append(f"ảnh động: {e}")


def finish(rows: list[dict], project_name: str, outdir: Path, cfg: dict) -> None:
    picks = {"project": project_name, "created": dt.datetime.now().isoformat(timespec="seconds"), "scenes": []}
    for r in rows:
        s = r["scene"]
        status = "missing" if not r["picks"] else ("muse" if r["picks"][0]["source"] == "muse" else "ok")
        picks["scenes"].append({"id": s["id"], "kind": s["kind"], "text": s.get("text", ""), "t": s.get("t"), "query": s["query"],
                                "status": status, "chosen": 0, "picks": r["picks"], "errors": r["errors"]})
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "scenes.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=1))
    write_picks(outdir / "picks.json", picks)
    n_ok = sum(1 for s in picks["scenes"] if s["status"] != "missing")
    log(f"xong: {n_ok}/{len(picks['scenes'])} cảnh có kết quả · {outdir / 'sheet.jpg'} · {outdir / 'review.html'}")


def write_picks(path: Path, picks: dict) -> None:
    path.write_text(json.dumps(picks, ensure_ascii=False, indent=1))
    review.render(path, picks)


# ---------- lệnh ----------
def cmd_transcribe(a) -> None:
    cmd = [str(VS_PY), str(Path(__file__).with_name("transcribe.py")), str(a.video), str(a.out)]
    if a.prompt:
        cmd += ["--prompt", a.prompt]
    subprocess.run(cmd, check=True)


def cmd_index(a) -> None:
    f = Finder(("local",))
    n = f.lib.update(f.ranker)
    n_img = sum(1 for x in f.lib.files if x.get("type") == "image")
    log(f"chỉ mục {ROOT}: {len(f.lib.files) - n_img} video + {n_img} ảnh ({n} mới / đổi)")


def cmd_search(a) -> None:
    f = Finder(tuple(a.sources.split(",")))
    for w in f.warn:
        log("⚠", w)
    cands, errs = f.find([a.query], a.orientation, kind=a.kind)
    for e in errs:
        log("⚠", e)
    for c in select(cands, a.orientation, 0, a.top):
        log(f"{c['rank_score']:.3f}  {c['source']:7} {orientation(c)[:4]} {c.get('duration') or 0:5.1f}s  {c['title'][:50]}  "
            f"{c.get('path') or c['page']}")


def cmd_run(a) -> None:
    cfg = load_scenes(a.scenes)
    project = media.slug(cfg["project"], 40)
    f = Finder(tuple(cfg.get("sources", ALL_SOURCES)))
    for w in f.warn:
        log("⚠", w)
    n_new = f.lib.update(f.ranker, log)
    log(f"kho: {len(f.lib.files)} file ({n_new} mới) · nguồn: {', '.join(f.use)} · Muse: {'sẵn sàng' if _muse_ready() else 'KHÔNG sẵn sàng'}")
    want = cfg["orientation"]
    rows, used = [], set()
    for s in cfg["scenes"]:
        cands, errs = f.find([s["query"], *s.get("alt_queries", [])], s.get("orientation", want), s.get("mixkit_tags"), s["kind"])
        picks = select(cands, s.get("orientation", want), float(s.get("min_dur", 3)), used=used)
        if picks:
            used.add((picks[0]["source"], picks[0]["id"]))
        rows.append({"scene": s, "picks": picks, "errors": errs, "category": media.slug(s.get("category") or s["query"], 24)})
        best = f"{picks[0]['rank_score']:.3f} {picks[0]['source']}" if picks else "—"
        log(f"cảnh {s['id']} ({s['kind']}): {len(cands)} ứng viên · tốt nhất {best}" + (f" · lỗi: {'; '.join(errs)}" if errs else ""))
    with ThreadPoolExecutor(4) as ex:                 # tải bản đầy đủ nguồn ngoài song song
        jobs = [(r, i, ex.submit(fetch.save_remote, p, r["category"], project)) for r in rows
                for i, p in enumerate(r["picks"]) if p["source"] != "local"]
        for r, i, fut in jobs:
            try:
                r["picks"][i] = fut.result()
            except Exception as e:  # noqa: BLE001
                r["errors"].append(str(e))
                r["picks"][i] = None
    for r in rows:
        r["picks"] = [p for p in r["picks"] if p]
    muse_rows = [r for r in rows if need_muse(r["picks"], r["scene"].get("muse", "auto")) and r["scene"].get("muse_prompt")]
    if muse_rows:
        run_muse(muse_rows, project)
    add_animation(rows, project)
    finish(rows, cfg["project"], ROOT / "_Tim_Footage" / project, cfg)


def cmd_make(a) -> None:
    """Tạo nhanh bằng Muse, không cần kịch bản: n biến thể × (ảnh | video | cả hai)."""
    project = media.slug(a.project, 40)
    base = {"query": a.prompt, "muse_prompt": a.prompt, "muse": "always", "category": a.name or a.prompt[:40],
            "muse_ref": a.ref or [], "seconds": a.seconds, "animate": a.animate, "text": a.prompt,
            "chain": not a.no_chain, "seg_seconds": a.seg, "camera": "move" if a.camera_move else "static",
            **({"muse_steps": a.steps} if a.steps else {})}
    bad = [r for r in base["muse_ref"] if not Path(r).is_file()]
    if bad or len(base["muse_ref"]) > 4:
        raise SystemExit(f"--ref tối đa 4 ảnh có thật ({', '.join(bad)})")
    cfg = {"project": a.project, "kind": a.kind, "scenes": [{**base, "id": k} for k in range(1, a.n + 1)]}
    tmp = ROOT / "_Tim_Footage" / project / f"make-{os.getpid()}.json"   # riêng mỗi tiến trình (chạy song song cùng dự án)
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(json.dumps(cfg, ensure_ascii=False, indent=1))
    cfg = load_scenes(tmp)
    tmp.unlink()                                   # finish() ghi scenes.json đầy đủ
    rows = [{"scene": s, "picks": [], "errors": []} for s in cfg["scenes"]]
    run_muse(rows, project)
    add_animation(rows, project)
    finish(rows, a.project, tmp.parent, cfg)
    for r in rows:
        for p in r["picks"][:1]:
            log(f"  {r['scene']['id']}: {p['path']}" + (f"  (ảnh động: {p['anim']})" if p.get("anim") else ""))


def cmd_render(a) -> None:
    sheet, page = review.render(a.picks, json.loads(a.picks.read_text()))
    log(f"{sheet}\n{page}")


def cmd_draft(a) -> None:
    import draft
    d = draft.draft(a.src, a.project)
    a.out.write_text(json.dumps(d, ensure_ascii=False, indent=1))
    log(f"{len(d['scenes'])} cảnh → {a.out} (điền query / alt_queries / category / muse_prompt rồi chạy run)")
    for sc in d["scenes"]:
        t = f"{sc['t'][0]:6.2f}–{sc['t'][1]:6.2f}" if sc["t"] else "      —      "
        log(f"  {sc['id']:2} [{t}] {sc['text'][:90]}")


def cmd_pick(a) -> None:
    picks = json.loads(a.picks.read_text())
    s = next((s for s in picks["scenes"] if str(s["id"]) == str(a.scene)), None)
    if s is None or not 1 <= a.alt <= len(s["picks"]):
        raise SystemExit(f"không có cảnh {a.scene} / lựa chọn {a.alt}")
    s["chosen"] = a.alt - 1
    write_picks(a.picks, picks)
    log(f"cảnh {a.scene} → {s['picks'][a.alt - 1]['path']}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("transcribe"); p.add_argument("video", type=Path); p.add_argument("--out", type=Path, required=True)
    p.add_argument("--prompt")
    sub.add_parser("index")
    p = sub.add_parser("search"); p.add_argument("query"); p.add_argument("--sources", default=",".join(ALL_SOURCES))
    p.add_argument("--orientation", default="portrait", choices=["portrait", "landscape", "any"]); p.add_argument("--top", type=int, default=8)
    p.add_argument("--kind", default="video", choices=["video", "image"])
    p = sub.add_parser("run"); p.add_argument("scenes", type=Path)
    p = sub.add_parser("make"); p.add_argument("prompt"); p.add_argument("--kind", default="video", choices=KINDS)
    p.add_argument("--n", type=int, default=1); p.add_argument("--project", default="Tao_Nhanh"); p.add_argument("--name")
    p.add_argument("--ref", nargs="+"); p.add_argument("--seconds", type=int, default=5); p.add_argument("--animate", action="store_true")
    p.add_argument("--seg", type=int, default=8, help="độ dài mỗi đoạn khi nối (5–10 s, dùng khi --seconds > 10)")
    p.add_argument("--no-chain", action="store_true", help="> 10 s vẫn tạo một video liền (bối cảnh dễ trôi)")
    p.add_argument("--steps", nargs="+", help="mô tả riêng từng đoạn khi nối (thiếu thì lặp mô tả cuối)")
    p.add_argument("--camera-move", action="store_true", help="clip nối: cho máy chuyển động (mặc định máy đứng yên để giữ bối cảnh)")
    p = sub.add_parser("draft"); p.add_argument("src", type=Path); p.add_argument("--project", required=True)
    p.add_argument("-o", "--out", type=Path, required=True)
    p = sub.add_parser("render"); p.add_argument("picks", type=Path)
    p = sub.add_parser("pick"); p.add_argument("picks", type=Path); p.add_argument("--scene", required=True)
    p.add_argument("--alt", type=int, required=True)
    a = ap.parse_args()
    {"transcribe": cmd_transcribe, "index": cmd_index, "search": cmd_search, "run": cmd_run, "make": cmd_make, "pick": cmd_pick,
     "draft": cmd_draft, "render": cmd_render}[a.cmd](a)


if __name__ == "__main__":
    main()
