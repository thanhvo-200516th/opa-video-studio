#!/usr/bin/env python3
"""Mẫu assets/motion-fx/build_spec_minimal.py (hồ sơ minimal-edu): chạy trên bản sao đầu vào KB08 với khối ví dụ ở đầu file mẫu
→ số track / clip trong ±10 % của kb08.craft.json dựng tay, spec_lint 0 HARD, edit_rules audit 0 LỖI; thiếu profile → dừng rõ ràng.
Chạy: ~/.venvs/video-skills/bin/python tests/test_build_spec_minimal.py"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_profile  # noqa: E402
from edit_rules import audit_spec  # noqa: E402
from spec_lint import lint  # noqa: E402

TEMPLATE = ROOT / "assets/motion-fx/build_spec_minimal.py"
DEMO = Path("/home/vmiz/Thanh/Media/A huy/Kich_ban/30 VID/Danh_Sach_Kich_Ban_6-10/"
            "18_KB08_AI_Lam_Video_Bat_Dong_San_Tu_Khoanh_Vung_Ban_Do_Google_/v_minimal105/work")
INPUTS = ("kb08.base.craft.json", "words_tl.json", "profile.json", "pain.json")
EDIT_RE = re.compile(r"(# -{20,} CHỈ SỬA[^\n]*\n)(.*?)(# -{20,} hết phần sửa\n)", re.S)
EXAMPLE_RE = re.compile(r"# --- VÍ DỤ KB08[^\n]*\n(.*?)# --- hết ví dụ ---", re.S)


def example_text() -> str:
    """Khối ví dụ KB08 ở đầu file mẫu, bỏ "# " đầu dòng."""
    src = TEMPLATE.read_text(encoding="utf-8")
    return "".join(re.sub(r"^# ?", "", ln, count=1) + "\n" for ln in EXAMPLE_RE.search(src).group(1).splitlines())


def kb08_template() -> str:
    """Mẫu với khối `# EDIT` thay bằng khối ví dụ KB08 (bỏ "# " đầu dòng)."""
    src = TEMPLATE.read_text(encoding="utf-8")
    return EDIT_RE.sub(lambda m: m.group(1) + example_text() + m.group(3), src, count=1)


def counts(spec: dict) -> tuple[int, int]:
    return len(spec["tracks"]), sum(len(t["clips"]) for t in spec["tracks"])


def workdir(name: str) -> Path:
    w = Path(tempfile.mkdtemp(prefix="build_minimal_")) / name / "work"
    w.mkdir(parents=True)
    return w


def run(w: Path) -> subprocess.CompletedProcess:
    env = {**os.environ, "OPA_SKILL_DIR": str(ROOT)}
    return subprocess.run([sys.executable, str(w / "build_spec_minimal.py")], capture_output=True, text=True, env=env, timeout=900)


def test_template_on_kb08() -> None:
    w = workdir("v1")
    for f in INPUTS:
        shutil.copy(DEMO / f, w / f)
    (w / "build_spec_minimal.py").write_text(kb08_template(), encoding="utf-8")
    r = run(w)
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-2500:]
    spec = json.loads((w / "kb08.craft.json").read_text(encoding="utf-8"))
    ref = json.loads((DEMO / "kb08.craft.json").read_text(encoding="utf-8"))
    (tn, tc), (rn, rc) = counts(spec), counts(ref)
    assert abs(tn - rn) <= max(1, 0.1 * rn) and abs(tc - rc) <= 0.1 * rc, f"tracks {tn} vs {rn}, clips {tc} vs {rc}"
    words = json.loads((w / "words_tl.json").read_text(encoding="utf-8"))
    hard = [x for x in lint(w / "kb08.craft.json", words) if x["status"] == "HARD"]
    assert not hard, hard
    prof = style_profile.load(w / "kb08.craft.json")
    res = audit_spec(spec, words, ["bãi đất trống", "quên ngay"], profile=prof)
    bad = [x for x in res if x["status"] == "LỖI"]
    assert not bad, bad
    warn = [x for x in res if x["status"] == "CẢNH BÁO" and x["rule"].startswith(("Chữ có chuyển động", "Nhiều B-roll"))]
    assert not warn, warn                                      # chữ ngắn không đứng yên lúc giữ; đoạn nói liền ≤ 8 s nhờ cutaway
    check_cutaway(spec, words)
    print(f"ok  KB08: {tn} track / {tc} clip (dựng tay {rn} / {rc}), 0 HARD, 0 LỖI, 0 cảnh báo chữ tĩnh / nói liền")


def check_cutaway(spec: dict, words: list) -> None:
    """("cutaway", "khoanh", 7, 2.4): clip câm của B-roll cảnh 7 (bản đồ vệ tinh) trên lane trên V1, bắt đầu ở «khoanh» (44,5 s), có chuyển cảnh vào + ra,
    giấy B-roll phủ; chữ trong lúc đó dùng vùng chữ B-roll."""
    cut = next(c for t in spec["tracks"] if t["name"].startswith("gfx_under") for c in t["clips"] if "cutaway" in c["name"])
    t_word = next(w[1] for w in words if w[0] == "khoanh" and w[1] > 40)
    assert Path(cut["src"]).name == "07_b-roll-5.mp4" and cut["audio"] is False, cut
    assert abs(cut["at"] - (t_word - 0.3)) < 0.05 and abs(cut["dur"] - 2.4) < 0.05, (cut["at"], cut["dur"])   # vào trước lời 0,3 s
    assert cut["transition_in"]["frames"] >= 12 and cut["transition_out"]["frames"] >= 12, cut
    assert any(e["effect"] == "vignette" for e in cut["effects"])
    paper = [c for t in spec["tracks"] if t["name"].startswith("card") for c in t["clips"]
             if c["name"].startswith("Giấy B-roll") and abs(c["at"] - cut["at"]) < 1e-3]
    assert paper, "thiếu giấy B-roll phủ cutaway"
    v1 = spec["tracks"][0]
    assert v1["name"].startswith("V1") and not any("cutaway" in c["name"] for c in v1["clips"])   # V1 / giọng chạy tiếp


def test_requires_minimal_profile() -> None:
    w = workdir("v2")
    for f in INPUTS:
        shutil.copy(DEMO / f, w / f)
    (w / "profile.json").write_text("{}", encoding="utf-8")
    (w / "build_spec_minimal.py").write_text(kb08_template(), encoding="utf-8")
    r = run(w)
    assert r.returncode != 0 and "minimal-edu" in (r.stdout + r.stderr), r.stderr[-800:]
    assert not (w / "kb08.craft.json").exists()
    print("ok  thiếu hồ sơ minimal-edu → dừng, nói rõ lý do")


def test_empty_groups_stops() -> None:
    w = workdir("v3")
    for f in INPUTS:
        shutil.copy(DEMO / f, w / f)
    shutil.copy(TEMPLATE, w / "build_spec_minimal.py")
    r = run(w)
    assert r.returncode != 0 and "GROUPS" in (r.stdout + r.stderr), r.stderr[-800:]
    print("ok  GROUPS trống → dừng, nói rõ lý do")


def edit_block(src: str, fn) -> str:
    """Sửa khối # EDIT đã thay bằng ví dụ KB08 (không đụng ví dụ chú thích trong docstring)."""
    m = EDIT_RE.search(src)
    return src[:m.start(2)] + fn(m.group(2)) + src[m.end(2):]


def placeholder_images(w: Path) -> None:
    from PIL import Image, ImageDraw
    for name, size in (("tranh.png", (1000, 1400)), ("minh_hoa.png", (900, 1100)), ("hinh_ben.png", (900, 1200))):
        im = Image.new("RGB", size, (255, 255, 255) if name != "tranh.png" else (40, 30, 24))
        d = ImageDraw.Draw(im)
        d.ellipse([size[0] * .25, size[1] * .3, size[0] * .75, size[1] * .6], fill=(30, 70, 200) if name != "tranh.png" else (190, 150, 110))
        d.rectangle([size[0] * .3, size[1] * .55, size[0] * .7, size[1]], fill=(30, 70, 200))
        im.save(w / name)


NEW_GFX = """SCENE_GFX = [("polaroid", 7, 1.6), ("arrow", "vẽ", 8), ("graph", "biểu", 9, ["vốn", "dòng", "bung", "con"]),
             ("quote_paper", 11, ["Độ tin cậy tăng lên", "gấp mười lần", "so với video cắt ghép"], 1, "white"),
             ("cutaway", "khoanh", 7, 2.4),
             ("painting", 4, "tranh.png", 2.5), ("illus_mid", 3, "minh_hoa.png"), ("illus_side", 5, "hinh_ben.png", "left"),
             ("path_text", 6, ["áp dụng | *hệ thống", "vào làm | *video", "diễn ra | rất | ~mạch lạc"]),
             ("path_illus", 10, "minh_hoa.png", "zigzag")]
"""
SCENE6 = '    "Cách mình | áp dụng | *hệ thống", "vào làm | *video | bất động sản", "diễn ra | rất | ~mạch lạc",\n'


def test_new_scene_kinds() -> None:
    """SCENE_GFX có đủ 6 kiểu cảnh mới (ảnh giả PIL): dựng không lỗi, spec_lint 0 HARD, edit_rules 0 LỖI; cảnh 6 do path_text tự dựng chữ (GROUPS None)."""
    w = workdir("v4")
    for f in INPUTS:
        shutil.copy(DEMO / f, w / f)
    placeholder_images(w)

    def fn(blk: str) -> str:
        assert SCENE6 in blk
        return re.sub(r"SCENE_GFX = \[.*?\]\n(?=CTA_WORD)", lambda _: NEW_GFX, blk.replace(SCENE6, "    None,\n"), flags=re.S)
    (w / "build_spec_minimal.py").write_text(edit_block(kb08_template(), fn), encoding="utf-8")
    r = run(w)
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-2500:]
    spec = json.loads((w / "kb08.craft.json").read_text(encoding="utf-8"))
    names = [c["name"] for t in spec["tracks"] for c in t["clips"]]
    for want in ("Tranh ·", "Texture tranh 1", "Minh hoạ giữa", "Hình bên", "Đường 1 (vẽ)", "Đường minh hoạ (vẽ)", "Nền giấy trích dẫn"):
        assert any(n.startswith(want) for n in names), want
    pic = next(c for t in spec["tracks"] for c in t["clips"] if c["name"].startswith("Tranh ·"))
    assert pic["motion"]["scale"][-1][1] == 112
    words = json.loads((w / "words_tl.json").read_text(encoding="utf-8"))
    hard = [x for x in lint(w / "kb08.craft.json", words) if x["status"] == "HARD"]
    assert not hard, hard
    prof = style_profile.load(w / "kb08.craft.json")
    bad = [x for x in audit_spec(spec, words, ["bãi đất trống", "quên ngay"], profile=prof) if x["status"] == "LỖI"]
    assert not bad, bad
    print(f"ok  6 kiểu cảnh mới trong mẫu: {counts(spec)[0]} track / {counts(spec)[1]} clip, 0 HARD, 0 LỖI")


def test_plan_json() -> None:
    """work/minimal_plan.json thay khối # EDIT: khối EDIT trống + plan = ví dụ KB08 → cùng số track / clip như chạy bằng khối ví dụ."""
    w = workdir("v5")
    for f in INPUTS:
        shutil.copy(DEMO / f, w / f)
    ns: dict = {}
    exec(example_text(), ns)
    plan = {"groups": ns["GROUPS"], "scene_gfx": [list(g) for g in ns["SCENE_GFX"]], "cta_word": ns["CTA_WORD"], "pain": ns["PAIN"]}
    (w / "minimal_plan.json").write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    shutil.copy(TEMPLATE, w / "build_spec_minimal.py")          # khối EDIT trống: GROUPS / SCENE_GFX / CTA_WORD / PAIN đều từ plan
    r = run(w)
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-2500:]
    spec = json.loads((w / "kb08.craft.json").read_text(encoding="utf-8"))
    ref = json.loads((DEMO / "kb08.craft.json").read_text(encoding="utf-8"))
    (tn, tc), (rn, rc) = counts(spec), counts(ref)
    assert abs(tn - rn) <= max(1, 0.1 * rn) and abs(tc - rc) <= 0.1 * rc, f"tracks {tn} vs {rn}, clips {tc} vs {rc}"
    print(f"ok  minimal_plan.json thay khối EDIT: {tn} track / {tc} clip")


if __name__ == "__main__":
    if not DEMO.is_dir():
        print(f"bỏ qua: không có đầu vào KB08 ở {DEMO}")
        sys.exit(0)
    for n in [n for n in sorted(globals()) if n.startswith("test_")]:
        globals()[n]()
    print("TẤT CẢ ĐẠT")
