#!/usr/bin/env python3
"""Rule 1 (tốc độ D4 2026-11-13: 1.10x / 1.05x, < 45 s giữ 1.0x) · Rule 2 (đa dạng chuyển cảnh) · Rule 3 (chặn media x125 / x115).
Chạy: ~/.venvs/video-skills/bin/python tests/test_rules_2026_11_11.py"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import cut_plan  # noqa: E402
from build_kit import choose_speed, speed_dir  # noqa: E402
from spec_lint import lint  # noqa: E402
from text_motion import ensure_motion, static_report  # noqa: E402
import frame_person as fp  # noqa: E402
import media_reuse as mr  # noqa: E402
import retime_voice as rv  # noqa: E402
from spec_lint import check_text_voice  # noqa: E402


def test_speed() -> None:
    # D4 (người dùng 2026-11-13): chỉ 1.10x / 1.05x; video < 45 s không tăng; tăng tốc không đẩy video xuống dưới 45 s
    for total, want in ((80, 1.1), (49.5, 1.1), (49, 1.05), (47.25, 1.05), (47, 1.0), (45, 1.0), (44.9, 1.0), (30, 1.0)):
        assert choose_speed(total) == want, (total, choose_speed(total))
    assert all(choose_speed(t) in (1.0, 1.05, 1.1) for t in range(10, 300))
    assert speed_dir(1.1) == "x110" and speed_dir(1.05) == "x105" and speed_dir(1.0) == "x100"
    for bad in (1.15, 1.25):
        try:
            speed_dir(bad)
            raise AssertionError(f"{bad} phải bị cấm")
        except ValueError:
            pass
    print("ok  Rule 1: 1.10x → 1.05x → 1.0x (< 45 s giữ 1.0x), cấm 1.15x / 1.25x")


def test_transitions() -> None:
    kinds = ["jump cut · câu mới", "đổi cảnh", "đổi góc gần", "jump cut · đổi phần", "ra B-roll"] * 8
    for seed in (0, 17, 401):
        used, recent_all, picks = {}, [], []
        for i, k in enumerate(kinds):
            p = cut_plan._pick(cut_plan.OPTIONS[k], recent_all[-cut_plan.RECENT_N:], used, len(recent_all), seed)
            picks.append(p); recent_all.append(p); used[p] = used.get(p, 0) + 1
        flashy = [i for i, p in enumerate(picks) if p in cut_plan.FLASHY]
        assert len(flashy) <= cut_plan.MAX_FLASHY_SHARE * len(picks) + 1, (seed, len(flashy))
        assert all(b - a >= cut_plan.FLASHY_GAP for a, b in zip(flashy, flashy[1:])), (seed, flashy)
        for i in range(len(picks)):
            assert picks[i] not in picks[max(0, i - cut_plan.RECENT_N):i], (seed, i, picks[i])
        assert len(set(picks)) >= 15, (seed, len(set(picks)))
    print(f"ok  Rule 2: nháy sáng ≤ {cut_plan.MAX_FLASHY_SHARE:.0%}, cách ≥ {cut_plan.FLASHY_GAP}, không lặp trong "
          f"{cut_plan.RECENT_N}, ≥ 15 kiểu / 40 điểm cắt")


def test_lint_speed() -> None:
    for bad in ("x125", "x115"):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / f"media/{bad}").mkdir(parents=True)
            v = d / f"media/{bad}/a.mp4"
            v.write_bytes(b"")
            spec = {"fps": 30, "duration": 1, "tracks": [{"type": "video", "name": "V1",
                                                           "clips": [{"src": str(v), "at": 0, "in": 0, "dur": 1}]}]}
            p = d / "kb99.craft.json"
            p.write_text(json.dumps(spec))
            res = {r["id"]: r["status"] for r in lint(p, None)}
            assert res["speed_not_allowed"] == "HARD", (bad, res)
    print("ok  Rule 1/3: spec dùng media x125 / x115 bị chặn HARD")


def test_text_motion() -> None:
    static = {"text": "Phụ đề", "at": 1.0, "dur": 1.6, "position": [540, 1400]}
    slam = {"text": "TỪ KHOÁ", "at": 2.0, "dur": 2.0, "position": [540, 500],
            "motion": {"anchor": [540, 500], "position": [540, 500], "scale": [[0, 140], [0.2, 100, "easeIn"]]}}
    typed = {"text": "Gõ chữ", "at": 0, "dur": 2.5, "position": [540, 300],
             "effects": [{"effect": "crop", "params": {"right": [[0, 70], [1.2, 0]]}}], "transition_out": {"effect": "x"}}
    items = [("text_low", static), ("text", slam), ("text_top", typed)]
    before = static_report([{"name": "text_low 1", "clips": [static]}, {"name": "text 1", "clips": [slam]},
                            {"name": "text_top 1", "clips": [typed]}])
    n = ensure_motion(items, 30)
    assert static["opacity"][0] == [0.0, 0] and static["opacity"][-1][1] == 0            # soft_in + soft_out
    assert any(e["effect"] == "transform" for e in static["effects"])                     # phóng chậm lúc giữ
    assert slam["motion"]["scale"][0] == [0, 140]                                         # giữ nguyên kiểu vào riêng
    assert not typed.get("opacity")                                                       # đã có transition_out: không thêm ra
    after = static_report([{"name": "text_low 1", "clips": [static]}, {"name": "text 1", "clips": [slam]},
                           {"name": "text_top 1", "clips": [typed]}])
    assert before["static_hold"] == 3 and after["static_hold"] == 0 and after["no_entrance"] == 0, (before, after)
    assert ensure_motion(items, 30)["hold"] == 0                                          # chạy lại không thêm chồng
    print(f"ok  Rule 4: chữ tĩnh lúc giữ {before['static_hold']} → {after['static_hold']}, thêm {n}")
    # lỗi phản biện 2026-11-11: clip 2 khung (font_flip) không bị thêm key trùng mốc
    flip = {"text": "A", "at": 0, "dur": 2 / 30, "position": [540, 1400]}
    ensure_motion([("text_low", flip)], 30)
    assert "opacity" not in flip and "effects" not in flip
    # key phóng giữ không vượt cuối clip khi dur = 1,3666… (fc_build chặn key quá cuối)
    odd = {"text": "B", "at": 0, "dur": 41 / 30, "position": [540, 1400], "transition_out": {"effect": "cross_dissolve"}}
    ensure_motion([("text_low", odd)], 30)
    tr = next(e for e in odd["effects"] if e["effect"] == "transform")
    assert tr["params"]["scale_height"][-1][0] <= odd["dur"] + 1e-9
    # chữ sau người: transform chèn TRƯỚC track_matte
    behind = {"text": "C", "at": 0, "dur": 2.0, "position": [540, 500],
              "effects": [{"effect": "crop", "params": {"right": [[0, 50], [0.2, 0]]}}, {"effect": "track_matte", "params": {}}]}
    ensure_motion([("text", behind)], 30)
    names = [e["effect"] for e in behind["effects"]]
    assert names.index("transform") < names.index("track_matte"), names
    print("ok  Rule 4: clip 2 khung giữ nguyên · key không vượt cuối · phóng trước track matte")


def test_framing() -> None:
    base = {"src_size": [1080, 1920], "rotate": 0, "face_cx": 540, "green_ratio": 0}
    ok = fp.plan({**base, "kind": "bright", "bg_luma": 190, "head_top": 650})
    assert ok["action"] == "ok"
    low = fp.plan({**base, "kind": "bright", "bg_luma": 190, "head_top": 900})          # người thấp → phóng ≤ 1,35
    assert low["action"] == "reframe" and 1.0 < low["scale"] <= fp.SCALE_MAX
    assert abs(low["scale"] * 900 - low["crop_y"] - fp.HEAD_TARGET) < 2                # đỉnh đầu về đường 1/3
    high = fp.plan({**base, "kind": "bright", "bg_luma": 190, "head_top": 300})         # người cao: phóng 2,1× quá mờ
    assert high["action"] == "composite"
    dark = fp.plan({**base, "kind": "dark", "bg_luma": 65, "head_top": 297})            # avatar HeyGen phòng tối
    assert dark["action"] == "composite" and abs(dark["dy"] + dark["scale"] * 297 - fp.HEAD_TARGET) <= 1
    assert abs(dark["dy"] + dark["scale"] * 1920 - 1920) <= 1                           # thân chạm đáy khung
    green = fp.plan({**base, "kind": "green", "bg_luma": 115, "head_top": 578})
    assert green["action"] == "composite"
    assert fp.plan({**base, "kind": "dark", "bg_luma": 60})["action"] == "skip"          # không thấy mặt
    print("ok  Rule 5: nền sáng giữ / phóng ≤ 1,35× · nền tối & phông xanh ghép phòng sáng · đầu ở đường 1/3")


def test_band_cover() -> None:
    from edit_rules import audit_spec
    spec = {"fps": 30, "duration": 5, "tracks": [
        {"type": "video", "name": "V4 Dải tối vùng phụ đề", "clips": [{"src": "x.png", "at": 0, "dur": 5, "name": "Dải tối dưới"}]},
        {"type": "video", "name": "Ảnh bìa (1 giây đầu)", "clips": [{"src": "c.png", "at": 0, "dur": 1.0, "name": "Ảnh bìa"}]}]}
    r = {x["rule"]: x["status"] for x in audit_spec(spec)}
    assert r["Không dải tối dưới chữ phụ"] == "CẢNH BÁO" and r["Ảnh bìa ≤ 0,3 s đầu video"] == "CẢNH BÁO", r
    spec["tracks"] = [{"type": "video", "name": "Ảnh bìa (0,3 giây đầu)", "clips": [{"src": "c.png", "at": 0, "dur": 0.3, "name": "Ảnh bìa"}]}]
    r = {x["rule"]: x["status"] for x in audit_spec(spec)}
    assert r["Không dải tối dưới chữ phụ"] == "OK" and r["Ảnh bìa ≤ 0,3 s đầu video"] == "OK", r
    import motion_fx
    assert motion_fx.MotionFX.ALLOW_CAPTION_BAND is False
    print("ok  B15 / A6: bắt dải tối dưới phụ đề + ảnh bìa 1 s; 0,3 s thì đạt")


def test_reuse_and_voice() -> None:
    assert mr.code_of("KB06_B02_35s-41s_So_Do.mp4") == "KB06" and mr.code_of("16_KB06_Cong_Thuc") == "KB06"
    assert mr.code_of("01_OPA01_Tuoi_32") == "OPA01" and mr.code_of("03_b-roll-2.mp4") is None
    spec = {"tracks": [{"type": "video", "name": "V1 chuỗi", "clips": [
        {"src": "/x/02_b-roll-1.mp4", "at": 0, "dur": 2, "name": "B-roll 1 (1)"},
        {"src": "/x/02_b-roll-1.mp4", "at": 2, "dur": 2, "name": "B-roll 1 (2)"},       # tách đôi liền nhau = 1 lần
        {"src": "/x/02_b-roll-1.mp4", "at": 9, "dur": 2, "name": "B-roll 1 lại"}]},     # lần 2 tách rời → đạt (MAX_PER_VIDEO=2)
        {"type": "video", "name": "trans 1", "clips": [{"src": "/x/flash.mp4", "at": 1, "dur": 1}]}]}
    assert mr.MAX_PER_VIDEO == 2 and mr.MAX_VIDEOS_PER_BROLL == 2
    assert len(mr.uses_of(spec)) == 2
    spec_extra = {"tracks": [{"type": "video", "name": "V1 chuỗi", "clips": [
        {"src": "/x/cam1.mp4", "at": 0, "dur": 2, "name": "Footage studio"},
        {"src": "/x/06_B-Roll/clip.mp4", "at": 3, "dur": 2, "name": "chèn"},
        {"src": "/x/flow_a.mp4", "at": 6, "dur": 2, "broll_source": "flow", "name": "clip"},
        {"src": "/x/ftg_desk.mp4", "at": 9, "dur": 2, "name": "desk"}]}]}
    assert len(mr.uses_of(spec_extra)) == 4
    good = {"words": [{"text": w, "start": i * 0.3, "end": i * 0.3 + 0.2, "type": "word"} for i, w in enumerate("một hai ba bốn năm sáu bảy".split())]}
    bad = {"words": [{"text": w, "start": 5.63, "end": 5.63, "type": "word"} for w in "a b c d".split()]}
    assert rv.broken(good) is None and rv.broken(bad)
    assert check_text_voice([[w, 1.0 + i * 0.01, 1.1] for i, w in enumerate("abcdefg")])[0]["status"] == "HARD"
    assert check_text_voice([[w, i * 0.3, i * 0.3 + 0.2] for i, w in enumerate("abcdefg")])[0]["status"] == "OK"
    print("ok  D8–D10 / B16: mã kịch bản · gộp đoạn liền · bắt dồn mốc giọng · HARD chữ bật cùng lúc")


def test_d15_and_d8_rules() -> None:
    import subprocess
    from edit_rules import audit_spec

    # 1) D15: 100% flow -> OK; 4% real_footage -> OK; >5% real_footage -> LỖI; stock/muse -> LỖI; unknown -> CẢNH BÁO
    base_spec = lambda clips: {"fps": 30, "duration": 100, "tracks": [{"type": "video", "name": "V1", "clips": clips}]}  # noqa: E731
    r_flow = {x["rule"]: x["status"] for x in audit_spec(base_spec([
        {"src": "/a/02_b-roll-1.mp4", "at": 0, "dur": 20, "name": "B-roll 1", "broll_source": "flow"},
        {"src": "/a/03_b-roll-2.mp4", "at": 25, "dur": 20, "name": "B-roll 2", "broll_source": "flow"},
    ]))}
    assert r_flow["B-roll Google Flow mặc định (100%); footage thật ≤ 5 %"] == "OK", r_flow
    assert r_flow["Mỗi clip B-roll tối đa 2 lần trong 1 video"] == "OK", r_flow

    r_real_ok = {x["rule"]: x["status"] for x in audit_spec(base_spec([
        {"src": "/a/02_b-roll-1.mp4", "at": 0, "dur": 48, "name": "B-roll 1", "broll_source": "flow"},
        {"src": "/a/03_b-roll-2.mp4", "at": 48, "dur": 2, "name": "Footage studio", "broll_source": "real_footage"},  # 2/50 = 4%
    ]))}
    assert r_real_ok["B-roll Google Flow mặc định (100%); footage thật ≤ 5 %"] == "OK", r_real_ok

    r_real_bad = {x["rule"]: x["status"] for x in audit_spec(base_spec([
        {"src": "/a/02_b-roll-1.mp4", "at": 0, "dur": 45, "name": "B-roll 1", "broll_source": "flow"},
        {"src": "/a/03_b-roll-2.mp4", "at": 45, "dur": 5, "name": "Footage studio", "broll_source": "real_footage"},   # 5/50 = 10%
    ]))}
    assert r_real_bad["B-roll Google Flow mặc định (100%); footage thật ≤ 5 %"] == "LỖI", r_real_bad

    for bad_src in ("stock", "muse"):
        r_bad = {x["rule"]: x["status"] for x in audit_spec(base_spec([
            {"src": "/a/02_b-roll-1.mp4", "at": 0, "dur": 20, "name": "B-roll 1", "broll_source": "flow"},
            {"src": "/a/03_b-roll-2.mp4", "at": 20, "dur": 5, "name": "B-roll 2", "broll_source": bad_src},
        ]))}
        assert r_bad["B-roll Google Flow mặc định (100%); footage thật ≤ 5 %"] == "LỖI", (bad_src, r_bad)

    r_unk = {x["rule"]: x["status"] for x in audit_spec(base_spec([
        {"src": "/a/02_b-roll-1.mp4", "at": 0, "dur": 10, "name": "B-roll 1"},
    ]))}
    assert r_unk["B-roll Google Flow mặc định (100%); footage thật ≤ 5 %"] == "CẢNH BÁO", r_unk

    # 2) D8: > 2 lần trong 1 video (gồm cả đường dẫn x110 / x105) -> LỖI; đúng 2 lần (hoặc ghép liền <= 0.15s) -> OK
    r_2 = {x["rule"]: x["status"] for x in audit_spec(base_spec([
        {"src": "/a/media/x110/02_b-roll-1_x110.mp4", "at": 0, "dur": 2, "name": "B-roll 1", "broll_source": "flow"},
        {"src": "/a/media/x110/02_b-roll-1_x110.mp4", "at": 2.05, "dur": 2, "name": "B-roll 1", "broll_source": "flow"},  # gộp liền = lần 1
        {"src": "/a/media/x105/02_b-roll-1_x105.mp4", "at": 10, "dur": 2, "name": "B-roll 1", "broll_source": "flow"},    # lần 2
    ]))}
    assert r_2["Mỗi clip B-roll tối đa 2 lần trong 1 video"] == "OK", r_2

    r_3 = {x["rule"]: x["status"] for x in audit_spec(base_spec([
        {"src": "/a/media/x110/02_b-roll-1_x110.mp4", "at": 0, "dur": 2, "name": "B-roll 1", "broll_source": "flow"},
        {"src": "/a/media/x110/02_b-roll-1_x110.mp4", "at": 5, "dur": 2, "name": "B-roll 1", "broll_source": "flow"},
        {"src": "/a/media/x105/02_b-roll-1_x105.mp4", "at": 10, "dur": 2, "name": "B-roll 1", "broll_source": "flow"},
    ]))}
    assert r_3["Mỗi clip B-roll tối đa 2 lần trong 1 video"] == "LỖI", r_3

    # 3) CLI auto-discover _broll_sources.json từ thư mục cha + media_reuse versioned dir collapse
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        proj = root / "ProjA"
        (proj / "v1/work").mkdir(parents=True)
        (proj / "v2/work").mkdir(parents=True)
        (proj / "_broll_sources.json").write_text(json.dumps({"02_b-roll-1.mp4": {"source": "flow"}}), encoding="utf-8")
        spec_p = proj / "v2/work/proja.craft.json"
        spec_p.write_text(json.dumps(base_spec([
            {"src": str(proj / "media/x110/02_b-roll-1_x110.mp4"), "at": 0, "dur": 10, "name": "B-roll 1"},
        ])), encoding="utf-8")
        res_cli = subprocess.run(
            [sys.executable, str(Path(__file__).resolve().parents[1] / "scripts/edit_rules.py"), "audit", str(spec_p), "--json"],
            capture_output=True, text=True,
        )
        items = {x["rule"]: x["status"] for x in json.loads(res_cli.stdout)}
        assert items["B-roll Google Flow mặc định (100%); footage thật ≤ 5 %"] == "OK", items

        # media_reuse versioned dir deduplication (v1/v2 gộp 1 video; ProjA/v2 vs ProjB/v2 không đụng tên)
        (root / "ProjB/v2/work").mkdir(parents=True)
        clip1 = root / "02_b-roll-1.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "mandelbrot=s=108x192:r=30", "-t", "1",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(clip1)], check=True)
        old_lib, old_raw = list(mr.LIB_DIRS), mr.SOURCE_RAW
        mr.LIB_DIRS[:] = []
        mr.SOURCE_RAW = root / "_no_raw"
        mr.fingerprint.cache_clear()
        try:
            (proj / "v1/work/proja.craft.json").write_text(json.dumps(base_spec([
                {"src": str(clip1), "at": 0, "dur": 1, "name": "B-roll 1"},
                {"src": str(clip1), "at": 3, "dur": 1, "name": "B-roll 1"},
                {"src": str(clip1), "at": 6, "dur": 1, "name": "B-roll 1"},  # v1 lỗi nhưng v2 đã sửa → chỉ xét v2!
            ])), encoding="utf-8")
            (proj / "v2/work/proja.craft.json").write_text(json.dumps(base_spec([
                {"src": str(clip1), "at": 0, "dur": 1, "name": "B-roll 1"},
                {"src": str(clip1), "at": 3, "dur": 1, "name": "B-roll 1"},  # 2 lần trong video -> đạt
            ])), encoding="utf-8")
            (root / "ProjB/v2/work/projb.craft.json").write_text(json.dumps(base_spec([
                {"src": str(clip1), "at": 0, "dur": 1, "name": "B-roll 1"},  # video thứ 2 dùng clip1 -> đạt (<=2)
            ])), encoding="utf-8")
            au = mr.audit([root])
            assert au["videos"] == 2 and not au["violations"], au
            # Thêm video thứ 3 cùng clip1 -> vi phạm D8 (> 2 video)
            (root / "ProjC/v1/work").mkdir(parents=True)
            (root / "ProjC/v1/work/projc.craft.json").write_text(json.dumps(base_spec([
                {"src": str(clip1), "at": 0, "dur": 1, "name": "B-roll 1"},
            ])), encoding="utf-8")
            au3 = mr.audit([root])
            assert au3["videos"] == 3 and any(v["rule"] == "D8" and "3 video" in v["detail"] for v in au3["violations"]), au3
        finally:
            mr.LIB_DIRS[:] = old_lib
            mr.SOURCE_RAW = old_raw
    print("ok  D15 / D8: nguồn Flow / footage thật ≤ 5 % / tối đa 2 lần/video / gộp thư mục phiên bản v1–v2")


if __name__ == "__main__":
    test_reuse_and_voice()
    test_d15_and_d8_rules()
    test_band_cover()
    test_framing()
    test_text_motion()
    test_speed()
    test_transitions()
    test_lint_speed()
    print("TẤT CẢ ĐẠT")
