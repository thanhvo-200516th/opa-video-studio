# Sổ tay After Effects: dựng và sửa project bằng script

Bản cuối v3, ngày 26/10/2026. Nguồn:
- **ca mẫu nhánh A** "OPA Agent × Pancake": bản v07–v10, 21–23/10;
- **bộ phân tích template AE** ngày 21/10;
- **ca mẫu nhánh B** sửa "template 5.aep", do một phiên agent khác làm (23–26/10);
- các bài học đã ghi trong memory.

Mọi con số đều đo trên máy của Minh, trừ chỗ ghi "nguồn web" hoặc "chưa đo".

Đọc nhanh: mục 2 (chọn nhánh), 3 (chạy AE), 5 (keyframe), 6 (chữ), 9 (âm), 11 (kiểm).

Ký hiệu đường dẫn:

| Ký hiệu | Đường dẫn |
|---|---|
| `<SKILL>` | thư mục của skill này (chứa `SKILL.md`) |
| `<VD-A>` | `<SKILL>\examples\opa-agent`: bản chụp code ca mẫu nhánh A |
| `<VD-B>` | `<SKILL>\examples\template-5`: script ca mẫu nhánh B |
| `<KHUNG>` | `<SKILL>\templates\du-an-ae`: bộ khung dự án mới, đã thử |
| `<AE>` | `C:\Program Files\Adobe\Adobe After Effects 2026\Support Files` |
| `<SFX>` | `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx`: kho SFX của Minh |
| `<OPA>` | `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/OPA-Motion-graphic-mascot`: dự án OPA sống |

Máy khác thì đổi các đường dẫn này theo mục 17.

## Mục lục

1. Từ ngữ
2. Bức tranh chung: hai nhánh
3. Chạy AE mà không đụng phiên của Minh
4. Cấu trúc project
5. Keyframe và easing
6. Chữ
7. Hình: shape, matte, parent, expression, máy quay, nhân vật, giao diện
8. Chuyển động và nhịp
9. Âm thanh
10. Render và xuất file
11. Thang kiểm trước khi giao
12. Học từ template AE có sẵn
13. Nhánh B: sửa template mua về
14. Bàn giao và cách sửa
15. Nhánh A: bắt đầu dự án mới
16. Lỗi hay gặp
17. Cấu hình máy, cài skill, phụ thuộc
18. Nguồn

## 1. Từ ngữ

| Từ | Nghĩa |
|---|---|
| Comp (composition) | Một khung dựng có kích thước, fps, thời lượng. Comp đặt trong comp khác gọi là pre-comp |
| Layer | Một lớp trong comp: chữ, hình vẽ (shape), ảnh, âm, null, comp con |
| Null | Layer vô hình làm tay cầm. Gắn layer khác vào để di chuyển chung, ví dụ máy quay ảo |
| Parent | Layer cha. Con đi theo vị trí, tỉ lệ, góc xoay của cha, nhưng không theo độ mờ |
| Khung (frame) | Một hình. 30 fps là 30 khung mỗi giây. Đánh số từ 0 |
| Keyframe (key) | Mốc giá trị tại một khung. AE tự tính giá trị giữa hai key |
| Nội suy | Cách đi giữa hai key: Linear (đều), Bezier (tăng, giảm tốc), Hold (đứng yên rồi nhảy) |
| Easing | Đường tăng tốc, giảm tốc giữa hai key |
| Speed, Influence | Hai số của mỗi tay nắm ease: tốc độ tại key và độ dài tay nắm (% của đoạn). Speed 0 với influence lớn là chậm lâu ở hai đầu |
| Temporal, spatial | Temporal: tốc độ theo thời gian. Spatial: hình dạng đường đi của Position. Hai thứ khác nhau |
| cubic-bezier | Cách viết easing trên web. Đổi qua lại được với speed, influence (mục 5.1) |
| Text Animator | Bộ tạo chuyển động cho chữ theo ký tự, từ hoặc dòng, nằm ngay trong layer chữ |
| Range Selector | Phần của Text Animator chọn chữ nào bị tác động. Cho Start chạy 0→100 thì chữ lần lượt hiện |
| em | Cỡ chữ dùng làm đơn vị. Chữ 126 px thì 1 em = 126 px |
| Track matte | Lấy độ trong suốt (alpha) của một layer làm khuôn cho layer khác |
| Mask | Đường cắt vẽ ngay trên layer |
| Expression | Đoạn JavaScript nhỏ gắn vào thuộc tính, tính lại giá trị mỗi khung |
| matchName | Tên cố định của thuộc tính dùng trong script (ví dụ `ADBE Opacity`). Không đổi theo ngôn ngữ giao diện |
| JSX, ExtendScript | Ngôn ngữ script của AE (JavaScript đời cũ, ES3) |
| Headless | Chạy AE không mở giao diện, trong một phiên riêng |
| aerender | Chương trình render của AE, chạy bằng dòng lệnh |
| Seed | File .aep trống dùng làm gốc để lưu project mới |
| Holder (comp giữ chỗ) | Comp trong template để người dùng thả logo, ảnh, video, nhạc của mình vào |
| .aepx | Project AE dạng XML (đọc được bằng chữ), cùng nội dung với .aep |
| BT.709 | Chuẩn màu video HD. MP4 phải gắn thẻ này thì máy phát mới hiện đúng màu |
| LUFS, LU | Độ to cảm nhận theo chuẩn ITU-R BS.1770. LU là chênh lệch giữa hai mức LUFS |
| M, S, I | Độ to tức thời (cửa sổ 400 ms), ngắn hạn (3 s), tích hợp (cả bài) |
| dBTP | Đỉnh thật: tính cả đỉnh nằm giữa hai mẫu số |
| LRA | Dải độ to: phần to và phần nhỏ của bài chênh nhau bao nhiêu LU |
| SFX, cue | SFX là hiệu ứng âm. Mỗi lần đặt một SFX vào timeline là một cue |
| Master âm | Bước cuối: chỉnh cả bản về đúng độ to và chừa khoảng trống cho đỉnh |
| Tĩnh A, Tĩnh B | Số đo khung đứng của `metrics.py`. Tĩnh B: khung gần như không đổi so với khung trước (≤ 0,5 % điểm ảnh đổi). Tĩnh A: khung đứng hẳn (≤ 0,04 %) |
| Q, Q5 | Agent rà chéo mới, chưa đọc gì của dự án. Q soát hình và chữ, Q5 soát âm (mục 11.1) |
| B8 | Ca cũ của pipeline video: bản trộn vượt trần đỉnh vì tiếng tick trùng đỉnh giọng. Từ đó có trần −12 dBTP mỗi cue và master ở −16,1 |

## 2. Bức tranh chung: hai nhánh

| | Nhánh A: dựng mới bằng script | Nhánh B: sửa template mua về |
|---|---|---|
| Khi nào | Không có template; cần .aep sạch, phân tầng rõ, dựng lại được | Có sẵn template .aep (Envato…) gần đúng ý |
| Đầu vào | kịch bản khóa, bảng cảnh | template .aep, kịch bản, logo, ảnh, giao diện, nhạc |
| Cách làm | JSX tạo mọi comp, layer, key từ đầu (mục 15) | đọc cấu trúc template, thay chữ, màu, tài nguyên, gắn SFX bằng script (mục 13) |
| Ca mẫu | `<VD-A>` (OPA Agent, đã qua thang kiểm) | `<VD-B>` (template 5, chưa kiểm lại khi đóng gói) |
| Phần dùng chung | chạy AE (3), keyframe (5), chữ (6), âm (9), render (10), thang kiểm (11), bàn giao (14) | như bên trái |

Lý do dựng bằng script thay vì bấm tay:
1. Đầu ra là .aep thật: có layer chữ, layer shape, keyframe gốc. Minh mở ra sửa được.
2. Dựng lại từ đầu chỉ mất khoảng 5–17 s. Sửa bao nhiêu vòng cũng không lệch.
3. Agent không phải bấm chuột vào AE của Minh.

Quy trình nhánh A:

```
kịch bản khóa ─► bảng cảnh (KHUNG-DUNG.md)
 ─► JSX: lib.jsx + scenes/*.jsx + main.jsx (+ dữ liệu sinh: path, cue âm)
 ─► AE headless (tools/ae.py build) ─► project .aep + báo cáo build/_report.json
 ─► aerender (tools/ae.py render) ─► MP4 ─► gắn thẻ BT.709
 ─► âm: SFX theo chuyển động + nhạc nền + giọng (tools/am_thanh_cues.py) ─► dựng lại
 ─► master âm (master.py) ─► thang kiểm + rà chéo ─► giao
```

## 3. Chạy AE mà không đụng phiên của Minh

Minh thường để AE mở sẵn, và có khi một agent khác cũng đang chạy script trong phiên đó. Vì vậy:
- không gửi script vào phiên ấy;
- không điều khiển AE bằng chuột (computer-use);
- không dùng mẹo đổi tiến trình cha (parent PID) để đẩy script vào phiên đang mở;
- mọi việc chạy trong một phiên AE riêng.

Nếu Minh muốn chạy script trong phiên AE đang mở của Minh:
- agent chỉ soạn file JSX;
- Minh lưu project của mình trước, rồi tự chạy bằng menu File › Scripts › Run Script File…;
- script không đóng project, không bỏ thay đổi chưa lưu, và lưu kết quả ra file mới.

### 3.1 Lệnh

```bash
cd "<thư mục dự án AE>"
python -I tools/ae.py build          # dựng project từ build/*.jsx
python -I tools/ae.py render --comp <COMP> --start 0 --end <khung cuối> --out out/review/_lam/bNN.mp4
python -I tools/ae.py stills --comp <COMP> --frames 20,60,100 --outdir out/stills
```

`tools/ae.py build` làm 5 việc:
1. Gộp các file theo thứ tự trong `BUNDLE_ORDER` thành `build/_bundle.jsx`: `lib.jsx`, `data/*.jsxinc`, `scenes/*.jsx`, `main.jsx`.
2. Đổi tên project cũ thành `*.bak-<giờ>.aep`, rồi chép seed trống `tools/seed/empty-ae26.aep` ra đường dẫn đích.
3. Mở phiên AE riêng: `AfterFX.exe -noui -m -s "<loader>"`.
4. Chờ tối đa 600 s. Quá giờ thì dừng đúng tiến trình đó.
5. Đọc `build/_report.json` và in lỗi.

### 3.2 Loader

```js
if (!(app.project && (app.project.file || app.project.numItems))) {
  var OPA_ARGS = {target: 'D:/.../project/X.aep', report: 'D:/.../build/_report.json', sfx: 'D:/.../assets/sfx'};
  var f = new File('D:/.../build/_bundle.jsx'); f.encoding = 'UTF-8'; f.open('r'); var s = f.read(); f.close(); eval(s);
}
```

- Loader là **một dòng**: `tools/ae.py` ghép sẵn thành một chuỗi rồi truyền làm một tham số. Bản trên xuống dòng chỉ để dễ đọc.
- Ý nghĩa các cờ:
  - `-noui`: chạy không giao diện;
  - `-m`: mở một phiên AE mới, riêng, không trao script cho phiên đang mở;
  - `-s`: chạy chuỗi script đi kèm.
- Loader chỉ đọc file bundle rồi `eval`. Không nhét cả script vào tham số `-s`.
- Trong loader không có `$` và không có dấu `"`, vì dòng lệnh Windows làm hỏng chúng. Đường dẫn viết bằng `/`.
- Dòng đầu là chốt an toàn: nếu phiên đã có project thì không chạy gì.
- Mấy cách sau không chạy được:
  - `-m -r file.jsx`: phiên mới tự thoát sau khoảng 6 s;
  - `$.evalFile` đặt trong `-s`.
- Phiên mở bằng `-s` tự thoát khi script chạy xong.
- Chạy một JSX bất kỳ (ví dụ script trích template, mục 12) cũng theo cách này: loader đọc file JSX rồi `eval`. Script phải tự ghi kết quả ra file.

### 3.3 Lưu .aep

- Phiên headless không lưu được project mới: `app.project.save(new File(...))` trả `false`.
- Cách làm: chép seed trống ra đường dẫn đích → `app.open(file)` → dựng → `app.project.save()` để lưu đè lên chính nó.
- Sửa một project có sẵn (nhánh B): chép project ra bản sao → mở bản sao → sửa → `save()`. Không mở file gốc.
- Template do bản AE cũ lưu cũng mở ra thành "converted", và phiên headless không lưu được nó. Nhờ Minh mở template bằng AE 2026 rồi File › Save As ra một file mới, một lần. Từ đó làm trên bản sao của file mới.
- Seed phải do chính AE 2026 lưu. Seed của bản AE cũ mở ra sẽ thành project "converted", khi đó `save()` đòi Save As.
- Mất seed, hoặc AE lên bản mới:
  - còn một file .aep do đúng bản AE hiện tại lưu: chép nó ra, mở bằng phiên headless, xóa mọi item (`app.project.item(i).remove()`, đi từ cuối về đầu), rồi `save()`. File đó thành seed mới;
  - AE vừa lên bản, chưa có file nào của bản mới: nhờ Minh mở AE, tạo project trống, File › Save As một lần.
- `main.jsx` kiểm project vừa mở có 0 item. Không đúng thì dừng.
- Đầu script gọi `app.beginSuppressDialogs()`, cuối script gọi `app.endSuppressDialogs(false)`.
- Đặt `project.expressionEngine = 'javascript-1.0'` và `project.bitsPerChannel = 8`.
- Hàm cần giao diện như `comp.openInViewer()` không dùng trong phiên headless.

### 3.4 Báo cáo

- Kênh kết quả duy nhất là file JSON do script ghi (`O.writeFile`). `app.exitCode` không truyền ra mã thoát.
- Mọi lỗi phải được ghi vào báo cáo. Không có khối `catch` rỗng.
- Báo cáo của ca mẫu nhánh A gồm:
  - `errors`, `warnings`;
  - `expressionErrors`: đã buộc tính mọi expression trước khi gom lỗi;
  - `textDump`: mọi layer chữ, kèm chữ, font, cỡ, `substitute`;
  - `comps`, `placements`, `texts` (công thức, mốc), `measures`;
  - `sfx`, `music`, `voice`, `saved`, `seconds`.

### 3.5 Treo, quá giờ

- Chỉ dừng đúng PID mình mở.
- Phiên bị buộc tắt thì lần mở sau hiện hộp "Crash Repair Options". Gửi phím Enter vào đúng cửa sổ của phiên mình (PostMessage theo PID) để chọn Continue.

## 4. Cấu trúc project

### 4.1 Phân tầng của template chuyên nghiệp

Template "Corporate Opener" (đọc bằng script ngày 21/10) phân tầng như sau:

`Master → Scene → Title (thiết kế chữ) → Text (nội dung) → layer chữ → Text Animator → Range Selector`

Mỗi tầng làm một việc:
- **Text:** nội dung, font, chuyển động theo từ, dòng hoặc ký tự.
- **Title:** gói text lại, để đổi chữ mà vẫn giữ cách dựng.
- **Scene:** vị trí, tỉ lệ, thời gian vào ra của cả khối, quan hệ với hình.
- **CONTROL:** màu, kích thước, vật liệu, điều khiển qua effect và expression.
- **Master:** thứ tự cảnh và các điểm nối.

Chất lượng của template đến từ cách phối các tầng này, không đến từ một hiệu ứng "chữ bay lên, mờ dần".

### 4.2 Cấu trúc ca mẫu nhánh A

```
00_MASTER/                     OPA_AGENT_MASTER_16x9: 5 cảnh, giọng đọc, marker câu thoại, comp âm
01_CANH (scene)/               S1_MO_DAU … S5_CTA; mỗi cảnh có null CAM
02_TITLE (thiet ke chu)/       TITLE_S1…S5: vị trí, offset thời gian, khối nhấn, icon đi kèm chữ
03_EDIT_CHU (sua chu o day)/   TXT_*: mỗi comp một layer "TEXT" có Text Animator
04_HINH/                       ART_* (nhân vật, mascot), UI_* (giao diện minh họa)
05_CONTROL (mau)/              CONTROL: null BRAND + Color Control; mọi màu shape nối bằng expression
06_AM_THANH/                   AM_THANH_SFX_NHAC: nhạc nền + các layer SFX; file WAV
```

- Tên comp và tên layer viết không dấu, để gọi `aerender -comp` và viết expression không lỗi mã hóa. Chữ hiển thị thì đủ dấu.
- `comp.comment` ghi mốc thời gian và cách sửa cho người mở project.
- Marker câu thoại nằm trên một null dẫn hướng (`guideLayer = true`, `enabled = false`), mỗi câu một marker tại giây bắt đầu.

### 4.3 Đặt comp con và đổi khung

- `O.place(cha, con)` đặt anchor bằng tâm comp con và position bằng tâm comp cha. Hai comp cùng kích thước thì toạ độ đi qua 1:1.
- Key trong comp con là khung **cục bộ**:
  - giây trên master = `sceneLayer.startTime + subLayer.startTime + … + giây của key` (cộng hết các tầng);
  - layer có stretch (`layer.stretch`, 100 = bình thường): giây trên comp cha = `startTime + giây cục bộ × stretch / 100`;
  - layer có time remap: không có công thức gọn. Tra bằng `timeRemap.valueAtTime(t)` trên comp cha để biết giây t của cha đang chiếu giây nào của con;
  - khung = `round(giây × fps)`.
- Ví dụ template: key f30 của Text 1 hiện ở f57 của Scene 1, vì Title 1 bắt đầu ở f27.
- `tools/bang_khung.py` (ca mẫu A) tự tính bảng mốc chữ theo khung master. `<VD-B>\parse_aep_timings.py` tính giây toàn cục cho mọi cảnh, comp con của template.

### 4.4 CONTROL màu

- Comp `CONTROL` có một null `BRAND`. Mỗi màu là một effect Color Control trên null đó.
- Màu của shape: đặt giá trị rồi gắn expression `comp("CONTROL").layer("BRAND").effect("blue")(1)`. Đổi một màu ở CONTROL thì cả phim đổi theo.
- Đổi màu tại một giây t: `var a = …, b = …; time < t ? a : b` (`O.fxColorSwitch`).

### 4.5 Cấu trúc template thương mại (ví dụ template 5)

- Comp tổng: `Final_4k (3840 x 2160)` và `Full_HD (1920 x 1080)`, chứa `01_Scene` … `13_Scene` nối nhau.
- Comp giữ chỗ (Holder) nằm trong thư mục Edit:
  - `Logo_Holder` (1000×1000);
  - `01_Person_Holder` … `08_Person_Holder` cho chân dung;
  - `06_Scene_Avatar01`, `06_Scene_Avatar02` cho avatar khung chat;
  - `Music_Holder` cho nhạc.
- Màu điều khiển tập trung ở các layer `Text Colors`, `Background Colors`, `Icons, Buttons & UI Colors` trong comp tổng. Vài comp còn màu gán cứng, ví dụ `Color_Flash` dùng `ADBE 4ColorGradient`, và Glow trên một số icon.
- Tên comp có thể trùng giữa các nhánh template. Nhận diện bằng ID kèm chuỗi sử dụng.

## 5. Keyframe và easing

### 5.1 Kiến thức nền

- Mỗi key có tay nắm vào (in) và tay nắm ra (out). Mỗi tay nắm là `KeyframeEase(speed, influence)`.
- **speed:** tốc độ tại key, đo bằng đơn vị của thuộc tính mỗi giây. 0 là đứng yên ở key.
- **influence:** tay nắm dài bao nhiêu % của đoạn, từ 0,1 đến 100. Càng lớn càng chậm lâu ở key.
- Easy Ease (phím F9) = speed 0, influence 33,33 %. Template chuyên nghiệp không dùng F9: chữ dùng khoảng 75 %.
- Sổ tay ghi preset dạng `{o: [k_o, inf_o], i: [k_i, inf_i]}`:
  - `o` là tay nắm ra của key đầu, `i` là tay nắm vào của key sau;
  - `k` là hệ số tốc độ: speed thật = k × tốc độ trung bình của đoạn.
- Đổi sang cubic-bezier của web:
  `cubic-bezier(inf_o/100, k_o × inf_o/100, 1 − inf_i/100, 1 − k_i × inf_i/100)`.

### 5.2 Bảng preset

Các preset nằm trong `O.EASE` của `lib.jsx`. Số trong ngoặc vuông là [hệ số tốc độ; influence %].

| Preset | o | i | cubic-bezier | Dùng cho | Nguồn |
|---|---|---|---|---|---|
| R1_IN | [0; 75,217] | [0; 75,121] | (0.752, 0, 0.249, 1) | Headline vào | template, đo native |
| R1_OUT | [0; 75,121] | [0; 75,217] | (0.751, 0, 0.248, 1) | Headline ra | template |
| R2_IN | [0; 75,322] | [0; 75,664] | (0.753, 0, 0.243, 1) | Nhãn phụ theo dòng (ra: đảo hai số) | template |
| R3_IN | [0; 75,217] | [0; 75,603] | (0.752, 0, 0.244, 1) | Display theo ký tự | template |
| R3_OUT | [0; 100] | [0; 20,993] | (1, 0, 0.79, 1) | Display ra | template |
| R4_IN | [0; 70,636] | [0; 70,540] | (0.706, 0, 0.295, 1) | Heading nhiều dòng | template |
| R5_IN | [0; 60,752] | [0; 60,174] | (0.608, 0, 0.398, 1) | Body theo dòng từ phải (ra: đảo hai số) | template |
| MASK (R10) | [0; 15,236] | [0; 100] | (0.152, 0, 0, 1) | Mở khung bằng matte: nhanh lúc đầu, đuôi dài | template |
| R6A, rồi R6B | [0; 0,01] → [0; 100] | [0; 100] → [0; 15,133] | | Thu cả khối chữ ở cấp Scene: 100 → 86 → 0 | template (Scene 5) |
| BRAND | [4; 20] | [0; 80] | (0.2, 0.8, 0.2, 1) | Vật vào cảnh | V2 (EASE_IN_SCENE) |
| EXIT | [0; 60] | [4; 20] | (0.6, 0, 0.8, 0.2) | Vật ra cảnh | V2 |
| SOFT | [0; 50] | [0; 50] | (0.5, 0, 0.5, 1) | Máy quay trôi, đoạn giữ | ca mẫu A |
| PUSH | [0; 85] | [2,2; 30] | (0.85, 0, 0.7, 0.34) | Máy quay lao vào điểm cắt | ca mẫu A |
| LIFT | [0; 15] | [0; 80] | (0.15, 0, 0.2, 1) | Vật cất cánh từ tốc độ 0 | ca mẫu A |
| LINEAR | — | — | đều | Nền trôi, kim đồng hồ | |
| HOLD | — | — | nhảy | Bật, tắt tức thì | |

- Mỗi vai trò một đường ease: chữ, mask, máy quay, vật khác nhau.
- Đừng tự thêm nảy (bounce) hay lò xo cho chữ khi công thức không có.

### 5.3 Đặt key bằng script

Hàm của ca mẫu: `O.anim(prop, [[khung, giá trị], [khung, giá trị, 'PRESET'], ...])`. Preset ghi ở key k là đường ease của đoạn từ key k−1 tới key k.

Thứ tự gọi bắt buộc:
1. `prop.setValueAtTime(t, v)` cho mọi key.
2. Lấy chỉ số key bằng `prop.nearestKeyIndex(t)`.
3. `prop.setTemporalEaseAtKey(k, inEase[], outEase[])`.
4. **Sau cùng** mới gọi `prop.setInterpolationTypeAtKey(k, inType, outType)`.

Lý do: `setTemporalEaseAtKey` đổi luôn phía LINEAR của key thành Bezier. Ca mẫu từng dính lỗi này: nền trôi "LINEAR" vẫn chậm dần ở hai đầu.

```js
// a, b: giá trị hai key liền nhau (1 chiều); dt: số giây giữa hai key; P = {o:[ko, io], i:[ki, ii]}
var avg = (b - a) / dt;
var outE = [new KeyframeEase(P.o[0] * avg, P.o[1])];
var inE  = [new KeyframeEase(P.i[0] * avg, P.i[1])];
prop.setTemporalEaseAtKey(k0, prop.keyInTemporalEase(k0), outE);
prop.setTemporalEaseAtKey(k1, inE, prop.keyOutTemporalEase(k1));
prop.setInterpolationTypeAtKey(k0, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER); // gọi sau ease
```

- Số phần tử của mảng ease bằng số chiều của thuộc tính:
  - Opacity: 1;
  - Scale: 3, kể cả layer 2D;
  - Audio Levels: 2;
  - Position là thuộc tính spatial nên chỉ 1 phần tử, là tốc độ dọc đường đi: speed = hệ số × (khoảng cách giữa hai key / số giây giữa hai key).
- Position đi thẳng: tắt `setSpatialAutoBezierAtKey` và `setSpatialContinuousAtKey`, rồi đặt `setSpatialTangentsAtKey(k, [0,0], [0,0])`. Không làm thì AE tự uốn cong đường đi.
- Đoạn giữ 100 → 100 nằm giữa pha vào và pha ra: dùng Bezier phẳng (SOFT) như template. Không cần HOLD.

### 5.4 Lò xo

- Lò xo OPA (SPRING_POP của V2): damping 12, stiffness 100, mass 1. Kết quả: vọt khoảng 9,5 %, đỉnh lúc 0,39 s.
- Trong AE, tính nghiệm lò xo y(t) = 1 − e^(−6t)·(cos 8t + 0,75·sin 8t) ra 4 key (`O.springKeys`, `O.popScale`). Ví dụ nút bật từ 0 lên 100 % ở 30 fps, bắt đầu tại khung `at`:

| Key | Khung | Scale (%) | Ease của đoạn đi tới key này |
|---|---|---|---|
| 1 | at | 0 | — |
| 2 | at + 12 (0,39 s) | 109,5 | BRAND |
| 3 | at + 24 (0,79 s) | 99,1 | SOFT |
| 4 | at + 39 (1,18 s + 4 khung) | 100 | SOFT |

- Key 4 là key cuối. Sau đó nút đứng ở 100 %, hoặc thở bằng expression.
- Số khung làm tròn bằng `Math.round(giây × fps)`. Ở 60 fps thì tính lại theo giây.
- Dùng key thay vì expression lò xo, để mở .aep ra vẫn thấy key.
- Lò xo dùng cho icon, nút, tin nhắn, mascot. Không dùng cho chữ: chữ đi bằng Text Animator.

### 5.5 Đổi fps

Giữ nguyên số giây, đổi số khung: khung ở 60 fps = khung ở 30 fps × 2. Influence giữ nguyên.

### 5.6 Đọc key từ project có sẵn

- Các hàm: `prop.numKeys`, `prop.keyTime(k)`, `prop.keyValue(k)`, `prop.keyInInterpolationType(k)`, `prop.keyInTemporalEase(k)[d].speed` và `.influence`, `keyTemporalAutoBezier`, `keyInSpatialTangent`.
- Script mẫu: `<SKILL>\references\template-audit\scripts\export-projects.jsx`.
- Giá trị enum: BEZIER = 6613, LINEAR = 6612, HOLD = 6614.
- Muốn lấy đường cong thật: đọc `prop.valueAtTime(f/fps, false)` mỗi 0,25 khung (`sample-and-render.jsx`).

## 6. Chữ

### 6.1 Text Animator hoạt động thế nào

- Animator chứa các giá trị lệch: Position [0, 1 em], Opacity 0, Blur. Range Selector chọn phần chữ chịu các giá trị lệch đó.
- Pha vào: keyframe `Start` từ 0 lên 100. Phần được chọn co dần, chữ lần lượt về đúng chỗ, rõ nét và hiện đủ. Pha ra: Start từ 100 về 0.
- Opacity 0 là độ mờ của phần đang được chọn. **Transform Opacity của layer chữ giữ ở 100.**
- Chỉ đặt key cho Position hay Opacity của cả layer thì không tạo được kiểu hiện theo từ, dòng, ký tự.
- **Một animator cho cả câu.** Đặt `Based On` = Từ thì AE tự chia từng từ. Không cần mỗi từ một animator.

| Phần | matchName |
|---|---|
| Animator | `ADBE Text Properties` › `ADBE Text Animators` › `ADBE Text Animator` |
| Giá trị lệch | `ADBE Text Animator Properties` › `ADBE Text Position 3D`, `ADBE Text Opacity`, `ADBE Text Blur` |
| Selector, Start | `ADBE Text Selectors` › `ADBE Text Selector` › `ADBE Text Percent Start` |
| Based On | `ADBE Text Range Advanced` › `ADBE Text Range Type2`: 1 = ký tự, 2 = ký tự trừ khoảng trắng, 3 = từ, 4 = dòng |
| Shape | `ADBE Text Range Advanced` › `ADBE Text Range Shape` = 1 (vuông) |

### 6.2 Công thức

Template đo trên chữ rất to (300 px, khổ 2160). Ca mẫu đổi sang em để giữ đúng tỉ lệ chuyển động.

| Mã | Dùng cho | Based On | Position | Blur | Ease |
|---|---|---|---|---|---|
| R1 | Headline | Từ (3) | [0; 1,0 em] | 0,427 em | R1_IN, R1_OUT |
| R2 | Nhãn phụ, cụm nhấn, câu định vị, nhãn CTA | Dòng (4) | [0; 0,667 em] | 0,667 em | R2 |
| R3 | Display, tên, URL, câu chốt | Ký tự (1) | [0; 0,711 em] | 0,356 em | R3 |
| R4 | Heading nhiều dòng, vào ra riêng | Dòng (4) | vào [0; −0,5 em], ra [0; +0,5 em] | 0,5 em | R4 |
| R5 | Body, mục danh sách | Dòng (4) | [2,0 em; 0] (từ phải) | 1,0 em | R5 |
| R6 | Cả khối chữ thoát | Không dùng animator: Scale của layer Title ở cấp Scene | 100 → 86 → 0 | | R6A, R6B |
| R10 | Mở khung, bảng | Không dùng animator: Size của khối matte từ 0 tới đủ | | | MASK |

- Mọi công thức chữ có Opacity 0 trên animator.
- Position của animator là `ADBE Text Position 3D`: nhập 3 số [x; y; 0]. Bảng ghi x; y. Blur nhập 2 số bằng nhau [b; b]. Bảng ghi b.
- R4 cần 2 animator: một animator vào (Start 0→100), một animator ra (End 0→100).
- Thời lượng mặc định: vào 30 khung, ra 30 khung. Ca mẫu: R6 thu 12 khung rồi 9 khung; R10 mở trong 28 khung.
- Gọi trong ca mẫu: `O.textAnim(layer, 'R1', {em: 126, inAt: 4, inDur: 30, outAt: 122, outDur: 28})`.
- Nhịp của template:
  - chữ chính vào trước, nhãn phụ vào trễ 28 khung (0,93 s);
  - hai nhóm rút ra cùng lúc;
  - nhờ vậy có thứ bậc khi vào và gom nhóm khi ra.

### 6.3 Đặt chữ theo hộp đo

- `layer.sourceRectAtTime(t, false)` trả {left, top, width, height} của phần chữ thật.
- Đặt mép trên-trái khối chữ tại (x, top): position = [x − left, top − rect.top] (`O.placeTop`).
- Co chữ cho vừa bề rộng, nhưng không nhỏ hơn 28 px (`O.fitWidth`).
- Khối nền, bong bóng giãn theo chữ: expression đọc `sourceRectAtTime` của layer chữ. Ví dụ: nút CTA của ca mẫu rộng 742 px theo URL.
- Text layer có anchor [0,0] gắn với baseline. Đó là bình thường, không phải lỗi.

### 6.4 Font

- Đặt font bằng tên PostScript, ví dụ `td.font = 'BeVietnamPro-ExtraBold'`.
- Sau `setValue(td)` thì đọc lại để kiểm:
  - `td.font` phải bằng tên đã đặt;
  - `td.fontObject.isSubstitute` phải là false;
  - toàn project: `app.fonts.missingOrSubstitutedFonts` phải rỗng.
- Chế độ headless không hiện hộp thoại báo thiếu font. Phải tự kiểm và ghi vào báo cáo.
- Cài font mới cho AE thấy:
  1. Chép file font vào `%LOCALAPPDATA%\Microsoft\Windows\Fonts` và ghi khóa HKCU `...\CurrentVersion\Fonts`, để font còn sau khi khởi động lại. Riêng bước này thì AE chưa thấy.
  2. Gọi `AddFontResourceW` và phát `WM_FONTCHANGE`:

```powershell
Add-Type @"
using System; using System.Runtime.InteropServices;
public class FontReg {
 [DllImport("gdi32.dll", CharSet=CharSet.Unicode)] public static extern int AddFontResourceW(string file);
 [DllImport("user32.dll", SetLastError=true)] public static extern IntPtr SendMessageTimeout(IntPtr h, uint msg, IntPtr w, IntPtr l, uint flags, uint timeout, out IntPtr res);
}
"@
$file = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Fonts\<Font>.ttf'
[FontReg]::AddFontResourceW($file)
$res = [IntPtr]::Zero
[void][FontReg]::SendMessageTimeout([IntPtr]0xffff, 0x001D, [IntPtr]::Zero, [IntPtr]::Zero, 0x0002, 3000, [ref]$res)
```

  3. Mở phiên AE mới, vì AE quét font lúc khởi động.
- Font biến thiên (variable font, chỉ có trục wght): AE cần file tĩnh. Cố định giá trị wght rồi ghép đủ bộ Latin và tiếng Việt. Ví dụ: `<VD-A>\tools\build_accent_font.py` làm Fraunces wght 800.
- Font của bộ OPA: Be Vietnam Pro (ExtraBold, SemiBold, Bold, Medium) và `<VD-A>\assets\fonts\FrauncesOPA-ExtraBoldItalic.ttf` (OFL).

### 6.5 Luật chữ của Minh

- Viết hoa chữ cái đầu mọi dòng hiển thị, kể cả mục danh sách. Dòng mở đầu bằng số thì viết hoa chữ cái đầu tiên sau số. Tên file và URL giữ chữ thường.
- Cỡ chữ nhỏ nhất 28 px (khung cao 1080). Ở khung 4K (cao 2160) là 56 px. Tính theo cỡ hiệu dụng: cỡ font × tích scale của các tầng cha. Ví dụ font 300 trong Title scale 75 % là 225 px.
- Cụm nhấn: dùng font khác thân bài, kèm hiệu ứng có nghĩa. Cách làm ở video OPA:
  - font Fraunces Italic 800;
  - khối đánh dấu quét từ trái trong 8 khung: đệm trái 0,12 em, đệm phải 0,22 em, cao 1,26 em;
  - chữ nằm trên khối là bản sao + effect Fill + track matte theo khối (`O.accentBlock`).
- Mục song song: cùng font, cùng cỡ, cùng công thức, cùng âm.
- Chữ lấy đúng kịch bản khóa. Không đoán tên riêng, số liệu, CTA.
- Soát tự động: `python -I tools/qa_chu.py` (đọc `textDump` trong báo cáo dựng).

### 6.6 Thay chữ trong template

- **Giữ tên layer.** Nhiều template dùng tên layer chữ trong expression, ví dụ để đo `sourceRectAtTime()` cho hộp nền. Layer chưa đặt tên riêng thì AE lấy chính nội dung chữ làm tên, nên đổi chữ là đổi luôn tên và gãy expression. Cách làm:
  1. lưu `var origName = layer.name;`;
  2. gán chữ mới bằng `setValue(textDocument)`;
  3. trả lại `layer.name = origName;`.
- **Câu tiếng Việt dài hơn câu mẫu.** Câu tiếng Việt thường nhiều từ hơn câu tiếng Anh gốc. Ca mẫu B thấy Text Animator theo từ dừng khi chưa hiện hết, chữ cuối còn mờ; nguyên nhân cụ thể chưa ghi lại. Cách ca mẫu B sửa (`fixTextAnimator` trong `<VD-B>\customize_template_assets.jsx`):
  - đặt `ADBE Text Levels Max Ease` = 0;
  - đặt lại 2 key của `ADBE Text Percent Start`: 0 % → 100 % trong 0,20–1,05 s (thẻ lật nhanh: 0–0,45 s). Đây là giây cục bộ của comp chữ.
- Hàm đó xóa mọi key Start của mọi animator và không đặt ease, nên mất luôn pha ra và đường ease của template. Làm đúng hơn:
  - chỉ đặt lại 2 key pha vào của animator vào;
  - giữ nguyên pha ra;
  - đặt ease theo vai trò (mục 5.2).
- Sau khi thay: đo `sourceRectAtTime` để chắc chữ không tràn khung, rồi chạy soát chữ.

## 7. Hình: shape, matte, parent, expression, máy quay, nhân vật, giao diện

### 7.1 Shape layer

- AE vẽ nhóm **đứng đầu danh sách lên trên cùng**. Muốn phần tử đầu mảng nằm dưới thì thêm nhóm theo thứ tự ngược (`O.shape`).
- Trong một layer, tên các nhóm phải khác nhau, vì hàm tìm nhóm theo tên.
- matchName hay dùng:
  - `ADBE Root Vectors Group` › `ADBE Vector Group` › `ADBE Vectors Group`;
  - hình chữ nhật: `ADBE Vector Shape - Rect` (`ADBE Vector Rect Size`, `ADBE Vector Rect Roundness`);
  - elip: `ADBE Vector Shape - Ellipse`; đường path: `ADBE Vector Shape - Group`;
  - tô và viền: `ADBE Vector Graphic - Fill`, `ADBE Vector Graphic - Stroke`;
  - vẽ nét dần: `ADBE Vector Filter - Trim`;
  - transform của nhóm: `ADBE Vector Transform Group`.
- Path trong AE gồm đỉnh và tiếp tuyến tương đối (vertices, inTangents, outTangents).
- Đổi SVG sang path AE: `<VD-A>\tools\svg_to_ae.py`. Cung A được đổi sang Bézier, mỗi đoạn ≤ 90°, sai số dưới 0,03 px.

### 7.2 Track matte, mask

- Gắn matte: `layer.setTrackMatte(matteLayer, TrackMatteType.ALPHA)`.
- Matte chỉ làm khuôn thì đặt `matte.enabled = false`. Matte vừa làm khuôn vừa phải hiện, như khối nhấn, thì để `enabled = true`.
- Mở khung kiểu R10: animate Size của khối matte từ 0 tới đủ với ease MASK. Thêm một viền chạy theo mép khối, để không lộ lỗ trống.
- Mask chữ nhật trên layer: `ADBE Mask Parade` › `ADBE Mask Atom` › `ADBE Mask Shape` (`O.rectMask`).

### 7.3 Parent

- Parent truyền vị trí, tỉ lệ, góc xoay. **Parent không truyền opacity.** Con cần mờ theo cha thì gắn expression `thisComp.layer("Cha").transform.opacity` (`O.followOpacity`).
- Position của layer có parent là toạ độ cục bộ. Muốn toạ độ thật trên khung thì dùng `toComp()` trong expression.

### 7.4 Expression hay dùng

- Engine là `javascript-1.0`.
- Thở (co giãn nhẹ, 100–103 % như Bò OPA): `var s = 100 + 1.5 * (1 - Math.cos(time * 2 * Math.PI * 0.5)); [s, s]`.
- Lắc nhẹ: `Math.sin(time * 2 * Math.PI * 0.9) * 2`.
- Con trỏ gõ chữ nhấp nháy: `Math.floor(time * 30 / 8) % 2 ? 0 : 100`.
- Kích thước theo chữ: đọc `comp("TXT_…").layer("TEXT").sourceRectAtTime(t, false)`.
- Sau khi dựng, buộc tính mọi expression bằng `valueAtTime`, rồi gom `expressionError` vào báo cáo. Ca mẫu A: 388 expression, 0 lỗi.
- Template mua về có thể có sẵn expression lỗi, ví dụ gọi một thuộc tính không tồn tại. Đừng chép lỗi đó sang bản mới.

### 7.5 Máy quay ảo, motion blur

- Mỗi cảnh có một null `CAM`. Mọi layer chính gắn parent vào CAM.
- CAM trôi Scale và Position một đường chậm, đều suốt cảnh. Ví dụ cảnh 5: 100 → 106 % trong 6 s, ease LINEAR.
- Motion blur phải bật ở hai chỗ: comp (`comp.motionBlur = true`) và layer (`layer.motionBlur = true`). Chỉ bật cho layer chuyển động nhanh.
- Blur trong công thức chữ là Text Animator Blur, khác motion blur.

### 7.6 Effect: số thô khác số trên giao diện

Script đọc số thô, không phải con số hiện trong bảng Effect Controls:

| Thuộc tính | Số thô | Trên giao diện |
|---|---|---|
| Drop Shadow Opacity | 76,5 (thang 0–255) | 30 % |
| Glow Threshold | 153 (thang 0–255) | 60 % |
| Fill Opacity | 1 (thang 0–1) | 100 % |

- Đọc `unitsText`, `minValue`, `maxValue` trước khi chép số.
- Kiểm effect hoặc layer style có đang bật không (`enabled`, `active`). API vẫn đọc được giá trị của style đang tắt.

### 7.7 Mẫu: con trỏ bấm nút (cảnh 5 ca mẫu A)

Khung ở đây là khung cục bộ của comp `TITLE_S5`. Cộng 900 ra khung master.

| Vật | Thuộc tính | Key |
|---|---|---|
| Con trỏ | Position | f92 ngoài khung [1880; 1040] → f122 tới điểm bấm (BRAND) → f128 lún thêm [−4; +4] px (SOFT) → f136 về điểm bấm (SOFT) |
| Con trỏ | Opacity | f92 = 0 → f96 = 100 (LINEAR) |
| Nút | Scale | f124 = 100 → f128 = 94 (BRAND) → f136 = 100 (BRAND) |
| Gợn bấm | Scale | f126 = 100 → f150 = [118; 150] (BRAND) |
| Gợn bấm | Opacity | f124 = 0 → f126 = 90 (LINEAR) → f150 = 0 (EXIT) |
| Nút thở | Scale, expression | từ f140: `var t = time - 140 / 30; var k = t > 0 ? 2.5 * Math.sin(t * 2 * Math.PI / 1.2) : 0; [value[0] + k, value[1] + k]` |

- Điểm bấm đặt ngay sau chữ URL, để con trỏ không che chữ.
- Âm: lớp press + lớp click có đỉnh ở f125, lúc nút vừa lún; tiếng release có đỉnh ở f130.
- Bật motion blur cho con trỏ.

### 7.8 Nhân vật, mascot tách bộ phận

Kỹ thuật rig (tách bộ phận để diễn trong AE), học từ dự án Motion Omi:
- Bộ tấm thiết kế nhân vật:
  - CS01: xoay 4 góc;
  - CS02: biểu cảm;
  - CS03: tách bộ phận trên nền phẳng để cắt PNG, SVG;
  - CS04: tư thế hành động;
  - CS05: bản đồ tâm xoay.
- Đặt anchor đúng chỗ khớp:
  - thân: anchor ở chân đế, để nhún nảy mà chân vẫn bám sàn;
  - sừng, tay: parent vào thân, anchor ở gốc khớp, để xoay không rời khớp;
  - bong bóng chat: anchor ở đuôi nhọn, để bung ra từ người gửi.

**Bò OPA theo `<OPA>\BRAND-SPEC.md`:**
- không mắt, miệng, tay chân; chỉ 5 màu;
- không bóp méo: chỉ co giãn đều mọi trục, nên không squash & stretch kiểu [108; 92] → [95; 106].

Bản mascot của Motion Omi có mắt LED, sừng tia sét vàng #FFD400, thân nam châm chữ U. Bản này trái các luật trên, và chưa có ghi nhận Minh duyệt. Chỉ dùng khi brief nêu rõ, hoặc Minh duyệt.

### 7.9 Đưa giao diện UI vào AE

- Ảnh UI sinh bằng AI dùng prompt 7 phần: loại màn hình + ngành hàng + danh sách thành phần + mã màu + font + phong cách + "4K UI mockup". Bản đầy đủ (cấu trúc 7 phần, prompt mẫu, bảng màu ngành hàng, lệnh xuất SVG tách lớp và bộ tấm nhân vật `CS01..CS05`) nằm ngay trong gói tại `<SKILL>\references\sketch-to-ui-va-nhan-vat.md`.
- Ba cách đưa vào AE:
  1. **Phác thảo hóa thật:** bản vẽ tay ở dưới, bản UI thật ở trên, quét bằng Linear Wipe hoặc mask.
  2. **Màn hình nghiêng có chiều sâu:** bật 3D Layer, nghiêng màn hình, đẩy các thẻ nổi lên trục Z −20 … −50 px để máy quay lia qua thấy chiều sâu.
  3. **SVG → Illustrator → AE:** SVG chia nhóm `<g id>` → Illustrator "Release to Layers" → lưu .ai → nhập vào AE kiểu "Composition - Retain Layer Sizes", để diễn từng thẻ riêng.
- Video OPA theo BRAND-SPEC: nền phẳng, 5 màu; không gradient, glow, bóng đổ, 3D bóng loáng (phim 3D trong `film3d/` là ngoại lệ riêng).
  - 5 màu OPA: xanh #0068FF, xanh đêm #003C99, xanh nhạt #E6F0FF, đen #0A0A0A, trắng #FFFFFF.
  - Đỏ cảnh báo #E5484D chỉ dùng cho dấu cảnh báo nhỏ.
  - Turbulent Displace và Glow ở cách 1, lớp 3D ở cách 2, bảng màu #0A2540 / #0052FF / #00E5FF / #FFD400 của ca Motion Omi chỉ dùng cho video không theo BRAND-SPEC OPA, hoặc khi Minh duyệt.
- Template có sẵn glow, kính mờ, gradient, 3D mà video là của OPA: mặc định làm phẳng theo BRAND-SPEC. Muốn giữ hiệu ứng của template thì Minh quyết ở G0.

### 7.10 Ảnh, logo, nút có chữ

- Nhập ảnh, logo PNG: `var it = app.project.importFile(new ImportOptions(new File(path)));` → `var L = comp.layers.add(it);` → đặt bằng `O.setT`. Ảnh nhập xong cho vào thư mục `04_HINH` (`it.parentFolder`).
- Logo là vật, không phải chữ. Cho vào bằng Scale và Opacity với ease BRAND, hoặc lò xo (mục 5.4). Logo khách giữ đúng tỉ lệ, không bóp méo.
- Nút có chữ (ca mẫu A, cảnh 5):
  1. nút là shape, bật lò xo ở khung f66;
  2. chữ trên nút là layer chữ riêng trong comp `TXT_…`, vào bằng R3 từ khung f72, tức sau khi nút đã bật;
  3. đặt layer chữ nằm trên nút (`moveBefore`);
  4. nút rộng theo chữ: đo `sourceRectAtTime` của chữ rồi tính bề rộng nút.
- Lò xo áp cho nút, không áp cho chữ trên nút.

## 8. Chuyển động và nhịp (gu của Minh)

- Mặc định: mượt, giàu chuyển động, chuyên nghiệp. Hai lời chê đã có:
  - V2 bản đầu "nhàm": 70 % khung gần như đứng yên;
  - phim 3D bản 1 "lúc nhanh lúc chậm".
- Nhịp phải đều:
  - máy quay trôi một đường chậm suốt cảnh;
  - hành động rơi đúng phách nhạc (120 BPM: mỗi phách 0,5 s = 15 khung ở 30 fps);
  - không lia máy gấp.
- Chuyển cảnh không cắt cứng. Một vật nở ra phủ kín khung đúng ở khung cuối cảnh trước; cảnh sau tan ra từ đó trong khoảng 10 khung. Ví dụ ca mẫu A:
  - nối 1→2: tin nhắn trắng nở ra;
  - nối 2→3: đĩa sáng nở đều trong 11 khung;
  - nối 4→5: khung xanh nở ra.
- So le đều: các mục song song cách nhau đều nhau (ca mẫu A: 28 khung).
- Chữ chạy suốt phim, mỗi nhịp một câu, đủ thời gian đọc.
- Đo bằng `python -X utf8 "<SKILL>/scripts/v2w/metrics.py" <mp4> --no-flow`. Đạt khi:
  - mỗi ô 2 s có ≤ 15 % khung gần đứng yên (Tĩnh B);
  - Tĩnh A = 0;
  - 0 cắt cứng.
  Đoạn giữ logo sau khi logo đã hiện xong được miễn đo (`--exempt`, Minh chốt 24/10).
- Video OPA theo BRAND-SPEC: 5 màu, nền phẳng; không gradient, glow, bóng đổ, 3D bóng loáng; mascot đúng hình. Góp ý "tiết chế" của agent không phải luật.

## 9. Âm thanh

### 9.1 Thang mức trong bản trộn (trước master)

| Lớp | Mức | Căn cứ |
|---|---|---|
| Giọng đọc | −16,3 LUFS. SFX và nhạc cộng thêm khoảng 0,3 LU, nên cả bản ra −16 | chuẩn của Minh; AES TD1008 (lời −18, nhạc −16) |
| Nhạc nền (có giọng) | −31 LUFS tích hợp, tức 15 LU dưới giọng (±1); LRA ≤ 5 LU | quy trình nền 1.2.3 Minh duyệt |
| SFX chuyển cảnh, logo | M −24,5 … −27 | đặt vào khoảng nghỉ giữa các câu |
| SFX sự kiện giao diện | M −27 … −33 | nhô trên nhạc tại chỗ 0–4 LU |
| Tiếng nhỏ (đồng hồ, gõ phím, click) | M −33 … −38; lớp tách của cú bấm xuống tới −46 khi trùng lời | âm ngắn và sáng nên vẫn nghe rõ dù M thấp |
| Mọi SFX lúc đang nói | thấp hơn giọng ≥ 8 LU | |
| Mỗi cue | đỉnh thật ≤ −12 dBTP, tính cả âm chồng cùng khung | âm trùng đỉnh giọng sẽ đẩy bản trộn quá trần (bài học B8) |
| Cả bản ngắn | độ to ngắn hạn lớn nhất ≤ tích hợp + 5 LU | EBU R 128 s1 |

- M đích là độ to tức thời lớn nhất (cửa sổ 400 ms) của riêng cue đó khi phát trong bản trộn.
- Mức cú bấm ở ca mẫu A (M đích):

| Lớp | Cảnh 2, trùng lời | CTA, trong khoảng nghỉ |
|---|---|---|
| Thân (press) | −29,5 | −28,5 |
| Tách (click) | −46 | −29; trần đỉnh giữ lại còn −41 |
| Nhả (release) | −32,5 | −31,5 |

- WCAG 1.4.7 (nền dưới lời ≥ 20 dB) là mức AAA cho người nghe kém, chỉ để tham khảo. Chuẩn Minh duyệt: nhạc 15 LU dưới giọng; lúc đang nói, giọng cao hơn nền ≥ 10 LU.
- EBU R 128 s1 cho phép đỉnh thật −1 dBTP. Chuẩn của Minh chặt hơn: file giao ≤ −2 dBTP. Bảng mức trong `<VD-A>\audio\BANG-CUE-AM-THANH.md` ghi tiếng giao diện −27 … −31; thực tế ca mẫu A dùng tới −33.
- Video không có giọng đọc: xem mục 9.10.

Đường link nguồn web nằm trong `<VD-A>\audio\BANG-CUE-AM-THANH.md`. Bản nghiên cứu đầy đủ: `<SKILL>\references\nghien-cuu-decibel.md`.

### 9.2 Đo cho đúng

- Độ to tính theo ITU-R BS.1770-4:
  - lọc K ở 48 kHz;
  - M dùng cửa sổ 400 ms;
  - I có cổng −70 LUFS và −10 LU;
  - đỉnh thật lấy mẫu ×4.
- **File mono:** AE phát ra cả 2 kênh với nguyên mức (L = R = file × gain). Vì vậy nghe to hơn số đo trên file mono 3 LU.
  - Đo đúng: nhân đôi kênh nguyên mức, bằng numpy `repeat` hoặc ffmpeg `pan=stereo|c0=c0|c1=c0`.
  - Không dùng `-ac 2` hay `aformat` của ffmpeg: chúng chia −3 dB mỗi kênh. Ca mẫu A từng vì vậy làm nhạc to hơn đích 3 LU.
- Âm ngắn hơn 400 ms: đệm im lặng tới 400 ms rồi mới đo M. Click, tick đo thêm trong dải tần ở cửa sổ ngắn, vì thước 400 ms đánh giá thấp chúng.
- Công cụ: `python -I tools/phan_tich_sfx.py "<kho>" out.csv` (có trong `<VD-A>\tools`). Các cột: dur, eff, onset, **peak_s**, peak_dbfs, tp_dbtp, m_max, i_lufs, centroid.
- Kho SFX của Minh đã đo sẵn: `<SKILL>\data\kho_sfx_do.csv` (2.982 file, đo ngày 22/10 sau khi sửa cách đọc file mono).
  - CSV chỉ dùng để chọn âm. Gain luôn được tính lại trên file WAV đã chép, trong `am_thanh_cues.py`.

### 9.3 Chọn SFX

- Kho: `<SFX>` (CC0, MIT), chia 7 nhóm theo chuyển động, cộng thư mục packs (`uisfx-themes` 12 chủ đề, Kenney, Remotion).
- Không dùng theSOUNDS. Kho không có nhạc nền dài.
- Chọn theo chuyển động:

| Chuyển động | Loại âm |
|---|---|
| Vật bật lò xo | pop, bounce |
| Icon bật | tick, marimba |
| Vật bay, chuyển cảnh | whoosh |
| Dẫn vào cao trào | swell, riser |
| Va chạm | thump |
| Cú bấm | press + click + release |
| Logo | sonic logo |

- Chọn bộ âm theo gu của video:
  - explainer vui, nhân vật (ca mẫu A): pop có nốt, marimba, tick. Minh đã duyệt bộ này ở v09;
  - quảng cáo SaaS, công nghệ sang (ca mẫu B): `packs/uisfx-themes/{studio, glass, minimal, scifi, soft, cinematic, zen}`, âm ấm, gọn; tránh âm hoạt hình, còi chói, whoosh nhiễu gắt;
  - video có cả nhân vật lẫn giao diện: chọn theo từng khoảnh khắc. Nhân vật nảy, bật dùng pop, bounce; thao tác giao diện dùng bộ uisfx. Mỗi loại khoảnh khắc giữ một họ âm. Gu cuối cùng do Minh chốt khi nghe đoạn mẫu.
- Âm có nốt phải hợp giọng của nhạc (ca mẫu A ở La trưởng). Đo cao độ bằng `python -X utf8 "<SKILL>/scripts/cao_do.py" <file1> <file2> …` (in 3–4 đỉnh phổ mạnh nhất kèm tên nốt). Lệch thì dịch bằng `aresample=48000,asetrate=48000*2^(c/1200),aresample=48000`. Âm sẽ ngắn lại theo cùng tỉ lệ. Ca mẫu A đã dịch success +200 cent, glass expand và collapse +155 cent.
- Mục song song dùng cùng âm, cùng mức. Một âm lặp lại nhiều lần (tin nhắn mới) thì lấy cách một, để hai lần cách nhau ≥ 0,5 s.
- Không đặt hai âm gần giống nhau cách nhau dưới 3 khung: tai nghe thành tiếng đúp.
- Chép sang WAV 48 kHz trước khi đưa vào AE. AE không đọc OGG; MP3 bị lệch giờ do độ trễ của bộ mã.
  - `am_thanh_cues.py` tự đổi cả SFX lẫn giọng.
  - Đổi tay: `ffmpeg -y -i vao.mp3 -ar 48000 -c:a pcm_s24le ra.wav`.
  - Tùy chọn cho tiếng UI êm hơn (ca mẫu B): thêm `lowpass=f=11000`. Lọc này đổi chất âm, nên nghe thử trước khi áp cả bộ.

### 9.4 Đặt SFX theo chuyển động

- **Căn đỉnh âm, không căn đầu file:** `layer.startTime = khung_hình / fps − peak_s`. peak_s là số giây từ đầu file tới lúc biên độ lớn nhất.
  - SFX đặt trong comp cảnh (nhánh B): `layer.startTime = (giây_toàn_cục − giây_bắt_đầu_cảnh) − peak_s`.
- Đỉnh rơi đúng khung chạm, hoặc khung vật chuyển động nhanh nhất. Không bao giờ sớm hơn hình; trễ tới 1 khung thì chấp nhận được.
- Whoosh chuyển cảnh: đỉnh ngay trước điểm cắt khoảng 1 khung, lúc vật nở nhanh nhất.
- Cú bấm gồm 2 lớp cùng khung (thân press + tách click), cộng tiếng nhả sau 4–5 khung.
- Gain = M đích − M đo được của file. Sau đó hạ thêm nếu đỉnh thật vượt −12 dBTP.
- Dựng lại stem SFX để đo đỉnh trong ±40 ms quanh mỗi cue, tính cả âm chồng. Nhóm cue nào vượt trần thì hạ cả nhóm.
- Ghi lại các chuyển động cố ý không gắn âm, kèm lý do. Ví dụ: chữ vào ra đã có lời đọc lo; chuyển động nền chạy liên tục.
- Công cụ của ca mẫu A: `<VD-A>\tools\am_thanh_cues.py`.
  - Sinh `build/data/am_thanh_cues.jsxinc`, mỗi cue gồm file, khung đỉnh, gain, tên layer.
  - Sinh bảng đọc được `audio/BANG-CUE-AM-THANH.md`.
- **Chống phát đúp:** ca mẫu B đặt SFX ở hai nơi: comp SFX riêng (`00_OPA_SFX_Master`) và trong từng comp cảnh. Khi đó, trong comp chính để render (`Final_4k`, `Full_HD`), đặt `audioEnabled = false` cho các layer cảnh. Không làm vậy thì mỗi tiếng phát hai lần, to thêm 6 dB.
  - Nếu nhạc hay âm nào khác nằm trong comp cảnh, tắt âm layer cảnh sẽ tắt luôn chúng. Khi đó chuyển nhạc ra comp SFX riêng, hoặc bỏ bản SFX trong comp cảnh.
  - Cách gọn nhất: mỗi tiếng chỉ đặt ở một nơi.

### 9.5 Khi có giọng đọc

- Dùng nguyên file Minh gửi. Chép sang WAV 48 kHz 24-bit, đặt gain để giọng ở −16,3 LUFS khi phát.
- Đặt marker cho từng câu theo chỗ năng lượng tăng lại sau khoảng nghỉ.
- Chữ lấy từ kịch bản; whisper chỉ dùng để căn giờ. Mốc từ của whisper thường sớm 0,1–0,4 s.
- Câu đọc dài hơn cảnh: cho lời vào trước hình (J-cut), không cắt câu.
- SFX trong lúc đang nói:
  - âm nhiều năng lượng ở 2–8 kHz (swish, whoosh, riser, giấy): đặt vào khoảng nghỉ, đỉnh sớm hơn đầu từ kế tiếp ≥ 0,07 s, hoặc bỏ;
  - kiểm che phụ âm: lọc dải 2–8 kHz, RMS 10 ms, xét **cả cửa sổ quanh cue**. SFX phải thấp hơn phụ âm ≥ 8 dB;
  - ví dụ ca mẫu A: tiếng chip to hơn phụ âm 15,5 dB (cần sửa: bỏ); lớp tách chỉ thấp hơn 3,6 dB (nên sửa: hạ 6 dB);
  - nếu chỉ xét giọng tại khung đỉnh thì sẽ bỏ sót đuôi âm chạy vào âm tiết sau;
  - whisper không nhạy với lỗi này (độ tin cậy vẫn 1,0), nên phải đo bằng dải tần.
- Đo che phụ âm bằng code dưới đây. Stem SFX dựng lại bằng `am_thanh_cues.sfx_stem(rows, peaks)` từ `build/data/am_thanh_cues.jsxinc`; giọng là file WAV nhân gain.

```python
# v = giọng (đã nhân gain), s = stem SFX: cùng 48 kHz, mảng numpy (n, 2); t = giây của cue
import numpy as np
from scipy.signal import butter, sosfilt

def band_db(x, sr=48000, w=480):  # dải 2–8 kHz, RMS 10 ms, ra dB
    y = sosfilt(butter(4, [2000, 8000], btype="bandpass", fs=sr, output="sos"), x, axis=0)
    n = len(y) // w
    return 10 * np.log10((y[:n * w] ** 2).reshape(n, w, -1).mean(axis=(1, 2)) + 1e-20)

bv, bs = band_db(v), band_db(s)
i, j = int((t - 0.10) * 100), int((t + 0.15) * 100)  # cửa sổ quanh cue
act = bv[i:j] > bv[i:j].max() - 20                   # khung giọng đang có phụ âm
print("SFX trừ giọng:", (bs[i:j][act] - bv[i:j][act]).max(), "dB")  # đạt khi ≤ −8
```

- Nhạc dưới giọng: lúc đang nói, giọng cao hơn nhạc + SFX ≥ 10 LU, đo theo cửa sổ 3 s. Ca mẫu A thấp nhất 11,7 LU.
- Dìm nhạc (duck) chỉ khi đo thấy cần. Ca mẫu A đã thử dìm −4 dB, không đổi gì nên bỏ.
- Kiểm rõ lời: chạy whisper trên bản trộn rồi so với giọng riêng. Ca mẫu A khớp 99,3 %.
- Kiểm đồng bộ: tương quan chéo giọng gốc với bản xuất.
- AAC của AE trễ đều khoảng 21 ms (1024 mẫu, 0,64 khung ở 30 fps). Mức này dưới ngưỡng nghe ra lệch, không cần bù.

### 9.6 Nhạc nền

- Video OPA: không dùng nhạc có bản quyền mà tự tổng hợp. Ca mẫu A dùng `<OPA>\tools\audio\score_agent.py`:
  - 36 s, 120 BPM, La trưởng, chia theo 5 cảnh;
  - mỗi cảnh có phách 1 riêng, để cú "đáp" rơi đúng mốc cảnh;
  - dựng lại ra đúng từng bit.
- Xử lý nền:
  - lọc bỏ dưới 100 Hz, giảm 3 dB ở 2 kHz;
  - vào dần 1 s, tắt dần 1,5 s;
  - LRA ≤ 5 LU;
  - mức tuyệt đối đặt bằng gain của layer trong AE.
- Để một khoảng lặng ngắn trước cú đáp cho SFX swell, whoosh, logo lấp vào. Ca mẫu A: 13,1–13,5 s và 29,93–30,4 s.
- Video không phải OPA: chỉ dùng nhạc có quyền dùng, do khách hoặc Minh đưa (có giấy phép). Chưa có thì hỏi Minh. Kho mặc định trên máy Minh nằm ở mục A.8 của `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/AI Video/prompts/MASTER_VIDEO_EDITOR_VI.md`.
- File nhạc gốc (hoặc nhạc đã duyệt) giữ nguyên, kiểm bằng MD5. Mọi xử lý làm trên một file WAV dẫn xuất, rồi đưa file đó vào `assets/music/` cho AE:

```bash
# cắt đúng thời lượng video (ví dụ 10 s), vào dần 1 s, tắt dần 1,5 s, lọc dưới 100 Hz, WAV 48 kHz
ffmpeg -y -i nhac-goc.mp3 -t 10 -af "highpass=f=100,afade=t=in:d=1,afade=t=out:st=8.5:d=1.5" -ar 48000 -c:a pcm_s24le assets/music/nhac-nen.wav
# có giọng đọc thì thêm vào chuỗi lọc: equalizer=f=2000:t=q:w=1:g=-3 (giảm 3 dB ở 2 kHz cho lời rõ)
```

- Cắt nhạc ở chỗ hết câu nhạc thì nghe tự nhiên hơn cắt giữa câu. Nghe thử điểm cắt trước khi chốt.

### 9.7 Đưa âm vào AE

- Dựng một comp âm riêng (ca mẫu A: `AM_THANH_SFX_NHAC`; ca mẫu B: `00_OPA_SFX_Master`). Thêm nhạc trước để nằm dưới cùng, rồi tới các SFX. Đặt comp này vào master.
- Mức của layer: `layer.property('ADBE Audio Group').property('ADBE Audio Levels').setValue([dB, dB])`.
- Giọng đọc là một layer riêng trong master, bắt đầu từ 0 s.
- Ghi marker tại giây của mỗi cue để người mở project tìm nhanh.

### 9.8 Master file giao

```bash
python -X utf8 "<SKILL>/scripts/master.py" out/review/_lam/bNN_709.mp4 out/review/<TEN>_vNN.mp4 --I -16.1 --TP -2.5 --voice assets/voice/<giong>.wav
```

- Công cụ chạy loudnorm hai lượt và **chỉ nhận chế độ tuyến tính** (không nén).
  - Không đạt vì đỉnh quá cao: công cụ in 8 điểm đỉnh thật cao nhất rồi thoát mã 2 mà không ghi file.
  - Khi đó hạ SFX hoặc nhạc ở các điểm ấy rồi dựng lại. Không để loudnorm tự nén.
- Đích −16,1, vì AAC làm lệch khoảng +0,1; file giao sẽ đo ra −16,0. TP đặt −2,5 để sau AAC vẫn ≤ −2 dBTP.
- Số của ca mẫu A: −16,0 LUFS, −3,5 dBTP, LRA 1,2 LU.
- Hình chép nguyên (`-c:v copy`), nên thẻ BT.709 vẫn còn. Âm mã hóa AAC 256k, 48 kHz.
- `--voice` là file giọng riêng (tùy chọn). Khi không đạt tuyến tính, công cụ in thêm đỉnh của giọng ở cùng cửa sổ, để biết đỉnh đến từ SFX, nhạc hay từ giọng. Video không giọng thì bỏ tham số này.
- Bản −14 LUFS để đăng mạng xã hội: chỉ làm khi Minh yêu cầu. Minh đã chốt bản này cho phim 3D; với video AE thì hỏi lại.

### 9.9 Lệnh âm (ca mẫu A)

```bash
cd "<thư mục dự án AE>"
python -X utf8 -I tools/am_thanh_cues.py "/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx" "/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/VOICE/<giong>.MP3"
#   tự chép SFX và giọng sang WAV 48 kHz, tính gain, sinh cue cho AE và bảng cue
python -I tools/ae.py build                                        # đưa cue mới vào project
ffmpeg -v info -i <mp4> -map 0:a -af ebur128=peak=true -f null -   # I, LRA, đỉnh thật
ffmpeg -y -i <mp4> -vn -ac 1 -ar 16000 giong16k.wav
PYTHONIOENCODING=utf-8 python "<SKILL>/scripts/transcribe.py" giong16k.wav whisper.json
```

Lệnh trích âm cho whisper dùng `-ac 1` cũng được, vì whisper không cần mức chuẩn.

### 9.10 Video không có giọng đọc (nhạc dẫn, thường gặp ở nhánh B)

- Không có chuẩn có nguồn cho số dB giữa nhạc và SFX (`<SKILL>\references\nghien-cuu-decibel.md` mục 3). Nhạc và các SFX chủ chốt cùng là lớp tiền cảnh.
- **Mức nhạc** (đề xuất, chưa đo trên ca thật nào): nhạc là lớp chính. Đặt nhạc khoảng −17 LUFS tích hợp trong bản trộn, để cả bản (nhạc + SFX) gần −16 trước master. Nhờ vậy master chỉ nâng hạ dưới 1–2 dB và trần đỉnh mỗi cue vẫn giữ được.
  - Đừng giữ −31 LUFS của video có giọng: master sẽ phải nâng khoảng 15 dB, đỉnh vượt trần và `master.py` dừng.
  - Trong `am_thanh_cues.py`, đổi hằng `MUSIC_LUFS` từ −31 sang khoảng −17.
- **So từng cú, không so cả bài:**
  - đo M (400 ms) của cue so với M của nhạc ngay tại chỗ, hoặc RMS trong dải tần của tiếng;
  - cột "Nhô" mà `am_thanh_cues.py` ghi vào bảng cue chính là số này;
  - tiếng giao diện nhỏ nhô 0–4 LU;
  - tiếng chủ chốt (mở màn, chốt đơn, logo, CTA) nhô +4 … +10 LU, tốt nhất đặt vào chỗ nhạc lặng hoặc cú đáp;
  - vẫn giữ trần đỉnh thật −12 dBTP mỗi cue (master nâng thêm X dB thì trần trước master là −12 − X).
- Không có lời đọc lo phần chữ, nên chữ chính vào có thể gắn tiếng nhẹ (tick, swish nhỏ) cho nhịp rõ. Mục song song dùng cùng âm. Có giọng thì thường bỏ.
- Số đặt của ca mẫu B (chưa đo trên bản xuất; dùng làm điểm xuất phát rồi đo):
  - file SFX hạ −4,5 dB trước (`volume=-4.5dB`), lọc `lowpass=f=11000`;
  - gain layer theo nhóm:

| Nhóm chuyển động | Ví dụ âm (uisfx-themes) | Gain layer |
|---|---|---|
| Điểm nhấn mở màn, chốt đơn, CTA | `cinematic/wake`, `glass/checkout`, `cinematic/complete` | −6 … −6,5 dB |
| Chuyển cảnh máy quay, nút bấm chính | `cinematic/expand`, `glass/send`, `studio/press`, `glass/toggle-on` | −7 … −7,5 dB |
| Thẻ trượt, tiêu đề, cảnh báo nhẹ | `studio/swipe`, `soft/warning`, `studio/connect` | −8 … −8,5 dB |
| Chuyển động nhỏ, avatar, gõ phím, quét AI | `studio/focus`, `minimal/progress-step`, `studio/typing`, `studio/scanning` | −9 … −9,5 dB |

  - nhạc trong `Music_Holder`: gain −8 dB.
- Gain layer chỉ có nghĩa khi biết file to bao nhiêu. Đổi bộ âm hay đổi nhạc thì đo lại, không chép số.
- Master như mục 9.8.

## 10. Render và xuất file

### 10.1 MP4

```bash
"<AE>\aerender.exe" -project <aep> -comp <COMP> -s 0 -e 1079 -RStemplate "Best Settings" -OMtemplate "H.264 - Match Render Settings - 40 Mbps" -output <mp4>
```

- `tools/ae.py render` gọi đúng lệnh này, ghi log `.aerender.log` và báo các dòng ERROR.
- aerender luôn mở engine riêng, không đụng phiên của Minh. Không dùng `-reuse`.
- Ca mẫu A: video 36 s, 1080p, 30 fps render khoảng 55 s.
- Render một project khác (nhánh B, bản sao template): thêm `--project`, ví dụ
  `python -I tools/ae.py render --project "<bản sao>.aep" --comp "Full_HD (1920 x 1080)" --start 0 --end <khung cuối> --out out/review/_lam/b01.mp4`.
  - Giao 1080p thì render comp Full HD của template; giao 4K thì render comp 4K.
  - Giữ fps của template. Đổi fps của template làm lệch mọi mốc thời gian đã dựng.

### 10.2 Gắn thẻ màu

H.264 xuất bằng template "Match Render Settings" được mã hóa theo BT.709 dải TV, nhưng không gắn thẻ. Máy phát vì vậy đoán sai màu. Gắn thẻ mà không mã hóa lại:

```bash
ffmpeg -y -i bNN.mp4 -c copy -bsf:v h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0 bNN_709.mp4
```

Khi đo màu phải giải mã theo bt709: #0068FF ra (0,104,255). Lệch ≤ 3 mức là do mã hóa.

### 10.3 Ảnh tĩnh

- `tools/ae.py stills`: dùng aerender với `-OMtemplate "TIFF Sequence with Alpha"` cho từng khung, rồi ffmpeg đổi ra PNG.
- aerender không ghi được chuỗi ảnh vào đường dẫn có dấu cách (đo 26/10, lỗi "Directory does not exist" với "Minh\ PC"). `ae.py` bản trong skill render TIFF vào thư mục tạm không dấu cách (`%PUBLIC%`), rồi mới đổi ra PNG ở thư mục đích.
- `comp.saveFrameToPng` không ghi được ảnh trong lần thử 21/10. Đừng dùng làm bằng chứng.
- RenderQueue trong script có thể trả `ERR_STOPPED` dù đã ghi TIFF. Mở file ra kiểm.
- Cách khác: trích khung từ MP4 bằng ffmpeg.
  - Tờ khung 1 khung mỗi giây: `tools/to_contact.py` (có trong `<KHUNG>` và `<VD-A>`).
  - Tờ khung đã hiện đủ: `<VD-A>\tools\to_khung.py`.

### 10.4 So hai bản

- Âm: `ffmpeg -v error -i a.mp4 -map 0:a -f md5 -`. Muốn biết khác ở đâu: giải mã hai bản ra f32, trừ cho nhau, gom vùng lệch theo cửa sổ 10 ms.
- Hình: `ffmpeg -i a.mp4 -i b.mp4 -lavfi "[0:v][1:v]psnr=stats_file=psnr.log" -f null -`. Vài khung có PSNR ≥ 78 dB là nhiễu mã hóa, hình không đổi.
- Dùng để chứng minh lần sửa chỉ đổi đúng chỗ cần đổi.

### 10.5 Bản nghe thử nhẹ

```bash
ffmpeg -y -i ban_giao.mp4 -vf scale=1280:720:flags=lanczos -c:v libx264 -preset slow -crf 28 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -c:a copy -movflags +faststart ban_nghe-thu-720p.mp4
```

`-c:a copy` giữ âm trùng từng byte với bản giao. Video 36 s ra khoảng 3 MB.

## 11. Thang kiểm trước khi giao

| Nấc | Kiểm | Lệnh, cách làm | Đạt khi |
|---|---|---|---|
| 1 | Dựng | `tools/ae.py build` (nhánh B: báo cáo của script sửa template) | 0 lỗi dựng, 0 lỗi expression, không có font thay thế |
| 2 | Khung đã hiện đủ | ảnh mỗi cảnh lúc chữ và hình đã vào đủ | xem bằng mắt: không đè, không tràn, đúng màu |
| 3 | Tờ khung, điểm nối | tờ 1 khung/giây; dải 5 khung quanh mọi điểm nối và cú chạm | không cắt cứng, không mất vật, không giật |
| 4 | Chữ | `tools/qa_chu.py` | đúng luật chữ mục 6.5; mục song song cùng kiểu |
| 5 | Màu | giải mã bt709, lấy mẫu nền và các khối | đúng bảng màu, lệch ≤ 3 mức |
| 6 | Chuyển động | `<SKILL>/scripts/v2w/metrics.py --no-flow` | Tĩnh B ≤ 15 % mỗi ô 2 s, Tĩnh A 0, 0 cắt cứng |
| 7 | Âm | ebur128; lệch đỉnh SFX so với khung; có giọng: nhạc dưới giọng, che phụ âm 2–8 kHz, whisper; không giọng: cột "Nhô" của từng cue so với nhạc | đúng mức mục 9; đỉnh SFX trễ ≤ 1 khung, không sớm |
| 8 | Rà chéo | agent mới: Q (hình, chữ) và Q5 (âm). Chỉ đưa file và số đo, không đưa kết luận tự kiểm | không còn "Cần sửa"; "Nên sửa" đã sửa hoặc ghi lý do để ngỏ |
| 9 | File giao | master; ffprobe; đo lại I, TP trên file giao; bản nghe thử 720p | −16,0 LUFS, ≤ −2 dBTP, h264 gắn thẻ bt709, đúng độ dài |

- Chỉ báo "xong" sau khi đã mở hoặc giải mã file ra và xem. Không suy từ việc lệnh đã chạy xong.
- Nấc nào không làm được thì ghi "chưa kiểm". Còn lỗi "Cần sửa" hoặc nấc "chưa kiểm" thì giao dưới tên **bản nháp**.
- Ở ca mẫu A, rà chéo âm bắt được 2 tiếng chip đè phụ âm mà tự kiểm, kể cả whisper, đã bỏ sót. Đừng bỏ nấc 8.
- Agent chỉ đo, không nghe được bằng tai. Ghi rõ điều đó và nhờ Minh nghe.
- Nhánh B: script sửa template phải xuất `textDump` vào báo cáo (chép hàm `dumpTexts` trong `<KHUNG>\build\main.jsx`), thì nấc 4 mới chạy được `qa_chu.py`.

### 11.1 Rà chéo: Q và Q5

- Mỗi agent rà là một agent mới, chưa đọc gì của dự án. Không đưa kết luận tự kiểm cho agent đó, để nó nhìn bằng mắt mới.
- Đầu vào: MP4 giao, tờ khung 1 giây, dải khung ở các điểm nối, bảng số đo, brief và kịch bản (`KHUNG-DUNG.md`). Q5 cần thêm bảng cue và file giọng riêng nếu có.
- Yêu cầu trả về:
  - danh sách lỗi, mỗi lỗi có giây hoặc khung, xếp ba mức "Cần sửa", "Nên sửa", "Ghi nhận";
  - điểm từng mặt. Q chấm chuyển động, chữ, thương hiệu, kể chuyện. Q5 chấm rõ lời, cân mức, đồng bộ, an toàn đỉnh.
- Sửa xong thì gửi lại đúng agent đó cho vòng 2: soát lại từng lỗi đã nêu và tìm lỗi mới.

## 12. Học từ template AE có sẵn

### 12.1 Xem trước khi có file (Envato)

Trang mẫu `app.envato.com/.../video-templates/<id>` không cần đăng nhập.
- Tab "Inside the file" → bấm "Expand all": hiện cây project thật (thư mục, tên comp, asset; tối đa 20 mục mỗi thư mục). Đọc bằng `document.body.innerText`.
- Video hướng dẫn thường quay màn hình AE. Cắt cận khung thì đọc được Effect Controls và lớp điều khiển.
- Lấy khung hình preview:
  1. tạo một `<video>` mới cùng `src`;
  2. seek tới thời điểm cần;
  3. chờ `requestVideoFrameCallback`;
  4. `drawImage` lên canvas rồi chụp màn hình.
- File .aep thì Minh phải tự tải bằng tài khoản của Minh.

### 12.2 Khi đã có .aep

- Mở **bản sao** trong phiên riêng, chỉ đọc, không lưu.
- Script trích nằm ở `<SKILL>\references\template-audit\scripts\`. Sửa đường dẫn cứng `/media/vmiz/Over Powers/video AE/...` trước khi chạy.
  - `export-projects.jsx`: cả cây comp, layer, thuộc tính, key, ease, tangent, expression → JSON.
  - `sample-and-render.jsx`: tìm font thiếu; lấy mẫu `valueAtTime` mỗi 0,25 khung.
  - `render-frames.jsx`: render vài khung TIFF để xem.
  - `property-units.jsx`: đối chiếu số thô với số trên giao diện.
- Kết quả của lần trích 21/10, nằm ở `<SKILL>\references\template-audit\`:
  - `BAO-CAO-PHAN-TICH.md`: đọc trước;
  - `MOTION-PRESETS.json`: 10 công thức;
  - `BANG-TEXT-VA-KEYFRAME.md`;
  - prompt giao việc: `PROMPT-HOAN-CHINH-OPUS.md`.
- Ca mẫu B tính giây toàn cục của mọi cảnh, comp con bằng `<VD-B>\parse_aep_timings.py`.
  - Script này đọc một báo cáo dạng chữ phân tab (`COMP`, `LAYER`, `TEXT_VAL`…), không đọc JSON của `export-projects.jsx`. Hai bước chưa nối được với nhau.
  - Có JSON của `export-projects.jsx` thì tự cộng `startTime` các tầng theo mục 4.3. Muốn dùng `parse_aep_timings.py` thì phải ghi báo cáo đúng dạng chữ đó.
  - Trong phiên riêng, cứ ghi báo cáo thẳng ra file. Không cần mẹo giấu báo cáo vào file .aepx.

### 12.3 Bẫy khi đọc template

- Font thiếu: Manrope bị thay bằng Times trong lần trích 21/10. Ảnh render khi ấy không đại diện cho font gốc.
- Expression lỗi có sẵn trong template (Bevel Angle gọi `Angle Glow` không tồn tại). Đừng chép.
- Tên comp trùng giữa hai nhánh template. Nhận diện bằng ID kèm chuỗi sử dụng.
- Key là khung cục bộ: phải cộng offset của các tầng (mục 4.3).
- Số thô khác số trên giao diện (mục 7.6). Style đang tắt vẫn đọc được giá trị.
- Pixel của template theo khổ gốc (ví dụ 2160×3840). Đổi khổ thì nhân q = bề rộng mới / bề rộng gốc cho các đại lượng pixel, giữ nguyên % và góc. Hoặc đổi theo em như ca mẫu A.
- Music comp của template có thể rỗng.

## 13. Nhánh B: sửa template mua về

Các bước. Ca mẫu: `<VD-B>` (đọc `README.md` trong đó trước):
1. **Kịch bản và brief:** chốt chữ, CTA, logo, ảnh, nhạc, khổ (G0). Template 4K (3840×2160) thì cỡ chữ nhỏ nhất 56 px.
2. **Đọc cấu trúc template** (mục 12.2, 4.5):
   - lập bảng cảnh: giây vào ra toàn cục của mỗi cảnh và comp con (mục 4.3);
   - lập danh sách comp giữ chỗ, layer chữ, layer màu điều khiển.
3. **Chuẩn bị tài nguyên:**
   - chân dung, logo, thẻ giao diện, avatar: đúng kích thước comp giữ chỗ (ví dụ logo 1000×1000);
   - thay footage vào comp giữ chỗ thì kéo dài thời lượng của comp giữ chỗ lẫn comp bao ngoài cho đủ cảnh, để hình không tắt sớm;
   - avatar khung chat: giữ layer Background của template, đặt avatar mới lên trên cùng (`moveToBeginning()`).
4. **Sửa bằng script, trên bản sao, trong phiên riêng:**
   - thay chữ theo mục 6.6;
   - đổi màu ở các layer điều khiển (mục 4.5), rồi tìm màu gán cứng còn sót;
   - không để `catch` rỗng; mọi lỗi ghi ra báo cáo.
5. **Âm** (mục 9.3, 9.4, 9.10): chọn bộ âm theo gu, căn đỉnh theo giây toàn cục, chống phát đúp, đo, rồi master.
6. **Render, thang kiểm, bàn giao** (mục 10, 11, 14).

Luật thương hiệu vẫn áp: video OPA theo BRAND-SPEC (5 màu, phẳng, mascot không mắt), dù template gốc có glow, kính, 3D. Mặc định làm phẳng; muốn giữ hiệu ứng của template trái BRAND-SPEC thì Minh quyết ở G0.

**Công cụ nhánh B còn thiếu trong gói** (chưa làm vì chưa thử được trên AE):
- Chưa có lệnh chạy một JSX lên bản sao template. `tools/ae.py build` luôn chép seed trống đè lên file đích, nên không dùng cho nhánh B.
- Cách làm tạm:
  1. viết JSX tự mở bản sao (`app.open(new File(...))`), sửa, `save()`, rồi ghi báo cáo JSON;
  2. chạy bằng loader như mục 3.2, đổi đường dẫn bundle thành file JSX đó;
  3. lần đầu chạy, đọc báo cáo và mở bản sao ra xem trước khi làm tiếp.
- Render, xuất khung của bản sao: `tools/ae.py render` hoặc `stills` với `--project` (mục 10.1).
- Bốn script của `<VD-B>` có nhiều chỗ làm trái luật của skill. Đọc mục "Chỗ làm trái luật" trong `README.md` của nó trước khi dùng.

## 14. Bàn giao và cách sửa

**Giao những gì:**
- project `.aep` cùng thư mục assets;
- script dựng lại hoặc script sửa template (`build/`, `tools/`);
- MP4 giao đã master và gắn thẻ bt709;
- bản nghe thử 720p;
- ảnh khung đã hiện đủ và tờ khung 1 giây;
- `KHUNG-DUNG.md`: brief đã chốt, giả định, phương án chuyển động, công thức, bảng theo cảnh, bảng mốc chữ, bảng SFX, cấu trúc project, cách sửa, kết quả từng nấc kiểm. Mẫu: `<VD-A>\KHUNG-DUNG.md`;
- bảng cue âm: cue, mức, lý do, nguồn research. Mẫu: `<VD-A>\audio\BANG-CUE-AM-THANH.md`.

**Cách sửa (ghi lại cho Minh), ví dụ nhánh A:**
- Đổi chữ: `03_EDIT_CHU` → comp `TXT_…` → layer `TEXT`.
- Đổi màu: `CONTROL` → `BRAND` → Color Control.
- Đổi giọng: chạy lại `am_thanh_cues.py` với file giọng mới, rồi dựng lại.
- Đổi âm: sửa `cues()` trong `am_thanh_cues.py`, chạy lại, dựng lại.
- Dựng lại từ đầu: `python -I tools/ae.py build`.
- Ghi rõ font cần cài. Không dùng plugin ngoài, chỉ effect gốc của AE.

**Báo cáo:** đã kiểm gì; tự kiểm hay rà chéo bằng agent; chưa kiểm gì; điểm chờ duyệt.
- Video OPA: Minh duyệt lời; Hùng duyệt hình trước khi đăng (BRAND-SPEC mục 7).
- Video làm cho khách khác: Minh quyết ai duyệt.

## 15. Nhánh A: bắt đầu dự án mới

1. Chép `<KHUNG>` thành `<dự án>\ae\<tên>\`. Bộ khung đã thử ngày 26/10 trên AE 2026: dựng, xuất khung, soát chữ đều đạt.
2. Sửa:

| File | Sửa gì |
|---|---|
| `build\lib.jsx` | `O.COLORS`, `O.FONT` (mặc định OPA); `O.W`, `O.H`, `O.FPS` nếu khác 1920×1080, 30 fps. Giữ `O.EASE`, `O.anim`, `O.textAnim`. `O.makeControl` ghi cứng 6 tên màu (`blue`, `blueDark`, `blueLight`, `black`, `white`, `alert`): giữ nguyên 6 tên và chỉ đổi giá trị RGB; thêm tên mới thì thêm cả vào danh sách trong `O.makeControl` |
| `build\main.jsx` | thời lượng master, danh sách cảnh `plan` |
| `build\scenes\*.jsx` | viết các cảnh `OPA.buildSx`; xóa cảnh mẫu `s1_mau.jsx` |
| `tools\qa_chu.py` | bộ font được duyệt |
| `tools\ae.py` | `AE_DIR` nếu AE cài chỗ khác |

3. Thêm âm: chép từ `<VD-A>` các file `build\scenes\am_thanh.jsx`, `tools\am_thanh_cues.py`, `tools\phan_tich_sfx.py`. Rồi sửa đủ các chỗ sau, vì chúng ghi cứng cho ca OPA Agent 36 s:

| Chỗ | Sửa gì |
|---|---|
| `build\main.jsx` của bộ khung | thêm đoạn gắn comp âm vào master và đoạn giọng đọc. Chép từ `<VD-A>\build\main.jsx`: khối `if (O.buildAudio && A.sfx)` và khối `if (O.VOICE && A.sfx)` |
| `build\scenes\am_thanh.jsx` | thời lượng comp âm đang là 1080 khung (36 s): đổi bằng thời lượng master |
| `am_thanh_cues.py`: `MUSIC` | đường dẫn file nhạc. Nhạc phải là WAV 48 kHz sẵn trong `assets\music\`, vì script không tự đổi nhạc (mục 9.6) |
| `am_thanh_cues.py`: `MUSIC_LUFS` | −31 khi có giọng; khoảng −17 khi không giọng (mục 9.10) |
| `am_thanh_cues.py`: `SND`, `SHIFT`, `cues()` | bộ âm, độ dịch cao độ, danh sách cue của video mới |
| `am_thanh_cues.py`: `OPA_KIT` | logo âm thanh OPA; video khác bỏ hoặc thay |
| `am_thanh_cues.py`: `write_md`, `LEVELS` | tiêu đề 5 cảnh và chú thích của ca OPA: viết lại theo video mới |
4. Đi qua các cổng:
   1. brief: hỏi gộp một lần;
   2. đoạn mẫu 3–5 s và khung đã hiện đủ, để Minh duyệt gu;
   3. dựng đủ, tự kiểm;
   4. âm, Minh nghe;
   5. lồng giọng, master;
   6. rà chéo;
   7. giao.

Ca mẫu A đã đi: v07 (mẫu gu) → v08 (đủ 5 cảnh, Minh duyệt) → v09 (SFX và nhạc, Minh duyệt âm) → v10 (giọng đọc và URL).

## 16. Lỗi hay gặp

| Dấu hiệu | Làm đúng |
|---|---|
| Gửi script vào AE bằng `-r`, đổi tiến trình cha để chui vào phiên đang mở, hoặc điều khiển AE bằng chuột | `AfterFX.exe -noui -m -s "<loader>"` trong phiên riêng |
| `-m -r file.jsx` tự thoát sau khoảng 6 s; `$.evalFile` không chạy | loader `File.read()` rồi `eval` |
| `app.project.save(new File())` trả false | chép seed trống (hoặc bản sao template) → open → save() |
| Script lưu đè lên template gốc | làm trên bản sao |
| `openInViewer()` trong phiên headless | bỏ; hàm này cần giao diện |
| `catch (err) {}` rỗng | ghi lỗi vào báo cáo |
| Nền "LINEAR" vẫn chậm dần ở hai đầu | đặt kiểu nội suy SAU `setTemporalEaseAtKey` |
| Dùng Easy Ease 33 % cho mọi thứ | preset theo vai trò (mục 5.2) |
| Mỗi từ một animator; key Opacity cho cả layer | một animator, Based On = Từ, Start 0→100 |
| Đổi chữ trong template làm gãy expression | giữ `layer.name` (mục 6.6) |
| Câu tiếng Việt dài, chữ cuối không hiện | Max Ease = 0, đặt lại Start 0→100 (mục 6.6) |
| Shape đứng đầu mảng lại nằm trên cùng | thêm nhóm theo thứ tự ngược |
| Layer con không mờ theo cha | expression theo opacity của cha |
| Squash & stretch, mắt, màu ngoài bảng cho Bò OPA | BRAND-SPEC: chỉ co giãn đều, không mắt, 5 màu (mục 7.8) |
| Chữ ra Times hoặc sai dáng | kiểm `isSubstitute`; AddFontResourceW + WM_FONTCHANGE; mở phiên mới |
| Màu MP4 lệch | gắn thẻ BT.709 bằng `h264_metadata` |
| `ae.py stills` báo "Directory does not exist" | đường dẫn có dấu cách; dùng `ae.py` bản trong skill (render qua thư mục tạm) |
| Nhạc to hơn đích 3 LU | file mono: đo bằng cách nhân đôi kênh, không dùng `-ac 2` |
| SFX lệch giờ | MP3 → WAV 48 kHz; căn ĐỈNH: `startTime = t − peak_s` |
| Đặt cứng gain −5 … −10 dB mà không đo | gain = M đích − M đo; số của ca mẫu B chỉ là điểm xuất phát (mục 9.10) |
| Mỗi tiếng SFX phát hai lần, to thêm 6 dB | tắt `audioEnabled` của layer cảnh trong comp tổng (mục 9.4) |
| Bản trộn vượt −2 dBTP | trần −12 dBTP mỗi cue, kiểm âm chồng; master tuyến tính |
| SFX đè phụ âm mà whisper vẫn báo ổn | đo dải 2–8 kHz trên cả cửa sổ cue |
| Âm có nốt lạc giọng nhạc | đo cao độ, dịch theo cent |
| Hai âm giống nhau cách dưới 3 khung | dời hoặc bỏ một âm |
| Báo "render xong" khi chưa mở file | giải mã, xem khung, đo âm rồi mới báo |
| Hộp "Crash Repair Options" sau khi buộc tắt | gửi Enter vào đúng cửa sổ của phiên mình |
| Lệnh `ffmpeg` không ghi file mà vẫn trả mã 0 | luôn thêm `-y` |
| Python in tiếng Việt bị lỗi | `python -X utf8` hoặc `PYTHONIOENCODING=utf-8` |
| Lệnh hỏng mà `\| tail` vẫn báo exit 0 | đọc kết quả thật |
| Template ghi opacity bóng 76,5 | đó là số thô thang 0–255, bằng 30 % trên giao diện |
| Template do bản AE cũ lưu, phiên headless không lưu được | nhờ Minh mở bằng AE 2026 và Save As một lần (mục 3.3) |
| Sửa Range Selector của template xong thì mất pha ra | chỉ đặt lại key pha vào, giữ pha ra, đặt ease theo vai trò (mục 6.6) |
| Tắt âm layer cảnh để chống phát đúp, nhạc cũng tắt theo | mỗi tiếng chỉ đặt ở một nơi; nhạc nằm ngoài comp cảnh (mục 9.4) |
| Video không giọng mà giữ nhạc −31 LUFS | nhạc khoảng −17 LUFS; đổi `MUSIC_LUFS` (mục 9.10) |
| Đổi fps của template | giữ fps của template |

## 17. Cấu hình máy, cài skill, phụ thuộc

**Đường dẫn theo máy của Minh** (máy khác thì đổi):

| Thứ | Đường dẫn | Ở đâu trong code |
|---|---|---|
| After Effects 2026 | `C:\Program Files\Adobe\Adobe After Effects 2026\Support Files` | `AE_DIR` trong `tools/ae.py` |
| Kho SFX | `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx` | tham số đầu của `am_thanh_cues.py` |
| Giọng đọc Minh gửi | `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/VOICE` | tham số thứ hai của `am_thanh_cues.py` |
| Dự án OPA sống | `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/OPA-Motion-graphic-mascot` | BRAND-SPEC, nhạc tự tổng hợp |
| Template nhánh B | `/media/vmiz/Over Powers/video AE/template intro/video edit teamplate` | đầu các script `<VD-B>` |

**Phụ thuộc:** Python 3.12 + numpy, scipy; ffmpeg, ffprobe trong PATH; After Effects 2026. Whisper cần thêm `faster-whisper` và model large-v3 tải sẵn. Thiếu thư viện thì hỏi Minh trước khi cài.

**Cài skill:**
- Claude Code: chép thư mục `after-effects` vào `C:\Users\<tên>\.claude\skills\`. Trên máy Minh, thư mục đó là junction trỏ về bản gốc `/media/vmiz/Over Powers/THÀNH V/Skill/after-effects`.
- Agent đọc `.agents\skills` (Codex, Gemini CLI, Antigravity…): chép thư mục vào `.agents\skills\` của agent đó, hoặc vào `C:\Users\<tên>\.agents\skills\`.
- claude.ai: tải file `after-effects.zip` lên mục Skills.
- Cập nhật: sửa bản gốc ở `/media/vmiz/Over Powers/THÀNH V/Skill/after-effects`. Bản chép ở chỗ khác (hiện có `/media/vmiz/Over Powers/THÀNH V/Motion Omi/.agents/skills/after-effects`) phải chép lại, rồi đóng lại file zip.

## 18. Nguồn

**Trong gói skill:**
- Ca mẫu A: `<VD-A>\KHUNG-DUNG.md`, `<VD-A>\audio\BANG-CUE-AM-THANH.md`, `<VD-A>\build\*`, `<VD-A>\tools\*.py`.
- Ca mẫu B: `<VD-B>\*`.
- Phân tích template: `<SKILL>\references\template-audit\` (`BAO-CAO-PHAN-TICH.md`, `MOTION-PRESETS.json`, `PROMPT-HOAN-CHINH-OPUS.md`, `BANG-TEXT-VA-KEYFRAME.md`, `scripts\*.jsx`).
- Thiết kế UI từ phác thảo (Sketch-to-UI) & Nhân vật 2D–3D tách lớp: `<SKILL>\references\sketch-to-ui-va-nhan-vat.md`.
- Âm: `<SKILL>\references\nghien-cuu-decibel.md`; `<SKILL>\scripts\master.py`, `transcribe.py`, `cao_do.py`; số đo kho SFX `<SKILL>\data\kho_sfx_do.csv`.
- Đo chuyển động: `<SKILL>\scripts\v2w\` (`metrics.py`, `metrics_core.py`, `scan_video.py`, `contact.py`).

**Trên máy Minh:**
- Luật: `<OPA>\BRAND-SPEC.md`; `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/AI Video/EDITORIAL_RULES.md`; skill `master-video-edit`.
- Dữ liệu trích template đầy đủ (khoảng 200 MB): `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/research/ae-text-audit-2026-10-21`.
- Motion Omi (UI, nhân vật, prompt Omni Flash): `/media/vmiz/Over Powers/THÀNH V/Motion Omi`.
- Nhạc tự tổng hợp của OPA: `<OPA>\tools\audio\score_agent.py`. Không có trong gói, vì cần bộ nhạc cụ của dự án OPA.

**Web:**
- Adobe, Scripts in After Effects: https://helpx.adobe.com/after-effects/using/scripts.html
- After Effects Scripting Guide (property, keyframe, ease): https://ae-scripting.docsforadobe.dev/
- Fonts object: https://ae-scripting.docsforadobe.dev/text/fontsobject/
- EBU R 128 s1: https://tech.ebu.ch/docs/r/r128s1.pdf
