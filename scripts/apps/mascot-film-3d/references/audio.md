# Âm thanh (G6): nhạc nền, SFX thư viện, đặt mức, hai bản −16 và −14 LUFS

Âm của phim 3D mascot dựng bằng script Python trong `<OPA>\tools\audio\`, không dùng phần mềm dựng âm. Mốc âm lấy từ `EVENTS` của `timeline.js` (qua `events.json`), nên hình và âm luôn khớp. `<OPA>` = `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/OPA-Motion-graphic-mascot`; lệnh chạy từ thư mục này.

Ca mẫu: phim Thủ môn bản 2. Nhạc nền tự tổng hợp; SFX lấy từ thư viện của Minh. Minh nghe và chọn bản này ngày 22/10/2026; bản SFX tự tổng hợp lưu lại để tra.
- Âm từng mốc, mức, số đo: `<OPA>\docs\film3d\am-thu-vien\README.md`.
- Nhạc nền và SFX tổng hợp (hợp âm, nhạc cụ, duck, lặng trước logo): `<OPA>\docs\film3d\g6-am-thanh.md`.
- Số liệu decibel có nguồn: `<OPA>\docs\film3d\am-thu-vien\nghien-cuu-decibel.md`.

## 1. Luật (BRAND-SPEC mục 9, Minh chốt 23/10/2026)

- Master mono 48 kHz 24-bit, −16 LUFS như V2, V3. True peak ≤ −2 dBTP.
- Bản đăng mạng xã hội −14 LUFS: cộng +2 dB ở bước ra stereo, sau limiter. True peak vẫn ≤ −2 dBTP.
- Nhạc nền tự tổng hợp. Không dùng nhạc có bản quyền.
- SFX tự tổng hợp hoặc lấy từ thư viện miễn bản quyền của Minh. Âm có nốt phải khớp giọng nhạc.
- Bò "nói" bằng hơi mũi phì, sừng gõ "tok", thân đáp trầm. Không tiếng bò kêu.
- Va chạm đạt đỉnh 1 khung (16,7 ms) sau hình. Không âm nào sớm hơn hình:
  - người xem nhận ra âm sớm từ khoảng 45 ms, âm trễ từ khoảng 125 ms (ITU-R BT.1359);
  - ATSC IS-191 cho phép âm sớm tối đa 15 ms.
- Không đổi file âm dùng chung (`master.py`, `mixbus.py`, `dsp*.py`...). V2, V3 dựng lại phải trùng md5 (`score_thumon_regress.py`).

## 2. Đường đi

```
events.json → cue sheet ─┬→ nhạc nền (tổng hợp) ───────────────┐
                         └→ SFX (thư viện hoặc tổng hợp) ───────┴→ mix → master mono −16 → mux: bản −16, bản −14, bản có giờ phim
```

| Bước | Ca mẫu | Ra (`O` = `film3d/films/thu-mon/out`) |
|---|---|---|
| 1. Cue sheet: mỗi cú chạm, mỗi chuyển động một cue, có kiểu căn và mức | `score_thumon_cues.py` (`--check`: chỉ so, không ghi) | `src/audio/cues/thu-mon.json`, `.csv` |
| 2. Nhạc nền + bản SFX tổng hợp, master | `score_thumon_build.py` | `$O/g6-am/ban2/stem/music.wav`, `thu-mon-master.wav`, `build.json` |
| 3. SFX thư viện trên nhạc đó, master, mux | `score_thumon_thuvien.py` + bảng chọn âm `src/audio/cues/thu-mon.thuvien.json` | `$O/g6-am/thu-vien/{sfx,mix,master}.wav`, `bao-cao.json`, các MP4 |
| 4. QA | `score_thumon_qa.py` (bản tổng hợp); `bao-cao.json` + `ebur128` (bản thư viện) | `$O/g6-am/ban2/qa/`; `bao-cao.json` |

Kiểu căn của cue (quy ước của cue sheet):
- va chạm (`peak`): đỉnh âm = khung hình + 1 khung;
- whoosh, riser, trượt, hít vào (`end`): đuôi âm kết đúng khung chuyển động kết thúc;
- hơi thở, phì, rung (`onset`): đầu âm đúng khung bắt đầu.

## 3. Thư viện SFX của Minh

- Ở `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx` (có README). 2982 file wav, mp3, ogg.
- 7 nhóm theo chuyển động: 01 whoosh/chuyển cảnh · 02 va chạm · 03 pop/nảy · 04 giao diện · 05 riser · 06 glitch/sci-fi · 07 nền/drone/foley. Thêm `packs/`: uisfx 12 chủ đề (CC0), Kenney (CC0), Remotion.
- **Không có nhạc nền dùng được.** File dài nhất là bản nghe thử, âm meme, vòng lặp động cơ 5 s; jingle dài tối đa 1,8 s. Muốn đổi nhạc thì xin Minh thêm bản nhạc có giấy phép.
- Danh mục đo: `<OPA>\docs\film3d\am-thu-vien\danh-muc-sfx.csv`. Thư viện đổi thì dựng lại:

```bash
python -X utf8 tools/audio/sfx_catalog.py "/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx" docs/film3d/am-thu-vien/danh-muc-sfx.csv
```

| Cột của danh mục | Dùng để |
|---|---|
| `dur_s`, `tail_ms` | âm có vừa khoảng trống tới cue kế không |
| `lead_ms`, `attack_ms` | lặng đầu và thời gian lên, để căn đúng khung. mp3, ogg có lặng đầu 0 vì ffmpeg đã bù độ trễ bộ mã hóa |
| `peak_dbfs`, `tp_dbtp`, `lufs_i`, `lufs_mmax` | độ to gốc, để biết phải cộng trừ bao nhiêu |
| `centroid_hz`, `low`, `mid`, `high` | âm sáng hay trầm. `low` cao là mất trên loa điện thoại (cắt dưới khoảng 200 Hz) |

**Chọn âm:**
1. Lọc theo nhóm chuyển động và tên. Ca mẫu: tin tới → `ui-soft-ping-night`; hứng → `catch-bright-ring`; thẻ gắn bảng → `ui-card-snap-dock`; nảy → `ui-wood-marimba-tick`.
2. Lọc theo số đo: độ dài vừa chỗ; đủ dải trung nếu cần nghe trên điện thoại.
3. Âm có nốt phải khớp giọng nhạc:
   - nhóm "Studio Synth" (`catch-*`, `pop-bubble-*`, `ui-tick-crisp-*`, `ui-soft-ping-night`, `ui-wood-marimba-tick`, `sonic-logo-*`...) lên dây đúng A, C#, E, lệch 0 cent: hợp nhạc giọng A;
   - uisfx lệch 30–47 cent: dịch cao độ trước khi dùng (ca mẫu: `glass/receive.ogg` dịch +2,06 nửa cung lên A5);
   - chuỗi âm lặp thì leo nốt theo hợp âm (ca mẫu, 7 cú hứng: A4 C5 E5 G5 A5 B5 G#5).
4. Thư viện không có âm hợp thì bỏ, ghi lý do. Ca mẫu: không có tiếng ù màn hình, tiếng phòng đêm; drone duy nhất là hợp âm A trưởng, chỏi Am của đoạn đêm.
5. Nghe bằng tai là việc của Minh. Opus ghi "CHƯA NGHE BẰNG TAI".

## 4. Bảng chọn âm (`src/audio/cues/<id>.thuvien.json`)

Giữ nguyên mốc, kiểu căn và mức của cue sheet đã duyệt; chỉ thay nguồn âm. Mỗi cue một dòng, ví dụ của ca mẫu:

```json
"catch-b2":   {"file": "03-pops-snaps-elastic/catch-bright-ring.wav", "st": -4, "why": "nốt C5"},
"ff-sweep":   {"file": "01-whooshes-transitions/fast-forward-whirr-sweep.wav", "anchor": "end", "why": "..."},
"sonic-logo": {"file": "07-textures-drones-foley/sonic-logo-brass-chord.wav", "trimDb": 2, "why": "..."},
"hum":        {"sound": false, "why": "thư viện không có tiếng ù màn hình hợp"}
```

| Trường | Nghĩa |
|---|---|
| `file` | đường dẫn trong thư viện |
| `st` | dịch cao độ (nửa cung) bằng đổi tốc độ: âm dài ngắn đi theo, nên kiểm lại khoảng trống |
| `anchor` | đổi kiểu căn của cue: `peak`, `onset`, `end` |
| `fOffset` | dời mốc, tính bằng khung 30 fps của cue sheet (0,5 = 1 khung 60 fps) |
| `trimDb` | cộng trừ thêm sau khi đặt mức |
| `group` | nhóm mức, khi khác `kind` của cue |
| `sound: false` | cue này không có tiếng; ghi lý do vào `why` |

- Lớp thêm không có trong cue sheet để ở mục `extra` (có `f`, `anchor`, `gainDb`, có thể `repeat: {n, everyF}`). Ca mẫu: kèn dâng lúc rạng sáng; 12 tick dòng CRM khi tua đêm.
- Script dừng (exit 2) khi cue sheet có cue chưa được chọn âm, hoặc bảng có cue lạ. Muốn bỏ tiếng một cue thì vẫn ghi dòng cho nó, với `"sound": false`.

## 5. Đặt mức

Nghiên cứu không tìm được chuẩn chính thức cho mức từng nhóm âm. Các đích dưới đây là đề xuất của nghiên cứu; Minh đã nghe và chọn trên bản ca mẫu.

Ba cách đặt, chọn theo loại âm (mục `levels` của bảng chọn âm):

| Loại âm | Cách đặt | Vì sao | Ca mẫu |
|---|---|---|---|
| Có nốt, đủ dài (hứng, nảy, bụp); whoosh, riser, swell | số LU so với độ to tức thời (momentary 400 ms) của nhạc ngay tại mốc | chuỗi giai điệu đều tai; whoosh, riser, swell không được vượt nhạc | hứng −1, nảy −4, bụp −2, trượt −4, riser −1, kèn dâng rạng sáng −6 |
| Click, tick ngắn dưới 0,2 s | `{"band": [lo, hi], "db": x}`: hơn nhạc x dB trong dải, cửa sổ 105 ms quanh đỉnh âm | thước 400 ms đánh giá thấp âm rất ngắn | ping tin tới +3 (150–2000 Hz); khối nhấn +6, thẻ gắn bảng +4, tick dòng +3 (800–6000 Hz); nét gạch +3 (2000–8000 Hz) |
| Sau khi nhạc dừng (logo, sub, CTA) | giữ quy ước của cue sheet: momentary max = −20 LUFS + `gainDb` | không còn nhạc để so | sonic logo thêm +2 dB để qua phép thử loa điện thoại |

- **Đích của nghiên cứu:** ping báo tin ≥ +3 dB so với nhạc trong dải của nó; tick hứng ≥ +6 dB ở 0,8–6 kHz, không đẩy thêm vì dễ chói; tick phụ thấp hơn 3–6 dB; whoosh, riser, swell không vượt nhạc; logo qua loa điện thoại to ít nhất bằng đoạn đuổi.
- **Bẫy:** đặt mọi âm theo một dải cố định 800–6000 Hz làm nốt có âm cơ bản dưới 800 Hz to vọt (ca mẫu: chuỗi hứng, nảy). Âm có nốt thì so với nhạc cả dải.
- Mỗi âm còn qua: dịch cao độ → low-shelf −2,6 dB dưới 90 Hz cho âm nhỏ (ping, hứng, tick, phì, nảy) → fade vào 3 ms (cú hit và sub của logo giữ nguyên đầu âm), fade ra 10 ms. Cả bus SFX qua `bus_eq` (HPF 25 Hz, −2 dB ở 250 Hz) rồi cộng với nhạc.
- So với bản tổng hợp đã duyệt, bản thư viện làm rõ những tiếng trước bị nhạc che: Bò nảy ban ngày từ −15 LU lên −4 LU so với nhạc; khối nhấn câu chốt lên +6 dB trong dải.

## 6. Master và hai bản

- **Master** bằng `master.py` của V2 (không đổi file này): volume → 192 kHz → limiter trần 0,79 (≈ −2,0 dBFS) → 48 kHz, mono pcm_s24le, đúng số mẫu của phim. Đích −16 LUFS.
- **Mux** bằng `pan`, chép nguyên luồng hình, AAC 320k, `-aac_pns 0`:
  - bản −16: mỗi kênh −3,0103 dB so với mono. Độ to MP4 bằng master, như `-ac 2` của bản đã duyệt;
  - bản −14: mỗi kênh −1,0103 dB, tức +2 dB sau limiter. Không ép limiter thêm; true peak tăng đúng 2 dB (ca mẫu: −5,0 → −2,9 dBTP trên MP4).
- **Vì sao −14 chỉ cho mạng xã hội:** Spotify chuẩn hóa về −14 cả hạ lẫn nâng; YouTube khoảng −14 nhưng chỉ hạ bản to, không nâng bản nhỏ; Facebook, Instagram chuẩn hóa trong app, Meta không công bố số; TikTok chưa có nguồn chính thức. File −16 giữ cho chiếu và để xem cạnh V2, V3.
- **Loa điện thoại** gần như mất phần dưới vài trăm Hz, cộng hưởng khoảng 800 Hz.
  - Phép thử của `score_thumon_thuvien.py`: lọc master qua HPF 500 Hz + LPF 8 kHz, so momentary max của logo (16,5–18,0 s) với đoạn đuổi (5,0–7,5 s). Logo phải to ít nhất bằng. Ca mẫu: +0,7 dB, sau khi cộng 2 dB cho sonic logo.
  - Tiếng trầm cần lớp trung đi kèm. Ca mẫu: cú đáp có `bookPlace2` dải trung chồng lên `impactSoft` trầm.

## 7. Đo

Ngưỡng và số của ca mẫu: `qa-checklist.md` nấc 6. Đo độ to trên MP4:

```bash
ffmpeg -hide_banner -nostats -i <mp4> -filter_complex ebur128=peak=true -f null - 2>&1 | grep -E "^ +(I|LRA|Peak):"
```

`bao-cao.json` của `score_thumon_thuvien.py` ghi:
- master: I, TP, LRA, gain;
- độ to nhạc và SFX; chênh SFX − nhạc (short-term, mỗi 0,5 s);
- phép thử loa điện thoại;
- từng âm: mốc, mức đặt, so với nhạc, mức trong dải;
- từng MP4: I, TP, LRA, đoạn to nhất.

## 8. Lệnh ca mẫu (chạy từ `<OPA>`)

```bash
F=film3d/films/thu-mon; O=$F/out; G=out/thu-mon-3d-16x9-ban2
python -I -X utf8 tools/film3d/render.py job $F/jobs/events.json      # mốc âm từ timeline.js
python -X utf8 tools/audio/score_thumon_cues.py                       # cue sheet (--check: chỉ so)
python -X utf8 tools/audio/score_thumon_build.py                      # nhạc nền + bản âm tổng hợp → $O/g6-am/ban2/
python -X utf8 tools/audio/score_thumon_thuvien.py --video $O/v2-ghep/thu-mon-v2-gio.mp4 --out $G/thu-mon-3d_16x9_ban2_gio-phim.mp4
python -X utf8 tools/audio/score_thumon_thuvien.py --video $O/v2-ghep/thu-mon-v2.mp4 --out $G/thu-mon-3d_16x9_ban2.mp4 --out-14 $G/thu-mon-3d_16x9_ban2_-14LUFS.mp4
python -X utf8 tools/audio/score_thumon_qa.py                         # QA bản âm tổng hợp
python -X utf8 tools/audio/score_thumon_regress.py                    # V2, V3 vẫn trùng md5
```

- **Hai lệnh `score_thumon_thuvien.py` ghi đè bản giao Minh đã duyệt.** Muốn giữ thì đổi `--out`.
- Chạy bản có giờ phim trước, bản chính sau: mỗi lần chạy ghi đè mục MP4 trong `bao-cao.json`.
- Dựng lại thì master thư viện phải trùng md5 `1331b5e5995a8486d6cc2c6109fac102`, master tổng hợp trùng `188b92d360dfca5767b1c591a10728c6`.

## 9. Bẫy

- **Mux bị từ chối sau khi sửa `timeline.js`.** Cue sheet giữ md5 của `events.json` và soát lại `timeline.js`. Chạy lại job `events`, rồi `score_thumon_cues.py`, rồi dựng âm. Mốc không đổi thì master không đổi.
- **Âm sớm hơn hình** là lỗi nặng hơn âm trễ. Va chạm luôn +1 khung.
- **Dịch cao độ đổi độ dài âm** (đổi tốc độ): kiểm lại đuôi âm với khoảng trống tới cue kế.
- **Bản −14 đẩy đoạn to nhất lên** (ca mẫu: short-term lớn nhất −11,9 LUFS). Đích: không quá mức đích + 5 LU.

## 10. Phim mới

Chép bộ của ca mẫu thành `score_<phim>_*.py`, rồi đổi:
- bảng cue: mốc end card, cue không nằm trong `EVENTS`;
- nhạc nền: nhịp, hợp âm theo storyboard;
- bảng chọn âm `<phim>.thuvien.json`;
- đoạn đo của phép thử loa điện thoại (logo, đoạn đuổi), đang ghi cứng trong `score_thumon_thuvien.py`.

Không gói nguyên các file `score_thumon_*` vào skill: chúng gắn chặt với phim Thủ môn. Chỉ `sfx_catalog.py` dùng chung được.
