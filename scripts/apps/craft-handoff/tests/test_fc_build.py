"""Tests for tools/fc_build.py.

Pure parts (validation, units, keyframes) run anywhere. The `craft` test drives a real FilmCraft on
CRAFT_DISPLAY (default :93) and builds examples/demo.craft.json; deselect it with `-m "not craft"`.
Run outputs land in pytest's tmp dir — pass `--basetemp DIR` to keep them somewhere specific.
"""

from __future__ import annotations

import json
import shutil
import sys
from fractions import Fraction
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "tools"))
import fc_build as fb  # noqa: E402

DEMO = SKILL / "examples" / "demo.craft.json"
T = fb.TICKS_PER_SECOND


@pytest.fixture
def media(tmp_path):
    for name in ("a.mp4", "b.png", "s.mp3"):
        (tmp_path / name).write_bytes(b"x")
    (tmp_path / "subs.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nHi\n\n2\n00:00:01,000 --> 00:00:02,000\nYo\n",
                                       encoding="utf-8")
    return tmp_path


@pytest.fixture
def spec(media):
    return {"name": "t", "width": 1080, "height": 1920, "fps": 25,
            "tracks": [{"type": "video", "name": "V1", "clips": [
                           {"src": str(media / "a.mp4"), "at": 0, "dur": 2,
                            "motion": {"scale": [[0, 100], [1, 110, "easeOut"]]}}]},
                       {"type": "text", "clips": [{"text": "Hi", "at": 0.5, "dur": 1, "color": "#FFFFFF"}]},
                       {"type": "audio", "clips": [{"src": str(media / "s.mp3"), "at": 1}]}],
            "captions": {"srt": str(media / "subs.srt")},
            "markers": [{"at": 1.0, "name": "m"}]}


def errors_of(spec) -> str:
    with pytest.raises(fb.SpecError) as exc:
        fb.validate(spec)
    return str(exc.value)


# ---------- units ---------------------------------------------------------------------------------

def test_ticks_per_frame_is_exact_for_common_rates():
    assert fb.frame_ticks(1, fb.fps_fraction(25)) == T // 25
    assert fb.fps_fraction(29.97) == Fraction(30000, 1001)
    assert fb.fps_fraction(23.976) == Fraction(24000, 1001)
    assert fb.frame_ticks(30, fb.fps_fraction(29.97)) == T * 1001 // 1000


def test_seconds_snap_to_nearest_frame_half_up():
    rate = fb.fps_fraction(25)
    assert fb.to_frames(0.4, rate) == 10
    assert fb.to_frames(0.35, rate) == 9           # 8.75 frames
    assert fb.to_frames(4.5, rate) == 113          # 112.5 rounds up
    assert fb.sec_ticks(3.85, rate) == 96 * T // 25
    assert fb.sec_ticks(0, rate) == 0


def test_media_time_follows_source_in_and_speed():
    info = {"start": 20 * T, "sourceIn": 20 * T, "speed": 2.0}
    assert fb.media_time(info, 21 * T) == 22 * T   # measured in FilmCraft: 1 s into a 200 % clip
    assert fb.media_time({"start": 4 * T, "sourceIn": 10 * T, "speed": 1.0}, 5 * T) == 11 * T


# ---------- keyframes -----------------------------------------------------------------------------

@pytest.mark.parametrize("value, animated", [
    (100, False), ([540, 960], False), ("#FFFFFF", False), ([], False),
    ([[0, 100], [0.4, 112, "bezier"]], True), ([[0, [540, 1100]], [0.5, [540, 960], "easeOut"]], True),
    ([[0, "#000000"], [1, "#FFFFFF"]], True)])
def test_is_animated(value, animated):
    assert fb.is_animated(value) is animated


def test_keyframes_default_to_linear_and_first_value():
    v = [[0, 80], [0.35, 100, "easeOut"]]
    assert fb.keyframes(v) == [(0, 80, "linear"), (0.35, 100, "easeOut")]
    assert fb.first_value(v) == 80 and fb.first_value(42) == 42


def test_every_spec_interpolation_maps_to_a_filmcraft_name():
    filmcraft = {"linear", "bezier", "autoBezier", "continuousBezier", "hold", "easeIn", "easeOut"}
    assert set(fb.INTERP) == {"linear", "bezier", "easeIn", "easeOut", "hold"}
    assert set(fb.INTERP.values()) <= filmcraft


def test_new_effect_indexes_finds_inserted_effects():
    before = ["motion", "opacity", "time_remap"]
    assert fb.new_effect_indexes(before, ["lumetri", "gaussian_blur", *before]) == [0, 1]
    assert fb.new_effect_indexes(["volume", "panner"], ["volume", "panner", "lowpass"]) == [2]
    assert fb.new_effect_indexes(before, before) == []


def test_match_preset():
    names = ["Fade In", "[DViet] Flash Out & Radial Blur Finisher", "[DViet] Flicker Strobe Visual Hook"]
    assert fb.match_preset("Fade In", names) == "Fade In"
    assert fb.match_preset("[DViet] Flash Out", names) == names[1]
    assert fb.match_preset("[dviet] f", names) is None           # ambiguous prefix
    assert fb.match_preset("Nope", names) is None


def test_track_labels_number_visual_and_audio_separately():
    tracks = [{"type": "video"}, {"type": "audio"}, {"type": "text"}, {"type": "audio"}]
    assert fb.track_labels(tracks) == ["V1", "A1", "V2", "A2"]


# ---------- validation ----------------------------------------------------------------------------

def test_demo_spec_is_valid():
    spec, unsupported = fb.load_spec(DEMO)
    assert unsupported == []
    assert fb.srt_cues(spec["captions"]["srt"]) == 3


def test_valid_spec_passes(spec):
    assert fb.validate(spec) == []


@pytest.mark.parametrize("key", ["name", "width", "height", "fps", "tracks"])
def test_missing_top_level_field_is_reported(spec, key):
    del spec[key]
    assert f"'{key}'" in errors_of(spec)


def test_relative_and_missing_paths_are_rejected(spec, media):
    spec["tracks"][0]["clips"][0]["src"] = "a.mp4"
    spec["tracks"][2]["clips"][0]["src"] = str(media / "missing.mp3")
    msg = errors_of(spec)
    assert "absolute path" in msg and "file not found" in msg


def test_bad_times_are_rejected(spec):
    clip = spec["tracks"][0]["clips"][0]
    clip.update(at=-1, dur=0)
    clip["motion"]["scale"] = [[0.5, 100], [0.2, 110], [3, 120]]
    msg = errors_of(spec)
    assert "'at'" in msg or ".at" in msg
    assert ".dur" in msg
    assert "increasing" in msg


def test_key_past_clip_end_and_bad_interpolation(spec):
    text = spec["tracks"][1]["clips"][0]
    text["opacity"] = [[0, 0], [2, 100, "smooth"]]
    msg = errors_of(spec)
    assert "past the clip end" in msg and "'smooth'" in msg


def test_bad_values_are_rejected(spec):
    text = spec["tracks"][1]["clips"][0]
    text.update(color="white", align="middle", position=[1, 2, 3])
    spec["tracks"][0]["clips"][0].update(blend="lighten", transition_in={"frames": 0}, audio_track="A9")
    msg = errors_of(spec)
    for needle in ("color", "align", "position", "blend", "transition_in", "A9"):
        assert needle in msg


def test_overlapping_clips_on_one_track_are_rejected(spec, media):
    spec["tracks"][0]["clips"].append({"src": str(media / "b.png"), "at": 1.5, "dur": 1})
    assert "overlaps" in errors_of(spec)


def test_unknown_keys_are_reported_not_dropped(spec):
    spec["tracks"][0]["clips"][0]["wiggle"] = 3
    spec["tracks"][0]["clips"][0]["motion"]["skew"] = 5
    spec["tracks"][2]["clips"][0]["opacity"] = 50          # audio clips have no opacity
    spec["extra"] = 1
    notes = " | ".join(fb.validate(spec))
    for needle in ("'wiggle'", "'skew'", "'opacity'", "'extra'"):
        assert needle in notes


def test_text_clip_needs_text(spec):
    del spec["tracks"][1]["clips"][0]["text"]
    assert "'text' is required" in errors_of(spec)


def test_cli_rejects_invalid_spec_with_exit_2(tmp_path, capsys):
    bad = tmp_path / "bad.craft.json"
    bad.write_text(json.dumps({"name": "x"}), encoding="utf-8")
    assert fb.main([str(bad), str(tmp_path / "out.fcproj")]) == 2
    assert "invalid spec" in capsys.readouterr().err


# ---------- integration: real FilmCraft -----------------------------------------------------------

def _filmcraft_available() -> bool:
    return (Path(fb.__file__).parent / "craftctl.py").exists() and (
        shutil.which("filmcraft") or Path("/home/vmiz/.local/bin/filmcraft").exists())


@pytest.mark.craft
@pytest.mark.skipif(not _filmcraft_available(), reason="FilmCraft is not installed")
def test_demo_builds_and_reopens_with_matching_counts(tmp_path):
    out, report_path = tmp_path / "demo.fcproj", tmp_path / "demo.report.json"
    code = fb.main([str(DEMO), str(out), "--report", str(report_path), "--frames", "2",
                    "--workdir", str(tmp_path / "work")])
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert code == 0, report["mismatches"]
    assert report["ok"] and report["mismatches"] == {} and report["unsupported"] == []
    assert report["actual"] == report["expected"]
    assert report["expected"] == {"video_tracks": 3, "audio_tracks": 2, "track_names": 5, "clips": 8,
                                  "linked_audio": 3, "track_items": 11, "keyframes": 19, "effects": 2,
                                  "text": 1, "transitions": 1, "captions": 3, "markers": 2}
    assert all(Path(f).stat().st_size > 0 for f in report["frames"]) and len(report["frames"]) == 2
    saved = json.loads(out.read_text(encoding="utf-8"))
    assert saved["format"] == "filmcraft.project" and saved["schema_version"] == 15



def test_keys_inside_one_frame_merge_last_wins():
    rate = fb.fps_fraction(30)
    keys = [[0.0, -63], [0.001, -23], [0.01, -3], [0.12, -3, "easeIn"], [0.2, -63]]
    assert fb.frame_keys(keys, rate) == [(0.01, -3, "linear"), (0.12, -3, "easeIn"), (0.2, -63, "linear")]


def test_touching_clips_stay_touching_after_frame_snap():
    """15.75 s + 0.55 s at 30 fps: rounding start (472.5) and length (16.5) apart gives 473 + 17 = 490 > 489."""
    rate = fb.fps_fraction(30)
    b = fb.Build.__new__(fb.Build)
    b.rate = rate
    assert fb.to_frames(15.75, rate) + b.span_frames(15.75, 0.55) == fb.to_frames(16.3, rate)
