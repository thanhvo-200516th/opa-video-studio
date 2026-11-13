# kb-talking-head-premiere — toàn văn tài liệu của nguồn `talking-head-premiere`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/talking-head-premiere/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: talking-head-premiere/SKILL.md ===== -->

---
name: talking-head-premiere
description: Dựng hoặc sửa video talking head theo style cá nhân của người dùng trong FilmCraft (.fcproj) hoặc Premiere Pro (.prproj), với icon bám lời nói, caption động, zoom nhấn ý và SFX rõ, đa dạng, nguyên đuôi. Dùng khi yêu cầu áp dụng style talking head đã học hoặc sửa bản dựng theo các tiêu chí này.
---

# Talking Head — FilmCraft & Premiere

## Kết quả

Tạo bản talking head có nhịp thị giác phong phú theo nội dung với sequence và timeline làm việc hoàn chỉnh đã nhập, kiểm tra, lưu trong **FilmCraft (`.fcproj`)** (mặc định trên máy hiện tại) hoặc Premiere Pro (`.prproj`). **Tuyệt đối KHÔNG tự động xuất (export/render) ra file video MP4 sau khi triển khai edit** (trừ khi người dùng yêu cầu rõ ràng xuất MP4): luôn giữ nguyên project và timeline làm việc để người dùng là người kiểm tra, chỉnh sửa và duyệt cuối cùng. Đây là style cá nhân của người dùng, không phải công thức cho mọi talking head. Yêu cầu hiện tại được ưu tiên hơn các mặc định này.

Đọc [references/local-context.md](references/local-context.md) để biết thư viện tài nguyên trên máy (`/home/vmiz/Thanh/Media/TNEDIT/...`, bộ preset FilmCraft) và các bài học từ bản thử. Khi cần chọn nhánh hình ảnh, đọc [references/style-reference.md](references/style-reference.md); đây là phân tích theo khung hình, không chứng minh đặc điểm âm thanh của mẫu.

## Nhịp dựng theo lời nói

- Kiểm tra footage, thông số và audio streams trước khi dựng. Nếu có voice riêng hoặc file mới, kiểm tra đồng bộ, không mặc định nguồn vẫn thiếu âm thanh.
- Lập transcript có thời gian, đối chiếu từ/câu quan trọng. Giữ nghĩa, thứ tự và độ dài theo yêu cầu; không tự thêm số liệu, bằng chứng hay CTA.
- Đặt điểm nhấn theo hook, từ khóa, chuyển ý, đối lập, số liệu, ví dụ và payoff. Phối hợp punch-in/out, icon, caption động, UI/thẻ, chart và minh họa toàn màn hình (kết hợp kho B-roll `/home/vmiz/Thanh/Media/TNEDIT/06_B-Roll/Stock_Theo_Chu_De_PR`). Tránh nhiều giây chỉ giữ nguyên hình rồi thay caption.
- Mật độ hiệu ứng cao nhưng có lý do nội dung. Không cắt theo đồng hồ cố định hoặc thêm whoosh cho mọi cú zoom. Cho thông tin đủ thời gian đọc. Không mặc định dựng chậm/tối giản vì chủ đề cảm xúc.
- Mở bằng điểm nhấn rõ; xen cận/trung cảnh và minh họa, trả về người nói khi cần kết nối. Không chép timing của video cũ sang nội dung mới.

## Icon và asset

- Dùng nhiều icon theo nghĩa đang nói: kiến thức → sách/não, thời gian → lịch/đồng hồ, tiền → ví/thẻ/tiền, AI → chip, tăng trưởng → chart, học nghề → mũ tốt nghiệp, khởi nghiệp → rocket/briefcase. Đây là ví dụ, không phải lịch cue cố định.
- Icon tham gia giải thích: xuất hiện cùng từ khóa, chuyển trạng thái, kết hợp sơ đồ/số liệu. Đổi kích thước và bố cục theo ý; tránh dán cùng badge ở mọi cảnh hoặc lạm dụng một kiểu card.
- Có thể tìm trên https://iconscout.com/. Nguồn vector chính thức: https://iconscout.com/unicons và https://github.com/Iconscout/unicons. Lưu nguồn/license cùng asset. Preview không đồng nghĩa đã có file hoặc quyền dùng premium; không tự mua/đăng ký gói.
- Ưu tiên asset phù hợp trong thư viện người dùng (`/home/vmiz/Thanh/Media/TNEDIT/06_B-Roll/Stock_Theo_Chu_De_PR`, `/home/vmiz/Thanh/Media/TNEDIT/` gồm 24 SVG + 48 PNG/3D Glass Badges tại `07_Assets/Icon_Lucide_Glass_Badge`, 6 UI Cards tại `07_Assets/UI_Card_Glassmorphism`, 3 Backlight Halos + Flash 60fps tại `03_VFX/Halo_Backlight_Flash`, và preset/template của FilmCraft); được tạo thêm SVG/PNG/WebP/video overlay khi thiếu. Chọn media gốc thay vì preview. Không chép tài nguyên thương mại vào gói skill chia sẻ.
- Giữ ngôn ngữ icon, màu và nét nhất quán. Animate bằng scale, slide, overshoot nhẹ, rotate hoặc reveal khi hợp ý (trên FilmCraft có thể kết hợp hiệu ứng `grow`, `shrink`, `move`, `drop_shadow` hoặc preset `[MisterHorse] Smooth Pop-In Elastic`, `[MisterHorse] Smooth Shrink Out`, `[MisterHorse] Slide In Motion Blur`, `[DViet] Slide Up Text Reveal + Motion Blur`, `[DViet] Flash Out & Radial Blur Finisher`, `[DViet] Flicker Strobe Visual Hook`, `[DViet] Floating Rounded Card Frame (PiP)`); không buộc cùng motion cho mọi icon.
- Caption/icon tránh mặt, thông tin chính và vùng giao diện mạng xã hội. Kiểm tra trên hình composited, không chỉ lớp alpha.

## Caption, font và zoom

- Chọn 1–2 font family đọc nhanh trên điện thoại, hỗ trợ dấu tiếng Việt đầy đủ từ `/home/vmiz/Thanh/Media/TNEDIT/01_Font/Google_Fonts_PR` (ưu tiên `BeVietnamPro-Regular.ttf` / `BeVietnamPro-Medium.ttf` / `BeVietnamPro-SemiBold.ttf` / `BeVietnamPro-Bold.ttf` / `BeVietnamPro-ExtraBold.ttf`, `Montserrat-Variable.ttf`, `PlusJakartaSans-Variable.ttf`, `Inter-Variable.ttf` cho caption; `Anton-Regular.ttf`, `Oswald-Variable.ttf`, `BarlowCondensed-Bold.ttf` cho hook; `GreatVibes-Regular.ttf`, `PinyonScript-Regular.ttf`, `AlexBrush-Regular.ttf`, `Allura-Regular.ttf`, `InstrumentSerif-Italic.ttf`, `PlayfairDisplay-Italic-Variable.ttf` khi phối chữ 2 tầng kiểu `@__dviet` / nhánh B).
- Ngắt caption theo nghĩa, thường 3–7 từ, khoảng tối đa 2 dòng khi phù hợp. Nhấn một trọng tâm bằng màu/weight/size. Không biến mọi style thành ALL CAPS. Kiểm tra dấu không bị cắt. Trên FilmCraft có thể dùng lớp `graphic_text`, `caption_tracks` hoặc 11 template `.fcgt` có sẵn: `[SubMachine] Hormozi Dynamic Pop Caption`, `[Captioneer] Viral Reels Pill Subtitle`, `[Editorial] 2-Tier Chest Caption (White + Yellow Impact)`, `[DViet] Dual-Font Calligraphy + Sans Title`, `[DViet] Giant Number + 2-Tier Hook (3 Effects)`, `[DViet] Overlapping Solid + Hollow Stroke Text`, `[DViet] Text Behind Subject Header (ep.2)`.
- Punch-in/out tại câu/từ nhấn hoặc chuyển ý. 105–115% là điểm thử; chỉ tăng mạnh hơn khi nguồn và nội dung cho phép. Chọn điểm neo (`anchor`) để không cắt mặt sai; tránh zoom theo chu kỳ máy móc.
- Chuyển động có vào/giữ/ra, vào nhanh và settle. Khoảng 0,15–0,35 giây là gợi ý thử, không phải hằng số. Dùng motion blur, flash, glitch có chọn lọc (trên FilmCraft có sẵn `[RSMB] Directional Whip Motion Blur`, `[Universe] Finisher RGB Glitch Shake`, `FTG_Overlay_Glitch`).

## SFX rõ, sang, đa dạng, nguyên đuôi

- Kho SFX cục bộ tại `/home/vmiz/Thanh/Media/TNEDIT/02_SFX/Thu_Vien_SFX_PR` (78 file WAV chia theo 14 nhóm: `UI_Click`, `UI_Select`, `Pop`, `Whoosh`, `Swoosh`, `Transition`, `Impact`, `Notification`, `Paper`, `Keyboard`, `Coin`, `Camera`, `Glitch`, `Cinematic`; riser và các bộ SFX khác ở `/home/vmiz/Thanh/Media/TNEDIT/02_SFX`) cùng BOOM Casual UI / POWER PODCAST BUNDLE là nguồn sử dụng chính.
- Chọn theo hành động/ý nghĩa, thay đổi nguồn, texture và take. Không xoay vòng 2–3 take cho cả phút. Kiểm tra cả cặp `source + sourceIn` và cảm giác lặp giữa các họ âm; đổi tên file không làm âm trở nên khác.
- WAV construction kit có thể chứa nhiều biến thể cách nhau bằng im lặng. Chọn một biến thể hoàn chỉnh, gồm attack/body/tail; không phát cả chuỗi. Silence detection chỉ giúp tìm ứng viên: kiểm tra chỗ cắt để không mất đuôi nhỏ.
- Giữ đủ âm và đuôi tự nhiên dù hình đã chuyển. Cho đuôi chồng trên track khác (`A2`, `A3`, `A4`) khi cần. Nếu quá dài, chọn âm khác hoặc đổi thời điểm; không tự cắt/fade sớm để ép theo animation. Âm cuối không bị cụt.
- Cân từng âm theo voice và vai trò. Không giảm đồng loạt 15–21 dB: cách này đã làm V01 quá nhỏ. V02 thử peak khoảng -12,5 đến -8,5 dBFS cho các nguồn cụ thể; đây không phải chuẩn cho mọi file. Peak không phản ánh đầy đủ độ lớn cảm nhận.
- Kiểm tra mix ở mức nghe bình thường: SFX phải nghe rõ và tạo nhấn, lời nói vẫn dễ hiểu. Dùng limiter/ducking có chủ đích (trên FilmCraft có sẵn preset Essential Sound `[CrumplePop] Studio Podcast Voice` cho thoại và `[AutoDuck] Smart BGM Ducking Under Voice` cho nhạc nền tại `/home/vmiz/Thanh/Media/TNEDIT/08_Nhac_Nen/BGM_Thu_Vien_PR`); không vô tình tự nâng/hạ toàn bộ mix. Không nói đã nghe nếu chỉ đo số liệu.
- Đọc [references/premiere-and-audio.md](references/premiere-and-audio.md) khi chuẩn bị audio/timeline hoặc tạo file `.fcproj` cho FilmCraft. Có thể chạy `scripts/audit_sfx.py` để tìm take lặp, kiểm tra mức âm và đuôi vượt thời lượng; không thay thế nghe kiểm tra.

## FilmCraft / Premiere và bàn giao

- **QUY TẮC BẮT BUỘC (KHÔNG TỰ XUẤT VIDEO):** Sau khi triển khai edit xong trên timeline, **KHÔNG tự động xuất/render ra file video (`.mp4`, `.mov`)**. Giữ nguyên trạng thái project (`.fcproj` / `.prproj`) và timeline làm việc nguyên vẹn (đầy đủ các track rời `V1..V5`, `A1..A4`, `C1`, các clip, hiệu ứng và keyframe có thể chỉnh sửa trực tiếp) để người dùng tự kiểm tra và duyệt cuối cùng trên phần mềm. Chỉ được phép chụp nhanh vài frame tĩnh (`file.exportFrame`) nếu cần tự kiểm tra bố cục trong quá trình dựng, hoặc chỉ xuất video khi có lệnh yêu cầu xuất rõ ràng từ người dùng.
- Trên máy hiện tại, ưu tiên tạo, mở và lưu sequence trong project **FilmCraft (`.fcproj`)** (hoặc import qua FCP7 XML `<xmeml>` / FCPXML `<fcpxml>` vào FilmCraft).
- Giữ phiên bản trước, tạo V02/V03 khi sửa đáng kể. Tách rõ các track: Voice (`A1`), SFX (`A2`, `A3`), BGM (`A4`), A-roll (`V1`), B-roll/Overlay (`V2`, `V3`), Icon/Card (`V4`), Caption (`V5` / `caption_tracks`); ưu tiên native (`graphic_text`, keyframes `motion`/`grow`/`shrink`/`move`) khi khả thi. Nếu chữ/icon/zoom đã render thành video overlay, nói rõ giới hạn; không gọi là text/keyframe native.
- Kiểm tra tên sequence, kích thước (`1080×1920`), fps, duration (đơn vị `1 giây = 254,016,000,000 ticks`), media online (`missingMedia: 0`), clip counts, routing audio và đồng bộ. Xem các khung caption nhiều dòng, icon lớn, graphic toàn màn hình và đoạn cuối trên Program Monitor.
- Chỉ báo lưu project/sequence khi đã ghi và xác nhận file `.fcproj` (hoặc `.prproj`) hợp lệ. Nói đúng phần đã/chưa hoàn thành.
- Bàn giao đường dẫn file `.fcproj` (hoặc `.prproj` / `.xml`), tên sequence, cấu trúc timeline làm việc, thay đổi chính và giới hạn chỉnh sửa để người dùng mở kiểm tra cuối. Số lượng SFX/icon không phải bằng chứng duy nhất rằng bản dựng tốt.

<!-- ===== /file: talking-head-premiere/SKILL.md ===== -->

<!-- ===== file: talking-head-premiere/references/local-context.md ===== -->

# Ngữ cảnh cá nhân trên máy

Kiểm tra đường dẫn tồn tại trước khi dựng; ưu tiên hệ thống tài nguyên trên máy Linux hiện tại (FilmCraft `0.13.0`).

## 1. Hệ sinh thái & Thư viện cục bộ trên máy Linux hiện tại (FilmCraft 0.13.0)

| Thành phần | Đường dẫn trên máy | Chi tiết & Cách dùng |
|---|---|---|
| **Phần mềm dựng chính** | `/home/vmiz/.local/bin/filmcraft` | **FilmCraft `0.13.0`** (`ai.storyteller.filmcraft`), hỗ trợ `.fcproj` (JSON schema v15), FCP7 XML (`<xmeml>`), FCPXML (`<fcpxml>`) và Control Server (`--control <port>`). |
| **Project mẫu & Tài liệu Preset** | `/home/vmiz/Minh/Setup/FilmCraft_Pro_Plugin_Suite/` | Chứa `Premiere_Pro_Plugin_Suite_Starter.fcproj` (mẫu cấu trúc `.fcproj` v15) và `README.md` (hướng dẫn **31 Effect Presets**, **11 `.fcgt` Templates** bao gồm bộ `@__dviet` & OpenAudio, 6 LUTs, 4 Essential Sound, 5 Export Presets). |
| **Cấu hình FilmCraft nội bộ** | `/home/vmiz/.local/share/filmcraft/` | Chứa `effect-presets.json` (31 presets), `export-presets.json`, thư mục `Graphics Templates/` (11 file `.fcgt`) và `LUTs/` (`.cube`). |
| **Phần mềm Motion / VFX (Thay AE)** | `/home/vmiz/.local/bin/effectcraft` | **EffectCraft `0.17`**, đã cài sẵn ScriptUI Panel **`DViet & Viral Text VFX Suite.jsx`**, `Animation Composer & TextEvo.jsx`, `Motion & Flow Tools.jsx`, `FX Console.jsx` cùng 4 plugin (`DeepGlow`, `Saber`, `OpticalFlares`, `TwitchGlitch`). |
| **Kho Assets Pro (Icon, UI Card, Halo)** | `/home/vmiz/Thanh/Media/TNEDIT/` | • `07_Assets/Icon_Lucide_Glass_Badge/`: 24 vector SVG + 24 3D Glass Badges (`BADGE_*.png`) + 24 White Icons (`ICO_*.png`).<br>• `07_Assets/UI_Card_Glassmorphism/`: 6 thẻ UI (`Card_DViet_3D_Fanned_Pocket.png`, `Card_DViet_Floating_Frame_Mask_9x16.png`, `Overlay_Bottom_Dark_Vignette_9x16.png`, `Card_AI_Prompt_Input_Glass.png`, `Card_Before_After_Split_Line.png`, `Card_Social_Comment_Bubble.png`).<br>• `03_VFX/Halo_Backlight_Flash/`: 3 quầng sáng Backlight Halo (`Purple`, `Cyan`, `Gold`) cho *Text Behind Subject* + video `OVL_Flash_Out_Burst_60fps.mp4`. |
| **Video gốc (Raw Talking Head)** | `/home/vmiz/Thanh/Media/TNEDIT/04_Footage/Sony_4K_C0009-C0022` | Chứa 14 file quay gốc (`C0009.MP4` đến `C0022.MP4`). Kiểm tra đúng file người dùng yêu cầu trước khi dựng. |
| **Kho B-Roll & Overlay (44 MP4)** | B-roll: `/home/vmiz/Thanh/Media/TNEDIT/06_B-Roll/Stock_Theo_Chu_De_PR`; overlay glitch / light leak / hạt: `/home/vmiz/Thanh/Media/TNEDIT/03_VFX/Overlay_Video_PR`; nền abstract: `/home/vmiz/Thanh/Media/TNEDIT/07_Assets/Nen_Background/Video_Chuyen_Dong_PR` | 13 nhóm chủ đề: `FTG_Business_Work`, `FTG_Creator_Podcast`, `FTG_Data_Analytics`, `FTG_Finance_Money`, `FTG_MotionBG_Abstract`, `FTG_MotionBG_Particles`, `FTG_Overlay_Glitch`, `FTG_Overlay_LightLeaks`, `FTG_Talkhead_Speaker`, `FTG_Tech_AI`, `FTG_Tech_Coding`, `FTG_Time_Clock`, `FTG_UI_Smartphone`. |
| **Kho SFX (78 WAV)** | `/home/vmiz/Thanh/Media/TNEDIT/02_SFX/Thu_Vien_SFX_PR` | 14 nhóm âm thanh: `SFX_UI_Click` (7), `SFX_UI_Select` (8), `SFX_Whoosh` (10), `SFX_Swoosh` (6), `SFX_Transition` (10), `SFX_Pop` (4), `SFX_Notification` (8), `SFX_Impact` (6), `SFX_Cinematic` (4), `SFX_Glitch` (4), `SFX_Paper` (3), `SFX_Camera` (3), `SFX_Coin` (2), `SFX_Keyboard` (3). 8 tiếng trùng (có riser) đã gộp, bản giữ ở `/home/vmiz/Thanh/Media/TNEDIT/02_SFX/TikTok_TalkingHead_Mixkit_Day_Du`; các bộ SFX khác ở `/home/vmiz/Thanh/Media/TNEDIT/02_SFX`. |
| **Kho Nhạc nền BGM (33 MP3)** | `/home/vmiz/Thanh/Media/TNEDIT/08_Nhac_Nen/BGM_Thu_Vien_PR` | 6 nhóm mood: `BGM_Ambient_Deep`, `BGM_Cinematic_Story`, `BGM_Dramatic_Hook`, `BGM_LoFi_Chill`, `BGM_Tech_Corporate`, `BGM_Tech_Electronic`, `BGM_Upbeat_Creator`. |
| **Kho Font chữ (58 TTF)** | `/home/vmiz/Thanh/Media/TNEDIT/01_Font/Google_Fonts_PR`; font script kiểu dviet (`GreatVibes`, `PinyonScript`, `AlexBrush`, `InstrumentSerif`, `PlayfairDisplay`, `Inter`, `PlusJakartaSans`…) ở `/home/vmiz/Thanh/Media/TNEDIT/01_Font/Google_Fonts_Style_DViet` *(đồng bộ `~/.local/share/fonts`)* | Đầy đủ font tiếng Việt & Calligraphy chuẩn `@__dviet`: trọn bộ `BeVietnamPro` (`Regular`, `Medium`, `SemiBold`, `Bold`, `ExtraBold`, `Italic`), `PlusJakartaSans-Variable.ttf`, `Inter-Variable.ttf`, `Montserrat-Variable.ttf`, `Anton-Regular.ttf`, `Oswald-Variable.ttf`, `GreatVibes-Regular.ttf`, `PinyonScript-Regular.ttf`, `AlexBrush-Regular.ttf`, `Allura-Regular.ttf`, `DancingScript-Variable.ttf`, `InstrumentSerif-Italic.ttf`, `PlayfairDisplay-Italic-Variable.ttf`. |
| **Thư mục làm việc** | `/home/vmiz/Thanh/Media/TNEDIT/09_Du_An/vid a huy` | Thư mục lưu bản dựng, manifest và project `.fcproj` (hoặc theo đường dẫn người dùng chỉ định). **Lưu ý: Chỉ lưu project `.fcproj` và giữ nguyên timeline làm việc, không tự xuất MP4.** |

---

## 2. Đường dẫn tham chiếu cũ trên Windows (Khi đồng bộ qua máy khác)

| Nguồn | Vị trí cũ | Cách dùng |
|---|---|---|
| Video mẫu | `E:\talking head` | Học bố cục/nhịp/motion; không tự đưa mẫu vào video mới |
| Footage | `E:\talking head\rawvideo` | Chọn đúng file yêu cầu, không mặc định video 1p |
| BOOM Casual UI | `E:\TaiNguyen\SFX Meme\Boom_Library_Casual_UI_Construction_Kit_WAV` | Click, whoosh, shimmer, impact, card; nhiều WAV chứa chuỗi take |
| POWER PODCAST BUNDLE | `E:\TaiNguyen\POWER PODCAST BUNDLE` | Được dùng toàn bộ asset, gồm SFX, trong bản dựng của người dùng; không cần hỏi lại quyền chọn asset |
| Bản thử trước | `E:\talking head\edit-1p` | MP4, project, XML, transcript, shot/icon/SFX manifests để đối chiếu |

Bundle có 3D ELEMENTS, BACKGROUNDS, CARTOON ELEMENTS, EFFECTS, FRAMES, SFX, SOCIAL MEDIA ELEMENTS, TRANSITION. Money1.mov, Transparent 3d earth.mov, Stopwatch Emoji .mov đã dùng trong 1p.

## 3. Phản hồi thật và giới hạn

- Bản 27 bị đánh giá quá tĩnh, đơn điệu: cần nhiều thay đổi thị giác và nhấn lời nói.
- 1p V01 có 41 shot/zoom và 50 SFX nhưng vẫn ít icon, âm nhỏ và cảm giác lặp. Không lấy các số này làm tiêu chí pass.
- V01 dùng 8 họ SFX, mỗi họ xoay 3 take, giảm gain 15–21 dB. Tránh lặp lại cách chọn/cân này.
- V02 thêm 32 Unicons ở 36 cue, đổi thành 49 take cho 50 sự kiện, cân từng file. Người dùng yêu cầu đóng gói sau V02, chưa xác nhận mọi lựa chọn của V02 đều đạt. Phản hồi mới luôn ưu tiên.
- Được tạo asset mới khi thiếu. Font phải dễ đọc, hợp talking head và hỗ trợ ngôn ngữ.
- **Quy tắc bàn giao bắt buộc từ người dùng:** Sau khi triển khai edit xong, **KHÔNG tự xuất video (MP4/MOV)**. Luôn giữ nguyên project (`.fcproj` / `.prproj`) và timeline làm việc nguyên trạng để người dùng trực tiếp kiểm tra, chỉnh sửa và là người duyệt cuối cùng.

Các manifest cũ chỉ là ví dụ. `build_1p.py`/`revise_v02.py` chứa timing, nội dung và đường dẫn riêng: không chạy như công cụ tổng quát. Không phân phối media thương mại cùng skill.

<!-- ===== /file: talking-head-premiere/references/local-context.md ===== -->

<!-- ===== file: talking-head-premiere/references/premiere-and-audio.md ===== -->

# FilmCraft, Premiere và Audio: Kinh nghiệm thực thi

## Chuẩn bị

Kiểm tra audio streams, duration, fps, resolution bằng `ffprobe`. ASR có timestamps giúp đặt cue, không bảo đảm đúng từng từ. `faster-whisper` trên máy từng lỗi `av` với tham số `metadata_errors`; cách đã chạy được là đọc WAV PCM bằng `wave`/`numpy` rồi truyền mảng audio cho ASR.

Giữ media ở đường dẫn ổn định, không đổi file của project cũ khi dựng phiên bản mới. Overlay alpha là phương án compositing hữu ích, nhưng không tương đương graphics native.

## Manifest SFX và audit

Danh sách JSON, một phần tử cho mỗi sự kiện:

```json
[{"path":"/home/vmiz/Thanh/Media/TNEDIT/02_SFX/Thu_Vien_SFX_PR/SFX_UI_Click_Select_click_1109.wav","start":1.12,"duration":1.77,"source":"/home/vmiz/Thanh/Media/TNEDIT/02_SFX/Thu_Vien_SFX_PR/SFX_UI_Click_Select_click_1109.wav","sourceIn":0.0,"sourceOut":1.77,"gain":-3.0,"key":"ui_click"}]
```

`gain` là thay đổi khi xuất file, không phải mức tuyệt đối. Cặp nguồn + in point giúp phát hiện cùng take đổi tên.

Chạy `scripts/audit_sfx.py manifest.json --video-duration 60.08 --measure`. Script dùng `ffmpeg` để đo peak/RMS, báo take lặp, file thiếu, tail vượt duration. Không normalize, cắt hay sửa audio. RMS có thể thấp vì im lặng/tail; luôn đối chiếu với nghe. `--measure` giải mã toàn file nên dùng có chọn lọc với manifest lớn.

Khi mix bằng `ffmpeg` `amix`, kiểm tra `normalize=0` để tránh vô tình hạ input. Đặt gain trước mix; với limiter, kiểm tra `level` và latency compensation theo phiên bản. Không để `-shortest` hoặc duration giới hạn làm cụt SFX cuối.

---

## Tạo và nhập Project trong FilmCraft (`0.13.0` — `.fcproj`)

Trên máy Linux hiện tại, phần mềm dựng chính là **FilmCraft (`0.13.0`)** (`/home/vmiz/.local/bin/filmcraft`). FilmCraft hỗ trợ 3 phương thức làm việc rất thuận tiện cho AI:

### 1. Tạo/chỉnh sửa trực tiếp file `.fcproj` (Khuyên dùng)
- File `.fcproj` là định dạng JSON thuần túy (`"format": "filmcraft.project"`, `"schema_version": 15`, `"generator": "FilmCraft 0.13.0"`). Tham khảo cấu trúc chuẩn tại `/home/vmiz/Minh/Setup/FilmCraft_Pro_Plugin_Suite/Premiere_Pro_Plugin_Suite_Starter.fcproj`.
- **Đơn vị thời gian (Ticks):** FilmCraft dùng chung đơn vị ticks với Premiere Pro:
  $$\text{1 giây} = 254\,016\,000\,000 \text{ ticks}$$
  Mọi trường `start`, `duration`, `source_in` của clip và `time` của keyframe đều tính bằng số nguyên `ticks` (`int(round(seconds * 254_016_000_000))`).
- **Thiết lập Sequence dọc 9:16 chuẩn Talking Head:**
  - `settings.width`: `1080`, `settings.height`: `1920`
  - Phân tầng Track hình (`video_tracks`):
    - `V1`: Video người nói chính (A-roll) kèm hiệu ứng `motion` (keyframes `scale` / `position` / `anchor` để punch-in/out 105–115%), `lumetri`.
    - `V2`: B-roll / footage minh họa từ `/home/vmiz/Thanh/Media/TNEDIT/06_B-Roll/Stock_Theo_Chu_De_PR`.
    - `V3`: Overlay ánh sáng / glitch (`FTG_Overlay_LightLeaks`, `FTG_Overlay_Glitch`) với `opacity` blend mode `Screen` / `Add`.
    - `V4`: Icon ngữ nghĩa (Unicons PNG/SVG) và thẻ UI/chart kèm hiệu ứng `grow`, `shrink`, `move`, `drop_shadow`.
    - `V5` (hoặc `caption_tracks`): Phụ đề động (`graphic_text` hoặc template `.fcgt`: `[SubMachine] Hormozi Dynamic Pop Caption`, `[Captioneer] Viral Reels Pill Subtitle`).
  - Phân tầng Track tiếng (`audio_tracks`):
    - `A1`: Voice chính (gắn `essential`: `{"kind": "Dialogue", "preset": "[CrumplePop] Studio Podcast Voice"}`).
    - `A2`, `A3`: Các clip SFX đặt so le để **giữ nguyên 100% đuôi âm (`duration` = độ dài gốc của biến thể)**, chỉnh `gain_db` hoặc effect `volume` riêng cho từng clip.
    - `A4`: Nhạc nền BGM từ `/home/vmiz/Thanh/Media/TNEDIT/08_Nhac_Nen/BGM_Thu_Vien_PR` (gắn `essential`: `{"kind": "Music", "preset": "[AutoDuck] Smart BGM Ducking Under Voice"}` hoặc hạ `volume` xuống `-22` đến `-26 dB`).

### 2. Nhập qua FCP7 XML (`<xmeml>`) hoặc FCPXML (`<fcpxml>`)
- FilmCraft hỗ trợ import và export trực tiếp cả FCP7 XML (`<xmeml version="4">` / `"5"`) lẫn Final Cut Pro `<fcpxml>`.
- Lưu ý: FCP7 XML làm tròn vị trí clip theo frame và không truyền `channel_volume` hay `non-uniform scale`; do đó nếu cần độ chính xác dưới frame cho SFX và đầy đủ hiệu ứng native (`grow`, `shrink`, `graphic_text`, `essential`), ưu tiên ghi trực tiếp vào `.fcproj`.

### 3. Mở Project và Điều khiển qua Control Server
- Mở trực tiếp project trên giao diện FilmCraft:
  ```bash
  /home/vmiz/.local/bin/filmcraft --no-recover /duong/dan/project.fcproj &
  ```
- Hoặc khởi chạy kèm JSON-lines Control Server trên `localhost`:
  ```bash
  FILMCRAFT_CONTROL_TOKEN=$(openssl rand -hex 32) /home/vmiz/.local/bin/filmcraft --control <port> /duong/dan/project.fcproj
  ```

---

## Nhập và lưu Premiere (Khi làm việc trên máy dùng Premiere Pro)

Ưu tiên tool Premiere đã kết nối. Kiểm tra project trước mutation, lưu phiên bản rõ ràng và xác nhận. Khi cần UI, dùng computer-use theo skill tương ứng.

FCP XML có thể nhập timeline nhưng không bảo đảm đã tạo project. Phải import rồi kiểm tra sequence thật. `save_project_as` không biến template trống thành project hoàn chỉnh.

Các vấn đề đã gặp trên Premiere:

- `import_media` nhận XML với đường dẫn dạng `E:/...` đã hoạt động.
- Một số lệnh export XML tạo đường dẫn sai và modal treo. Không export chỉ để dò format nếu không cần; đọc trạng thái UI trước khi tiếp tục, không chồng timeout.
- MCP Bridge có thể disconnected khi Premiere nạp panel. Đợi app sẵn sàng, kiểm tra panel/kết nối, chỉ retry sau khi có thay đổi trạng thái. Không reset preferences hoặc sửa plugin ngoài phạm vi.
- Stereo XML có thể hiện thành cặp L/R trên track riêng. Kiểm tra routing/output, gain, duration và playback. Hai clip không tự động có nghĩa bị lặp âm nếu là hai kênh. Ưu tiên import audio native nếu mapping không rõ. Waveform/clip counts không chứng minh âm đúng.
- XML theo frame làm tròn thời điểm âm; nếu cần chính xác dưới frame, dùng audio timing native/sample ticks. Đối chiếu sequence với MP4 tham chiếu.

## Bằng chứng hoàn tất

Project (`.fcproj` hoặc `.prproj`) đúng đường dẫn, sequence đúng tên, track/clip counts khớp manifest, media online (`missingMedia: 0`), save thành công, và **giữ nguyên project cùng timeline làm việc để người dùng kiểm tra cuối cùng (tuyệt đối không tự xuất file video MP4 trừ khi người dùng yêu cầu rõ)**. Có thể kiểm tra nhanh bằng cách xuất vài frame tĩnh (`file.exportFrame`) ở điểm khó, nghe nếu có khả năng. Nếu chỉ kiểm tra số liệu thì ghi đúng giới hạn đó.

<!-- ===== /file: talking-head-premiere/references/premiere-and-audio.md ===== -->

<!-- ===== file: talking-head-premiere/references/style-reference.md ===== -->

# Style edit tham chiếu — Talking head
Ngày phân tích: 20/10/2026. Nguồn: 10 MP4 tại E:\talking head.

## Phạm vi kiểm tra
Đã kiểm tra metadata và 20 khung hình trải đều trên mỗi video; bổ sung 20 khung hình cách nhau 0,25 giây ở 5 giây đầu của mẫu 04, 06, 10. Đây là phân tích hình ảnh theo mẫu thời gian, chưa phải xem/nghe liên tục toàn bộ video. Chưa xác nhận nhạc, SFX, độ khớp lời nói hoặc easing chính xác. Các thông số dựng gợi ý dưới đây là điểm khởi đầu áp dụng, không phải thông số gốc đo được.

## DNA chung
- Video dọc 9:16; nhân vật là điểm neo, xen minh họa trực tiếp cho điều đang giải thích.
- Thay đổi giữa trung cảnh, cận hơn, overlay và cảnh minh họa toàn màn hình. Mục đích là làm rõ ý và tạo nhịp thị giác.
- Caption theo cụm ngắn; có phân cấp từ khóa với phần phụ. Không phải mọi mẫu đều dùng chữ in hoa.
- Số liệu, UI, màn hình điện thoại, biểu đồ và thẻ so sánh đóng vai trò bằng chứng.
- Nền tối tách khuôn mặt và chữ; nền trắng tạo khoảng nghỉ cho phần giải thích.
- Vật thể có lớp trước/sau, bóng đổ, bo góc, đôi khi nghiêng phối cảnh. Một số mẫu dùng vùng tối chuyển sắc phía dưới để chữ dễ đọc.

## Ba nhánh style
### A. Creator / marketing: nền tối, chữ mạnh, UI nổi
Mẫu 03 và 05–09. Đặc trưng: chữ trắng đậm, từ khóa đỏ/xanh/vàng hoặc màu Instagram; thẻ số lượt xem, màn hình điện thoại, biểu đồ, notification. Bố cục đổi theo hướng tay chỉ hoặc vật thể được nhắc đến.
- 06: 0–1,75s giữ hook STOP USING HOOKS và đồ thị đỏ; khoảng 2–2,25s chuyển vào điện thoại cầm tay; khoảng 3,5s và 4,75s có trạng thái nhòe dọc khi đổi nội dung trong điện thoại. Khoảng 15–30s dùng hai thẻ video và làm nổi từ khóa để so sánh.
- 05: 0–8s so sánh hai video kèm số lượt xem; khoảng 22–35s chuyển sang sơ đồ automation trên nền sáng; khoảng 39–47s trở lại UI tối và người nói.
- 07: đoạn đầu dùng chia màn hình người nói và tư liệu; khoảng 12–22s màn hình điện thoại; khoảng 24–39s UI/analytics toàn màn hình; cuối quay về người nói.
- 08: hook màu Instagram, đoạn thao tác UI tối với điểm sáng chỉ chạm; khoảng 21–27s điện thoại trên nền trắng kèm vòng thống kê; cuối dùng hai thẻ so sánh.
- 09: nửa trên UI, nửa dưới talking head ở phần hướng dẫn đầu; sau đó chuyển sang video/UI toàn màn hình và biểu đồ, link được highlight.

### B. Editorial sạch: nền trắng, thẻ hình và chữ có phân cấp
Mẫu 04 và 10.
- 04: chữ trắng đậm trộn chữ phụ nhỏ và chữ nghiêng trang trí, nhấn đỏ. 0–4,25s chữ được bổ sung theo cụm; khoảng 4,5s đổi sang nền trắng. Khoảng 5s có số 10K đỏ dạng khối; khoảng 12–16s nền sáng, nhãn đỏ và icon; khoảng 26s typography riêng toàn màn hình. Tên file nói real estate nhưng hình ảnh mẫu thực tế là người nói về scripting/content.
- 10: talking head tông trầm, caption trắng nhỏ ở ngực; tiêu đề lớn phía sau đầu tạo cảm giác chiều sâu. Khoảng 2,5–4s thẻ hình xếp lớp trên nền trắng đổi nội dung; khoảng 4,25s thành thẻ prompt. Khoảng 28–33s UI phía trên và người nói trong khung bo góc phía dưới. Hợp nội dung hướng dẫn công cụ, thiết kế và AI.

### C. Storytelling kinh doanh: tư liệu, quote và nhấn xanh
Mẫu 02, dài 115,3s, nguồn chỉ 234×416 nên không dùng để kết luận độ nét/font chính xác. Nhân vật ngồi ghế nền xanh tối, xen tư liệu McDonald's, chữ xanh phát sáng, đoạn đơn sắc, quote và hiệu ứng glitch. Nhịp kể dài hơn nhánh A. Khoảng 23s có tư liệu lịch sử; 29s quote đơn sắc; 46s ảnh minh họa thương hiệu; 58s cụm chữ nhấn xanh; cuối có outro thương hiệu.

### Mẫu 01: nhịp typography và demo sản phẩm
Xen podcast/talking head, giao diện phần mềm và nền xanh dương/trắng với từng từ lớn. Khoảng 19–26s demo trước/sau, màn hình điện thoại và B-roll. Có thể tham khảo nhịp thay đổi bố cục, nhưng phần demo là nội dung quảng bá công cụ, không nên sao chép nguyên giao diện vào nội dung khác.

## Quy tắc áp dụng lại
1. Chọn một nhánh chính cho mỗi video; xác định màu nhấn và kiểu chữ trước khi dựng.
2. Dựng nội dung lời nói thành ý rõ ràng; đặt minh họa tại câu cần chứng minh hoặc giải thích.
3. Mở bằng người nói và thông điệp cụ thể; nếu có số liệu/so sánh, đưa bằng chứng lên sớm.
4. Mỗi cụm caption chỉ nên có một trọng tâm. Khi dùng tiếng Việt, giữ dấu, ngắt theo nghĩa, kiểm tra font hỗ trợ tiếng Việt.
5. Thay đổi cỡ cảnh ở chỗ chuyển ý hoặc nhấn mạnh; đưa UI lên toàn màn hình khi người xem cần đọc/thấy thao tác.
6. Dùng chuyển động có hướng: thẻ vào vị trí cần nhìn, zoom vào chi tiết, làm tối phần phụ để giữ điểm tập trung.
7. Tránh đặt caption lên mặt; kiểm tra vùng bị giao diện Reels/TikTok che ở cạnh phải và đáy.
8. Kết lại bằng kết quả hoặc hành động phù hợp nội dung; không tự thêm CTA thiếu liên quan.

## Thông số khởi đầu gợi ý — không phải đo từ bản gốc
- Canvas 1080×1920; fps theo footage và yêu cầu xuất.
- Caption khoảng 3–7 từ/cụm, tối đa 2 dòng khi phù hợp; điều chỉnh theo tiếng Việt và tốc độ nói.
- Punch-in thử 105–115%, dùng tại từ/câu nhấn, giữ chất lượng nguồn.
- Animation chữ/thẻ thử 0,15–0,35s, có giảm tốc cuối và motion blur vừa phải.
- Thử đổi thông tin thị giác sau 1,5–3s khi nội dung cần; cho UI/phần giải thích thời gian đọc dài hơn. Không coi đây là chu kỳ cắt bắt buộc.
- Bảng màu A: trắng + đỏ hoặc xanh, nền than. B: trắng ngà + đỏ trầm, chữ đen/trắng. C: xanh lá + trắng, nền xanh tối.
- Chưa xác định font gốc. Chọn sans đậm/condensed hỗ trợ tiếng Việt; chỉ dùng serif italic làm điểm nhấn ở nhánh B.

## Âm thanh — cần kiểm tra bổ sung
Chưa nghe được nguồn trong lượt phân tích này nên không kết luận nhạc, BPM, SFX hay mức âm lượng của mẫu. Khi dựng có thể thử click cho thao tác UI, whoosh ngắn cho chuyển thẻ, impact nhẹ cho số liệu; đây là đề xuất, chưa phải đặc điểm âm thanh đã xác nhận.

## Cách gọi lại style
Có thể yêu cầu: “Dựng theo style talking head trong E:\talking head\style-analysis\STYLE-GUIDE.md, nhánh A/B/C”. Tài liệu này là bộ nhớ tham chiếu trên máy; không ngụ ý mô hình được huấn luyện lại hay sẽ tự nhớ ở mọi chat.

## Danh mục đối chiếu
01 — Ghim trên Proução 360 - Roteiro - Direção - Edição_2.mp4 — 37,64s
02 — Ghim trên Proução 360 - Roteiro - Direção - Edição.mp4 — 115,30s
03 — Here are the Prompts I use as an Editor to create Stunning Visuals Comment 'Guide' to get them..mp4 — 91,84s
04 — Real estate video editing inspiration..mp4 — 34,87s
05 — snapgram.io_91q5fvxo93fs.mp4 — 49,92s
06 — snapgram.io_jjlqhu0ma4a2.mp4 — 50,96s
07 — snapgram.io_qs74bpimiwbs.mp4 — 49,06s
08 — snapgram.io_s54fk5luoaah.mp4 — 36,01s
09 — snapgram.io_uiomwzd105q9.mp4 — 31,72s
10 — Talking head edit.mp4 — 56,29s

sheet-01.jpg đến sheet-10.jpg: khung hình tổng quan theo thời gian.
motion-04.jpg, motion-06.jpg, motion-10.jpg: chuỗi hình mở đầu cách nhau 0,25s.

## Ưu tiên SFX do người dùng xác định — 20/10/2026
Nguồn ưu tiên: E:\TaiNguyen\SFX Meme\Boom_Library_Casual_UI_Construction_Kit_WAV
Chất âm mong muốn: sang, tinh tế, phù hợp chuyển động UI và talking head. Đã xác nhận thư mục có các nhóm click, whoosh, shimmer, impact, card và effect; chưa nghe thử để chốt từng file.

Quy tắc dựng bắt buộc theo yêu cầu người dùng:
- Ưu tiên chọn SFX từ bộ này, nghe và chọn âm phù hợp từng hành động khi dựng.
- Mặc định để SFX chạy đủ âm và đuôi ngân tự nhiên. Không tự cắt ngắn để ép vừa thời lượng animation hoặc cảnh.
- Cảnh hình đã chuyển vẫn cho đuôi SFX tiếp tục trên track âm thanh; bố trí track riêng hoặc chồng đuôi khi cần.
- Nếu âm quá dài hoặc quá dày, ưu tiên chọn âm khác phù hợp hơn, giảm gain hoặc giảm số lần dùng trước khi nghĩ đến việc cắt.
- Tránh fade-out sớm làm mất đuôi. Chỉ cắt khi thực sự cần thiết, hạn chế tối đa; không coi việc cắt theo ranh giới cảnh là mặc định.
- Cân mức âm để lời nói rõ, dùng có chọn lọc nhằm giữ cảm giác sang và gọn.
- Nếu một WAV chứa nhiều biến thể liên tiếp, kiểm tra trước khi dùng: giữ đầy đủ một âm/biến thể được chọn và đuôi của nó; không mặc định phát cả chuỗi biến thể như một SFX.

## Nguồn tài nguyên bổ sung được người dùng cho phép — 20/10/2026
Được sử dụng toàn bộ tài nguyên trong E:\TaiNguyen\POWER PODCAST BUNDLE cho các bản dựng của người dùng; không cần hỏi lại quyền chọn asset trong thư mục này.
Đã kiểm tra các nhóm cấp đầu: 3D ELEMENTS, BACKGROUNDS, CARTOON ELEMENTS, EFFECTS, FRAMES, SFX, SOCIAL MEDIA ELEMENTS, TRANSITION và _Mister Horse Previews.
Chọn asset theo nội dung và nhánh style đang dựng; ưu tiên bản media gốc phù hợp thay vì preview khi có cả hai. Chưa xem/nghe từng asset nên cần kiểm tra asset cụ thể lúc sử dụng.
Nguồn này bổ sung cho bộ BOOM Casual UI; ưu tiên SFX sang, tinh tế từ BOOM theo yêu cầu trước đó. Với mọi SFX, mặc định giữ đủ âm và đuôi tự nhiên, hạn chế tự cắt ngắn.

### Làm rõ lựa chọn SFX — 20/10/2026
Người dùng xác nhận có thể chọn SFX trong POWER PODCAST BUNDLE bất cứ khi nào phù hợp. BOOM Casual UI là nguồn tham chiếu chất âm, không phải nguồn độc quyền; không bỏ qua SFX phù hợp của bundle chỉ vì đã có BOOM. Chọn theo độ phù hợp với cảnh, chất âm sang/tinh tế và khả năng hòa cùng giọng nói. Quy tắc giữ đủ âm và đuôi tự nhiên áp dụng cho cả hai nguồn.

## Tạo asset bổ sung và chọn font — 20/10/2026
- Người dùng cho phép chủ động tạo thêm asset để đưa vào video khi các thư viện hiện có không có asset phù hợp. Asset mới phải bám ý đang nói, nhánh style đã chọn và thống nhất với các asset khác; không thêm chỉ để trang trí.
- Tùy nhu cầu có thể tạo hình minh họa, icon, thẻ UI, biểu đồ, background hoặc motion graphic. Nội dung số liệu/chứng cứ phải lấy từ nguồn thực, không tạo hình giả làm bằng chứng.
- Font cần phù hợp talking head: dễ đọc nhanh trên điện thoại, rõ ở cỡ nhỏ, có phân cấp caption/từ khóa/tiêu đề. Với tiếng Việt phải hỗ trợ đầy đủ dấu và kiểm tra dấu không bị cắt.
- Ưu tiên sans-serif medium/bold cho caption, bold/condensed cho hook và từ khóa khi phù hợp; serif italic chỉ làm điểm nhấn ở nhánh editorial. Chọn font cụ thể theo footage và style, không bắt buộc một font cho mọi video.
- Giữ bộ font gọn, thường 1–2 family mỗi video; dùng màu, weight và kích thước để phân cấp. Tránh chữ quá mảnh, quá hẹp hoặc trang trí nhiều làm khó đọc.

## Điều chỉnh style sau bản thử 27 — 20/10/2026
Người dùng thấy bản 27 quá tĩnh và đơn điệu so với reference. Với bản 1p và các bản dựng tiếp theo, ưu tiên talking head có nhịp mạnh: hiệu ứng liên tục nhưng theo nội dung; nhiều SFX hơn để nhấn chuyển động; zoom in/zoom out theo điểm nhấn lời nói; kinetic typography, thay bố cục, card minh họa, chuyển cảnh và nhấn màu. Không mặc định dựng tối giản/editorial chậm chỉ vì chủ đề cảm xúc. Duy trì các khoảng nhấn có chủ đích nhưng tránh nhiều giây chỉ giữ nguyên khung và đổi caption. SFX vẫn giữ trọn âm/đuôi của biến thể chọn.

## Phản hồi V02
Talking head cần dùng nhiều icon theo nội dung. Có thể tìm icon trên IconScout. SFX V01 quá nhỏ và cảm giác lặp: cân từng âm theo voice, đa dạng nguồn/take; không chỉ thêm số lượng hit. Giữ nguyên đuôi âm.

<!-- ===== /file: talking-head-premiere/references/style-reference.md ===== -->
