"""Tests of tools/adapters/th_to_craft.py on the dung-video-talking-head repo fixtures.

Two throw-away projects are assembled under tmp_path from read-only repo fixtures plus ffmpeg dummies
(the real HeyGen master / B-roll / voice are not on this machine):
  * v16 — tests/fixtures/v16: picture lock + SFX plan + meta of the same video (built with release 1.1.0,
    whose SFX manifest the plan's file keys belong to);
  * v2b — tests/fixtures/broll_v2_b13/picture_lock.json: video 02 with hook, stomp heroes, bottom lines,
    a step card, CTA and four B-roll slots (one clip, three stills); no SFX, a BGM bed.
Run: /home/vmiz/.hermes/shared-skills/video/dung-video-talking-head/.venv/bin/python -m pytest <this file>
"""
from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ADAPTERS = Path(__file__).resolve().parents[1] / "tools" / "adapters"
sys.path.insert(0, str(ADAPTERS))
import th_to_craft as tc  # noqa: E402

FIX = tc.SKILL_ROOT / "tests" / "fixtures"
K = 1080 / 1620                       # master 1620x2880 cover-fit into 1080x1920
SRT_TIME = r"(\d\d):(\d\d):(\d\d),(\d\d\d)"


def _ff(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *map(str, args)], check=True)


@pytest.fixture(scope="session")
def media(tmp_path_factory):
    d = tmp_path_factory.mktemp("media")
    _ff("-f", "lavfi", "-i", "color=c=gray:s=1620x2880:r=30", "-t", 45, "-c:v", "libx264", "-preset", "ultrafast",
        "-tune", "stillimage", "-pix_fmt", "yuv420p", d / "master.mp4")
    _ff("-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", 0.5, d / "silence.wav")
    _ff("-f", "lavfi", "-i", "sine=frequency=220:sample_rate=48000", "-t", 2, d / "bed.wav")
    _ff("-f", "lavfi", "-i", "color=c=blue:s=720x1280", "-frames:v", 1, d / "still.jpg")
    _ff("-f", "lavfi", "-i", "color=c=red:s=720x1280:r=24", "-t", 3, "-c:v", "libx264", "-preset", "ultrafast",
        "-pix_fmt", "yuv420p", d / "clip.mp4")
    return d


def _project(root: Path, media: Path, lock: Path, plan: Path | None, version: str, meta: dict, bgm: bool) -> Path:
    p = root / str(meta["video"]) / f"edit-r{version}"
    (p / "out").mkdir(parents=True)
    pub = p / "public"
    pub.mkdir()
    shutil.copy(lock, p / "picture_lock.json")
    if plan is None:
        (p / "out" / "sfx_plan.json").write_text('{"cues": []}', encoding="utf-8")
    else:
        shutil.copy(plan, p / "out" / "sfx_plan.json")
    (p / "rules.lock").write_text(json.dumps({"skill": "dung-video-talking-head", "version": version}), encoding="utf-8")
    (p / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    shutil.copy(media / "master.mp4", pub / "master.mp4")
    shutil.copy(media / "silence.wav", pub / "vo-clean.wav")
    shutil.copy(media / "silence.wav", pub / "sfx_stem.wav")
    if bgm:
        shutil.copy(media / "bed.wav", pub / "bgm_bed.wav")
    for b in json.loads(lock.read_text(encoding="utf-8")).get("broll") or []:
        (pub / b["file"]).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(media / ("clip.mp4" if b["media"] == "clip" else "still.jpg"), pub / b["file"])
    return p


def _convert(project: Path, out_dir: Path) -> dict:
    spec = tc.convert(project, out_dir / "out.craft.json", captions=True)
    return {"project": project, "spec": spec, "lock": json.loads((project / "picture_lock.json").read_text("utf-8")),
            "plan": json.loads((project / "out" / "sfx_plan.json").read_text("utf-8")),
            "srt": Path(spec["captions"]["srt"]).read_text(encoding="utf-8")}


@pytest.fixture(scope="module")
def v16(tmp_path_factory, media):
    root = tmp_path_factory.mktemp("v16")
    meta = json.loads((FIX / "v16" / "meta.json").read_text(encoding="utf-8"))
    project = _project(root, media, FIX / "v16" / "picture_lock_canary.json", FIX / "v16" / "sfx_plan_canary.json",
                       meta["rules_version"], meta, bgm=False)
    return _convert(project, root)


@pytest.fixture(scope="module")
def v2b(tmp_path_factory, media):
    root = tmp_path_factory.mktemp("v2b")
    project = _project(root, media, FIX / "broll_v2_b13" / "picture_lock.json", None, "1.2.6", {"video": 2}, bgm=True)
    return _convert(project, root)


def _track(spec: dict, name: str) -> list:
    return [c for t in spec["tracks"] if t["name"] == name or t["name"].startswith(name + " ") for c in t["clips"]]


def _by_name(clips: list, name: str) -> dict:
    return next(c for c in clips if c["name"] == name)


# ------------------------------------------------------------------ cuts and zoom

def test_one_aroll_clip_per_shot_on_the_frame_the_template_cuts(v16):
    shots, fps, aroll = v16["lock"]["shots"], v16["lock"]["fps"], _track(v16["spec"], "A-roll")
    assert len(aroll) == len(shots) == 15
    for clip, shot in zip(aroll, shots):
        assert clip["at"] == round(math.ceil(shot["t"] * fps - 1e-6) / fps, 4)
        assert clip["in"] == clip["at"] and clip["audio"] is False
        assert clip["src"] == str((v16["project"] / "public" / "master.mp4").resolve())
    for a, b in zip(aroll, aroll[1:]):
        assert a["at"] + a["dur"] == pytest.approx(b["at"], abs=1e-6)
    assert aroll[-1]["at"] + aroll[-1]["dur"] == pytest.approx(v16["lock"]["duration_f"] / fps, abs=1e-4)
    assert v16["spec"]["duration"] == pytest.approx(v16["lock"]["duration_f"] / fps, abs=1e-4)


def test_zoom_push_and_cut_bump_are_scale_and_position_keys(v16):
    s0, s1 = _track(v16["spec"], "A-roll")[:2]
    assert s0["motion"]["scale"] == [[0.0, round(100 * K, 3), "easeOut"], [s0["dur"], round(100 * K * 1.04, 3), "easeIn"]]
    assert s0["motion"]["position"] == [[0.0, [540.0, 960.0], "easeOut"], [s0["dur"], [540.0, 973.8], "easeIn"]]
    scale = s1["motion"]["scale"]                 # shot 2: 1.16 -> 1.2 with the +1.8 % cut bump over 5 frames
    assert [k[0] for k in scale] == [0.0, round(5 / 30, 4), s1["dur"]]
    assert scale[0][1] == round(100 * K * (1.16 + 0.018), 3)
    assert scale[-1] == [s1["dur"], round(100 * K * 1.2, 3), "easeIn"]
    assert len(s1["motion"]["position"]) == 3


def test_shot_offset_moves_the_position(v2b):
    shot = v2b["lock"]["shots"][5]
    assert (shot["s0"], shot["y"]) == (1.18, -0.0864)
    clip = _track(v2b["spec"], "A-roll")[5]
    y = 0.32 * 1920 + shot["y"] * 1920 + (1.18 + 0.018) * (960 - 0.32 * 1920)
    assert clip["motion"]["position"][0][1] == [540.0, pytest.approx(y, abs=0.1)]


# ------------------------------------------------------------------ B-roll

def test_broll_slots_become_cover_fitted_clips(v2b):
    slots, clips = v2b["lock"]["broll"], _track(v2b["spec"], "B-roll")
    assert len(clips) == len(slots) == 4
    for clip, b in zip(clips, slots):
        assert clip["at"] == round(b["f_in"] / 30, 4) and clip["dur"] == round((b["f_out"] - b["f_in"]) / 30, 4)
        assert clip["motion"]["position"] == [540.0, 960.0]
    clip, still = clips[0], clips[1]                  # 720x1280 dummies -> cover factor 1.5
    assert clip["audio"] is False and clip["in"] == 0.0 and clip["motion"]["scale"] == 150.0
    keys, n = still["motion"]["scale"], slots[1]["f_out"] - slots[1]["f_in"]
    assert keys[0] == [0.0, round(150 * 1.018, 3)]
    assert keys[-1] == [round((n - 1) / 30, 4), round(150 * 1.06, 3), "easeIn"]


# ------------------------------------------------------------------ SFX and other audio

def test_every_sfx_cue_is_a_clip_at_its_time_and_gain(v16):
    cues, clips = v16["plan"]["cues"], _track(v16["spec"], "SFX")
    manifest = json.loads((tc.SKILL_ROOT / "releases" / "1.1.0" / "sfx_manifest.json").read_text("utf-8"))["files"]
    assert len(clips) == len(cues) == 9
    for clip, cue in zip(clips, cues):
        assert clip["at"] == round(cue["start_s"], 4)
        assert clip["dur"] == pytest.approx(cue["end_s"] - cue["start_s"], abs=1e-4)
        assert clip["in"] == pytest.approx(manifest[cue["file"]]["lag_ms"] / 1000 - (cue["peak_s"] - cue["start_s"]),
                                           abs=3 / 48000)
        gains = [k[1] for k in clip["gain_db"]] if isinstance(clip["gain_db"], list) else [clip["gain_db"]]
        assert max(gains) == round(cue["gain_db"], 2) and min(gains) >= round(cue["gain_db"], 2) - 60
        assert clip["src"].startswith(str(tc.SKILL_ROOT / "releases" / "1.1.0" / "sfx")) and Path(clip["src"]).is_file()


def test_audio_tracks_voice_first_then_bgm(v2b):
    audio = [t["name"] for t in v2b["spec"]["tracks"] if t["type"] == "audio"]
    assert audio == ["Voice", "BGM"]                 # no cues in this plan -> no SFX track
    voice, = _track(v2b["spec"], "Voice")
    assert voice["src"].endswith("public/vo-clean.wav") and voice["dur"] == v2b["spec"]["duration"]
    assert voice["gain_db"][-1] == [voice["dur"], -60]          # 0.15 s master end fade
    bgm, = _track(v2b["spec"], "BGM")
    assert bgm["src"].endswith("public/bgm_bed.wav") and bgm["at"] == 0.0


# ------------------------------------------------------------------ text

TEXT_FIELDS = ("text", "at", "dur", "font", "style", "size", "color", "align", "position")


def test_text_clips_have_the_template_styles(v2b):
    spec, lock = v2b["spec"], v2b["lock"]
    texts = [c for t in spec["tracks"] if t["type"] == "text" for c in t["clips"]]
    for c in texts:
        assert all(f in c for f in TEXT_FIELDS), c["name"]
        assert re.fullmatch(r"#[0-9a-f]{6}", c["color"]) and c["dur"] > 0
        assert 0 <= c["position"][0] <= 1080 and 0 <= c["position"][1] <= 1920
    hook, = _track(spec, "Hook")
    bebas = 4 * 0.43 + 0.43 + 0.16                   # "20 LẦN": five glyphs + one space (anim.ts bebasEm)
    assert (hook["text"], hook["font"], hook["color"], hook["at"], hook["dur"]) == ("20 LẦN", "PS Bebas Neue", "#ff5d73", 0.0, 1.5)
    assert hook["size"] == round(min(460, 800 / (1.05 * bebas)), 1)
    assert hook["motion"]["scale"][0] == [0.0, 134]
    heroes = _track(spec, "Hero")
    assert len(heroes) == len(lock["blocks"])
    b2 = _by_name(heroes, "b2 hero")                 # stomp/warn: DT Phudu Black, upper case, solid colour
    assert (b2["text"], b2["font"], b2["style"], b2["color"], b2["size"]) == ("20 LẦN", "DT Phudu", "Black", "#ff5d73", 176.0)
    b1 = _by_name(heroes, "b1 hero")
    assert (b1["font"], b1["color"], b1["at"]) == ("TF Youth Shandey", "#d7ccff", lock["blocks"][0]["hero"][0]["show"])
    for c in _track(spec, "Sub top") + heroes + _track(spec, "Sub bottom"):
        assert c["position"][1] <= lock["safe"]["text_y_max"]      # stacked above the bottom of the text box
    top = _by_name(_track(spec, "Sub top"), "b1 top")
    assert (top["text"], top["font"], top["style"], top["color"]) == ("Một shop nhỏ", "Be Vietnam Pro", "Medium", "#ffffff")
    assert top["position"][1] < b1["position"][1]


def test_cta_and_step_card_texts(v2b):
    spec, lock = v2b["spec"], v2b["lock"]
    label, = _track(spec, "CTA label")
    kw, = _track(spec, "CTA keyword")
    assert label["text"] == "👇 Bình luận" and kw["text"] == "5 TÀI SẢN" and kw["color"] == "#ffcf6b"
    assert label["at"] == kw["at"] == lock["cta"]["show"]
    assert label["at"] + label["dur"] == pytest.approx(spec["duration"], abs=1e-4)
    assert label["position"][0] < kw["position"][0] and label["align"] == "right" and kw["align"] == "left"
    steps = _track(spec, "Steps")
    st = lock["steps"]
    assert [c["text"] for c in steps] == [st["title"]] + [f"0{i + 1}  {it['label']}" for i, it in enumerate(st["items"])]
    assert [c["at"] for c in steps] == [st["in"]] + [it["show"] for it in st["items"]]
    assert [c["position"][1] for c in steps] == sorted(c["position"][1] for c in steps)
    assert [k[1] for k in steps[1]["opacity"]] == [0, 100, 100, 46, 46, 0]   # dims when item 2 starts


# ------------------------------------------------------------------ captions, paths, unsupported

def _srt_cues(text: str) -> list:
    cues = []
    for i, chunk in enumerate(text.strip().split("\n\n"), 1):
        num, times, *lines = chunk.split("\n")
        m = re.fullmatch(SRT_TIME + " --> " + SRT_TIME, times)
        assert num == str(i) and m and lines, chunk
        g = list(map(int, m.groups()))
        cues.append((g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000, g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000, lines))
    return cues


def test_srt_has_one_valid_cue_per_block(v16):
    cues, blocks = _srt_cues(v16["srt"]), v16["lock"]["blocks"]
    assert len(cues) == len(blocks) == 19
    for (start, end, lines), b in zip(cues, blocks):
        assert start == pytest.approx(min(w["show"] for w in b["top"] + b["hero"]), abs=1e-3) and start < end
        assert lines == [" ".join(w["t"] for w in b["top"]), " ".join(w["t"] for w in b["hero"])]
    assert all(a[1] <= b[0] for a, b in zip(cues, cues[1:]))
    assert cues[-1][1] <= v16["spec"]["duration"] + 1e-3


def _paths(node):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from ([v] if k in ("src", "srt") else _paths(v))
    elif isinstance(node, list):
        for v in node:
            yield from _paths(v)


@pytest.mark.parametrize("name", ["v16", "v2b"])
def test_every_path_is_absolute_and_exists(name, request):
    spec = request.getfixturevalue(name)["spec"]
    paths = list(_paths(spec))
    assert len(paths) > 10
    for p in paths:
        assert Path(p).is_absolute() and Path(p).is_file(), p


@pytest.mark.parametrize("name", ["v16", "v2b"])
def test_tracks_never_overlap_and_losses_are_listed(name, request):
    spec = request.getfixturevalue(name)["spec"]
    for t in spec["tracks"]:
        assert t["type"] in ("video", "text", "audio") and t["clips"]
        for a, b in zip(t["clips"], t["clips"][1:]):
            assert a["at"] + a["dur"] <= b["at"] + 1e-3, (t["name"], a["name"], b["name"])
    assert spec["notes"] and all(isinstance(n, str) and n for n in spec["notes"])
    for u in spec["unsupported"]:
        assert set(u) == {"what", "why", "where"} and all(isinstance(v, str) and v for v in u.values())
    whats = " ".join(u["what"] for u in spec["unsupported"])
    assert "Grade overlay" in whats and "Per-word reveal" in whats
    assert ("Text styling of release 1.1.0" in whats) == (name == "v16")
    assert ("Step card" in whats) == (name == "v2b")


# ------------------------------------------------------------------ errors and CLI

@pytest.mark.parametrize("drop, message", [("picture_lock.json", "picture_lock.json"),
                                           ("public/sfx_stem.wav", "stem_bed"),
                                           ("public/master.mp4", "master footage"),
                                           ("rules.lock", "rules.lock")])
def test_incomplete_project_fails_with_a_clear_error(tmp_path, media, drop, message):
    project = _project(tmp_path, media, FIX / "broll_v2_b13" / "picture_lock.json", None, "1.2.6", {"video": 2}, False)
    (project / drop).unlink()
    with pytest.raises(tc.AdapterError, match=message):
        tc.convert(project, tmp_path / "x.craft.json")


def test_short_master_is_rejected(tmp_path, media):
    project = _project(tmp_path, media, FIX / "broll_v2_b13" / "picture_lock.json", None, "1.2.6", {"video": 2}, False)
    _ff("-i", media / "master.mp4", "-t", 10, "-c", "copy", project / "public" / "master.mp4")
    with pytest.raises(tc.AdapterError, match="needs 43.13 s"):
        tc.convert(project, tmp_path / "x.craft.json")


def test_cli_writes_spec_and_srt_next_to_it(v2b, tmp_path):
    out = tmp_path / "deep" / "video02.craft.json"
    run = subprocess.run([sys.executable, str(ADAPTERS / "th_to_craft.py"), str(v2b["project"]), str(out)],
                         capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    spec = json.loads(out.read_text(encoding="utf-8"))
    srt = tmp_path / "deep" / "video02.srt"
    assert "captions" not in spec and srt.is_file()      # words are text clips already: SRT only on request
    assert any(str(srt) in n for n in spec["notes"])
    run = subprocess.run([sys.executable, str(ADAPTERS / "th_to_craft.py"), str(v2b["project"]), str(out),
                          "--captions"], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert json.loads(out.read_text(encoding="utf-8"))["captions"]["srt"] == str(srt)
    bad = subprocess.run([sys.executable, str(ADAPTERS / "th_to_craft.py"), str(tmp_path), str(out)],
                         capture_output=True, text=True)
    assert bad.returncode == 2 and bad.stderr.startswith("th_to_craft: error: missing")


def test_segment_easing_becomes_key_side_easing():
    """Curve builders tag the segment ending at a key; the spec eases the key's own sides (Premiere/AE)."""
    from th_to_craft import _key_sides
    keys = [[0, 0], [1, 10, "easeOut"], [2, 20, "easeIn"], [3, 30, "bezier"], [4, [1, 2]]]
    assert _key_sides({"scale": keys, "position": [540, 960]}) == {
        "scale": [[0, 0], [1, 10, "bezier"], [2, 20, "easeOut"], [3, 30, "easeIn"], [4, [1, 2]]],
        "position": [540, 960]}
