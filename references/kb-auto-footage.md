# kb-auto-footage — toàn văn tài liệu của nguồn `auto-footage`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/auto-footage/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.


<!-- ===== file: auto-footage/SKILL.md ===== -->

---
name: auto-footage
description: Tự tìm hoặc tự tạo B-roll — video cảnh chèn / footage và ảnh B-roll — cho từng cảnh của một video người nói hoặc một kịch bản, hoặc tạo nhanh theo một câu mô tả. Đọc lời (Whisper khi đầu vào là video), chia cảnh, tìm theo nội dung hình bằng CLIP trong kho TNEDIT/06_B-Roll, Pexels, Pixabay, Mixkit; không có kết quả đủ hợp thì tạo bằng Muse AI (ảnh 9:16, video 1–60 s từ ảnh đó, giữ nhân vật bằng ảnh tham chiếu); ảnh có thể thành clip zoom chậm; tải, chuẩn hoá (H.264 / JPEG, bỏ tiếng, xoá metadata), lưu kho theo chủ đề kèm nguồn/giấy phép, bảng ảnh + trang duyệt phát video, mỗi cảnh 1 lựa chọn + 2 dự phòng. Dùng khi người dùng nhờ "tìm footage", "tìm B-roll", "tìm cảnh chèn", "tạo footage", "tạo ảnh b-roll", "tạo video cảnh chèn", "kiếm stock video/ảnh", "footage cho kịch bản/video này", hoặc gọi "auto-footage". Đã tích hợp vào opa-video-studio (scripts/apps/auto-footage/, references/kb-auto-footage.md) và cũng có thể gọi độc lập.
---

# auto-footage — tìm / tạo B-roll (video cảnh chèn + ảnh) theo cảnh

Đầu vào: **video người nói**, **kịch bản**, hoặc **một câu mô tả** (lệnh `make`). Mỗi cảnh ra **video cảnh chèn**, **ảnh B-roll**, hoặc cả hai (`kind`). Đầu ra trong `TNEDIT/06_B-Roll/_Tim_Footage/<dự_án>/`: `picks.json` (mỗi cảnh 1 clip chọn + 2 dự phòng, đường dẫn file đã chuẩn hoá, điểm, nguồn, giấy phép), `sheet.jpg` (bảng ảnh 2 cảnh / hàng, viền vàng = clip đang chọn) và `review.html` (trang duyệt mở bằng trình duyệt, rê chuột lên clip để phát). Thiết kế: `/home/vmiz/Thanh/Media/EDIT agnet/docs/specs/2026-11-01-auto-footage-design.md`.

```bash
F=~/.venvs/footage/bin/python; S=~/.claude/skills/auto-footage/scripts
```

## Quy trình

1. **Lấy lời** (chỉ khi đầu vào là video): `$F $S/footage.py transcribe VIDEO --out <thư mục làm việc> [--prompt "kịch bản nếu có"]` → `transcript.txt` (câu có mốc giây; GPU ~20 s / phút video).
2. **Chia cảnh → `scenes.json`:** `$F $S/footage.py draft <transcript.json | kich_ban.txt> --project TÊN -o scenes.json` lập khung (gộp câu thành cảnh 4–8,5 s, mỗi ý liệt kê "Thứ hai…" một cảnh, điền mốc + lời). Agent sửa ranh giới cảnh nếu cần, bỏ cảnh chào / cảm ơn không cần hình, rồi **điền** `query`, `alt_queries`, `category`, `mixkit_tags`, `muse_prompt` (định dạng dưới). `run` từ chối cảnh còn trống `query`.
3. **Chạy:** `$F $S/footage.py run scenes.json` — tự cập nhật chỉ mục kho, tìm 4 nguồn song song, CLIP chấm điểm cùng thang, tải bản đầy đủ top 3, Muse tạo cảnh thiếu, ghi `picks.json` + `sheet.jpg`. Kịch bản 6–8 cảnh: ~1–2 phút tìm + tải; mỗi cảnh Muse thêm ~1–2 phút (2 cảnh song song).
4. **Xem `sheet.jpg` bằng mắt** (Read ảnh): đúng nghĩa cảnh, không chữ/logo/watermark lộ, không người nổi tiếng, không cảnh nhạy cảm. Clip chọn kém hơn dự phòng thì đổi: `$F $S/footage.py pick picks.json --scene 3 --alt 2` (vẽ lại bảng + trang duyệt), hoặc sửa query rồi chạy lại.
5. **Báo người dùng:** gửi `sheet.jpg` (ảnh) + đường dẫn `review.html` (xem chuyển động); mỗi cảnh: nguồn, điểm, dọc/ngang, cảnh nào do Muse tạo, cảnh nào `missing`, nguồn nào bị bỏ qua (thiếu key / lỗi mạng). Người dùng đổi bằng câu "cảnh N lấy số K".

**Tạo nhanh không cần kịch bản** (người dùng: "tạo 2 ảnh b-roll …", "tạo video cảnh chèn …"): `$F $S/footage.py make "mô tả tiếng Anh, ảnh chụp thật" --kind image|video|both [--n 2] [--project TÊN] [--name Chu_De] [--ref mat.jpg] [--seconds 8] [--animate]` → Muse tạo `n` biến thể vào `AI_Muse/<dự án>/`, bảng ảnh + trang duyệt ở `_Tim_Footage/<dự án>/`. `both` = một ảnh + video đi từ chính ảnh đó (1 lượt ảnh, 1 lượt video); `--animate` thêm bản zoom chậm của ảnh; `--seconds 30` (> 10) tự nối đoạn, máy đứng yên — `--seg 6`, `--steps "…" "…"`, `--camera-move`, `--no-chain`. Thời gian đo: 30 s ≈ 9–10 phút, 60 s ≈ 17 phút. Ảnh ~30–60 s, video ~1–2 phút; 2 việc song song (2 tài khoản Muse). Chạy nhiều lệnh `make` cùng lúc thì mỗi lệnh một `--project` (bảng ảnh / picks.json ghi theo dự án).

Lệnh lẻ: `$F $S/footage.py search "query tiếng Anh" [--kind image] [--sources local,mixkit] [--orientation any]` (xem nhanh, không tải) · `$F $S/footage.py index` (lập lại chỉ mục sau khi chép nhiều clip vào kho) · `$F $S/footage.py render picks.json` (vẽ lại bảng ảnh + trang duyệt).

## scenes.json

```json
{"project": "THCN05", "orientation": "portrait",
 "scenes": [
  {"id": 1, "text": "Đừng bắt AI viết kịch bản nữa", "t": [1.8, 5.7],
   "query": "frustrated young man staring at blank paper at desk",
   "alt_queries": ["confused creator holding empty notebook"],
   "category": "Mood_Confused", "min_dur": 4, "mixkit_tags": ["confused", "paper"],
   "muse": "auto", "muse_prompt": "Young Asian man at a desk holding a blank sheet of paper, puzzled expression, modern room"}]}
```

- `kind` (cảnh hoặc cả dự án): `video` (mặc định — clip cảnh chèn), `image` (ảnh B-roll; nguồn: kho TNEDIT, Pexels / Pixabay ảnh — Mixkit không có ảnh), `both` (tách thành cảnh `N` video + cảnh `N-anh` ảnh; Muse dùng chung một ảnh cho cả hai).
- `animate: true` (cảnh ảnh): ảnh được chọn thêm bản clip zoom chậm 9:16 (`anim_seconds`, mặc định 5) ở `_Tim_Footage/<dự án>/anh_dong/` — dùng làm cảnh chèn động mà không tốn lượt Muse video.
- `seconds` (cảnh video Muse): mặc định 5. **≤ 10 s → một video Muse; > 10 s → tự nối nhiều đoạn 5–10 s** (`seg_seconds`, mặc định 8): khung cuối đoạn trước làm khung đầu đoạn sau + câu nhắc giữ nguyên người / phòng / đạo cụ / ánh sáng, mối nối chuyển mờ 0,2 s, cắt đúng độ dài. Lý do (đo 2026-11-02, cùng prompt): một video Muse 10 s liền mạch, nhưng 30–60 s liền thì bối cảnh trôi dần (đạo cụ, góc máy, cửa sổ đổi). Đoạn tạo lần lượt (~1,5–2,3 phút / đoạn: 30 s ≈ 4 đoạn, 60 s ≈ 8 đoạn); đoạn giữ trong `AI_Muse/<dự án>/<tên>_doan/` để chạy lại không tốn lượt; độ lệch từng mối nối ghi trong `_nguon.json`. `muse_steps: ["đoạn 1 …", "đoạn 2 …"]` = mô tả riêng từng đoạn để kể diễn biến (thiếu thì lặp câu cuối). `chain: false` = ép một video liền (≤ 60 s). **Clip nối mặc định máy đứng yên** (`camera: "static"`): đo 2026-11-02 cùng cảnh 30 s — máy đứng yên giữ bối cảnh (độ giống CLIP với khung đầu 0,86–0,96, không đổi cảnh), còn prompt có đẩy / lia máy thì dù nối đoạn bối cảnh vẫn trôi (0,48: máy vào cận rồi Muse vẽ lại xung quanh). Đừng ghi chuyển động máy vào `muse_prompt` của clip dài; cần thì `camera: "move"` / `--camera-move` và chấp nhận trôi. Mỗi đoạn được kiểm ngay: trùng từng byte với đoạn trước (Muse trả lại video cũ khi prompt trùng) hoặc lệch khung đầu > 20/255 (Muse không bám ảnh) → tạo lại tối đa 2 lần, giữ bản khớp nhất; mọi video Muse có dấu `(shot <mã ảnh>)` trong prompt để tránh trả lại kết quả cũ.
- `query` / `alt_queries`: **tiếng Anh, tả cái nhìn thấy** (người, hành động, vật, bối cảnh, góc máy) — CLIP không hiểu khái niệm trừu tượng ("năng suất", "chiến lược"); khái niệm thì đổi thành hình cụ thể. 1 câu chính + 0–2 câu phụ.
- `category`: chủ đề kiểu kho hiện có (`Mood_Bored`, `UI_Smartphone`, `Video_Editing`, `Tech_AI_Future`…) → tên file `FTG_<category>_<mô_tả>_<id>.mp4`.
- `orientation`: `portrait` (mặc định, video 9:16), `landscape` hoặc `any`; clip ngang vẫn được nhận (làm thẻ / nền mờ) nhưng kém 0,01 điểm.
- `muse`: `auto` (tạo khi điểm cao nhất < 0,27 — đúng nghĩa đo được ≥ 0,28, lạc nghĩa ~0,24–0,25), `always` (luôn tạo — cảnh đặc thù không stock nào có, ví dụ màn hình phần mềm riêng, người Việt cụ thể), `never`. `muse_prompt` tiếng Anh, ảnh chụp thật; skill tự thêm "photorealistic, 9:16, no text, no watermark". Không có `muse_prompt` thì không tạo.
- `muse_ref` (cảnh hoặc cả dự án): ≤ 4 ảnh tham chiếu để Muse giữ đúng nhân vật — cảnh cần chính người nói (cầm đồ vật, ngồi bàn của họ…). Lấy khung mặt rõ từ video: `ffmpeg -ss 3 -i VIDEO -frames:v 1 -vf crop=… -map_metadata -1 ref.jpg`; prompt ghi "the same person from the reference photo" + mô tả áo / kính / phòng. Ảnh tạo ra làm khung đầu cho video nên video cũng giữ người.
- `t`, `text`: ghi lại để đặt B-roll lên timeline sau; skill không dùng để tìm.

## Nguồn, key, nơi lưu

- Thứ tự / chấm điểm: kho TNEDIT (chỉ mục CLIP `06_B-Roll/.footage_index/`, 3 khung / clip, 1 / ảnh) + Pexels + Pixabay + Mixkit (video) hoặc Pexels + Pixabay (ảnh) → cùng thang CLIP ViT-B-32; +0,01 đúng hướng khung, +0,01 clip đã có trong kho; clip ngắn hơn `min_dur` −0,05. Clip nguồn ngoài mà kho đã có (trùng mã số cuối tên file) bị bỏ.
- Key Pexels / Pixabay: người dùng tự dán vào `~/.config/footage/env` (`PEXELS_API_KEY=…`, `PIXABAY_API_KEY=…`). **Không hỏi key trong chat, không in key, không ghi key vào file khác.** Thiếu key → nguồn đó bị bỏ qua, có cảnh báo; vẫn chạy với kho + Mixkit + Muse.
- Lưu: video `06_B-Roll/Stock_Theo_Chu_De_Pexels|Pixabay|Mixkit/` (`FTG_…mp4`), ảnh `06_B-Roll/Anh_Theo_Chu_De_Pexels|Pixabay/` (`IMG_…jpg`, cạnh dài ≤ 2560, không EXIF), Muse → `06_B-Roll/AI_Muse/<dự_án>/` (`canhNN_….png` + `.mp4`), ảnh động → `_Tim_Footage/<dự_án>/anh_dong/`. Mỗi thư mục có `_nguon.json` (trang gốc, tác giả, giấy phép, dự án, ngày). Đã có cùng mã thì dùng lại, không tải lại.
- Chi tiết API, giới hạn, giấy phép: [references/sources.md](references/sources.md).

## Luật

- Muse là cách tạo mặc định; Muse không `ready` → báo người dùng, **không** tự chuyển sang dịch vụ trả phí.
- Clip Muse: xem kỹ khung đầu và giây cuối (có lúc nội dung biến mất / méo); hỏng thì xoá file `.png` / `.mp4` của cảnh đó rồi chạy lại với prompt cụ thể hơn (file còn thì skill dùng lại, không tạo mới).
- Ảnh tham chiếu người thật: Muse đôi khi thêm phụ kiện (dây chuyền, khuyên tai) — so với người thật trước khi dùng.
- File giao đã chuẩn hoá: H.264 30fps BT.709, cạnh ngắn ≤ 1080, không tiếng, không metadata / dấu phần mềm (kiểm bằng `selftest.py`).
- Cảnh không có gì dùng được → để `missing`, báo rõ; không lấy clip lạc nghĩa cho đủ số.
- Thêm nhiều clip vào kho bằng tay → `footage.py index` (lần sau `run` cũng tự cập nhật).
- Sửa script xong: `$F $S/selftest.py` (offline, phải ĐẠT).

## Môi trường

`~/.venvs/footage` (Python 3.12, torch CPU, open_clip `ViT-B-32 / laion2b_s34b_b79k`, Pillow, NumPy) — riêng, không đụng `video-skills` / `rvm` / `clearvoice`. Bóc lời dùng `~/.venvs/video-skills` (faster-whisper large-v3-turbo, mượn libcublas có sẵn; không GPU thì CPU). Cài lại: `uv venv ~/.venvs/footage --python 3.12 && uv pip install --python ~/.venvs/footage/bin/python torch torchvision --index-url https://download.pytorch.org/whl/cpu && uv pip install --python ~/.venvs/footage/bin/python open_clip_torch pillow numpy`.

<!-- ===== /file: auto-footage/SKILL.md ===== -->

<!-- ===== file: auto-footage/references/sources.md ===== -->

# Nguồn footage — API, giới hạn, giấy phép

Kiểm 2026-11-01. Mã nguồn tham khảo cho phần Pexels / Pixabay: `harry0703/MoneyPrinterTurbo` (MIT, `app/services/material.py`).

| Nguồn | Cách gọi | Key | Giới hạn | Giấy phép |
|---|---|---|---|---|
| Kho TNEDIT | chỉ mục CLIP `06_B-Roll/.footage_index/` (`index.json` + `index.npz`, 3 khung / clip) | — | — | theo `_nguon.json` / README danh mục từng thư mục |
| Pexels | `GET https://api.pexels.com/videos/search?query=&orientation=portrait&per_page=15`, header `Authorization: <key>` → `videos[].video_files[] {width, height, link}`, `image` (ảnh xem trước), `duration`, `user.name` | `PEXELS_API_KEY` (miễn phí, pexels.com/api) | 200 yêu cầu / giờ, 20.000 / tháng | Pexels License: miễn phí, dùng thương mại, không bắt ghi nguồn; không bán lại nguyên clip |
| Pixabay | `GET https://pixabay.com/api/videos/?key=&q=&per_page=20&safesearch=true` → `hits[].videos.{large,medium,small,tiny} {url, width, height, thumbnail}`, `duration`, `tags`, `user`, `pageURL` | `PIXABAY_API_KEY` (miễn phí, pixabay.com/api/docs) | 100 yêu cầu / 60 s; giữ kết quả 24 h | Pixabay Content License: miễn phí, dùng thương mại, không bắt ghi nguồn |
| Pexels ảnh | `GET https://api.pexels.com/v1/search?query=&orientation=portrait&per_page=15` → `photos[] {id, width, height, alt, photographer, src.{original, medium}}`; tải `original?auto=compress&cs=tinysrgb&h=2560` | `PEXELS_API_KEY` | như trên | Pexels License — **chưa chạy thật** (máy chưa có key; parser kiểm bằng dữ liệu mẫu) |
| Pixabay ảnh | `GET https://pixabay.com/api/?key=&q=&image_type=photo&orientation=vertical&per_page=20&safesearch=true` → `hits[] {webformatURL (640), largeImageURL (1280), imageWidth, imageHeight}` | `PIXABAY_API_KEY` | như trên | Pixabay Content License — **chưa chạy thật** |
| Mixkit | không có API: trang `https://mixkit.co/free-stock-video/<từ>/` (24 clip, chỉ 1 từ; trang tìm nhiều từ tải bằng JS nên không đọc được). Clip: `https://assets.mixkit.co/videos/<id>/<id>-1080.mp4` (hoặc `-720.mp4`), ảnh xem trước `<id>-thumb-360-0.jpg` | — | đọc ít (1–2 trang / cảnh); giao diện đổi → nguồn lỗi, bị bỏ qua | Mixkit Stock Video Free License: dùng thương mại, không bắt ghi nguồn |
| Muse | muse2api local `http://127.0.0.1:18610/v1` (khoá `~/.config/muse/env`): `POST /images/generations {model: muse-image, size: 9:16, async}` → `POST /videos {model: muse-video, seconds: 1–60, image: <data URL khung đầu>}`; hỏi tiến độ `GET …/<id>` | `MUSE_API_KEY` (đã có) | 2 tài khoản → chạy 2 việc / lần; ảnh ~30 s, video 5 s ~1–2 phút, 10 s ~2,3 phút, 30 s ~4,8 phút, 60 s ~7,5 phút (đo 2026-11-02); ra 720×1280 hoặc 704×1248 24fps có tiếng (skill bỏ tiếng, đổi 30fps; đặt lên timeline 1080×1920 cần phóng ~150%); ≥ 30 s bối cảnh trôi (đạo cụ / góc máy đổi dần); **video trả lại kết quả cũ khi prompt + độ dài trùng, kể cả khác ảnh khung đầu** (đo 2026-11-02: đoạn 6 trùng từng byte đoạn 2) → skill gắn `(shot <sha1 ảnh>)`; đôi khi không bám ảnh khung đầu (lệch 45/255) → kiểm + tạo lại | tạo bằng AI — xem kỹ trước khi dùng |

Ghi chú:
- Điểm CLIP ViT-B-32 (đã cộng thưởng hướng khung / kho) giữa câu tả và ảnh thường 0,20–0,37: kết quả đúng nghĩa đo được ≥ 0,28, lạc nghĩa ~0,24–0,25 → ngưỡng Muse 0,27 (đo 2026-11-01 trên THCN04).
- Ảnh xem trước Pexels / Pixabay là khung đại diện, có thể khác phần còn lại của clip: xem `sheet.jpg` (khung giữa clip đã tải).
- Lỗi tải không in URL có key (Pixabay đặt key trong URL): `media.http_get` chỉ báo phần trước `?`.

<!-- ===== /file: auto-footage/references/sources.md ===== -->
