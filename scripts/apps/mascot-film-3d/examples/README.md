# Ca mẫu: phim 3D Bò OPA "Thủ môn" (bản 2)

File này chỉ trỏ tới ca mẫu trong dự án OPA. Không chép code vào skill: code sống ở dự án, skill chỉ ghi cách dùng.

## Tóm tắt

- **Dự án:** `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/OPA-Motion-graphic-mascot` (gọi tắt `<OPA>`).
- **Mạch truyện:** khách nhắn lúc đêm → AI của OPA trực, hứng hết từng tin → ghi lại, trả lời ngay → sáng ra không bỏ sót khách nào → nhắn OPA.
- **Phim:**
  - 22:47, nền đêm #003C99 phẳng. Tin nhắn khách (đúng biểu tượng tin nhắn V2) bật ra từ chiếc điện thoại khổng lồ.
  - Bò OPA hứng từng tin qua khe trán, đúng phách nhạc 120 BPM. Mỗi tin thành thẻ khách, sang bảng CRM.
  - Tua cả đêm, trời sáng. "Bỏ sót khách" bị gạch đúng lúc Bò hứng tin buổi sáng → "Không bỏ sót khách".
  - Vùng xanh tràn từ lòng O, Bò chuyển trắng và khóa vào end card.
- **Khổ:** 21,0 s, 16:9, 60 fps. 3D từ 0–16 s (960 khung) + end card 2D từ 16–21 s (chương "trạm OPA" của V2).
- **Lịch sử:**
  - 19/10/2026: bản 1 qua G0–G8. Minh xem lại, chê 5 điều; không đăng.
  - 21/10: Minh duyệt hướng sửa (`DE-XUAT-V2.md`), rồi xem, nghe và duyệt bản 2.
  - 22/10: Minh chọn âm từ thư viện SFX; chốt đăng mạng xã hội bằng bản −14 LUFS.
  - 23/10: BRAND-SPEC mục 9 cập nhật phần âm. Còn chờ Hùng duyệt đăng.
- **Chưa kiểm:** rà chéo riêng cho âm (Minh nghe thay); xem trên màn điện thoại; nền tảng nén lại khi đăng.
- **Để ngỏ, có lý do** (chi tiết: `FOLLOWUPS.md` mục "Để ngỏ, có lý do"):
  - dải "độ chuyển động 1,5–8" của đề xuất không đạt theo nghĩa đen, vì nền phẳng làm số nhỏ đi ~10 lần;
  - ban đêm, đáy chữ U của Bò đứng trước mặt bàn tối;
  - CTA cuối đứng ~1,6 s cho 9 chữ (Minh giữ 21 s);
  - người rà nhận xét chữ trên bảng CRM có thể vẫn nhỏ khi xem trên điện thoại.

## File chính (đường dẫn tính từ `<OPA>`)

| Vai | File |
|---|---|
| Phương án, quyết định của Minh, lộ trình G0–G9 | `docs/film3d/phuong-an-phim-3d.md` |
| Thử look G1 | `docs/film3d/g1-thu-look.md`; tờ so sánh `film3d/films/look-test/out/G1-to-so-sanh.png` |
| 5 lời chê bản 1 → việc đo được → kịch bản bản 2 | `film3d/films/thu-mon/DE-XUAT-V2.md`; tờ một trang `film3d/films/thu-mon/out/thu-v2/de-xuat-v2.png` |
| Kịch bản 6 khối + storyboard theo giây | `film3d/films/thu-mon/PROMPT-PACK.md` (bản 1: `PROMPT-PACK.ban1.md`) |
| Tự soát, rà chéo 2 vòng, thang kiểm | `film3d/films/thu-mon/FOLLOWUPS.md` (bản 2 ở đầu); báo cáo người rà `film3d/films/thu-mon/out/v2-ghep/ra-cheo/` |
| Bản giao, cách dựng lại, đã kiểm gì | `out/thu-mon-3d-16x9-ban2/README.md` |
| Âm thư viện (âm chính thức): âm từng mốc, mức, số đo | `docs/film3d/am-thu-vien/README.md`; `tools/audio/score_thumon_thuvien.py`; `src/audio/cues/thu-mon.thuvien.json` |
| Nghiên cứu decibel; danh mục đo thư viện SFX | `docs/film3d/am-thu-vien/nghien-cuu-decibel.md`; `docs/film3d/am-thu-vien/danh-muc-sfx.csv` (dựng bằng `tools/audio/sfx_catalog.py`) |
| Nhạc nền và âm tổng hợp | `docs/film3d/g6-am-thanh.md`; `tools/audio/score_thumon_{cues,build,music,sfx,qa}.py`; `src/audio/cues/thu-mon.json`, `.csv` |
| Luật phim 3D (mục 9) | `BRAND-SPEC.md` |
| Trang phim, hai chế độ (job, xem) | `film3d/films/thu-mon/film.html`, `main.js` |
| Timeline thuần: `BEATS`, `EVENTS`, `poseAt(t)`, đường bay tin, máy quay, cầu 3D → 2D | `film3d/films/thu-mon/timeline.js` (chỉ còn bản 2) |
| Các job bản 2 | `film3d/films/thu-mon/jobs/`: `v2-hq`, `v2-boxes`, `v2-tat-dinh-a/b`, `events`, `thu-v2-*`, `look-v2` |
| Thế giới bàn đêm → ngày, nền phẳng hoặc phòng có đèn (riêng phim này) | `film3d/lib/world-desk.js` |
| Mascot 3D, look A/B/C/C2, mặt nạ | `film3d/lib/mascot3d.js` |
| Tích lũy mẫu, hoàn thiện | `film3d/lib/accum.js` |
| Gửi khung qua WebSocket | `film3d/lib/wire.js` |
| Random có seed; đường cong theo thời gian | `film3d/lib/rng.js`, `film3d/lib/rig.js` |
| Màu, hình từ nguồn sự thật | `film3d/brand-opa/export.ts` → `brand.js` |
| Thư viện ghim + SHA-256 | `film3d/vendor/SOURCE.md` |
| Lớp phủ chữ + end card (Remotion) | `src/film3d/ThuMonOverlay.tsx`, `thuMonPlan.ts`, `ThesisW.tsx` (câu chốt), `textColumn.ts`, `compositions.tsx` |
| Khung khóa cho cú cắt | `src/film3d/exportEndcardBo.ts` → `film3d/films/thu-mon/out/endcard-bo.json` |
| Render, xem, ghép | `tools/film3d/render.py` |
| Đo | `tools/film3d/qa.py`, `tools/film3d/crop_base.py`, `tools/v2w/metrics.py`, `tools/v2w/contact.py`, `tools/v2w/lint_v2w.py` |

## Đầu ra bản 2 (`film3d/films/thu-mon/out/`)

| Thư mục, file | Chứa |
|---|---|
| `v2-hq/` | **Bản 3D chất lượng cuối** (16 mẫu, 2×): `clip.mkv` FFV1 ~1,1 GB, `clip.mp4`, 20 mặt nạ đo màu. `qa/`: tất định, `boxes.json`, tờ khung 0,25 s, dải nhịp, đo chuyển động riêng phần 3D |
| `overlay/` | `thu-mon-overlay.mov` (ProRes 4444, 21 s), nay là lớp chữ bản 2 |
| `v2-ghep/` | `thu-mon-v2.mp4` (sạch), `thu-mon-v2-gio.mp4` (có giờ phim); `qa/` (màu, chuyển động, cú cắt, tương phản chữ, nhịp); `lock/`; `ra-cheo/` (báo cáo 2 vòng, ảnh bằng chứng) |
| `thu-v2/` | Ảnh cho đề xuất bản 2: trước/sau (`cu/`, `moi/`), đường bay (`bay/`), tờ đề xuất, biểu đồ nhịp bản 1 |
| `look-v2/` | Ảnh thử look nền phẳng: đêm, ngày, khung chữ |
| `g6-am/ban2/` | Nhạc nền + âm tổng hợp bản 2: `stem/music.wav` (nhạc dùng cho bản thư viện), master, `qa/` |
| `g6-am/thu-vien/` | Âm thư viện: `sfx.wav`, `mix.wav`, `master.wav`, `bao-cao.json` |
| `events.json`, `endcard-bo.json` | Sự kiện bản 2 cho âm; khung khóa |
| `<OPA>/out/thu-mon-3d-16x9-ban2/` | **Bản giao**: MP4 −16 LUFS, MP4 −14 LUFS (đăng mạng xã hội), MP4 có giờ phim, ảnh bìa (khung 12,40 s), tờ khung 1 s và 0,5 s, `metrics.md` đo trên file giao, `README.md`, `luu-tru/` (bản âm tổng hợp). Bản sao bản sạch: `<OPA>/out/thu-mon-3d_16x9.mp4` |

## Dựng lại bản 2

**Cảnh báo:** các lệnh dưới đây ghi đè đầu ra bản 2 trong `film3d/films/thu-mon/out/` và bản giao Minh đã duyệt trong `out/thu-mon-3d-16x9-ban2/`. Muốn giữ thì chép ra chỗ khác trước, hoặc đổi đường ra.

Chạy trong Git Bash (công cụ Bash của Claude Code), từ `<OPA>`:

```bash
cd "/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/OPA-Motion-graphic-mascot"
F=film3d/films/thu-mon; O=$F/out; G=out/thu-mon-3d-16x9-ban2
# 0. màu, hình còn khớp nguồn (chỉ so, không ghi)
node node_modules/tsx/dist/cli.mjs film3d/brand-opa/export.ts --check
# 1. khung khóa từ end card (timeline.js đọc file này khi nạp)
node node_modules/tsx/dist/cli.mjs src/film3d/exportEndcardBo.ts
# 2. sự kiện cho âm; khung chiếu cho kiểm cắt mép (vài giây mỗi job)
python -I -X utf8 tools/film3d/render.py job $F/jobs/events.json
python -I -X utf8 tools/film3d/render.py job $F/jobs/v2-boxes.json
# 3. phần 3D chất lượng cuối: ~105 s render + ~17 s mã hóa
python -I -X utf8 tools/film3d/render.py job $F/jobs/v2-hq.json
# 4. lớp phủ chữ + end card
python tools/remotion_run.py render film3d-thu-mon-overlay $O/overlay/thu-mon-overlay.mov --codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png --muted
# 5. ghép: bản sạch và bản có giờ phim
python -I -X utf8 tools/film3d/render.py compose $O/v2-hq/clip.mkv $O/overlay/thu-mon-overlay.mov $O/v2-ghep/thu-mon-v2.mp4
python -I -X utf8 tools/film3d/render.py compose $O/v2-hq/clip.mkv $O/overlay/thu-mon-overlay.mov $O/v2-ghep/thu-mon-v2-gio.mp4 --timecode
# 6. đo (ngưỡng và cách đọc: references/qa-checklist.md)
python -I -X utf8 tools/film3d/qa.py video $O/v2-ghep/thu-mon-v2.mp4 $O/v2-hq --table
python -I -X utf8 tools/film3d/qa.py boxes $O/v2-hq/qa/boxes.json
python -X utf8 tools/v2w/metrics.py $O/v2-ghep/thu-mon-v2.mp4 --declared 15.95:16.05 --json $O/v2-ghep/qa/chuyen-dong.json --md $O/v2-ghep/qa/chuyen-dong.md
ffmpeg -v error -y -i $O/v2-hq/clip.mkv -vf "select=eq(n\,959)" -frames:v 1 $O/v2-ghep/lock/hq-f0959.png
ffmpeg -v error -y -i $O/overlay/thu-mon-overlay.mov -vf "select=eq(n\,960),scale=in_color_matrix=bt709:in_range=tv,format=rgb24" -frames:v 1 $O/v2-ghep/lock/endcard-f0960.png
python -I -X utf8 tools/film3d/qa.py lock $O/v2-ghep/lock/hq-f0959.png $O/v2-ghep/lock/endcard-f0960.png
python -I -X utf8 tools/film3d/qa.py text $O/v2-hq/clip.mkv $O/overlay/thu-mon-overlay.mov --step 3 --table   # câu chốt báo động giả: đo cục bộ, qa-checklist nấc 5
# 7. âm (references/audio.md): cue sheet → nhạc nền + âm tổng hợp → SFX thư viện, master, mux
python -X utf8 tools/audio/score_thumon_cues.py
python -X utf8 tools/audio/score_thumon_build.py
python -X utf8 tools/audio/score_thumon_thuvien.py --video $O/v2-ghep/thu-mon-v2-gio.mp4 --out $G/thu-mon-3d_16x9_ban2_gio-phim.mp4
python -X utf8 tools/audio/score_thumon_thuvien.py --video $O/v2-ghep/thu-mon-v2.mp4 --out $G/thu-mon-3d_16x9_ban2.mp4 --out-14 $G/thu-mon-3d_16x9_ban2_-14LUFS.mp4
cp $G/thu-mon-3d_16x9_ban2.mp4 out/thu-mon-3d_16x9.mp4
# 8. đo trên file giao: luồng hình phải trùng bản ghép; chuyển động, tờ khung, ảnh bìa
ffmpeg -v error -i $G/thu-mon-3d_16x9_ban2.mp4 -map 0:v -c copy -f md5 -
ffmpeg -v error -i $O/v2-ghep/thu-mon-v2.mp4 -map 0:v -c copy -f md5 -
python -X utf8 tools/v2w/metrics.py $G/thu-mon-3d_16x9_ban2.mp4 --declared 15.95:16.05 --json $G/metrics.json --md $G/metrics.md
python -X utf8 tools/v2w/contact.py $G/thu-mon-3d_16x9_ban2.mp4 --every 1 --out $G/contact_1s.png
python -X utf8 tools/v2w/contact.py $G/thu-mon-3d_16x9_ban2.mp4 --every 0.5 --out $G/contact_0.5s.png
ffmpeg -v error -y -i $G/thu-mon-3d_16x9_ban2.mp4 -vf "select=eq(n\,744),scale=in_color_matrix=bt709:in_range=tv,format=rgb24" -frames:v 1 $G/thu-mon-3d_16x9_ban2_cover.png
```

Kết quả đo phải ra như `FOLLOWUPS.md` (phần BẢN 2) và `docs/film3d/am-thu-vien/README.md`:
- **hình:** mặt trước #0067FF lệch 0,34 (20/20 khung); `boxes` pass, không cần `--allow`; Tĩnh B 1,04 %, chuỗi dài nhất 9 khung, 0 cắt cứng; `lock` 1,05 px; chữ đêm thấp nhất 9,84 : 1; câu chốt 4,70 : 1 (đo cục bộ);
- **âm:** master WAV −16,0 LUFS, true peak −2,0 dBTP; MP4 −16,1 LUFS, −5,0 dBTP; bản −14: −14,1 LUFS, −2,9 dBTP; logo qua giả lập loa điện thoại hơn đoạn đuổi 0,7 dB;
- **md5:** master thư viện `1331b5e5995a8486d6cc2c6109fac102`; master tổng hợp `188b92d360dfca5767b1c591a10728c6`; luồng hình của bản giao sạch và bản −14 là `316cd4274dd4c76f23cc80a50a74e8ac`, trùng `v2-ghep/thu-mon-v2.mp4`.

Xem một khung trong trình duyệt thường: `python -I -X utf8 tools/film3d/render.py serve`, rồi mở `http://127.0.0.1:8765/films/thu-mon/film.html?t=3.25`.

Thử look G1 (mỗi lệnh dưới 15 s):

```bash
python -I -X utf8 tools/film3d/render.py job film3d/films/look-test/jobs/stills.json
python -I -X utf8 tools/film3d/render.py job film3d/films/look-test/jobs/clip-C.json
python -I -X utf8 tools/film3d/qa.py brand film3d/films/look-test/out/stills --table
python -I -X utf8 film3d/films/look-test/make_sheet.py
```

## Bản 1 (19/10/2026, để tra)

- Kịch bản `film3d/films/thu-mon/PROMPT-PACK.ban1.md`; tự soát, rà chéo, thang kiểm ở `FOLLOWUPS.md` phần BẢN 1; mốc `film3d/films/thu-mon/out/events.ban1.json`; cue sheet `src/audio/cues/thu-mon.ban1.{json,csv}`.
- Hình trong `film3d/films/thu-mon/out/`: `animatic-hq/` (3D chất lượng cuối), `animatic/` (1 mẫu, chỉ để so tốc độ), `g2-duyet/` (bản ghép, tờ duyệt của `make_sheet.py`), `g4-tu-soat/`, `g8-thang-kiem/`, `keyframes/`, `lock/`, `tat-dinh/`, `thu-khung/`, `boxes.json`. Âm: `g6-am/`. Bản giao: `<OPA>/out/thu-mon-3d-16x9/`.
- **Mã `timeline.js` bản 1 đã mất** (dự án không có git), nên không dựng lại được bản 1.
- **Đừng chạy job cũ** (`animatic-hq`, `animatic`, `boxes`, `keyframes`, `lock`, `tat-dinh-a/b`, `thu-khung`): chúng nay vẽ bản 2 đè lên ảnh bản 1.

## Ghi chú cho lúc thu hoạch (G9)

- `render.py`, `qa.py`, `accum.js`, `wire.js`, `rng.js`, `rig.js`, `mascot3d.js` dùng chung được. Từ bản 2, `render.py compose` đưa mốc giờ về `settb=1/60,setpts=N`. Nên sửa `qa.py text` cho chữ có tấm nền riêng trước khi gói.
- `sfx_catalog.py` dùng chung được nguyên file.
- Bộ âm `tools/audio/score_thumon_*.py` gắn chặt với phim này (bảng cue, hợp âm, mốc end card, đoạn đo loa điện thoại). Gói cách làm (`references/audio.md`), không gói nguyên file.
- `world-desk.js` nằm trong `lib/` nhưng là thế giới riêng của Thủ môn (cả hai kiểu nền). Không gói vào template.
- `make_sheet.py` (tờ duyệt G2 bản 1) ghi cứng số đo và nhãn trong code. Phim sau nên đọc số từ file đo.
- Bản 2 còn làm bằng script tạm: tờ khung 0,25 s và dải nhịp; tương phản chữ đo cục bộ; độ đều nhịp mỗi 0,5 s; đối chiếu âm MP4 với WAV. Đây là các ứng viên script đầu tiên.
- `render.py` chưa chia chunk 120 khung; job hết giờ sau 900 s.

## Kết quả đối chiếu 6 câu thử (description, 19/10/2026)

Description không đổi ở lần cập nhật 23/10, nên kết quả dưới đây vẫn dùng được.

**Cách làm.** Đọc description của `mascot-film-3d` cạnh description các skill có thể tranh: `hyperframes`, `motion-director`, `video-production-lead`, `kinetic-reel`, `embedded-captions`, `remotion-best-practices`. Xét từng câu: từ nào khớp, skill nào hợp hơn. Đây là soát tay. Chưa thử trigger thật bằng một phiên mới.

**Đã kiểm thêm:**
- frontmatter parse được bằng `yaml.safe_load` (PyYAML 6.0.3): đủ `name`, `description`; description 863 ký tự (dưới mốc 1024);
- ngay sau khi ghi file, Claude Code liệt kê `mascot-film-3d` (kèm đủ description) trong danh sách skill của phiên đang chạy. Chưa thử mở Claude Code thẳng ở thư mục con `OPA-Motion-graphic-mascot` xem có thấy skill không.

| # | Câu | Mong muốn | Kết quả soát | Lý do |
|---|---|---|---|---|
| 1 | "phim 3D con trâu OPA" | vào skill | **Đạt**: vào | Khớp "phim hay video 3D có mascot"; description có nguyên ví dụ "phim 3D con trâu OPA" |
| 2 | "chạy prompt pack này" | vào skill | **Đạt**: vào | Khớp "bảo chạy một prompt pack kiểu này"; câu nằm nguyên trong description |
| 3 | "video giới thiệu OPA" | không vào | **Đạt**: không vào | Không có "3D"; description loại "video giới thiệu, promo hay explainer 2D". Đi `video-production-lead` (loại C) hoặc `motion-director` |
| 4 | "thêm phụ đề" | không vào | **Đạt**: không vào | Description loại "thêm phụ đề". Đi `video-production-lead` hoặc `embedded-captions` |
| 5 | "kinetic reel" | không vào | **Đạt**: không vào | Description loại "kinetic reel"; skill `kinetic-reel` khớp đúng tên |
| 6 | "sửa con Bò OPA 2D trong video V3" (tự chọn: có từ khóa "Bò OPA" nhưng là 2D) | không vào | **Đạt**: không vào | Description loại "mascot 2D trong Remotion (V2, V3)". Đi `video-production-lead` (loại E) |

**Rủi ro còn lại:**
- `hyperframes` tự nhận là "cửa vào bắt buộc" cho mọi yêu cầu video. Câu 1 vẫn có thể bị nó giành. Nếu gặp, gọi thẳng `/mascot-film-3d`.
- Câu 2 phụ thuộc ngữ cảnh: nếu thứ được đưa không phải prompt pack 6 khối (ví dụ gói `opa-chatbot-pack` cùng thư mục motion), skill phải nhận ra và nhả việc.
- Câu mép chưa thử: "logo OPA xoay 3D trên landing page" (three.js tương tác, không ra MP4). Description ghi "phim ngắn ... ffmpeg ra MP4", nên dự kiến không vào.
