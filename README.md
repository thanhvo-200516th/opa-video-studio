# opa-video-studio

Skill DUY NHẤT, tự đủ, cho mọi việc dựng / sửa video của OPA (OverPowers Agency) — bản 3.2.0.

- `SKILL.md` — vai trò, bộ luật tóm tắt, quy trình (19 lệnh dựng FilmCraft, tìm B-roll bằng `auto-footage`, tạo B-roll bằng Muse / Google Flow MCP, việc S: Edit Blueprint cho Premiere / After Effects / CapCut), định dạng bàn giao, ví dụ.
- `rules.json` + `references/rules-full.md` — 85 luật (68 hiện hành, 5 hồ sơ @__dviet tuỳ chọn, 12 đã thay), mỗi luật có nguồn.
- `references/visual-motion-system.md` — 9 thông số thẩm mỹ OPA + quy trình bảng phân cảnh dựng.
- `references/kb-*.md` — toàn văn 80 nguồn kiến thức đã gộp; `scripts/` — công cụ (mỗi script một lệnh độc lập, không pipeline); `tests/` — 14 bộ test.

## Cài
```bash
git clone https://github.com/thanhvo-200516th/opa-video-studio.git ~/.claude/skills/opa-video-studio
```
Python: `~/.venvs/video-skills/bin/python` (ffmpeg, faster-whisper, numpy, opencv, Pillow) và `~/.venvs/footage/bin/python` (CLIP cho `auto-footage`). Kiểm: `for t in tests/test_*.py; do python $t; done` → mỗi bộ in "TẤT CẢ ĐẠT".

Không xuất MP4 khi chưa có người duyệt. Gọi skill: "Dùng opa-video-studio …" hoặc nói việc cần làm (dựng video, phụ đề, B-roll, bảng phân cảnh…).
