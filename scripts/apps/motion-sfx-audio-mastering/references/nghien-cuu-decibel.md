Ngày 22/10/2026 · Nghiên cứu mức decibel cho âm thanh phim 3D "Thủ môn" (21 s, 16:9, 60 fps, không lời) · Soạn: Claude Code (Opus 5.5)

Phạm vi: chỉ tra cứu và tổng hợp, không sửa file nào khác. Số "hiện tại" của phim lấy từ `docs/film3d/g6-am-thanh.md` (bản 2) và từ một lần đo lại chỉ đọc ngày 22/10 trên `out/thu-mon-3d-16x9-ban2/thu-mon-3d_16x9_ban2.mp4` (ffmpeg `ebur128=peak=true`).

**Nhãn nguồn dùng trong báo cáo**

- **[CT]** tài liệu chính thức: ITU, EBU, ATSC, trang trợ giúp của nền tảng, datasheet, bằng sáng chế.
- **[NC]** bài nghiên cứu khoa học.
- **[TC]** nguồn thứ cấp: bài của kỹ sư uy tín, hoặc bản tóm tắt tài liệu AES. Trang aes.org chặn truy cập tự động (lỗi 403), nên tôi không mở được bản gốc TD1004, TD1008.
- **[ĐO]** đo thực nghiệm của bên thứ ba, không phải tài liệu chính thức.
- **[TÍNH]** tôi tự tính từ công thức hoặc hệ số trong nguồn.
- **[SL]** suy luận của tôi, chưa có nguồn chuẩn. Đây là điểm xuất phát để nghe thử, không phải số chuẩn.
- **"chưa tìm được nguồn"**: đã tìm nhưng không thấy nguồn đáng tin.

---

## 0. Bảng số chính

| Mục | Số | Nguồn |
|---|---|---|
| EBU R 128 (phát sóng) | Đích −23,0 LUFS. Dung sai ±1,0 LU khi không đạt được, ví dụ chương trình trực tiếp; ±0,2 LU cho sai số đo ở khâu QC. True peak ≤ −1 dBTP (sai số đo ±0,3 dB). Đo cả chương trình, không đo riêng lời, nhạc hay SFX | [CT] [R 128 v5.0, 2023](https://tech.ebu.ch/files/live/sites/tech/files/shared/r/r128v5_0.pdf) |
| EBU R 128: LRA | Không khuyên dùng LRA cho chương trình ngắn hơn 1 phút | [CT] như trên, chú thích 2 |
| EBU R 128 s1 (quảng cáo, promo, tối đa khoảng 2 phút) | −23,0 LUFS. Max Short-term ≤ −18,0 LUFS (+5,0 LU so với đích). TP ≤ −1 dBTP. LRA không áp dụng | [CT] [R 128 s1, 2020](https://tech.ebu.ch/docs/r/r128s1.pdf) |
| EBU R 128 s2 (streaming) | Phát nguyên −23 LUFS. Nếu không dùng metadata, mức phát tạm thời là −20 đến −16 LUFS | [CT] [R 128 s2 v3.0, 2023](https://tech.ebu.ch/files/live/sites/tech/files/shared/r/r128s2v3_0.pdf) |
| EBU Tech 3343 / 3344 (codec nén) | Codec MPEG-1 L2, AC-3: TP ≤ −2 dBTP. Đặt limiter −2 dBTP trước encoder, hạ thấp hơn nếu bitrate thấp | [CT] [Tech 3343](https://tech.ebu.ch/docs/tech/tech3343.pdf), [Tech 3344](https://tech.ebu.ch/docs/tech/tech3344.pdf) |
| ATSC A/85:2013 (truyền hình Mỹ) | Đích −24 LKFS. Chênh khoảng ±2 dB do sai số đo là chấp nhận được. TP < −2 dBTP | [CT] [A/85:2013](https://www.atsc.org/wp-content/uploads/2025/06/A85-2013-with-Corrigendum-No-1.pdf) |
| AES TD1004 (2015) | Cửa sổ −16 đến −20 LUFS, TP −1 dBTP | [TC] [Production Expert](https://www.production-expert.com/home-page/2015/11/17/aes-release-recommendations-for-loudness-of-audio-streaming-and-network-file-playback) |
| AES TD1008 (2021, thay TD1004) | Nhạc −16 LUFS. Lời và nội dung hỗn hợp −18 LUFS. Quảng cáo, trailer −18 LUFS. TP ≤ −1 dBTP ở đầu vào codec. Không dành cho âm kèm hình | [TC] [Production Advice](https://productionadvice.co.uk/td1008/), [Production Expert](https://www.production-expert.com/production-expert-1/aes-update-loudness-recommendations-for-audio-only-streaming), [trích §4, §7B](https://raw.githubusercontent.com/M-Igashi/baken/main/docs/true-peak-ceiling.md) |
| Spotify | Normal −14, Loud −11, Quiet −19 LUFS. Chuẩn hóa cả lên lẫn xuống. Khuyên master −14 LUFS, TP ≤ −1 dBTP; master to hơn −14 thì TP ≤ −2 dBTP | [CT] [Spotify for Artists](https://support.spotify.com/us/artists/article/loudness-normalization/) |
| YouTube | Mốc khoảng −14 LUFS từ 2019. Chỉ hạ bản to, không nâng bản nhỏ | [ĐO] [Ian Shepherd, MeterPlugs 2019](https://www.meterplugs.com/blog/2019/09/18/youtube-changes-loudness-reference-to-14-lufs.html) |
| YouTube "Stable volume" | Bật mặc định. Liên tục chỉnh mức để thu hẹp chênh lệch to nhỏ | [CT] [YouTube Help](https://support.google.com/youtube/answer/14106294?hl=en) |
| Facebook, Instagram (Reels, Stories) | Chuẩn hóa ở app bằng metadata xHE-AAC (MPEG-D DRC). App tự đặt đích theo ngữ cảnh. Meta không công bố số LUFS | [CT] [Meta Engineering 2023](https://engineering.fb.com/2023/04/11/video-engineering/high-quality-audio-xhe-aac-codec-meta/) |
| TikTok | chưa tìm được nguồn chính thức. Blog bên thứ ba ghi −13 đến −14 LUFS, không kèm phép đo | — |
| Đồng bộ: ITU-R BT.1359 | Ngưỡng nhận ra: âm sớm 45 ms, âm trễ 125 ms. Ngưỡng chấp nhận: sớm 90 ms, trễ 185 ms. Chuỗi phát sóng: sớm ≤ 22,5 ms, trễ ≤ 30 ms | [CT] [BT.1359](https://itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.1359-0-199802-S!!PDF-E.pdf) |
| Đồng bộ: EBU R37 | Mỗi khâu: âm sớm ≤ 5 ms, trễ ≤ 15 ms. Từ đầu đến cuối: sớm ≤ 40 ms, trễ ≤ 60 ms | [CT] [R37-2007](https://tech.ebu.ch/docs/r/r037.pdf) |
| Đồng bộ: ATSC IS-191 | Đầu vào encoder: âm sớm ≤ 15 ms, trễ ≤ 45 ms | [TC] [TV Technology 2004](https://tvtechnology.com/opinions/atsc-recommends-av-sync-rules) |
| Đồng bộ: tiếng va kiểu clapperboard | Điểm nghe như trùng nhau: âm trễ 32–39 ms. Không nhận ra lệch khi âm trễ từ 1,7 đến 75,8 ms. Khuyên âm trễ 0–80 ms, không để âm sớm | [NC] [Heide & Maempel, Tonmeistertagung 2010](https://www.simpk.de/fileadmin/user_upload_sim/Dokumente/Forschung/Themen/Abteilung_III/Publikationen/Heide_Maempel_2011_Die_Wahrnehmung_audiovisueller_Synchronitaet_in_elektronischen_Medien.pdf) |
| Loa điện thoại | Loa linh kiện 11×15 mm cho smartphone cộng hưởng ở 800 Hz ±10 % (hộp sau 1 cm³) | [CT] [Datasheet Knowles](https://cdn.eicom.ru/media/PDF/440124.pdf) |

---

## 1. Đơn vị

### 1.1 Các đơn vị đo

| Đơn vị | Nghĩa | Cần nhớ | Nguồn |
|---|---|---|---|
| **dBFS** | Mức số so với mức lớn nhất máy số ghi được. 0 dBFS là mức tối đa; nửa biên độ khoảng −6 dBFS | Đồng hồ đỉnh mẫu (sample peak) bỏ sót đỉnh nằm giữa hai mẫu | [CT] [Wikipedia: DBFS](https://en.wikipedia.org/wiki/DBFS), [BS.1770-5 Annex 2](https://www.itu.int/dms_pubrec/itu-r/rec/bs/R-REC-BS.1770-5-202311-I!!PDF-E.pdf) |
| **dBTP** | Đỉnh thật (true peak): đỉnh của sóng liên tục, ước bằng nội suy ×4 (48 kHz → 192 kHz) | Đồng hồ ×4 có thể đọc thiếu khoảng 0,5 dB, vì thế trần sản xuất là −1 dBTP | [CT] [BS.1770-5](https://www.itu.int/dms_pubrec/itu-r/rec/bs/R-REC-BS.1770-5-202311-I!!PDF-E.pdf), [Tech 3343](https://tech.ebu.ch/docs/tech/tech3343.pdf) |
| **LUFS = LKFS** | Độ to theo trọng số K, so với full scale. Tín hiệu tăng 1 dB thì số đo tăng 1 LUFS. Sine 997 Hz ở 0 dBFS vào một kênh đo được −3,01 LKFS | EBU gọi là LUFS, ITU gọi là LKFS, hai tên cùng một đại lượng | [CT] [BS.1770-5](https://www.itu.int/rec/R-REC-BS.1770-5-202311-I/en), [R 128](https://tech.ebu.ch/files/live/sites/tech/files/shared/r/r128v5_0.pdf) |
| **LU** | Đơn vị tương đối, 1 LU = 1 dB | Dùng cho chênh lệch, LRA, thang tương đối | [CT] [Tech 3341](https://tech.ebu.ch/docs/tech/tech3341.pdf) |
| **M / S / I** | Momentary: cửa sổ 400 ms. Short-term: 3 s. Hai loại này không có cổng lọc. Integrated: cả bài, chia khối 400 ms chồng 75 %, bỏ khối dưới −70 LUFS rồi bỏ khối thấp hơn 10 LU | Max M và Max S dùng để soi đoạn to nhất | [CT] [Tech 3341](https://tech.ebu.ch/docs/tech/tech3341.pdf), [BS.1770-5](https://www.itu.int/rec/R-REC-BS.1770-5-202311-I/en) |
| **LRA** | Khoảng giữa phân vị 10 % và 95 % của các giá trị Short-term (3 s). Bỏ phần dưới −70 LUFS và phần thấp hơn 20 LU | Không dùng cho bài ngắn hơn 1 phút | [CT] [Tech 3342](https://tech.ebu.ch/docs/tech/tech3342.pdf), [R 128](https://tech.ebu.ch/files/live/sites/tech/files/shared/r/r128v5_0.pdf) |
| **RMS** | Căn bậc hai của trung bình bình phương. Có hai quy ước: AES17 coi sine đầy thang là 0 dBFS RMS; quy ước toán học cho cùng sine đó −3,01 dB | Phải biết máy đo dùng quy ước nào | [CT] [Wikipedia: DBFS](https://en.wikipedia.org/wiki/DBFS) |
| **Crest factor** | Đỉnh chia RMS. Sine: 1,414, tức 3,01 dB | Đo trên dạng sóng, không có trọng số K | [CT] [Wikipedia: Crest factor](https://en.wikipedia.org/wiki/Crest_factor) |
| **PLR** | True peak lớn nhất trừ độ to chương trình (LUFS). Đo độ động ở quy mô nhỏ ("vi động") | PLR cao: âm nhiều gai, đỉnh nhọn | [CT] [R 128 s2](https://tech.ebu.ch/files/live/sites/tech/files/shared/r/r128s2v3_0.pdf) |

### 1.2 Cộng trừ dB

| Phép | Kết quả | Nguồn |
|---|---|---|
| Gấp đôi biên độ (điện áp, áp suất) | +6,02 dB (20·log₁₀2) | [CT] [sengpielaudio](https://sengpielaudio.com/calculator-loudness.htm) |
| Gấp đôi công suất | +3,01 dB | như trên |
| Hai nguồn bằng nhau, không tương quan (hai tiếng khác nhau) | +3 dB | [CT] [sengpielaudio: coherent sources](https://sengpielaudio.com/calculator-coherentsources.htm) |
| Hai nguồn bằng nhau, cùng pha (hai lớp cùng mẫu đặt trùng) | +6 dB. Đây là cách đỉnh cộng dồn khi chồng lớp | như trên |
| 0 dB cộng −6 dB, không tương quan | +0,97 dB | [TÍNH] 10·log₁₀(1 + 10^−0,6) |
| Hai mức chênh nhau 10 dB | Tổng chỉ tăng 0,41 dB | [TÍNH] 10·log₁₀(1,1) |
| Tăng 10 dB | Nghe to khoảng gấp đôi. Đây là quy tắc ước lượng: số sone gấp đôi khi tăng 10 phon (trên 40 phon). Tăng 3 dB **không** nghe to gấp đôi | [CT] [sengpielaudio](https://sengpielaudio.com/calculator-loudness.htm), [Wikipedia: Sone](https://en.wikipedia.org/wiki/Sone) |

### 1.3 Đường cong Fletcher–Munson / ISO 226: nghe nhỏ thì mất trầm

ISO 226:2023 là bản hiện hành của đường cong đồng mức to. Bảng dưới tính bằng công thức và hệ số của ISO 226:2003, lấy từ [mã của Jeff Tackett](https://dsprelated.com/showcode/174.php). Bản 2023 chỉnh lại một ít, nên dùng số này để thấy xu hướng, đừng coi là số chính xác. Đơn vị là dB SPL: mức cần để tone ở tần số đó nghe to bằng 1 kHz. [TÍNH]

| Tần số | 40 phon (nghe nhỏ) | 60 phon | 80 phon (nghe to) |
|---|---|---|---|
| 50 Hz | 77,8 | 90,0 | 101,7 |
| 100 Hz | 64,4 | 78,7 | 92,5 |
| 200 Hz | 53,4 | 69,9 | 85,9 |
| 500 Hz | 43,1 | 62,1 | 80,9 |
| 1 kHz | 40,0 | 60,0 | 80,0 |
| 3,15 kHz | 35,6 | 56,4 | 77,1 |

- Nghe nhỏ (40 phon): 50 Hz phải mạnh hơn 1 kHz 37,8 dB. Nghe to (80 phon): chỉ cần 21,7 dB. Vậy khi vặn nhỏ, tiếng 50 Hz yếu đi thêm khoảng 16 dB so với dải trung. Ở 100 Hz con số này khoảng 12 dB, ở 200 Hz khoảng 7,5 dB.
- Tai nhạy nhất ở 2–5 kHz ([Wikipedia: Equal-loudness contour](https://en.wikipedia.org/wiki/Equal-loudness_contour)).
- Trên điện thoại vặn nhỏ, loa nhỏ đã thiếu trầm (mục 5), tai lại kém nhạy trầm thêm. Kết quả: tick, pop ở 1–5 kHz vẫn rõ, còn sub drop gần như biến mất.

### 1.4 Trọng số K của đồng hồ LUFS

Tôi tính từ hệ số bộ lọc trong BS.1770-5 (48 kHz). Số là mức so với 997 Hz. [TÍNH]

| 40 Hz | 50 Hz | 100 Hz | 200 Hz | 1 kHz | 2 kHz | 4 kHz | 8 kHz |
|---|---|---|---|---|---|---|---|
| −6,3 dB | −4,6 dB | −1,8 dB | −1,0 dB | 0 | +2,4 dB | +3,3 dB | +3,4 dB |

Cùng một mức đỉnh, sub 40–50 Hz được đồng hồ LUFS tính nhỏ hơn 1 kHz 5–6 dB, còn tiếng sáng trên 2 kHz được tính to hơn 2–3 dB. Sub tốn chỗ đỉnh mà góp ít LUFS. Tiếng sáng góp nhiều LUFS.

---

## 2. Mức độ to mục tiêu và true peak theo nền tảng

### 2.1 Bảng nền tảng

| Nền tảng | Mức chuẩn hóa | Chiều | True peak | Nguồn |
|---|---|---|---|---|
| YouTube | Khoảng −14 LUFS | Chỉ hạ bản to, không nâng bản nhỏ | Chưa tìm được nguồn chính thức. Bên thứ ba thường khuyên ≤ −1 dBTP | [ĐO] [MeterPlugs 2019](https://www.meterplugs.com/blog/2019/09/18/youtube-changes-loudness-reference-to-14-lufs.html) |
| YouTube "Stable volume" | Liên tục chỉnh mức khi phát. Không áp cho YouTube Music và MV chính thức | Nén độ động khi phát | — | [CT] [YouTube Help](https://support.google.com/youtube/answer/14106294?hl=en) |
| YouTube: file tải lên | AAC-LC hoặc Opus, stereo, 48 kHz, 384 kbps | — | — | [CT] [YouTube Help](https://support.google.com/youtube/answer/1722171?hl=en) |
| Spotify | −14 (Normal), −11 (Loud), −19 (Quiet) | Cả hai chiều. Khi nâng bản nhỏ vẫn chừa 1 dB cho codec nén. Chế độ Loud có limiter ở −1 dB (đỉnh mẫu), attack 5 ms, release 100 ms | ≤ −1 dBTP; ≤ −2 dBTP nếu master to hơn −14 LUFS | [CT] [Spotify](https://support.spotify.com/us/artists/article/loudness-normalization/) |
| Facebook, Instagram | Đích do app đặt theo ngữ cảnh (loa máy, tai nghe, tiếng ồn). Meta không công bố số | Meta nói đưa "độ to trung bình mọi phiên về cùng đích". Chưa tìm được nguồn nói rõ có nâng bản nhỏ không | Chưa tìm được nguồn | [CT] [Meta Engineering](https://engineering.fb.com/2023/04/11/video-engineering/high-quality-audio-xhe-aac-codec-meta/) |
| TikTok | Chưa tìm được nguồn | Chưa tìm được nguồn | Chưa tìm được nguồn | Một bài tổng hợp năm 2026 cũng ghi Meta và TikTok không công bố số: [Fora Soft](https://www.forasoft.com/learn/audio-for-video/articles-audio/lufs-targets-per-platform-2026) |
| EBU R 128 (phát sóng) | −23,0 LUFS | Bắt buộc với bên sản xuất | ≤ −1 dBTP; codec nén −2 dBTP | [CT] mục 0 |
| AES (streaming âm thanh) | TD1004: −16 đến −20 LUFS. TD1008: nhạc −16, lời −18 LUFS | Khuyến nghị cho bên phân phối, không phải mức để master | ≤ −1 dBTP ở đầu vào codec. TD1008 §7B: codec 256 kbps có thể chịu −0,5 dBTP; bitrate thấp cần hạ dưới −1 | [TC] mục 0 |
| Game (IESD 2015, để tham khảo) | Console −24 LUFS ±2. Mobile −16 LUFS ±2, LRA 10–15 LU | — | Console ≤ −1 dBTP | [TC] [IESD](https://www.audiogang.org/wp-content/uploads/2015/04/IESD-Mix-Ref-Levels-v03.02.pdf) |

### 2.2 Video ngắn trên mạng xã hội nên master bao nhiêu

Chưa tìm được chuẩn chính thức riêng cho video ngắn mạng xã hội. Lập luận:

1. YouTube đo được ở khoảng −14 LUFS và chỉ hạ, không nâng [ĐO]. Bản thấp hơn −14 sẽ phát nhỏ hơn video khác đúng bằng phần thiếu.
2. Spotify chính thức dùng −14 LUFS [CT]. Đây không phải nền tảng video, nhưng là mốc chung của nhiều dịch vụ.
3. Meta chuẩn hóa ở app, không công bố số [CT]. Trên app bản mới, master ở mức nào cũng bị đưa về đích của app. TikTok chưa rõ.
4. Các khuyến nghị −16 đến −20 của AES và EBU s2 dành cho dòng âm thanh và đài phát sóng. TD1008 ghi rõ không dành cho âm kèm hình.

→ **Đề xuất: −14 LUFS integrated, đo trên file stereo cuối cùng. True peak ≤ −1 dBTP là trần cứng, nên ≤ −2 dBTP.** Lý do của mức −2: nền tảng sẽ nén lại file. EBU Tech 3344 đặt limiter −2 dBTP trước encoder, Spotify yêu cầu ≤ −2 với master to hơn −14, ATSC dùng −2. [SL dựa trên các nguồn trên]

### 2.3 So sánh −16 và −14 LUFS

| | −16 LUFS (đang dùng) | −14 LUFS |
|---|---|---|
| YouTube | Phát nhỏ hơn video −14 khoảng 2 dB, không được bù | Không bị hạ, không bị nâng |
| Dịch vụ nâng cả bản nhỏ (kiểu Spotify) | Được nâng lên nếu còn chỗ đỉnh | Giữ nguyên |
| App Meta bản mới | App tự đưa về đích, khác biệt nhỏ | Như bên trái |
| Chỗ cho đỉnh | Với TP −1: PLR tối đa 15 dB | Với TP −1: PLR tối đa 13 dB; với TP −2: 12 dB |
| Khớp chuẩn | Mép trên của AES TD1004 (−16 đến −20) và của EBU s2 | Khớp mốc YouTube và Spotify |
| Với phim này | PLR của MP4 là 10,8 dB | Chỉ cần +2 dB. TP thành −3,2 dBTP, không phải ép thêm |

Lợi của −16: còn nhiều chỗ cho đỉnh, hợp với mix nhiều gai nhọn. Hại: thua 2 dB trên YouTube và trên mọi nền tảng không chuẩn hóa. Lợi của −14: ngang mặt bằng chung. Hại: phim có PLR trên 13 dB sẽ phải ép limiter. Phim này chỉ có PLR 10,8 dB nên lên −14 không mất gì. [SL]

---

## 3. Cân bằng nhạc nền và SFX khi không có lời đọc

### 3.1 Nhạc nên thấp hơn SFX bao nhiêu

**Chưa tìm được nguồn chuẩn** cho số dB hay LU cụ thể. Những gì có nguồn:

- EBU R 128 đo cả chương trình, không đo riêng lời, nhạc hay SFX [CT].
- EBU Tech 3343 ([link](https://tech.ebu.ch/docs/tech/tech3343.pdf)) nói mức của từng thành phần là quyết định nghệ thuật [CT]. Cảm giác to do "âm tiền cảnh" quyết định: giọng, nhạc tiêu đề, **SFX chủ chốt**.
- Cũng theo Tech 3343: tiếng cụng ly có đỉnh cao mà độ to thấp (PLR cao). Một đoạn guitar nén có độ to gần bằng đỉnh. Hai tiếng có cùng đỉnh thì guitar to hơn nhiều. Vì vậy không so SFX với nhạc bằng đỉnh. [CT]
- Blog của Krotos (hãng làm công cụ âm thanh, 2025) đưa quy tắc ước lượng: nhạc khoảng −20 dB; tiếng hit, crack từ −20 đến −10 dB. Bài không ghi đơn vị đo. [TC, độ tin thấp] [link](https://krotos.studio/blog/how-to-balance-music-and-sound-effects)

Hệ quả cho cách đo [SL]: so integrated của bus nhạc (liên tục) với bus SFX (thưa, gai) sẽ ra chênh lệch lớn mà không phản ánh tai nghe. Nên so theo từng cú: Momentary 400 ms, hoặc RMS trong dải tần của tiếng, như QA ping của dự án đang làm.

### 3.2 Ducking (hạ nhạc khi SFX nổ)

**Chưa tìm được nguồn cho ducking theo SFX.** Các nguồn dưới đây đều cho trường hợp hạ nhạc dưới lời nói:

| Nguồn | Mức hạ | Attack | Release / fade |
|---|---|---|---|
| [Audacity Auto Duck](https://manual.audacityteam.org/man/auto_duck.html), mặc định [CT] | −12 dB, ngưỡng −30 dB RMS | fade xuống 0,5 s | fade lên 0,5 s, giữ tối thiểu 1 s |
| [Vindral Composer](https://composer-docs.vindral.com/operators/operators-sidechain-ducking.html) [CT, tài liệu hãng] | −6 đến −12 dB là hạ nhẹ; từ −30 dB trở xuống thì nhạc gần như mất | 1–10 ms: hạ tức thì. 50–200 ms: mềm hơn nhưng lọt đầu tiếng | 50–200 ms: hồi nhanh nhưng dễ nghe "bơm". 500–1500 ms: giữ nhạc thấp qua các khoảng nghỉ |
| [Sound On Sound 2010](https://www.soundonsound.com/node/4908058) (Len Sasso) [TC] | ratio vô cực cho ducking dưới lời | — | khoảng 100 ms ở cuối clip |

### 3.3 LRA cho video ngắn xem trên điện thoại

- EBU không khuyên dùng LRA cho bài ngắn hơn 1 phút, vì LRA dựa trên cửa sổ 3 s nên có quá ít điểm dữ liệu ([R 128](https://tech.ebu.ch/files/live/sites/tech/files/shared/r/r128v5_0.pdf), [R 128 s1](https://tech.ebu.ch/docs/r/r128s1.pdf)) [CT]. Thay vào đó, R 128 s1 giới hạn **Max Short-term ≤ đích + 5 LU**.
- EBU R 128 s2 xếp điện thoại vào nhóm "ít chỗ khuếch đại, tiếng ồn nền cao" [CT]. Tech 3343 nói nền tảng như vậy có thể cần LRA thấp hơn, nhưng không cho số [CT].
- IESD khuyên game mobile LRA 10–15 LU [TC]. Số này dành cho phiên chơi dài, không áp cho phim 21 s.
- → **Chưa tìm được nguồn** cho số LRA của video ngắn hơn 1 phút trên điện thoại.

---

## 4. Mức theo loại SFX

| Loại | Số dB có nguồn | Nguyên tắc có nguồn |
|---|---|---|
| Tick, click giao diện | chưa tìm được nguồn | PLR cao (Tech 3343). Năng lượng ở 1–5 kHz, nơi tai nhạy nhất (ISO 226). Trọng số K cộng thêm 2–3 dB (mục 1.4) |
| Pop | chưa tìm được nguồn | như trên |
| Whoosh | chưa tìm được nguồn | — |
| Va chạm nhẹ | chưa tìm được nguồn | — |
| Impact lớn | chưa tìm được nguồn | Giới hạn chung: Max Short-term ≤ đích + 5 LU (R 128 s1), TP ≤ −1 dBTP |
| Riser | chưa tìm được nguồn | — |
| Logo sting, sub drop | chưa tìm được nguồn | Sub được đồng hồ LUFS tính nhỏ đi 5–6 dB (mục 1.4). Ở 40 phon, 50 Hz phải mạnh hơn 1 kHz 38 dB mới nghe to bằng (mục 1.3) |

**Nhóm nào nên nổi rõ nhất.** Tech 3343 nói "âm tiền cảnh" (giọng, nhạc tiêu đề, SFX chủ chốt) quyết định cảm giác to [CT]. Phim không lời thì SFX mang ý chính đóng vai tiền cảnh. Chọn tiếng nào là quyết định nội dung, không phải quyết định kỹ thuật.

**Giữ chỗ đỉnh cho tiếng trầm (sub):**

- Sub tốn chỗ đỉnh mà góp ít LUFS: 50 Hz bị trọng số K tính nhỏ đi 4,6 dB [TÍNH].
- Lớp cùng pha cộng biên độ, tới +6 dB ([sengpielaudio](https://sengpielaudio.com/calculator-coherentsources.htm)). Sub drop, kick và bass đạt đỉnh cùng lúc là chỗ dễ vượt trần nhất.
- Codec nén làm đỉnh vượt lên, bitrate càng thấp càng vượt nhiều (TD1008 §7B, [TC]). EBU Tech 3344 đặt limiter −2 dBTP trước encoder [CT].
- [Sound On Sound 1998](https://www.soundonsound.com/reviews/waves-maxxbass) (Paul White, bài review Waves MaxxBass) [TC]: hạ phần trầm gốc khoảng 3 dB, rồi thêm hài cao hơn khoảng một quãng tám để bù cảm giác trầm.
- [SL]:
  - lọc bỏ dưới khoảng 30 Hz, vì trọng số K tính nhỏ đi 9 dB ở 30 Hz và loa nhỏ không phát được;
  - không để đỉnh sub trùng đỉnh kick;
  - đo TP trên file AAC đã giải mã, không đo trên WAV.

---

## 5. Loa điện thoại và lớp trung cho tiếng trầm

| Dữ kiện | Nguồn |
|---|---|
| Loa Knowles "Donau Slim" 11×15×3 mm cho smartphone: cộng hưởng 800 Hz ±10 % trong hộp sau 1 cm³, nhà sản xuất gọi là "thấp nhất". Phép thử độ bền dùng lọc cắt trầm 12 dB/oct ở 800 Hz | [CT] [datasheet](https://cdn.eicom.ru/media/PDF/440124.pdf) |
| Bằng sáng chế của Dolby: với thiết bị cầm tay, "tần số thấp nhất" của nội dung là 100–500 Hz, cần ống dẫn âm để bù | [CT] [US10536769B2](https://patents.google.com/patent/US10536769B2/en) |
| Larsen & Aarts (JAES, 2002): dùng hài để tạo ảo giác trầm qua loa nhỏ ("virtual bass") | [NC] [TU/e](https://research.tue.nl/en/publications/reproducing-low-pitched-signals-through-small-loudspeakers/) |
| MaxxBass tạo hài cao hơn khoảng một quãng tám. Hài cho cảm giác trầm nhưng không cho cảm giác rung vật lý | [TC] [Sound On Sound](https://www.soundonsound.com/reviews/waves-maxxbass) |

- **Mốc "~200 Hz": chưa tìm được nguồn đo** cho điện thoại đời mới. Dữ liệu loa linh kiện ở trên cho thấy mốc thực có thể cao hơn: vài trăm Hz, tới khoảng 800 Hz ở loa nhỏ.
- **Lớp trung 300 Hz–2 kHz: chưa có nguồn cho dải cụ thể này, nhưng hướng làm có nguồn** (hài, virtual bass). [SL]: dồn năng lượng lớp trung vào 400 Hz–2,5 kHz, cho tiếng "cắc" đầu cú lên tới khoảng 4 kHz. Dự án đang có:
  - `phone_layer` dải 250–2500 Hz;
  - lớp phone của cú accent dải 400–4000 Hz;
  - QA giả lập loa điện thoại bằng lọc dải 400–8000 Hz.

  Các dải này nhất quán với dữ liệu trên.

---

## 6. Đồng bộ âm và hình

| Nguồn | Âm sớm (trước hình) | Âm trễ (sau hình) | Ghi chú |
|---|---|---|---|
| ITU-R BT.1359 (1998), ngưỡng nhận ra [CT] | 45 ms | 125 ms | Thử ở Nhật, Thụy Sĩ, Úc trên tư liệu truyền hình NTSC và PAL |
| ITU-R BT.1359, ngưỡng chấp nhận [CT] | 90 ms | 185 ms | |
| ITU-R BT.1359, chuỗi phát sóng [CT] | 22,5 ms | 30 ms | |
| EBU R37-2007, mỗi khâu [CT] | 5 ms | 15 ms | |
| EBU R37-2007, đầu đến cuối [CT] | 40 ms | 60 ms | Ngưỡng 50 % người xem nhận ra lệch khẩu hình |
| ATSC IS-191 (2003), đầu vào encoder [TC] | 15 ms | 45 ms | Bài TV Technology ghi cả chuỗi là sớm 30 ms, trễ 90 ms |
| Dixon & Spitz 1980, búa đóng (trích qua Heide & Maempel) [NC] | 75 ms | 188 ms | |
| Heide & Maempel 2010, tiếng clapperboard [NC] | Âm trễ ít hơn 1,7 ms, kể cả trùng khung, đã bị nhận ra là lệch | 75,8 ms | Nghe như trùng nhau khi âm trễ 32,4–38,7 ms. Mức người nghe thích: âm trễ 47,5 ms. Khuyên âm trễ 0–80 ms, không để âm sớm. 105 người nghe (51 người làm dựng phim, âm thanh), màn CRT, mức lệch thử theo bước 40 ms |

- Âm sớm bị nhận ra nhanh hơn âm trễ. Lý do tự nhiên: ngoài đời ánh sáng luôn tới trước âm thanh.
- Hoffner (TV Technology, 2004): trong chuỗi phát, hình thường bị trễ nhiều hơn tiếng, nên tiếng hay bị **sớm** [TC]. Máy chiếu và TV ở hội thảo cũng là một khâu trong chuỗi phát.
- Ở 60 fps: 1 khung = 16,7 ms = 800 mẫu ở 48 kHz.
  - Trễ 1 khung: nằm trong mọi chuẩn.
  - Sớm 1 khung: đã vượt mức sớm 15 ms của ATSC và ngưỡng của Heide & Maempel.
- → **Đặt tiếng va chạm trễ 1 khung, không đặt trùng khung.** Theo dữ liệu tiếng va của Heide & Maempel, đặt trùng khung là đã ở vùng tai nghe "âm hơi sớm". [NC + SL]

---

## 7. Áp dụng cho phim 21 s này

### 7.1 Hiện trạng

Đo lại ngày 22/10, chỉ đọc, trên MP4 giao bản 2.

| I | TP | LRA | Max S | Max M | PLR | Định dạng |
|---|---|---|---|---|---|---|
| −16,0 LUFS | −5,2 dBTP | 6,4 LU | −14,0 LUFS (khoảng 16,0 s) | −12,6 LUFS (khoảng 15,1 s, tràn xanh) | 10,8 dB | AAC stereo 48 kHz, L = R |

MP4 là master mono tách ra hai kênh, mỗi kênh −3 dB. Vì vậy MP4 đo stereo vẫn ra −16,0 LUFS như WAV mono, còn TP thấp hơn WAV 3 dB (WAV: −2,2 dBTP).

### 7.2 Master (file giao)

| Thông số | Đặt | Căn cứ |
|---|---|---|
| Integrated | **−14,0 LUFS**, đo trên MP4 stereo cuối, sai số ±0,5 LU | Mục 2.2 |
| True peak | **≤ −2,0 dBTP** trên MP4. Trần cứng −1,0 | EBU Tech 3344, Spotify, ATSC |
| Max Short-term | **≤ I + 5 LU = −9 LUFS** | Quy tắc +5 LU của R 128 s1, áp sang đích −14 [SL] |
| LRA | Chỉ ghi lại, không chấm đạt hay trượt. Mục "LRA 5–8 LU" của lane A nên thay bằng Max Short-term | R 128 và R 128 s1 không dùng LRA cho bài ngắn hơn 1 phút |
| Kênh | Stereo L = R, 48 kHz, AAC-LC, 320–384 kbps | YouTube khuyên AAC-LC stereo 48 kHz 384 kbps |
| Cách lên −14 | Cộng **+2,0 dB ở bước stereo, sau limiter**, không thêm limiter. Ví dụ khi mux, dùng hệ số 0,891 (−1 dB) mỗi kênh thay cho 0,708 (−3 dB). Hoặc master thẳng ở miền stereo như lane A đề xuất | [TÍNH] |
| Kết quả dự kiến | I −14,0 · TP −3,2 dBTP · Max S −12,0 · Max M −10,6 · PLR 10,8 dB. Limiter không ép thêm (ép tối đa vẫn 4,66 dB ở logo) | [TÍNH] |
| Chú ý | Không nâng WAV mono +2 dB rồi dùng như file giao: WAV sẽ có TP −0,2 dBTP, vượt trần −1 | [TÍNH] |
| Chiếu ở hội thảo | Dùng file stereo. WAV mono phát ra hai loa ở cùng mức sẽ to hơn khoảng 3 LU | [CT] [Tech 3344 §6.16](https://tech.ebu.ch/docs/tech/tech3344.pdf), [Auphonic](https://auphonic.com/blog/2020/06/09/loudness-normalization-mono-productions/) |
| Phát sóng truyền hình (nếu cần) | Làm bản riêng. EBU: −23 LUFS (bớt 9 dB từ bản −14), TP ≤ −1. ATSC: −24 LKFS, TP ≤ −2 | [CT] |

### 7.3 Từng nhóm âm

Cột "Hiện tại" lấy từ `g6-am-thanh.md` bản 2, đã được Minh duyệt. **Mọi số trong cột "Đích" là [SL]**: các chuẩn không quy định mức dB cho từng loại SFX. Cộng +2 dB ở bước master giữ nguyên mọi chênh lệch dưới đây.

| Nhóm | Vai trò | Đích đề xuất | Hiện tại |
|---|---|---|---|
| Ping báo tin | Ý chính của phim | Trong dải của ping: ≥ +3 dB so với nhạc (sàn +2 dB) | +3,0…+3,4 dB (b1 +7,2) |
| Tick hứng | Nhịp chính, tiền cảnh | ≥ +6 dB so với nhạc trong dải 0,8–6 kHz. Không nâng thêm: dải này tai nhạy nhất, dễ chói khi vặn to | +8…+14 dB |
| Tick thẻ CRM, tick dòng, tick nút CTA | Phụ | Thấp hơn tick hứng 3–6 dB trong cùng dải | Chưa đo riêng |
| "Bụp" tin bay ra (pop) | Phụ | Khoảng như ping: ≥ +2 dB trong dải của nó, thấp hơn tick hứng | Chưa đo riêng |
| Whoosh, riser, swell | Nối cảnh | Momentary của tiếng (solo) không vượt Momentary của nhạc tại đó. Riser kết hoặc đạt đỉnh đúng khung cú chính, không to hơn cú chính | PLR bus chuyển cảnh 18,4 dB (bản 1) |
| Va chạm nhẹ (đáp nhỏ, tok sừng, nảy) | Vật lý | Nghe được qua giả lập loa điện thoại 400–8000 Hz. Không cần nổi hơn nhạc | — |
| Impact lớn (đáp sau nhảy, tràn xanh) | Cao trào | Limiter ép (RMS 300 ms) ≤ 3 dB, theo lane A. Max S toàn phim ≤ I + 5 LU | Ép 1,30 dB ở cú đáp; Max M = I + 3,4 LU |
| Logo sting + sub drop | Kết, tiền cảnh | Qua giả lập loa điện thoại, logo ≥ thân đoạn đuổi (0 dB trở lên). Nếu thiếu, nâng lớp phone của hit và sub drop khoảng +2 dB trước khi hạ nhạc. Sub: lọc dưới khoảng 30 Hz, không trùng đỉnh kick, TP sau AAC ≤ −2 dBTP | Qua giả lập: −1,1 dB (WARN) |
| Nhạc nền | Thảm | Chấm theo từng cú như các dòng trên, không chấm "nhạc − SFX (integrated của bus) ≤ 2 LU". Nếu cần ducking cho cú lớn: hạ 2–4 dB, attack ≤ 10 ms, release 150–250 ms (không quá nửa phách ở 120 BPM) | Bus nhạc to hơn bus SFX 5,2 LU |

**Nhóm nổi rõ nhất:** ping báo tin, tick hứng, logo. Ping là ý chính theo điều phối 21/10, và đúng vai "SFX chủ chốt" trong Tech 3343.

### 7.4 Đồng bộ (60 fps)

- **Va chạm:** giữ đỉnh **trễ 1 khung (16,7 ms)** sau hình như đang làm. Vật nặng có thể trễ tới 2 khung (33 ms), vẫn sát điểm "nghe trùng" 32–39 ms. **Không bao giờ để âm sớm.**
- **Whoosh, riser:** kết hoặc đạt đỉnh đúng khung sự kiện (giữ quy ước hiện tại). Căn theo đỉnh tiếng, không theo đầu file.
- **Hit logo, cắt nhạc:** hiện đặt đúng khung. [SL] Có thể dời hit logo trễ 1 khung cho cùng cảm giác với các cú va chạm.

### 7.5 Kiểm trước khi giao

- Đo trên MP4 cuối, không đo trên WAV:
  - I, LRA, TP: `ffmpeg -i <mp4> -af ebur128=peak=true -f null -`
  - Max S, Max M: thêm `-v verbose` và `framelog=verbose`.
- Nghe trên điện thoại thật, ở khoảng 1/3 âm lượng rồi ở mức to. Mục 1.3 cho thấy nghe nhỏ thì mất trầm nhiều nhất.
- Sau khi đăng YouTube: mở "Stats for nerds". Bản −14 sẽ hiện mức chỉnh khoảng 0 dB.

---

## 8. Chưa tìm được nguồn hoặc chưa chắc

- Mức đích và cách chuẩn hóa của TikTok. Số LUFS của Meta. Tài liệu chính thức của YouTube về −14 LUFS (hiện chỉ có số đo của bên thứ ba).
- Bản gốc AES TD1004, TD1008, AES71 (video OTT), AES77 (streaming): aes.org chặn truy cập. Số AES trong báo cáo lấy qua nguồn thứ cấp.
- ATSC A/85 đã sửa đổi tháng 7/2026, có thêm phụ lục streaming ([SVG](https://www.sportsvideo.org/2026/07/16/atsc-releases-first-major-revision-to-a-85-audio-loudness-recommended-practice-since-2013/)). Tôi chưa xem được số mới; số trong báo cáo là bản 2013.
- Mức dB cho từng loại SFX, mức nhạc so với SFX, ducking theo SFX: không có nguồn chuẩn. Mọi số ở mục 7.3 là [SL].
- LRA cho video ngắn hơn 1 phút trên điện thoại.
- Đáp tuyến loa của điện thoại đời mới (mốc ~200 Hz). Bảng ISO 226 tính theo hệ số bản 2003, bản 2023 chỉnh nhẹ.

## 9. Danh mục nguồn

| # | Nguồn | Link |
|---|---|---|
| 1 | ITU-R BS.1770-5 (11/2023) | https://www.itu.int/rec/R-REC-BS.1770-5-202311-I/en |
| 2 | EBU R 128 v5.0 (2023) | https://tech.ebu.ch/files/live/sites/tech/files/shared/r/r128v5_0.pdf |
| 3 | EBU R 128 s1 (2020) | https://tech.ebu.ch/docs/r/r128s1.pdf |
| 4 | EBU R 128 s2 v3.0 (2023) | https://tech.ebu.ch/files/live/sites/tech/files/shared/r/r128s2v3_0.pdf |
| 5 | EBU Tech 3341, 3342, 3343 (2023) | https://tech.ebu.ch/docs/tech/tech3341.pdf · https://tech.ebu.ch/docs/tech/tech3342.pdf · https://tech.ebu.ch/docs/tech/tech3343.pdf |
| 6 | EBU Tech 3344 v2.1 (2016) | https://tech.ebu.ch/docs/tech/tech3344.pdf |
| 7 | EBU R37-2007 | https://tech.ebu.ch/docs/r/r037.pdf |
| 8 | ITU-R BT.1359 (1998) | https://itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.1359-0-199802-S!!PDF-E.pdf |
| 9 | ATSC A/85:2013 | https://www.atsc.org/wp-content/uploads/2025/06/A85-2013-with-Corrigendum-No-1.pdf |
| 10 | ATSC IS-191 (R. Hoffner, TV Technology 2004) | https://tvtechnology.com/opinions/atsc-recommends-av-sync-rules |
| 11 | AES TD1004 (qua Production Expert) | https://www.production-expert.com/home-page/2015/11/17/aes-release-recommendations-for-loudness-of-audio-streaming-and-network-file-playback |
| 12 | AES TD1008 (qua Ian Shepherd, M. Thornton, trích §4 và §7B) | https://productionadvice.co.uk/td1008/ · https://www.production-expert.com/production-expert-1/aes-update-loudness-recommendations-for-audio-only-streaming · https://raw.githubusercontent.com/M-Igashi/baken/main/docs/true-peak-ceiling.md |
| 13 | Spotify for Artists | https://support.spotify.com/us/artists/article/loudness-normalization/ |
| 14 | YouTube −14 LUFS (Ian Shepherd) | https://www.meterplugs.com/blog/2019/09/18/youtube-changes-loudness-reference-to-14-lufs.html |
| 15 | YouTube Help: Stable volume; thông số tải lên | https://support.google.com/youtube/answer/14106294?hl=en · https://support.google.com/youtube/answer/1722171?hl=en |
| 16 | Meta Engineering: xHE-AAC | https://engineering.fb.com/2023/04/11/video-engineering/high-quality-audio-xhe-aac-codec-meta/ |
| 17 | Fora Soft: mức LUFS theo nền tảng (2026) | https://www.forasoft.com/learn/audio-for-video/articles-audio/lufs-targets-per-platform-2026 |
| 18 | sengpielaudio | https://sengpielaudio.com/calculator-loudness.htm · https://sengpielaudio.com/calculator-coherentsources.htm |
| 19 | Wikipedia: Sone, Equal-loudness contour, DBFS, Crest factor | https://en.wikipedia.org/wiki/Sone · https://en.wikipedia.org/wiki/Equal-loudness_contour · https://en.wikipedia.org/wiki/DBFS · https://en.wikipedia.org/wiki/Crest_factor |
| 20 | Hệ số ISO 226:2003 (mã J. Tackett) | https://dsprelated.com/showcode/174.php |
| 21 | Datasheet Knowles Donau Slim | https://cdn.eicom.ru/media/PDF/440124.pdf |
| 22 | Dolby US10536769B2 | https://patents.google.com/patent/US10536769B2/en |
| 23 | Larsen & Aarts, JAES 2002 | https://research.tue.nl/en/publications/reproducing-low-pitched-signals-through-small-loudspeakers/ |
| 24 | Sound On Sound: Waves MaxxBass (1998); Live Side-chain Compression (2010) | https://www.soundonsound.com/reviews/waves-maxxbass · https://www.soundonsound.com/node/4908058 |
| 25 | Heide & Maempel, Tonmeistertagung 2010 | https://www.simpk.de/fileadmin/user_upload_sim/Dokumente/Forschung/Themen/Abteilung_III/Publikationen/Heide_Maempel_2011_Die_Wahrnehmung_audiovisueller_Synchronitaet_in_elektronischen_Medien.pdf |
| 26 | Auphonic: mono và dual mono | https://auphonic.com/blog/2020/06/09/loudness-normalization-mono-productions/ |
| 27 | Audacity Auto Duck; Vindral Composer ducking | https://manual.audacityteam.org/man/auto_duck.html · https://composer-docs.vindral.com/operators/operators-sidechain-ducking.html |
| 28 | Krotos blog (2025) | https://krotos.studio/blog/how-to-balance-music-and-sound-effects |
| 29 | IESD Mix Ref Levels v03.02 (2015) | https://www.audiogang.org/wp-content/uploads/2015/04/IESD-Mix-Ref-Levels-v03.02.pdf |
