# Thang kiểm loại F (phim 3D mascot)

Thang kiểm là danh sách 8 nấc phải qua trước khi giao (cổng G8). Làm đủ từng nấc. Nấc nào không làm được thì ghi **"chưa kiểm"**, không bỏ qua im lặng. Còn nấc "chưa kiểm" hay lỗi "cần sửa" thì giao là **bản nháp**.

**Đo trước, xem ảnh sau.** Lệnh chạy từ `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/OPA-Motion-graphic-mascot`. Trong lệnh: `F=film3d/films/<id>`, `O=$F/out`; `<clip>` là thư mục của job `clip` chất lượng cuối (ca mẫu bản 2: `v2-hq`; bản 1: `animatic-hq`, tên cũ từ lúc còn định làm animatic); `<ghép>` là bản ghép sạch (ca mẫu bản 2: `$O/v2-ghep/thu-mon-v2.mp4`). Lệnh Python luôn có `-X utf8` (xem bẫy ở SKILL.md mục 9).

Số "ca mẫu" là của phim Thủ môn bản 2, đo ngày 21–22/10/2026 (`FOLLOWUPS.md`, phần BẢN 2). Chỗ nào bản 2 không đo lại thì ghi rõ "bản 1".

## Nấc 1. Không lỗi trang, tất định, GPU thật

**Tất định** nghĩa là render lại ra đúng từng bit. Có nó thì mọi phép so trước/sau mới có nghĩa.

```bash
F=film3d/films/<id>; O=$F/out
# mọi job: không lỗi, GPU NVIDIA, bản Chrome đầu = cuối
python -X utf8 -c "import json,glob;[print(p,(m:=json.load(open(p,encoding='utf-8'))).get('error'),'NVIDIA' in (m.get('renderer') or ''),m.get('uaStart')==m.get('uaEnd')) for p in glob.glob('$O/**/render-meta.json',recursive=True)]"
# màu và hình của phim còn khớp nguồn (tokens.ts, geometry.json)
node node_modules/tsx/dist/cli.mjs film3d/brand-opa/export.ts --check
# tất định: 2 job "frames" giống hệt nhau (3 khung ở 3 đoạn phim, spp 16, scale 2), chỉ khác "out"
# ca mẫu bản 2: v2-tat-dinh-a.json, v2-tat-dinh-b.json → $O/v2-hq/qa/tat-dinh-a, tat-dinh-b
python -I -X utf8 tools/film3d/render.py job $F/jobs/v2-tat-dinh-a.json
python -I -X utf8 tools/film3d/render.py job $F/jobs/v2-tat-dinh-b.json
cd $O/v2-hq/qa && sha256sum tat-dinh-a/*.png tat-dinh-b/*.png > tat-dinh-sha256.txt
for f in tat-dinh-a/*.png; do cmp -s "$f" "tat-dinh-b/${f#tat-dinh-a/}" && echo "trùng $f" || echo "KHÁC $f"; done
```

| Đạt khi | Ca mẫu |
|---|---|
| Mọi dòng: `None True True` | Đạt. GPU `ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 Ti ... Direct3D11 ...)`, `HeadlessChrome/156.0.0.0` đầu = cuối |
| `export.ts --check` in "brand.js khớp nguồn" | Đạt |
| Cả hình lẫn mặt nạ của 3 khung trùng SHA-256 giữa 2 lần, 2 tiến trình Chrome | Đạt: khung 300, 600, 900 (`$O/v2-hq/qa/tat-dinh-sha256.txt`) |

## Nấc 2. 24 khung + dải 5 khung quanh mọi nhịp chạm

- **24 khung** chất lượng cuối, ghép 4 tờ × 6 ô: rải đều theo thời gian, cộng các nhịp chạm. Lấy bằng job `frames` (vài giây) hoặc cắt từ `$O/<clip>/clip.mkv`. Ca mẫu ghép bằng script tạm; chưa có script riêng (ứng viên thu hoạch).
- **Nhịp chạm** đọc từ `$O/events.json` (job `events`). Ca mẫu bản 2 có `kind`: appear, launch, catch, land, card, bob, snort, jump, ff, ff-end, dawn, strike, flood, lock (bản 1 có thêm startle, teeter, hold).
- **Dải 5 khung** f−2 … f+2 quanh mỗi nhịp f, cắt từ FFV1:

```bash
ffmpeg -v error -y -i $O/<clip>/clip.mkv -vf "select='between(n\,178\,182)',scale=640:-1,tile=5x1" -frames:v 1 $O/<clip>/qa/dai-f0180.png   # nhịp f = 180 (hứng tin 1, bản 2)
```

- **Đoạn vật dồn dập** (nhiều vật bay cùng lúc, mascot nhảy): soát **mọi khung** của đoạn, không chỉ dải 5 khung. Ca mẫu bản 2: lỗi bắt buộc B1 nằm giữa hai nhịp; sau khi sửa, soát 79 khung 6,00–7,30 s, hai tin gần nhau nhất còn cách 7 px.
- **Tờ mỗi 0,5 s trên bản ghép có chữ** (một phách ở 120 BPM):

```bash
python -X utf8 tools/v2w/contact.py <ghép> --t0 0 --every 0.5 --cols 4 --out $O/<clip>/qa/contact-0.5s-co-chu.png
```

Xem bằng Read **sau** khi đã có số đo của nấc 3–5. Chỗ nghi ngờ thì phóng to ở độ phân giải gốc. Đạt khi không còn lỗi "cần sửa" trên tờ và dải.
- Ca mẫu bản 2: tờ 0,25 s `out/v2-hq/qa/to-khung-025.png`, dải quanh nhịp `dai-nhip.png` (script tạm, chưa có trong dự án). Đạt sau rà chéo vòng 1.
- Bản 1: đạt sau khi sửa lỗi 8 (thẻ bay xuyên cánh chữ U) và lỗi rà chéo số 1 (bóng lơ lửng: dải `land-3` đã có lỗi này nhưng lần đầu bị đọc nhầm).

## Nấc 3. Mascot: màu, hình, cắt mép, luật đêm

**Màu.** Job `clip` khai báo `maskFrames` (các khung có mặt nạ). Đo trên **bản đã ghép chữ**, vì màu đổi sau mỗi lần nén:

```bash
python -I -X utf8 tools/film3d/qa.py video <ghép> $O/<clip> --table
```

- Mặt trước = vùng có pháp tuyến hướng thẳng ra máy, co vào 3 px. Đo trung vị ΔE2000 so với màu token.
- **Đạt** ≤ 2; **cần sửa** 2–3 nếu kéo dài quá 0,5 s; **hỏng** > 3. Cột ±4 (tỉ lệ điểm ảnh lệch ≤ 4 mức mỗi kênh) chỉ để báo kèm.
- Khung mascot ra ngoài khung báo "chưa đo": bình thường.
- Mascot trắng (khung cầu sang end card) tự đo theo màu trắng: job ghi `cfg.color` cho từng khung.
- Ca mẫu bản 2: 20/20 khung đạt (#0067FF, lệch 0,34; khung cuối Bò trắng #FFFFFF). Bản 1: 19/19 khung có Bò đạt; khung 760 Bò nằm ngoài khung nên "chưa đo".
- Cả hai bản mới đo 20 khung chọn tay. Phương án muốn mỗi 5 khung + 5 khung quanh mỗi nhịp, nên phim sau thêm `maskFrames`.

**Hình.** Chạy lại mỗi khi sửa `lib/mascot3d.js`:

```bash
python -I -X utf8 tools/film3d/render.py job film3d/films/look-test/jobs/shape.json
python -I -X utf8 tools/film3d/qa.py shape film3d/films/look-test/out/shape/coverage.png
```

So ảnh phủ chính diện (máy chiếu song song, 64 lệch dưới điểm ảnh) với kênh trong suốt của logo PNG gốc 2000 px. **IoU** là phần trùng chia phần hợp của hai hình. Đạt khi IoU ≥ 0,999 và lệch viền tối đa ≤ 1 px. Ca mẫu: IoU 0,99968, lệch tối đa 0,722 px.

**Cắt mép.**

```bash
python -I -X utf8 tools/film3d/render.py job $F/jobs/v2-boxes.json   # ghi $O/v2-hq/qa/boxes.json
python -I -X utf8 tools/film3d/qa.py boxes $O/v2-hq/qa/boxes.json     # bản 2 không có cận cố ý nên không cần --allow
# bản 1 có 2 khoảng cố ý: qa.py boxes $O/boxes.json --allow 6.55:7.65,12.30:12.95
```

- Ngọn sừng cách mép khung ≥ 24 px (chạm mép trông như bị cắt). Thân mascot chỉ được ra khỏi khung trong các khoảng `--allow`.
- `--allow` lấy đúng các đoạn storyboard ghi "cố ý", nới vài khung hai đầu.
- Đạt khi `"pass": true`. Ca mẫu bản 2: đạt, không sừng hay thân nào ra khỏi khung. Bản 1: chỉ ra ngoài ở cận ngọn sừng 6,58–7,62 s và cú lia sang CRM 12,43–12,85 s.
- `boxes` chỉ đo mascot và hai sừng. Vật chính khác (đồng hồ, nhãn) soát bằng mắt ở nấc 2.

**Luật đêm.** Cột "nền sau Bò" trong bảng `qa.py video`: độ sáng trung vị của vòng nền 6–20 px quanh mascot. Cảnh đêm, mascot xanh: trung vị phải gần 1,0 (nền ngay sau là vật sáng). Chưa có ngưỡng số chính thức. Bản 1: 1,00. Bản 2: đáy chữ U đứng trước mặt bàn tối, chiếm 16–26 % vòng nền; bản 1 cũng vậy. Để ngỏ: muốn hết thì thêm đế trắng dưới Bò hoặc hạ máy.

## Nấc 4. Không xuyên vật, không lơ lửng; khung đứng; cú cắt 3D → 2D

**Xuyên vật, lơ lửng, chồng vật.** v0 chưa có kiểm tự động (cách đo bằng trường khoảng cách của lane T mới là thiết kế). Soát bằng mắt trên dải 5 khung ở nấc 2, phóng 3× chỗ vật lọt khe; đoạn dồn dập thì soát mọi khung. Ghi rõ "soát bằng mắt".

**Khung đứng** (chống nhàm), đo trên bản ghép chất lượng cuối, không đo trên bản nháp 1 mẫu:

```bash
python -X utf8 tools/v2w/metrics.py <ghép> --declared 15.95:16.05 --json $O/v2-ghep/qa/chuyen-dong.json --md $O/v2-ghep/qa/chuyen-dong.md   # cú cắt của ca mẫu ở 16,0 s
```

- Điểm ảnh **đổi** khi lệch > 6 mức (ảnh xám 960×540). **Tĩnh B** = khung có ≤ 0,5 % điểm ảnh đổi so với 1/30 s trước. **Tĩnh A** = ≤ 0,04 %. **Cắt cứng** = khung có > 30 % điểm đổi so với khung ngay trước, trong khi khung trước và khung sau đổi chưa tới 1/3 mức đó.
- **Trượt khi:** ô 2 s có Tĩnh B > 15 % (ô chạm khoảng khai báo: bỏ các khung khai báo rồi mới xét 15 %, và cả ô không quá 30 %); cả đoạn > 10 %; Tĩnh A > 0; chuỗi Tĩnh B dài hơn 12 khung (0,2 s); có cắt cứng.
- `--declared a:b`: khoảng lặng có chủ ý (ca mẫu: 1 khung quanh cú cắt 16,0 s). `--exempt a:b`: miễn hẳn (khung CTA cuối, nếu cần).
- Exit 0 đạt, 1 trượt. Ca mẫu bản 2: Tĩnh B 1,04 %, Tĩnh A 0, chuỗi dài nhất 9 khung, cắt cứng 0. Bản 1: 1,68 %, chuỗi 10 khung.
- **Nền phẳng** cho ít điểm ảnh đổi hơn hẳn phòng có đèn, với cùng một chuyển động. Bản 2 lúc đầu có 42 % khung gần đứng ở phần 3D. Nên đo riêng phần 3D (`metrics.py $O/<clip>/clip.mp4`) trước khi ghép chữ, để biết hình tự đủ động chưa (bản 2 sau sửa: 4,4 %), rồi mới đo bản ghép.
- **Cắt cứng giả ở chuyển màu nền chậm.** Đường cong êm (ease 0,65–0,75 s) có đoạn giữa đổi gần 6 mức mỗi khung, sát ngưỡng "đổi". Nhiễu H.264 ±2 mức đẩy vài khung lẻ vượt ngưỡng trên > 30 % khung (nền chiếm gần hết khung), nên bị đếm là cắt cứng. Chuyển đều thì bước mỗi khung xa ngưỡng (bản 2: rạng sáng 0,97 s tuyến tính, ~3,5 mức mỗi khung, 0 cắt cứng).
- **Độ đều** (Minh chê bản 1 "lúc nhanh lúc chậm"): `metrics.py` chỉ bắt chỗ đứng, không bắt chỗ dồn dập. Ca mẫu đo thêm độ chuyển động trung bình mỗi 0,5 s bằng script tạm (`$O/v2-ghep/qa/nhip-chuyen-dong.json`): ô động nhất gấp ô lặng nhất 4,8 lần ở bản 2, 56 lần ở bản 1. Chưa có ngưỡng chính thức.

**Cú cắt 3D → 2D.** Lấy khung 3D cuối và khung đầu end card (ca mẫu: 959 và 960):

```bash
ffmpeg -v error -y -i $O/<clip>/clip.mkv -vf "select=eq(n\,959)" -frames:v 1 $O/v2-ghep/lock/hq-f0959.png
ffmpeg -v error -y -i $O/overlay/<id>-overlay.mov -vf "select=eq(n\,960),scale=in_color_matrix=bt709:in_range=tv,format=rgb24" -frames:v 1 $O/v2-ghep/lock/endcard-f0960.png
python -I -X utf8 tools/film3d/qa.py lock $O/v2-ghep/lock/hq-f0959.png $O/v2-ghep/lock/endcard-f0960.png
```

Đạt khi `edgeMaxPx` ≤ 2 (lệch viền lớn nhất giữa bóng mascot trắng của hai khung). Ca mẫu bản 2: 1,048 px (`$O/v2-ghep/qa/cu-cat.json`); bản 1 cũng 1,05 px.

## Nấc 5. Chữ

- **Luật của Minh:** viết hoa chữ cái đầu mọi dòng; cụm nhấn Fraunces Italic 800 + khối đánh dấu; dấu tiếng Việt đủ, không vỡ; tối đa 7–9 chữ mỗi khung; mỗi nhóm đứng ≥ 1,8 s (file `<phim>Plan.ts` tự báo lỗi nếu ngắn hơn).
- **Lint code lớp phủ** (cấm mã màu viết tay, chữ tiếng Việt nằm trong code thay vì file lời, `Math.random`...):

```bash
python -X utf8 tools/v2w/lint_v2w.py src/film3d
```

  Đạt khi "0 vi phạm". Ca mẫu: 0 vi phạm ở cả hai bản.
- **Độ phủ chữ** (Minh chê bản 1 "chữ không dàn trải"): tính từ mốc hiện và mốc rút của từng nhóm trong `<phim>Plan.ts`. Đạt khi chữ phủ ≥ 65 % phần 3D và khoảng trống giữa hai nhóm ≤ 0,6 s. Ca mẫu bản 2: 80 % (12,8 / 16 s), trống dài nhất 0,52 s. Bản 1: chữ chỉ hiện 6,2 / 16 s.
- **Tương phản chữ trên nền 3D:**

```bash
python -I -X utf8 tools/film3d/qa.py text $O/<clip>/clip.mkv $O/overlay/<id>-overlay.mov --step 3 --table
```

  Trong khung bao vùng chữ (nới 16 px), lấy nền 3D xấu nhất (phân vị 99,5 với chữ trắng, 0,5 với chữ đen), so với màu chữ theo công thức tương phản WCAG. Đạt khi ≥ 4,5 : 1 ở mọi khung có chữ (exit 0, "trượt 0"). Ca mẫu bản 2: chữ đêm thấp nhất 9,84 : 1. Bản 1: 15,9 : 1 trên 122 khung.
- **Chữ có tấm nền riêng** (khung trắng, khối nhấn xanh, như câu chốt kiểu V2): `qa.py text` coi tấm nền là "màu chữ" rồi so với nền 3D, nên báo động giả (bản 2: câu chốt báo 1,0 : 1). Đo cục bộ thay: trên bản ghép, trong khung bao từng dòng, tách nét chữ khỏi nền ngay quanh nét bằng ngưỡng Otsu theo độ sáng, rồi tính tương phản WCAG giữa hai màu đó. Ca mẫu bản 2: chữ trắng trên khối #0068FF 4,70 : 1 (lý thuyết 4,75 : 1, nên khối nhấn xanh chỉ vừa đủ); chữ đen trong khung trắng 19,8 : 1. Chưa có lệnh trong dự án (ca mẫu dùng script tạm); nên sửa `qa.py text` để lần sau không chặn nhầm.

## Nấc 6. Âm thanh

Cách dựng, chọn SFX, đặt mức: `references/audio.md`. Bộ script là riêng từng phim (ca mẫu: `tools/audio/score_thumon_*.py`); phim mới chép rồi đổi bảng cue.

```bash
python -X utf8 tools/audio/score_thumon_cues.py --check   # cue sheet còn khớp events.json, timeline.js không
python -X utf8 tools/audio/score_thumon_qa.py             # QA bản âm tổng hợp, ảnh phổ → $O/g6-am/ban2/qa/audio.md
python -X utf8 tools/audio/score_thumon_regress.py        # V2, V3 dựng lại vẫn trùng md5
# bản âm thư viện: số đo in ra màn hình và ghi vào $O/g6-am/thu-vien/bao-cao.json (master, loa điện thoại, từng âm, từng MP4)
python -X utf8 tools/audio/score_thumon_thuvien.py --target-i -16 --video <ghép> --out <bản −16.mp4> --out-14 <bản −14.mp4>
```

| Mục | Ngưỡng | Ca mẫu bản 2 (âm thư viện) |
|---|---|---|
| Độ to tích hợp | file chính −16 LUFS (như V2, V3); bản đăng mạng xã hội −14 LUFS; lệch ≤ 0,5 | −16,1 và −14,1 trên MP4; master WAV −16,0 |
| True peak | ≤ −2 dBTP trên WAV master và trên MP4 −14 (chừa chỗ cho bộ nén AAC) | −2,0 trên WAV; −5,0 trên MP4 −16 (master mono tách 2 kênh, mỗi kênh −3 dB, độ to cảm nhận không đổi); −2,9 trên MP4 −14 |
| Đoạn to nhất (short-term 3 s) | ≤ đích + 5 LU | −13,9 và −11,9 |
| Đồng bộ | va chạm đạt đỉnh 1 khung (16,7 ms) sau hình; không âm nào sớm hơn hình | mọi âm đặt đúng tới từng mẫu theo mốc của cue sheet; âm trong MP4 lệch WAV 0 mẫu tại 5 cú chạm (script tạm) |
| Lệch thời lượng hình–tiếng | < 1 khung | hình và tiếng đều 21,000 s |
| Loa điện thoại | logo qua giả lập (HPF 500 Hz + LPF 8 kHz) to ít nhất bằng đoạn đuổi (momentary max) | logo hơn đoạn đuổi 0,7 dB |
| QA âm tổng (bản âm tổng hợp, `score_thumon_qa.py`) | 0 trượt; lệch va chạm trung vị 16,7 ± 2 ms, từng tiếng 8–25 ms, < 0 hoặc > 33 ms là hỏng | 103 đạt, 0 trượt, 5 cảnh báo (bản 1: 133 đạt, trung vị 16,67 ms) |

Đo nhanh độ to trên bất kỳ MP4 có tiếng:

```bash
ffmpeg -hide_banner -nostats -i <file.mp4> -filter_complex ebur128=peak=true -f null - 2>&1 | grep -E "^ +(I|LRA|Peak):"
```

Opus không nghe được: ghi **"CHƯA NGHE BẰNG TAI"** cho tới khi Minh nghe bản chính và bộ A/B. Ca mẫu: Minh nghe bản 1 ngày 19/10 (giữ phương án A cả ba nhóm), duyệt âm tổng hợp bản 2 ngày 21/10, rồi chọn âm thư viện ngày 22/10. Âm chưa rà chéo bằng agent riêng; chưa nghe trên điện thoại thật.

## Nấc 7. Rà chéo bằng agent mới

- Mở một agent mới, chạy nền, chưa đọc gì của phim (ngữ cảnh sạch).
- Đầu vào: bản ghép, `PROMPT-PACK.md`, 4 tờ khung, các dải khung, tờ 0,5 s, bảng số đo nấc 1–5, báo cáo âm. Không đưa kết luận tự soát (`FOLLOWUPS.md`) trước, để người rà nhìn bằng mắt mới; đối chiếu mục "Để ngỏ, có lý do" sau, lúc xếp mức.
- Việc: so phim với storyboard từng dòng; tìm lỗi mắt người thấy mà số không bắt (xuyên vật, lơ lửng, diễn không đọc ra, chữ sai luật); chấm điểm 4 mục: không nhàm, thương hiệu, chữ, rõ chuyện; xếp mức "bắt buộc / nên sửa / để ngỏ"; lưu ảnh bằng chứng vào `$O/g8-thang-kiem/ra-cheo/`.
- Sửa xong thì đo lại toàn bộ nấc 1–5 trên bản mới.
- **Vòng 2:** gửi lại đúng người rà vòng 1 (SendMessage), kèm bản mới và bảng đã sửa. Người rà soát lại từng lỗi đã nêu và tìm lỗi mới. Dừng khi không còn lỗi "bắt buộc" hay "nên sửa" mới.
- Ca mẫu bản 2 (hình và chữ; báo cáo `$O/v2-ghep/ra-cheo/bao-cao.md`, `bao-cao-vong-2.md`):
  - vòng 1: điểm 7 · 8,5 · 8,5 · 7,5; 1 lỗi bắt buộc (tin chồng nhau, cắm vào vai khe khi Bò nhảy, 6,10–7,12 s) + 4 lỗi nên sửa (chữ giật do bước ghép, vệt tối trên vùng xanh, bảng CRM quá nhỏ, Bò gần đứng 12,0–14,5 s);
  - vòng 2: 7,5 · 9 · 9 · 8,5, "phần hình giao được".
- Bản 1: vòng 1 điểm 8,5 · 9 · 8,5 · 7; 1 lỗi bắt buộc (bóng lơ lửng, tự soát đã đọc nhầm) + 7 lỗi nên sửa.
- Âm chưa rà chéo bằng agent riêng ở cả hai bản: Minh nghe thay.

## Nấc 8. Đo lại trên file giao

```bash
ffprobe -v error -show_entries stream=codec_name,profile,pix_fmt,width,height,r_frame_rate,nb_frames,color_range,color_space,color_primaries,color_transfer -of default=nw=1 <file giao.mp4>
ffprobe -v error -show_entries stream=codec_type,duration -of csv=p=0 <file giao.mp4>
python -I -X utf8 tools/film3d/qa.py video <file giao.mp4> $O/<clip> --table
# mux chỉ thay tiếng: luồng hình của bản giao sạch và bản −14 phải trùng md5 với bản ghép
ffmpeg -v error -i <file giao.mp4> -map 0:v -c copy -f md5 -
ffmpeg -v error -i <ghép> -map 0:v -c copy -f md5 -
```

| Đạt khi | |
|---|---|
| Hình | h264 High, yuv420p, 1920×1080, 60/1, `tv`, bt709 ở cả 3 nhãn màu; đủ số khung (ca mẫu: 1260 = 21,0 s) |
| Tiếng | aac; thời lượng hình và tiếng lệch < 1 khung (16,7 ms) |
| Luồng hình | bản giao sạch và bản −14 trùng md5 luồng hình với bản ghép |
| Màu | như nấc 3, trên chính file giao |
| Độ to | như nấc 6, trên chính file giao, cả bản −16 lẫn bản −14 |
| Chống nhàm | `metrics.py` như nấc 4, trên chính file giao |

Ca mẫu bản 2: đạt trên `out/thu-mon-3d-16x9-ban2/thu-mon-3d_16x9_ban2.mp4` (gốc dự án):
- màu 20/20 khung; khung đứng đạt; cú cắt 1,05 px; hình và tiếng đều 21,000 s;
- −16,1 LUFS; bản `_-14LUFS.mp4`: −14,1 LUFS, true peak −2,9 dBTP;
- bản sạch, bản −14 và `film3d/films/thu-mon/out/v2-ghep/thu-mon-v2.mp4` cùng md5 luồng hình `316cd4274dd4c76f23cc80a50a74e8ac`.

Thư mục giao còn có bản có giờ phim, ảnh bìa, tờ khung mỗi 1 s và 0,5 s, `metrics.md` đo trên file giao, `README.md` ghi cách dựng lại và những gì chưa kiểm.

## Mẫu báo cáo

Ghi vào `FOLLOWUPS.md`, mục "Thang kiểm loại F (G8)":

| Nấc | Nội dung | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | Không lỗi trang, tất định, GPU thật | Đạt / Trượt / Chưa kiểm | file, số |
| ... | | | |

Gọi đúng tên phần đã làm: "tự kiểm" hay "rà chéo bằng agent". Không viết "đã kiểm" cho phần chưa chạy lệnh.
