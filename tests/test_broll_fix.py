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
    # 1.2.2–1.2.3 F2: bộ từ cấm sinh chữ/UI/số liệu giả/tên hãng & nền tảng
    f2_banned = [
        "note", "notes", "checklist", "checklists", "checkbox", "checkboxes", "written", "bullet", "bullets",
        "handwritten", "handwriting", "chatting", "message", "messages", "messaging", "texting",
        "side-by-side", "comparison", "graph", "graphs", "metrics", "analytics", "statistics", "engagement",
        "youtube", "tiktok", "facebook", "instagram", "iphone", "macbook", "apple", "samsung", "google",
    ]
    for w in f2_banned:
        p = f"A young Vietnamese creator looks at {w} on a bright wooden desk in a sunlit modern office."
        errs = bf.lint_prompt(p)
        assert any("chứa từ cấm" in e for e in errs), (w, errs)
    assert bf.lint_prompt(GOOD3, TTS3, "một câu không có trong lời cảnh") and bf.lint_prompt(GOOD3, TTS3, None)
    assert bf.lint_prompt(GOOD3, TTS3, "minh và KHỐI kỹ thuật, tập trung tối đa") == []      # chuẩn hoá hoa/thường/dấu câu
    assert bf.core_of(f"{GOOD3} ({rmb.BROLL_STRICT_SUFFIX_EN})") == GOOD3

    # v3.2: MAX_WORDS=95, Anti-Slop, Anti-Plastic-CGI, CLIP weights, Negative tail, strict_layers & 5 layers
    assert bf.MAX_WORDS == 95
    words_75 = (
        "Medium close-up of a young Vietnamese founder seen from behind at a clean wooden desk "
        "in a sunlit modern office, carefully sorting plain blank cardboard folders while unbranded "
        "monitors remain blurred and out of focus in the background, warm window light across linen "
        "sleeves and natural skin texture, shot on 35mm documentary lens with subtle film grain "
        "and shallow depth of field, slow push-in toward the hands "
        + " ".join(["calmly"] * 12)
        + "."
    )
    assert 61 <= len(words_75.split()) <= 95
    assert bf.lint_prompt(words_75, strict_layers=True) == [], bf.lint_prompt(words_75, strict_layers=True)
    words_96 = words_75 + " " + " ".join(["extra"] * (96 - len(words_75.split())))
    assert any("96 chữ" in e for e in bf.lint_prompt(words_96, strict_layers=True))

    anti_slop_samples = [
        "stunning", "breathtaking", "hyper-detailed", "hyperdetailed", "8k", "4k", "masterpiece",
        "magical", "very realistic", "ultra-realistic", "ultra realistic", "photorealistic",
        "award-winning", "best quality",
    ]
    for w in anti_slop_samples:
        p = f"Medium shot of a Vietnamese designer in a {w} wooden studio, window light, slow push-in."
        errs = bf.lint_prompt(p, strict_layers=True)
        assert any("Anti-Slop" in e for e in errs), (w, errs)

    plastic_ai_samples = [
        "3d render", "cgi", "unreal engine", "octanerender", "octane", "blender render",
        "glowing prism", "amber prism", "frosted-glass gears", "hologram", "holographic",
        "cyberpunk", "neon cyber", "futuristic glowing", "glowing nodes", "floating icons",
        "pipeline rail", "parallel steel tracks", "sci-fi", "plastic sheen", "porcelain skin",
        "rubbery", "energy core",
    ]
    for w in plastic_ai_samples:
        p = f"Medium shot of a Vietnamese engineer beside a {w} on a wooden desk, daylight, slow push-in."
        errs = bf.lint_prompt(p, strict_layers=True)
        assert any("CGI/nhựa" in e for e in errs), (w, errs)

    for bad_syn in (
        "Medium shot of a (Vietnamese:1.3) designer at a wooden desk, daylight, slow push-in.",
        "Medium shot of a Vietnamese designer at a wooden::2 desk, daylight, slow push-in.",
    ):
        errs = bf.lint_prompt(bad_syn, strict_layers=True)
        assert any("trọng số CLIP" in e for e in errs), (bad_syn, errs)

    for bad_neg in (
        "Medium shot of a Vietnamese designer at a wooden desk, daylight, slow push-in, no text.",
        "Medium shot of a Vietnamese designer at a wooden desk, daylight, slow push-in, no logos.",
        "Medium shot of a Vietnamese designer at a wooden desk, daylight, slow push-in, no watermarks.",
        "Medium shot of a Vietnamese designer at a wooden desk, daylight, slow push-in, no subtitles.",
    ):
        errs = bf.lint_prompt(bad_neg, strict_layers=True)
        assert any("phủ định" in e for e in errs), (bad_neg, errs)

    no_cam = "Medium shot of a Vietnamese designer at a wooden desk, warm window light, 35mm film grain."
    assert bf.lint_prompt(no_cam, strict_layers=False) == []
    assert any("chuyển động camera" in e for e in bf.lint_prompt(no_cam, strict_layers=True))

    no_realism = "Medium shot of a young Vietnamese designer standing in a quiet modern office, slow push-in."
    assert bf.lint_prompt(no_realism, strict_layers=False) == []
    assert any("quang học / chất liệu" in e for e in bf.lint_prompt(no_realism, strict_layers=True))

    good_layers = {
        "l1_shot_subject": "Over-the-shoulder medium shot of a young Vietnamese engineering team",
        "l2_action_script": "three colleagues working closely together to sharpen their product",
        "l3_environment": "in a bright modern office with monitors blurred and out of focus",
        "l4_optics_realism": "35mm documentary look, warm daylight, natural skin texture, shallow depth of field",
        "l5_camera_motion": "slow push-in",
    }
    assembled = bf.assemble_layered_prompt(good_layers)
    assert bf.lint_prompt(assembled, TTS3, ANCHOR3, strict_layers=True, layers=good_layers) == []
    bad_layers_missing = {**good_layers, "l4_optics_realism": "  "}
    assert any("layers thiếu hoặc rỗng" in e for e in bf.lint_prompt(assembled, strict_layers=True, layers=bad_layers_missing))
    bad_layers_vi = {**good_layers, "l2_action_script": "ba kỹ sư Việt đang tập trung"}
    assert any("layers có dấu tiếng Việt" in e for e in bf.lint_prompt(assembled, strict_layers=True, layers=bad_layers_vi))
    print("ok  v3.2 lint: MAX_WORDS=95, Anti-Slop, Plastic-CGI, CLIP weights, negative tail, strict_layers, 5 layers")
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
        r = subprocess.run([*cli, "prepare", str(f), "--prompts", str(newp), "--source", "muse", "--backup-root", str(backup_root)], capture_output=True, text=True)
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

        # --- prepare mặc định (--source flow) + plan mặc định (--engine flow)
        newp4 = root / "p4.json"
        newp4.write_text(json.dumps([{"seq": 4, "prompt": GOOD3, "anchor_quote": ANCHOR3}], ensure_ascii=False), encoding="utf-8")
        r = subprocess.run([*cli, "prepare", str(f), "--prompts", str(newp4), "--backup-root", str(backup_root)],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        i4 = json.loads((f / "prompts_muse_veo_broll.json").read_text(encoding="utf-8"))[1]
        m4 = json.loads((f / "00_storyboard_manifest.json").read_text(encoding="utf-8"))["segments"][1]
        assert i4["source"] == "flow" and m4["broll_source"] == "flow" and i4["duration_target_sec"] == 3, (i4, m4)
        assert i4["prompt_full"] == GOOD3                                           # Flow: gõ lõi prompt, không nối đuôi "NO text…"
        r = subprocess.run([*cli, "plan", str(f)], capture_output=True, text=True)
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
        # --- lint & prepare với 5 tầng `layers` (không cần ghi `prompt`) + `script_beat_vi` + `--no-strict-layers`
        beat = "Minh và khối kỹ thuật tập trung rèn giũa sản phẩm trong văn phòng sáng"
        layered_p = root / "layered.json"
        layered_p.write_text(json.dumps([{
            "seq": 4,
            "anchor_quote": ANCHOR3,
            "script_beat_vi": beat,
            "layers": good_layers,
        }], ensure_ascii=False), encoding="utf-8")
        r = subprocess.run([*cli, "lint", str(f), "--prompts", str(layered_p)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        r = subprocess.run([*cli, "prepare", str(f), "--prompts", str(layered_p), "--source", "flow", "--keep-clips",
                            "--backup-root", str(backup_root)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        i4 = json.loads((f / "prompts_muse_veo_broll.json").read_text(encoding="utf-8"))[1]
        m4 = json.loads((f / "00_storyboard_manifest.json").read_text(encoding="utf-8"))["segments"][1]
        assert i4["layers"] == good_layers and i4["script_beat_vi"] == beat, i4
        assert m4["broll_layers"] == good_layers and m4["script_beat_vi"] == beat, m4
        assert i4["prompt_core"] == assembled and m4["broll_prompt"] == assembled

        no_strict_p = root / "nostrict.json"
        no_strict_p.write_text(json.dumps([{
            "seq": 4,
            "anchor_quote": ANCHOR3,
            "prompt": "A Vietnamese founder seen from behind, over the shoulder, listens to a client across a table in an office.",
        }], ensure_ascii=False), encoding="utf-8")
        assert subprocess.run([*cli, "lint", str(f), "--prompts", str(no_strict_p)], capture_output=True, text=True).returncode == 1
        assert subprocess.run([*cli, "lint", str(f), "--prompts", str(no_strict_p), "--no-strict-layers"], capture_output=True, text=True).returncode == 0

        bad_beat_p = root / "bad_beat.json"
        bad_beat_p.write_text(json.dumps([{
            "seq": 4, "anchor_quote": ANCHOR3, "script_beat_vi": "   ", "layers": good_layers,
        }], ensure_ascii=False), encoding="utf-8")
        r = subprocess.run([*cli, "lint", str(f), "--prompts", str(bad_beat_p)], capture_output=True, text=True)
        assert r.returncode == 1 and "script_beat_vi" in r.stdout, r.stdout
        print("ok  prepare --source flow + plan --engine flow + layers/script_beat_vi/--no-strict-layers")

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
        prov = json.loads((Path(td) / "_broll_sources.json").read_text(encoding="utf-8"))
        assert prov["03_b-roll-2.mp4"]["source"] == "flow" and prov["03_b-roll-2.mp4"]["mark"] == "flow", prov
        print("ok  normalize: 1080x1920 30 fps không tiếng, xoá dấu Flow, ghi _broll_sources.json")

    # normalize provenance inference & manifest sync
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "_google_raw").mkdir()
        (d / "06_B-Roll").mkdir()
        (d / "04_footage").mkdir()
        man_p = d / "00_storyboard_manifest.json"
        man_p.write_text(json.dumps({"segments": [
            {"seq_index": 2, "type": "b-roll", "files": {"video_file": "02_b-roll-1.mp4"}},
            {"seq_index": 3, "type": "b-roll", "files": {"video_file": "03_b-roll-2.mp4"}},
            {"seq_index": 4, "type": "b-roll", "files": {"video_file": "04_b-roll-3.mp4"}},
        ]}, ensure_ascii=False), encoding="utf-8")
        r_flow = d / "_google_raw/shot1.mp4"
        r_stock = d / "06_B-Roll/ftg_desk.mp4"
        r_real = d / "04_footage/C0001_studio.mp4"
        for rp in (r_flow, r_stock, r_real):
            ff(["-f", "lavfi", "-i", "color=c=black:s=1080x1920:r=30:d=0.5", "-c:v", "libx264", str(rp)])
        assert bf.normalize(r_flow, d / "02_b-roll-1.mp4") == 0
        assert bf.normalize(r_stock, d / "03_b-roll-2.mp4") == 0
        assert subprocess.run([sys.executable, str(SCRIPTS / "broll_fix.py"), "normalize", str(r_real), str(d / "04_b-roll-3.mp4")],
                              capture_output=True, text=True).returncode == 0
        prov = json.loads((d / "_broll_sources.json").read_text(encoding="utf-8"))
        assert prov["02_b-roll-1.mp4"]["source"] == "flow"
        assert prov["03_b-roll-2.mp4"]["source"] == "stock"
        assert prov["04_b-roll-3.mp4"]["source"] == "real_footage"
        segs = json.loads(man_p.read_text(encoding="utf-8"))["segments"]
        assert [s["broll_source"] for s in segs] == ["flow", "stock", "real_footage"], segs
        print("ok  normalize: suy nguồn flow/stock/real_footage + cập nhật _broll_sources.json & manifest")

    # 1.2.2 F3 trim_uniform_borders: cắt viền trắng/đen/đồng màu >= 2 %, giữ nguyên < 2 % và nền chuyển êm
    import numpy as np
    from PIL import Image
    rng = np.random.default_rng(42)
    core_arr = rng.integers(30, 180, (400, 300, 3), dtype=np.uint8)
    # 1) Viền trắng 30 px (> 2 %) -> cắt gọn còn đúng 300x400
    bordered_white = np.full((460, 360, 3), 255, dtype=np.uint8)
    bordered_white[30:430, 30:330] = core_arr
    assert bf.trim_uniform_borders(Image.fromarray(bordered_white)).size == (300, 400)
    # 2) Viền đen + đồng màu (xám xanh) >= 2 % -> cắt gọn
    bordered_color = np.full((460, 360, 3), (60, 90, 120), dtype=np.uint8)
    bordered_color[30:430, 30:330] = rng.integers(180, 250, (400, 300, 3), dtype=np.uint8)
    assert bf.trim_uniform_borders(Image.fromarray(bordered_color)).size == (300, 400)
    # 3) Viền mỏng < 2 % (10 px trên 1080x1920 = 0.9 % / 0.5 %) -> giữ nguyên an toàn
    thin = np.full((1920, 1080, 3), 255, dtype=np.uint8)
    thin[10:1910, 10:1070] = rng.integers(20, 140, (1900, 1060, 3), dtype=np.uint8)
    assert bf.trim_uniform_borders(Image.fromarray(thin)).size == (1080, 1920)
    # 4) Gradient tự nhiên êm không nhảy đột ngột -> giữ nguyên
    grad = np.tile(np.linspace(255, 80, 500, dtype=np.uint8)[:, None, None], (1, 300, 3))
    assert bf.trim_uniform_borders(Image.fromarray(grad)).size == (300, 500)
    # 5) Tích hợp normalize: video có viền trắng 48 px quanh cảnh tối -> cắt sạch viền trước khi scale 1080x1920
    with tempfile.TemporaryDirectory() as td:
        raw, out = Path(td) / "bordered.mp4", Path(td) / "clean.mp4"
        ff(["-f", "lavfi", "-i", "color=c=#203040:s=624x1184:r=30:d=1",
            "-vf", "pad=720:1280:48:48:color=white", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(raw)])
        assert bf.cmd_normalize(type("A", (), {"raw": str(raw), "out": str(out), "mark": None})()) == 0
        raw_px = subprocess.run(["ffmpeg", "-v", "error", "-i", str(out), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                                capture_output=True).stdout
        fr = np.frombuffer(raw_px, np.uint8).reshape(1920, 1080)
        assert float(fr[:10, :].mean()) < 100 and float(fr[-10:, :].mean()) < 100, (fr[:10, :].mean(), fr[-10:, :].mean())
    print("ok  trim_uniform_borders: trắng/đồng màu >= 2 % cắt gọn, < 2 % giữ nguyên, normalize tích hợp")

    print("TẤT CẢ ĐẠT")


if __name__ == "__main__":
    main()
