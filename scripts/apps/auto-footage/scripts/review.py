"""Bảng ảnh (sheet.jpg) + trang duyệt có phát video (review.html) từ picks.json."""
from __future__ import annotations

import html
import os
from pathlib import Path

import media

SRC_NAME = {"local": "kho", "mixkit": "Mixkit", "pexels": "Pexels", "pixabay": "Pixabay", "muse": "Muse AI"}


def orient(p: dict) -> str:
    return "dọc" if p.get("h", 0) > p.get("w", 0) else "ngang"


def is_image(p: dict) -> bool:
    return Path(p.get("path", "")).suffix.lower() in media.IMG_EXT


def caption(k: int, p: dict) -> str:
    sc = f" {p['rank_score']:.2f}" if p.get("rank_score") is not None else " (tạo mới)"
    what = ("ảnh + động" if p.get("anim") else "ảnh") if is_image(p) else f"{p.get('duration') or 0:.0f}s"
    return f"{k} · {SRC_NAME.get(p['source'], p['source'])}{sc} · {what} · {orient(p)}"


def render(picks_path: Path, picks: dict) -> tuple[Path, Path]:
    blocks = []
    for s in picks["scenes"]:
        cells = [(media.frame(Path(p["path"]), (p.get("duration") or 2) / 2) if p.get("path") else None, caption(k, p), k - 1 == s["chosen"])
                 for k, p in enumerate(s["picks"], 1)]
        t = f" · {s['t'][0]:.1f}–{s['t'][1]:.1f}s" if s.get("t") else ""
        kind = " · ảnh" if s.get("kind") == "image" else ""
        blocks.append((f"Cảnh {s['id']}{t}{kind} · {s['status']}", s.get("text") or s["query"], cells or [(None, "không có kết quả", False)]))
    sheet = media.contact_sheet(blocks, picks_path.with_name("sheet.jpg"))
    page = picks_path.with_name("review.html")
    page.write_text(_html(picks, page.parent), encoding="utf-8")
    return sheet, page


def _html(picks: dict, base: Path) -> str:
    e = html.escape
    parts = [f"""<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Duyệt footage · {e(picks['project'])}</title>
<style>
body{{margin:0;padding:20px;background:#161616;color:#eee;font:15px/1.45 system-ui,sans-serif}}
h1{{font-size:20px;margin:0 0 4px}} .hint{{color:#aaa;margin:0 0 18px}}
.scene{{border-top:1px solid #333;padding:14px 0}} .scene h2{{font-size:16px;margin:0;color:#ffd23c}}
.scene p{{margin:4px 0 10px;color:#ccc}} .q{{color:#888;font-size:13px}}
.row{{display:flex;gap:12px;flex-wrap:wrap}} figure{{margin:0;width:220px}}
video,img.m{{width:220px;height:391px;background:#000;object-fit:contain;border-radius:6px;border:3px solid transparent}}
figure.on video,figure.on img.m{{border-color:#ffd23c}} a{{color:#8cc8ff}} figcaption{{font-size:13px;margin-top:4px}} figure.on figcaption{{color:#ffd23c}}
.err{{color:#f77;font-size:13px}}
</style>
<h1>Duyệt footage · {e(picks['project'])}</h1>
<p class="hint">Viền vàng = lựa chọn đang dùng. Rê chuột lên clip để phát. Muốn đổi, nói: "cảnh N lấy số K".</p>"""]
    for s in picks["scenes"]:
        t = f" · {s['t'][0]:.1f}–{s['t'][1]:.1f}s" if s.get("t") else ""
        parts.append(f'<section class="scene"><h2>Cảnh {s["id"]}{t} · {e(s["status"])}</h2><p>{e(s.get("text") or "")}</p>'
                     f'<div class="q">query: {e(s["query"])}</div><div class="row">')
        for k, p in enumerate(s["picks"], 1):
            rel = os.path.relpath(p["path"], base) if p.get("path") else ""
            on = " class=\"on\"" if k - 1 == s["chosen"] else ""
            media_tag = (f'<img class="m" src="{e(rel)}" loading="lazy" alt="">' if is_image(p) else
                         f'<video src="{e(rel)}" muted loop playsinline preload="metadata" '
                         f'onmouseenter="this.play()" onmouseleave="this.pause()"></video>')
            anim = (f'<br><a href="{e(os.path.relpath(p["anim"], base))}">▶ ảnh động</a>' if p.get("anim") else "")
            parts.append(f'<figure{on}>{media_tag}<figcaption>{e(caption(k, p))}<br>'
                         f'<span class="q">{e(Path(p.get("path", "")).name[:42])}</span>{anim}</figcaption></figure>')
        if not s["picks"]:
            parts.append('<p class="err">Không có kết quả phù hợp.</p>')
        parts.append("</div>")
        for err in s.get("errors", []):
            parts.append(f'<div class="err">⚠ {e(err)}</div>')
        parts.append("</section>")
    return "\n".join(parts) + "\n</html>\n"
