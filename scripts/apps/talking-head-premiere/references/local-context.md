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
