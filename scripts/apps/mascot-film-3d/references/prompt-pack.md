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
