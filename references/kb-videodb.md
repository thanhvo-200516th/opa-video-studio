# kb-videodb — toàn văn tài liệu của nguồn `videodb`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/videodb/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: videodb/SKILL.md ===== -->

---
name: videodb
description: See, Understand, Act on video and audio. See- ingest from local files, URLs, RTSP/live feeds, or live record desktop; return realtime context and playable stream links. Understand- extract frames, build visual/semantic/temporal indexes, and search moments with timestamps and auto-clips. Act- transcode and normalize (codec, fps, resolution, aspect ratio), perform timeline edits (subtitles, text/image overlays, branding, audio overlays, dubbing, translation), generate media assets (image, audio, video), and create real time alerts for events from live streams or desktop capture. Use when ingesting, indexing, searching, editing, transcoding, or alerting on video or audio content.
metadata:
  origin: ECC
allowed-tools: Read Grep Glob Bash(python:*)
argument-hint: "[task description]"
---

# VideoDB Skill

**Perception + memory + actions for video, live streams, and desktop sessions.**

## When to use

### Desktop Perception
- Start/stop a **desktop session** capturing **screen, mic, and system audio**
- Stream **live context** and store **episodic session memory**
- Run **real-time alerts/triggers** on what's spoken and what's happening on screen
- Produce **session summaries**, a searchable timeline, and **playable evidence links**

### Video ingest + stream
- Ingest a **file or URL** and return a **playable web stream link**
- Transcode/normalize: **codec, bitrate, fps, resolution, aspect ratio**

### Index + search (timestamps + evidence)
- Build **visual**, **spoken**, and **keyword** indexes
- Search and return exact moments with **timestamps** and **playable evidence**
- Auto-create **clips** from search results

### Timeline editing + generation
- Subtitles: **generate**, **translate**, **burn-in**
- Overlays: **text/image/branding**, motion captions
- Audio: **background music**, **voiceover**, **dubbing**
- Programmatic composition and exports via **timeline operations**

### Live streams (RTSP) + monitoring
- Connect **RTSP/live feeds**
- Run **real-time visual and spoken understanding** and emit **events/alerts** for monitoring workflows

## How it works

### Common inputs
- Local **file path**, public **URL**, or **RTSP URL**
- Desktop capture request: **start / stop / summarize session**
- Desired operations: get context for understanding, transcode spec, index spec, search query, clip ranges, timeline edits, alert rules

### Common outputs
- **Stream URL**
- Search results with **timestamps** and **evidence links**
- Generated assets: subtitles, audio, images, clips
- **Event/alert payloads** for live streams
- Desktop **session summaries** and memory entries

### Running Python code

Before running any VideoDB code, change to the project directory and load environment variables:

```python
from dotenv import load_dotenv
load_dotenv(".env")

import videodb
conn = videodb.connect()
```

This reads `VIDEO_DB_API_KEY` from:
1. Environment (if already exported)
2. Project's `.env` file in current directory

If the key is missing, `videodb.connect()` raises `AuthenticationError` automatically.

Do NOT write a script file when a short inline command works.

When writing inline Python (`python -c "..."`), always use properly formatted code — use semicolons to separate statements and keep it readable. For anything longer than ~3 statements, use a heredoc instead:

```bash
python << 'EOF'
from dotenv import load_dotenv
load_dotenv(".env")

import videodb
conn = videodb.connect()
coll = conn.get_collection()
print(f"Videos: {len(coll.get_videos())}")
EOF
```

### Setup

When the user asks to "setup videodb" or similar:

### 1. Install SDK

```bash
pip install "videodb[capture]" python-dotenv
```

If `videodb[capture]` fails on Linux, install without the capture extra:

```bash
pip install videodb python-dotenv
```

### 2. Configure API key

The user must set `VIDEO_DB_API_KEY` using **either** method:

- **Export in terminal** (before starting Claude): `export VIDEO_DB_API_KEY=your-key`
- **Project `.env` file**: Save `VIDEO_DB_API_KEY=your-key` in the project's `.env` file

Get a free API key at [console.videodb.io](https://console.videodb.io) (50 free uploads, no credit card).

**Do NOT** read, write, or handle the API key yourself. Always let the user set it.

### Quick Reference

### Upload media

```python
# URL
video = coll.upload(url="https://example.com/video.mp4")

# YouTube
video = coll.upload(url="https://www.youtube.com/watch?v=VIDEO_ID")

# Local file
video = coll.upload(file_path="/path/to/video.mp4")
```

### Transcript + subtitle

```python
# force=True skips the error if the video is already indexed
video.index_spoken_words(force=True)
text = video.get_transcript_text()
stream_url = video.add_subtitle()
```

### Search inside videos

```python
from videodb.exceptions import InvalidRequestError

video.index_spoken_words(force=True)

# search() raises InvalidRequestError when no results are found.
# Always wrap in try/except and treat "No results found" as empty.
try:
    results = video.search("product demo")
    shots = results.get_shots()
    stream_url = results.compile()
except InvalidRequestError as e:
    if "No results found" in str(e):
        shots = []
    else:
        raise
```

### Scene search

```python
import re
from videodb import SearchType, IndexType, SceneExtractionType
from videodb.exceptions import InvalidRequestError

# index_scenes() has no force parameter — it raises an error if a scene
# index already exists. Extract the existing index ID from the error.
try:
    scene_index_id = video.index_scenes(
        extraction_type=SceneExtractionType.shot_based,
        prompt="Describe the visual content in this scene.",
    )
except Exception as e:
    match = re.search(r"id\s+([a-f0-9]+)", str(e))
    if match:
        scene_index_id = match.group(1)
    else:
        raise

# Use score_threshold to filter low-relevance noise (recommended: 0.3+)
try:
    results = video.search(
        query="person writing on a whiteboard",
        search_type=SearchType.semantic,
        index_type=IndexType.scene,
        scene_index_id=scene_index_id,
        score_threshold=0.3,
    )
    shots = results.get_shots()
    stream_url = results.compile()
except InvalidRequestError as e:
    if "No results found" in str(e):
        shots = []
    else:
        raise
```

### Timeline editing

**Important:** Always validate timestamps before building a timeline:
- `start` must be >= 0 (negative values are silently accepted but produce broken output)
- `start` must be < `end`
- `end` must be <= `video.length`

```python
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, TextAsset, TextStyle

timeline = Timeline(conn)
timeline.add_inline(VideoAsset(asset_id=video.id, start=10, end=30))
timeline.add_overlay(0, TextAsset(text="The End", duration=3, style=TextStyle(fontsize=36)))
stream_url = timeline.generate_stream()
```

### Transcode video (resolution / quality change)

```python
from videodb import TranscodeMode, VideoConfig, AudioConfig

# Change resolution, quality, or aspect ratio server-side
job_id = conn.transcode(
    source="https://example.com/video.mp4",
    callback_url="https://example.com/webhook",
    mode=TranscodeMode.economy,
    video_config=VideoConfig(resolution=720, quality=23, aspect_ratio="16:9"),
    audio_config=AudioConfig(mute=False),
)
```

### Reframe aspect ratio (for social platforms)

**Warning:** `reframe()` is a slow server-side operation. For long videos it can take
several minutes and may time out. Best practices:
- Always limit to a short segment using `start`/`end` when possible
- For full-length videos, use `callback_url` for async processing
- Trim the video on a `Timeline` first, then reframe the shorter result

```python
from videodb import ReframeMode

# Always prefer reframing a short segment:
reframed = video.reframe(start=0, end=60, target="vertical", mode=ReframeMode.smart)

# Async reframe for full-length videos (returns None, result via webhook):
video.reframe(target="vertical", callback_url="https://example.com/webhook")

# Presets: "vertical" (9:16), "square" (1:1), "landscape" (16:9)
reframed = video.reframe(start=0, end=60, target="square")

# Custom dimensions
reframed = video.reframe(start=0, end=60, target={"width": 1280, "height": 720})
```

### Generative media

```python
image = coll.generate_image(
    prompt="a sunset over mountains",
    aspect_ratio="16:9",
)
```

## Error handling

```python
from videodb.exceptions import AuthenticationError, InvalidRequestError

try:
    conn = videodb.connect()
except AuthenticationError:
    print("Check your VIDEO_DB_API_KEY")

try:
    video = coll.upload(url="https://example.com/video.mp4")
except InvalidRequestError as e:
    print(f"Upload failed: {e}")
```

### Common pitfalls

| Scenario | Error message | Solution |
|----------|--------------|----------|
| Indexing an already-indexed video | `Spoken word index for video already exists` | Use `video.index_spoken_words(force=True)` to skip if already indexed |
| Scene index already exists | `Scene index with id XXXX already exists` | Extract the existing `scene_index_id` from the error with `re.search(r"id\s+([a-f0-9]+)", str(e))` |
| Search finds no matches | `InvalidRequestError: No results found` | Catch the exception and treat as empty results (`shots = []`) |
| Reframe times out | Blocks indefinitely on long videos | Use `start`/`end` to limit segment, or pass `callback_url` for async |
| Negative timestamps on Timeline | Silently produces broken stream | Always validate `start >= 0` before creating `VideoAsset` |
| `generate_video()` / `create_collection()` fails | `Operation not allowed` or `maximum limit` | Plan-gated features — inform the user about plan limits |

## Examples

### Canonical prompts
- "Start desktop capture and alert when a password field appears."
- "Record my session and produce an actionable summary when it ends."
- "Ingest this file and return a playable stream link."
- "Index this folder and find every scene with people, return timestamps."
- "Generate subtitles, burn them in, and add light background music."
- "Connect this RTSP URL and alert when a person enters the zone."

### Screen Recording (Desktop Capture)

Use `ws_listener.py` to capture WebSocket events during recording sessions. Desktop capture supports **macOS** only.

#### Quick Start

1. **Choose state dir**: `STATE_DIR="${VIDEODB_EVENTS_DIR:-$HOME/.local/state/videodb}"`
2. **Start listener**: `VIDEODB_EVENTS_DIR="$STATE_DIR" python scripts/ws_listener.py --clear "$STATE_DIR" &`
3. **Get WebSocket ID**: `cat "$STATE_DIR/videodb_ws_id"`
4. **Run capture code** (see reference/capture.md for the full workflow)
5. **Events written to**: `$STATE_DIR/videodb_events.jsonl`

Use `--clear` whenever you start a fresh capture run so stale transcript and visual events do not leak into the new session.

#### Query Events

```python
import json
import os
import time
from pathlib import Path

events_dir = Path(os.environ.get("VIDEODB_EVENTS_DIR", Path.home() / ".local" / "state" / "videodb"))
events_file = events_dir / "videodb_events.jsonl"
events = []

if events_file.exists():
    with events_file.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

transcripts = [e["data"]["text"] for e in events if e.get("channel") == "transcript"]
cutoff = time.time() - 300
recent_visual = [
    e for e in events
    if e.get("channel") == "visual_index" and e["unix_ts"] > cutoff
]
```

## Additional docs

Reference documentation is in the `reference/` directory adjacent to this SKILL.md file. Use the Glob tool to locate it if needed.

- [reference/api-reference.md](reference/api-reference.md) - Complete VideoDB Python SDK API reference
- [reference/search.md](reference/search.md) - In-depth guide to video search (spoken word and scene-based)
- [reference/editor.md](reference/editor.md) - Timeline editing, assets, and composition
- [reference/streaming.md](reference/streaming.md) - HLS streaming and instant playback
- [reference/generative.md](reference/generative.md) - AI-powered media generation (images, video, audio)
- [reference/rtstream.md](reference/rtstream.md) - Live stream ingestion workflow (RTSP/RTMP)
- [reference/rtstream-reference.md](reference/rtstream-reference.md) - RTStream SDK methods and AI pipelines
- [reference/capture.md](reference/capture.md) - Desktop capture workflow
- [reference/capture-reference.md](reference/capture-reference.md) - Capture SDK and WebSocket events
- [reference/use-cases.md](reference/use-cases.md) - Common video processing patterns and examples

**Do not use ffmpeg, moviepy, or local encoding tools** when VideoDB supports the operation. The following are all handled server-side by VideoDB — trimming, combining clips, overlaying audio or music, adding subtitles, text/image overlays, transcoding, resolution changes, aspect-ratio conversion, resizing for platform requirements, transcription, and media generation. Only fall back to local tools for operations listed under Limitations in reference/editor.md (transitions, speed changes, crop/zoom, colour grading, volume mixing).

### When to use what

| Problem | VideoDB solution |
|---------|-----------------|
| Platform rejects video aspect ratio or resolution | `video.reframe()` or `conn.transcode()` with `VideoConfig` |
| Need to resize video for Twitter/Instagram/TikTok | `video.reframe(target="vertical")` or `target="square"` |
| Need to change resolution (e.g. 1080p → 720p) | `conn.transcode()` with `VideoConfig(resolution=720)` |
| Need to overlay audio/music on video | `AudioAsset` on a `Timeline` |
| Need to add subtitles | `video.add_subtitle()` or `CaptionAsset` |
| Need to combine/trim clips | `VideoAsset` on a `Timeline` |
| Need to generate voiceover, music, or SFX | `coll.generate_voice()`, `generate_music()`, `generate_sound_effect()` |

## Provenance

Reference material for this skill is vendored locally under `skills/videodb/reference/`.
Use the local copies above instead of following external repository links at runtime.

<!-- ===== /file: videodb/SKILL.md ===== -->

<!-- ===== file: videodb/reference/api-reference.md ===== -->

# Complete API Reference

Reference material for the VideoDB skill. For usage guidance and workflow selection, start with [../SKILL.md](../SKILL.md).

## Connection

```python
import videodb

conn = videodb.connect(
    api_key="your-api-key",      # or set VIDEO_DB_API_KEY env var
    base_url=None,                # custom API endpoint (optional)
)
```

**Returns:** `Connection` object

### Connection Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `conn.get_collection(collection_id="default")` | `Collection` | Get collection (default if no ID) |
| `conn.get_collections()` | `list[Collection]` | List all collections |
| `conn.create_collection(name, description, is_public=False)` | `Collection` | Create new collection |
| `conn.update_collection(id, name, description)` | `Collection` | Update a collection |
| `conn.check_usage()` | `dict` | Get account usage stats |
| `conn.upload(source, media_type, name, ...)` | `Video\|Audio\|Image` | Upload to default collection |
| `conn.record_meeting(meeting_url, bot_name, ...)` | `Meeting` | Record a meeting |
| `conn.create_capture_session(...)` | `CaptureSession` | Create a capture session (see [capture-reference.md](capture-reference.md)) |
| `conn.youtube_search(query, result_threshold, duration)` | `list[dict]` | Search YouTube |
| `conn.transcode(source, callback_url, mode, ...)` | `str` | Transcode video (returns job ID) |
| `conn.get_transcode_details(job_id)` | `dict` | Get transcode job status and details |
| `conn.connect_websocket(collection_id)` | `WebSocketConnection` | Connect to WebSocket (see [capture-reference.md](capture-reference.md)) |

### Transcode

Transcode a video from a URL with custom resolution, quality, and audio settings. Processing happens server-side — no local ffmpeg required.

```python
from videodb import TranscodeMode, VideoConfig, AudioConfig

job_id = conn.transcode(
    source="https://example.com/video.mp4",
    callback_url="https://example.com/webhook",
    mode=TranscodeMode.economy,
    video_config=VideoConfig(resolution=720, quality=23),
    audio_config=AudioConfig(mute=False),
)
```

#### transcode Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `source` | `str` | required | URL of the video to transcode (preferably a downloadable URL) |
| `callback_url` | `str` | required | URL to receive the callback when transcoding completes |
| `mode` | `TranscodeMode` | `TranscodeMode.economy` | Transcoding speed: `economy` or `lightning` |
| `video_config` | `VideoConfig` | `VideoConfig()` | Video encoding settings |
| `audio_config` | `AudioConfig` | `AudioConfig()` | Audio encoding settings |

Returns a job ID (`str`). Use `conn.get_transcode_details(job_id)` to check job status.

```python
details = conn.get_transcode_details(job_id)
```

#### VideoConfig

```python
from videodb import VideoConfig, ResizeMode

config = VideoConfig(
    resolution=720,              # Target resolution height (e.g. 480, 720, 1080)
    quality=23,                  # Encoding quality (lower = better, default 23)
    framerate=30,                # Target framerate
    aspect_ratio="16:9",         # Target aspect ratio
    resize_mode=ResizeMode.crop, # How to fit: crop, fit, or pad
)
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `resolution` | `int\|None` | `None` | Target resolution height in pixels |
| `quality` | `int` | `23` | Encoding quality (lower = higher quality) |
| `framerate` | `int\|None` | `None` | Target framerate |
| `aspect_ratio` | `str\|None` | `None` | Target aspect ratio (e.g. `"16:9"`, `"9:16"`) |
| `resize_mode` | `str` | `ResizeMode.crop` | Resize strategy: `crop`, `fit`, or `pad` |

#### AudioConfig

```python
from videodb import AudioConfig

config = AudioConfig(mute=False)
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `mute` | `bool` | `False` | Mute the audio track |

## Collections

```python
coll = conn.get_collection()
```

### Collection Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `coll.get_videos()` | `list[Video]` | List all videos |
| `coll.get_video(video_id)` | `Video` | Get specific video |
| `coll.get_audios()` | `list[Audio]` | List all audios |
| `coll.get_audio(audio_id)` | `Audio` | Get specific audio |
| `coll.get_images()` | `list[Image]` | List all images |
| `coll.get_image(image_id)` | `Image` | Get specific image |
| `coll.upload(url=None, file_path=None, media_type=None, name=None)` | `Video\|Audio\|Image` | Upload media |
| `coll.search(query, search_type, index_type, score_threshold, namespace, scene_index_id, ...)` | `SearchResult` | Search across collection (semantic only; keyword and scene search raise `NotImplementedError`) |
| `coll.generate_image(prompt, aspect_ratio="1:1")` | `Image` | Generate image with AI |
| `coll.generate_video(prompt, duration=5)` | `Video` | Generate video with AI |
| `coll.generate_music(prompt, duration=5)` | `Audio` | Generate music with AI |
| `coll.generate_sound_effect(prompt, duration=2)` | `Audio` | Generate sound effect |
| `coll.generate_voice(text, voice_name="Default")` | `Audio` | Generate speech from text |
| `coll.generate_text(prompt, model_name="basic", response_type="text")` | `dict` | LLM text generation — access result via `["output"]` |
| `coll.dub_video(video_id, language_code)` | `Video` | Dub video into another language |
| `coll.record_meeting(meeting_url, bot_name, ...)` | `Meeting` | Record a live meeting |
| `coll.create_capture_session(...)` | `CaptureSession` | Create a capture session (see [capture-reference.md](capture-reference.md)) |
| `coll.get_capture_session(...)` | `CaptureSession` | Retrieve capture session (see [capture-reference.md](capture-reference.md)) |
| `coll.connect_rtstream(url, name, ...)` | `RTStream` | Connect to a live stream (see [rtstream-reference.md](rtstream-reference.md)) |
| `coll.make_public()` | `None` | Make collection public |
| `coll.make_private()` | `None` | Make collection private |
| `coll.delete_video(video_id)` | `None` | Delete a video |
| `coll.delete_audio(audio_id)` | `None` | Delete an audio |
| `coll.delete_image(image_id)` | `None` | Delete an image |
| `coll.delete()` | `None` | Delete the collection |

### Upload Parameters

```python
video = coll.upload(
    url=None,            # Remote URL (HTTP, YouTube)
    file_path=None,      # Local file path
    media_type=None,     # "video", "audio", or "image" (auto-detected if omitted)
    name=None,           # Custom name for the media
    description=None,    # Description
    callback_url=None,   # Webhook URL for async notification
)
```

## Video Object

```python
video = coll.get_video(video_id)
```

### Video Properties

| Property | Type | Description |
|----------|------|-------------|
| `video.id` | `str` | Unique video ID |
| `video.collection_id` | `str` | Parent collection ID |
| `video.name` | `str` | Video name |
| `video.description` | `str` | Video description |
| `video.length` | `float` | Duration in seconds |
| `video.stream_url` | `str` | Default stream URL |
| `video.player_url` | `str` | Player embed URL |
| `video.thumbnail_url` | `str` | Thumbnail URL |

### Video Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `video.generate_stream(timeline=None)` | `str` | Generate stream URL (optional timeline of `[(start, end)]` tuples) |
| `video.play()` | `str` | Open stream in browser, returns player URL |
| `video.index_spoken_words(language_code=None, force=False)` | `None` | Index speech for search. Use `force=True` to skip if already indexed. |
| `video.index_scenes(extraction_type, prompt, extraction_config, metadata, model_name, name, scenes, callback_url)` | `str` | Index visual scenes (returns scene_index_id) |
| `video.index_visuals(prompt, batch_config, ...)` | `str` | Index visuals (returns scene_index_id) |
| `video.index_audio(prompt, model_name, ...)` | `str` | Index audio with LLM (returns scene_index_id) |
| `video.get_transcript(start=None, end=None)` | `list[dict]` | Get timestamped transcript |
| `video.get_transcript_text(start=None, end=None)` | `str` | Get full transcript text |
| `video.generate_transcript(force=None)` | `dict` | Generate transcript |
| `video.translate_transcript(language, additional_notes)` | `list[dict]` | Translate transcript |
| `video.search(query, search_type, index_type, filter, **kwargs)` | `SearchResult` | Search within video |
| `video.add_subtitle(style=SubtitleStyle())` | `str` | Add subtitles (returns stream URL) |
| `video.generate_thumbnail(time=None)` | `str\|Image` | Generate thumbnail |
| `video.get_thumbnails()` | `list[Image]` | Get all thumbnails |
| `video.extract_scenes(extraction_type, extraction_config)` | `SceneCollection` | Extract scenes |
| `video.reframe(start, end, target, mode, callback_url)` | `Video\|None` | Reframe video aspect ratio |
| `video.clip(prompt, content_type, model_name)` | `str` | Generate clip from prompt (returns stream URL) |
| `video.insert_video(video, timestamp)` | `str` | Insert video at timestamp |
| `video.download(name=None)` | `dict` | Download the video |
| `video.delete()` | `None` | Delete the video |

### Reframe

Convert a video to a different aspect ratio with optional smart object tracking. Processing is server-side.

> **Warning:** Reframe is a slow server-side operation. It can take several minutes for long videos and may time out. Always use `start`/`end` to limit the segment, or pass `callback_url` for async processing.

```python
from videodb import ReframeMode

# Always prefer short segments to avoid timeouts:
reframed = video.reframe(start=0, end=60, target="vertical", mode=ReframeMode.smart)

# Async reframe for full-length videos (returns None, result via webhook):
video.reframe(target="vertical", callback_url="https://example.com/webhook")

# Custom dimensions
reframed = video.reframe(start=0, end=60, target={"width": 1080, "height": 1080})
```

#### reframe Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start` | `float\|None` | `None` | Start time in seconds (None = beginning) |
| `end` | `float\|None` | `None` | End time in seconds (None = end of video) |
| `target` | `str\|dict` | `"vertical"` | Preset string (`"vertical"`, `"square"`, `"landscape"`) or `{"width": int, "height": int}` |
| `mode` | `str` | `ReframeMode.smart` | `"simple"` (centre crop) or `"smart"` (object tracking) |
| `callback_url` | `str\|None` | `None` | Webhook URL for async notification |

Returns a `Video` object when no `callback_url` is provided, `None` otherwise.

## Audio Object

```python
audio = coll.get_audio(audio_id)
```

### Audio Properties

| Property | Type | Description |
|----------|------|-------------|
| `audio.id` | `str` | Unique audio ID |
| `audio.collection_id` | `str` | Parent collection ID |
| `audio.name` | `str` | Audio name |
| `audio.length` | `float` | Duration in seconds |

### Audio Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `audio.generate_url()` | `str` | Generate signed URL for playback |
| `audio.get_transcript(start=None, end=None)` | `list[dict]` | Get timestamped transcript |
| `audio.get_transcript_text(start=None, end=None)` | `str` | Get full transcript text |
| `audio.generate_transcript(force=None)` | `dict` | Generate transcript |
| `audio.delete()` | `None` | Delete the audio |

## Image Object

```python
image = coll.get_image(image_id)
```

### Image Properties

| Property | Type | Description |
|----------|------|-------------|
| `image.id` | `str` | Unique image ID |
| `image.collection_id` | `str` | Parent collection ID |
| `image.name` | `str` | Image name |
| `image.url` | `str\|None` | Image URL (may be `None` for generated images — use `generate_url()` instead) |

### Image Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `image.generate_url()` | `str` | Generate signed URL |
| `image.delete()` | `None` | Delete the image |

## Timeline & Editor

### Timeline

```python
from videodb.timeline import Timeline

timeline = Timeline(conn)
```

| Method | Returns | Description |
|--------|---------|-------------|
| `timeline.add_inline(asset)` | `None` | Add `VideoAsset` sequentially on main track |
| `timeline.add_overlay(start, asset)` | `None` | Overlay `AudioAsset`, `ImageAsset`, or `TextAsset` at timestamp |
| `timeline.generate_stream()` | `str` | Compile and get stream URL |

### Asset Types

#### VideoAsset

```python
from videodb.asset import VideoAsset

asset = VideoAsset(
    asset_id=video.id,
    start=0,              # trim start (seconds)
    end=None,             # trim end (seconds, None = full)
)
```

#### AudioAsset

```python
from videodb.asset import AudioAsset

asset = AudioAsset(
    asset_id=audio.id,
    start=0,
    end=None,
    disable_other_tracks=True,   # mute original audio when True
    fade_in_duration=0,          # seconds (max 5)
    fade_out_duration=0,         # seconds (max 5)
)
```

#### ImageAsset

```python
from videodb.asset import ImageAsset

asset = ImageAsset(
    asset_id=image.id,
    duration=None,        # display duration (seconds)
    width=100,            # display width
    height=100,           # display height
    x=80,                 # horizontal position (px from left)
    y=20,                 # vertical position (px from top)
)
```

#### TextAsset

```python
from videodb.asset import TextAsset, TextStyle

asset = TextAsset(
    text="Hello World",
    duration=5,
    style=TextStyle(
        fontsize=24,
        fontcolor="black",
        boxcolor="white",       # background box colour
        alpha=1.0,
        font="Sans",
        text_align="T",         # text alignment within box
    ),
)
```

#### CaptionAsset (Editor API)

CaptionAsset belongs to the Editor API, which has its own Timeline, Track, and Clip system:

```python
from videodb.editor import CaptionAsset, FontStyling

asset = CaptionAsset(
    src="auto",                    # "auto" or base64 ASS string
    font=FontStyling(name="Clear Sans", size=30),
    primary_color="&H00FFFFFF",
)
```

See [editor.md](editor.md#caption-overlays) for full CaptionAsset usage with the Editor API.

## Video Search Parameters

```python
results = video.search(
    query="your query",
    search_type=SearchType.semantic,       # semantic, keyword, or scene
    index_type=IndexType.spoken_word,      # spoken_word or scene
    result_threshold=None,                 # max number of results
    score_threshold=None,                  # minimum relevance score
    dynamic_score_percentage=None,         # percentage of dynamic score
    scene_index_id=None,                   # target a specific scene index (pass via **kwargs)
    filter=[],                             # metadata filters for scene search
)
```

> **Note:** `filter` is an explicit named parameter in `video.search()`. `scene_index_id` is passed through `**kwargs` to the API.
>
> **Important:** `video.search()` raises `InvalidRequestError` with message `"No results found"` when there are no matches. Always wrap search calls in try/except. For scene search, use `score_threshold=0.3` or higher to filter low-relevance noise.

For scene search, use `search_type=SearchType.semantic` with `index_type=IndexType.scene`. Pass `scene_index_id` when targeting a specific scene index. See [search.md](search.md) for details.

## SearchResult Object

```python
results = video.search("query", search_type=SearchType.semantic)
```

| Method | Returns | Description |
|--------|---------|-------------|
| `results.get_shots()` | `list[Shot]` | Get list of matching segments |
| `results.compile()` | `str` | Compile all shots into a stream URL |
| `results.play()` | `str` | Open compiled stream in browser |

### Shot Properties

| Property | Type | Description |
|----------|------|-------------|
| `shot.video_id` | `str` | Source video ID |
| `shot.video_length` | `float` | Source video duration |
| `shot.video_title` | `str` | Source video title |
| `shot.start` | `float` | Start time (seconds) |
| `shot.end` | `float` | End time (seconds) |
| `shot.text` | `str` | Matched text content |
| `shot.search_score` | `float` | Search relevance score |

| Method | Returns | Description |
|--------|---------|-------------|
| `shot.generate_stream()` | `str` | Stream this specific shot |
| `shot.play()` | `str` | Open shot stream in browser |

## Meeting Object

```python
meeting = coll.record_meeting(
    meeting_url="https://meet.google.com/...",
    bot_name="Bot",
    callback_url=None,          # Webhook URL for status updates
    callback_data=None,         # Optional dict passed through to callbacks
    time_zone="UTC",            # Time zone for the meeting
)
```

### Meeting Properties

| Property | Type | Description |
|----------|------|-------------|
| `meeting.id` | `str` | Unique meeting ID |
| `meeting.collection_id` | `str` | Parent collection ID |
| `meeting.status` | `str` | Current status |
| `meeting.video_id` | `str` | Recorded video ID (after completion) |
| `meeting.bot_name` | `str` | Bot name |
| `meeting.meeting_title` | `str` | Meeting title |
| `meeting.meeting_url` | `str` | Meeting URL |
| `meeting.speaker_timeline` | `dict` | Speaker timeline data |
| `meeting.is_active` | `bool` | True if initializing or processing |
| `meeting.is_completed` | `bool` | True if done |

### Meeting Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `meeting.refresh()` | `Meeting` | Refresh data from server |
| `meeting.wait_for_status(target_status, timeout=14400, interval=120)` | `bool` | Poll until status reached |

## RTStream & Capture

For RTStream (live ingestion, indexing, transcription), see [rtstream-reference.md](rtstream-reference.md).

For capture sessions (desktop recording, CaptureClient, channels), see [capture-reference.md](capture-reference.md).

## Enums & Constants

### SearchType

```python
from videodb import SearchType

SearchType.semantic    # Natural language semantic search
SearchType.keyword     # Exact keyword matching
SearchType.scene       # Visual scene search (may require paid plan)
SearchType.llm         # LLM-powered search
```

### SceneExtractionType

```python
from videodb import SceneExtractionType

SceneExtractionType.shot_based   # Automatic shot boundary detection
SceneExtractionType.time_based   # Fixed time interval extraction
SceneExtractionType.transcript   # Transcript-based scene extraction
```

### SubtitleStyle

```python
from videodb import SubtitleStyle

style = SubtitleStyle(
    font_name="Arial",
    font_size=18,
    primary_colour="&H00FFFFFF",
    bold=False,
    # ... see SubtitleStyle for all options
)
video.add_subtitle(style=style)
```

### SubtitleAlignment & SubtitleBorderStyle

```python
from videodb import SubtitleAlignment, SubtitleBorderStyle
```

### TextStyle

```python
from videodb import TextStyle
# or: from videodb.asset import TextStyle

style = TextStyle(
    fontsize=24,
    fontcolor="black",
    boxcolor="white",
    font="Sans",
    text_align="T",
    alpha=1.0,
)
```

### Other Constants

```python
from videodb import (
    IndexType,          # spoken_word, scene
    MediaType,          # video, audio, image
    Segmenter,          # word, sentence, time
    SegmentationType,   # sentence, llm
    TranscodeMode,      # economy, lightning
    ResizeMode,         # crop, fit, pad
    ReframeMode,        # simple, smart
    RTStreamChannelType,
)
```

## Exceptions

```python
from videodb.exceptions import (
    AuthenticationError,     # Invalid or missing API key
    InvalidRequestError,     # Bad parameters or malformed request
    RequestTimeoutError,     # Request timed out
    SearchError,             # Search operation failure (e.g. not indexed)
    VideodbError,            # Base exception for all VideoDB errors
)
```

| Exception | Common Cause |
|-----------|-------------|
| `AuthenticationError` | Missing or invalid `VIDEO_DB_API_KEY` |
| `InvalidRequestError` | Invalid URL, unsupported format, bad parameters |
| `RequestTimeoutError` | Server took too long to respond |
| `SearchError` | Searching before indexing, invalid search type |
| `VideodbError` | Server errors, network issues, generic failures |

<!-- ===== /file: videodb/reference/api-reference.md ===== -->

<!-- ===== file: videodb/reference/capture-reference.md ===== -->

# Capture Reference

Code-level details for VideoDB capture sessions. For workflow guide, see [capture.md](capture.md).

---

## WebSocket Events

Real-time events from capture sessions and AI pipelines. No webhooks or polling required.

Use [scripts/ws_listener.py](../scripts/ws_listener.py) to connect and dump events to `${VIDEODB_EVENTS_DIR:-$HOME/.local/state/videodb}/videodb_events.jsonl`.

### Event Channels

| Channel | Source | Content |
|---------|--------|---------|
| `capture_session` | Session lifecycle | Status changes |
| `transcript` | `start_transcript()` | Speech-to-text |
| `visual_index` / `scene_index` | `index_visuals()` | Visual analysis |
| `audio_index` | `index_audio()` | Audio analysis |
| `alert` | `create_alert()` | Alert notifications |

### Session Lifecycle Events

| Event | Status | Key Data |
|-------|--------|----------|
| `capture_session.created` | `created` | — |
| `capture_session.starting` | `starting` | — |
| `capture_session.active` | `active` | `rtstreams[]` |
| `capture_session.stopping` | `stopping` | — |
| `capture_session.stopped` | `stopped` | — |
| `capture_session.exported` | `exported` | `exported_video_id`, `stream_url`, `player_url` |
| `capture_session.failed` | `failed` | `error` |

### Event Structures

**Transcript event:**
```json
{
  "channel": "transcript",
  "rtstream_id": "rts-xxx",
  "rtstream_name": "mic:default",
  "data": {
    "text": "Let's schedule the meeting for Thursday",
    "is_final": true,
    "start": 1710000001234,
    "end": 1710000002345
  }
}
```

**Visual index event:**
```json
{
  "channel": "visual_index",
  "rtstream_id": "rts-xxx",
  "rtstream_name": "display:1",
  "data": {
    "text": "User is viewing a Slack conversation with 3 unread messages",
    "start": 1710000012340,
    "end": 1710000018900
  }
}
```

**Audio index event:**
```json
{
  "channel": "audio_index",
  "rtstream_id": "rts-xxx",
  "rtstream_name": "mic:default",
  "data": {
    "text": "Discussion about scheduling a team meeting",
    "start": 1710000021500,
    "end": 1710000029200
  }
}
```

**Session active event:**
```json
{
  "event": "capture_session.active",
  "capture_session_id": "cap-xxx",
  "status": "active",
  "data": {
    "rtstreams": [
      { "rtstream_id": "rts-1", "name": "mic:default", "media_types": ["audio"] },
      { "rtstream_id": "rts-2", "name": "system_audio:default", "media_types": ["audio"] },
      { "rtstream_id": "rts-3", "name": "display:1", "media_types": ["video"] }
    ]
  }
}
```

**Session exported event:**
```json
{
  "event": "capture_session.exported",
  "capture_session_id": "cap-xxx",
  "status": "exported",
  "data": {
    "exported_video_id": "v_xyz789",
    "stream_url": "https://stream.videodb.io/...",
    "player_url": "https://console.videodb.io/player?url=..."
  }
}
```

> For latest details, see [VideoDB Realtime Context docs](https://docs.videodb.io/pages/ingest/capture-sdks/realtime-context.md).

---

## Event Persistence

Use `ws_listener.py` to dump all WebSocket events to a JSONL file for later analysis.

### Start Listener and Get WebSocket ID

```bash
# Start with --clear to clear old events (recommended for new sessions)
python scripts/ws_listener.py --clear &

# Append to existing events (for reconnects)
python scripts/ws_listener.py &
```

Or specify a custom output directory:

```bash
python scripts/ws_listener.py --clear /path/to/output &
# Or via environment variable:
VIDEODB_EVENTS_DIR=/path/to/output python scripts/ws_listener.py --clear &
```

The script outputs `WS_ID=<connection_id>` on the first line, then listens indefinitely.

**Get the ws_id:**
```bash
cat "${VIDEODB_EVENTS_DIR:-$HOME/.local/state/videodb}/videodb_ws_id"
```

**Stop the listener:**
```bash
kill "$(cat "${VIDEODB_EVENTS_DIR:-$HOME/.local/state/videodb}/videodb_ws_pid")"
```

**Functions that accept `ws_connection_id`:**

| Function | Purpose |
|----------|---------|
| `conn.create_capture_session()` | Session lifecycle events |
| RTStream methods | See [rtstream-reference.md](rtstream-reference.md) |

**Output files** (in output directory, default `${XDG_STATE_HOME:-$HOME/.local/state}/videodb`):
- `videodb_ws_id` - WebSocket connection ID
- `videodb_events.jsonl` - All events
- `videodb_ws_pid` - Process ID for easy termination

**Features:**
- `--clear` flag to clear events file on start (use for new sessions)
- Auto-reconnect with exponential backoff on connection drops
- Graceful shutdown on SIGINT/SIGTERM
- Connection status logging

### JSONL Format

Each line is a JSON object with added timestamps:

```json
{"ts": "2026-03-02T10:15:30.123Z", "unix_ts": 1772446530.123, "channel": "visual_index", "data": {"text": "..."}}
{"ts": "2026-03-02T10:15:31.456Z", "unix_ts": 1772446531.456, "event": "capture_session.active", "capture_session_id": "cap-xxx"}
```

### Reading Events

```python
import json
import time
from pathlib import Path

events_path = Path.home() / ".local" / "state" / "videodb" / "videodb_events.jsonl"
transcripts = []
recent = []
visual = []

cutoff = time.time() - 600
with events_path.open(encoding="utf-8") as handle:
    for line in handle:
        event = json.loads(line)
        if event.get("channel") == "transcript":
            transcripts.append(event)
        if event.get("unix_ts", 0) > cutoff:
            recent.append(event)
        if (
            event.get("channel") == "visual_index"
            and "code" in event.get("data", {}).get("text", "").lower()
        ):
            visual.append(event)
```

---

## WebSocket Connection

Connect to receive real-time AI results from transcription and indexing pipelines.

```python
ws_wrapper = conn.connect_websocket()
ws = await ws_wrapper.connect()
ws_id = ws.connection_id
```

| Property / Method | Type | Description |
|-------------------|------|-------------|
| `ws.connection_id` | `str` | Unique connection ID (pass to AI pipeline methods) |
| `ws.receive()` | `AsyncIterator[dict]` | Async iterator yielding real-time messages |

---

## CaptureSession

### Connection Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `conn.create_capture_session(end_user_id, collection_id, ws_connection_id, metadata)` | `CaptureSession` | Create a new capture session |
| `conn.get_capture_session(capture_session_id)` | `CaptureSession` | Retrieve an existing capture session |
| `conn.generate_client_token()` | `str` | Generate a client-side authentication token |

### Create a Capture Session

```python
from pathlib import Path

ws_id = (Path.home() / ".local" / "state" / "videodb" / "videodb_ws_id").read_text().strip()

session = conn.create_capture_session(
    end_user_id="user-123",  # required
    collection_id="default",
    ws_connection_id=ws_id,
    metadata={"app": "my-app"},
)
print(f"Session ID: {session.id}")
```

> **Note:** `end_user_id` is required and identifies the user initiating the capture. For testing or demo purposes, any unique string identifier works (e.g., `"demo-user"`, `"test-123"`).

### CaptureSession Properties

| Property | Type | Description |
|----------|------|-------------|
| `session.id` | `str` | Unique capture session ID |

### CaptureSession Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `session.get_rtstream(type)` | `list[RTStream]` | Get RTStreams by type: `"mic"`, `"screen"`, or `"system_audio"` |

### Generate a Client Token

```python
token = conn.generate_client_token()
```

---

## CaptureClient

The client runs on the user's machine and handles permissions, channel discovery, and streaming.

```python
from videodb.capture import CaptureClient

client = CaptureClient(client_token=token)
```

### CaptureClient Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `await client.request_permission(type)` | `None` | Request device permission (`"microphone"`, `"screen_capture"`) |
| `await client.list_channels()` | `Channels` | Discover available audio/video channels |
| `await client.start_capture_session(capture_session_id, channels, primary_video_channel_id)` | `None` | Start streaming selected channels |
| `await client.stop_capture()` | `None` | Gracefully stop the capture session |
| `await client.shutdown()` | `None` | Clean up client resources |

### Request Permissions

```python
await client.request_permission("microphone")
await client.request_permission("screen_capture")
```

### Start a Session

```python
selected_channels = [c for c in [mic, display, system_audio] if c]
await client.start_capture_session(
    capture_session_id=session.id,
    channels=selected_channels,
    primary_video_channel_id=display.id if display else None,
)
```

### Stop a Session

```python
await client.stop_capture()
await client.shutdown()
```

---

## Channels

Returned by `client.list_channels()`. Groups available devices by type.

```python
channels = await client.list_channels()
for ch in channels.all():
    print(f"  {ch.id} ({ch.type}): {ch.name}")

mic = channels.mics.default
display = channels.displays.default
system_audio = channels.system_audio.default
```

### Channel Groups

| Property | Type | Description |
|----------|------|-------------|
| `channels.mics` | `ChannelGroup` | Available microphones |
| `channels.displays` | `ChannelGroup` | Available screen displays |
| `channels.system_audio` | `ChannelGroup` | Available system audio sources |

### ChannelGroup Methods & Properties

| Member | Type | Description |
|--------|------|-------------|
| `group.default` | `Channel` | Default channel in the group (or `None`) |
| `group.all()` | `list[Channel]` | All channels in the group |

### Channel Properties

| Property | Type | Description |
|----------|------|-------------|
| `ch.id` | `str` | Unique channel ID |
| `ch.type` | `str` | Channel type (`"mic"`, `"display"`, `"system_audio"`) |
| `ch.name` | `str` | Human-readable channel name |
| `ch.store` | `bool` | Whether to persist the recording (set to `True` to save) |

Without `store = True`, streams are processed in real-time but not saved.

---

## RTStreams and AI Pipelines

After session is active, retrieve RTStream objects with `session.get_rtstream()`.

For RTStream methods (indexing, transcription, alerts, batch config), see [rtstream-reference.md](rtstream-reference.md).

---

## Session Lifecycle

```
  create_capture_session()
          │
          v
  ┌───────────────┐
  │    created     │
  └───────┬───────┘
          │  client.start_capture_session()
          v
  ┌───────────────┐     WebSocket: capture_session.starting
  │   starting     │ ──> Capture channels connect
  └───────┬───────┘
          │
          v
  ┌───────────────┐     WebSocket: capture_session.active
  │    active      │ ──> Start AI pipelines
  └───────┬──────────────┐
          │              │
          │              v
          │      ┌───────────────┐     WebSocket: capture_session.failed
          │      │    failed      │ ──> Inspect error payload and retry setup
          │      └───────────────┘
          │      unrecoverable capture error
          │
          │  client.stop_capture()
          v
  ┌───────────────┐     WebSocket: capture_session.stopping
  │   stopping     │ ──> Finalize streams
  └───────┬───────┘
          │
          v
  ┌───────────────┐     WebSocket: capture_session.stopped
  │   stopped      │ ──> All streams finalized
  └───────┬───────┘
          │  (if store=True)
          v
  ┌───────────────┐     WebSocket: capture_session.exported
  │   exported     │ ──> Access video_id, stream_url, player_url
  └───────────────┘
```

<!-- ===== /file: videodb/reference/capture-reference.md ===== -->

<!-- ===== file: videodb/reference/capture.md ===== -->

# Capture Guide

## Overview

VideoDB Capture enables real-time screen and audio recording with AI processing. Desktop capture currently supports **macOS** only.

For code-level details (SDK methods, event structures, AI pipelines), see [capture-reference.md](capture-reference.md).

## Quick Start

1. **Start WebSocket listener**: `python scripts/ws_listener.py --clear &`
2. **Run capture code** (see Complete Capture Workflow below)
3. **Events written to**: `/tmp/videodb_events.jsonl`

---

## Complete Capture Workflow

No webhooks or polling required. WebSocket delivers all events including session lifecycle.

> **CRITICAL:** The `CaptureClient` must remain running for the entire duration of the capture. It runs the local recorder binary that streams screen/audio data to VideoDB. If the Python process that created the `CaptureClient` exits, the recorder binary is killed and capture stops silently. Always run the capture code as a **long-lived background process** (e.g. `nohup python capture_script.py &`) and use signal handling (`asyncio.Event` + `SIGINT`/`SIGTERM`) to keep it alive until you explicitly stop it.

1. **Start WebSocket listener** in background with `--clear` flag to clear old events. Wait for it to create the WebSocket ID file.

2. **Read the WebSocket ID**. This ID is required for capture session and AI pipelines.

3. **Create a capture session** and generate a client token for the desktop client.

4. **Initialize CaptureClient** with the token. Request permissions for microphone and screen capture.

5. **List and select channels** (mic, display, system_audio). Set `store = True` on channels you want to persist as a video.

6. **Start the session** with selected channels.

7. **Wait for session active** by reading events until you see `capture_session.active`. This event contains the `rtstreams` array. Save session info (session ID, RTStream IDs) to a file (e.g. `/tmp/videodb_capture_info.json`) so other scripts can read it.

8. **Keep the process alive.** Use `asyncio.Event` with signal handlers for `SIGINT`/`SIGTERM` to block until explicitly stopped. Write a PID file (e.g. `/tmp/videodb_capture_pid`) so the process can be stopped later with `kill $(cat /tmp/videodb_capture_pid)`. The PID file should be overwritten on every run so reruns always have the correct PID.

9. **Start AI pipelines** (in a separate command/script) on each RTStream for audio indexing and visual indexing. Read the RTStream IDs from the saved session info file.

10. **Write custom event processing logic** (in a separate command/script) to read real-time events based on your use case. Examples:
    - Log Slack activity when `visual_index` mentions "Slack"
    - Summarize discussions when `audio_index` events arrive
    - Trigger alerts when specific keywords appear in `transcript`
    - Track application usage from screen descriptions

11. **Stop capture** when done — send SIGTERM to the capture process. It should call `client.stop_capture()` and `client.shutdown()` in its signal handler.

12. **Wait for export** by reading events until you see `capture_session.exported`. This event contains `exported_video_id`, `stream_url`, and `player_url`. This may take several seconds after stopping capture.

13. **Stop WebSocket listener** after receiving the export event. Use `kill $(cat /tmp/videodb_ws_pid)` to cleanly terminate it.

---

## Shutdown Sequence

Proper shutdown order is important to ensure all events are captured:

1. **Stop the capture session** — `client.stop_capture()` then `client.shutdown()`
2. **Wait for export event** — poll `/tmp/videodb_events.jsonl` for `capture_session.exported`
3. **Stop the WebSocket listener** — `kill $(cat /tmp/videodb_ws_pid)`

Do NOT kill the WebSocket listener before receiving the export event, or you will miss the final video URLs.

---

## Scripts

| Script | Description |
|--------|-------------|
| `scripts/ws_listener.py` | WebSocket event listener (dumps to JSONL) |

### ws_listener.py Usage

```bash
# Start listener in background (append to existing events)
python scripts/ws_listener.py &

# Start listener with clear (new session, clears old events)
python scripts/ws_listener.py --clear &

# Custom output directory
python scripts/ws_listener.py --clear /path/to/events &

# Stop the listener
kill $(cat /tmp/videodb_ws_pid)
```

**Options:**
- `--clear`: Clear the events file before starting. Use when starting a new capture session.

**Output files:**
- `videodb_events.jsonl` - All WebSocket events
- `videodb_ws_id` - WebSocket connection ID (for `ws_connection_id` parameter)
- `videodb_ws_pid` - Process ID (for stopping the listener)

**Features:**
- Auto-reconnect with exponential backoff on connection drops
- Graceful shutdown on SIGINT/SIGTERM
- PID file for easy process management
- Connection status logging

<!-- ===== /file: videodb/reference/capture.md ===== -->

<!-- ===== file: videodb/reference/editor.md ===== -->

# Timeline Editing Guide

VideoDB provides a non-destructive timeline editor for composing videos from multiple assets, adding text and image overlays, mixing audio tracks, and trimming clips — all server-side without re-encoding or local tools. Use this for trimming, combining clips, overlaying audio/music on video, adding subtitles, and layering text or images.

## Prerequisites

Videos, audio, and images **must be uploaded** to a collection before they can be used as timeline assets. For caption overlays, the video must also be **indexed for spoken words**.

## Core Concepts

### Timeline

A `Timeline` is a virtual composition layer. Assets are placed on it either **inline** (sequentially on the main track) or as **overlays** (layered at a specific timestamp). Nothing modifies the original media; the final stream is compiled on demand.

```python
from videodb.timeline import Timeline

timeline = Timeline(conn)
```

### Assets

Every element on a timeline is an **asset**. VideoDB provides five asset types:

| Asset | Import | Primary Use |
|-------|--------|-------------|
| `VideoAsset` | `from videodb.asset import VideoAsset` | Video clips (trim, sequencing) |
| `AudioAsset` | `from videodb.asset import AudioAsset` | Music, SFX, narration |
| `ImageAsset` | `from videodb.asset import ImageAsset` | Logos, thumbnails, overlays |
| `TextAsset` | `from videodb.asset import TextAsset, TextStyle` | Titles, captions, lower-thirds |
| `CaptionAsset` | `from videodb.editor import CaptionAsset` | Auto-rendered subtitles (Editor API) |

## Building a Timeline

### Add Video Clips Inline

Inline assets play one after another on the main video track. The `add_inline` method only accepts `VideoAsset`:

```python
from videodb.asset import VideoAsset

video_a = coll.get_video(video_id_a)
video_b = coll.get_video(video_id_b)

timeline = Timeline(conn)
timeline.add_inline(VideoAsset(asset_id=video_a.id))
timeline.add_inline(VideoAsset(asset_id=video_b.id))

stream_url = timeline.generate_stream()
```

### Trim / Sub-clip

Use `start` and `end` on a `VideoAsset` to extract a portion:

```python
# Take only seconds 10–30 from the source video
clip = VideoAsset(asset_id=video.id, start=10, end=30)
timeline.add_inline(clip)
```

### VideoAsset Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `asset_id` | `str` | required | Video media ID |
| `start` | `float` | `0` | Trim start (seconds) |
| `end` | `float\|None` | `None` | Trim end (`None` = full) |

> **Warning:** The SDK does not validate negative timestamps. Passing `start=-5` is silently accepted but produces broken or unexpected output. Always ensure `start >= 0`, `start < end`, and `end <= video.length` before creating a `VideoAsset`.

## Text Overlays

Add titles, lower-thirds, or captions at any point on the timeline:

```python
from videodb.asset import TextAsset, TextStyle

title = TextAsset(
    text="Welcome to the Demo",
    duration=5,
    style=TextStyle(
        fontsize=36,
        fontcolor="white",
        boxcolor="black",
        alpha=0.8,
        font="Sans",
    ),
)

# Overlay the title at the very start (t=0)
timeline.add_overlay(0, title)
```

### TextStyle Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fontsize` | `int` | `24` | Font size in pixels |
| `fontcolor` | `str` | `"black"` | CSS colour name or hex |
| `fontcolor_expr` | `str` | `""` | Dynamic font colour expression |
| `alpha` | `float` | `1.0` | Text opacity (0.0–1.0) |
| `font` | `str` | `"Sans"` | Font family |
| `box` | `bool` | `True` | Enable background box |
| `boxcolor` | `str` | `"white"` | Background box colour |
| `boxborderw` | `str` | `"10"` | Box border width |
| `boxw` | `int` | `0` | Box width override |
| `boxh` | `int` | `0` | Box height override |
| `line_spacing` | `int` | `0` | Line spacing |
| `text_align` | `str` | `"T"` | Text alignment within the box |
| `y_align` | `str` | `"text"` | Vertical alignment reference |
| `borderw` | `int` | `0` | Text border width |
| `bordercolor` | `str` | `"black"` | Text border colour |
| `expansion` | `str` | `"normal"` | Text expansion mode |
| `basetime` | `int` | `0` | Base time for time-based expressions |
| `fix_bounds` | `bool` | `False` | Fix text bounds |
| `text_shaping` | `bool` | `True` | Enable text shaping |
| `shadowcolor` | `str` | `"black"` | Shadow colour |
| `shadowx` | `int` | `0` | Shadow X offset |
| `shadowy` | `int` | `0` | Shadow Y offset |
| `tabsize` | `int` | `4` | Tab size in spaces |
| `x` | `str` | `"(main_w-text_w)/2"` | Horizontal position expression |
| `y` | `str` | `"(main_h-text_h)/2"` | Vertical position expression |

## Audio Overlays

Layer background music, sound effects, or voiceover on top of the video track:

```python
from videodb.asset import AudioAsset

music = coll.get_audio(music_id)

audio_layer = AudioAsset(
    asset_id=music.id,
    disable_other_tracks=False,
    fade_in_duration=2,
    fade_out_duration=2,
)

# Start the music at t=0, overlaid on the video track
timeline.add_overlay(0, audio_layer)
```

### AudioAsset Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `asset_id` | `str` | required | Audio media ID |
| `start` | `float` | `0` | Trim start (seconds) |
| `end` | `float\|None` | `None` | Trim end (`None` = full) |
| `disable_other_tracks` | `bool` | `True` | When True, mutes other audio tracks |
| `fade_in_duration` | `float` | `0` | Fade-in seconds (max 5) |
| `fade_out_duration` | `float` | `0` | Fade-out seconds (max 5) |

## Image Overlays

Add logos, watermarks, or generated images as overlays:

```python
from videodb.asset import ImageAsset

logo = coll.get_image(logo_id)

logo_overlay = ImageAsset(
    asset_id=logo.id,
    duration=10,
    width=120,
    height=60,
    x=20,
    y=20,
)

timeline.add_overlay(0, logo_overlay)
```

### ImageAsset Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `asset_id` | `str` | required | Image media ID |
| `width` | `int\|str` | `100` | Display width |
| `height` | `int\|str` | `100` | Display height |
| `x` | `int` | `80` | Horizontal position (px from left) |
| `y` | `int` | `20` | Vertical position (px from top) |
| `duration` | `float\|None` | `None` | Display duration (seconds) |

## Caption Overlays

There are two ways to add captions to video.

### Method 1: Subtitle Workflow (simplest)

Use `video.add_subtitle()` to burn subtitles directly onto a video stream. This uses the `videodb.timeline.Timeline` internally:

```python
from videodb import SubtitleStyle

# Video must have spoken words indexed first (force=True skips if already done)
video.index_spoken_words(force=True)

# Add subtitles with default styling
stream_url = video.add_subtitle()

# Or customise the subtitle style
stream_url = video.add_subtitle(style=SubtitleStyle(
    font_name="Arial",
    font_size=22,
    primary_colour="&H00FFFFFF",
    bold=True,
))
```

### Method 2: Editor API (advanced)

The Editor API (`videodb.editor`) provides a track-based composition system with `CaptionAsset`, `Clip`, `Track`, and its own `Timeline`. This is a separate API from the `videodb.timeline.Timeline` used above.

```python
from videodb.editor import (
    CaptionAsset,
    Clip,
    Track,
    Timeline as EditorTimeline,
    FontStyling,
    BorderAndShadow,
    Positioning,
    CaptionAnimation,
)

# Video must have spoken words indexed first (force=True skips if already done)
video.index_spoken_words(force=True)

# Create a caption asset
caption = CaptionAsset(
    src="auto",
    font=FontStyling(name="Clear Sans", size=30),
    primary_color="&H00FFFFFF",
    back_color="&H00000000",
    border=BorderAndShadow(outline=1),
    position=Positioning(margin_v=30),
    animation=CaptionAnimation.box_highlight,
)

# Build an editor timeline with tracks and clips
editor_tl = EditorTimeline(conn)
track = Track()
track.add_clip(start=0, clip=Clip(asset=caption, duration=video.length))
editor_tl.add_track(track)
stream_url = editor_tl.generate_stream()
```

### CaptionAsset Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `src` | `str` | `"auto"` | Caption source (`"auto"` or base64 ASS string) |
| `font` | `FontStyling\|None` | `FontStyling()` | Font styling (name, size, bold, italic, etc.) |
| `primary_color` | `str` | `"&H00FFFFFF"` | Primary text colour (ASS format) |
| `secondary_color` | `str` | `"&H000000FF"` | Secondary text colour (ASS format) |
| `back_color` | `str` | `"&H00000000"` | Background colour (ASS format) |
| `border` | `BorderAndShadow\|None` | `BorderAndShadow()` | Border and shadow styling |
| `position` | `Positioning\|None` | `Positioning()` | Caption alignment and margins |
| `animation` | `CaptionAnimation\|None` | `None` | Animation effect (e.g., `box_highlight`, `reveal`, `karaoke`) |

## Compiling & Streaming

After assembling a timeline, compile it into a streamable URL. Streams are generated instantly - no render wait times.

```python
stream_url = timeline.generate_stream()
print(f"Stream: {stream_url}")
```

For more streaming options (segment streams, search-to-stream, audio playback), see [streaming.md](streaming.md).

## Complete Workflow Examples

### Highlight Reel with Title Card

```python
import videodb
from videodb import SearchType
from videodb.exceptions import InvalidRequestError
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, TextAsset, TextStyle

conn = videodb.connect()
coll = conn.get_collection()
video = coll.get_video("your-video-id")

# 1. Search for key moments
video.index_spoken_words(force=True)
try:
    results = video.search("product announcement", search_type=SearchType.semantic)
    shots = results.get_shots()
except InvalidRequestError as exc:
    if "No results found" in str(exc):
        shots = []
    else:
        raise

# 2. Build timeline
timeline = Timeline(conn)

# Title card
title = TextAsset(
    text="Product Launch Highlights",
    duration=4,
    style=TextStyle(fontsize=48, fontcolor="white", boxcolor="#1a1a2e", alpha=0.95),
)
timeline.add_overlay(0, title)

# Append each matching clip
for shot in shots:
    asset = VideoAsset(asset_id=shot.video_id, start=shot.start, end=shot.end)
    timeline.add_inline(asset)

# 3. Generate stream
stream_url = timeline.generate_stream()
print(f"Highlight reel: {stream_url}")
```

### Logo Overlay with Background Music

```python
import videodb
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, AudioAsset, ImageAsset

conn = videodb.connect()
coll = conn.get_collection()

main_video = coll.get_video(main_video_id)
music = coll.get_audio(music_id)
logo = coll.get_image(logo_id)

timeline = Timeline(conn)

# Main video track
timeline.add_inline(VideoAsset(asset_id=main_video.id))

# Background music — disable_other_tracks=False to mix with video audio
timeline.add_overlay(
    0,
    AudioAsset(asset_id=music.id, disable_other_tracks=False, fade_in_duration=3),
)

# Logo in top-right corner for first 10 seconds
timeline.add_overlay(
    0,
    ImageAsset(asset_id=logo.id, duration=10, x=1140, y=20, width=120, height=60),
)

stream_url = timeline.generate_stream()
print(f"Final video: {stream_url}")
```

### Multi-Clip Montage from Multiple Videos

```python
import videodb
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, TextAsset, TextStyle

conn = videodb.connect()
coll = conn.get_collection()

clips = [
    {"video_id": "vid_001", "start": 5, "end": 15, "label": "Scene 1"},
    {"video_id": "vid_002", "start": 0, "end": 20, "label": "Scene 2"},
    {"video_id": "vid_003", "start": 30, "end": 45, "label": "Scene 3"},
]

timeline = Timeline(conn)
timeline_offset = 0.0

for clip in clips:
    # Add a label as an overlay on each clip
    label = TextAsset(
        text=clip["label"],
        duration=2,
        style=TextStyle(fontsize=32, fontcolor="white", boxcolor="#333333"),
    )
    timeline.add_inline(
        VideoAsset(asset_id=clip["video_id"], start=clip["start"], end=clip["end"])
    )
    timeline.add_overlay(timeline_offset, label)
    timeline_offset += clip["end"] - clip["start"]

stream_url = timeline.generate_stream()
print(f"Montage: {stream_url}")
```

## Two Timeline APIs

VideoDB has two separate timeline systems. They are **not interchangeable**:

| | `videodb.timeline.Timeline` | `videodb.editor.Timeline` (Editor API) |
|---|---|---|
| **Import** | `from videodb.timeline import Timeline` | `from videodb.editor import Timeline as EditorTimeline` |
| **Assets** | `VideoAsset`, `AudioAsset`, `ImageAsset`, `TextAsset` | `CaptionAsset`, `Clip`, `Track` |
| **Methods** | `add_inline()`, `add_overlay()` | `add_track()` with `Track` / `Clip` |
| **Best for** | Video composition, overlays, multi-clip editing | Caption/subtitle styling with animations |

Do not mix assets from one API into the other. `CaptionAsset` only works with the Editor API. `VideoAsset` / `AudioAsset` / `ImageAsset` / `TextAsset` only work with `videodb.timeline.Timeline`.

## Limitations & Constraints

The timeline editor is designed for **non-destructive linear composition**. The following operations are **not supported**:

### Not Possible

| Limitation | Detail |
|---|---|
| **No transitions or effects** | No crossfades, wipes, dissolves, or transitions between clips. All cuts are hard cuts. |
| **No video-on-video (picture-in-picture)** | `add_inline()` only accepts `VideoAsset`. You cannot overlay one video stream on top of another. Image overlays can approximate static PiP but not live video. |
| **No speed or playback control** | No slow-motion, fast-forward, reverse playback, or time remapping. `VideoAsset` has no `speed` parameter. |
| **No crop, zoom, or pan** | Cannot crop a region of a video frame, apply zoom effects, or pan across a frame. `video.reframe()` is for aspect-ratio conversion only. |
| **No video filters or color grading** | No brightness, contrast, saturation, hue, or color correction adjustments. |
| **No animated text** | `TextAsset` is static for its full duration. No fade-in/out, movement, or animation. For animated captions, use `CaptionAsset` with the Editor API. |
| **No mixed text styling** | A single `TextAsset` has one `TextStyle`. Cannot mix bold, italic, or colors within a single text block. |
| **No blank or solid-color clips** | Cannot create a solid color frame, black screen, or standalone title card. Text and image overlays require a `VideoAsset` beneath them on the inline track. |
| **No audio volume control** | `AudioAsset` has no `volume` parameter. Audio is either full volume or muted via `disable_other_tracks`. Cannot mix at a reduced level. |
| **No keyframe animation** | Cannot change overlay properties over time (e.g., move an image from position A to B). |

### Constraints

| Constraint | Detail |
|---|---|
| **Audio fade max 5 seconds** | `fade_in_duration` and `fade_out_duration` are capped at 5 seconds each. |
| **Overlay positioning is absolute** | Overlays use absolute timestamps from the timeline start. Rearranging inline clips does not move their overlays. |
| **Inline track is video only** | `add_inline()` only accepts `VideoAsset`. Audio, image, and text must use `add_overlay()`. |
| **No overlay-to-clip binding** | Overlays are placed at a fixed timeline timestamp. There is no way to attach an overlay to a specific inline clip so it moves with it. |

## Tips

- **Non-destructive**: Timelines never modify source media. You can create multiple timelines from the same assets.
- **Overlay stacking**: Multiple overlays can start at the same timestamp. Audio overlays mix together; image/text overlays layer in add-order.
- **Inline is VideoAsset only**: `add_inline()` only accepts `VideoAsset`. Use `add_overlay()` for `AudioAsset`, `ImageAsset`, and `TextAsset`.
- **Trim precision**: `start`/`end` on `VideoAsset` and `AudioAsset` are in seconds.
- **Muting video audio**: Set `disable_other_tracks=True` on `AudioAsset` to mute the original video audio when overlaying music or narration.
- **Fade limits**: `fade_in_duration` and `fade_out_duration` on `AudioAsset` have a maximum of 5 seconds.
- **Generated media**: Use `coll.generate_music()`, `coll.generate_sound_effect()`, `coll.generate_voice()`, and `coll.generate_image()` to create media that can be used as timeline assets immediately.

<!-- ===== /file: videodb/reference/editor.md ===== -->

<!-- ===== file: videodb/reference/generative.md ===== -->

# Generative Media Guide

VideoDB provides AI-powered generation of images, videos, music, sound effects, voice, and text content. All generation methods are on the **Collection** object.

## Prerequisites

You need a connection and a collection reference before calling any generation method:

```python
import videodb

conn = videodb.connect()
coll = conn.get_collection()
```

## Image Generation

Generate images from text prompts:

```python
image = coll.generate_image(
    prompt="a futuristic cityscape at sunset with flying cars",
    aspect_ratio="16:9",
)

# Access the generated image
print(image.id)
print(image.generate_url())  # returns a signed download URL
```

### generate_image Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | required | Text description of the image to generate |
| `aspect_ratio` | `str` | `"1:1"` | Aspect ratio: `"1:1"`, `"9:16"`, `"16:9"`, `"4:3"`, or `"3:4"` |
| `callback_url` | `str\|None` | `None` | URL to receive async callback |

Returns an `Image` object with `.id`, `.name`, and `.collection_id`. The `.url` property may be `None` for generated images — always use `image.generate_url()` to get a reliable signed download URL.

> **Note:** Unlike `Video` objects (which use `.generate_stream()`), `Image` objects use `.generate_url()` to retrieve the image URL. The `.url` property is only populated for some image types (e.g. thumbnails).

## Video Generation

Generate short video clips from text prompts:

```python
video = coll.generate_video(
    prompt="a timelapse of a flower blooming in a garden",
    duration=5,
)

stream_url = video.generate_stream()
video.play()
```

### generate_video Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | required | Text description of the video to generate |
| `duration` | `int` | `5` | Duration in seconds (must be integer value, 5-8) |
| `callback_url` | `str\|None` | `None` | URL to receive async callback |

Returns a `Video` object. Generated videos are automatically added to the collection and can be used in timelines, searches, and compilations like any uploaded video.

## Audio Generation

VideoDB provides three separate methods for different audio types.

### Music

Generate background music from text descriptions:

```python
music = coll.generate_music(
    prompt="upbeat electronic music with a driving beat, suitable for a tech demo",
    duration=30,
)

print(music.id)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | required | Text description of the music |
| `duration` | `int` | `5` | Duration in seconds |
| `callback_url` | `str\|None` | `None` | URL to receive async callback |

### Sound Effects

Generate specific sound effects:

```python
sfx = coll.generate_sound_effect(
    prompt="thunderstorm with heavy rain and distant thunder",
    duration=10,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | required | Text description of the sound effect |
| `duration` | `int` | `2` | Duration in seconds |
| `config` | `dict` | `{}` | Additional configuration |
| `callback_url` | `str\|None` | `None` | URL to receive async callback |

### Voice (Text-to-Speech)

Generate speech from text:

```python
voice = coll.generate_voice(
    text="Welcome to our product demo. Today we'll walk through the key features.",
    voice_name="Default",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | required | Text to convert to speech |
| `voice_name` | `str` | `"Default"` | Voice to use |
| `config` | `dict` | `{}` | Additional configuration |
| `callback_url` | `str\|None` | `None` | URL to receive async callback |

All three audio methods return an `Audio` object with `.id`, `.name`, `.length`, and `.collection_id`.

## Text Generation (LLM Integration)

Use `coll.generate_text()` to run LLM analysis. This is a **Collection-level** method -- pass any context (transcripts, descriptions) directly in the prompt string.

```python
# Get transcript from a video first
transcript_text = video.get_transcript_text()

# Generate analysis using collection LLM
result = coll.generate_text(
    prompt=f"Summarize the key points discussed in this video:\n{transcript_text}",
    model_name="pro",
)

print(result["output"])
```

### generate_text Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | required | Prompt with context for the LLM |
| `model_name` | `str` | `"basic"` | Model tier: `"basic"`, `"pro"`, or `"ultra"` |
| `response_type` | `str` | `"text"` | Response format: `"text"` or `"json"` |

Returns a `dict` with an `output` key. When `response_type="text"`, `output` is a `str`. When `response_type="json"`, `output` is a `dict`.

```python
result = coll.generate_text(prompt="Summarize this", model_name="pro")
print(result["output"])  # access the actual text/dict
```

### Analyze Scenes with LLM

Combine scene extraction with text generation:

```python
from videodb import SceneExtractionType

# First index scenes
scenes = video.index_scenes(
    extraction_type=SceneExtractionType.time_based,
    extraction_config={"time": 10},
    prompt="Describe the visual content in this scene.",
)

# Get transcript for spoken context
transcript_text = video.get_transcript_text()
scene_descriptions = []
for scene in scenes:
    if isinstance(scene, dict):
        description = scene.get("description") or scene.get("summary")
    else:
        description = getattr(scene, "description", None) or getattr(scene, "summary", None)
    scene_descriptions.append(description or str(scene))

scenes_text = "\n".join(scene_descriptions)

# Analyze with collection LLM
result = coll.generate_text(
    prompt=(
        f"Given this video transcript:\n{transcript_text}\n\n"
        f"And these visual scene descriptions:\n{scenes_text}\n\n"
        "Based on the spoken and visual content, describe the main topics covered."
    ),
    model_name="pro",
)
print(result["output"])
```

## Dubbing and Translation

### Dub a Video

Dub a video into another language using the collection method:

```python
dubbed_video = coll.dub_video(
    video_id=video.id,
    language_code="es",  # Spanish
)

dubbed_video.play()
```

### dub_video Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `video_id` | `str` | required | ID of the video to dub |
| `language_code` | `str` | required | Target language code (e.g., `"es"`, `"fr"`, `"de"`) |
| `callback_url` | `str\|None` | `None` | URL to receive async callback |

Returns a `Video` object with the dubbed content.

### Translate Transcript

Translate a video's transcript without dubbing:

```python
translated = video.translate_transcript(
    language="Spanish",
    additional_notes="Use formal tone",
)

for entry in translated:
    print(entry)
```

**Supported languages** include: `en`, `es`, `fr`, `de`, `it`, `pt`, `ja`, `ko`, `zh`, `hi`, `ar`, and more.

## Complete Workflow Examples

### Generate Narration for a Video

```python
import videodb

conn = videodb.connect()
coll = conn.get_collection()
video = coll.get_video("your-video-id")

# Get transcript
transcript_text = video.get_transcript_text()

# Generate narration script using collection LLM
result = coll.generate_text(
    prompt=(
        f"Write a professional narration script for this video content:\n"
        f"{transcript_text[:2000]}"
    ),
    model_name="pro",
)
script = result["output"]

# Convert script to speech
narration = coll.generate_voice(text=script)
print(f"Narration audio: {narration.id}")
```

### Generate Thumbnail from Prompt

```python
thumbnail = coll.generate_image(
    prompt="professional video thumbnail showing data analytics dashboard, modern design",
    aspect_ratio="16:9",
)
print(f"Thumbnail URL: {thumbnail.generate_url()}")
```

### Add Generated Music to Video

```python
import videodb
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, AudioAsset

conn = videodb.connect()
coll = conn.get_collection()
video = coll.get_video("your-video-id")

# Generate background music
music = coll.generate_music(
    prompt="calm ambient background music for a tutorial video",
    duration=60,
)

# Build timeline with video + music overlay
timeline = Timeline(conn)
timeline.add_inline(VideoAsset(asset_id=video.id))
timeline.add_overlay(0, AudioAsset(asset_id=music.id, disable_other_tracks=False))

stream_url = timeline.generate_stream()
print(f"Video with music: {stream_url}")
```

### Structured JSON Output

```python
transcript_text = video.get_transcript_text()

result = coll.generate_text(
    prompt=(
        f"Given this transcript:\n{transcript_text}\n\n"
        "Return a JSON object with keys: summary, topics (array), action_items (array)."
    ),
    model_name="pro",
    response_type="json",
)

# result["output"] is a dict when response_type="json"
print(result["output"]["summary"])
print(result["output"]["topics"])
```

## Tips

- **Generated media is persistent**: All generated content is stored in your collection and can be reused.
- **Three audio methods**: Use `generate_music()` for background music, `generate_sound_effect()` for SFX, and `generate_voice()` for text-to-speech. There is no unified `generate_audio()` method.
- **Text generation is collection-level**: `coll.generate_text()` does not have access to video content automatically. Fetch the transcript with `video.get_transcript_text()` and pass it in the prompt.
- **Model tiers**: `"basic"` is fastest, `"pro"` is balanced, `"ultra"` is highest quality. Use `"pro"` for most analysis tasks.
- **Combine generation types**: Generate images for overlays, music for backgrounds, and voice for narration, then compose using timelines (see [editor.md](editor.md)).
- **Prompt quality matters**: Descriptive, specific prompts produce better results across all generation types.
- **Aspect ratios for images**: Choose from `"1:1"`, `"9:16"`, `"16:9"`, `"4:3"`, or `"3:4"`.

<!-- ===== /file: videodb/reference/generative.md ===== -->

<!-- ===== file: videodb/reference/rtstream-reference.md ===== -->

# RTStream Reference

Code-level details for RTStream operations. For workflow guide, see [rtstream.md](rtstream.md).
For usage guidance and workflow selection, start with [../SKILL.md](../SKILL.md).

Based on [docs.videodb.io](https://docs.videodb.io/pages/ingest/live-streams/realtime-apis.md).

---

## Collection RTStream Methods

Methods on `Collection` for managing RTStreams:

| Method | Returns | Description |
|--------|---------|-------------|
| `coll.connect_rtstream(url, name, ...)` | `RTStream` | Create new RTStream from RTSP/RTMP URL |
| `coll.get_rtstream(id)` | `RTStream` | Get existing RTStream by ID |
| `coll.list_rtstreams(limit, offset, status, name, ordering)` | `List[RTStream]` | List all RTStreams in collection |
| `coll.search(query, namespace="rtstream")` | `RTStreamSearchResult` | Search across all RTStreams |

### Connect RTStream

```python
import videodb

conn = videodb.connect()
coll = conn.get_collection()

rtstream = coll.connect_rtstream(
    url="rtmp://your-stream-server/live/stream-key",
    name="My Live Stream",
    media_types=["video"],  # or ["audio", "video"]
    sample_rate=30,         # optional
    store=True,             # enable recording storage for export
    enable_transcript=True, # optional
    ws_connection_id=ws_id, # optional, for real-time events
)
```

### Get Existing RTStream

```python
rtstream = coll.get_rtstream("rts-xxx")
```

### List RTStreams

```python
rtstreams = coll.list_rtstreams(
    limit=10,
    offset=0,
    status="connected",  # optional filter
    name="meeting",      # optional filter
    ordering="-created_at",
)

for rts in rtstreams:
    print(f"{rts.id}: {rts.name} - {rts.status}")
```

### From Capture Session

After a capture session is active, retrieve RTStream objects:

```python
session = conn.get_capture_session(session_id)

mics = session.get_rtstream("mic")
displays = session.get_rtstream("screen")
system_audios = session.get_rtstream("system_audio")
```

Or use the `rtstreams` data from the `capture_session.active` WebSocket event:

```python
for rts in rtstreams:
    rtstream = coll.get_rtstream(rts["rtstream_id"])
```

---

## RTStream Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `rtstream.start()` | `None` | Begin ingestion |
| `rtstream.stop()` | `None` | Stop ingestion |
| `rtstream.generate_stream(start, end)` | `str` | Stream recorded segment (Unix timestamps) |
| `rtstream.export(name=None)` | `RTStreamExportResult` | Export to permanent video |
| `rtstream.index_visuals(prompt, ...)` | `RTStreamSceneIndex` | Create visual index with AI analysis |
| `rtstream.index_audio(prompt, ...)` | `RTStreamSceneIndex` | Create audio index with LLM summarization |
| `rtstream.list_scene_indexes()` | `List[RTStreamSceneIndex]` | List all scene indexes on the stream |
| `rtstream.get_scene_index(index_id)` | `RTStreamSceneIndex` | Get a specific scene index |
| `rtstream.search(query, ...)` | `RTStreamSearchResult` | Search indexed content |
| `rtstream.start_transcript(ws_connection_id, engine)` | `dict` | Start live transcription |
| `rtstream.get_transcript(page, page_size, start, end, since)` | `dict` | Get transcript pages |
| `rtstream.stop_transcript(engine)` | `dict` | Stop transcription |

---

## Starting and Stopping

```python
# Begin ingestion
rtstream.start()

# ... stream is being recorded ...

# Stop ingestion
rtstream.stop()
```

---

## Generating Streams

Use Unix timestamps (not seconds offsets) to generate a playback stream from recorded content:

```python
import time

start_ts = time.time()
rtstream.start()

# Let it record for a while...
time.sleep(60)

end_ts = time.time()
rtstream.stop()

# Generate a stream URL for the recorded segment
stream_url = rtstream.generate_stream(start=start_ts, end=end_ts)
print(f"Recorded stream: {stream_url}")
```

---

## Exporting to Video

Export the recorded stream to a permanent video in the collection:

```python
export_result = rtstream.export(name="Meeting Recording 2024-01-15")

print(f"Video ID: {export_result.video_id}")
print(f"Stream URL: {export_result.stream_url}")
print(f"Player URL: {export_result.player_url}")
print(f"Duration: {export_result.duration}s")
```

### RTStreamExportResult Properties

| Property | Type | Description |
|----------|------|-------------|
| `video_id` | `str` | ID of the exported video |
| `stream_url` | `str` | HLS stream URL |
| `player_url` | `str` | Web player URL |
| `name` | `str` | Video name |
| `duration` | `float` | Duration in seconds |

---

## AI Pipelines

AI pipelines process live streams and send results via WebSocket.

### RTStream AI Pipeline Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `rtstream.index_audio(prompt, batch_config, ...)` | `RTStreamSceneIndex` | Start audio indexing with LLM summarization |
| `rtstream.index_visuals(prompt, batch_config, ...)` | `RTStreamSceneIndex` | Start visual indexing of screen content |

### Audio Indexing

Generate LLM summaries of audio content at intervals:

```python
audio_index = rtstream.index_audio(
    prompt="Summarize what is being discussed",
    batch_config={"type": "word", "value": 50},
    model_name=None,       # optional
    name="meeting_audio",  # optional
    ws_connection_id=ws_id,
)
```

**Audio batch_config options:**

| Type | Value | Description |
|------|-------|-------------|
| `"word"` | count | Segment every N words |
| `"sentence"` | count | Segment every N sentences |
| `"time"` | seconds | Segment every N seconds |

Examples:
```python
{"type": "word", "value": 50}      # every 50 words
{"type": "sentence", "value": 5}   # every 5 sentences
{"type": "time", "value": 30}      # every 30 seconds
```

Results arrive on the `audio_index` WebSocket channel.

### Visual Indexing

Generate AI descriptions of visual content:

```python
scene_index = rtstream.index_visuals(
    prompt="Describe what is happening on screen",
    batch_config={"type": "time", "value": 2, "frame_count": 5},
    model_name="basic",
    name="screen_monitor",  # optional
    ws_connection_id=ws_id,
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `prompt` | `str` | Instructions for the AI model (supports structured JSON output) |
| `batch_config` | `dict` | Controls frame sampling (see below) |
| `model_name` | `str` | Model tier: `"mini"`, `"basic"`, `"pro"`, `"ultra"` |
| `name` | `str` | Name for the index (optional) |
| `ws_connection_id` | `str` | WebSocket connection ID for receiving results |

**Visual batch_config:**

| Key | Type | Description |
|-----|------|-------------|
| `type` | `str` | Only `"time"` is supported for visuals |
| `value` | `int` | Window size in seconds |
| `frame_count` | `int` | Number of frames to extract per window |

Example: `{"type": "time", "value": 2, "frame_count": 5}` samples 5 frames every 2 seconds and sends them to the model.

**Structured JSON output:**

Use a prompt that requests JSON format for structured responses:

```python
scene_index = rtstream.index_visuals(
    prompt="""Analyze the screen and return a JSON object with:
{
  "app_name": "name of the active application",
  "activity": "what the user is doing",
  "ui_elements": ["list of visible UI elements"],
  "contains_text": true/false,
  "dominant_colors": ["list of main colors"]
}
Return only valid JSON.""",
    batch_config={"type": "time", "value": 3, "frame_count": 3},
    model_name="pro",
    ws_connection_id=ws_id,
)
```

Results arrive on the `scene_index` WebSocket channel.

---

## Batch Config Summary

| Indexing Type | `type` Options | `value` | Extra Keys |
|---------------|----------------|---------|------------|
| **Audio** | `"word"`, `"sentence"`, `"time"` | words/sentences/seconds | - |
| **Visual** | `"time"` only | seconds | `frame_count` |

Examples:
```python
# Audio: every 50 words
{"type": "word", "value": 50}

# Audio: every 30 seconds
{"type": "time", "value": 30}

# Visual: 5 frames every 2 seconds
{"type": "time", "value": 2, "frame_count": 5}
```

---

## Transcription

Real-time transcription via WebSocket:

```python
# Start live transcription
rtstream.start_transcript(
    ws_connection_id=ws_id,
    engine=None,  # optional, defaults to "assemblyai"
)

# Get transcript pages (with optional filters)
transcript = rtstream.get_transcript(
    page=1,
    page_size=100,
    start=None,   # optional: start timestamp filter
    end=None,     # optional: end timestamp filter
    since=None,   # optional: for polling, get transcripts after this timestamp
    engine=None,
)

# Stop transcription
rtstream.stop_transcript(engine=None)
```

Transcript results arrive on the `transcript` WebSocket channel.

---

## RTStreamSceneIndex

When you call `index_audio()` or `index_visuals()`, the method returns an `RTStreamSceneIndex` object. This object represents the running index and provides methods for managing scenes and alerts.

```python
# index_visuals returns an RTStreamSceneIndex
scene_index = rtstream.index_visuals(
    prompt="Describe what is on screen",
    ws_connection_id=ws_id,
)

# index_audio also returns an RTStreamSceneIndex
audio_index = rtstream.index_audio(
    prompt="Summarize the discussion",
    ws_connection_id=ws_id,
)
```

### RTStreamSceneIndex Properties

| Property | Type | Description |
|----------|------|-------------|
| `rtstream_index_id` | `str` | Unique ID of the index |
| `rtstream_id` | `str` | ID of the parent RTStream |
| `extraction_type` | `str` | Type of extraction (`time` or `transcript`) |
| `extraction_config` | `dict` | Extraction configuration |
| `prompt` | `str` | The prompt used for analysis |
| `name` | `str` | Name of the index |
| `status` | `str` | Status (`connected`, `stopped`) |

### RTStreamSceneIndex Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `index.get_scenes(start, end, page, page_size)` | `dict` | Get indexed scenes |
| `index.start()` | `None` | Start/resume the index |
| `index.stop()` | `None` | Stop the index |
| `index.create_alert(event_id, callback_url, ws_connection_id)` | `str` | Create alert for event detection |
| `index.list_alerts()` | `list` | List all alerts on this index |
| `index.enable_alert(alert_id)` | `None` | Enable an alert |
| `index.disable_alert(alert_id)` | `None` | Disable an alert |

### Getting Scenes

Poll indexed scenes from the index:

```python
result = scene_index.get_scenes(
    start=None,      # optional: start timestamp
    end=None,        # optional: end timestamp
    page=1,
    page_size=100,
)

for scene in result["scenes"]:
    print(f"[{scene['start']}-{scene['end']}] {scene['text']}")

if result["next_page"]:
    # fetch next page
    pass
```

### Managing Scene Indexes

```python
# List all indexes on the stream
indexes = rtstream.list_scene_indexes()

# Get a specific index by ID
scene_index = rtstream.get_scene_index(index_id)

# Stop an index
scene_index.stop()

# Restart an index
scene_index.start()
```

---

## Events

Events are reusable detection rules. Create them once, attach to any index via alerts.

### Connection Event Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `conn.create_event(event_prompt, label)` | `str` (event_id) | Create detection event |
| `conn.list_events()` | `list` | List all events |

### Creating an Event

```python
event_id = conn.create_event(
    event_prompt="User opened Slack application",
    label="slack_opened",
)
```

### Listing Events

```python
events = conn.list_events()
for event in events:
    print(f"{event['event_id']}: {event['label']}")
```

---

## Alerts

Alerts wire events to indexes for real-time notifications. When the AI detects content matching the event description, an alert is sent.

### Creating an Alert

```python
# Get the RTStreamSceneIndex from index_visuals
scene_index = rtstream.index_visuals(
    prompt="Describe what application is open on screen",
    ws_connection_id=ws_id,
)

# Create an alert on the index
alert_id = scene_index.create_alert(
    event_id=event_id,
    callback_url="https://your-backend.com/alerts",  # for webhook delivery
    ws_connection_id=ws_id,  # for WebSocket delivery (optional)
)
```

**Note:** `callback_url` is required. Pass an empty string `""` if only using WebSocket delivery.

### Managing Alerts

```python
# List all alerts on an index
alerts = scene_index.list_alerts()

# Enable/disable alerts
scene_index.disable_alert(alert_id)
scene_index.enable_alert(alert_id)
```

### Alert Delivery

| Method | Latency | Use Case |
|--------|---------|----------|
| WebSocket | Real-time | Dashboards, live UI |
| Webhook | < 1 second | Server-to-server, automation |

### WebSocket Alert Event

```json
{
  "channel": "alert",
  "rtstream_id": "rts-xxx",
  "data": {
    "event_label": "slack_opened",
    "timestamp": 1710000012340,
    "text": "User opened Slack application"
  }
}
```

### Webhook Payload

```json
{
  "event_id": "event-xxx",
  "label": "slack_opened",
  "confidence": 0.95,
  "explanation": "User opened the Slack application",
  "timestamp": "2024-01-15T10:30:45Z",
  "start_time": 1234.5,
  "end_time": 1238.0,
  "stream_url": "https://stream.videodb.io/v3/...",
  "player_url": "https://console.videodb.io/player?url=..."
}
```

---

## WebSocket Integration

All real-time AI results are delivered via WebSocket. Pass `ws_connection_id` to:
- `rtstream.start_transcript()`
- `rtstream.index_audio()`
- `rtstream.index_visuals()`
- `scene_index.create_alert()`

### WebSocket Channels

| Channel | Source | Content |
|---------|--------|---------|
| `transcript` | `start_transcript()` | Real-time speech-to-text |
| `scene_index` | `index_visuals()` | Visual analysis results |
| `audio_index` | `index_audio()` | Audio analysis results |
| `alert` | `create_alert()` | Alert notifications |

For WebSocket event structures and ws_listener usage, see [capture-reference.md](capture-reference.md).

---

## Complete Workflow

```python
import time
import videodb
from videodb.exceptions import InvalidRequestError

conn = videodb.connect()
coll = conn.get_collection()

# 1. Connect and start recording
rtstream = coll.connect_rtstream(
    url="rtmp://your-stream-server/live/stream-key",
    name="Weekly Standup",
    store=True,
)
rtstream.start()

# 2. Record for the duration of the meeting
start_ts = time.time()
time.sleep(1800)  # 30 minutes
end_ts = time.time()
rtstream.stop()

# Generate an immediate playback URL for the captured window
stream_url = rtstream.generate_stream(start=start_ts, end=end_ts)
print(f"Recorded stream: {stream_url}")

# 3. Export to a permanent video
export_result = rtstream.export(name="Weekly Standup Recording")
print(f"Exported video: {export_result.video_id}")

# 4. Index the exported video for search
video = coll.get_video(export_result.video_id)
video.index_spoken_words(force=True)

# 5. Search for action items
try:
    results = video.search("action items and next steps")
    stream_url = results.compile()
    print(f"Action items clip: {stream_url}")
except InvalidRequestError as exc:
    if "No results found" in str(exc):
        print("No action items were detected in the recording.")
    else:
        raise
```

<!-- ===== /file: videodb/reference/rtstream-reference.md ===== -->

<!-- ===== file: videodb/reference/rtstream.md ===== -->

# RTStream Guide

## Overview

RTStream enables real-time ingestion of live video streams (RTSP/RTMP) and desktop capture sessions. Once connected, you can record, index, search, and export content from live sources.

For code-level details (SDK methods, parameters, examples), see [rtstream-reference.md](rtstream-reference.md).

## Use Cases

- **Security & Monitoring**: Connect RTSP cameras, detect events, trigger alerts
- **Live Broadcasts**: Ingest RTMP streams, index in real-time, enable instant search
- **Meeting Recording**: Capture desktop screen and audio, transcribe live, export recordings
- **Event Processing**: Monitor live feeds, run AI analysis, respond to detected content

## Quick Start

1. **Connect to a live stream** (RTSP/RTMP URL) or get RTStream from a capture session

2. **Start ingestion** to begin recording the live content

3. **Start AI pipelines** for real-time indexing (audio, visual, transcription)

4. **Monitor events** via WebSocket for live AI results and alerts

5. **Stop ingestion** when done

6. **Export to video** for permanent storage and further processing

7. **Search the recording** to find specific moments

## RTStream Sources

### From RTSP/RTMP Streams

Connect directly to a live video source:

```python
rtstream = coll.connect_rtstream(
    url="rtmp://your-stream-server/live/stream-key",
    name="My Live Stream",
)
```

### From Capture Sessions

Get RTStreams from desktop capture (mic, screen, system audio):

```python
session = conn.get_capture_session(session_id)

mics = session.get_rtstream("mic")
displays = session.get_rtstream("screen")
system_audios = session.get_rtstream("system_audio")
```

For capture session workflow, see [capture.md](capture.md).

---

## Scripts

| Script | Description |
|--------|-------------|
| `scripts/ws_listener.py` | WebSocket event listener for real-time AI results |

<!-- ===== /file: videodb/reference/rtstream.md ===== -->

<!-- ===== file: videodb/reference/search.md ===== -->

# Search & Indexing Guide

Search allows you to find specific moments inside videos using natural language queries, exact keywords, or visual scene descriptions.

## Prerequisites

Videos **must be indexed** before they can be searched. Indexing is a one-time operation per video per index type.

## Indexing

### Spoken Word Index

Index the transcribed speech content of a video for semantic and keyword search:

```python
video = coll.get_video(video_id)

# force=True makes indexing idempotent — skips if already indexed
video.index_spoken_words(force=True)
```

This transcribes the audio track and builds a searchable index over the spoken content. Required for semantic search and keyword search.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `language_code` | `str\|None` | `None` | Language code of the video |
| `segmentation_type` | `SegmentationType` | `SegmentationType.sentence` | Segmentation type (`sentence` or `llm`) |
| `force` | `bool` | `False` | Set to `True` to skip if already indexed (avoids "already exists" error) |
| `callback_url` | `str\|None` | `None` | Webhook URL for async notification |

### Scene Index

Index visual content by generating AI descriptions of scenes. Like spoken word indexing, this raises an error if a scene index already exists. Extract the existing `scene_index_id` from the error message.

```python
import re
from videodb import SceneExtractionType

try:
    scene_index_id = video.index_scenes(
        extraction_type=SceneExtractionType.shot_based,
        prompt="Describe the visual content, objects, actions, and setting in this scene.",
    )
except Exception as e:
    match = re.search(r"id\s+([a-f0-9]+)", str(e))
    if match:
        scene_index_id = match.group(1)
    else:
        raise
```

**Extraction types:**

| Type | Description | Best For |
|------|-------------|----------|
| `SceneExtractionType.shot_based` | Splits on visual shot boundaries | General purpose, action content |
| `SceneExtractionType.time_based` | Splits at fixed intervals | Uniform sampling, long static content |
| `SceneExtractionType.transcript` | Splits based on transcript segments | Speech-driven scene boundaries |

**Parameters for `time_based`:**

```python
video.index_scenes(
    extraction_type=SceneExtractionType.time_based,
    extraction_config={"time": 5, "select_frames": ["first", "last"]},
    prompt="Describe what is happening in this scene.",
)
```

## Search Types

### Semantic Search

Natural language queries matched against spoken content:

```python
from videodb import SearchType

results = video.search(
    query="explaining the benefits of machine learning",
    search_type=SearchType.semantic,
)
```

Returns ranked segments where the spoken content semantically matches the query.

### Keyword Search

Exact term matching in transcribed speech:

```python
results = video.search(
    query="artificial intelligence",
    search_type=SearchType.keyword,
)
```

Returns segments containing the exact keyword or phrase.

### Scene Search

Visual content queries matched against indexed scene descriptions. Requires a prior `index_scenes()` call.

`index_scenes()` returns a `scene_index_id`. Pass it to `video.search()` to target a specific scene index (especially important when a video has multiple scene indexes):

```python
from videodb import SearchType, IndexType
from videodb.exceptions import InvalidRequestError

# Search using semantic search against the scene index.
# Use score_threshold to filter low-relevance noise (recommended: 0.3+).
try:
    results = video.search(
        query="person writing on a whiteboard",
        search_type=SearchType.semantic,
        index_type=IndexType.scene,
        scene_index_id=scene_index_id,
        score_threshold=0.3,
    )
    shots = results.get_shots()
except InvalidRequestError as e:
    if "No results found" in str(e):
        shots = []
    else:
        raise
```

**Important notes:**

- Use `SearchType.semantic` with `index_type=IndexType.scene` — this is the most reliable combination and works on all plans.
- `SearchType.scene` exists but may not be available on all plans (e.g. Free tier). Prefer `SearchType.semantic` with `IndexType.scene`.
- The `scene_index_id` parameter is optional. If omitted, the search runs against all scene indexes on the video. Pass it to target a specific index.
- You can create multiple scene indexes per video (with different prompts or extraction types) and search them independently using `scene_index_id`.

### Scene Search with Metadata Filtering

When indexing scenes with custom metadata, you can combine semantic search with metadata filters:

```python
from videodb import SearchType, IndexType

results = video.search(
    query="a skillful chasing scene",
    search_type=SearchType.semantic,
    index_type=IndexType.scene,
    scene_index_id=scene_index_id,
    filter=[{"camera_view": "road_ahead"}, {"action_type": "chasing"}],
)
```

See the [scene_level_metadata_indexing cookbook](https://github.com/video-db/videodb-cookbook/blob/main/quickstart/scene_level_metadata_indexing.ipynb) for a full example of custom metadata indexing and filtered search.

## Working with Results

### Get Shots

Access individual result segments:

```python
results = video.search("your query")

for shot in results.get_shots():
    print(f"Video: {shot.video_id}")
    print(f"Start: {shot.start:.2f}s")
    print(f"End: {shot.end:.2f}s")
    print(f"Text: {shot.text}")
    print("---")
```

### Play Compiled Results

Stream all matching segments as a single compiled video:

```python
results = video.search("your query")
stream_url = results.compile()
results.play()  # opens compiled stream in browser
```

### Extract Clips

Download or stream specific result segments:

```python
for shot in results.get_shots():
    stream_url = shot.generate_stream()
    print(f"Clip: {stream_url}")
```

## Cross-Collection Search

Search across all videos in a collection:

```python
coll = conn.get_collection()

# Search across all videos in the collection
results = coll.search(
    query="product demo",
    search_type=SearchType.semantic,
)

for shot in results.get_shots():
    print(f"Video: {shot.video_id} [{shot.start:.1f}s - {shot.end:.1f}s]")
```

> **Note:** Collection-level search only supports `SearchType.semantic`. Using `SearchType.keyword` or `SearchType.scene` with `coll.search()` will raise `NotImplementedError`. For keyword or scene search, use `video.search()` on individual videos instead.

## Search + Compile

Index, search, and compile matching segments into a single playable stream:

```python
video.index_spoken_words(force=True)
results = video.search(query="your query", search_type=SearchType.semantic)
stream_url = results.compile()
print(stream_url)
```

## Tips

- **Index once, search many times**: Indexing is the expensive operation. Once indexed, searches are fast.
- **Combine index types**: Index both spoken words and scenes to enable all search types on the same video.
- **Refine queries**: Semantic search works best with descriptive, natural language phrases rather than single keywords.
- **Use keyword search for precision**: When you need exact term matches, keyword search avoids semantic drift.
- **Handle "No results found"**: `video.search()` raises `InvalidRequestError` when no results match. Always wrap search calls in try/except and treat `"No results found"` as an empty result set.
- **Filter scene search noise**: Semantic scene search can return low-relevance results for vague queries. Use `score_threshold=0.3` (or higher) to filter noise.
- **Idempotent indexing**: Use `index_spoken_words(force=True)` to safely re-index. `index_scenes()` has no `force` parameter — wrap it in try/except and extract the existing `scene_index_id` from the error message with `re.search(r"id\s+([a-f0-9]+)", str(e))`.

<!-- ===== /file: videodb/reference/search.md ===== -->

<!-- ===== file: videodb/reference/streaming.md ===== -->

# Streaming & Playback

VideoDB generates streams on-demand, returning HLS-compatible URLs that play instantly in any standard video player. No render times or export waits - edits, searches, and compositions stream immediately.

## Prerequisites

Videos **must be uploaded** to a collection before streams can be generated. For search-based streams, the video must also be **indexed** (spoken words and/or scenes). See [search.md](search.md) for indexing details.

## Core Concepts

### Stream Generation

Every video, search result, and timeline in VideoDB can produce a **stream URL**. This URL points to an HLS (HTTP Live Streaming) manifest that is compiled on demand.

```python
# From a video
stream_url = video.generate_stream()

# From a timeline
stream_url = timeline.generate_stream()

# From search results
stream_url = results.compile()
```

## Streaming a Single Video

### Basic Playback

```python
import videodb

conn = videodb.connect()
coll = conn.get_collection()
video = coll.get_video("your-video-id")

# Generate stream URL
stream_url = video.generate_stream()
print(f"Stream: {stream_url}")

# Open in default browser
video.play()
```

### With Subtitles

```python
# Index and add subtitles first
video.index_spoken_words(force=True)
stream_url = video.add_subtitle()

# Returned URL already includes subtitles
print(f"Subtitled stream: {stream_url}")
```

### Specific Segments

Stream only a portion of a video by passing a timeline of timestamp ranges:

```python
# Stream seconds 10-30 and 60-90
stream_url = video.generate_stream(timeline=[(10, 30), (60, 90)])
print(f"Segment stream: {stream_url}")
```

## Streaming Timeline Compositions

Build a multi-asset composition and stream it in real time:

```python
import videodb
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, AudioAsset, ImageAsset, TextAsset, TextStyle

conn = videodb.connect()
coll = conn.get_collection()

video = coll.get_video(video_id)
music = coll.get_audio(music_id)

timeline = Timeline(conn)

# Main video content
timeline.add_inline(VideoAsset(asset_id=video.id))

# Background music overlay (starts at second 0)
timeline.add_overlay(0, AudioAsset(asset_id=music.id))

# Text overlay at the beginning
timeline.add_overlay(0, TextAsset(
    text="Live Demo",
    duration=3,
    style=TextStyle(fontsize=48, fontcolor="white", boxcolor="#000000"),
))

# Generate the composed stream
stream_url = timeline.generate_stream()
print(f"Composed stream: {stream_url}")
```

**Important:** `add_inline()` only accepts `VideoAsset`. Use `add_overlay()` for `AudioAsset`, `ImageAsset`, and `TextAsset`.

For detailed timeline editing, see [editor.md](editor.md).

## Streaming Search Results

Compile search results into a single stream of all matching segments:

```python
from videodb import SearchType
from videodb.exceptions import InvalidRequestError

video.index_spoken_words(force=True)
try:
    results = video.search("key announcement", search_type=SearchType.semantic)

    # Compile all matching shots into one stream
    stream_url = results.compile()
    print(f"Search results stream: {stream_url}")

    # Or play directly
    results.play()
except InvalidRequestError as exc:
    if "No results found" in str(exc):
        print("No matching announcement segments were found.")
    else:
        raise
```

### Stream Individual Search Hits

```python
from videodb.exceptions import InvalidRequestError

try:
    results = video.search("product demo", search_type=SearchType.semantic)
    for i, shot in enumerate(results.get_shots()):
        stream_url = shot.generate_stream()
        print(f"Hit {i+1} [{shot.start:.1f}s-{shot.end:.1f}s]: {stream_url}")
except InvalidRequestError as exc:
    if "No results found" in str(exc):
        print("No product demo segments matched the query.")
    else:
        raise
```

## Audio Playback

Get a signed playback URL for audio content:

```python
audio = coll.get_audio(audio_id)
playback_url = audio.generate_url()
print(f"Audio URL: {playback_url}")
```

## Complete Workflow Examples

### Search-to-Stream Pipeline

Combine search, timeline composition, and streaming in one workflow:

```python
import videodb
from videodb import SearchType
from videodb.exceptions import InvalidRequestError
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, TextAsset, TextStyle

conn = videodb.connect()
coll = conn.get_collection()
video = coll.get_video("your-video-id")

video.index_spoken_words(force=True)

# Search for key moments
queries = ["introduction", "main demo", "Q&A"]
timeline = Timeline(conn)
timeline_offset = 0.0

for query in queries:
    try:
        results = video.search(query, search_type=SearchType.semantic)
        shots = results.get_shots()
    except InvalidRequestError as exc:
        if "No results found" in str(exc):
            shots = []
        else:
            raise

    if not shots:
        continue

    # Add the section label where this batch starts in the compiled timeline
    timeline.add_overlay(timeline_offset, TextAsset(
        text=query.title(),
        duration=2,
        style=TextStyle(fontsize=36, fontcolor="white", boxcolor="#222222"),
    ))

    for shot in shots:
        timeline.add_inline(
            VideoAsset(asset_id=shot.video_id, start=shot.start, end=shot.end)
        )
        timeline_offset += shot.end - shot.start

stream_url = timeline.generate_stream()
print(f"Dynamic compilation: {stream_url}")
```

### Multi-Video Stream

Combine clips from different videos into a single stream:

```python
import videodb
from videodb.timeline import Timeline
from videodb.asset import VideoAsset

conn = videodb.connect()
coll = conn.get_collection()

video_clips = [
    {"id": "vid_001", "start": 0, "end": 15},
    {"id": "vid_002", "start": 10, "end": 30},
    {"id": "vid_003", "start": 5, "end": 25},
]

timeline = Timeline(conn)
for clip in video_clips:
    timeline.add_inline(
        VideoAsset(asset_id=clip["id"], start=clip["start"], end=clip["end"])
    )

stream_url = timeline.generate_stream()
print(f"Multi-video stream: {stream_url}")
```

### Conditional Stream Assembly

Build a stream dynamically based on search availability:

```python
import videodb
from videodb import SearchType
from videodb.exceptions import InvalidRequestError
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, TextAsset, TextStyle

conn = videodb.connect()
coll = conn.get_collection()
video = coll.get_video("your-video-id")

video.index_spoken_words(force=True)

timeline = Timeline(conn)

# Try to find specific content; fall back to full video
topics = ["opening remarks", "technical deep dive", "closing"]

found_any = False
timeline_offset = 0.0
for topic in topics:
    try:
        results = video.search(topic, search_type=SearchType.semantic)
        shots = results.get_shots()
    except InvalidRequestError as exc:
        if "No results found" in str(exc):
            shots = []
        else:
            raise

    if shots:
        found_any = True
        timeline.add_overlay(timeline_offset, TextAsset(
            text=topic.title(),
            duration=2,
            style=TextStyle(fontsize=32, fontcolor="white", boxcolor="#1a1a2e"),
        ))
        for shot in shots:
            timeline.add_inline(
                VideoAsset(asset_id=shot.video_id, start=shot.start, end=shot.end)
            )
            timeline_offset += shot.end - shot.start

if found_any:
    stream_url = timeline.generate_stream()
    print(f"Curated stream: {stream_url}")
else:
    # Fall back to full video stream
    stream_url = video.generate_stream()
    print(f"Full video stream: {stream_url}")
```

### Live Event Recap

Process an event recording into a streamable recap with multiple sections:

```python
import videodb
from videodb import SearchType
from videodb.exceptions import InvalidRequestError
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, AudioAsset, ImageAsset, TextAsset, TextStyle

conn = videodb.connect()
coll = conn.get_collection()

# Upload event recording
event = coll.upload(url="https://example.com/event-recording.mp4")
event.index_spoken_words(force=True)

# Generate background music
music = coll.generate_music(
    prompt="upbeat corporate background music",
    duration=120,
)

# Generate title image
title_img = coll.generate_image(
    prompt="modern event recap title card, dark background, professional",
    aspect_ratio="16:9",
)

# Build the recap timeline
timeline = Timeline(conn)
timeline_offset = 0.0

# Main video segments from search
try:
    keynote = event.search("keynote announcement", search_type=SearchType.semantic)
    keynote_shots = keynote.get_shots()[:5]
except InvalidRequestError as exc:
    if "No results found" in str(exc):
        keynote_shots = []
    else:
        raise
if keynote_shots:
    keynote_start = timeline_offset
    for shot in keynote_shots:
        timeline.add_inline(
            VideoAsset(asset_id=shot.video_id, start=shot.start, end=shot.end)
        )
        timeline_offset += shot.end - shot.start
else:
    keynote_start = None

try:
    demo = event.search("product demo", search_type=SearchType.semantic)
    demo_shots = demo.get_shots()[:5]
except InvalidRequestError as exc:
    if "No results found" in str(exc):
        demo_shots = []
    else:
        raise
if demo_shots:
    demo_start = timeline_offset
    for shot in demo_shots:
        timeline.add_inline(
            VideoAsset(asset_id=shot.video_id, start=shot.start, end=shot.end)
        )
        timeline_offset += shot.end - shot.start
else:
    demo_start = None

# Overlay title card image
timeline.add_overlay(0, ImageAsset(
    asset_id=title_img.id, width=100, height=100, x=80, y=20, duration=5
))

# Overlay section labels at the correct timeline offsets
if keynote_start is not None:
    timeline.add_overlay(max(5, keynote_start), TextAsset(
        text="Keynote Highlights",
        duration=3,
        style=TextStyle(fontsize=40, fontcolor="white", boxcolor="#0d1117"),
    ))
if demo_start is not None:
    timeline.add_overlay(max(5, demo_start), TextAsset(
        text="Demo Highlights",
        duration=3,
        style=TextStyle(fontsize=36, fontcolor="white", boxcolor="#0d1117"),
    ))

# Overlay background music
timeline.add_overlay(0, AudioAsset(
    asset_id=music.id, fade_in_duration=3
))

# Stream the final recap
stream_url = timeline.generate_stream()
print(f"Event recap: {stream_url}")
```

---

## Tips

- **HLS compatibility**: Stream URLs return HLS manifests (`.m3u8`). They work in Safari natively, and in other browsers via hls.js or similar libraries.
- **On-demand compilation**: Streams are compiled server-side when requested. The first play may have a brief compilation delay; subsequent plays of the same composition are cached.
- **Caching**: Calling `video.generate_stream()` a second time without arguments returns the cached stream URL rather than recompiling.
- **Segment streams**: `video.generate_stream(timeline=[(start, end)])` is the fastest way to stream a specific clip without building a full `Timeline` object.
- **Inline vs overlay**: `add_inline()` only accepts `VideoAsset` and places assets sequentially on the main track. `add_overlay()` accepts `AudioAsset`, `ImageAsset`, and `TextAsset` and layers them on top at a given start time.
- **TextStyle defaults**: `TextStyle` defaults to `font='Sans'`, `fontcolor='black'`. Use `boxcolor` (not `bgcolor`) for background color on text.
- **Combine with generation**: Use `coll.generate_music(prompt, duration)` and `coll.generate_image(prompt, aspect_ratio)` to create assets for timeline compositions.
- **Playback**: `.play()` opens the stream URL in the default system browser. For programmatic use, work with the URL string directly.

<!-- ===== /file: videodb/reference/streaming.md ===== -->

<!-- ===== file: videodb/reference/use-cases.md ===== -->

# Use Cases

Common workflows and what VideoDB enables. For code details, see [api-reference.md](api-reference.md), [capture.md](capture.md), [editor.md](editor.md), and [search.md](search.md).

---

## Video Search & Highlights

### Create Highlight Reels
Upload a long video (conference talk, lecture, meeting recording), search for key moments by topic ("product announcement", "Q&A session", "demo"), and automatically compile matching segments into a shareable highlight reel.

### Build Searchable Video Libraries
Batch upload videos to a collection, index them for spoken word search, then query across the entire library. Find specific topics across hundreds of hours of content instantly.

### Extract Specific Clips
Search for moments matching a query ("budget discussion", "action items") and extract each matching segment as an individual clip with its own stream URL.

---

## Video Enhancement

### Add Professional Polish
Take raw footage and enhance it with:
- Auto-generated subtitles from speech
- Custom thumbnails at specific timestamps
- Background music overlays
- Intro/outro sequences with generated images

### AI-Enhanced Content
Combine existing video with generative AI:
- Generate text summaries from transcript
- Create background music matching video duration
- Generate title cards and overlay images
- Mix all elements into a polished final output

---

## Real-Time Capture (Desktop/Meeting)

### Screen + Audio Recording with AI
Capture screen, microphone, and system audio simultaneously. Get real-time:
- **Live transcription** - Speech to text as it happens
- **Audio summaries** - Periodic AI-generated summaries of discussions
- **Visual indexing** - AI descriptions of screen activity

### Meeting Capture with Summarization
Record meetings with live transcription of all participants. Get periodic summaries with key discussion points, decisions, and action items delivered in real-time.

### Screen Activity Tracking
Track what's happening on screen with AI-generated descriptions:
- "User is browsing a spreadsheet in Google Sheets"
- "User switched to a code editor with a Python file"
- "Video call with screen sharing enabled"

### Post-Session Processing
After capture ends, the recording is exported as a permanent video. Then:
- Generate searchable transcript
- Search for specific topics within the recording
- Extract clips of important moments
- Share via stream URL or player link

---

## Live Stream Intelligence (RTSP/RTMP)

### Connect External Streams
Ingest live video from RTSP/RTMP sources (security cameras, encoders, broadcasts). Process and index content in real-time.

### Real-Time Event Detection
Define events to detect in live streams:
- "Person entering restricted area"
- "Traffic violation at intersection"
- "Product visible on shelf"

Get alerts via WebSocket or webhook when events occur.

### Live Stream Search
Search across recorded live stream content. Find specific moments and generate clips from hours of continuous footage.

---

## Content Moderation & Safety

### Automated Content Review
Index video scenes with AI and search for problematic content. Flag videos containing violence, inappropriate content, or policy violations.

### Profanity Detection
Detect and locate profanity in audio. Optionally overlay beep sounds at detected timestamps.

---

## Platform Integration

### Social Media Formatting
Reframe videos for different platforms:
- Vertical (9:16) for TikTok, Reels, Shorts
- Square (1:1) for Instagram feed
- Landscape (16:9) for YouTube

### Transcode for Delivery
Change resolution, bitrate, or quality for different delivery targets. Output optimized streams for web, mobile, or broadcast.

### Generate Shareable Links
Every operation produces playable stream URLs. Embed in web players, share directly, or integrate with existing platforms.

---

## Workflow Summary

| Goal | VideoDB Approach |
|------|------------------|
| Find moments in video | Index spoken words/scenes → Search → Compile clips |
| Create highlights | Search multiple topics → Build timeline → Generate stream |
| Add subtitles | Index spoken words → Add subtitle overlay |
| Record screen + AI | Start capture → Run AI pipelines → Export video |
| Monitor live streams | Connect RTSP → Index scenes → Create alerts |
| Reformat for social | Reframe to target aspect ratio |
| Combine clips | Build timeline with multiple assets → Generate stream |

<!-- ===== /file: videodb/reference/use-cases.md ===== -->
