Ngày tạo: 23/10/2026 · Dựa trên phân tích 3 mẫu Envato: `research/envato-chatbot-2026-10-23/PHAN-TICH-3-MAU.md` (mã hiệu ứng H01–H21)
Trạng thái: kịch bản, chưa dựng.
- Toàn bộ chữ trên màn hình là **gợi ý, chờ Minh duyệt lời**.
- Cảnh 3 có một chỗ **hỏi Hùng** (khung chat nghiêng 2.5D).

# Promo 32 s "OPA trực chat cho đội bán hàng"

## 0. Mạch truyện

Khách nhắn khắp nơi → một khách hỏi → OPA trả lời ngay và ghi vào CRM → một OPA trực mọi kênh → không bỏ sót khách nào → logo và lời mời.

Mạch này lấy khung kể chuyện của mẫu 2 (vấn đề → giới thiệu → tính năng → kết), giao diện chat của mẫu 1 và mẫu 3, và chuyển động logo của bộ KB1–KB9.

## 1. Phân công công cụ

Chia việc theo một luật: **cảnh nào có chữ tiếng Việt phải đúng thì làm bằng After Effects; chuyển động hình khối thì giao Omni Flash.**

| Cảnh | Giây | Công cụ | Nội dung | Hiệu ứng | Khung đầu → cuối (Omni) |
|---|---|---|---|---|---|
| C1 | 0–4 | After Effects | Tin nhắn dồn, huy hiệu đỏ đếm số | H18, H11, H02, H01 | — |
| C2 | 4–8 | After Effects | Khách gõ câu hỏi, máy bám theo chữ | H07, H06, H08 | — |
| C3 | 8–14 | After Effects | OPA trả lời, ghi CRM, tiêu đề đổi từ | H17, H12, H06, H04, H21 | — |
| C4 | 14–20 | **Omni Flash** + chữ AE | Một OPA trực mọi kênh (mạng lưới) | H10, H01 | `K02` → `K07` |
| C5 | 20–26 | **Omni Flash** + chữ AE | Hứng tin nhắn, không bỏ sót | KB8 rút gọn, H03 | `K01` → `K01` |
| C6 | 26–32 | **Omni Flash** + chữ AE | Đóng logo, khẩu hiệu, nút CTA | KB9 cảnh C, H07 | `K01` → `K04` |

**Khung hình:** 16:9, 1920 × 1080, comp 30 fps như video "OPA Agent × Pancake" đã duyệt. Clip Omni đặt thẳng vào comp; soát giật ở đoạn chạy nhanh, vì fps của clip Omni có thể khác 30.

**Nhịp:**
- 120 BPM, một phách = 0,5 s, mọi mốc nằm trên lưới 0,25 s.
- Cảnh dài 4 hoặc 6 s.
- Chữ có mặt ở mọi cảnh, mỗi nhịp một câu.
- Không đoạn nào đứng yên quá 0,5 s.

## 2. Từng cảnh

### C1 · 0–4 s · "Tin nhắn dồn" (After Effects, nền trắng)

**Chữ (gợi ý):** "Khách nhắn khắp nơi" — tiêu đề Be Vietnam Pro 800, 88 px, góc trên trái, lề 72 px.

| Giây | Lớp | Thuộc tính | Giá trị | Nội suy / hiệu ứng |
|---|---|---|---|---|
| 0,25 / 0,75 / 1,25 | 3 bong bóng khách (nền #E6F0FF, chữ #0A0A0A, 38 px) | Scale, Anchor ở góc đuôi | 0 → 105 → 100 % trong 8 khung | H18, lệch nhau 0,5 s |
| 0,5 → 2,0 | Tiêu đề | Text Animator theo ký tự; trong animator: Opacity 0 %, Position X +40, Blur 12 | Range Start 0 → 100 % | H02, Ease out |
| 1,25 → 3,0 | 3 huy hiệu đỏ `ALERT #E5484D` | Slider "So" | 1 → 12 · 1 → 27 · 1 → 99 (hiện "99+") | H11, Ease in; huy hiệu nảy 100 → 115 → 100 % mỗi lần tăng chục |
| 2,5 → 3,5 | 3 bong bóng nhỏ thêm | Scale | Bật dày hơn, lệch 0,25 s | Tạo cảm giác "dồn dập" |
| 0 → 3,75 | Null máy quay | Scale | 100 → 104 % | Tuyến tính |
| 3,75 → 4,25 | Khối #0068FF phủ kín | Position X | Quét từ trái sang, che rồi để lại nền xanh | H01, Ease in-out |

Câu chữ trong bong bóng (giả, chung chung): "Còn hàng không shop?", "Ship Hà Nội mấy ngày ạ?", "Giá sỉ thế nào ạ?".

### C2 · 4–8 s · "Khách hỏi" (After Effects, nền xanh #0068FF)

**Chữ:** câu khách gõ "Shop còn size M không ạ?" (gợi ý), Be Vietnam Pro 500, 48 px, chữ đen trong ô trắng.

| Giây | Lớp | Thuộc tính | Giá trị | Nội suy / hiệu ứng |
|---|---|---|---|---|
| 4,25 → 4,5 | Nút "+" tròn trắng | Scale | 0 → 110 → 100 % | Bật, Ease out |
| 4,5 → 4,9 | Ô nhập trắng | Rectangle Size, Roundness = cao/2, Anchor mép trái | [96, 96] → [1100, 96] | H07, Ease out mạnh |
| 4,9 → 6,9 | Chữ câu hỏi | Source Text gõ dần (expression mục 4) | 0 → 24 ký tự | H06 |
| 4,9 → 6,9 | Null máy quay | Scale 150 %, Position X bám mép phải chữ | Trôi đều sang phải | H08 |
| 6,9 → 7,25 | Nút gửi: tròn trắng, dấu đầu bò xanh nhỏ ở giữa | Scale | 0 → 110 → 100 % | Bật |
| 7,25 → 8,0 | Null máy quay | Scale, Anchor ở tâm nút gửi | 150 → 900 % | Ease in mạnh; nút trắng phủ kín màn hình → nối sang C3 |

### C3 · 8–14 s · "OPA trả lời" (After Effects, nền trắng)

**Chữ (gợi ý):**
- **Tiêu đề đổi từ (H04):** "OPA *trả lời ngay*" → "OPA *ghi vào CRM*" → "OPA *có báo cáo*". Cụm nhấn dùng Fraunces Italic 800 kèm khối đánh dấu quét dưới chữ (BRAND-SPEC mục 2).
- **Bong bóng OPA:** "Dạ còn ạ! Anh chị cho OPA xin số điện thoại để giữ hàng nhé."
- **Chip:** "✓ Đã ghi vào CRM".

| Giây | Lớp | Thuộc tính | Giá trị | Nội suy / hiệu ứng |
|---|---|---|---|---|
| 8,0 → 9,0 | Khung chat (thẻ trắng, viền 2 px #0068FF, bo 32 px); avatar OPA ở đầu khung | Scale, Anchor ở tâm avatar | 900 → 100 % | H17 zoom ra: hóa ra nút gửi là avatar OPA |
| 8,0 → 9,0 | Khung chat | Y Rotation (lớp 3D) | 20° → 0° | H12 không glow. **Hỏi Hùng**; nếu không duyệt thì bỏ dòng này |
| 9,0 → 9,5 | Bong bóng khách (câu C2) | Position Y + Scale từ góc đuôi | Trượt vào khung | H18 |
| 9,5 → 10,25 | Ba chấm "đang gõ" của OPA | Position Y (expression sóng) | Nhún lệch pha | H06 |
| 10,25 → 11,75 | Bong bóng OPA (nền #0068FF, chữ trắng 38 px) | Source Text gõ dần + Size theo chữ | Bong bóng giãn theo chữ. Dùng chữ dạng khung (paragraph text) rộng ~620 px để câu tự xuống dòng | H06 |
| 11,75 → 12,25 | Chip "Đã ghi vào CRM" (viền xanh, dấu tích xanh) | Scale | 0 → 110 → 100 % | H21 |
| 8,5 → 13,5 | Tiêu đề | Đổi từ ở 9,0 · 11,75 · 12,75 s | Từ cũ nhòe bay lên, từ mới nhòe đi vào trong 8 khung | H04; lần đổi 11,75 s trùng lúc chip bật |
| 13,75 → 14,25 | Khối #0068FF | Position X | Quét che, lộ cảnh C4 | H01 |

### C4 · 14–20 s · "Mọi kênh" (Omni Flash 6 s: `K02` → `K07`, chữ thêm bằng AE)

**Chữ (gợi ý, AE, dải dưới y 900–1015):** "Một OPA trực mọi kênh". Chữ trắng, 48 px, hiện từ nhòe (H03) ở 15,5 s.

```text
Flat 2D vector motion graphics, 6 seconds. Plain solid #0068FF background. Start exactly on the first frame (the large white OPA bull-head logo, centered) and end exactly on the last frame (a smaller white logo in the middle of a network of six white round icons joined by thin white lines).

[0.0-1.0s] The logo takes one calm breath.
[1.0-2.5s] The camera pulls back smoothly: the logo shrinks evenly to about 60% of its size and rises slightly, staying centered horizontally.
[1.5-3.0s] Six white round icon buttons burst outward from behind the logo one after another, clockwise, each flying along a straight line with light motion blur and settling into its place on a ring around the logo with a small overshoot.
[2.5-4.0s] Thin straight white lines draw themselves from the logo out to each icon, then around the ring from icon to icon.
[4.0-6.0s] The icons pulse gently one by one, clockwise, like messages arriving, and everything lands exactly on the last frame.

Camera: only the smooth pull-back, no rotation.
Audio: a soft whoosh for the pull-back, six light pops as the icons arrive, a gentle rising shimmer while the lines draw. No music, no voice, no animal sounds.
Brand lock: flat solid white shapes on a flat solid #0068FF background, crisp vector edges. The logo keeps the exact silhouette of the first and last frames. Icons stay simple and identical to the last frame; no photos, no faces, no text. No gradients, glow, shadows, 3D or texture. Uniform scaling only.
```

**Vì sao giao Omni:** sáu nút bay ra, đường nối tự vẽ, máy lùi là chuyển động hình khối hữu cơ, Omni làm mượt mà không cần dựng từng đường. Khung cuối `K07` ghim đúng vị trí cuối, nên mạng lưới luôn gọn. Mẫu 2 cũng không vẽ đường nối trực tiếp mà dùng video dựng sẵn (`02_Scene_Lines.mov`).

**Nối sang C5:** ở 19,75 → 20,25 s, một khối trắng quét từ trái sang (H01 bản trắng) che chỗ nối từ nền xanh sang nền trắng.

### C5 · 20–26 s · "Không bỏ sót" (Omni Flash 6 s: `K01` → `K01`, chữ thêm bằng AE)

**Chữ (gợi ý, AE, góc trên):** "Không bỏ sót *khách nào*". Hiện từ nhòe (H03) ở 20,5 s; cụm nhấn dùng Fraunces + khối đánh dấu.

Đây là KB8 rút còn 6 s và 3 bong bóng. Bong bóng chỉ bay từ trái, phải và dưới, để vùng trên trống cho chữ.

```text
Flat 2D vector motion graphics, 6 seconds: the OPA bull catches every incoming message. Plain solid white background. The first and last frames are the same centered OPA bull-head logo.

[0.0-0.75s] The logo breathes calmly once.
[0.75-4.5s] Three small, simple chat-bubble icons (flat #003C99, a rounded bubble with a little tail, no text inside) fly in one by one, one every 1.25 seconds, from the left edge, the right edge and the bottom edge, never from the top. Each flies on a smooth curved arc and falls neatly through the gap at the top of the head, between the horns, into the hollow of the U, sinks to the bottom and dissolves. Every catch makes the head give a quick, small pulse (about 4% bigger and back) and the horns tick slightly. No bubble ever misses.
[4.5-5.25s] Two small puffs of #0068FF dots burst upward from the two edges of the gap at the top of the head, like a satisfied snort, and fade quickly.
[5.25-6.0s] One calm breath, landing exactly on the last frame.

Camera: locked, no camera movement.
Audio: a soft whoosh for each bubble, a gentle pop on each catch, each pop slightly higher in pitch, a short airy nose puff on the snort. No music, no voice, no animal sounds.
Brand lock: keep the logo identical to the first and last frame — same silhouette, proportions and horn shape, flat solid #0068FF, crisp vector edges. It is a flat logo, not a character: no eyes, no mouth, no face, no extra details. No gradients, glow, shadows, 3D or text. Only the small bubbles and dots may be added, and they stay flat and simple. Uniform scaling only.
```

**Nối sang C6:** khung cuối C5 trùng khung đầu C6 (`K01`), nên cắt cứng.

### C6 · 26–32 s · "Đóng" (Omni Flash 6 s: `K01` → `K04`, chữ và nút thêm bằng AE)

Dùng nguyên prompt **KB9 cảnh C** trong `KICH-BAN-OMNI-FLASH.md`.

**Phần AE thêm dưới cụm logo:**
- 29,0 s: dòng "Đối tác vận hành AI cho đội bán hàng" (chữ đã có trong màn kết BRAND-SPEC mục 4), 48 px, đen, hiện từ nhòe (H03), tâm y ≈ 790.
- 30,0 → 30,5 s: nút CTA, chấm tròn #0068FF kéo thành viên thuốc (H07), chữ trắng "opa.business" (`links.json`), tâm y ≈ 900.
- 30,5 → 32 s: nút thở nhẹ 100 → 102 → 100 % cùng nhịp cụm logo.

## 3. Cách dựng project After Effects (học từ mẫu 1 và 2)

```
PROMO_OPA_32s (1920×1080, 30 fps, marker C1…C6)
├─ 00_DIEU_KHIEN   Null có 6 Color Control: XANH #0068FF · DEN #0A0A0A · TRANG #FFFFFF
│                  · XANH_NHAT #E6F0FF · XANH_DAM #003C99 · ALERT #E5484D
├─ 01_HOLDER       Logo_Holder (PNG logo/OPA-V4-A-Core-*-2000.png), Omni_C4, Omni_C5, Omni_C6
├─ 02_UI           PRE_BongBong_Khach, PRE_BongBong_OPA, PRE_O_Nhap, PRE_Chip, PRE_HuyHieu, PRE_NutCTA
└─ 03_CANH         C1_TinNhanDon, C2_KhachHoi, C3_OPATraLoi, C4_MoiKenh, C5_KhongBoSot, C6_Dong
```

- **Màu:** mọi Fill lấy từ lớp điều khiển, ví dụ `comp("PROMO_OPA_32s").layer("00_DIEU_KHIEN").effect("XANH")("Color")`. Đổi một chỗ là cả phim đổi, như lớp `Background Colors` của mẫu 2.
- **Font:** Be Vietnam Pro (800 tiêu đề, 500 nội dung), "Fraunces OPA" Italic 800 cho cụm nhấn. Font này đã cài trên máy theo video "OPA Agent × Pancake".
- **Mỗi thành phần giao diện là một precomp tái dùng,** như `PRE_xx_Button` của mẫu 1.

## 4. Ba expression cần dùng

**Bong bóng giãn theo chữ đang gõ (H06).** Đặt trên Source Text của lớp chữ:

```js
txt = "Dạ còn ạ! Anh chị cho OPA xin số điện thoại để giữ hàng nhé.";
n = Math.floor(linear(time, inPoint, inPoint + 1.5, 0, txt.length));
txt.substr(0, n)
```

Đặt trên Size của Rectangle Path trong lớp bong bóng:

```js
r = thisComp.layer("Chu_OPA").sourceRectAtTime(time, false);
[r.width + 64, r.height + 40]
```

Đặt trên Position của Rectangle Path, để bong bóng giãn theo đúng phía chữ chạy:

```js
r = thisComp.layer("Chu_OPA").sourceRectAtTime(time, false);
[r.left + r.width / 2, r.top + r.height / 2]
```

Lớp bong bóng phải cùng Position và Anchor Point với lớp chữ. Cách gọn nhất: parent bong bóng vào lớp chữ, rồi đặt Position của bong bóng về [0, 0].

Gõ câu bằng Unicode dựng sẵn (NFC). Nếu dấu tiếng Việt nằm thành ký tự riêng, mỗi bước gõ sẽ hiện dấu rời khỏi chữ.

**Huy hiệu đếm số (H11).** Slider Control "So" trên lớp huy hiệu; Source Text:

```js
v = Math.round(effect("So")("Slider"));
v >= 99 ? "99+" : String(v)
```

**Ba chấm "đang gõ" (H06).** Position của từng chấm; đổi `pha` thành 0, 1, 2 cho từng chấm:

```js
pha = 0;
value + [0, -6 * Math.max(0, Math.sin((time - pha * 0.12) * 10))]
```

## 5. Âm thanh

- Tắt âm của cả ba clip Omni, vì âm từng clip không khớp nhau và không khớp phần AE.
- Gắn SFX theo hành động từ thư viện `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx`:
  - bật bong bóng: pop nhẹ;
  - huy hiệu tăng: tick;
  - quét màu: whoosh;
  - gõ chữ: phím mềm;
  - sừng: "tok";
  - hơi phì: luồng hơi.
- Nhạc nền tự tổng hợp 120 BPM.
- Master −16 LUFS; bản đăng mạng xã hội −14 LUFS (BRAND-SPEC mục 9).

## 6. Việc còn chờ

- [ ] Minh duyệt lời của 6 cảnh (mục 2).
- [ ] Hùng duyệt có cho khung chat nghiêng 2.5D (C3) không.
- [ ] Tạo 3 clip Omni (C4, C5, C6) và soát theo checklist mục 10 của `KICH-BAN-OMNI-FLASH.md`.
- [ ] Nếu muốn khớp đúng easing của mẫu Envato: tải file .aep về để đọc dữ liệu thật (mục 5 của bản phân tích).
