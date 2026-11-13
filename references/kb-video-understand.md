# kb-video-understand — toàn văn tài liệu của nguồn `video-understand`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/video-understand/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: video-understand/MODULE.md ===== -->

<!-- master-video-edit: mô-đun nhập 2026-10-29 -->
> **Mô-đun `video-understand`** của `master-video-edit` — chạy được trên máy này (đã sửa theo ghi chú).
> Thêm gì: Scene/keyframe extraction + transcript JSON so the agent can 'watch' footage
> Nguồn (USB): `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Remotion/research/vendors/OpenMontage/.agents/skills/video-understand`
> **Khi dùng trên máy Linux này:**
> - switch transcription to faster-whisper (~/.venvs/video-skills) or run with --no-transcribe
> - remove the interactive pip-install prompt
> - fix paths skills/video-understand/scripts/ -> module path; brew -> apt
> **Đã sửa (2026-10-29):** `scripts/understand_video.py` dùng faster-whisper trước (GPU, rơi về CPU), bỏ câu hỏi tự cài openai-whisper. Chạy: `PATH=$HOME/.local/bin:$PATH ~/.venvs/video-skills/bin/python scripts/understand_video.py <video>`. Đã thử trên C0022: 20 khung + lời đúng.
> Công cụ OpenChatCut nhắc trong file (nếu có) chỉ dùng được khi app OpenChatCut mở, qua MCP `openchatcut`; không có thì làm bằng ffmpeg / faster-whisper / FilmCraft.

---
name: video-understand
description: |
  Understand video content locally using ffmpeg frame extraction and Whisper transcription. No API keys needed.
  Use when: (1) Understanding what a video contains, (2) Transcribing video audio locally,
  (3) Extracting key frames for visual analysis, (4) Getting video content without API keys.
---

# video-understand

Understand video content locally using ffmpeg for frame extraction and Whisper for transcription. Fully offline, no API keys required.

## Prerequisites

- `ffmpeg` + `ffprobe` (required): `brew install ffmpeg`
- `openai-whisper` (optional, for transcription): `pip install openai-whisper`

## Commands

```bash
# Scene detection + transcribe (default)
python3 skills/video-understand/scripts/understand_video.py video.mp4

# Keyframe extraction
python3 skills/video-understand/scripts/understand_video.py video.mp4 -m keyframe

# Regular interval extraction
python3 skills/video-understand/scripts/understand_video.py video.mp4 -m interval

# Limit frames extracted
python3 skills/video-understand/scripts/understand_video.py video.mp4 --max-frames 10

# Use a larger Whisper model
python3 skills/video-understand/scripts/understand_video.py video.mp4 --whisper-model small

# Frames only, skip transcription
python3 skills/video-understand/scripts/understand_video.py video.mp4 --no-transcribe

# Quiet mode (JSON only, no progress)
python3 skills/video-understand/scripts/understand_video.py video.mp4 -q

# Output to file
python3 skills/video-understand/scripts/understand_video.py video.mp4 -o result.json
```

## CLI Options

| Flag | Description |
|------|-------------|
| `video` | Input video file (positional, required) |
| `-m, --mode` | Extraction mode: `scene` (default), `keyframe`, `interval` |
| `--max-frames` | Maximum frames to keep (default: 20) |
| `--whisper-model` | Whisper model size: tiny, base, small, medium, large (default: base) |
| `--no-transcribe` | Skip audio transcription, extract frames only |
| `-o, --output` | Write result JSON to file instead of stdout |
| `-q, --quiet` | Suppress progress messages, output only JSON |

## Extraction Modes

| Mode | How it works | Best for |
|------|-------------|----------|
| `scene` | Detects scene changes via ffmpeg `select='gt(scene,0.3)'` | Most videos, varied content |
| `keyframe` | Extracts I-frames (codec keyframes) | Encoded video with natural keyframe placement |
| `interval` | Evenly spaced frames based on duration and max-frames | Fixed sampling, predictable output |

If `scene` mode detects no scene changes, it automatically falls back to `interval` mode.

## Output

The script outputs JSON to stdout (or file with `-o`). See `references/output-format.md` for the full schema.

```json
{
  "video": "video.mp4",
  "duration": 18.076,
  "resolution": {"width": 1224, "height": 1080},
  "mode": "scene",
  "frames": [
    {"path": "/abs/path/frame_0001.jpg", "timestamp": 0.0, "timestamp_formatted": "00:00"}
  ],
  "frame_count": 12,
  "transcript": [
    {"start": 0.0, "end": 2.5, "text": "Hello and welcome..."}
  ],
  "text": "Full transcript...",
  "note": "Use the Read tool to view frame images for visual understanding."
}
```

Use the Read tool on frame image paths to visually inspect extracted frames.

## References

- `references/output-format.md` -- Full JSON output schema documentation

<!-- ===== /file: video-understand/MODULE.md ===== -->

<!-- ===== file: video-understand/references/output-format.md ===== -->

# Output Format

## Result JSON

The main script (`understand_video.py`) outputs a JSON object to stdout (or to a file with `-o`) containing video metadata, extracted frame paths, and transcription data.

```json
{
  "video": "video.mp4",
  "duration": 18.076,
  "resolution": {
    "width": 1224,
    "height": 1080
  },
  "mode": "scene",
  "frames": [
    {
      "path": "/absolute/path/to/frames/frame_0001.jpg",
      "timestamp": 0.0,
      "timestamp_formatted": "00:00"
    },
    {
      "path": "/absolute/path/to/frames/frame_0002.jpg",
      "timestamp": 3.2,
      "timestamp_formatted": "00:03"
    }
  ],
  "frame_count": 12,
  "transcript": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "Hello and welcome to this video."
    },
    {
      "start": 2.8,
      "end": 5.1,
      "text": "Today we will discuss..."
    }
  ],
  "text": "Hello and welcome to this video. Today we will discuss...",
  "note": "Use the Read tool to view frame images for visual understanding."
}
```

## Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `video` | string | Original video filename (basename) |
| `duration` | float | Video duration in seconds |
| `resolution` | object | Video resolution with `width` and `height` |
| `mode` | string | Extraction mode used: `scene`, `keyframe`, or `interval` |
| `frames` | array | Array of extracted frame objects |
| `frame_count` | integer | Number of frames extracted |
| `transcript` | array or null | Array of transcript segments, or `null` if transcription was skipped |
| `text` | string or null | Full transcript as a single string, or `null` if skipped |
| `note` | string | Hint for Claude on how to use the frame images |

## Frame Object

| Field | Type | Description |
|-------|------|-------------|
| `path` | string | Absolute path to the extracted JPEG frame |
| `timestamp` | float | Frame timestamp in seconds from the start of the video |
| `timestamp_formatted` | string | Human-readable timestamp in `MM:SS` or `HH:MM:SS` format |

## Transcript Segment

| Field | Type | Description |
|-------|------|-------------|
| `start` | float | Segment start time in seconds |
| `end` | float | Segment end time in seconds |
| `text` | string | Transcribed text for this segment |

## Frame Path Convention

Frames are extracted to a directory next to the video file:

```
video.mp4
video_frames/
  frame_0001.jpg
  frame_0002.jpg
  ...
```

The directory name is `{video_stem}_frames`. All frame paths in the JSON output are absolute paths, suitable for direct use with the Read tool.

## Null Fields

- `transcript` and `text` are `null` when `--no-transcribe` is used or when Whisper is not installed.
- If scene detection finds no scenes, mode automatically falls back to `interval` and the `mode` field reflects the actual mode used.

## Using with Claude

To visually inspect the video content, use the Read tool on the frame paths returned in the `frames` array. Claude can view JPEG images directly and describe their contents. Combined with the transcript, this provides full video understanding without any cloud APIs.

<!-- ===== /file: video-understand/references/output-format.md ===== -->
