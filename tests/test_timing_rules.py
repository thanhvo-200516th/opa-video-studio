#!/usr/bin/env python3
"""Hồ sơ minimal-edu, phần TIMING: C7 cut_lead · C8 text_cut_overrun · C1 theo hồ sơ · SFX highlighter + sfx_density ·
silence_cut pad/snap theo hồ sơ. Spec giả, không mở FilmCraft.
Chạy: ~/.venvs/video-skills/bin/python tests/test_timing_rules.py"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import edit_rules  # noqa: E402
import qa_sync  # noqa: E402
import style_profile  # noqa: E402
from silence_cut import speech_segments  # noqa: E402

fails: list[str] = []
PROF = style_profile.load(name="minimal-edu")


def check(ok: bool, label: str, detail: str = "") -> None:
    print(f"[{'OK' if ok else 'LỖI'}] {label}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        fails.append(label)


def spec(starts=(0.0, 3.0), texts=(), trans=None, sfx_n=0, dur=6.0) -> dict:
    """V1 có clip bắt đầu ở `starts` (mỗi clip dài tới clip kế); texts = [(at, end)] ở lane text_top;
    trans = {chỉ số clip: transition_in}; sfx_n = số SFX trong track âm."""
    ends = list(starts[1:]) + [dur]
    v1 = [{"src": "a.mp4", "at": a, "dur": e - a, "name": f"A{i}"} for i, (a, e) in enumerate(zip(starts, ends))]
    for i, t in (trans or {}).items():
        v1[i]["transition_in"] = t
    tracks = [{"type": "video", "name": "V1 chuỗi", "clips": v1}]
    if texts:
        tracks.append({"type": "video", "name": "text_top 1", "clips": [
            {"src": "t.png", "text": "ý chính", "color": "#FFFFFF", "at": a, "dur": e - a, "name": "chữ"} for a, e in texts]})
    if sfx_n:
        tracks.append({"type": "audio", "name": "SFX 1", "clips": [
            {"src": "s.wav", "at": i * 0.5, "dur": 0.3, "name": "SFX pop · x"} for i in range(sfx_n)]})
    return {"fps": 30, "duration": dur, "tracks": tracks}


def rule(res: list[dict], prefix: str) -> dict:
    hit = [r for r in res if r["rule"].startswith(prefix)]
    assert len(hit) == 1, (prefix, [r["rule"] for r in res])
    return hit[0]


def w(*starts: float) -> list:
    return [["từ", s] for s in starts]


def test_cut_lead() -> None:
    sp = spec()
    for t, want in ((3.050, "OK"), (2.950, "LỖI"), (3.200, "OK"), (3.120, "CẢNH BÁO"), (3.000, "OK")):
        r = rule(edit_rules.audit_spec(sp, w(1.0, t)), "C7")
        check(r["status"] == want, f"C7 mặc định: chữ đầu {t} → {want}", f"{r['status']} {r['detail']}")
    r = rule(edit_rules.audit_spec(sp, w(1.0, 3.2)), "C7")
    check("bỏ qua" in r["detail"], "C7: chữ đầu 3,200 bị bỏ qua (không phải đầu câu)", r["detail"])
    check(rule(edit_rules.audit_spec(sp), "C7")["status"] == "CHƯA KIỂM", "C7: thiếu --words → CHƯA KIỂM")
    for t, want in ((3.050, "OK"), (3.080, "CẢNH BÁO"), (2.950, "LỖI")):
        r = rule(edit_rules.audit_spec(sp, w(1.0, t), profile=PROF), "C7")
        check(r["status"] == want, f"C7 hồ sơ (≤ 0,067 s): chữ đầu {t} → {want}", f"{r['status']} {r['detail']}")
    check(rule(edit_rules.audit_spec(sp, w(1.0, 3.080)), "C7")["status"] == "OK", "C7 mặc định: 3,080 vẫn OK (≤ 0,09)")


def test_text_cut() -> None:
    for e, want_def, want_prof in ((2.967, "OK", "OK"), (3.000, "OK", "OK"), (3.100, "CẢNH BÁO", "CẢNH BÁO"),
                                   (2.900, "OK", "CẢNH BÁO"), (3.040, "CẢNH BÁO", "CẢNH BÁO"), (5.0, "OK", "OK")):
        sp = spec(texts=[(2.0, e)])
        a = rule(edit_rules.audit_spec(sp), "C8")["status"]
        b = rule(edit_rules.audit_spec(sp, profile=PROF), "C8")["status"]
        check(a == want_def and b == want_prof, f"C8 chữ kết thúc {e}: mặc định {want_def} · hồ sơ {want_prof}", f"{a}/{b}")
    check(rule(edit_rules.audit_spec(spec(texts=[])), "C8")["status"] == "OK", "C8: không có chữ chính → OK")


def test_c1_profile() -> None:
    hard = spec(starts=(0, 2, 4, 6), dur=8, trans={1: {"effect": "cross_dissolve", "frames": 1}})
    c1 = "Mọi điểm cắt có chuyển cảnh"
    check(rule(edit_rules.audit_spec(hard), c1)["status"] == "LỖI", "C1 không hồ sơ: cắt cứng → LỖI")
    on = edit_rules.audit_spec(hard, profile=PROF)
    check(rule(on, c1)["status"] == "OK", "C1 có hồ sơ: cắt cứng được phép → OK", rule(on, c1)["detail"])
    div = rule(on, "Chuyển cảnh đa dạng")
    check("cross_dissolve" in div["detail"] and div["status"] == "CẢNH BÁO",
          "3.6.2: cắt cứng 67 % + 1 kiểu → CẢNH BÁO (cắt cứng ≤ 40 %, ≥ 6 kiểu)", div["detail"])
    kinds = ["soft_wipe", "punch_settle", "blur_dissolve_cut", "card_swipe", "drift_reset", "iris_round_focus", "j_cut_return"]
    mix = spec(starts=tuple(range(0, 16, 2)), dur=16)
    v1 = mix["tracks"][0]["clips"]
    for c, k in zip(v1[1:], kinds):
        c["name"] += " ⇢ " + k
    dm = rule(edit_rules.audit_spec(mix, profile=PROF), "Chuyển cảnh đa dạng")
    check(dm["status"] == "OK" and "cắt cứng 14%" in dm["detail"],
          "3.6.2: 6 kiểu talking-head + 1 j_cut (tính là cắt cứng) → OK", dm["detail"])
    twice = spec(starts=tuple(range(0, 16, 2)), dur=16)
    for c, k in zip(twice["tracks"][0]["clips"][1:], kinds[:3] + ["paper_rip", "soft_wipe", "paper_rip", "card_swipe"]):
        c["name"] += " ⇢ " + k
    dt = rule(edit_rules.audit_spec(twice, profile=PROF), "Chuyển cảnh đa dạng")
    check(dt["status"] == "CẢNH BÁO" and "paper_rip" in dt["detail"], "3.6.2: giấy rách 2 lần → CẢNH BÁO", dt["detail"])
    only_hard = edit_rules.audit_spec(spec(starts=(0, 2, 4, 6), dur=8), profile=PROF)
    check(rule(only_hard, "Chuyển cảnh đa dạng")["status"] == "CẢNH BÁO", "hồ sơ: toàn cắt cứng → thiếu kiểu (< 2) CẢNH BÁO")
    flashy = spec(starts=(0, 2, 4), dur=6, trans={1: {"effect": "flash_burst", "frames": 4}})
    check(rule(edit_rules.audit_spec(flashy, profile=PROF), "Chuyển cảnh đa dạng")["status"] == "CẢNH BÁO",
          "hồ sơ: nháy sáng > 0 % → CẢNH BÁO (max_flashy_share = 0)")
    # không hồ sơ: lặp liền vẫn bắt như cũ
    same = spec(starts=(0, 2, 4), dur=6, trans={1: {"effect": "slide", "frames": 4}, 2: {"effect": "slide", "frames": 4}})
    check(rule(edit_rules.audit_spec(same), "Chuyển cảnh đa dạng")["status"] == "CẢNH BÁO", "không hồ sơ: lặp liền / < 6 kiểu vẫn CẢNH BÁO")


def test_no_regression() -> None:
    sp = spec(starts=(0, 2, 4), dur=6, texts=[(2.0, 3.1)], sfx_n=3)
    base = edit_rules.audit_spec(sp, w(1.0, 2.05))
    check(base == edit_rules.audit_spec(sp, w(1.0, 2.05), profile=None), "profile=None ≡ không truyền profile")
    old = [r for r in base if not r["rule"].startswith(("C7", "C8", "sfx_density"))]
    names = [r["rule"] for r in old]
    check(rule(old, "Mọi điểm cắt")["status"] == "LỖI" and "Chuyển cảnh đa dạng (flash / flicker ≤ 25 %, ≥ 6 kiểu, không lặp liền)" in names,
          "dòng cũ giữ nguyên tên, C1 vẫn LỖI khi không hồ sơ", str(names))


def test_sfx() -> None:
    check(qa_sync.beat_of("SFX highlighter · đồ thị") == "text" and "highlighter" in qa_sync.TEXT_KINDS,
          "beat_of: SFX highlighter = nhịp chữ, không phải cắt")
    check(qa_sync.beat_of("SFX whoosh · cắt") == "cut", "beat_of: whoosh vẫn là cắt")
    cat = json.loads((ROOT / "assets/motion-fx/sfx_catalog.json").read_text(encoding="utf-8"))
    k = cat["kinds"].get("highlighter", {})
    check(bool(k.get("files")) and k.get("tier") == "soft" and k.get("align") == "onset", "catalog có kind highlighter (soft, onset)")
    r = rule(edit_rules.audit_spec(spec(sfx_n=6, dur=6.0)), "sfx_density")
    check(r["status"] == "OK" and "1.00" in r["detail"], "sfx_density: 6 SFX / 6 s = 1.00 /s (chỉ báo)", r["detail"])


def wav(path: Path, parts: list[str]) -> Path:
    args = sum((["-f", "lavfi", "-i", s] for s in parts), [])
    graph = "".join(f"[{i}]aresample=48000,aformat=channel_layouts=mono[a{i}];" for i in range(len(parts)))
    graph += "".join(f"[a{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=0:a=1[o]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", graph, "-map", "[o]", str(path)], check=True, timeout=60)
    return path


def test_silence_cut() -> None:
    with tempfile.TemporaryDirectory() as td:
        f = wav(Path(td) / "v.wav", ["anullsrc=r=48000:cl=mono:d=1.05", "sine=f=300:d=1.5"])
        words = [{"text": "a", "start": 1.05, "end": 2.4}]
        d = speech_segments(f, words)
        check(abs(d[0][0] - 29 / 30) < 1e-6, "mặc định giữ nguyên: pad 0,07 + round → 0,967", str(d))
        p = speech_segments(f, words, profile=PROF)
        check(abs(p[0][0] - 1.0) < 1e-6, "hồ sơ: pad 0,03 + floor → 1,000 (0–2 khung trước chữ)", str(p))
        check(p[0][0] <= 1.05 and 1.05 - p[0][0] <= 2 / 30 + 1e-6, "hồ sơ: cắt trước chữ đầu 0–2 khung", str(p))
        q = speech_segments(f, words, pad=0.03, snap="floor")
        check(q == p, "pad / snap truyền tay ≡ qua hồ sơ", f"{q} {p}")
        r = speech_segments(f, words, pad=0.03)
        check(abs(r[0][0] - 31 / 30) < 1e-6, "chỉ pad (snap round mặc định) → 1,033", str(r))


def test_p8_p11_font_glow() -> None:
    """P8: hồ sơ nhận 2–3 font; P11: hồ sơ bắt chữ màu sáng phải glow (trắng / đen không). Không hồ sơ: giữ 4–6 và CẢNH BÁO."""
    def txt(fam, i):
        return {"type": "text", "name": f"text 1", "clips": [{"text": f"t{i}", "font": fam, "at": float(i), "dur": 1.0, "color": "#FFFFFF"}]}
    sp = {"fps": 30, "duration": 6.0, "tracks": [{"type": "video", "name": "V1", "clips": [{"src": "a.mp4", "at": 0, "dur": 6}]},
                                                 txt("Inter", 0), txt("Playfair Display", 1)]}
    sp["tracks"][1]["clips"][0]["color"] = "#123CE8"          # chữ chính không trắng, không glow
    off, on = edit_rules.audit_spec(sp), edit_rules.audit_spec(sp, profile=PROF)
    check(rule(off, "Font")["status"] == "LỖI", "không hồ sơ: 2 font → LỖI (4–6)")
    check(rule(on, "Font")["status"] == "OK", "hồ sơ: 2 font → OK (P8: 2–3)", rule(on, "Font")["detail"])
    four = {**sp, "tracks": sp["tracks"] + [txt("A", 2), txt("B", 3), txt("C", 4)]}
    check(rule(edit_rules.audit_spec(four, profile=PROF), "Font")["status"] == "LỖI", "hồ sơ: 5 font → LỖI (> 3)")
    check(rule(off, "Chữ chính có phát sáng")["status"] == "CẢNH BÁO", "không hồ sơ: thiếu phát sáng → CẢNH BÁO")
    check(rule(on, "Chữ chính có phát sáng")["status"] == "OK", "hồ sơ: không phát sáng (P11) → OK", rule(on, "Chữ chính có phát sáng")["detail"])


if __name__ == "__main__":
    for fn in (test_cut_lead, test_text_cut, test_c1_profile, test_no_regression, test_sfx, test_silence_cut, test_p8_p11_font_glow):
        fn()
    print("TẤT CẢ ĐẠT" if not fails else f"{len(fails)} LỖI: {fails}")
    sys.exit(1 if fails else 0)
