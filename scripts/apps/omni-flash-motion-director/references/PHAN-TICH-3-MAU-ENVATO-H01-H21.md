Ngày đọc: 23/10/2026 · Nguồn: 3 mẫu Envato tìm bằng từ khóa "ai chatbot promo"
Trạng thái: phân tích từ video preview, cây project Envato công bố và video hướng dẫn. **Chưa mở file .aep**: trên máy không có bản tải của 3 mẫu này (đã quét `Downloads`, `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/`, `/media/vmiz/Over Powers/video AE`).

# Phân tích hiệu ứng 3 mẫu "AI chatbot promo"

## 0. Đọc nhanh

- **Mẫu 1** (Ae_Rocket): bộ 30 cảnh giao diện chatbot sáng màu, kiểu "UI pack". Học được: bong bóng chat tự giãn theo chữ, chấm tròn kéo thành ô nhập, danh sách chọn kiểu bánh xe, con trỏ bấm nút.
- **Mẫu 2** (refinality): promo kể chuyện nền tím tối. Học được: mạng lưới bung ra từ logo, huy hiệu thông báo đếm số, khung chat nghiêng vào, câu hỏi kèm nút chọn, từ cuối câu đổi liên tục, chớp màu chuyển cảnh.
- **Mẫu 3** (Yura_Kobitovich): bản MOGRT cho Premiere, nền đen tối giản. Học được: máy bám theo chữ đang gõ, zoom ra lộ thiết bị, điện thoại trồi lên với tin nhắn.
- **21 hiệu ứng** ở mục 4 đã quy về công thức After Effects, câu prompt Omni Flash và mức hợp thương hiệu OPA.
- **Các hiệu ứng đã được đem dùng** trong kịch bản promo 32 s: `OPA-Motion-graphic-mascot/flow-omni/KICH-BAN-PROMO-CHATBOT-OPA.md`.

> Cột "Cách dựng trong AE" là **suy từ hình**, chưa phải dữ liệu đọc từ file. Tên comp, thư mục và lớp điều khiển là **dữ liệu thật**, lấy từ mục "Inside the file" của Envato và video hướng dẫn. Muốn có keyframe, easing và expression thật như bộ phân tích ngày 21/10 thì phải có file .aep (mục 5).

## 1. Thông tin 3 mẫu

| | Mẫu 1 | Mẫu 2 | Mẫu 3 |
|---|---|---|---|
| Tên | AI Chatbot Promo Agent Builder UI Pack | AI Chat Agent Promo | AI Chatbot Promo for Premiere Pro |
| Tác giả | Ae_Rocket | refinality | Yura_Kobitovich |
| Link | [envato](https://app.envato.com/search/all/video-templates/659edcd0-f195-4f38-9f15-11f0660d07ac) | [envato](https://app.envato.com/search/all/video-templates/b67cac33-0451-4281-a7c8-1bf97c483e2a) | [envato](https://app.envato.com/search/all/video-templates/41a7034d-8ff7-4f2e-a0df-874ba5ef7385) |
| Phần mềm | After Effects CC | After Effects CC | **Premiere Pro** (MOGRT) |
| Khung | 1920 × 1080 | Co giãn được (comp 4K và Full HD) | 3840 × 2160 |
| fps · dài | 24 fps · 124 s | 30 fps · 56 s | 30 fps · 30 s |
| Plugin | Không cần | Không cần | Không cần |
| Gói tải | 10 MB: aep, mp4, pdf, txt | 155 MB: aep, mov, mp4, png, txt | 32,4 MB: mogrt, mp4, txt |
| Tông màu | Sáng, pastel, nền khối màu nhòe | Tím tối, viền phát sáng hồng tím | Đen, xám, chữ trắng |
| Nhạc | Không ghi | "Future Technology Industrial" (bán riêng) | "Emotional Background Electronica" (bán riêng) |

Mẫu 3 có bản After Effects riêng cùng tác giả, tên "AI Chatbot Promo". Envato liệt kê bản này trong mục "Similar by Yura_Kobitovich"; tôi chưa mở trang đó.

## 2. Cấu trúc project (dữ liệu thật từ Envato)

### Mẫu 1 · `AI Chatbot Promo Agent Builder UI Pack.aep` (369 mục, 68 comp)

| Thư mục | Số mục | Nội dung thấy được (Envato chỉ hiện 20 mục đầu mỗi thư mục) |
|---|---:|---|
| `01_MAIN_COMPS` | 30 | 30 cảnh tên thương hiệu giả "LUMORA": `_01_Bot_From_Prompt`, `_02_Support_Flow`, `_03_Support_Chat`, `_04_Agent_Setup`, `_05_Shop_Widget`, `_06_Template_Gallery`, `_07_Sales_Agent`, `_08_Lead_Router_Flow`, `_09_Demo_Booking_Chat`, `_10_Sales_Agent_Setup`, … `_20_Screening_Flow`, +10 |
| `02_PRECOMPS` | 36 | `PRE_01_Button` … `PRE_20_Button`, +16: nút bấm tách thành precomp riêng để tái dùng |
| `03_ASSETS` | 298 | Mỗi cảnh ("SLD" = slide) có bộ riêng: `SLD_01_BG_Gradient`, `SLD_01B_BTN_Base`, `SLD_01B_BTN_Shine`, `SLD_01_CARD_Result_0x_Tile`, `SLD_01_CARD_Result_03_ChannelOn_0x`, `SLD_01_DECOR_Avatar_0x_Disc`, `SLD_02_NODE_0x_Tile`… |
| Gốc | 2 | `PREVIEW` (lưới 2 × 2 bốn cảnh), `PROMO_AI` (đoạn promo 0–30 s) |

**Cách tổ chức:** mỗi cảnh là một comp độc lập. Tài sản đặt tên theo `SLD_<số cảnh>_<loại>_<tên>`. Nút bấm gồm hai lớp: `BTN_Base` (thân nút) và `BTN_Shine` (vệt sáng chạy qua).

### Mẫu 2 · `AI Chat Agent Promo.aep` (115 mục, 114 comp)

| Thư mục | Nội dung |
|---|---|
| `01. Edit Comps` (37) | `-> Edit Logo/Logo_Holder`, `-> Edit Music/Music_Holder`; mỗi cảnh có comp chữ `0x_Scene_Text01/02`; cảnh 2 có `Edit_Icons/Icon_Holder_01…06` và `Edit_Persons_Avatar/01…08_Person_Holder` |
| `02. Final Render` (2) | `Final_4k (3840 x 2160)`, `Full_HD (1920 x 1080)` |
| `03. Other/1) Scene Comps` (46) | `01_Scene` + `01_Scene_Color_Flash`; `02_Scene` + `02_Scene_EdgeGlow`, `Avatar_Comps`, `Icon_Comps`; `04_Scene_AlertComp`, `Notification_Comps`, `04_Scene_Counter01/02`, `Number_Counter/Numbers_Comp01/02`; `05_Scene_Button`, `05_Scene_Color_Flash`… |
| `03. Other/2) Assets` (12) | `Icons/01…09_Icon.png`; `Pre_Render/02_Scene_Lines.mov` |
| `03. Other/3) Controls` (7) | `Background Colors`, `Camera_Control`, `Guide_Layer`, `Icons, Buttons & UI Colors`, `Num_Control`, +2 |
| `03. Other/4) Solids` (3) | `Background`, `Edge_Glow`, `Flash` |

**Đọc từ video hướng dẫn (5:40):**
- Lớp `Background Colors` có `BG_Color_01…04` (Color Control) và `Flash_Transition` (Checkbox Control, bật/tắt chớp chuyển cảnh).
- Comp `Final_4k` 30 fps có ba lớp điều khiển ở trên cùng: `Text Colors`, `Background Colors`, `Icons, Buttons & UI Colors`. Marker comp chia cảnh `01_Scene` … `06_Scene`.
- Đổi màu một lần là cả phim đổi theo, vì mọi lớp lấy màu từ đây bằng expression. Ở phút 4–5 video hướng dẫn đổi cả mẫu sang tông xanh dương.
- **Đường nối của mạng lưới là video dựng sẵn** (`02_Scene_Lines.mov`), không phải shape động. Mẹo này giảm thời gian render.

### Mẫu 3 · MOGRT

`AI_Chatbot_Promo_MOGRT/MOGRT Files/AI Chatbot Promo.mogrt` (912,7 KB), `Font/Fonts Link.txt`, `Help/Help.mp4`. Không có file .aep. Sửa chữ trong bảng Essential Graphics của Premiere. File MOGRT xuất từ AE thường gói project AE bên trong, nhưng phải mở mới biết bản này có hay không.

## 3. Dòng thời gian từng mẫu

Đọc bằng cách lấy khung hình mỗi 0,25–0,75 s ngay trong trình duyệt. Tờ khung hình lưu ở `khung-xem/` (ảnh nhỏ, chỉ để tra cứu nội bộ).

### Mẫu 1 · đoạn `PROMO_AI` (0–30 s), sau đó là lưới 30 cảnh

| Giây | Cảnh | Hiệu ứng (mã ở mục 4) |
|---|---|---|
| 0–2 | Bong bóng khách gõ "Can you make my AI chatbot look amazing?" | H06 bong bóng giãn theo chữ |
| 2–4 | Avatar bot, ba chấm "đang gõ", trả lời "Absolutely. Meet AI Chatbot Promo." + chip gợi ý bật lần lượt | H06, chip bật so le |
| 4,5 | Khối màu xanh lá quét kín màn hình | H01 chớp/quét màu |
| 5–8,5 | Bức tường thẻ UI nghiêng, máy trôi; thẻ trắng ở giữa đếm "3 → 20 → 30 chatbot & agent scenes" | H13, H14 |
| 9 | Vệt chéo xanh quét | H01 |
| 9,5–14 | Cột chữ "Chat apps / Website widgets / Agent builder / Setup wizards / Template gallery" cuộn lên từng mục; mục đang chọn đậm, có vạch dọc; thẻ UI bên phải đổi theo | H05 |
| 14,5 | Quét màu chéo xanh dương → xanh lá | H01 |
| 15–20 | "Your brand. Every bubble." hiện từ nhòe; thẻ chat đổi tông màu bằng vạch quét dọc | H03, H16 |
| 20,5–24,5 | "Type a message. The bubble follows." Chấm tròn kéo thành ô nhập, bong bóng câu hỏi, ba nút có nhãn trượt vào so le | H03, H07, H06 |
| 25 | Quét màu xanh lá | H01 |
| 25,5–29,5 | Thẻ trắng phóng ra, "AI Chatbot Pack" gõ chữ (chữ 2 màu nhấn), hàng chip có dấu tích | H21 |
| 30–124 | Lưới 2 × 2: mỗi nhóm bốn cảnh chạy ~2,5 s rồi tan vào nền khối màu nhòe ~2 s | H20 |
| 31,6–34,8 (trong lưới) | "Describe your bot. Lumora builds it.": chữ gõ trong ô prompt có con trỏ nhấp nháy, chuột di tới nút "Generate" rồi bấm | H09 |

### Mẫu 2 · 56 s, 30 fps

| Giây | Cảnh | Hiệu ứng |
|---|---|---|
| 0–0,3 | Chớp màu hồng tím | H01 (`01_Scene_Color_Flash`) |
| 0,45–3 | "Building a strong community / is real success": chữ chạy từ trái sang kèm nhòe ngang; dòng 2 màu nhấn; ra bằng nhòe ngang | H02 |
| 3,2–6,5 | Logo AI lớn → máy lùi; avatar bay vào có nhòe chuyển động; đường nối tự vẽ từ tâm; nút icon bật; vòng ngoài mở rộng | H10 |
| 7–9 | "But managing it all / that's the challenge" | H02 |
| 9,5–12 | Hai avatar có huy hiệu đỏ đếm số tăng nhanh, "Endless notifications" | H11 |
| 12,5 | Chớp màu | H01 |
| 13–15 | "Presenting / AI Agents" + nút "Chat Agent" bật | H03 |
| 15,5–21,5 | Khung chat nghiêng 3D quay vào, viền phát sáng; tin khách → bot gõ → trả lời | H12, H06 |
| 22–26,5 | Tiêu đề đổi từ cuối: "Ready to answer questions" → "Ready to support members" | H04 |
| 27–31,5 | Máy lùi ra thành bức tường thẻ chat, trôi ngang; viên thuốc "Ready to control all processes" | H13 |
| 32–34 | "Build your own AI-powered Agent" | H02 |
| 34,5–42,75 | "How should the agent answer?" / "…sound?": nút lựa chọn bật so le, vệt chọn nhảy giữa các nút | H15 |
| 43,5–47,25 | "Teach your agents with custom data → community content → knowledge sources" | H04 |
| 48–50,25 | Mạng lưới lần hai, lùi xa hơn | H10 |
| 51 | Chớp màu | H01 |
| 51,75–55,5 | "Scale your business with AI Agents" + URL nhỏ | H03 |

### Mẫu 3 · 30 s, 30 fps

| Giây | Cảnh | Hiệu ứng |
|---|---|---|
| 0,6–1,5 | "Turn AI into your workflow" hiện từ nhòe | H03 |
| 1,7–4,6 | Nút "+" bật, ô tìm kiếm kéo dài sang phải; "Work smarter at every step" gõ ra, mép chữ mới mờ dần; máy bám theo chữ sang phải; dừng ở nút ✦ | H07, H08 |
| 4,6–6 | Nút ✦ đứng giữa → zoom ra: hóa ra nó nằm trong dock của máy tính bảng | H17 |
| 6,6–8,4 | "Save hours every single day" | H03 |
| 9–12 | Điện thoại trồi lên, tin nhắn xanh/xám bật lần lượt | H18 |
| 12,6–16,8 | "Stay ahead of the competition" → bong bóng chat trôi khắp màn hình (lớp xa gần) | H13 |
| 17,4–22,8 | Cửa sổ ứng dụng (code + khung chat) trượt vào rồi trôi chậm, tin nhắn hiện dần | H19 |
| 23,4–30 | Chuỗi câu "From request to result", "Designed for every task", "Ready for anything", "my-AI-chatbot.com" | H03 |

## 4. Thư viện 21 hiệu ứng

Cột "OPA" so với BRAND-SPEC:
- ✅ dùng được nguyên;
- ✏️ dùng được nếu chỉnh (đã ghi cách chỉnh);
- ❌ trái luật thương hiệu.

| Mã | Hiệu ứng | Thấy ở | Cách dựng trong AE (suy từ hình) | Viết cho Omni Flash | OPA |
|---|---|---|---|---|---|
| H01 | Chớp / quét màu chuyển cảnh | M2 0,3 · 12,5 · 51 s; M1 4,5 · 9 · 14,5 · 25 s | Solid `Flash` hoặc shape phủ kín. M2: Opacity 0 → 100 → 0 trong ~8 khung, bật tắt bằng checkbox `Flash_Transition`. M1: shape quét chéo, Position đi ngang khung | `a flat #0068FF panel sweeps across the frame from left to right and clears` | ✏️ Bỏ gradient hồng tím; dùng khối #0068FF phẳng quét |
| H02 | Chữ chạy từ trái kèm nhòe ngang | M2 0,45–3 · 7–9 · 32–34 s | Text Animator, Range Selector theo ký tự, Start 0 → 100 %; trong animator: Opacity 0, Position X +40, Blur ngang (hoặc Scale X 150 %); Ease out | Không giao cho Omni (chữ tiếng Việt hỏng) | ✅ Làm trong AE |
| H03 | Chữ hiện từ nhòe theo từ | M1 15 · 20,5 s; M3 nhiều câu | Animator theo Words: Blur 20 → 0, Opacity 0 → 100, Tracking −20 → 0; offset từng từ 2 khung | Không giao cho Omni | ✅ AE |
| H04 | Đổi từ cuối câu | M2 22 · 43,5–47 s | Phần đầu câu giữ nguyên; từ cuối là layer riêng (hoặc Source Text keyframe); từ cũ nhòe bay lên, từ mới nhòe đi vào; chu kỳ ~1,5 s | Không giao cho Omni | ✅ AE: "OPA **trả lời** / **ghi CRM** / **báo cáo**" |
| H05 | Danh sách cuộn kiểu bánh xe chọn | M1 9,5–14 s | Các dòng chữ con của một Null; Position Y của Null nhảy mỗi ~0,9 s (Easy Ease); Opacity từng dòng bằng expression theo khoảng cách tới dòng giữa; vạch dọc đánh dấu đứng yên | Không giao cho Omni | ✅ AE |
| H06 | Bong bóng chat giãn theo chữ + gõ chữ | M1 0–4 · 22–24,5 s; M2 16–26 s | Text Animator kiểu máy đánh chữ (Range Start theo khung). Rectangle của bong bóng lấy Size từ `sourceRectAtTime()` của chữ + lề. Ba chấm "đang gõ" nhún bằng expression sóng sin lệch pha. Chip bật Scale 0 → 110 → 100 lệch 3 khung | Chỉ bong bóng không chữ: `a simple flat chat bubble with three dots pops in` | ✅ AE (chữ tiếng Việt phải đúng) |
| H07 | Chấm tròn kéo thành ô nhập (thanh dài) | M1 20,75–22 s; M3 1,7–2,6 s | Rectangle Size [w, h] từ [h, h] → [w, h], Roundness = h/2, Anchor ở mép trái; Ease out mạnh; M3 có nút "+" bật trước | `a small dot stretches sideways into a long rounded input bar` | ✅ |
| H08 | Máy bám theo chữ đang gõ | M3 2,2–4,6 s | Null "máy quay" làm cha nhóm ô nhập; Position X = −(mép phải chữ) bằng `sourceRectAtTime`, Scale 160 %; khi gõ xong máy dừng ở nút | `the camera stays close and glides right, following the text as it is typed` | ✅ AE |
| H09 | Con trỏ chuột di và bấm nút | M1 31,6–34,8 s | Lớp con trỏ PNG có Position theo đường cong; nút Scale 100 → 94 → 100 trong 6 khung khi bấm; vệt sáng (`BTN_Shine`) chạy qua | `a mouse cursor glides to the button and clicks it; the button presses in briefly` | ✅ |
| H10 | Mạng lưới bung từ logo | M2 3,2–6,5 · 48–50 s | Máy lùi (3D camera hoặc Scale 140 → 100 %); avatar bay từ ngoài vào với Motion Blur; đường nối là `02_Scene_Lines.mov` dựng sẵn; icon bật Scale; viền glow từ comp `EdgeGlow` | `small flat icons burst outward from the logo and settle in a ring; thin straight lines draw themselves from the logo to each icon` | ✏️ **Không dùng ảnh người** (BRAND mục 1) → thay bằng biểu tượng kênh; bỏ glow; nét phẳng |
| H11 | Huy hiệu thông báo đếm số | M2 9,5–12 s | Slider Control trên lớp `Num_Control`; Source Text = `Math.round(slider)`; huy hiệu tròn đỏ co giãn nhẹ mỗi lần tăng | Không giao cho Omni (số phải đúng) | ✏️ Đỏ chỉ dùng `ALERT #E5484D` cho dấu nhỏ, đúng ý "tin bị bỏ sót" |
| H12 | Khung chat nghiêng 3D quay vào | M2 15,5–16,5 s | Lớp 3D: Y Rotation 35° → 0, Z lùi → 0, Ease out; viền phát sáng bằng comp `EdgeGlow` (Glow) | `a flat chat window swings in from a slight angle and faces the camera` | ✏️ Bỏ glow, viền phẳng 2 px #0068FF. Nghiêng 2.5D phẳng chưa có trong BRAND-SPEC → **hỏi Hùng** |
| H13 | Bức tường thẻ + máy lùi trôi | M1 5,5–8,5 s; M2 27–31,5 s; M3 14,4–16,8 s | Lưới precomp trên lớp 3D, khác độ sâu Z; máy lùi + trôi ngang chậm (parallax); thẻ gần chạy nhanh hơn thẻ xa | `the camera pulls back to reveal a wall of chat cards drifting slowly sideways` | ✅ Thẻ trắng viền xanh trên nền phẳng |
| H14 | Bộ đếm số lớn | M1 6,5–7,5 s | Slider 0 → 30, Ease out, Source Text làm tròn | Không giao cho Omni | ✏️ Chỉ đếm thứ có thật (số kênh, số bước). **Không** đếm số kết quả (BRAND mục 7) |
| H15 | Câu hỏi + nút lựa chọn | M2 34,5–42,75 s | Nút viên thuốc bật so le; khối chọn trượt sang nút được chọn (Position, Ease in-out) | Không giao cho Omni | ✏️ Nút được chọn: nền #0068FF chữ trắng; nút khác: viền xanh. Bỏ glow |
| H16 | Đổi tông màu bằng vạch quét | M1 15,5–20 s | Hai bản màu chồng nhau; Linear Wipe hoặc Track Matte theo một vạch dọc chạy ngang | `a thin vertical line sweeps across and the card switches from white to blue behind it` | ✏️ Chỉ đổi trắng ↔ xanh OPA |
| H17 | Zoom ra lộ thiết bị (nối cảnh bằng zoom) | M3 4,6–5 s | Đối tượng giữa khung ở Scale 400 % → 100 %, đồng thời lộ khung thiết bị; Ease in-out | `the camera pulls back and reveals the icon is the avatar inside a chat window` | ✅ Logo OPA → hóa ra là avatar bot trong khung chat |
| H18 | Điện thoại trồi lên, tin nhắn bật | M3 9–12 s | Điện thoại: Position Y từ dưới lên, Ease out; mỗi tin: Anchor ở góc đuôi bong bóng, Scale 0 → 105 → 100; danh sách tự đẩy lên | `a phone rises from the bottom; message bubbles pop in one by one from their tails` | ✅ |
| H19 | Cửa sổ ứng dụng trôi chậm | M3 17,4–22,8 s | Precomp cửa sổ; Position + Scale tuyến tính rất chậm suốt cảnh | `the app window drifts very slowly to the left` | ✅ |
| H20 | Nền khối màu nhòe trôi | M1 0–4 s, giữa các lưới | Hình elip màu + Gaussian Blur lớn, `wiggle()` trên Position | — | ❌ Gradient, nhòe màu trái BRAND mục 1 → dùng nền phẳng |
| H21 | Thẻ tiêu đề + chip có dấu tích | M1 25,5–29,5 s | Thẻ trắng Scale 90 → 100 %, chữ gõ ra (từ thứ hai màu nhấn), chip bật so le 3 khung | — | ✏️ Bỏ kính mờ, bóng đổ; thẻ phẳng viền xanh |

**Cách tổ chức đáng học** (áp cho project AE của OPA):

1. **Một lớp điều khiển màu duy nhất.** Mọi màu lấy từ Color Control bằng expression, như mẫu 2. Với OPA, gắn sẵn năm màu BRAND-SPEC; sau này đổi màu không phải sửa từng lớp.
2. **Comp "Holder" cho thứ khách thay:** `Logo_Holder`, `Icon_Holder_xx`, `Music_Holder`.
3. **Dựng sẵn phần nặng** (`02_Scene_Lines.mov`) để render nhanh.
4. **Marker comp đặt tên theo cảnh** để nhảy nhanh khi sửa.
5. **Mỗi cảnh một comp độc lập**, tài sản đặt tên theo cảnh (`SLD_<số>_<loại>_<tên>`), như mẫu 1.

## 5. Muốn có dữ liệu .aep thật

Bộ phân tích ngày 21/10 (`research/ae-text-audit-2026-10-21`) đã có script đọc .aep bằng ExtendScript chạy nền: `scripts/export-projects.jsx`, `analyze.py`, `build_presets.py`. Script xuất từng layer, hiệu ứng, keyframe, easing và expression. Để chạy cho bộ này:

1. Bạn tải 2 mẫu AE (10 MB và 155 MB) và file MOGRT (32,4 MB) bằng tài khoản Envato của bạn. Envato yêu cầu đăng ký tên dự án cho mỗi lần tải để cấp giấy phép, nên tôi không tải thay được.
2. Giải nén vào `research/envato-chatbot-2026-10-23/nguon/`.
3. Tôi chạy lại các script trên. Kết quả: danh sách effect thật từng layer, đồ thị easing, expression của lớp điều khiển, file `MOTION-PRESETS.json` cho bộ chatbot.

**Lưu ý giấy phép:** không đưa video preview hay file của mẫu Envato vào Google Flow làm tham chiếu chuyển động. Muốn Omni bắt chước một chuyển động, hãy dựng lại chuyển động đó bằng AE với hình OPA rồi dùng bản của mình.
