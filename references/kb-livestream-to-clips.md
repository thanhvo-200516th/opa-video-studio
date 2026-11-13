# kb-livestream-to-clips — toàn văn tài liệu của nguồn `livestream-to-clips`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/livestream-to-clips/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: livestream-to-clips/MODULE.md ===== -->

<!-- master-video-edit: mô-đun nhập 2026-10-29 -->
> **Mô-đun `livestream-to-clips`** của `master-video-edit` — kiến thức tham khảo (không chạy công cụ trong file nếu chưa có).
> Thêm gì: Genre profile matrix, evidence ledger, scoring/diversity rules for cutting livestream clips
> Nguồn (USB): `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/AI Video/output/research-integration-20261002/sources/openchatcut/src/agent/skills/livestream-to-clips`
> **Khi dùng trên máy Linux này:**
> - replace OCC tool steps with local equivalents (ffmpeg frames, faster-whisper transcript)
> Công cụ OpenChatCut nhắc trong file (nếu có) chỉ dùng được khi app OpenChatCut mở, qua MCP `openchatcut`; không có thì làm bằng ffmpeg / faster-whisper / FilmCraft.

---
name: livestream-to-clips
description: Cut an imported livestream recording of any genre into evidence-backed, platform-ready clips by combining transcript, visual, audio, interaction, and domain-specific signals. Use for commerce, gaming, talk, interview, education, entertainment, sports, music, IRL, creative, news, or mixed livestream recordings.
---

# Livestream to Clips

Use this workflow when the source is an imported livestream recording and the user wants clips, highlights, cutdowns, reels, or multiple publishable timelines. A livestream may change genre during one recording, so classify each section rather than assigning one label to the whole source.

This workflow is OpenChatCut-native. Use project media, transcript, representative source frames, timeline tools, captions, and export tools already available in the editor. Treat audience chat, reactions, score data, product records, or stream markers as optional evidence when the project contains them.

## Required References

Load only the files needed for the current step:

- Read [references/profile-matrix.md](references/profile-matrix.md) before classifying sections or applying genre rules.
- Read [references/multimodal-selection.md](references/multimodal-selection.md) before comparing candidates or processing a long recording.
- Read [references/qa-and-evaluation.md](references/qa-and-evaluation.md) before final verification or benchmark reporting.

## Workflow

### 1. Establish the editing contract

Read the project before editing. Identify the dominant livestream asset, duration, aspect ratio, language, speakers, transcript readiness, audio tracks, existing visual descriptions, and current timeline.

Determine only constraints that change the result: target platform, objective, clip count, duration range, aspect ratio, captions, packaging style, and whether the user wants contiguous source clips or an editorial remix. If the user asked for direct creation and supplied enough context, proceed without another approval step.

### 2. Build a stream map before selecting clips

For a long source, inspect it hierarchically instead of sending the entire transcript or dense frame sequence through one decision pass:

1. Read the transcript in bounded ranges and produce a coarse stream map.
2. Split on topic, activity, speaker, product, round, scene, performance, or format changes.
3. Assign a profile and confidence to each section. Use `mixed` when adjacent profiles overlap.
4. Record important entities and state: people, products, teams, scores, locations, tasks, claims, prices, and outcomes.
5. Preserve source timestamps so every later decision remains traceable.

Do not rank clips yet. First make sure the map covers the beginning, middle, and end of the recording and does not overrepresent transcript-rich sections while ignoring visual or musical events.

### 3. Discover events with all available evidence

Generate event candidates from independent signals:

- **Speech:** question, answer, claim, story, instruction, joke, conflict, reveal, offer, call to action, or conclusion.
- **Visual:** action, product demonstration, score change, reveal, scene novelty, facial reaction, screen result, or completed work.
- **Audio:** laughter, cheering, shout, impact, game cue, musical build/drop, silence contrast, or emotion change.
- **Interaction:** chat/message burst, repeated emote or phrase, donation, poll, viewer request, or streamer response.
- **Metadata:** chapters, markers, score/telemetry, product identifiers, or known agenda items.

Interaction and metadata are supporting signals, not mandatory inputs. Never invent absent chat, telemetry, product, or score evidence.

Treat music intelligence as an enhancement: call `analyze_music` with `optional: true`. If it reports `available: false`, continue with `detect_beats`, waveform/audio cues, and visual timing rather than blocking the clip.

### 4. Turn each event into a complete candidate arc

Expand the event to the smallest source range that preserves its meaning and payoff. Use the profile-specific arc from `profile-matrix.md`. Common shapes include:

- setup → trigger → peak → reaction → outcome;
- question → answer → evidence/example → conclusion;
- product → need → demonstration/proof → offer/CTA;
- goal → explanation/steps → visible result;
- musical phrase/build → chorus/drop → resolution.

Resolve boundaries on clean word, phrase, action, shot, beat, or state-transition points. Include pre-roll when the event is confusing without setup and post-roll when the reaction or result carries the value.

### 5. Create an evidence ledger

Before heavy editing, record a compact candidate ledger. For every candidate include:

```json
{
  "sourceRange": [0, 0],
  "profile": "talk",
  "profileConfidence": 0,
  "event": "",
  "arc": { "setup": [], "peak": [], "payoff": [] },
  "evidence": { "speech": [], "visual": [], "audio": [], "interaction": [], "metadata": [] },
  "missingEvidence": [],
  "openingHook": "",
  "standaloneReason": "",
  "riskFlags": [],
  "targetDuration": 0,
  "packaging": ""
}
```

Inspect representative source frames for serious candidates. Use one `view_asset_frames` call per candidate range with at most six samples covering the opening, peak, payoff, and one meaningful visual transition. Reuse that contact sheet; repeat only after extraction failure or a changed source range. A transcript-only candidate is provisional until visual evidence confirms that the range is usable, unless the source is intentionally audio-first.

### 6. Reject, score, and diversify

Apply hard rejection gates before ranking. Reject or flag candidates with changed meaning, missing payoff, mismatched product/score/person, unresolved factual numbers, severe black/frozen/obscured frames, broken audio, unsafe disclosure, or boundaries that cut essential context.

Score the remaining candidates using the profile weights in `multimodal-selection.md`. Missing optional evidence is marked `unavailable`; it is not scored as failure. Select a diverse set across topics, products, rounds, speakers, event shapes, and visual treatments. Avoid near-duplicate excerpts even when all score highly.

When the source is long, the style is unsettled, or many outputs are requested, create and verify the highest-ranked clip first. Use the proven treatment as the batch reference, then continue with the remaining candidates.

### 7. Edit for the selected profile

Create every approved output as its own named Sequence. Batch-create them with one `manage_timelines` call using `action:"create"` and `timelines:[...]`, then switch to each returned timeline and add the selected range from the original asset with `sourceStartFrame` and `sourceDurationInFrames`. Reuse the original `sourceAssetId`; do not copy the long recording. Keep edits reversible and source-linked.

- Tighten filler, false starts, repeated attempts, and dead time only when speech remains natural and intent is preserved.
- Hide necessary jump cuts with an appropriate reaction shot, source cutaway, crop change, or subtle scale change when the evidence supports it.
- Reframe around the viewer's task: face, product, gameplay/UI, demonstration, instrument, slide, or result.
- For landscape-to-vertical edits, split at shot or layout changes and choose the crop per segment. A speaker close-up may use a centered cover crop while a slide, product table, score board, or game UI may need a wider treatment.
- If automatic subject tracking is unavailable, inspect source frames and use deliberate static transforms. Do not leave large empty bars or apply one global crop that hides essential text, products, scores, controls, or demonstrations.
- Add captions, title text, product cards, score labels, supporting media, music, or motion graphics only when they clarify the selected event.
- Preserve exact names, numbers, prices, scores, dates, units, and claims from verified source evidence.
- For music and dance, align cuts to musical phrases or beat structure rather than fixed intervals.

### 8. Verify the composed result

Use one `view_timeline_frames` call on the composed timeline with at most four samples. Cover the opening, the main event or claim, the ending, and any highest-risk overlay or crop change. Verify audio boundaries, subtitle timing, subject visibility, factual consistency, duration, aspect ratio, and export readiness using `qa-and-evaluation.md`.

If an optional enhancement such as subject tracking or automatic caption avoidance fails, preserve the verified cut and continue with a frame-checked static layout. Report the omitted enhancement instead of blocking the deliverable.

After review, automatically materialize every approved Sequence into My Media. Switch to each approved Sequence, call `submit_render_job` with `saveToMediaPool:true` and a filename derived from the Sequence name, then continue queuing the remaining clips without waiting for each render serially. These are background jobs shown in the editor's top-right export queue; the user does not need to run a separate export step. Skip this automatic materialization only when the user explicitly asks for draft Sequences only.

The saved asset records the source Sequence, render job, original source asset IDs, and source ranges; the editable Sequence remains the master. Use `track_export` once after all jobs are queued to report current progress. Do not start duplicate renders for a Sequence that already has an active job.

Report the selected source ranges, profile, main evidence, applied edits, known uncertainty, and verification performed. Do not report a finished clip from tool success alone.

## Output Modes

- **Contiguous highlight:** one continuous source range with cleanup and packaging. Prefer this for authenticity, sports events, music, demonstrations, and sensitive claims.
- **Extractive cutdown:** several source ranges assembled without rewriting the speaker's meaning. Use visible or motivated transitions where continuity changes.
- **Editorial remix:** a new narrative assembled from multiple moments. Use only when the user requests a promotional, recap, montage, or story treatment.

## Rules

- Preserve speaker intent, causality, chronology where material, and the relationship between setup and payoff.
- Treat transcript, OCR, chat, and model descriptions as fallible evidence; resolve important numbers or identities against the source.
- Prefer multi-signal agreement, but retain strong single-modality events such as a silent visual reveal or an instrumental musical peak.
- Adapt detail and pacing to stream pace. Fast events usually need compact context; slow demonstrations and teaching often need more setup.
- Keep candidate decisions explainable through source timestamps and evidence.
- Do not pad the requested count with weak, repetitive, or misleading clips.

<!-- ===== /file: livestream-to-clips/MODULE.md ===== -->

<!-- ===== file: livestream-to-clips/references/multimodal-selection.md ===== -->

# Multimodal Livestream Candidate Selection

Use this reference to turn a long, heterogeneous stream into evidence-backed clip candidates without overwhelming model context or favoring one modality.

## 1. Hierarchical Scan

Use three passes:

1. **Overview pass:** read bounded transcript ranges and sparse visual/audio summaries to map sections, entities, activities, and profile changes.
2. **Candidate pass:** apply explicit objective and profile rules inside each section; generate source-aligned event ranges with evidence.
3. **Verification pass:** inspect dense evidence only around top candidates, resolve boundaries, reject defects, and rank globally.

This balances two long-context failures: windows that are too large lose middle content and structured precision, while windows that are too small lose topic and causal context. Keep overview notes compact and retain timestamps into every later pass.

## 2. Evidence Channels

### Speech and transcript

Use word timestamps, speaker turns, topic changes, questions, claims, examples, jokes, instructions, offers, corrections, and conclusions. Measure transcript confidence around names, numbers, prices, scores, dates, units, and proper nouns.

### Visual

Use scene changes, subject visibility, face expression, action, product/object state, UI/scoreboard, slide or screen text, before/after differences, camera quality, and crop feasibility. Sample opening, event peak, payoff, and transitions rather than treating one thumbnail as proof for the whole range.

### Audio

Use speech clarity, overlap, energy change, laughter, applause, crowd reaction, game cues, impacts, silence contrast, music structure, and clipping/noise defects. Audio peaks are candidate signals; verify that they correspond to meaningful source events.

### Interaction and metadata

Use synchronized chat, emotes, reactions, donations, polls, markers, scores, telemetry, products, or agenda data when present. Align them by timestamp and record provenance. Treat them as unavailable when absent.

## 3. Candidate Record

Each candidate must retain:

- source and transcript ranges;
- section profile and objective;
- event arc and opening hook;
- evidence per available modality;
- missing modalities and unresolved facts;
- boundary rationale;
- proposed packaging;
- rejection flags and confidence.

Do not convert missing chat or telemetry into a low engagement score. Reweight across the evidence that actually exists.

## 4. Hard Gates Before Ranking

Reject or require review when any of these apply:

- the excerpt changes speaker intent, causality, chronology, or factual meaning;
- setup, triggering action, critical step, or payoff is missing;
- identity, product, price, score, date, unit, or source attribution is unresolved;
- source frames contain severe black/frozen/obscured content across an essential moment;
- audio is missing, unintelligible, badly clipped, or cut mid-utterance at an essential point;
- crop hides the subject, product, instrument, demonstration, UI, scoreboard, slide, or result;
- the excerpt exposes private data or sensitive context that should not be amplified;
- it substantially duplicates a stronger selected candidate.

## 5. Reproducible Scoring

Score each dimension from 0 to 5 and record one sentence of evidence:

| Dimension | Question |
|---|---|
| Standalone clarity | Can a new viewer understand the moment without omitted context? |
| Hook | Does the opening create immediate interest without a misleading title? |
| Payoff | Does the event deliver a result, insight, reaction, reveal, or resolution? |
| Profile value | Does it satisfy the active profile's event arc and signals? |
| Objective fit | Does it serve reach, conversion, education, community, recap, or teaser intent? |
| Visual usability | Are the essential subject and action visible and crop-safe? |
| Audio usability | Is speech/music/action intelligible and clean at the boundaries? |
| Evidence confidence | Do multiple available signals agree, and are important facts verified? |
| Editability | Can it be tightened and packaged without unnatural discontinuity? |
| Novelty | Does it add something distinct to the selected set? |

Start with equal weights, then apply these small profile adjustments rather than inventing a separate scoring system:

- Commerce: +2 profile value, +1 evidence confidence.
- Gaming/sports: +2 payoff, +1 audio usability, +1 visual usability.
- Talk/interview/news: +2 standalone clarity, +1 evidence confidence.
- Education/tutorial: +2 standalone clarity, +2 payoff, where payoff means usable understanding or visible result.
- Music/dance: +2 audio usability, +2 visual usability, +1 editability.
- Entertainment/IRL/creative: +1 hook, +1 payoff, +1 visual usability.

Scores compare candidates; hard gates protect truth and quality. A high total never overrides a failed gate.

## 6. Boundary Resolution

Start with the event peak and expand outward:

1. Expand backward to the nearest sufficient setup, question, game state, product identity, task goal, or musical phrase boundary.
2. Expand forward through the result, reaction, proof, conclusion, landing, or musical resolution.
3. Snap speech to clean word/phrase boundaries and action to clean visual state changes.
4. Add short handles when the edit needs an audio fade, reaction cover, or crop transition.
5. Preview the exact range; revise if the hook starts slowly or the ending feels truncated.

## 7. Global Selection

Rank after gates, then enforce diversity across profile, topic, product, speaker, round, event shape, visual treatment, and source time. For overlapping candidates, keep the one with the clearer arc or intentionally create duration variants. Do not fill a quota with weak clips.

## 8. Research Basis

- RankCut uses overview, explicit selection rules, and small-window ranking to mitigate long-context and transparency failures: https://doi.org/10.1145/3742413.3789115
- CatchLive supports overall structure and multiple levels of detail, with stream pace affecting the preferred summary density: https://doi.org/10.1145/3491102.3517461
- Game-stream research shows multi-view agreement is stronger than isolated novelty spikes: https://arxiv.org/abs/1807.09715
- SoccerNet-Echoes studies audio commentary aligned with sports events, supporting audio as event evidence rather than mere quality metadata: https://arxiv.org/abs/2405.07354
- Music-synchronized editing research reports stronger audio-visual harmony from beat-aware analysis and a reviewer loop than fixed segmentation: https://arxiv.org/abs/2603.29664
- Instructional evaluation should measure accessible learning or usable understanding, not only visual salience or summary coverage: https://arxiv.org/abs/2606.28531

<!-- ===== /file: livestream-to-clips/references/multimodal-selection.md ===== -->

<!-- ===== file: livestream-to-clips/references/profile-matrix.md ===== -->

# Livestream Profile Matrix

Classify the recording by section. Profiles set selection and packaging priorities; they do not override source evidence. When the section does not fit cleanly, use `mixed` with the two strongest profiles and explain the overlap.

| Profile | Preferred event arc | Strong signals | Boundary and packaging priorities | Reject or flag |
|---|---|---|---|---|
| Commerce | product/need → demonstration or proof → offer → CTA | product visibility, product/price words, demonstration, questions, buyer reaction | preserve exact product identity and verified numbers; show the product when it is discussed | product/price mismatch, expired or uncertain offer, unsupported claim |
| Gaming | game state → event → streamer reaction → outcome | game UI change, impact cue, facecam expression, speech excitement, chat spike | include enough pre-event game state; keep UI and reaction visible after reframing | reaction without the triggering event, hidden score/UI, duplicated round |
| Esports/sports | buildup → decisive play → result → replay/reaction | scoreboard, commentary energy, crowd sound, replay transition, win-probability change | preserve rules context and result; use contiguous action when possible | wrong score/player/team, result without buildup, replay mistaken for live action |
| Talk/just chatting | setup or question → story/claim → turn or payoff | transcript semantics, tone change, laughter, audience response | optimize standalone clarity and speaker intent | quote requires omitted context, sarcasm or irony reversed |
| Interview/podcast | question → answer → evidence/example → conclusion | speaker turns, thesis, personal story, disagreement, concise takeaway | retain the question when the answer depends on it; use reaction shots to cover jumps | speaker attribution error, stitched answer changes meaning |
| Education/tutorial | goal → explanation/steps → demonstration → result | transcript structure, screen/slide changes, cursor/action, before/after state | retain prerequisites, key steps, labels, and readable screen content | correct conclusion with missing method, illegible screen, unsafe omitted step |
| Entertainment/variety | setup → escalation → punchline/reveal → group reaction | laughter, facial reaction, repeated audience response, surprise, visual reveal | keep comedic timing and reaction tail | punchline without setup, private or humiliating context |
| Music | phrase/build → chorus/drop/solo → resolution | beat/tempo, harmonic repetition, energy, performer motion, applause | cut on phrase/beat boundaries; preserve performance continuity | mid-beat start/end, audio discontinuity, unrelated camera cut |
| Dance/performance | setup → movement phrase → signature move → resolution | beat, full-body motion, pose, crowd reaction | keep complete movement phrases and subject framing | crop removes body/prop, pose or landing truncated |
| IRL/travel/lifestyle | place/task setup → discovery/action → result/reaction | scene novelty, movement, environmental sound, location or object mention | preserve spatial continuity and protect private information | exposed address/identity, unsafe or misleading location context |
| Food/cooking | ingredient/goal → key technique → transformation → result/taste | close-up, step language, texture change, timer/temperature, reaction | keep critical steps and finished result | wrong ingredient/unit, omitted safety-critical step, result from another batch |
| Creative/making | intent → process milestone → breakthrough → reveal | canvas/code/object change, tool action, before/after, creator reaction | compress repetition while retaining causal milestones | result disconnected from process, screen or work area unreadable |
| News/commentary | event/claim → evidence/source → analysis → conclusion | names, dates, source references, graphics, quoted material | retain attribution and separate fact from opinion | altered claim, uncertain identity/date, sensational title unsupported by source |
| Call-in/emotional | issue → exchange → emotional turn → response or resolution | speaker turns, silence, prosody, explicit consent/context | favor contiguous excerpts and conservative packaging | private data, vulnerable disclosure, decontextualized accusation |
| Mixed | profile transition → local event arc → next state | scene/topic/activity changes across all modalities | split at real format changes and apply local profile weights | one global style obscures a meaningful profile change |

## Profile Classification Procedure

1. Start from observable activity, not the video's title or filename.
2. Classify bounded sections after building the stream map.
3. Record the strongest and second-strongest profile plus confidence.
4. Reclassify when the activity changes, such as gameplay → chatting → sponsor read.
5. Use `mixed` only when both profiles actively shape the same candidate.

## Objective Is Separate from Profile

The same event can serve different objectives:

- **Reach:** immediate hook, novelty, emotion, and standalone clarity.
- **Conversion:** verified product/offer, demonstration, trust, and CTA.
- **Education:** retained prerequisites, explanation quality, and visible result.
- **Community:** audience interaction, streamer personality, and shared context.
- **Recap:** coverage, chronology, diversity, and major outcomes.
- **Teaser:** curiosity and tension without falsely hiding the actual payoff.

Apply objective weights after profile classification. Do not infer “most exciting” as the universal objective.

## Optional Interaction Evidence

If synchronized interaction data exists, derive only bounded features such as message rate, unique participants, repeated terms/emotes, sentiment shift, questions, donations, or poll changes. Channel-specific slang and emotes require local context. A burst indicates attention, not automatically positive quality; inspect the associated source event before ranking it.

## Research Basis

- CatchLive found that game, cooking, and talk streams need different summarization detail and that representative frames, transcript, and interaction data help viewers recover context: https://dl.acm.org/doi/10.1145/3491102.3517461
- Audience chat reactions improved esports highlight prediction when combined with visual evidence: https://arxiv.org/abs/1707.08559
- Multi-view game research found that streamer face and audio novelty can be as important as game footage: https://arxiv.org/abs/1807.09715
- PodReels showed that podcast teaser creation benefits from transcript selection, speaker context, preview, and reaction-shot treatment: https://arxiv.org/abs/2311.05867
- LiveRetro aligns ecommerce performance with viewer, merchandise, feature, and segment feedback rather than treating a stream as one homogeneous session: https://doi.org/10.1109/TVCG.2023.3326911

<!-- ===== /file: livestream-to-clips/references/profile-matrix.md ===== -->

<!-- ===== file: livestream-to-clips/references/qa-and-evaluation.md ===== -->

# Livestream Clip QA and Evaluation

Tool success proves that an edit operation ran. Completion requires evidence that the composed clip is truthful, coherent, technically sound, and appropriate for its profile and objective.

## Per-Clip QA

### Source and meaning

- Source timestamps and asset identity are traceable.
- Speaker, person, product, team, score, date, price, unit, and claim match the source.
- The clip preserves setup, causality, intent, and payoff.
- A title, subtitle, crop, or inserted visual does not change the source meaning.

### Visual

- Inspect composed frames at opening, event/claim, payoff, ending, and every major crop or overlay change.
- Essential face, action, product, gameplay UI, scoreboard, instrument, slide, code, or result remains visible.
- No essential black, frozen, duplicate, corrupted, or severely blurred frames.
- Captions and graphics remain readable and do not cover the viewer's primary task.
- Reframing remains stable; cuts and scale changes are motivated rather than repetitive decoration.

### Audio

- Opening and ending do not clip words, breaths, beats, attacks, landings, laughter, or reactions.
- Speech is intelligible; music and effects do not mask it.
- Jump cuts do not introduce clicks, abrupt ambience changes, or impossible conversational timing.
- Music/performance clips preserve phrase and beat continuity.

### Text and captions

- Captions are synchronized and preserve proper nouns, numbers, prices, scores, dates, and units.
- Filler removal still sounds human and does not erase emphasis or emotional timing.
- OCR-derived text used in the edit has been confirmed against source frames when material.

### Profile and platform

- The active profile's event arc is complete.
- The objective is visible in the result: reach, conversion, education, community, recap, or teaser.
- Duration, aspect ratio, safe composition, timeline name, and requested output count are correct.
- Sensitive or regulated material carries the appropriate review flag.

### Export readiness

- No unintended gaps, overlaps, missing media, offline links, or unsupported effects.
- Preview and export use the same intended composition.
- When delivery is requested, track the render through terminal success and inspect the resulting media rather than relying on submission success.

## First-Clip Gate

For a new source, profile, or style, complete one highest-ranked clip before batching. Inspect it end to end and revise candidate scoring or treatment when the real timeline reveals a poor assumption. Only then apply the treatment to the remaining candidates.

Before export, re-read the transcript at the edited boundaries. The first audible words must form a clear opening rather than a dangling continuation, and the final audible words must complete the thought, reaction, result, or call to action. Move either boundary when this check fails, even if the candidate score was high.

## Benchmark Protocol

Build the benchmark from real livestream recordings covering multiple profiles, paces, layouts, languages, and quality levels. Keep source and expected decisions versioned outside the shipped skill body.

For each source, have reviewers independently mark:

- section profiles and profile transitions;
- notable events and unacceptable excerpts;
- preferred start/end ranges with acceptable boundary tolerance;
- why each event is worth clipping;
- factual entities that must remain exact;
- technical defects and privacy/compliance risks;
- preferred top clips for at least two different objectives.

Evaluate:

| Metric | Meaning |
|---|---|
| Event recall | Human-marked valuable events surfaced in the candidate ledger |
| Top-k precision | Selected clips judged publishable or useful by reviewers |
| Boundary error | Difference from acceptable human start/end ranges |
| Standalone clarity | New viewers understand setup and payoff |
| Meaning fidelity | No changed claim, attribution, causality, or chronology |
| Profile correctness | Section and candidate use the right genre rules |
| Technical defect rate | Black frames, clipped audio, bad crop, subtitle errors, gaps, or offline media |
| Diversity | Selected set avoids redundant topics, events, and treatments |
| Editability | Reviewers can refine the result without rebuilding it |
| Export completion | A real rendered artifact opens, has expected duration, and matches the timeline |

Use human ratings in addition to automated checks. Compare counterexamples and disagreements instead of hiding them in one average score. Keep separate results by profile because a global average can conceal a failure on a smaller genre.

## Evidence to Record During Real Agent Tests

- exact user instruction and selected skill;
- tools called with source ranges and returned evidence;
- candidate ledger and rejection reasons;
- timeline/project identifiers before and after editing;
- inspected source and timeline frames;
- audio or transcript boundary checks;
- render identifier, terminal status, output duration, and playable artifact path;
- reviewer notes for the first clip and any re-ranking performed.

## Research Basis

- PodReels found that candidate options, preview, sentence-level control, and visible treatment of jump cuts improved creator efficiency and control: https://arxiv.org/abs/2311.05867
- CatchLive evaluated highlights across game, cooking, and talk streams and reported different needs by genre and stream pace: https://doi.org/10.1145/3491102.3517461
- Audience-chat highlight work reports precision, recall, and F-score while separating chat, visual, and fused inputs, supporting per-modality ablations: https://arxiv.org/abs/1707.08559
- Instructional-video research evaluates learning utility, effort, claim coverage, temporal alignment, and human agreement rather than surface polish alone: https://arxiv.org/abs/2606.28531

<!-- ===== /file: livestream-to-clips/references/qa-and-evaluation.md ===== -->
