# Talking-head Rulebook 1.1 — M0 + R0a Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship release `1.1.0` of the Hermes skill `dung-video-talking-head` — rules-as-data, a deterministic pause-aware SFX + BGM planner with an independent lint, a single audio axis (stem + ffmpeg mux), content-based video↔script mapping, a PREP stage, a 4-card-per-video kanban pipeline, and `verify.py` — plus the M0 cleanup that stops rule drift.

**Architecture:** A Python package `thlib` (pure functions, unit-tested) under `releases/1.1.0/scripts/`, thin CLI scripts on top of it, and `stage.py` as the single entry point each kanban card runs. All numbers live in `releases/1.1.0/rules.json`; every project folder pins a version in `rules.lock`. Remotion renders picture only; audio is mixed sample-accurately in Python and muxed with ffmpeg.

**Tech Stack:** Python 3.12 (numpy 2.4, scipy 1.17, jsonschema 4.26, pytest 8.3, faster-whisper large-v3 cached), ffmpeg/ffprobe in PATH, Remotion 4.0.484 + React 19 + TypeScript (existing template), Hermes CLI (`hermes kanban`).

**Spec:** `D:\MMO\Van Minh AI\docs\specs\2026-09-11-talking-head-rulebook-1.1-design.md` (read it; this plan implements §4–§13 for release 1.1.0). Evidence and reference code: `D:\MMO\Van Minh AI\docs\specs\2026-09-11-rulebook-evidence\` — especially `prototype/planner_v11.py`, `prototype/vlib.py`, `prototype/measure_files.py`, `prototype/files_v11.json`, `prototype/sim_v11_auto_standard.json`, `audit/video_v3_mapping.csv`.

**Out of scope (separate later plans):** R1 listening calibration + tag 1.1.1; R0b / B-roll 1.2.0 (B01–B12, B15–B21 — gated on 9router image/video models); production batches.

## Global Constraints

- Skill root `SKILL = C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head`; release root `REL = SKILL/releases/1.1.0`. Until Task 16 cut-over, **do not modify** `SKILL/SKILL.md`, `SKILL/references/`, `SKILL/scripts/`, `SKILL/template/`, `SKILL/examples/`, `SKILL/assets/` (1.0.0 must keep working).
- Never modify anything under `D:/MMO/Van Minh AI/Vid Heygen/<n>/` except inside a new `edit-r<ver>/` folder and `.stage.lock`; never move or delete a user mp4. Never touch `Vid Heygen/1/edit` or `Vid Heygen/2/edit` (D11).
- Never write an API key anywhere. 9router key is read at runtime from env `NINEROUTER_API_KEY`.
- Do not commit anything to the public repo `D:/Vibe Coding/AI Video/video-shotcraft` (third-party). It is read-only input (SFX library, BGM candidates).
- Python: always run with `PYTHONIOENCODING=utf-8`. Blocked in Hermes workers: `python -c`, `node -e`, `execute_code` — every operation must be a script file.
- Remotion: call `./node_modules/.bin/remotion` (never `npx remotion`, the RTK hook rewrites it).
- fps 30, composition 1080×1920, audio 48 kHz. Source HeyGen is 2160×3840 @25 fps.
- Deterministic: same inputs ⇒ byte-identical `sfx_plan.json` and `sfx_stem.wav` (no `hash()`, no randomness, no wall-clock in outputs except STATE.md).
- Code comments and CLI messages in Vietnamese (match the 1.0.0 skill style); identifiers in English.
- Git: repo is `SKILL` (created in Task 0). Conventional commits (`feat:`, `test:`, `docs:`, `chore:`), end every commit message with `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.
- Tests: `pytest` from `SKILL` (`python -m pytest tests -q`); slow tests (whisper, render) marked `@pytest.mark.slow` and run with `-m slow`.

---

## File Structure (release 1.1.0)

```
SKILL/
  .gitignore                    node_modules/ __pycache__/ .pytest_cache/ tests/_out/ *.pyc
  pytest.ini                    testpaths=tests, markers: slow
  CHANGELOG.md                  (Task 16)
  SKILL.md                      router ≤ 40 lines (Task 16 cut-over)
  releases/1.1.0/
    rules.json                  ALL numbers (Task 2) — {"version","params":{…},"sources":{dotted:{label,confidence}}}
    rules.schema.json           JSON schema for rules.json (Task 2)
    MANIFEST.sha256             sha256 of every file under releases/1.1.0 except itself (Task 16)
    stages/PLAN.md stages/PREP.md examples/edit.json   (Task 7, Task 14)
    sfx/*.wav sfx_manifest.json                        (Task 6)
    bgm/*.wav bgm_manifest.json                        (Task 9)
    template/                   Remotion, picture-only (Task 11)
    scripts/
      thlib/__init__.py
      thlib/paths.py            path conventions (Task 0)
      thlib/audio.py            decode/write, envelopes, K/phone/A weighting, true peak, xcorr (Task 1)
      thlib/rules.py            load rules by lock, get(), preset merge (Task 2)
      thlib/textnorm.py         Vietnamese normalisation incl. number words (Task 3)
      thlib/scripts_v3.py       parse v3 scripts / director / eval files (Task 3)
      thlib/mapping.py          mp4 ↔ v3 section ↔ director/eval rows (Task 4)
      thlib/voice.py            vo-clear chain, pauses, onsets, VO_REF, designed breaks (Task 5)
      thlib/align.py            vo_script ↔ whisper word alignment (Task 5)
      thlib/sfxlib.py           SFX measurement + cue construction (Task 6)
      thlib/editschema.py       edit.json 1.1 schema, validation, legacy conversion, proposal (Task 7)
      thlib/planner.py          SFX planner S01–S27 (Task 8)
      thlib/mix.py              stem render, BGM bed (S29), mix, loudnorm (Task 9)
      thlib/lint.py             L1–L14 (Task 10)
      thlib/picture.py          picture_lock + script.ts generation (Task 11)
      thlib/state.py            rules.lock, STATE.md provenance, sha helpers (Task 0)
      thlib/kanban.py           hermes CLI wrapper (Task 14)
      intake.py                 P0 batch intake: mapping + manifests + vo_script extraction (Task 4)
      import_sfx.py import_bgm.py                         (Task 6, Task 9)
      validate_edit.py propose_edit.py                    (Task 7)
      lint_sfx.py lint_rules.py check_text_safe.py        (Task 10, Task 2, Task 11)
      render_video.py mux.py make_report.py               (Task 12)
      verify.py                                           (Task 13)
      stage.py make_cards.py check_prep.py                (Task 14)
      check_drift.py                                      (Task 15)
  tests/
    conftest.py                 fixtures: tmp project dirs, fixture paths, rules loader
    fixtures/v2/                words_whisper.json edit_legacy.json old_cues.json vo-clean.m4a (copied from Vid Heygen/2/edit)
    fixtures/scripts/           symlink-free copies of the 3 script .md files (Task 3)
    test_*.py                   one per module
```

## Shared test fixtures (`tests/conftest.py`, session-scoped; each task adds the ones it needs)

| Fixture | Content | Added in |
|---|---|---|
| `rules_110` | `rules.load("1.1.0")` | Task 2 |
| `v3_sections`, `eval_rows` | parsed copies in `tests/fixtures/scripts/` | Task 3 |
| `fixture_v2_words` | raw whisper words `[{w,s,e}]` from `tests/fixtures/v2/words_whisper.json` (**indices of the legacy edit.json refer to these**) | Task 3 |
| `scan_rows` | `tests/fixtures/scan/video_v3_mapping.csv` rows | Task 4 |
| `v2_vo_mono` | `audio.decode_mono(tests/fixtures/v2/vo-clean.m4a)` | Task 5 |
| `fixture_v2_whisper_words_on` | `fixture_v2_words` + `i` + `on` (via `voice.correct_onsets`) — use with `edit_legacy.json` | Task 5 |
| `fixture_v2_words_corrected` | `align.align(v3_sections[2]["script"], fixture_v2_words)["words"]` + `on` — **indices of `edit_v11.json` refer to these** | Task 5 |
| `fixture_v2_pauses_full` | pauses.json dict: `find_pauses(v2_vo_mono)`, `designed_breaks` from the v3 script, `vo_ref`, `duration_s`, `last_word_end` | Task 5 |
| `v2plan` / `v2plan_and_stem` | planner output on `edit_v11.json` (+ rendered stem, vo, picture lock, manifest) | Task 8 / Task 10 |
| `old_cues_plan_and_stem` | 25 legacy cues converted by `lint.old_cues_to_plan` + stem rendered from 1.0.0 pack files | Task 10 |
| `v2_lock` | `picture.build_lock(fixture_v2_words_corrected, edit_v11, v2plan, fixture_v2_pauses_full, rules_110)` | Task 11 |

## Data Contracts (every task must follow these exactly)

**Paths** (`thlib/paths.py`): `VID_ROOT = env TH_VID_ROOT or "D:/MMO/Van Minh AI/Vid Heygen"`, `DOCS_ROOT = env TH_DOCS_ROOT or "D:/MMO/Van Minh AI"`, `SFX_LIB = env TH_SFX_LIB or "D:/Vibe Coding/AI Video/video-shotcraft/assets/audio"`. `project_dir(n, ver) = VID_ROOT/<n>/edit-r<ver>`; `batch_dir(b) = VID_ROOT/_batches/<b>`; `release_dir(ver) = SKILL/releases/<ver>`.

**rules.lock** (project root): `{"skill": "dung-video-talking-head", "version": "1.1.0", "manifest_sha256": "<hex>"}`.

**words.json** (INTAKE): list of `{"i": int, "w": str (display text, from vo_script), "s": float, "e": float, "on": float (S04 corrected onset), "src": "script"|"asr", "guess": bool}`; `s,e` in seconds on the vo-clean axis; `on` monotone (≥ previous `on` + 0.02).

**pauses.json** (INTAKE): `{"pauses": [[t0, t1], …], "designed_breaks": [{"after_word": int, "kind": "paragraph"|"ellipsis"}], "vo_ref": {"phone_k": float, "k": float, "phone_a": float}, "duration_s": float, "last_word_end": float}`.

**meta.json** (INTAKE): `{"video": int, "source": str, "duration_s": float, "rules_version": str, "preset": str, "vo_script_sha256": str|null, "script_match": float|null, "guess_count": int, "voice_hf_ratio": float, "vo_qa": {"tilt_db": float, "low_db": float, "lufs": float, "tp_dbtp": float}, "xcorr_ms": float, "broll_class": str, "claim_gate": bool}`.

**edit.json** (PLAN, schema `edit/1.1`): `{"schema": "edit/1.1", "hook": {"text": str, "color": "warn"|"gold"|"ink", "hit_word": int|null}|null, "blocks": [{"id": str, "top": [a,b]|null, "hero": [a,b], "bottom": [a,b]|null, "style": "script"|"stomp"|"quote", "color": "warn"|"gold"|"ink"|null, "accent": int|null, "display": {"<word index>": str}, "reveal": bool}], "steps": {"title": str, "items": [{"range": [a,b], "label": str}]}|null, "shots": [{"cut_at_word": int, "s0": float, "s1": float, "x": float, "y": float}], "cta": {"range": [a,b], "label": str, "keyword": str}|null}`. Ranges are half-open word indices into words.json.

**picture_lock.json** (BUILD): `{"fps": 30, "duration_f": int, "t_end": float, "hook": {"text","color","land","out","end"}|null, "blocks": [{"id","style","color","accent","synced": bool,"out": float,"top": [{"t": str,"show": float}],"hero": [...],"bottom": [...]}], "steps": {"title","in","out","items":[{"label","show"}]}|null, "cta": {"label","keyword","show"}|null, "shots": [{"t","s0","s1","x","y"}]}`. `show` = on-screen time in seconds (default `on − text.lead_s`; synced events: `display_s = peak − SYNC_FRAME/fps`).

**sfx_manifest.json** (Task 6): `{"files": {"<role-family>/<name>": {"path": "sfx/<family>/<name>.wav", "md5": str, "origin": "pack"|"lib", "source_url": str, "license": str, "license_checked_at": "YYYY-MM-DD", "lag_ms","attack20_ms","pre30_ms","tail30_ms","tail40_ms","onsets","lt250","b250_1k","b1_4k","gt4k","MmaxK","MmaxPK","crestPK"}}}` (measure definitions = `prototype/measure_files.py`).

**sfx_plan.json** (BUILD): `{"rules_version","preset","vo_ref":{…},"budget": int,"candidates":[{"id","role","tier","rank","source","anchor_word": int|null,"decision":"OK"|"GỘP"|"CHỈ CHỮ"|"BỎ"|"XOÁ","rule": str|null,"tried":[{"mode","pause":[t0,t1],"file","reason"}],"cue": {"file","mode","pause":[t0,t1],"frame": int,"peak_s","start_s","end_s","gain_db","fade_loss_db","short_db","target_db","levels":{"phone_k","k","phone_a"}}|null}],"cues":[<cue objects of OK candidates, sorted by peak_s, each with id/role/tier>],"warnings":[str],"inputs_sha256":{"words","pauses","edit","overrides","vo","manifest","rules"}}`.

**batch_manifest.json** (P0): `{"batch": "bNN", "rules_version", "preset", "videos": [{"n": int, "source": str, "v3": int|null, "v3_title": str|null, "score": float, "second_score": float, "status": "ok"|"needs_rerender"|"needs_input", "reasons": [str], "director_row": int|null, "eval_row": int|null, "eval_type": str|null, "vo_script": str|null, "vo_script_sha256": str|null, "canary": bool, "sample": bool}]}`.

**STATE.md** row (append-only, written only by `thlib.state.append_state`): `| 2026-09-11T10:00:00 | BUILD | task=t_x run=7 | profile=opa-editor | release=1.1.0@<8hex> | edit.json=<8hex>; sfx_plan.json=<8hex> |`.

**Card body** (make_cards.py): three lines `VIDEO: <n>   STAGE: <STAGE>   RULES: dung-video-talking-head@<ver>` / `PRESET: <preset>   ATTEMPT: a<k>` / `BATCH: <bNN>`.

**stage.py stdout protocol** (last 4 lines, always): `RESULT: PASS|FAIL|BLOCK`, `NEXT: <Vietnamese instruction>`, `SUMMARY: <one Vietnamese sentence, no technical numbers>`, `METADATA: <single-line JSON>`.

---

### Task 0: Repository bootstrap

**Files:**
- Create: `SKILL/.gitignore`, `SKILL/pytest.ini`, `SKILL/releases/1.1.0/scripts/thlib/__init__.py`, `SKILL/releases/1.1.0/scripts/thlib/paths.py`, `SKILL/releases/1.1.0/scripts/thlib/state.py`, `SKILL/tests/conftest.py`, `SKILL/tests/test_state.py`, `SKILL/tests/fixtures/v2/*`

**Interfaces:**
- Produces: `thlib.paths.{SKILL, VID_ROOT, DOCS_ROOT, SFX_LIB, release_dir(ver)->Path, project_dir(n:int, ver:str)->Path, batch_dir(b:str)->Path}`; `thlib.state.{sha256_file(p)->str, sha8(p)->str, write_lock(project:Path, ver:str)->dict, read_lock(project:Path)->dict, append_state(project:Path, stage:str, task:str, run:str, profile:str, files:list[Path])->str, read_state(project:Path)->list[dict]}`.

- [ ] **Step 1: Initialise git and commit the 1.0.0 baseline**

```bash
cd "C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head"
git init -b main
printf "node_modules/\n__pycache__/\n.pytest_cache/\ntests/_out/\n*.pyc\n" > .gitignore
git add -A
git commit -m "chore: baseline skill 1.0.0 before rulebook 1.1

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
git tag v1.0.0
```

- [ ] **Step 2: Create pytest.ini and fixtures**

`pytest.ini`:
```ini
[pytest]
testpaths = tests
markers =
    slow: needs whisper/ffmpeg render (run with -m slow)
addopts = -m "not slow"
pythonpath = releases/1.1.0/scripts
```
Copy fixtures (read-only sources):
```bash
mkdir -p tests/fixtures/v2
cp "D:/MMO/Van Minh AI/Vid Heygen/2/edit/scripts/words.json" tests/fixtures/v2/words_whisper.json
cp "D:/MMO/Van Minh AI/Vid Heygen/2/edit/edit.json" tests/fixtures/v2/edit_legacy.json
cp "D:/MMO/Van Minh AI/Vid Heygen/2/edit/public/vo-clean.m4a" tests/fixtures/v2/vo-clean.m4a
```
Extract the old SFX cue table to JSON with a script file `tests/fixtures/v2/extract_old_cues.py` (reads `D:/MMO/Van Minh AI/Vid Heygen/2/edit/src/data/script.ts`, takes the text between `export const SFX: Cue[] = ` and the final `;`, `json.loads` it, writes `old_cues.json`), run it once, commit both.

- [ ] **Step 3: Write failing tests for state helpers** — `tests/test_state.py`:

```python
import json
from pathlib import Path
from thlib import state

def test_lock_roundtrip(tmp_path):
    lock = state.write_lock(tmp_path, "1.1.0")
    assert lock["version"] == "1.1.0" and lock["skill"] == "dung-video-talking-head"
    assert state.read_lock(tmp_path) == lock

def test_append_state_is_append_only(tmp_path):
    f = tmp_path / "a.json"; f.write_text("{}", encoding="utf-8")
    state.write_lock(tmp_path, "1.1.0")
    r1 = state.append_state(tmp_path, "INTAKE", "t_1", "1", "opa-editor", [f])
    r2 = state.append_state(tmp_path, "PLAN", "t_2", "1", "opa-editor", [f])
    rows = state.read_state(tmp_path)
    assert [r["stage"] for r in rows] == ["INTAKE", "PLAN"]
    assert rows[0]["files"]["a.json"] == state.sha8(f)
    assert r1 != r2

def test_sha8_changes_with_content(tmp_path):
    f = tmp_path / "x"; f.write_text("1"); a = state.sha8(f)
    f.write_text("2"); assert state.sha8(f) != a
```

- [ ] **Step 4: Run** `python -m pytest tests/test_state.py -q` → FAIL (module missing).

- [ ] **Step 5: Implement `thlib/paths.py` and `thlib/state.py`** following the Data Contracts. `manifest_sha256` in the lock = `sha256_file(release_dir(ver)/"MANIFEST.sha256")` if it exists else `"dev"`. STATE.md header row is written on first append: `| time | stage | task/run | profile | release | files |` + separator. `read_state` parses rows back into dicts `{"time","stage","task","run","profile","release","files":{name:sha8}}`.

- [ ] **Step 6: Run tests → PASS. Commit** `chore: bootstrap release 1.1.0 skeleton, state helpers, fixtures`.

---

### Task 1: Audio library `thlib/audio.py`

**Files:** Create `releases/1.1.0/scripts/thlib/audio.py`, `tests/test_audio.py`.

**Interfaces:**
- Consumes: nothing.
- Produces: `SR=48000`; `decode(path, ch=2)->np.ndarray[n,ch] float64`; `decode_mono(path)->np.ndarray` ((L+R)/2); `write_wav(path, x, sr=SR)` (16-bit PCM, mono or [n,2]); `db(v)`; `rms_env(x, win_s)`; `kweight(x)`; `momentary(x)` (LUFS-like, 400 ms); `phone(x, hpf=300.0, order=4)`; `phone_k(x)=momentary(phone(x))`; `a_momentary(x)`; `phone_a(x)=a_momentary(phone(x))`; `hpf(x, fc, order)`; `true_peak_db(x)` (4× `resample_poly`); `spectrum(x)`; `band_frac(f,P,lo,hi)`; `runs(mask)->list[(a,b)]`; `integrated_lufs(x)` (gated per BS.1770: abs −70, rel −10 over 400 ms blocks 75 % overlap); `xcorr_lag_ms(a, b, max_ms=200)->float` (lag of b vs a, positive = b later).

- [ ] **Step 1: Tests** `tests/test_audio.py`:

```python
import numpy as np
from thlib import audio as A

def sine(f, amp=1.0, dur=3.0):
    t = np.arange(int(A.SR * dur)) / A.SR
    return amp * np.sin(2 * np.pi * f * t)

def test_momentary_1k_fullscale_is_minus3():
    m = A.momentary(sine(997.0))
    assert abs(np.median(m[A.SR:]) - (-3.01)) < 0.15

def test_integrated_matches_momentary_for_steady_tone():
    assert abs(A.integrated_lufs(sine(997.0, 0.1)) - (-23.01)) < 0.2

def test_phone_filter_kills_100hz_keeps_1k():
    lo = A.db(np.sqrt(np.mean(A.phone(sine(100.0))[A.SR:] ** 2)))
    hi = A.db(np.sqrt(np.mean(A.phone(sine(1000.0))[A.SR:] ** 2)))
    assert hi - lo > 30

def test_runs():
    assert A.runs(np.array([0,1,1,0,1])) == [(1,3),(4,5)]

def test_true_peak_not_below_sample_peak():
    x = sine(11025.0, 0.5, 0.5)
    assert A.true_peak_db(x) >= A.db(np.abs(x).max()) - 1e-6

def test_xcorr_detects_delay():
    rng = np.random.default_rng(0); a = rng.standard_normal(A.SR)
    b = np.concatenate([np.zeros(2048), a])[: len(a)]
    assert abs(A.xcorr_lag_ms(a, b) - 2048 / 48) < 0.1
```

- [ ] **Step 2: Run → FAIL.**
- [ ] **Step 3: Implement** by porting `prototype/vlib.py` (`decode`, `db`, `rms_env`, `kweight` with the BS.1770 48 kHz coefficients `KB1/KA1/KB2/KA2`, `momentary`, `a_weight`, `a_momentary`, `phone` **with `lpf=None` default and hpf 300 Hz order 4**, `hpf`, `spectrum`, `frac`→`band_frac`, `runs`), plus: `write_wav` via `scipy.io.wavfile.write` with int16 clipping; `true_peak_db(x) = db(max|resample_poly(x,4,1)|)`; `integrated_lufs` (blocks 400 ms hop 100 ms, abs gate −70, relative gate −10 LU); `xcorr_lag_ms` via FFT cross-correlation restricted to ±max_ms.
- [ ] **Step 4: Run → PASS. Commit** `feat(thlib): audio measurement library (K, phone, true peak, xcorr)`.

---

### Task 2: `rules.json`, schema, loader, `lint_rules.py`

**Files:** Create `releases/1.1.0/rules.json`, `releases/1.1.0/rules.schema.json`, `scripts/thlib/rules.py`, `scripts/lint_rules.py`, `tests/test_rules.py`.

**Interfaces:**
- Produces: `thlib.rules.load(ver:str|None=None, project:Path|None=None)->Rules` (when `project` is given, version comes from its `rules.lock`); `Rules.get("sfx.p2p_s")`; `Rules.preset(name)->dict` merged over `params.presets.<name>`; `Rules.version`; `Rules.sha256`. `lint_rules.py <project_dir>` exits 1 when the lock version is missing, the release sha differs from the lock, or `rules.json` fails the schema / has a leaf without a `sources` entry.

- [ ] **Step 1: Write `rules.json`** — exact content (values copied from spec §5–§9; every leaf must have a `sources` entry; `label` uses the spec's căn cứ tags):

```json
{
  "version": "1.1.0",
  "params": {
    "fps": 30, "sr": 48000,
    "audio": {"rms_win_s": 0.02, "pause_rms_db": -35.0, "pause_min_s": 0.12, "pause_deep_db": -45.0,
              "pause_deep_min_s": 0.06, "voiced_rms100_db": -35.0, "onset_pre_s": 0.10, "onset_post_s": 0.05,
              "onset_mono_gap_s": 0.02, "phone_hpf_hz": 300.0, "phone_hpf_order": 4, "momentary_s": 0.4},
    "sfx": {
      "role_tier": {"hook": "A", "stomp": "A", "reveal": "A", "cta": "B", "card": "B", "section": "B",
                    "broll_in": "B", "cut": "C", "gapfill": "C"},
      "role_rank": {"hook": 1, "stomp": 2, "reveal": 2, "cta": 3, "card": 4, "section": 5, "broll_in": 5,
                    "cut": 6, "gapfill": 7},
      "role_family": {"hook": "impact", "stomp": "impact", "reveal": "impact", "cta": "sparkle", "card": "slide",
                      "section": "whoosh", "broll_in": "whoosh", "cut": "air", "gapfill": "air"},
      "family_files": {"impact": ["impact/hit-blow", "impact/hit-weak"],
                       "sparkle": ["sparkle/sparkle-wand", "sparkle/sparkle-touch"],
                       "slide": ["slide/paper-slice-quick", "slide/glass-plate-slide"],
                       "whoosh": ["whoosh/transition-soft", "whoosh/wind-swoosh-short", "whoosh/transition-snap"],
                       "air": ["air/sweep-short", "air/transition-snap"]},
      "family_constraints": {
        "impact": {"onsets_max": 1, "attack20_ms_max": 80, "lt250_max": 50.0, "crestPK_max": 21.0},
        "sparkle": {"attack20_ms_max": 400, "tail30_ms_max": 1200, "lt250_max": 50.0},
        "slide": {"attack20_ms_max": 200, "tail30_ms_max": 400, "lt250_max": 50.0, "crestPK_max": 25.0},
        "whoosh": {"attack20_ms_max": 300, "tail30_ms_max": 400, "lt250_max": 50.0},
        "air": {"tail30_ms_max": 400, "lt250_max": 50.0, "gt4k_min": 20.0}},
      "pause_min_s": {"A": 0.25, "B": 0.25, "C": 0.21},
      "g0_s": 0.02, "g1_s": 0.06, "lead_max_s": 0.6, "posthit_s": 0.3, "posthit_pre_s": 0.10,
      "tail_floor_s": 0.03, "attack_cap_s": 0.06, "min_window_s": 0.06,
      "section_pause_s": 0.40, "cut_jump": 0.12, "cut_near_s": 0.6,
      "p2p_s": 1.0, "aa_s": 6.0, "stomp_s": 8.0, "same_file_s": 5.0, "cta_clear_s": 1.0,
      "max_a": 4, "hook_window_s": 3.5, "max_cut_c": 2,
      "fade_out_s": {"default": 0.08, "sparkle": 0.12},
      "fade_in_s": {"impact": 0.01, "sparkle": 0.01, "whoosh": 0.03, "slide": 0.03, "air": 0.03},
      "max_fade_loss_db": 3.0, "tp_cap_dbtp": -2.0, "max_short_db": 1.5, "level_tol_db": 1.5,
      "l6_floor_dbfs": -50.0, "l6_rel_db": -30.0,
      "max_gap_s": 8.0, "min_events": 3, "gapfill_margin_s": 1.0,
      "never_sound": ["jump_cut", "camera_drift", "broll_out", "hero_script", "line_change", "word_pop",
                      "list_item", "hook_title", "ai_disclosure", "joke", "over_speech"],
      "sync_frame": {"block": 5, "card": 6, "item": 5, "cta_pill": 4, "hook_title": 6, "cut": 0},
      "sync_tol_f": {"early": 1, "late": 2}
    },
    "presets": {
      "standard": {"max_5s": 2, "max_10s": 3, "k_per10": 2.5, "tier_db": {"A": -3.0, "B": -8.0, "C": -12.0}},
      "calm": {"max_5s": 2, "max_10s": 2, "k_per10": 2.0, "tier_db": {"A": -5.0, "B": -10.0, "C": -14.0}},
      "punchy": {"max_5s": 3, "max_10s": 4, "k_per10": 3.0, "tier_db": {"A": -2.0, "B": -6.0, "C": -11.0}}
    },
    "default_preset": "standard",
    "loudness": {"final_lufs": -16.0, "social_lufs": -14.0, "tol_lu": 0.5, "tp_dbtp": -1.5, "smax_over_i_lu": 5.0,
                 "sfx_di_max_lu": 0.5, "mmax_over_vo_lu": 1.0},
    "voice": {"hp_hz": 110, "lp_hz": 10000, "eq": [[220, 1.1, -6.0], [3500, 1.3, 3.5]],
              "comp": {"thr_db": -18, "ratio": 2.2, "attack_ms": 10, "release_ms": 90, "makeup_db": 2},
              "target_lufs": -16.0, "tol_lu": 0.5, "tp_dbtp": -2.0, "tilt_min_db": -8.5, "low_max_db": -12.0,
              "xcorr_max_ms": 2.0},
    "bgm": {"rel_lu": -15.0, "hpf_hz": 100, "eq_hz": 2000, "eq_q": 0.7, "eq_db": -3.0, "fade_in_s": 1.0,
            "fade_out_s": 1.5, "loop_xfade_s": 0.5, "tol_lu": 1.0, "smax_over_i_lu": 6.0},
    "end": {"pad_s": 0.5, "fade_s": 0.15},
    "text": {"lead_s": 0.05, "reveal_f": 9, "block_min_s": 1.5, "block_max_s": 3.0, "hero_words_min": 2,
             "hero_words_max": 5, "max_stomp_like": 3, "shot_gap_min_s": 2.0, "shot_gap_max_s": 4.0,
             "scale_max": 1.22, "scale_hi": 1.25, "scale_hi_max_shots": 2},
    "safe_zone": {"text_x_min": 140, "text_x_max": 940, "text_y_min": 270, "text_y_max": 1436,
                  "sub_bottom_px": 484, "sub_max_w": 800, "subject_y_min": 270, "subject_y_max": 1080},
    "mapping": {"clip_s": 25, "min_score": 0.60, "min_margin": 0.10, "script_pass": 0.90, "script_min": 0.80},
    "xcorr_max_ms": 2.0,
    "budgets": {"PREP": {"turns": 25, "runtime": "20m", "retries": 2, "goal_turns": 2},
                "INTAKE": {"turns": 15, "runtime": "25m", "retries": 1, "goal_turns": 0},
                "PLAN": {"turns": 25, "runtime": "20m", "retries": 2, "goal_turns": 2},
                "BUILD": {"turns": 15, "runtime": "25m", "retries": 1, "goal_turns": 0},
                "VERIFY": {"turns": 20, "runtime": "15m", "retries": 1, "goal_turns": 0}},
    "models": {"plan_a2": "ag/claude-sonnet-4-6"},
    "batch": {"max_videos": 10, "prep_videos_per_card": 5, "sample_every": 5}
  },
  "sources": {}
}
```

Then fill `"sources"` with one entry per leaf dotted path (e.g. `"sfx.p2p_s": {"label": "[ngành]", "confidence": "medium"}`; `sfx.pause_min_s.A`, `presets.standard.tier_db.A`, etc.). Use labels from spec §5.2 "Căn cứ" column; `family_constraints.*` and anything marked [GĐ→R1] get `"confidence": "low"`; standards get `"high"`. Lists are leaves (one entry for `sfx.never_sound`, one for `voice.eq`).

> Note on `family_constraints`: the non-impact caps are initial values chosen so the 10 v1 files pass and excluded files fail per role; Task 6 verifies this against real measurements and adjusts the caps in `rules.json` if a listed file fails its own role (record the change in the commit message). Onset limits apply to `impact` only (spec S03).

- [ ] **Step 2: Write `rules.schema.json`** (draft 2020-12) requiring `version` (pattern `^\d+\.\d+\.\d+$`), `params` with all top-level keys above as required objects/numbers, `sources` object of `{label: string, confidence: enum[high,medium,low]}`.

- [ ] **Step 3: Tests** `tests/test_rules.py`:

```python
import json
from thlib import rules, state, paths

def test_load_and_get():
    R = rules.load("1.1.0")
    assert R.version == "1.1.0"
    assert R.get("sfx.p2p_s") == 1.0
    assert R.preset("standard")["tier_db"]["A"] == -3.0

def test_every_leaf_has_source():
    R = rules.load("1.1.0")
    missing = rules.leaves_without_source(R.raw)
    assert missing == []

def test_schema_valid():
    R = rules.load("1.1.0")
    rules.validate(R.raw)  # raises on error

def test_load_from_project_lock(tmp_path):
    state.write_lock(tmp_path, "1.1.0")
    assert rules.load(project=tmp_path).version == "1.1.0"

def test_per_video_budget_formula():
    R = rules.load("1.1.0")
    assert rules.per_video_budget(R, "standard", 43.12) == 11   # ceil(2.5*4.312)
```

- [ ] **Step 4: Run → FAIL. Step 5: Implement** `thlib/rules.py` (`Rules` dataclass with `raw`, `version`, `sha256`; `get(dotted)` raising `KeyError` with the path; `preset(name)`; `leaves_without_source(raw)`; `validate(raw)` via `jsonschema`; `per_video_budget(R, preset, dur_s) = ceil(k × dur_s / 10)`), and `lint_rules.py` (CLI; prints Vietnamese PASS/FAIL lines; exit code). **Step 6: PASS. Commit** `feat: rules 1.1.0 as data with sources, schema and loader`.

---

### Task 3: Text normalisation and script-file parsers

**Files:** Create `scripts/thlib/textnorm.py`, `scripts/thlib/scripts_v3.py`, `tests/test_textnorm.py`, `tests/test_scripts_v3.py`, copy the three `.md` script files into `tests/fixtures/scripts/` (read-only copies).

**Interfaces:**
- Produces: `textnorm.norm_tokens(text:str)->list[tuple[str, list[int]]]` — normalised tokens, each with the indices of the source whitespace-words it came from; `textnorm.norm(text)->list[str]`; `textnorm.similarity(a_tokens, b_tokens)->float` (difflib ratio, autojunk False). `scripts_v3.load_v3(path)->dict[int, Section]` where `Section = {"n", "title", "script", "motion", "placeholders": list[str], "paragraphs": list[str]}`; `scripts_v3.load_director(path)->dict[int, {"n","title","body"}]`; `scripts_v3.load_eval(path)->list[{"row": int, "title", "verdict", "type", "note"}]` (rows like `| 18 | … |`; also range rows `| 43–50 | … |` → one entry per number); `scripts_v3.find_v3_file(docs_root)->Path` (name starts with `60 k` and contains `v3`).

Normalisation rules (spec §6.2): NFC; lowercase; strip punctuation except `%`; `%` and the word pair `phần trăm` → `%`; attach `90 %` → `90%`; Vietnamese number words → digits: units `không 0, một/mốt 1, hai 2, ba 3, bốn/tư 4, năm/lăm/nhăm 5, sáu 6, bảy 7, tám 8, chín 9`, `mười 10`, `mươi ×10`, `trăm ×100`, `nghìn/ngàn ×1000`, `linh/lẻ` (zero tens). Parse maximal runs of number words into one integer token (e.g. `hai mươi lăm`→`25`, `một trăm hai mươi`→`120`, `mười lăm`→`15`), single `năm`→`5`, `một`→`1`. Mapping indices: a merged token lists all source-word indices it consumed.

- [ ] **Step 1: Tests**

```python
# tests/test_textnorm.py
from thlib.textnorm import norm, norm_tokens, similarity

def test_numbers():
    assert norm("hai mươi lăm người") == ["25", "người"]
    assert norm("một trăm hai mươi") == ["120"]
    assert norm("mười lăm phút") == ["15", "phút"]
    assert norm("năm loại content") == ["5", "loại", "content"]
    assert norm("90 % ảnh") == ["90%", "ảnh"]
    assert norm("chín mươi phần trăm") == ["90%"]

def test_indices_track_source_words():
    toks = norm_tokens("Chụp lại hai mươi lần.")
    assert toks == [("chụp", [0]), ("lại", [1]), ("20", [2, 3]), ("lần", [4])]

def test_similarity_video02_script_vs_whisper(fixture_v2_words, v3_sections):
    whisper = " ".join(w["w"] for w in fixture_v2_words)
    assert similarity(norm(v3_sections[2]["script"]), norm(whisper)) >= 0.97
```

```python
# tests/test_scripts_v3.py
from thlib import scripts_v3 as S

def test_v3_has_60_sections(v3_sections):
    assert sorted(v3_sections) == list(range(1, 61))
    assert v3_sections[2]["title"].startswith("Một ảnh sản phẩm")
    assert "APPLY" not in v3_sections[2]["script"]

def test_placeholders(v3_sections):
    assert "[CLAIM]" in v3_sections[37]["placeholders"]
    assert v3_sections[2]["placeholders"] == []

def test_paragraphs_video02(v3_sections):
    assert len(v3_sections[2]["paragraphs"]) == 6

def test_eval_rows_expand_ranges(eval_rows):
    nums = [r["row"] for r in eval_rows]
    assert 18 in nums and 43 in nums and 50 in nums
```
Add fixtures `fixture_v2_words`, `v3_sections`, `eval_rows` to `tests/conftest.py` (load from `tests/fixtures`).

- [ ] **Step 2: Run → FAIL. Step 3: Implement.** Section regex (from the verified scan): `^## (\d{2})\. (.*)$`, script `### VIDEO SCRIPT\s*```text\n(.*?)```` (DOTALL), motion `### APPLY CUSTOM MOTION\s*```text\n(.*?)````, placeholders `\[[A-ZÀ-Ỹ0-9 _/\-]{3,}\]`, paragraphs = non-empty blocks split on blank lines. Director headings `^## Video (\d{2}) — (.*)$`. Eval rows `^\| (\d{2})(?:–(\d{2}))? \| ([^|]+)\|([^|]+)\|([^|]+)\|([^|]*)\|`.
- [ ] **Step 4: PASS. Commit** `feat(thlib): Vietnamese text normalisation and script parsers`.

---

### Task 4: Content-based mapping + `intake.py` (P0)

**Files:** Create `scripts/thlib/mapping.py`, `scripts/intake.py`, `tests/test_mapping.py`.

**Interfaces:**
- Consumes: `textnorm`, `scripts_v3`, `audio.decode_mono`, `rules`.
- Produces: `mapping.list_videos(vid_root)->list[{"n": int, "source": Path, "loose": bool}]` (folders `<n>/<n>.mp4` plus loose `<n>.mp4` at root, `loose=True`); `mapping.match_clip(heard_text:str, sections)->{"v3","score","second","second_score","motion_score"}`; `mapping.classify(video, match, sections, R)->{"status","reasons"}`; `mapping.match_director(section, director)->int|None` and `mapping.match_eval(section, director_row, eval_rows)->int|None` (title+body similarity, threshold 0.5 on title tokens, else None); `intake.main(argv)`.
- `intake.py --batch b01 [--videos 3,4,5 | --all] [--transcriber whisper|cache:<csv>] --preset standard --rules 1.1.0` writes `_batches/<b>/batch_manifest.json`, `mapping.csv`, `vo_script/<n>.txt` + `.sha256`, `APPROVALS.md` (header + deterministic sample list), never writes inside `<n>/`.

Classification (spec §6.1): `status="needs_input"` with reason `SỐ LỆCH: giống mục NN` when `v3 != n`; `needs_rerender` with reason `placeholder` when the matched section has placeholders and any placeholder word (lowercased, brackets stripped) appears in the heard text's first 25 s, or reason `motion` when `motion_score > score` or `score < R.mapping.min_score`; `needs_input` when `score - second_score < min_margin`. Otherwise `ok`. Canary = the lowest-numbered `ok` video in the batch; sample = every `ok` video whose index in the sorted ok-list satisfies `(sha256(batch+str(n)) int) % sample_every == 0` excluding the canary (deterministic).

- [ ] **Step 1: Tests** (fast tests use a fake transcriber; the real scan CSV is the oracle):

```python
from pathlib import Path
from thlib import mapping, scripts_v3

def test_list_videos_includes_loose(tmp_path):
    (tmp_path / "7").mkdir(); (tmp_path / "7" / "7.mp4").write_bytes(b"x")
    (tmp_path / "55.mp4").write_bytes(b"x")
    vids = mapping.list_videos(tmp_path)
    assert [(v["n"], v["loose"]) for v in vids] == [(7, False), (55, True)]

def test_match_and_classify_against_verified_scan(v3_sections, scan_rows, rules_110):
    for row in scan_rows:                       # audit/video_v3_mapping.csv (copied to fixtures)
        m = mapping.match_clip(row["heard"], v3_sections)
        n = int(row["video"].split()[0])
        c = mapping.classify({"n": n}, m, v3_sections, rules_110)
        if n in (31, 33, 37):
            assert c["status"] == "needs_rerender"
        elif n == 38:
            assert c["status"] == "needs_rerender"
        elif n == 34:
            assert c["status"] == "needs_input" and "35" in c["reasons"][0]
        elif n not in (32,):
            assert c["status"] == "ok", (n, c)
```
(Copy `audit/video_v3_mapping.csv` into `tests/fixtures/scan/`. Video 32 is allowed `ok` or `needs_rerender`; the PREP stage records it as CONCERN — spec §7.1.)

- [ ] **Step 2: FAIL. Step 3: Implement** `mapping.py`; `intake.py` whisper transcriber = faster-whisper large-v3, int8, `beam_size=1`, `condition_on_previous_text=False`, on the first `mapping.clip_s` seconds (ffmpeg → 16 kHz mono wav in a temp dir); `--transcriber cache:<csv>` reads `heard` from a previous scan CSV (used by tests and re-runs).
- [ ] **Step 4: PASS. Step 5: slow test** `@pytest.mark.slow test_intake_real_three_videos` runs `intake.py --batch _t --videos 2,34,38 --transcriber whisper` into `tmp_path` (set `TH_VID_ROOT` to the real root but batch dir redirected via `--out`) and asserts statuses ok / needs_input / needs_rerender. **Commit** `feat: content-based video mapping and P0 intake`.

---

### Task 5: Voice processing, alignment and INTAKE stage core

**Files:** Create `scripts/thlib/voice.py`, `scripts/thlib/align.py`, `tests/test_voice.py`, `tests/test_align.py`.

**Interfaces:**
- Consumes: `audio`, `rules`, `textnorm`, `scripts_v3`.
- Produces:
  - `voice.vo_clear(src:Path, out_wav:Path, R)->dict` — ffmpeg chain `highpass=f=110,lowpass=f=10000,equalizer=f=220:t=q:w=1.1:g=-6,equalizer=f=3500:t=q:w=1.3:g=3.5,acompressor=threshold=-18dB:ratio=2.2:attack=10:release=90:makeup=2` then **two-pass linear loudnorm** (`loudnorm=I=-16:TP=-2:LRA=11:print_format=json` measure pass, then `loudnorm=…:measured_I=…:measured_TP=…:measured_LRA=…:measured_thresh=…:offset=…:linear=true`), output WAV PCM 48 kHz stereo; returns QA `{"lufs","tp_dbtp","tilt_db","low_db","voice_hf_ratio","xcorr_ms"}` where tilt = band power 1–3.5 kHz minus 250 Hz–1 kHz (dB), low = 80–250 Hz minus 250 Hz–1 kHz, `voice_hf_ratio` = energy fraction > 4 kHz, xcorr = `audio.xcorr_lag_ms(source_mono, clean_mono)`.
  - `voice.find_pauses(vo_mono, R)->list[(t0,t1)]` (spec §5.1); `voice.correct_onsets(words, pauses, R)->list[float]` (earliest-word rule, monotone clamp); `voice.vo_ref(vo_mono, R)->{"phone_k","k","phone_a"}`; `voice.last_word_end(words, pauses, dur)`.
  - `align.align(script_text:str, whisper_words:list[{"w","s","e"}])->{"words": [...words.json entries...], "score": float, "guess_count": int}` — display words = whitespace-split script words with trailing `,.!?…:;` stripped and ellipsis-only tokens removed; timing via `textnorm.norm_tokens` + `difflib.SequenceMatcher` opcodes; matched tokens take whisper `s,e` (merged number tokens split the span evenly over their source words); unmatched script words are interpolated linearly between the nearest matched neighbours and flagged `guess=False` (script text is authoritative; `guess` is reserved for ASR-only mode); `score` = token similarity.
  - `align.designed_breaks(script_text, words)->list[{"after_word","kind"}]` — paragraph boundaries (blank line) and `...`/`…` positions mapped to the index of the last display word before them.

- [ ] **Step 1: Tests**

```python
# tests/test_voice.py
import numpy as np
from thlib import audio as A, voice, rules

def burst(sec_on, sec_off, n=4):
    x = []
    rng = np.random.default_rng(1)
    for _ in range(n):
        x.append(0.1 * rng.standard_normal(int(sec_on * A.SR)))
        x.append(np.zeros(int(sec_off * A.SR)))
    return np.concatenate(x)

def test_find_pauses_on_synthetic():
    R = rules.load("1.1.0")
    P = voice.find_pauses(burst(0.8, 0.3), R)
    assert len(P) == 4 and all(abs((b - a) - 0.3) < 0.03 for a, b in P)

def test_onset_earliest_word_rule():
    R = rules.load("1.1.0")
    words = [{"s": 2.46, "e": 3.30}, {"s": 3.30, "e": 3.60}]   # '20', 'lần' from video 2
    on = voice.correct_onsets(words, [(2.66, 3.043)], R)
    assert abs(on[0] - 3.043) < 1e-9 and on[1] >= on[0] + 0.02
```

```python
# tests/test_align.py
from thlib import align

def test_align_video02(v3_sections, fixture_v2_words):
    res = align.align(v3_sections[2]["script"], fixture_v2_words)
    assert res["score"] >= 0.95
    texts = [w["w"] for w in res["words"]]
    assert "trước" in texts                 # whisper heard 'cho'; display keeps the script word
    ss = [w["s"] for w in res["words"]]
    assert ss == sorted(ss)

def test_designed_breaks_video02(v3_sections, fixture_v2_words):
    res = align.align(v3_sections[2]["script"], fixture_v2_words)
    br = align.designed_breaks(v3_sections[2]["script"], res["words"])
    assert sum(1 for b in br if b["kind"] == "paragraph") == 5
```
- [ ] **Step 2: FAIL. Step 3: Implement** (port pause/onset/VO_REF code from `prototype/planner_v11.py` lines 76–98). **Step 4: PASS.**
- [ ] **Step 5: slow test** `test_vo_clear_qa_on_video2`: run `voice.vo_clear` on `D:/MMO/Van Minh AI/Vid Heygen/2/2.mp4` into `tmp_path`; assert `abs(lufs+16)<=0.5`, `tp<=-2.0+0.1`, `abs(xcorr_ms)<=2.0`. **Commit** `feat(thlib): vo-clear chain, pauses/onsets/VO_REF, script alignment`.

---

### Task 6: SFX import, manifest and role constraints

**Files:** Create `scripts/thlib/sfxlib.py`, `scripts/import_sfx.py`, `releases/1.1.0/sfx/<family>/<name>.wav` (10 files), `releases/1.1.0/sfx_manifest.json`, `tests/test_sfxlib.py`.

**Interfaces:**
- Produces: `sfxlib.measure(y:np.ndarray)->dict` (fields of `prototype/measure_files.py::shape` + band split + `MmaxK`, `MmaxPK`, `crestPK`); `sfxlib.prepare(path)->np.ndarray` (decode mono (L+R)/2 → `audio.hpf(120,2)` → peak −1 dBFS); `sfxlib.load_manifest(ver)->dict`; `sfxlib.load_signal(ver, key)->np.ndarray` (reads the WAV); `sfxlib.role_ok(meta, family, R)->(bool, [reasons])`.
- `import_sfx.py --rules 1.1.0` imports the 10 files (sources: `SKILL/assets/sfx/<orig>` for `pack:` and `SFX_LIB/sfx/<orig>` for `lib:`; mapping below), writes WAV + manifest, reads `source_url` from the two ATTRIBUTION.md files (line containing the file name → first `https://…mp3` URL), `license = "Mixkit SFX Free License"`, `license_checked_at = "2026-09-11"`, refuses any file whose URL is missing or md5 duplicates another.

| manifest key | origin | source file |
|---|---|---|
| impact/hit-blow | pack | impact/hit-blow.mp3 |
| impact/hit-weak | lib | impact/hit-weak.mp3 |
| sparkle/sparkle-wand | lib | light/sparkle-wand.mp3 |
| sparkle/sparkle-touch | pack | light/sparkle-touch.mp3 |
| slide/paper-slice-quick | lib | paper/paper-slice-quick.mp3 |
| slide/glass-plate-slide | lib | glass/glass-plate-slide.mp3 |
| whoosh/transition-soft | lib | transition/transition-soft.mp3 |
| whoosh/wind-swoosh-short | lib | transition/wind-swoosh-short.mp3 |
| whoosh/transition-snap | lib | transition/transition-snap.mp3 |
| air/sweep-short | pack | transition/sweep-short.mp3 |
| air/transition-snap | lib | transition/transition-snap.mp3 (same WAV bytes as whoosh/transition-snap is allowed: md5 uniqueness is checked **per family**) |

- [ ] **Step 1: Tests**

```python
from thlib import sfxlib, rules

def test_manifest_has_10_licensed_files():
    m = sfxlib.load_manifest("1.1.0")["files"]
    assert len(m) == 11                          # 10 distinct sounds; transition-snap listed in whoosh and air
    for k, v in m.items():
        assert v["source_url"].startswith("https://") and v["license"]

def test_every_listed_file_passes_its_family():
    R = rules.load("1.1.0"); m = sfxlib.load_manifest("1.1.0")["files"]
    for fam, keys in R.get("sfx.family_files").items():
        for k in keys:
            ok, why = sfxlib.role_ok(m[k], fam, R)
            assert ok, (k, why)

def test_excluded_files_fail(tmp_path):
    R = rules.load("1.1.0")
    bass = sfxlib.measure(sfxlib.prepare(r"C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/assets/sfx/impact/bass-hit-short.mp3"))
    assert not sfxlib.role_ok(bass, "impact", R)[0]
    pop = sfxlib.measure(sfxlib.prepare(r"C:/Users/Minh PC/AppData/Local/hermes/shared-skills/video/dung-video-talking-head/assets/sfx/ui/pop-electric.mp3"))
    assert not sfxlib.role_ok(pop, "impact", R)[0]

def test_measurements_match_prototype():
    import json
    proto = json.load(open(r"D:/MMO/Van Minh AI/docs/specs/2026-09-11-rulebook-evidence/prototype/files_v11.json", encoding="utf-8"))
    m = sfxlib.load_manifest("1.1.0")["files"]
    assert abs(m["impact/hit-blow"]["attack20_ms"] - proto["pack:impact/hit-blow.mp3"]["attack20_ms"]) <= 2
```
- [ ] **Step 2: FAIL. Step 3: Implement + run** `python releases/1.1.0/scripts/import_sfx.py --rules 1.1.0`. If a listed file fails its family constraint, widen that family cap in `rules.json` to the measured value + 10 % and note it in the commit body. **Step 4: PASS. Commit** `feat: import 10 licensed SFX with measured manifest`.

---

### Task 7: edit.json 1.1 schema, validation, legacy conversion, proposal, PLAN doc

**Files:** Create `scripts/thlib/editschema.py`, `scripts/validate_edit.py`, `scripts/propose_edit.py`, `releases/1.1.0/stages/PLAN.md`, `releases/1.1.0/examples/edit.json`, `tests/fixtures/v2/edit_v11.json`, `tests/test_editschema.py`.

**Interfaces:**
- Produces: `editschema.SCHEMA` (jsonschema dict for `edit/1.1`); `editschema.validate(edit, words, pauses, R)->list[{"code","msg","where"}]` (empty = PASS); `editschema.from_legacy(legacy_edit, words)->edit` (seconds → `cut_at_word` = first word with `s >= t`, keeps everything else); `editschema.propose(words, pauses, designed_breaks, R)->edit` (skeleton: one block per sentence chunk of 1.5–3 s cut at pauses; hero = last 2–4 words; style script; shots every 2–4 s at block starts alternating 1.00→1.04 / 1.16→1.20; hook/cta null).
- Validation codes (each returns a Vietnamese message): `SCHEMA`, `BLOCK_LEN` (1.5–3.0 s), `HERO_WORDS` (2–5), `OVERLAP_OR_GAP` (ranges contiguous, no overlap; allowed gaps only where `steps` or `hook` consume words), `STOMP_SPACING` (≥ 8 s between stomp/quote blocks), `STOMP_LIKE_MAX` (stomp+quote+reveal ≤ 3), `REVEAL_STYLE` (reveal only on script), `HIT_WORD` (inside a stomp hero and `on ≤ 3.5 s`), `CTA_RANGE` (cta present ⇒ range present), `CTA_KEYWORD_IN_STOMP`, `SCALE` (≤ 1.22; ≤ 1.25 allowed for at most 2 shots), `SHOT_GAP` (2–4 s between cuts), `CUT_SNAP` (each `cut_at_word` has a pause within ±0.6 s of its onset).
- `validate_edit.py <project_dir> [--legacy <old edit.json>]` prints codes and exits 1 on any.

- [ ] **Step 1: Tests**

```python
import json
from thlib import editschema, rules

def test_legacy_video2_violations(fixture_v2_whisper_words_on, fixture_v2_pauses_full):
    R = rules.load("1.1.0")
    legacy = json.load(open("tests/fixtures/v2/edit_legacy.json", encoding="utf-8"))
    W = fixture_v2_whisper_words_on          # legacy indices refer to the old whisper words
    errs = editschema.validate(editschema.from_legacy(legacy, W), W, fixture_v2_pauses_full, R)
    codes = [e["code"] for e in errs]
    assert codes.count("STOMP_SPACING") >= 2
    assert codes.count("BLOCK_LEN") >= 7
    assert codes.count("HERO_WORDS") >= 2
    assert codes.count("SHOT_GAP") >= 3

def test_fixed_video2_edit_passes(fixture_v2_words_corrected, fixture_v2_pauses_full):
    R = rules.load("1.1.0")
    edit = json.load(open("tests/fixtures/v2/edit_v11.json", encoding="utf-8"))   # indices = aligned script words
    assert editschema.validate(edit, fixture_v2_words_corrected, fixture_v2_pauses_full, R) == []

def test_propose_is_valid(fixture_v2_words_corrected, fixture_v2_pauses_full):
    R = rules.load("1.1.0")
    W, P = fixture_v2_words_corrected, fixture_v2_pauses_full
    p = editschema.propose(W, P, P["designed_breaks"], R)
    bad = [e for e in editschema.validate(p, W, P, R) if e["code"] not in ("HIT_WORD", "CTA_RANGE")]
    assert bad == []
```

- [ ] **Step 2: FAIL. Step 3: Implement**, then hand-author `tests/fixtures/v2/edit_v11.json` (video 2 labels: hook `20` with `hit_word` = index of `20`; blocks re-cut to 1.5–3 s and hero 2–5 words; one stomp per ≥ 8 s; `cta.range` starting at `Lưu`; shots 2–4 s) until it validates; copy it to `examples/edit.json`. Write `stages/PLAN.md` by moving the judgement rules from `SKILL/references/edit-json.md` and `SKILL/references/style.md` (style/color meaning, accent, toàn/cận alternation, direction words → `x ±0.045`, steps → `y −0.06`, last shot pushes into CTA, hook from spoken numbers only, CTA only if spoken) into the new label-only schema; add the exact loop: `stage.py PLAN` prints `propose_edit.json` path → agent edits `edit.json` → `validate_edit.py` → max 3 rounds.
- [ ] **Step 4: PASS. Commit** `feat: edit.json 1.1 labels schema, validator, legacy converter, PLAN guide`.

---

### Task 8: SFX planner `thlib/planner.py`

**Files:** Create `scripts/thlib/planner.py`, `tests/test_planner.py`.

**Interfaces:**
- Consumes: `audio`, `rules`, `sfxlib.load_manifest/load_signal`, words/pauses/edit/overrides dicts.
- Produces: `planner.plan(words, pauses, edit, overrides, manifest, signals, vo_mono, R, preset)->(sfx_plan:dict, cues_audio:list[{"start_s": float, "samples": np.ndarray}])` following Data Contracts; `planner.candidates(...)`, `planner.slots(...)`, `planner.build_cue(...)` exposed for tests.

Port `prototype/planner_v11.py` (lines 64–334) into pure functions with these **required changes**:
1. Read every constant from `R` (`sfx.*`, `presets.<preset>`); files per role = `sfx.family_files[role_family[role]]`; fade-in by family (`sfx.fade_in_s`), fade-out `sfx.fade_out_s.sparkle` for sparkle else default.
2. Gain: `gain_db = (vo_ref.phone_k + tier_db[tier]) − MmaxPK(trimmed_faded_cue)`; true-peak cap `tp_cap_dbtp`, shortfall ≤ `max_short_db` else next file (S14).
3. Candidates: hook from `edit.hook.hit_word` (skip if null); stomp/quote blocks (anchor = first word of the block, `last` = last hero word) — remove with rule `S20` when the hero contains all CTA keyword tokens; `reveal` blocks (role `reveal`, anchor hero first word); CTA from `edit.cta.range[0]` with `last` = last word of the video; card from `edit.steps.items[0].range[0]`; sections **5a** = words that start a paragraph in `pauses.designed_breaks` (word index `after_word + 1`) with a pause ≥ `sfx.pause_min_s.B` ending at their onset, **5b** = block starts with a pause ≥ `section_pause_s` ending at their onset; merge 5a/5b that share a pause (source `5a`); cuts from consecutive `edit.shots` whose `|s0 − previous s1| ≥ cut_jump` (time = onset of `cut_at_word`).
4. Slots: pre-hit for all; post-hit for hook/stomp/reveal; **CTA**: pre-hit at its anchor, else post-hit in the pause after the last word (S20); cut: pauses whose centre is within `cut_near_s` of the cut.
5. Allocation: rank order; within a rank pick the candidate whose valid slot is farthest from placed cues (tie → earlier); record `tried` with rule codes (`S05`, `S07`, `S10`, `S11`, `S14`, `S20`, `S22`); decisions `OK` / `GỘP` (pause already used) / `CHỈ CHỮ` (tier A, no slot) / `BỎ` (tier B/C) / `XOÁ` (S20).
6. Spacing (S10) and budget (S11): `max_5s`, `max_10s`, `per_video_budget`, `max_a`, ≤ 1 tier A in `[0, hook_window_s]`, **cut cues ≤ `max_cut_c` and never on two consecutive shot cuts**.
7. Gap-fill (S26) exactly as prototype lines 299–334 with `gapfill_margin_s`; add warning strings `LOW_DENSITY:<a>-<b>` for remaining stretches > `max_gap_s`, `LOW_DENSITY:events<3`, `LOW_DENSITY:no-hook-no-cta`.
8. Overrides: `{"target": candidate_id, "action": "none"}` removes the candidate (decision `BỎ`, rule `OVERRIDE`); `"promote_A"` sets tier A/rank 2 for that candidate.
9. Output `cues_audio` = list of (`start_s`, gained samples) for `mix.render_stem`; `sfx_plan.cues[*].levels` measured on the placed cue in the three domains relative to `vo_ref`.
10. Determinism: iterate in sorted orders only; round all floats written to JSON to 4 decimals.

- [ ] **Step 1: Tests** (property tests on video 2 fixture with `edit_v11.json`):

```python
import json, math
import numpy as np
from thlib import planner, rules, sfxlib, voice, audio as A

@pytest.fixture(scope="module")
def v2plan(fixture_v2_words_corrected, fixture_v2_pauses_full, v2_vo_mono):
    R = rules.load("1.1.0")
    edit = json.load(open("tests/fixtures/v2/edit_v11.json", encoding="utf-8"))
    man = sfxlib.load_manifest("1.1.0")
    sig = {k: sfxlib.load_signal("1.1.0", k) for k in man["files"]}
    return planner.plan(fixture_v2_words_corrected, fixture_v2_pauses_full, edit, [], man, sig, v2_vo_mono, R, "standard")

def test_every_cue_inside_a_pause(v2plan, fixture_v2_pauses_full):
    plan, _ = v2plan
    P = fixture_v2_pauses_full["pauses"]
    for c in plan["cues"]:
        t0, t1 = c["pause"]
        assert [t0, t1] in [list(p) for p in P]
        assert c["start_s"] >= t0 + 0.02 - 1e-6 and c["end_s"] <= t1 - 0.06 + 1e-6

def test_spacing_and_budget(v2plan):
    plan, _ = v2plan
    peaks = sorted(c["peak_s"] for c in plan["cues"])
    assert all(b - a >= 1.0 - 1e-9 for a, b in zip(peaks, peaks[1:]))
    assert all(sum(1 for p in peaks if s <= p < s + 5) <= 2 for s in peaks)
    assert len(peaks) <= math.ceil(2.5 * 43.12 / 10)

def test_hook_and_cta_placed(v2plan):
    plan, _ = v2plan
    roles = {c["role"] for c in plan["cues"]}
    assert "hook" in roles and "cta" in roles

def test_levels_relative_to_voice(v2plan):
    plan, _ = v2plan
    for c in plan["cues"]:
        assert abs(c["levels"]["phone_k"] - c["target_db"]) <= 1.5 + 1e-6

def test_deterministic(fixture_v2_words_corrected, fixture_v2_pauses_full, v2_vo_mono):
    R = rules.load("1.1.0"); man = sfxlib.load_manifest("1.1.0")
    sig = {k: sfxlib.load_signal("1.1.0", k) for k in man["files"]}
    edit = json.load(open("tests/fixtures/v2/edit_v11.json", encoding="utf-8"))
    a = planner.plan(fixture_v2_words_corrected, fixture_v2_pauses_full, edit, [], man, sig, v2_vo_mono, R, "standard")[0]
    b = planner.plan(fixture_v2_words_corrected, fixture_v2_pauses_full, edit, [], man, sig, v2_vo_mono, R, "standard")[0]
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)

def test_calm_has_fewer_or_equal_cues(v2plan, fixture_v2_words_corrected, fixture_v2_pauses_full, v2_vo_mono):
    R = rules.load("1.1.0"); man = sfxlib.load_manifest("1.1.0")
    sig = {k: sfxlib.load_signal("1.1.0", k) for k in man["files"]}
    edit = json.load(open("tests/fixtures/v2/edit_v11.json", encoding="utf-8"))
    calm = planner.plan(fixture_v2_words_corrected, fixture_v2_pauses_full, edit, [], man, sig, v2_vo_mono, R, "calm")[0]
    assert len(calm["cues"]) <= len(v2plan[0]["cues"])
```
(conftest: `fixture_v2_words_corrected` = aligned words from Task 5 with `on`; `fixture_v2_pauses_full` = pauses.json dict incl. `designed_breaks` and `vo_ref`; `v2_vo_mono` = decoded fixture vo-clean.)

- [ ] **Step 2: FAIL. Step 3: Implement. Step 4: PASS.** Record the resulting cue list in the commit body and compare against `prototype/sim_v11_auto_standard.json` (expect hook ≈ 2.767 s and CTA ≈ 38.733 s; differences elsewhere are acceptable if properties hold). **Commit** `feat(thlib): deterministic pause-aware SFX planner S01–S27`.

---

### Task 9: Mix, BGM bed, loudness; `import_bgm.py`

**Files:** Create `scripts/thlib/mix.py`, `scripts/import_bgm.py`, `releases/1.1.0/bgm/` (+ manifest), `tests/test_mix.py`.

**Interfaces:**
- Produces: `mix.render_stem(cues_audio, n_samples)->np.ndarray` (sample-accurate placement, float64 mono); `mix.bgm_bed(track:np.ndarray, vo_mono, t_end_s, R)->np.ndarray` (S29: HPF 100 Hz, peaking −3 dB @ 2 kHz Q 0.7, loop with 0.5 s crossfade, level so that `integrated(bed) = integrated(vo) + rel_lu`, fade in 1.0 s, fade out 1.5 s ending at `t_end`); `mix.mixdown(vo_stereo, stem, bed|None, t_end_s, R)->np.ndarray[n,2]` (sum, trim to `t_end`, 150 ms end fade); `mix.loudnorm_file(in_wav, out_wav, target_lufs, tp_dbtp)->dict` (ffmpeg two-pass `linear=true`, 48 kHz); `mix.select_bgm(ver, video_n)->key|None` (`selected` tracks sorted by `order`, index `video_n mod N`).
- `import_bgm.py --rules 1.1.0 --add <path> --id <id> --url <source_url> --license "<license>" [--select --order k]` converts to WAV 48 kHz stereo into `releases/1.1.0/bgm/<id>.wav`, measures integrated LUFS, writes/updates `bgm_manifest.json` with `content_id_risk: "none"` only when `--content-id-none` is passed (else `"unknown"`, and `select_bgm` ignores it).

- [ ] **Step 1: Tests**

```python
import numpy as np
from thlib import mix, audio as A, rules

def noise(sec, amp=0.1, seed=0):
    return amp * np.random.default_rng(seed).standard_normal(int(sec * A.SR))

def test_render_stem_places_samples():
    s = mix.render_stem([{"start_s": 1.0, "samples": np.ones(10)}], A.SR * 2)
    assert s[A.SR - 1] == 0 and s[A.SR] == 1 and s[A.SR + 9] == 1 and s[A.SR + 10] == 0

def test_bgm_bed_level_and_fades():
    R = rules.load("1.1.0")
    vo = noise(20, 0.05); track = noise(8, 0.3, seed=2)
    bed = mix.bgm_bed(track, vo, 19.0, R)
    assert abs((A.integrated_lufs(bed[: int(18 * A.SR)]) - A.integrated_lufs(vo)) - (-15.0)) <= 1.0
    assert np.abs(bed[:100]).max() < 1e-3 and np.abs(bed[int(19.0 * A.SR):]).max() == 0

def test_loudnorm_file_hits_target(tmp_path):
    x = np.stack([noise(10, 0.02), noise(10, 0.02, 1)], axis=1)
    A.write_wav(tmp_path / "in.wav", x)
    r = mix.loudnorm_file(tmp_path / "in.wav", tmp_path / "out.wav", -16.0, -1.5)
    y = A.decode(tmp_path / "out.wav").mean(axis=1)
    assert abs(A.integrated_lufs(y) + 16.0) <= 0.5
```
- [ ] **Step 2: FAIL. Step 3: Implement.** Import the 5 local BGM candidates (not selected yet) from `SFX_LIB/bgm/*.mp3` with `--url` taken from `SFX_LIB/ATTRIBUTION.md` bgm section and `--license "Mixkit Stock Music Free License" --content-id-none`. **Step 4: PASS. Commit** `feat(thlib): stem/BGM mixdown and two-pass linear loudnorm; BGM candidates`.

---

### Task 10: Lint `thlib/lint.py` + `lint_sfx.py`

**Files:** Create `scripts/thlib/lint.py`, `scripts/lint_sfx.py`, `tests/test_lint.py`.

**Interfaces:**
- Consumes: `sfx_plan`, stem, vo, bed, pauses, picture_lock, manifest, rules.
- Produces: `lint.run_pre_mux(plan, stem, vo_mono, bed|None, pauses, picture_lock, manifest, R, preset)->list[{"code": "L1".."L14", "ok": bool, "msg": str, "frame": int|null}]`; `lint.run_post_mux(project, R)->list[...]` (L11); `lint.old_cues_to_plan(old_cues, pauses, manifest_or_files)->plan` (converter for the 25-cue fixture: peak = `from/30 + lag`, role from note text: `hook|chữ đập|hero|bảng|mục|CTA|cắt`).
- L1–L14 exactly as spec §5.8; L1 re-measures each cue body on the **stem** (not from the plan): first sample ≥ t0+20 ms, RMS20 at t1−60 ms ≤ max(−50 dBFS, peak−30 dB), zero cue samples on voiced frames (RMS20 > −35 dBFS); L2 counts overlapping cue envelopes at −30 dB; L10 recomputes planner output hash (caller passes `expected_sha`); L13 checks no cue's candidate role/event is in `sfx.never_sound` and no cue lies inside a voiced frame; L14 checks plan completeness fields.
- `lint_sfx.py <project_dir>` loads everything, writes `out/sfx_lint.json`, prints one line per code, exit 1 on any `ok=false` (warnings `LOW_DENSITY` do not fail).

- [ ] **Step 1: Tests**

```python
def test_planner_output_passes_lint(v2plan_and_stem, fixture_v2_pauses_full, rules_110):
    plan, stem, vo, lock, man = v2plan_and_stem
    res = lint.run_pre_mux(plan, stem, vo, None, fixture_v2_pauses_full, lock, man, rules_110, "standard")
    assert [r for r in res if not r["ok"]] == []

def test_old_25_cues_fail_expected_codes(old_cues_plan_and_stem, fixture_v2_pauses_full, rules_110):
    plan, stem, vo, lock, man = old_cues_plan_and_stem
    failed = {r["code"] for r in lint.run_pre_mux(plan, stem, vo, None, fixture_v2_pauses_full, lock, man, rules_110, "standard") if not r["ok"]}
    assert {"L1", "L2", "L3", "L4", "L7"} <= failed
```
(Old-cue stem is rendered from the **1.0.0 pack files** `SKILL/assets/sfx/<src>` at the old volumes, placed at `from/30` s, as in `prototype/planner_v11.py` lines 379–389.)

- [ ] **Step 2: FAIL. Step 3: Implement. Step 4: PASS. Commit** `feat(thlib): independent SFX lint L1–L14`.

---

### Task 11: Picture lock, script.ts generation, template 1.1, text-safe check

**Files:**
- Create: `scripts/thlib/picture.py`, `scripts/check_text_safe.py`, `tests/test_picture.py`
- Create `releases/1.1.0/template/` by copying `SKILL/template/` then modify: `src/theme.ts`, `src/data/script.ts` (placeholder), `src/comp/Subtitle.tsx`, `src/comp/StepList.tsx`, `src/comp/Cta.tsx`, `src/comp/Footage.tsx`, `src/comp/Main.tsx`, `src/Root.tsx`; delete `src/comp/Sfx.tsx`, `scripts/build.py`, `scripts/check_av_sync.py`, `scripts/transcribe.py` from the 1.1.0 template copy.

**Interfaces:**
- Produces: `picture.build_lock(words, edit, plan, pauses, R)->picture_lock` and `picture.write_script_ts(lock, path)`; `picture.SYNC_PROGRESS(frames, ease)` helper used by the unit test; `check_text_safe.py <project_dir>` renders transparent PNG stills of composition `TextOnly` at probe frames (for each block: its last `show` + 12 f; steps mid; CTA `show` + 20 f; hook `land`) with `./node_modules/.bin/remotion still src/index.ts TextOnly out/safe/f<N>.png --frame=<N> --image-format=png`, extracts alpha with `ffmpeg -i f.png -vf alphaextract -f rawvideo -pix_fmt gray -`, FAILs when any alpha > 0 pixel lies outside `safe_zone.text_*`.

Display rules: every word `show = on − text.lead_s`; for a block whose stomp/reveal cue is `OK`: `show = peak − sync_frame.block/fps` for all top+hero words (bottom unchanged); card cue OK ⇒ `steps.in = peak − sync_frame.card/fps`, else `steps.in = items[0].show − 0.29`; items `show = on(range[0]) + 2/fps − text.lead_s`; CTA cue OK ⇒ `cta.show = peak − sync_frame.cta_pill/fps`, else `on(cta.range[0])`; block `out = min(last word e + 0.22, next block first show − 0.22)`; `t_end` = first pause after the last word `t0 + end.pad_s` (≤ duration); `duration_f = round(t_end × fps)`; shots `t = on(cut_at_word)` and a shot whose cut has a cut/section cue snaps `t` to the cue frame `k/fps`.

Template changes (TypeScript):
- `data/script.ts` generated: exports `FPS`, `DURATION_F`, `DURATION_S`, `HOOK`, `BLOCKS` (words `{t, show}`), `STEPS`, `SHOTS`, `CTA`, `SAFE` (safe_zone numbers). No `SFX`.
- `theme.ts`: `import { FPS as LOCK_FPS, DURATION_F } from "./data/script"; export const FPS = LOCK_FPS;` (W/H unchanged).
- `Subtitle.tsx`: `wordP = (frame, w) => EASE.outCubic(clamp((frame − w.show*FPS)/REVEAL))`; `inAt = min(show)`; `outAt = b.out`; container `bottom: SAFE.sub_bottom_px`, line `maxWidth: SAFE.sub_max_w`.
- `StepList.tsx`: use `STEPS.in`, `STEPS.out`, `items[i].show`.
- `Cta.tsx`: `CTA.show` instead of `CTA.start`.
- `Footage.tsx`: `<OffthreadVideo … muted />` (volume 0).
- `Main.tsx`: remove `<Sfx/>`; add `<Audio src={staticFile("mix.wav")} />` (Studio preview only; production render uses `--muted`).
- `Root.tsx`: add `<Composition id="TextOnly" component={TextOnly} …/>` where `TextOnly` renders `<Fonts/><StepList/><Subtitle/><Hook/><Cta/>` with no background.

- [ ] **Step 1: Tests**

```python
from thlib import picture

def test_sync_frames_match_template_easing():
    import re
    src = open("releases/1.1.0/template/src/comp/Subtitle.tsx", encoding="utf-8").read()
    reveal = int(re.search(r"const REVEAL = (\d+)", src).group(1))
    out_cubic = lambda t: 1 - (1 - t) ** 3
    first90 = next(f for f in range(reveal + 1) if out_cubic(f / reveal) >= 0.9)
    assert first90 == 5          # rules sfx.sync_frame.block

def test_synced_block_shows_top_and_hero_together(v2_lock):
    b = next(b for b in v2_lock["blocks"] if b["synced"])
    shows = {w["show"] for w in b["top"] + b["hero"]}
    assert len(shows) == 1

def test_t_end_after_last_word(v2_lock, fixture_v2_words_corrected):
    assert v2_lock["t_end"] > fixture_v2_words_corrected[-1]["e"]
```
- [ ] **Step 2: FAIL. Step 3: Implement** Python + TS; run `npm install` in a scratch project created from the 1.1.0 template and `./node_modules/.bin/tsc --noEmit` → clean. **Step 4: PASS. Commit** `feat: picture lock, template 1.1 (picture-only, display_s, safe zone), text-safe gate`.

---

### Task 12: BUILD orchestration (`render_video.py`, `mux.py`, `make_report.py`)

**Files:** Create `scripts/render_video.py`, `scripts/mux.py`, `scripts/make_report.py`, `scripts/thlib/build.py`, `tests/test_build_e2e.py` (slow).

**Interfaces:**
- Consumes: Tasks 5–11.
- Produces: `build.run(project:Path, R, preset)->dict` executing, in order and stopping at the first failure: picture lock → `write_script_ts` → `check_text_safe` → planner → `render_stem` + `select_bgm` + `bgm_bed` → `lint.run_pre_mux` (L1–L10, L12–L14) → write `public/mix.wav`, `public/mix-nobgm.wav` (each loudnorm'd to −16 LUFS / TP −1.5) → `render_video.py` → `mux.py` → `lint.run_post_mux` (L11) → `make_report.py`. Returns `{"ok": bool, "failed_gate": str|None, "artifacts": [...]}`.
- `render_video.py <project>`: `./node_modules/.bin/remotion render src/index.ts Main out/_video.mp4 --muted --concurrency=4 --crf=18`.
- `mux.py <project>`: `ffmpeg -i out/_video.mp4 -i public/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest out/final.mp4`; same for `mix-nobgm.wav` → `final-nobgm.mp4`; social = two-pass linear loudnorm of `final.mp4` audio to −14 / TP −1.5 → `final-social.mp4` (`-c:v copy`); then measures `xcorr_lag_ms(decode(mix.wav), decode(final.mp4))` and per-cue frame offsets (cross-correlate each cue's samples in ±12 f around its planned start on the final track) and writes `out/QA.json`.
- `make_report.py <project>` writes `out/EDITOR-REPORT.md`: paths; loudness table (final/nobgm/social); sfx_plan table (every candidate: id, role, tier, decision, rule, peak, file, levels); lint results; vo_script match score and every `guess`; warnings; claim_gate; B-roll class.

- [ ] **Step 1: Slow e2e test** (`@pytest.mark.slow`): create a temp project for video 2 (`TH_VID_ROOT` → `tmp_path`, source = real `2.mp4`), run INTAKE core (Task 5 functions) + copy `edit_v11.json`, run `build.run`; assert `ok`, `final.mp4` duration equals `duration_f/30 ± 1 f`, `QA.json` xcorr ≤ 2 ms, every cue offset within −1/+2 f, final integrated −16 ± 0.5, social −14 ± 0.5, TP ≤ −1.5.
- [ ] **Step 2: FAIL. Step 3: Implement. Step 4: run** `python -m pytest -m slow tests/test_build_e2e.py -q` → PASS (render ≈ 3 min). **Commit** `feat: BUILD pipeline with picture-only render and ffmpeg mux`.

---

### Task 13: `verify.py`

**Files:** Create `scripts/verify.py`, `tests/test_verify.py`.

**Interfaces:** `verify.py <project_dir> [--release-root <SKILL>]` writes `out/verify/VERDICT.json` `{"verdict": "VERIFIED"|"DONE_WITH_CONCERNS"|"REJECTED", "owner_stage": str|null, "checks": [{"id": "V1".."V7", "ok": bool, "msg"}], "concerns": [str]}`, `out/verify/VERDICT.md`, `out/verify/kpi.json`; first stdout line `VERDICT: <v> | checked n | missing n | reporter-ready yes/no`.
- V1 lock/manifest/shadow-skill scan of `C:/Users/Minh PC/AppData/Local/hermes/profiles/*/skills/**/dung-video-talking-head`; V2 rerun `validate_edit`, `lint_sfx` (pre-mux on saved stem), `check_text_safe` **from the release scripts, not the project**; V3 from `QA.json` recomputed; V4 loudness of the three outputs; V5 every artifact listed in the Data Contracts has a STATE row with matching sha8; V6 report sections present; V7 writes `contact_sheet.png` (ffmpeg tile of 12 frames) and a CONCERN placeholder entry the verifier model fills in the card summary.
- DONE_WITH_CONCERNS when any: `LOW_DENSITY` warning, `meta.guess_count > 0`, `meta.script_match < script_pass`, V7 concern. REJECTED maps failing ids to `owner_stage` per spec §10.5 table.

- [ ] Steps: tests on the Task 12 e2e output (tamper tests: edit a byte in `edit.json` ⇒ V5 fails ⇒ `REJECTED`, owner `PLAN`; delete `final-nobgm.mp4` ⇒ V4/L11 fail ⇒ `BUILD`) → implement → PASS → **commit** `feat: deterministic verify.py V1–V7`.

---

### Task 14: `stage.py`, kanban wrapper, `make_cards.py`, PREP

**Files:** Create `scripts/stage.py`, `scripts/thlib/kanban.py`, `scripts/make_cards.py`, `scripts/check_prep.py`, `releases/1.1.0/stages/PREP.md`, `tests/test_stage.py`, `tests/test_make_cards.py`.

**Interfaces:**
- `kanban.HB = "C:/Users/Minh PC/AppData/Local/hermes/hermes-agent/venv/Scripts/hermes.exe"`; `kanban.show(task_id, board)->dict` (`--json`); `kanban.create(board, title, body, assignee, parents, workspace, idem, skills, runtime, retries, goal_turns, model=None, initial_status=None, dry_run=False)->str|dict`; filters the `⚠ … gateway` banner lines from stdout before JSON parsing.
- `stage.py <STAGE> [--project <dir>] [--card-file <txt>]`: reads the card body from `hermes kanban show $HERMES_KANBAN_TASK --json` (board from `$HERMES_KANBAN_BOARD`) or `--card-file`; validates the three-line body regex; resolves project `VID_ROOT/<n>/edit-r<ver>`; acquires `VID_ROOT/<n>/.stage.lock` (+ global `VID_ROOT/_batches/.heavy.lock` around whisper and render); runs the stage; appends STATE; prints the 4-line protocol.
  - `PREP`: prints paths of `_batches/<b>/vo_script/*.txt`, mapping rows and `stages/PREP.md`; after the agent writes `prep/prep-<k>.json`, `stage.py PREP --check` runs `check_prep.py` and renders `PREP-SHEET.md`.
  - `INTAKE`: scaffold from `release/template` (copy + `npm install --no-audit --no-fund`, master 1620×2880 as in 1.0.0 `new_project.py`, fonts from the 1.0.0 list), `rules.lock`, copy `vo_script.txt` from the batch dir, `voice.vo_clear`, whisper large-v3 (`word_timestamps=True`, `vad_filter=True`, `beam_size=5`) on vo-clean, `align.align`, pauses/onsets/VO_REF/designed breaks, `meta.json`, `ASR_REPORT.md`.
  - `PLAN`: writes `propose_edit.json` (code), prints the PLAN guide path; `stage.py PLAN --check` runs `validate_edit.py`.
  - `BUILD`: `build.run`. `VERIFY`: `verify.py`.
- `make_cards.py --batch b01 --board vm-heygen-b01 [--dry-run]`: reads `batch_manifest.json` + approved PREP state; creates, with idempotency keys `vmh-<n>-<stage>-a1`: `PREP-<k>` (opa-editor) → `APPROVE-PREP-<k>` (assignee `user`, `--initial-status blocked`) → for the canary: `INTAKE→PLAN→BUILD→VERIFY` → `APPROVE-CANARY` (user, blocked) → for every other `ok` video: `INTAKE` (parents: its APPROVE-PREP **and** APPROVE-CANARY) → PLAN → BUILD → VERIFY. Budgets/flags from `rules.budgets`; PLAN a2 cards use `--model <models.plan_a2>`; `--workspace dir:<VID_ROOT>/<n>`; `--skill dung-video-talking-head`. `--check` = dry-run that validates the plan of cards and prints it.
- `check_prep.py <prep json>`: jsonschema for the prep contract (spec §7.1); every video has `status` and `broll_class`; every `heavy` asset has `desc` and `anchor_quote`.

- [ ] Steps: tests for body parsing (valid/invalid), lock contention (second acquire fails fast with BLOCK), protocol lines present, `make_cards --dry-run` on a fake manifest of 3 ok + 1 needs_rerender videos ⇒ exactly: 1 PREP, 1 APPROVE-PREP, 4 canary cards, 1 APPROVE-CANARY, 8 cards for the other two, 0 for needs_rerender; parents as specified → implement → PASS → **commit** `feat: stage.py entrypoint, card generator with canary gating, PREP check`.

---

### Task 15: M0 — drift check and cleanup

**Files:** Create `scripts/check_drift.py`, `tests/test_check_drift.py`.

**Interfaces:** `check_drift.py [--hermes-root C:/Users/Minh PC/AppData/Local/hermes]` read-only; prints one PASS/FAIL line per item and exits 1 on FAIL:
1. no file under `profiles/opa-operator/staging/` (excluding `_superseded/`) contains the regexes `\b0\.82\b|DUCK_DB|OUTPUT_AUDIO_OFFSET` in `*.md|*.py`;
2. no `profiles/*/skills/**/dung-video-talking-head` directory;
3. `profiles/opa-operator/config.yaml`: `kanban.max_in_progress_per_profile == 1` and `kanban.auto_decompose` is true (kept);
4. `profiles/opa-editor/config.yaml` and `profiles/opa-verifier/config.yaml`: `auxiliary.background_review.enabled == false`;
5. `profiles/opa-operator/config.yaml` allowlist has no entry allowing `-c`/`-e` script execution and `execute_code` is not enabled;
6. file `profiles/opa-operator/skills/claude-import/remotion-best-practices/rules/sfx.md` absent.
(Parse YAML with a minimal reader if PyYAML is missing: `python -c` is forbidden, so check `import yaml` inside the script and fall back to regex on `key: value` lines.)

- [ ] **Step 1:** tests with a fake hermes root in `tmp_path` (one failing and one passing tree). **Step 2–4:** implement, PASS.
- [ ] **Step 5: Cleanup actions (orchestrator, not a worker):** `mkdir .../staging/_superseded && git mv`-free plain move of `.../staging/vm-heygen-1-20260910` into `_superseded/` plus a `DEPRECATED.md` note (`dùng dung-video-talking-head@1.1.x`). Print the exact config edits (items 3–6) for the user; the user applies them (D9). Run `check_drift.py`; expected FAIL on 3–6 until the user edits.
- [ ] **Step 6: Commit** `feat: M0 drift checker`.

---

### Task 16: Router SKILL.md, CHANGELOG, MANIFEST, cut-over

**Files:** Modify `SKILL/SKILL.md` (router), create `SKILL/CHANGELOG.md`, `releases/1.1.0/MANIFEST.sha256`, copy spec + this plan into `SKILL/docs/`.

- [ ] **Step 1: Write SKILL.md (≤ 40 lines)**: frontmatter (same `name`, `metadata.version: 1.1.0`, description + triggers unchanged), then: "Mọi việc đi qua card con trỏ. Lệnh đầu tiên: `python <skill>/releases/<ver>/scripts/stage.py <STAGE>` với `<ver>` lấy từ dòng RULES của card. Chép nguyên văn SUMMARY/NEXT. Không sửa rules/component/script; không tự viết script; không `python -c`. Phán đoán chỉ ở PREP (stages/PREP.md), PLAN (stages/PLAN.md). Lỗi: làm theo NEXT; card đã block thì không tự unblock." Keep a short "1.0.0 legacy" note pointing to `git show v1.0.0:SKILL.md` for old projects.
- [ ] **Step 2: CHANGELOG.md** with the 1.1.0 entry (restructure exception note from spec §4.3).
- [ ] **Step 3: MANIFEST.sha256** generated by a script `scripts/make_manifest.py` (sha256 of every file under `releases/1.1.0/` except `MANIFEST.sha256`, sorted paths).
- [ ] **Step 4:** full fast test run + slow e2e green → **commit** `docs: SKILL.md router and changelog for 1.1.0` → do **not** tag yet (tag after Task 17 gates).

---

### Task 17: R0a gates (spec §13.2) and tag

- [ ] Gate 1–3: `python -m pytest tests -q` and `-m slow` green (planner PASS lint; old 25 cues FAIL L1/L2/L3/L4/L7; determinism).
- [ ] Gate 4: `validate_edit.py --legacy tests/fixtures/v2/edit_legacy.json` lists **at least** STOMP_SPACING ×2, BLOCK_LEN ×7, HERO_WORDS ×2, SHOT_GAP ×3 — measured on corrected onsets the real counts are SHOT_GAP ×4 plus two 1.1-only findings (STOMP_LIKE_MAX ×1, CTA_KEYWORD_IN_STOMP ×1), 17 in total (controller ruling R12).
- [ ] Gate 5: SYNC unit test green. Gate 6: e2e QA.json xcorr ≤ 2 ms.
- [ ] Gate 7: alignment 01/02 ≥ 0.90 (slow test runs whisper on vo-clean of both).
- [ ] Gate 8: `intake.py --transcriber cache:<scan csv> --all --batch _gate` reproduces 58/60 same-number matches and flags 31, 33, 37, 38 `needs_rerender`, 34.mp4 `needs_input`.
- [ ] Gate 9: **BGM-SELECT** — list the 5 imported candidates to the user; user picks 1–3 (`import_bgm.py --select`); e2e mix passes L12. *(Blocks the tag until the user answers.)*
- [ ] Gate 10: `check_prep.py` on a PREP sheet produced by running `stage.py PREP` for batch 1 candidates (folders 16, 21, 27, 51, 53, 59, 60).
- [ ] Gate 11: **agent dry-run** — with the user's go-ahead (4 cards), create board `vm-heygen-r0a` and cards INTAKE/PLAN/BUILD/VERIFY for a test copy of video 2 at `Vid Heygen/_r0a_test/2` (source path pointing to the real `2.mp4`, nothing copied into `Vid Heygen/2`); pass = every card within its budget and VERDICT not REJECTED.
- [ ] Regenerate MANIFEST, commit, `git tag v1.1.0`.

---

## Self-review notes (plan vs spec)

- Spec §5 S01–S29 → Tasks 2, 5, 6, 8, 9, 10, 11; §5.8 L1–L14 → Task 10 (+L11 in Task 12); §6 mapping/alignment → Tasks 3, 4, 5; §7 PREP → Task 14 (+ Gate 10); §8 B13/B14 → Task 11 (safe zone + layer order; disclosure layer deferred with B-roll 1.2); §9 pipeline & canary → Task 14; §10 protocol/STATE/locks → Tasks 0, 14; §11 verify → Task 13; §12 F1 → process only (no code in 1.1.0 beyond overrides support in Task 8); §13.1 M0 → Task 15; §13.2 gates → Task 17; §13.3 R1 variants → **not in this plan** (R1 plan will add `stage.py BUILD --variant`).
- Deferred explicitly: B01–B12, B15–B21 (1.2.0), R1, F1 tooling beyond `overrides.json`.
