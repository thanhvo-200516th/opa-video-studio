# kb-lemo-opuscar — toàn văn tài liệu của nguồn `lemo-opuscar`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/lemo-opuscar/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: lemo-opuscar/SKILL.md ===== -->

---
name: lemo-opuscar
description: Direct and produce a short film made entirely in code, in one of the styles of the Lemo-Opuscar library (e.g. Impasto Oil Painting 油画厚涂, Watercolor Brush 水彩笔刷, Chinese Ink Wash 中国水墨, Ukiyo-e 浮世绘, Whiteboard Explainer 白板讲解). Use when the user asks for a video, film, short, promo, explainer or animation (视频、短片、动画、宣传片) in a named style; when they want a film made about their own topic and haven't chosen a style (help them choose); or when they ask which film styles there are. Not for editing or converting existing video files.
---

# Lemo-Opuscar

The styles, guides and tools live in the Lemo-Opuscar library (github.com/lemomo-ai/lemo-opuscar). This skill fetches it and hands you over to it.

## On this Windows machine: the library runs inside WSL

This copy is adapted for Windows (native Windows is unsupported by the library). The library is installed in WSL at `/root/lemo-opuscar` (distro `Ubuntu-24.04`, user root) with the core, voice and music tiers and the HDRI pack; instrument packs are fetched only when `sampler.py` asks. You still write the film's files from Windows. Everything below and in the library's guides applies, with these substitutions:

| Guides say | Do this instead |
|---|---|
| `sh "<skill base directory>/scripts/setup.sh" …` | `bash "<skill base directory>/scripts/wsl.sh" setup …` (same arguments) |
| read `$LIB/<file>` | Read tool at `\wsl.localhost\Ubuntu-24.04\root\lemo-opuscar\<file>` |
| `cd "$LIB" && <command>` | `bash "<skill base directory>/scripts/wsl.sh" run '<command>'` (starts in `$LIB`) |
| the project's absolute path in a command | its WSL form, from `bash "<skill base directory>/scripts/wsl.sh" path '<Windows path>'` (`D:\Vibe Coding\x` → `/mnt/d/Vibe Coding/x`) |
| `LIB=<path>` at the top of `build.sh` | `LIB=/root/lemo-opuscar`; run it with `wsl.sh run 'bash "<WSL path>/build.sh"'` |

- Create and edit project files at the Windows path with the normal tools; open the stills and videos the tools write there the same way. Paths contain spaces: always quote them.
- Write project files with LF line endings (`build.sh` runs in Linux).
- WebGL runs on software rendering (SwiftShader) in WSL: 3D, shader and CRT styles are slow. Render stills first and tell the user before a long render.
- Narration: Kokoro (offline) has no Vietnamese voice; for Vietnamese narration say so and offer edge-tts (online, `vi-VN` voices) or a voice-free film.

1. **Get the library.** Run `sh "<skill base directory>/scripts/setup.sh"`. It clones or updates the library (default `~/lemo-opuscar`; a clone the user is standing in is used as it is) and prints `LIB=<path>` on its last line.
2. **Install the core tools early.** Start `sh "<skill base directory>/scripts/setup.sh" deps` right away, in the background if you can: it takes a few minutes the first time. Add `deps voice` or `deps music` later, only if the film needs them (`$LIB/TECHNIQUE.md` §1). Report missing system tools in your one round of questions; don't install system software yourself.
3. **Follow the library.** Read `$LIB/AGENTS.md` and do what it says: finding the style, the one round of questions, the treatment, production and delivery.

What changes in skill mode:

| | |
|---|---|
| Project folder | `<name>/` in the folder the user started from (lowercase letters, digits, hyphens; avoid `#` and `?` in the path). Wherever the guides say `films/<name>/`, read this folder |
| Running tools | from `$LIB`, with the project's absolute path: `cd "$LIB" && node core/render/still.mjs "<project>" 1.5 3` |
| Library files in pages | absolute URLs: `/core/lib.js`, `/node_modules/three/…` (the project is served at `/@film/`) |
| Library files in scripts and `build.sh` | `$LIB/…`, with `LIB=<path>` at the top of `build.sh`; never `../..` |
| Demo source | not downloaded. `sh "<skill base directory>/scripts/setup.sh" demo <slug>`, only after your `TREATMENT.md` is written, to read its techniques; it is not meant to be rendered |

Deliver what `$LIB/DIRECTOR.md` §11 lists, in the project folder, and tell the user where it is.

<!-- craft-handoff:start -->
## Mở và sửa tiếp trong FilmCraft / EffectCraft

Khi user muốn sửa tiếp trong FilmCraft hoặc EffectCraft, không giao một MP4 phẳng: viết timeline spec rồi dùng skill `craft-handoff` dựng project gốc (`.fcproj` / `.ecproj`) có đủ track, clip, keyframe, chữ, effect và SFX. Với skill này: mỗi cảnh một clip (nền trong suốt nếu phủ lên nền khác); tiêu đề ít chuyển động → text clip gốc; cần chỉnh chuyển động từng ký tự → EffectCraft qua `ae-script-builder`. Chi tiết: `craft-handoff/references/skills-map.md`.
<!-- craft-handoff:end -->

<!-- ===== /file: lemo-opuscar/SKILL.md ===== -->
