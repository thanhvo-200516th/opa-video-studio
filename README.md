# opa-video-studio

Skill DUY NHẤT, tự đủ, cho mọi việc dựng / sửa video của OPA (OverPowers Agency) — bản 3.5.1.

- `SKILL.md` — vai trò, bộ luật tóm tắt, quy trình (19 lệnh dựng FilmCraft, tìm ngoại lệ footage bằng `auto-footage`, tạo B-roll 100% mặc định & 3D assets minh hoạ câu thoại qua Google Flow (MCP hoặc trình duyệt Cindy theo phiên) + prompt 5 tầng Anti-Plastic, huấn luyện style mới qua `video-style-trainer`, việc S: Edit Blueprint cho Premiere / After Effects / CapCut), định dạng bàn giao, ví dụ.
- `rules.json` + `references/rules-full.md` — 88 luật (69 hiện hành, 5 hồ sơ @__dviet tuỳ chọn, 14 đã thay), mỗi luật có nguồn.
- `references/visual-motion-system.md` — 9 thông số thẩm mỹ OPA + quy trình bảng phân cảnh dựng.
- `references/kb-*.md` — toàn văn 81 nguồn kiến thức đã gộp (kể cả `dung-video-talking-head v1.2.3`, `auto-footage`, `hyperframes-*`, `video-style-trainer`); `scripts/` — công cụ (mỗi script một lệnh độc lập, không pipeline); `tests/` — 16 bộ test.

## Cài
```bash
git clone https://github.com/thanhvo-200516th/opa-video-studio.git ~/.claude/skills/opa-video-studio
```
Python: `~/.venvs/video-skills/bin/python` (ffmpeg, faster-whisper, numpy, opencv, Pillow) và `~/.venvs/footage/bin/python` (CLIP cho `auto-footage`). Kiểm: `for t in tests/test_*.py; do python $t; done` → mỗi bộ in "TẤT CẢ ĐẠT".

Không xuất MP4 khi chưa có người duyệt. Gọi skill: "Dùng opa-video-studio …" hoặc nói việc cần làm (dựng video, phụ đề, B-roll, bảng phân cảnh…).

## Changelog
- 3.5.1 — đường thực thi Google Flow theo phiên (MCP khi có tool `flow_*`, không thì trình duyệt Cindy); tham số MCP theo `flow_inspect_account`; tải 1080p; X13; mô tả ≤ 1024.

- **3.6.2** (2026-11-17): `minimal-edu` — chữ chính có chiều sâu: `brooks_text.HeroLooks` (`caption_group(..., looks=HeroLooks(prof), gfx_dir=...)`, `quote_text(hero_index=…, looks=…)`; `text.hero_looks` / `gradients` / `look_shadows`): glow mức thường + bóng mềm, gradient PNG, bóng đổ sâu (không viền), nền sáng không glow; edit_rules chấp nhận gradient PNG (text_img) có glow, không tính font; `tests/test_minimal_looks.py`.

- **3.6.1** (2026-11-17): `minimal-edu` — từ lớn xoay nhiều màu (`brooks_text.HeroColors`, `text.colors.hero_rotation_dark / _light`; chữ màu glow nhẹ, trắng / đen không glow; `edit_rules` kiểm "chữ màu ⇒ glow"), `caption_group(color=, colors=)` + `quote_text(hero_color=)`; tự co khi chật (hero −8 px tới `auto_fit_min_hero` 120, span chữ nhỏ +0,1 tới 800 px) thay vì báo lỗi; `build_kit.retime_cuts` dời điểm cắt cứng về 1 khung trước chữ đầu câu; tốc độ 1.05x cho hồ sơ (`speed_media.py plan --speed 1.0|1.05|1.10 | --profile minimal-edu`, D4 giữ nguyên).

- **3.6.0** (2026-11-17): hồ sơ tuỳ chọn `minimal-edu` (P6–P12, kiểu Joseph / Arthur Brooks — `references/minimal-edu-style.json`, `scripts/style_profile.py`): cụm chữ 1 từ lớn + font Inter / Playfair (`brooks_text.py`, `assets/fonts/`), chữ vào nhanh / mờ ra 2 khung, cắt cứng trong hồ sơ, đồ hoạ 10 nguyên tắc (`draw_path.py` ProRes 4444 alpha, `fx_gfx` giấy / thẻ trích dẫn / polaroid, `MotionFX` box_wipe · polaroid_pop · whip_pan · scene_camera · graph_scene…); tài liệu kế hoạch chọn A/B/C từng nhịp `plan_doc.py` (§3 bước 7b, D16); kiểm C7 điểm cắt đầu câu, C8 chữ quá điểm cắt; SFX `highlighter`; `env_status.py --install-fonts`.
