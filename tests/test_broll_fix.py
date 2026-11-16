#!/usr/bin/env python3
"""Kiểm broll_fix.py (lint H5 / prepare / verify / ready) và các chỗ vá của render_muse_broll.py. Offline: clip giả bằng ffmpeg lavfi.
Chạy: ~/.venvs/video-skills/bin/python tests/test_broll_fix.py"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import broll_fix as bf  # noqa: E402
import media_reuse as mr  # noqa: E402
import render_muse_broll as rmb  # noqa: E402

TTS3 = "Anh em nhìn cách bọn mình vận hành. Minh và khối kỹ thuật tập trung tối đa vào việc rèn giũa sản phẩm sao cho sắc bén nhất."
ANCHOR3 = "Minh và khối kỹ thuật tập trung tối đa vào việc rèn giũa sản phẩm"
GOOD3 = ("Slow push-in on a young Vietnamese engineering team in a bright modern office, three colleagues shoulder to shoulder at monitors, "
         "intensely focused on sharpening a product, the monitors blurred and out of focus in the foreground. Warm daylight, shallow depth of field.")


def ff(args: list[str]) -> None:
    subprocess.run(["ffmpeg", "-y", "-v", "error", *args], check=True)


def make_clip(path: Path, src: str, secs: float, size: str = "1080x1920", fps: int = 30, audio: bool = False) -> None:
    cmd = ["-f", "lavfi", "-i", f"{src}=size={size}:rate={fps}"]
    if audio:
        cmd += ["-f", "lavfi", "-i", "sine=frequency=440"]
    ff([*cmd, "-t", str(secs), "-pix_fmt", "yuv420p", *(["-c:a", "aac"] if audio else ["-an"]), str(path)])


def make_voice(path: Path, secs: float) -> None:
    ff(["-f", "lavfi", "-i", "sine=frequency=300", "-t", str(secs), str(path)])


def build_folder(root: Path) -> Path:
    f = root / "09_TEST09_Demo"
    (f / "media" / "x110").mkdir(parents=True)
    segs = []
    for i, (role, vlen) in enumerate([(2, 3.0), (10, 2.5)], start=3):
        stem = f"{i:02d}_b-roll-{role}"
        make_clip(f / f"{stem}.mp4", "testsrc", 3)
        make_clip(f / "media" / "x110" / f"{stem}_x110.mp4", "testsrc", 3)
        make_voice(f / f"{i:02d}_voice-b-roll-{role}.mp3", vlen)
        segs.append({"seq_index": i, "seq_prefix": f"{i:02d}", "type": "b-roll", "role_id": f"b-roll-{role}", "tts_text": TTS3,
                     "duration_sec": 3.0, "visual_direction": "Clip thư viện: KB07_B02_Kho.mp4",
                     "broll_prompt": "Clip thư viện: KB07_B02_Kho.mp4 (Pure visual footage/motion only, NO text)",
                     "files": {"video_file": f"{stem}.mp4", "voice_file": f"{i:02d}_voice-b-roll-{role}.mp3"}})
    (f / "00_storyboard_manifest.json").write_text(json.dumps({"script_id": "TEST09", "segments": segs}, ensure_ascii=False), encoding="utf-8")
    items = [{"seq_index": s["seq_index"], "role_id": s["role_id"], "output_file": s["files"]["video_file"],
              "paired_voice_file": s["files"]["voice_file"], "duration_target_sec": 3.0, "prompt_vi": s["visual_direction"],
              "prompt_full": s["broll_prompt"], "rules": {"aspect_ratio": "9:16"}} for s in segs]
    (f / "prompts_muse_veo_broll.json").write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    (f / "00_BANG_PHAN_CANH.md").write_text("| 03 | Clip thư viện: KB07_B02_Kho.mp4 |\n", encoding="utf-8")
    return f


def main() -> None:
    # --- lint H5
    assert bf.lint_prompt(GOOD3, TTS3, ANCHOR3) == [], bf.lint_prompt(GOOD3, TTS3, ANCHOR3)
    bad = {
        "Clip thư viện: KB07_B02_Kho.mp4": "thư viện",
        "Cảnh một nhóm kỹ sư làm việc trong văn phòng sáng sủa hiện đại với ánh sáng ấm": "dấu",
        "A founder walks": "chữ",
        GOOD3 + " A neon sign and a logo glow on the wall.": "cấm",
        "Colleagues work at laptops in a bright modern office with warm daylight and shallow depth of field": "màn hình",
        "A woman writing on paper at a bright desk in a modern office with warm daylight and soft focus.": "cấm",
    }
    for text, why in bad.items():
        assert bf.lint_prompt(text), (why, text)
    assert bf.lint_prompt("A Vietnamese designer in a bright modern office reviews a product box with warm daylight, shallow focus.") == []
    # v3.1 (Flow 2026-11-14): "angled away" không đủ — Flow vẫn vẽ logo; người nói / founder không lộ mặt; bảng trắng / giấy phải mờ
    flow_bad = {
        "Three engineers at monitors in a bright office, screens angled away with a soft glow, warm daylight, shallow focus.": "màn hình",
        "A founder in a dark polo talks calmly with a client across a wooden table in a bright modern office.": "người nói",
        "A team brainstorms around a whiteboard in a bright modern office, warm daylight, handheld camera, shallow focus.": "màn hình",
        "A failed project desk transitions from chaos to two men shaking hands in a bright modern office, warm light.": "một cảnh",
        "A busy kitchen crew plates dishes, picture-in-picture of the host in the corner, warm light, slow push-in.": "một cảnh",
        "A tired young woman rubs her eyes at a cluttered desk late at night, warm lamp light, slow push-in.": "Vietnamese",
    }
    for text, why in flow_bad.items():
        assert any(why in p for p in bf.lint_prompt(text)), (why, bf.lint_prompt(text))
    assert bf.lint_prompt("A Vietnamese founder seen from behind, over the shoulder, listens to a client across a wooden table in a bright office.") == []
    assert bf.lint_prompt(GOOD3, TTS3, "một câu không có trong lời cảnh") and bf.lint_prompt(GOOD3, TTS3, None)
    assert bf.lint_prompt(GOOD3, TTS3, "minh và KHỐI kỹ thuật, tập trung tối đa") == []      # chuẩn hoá hoa/thường/dấu câu
    assert bf.core_of(f"{GOOD3} ({rmb.BROLL_STRICT_SUFFIX_EN})") == GOOD3
    assert [bf.request_seconds(v) for v in (7.31, 9.74, 5.67, 1.0)] == [8, 10, 6, 2]
    assert [bf.flow_seconds(v) for v in (7.31, 9.74, 5.67, 18.02, 1.0)] == [8, 11, 6, 15, 3]
    assert bf.flow_credits(8, 2) == 48 and bf.flow_credits(10, 1) == 30          # 720p 3 tín dụng/s, nâng 1080p miễn phí ≤ 10 s
    assert bf.flow_credits(15, 2) == 2 * 60 + 5                                    # 11–15 s: 6 tín dụng/s, nâng 1080p 1 tín dụng/s
    print("ok  lint H5 + request_seconds + flow_seconds / flow_credits")

    # --- render_muse_broll vá
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        f = build_folder(root)
        jobs = rmb.collect_broll_jobs([f], shot_filter="b-roll-2", force=True)
        assert [j[1]["output_file"] for j in jobs] == ["03_b-roll-2.mp4"], jobs        # không dính b-roll-20 / b-roll-10
        jobs = rmb.collect_broll_jobs([f], shot_filter="04_b-roll-10.mp4", force=True)
        assert [j[1]["output_file"] for j in jobs] == ["04_b-roll-10.mp4"]
        assert len(rmb.collect_broll_jobs([f], shot_filter="b-roll-1", force=True)) == 0
        assert rmb.job_seconds(f, jobs[0][1]) == 3, rmb.job_seconds(f, jobs[0][1])      # tiếng 2.5 s + 0.3 → 3
        print("ok  --shot khớp chính xác; giây theo tiếng")

        # prompt tiếng Việt / thư viện bị từ chối trước khi gọi API
        assert rmb.h5_problems(jobs)
        # --- ready: bị chặn → mã 1, không in khoá
        env = {**os.environ, "MUSE_BASE_URL": "http://127.0.0.1:9/v1", "MUSE_API_KEY": "khoa-gia-123"}
        r = subprocess.run([sys.executable, str(SCRIPTS / "broll_fix.py"), "ready"], env=env, capture_output=True, text=True)
        assert r.returncode == 1 and "D3" in r.stdout and "khoa-gia-123" not in r.stdout + r.stderr, r.stdout + r.stderr
        r = subprocess.run([sys.executable, str(SCRIPTS / "render_muse_broll.py"), str(f), "--shot", "03_b-roll-2.mp4", "--force"],
                           env=env, capture_output=True, text=True)
        assert r.returncode == 1 and "H5" in r.stdout, r.stdout + r.stderr        # prompt thư viện bị từ chối trước cả /readyz
        print("ok  ready → D3, render từ chối prompt sai H5")

        # --- prepare
        newp = root / "broll_new_prompts.json"
        newp.write_text(json.dumps([{"seq": 3, "prompt": GOOD3, "anchor_quote": ANCHOR3}], ensure_ascii=False), encoding="utf-8")
        backup_root = root / "backup"
        cli = [sys.executable, str(SCRIPTS / "broll_fix.py")]
        r = subprocess.run([*cli, "lint", str(f), "--prompts", str(newp)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout
        before = (f / "00_storyboard_manifest.json").read_text(encoding="utf-8")
        r = subprocess.run([*cli, "prepare", str(f), "--prompts", str(newp), "--dry-run", "--backup-root", str(backup_root)], capture_output=True, text=True)
        assert r.returncode == 0 and (f / "03_b-roll-2.mp4").exists() and not backup_root.exists()
        assert (f / "00_storyboard_manifest.json").read_text(encoding="utf-8") == before
        badp = root / "bad.json"
        badp.write_text(json.dumps([{"seq": 3, "prompt": "Clip thư viện: KB07", "anchor_quote": ANCHOR3}], ensure_ascii=False), encoding="utf-8")
        r = subprocess.run([*cli, "prepare", str(f), "--prompts", str(badp), "--backup-root", str(backup_root)], capture_output=True, text=True)
        assert r.returncode == 1 and (f / "03_b-roll-2.mp4").exists() and not backup_root.exists()
        r = subprocess.run([*cli, "prepare", str(f), "--prompts", str(newp), "--backup-root", str(backup_root)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        assert not (f / "03_b-roll-2.mp4").exists() and not (f / "media/x110/03_b-roll-2_x110.mp4").exists()
        assert (f / "04_b-roll-10.mp4").exists()                                   # cảnh khác nguyên vẹn
        bk = next(backup_root.glob("*/09_TEST09_Demo"))
        assert (bk / "03_b-roll-2.mp4").exists() and (bk / "media/x110/03_b-roll-2_x110.mp4").exists()
        assert (bk / "00_storyboard_manifest.json").read_text(encoding="utf-8") == before and (bk / "prompts_muse_veo_broll.json").exists()
        items = json.loads((f / "prompts_muse_veo_broll.json").read_text(encoding="utf-8"))
        i3, i4 = items
        assert i3["prompt_full"] == f"{GOOD3} ({rmb.BROLL_STRICT_SUFFIX_EN})" and "prompt_vi" not in i3
        assert i3["duration_target_sec"] == 4 and i3["source"] == "muse" and i3["anchor_quote"] == ANCHOR3
        assert i3["regen_of"].startswith("Clip thư viện") and i3["backup"] == str(bk)
        assert i4["prompt_vi"].startswith("Clip thư viện")                         # cảnh khác không đụng
        man = json.loads((f / "00_storyboard_manifest.json").read_text(encoding="utf-8"))["segments"]
        assert man[0]["broll_prompt"] == i3["prompt_full"] and man[0]["visual_direction"] == GOOD3 and man[0]["broll_source"] == "muse"
        assert man[0]["regen_history"][0]["old_prompt"].startswith("Clip thư viện") and "broll_source" not in man[1]
        assert GOOD3 in (f / "00_BANG_PHAN_CANH.md").read_text(encoding="utf-8")
        assert not rmb.h5_problems([(f, i3)]) and rmb.h5_problems([(f, i4)])
        print("ok  prepare: dry-run / lint chặn / sao lưu / viết lại prompts + manifest")

        # --- prepare --source flow: ghi đúng nguồn, giây theo mức Flow
        newp4 = root / "p4.json"
        newp4.write_text(json.dumps([{"seq": 4, "prompt": GOOD3, "anchor_quote": ANCHOR3}], ensure_ascii=False), encoding="utf-8")
        r = subprocess.run([*cli, "prepare", str(f), "--prompts", str(newp4), "--source", "flow", "--backup-root", str(backup_root)],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        i4 = json.loads((f / "prompts_muse_veo_broll.json").read_text(encoding="utf-8"))[1]
        m4 = json.loads((f / "00_storyboard_manifest.json").read_text(encoding="utf-8"))["segments"][1]
        assert i4["source"] == "flow" and m4["broll_source"] == "flow" and i4["duration_target_sec"] == 3, (i4, m4)
        assert i4["prompt_full"] == GOOD3                                           # Flow: gõ lõi prompt, không nối đuôi "NO text…"
        r = subprocess.run([*cli, "plan", str(f), "--engine", "flow"], capture_output=True, text=True)
        assert r.returncode == 0 and "Flow" in r.stdout and "tín dụng" in r.stdout, r.stdout + r.stderr
        # --- prepare --keep-clips: chỉ ghi prompt cuối vào manifest / prompts, clip đang dùng giữ nguyên
        make_clip(f / "04_b-roll-10.mp4", "testsrc", 3)
        GOOD4 = GOOD3.replace("Slow push-in", "Gentle handheld drift")
        newk = root / "pk.json"
        newk.write_text(json.dumps([{"seq": 4, "prompt": GOOD4, "anchor_quote": ANCHOR3}], ensure_ascii=False), encoding="utf-8")
        r = subprocess.run([*cli, "prepare", str(f), "--prompts", str(newk), "--source", "flow", "--keep-clips",
                            "--backup-root", str(backup_root)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        assert (f / "04_b-roll-10.mp4").exists(), "keep-clips đã chuyển clip đi"
        m4 = json.loads((f / "00_storyboard_manifest.json").read_text(encoding="utf-8"))["segments"][1]
        assert m4["visual_direction"] == GOOD4 and m4["broll_source"] == "flow", m4
        print("ok  prepare --source flow + plan --engine flow")

        # --- verify (lib giả để khỏi quét thư viện thật)
        lib = root / "lib"
        lib.mkdir()
        make_clip(lib / "KB01_B01_lib.mp4", "mandelbrot", 4)
        mr.LIB_DIRS[:] = [lib]
        out = root / "qa"
        make_clip(f / "03_b-roll-2.mp4", "rgbtestsrc", 4)
        good = bf.check_clip(f / "03_b-roll-2.mp4", 3.0, 1.10)
        assert [s for s, _ in good] == ["OK"] * 4, good
        assert any(s == "OK" and "3.64" in m for s, m in good), good                # 4.0/1.10 = 3.64
        make_clip(f / "03_b-roll-2.mp4", "rgbtestsrc", 2.9)
        assert bf.check_clip(f / "03_b-roll-2.mp4", 3.0, 1.10)[3][0] == "WARN"
        assert bf.check_clip(f / "03_b-roll-2.mp4", 3.4, 1.10)[3][0] == "FAIL"
        make_clip(f / "03_b-roll-2.mp4", "rgbtestsrc", 4, size="720x1280")
        assert bf.check_clip(f / "03_b-roll-2.mp4", 3.0, 1.10)[0][0] == "FAIL"
        make_clip(f / "03_b-roll-2.mp4", "rgbtestsrc", 4, fps=25)
        assert bf.check_clip(f / "03_b-roll-2.mp4", 3.0, 1.10)[1][0] == "FAIL"
        make_clip(f / "03_b-roll-2.mp4", "rgbtestsrc", 4, audio=True)
        assert bf.check_clip(f / "03_b-roll-2.mp4", 3.0, 1.10)[2][0] == "FAIL"
        print("ok  verify: kích thước / fps / tiếng / độ dài")

        make_clip(f / "03_b-roll-2.mp4", "rgbtestsrc", 4)
        mr.fingerprint.cache_clear()
        assert bf.cmd_verify(type("A", (), {"folder": str(f), "scenes": "3", "speed": 1.10, "out_dir": str(out)})()) == 0
        sheet = out / "broll_check_sheet.jpg"
        assert sheet.is_file() and sheet.stat().st_size > 2000
        from PIL import Image
        assert Image.open(sheet).size == (216 * 5, 384)
        # clip trùng clip thư viện (đã mã hoá lại) → FAIL
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(lib / "KB01_B01_lib.mp4"), "-vf", "scale=1080:1920,fps=30", "-an",
                        "-t", "4", str(f / "03_b-roll-2.mp4")], check=True)
        mr.fingerprint.cache_clear()
        assert bf.cmd_verify(type("A", (), {"folder": str(f), "scenes": "3", "speed": 1.10, "out_dir": str(out)})()) == 1
        print("ok  verify: contact sheet + trùng thư viện → FAIL")

    # v2.8 normalize: clip Google Flow 720×1280 có tiếng + dấu ngôi sao → 1080×1920, 30 fps, không tiếng, góc dấu bị xoá
    with tempfile.TemporaryDirectory() as td:
        raw, out = Path(td) / "raw.mp4", Path(td) / "03_b-roll-2.mp4"
        ff(["-f", "lavfi", "-i", "color=c=black:s=720x1280:r=24:d=2", "-f", "lavfi", "-i", "sine=f=440:d=2",
            "-vf", "drawbox=x=584:y=1144:w=40:h=40:color=white@1:t=fill", "-shortest", "-c:v", "libx264", "-c:a", "aac", str(raw)])
        assert bf.cmd_normalize(type("A", (), {"raw": str(raw), "out": str(out), "mark": "flow"})()) == 0
        streams = bf.probe(out).get("streams", [])
        v = next(x for x in streams if x["codec_type"] == "video")
        assert (v["width"], v["height"], v["avg_frame_rate"]) == (1080, 1920, "30/1") and not any(x["codec_type"] == "audio" for x in streams), streams
        import numpy as np
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "1", "-i", str(out), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                             capture_output=True).stdout
        fr = np.frombuffer(raw, np.uint8).reshape(1920, 1080)
        assert float(fr[1700:1780, 860:940].mean()) < 40, f"dấu Flow chưa bị xoá ({fr[1700:1780, 860:940].mean():.0f})"
        print("ok  normalize: 1080x1920 30 fps không tiếng, xoá dấu Flow")

    print("TẤT CẢ ĐẠT")


if __name__ == "__main__":
    main()
