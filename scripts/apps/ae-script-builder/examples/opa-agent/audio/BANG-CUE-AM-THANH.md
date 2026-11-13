# Bảng cue âm thanh — OPA Agent × Pancake

Sinh bởi `tools/am_thanh_cues.py` (không sửa tay; sửa cue trong file đó rồi chạy lại và dựng lại AE).
Kho SFX: `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx` (CC0 / MIT). Logo âm thanh: bộ âm OPA. Nhạc nền: tự tổng hợp (`tools/audio/score_agent.py`).

**Cột:** khung = khung master (30 fps) mà **đỉnh** âm rơi vào; M đích = độ to tức thời 400 ms muốn có trong bản trộn (LUFS); M = độ to thực sau gain (thấp hơn đích khi bị trần đỉnh thật −12 dBTP giữ lại: âm cực ngắn, đỉnh nhọn); gain = chỉnh trên layer AE; TP = đỉnh thật của toàn bộ SFX trong ±40 ms quanh đỉnh cue (dựng lại stem, đã tính các âm chồng nhau; vượt trần thì cả nhóm cùng khung bị hạ).

**Nhạc nền:** `nhac-nen-opa-agent.wav` · đo −20,5 LUFS → gain −10,50 dB → tích hợp −31 LUFS (15 LU dưới giọng −16 LUFS). Cột **Nhô** = M của cue trừ độ to tức thời của nhạc quanh khung đó (âm ngắn, sáng vẫn nghe rõ khi Nhô hơi âm vì thang 400 ms tính thấp âm cực ngắn).

**Giọng đọc:** `1023.MP3` → `assets/voice/giong-doc-1023.wav` · đo −18,9 LUFS → gain +2,60 dB → −16,3 LUFS. Cột **Lời** = cue rơi lúc đang nói hay khoảng nghỉ; **Dưới giọng** = độ to tức thời của giọng trừ M của cue (chỉ tính lúc đang nói).

## Thang mức (research decibel, 22/10/2026)

| Lớp | Mức trong bản trộn | Căn cứ |
|---|---|---|
| Giọng đọc | −16,3 LUFS trong bản trộn (bản giao chuẩn hoá −16 LUFS, đỉnh thật ≤ −2 dBTP) | Chuẩn Minh chốt; AES TD1008: nhạc −16, lời −18 LUFS; YouTube chuẩn hoá về khoảng −14 LUFS và không kéo bản nhỏ lên |
| Nhạc nền | −31 LUFS tích hợp (15 LU dưới giọng), dải độ to ≤ 5 LU | Quy trình nền 1.2.3 Minh duyệt (giọng luôn cao hơn nền ≥ 10 LU); hướng dẫn trộn phổ biến: nhạc dưới lời 15–25 dB; WCAG 1.4.7 (AAA): nền dưới lời ≥ 20 dB |
| SFX chuyển cảnh, logo | M −24,5 … −27 | Rơi vào khoảng nghỉ giữa các câu; vẫn dưới giọng ≥ 8 LU |
| SFX sự kiện giao diện | M −27 … −31 | Nhô trên nền nhạc tại chỗ 0–4 LU |
| Tiếng nhỏ (đồng hồ, gõ phím, click) | M −33 … −38 | Âm cực ngắn, sáng: nghe rõ dù M thấp |
| Mỗi cue | Đỉnh thật ≤ −12 dBTP | Âm trùng đỉnh giọng đẩy bản trộn quá trần (bài học B8 trong master prompt) |
| Cả bản ngắn (nội dung quảng cáo) | Độ to ngắn hạn 3 s không vượt mức tích hợp quá 5 LU; đỉnh thật ≤ −1 dBTP | EBU R 128 s1 (nội dung ngắn); đo theo ITU-R BS.1770 / EBU Tech 3341 |

Nguồn: [EBU R 128 s1](https://tech.ebu.ch/docs/r/r128s1.pdf) · [EBU R 128](https://en.wikipedia.org/wiki/EBU_R_128) · [AES TD1008 (Production Advice)](https://productionadvice.co.uk/td1008/) · [Telos: loudness cho streaming](https://docs.telosalliance.com/docs/understanding-loudness-for-streaming-audio) · [WCAG 1.4.7](https://www.disabilityworld.org/toolkit/standards/wcag/1-4-7-low-or-no-background-audio/) · [Vidpros: nhạc nền quá to](https://vidpros.com/fix-background-music-too-loud-video/).

## Cảnh 1 · Hook (0–5 s)

| Giây | Khung | Chuyển động | Âm (file trong kho) | M đích | M | Nhô | Lời | Dưới giọng | Gain | TP | Lý do |
|---:|---:|---|---|---:|---:|---:|---|---:|---:|---:|---|
| 0,07 | 2 | Tin nhắn 1 bật lò xo | `03-pops-snaps-elastic/pop-bubble-low-A4.wav` | −28 | −30,1 | +20,5 | nghỉ | — | −11,0 | −12 | Pop A4–C#5–E5 đi lên theo hợp âm La trưởng của nhạc: dồn dập mà vẫn hợp giọng |
| 0,40 | 12 | Tin nhắn 2 bật lò xo | `03-pops-snaps-elastic/pop-bubble-mid-C#5.wav` | −27,5 | −30,7 | +12,0 | nghỉ | — | −11,0 | −12 | Pop A4–C#5–E5 đi lên theo hợp âm La trưởng của nhạc: dồn dập mà vẫn hợp giọng |
| 0,50 | 15 | Đồng hồ nảy mỗi 0,5 s | `04-ui-tech-hud/ui-tick-crisp-E6.wav` | −32 | −33,2 | +6,5 | đang nói | 19,1 | −11,1 | −12,1 | Tích A6 / tắc E6 xen kẽ, ngang nền nhạc: nhịp thời gian trôi, không đè lời |
| 0,70 | 21 | Tin nhắn 3 bật lò xo | `03-pops-snaps-elastic/pop-bubble-high-E5.wav` | −27 | −30,7 | +4,5 | đang nói | 17,0 | −11,0 | −12 | Pop A4–C#5–E5 đi lên theo hợp âm La trưởng của nhạc: dồn dập mà vẫn hợp giọng |
| 0,97 | 29 | Tin nhắn 4 bật lò xo | `03-pops-snaps-elastic/pop-bubble-low-A4.wav` | −26,5 | −30,1 | +3,7 | đang nói | 15,0 | −11,0 | −12 | Pop A4–C#5–E5 đi lên theo hợp âm La trưởng của nhạc: dồn dập mà vẫn hợp giọng |
| 1,20 | 36 | Tin nhắn 5 bật lò xo | `03-pops-snaps-elastic/pop-bubble-mid-C#5.wav` | −26,5 | −30,7 | +3,4 | đang nói | 15,6 | −11,0 | −12 | Pop A4–C#5–E5 đi lên theo hợp âm La trưởng của nhạc: dồn dập mà vẫn hợp giọng |
| 1,40 | 42 | Tin nhắn 6 bật lò xo | `03-pops-snaps-elastic/pop-bubble-high-E5.wav` | −26,5 | −30,7 | +2,6 | đang nói | 14,7 | −11,0 | −12 | Pop A4–C#5–E5 đi lên theo hợp âm La trưởng của nhạc: dồn dập mà vẫn hợp giọng |
| 1,50 | 45 | Đồng hồ nảy mỗi 0,5 s | `04-ui-tech-hud/ui-tick-crisp-E6.wav` | −32 | −33,2 | −0,2 | đang nói | 17,7 | −11,1 | −12 | Tích A6 / tắc E6 xen kẽ, ngang nền nhạc: nhịp thời gian trôi, không đè lời |
| 2,00 | 60 | Đồng hồ nảy mỗi 0,5 s | `04-ui-tech-hud/ui-tick-crisp-A6.wav` | −32 | −33,3 | +0,9 | đang nói | 18,1 | −11,1 | −12 | Tích A6 / tắc E6 xen kẽ, ngang nền nhạc: nhịp thời gian trôi, không đè lời |
| 2,50 | 75 | Đồng hồ nảy mỗi 0,5 s | `04-ui-tech-hud/ui-tick-crisp-E6.wav` | −32 | −33,2 | +1,7 | đang nói | 18,1 | −11,1 | −12 | Tích A6 / tắc E6 xen kẽ, ngang nền nhạc: nhịp thời gian trôi, không đè lời |
| 2,63 | 79 | Khối nhấn trắng quét "Mỗi ngày?" | `04-ui-tech-hud/ui-swish-accent-tick.wav` | −32 | −32 | +3,0 | đang nói | 17,4 | −13,1 | −14,1 | Swish ngắn đúng nhịp quét 8 khung; nằm dưới câu 1 nên hạ còn −32; cùng âm, cùng mức khối nhấn cảnh 3 |
| 3,00 | 90 | Đồng hồ nảy mỗi 0,5 s | `04-ui-tech-hud/ui-tick-crisp-A6.wav` | −32 | −33,3 | +1,2 | đang nói | 17,7 | −11,1 | −12 | Tích A6 / tắc E6 xen kẽ, ngang nền nhạc: nhịp thời gian trôi, không đè lời |
| 3,50 | 105 | Đồng hồ nảy mỗi 0,5 s | `04-ui-tech-hud/ui-tick-crisp-E6.wav` | −32 | −33,2 | +1,7 | đang nói | 15,8 | −11,1 | −12 | Tích A6 / tắc E6 xen kẽ, ngang nền nhạc: nhịp thời gian trôi, không đè lời |
| 4,00 | 120 | Đồng hồ nảy mỗi 0,5 s | `04-ui-tech-hud/ui-tick-crisp-A6.wav` | −32 | −33,3 | +0,9 | nghỉ | — | −11,1 | −12 | Tích A6 / tắc E6 xen kẽ, ngang nền nhạc: nhịp thời gian trôi, không đè lời |
| 4,50 | 135 | Đồng hồ nảy mỗi 0,5 s | `04-ui-tech-hud/ui-tick-crisp-E6.wav` | −32 | −33,2 | +0,5 | nghỉ | — | −11,1 | −12 | Tích A6 / tắc E6 xen kẽ, ngang nền nhạc: nhịp thời gian trôi, không đè lời |

## Cảnh 2 · Nỗi đau (5–13,5 s)

| Giây | Khung | Chuyển động | Âm (file trong kho) | M đích | M | Nhô | Lời | Dưới giọng | Gain | TP | Lý do |
|---:|---:|---|---|---:|---:|---:|---|---:|---:|---:|---|
| 5,70 | 171 | Tin khách mới trượt vào hộp thư | `04-ui-tech-hud/ui-soft-ping-night.wav` | −29,5 | −29,5 | +3,6 | đang nói | 14,2 | −14,2 | −15,2 | Ping A3 trầm "night" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s |
| 5,87 | 176 | Icon "!" của gạch đầu dòng 1 bật | `04-ui-tech-hud/ui-alert-soft-low.wav` | −28,5 | −28,5 | +4,3 | đang nói | 13,1 | −13,9 | −14,8 | Cảnh báo mềm (Rê5, trong giọng La); ba mục song song cùng một âm, cùng mức |
| 6,30 | 189 | Tin khách mới trượt vào hộp thư | `04-ui-tech-hud/ui-soft-ping-night.wav` | −29,5 | −29,5 | +4,3 | đang nói | 12,3 | −14,2 | −15,2 | Ping A3 trầm "night" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s |
| 7,10 | 213 | Tin khách mới trượt vào hộp thư | `04-ui-tech-hud/ui-soft-ping-night.wav` | −29,5 | −29,5 | +3,7 | đang nói | 13,1 | −14,2 | −15,2 | Ping A3 trầm "night" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s |
| 7,90 | 237 | Tin khách mới trượt vào hộp thư | `04-ui-tech-hud/ui-soft-ping-night.wav` | −29,5 | −29,5 | +3,7 | đang nói | 13,6 | −14,2 | −15,2 | Ping A3 trầm "night" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s |
| 8,27 | 248 | Icon "!" của gạch đầu dòng 2 bật | `04-ui-tech-hud/ui-alert-soft-low.wav` | −28,5 | −28,5 | +5,6 | đang nói | 12,9 | −13,9 | −14,9 | Cảnh báo mềm (Rê5, trong giọng La); ba mục song song cùng một âm, cùng mức |
| 8,40 | 252 | Câu trả lời y hệt lần 1 gửi đi | `04-ui-tech-hud/ui-card-snap-dock.wav` | −32 | −33,7 | −0,8 | nghỉ | — | −11,0 | −12,1 | Cùng một tiếng "snap" mỗi lần: nghe ra sự lặp; lần 4 (316) bỏ vì trùng cảnh báo 3 và phiếu POS |
| 8,77 | 263 | Tin khách mới trượt vào hộp thư | `04-ui-tech-hud/ui-soft-ping-night.wav` | −29,5 | −29,5 | +1,5 | nghỉ | — | −14,2 | −15,2 | Ping A3 trầm "night" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s |
| 9,13 | 274 | Câu trả lời y hệt lần 2 gửi đi | `04-ui-tech-hud/ui-card-snap-dock.wav` | −32 | −33,7 | −1,4 | đang nói | 18,0 | −11,0 | −12 | Cùng một tiếng "snap" mỗi lần: nghe ra sự lặp; lần 4 (316) bỏ vì trùng cảnh báo 3 và phiếu POS |
| 9,50 | 285 | Tin khách mới trượt vào hộp thư | `04-ui-tech-hud/ui-soft-ping-night.wav` | −29,5 | −29,5 | +1,9 | nghỉ | — | −14,2 | −15,2 | Ping A3 trầm "night" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s |
| 9,87 | 296 | Câu trả lời y hệt lần 3 gửi đi | `04-ui-tech-hud/ui-card-snap-dock.wav` | −32 | −33,7 | −3,1 | đang nói | 16,5 | −11,0 | −12 | Cùng một tiếng "snap" mỗi lần: nghe ra sự lặp; lần 4 (316) bỏ vì trùng cảnh báo 3 và phiếu POS |
| 10,23 | 307 | Tin khách mới trượt vào hộp thư | `04-ui-tech-hud/ui-soft-ping-night.wav` | −29,5 | −29,5 | +3,3 | đang nói | 12,5 | −14,2 | −15,2 | Ping A3 trầm "night" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s |
| 10,67 | 320 | Icon "!" của gạch đầu dòng 3 bật | `04-ui-tech-hud/ui-alert-soft-low.wav` | −28,5 | −28,5 | +3,0 | nghỉ | — | −13,9 | −14,9 | Cảnh báo mềm (Rê5, trong giọng La); ba mục song song cùng một âm, cùng mức |
| 11,17 | 335 | Tin khách mới trượt vào hộp thư | `04-ui-tech-hud/ui-soft-ping-night.wav` | −29,5 | −29,5 | +1,5 | nghỉ | — | −14,2 | −15,2 | Ping A3 trầm "night" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s |
| 11,53 | 346 | Vạch gõ dài ra trong ô | `04-ui-tech-hud/uisfx-minimal-typing.mp3` | −34 | −34 | −2,9 | đang nói | 20,6 | −2,6 | −14 | Gõ phím rất nhỏ, xen mức ±1 dB; cách ping tin mới (355, 373) ít nhất 3 khung |
| 11,63 | 349 | Vạch gõ dài ra trong ô | `04-ui-tech-hud/uisfx-minimal-typing.mp3` | −35 | −35 | −3,8 | đang nói | 21,9 | −3,6 | −15 | Gõ phím rất nhỏ, xen mức ±1 dB; cách ping tin mới (355, 373) ít nhất 3 khung |
| 11,73 | 352 | Vạch gõ dài ra trong ô | `04-ui-tech-hud/uisfx-minimal-typing.mp3` | −34 | −34 | −2,8 | nghỉ | — | −2,6 | −14 | Gõ phím rất nhỏ, xen mức ±1 dB; cách ping tin mới (355, 373) ít nhất 3 khung |
| 11,83 | 355 | Tin khách mới trượt vào hộp thư | `04-ui-tech-hud/ui-soft-ping-night.wav` | −29,5 | −29,5 | +1,0 | đang nói | 12,9 | −14,2 | −15,2 | Ping A3 trầm "night" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s |
| 12,23 | 367 | Vạch gõ dài ra trong ô | `04-ui-tech-hud/uisfx-minimal-typing.mp3` | −35 | −35 | −4,0 | đang nói | 19,6 | −3,6 | −15 | Gõ phím rất nhỏ, xen mức ±1 dB; cách ping tin mới (355, 373) ít nhất 3 khung |
| 12,33 | 370 | Vạch gõ dài ra trong ô | `04-ui-tech-hud/uisfx-minimal-typing.mp3` | −34 | −34 | −3,4 | đang nói | 17,8 | −2,6 | −14 | Gõ phím rất nhỏ, xen mức ±1 dB; cách ping tin mới (355, 373) ít nhất 3 khung |
| 12,43 | 373 | Tin khách mới trượt vào hộp thư | `04-ui-tech-hud/ui-soft-ping-night.wav` | −29,5 | −29,5 | +1,5 | đang nói | 12,6 | −14,2 | −15,2 | Ping A3 trầm "night" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s |
| 12,53 | 376 | Vạch gõ dài ra trong ô | `04-ui-tech-hud/uisfx-minimal-typing.mp3` | −35 | −35 | −3,8 | đang nói | 18,3 | −3,6 | −14,6 | Gõ phím rất nhỏ, xen mức ±1 dB; cách ping tin mới (355, 373) ít nhất 3 khung |
| 12,70 | 381 | Con trỏ bấm lưu: lớp thân | `04-ui-tech-hud/uisfx-minimal-press.mp3` | −29,5 | −29,5 | +1,8 | đang nói | 13,1 | −8,0 | −13 | Press của bộ minimal (đỉnh không nhọn nên đứng trên nhạc mà vẫn dưới trần đỉnh) |
| 12,70 | 381 | Con trỏ bấm lưu: lớp tách | `04-ui-tech-hud/kenney-mouseclick1.wav` | −46 | −46 | −14,7 | đang nói | 29,6 | −19,9 | −13 | Click chuột Kenney cùng khung, nhập với lớp thân thành một cú bấm; trùng âm /s/ của "sẽ" nên rất nhỏ (Q5 v10) |
| 12,83 | 385 | Con trỏ nhả | `packs/uisfx-themes/minimal/release.mp3` | −32,5 | −32,5 | −0,7 | đang nói | 15,8 | −11,6 | −16,8 | Release của bộ minimal, nhỏ hơn lúc bấm |
| 12,93 | 388 | Bò trắng lao vào từ phải | `01-whooshes-transitions/whoosh-deep-windup.wav` | −31 | −31 | +1,7 | đang nói | 15,3 | −19,8 | −20,7 | Whoosh trầm, đỉnh lúc Bò vừa lọt vào hình và nhanh nhất; nằm dưới "mệt mỏi như thế nào" nên hạ còn −31 |
| 13,10 | 393 | Đĩa sáng bật sau lưng Bò, Bò hoá xanh | `02-impacts-hits/thump-body-punch.wav` | −28 | −30,4 | +5,7 | đang nói | 14,1 | −11,8 | −12 | Tiếng thịch thân trầm cho cú va: rơi đúng khoảng lặng của nhạc |
| 13,47 | 404 | Đĩa nở phủ kín khung (393–404) | `05-risers-builders/swell-tonal-brass-1.0s.wav` | −28 | −28 | +5,8 | nghỉ | — | −15,9 | −16,9 | Swell hợp âm (giọng La) dâng tới khung trắng cuối, nhạc đáp cảnh 3 ngay sau; dưới chữ cuối câu 2 nên −28 |

## Cảnh 3 · Giải pháp (13,5–22 s)

| Giây | Khung | Chuyển động | Âm (file trong kho) | M đích | M | Nhô | Lời | Dưới giọng | Gain | TP | Lý do |
|---:|---:|---|---|---:|---:|---:|---|---:|---:|---:|---|
| 13,83 | 415 | Bảng OPA Agent mở bằng mask | `01-whooshes-transitions/uisfx-glass-expand.mp3` (+155 cent) | −28 | −28 | −0,2 | nghỉ | — | −12,2 | −20,1 | Expand mềm, đỉnh lúc mask mở nhanh nhất; dịch +155 cent về La–Đô♯–Fa♯ cho hợp giọng |
| 14,53 | 436 | Khối nhấn xanh quét "Chỉ 1 kết nối —" | `04-ui-tech-hud/ui-swish-accent-tick.wav` | −32 | −32 | −3,9 | nghỉ | — | −13,1 | −14,1 | Cùng âm, cùng mức khối nhấn cảnh 1; rơi vào khoảng nghỉ 14,46–14,75 s |
| 14,70 | 441 | Bò đáp vào đầu bảng, màu xanh lan ra | `03-pops-snaps-elastic/catch-bright-ring.wav` | −28,5 | −28,5 | −0,2 | nghỉ | — | −11,9 | −12,9 | "Catch" sáng E5: Bò về đúng chỗ |
| 15,03 | 451 | Icon tính năng 1 bật | `04-ui-tech-hud/ui-wood-marimba-tick.wav` | −28 | −28 | +1,0 | đang nói | 13,3 | −12,5 | −13,5 | Marimba A5 ấm, hợp giọng; năm mục song song cùng âm, cùng mức |
| 15,23 | 457 | Chip "Pancake POS" cắm vào, vòng tỏa | `04-ui-tech-hud/ui-chime-question-bell.wav` | −27 | −27 | +1,8 | đang nói | 10,8 | −18,7 | −19,8 | Chuông hai tông sáng (E6–A5) = đã kết nối; âm dày, đỉnh thấp nên nổi trên nhạc thân đầy mà không vượt trần đỉnh (tiếng chốt khóa bị trần giữ, chìm dưới nhạc 3,8 LU); cách tick tính năng 1 sáu khung |
| 15,97 | 479 | Icon tính năng 2 bật | `04-ui-tech-hud/ui-wood-marimba-tick.wav` | −28 | −28 | +1,2 | nghỉ | — | −12,5 | −13,6 | Marimba A5 ấm, hợp giọng; năm mục song song cùng âm, cùng mức |
| 16,90 | 507 | Icon tính năng 3 bật | `04-ui-tech-hud/ui-wood-marimba-tick.wav` | −28 | −28 | +0,6 | đang nói | 12,1 | −12,5 | −13,5 | Marimba A5 ấm, hợp giọng; năm mục song song cùng âm, cùng mức |
| 17,83 | 535 | Icon tính năng 4 bật | `04-ui-tech-hud/ui-wood-marimba-tick.wav` | −28 | −28 | +0,5 | đang nói | 12,5 | −12,5 | −13,5 | Marimba A5 ấm, hợp giọng; năm mục song song cùng âm, cùng mức |
| 18,77 | 563 | Icon tính năng 5 bật | `04-ui-tech-hud/ui-wood-marimba-tick.wav` | −28 | −28 | +1,3 | đang nói | 11,5 | −12,5 | −13,5 | Marimba A5 ấm, hợp giọng; năm mục song song cùng âm, cùng mức |
| 19,13 | 574 | Nút gạt chạy từ Bò sang nhân viên | `04-ui-tech-hud/uisfx-minimal-toggle-on.mp3` | −29,5 | −29,5 | −0,7 | đang nói | 12,6 | −11,5 | −19,3 | Toggle-on lúc nút gạt gần tới đích (đã đi 77 % ở 574) |
| 21,30 | 639 | Cột chữ thu R6, bảng hoá xanh | `01-whooshes-transitions/uisfx-glass-collapse.mp3` (+155 cent) | −34 | −34 | −4,2 | đang nói | 18,0 | −16,8 | −24,8 | Collapse mềm cùng cú thu đầu của R6, dịch +155 cent như expand; nằm dưới chữ "OPA Agent" cuối câu 3 nên hạ còn −34 |
| 22,30 | 669 | Chủ shop trồi lên trong khung xanh | `01-whooshes-transitions/whoosh-light-airy.wav` | −29 | −29 | +2,9 | nghỉ | — | −18,2 | −17,5 | Whoosh nhẹ đi lên, đỉnh trong khoảng nghỉ 22,19–22,62 s, trước câu 4 hơn 0,3 s (âm nhiều 2–8 kHz) |

## Cảnh 4 · Giải phóng (22–30 s)

| Giây | Khung | Chuyển động | Âm (file trong kho) | M đích | M | Nhô | Lời | Dưới giọng | Gain | TP | Lý do |
|---:|---:|---|---|---:|---:|---:|---|---:|---:|---:|---|
| 22,47 | 674 | Icon tích mục 1 bật | `04-ui-tech-hud/uisfx-minimal-success.mp3` (+200 cent) | −29 | −29 | +1,8 | nghỉ | — | −15,1 | −23 | Chuông "xong" ba nốt đi lên, dịch +2 cung thành La–Đô♯–Mi (hợp âm chủ của nhạc); nốt cuối, cũng là đỉnh, rơi đúng lúc icon tích bật; ba mục cùng âm, cùng mức |
| 24,07 | 722 | Icon tích mục 2 bật | `04-ui-tech-hud/uisfx-minimal-success.mp3` (+200 cent) | −29 | −29 | +2,9 | đang nói | 9,7 | −15,1 | −23 | Chuông "xong" ba nốt đi lên, dịch +2 cung thành La–Đô♯–Mi (hợp âm chủ của nhạc); nốt cuối, cũng là đỉnh, rơi đúng lúc icon tích bật; ba mục cùng âm, cùng mức |
| 25,60 | 768 | Icon tích mục 3 bật | `04-ui-tech-hud/uisfx-minimal-success.mp3` (+200 cent) | −29 | −29 | +1,9 | đang nói | 13,5 | −15,1 | −23 | Chuông "xong" ba nốt đi lên, dịch +2 cung thành La–Đô♯–Mi (hợp âm chủ của nhạc); nốt cuối, cũng là đỉnh, rơi đúng lúc icon tích bật; ba mục cùng âm, cùng mức |
| 29,93 | 898 | Khung xanh nở tràn khung sang cảnh 5 | `01-whooshes-transitions/whoosh-cut-medium.wav` | −26 | −26 | +9,8 | nghỉ | — | −15,9 | −16,9 | Whoosh đỉnh trước cắt 0,03 s (luật whoosh vào cảnh mới) |

## Cảnh 5 · CTA (30–36 s)

| Giây | Khung | Chuyển động | Âm (file trong kho) | M đích | M | Nhô | Lời | Dưới giọng | Gain | TP | Lý do |
|---:|---:|---|---|---:|---:|---:|---|---:|---:|---:|---|
| 30,13 | 904 | Bò hiện, vòng tỏa đầu tiên | `opa-sonic-logo-c.wav` | −27 | −27 | +59,2 | nghỉ | — | −15,4 | −16,4 | Logo âm thanh OPA (giọng La, đã dùng ở V2/V3); đỉnh trong khoảng nghỉ trước "OPA Agent" câu 5 (30,33 s), đuôi nằm dưới lời nên −27 |
| 32,20 | 966 | Nút URL bật lò xo | `03-pops-snaps-elastic/catch-bounce-dry.wav` | −29 | −29 | +2,4 | đang nói | 13,5 | −11,7 | −12,7 | Bounce A4: về chủ âm, kết ý |
| 34,17 | 1025 | Con trỏ bấm nút CTA: lớp thân | `04-ui-tech-hud/uisfx-minimal-press.mp3` | −28,5 | −31,9 | +1,1 | nghỉ | — | −10,4 | −12,1 | Cùng cú bấm cảnh 2, to hơn 1 dB vì là hành động chốt |
| 34,17 | 1025 | Con trỏ bấm nút CTA: lớp tách | `04-ui-tech-hud/kenney-mouseclick1.wav` | −29 | −41,2 | −8,2 | nghỉ | — | −15,1 | −12,1 | Lớp tách sáng như cảnh 2 |
| 34,33 | 1030 | Con trỏ nhả | `packs/uisfx-themes/minimal/release.mp3` | −31,5 | −31,5 | +1,3 | đang nói | 16,1 | −10,6 | −18,5 | Release của bộ minimal |

## Chuyển động cố ý không gắn âm

- Chữ vào/ra (R1–R6): lời đọc sẽ đọc đúng chữ đó, thêm âm sẽ che lời.
- Điện thoại rung lần 7–11 (56–112): nhịp 14 khung lệch nhịp đồng hồ 15 khung, chồng lên nhau thành lộn xộn dưới lời cảnh 1; sáu lần rung đầu trùng tin nhắn bật nên đã có âm.
- Tin mới thứ 2, 4, 6 (178, 200, 224) và chấm đỏ, "99+" nảy: cách tin trước dưới 0,5 s (nghe thành tiếng đúp), đã có ping của tin kề.
- Trả lời lặp lần 4 (316): trùng cảnh báo 3 và phiếu POS mở.
- Rung quá tải (375–389): nhạc dâng hats và whoosh Bò lao vào đảm nhận.
- Hàng minh họa cảnh 3 (hộp kho, tích, vạch quét, giỏ hàng, người) và chuông 24H: lời cảnh 3 dày, tick tính năng đã đánh dấu từng hàng.
- Tích bay lên cảnh 4 (684–814), hơi cà phê, Bò thở, nút CTA thở: chuyển động nền liên tục, giữ cảnh 4 thư thả.
- Vòng tỏa thứ hai (916) và con trỏ CTA đi vào (992–1022): logo âm thanh đã phủ; chỉ gắn âm lúc bấm.
- Riser vào màn trắng (4,9 s) và tiếng giấy phiếu POS (10,77 s): bỏ khi lồng giọng 23/10. Riser nằm đè "tưởng tượng" đầu câu 2, tiếng giấy đè đúng chữ "size"; cả hai nhiều năng lượng 2–8 kHz, che phụ âm.
- Chip số điện thoại, địa chỉ bay vào ô (338–348, 358–368): bỏ sau rà chéo v10, vì tiếng swish đè đầu âm tiết "rồi", "từng" lúc lời đang đọc đúng "nhập tay từng đơn hàng"; dời đi thì chỉ cách ping tin mới 1 khung.
