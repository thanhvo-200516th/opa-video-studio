# Bộ luật opa-video-studio — toàn văn hiện hành

Sinh tự động từ `rules.json` (nguồn: `tools/rules_src.py`). Thứ tự ưu tiên: **lời người dùng trong chat > `rules.json` > `SKILL.md` > `references/kb-*.md`**. Luật `optional` chỉ áp khi người dùng chọn; luật `superseded` giữ để tra, KHÔNG áp. Nguyên văn gốc của mọi luật nằm trong `references/kb-*.md` (cột Nguồn gốc).

Cột Kiểm: tên lệnh trong `scripts/`; `mắt` = xem ảnh khung `qa_frames.py`; `tai` = nghe thử.

## A. Giao file

### A1 — Không xuất MP4 khi chưa có người duyệt

Không tự xuất MP4 sau khi dựng trên FilmCraft / EffectCraft / Premiere. Lưu project (`.fcproj`, `.ecproj`, `.prproj`) đủ track, clip, keyframe, mở phần mềm cho người dùng tự duyệt. **Chỉ xuất MP4 cho video người dùng đã nói DUYỆT** (hoặc khi người dùng yêu cầu rõ). Được render clip thành phần (VFX facecam, Remotion, EffectCraft, B-roll) để đưa vào timeline — đó không phải bản giao. Clip đo QA (`qa_sync`: 270×480 câm + wav SFX trong `work/qa/`, xoá sau khi đo) cũng không phải bản giao, được chạy trước duyệt `[cách hiểu, chờ người dùng xác nhận]`.

- Kiểm: mắt · Nguồn: người dùng 2026-11-13 (giữ A1, sửa G7) + rules.md mục 1 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md A1`, `kb-master-video-edit.md#rules.md mục 1`

### A2 — Nhiều video: mỗi video một cửa sổ, dựng song song

Nhiều video trong một yêu cầu: mỗi video một cửa sổ FilmCraft riêng, dựng song song; dựng xong mở tất cả: `python3 scripts/open_in_app.py a.fcproj b.fcproj c.fcproj`. Tối đa 3 cửa sổ duyệt + 1 FilmCraft headless cùng lúc (máy từng hết RAM 62 GB với ~10 instance, 2026-10-31); mở cửa sổ duyệt tách khỏi phiên agent: `systemd-run --user --collect --setenv=DISPLAY=:0 --setenv=XAUTHORITY=$HOME/.Xauthority filmcraft --no-recover --data-dir <dir> <proj>`. Trước khi mở bản mới: đóng cửa sổ duyệt BẢN CŨ của cùng project theo ngoại lệ (1) của A3; lệnh dựng / kiểm chạy lần lượt. Bị sập thì cứu chỉnh sửa của người dùng từ `Auto-Save/` và `<data-dir>/Recovery/*/snapshot.fcproj`.

- Kiểm: — · Nguồn: rules.md mục 1 (2026-10-31) + ghi nhớ filmcraft-ram-limit · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md A2`, `kb-master-video-edit.md#cindy-memories/project_filmcraft-ram-limit.md`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục A2

### A3 — Sửa thẳng trên project cũ, sao lưu trước

Sửa video đã có project: sửa thẳng trên project đó, không tạo `.fcproj` / `.ecproj` hay bản `_V0n` mới (chỉ tạo mới khi dựng lần đầu hoặc người dùng bảo). Trước khi lưu đè, chép bản hiện tại vào `~/.cache/opa-video-studio/backup/<tên>-<yyyymmdd-hhmm>.<đuôi>` (ngoài thư mục project; bản dự phòng, không phải bản giao). Người dùng dặn không lưu thì để thay đổi trong cửa sổ cho họ tự lưu. EffectCraft mở kèm `--control`: gắn vào đúng cửa sổ qua cổng của tiến trình, token đọc từ `/proc/<pid>/environ`; MCP `effectcraft`/`filmcraft` luôn mở cửa sổ mới nên không dùng để sửa project đang mở. FilmCraft mở bằng `open_in_app.py` không có cổng điều khiển: sửa thẳng file `.fcproj` (ưu tiên `scripts/fc_fast_patch.py`), rồi mở lại cho người dùng xem; cửa sổ cũ còn thay đổi chưa lưu thì hỏi trước. Không mở hay đóng project khác trong cửa sổ đó. KHÔNG tự đóng cửa sổ người dùng đang mở, trừ 2 ngoại lệ có điều kiện: (1) cửa sổ duyệt bản cũ của cùng project mà agent đã mở (A2) — chỉ đóng sau khi kiểm không còn chỉnh sửa chưa lưu; (2) trước khi ghi đè file project hoặc xuất (G7) — FilmCraft của project đó phải đóng: còn chỉnh sửa chưa lưu, hoặc là cửa sổ người dùng tự mở, thì HỎI người dùng trước, không tự đóng.

- Kiểm: — · Nguồn: rules.md mục 1 (2026-10-31) · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md A3`, `kb-master-video-edit.md#rules.md mục 1`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục A3

### A4 — Không đăng, không đưa nguồn ra ngoài, không ghi khoá

Không publish / đăng mạng xã hội, không đưa nguồn lên host ngoài, không upgrade CLI tự ý; khoá API không bao giờ ghi vào project, prompt, báo cáo. Không sửa file gốc hay thư mục dựng của dự án khác.

- Kiểm: — · Nguồn: rules.md mục 4 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md A4`, `kb-master-video-edit.md#rules.md mục 4`

### A5 — Xoá metadata trước khi giao

Ảnh / clip giao đi: xoá metadata lộ nguồn (EXIF, XMP, IPTC, C2PA, prompt AI, GPS) theo `references/kb-strip-media-metadata.md` (công cụ ở `scripts/apps/strip-media-metadata/`), trừ khi người dùng muốn giữ.

- Kiểm: — · Nguồn: rules.md mục 1 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md A5`

### A6 — Ảnh bìa chỉ 0,2–0,3 s đầu

Ảnh bìa (thumbnail) chỉ 0,2–0,3 s đầu video: hiện đủ tới 0,2 s, mờ hết trước 0,3 s (để 1 s che mất nội dung mở đầu). Luật giới hạn thời lượng, KHÔNG bắt buộc có bìa: mặc định không làm; người dùng yêu cầu thì `MotionFX.cover(png)`.

- Kiểm: edit_rules · Nguồn: người dùng 2026-11-11 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md A6`

### A7 — Nơi để bản đã duyệt

Bản người dùng đã duyệt để ở `/home/vmiz/Thanh/Media/TNEDIT/09_Du_An/ Video Final/` (tên thư mục BẮT ĐẦU BẰNG DẤU CÁCH, giữ nguyên).

- Kiểm: — · Nguồn: rules.md mục 1 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#rules.md mục 1`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục A7

## B. Chữ

### B1 — 4–6 font mỗi video, đủ dấu

Mỗi video dùng 4–6 font family (đếm trong spec), font phải đủ dấu tiếng Việt. Dưới 4 là đơn điệu, trên 6 là rối. Phụ đề đổi font theo đoạn (`CAPTION_STYLE_ROTATION`) + chữ chính + chữ viết tay mảnh là đủ; không thêm font chỉ để đủ số. Montserrat bản variable bị FilmCraft đọc thành "Thin" → dùng bản tĩnh `~/.local/share/fonts/Montserrat_Static/` (vd `Montserrat-Black.otf`).

- Kiểm: edit_rules · Nguồn: người dùng 2026-11-06 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md B1`, `kb-master-video-edit.md#rules.md mục 2`

### B2 — Không viền, nổi bằng bóng đen mềm

Yếu tố tiên quyết: chữ KHÔNG viền (stroke). Nổi bằng bóng đen mềm lệch dưới-phải (kiểu @magentx.ai). Chữ chính: lệch 4–6 px, nhoè 10–14 px, đậm 75–90 %, thêm độ lan khi nền sáng. Chữ phụ (từ dẫn, nhãn): `MX_SHADOW` đậm 55 % / nhoè 8 / lệch 3 / 135°; viết tay: `SCRIPT_SHADOW` 55 / 7 / 3; phụ đề: `CAP_SHADOW` 75 / nhoè 10 / lệch 3 / lan 2 (đậm hơn để đủ tương phản). PNG từ khoá có bóng sẵn (`fx_gfx.gradient_text`). Màu nhấn dùng bản bão hoà, không pastel.

- Kiểm: mắt · Nguồn: người dùng 2026-11-04 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md B2`, `kb-master-video-edit.md#cindy-memories/feedback_text-no-stroke-black-shadow.md`

### B3 — Chữ chính nhiều màu, luôn phát sáng, 10–15 kiểu vào

Chữ chính (từ khoá, câu chốt, chữ viết tay to) nhiều màu (vàng, xanh lam, đỏ, tím, xanh dương, xanh ngọc, trắng), luôn phát sáng cùng màu: vàng / trắng phát sáng siêu nhẹ (`GLOW["soft"]`), màu khác phát sáng rõ (`GLOW["normal"]`); KHÔNG dùng hồng, cam, xanh lá — nếu BUỘC dùng thì chữ đó phải phát sáng (`GLOW_REQUIRED`); xanh lam / xanh dương dùng hạn chế. Bán kính / độ đậm phát sáng: `GLOW["soft"]` 12 px, 55 → 20; `GLOW["normal"]` 20 px, 170 → 70. Luôn có điểm nhấn: kiểu vào mạnh (đập vào, nở ra, nhấp nháy, nảy, bay vào…) hoặc đổ bóng. Mỗi video 10–15 kiểu vào chọn theo tên video từ `KEY_POOL` 17 kiểu (slam · burst · flicker · pop · glow_in · fly · drop · slide_up · slide_down · type · grey · blur · nudge · dreamy · wipe · flip3d · swing_in) + 24 hiệu ứng chữ (`MotionFX(name=…, key_seed=…)`), xoay vòng, không lặp một kiểu hai lần liền; `flip3d`, `swing_in` là 3D, tính vào C5. Cụm nhấn dùng font khác font thân, kèm hiệu ứng có nghĩa; các mục song song xử lý như nhau.

- Kiểm: edit_rules · Nguồn: người dùng 2026-11-04..06 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md B3`, `kb-master-video-edit.md#rules.md mục 2`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục B3

### B4 — Chữ phụ không cam / hồng / tím / đỏ; sáng, tương phản ≥ 4,5:1

Chữ phụ (phụ đề, nhãn, từ dẫn, chữ viết tay nhỏ) không dùng cam, hồng, tím, đỏ; buộc dùng cam / hồng / tím thì phát sáng nhẹ (`CAP_GLOW_REQUIRED`, `key_glow(soft=True)`). Màu sáng (độ chói ≥ 0,45) — đỏ, xanh dương đậm, tím đậm chìm trên áo / B-roll (đo THCN 07: đỏ 3,0:1) nên chỉ cho chữ chính. Tương phản với nền ≥ 4,5:1 — vì không còn dải tối dưới phụ đề (B15), đạt bằng bóng đậm (`CAP_SHADOW`, `STRONG_SHADOW` khi nền sáng) và chỉnh khung A-roll; vẫn không đạt thì ghi vào bàn giao. Nhãn / từ dẫn / viết tay nhỏ chỉ đổ bóng nhẹ; phụ đề dùng `CAP_SHADOW` đậm hơn (B2).

- Kiểm: edit_rules + mắt · Nguồn: người dùng 2026-11-05..06 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md B4`, `kb-master-video-edit.md#rules.md mục 2`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục B4

### B5 — Phụ đề 2 dòng: trắng + màu đổi mỗi cụm

Phụ đề: dòng 1 trắng nét to; dòng 2 đổi màu MỖI CỤM theo `CAPTION_ROTATION` (xanh ngọc · vàng · xanh lam · xanh da trời). Dòng 2 chỉ hiện khi bắt đầu được nói tới. Mọi dòng màu dùng bóng đậm `CAP_SCRIPT_SHADOW`.

- Kiểm: mắt · Nguồn: người dùng 2026-11-05 lần 12, 17 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md B5`, `kb-master-video-edit.md#rules.md mục 2`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục B5

### B6 — 6 kiểu vào chữ phụ đã duyệt

Kiểu vào chữ phụ (duyệt lần 18): gõ từng ký tự · phát sáng dâng lên · blur-in · nhấp nháy DỊU và ÍT (1 lần / 11 cụm, chỉ chùng 60 % một khung — bản tắt bật mạnh bị chê chói) · đổi font liên tục · hiện từng chữ khớp lời (`CAP_ENTRANCES`). Bộ lần 15 (từng từ nảy + click, khung chọn, quét lộ, viết tay thay nhau) vẫn gọi được; 7 kiểu mạnh (đập vào, loé sáng…) KHÔNG dùng cho chữ phụ. Nhãn, từ dẫn: gõ / phát sáng dâng / blur (không nhấp nháy). Không lặp một kiểu hai lần liền.

- Kiểm: mắt · Nguồn: người dùng 2026-11-05 lần 12–18 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md B6`, `kb-master-video-edit.md#cindy-memories/feedback_text-entrance-color-voice-rules.md`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục B6

### B7 — Chữ viết tay mảnh và ít; font phụ đề phân tầng theo đoạn

Font phụ đề phân tầng theo đoạn (mẫu @prodby.viet): mỗi đoạn 3–5 cụm một kiểu — Montserrat + viết tay MẢNH (TF Whispers) · toàn Montserrat · Be Vietnam Pro · SF Pro Light — xoay vòng. Trong 3–5 nhịp tối đa 3–4 chữ viết tay (đoạn viết tay ≤ 3 cụm phụ đề + chữ viết tay của từ khoá). Code: `CAPTION_STYLES`, `CAPTION_STYLE_ROTATION` (`scripts/motion_fx.py`).

- Kiểm: mắt · Nguồn: người dùng 2026-11-04 lần 11 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md B7`, `kb-master-video-edit.md#cindy-memories/feedback_text-colors-and-sfx-sync.md`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục B7

### B8 — Hai vùng chữ

Khung trên x 140–940, y 240–680: từ khoá, tiêu đề nổi; baseline dòng đầu y ≈ 500 (`FX(key_y=500)`). Khung dưới x 140–920, y 1290–1480: thoại, phụ đề; baseline y ≈ 1400–1440 (`FX(cap_y=1400)`). Rộng ≤ 800 px căn giữa x 540 (tránh cột icon TikTok x > 950 và phần tên/mô tả y > 1500). Chữ nhỏ nhất 28 px trên khung 1080. Chỉ đặt chữ ngoài 2 khung khi hiệu ứng cần (chữ sau đầu, chữ gắn tường, CTA giữa màn hình) và ghi lý do trong spec. Mặt lọt vào khung: chỉnh scale / vị trí A-roll cho mặt nằm y ≈ 700–1280, không dời chữ. Các khối thẳng một cột.

- Kiểm: mắt · Nguồn: người dùng 2026-11-03 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md B8`, `kb-master-video-edit.md#rules.md mục 2`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục B8

### B9 — Phân tầng; không đè mặt; chữ chạm mặt ra sau người

Tối đa 1 tầng chính + 2 tầng phụ cùng lúc. Chữ không đè mặt. Từ khoá chạm vùng đầu / mặt (không nằm trên B-roll): dò mặt (Haar) + tách nền người (`scripts/matte.py`), phóng ~1,45×, đáy chữ thấp hơn đỉnh đầu thật (đo từ alpha) ~0,18 cỡ để tóc che ~25 % chân chữ, ẩn chỗ có người bằng Track Matte đảo (`fx.behind_person`): lớp người là track V2 ngay trên V1, dưới dải tối; `matte_in` khớp đoạn nguồn và chép cùng `motion` (push-in) của A-roll sang lớp người. Đoạn đó giữ cỡ khung thường (không punch); bỏ dòng viết tay rơi vào mặt. Từ khoá trên B-roll giữ phía trước. Kiểm bằng ảnh khung.

- Kiểm: mắt · Nguồn: người dùng 2026-11-05 lần 19 + duyệt V07 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md B9`, `kb-master-video-edit.md#cindy-memories/feedback_key-text-behind-face.md`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục B9

### B10 — Chữ lấy từ kịch bản; viết hoa đầu dòng; dấu không đè

Viết hoa chữ cái đầu mọi dòng hiển thị (kể cả dòng bắt đầu bằng số); tên file hiện trên hình giữ chữ thường. Có kịch bản gốc thì chữ lấy từ kịch bản; Whisper chỉ để căn giờ. Không đoán tên riêng, số liệu, CTA. Dòng phụ không đè dấu thanh dòng chính; giãn dòng ≥ 1,28 × cỡ chữ khi có dấu chồng — TRỪ khi dòng 2 là chữ viết tay: không giãn 1,28× (khối sẽ rơi khỏi vùng phụ đề tới y ≈ 1580), đặt sát dưới dòng 1 theo nét thật (`ink_top` dòng 2 + `mark_below` dòng 1), cả khối nâng 0,45× cỡ.

- Kiểm: mắt · Nguồn: rules.md mục 2 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md B10`, `kb-master-video-edit.md#rules.md mục 2`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục B10

### B11 — Chữ khớp giọng; nhịp chậm; ra bằng mờ dần

Căn mốc từng từ bằng `build_kit.refine_words` trước khi dựng (Whisper turbo đặt từ đầu sau lặng sớm 0,18–0,29 s); phụ đề gõ / khung chọn / quét lộ / từng chữ chạy THEO MỐC LỜI. Nhịp chậm: phụ đề ~7 ký tự/s, từ khoá ~6 ký tự/s. Không dùng kiểu "chạy ra rồi thu vào" (gõ rồi xoá ngược): chữ ra bằng soft_out của B14 (mờ + nhoè 0,13 s; thay "mờ dần 8 khung" cũ). Kiểm bằng ảnh khung ngay sau mốc từng từ.

- Kiểm: mắt · Nguồn: người dùng 2026-11-05 lần 16 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md B11`, `kb-master-video-edit.md#rules.md mục 2`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục B11

### B12 — Dải tối mép trên = Color Matte + mask

Dải tối mép trên (làm nổi chữ chính) = Color Matte đen + mask chữ nhật phủ mép trên: Mask Feather 868,8 · Mask Opacity 59,2 % · Mask Expansion 213,1 · Opacity 100 % · Normal (`scripts/fc_matte_band.py`; mở cho người dùng bằng `open_in_app.py --select "Dải tối trên · Color Matte"`). Khi người dùng gửi ảnh Effect Controls làm mẫu, lấy đúng số trong ảnh.

- Kiểm: mắt · Nguồn: người dùng làm mẫu 2026-11-05 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md B12`, `kb-master-video-edit.md#cindy-memories/feedback_top-band-color-matte-mask.md`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục B12

### B13 — Chữ trên hình không có dấu phẩy

Chữ hiện trên hình (phụ đề, từ khoá, nhãn) không có dấu phẩy `,`; dấu phẩy thập phân giữa hai số (2,5) giữ nguyên. `text_fx.nfc` tự loại. Chỉ áp cho video dựng từ 2026-11-10; project cũ không sửa.

- Kiểm: edit_rules · Nguồn: người dùng 2026-11-10 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md B13`

### B14 — Chữ không tĩnh: vào · giữ · ra đều chuyển động

Mọi lớp chữ có VÀO · GIỮ · RA chuyển động (đo từ @__dviet, `kb-master-video-edit.md` › dviet-text-motion-2026-11-11.md). Vào mặc định soft_in (mờ nhoè → nét, KHÔNG nảy): chữ chính 0,29 s (opacity 0/15/65/88/100 %, blur 22/9/3/0), phụ đề 0,17 s; giữ: phóng chậm 100 → 103 % (chữ chính) / 101,5 % (phụ đề); ra soft_out 0,13 s (mờ + blur 12). Kiểu vào riêng (slam, type, glow_in…) giữ nguyên. Chữ hiện sớm hơn lời 0–80 ms. `MotionFX.tracks()` tự áp (`text_motion.ensure_motion`); bỏ qua clip chữ < 0,3 s. Bộ kiểm: 0 lớp thiếu kiểu vào, ≤ 5 % đứng yên lúc giữ.

- Kiểm: edit_rules · Nguồn: người dùng 2026-11-11 (Rule 4) · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md B14`

### B15 — Không dải tối dưới phụ đề

Không đặt dải tối / vignette sau vùng phụ đề (`MotionFX.caption_band` tắt mặc định, `ALLOW_CAPTION_BAND = False`); phụ đề nổi bằng bóng đen mềm (B2). Dải tối mép TRÊN cho chữ chính (B12) giữ nguyên. Thay luật cũ "dải tối mềm ~50 % sau phụ đề".

- Kiểm: edit_rules · Nguồn: người dùng 2026-11-11 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md B15`

### B16 — Mốc chữ theo giọng thật

Mốc từng từ theo GIỌNG THẬT. Transcript giọng B-roll HeyGen bị dồn mốc (14–18 chữ bật cùng lúc) → `scripts/retime_voice.py` cho Whisper nghe lại, giữ chữ kịch bản, ghép mốc thật. `spec_lint` chặn HARD `text_voice_burst` (≥ 6 từ trong 0,3 s).

- Kiểm: spec_lint · Nguồn: người dùng 2026-11-11 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md B16`

## C. Chuyển cảnh và zoom

### C1 — Mọi điểm cắt có chuyển cảnh

Mọi chỗ nối hai clip (A-roll với A-roll, A-roll với B-roll) đều có hiệu ứng chuyển cảnh (danh sách ở kb-master-video-edit › filmcraft-effects.md). Chữ kết thúc đúng điểm cắt. Áp cả khi dùng hồ sơ @__dviet (thay "cắt thẳng là chính").

- Kiểm: edit_rules · Nguồn: người dùng 2026-10-31 (rules.md mục 7) · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md C1`, `kb-master-video-edit.md#rules.md mục 7`

### C2 — Chuyển cảnh đa dạng theo ngữ cảnh

`cut_plan` chọn theo ngữ cảnh điểm cắt (câu mới · đổi phần · đổi cảnh · đổi góc gần · ra B-roll, `cut_plan.OPTIONS`), lấy kiểu ít dùng nhất, không lặp trong 4 điểm cắt; ≥ 6 kiểu mỗi video; họ nháy sáng (`flash_burst`, `flash_shake`, `shutter`, `flicker`) — bộ lập kế hoạch nhắm ≤ 20 % điểm cắt và cách nhau ≥ 3 điểm cắt; máy chấm cho tới 25 % (dư cho flash khi vào B-roll, `edit_rules.MAX_FLASHY_SHARE`). Mỗi video lệch thứ tự theo `rotation.json`. Ưu tiên kiểu dựng bằng keyframe (`zoom_through`, `panel_wipe`, `split_slide`) và kiểu ghép (`flash_shake`, `rgb_glitch`, `spin_zoom`, `light_sweep`, `slice`, `spring`, `spin`, `travel`, `glass`, `liquid`) bên cạnh overlay TNEDIT. Thay luật "≥ 40 % họ flash" (2026-11-06).

- Kiểm: edit_rules · Nguồn: người dùng 2026-11-11 (Rule 2) · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md C2`, `kb-master-video-edit.md#rules.md mục 7`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục C2

### C3 — Lập bảng điểm cắt trước khi dựng

Chạy `scripts/cut_plan.py` trước, đưa bảng điểm cắt → loại → chuyển cảnh → SFX → lý do cho người dùng. Jump cut cùng khung không dùng dải dọc / ô lưới. Flash FilmCraft không đặt dưới dải tối (thành vệt xám).

- Kiểm: — · Nguồn: người dùng 2026-11-04 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md C3`, `kb-master-video-edit.md#cindy-memories/feedback_analyze-cuts-before-transitions.md`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục C3

### C4 — Zoom động cho đoạn nói dài; punch che jump cut

Đoạn người nói liền ≥ 4 s `[đề xuất]` có zoom động in/out chậm luân phiên (`edit_rules.zoom_keys`), không để khung đứng yên. Jump cut giữa câu: punch 100 ↔ 112 % + zoom blur.

- Kiểm: edit_rules · Nguồn: người dùng 2026-11-06 · Độ tin: medium
- Nguồn gốc: `kb-master-video-edit.md#style.md C4`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục C4

### C5 — 3D chỉ 3–4 lần mỗi video

Hiệu ứng 3D (xoay, lật, nghiêng phối cảnh) cho chữ hoặc B-roll lúc xuất hiện: tính chung 3–4 lần mỗi video; còn lại dùng hiệu ứng phẳng. Tính là 1 lần 3D: `swing3d`, `ui_card(threed=True)`, `flip3d_in`, `wall_text`, `roll_3d`, kiểu chữ chính `flip3d` và `swing_in`.

- Kiểm: — · Nguồn: người dùng 2026-10-31 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md C5`, `kb-master-video-edit.md#rules.md mục 7`

### C6 — SFX chuyển cảnh trúng khung đổi mạnh nhất

Đỉnh tiếng SFX chuyển cảnh rơi vào đúng khung đổi hình mạnh nhất, không vào trước hình; kiểm trên bản xuất bằng `scripts/qa_sync.py` (đỉnh ≤ 0,05 s so với khung mạnh nhất). File SFX dùng cho chuyển cảnh phải to nhất ngay đầu (đỉnh cách đầu file ≤ 0,06 s) — file đỉnh trễ (vd glitch "stutter" 0,19 s) sẽ vang sau hình.

- Kiểm: qa_sync · Nguồn: người dùng 2026-11-04 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md C6`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục C6

## D. Cảnh chèn, nguồn hình, tốc độ, chất lượng

### D1 — Cảnh chèn dày

B-roll + footage ≥ 25 % thời lượng `[đề xuất]`; người nói trơ một mình ≤ 8 s `[đề xuất]`. Thiếu cảnh chèn hợp lệ (D9 chặn cảnh mượn): 1) dùng B-roll đúng cảnh trong thư mục đánh số; 2) không có thì tạo cảnh chèn mặc định bằng Google Flow MCP từ chính lời đang nói (D3, D15, quy trình `broll_fix.py`, D9; chỉ dùng footage thật / stock trong trần ngoại lệ 2–5 % của D15, hoặc Muse dự phòng khi Flow hỏng và người dùng đồng ý), đặt câm và chỉ trong lúc lời đó chạy; 3) Google Flow (và dự phòng hợp lệ nếu có) không sẵn sàng (D3) thì chấp nhận CẢNH BÁO và ghi vào bàn giao.

- Kiểm: edit_rules · Nguồn: người dùng 2026-11-06 (số do skill đề xuất); cập nhật engine mặc định 2026-11-16 · Độ tin: medium
- Nguồn gốc: `kb-master-video-edit.md#style.md D1`

### D2 — B-roll không giọng, không chữ

B-roll không voice, không chữ (`no_voice`, `no_text`); tắt tiếng clip, scale 1080×1920; tên clip bắt đầu `B-roll` hoặc `Footage`. Prompt B-roll: xem H5.

- Kiểm: analyze_and_scaffold.py validate · Nguồn: quy trình 10 bước 2026-11-06 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md D2`

### D3 — Google Flow MCP mặc định tạo B-roll (D15); trình duyệt Cindy phụ, Muse dự phòng khẩn; không mua thêm

Google Flow (`labs.google/fx/tools/flow`) qua MCP `google-flow` là **công cụ tạo B-roll mặc định chính** (D15: mục tiêu 100 %, tối thiểu ≥ 95 %): `flow_list_accounts` → `flow_inspect_account` (báo tên tài khoản và số dư tín dụng trước khi tạo) → `flow_generate_video` → `flow_job_status` → chọn bản bằng mắt → `flow_upscale_video` 1080p → `flow_download_job`. Nếu MCP `google-flow` lỗi / chưa kết nối được thì chuyển sang **kênh phụ là trình duyệt Cindy** (`mcp__cindy_browser`) với tài khoản Google người dùng đã đăng nhập — dùng tín dụng có sẵn trong gói, KHÔNG tự mua thêm, không bật dùng thử, không tự nhập mật khẩu (gặp trang đăng nhập → nhờ người dùng đăng nhập). **Muse local** (`scripts/broll_fix.py ready` + `render_muse_broll.py`) chỉ là **dự phòng khẩn cấp** khi cả Google Flow MCP lẫn trình duyệt Cindy đều không khả dụng VÀ người dùng đồng ý. Không có cả Google Flow lẫn Muse (có đồng ý): báo người dùng, dừng bước tạo B-roll; không chuyển sang dịch vụ trả phí khác. Làm đúng `references/flow-broll.md`: `scripts/broll_fix.py plan --engine flow` (giây + tín dụng) → `lint` → `prepare --source flow` → Flow: Video, `9:16`, **Omni 1.2 Flash** (`model: "omni-flash"`), 720p, độ dài ⌈giọng + 0,3 s⌉ (3–15 s), **`outputs: 2`** mỗi cảnh (người dùng 2026-11-14), gõ đúng `prompt_core` không thêm câu cấm → chọn bản 720p theo bảng kiểm bằng mắt (không chữ / logo, màn hình không lộ nội dung, người nói không lộ mặt, một cảnh liền, đúng `anchor_quote`) → nâng & tải **«1080p Đã tăng độ phân giải»** (`flow_upscale_video` 1080p + `flow_download_job` khi dùng MCP; miễn phí ≤ 10 s) → `scripts/broll_fix.py normalize <file> <NN_b-roll-M.mp4> --mark flow` (1080×1920, 30 fps, không tiếng; `--mark flow` chỉ khi bản tải về có dấu ngôi sao — tài khoản PRO ở Việt Nam bị khoá bật, ULTRA tắt được) → `verify`. Không đính ảnh khuôn mặt người nói vào Flow (Thành phần / Khung hình) khi người dùng chưa đồng ý riêng cho video đó (A4).

- Kiểm: — · Nguồn: người dùng 2026-11-13..16 (2026-11-16 chốt Google Flow MCP mặc định thay Muse; 2026-11-14: 1080p, x2, Omni 1.2 Flash) · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md D3`

### D4 — Tốc độ 1.10x / 1.05x / 1.0x; video < 45 s không tăng tốc

Chỉ tăng `1.10x` hoặc `1.05x` — BỎ HẲN `1.15x`, `1.25x`, `1.35x`, `1.5x`. Video < 45 s KHÔNG tăng tốc (1.0x). Chọn `1.10x` nếu sau khi tăng video vẫn ≥ 45 s; không thì `1.05x` nếu vẫn ≥ 45 s; không thì `1.0x` — tăng tốc không bao giờ đẩy video xuống dưới 45 s. THỨ TỰ (người dùng 2026-11-13): cắt HẾT khoảng lặng trước, tăng tốc sau — `scripts/speed_media.py plan` cắt lặng trên media GỐC, cộng tổng giây giữ lại, gọi `build_kit.choose_speed` → `media/speed_plan.json`; rồi `scripts/speed_media.py apply` mới tăng tốc; điểm cắt trên timeline = điểm cắt gốc ÷ tốc độ (`build_kit.at_speed`), không mã hoá lại lần hai. Áp cho MỌI nguồn hình của video: HeyGen, Muse, B-roll, cảnh quay thật / phông xanh (`scripts/chroma_studio.py` mặc định 1.0, chặn tốc độ ngoài 1.0 / 1.05 / 1.10). Hình và giọng của cùng cảnh tăng cùng một mức (`setpts=PTS/<tốc độ>`, `atempo=<tốc độ>` giữ cao độ) để giữ D14. Media tăng tốc ở `media/x110/` · `media/x105/`; `spec_lint` chặn HARD spec còn dùng `x125` hoặc `x115`.

- Kiểm: spec_lint · Nguồn: người dùng 2026-11-13 (thay Rule 1 2026-11-11) · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md D4`, `kb-master-video-edit.md#rules.md mục 7`

### D5 — Kho tài nguyên trám cảnh (giới hạn ngoại lệ D15 ≤ 5 %)

Áp dụng trong trần ngoại lệ **D15** (footage thật / stock tối đa **2–5 %**, trần cứng **≤ 5 %** tổng thời lượng B-roll — ưu tiên tạo B-roll độc bản bằng Google Flow MCP theo D3, cấm lấy stock thay thế B-roll Flow): khi cần footage thật trong phần ngoại lệ đó, lấy thêm cảnh chèn từ `/home/vmiz/Thanh/Media/A huy/Source/soucre thô` (cảnh quay thật Anh Huy; bản gốc ghi thiếu `Source/`, sửa 2026-11-13), `/home/vmiz/Thanh/Media/A huy/B-roll` và `/home/vmiz/Thanh/Media/TNEDIT` (`04_Footage`, `06_B-Roll`). Mọi cảnh lấy từ kho phải minh hoạ đúng lời cảnh đó (D9) và tuân giới hạn lặp D8 (≤ 2 lần / video, ≤ 2 video). Clip phông xanh: không để lộ vải phông; cách tách theo D11, nền theo D12 (thay cách cũ `rvm-matte` + `despill`).

- Kiểm: mắt · Nguồn: người dùng 2026-11-09; cách tách sửa bởi D11–D12; giới hạn ngoại lệ bởi D15 (2026-11-16) · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md D5`, `kb-master-video-edit.md#rules.md mục 7`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục D5

### D6 — Chất lượng vào / ra

Giữ nguyên độ phân giải gốc (không scale khi chỉ đổi tốc độ / cắt); mã hoá trung gian `build_kit.X264_HQ` (x264 CRF 12, preset slow, High, BT.709) + `AAC_HQ` 320 kbps 48 kHz; nguồn Muse / B-roll CRF 12 slow; MP4 giao (khi đã duyệt, A1) CRF 14; không render lại media chỉ để đổi định dạng; nguồn thấp hơn khung dựng → `spec_lint` SOFT `low_res_source`, tạo lại nguồn 1080×1920.

- Kiểm: spec_lint · Nguồn: người dùng 2026-11-11 (Rule 3) · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md D6`

### D7 — Clip quay thật nền sáng: người ở 2/3 dưới khung

Chỉ áp cho clip QUAY THẬT nền sáng (`live_shoot`) — KHÔNG áp avatar HeyGen (giữ nền và khung gốc): đỉnh đầu ngang đường 1/3 trên (y ≈ 640 ± 60), 1/3 trên trống cho chữ chính; nền đã sáng chỉ chỉnh khung (phóng ≤ 1,35×; cần phóng hơn thì tách người + ghép nền theo D12), clip quay xoay ngang tự xoay đúng (`scripts/frame_person.py` analyze / fix), áp TRƯỚC bước tăng tốc; video giữ 1.0x chỉ cảnh báo. Clip phông xanh dùng D11 + D12 thay cho phần "ghép phòng làm việc sáng" của luật này.

- Kiểm: frame_person · Nguồn: người dùng 2026-11-11 (Rule 5); phần phông xanh thay bởi D12 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md D7`

### D8 — B-roll lặp giới hạn: ≤ 2 lần / video, ≤ 2 video

Mỗi cảnh / clip B-roll được dùng tối đa **2 lần trong 1 video** và tối đa **2 video khác nhau** (tổng cộng). Đo bằng vân tay hình (bắt cả bản mã hoá lại / tăng tốc): `scripts/media_reuse.py audit` + `scripts/edit_rules.py`; bảng lô báo WARN/HOLD khi vượt ngưỡng. Số trong `rules.json › params.broll`.

- Kiểm: media_reuse + edit_rules · Nguồn: người dùng 2026-11-16 (thay D8 cũ 2026-11-11 ≤ 1 lần / video) · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md D8`

### D9 — Cảnh chèn và B-roll bám sát kịch bản

Kịch bản nói gì thì cảnh chèn / B-roll / footage chiếu đúng điều đó theo nghĩa đen đời thực — mọi cảnh chèn (kể cả cảnh quay thật, cảnh lấy từ kho D5 trong trần ngoại lệ ≤ 5 % của D15) minh hoạ đúng lời đang nói ở cảnh đó, không cảnh "cho đẹp" lệch nội dung và CẤM ẩn dụ CGI trừu tượng xa rời câu thoại (như khối lập phương phát sáng, lăng kính, bánh răng, thanh ray thép trượt hộp đèn, lõi năng lượng, các nút trôi nổi). Trước khi tạo B-roll phải đi qua Quy trình 3 Agent: Agent 1 (Script Semantic Analyst) đọc trọn `tts_text` của video, tách các đoạn dài > 7,5 s hoặc chứa 2 vế đối lập thành sub-beats rõ ràng và viết `script_beat_vi` (cảnh người & đồ vật đời thực cụ thể chứng minh câu nói); Agent 2 viết `layers` 5 tầng chống nhựa thành `prompt` H5; Agent 3 kiểm `lint` + đối chiếu trực quan 2 bản 720p (`qa/broll_check_sheet.jpg`) loại ngay bản lệch `anchor_quote` hoặc có dấu hiệu nhựa/AI. Chỉ dùng cảnh tạo cho CHÍNH kịch bản đó (tên thư viện `KBxx_Byy` trùng mã video); cấm cảnh của kịch bản khác (lỗi cũ: OPA01–05 dùng 25 cảnh của KB01–KB10); prompt B-roll tạo từ lời từng cảnh (H5) và không được để trống; giọng dưới cảnh phải đúng lời kịch bản của cảnh (bản bóc lời giống `tts_text` ≥ 80 %). Kiểm: `scripts/scene_check.py --manifest … --spec … --words words_tl.json --transcripts … --review scene_review.md` (FAIL = sửa trước khi mở duyệt) + người duyệt xem bảng `scene_review.md` (lời ↔ prompt ↔ cảnh); bảng lô `media_reuse` báo HOLD khi dùng cảnh kịch bản khác. `scene_check` FAIL `script_source` / `broll_h5` → TỰ tạo lại cảnh đó mặc định qua **Google Flow MCP** (D3, D15) từ lời của chính cảnh (người dùng 2026-11-13, cập nhật engine & quy trình 3 Agent 2026-11-16, không cần hỏi lại nếu đủ tín dụng trong gói), mỗi bước một lệnh riêng: `broll_fix.py plan --engine flow` → quy trình 3 Agent viết `layers` + prompt H5 → `broll_fix.py lint` → `broll_fix.py prepare --source flow` (sao lưu bản cũ, cập nhật prompts + manifest) → MCP `google-flow` (D3: 720p `outputs: 2` → Agent 3 xem chọn → 1080p → download) → `broll_fix.py normalize` → `broll_fix.py verify` (xem ảnh kiểm) → `scene_check` lại (chỉ dùng Muse dự phòng khi Flow hỏng và người dùng đồng ý theo D3). Mỗi cảnh thử lại tối đa 1 lần; làm TRƯỚC bước tăng tốc (sau thì tăng tốc lại riêng file đó).

- Kiểm: scene_check + media_reuse + mắt · Nguồn: người dùng 2026-11-11; mở rộng cho mọi cảnh chèn 2026-11-13; cập nhật engine mặc định Google Flow MCP & quy trình 3 Agent chống ẩn dụ CGI 2026-11-16 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md D9`

### D10 — Clip `soucre thô` tối đa 2 lần

Mỗi clip quay thật `Source/soucre thô` tối đa 2 lần trên toàn bộ các video (khi dùng làm cảnh chèn B-roll vẫn phải tuân trần ngoại lệ 2–5 % của D15 và giới hạn lặp D8 ≤ 2 lần / video, ≤ 2 video); `media_reuse.py audit` khớp bằng thời lượng + vân tay.

- Kiểm: media_reuse · Nguồn: người dùng 2026-11-11; tham chiếu D8/D15 2026-11-16 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md D10`

### D11 — Phông xanh: tách lại từ file GỐC

Không dùng `Footage_SoucreTho_*_Keyed.mp4` (người dính nền B-roll mờ → tách ra cánh tay bị cắt, viền trắng, ghế trong suốt). Luôn lấy `Source/soucre thô/soucre 2/C00xx.MP4`, `scripts/chroma_studio.py` (matte độ xanh trội, giữ thành phần lớn nhất, khử ám xanh, không lấp lỗ thân, xoay 9:16, phóng ≥ 1,3×, đầu ở 36 %), render đúng thời lượng bản cũ, ghi đè `media/footage_studio/<tên>_Studio.mp4` rồi cập nhật media trong project (path, duration, file_size, fingerprint). Không còn đường dẫn `Keyed` trong project. Nguồn gốc không còn (C0067) thì lấy clip cùng loạt chưa dùng (C0062).

- Kiểm: mắt + đếm `Keyed` · Nguồn: người dùng 2026-11-12 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md D11`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục D11

### D12 — Nền studio = ảnh phòng thật không người

Clip phông xanh ghép lên ảnh phòng THẬT không người do người dùng gửi (kệ sách, đèn, cây, rèm, ghế bành): `scripts/studio_plate.py` (`fit` / `nochair` / `curtain` / `dark`) dựng 1080×1920; ảnh có người thì chỉ lấy phần rèm / tường, xoá vật thể người dùng bảo. CẤM nền vẽ bằng code (gradient, bokeh, lá giả — bị chê "phèn") và xoá người tự động bằng inpaint (vết nhoè). Mỗi video một nền / biến thể (lật, phóng, chỉnh màu). Kho: `TNEDIT/07_Assets/Nen_Background/Phong_Studio_Podcast/{ref,plate}`. Chữ tiêu đề đỏ chìm trên rèm cam → đổi trắng / vàng `[đề xuất]`.

- Kiểm: mắt · Nguồn: người dùng 2026-11-12 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md D12`

### D13 — Footage ban công AHUY QUAY

Footage `AHUY QUAY/Video`: xoay `transpose=1`, 1080×1920, tắt tiếng, cắt đoạn 6–10 s CRF 12, tối đa 2 lần mỗi clip; chỉ thay B-roll có người (không thay cảnh màn hình / dữ liệu); chỉ thay clip còn NHÌN THẤY (project cũ có lớp `gfx_under` / ô lưới che V1) — đo phần thấy trước khi thay.

- Kiểm: qa_frames · Nguồn: người dùng 2026-11-11 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md D13`

### D14 — Hình đến đâu tiếng đến đó

Giọng của cảnh nào phát dưới hình của chính cảnh đó: đến cảnh nào thì có lời nói của cảnh đó, kể cả cảnh chèn / B-roll (B-roll không có tiếng riêng theo D2 nhưng giọng `voice-b-roll-N` của nó phải chạy đúng dưới hình `b-roll-N`). Đầu giọng lệch đầu hình ≤ 0,12 s; hình của cảnh khác không được chiếm khung khi giọng cảnh này đang nói quá 0,5 s (chỉ cho phép phần chuyển cảnh); thứ tự cảnh theo kịch bản. Cảnh chèn ngoài danh sách (footage, kho D5) được tính là cảnh chèn của cảnh đang nói và phải minh hoạ đúng lời đó (D9). Tăng tốc thì hình và giọng cùng mức (D4). Kiểm: `scripts/scene_check.py` (FAIL chặn như G5).

- Kiểm: scene_check · Nguồn: người dùng 2026-11-13 · Độ tin: high
- Nguồn gốc: 

### D15 — B-roll mặc định 100 % Google Flow MCP; footage thật / stock tối đa 2–5 % thời lượng B-roll

Mục tiêu **100 %** thời lượng B-roll được tạo bằng **Google Flow MCP** (D3; tối thiểu **≥ 95 %**). Footage quay thật hoặc stock (`auto-footage`, kho `TNEDIT/06_B-Roll`, Pexels, Pixabay, Mixkit, kho D5) chỉ là ngoại lệ hẹp tối đa **2–5 %** thời lượng B-roll (trần cứng **≤ 5 %**; ưu tiên **0 %** nếu Google Flow phủ tốt nội dung cảnh). CẤM kéo clip stock lặp lại từ `auto-footage` / Mixkit / TNEDIT để thay thế việc tạo B-roll độc bản bằng Google Flow. Muse local chỉ dùng làm dự phòng khẩn khi Google Flow không khả dụng và người dùng đồng ý (D3). Số trong `rules.json › params.broll`.

- Kiểm: edit_rules + media_reuse · Nguồn: người dùng 2026-11-16 · Độ tin: high
- Nguồn gốc: 

## E. Nỗi đau (ưu tiên edit)

### E1 — Nhấn mọi từ khoá nỗi đau

Mỗi từ khoá nỗi đau của người xem (thất bại, mất khách, tốn thời gian, không biết bắt đầu…) có chữ chính phát sáng + zoom punch (~118 % `[đề xuất]`) + SFX nhấn, trong −0,3 … +1,5 s quanh lúc nói. Ngoại lệ: từ khoá chạm mặt thì chữ ra sau người (B9), đoạn đó giữ cỡ khung thường, không punch. Từ điển `edit_rules.PAIN_LEXICON` (90+ cụm); từ riêng của ngành thêm qua `keywords` của kịch bản; `analyze_and_scaffold.py` ghi `pain_keywords` cho từng phân cảnh.

- Kiểm: edit_rules · Nguồn: người dùng 2026-11-06 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md E1`, `kb-master-video-edit.md#rules.md mục 2`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục E1

### E2 — Cảnh chèn sau minh hoạ đúng nỗi đau

Cảnh chèn ngay sau từ khoá nỗi đau minh hoạ đúng nỗi đau đó.

- Kiểm: mắt · Nguồn: người dùng 2026-11-06 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md E2`

## F. Âm thanh

### F1 — SFX mở đầu ở khung 0–1, mỗi video một kiểu

Một tiếng ting / switch / impact / whoosh / glitch bắt đầu ở khung 0–1 (00:00:00:00–01), dài ~0,3 s, cắt lặng đầu file, mờ ~0,1 s cuối; mỗi video một kiểu (cặp mở đầu cấp bởi `rotation.json`, không lặp trong 5 video); đặt NGAY DƯỚI track giọng, tên "★ SFX MỞ ĐẦU …", màu Violet, marker "SFX MỞ ĐẦU" ở 00:00 (ngày 2026-10-31 đặt ở A7–A8 nên người dùng tưởng chưa có).

- Kiểm: scripts/audit_sfx.py · Nguồn: người dùng 2026-10-31 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md F1`, `kb-master-video-edit.md#cindy-memories/feedback_opening-sfx-every-video.md`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục F1

### F2 — Mỗi click một file; không lặp take; không file méo

Mỗi click trong một chùm (ô lưới, dải, từng từ, cắt nhanh) là một file khác; không lặp một take cả video; không dùng file SFX méo (đỉnh bị cắt bằng); không dùng theSOUNDS. SFX căn đỉnh vào khoảnh khắc hình, giữ nguyên đuôi.

- Kiểm: scripts/audit_sfx.py · Nguồn: người dùng 2026-11-04 lần 10 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md F2`, `kb-master-video-edit.md#rules.md mục 3`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục F2

### F3 — Mức âm thanh: giọng −3…−5 dBFS, nhạc nền thấp hơn giọng 15–20 LU, SFX −8…−12 dBFS

Đo trên bản mix: đỉnh giọng −3 … −5 dBFS (đích −4); nhạc nền có độ to tích hợp THẤP HƠN giọng 15–20 LU (đích 17), lời luôn trên nhạc ≥ 10 LU mọi cửa sổ có lời; SFX đỉnh −8 … −12 dBFS (tầng A nhấn mạnh −8, B −10, C −12). Bản giao −16 LUFS (−14 LUFS khi đăng mạng), true peak ≤ −1,5 dBTP. Giọng đều giữa các clip (`scripts/voice_level.py`, lệch ≤ 1,5 LU; xuất WAV 2 kênh — WAV mono đo đúng nhưng FilmCraft phát ra 2 kênh to thêm 3 dB). Giọng đã lọc sát đỉnh nên luôn gắn limiter master (`scripts/limit_master.py`, mặc định −2,2 dB để true peak liên mẫu ≤ −1,5 dBTP). Đặt mức bằng `scripts/audio_levels.py plan`, kiểm bằng `scripts/audio_levels.py check`. Số trong `rules.json › params.audio`.

- Kiểm: scripts/audio_levels.py check · Nguồn: người dùng 2026-11-13 (thay F3 cũ −14…−16 LUFS, giọng −16 LUFS/clip) · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md F3`, `kb-master-video-edit.md#rules.md mục 3`, `kb-dung-video-talking-head.md#rules.json loudness/bgm/presets`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục F3

### F4 — Kho SFX, font, nhạc mặc định

Ưu tiên SFX hot trend `/home/vmiz/Thanh/Media/TNEDIT/02_SFX/sfx hmc` (`HMC:` trong `assets/motion-fx/sfx_catalog.json`; quy luật đặt ở kb-master-video-edit › sfx-hmc.md) kết hợp toàn bộ kho SFX (`02_SFX`, `sfx trends`), Font (`01_Font`), VFX (`03_VFX`), Assets (`07_Assets`), Nhạc nền (`08_Nhac_Nen`) tại `/home/vmiz/Thanh/Media/TNEDIT`. Kho SFX lớn 2.995 file chỉ có khi cắm USB (`/media/vmiz/Over Powers/…/Motion Claude/sfx`).

- Kiểm: scripts/audit_sfx.py · Nguồn: người dùng 2026-11-09 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md F4`, `kb-master-video-edit.md#rules.md mục 6`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục F4

### F5 — Chuỗi xử lý nhạc nền

Nhạc nền: lọc cắt trầm 100 Hz, giảm 3 dB quanh 2 kHz (Q 0,7) để chừa chỗ cho giọng, fade vào 1,0 s, fade ra 1,5 s; chạy suốt video; hạ 5 dB quanh điểm cắt (`sfx_auto.duck`, bản MotionFX đã duyệt). Hồ sơ @__dviet: không duck.

- Kiểm: scripts/audio_levels.py check · Nguồn: dvth bgm.* (thlib/mix.py) + motion-fx.md mục SFX (duck 5 dB) · Độ tin: medium
- Nguồn gốc: `kb-dung-video-talking-head.md#rules.json bgm`

### F6 — Lọc giọng khi còn ồn

Giọng còn ồn sau lọc mặc định (DeepFilterNet): đề xuất lọc mạnh hơn (attenuation cao hơn / ClearerVoice / gate), nghe thử đoạn ngắn trước rồi mới thay vào project. Chuỗi lọc mở: kb-dviet-viral-text-audio-edit (`scripts/apps/dviet-viral-text-audio-edit/scripts/clean_and_master_voice.py`).

- Kiểm: tai · Nguồn: ghi nhớ thcn-voice-ambient-noise 2026-11-01 · Độ tin: medium
- Nguồn gốc: `kb-master-video-edit.md#cindy-memories/project_thcn-voice-ambient-noise.md`

## G. Quy trình và quyền

### G1 — Thứ tự làm một video từ kịch bản

Phân tích kịch bản → HeyGen A-roll → **Google Flow MCP B-roll** (D3, D15; Muse chỉ dự phòng khẩn khi được đồng ý) → voice B-roll → đối chiếu đủ file (cổng 05.5) → chọn ứng dụng → sơ đồ timeline (C3) → dựng → tự kiểm (G5) → mở cho người dùng duyệt. Đây là thứ tự công việc agent tự theo, không phải chuỗi script tự chạy. Chi tiết: kb-master-video-edit › aroll-broll-workflow.md (bước B-roll áp D3, D15).

- Kiểm: analyze_and_scaffold.py validate · Nguồn: người dùng 2026-11-06; cập nhật engine B-roll 2026-11-16 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md G1`

### G2 — Khoá HeyGen gửi riêng từng lần

Khoá HeyGen người dùng gửi riêng mỗi lần qua chat, chỉ dùng cho lần đó, KHÔNG lưu vào `~/.config/heygen/env` hay skill. Không có khoá thì dừng ở dry-run (0 credit).

- Kiểm: — · Nguồn: người dùng 2026-11-06 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md G2`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục G2

### G3 — Thiếu file thì báo đúng tên, không dựng nửa chừng

Thiếu file: báo đúng tên file thiếu, không dựng nửa chừng. Thiếu thông tin không đoán được (kịch bản, CTA, số liệu, tên riêng): hỏi gộp một lần; trong lúc chờ làm phần không phụ thuộc câu trả lời.

- Kiểm: analyze_and_scaffold.py validate · Nguồn: rules.md mục 5 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md G3`

### G4 — Chọn ứng dụng

Ứng dụng 1 = FilmCraft (nói chuyện, xây kênh). Ứng dụng 2 = EffectCraft (motion graphic, animation). Chưa rõ thì chọn theo bảng loại việc trong SKILL.md và ghi giả định; chỉ hỏi khi quyết định thật sự thuộc người dùng. Máy này có FilmCraft 0.13 (`~/.local/bin/filmcraft`), EffectCraft 0.17, OpenChatCut, Diffusion Studio; KHÔNG có After Effects / Premiere (`.jsx` / `.aep` / `.prproj` chỉ soạn, chạy trên máy Windows). GPU RTX 3070 Ti 8 GB dùng chung với FilmCraft / EffectCraft: công cụ AI nặng thiếu bộ nhớ → chạy CPU hoặc đóng bớt app.

- Kiểm: — · Nguồn: người dùng 2026-11-06 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md G4`

### G5 — Tự kiểm trước khi giao

CỔNG CHẶN: `spec_lint` phải 0 HARD (HARD: thiếu media, clip vượt cuối file / SFX ngắn, key trùng / lùi mốc, dur ≤ 0, media `x125` / `x115`, `text_voice_burst`), `edit_rules audit` phải 0 LỖI và — khi có `00_storyboard_manifest.json` — `scene_check` phải 0 FAIL (D14 hình–tiếng, D9 bám kịch bản); chưa đạt thì TỰ SỬA trước khi mở cho người dùng duyệt. SOFT ghi báo cáo: chữ hook sau 1,5 s, lời đầu sau 0,5 s, khoảng chết > 0,8 s, hình hết trước giọng, đuôi đen, thiếu SFX mở đầu, nguồn bị phóng to. Thứ tự: `scripts/spec_lint.py` (trước khi dựng) → `scripts/scene_check.py` → `scripts/edit_rules.py audit` (12 tiêu chí) → `scripts/qa_frames.py` → `scripts/limit_master.py` → `scripts/audit_sfx.py` → `scripts/audio_levels.py check` / `scripts/qa_audio.py` → `scripts/qa_sync.py` (nhanh: `scripts/fc_fast_qa.py` gộp nhiều bước trong 1 phiên FilmCraft). Mỗi bước là một lệnh riêng agent tự gọi. Nấc chưa kiểm ghi "chưa kiểm" và gọi sản phẩm là "bản nháp". Video dài hoặc người dùng cần chắc: rà chéo bằng một agent khác, bàn giao ghi đúng "tự kiểm" / "rà chéo".

- Kiểm: — · Nguồn: rules.md + PROMPT tầng 6 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md G5`, `kb-master-video-edit.md#PROMPT_CHUAN_THEO_TANG.md tầng 6`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục G5

### G6 — Sửa theo góp ý

Đổi đúng phần bị chê trên project đang mở (A3), chạy lại G5, mở lại cho người dùng.

- Kiểm: — · Nguồn: rules.md · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md G6`

### G7 — Chạy theo lô 5 project / lượt; MP4 chỉ sau duyệt

Sửa 5 → mở cho duyệt → **người dùng duyệt video nào mới xuất MP4 video đó** (A1) → đo (`ffprobe`, `ebur128`) → mới sang 5 tiếp. Xuất MP4 tối đa 2 phiên song song (3 phiên + cửa sổ đang mở làm FilmCraft đóng kết nối, file ra thiếu); đóng cửa sổ FilmCraft của project trước khi ghi đè file hay xuất (theo ngoại lệ (2) của A3: còn chỉnh sửa chưa lưu / cửa sổ người dùng tự mở → hỏi trước); việc GPU bọc `flock /tmp/gpu.lock`; nhiều agent thì mỗi agent chỉ sửa 1 file project.

- Kiểm: mắt · Nguồn: người dùng 2026-11-12; sửa 2026-11-13 (MP4 chỉ sau duyệt) · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md G7`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục G7

### G8 — Xoá MP4 lỗi khi được bảo; sao lưu ngoài project

Bản lỗi thì xoá đúng MP4 lỗi khi người dùng bảo, giữ project; bản sao lưu để ngoài thư mục project (`/tmp/…`), không để `.bak` trong `Porject/`; tên gần giống phải phân biệt: `16_KB06_…` (HeyGen + Muse, không phông xanh) ≠ `KB06_XM06_…` (phông xanh).

- Kiểm: — · Nguồn: người dùng 2026-11-12 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md G8`

### G9 — Tra soát lô phông xanh

Đếm trong `.fcproj` clip `Keyed`, `footage_studio`, `SoucreTho`, `Video_9x16_cat`, `cover.png` + có MP4 chưa; mỗi nguồn `soucre thô` ≤ 2 video (D10). Agent báo xong chỉ là lời tự báo → người điều phối tự `qa_frames` và quét đường dẫn.

- Kiểm: qa_frames · Nguồn: người dùng 2026-11-12 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#style.md G9`

### G10 — Thời gian giao là thời gian thực

"Làm trong N phút" = tổng thời gian thật từ lúc nhận việc tới lúc mở project; mục tiêu dựng gọn dưới 10 phút: bóc lời faster-whisper large-v3-turbo CPU int8 ngay từ đầu; tiếng lấy từ file video qua `audio_of`; kẹp keyframe trong clip; nguồn 4K quay ngang → proxy 1080×1920; chỉ dựng một lần sau khi soát spec (`fc_build_fast`); kiểm 3–4 khung trước khi mở. Riêng việc có hạn giờ: `qa_sync` (cần xuất) được chạy SAU khi mở project, ghi "chưa kiểm" tới khi xong; không chờ Muse trong hạn ngắn; báo tiến độ theo mốc thời gian; hạn 6–10 phút thì bỏ lọc giọng nặng.

- Kiểm: — · Nguồn: người dùng 2026-11-05 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#cindy-memories/feedback_time-budget-is-wall-clock.md`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục G10

### G11 — Việc dựng video không áp quy trình phần mềm

Việc dựng video không áp quy trình phần mềm của luật chung `~/.claude` (TDD, độ phủ test, tự mở planner/code-reviewer…); kiểm bằng G5. Giao việc cho đội OPA (Hermes) theo kb-opa-delegate.

- Kiểm: — · Nguồn: rules.md mục 4–5 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#rules.md mục 5`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục G11

### G12 — Không chắc loại việc: chọn, ghi giả định

Không chắc loại việc: chọn theo bảng loại việc trong SKILL.md, ghi giả định, không dừng để hỏi. Footage người nói không bao giờ đi đường promo không footage hay phim 3D.

- Kiểm: — · Nguồn: rules.md mục 5 + SKILL.md Bước 0 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#rules.md mục 5`

## H. Học từ dung-video-talking-head

### H1 — Mọi con số có nguồn

Mọi con số trong luật có `source` + `confidence` trong `rules.json`; số `[đề xuất]` là confidence medium/low. Thiếu số thì báo lỗi, không lặng lẽ dùng số cứng cũ trong code (không fallback).

- Kiểm: — · Nguồn: dvth rulebook-1.1 design §4.1, test_no_rule_fallbacks.py · Độ tin: high
- Nguồn gốc: `kb-dung-video-talking-head.md#docs/2026-09-11-talking-head-rulebook-1.1-design.md`

### H2 — Kiểm bằng đo lại, không tin lời tự báo

Bước kiểm đọc lại project / audio / khung hình từ đĩa và đo lại; không dùng số do bước dựng tự báo. Ảnh contact sheet chỉ thêm "cần xem", không tự kết luận đạt.

- Kiểm: — · Nguồn: dvth verify.py V1–V8 · Độ tin: high
- Nguồn gốc: `kb-dung-video-talking-head.md#releases/1.2.3/scripts/verify.py`

### H3 — Agent chọn trong ứng viên do code sinh

Chỗ cần phán đoán (từ khoá nhấn, nỗi đau, hook, CTA) lấy từ danh sách ứng viên do script đề xuất (`edit_rules.PAIN_LEXICON`, `cut_plan.OPTIONS`, `analyze_and_scaffold` pain_keywords); agent chọn và ghi lý do; spec do code lắp, không sửa tay spec đã lắp.

- Kiểm: — · Nguồn: dvth PLAN (H/K/S/C candidates → compose) · Độ tin: medium
- Nguồn gốc: `kb-dung-video-talking-head.md#releases/1.2.3/stages/PLAN.md`

### H4 — Lưu duyệt và góp ý có cấu trúc

Mỗi lần người dùng duyệt / chê: ghi nguyên văn vào `APPROVALS.md` / `FEEDBACK.jsonl` trong thư mục dự án (ngày, video, câu người dùng nói, luật bị ảnh hưởng). Góp ý thành luật mới thì thêm vào `rules.json` với nguồn = câu người dùng.

- Kiểm: — · Nguồn: dvth OPERATOR.md · Độ tin: medium
- Nguồn gốc: `kb-dung-video-talking-head.md#releases/1.2.3/stages/OPERATOR.md`

### H5 — Prompt B-roll có kỷ luật (5 tầng chống nhựa)

Prompt B-roll AI cho Google Flow (`omni-flash`, T5-XXL/Gemma): tiếng Anh `18–95` từ, viết có cấu trúc từ 5 tầng (`layers`: `l1_shot_subject`, `l2_action_script`, `l3_environment`, `l4_optics_realism`, `l5_camera_motion`) bám sát nghĩa đen `anchor_quote` và `script_beat_vi` từ Quy trình 3 Agent (`params.broll.layered_prompt_spec`). (1) `l1_shot_subject` (Primacy Zone): Shot size + Camera angle + bắt buộc `Vietnamese` (khi có người) + Faceless lock (`from behind`, `over the shoulder`, `hands only`, `silhouette`, `face out of frame`) nếu nhắc `founder`/`CEO`/`speaker`/`narrator`/`host` + ngoại hình/trang phục vải thật tự nhiên (copy-paste nguyên văn Frozen Descriptor nếu nhân vật lặp lại). (2) `l2_action_script` (Literal Action): Hành động `State A → Verb → State B` diễn tả đúng nghĩa đen `anchor_quote` bằng con người & đồ vật đời thường thật; CẤM ẩn dụ CGI trừu tượng (`glowing prism`, `amber cube`, `metal pipeline rails`, `floating nodes`, `energy core`, `gears`, `hologram`, `sci-fi`). (3) `l3_environment` (Lived-in Grounding): Bối cảnh công sở/đời thực Việt Nam sống động vừa đủ; màn hình / laptop / tivi / bảng / giấy chỉ xuất hiện khi ghi rõ `out of frame`, `out of focus`, `blurred`, `defocused` hoặc `blank` («angled away», «soft glow» KHÔNG đủ — Flow vẫn vẽ logo và dashboard); sản phẩm chung không thương hiệu. (4) `l4_optics_realism` (Anti-Plastic Optics & Physics): Thông số ống kính tài liệu (`shot on 35mm documentary lens f/2.8`, `subtle natural handheld camera feel`, `soft overcast window light mixing with desk lamp`, `subtle 35mm film grain`, `unretouched skin texture`, `natural fabric creases`); CẤM từ sáo rỗng Anti-Slop (`stunning`, `breathtaking`, `hyper-detailed`, `8k`, `masterpiece`, `magical`, `very realistic`) và từ nhựa/CGI (`glossy skin`, `porcelain skin`, `airbrushed`, `cyberpunk neon`, `unreal engine`, `octane render`). (5) `l5_camera_motion` (Kinetic & Clean Tail): Đúng 1 chuyển động máy nhẹ nhàng tự nhiên + khẳng định sạch khung (`unbranded blank surfaces, clean frame`), KHÔNG nối đuôi `no text/no logo`, KHÔNG cú pháp trọng số CLIP `(keyword:1.3)`. Một clip một cảnh liền (không `transition from/to`, `cut to`, `montage`, `split-screen`, `PiP`, `overlay`); cấm từ sinh chữ/logo/số liệu/UI giả trong `BANNED_RE` (`scripts/broll_fix.py`: `note`, `checklist`, `checkbox`, `written`, `bullet`, `handwritten`, `handwriting`, `chatting`/`message`/`messaging`/`texting`, `side-by-side`, `comparison`, `graph`, `metrics`, `analytics`, `statistics`, `engagement`, tên nền tảng & hãng `youtube`/`tiktok`/`facebook`/`instagram`/`iphone`/`macbook`/`apple`/`samsung`/`google`…); không voice, không text (D2). Độ dài xin Google Flow = ⌈giọng của cảnh + 0,3 s⌉ (3–15 s; tách sub-beat khi > 7,5 s hoặc 2 vế đối lập; Muse dự phòng tối đa 10 s). Kiểm bằng `scripts/broll_fix.py lint` (strict layers & anti-plastic) trước khi gọi Google Flow MCP (hoặc Muse dự phòng theo D3); khi chuẩn hoá bằng `scripts/broll_fix.py normalize` tự động cắt viền trắng/đen/đồng màu ≥ 2 % từ khung đầu (`1.2.2 F3` `trim_uniform_borders`) trước khi scale 1080×1920, rồi kiểm lại bằng `scripts/broll_fix.py verify` + Agent 3 kiểm tra trực quan 2 bản 720p & `qa/broll_check_sheet.jpg` loại ngay bản da nhựa, ngón tay méo, đồ vật phi vật lý, cắt cảnh ngầm hoặc lệch `anchor_quote`.

- Kiểm: broll_fix lint + verify + mắt · Nguồn: dvth B-roll 1.2.0–1.2.3 + luật trung thực v2.16; cập nhật Flow 2026-11-16; chuẩn hoá 5 tầng Anti-Plastic & 3-Agent 2026-11-16 · Độ tin: high
- Nguồn gốc: `kb-dung-video-talking-head.md#releases/1.2.3/stages/PLAN.md`, `kb-master-video-edit.md#CHANGELOG.md 2.16`

## P. Hồ sơ style @__dviet (tuỳ chọn)

### P1 — Hồ sơ @__dviet chỉ bật khi người dùng gọi tên · *tuỳ chọn*

Style @__dviet là HỒ SƠ TUỲ CHỌN: chỉ áp khi người dùng nói rõ ("kiểu dviet", "như @__dviet"). Học kỹ thuật và nhịp, không chép nội dung, câu chữ hay logo của kênh. Khi bật, các điểm sau GHI ĐÈ luật chung; mọi luật khác (A, D, E, F, G, B2, B8–B13, B15–B16, C1) vẫn giữ. Đánh giá 2026-11-13: giữ luật chung làm mặc định (đã duyệt nhiều vòng), thử A/B cùng 1 clip trước khi đổi luật chung.

- Kiểm: — · Nguồn: người dùng 2026-11-13 + rules.md mục 2, 7 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#dviet-style-guide.md`, `kb-master-video-edit.md#dviet-text-motion-2026-11-11.md`

### P2 — dviet: 3 font · *tuỳ chọn*

Ghi đè B1: 3 font — SF Pro Display (chữ nối / phụ đề), Playfair Display Bold Italic (từ khoá, màu nhấn), Great Vibes (viết tay, hiếm). Không Instrument Serif / Satisfy (thiếu dấu).

- Kiểm: mắt · Nguồn: đo 17 video 2026-10-29 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#dviet-style-guide.md`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục P2

### P3 — dviet: trắng + một màu nhấn · *tuỳ chọn*

Ghi đè B3/B5: trắng + MỘT màu nhấn mỗi video (vàng `#F4C40C` mặc định; tím `#8C6CFF`, xanh neon `#04AC04`, hổ phách khi cảnh tối); ghép lớn–nhỏ (từ khoá to gấp 2–4 lần), chồng 3 tầng, số lớn mở đầu danh sách, tiêu đề phần y ≈ 25 %, CTA "lưu lại" sớm (4–8 s). Bóng mềm, không viền, giãn chữ âm. Chữ minh hoạ chính hiệu ứng nó nói (nói "phát sáng" thì chữ phát sáng, "mờ" thì chữ mờ). Mã màu vàng mặc định `#F4C40C` (`dviet-style.json` › `yellow_default`; bản sáng `#F3C610`).

- Kiểm: mắt · Nguồn: đo 17 video 2026-10-29 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#dviet-style-guide.md`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục P3

### P4 — dviet: chữ vào blur-in, ra theo B14 · *tuỳ chọn*

Chữ vào blur-in 0,17 s, đúng / sớm 0–0,1 s so với lời. Phần "ra bằng cắt cứng" của bản đo 17 video KHÔNG áp: B14 (soft_out, đo lại 2026-11-11) giữ nguyên.

- Kiểm: mắt · Nguồn: đo 2026-10-29 + 2026-11-11 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#dviet-style-guide.md`, `kb-master-video-edit.md#dviet-text-motion-2026-11-11.md`

### P5 — dviet: nhịp và zoom · *tuỳ chọn*

Ghi đè C4/E1 punch: punch-in ×1,12–1,25 tức thì giữa câu, zoom blur 0,15–0,25 s che jump cut; nhịp ~287 từ/phút, khối chữ ~1,3 s, cảnh nói 1,7–3 s; nhạc nền chạy suốt (mức theo F3). C1 vẫn giữ: mọi điểm cắt có chuyển cảnh (không "cắt thẳng là chính").

- Kiểm: mắt · Nguồn: đo 17 video 2026-10-29 + rules.md mục 7 · Độ tin: high
- Nguồn gốc: `kb-master-video-edit.md#dviet-style-guide.md`
- Chi tiết nguyên văn (thông số, ngoại lệ): `references/rules-details.md` › mục P5

## Luật đã bị thay (không áp)

| ID | Luật cũ | Thay bởi | Nguồn |
|---|---|---|---|
| X1 | Luật D4 bản 2.15 (2026-11-08): tăng đúng 1.25x cho HeyGen / Muse; ngoại lệ 2.15.4: < 40 s giữ 1.0x. | D4 | CHANGELOG 2.15, 2.15.4 |
| X2 | Luật 2026-11-06: ưu tiên flash · shutter · flicker · glitch · light leak ≥ 40 % điểm cắt. | C2 | rules.md mục 2 (2026-11-06) |
| X3 | `fx.caption_band` ~50 %, đậm thêm ~40 % trên B-roll sáng. | B15 | rules.md mục 2 |
| X4 | Ghi nhớ 2026-11-04 (lần đầu): chữ nhiều màu, có viền. | B2 | cindy-memories/feedback_analyze-cuts-before-transitions.md |
| X5 | Luật lần 8 / lần 11: phụ đề trắng + vàng. | B5 | cindy-memories/feedback_text-colors-and-sfx-sync.md |
| X6 | F3 cũ: master −14…−16 LUFS, true peak ≤ −1,5 dBTP; voice_level bù từng đoạn về −16 LUFS; mô tả skill "lọc giọng −16 LUFS", dviet −14 LUFS. | F3 | style.md F3, rules.md mục 3 |
| X7 | G7 bản 2026-11-12: sửa 5 → mở cho duyệt → xuất 5 MP4. | G7 | style.md G7 |
| X8 | D5 / D7 bản 2026-11-09..11: `rvm-matte` + `despill=type=green`, ghép phòng làm việc sáng mờ hoặc nền vẽ sẵn. | D11 | style.md D5, D7 |
| X10 | motion-fx.md: không lặp file khi còn file khác; dùng lại khi cách ≥ 6 s. | F2 | motion-fx.md (mâu thuẫn rules.md mục 3: không lặp một take cả video) |
| X11 | motion-fx.md mục trộn (THCN 07): giọng −2,4 dB, nhạc ~−22,5 LUFS, SFX gain_offset −0,5. | F3 | motion-fx.md |
| X12 | D4 bản 2026-11-11 (Rule 1): chọn 1.15x; sau khi tăng < 40 s thì 1.1x; vẫn < 40 s thì 1.0x; áp cho HeyGen / Muse; media `x115`. | D4 | style.md D4 (2026-11-11) |
| X9 | PROMPT tầng 6: `edit_rules.py audit` đạt 8/8. Nay máy chấm có 12 tiêu chí. | G5 | PROMPT_CHUAN_THEO_TANG.md |
| X13 | D3 bản 2026-11-13..14: Muse local là nguồn tạo B-roll mặc định; chỉ chuyển sang Google Flow khi `broll_fix.py ready` báo Muse hỏng. | D3, D15 | rules.md; người dùng 2026-11-13..14 |
| X14 | D8 bản 2026-11-11: mỗi cảnh B-roll tối đa 1 lần trong một video và tối đa 2 video khác nhau. | D8 | người dùng 2026-11-11 |
