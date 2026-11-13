# Khung dựng — OPA Agent × Pancake (After Effects native)

21/10/2026 · 16:9, 1920×1080, 30 fps, 36 s (1.080 khung, khung đầu là 0)
Trạng thái: **bản giao v10 (23/10/2026)**: `out/review/OPA-Agent-Pancake_v10.mp4` = hình v08 + URL thật trên nút CTA + âm v09 (68 SFX theo chuyển động, nhạc tự tổng hợp; quanh lời bỏ 4 SFX, chỉnh 7, còn 64) + giọng đọc `VOICE/1023.MP3`, master −16,0 LUFS, đỉnh thật −3,5 dBTP; đã tự kiểm và rà chéo âm bằng agent (mục 6c). Hình v08 và âm v09 bạn đã duyệt ngày 22/10. Còn chờ: bạn duyệt v10 (lưu ý câu 5 đọc "Oping"), Hùng duyệt đăng. Bản cũ nằm ở `out/review/_ban-cu`.

## 1. Brief đã chốt

- **Mục tiêu:** giới thiệu OPA Agent — AI bán hàng cho shop dùng Pancake, đi từ quá tải tin nhắn đến tự động hóa và giải phóng thời gian.
- **Người xem:** chủ shop online, người quản lý nhiều trang, nhân viên trực page đang dùng Pancake/Pancake POS.
- **Thông điệp:** "OPA lo phần trả lời, shop lo phần bán!" (trong lời đọc cảnh 5).
- **Đã khóa:** trình tự Hook → Nỗi đau → Giải pháp → Giải phóng → CTA; chữ và lời theo kịch bản; tên OPA Agent, Pancake/Pancake POS; hoạt hình 2D, mascot Bò OPA, đi từ tối sang sáng; cảnh cuối nền xanh thương hiệu.
- **Bạn chốt 21/10:**
  - Cài Fraunces Italic 800 đúng bản V2 đã render, tên `Fraunces OPA ExtraBold Italic`.
  - "OPING" là chỗ chờ URL: nút CTA hiện `[URL]`, sửa ở comp `TXT_S5_URL`.
  - Mốc cảnh 2→3 dời sang **13,5 s**; mốc: 0–5 / 5–13,5 / 13,5–22 / 22–30 / 30–36 s.
  - Giọng đọc bạn gửi file sau; project có lớp giữ chỗ kèm marker từng câu; MP4 duyệt chỉ có SFX.
  - Duyệt gu đoạn mẫu, giao dựng hoàn thiện cảnh 2–5 và các điểm nối.
- **Bạn chốt 22/10:** duyệt bản hoàn thiện v08; giao chọn SFX theo từng chuyển động từ kho `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx`, chọn nhạc nền, đặt mức theo research decibel (bản v09, mục 6b); **duyệt phần âm v09** (nhạc nền tự tổng hợp, `assets/music/nhac-nen-opa-agent.wav`, MD5 01881e83…, dựng lại từ `tools/audio/score_agent.py` ra đúng từng bit).
- **Bạn gửi 23/10:** giọng đọc `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/VOICE/1023.MP3` (36,0 s, khớp lời kịch bản; câu 5 đọc "ngay tại Oping") và URL `https://chat.overpowers.agency/` (nút CTA hiện `chat.overpowers.agency`).

### Giả định và lựa chọn đảo ngược được

| Chỗ | Đã chọn | Lý do |
|---|---|---|
| fps | 30 fps theo brief | BRAND-SPEC ghi 16:9 = 60 fps (chốt 19/10); brief mới ghi 30. Đổi 60 fps trong AE giữ nguyên giây, không phải dựng lại. |
| Màu | Đêm #003C99 (cảnh 1–2) → trắng (3–4) → xanh #0068FF (5) | Tối → sáng như brief; nền phẳng kiểu V2 |
| Nhân vật chủ shop | Vẽ phẳng bằng đúng 5 màu OPA: da #E6F0FF, tóc đen, áo trắng, ghế xanh | Palette OPA không có màu da; kiểu đơn sắc giữ thương hiệu |
| ✅ 👉 • | Icon vector: tích xanh OPA, mũi tên, dấu "!" đỏ ALERT | Emoji trong AE không ổn định; palette không có xanh lá; ALERT chỉ cho dấu cảnh báo nhỏ |
| Dấu "—" cảnh 5 | Xuống dòng "OPA Agent" / "AI bán hàng cho shop dùng Pancake" | Chữ giữ nguyên, chỉ đổi cách trình bày |
| Glass, glow, đổ bóng, CC Cylinder của mẫu (R7, R8, R9) | Không dùng; nhãn kính R9 thành chip phẳng | Video OPA: phẳng, không bóng đổ, không 3D |
| Luật "7–9 chữ mỗi khung" | Giữ chữ khóa, cho vào từng dòng; cuối cảnh 3 có khoảng 45 chữ trên hình | Kịch bản khóa dài hơn luật; cần bạn xem có chấp nhận không |
| Nhãn giao diện | "24H", "POS", "99+", "Pancake POS"; dữ liệu UI giả | Luật Minh: dòng bắt đầu bằng số thì viết hoa chữ ngay sau; không dùng giao diện thật |
| SFX | 68 cue theo từng chuyển động, 29 file từ kho `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx` (CC0/MIT, không theSOUNDS) chép WAV vào `assets/sfx`; logo âm thanh giữ bản của bộ OPA | Bảng cue kèm lý do và mức: `audio/BANG-CUE-AM-THANH.md`. Âm có cao độ chọn trong giọng La trưởng của nhạc (đo cao độ từng file) |
| Nhạc nền | Tự tổng hợp 36 s, 120 BPM, La trưởng, theo 5 cảnh (`tools/audio/score_agent.py`, bộ nhạc cụ V2/V3); −31 LUFS khi phát | Kho sfx không có bài nhạc nào đủ dài (file dài nhất là bản nghe thử gộp SFX của Kenney); BRAND-SPEC OPA: không nhạc có bản quyền, tự tổng hợp như V2/V3. Dự phòng nếu bạn muốn: 4 bài Mixkit ở kho nhạc mặc định |
| URL trên nút CTA | `chat.overpowers.agency` (bỏ `https://` và `/` cuối), chữ thường; nút giãn theo chữ (742 px), con trỏ bấm sau chữ | Gọn trên nút; URL/tên miền giữ chữ thường như luật tên file (08/10), `tools/qa_chu.py` miễn viết hoa cho dòng là URL |
| Giọng đọc | Dùng nguyên file của bạn, đặt từ 0 s, gain +2,6 dB (giọng ở −16,3 LUFS trong bản trộn) | File đã khớp nhịp 5 cảnh; không cắt ghép câu |
| Khối trang trí nền | Màu đặc theo V2 (`src/v2w/world/tones.ts`): nền đêm dùng khối #0068FF, khung và nền xanh dùng khối #003C99, nền trắng dùng khối #E6F0FF | Bản trước pha độ mờ ra màu ngoài bảng (#0042A9, #1776FD, #005BE1). Muốn khối chìm hơn: sửa fill trong layer `DECO …` của từng cảnh |

## 2. Phương án hình và chuyển động

Ngôn ngữ chung: nền phẳng kiểu V2, khối trang trí màu đặc; máy quay ảo (null `CAM`) trôi **một đường chậm và đều** suốt từng cảnh, hướng trôi chọn để khối chính luôn cách lề; chữ và giao diện gắn vào máy quay; chuyển cảnh liền mạch, không cắt cứng.

- **Cảnh 1 · 0–5 s · Hook (đêm):** chủ shop chau mày gõ phím, đồng hồ quay 3 vòng/5 s tích tắc, 6 tin nhắn bật dồn dập có chấm đỏ, điện thoại rung. Cột chữ: headline theo từ → phụ theo dòng → cụm nhấn "Mỗi ngày?" có khối trắng quét. Máy quay lao vào chồng tin nhắn.
- **Nối 1→2 (4,5–5,3 s):** một tin nhắn trắng giữa chồng tin nở về phía ống kính, phủ kín khung đúng khung cuối cảnh 1; cảnh 2 tan ra từ màn trắng trong 10 khung, máy quay tiếp tục chiều đẩy vào (80 % → 100 %).
- **Cảnh 2 · 5–13,5 s · Nỗi đau (đêm):**
  - Nhịp 1 (5,8 s): hộp thư cuộn liên tục, mỗi tin mới đẩy danh sách lên một ô, "99+" nảy, chấm đỏ chưa đọc → "Hàng chục cuộc chat bỏ dở".
  - Nhịp 2 (8,2 s): câu hỏi lặp lại, câu trả lời giống hệt nhau bật ra, chấm đỏ của câu vừa trả lời tắt → "Trả lời lặp đi lặp lại".
  - Nhịp 3 (10,6 s): phiếu POS mở bằng mask (R10), viền xanh chạy theo mép khối mở; chip số điện thoại, chip địa chỉ bay vào ô; vạch gõ dài ra; con trỏ bấm lưu → "Lên đơn POS thủ công".
  - Cuối cảnh: hộp thư và phiếu rung quá tải.
- **Nối 2→3 (12,9–13,5 s):** Bò OPA trắng lao vào (cúi đầu, dừng có rung tắt dần); đĩa sáng đi cùng Bò, bật sau lưng Bò (Bò chuyển xanh đúng khung đó) rồi nở đều trong 11 khung, phủ kín đúng khung cuối cảnh. Sang cảnh 3, Bò cất cánh từ tốc độ 0, bay vào đầu bảng; đầu bảng hoá xanh từ chỗ Bò đáp.
- **Cảnh 3 · 13,5–22 s · Giải pháp (ngày):**
  - Bảng OPA Agent mở bằng mask (R10) từ góc trên-trái; Bò bay vào đầu bảng và hoá trắng trên nền xanh của đầu bảng.
  - Chip "Pancake POS" cắm vào kèm vòng tỏa lặp lại (1 kết nối).
  - 5 hàng minh họa bật đúng nhịp 5 tính năng: trả lời kèm kho hàng; đơn vào Pancake POS có tích; ảnh chuyển khoản có vạch quét rồi tích; chuông nhắc 24H rung; nút gạt chuyển từ Bò sang nhân viên.
  - Cột chữ: "Chỉ 1 kết nối —" (khối xanh) → headline → 5 tính năng → "Và nhiều hơn thế nữa!".
- **Nối 3→4 (21,2–22 s):** cột chữ thoát R6 (thu nhỏ cả khối); khung bảng hoá xanh ngay tại chỗ, giao diện tắt dưới nó, rồi khung dời đều về đúng khung xanh của cảnh 4.
- **Cảnh 4 · 22–30 s · Giải phóng:** chủ shop trồi lên từ mép dưới khung xanh rồi ngả lưng, hai tay sau gáy, mắt cười; cà phê bốc hơi; tích xanh bay lên từ laptop. Ba dòng "Không cần…" có icon tích.
- **Nối 4→5 (29,1–30 s):** chữ rút, nhân vật trượt xuống, khung xanh nở tăng tốc phủ kín khung đúng khung cuối.
- **Cảnh 5 · 30–36 s · CTA (xanh):**
  - Bò trắng hiện kiểu V2: mõm bật lên theo lò xo, sừng mọc từ gốc, hai vòng tỏa theo sonic logo, rồi thở 1,00–1,03.
  - Chữ: "OPA Agent" theo ký tự → câu định vị → nhãn CTA.
  - Nút `[URL]` bật lò xo, con trỏ bấm, gợn bấm; một gợn nhắc lại và nút thở nhẹ tới hết phim.

## 3. Công thức dùng (từ MOTION-PRESETS.json)

Đại lượng pixel của mẫu đổi theo **em (cỡ chữ)** để giữ đúng tỉ lệ chuyển động (mẫu R1: Position 300 trên chữ 300 px = 1,0 em). Influence giữ nguyên số gốc.

| Mã | Dùng cho | Thông số | Chọn theo | Easing gốc |
|---|---|---|---|---|
| R1 | Headline cảnh 1, 3 | Position [0, 1,0 em], Opacity 0, Blur 0,427 em | Từ | Start 0→100 trong 30 khung; Out 75,217 % / In 75,121 % |
| R2 | Phụ, cụm nhấn, định vị, nhãn CTA | [0, 0,667 em], Opacity 0, Blur 0,667 em | Dòng | 75,322 % / 75,664 % |
| R3 | "Và nhiều hơn thế nữa!", "OPA Agent", "[URL]" | [0, 0,711 em], Opacity 0, Blur 0,356 em | Ký tự | Vào 75,217 % / 75,603 % |
| R5 | Gạch đầu dòng cảnh 2, tính năng cảnh 3, "Không cần…" cảnh 4 | [2,0 em, 0], Opacity 0, Blur 1,0 em | Dòng | 60,752 % / 60,174 % |
| R6 | Cột chữ cảnh 3 thoát | Scale cấp Scene 100 → 86 → 0 | — | Out 0,01 % / In 100 % rồi Out 100 % / In 15,133 % |
| R10 | Mở phiếu POS (cảnh 2), mở bảng OPA Agent (cảnh 3) | Size khối matte 0 → đủ, track matte alpha | — | Out 15,236 % / In 100 % |
| Khối nhấn | "Mỗi ngày?", "Chỉ 1 kết nối —" | Quét từ trái 8 khung; đệm trái 0,12 em, phải 0,22 em, cao 1,26 em; chữ trên khối là bản sao + Fill + track matte | — | EASE_IN_SCENE (0,2; 0,8; 0,2; 1) |
| Lò xo OPA | Icon, tin nhắn, nút, mõm và sừng Bò | Damping 12, stiffness 100: vọt khoảng 9,5 %, đỉnh 0,39 s | — | Không áp vào chữ |

- Transform Opacity của mọi text layer giữ 100; độ mờ 0 nằm ở Animator, đúng như mẫu.
- Blur của chữ là Text Animator Blur; motion blur theo màn trập chỉ bật cho layer chuyển động nhanh.

## 4. Bảng theo cảnh

| Cảnh | Chữ chính xác | Vai trò | Font, cỡ hiệu dụng | Selector, transform | Matte, effect | Quan hệ với hình |
|---|---|---|---|---|---|---|
| 1 | BẠN MẤT / BAO NHIÊU / THỜI GIAN | Headline (tiêu điểm) | Be Vietnam Pro ExtraBold 126 px, dòng 166 | R1 theo từ, ra Start 100→0 | Không | Cột phải x 1010; máy quay đẩy làm bay khỏi khung |
| 1 | Để trả lời khách và lên đơn / Trên Pancake | Phụ | Medium 56 px | R2 theo dòng | Không | Dưới headline 46 px |
| 1 | Mỗi ngày? | Cụm nhấn | Fraunces OPA ExtraBold Italic 80 px | R2 + khối trắng quét, chữ xanh trên khối | Track matte alpha theo khối | Chốt câu hỏi, cùng nhịp đồng hồ |
| 2 | Hàng chục cuộc chat bỏ dở · Trả lời lặp đi lặp lại · Lên đơn POS thủ công | Ba mục song song | SemiBold 50 px, trắng | R5 từ phải; icon "!" lò xo | Không | Mỗi mục khớp một nhịp UI: hộp thư cuộn, câu trả lời lặp, phiếu POS |
| 2 | Còn size M không shop? · Giá bao nhiêu? · Check bill giúp em | Chữ trong UI | Medium 32 px | Dòng tin trượt vào, danh sách cuộn | Mask chữ nhật cắt vùng danh sách | Comp `DONG_TIN_1–3`: sửa một lần đổi mọi lần lặp |
| 3 | Chỉ 1 kết nối — | Cụm nhấn | Fraunces 80 px | R2 + khối xanh, chữ trắng | Track matte | Cùng lúc chip "Pancake POS" cắm vào |
| 3 | OPA tự động hóa toàn bộ / Quy trình bán hàng / Trên Pancake: | Headline | ExtraBold 56 px, dòng 74 | R1 theo từ | Không | Dưới cụm nhấn 34 px |
| 3 | 5 tính năng (nguyên văn) | Mục song song | Medium 40 px, icon tròn xanh 52 px | R5 + icon lò xo | Không | Mỗi dòng ứng một hàng minh họa trong bảng OPA Agent |
| 3 | Và nhiều hơn thế nữa! | Câu chốt | ExtraBold 44 px, xanh | R3 theo ký tự | Không | Cả cột thoát R6 |
| 4 | Không cần tạo App / Facebook phức tạp · Không cần gõ lại một câu hỏi / Hàng trăm lần · Không cần copy-paste từng / Số điện thoại, địa chỉ vào POS | Ba mục song song | Medium 48 px, dòng 64, icon tích 70 px | R5 + icon lò xo | Không | Khớp lời đọc từng vế; bên trái tích bay lên |
| 5 | OPA Agent | Tên (display) | ExtraBold 128 px, trắng | R3 theo ký tự | Không | Cạnh Bò trắng |
| 5 | AI bán hàng cho shop dùng Pancake | Định vị | Medium 46 px | R2 | Không | — |
| 5 | Thử miễn phí ngay tại: + [URL] | CTA | SemiBold 40 px; nút ExtraBold 48 px | R2, R3, lò xo, con trỏ, gợn | Không | Link thật điền vào `TXT_S5_URL` |

<!-- BANG-TU-DONG:BAT-DAU (sinh bởi tools/bang_khung.py từ build/_report.json, không sửa tay) -->
### Bảng thời gian chữ theo khung master

| Text comp | Công thức | Cỡ chữ | Bắt đầu vào | Hiện đủ | Bắt đầu ra | Hết |
|---|---|---:|---|---|---|---|
| TXT_S1_HEADLINE | R1 theo từ | 126 px | f4 (0,13 s) | f34 (1,13 s) | f122 (4,07 s) | f150 (5,00 s) |
| TXT_S1_PHU | R2 theo dòng | 56 px | f28 (0,93 s) | f58 (1,93 s) | f120 (4,00 s) | f146 (4,87 s) |
| TXT_S1_NHAN | R2 theo dòng | 80 px | f52 (1,73 s) | f82 (2,73 s) | f120 (4,00 s) | f146 (4,87 s) |
| TXT_S2_Y1 | R5 dòng từ phải | 50 px | f174 (5,80 s) | f204 (6,80 s) | f370 (12,33 s) | f396 (13,20 s) |
| TXT_S2_Y2 | R5 dòng từ phải | 50 px | f246 (8,20 s) | f276 (9,20 s) | f370 (12,33 s) | f396 (13,20 s) |
| TXT_S2_Y3 | R5 dòng từ phải | 50 px | f318 (10,60 s) | f348 (11,60 s) | f370 (12,33 s) | f396 (13,20 s) |
| TXT_S3_NHAN | R2 theo dòng | 80 px | f413 (13,77 s) | f443 (14,77 s) | theo chuyển cảnh | — |
| TXT_S3_HEADLINE | R1 theo từ | 56 px | f425 (14,17 s) | f455 (15,17 s) | theo chuyển cảnh | — |
| TXT_S3_TINH_NANG_1 | R5 dòng từ phải | 40 px | f449 (14,97 s) | f479 (15,97 s) | theo chuyển cảnh | — |
| TXT_S3_TINH_NANG_2 | R5 dòng từ phải | 40 px | f477 (15,90 s) | f507 (16,90 s) | theo chuyển cảnh | — |
| TXT_S3_TINH_NANG_3 | R5 dòng từ phải | 40 px | f505 (16,83 s) | f535 (17,83 s) | theo chuyển cảnh | — |
| TXT_S3_TINH_NANG_4 | R5 dòng từ phải | 40 px | f533 (17,77 s) | f563 (18,77 s) | theo chuyển cảnh | — |
| TXT_S3_TINH_NANG_5 | R5 dòng từ phải | 40 px | f561 (18,70 s) | f591 (19,70 s) | theo chuyển cảnh | — |
| TXT_S3_CHOT | R3 theo ký tự | 44 px | f585 (19,50 s) | f615 (20,50 s) | theo chuyển cảnh | — |
| TXT_S4_Y1 | R5 dòng từ phải | 48 px | f672 (22,40 s) | f702 (23,40 s) | f856 (28,53 s) | f882 (29,40 s) |
| TXT_S4_Y2 | R5 dòng từ phải | 48 px | f720 (24,00 s) | f750 (25,00 s) | f856 (28,53 s) | f882 (29,40 s) |
| TXT_S4_Y3 | R5 dòng từ phải | 48 px | f766 (25,53 s) | f796 (26,53 s) | f856 (28,53 s) | f882 (29,40 s) |
| TXT_S5_TEN | R3 theo ký tự | 128 px | f912 (30,40 s) | f942 (31,40 s) | theo chuyển cảnh | — |
| TXT_S5_DINH_VI | R2 theo dòng | 46 px | f934 (31,13 s) | f964 (32,13 s) | theo chuyển cảnh | — |
| TXT_S5_NHAN_CTA | R2 theo dòng | 40 px | f956 (31,87 s) | f986 (32,87 s) | theo chuyển cảnh | — |
| TXT_S5_URL | R3 theo ký tự | 48 px | f972 (32,40 s) | f996 (33,20 s) | theo chuyển cảnh | — |

Bản dựng: 46 comp, 388 expression, lỗi expression: 0, lỗi dựng: 0.

### SFX theo chuyển động (chưa có giọng đọc; bảng đầy đủ kèm lý do: `audio/BANG-CUE-AM-THANH.md`)

| Âm | Đỉnh (khung master) | Mức |
|---|---|---:|
| Tin nhan bat 1 | f2 (0,07 s) | -11 dB |
| Tin nhan bat 2 | f12 (0,40 s) | -11 dB |
| Dong ho tac 15 | f15 (0,50 s) | -11.1 dB |
| Tin nhan bat 3 | f21 (0,70 s) | -11 dB |
| Tin nhan bat 4 | f29 (0,97 s) | -11 dB |
| Tin nhan bat 5 | f36 (1,20 s) | -11 dB |
| Tin nhan bat 6 | f42 (1,40 s) | -11 dB |
| Dong ho tac 45 | f45 (1,50 s) | -11.1 dB |
| Dong ho tich 60 | f60 (2,00 s) | -11.1 dB |
| Dong ho tac 75 | f75 (2,50 s) | -11.1 dB |
| Khoi nhan quet (Moi ngay) | f79 (2,63 s) | -13.1 dB |
| Dong ho tich 90 | f90 (3,00 s) | -11.1 dB |
| Dong ho tac 105 | f105 (3,50 s) | -11.1 dB |
| Dong ho tich 120 | f120 (4,00 s) | -11.1 dB |
| Dong ho tac 135 | f135 (4,50 s) | -11.1 dB |
| Tin moi 1 | f171 (5,70 s) | -14.2 dB |
| Canh bao 1 | f176 (5,87 s) | -13.9 dB |
| Tin moi 2 | f189 (6,30 s) | -14.2 dB |
| Tin moi 3 | f213 (7,10 s) | -14.2 dB |
| Tin moi 4 | f237 (7,90 s) | -14.2 dB |
| Canh bao 2 | f248 (8,27 s) | -13.9 dB |
| Tra loi lap 1 | f252 (8,40 s) | -11 dB |
| Tin moi 5 | f263 (8,77 s) | -14.2 dB |
| Tra loi lap 2 | f274 (9,13 s) | -11 dB |
| Tin moi 6 | f285 (9,50 s) | -14.2 dB |
| Tra loi lap 3 | f296 (9,87 s) | -11 dB |
| Tin moi 7 | f307 (10,23 s) | -14.2 dB |
| Canh bao 3 | f320 (10,67 s) | -13.9 dB |
| Tin moi 8 | f335 (11,17 s) | -14.2 dB |
| Go phim 1 | f346 (11,53 s) | -2.6 dB |
| Go phim 2 | f349 (11,63 s) | -3.6 dB |
| Go phim 3 | f352 (11,73 s) | -2.6 dB |
| Tin moi 9 | f355 (11,83 s) | -14.2 dB |
| Go phim 4 | f367 (12,23 s) | -3.6 dB |
| Go phim 5 | f370 (12,33 s) | -2.6 dB |
| Tin moi 10 | f373 (12,43 s) | -14.2 dB |
| Go phim 6 | f376 (12,53 s) | -3.6 dB |
| Bam luu (than) | f381 (12,70 s) | -8 dB |
| Bam luu (tach) | f381 (12,70 s) | -19.9 dB |
| Bam luu (nha) | f385 (12,83 s) | -11.6 dB |
| Bo OPA lao vao | f388 (12,93 s) | -19.8 dB |
| Dia sang bat | f393 (13,10 s) | -11.8 dB |
| Swell sang ngay | f404 (13,47 s) | -15.9 dB |
| Bang OPA mo | f415 (13,83 s) | -12.2 dB |
| Khoi nhan quet (1 ket noi) | f436 (14,53 s) | -13.1 dB |
| Bo dap dau bang | f441 (14,70 s) | -11.9 dB |
| Tinh nang 1 | f451 (15,03 s) | -12.5 dB |
| Ket noi Pancake POS | f457 (15,23 s) | -18.7 dB |
| Tinh nang 2 | f479 (15,97 s) | -12.5 dB |
| Tinh nang 3 | f507 (16,90 s) | -12.5 dB |
| Tinh nang 4 | f535 (17,83 s) | -12.5 dB |
| Tinh nang 5 | f563 (18,77 s) | -12.5 dB |
| Nut gat tiep quan | f574 (19,13 s) | -11.5 dB |
| Cot chu thu R6 | f639 (21,30 s) | -16.8 dB |
| Nhan vat troi len | f669 (22,30 s) | -18.2 dB |
| Dau tich 1 | f674 (22,47 s) | -15.1 dB |
| Dau tich 2 | f722 (24,07 s) | -15.1 dB |
| Dau tich 3 | f768 (25,60 s) | -15.1 dB |
| Khung xanh no tran | f898 (29,93 s) | -15.9 dB |
| Sonic logo OPA | f904 (30,13 s) | -15.4 dB |
| Nut CTA bat | f966 (32,20 s) | -11.7 dB |
| Bam nut CTA (than) | f1025 (34,17 s) | -10.4 dB |
| Bam nut CTA (tach) | f1025 (34,17 s) | -15.1 dB |
| Bam nut CTA (nha) | f1030 (34,33 s) | -10.6 dB |
<!-- BANG-TU-DONG:KET-THUC -->

## 5. Cấu trúc project (`project/OPA-Agent-Pancake_v01.aep`)

```
00_MASTER/                     OPA_AGENT_MASTER_16x9: 5 cảnh nối tiếp, GIONG DOC (1023.MP3, +2,6 dB), MARKER CAU THOAI, AM THANH (SFX + nhạc)
01_CANH (scene)/               S1_MO_DAU, S2_NOI_DAU, S3_GIAI_PHAP, S4_GIAI_PHONG, S5_CTA — mỗi cảnh có null CAM
02_TITLE (thiet ke chu)/       TITLE_S1…S5: vị trí, offset thời gian, khối nhấn, icon đi kèm chữ
03_EDIT_CHU (sua chu o day)/   TXT_*: mỗi comp một layer "TEXT" có Text Animator; DONG_TIN_1–3: câu hỏi trong hộp thư
04_HINH/                       ART_CHU_SHOP_*, ART_MASCOT_BO_OPA(_HIEN), UI_* (hộp thư, danh sách tin, phiếu POS, bảng OPA Agent)
05_CONTROL (mau)/              CONTROL: null BRAND, 6 Color Control; mọi màu shape nối bằng expression
06_AM_THANH/                   AM_THANH_SFX_NHAC: nhạc nền (dưới cùng) + 68 layer SFX + file WAV (assets/sfx, assets/music)
```

- **Đổi chữ:** mở `03_EDIT_CHU` → comp `TXT_…` → sửa layer `TEXT`. Khối nhấn và bong bóng tin nhắn tự giãn theo chữ (`sourceRectAtTime`). Chữ trong UI minh họa khác (chip, nhãn) nằm trong comp `UI_…`.
- **Đổi màu:** sửa Color Control trong `CONTROL > BRAND`; màu chữ đặt trực tiếp trên layer chữ.
- **Giọng đọc:** layer `GIONG DOC (1023.MP3 cua ban)` trong master, từ 0 s, gain +2,6 dB; thay giọng: chạy lại `tools/am_thanh_cues.py` với file mới (tham số thứ hai) rồi dựng lại; marker từng câu ở layer `MARKER CAU THOAI`.
- **Đổi âm:** sửa cue (âm, khung, mức đích) trong `tools/am_thanh_cues.py` → `python -I tools/am_thanh_cues.py "/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx"` (chép file, tính gain, sinh `build/data/am_thanh_cues.jsxinc` và bảng cue) → dựng lại. Nhạc nền: `python tools/audio/score_agent.py ae/opa-agent/assets/music/nhac-nen-opa-agent.wav` (chạy trong thư mục gốc OPA). Khi có giọng đọc: kéo vào master, căn theo marker, giữ nhạc như cũ, rồi chuẩn hoá cả bản về −16 LUFS, đỉnh thật ≤ −2 dBTP.
- **Dựng lại từ đầu:** `python -I tools/ae.py build` (JSX trong `build/`, chạy trong phiên AE headless riêng, không đụng AE đang mở). Render: `python -I tools/ae.py render --comp OPA_AGENT_MASTER_16x9 --start 0 --end 1079 --out …`.
- **Font cần cài:** Be Vietnam Pro (ExtraBold, SemiBold, Bold, Medium) và `assets/fonts/FrauncesOPA-ExtraBoldItalic.ttf` (Fraunces Italic wght 800, Google Fonts v38, OFL).
- **Plugin:** không dùng plugin ngoài; chỉ effect gốc của AE (Fill, Color Control).

<!-- KIEM:BAT-DAU -->
## 6. Tự kiểm và rà chéo (bản v08 = b13, 21/10/2026)

File: `out/review/_ban-cu/OPA-Agent-Pancake_v08.mp4` (H.264 1920×1080, 30 fps, 1.080 khung, gắn nhãn BT.709; AAC 48 kHz chỉ có SFX bộ cũ; hình dùng tiếp ở v09). Ảnh: `KHUNG-HIEN-DU_v08.png` (5 khung đã hiện đủ), `TO-KHUNG-1s_v08.png` (1 khung mỗi giây).

| Nấc | Cách kiểm | Kết quả |
|---|---|---|
| 1. Dựng | `tools/ae.py build`, buộc tính mọi expression rồi gom lỗi | 0 lỗi dựng, 0 lỗi expression · 46 comp · 388 expression |
| 2. Khung đã hiện đủ | 5 khung 3,5 / 12,0 / 20,6 / 28,4 / 35,6 s, xem bằng mắt | Đạt |
| 3. Tờ khung, điểm nối | Tờ 1 khung/giây; dải khung gốc ở 4 điểm nối (140–165, 386–412, 630–670, 880–915), Bò đáp đầu bảng (405–442), phiếu POS (316–356), hơi cà phê | Đạt sau 4 vòng dựng (b10 → b13) |
| 4. Chữ | `tools/qa_chu.py` trên chữ trong project: viết hoa đầu dòng, cỡ ≥ 28 px, font trong bộ, Fraunces chỉ ở cụm nhấn, mục song song cùng kiểu, không font thay thế | Đạt · 31 layer · 39 dòng |
| 5. Màu | Giải mã BT.709, lấy mẫu nền và khối trang trí cả 5 cảnh | Đúng bảng OPA, lệch ≤ 3 mức do mã hoá (#003998 ≈ #003C99, #0067FF ≈ #0068FF) |
| 6. Chuyển động | `tools/v2w/metrics.py --no-flow` (thước đo của V2) | Tĩnh B 0,46 % · Tĩnh A 0 · chuỗi đứng yên dài nhất 2 khung · cắt cứng 0 → **đạt** |
| 7. Âm thanh (chỉ SFX) | ebur128, true peak, đỉnh tức thời; lệch đỉnh SFX so với khung hình | −28,0 LUFS · −8,8 dBTP · M lớn nhất −20,9 LUFS · mọi đỉnh trễ đều +0,63 khung (21 ms, độ trễ mồi AAC của AE) |
| Rà chéo | Agent Q hình–chữ trên b7 (14 mục), Q5 âm thanh trên b7, Q hình–chữ lần 2 trên b11, lần 3 trên b13 | Lần 2: 10/12 lỗi cũ đã hết; tìm thêm Bò mất 1 khung ở 441 (có từ b8), đĩa sáng còn khựng, Bò cất cánh giật, hơi cà phê pha độ mờ → sửa ở b13. Điểm lần 2: chuyển động 7,5 · chữ 8,5 · thương hiệu 8 · kể chuyện 8,5. Lần 3: cả 4 chỗ đạt (đĩa phủ đều 33→98 % qua 393–404, phủ kín đúng 404; Bò cất cánh 1→19→44→63 px/khung), không lỗi cần sửa |

**Sửa trong vòng hoàn thiện (theo rà chéo b7, b11 và tự kiểm b10–b13):**
- Nối 1→2: tin nhắn trắng nở phủ kín khung cuối cảnh 1, cảnh 2 tan ra từ trắng (hết cắt cứng 149→150).
- Đĩa sáng 2→3 đi cùng Bò, bật che trọn Bò rồi nở đều 11 khung thay vì loé 3 khung; Bò đổi xanh đúng khung đĩa bật.
- Bò cảnh 3 giữ xanh tới khung đáp (hết mất Bò ở 441), cất cánh từ tốc độ 0; hơi cà phê thành nét trắng đặc chạy bằng trim.
- Nối 3→4: khung bảng hoá xanh tại chỗ rồi dời về khung cảnh 4 (hết chồng lệch, hết mép bảng ló ra); nhân vật cảnh 4 trồi từ mép dưới khung.
- Máy quay cảnh 2, 3, 4 đổi hướng trôi để khối chính cách lề (mép phải chữ cảnh 4 ≤ x 1788, lề phải ≥ 131 px); cột chữ cảnh 3 hạ 40 px.
- Nhịp chữ: tính năng cảnh 3 cách 28 khung (hàng minh hoạ bật cùng nhịp), mục 3 cảnh 4 vào sớm 24 khung, "OPA Agent" vào ở 30,4 s.
- Phiếu POS có viền xanh ngay khi mở; khối trang trí màu đặc; ping chip "Pancake POS" tách khỏi tick tính năng 1.
- Thư viện dựng: keyframe "LINEAR" trước đây bị AE làm êm hai đầu (trôi máy quay, kim đồng hồ chậm dần ở đầu, cuối); nay chạy đều đúng ý.

**Ghi nhận, để nguyên:** "Lên đơn POS thủ công" (cảnh 2) đọc trọn ~1,4 s, ngắn nhất phim, vì đĩa sáng 2→3 phủ cột chữ từ 393; viền phiếu POS chạm nút lưu ở 326–333 (chỉ thấy khi soi từng khung); khung 404–405 gần trùng (Bò lấy đà, 1 khung).

**Chưa kiểm:** chưa nghe bằng tai (chỉ đo); chưa mở project trong AE có giao diện (project dựng và render bằng phiên AE riêng, không đụng AE đang mở của bạn); chưa có giọng đọc nên chưa trộn master −16 LUFS.

### 6b. Âm thanh v09 (SFX theo chuyển động + nhạc nền, 22/10/2026)

File: `out/review/OPA-Agent-Pancake_v09.mp4` (= b18). Hình trùng v08 (PSNR trung bình 104 dB, thấp nhất 78 dB), chỉ thay âm. Bảng cue đầy đủ kèm lý do, mức và nguồn research: `audio/BANG-CUE-AM-THANH.md`.

| Nấc | Cách kiểm | Kết quả |
|---|---|---|
| Kho, chọn âm | Đo cả 2.982 file (`tools/phan_tich_sfx.py` → `audio/kho_sfx_do.csv`): thời lượng, đỉnh, đỉnh thật, M, độ to tích hợp, độ sáng; đo cao độ các âm có nốt | 68 cue, 30 file; âm có cao độ đều trong giọng La trưởng (3 file dịch cao độ); kho không có bài nhạc nào đủ dài |
| Đồng bộ | Đỉnh từng file đặt vào khung chuyển động; đo lại trên MP4 | Mọi cue trễ đều 0,64 khung (độ trễ AAC của AE), không cue nào lệch riêng |
| Mức | ebur128 trên MP4 (chưa có giọng) | Nhạc riêng −31,1 LUFS khi phát (đích −31); SFX + nhạc −28,0 LUFS, LRA 4,9 LU; độ to ngắn hạn lớn nhất −25,0 LUFS (+3,0 LU so với tích hợp; EBU R 128 s1 cho tới +5) |
| Đỉnh | Đỉnh thật cả bản; dựng lại stem SFX, đo ±40 ms quanh mỗi cue (tính cả âm chồng) | Cả bản −10,9 dBTP; stem SFX ≤ −12,0 dBTP ở mọi cue |
| Nhô trên nhạc | M 400 ms và RMS 50 ms của cue so với nhạc tại chỗ | Mọi cue nhô ≥ +2,6 dB ở cửa sổ 50 ms (Q5 đo b17) |
| Nhạc nền | `tools/audio/score_agent.py`: LRA, lọc 100 Hz, −3 dB ở 2 kHz, vào 1 s, tắt 1,5 s, lặng tuyệt đối 13,1–13,5 s và 29,93–30,4 s | Đạt (Q5 dựng lại trùng từng bit; không click ở chỗ lặng) |
| Rà chéo Q5 | b17: 68 cue đúng khung, nhạc đạt; 4 lỗi cần sửa (2 cú bấm chồng lớp vượt trần đỉnh, giấy POS trễ 7–9 khung, chuông "xong" là Sol trưởng, glass lệch ¼ cung) và 5 nên sửa → sửa hết ở b18 | b18: cả 5 nhóm đã hết, không lỗi mới cần sửa; stem SFX lớn nhất −11,95 dBTP; chuông "xong" thành A4–C#5–E5 (lệch ≤ 2 cent), glass thành A–C#–F# (≤ 8 cent); không cặp âm nào cách dưới 3 khung; SFX lớn nhất −24,2 LUFS (8,2 LU dưới giọng). Điểm: an toàn đỉnh 8 (từ 5), hợp giọng 8 (từ 6). Ghi nhận: nốt đầu chuông "xong" vào trước icon 7 khung (đỉnh đúng icon); riser sớm 2 khung so với khung trắng để chừa đầu câu 2; press/typing/release lệch khoảng 35 cent (tiếng ngắn) |

**Khi lồng giọng đọc (bắt buộc):**
- Đặt giọng khoảng −16,3 LUFS: SFX + nhạc cộng thêm khoảng 0,3 LU để bản cuối ra đúng −16.
- Master cuối qua limiter đỉnh thật −2 dBTP: trần −12 dBTP mỗi cue không đủ nếu đỉnh giọng −3 dBTP trùng pha với SFX (Q5 tính trường hợp xấu nhất).
- Câu 2 bắt đầu từ 5,04 s trở đi (riser đỉnh ở 4,9 s); câu 5 vào sau logo âm thanh khoảng 0,3 s.
- Nghe lại cụm 12,6–13,4 s (bấm lưu, whoosh Bò, thịch, swell): M −24 LUFS, gần ngưỡng 8 LU dưới giọng.

### 6c. Giọng đọc, URL và bản giao v10 (23/10/2026)

File: `out/review/OPA-Agent-Pancake_v10.mp4` (bản dựng b23, master theo A.10 bằng `master.py`). Ảnh: `KHUNG-HIEN-DU_v10.png`, `TO-KHUNG-1s_v10.png`; bản nghe thử nhẹ `OPA-Agent-Pancake_v10_nghe-thu-720p.mp4` (âm giữ nguyên).

| Nấc | Cách kiểm | Kết quả |
|---|---|---|
| Lời so kịch bản | whisper large-v3 (`audio/giong/whisper.json`) so lời khóa | Khớp; whisper nghe nhầm "size" → "Sai", "tồn" → "tuần", "POS" → "Post". Câu 5 đọc "ngay tại Oping" (kịch bản: "[URL]") |
| Mốc câu | Năng lượng sau khoảng nghỉ | 0,10 / 4,38 / 14,09 / 22,62 / 30,33 s. Câu 2 dài 9,4 s nên vào trước cảnh 2 0,6 s (lời đi trước hình); "Giờ đây" vào sau cú đáp nhạc cảnh 3 0,6 s |
| SFX quanh lời | Mỗi cue: rơi lúc nói hay nghỉ, dưới giọng bao nhiêu LU (cột Lời, Dưới giọng trong bảng cue) | 43/64 cue rơi lúc nói, thấp hơn giọng ≥ 9,7 LU. Bỏ riser 4,9 s và tiếng giấy POS (đè "tưởng tượng", "size"); hạ khối nhấn, whoosh Bò, swell, collapse; dời whoosh nhân vật và logo âm thanh vào khoảng nghỉ. Sau rà chéo: bỏ 2 tiếng chip bay, hạ lớp tách của cú bấm lưu 6 dB (dòng Rà chéo Q5) |
| Nhạc dưới giọng | Cửa sổ 3 s và 400 ms trên từng lớp | 3 s: thấp nhất 11,7 LU, trung vị 14,9 LU. Cửa sổ 400 ms dưới 10 LU chỉ ở chỗ vắt qua khoảng nghỉ |
| Rõ lời | whisper trên bản giao so với giọng riêng | Cùng 152 từ, khớp 99,3 %, độ tin cậy trung bình 0,975 so 0,976 (b20 và b23 như nhau; whisper không nhạy với SFX đè phụ âm, phần đó đo ở dòng Rà chéo Q5). Chữ khóa: giọng trên (nhạc + SFX) từ 10,7 LU ("Giờ đây") tới 17,3 LU ("OPA") |
| Đồng bộ | Tương quan chéo giọng gốc với bản giao | Trễ 21,3 ms (0,64 khung) như mọi SFX: độ trễ AAC của AE, dưới ngưỡng nghe lệch |
| Master | `master.py` (loudnorm hai lượt, chỉ nhận tuyến tính), đích −16,1 như ca B8 | Tuyến tính; file giao −16,0 LUFS, đỉnh thật −3,5 dBTP, LRA 1,2 LU; ngắn hạn lớn nhất cao hơn tích hợp 1,4 LU |
| Hình | Đo chuyển động V2; dải khung cảnh 5 | Đạt (Tĩnh B 0,46 %, Tĩnh A 0, cắt cứng 0). Nút giãn theo URL (742 px), con trỏ bấm sau chữ, không đè URL |
| Rà chéo Q5 | Agent soát bản v10 đầu (dựng b20): rõ lời, cân mức, đồng bộ, đỉnh; đo dải 2–8 kHz quanh đầu âm tiết | Điểm: rõ lời 8, cân mức 9, đồng bộ 8, an toàn đỉnh 10. **Cần sửa:** 2 tiếng chip bay (11,30 / 11,97 s) đè đầu âm tiết "rồi" và /t/ của "từng". **Nên sửa:** lớp tách của cú bấm lưu (12,70 s) chỉ thấp hơn /s/ của "sẽ" 3,6 dB. **Đã sửa ở b23 (bản giao này):** bỏ 2 chip (dời sang khung 336/356 thì chỉ cách ping tin mới 1 khung, nghe thành tiếng đúp); hạ lớp tách 6 dB. Đo lại dải 2–8 kHz: chỗ chip không còn SFX (trước đó chip 2 to hơn phụ âm 15,5 dB); lớp tách thấp hơn /s/ 8,8 dB. Âm b23 chỉ khác b20 ở đúng 3 chỗ đó, còn lại trùng từng mẫu; hình trùng b22 (khung 84–130 lệch nhiễu mã hóa, PSNR ≥ 78 dB). **Ghi nhận, giữ:** whoosh nhân vật (22,3 s) trễ hình 5–7 khung để đuôi chữ "Agent" sạch |

**Đã thử rồi bỏ:** dìm nhạc −4 dB dưới "OPA Agent" cuối câu 3 vì whisper tin chữ "Agent" giảm 0,80 → 0,58. Dìm xong vẫn 0,56, và giọng đã cao hơn nhạc + SFX 15,9 LU ở đó, nên đây là dao động của whisper với từ tiếng Anh; giữ nhạc đúng bản đã duyệt.
<!-- KIEM:KET-THUC -->
