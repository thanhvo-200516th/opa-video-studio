# BỘ PROMPT GOOGLE OMNI FLASH & MOTION CONTROL (AFTER EFFECTS) — KỊCH BẢN SỐ 1 (ADS #1)

> **Dự án**: OPA Agent — AI Bán Hàng Cho Shop Dùng Pancake  
> **Kịch bản gốc**: `VIDEO 01 · Ads #1 (Flagship - 36s)` từ `https://opa-agent-video-roadmap-pitch.vercel.app/`  
> **Project After Effects tham chiếu**: `/media/vmiz/Over Powers/video AE/template intro/video edit teamplate/template 5.aep` (`Final_4k (3840 x 2160)`)  
> **Sản phẩm render mẫu**: `/media/vmiz/Over Powers/EDIT ADOBE/videointro/Final_4k (3840 x 2160)\o ping.mp4` (`3840×2160`, `30 fps`, `55.5s`)  
> **Kiến trúc Motion Control kế thừa**: `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude` (`PROMPT-PACK-OMNI-FLASH.md`, `KICH-BAN-OMNI-FLASH.md`, `PHAN-TICH-3-MAU.md`, `BAO-CAO-PHAN-TICH.md`, `PROMPT-HOAN-CHINH-OPUS.md`, `KET-LUAN-VA-PROMPT-SUA.md`, `KHUNG-DUNG.md`)

---

## PHẦN 1: GIẢI MÃ KIẾN TRÚC AFTER EFFECTS TỪ ẢNH CHỤP (`template 5.aep`) & VIDEO MẪU (`o ping.mp4`)

### 1.1. Cấu trúc cây Pre-comp trong `template 5.aep` (`Final_4k (3840 x 2160)`)
Trên ảnh chụp màn hình tại timecode `0:00:19:03` và file render mẫu `o ping.mp4`, project After Effects được tổ chức theo **Pre-comp lồng 4 tầng (Nested Pre-compositions)** kết hợp **Global Control Layers**:

```text
Final_4k (3840 x 2160) [3840×2160 | 30 fps | Anchor: 1920.0, 1080.0 | Pos: 1920.0, 1080.0 | Scale: 100%, 100% | Rot: 0x+0.0°]
 ├── # Global Controllers (Adjustment / Guide / Null Layers đầu timeline):
 │    ├── 1. Text Colors                   (Expression Control đổi màu chữ toàn cục)
 │    ├── 2. Background Colors             (Màu nền #0A142E / #FFFFFF / Gradient Blue)
 │    ├── 3. Icons, Buttons & UI Colors    (Màu pill, viền sáng EdgeGlow #2690FF / #1E40FF)
 │    ├── 4. Camera_Control                (Master Null 3D điều khiển Zoom/Pan/Parallax toàn cảnh)
 │    └── 5. Num_Control                   (Slider Control đếm số tự động: 268, 311, 159.000đ)
 │
 └── # Scene Pre-comps (Cắt theo nhịp 120 BPM = 15 frames/beat @ 30fps):
      └── 05_Scene (00:15:00 – 00:26:15)   [Cảnh khung chat 3D nghiêng đang mở trên ảnh chụp]
           ├── 05_Scene_Text01             (Header trên: "Tự trả lời khách theo tồn kho" -> H04 Word/Line Swap)
           ├── 05_Scene_Button02           (Pre-comp khung thẻ UI / Pill / Bubble)
           │    └── 05_Scene_Text02        (Layer chữ bên trong nút/bong bóng chat)
           ├── Chat_Card_3D                (3D Layer: Y Rotation +35° -> 0°, Z Position đẩy lùi, viền EdgeGlow)
           └── BG_Glow_Grid                (Lưới sáng mờ + Radial Glow chuyển động chậm)
```

### 1.2. Nguyên lý Vật lý & 5 Thông số Transform cốt lõi từ `Motion Claude` áp vào `Kịch bản số 1`

Để Google Omni Flash (hoặc After Effects) tạo ra chuyển động **mượt như sản phẩm mẫu `o ping.mp4`** và không bị "đơ hình" (47.8% khung tĩnh ở bản cũ), mọi chuyển động phải tuân thủ **5 thông số Transform + Đồ thị vận tốc (Graph Editor)**:

| Thông số AE | Quy chuẩn trong `Final_4k (3840×2160)` (Pixel) | Quy chuẩn trong Prompt Omni Flash (`%` & Ngôn ngữ tự nhiên) | Quy tắc Vật lý & Easing bắt buộc |
| :--- | :--- | :--- | :--- |
| **1. Anchor Point (Điểm neo `A`)** | • Comp / Card trung tâm: `[1920, 1080]`<br>• Bong bóng chat khách (trái): Góc dưới-trái `[0, H]`<br>• Bong bóng chat OPA (phải): Góc dưới-phải `[W, H]`<br>• Đầu Bò OPA (`U_HEAD`): Đáy giữa `[50%, 100%]`<br>• Gốc sừng trái/phải: `[22.6%, 42.1%]` & `[77.4%, 42.1%]`<br>• Form/Card bung mở: Đỉnh-trái `[0, 0]` hoặc Tâm `[W/2, H/2]` | • Luôn khóa điểm neo trước khi Scale/Rotate.<br>• Trong prompt Omni Flash: Mô tả bằng vị trí vật lý (*"from its bottom-left tail corner"*, *"from a single point at its bottom-center"*, *"around each horn's root where it joins the head"*) để AI không vẽ số tọa độ lên hình. | **Sai lầm phổ biến nhất**: Để Anchor Point ở giữa `[50%, 50%]` khi bung bong bóng chat hoặc xoay sừng làm hình bị trượt (floating pivot). |
| **2. Position (Vị trí `P`)** | • Tách X/Y (`Separate Dimensions`) hoặc 3D `[X, Y, Z]`<br>• Bước cuộn tin nhắn (Step-scroll): `ΔY = -210 px` (4K) mỗi khi có tin mới.<br>• Text Reveal (R1/H02): Trượt ngang hoặc trượt dọc qua `Alpha Track Matte` (`ΔY = +120 px -> 0 px`). | • Hệ tọa độ `(x%, y%)` với `(0%, 0%)` là góc trên-trái, `(50%, 50%)` là tâm khung hình.<br>• Tách bạch **Local Position** (vật thể tự trượt) và **Camera Null (`CAM`) Position** (khung hình đẩy tới). | **Rule R1 (Text Slide)**: `Out Influence 75.2% / In Influence 75.1%` (`cubic-bezier(0.75, 0, 0.25, 1)`).<br>**Rule R10 (Card/Mask Wipe)**: `Out Influence 15.2% / In Influence 100%` (`cubic-bezier(0.15, 0, 0, 1)` — vọt nhanh đầu, đáp cực êm). |
| **3. Scale (Tỷ lệ `S`)** | • Logo / Mascot: **Đồng nhất 2 trục** `[S%, S%]` (Tuyệt đối không Squash & Stretch méo logo).<br>• UI Pop-in: `0% -> 108% -> 100%` (trong `10–12 frames`).<br>• Mascot Reveal: `0% -> 112% -> 95% -> 100%` (`22 frames`).<br>• Camera (`CAM` Null): Push-in liên tục `96% -> 100%` suốt cảnh. | • Ghi rõ chuỗi **3-keyframe hoặc 4-keyframe spring**: `0% -> 108% -> 100%` (overshoot nhẹ 6–8%) hoặc `0% -> 112% -> 95% -> 100%`.<br>• Nút CTA / Thanh Input: Dùng `Rectangle Size [h, h] -> [w, h]` (nở từ hình tròn thành viên thuốc) thay vì kéo giãn `Scale X` làm méo bo góc (`Roundness`). | **Lò xo chuẩn (`SPRING_POP`)**: $\omega = 16, \zeta = 0.67$ (~6–8% overshoot, tắt hẳn sau 1 chu kỳ). Không bao giờ dùng Linear hoặc chỉ 2 keyframe `0% -> 100%`. |
| **4. Rotation (Góc xoay `R`)** | • Quy ước chiều kim đồng hồ = Dương (`+°`).<br>• Kim đồng hồ (Scene 1): Kim phút `0° -> +1080°` (3 vòng), kim giờ `0° -> +90°`.<br>• Bò OPA húc (`Charge` - Scene 3): Lấy đà `-8°` (ngả sau) -> `+6°` (húc tới) -> `-3° -> +1° -> 0°`.<br>• Hai sừng (`HORN_L/R`): Cụm vào `-40° -> +6° -> 0°` (lệch pha 2 frames = `0.08s`).<br>• Card 3D (`05_Scene`): `Y Rotation +35° -> 0°`, `X Rotation +8° -> 0°`. | • Chỉ định rõ tâm xoay (Anchor) + chiều xoay (`counter-clockwise` = `-°`, `clockwise` = `+°`) + biên độ giảm chấn (damped oscillation). | Xoay luôn đi kèm **Overlap / Follow-through**: Sừng trễ hơn đầu `0.08s` (2–3 frames); đuôi trỏ chuột hoặc icon trong pill trễ hơn khung pill `0.05s` (1–2 frames). |
| **5. Keyframe & Timing Grid** | • Khung chuẩn: `30 fps` (`1 frame = 0.0333s`) hoặc `60 fps`.<br>• Nhịp nhạc: `120 BPM` = `0.50s / beat` (`15 frames @ 30fps`).<br>• Mọi điểm nổ (Pop-in, Cut, Click) phải khóa vào lưới `0.25s` (`7–8 frames`). | • Trong Omni Flash (giới hạn 3s–10s mỗi clip): Chia Kịch bản 36s thành **6 Clip chuẩn (5s – 6s – 5s – 6s – 8s – 6s)**, khóa `First Frame` + `Last Frame`. | **Tỷ lệ vàng**: `70% thời lượng` cho chuyển động (Action + Settle), tối đa `30% thời lượng` giữ tĩnh cuối clip (trong lúc giữ tĩnh, `CAM` vẫn trôi chậm `2–4%` để khung hình luôn "sống"). |

---

## PHẦN 2: BẢNG THÔNG SỐ KỸ THUẬT AFTER EFFECTS (`Final_4k 3840x2160 @ 30fps`) CHO KỊCH BẢN SỐ 1

Dưới đây là bảng thông số Keyframe chuẩn xác để dựng hoặc hậu kỳ 5 cảnh của **Kịch bản số 1 (Ads #1 - 36s)** trên After Effects (tương thích 100% cấu trúc `template 5.aep`):

| Scene & Timecode | Tên Pre-comp & Layer (Chuẩn `template 5.aep`) | Anchor Point `[X, Y]` (4K px & %) | Position `[X, Y, (Z)]` | Scale `[X%, Y%]` | Rotation `R / Rx,Ry,Rz` | Easing (Speed Graph) & Expression |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SCENE 1**<br>`00:00 – 00:05`<br>*(Hook: Chủ shop quá tải & Đồng hồ quay)* | `01_Scene` > `CAM_Null` | `[1920, 1080]` (`50%, 50%`) | `[1920, 1080] -> [1980, 1040]` | `100% -> 106%` (`f0 -> f150`) | `0°` | Linear Push-in liên tục hướng về laptop & đồng hồ |
| | `01_Scene_Clock_Hands` | Tâm trục đồng hồ `[2880, 520]` (`75%, 24%`) | `[2880, 520]` | `[100%, 100%]` | Kim phút: `0° -> +1080°`<br>Kim giờ: `0° -> +90°` | `In 40% / Out 85%` (Tăng tốc vù vù tạo cảm giác trôi giờ) |
| | `01_Scene_ShopOwner_Head` | Đáy cổ `[1820, 1380]` (`47%, 64%`) | `[1820, 1380]` | `[100%, 100%]` | `0° -> -5° -> +4° -> -3° -> 0°` | Nghiêng đầu thở dài + Rung nhẹ `wiggle(6, 8)` khi tin nhắn nổ dồn dập |
| | `01_Scene_MsgBubble_01..08` | Góc đuôi bong bóng (`[0%, 100%]` hoặc `[100%, 100%]`) | Xếp chồng quanh laptop (Stagger `6 frames` = `0.20s`/tin) | `0% -> 108% -> 100%` (`10 frames` mỗi bubble) | `-6° -> +2° -> 0°` | **Spring Pop**: `Out 15.2% / In 100%` + Overshoot `108%` tại `f7` |
| | `01_Scene_Text01` *(TOS Hook)* | Đáy dòng chữ `[1920, 320]` (`50%, 15%`) | `[1920, 440] -> [1920, 320]` (Qua `Alpha Matte`) | `[100%, 100%]` | `0°` | **Rule R1**: `Out 75.2% / In 75.1%` trong `16 frames` (`0.53s`) |
| **SCENE 2**<br>`00:05 – 00:11`<br>*(Xoáy sâu nỗi đau: Hàng chục chat bỏ dở & Lên đơn tay)* | `02_Scene` > `ChatList_Scroll_Null` | `[960, 1080]` (`25%, 50%`) | `Y: 1080 -> 870 -> 660 -> 450` (Nhảy bậc mỗi `0.50s`) | `[100%, 100%]` | `0°` | Step-scroll theo nhịp beat: `Out 20% / In 90%` (`12 frames` trượt, `3 frames` nghỉ) |
| | `02_Scene_Badge_99Plus` | Tâm huy hiệu đỏ `[1420, 310]` (`37%, 14%`) | `[1420, 310]` | `0% -> 115% -> 95% -> 100%` (Nhịp lặp `100% -> 108% -> 100%`) | `0° -> -8° -> +8° -> 0°` | `Slider Control` đếm số `12 -> 99+` (`Math.round(slider)`) |
| | `02_Scene_POS_ManualCard` | Đỉnh-trái `[2100, 360]` (`55%, 17%`) | `[2100, 360]` | Mask Wipe `0% -> 100%` (`18 frames`) | `0°` | **Rule R10**: `Out 15.2% / In 100%` + 3 bullet nỗi đau trượt vào cách nhau `0.35s` |
| | `02_Scene_DarkVignette` | `[1920, 1080]` | `[1920, 1080]` | `[100%, 100%]` | `0°` | `Opacity: 0% -> 65%` (`f0 -> f180`) tạo áp lực trực đêm quá tải |
| **SCENE 3**<br>`00:11 – 00:22`<br>*(Giải pháp: Mascot Bò OPA + Split-Screen Chat & 5 Pills)* | `05_Scene` > `Mascot_Bull_OPA` | Đáy giữa đầu bò `[50%, 100%]` | `[960, 540]` (`25%, 25%`) | `0% -> 112% -> 95% -> 100%` (`22 frames`) | `-8°` (lấy đà `f0–f6`) -> `+6°` (húc `f12`) -> `-3° -> 0°` | **Cú húc thương hiệu (Bull Charge)** quét sạch màn tối bằng `Whoosh Glow Sweep` |
| | `05_Scene_ChatCard_Left` *(Giống hệt ảnh `00:19:03`)* | Tâm thẻ trái `[1020, 1180]` (`26.5%, 54.6%`) | `[1020, 1180, +300] -> [1020, 1180, 0]` | `88% -> 100%` | `Y Rot: +28° -> 0°`<br>`X Rot: +6° -> 0°` (`24 frames`) | Card 3D xoay phẳng về phía camera + viền `EdgeGlow` xanh `#1E40FF` chạy quanh mép (`Trim Paths`) |
| | `05_Scene_Button02` *(5 Feature Pills cột phải)* | Cạnh trái mỗi Pill `[2040, Y_i]` (`53%, Y_i%`) | `X: 2240 -> 2040`<br>`Y_1..5`: `620, 820, 1020, 1220, 1420` | `0% -> 108% -> 100%` (Stagger `15 frames` = `0.50s` đúng nhịp 120 BPM) | `0°` | Kích thước Pill tự co giãn theo chữ bằng `sourceRectAtTime()` + Khung sáng `Selection_Frame` (H15) trượt qua từng Pill |
| **SCENE 4**<br>`00:22 – 00:30`<br>*(Giải phóng sức lao động: Chủ shop thảnh thơi & 3 Tích xanh)* | `04_Relief_ShopOwner` | Đáy lưng ghế `[1920, 1520]` (`50%, 70%`) | `[1920, 1520]` | `95% -> 100%` | Ngả lưng thư giãn `0° -> -4°`, hai tay mở rộng `+15°` | Chuyển động thở êm (`Math.sin(time*2)*1.5`) |
| | `04_Relief_StrikeCard_01..03` | Tâm từng thẻ `[920, 580]`, `[2920, 580]`, `[1920, 360]` | Giữ nguyên theo vòng cung quanh chủ shop | `0% -> 106% -> 100%` (Stagger `0.60s`) | `0°` | Đường gạch bỏ đỏ (`Trim Paths End: 0% -> 100%` trong `10 frames`) -> Thay bằng Icon Check xanh ✅ (`Scale 0% -> 115% -> 100%`) |
| **SCENE 5**<br>`00:30 – 00:36`<br>*(Outro & CTA: Logo Lockup + Click `chat.overpowers.agency`)* | `13_Scene` > `OPA_Mascot_Master` | Đáy giữa `U_HEAD` `[50%, 100%]` | `[1920, 920]` (`50%, 42.6%`) -> Trượt sang `[1320, 920]` (`34.4%, 42.6%`) tại `01.50s` | `0% -> 112% -> 95% -> 100%` -> Thu về `72%` khi nhường chỗ cho chữ `OPA AGENT` | Sừng `HORN_L/R`: `-40° -> +6° -> 0°` quanh gốc sừng `[22.6%, 42.1%]` | Chuẩn tuyệt đối từ `KET-LUAN-VA-PROMPT-SUA.md` (Không thêm mắt/mũi, giữ đúng lỗ trắng hình chữ O ở `[50%, 64.7%]`) |
| | `13_Scene_CTA_Pill` | Tâm nút `[1920, 1560]` (`50%, 72.2%`) | `[1920, 1560]` | `Rectangle Size: [140, 140] -> [1480, 140]` (`16 frames`)<br>Khi Click (`03.50s`): `Scale 100% -> 94% -> 102% -> 100%` (`8 frames`) | `0°` | Nở từ vòng tròn thành nút Pill (`Out 15.2% / In 100%`) + Sóng `Click Ripple` (`Scale 80% -> 150%`, `Opacity 60% -> 0%`) |
| | `13_Scene_MouseCursor` | Đỉnh mũi tên `[0, 0]` | Đường cong Bézier từ `[2950, 1950]` -> `[2180, 1580]` (`02.50s -> 03.45s`) | `100% -> 88% -> 100%` tại `03.50s` | `-15° -> 0°` | Trỏ chuột lướt đường cong tự nhiên, nhấn xuống đúng nhịp âm thanh `Click` |

---

## PHẦN 3: QUY TẮC SỐNG CÒN KHI VIẾT PROMPT CHO GOOGLE OMNI FLASH (TỪ THỰC NGHIỆM `MOTION CLAUDE`)

Qua quá trình kiểm thử thực tế trong `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/OPA-Motion-graphic-mascot/flow-omni`, có **4 quy tắc bắt buộc** quyết định 100% chất lượng đầu ra trên Google Omni Flash:

1. **Chốt chặn "Invisible Data Guard" (Chống lỗi AI vẽ thông số lên màn hình)**:
   - Trong lần chạy P01 (`KET-LUAN-VA-PROMPT-SUA.md`), khi đưa các tên biến (`HORN_L`, `22.6%`, `C#`, mũi tên kích thước) vào prompt mà không rào chắn, **Omni Flash đã vẽ luôn chữ `HORN_L`, `22.6%` và đường gióng kỹ thuật lên video!**
   - **Giải pháp bắt buộc**: Mọi prompt Motion Control phải có câu khóa ở đầu:
     > `"Everything below is invisible animation and camera control data. Never draw any of it on screen: no labels, layer names, numbers, percentages, coordinates, arrows, guides, dimension lines, bounding boxes, or any text."`
2. **Chiến lược Hybrid "Clean Motion Plates + AE Typography"**:
   - Các mô hình tạo video (Omni Flash / Veo / Kling) xử lý **Vật lý chuyển động, Mascot 2D/2.5D, Khung thẻ UI 3D, Ánh sáng Glow, Chuyển cảnh Whoosh** cực đẹp, nhưng **luôn làm nhòe hoặc sai dấu tiếng Việt cỡ nhỏ**.
   - Vì vậy, với mỗi cảnh bên dưới, bộ tài liệu cung cấp **2 phiên bản Prompt**:
     - **Bản A — `Clean Plate Mode` (Khuyên dùng cho quy trình chuyên nghiệp với AE)**: Yêu cầu Omni Flash dựng toàn bộ nhân vật, khung thẻ UI, bong bóng chat, thanh skeleton, hiệu ứng sáng và chuyển động camera (không vẽ chữ tiếng Việt), sau đó thả vào `template 5.aep` để gắn lớp chữ tiếng Việt sắc nét 4K.
     - **Bản B — `Full Visual + Motion Control Mode`**: Dành cho trường hợp muốn xem bản nháp đầy đủ bố cục ngay trên Google Omni Flash.
3. **Khóa `First Frame` + `Last Frame` (Omni 1.1 Flash) hoặc `Style Reference`**:
   - Google Omni Flash chỉ giữ chuẩn hình học thương hiệu (đặc biệt là Mascot Bò OPA và giao diện thẻ chat `05_Scene`) khi đính kèm **Ảnh tham chiếu (Reference Image)** hoặc cặp **First Frame + Last Frame**.
4. **Prompt bằng Tiếng Anh chuyên ngành Motion Graphics**:
   - Toàn bộ thuật ngữ điều khiển (`anchor point`, `overshoot spring`, `staggered pop-in`, `3D Y-rotation swing`, `track-matte slide`, `damped oscillation`) phải viết bằng **tiếng Anh** để khớp 100% với không gian huấn luyện của Google Omni Flash.

---

## PHẦN 4: PROMPT KHỞI TẠO HỆ THỐNG (SYSTEM / SESSION INIT PROMPT CHO GOOGLE OMNI FLASH)

Copy đoạn prompt dưới đây gửi vào đầu phiên làm việc với **Google Omni Flash Agent** để thiết lập tư duy **After Effects Motion Control Director**:

```markdown
You are a Senior After Effects Motion Graphics Director and Google Omni Flash Motion-Control Specialist creating a 36-second flagship 2D/2.5D SaaS commercial ("VIDEO 01 - Ads #1: OPA Agent for Pancake POS") inspired by the "AI Chat Agent Promo" After Effects template (`Final_4k 3840x2160 @ 30fps`) and SMIT - Ads Check Pro pacing.

STRICT VISUAL & MOTION CONTROL RULES FOR ALL SHOTS:
1. INVISIBLE DATA GUARD: All technical parameters (timestamps, percentages, degrees, anchor points, easing curves, layer names) are INVISIBLE animation instructions. NEVER render any labels, coordinates, numbers, percentages, dimension lines, arrows, or technical HUD overlays onto the video frames.
2. FORMAT & RHYTHM LOCK:
   - Resolution & Aspect Ratio: 16:9 widescreen (3840x2160 4K aesthetic), 30 fps (or 60 fps smooth interpolation).
   - Tempo Grid: 120 BPM (1 beat = 0.50s = 15 frames @ 30fps; half-beat = 0.25s). Every pop-in, scroll step, and camera cut locks to this 0.25s grid.
   - Zero Dead Frames: The master camera (`CAM_Null`) must maintain a continuous, subtle push-in (`Scale 96% -> 100%`) or gentle parallax drift throughout every shot so no frame is ever frozen.
3. AFTER EFFECTS TRANSFORM & EASING DISCIPLINE:
   - ANCHOR POINT LOCK: Every element scales and rotates strictly from its functional mechanical pivot:
     * Chat bubbles: pivot from the bottom-left (incoming) or bottom-right (outgoing) tail corner.
     * UI cards & modals: expand from their top-left corner or center with fast-out, long-settle easing (`cubic-bezier(0.15, 0, 0, 1)`, AE Out Influence 15.2% / In Influence 100%).
     * OPA Bull Mascot head: pivots from its bottom-center base (`[50%, 100%]`); left and right horns pivot from their respective horn roots (`[22.6%, 42.1%]` and `[77.4%, 42.1%]`) with a 0.08s overlap delay.
     * CTA & Feature Pills: expand horizontally from a circle into a rounded pill (`Rectangle Size [h, h] -> [w, h]`) so corner roundness never distorts.
   - SCALE & SPRING PHYSICS: Never use linear 2-keyframe scaling (`0% -> 100%`). Always use a 3- or 4-keyframe spring curve (`0% -> 108% -> 100%` for UI pills/bubbles; `0% -> 112% -> 95% -> 100%` for hero mascot/checkmarks).
   - 2.5D CARD PERSPECTIVE (Template `05_Scene` Style): Hero UI panels enter with a subtle 3D perspective swing (`Y-Rotation +28° -> 0°`, `X-Rotation +6° -> 0°`) accompanied by a traveling cobalt-blue edge glow (`#1E40FF` to `#2690FF`) and soft multi-layered drop shadows (`opacity 12%, blur 40px, Y-offset +18px`).
4. BRAND PALETTE & MASCOT IDENTITY LOCK:
   - Primary Brand Blue: `#1E40FF` (Electric Cobalt) | Deep Navy Background: `#0A142E` | Clean Daylight Surface: `#F4F7FF` to `#FFFFFF`.
   - Alert / Pain-Point Accent: `#FF3B30` (Coral Red) | Success / Relief Accent: `#10B981` (Emerald Green) & `#2690FF` (Cyan-Blue Glow).
   - OPA Bull Mascot: Minimalist flat geometric royal-blue bull head (`#1E40FF`) composed of a U-shaped head, two curved crescent horns on top, and a single solid white circular O-ring cutout in the lower center of the face. NO eyes, NO nostrils, NO mouth, NO ears, NO 3D shading on the mascot.
```

---

## PHẦN 5: BỘ PROMPT CHI TIẾT TỪNG CẢNH CHO KỊCH BẢN SỐ 1 TRÊN GOOGLE OMNI FLASH (6 CLIPS = 36 GIÂY)

> **Lưu ý vận hành trên Google Flow / Omni Flash**: Vì Scene 3 dài `11 giây` (`00:11 – 00:22`), vượt quá ngưỡng tối ưu 5s–8s của 1 clip đơn trên Omni Flash, chúng ta tách **Scene 3** thành **Clip 3A (5s — Cú húc chuyển cảnh & Khung Chat 3D `05_Scene` tự chốt đơn)** và **Clip 3B (6s — Split-Screen & 5 Feature Pills nảy theo nhịp 120 BPM)**. Tổng cộng **6 Clips = 36 giây** khớp 100% kịch bản gốc trên web.

---

### 🎬 CLIP 1 — SCENE 1 (`00:00 – 00:05` | Thời lượng: `5.0s`): HOOK — CHỦ SHOP QUÁ TẢI & ĐỒNG HỒ QUAY VÙ VÙ

* **Bối cảnh Kịch bản số 1**: Hoạt hình 2D/2.5D: Chủ shop ngồi quay lưng trước laptop, đồng hồ treo tường bên phải quay vù vù. Hàng loạt icon tin nhắn Messenger/Pancake nảy lên liên tục kèm tiếng *"Ting! Ting! Ting!"* dồn dập.
* **Text hậu kỳ trong AE (`01_Scene_Text01`)**:
  `BẠN MẤT BAO NHIÊU THỜI GIAN`  
  `để trả lời khách và lên đơn trên Pancake mỗi ngày?`

#### 🔹 Prompt 1A — Motion Control Chi Tiết (Chuẩn After Effects Keyframe + Invisible Guard)
```text
Everything below is invisible animation and camera control data. Never draw any of it on screen: no labels, layer names, numbers, percentages, coordinates, arrows, guides, dimension lines, or any text.

[INPUT & STYLE LOCK]
High-end 2D/2.5D vector motion graphics animation in 16:9 widescreen (4K 3840x2160 aesthetic, 30 fps). Clean modern SaaS commercial style matching SMIT Ads Check Pro and Envato AI Chat Promo.

[BACKGROUND & LIGHTING LOCK]
A cozy e-commerce shop office room seen from behind a young shop owner sitting at a desk in front of a glowing laptop at center-bottom `(50%, 68%)`. Warm indoor desk lamp gradually cools into stressed slate-blue twilight (`#162238`). On the upper-right wall at `(76%, 26%)` hangs a minimalist circular wall clock.

[LAYERS & MECHANICAL ANCHOR POINTS]
- `CAM_NULL` (Master Camera): Anchor at canvas center `(50%, 50%)`.
- `SHOP_OWNER`: Viewed from behind at `(50%, 68%)`, upper torso and head pivoting from the base of the neck `(50%, 62%)`.
- `WALL_CLOCK`: Circular dial at `(76%, 26%)`; minute hand and hour hand both pivot strictly from the center pin of the clock face `(76%, 26%)`.
- `MSG_BUBBLES_01_TO_08`: Eight glossy blue and orange chat notification bubbles with circular avatar dots and skeleton message bars (no readable words), each pivoting strictly from its bottom-left or bottom-right speech-tail corner.

[KEYFRAMES & TRANSFORM TIMELINE (0.00s to 5.00s @ 120 BPM)]
- `[0.00s -> 5.00s]` `CAM_NULL`: Continuous slow push-in from Scale `96%` to `104%`, drifting slightly toward the laptop and clock so the frame feels alive and increasingly claustrophobic.
- `[0.00s -> 4.50s]` `WALL_CLOCK` Rotation: The minute hand spins clockwise rapidly through three full revolutions (`Rotation 0 deg -> +1080 deg`, accelerating with ease-in `40%` and ease-out `85%`), while the hour hand advances `0 deg -> +90 deg`, visually showing hours flying by.
- `[0.25s -> 4.25s]` `MSG_BUBBLES_01_TO_08` Staggered Pop-In: Every `0.25s` (half-beat), a new chat notification bubble pops out around the laptop screen in a rising arc from `(32%, 58%)` to `(68%, 34%)`. Each bubble scales from its tail-corner anchor using a crisp 3-keyframe spring (`Scale 0% -> 108% -> 100%` over `0.30s`, `Rotation -6 deg -> +2 deg -> 0 deg`).
- `[1.00s -> 4.50s]` `SHOP_OWNER` Reaction: As the bubbles pile up around the laptop, the shop owner's shoulders slump and their head tilts from `0 deg -> -5 deg -> +4 deg` with a subtle stressed tremor, hands frantically hovering over the keyboard.
- `[0.00s -> 5.00s]` Top 22% of the frame `(y: 0% to 22%)` is kept clean and uncluttered dark-slate space reserved for the After Effects headline overlay.

[VFX & SFX CUES]
Subtle radial screen glow from the laptop monitor reflecting on the shop owner's silhouette; soft motion blur on the spinning clock hands and popping bubbles. Audio cues: fast rhythmic clock ticking accelerating under rapid-fire "Ting! Ting! Ting!" message chime pops.
```

#### 🔹 Prompt 1B — Bản Ngôn Ngữ Tự Nhiên Thuần Khiết (An toàn 100% không lo AI vẽ thông số)
```text
A crisp 2D/2.5D vector motion-graphics animation in 16:9 widescreen, styled like a modern SaaS tech commercial. We see a young online shop owner from behind, sitting at a desk in front of a glowing laptop in the lower center of the frame, while the top fifth of the composition stays clean dark navy-slate negative space for a title header. On the upper-right wall hangs a clean minimalist round clock whose hands spin rapidly clockwise, showing hours flying past in seconds. Starting immediately and building to a frantic rhythm, glossy blue and orange chat notification bubbles with tiny bell and message icons pop out one after another around the laptop screen, each springing cleanly from its pointed tail corner with a lively bounce and a soft glow. As dozens of unread chat bubbles stack up around the monitor, the room lighting dims into a stressed late-night blue glow and the shop owner's shoulders slump with exhaustion while the camera pushes slowly inward. No text, no letters, and no numbers appear anywhere on screen.
```

---

### 🎬 CLIP 2 — SCENE 2 (`00:05 – 00:11` | Thời lượng: `6.0s`): XOÁY SÂU NỖI ĐAU — MÀN HÌNH QUÁ TẢI HỘI THOẠI & NHẬP ĐƠN POS THỦ CÔNG

* **Bối cảnh Kịch bản số 1**: Góc nhìn chuyển sang màn hình máy tính mở hàng chục hội thoại Pancake đang nhấp nháy chờ rep (*"Còn size M không shop?"*, *"Giá bao nhiêu?"*, *"Check bill giúp em"*). Không gian xung quanh tối dần (trực page đêm muộn, quá tải).
* **Text hậu kỳ trong AE (`02_Scene_Text01..03`)**:
  `• Hàng chục cuộc chat bỏ dở`  
  `• Trả lời lặp đi lặp lại`  
  `• Lên đơn POS thủ công`

#### 🔹 Prompt 2A — Motion Control Chi Tiết (Chuẩn After Effects Keyframe + Invisible Guard)
```text
Everything below is invisible animation and camera control data. Never draw any of it on screen: no labels, layer names, numbers, percentages, coordinates, arrows, guides, dimension lines, or any text.

[INPUT & STYLE LOCK]
2.5D UI motion graphics in 16:9 widescreen (4K 3840x2160 aesthetic, 30 fps), matching the dark-mode UI card aesthetic of Envato AI Chat Agent Promo (`04_Scene` & `05_Scene`).

[BACKGROUND & LIGHTING LOCK]
Deep midnight navy workspace background (`#081024`) with a darkening vignette around the edges to evoke late-night burnout. A soft coral-red warning ambient glow (`#FF3B30` at 15% opacity) pulses gently behind the overloaded inbox panel.

[LAYERS & MECHANICAL ANCHOR POINTS]
- `CAM_NULL`: Anchor at `(50%, 50%)`, slight 2.5D perspective tilt.
- `INBOX_PANEL_LEFT`: A sleek multi-channel chat inbox window occupying the left half of the screen `(28%, 54%)`, tilted slightly in 3D space (`Y-Rotation +12 deg`). Inside is a vertical stack of incoming customer chat rows.
- `ALERT_BADGE_RED`: A glossy coral-red notification counter pill anchored at the top-right corner of the inbox window `(44%, 20%)`, pivoting from its center.
- `MANUAL_POS_FORM_RIGHT`: A manual order-entry spreadsheet/POS form card on the right `(72%, 62%)`, anchored at its top-left corner `(54%, 38%)`, while the upper-right area `(54%, 15% to 35%)` holds three clean horizontal glass pill slots for bullet points.

[KEYFRAMES & TRANSFORM TIMELINE (0.00s to 6.00s @ 120 BPM)]
- `[0.00s -> 0.50s]` `INBOX_PANEL_LEFT` Entrance: Swings in from `Scale 88% -> 100%` and `Y-Rotation +24 deg -> +12 deg` with fast-out, long-settle easing (`Out Influence 15.2%, In Influence 100%`).
- `[0.50s -> 4.50s]` Vertical Step-Scroll on Beat: Every `0.50s` (on each 120 BPM beat), the stack of chat rows inside `INBOX_PANEL_LEFT` shifts downward by one row height as a new urgent incoming message row pops in at the top from its left avatar anchor (`Scale 0% -> 108% -> 100%`), flashing an unread red dot and skeleton question bars.
- `[0.75s -> 5.00s]` `ALERT_BADGE_RED`: Pops in (`Scale 0% -> 115% -> 95% -> 100%`) and pulses rhythmically (`Scale 100% -> 108% -> 100%` + subtle shake `Rotation -6 deg -> +6 deg -> 0 deg`) as unread alerts accumulate.
- `[1.25s -> 3.00s]` `MANUAL_POS_FORM_RIGHT`: Wipes open diagonally from its top-left anchor `(54%, 38%)` (`Mask Scale 0% -> 100%`, `cubic-bezier(0.15, 0, 0, 1)`), showing a blinking cursor tediously copying and pasting skeleton bars from the chat window into manual phone and address input boxes.
- `[1.50s, 2.25s, 3.00s]` Three dark-glass bullet pill containers slide in horizontally at the upper right `(72%, 20%)`, `(72%, 28%)`, and `(72%, 36%)` with a `0.75s` stagger (`Position X +8% -> 0%`, `Opacity 0% -> 100%`), ready for After Effects Vietnamese bullet text.
- `[4.00s -> 6.00s]` `CAM_NULL`: Pushes in from `Scale 100% -> 106%` as the surrounding ambient light dims further, emphasizing overload just before the hero transition.

[VFX & SFX CUES]
Crisp glassmorphism borders, subtle coral-red edge pulse on unread rows, shallow depth-of-field blur on background grid.
```

#### 🔹 Prompt 2B — Bản Ngôn Ngữ Tự Nhiên Thuần Khiết
```text
A sleek 2.5D dark-mode UI motion-graphics scene in 16:9 widescreen. On the left side of the frame, a slightly angled multi-channel chat inbox window is flooded with incoming customer message rows that step-scroll downward on every beat as new unread rows pop in at the top with glowing red alert dots and pulsing notification badges. On the lower-right side, a manual order-entry form wipes open from its top-left corner, showing a blinking cursor struggling to copy and paste bars of customer data from the chat into form fields one by one. Above the form on the upper right, three sleek translucent glass pill banners slide smoothly into place one after another, left clean and blank for text overlay. As the inbox continues flashing with unanswered messages, the surrounding midnight-blue workspace darkens around the edges while the camera pushes slowly inward. Render all UI cards with clean geometric bars and icons only—no letters, words, or numbers on screen.
```

---

### 🎬 CLIP 3A — SCENE 3 PHẦN ĐẦU (`00:11 – 00:16` | Thời lượng: `5.0s`): CHUYỂN CẢNH BỪNG SÁNG, MASCOT BÒ OPA XUẤT HIỆN & KHUNG CHAT 3D (`05_Scene`) TỰ CHỐT ĐƠN POS

* **Bối cảnh Kịch bản số 1 + Khớp 100% ảnh chụp `template 5.aep` (`00:19:03`)**:
  - Chuyển cảnh bừng sáng (`Whoosh Transition`): Mascot Bò OPA xuất hiện, giao diện OPA Agent bung ra mượt mà bên trái màn hình.
  - Khung chat OPA tự động tư vấn size M giá 159.000đ và tự đẩy đơn sang bảng Pancake POS (dựa trên đúng cơ chế `05_Scene` trong ảnh chụp: thẻ trắng 3D có viền xanh `EdgeGlow` xoay về phía camera).

#### 🔹 Prompt 3A — Motion Control Chi Tiết (Chuẩn `05_Scene` trong `template 5.aep` + Mascot Charge)
```text
Everything below is invisible animation and camera control data. Never draw any of it on screen: no labels, layer names, numbers, percentages, coordinates, arrows, guides, dimension lines, or any text.

[INPUT & STYLE LOCK]
Use the attached OPA Bull Mascot reference image (`T01`) and `05_Scene` UI layout (`T03`). 2.5D SaaS UI & Mascot motion graphics in 16:9 widescreen (4K 3840x2160, 30 fps).

[BACKGROUND & TRANSITION LOCK]
At `[0.00s -> 0.50s]`, a brilliant royal-blue and cyan light-sweep wave (`#1E40FF` to `#2690FF`) wipes across the dark screen from left to right, transforming the canvas into a vibrant, high-tech cobalt-and-daylight blue studio environment (`#0D1B3E` with a bright radial glow `#1E40FF` on the left).

[LAYERS & MECHANICAL ANCHOR POINTS]
- `MASCOT_OPA_BULL`: Minimalist flat royal-blue geometric bull head (`#1E40FF`) with two curved crescent horns and a single solid white circular O-ring cutout in the lower center of the face (strictly no eyes, no nostrils, no mouth). Anchored at its bottom-center base `(50%, 100%)`, positioned at the top-left of the chat panel `(16%, 22%)`.
- `CHAT_CARD_05_LEFT`: A crisp white rounded UI chat card (`#FFFFFF`, corner radius `28px`) with a glowing cobalt-blue outer rim (`EdgeGlow #2690FF`), occupying the left column `(28%, 56%)`, pivoting from its center in 3D space.
- `BUBBLE_CUSTOMER`: Incoming light-gray chat bubble at upper-left inside the card, anchored at its bottom-left tail corner.
- `BUBBLE_OPA_REPLY`: Outgoing royal-blue (`#1E40FF`) AI reply bubble on the right side of the card, anchored at its bottom-right tail corner, containing a mini product thumbnail and a green POS order-confirmed badge.

[KEYFRAMES & TRANSFORM TIMELINE (0.00s to 5.00s @ 120 BPM)]
- `[0.00s -> 0.75s]` `MASCOT_OPA_BULL` Hero Charge & Pop: Springs up from its bottom-center anchor (`Scale 0% -> 112% -> 95% -> 100%`). It performs a signature energetic bull-charge tilt: leans back `-8 deg` in anticipation (`0.15s`), lunges forward `+6 deg` (`0.35s`), and settles `0 deg` (`0.75s`), while both crescent horns swing outward from their roots with a `0.08s` overlap (`-35 deg -> +5 deg -> 0 deg`).
- `[0.40s -> 1.40s]` `CHAT_CARD_05_LEFT` 3D Swing-In (exact `template 5.aep` `05_Scene` motion): Enters on the left half of the screen, rotating smoothly in 3D from an angled perspective (`Y-Rotation +32 deg -> +4 deg`, `X-Rotation +6 deg -> 0 deg`, `Scale 86% -> 100%`, `cubic-bezier(0.15, 0, 0, 1)`) as a bright blue streak traces around its border (`Trim Paths 0% -> 100%`).
- `[1.50s -> 2.00s]` `BUBBLE_CUSTOMER`: Pops out from its bottom-left tail corner (`Scale 0% -> 108% -> 100%`).
- `[2.10s -> 2.60s]` Instant AI Typing Indicator: A tiny blue pill appears at the bottom-right with three white dots bouncing in a sine-wave sequence (`phase offset 0.08s`).
- `[2.60s -> 3.40s]` `BUBBLE_OPA_REPLY`: Morphs from the typing pill into a full royal-blue reply bubble from its bottom-right anchor (`Scale 0% -> 108% -> 100%`).
- `[3.50s -> 4.75s]` Automated POS Order Sync Card: Immediately below the AI reply, a sleek emerald-green & blue POS order confirmation card slides down (`Mask Wipe Out 15.2% / In 100%`) and stamps a glowing green checkmark (`Scale 0% -> 115% -> 100%`), while the right half of the screen `(x: 52% to 94%)` remains clean open studio space ready for the 5 Feature Pills in Shot 3B.

[VFX & SFX CUES]
Energetic "Whoosh!" light sweep at `0.00s`, crisp UI pop chimes on each bubble, and a bright confirmation chime at `3.60s`.
```

---

### 🎬 CLIP 3B — SCENE 3 PHẦN SAU (`00:16 – 00:22` | Thời lượng: `6.0s`): BỐ CỤC SPLIT-SCREEN & 5 PILL TÍNH NĂNG NẢY RA THEO NHỊP NHẠC (`05_Scene_Button02` + `H15`)

* **Bối cảnh Kịch bản số 1**:
  - Bên trái: Khung chat OPA + Mascot Bò OPA vẫn hoạt động mượt mà, tự động đẩy đơn sang bảng Pancake POS.
  - Bên phải: Tiêu đề lớn phía trên + **5 Pill tính năng (Icon + Text)** lần lượt nảy ra (`Pop-in`) theo nhịp nhạc 120 BPM, kèm khung sáng chọn chạy dọc (`H15 Option Pill Selector` từ `o ping.mp4` cảnh `09_Scene`).
* **Text hậu kỳ trong AE (`05_Scene_Text01` & `05_Scene_Button01..05`)**:
  - Header: `Chỉ 1 kết nối — OPA tự động hóa toàn bộ quy trình bán hàng trên Pancake:`
  - Pill 1: `💬 Tự trả lời đúng tồn kho POS`
  - Pill 2: `📦 Tự chốt đơn vào Pancake POS`
  - Pill 3: `🧾 Xác minh chuyển khoản bằng ảnh`
  - Pill 4: `⏰ Nhắc khách bỏ giỏ trong 24h`
  - Pill 5: `🤝 Nhân viên tiếp quản bất cứ lúc nào`
  - Footer: `Và nhiều hơn thế nữa!`

#### 🔹 Prompt 3B — Motion Control Chi Tiết (Split-Screen + 5 Staggered Feature Pills trên lưới 0.50s)
```text
Everything below is invisible animation and camera control data. Never draw any of it on screen: no labels, layer names, numbers, percentages, coordinates, arrows, guides, dimension lines, or any text.

[INPUT & CONTINUITY LOCK]
Use the last frame of Clip 3A as First Frame lock. 2.5D Split-Screen SaaS UI motion graphics in 16:9 widescreen (4K 3840x2160, 30 fps).

[BACKGROUND & SPLIT-SCREEN LAYOUT]
Left column `(x: 6% to 48%)` keeps the active white 3D-angled OPA Chat & Pancake POS sync card with the royal-blue OPA Bull Mascot perched at its top-left corner. Right column `(x: 52% to 94%)` is dedicated to a vertical stack of five sleek rounded feature-pill buttons (`05_Scene_Button` style) beneath a clean header zone at `(y: 12% to 22%)`.

[LAYERS & MECHANICAL ANCHOR POINTS]
- `LEFT_CHAT_POS_GROUP`: Gently floating in 2.5D space (`Y-Rotation +4 deg`), showing live order sync pulses flowing from the chat bubble into a compact POS order table at the bottom of the card.
- `FEATURE_PILLS_01_TO_05`: Five horizontal white-and-glass rounded pill cards stacked vertically in the right column at `y = 28%, 40%, 52%, 64%, 76%`. Each pill is anchored at its left circular icon badge `(x = 54%)` and features a distinct minimalist 2D vector icon on the left:
  1. Pill 1 (`y=28%`): Blue chat bubble + inventory box icon.
  2. Pill 2 (`y=40%`): Package box + lightning POS arrow icon.
  3. Pill 3 (`y=52%`): Receipt bill + green verification shield icon.
  4. Pill 4 (`y=64%`): Clock + shopping cart bell icon.
  5. Pill 5 (`y=76%`): Handshake / human headset takeover icon.
- `GLOW_SELECTOR_FRAME`: A luminous cobalt-cyan border highlight (`#2690FF`) that glides vertically from Pill 1 down to Pill 5 (`H15` selector mechanic).

[KEYFRAMES & TRANSFORM TIMELINE (0.00s to 6.00s @ 120 BPM)]
- `[0.00s -> 6.00s]` `CAM_NULL`: Smooth continuous push-in `Scale 100% -> 104%`.
- Staggered 5-Pill Pop-In on Exact 120 BPM Beats (`0.50s` interval):
  * `[0.50s -> 0.90s]` `FEATURE_PILL_01`: Springs open from its left icon anchor (`Scale 0% -> 108% -> 100%`, `Position X +4% -> 0%`, `Out Influence 15.2% / In Influence 100%`); its icon pops `0.06s` later (`Scale 0% -> 115% -> 100%`).
  * `[1.00s -> 1.40s]` `FEATURE_PILL_02`: Same crisp spring pop-in at `y = 40%`.
  * `[1.50s -> 1.90s]` `FEATURE_PILL_03`: Same crisp spring pop-in at `y = 52%`.
  * `[2.00s -> 2.40s]` `FEATURE_PILL_04`: Same crisp spring pop-in at `y = 64%`.
  * `[2.50s -> 2.90s]` `FEATURE_PILL_05`: Same crisp spring pop-in at `y = 76%`.
- `[3.00s -> 5.20s]` `GLOW_SELECTOR_FRAME` Cascade: A bright electric-blue selection border sweeps smoothly down across all five pills (`Out Influence 75% / In Influence 75%`), lighting up each pill's icon with a subtle scale pulse (`100% -> 104% -> 100%`) while the left chat panel shows a matching green order-synced pulse.
- `[0.00s -> 6.00s]` Inside each pill to the right of the icon, leave clean uncluttered white pill surface (or ultra-subtle skeleton bars) so Vietnamese typography can be composited cleanly in After Effects.

[VFX & SFX CUES]
Five rhythmic, ascending melodic synth-marimba pop notes synced to `0.50s, 1.00s, 1.50s, 2.00s, 2.50s`.
```

---

### 🎬 CLIP 4 — SCENE 4 (`00:22 – 00:30` | Thời lượng: `8.0s`): GIẢI PHÓNG SỨC LAO ĐỘNG (RELIEF) — CHỦ SHOP THẢNH THƠI & GẠCH BỎ 3 NỖI ĐAU KÈM TÍCH XANH ✅

* **Bối cảnh Kịch bản số 1**: Quay lại nhân vật chủ shop 2D ngồi trước laptop nhưng giờ mỉm cười thảnh thơi, hai tay dang rộng thoải mái (hoặc đan sau gáy thư giãn). Xung quanh nhân vật lần lượt nảy lên 3 khung thoại gạch bỏ các thao tác cực nhọc, kèm dấu tích xanh ✅.
* **Text hậu kỳ trong AE (`04_Relief_Text01..03`)**:
  `✅ Không cần tạo App Facebook phức tạp`  
  `✅ Không cần gõ lại một câu hỏi hàng trăm lần`  
  `✅ Không cần copy-paste từng số điện thoại, địa chỉ vào POS`

#### 🔹 Prompt 4A — Motion Control Chi Tiết (Chuẩn After Effects Keyframe + Invisible Guard)
```text
Everything below is invisible animation and camera control data. Never draw any of it on screen: no labels, layer names, numbers, percentages, coordinates, arrows, guides, dimension lines, or any text.

[INPUT & STYLE LOCK]
2D/2.5D vector character & UI motion graphics in 16:9 widescreen (4K 3840x2160 aesthetic, 30 fps), matching the character style of Shot 1 but now in bright, airy daylight.

[BACKGROUND & LIGHTING LOCK]
Bright, sunlit modern shop studio (`#F4F7FF` to `#FFFFFF`) with warm morning sunlight streaming in and soft floating royal-blue ambient particles. The oppressive dark mood of Shot 1 is completely gone.

[LAYERS & MECHANICAL ANCHOR POINTS]
- `SHOP_OWNER_RELAXED`: Centered in the lower-middle frame `(50%, 66%)` behind the laptop, facing three-quarters toward camera with a calm, relieved smile. Upper body pivots from the lower spine `(50%, 74%)`; arms pivot from the shoulders.
- `LAPTOP_SCREEN`: Shows a tiny blue OPA Bull Mascot icon smoothly handling chats automatically on its own.
- `RELIEF_CARDS_01_TO_03`: Three wide rounded floating white UI banners arranged in a clean arc above and around the shop owner at `(26%, 36%)`, `(74%, 36%)`, and `(50%, 18%)`. Each card is anchored at its center and has a circular badge slot on its left edge.

[KEYFRAMES & TRANSFORM TIMELINE (0.00s to 8.00s @ 120 BPM)]
- `[0.00s -> 1.50s]` `SHOP_OWNER_RELAXED` Motion: Leans back comfortably into the chair (`Rotation 0 deg -> -4 deg`, `Out Influence 80%`) and stretches both arms wide open in a relaxed, carefree posture (`Shoulder Rotation 0 deg -> +18 deg`), followed by a gentle breathing loop (`Scale Y 100% <-> 101.5%`).
- `[1.25s -> 2.50s]` `RELIEF_CARD_01` (Left `(26%, 36%)`):
  * Pops in from its center (`Scale 0% -> 108% -> 100%` over `0.35s`) initially showing a faded gray gear/code icon with a red diagonal strike-through line drawing across it (`Trim Paths 0% -> 100%` in `0.25s`).
  * At `1.85s`, a vibrant emerald-green checkmark badge (`#10B981`) springs over the left badge slot (`Scale 0% -> 115% -> 95% -> 100%`) as the card border glows clean blue (`#1E40FF`).
- `[2.75s -> 4.00s]` `RELIEF_CARD_02` (Right `(74%, 36%)`):
  * Pops in (`Scale 0% -> 108% -> 100%`), crosses out a repetitive keyboard-typing icon (`Trim Paths 0% -> 100%`), and snaps into a glowing green checkmark badge (`Scale 0% -> 115% -> 95% -> 100%`) at `3.35s`.
- `[4.25s -> 5.50s]` `RELIEF_CARD_03` (Top-Center `(50%, 18%)`):
  * Pops in (`Scale 0% -> 108% -> 100%`), crosses out a manual copy-paste clipboard icon (`Trim Paths 0% -> 100%`), and snaps into a glowing green checkmark badge (`Scale 0% -> 115% -> 95% -> 100%`) at `4.85s`.
- `[5.50s -> 8.00s]` All three cards float gently in zero-gravity (`vertical sine drift +-6px`) while the camera performs a slow celebratory pull-back (`Scale 103% -> 98%`). Keep the interior right side of all three cards clean white space for the After Effects Vietnamese text lines.

[VFX & SFX CUES]
Three crisp "slash -> ding!" sound pairs synced to the strikethrough and green checkmark pops at `1.85s`, `3.35s`, and `4.85s`.
```

#### 🔹 Prompt 4B — Bản Ngôn Ngữ Tự Nhiên Thuần Khiết
```text
A bright, uplifting 2D/2.5D vector motion-graphics scene in 16:9 widescreen. In a sunlit, airy studio workspace, the young shop owner sits in front of the laptop smiling peacefully, leaning back and stretching both arms out wide in complete relief while the laptop screen quietly runs automated blue chat bubbles on its own. Around the shop owner in the upper half of the frame, three sleek floating white rounded banners pop in one by one in a balanced arc—first on the left, then on the right, and finally at top-center. On each banner, a small gray icon representing tedious manual work is swiftly crossed out by a red line and immediately replaced by a vibrant emerald-green checkmark badge that springs in with a joyful bounce. The interior of each banner stays clean white space reserved for post-production text, while the camera glides slowly back. No words, letters, or numbers appear on screen.
```

---

### 🎬 CLIP 5 — SCENE 5 (`00:30 – 00:36` | Thời lượng: `6.0s`): OUTRO & CTA — MASCOT BÒ OPA + LOGO LOCKUP & CLICK `chat.overpowers.agency`

* **Bối cảnh Kịch bản số 1 + Quy chuẩn Logo Animation từ `KET-LUAN-VA-PROMPT-SUA.md`**:
  - Chuyển cảnh nền trắng/xanh thương hiệu tinh gọn. Mascot Bò OPA + Logo OPA Agent hiện lớn ở chính giữa màn hình.
  - Bên dưới là nút CTA nổi bật kèm hiệu ứng trỏ chuột click vào.
* **Text hậu kỳ trong AE (`13_Scene_Text01..02`)**:
  `OPA Agent — AI bán hàng cho shop dùng Pancake`  
  `👉 Thử miễn phí ngay tại: chat.overpowers.agency`

#### 🔹 Prompt 5A — Motion Control Chi Tiết (Chuẩn Logo OPA `KET-LUAN-VA-PROMPT-SUA.md` + CTA Pill Click)
```text
Everything below is invisible animation and camera control data. Never draw any of it on screen: no labels, layer names, numbers, percentages, coordinates, arrows, guides, dimension lines, or any text.

[INPUT & BRAND LOCK]
Attach First Frame (`K00` clean white-blue studio canvas) and Reference Image (`T01` OPA Bull Mascot & Lockup). 16:9 widescreen (4K 3840x2160, 30 fps).
Strict Mascot Geometry Lock: Flat royal-blue (`#1E40FF`) U-shaped bull head, two curved crescent horns on top, and a single solid white circular O-ring cutout inside the lower center of the head. Never add eyes, pupils, nostrils, mouth, ears, or gradients to the bull head.

[BACKGROUND LOCK]
Minimalist pure white and soft daylight-blue studio background (`#F8FAFF` to `#FFFFFF`) with a subtle royal-blue ambient halo in the center.

[LAYERS & MECHANICAL ANCHOR POINTS]
- `OPA_BULL_MARK`: Positioned initially at `(50%, 40%)`. The U-shaped head scales and rotates strictly from its bottom-center point `(50%, 100% of the head)`. Left and right crescent horns pivot from their respective horn roots where they meet the head. The inner white circle expands from its center.
- `CTA_PILL_BUTTON`: Centered below at `(50%, 74%)`, anchored at its center `(50%, 74%)`, filled with vibrant royal-blue (`#1E40FF`) and a soft outer glow.
- `MOUSE_CURSOR`: A crisp white-and-navy vector pointer arrow starting from the bottom-right corner `(82%, 92%)`, pivoting from its arrow tip.

[KEYFRAMES & TRANSFORM TIMELINE (0.00s to 6.00s @ 120 BPM)]
- `[0.25s -> 1.00s]` `OPA_BULL_MARK` Signature Spring Reveal:
  * The royal-blue U-head pops up from its bottom-center point using the exact 4-keyframe spring (`Scale 0% -> 112% -> 95% -> 100%` over `0.60s`), accompanied by a damped tilt (`Rotation -8 deg -> +5 deg -> -2 deg -> 0 deg`).
  * Delayed by `0.10s`, the inner white circle pops open from its center (`Scale 0% -> 110% -> 100%`).
  * Delayed by `0.15s`, the left horn (`0.40s`) and right horn (`0.48s`, `0.08s` stagger) swing outward from their roots (`Rotation -40 deg -> +6 deg -> 0 deg`) and lock into the exact reference silhouette.
- `[1.25s -> 2.00s]` Horizontal Lockup Slide: The completed bull mark glides smoothly left from `x = 50%` to `x = 34%` while scaling uniformly to `72%` (`Out Influence 75% / In Influence 75%`), leaving clean horizontal space on the right `(x: 42% to 72%, y: 40%)` for the `OPA AGENT` wordmark and subtitle in After Effects.
- `[1.75s -> 2.40s]` `CTA_PILL_BUTTON` Morph Expand: Starts as a royal-blue circle at `(50%, 74%)` and stretches horizontally from its center into a wide rounded CTA pill button (`Rectangle Size [h, h] -> [w, h]`, `Out Influence 15.2% / In Influence 100%`), keeping semi-circular end caps perfectly round.
- `[2.50s -> 3.45s]` `MOUSE_CURSOR` Arc & Click: Glides along a smooth curved Bézier arc from `(82%, 92%)` to `(58%, 75%)` over the CTA pill (`Out Influence 80%`).
- `[3.50s -> 3.85s]` The Click Impact: Cursor tip presses down (`Scale 100% -> 88% -> 100%`) as the entire `CTA_PILL_BUTTON` compresses and rebounds (`Scale 100% -> 94% -> 103% -> 100%` in `0.25s`), emitting two concentric royal-blue ripple rings (`Scale 95% -> 135%`, `Opacity 60% -> 0%`).
- `[3.85s -> 6.00s]` Final Hold with Subtle Life: The logo lockup and glowing CTA button hold steady while `CAM_NULL` continues a gentle `100% -> 102%` drift to the end of the 6-second clip.

[VFX & SFX CUES]
Playful 3-note rising synth chime on the bull reveal (`0.25s–0.90s`), crisp mechanical mouse click at `3.50s`, and a warm resolving major chord logo tail (`3.50s–6.00s`).
```

#### 🔹 Prompt 5B — Bản Ngôn Ngữ Tự Nhiên Thuần Khiết (Kèm First Frame + Last Frame Lock)
```text
Create a 6-second 2D minimalist vector outro animation in 16:9 widescreen on a clean white-and-daylight-blue background, using the attached OPA Bull Mascot reference image. In the first second, the flat royal-blue U-shaped bull head springs up from its bottom-center point with a lively bounce and a slight playful tilt; a split-second later, the solid white circular ring opens inside the lower center of the head and both curved crescent horns swing smoothly outward from their roots to lock into the exact mascot silhouette, with no eyes, nostrils, or mouth. In the second second, the bull mark glides smoothly to the left of center to make room for a headline beside it, while below it a royal-blue circle stretches horizontally into a sleek rounded call-to-action pill button. A crisp vector mouse cursor glides in along a smooth curved path from the bottom right, lands on the blue pill button at 3.5 seconds, and clicks it—causing the button to press down and spring back with a glowing blue ripple ring before holding steady to the end. Do not draw any text, letters, or numbers on screen.
```

---

## PHẦN 6: BỘ PROMPT ĐIỀU KHIỂN HỘI THOẠI (FOLLOW-UP CONVERSATIONAL CONTROL TRÊN GOOGLE OMNI FLASH)

Khi làm việc với **Google Omni Flash**, nếu sau lần render đầu tiên bạn muốn chỉnh sửa **đúng 1 thông số After Effects** (ví dụ: chỉnh lại độ nảy `Scale`, đổi tâm xoay `Anchor Point`, chỉnh góc nghiêng 3D `Rotation`, hay xóa chữ lạ do AI tự vẽ), hãy áp dụng quy tắc **"1 Lượt = 1 Thay Đổi + Khóa Phần Còn Lại"** từ `KICH-BAN-OMNI-FLASH.md`:

### 1. Sửa lỗi AI tự ý vẽ chữ / số / nhãn kỹ thuật lên video
```text
Keep the exact same camera motion, layout, colors, and animation timing. Remove all text, letters, numbers, labels, and technical lines from the screen so every UI card, pill, and chat bubble contains only clean geometric shapes, icons, and solid skeleton bars.
```

### 2. Chỉnh lại độ nảy `Scale` (Overshoot Spring) theo chuẩn After Effects (`0% -> 108% -> 100%`)
```text
Keep everything else in the scene identical. Only refine the scale pop-in of the [chat bubbles / 5 feature pills / CTA button]: make each element spring crisply from 0% to a slight 108% overshoot and settle smoothly back to 100% over 0.30 seconds, instead of scaling linearly.
```

### 3. Sửa lỗi sai `Anchor Point` (Tâm neo bị trượt khi phóng to hoặc xoay)
```text
Keep the background, colors, and timing unchanged. Only fix the pivot point (anchor point) of the [chat bubbles / bull horns / UI card]:
- For incoming chat bubbles: make them scale and pop strictly from their bottom-left tail corner.
- For the OPA bull head: make it scale and tilt strictly from its bottom-center base so the bottom edge stays planted.
- For the two horns: make each horn rotate strictly around its root where it connects to the head.
```

### 4. Chỉnh góc xoay 3D (`Y-Rotation` / `X-Rotation`) của khung Chat `05_Scene` giống hệt ảnh chụp `template 5.aep`
```text
Keep the exact same chat bubble animation inside the card. Only adjust the 3D perspective of the main white chat panel on the left: start the card angled at roughly 30 degrees toward the center, then smoothly rotate it flatter toward the camera (around a 4-degree subtle angle) over 0.8 seconds with a glowing royal-blue border tracing its outer edge.
```

### 5. Đồng bộ lại nhịp `Stagger` (Độ trễ giữa 5 Pill tính năng ở Scene 3B theo đúng nhịp 120 BPM)
```text
Keep the split-screen layout and left chat panel unchanged. Only adjust the timing of the five feature pills on the right column: make them pop in sequentially from top to bottom at strict 0.50-second intervals (at 0.5s, 1.0s, 1.5s, 2.0s, and 2.5s), with each pill expanding from its left icon badge.
```

---

## PHẦN 7: QUY TRÌNH RÁP HẬU KỲ TRONG AFTER EFFECTS (`template 5.aep` / `Final_4k 3840x2160`)

Để sản phẩm cuối cùng đạt độ sắc nét **4K chuẩn thương mại như `o ping.mp4`** mà không bị lỗi dấu tiếng Việt của AI:

1. **Bước 1 — Xuất Clean Plates từ Google Omni Flash**:
   - Render 6 clips (`Clip 1`, `Clip 2`, `Clip 3A`, `Clip 3B`, `Clip 4`, `Clip 5`) bằng các **Prompt Bản A (Clean Plate Mode)** ở trên.
   - Upscale hoặc đưa trực tiếp vào comp `Final_4k (3840 x 2160)` (`30 fps`) trong `template 5.aep`.
2. **Bước 2 — Gắn lớp Text Tiếng Việt chuẩn `Inter` / `Plus Jakarta Sans` (`SemiBold` & `Bold`)**:
   - Áp dụng **Expression tự co giãn khung Pill (`sourceRectAtTime`)** từ `BAO-CAO-PHAN-TICH.md` lên các layer `05_Scene_Button02` để khung tự ôm khít độ dài chữ tiếng Việt:
     ```javascript
     // Gắn vào thuộc tính Size của Rectangle Path trong Shape Layer (Pill):
     const s = thisComp.layer("05_Scene_Text02");
     const r = s.sourceRectAtTime(time, false);
     const padX = 80; // Padding ngang (4K)
     const padY = 44; // Padding dọc (4K)
     [r.width + padX * 2, r.height + padY * 2];
     ```
   - Áp dụng **Expression đếm số tự động (`Slider Control`)** cho huy hiệu tin nhắn quá tải (Scene 2) và giá tiền/mã đơn `#PK8921` (Scene 3):
     ```javascript
     // Gắn vào Source Text của Badge_Counter:
     Math.round(effect("Slider Control")("Slider")) + "+"
     ```
3. **Bước 3 — Khóa Easing trong Graph Editor (Speed Graph)**:
   - Chọn toàn bộ keyframe `Position` của chữ tiêu đề (`TOS`): Mở `Keyframe Velocity` (`Ctrl + Shift + K`) -> Đặt **Outgoing Influence = `75.2%`**, **Incoming Influence = `75.1%`** (Rule R1).
   - Chọn toàn bộ keyframe `Scale` / `Mask Expansion` của khung thẻ UI: Đặt **Outgoing Influence = `15.2%`**, **Incoming Influence = `100%`** (Rule R10).
4. **Bước 4 — Đồng bộ Voice-Over (VO) & Sound Effects (SFX 48kHz)**:
   - Đặt marker tại đúng các mốc `00:00`, `00:05`, `00:11`, `00:16`, `00:22`, `00:30`, `00:36` và khớp tiếng *Ting! Ting!* (Scene 1), *Whoosh!* (Scene 3A `00:11`), *5 tiếng Pop Marimba* (Scene 3B `00:16.5 – 00:19.0`), *3 tiếng Ding!* (Scene 4) và *Mouse Click + Logo Chime* (Scene 5 `00:33.5`).
