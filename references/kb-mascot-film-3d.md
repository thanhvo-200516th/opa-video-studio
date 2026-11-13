# kb-mascot-film-3d — toàn văn tài liệu của nguồn `mascot-film-3d`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/mascot-film-3d/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: mascot-film-3d/SKILL.md ===== -->

---
name: mascot-film-3d
description: >-
  Xây dựng và kết xuất phim hoạt hình 3D ngắn cho linh vật thương hiệu bằng mã nguồn (three.js + HTML/JS điều khiển tất định theo frame), chạy ngầm trên GPU RTX qua Chrome Headless + WebSocket (tích lũy 16 spp jittered supersampling -> FFV1 lossless -> H.264 MP4), ghép lớp chữ 2D từ Remotion và khóa khớp dáng 3D-sang-2D ở cảnh kết. Bao gồm bộ quy trình 6 khối PROMPT-PACK.md, cổng kiểm soát G0–G9, thư viện rig/mascot3d/accum và 8 bài kiểm định tự động (qa.py). Kích hoạt khi người dùng muốn làm phim hoạt hình 3D bằng code/three.js, dựng linh vật 3D chuyển động, render 3D headless trên GPU, hoặc kiểm định chất lượng phim 3D.
---

# Mascot Film 3D — Sản Xuất Phim Hoạt Hình 3D Linh Vật Bằng Mã Nguồn (`three.js` + RTX GPU)

Skill này cung cấp toàn bộ kiến trúc kỹ thuật, thư viện dựng hình/khớp xương 3D (`scripts/lib/`), bộ công cụ kết xuất tất định trên GPU (`scripts/render.py`), hệ thống kiểm định 8 bước (`scripts/qa.py`) và quy trình `PROMPT-PACK.md` để sản xuất phim hoạt hình 3D ngắn chất lượng studio chỉ bằng mã nguồn.

---

## Chạy trên máy Linux này

- Python: `~/.venvs/video-skills/bin/python` (máy không có lệnh `python`/`py`; venv có numpy, scipy, matplotlib, opencv, scikit-image, Pillow, fontTools, resvg-py, faster-whisper). Lệnh `python …` trong tài liệu chạy bằng đường dẫn này.
- ffmpeg/ffprobe 8.1 ở `~/.local/bin` (libx264, FFV1, ProRes 4444, loudnorm, ebur128).
- Đường dẫn Windows trong tài liệu đã đổi sang Linux: `F:\` → `/media/vmiz/Over Powers/`, `D:\` → `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/` (bản sao lưu ổ D ngày 2026-10-28). Ổ USB `Over Powers` phải đang gắn. `E:\` không có trên máy; tài nguyên thay thế ở `/home/vmiz/Thanh/Media/TNEDIT/` (`02_SFX`, `08_Nhac_Nen`, `01_Font`, `06_B-Roll`…).
- Chrome: `/usr/bin/google-chrome` với `--use-angle=gl`. Đã render thử 1 khung trên RTX 3070 Ti ngày 2026-10-29. Cờ `d3d11` trong tài liệu chỉ dùng trên Windows (trên Linux không có WebGL); xem bảng ở `references/render-quality.md` mục 5. Dọn Chrome bằng `os.killpg` thay cho `taskkill`.

---

## 1. Cấu Trúc Thư Mục Trong Skill

- **`SKILL.md`** — Quy trình tổng thể, kiến trúc kết xuất tất định (`window.__renderFrame`), cổng kiểm soát `G0..G9` và quy tắc khóa khớp 3D-sang-2D.
- **`scripts/`** — Công cụ điều phối Render, QA và Thư viện 3D lõi:
  - `scripts/render.py`: Khởi chạy máy chủ HTTP + WebSocket, gọi Chrome Headless chạy trên GPU rời NVIDIA RTX, điều khiển bộ tích lũy mẫu (`16 spp` cho từng frame), ghi luồng ảnh thẳng vào `ffmpeg` xuất `FFV1 (.mkv)` không nén và `H.264 (.mp4)`.
  - `scripts/qa.py`: Chạy 8 bài kiểm định tự động (hộp bao nhân vật, màu sắc thương hiệu, chuyển động không giật, kiểm tra tắt đỉnh sáng, đồng bộ khoảnh khắc vàng, khớp dáng 3D->2D ở cảnh kết).
  - `scripts/crop_base.py`: Đo đạc và cắt khung chuẩn cho linh vật.
  - `scripts/lib/mascot3d.js`, `rig.js`, `accum.js`, `rng.js`, `wire.js`, `world-desk.js`: Thư viện JavaScript dựng hình linh vật 3D từ đường cong Lathe/Extrude/Tube, hệ thống xương FK/IK, bộ tích lũy khử răng cưa `accum.js` (Halton jitter + Depth of Field + Subframe Motion Blur) và bộ sinh số ngẫu nhiên tất định `rng.js`.
- **`references/`** — Sổ tay kỹ thuật chuyên sâu:
  - `references/prompt-pack.md`: Khung sườn 6 khối bắt buộc của file `PROMPT-PACK.md` và 10 cổng kiểm soát `G0..G9`.
  - `references/render-quality.md`: Cấu hình ánh sáng studio 3 nguồn (`Key / Fill / Rim`), vật liệu PBR Vinyl/Clay mờ, khử răng cưa tích lũy `16 spp` và mã hóa màu `BT.709`.
  - `references/qa-checklist.md`: Chi tiết 8 bài kiểm định tự động trước khi bàn giao.
  - `references/audio.md`: Quy chuẩn ghép nhạc nền, hiệu ứng âm thanh vật lý 3D và chuẩn hóa âm lượng `-16 LUFS`.
  - `references/follow-up-playbook.md`: Kịch bản xử lý nhanh các lỗi thường gặp sau khi xem bản nháp.
- **`examples/`** — Dự án mẫu thực chiến (`PROMPT-PACK-thu-mon.md`, `DE-XUAT-V2-thu-mon.md`, `README.md`).

---

## 2. Kiến Trúc Kết Xuất Tất Định Theo Từng Khung Hình (`Deterministic Frame Stepping`)

1. **Cấm dùng `requestAnimationFrame` hoặc `Date.now()` / `Math.random()` tự do:**
   - Toàn bộ trạng thái của thế giới 3D (vị trí xương nhân vật, hạt bụi, góc máy quay, cường độ đèn) tại khung hình `f` phải là một **hàm toán học thuần túy** phụ thuộc duy nhất vào `f` (với `t = f / FPS`) và bộ sinh số ngẫu nhiên có hạt giống cố định (`scripts/lib/rng.js`).
2. **Giao diện điều khiển chuẩn trên `film.html`:**
   - Trang `film.html` phơi bày hàm `window.__renderFrame(frameIndex, spp, shutterAngle)` để `scripts/render.py` gọi qua giao thức WebSocket.
   - Với mỗi `frameIndex`, bộ tích lũy `scripts/lib/accum.js` lấy mẫu `spp` lần (chế độ nháp: `2–4 spp`, chế độ xuất bản: `16 spp`) dịch chuyển nhẹ vị trí ống kính (bokeh DoF) và thời gian trong khoảng màn trập (`shutter = 0.5` tạo hiệu ứng nhòe chuyển động Subframe Motion Blur chân thực).

---

## 3. Quy Trình 10 Cổng Kiểm Soát (`G0 -> G9`) Khi Làm Phim 3D Mới

Trước khi viết code hoặc kết xuất toàn bộ phim, phải đi qua tuần tự các cổng kiểm soát (chi tiết tại `references/prompt-pack.md`):
- **`G0` — Soạn `PROMPT-PACK.md` 6 khối:** Khai báo rõ Thông số kỹ thuật, Hồ sơ nhân vật & bối cảnh, Bảng phân cảnh chi tiết theo frame, Bảng đạo cụ, Bảng âm thanh và Tiêu chuẩn nghiệm thu.
- **`G1` — Kiểm tra Tỷ lệ & Hình khối Linh vật (`Look-Test Stills`):** Xuất 6 góc chụp tĩnh (`0°, 20°, 35°`, sáng/tối) kiểm tra chất liệu Vinyl/Clay, mắt, sừng và màu thương hiệu.
- **`G2` — Kiểm tra Khớp Xương & Biên Độ Cử Động (`Rig & Pose Sheet`):** Đảm bảo chân tay không đâm xuyên qua thân (`self-intersection`) khi nhảy hoặc vung tay.
- **`G3` — Bản Nháp Chuyển Động Nhanh (`Animatic 2 spp`):** Kiểm tra nhịp điệu câu chuyện và góc máy trong 1–2 phút.
- **`G4` — Kiểm tra Cắt Đỉnh Sáng (`Highlight Clipping A/B Test`):** So sánh có/không có đèn chói để đảm bảo bề mặt linh vật không bị cháy trắng (`RGB > 250`).
- **`G5` — Ghép Lớp Chữ 2D & Khóa Khớp Cảnh Kết (`3D-to-2D Endcard Lock`):** Ở cảnh cuối, đưa camera và tư thế linh vật 3D về khớp 100% vị trí/tỷ lệ với logo linh vật 2D trên thẻ kết thúc (sai số tâm `≤ 2 px`).
- **`G6` — Kết Xuất Bản Đẹp (`HQ Render 16 spp -> FFV1`).**
- **`G7` — Chạy 8 Bài Kiểm Định Tự Động (`python scripts/qa.py`).**
- **`G8` — Phối Âm & Chuẩn Hóa Âm Lượng (`-16 LUFS`, `-1.5 dBTP`).**
- **`G9` — Xuất Bảng Contact Sheet & Đóng Gói Bàn Giao.**

<!-- ===== /file: mascot-film-3d/SKILL.md ===== -->

<!-- ===== file: mascot-film-3d/examples/DE-XUAT-V2-thu-mon.md ===== -->

Phim 3D Bò OPA "Thủ môn" · Đề xuất bản 2 sau góp ý của Minh ngày 19/10/2026 · Soạn: Claude Code (Opus 5.5)
Trạng thái: **MINH ĐÃ DUYỆT HƯỚNG SỬA 21/10/2026, rồi xem, nghe và DUYỆT BẢN 2 cùng ngày.** Bản 2 ở `out/thu-mon-3d-16x9-ban2/` (gốc dự án); kết quả đo và rà chéo trong `FOLLOWUPS.md`. Dải "độ chuyển động 1,5–8" ở bảng dưới không đạt theo nghĩa đen trên nền phẳng (đã báo, xem `FOLLOWUPS.md` mục "Để ngỏ"). Bản 1 giữ nguyên ở `out/thu-mon-3d-16x9/`.

Góp ý của Minh: "biểu tượng tin nhắn vẫn bị lỗi, background thì đen không đồng nhất, hiệu ứng thì lúc nhanh lúc chậm, text thì không dàn trải nên làm ý nghĩa của video khó hiểu! Xem không đọng lại gì cho người xem cả".

Tờ một trang: `out/thu-v2/de-xuat-v2.png` (ảnh trước/sau + biểu đồ nhịp).

# 1. Đổi lời chê thành việc đo được

| Minh nói | Soi lại thấy (bằng chứng) | Sửa ở bản 2 | Đạt khi |
|---|---|---|---|
| Biểu tượng tin nhắn vẫn bị lỗi | Bong bóng trắng bay trước màn hình trắng gần như vô hình (3,17 s). Bóng bật ra đè lên vạch của ô tin trông như lỗi hình (5,70 s, 11,55 s). Bóng là khối trắng viền dày, không có vạch chữ nên không đọc ra là tin nhắn (6,83 s). | Bong bóng đúng biểu tượng tin nhắn của V2 (vỏ bo, đuôi, 2 vạch chữ trắng ở cả hai mặt), dày 7 mm. Tin khách màu #003C99, hứng xong chuyển #0068FF. Ô tin trên màn hình đổi sang nền nhạt; chỉ tin mới nhất màu #003C99 và chính nó bay ra. | Ảnh thử `out/thu-v2/moi/*.png`. Mọi khung có bóng bay: bóng không nằm trên nền cùng màu (soi tờ khung). |
| Nền đen không đồng nhất | Phòng tối có đèn: tường xám đen, mặt bàn loang sáng, sàn đen. Ba mảng tối khác nhau, có vệt sáng. V2 vẽ đêm là nền phẳng #003C99, ngày là nền phẳng trắng. | Nền liền một màu như V2: đêm #003C99, sáng chuyển dần sang trắng. Bàn, tường, sàn cùng một màu không chịu đèn. Đồ vật dùng đèn cố định, có bóng tiếp xúc nhuộm xanh. | Ảnh thử. Nền ngoài đồ vật lệch không quá 2 mức trong cả khung. |
| Hiệu ứng lúc nhanh lúc chậm | Đo độ chuyển động mỗi khung: lúc có chữ gần đứng yên (0,3–0,7), lúc hứng bóng dồn dập (3–16), cú lia sang CRM 46, gấp khoảng 100 lần. Biểu đồ `out/thu-v2/nhip-ban-cu.png`. | Một nhịp đều 120 BPM: mọi cú hứng rơi đúng phách (mỗi 0,5–1,5 s). Máy quay một đường chậm, đều; bỏ cú lia gấp sang CRM, cú xoay 180°, cú lao ra mép bàn và nhịp khựng. Bảng CRM luôn trong khung. | Trung bình mỗi 0,5 s nằm trong dải 1,5–8. Không đỉnh nào quá 12, trừ cú dolly-zoom cuối. |
| Chữ không dàn trải, khó hiểu ý | Chữ chỉ hiện 6,2 / 16 s của phần 3D. Đoạn 2,3–10,2 s (8 s hứng bóng) không có chữ nào giải thích. | Chữ chạy suốt phim, mỗi nhịp một câu, đều một cột trái. Dùng **lời V2 bản 16:9 Minh đã duyệt**, không viết lời mới. | Chữ phủ ≥ 65 % phần 3D; khoảng trống giữa hai nhóm ≤ 0,6 s. |
| Xem không đọng lại gì | Chưa có câu chốt; ý "không sót khách" chỉ nằm trên nút của end card. | Cao trào là câu chốt của V2: "Bỏ sót khách" bị gạch, đổi thành "Không bỏ sót khách". End card nhắc lại bằng nút "KHÔNG SÓT KHÁCH". | Người xem chỉ nhớ một câu: "Không bỏ sót khách". |

# 2. Kịch bản bản 2 (21 s, giữ end card đã duyệt)

Mạch truyện một câu: **khách nhắn lúc đêm → AI của OPA trực, hứng hết từng tin → ghi lại, trả lời ngay → sáng ra: không bỏ sót khách nào → nhắn OPA.**

| # | Giây | Người xem thấy | Bò diễn | Máy | Chữ (lời V2 16:9 đã duyệt) |
|---|---|---|---|---|---|
| 1 | 0,0–2,5 | Đêm: nền #003C99 phẳng. Điện thoại khổng lồ sáng sau Bò, đồng hồ 22:47. Một ô tin mới hiện trên màn hình rồi bay ra (1,5 s). | Thở chậm, ngẩng theo tin | Đẩy vào chậm, đều | **L1** "Khách nhắn / Tối qua…" (0,3–2,3) |
| 2 | 2,5–5,0 | Bò trượt sang hứng tin 1 qua khe trán (3,0 s). Tin chuyển xanh OPA, thành thẻ bay sang bảng CRM; bảng thêm dòng "Đã trả lời". Tin 2 tới, hứng (4,5 s). | Trượt gọn, đáp đúng phách | Bám ngang chậm | **L4** "AI trực thay / Anh chị." (2,6–4,7) |
| 3 | 5,0–7,5 | Tin tới dày hơn, đều đặn mỗi 0,5 s: hứng ở 5,5 · 6,0 · 6,5 (nhảy hứng quả cao) · 7,0. Mỗi thẻ thêm một dòng ở bảng CRM. | Hứng liên tiếp, gọn, chắc | Lùi nhẹ cho thấy cả bảng CRM | **L5** "OPA ghi lại / Từng khách." (5,0–7,1) |
| 4 | 7,5–10,0 | Bảng CRM: mọi dòng "Đã trả lời". Đồng hồ trên bảng tua 22:59 → 07:00. | Đứng vững, thở đều | Trôi về khung chữ | **L6** "Trả lời ngay, / Cả ngoài giờ" (7,6–9,7) |
| 5 | 10,0–13,8 | Trời sáng: nền chuyển dần sang trắng phẳng. "Bỏ sót khách" hiện, bị gạch, đổi thành "Không bỏ sót khách" (đúng kiểu V2). | Hếch đầu tự hào, một hơi phì | Đẩy vào chậm | **L8 → L8b** "Bỏ sót khách" → "Không bỏ sót khách" (10,2–13,6) |
| 6 | 13,8–16,0 | Vùng xanh tràn từ lòng O; Bò chuyển trắng, khóa đúng chỗ Bò của end card (như bản 1, lệch ≤ 2 px). | Sừng, nhịp thở về khung khóa | Dolly-zoom | — |
| 7 | 16,0–21,0 | End card "trạm OPA" (giữ nguyên bản đã duyệt) | Bò 2D | — | "OPA" / "AI CRM + AI Sales Agent", rồi "Nhắn OPA / Để nhận báo giá" + nút "“KHÔNG SÓT KHÁCH”" |

- **Số cú hứng:** 7 (bản 1: 10), đều nhịp, mỗi cú một thẻ sang CRM. Bỏ: xoay 180°, bóng đậu ngọn sừng rồi hất, lao ra mép bàn, nhịp khựng, cú lia gấp sang CRM.
- **Chữ:** 5 nhóm lời V2 đã duyệt, đặt theo thứ tự mới. Không thêm lời mới, không đổi chữ.
- **Giữ nguyên:** hình Bò (look C2, dày t), tổng 21 s, end card, cú cắt khớp 3D → 2D, giọng âm (phương án A cả ba nhóm). Nhạc dựng lại theo nhịp mới.

# 3. Việc phải làm nếu duyệt (ước lượng)

1. Lead: viết lại `timeline.js` theo bảng trên; bật `world: { bg: 'flat', bubble: 'icon' }`; đổi ô tin trên màn hình sang nền nhạt + tin mới nhất bay ra; luật đêm vẫn giữ (Bò xanh luôn đứng trước màn hình sáng). Khoảng 1–2 giờ.
2. Lane R: lớp chữ theo 5 nhóm mới (dùng lại `StrikeW` của V2 cho L8 → L8b), end card giữ nguyên. Khoảng 30–45 phút.
3. Lane A: dựng lại cue và nhạc theo nhịp mới, giữ âm sắc phương án A. Khoảng 1 giờ.
4. Thang kiểm 8 nấc + rà chéo bằng agent mới, rồi gửi Minh bản có giờ phim.

<!-- ===== /file: mascot-film-3d/examples/DE-XUAT-V2-thu-mon.md ===== -->

<!-- ===== file: mascot-film-3d/examples/PROMPT-PACK-thu-mon.md ===== -->

Phim 3D Bò OPA — Ý 2 "Thủ môn" · BẢN 2 · 21/10/2026
Trạng thái: **ĐÃ DUYỆT 21/10.** Minh duyệt hướng sửa (`DE-XUAT-V2.md`, "Duyệt hướng sửa bản 2 như đề xuất, dựng lại đi"), rồi xem, nghe và duyệt bản 2 cùng ngày. Ngày 22/10 Minh chọn bản âm dùng thư viện SFX (`docs/film3d/am-thu-vien/README.md`). Bản giao: `out/thu-mon-3d-16x9-ban2/` (gốc dự án).
- Bản 1 (G2 duyệt 19/10, sau đó Minh chê và không đăng) giữ ở `PROMPT-PACK.ban1.md`. Hình bản 1 còn nguyên ở `out/animatic-hq/`, `out/thu-mon-3d-16x9/` (gốc dự án).
- Mã `timeline.js` bản 1 đã được thay bằng bản 2 (dự án không có git).
- Giữ từ bản 1: hình Bò (look C2, dày t), tổng 21 s, end card, cú cắt khớp 3D → 2D, âm sắc phương án A.

# Kịch bản (prompt pack 6 khối)

```text
BRAND
HERO: Bò OPA — dấu hình học chỉ là cái đầu: mõm chữ U bo tròn có lòng O xuyên, 2 sừng cong, khe trán
(2 mép = 2 lỗ mũi). Đùn từ geometry.json "mark", dày t, cạnh vát vào trong. Look C2: mặt trước và mặt sau
#0068FF, thành bên #003C99 → gần #0068FF. Không mắt, miệng, tay chân; không bóp méo; sừng cử động quanh chân
sừng, về khung khóa ở cuối. Diễn bằng tư thế, sừng, hơi thở phì (hạt xanh từ 2 lỗ mũi).
ĐỐI THỦ: tin nhắn của khách — đúng biểu tượng tin nhắn V2 (vỏ bo R28, đuôi trái, 2 vạch chữ trắng ở cả hai
mặt), dày 7 mm. Tin khách #003C99; hứng xong chuyển #0068FF.
THẾ GIỚI: nền liền một màu như V2 (bàn, tường, sàn cùng một màu không chịu đèn): đêm #003C99, sáng trắng.
Điện thoại khổng lồ thân trắng dựng sau Bò (màn hình sáng là nền ngay sau Bò); trên màn hình là cột tin cũ
màu nhạt #E6F0FF, tin mới hiện ngay dưới cột. Bảng CRM nhỏ ngay bên phải Bò, luôn trong khung (tên giả của
V2, "Đã trả lời"). Chồng sổ bên trái. Đồ vật có đèn cố định và vệt bóng tiếp xúc nhuộm xanh.
BẪY: chính khối chữ U — tin lọt khe trán, rơi xuống đáy lòng O, chuyển xanh OPA, thành thẻ khách lùi ra sau
qua lỗ O rồi vòng sang bảng CRM.
BẢNG MÀU: #0068FF, #003C99, #FFFFFF, #E6F0FF, #0A0A0A.
KẾT: sáng ra, "Bỏ sót khách" bị gạch đúng lúc Bò hứng tin buổi sáng → "Không bỏ sót khách"; Bò lấy đà,
vùng xanh tràn từ lòng O, Bò chuyển trắng, khóa đúng chỗ Bò của end card 16:9.

FORMAT: một film.html, three.js 0.160.0, 1920×1080, 60 fps, 16 s 3D + 5 s end card Remotion; poseAt(t)
là hàm thuần của t; random có seed; mọi cú chạm là một dòng EVENTS dùng chung cho hình và âm.

LOOK: phẳng như V2, không còn phòng tối có đèn. Bò không chịu đèn (C2). DOF nhẹ, Bò luôn nét; không tone map
ACES; nhòe chuyển động 16 mẫu. Rạng sáng trộn màu nền trong sRGB như V2 (trộn tuyến tính ra xám đục).

BEATS (s): một nhịp đều 120 BPM (phách 0,5 s), mọi cú hứng rơi đúng phách. Xem bảng storyboard.

CAMERA: một đường máy duy nhất: đẩy vào đều 0 → 14,85 s, trôi ngang/dọc ±1 cm (hai chu kỳ lệch nhau, không
lúc nào cùng dừng); không lia gấp, không xoay quanh Bò. Cột chữ trái x ≤ 780 px là nền trơn; mép trái màn
hình ≥ ~850 px; bảng CRM luôn trong khung. Cuối: dolly-zoom FOV 30° → 7° về khung khóa.

CHECKS: mặt trước Bò #0068FF (lệch CIEDE2000 ≤ 2) mọi khung đo; ban đêm nền ngay sau Bò sáng; khung khóa khớp
Bò 2D ≤ 2 px; không xuyên vật, không chồng bóng; ngọn sừng cách mép ≥ 24 px; mỗi 2 s ≤ 15 % khung gần đứng,
chuỗi ≤ 12 khung; chữ phủ ≥ 65 % phần 3D, khoảng trống giữa hai nhóm ≤ 0,6 s; tương phản chữ ≥ 4,5 : 1.
```

# Storyboard theo giây (60 fps)

| # | Giây | Khung | Người xem thấy | Bò diễn | Máy | Chữ |
|---|---|---|---|---|---|---|
| 1 | 0,00–1,50 | 0–89 | Đêm, nền phẳng #003C99. Điện thoại khổng lồ thân trắng sau Bò; cột tin cũ màu nhạt. 1,00 s: tin mới #003C99 hiện ở ô ngay dưới cột, rung như báo tin. | Đung đưa nhẹ (lắc 1,2°/2 s, xoay 2,5°/4 s), thở chu kỳ 2,4 s; 0,95–1,35 quay nhìn tin | Đẩy vào đều, trôi ±1 cm | **L1** "Khách nhắn / Tối qua…" |
| 2 | 1,50–3,40 | 90–203 | Tin 1 bật khỏi màn hình, lật một vòng, nhỏ dần, trượt chéo xuống trên đầu Bò rồi lọt khe đúng 3,00 s, chuyển xanh OPA. 3,20 thẻ lùi qua lỗ O, vòng sau lưng Bò, tới bảng CRM 3,80; cột tin cuộn lên một dòng. | Ngẩng nhìn (1,5–2,4), phì 2,25, trượt trái tới chỗ hứng, nảy 6 mm đúng phách, gật nhận tin | như trên | **L4** "AI trực thay / Anh chị." (khối nhấn "Anh chị." quét đúng 3,00 s) |
| 3 | 3,40–5,00 | 204–299 | Tin 2 (hiện 3,20, bay 3,40) hứng 4,50; tin 3 hiện 4,30. | Trượt phải đón tin 2 | như trên | (L4 rút) |
| 4 | 5,00–7,50 | 300–449 | Tin dày, đều mỗi 0,5 s: hứng 5,5 · 6,0 · 6,5 (nhảy cao 9 cm, hứng trên không) · 7,0. Mỗi thẻ thêm một dòng ở bảng CRM, cột tin cuộn mỗi cú hứng. | Hứng liên tiếp, gọn; thở nhanh (chu kỳ 1,3 s); phì mạnh 7,25 sau đợt dồn | như trên | **L5** "OPA ghi lại / Từng khách." |
| 5 | 7,50–9,70 | 450–581 | Bò quay sang bảng CRM. Tua cả đêm 8,2–9,6: cột tin cuộn đều 10 dòng, CRM thêm 12 dòng "Đã trả lời", đồng hồ CRM 22:51 → 07:00. | Quay sang CRM (7,4–8,0), gật soát theo phách 8,5 · 9,0, quay lại 9,3 | như trên | **L6** "Trả lời ngay, / Cả ngoài giờ" |
| 6 | 9,70–10,20 | 582–611 | Rạng sáng: nền chuyển dần #003C99 → trắng; máy trắng hòa vào nền. | Đung đưa, thở | như trên | (giữa L6 và câu chốt) |
| 7 | 10,20–12,00 | 612–719 | Tin buổi sáng hiện 10,40, bay 10,60; Bò ngẩng nhìn; hứng 11,50 đúng lúc chữ gạch "Bỏ sót khách"; tin ở lại lòng O (nguồn vùng xanh). | Ngẩng 4°, xoay 5° nhìn tin; hứng | như trên | **L8 → L8b**: "Bỏ sót khách" hiện 10,20, bị gạch 11,50; "Không bỏ sót khách" trồi 11,75, khối nhấn quét 12,00 |
| 8 | 12,00–14,50 | 720–869 | Sáng, nền trắng. | Hếch đầu tự hào (12,1–13,3); nảy liền mạch theo phách, chạm đáy đúng 12,0 · 12,5 · … · 14,5; sừng giật nhẹ mỗi phách; phì 12,50 | như trên | L8b đọc trọn, rút xong trước 14,80 |
| 9 | 14,50–16,00 | 870–959 | Lấy đà 14,50–14,85, bật xả: vùng xanh tràn từ lòng O (14,85–15,35); Bò chuyển trắng theo từng điểm ảnh, dẹt thành dấu 2D, khóa 15,98 đúng vị trí, cỡ, góc sừng, độ nghiêng, nhịp thở của Bò end card. | Hít hơi (phồng 4 %), ngửa 5°, nhổm 4 mm nhanh dần → xả | Dolly-zoom FOV 30° → 7° | — |
| 10 | 16,00–21,00 | 960–1259 | End card 16:9 "trạm OPA" của V2, giữ nguyên bản 1: "OPA" khóa 16,60; "AI CRM + AI Sales Agent"; "Nhắn OPA / Để nhận báo giá" + nút "“KHÔNG SÓT KHÁCH”" đứng yên từ 19,60. | Bò 2D | — | end card |

**Tổng: 21,0 s** (16,0 s 3D + 5,0 s end card).

# Chữ (lời V2 bản 16:9 Minh đã duyệt, không viết lời mới)

- Lấy nguyên văn bằng `copyGroupsW()`, theo thứ tự mới:
  - L1 "Khách nhắn / Tối qua…"
  - L4 "AI trực thay / Anh chị."
  - L5 "OPA ghi lại / Từng khách."
  - L6 "Trả lời ngay, / Cả ngoài giờ"
  - Câu chốt kiểu V2: L8 "Bỏ sót khách" bị gạch (`StrikeW`) → L8b "Không bỏ sót khách"
- Đêm chữ trắng trên #003C99; ngày chữ đen trên trắng.
- Cột trái x ≤ 780 px cho L1–L6. Riêng câu chốt nới cột (giữ cỡ 112 px và khối nhấn #0068FF như V2), nằm trên y = 450 px ở phần x ≥ 1130 px để không chạm sừng Bò.
- Mọi nhóm trôi nhẹ liên tục lúc đứng, như máy quay ảo của V2.

# Luật rút từ bản 2

1. Nền phẳng làm cùng một chuyển động ra ít điểm ảnh đổi hơn hẳn phòng có đèn (thước "độ chuyển động" của bản 1 nhỏ đi khoảng 10 lần). Vì vậy:
   - Máy phải trôi liên tục, chọn pha để không lúc nào cùng dừng.
   - Bò luôn đung đưa nhẹ.
   - Nhịp lặng thì dùng cử chỉ theo phách (nảy, gật), không đứng.
   - Đo khung đứng trên bản chất lượng cuối, sau khi ghép chữ.
2. Tin bay ra không được đi ngang qua cột tin cũ (lỗi "bóng đè vạch ô tin" của bản 1). Tin bật khỏi ô theo hướng xa cột, đủ nhanh để tin sau (cách 0,45 s) hiện không chạm tin trước.
3. Vật cùng màu Bò không được lướt trước thân Bò (chỉ còn 2 vạch trắng nhòe, trông như lỗi). Thẻ lùi ra sau, để Bò che.
4. Ban đêm, nền ngay sau Bò luôn là màn hình sáng (kiểm bằng độ sáng vòng nền quanh bóng Bò).
5. Cú cắt 3D → 2D như bản 1: tư thế khóa lấy từ `out/endcard-bo.json`, Bò dẹt dần thành dấu 2D, `qa.py lock` ≤ 2 px. Khi đo chuyển động, khai báo 15,95–16,05 s là khoảng lặng có chủ ý.

<!-- ===== /file: mascot-film-3d/examples/PROMPT-PACK-thu-mon.md ===== -->

<!-- ===== file: mascot-film-3d/examples/README.md ===== -->

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

<!-- ===== /file: mascot-film-3d/examples/README.md ===== -->

<!-- ===== file: mascot-film-3d/references/audio.md ===== -->

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

<!-- ===== /file: mascot-film-3d/references/audio.md ===== -->

<!-- ===== file: mascot-film-3d/references/follow-up-playbook.md ===== -->

# Vòng soát và follow-up cho phim 3D

**Follow-up** là đoạn yêu cầu sửa, viết sau mỗi lần xem (ảnh tĩnh, bản ghép, số đo). Ở ca mẫu, Claude tự xem và tự viết follow-up; Minh chỉ duyệt ở các cổng. Mọi vòng ghi vào `film3d/films/<id>/FOLLOWUPS.md`.

Nguyên tắc: **đo trước, xem ảnh sau.** Phần lớn lỗi của phim 3D (cắt mép, lệch màu, chữ đè nền sáng, đứng hình, lệch cú cắt) đo được bằng số. Đo trước thì bớt vòng sửa và bớt token đọc ảnh. Lệnh đo: `qa-checklist.md`.

Ví dụ đủ: `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/OPA-Motion-graphic-mascot/film3d/films/thu-mon/FOLLOWUPS.md`.

## 1. Nhịp vòng soát

| Lúc | Đo trước | Rồi xem | Ai quyết |
|---|---|---|---|
| G1 thử look | `qa.py shape`; `qa.py brand` trên ảnh tĩnh; `qa.py video` trên đoạn 4 s | một tờ so sánh các kiểu look | Minh trả lời 3 câu có/không |
| G2 bản ghép | màu, cắt mép, chữ, khung đứng, cú cắt | bản ghép có giờ phim + tờ duyệt một trang | Minh duyệt |
| Sau góp ý của Minh | phép đo liên quan | ảnh trước/sau cùng góc, phóng 3× chỗ được chê | Minh |
| Minh chê bản đã giao | đo lại đúng thứ bị chê trên bản cũ (ca mẫu: độ chuyển động mỗi khung, độ phủ chữ) | tờ đề xuất một trang: ảnh trước/sau + biểu đồ nhịp (mục 3) | Minh duyệt hướng, rồi mới dựng lại |
| G4 tự soát | đủ bộ đo trên bản ghép | 24 khung (4 tờ × 6 ô) + dải 5 khung quanh mọi nhịp chạm; mọi khung ở đoạn vật dồn dập | Claude |
| Sau mỗi lần sửa | đúng phép đo đã trượt | 12 khung ở chỗ đã sửa | Claude |
| G6 âm | độ to, true peak, lệch tiếng, loa điện thoại (lane A) | sau mix đầu; sau khi solo từng bus; bộ A/B (ca mẫu bản 2: âm tổng hợp với âm thư viện) | Minh nghe |
| G8 | đủ 8 nấc, đo lại sau mỗi đợt sửa | agent mới rà chéo, chấm điểm, xếp mức lỗi; vòng 2 cùng người rà | Minh, Hùng |

**Vì sao cần rà chéo dù đã tự soát:**
- Bản 1: agent rà chéo bắt được một lỗi bắt buộc (bóng lơ lửng 5,13–5,25 s). Dải 5 khung của G4 đã chứa lỗi này, nhưng người tự soát đọc nhầm thành lỗi xuyên vật. Người rà chấm 4 mục: không nhàm 8,5 · thương hiệu 9 · chữ 8,5 · rõ chuyện 7, và tìm thêm 7 lỗi "nên sửa". Mục thấp nhất (rõ chuyện) là chỗ số đo không bắt được.
- Bản 2: vòng 1 bắt lỗi bắt buộc nằm giữa hai nhịp (tin chồng nhau, cắm vào vai khe lúc Bò nhảy, 6,10–7,12 s), nên dải 5 khung không chứa. Vòng 1 còn bắt chữ giật do bước ghép, có từ bản 1 mà chưa ai thấy. Vòng 2 cùng người rà: "phần hình giao được".

- **Tờ khung** (contact sheet) là một ảnh ghép nhiều khung nhỏ. Xem tờ 6 ô thay cho 6 ảnh rời tốn ít token ảnh hơn khoảng 4 lần.
- **Chọn khung:** rải đều theo thời gian, cộng mọi nhịp chạm trong `EVENTS` (hứng, đáp, thẻ bay, phì, cú cắt).
- **Dải 5 khung** là các khung f−2 … f+2 quanh một nhịp f. Cắt từ bản 3D FFV1 (không mất chất lượng), không cắt từ MP4 đã nén.
- Chỗ nghi ngờ: phóng to ở độ phân giải gốc (ca mẫu: `bong-qua-khe-7.70s-x3.png`). Chân mascot và bóng tiếp xúc: `tools/film3d/crop_base.py`.
- Mỗi vòng tối đa khoảng 6 lỗi. Thứ tự: khung cắt và màu mascot trước, va chạm sau, câu chuyện cuối.
- Muốn xem nhanh một chỗ đã sửa: job `frames` vài khung (vài giây). Đo màu và chống nhàm thì luôn trên bản đủ, chất lượng cuối.
- Gửi Minh bản có giờ phim ở góc (`render.py compose ... --timecode`), để Minh chỉ đúng giây.

## 2. Mẫu một vòng follow-up

```text
Vòng {n} · sau {bản ghép G2 | tờ khung G4 | số đo | góp ý của Minh ngày ...}
Đã ổn, khóa lại: {những gì không được đụng tới}.
Lỗi:
{k}. [{giây hoặc khung}] Thấy: {mô tả, kèm tên ảnh hoặc số đo}.
     Sửa: {bằng số: mét, độ, px, khung; tên hằng trong code}.
     Đạt khi: {lệnh đo + ngưỡng}; xem lại {ảnh nào}.
```

Trong `FOLLOWUPS.md`, ghi thành bảng `# | Lỗi | Bằng chứng | Sửa | Kiểm lại`, kèm hai mục:
- **Đã soát, không lỗi**: để người rà chéo khỏi soát lại.
- **Để ngỏ, có lý do**: chỗ trông như lỗi nhưng cố ý (ví dụ cận cắt thân mascot đã được duyệt ở G2).

Ví dụ, lỗi 7 của ca mẫu viết theo mẫu:

```text
7. [3,15–3,35 s, máy nhìn xuyên lòng O] Thấy: ngọn sừng cách mép trên 0–42 px, khung 3,25 s ra ngoài
   khung (qa.py boxes).
   Sửa: máy ở khóa 3,25 s lùi 0,62 → 0,70 m.
   Đạt khi: qa.py boxes --allow 6.55:7.65,12.30:12.95 báo pass; ngọn sừng ≥ 24 px ở mọi khung.
```

## 3. Đổi lời chê thường thành yêu cầu đo được

Minh chê bằng lời thường. Đổi sang dạng trên, đọc lại cho Minh, rồi mới sửa. Ví dụ góp ý của Minh ở G2 ca mẫu:

| Minh nói | Đổi thành |
|---|---|
| "Góc chưa 3D" | Thành bên một màu phẳng → look C2: thành bên nhận sáng theo đèn trong không gian vật, cạnh vát bo 0,08t có vệt sáng |
| "Răng cưa" | Ranh màu khấc theo mặt lưới → trọng số cạnh vát tính theo vị trí chiều sâu; so ảnh phóng 3× trước/sau |
| "Bóng chưa đẹp" | Bóng tiếp xúc nhuộm xanh dưới chân; đèn chính có diện tích (lệch 7° mỗi mẫu) cho bóng mềm |
| "Bố cục chưa cân" | Điện thoại giữa, sổ trái, bảng CRM phải; vật không che chân mascot |

Gửi lại một tờ "trước / bây giờ" cùng góc xoay (ca mẫu: 35°), có ảnh phóng 3× đúng chỗ bị chê.

**Khi Minh chê bản đã giao,** làm file đề xuất trước khi đụng code (ca mẫu: `film3d/films/thu-mon/DE-XUAT-V2.md`):
1. Chép nguyên văn lời chê.
2. Mỗi ý một dòng: Minh nói | soi lại thấy (bằng chứng: giây, ảnh, số đo) | sửa ở bản mới | đạt khi.
3. Kịch bản bản mới theo giây, chỉ dùng lời đã duyệt.
4. Ghi rõ giữ nguyên gì (ca mẫu: hình Bò, tổng 21 s, end card, cú cắt 3D → 2D, âm sắc).
5. Tờ một trang: ảnh trước/sau + biểu đồ nhịp. Chờ Minh duyệt hướng.

Bảng của ca mẫu (Minh chê bản 1 ngày 19/10):

| Minh nói | Soi lại thấy | Sửa ở bản 2 | Đạt khi |
|---|---|---|---|
| "Biểu tượng tin nhắn vẫn bị lỗi" | Bong bóng trắng trước màn hình trắng gần như vô hình; bóng bật ra đè vạch ô tin; khối trắng viền dày không ra tin nhắn | Đúng biểu tượng tin nhắn V2 (vỏ bo, đuôi, 2 vạch chữ), #003C99, hứng xong chuyển #0068FF; cột tin cũ màu nhạt | không khung nào bóng nằm trên nền cùng màu |
| "Background thì đen không đồng nhất" | Phòng tối có đèn: tường, bàn, sàn ba mảng tối khác nhau, có vệt sáng | Nền liền một màu như V2: đêm #003C99, sáng trắng | nền ngoài đồ vật lệch ≤ 2 mức |
| "Hiệu ứng thì lúc nhanh lúc chậm" | Độ chuyển động mỗi khung: lúc có chữ 0,3–0,7, lúc hứng 3–16, cú lia sang CRM 46 | Một nhịp đều 120 BPM, mọi cú hứng đúng phách; một đường máy; bỏ lia gấp, xoay 180°, nhịp khựng | ô động nhất gấp ô lặng nhất ít lần (bản 2: 4,8; bản 1: 56) |
| "Text thì không dàn trải ... khó hiểu" | Chữ chỉ hiện 6,2 / 16 s; 8 s hứng bóng không có chữ nào | Chữ chạy suốt phim, mỗi nhịp một câu, lời V2 đã duyệt | chữ phủ ≥ 65 %, trống ≤ 0,6 s (bản 2: 80 %, 0,52 s) |
| "Xem không đọng lại gì" | Chưa có câu chốt; ý chính chỉ nằm trên nút end card | Câu chốt V2: "Bỏ sót khách" bị gạch đúng cú hứng cao trào → "Không bỏ sót khách" | người xem nhắc lại được một câu |

Bài học: đề xuất bản 2 hứa "độ chuyển động mỗi 0,5 s trong dải 1,5–8", đặt theo thước của phòng có đèn. Nền phẳng làm số nhỏ đi khoảng 10 lần, nên dải đó không đạt theo nghĩa đen dù phim đã đều, và phải giải thích lại với Minh. Đặt ngưỡng sau khi dựng thử vài giây trên đúng kiểu nền, hoặc dùng tỉ số không phụ thuộc nền (ô động nhất / ô lặng nhất).

## 4. Bệnh → thuốc

Rút từ `FOLLOWUPS.md` (bản 1 và bản 2), `g1-thu-look.md` và bài học của ca mẫu. Cột "Đo" là cách biết đã khỏi.

### Màu và look

| Bệnh | Thuốc | Đo |
|---|---|---|
| Mặt trước mascot tối đi khi xoay (đèn đặt cố định trong cảnh: lệch 1,36 / 2,97 / 5,41 ở 0° / 20° / 35°) | Bỏ đèn cố định. Dùng kiểu C/C2 (mặt trước tô phẳng) hoặc B (đèn bám theo mascot) | `qa.py brand` ở 0°, 20°, 35° với cùng một bộ đèn |
| Mặt trước lệch sang lơ hay tím | Không tone map ACES; vật liệu không phản xạ bóng; phơi sáng (EXPO) tính bằng công thức từ cường độ đèn, không đoán | trung vị ΔE2000 ≤ 2 |
| Vật không chịu đèn (màn hình, bong bóng, hạt, vùng tràn xanh) ra sai màu token | Nhân màu với `INV_EXPO` (= 1/EXPO) trước khi vẽ | soi màu điểm ảnh trên khung |
| Vòng đặt màu chung ghi đè màu riêng (G1: hạt thở mất màu xanh) | Vòng chung chỉ cho vật trắng; vật có màu riêng đặt màu một lần lúc dựng | xem khung có hạt |
| "Góc chưa 3D": thành bên một màu phẳng | Look C2: thành bên đi từ #003C99 tới gần #0068FF theo đèn; vệt sáng dọc cạnh vát | ảnh 35° trước/sau |
| Răng cưa giả, khấc ở ranh mặt trước và thành bên | Trọng số cạnh vát tính theo khoảng cách chiều sâu (0 trên mặt, 1 ở thành bên), không theo pháp tuyến từng mặt nhỏ; cạnh vát 6 đoạn, pháp tuyến mượt | ảnh phóng 3× |
| Mascot trắng mất hình trước màn hình trắng | Luật đêm: mascot xanh trước nền sáng; mascot trắng chỉ trên nền xanh hoặc tối | `ringLuma` của `qa.py brand` hoặc `qa.py video` |
| Mascot trắng có thành bên xám #D1D1D1 (kiểu B) | Kiểu C/C2: thành bên #E6F0FF | `qa.py brand --color white` |
| Bóng xám hay đen | Bóng tiếp xúc nhuộm xanh; đèn chính có diện tích cho bóng mềm | xem chân mascot (`crop_base.py`) |
| Ban đêm mặt bàn trắng xóa (đèn màn hình cường độ 4) | Hạ cường độ đèn màn hình còn 1,0 | xem khung đêm |
| Nền tối loang, không đồng nhất (phòng có đèn: tường, bàn, sàn ba mảng tối, có vệt sáng) | Nền phẳng như V2: bàn, tường, sàn một màu không chịu đèn (`world.bg = 'flat'`) | nền ngoài đồ vật lệch ≤ 2 mức |
| Chuyển nền đêm → ngày ra xám đục giữa chừng | Trộn màu nền trong sRGB như V2 (trộn mã sRGB), không trộn trong ánh sáng tuyến tính | tờ khung mỗi 0,25 s qua rạng sáng |
| Vật cùng màu nền tan mất (sổ #003C99 trên nền đêm #003C99) | Đổi vật sang màu token khác (#0068FF) | tờ khung đêm |
| Một nét đen duy nhất trên nền sáng hút mắt, cắt ngang chữ (viền điện thoại) | Thân máy trắng | tờ khung ban ngày |
| Chấm đen ở góc bảng bo tròn | Canvas của bảng tô trắng cả góc ngoài vùng bo | ảnh phóng góc bảng |

### Hình và khung cắt

| Bệnh | Thuốc | Đo |
|---|---|---|
| Ngọn sừng sát hay ra khỏi mép khung ở cú cận | Lùi máy (ca mẫu: 0,62 → 0,70 m ở khóa 3,25 s) | `qa.py boxes`: ngọn sừng ≥ 24 px |
| Thân mascot ra khỏi khung | Cố ý: ghi khoảng giây vào storyboard và `--allow`. Không cố ý: lùi máy | `qa.py boxes` |
| Dải vật sáng lấp ló ở mép khung (ca mẫu: bảng CRM 59 px ở 0,3–2,0 s) | Dời vật ra xa (`SET.crm.x` 0,66 → 0,73). Mọi đích bay, cú lia tính theo hằng bố cục nên tự đi theo | đo dải sáng ở mép = 0 px |
| Đồng hồ, nhãn trong cảnh bị cắt mép | `boxes` hiện chỉ đo mascot và sừng; vật khác soát bằng mắt trên tờ khung | tờ khung |
| Mascot trông như tấm mỏng | Tránh dừng lâu ở góc xoay ngang quá ~35°; dày t (0,6t trông như huy hiệu) | ảnh tĩnh nhiều góc |
| Mascot lún vào bàn khi gật hay lắc | Xoay quanh mép đáy: bù vị trí theo góc gật, góc lắc (`boPose` của ca mẫu) | dải khung quanh cú đáp |

### Chữ

| Bệnh | Thuốc | Đo |
|---|---|---|
| Chữ đè màn hình sáng khi máy quét (thấp nhất 1,0 : 1) | Máy lùi xa và dạt trái ở nhịp chữ; mép trái màn hình sáng ở x ≥ ~850 px; chỉ quét qua cột chữ khi chữ đã rút; dời mốc chữ | `qa.py text` ≥ 4,5 : 1 (sau sửa: 15,9 : 1) |
| Chữ đè lên vật nhiều chi tiết (G1: chữ "thay" đè giao diện điện thoại) | Giao diện trên màn hình dồn sang nửa phải; nửa trái là tường trơn | `qa.py text` |
| Bảng tên trống dòng khi số khách vượt danh sách (9 tên, ~22 khách) | Quay vòng danh sách tên | khung lúc bảng đầy nhất |
| Chữ thưa, người xem không hiểu ý (bản 1: chữ chỉ hiện 6,2 / 16 s) | Chữ chạy suốt phim, mỗi nhịp một câu, kết bằng câu chốt; chỉ dùng lời đã duyệt | chữ phủ ≥ 65 % phần 3D, trống ≤ 0,6 s |
| Chữ giật, cứ 3 khung lặp 1; end card lệch dần (cả bản 1 cũng bị) | `compose` đưa cả hai nguồn về `settb=1/60,setpts=N` trước khi chồng (đã sửa trong `render.py` 21/10) | so khung chữ trên bản ghép với khung lớp phủ: bản 2 khớp 31/31 và 101/101 khung, end card 300/300 |
| Câu chốt dài hơn cột chữ | Nới cột riêng cho nhịp câu chốt, giữ một dòng và cỡ chữ như V2; phần vượt cột nằm cao hơn ngọn sừng | ảnh khung câu chốt; tương phản đo cục bộ |
| `qa.py text` báo 1,0 : 1 ở chữ có tấm nền riêng (khung trắng, khối nhấn) | Báo động giả: đo cục bộ nét chữ so với nền quanh nét | `qa-checklist.md` nấc 5 (bản 2: 4,70 : 1) |
| Chữ trong cảnh quá nhỏ (bảng CRM: chữ 5–8 px) | Bảng to hơn (0,17 × 0,12 → 0,21 × 0,15 m); chỉ giữ chữ to: giờ, số khách, 2 dòng mới nhất | giờ cao 24–25 px; trên điện thoại vẫn nhỏ |
| Chữ trong cảnh nhòe ở khung đầu | Chặn đồng hồ, chữ trong cảnh ở t ≥ 0 (mẫu nhòe chuyển động lấy t < 0) | khung 0 đọc được |

### Chuyển động

| Bệnh | Thuốc | Đo |
|---|---|---|
| Đứng hình ở nhịp "khựng" (ca mẫu: 33 khung liền ở 9,42–10,0 s) | Nín thở nhưng vẫn chao nhẹ giữ thăng bằng, sừng run khẽ, máy đẩy chậm vào | `metrics.py`: chuỗi đứng ≤ 12 khung (sau sửa: 10) |
| Chống nhàm "đạt" giả | Bản nháp 1 mẫu có nhiễu răng cưa làm khung nào cũng "đổi". Chỉ đo trên bản 16 mẫu | `metrics.py` trên bản chất lượng cuối |
| Khóa cuối đứng lâu trước cú cắt | Dời khóa sát cú cắt (15,85 → 15,98 s); khai báo khoảng lặng 1 khung quanh cú cắt | `metrics.py --declared 15.95:16.05` |
| Hứng lặp đơn điệu, giống "game hứng trứng" | Tăng dần (bản 1: 1 → 2 → 3 vật; bản 2: dày dần theo phách, cách 1,5 s rồi 0,5 s), mỗi lần một kiểu hứng (bản 2: một cú nhảy hứng trên không); không điểm số, không tiếng "boing" | xem tờ khung theo nhịp |
| Sừng giật 1,8° trong 1 khung (ca mẫu: 7,00 s và 7,40 s) | Bỏ công tắc bật/tắt 0/1 trong hàm tư thế (ở đây: tắt dao động sừng khi nín thở). Để pha thở đứng yên thì sừng tự đứng đúng chỗ | dải khung quanh mốc bật/tắt |
| Lúc nhanh lúc chậm: cú lia gấp hơn ~100 lần lúc chậm nhất (bản 1) | Một nhịp đều (ca mẫu 120 BPM), mọi cú chạm rơi đúng phách; muốn dồn thì tăng mật độ cú chạm, không tăng tốc máy; một đường máy; bỏ lia gấp, xoay 180°, nhịp khựng | ô động nhất / ô lặng nhất mỗi 0,5 s (bản 2: 4,8 lần; bản 1: 56) |
| Nền phẳng: 42 % khung gần đứng dù vẫn có chuyển động | Mascot đung đưa liên tục (lắc 1,2° chu kỳ 2 s, xoay 2,5° chu kỳ 4 s); nảy theo phách; máy trôi ±1 cm theo hai chu kỳ lệch nhau (5,3 s và 4,1 s), pha chọn bằng quét lưới để không lúc nào cùng dừng; vật nền cuộn (cột tin); lấy đà trước cú bật | `metrics.py`: phần 3D 42 % → 4,4 %; bản ghép 1,04 % |
| Mascot gần như đứng ở nhịp lặng (nảy 2–4 px) | Nảy theo phách: biên 9 mm, dạng \|sin\|, chạm đáy đúng phách | 6–12 px mỗi phách |
| `metrics.py` báo cắt cứng ở cú chuyển màu nền chậm | Chuyển đều, đủ dài (bản 2: rạng sáng 0,97 s tuyến tính, ~3,5 mức mỗi khung). Đường cong êm 0,65–0,75 s bị nhiễu H.264 đẩy vượt ngưỡng | 0 cắt cứng |

### Kể chuyện

| Bệnh | Thuốc | Đo |
|---|---|---|
| Mascot giật mình mà không rõ vì sao (vật gây ra nhỏ, sát mép trên) | Vật to, rõ, xa mép; xuất hiện trước phản ứng ~0,15 s; có cú "bụp" phồng 1,3 lần (ca mẫu: tin đầu dời 2,05 → 1,95 s, phóng từ ô tin thứ 2) | khung quanh nhịp, bóng ~60 px |
| Vật mang thông tin không bao giờ vào khung (ca mẫu: đồng hồ trên điện thoại) | Chuyển thông tin lên vật máy có quay tới (giờ lên tiêu đề bảng CRM) | tờ khung: đọc được giờ |
| Bảng cuộn nhòe đúng lúc máy lia tới | Cho danh sách đứng yên trước khi máy tới (ca mẫu: từ 12,58 s) | khung cận bảng đọc được 5 dòng |
| Lời kêu gọi cuối đứng không đủ đọc (9 chữ, ~1,6 s) | Tính thời gian đọc ở G2; nới end card nếu Minh đồng ý (ca mẫu: cần ~22 s; Minh giữ 21 s khi duyệt hướng bản 2) | đếm chữ × thời gian đọc |
| Xem không đọng lại gì (bản 1) | Một câu chốt đã duyệt, đặt đúng cú chạm cao trào (bản 2: "Bỏ sót khách" bị gạch đúng lúc Bò hứng tin buổi sáng → "Không bỏ sót khách"); end card nhắc lại | người xem nhắc lại được một câu |
| Vật mang ý nghĩa không đọc ra (bong bóng là khối trắng viền dày) | Làm giống biểu tượng 2D đã duyệt (tin nhắn V2: vỏ bo, đuôi, 2 vạch chữ ở cả hai mặt) | tờ khung |

### Vật và va chạm

| Bệnh | Thuốc | Đo |
|---|---|---|
| Vật bay ra khỏi lòng mascot xuyên qua thành (ca mẫu: thẻ khách xuyên cánh chữ U ở 5,20 s, 6,37 s) | Xuất phát đúng chỗ vật nằm, đi thẳng ra trước 18 cm qua lỗ O (Bezier bậc 3, điểm điều khiển đầu thẳng phía trước), rồi mới vòng sang đích | dải 5 khung quanh nhịp |
| Vật lơ lửng: rời mascot khi mascot còn trên không (ca mẫu: 5,13–5,25 s, lỗi bắt buộc) | Vật chỉ rời sau khi mascot đáp xong (`hold` 0,30 s) | dải 5 khung quanh cú đáp; rà chéo |
| Vật văng ra hông khi mascot còn đang xoay (ca mẫu: 6,27–6,37 s) | Đợi mascot quay mặt lại (`hold` 0,31 s); vật bật ra nhanh rồi chậm dần (ease-out) để rời chỗ trước vật kế tiếp | dải khung, không chồng vật |
| Vật lật hướng trong 1 khung lúc vào khe (ca mẫu: 5,95 s, 6,30 s) | Đường bay kết thúc đúng hướng của mascot lúc tới (nối bằng quaternion), rồi mới chuyển sang toạ độ mascot | khung đúng lúc chuyển |
| Nhiều vật cùng lúc bay ra ngoài mép trên | Hạ điểm phóng; ngửa máy lên vài cm ở các khóa đó | khung đủ mọi vật |
| Khung đầu của vật nhảy vị trí (~3,4 cm) | Khung đầu đặt đúng chỗ vật đang nằm, giữ góc xoay của mascot | dải 5 khung |
| Hạt thở phì quá nhỏ, lẹm vào thành khe | To 34–56 px logo, sinh trong lòng khe, lớn dần trong 60 ms, bay thẳng lên rồi mới tỏa | khung có hạt, phóng 3× |
| Không chắc vật lọt khe có chạm thành | Phóng 3× khung lọt khe; tính kích thước (ca mẫu: khe 53 mm, bóng 40 mm; bóng dày 16 mm < Bò dày 43 mm) | ảnh phóng + số |
| Vùng tràn xanh bị vật phía trước che thành vết khuyết trên mascot | Vẽ vùng xanh xong thì xóa độ sâu, để mascot vẽ đè lên | khung cầu |
| Vệt tối dài 200–310 px trên vùng tràn xanh (bản 2, 15,2–16,0 s) | Bóng tiếp xúc của đồ vật là vật trong suốt, vẽ sau vùng xanh: tắt khi vùng xanh tràn | điểm ảnh lệch nền xanh: 1500–2000 → ≤ 6 |
| Tin sau hiện đè tin trước chưa rời chỗ (tin bay chủ yếu theo chiều sâu nên trên hình gần như đứng yên) | Tính đường bay theo màn hình: ngang ease-out bậc 3 (bật rất nhanh), dọc 1,6k − 0,6k² (nhanh rồi chậm), sâu tuyến tính; tin hiện 0,20 s rồi mới bay | tờ khung quanh mỗi lần hiện |
| Vật bay đè qua cột vật cũ trên màn hình | Luôn bay xuống, xa cột; bỏ kiểu "ném lên" | ảnh phóng quanh cột |
| Vật cùng màu mascot lướt trước thân mascot (chỉ còn vạch trắng nhòe) | Vật lùi ra sau qua lỗ O, vòng sau lưng để mascot che, rồi mới tới đích | dải khung |
| Vật chờ cắm vào vai khe khi mascot đang nhảy (đường bay nhắm chỗ mascot sau khi đáp) | Vật giữ cao, rơi muộn; đoạn rơi nối liền vận tốc: gia tốc a = 2(D − v·Td)/Td² với D quãng rơi, Td thời gian rơi, v vận tốc cuối đường bay (để không gãy tốc độ) | soát mọi khung đoạn nhảy |
| Vật mới rơi đè vật cũ còn trong lòng mascot | Vật cũ lùi ngay khi hứng, hoặc trước cú nhảy; lúc lùi tính trong toạ độ của mascot để bám theo cả khi mascot nhảy | soát mọi khung; khoảng cách nhỏ nhất giữa hai vật trên hình (bản 2: 7 px) |

### Cầu 3D → 2D

| Bệnh | Thuốc | Đo |
|---|---|---|
| Họa tiết nền end card bật ra đúng cú cắt | Khung 2D đầu chỉ có nền trơn + mascot; họa tiết nở dần (ca mẫu: khung 960–990, từ mascot ra) | nền ngoài mascot ở khung đầu lệch ≤ 1 mức |
| Mascot 3D lệch mascot 2D ở cú cắt | Đo vị trí 2D bằng chính hàm vẽ của Remotion (`endcard-bo.json`); 3D về đúng vị trí, cỡ, góc sừng, nhịp thở đó | `qa.py lock` ≤ 2 px (ca mẫu: 1,05 px) |
| Thành trong lòng O, khe lộ ra do phối cảnh ở khung khóa | Dẹt độ dày 1 → 0,03 lúc tô phẳng; ống kính hẹp dần (FOV 30° → 7°) | `qa.py lock` |

### Render và máy

| Bệnh | Thuốc | Đo |
|---|---|---|
| Render chậm 5–6 lần | Đang chạy GPU Intel: kiểm cờ GPU | `renderer` trong `render-meta.json` có "NVIDIA" |
| Khung đầu chậm (250–660 ms) | Bình thường: biên dịch shader. Không tính vào tốc độ; xem trung vị | `msMedian` trong `render-meta.json` |
| Vệt nhòe có vân sọc khi vật bay rất nhanh (ca mẫu: khung 298, 446) | Tăng mẫu cho đúng khoảng khung đó: `"sppBoost": [[292, 304, 48], [440, 452, 48]]` trong job `clip` | phóng to khung đó |
| Bản có giờ phim ghi khung 960 là "15.999" | In giờ phim theo số khung (giờ:phút:giây:khung), không theo giây làm tròn | xem khung 960 hiện `00:00:16:00` |

<!-- ===== /file: mascot-film-3d/references/follow-up-playbook.md ===== -->

<!-- ===== file: mascot-film-3d/references/prompt-pack.md ===== -->

# Prompt pack: mẫu 6 khối và storyboard theo giây

**Prompt pack** là kịch bản của một phim. Minh đọc và sửa được. Agent dựng phim chỉ từ file này cộng brand pack (với OPA: `film3d/brand-opa/brand.js` sinh từ `BRAND-SPEC`). Lưu ở `film3d/films/<id>/PROMPT-PACK.md`.

Ví dụ đủ: `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/OPA-Motion-graphic-mascot/film3d/films/thu-mon/PROMPT-PACK.md` (bản 2, Minh duyệt 21/10/2026; bản 1 ở `PROMPT-PACK.ban1.md` cùng thư mục). File này chỉ trích ngắn.

## 1. Cấu trúc file

1. **Dòng trạng thái**: cổng, ngày, ai đã duyệt, bản ghép nằm ở đâu, quyết định đã chốt ở cổng trước.
2. **Kịch bản 6 khối** trong một khối `text`, khoảng 300 chữ. Chi tiết theo giây để ở storyboard, không nhồi vào khối.
3. **Storyboard theo giây** (bảng, mục 4).
4. **Chữ và end card** (mục 6).
5. **Luật rút ra cho phim này**: thêm dần sau mỗi vòng soát. Phim sau đọc lại mục này.

## 2. Mẫu 6 khối

Điền vào chỗ `{...}`. Bỏ dòng nào không dùng.

```text
BRAND
HERO: {tên mascot} — {tả hình bằng các phần có thật của logo}. Đùn từ {nguồn hình}, dày {độ dày},
cạnh vát vào trong. Kiểu {look đã duyệt ở G1}: {màu mặt trước, mặt sau, thành bên}. Không {điều cấm
của brand pack}. Diễn bằng {tư thế, bộ phận cử động, hơi thở}.
ĐỐI THỦ: {ai hoặc cái gì gây khó; không logo nền tảng thật}.
THẾ GIỚI: {bối cảnh; vật chính đặt đâu so với mascot; nền ngay sau mascot là gì}.
BẪY: {động tác chữ ký của mascot}.
BẢNG MÀU: {chỉ màu token của brand pack}.
KẾT: {cầu sang end card: khung khóa khớp vào đâu}.

FORMAT: một film.html, three.js 0.160.0, 1920×1080, 60 fps, {N} s 3D + {M} s end card Remotion;
poseAt(t) vẽ đúng thời điểm t; random có seed; mọi cú chạm là một dòng EVENTS dùng chung cho hình và âm.

LOOK: {preset đã duyệt}; nền {phẳng một màu như V2, đêm → ngày nếu có}; {đèn của đồ vật};
bóng {mềm, nhuộm màu token}; DOF nhẹ, mascot luôn nét; không tone map ACES; nhòe chuyển động 16 mẫu.

BEATS (s): {nhịp BPM}; mọi cú chạm đúng phách; xem bảng storyboard.

CAMERA: {một đường máy liên tục, đều, luôn trôi; độ cao máy; vùng nền trơn cho chữ; cú cầu}.

CHECKS: {mỗi điều là một phép đo có ngưỡng, xem references/qa-checklist.md}.
```

Trích khối CAMERA của Thủ môn bản 2 (để thấy độ cụ thể cần có):

> một đường máy duy nhất: đẩy vào đều 0 → 14,85 s, trôi ngang/dọc ±1 cm (hai chu kỳ lệch nhau, không lúc nào cùng dừng); không lia gấp, không xoay quanh Bò. Cột chữ trái x ≤ 780 px là nền trơn; ...

Bản 1 từng viết "bám nhanh khi hứng, lia gấp giữa các cú" và bị Minh chê "lúc nhanh lúc chậm".

## 3. Luật viết từng khối

**BRAND**
- Tả HERO bằng các phần có thật của logo. Thủ môn: mõm chữ U bo tròn có lòng O xuyên, 2 sừng cong, khe trán (2 mép là 2 lỗ mũi).
- Gọi đúng tên mascot ("Bò OPA") hoặc HERO. Không dùng danh từ con vật chung ("buffalo", "bull", "cow"): model dễ tự thêm mắt, tai, thân.
- Ghi điều cấm ngay trong HERO: không mắt, miệng, tay chân; không bóp méo (chỉ phóng to thu nhỏ đều); sừng về đúng góc ở khung khóa.
- THẾ GIỚI: đặt vật theo luật nền. Với OPA: Bò xanh chỉ đứng trước nền sáng; Bò trắng chỉ trên nền xanh hoặc tối. Chừa sẵn một vùng nền trơn cho chữ.
- ĐỐI THỦ và THẾ GIỚI: không logo nền tảng thật, không tên hay dữ liệu khách thật. Tên giả lấy từ code của dự án (`FAKE_NAMES`).
- KẾT: nói rõ khung khóa khớp vào end card nào, ở vị trí nào.

**FORMAT**: thông số cố định. Ghi rõ độ dài 3D và độ dài end card riêng.

**LOOK**: chỉ lấy preset brand pack đã duyệt ở G1. Không mượn look của Bug Chase: voxel bóng, kính, gỗ, đèn ấm đều trái luật OPA. Nền mặc định phẳng như V2 (luật của Minh từ bản 2): phòng tối có đèn cho ra nền loang.

**BEATS**: để trong bảng storyboard. Khối chỉ trỏ tới bảng.

**CAMERA**
- Một đường máy liên tục; mọi khóa máy là hàm của t.
- Đều: không lia gấp, không xoay quanh mascot. Máy luôn trôi chậm (hai chu kỳ lệch pha) để không có lúc cả máy lẫn vật cùng dừng.
- Ở nhịp có chữ, máy dạt để cột chữ nằm trên nền trơn. Máy chỉ quét ngang qua cột chữ khi chữ đã rút hẳn.
- Cận cố ý làm mascot ra khỏi khung: ghi đúng khoảng giây ("6,58–7,62 s: thân Bò ra khỏi mép dưới, cố ý; sừng luôn trong khung"). Khoảng này thành `--allow` của `qa.py boxes`.

**CHECKS**: mỗi câu là một phép đo có ngưỡng. Mẫu của Thủ môn bản 2:

> mặt trước Bò #0068FF (lệch CIEDE2000 ≤ 2) mọi khung đo; ban đêm nền ngay sau Bò sáng; khung khóa khớp Bò 2D ≤ 2 px; không xuyên vật, không chồng bóng; ...; chữ phủ ≥ 65 % phần 3D, khoảng trống giữa hai nhóm ≤ 0,6 s; tương phản chữ ≥ 4,5 : 1.

## 4. Storyboard theo giây

Cột: `# | Giây | Khung | Người xem thấy | {Mascot} diễn | Máy | Chữ | Âm`.

- **Khung** = giây × 60. Ghi cả hai: Minh nói theo giây, agent sửa theo khung.
- **Mỗi dòng một điều người xem phải thấy.** Hai sự kiện tranh mắt thì tách dòng, lệch giờ.
- **Nhịp chạm ghi giây chính xác** (3,25 s, không "khoảng 3 s"). Các mốc này thành `BEATS`, `EVENTS` trong `timeline.js`, rồi thành cue âm.
- **Một nhịp đều**: chọn BPM của nhạc (ca mẫu 120, phách 0,5 s); mọi nhịp chạm rơi đúng phách.
- **Tăng dần** để hứng lặp không nhàm, bằng mật độ và kiểu hứng, không bằng tốc độ máy. Bản 2: hứng cách 1,5 s rồi dày dần tới mỗi 0,5 s, có một cú nhảy hứng trên không. Bản 1: 1 → 2 → 3 vật.
- **Nhịp lặng vẫn có chuyển động**: đung đưa, nảy hay gật theo phách, máy trôi. Ghi rõ trong cột diễn và cột máy. Bản 2 bỏ hẳn nhịp khựng của bản 1.
- **Chữ**: ghi mốc hiện và mốc rút xong (giây). Chạy suốt phim, mỗi nhịp một câu (bản 1 chỉ đặt ở nhịp giữ, bị chê "không dàn trải").
- **Âm**: ghi gợi ý nếu cần; làm thật ở G6 từ `EVENTS`. Storyboard bản 2 bỏ cột Âm.
- Cuối bảng ghi tổng thời lượng: "16,0 s 3D + 5,0 s end card".

Trích một dòng của Thủ môn bản 2:

| # | Giây | Khung | Người xem thấy | Bò diễn | Máy | Chữ |
|---|---|---|---|---|---|---|
| 7 | 10,20–12,00 | 612–719 | Tin buổi sáng hiện 10,40, bay 10,60; Bò ngẩng nhìn; hứng 11,50 đúng lúc chữ gạch "Bỏ sót khách"; tin ở lại lòng O (nguồn vùng xanh). | Ngẩng 4°, xoay 5° nhìn tin; hứng | như trên | **L8 → L8b**: "Bỏ sót khách" hiện 10,20, bị gạch 11,50; "Không bỏ sót khách" trồi 11,75, khối nhấn quét 12,00 |

Sửa `timeline.js` thì sửa bảng ngay. Ở bản 1, G4 thấy hai dòng tả lệch phim (tên khách, "nảy lên chồng sổ"); sau rà chéo G8, tin đầu dời từ 2,05 s sang 1,95 s, nên bảng lại phải theo.

## 5. Diễn không có mặt (mascot OPA)

Điểm khởi đầu, không phải mức trần. Diễn chưa đọc ra thì tăng biên độ.

| Người xem hiểu | Mascot làm |
|---|---|
| Giật mình | Nảy cứng ~10 % chiều cao trong 3 khung, ngửa 5°, sừng rung tắt dần, 2 tia phì ngắn, đứng sững 6 khung |
| Nghi ngờ | Nghiêng 6–8°, xoay 15° về phía nghi, nín thở 0,5 s (mascot luôn thở nên khựng thở là đọc ra ngay) |
| Quyết tâm | Cúi 8°, lùi lấy đà, thở gấp chu kỳ 0,8 s, 2 hơi phì mạnh |
| Đắc thắng | Hếch 8–10°, một hơi phì dài hướng lên, xoay 15° khoe khối |
| Dịu lại | Bập bênh rồi yên, thở về chu kỳ 2,4 s, một hơi thở ra dài |

Mascot luôn nặng: có bóng tiếp xúc, đáp có bập bênh, xoay quanh mép đáy chứ không lún vào bàn.

## 6. Chữ và end card

- **Lời lấy nguyên văn từ code lời đã duyệt** (`groupById()`, `copyGroupsW()` trong `src/v2w/text/copyW.ts`). Không gõ lại.
- Viết hoa chữ cái đầu mọi dòng. Cụm nhấn dùng Fraunces Italic 800 + khối đánh dấu (`KineticGroup` + `accentMark`, tính theo giây).
- **Chữ chạy suốt phim**: mỗi nhịp một nhóm, kể một mạch truyện. Phủ ≥ 65 % phần 3D, khoảng trống giữa hai nhóm ≤ 0,6 s (bản 2: 80 %, 0,52 s). Mọi nhóm trôi nhẹ khi đứng, như máy quay ảo của V2. Trôi ngang, không trôi dọc chậm: Chrome làm tròn vị trí dọc của chữ nên chữ nhảy từng 1 px.
- **Cột chữ trái**: từ lề an toàn tới x = 780 px (`src/film3d/textColumn.ts`). Dòng dài hơn cột thì co đều cả nhóm (cho phép tới 15 %). Riêng câu chốt cỡ lớn kiểu V2 (112 px) được nới cột tới x ≈ 1240 px để giữ một dòng; phần x ≥ 1130 px phải nằm cao hơn ngọn sừng (ca mẫu: trên y = 450 px, ngọn sừng thấp nhất ≈ 488 px).
- **Câu chốt kiểu V2** (ca mẫu: `src/film3d/ThesisW.tsx`, dựng lại theo chương "RÕ" của V2 16:9 `scenes/t3/StrikeKk6.tsx`, không sửa file của V2): nét gạch đúng cú chạm cao trào, khối nhấn quét đúng phách. Chữ trắng trên khối #0068FF chỉ đạt 4,75 : 1 trên lý thuyết, nên không dùng nét mảnh hay chữ nhỏ trên khối này.
- **Mỗi nhóm đứng ≥ 1,8 s** từ lúc vào tới lúc bắt đầu rút (luật đọc V2: 5–6 chữ cần 1,67–1,93 s).
- **Màu chữ theo nền sau cột** (`TEXT_ON`): nền tối thì chữ trắng; nền sáng thì chữ đen. Bản 2: đêm chữ trắng trên #003C99, ngày chữ đen trên trắng.
- **End card**: dùng cảnh đã duyệt (Thủ môn: chương "trạm OPA" 16:9 của V2), dời về mốc 0 của end card. Không đổi chữ, không thêm giá (`SHOW_PRICE=false`). CTA lấy đúng từng chữ từ code; không đoán.
- **Khung đầu end card chỉ có nền trơn + mascot.** Họa tiết nở dần sau đó, để không lộ cú cắt.
- End card cần chỗ để tagline đọc đủ. Thủ môn: 5,0 s, chữ chuyển động phát ×1,40, đoạn đọc tagline giãn ×0,80 (`src/film3d/thuMonPlan.ts`).

## 7. Nhận prompt pack từ ngoài (ví dụ PDF Bug Chase)

Không "chỉ thay khối BRAND". Phần lớn cái duyên của Bug Chase nằm ở thứ OPA cấm:

| Bug Chase dựa vào | Luật OPA | Đổi thành |
|---|---|---|
| Mặt voxel: mắt, chớp, má hồng | Không thêm mắt, miệng | Diễn bằng tư thế, sừng, hơi thở (mục 5) |
| Tay chân, nhảy phím | Mascot chỉ là cái đầu | Nảy, trượt, húc, hứng bằng cả khối |
| Voxel bóng, kính, gỗ, đèn ấm | Không 3D bóng loáng; chỉ 5 màu | Look C2 tô phẳng, thế giới trắng–xanh |
| Dễ thương, đỏ mặt, tim | Không dễ thương kiểu trẻ con | Quyết tâm, chắc chắn, đắc thắng |
| Lưới pixel thành voxel | Không đổi tỉ lệ | Đùn khối từ vector (voxel lệch hình 5–40 %) |

Cách làm:
1. Đọc pack, xếp nội dung vào 6 khối.
2. Liệt kê chỗ trái brand pack và cách đổi (bảng trên).
3. Hỏi Minh gộp một lần ở G0, rồi sang G1 thử look.
4. Giữ cấu trúc, không chép nguyên văn prompt hay các vòng follow-up của PDF.

## 8. Luật rút ra từ ca mẫu (mặc định cho phim sau)

Nguồn: mục "Luật rút từ G1" của PROMPT-PACK Thủ môn và `docs/film3d/g1-thu-look.md`.

1. **Luật đêm**: cảnh tối thì nền ngay sau mascot xanh luôn là vật sáng (màn hình). Đo bằng độ sáng vòng nền quanh mascot (`ringLuma` của `qa.py brand` hoặc `qa.py video`).
2. **Vùng chữ là nền trơn.** Khi có chữ, mép trái của màn hình sáng hay viền điện thoại nằm ở x ≥ ~850 px (cột chữ tới 780 px).
3. **Hạt thở phì** to 34–56 px logo, sinh trong lòng khe, lớn dần trong 60 ms, bay thẳng lên rồi mới tỏa.
4. **Mặt sau cùng màu mặt trước** (dấu đối xứng trái–phải): mascot xoay 180° vẫn đúng màu thương hiệu.
5. **Look C2**: cạnh vát bo tròn 0,08t có vệt sáng; thành bên nhận sáng từ #003C99 tới gần #0068FF; ranh màu tính theo vị trí trên cạnh vát, không theo từng mặt lưới.
6. **Không khung đứng hình**, kể cả nhịp khựng. Đo trên bản chất lượng cuối.
7. **Cầu 3D → 2D**: khung khóa lấy từ `out/endcard-bo.json`; mascot dẹt dần (độ dày 1 → 0,03) lúc tô phẳng; khai báo khoảng lặng 1 khung quanh cú cắt khi đo chuyển động.
8. **Vật bay ra khỏi lòng mascot** đi thẳng theo chiều sâu trước, rồi mới dạt ngang (đường Bezier bậc 3, điểm điều khiển đầu nằm thẳng phía trước).
9. **Chữ trong thế giới 3D** (đồng hồ, tên trên bảng) vẽ thành texture phẳng, không chịu đèn, font cục bộ. Danh sách tên phải quay vòng: số khách có thể vượt độ dài danh sách.
10. **Tránh dừng lâu ở góc xoay ngang quá ~35°**: mascot đùn trông như tấm mỏng. Trong chuyển động thì xoay 180° vẫn được.

Thêm từ rà chéo G8 của ca mẫu (`FOLLOWUPS.md`, mục "Rà chéo G8 vòng 1"):

11. **Nguyên nhân phải thấy trước phản ứng.** Vật gây giật mình phải to, rõ, xa mép, và xuất hiện trước phản ứng ~0,15 s (ca mẫu: tin đầu bật ở 1,95 s, Bò giật mình 2,10 s; bóng "bụp" phồng 1,3 lần).
12. **Vật chỉ rời mascot khi mascot đã yên**: đáp xong, quay mặt lại. Ca mẫu: thẻ rời lòng O khi Bò còn trên không thành bóng lơ lửng (lỗi bắt buộc); sửa bằng `hold` 0,30–0,31 s.
13. **Thông tin phải nằm nơi máy quay tới.** Ca mẫu: đồng hồ trên điện thoại không bao giờ vào khung, phải chuyển giờ lên tiêu đề bảng CRM. Bảng phải đứng yên trước khi máy lia tới, kẻo cuộn nhòe.
14. **Lời kêu gọi cuối cần đủ thời gian đọc.** Ca mẫu: CTA 9 chữ chỉ đứng ~1,6 s; muốn đọc thoải mái thì cần ~22 s. Minh giữ 21 s ở G2 và giữ tiếp khi duyệt hướng bản 2. Tính thời gian đọc của CTA ngay ở G2.

Thêm từ bản 2 (`PROMPT-PACK.md` mục "Luật rút từ bản 2", `FOLLOWUPS.md` phần BẢN 2). Đây là mặc định cho phim sau:

15. **Nền phẳng như V2**: đêm #003C99, ngày trắng; bàn, tường, sàn một màu không chịu đèn. Chuyển đêm → ngày trộn trong sRGB, đều, khoảng 1 s.
16. **Một nhịp đều.** Mọi cú chạm rơi đúng phách nhạc; một đường máy chậm; không lia gấp, không xoay quanh mascot, không nhịp khựng. Muốn dồn dập thì tăng mật độ cú chạm, không tăng tốc máy.
17. **Nền phẳng cần chuyển động liên tục.** Cùng một chuyển động, nền phẳng ra ít điểm ảnh đổi hơn phòng có đèn khoảng 10 lần. Vì vậy máy trôi liên tục với pha chọn để không lúc nào cùng dừng; mascot luôn đung đưa; nhịp lặng dùng cử chỉ theo phách. Đo khung đứng trên bản chất lượng cuối, sau khi ghép chữ.
18. **Chữ chạy suốt phim**, mỗi nhịp một câu, một mạch truyện, kết bằng một câu chốt đã duyệt đặt đúng cú chạm cao trào.
19. **Vật mang ý nghĩa giống biểu tượng 2D đã duyệt** (bong bóng = tin nhắn V2), và không bao giờ nằm trên nền cùng màu.
20. **Đường bay tính theo màn hình**, không theo chiều sâu: vật bay chủ yếu về phía máy thì trên hình gần như đứng yên, và vật sau đè vật trước. Vật bay ra không đi ngang qua cột vật cũ.
21. **Vật cùng màu mascot không lướt trước thân mascot**: lùi ra sau để mascot che.
22. **Thêm cho luật 12:** lúc vật lùi khỏi lòng mascot, tính trong toạ độ của mascot, nên vật đi theo cả khi mascot nhảy. Vật cũ phải rời trước khi vật mới tới.

<!-- ===== /file: mascot-film-3d/references/prompt-pack.md ===== -->

<!-- ===== file: mascot-film-3d/references/qa-checklist.md ===== -->

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

<!-- ===== /file: mascot-film-3d/references/qa-checklist.md ===== -->

<!-- ===== file: mascot-film-3d/references/render-quality.md ===== -->

# Chất lượng render: tích lũy mẫu, hoàn thiện, màu, GPU, gửi khung, mã hóa

Mô tả đúng code của ca mẫu trong `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/OPA-Motion-graphic-mascot`:
`film3d/lib/accum.js` (tích lũy, hoàn thiện), `film3d/lib/wire.js` (gửi khung), `tools/film3d/render.py` (Chrome, nhận khung, mã hóa, ghép), `film3d/lib/world-desk.js` (đèn, phơi sáng), `film3d/lib/mascot3d.js` (look C2). Số đo lấy từ `render-meta.json` của ca mẫu, `docs/film3d/g1-thu-look.md` và báo cáo lane T.

## 1. Đường đi của một khung

```
poseAt(t + lệch) → world.apply → vẽ 1 mẫu ở 3840×2160 (RGBA16F, có độ sâu) → cộng vào bộ đệm RGBA32F
   ↑ lặp 16 lần (mẫu i = 0 … 15)
bộ đệm 32F → ×1/16 ×EXPO → kẹp [0, 1] (không tone map) → Lanczos-3 ngang → Lanczos-3 dọc + sRGB + dither
→ RGBA8 1920×1080 → readPixels → WebSocket → Python → ffmpeg FFV1 (clip.mkv) → H.264 (clip.mp4)
```

## 2. Tích lũy 16 mẫu

Một **mẫu** là một lần vẽ cả khung. Mẫu i trong N lệch bốn thứ (`sampleOffsets(i, N, 0.45)`). Mặc định N = 16. N không được chia hết cho 7, để phép xáo π(i) bên dưới đi qua đủ mọi mẫu; lũy thừa của 2 và 48 đều được.

| Lệch | Cách tính | Ra hiệu ứng |
|---|---|---|
| Thời điểm | t + (0,45 / fps) × ((π(i) + 0,5) / N − 0,5), với π(i) = (7i + 3) mod N | Nhòe chuyển động. "Màn trập 0,45 khung" = cửa chập mở 45 % thời gian một khung. π(i) xáo thứ tự để lệch thời gian không đi cùng lệch ống kính |
| Dưới điểm ảnh | dãy Halton cơ số 2 và 3, trong ±0,5 điểm ảnh (khung 2×) | Khử răng cưa |
| Điểm trên ống kính | Halton cơ số 5 và 7, ánh xạ lên đĩa | Xóa phông (DOF, độ sâu trường ảnh) |
| Hướng đèn | Halton cơ số 11 và 13; ca mẫu xoay đèn chính trong nón 7° | Bóng mềm |

- **Dãy Halton** là dãy số rải đều có quy luật, đều hơn số ngẫu nhiên, và tất định.
- **Xóa phông bằng xô phép chiếu** (`lensAndJitter`): máy dời theo (ex, ey) = điểm trên đĩa × độ mở ống kính; ma trận chiếu cộng `P[8] −= P00·ex/focus`, `P[9] −= P11·ey/focus`, nên mặt phẳng nét giữ ở khoảng cách `focus`. Lệch dưới điểm ảnh cộng vào cùng hai ô đó. Ca mẫu: độ mở 0,006 m; `focus` = khoảng cách máy tới mascot; độ mở về 0 ở khung khóa.
- **N = 1** (nháp): không lệch gì, như máy ảnh lỗ kim, có răng cưa.
- Mỗi mẫu vẽ vào đích RGBA16F có độ sâu; bóng đổ vẽ lại cho từng mẫu; rồi cộng vào RGBA32F bằng phép blend cộng.
- **Phải cộng dồn bằng 32F.** Probe lane T: cộng 0,001 hai lần vào 0,25 thì 16F ra 0,25195, 32F ra 0,25200.
- Cần extension `EXT_float_blend`; thiếu thì trang ném lỗi "thiếu EXT_float_blend".
- **Tăng mẫu theo đoạn** (`sppBoost` trong job `clip`): `[[f0, f1, spp], ...]`. Bản 1 của ca mẫu: vật bay rất nhanh làm vệt nhòe có vân sọc ở khung 298 và 446, nên khung 292–304 và 440–452 vẽ 48 mẫu; khung khác vẫn 16. Bản 2 đi đều nhịp, không còn cú bay nhanh như vậy, nên không cần.

## 3. Hoàn thiện trên GPU (resolve)

`Accumulator.resolve({expo, tone, frame, grain})`, khoảng 0,7 ms mỗi khung trên RTX:

1. Nhân 1/N rồi nhân EXPO (phơi sáng).
2. `tone: 0` = kẹp vào [0, 1] (ca mẫu dùng); `tone: 1` = Neutral. Không có ACES.
3. Lanczos-3 thu nhỏ 2:1, tách hai lượt (ngang rồi dọc), trong ánh sáng tuyến tính. Kẹp trước rồi mới thu, để không có viền tối quanh vùng sáng.
4. OETF sRGB: đường cong đổi ánh sáng tuyến tính sang mã màu của màn hình.
5. **Dither TPDF ±1 mức**: cộng nhiễu tam giác rất nhỏ, để dải chuyển màu không thành bậc. Grain có seed theo khung: có sẵn, ca mẫu để 0.
6. Lật dòng ngay trong shader, để `readPixels` ra ảnh từ trên xuống. Dữ liệu float không ra khỏi GPU.

`scale` của `Accumulator` chỉ nhận 1 hoặc 2 (render 1× hoặc 2× rồi thu về 1080p).

## 4. Màu

- #0068FF nằm sát mép gam màu sRGB (R = 0, B = 255). Tone map nào cũng kéo lệch: lane B tính ACES lệch ΔE2000 3,98, Neutral 1,31, kẹp 0. Vì vậy: không tone map, vật liệu không phản xạ bóng, phơi sáng tính chứ không đoán.
- Trên MP4, #0068FF giải mã ra (0, 103, 255) = #0067FF. Đây là số dự án từng đo trên V2, V3. `qa.py` lấy đích (0, 104, 255).
- **EXPO tính giải tích** (`world-desk.js`): EXPO = 0,995·π / (I_key·key_z + I_fill·fill_z + I_hemi·hemi_B). Tức là chọn sao cho mặt trắng hướng thẳng về máy, dưới đèn ban ngày, ra 0,995: sát trắng mà không cháy. Ca mẫu: EXPO = 0,8305.
- **Vật không chịu đèn** (màn hình, bong bóng, hạt thở, vùng tràn xanh) nhân màu với `INV_EXPO` = 1/EXPO. Sau bước ×EXPO, chúng ra đúng màu token.
- **Nền phẳng** (`style.bg = 'flat'`, mặc định từ bản 2):
  - bàn, tường, sàn là một vật liệu không chịu đèn (`fieldMat`), cùng màu với màu xóa khung, nhân `INV_EXPO`;
  - đèn của đồ vật luôn ở mức ban ngày; đêm hay ngày chỉ đổi màu nền (#003C99 → trắng), như V2;
  - đổi màu nền trộn mã sRGB (`getRGB(..., SRGBColorSpace)` rồi `setRGB(..., SRGBColorSpace)`). Trộn trong ánh sáng tuyến tính cho màu xám đục giữa chừng;
  - kiểu phòng có đèn của bản 1 vẫn còn (`style.bg = 'room'`).
- **Look C2** (shader `C2_FS` trong `mascot3d.js`; mascot không dùng đèn của cảnh):
  - mặt trước và mặt sau giữ đúng màu token, phẳng tuyệt đối;
  - trọng số cạnh vát f tính theo vị trí chiều sâu |z| của điểm (0 trên mặt, 1 ở thành bên), không theo pháp tuyến từng mặt nhỏ, nên ranh màu mượt, hết khấc;
  - thành bên đi từ token đậm (#003C99) tới token (#0068FF) theo độ sáng e = 0,30 + 0,55·max(n·key, 0) + 0,20·max(n·fill, 0), với đèn tính trong không gian vật (bám theo mascot);
  - vệt sáng mảnh dọc cạnh vát hướng về đèn chính (`uRim` 0,45);
  - `uFlat` = 1: tô phẳng hoàn toàn (khung khóa); `uWhite` và vùng tràn xanh đổi sang bảng màu trắng theo từng điểm ảnh (cầu sang end card);
  - cuối cùng nhân `uInvExpo`.
- Hình C2: dày t, cạnh vát 0,08t, 6 đoạn, pháp tuyến mượt tới 40°, `bevelOffset = −bevel` để viền ngoài nằm đúng vector. Kiểu A, B, C của G1 vẫn còn trong `createBo` để so.
- `tools/qa/palette.py` của dự án báo lỗi oan trên ảnh 3D (mảng chuyển sắc). Phim 3D đo màu theo mặt nạ bằng `qa.py`.

## 5. GPU và Chrome

Bộ cờ đủ nằm ở hằng `BASE_FLAGS`, `GPU_FLAGS` của `render.py`. Phần quan trọng:

```
chrome.exe --headless --use-angle=d3d11 --force_high_performance_gpu --enable-gpu --ignore-gpu-blocklist
           --force-color-profile=srgb --disable-background-timer-throttling --disable-renderer-backgrounding
           --user-data-dir=<thư mục tạm của job> <url>
```

| Cờ (đo bằng chuỗi GPU của WebGL, lane T) | GPU |
|---|---|
| Mặc định; `--use-angle=d3d11 --enable-gpu --ignore-gpu-blocklist`; cờ kiểu HyperFrames; `d3d11on12` | Intel UHD 770 |
| `--use-angle=d3d11 --force_high_performance_gpu` | **RTX 3070 Ti** (mặc định của skill) |
| `--use-angle=vulkan --enable-features=Vulkan --no-sandbox` | RTX, nhanh hơn ~40 %, nhưng phải tắt sandbox; chưa kiểm tất định trên đường này |
| `--use-angle=swiftshader` | CPU |
| **Linux (máy vmiz):** `--use-angle=d3d11` | Không có WebGL (d3d11 chỉ có trên Windows) |
| **Linux:** `--use-angle=gl --enable-gpu --ignore-gpu-blocklist` | **RTX 3070 Ti**, ANGLE OpenGL 4.5 (mặc định của `render.py` trên Linux, đã render thử 2026-10-29) |
| **Linux:** `--use-angle=vulkan --enable-features=Vulkan` | RTX, không cần `--no-sandbox`; chưa kiểm tất định |

- Tin đầu (`hello`) mang chuỗi GPU. Không có "NVIDIA" thì `render.py` dừng ngay.
- Bản Chrome (user agent) ghi ở tin đầu và tin `done`. Khác nhau (Chrome tự cập nhật giữa chừng) thì báo lỗi. Ca mẫu: `HeadlessChrome/156.0.0.0`.
- Mỗi job một thư mục profile tạm. Xong hoặc lỗi đều dọn cả cây tiến trình Chrome trong khối `finally` (Windows: `taskkill /PID <pid> /T /F`; Linux: `os.killpg`, Chrome chạy trong session riêng). Hết giờ sau 900 s.
- HTTP chỉ phục vụ file trong `film3d/`, ở 127.0.0.1 (cổng ngẫu nhiên khi chạy job, 8765 khi `serve`), không cache.

## 6. Gửi khung: WebSocket, không CDP

- **CDP** (Chrome DevTools Protocol) là đường Playwright, Puppeteer dùng để điều khiển Chrome. Chụp khung 1080p qua đó mất 190–1100 ms. Ngay cả WebSocket, khi Chrome đang nối Playwright, cũng tụt còn 260–380 ms mỗi tin từ tin thứ 3.
- Cách của skill: Chrome chạy như tiến trình thường, không nối CDP; trang tự render rồi đẩy khung qua WebSocket. 2,3 ms mỗi khung 1080p (4K: 7,7 ms).
- Mỗi tin: `[u32 little-endian độ dài header][header JSON UTF-8][dữ liệu]`. Python trả "ok" sau mỗi tin; trang chờ "ok" rồi mới gửi tin sau, để giữ nhịp và không dồn bộ nhớ.
- Chrome chia tin lớn thành nhiều mảnh. Bộ nhận Python ghép đủ mảnh rồi mới xử lý.
- Bộ nhận chỉ dùng thư viện chuẩn + numpy (gỡ mặt nạ XOR của WebSocket bằng numpy).

## 7. Mã hóa

Khung về Python được đẩy thẳng vào ffmpeg:

```
-f rawvideo -pix_fmt rgba -s 1920x1080 -r 60 -i - -c:v ffv1 -level 3 -pix_fmt bgr0 -slices 24 -g 1   → clip.mkv
```

FFV1 là codec không mất chất lượng; 960 khung khoảng 1,2 GB. Rồi ra H.264 (hằng `RGB2YUV`, `X264` của `render.py`):

```
-vf scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p,
    setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709
-c:v libx264 -preset slow -profile:v high -b:v 25M -maxrate 30M -bufsize 50M -pix_fmt yuv420p
-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv -movflags +faststart
```

- **bt709** là chuẩn màu của video HD. **Dải TV** dùng mã 16–235 thay vì 0–255, là chuẩn của video phát.
- Thiếu `setparams` thì nhãn primaries và trc bị ghi "unknown".
- v0: mỗi job `clip` ra một file FFV1. Chưa chia chunk 120 khung như phương án; job lỗi thì chạy lại cả job.
- **Mux âm** (G6, G7) không mã hóa lại hình: chép nguyên luồng H.264 của bản ghép, thêm AAC 320k, `-aac_pns 0`, master mono tách thành 2 kênh giống nhau, theo quy ước mux của dự án. Kiểm bằng md5 luồng hình (`ffmpeg -i <mp4> -map 0:v -c copy -f md5 -`): bản giao phải trùng bản ghép.
  - Ca mẫu bản 2: `score_thumon_thuvien.py --video <bản ghép> --out <bản −16> --out-14 <bản −14>`. Tách kênh bằng `pan`: mỗi kênh −3,0103 dB so với mono (bản −16, độ to bằng master như `-ac 2`), hoặc −1,0103 dB (bản −14: cộng +2 dB sau limiter, không ép limiter thêm).
  - Bản 1: `score_thumon_build.py --video <bản ghép> --out <file giao>` (`-ac 2`).

## 8. Ghép lớp phủ chữ + end card

- Lớp phủ render bằng Remotion: `--codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png --muted`. Ra `.mov` ProRes 4444 có kênh trong suốt, bt709 dải TV. Ca mẫu: 1260 khung, ~177 MB; ffprobe đọc ra `yuva444p12le`.
- `render.py compose <3D.mkv> <lớp phủ.mov> <ra.mp4> [--timecode]`:
  - cả hai nguồn đưa về `settb=1/60,setpts=N` trước tiên. `clip.mkv` (Matroska) ghi mốc giờ theo ms, không chia chẵn cho 60 fps; thiếu bước này thì `overlay` chọn lệch khung: chữ giật, cứ 3 khung lặp 1, end card lệch dần. Lỗi có từ bản 1, rà chéo bản 2 mới bắt được; sửa ngày 21/10;
  - phần 3D đổi sang RGB (`gbrp`); lớp phủ đổi về RGB có alpha theo đúng bt709 dải TV;
  - chồng bằng `overlay=format=gbrp:alpha=straight`. **Alpha thẳng** nghĩa là màu chưa nhân sẵn với độ trong suốt; Remotion xuất kiểu này;
  - phần 3D ngắn hơn lớp phủ thì giữ khung cuối (`tpad ... stop_mode=clone`); end card đục che đi;
  - mã hóa H.264 một lần như mục 7, `-r 60`;
  - `--timecode`: in giờ phim ở góc dưới phải cho bản duyệt, theo số khung (giờ:phút:giây:khung, `drawtext ... timecode ... rate=60`), nên khung 960 hiện đúng `00:00:16:00`. Bản đầu in theo giây làm tròn và ghi khung 960 là "15.999". Font cục bộ, đường dẫn tương đối, nên lệnh tự chạy từ gốc dự án.
- **Vì sao không đưa MP4 3D qua Remotion:** chuỗi 3D → H.264 → Remotion chụp JPEG → H.264 là ba lần nén chồng lên một màu xanh sát mép gam màu (lane Q). Ghép bằng ffmpeg chỉ nén H.264 một lần, từ nguồn không mất.

## 9. Tốc độ đo thật (RTX 3070 Ti, D3D11, không CDP)

| Việc | Số đo | Nguồn |
|---|---|---|
| Clip 960 khung, 16 mẫu, 2×, nền phẳng, không tăng mẫu (Thủ môn bản 2, bản giao) | trung vị 25 ms/khung trong trang; cả job 105 s; mã hóa H.264 thêm ~17 s | `out/v2-hq/render-meta.json` |
| Clip 960 khung, 16 mẫu, 2×, có 26 khung 48 mẫu (Thủ môn bản 1) | trung vị 36 ms/khung trong trang; cả job 84,5 s (bản trước, chưa tăng mẫu: 75,6 s); mã hóa H.264 thêm ~17 s | `out/animatic-hq/render-meta.json` |
| Cùng clip, 1 mẫu, 1× | trung vị 15 ms/khung; cả job 36,2 s | `out/animatic/render-meta.json` |
| Khung lẻ kèm mặt nạ (job `frames`, `stills`) | trung vị 44–97 ms | `render-meta.json` các job |
| Đoạn 4 s của G1 | 26 ms/khung; 240 khung ~12 s | `g1-thu-look.md` |
| Khung đầu (biên dịch shader) | 250–660 ms; khung 48 mẫu tới ~1 s | G1, ca mẫu |
| Cảnh vừa, 614 nghìn tam giác, 3 đèn (probe) | 100,6 ms/khung | lane T |
| Lỡ chạy trên Intel (probe) | ~500 ms/khung | lane T |

Hệ quả: bản nháp 1 mẫu chỉ nhanh gấp 2 mà đo sai (nhiễu răng cưa). Duyệt luôn bằng bản chất lượng cuối.

## 10. Chưa làm, để phim sau

- **Số mẫu tự động theo tốc độ**: N = clamp(⌈v·0,45/2⌉, 16, 64), v là tốc độ trên màn hình (px/khung). Lane T đề xuất. Ca mẫu mới làm tay bằng `sppBoost` cho hai đoạn đã thấy vân sọc.
- **Chia chunk 120 khung**, chunk lỗi thì render lại riêng chunk đó.
- **Kiểm xuyên vật tự động** bằng trường khoảng cách (SDF): mascot lấy từ đường viền logo, đạo cụ giải tích, thử ở 240 Hz. Lane T thiết kế, chưa dựng.
- **`dump=anchors`** (điểm neo cho chữ bám theo vật): ca mẫu chưa cần.
- **Vulkan**: chỉ khi cần nhanh hơn; chấp nhận tắt sandbox; phải kiểm lại tất định.

<!-- ===== /file: mascot-film-3d/references/render-quality.md ===== -->
