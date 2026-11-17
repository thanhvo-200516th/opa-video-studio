#!/usr/bin/env python3
"""Kiểm flow_3d_assets.py (plan, lint-plan, extract-alpha, sheet) và MotionFX.asset_3d + spec_lint.
Chạy: ~/.venvs/video-skills/bin/python -B tests/test_flow_3d_assets.py"""
from __future__ import annotations

import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import flow_3d_assets as f3d  # noqa: E402
from motion_fx import MotionFX  # noqa: E402
from spec_lint import lint as spec_lint  # noqa: E402

KB11_MANIFEST = Path(
    "/home/vmiz/Thanh/Media/A huy/Kich_ban/30 VID/Danh_Sach_Kich_Ban_11-15/"
    "21_KB11_Bang_Xep_Hang_Tier_List_S_A_B_C_Ung_Dung_AI_Thuc_Te_Nha/00_storyboard_manifest.json"
)
KB11_SPEED_PLAN = KB11_MANIFEST.parent / "v3" / "media" / "speed_plan.json"


def run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / "flow_3d_assets.py"), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _png_chunks(path: Path) -> list[bytes]:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos = 8
    chunks: list[bytes] = []
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        chunks.append(ctype)
        pos += 12 + length
    return chunks


def test_plan_and_lint_real_manifest() -> None:
    assert KB11_MANIFEST.is_file(), f"Thiếu manifest mẫu: {KB11_MANIFEST}"
    with tempfile.TemporaryDirectory() as td:
        out_dir = Path(td) / "3d_out"
        cmd = [
            "plan",
            "--manifest", str(KB11_MANIFEST),
            "--max-assets", "6",
            "--mode", "mixed",
            "--out-dir", str(out_dir),
        ]
        if KB11_SPEED_PLAN.is_file():
            cmd += ["--speed-plan", str(KB11_SPEED_PLAN)]
        res = run_cli(cmd)
        assert res.returncode == 0, f"plan thất bại:\n{res.stdout}\n{res.stderr}"

        plan_json = out_dir / "3d_assets_plan.json"
        plan_md = out_dir / "3d_assets_plan.md"
        assert plan_json.is_file() and plan_md.is_file()

        plan = json.loads(plan_json.read_text(encoding="utf-8"))
        assets = plan["assets"]
        assert 1 <= len(assets) <= 6
        assert any(a["mode"] == "image_alpha" for a in assets)
        assert any(a["mode"] == "video_3d" for a in assets)
        for a in assets:
            assert a["placement"] in f3d.VALID_PLACEMENTS
            assert a["at"] >= 0 and a["dur"] > 0
            assert a["anchor_quote"].strip() != ""
            assert a["concept_object"].strip() != ""

        # lint-plan phải PASS trên plan vừa tạo
        res_lint = run_cli(["lint-plan", str(plan_json)])
        assert res_lint.returncode == 0, f"lint-plan FAIL:\n{res_lint.stdout}\n{res_lint.stderr}"
        assert "[3D LINT OK]" in res_lint.stdout

        # lint-plan phải FAIL khi có Anti-Slop hoặc sai anchor_quote
        bad_plan = json.loads(json.dumps(plan))
        bad_plan["assets"][0]["prompt"] = "A (stunning:1.3) 8k masterpiece 3D cube with no text."
        bad_plan["assets"][0]["anchor_quote"] = "câu bịa không có trong kịch bản"
        bad_path = out_dir / "bad_plan.json"
        bad_path.write_text(json.dumps(bad_plan, ensure_ascii=False, indent=2), encoding="utf-8")
        res_bad = run_cli(["lint-plan", str(bad_path)])
        assert res_bad.returncode != 0, "lint-plan phải thoát khác 0 khi prompt/anchor lỗi"
        assert "[3D LINT FAIL]" in res_bad.stdout


def test_extract_alpha_green_and_white() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        # 1) Green-screen RGBA (400x400) có object xám-trắng + xanh dương ở giữa và metadata EXIF/tEXt
        raw_green = tmp / "raw_green.png"
        im_g = Image.new("RGBA", (400, 400), (0, 255, 0, 255))
        draw_g = ImageDraw.Draw(im_g)
        draw_g.ellipse((110, 110, 290, 290), fill=(235, 235, 235, 255))
        draw_g.rectangle((165, 165, 235, 235), fill=(70, 130, 220, 255))
        # Mô phỏng viền anti-aliased pha xanh lá
        draw_g.ellipse((109, 109, 291, 291), outline=(120, 245, 120, 255), width=2)
        meta = PngImagePlugin.PngInfo()
        meta.add_text("Software", "Google Flow Secret Generator")
        meta.add_text("Prompt", "secret prompt metadata")
        im_g.save(raw_green, format="PNG", pnginfo=meta)

        out_green = tmp / "out_green.png"
        res_g = run_cli(["extract-alpha", str(raw_green), str(out_green), "--bg", "auto", "--pad", "16", "--max-size", "720"])
        assert res_g.returncode == 0, f"extract-alpha green lỗi:\n{res_g.stdout}\n{res_g.stderr}"
        assert out_green.is_file()

        with Image.open(out_green) as og:
            assert og.mode == "RGBA"
            assert not og.info, f"PNG vẫn còn info/metadata: {og.info}"
            arr = np.array(og)
        # Viền ảnh phải trong suốt hoàn toàn (alpha == 0)
        assert int(arr[0, :, 3].max()) == 0 and int(arr[-1, :, 3].max()) == 0
        assert int(arr[:, 0, 3].max()) == 0 and int(arr[:, -1, 3].max()) == 0
        # Tâm vật thể phải đặc (alpha == 255)
        cy, cx = arr.shape[0] // 2, arr.shape[1] // 2
        assert int(arr[cy, cx, 3]) == 255
        # Zero green spill: với vật thể trắng/xám/xanh dương, không có pixel nào G > max(R, B)
        vis = arr[arr[..., 3] > 0]
        assert int((vis[:, 1].astype(int) - np.maximum(vis[:, 0], vis[:, 2]).astype(int)).max()) <= 0
        # Không còn chunk metadata PNG
        chunks = _png_chunks(out_green)
        assert not any(c in chunks for c in (b"tEXt", b"iTXt", b"zTXt", b"eXIf")), chunks

        # 2) White-screen RGBA (400x400) với vùng sáng trắng kín nằm bên trong vật thể tối
        raw_white = tmp / "raw_white.png"
        im_w = Image.new("RGBA", (400, 400), (255, 255, 255, 255))
        draw_w = ImageDraw.Draw(im_w)
        draw_w.rounded_rectangle((100, 100, 300, 300), radius=24, fill=(40, 50, 70, 255))
        draw_w.ellipse((170, 170, 230, 230), fill=(252, 252, 252, 255))  # highlight trắng bên trong vật thể
        im_w.save(raw_white, format="PNG")

        out_white = tmp / "out_white.png"
        res_w = run_cli(["extract-alpha", str(raw_white), str(out_white), "--bg", "auto", "--pad", "16"])
        assert res_w.returncode == 0, f"extract-alpha white lỗi:\n{res_w.stdout}\n{res_w.stderr}"
        with Image.open(out_white) as ow:
            assert ow.mode == "RGBA"
            arr_w = np.array(ow)
        assert int(arr_w[0, 0, 3]) == 0 and int(arr_w[-1, -1, 3]) == 0
        # Highlight trắng nằm bên trong vật thể phải được flood-fill bảo vệ -> alpha == 255
        wcy, wcx = arr_w.shape[0] // 2, arr_w.shape[1] // 2
        assert int(arr_w[wcy, wcx, 3]) == 255


def test_sheet_generates_checkerboard_jpeg() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        res_plan = run_cli([
            "plan", "--manifest", str(KB11_MANIFEST), "--max-assets", "3", "--mode", "image_alpha", "--out-dir", str(tmp),
        ])
        assert res_plan.returncode == 0, res_plan.stderr
        plan_path = tmp / "3d_assets_plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))

        # Tạo 3 file RGBA giả khớp tên alpha_file trong plan
        colors = [(230, 180, 50, 255), (80, 200, 240, 255), (220, 90, 80, 255)]
        for a, col in zip(plan["assets"], colors):
            im = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
            ImageDraw.Draw(im).ellipse((40, 40, 200, 200), fill=col)
            im.save(tmp / a["alpha_file"], format="PNG", pnginfo=None)

        sheet_path = tmp / "3d_assets_sheet.jpg"
        res_sheet = run_cli(["sheet", str(plan_path), "--out", str(sheet_path)])
        assert res_sheet.returncode == 0, f"sheet thất bại:\n{res_sheet.stdout}\n{res_sheet.stderr}"
        assert sheet_path.is_file() and sheet_path.stat().st_size > 2000
        with Image.open(sheet_path) as sim:
            assert sim.format == "JPEG"
            assert sim.width >= 340 and sim.height >= 400


def test_motion_fx_asset_3d_and_spec_lint() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        v = tmp / "v1.mp4"
        a = tmp / "sfx.wav"
        png = tmp / "prop.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=black:s=1080x1920:d=5", "-r", "30", str(v)], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=880:d=0.4", str(a)], check=True)
        Image.new("RGBA", (256, 256), (255, 200, 40, 255)).save(png, format="PNG")

        fx = MotionFX(gfx_dir=tmp / "gfx", fps=30, name="test_3d")
        c_float = fx.asset_3d(str(png), at=0.5, dur=1.8, pos=(760, 560), scale=38.0, anim="float", cue="pop")
        c_spin = fx.asset_3d(str(png), at=2.6, dur=1.6, pos=(540, 820), scale=46.0, anim="spin3d", cue="pop")

        assert any(ln == "gfx_over" and cl is c_float for ln, cl in fx.items)
        assert any(ln == "gfx_over" and cl is c_spin for ln, cl in fx.items)
        # B14: không tĩnh — có keyframe chuyển động scale/position/opacity và spin3d có rotate_3d
        assert isinstance(c_float["motion"]["scale"], list) and len(c_float["motion"]["scale"]) >= 3
        assert isinstance(c_float["motion"]["position"], list) and len(c_float["motion"]["position"]) >= 3
        assert isinstance(c_float["opacity"], list) and len(c_float["opacity"]) >= 3
        assert any(e["effect"] == "rotate_3d" for e in c_spin.get("effects", []))
        assert len([q for q in fx.cues if q["kind"] == "pop"]) == 2

        spec = {
            "name": "TEST_3D",
            "width": 1080,
            "height": 1920,
            "fps": 30,
            "duration": 5.0,
            "tracks": [
                {"type": "video", "name": "V1 chính", "clips": [{"src": str(v), "at": 0.0, "in": 0.0, "dur": 5.0}]},
                *fx.tracks("FX · "),
                {"type": "audio", "name": "A1 Giọng", "clips": [{"src": str(v), "at": 0.0, "in": 0.0, "dur": 5.0}]},
                {"type": "audio", "name": "A2 SFX (mở đầu)", "clips": [{"src": str(a), "at": 0.0, "in": 0.0, "dur": 0.35, "name": "SFX MỞ ĐẦU"}]},
            ],
        }
        spec_path = tmp / "test_3d.craft.json"
        spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
        lint_res = spec_lint(spec_path, words=[["Sau", 0.2, 0.4], ["một", 0.45, 0.7], ["năm", 0.8, 1.1]])
        hard = [r for r in lint_res if r["status"] == "HARD"]
        assert not hard, f"spec_lint có lỗi HARD: {hard}"


def main() -> None:
    test_plan_and_lint_real_manifest()
    print("[OK] plan + lint-plan trên 21_KB11 manifest (cả PASS và chặn Anti-Slop/anchor sai)")
    test_extract_alpha_green_and_white()
    print("[OK] extract-alpha (nền xanh lá + nền trắng, RGBA, viền alpha=0, tâm alpha=255, zero green spill, sạch metadata)")
    test_sheet_generates_checkerboard_jpeg()
    print("[OK] sheet tạo 3d_assets_sheet.jpg nền caro hợp lệ")
    test_motion_fx_asset_3d_and_spec_lint()
    print("[OK] MotionFX.asset_3d trên gfx_over (B14 motion + spin3d + cue pop) & spec_lint 0 HARD")
    print("\nTẤT CẢ ĐẠT")


if __name__ == "__main__":
    main()
