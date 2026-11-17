#!/usr/bin/env python3
"""Sửa lỗi công cụ từ đợt chạy thử skill (audit): broll_fix lint/mcp-jobs, aroll_bank, render_heygen_aroll, render-aroll, rotation.
Không gọi mạng. Chạy: ~/.venvs/video-skills/bin/python tests/test_skill_audit_fixes.py"""
from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
import broll_fix as bf  # noqa: E402
import render_heygen_aroll as rh  # noqa: E402

PY = sys.executable
LAYERS = {
    "l1_shot_subject": "Over-the-shoulder medium shot of a Vietnamese shop owner counting wooden building blocks",
    "l2_action_script": "stacking each block carefully onto a small tower on the table",
    "l3_environment": "in a bright small workshop with monitors blurred and out of focus",
    "l4_optics_realism": "35mm documentary look, warm window light, natural skin texture, shallow depth of field",
    "l5_camera_motion": "slow push-in",
}
LOOKS = [{"id": f"L{i}", "name": f"look {i}", "group_id": "G", "preview_image_url": "http://x", "supported_api_engines": ["avatar_iv"]}
         for i in (1, 2, 3)]


def run(args, cwd=None):
    return subprocess.run([PY, *map(str, args)], capture_output=True, text=True, cwd=cwd)


def seg(seq, typ, text, dur=4.0, live=False, role=None):
    s = {"seq_index": seq, "type": typ, "role_id": role or f"r{seq}", "tts_text": text, "display_text": text,
         "duration_sec": dur, "beat_name": "x", "files": {"video_file": f"{seq:02d}_{typ}-{seq}.mp4", "voice_file": f"{seq:02d}_v.mp3"}}
    if live:
        s["api_routing"] = {"video_generator": "live_shoot"}
    return s


def make_video(root: Path, sid: str, segs: list, payload=True) -> Path:
    d = root / sid
    d.mkdir(parents=True)
    (d / "00_storyboard_manifest.json").write_text(json.dumps({"script_id": sid, "segments": segs}, ensure_ascii=False), encoding="utf-8")
    items = [{"seq_index": s["seq_index"], "role_id": s["role_id"], "output_file": s["files"]["video_file"],
              "tts_text": s["tts_text"], "duration_hint_sec": s["duration_sec"]}
             for s in segs if s["type"] == "a-roll" and "api_routing" not in s]
    if payload:
        (d / "prompts_heygen_aroll.json").write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    return d


def mixed_video(root: Path, sid: str, shared: str) -> Path:
    """A-roll 1 (live), b-roll 2, A-roll 3 (HeyGen, câu chung), b-roll 4, A-roll 5 (HeyGen, câu riêng)."""
    return make_video(root, sid, [
        seg(1, "a-roll", "Mở đầu quay thật của " + sid, live=True),
        seg(2, "b-roll", "Chủ tiệm xếp khối gỗ lên bàn"),
        seg(3, "a-roll", shared),
        seg(4, "b-roll", "Hai người bàn nhau trong xưởng"),
        seg(5, "a-roll", "Câu kết riêng của " + sid)])


# ---------------------------------------------------------------- 1-2 broll_fix
def test_broll_lint_and_mcp() -> None:
    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        d = mixed_video(root, "KB01", "Cứ bình luận ở dưới nhé.")
        good = {"seq": 2, "anchor_quote": "xếp khối gỗ", "anchor_en": "owner stacks wooden blocks on the table",
                "layers": LAYERS, "prompt": bf.assemble_layered_prompt(LAYERS)}
        (d / "p_good.json").write_text(json.dumps([good]), encoding="utf-8")
        # (1a) --prompts tương đối giải theo thư mục video, kể cả khi cwd là nơi khác
        r = run([SCRIPTS / "broll_fix.py", "lint", d, "--prompts", "p_good.json"], cwd=root)
        assert r.returncode == 0 and "H5 OK" in r.stdout, r.stdout + r.stderr
        assert "CẢNH BÁO" not in r.stdout, r.stdout                                      # anchor_en chung từ "wooden", "blocks"
        # (1b) chỉ có prompt, không có layers -> FAIL
        flat = {k: v for k, v in good.items() if k != "layers"}
        (d / "p_flat.json").write_text(json.dumps([flat]), encoding="utf-8")
        r = run([SCRIPTS / "broll_fix.py", "lint", d, "--prompts", "p_flat.json"])
        assert r.returncode == 1 and "layers" in r.stdout and "H5 FAIL" in r.stdout, r.stdout
        # --no-strict-layers vẫn cho qua đường cũ
        assert run([SCRIPTS / "broll_fix.py", "lint", d, "--prompts", "p_flat.json", "--no-strict-layers"]).returncode == 0
        # (1c) ẩn dụ: prompt không chung từ nội dung với anchor_en -> CẢNH BÁO nhưng không FAIL
        meta = {**good, "anchor_en": "money multiplies by itself"}
        (d / "p_meta.json").write_text(json.dumps([meta]), encoding="utf-8")
        r = run([SCRIPTS / "broll_fix.py", "lint", d, "--prompts", "p_meta.json"])
        assert r.returncode == 0 and "CẢNH BÁO" in r.stdout and "ẩn dụ" in r.stdout, r.stdout
        # không có anchor_en -> "không kiểm được"
        noen = {k: v for k, v in good.items() if k != "anchor_en"}
        (d / "p_noen.json").write_text(json.dumps([noen]), encoding="utf-8")
        r = run([SCRIPTS / "broll_fix.py", "lint", d, "--prompts", "p_noen.json"])
        assert r.returncode == 0 and "CẢNH BÁO" in r.stdout and "không kiểm được" in r.stdout, r.stdout
        # (1d) prepare --dry-run cũng giải đường dẫn tương đối theo thư mục video
        (d / "prompts_muse_veo_broll.json").write_text(json.dumps([{"seq_index": 2, "prompt_full": "x"}]), encoding="utf-8")
        r = run([SCRIPTS / "broll_fix.py", "prepare", d, "--prompts", "p_good.json", "--dry-run", "--backup-root", root / "bk"], cwd=root)
        assert "không đọc được" not in r.stderr and "No such file" not in r.stderr, r.stderr
        # (2) mcp-jobs không --inspect: hướng dẫn rõ, không phải lỗi argparse
        r = run([SCRIPTS / "broll_fix.py", "mcp-jobs", d])
        assert r.returncode == 0 and "--inspect" in r.stderr and "required" not in r.stderr, r.stderr
        assert "cảnh 2" in r.stdout and "cảnh 4" in r.stdout, r.stdout
    print("ok  broll_fix: --prompts tương đối, layers bắt buộc, cảnh báo ẩn dụ, mcp-jobs không inspect")


# ---------------------------------------------------------------- 3 aroll_bank
def test_aroll_bank_modes() -> None:
    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        shared = "Cứ bình luận chữ MẪU ở dưới nhé."
        ms = [mixed_video(root, f"KB0{i}", shared) / "00_storyboard_manifest.json" for i in (1, 2)]
        out = root / "o"
        r = run([SCRIPTS / "aroll_bank.py", *ms, "--out", out])
        assert r.returncode == 0, r.stderr[-600:]
        bank = json.loads((out / "bank.json").read_text(encoding="utf-8"))
        plans = json.loads((out / "plans.json").read_text(encoding="utf-8"))
        stats = json.loads((out / "stats.json").read_text(encoding="utf-8"))
        # mode script (mặc định): câu y hệt gộp một render, câu riêng giữ nguyên, không thay chữ
        assert all(not e["requires_rewrite"] for e in bank)
        by_text = {e["bank_text"]: e for e in bank}
        assert len(by_text[shared]["used_in"]) == 2
        # (3a) seq_index = seq_index thật của A-roll trong manifest (3 và 5), không phải vị trí 1,2
        assert sorted(u["seq_index"] for e in bank for u in e["used_in"]) == [3, 3, 5, 5]
        for p in plans:
            assert [s["seq_index"] for s in p["slots"]] == [3, 5]
            for s in p["slots"]:
                assert s["original_text"] == s["bank_text"] and s["requires_rewrite"] is False
        # (3c) live_shoot không vào bank; có trong stats "quay thật"
        assert not any("quay thật" in e["bank_text"] for e in bank)
        live = stats["quay thật"]
        assert live["shots"] == 2 and {i["seq_index"] for i in live["list"]} == {1}
        assert stats["plan"]["baseline_aroll_renders"] == 4 and stats["plan"]["planned_renders"] == 3
        assert "Quay thật" in (out / "approval.md").read_text(encoding="utf-8")
        # (3b) mode library: câu chung, MỌI slot requires_rewrite + giữ original_text
        out2 = root / "o2"
        assert run([SCRIPTS / "aroll_bank.py", *ms, "--out", out2, "--mode", "library"]).returncode == 0
        plans2 = json.loads((out2 / "plans.json").read_text(encoding="utf-8"))
        slots = [s for p in plans2 for s in p["slots"]]
        assert slots and all(s["requires_rewrite"] for s in slots)
        assert {s["original_text"] for s in slots} - {None} <= {"Cứ bình luận chữ MẪU ở dưới nhé.", "Câu kết riêng của KB01", "Câu kết riêng của KB02"}
        assert all(s["seq_index"] in (3, 5, None) for s in slots)
        assert any(s["original_text"] and s["original_text"] != s["bank_text"] for s in slots)
    print("ok  aroll_bank: seq_index thật, original/bank/requires_rewrite, --mode script|library, quay thật")


# ---------------------------------------------------------------- 4 render_heygen_aroll
def run_rh(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = rh.main(argv)
    return rc, buf.getvalue()


def test_render_bank_looks_estimate_live() -> None:
    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        looks = root / "looks.json"
        looks.write_text(json.dumps(LOOKS), encoding="utf-8")
        bank = [{"bank_id": "B01", "text": "cau mot", "look_slot": 1, "duration_hint_sec": 3.0},
                {"bank_id": "B02", "text": "cau hai", "look_slot": 2, "duration_hint_sec": 4.0},
                {"bank_id": "B03", "text": "cau ba", "look_slot": 5, "duration_hint_sec": 5.0}]
        bj = root / "bank.json"
        bj.write_text(json.dumps(bank), encoding="utf-8")
        # --bank --looks --assign auto: look_slot -> look thật (vòng quanh); không dùng avatar mặc định
        rc, out = run_rh(["--bank", str(bj), "--looks", str(looks), "--assign", "auto", "--estimate"])
        assert rc == 0, out
        for lid in ("L1", "L2"):
            assert lid in out, out
        assert "761364fad106369de1c3ada3994aee9c" not in out, out
        # slot 5 trên 3 look -> L2
        jobs = rh.plan_jobs(rh.build_parser().parse_args(["--bank", str(bj), "--looks", str(looks), "--assign", "auto"]))
        assert {it["output_file"]: it["avatar_id"] for _, it in jobs} == {"B01.mp4": "L1", "B02.mp4": "L2", "B03.mp4": "L2"}
        # --estimate không có giá: giây + "giá: chưa có (thêm --usd-per-min)"
        assert "12.0" in out and "giá: chưa có (thêm --usd-per-min)" in out, out
        rc, out = run_rh(["--bank", str(bj), "--estimate", "--usd-per-min", "2"])
        assert "giá: chưa có" not in out and "USD" in out, out
        # --assign auto thiếu --looks -> lỗi rõ
        rc, out = run_rh(["--bank", str(bj), "--assign", "auto"])
        assert rc == 1 and "--looks" in out, out
        # live_shoot: dòng cảnh báo trong dry-run (manifest có live, payload không có)
        vids = root / "vids"
        mixed_video(vids, "KB01", "Cứ bình luận ở dưới nhé.")
        rc, out = run_rh([str(vids)])
        assert rc == 0 and "BỎ QUA (quay thật): KB01/01_a-roll-1.mp4" in out, out
        assert "01_a-roll-1.mp4 (" not in out.replace("BỎ QUA (quay thật): KB01/01_a-roll-1.mp4", ""), out
        rc, out = run_rh([str(vids), "--shot", "a-roll-3"])
        assert "BỎ QUA (quay thật)" not in out, out                                       # lọc shot: không báo shot ngoài bộ lọc
    print("ok  render_heygen_aroll: bank honours looks/assign, estimate không giá, cảnh báo quay thật")


def test_link_bank_accepts_used_in_dicts() -> None:
    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        vids = root / "vids"
        d = make_video(vids, "KB01", [seg(1, "a-roll", "cau mot")])
        items = json.loads((d / "prompts_heygen_aroll.json").read_text(encoding="utf-8"))
        items[0]["bank_id"] = "B01"
        (d / "prompts_heygen_aroll.json").write_text(json.dumps(items), encoding="utf-8")
        (root / "bank").mkdir()
        (root / "bank/B01.mp4").write_bytes(b"0" * 20_000)
        bank = [{"bank_id": "B01", "text": "cau mot", "used_in": [{"script_id": "KB01", "seq_index": 1}]}]
        msgs = rh.link_bank(bank, vids, root / "bank")
        assert msgs and msgs[0].startswith("linked"), msgs
    print("ok  link_bank nhận used_in dạng dict của aroll_bank")


# ---------------------------------------------------------------- 5 analyze_and_scaffold render-aroll
def test_render_aroll_forwards() -> None:
    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        looks = root / "looks.json"
        looks.write_text(json.dumps(LOOKS), encoding="utf-8")
        vids = root / "vids"
        d = mixed_video(vids, "KB01", "Cứ bình luận ở dưới nhé.")
        asc = SCRIPTS / "analyze_and_scaffold.py"
        r = run([asc, "render-aroll", vids, "--looks", looks, "--assign", "auto", "--estimate"])
        assert r.returncode == 0, r.stdout + r.stderr
        assert "ƯỚC LƯỢNG" in r.stdout and "L1" in r.stdout, r.stdout                      # --looks/--assign/--estimate tới nơi
        assert "BỎ QUA (quay thật): KB01/01_a-roll-1.mp4" in r.stdout, r.stdout
        # --bank không cần target_dir
        bj = root / "bank.json"
        bj.write_text(json.dumps([{"bank_id": "B01", "text": "cau mot", "look_slot": 2}]), encoding="utf-8")
        r = run([asc, "render-aroll", "--bank", bj, "--looks", looks, "--assign", "auto", "--estimate"])
        assert r.returncode == 0 and "L2" in r.stdout, r.stdout + r.stderr
        # --key-file chỉ dùng khi --yes; không có --yes vẫn DRY-RUN, không gọi mạng
        r = run([asc, "render-aroll", d, "--key-file", root / "nokey.txt"])
        assert r.returncode == 0 and "DRY-RUN" in r.stdout, r.stdout + r.stderr
    print("ok  render-aroll chuyển --looks --assign --bank --estimate --key-file, in cảnh báo quay thật")


# ---------------------------------------------------------------- 6 rotation
def test_rotation_help() -> None:
    for argv in (["plan", "--help"], ["--help"], ["show", "-h"]):
        r = run([SCRIPTS / "rotation.py", *argv])
        assert r.returncode == 0 and "Traceback" not in r.stderr, (argv, r.stderr[-300:])
        assert "rotation.py plan" in r.stdout, r.stdout
    print("ok  rotation.py plan --help in cách dùng")


if __name__ == "__main__":
    test_broll_lint_and_mcp()
    test_aroll_bank_modes()
    test_render_bank_looks_estimate_live()
    test_link_bank_accepts_used_in_dicts()
    test_render_aroll_forwards()
    test_rotation_help()
    print("TẤT CẢ ĐẠT")
