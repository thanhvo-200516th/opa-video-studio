#!/usr/bin/env python3
"""Kiểm broll_from_video.py (analyze + check-prompts) với transcript giả lập ~45s offline.
Chạy: ~/.venvs/video-skills/bin/python -B tests/test_broll_from_video.py"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import broll_fix as bf  # noqa: E402
import broll_from_video as bfv  # noqa: E402


def make_scribe_transcript(sentences: list[tuple[str, float, float]]) -> dict:
    """Tạo transcript Scribe-style JSON từ danh sách (câu, start, end)."""
    words: list[dict] = []
    full_texts: list[str] = []
    for text, t0, t1 in sentences:
        full_texts.append(text)
        toks = text.split()
        step = (t1 - t0) / max(1, len(toks))
        for i, tok in enumerate(toks):
            ws = round(t0 + i * step, 3)
            we = round(t0 + (i + 1) * step - 0.02, 3)
            if words:
                words.append({
                    "text": " ",
                    "start": words[-1]["end"],
                    "end": ws,
                    "type": "spacing",
                    "speaker_id": "speaker_0",
                })
            words.append({
                "text": tok,
                "start": ws,
                "end": max(ws + 0.05, we),
                "type": "word",
                "speaker_id": "speaker_0",
            })
    return {
        "language_code": "vi",
        "text": " ".join(full_texts),
        "words": words,
    }


def build_45s_transcript() -> dict:
    sentences = [
        ("Tại sao nhiều chủ shop làm việc suốt ngày mà vẫn không ra đơn?", 0.0, 3.4),
        ("Mỗi sáng mở mắt ra bạn ngồi trước bàn làm việc đầy việc không tên.", 3.9, 8.2),
        ("Nhân viên thì chậm trễ, khách nhắn tin năm phút chưa trả lời là mất khách ngay.", 8.8, 14.3),
        ("Bọn mình từng mất thời gian cả tháng trời để tự bơi với quy trình rác đó.", 14.9, 20.1),
        ("Sau đó đội ngũ kỹ thuật đã ngồi lại xây dựng quy trình gọn nhẹ trong văn phòng.", 20.7, 26.5),
        ("Ví dụ khi khách hàng mới hỏi sản phẩm, hệ thống xử lý ngay trong ba mươi giây.", 27.1, 32.8),
        ("Nhờ vậy buổi sáng nhân viên kiểm tra đơn hàng rất nhẹ nhàng và không còn quá tải.", 33.4, 39.6),
        ("Kết quả là tỷ lệ chốt đơn tăng rõ rệt, hãy follow kênh để xem thêm nhé.", 40.2, 45.0),
    ]
    return make_scribe_transcript(sentences)


def verify_max_aroll_run(slots: list[dict], limit: float = 8.0) -> None:
    cur_start = None
    cur_end = None
    for s in slots:
        if s["role"] == "A-ROLL":
            if cur_start is None:
                cur_start = s["start"]
            cur_end = s["end"]
            assert cur_end - cur_start <= limit + 1e-6, (
                f"Đoạn A-ROLL trơ vượt {limit}s: {cur_start}–{cur_end} ({cur_end - cur_start:.2f}s)"
            )
        else:
            cur_start = None
            cur_end = None


def safe_prompt_for(slot: dict) -> str:
    quote = slot["anchor_quote"].lower()
    if "mất khách" in quote:
        return (
            "Over-the-shoulder shot of a young Vietnamese shop owner holding a blank phone out of focus "
            "in a quiet evening store, looking toward an empty doorway, warm lamp light, slow push-in."
        )
    if "quy trình rác" in quote or "tự bơi" in quote:
        return (
            "Back view of a tired Vietnamese office worker sitting at a wooden desk stacked with plain "
            "blank folders in a dimly lit room, rubbing temples slowly, warm desk glow, slow dolly-in."
        )
    if "hệ thống" in quote or "sản phẩm" in quote:
        return (
            "Medium shot of a young Vietnamese engineering team working calmly at a long table with "
            "unbranded laptops blurred out of focus in a bright office, warm daylight, smooth lateral tracking."
        )
    if "quá tải" in quote or "đơn hàng" in quote:
        return (
            "Medium close-up of a Vietnamese warehouse staff member taping a plain unbranded cardboard box "
            "on a clean wooden packing table in morning sunlight, shallow depth of field, slow orbit."
        )
    return (
        "Seen from behind, a Vietnamese founder in a plain dark shirt organizing clean desk items "
        "near a sunlit office window, laptop lid closed and out of focus, warm daylight, slow push-in."
    )


def run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / "broll_from_video.py"), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_analyze_45s() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        tr_path = tmp / "transcript_45s.json"
        tr_path.write_text(json.dumps(build_45s_transcript(), ensure_ascii=False, indent=2), encoding="utf-8")

        out_dir = tmp / "work"
        res = run_cli(["analyze", "--transcript", str(tr_path), "--out", str(out_dir)])
        assert res.returncode == 0, f"analyze thất bại:\n{res.stdout}\n{res.stderr}"

        plan_json = out_dir / "broll_plan.json"
        plan_md = out_dir / "broll_plan.md"
        assert plan_json.is_file() and plan_md.is_file(), "Thiếu broll_plan.json hoặc broll_plan.md"

        plan = json.loads(plan_json.read_text(encoding="utf-8"))
        slots = plan["slots"]
        assert len(slots) >= 6, f"Số block quá ít: {len(slots)}"
        assert round(plan["video_duration"], 1) == 45.0, plan["video_duration"]

        # Hook mở đầu và CTA cuối video giữ A-ROLL
        assert slots[0]["role"] == "A-ROLL", f"Hook phải là A-ROLL: {slots[0]}"
        assert slots[-1]["role"] == "A-ROLL", f"CTA cuối nên giữ A-ROLL: {slots[-1]}"

        # Luật D1: B-Roll >= 25%, không đoạn A-Roll trơ > 8s
        assert plan["broll_pct"] >= 25.0, f"Độ phủ B-Roll < 25%: {plan['broll_pct']}%"
        assert plan["broll_duration"] / plan["video_duration"] >= 0.25
        assert plan["max_aroll_run_sec"] <= 8.0, f"max_aroll_run_sec={plan['max_aroll_run_sec']}"
        verify_max_aroll_run(slots, 8.0)

        # Luật E2: Ít nhất các đoạn có từ khoá nỗi đau phải được chọn làm B-ROLL
        broll_slots = [s for s in slots if s["role"] == "B-ROLL"]
        assert any(s["pain_keywords"] for s in broll_slots), "Không có slot nỗi đau nào được chọn B-ROLL"

        # Kiểm tra flow_seconds & flow_credits_x2 khớp broll_fix
        sum_credits = 0
        for s in broll_slots:
            expected_sec = bf.flow_seconds(s["voice_len"])
            expected_cred = bf.flow_credits(expected_sec, outputs=2)
            assert s["flow_seconds"] == expected_sec, (s["slot_id"], s["flow_seconds"], expected_sec)
            assert s["flow_credits_x2"] == expected_cred, (s["slot_id"], s["flow_credits_x2"], expected_cred)
            assert s["anchor_quote"].strip() != ""
            assert s["prompt_draft_hint"].strip() != ""
            sum_credits += expected_cred
        assert plan["total_credits_x2"] == sum_credits, (plan["total_credits_x2"], sum_credits)

        md_text = plan_md.read_text(encoding="utf-8")
        assert "anchor_quote" in md_text and "Tín dụng" in md_text

        # --- Kiểm check-prompts: trường hợp vi phạm H5 phải FAIL
        bad_prompts = []
        for idx, s in enumerate(broll_slots):
            if idx == 0:
                bad_prompts.append({
                    "slot_id": s["slot_id"],
                    "anchor_quote": s["anchor_quote"],
                    "prompt": "A tired woman checks analytics dashboard and chart on laptop in office, warm light.",
                })
            elif idx == 1:
                bad_prompts.append({
                    "slot_id": s["slot_id"],
                    "anchor_quote": "câu không hề có trong lời thoại",
                    "prompt": safe_prompt_for(s) + " (Pure visual footage/motion only, NO text)",
                })
            else:
                bad_prompts.append({
                    "slot_id": s["slot_id"],
                    "anchor_quote": s["anchor_quote"],
                    "prompt": "A founder walks into office transitions from chaos to calm.",
                })
        bad_path = out_dir / "prompts_bad.json"
        bad_path.write_text(json.dumps(bad_prompts, ensure_ascii=False, indent=2), encoding="utf-8")
        res_bad = run_cli(["check-prompts", "--plan", str(plan_json), "--prompts", str(bad_path)])
        assert res_bad.returncode == 1, f"Prompt lỗi mà vẫn PASS:\n{res_bad.stdout}"
        assert "[H5 FAIL]" in res_bad.stdout

        # --- Kiểm check-prompts: thiếu slot phải FAIL
        partial_path = out_dir / "prompts_partial.json"
        partial_path.write_text(
            json.dumps(
                [{"slot_id": broll_slots[0]["slot_id"], "anchor_quote": broll_slots[0]["anchor_quote"], "prompt": safe_prompt_for(broll_slots[0])}],
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        res_partial = run_cli(["check-prompts", "--plan", str(plan_json), "--prompts", str(partial_path)])
        assert res_partial.returncode == 1 and "thiếu prompt" in res_partial.stdout

        # --- Kiểm check-prompts: prompt sạch chuẩn H5 phải PASS
        good_prompts = [
            {
                "slot_id": s["slot_id"],
                "anchor_quote": s["anchor_quote"],
                "prompt": safe_prompt_for(s),
            }
            for s in broll_slots
        ]
        good_path = out_dir / "prompts_good.json"
        ready_path = out_dir / "flow_ready.json"
        good_path.write_text(json.dumps(good_prompts, ensure_ascii=False, indent=2), encoding="utf-8")
        res_good = run_cli([
            "check-prompts", "--plan", str(plan_json),
            "--prompts", str(good_path), "--out", str(ready_path),
        ])
        assert res_good.returncode == 0, f"Prompt sạch bị FAIL:\n{res_good.stdout}\n{res_good.stderr}"
        assert "[H5 OK]" in res_good.stdout and ready_path.is_file()

        ready = json.loads(ready_path.read_text(encoding="utf-8"))
        assert ready["total_jobs"] == len(broll_slots)
        assert ready["total_credits"] == plan["total_credits_x2"]
        assert ready["total_flow_seconds"] == sum(s["flow_seconds"] for s in broll_slots)
        for j in ready["jobs"]:
            assert j["model"] == "omni-flash"
            assert j["aspect_ratio"] == "9:16"
            assert j["upscale"] == "1080p"
            assert bf.SUFFIX_MARK not in j["prompt"]


def test_long_unpunctuated_run_split() -> None:
    """Đảm bảo văn bản dài không dấu chấm vẫn bị tách và không để đoạn A-ROLL nào > 8s."""
    long_text = (
        "Hôm nay mình chia sẻ cách tối ưu quy trình làm việc tại văn phòng để anh em không còn "
        "mất thời gian ngồi xử lý thủ công từng đơn hàng và bị quá tải mỗi cuối tuần nữa nhé "
        "bởi vì khi mọi thứ rõ ràng thì khách hàng phản hồi nhanh hơn rất nhiều"
    )
    tr = make_scribe_transcript([(long_text, 0.0, 26.0)])
    words = bfv.extract_words(tr)
    blocks = bfv.build_blocks(words, min_seg=3.0, max_seg=10.0)
    assert len(blocks) >= 3
    assert all(b["dur"] <= 10.05 for b in blocks), [b["dur"] for b in blocks]
    plan = bfv.plan_broll(blocks, min_coverage=0.25)
    assert plan["broll_pct"] >= 25.0
    assert plan["max_aroll_run_sec"] <= 8.0
    verify_max_aroll_run(plan["slots"], 8.0)


def main() -> None:
    test_analyze_45s()
    print("[OK] analyze_45s + check-prompts (FAIL vi phạm H5 & PASS prompt sạch)")
    test_long_unpunctuated_run_split()
    print("[OK] tách câu dài không dấu câu + giữ A-ROLL <= 8s & B-ROLL >= 25%")
    print("\nTẤT CẢ ĐẠT")


if __name__ == "__main__":
    main()
