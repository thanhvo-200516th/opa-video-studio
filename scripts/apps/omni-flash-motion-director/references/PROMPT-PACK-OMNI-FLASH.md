Ngày tạo: 23/10/2026 · **Bản 2.2**: P01 dời nhịp sớm 0,3 s, 24/10 (bản 1: `.ban1.md`; bản 2: `.ban2.md`; bản 2.1: `.ban2-1.md`)
Dùng cùng `KICH-BAN-OMNI-FLASH.md` (KB1–KB9), `KICH-BAN-PROMO-CHATBOT-OPA.md` (C1–C6) và bản phân tích 3 mẫu Envato (mã hiệu ứng H01–H21).
Trạng thái: bộ prompt sẵn để dán vào Google Flow. Chưa chạy thử trên Omni Flash; số trong prompt chưa được đo trên clip thật.

# Bộ prompt Omni Flash có thông số motion graphic · bản 2

## 0. Bản 2 thêm gì

Mỗi prompt nay có đủ **mười khối**, theo đúng thứ tự:

| Khối | Giữ cái gì | Mới ở bản 2 |
|---|---|---|
| `INPUT` | Dùng ảnh nào, theo chế độ nào (khung hay tham chiếu) | ✅ |
| `FORMAT LOCK` | Tỉ lệ, khung hình, thời lượng, một cảnh liền | ✅ |
| `BACKGROUND LOCK` | Nền đúng một màu phẳng suốt clip | ✅ |
| `COLOR` | Màu nào cho vật nào, cấm chỉnh màu | ✅ |
| `UNITS` · `LAYERS & ANCHOR POINTS` · `KEYFRAMES` | Thông số chuyển động kiểu After Effects | như bản 1 |
| `VFX` | Hiệu ứng được dùng kèm thông số; mọi thứ khác bị cấm | ✅ |
| `TIMING RATIO` · `DIRECTOR NOTE` | Tỷ lệ nhịp và ý định | như bản 1 |
| `SFX` | Danh sách âm theo mốc giây, cao độ, mức to, hướng | ✅ thay dòng AUDIO |
| `LOGO LOCK` | Hình logo không đổi | tách từ BRAND LOCK |

Thêm ảnh tham chiếu mới **T04 bảng phong cách** (`tham-chieu/T04_bang-phong-cach.png`): bảng màu và mẫu giao diện phẳng, không chữ, dùng cho các prompt dựng nền giao diện (P12, P13, P15).

> **Omni hiểu số như "lực kéo", không như lệnh chính xác.** Khung đầu và khung cuối mới ghim đúng tuyệt đối. Cách làm: tạo 2–4 bản → đo (mục 10) → sửa bằng prompt sửa có số (mục 9).

**Bài học lần chạy đầu (P01, 23/10)** — đo ở `do/OPA_logo_animation_rules_20261023170017/`:

1. **Omni vẽ chữ của prompt lên hình**: tên lớp ("HORN_L"), con số ("22.6%"), tên nốt ("C#"), đường đo kích thước. Bản 2.1 thêm vào mọi prompt câu "Everything below is invisible animation data. Never draw any of it…", và P01 đổi tên lớp sang lời thường. Nếu vẫn hiện chữ, dùng kiểu B (chỉ ý định) của P01.
2. **Omni tự thêm chữ OPA** khi prompt nói "OPA logo". Mọi prompt không cần chữ nay ghi `the bull-head mark only — no "OPA" letters`.
3. **Thời lượng do cài đặt của Flow quyết định**, không do chữ "exactly N seconds". Đặt đúng thời lượng trong Flow trước khi tạo.
4. **Khung cuối chỉ khớp khi bật chế độ khung đầu/cuối.** Lần chạy đầu, khung cuối chỉ trùng 61 %.
5. **Màu logo lệch** (18, 110, 234) và âm vỡ (+0,4 dBFS): sửa ở hậu kỳ (mục 10), đừng trông vào prompt.

**Độ dài:** mỗi prompt bản 2.1 dài 1.700–3.050 ký tự (đã đo). Nếu Flow báo quá dài, bỏ dần theo thứ tự:
1. DIRECTOR NOTE;
2. TIMING RATIO;
3. UNITS (chỉ bỏ khi đã gửi prompt khởi tạo ở mục 7).

**Không bao giờ bỏ:** INPUT, FORMAT LOCK, BACKGROUND LOCK, COLOR, KEYFRAMES, SFX, LOGO LOCK.

## 1. Quy ước thông số

### 1.1 Đơn vị

| Thuộc tính | Đơn vị trong prompt | Ghi chú |
|---|---|---|
| Thời gian | giây, `0.50s` | Mốc trên lưới 0,25 s (nửa phách 120 BPM) |
| Position | % khung, `(x%, y%)`, gốc (0, 0) góc trên trái | Không dùng px |
| Scale | % so với cỡ ở khung cuối | 100 % = đúng cỡ khung cuối |
| Rotation | độ, **dương = chiều kim đồng hồ** | Như After Effects |
| Anchor Point | tên + `(x%, y%)` của khung bao dấu | Bảng 1.2 |
| Lệch nhịp | giây, `+0.08s` | ≈ 2 khung ở 24 fps |

### 1.2 Điểm neo trên dấu đầu bò

Đo từ `logo/OPA-V4-A-Core-blue-2000.png`, theo % khung bao của dấu.

| Tên | Vị trí | Dùng cho |
|---|---|---|
| `bottom-center` | (50 %, 100 %) | Bật nảy, thở, lấy đà, lao tới |
| `horn-root-L` / `horn-root-R` | (22,6 %, 42,1 %) / (77,4 %, 42,1 %) | Xoay sừng |
| `inner-opening-center` | (50 %, 64,7 %) | Chui qua lòng O |
| `top-gap-center` | (50 %, 40,2 %) | Hứng tin nhắn |
| `top-gap-edges` | (41,1 %, 40,2 %) và (58,9 %, 40,2 %) | Hạt phì ra |

### 1.3 Vị trí dấu trong khung neo

| Khung | 16:9 | 9:16 |
|---|---|---|
| `K01`, `K02` | tâm (50 %, 50 %), cao 46,2 % H | tâm (50 %, 45,6 %), rộng 57,3 % W |
| `K04` | dấu (29,3 %, 50 %) = 64,6 % cỡ K01; cụm rộng 59,7 % W | dấu (22,5 %, 45,6 %) = 42,8 % cỡ K01; cụm rộng 79,4 % W |
| `K06` | (28 %, 50 %) | (50 %, 63,1 %) |
| `K05` | bong bóng (50 %, 50 %), rộng 21,9 % W | (50 %, 45,5 %), rộng 44,4 % W |
| `K07` | dấu (50 %, 46,3 %) = 60 % cỡ K02; vòng nút 27,1 % W × 27,8 % H | dấu (50 %, 42,7 %) = 46 % cỡ K02; vòng 33,3 % W × 24,5 % H |
| Tâm lòng O | (50 %, 56,8 %) | (50 %, 49,9 %) |
| Hai mép khe trán | (47,5 %, 45,5 %), (52,5 %, 45,5 %) | — |

### 1.4 Bảng ease

| Tên | Nghĩa trong After Effects | Cảm giác |
|---|---|---|
| `[linear]` | Không ease | Đều tuyệt đối |
| `[ease-in-out]` | Easy Ease (F9) | Vào êm, ra êm |
| `[ease-out 80%]` | Ease out, influence 80 % | Nhanh rồi đáp rất nhẹ |
| `[pop]` | Spring damping 12 (`SPRING_POP`) | Vượt ~10–12 % một nhịp rồi đứng |
| `[ease-in 90%]` | Ease in 90 % | Chậm rồi nhanh dần rất gắt |
| `[sine]` | Easy Ease liên tục | Thở, đung đưa |
| `[decay]` | Mỗi nhịp lắc = −0,5 lần nhịp trước | Lắc tắt dần |

### 1.5 Tỷ lệ chuẩn của OPA

| Động tác | Scale | Rotation | Thời lượng |
|---|---|---|---|
| Thở | 100 → 103 → 100 % | Sừng ±2° | Chu kỳ 2,5 s |
| Nhịp đập khi hứng | 100 → 104 → 100 % | Sừng ±3° | 0,25 s |
| Bật vào | 0 → 112 → 95 → 100 % | — | 0,75 s |
| Lấy đà | 100 → 96 % | −8° | 0,5 s |
| Lao tới | 96 → 100 % | +6° | 0,4 s |
| Dư âm | — | +6 → −3 → +1 → 0° | 0,85 s |
| Máy đẩy vào | 94–97 → 100 % | — | Suốt clip |

**Luật nhịp:**
- Đoạn đứng yên hoàn toàn không quá 10 % clip.
- Khung đầu trống thì đẩy máy vào suốt clip. Khung đầu có hình thì không đẩy máy, mà cho logo thở.
- **Khung chốt logo** (Minh chốt 24/10/2026): đoạn giữ logo sau khi logo đã hiện xong được miễn đo đứng yên, như khung CTA cuối của V2. P01 bản 2.2 miễn từ 1,20 s, lúc sừng vừa đứng (`do/P01.json`, khóa `exempt`). Đoạn mở đầu không được để nền trống quá 0,2 s.
- **Đo đứng yên trên clip chỉ có logo:** thước V2 tính cả các khung đổi chiều của ease (đỉnh vượt đà, đáy hụt) là "đứng", vì logo chỉ chiếm ~7 % khung. Clip giả làm đúng nhịp vẫn ra 35–49 % ở đoạn bật nảy. Với logo, xem thêm **chuỗi đứng yên dài nhất** (ngưỡng V2: ≤ 0,2 s, tức 5 khung ở 24 fps).

## 2. Luật màu

### 2.1 Bảng màu và vai trò

Chỉ dùng các màu trong BRAND-SPEC mục 1. Prompt luôn ghi **mã hex**, không ghi tên màu chung chung như "blue".

| Mã | Vai trò được phép | Không được dùng cho |
|---|---|---|
| `#0068FF` | Logo trên nền sáng; nền chính của cảnh xanh; bong bóng OPA; nút; viền 2 px của thẻ | — |
| `#FFFFFF` | Nền sáng; logo trên nền xanh; thẻ, ô nhập, nút tròn | Logo trên nền trắng |
| `#E6F0FF` | Bong bóng khách; vạch giữ chỗ; mảng phụ nhạt | Logo |
| `#003C99` | Vật nhỏ: bong bóng tin đang bay, chấm | Nền lớn, logo |
| `#0A0A0A` | Chữ (thêm trong AE); nền tối khi được yêu cầu | Logo xanh |
| `#E5484D` | **Chỉ** chấm cảnh báo nhỏ (≤ 3 % chiều cao khung) | Nền, chữ, logo, mảng lớn |

### 2.2 Luật phối

1. **Logo xanh chỉ trên nền trắng hoặc `#E6F0FF`. Logo trắng chỉ trên `#0068FF`, `#003C99` hoặc `#0A0A0A`.** Không bao giờ để logo xanh trên nền xanh.
2. **Mỗi cảnh tối đa 1 màu nền + 1 màu chính + 2 màu phụ.** Mỗi prompt liệt kê đủ trong khối COLOR; màu nào không có tên trong khối là không được xuất hiện.
3. **Không chỉnh màu:** không color grading, không phủ tông, không đổi độ sáng hay độ bão hòa, không để màu trôi dần giữa các khung. Trắng phải là trắng tuyệt đối.
4. **Không gradient, không màu chuyển.** Đổi màu chỉ bằng mép cứng (khối quét, track matte), như P11.

**Câu chuẩn trong prompt:**

```text
COLOR: <vật> #0068FF; <vật> #FFFFFF; … Only these colors. No color grading, tint, exposure change or color drift between frames; whites stay pure #FFFFFF.
```

## 3. Luật VFX

Motion graphic của OPA là **phẳng**. VFX chỉ được dùng để chuyển động dễ đọc hơn, không để trang trí.

### 3.1 Được dùng (phải ghi rõ mốc và mức)

| VFX | Thông số | Dùng ở |
|---|---|---|
| Motion blur theo hướng | Chỉ trong đoạn nhanh đã ghi mốc; shutter 180°; không có trên khung đứng | P01, P03, P07, P09, P10 |
| Zoom blur | Chỉ ở 0,8 s cuối của cú zoom xuyên; tâm blur = điểm neo zoom | P06 |
| Vẽ nét (Trim Paths) | Nét đều, đầu nét tròn, không phát sáng | P04, P10 |
| Quét phẳng (Linear Wipe) | Mép cứng, không mờ mép | P04, P11 |
| Lộ ra sau mép (Track Matte) | Mép cứng | P03, P09 |
| Biến hình (Path morph) | Một hình liền, không tan, không chớp | P05 |
| Hạt phẳng | Chấm tròn đặc `#0068FF` hoặc `#003C99`, tối đa 10 hạt mỗi cụm, tan trong 0,4 s | P08 |
| Lệch tầng (parallax) | Ba lớp xa gần chạy khác tốc độ, không mờ | P14 |

### 3.2 Bị cấm (luôn ghi trong khối VFX)

Glow, bloom, lens flare, light leak, tia sáng, chromatic aberration, film grain, nhiễu, glitch, tách RGB, bokeh, depth of field, khói, sương, lấp lánh, vệt sáng chạy qua nút (như `BTN_Shine` của mẫu 1), bóng đổ, bevel, phản chiếu, khối 3D, rung máy, vignette.

**Câu chuẩn:**

```text
VFX: allowed only — <danh sách kèm mốc>. Forbidden: glow, bloom, lens flares, light leaks, sparkles, shine sweeps, grain, noise, glitch, chromatic aberration, depth of field, smoke, shadows, bevel, reflections, 3D, camera shake, vignette.
```

## 4. Luật SFX

Omni tạo âm cùng lúc với hình. Âm phải **bám chuyển động**, đúng như cách các video OPA đã duyệt dùng âm.

### 4.1 Mười luật

1. **Mỗi âm gắn với một keyframe.** Điểm đánh của âm rơi đúng mốc giây trong KEYFRAMES, lệch tối đa 1 khung.
2. **Âm có nốt nằm trong hợp âm A trưởng (A, C#, E)**, khớp bộ SFX đã duyệt. Ví dụ: `pop-bubble-low-A4`, `pop-bubble-mid-C#5`, `pop-bubble-high-E5`, `tick-catch-a4`, `ping-a3`.
3. **Chuỗi âm lặp thì nốt đi lên:** A4 → C#5 → E5 → A5…, như tiếng hứng tin của phim "Thủ môn".
4. **Ba mức to:** strong (0 dB, âm chính), medium (−6 dB, âm phụ), soft (−12 dB, âm nền). Mỗi thời điểm chỉ một âm strong.
5. **Hướng âm theo vị trí vật:** vật bên trái kêu bên trái, vật chạy ngang thì âm chạy theo.
6. **Whoosh dài đúng bằng cú di chuyển** và to nhất lúc vật nhanh nhất.
7. **Giữa các âm là im lặng:** không tiếng ù, không tiếng phòng, không đuôi vang dài quá 0,5 s.
8. **Bò "nói" bằng:** hơi mũi phì, sừng gõ "tok" (gỗ khô), thân đáp trầm. **Không** tiếng bò kêu.
9. **Cấm:** nhạc, giọng nói, tiếng người, tiếng động vật, tiếng còi, tiếng glitch hay nhiễu số, nhạc có bản quyền.
10. **Âm của Omni là bản nháp.** Khi đưa vào phim, thay bằng file thư viện (bảng 4.2) rồi master −16 LUFS; bản đăng mạng xã hội −14 LUFS (BRAND-SPEC mục 9).

### 4.2 Từ điển âm → file đã duyệt

| Loại âm (viết trong prompt) | Khi nào | File thay trong After Effects |
|---|---|---|
| `soft bubbly pop` (có nốt) | Bong bóng, nút, nút mạng lưới bật | `ae/opa-agent/assets/sfx/pop-bubble-low-A4.wav`, `pop-bubble-mid-C#5.wav`, `pop-bubble-high-E5.wav` |
| `dry wooden tok` (có nốt) | Sừng khớp, chữ cái đáp | `ae/opa-agent/assets/sfx/ui-wood-marimba-tick.wav` |
| `bright catch pop` (có nốt) | Tin lọt khe | `sfx/03-pops-snaps-elastic/catch-bright-ring.wav` (đổi cao độ theo A trưởng), `ae/opa-agent/assets/sfx/tick-catch-a4.wav` |
| `soft low thump` | Thân đáp, dừng gắt | `ae/opa-agent/assets/sfx/thump-body-punch.wav` |
| `airy whoosh` | Di chuyển, quét màu | `ae/opa-agent/assets/sfx/whoosh-cut-light.wav`, `whoosh-cut-medium.wav`, `whoosh-light-airy.wav` |
| `deep wind-up whoosh` | Lấy đà, hít vào | `ae/opa-agent/assets/sfx/whoosh-deep-windup.wav` |
| `airy nose puff` | Bò phì hơi | `sfx/07-textures-drones-foley/foley-snort-puff.wav` |
| `tiny UI tick` (có nốt) | Huy hiệu, nhịp đập, con trỏ | `ae/opa-agent/assets/sfx/ui-tick-crisp-A6.wav`, `ui-tick-crisp-E6.wav` |
| `soft expand swipe` | Ô nhập kéo dài, biến hình | `ae/opa-agent/assets/sfx/uisfx-glass-expand+155c.wav` |
| `soft typing blips` | Gõ chữ, ba chấm | `ae/opa-agent/assets/sfx/uisfx-minimal-typing.wav` |
| `soft notification ping` | Tin tới | `ae/opa-agent/assets/sfx/ping-a3.wav`, `ping-e4.wav` |
| `soft low whump` | Kết cú zoom xuyên | `sfx/02-impacts-hits/impact-deep-logo.wav` (mức medium) |

Các file trong `ae/opa-agent/assets/sfx/` là bộ đã dùng trong video "OPA Agent × Pancake" v09, Minh duyệt âm ngày 22/10/2026. Các file trong `sfx/` lấy từ cue sheet âm thư viện của phim "Thủ môn" bản 2.

**Mẫu khối SFX:**

```text
SFX (each sound lands exactly on its keyframe; pitched sounds in A major — A, C#, E; levels: strong 0 dB, medium −6 dB, soft −12 dB; silence between cues; no music, voice, animal sounds or long reverb):
- 0.50s soft bubbly pop, A4, strong, center
- …
```

## 5. Ảnh tham chiếu và chế độ đầu vào

### 5.1 Ba chế độ

| Chế độ | Đưa vào | Khi nào dùng | Giới hạn |
|---|---|---|---|
| **A · Khung đầu + cuối** | 2 ảnh `K0x` | Logo phải đúng ở đầu và cuối (hiện logo, chuyển cảnh, nối clip) | Theo tài liệu API, không kèm được ảnh tham chiếu |
| **A1 · Chỉ khung đầu** | 1 ảnh `K0x` | Bắt đầu từ logo đúng, kết mở | Như trên |
| **B · Ảnh tham chiếu** | 1–3 ảnh `T0x` | Cảnh tự do không có khung cuối nhưng cần đúng logo hoặc đúng phong cách | Không ghim bố cục; nền và khung giữ bằng chữ |

Bản API của Omni 1.1 không cho dùng khung và ảnh tham chiếu trong cùng một lần tạo. Giao diện Flow có thể khác; nếu Flow cho đưa cả hai, vẫn ưu tiên chế độ A cho cảnh logo.

### 5.2 Ảnh tham chiếu có sẵn

| File | Nội dung | Gọi trong prompt là |
|---|---|---|
| `T01_dau-bo-xanh_nen-trang.png` | Dấu xanh trên nền trắng | `reference image N — the OPA bull-head logo (blue on white)` |
| `T02_logo-chu-xanh_nen-trang.png` | Dấu + chữ OPA | `reference image N — the OPA lockup` |
| `T03_dau-bo-trang_nen-xanh.png` | Dấu trắng trên nền xanh | `reference image N — the OPA bull-head logo (white on blue)` |
| `T04_bang-phong-cach.png` | Bảng màu + bong bóng, thẻ, nút, ô nhập phẳng | `reference image N — the OPA style board` |

### 5.3 Năm luật dùng tham chiếu

1. **Đưa ảnh theo đúng thứ tự gọi trong prompt.** Thứ tự ảnh là tín hiệu model đọc.
2. **Nói rõ vai trò từng ảnh:**
   - ảnh logo: `keep it identical wherever it appears`;
   - ảnh phong cách: `match its colors, outline weight, corner roundness and flat shapes; do not copy its layout`.
3. **Kết bằng câu ghim:** `Keep the logo identical to reference image 1.`
4. **Không đưa ảnh có chữ** ngoài T02. Không đưa ảnh hoặc video của mẫu Envato (giấy phép).
5. Nếu Flow hiện thẻ tên cho ảnh (ví dụ `@image1`), thay chữ `reference image 1` bằng thẻ đó.

## 6. Giữ nguyên định dạng và giữ nguyên nền

### 6.1 FORMAT LOCK

Giữ đúng tỉ lệ đã chọn trong Flow, tràn khung. Cấm:
- viền đen, letterbox, khung viền, góc bo;
- chia đôi màn hình, cảnh lồng cảnh;
- chữ, phụ đề, watermark, giao diện máy;
- cắt cảnh, chuyển cảnh lạ;
- quay chậm, tăng giảm tốc, dừng hình (trừ khi KEYFRAMES ghi);
- phóng hay cắt mép của khung đầu, khung cuối (bố cục hai khung đó phải trùng từng vị trí).

```text
FORMAT LOCK: <16:9 | 9:16>, full frame, exactly <N> seconds, one continuous shot. Keep the exact framing of the given frames — no crop, reframing, black bars, borders, split screen, captions, watermark, cuts, slow motion, speed ramps or freeze frames.
```

### 6.2 BACKGROUND LOCK

Nền là **một màu phẳng đúng mã hex, suốt mọi khung**. Cấm:
- gradient, hoa văn, chất liệu, nhiễu, vignette;
- ánh sáng thay đổi, bóng đổ lên nền;
- sàn, đường chân trời, tường, phòng, bầu trời;
- vật trang trí hay hạt bay ở nền;
- máy di chuyển làm lộ nền mới.

Chỉ được đổi màu nền khi KEYFRAMES ghi rõ (P06 kết bằng màu nền cũ; P11 đổi bằng khối quét).

```text
BACKGROUND LOCK: solid <#FFFFFF | #0068FF> in every frame — no gradient, texture, noise, vignette, light change, shadows, floor, horizon, room, sky, decoration or background particles. Camera moves never reveal anything new behind.
```

**Khi sửa bằng hội thoại**, câu mở đầu luôn nhắc giữ cả hai:

```text
Keep everything else exactly the same — same format and framing, same background, same colors, same timing and same sound. Only …
```

## 7. Prompt khởi tạo phiên (Agent của Flow)

Dán một lần khi mở project. Các prompt sau vẫn giữ đủ khối khóa, vì chưa kiểm được Agent nhớ quy ước qua nhiều lượt.

```text
You are my motion designer for OPA logo animations in this project. Apply these rules to every request.

UNITS: seconds; positions in % of the frame, (0%,0%) = top-left; scale in % of the last-frame size; rotation in degrees, positive = clockwise.
ANCHORS on the OPA bull-head (in % of its bounding box): bottom-center (50%,100%); horn roots (22.6%,42.1%) and (77.4%,42.1%); inner opening center (50%,64.7%); top gap center (50%,40.2%).
EASING: linear; ease-in-out; ease-out 80%; pop (one ~12% overshoot); ease-in 90%; sine; decay (each swing half the previous).
COLOR: only #0068FF, #FFFFFF, #E6F0FF, #003C99, #0A0A0A, and #E5484D for tiny alert dots only. Blue logo only on white or #E6F0FF; white logo only on #0068FF, #003C99 or #0A0A0A. No gradients, grading, tint or color drift.
FORMAT: keep the chosen aspect ratio, full frame, one continuous shot; no crop, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND: one flat solid color in every frame; nothing appears behind; no light change.
VFX: only motion blur, zoom blur, line draw, hard-edged wipes, track-matte reveals, shape morphs and flat dot particles when I list them. Never glow, flares, sparkles, shine sweeps, grain, glitch, depth of field, smoke, shadows, 3D or camera shake.
SFX: every sound lands on a keyframe; pitched sounds in A major (A, C#, E), rising when repeated; levels strong 0 dB / medium −6 dB / soft −12 dB; silence between cues; the bull speaks only with nose puffs, wooden "tok" horn clicks and soft low thumps. Never music, voice, animal sounds or long reverb.
REFERENCES: when I attach reference images, keep any logo identical to them and use the style board only for look, not layout.
NEVER DRAW THE DATA: my prompts contain timings, names, numbers and notes as invisible instructions; never show labels, numbers, guides, diagrams or any text on screen unless I ask for on-screen text.
LOGO: the bull-head is a flat logo, not a character — never add eyes, mouth, face, limbs or details; uniform scaling only.
PRIORITY when something conflicts: 1) logo, color and background locks, 2) exact first and last frames, 3) timing and sound sync, 4) exact values.

Reply only "OK" and wait for my first shot.
```

## 8. Mười lăm prompt

| # | Tên | Chế độ | Đầu vào | Nền | Dài |
|---|---|---|---|---|---|
| P01 | Bật nảy | A | K00 → K01 | trắng | 5 s |
| P02 | Thở lặp | A | K01 → K01 | trắng | 5 s |
| P03 | Lắp ráp + chữ | A | K00 → K04 | trắng | 6 s |
| P04 | Vẽ nét, đổ màu | A | K00 → K01 | trắng | 5 s |
| P05 | Bong bóng hóa đầu bò | A | K05 → K01 | trắng | 6 s |
| P06 | Chui qua lòng O | A | K02 → K03 | xanh | 4 s |
| P07 | Lao tới | A | K06 → K01 | trắng | 4 s |
| P08 | Hứng tin nhắn | A | K01 → K01 | trắng | 8 s |
| P09 | Đóng logo | A | K01 → K04 | trắng | 6 s |
| P10 | Mạng lưới kênh | A | K02 → K07 | xanh | 6 s |
| P11 | Quét màu đảo nền | A | K01 → K02 | trắng → xanh | 3 s |
| P12 | Thông báo dồn (nền cho AE) | B | T04 | trắng | 5 s |
| P13 | Ô nhập kéo dài (nền cho AE) | B | T04 | xanh | 4 s |
| P14 | Zoom ra thành tường thẻ chat | A1 | K01 | trắng | 6 s |
| P15 | Điện thoại trồi lên | B | T03 + T04 | xanh | 5 s |

Prompt viết cho 16:9. Làm bản 9:16 thì đổi `16:9` trong FORMAT LOCK và thay vị trí theo cột 9:16 của bảng 1.3.

---

### P01 · Bật nảy · A · K00 → K01 · 5 s · bản 2.2

Bản 2.2 (Minh chốt 24/10): **dời cả nhịp sớm 0,3 s**. Đầu bò bật từ 0,20 s, bỏ 0,5 s nền trắng chết ở đầu. Khung chốt bắt đầu lúc sừng phải vừa đứng (1,20 s).

Bản 2.1 (23/10, sau lần chạy đầu): Omni vẽ cả tên lớp, con số, tên nốt lên hình; tự thêm chữ OPA; diễn thêm sau 6 s. Đo và kết luận: `do/OPA_logo_animation_rules_20261023170017/KET-LUAN-VA-PROMPT-SUA.md`.

Trong Flow:
- đặt thời lượng **5 s** trong phần cài đặt;
- bật chế độ khung đầu `K00`, khung cuối `K01`;
- không gắn ảnh tham chiếu.

Thử kiểu A trước; nếu vẫn hiện chữ thì dùng kiểu B.

**Kiểu A: có thông số**

```text
OPA logo animation — flat 2D vector motion graphics.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first frame = empty white (given); last frame = the OPA bull-head mark alone, centered (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 5 seconds, one continuous shot. Keep the exact framing of the given frames — no crop, reframing, bars, borders, captions, watermark, cuts, slow motion or speed ramps.
BACKGROUND LOCK: solid #FFFFFF in every frame — no gradient, texture, vignette, light change, shadows, faint text, scribbles, ghost shapes, ripples or background objects.
COLOR: the mark is solid #0068FF, exactly as in the last frame. No grading, tint or color drift.
MOTION (seconds; scale in % of the last-frame size; rotation positive = clockwise):
- The head starts popping almost immediately, from a single point at its bottom-center: 0.20s 0% → 0.60s 112% (fast ease-out) → 0.80s 95% → 0.95s 100%. Its bottom edge stays planted.
- The left horn grows from its root where it joins the head and swings up: 0.45s −40° → 0.95s +6° → 1.10s 0°. The right horn mirrors it, 0.08s later.
- The whole frame pushes in very slowly and steadily: 0.00s 97% → 5.00s 100%.
- After 1.20s nothing else animates: no second pop, no pulse, no ripple, no re-scaling — only the slow push continues.
VFX: light motion blur only during the fast pop (0.20–0.60s) and the horn swing (0.45–0.95s). Nothing else: no glow, flares, sparkles, grain, glitch, shadows, 3D or camera shake.
SOUND (audio only, never shown): exactly three sounds and silence everywhere else — a soft bubbly pop at 0.20s; a dry wooden click at 0.95s; a second, slightly higher wooden click at 1.03s. Both clicks tuned to an A major chord. Gentle levels, no clipping, no music, no voice, no animal sounds, no extra hits or swells.
LOGO LOCK: the bull-head mark only — no "OPA" letters, no wordmark, no text. Identical to the last frame: same silhouette, proportions and horn shape, crisp edges. A flat logo, not a character: no eyes, mouth or face. Uniform scaling only.
```

**Kiểu B: chỉ ý định**

```text
A clean, premium flat 2D logo reveal on a plain pure white background, 5 seconds, one continuous shot, 16:9. Start on the given empty white frame and end exactly on the given last frame: the blue OPA bull-head mark alone in the center.
Almost immediately — a fifth of a second in — the U-shaped head pops up from a tiny point at its base, overshoots a little and settles with one tight bounce, its base staying planted. Right after, the two horns sprout from their roots and swing up into place, the left one a moment before the right, each with a small overshoot. Then the frame keeps a very slow, steady push-in until the end; nothing else moves.
Flat solid #0068FF on pure white. No text, letters, numbers, labels, guides or diagrams anywhere; no "OPA" wordmark. No gradients, glow, shadows, sparkles, ripples, ghost shapes or 3D. Never squash or stretch the mark; it is a flat logo, not a character.
Sound: one soft bubbly pop when the head appears, then two dry wooden clicks as the horns lock, the second slightly higher; silence otherwise. No music, voice or animal sounds.
```

**Đọc nhanh:** đầu chữ U bật từ điểm đáy ngay từ 0,2 s (đáy đứng yên), vượt 112 % rồi hụt 95 % rồi đứng lúc 0,95 s. Sừng xoay quanh gốc từ −40° về 0°, sừng phải trễ 0,08 s, đứng hẳn lúc 1,18 s. Từ 1,2 s chỉ còn máy đẩy chậm. Đúng ba âm: 0,20 · 0,95 · 1,03 s.

**Khung chốt:** từ 1,20 s đến hết là khung chốt logo, miễn đo đứng yên (Minh chốt 24/10/2026). Thông số đo ở `do/P01.json`. Thử trên clip giả đúng nhịp này: ngoài khung chốt, chuỗi đứng dài nhất 5 khung (0,21 s), đạt ngưỡng V2.

**Tỷ lệ nhịp:** chờ 4 % · bật nảy và sừng 20 % · khung chốt 76 %.

---

### P02 · Thở lặp · A · K01 → K01 · 5 s

```text
OPA logo animation — seamless loop, flat 2D vector motion graphics.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first and last frames = the same OPA bull-head logo centered at (50%,50%) (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 5 seconds, one continuous shot that loops perfectly. No crop, reframing, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #FFFFFF in every frame — no gradient, texture, vignette, light change, shadows or background objects.
COLOR: logo #0068FF only. No grading, tint or color drift.
UNITS: seconds; scale in % of the last-frame size; rotation in degrees, positive = clockwise.
LAYERS & ANCHOR POINTS: LOGO = whole bull-head, anchor bottom-center (50%,100% of its box). HORN_L, HORN_R, anchor at each horn's root.
KEYFRAMES:
- LOGO scale: 0.00s 100% → 1.25s 103% → 2.50s 100% → 3.75s 103% → 5.00s 100% [sine].
- HORN_L rotation: 0° → 1.25s −2° → 2.50s 0° → 3.75s −2° → 5.00s 0° [sine]; HORN_R mirrored (+2°).
- Camera locked.
VFX: none. Forbidden: glow, flares, sparkles, grain, glitch, depth of field, shadows, 3D, camera shake, vignette.
TIMING RATIO: inhale 50% · exhale 50%, two identical cycles; nothing ever stops.
DIRECTOR NOTE: A calm, strong breath — the logo swells gently from its base and the horns open slightly on each inhale, even like a resting heartbeat.
SFX (no music, voice or animal sounds; the sound at 5.00s matches 0.00s so the loop is seamless):
- 0.00–1.25s and 2.50–3.75s very soft low inhale of air, soft, center
- 1.25–2.50s and 3.75–5.00s near silence
LOGO LOCK: the bull-head mark only — no "OPA" letters, no wordmark, no text. Identical to the first and last frame — same silhouette, proportions and horn shape. A flat logo, not a character: no eyes, mouth, face or extra details. Uniform scaling only.
```

---

### P03 · Lắp ráp + chữ OPA · A · K00 → K04 · 6 s

```text
OPA logo animation — flat 2D vector motion graphics.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first frame = empty white (given); last frame = the OPA lockup: bull-head mark centered at (29.3%,50%) with the "OPA" wordmark to its right (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 6 seconds, one continuous shot. Keep the exact framing of the last frame — no crop, reframing, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #FFFFFF in every frame — no gradient, texture, vignette, light change, shadows or background objects.
COLOR: mark and wordmark #0068FF only. No grading, tint or color drift.
UNITS: seconds; positions in % of frame; scale in % of the last-frame size; rotation in degrees, positive = clockwise.
LAYERS & ANCHOR POINTS: HEAD = U-shaped head of the mark, anchor bottom-center. HORNS = both horns, anchor at each root. LETTER_O, LETTER_P, LETTER_A = wordmark letters, hidden behind an invisible vertical edge at the right side of the mark (track matte). CAMERA = whole frame.
KEYFRAMES:
- HEAD position y: 0.50s below the frame (y 120%) → 1.00s final place [ease-out 80%].
- HORNS position y: 1.00s above the frame (y −20%) → 1.50s final place [ease-in, hard stop]; rotation 1.00s ±20° → 1.50s 0°.
- HEAD scale: 1.50s 100% → 1.62s 97% → 1.75s 100% (impact dip).
- LETTER_O x: 1.75s hidden → 2.25s final [ease-out 80%]; LETTER_P +0.12s; LETTER_A +0.25s. Letters only slide, never change shape.
- CAMERA scale: 0.00s 96% → 6.00s 100% [linear].
VFX: allowed only — vertical motion blur on HEAD 0.50–1.00s and HORNS 1.00–1.50s; hard-edged track-matte reveal for the letters. Forbidden: glow, flares, sparkles, shine sweeps, grain, glitch, depth of field, smoke, shadows, 3D, camera shake, vignette.
TIMING RATIO: wait 8% · build 17% · letters 17% · slow push 58%.
DIRECTOR NOTE: Parts snapping together — the head rises, the horns drop and lock with a firm click, the head absorbs the impact, then the letters glide out from behind the mark.
SFX (each sound on its keyframe; pitched sounds in A major; strong 0 dB, medium −6 dB, soft −12 dB; silence between cues; no music, voice or animal sounds):
- 0.50–1.00s quick rising swoosh, medium, bottom to center
- 1.50s dry wooden tok (both horns together), A4, strong, center-left
- 1.55s soft low thump, medium
- 2.25s, 2.37s, 2.50s tiny UI ticks for O, P, A, notes A5, C#6, E6, soft, panning left to right
LOGO LOCK: mark and wordmark identical to the last frame — same shapes, spacing and proportions. No other text or letters. No eyes, face or extra details. Uniform scaling only.
```

---

### P04 · Vẽ nét rồi đổ màu · A · K00 → K01 · 5 s

```text
OPA logo animation — "draw-on" style, flat 2D vector motion graphics.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first frame = empty white (given); last frame = the OPA bull-head logo centered at (50%,50%) (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 5 seconds, one continuous shot. No crop, reframing, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #FFFFFF in every frame — no paper texture, gradient, vignette, light change, shadows or background objects.
COLOR: outline and fills #0068FF only. No grading, tint or color drift.
UNITS: seconds; scale in % of the last-frame size.
LAYERS & ANCHOR POINTS: OUTLINE = thin stroke along the logo silhouette, 0.8% of the frame height thick, starting at the bottom-center. HEAD_FILL = fill of the U-shaped head, wiped bottom to top. HORN_FILL = fill of each horn, wiped root to tip. CAMERA = whole frame.
KEYFRAMES:
- OUTLINE trim: 0.25s 0% → 1.50s 100%, growing from the bottom-center in both directions at the same speed [ease-in-out].
- HEAD_FILL wipe: 1.25s 0% → 2.00s 100% [ease-in-out].
- HORN_FILL wipe: 1.75s 0% → 2.50s 100% [ease-out 80%].
- OUTLINE merges into the fill at 2.50s.
- CAMERA scale: 0.00s 94% → 5.00s 100% [linear].
VFX: allowed only — line draw (round caps, even width) and hard-edged flat wipes. Forbidden: glow, liquid, paint texture, brush strokes, sparkles, grain, glitch, depth of field, shadows, 3D, camera shake, vignette.
TIMING RATIO: wait 5% · draw 25% · fill 20% · slow push 50%.
DIRECTOR NOTE: A designer drawing the mark live — a clean line traces the shape, flat blue fills it from the bottom up, the horns fill last.
SFX (each sound on its keyframe; pitched sounds in A major; strong 0 dB, medium −6 dB, soft −12 dB; silence between cues; no music, voice or animal sounds):
- 0.25–1.50s light pencil-like scratch following the line, soft, panning with the line
- 1.25–2.00s soft rising whoosh, medium
- 2.50s dry wooden tok, A4, strong, center
LOGO LOCK: the bull-head mark only — no "OPA" letters, no wordmark, no text. Identical to the last frame — same silhouette, proportions and horn shape, crisp edges. A flat logo, not a character: no eyes, mouth, face or extra details.
```

---

### P05 · Bong bóng chat hóa đầu bò · A · K05 → K01 · 6 s

```text
OPA logo animation — flat 2D vector motion graphics: a chat message becomes the logo.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first frame = a #0068FF chat bubble with three white dots, centered (given); last frame = the OPA bull-head logo, centered (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 6 seconds, one continuous shot. No crop, reframing, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #FFFFFF in every frame — no gradient, texture, vignette, light change, shadows or background objects.
COLOR: bubble, head and horns #0068FF; dots #FFFFFF. Only these colors. No grading, tint or color drift.
UNITS: seconds; positions in % of frame; scale in % of the last-frame size; rotation in degrees, positive = clockwise.
LAYERS & ANCHOR POINTS: DOT_1–3, anchor each dot's center. BUBBLE = bubble with its tail, anchor bubble center. HEAD = U-shaped head the bubble becomes, anchor bottom-center. HORN_L, HORN_R, anchor at each root.
KEYFRAMES:
- DOTS y: 0.00–1.00s each bounces up 1.5% of the frame height and back, in a wave, 0.12s apart [sine].
- BUBBLE scale: 1.00s 100% → 1.25s 92% [ease-in-out] (anticipation).
- BUBBLE → HEAD morph: 1.25s → 2.50s, one continuous shape, the tail retracts [ease-in-out].
- DOTS: 1.25s slide to the center → 1.75s drop into the hollow of the U and vanish [ease-in].
- HORN_L: 2.25s scale 0%, rotation −30° → 2.75s +5° → 3.00s 0° [pop]; HORN_R mirrored.
- LOGO scale: 3.00s 100% → 3.75s 102% → 4.50s 100% → 5.25s 102% → 6.00s 100% [sine], anchor bottom-center.
- Camera locked.
VFX: allowed only — one continuous shape morph (no cut, flash or dissolve) and light motion blur on the horns 2.25–2.75s. Forbidden: glow, sparkles, particles, grain, glitch, depth of field, shadows, 3D, camera shake, vignette.
TIMING RATIO: typing 17% · anticipation 4% · morph 29% · settle with breaths 50%.
DIRECTOR NOTE: The typing dots bounce, the bubble gathers itself, then reshapes into the bull's head and sprouts its horns — a customer message turning into OPA.
SFX (each sound on its keyframe; pitched sounds in A major; strong 0 dB, medium −6 dB, soft −12 dB; silence between cues; no music, voice or animal sounds):
- 0.00–1.00s soft typing blips on each dot bounce, A5, C#6, E6, soft
- 1.00s small deep wind-up whoosh, soft
- 1.25–2.50s soft expand swipe following the morph, medium
- 1.75s tiny drop pop as the dots fall in, A4, soft
- 2.75s dry wooden tok, E5, strong, center
LOGO LOCK: the bull-head mark only — no "OPA" letters, no wordmark, no text. The final logo identical to the last frame — same silhouette, proportions and horn shape, crisp edges. A flat logo, not a character: no eyes, mouth, face or extra details. Uniform scaling only.
```

---

### P06 · Chui qua lòng chữ O · A · K02 → K03 · 4 s

```text
OPA logo transition — flat 2D vector motion graphics.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first frame = the white OPA bull-head logo centered on #0068FF (given); last frame = completely plain #0068FF (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 4 seconds, one continuous shot. No crop of the first frame, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #0068FF in every frame, including the final second — no gradient, vignette, light change, flash or background objects.
COLOR: logo #FFFFFF on #0068FF. Only these two colors. No grading, tint or color drift.
UNITS: seconds; scale in % of the first-frame size.
LAYERS & ANCHOR POINTS: LOGO = the white bull-head. ANCHOR = the center of its inner opening (the hollow inside the U), (50%,64.7%) of the logo box = (50%,56.8%) of the frame. All scaling happens around this point, so the camera dives into the hollow, not into the forehead.
KEYFRAMES:
- LOGO scale: 0.00s 100% → 0.75s 95% [ease-in-out] (pull back).
- LOGO scale: 0.75s 95% → 3.00s 2500% [ease-in 90%: slow, then sharply accelerating].
- 3.00–4.00s plain #0068FF, perfectly still.
VFX: allowed only — zoom blur centered on the anchor from 2.20s to 3.00s. Forbidden: glow, white flash, flares, sparkles, grain, glitch, depth of field, shadows, 3D, camera shake, vignette.
TIMING RATIO: breath 19% · dive 56% · blue 25%.
DIRECTOR NOTE: A short breath back, then a dive straight through the hollow of the U; the white walls rush past the frame edges until only the blue inside remains.
SFX (each sound on its keyframe; strong 0 dB, medium −6 dB, soft −12 dB; silence between cues; no music, voice or animal sounds):
- 0.00–0.75s deep wind-up whoosh, soft
- 0.75–3.00s airy whoosh rising with the zoom from soft to strong, center
- 3.00s soft low whump, medium
- 3.00–4.00s silence
LOGO LOCK: the bull-head mark only — no "OPA" letters, no wordmark, no text. The same silhouette in every frame until it leaves the screen. A flat logo, not a character: no eyes, face or extra details. Uniform scaling only.
```

---

### P07 · Lao tới · A · K06 → K01 · 4 s

```text
OPA logo animation — flat 2D vector motion graphics; the logo acts with posture only.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first frame = the logo at (28%,50%) (given); last frame = the same logo centered at (50%,50%), same size (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 4 seconds, one continuous shot. Camera locked; no crop, reframing, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #FFFFFF in every frame — no floor, ground line, dust, shadows, gradient, vignette or background objects.
COLOR: logo #0068FF only. No grading, tint or color drift.
UNITS: seconds; positions in % of frame; scale in % of the last-frame size; rotation in degrees, positive = clockwise.
LAYERS & ANCHOR POINTS: LOGO = whole bull-head, anchor bottom-center (50%,100% of its box); all rotation pivots here. HORNS, anchor at each root; they follow the LOGO 0.08s late (overlap).
KEYFRAMES:
- LOGO scale: 0.00s 100% → 0.25s 101.5% → 0.50s 100% [sine].
- ANTICIPATION 0.50s → 1.00s [ease-in-out]: rotation 0° → −8°; position x 28% → 26%; scale 100% → 96%.
- CHARGE 1.00s → 1.40s [ease-out 80%]: position x 26% → 50%; rotation −8° → +6°; scale 96% → 100%.
- FOLLOW-THROUGH 1.40s → 2.25s [decay]: rotation +6° → −3° (1.60s) → +1° (1.80s) → 0° (2.25s).
- SETTLE: scale 2.25s 100% → 3.10s 102% → 4.00s 100% [sine].
VFX: allowed only — strong horizontal motion blur 1.00–1.40s. Forbidden: speed lines, dust, impact flash, glow, sparkles, grain, glitch, depth of field, shadows, 3D, camera shake, vignette.
TIMING RATIO: breath 12% · anticipation 13% · charge 10% · follow-through 21% · settle 44%.
DIRECTOR NOTE: A determined bull told only through posture — it leans back gathering power, dashes to the center, stops hard, rocks twice and stands firm.
SFX (each sound on its keyframe; pitched sounds in A major; strong 0 dB, medium −6 dB, soft −12 dB; silence between cues; no music, voice, mooing or other animal sounds):
- 0.50s airy nose puff, medium, left
- 0.50–1.00s deep wind-up whoosh, soft, left
- 1.00–1.40s fast whoosh, strong, panning left to center
- 1.40s soft low thump, strong, center
- 1.48s dry wooden tok, A4, medium, center
LOGO LOCK: the bull-head mark only — no "OPA" letters, no wordmark, no text. Identical to the last frame — same silhouette, proportions and horn shape. A flat logo, not a character: no eyes, mouth, face, legs or extra details. Uniform scaling only, never squash or stretch.
```

**Bản 9:16:** dấu từ (50 %, 63,1 %) lao lên (50 %, 45,6 %). Đổi `position x 28% → 26%` thành `position y 63.1% → 64.5%`, `position x 26% → 50%` thành `position y 64.5% → 45.6%`, `horizontal` thành `vertical`, `left` thành `bottom` trong SFX.

---

### P08 · Hứng tin nhắn · A · K01 → K01 · 8 s

```text
OPA logo animation — flat 2D vector motion graphics: the bull catches every message.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first and last frames = the same OPA bull-head logo centered at (50%,50%) (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 8 seconds, one continuous shot. Camera locked; no crop, reframing, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #FFFFFF in every frame — no gradient, texture, vignette, light change, shadows or background objects; only the listed bubbles and dots move.
COLOR: logo #0068FF; bubbles #003C99; puff dots #0068FF. Only these colors. No grading, tint or color drift.
UNITS: seconds; positions in % of frame; scale in % of the last-frame size; rotation in degrees, positive = clockwise.
LAYERS & ANCHOR POINTS: LOGO, anchor bottom-center. HORNS, anchor at each root. BUBBLE_1–5 = small flat chat-bubble icons (rounded, with a tail, no text), 4% of the frame width, auto-oriented along their paths. GAP = top gap between the horns at (50%,45.5%). PUFFS = dots from the gap edges (47.5%,45.5%) and (52.5%,45.5%).
KEYFRAMES:
- LOGO scale: 0.00s 100% → 0.50s 102% → 1.00s 100% [sine].
- BUBBLE_n launch at 1.00s, 2.00s, 3.00s, 4.00s, 5.00s from the left, right, bottom, left and right edges, each on a curved arc, reaching GAP 0.75s after launch [ease-in], then sinking into the hollow and dissolving.
- Each catch (1.75s, 2.75s, 3.75s, 4.75s, 5.75s): LOGO scale 100% → 104% → 100% in 0.25s [pop]; HORNS ±3° → 0° [decay].
- PUFFS: 6.00s two puffs rise 5% of the frame height, gone by 6.40s.
- LOGO scale: 7.00s 100% → 7.50s 102% → 8.00s 100% [sine].
VFX: allowed only — light motion blur on the flying bubbles; flat solid dot particles for PUFFS (at most 10 dots per puff, no glow). Forbidden: glow, sparkles, stars, trails, grain, glitch, depth of field, shadows, 3D, camera shake, vignette.
TIMING RATIO: breath 12% · five catches on the beat 63% · snort 12% · breath 13%.
DIRECTOR NOTE: Messages arrive one per second like a steady beat and every one lands inside the bull's head — none is missed. The snort at the end says "done".
SFX (each sound on its keyframe; pitched sounds in A major, rising; strong 0 dB, medium −6 dB, soft −12 dB; silence between cues; no music, voice or animal sounds):
- each launch: soft airy whoosh, soft, panned from the bubble's side
- catches 1.75s, 2.75s, 3.75s, 4.75s, 5.75s: bright catch pop on A4, C#5, E5, A5, C#6, medium, center
- 6.00s airy nose puff, strong, center
LOGO LOCK: the bull-head mark only — no "OPA" letters, no wordmark, no text. Identical to the first and last frame — same silhouette, proportions and horn shape. A flat logo, not a character: no eyes, mouth, face or extra details. Uniform scaling only.
```

**Bản 6 s cho promo C5:** 3 bong bóng phóng ở 0,75 s · 2,0 s · 3,25 s, chỉ từ trái, phải, dưới; hứng ở 1,5 s · 2,75 s · 4,0 s (A4, C#5, E5); PUFFS ở 4,5 s; thở 5,25–6,0 s.

---

### P09 · Đóng logo · A · K01 → K04 · 6 s

```text
OPA logo animation — flat 2D vector motion graphics.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first frame = the bull-head mark centered at (50%,50%), 46% of the frame height (given); last frame = the OPA lockup: the mark at (29.3%,50%) at 64.6% of its first size, with the "OPA" wordmark to its right (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 6 seconds, one continuous shot. Keep the exact framing of both given frames — no crop, reframing, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #FFFFFF in every frame — no gradient, texture, vignette, light change, shadows or background objects.
COLOR: mark and wordmark #0068FF only. No grading, tint or color drift.
UNITS: seconds; positions in % of frame; scale in % of the first-frame mark size.
LAYERS & ANCHOR POINTS: MARK = bull-head, anchor its box center. LETTER_O, LETTER_P, LETTER_A, hidden behind an invisible vertical edge at the right side of the mark (track matte). LOCKUP = mark + wordmark, anchor lockup center.
KEYFRAMES:
- MARK scale: 0.00s 100% → 0.25s 101.5% → 0.50s 100% [sine].
- MARK position: 0.50s (50%,50%) → 1.50s (29.3%,50%) [ease-in-out]; scale 0.50s 100% → 1.50s 64.6% [ease-in-out].
- LETTER_O x: 1.25s hidden → 1.75s final [ease-out 80%]; LETTER_P +0.12s; LETTER_A +0.25s. Letters only slide.
- LOCKUP scale: 2.25s 100% → 3.15s 102% → 4.10s 100% → 5.05s 102% → 6.00s 100% [sine].
VFX: allowed only — light horizontal motion blur on MARK 0.50–1.50s; hard-edged track-matte reveal for the letters. Forbidden: glow, flares, sparkles, shine sweeps, grain, glitch, depth of field, shadows, 3D, camera shake, vignette.
TIMING RATIO: breath 8% · glide 17% · letters 13% · breathing hold 62%.
DIRECTOR NOTE: The mark glides into its place in the lockup while the letters slide out from behind it, then the whole signature breathes calmly.
SFX (each sound on its keyframe; pitched sounds in A major; strong 0 dB, medium −6 dB, soft −12 dB; silence between cues; no music, voice or animal sounds):
- 0.50–1.50s smooth glide whoosh, medium, panning center to left
- 1.75s, 1.87s, 2.00s tiny UI ticks for O, P, A, notes A5, C#6, E6, soft, panning left to right
- 2.25s warm low wooden tok, A3, strong, center
LOGO LOCK: mark and wordmark identical to the last frame — same shapes, spacing and proportions. No other text. No eyes, face or extra details. Uniform scaling only.
```

**Bản 9:16:** MARK từ (50 %, 45,6 %) tới (22,5 %, 45,6 %), scale 42,8 %.

---

### P10 · Mạng lưới kênh · A · K02 → K07 · 6 s

```text
OPA motion graphics — flat 2D vector: one OPA, every channel.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first frame = the white bull-head logo centered on #0068FF (given); last frame = the logo at (50%,46.3%) at 60% of its first size, ringed by six white round icon buttons joined by thin white lines (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 6 seconds, one continuous shot. Keep the exact framing of both given frames — no crop, reframing, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #0068FF in every frame — no gradient, glow, grid, stars, vignette, light change or background objects.
COLOR: logo, buttons and lines #FFFFFF; icon glyphs inside the buttons #0068FF. Only these two colors. No grading, tint or color drift.
UNITS: seconds; positions in % of frame; scale in % of the first-frame logo size.
LAYERS & ANCHOR POINTS: LOGO, anchor box center. NODE_1–6 = round icon buttons clockwise from the top: globe, phone, chat bubble, envelope, person icon, shopping bag, on an ellipse 27% of the frame width × 28% of the frame height around the logo, each 11% of the frame height. SPOKES = lines from just outside the logo to each node. RING = thinner lines between neighbouring nodes.
KEYFRAMES:
- LOGO scale: 0.00s 100% → 0.50s 102% → 1.00s 100% [sine].
- LOGO: 1.00s → 2.50s scale 100% → 60%, position (50%,50%) → (50%,46.3%) [ease-in-out].
- NODE_n: launch from behind the logo at 1.50s + 0.25s × (n−1), fly straight to its ring position, scale 0% → 110% → 100% [pop].
- SPOKES trim 2.50s → 3.25s (from the logo outward) [ease-out 80%]; RING trim 3.25s → 4.00s.
- NODE_n pulse at 4.00s + 0.33s × (n−1): scale 100% → 108% → 100% in 0.25s [pop].
VFX: allowed only — light motion blur on nodes while flying (1.50–3.00s); line draw with even width. Forbidden: glow on lines or nodes, sparkles, data particles, grain, glitch, depth of field, shadows, 3D, camera shake, vignette.
TIMING RATIO: breath 17% · pull-back and burst 25% · lines 25% · pulses 33%.
DIRECTOR NOTE: The camera pulls back as six channels burst out of OPA and get wired together — one assistant on every channel, each blinking as a message arrives.
SFX (each sound on its keyframe; pitched sounds in A major, rising; strong 0 dB, medium −6 dB, soft −12 dB; silence between cues; no music, voice or animal sounds):
- 1.00–2.50s soft airy whoosh for the pull-back, medium
- node landings around 1.75s, 2.00s, 2.25s, 2.50s, 2.75s, 3.00s: soft bubbly pops A4, C#5, E5, A5, C#6, E6, medium, panned to each node's side
- 2.50–4.00s gentle rising shimmer with no melody, soft
- pulses from 4.00s: tiny UI ticks, soft, panned to each node
LOGO LOCK: the bull-head mark only — no "OPA" letters, no wordmark, no text. The logo keeps its exact silhouette; icons simple and identical to the last frame — no photos, faces or text. Uniform scaling only.
```

---

### P11 · Quét màu đảo nền · A · K01 → K02 · 3 s

```text
OPA motion graphics transition — flat 2D vector.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first frame = blue OPA bull-head logo centered on white (given); last frame = the same logo in white, centered on solid #0068FF (given). No reference images.
FORMAT LOCK: 16:9, full frame, exactly 3 seconds, one continuous shot. Camera locked; no crop, reframing, bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #FFFFFF until the panel passes, then solid #0068FF — the panel is the only thing that changes the background; no gradient between them.
COLOR: #0068FF and #FFFFFF only. Wherever the panel covers the logo, the logo becomes #FFFFFF (track matte); the flip travels exactly with the panel edge. No grading, tint or color drift.
UNITS: seconds; positions in % of frame.
LAYERS & ANCHOR POINTS: PANEL = flat #0068FF panel as tall as the frame with a straight vertical leading edge, anchor at that edge. LOGO = bull-head, same size and place in both frames, anchor bottom-center.
KEYFRAMES:
- LOGO scale: 0.00s 100% → 0.50s 101.5% → 0.75s 100% [sine].
- PANEL leading edge x: 0.75s 0% → 1.75s 100% [ease-in-out].
- LOGO scale: 1.75s 100% → 2.40s 102% → 3.00s 100% [sine].
VFX: allowed only — one hard-edged wipe (no feather, no blur on the edge). Forbidden: motion blur on the panel, glow, flash, sparkles, grain, glitch, shadows, 3D, camera shake, vignette.
TIMING RATIO: breath 25% · sweep 33% · breath 42%.
DIRECTOR NOTE: A clean blue sweep crosses the frame and inverts the colors as it passes — the logo turns white exactly at the moving edge.
SFX (no music, voice or animal sounds; silence before and after):
- 0.75–1.75s clean airy whoosh, medium, panning left to right
LOGO LOCK: the bull-head mark only — no "OPA" letters, no wordmark, no text. Same silhouette and size in every frame. A flat logo, not a character: no eyes, face or extra details.
```

---

### P12 · Thông báo dồn (nền cho AE) · B · T04 · 5 s

```text
Flat 2D vector motion graphics plate for compositing.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: reference image 1 = the OPA style board — match its colors, outline weight, corner roundness and flat shapes; do not copy its layout. No first or last frame.
FORMAT LOCK: 16:9, full frame, exactly 5 seconds, one continuous shot. No bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #FFFFFF in every frame — no gradient, texture, vignette, light change, shadows or background objects.
COLOR: bubbles #E6F0FF; alert dots #E5484D, only as small dots (at most 3% of the frame height). Nothing else colored. No grading, tint or color drift.
UNITS: seconds; positions in % of frame; scale in %.
LAYERS & ANCHOR POINTS: BUBBLE_1 at (22%,30%), BUBBLE_2 at (70%,38%), BUBBLE_3 at (35%,68%) = empty rounded chat bubbles with a tail, 20% of the frame width, anchor at the tip of each tail. BADGE_n = small empty #E5484D dot at the top-right corner of each bubble, anchor its center. SMALL_BUBBLES = three more at half size. CAMERA = whole frame.
KEYFRAMES:
- BUBBLE_1/2/3 scale 0% → 105% → 100% in 0.33s [pop], at 0.25s, 0.75s, 1.25s.
- BADGE_n scale 0% → 120% → 100% [pop], 0.25s after its bubble; then pulses 100% → 115% → 100% three times, each gap shorter (0.60s, 0.45s, 0.30s).
- SMALL_BUBBLES scale 0% → 105% → 100% [pop] at 2.50s, 2.75s, 3.00s, filling empty areas.
- CAMERA scale 0.00s 100% → 5.00s 104% [linear].
- 4.00–5.00s: layout stays put (only the slow push continues) so text can be added on top.
VFX: none besides the pops. Forbidden: glow, sparkles, shine, grain, glitch, depth of field, shadows, 3D, camera shake, vignette.
TIMING RATIO: bubbles 30% · badges 30% · crowding 20% · steady 20%.
DIRECTOR NOTE: Customer messages keep popping up and the red dots keep pulsing faster — an inbox overflowing.
SFX (each sound on its keyframe; pitched sounds in A major; strong 0 dB, medium −6 dB, soft −12 dB; no music, voice or animal sounds):
- 0.25s, 0.75s, 1.25s soft notification pings A3, C#4, E4, medium, panned left, right, left
- each badge pop and pulse: tiny UI tick, E6, soft, getting busier
- 2.50s, 2.75s, 3.00s lighter bubbly pops, soft
LOCK: no text, numbers, letters, logos, faces or photos anywhere — bubbles and dots stay empty.
```

Sau đó trong AE: đặt chữ câu hỏi của khách vào trong bong bóng, số đếm lên chấm đỏ (expression ở mục 4 của kịch bản promo).

---

### P13 · Ô nhập kéo dài (nền cho AE) · B · T04 · 4 s

```text
Flat 2D vector UI motion plate for compositing.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: reference image 1 = the OPA style board — match its input bar, round button, outline weight and corner roundness; do not copy its layout. No first or last frame.
FORMAT LOCK: 16:9, full frame, exactly 4 seconds, one continuous shot. Camera locked; no bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #0068FF in every frame — no gradient, texture, vignette, light change, shadows or background objects.
COLOR: plus button, bar and send button #FFFFFF; plus sign and cursor #0068FF. Only these two colors. No grading, tint or color drift.
UNITS: seconds; positions and sizes in % of frame.
LAYERS & ANCHOR POINTS: PLUS = white circle with a thin plus sign, 9% of the frame height, at (22%,50%), anchor its center. BAR = white fully rounded input bar, 9% of the frame height tall, anchor its LEFT edge at the right side of PLUS. CURSOR = thin vertical cursor near the bar's left end. SEND = white circle, 9% of the frame height.
KEYFRAMES:
- PLUS scale: 0.25s 0% → 0.40s 110% → 0.50s 100% [pop].
- BAR width: 0.50s 9% → 0.90s 57% of the frame width, growing to the right only [ease-out 80%]; corners stay fully round.
- CURSOR: blinks every 0.50s from 0.90s to 4.00s, on the beat.
- SEND scale: 3.40s 0% → 3.55s 110% → 3.65s 100% [pop] at (82%,50%).
- From 0.90s, PLUS and BAR stay perfectly still (no drift) so text can be placed later.
VFX: none. Forbidden: glow, shine sweeps, sparkles, grain, glitch, depth of field, shadows, 3D, camera shake, vignette.
TIMING RATIO: build 22% · steady bar 63% · send button 15%.
DIRECTOR NOTE: A clean chat input appears — the plus pops, the bar stretches out from it, the cursor waits for a customer's question, and a send button arrives.
SFX (each sound on its keyframe; pitched sounds in A major; strong 0 dB, medium −6 dB, soft −12 dB; no music, voice or animal sounds):
- 0.25s soft bubbly pop, A5, medium, left
- 0.50–0.90s soft expand swipe, medium, left to center
- 3.40s soft bubbly pop, E5, medium, right
LOCK: no text, letters, numbers or logos anywhere.
```

Sau đó trong AE: gõ "Shop còn size M không ạ?" bằng expression gõ chữ, 0,9–3,4 s, đặt vào thanh. Thanh đứng yên nên không cần tracking.

---

### P14 · Zoom ra thành tường thẻ chat · A1 · K01 · 6 s

```text
Flat 2D vector motion graphics.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: first frame only = the blue OPA bull-head logo centered on white (given). No last frame, no reference images.
FORMAT LOCK: 16:9, full frame, exactly 6 seconds, one continuous shot. No bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #FFFFFF in every frame — the pull-back reveals only the cards, never a room, desk, floor, gradient or shadows.
COLOR: cards #FFFFFF with 2px #0068FF outlines; placeholder bars #E6F0FF; avatar logo #0068FF. Only these colors. No grading, tint or color drift.
UNITS: seconds; positions in % of frame; scale in % of the first-frame size.
LAYERS & ANCHOR POINTS: LOGO = the bull-head; it turns out to be the small avatar at the top-left of CARD_MAIN; zoom anchor = LOGO center. CARD_MAIN = white rounded chat card with placeholder bars. WALL = about 20 similar cards in a loose grid on three depth layers.
KEYFRAMES:
- CAMERA scale (zoom-out around LOGO): 0.00s 100% → 1.50s 18% [ease-in-out]; CARD_MAIN appears around the logo as it shrinks.
- WALL: 1.00s → 2.00s cards appear from the edges, 0.05s apart.
- CAMERA pan 1.50s → 6.00s, constant leftward drift: near cards 6%, mid 4%, far 2% of the frame width [linear].
VFX: allowed only — parallax between the three layers. Forbidden: blur on far cards, depth of field, 3D tilt, glow, shine, grain, glitch, shadows, camera shake, vignette.
TIMING RATIO: zoom-out 25% · reveal 8% · parallax drift 67%.
DIRECTOR NOTE: What looked like a logo is OPA's avatar inside one chat; pulling back reveals a whole wall of conversations OPA handles at once, drifting calmly.
SFX (pitched sounds in A major; strong 0 dB, medium −6 dB, soft −12 dB; no music, voice or animal sounds):
- 0.00–1.50s soft airy whoosh, medium, center
- 1.00–2.00s faint layered card slides, soft, spread left and right
- 2.00–6.00s near silence
LOGO LOCK: the bull-head mark only — no "OPA" letters, no wordmark, no text. The avatar logo keeps the exact silhouette of the first frame at every size. No readable text, faces or photos.
```

---

### P15 · Điện thoại trồi lên · B · T03 + T04 · 5 s

```text
Flat 2D vector UI motion plate.
Everything below is invisible animation data. Never draw any of it: no labels, names, numbers, percentages, note names, arrows, guides, dimension lines, boxes, grids or any text on screen.
INPUT: reference image 1 = the OPA bull-head logo, white on blue — keep it identical wherever it appears; reference image 2 = the OPA style board — match its bubbles, outline weight and corner roundness; do not copy its layout. No first or last frame.
FORMAT LOCK: 16:9, full frame, exactly 5 seconds, one continuous shot. No bars, borders, captions, watermark, cuts or speed ramps.
BACKGROUND LOCK: solid #0068FF in every frame — no gradient, glow, vignette, light change, shadows or background objects.
COLOR: phone body and screen #FFFFFF; customer bubbles #E6F0FF; OPA bubbles #0068FF with a tiny #FFFFFF bull-head avatar. Only these colors. No grading, tint or color drift.
UNITS: seconds; positions in % of frame; scale in %.
LAYERS & ANCHOR POINTS: PHONE = flat white phone outline, 70% of the frame height, final center (50%,52%), anchor bottom-center. MSG_1–4 = empty chat bubbles inside the screen: customer on the left, OPA on the right; anchor at the tip of each tail.
KEYFRAMES:
- PHONE position y: 0.25s y 130% → 1.00s 52% [ease-out 80%]; rotation 0.25s −4° → 1.00s 0°.
- MSG_1 (customer) 1.25s, MSG_2 (OPA) 2.00s, MSG_3 (customer) 2.75s, MSG_4 (OPA) 3.50s: scale 0% → 105% → 100% in 0.30s [pop]; older messages slide up [ease-in-out].
- PHONE stays perfectly still from 3.50s to 5.00s.
VFX: allowed only — light vertical motion blur on PHONE 0.25–1.00s. Forbidden: screen glare, glow, reflections, shadows, 3D tilt, depth of field, grain, glitch, camera shake, vignette.
TIMING RATIO: rise 15% · conversation 55% · steady 30%.
DIRECTOR NOTE: A phone rises and a quick chat plays out — a customer asks, OPA answers right away, twice, on an even rhythm.
SFX (each sound on its keyframe; pitched sounds in A major; strong 0 dB, medium −6 dB, soft −12 dB; no music, voice or animal sounds):
- 0.25–1.00s soft rising swoosh, medium, bottom to center
- 1.25s and 2.75s soft notification ping, A3, medium, left (customer)
- 2.00s and 3.50s soft bubbly pop, E5, medium, right (OPA)
LOGO LOCK: the tiny avatar identical to reference image 1. No readable text, faces, photos or other brand logos.
```

## 9. Prompt sửa có số

Mỗi lượt chỉ đổi **một** thứ. Câu luôn mở đầu bằng:

```text
Keep everything else exactly the same — same format and framing, same background, same colors, same timing and same sound. Only …
```

| Lỗi | Phần sau chữ "Only" |
|---|---|
| Vượt đà quá mạnh | `change HEAD overshoot from 112% to 106%, settling by 1.15s.` |
| Sừng vào trễ | `shift all HORN keyframes 0.25s earlier.` |
| Xoay quanh tâm thay vì đáy | `move the rotation anchor of LOGO to its bottom-center (50%,100% of its box).` |
| Zoom vào sai chỗ | `move the zoom anchor to the center of the inner opening, (50%,56.8%) of the frame.` |
| Logo lệch màu | `fix the logo color to exactly #0068FF in every frame; no tint or grading.` |
| Nền ngả xám, có vignette hay gradient | `fix the background to solid #FFFFFF in every frame; no vignette, gradient or shading.` |
| Nền xuất hiện sàn, phòng, đồ vật | `remove everything behind the logo; the background is plain #FFFFFF only.` |
| Có viền đen hoặc khung bị cắt | `fix the format: full 16:9 frame, no black bars, borders or crop.` |
| Có glow, lấp lánh, bóng đổ | `remove the glow, sparkles and shadows; keep every shape flat.` |
| Motion blur quá nhiều | `reduce motion blur to a light trail during the fastest 0.2s only.` |
| Âm lệch nhịp | `move the wooden tok so it lands exactly at 1.25s, on the horn lock.` |
| Có nhạc hoặc giọng nói | `remove the music and any voice; keep the sound effects.` |
| Âm chói, không cùng giọng | `retune the pops to the notes A4, C#5, E5 (A major).` |
| Logo sai khi dùng ảnh tham chiếu | `make the logo identical to reference image 1: same silhouette, flat color.` |
| Đoạn cuối đứng chết | `add one slow breath on LOGO (100% → 102% → 100%, [sine]) in the last 1.5s.` |

## 10. Kiểm clip ra

Đưa clip vào After Effects. Bật **Info** (Ctrl + 2) và **Rulers** (Ctrl + R).

| Kiểm | Cách | Ngưỡng đạt |
|---|---|---|
| Thời gian | Tua từng khung tới các mốc KEYFRAMES | Lệch ≤ 0,2 s |
| Scale, góc | Solid mỏng làm thước; guide theo bảng 1.3 | Scale ≤ 3 %, góc ≤ 2° |
| Khung đầu, cuối | Đặt khung neo lên trên, blend mode Difference | Đen tuyền |
| Màu logo | Bảng Info, đo ở giữa thân logo | ≈ (0, 104, 255), lệch ≤ 3 mỗi kênh |
| Nền | Đo 4 góc ở 0 s, giữa clip và cuối clip | Đúng một giá trị (255, 255, 255) hoặc (0, 104, 255), không trôi |
| Định dạng | Xem mép khung, đặc biệt khung cuối | Không viền đen, không bị cắt |
| VFX | Tua chậm các đoạn nhanh | Chỉ có VFX trong danh sách được dùng |
| SFX | Bật waveform âm (phím L L), so điểm đánh với mốc keyframe | Lệch ≤ 1 khung; không nhạc, không giọng |

Lệch quá ngưỡng thì dùng đúng một câu ở mục 9 rồi tạo lại. Âm Omni dù đạt vẫn thay bằng file thư viện (bảng 4.2) khi dựng phim.

## 11. Ghép thành promo

| Promo | Prompt |
|---|---|
| C1 (0–4 s) | P12 làm nền + chữ, số AE |
| C2 (4–8 s) | P13 làm nền + chữ AE |
| C3 (8–14 s) | AE hoàn toàn; P15 làm nền thay thế |
| C4 (14–20 s) | P10 |
| C5 (20–26 s) | P08 bản 6 s |
| C6 (26–32 s) | P09 + chữ, nút CTA AE |
| Nối nền trắng ↔ xanh | P11 hoặc khối quét làm bằng AE |
