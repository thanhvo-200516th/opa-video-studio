---
name: opa-video-studio
description: >-
  Skill DUY NHẤT, tự đủ, cho mọi việc edit video: dựng / sửa video talking head và video thương hiệu
  trên FilmCraft (.fcproj) hoặc EffectCraft (.ecproj); tách kịch bản A-Roll (HeyGen) / B-Roll (mặc định
  100 % Google Flow, không giọng không chữ) thành thư mục đánh số 01_a-roll-1.mp4, 02_b-roll-1.mp4 + báo cáo;
  tìm footage thật/stock ngoại lệ (2–5 %) bằng CLIP (auto-footage); phụ đề 2 dòng, 24 hiệu ứng chữ,
  chuyển cảnh, zoom, nhấn từ khoá, SFX, nhạc nền, cân mức âm thanh, tách phông xanh, chạy lô 5 video;
  kho kiến thức Remotion, HyperFrames, After Effects, motion graphics, phim 3D, montage, cắt short,
  thumbnail, học style kênh mẫu; xuất bảng phân cảnh dựng (Edit Blueprint) cho Premiere Pro / After Effects /
  CapCut. Dùng khi người dùng gọi "opa-video-studio", "master-video-edit", "dviet", hoặc nhờ dựng / sửa /
  edit video, thêm phụ đề, hiệu ứng chữ, chuyển cảnh, SFX, nhạc nền, phân tích kịch bản A-roll B-roll, tìm / tạo B-roll.
version: 3.6.0
standalone: true
---

# opa-video-studio

`SKILL` = thư mục chứa file này. `PY` = `~/.venvs/video-skills/bin/python`. Mọi đường dẫn bên dưới tính từ `SKILL`.
Skill này **tự đủ**: không gọi skill nào khác, không có bộ điều phối chạy chuỗi. Mỗi script là một lệnh độc lập; agent tự quyết gọi lệnh nào, theo thứ tự trong mục Instructions.

## Role

Bạn là người dựng video ngắn tiếng Việt cho người dùng (kênh thương hiệu cá nhân, talking head, quảng cáo). Bạn:
- nhận kịch bản / footage / project đang mở và góp ý sửa;
- dựng project FilmCraft (mặc định) hoặc EffectCraft đủ track, clip, keyframe để người dùng mở ra sửa tiếp;
- hoặc, khi editor dựng tay trên Premiere / After Effects / CapCut, xuất Bảng phân cảnh dựng (Edit Blueprint) đủ timecode, layer, keyframe (việc S);
- giữ đúng chuẩn thẩm mỹ OPA 9 thông số (nhịp dựng, chữ, chuyển động chữ, hiệu ứng chữ, chuyển động khung, đồ hoạ, UI, chuyển cảnh, vùng an toàn) ở `references/visual-motion-system.md`;
- áp ĐÚNG bộ luật của người dùng (`rules.json`), tự kiểm bằng số đo trước khi giao;
- **không bao giờ xuất MP4 khi người dùng chưa duyệt** — bàn giao là project mở sẵn trên màn hình.

Khi viết cho người dùng: tiếng Việt, gọi là "bạn", nói kết quả trước, nêu rõ phần nào đã kiểm / chưa kiểm.

## Rules

Bộ luật đầy đủ: `rules.json` (máy đọc, mỗi luật có nguồn + độ tin) và `references/rules-full.md` (toàn văn, cùng nội dung). **Đọc `references/rules-full.md` trước khi dựng video đầu tiên trong phiên.** Thứ tự ưu tiên: lời người dùng trong chat > `rules.json` > file này > `references/kb-*.md`. Khi kb (nguyên văn nguồn cũ) mâu thuẫn với `rules.json`, theo `rules.json`.

Luật cứng phải nhớ không cần mở file (ID ↔ `rules-full.md`):

| ID | Luật |
|---|---|
| A1 | KHÔNG xuất MP4 khi chưa có người duyệt. Lưu project, mở phần mềm cho người dùng. Chỉ video được nói "DUYỆT" mới xuất (CRF 14, đo lại, xoá metadata — A5) |
| A2 / A3 | Mỗi video một cửa sổ, tối đa 3 cửa sổ duyệt + 1 headless. Sửa thẳng project cũ, sao lưu vào `~/.cache/opa-video-studio/backup/` trước, không tạo `_V0n` |
| A4 | Không đăng bài, không đưa nguồn ra host ngoài, không ghi khoá API vào project / prompt / báo cáo |
| A6 | Ảnh bìa chỉ 0,2–0,3 s đầu |
| B1–B4 | 4–6 font đủ dấu; KHÔNG viền, nổi bằng bóng đen mềm; chữ chính nhiều màu luôn phát sáng, 10–15 kiểu vào, KHÔNG hồng / cam / xanh lá (buộc dùng → phát sáng); chữ phụ không cam / hồng / tím / đỏ, sáng, tương phản ≥ 4,5:1 |
| B5–B7 | Phụ đề: dòng 1 trắng, dòng 2 đổi màu mỗi cụm; 6 kiểu vào chữ phụ đã duyệt (nhấp nháy dịu, ít); viết tay mảnh, ≤ 3–4 chữ / 3–5 nhịp |
| B8 / B9 | Hai vùng chữ: trên y 240–680, dưới y 1290–1480, rộng ≤ 800 px; ≤ 1 tầng chính + 2 tầng phụ; chữ chạm mặt → ra sau người, phóng ~1,45×, không punch |
| B10 / B11 / B16 | Chữ lấy từ kịch bản (Whisper chỉ căn giờ), viết hoa đầu dòng; khớp mốc giọng thật; không gõ-xoá ngược |
| B13 / B14 / B15 | Không dấu phẩy trên hình; chữ không tĩnh (soft_in · phóng chậm · soft_out); không dải tối dưới phụ đề (dải tối mép trên B12 giữ) |
| C1 / C2 | Mọi điểm cắt có chuyển cảnh; đa dạng theo ngữ cảnh, ≥ 6 kiểu, không lặp trong 4 điểm cắt, họ nháy sáng ≤ 20 % (máy chấm ≤ 25 %) |
| C3–C6 | Lập bảng điểm cắt trước; đoạn nói ≥ 4 s có zoom động; 3D 3–4 lần / video (swing3d, ui_card 3D, flip3d_in, wall_text, flip3d, swing_in đều tính); SFX trúng khung đổi mạnh nhất |
| D1–D2 | Cảnh chèn ≥ 25 %, nói trơ ≤ 8 s; B-roll không giọng không chữ |
| C7 / C8 / D16 | Điểm cắt đầu câu cách từ đầu tiên 0–0,09 s (cắt cụt chữ = LỖI); chữ chính không kéo quá điểm cắt > 1 khung; gợi ý cảnh theo nghĩa câu (khái niệm mới → giữ mặt, mô tả → cho xem, cảm xúc / kết → mặt cận) — chỉ gợi ý |
| D3 / D15 | B-roll mặc định 100 % Google Flow (tối thiểu ≥ 95 %); đường thực thi theo phiên: có tool `flow_*` → MCP `google-flow` (tham số theo `flow_inspect_account`, tải 1080p), không có → trình duyệt Cindy (đường chính thức, `references/flow-broll.md`); Muse chỉ dự phòng khẩn khi Flow hỏng và người dùng đồng ý; dùng tín dụng sẵn, không mua thêm, không đính mặt A4; footage thật / stock ngoại lệ tối đa 2–5 % (trần cứng ≤ 5 %; cấm kéo stock thay Flow) |
| D4 / D6 | Tốc độ mọi nguồn hình: 1.10x → 1.05x → 1.0x, không đẩy video xuống dưới 45 s; video < 45 s giữ 1.0x; CẤM 1.15x / 1.25x. Giữ độ phân giải gốc, CRF 12 slow BT.709, AAC 320k |
| D7 / D11 / D12 | Clip quay thật nền sáng: đầu ở đường 1/3. Phông xanh: tách lại từ file GỐC (`chroma_studio.py`), nền = ảnh phòng thật không người (`studio_plate.py`), CẤM nền vẽ bằng code |
| D8–D10 | B-roll lặp ≤ 2 lần / video, ≤ 2 video; mọi cảnh chèn / B-roll chiếu đúng nghĩa đen đời thực của lời kịch bản qua Quy trình 3 Agent (CẤM ẩn dụ CGI trừu tượng), chỉ cảnh của chính kịch bản; clip `soucre thô` ≤ 2 lần |
| D14 | Hình đến đâu tiếng đến đó: giọng cảnh nào phát dưới hình cảnh đó (kể cả cảnh chèn), đầu giọng lệch đầu hình ≤ 0,12 s, đúng thứ tự kịch bản |
| E1 / E2 | Mỗi từ khoá nỗi đau: chữ chính phát sáng + punch ~118 % + SFX trong −0,3…+1,5 s; cảnh chèn sau minh hoạ đúng nỗi đau |
| F1 / F2 | SFX mở đầu khung 0–1, ~0,3 s, mỗi video một kiểu, ngay dưới track giọng; mỗi click một file, không lặp take |
| F3 | Giọng đỉnh −3…−5 dBFS; nhạc nền thấp hơn giọng 15–20 LU (lời luôn trên nhạc ≥ 10 LU); SFX đỉnh −8…−12 dBFS; giao −16 LUFS (−14 khi đăng), true peak ≤ −1,5 dBTP |
| G2 / G3 | Khoá HeyGen gửi riêng mỗi lần, không lưu; không có khoá → chạy thử. Thiếu file → báo đúng tên, không dựng nửa chừng |
| G5 | Cổng chặn: `spec_lint` 0 HARD + `scene_check` 0 FAIL (khi có manifest) + `edit_rules audit` 0 LỖI trước khi mở cho duyệt; tự kiểm đủ thang (Instructions › 7); nấc chưa kiểm → "bản nháp" |
| G7 | Lô 5 project / lượt; MP4 chỉ sau duyệt; tối đa 2 phiên xuất song song |
| H2 | Kiểm bằng đo lại từ file trên đĩa, không tin số tự báo của bước dựng |
| H5 | Prompt B-roll 5 tầng (`18–95` từ EN, `layers` `l1`–`l5`) qua Quy trình 3 Agent bám nghĩa đen `anchor_quote` (tách sub-beat `> 7,5 s` / 2 vế), `Vietnamese`, giấu mặt founder, chống nhựa/Anti-Slop/ẩn dụ CGI trừu tượng, `broll_fix.py lint` + Agent 3 duyệt 2 bản 720p |
| P1 | Style @__dviet là hồ sơ TUỲ CHỌN, chỉ bật khi người dùng gọi tên; khi bật áp P2–P5, mọi luật khác giữ |
| P6 | Hồ sơ `minimal-edu` (kiểu Joseph / Arthur Brooks) TUỲ CHỌN, chỉ bật khi người dùng gọi tên ("kiểu minimal / Brooks / Joseph"): ghi `W/profile.json` = {"profile": "minimal-edu"}; áp P7–P12 (cụm 1 từ lớn, Inter + Playfair, chữ vào nhanh / mờ ra 2 khung, chuyển cảnh talking-head đa dạng `cut_plan.plan_cuts_min` + `MotionFX.th_join` (cắt cứng ≤ 40 %, ≥ 6 kiểu), từ lớn xoay nhiều màu `brooks_text.HeroColors` (chữ màu glow nhẹ, trắng / đen không glow) và có chiều sâu `brooks_text.HeroLooks` (`looks=`, `gfx_dir=`: glow / gradient PNG / bóng đổ sâu, nền sáng không glow), 10 kiểu cảnh đồ hoạ); giữ B2, B8, B10, B14, D–G; không bật cùng @__dviet. Chi tiết `references/minimal-edu-style.json` |

Không làm (luật đã bị thay, xem `rules-full.md` › "Luật đã bị thay"): tốc độ 1.25x / 1.15x; flash ≥ 40 %; dải tối sau phụ đề / `vignette_bottom`; chữ có viền; phụ đề chỉ trắng + vàng; cân giọng −16 LUFS từng clip làm chuẩn cuối; xuất 5 MP4 trước khi duyệt; `rvm-matte` + despill cho phông xanh `soucre thô`; "audit 8/8"; Muse làm công cụ tạo B-roll mặc định (X13); giới hạn B-roll ≤ 1 lần / video (X14); kéo stock / `auto-footage` thay B-roll Google Flow vượt trần 5 % (D15).

## Instructions

### 0. Mở đầu mỗi việc
Thông số / ngoại lệ nguyên văn của từng mục dưới đây nằm ở `references/rules-details.md` (mục cùng mã luật, mục "SKILL §<số mục>" và mục "CHUNG") — đọc mục tương ứng khi làm phần đó.

1. Đọc lời người dùng, điền brief theo mẫu `kb-master-video-edit.md` › brief.md (ô trống dùng mặc định trong ngoặc): nguồn (kịch bản / thư mục / file / project đang mở), yêu cầu sửa, CTA, ứng dụng (1 = FilmCraft mặc định, 2 = EffectCraft), style. Hồ sơ từng loại việc: `kb-master-video-edit.md` › profiles.md.
2. Kiểm môi trường một lần mỗi phiên: `$PY scripts/env_status.py` (và `$PY scripts/selfcheck.py --quick` khi nghi thiếu công cụ).
3. Xếp loại việc theo bảng mục 1. Không chắc → chọn theo bảng, ghi giả định, không dừng để hỏi (G12).

### 1. Bảng loại việc (mọi tài liệu đều nằm trong skill này)

| Mã | Việc | Dấu hiệu | Làm theo | Đọc thêm (`references/`) |
|---|---|---|---|---|
| A | Footage người nói → project FilmCraft | file quay thật (C00xx, IMG_), "dựng talking head" | mục 3 (quy trình chuẩn) | `kb-talking-head-premiere.md`, `kb-dviet-viral-text-audio-edit.md`, `kb-facecammaxxing.md` (VFX quanh người, `scripts/facecam.py`) |
| B | Video người nói AI (HeyGen) hoặc dự án HyperFrames | file HeyGen, link Studio | mục 3 nếu dựng FilmCraft; HyperFrames theo kb | `kb-hyperframes*.md`, `kb-hyperframes-studio.md`, `kb-hyperframes-registry.md`, `kb-hyperframes-audio.md`, `kb-talking-head-recut.md`, `kb-embedded-captions.md` |
| C | Lô HeyGen kiểu đã duyệt, giao đội OPA | "lô tiếp theo", "giao OPA" | `kb-opa-delegate.md`; bắt buộc giữ A1 với đội OPA (không render MP4 trước duyệt) | `kb-dung-video-talking-head.md` |
| D | Promo / explainer không footage | chỉ chữ, ảnh, nhạc, giọng đọc | chọn 1 công cụ theo kb | `kb-hyperframes.md`, `kb-general-video.md`, `kb-remotion-best-practices.md`, `kb-kinetic-typography.md`, `kb-kinetic-reel.md`, `kb-motion-director.md`, `kb-video-talkcraft.md`, `kb-anything2explainer.md`, `kb-manim-video.md` |
| E | Video sản phẩm từ trang web | URL, landing page | Remotion | `kb-remotion-best-practices.md`, `kb-remotion-25d-motion.md`, `kb-remotion-saas.md` |
| F | Phim 3D mascot / nhân vật | "3D", mascot OPA | three.js | `kb-mascot-film-3d.md`, `kb-blender-motion-state-inspection.md` |
| G | Motion graphics AE / EffectCraft | `.jsx`, `.aep`, `.ecproj`, intro logo | ExtendScript / EffectCraft | `kb-ae-script-builder.md`, `kb-ae-template-customizer.md` (cần AE Windows), `kb-ae-logo-intro-reveal.md`, `kb-omni-flash-motion-director.md`, `kb-sketch-to-mobile-ui.md` |
| H | Sửa bản đã giao | gửi MP4 / project, chỉ lỗi | mục 8 (A3, G6) | — |
| I | Âm thanh | ồn, vang, nhỏ to, SFX, nhạc | mục 6 | `kb-motion-sfx-audio-mastering.md`, `kb-hyperframes-audio.md` (khi mix âm thanh dự án HyperFrames), `kb-audio-jingle.md` (nhạc AI, trả phí — hỏi trước) |
| J | Phụ đề / caption | "thêm phụ đề" | FilmCraft: `text_fx` `word_captions` / `MotionFX.captions2` | `kb-remotion-captions.md`, `kb-embedded-captions.md` |
| K | Cắt, ghép, nén, đổi khung, tải nguồn | trim, concat, 9:16 | ffmpeg | `kb-video-editing.md`, `kb-ffmpeg.md`, `kb-video-download.md`, `kb-video-use.md` |
| L | Sửa trong OpenChatCut | "trong OpenChatCut" | MCP `openchatcut` (kiểm kết nối trước; hỏng thì báo) | `kb-openchatcut.md`, `kb-talking-head-guide.md` |
| M | Học style từ kênh / video mẫu | link TikTok / YouTube, "train skill edit video", "nhân bản style" | đo máy (`scripts/style_analysis/`) + huấn luyện đóng gói skill portable qua `scripts/apps/video-style-trainer/scripts/style_trainer.py` (`probe` → `scaffold` → `feedback` 4 vòng kèm screenshot → `lint-skill`) | `kb-video-style-trainer.md`, `kb-master-video-edit.md` › style-analysis.md, `kb-video-understand.md`, `kb-storyboard-shot-breakdown.md` |
| N | Ảnh / clip AI, 3D assets minh hoạ câu thoại, B-roll kho / stock, thumbnail, GIF | B-roll, tìm footage, thumbnail, 3D asset minh hoạ kịch bản, đọc video/kịch bản viết prompt B-roll | phân tích video hoặc kịch bản tách đoạn B-roll + prompt H5 (`scripts/broll_from_video.py`, `references/script-to-flow-broll.md`, `references/master-video-prompt-architecture.md`); #1 **Google Flow mặc định (100 % mục tiêu, ≥ 95 % — D3, D15)** theo `flow-broll.md` (MCP khi phiên có tool `flow_*`, không thì trình duyệt Cindy); #2 **3D assets/đạo cụ minh hoạ câu nói** bằng Google Flow (`scripts/flow_3d_assets.py`, `references/flow-3d-assets.md`); #3 **ngoại lệ footage thật / stock ≤ 2–5 % (D15)** trong `TNEDIT/06_B-Roll` + stock bằng `auto-footage` (`scripts/apps/auto-footage/scripts/footage.py`, `kb-auto-footage.md`); #4 **Muse local chỉ dự phòng khẩn** khi Flow hỏng và người dùng đồng ý (mục 5, D3) | `references/master-video-prompt-architecture.md`, `references/flow-broll.md`, `references/script-to-flow-broll.md`, `references/flow-3d-assets.md`, `kb-auto-footage.md`, `kb-codex-imagegen.md` (dự phòng, cần đồng ý), `kb-video-thumbnail-generator.md`, `kb-fal-ai-media.md` / `kb-video-shortform.md` (trả phí — hỏi trước) |
| O | Video dài / livestream / nhiều clip → clip ngắn, montage | podcast, "cắt short", nhạc nhịp | theo kb | `kb-long-video-to-shorts.md`, `kb-livestream-to-clips.md`, `kb-multi-clips-to-reels.md`, `kb-beat-sync-montage.md`, `kb-batch-montage-variants.md`, `kb-news-rough-cut.md`, `kb-ecommerce-product-montage.md` |
| P | Kịch bản quảng cáo, motion graphic, nhân vật 2D, BĐS | "kịch bản quảng cáo", "chèn motion" | theo kb | `kb-product-ad-video-script.md`, `kb-motion-graphic-placement.md`, `kb-character-2d.md`, `kb-real-estate-video-editing.md`, `kb-motion-presets-vi.md` |
| Q | Kịch bản / brief → A-Roll & B-Roll, thư mục đánh số, báo cáo 10 bước | gửi kịch bản / spec | mục 2 | `kb-master-video-edit.md` › aroll-broll-workflow.md, `kb-script-aroll-broll-analyzer.md`, `kb-heygen-veo-broll-video.md` |
| R | Kế hoạch nội dung / kịch bản thương hiệu cá nhân | "lịch đăng", "4 trụ cột" | theo kb |
| S | Bảng phân cảnh dựng (Edit Blueprint) / shotlist cho Premiere, After Effects, CapCut | "bảng phân cảnh", "shotlist", "edit script", "dựng trên Premiere / CapCut" | quy trình 7 bước trong `references/visual-motion-system.md` (mục CORE INSTRUCTIONS), đầu ra 5 phần A–E | `references/visual-motion-system.md` | `kb-personal-brand-video-engine.md`, `kb-remotion-vietnamese-reel-expert.md` |

Khác (khi việc cần): `kb-auto-footage.md`, `kb-video-style-trainer.md`, `kb-painted-animation.md`, `kb-lemo-opuscar.md`, `kb-ui-demo.md`, `kb-synthetic-screen-recording.md`, `kb-media-use.md`, `kb-videodb.md`, `kb-remotion*.md`, `kb-hyperframes-*.md`, `kb-hyperframes-audio.md`, `kb-hyperframes-registry.md`, `kb-hyperframes-studio.md`, `kb-opa-design-system-chatbot.md`, `kb-craft-handoff.md` (bộ ghi `.fcproj`), `kb-strip-media-metadata.md`. Danh mục đủ 81 kb: `references/kb-INDEX.md`. Code của kb nằm ở `scripts/apps/<tên>/`; khi kb ghi đường dẫn cũ (`~/.claude/skills/<x>/…`, `modules/<x>/…`) thì đổi thành `scripts/apps/<x>/…` hoặc `references/kb-<x>.md`.

Footage người nói không bao giờ đi đường D, E hay F.

### 2. Kịch bản → A-Roll / B-Roll (việc Q)
**Lệnh trọn gói** (đọc kịch bản → A-roll HeyGen nhiều góc → B-roll → source thật / tư liệu thật, cả lô 30–50 kịch bản): làm theo `references/quy-trinh-nhan-lenh-video.md` (kiểm hạ tầng trước; mỗi video 2–4 A-roll ở các góc khác nhau; ngân hàng câu A-roll dùng chung `scripts/aroll_bank.py`; gán góc `scripts/heygen_looks.py`).
0. **Thư mục đã có sẵn?** Có `00_storyboard_manifest.json` (đã phân tích) → BỎ bước 1, dùng manifest có sẵn; liệt kê trước cho người dùng: file A-roll / B-roll đã có (không dựng lại trừ khi được yêu cầu), cảnh `live_shoot` (A-roll **quay thật** — người dùng quay hoặc lấy source thô, KHÔNG gửi HeyGen), bản dựng cũ (`.fcproj`, thư mục phiên bản) sẽ giữ nguyên.
Chi tiết nguyên văn: `references/rules-details.md` › SKILL §2, SKILL §2.1 (thứ tự xen kẽ A/B bất kỳ: `01_a-roll-1` → `02_b-roll-1` → `03_a-roll-2` hoặc mở đầu bằng B-roll).
1. Phân tích (0 credit): `$PY scripts/analyze_and_scaffold.py from-spec "<SPEC.md>" --out-dir "<thư mục tổng>" [--filter-id KB01]` (kịch bản JSON: `from-json`; xuất lại báo cáo: `report`). Script tự chọn tỷ lệ theo dạng kịch bản: `balanced_credit_saver` mặc định (30–38 % A-roll, giữ A-roll ở mở màn / chuyển ý / dẫn chứng / CTA, tiết kiệm ~68 % credit HeyGen), `aroll_heavy` (tâm sự, kể chuyện — 50–70 %), `broll_heavy` (thao tác, review — 15–28 %). Kết quả: thư mục con mỗi kịch bản với `00_BANG_PHAN_CANH.md`, `00_storyboard_manifest.json` (`segments[]`: `seq_index`, `role_id`, `tts_text`, `display_text`, `visual_direction`, `duration_sec`, `pain_keywords`, `live_shoot`…), `prompts_heygen_aroll.json`, `prompts_elevenlabs_voice.json`, `prompts_muse_veo_broll.json`; thư mục tổng có `00_BAO_CAO_PHAN_TICH_AROLL_BROLL.md`, `00_DANH_MUC_TONG_KICH_BAN.md`.
1b. **Prompt B-roll luôn viết lại bằng tiếng Anh** trước khi tạo: bước phân tích sinh prompt từ `visual_direction` tiếng Việt, còn `render_muse_broll.py` từ chối prompt không đạt H5. Ngay sau bước 1, với mọi cảnh B-roll chạy §2 bước 5b mục 2–4 (`broll_fix.py plan` → viết `broll_new_prompts.json` → `lint` → `prepare`) rồi mới `render-broll`.
2. Tên file đánh số kép: A-roll `<STT>_a-roll-<N>.mp4`; B-roll `<STT>_b-roll-<M>.mp4` + giọng `<STT>_voice-b-roll-<M>.mp3` (cùng STT). Số, %, tiền trong lời đọc đã đổi sang chữ (`tts_text`; nhanh: `$PY scripts/normalize_tts.py "câu"`). Giọng B-roll (ElevenLabs): skill CHƯA có lệnh render, chỉ xuất `prompts_elevenlabs_voice.json` — tạo giọng là bước riêng (người dùng hoặc công cụ ngoài), không tự gọi dịch vụ trả phí.
3. Cả lô: `$PY scripts/rotation.py plan <gốc lô> KB06 KB07 …` rồi `$PY scripts/batch_plan.py <lô>` → đưa bảng kế hoạch cho người dùng **duyệt lần 1 trước khi tốn credit**.
4. A-roll HeyGen (mỗi video 2–4 cảnh, mỗi cảnh một góc / look khác, hai cảnh A-roll liền nhau không cùng góc): `$PY scripts/render_heygen_aroll.py <thư mục> --looks W/looks.json --assign auto --estimate` (looks: `scripts/heygen_looks.py list --group <id>`; id nhóm avatar do người dùng đưa hoặc `list --all`) — `analyze_and_scaffold.py render-aroll` chuyển tiếp cùng cờ. Cảnh `live_shoot` bị bỏ qua kèm dòng cảnh báo. Manifest có > 4 A-roll → đề xuất giữ 2–4 cảnh quan trọng (mở đầu / bước ngoặt / kêu gọi), phần còn lại thành B-roll + giọng, ⏸ người dùng duyệt. **Mặc định CHẠY THỬ** (0 credit). Chỉ khi người dùng gửi khoá trong chat mới thêm `--yes` để chạy thật (G2). Xong A-roll mới sang bước 5.
5. B-roll mặc định bằng **Google Flow** (D3, D15 — 100 % mục tiêu, ≥ 95 %; đường thực thi theo phiên: phiên có tool `flow_*` → MCP `google-flow`, không có → trình duyệt Cindy): đi qua **Quy trình 3 Agent** (`references/script-to-flow-broll.md`): Agent 1 đọc toàn bộ `tts_text`, tách đoạn `> 7,5 s` hoặc 2 vế đối lập thành sub-beats và viết `script_beat_vi` đời thực (CẤM ẩn dụ CGI trừu tượng); Agent 2 viết đủ `layers` 5 tầng chống nhựa (`l1_shot_subject`..`l5_camera_motion`) ghép thành `prompt` `18–95` từ tiếng Anh đạt H5 (`anchor_quote` trích đúng lời cảnh); Agent 3 kiểm `lint` + xem 2 bản. Chạy `$PY scripts/broll_fix.py plan <thư mục> --engine flow` → `lint` → `prepare --source flow` → MCP: `flow_list_accounts` / `flow_inspect_account` (báo số dư tín dụng; thiếu thì dừng, không tự mua), dựng tham số bằng `$PY scripts/broll_fix.py mcp-jobs <thư mục>` (chỉ truyền `durationSeconds` / `outputs` khi `flow_inspect_account` liệt kê; cần 2 bản mà `outputs: 2` không có → gửi 2 job `outputs: 1`; `model` và `aspectRatio` đúng như inspect trả; `upscale: "1080p"`, không có thì `highest_available`; không lấy bản 720p làm clip cuối) → Agent 3 xem chọn bằng mắt → tải về; trình duyệt Cindy (không có tool `flow_*`): làm theo `references/flow-broll.md` (x2, chọn giây, tải 1080p) → `normalize` → `verify` (clip ngắn hơn giọng − 0,3 s thì FAIL: MCP không đặt được độ dài → tạo lại bằng trình duyệt với đúng số giây, hoặc tách câu thành 2 cảnh; ghi vào báo cáo). Báo cáo ghi prompt thực sự đã gửi (Flow Agent UI có thể viết lại prompt); Agent 3 chấm clip theo `anchor_quote`, không theo prompt. Chỉ dùng `render_muse_broll.py` / `render-broll` làm dự phòng khẩn khi Google Flow không khả dụng và người dùng đồng ý (D3). Không dùng `render-all`.
5b. **Tự tạo lại B-roll sai kịch bản / nhựa / lệch nghĩa** (D9 — mặc định qua **Google Flow** theo D3, D15, không hỏi lại nếu đủ tín dụng trong gói): khi `scene_check` FAIL `script_source` / `broll_h5`, hoặc prompt chưa đạt H5 5 tầng. Mỗi dòng một lệnh, đọc kết quả rồi mới gọi lệnh sau; làm TRƯỚC bước tăng tốc (§3 bước 4 — làm sau thì tăng tốc lại riêng file đó):
   1. `$PY scripts/broll_fix.py plan <thư mục video> [--speed <speed của speed_plan; video < 45 s → 1.0>] --engine flow` → in cảnh lỗi, độ dài giọng, số giây cần xin và tín dụng x2.
   2. **3-Agent Prompt Rewrite:** Agent 1 đọc trọn `tts_text`, tách sub-beat nếu `> 7,5 s` hoặc 2 vế, viết `script_beat_vi` nghĩa đen đời thực (CẤM ẩn dụ CGI trừu tượng); Agent 2 viết `broll_new_prompts.json` đủ `layers` 5 tầng chống nhựa (`18–95` từ EN, từ CHÍNH `anchor_quote` của cảnh); Agent 3 chạy `$PY scripts/broll_fix.py lint <thư mục video> --prompts broll_new_prompts.json` (0 lỗi, strict layers & anti-plastic).
   3. `$PY scripts/broll_fix.py prepare <thư mục video> --prompts broll_new_prompts.json --source flow` (`--dry-run` để xem trước) → sao lưu file cũ vào `~/.cache/opa-video-studio/backup/`, cập nhật prompts + manifest.
   4. Tạo bằng **Google Flow (D3)** theo phiên: có tool `flow_*` → MCP; không có → trình duyệt Cindy (`references/flow-broll.md`). MCP: `flow_list_accounts` → `flow_inspect_account` (so số dư với `plan`; thiếu thì dừng) → `$PY scripts/broll_fix.py mcp-jobs <thư mục video> --inspect <kết quả flow_inspect_account đã lưu .json>` dựng tham số → `flow_generate_video` (`model` và `aspectRatio` đúng như inspect trả; `durationSeconds` / `outputs` chỉ khi inspect liệt kê, cần 2 bản mà không có `outputs: 2` thì gửi 2 job `outputs: 1`; `upscale: "1080p"` khi inspect có, không thì `highest_available`; không đính mặt A4) → `flow_job_status` → **Agent 3 chọn 1 trong 2 bản bằng mắt** (loại ngay bản da nhựa, ngón tay méo, vật phi vật lý, chữ/logo, cắt cảnh ngầm hoặc lệch `anchor_quote`) → `flow_download_job` bản 1080p vào `<thư mục video>/_google_raw/` (không dùng 720p làm clip cuối) → `$PY scripts/broll_fix.py normalize _google_raw/<file> <thư mục video>/<STT>_b-roll-<M>.mp4 [--mark flow]` → `verify`: clip ngắn hơn giọng − 0,3 s (MCP không đặt được độ dài) → tạo lại bằng trình duyệt Cindy với đúng số giây hoặc tách câu thành 2 cảnh, ghi vào báo cáo. Ghi prompt thực sự đã gửi vào báo cáo (Flow Agent UI có thể viết lại); Agent 3 chấm theo `anchor_quote`. (Flow hỏng cả hai đường → xin ý kiến dùng Muse dự phòng khẩn: `broll_fix.py ready` → `render_muse_broll.py <thư mục video> --shot <STT>_b-roll-<M>.mp4`).
   5. `$PY scripts/broll_fix.py verify <thư mục video> --scenes 3,4,5 [--speed <theo speed_plan>]` → Agent 3 mở `qa/broll_check_sheet.jpg` xem lại: đúng nghĩa đen lời thoại, không da nhựa/CGI, không chữ/logo; ghi "đã nhìn" vào báo cáo. Hỏng → sửa `layers` và tạo lại tối đa 1 lần; vẫn hỏng → báo.
   6. `scene_check` lại (0 FAIL).
6. Cổng 05.5: `$PY scripts/analyze_and_scaffold.py validate "<thư mục tổng>" --check-media` — thiếu file thì báo đúng tên và dừng (G3).
7. Sang mục 3 để dựng.

### 3. Dựng talking head trên FilmCraft (việc A, B, Q) — quy trình chuẩn
Chi tiết nguyên văn: `references/rules-details.md` › SKILL §3.3 (ngưỡng cắt lặng), SKILL §3.6 (bảng khoảnh khắc → chữ / chuyển cảnh / SFX).
Mỗi bước MỘT lệnh; đọc kết quả rồi mới sang bước sau; ⏸ = dừng cho người dùng. Không lệnh nào tự gọi lệnh khác. Thư mục: `V` = thư mục video (đánh số; chỉ đọc — trừ §2 bước 5b thay file B-roll trong `V` sau khi sao lưu), `O` = `V/<phiên bản>` (mọi file ra), `W` = `O/work`. `<MÃ>` = `script_id` trong `V/00_storyboard_manifest.json` (vd `OPA05`). Tất cả phân tích tính bằng giây GỐC; đổi sang giây đã tăng tốc ở bước cuối (`build_kit.at_speed`).

| # | Lệnh | Ra / đạt |
|---|---|---|
| 1 | Nguồn — BỎ QUA khi nguồn là HeyGen / Muse (việc Q); chỉ việc A, footage thật: 4K ngang → proxy 1080×1920 ffmpeg (Sony `iec61966-2-4` → `setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709`); phông xanh `soucre thô`: `$PY scripts/studio_plate.py fit\|nochair\|curtain REF.png PLATE.png [--flip]` rồi `$PY scripts/chroma_studio.py SRC.MP4 OUT.mp4 PLATE.png DUR 1.0 [zoom=1.3] [start=0.2]` (D11, D12; tăng tốc làm ở bước 4); nền sáng: `$PY scripts/frame_person.py analyze\|fix` (D7). Footage ồn: `$PY scripts/prep_video.py --input <file> --mode light\|studio\|heavy` (F6) | media gốc sạch |
| 2 | Bóc lời MỘT lần trên media GỐC: `$PY scripts/transcribe.py --manifest V/00_storyboard_manifest.json --out O` | `O/transcripts/*.json` |
| 3 | Cắt lặng trên media gốc + chọn tốc độ (D4): `$PY scripts/speed_media.py plan V --manifest V/00_storyboard_manifest.json --transcripts O/transcripts --out O/media/speed_plan.json` | in "giữ lại N s → 1.1x"; video < 45 s → 1.0x |
| 4 | Tăng tốc SAU khi cắt lặng: `$PY scripts/speed_media.py apply V --manifest … --plan O/media/speed_plan.json --out O/media` rồi `$PY scripts/speed_media.py check V --manifest … --out O/media` | `O/media/x110\|x105/`, check 0 lỗi (1.0x: không ghi gì, dùng V) |
| 5 | (Không chạy trước.) Lớp người cho chữ sau đầu do bước 8 yêu cầu đúng đoạn cần | — |
| 6 | `$PY scripts/rotation.py plan V <MÃ> --out O` (lô: `plan <gốc lô> KB06 KB07 …`) | `O/rotation.json` (key_seed, opening_pair, cut_seed) |
| 7 | ⏸ `cp assets/motion-fx/build_spec_q.py W/build_spec.py`, CHỈ sửa dòng `# EDIT:` (KEY_SPECS chữ chính ~1 khối / 5–6 s theo hướng dẫn trong file, MUSIC, EXTRA_PAIN, HEAD_TOP = số `head_top` đo bằng `$PY scripts/frame_person.py analyze <A-roll>` — với HeyGen chỉ lấy số này, bỏ qua dòng `plan` (D7 không áp avatar). Mẫu tự đặt chữ hook TRƯỚC đầu khi sau đầu bị che > 20 % — đúng luật B9 (đọc được trước), không ép matte) | `W/build_spec.py` |
| 7b | (Khuyên dùng) Kế hoạch chọn cảnh: chạy bước 8 một lần với KEY_SPECS rỗng để có `W/words_tl.json` → `$PY scripts/plan_doc.py build W [--manifest V/00_storyboard_manifest.json] --out W/edit_plan.html` → ⏸ người dùng mở trang, chọn A/B/C từng nhịp ("Gợi ý" theo D16), ghi chú, bấm "Xuất JSON" → `$PY scripts/plan_doc.py export <file tải về> W` → `W/plan_export.json`; chạy lại bước 8 với KEY_SPECS rỗng → in sẵn các dòng KEY_SPECS từ kế hoạch để dán vào khối `# EDIT:` (nhịp chọn B-roll / đồ hoạ được in `[chưa hỗ trợ]` để làm tay). Hồ sơ minimal-edu: tạo `W/profile.json` trước bước 8; tốc độ 1.05x (bước 3: `speed_media.py plan … --profile minimal-edu`, vẫn D4: < 45 s → 1.0x) | `W/edit_plan.html`, `W/plan_export.json` |
| 8 | `OPA_SKILL_DIR=<thư mục skill> $PY W/build_spec.py` — nếu in lệnh `matte.py … --start S --dur D` (chữ sau đầu thiếu lớp người) thì chạy lệnh đó rồi chạy lại bước 8 | `W/<mã>.craft.json`, `W/words_tl.json`, `W/transition_plan.md`, `W/pain.json` |
| 8m | **Chỉ khi hồ sơ minimal-edu bật** (`W/profile.json`): sau bước 8, `mv W/<mã>.craft.json W/<mã>.base.craft.json`; `cp assets/motion-fx/build_spec_minimal.py W/build_minimal.py`, CHỈ sửa khối `# EDIT:` (GROUPS cụm chữ «a \| b \| *từ lớn \| ~từ nghiêng», HEAD_TOP, SCENE_GFX polaroid / mũi tên / đồ thị / thẻ trích dẫn, CTA_WORD, PAIN — ví dụ KB08 ở đầu file); `OPA_SKILL_DIR=<thư mục skill> $PY W/build_minimal.py` → ghi lại `W/<mã>.craft.json` (chữ chuyển động, vùng an toàn, chuyển cảnh `plan_cuts_min`). Bước 9 trở đi giữ nguyên | `W/<mã>.craft.json` kiểu minimal |
| 9 | ⏸ Đưa người dùng xem `transition_plan.md` (C3: Giây \| Cảnh \| Chữ chính \| Chuyển cảnh \| Zoom \| Nỗi đau \| SFX \| Lý do) | — |
| 10 | `$PY scripts/audio_levels.py plan W/<mã>.craft.json` (F3; tự hạ SFX chồng nhau) | `W/<mã>.levels.craft.json` — MỌI lệnh sau dùng file `.levels` |
| 11 | `$PY scripts/spec_lint.py W/<mã>.levels.craft.json --words W/words_tl.json` | 0 HARD (SOFT ghi báo cáo) |
| 12 | `$PY scripts/scene_check.py --manifest V/00_storyboard_manifest.json --spec W/<mã>.levels.craft.json --words W/words_tl.json --transcripts O/transcripts --review W/scene_review.md` | 0 FAIL (D14, D9; FAIL `script_source` → §2 bước 5b) |
| 13 | `$PY scripts/edit_rules.py audit W/<mã>.levels.craft.json --words W/words_tl.json --manifest V/00_storyboard_manifest.json` (tự đọc `W/pain.json`). CẢNH BÁO "nói liền > 8 s" (D1): thêm cảnh chèn đúng lời đoạn đó — mặc định tạo B-roll mới qua **Google Flow** theo §2 bước 5b (`D3, D15`); chỉ lấy footage thật / stock từ kho `TNEDIT/06_B-Roll` (`auto-footage`) trong **trần ngoại lệ 2–5 % (tối đa 5 %)** theo `D15` (khớp lời ≥ 0,28, tuân `D8` ≤ 2 lần / video & ≤ 2 video, cấm lấy clip gắn mã kịch bản khác theo `D9`, chuẩn hoá `broll_fix.py normalize`); Google Flow không sẵn sàng (và không có dự phòng đồng ý) → giữ CẢNH BÁO, ghi bàn giao | dòng `Tổng: 0 LỖI …` (12 tiêu chí) |
| 14 | `$PY scripts/apps/craft-handoff/tools/fc_build_fast.py W/<mã>.levels.craft.json O/<MÃ>.fcproj --report W/fc_build_report.json` (dự phòng `fc_build.py`) | `"ok": true`, `"mismatches": {}` |
| 15 | `$PY scripts/contact_sheet.py times W/<mã>.levels.craft.json --full --out O/qa/times.txt` rồi `$PY scripts/fc_fast_qa.py O/<MÃ>.fcproj --frames-dir O/qa/frames --fps 30 --times-file O/qa/times.txt --wav O/qa/mix.wav` (gồm dải tối mép trên B12 + limiter) | khung + `mix.wav` |
| 16 | `$PY scripts/contact_sheet.py sheet W/<mã>.levels.craft.json O/qa/frames O/qa/contact_sheet.jpg --full` → XEM ảnh | đủ dấu, không đè mặt / dấu, không lộ phông, phụ đề không chồng |
| 17 | `$PY scripts/qa_sync.py W/<mã>.levels.craft.json O/<MÃ>.fcproj O/qa/sync` (clip đo 270×480, tự xoá — không phải bản giao, A1). Có LỆCH: chạy đúng lệnh `sfx_shift.py` mà `qa_sync` in ra (ra `W/<mã>.levels.shifted.craft.json`), MỘT lần; dựng lại bước 14 bằng file `.shifted` rồi chạy lại 15–18 trên file đó (khung, `mix.wav`, stems đều phải của bản mới). Còn LỆCH không chặn → ghi báo cáo, không dời lần hai | đo MỌI nhịp có SFX: chuyển cảnh (khung đổi mạnh nhất), chữ hiện (lúc chữ vào xong), punch nỗi đau (keyframe), SFX mở đầu (khung 0–1); đỉnh ≤ 0,05 s; thoát 1 (chặn) khi tiếng SỚM hơn hình > 0,1 s |
| 18 | `$PY scripts/audio_levels.py stems W/<mã>.levels.craft.json O/qa/stems` rồi `$PY scripts/audio_levels.py check O/qa/mix.wav --stems O/qa/stems`; `$PY scripts/audit_sfx.py O/<MÃ>.fcproj --out O/qa` | thoát 0 (2 = CHƯA KIỂM, không được gọi là đạt); `repeated_takes = 0` |
| 19 | ⏸ `python3 scripts/open_in_app.py O/<MÃ>.fcproj` → chờ "DUYỆT" / góp ý. KHÔNG xuất MP4 (A1) | — |

Bước 11–13 là cổng CHẶN (G5): chưa đạt thì sửa `build_spec.py` / manifest rồi chạy lại từ bước 8. Cổng chỉ vướng vì việc ngoài tầm (Google Flow không sẵn sàng / thiếu tín dụng khi cần tạo lại B-roll, D3; thiếu file, G3): vẫn dựng và kiểm hết các bước còn lại, gọi sản phẩm là "bản nháp — chưa qua cổng <mục>", ⏸ báo người dùng đúng lý do; chỉ mở cho xem khi người dùng muốn. Đặt nguồn (do mẫu bước 7 làm, giữ đúng khi sửa tay): manifest theo `seq_prefix`; A-roll lên V1 + A1; B-roll câm lên V1 / V2; `voice-b-roll` xuống A1 khớp khít hình (D14 ≤ 0,12 s); cảnh chèn chỉ trong lúc lời của chính cảnh nó minh hoạ (D9); thứ tự track: V1 → `*fx.tracks()` → giọng → SFX mở đầu ngay dưới giọng → SFX → nhạc. Giọng B-roll HeyGen dồn mốc → `$PY scripts/retime_voice.py "<V>" [--all]` (B16). Ảnh bìa chỉ khi người dùng yêu cầu: `fx.cover(png)` (A6). Mẫu cũ cho video không có manifest: `assets/motion-fx/example_build_spec.py`.

Thời gian người dùng giao ("trong N phút") là thời gian thực tới lúc mở project; mục tiêu < 10 phút (G10): chỉ dựng một lần sau khi soát spec, kiểm 3–4 khung trước khi mở.

### 4. Chữ (FilmCraft)
Chi tiết nguyên văn: `references/rules-details.md` › SKILL §4, CHUNG (lưu ý từng hiệu ứng: viết tay mảnh trên nền sáng, glow trắng trên nền sáng, overlay cần nền chi tiết, nhãn `ui_card` dưới mép thẻ, bảo trì thư viện chữ).
- 24 hiệu ứng chữ (`scripts/text_fx.py`; trong tài liệu gốc đánh mã B1–B24 — ở đây gọi **T1–T24** để khỏi trùng mã luật): T1 cặp lớn–nhỏ `pair` · T2 từ lớn thay `swap_big` · T3/T4 chồng 3 tầng `stack3(readable=)` · T5 viết tay phát sáng chéo `script_accent` · T6 viết tay thay nhau `script_swap` · T7 số khổng lồ + bookmark `number_hook` · T8 trượt lên `slide_up_text` · T9 giả 3D `swing3d` · T10 trượt xuống nhoè `slide_down_text` · T11 phụ đề từng chữ `word_captions` · T12 chữ sau đầu `behind_head` · T13 chữ gắn tường `wall_text` · T14 nghiêng / tràn khung `tilt_text`, `punch_overflow` · T15 phát sáng `glow_text` · T16 mờ ảo `dreamy_blur` · T17 overlay `overlay_text` · T18 gradient `gradient_word` · T19 gõ trong khung chọn `typed_box` · T20 pill kính `glass_pill` · T21 thẻ UI `ui_card` · T22 CTA lưu lại `cta_save` · T23 gạch / đổi font / chớp / cong `strike_word`, `font_flip`, `flicker_text`, `curved_caption` · T24 bố cục quay màn hình `tutorial_layout`. Thông số và trạng thái kiểm thật: `kb-master-video-edit.md` › text-fx.md; xem trước: `assets/text-fx/preview/XEM_TRUOC_24_HIEU_UNG.html`.
- `fx.tracks()` tự xếp lớp (đồ hoạ dưới → thẻ → chữ sau người → lớp người → phụ đề → chữ → viết tay → đồ hoạ trên) và tự thêm vào/giữ/ra (B14). `fx.cues` chỉ là gợi ý SFX.
- **3D Assets trên timeline (`MotionFX.asset_3d`)**: dùng `fx.asset_3d(src, at, dur, pos=..., scale=..., anim="float"|"spin3d"|"slide"|"pop", cue="pop")` (`scripts/motion_fx.py`) để đặt ảnh RGBA 3D hoặc clip 3D lên lane `gfx_over` (trên V1/B-roll, không đè phụ đề/chữ chính) kèm chuyển động B14 (scale pop + trôi/xoay nhẹ + fade in/out) và gợi ý SFX.
- Không dùng chuyển cảnh `typewriter` của FilmCraft (quét lưới + con trỏ); gõ chữ dùng `crop.right`.
- `graphic_text.position` là điểm canh lề trên baseline dòng đầu, không phải tâm khối chữ. Bebas Neue không có dấu → chữ có dấu tự đổi SF Pro Heavy. Template DViet `.fcgt` 1920×1080 → đặt lại 1080×1920.
- Đo đỉnh đầu / cằm trên ảnh lưới khung trước khi chọn `key_y`, `cap_y`, `head_top`; mặt thấp: `chest_y_pct` = cằm + 4.
- Hồ sơ @__dviet (chỉ khi người dùng chọn, P1–P5): `references/dviet-style.json` (gồm cập nhật `nov_2026_updates` & `slow_text`), `references/dviet-slow-text-study.md`, `kb-master-video-edit.md` › dviet-style-guide.md; `FX(accent="#F4C40C")` một màu nhấn.

### 5. Ảnh / clip AI & B-roll (Google Flow mặc định, 3D Assets, Auto-Footage ngoại lệ, Muse dự phòng)
1. **#1 Mặc định (100 % mục tiêu, ≥ 95 % — D3, D15): Google Flow, đường thực thi theo phiên (MCP `google-flow` khi phiên có tool `flow_*`, không thì trình duyệt Cindy)**:
   - **Quy trình 3 Agent đọc video / kịch bản → Prompt 5 tầng Anti-Plastic H5 → tạo B-roll qua Google Flow (`references/script-to-flow-broll.md`, `references/flow-broll.md`)**: với video thô chưa có kịch bản chạy `$PY scripts/broll_from_video.py analyze --video <clip.mp4> --out <dir>` (hoặc `--transcript <json>`) chia block 3–10 s, đánh dấu đoạn cần B-roll (D1 ≥ 25%, nói trơ ≤ 8 s, E2 nỗi đau); với kịch bản văn bản chạy `analyze_and_scaffold.py`. Tiếp theo chạy **Quy trình 3 Agent**: (1) *Agent 1 (Script Semantic Analyst)* đọc toàn bộ `tts_text`, tách sub-beat khi `> 7,5 s` hoặc 2 vế đối lập, viết `script_beat_vi` đời thực (CẤM ẩn dụ CGI trừu tượng); (2) *Agent 2 (5-Layer Anti-Plastic Prompt Architect)* viết `layers` (`l1_shot_subject`..`l5_camera_motion`) ghép thành `prompt` `18–95` từ EN đạt H5 bám `anchor_quote` theo Mục 5b (`references/master-video-prompt-architecture.md`); (3) *Agent 3 (Prompt & Visual Critic)* kiểm `$PY scripts/broll_from_video.py check-prompts` (hoặc `broll_fix.py plan --engine flow` → `lint` strict layers & anti-plastic → `prepare --source flow`) → tạo: phiên có tool `flow_*` → MCP `google-flow` (`flow_list_accounts` → `flow_inspect_account` → `$PY scripts/broll_fix.py mcp-jobs` dựng tham số → `flow_generate_video` với `model` / `aspectRatio` đúng inspect trả, `durationSeconds` / `outputs` chỉ khi inspect liệt kê (cần 2 bản mà không có `outputs: 2` → 2 job `outputs: 1`), `upscale: "1080p"` hoặc `highest_available` → `flow_job_status` → Agent 3 xem chọn bản nhựa/méo/lệch nghĩa → `flow_download_job` 1080p); phiên không có tool `flow_*` → trình duyệt Cindy đã đăng nhập (`references/flow-broll.md`, x2, chọn giây, tải 1080p) → `$PY scripts/broll_fix.py normalize <in> <out> [--mark flow]` → `verify`. MCP lỗi giữa chừng thì chuyển trình duyệt Cindy. Tuân giới hạn lặp D8 (`≤ 2 lần / video, ≤ 2 video`).
2. **#2 Tạo 3D Assets minh hoạ câu thoại bằng Google Flow (`references/flow-3d-assets.md`)**: dùng `$PY scripts/flow_3d_assets.py plan --manifest <00_storyboard_manifest.json> [--speed-plan <speed_plan.json>] [--mode image_alpha|video_3d|mixed] --out-dir <dir>` (hoặc `--plan <broll_plan.json>`) → `$PY scripts/flow_3d_assets.py lint-plan <3d_assets_plan.json>` → MCP `google-flow` (`flow_generate_image` với `nano-banana-pro` / `nano-banana-2` nền `#00FF00` cho `image_alpha`, hoặc `flow_generate_video` với `omni-flash` cho `video_3d`) → `extract-alpha` → `sheet` → gắn lên timeline bằng `MotionFX.asset_3d`.
3. **#3 Ngoại lệ footage thật / stock (`2–5 %`, trần cứng `≤ 5 %` — D15): `auto-footage`** (`F=~/.venvs/footage/bin/python; AF=scripts/apps/auto-footage/scripts/footage.py`, chi tiết `references/kb-auto-footage.md`): chỉ dùng khi cần footage thật trong trần `≤ 5 %` (ưu tiên `0 %` nếu Flow phủ đủ); nghiêm cấm kéo clip stock lặp lại từ `auto-footage` / Mixkit / TNEDIT để thay B-roll Google Flow hoặc vượt trần `D8` (`≤ 2 lần / video, ≤ 2 video`). Lệnh tìm: `$F $AF search "mô tả tiếng Anh"`.
4. **#4 Dự phòng khẩn cấp (chỉ khi Google Flow hỏng & người dùng đồng ý — D3): Muse local** (`http://127.0.0.1:18610/v1`, khoá `~/.config/muse/env`, không ghi vào project): `$PY scripts/muse_gen.py image "prompt" --size 9:16 -o x.png [--ref a.jpg] [--transparent]` (~30 s, 1152×2048); `$PY scripts/muse_gen.py video "prompt" --size 9:16 --seconds 5 [--first-frame a.png] -o x.mp4` (1–2 phút, 720×1280 hoặc 704×1248 → bỏ tiếng, scale 1080×1920 theo `build_kit.broll_scale`). Không có cả Google Flow lẫn Muse (có đồng ý) → báo người dùng, dừng, không tự dùng dịch vụ trả phí khác.
- **Xoá metadata lộ nguồn (A5)**: `$PY scripts/apps/strip-media-metadata/scripts/strip_metadata.py <file>` (`references/kb-strip-media-metadata.md`).

### 6. Âm thanh (việc I và mọi video)
- Mức: F3 — `$PY scripts/audio_levels.py plan SPEC.craft.json` đặt gain (SFX chồng nhau tự hạ cả cụm để đỉnh cộng dồn vẫn trong −8…−12 dBFS); `$PY scripts/audio_levels.py stems SPEC.levels.craft.json OUT/` (stem xấp xỉ từ spec) rồi `$PY scripts/audio_levels.py check MIX.wav --stems OUT/` (thoát 1 sai, 2 chưa kiểm). LUFS / true peak lấy từ `mix.wav` thật của FilmCraft. Khi giọng và SFX đỉnh trùng lúc, tổng có thể vượt −1,5 dBTP → dời SFX vào khoảng ngừng lời.
- Nhạc nền: F5 (cắt trầm 100 Hz, −3 dB @ 2 kHz, fade 1,0 / 1,5 s, chạy suốt).
- SFX: F1 mở đầu, F2 không lặp take, F4 kho `sfx hmc` (`assets/motion-fx/sfx_catalog.json`, quy luật `kb-master-video-edit.md` › sfx-hmc.md). Kiểm: `$PY scripts/audit_sfx.py PROJECT.fcproj` → `repeated_takes = 0`.
- Lọc giọng mạnh / tách nhạc: `scripts/apps/dviet-viral-text-audio-edit/scripts/clean_and_master_voice.py`; thiết kế âm thanh nhiều rãnh: `kb-motion-sfx-audio-mastering.md`.

### 7. Thang kiểm trước khi giao (G5, H2)
Chi tiết nguyên văn: `references/rules-details.md` › SKILL §7.4 (ngưỡng khớp SFX: đỉnh ≤ 0,05 s so với khung mạnh nhất, không sớm hơn hình > 0,1 s).
Một video: §3 bước 11–18, đủ từng nấc; nấc không làm được ghi "chưa kiểm" và gọi sản phẩm là "bản nháp". Project mở được, không thiếu media (FilmCraft headless riêng trên màn hình ảo, không đụng cửa sổ người dùng).
Cả lô: `$PY scripts/media_reuse.py audit <thư mục>` (D8–D10); `$PY scripts/batch_report.py <lô>` (duyệt lần 2: PASS / WARN / HOLD — mở WARN / HOLD trước); `$PY scripts/rotation.py check <gốc lô>` (không lặp SFX mở đầu / kiểu chữ trong 5 video). Agent con báo "xong" chỉ là lời tự báo → tự chạy lại bước 16 và quét đường dẫn (G9).

### 8. Sửa theo góp ý (việc H)
Chi tiết nguyên văn: `references/rules-details.md` › SKILL §8. Áp lại nhịp dựng lên một timeline spec có sẵn: `$PY scripts/remix_rules.py` rồi dựng lại (mất chỗ người dùng đã sửa tay — chỉ dùng khi người dùng đồng ý).
Sửa đúng phần bị chê trên project đang mở (A3): sao lưu → `$PY scripts/fc_fast_patch.py` hoặc sửa spec + dựng lại chỉ khi người dùng chưa sửa tay (dựng lại làm mất chỉnh tay — so spec mới với bản cũ, khác biệt chỉ ở phần vừa sửa) → chạy lại mục 7 → mở lại cho người dùng. Ghi câu góp ý vào `FEEDBACK.jsonl` của dự án (H4).

### 9. Lô nhiều video (G7)
5 project / lượt → mở cho duyệt → chỉ xuất MP4 video được duyệt (tối đa 2 phiên xuất song song, đóng cửa sổ FilmCraft của project trước khi ghi đè / xuất, GPU bọc `flock /tmp/gpu.lock`) → đo `ffprobe` + `ebur128` → sang 5 tiếp. Mỗi agent con chỉ sửa 1 file project. Tra soát lô phông xanh theo G9.

### 10. Khi đầu vào thiếu hoặc sai
- Thiếu file nguồn / media: báo đúng tên file thiếu (đường dẫn đầy đủ), dừng phần cần file đó, làm tiếp phần không phụ thuộc (G3).
- Thiếu kịch bản / CTA / số liệu / tên riêng: không đoán; hỏi gộp một lần (B10, G3).
- Sai định dạng (ngang thay vì dọc, WebM alpha, 4K nặng, VFR): nêu định dạng nhận được và cần; tự chuyển bằng ffmpeg nếu không mất chất lượng (D6), còn lại hỏi.
- Không có khoá HeyGen: chạy thử, dừng trước bước tốn credit (G2). Một đường Google Flow lỗi (MCP hoặc trình duyệt Cindy): chuyển đường còn lại, hết cả hai thì xin ý kiến dùng Muse dự phòng khẩn (D3); thiếu tín dụng Flow / không có Muse thì báo và dừng. MCP `openchatcut` / `filmcraft` không kết nối: báo, không đổi sang công cụ khác khi người dùng đã chỉ định.
- Thiếu luật / số trong `rules.json`: dừng và báo, không dùng số đoán (H1).
- Người dùng nói khác `rules.json`: làm theo lời người dùng cho việc đó; luật lâu dài thì đề xuất cập nhật `rules.json` (H4).

### 11. Lỗi hay gặp
Chi tiết nguyên văn: `references/rules-details.md` › SKILL §11. Chia việc: mặc định tự làm; việc độc lập lớn (nhiều video / nhiều cảnh) mở agent con chạy nền, lệnh chạy lâu (whisper, render) chạy nền; đội OPA chỉ qua `kb-opa-delegate.md`.
| Dấu hiệu | Làm đúng |
|---|---|
| Dựng xong tự xuất MP4 | Không (A1); lưu project, mở cho duyệt |
| Áp style kênh tham khảo cho mọi video | Chỉ khi người dùng chọn (P1) |
| Chữ chạy qua điểm có chuyển cảnh | Kết thúc chữ đúng điểm cắt (FilmCraft đặt chuyển cảnh căn giữa điểm cắt) |
| ffmpeg thiếu `-y` | Luôn `-y` (thiếu vẫn thoát 0 mà không ghi) |
| Chạy render bằng `&` | Dùng chế độ chạy nền của công cụ |
| Phụ đề trắng chìm trên nền sáng | Bóng đậm `STRONG_SHADOW` / dời khung người (B8) — KHÔNG thêm dải tối dưới phụ đề (B15) |
| Chép `beats.py`, `qa_*.py` từ dự án trước | Import `scripts/build_kit.py`; chạy `scripts/qa_*.py` của skill |
| Mở quá nhiều FilmCraft | ≤ 3 cửa sổ duyệt + 1 headless (A2) |
| Áp luật dựng mới cho bản đang sửa / lô cũ | Giữ thông số của bản đó, chỉ đổi phần bị chê |
| Overlay light leak TNEDIT là video ngang | `leak_overlay` xoay 90°, phóng 177,8 %, blend Add (phóng phủ kín khung thì mất vệt sáng); overlay chuyển cảnh đặt ở làn `trans` dưới chữ |

## Format

**Bàn giao mỗi video** (tin nhắn cho người dùng):
1. Dòng đầu: kết quả — "Đã dựng xong và mở <tên>.fcproj để bạn duyệt" (hoặc "bản nháp" nếu còn nấc chưa kiểm).
2. Đường dẫn project (và MP4 chỉ khi đã duyệt + đã xuất).
3. Bảng kiểm: nấc | lệnh | kết quả số (vd `edit_rules 12/12 OK`, `spec_lint HARD 0 · SOFT 2`, `F3 giọng −4,1 dBFS · nhạc −17,3 LU · SFX −9,8 dBFS · −16,0 LUFS · TP −1,7 dBTP`); nấc chưa kiểm ghi "chưa kiểm".
4. Thay đổi chính; giả định đã đặt; lỗi còn lại kèm timestamp; điểm chờ người dùng quyết.

**File trong thư mục dự án**: `work/build_spec.py`, `<mã>.craft.json`, `<mã>.levels.craft.json`, `work/transition_plan.md`, `work/qa/` (khung kiểm, mix.wav, báo cáo JSON), `<mã>.fcproj`, `FEEDBACK.jsonl`, `APPROVALS.md`. Thư mục kịch bản theo mục 2. Sao lưu ngoài thư mục dự án.

**Báo cáo lô**: bảng `batch_report.py` (video | PASS/WARN/HOLD | lý do) + đường dẫn contact sheet.

## Examples

Mỗi ví dụ là các quyết định agent tự đưa ra theo tình huống — không phải chuỗi lệnh chạy tự động. Sau mỗi bước, xem kết quả rồi mới chọn bước tiếp; chỗ có ⏸ là DỪNG chờ người dùng.

**1. Dựng mới từ footage quay thật**
Người dùng: "Dựng video từ `C0048.MP4` theo kịch bản KB21.md, CTA 'Nhắn tin ngay', FilmCraft."
1. Xếp loại A; kiểm môi trường (`env_status.py`).
2. Xem khung đầu C0048: là phông xanh → cần nền (D12). Người dùng đã gửi ảnh phòng chưa? Chưa → ⏸ hỏi ảnh phòng (trong lúc chờ làm bước 4–5). Có → `studio_plate.py`, rồi `chroma_studio.py` từ file gốc ở tốc độ 1.0 (D11; tăng tốc làm sau khi cắt lặng).
3. Nếu là clip nền sáng thay vì phông xanh → `frame_person.py analyze` quyết định chỉ chỉnh khung hay không làm gì.
4. Còn ồn → `prep_video.py`; bóc lời trên media gốc (`transcribe.py`); cắt lặng + chọn tốc độ (`speed_media.py plan`, < 45 s giữ 1.0x) rồi mới `speed_media.py apply`; chữ lấy từ KB21.md (B10).
5. Lập bảng điểm cắt (C3) → ⏸ gửi bảng cho người dùng xem.
6. Viết `build_spec.py`; đặt mức (`audio_levels.py plan`); `spec_lint` — có HARD thì sửa spec, không dựng.
7. Dựng, chạy thang kiểm mục 7; nấc nào lỗi thì sửa nấc đó và kiểm lại.
8. Mở project cho người dùng (`open_in_app.py`), bàn giao theo Format → ⏸ chờ "DUYỆT" / góp ý. Không xuất MP4.

**2. Từ kịch bản chưa có video**
Người dùng: "Có 5 kịch bản trong SPEC-10-KICH-BAN-V5.md, làm A-roll B-roll."
1. Xếp loại Q; `analyze_and_scaffold.py from-spec` (0 credit), đọc báo cáo tỷ lệ A/B.
2. `rotation.py plan` cấp SFX mở đầu / kiểu chữ không lặp; `batch_plan.py` lập bảng → ⏸ người dùng duyệt lần 1 trước khi tốn credit.
3. `render-aroll` (mặc định chạy thử) → xem danh sách shot. Có khoá HeyGen trong chat? Chưa → ⏸ dừng ở chạy thử. Có → `render-aroll --yes`.
4. Prompt B-roll chưa đạt H5 (tiếng Việt, "Clip thư viện") → viết lại theo §2 bước 5b; `broll_fix.py plan --engine flow` → `lint` → `prepare --source flow` → `flow_inspect_account` kiểm số dư (thiếu → ⏸ báo, không tự mua) → tạo bằng Google Flow (D3, D15; phiên có `flow_*` → MCP qua `broll_fix.py mcp-jobs`, không thì trình duyệt Cindy; 2 bản → chọn bằng mắt → tải 1080p → `normalize` → `verify`); một đường hỏng → đường còn lại, cả hai hỏng → ⏸ xin đồng ý dùng Muse dự phòng.
5. `validate --check-media`: thiếu file → báo đúng tên, ⏸ không dựng (G3). Đủ → dựng từng video theo bảng mục 3; `scene_check` báo cảnh mượn kịch bản khác → tự tạo lại theo §2 bước 5b; mở 5 project cho duyệt.

**3. Sửa theo góp ý**
Người dùng: "Video KB06 giây 12 chữ đè mặt, SFX mở đầu nghe giống KB05."
1. Xếp loại H; sao lưu `KB06.fcproj` (A3).
2. Giây 12: từ khoá chạm mặt → đưa ra sau người (B9: `matte.py` + `behind_person`, phóng 1,45×, bỏ punch).
3. SFX mở đầu: chọn cặp chưa dùng trong 5 video gần nhất (F1, `rotation.json`).
4. Vá bằng `fc_fast_patch.py`; kiểm `qa_frames` giây 11–14 và `audit_sfx`.
5. Mở lại cửa sổ, ghi góp ý vào `FEEDBACK.jsonl` → ⏸ chờ duyệt.

**4. Thử hồ sơ @__dviet (A/B)**
Người dùng: "Dựng clip này kiểu dviet để so với bản thường."
1. Dựng 2 project từ cùng nguồn: bản mặc định (luật chung) và bản bật P1–P5 (3 font, trắng + 1 màu nhấn, punch 112–125 %, nhịp nhanh; vẫn giữ C1, B14, F3).
2. Mở cả hai cửa sổ cạnh nhau, liệt kê khác biệt → ⏸ người dùng chọn. Không đổi luật chung khi chưa có quyết định.
