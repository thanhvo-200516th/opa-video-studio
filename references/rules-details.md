# Chi tiết kỹ thuật nguyên văn theo luật

Các dòng dưới đây chép NGUYÊN VĂN từ nguồn gốc (`kb-master-video-edit.md`), là thông số / lưu ý / ngoại lệ mà bộ luật rút gọn chưa nêu đủ (kiểm định ngữ nghĩa v2.3, mức nhẹ). Đọc kèm luật cùng mã trong `rules-full.md`. Khi một dòng ở đây mâu thuẫn với luật hiện hành (vd tốc độ 1.25x, dải tối sau phụ đề, xuất MP4 trước duyệt), luật trong `rules-full.md` thắng.

## A2

- `references/rules.md:9` — - **Nhiều video trong một yêu cầu: mỗi video một cửa sổ FilmCraft riêng, dựng song song** (chốt 2026-10-31). Mỗi video giao một agent chạy nền; dựng xong mở tất cả cùng lúc trên màn hình người dùng: `python3 scripts/open_in_app.py a.fcproj b.fcproj c.fcproj`.
- `references/cindy-memories/project_filmcraft-ram-limit.md:14` — - Chạy tối đa 3 cửa sổ duyệt cùng lúc, cộng thêm 1 instance headless. Các lệnh dựng/kiểm chạy lần lượt từng cái.

## A3

- `SKILL.md:246` — - Đường dẫn project (và MP4 nếu đã xuất); bản trước giữ nguyên. **[có nội dung đã thay — theo A1 hiện hành]**

## A7

- `references/rules.md:77` — | Kho tài nguyên dựng | `/home/vmiz/Thanh/Media/TNEDIT/` — xếp theo loại: `01_Font`, `02_SFX`, `03_VFX`, `04_Footage`, `05_Hieu_Ung_Chuyen_Canh`, `06_B-Roll`, `07_Assets`, `08_Nhac_Nen`; danh mục ở `README_DANH_MUC_TAI_NGUYEN.md` |

## B3

- `references/rules.md:35` — - **Chữ key / chữ chính** (từ khoá to, chữ viết tay to của câu chốt) **luôn phát sáng cùng màu**; chữ key **vàng hoặc trắng chỉ phát sáng siêu nhẹ** (`GLOW["soft"]`), màu khác phát sáng rõ (`GLOW["normal"]`) — chốt 2026-11-04 lần 9. **Chữ phụ** (phụ đề, từ dẫn, nhãn, chữ viết tay nhỏ) chỉ đổ bóng **nhẹ**.
- `references/motion-fx.md:113` — - **Vàng, trắng làm chữ key: phát sáng siêu nhẹ** (`GLOW["soft"]`: bán kính 12, cường độ 55 → 20). Màu khác:
- `references/motion-fx.md:114` — `GLOW["normal"]` (bán kính 20, 170 → 70). Bảng thuộc `SOFT_GLOW` thì tự dùng mức nhẹ.
- `references/motion-fx.md:117` — - Xanh ngọc (`mint`) vẫn dùng (người dùng giữ lại) — luôn phát sáng như mọi chữ key. Xanh lam / xanh dương dùng hạn chế.

## B4

- `references/rules.md:35` — - **Chữ key / chữ chính** (từ khoá to, chữ viết tay to của câu chốt) **luôn phát sáng cùng màu**; chữ key **vàng hoặc trắng chỉ phát sáng siêu nhẹ** (`GLOW["soft"]`), màu khác phát sáng rõ (`GLOW["normal"]`) — chốt 2026-11-04 lần 9. **Chữ phụ** (phụ đề, từ dẫn, nhãn, chữ viết tay nhỏ) chỉ đổ bóng **nhẹ**.

## B5

- `references/motion-fx.md:119` — - **Phụ đề: dòng 1 trắng + dòng 2 màu đổi MỖI CỤM** (lần 17) xanh ngọc · vàng · xanh lam · xanh ngọc · xanh da trời #9FD4FF · vàng · xanh lam (2026-11-06: bỏ tím #D6CCFF)
- `references/motion-fx.md:158` — Đo THCN 07: file giọng đã cân khớp gốc (≤ 0,025 s) — lệch nằm ở (1) Whisper turbo đặt từ đầu sau khoảng lặng **sớm
- `references/motion-fx.md:159` — 0,18–0,29 s** so với tiếng thật (giữa câu chỉ ±0,05 s) và (2) phụ đề gõ theo tốc độ cố định 7 ký tự/s, dòng 2 hiện ngay sau dòng 1
- `references/motion-fx.md:160` — dù chưa được nói. Sửa:
- `references/motion-fx.md:161` — - `build_kit.refine_words(words, audio)` ngay sau bóc lời: từ sau lặng ≥ 0,25 s → chỗ năng lượng vượt nền + 18 dB; từ giữa câu →
- `references/motion-fx.md:162` — điểm bật âm tiết (spectral flux) gần nhất ±0,2 s. Đầu mỗi đoạn cắt gọn hơn (THCN 07: 46,5 → 44,7 s).
- `references/motion-fx.md:163` — - `captions2` truyền mốc từng từ (giây tính từ đầu cụm) cho cả 2 dòng; dòng 2 bắt đầu ở mốc từ đầu của nó − 0,05 s.
- `references/motion-fx.md:164` — `type_sync` (gõ / khung chọn: mỗi từ gõ trong lúc được nói, ≥ 12 ký tự/s), `wipe_sync` (mép quét chạy theo mốc từ),
- `references/motion-fx.md:165` — `word_in` (chưa nói thì chưa hiện), viết tay lộ mượt theo lời; blur hiện cả dòng đúng lúc dòng bắt đầu được nói.
- `references/motion-fx.md:166` — `_mono` giữ keyframe tăng dần (dòng ngắn, từ dồn → gộp vào cùng khung).
- `references/motion-fx.md:167` — - Kiểm: tính mốc nói trên timeline rồi chụp khung +0,06 s sau mỗi mốc — chữ hiện tới đúng từ vừa nói.
- `references/motion-fx.md:168` — - Cụm phụ đề kết thúc đúng lúc cụm sau vào (mốc từ đầu − 0,05 s) — trước lần 17 hai cụm chồng nhau 0,05 s, thấy rõ khi cụm sau
- `references/motion-fx.md:169` — nhấp nháy / blur.
- `references/motion-fx.md:256` — | `caption2(top, bottom, style=, bottom_role=)` / `captions2(words, end, skip=, style=)` | Newbie + lần 10–11 | Dòng 1 trắng 86 px, dòng 2 vàng vào sau 0,15 s; font theo kiểu của đoạn (`CAPTION_STYLES`, mục "Phụ đề 2 dòng"); `captions2` tự xoay kiểu mỗi 3–5 cụm. Kiểu không viết tay: giãn ≥ 1,28× khi dòng 2 có dấu chồng | **[có nội dung đã thay — theo B5 hiện hành]**
- `references/motion-fx.md:152` — - **Mọi dòng vàng** dùng `CAP_SCRIPT_SHADOW` (đậm 100, nhoè 12, lệch 3, lan 7) + dải tối `caption_band` phủ tới **[có nội dung đã thay — theo B15 hiện hành]**

## B6

- `references/motion-fx.md:205` — | Chữ phụ (`CAP_ENTRANCES`, phụ đề mỗi cụm) | **lần 17, người dùng giữ ở lần 18**: type (gõ theo lời) · glow_rise (phát sáng dâng lên: hiện 0,12 s, quầng cùng màu 0 → 120 trong 0,35 s rồi lắng 40) · blur · flicker (lần 18: dịu — hiện, chùng 60 % một khung rồi đứng; chỉ 1 lần / 11 cụm qua vòng 11 vị trí) · font_flip (dòng 1 chớp qua Anton → viết tay → SF mảnh → Be Vietnam, mỗi font 2 khung, rồi về font chính; dòng 2 blur-in khi được nói) · word (từng chữ khớp lời). Lần 15 (vẫn gọi được qua `entrance=`): word_pop · box · wipe · script_swap. Nhãn / từ dẫn: `LABEL_ENTRANCES` gõ · phát sáng dâng lên · blur. Lần 14 (đập vào, loé sáng… cho chữ phụ) bị chê | đã kiểm khung thật THCN 07 |

## B7

- `references/motion-fx.md:134` — - **Nhịp nói = một cụm phụ đề** (một hơi nói, ≤ 5 từ). **Đoạn = 3–5 nhịp**: đổi đoạn ở cuối câu khi đã ≥ 3 cụm, bắt buộc đổi
- `references/motion-fx.md:135` — ở cụm thứ 5 (`SEGMENT_MIN`, `SEGMENT_MAX`). Mỗi đoạn một kiểu, xoay `CAPTION_STYLE_ROTATION` = script · mont · bevn ·
- `references/motion-fx.md:136` — script · sf · mont (`fx.next_cap_style()`, tự chạy trong `captions2`; ép một kiểu: `captions2(..., style="sf")`).
- `references/motion-fx.md:137` — - Đoạn `script` chỉ ≤ 3 cụm (`SCRIPT_PER_SEGMENT`) có dòng viết tay mảnh, cụm còn lại về `mont` → cộng chữ viết tay của từ
- `references/motion-fx.md:138` — khoá (`keyword_tpl` / `collage`) vẫn ≤ 4 chữ viết tay trong 3–5 nhịp. `fx.cap_style_log` ghi (giây, kiểu) từng cụm để kiểm.

## B8

- `references/rules.md:44` — - Khung trên, x 140–940, y 240–680: từ khoá, tiêu đề nổi (key). Baseline dòng đầu mặc định y ≈ 500 (`FX(key_y=500)`; khối chồng 3 tầng cao nhất vẫn nằm trọn trong khung).

## B9

- `references/cindy-memories/feedback_key-text-behind-face.md:13` — **How to apply:** master-video-edit: dò mặt Haar (venv clearvoice, OpenCV 4) + master_pipeline.py matte; từ khoá chạm vùng đầu và không nằm trên B-roll → keyword_tpl(size≈218, y = max(đỉnh đầu thật từ alpha + 0,18×cỡ, 235 + 0,75×cỡ)) rồi fx.behind_person (track_matte đảo, lớp người là track V2 ngay trên V1, dưới dải tối); đoạn đó không punch; bỏ dòng viết tay rơi vào mặt. Kiểm bằng ảnh khung. **[có nội dung đã thay — theo G5 hiện hành]**

## B10

- `references/motion-fx.md:256` — | `caption2(top, bottom, style=, bottom_role=)` / `captions2(words, end, skip=, style=)` | Newbie + lần 10–11 | Dòng 1 trắng 86 px, dòng 2 vàng vào sau 0,15 s; font theo kiểu của đoạn (`CAPTION_STYLES`, mục "Phụ đề 2 dòng"); `captions2` tự xoay kiểu mỗi 3–5 cụm. Kiểu không viết tay: giãn ≥ 1,28× khi dòng 2 có dấu chồng | **[có nội dung đã thay — theo B5 hiện hành]**

## B11

- `references/rules.md:37` — - **Không dùng kiểu chữ "chạy ra rồi thu vào"** (gõ vào rồi xoá ngược hết): chữ gõ vào xong thì ra bằng mờ dần ngắn. Nhịp chữ chậm: phụ đề gõ ~7 ký tự/s, từ khoá ~6 ký tự/s, mờ dần 8 khung. **[có nội dung đã thay — theo B14 hiện hành]**
- `references/motion-fx.md:158` — Đo THCN 07: file giọng đã cân khớp gốc (≤ 0,025 s) — lệch nằm ở (1) Whisper turbo đặt từ đầu sau khoảng lặng **sớm
- `references/motion-fx.md:159` — 0,18–0,29 s** so với tiếng thật (giữa câu chỉ ±0,05 s) và (2) phụ đề gõ theo tốc độ cố định 7 ký tự/s, dòng 2 hiện ngay sau dòng 1
- `references/motion-fx.md:160` — dù chưa được nói. Sửa:
- `references/motion-fx.md:161` — - `build_kit.refine_words(words, audio)` ngay sau bóc lời: từ sau lặng ≥ 0,25 s → chỗ năng lượng vượt nền + 18 dB; từ giữa câu →
- `references/motion-fx.md:162` — điểm bật âm tiết (spectral flux) gần nhất ±0,2 s. Đầu mỗi đoạn cắt gọn hơn (THCN 07: 46,5 → 44,7 s).
- `references/motion-fx.md:163` — - `captions2` truyền mốc từng từ (giây tính từ đầu cụm) cho cả 2 dòng; dòng 2 bắt đầu ở mốc từ đầu của nó − 0,05 s.
- `references/motion-fx.md:164` — `type_sync` (gõ / khung chọn: mỗi từ gõ trong lúc được nói, ≥ 12 ký tự/s), `wipe_sync` (mép quét chạy theo mốc từ),
- `references/motion-fx.md:165` — `word_in` (chưa nói thì chưa hiện), viết tay lộ mượt theo lời; blur hiện cả dòng đúng lúc dòng bắt đầu được nói.
- `references/motion-fx.md:166` — `_mono` giữ keyframe tăng dần (dòng ngắn, từ dồn → gộp vào cùng khung).
- `references/motion-fx.md:167` — - Kiểm: tính mốc nói trên timeline rồi chụp khung +0,06 s sau mỗi mốc — chữ hiện tới đúng từ vừa nói.
- `references/motion-fx.md:168` — - Cụm phụ đề kết thúc đúng lúc cụm sau vào (mốc từ đầu − 0,05 s) — trước lần 17 hai cụm chồng nhau 0,05 s, thấy rõ khi cụm sau
- `references/motion-fx.md:169` — nhấp nháy / blur.
- `references/motion-fx.md:230` — - Phụ đề gõ ~7 ký tự/s (`CAP_CPS`; 22 → 16 → 12 → 9 đều bị chê nhanh), gõ xong trước 80% thời gian hiện; cụm ≤ 5 từ, cụm
- `references/motion-fx.md:231` — hiện < 1,8 s gộp với cụm sau (≤ 8 từ); cụm sau thay thẳng, chỉ mờ dần ở cuối câu / trước khoảng lặng.
- `references/motion-fx.md:232` — - Từ khoá gõ ~6 ký tự/s, từ dẫn ~7, chữ viết tay lộ 30 khung; từ khoá hook giữ ≥ 2,2 s (1,6 s bị chê nhanh).

## B12

- `references/cindy-memories/feedback_top-band-color-matte-mask.md:13` — **How to apply:** sau fc_build chạy master-video-edit/scripts/fc_matte_band.py PROJECT.fcproj (mặc định đúng các thông số trên); mở cho người dùng bằng open_in_app.py --select "Dải tối trên · Color Matte". Khi người dùng gửi ảnh Effect Controls làm mẫu, lấy đúng số trong ảnh.
- `references/motion-fx.md:217` — Chạy sau `fc_build`: `python3 scripts/fc_matte_band.py PROJECT.fcproj` (xoá clip «Dải tối trên», đặt Color Matte cùng chỗ,
- `references/motion-fx.md:218` — lưu); mở cho người dùng xem: `open_in_app.py PROJECT.fcproj --select "Dải tối trên · Color Matte"` (chọn sẵn clip; điều khiển
- `references/motion-fx.md:219` — FilmCraft không có lệnh chuyển tab — người dùng bấm tab Effect Controls). Ảnh kiểm THCN 07: tối mềm như PNG cũ.
- `references/motion-fx.md:215` — Controls. Thông số người dùng chốt: Mask Feather **868,8** · Mask Opacity **59,2 %** · Mask Expansion **213,1** · khung mask
- `references/motion-fx.md:216` — phủ mép trên (y −50 → 115, tràn hai bên), Opacity clip 100 %, Normal. Màu đen (hoặc màu khác qua `--color`).

## C2

- `references/rules.md:91` — - **Đa dạng chuyển cảnh (Rule 2, chốt 2026-11-11 — thay "họ ưu tiên ≥ 40 %" ngày 2026-11-06):** 10 video KB06–15 chỉ dùng 6/26 kiểu, flash / shutter / flicker chiếm 57,6 % điểm cắt. Từ nay `cut_plan` chọn theo ngữ cảnh (câu mới · đổi phần · đổi cảnh · đổi góc gần · ra B-roll), lấy kiểu ít dùng nhất, không lặp trong 4 điểm cắt; họ nháy sáng (`flash_burst`, `flash_shake`, `shutter`, `flicker`) ≤ 20 % và cách nhau ≥ 3 điểm cắt; file mẫu dựng KHÔNG còn ghi đè bằng vòng cố định. Bộ kiểm: nháy sáng ≤ 25 %, ≥ 6 kiểu, không lặp liền. **[có nội dung đã thay — theo C2 hiện hành]**
- `references/cindy-memories/feedback_analyze-cuts-before-transitions.md:15` — **How to apply:** (1) chạy scripts/cut_plan.py, đưa bảng điểm cắt → loại → chuyển cảnh → SFX → lý do cho người dùng trước khi dựng; jump cut cùng khung không dải/ô. (2) Chuyển cảnh lớn = overlay TNEDIT qua fx.transition (flash_burst, film_burn có tiếng sẵn, light_leak, glitch, film_roll), khung sáng nhất trúng điểm cắt, SFX căn đỉnh vào đó, không lặp kiểu liền nhau. (3) Chữ: bảng màu xoay vòng; caption dòng 2 ExtraBold Italic + viền tối 3 px + bóng đậm; gõ ~16 ký tự/s (từ khoá ~12), cụm ≤ 5 từ thay thẳng, từ khoá giữ ≥ 2 s.
- `references/motion-fx.md:28` — | Loại điểm cắt (đo) | Chuyển cảnh (thứ tự ưu tiên) | Không dùng |
- `references/motion-fx.md:29` — |---|---|---|
- `references/motion-fx.md:30` — | Jump cut cùng khung (cùng file A-roll, sim ≥ 0,3; hoặc sim ≥ 0,8), giữa câu | zoom blur 5 khung + đổi punch 100 ↔ 112% | dải dọc, ô lưới |
- `references/motion-fx.md:31` — | Jump cut cùng khung, sang câu mới | zoom_through → panel_wipe → flash_shake → spin_zoom → light_leak → light_sweep → slice → spring → film_roll → flash_burst | dải dọc, ô lưới, `flash` FilmCraft |
- `references/motion-fx.md:32` — | Jump cut cùng khung, đổi phần lớn | split_slide → rgb_glitch → film_burn → spin → glass → whip → liquid | — |
- `references/motion-fx.md:33` — | Vào B-roll khác cảnh | ô lưới (B-roll lệch sáng ≥ 45, TB ≤ 185) hoặc dải dọc (B-roll sáng / phẳng) + flash_burst ở chỗ nối | — |
- `references/motion-fx.md:34` — | Ra B-roll về người nói | light_leak → zoom (B-roll là lớp phủ: chỉ overlay hoặc `transition_out` của chính nó) | hiệu ứng lớn |
- `references/motion-fx.md:35` — | Đổi cảnh thật (sim < 0,5) | panel_wipe → film_burn → flash_shake → liquid → travel | — |
- `references/motion-fx.md:36` — | Đổi góc gần (sim 0,5–0,8) | slice → zoom_through → flash_burst → travel → slide | — |

## C3

- `references/motion-fx.md:28` — | Loại điểm cắt (đo) | Chuyển cảnh (thứ tự ưu tiên) | Không dùng |
- `references/motion-fx.md:29` — |---|---|---|
- `references/motion-fx.md:30` — | Jump cut cùng khung (cùng file A-roll, sim ≥ 0,3; hoặc sim ≥ 0,8), giữa câu | zoom blur 5 khung + đổi punch 100 ↔ 112% | dải dọc, ô lưới |
- `references/motion-fx.md:31` — | Jump cut cùng khung, sang câu mới | zoom_through → panel_wipe → flash_shake → spin_zoom → light_leak → light_sweep → slice → spring → film_roll → flash_burst | dải dọc, ô lưới, `flash` FilmCraft |
- `references/motion-fx.md:32` — | Jump cut cùng khung, đổi phần lớn | split_slide → rgb_glitch → film_burn → spin → glass → whip → liquid | — |
- `references/motion-fx.md:33` — | Vào B-roll khác cảnh | ô lưới (B-roll lệch sáng ≥ 45, TB ≤ 185) hoặc dải dọc (B-roll sáng / phẳng) + flash_burst ở chỗ nối | — |
- `references/motion-fx.md:34` — | Ra B-roll về người nói | light_leak → zoom (B-roll là lớp phủ: chỉ overlay hoặc `transition_out` của chính nó) | hiệu ứng lớn |
- `references/motion-fx.md:35` — | Đổi cảnh thật (sim < 0,5) | panel_wipe → film_burn → flash_shake → liquid → travel | — |
- `references/motion-fx.md:36` — | Đổi góc gần (sim 0,5–0,8) | slice → zoom_through → flash_burst → travel → slide | — |

## C4

- `references/rules.md:24` — 3. **Mỗi nhịp cắt là một chuyển cảnh** (mở rộng mục 7). Ưu tiên họ **flash · camera shutter (màn trập) · flicker (nháy) · glitch · light leak**, đặc biệt **zoom in / zoom out**: dùng cho cả đoạn nói dài lẫn đoạn có từ khoá nỗi đau. Đoạn nói liền từ 4 s trở lên phải có zoom động (chậm, luân phiên in / out), không để khung đứng yên. **[có nội dung đã thay — theo C2 hiện hành]**
- `references/motion-fx.md:358` — | Zoom đoạn nói dài | `edit_rules.zoom_keys(dur, pains=[giây_từ_đầu_clip…])` → `clip["motion"]["scale"]` | in / out luân phiên 3,2 s, punch 118 % ở nỗi đau; đặt `anchor`/`position` ở tâm mặt |

## C6

- `SKILL.md:239` — 4. Video có chuyển cảnh Motion FX: `scripts/qa_sync.py SPEC.craft.json PROJECT.fcproj OUT_DIR <mốc cắt…>` (đo trên bản xuất — đỉnh tiếng ≤ 0,05 s so với khung mạnh nhất, tiếng không vào trước hình).
- `references/cindy-memories/feedback_analyze-cuts-before-transitions.md:15` — **How to apply:** (1) chạy scripts/cut_plan.py, đưa bảng điểm cắt → loại → chuyển cảnh → SFX → lý do cho người dùng trước khi dựng; jump cut cùng khung không dải/ô. (2) Chuyển cảnh lớn = overlay TNEDIT qua fx.transition (flash_burst, film_burn có tiếng sẵn, light_leak, glitch, film_roll), khung sáng nhất trúng điểm cắt, SFX căn đỉnh vào đó, không lặp kiểu liền nhau. (3) Chữ: bảng màu xoay vòng; caption dòng 2 ExtraBold Italic + viền tối 3 px + bóng đậm; gõ ~16 ký tự/s (từ khoá ~12), cụm ≤ 5 từ thay thẳng, từ khoá giữ ≥ 2 s.
- `references/motion-fx.md:97` — - Tiếng **không bắt đầu trước khi hình đổi**: chuyển cảnh tức thời (flash, cắt) → tiếng tấn công đúng khung đổi, không tiếng
- `references/motion-fx.md:98` — hút trước; overlay dâng dần (leak, burn) → tiếng vào cùng overlay (`max_pre` = độ dâng); chuyển cảnh FilmCraft căn giữa
- `references/motion-fx.md:99` — điểm cắt → tiếng vào từ nửa đầu (`max_pre` = nửa thời lượng + 0,02 s).

## D5

- `references/rules.md:77` — | Kho tài nguyên dựng | `/home/vmiz/Thanh/Media/TNEDIT/` — xếp theo loại: `01_Font`, `02_SFX`, `03_VFX`, `04_Footage`, `05_Hieu_Ung_Chuyen_Canh`, `06_B-Roll`, `07_Assets`, `08_Nhac_Nen`; danh mục ở `README_DANH_MUC_TAI_NGUYEN.md` |
- `references/rules.md:109` — - **Bắt buộc xóa phông xanh khi dùng `soucre thô`**: các video quay phông xanh trong `/home/vmiz/Thanh/Media/A huy/soucre thô` (`C0043..C0071`, `soucre 1..3`, `soucre final`) phải được xoay đúng chiều dọc 9:16, tách sạch 100% phông xanh + mép tường/kẹp phông (`rvm-matte` + `despill=type=green`) và ghép một background mới (phòng studio tối, văn phòng hiện đại, màn hình hệ thống) thay thế phông xanh trước khi chèn vào timeline. Tuyệt đối không để lộ vải phông xanh. **[có nội dung đã thay — theo D11 hiện hành]**

## D11

- `references/rules.md:109` — - **Bắt buộc xóa phông xanh khi dùng `soucre thô`**: các video quay phông xanh trong `/home/vmiz/Thanh/Media/A huy/soucre thô` (`C0043..C0071`, `soucre 1..3`, `soucre final`) phải được xoay đúng chiều dọc 9:16, tách sạch 100% phông xanh + mép tường/kẹp phông (`rvm-matte` + `despill=type=green`) và ghép một background mới (phòng studio tối, văn phòng hiện đại, màn hình hệ thống) thay thế phông xanh trước khi chèn vào timeline. Tuyệt đối không để lộ vải phông xanh. **[có nội dung đã thay — theo D11 hiện hành]**

## E1

- `references/motion-fx.md:358` — | Zoom đoạn nói dài | `edit_rules.zoom_keys(dur, pains=[giây_từ_đầu_clip…])` → `clip["motion"]["scale"]` | in / out luân phiên 3,2 s, punch 118 % ở nỗi đau; đặt `anchor`/`position` ở tâm mặt |
- `references/motion-fx.md:363` — Nhịp dựng nỗi đau (mỗi từ khoá): t−0,12 s bắt đầu punch · t chữ chính vào + glow · t+0,03 đỉnh zoom 118 % · t+0,9 trả về · SFX nhấn đúng khung đỉnh · cảnh chèn minh hoạ ngay sau.

## F1

- `references/cindy-memories/feedback_opening-sfx-every-video.md:9` — Người dùng yêu cầu (2026-10-31): mỗi video phải có SFX mở đầu (ting, switch, bùm, chuyển cảnh…) đánh ngay khung 00:00:00:00 hoặc 00:00:00:01, dài khoảng 0,3 s, để người xem vừa lướt từ video khác sang là nghe ngay. Không dùng cùng một form mở đầu cho nhiều video: mỗi video một bộ SFX và cách chồng lớp riêng, hợp chủ đề.

## F2

- `references/cindy-memories/feedback_text-colors-and-sfx-sync.md:13` — **How to apply:** master-video-edit Motion FX: CAPTION_STYLES + CAPTION_STYLE_ROTATION (script · mont · bevn · script · sf · mont), đoạn 3–5 cụm, SCRIPT_PER_SEGMENT 3, thin_script = TF Whispers (bộ ProdByViet trong TNEDIT/01_Font), máy không có UTM nên dùng Be Vietnam Pro / SF Pro Light; mọi dòng vàng CAP_SCRIPT_SHADOW + dải tối tới cap_y+150, đo tương phản ≥ 4,5:1; kho click ≥ 8 file / nhóm, audit-sfx repeated_takes = 0; chuyển cảnh qua cut_plan + fx.cut_fx(..., clip_before=); đỉnh SFX vào khung hình đổi mạnh nhất; luôn chạy qa_sync trên bản xuất trước khi báo xong. Đã ghi vào references/rules.md và references/motion-fx.md.
- `references/motion-fx.md:284` — - Không lặp file khi còn file khác (dùng lại khi cách ≥ 6 s). **Mỗi click trong một chùm (ô lưới, dải, từng từ, cắt nhanh)
- `references/motion-fx.md:285` — là một file khác** (chốt lần 10 — bỏ ngoại lệ "cả chùm chung một file" theo mẫu 1cho). Kho click: `grid_click` 10,
- `references/motion-fx.md:286` — `bar_click` 8, `word_click` 9 file, không chung file giữa các nhóm; chọn thêm bằng so phổ với bộ click cũ (giữ chất tiếng),
- `references/motion-fx.md:287` — bỏ bản trùng tiếng (khoảng cách phổ < 0,08 — kho TNEDIT có nhiều file cùng tiếng khác tên) và bản méo (đỉnh bị cắt bằng:
- `references/motion-fx.md:288` — `Pop 4`, `Pop 5`). Demo vòng 10: 41 SFX = 41 file, `audit-sfx` `repeated_takes` = 0.

## F3

- `SKILL.md:202` — **Màu chữ** (chốt 2026-11-06): chữ key đa dạng màu (vàng, xanh lam, đỏ, tím, xanh dương, xanh ngọc, trắng — `DEFAULT_ROTATION`), **luôn phát sáng cùng màu** (`fx.key_glow`; vàng / trắng mức siêu nhẹ `GLOW["soft"]`); không hồng, cam, xanh lá — nếu buộc dùng thì phải phát sáng (`GLOW_REQUIRED`). Phụ đề dưới = dòng 1 trắng + dòng 2 xoay vòng đa màu theo cụm (`CAPTION_ROTATION`: vàng · xanh lam · xanh dương · xanh ngọc, không cam / hồng / tím / đỏ; nếu buộc dùng cam/hồng/tím thì phát sáng nhẹ `CAP_GLOW_REQUIRED`), font **đổi theo đoạn 3–5 nhịp** (Montserrat + viết tay mảnh ≤ 3 cụm · toàn Montserrat · Be Vietnam Pro · SF Pro Light — không dùng viết tay quá nhiều), có dải tối `fx.caption_band` sau vùng phụ đề (tương phản ≥ 4,5 : 1). Chữ phụ bóng nhẹ. Không xoá ngược chữ — ra bằng mờ dần; gõ chậm (~7 / ~6 ký tự/s). **Tiếng không vào trước hình** (kiểm bằng `qa_sync.py`). **Chữ không dùng viền** (yếu tố tiên quyết, rules.md mục 2): nổi bằng bóng đen lệch dưới-phải kiểu @magentx.ai (`MX_SHADOW`, `CAP_SHADOW`), màu bão hoà đậm. Tiếng chuyển cảnh 2 lớp (hút vào + hit) ở mức `transition`, nhạc hạ 5 dB quanh điểm cắt (`sfx_auto.duck`), `limit-master --max -2.0`. **[có nội dung đã thay — theo B15 hiện hành]**
- `SKILL.md:240` — 4. Âm thanh: `master_pipeline.py limit-master <project.fcproj>` (hard_limiter −1,5 dB trên master — giọng đã lọc sát −1,5 dBFS nên cộng nhạc + SFX là vượt 0 dBFS); `master_pipeline.py audit-sfx <project.fcproj>` (đủ file, không lặp take, đuôi không vượt video, không vỡ); đo loudness/true peak trên bản trộn: `scripts/qa_audio.py PROJECT.fcproj work/qa/mix.wav` (FilmCraft `export.quick` WAV 48 kHz 24-bit, không phải MP4 giao; in ĐẠT khi −16…−14 LUFS và TP ≤ −1,5). **[có nội dung đã thay — theo G5 hiện hành]**

## F4

- `references/rules.md:77` — | Kho tài nguyên dựng | `/home/vmiz/Thanh/Media/TNEDIT/` — xếp theo loại: `01_Font`, `02_SFX`, `03_VFX`, `04_Footage`, `05_Hieu_Ung_Chuyen_Canh`, `06_B-Roll`, `07_Assets`, `08_Nhac_Nen`; danh mục ở `README_DANH_MUC_TAI_NGUYEN.md` |
- `references/rules.md:79` — | Kho SFX theo reel Hoàng Mạnh Cường (57 file / 8 nhóm) | `/home/vmiz/Thanh/Media/TNEDIT/02_SFX/sfx hmc` — quy luật đặt và giới hạn ở `sfx-hmc.md` |

## G2

- `references/PROMPT_CHUAN_THEO_TANG.md:44` — - 3a. A-Roll HeyGen (dry-run 0 credit trước; chờ tôi gửi key mới render thật) → 3b. B-Roll Muse (`muse_gen.py`) → 3c. Voice B-Roll.

## G5

- `references/PROMPT_CHUAN_THEO_TANG.md:58` — - 6.3. Chạy `scripts/fc_fast_qa.py <project.fcproj> <out_dir> <fps> <mốc_giây...>` (gộp `fc_matte_band` + `limit-master -2.2 dB` + `qa_frames` + `qa_audio` + `audit-sfx` trong 1 phiên duy nhất) + `qa_sync.py`.
- `SKILL.md:202` — **Màu chữ** (chốt 2026-11-06): chữ key đa dạng màu (vàng, xanh lam, đỏ, tím, xanh dương, xanh ngọc, trắng — `DEFAULT_ROTATION`), **luôn phát sáng cùng màu** (`fx.key_glow`; vàng / trắng mức siêu nhẹ `GLOW["soft"]`); không hồng, cam, xanh lá — nếu buộc dùng thì phải phát sáng (`GLOW_REQUIRED`). Phụ đề dưới = dòng 1 trắng + dòng 2 xoay vòng đa màu theo cụm (`CAPTION_ROTATION`: vàng · xanh lam · xanh dương · xanh ngọc, không cam / hồng / tím / đỏ; nếu buộc dùng cam/hồng/tím thì phát sáng nhẹ `CAP_GLOW_REQUIRED`), font **đổi theo đoạn 3–5 nhịp** (Montserrat + viết tay mảnh ≤ 3 cụm · toàn Montserrat · Be Vietnam Pro · SF Pro Light — không dùng viết tay quá nhiều), có dải tối `fx.caption_band` sau vùng phụ đề (tương phản ≥ 4,5 : 1). Chữ phụ bóng nhẹ. Không xoá ngược chữ — ra bằng mờ dần; gõ chậm (~7 / ~6 ký tự/s). **Tiếng không vào trước hình** (kiểm bằng `qa_sync.py`). **Chữ không dùng viền** (yếu tố tiên quyết, rules.md mục 2): nổi bằng bóng đen lệch dưới-phải kiểu @magentx.ai (`MX_SHADOW`, `CAP_SHADOW`), màu bão hoà đậm. Tiếng chuyển cảnh 2 lớp (hút vào + hit) ở mức `transition`, nhạc hạ 5 dB quanh điểm cắt (`sfx_auto.duck`), `limit-master --max -2.0`. **[có nội dung đã thay — theo B15 hiện hành]**
- `SKILL.md:240` — 4. Âm thanh: `master_pipeline.py limit-master <project.fcproj>` (hard_limiter −1,5 dB trên master — giọng đã lọc sát −1,5 dBFS nên cộng nhạc + SFX là vượt 0 dBFS); `master_pipeline.py audit-sfx <project.fcproj>` (đủ file, không lặp take, đuôi không vượt video, không vỡ); đo loudness/true peak trên bản trộn: `scripts/qa_audio.py PROJECT.fcproj work/qa/mix.wav` (FilmCraft `export.quick` WAV 48 kHz 24-bit, không phải MP4 giao; in ĐẠT khi −16…−14 LUFS và TP ≤ −1,5). **[có nội dung đã thay — theo G5 hiện hành]**
- `SKILL.md:248` — - Gọi đúng tên phần đã kiểm ("tự kiểm" / "rà chéo"); còn nấc chưa kiểm thì gọi là "bản nháp".

## G7

- `references/style.md:95` — | G7 | **Chạy theo lô 5 project / lượt** (chốt 2026-11-12): sửa 5 → mở cho duyệt → xuất 5 MP4 → đo (`ffprobe`, `ebur128`) → mới sang 5 tiếp. Xuất MP4 **tối đa 2 phiên song song** (3 phiên + cửa sổ đang mở làm FilmCraft đóng kết nối, file ra thiếu); đóng cửa sổ FilmCraft của project trước khi ghi đè file hay xuất; việc GPU bọc `flock /tmp/gpu.lock`; chạy nhiều agent thì mỗi agent chỉ sửa 1 file project | mắt | **[có nội dung đã thay — theo G7 hiện hành]**
- `references/rules.md:84` — | GPU | RTX 3070 Ti 8 GB, dùng chung với FilmCraft/EffectCraft: công cụ AI nặng có thể thiếu bộ nhớ → chạy CPU hoặc đóng bớt app |

## G10

- `references/cindy-memories/feedback_time-budget-is-wall-clock.md:15` — **How to apply:** Bóc lời bằng faster-whisper large-v3-turbo CPU int8 ngay từ đầu; tiếng từ file video qua audio_of; kẹp keyframe trong clip; nguồn 4K quay ngang → proxy 1080×1920 bằng ffmpeg; chỉ fc_build một lần sau khi soát spec; kiểm 3–4 khung trước khi mở; qa_sync chạy sau khi mở project; không chờ Muse trong hạn ngắn; báo tiến độ theo mốc thời gian.

## G11

- `references/rules.md:66` — - Giao việc cho đội OPA (Hermes) chỉ qua skill `opa-delegate`.
- `SKILL.md:114` — - Chia việc: mặc định tự làm; việc độc lập lớn (phân tích nhiều video, nhiều cảnh) thì mở agent con chạy nền. Lệnh chạy lâu (whisper, render) do lead chạy nền. Đội OPA chỉ qua `opa-delegate`.

## P2

- `references/text-fx.md:13` — - Font: SF Pro Display (Medium nối/phụ đề 34–66 px · Heavy từ khoá 95–230) · Playfair Display Bold Italic (từ khoá màu nhấn 100–190) · Great Vibes (viết tay 96–300) · Montserrat Black (số 190–260) · Bebas Neue (HOA không dấu).
- `references/text-fx.md:14` — - Một màu nhấn mỗi video (tím `#B05FFD`, vàng `#F3C60F`/`#D7A21A`, xanh neon `#00C800`, xanh ngọc `#47A383`), còn lại trắng; tracking −20…−50; bóng đen mềm (60%, blur 10, lệch 4); không viền.

## P3

- `SKILL.md:91` — - Trắng + **một** màu nhấn/video (vàng `#F4C40C` mặc định; theo chủ đề: tím `#8C6CFF`, xanh neon `#04AC04`, hổ phách khi cảnh tối). Bóng mềm, không viền, giãn chữ âm.
- `references/text-fx.md:13` — - Font: SF Pro Display (Medium nối/phụ đề 34–66 px · Heavy từ khoá 95–230) · Playfair Display Bold Italic (từ khoá màu nhấn 100–190) · Great Vibes (viết tay 96–300) · Montserrat Black (số 190–260) · Bebas Neue (HOA không dấu).
- `references/text-fx.md:14` — - Một màu nhấn mỗi video (tím `#B05FFD`, vàng `#F3C60F`/`#D7A21A`, xanh neon `#00C800`, xanh ngọc `#47A383`), còn lại trắng; tracking −20…−50; bóng đen mềm (60%, blur 10, lệch 4); không viền.

## P5

- `SKILL.md:94` — - Chuyển cảnh: cắt thẳng là chính; flash/âm bản 1–2 khung, vệt sáng 0,25–0,6 s ở chỗ đổi phần, punch-in ×1,12–1,25, zoom blur 0,15–0,25 s che jump cut. Mép khung hơi mờ. **[có nội dung đã thay — theo C1 hiện hành]**

## CHUNG

- `references/style.md:60` — | D7 | **Phông sáng + người ở 2/3 dưới khung (Rule 5, chốt 2026-11-11):** đỉnh đầu ngang đường 1/3 trên (y ≈ 640 ± 60), 1/3 trên là nền sáng trống cho chữ chính. **Chỉ áp cho clip QUAY THẬT** (`live_shoot` trong manifest: phông xanh và nền sáng sẵn) — **KHÔNG áp cho avatar HeyGen** (chốt 2026-11-11, avatar giữ nguyên nền và khung gốc): nền tối / phông xanh → tách người (rvm-matte) ghép lên **phòng làm việc sáng, mờ** (ảnh trong `TNEDIT/07_Assets/Nen_Background/Phong_Lam_Viec_Sang/`, trống thì dùng nền dự phòng); nền đã sáng → chỉ chỉnh khung (phóng ≤ 1,35×, hơn nữa thì tách + ghép); clip quay xoay ngang tự xoay đúng. `scripts/frame_person.py` (analyze / fix), `run_kb_v2152.py` tự áp cho clip `live_shoot` trước bước tăng tốc | frame_person | **[có nội dung đã thay — theo D11 hiện hành]**
- `references/rules.md:50` — - Không mặc định nền navy, chữ viết tay (chữ vàng giờ là màu chủ đạo theo dòng "Màu chữ" ở trên). Kiểu @__dviet (serif nghiêng màu nhấn) chỉ áp khi người dùng chọn style đó — xem `dviet-style-guide.md`.
- `references/rules.md:82` — | Playbook HyperFrames cũ (Windows `D:\Vibe Coding\…`) | `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/AI Video/` (`prompts/MASTER_VIDEO_EDITOR_VI.md`, `prompts/VIDEO_EDITOR_REVIEW_PROMPT_VI.md`, `scripts/hf-pipeline/`, `EDITORIAL_RULES.md`) — chỉ có khi cắm USB |
- `references/rules.md:83` — | Phần mềm | FilmCraft 0.13 (`~/.local/bin/filmcraft`), EffectCraft 0.17, OpenChatCut, Diffusion Studio; không có After Effects / Premiere |
- `references/PROMPT_CHUAN_THEO_TANG.md:19` — ═══ QUY TRÌNH 8 TẦNG BẮT BUỘC (Agent tự chạy & in "TẦNG n ✔ <số đo>" sau mỗi tầng) ═══
- `SKILL.md:76` — - Khi người dùng gửi **Brief hoặc Kịch bản (đơn lẻ hoặc file Spec nhiều kịch bản)** chưa có sẵn video `A-Roll`/`B-Roll`: chạy ngay **Quy trình 10 bước chuẩn** (`scripts/analyze_and_scaffold.py` hoặc `scripts/master_pipeline.py analyze-spec|analyze-json`, xem mục "Phân tích Kịch bản A-Roll / B-Roll & Xuất Báo Cáo Thư Mục Con" bên dưới và `references/aroll-broll-workflow.md`) để tách cảnh linh hoạt, chuẩn hóa lời đọc tiếng Việt, khóa rule B-Roll (`no_voice`, `no_text`), tạo **Thư mục con đánh số** (`01_a-roll-1.mp4`, `02_b-roll-1.mp4` + `02_voice-b-roll-1.mp3`...) và xuất báo cáo `00_BAO_CAO_PHAN_TICH_AROLL_BROLL.md`. **[có nội dung đã thay — theo G5 hiện hành]**
- `SKILL.md:120` — 1. **Tỷ lệ và thứ tự `A-Roll` / `B-Roll` linh hoạt theo dạng kịch bản:**
- `SKILL.md:198` — - Sửa thư viện xong: chạy `scripts/text_fx_demo.py --snippets assets/text-fx/snippets.json`, cập nhật `const SNIP` trong trang xem trước, rồi `scripts/selfcheck.py --quick`.
- `references/text-fx.md:34` — Chữ nhỏ đứng yên; từ cũ mờ ra, từ mới blur-in, chồng 0,3 s. ⚠ Great Vibes mảnh: trên nền sáng cần dải tối phía sau.
- `references/text-fx.md:64` — `wonder_glow` (threshold 40, radius 22) cường độ 0 → ~120 trong 0,6 s. CapCut (video dạy): Hiệu ứng "phát sáng 2", Rực sáng ~70–100, Cỡ ~30–50; dùng cho chữ phát sáng hoặc flash. ⚠ Trên nền sáng glow trắng gần như không thấy — cần nền tối/dải tối.
- `references/text-fx.md:70` — Chữ trắng blend Overlay + bản glow mờ 35% bên dưới; vào bằng vệt kéo dọc 0,3 s. CapCut (video dạy): chữ trắng → Alt+G → Video → Cơ bản → Hoà trộn Overlay; nền đen cần xoá → Screen; nền trắng → Multiply. ⚠ Chỉ đẹp khi nền phía sau có chi tiết/màu (áo, tường); trên nền rất tối Overlay gần như mất chữ, khi đó bản glow mới là phần thấy được.
- `references/text-fx.md:82` — Thẻ video rộng 1000 px bo góc, viền màu nhấn 6 px, bóng; phóng 82 → 100% + nhoè 0,28 s (hoặc xoay 3D vào); nhãn SF Heavy 60 màu nhấn nằm ngay dưới mép thẻ (kênh đè lên mép, nhưng trên nội dung rối khó đọc — THCN 03). Nền mờ phía sau làm riêng (bản sao clip + `gaussian_blur` 60 + `brightness_contrast` −45).

## SKILL §11

- `SKILL.md:227` — - Overlay light leak TNEDIT là video ngang: `leak_overlay` xoay 90° phóng 177,8% và blend Add; phóng phủ khung thì mất vệt sáng.
- `references/motion-fx.md:45` — Khung sáng nhất của overlay (đo độ sáng từng khung) đặt trúng điểm cắt; lane `trans` (trên A-roll / B-roll / dải tối, dưới
- `references/motion-fx.md:46` — chữ — overlay từng làm chìm chữ). Overlay ngang có vệt sáng ở 2 mép → xoay 90° rồi phóng 177,8% (phóng 267% mất hết vệt).
- `references/text-fx.md:50` — Mỗi chữ một clip căn trái theo độ dài đo bằng PIL, giữ tới hết cụm (≤ 4 chữ, không tách số khỏi đơn vị), rộng ≤ 700 px tự thu cỡ (≥ 48). `mode="grey"`: xám → trắng; `mode="color"`: tím `#A855F7` → trắng 0,25 s. Mốc từng từ lấy từ Whisper: `build_kit.align_words(chữ kịch bản, từ Whisper)`. Phụ đề trên áo/tường sáng: `shadow=STRONG_SHADOW` (bóng 85%, blur 14 — THCN 03).

## SKILL §2

- `references/cindy-memories/project_aroll-broll-10step-pipeline.md:17` — Đã đồng bộ analyze_and_scaffold.py bản đầy đủ (render-all/aroll/broll + rule live_shoot) vào master-video-edit/scripts và sửa bug script_id hardcode "KB01" (chạy nhiều kịch bản 1 JSON bị ghi đè thư mục). ElevenLabs render voice chưa có lệnh trong script — chỉ xuất prompts_elevenlabs_voice.json.

## SKILL §2.1

- `SKILL.md:124` — - Hỗ trợ mọi trật tự xen kẽ (`01_a-roll-1` ➔ `02_b-roll-1` ➔ `03_a-roll-2` hoặc mở đầu bằng `01_b-roll-1` ➔ `02_a-roll-1`).

## SKILL §3.3

- `SKILL.md:103` — - Cắt khoảng lặng tự động (A-roll một clip dài, nói lặp lại ngắt quãng): `scripts/silence_cut.py <giọng_đã_lọc.wav> --words <transcripts/*.json>` in các đoạn giữ và thời lượng sau cắt; trong `build_spec.py`: `words = load_words(json)`, `segs = speech_segments(voice, words)`, `words = fit_words(words, segs)` (bắt buộc trước khi làm phụ đề / đặt chữ theo lời), `words = refine_words(words, voice_wav)` (căn mốc từ đầu sau lặng theo tiếng thật), `tl = Timeline(segs)` → V1 / A1 mỗi đoạn một clip (`in` = giây vào, `at` = `tl.T0[i]`), chữ / SFX đặt bằng `tl.at(giây_nguồn)`, kết thúc chữ ở `tl.end_of(giây_nguồn)`; mọi điểm cắt vẫn phải có chuyển cảnh (`cut_plan.py`). Ngưỡng mặc định −35 dB / 0,3 s; phòng ồn thì lọc giọng `--mode heavy` trước. Ví dụ chạy trọn: `/home/vmiz/Thanh/Media/TNEDIT/09_Du_An/THCN/Video04_Thu_V2/work/build_spec.py` (53,6 s → 34,5 s, 12 đoạn).
- `references/motion-fx.md:327` — - Clip có khoảng lặng dài giữa câu (CTA THCN 07: 5,2 s) → tách đoạn theo mốc lời (khoảng lặng > 0,9 s), mỗi đoạn một clip
- `references/motion-fx.md:328` — V1 và có chuyển cảnh riêng.

## SKILL §3.6

- `SKILL.md:206` — Chọn hiệu ứng theo **khoảnh khắc** (bảng "Khi nào dùng" trong `references/motion-fx.md`): câu thường → `captions2`, từ khoá → `keyword_tpl`, câu chốt → `collage`, liệt kê → `word_pop`, điểm cắt → kiểu do `cut_plan` chọn (`fx.cut_fx`), B-roll vào → `grid_reveal` / `strip_reveal` + `flash_burst`, cao trào → `cut_burst`. Mỗi hàm ghi `fx.cues`; `plan_sfx` biến thành clip SFX (đã căn đỉnh, chỉnh mức theo lúc đang nói, không lặp file, SFX mở đầu khung 0).
- `references/motion-fx.md:234` — ## Khi nào dùng (chọn theo khoảnh khắc, không theo dạng video)
- `references/motion-fx.md:236` — | Khoảnh khắc | Chữ | Chuyển cảnh | SFX tự gắn |
- `references/motion-fx.md:237` — |---|---|---|---|
- `references/motion-fx.md:238` — | Câu thoại thường | `captions2` | — | không (phụ đề không tick) |
- `references/motion-fx.md:239` — | Hook / từ khoá của câu | `keyword_tpl` (dẫn nhỏ + từ khoá gradient phát sáng + viết tay) | — | tick gõ, hit khi từ khoá rơi, nét bút, lấp lánh khi giữ ≥ 1,4 s |
- `references/motion-fx.md:240` — | Câu chốt nhiều tầng nghĩa | `collage` (sans đậm + viết tay to phát sáng) | — | hit ở chữ lớn |
- `references/motion-fx.md:241` — | Liệt kê, đếm, outro | `word_pop` / `label_quote` | — | click mỗi từ (một chùm một file) |
- `references/motion-fx.md:242` — | Jump cut giữa câu | — | punch 100 ↔ 112% + `join(clip, "zoom")` | whoosh nhẹ |
- `references/motion-fx.md:243` — | Jump cut sang câu mới | — | theo `cut_plan` (zoom_through, panel_wipe, flash_shake, spin_zoom, light_leak…) | theo kiểu |
- `references/motion-fx.md:244` — | Đổi phần lớn | — | split_slide / rgb_glitch / film_burn / spin | theo kiểu |
- `references/motion-fx.md:245` — | B-roll vào | — | `grid_reveal` / `strip_reveal` + flash_burst | click mỗi ô + flash hit |
- `references/motion-fx.md:246` — | Cao trào, dẫn chứng dồn dập | — | `cut_burst` | riser + click mỗi cắt + flash hit |

## SKILL §4

- `SKILL.md:162` — - `fx.cues` chỉ là **gợi ý** SFX; kênh mẫu không gắn SFX cho mọi chữ (chỉ cao hơn ngẫu nhiên 2–15 điểm) — chữ lớn nên rơi vào phách nhạc (`build_kit.on_beat`), SFX rời chỉ ở chuyển động lớn hoặc có nghĩa.
- `references/text-fx.md:96` — ## SFX đi với chữ (đo)
- `references/text-fx.md:97` — 340 lần chữ xuất hiện: có tiếng nổi bật ±0,15 s chỉ cao hơn ngẫu nhiên 2–15 điểm → kênh không gắn SFX cho từng chữ. Chữ lớn rơi vào snare của nhạc (ví dụ 97,5 BPM: "21" 6,8 s, "editor" 19,2 s); tiếng rời chủ yếu là whoosh khi chữ/thẻ trượt vào. `fx.cues` chỉ gợi ý các khoảnh khắc có chuyển động lớn hoặc có nghĩa (bấm bookmark, gạch chữ, gõ chữ).

## SKILL §7.4

- `references/motion-fx.md:106` — - Kiểm: `python3 scripts/qa_sync.py work/x.craft.json x.fcproj qa <mốc cắt…>` → ĐẠT khi |đỉnh tiếng − khung mạnh nhất|
- `references/motion-fx.md:107` — ≤ 0,05 s và tiếng không vào sớm hơn hình > 0,1 s. Demo THCN 03 bản vòng 10 và 11: 6/6 ĐẠT (−0,04 … +0,05 s).

## SKILL §8

- `SKILL.md:105` — - Áp nhịp dựng (`references/rules.md` mục 7) lên timeline spec có sẵn: `scripts/remix_rules.py` → `craft-handoff/tools/fc_build.py`. Dựng lại từ spec nên mất chỗ người dùng đã sửa tay; cách dùng và giới hạn ở `references/pipelines.md` GĐ4.
