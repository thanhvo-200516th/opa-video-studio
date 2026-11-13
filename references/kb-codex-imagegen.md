# kb-codex-imagegen — toàn văn tài liệu của nguồn `codex-imagegen`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/codex-imagegen/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: codex-imagegen/SKILL.md ===== -->

---
name: codex-imagegen
description: Use when the user asks to create, draw, generate, or edit a raster image — photo, illustration, banner, thumbnail, poster, product shot, avatar, mockup ("tạo ảnh", "vẽ ảnh", "làm ảnh", "gen ảnh", "sửa ảnh", "ảnh minh hoạ") — or when a deliverable needs a generated picture. Claude has no native image generation; the local Codex CLI does.
---

# Codex Image Generation

## Overview
Delegate the pixels to the local Codex CLI (`codex exec`, built-in `image_generation` tool, ChatGPT login). Claude writes the prompt, Codex renders and saves the PNG, Claude reads the file back to check it.

**Not for:** charts, diagrams, SVG icons, HTML/CSS layouts, OG cards built from text — make those directly.

## Generate
Run via the Bash tool with `timeout: 300000` (one image takes ~50s, can reach 2–3 min). Use forward-slash absolute Windows paths.

```bash
codex exec --skip-git-repo-check -C "D:/proj/assets" -c model_reasoning_effort="low" \
  -o "D:/proj/assets/.codex-last.txt" - <<'EOF'
Use your built-in image generation tool (not code, not SVG, not PIL) to create this image:
<subject, style, composition, lighting, palette, aspect ratio, exact in-image text in quotes>
Then copy the generated PNG to: D:/proj/assets/hero.png
Final reply: only the absolute path of the saved file.
EOF
```

Then **Read the PNG** to verify it matches the request before reporting.

## Edit / use reference images
Add `-i "D:/path/source.png"` (repeatable) before `-`, and write "Edit the attached image: …" in the prompt. To iterate on a result, pass the previous output with `-i` plus the change request.

## Quick reference
| Need | How |
|---|---|
| Output location fallback | Newest PNG in `~/.codex/generated_images/<session id>/` (session id is in the output header) |
| Final message only | `-o <file>` |
| Several images | One `codex exec` per image; run independent ones in parallel |
| Aspect ratio | Codex picks the nearest supported size (16:9 → 1672x941); resize afterwards if exact pixels matter |
| Warning `Exceeded skills context budget` | Harmless, ignore |

## Common mistakes
| Symptom | Fix |
|---|---|
| `model is not supported when using Codex with a ChatGPT account` | `codex` on PATH is outdated: `npm i -g @openai/codex@latest` |
| Hangs on `Reading additional input from stdin` | Pass the prompt through stdin with `-` + heredoc, as above |
| Codex draws with code/SVG instead of a real image | Say "built-in image generation tool" explicitly |
| Very slow / burns quota | Config default effort is `ultra`; keep `-c model_reasoning_effort="low"` |
| Vietnamese text in image is misspelled | Quote exact text, check after Read; for long text, overlay it in HTML/design tool instead |

Each run spends the user's ChatGPT plan quota (~20k tokens + one image). Don't generate speculative variants unless asked.

<!-- ===== /file: codex-imagegen/SKILL.md ===== -->
