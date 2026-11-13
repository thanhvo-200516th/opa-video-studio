Ngày tạo: 07/10/2026 · Claude Code (Opus 5.5) · Trạng thái: thiết kế để dựng 3 đoạn test, chờ chủ dự án chọn sau khi xem test

# NGÔN NGỮ CHUYỂN ĐỘNG OPA v2 + KỊCH BẢN 3 TEST (V2 "Không bỏ sót khách", 16:9)

**Khung:** 1920×1080, 60 fps. **Giữ nguyên:** câu chuyện, lời đã duyệt (`src\videos\V2\copy.ts`, biến thể mặc định `V2_DEFAULT_PROPS`), master âm `public\audio\v2-khong-bo-sot-khach-master.wav` (−16 LUFS). Mọi mốc tính bằng **giây** (cue `f` trong `src\audio\cues\v2-khong-bo-sot-khach.json` chia 30). Frame 60 fps ghi là **f60** = giây × 60.

**Nguồn:** `docs\v2-16x9\research-chan-doan.md` (CĐ), `research-ky-thuat.md` (KT), `research-tu-vung.md` (TV, mã K01–K62), `research-prompt-motion.md` (PM), `BRAND-SPEC.md`, `docs\v2-thiet-ke.md` (TK), `docs\v2-ke-hoach-thuc-thi.md` (KH), `out\v2-khong-bo-sot-khach\README.md`, mã `src\videos\V2\*`, `src\mascot\*`, `src\fx\*`, `src\ui\*`.

---

## 0. Tóm tắt

**Vì sao bản 9:16 nhàm (CĐ):** 57,6 % frame gần đứng yên, không camera, không lớp sâu, mọi chữ một kiểu trồi, gần như không đường cong nào có vọt, 2 cắt cứng toàn khung, Bò vắng mặt 49 % thời lượng. Chỉ chương GỌN (10–17,5 s) sống, vì nhiều lớp cùng chạy.

**Ngôn ngữ mới, 5 trụ:**
1. **Một camera luôn sống** trôi qua một thế giới phẳng 4 lớp sâu (parallax 2.5D). Camera không bao giờ đứng, không bao giờ nảy.
2. **Chuyển cảnh liền mạch:** wipe khối màu bằng camera, tràn từ khe, biến hình khối từ lòng U, zoom xuyên khe trán, match/morph thẻ. Trong 3 test: 0 cắt cứng.
3. **Vũ đạo:** so le, chồng nhịp, follow-through, lấy đà, va chạm nhân quả, nảy có kiểm soát theo loại vật. Lặp lại thì biến tấu.
4. **Blur theo tốc độ** (blur hướng từng vật + subframe cho camera nhanh). Vật đứng và chữ đang đọc luôn sắc.
5. **Bò là nhân vật:** từ lúc trồi (7,733 s) tới hết, Bò luôn có mặt, diễn bằng thư viện có sẵn cộng camera.

**Quyết định chốt khi các nghiên cứu lệch nhau:**

| Chỗ lệch | Chốt | Lý do |
|---|---|---|
| Motion blur: PM xếp `@remotion/motion-blur` ưu tiên 1; KT đo thấy lệch màu token và hình đi trước âm 0,7 f | **Không cài gói.** T1 blur hướng từng vật + T2 `SubframeBlur` tự viết (trung bình chạy, mẫu đối xứng) | Số đo trên máy này (KT §2.2) thắng ý chưa kiểm |
| Quy ước độ sâu: TV dùng hệ số k (k < 1 là xa); KT dùng depth d (d > 1 là xa) | **Mô hình kim lỗ của KT**, d > 1 là xa, parallax = 1/d. Lớp: 2,5 / 1,5 / 1 / 0,75 (tương đương 0,4 / 0,67 / 1 / 1,33 của PM) | Có dolly z và đạo hàm chính xác cho blur |
| Camera dùng spring? | Chỉ bezier, hermite hoặc spring tới hạn ζ = 1 (vọt 0). Ngoại lệ duy nhất: cú đập (punch) ở mốc tác động | TV §2.3, KT §3.3 |
| Lặng trước húc: tĩnh tuyệt đối (PM) hay gần lặng (TV, CĐ) | [9,2; 9,6) s: **mọi vật đứng tuyệt đối, camera dolly-zoom** (nền dồn tới). Khai báo là ngoại lệ đo | Giữ tương phản, vẫn không có frame chết |
| Rung ở HIT: rung tịnh tiến (TV K11) hay chỉ scale (PM) | **Chỉ đập scale 3 % + nghiêng đá 0,5°**, không rung tịnh tiến | Sạch, không trông như lỗi |
| Bảng spring: 3 bộ tên khác nhau | Gộp thành bộ `SP` ở §2.2 | Một nguồn |

---

## 1. Nguyên tắc (12) và chỉ số đo

**Cách đo chung** (`tools\v2w\metrics.py`, §8.7): giải mã MP4 về xám 960×540; một điểm ảnh "đổi" khi lệch > 6 mức. So frame f với f − 2 (cách 1/30 s, để so được với số 9:16). **Tĩnh B** = frame có ≤ 0,5 % điểm ảnh đổi. **Tĩnh A** = ≤ 0,04 %. **Cắt cứng** = frame có > 30 % điểm ảnh đổi so với f − 1 (60 fps), đồng thời cả f − 1 và f + 1 đổi < 1/3 mức đó. Ô 2 s căn theo giây chẵn của phim (ô ngắn hơn 1 s gộp vào ô kề).

| # | Nguyên tắc | Chỉ số đo được và ngưỡng |
|---|---|---|
| 1 | **Không frame chết** | Tĩnh B ≤ **15 %** mỗi ô 2 s; ≤ 10 % cả đoạn test. Tĩnh A = **0** frame. Không chuỗi Tĩnh B > **12 f60** (0,2 s). Ngoại lệ khai báo duy nhất trong 3 test: [9,2; 9,6) s (ô [8; 10) được tới 30 %). Bản 9:16 đang 57,6 % |
| 2 | **Một camera, luôn sống, không nảy** | Mọi lớp đọc một `camAt(t)`. Tốc độ góc khung lớp d = 1 ≥ **15 px/s** (đích 20 px/s) ngoài khoảng khai báo. Vọt camera = 0. Roll ≤ 2°. Cú đập cả khung ≤ **3/phim**: 8,0 s (1 %), 10,0 s (3 %), 24,5 s (1,5 %) |
| 3 | **Liền mạch** | 3 test: **0** cắt cứng. Cả phim ≤ **2** cắt cứng có chủ đích, khai báo trong `CUTS`, phải là "cắt khớp vận tốc" (§3.5 F). Mỗi chuyển cảnh dùng một trong 6 kiểu A–F. Khối nối có mặt ở mọi frame của chuyển cảnh |
| 4 | **Chồng nhịp và biến tấu** | Vật sau bắt đầu khi vật trước đi được 60–90 % (chồng ≥ 10 %). So le anh em 3–5 f60, cả đợt ≤ 0,5 s. Mỗi phách (0,5 s) có ≥ 1 sự kiện bắt đầu ở đoạn nhạc intro/build/full; ≥ 1 mỗi 2 phách ở breath (đếm trên bảng kịch bản §7). Sự kiện lặp đổi ≥ 1 thông số mỗi lần (biên độ ±15–25 %, cung, hướng, làn) |
| 5 | **Follow-through, không dừng phẳng** | Con trễ cha 2–4 f60 (tối đa 6). Mọi lần đáp có một trong ba: vọt theo loại vật (#6), lắc tắt ≤ 3° trong 0,35 s, hoặc trôi tiếp 12–30 px/s |
| 6 | **Nảy có kiểm soát theo loại vật** | Vọt tối đa: camera **0**; kích thước mascot **0** (chỉ `reveal` có sẵn nảy vị trí); chữ ≤ **2,5 %**; khối nặng ≤ **2 %**; khối biến hình ≤ **3 %**; UI nhỏ (chip, pill, bong bóng) ≤ **6 %**; `SPRING_POP` 9,5 % ≤ **2 lần/phim** (reveal + nút CTA). Vọt chỉ áp lên transform, không lên opacity |
| 7 | **Blur theo tốc độ** | Vật có tốc độ màn hình v ≥ **8 px/f60**: blur hướng σ = min(v/6; 8) px. v < 8: σ = 0. Chữ trong thời gian đọc: σ = 0. Trắng trên xanh: trần σ 4. Camera có tốc độ góc khung ≥ **16 px/f60**: subframe 3–12 mẫu. Không blur làm chiều sâu |
| 8 | **Chiều sâu 2.5D bằng 5 màu** | 4 lớp thế giới d = 2,5 / 1,5 / 1 / 0,75 + lớp chữ HUD. Hai lớp kề chênh parallax ≥ 1,5 lần. Lớp xa dùng token gần màu nền. Mọi chặng camera ≥ 0,4 s phải thấy parallax. Lớp gần chỉ xuất hiện khi camera nhanh, không đứng trong khung > 0,3 s |
| 9 | **Mỗi lúc một tiêu điểm** | Tối đa 1 chuyển động lớn (vật > 2 % diện tích khung, v > 8 px/f60) làm tiêu điểm; vật khác chỉ thở hoặc trôi. Chuỗi trao tay: B bắt đầu trong [A tới đích − 2 f60; + 4 f60] |
| 10 | **Chữ đọc được, dấu nguyên** | Nhóm đọc được ≤ 0,45 s sau mốc vào, giữ ≥ 1,5 s. ≤ **9 chữ/khung** (một chữ được đếm khi ≥ 50 % hộp chữ hiện và opacity ≥ 0,5; tên giả không đếm). Mask chừa trên ≥ **0,24 em**, dưới ≥ **0,16 em**. Cỡ hiệu dụng (cỡ × mọi scale) ≥ 56 px cho lời, ≥ 40 px cho tên trên UI |
| 11 | **Bò là nhân vật** | Từ 7,733 s tới hết: Bò có mặt ≥ **90 %** thời lượng (cao ≥ 270 px = 25 % H, hoặc là chủ thể camera). Vắng chỉ khi camera lặn qua khe (≤ 0,4 s). Trước 7,733 s Bò vắng vì câu chuyện ("đêm qua không ai trực"). Chỉ biến đổi cứng (dời, phóng đều, xoay ≤ 8°) và động tác thư viện; màu theo `MASCOT_ON`; không squash, không morph |
| 12 | **Ăn khớp âm đã duyệt** | Mỗi cue có sự kiện hình trong ±1 f60 theo `anchor` (onset hoặc peak). Cú tác động đúng f60 480 (8,0 s), 600 (10,0 s), 1470 (24,5 s). Đỉnh whoosh trùng frame đổi nhiều nhất của chuyển cảnh (whip: vận tốc camera lớn nhất; iris, flood: frame phủ thêm nhiều nhất) ±2 f60. Trong lặng [9,733; 10,0) s chỉ có pha lao |

---

## 2. Bộ preset

Đặt trong `src\v2w\core\ease.ts` và `src\v2w\core\spring.ts` trong giai đoạn test. Màu luôn lấy từ `COLORS` (`src\brand\tokens.ts`). Khi chủ dự án duyệt hướng, preset được chuyển vào `src\brand\tokens.ts` và ghi vào BRAND-SPEC.

### 2.1 Easing (`Easing.bezier` của Remotion)

| Token | Bezier | Tính cách | Dùng cho |
|---|---|---|---|
| `EZ.OUT` | (0.16, 1, 0.3, 1) | dứt khoát, đuôi dài | khối, UI, chữ vào; camera đáp sau cú lao |
| `EZ.OUT_SOFT` | (0.22, 1, 0.36, 1) | chuẩn | phần tử phụ; độ mờ vào |
| `EZ.IN` | (0.55, 0, 1, 0.45) | rời dứt khoát | ra cảnh, vật bị hất hoặc văng, chữ rút |
| `EZ.IN_HARD` | (0.7, 0, 0.84, 0) | bứt tốc | pha lấy đà ngắn |
| `EZ.CAM` | (0.65, 0, 0.35, 1) | vào ra đều; vận tốc đỉnh ở giữa = 2,86 lần trung bình | camera đổi trạm, whip, quỹ đạo cung |
| `EZ.DRIFT` | (0.45, 0, 0.55, 1) | êm | trôi dài, đẩy chậm |
| `EZ.ZOOM_THRU` | (0.6, 0, 0.85, 0.5) | chậm đầu, dốc cuối (vận tốc lớn nhất ở cuối) | lặn xuyên khe |
| `EZ.SCENE` | (0.2, 0.8, 0.2, 1) | = `EASE_IN_SCENE` có sẵn | mép trước nét gạch |
| `approach` | x = đích + (gốc − đích)·e^(−Δt/τ), τ = 0,2 s | "vào khi đang chạy": vận tốc lớn nhất ngay t0 | khung đầu sau chuyển cảnh, chữ ăn theo camera |

Luật dùng: vào dùng OUT, ra dùng IN, đổi chỗ và camera dùng CAM hoặc DRIFT. Không dùng một easing cho mọi thứ.

### 2.2 Spring (nghiệm đóng, `springAt`)

`ω = √(stiffness/mass)`, `ζ = damping / (2·√(stiffness·mass))`, vọt = e^(−ζπ/√(1−ζ²)). Nghiệm đóng trùng `spring()` của Remotion cùng config (KT §1.3 đo lệch ≤ 4,4·10⁻¹⁶) nhưng nhận t lẻ và tính bằng giây.

| Tên | mass | stiffness | damping | ω | ζ | Vọt | Đỉnh vọt | Vào ±2 % (≤) | Dùng cho |
|---|---|---|---|---|---|---|---|---|---|
| `KHOI_NANG` | 2 | 200 | 32 | 10 | 0,80 | 1,5 % | 0,52 s | 0,55 s | khung hộp thư, thẻ lớn dời chỗ, khối nền |
| `MORPH` | 1 | 196 | 21 | 14 | 0,75 | 2,8 % | 0,34 s | 0,41 s | w/h khối biến hình, thẻ nở |
| `UI_SNAP` | 1 | 400 | 34 | 20 | 0,85 | 0,6 % | 0,30 s | 0,27 s | hàng vào slot, chồng bong bóng dịch, mép trước, bo góc khối |
| `UI_POP` | 1 | 256 | 21,4 | 16 | 0,67 | 5,9 % | 0,26 s | 0,39 s | bong bóng bật, chip ✓, pill, nút |
| `CHU` | 1 | 324 | 28 | 18 | 0,78 | 2,0 % | 0,28 s | 0,31 s | mỗi từ trồi trong mask |
| `MEP_SAU` | 1 | 144 | 21,6 | 12 | 0,90 | 0,15 % | 0,60 s | 0,44 s | mép sau (kỹ thuật hai mép) |
| `BO` | 1 | 81 | 16,2 | 9 | 0,90 | 0,15 % | 0,80 s | 0,59 s | Bò dời chỗ (chỉ vị trí) |
| `CAMERA` | 1 | 42,25 | 13 | 6,5 | 1,00 | 0 | — | 0,90 s | camera bám vật (trễ tự nhiên 0,15–0,3 s) |
| `CAMERA_NHANH` | 1 | 100 | 20 | 10 | 1,00 | 0 | — | 0,58 s | camera đổi đích gấp, đi trước |
| `POP_NHAN` | 1 | 100 | 12 | 10 | 0,60 | 9,5 % | 0,39 s | 0,6 s | = `SPRING_POP`: reveal (trong thư viện) và nút CTA, ≤ 2/phim |

### 2.3 Hàm mẫu

```ts
// 0 → 1 từ t0 (giây). Nghiệm đóng, nhận t lẻ (subframe).
export const springAt = (t: number, t0: number, s: SpringSpec): number => {
  const dt = t - t0;
  if (dt <= 0) return 0;
  const w = Math.sqrt(s.stiffness / s.mass), z = s.damping / (2 * Math.sqrt(s.stiffness * s.mass));
  if (z >= 1 - 1e-9 && z <= 1 + 1e-9) return 1 - (1 + w * dt) * Math.exp(-w * dt);
  if (z > 1) { const wd = w * Math.sqrt(z * z - 1); return 1 - Math.exp(-z * w * dt) * (Math.cosh(wd * dt) + (z * w / wd) * Math.sinh(wd * dt)); }
  const wd = w * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-z * w * dt) * (Math.cos(wd * dt) + (z * w / wd) * Math.sin(wd * dt));
};
// Nhiều lần đổi đích: cộng chồng, vận tốc liên tục (PM §3.3). Zoom: dùng trackLog (cộng trong ln).
export const track = (t: number, from: number, changes: readonly Change[], s: SpringSpec): number =>
  changes.reduce((acc, c, i) => acc + (c.to - (i === 0 ? from : changes[i - 1].to)) * springAt(t, c.at, s), from);
```

### 2.4 So le, chồng nhịp, follow-through

| Hằng | Giá trị | Ghi chú |
|---|---|---|
| `STAGGER.sibling` | khe đầu 0,067 s (4 f60), mỗi khe sau × 0,85 | đợt co dần, tổng ≤ 0,5 s (K28) |
| `STAGGER.word` | 0,06 s | mỗi từ trong một dòng |
| `STAGGER.line2` | 0,10 s; dòng nhấn (`accent` của copy.ts) 0,133 s | khớp `PUNCH.stagger`, `accentDelay` của V2 |
| `STAGGER.row` | 0,05 s | hàng trong thẻ |
| `STAGGER.radial` | trễ = khoảng cách / 2400 px/s, tối đa 0,5 s | gợn sóng từ điểm va chạm (K40) |
| `OVERLAP` | nhóm B bắt đầu khi nhóm A đạt 60 % | chồng 40 % (K29) |
| `EXIT_GAP` | cùng một ô chữ: nhóm cũ ra xong ≥ 0,067 s trước nhóm mới vào | khác ô thì được chồng ≤ 0,15 s |
| `CAM_LEAD` / `CAM_LAG` | camera đi trước đổi cảnh 0,15 s; bám vật trễ 0,15–0,3 s (spring `CAMERA`) | PM §3.6 |
| `LAG_CHILD` | 0,05 s (2–4 f60), tối đa 0,1 s | `child(t) = parent(t − lag)` |
| `HANG_ROT` | xoay con = clamp(−0,05·vx; ±4°), vx tính bằng px/f60 | vật treo hoặc nội dung trong khối |
| `SETTLE_WOBBLE` | rot = 2,5°·e^(−Δ/0,12)·cos(2π·4·Δ), trần 3°, 0,35 s | UI đáp; cấm cho mascot |
| `POST_DRIFT` | 12–30 px/s theo hướng vừa đi | sau khi khối lớn tới đích |
| `ANTICIPATION` | lùi 4–8 % quãng trong 0,1–0,15 s (`EZ.OUT`) rồi đi (`EZ.IN`) | chỉ khi làm rõ hướng |

### 2.5 Thời lượng theo khối lượng (giây)

| Loại | Vào | Ra (≈ 0,6 lần vào) |
|---|---|---|
| Camera đổi trạm | 0,8–1,2 (≤ 2,0) | — |
| Whip | 0,45–0,5 (đỉnh ≥ 150 px/f60) | — |
| Lặn xuyên khe + iris | 0,35 + 0,267 | — |
| Flood | 0,367 (22 f60, mỗi f60 phủ ≤ 15 % khung) | — |
| Khối nặng dời | 0,45–0,6 | 0,3–0,35 |
| Thẻ, khối biến hình | 0,35–0,45 | 0,25 |
| Pill, chip, bong bóng | 0,2–0,28 | 0,15 |
| Chấm, tick | 0,12–0,15 | 0,1 |
| Chữ: mỗi từ | 0,30 (`CHU`) | rút 0,20 (`EZ.IN`) |
| Bò dời chỗ | 0,5–0,6 (`BO`) | — |

### 2.6 Motion blur

**T1. Blur hướng cho từng vật (mặc định):**
- `v = p(t) − p(t − 1/60)`: px màn hình mỗi f60, đã cộng chuyển động camera (lấy mẫu hàm thuần, không state).
- `σ = |v| < 8 ? 0 : min(|v|/6, 8)` (màn trập 180°: vệt L = |v|/2, σ = L/3). Trần 4 cho khối hoặc chữ trắng trên nền xanh. Chữ đang đọc: 0.
- Vẽ: lớp ngoài xoay θ = atan2(vy, vx) và gắn `feGaussianBlur stdDeviation="σ 0"`, lớp trong xoay −θ (KT §2.5, đã chạy được cả HTML lẫn SVG).
- Mascot đang `charge` dùng `blurX` có sẵn của thư viện, không chồng T1.

**T2. `SubframeBlur` cho camera nhanh** (chỉ bọc lớp thế giới, chữ HUD nằm ngoài):
- `vCam` = độ dời lớn nhất của 4 góc khung (lớp d = 1) giữa t − 1/120 và t + 1/120, tính bằng px/f60.
- `samples = vCam < 16 ? 1 : clamp(1 + ceil(0,5·vCam / 6), 3, 12)`.
- Mẫu i ở frame + 0,5·(i/(N−1) − 0,5) (đối xứng quanh t), lớp i opacity 1/(i+1), blend thường. Mỗi mẫu có nền đục. Màu vùng đứng yên giữ đúng token (KT đo PASS palette).
- Không có `<Sequence>` mount hoặc unmount trong ±0,5 frame quanh khúc blur: bật tắt bằng điều kiện t.

### 2.7 Hạn mức liều lượng

| Thủ pháp | Tối đa cả phim | Trong 3 test |
|---|---|---|
| Cú đập cả khung (punch) | 3 | 8,0 s (1 %), 10,0 s (3 %) |
| `SPRING_POP` | 2 | reveal 7,733 s |
| Cắt cứng | 2 | 0 |
| Whip | 1 | 1,967 s |
| Flood từ khe | 1 | 10,0 s |
| Lặn xuyên khe + iris | 1 | 17,033–17,650 s |
| Dolly-zoom | 1 | 9,2–9,6 s |
| Match/morph thẻ | 2 | 19,9 s |
| Charge | 1 lớn + 1 nhẹ | 9,6 s (lớn), 17,7 s (nhẹ) |
| Snort | 2 | 8,8 s (có âm), 18,5 s (dưới brass, không âm riêng) |
| Lặng khai báo | 1 (+ khung CTA cuối) | 9,2–9,6 s |

---

## 3. Ngữ pháp camera và chuyển cảnh

### 3.1 Mô hình camera kim lỗ 2.5D (KT §3.1)

- Đơn vị thế giới: px khung khi camera nghỉ, đo ở lớp d = 1. Camera `Cam = { x, y, z, zoom, rot }`: x, y là lia (px ở d = 1); z là dolly theo đơn vị độ sâu; zoom là ống kính; rot là roll (độ).
- Điểm (u, v) trên lớp d ra màn hình:

```
s      = zoom · d / (d − z)          (d − z ≤ 0,08 hoặc s > 40 ⇒ ẩn lớp)
screen = C + R(rot) · s · ((u, v) − C − (x, y)/d)          C = (960, 540)
CSS mỗi lớp: transform-origin 0 0; transform: translate(960px,540px) rotate(rot) scale(s) translate(−960 − x/d px, −540 − y/d px)
```

- Lia có parallax 1/d. Dolly làm lớp gần phóng nhanh hơn lớp xa. Camera nghỉ thì mọi lớp đúng cỡ đã vẽ.
- Không dùng CSS 3D, không `will-change` trên lớp bị scale (chữ mờ).
- **Đặt điểm vào chỗ** (`camFor`): muốn điểm thế giới P (d = 1) nằm ở điểm màn S với s = zoom/(1 − z): `x = Pu − 960 − (Sx − 960)/s`, `y = Pv − 540 − (Sy − 540)/s`.

### 3.2 Lớp thế giới

| Lớp | d | Parallax | Nội dung (phẳng, 5 màu) | Mật độ |
|---|---|---|---|---|
| `XA` | 2,5 | 0,4 | khối bo 40–80 và tròn, 180–520 px, scale 0,6–0,8, mỗi khối tự trôi 6–14 px/s (seed) | 4–8 khối mỗi khung |
| `GIUA` | 1,5 | 0,67 | bong bóng ma (không vạch), vòng viền 4 px, thanh mảnh | 2–4 |
| `CHINH` | 1 | 1 | trường màu chương, hộp thư, Bò, tin, thẻ, chữ gắn thế giới (L8, L8b) | — |
| `GAN` | 0,75 | 1,33 | 1 khối lớn (≥ 0,4 khung) lướt sát ống kính khi camera nhanh | chỉ trong whip, lặn |
| `HUD` | ngoài thế giới | — | lời chính; chỉ nhận 0,5 × thành phần trôi vi mô của camera, không nhận lia trạm, zoom, roll | — |

**Tông theo trường màu (K15, không nội suy màu):**

| Trường | Nền (`CHINH`) | `XA` | `GIUA` | `GAN` | Chữ HUD | Bò |
|---|---|---|---|---|---|---|
| đêm | #003C99 | #0068FF | viền #0068FF | #0068FF | #FFFFFF | (chưa có) |
| ngày | #FFFFFF | #E6F0FF | #E6F0FF | #E6F0FF | #0A0A0A, nhấn #0068FF | #0068FF |
| xanh (GON) | #0068FF | #003C99 | viền #003C99 | #003C99 | #FFFFFF | #FFFFFF |
| RÕ | #FFFFFF | #E6F0FF | #E6F0FF | — | #0A0A0A, nhấn #0068FF | #0068FF |

### 3.3 Thành phần camera

`camAt(t) = base(t) ⊕ trôi(t) ⊕ xung(t)`.
- **base:** nội suy giữa các khóa `CamKey { t, cam, ease, hold?, arcY?, bank? }`. x, y, rot tuyến tính theo tiến độ đã ease; zoom nội suy log; z nội suy theo ln s của lớp đích. Khóa có `hold: { world, screen }` thì x, y tính bằng `camFor`. **Nếu hai khóa liền nhau đều có `hold`, x, y được tính lại ở mỗi t từ điểm ngắm nội suy** (giữ điểm ngắm đứng đúng chỗ trong lúc zoom). Ease `hermite` cho khóa trơn vận tốc (Catmull-Rom). Ease `zoomPath` cho chặng vừa lia vừa zoom lớn (van Wijk–Nuij, ρ = 1,4, §3.4 số 9).
- **trôi:** `dx = ax·sin(2πt/7,3 + φ1)`, `dy = ay·sin(2πt/11,9 + φ2)`, `drot = arot·sin(2πt/17,1 + φ3)`, `zoom ×= 1 + azoom·sin(2πt/9,7 + φ4)`. Mặc định ax 6, ay 3,5 px, arot 0,15°, azoom 0,004; pha từ `random(seed)`. Trôi vi mô không đủ 15 px/s, nên **khóa base không bao giờ đứng**: giữa hai khóa liền nhau luôn có dời ≥ 15 px/s hoặc zoom đổi ≥ 0,4 %/s.
- **xung:** `punch` (zoom ×(1 + A·e^(−Δ/τ)·cos(2π·hz·Δ)), mặc định τ 0,1 s, hz 5), `kick` (rot), `nudge` (bướu dời `d·sin(π·clamp(Δ/dur))`), `zoomBump` (zoom ×(1 + A·sin(π·clamp(Δ/dur)))). Chỉ `punch` và `kick` là cú tác động (tính hạn mức).
- **bank:** chặng có `bank` thì roll += clamp(−0,008·vx; ±1,5°), vx tính bằng px/f60.

### 3.4 Các kiểu move

| # | Kiểu | Khi dùng | Công thức và thông số |
|---|---|---|---|
| 1 | Trôi | luôn bật | §3.3 + khóa base dời 15–25 px/s |
| 2 | Đẩy chậm | lúc đọc, lúc căng trước húc, khóa logo | zoom 1,00 → 1,04–1,10 trong 2–4 s, `EZ.DRIFT` |
| 3 | Kéo ra lộ | mở chương từ một chi tiết | zoom 1,5–3 → 1 trong 1,2–1,8 s, `EZ.OUT`, có `hold` giữ chi tiết (K07) |
| 4 | Lia trạm | đổi cảnh cùng năng lượng | 0,8–1,2 s, `EZ.CAM`, `bank`; phần tử trạm mới vào ở 60–70 % chặng |
| 5 | Whip | đổi chương có năng lượng | Δx ≈ 1 khung (1950 px kể cả lấy đà) trong 0,5 s, `EZ.CAM` (đỉnh ≈ 186 px/f60), arcY +40·sin(πp), `bank`; T2 ở lõi; nội dung đổi ở đỉnh |
| 6 | Bám | theo vật bay, theo Bò | điểm ngắm = vật, spring `CAMERA` (trễ tự nhiên); đặt vật ở đường 1/3 |
| 7 | Đập | đúng 8,0 / 10,0 / 24,5 s | `punch` 1 % / 3 % / 1,5 %; ở 10,0 thêm `kick` 0,5° (τ 0,08, 6 Hz) |
| 8 | Dolly-zoom | 1 lần: 9,2–9,6 s | z 0 → −0,25, zoom bù = s₁·(1 − z) để lớp d = 1 đứng yên; lớp `XA` phóng ×1,14 ("thế giới dồn lại"), `EZ.IN` |
| 9 | Lia kèm zoom lớn | từ thẻ về Bò, từ Bò sang thẻ | van Wijk–Nuij: w = W/zoom; b0 = (w1² − w0² + ρ⁴d²)/(2w0ρ²d), b1 = (w1² − w0² − ρ⁴d²)/(2w1ρ²d), r_i = ln(√(b_i²+1) − b_i), S = (r1 − r0)/ρ; tại s = p·S: u = w0/(ρ²d)·(cosh r0·tanh(ρs + r0) − sinh r0), tâm = P0 + u·(P1 − P0), w = w0·cosh r0 / cosh(ρs + r0) |
| 10 | Lặn xuyên | 1 lần: qua khe trán Bò | §3.5 D |
| 11 | Roll | chỉ banking hoặc trôi thở | ≤ 2°; breath 0 → 0,4° trong 2 s |

### 3.5 Chuyển cảnh (6 kiểu)

**A. Wipe khối màu bằng camera** (dùng ở 1,967 s, đêm → sáng):
- Hai trường màu nằm trên lớp `CHINH`, chung một ranh thẳng qua điểm thế giới B, nghiêng 10° so với phương đứng: hướng ranh u = (sin 10°, cos 10°), pháp tuyến n = (cos 10°, −sin 10°). Phía đêm là (p − B)·n < 0.
- Camera whip qua ranh (kiểu move 5). Ranh trên màn = `project(B ± 2000·u)`, nên ranh quét đúng tốc độ thế giới.
- `FieldSplit` (§8.3) vẽ mọi lớp hai lần, clip theo nửa mặt phẳng: phía đêm dùng kiểu đêm, phía ngày dùng kiểu ngày. Vật đi qua ranh (bong bóng) đổi kiểu đúng chỗ ranh cắt qua nó.
- Đỉnh vận tốc camera lúc ranh qua giữa màn. T2 bật.
- **Dự phòng (K23):** 6 dải khối màu mới quét so le 0,035 s, mỗi dải 0,5 s `EZ.CAM`.

**B. Tràn từ khe** (10,0 s):
- Tâm c = khe Bò ở tư thế chạm, chiếu qua camera ở từng t (`anchorPx` + `project`).
- `r(t) = R·√(easeInOutQuad(p))`, p = (t − t0 + 1/60)/0,367, R = 1,05 × khoảng cách từ c tới góc khung xa nhất.
- Mỗi f60 phủ thêm ≤ 15 % khung: 22 f60 cho tối đa 14,4 % (20 f60 ra 15,2 %, trượt ngưỡng; tính bằng lưới 4 px).
- `FieldSplit` kiểu vòng tròn: trong vòng là thế giới xanh, ngoài là thế giới ngày. Bò hai lớp (`SplitMascot`): xanh ngoài vòng, trắng trong vòng. Dưới vòng đã phủ, đổi cảnh phía sau ("dọn cảnh dưới che phủ").

**C. Biến hình khối từ U** (lòng U nhả ra một khối thành hàng CRM; 11,0–15,0 s, 9 lần):
- Mascot không đổi. Khối mới sinh **bên trong lòng U, nhỏ hơn khe** (rộng 0,6 lần, cao 0,8 lần khe trán), vẽ ở lớp sau Bò (`underlay`) nên chỉ thấy qua lòng U và khe, đúng như vật rơi vào trong thư viện `catch`. Hai mép khe luôn còn thấy.
- Pha 1, [te; te + 0,10): tâm khối đi từ điểm đáy U (`U_BOTTOM`) lên trên đỉnh khe 0,6 lần chiều cao khe, `EZ.OUT`. Khối nằm gọn giữa hai chân sừng.
- Pha 2, [te + 0,10; te + 0,35]: chuyển lên lớp trước. Vị trí theo Bézier bậc 2: P0 là điểm cuối pha 1, P1 = (P0x + 0,35·(P2x − P0x), min(P0y, P2y) − cungᵢ), P2 là tâm slot đầu thẻ. Tiến độ `EZ.CAM`.
  - w = w0 + (W_hàng − w0)·springAt(MORPH); h đi cùng nhưng trễ 0,05 s; bo góc `UI_SNAP`.
  - Xoay theo tiếp tuyến: rot = clamp(0,15·góc vận tốc; ±8°), về 0 khi tới nơi.
  - Đường đi cách silhouette Bò ≥ 24 px (kiểm bằng `markPolygonPx`); đỉnh cung cao hơn ngọn sừng.
  - Nội dung (tên, pill) trồi trong mask riêng khi w đạt 70 %.
- Tới nơi: khối trùng rect hàng (±2 px). Chồng hàng đã dịch xuống từ 0,067 s trước (`track` `UI_SNAP`).
- Biến tấu: cung cao, thấp xen kẽ (cungᵢ = 220 / 300 / 260 / 340 px …), không lặp y hệt.

**D. Zoom xuyên khe trán** (17,033–17,650 s, một lần):
- Khung trước: khe Bò ở (960, 600), Bò cao 620 px (s₁ = 1,107 so với Bò thế giới 560 px). Đặt thấp 60 px để ngọn sừng cách đáy L7 ≥ 40 px.
- p = seg(t; 17,033; 0,35), e = `EZ.ZOOM_THRU`(p).
- Điểm ngắm H(e) = lerp(K khe; Q tâm lòng U; smoothstep(e)); điểm màn của nó trượt (960, 600) → (960, 540) cùng tiến độ: camera chui qua khe xuống lòng U.
- s₁(e) = s_a·(s_b/s_a)^e cho lớp d = 1, lens zoom giữ 1,107, z(e) = 1 − 1,107/s₁(e) (dolly thật: lớp `XA` chỉ lớn ×1,52, lớp `GAN` lao qua rồi ẩn khi d − z ≤ 0,08). roll 0 → 1,5°.
- s_b = 1,05·s_min. s_min là scale nhỏ nhất để cả 4 góc khung nằm trong lòng U (hình chữ nhật bo r = 198,62 vb, nửa rộng 321,38, nửa cao 248,28 vb). Với khung 1920×1080 giải ra Bò cao ≥ 4234 px, tức s_min = 7,56, s_b = 7,94. `cavityFillScale()` tính lại bằng số.
- Lúc mọi góc khung đã nằm trong lòng U (t_in ≈ 17,380 s), khung chỉ còn nền xanh và lớp `XA` #003C99.
- Pha 2, iris: từ 17,383 s, vòng tròn tâm (960, 540) mở thế giới RÕ trong 0,267 s (16 f60, mỗi f60 phủ ≤ 14,6 %; 14 f60 ra 17,3 %, trượt ngưỡng). R = 1,05·√(960² + 540²) = 1156,5. r theo công thức B. Đỉnh whoosh 17,467 s (f60 1048) rơi đúng frame iris phủ thêm nhiều nhất (frame thứ 5–6, khoảng 50 % khung); kín khung ≈ 17,55 s. Trong vòng là thế giới RÕ với camera riêng.
- Camera RÕ vào khi đang chạy: s₁ 0,82 → 1 (`approach` τ 0,2), roll 1,5° → 0. Hướng chuyển động liền (đang lao tới thì cảnh mới tiếp tục lớn lên).
- T2 bật suốt pha 1. Bò chỉ phóng đều, không méo. Iris chỉ bắt đầu sau t_in, nên không có frame nào vẽ gì vào lòng U khi viền Bò còn trong khung.

**E. Match/morph thẻ** (19,9 s: thẻ KK6 nở thành thẻ báo cáo):
- Một khối, một tiến độ: rect đi từ A sang B. x, y, w theo `MORPH`, h theo `MORPH` trễ 0,05 s, bo góc `UI_SNAP`.
- Màu đổi bằng cắt cứng ở 60–70 % đường đi (nếu có đổi màu). Nội dung cũ rút trong mask ở 40 % đầu; nội dung mới vào so le 0,05 s ở 40 % cuối.
- Va chạm nhân quả (K35): vật nằm trên đường mép khối bị đẩy bằng cùng tiến độ, hoàn tất ở 40–50 % (L8, L8b bị mép trên đẩy bay khỏi khung).
- Lệch tâm tại frame khớp ≤ 10 px.

**F. Cắt khớp vận tốc** (dành cho ≤ 2 cắt cứng của cả phim, không dùng trong test):
- Cảnh A rời bằng `EZ.IN` trong T1 = 0,25–0,35 s, cảnh B vào bằng `EZ.OUT` trong T2 = 0,5–1,0 s, cùng hướng.
- Điều kiện D1/T1 ≈ D2/T2. Cắt đúng đỉnh vận tốc; whoosh đạt đỉnh đúng frame cắt.

---

## 4. Chữ động

**Nguồn chữ:** chỉ từ `copy.ts`. `copyGroupsW()` gọi `copyGroupsFor(V2_DEFAULT_PROPS)` rồi đổi enterAt, exitAt từ f30 sang giây. Trong `src\v2w` không có chuỗi tiếng Việt có dấu (lint §8.6).

**Tách:**
- `text.normalize("NFC").split(" ")`. Mỗi từ là một `inline-block`; dấu cách là text node nằm ngoài span (nếu không, từ dính nhau).
- NFC biến mọi chữ tiếng Việt thành một code point dựng sẵn (ầ, ặ, ữ, đ…), nên tách ký tự bằng `Array.from(word)` không bao giờ rời dấu khỏi chữ.
- Không dùng `Intl.Segmenter` (tsconfig lib es2019). Hiệu ứng theo ký tự chỉ cho từ hiển thị ≤ 6 ký tự ("OPA"); câu luôn tách theo từ để giữ kerning Be Vietnam Pro.

**Mask giữ dấu (nới mép trên):**
- Mỗi dòng một wrapper `overflow: hidden`. Mép trên lấn lên **0,24 em**, mép dưới lấn xuống **0,16 em**; `paddingTop` bù đúng 0,24 em, nên vị trí chữ không đổi.
- Lý do: KT đo dấu chồng nhô 0,18 em ở 112 px; vọt 2 % của `CHU` trên quãng trồi chỉ cộng ≤ 0,012 em.
- Line-height 1,32. Chữ gắn thế giới (L8, L8b) dùng cùng mask.

**Vào:**
- Mỗi từ trồi từ dưới mask: y = (1 − springAt(t; t_từ; `CHU`))·1,05·chiều cao mask.
- t_từ = enter + dòng·`STAGGER.line2` (dòng `accent` dùng 0,133) + chỉ số từ·0,06.
- Opacity 0 → 1 trong 0,05 s (từ được "nhét vào khe", không hiện mờ dần).
- Sau chuyển cảnh, chữ thêm trượt x từ +60 px về 0 bằng `approach` τ 0,2, cùng hướng camera vừa đi.

**Giữ:** σ blur = 0. HUD chỉ nhận 0,5 × trôi vi mô. Đọc được = từ cuối đạt ≥ 98 %, phải ≤ 0,45 s sau enter.

**Nhấn nhịp:**
- Dòng `accent` (mới thấy., anh chị., Không bỏ sót khách, có báo cáo.) nảy đúng phách mạnh đầu tiên sau khi khóa: scale = 1 + 0,06·e^(−Δ/0,09)·cos(2π·3Δ), gốc ở baseline trái.
- Mỗi khung tối đa 1 lần nhấn. Không đổi màu theo thời gian.

**Ra (4 kiểu, gán cho từng nhóm ở §5.5):**

| Kiểu | Công thức | Dùng cho |
|---|---|---|
| `mask` | mỗi từ y 0 → −1,1 mask, `EZ.IN` 0,2 s, so le 0,03 s | mặc định |
| `carry` | chữ gắn vào thế giới từ lúc ra: dịch theo Δcam × 1, có T1 blur | L1 trong whip |
| `fling` | bị vật hất: x theo vật hất, `EZ.IN` 0,3 s, xoay tới ±6°, T1 blur (trần 8) | L4 ở HIT (khung văng hất chữ) |
| `push` | bị mép khối đẩy: dịch theo mép từ lúc chạm, rồi `EZ.IN` bay khỏi khung | L8, L8b khi thẻ báo cáo nở |

Bốn nhóm cắt cứng của V2 (L4, L8, L8b, L10) không cắt nữa mà ra bằng `fling`, `push`, hoặc chuyển cảnh mang đi.

**Nét gạch "Bỏ sót khách" (hai mép):**
- Mép trước chạy từ mép phải chữ sang mép trái (phía Bò lao tới) trong 0,267 s bằng `EZ.SCENE`, vọt 4 % rồi về.
- Mép sau đi theo bằng `MEP_SAU`. Dày 0,11 em, #0068FF, nằm giữa chiều cao chữ hoa (như `StrikeThrough` V2).
- Chữ bị gạch nhích 8 px, rung tắt e^(−Δ/0,08)·sin(2π·9Δ).

---

## 5. Bố cục 16:9

### 5.1 Lưới và vùng an toàn

- Lưới 12 cột: lề 96, rãnh 24, cột 122 px. Cột n bắt đầu ở x = 96 + (n − 1)·146. Đường 1/3: x 640 và 1280, y 360 và 720.
- **Vùng an toàn chữ** (mọi chữ, kể cả UI, logo, CTA): trên 65, phải 96, dưới 108, trái 96 (KT §3.6, đề xuất chờ duyệt). Hành động và thế giới tràn khung tự do.
- Không sửa `safeInsets()` (sting 16:9 đang dùng). Bản 16:9 dùng hằng riêng `TEXT_SAFE_W` trong `src\v2w\core\layout.ts`.
- **Chữ và hành động:** chữ ở một nửa (cột 1–6 hoặc 7–12), hành động ở nửa kia. Hộp chữ cách silhouette Bò ≥ 40 px ở mọi frame (kiểm bằng `mascotExtentPx`). Câu một dòng dài (L7, L8b) được chiếm cột 1–9 khi hành động nằm dưới.

### 5.2 Cỡ chữ (map từ `TYPE`)

| Loại | `TYPE` (9:16) | `TYPE_W` (16:9) | Dùng |
|---|---|---|---|
| display | 150 | 180 | "OPA" |
| title | 88 | 112 | lời chính L1–L10 |
| body | 48 | 56 | tên giả trên thẻ báo cáo, tagline |
| caption | 38 | 42 | chữ phụ |
| UI (tên hàng CRM, nhãn pill) | 38 | 48 (UI × 1,25) | hàng CRM, pill |
| lineHeight | 1,32 | 1,32 | |

- Co chữ: dùng `fitSize` của V2. `maxShrink` mặc định 0; L4, L10 tối đa 0,15; L8b tối đa 0,03. Vượt mức thì dừng render với lỗi.
- UI × 1,25 (`UI_W`): radius 35, khung 50, viền 4, viền khung 5, nét đứt "18 12", pill cao 70, hàng 104, chip 56.

### 5.3 Trạm NGÀY (camera (1920, 0), zoom 1; tọa độ màn = thế giới − (1920, 0))

| Vật | Màn | Ghi chú |
|---|---|---|
| `INBOX_W` | trái 96, trên 110, đáy 970; phải = ceil(maxX của Bò ở tư thế chạm) ≈ 877 | bo 50, viền 5 px #0A0A0A, nét "18 12", chạy kiến 30 px/s |
| `HERO_W` | cx 450, cy 600, cao 560 (bbox x 143–757, y 320–880) | Bò trồi ở đây |
| Khe `K_W` | (450, 545); thế giới (2370, 545) | `GAP_CENTER_VB` |
| Tư thế chạm | `charge` với lunge 64,6 px, back 21,5 px (× 560/520), cúi 8° | `INBOX_W.right` tính từ đây |
| Bong bóng khách / shop | x 136, rộng 520, cao 108 / mép phải 837, rộng 330 | khe đáy cy 880, bước 132; 6 bóng: 880 … 220 |
| Ô chữ R1 / R2 | (1000, 230, rộng 824) / (1100, 230, rộng 724) | L1–L3 / L4 |

Trạm ĐÊM (gói T1): cột bong bóng cùng vị trí màn với trạm NGÀY; trường đêm là phần thế giới x < 1920 (ranh nghiêng 10° qua (1920, 540)).

### 5.4 Trạm GON (thế giới xanh)

Camera GON = `camFor(K_chạm, (560, 649), 0,929)` ≈ (1905, −112, zoom 0,929). K_chạm = khe Bò sau cú lao = (2434,6, 545).

| Vật | Màn | Thế giới |
|---|---|---|
| Bò phễu | cx 560, cy 700, cao 520; khe (560, 649), đỉnh khe y 624, đáy U y 878 | HERO + lunge |
| Thẻ CRM (trắng) | (1000, 520, 824, 400): 3 hàng × 104, khe 14, đệm 22 | ≈ (2908, 406, 887, 431) = `screenToWorld(GON_CAM, …)` |
| Ô chữ RT | (1000, 120, rộng 824); L7 dùng ô RTW (640, 110, rộng 1184) | HUD |
| Làn tin vào | mép trái x −140, y ∈ {300, 480, 760, 960}, cung vượt ngọn sừng trái (≈ (293, 440)) rồi rơi vào khe | — |

### 5.5 Trạm RÕ (thế giới riêng sau khi lặn; camera (0, 0))

| Vật | Màn lúc nghỉ | Ghi chú |
|---|---|---|
| L8 trong dải nét đứt | (96, 120), chữ 112, dải viền 3 px #0A0A0A nền trắng | gắn thế giới |
| L8b | (96, 320), một dòng ≈ 1131 px | gắn thế giới, nhấn #0068FF |
| Thẻ KK6 | (96, 520, 924, 380), #E6F0FF, 3 hàng vòng tick | hàng 8, 7, 6 như V2 |
| Thẻ báo cáo | (96, 140, 924, 800), #E6F0FF, 4 hàng × 150, khe 24, đệm 48, tên 56 | hàng 0, 1, 7 tick; hàng 2 pill "Cần gọi lại" từ 23,0 s |
| Bò (lúc gạch) | cx 1560, cy 400, cao 460 | xanh |
| Bò (lúc báo cáo) | cx 1442, cy 720, cao 420 | nhảy cung từ 19,9 s |
| Ô chữ RC | (1060, 120, rộng 764) | L9, L10 (HUD) |

**Gán ô và kiểu ra:**

| Nhóm | Ô | Kiểu ra |
|---|---|---|
| L1 | R1 | `carry` |
| L2, L3 | R1 | `mask` |
| L4 | R2 | `fling` |
| L5, L6 | RT | `mask` |
| L7 | RTW | `mask` |
| L8, L8b | thế giới RÕ | `push` |
| L9, L10 | RC | `mask` |

---

## 6. Mascot: Bò diễn xuyên phim

**Luật (giữ):**
- Không thêm mắt, miệng, chi tiết. Không đổi tỉ lệ. `scaleY` = 1. Không morph, không squash.
- Màu `MASCOT_ON[nền]`: xanh trên trắng và #E6F0FF; trắng trên xanh và #003C99. Ranh màu đi qua Bò thì dùng `SplitMascot` (hai lớp clip).
- Được: dời theo cung (`BO`), phóng đều (camera hoặc placement), xoay cả khối ≤ 8° (như `charge`), blur hướng khi lao, mọi động tác của `src\mascot\motions.ts`.

**Gọi thư viện qua adapter thời gian** (KT §1): `frame30 = t·30`, fps luôn là 30. Không bao giờ truyền fps 60, vì `REVEAL` và `CHARGE` tính bằng frame (gọi thẳng làm sừng mọc sớm).

| Động tác | Hàm v2w | Gọi vào thư viện |
|---|---|---|
| Trồi | `revealW(t, 7.733)` | `reveal(t·30, 30, 232)` |
| Thở | `idleW(t, start, { periodSeconds: 2.0 })` | `idle(…)`, chu kỳ 2,0 s = 1 ô nhịp, khớp nhạc |
| Húc lớn | `chargeW(t, 9.6, { lunge: 64.6, back: 21.5 })` | `charge(t·30, 288, …)` |
| Húc nhẹ | `chargeW(t, 17.7, { direction: -1, lunge: 32, back: 10, tiltDegrees: 5, blurScale: 0.5 })` | `charge` rồi nhân `blurX` |
| Thở phì | `snortPuffW` + `SnortParticlesW` | `snortPuff(…)`; hạt chép đúng toán của `SnortParticles` với thời gian tường minh (component gốc đọc fps của composition, chạy sai ở 60 fps) |
| Nuốt, gật | `pulseW(t, mốc[])` | cùng công thức `catchPulse` (2,5 %, 0,2 s) theo giây |

**Kịch bản vai diễn (cả phim, phần trong test in đậm):**

| Giây | Bò làm gì | Camera làm gì |
|---|---|---|
| 0–7,733 | vắng (câu chuyện) | |
| **7,733–9,2** | trồi trong hộp thư trống (`reveal`, `SPRING_POP`), chạm đáy 8,0, sừng mọc 8,2–8,8, thở phì 8,8 | đẩy vào khe 1,10 → 1,20 |
| **9,2–9,6** | đứng tuyệt đối | dolly-zoom, nền dồn tới |
| **9,6–10,4** | lấy đà, lao, húc văng khung, lắng | đi trước, bám pha lao, đập 3 % |
| **10,4–16,5** | phễu: idle chu kỳ 2 s, nuốt mỗi tin (`pulseW`), lòng U nhả hàng CRM | kéo về GON, trôi, đẩy vào thẻ rồi kéo ra |
| **16,5–17,38** | đứng giữa khung làm cửa | đưa khe vào tâm, lặn xuyên khe |
| **17,4–19,9** | ở thế giới RÕ: húc nhẹ về phía "Bỏ sót khách" đúng lúc nét gạch chạy, thở phì khi "Không bỏ sót khách" khóa, gật ở 19,0 và 19,5 | trôi |
| **19,9–22,5** | nhảy cung xuống cạnh thẻ báo cáo, gật ở mỗi tick 21,0 / 21,5 / 22,0 | bám khối nở, thở |
| 23,6–24,5 | bay cung về giữa, "OPA" khóa 24,5 | dừng lia, đẩy 4 %, đập 1,5 % |
| 24,5–30 | outro: thở; nút CTA `SPRING_POP` lần 2 | thở zoom +0,8 % |

**Đo:** mỗi gói T xuất `boPresence(t)` (Bò có điểm silhouette trong khung và cao ≥ 270 px). Test TS kiểm ≥ 90 % trên [7,733; hết đoạn).

---

## 7. Kịch bản 3 test

**Quy ước:**
- Cột 1 ghi: giây toàn phim (f60 toàn phim · f cục bộ). f cục bộ = f60 − 60·t0. T1: t0 = 0; T2: t0 = 7,5 (f60 450); T3: t0 = 14,5 (f60 870).
- Chữ là lời nguyên văn trong `copy.ts` (biến thể mặc định). Dấu "/" là chỗ xuống dòng của copy.ts.
- Mọi cue lấy từ cues.json (f/30). Ba test cùng một liều (cân bằng). Chưa có lời mới.

### 7.1 T1 "Mở đầu hỗn loạn" [0,0; 8,0) s · f60 0–479 · 480 frame

**Khóa camera T1:**

| t (s) | Khóa | Ease tới khóa sau |
|---|---|---|
| 0,000 | zoom 1,5; hold tâm bong bóng đầu (khe đáy, thế giới đêm) → màn (560, 640) | `EZ.OUT` (kéo ra lộ) |
| 1,650 | zoom 1,0; x −10, y 0 | `EZ.OUT` (lấy đà) |
| 1,717 | x −30 | `EZ.CAM`, arcY 40, bank |
| 2,217 | x 1920, y 0 (= hold K_W → (450, 545)) | `EZ.DRIFT` |
| 4,400 | zoom 1,04; hold K_W → (410, 548) | `EZ.DRIFT` |
| 7,000 | zoom 1,08; hold K_W → (380, 552) | `HANDOFF_12` (§7.4) |

Xung: nudge 4,0 (dx +12, 0,5 s); zoomBump 4,5 (+2 %, 0,6 s); nudge 5,0 / 5,5 / 6,0 / 6,5 (dx −20, 0,6 s); nudge 7,0 (dx −14, 0,6 s).

| Giây (f60 · cục bộ) | Camera | Lớp, phần tử và chuyển động (preset) | Chữ | Chuyển cảnh | Cue trùng |
|---|---|---|---|---|---|
| 0,000 (0 · 0) | mở cận zoom 1,5 rồi kéo ra; trôi | Trường đêm #003C99. `XA` 6 khối #0068FF tự trôi; `GIUA` 3 bong bóng ma viền #0068FF | L1 "Khách nhắn / tối qua…" đang trồi (vào −0,200 s), ô R1, trắng | — | pad Am |
| 0,033 (2 · 2) | | Bong bóng 1 bật ở khe đáy: scale 0,6 → 1 `UI_POP` (gốc ở đuôi), opacity 0 → 1 trong 0,05 s; 2 vạch trễ 0,05 s | | | ping-1 0,033 |
| 0,467 · 1,033 · 1,467 (28 · 62 · 88) | | Bong bóng 2, 3, 4 bật như trên, biên độ bật 0,6 / 0,65 / 0,55. Chồng cũ đẩy lên 132 px bằng `track` `UI_SNAP`, bắt đầu 0,033 s trước khi bật, so le 0,02 s mỗi bóng từ dưới lên | L1 đọc được [0,10; 1,733) | | ping-2 0,467 · ping-3 1,033 · ping-4 1,467 |
| 1,650–1,717 (99–103) | lấy đà x −30 | | L1 ra 1,733–1,933 kiểu `carry` | | |
| **1,717–2,217 (103–133)** | **WHIP** phải 1950 px trong 0,5 s, cung y, bank ≤ 1,5°, đỉnh ≈ 186 px/f60 đúng 1,967; T2 tới 12 mẫu | Ranh đêm/ngày quét phải sang trái. Bong bóng được **mang theo** (cộng Δcam(t) = cam(t) − cam(1,717) nên đứng trên màn, lệch trễ ≤ 40 px, nghiêng theo gia tốc ≤ 3°); bóng đổi kiểu "night" → "missed" theo ranh. `XA`, `GIUA` đổi tông theo ranh. `GAN`: 1 khối 900×700 lướt qua 1,85–2,10 | — | **A. Wipe khối màu** | whoosh-day (clip 1,787–2,087, đỉnh 1,967 = f60 118) |
| 2,000 (120 · 120) | đuôi whip | Hộp thư nét đứt (thế giới ngày) trượt vào ôm chồng bóng, khóa 2,217; viền chạy kiến | L2 "Sáng nay / mới thấy." vào 2,000: mỗi từ trồi + x +60 → 0 (`approach`); "mới thấy." trễ 0,133 | | pad-open 1,967 · motif E5 2,000 |
| 2,000 · 2,250 · 2,500 (120 · 135 · 150) | | 3 bóng "sót" (4, 3, 2) lần lượt rũ xuống 6 px + lắc tắt ±2° 0,35 s, mỗi nốt một bóng | nhấn "mới thấy." ở 2,500 | | motif E5 2,000 · A4 2,250 · C5 2,500 |
| 2,500 (150) | trôi 18 px/s, đẩy 1,00 → 1,04 | Bóng shop "đang gõ" #0068FF bật ở khe đáy phải (`UI_POP`), chồng đẩy lên. 3 chấm nảy sóng (lệch pha 1/3, chu kỳ 0,5 s, 10 px), nhấn thêm ở 3,000 / 3,250 / 3,500 / 3,750 | L2 đọc được [2,333; 4,233) | | (pulse 1/8 trong nhạc) |
| 4,000 (240) | nudge +12 | Shop gửi muộn: chấm rút lên trong khe 0,1 s, 2 vạch trắng trồi 0,15 s (`UI_SNAP`); bóng nhích x +12 rồi về (`UI_POP`) | L2 ra 4,233–4,433 (`mask`) | | tick-reply-1 4,000 |
| 4,500 (270) | zoomBump +2 % về bóng mới | Bóng khách mới #003C99 (vạch trắng) bật ở khe đáy trái; chồng đẩy lên (6 bóng) | L3 "“Chị mua chỗ / khác rồi.”" vào 4,500, ô R1 | | ping-5 4,500 |
| 5,000 · 5,500 · 6,000 · 6,500 (300 · 330 · 360 · 390) | nudge −20 mỗi lần; đẩy 1,04 → 1,08 | b1 → b4 (trên xuống) rời: lấy đà x +16 (0,1 s `EZ.OUT`), rồi bay trái ra khỏi khung (`EZ.IN` 0,35 s, 1300 px), xoay 0 → −8° (luân phiên −6 / −9 / −7 / −10), T1 blur tới σ 8. Bóng dưới không xếp lại | L3 đọc được [4,8; 7,667) | | (build: nhạc dồn) |
| 7,000 (420) | nudge −14 | Khách mới rời trái, shop rời phải cùng lúc (`EZ.IN` 0,35 s, ngược chiều); hộp thư trống từ 7,267 | | | |
| 7,267–7,733 (436–464) | `HANDOFF_12`; từ 7,500 dồn nhanh hơn về chỗ Bò | Hộp thư trống: viền chạy kiến, `XA` trôi | L3 ra 7,667–7,867 | | |
| 7,733 (464) | đẩy 1,10 | Bò trồi `revealW` ở HERO_W, #0068FF: mõm bật (`SPRING_POP` lần 1/2), viền rồi đổ màu từ dưới 0,4 s | L4 "AI trực thay / anh chị." vào 7,933, ô R2 | | — |
| 7,983 (479) | | hết T1: mõm sắp chạm | | | thump 8,000 thuộc T2 |

**Ô 2 s dự kiến:** [0; 2) bật + kéo ra + whip; [2; 4) motif + gõ + trôi; [4; 6) gửi, bóng mới, 2 bóng rời; [6; 8) 2 bóng rời, hộp trống, đẩy, Bò trồi. Không ô nào thiếu chuyển động liên tục.

### 7.2 T2 "Bò húc + flood" [7,5; 14,0) s · f60 450–839 · 390 frame

**Khóa camera T2** (gồm `HANDOFF_12` và `HANDOFF_23`):

| t (s) | Khóa | Ease tới khóa sau |
|---|---|---|
| 7,000–8,200 | `HANDOFF_12` (§7.4) | |
| 9,200 | zoom 1,20; hold K_W → (560, 560); z 0 | dolly-zoom `EZ.IN` |
| 9,600 | z −0,25, zoom 1,50 (s₁ giữ 1,20) | `CAMERA_NHANH` (đi trước) |
| 9,833 | s₁ 1,176; hold K_W → (575, 560) | `EZ.IN` (bám lao) |
| 10,000 | s₁ 1,20; hold (K_W + (39, 0)) → (560, 560) | z về 0 trong 0,367 s (dưới flood), giữ s₁ liền |
| 10,367 | z 0, zoom 1,20 | `EZ.CAM` → hermite |
| 10,900 | GON: zoom 0,929; hold K_chạm → (560, 649) | `EZ.DRIFT` |
| 12,700 | zoom 0,95; hold K_chạm → (520, 652) | `EZ.CAM` |
| 13,200 | zoom 1,06; hold tâm hàng đầu thẻ → (1340, 560) | `EZ.DRIFT` |
| 13,600 | zoom 1,06; hold tâm hàng đầu → (1325, 561) | `HANDOFF_23` |

Xung: punch 8,000 (1 %, τ 0,08); punch 10,000 (3 %, τ 0,1, 5 Hz) + kick 10,000 (0,5°, τ 0,08, 6 Hz).

| Giây (f60 · cục bộ) | Camera | Lớp, phần tử và chuyển động (preset) | Chữ | Chuyển cảnh | Cue trùng |
|---|---|---|---|---|---|
| 7,500 (450 · 0) | `HANDOFF_12` | Hộp thư trống, viền chạy kiến; `XA` #E6F0FF trôi | L3 đang đọc tới 7,667, ra 7,667–7,867 | | |
| 7,733 (464 · 14) | đẩy 1,10 | Bò trồi (như T1) | L4 "AI trực thay / anh chị." vào 7,933 (ô R2) | | |
| **8,000 (480 · 30)** | **đập 1 %** (cú 1/3) | Mõm chạm đáy. `XA` gợn sóng toả từ Bò: mỗi khối +6 px tắt dần, trễ = khoảng cách / 2400 px/s | L4 đọc được [8,267; 10,0) | | thump 8,000 |
| 8,200–8,800 (492–528) | đẩy 1,14 → 1,20 tới 9,2 | Sừng vẽ từ gốc lên ngọn (trong `reveal`) | | | riser 8,200 → 9,733 · esus→E 8,500 · band-drop 8,750 |
| 8,800 (528 · 78) | | Thở phì: `snortPuffW` + `SnortParticlesW` (hạt #0068FF, 0,4 s) | | | snort 8,844 (neo 50 % độ phồng) |
| **9,200–9,600 (552–576)** | **dolly-zoom** (1/phim): z 0 → −0,25, lớp `XA` phóng ×1,14 | Bò REST đứng tuyệt đối (không idle), hộp thư đứng. **Lặng khai báo** | | | riser lên |
| 9,600–9,833 (576–590) | đi trước: s₁ × 0,98, lệch 15 px ngược hướng lao | `chargeW` lấy đà: lùi 21,5 px, cúi 8° | | | whoosh-charge 9,600–9,733 |
| 9,733–10,000 (584–600) | | | | | **LẶNG** (mix −inf) |
| 9,833–10,000 (590–600) | bám pha lao 60 %; T2 khi ≥ 16 px/f60 | Lao 64,6 px (đỉnh vận tốc 9,900), `blurX` của `charge`. 4 vệt tốc độ phẳng #0068FF sau Bò (dài 120–260, dày 8, cách Bò ≥ 20 px), hiện 9,85, co từ đuôi tới 10,08 | | | |
| **10,000 (600 · 150)** | **đập 3 % + kick 0,5°** (cú 2/3) | Sừng chạm mép trong viền phải hộp thư. Hộp thư giãn scaleX 1 → 1,06 (gốc trái, 10,0–10,1 `EZ.OUT`), rồi văng phải 10,1–10,4 (`EZ.IN`, xoay 0 → +10°, T1 blur). Flood #0068FF từ khe, 22 f60 (10,000–10,367). Bò hai lớp (xanh ngoài, trắng trong). Trong vòng: thế giới xanh (`XA` #003C99) | L4 bị khung văng hất (`fling`): bay phải cùng `EZ.IN`, trễ 0,033 s, xoay +6°, T1 blur | **B. Tràn từ khe** | hit-accent + subdrop-accent + brass-stab 10,000 |
| 10,000–10,400 | z về 0 dưới flood | `charge` lắng 0,4 s có rung tắt | | | |
| 10,233 (614) | | Tin 1 xuất hiện ở mép trái (lịch `CATCH`), bay cung vào khe | | | |
| 10,367–10,900 (622–654) | kéo về GON, hermite vào trôi | Thẻ CRM (thế giới) lộ dần từ phải theo camera, tự trượt x +240 → 0 từ 10,500 (`KHOI_NANG`); 3 hàng chờ #E6F0FF so le 0,05 s (không chữ) | L5 "OPA ghi lại / từng khách." vào 10,467, ô RT, trắng | | subdrop còn tới 11,2 |
| 10,400 (624) | | Bò `idleW` từ 10,4, chu kỳ 2,0 s | | | |
| **11,000 · 11,500 · 12,000 · 12,500 (660 · 690 · 720 · 750)** | trôi 22 px/s, đẩy 0,929 → 0,95 | Tin chạm đáy lòng U rồi tan; Bò `pulseW`. +0,05 s: **lòng U nhả khối** bay cung tới slot đầu thẻ, tới nơi ở land + 0,35 s; chồng hàng dịch xuống từ land + 0,283 (`UI_SNAP`); tên + pill "Mới" trồi mask từ land + 0,30. Cung cao/thấp xen kẽ; làn tin đổi mỗi lần | L5 đọc được [10,767; 12,7) | **C. Biến hình khối từ U** | tick-catch 11,0 · 11,5 · 12,0 · 12,5 |
| 12,700–13,200 (762–792) | đẩy vào hàng đầu thẻ, đi trước pill 0,3 s | | L5 ra 12,700–12,900; L6 "Trả lời ngay, / cả ngoài giờ" vào 12,967 (ô RT) | | |
| **13,000 (780 · 330)** | | Pill hàng đầu (Anh Nam, tới 12,85) "Mới" → "Đã trả lời": rộng đổi hai mép (`UI_SNAP` / `MEP_SAU`), màu cắt cứng ở 13,000, chữ cũ rút mask 0,067 s, chữ mới trồi trễ 0,1 s. Hàng 2–3: pill → chip ✓ (`UI_POP`, so le 0,05 s). Land 5 (Chị Thảo, im lặng) | | | tick-reply-2 13,000 |
| 13,350 · 13,500 (801 · 810) | trôi | Chị Thảo vào slot đầu mang "Đã trả lời"; hàng cũ thành chip. Land 6 (Anh Phúc) | L6 đọc được [13,267; 15,2) | | (từ tin 5 không âm) |
| 13,600–14,000 (816–839) | `HANDOFF_23`: kéo về GON rộng | Land 7 (14,000) đang bay | | | |

**Đếm chữ (giống 9:16):** trước 13,0 s: L5 (5) + 3 pill "Mới" (3) = 8. 12,967–13,0: L6 (6) + 3 "Mới" = 9. Từ 13,0: L6 (6) + "Đã trả lời" (3) = 9, các hàng khác là chip. Hàng đang bay chưa có chữ.

### 7.3 T3 "Phễu CRM → gạch nỗi đau → báo cáo" [14,5; 22,5) s · f60 870–1349 · 480 frame

**Khóa camera T3:**

| t (s) | Khóa | Ease tới khóa sau |
|---|---|---|
| 14,400–15,350 | `HANDOFF_23` (§7.4) | |
| 15,850 | zoom 1,04; hold tâm thẻ → (1350, 640) | `EZ.DRIFT` |
| 16,500 | zoom 1,05; hold tâm thẻ → (1330, 642) | `zoomPath` ρ 1,4 |
| 17,033 | s₁ 1,107; hold K_chạm → (960, 600) | lặn (§3.5 D) |
| 17,383 | s₁ 7,94 (z 0,861); hold tâm lòng U → (960, 540); roll 1,5° | (hết GON) |

**Camera RÕ** (thế giới riêng):

| t (s) | Khóa | Ease tới khóa sau |
|---|---|---|
| 17,383 | x 0, y 0, z −0,2195 (s₁ 0,82), roll 1,5° | `approach` τ 0,2 |
| 18,000 | z 0, roll 0, x 11 | `EZ.DRIFT` |
| 19,900 | x 40, zoom 1,03 | `EZ.CAM` |
| 20,450 | x 48, y −40, zoom 0,97 | `EZ.DRIFT` |
| 22,500 | x 79, zoom 0,99, roll 0,4° | |

Xung: nudge 17,9 (dx −10, 0,6 s).

| Giây (f60 · cục bộ) | Camera | Lớp, phần tử và chuyển động (preset) | Chữ | Chuyển cảnh | Cue trùng |
|---|---|---|---|---|---|
| 14,500 (870 · 0) | `HANDOFF_23`: trôi 20 px/s | GON: Bò phễu idle. Land 8 (14,5): tin vào, lòng U nhả → hàng "Chị Mai – cần tư vấn" tới 14,85 | L6 đang đọc tới 15,2 | | (full) |
| 15,000 (900 · 30) | | Land 9 (cuối): "Anh Tùng – hẹn demo" tới 15,35; Bò `pulseW` | L6 ra 15,200–15,400 | | |
| 15,350–15,850 (921–951) | đẩy vào thẻ, đi trước pill 0,15 s | | L7 "Nhắc đội chăm tiếp" vào 15,467 (ô RTW, một dòng) | | |
| **15,500 (930 · 60)** | | Hàng đầu → "Đã nhắc" (15,5), hàng 2 → "Hẹn demo" (15,6): hai mép + màu cắt cứng + chữ đổi trong khe | L7 đọc được [15,667; 17,2) | | (không cue) |
| 16,000 (960 · 90) | | Thẻ "gật": scale 1 → 1,015 → 1 (`UI_POP`); 3 chip nảy sóng so le 0,05 s | | | |
| 16,500–17,033 (990–1022) | đưa khe Bò về (960, 600), Bò cao 620 px (`zoomPath`) | Thẻ ra khỏi khung phải (vẫn trong thế giới) | | | |
| **17,033–17,383 (1022–1043)** | **LẶN XUYÊN KHE**: ngắm trượt khe → tâm lòng U, dolly z 0 → 0,861 (ln s, `EZ.ZOOM_THRU`), roll 0 → 1,5°, T2 12 mẫu | Bò phóng đều ×7,2 rồi ra khỏi khung (ẩn khi không còn điểm nào trong khung). `GAN` #003C99 lao qua rồi ẩn. `XA` #003C99 lớn ×1,52 trong lòng U | L7 ra 17,200–17,400 | **D. Zoom xuyên khe trán** (pha 1) | kick-rest 17,000–17,467 (nhạc lấy hơi) |
| 17,383–17,650 (1043–1059) | camera RÕ bắt đầu: s₁ 0,82 → 1, roll 1,5° → 0 | Iris mở thế giới RÕ (trắng) từ tâm màn, 16 f60, mỗi f60 ≤ 15 % | | **D** (pha 2: iris) | whoosh-thesis (clip 17,287–17,587, đỉnh 17,467 = f60 1048) |
| 17,467 (1048 · 178) | RÕ trôi | RÕ: dải nét đứt chứa L8, thẻ KK6 #E6F0FF (3 hàng vòng tick), Bò xanh (1560, 400, 460); `XA` #E6F0FF. Tất cả đang lao tới (s₁ < 1) | L8 "Bỏ sót khách" (gắn thế giới) | | |
| 17,700–18,100 (1062–1086) | nudge −10 theo Bò | `chargeW` nhẹ hướng trái (lunge 32, cúi 5°, blur × 0,5), đỉnh vận tốc 18,000 | L8 đọc được [17,667; 19,9) | | |
| **18,000 (1080 · 210)** | | Nét gạch #0068FF chạy từ mép phải chữ sang trái 0,267 s (hai mép). Chữ bị đẩy 8 px rung tắt, dải nét đứt lắc ±1,5° | | | (không cue) |
| 18,167 (1090 · 220) | | | L8b "Không bỏ sót khách" (gắn thế giới, nhấn #0068FF) trồi theo từ, khóa 18,5 | | |
| **18,500 (1110 · 240)** | | L8b nhấn scale 1 → 1,06 tắt dần. Bò thở phì (không âm riêng). Tick 1 trên KK6: vòng → chip ✓ (`UI_POP`) + vạch quét #0068FF dưới hàng (hai mép, 0,2 s) | | | tick-thesis + brass-stab 18,500 |
| 19,000 · 19,500 (1140 · 1170) | | Tick 2, 3 như trên; Bò `pulseW` mỗi tick | | | (không cue) |
| **19,900–20,450 (1194–1227)** | bám khối nở: lên 40, zoom 1,03 → 0,97 | **KK6 nở thành thẻ báo cáo**: mép trên 520 → 140, h 380 → 800 (`MORPH`, h trễ 0,05 s, bo `UI_SNAP`). 3 hàng cũ rút mask (40 % đầu); 4 hàng mới (Chị Lan, Anh Khoa, Chị Mai, Chị Hà) so le 0,05 s (40 % cuối). Mép trên đẩy L8, L8b bay khỏi khung. Bò nhảy cung tới (1442, 720, cao 420) (`BO`, đỉnh cung −40 px) | L8, L8b bị đẩy đi 19,90–20,02 (`push`). L9 "Cuối ngày / có báo cáo." vào 19,967 (ô RC) | **E. Match/morph thẻ** | (breath từ 20,000) |
| 20,450–22,500 | thở: trôi 15 px/s, roll 0 → 0,4° | Hàng báo cáo thở 2,5 px lệch pha; Bò idle | L9 đọc được [20,3; 21,967) | | breath (nhạc thưa) |
| 21,000 · 21,500 · 22,000 (1260 · 1290 · 1320) | | Tick trên Chị Lan, Anh Khoa, Chị Mai: chip ✓ `UI_POP` + vạch quét; Bò `pulseW` | L9 ra 21,967–22,167 | | (không cue) |
| 22,233 (1334 · 464) | | | L10 "Không đoán mò." vào (ô RC, co ≤ 15 %) | | |
| 22,483 (1349 · 479) | | hết T3 | | | |

**Đếm chữ:** 15,5: L7 (4) + "Đã nhắc" (2) + "Hẹn demo" (2) = 8. 17,2–17,5: L7 ra xong 17,4, chữ L8 trồi từ 17,467 (dải nét đứt đã có trong iris nhưng còn rỗng): tối đa 4. 18,5: L8 (3) + L8b (4) = 7 (tên trên KK6 không đếm). 19,967: L8, L8b phải hết đếm được (≥ 50 % hộp ra khỏi khung) trước khi từ đầu của L9 hiện ≥ 50 % (≈ 20,03); test TS kiểm từng 1/60 s.

**Vắng Bò:** từ lúc khung lọt hẳn vào lòng U (≈ 17,380) tới lúc iris chạm Bò RÕ (≈ 17,43): dưới 0,1 s.

### 7.4 Đoạn camera dùng chung (gói NỀN, `world\handoff.ts`)

| Đoạn | Khóa |
|---|---|
| `HANDOFF_12` (T1 và T2 cùng dùng) | 7,000: zoom 1,08, hold K_W → (380, 552) · 7,733: zoom 1,10, hold K_W → (450, 556) · 8,200: zoom 1,14, hold K_W → (500, 558) · 9,200: zoom 1,20, hold K_W → (560, 560); ease `EZ.DRIFT` |
| `HANDOFF_23` (T2 và T3 cùng dùng) | 13,600: zoom 1,06, hold hàng đầu → (1325, 561) · 14,400: zoom 0,93, hold K_chạm → (540, 650) · 15,350: zoom 0,94, hold K_chạm → (520, 651); ease `EZ.CAM`, rồi `EZ.DRIFT` |
| `DRIFT_DEFAULT` | ax 6, ay 3,5, arot 0,15°, azoom 0,004, seed "v2w-cam" |

Đoạn chồng [7,5; 8,0) do cả T1 và T2 vẽ: cùng khóa, cùng hằng bố cục, cùng `InboxW`, `MascotW`, `CopyHud`, nên ra hình như nhau. Khi ghép phim đủ, T2 sở hữu từ 7,5 s.

---

## 8. Kiến trúc mã

### 8.1 Thư mục, chủ sở hữu, đợt

Thư mục mới `src\v2w\`. **Không sửa** `src\videos\V2`, `src\mascot`, `src\fx`, `src\ui`, `src\brand`, `src\components` (chỉ import). Không có git: mỗi file có đúng một gói chủ. Mỗi file < 300 dòng, chú thích tiếng Việt ngắn.

| Đợt | Gói | Việc |
|---|---|---|
| 1 | **NỀN** | core, chữ, mascot adapter, UI dùng chung, world, compositions, công cụ, test lõi, lab |
| 2 | **T1, T2, T3** song song (Remotion chờ khóa) | mỗi gói dựng cảnh của mình; T3 dựng 16,5–22,5 s trước, chờ T2 báo `GonSystem` xong mới render cuối |
| 3 | điều phối | xem chéo, gửi 3 MP4 + contact sheet + chỉ số cho chủ dự án |

| Đường dẫn | Chủ | Nội dung |
|---|---|---|
| `src\v2w\core\time.ts` | NỀN | FPS_W 60, LIB_FPS 30, W, H, `f30ToSec`, `secToLib`, `framesOf`, `TestTimeContext`, `useClock` |
| `src\v2w\core\ease.ts` | NỀN | `EZ`, `EZ_P`, `seg`, `lerp`, `clamp01`, `smoothstep`, `logLerp`, `approach`, `quadBezier` |
| `src\v2w\core\spring.ts` | NỀN | `SP`, `springAt`, `track`, `trackLog`, `springInfo` |
| `src\v2w\core\camera.ts` | NỀN | `Cam`, `CamKey`, `CamTrack`, `camAt`, `project`, `unproject`, `layerScale`, `layerTransform`, `camFor`, `camSpeed`, `dollyForScale`, van Wijk |
| `src\v2w\core\World.tsx` | NỀN | `World`, `Layer`, `Hud`, `useCam`, `useTrack` |
| `src\v2w\core\blur.tsx` | NỀN | `BLUR`, `BlurSwitch`, `sigmaFor`, `samplesFor`, `velocityOf`, `DirBlur`, `DirBlurG`, `SubframeBlur` (file **duy nhất** được dùng `filter`/`feGaussianBlur`) |
| `src\v2w\core\split.tsx` | NỀN | `SplitShape`, `clipPathOf`, `FieldSplit` |
| `src\v2w\core\motion.ts` | NỀN | `staggerStarts`, `lagged`, `settleWobble`, `floatIdle`, `decayPulse`, `bump`, `twoEdge`, `reactive` |
| `src\v2w\core\layout.ts` | NỀN | `TEXT_SAFE_W`, `GRID`, `TYPE_W` |
| `src\v2w\text\copyW.ts`, `KineticGroup.tsx`, `CopyHud.tsx`, `StrikeW.tsx`, `words.ts` | NỀN | §4 |
| `src\v2w\mascot\mascotW.ts`, `MascotW.tsx`, `SplitMascot.tsx`, `SnortParticlesW.tsx` | NỀN | §6 |
| `src\v2w\ui\uiW.ts`, `InboxW.tsx`, `CardW.tsx`, `RowW.tsx`, `PillW.tsx`, `ChipW.tsx`, `MessageW.tsx`, `SweepBar.tsx`, `crmState.ts` | NỀN | UI × 1,25 dùng chung T1–T3; trạng thái CRM, KK6, báo cáo theo giây |
| `src\v2w\world\schedule.ts`, `stations.ts`, `handoff.ts`, `tones.ts`, `BackgroundW.tsx` | NỀN | mốc giây, trạm NGÀY/GON, đoạn camera chung, tông, lớp XA/GIỮA/GẦN |
| `src\v2w\tests.ts`, `compositions.tsx`, `lab\LabCamera.tsx` | NỀN | cửa sổ test, `TestShell`, `V2wFolder`, composition `v2w-lab` |
| `src\Root.tsx` (thêm 2 dòng) | NỀN | `import { V2wFolder } from "./v2w/compositions";` + `<V2wFolder />` |
| `package.json` (thêm script) | NỀN | `v2w:lint`, `v2w:test`, `v2w:t1`, `v2w:t2`, `v2w:t3` |
| `scripts\test-v2w-core.ts`, `scripts\v2w-tests.ts` | NỀN | test lõi; in `tests.json` |
| `tools\v2w\build_test.py`, `mux_test.py`, `contact.py`, `metrics.py`, `palette_w.py`, `lint_v2w.py`, `tests\test_metrics.py` | NỀN | §8.5–8.7 |
| `src\v2w\scenes\t1\*`, `scripts\test-v2w-t1.ts` | **T1** | `T1Scene.tsx` (NỀN tạo stub rồi giao), `t1Timeline.ts` (khóa camera, mốc), `NightDay.tsx`, `Bubbles.tsx`, `bubblesState.ts`, `index.ts` |
| `src\v2w\scenes\t2\*`, `scenes\t2\gon\*`, `scripts\test-v2w-t2.ts` | **T2** | `T2Scene.tsx`, `t2Timeline.ts`, `RevealHit.tsx`, `HitFlood.tsx`, `index.ts`; **`gon\GonSystem.tsx`** (stub NỀN rồi giao), `gon\messages.ts`, `gon\eject.ts`, `gon\GonCard.tsx` |
| `src\v2w\scenes\t3\*`, `scripts\test-v2w-t3.ts` | **T3** | `T3Scene.tsx`, `t3Timeline.ts`, `t3Layout.ts` (trạm RÕ), `Dive.tsx`, `RoWorld.tsx`, `StrikeKk6.tsx`, `ReportMorph.tsx`, `index.ts` |

**Giao chủ:** hết đợt 1, NỀN ghi vào báo cáo danh sách stub (`scenes\t1\T1Scene.tsx`, `scenes\t2\T2Scene.tsx`, `scenes\t2\gon\GonSystem.tsx`, `scenes\t3\T3Scene.tsx`, `scenes\tN\index.ts`, `scripts\test-v2w-tN.ts`). Từ đợt 2 các file này thuộc gói T tương ứng. Gói T cần đổi file NỀN thì ghi `contractIssues`, không tự sửa.

### 8.2 API chính xác (NỀN)

```ts
// core/time.ts
export const FPS_W = 60, LIB_FPS = 30, W = 1920, H = 1080;
export type Pt = readonly [number, number];
export type Span = { from: number; to: number };                 // giây, [from, to)
export const inSpan: (t: number, s: Span) => boolean;
export const f30ToSec: (f30: number) => number;                  // f/30
export const secToLib: (s: number) => number;                    // s·30, lẻ được
export const framesOf: (seconds: number) => number;              // Math.round(s·60); CHỈ cho durationInFrames
export const TestTimeContext: React.Context<{ t0: number }>;
export type Clock = { t: number; lib: number; frame: number };
export const useClock: () => Clock;                              // t = t0 + useCurrentFrame()/fps (lẻ dưới Freeze)

// core/ease.ts
export type EaseFn = (x: number) => number;
export const EZ: Record<"OUT" | "OUT_SOFT" | "IN" | "IN_HARD" | "CAM" | "DRIFT" | "ZOOM_THRU" | "SCENE", EaseFn>;
export const EZ_P: Record<keyof typeof EZ, readonly [number, number, number, number]>;
export const seg: (t: number, t0: number, dur: number, ease?: EaseFn) => number;          // 0..1, kẹp
export const lerp: (a: number, b: number, p: number) => number;
export const clamp01: (x: number) => number;
export const smoothstep: (x: number) => number;
export const logLerp: (a: number, b: number, p: number) => number;
export const approach: (t: number, t0: number, from: number, to: number, tau?: number) => number;
export const quadBezier: (p0: Pt, p1: Pt, p2: Pt, q: number) => { p: Pt; tangentDeg: number };

// core/spring.ts
export type SpringSpec = { mass: number; stiffness: number; damping: number };
export const SP: Record<"KHOI_NANG" | "MORPH" | "UI_SNAP" | "UI_POP" | "CHU" | "MEP_SAU" | "BO" | "CAMERA" | "CAMERA_NHANH" | "POP_NHAN", SpringSpec>;
export const springAt: (t: number, t0: number, s: SpringSpec) => number;
export type Change = { at: number; to: number };
export const track: (t: number, from: number, changes: readonly Change[], s: SpringSpec) => number;
export const trackLog: (t: number, from: number, changes: readonly Change[], s: SpringSpec) => number;
export const springInfo: (s: SpringSpec) => { omega: number; zeta: number; overshoot: number; peakT: number; settleT: number };

// core/camera.ts
export type Cam = { x: number; y: number; z: number; zoom: number; rot: number };
export const CAM_REST: Cam;                                      // {0,0,0,1,0}
export type EaseSpec =
  | { kind: "bezier"; p: readonly [number, number, number, number] }
  | { kind: "hermite" }
  | { kind: "zoomPath"; rho?: number }                           // mặc định 1,4
  | { kind: "approach"; tau: number };
export type Hold = { world: Pt; screen: Pt };                    // điểm thế giới (d = 1) → điểm màn
export type CamKey = { t: number; cam?: Partial<Cam>; s1?: number; hold?: Hold; ease?: EaseSpec; arcY?: number; bank?: boolean };
// s1: scale lớp d = 1 mong muốn; có s1 thì z = 1 − zoom/s1 (dolly), zoom giữ theo khóa
export type DriftSpec = { ax: number; ay: number; arot: number; azoom: number; seed: string };
export type Impulse =
  | { kind: "punch"; t: number; amp: number; tau?: number; hz?: number }
  | { kind: "kick"; t: number; deg: number; tau?: number; hz?: number }
  | { kind: "nudge"; t: number; dx: number; dy?: number; dur: number }
  | { kind: "zoomBump"; t: number; amp: number; dur: number };
export type CamTrack = { keys: readonly CamKey[]; drift: DriftSpec; impulses?: readonly Impulse[] };
export const camAt: (t: number, tr: CamTrack) => Cam;
export const driftAt: (t: number, d: DriftSpec) => { dx: number; dy: number; drot: number; dzoom: number };
export const layerScale: (cam: Cam, depth: number) => number;    // zoom·d/(d − z); 0 nếu d − z ≤ 0,08
export const project: (cam: Cam, depth: number, p: Pt) => Pt;
export const unproject: (cam: Cam, depth: number, s: Pt) => Pt;
export const layerTransform: (cam: Cam, depth: number) => string | null;   // null = ẩn (qua camera hoặc s > 40)
export const camFor: (world: Pt, screen: Pt, zoom: number, z?: number) => { x: number; y: number };
export const camSpeed: (t: number, tr: CamTrack) => number;      // px/f60, max 4 góc lớp d = 1, sai phân ±1/120 s
export const dollyForScale: (s1: number, zoom: number, depth?: number) => number;
export const mergeKeys: (...parts: ReadonlyArray<readonly CamKey[]>) => CamKey[];   // ghép + sắp, lỗi nếu trùng t

// core/World.tsx
export type WorldProps = { track: CamTrack; background: string; clip?: string; children: React.ReactNode };
export const World: React.FC<WorldProps>;  // AbsoluteFill overflow hidden + nền đục + SubframeBlur(samplesFor(camSpeed)) + context camera
export const Layer: React.FC<{ depth: number; children: React.ReactNode }>;
export const Hud: React.FC<{ track: CamTrack; children: React.ReactNode }>;   // ngoài World; dịch 0,5·drift
export const useCam: () => Cam;
export const useTrack: () => CamTrack;

// core/blur.tsx
export const BLUR: { vMin: 8; perV: number /* 1/6 */; cap: 8; capWhiteOnBlue: 4; camMin: 16; samplesMax: 12; sampleStep: 6; shutter: 0.5 };
export const BlurSwitch: React.Context<boolean>;                 // prop `blur` của TestShell; false = ảnh tham chiếu QA
export const sigmaFor: (v: number, o?: { cap?: number; reading?: boolean }) => number;
export const samplesFor: (vCam: number) => number;
export const velocityOf: (pos: (t: number) => Pt, t: number) => Pt;        // px/f60, sai phân lùi 1/60 s
export const DirBlur: React.FC<{ v: Pt; cap?: number; reading?: boolean; children: React.ReactNode }>;   // HTML
export const DirBlurG: React.FC<{ v: Pt; cap?: number; children: React.ReactNode }>;                     // trong <svg>
export const SubframeBlur: React.FC<{ samples: number; shutter?: number; children: React.ReactNode }>;

// core/split.tsx
export type SplitShape =
  | { kind: "halfPlane"; a: Pt; b: Pt }                          // màn; "trong" = bên trái hướng a→b
  | { kind: "circle"; c: Pt; r: number };
export const clipPathOf: (s: SplitShape, side: "in" | "out") => string;    // polygon / circle / path(evenodd, …)
export const FieldSplit: React.FC<{ shape: SplitShape | null; render: (side: "in" | "out") => React.ReactNode }>;

// core/motion.ts
export const staggerStarts: (t0: number, n: number, gap?: number, ratio?: number) => number[];
export const lagged: <T>(fn: (t: number) => T, t: number, lag?: number) => T;
export const settleWobble: (t: number, t0: number, amp?: number) => number;          // độ
export const floatIdle: (t: number, phase: number, amp?: number, period?: number) => number;
export const decayPulse: (t: number, t0: number, amp: number, tau?: number, hz?: number) => number;
export const bump: (t: number, t0: number, dur: number) => number;                   // sin(π·p)
export const twoEdge: (t: number, t0: number, from: number, to: number) => { lead: number; trail: number };
export const reactive: (p: number, done?: number) => number;                         // tiến độ vật bị đẩy, xong ở 0,45

// text/copyW.ts, KineticGroup.tsx, CopyHud.tsx, StrikeW.tsx, words.ts
export type GroupId = "L1" | "L2" | "L3" | "L4" | "L5" | "L6" | "L7" | "L8" | "L8b" | "L9" | "L10";
export type ExitMode = "mask" | "carry" | "fling" | "push";
export type TextSlot = { left: number; top: number; width: number; size: number; maxShrink: number };
export type CopyGroupW = { id: GroupId; enter: number; exit: number; lines: LineSpec[]; exitMode: ExitMode; world: boolean;
  slot: TextSlot; strike?: { line: number; at: number; dur: number } };
export const TEXT_SLOTS: Record<GroupId, TextSlot>;
export const copyGroupsW: () => CopyGroupW[];                    // copyGroupsFor(V2_DEFAULT_PROPS), f30 → giây
export const MASK_EM: { top: 0.24; bottom: 0.16 };
export const splitWords: (text: string) => string[];
export const wordStart: (g: CopyGroupW, line: number, word: number) => number;
export type ExitDrive = { vector: (t: number) => Pt; from: number };          // fling/push/carry do cảnh cấp
export const KineticGroup: React.FC<{ group: CopyGroupW; color: string; accentColor: string; exit?: ExitDrive; v?: (t: number) => Pt }>;
export const CopyHud: React.FC<{ track: CamTrack; bgAt: (t: number) => BrandColor; exits?: Partial<Record<GroupId, ExitDrive>> }>;
export const StrikeW: React.FC<{ at: number; dur: number; dir: 1 | -1; widthPx: number; sizePx: number }>;
export type ScreenWordW = { text: string; kind: "copy" | "ui" | "fakeName"; source: string; visible: number /* 0..1 */ };
export const copyWordsAt: (t: number) => ScreenWordW[];
export const countVisibleWords: (words: readonly ScreenWordW[]) => number;   // countWords của copy.ts, bỏ fakeName, visible ≥ 0,5

// mascot/mascotW.ts, MascotW.tsx, SplitMascot.tsx, SnortParticlesW.tsx
export const revealW: (t: number, start: number) => PoseDelta;
export const revealEndW: (start: number) => number;
export const idleW: (t: number, start: number, o?: IdleOptions) => PoseDelta;        // periodSeconds mặc định 2.0
export const chargeW: (t: number, start: number, o?: ChargeOptions & { blurScale?: number }) => PoseDelta;
export const snortPuffW: (t: number, start: number) => PoseDelta;
export const pulseW: (t: number, times: readonly number[], amp?: number, dur?: number) => PoseDelta;
export const poseW: (...d: PoseDelta[]) => MascotPose;                               // = combine
export const ANCHOR_VB: { gapCenter: Pt; gapTop: Pt; uBottom: Pt; cavityCenter: Pt;
  gapRect: { x: number; y: number; w: number; h: number }; cavityRect: { x: number; y: number; w: number; h: number; r: number } };
export const anchorPx: (p: Placement, pose: MascotPose, vb: Pt) => Pt;              // = mascotPointPx
export const cavityFillScale: (frame?: { w: number; h: number }) => number;         // s_min (§3.5 D)
export const MascotW: React.FC<Placement & { pose: MascotPose; bg: BrandColor; v?: Pt; underlay?: React.ReactNode; overlay?: React.ReactNode }>;
export const SplitMascot: React.FC<Placement & { pose: MascotPose; shape: SplitShape; inBg: BrandColor; outBg: BrandColor;
  underlay?: React.ReactNode; overlay?: React.ReactNode }>;
export const SnortParticlesW: React.FC<{ t: number; start: number; color: string; perCluster?: number }>;

// ui/crmState.ts
export const EJECT_DELAY = 0.05, ROW_FLIGHT = 0.35;
export type CrmRowW = { index: number; name: string; channel: Channel; slot: number; y: number; arriveAt: number;
  status: RowStatus; statusAt: number };
export const crmRowsW: (t: number) => CrmRowW[];      // trạng thái theo slot như V2: <13,0 "Mới"; 13,0–15,5 slot 0 "Đã trả lời"; ≥15,5 "Đã nhắc"/"Hẹn demo"
export type CardRowW = { index: number; name: string; channel: Channel; status: RowStatus; tickAt?: number };
export const kk6RowsW: (t: number) => CardRowW[];     // hàng 8, 7, 6; tick 18,5 / 19,0 / 19,5
export const reportRowsW: (t: number) => CardRowW[];  // hàng 0, 1, 7 tick 21,0 / 21,5 / 22,0; hàng 2 pill từ 23,0
export const uiWordsAt: (t: number, cards: ReadonlyArray<"crm" | "kk6" | "report">) => ScreenWordW[];

// world/schedule.ts: mọi mốc giây suy từ src/videos/V2/timeline.ts (không gõ số)
export const S: { NIGHT_POPS: number[]; CUT_DAY: number; SHOP_TYPING_AT: number; TYPING_DOTS: number[]; REPLY_LATE_AT: number;
  QUOTE_AT: number; LEAVE: number[]; LEAVE_LAST: number; INBOX_EMPTY: number; REVEAL_AT: number; REVEAL_CONTACT: number;
  HORNS: Span; SNORT_AT: number; SNORT_ANCHOR: number; STILL: Span; CHARGE_AT: number; LUNGE_AT: number; LUNGE_PEAK: number;
  SILENCE_PRE_HIT: Span; HIT: number; IDLE_AT: number; CATCH_SPAWNS: number[]; CATCH_LANDS: number[]; CARD_IN: number;
  PILL_ANSWERED_AT: number; PILL_REMIND_AT: number; BADGE_AT: number; KICK_REST: Span; CUT_THESIS: number; STRIKE: Span;
  THESIS_IN: number; THESIS_LOCK: number; KK6_TICKS: number[]; CUT_REPORT: number; REPORT_TICKS: number[];
  PILL_CALLBACK_AT: number; OUTRO_AT: number; LOGO: number };
export const cueSec: (id: string) => number;           // đọc cues JSON, f/30

// world/stations.ts, handoff.ts, tones.ts, BackgroundW.tsx
export const DAY_CAM: Cam; export const GON_CAM: Cam;
export const HERO_W: Placement; export const CONTACT_POSE_W: MascotPose; export const INBOX_W: Rect;
export const K_W: Pt; export const K_CHAM: Pt; export const CAVITY_CENTER_W: Pt;
export const BO_GON: { placement: Placement /* thế giới */; screen: Pt; zoom: number };
export const CRM_CARD_W: Rect;
export const screenToWorld: (cam: Cam, r: Rect) => Rect;
export const HANDOFF_12: readonly CamKey[]; export const HANDOFF_23: readonly CamKey[]; export const DRIFT_DEFAULT: DriftSpec;
export type Field = "night" | "day" | "blue" | "ro";
export const FIELD_BG: Record<Field, BrandColor>;
export const FIELD_TONE: Record<Field, { far: BrandColor; mid: BrandColor; near: BrandColor; text: BrandColor }>;
export type Ripple = { t: number; center: Pt; amp: number };
export const FarShapes: React.FC<{ field: Field; seed: string; span: Rect; density?: number; ripples?: readonly Ripple[]; growAt?: (t: number) => number }>;
export const MidShapes: React.FC<{ field: Field; seed: string; span: Rect }>;
export const NearBlock: React.FC<{ rect: Rect; color: BrandColor }>;

// tests.ts
export type TestId = 1 | 2 | 3;
export type SceneDef = { Scene: React.FC; track: CamTrack; declared: readonly Span[]; keyStills: readonly number[];
  boPresence: (t: number) => boolean; screenWords: (t: number) => ScreenWordW[] };
export type TestWindow = { n: TestId; id: "v2w-test-1" | "v2w-test-2" | "v2w-test-3"; from: number; to: number };
export const TEST_WINDOWS: readonly TestWindow[];       // (1, 0,0, 8,0) · (2, 7,5, 14,0) · (3, 14,5, 22,5)
export const SCENES: Record<TestId, SceneDef>;          // import T1_SCENE, T2_SCENE, T3_SCENE từ scenes/tN/index.ts

// compositions.tsx
export type TestShellProps = { n: TestId; guides: boolean; blur: boolean };
export const TestShell: React.FC<TestShellProps>;       // TestTimeContext {t0: from} + BlurSwitch + Scene + lưới/vùng an toàn khi guides
export const V2wFolder: React.FC;                       // <Folder name="OPA-V2-16x9">
```

**Hợp đồng gói T** (`src\v2w\scenes\tN\index.ts`): `export const TN_SCENE: SceneDef`. `Scene` không nhận prop; mọi thứ theo `useClock().t` (giây toàn phim), nên ghép phim đủ sau này không phải viết lại.

**Hợp đồng T2 → T3** (`src\v2w\scenes\t2\gon\GonSystem.tsx`):

```ts
export const GON_SPAN: Span;                             // { from: 10.0, to: 17.3 }
export const GonSystem: React.FC;                        // vẽ TRONG <World>: tin bay, Bò phễu, khối nhả từ lòng U, thẻ CRM
export const gonBoAt: (t: number) => { placement: Placement; pose: MascotPose };   // thế giới; T3 dùng để ngắm khe
export const gonWordsAt: (t: number) => ScreenWordW[];
```

Stub của NỀN vẽ Bò phễu + thẻ CRM rỗng, đúng chữ ký. T3 làm việc trên stub; render cuối sau khi T2 báo xong.

### 8.3 Luật code trong `src\v2w`

- Mọi chuyển động là hàm thuần của `t` (giây, lẻ). Không `Math.random`, `Date`, `useState` (trừ `useFontsReady` có sẵn), không `useRef` tích lũy.
- Không `Math.floor`/`Math.round` trên thời gian (trừ `framesOf` cho `durationInFrames`).
- Không `<Sequence>`/`<Series>` trong cảnh: bật tắt bằng điều kiện t.
- Không `interpolateColors`; đổi màu bằng cắt cứng.
- Không gradient, shadow, glow, backdrop, `will-change`, CSS 3D. Không `@remotion/motion-blur`.
- `filter` chỉ trong `core\blur.tsx`. Màu chỉ từ `COLORS`. Chữ chỉ từ `copy.ts`.
- tsconfig lib es2019: không `Intl.Segmenter`, không `replaceAll`, không `.at()`.

### 8.4 Compositions

| id | Kích thước | fps | durationInFrames | defaultProps |
|---|---|---|---|---|
| `v2w-test-1` | 1920×1080 | 60 | `framesOf(8.0)` = 480 | `{ n: 1, guides: false, blur: true }` |
| `v2w-test-2` | 1920×1080 | 60 | `framesOf(6.5)` = 390 | `{ n: 2, guides: false, blur: true }` |
| `v2w-test-3` | 1920×1080 | 60 | `framesOf(8.0)` = 480 | `{ n: 3, guides: false, blur: true }` |
| `v2w-lab` | 1920×1080 | 60 | 240 | lab của NỀN: whip có parallax + T2, flood chia hai lớp, `reveal` qua adapter, L8b có mask, iris |

### 8.5 Render, cắt âm, mux

Một lệnh cho mỗi test: `cmd /c --% python tools\v2w\build_test.py 2`. Script gọi các bước sau bằng `subprocess` danh sách tham số (không shell, nên không vướng `|`):

1. **Cửa sổ:** `node node_modules\tsx\dist\cli.mjs scripts\v2w-tests.ts` in `out\v2-16x9\tests\tests.json` (from, to, declared, keyStills, frames).
2. **Render câm:** `python tools\remotion_run.py render v2w-test-2 out\v2-16x9\tests\test-2-muted.mp4 --muted --codec=h264 --jpeg-quality=95 --crf=16`.
3. **Cắt âm đúng giây** (atrim theo mẫu, 10 ms fade hai đầu chống click, chỉ cho clip test):
   `ffmpeg -hide_banner -y -i public\audio\v2-khong-bo-sot-khach-master.wav -af atrim=start=7.5:end=14.0,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.01,afade=t=out:st=6.49:d=0.01 -c:a pcm_s16le -ar 48000 out\v2-16x9\tests\test-2.wav`
4. **Mux:** `ffmpeg -hide_banner -y -i out\v2-16x9\tests\test-2-muted.mp4 -i out\v2-16x9\tests\test-2.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 320k -ac 2 -movflags +faststart out\v2-16x9\tests\test-2.mp4`
5. **ffprobe:** h264 1920×1080, `r_frame_rate` 60/1, `nb_read_frames` đúng 480 / 390 / 480; |thời lượng âm − hình| < 1/60 s. Sai thì exit 1.
6. **Contact sheet:** `python tools\v2w\contact.py out\v2-16x9\tests\test-2.mp4 --t0 7.5 --every 0.5 --out out\v2-16x9\tests\test-2_contact.png`. Một ô mỗi phách, ô 480×270, nhãn "t = giây toàn phim · f60".
7. **Still khóa:** ffmpeg cắt từ MP4 các mốc `keyStills` → `out\v2-16x9\tests\stills\test-2_t<giây>.png`.
8. **Chỉ số:** `python tools\v2w\metrics.py out\v2-16x9\tests\test-2.mp4 --t0 7.5 --declared 9.2:9.6 --json … --md …`; rồi `palette_w.py` trên ảnh contact.

Exit 0 khi mọi bước đạt; exit 1 khi chỉ số trượt ngưỡng; exit 2 khi thiếu file. Thời gian ước 15–40 s render mỗi test (KT §4). Remotion chỉ chạy qua `tools\remotion_run.py` (có khóa).

### 8.6 Lint và test

- `tools\v2w\lint_v2w.py`: quét `src\v2w`, bỏ chú thích. Luật: hiệu ứng cấm (§8.3), `filter`/`feGaussianBlur` ngoài `core\blur.tsx`, hex ngoài `COLORS`, chữ tiếng Việt có dấu trong mã, `<Sequence`, `Math.floor|Math.round` ngoài allowlist, `from={số`, `durationInFrames={số`, tên cấm (Zalo, Messenger, Facebook, "bạn"). Dòng có `// qa-allow: <lý do>` được bỏ qua.
- `scripts\test-v2w-core.ts` (NỀN):
  1. Bảng spring khớp §2.2 ±0,2 % vọt.
  2. Adapter: ở f60 chẵn, `revealW`, `chargeW`, `idleW` trùng tuyệt đối pose V2 ở f30.
  3. Camera: parallax 1/d; `camFor` đặt đúng điểm (±0,01 px); khóa hai `hold` giữ điểm ngắm đứng (±0,5 px) trong lúc zoom.
  4. `camSpeed` đối xứng; `sigmaFor` và `samplesFor` đúng ngưỡng.
  5. `copyGroupsW` = `copyGroupsFor(V2_DEFAULT_PROPS)` /30.
  6. `cavityFillScale` ≈ 7,56.
  7. `FieldSplit` clip đúng phía.
- `scripts\test-v2w-tN.ts` (gói T), lấy mẫu mỗi 1/60 s trên cửa sổ test:
  1. ≤ 9 chữ (`countVisibleWords(screenWords(t))`).
  2. Hộp chữ cách silhouette Bò ≥ 40 px.
  3. Khóa camera liền vận tốc: nhảy ≤ 2 px/f60 ở chỗ nối, trừ xung khai báo.
  4. `boPresence` ≥ 90 % trên [7,733; hết đoạn).
  5. Mọi vật dùng `DirBlur`/`MascotW` có `v` lấy từ hàm vị trí thật.
  6. Mốc sự kiện hình khớp cue ±1 f60.

### 8.7 Script đo chuyển động (`tools\v2w\metrics.py`)

- Đọc MP4 bằng ffmpeg (`-vf scale=960:540,format=gray -f rawvideo`, pipe trong Python), numpy.
- Tính theo §1: Tĩnh B, Tĩnh A (f so f − 2), chuỗi Tĩnh B dài nhất, cắt cứng (f so f − 1 + luật hàng xóm), % khung đổi trung bình.
- **Độ dời:** optical flow Farneback (OpenCV, nếu không có thì bỏ và ghi WARN) trên frame có đổi; p50 và p99 độ lớn, quy về px khung gốc mỗi f60.
- Theo ô 2 s căn giây chẵn toàn phim (`--t0` đổi f cục bộ sang giây). Frame trong `--declared` bị loại khỏi ngưỡng nhưng vẫn báo.
- **Ngưỡng FAIL:** ô có Tĩnh B > 15 %; cả đoạn > 10 %; Tĩnh A > 0; chuỗi > 12 f60; cắt cứng > 0.
- **Báo, không chặn:** flow p50/p99 mỗi ô, % đổi trung bình, so sánh với số 9:16 (Tĩnh B 57,6 %).
- **Đầu ra:** `test-N_metrics.json` (`{ test, t0, frames, windows: [{ from, to, tinhB, tinhA, meanChanged, flowP50, flowP99, longestRun }], hardCuts, declared, pass, fails }`) và `test-N_metrics.md`.
- `palette_w.py`: mỗi điểm ảnh phải nằm cách một token hoặc **đoạn thẳng nối hai token** ≤ 8/255 (khử răng cưa và blur trộn hai màu; KT §2.6). FAIL khi > 2 % điểm lệch. Vùng phẳng (3×3 chênh ≤ 6) xa token > 4 mức ghi WARN.
- `tools\v2w\tests\test_metrics.py`: video tổng hợp (đứng yên → Tĩnh 100 %; trôi 20 px/s → 0 %; một frame đổi 90 % → 1 cắt cứng).

### 8.8 Nghiệm thu

**NỀN:**
- tsc, eslint `src\v2w`, `lint_v2w.py`, `test-v2w-core.ts`, `test_metrics.py`: exit 0.
- `v2w-lab` render, metrics đạt; `palette_w.py` đạt; still L8b ở 112 px cho thấy Ầ Ổ Ữ ặ đ không bị cắt.
- `npm run regress:sting` vẫn PASS (Root.tsx có đổi).
- Báo cáo JSON có danh sách stub giao chủ.

**T1, T2, T3:**
- `python tools\v2w\build_test.py N` exit 0, ra `out\v2-16x9\tests\test-N.mp4`, `test-N_contact.png`, `test-N_metrics.json`/`.md`, `stills\`.
- `test-v2w-tN.ts` exit 0.
- Báo cáo `{wp, status, files, metrics, contractIssues}`.

**Điều phối:** ba MP4 cùng liều, đặt cạnh nhau với bảng chỉ số và 9:16 để chủ dự án chọn.

---

## 9. Điểm cần chủ dự án duyệt khi xem test

1. Vùng an toàn chữ 16:9: 65 / 96 / 108 / 96; cỡ chữ 180 / 112 / 56 / 42.
2. Motion blur trộn hai màu token dọc vệt (giống khử răng cưa), chỉ khi nhanh.
3. Camera phóng Bò đều tới khoảng ×7 khi lặn xuyên khe (không méo, vài frame).
4. Khối hàng CRM nhả từ lòng U qua khe trán (khối nhỏ hơn khe, mascot không đổi).
5. Bò thêm hai cử chỉ không âm riêng ở chương RÕ: húc nhẹ lúc gạch (17,7 s), thở phì khi câu chốt khóa (18,5 s). Nét gạch chạy phải sang trái theo hướng Bò lao.
6. Bốn nhóm chữ cắt cứng của 9:16 nay ra bằng hất/đẩy/chuyển cảnh mang đi.
7. Đêm → sáng bằng whip qua ranh màu; chương RÕ mở bằng lặn xuyên khe + iris, thay hai cắt cứng cũ.
8. Mức liều: cả 3 test ở mức cân bằng. Nếu thấy quá tay hoặc còn hiền, chỉnh ở `core\ease.ts`/`spring.ts`/`handoff.ts` (biên độ trôi, vọt, cú đập) rồi render lại.

**Rủi ro đã biết:**
- `SubframeBlur` đòi mọi thứ bên trong thuần theo t lẻ; một state làm các mẫu lệch nhau.
- Chữ dài ở ô hẹp (L4, L10) phụ thuộc số đo thật: vượt `maxShrink` thì render dừng, gói T báo `contractIssues`.
- Các số px bố cục ở §5 là điểm xuất phát; gói T chỉnh trong giới hạn luật (khoảng cách chữ–Bò, vùng an toàn) và ghi lại.
