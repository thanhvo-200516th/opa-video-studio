# kb-beat-sync-montage — toàn văn tài liệu của nguồn `beat-sync-montage`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/beat-sync-montage/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: beat-sync-montage/MODULE.md ===== -->

<!-- master-video-edit: mô-đun nhập 2026-10-29 -->
> **Mô-đun `beat-sync-montage`** của `master-video-edit` — kiến thức tham khảo (không chạy công cụ trong file nếu chưa có).
> Thêm gì: Density arc, downbeat anchor points, breathing rules for beat-synced montage
> Nguồn (USB): `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/AI Video/output/research-integration-20261002/sources/openchatcut/src/agent/skills/beat-sync-montage`
> **Khi dùng trên máy Linux này:**
> - sibling ref music-intelligence not imported: map execution to OCC MCP tools or a local beat source (e.g. `npx hyperframes beats`)
> Công cụ OpenChatCut nhắc trong file (nếu có) chỉ dùng được khi app OpenChatCut mở, qua MCP `openchatcut`; không có thì làm bằng ffmpeg / faster-whisper / FilmCraft.

---
name: beat-sync-montage
description: |
  Plan and build a finished beat-synced montage where cut placement serves the content, not just the metronome.
  Use for 卡点混剪, 卡点剪辑, 踩点视频, beat-sync montage, rhythm edit, 节奏剪辑, 音乐驱动剪辑, or when the user wants cuts that land on the beat.
---

# Beat Sync Montage

Use this workflow when the edit should be driven by music. The failure mode to
avoid is a metronome edit: every cut technically lands on a beat, and the result
still feels mechanical, tiring, or unrelated to what is on screen.

This workflow decides **what** to cut and **why**. It does not re-explain the
music tools — when you reach an execution step, follow `music-intelligence` for
`analyze_music`, `music_edit_plan`, and `sync_cuts_to_music`. Load it there.

This is a OpenChatCut-native workflow. Use the current project, source assets,
asset-frame inspection, AV/script context, and OpenChatCut editing tools.

## When to switch workflows

- Beat-synced photos on a locked, empty track → `music-intelligence` handles this directly with `music_image_plan`. This workflow is for video montage.
- One long source cut to speech rhythm → `long-video-to-shorts`.
- Many clips packaged as highlights without music driving the cut → `multi-clips-to-reels`.
- N distinct beat-synced variants from one pool → `batch-montage-variants`, using this workflow for each cut.

## Workflow

1. Confirm the track is on the timeline and identified. Read the music first: BPM, meter, sections, and energy shape. Use `music-intelligence` → `analyze_music` or `inspect_music`; never request the CLAP embedding.
2. Judge whether the material actually suits a beat edit. See [references/shot-fitness.md](references/shot-fitness.md). Footage with no clear motion onset, or whose motion contradicts the music's energy, will not improve by cutting on every beat. Say so instead of forcing it.
3. Choose the **density arc** before choosing individual cut points. See [references/beat-density.md](references/beat-density.md). Density is a property of the whole piece, not a per-cut decision: a verse and a chorus should not be cut the same way.
4. Assign content to the music's structure. Map sections to narrative roles — intro to the hook, verse to context, build to escalation, drop/chorus to payoff. Cut density follows that map.
5. Pick the anchor points first: 3–6 moments where a cut must hit a downbeat or a section boundary because the content has real impact there. See [references/beat-density.md](references/beat-density.md). Everything else is filler rhythm between anchors.
6. Fill between anchors at the density chosen for that section. Do not fill uniformly — uniform filling is what makes an edit feel mechanical.
7. Reserve breathing room. See [references/beat-density.md](references/beat-density.md). A montage that never stops cutting exhausts the viewer and hides the anchors you built in step 5.
8. Check motion continuity across cuts. See [references/shot-fitness.md](references/shot-fitness.md). Consecutive cuts should not fight each other in screen direction or motion axis unless the collision is deliberate.
9. Plan with `music_edit_plan`, show the bounded summary and any cap warning, and get acceptance. Then apply with `sync_cuts_to_music` and the returned `analysisRef`. Follow `music-intelligence` for both.
10. QA by watching, not by counting. See the rules below. A cut list that is 100% on-beat can still be a bad edit.

## Plan Format

- Track, BPM, meter, section map with timecodes
- Density arc per section (sparse / medium / dense / rest)
- Anchor points: frame, musical event, and what lands there
- Shot order with the reason each shot sits where it does
- Breathing points: where the edit deliberately stops cutting
- Risks: weak motion onsets, motion-direction collisions, sections that outrun the material

## Rules

- **Anchors over uniformity.** Three or four meaningful downbeat hits beat forty evenly spaced ones.
- **Density follows the music, not the maximum.** Dense cutting is a choice for a section, not a default for the piece.
- **Never cut a strong shot short to satisfy a beat.** If a moment needs four beats, give it four beats and adjust around it.
- **Protect the hook.** The first downbeat hit should land within the first three seconds. A beat edit that eases in has wasted its advantage.
- **Breathe.** At least one held shot per 15 seconds unless the brief explicitly asks for relentless pace.
- **Motion must be legible.** A cut that lands on a beat but lands mid-action with no visible onset reads as an error, not as rhythm.
- **The cut serves the content.** If a section has nothing worth cutting, hold the shot and let the music carry it.
- Do not use captions to invent claims the footage does not support.
- Report honestly when the material does not support the requested density.

<!-- ===== /file: beat-sync-montage/MODULE.md ===== -->

<!-- ===== file: beat-sync-montage/references/beat-density.md ===== -->

# Beat Density

Density is the main artistic control in a beat edit, and it is a property of the
whole piece. Deciding it per-cut produces a metronome edit: technically on beat,
mechanically flat.

## 1. Read the music's structure first

Before choosing any cut point, get the section map. Typical shape:

| Section | Role in the edit | Default density |
|---|---|---|
| Intro | Establish, hook | sparse — one or two hits, let the viewer orient |
| Verse | Context, information | sparse to medium |
| Build / pre-chorus | Escalation | medium, accelerating |
| Drop / chorus | Payoff | dense, but only as long as the material holds |
| Breakdown | Reset | rest — hold shots, stop cutting |
| Outro | Resolve | sparse, land the final hit cleanly |

The density arc should look like the energy curve of the track. An edit that is
dense from second one has nowhere to go.

## 2. The four density levels

| Level | Cut on | Shots per 4 beats | Feels like |
|---|---|---|---|
| `rest` | section boundary only | 1 or fewer | Deliberate, lets a moment breathe |
| `sparse` | downbeats | 1 | Calm, readable, good for information |
| `medium` | downbeats + off-beats | 2 | Forward motion without pressure |
| `dense` | every beat | 4 | High energy; fatiguing past ~8 seconds |

`dense` is a spice, not a setting. Past roughly eight continuous seconds it
stops reading as energy and starts reading as noise.

## 3. Anchors first

An anchor is a cut that must land on a specific musical event because the
**content** has impact there — a product reveal, a jump, an impact frame, a
lyric that means something.

Plan 3–6 anchors before filling anything else:

- Put one on the first downbeat of the drop or chorus.
- Put one on the section boundary into the payoff.
- Put the strongest visual on the strongest musical event, not merely on an early one.

Everything between anchors is connective rhythm. Fill it at the section's
density, then stop. An edit built anchor-first reads as intentional; an edit
built by filling every beat reads as generated.

## 4. Breathing room

Rule of thumb: **at least one held shot per 15 seconds**, longer than the
surrounding cuts, where the edit deliberately stops cutting.

Why it matters:

- It resets attention, so the next dense passage lands harder.
- It gives the viewer time to read what they just saw.
- Without it, every cut is equally weighted, which means nothing is emphasised.

Place a breath right before a drop. The contrast is what makes the drop feel
like a drop.

## 5. When to break the grid

Deliberately hold across beats when:

- The shot contains an action that needs to complete (a pour, a turn, a landing).
- The shot carries information the viewer must read (text on screen, a product detail).
- The music has a sustained note or a vocal line that the cutting would chop.

Deliberately cut off-grid when:

- The action onset does not align with the beat — cut on the action, and let the beat be approximate. A visible action landing cleanly beats an invisible beat landing exactly.
- Syncing to a lyric or a sound effect rather than to the rhythm section.

## 6. Capacity check against the material

Density is capped by the material, not by the music:

```
max_sustainable_dense_seconds = usable_onset_shots / (shots_per_second_at_dense)
```

If the plan needs 20 dense seconds and the pool has 12 usable onset shots, the
honest options are to lower the density, extend the pool, or accept repetition.
Repetition in a beat edit is very visible — say so before shipping it rather
than after.

<!-- ===== /file: beat-sync-montage/references/beat-density.md ===== -->

<!-- ===== file: beat-sync-montage/references/shot-fitness.md ===== -->

# Shot Fitness for Beat Edits

Most footage that gets forced into a beat edit was never suitable for one. Check
fitness before planning, because no amount of accurate beat alignment rescues
unsuitable material.

## 1. What makes a shot cuttable on a beat

A shot works in a beat edit when it has a **legible onset** — something the
viewer can see begin. Score each candidate:

| Signal | Good | Poor |
|---|---|---|
| Motion onset | Clear start: a hand enters frame, a jump launches, a door opens | Ambiguous: slow drift, continuous ambient movement |
| Subject framing | Subject readable within ~0.5s | Needs a second to parse what is on screen |
| Motion axis | One dominant direction | Motion scattered or chaotic |
| Duration | Long enough to trim to the slot with margin | Already shorter than the slot |
| Contrast against neighbours | Visually distinct from adjacent shots | Nearly identical to the shot before it |

A shot can fail one signal and still be usable. Two or more failures means it
should be replaced, not cut harder.

## 2. Fast BPM is not a licence

High BPM tracks demand more cuts per second, which demands more usable onset
shots. Before committing to a dense plan, count them:

```
shots_needed ≈ (section_seconds / 60) × BPM × (cuts_per_beat)
```

A 140 BPM track at dense (1 cut per beat) needs ~2.3 shots per second — roughly
28 shots for a 12-second chorus. If the pool has 15 usable onset shots, the
chorus cannot be dense. Lower the density, extend the pool, or accept visible
repetition and tell the user.

## 3. Motion continuity across cuts

Consecutive cuts should not fight each other:

- **Screen direction.** A subject moving left followed by a subject moving right reads as a collision. Either match direction or make the reversal deliberate and rare.
- **Motion axis.** Cutting between horizontal motion and vertical motion in quick succession is jarring unless the beat is strong enough to justify it.
- **Scale jumps.** Extreme close-up to wide and back, repeatedly, reads as strobing rather than rhythm.
- **Luminance flashes.** Alternating very bright and very dark shots at high frequency is physically uncomfortable. Watch for it specifically.

These are the checks that separate a professional beat edit from a generated
one. They are also the ones that only show up when watching the cut, not when
reviewing the cut list.

## 4. Holding a shot is a legitimate choice

When a shot is the strongest available and the section is dense, prefer holding
it across two beats over cutting to a weaker shot just to satisfy the grid. One
strong held shot reads as confidence; two weak cuts read as filler.

## 5. Red flags

Stop and reconsider when:

- More than a third of planned cuts land on shots with no visible onset.
- The same shot appears more than twice in a single section.
- Consecutive shots are near-identical framings of the same subject.
- The cut list is perfectly regular — every cut exactly N beats apart. Real edits have shape; a perfectly regular list is usually a sign the content was ignored.
- You cannot say what a given cut is for.

<!-- ===== /file: beat-sync-montage/references/shot-fitness.md ===== -->
