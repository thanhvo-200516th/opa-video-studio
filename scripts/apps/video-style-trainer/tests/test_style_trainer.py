#!/usr/bin/env python3
"""Offline unit tests for video-style-trainer CLI (scripts/style_trainer.py)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

SKILL_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = SKILL_ROOT / "scripts" / "style_trainer.py"
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import style_trainer  # noqa: E402


def _make_synthetic_clip(dest: Path) -> None:
    """Create a 3-second 9:16 synthetic MP4 with a hard color cut at 1.5s and 440Hz audio."""
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=red:s=360x640:d=1.5",
        "-f",
        "lavfi",
        "-i",
        "color=c=blue:s=360x640:d=1.5",
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=440:duration=3.0",
        "-filter_complex",
        "[0:v][1:v]concat=n=2:v=1:a=0[v]",
        "-map",
        "[v]",
        "-map",
        "2:a",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        str(dest),
        "-loglevel",
        "error",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        raise RuntimeError(f"Failed to synthesize test video: {res.stderr}")


class TestStyleTrainerCLI(unittest.TestCase):
    def test_end_to_end_probe_scaffold_feedback_lint(self) -> None:
        with tempfile.TemporaryDirectory(prefix="vst_test_") as tmp:
            tmp_path = Path(tmp)
            clip_path = tmp_path / "sample_talking_head.mp4"
            _make_synthetic_clip(clip_path)

            # 1. probe (with contact sheet)
            probe_out = tmp_path / "probe_out"
            rc = style_trainer.main(["probe", str(clip_path), "--out", str(probe_out), "--fps", "1.0"])
            self.assertEqual(rc, 0)

            report_file = probe_out / "probe_report.json"
            summary_file = probe_out / "probe_summary.md"
            sheet_file = probe_out / "sample_talking_head_contact_sheet.jpg"
            self.assertTrue(report_file.is_file())
            self.assertTrue(summary_file.is_file())
            self.assertTrue(sheet_file.is_file())

            with Image.open(sheet_file) as im:
                self.assertGreater(im.width, 100)
                self.assertGreater(im.height, 100)

            report = json.loads(report_file.read_text(encoding="utf-8"))
            self.assertEqual(report["sample_count"], 1)
            self.assertEqual(report["sample_strategy"], "exact_clone_1_video")
            v0 = report["videos"][0]
            self.assertEqual(v0["aspect_ratio"], "9:16")
            self.assertGreaterEqual(v0["duration_sec"], 2.8)
            self.assertGreaterEqual(v0["pacing"]["cut_count"], 1)
            self.assertIsNotNone(v0["audio"]["integrated_lufs"])

            # probe --no-sheets on a directory with 2 videos -> common_pattern_multi_video
            clip2_path = tmp_path / "sample_2.mp4"
            clip2_path.write_bytes(clip_path.read_bytes())
            clips_dir = tmp_path / "clips_dir"
            clips_dir.mkdir()
            (clips_dir / "a.mp4").write_bytes(clip_path.read_bytes())
            (clips_dir / "b.mp4").write_bytes(clip2_path.read_bytes())
            probe_dir_out = tmp_path / "probe_dir_out"
            rc_dir = style_trainer.main(["probe", str(clips_dir), "--out", str(probe_dir_out), "--no-sheets"])
            self.assertEqual(rc_dir, 0)
            dir_report = json.loads((probe_dir_out / "probe_report.json").read_text(encoding="utf-8"))
            self.assertEqual(dir_report["sample_count"], 2)
            self.assertEqual(dir_report["sample_strategy"], "common_pattern_multi_video")
            self.assertIsNone(dir_report["videos"][0]["contact_sheet"])

            # 2. scaffold
            skills_root = tmp_path / "skills_out"
            rc_scaf = style_trainer.main(
                [
                    "scaffold",
                    "my-talking-head",
                    "--out",
                    str(skills_root),
                    "--preset",
                    "talking-head-ui-hyperframes",
                    "--engine",
                    "hyperframes",
                    "--probe",
                    str(report_file),
                ]
            )
            self.assertEqual(rc_scaf, 0)

            skill_dir = skills_root / "my-talking-head"
            for rel in (
                "SKILL.md",
                "config.json",
                "references/style-spec.md",
                "references/feedback-log.md",
                "templates/index.html",
                "templates/motion.css",
                "templates/edit.config.json",
                "assets/README.md",
            ):
                self.assertTrue((skill_dir / rel).is_file(), f"Missing scaffolded file: {rel}")

            cfg = json.loads((skill_dir / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(cfg["skill_name"], "my-talking-head")
            self.assertEqual(cfg["motion"]["easing"], "ease-in-out")
            self.assertTrue(cfg["face_safe_zone"]["enabled"])
            self.assertIn("measured_baseline", cfg)

            # 3. feedback (nested key updates + screenshot copy)
            shot_src = tmp_path / "overlap_issue.png"
            Image.new("RGB", (320, 568), (40, 60, 90)).save(shot_src)

            rc_fb2 = style_trainer.main(
                [
                    "feedback",
                    str(skill_dir),
                    "--round",
                    "2",
                    "--note",
                    "Cham motion chu lai cho de doc va ep ease-in-out",
                    "--set",
                    "motion.text_speed_scale=1.35",
                    "--set",
                    "motion.easing=ease-in-out",
                ]
            )
            self.assertEqual(rc_fb2, 0)

            rc_fb3 = style_trainer.main(
                [
                    "feedback",
                    str(skill_dir),
                    "--round",
                    "3",
                    "--note",
                    "Element de mat nguoi noi, tang co chu len",
                    "--screenshot",
                    str(shot_src),
                    "--set",
                    "typography.scale=1.25",
                ]
            )
            self.assertEqual(rc_fb3, 0)

            rc_fb4 = style_trainer.main(
                [
                    "feedback",
                    str(skill_dir),
                    "--round",
                    "4",
                    "--note",
                    "Them fake camera in/out trong 10s dau",
                    "--set",
                    "hook.fake_camera=true",
                    "--set",
                    "hook.hook_window_sec=10",
                ]
            )
            self.assertEqual(rc_fb4, 0)

            updated_cfg = json.loads((skill_dir / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(updated_cfg["motion"]["text_speed_scale"], 1.35)
            self.assertEqual(updated_cfg["text_speed_scale"], 1.35)
            self.assertEqual(updated_cfg["typography"]["scale"], 1.25)
            self.assertIs(updated_cfg["hook"]["fake_camera"], True)
            self.assertEqual(updated_cfg["feedback_rounds"], 4)

            # Check edit.config.json stayed synced
            edit_cfg = json.loads((skill_dir / "templates" / "edit.config.json").read_text(encoding="utf-8"))
            self.assertEqual(edit_cfg["typography"]["scale"], 1.25)

            copied_shot = skill_dir / "references" / "feedback_shots" / "round_3_overlap_issue.png"
            self.assertTrue(copied_shot.is_file())
            fb_log = (skill_dir / "references" / "feedback-log.md").read_text(encoding="utf-8")
            self.assertIn("references/feedback_shots/round_3_overlap_issue.png", fb_log)
            self.assertIn("motion.text_speed_scale", fb_log)

            # 4. lint-skill PASS on clean skill
            rc_lint_ok = style_trainer.main(["lint-skill", str(skill_dir)])
            self.assertEqual(rc_lint_ok, 0)

            # 5. lint-skill catches hardcoded Windows path D:\Kho_SFX
            (skill_dir / "templates" / "bad_paths.json").write_text(
                json.dumps({"sfx_dir": r"D:\Kho_SFX\whoosh.wav"}),
                encoding="utf-8",
            )
            rc_lint_win = style_trainer.main(["lint-skill", str(skill_dir)])
            self.assertEqual(rc_lint_win, 1)
            (skill_dir / "templates" / "bad_paths.json").unlink()

            # 6. lint-skill catches personal Unix home path
            (skill_dir / "templates" / "bad_unix.json").write_text(
                json.dumps({"font": "/home/someuser/fonts/inter.ttf"}),
                encoding="utf-8",
            )
            rc_lint_unix = style_trainer.main(["lint-skill", str(skill_dir)])
            self.assertEqual(rc_lint_unix, 1)
            (skill_dir / "templates" / "bad_unix.json").unlink()

            # 7. lint-skill catches nested SKILL.md inside templates/
            (skill_dir / "templates" / "SKILL.md").write_text("---\nname: nested\n---\n", encoding="utf-8")
            rc_lint_nested = style_trainer.main(["lint-skill", str(skill_dir)])
            self.assertEqual(rc_lint_nested, 1)
            (skill_dir / "templates" / "SKILL.md").unlink()

            # 8. lint-skill catches linear easing
            bad_cfg = json.loads((skill_dir / "config.json").read_text(encoding="utf-8"))
            bad_cfg["motion"]["easing"] = "linear"
            (skill_dir / "config.json").write_text(json.dumps(bad_cfg), encoding="utf-8")
            rc_lint_linear = style_trainer.main(["lint-skill", str(skill_dir)])
            self.assertEqual(rc_lint_linear, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
