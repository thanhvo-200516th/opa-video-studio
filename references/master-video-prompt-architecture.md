# Kiến trúc Prompt & Quy trình Sản xuất Video AI 8 Tầng (`SPEC-MASTER-VIDEO-PROMPT-ARCH-V1.0`)

Tài liệu tham chiếu chuẩn hoá cho toàn bộ quy trình viết prompt ảnh Keyframe (T2I / Multi-Ref), video chuyển động (I2V / T2V / First-to-Last Frame) và điều phối sản xuất 8 tầng trong `opa-video-studio`.

> **Thứ tự ưu tiên khi dùng trong `opa-video-studio`:**
> Khi dựng talking head / B-roll theo `rules.json` và `references/flow-broll.md`, luôn tuân thủ các luật địa phương của skill (vd: khung `9:16`, quy tắc H5 của `broll_fix.py`, mức giao `-16 LUFS` của luật F3, **không** nối đuôi `"no text, no logos"` khi gửi text-only Google Flow). Tài liệu này cung cấp kiến trúc prompt và pipeline 8 tầng tổng quát ở cấp độ studio (áp dụng cho cả `16:9` lẫn `9:16`, các dự án thương hiệu, phim AI đa cảnh, Keyframe + I2V).

---

## 1. Quy luật Vị trí Từ khoá (Positional Bias)

Cả mô hình Diffusion và Transformer/DiT đều phân bố trọng số Attention không đều theo vị trí token:

| Vùng vị trí | Tác dụng điều hướng | Nội dung BẮT BUỘC đặt tại đây |
| :--- | :--- | :--- |
| **Primacy Zone (20–35 từ đầu tiên)** | Trọng số định hình bố cục & hình học lớn nhất. | `[Khóa ảnh tham chiếu @Image / Frozen Descriptor] + [Cỡ cảnh Shot Size] + [Góc máy Camera Angle] + [Chủ thể chính]` |
| **Middle Zone (Phần giữa)** | Dễ suy giảm chú ý (*Lost in the Middle*) hoặc *Attention Bleeding* (lem màu/đặc điểm giữa các đối tượng) nếu viết thành một câu dài lê thê. | Chia thành các **khối nhãn in hoa** với mệnh đề độc lập:<br>`SUBJECT ACTION:` …<br>`ENVIRONMENT:` …<br>`LIGHTING & OPTICS:` … |
| **Recency Zone (Câu kết thúc)** | Đóng vai trò bộ lọc khóa cuối cùng của khung hình. | `[Clean-Frame & Temporal Stability Lock]` — vd: `"Smooth 25fps cinematic motion, consistent facial geometry, anatomically correct hands with five fingers, zero morphing. Clean frame with no text, no subtitles, no watermarks."` |

> **Ngoại lệ bắt buộc cho Google Flow Text-to-Video (T2V B-roll):** Flow không có ô Negative Prompt riêng; đặt cụm `"no text, no logos"` ở cuối có thể bị hiểu ngược thành vẽ chữ/logo. Với Flow T2V, thay Recency Zone bằng **ràng buộc khẳng định (Affirmative Clean-Frame Cues)**: `"unbranded, blank surface, out of focus, clean frame"` (xem `references/flow-broll.md` & `references/script-to-flow-broll.md`).

---

## 2. Luật Mã hoá T5-XXL / Gemma vs. CLIP

Các mô hình hiện đại (`Flux.1`, `Nano Banana / Imagen 3`, `Veo 3`, `Sora`, `Kling 2.0`, `Google Flow Omni 1.2 Flash`) dùng bộ mã hoá **LLM / T5-XXL / Gemma**, khác hoàn toàn thế hệ **CLIP** cũ (`SD 1.5`, `SDXL`, `Midjourney v5`):

| Đặc tính | CLIP Encoder (Cũ) | T5-XXL / Gemma / LLM Encoder (Hiện đại) |
| :--- | :--- | :--- |
| **Context Window** | Cứng **77 tokens** (sau token 77 bị cắt/giảm lực). | **256–512+ tokens**, đọc trọn vẹn đoạn mô tả có cấu trúc. |
| **Ngữ pháp & Không gian** | Yếu với giới từ; ưu tiên tag danh từ ngăn cách bởi dấu phẩy. | Hiểu chuẩn **mệnh đề quan hệ, trái/phải/trước/sau/trên/dưới, trình tự thời gian** và chữ viết trong ngoặc kép `""` (chỉ dùng ngoặc kép khi T2I/VFX **cố ý** render chữ). |
| **Nhấn trọng số** | Dùng `(keyword:1.3)` hoặc `keyword::2`. | **CẤM dùng `(keyword:1.3)` hoặc `keyword::2`** — bộ mã hoá T5-XXL/Gemma đọc dấu ngoặc và số như ký tự rác/chữ viết. Phải dùng **Khuếch đại ngữ nghĩa (Semantic Amplification)** và tiêu đề khối in hoa (`SUBJECT ACTION:`, `LIGHTING & OPTICS:`). |
| **CFG Scale ($w$)** | Đẩy $w$ cao dễ cháy tương phản. | Giữ $w$ ở mức tự nhiên; $w$ quá cao đẩy mẫu ra khỏi đa tạp ảnh thật, tạo bề mặt bóng nhựa CGI và cứng cơ mặt. |

---

## 3. Quy tắc Anti-Slop: Cấm từ sáo rỗng, thay bằng Vật lý & Quang học đo lường được

Prompt chung chung (như *"a handsome Vietnamese man in an office"*) hoặc nhồi từ khoá sáo rỗng đẩy vector điều kiện về **Tâm điểm trung bình (Centroid / Mode Collapse)** của tập dữ liệu huấn luyện — gây lỗi **"Tượng sáp" (Symmetry Drift)** với gương mặt đối xứng giả và da bóng nhựa.

**Danh sách từ CẤM (Anti-Slop Forbidden Fluff):**
- `stunning`, `breathtaking`, `hyper-detailed`, `hyperdetailed`, `8k`, `4k masterpiece`, `masterpiece`, `magical`, `very realistic`, `ultra realistic`, `ultra-realistic`, `photorealistic masterpiece`, `award-winning`, `best quality`.

**Bảng thay thế bằng thông số đo lường được:**

| Thay vì viết (Slop) | Thay bằng (Vật lý / Quang học / Sinh học) |
| :--- | :--- |
| `very realistic, hyper-detailed face` | `unretouched human skin with visible micro-pores, natural facial asymmetry, wet aqueous iris depth, fine flyaway baby hairs` |
| `stunning lighting, magical mood` | `warm golden hour volumetric sunbeams through dusty high factory windows, soft 3200K tungsten fill, crisp rim light on shoulders` |
| `8k masterpiece, cinematic` | `shot on Arri Alexa Mini LF, Atlas Orion 40mm Anamorphic at f/1.4, Kodak Vision3 500T color science, subtle 2.5% 35mm film grain` |
| `high quality fabric` | `heavyweight olive-green cotton trench weave with natural shoulder crease and tactile stitching` |

---

## 4. Cấu trúc 7 Thành phần Keyframe (T2I / Multi-Ref) & 4 Khóa Sinh học Chống Tượng Sáp

### 4.1. Khung 7 Thành phần T2I

1. **`SHOT SIZE, ANGLE & ASPECT RATIO`**: Cỡ cảnh, góc máy, bố cục (`--ar 16:9` hoặc `9:16`).
2. **`ACTIVE REFERENCES (@Image 1..N)`**: Nguồn ảnh khóa mặt, dáng, bối cảnh.
3. **`SUBJECT IDENTITY & 4 BIOLOGICAL ANTI-WAX LOCKS`**: Chuỗi nhận diện cố định (`Frozen Descriptor String`) + 4 khóa sinh học bên dưới.
4. **`WARDROBE & MATERIAL PHYSICS`**: Trang phục mô tả từ ngoài vào trong, chất liệu vải, nếp nhăn tự nhiên.
5. **`ENVIRONMENT & DEPTH LAYERS`**: Tiền cảnh mờ (foreground bokeh), trung cảnh hành động, hậu cảnh.
6. **`LIGHTING ARCHITECTURE`**: Nguồn sáng chính (key), phụ (fill), ven tóc/vai (rim), nhiệt độ màu (Kelvin).
7. **`CAMERA BODY, LENS OPTICS & FILM STOCK`**: Thân máy, tiêu cự, khẩu độ, đặc tính phim/màu.

### 4.2. Bốn Khóa Sinh học Chống Tượng Sáp (Mandatory Anti-Wax Locks)

Bất kỳ prompt T2I tạo người thật nào cũng phải nhúng 4 khối khóa chi tiết vi mô (High-Frequency Manifold Injection):

1. **`Face & Natural Asymmetry Lock`:**
   > `"Keep @Image 1's exact eye shape, eyelid folds, brow placement, nose bridge and softly rounded tip, lip fullness, and jawline. The face preserves natural human asymmetry: the two eyes, brows, and cheeks are not mirror copies of each other."`
2. **`Skin Texture & Subcutaneous Flush Lock`:**
   > `"Real unretouched human skin with visible micro-pores, natural subcutaneous warmth, a subtle rosy flush across the cheeks and nose bridge, and signature moles/marks. Zero waxy sheen, zero plastic airbrushing."`
3. **`Hair Strand & Flyaway Lock`:**
   > `"Individual hair strands with natural thickness variations, wispy uneven fringe tips, and fine flyaway baby hairs along the crown and temples (never a solid plastic helmet-hair block)."`
4. **`Eye Aqueous Depth & Catchlight Lock`:**
   > `"Dark-brown irises with realistic wet aqueous depth, crisp softbox/window catchlights reflected in both corneas, and natural convergent gaze focused on the target (never blank or cross-eyed)."`

---

## 5. Cấu trúc 4 Trục Động lực học cho Video (I2V Motion Prompt)

> **Quy tắc thép của Image-to-Video (I2V):**
> Khi đã nạp ảnh Keyframe đầu vào, mô hình Video AI đã nhìn thấy toàn bộ màu sắc, trang phục và bối cảnh tĩnh. Lặp lại mô tả tĩnh dài dòng trong prompt I2V sẽ gây nhiễu Cross-Attention và làm cứng chuyển động. **Prompt I2V phải tập trung 100% vào Động lực học theo 4 Trục:**

| Trục | Quy tắc viết | Ví dụ chuẩn |
| :--- | :--- | :--- |
| **1. `Camera Trajectory`** | Chỉ chọn **1 chuyển động máy duy nhất** trong 1 shot ngắn (2–4 s). | `"Slow dolly push-in toward the subject"`, `"Smooth 3D camera orbit from left to right"`, `"Low-angle tracking shot moving backward ahead of the runner"`, `"Static camera locked on a tripod"`. |
| **2. `Primary Subject Action`** | Nêu rõ **State A $\rightarrow$ Action Verb + Speed $\rightarrow$ State B** + vi biểu cảm. | `"The man swiftly pulls the burlap sack upward off the seated woman's head, revealing her surprised face as she blinks twice and smiles slightly."` |
| **3. `Secondary Physics`** | Quán tính phụ quyết định độ thật: tóc bay, nếp vải, hạt bụi trong nắng, khói cuộn, giọt nước bắn, phản chiếu lấp lánh trên mắt. | `"As the rough fabric lifts away, her voluminous silver afro hair springs out naturally and catches the warm golden rim light; dust motes drift through sunbeams."` |
| **4. `Temporal Stability & Clean-Frame Guardrails`** | Khóa ổn định thời gian & sạch khung hình (cho I2V có hỗ trợ/cần khóa). | `"Smooth 25fps cinematic motion, consistent facial geometry, anatomically correct hands with five fingers, zero morphing. Clean frame with no text, no subtitles, no watermarks."` |

---

## 5b. Ánh xạ trực tiếp: Công thức 5 Tầng T2V Anti-Plastic cho Google Flow B-roll (`omni-flash`, T5-XXL/Gemma)

Khi tạo B-roll Text-to-Video (`T2V`) bằng Google Flow (`omni-flash`), không có ảnh Keyframe đầu vào để khóa da/vải/bối cảnh. Nếu chỉ viết một câu ngắn chung chung hoặc dùng ẩn dụ trừu tượng (khối phát sáng, lăng kính, thanh ray kim loại), bộ mã hoá **T5-XXL / Gemma** sẽ trượt về *Centroid Mode Collapse* (da sáp bóng nhựa, ánh sáng neon giả tạo, CGI xa rời lời thoại).

Mọi prompt Flow B-roll chuẩn **H5 / D9** (`18–95` từ tiếng Anh) phải được xây dựng từ **5 tầng JSON (`layers`)** qua Quy trình 3 Agent (`references/script-to-flow-broll.md`):

| Tầng (`layers` key) | Vùng Attention | Thành phần bắt buộc | Quy tắc Anti-Plastic & Khớp nghĩa đen |
| :--- | :--- | :--- | :--- |
| **Tầng 1: `l1_shot_subject`** | **Primacy Zone** | `[Shot Size] + [Camera Angle] + Vietnamese + [Faceless Lock nếu founder/CEO/speaker] + [Ngoại hình & chất liệu vải thật]` | Khóa danh tính người Việt và chất liệu vải tự nhiên (vd: `wrinkled cotton polo`, `matte linen shirt`). Lặp ≥ 2 cảnh phải copy-paste **Frozen Descriptor** nguyên văn. |
| **Tầng 2: `l2_action_script`** | **Middle Zone (Core)** | `[State A → Action Verb → State B]` minh hoạ **nghĩa đen đời thực** của `anchor_quote` | Tả hành động người & đồ vật đời thường chứng minh câu nói. **CẤM ẩn dụ CGI trừu tượng** (`glowing prism`, `amber cube`, `metal pipeline rails`, `floating nodes`, `energy core`, `gears`, `hologram`, `sci-fi`). |
| **Tầng 3: `l3_environment`** | **Middle Zone (Grounding)** | Bối cảnh công sở / đời thực Việt Nam sống động vừa đủ + ràng buộc bề mặt | Đặt vật thật cụ thể trên bàn/phòng; mọi màn hình/giấy/bảng nếu xuất hiện **bắt buộc** ghi `out of focus`, `blurred`, `defocused`, `blank` hoặc `out of frame`; đồ vật `unbranded`. |
| **Tầng 4: `l4_optics_realism`** | **Anti-Plastic Manifold Injection** | Thông số ống kính tài liệu + ánh sáng tự nhiên + kết cấu sinh học/vật lý vi mô | Bắt buộc có chi tiết quang học/hạt phim/da vải thật (`shot on 35mm documentary lens f/2.8`, `subtle natural handheld camera feel`, `soft overcast window light mixing with desk lamp`, `subtle 35mm film grain`, `unretouched skin texture`, `natural fabric creases`). **CẤM** Anti-Slop (`stunning`, `8k`, `masterpiece`, `very realistic`) & từ nhựa/CGI (`glossy skin`, `porcelain skin`, `airbrushed`, `cyberpunk neon`, `octane render`, `unreal engine`). |
| **Tầng 5: `l5_camera_motion`** | **Recency Zone (Kinetic & Clean Tail)** | **Đúng 1** chuyển động máy nhẹ nhàng tự nhiên + khẳng định sạch khung | Vd: `slow gentle push-in, unbranded blank surfaces, clean frame`. **KHÔNG** nối đuôi `no text, no logos`, **KHÔNG** dùng trọng số CLIP `(keyword:1.3)`, **KHÔNG** gimbal trơn tuột siêu thực hay cắt cảnh ngầm (`transition/cut/montage/split-screen`). |

**Mẫu ánh xạ 5 tầng hoàn chỉnh (ghép thành 1 đoạn văn `18–95` từ):**
> - *`l1_shot_subject`:* `Over-the-shoulder medium shot of a young Vietnamese woman in a slightly wrinkled beige cotton shirt at a wooden desk,`
> - *`l2_action_script`:* `handing plain manila folders to two Vietnamese teammates beside her who open them together at the same pace,`
> - *`l3_environment`:* `in a lived-in Saigon office with blurred out-of-focus monitors behind and potted plants by a glass window,`
> - *`l4_optics_realism`:* `shot on 35mm documentary lens f/2.8, subtle natural handheld camera feel, soft overcast window light mixing with desk lamp, subtle 35mm film grain, unretouched skin texture, natural fabric creases,`
> - *`l5_camera_motion`:* `slow gentle lateral tracking shot, unbranded blank surfaces, clean frame.`

---

## 6. Từ điển Ngôn ngữ Điện ảnh DOP (Compact Cinematography Lexicon)

| Nhóm | Thuật ngữ chuẩn (Tiếng Anh) | Hiệu ứng & Ngữ cảnh sử dụng |
| :--- | :--- | :--- |
| **Shot Size** | `Extreme Wide Shot (EWS)` / `Aerial Establishing Shot` | Đại cảnh từ xa/trên cao thiết lập không gian hùng vĩ. |
| | `Wide Full Shot (WFS)` | Lấy trọn toàn thân từ đầu đến chân trong bối cảnh. |
| | `Medium Full Shot (MFS)` / `Knee Shot` | Từ đầu gối trở lên — lý tưởng khi nhân vật vừa đi vừa tương tác. |
| | `Medium Close-Up (MCU)` | Từ ngực trở lên — **cỡ cảnh vàng** cho Talking Head & vi biểu cảm. |
| | `Extreme Close-Up (ECU)` / `Macro Detail Shot` | Đặc tả cực cận mắt, ngón tay, vật thể chuyển động chậm. |
| **Camera Angle** | `Eye-Level Shot` | Ngang tầm mắt — kết nối trực diện, trung thực. |
| | `Low-Angle Hero Shot` | Đặt máy thấp hất lên — tạo cảm giác quyền lực, choáng ngợp. |
| | `High-Angle Looking Down` / `Overhead Bird's-Eye` | Nhìn từ trần/trên cao xuống — phô diễn bố cục & bóng đổ dài. |
| | `Over-the-Shoulder Shot (OTS)` | Sau vai nhân vật A nhìn về B hoặc bàn làm việc (tốt cho giấu mặt A-roll). |
| | `Under-Desk Low-Angle Framing` | Đặt máy thấp xuyên qua gầm bàn mở ra không gian mới. |
| **1-Shot Kinematics** | `Static locked-off tripod shot, one continuous take` | Khóa cứng khung — bắt buộc cho cảnh thoại dài hoặc ghép VFX. |
| | `Slow push-in dolly` / `Pull-back tracking shot` | Đẩy tiến thu hẹp chú ý / kéo lùi bám nhân vật đang tiến tới. |
| | `3D Camera Orbit / 180-degree Arc Shot` | Máy xoay cung quanh chủ thể (kết hợp `Bullet-time frozen motion`). |
| | `Whip-pan` / `Whip-tilt Match Cut` | Lia ngang/dọc cực nhanh tạo motion blur nối cảnh tiếp theo. |
| | `Passing-by Foreground Wipe` | Người/vật thể lướt ngang sát ống kính che kín khung mở ra cảnh mới. |
| **Optics & Lighting** | `Arri Alexa Mini LF, Atlas Orion Anamorphic 40mm f/1.4` | Màn ảnh rộng, DOF mỏng, bokeh bầu dục và flare ngang. |
| | `Phase One IQ4 150MP, 80mm f/9 Medium Format` | Nét sâu từ tiền cảnh đến hậu cảnh cho nhóm đông người, không méo. |
| | `Volumetric God Rays / Golden Hour Backlit Rim Light` | Tia nắng xuyên bụi, tách viền tóc và vai nhân vật. |
| | `Chiaroscuro High-Contrast / Emerald & Slate Fantasy Grade` | Tương phản sáng tối kịch tính pha ánh sáng hiệu ứng chuyên biệt. |

---

## 7. Tóm tắt Kiến trúc Sản xuất 8 Tầng (Layer 0 $\rightarrow$ Layer 7)

| Tầng | Tên tầng & Đầu ra chính | Quy tắc cốt lõi & Liên kết trong `opa-video-studio` |
| :---: | :--- | :--- |
| **Layer 0** | **Meta-Prompt & System Guardrails**<br>`00_System_Constitution.json` | Khóa Aspect Ratio (`16:9` hoặc `9:16`), FPS (`24/25/30`), bảng màu thương hiệu, Target Loudness, danh sách từ CẤM Anti-Slop và mã định danh `@CHAR_ID`, `@ENV_ID`, `@STYLE_ANCHOR`. |
| **Layer 1** | **Ideation, Concept & Creative Direction**<br>`01_Creative_Brief.md` | Xác định Core Insight, **3-Second Hook** (*Visual Hook 0–1.5s* + *Verbal Hook < 15 từ*), Ẩn dụ thị giác (Visual Metaphor) và leo thang 4 Chương. |
| **Layer 2** | **Narrative, Script & Master Storyboard**<br>`02_Master_Storyboard.json` | **Atomic Action Rule:** 1 shot `0.8–4.5 s` = 1 hành động + 1 chuyển động máy; **cấm 2 shot liên tiếp trùng cỡ cảnh/góc máy**; thiết kế nối cảnh (`Hard Cut on Action`, `Match Cut`, `Foreground Wipe`, `Start-to-End Morph`).<br>**`normalize_vi_tts`:** tách riêng `vo_sub_display` (`"599K"`, `"LV1"`) và `vo_tts_phonetic` (`"năm trăm chín mươi chín nghìn"`, `"level một"`) — dùng `scripts/normalize_tts.py` / `analyze_and_scaffold.py`. |
| **Layer 3** | **Visual Bible & Asset DNA Consistency**<br>`03_Visual_Bible.json` + Turnaround `CS01` | Dựng bảng nhân vật 4 góc (`Front`, `3/4`, `Side`, `Back`) trên nền xám trung tính `#D2D4D6`. Đóng băng **Frozen Descriptor String (35–50 từ)** cho mỗi nhân vật/bối cảnh — copy-paste nguyên văn xuyên suốt mọi shot ở Layer 4–5, cấm viết lại bằng từ đồng nghĩa. |
| **Layer 4** | **Keyframe Synthesis (T2I)**<br>`SHXX_first.png` & `SHXX_last.png` | **Single Keyframe (`First Frame Only`)** cho cảnh đi/nói/orbit liên tục. **Dual Keyframe (`First Frame` + `Last Frame`)** cho biến đổi phức tạp (lột vật che, đổi trang phục, biến đổi bối cảnh): dùng Inpainting/Image Editing sửa trực tiếp trên `First Frame` để giữ nguyên góc máy & ánh sáng. |
| **Layer 5** | **Motion, Physics & Video Gen (I2V / T2V)**<br>`XX_SHXX_raw.mp4` | Áp dụng **4-Axis Motion Prompt** và **Model Routing Matrix**:<br>• *Start/End Frame Morph:* **Kling 1.6 / 2.0 Master (Start/End)** (dự phòng: Luma Ray 2 / Vidu)<br>• *Vật lý phức tạp / 3D Orbit / Combat:* **Kling 2.0 Master** (dự phòng: Veo 2/3, Runway Gen-4)<br>• *Thoại trực diện tiếng Việt & Room Tone:* **Google Flow (`veo-3-1-fast`)** (dự phòng: HeyGen Avatar IV, OmniHuman-1)<br>• *Đại cảnh thiên nhiên / Sóng / Khí quyển:* **Google Veo 3 / Sora** (dự phòng: Hailuo MiniMax)<br>• *B-roll Text-only cho Talking Head Việt:* **Muse** hoặc **Google Flow (`omni-flash`)** theo `references/flow-broll.md` & `scripts/broll_fix.py`. |
| **Layer 6** | **Audio, Voiceover, SFX & Lip-Sync**<br>`VO_Master.wav`, `BGM.wav`, `SFX_Stems/` | 4 Stem: (1) VO/Dialogue `A1` (HPF 80 Hz, comp 3:1, đỉnh `-3…-5 dBFS`); (2) Lip-Sync Pass (Kling Lip-Sync / Sync.so cho clip động cần thoại); (3) Dynamic BGM `A2` (ducking `15–20 LU` dưới giọng); (4) Foley & Transition SFX `A3–A4` (`-8…-12 dBFS`). Đồng bộ với `scripts/audio_levels.py` và luật F1–F5. |
| **Layer 7** | **Post-Production, VLM QA & Mastering**<br>`QA_Report.json` + Final Clean MP4 | 1. **VLM QA & Trim dead-frames:** Cắt bỏ `0.3 s` khựng đầu hoặc `0.5 s` biến dạng cuối mỗi clip AI.<br>2. **VFX & Depth Masking:** Đặt chữ lớn sau chủ thể (hoặc `scripts/matte.py` / `behind_person` trong FilmCraft).<br>3. **Color & Grain:** Phủ LUT thống nhất + `2.5% 35mm Film Grain` xóa ranh giới giữa các model AI.<br>4. **Clean Metadata Delivery:** Chuẩn hóa loudness (`-12.9 LUFS` bản thương mại hoặc `-16 / -14 LUFS` theo luật F3 của skill) và chạy `ffmpeg -i input.mp4 -map_metadata -1 -c:v copy -c:a copy output_clean.mp4` (hoặc `scripts/apps/strip-media-metadata/scripts/strip_metadata.py`). |

### Giao thức Dữ liệu Hợp nhất (`Unified_Production_State.json`)

Mỗi dự án đa tầng nên lưu một trạng thái JSON xuyên suốt gồm các khối:
- `layer_0_constitution` (`project_id`, `aspect_ratio`, `resolution`, `fps`, `target_lufs`, `brand_palette`, `global_negative_guardrails`)
- `layer_1_creative_brief` (`core_insight`, `hook_visual`, `hook_verbal`, `core_metaphor`)
- `layer_3_visual_bible` (`style_anchor`, `characters` với `frozen_descriptor` + `ref_images`)
- `shots_pipeline[]` (`shot_id`, `layer_2_storyboard`, `layer_4_keyframes`, `layer_5_motion`, `layer_6_audio`, `layer_7_post_qa`)

---

## 8. Bảng Kiểm Nghiệm Thu 8 Điểm (8-Point Quality Gate Checklist)

Trước khi chạy render hàng loạt ở Layer 4–5 hoặc xuất bản ở Layer 7, kiểm tra đủ 8 cổng:

- [ ] **Gate 1 (Layer 0):** Đã khóa cứng tỷ lệ khung (`16:9` / `9:16`), FPS, và loại sạch từ Anti-Slop (`stunning`, `8k masterpiece`, `magical`, `very realistic`) + cú pháp `(keyword:1.3)` khỏi mọi prompt chưa?
- [ ] **Gate 2 (Layer 1):** 3 giây đầu đã có **Pattern Interrupt** (hình ảnh gây tò mò + câu mở đầu ngắn) thay cho intro logo tĩnh chưa?
- [ ] **Gate 3 (Layer 2):** Mỗi shot đã đạt **1 Shot = 1 Hành động + 1 Chuyển động máy (`0.8–4.5 s`)** và không có 2 shot liên tiếp trùng cỡ cảnh/góc máy chưa?
- [ ] **Gate 4 (Layer 3):** Mọi nhân vật/bối cảnh xuất hiện > 1 lần đã có ảnh gốc (`@Image`) và **Frozen Descriptor String** copy-paste nguyên văn giữa các cảnh chưa?
- [ ] **Gate 5 (Layer 4):** Mọi keyframe người thật đã nhúng đủ **4 Anti-Wax Locks** (`Asymmetry`, `Micro-Pore Skin`, `Flyaway Hair`, `Aqueous Eye Catchlight`), và cảnh biến đổi đã có đủ `First Frame` + `Last Frame` chưa?
- [ ] **Gate 6 (Layer 5):** Prompt I2V đã bỏ mô tả tĩnh dư thừa để tập trung vào **4 Trục Động lực học**, còn Flow T2V đã viết đủ **5 tầng Anti-Plastic (`l1`–`l5`, `18–95` từ)** bám nghĩa đen `anchor_quote`, cấm ẩn dụ CGI trừu tượng, bỏ đuôi phủ định và dùng từ khóa khẳng định sạch khung chưa?
- [ ] **Gate 7 (Layer 6):** Lời đọc đã chuẩn hóa qua `normalize_vi_tts` (`scripts/normalize_tts.py`), và mỗi điểm cắt cảnh đều có Foley/Transition SFX đúng mức âm lượng chưa?
- [ ] **Gate 8 (Layer 7):** Đã **trim dead-frames** đầu/cuối clip, cân loudness đạt chuẩn, và xóa sạch metadata (`-map_metadata -1` / `strip_metadata.py`) trước khi giao chưa?
