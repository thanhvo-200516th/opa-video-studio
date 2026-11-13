"""Tests for tools/ec_build.py.

Pure parts (validation, time / keyframe conversion, effect mapping, SRT, fonts, plan, verification) run
anywhere. The `craft` test drives a real EffectCraft on CRAFT_DISPLAY and builds examples/demo.craft.json;
deselect it with `-m "not craft"`. Outputs land in pytest's tmp dir (`--basetemp DIR` keeps them).
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "tools"))
import ec_build as eb  # noqa: E402

DEMO = SKILL / "examples" / "demo.craft.json"
FAMILIES = [{"family": "Be Vietnam Pro", "styles": ["Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Italic"]},
            {"family": "Inter", "styles": ["Regular", "Medium", "SemiBold", "Bold", "Italic"]}]
COLOR_PARAMS = {"color", "creative/adjustments/shadowTint", "creative/adjustments/highlightTint"}


def fake_effect_list() -> list:
    """effect.list entries for every EffectCraft parameter the map uses (order = leaf index)."""
    effects = {}
    for ec_id, pmap in eb.EFFECTS.values():
        effects.setdefault(ec_id, []).extend(p for p in pmap.values() if p not in effects.get(ec_id, []))
    effects[eb.STROKE_FX] = list(eb.STROKE_PARAMS)
    return [{"id": ec_id, "params": [{"id": p, "name": p.split("/")[-1].title(),
                                      "type": "color" if p in COLOR_PARAMS else "scalar"} for p in params]}
            for ec_id, params in effects.items()]


@pytest.fixture
def media(tmp_path):
    for name in ("a.mp4", "b.png", "s.mp3"):
        (tmp_path / name).write_bytes(b"x")
    (tmp_path / "subs.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nHi\n\n2\n00:00:01,000 --> 00:00:02,000\nYo\n",
                                       encoding="utf-8")
    return tmp_path


@pytest.fixture
def probe(media):
    """What ec_build.js `probe` reports for the fixture files."""
    return {str(media / "a.mp4"): {"id": 1, "duration": 20.0, "width": 1080, "height": 1920, "hasVideo": True,
                                   "hasAudio": True, "still": False},
            str(media / "b.png"): {"id": 2, "duration": 0, "width": 1000, "height": 800, "hasVideo": True,
                                   "hasAudio": False, "still": True},
            str(media / "s.mp3"): {"id": 3, "duration": 1.5, "width": 0, "height": 0, "hasVideo": False,
                                   "hasAudio": True, "still": False}}


@pytest.fixture
def spec(media):
    return {"name": "t", "width": 1080, "height": 1920, "fps": 25,
            "tracks": [{"type": "video", "name": "V1", "clips": [
                           {"src": str(media / "a.mp4"), "name": "A", "at": 0, "dur": 2,
                            "motion": {"scale": [[0, 100], [1, 110, "easeOut"]]}},
                           {"src": str(media / "a.mp4"), "name": "B", "at": 2, "in": 5, "dur": 2,
                            "transition_in": {"effect": "cross_dissolve", "frames": 5},
                            "effects": [{"effect": "lumetri", "params": {"exposure": [[0, 0.6], [0.5, 0]]}}]}]},
                       {"type": "video", "name": "V2", "clips": [
                           {"src": str(media / "b.png"), "name": "P", "at": 1, "dur": 2, "motion": {"scale": 25},
                            "effects": [{"effect": "drop_shadow", "params": {"color": "#FF0000"}},
                                        {"effect": "rounded_crop", "params": {"left": 10, "right": 10, "radius": 20,
                                                                              "border": 4}},
                                        {"effect": "grow", "params": {}}]}]},
                       {"type": "text", "name": "T", "clips": [
                           {"text": "Xin chào", "at": 0.4, "dur": 2, "font": "Be Vietnam Pro", "style": "ExtraBold",
                            "size": 100, "color": "#FFD43B", "position": [540, 500],
                            "stroke": {"color": "#000000", "width": 6}}]},
                       {"type": "audio", "name": "A2", "clips": [
                           {"src": str(media / "s.mp3"), "at": 0.5, "gain_db": -8},
                           {"src": str(media / "s.mp3"), "at": 1.0}]}],
            "captions": {"srt": str(media / "subs.srt")},
            "markers": [{"at": 2.0, "name": "Cut", "comment": "B"}]}


def make_plan(spec, probe):
    planner = eb.Plan(spec, probe, FAMILIES, eb.index_effects(fake_effect_list()))
    return planner.make(eb.parse_srt(Path(spec["captions"]["srt"]).read_text(encoding="utf-8"))), planner.notes


def by_name(plan) -> dict:
    return {L["name"]: L for L in plan["layers"]}


# ---------------------------------------------------------------- validation

def test_demo_spec_is_valid():
    spec = json.loads(DEMO.read_text(encoding="utf-8"))
    if not Path(spec["tracks"][0]["clips"][0]["src"]).exists():
        pytest.skip("demo media not on this machine")
    assert eb.validate(spec) == []


def test_fixture_spec_is_valid(spec):
    assert eb.validate(spec) == []


@pytest.mark.parametrize("key, message", [("name", "name:"), ("width", "width, height"), ("fps", "fps:"),
                                          ("tracks", "tracks:")])
def test_missing_top_level_field(spec, key, message):
    del spec[key]
    assert any(message in e for e in eb.validate(spec))


@pytest.mark.parametrize("change, message", [
    ({"src": "relative.mp4"}, "absolute path"),
    ({"src": "/no/such/file.mp4"}, "source file not found"),
    ({"at": -1}, "'at'"),
    ({"dur": 0}, "'dur' must be > 0"),
    ({"speed": 0}, "'speed'"),
    ({"blend": "dodge"}, "blend must be"),
    ({"opacity": [[0, 0], [0, 100]]}, "increasing"),
    ({"motion": {"scale": [[0, 100, "smooth"]]}}, "interpolation 'smooth'"),
    ({"motion": {"position": [1, 2, 3]}}, "bad value"),
    ({"transition_in": {"effect": "cross_dissolve", "frames": 0}}, "transition_in"),
    ({"effects": [{"params": {}}]}, "effects entries"),
])
def test_bad_media_clip_is_reported(spec, change, message):
    spec["tracks"][0]["clips"][0].update(change)
    errs = eb.validate(spec)
    assert any(message in e for e in errs), errs
    assert all(e.startswith("tracks[0] 'V1' clip 1 (A)") for e in errs)


def test_text_clip_needs_text_but_not_dur(spec):
    clip = spec["tracks"][2]["clips"][0]
    del clip["dur"]
    assert eb.validate(spec) == []
    clip["text"] = " "
    assert any("'text' is required" in e for e in eb.validate(spec))


def test_overlapping_clips_on_one_track_are_rejected(spec):
    spec["tracks"][0]["clips"][0]["dur"] = 3
    assert any("clip 1 overlaps clip 2" in e for e in eb.validate(spec))


def test_bad_captions_and_markers(spec):
    spec["captions"] = {"srt": "subs.srt"}
    spec["markers"] = [{"name": "no time"}]
    errs = eb.validate(spec)
    assert any(e.startswith("captions.srt") for e in errs) and any(e.startswith("markers[0]") for e in errs)


def test_load_spec_lists_every_problem(tmp_path):
    bad = tmp_path / "bad.craft.json"
    bad.write_text(json.dumps({"name": "", "width": 0, "fps": 25, "tracks": []}), encoding="utf-8")
    with pytest.raises(eb.SpecError) as e:
        eb.load_spec(str(bad))
    assert "name:" in str(e.value) and "width, height" in str(e.value) and "tracks:" in str(e.value)
    bad.write_text("{oops", encoding="utf-8")
    with pytest.raises(eb.SpecError, match="invalid JSON at line 1"):
        eb.load_spec(str(bad))


# ---------------------------------------------------------------- time and keyframes

@pytest.mark.parametrize("t, fps, want", [(4.5, 25, 4.52), (3.85, 25, 3.84), (0.3, 25, 0.32), (1.234, 30, 37 / 30)])
def test_snap_rounds_to_the_nearest_frame(t, fps, want):
    assert eb.snap(t, fps) == pytest.approx(want)


@pytest.mark.parametrize("interp, sides", [("linear", ("linear", "linear")), ("bezier", ("ease", "ease")),
                                           ("easeIn", ("ease", "linear")), ("easeOut", ("linear", "ease")),
                                           ("hold", ("linear", "hold"))])
def test_interpolation_sits_on_its_own_key(interp, sides):
    keys = eb.to_keys([[0, 1], [1, 2, interp]], at=2.0, fps=25)
    assert (keys[1]["in"], keys[1]["out"]) == sides
    assert (keys[0]["in"], keys[0]["out"]) == ("linear", "linear")


def test_keys_are_clip_relative_and_snapped():
    keys = eb.to_keys([[0, [540, 2100]], [0.41, [540, 1500]]], at=4.5, fps=25)
    assert [k["t"] for k in keys] == pytest.approx([4.52, 4.92])
    assert keys[1]["v"] == [540, 1500]


def test_keys_inside_one_frame_merge_onto_whole_frames():
    notes = []
    fade = [[0, -60], [0.001, -40], [0.003, -20], [0.01, -3.2], [0.12, -3.2], [0.2, -60]]
    keys = eb.to_keys(fade, at=1.0, fps=30, where="sfx gain_db", notes=notes)
    assert [(round(k["t"] * 30), k["v"]) for k in keys] == [(30, -60), (31, -3.2), (34, -3.2), (36, -60)]
    assert notes == ["sfx gain_db: 3 key(s) closer than one frame — merged onto whole frames"]


def test_animated_constant_and_scale():
    assert eb.animated(25, 0, 25, eb.as_scale) == {"value": [25, 25]}
    assert eb.animated([[0, 80], [0.4, 100]], 1, 25, eb.as_scale)["keys"][1]["v"] == [100, 100]
    assert eb.is_keyed([[0, 1]]) and not eb.is_keyed([540, 960]) and not eb.is_keyed("#fff")


def test_colours():
    assert eb.rgb("#FF8000") == pytest.approx([1.0, 128 / 255, 0.0])
    assert eb.rgba([1, 1, 1, 0.5]) == [1.0, 1.0, 1.0, 0.5]
    assert eb.rgba("#000000")[3] == 1.0
    with pytest.raises(eb.SpecError):
        eb.rgb("red")


# ---------------------------------------------------------------- SRT

def test_parse_srt_handles_bom_crlf_tags_and_lines():
    text = "﻿1\r\n00:00:00,300 --> 00:00:02,000\r\n<i>Tư duy</i> AI\r\nhai dòng\r\n\r\n2\r\n00:01:02.5 --> 00:01:03,000\r\nB\r\n"
    assert eb.parse_srt(text) == [(0.3, 2.0, "Tư duy AI\nhai dòng"), (62.5, 63.0, "B")]


def test_parse_demo_srt():
    cues = eb.parse_srt((SKILL / "examples" / "demo.srt").read_text(encoding="utf-8"))
    assert [c[:2] for c in cues] == [(0.3, 2.0), (2.0, 4.0), (4.2, 7.8)]


@pytest.mark.parametrize("text, message", [("1\n00:00:01,000 --> 00:00:00,500\nx\n", "ends before"),
                                           ("1\nno time here\n", "without a time line"),
                                           ("1\n00:00 --> 00:00:01,000\nx\n", "bad SRT time")])
def test_parse_srt_errors(text, message):
    with pytest.raises(eb.SpecError, match=message):
        eb.parse_srt(text)


# ---------------------------------------------------------------- fonts

@pytest.mark.parametrize("family, style, want, fallback", [
    ("Be Vietnam Pro", "ExtraBold", ("Be Vietnam Pro", "ExtraBold"), False),
    ("be vietnam pro", "bold", ("Be Vietnam Pro", "Bold"), False),
    ("Be Vietnam Pro", "Black", ("Be Vietnam Pro", "ExtraBold"), True),
    ("Be Vietnam Pro", "Thin", ("Be Vietnam Pro", "Regular"), True),
    ("Be Vietnam Pro", "Bold Italic", ("Be Vietnam Pro", "Italic"), True),
    ("No Such Font", "Black", ("Inter", "Bold"), True),
])
def test_resolve_font(family, style, want, fallback):
    fam, sty, why = eb.resolve_font(family, style, FAMILIES)
    assert (fam, sty) == want and (why is not None) == fallback


# ---------------------------------------------------------------- effect mapping and plan

def test_index_effects_counts_leaves_from_one():
    idx = eb.index_effects([{"id": "fx", "params": [{"id": "a"}, {"id": "g/b"}]}])
    assert idx["fx"]["g/b"][0] == 2


def test_rounded_rect_path():
    p = eb.rounded_rect(10, 20, 110, 220, 20)
    xs, ys = [v[0] for v in p["vertices"]], [v[1] for v in p["vertices"]]
    assert len(xs) == 8 and (min(xs), max(xs), min(ys), max(ys)) == (10, 110, 20, 220)
    assert p["inTangents"][0] == [pytest.approx(-0.5523 * 20), 0]
    assert len(eb.rounded_rect(0, 0, 10, 10, 0)["vertices"]) == 4


def test_plan_stacks_audio_then_tracks_then_captions(spec, probe):
    plan, _ = make_plan(spec, probe)
    assert [L["name"] for L in plan["layers"]] == ["s.mp3", "s.mp3", "A", "B", "P", "Xin chào", "CC 01 Hi", "CC 02 Yo"]
    assert [L["kind"] for L in plan["layers"]] == ["audio"] * 2 + ["footage"] * 3 + ["text"] * 3
    assert plan["comp"] == {"name": "t", "width": 1080, "height": 1920, "fps": 25, "duration": 4.0}
    assert plan["markers"] == [{"time": 2.0, "comment": "Cut: B"}]


def test_plan_media_timing_and_trim_to_next_clip(spec, probe):
    plan, notes = make_plan(spec, probe)
    L = by_name(plan)
    assert (L["B"]["in"], L["B"]["out"], L["B"]["start"]) == (2.0, 4.0, -3.0)
    sfx = [x for x in plan["layers"] if x["kind"] == "audio"]
    assert (sfx[0]["in"], sfx[0]["out"]) == (0.52, 1.0)         # trimmed at the next clip, no overlap
    assert (sfx[1]["in"], sfx[1]["out"]) == (1.0, 2.52)         # natural length (1.5 s), last on its track
    assert sfx[0]["props"] == [{"path": "levels", "value": [-8, -8]}]
    assert any("trimmed to 0.50s" in w for w in notes["warnings"])


def test_plan_speed_sets_stretch_and_start(spec, probe):
    spec["tracks"][0]["clips"][1].update(speed=200)
    L = by_name(make_plan(spec, probe)[0])["B"]
    assert (L["stretch"], L["start"]) == (50.0, eb.snap(2.0 - 5 * 0.5, 25))


def test_plan_rejects_clips_longer_than_their_source(spec, probe):
    spec["tracks"][0]["clips"][1].update(**{"in": 19, "dur": 2})
    with pytest.raises(eb.SpecError, match="the file is 20.00s long"):
        make_plan(spec, probe)


def test_cross_dissolve_extends_the_clip_before_and_cuts_its_sound(spec, probe):
    plan, notes = make_plan(spec, probe)
    L = by_name(plan)
    fade = next(p for p in L["B"]["props"] if p["path"] == "opacity")
    assert [(k["t"], k["v"]) for k in fade["keys"]] == [(2.0, 0), (2.2, 100)]
    assert L["A"]["out"] == pytest.approx(2.2)
    levels = next(p for p in L["A"]["props"] if p["path"] == "levels")
    assert [(k["t"], k["v"][0], k["out"]) for k in levels["keys"]] == [(1.96, 0, "hold"), (2.0, eb.SILENT_DB, "linear")]
    assert any("A: cross dissolve — out point extended 5 frames" in a for a in notes["approximations"])


def test_unknown_transition_is_reported(spec, probe):
    spec["tracks"][0]["clips"][1]["transition_in"] = {"effect": "push", "frames": 5}
    _, notes = make_plan(spec, probe)
    assert "V1 / B: transition_in push — only cross_dissolve maps (to opacity keys)" in notes["unsupported"]


def test_effects_map_to_effectcraft_parameters(spec, probe):
    plan, notes = make_plan(spec, probe)
    L = by_name(plan)
    lum = L["B"]["effects"][0]
    assert lum["ec"] == "ec.color.lumetri" and lum["params"][0]["name"] == "Exposure"
    assert [(k["t"], k["v"]) for k in lum["params"][0]["keys"]] == [(2.0, 0.6), (2.52, 0)]
    shadow, stroke = L["P"]["effects"]
    assert shadow["ec"] == "ec.perspective.dropshadow" and shadow["params"][0]["value"] == [1.0, 0.0, 0.0, 1.0]
    assert stroke["ec"] == eb.STROKE_FX and [p["value"] for p in stroke["params"]][0::2] == [1, 4]
    assert len(L["P"]["masks"]) == 1 and L["P"]["masks"][0]["vertices"][0] == [100 + 20, 0]
    assert notes["unsupported"] == ["V2 / P: effect grow — no EffectCraft mapping (references/effect-map.md)"]


def test_unknown_effect_parameters_and_switches(spec, probe):
    spec["tracks"][0]["clips"][1]["effects"] = [{"effect": "lumetri", "params": {
        "basic_on": True, "creative_on": False, "look_lut": "x", "saturation": 50}}]
    plan, notes = make_plan(spec, probe)
    assert [u.split(" — ")[0] for u in notes["unsupported"] if "lumetri" in u] == [
        "V1 / B: lumetri.creative_on=false", "V1 / B: lumetri.look_lut"]
    assert by_name(plan)["B"]["effects"][0]["params"][0]["value"] == 50


def test_text_layer(spec, probe):
    spec["tracks"][2]["clips"][0].update(shadow={"opacity": 50, "blur": 8}, color=[[0, "#FF0000"], [1, "#00FF00"]])
    plan, notes = make_plan(spec, probe)
    L = by_name(plan)["Xin chào"]
    assert L["text"]["font"] == "Be Vietnam Pro" and L["text"]["style"] == "ExtraBold"
    assert L["text"]["stroke"]["width"] == 12 and L["text"]["fill"] == [1.0, 0.0, 0.0]
    assert {"path": "position", "value": [540, 500]} in L["props"]
    assert L["effects"][0]["ec"] == "ec.perspective.dropshadow"
    assert any(u.startswith("T / Xin chào: animated color") for u in notes["unsupported"])


def test_keyed_gain_becomes_audio_level_keys(spec, probe):
    spec["tracks"][3]["clips"][0]["gain_db"] = [[0, -60], [0.04, -3], [0.4, -60]]
    sfx = make_plan(spec, probe)[0]["layers"][0]
    assert sfx["props"] == [{"path": "levels", "keys": [
        {"t": 0.52, "v": [-60, -60], "in": "linear", "out": "linear"},
        {"t": 0.56, "v": [-3, -3], "in": "linear", "out": "linear"},
        {"t": 0.92, "v": [-60, -60], "in": "linear", "out": "linear"}]}]


def test_adapter_notes_and_unsupported_reach_the_report(spec, probe):
    spec["notes"] = ["converted from X"]
    spec["unsupported"] = [{"what": "film grain", "why": "no effect", "where": "whole video"}, "plain line"]
    notes = make_plan(spec, probe)[1]
    assert notes["spec"] == ["converted from X"]
    assert notes["unsupported"][:2] == ["whole video: film grain — no effect", "plain line"]


def test_captions_wrap_and_sit_on_their_last_line(spec, probe):
    Path(spec["captions"]["srt"]).write_text("1\n00:00:00,000 --> 00:00:01,000\n" + "chữ " * 30 + "\n",
                                             encoding="utf-8")
    plan, _ = make_plan(spec, probe)
    cap = plan["layers"][-1]
    lines = cap["text"]["str"].split("\r")
    assert len(lines) > 1 and cap["caption"] and cap["comment"] == "captions subs.srt"
    pos = next(p for p in cap["props"] if p["path"] == "position")["value"]
    assert pos[1] == pytest.approx(1920 * eb.CAPTION_Y - (len(lines) - 1) * 1.2 * 64)


# ---------------------------------------------------------------- verification

def as_dump(plan) -> dict:
    """A dump that matches the plan exactly (what ec_build.js reads back from a faithful project)."""
    fps = plan["comp"]["fps"]
    layers = [{**eb.plan_sig(L, fps), "comment": L["comment"], "effects": []} for L in plan["layers"]][::-1]
    return {"comp": dict(plan["comp"]), "comps": 1, "layers": layers, "markers": [dict(m) for m in plan["markers"]]}


def test_compare_accepts_a_faithful_project(spec, probe):
    plan, _ = make_plan(spec, probe)
    bad, expected, found = eb.compare(plan, as_dump(plan))
    assert bad == [] and expected == found
    assert expected == {"layers": 8, "footage": 3, "text": 3, "audio": 2, "captions": 2, "keyframes": 8,
                        "effects": 3, "masks": 1, "markers": 1}


def test_compare_reports_what_differs(spec, probe):
    plan, _ = make_plan(spec, probe)
    dump = as_dump(plan)
    dump["comp"]["width"] = 720
    dump["markers"] = []
    del dump["layers"][3]                                  # "P"
    dump["layers"][-1]["keys"]["levels"] = [99]           # bottom SFX
    bad, _, found = eb.compare(plan, dump)
    assert "comp width: 720, expected 1080" in bad
    assert "layer 'P' (footage) is missing or out of stacking order" in bad
    assert any(b.startswith("layer 's.mp3': keys") for b in bad)
    assert any(b.startswith("markers") for b in bad) and found["layers"] == 7


# ---------------------------------------------------------------- the real app

def _effectcraft_available() -> bool:
    return bool(shutil.which("effectcraft")) or Path("/home/vmiz/.local/bin/effectcraft").exists()


@pytest.mark.craft
@pytest.mark.skipif(not _effectcraft_available(), reason="EffectCraft is not installed")
def test_build_demo_in_effectcraft(tmp_path, capsys):
    spec = json.loads(DEMO.read_text(encoding="utf-8"))
    if not Path(spec["tracks"][0]["clips"][0]["src"]).exists():
        pytest.skip("demo media not on this machine")
    out, report = tmp_path / "demo.ecproj", tmp_path / "demo.ec-report.json"
    code = eb.main([str(DEMO), str(out), "--report", str(report), "--frames", "2", "--workdir", str(tmp_path / "w")])
    rep = json.loads(report.read_text(encoding="utf-8"))
    assert code == 0, rep["mismatches"]
    assert rep["ok"] and rep["mismatches"] == [] and rep["unsupported"] == []
    assert rep["comp"] == {"name": "craft-handoff demo", "width": 1080, "height": 1920, "fps": 25, "duration": 12}
    assert rep["counts"]["found"] == {"layers": 11, "footage": 4, "text": 4, "audio": 3, "captions": 3,
                                      "keyframes": 23, "effects": 2, "masks": 0, "markers": 2}
    assert all(Path(p).stat().st_size > 0 for p in rep["qa_frames"]) and len(rep["qa_frames"]) == 2
    saved = json.loads(out.read_text(encoding="utf-8"))
    assert saved["savedBy"].startswith("0.17") and str(tmp_path / "w") not in out.read_text(encoding="utf-8")
