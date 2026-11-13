# kb-video-download — toàn văn tài liệu của nguồn `video-download`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/video-download/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: video-download/MODULE.md ===== -->

<!-- master-video-edit: mô-đun nhập 2026-10-29 -->
> **Mô-đun `video-download`** của `master-video-edit` — chạy được trên máy này (đã sửa theo ghi chú).
> Thêm gì: yt-dlp recipes: resolution pick, audio-only, subtitles, metadata, playlists
> Nguồn (USB): `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Remotion/research/vendors/OpenMontage/.agents/skills/video-download`
> **Khi dùng trên máy Linux này:**
> - call `uvx --from yt-dlp --with curl_cffi yt-dlp` (system /usr/bin/yt-dlp may be stale)
> - drop brew/pip install lines
> - optional: add tai-video's --cookies-from-browser tip
> Công cụ OpenChatCut nhắc trong file (nếu có) chỉ dùng được khi app OpenChatCut mở, qua MCP `openchatcut`; không có thì làm bằng ffmpeg / faster-whisper / FilmCraft.

---
name: video-download
description: |
  Download video and audio from YouTube and 1000+ sites using yt-dlp. No API keys needed.
  Use when: (1) Downloading a video from YouTube or other sites, (2) Extracting audio from a video URL,
  (3) Downloading subtitles/captions from a video, (4) Getting video metadata without downloading.
---

# video-download

Download video and audio from URLs using yt-dlp directly. No wrapper scripts needed.

## Prerequisites

- **yt-dlp**: `brew install yt-dlp` or `pip install yt-dlp`
- **ffmpeg**: `brew install ffmpeg` or `apt install ffmpeg` (required for merging video+audio streams)

Update yt-dlp periodically to keep up with site changes: `yt-dlp -U` or `pip install -U yt-dlp`.

## Commands

### Download best quality

```bash
yt-dlp "URL" -o "%(title)s.%(ext)s" --merge-output-format mp4
```

### Download specific resolution

```bash
# 720p
yt-dlp "URL" -f "bestvideo[height<=720]+bestaudio/best[height<=720]" --merge-output-format mp4

# 1080p
yt-dlp "URL" -f "bestvideo[height<=1080]+bestaudio/best[height<=1080]" --merge-output-format mp4
```

### Audio only

```bash
yt-dlp "URL" -x --audio-format mp3 --audio-quality 0
```

### Download subtitles

```bash
# Download video with English subtitles
yt-dlp "URL" --write-subs --sub-langs en --merge-output-format mp4

# Download video with multiple subtitle languages
yt-dlp "URL" --write-subs --sub-langs "en,es,fr" --merge-output-format mp4

# Download only subtitles (no video)
yt-dlp "URL" --write-subs --sub-langs en --skip-download
```

### Get metadata (no download)

```bash
yt-dlp "URL" --dump-json --no-download
```

### List available formats

```bash
yt-dlp "URL" -F
```

### Specify output directory

```bash
yt-dlp "URL" -o "./downloads/%(title)s.%(ext)s" --merge-output-format mp4
```

## Quality Presets

| Quality | Format flag |
|---------|-------------|
| Best | `-f "bestvideo+bestaudio/best"` (default) |
| 1080p | `-f "bestvideo[height<=1080]+bestaudio/best[height<=1080]"` |
| 720p | `-f "bestvideo[height<=720]+bestaudio/best[height<=720]"` |
| 480p | `-f "bestvideo[height<=480]+bestaudio/best[height<=480]"` |
| Worst | `-f "worstvideo+worstaudio/worst"` |

## Output Template Variables

Common variables for `-o` templates:

| Variable | Description |
|----------|-------------|
| `%(title)s` | Video title |
| `%(ext)s` | File extension |
| `%(id)s` | Video ID |
| `%(uploader)s` | Channel/uploader name |
| `%(upload_date)s` | Upload date (YYYYMMDD) |
| `%(duration)s` | Duration in seconds |
| `%(resolution)s` | Video resolution |

## Tips

- Always use `--merge-output-format mp4` to avoid ending up with `.webm` or `.mkv` files.
- Use `--no-download` with `--dump-json` for metadata-only queries -- no files written to disk.
- If a download fails with HTTP errors, update yt-dlp first (`yt-dlp -U`).
- Use `-f "bestvideo[height<=720]+bestaudio"` to save bandwidth when full resolution is not needed.
- yt-dlp automatically handles rate limiting and retries.
- The `--dump-json` output includes `title`, `duration`, `uploader`, `view_count`, `description`, `formats`, `subtitles`, and much more.

## Troubleshooting

- **"yt-dlp: command not found"**: Install it (`pip install yt-dlp`) and ensure your PATH includes pip's bin directory.
- **"ffmpeg: command not found"**: Install ffmpeg. Without it, downloads fail when video and audio are separate streams (common on YouTube for HD).
- **Downloads fail or return errors**: Run `yt-dlp -U` to update. Sites change frequently and yt-dlp ships fixes regularly.

<!-- ===== /file: video-download/MODULE.md ===== -->
