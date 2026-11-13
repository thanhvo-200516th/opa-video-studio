# Chất lượng render: tích lũy mẫu, hoàn thiện, màu, GPU, gửi khung, mã hóa

Mô tả đúng code của ca mẫu trong `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/OPA-Motion-graphic-mascot`:
`film3d/lib/accum.js` (tích lũy, hoàn thiện), `film3d/lib/wire.js` (gửi khung), `tools/film3d/render.py` (Chrome, nhận khung, mã hóa, ghép), `film3d/lib/world-desk.js` (đèn, phơi sáng), `film3d/lib/mascot3d.js` (look C2). Số đo lấy từ `render-meta.json` của ca mẫu, `docs/film3d/g1-thu-look.md` và báo cáo lane T.

## 1. Đường đi của một khung

```
poseAt(t + lệch) → world.apply → vẽ 1 mẫu ở 3840×2160 (RGBA16F, có độ sâu) → cộng vào bộ đệm RGBA32F
   ↑ lặp 16 lần (mẫu i = 0 … 15)
bộ đệm 32F → ×1/16 ×EXPO → kẹp [0, 1] (không tone map) → Lanczos-3 ngang → Lanczos-3 dọc + sRGB + dither
→ RGBA8 1920×1080 → readPixels → WebSocket → Python → ffmpeg FFV1 (clip.mkv) → H.264 (clip.mp4)
```

## 2. Tích lũy 16 mẫu

Một **mẫu** là một lần vẽ cả khung. Mẫu i trong N lệch bốn thứ (`sampleOffsets(i, N, 0.45)`). Mặc định N = 16. N không được chia hết cho 7, để phép xáo π(i) bên dưới đi qua đủ mọi mẫu; lũy thừa của 2 và 48 đều được.

| Lệch | Cách tính | Ra hiệu ứng |
|---|---|---|
| Thời điểm | t + (0,45 / fps) × ((π(i) + 0,5) / N − 0,5), với π(i) = (7i + 3) mod N | Nhòe chuyển động. "Màn trập 0,45 khung" = cửa chập mở 45 % thời gian một khung. π(i) xáo thứ tự để lệch thời gian không đi cùng lệch ống kính |
| Dưới điểm ảnh | dãy Halton cơ số 2 và 3, trong ±0,5 điểm ảnh (khung 2×) | Khử răng cưa |
| Điểm trên ống kính | Halton cơ số 5 và 7, ánh xạ lên đĩa | Xóa phông (DOF, độ sâu trường ảnh) |
| Hướng đèn | Halton cơ số 11 và 13; ca mẫu xoay đèn chính trong nón 7° | Bóng mềm |

- **Dãy Halton** là dãy số rải đều có quy luật, đều hơn số ngẫu nhiên, và tất định.
- **Xóa phông bằng xô phép chiếu** (`lensAndJitter`): máy dời theo (ex, ey) = điểm trên đĩa × độ mở ống kính; ma trận chiếu cộng `P[8] −= P00·ex/focus`, `P[9] −= P11·ey/focus`, nên mặt phẳng nét giữ ở khoảng cách `focus`. Lệch dưới điểm ảnh cộng vào cùng hai ô đó. Ca mẫu: độ mở 0,006 m; `focus` = khoảng cách máy tới mascot; độ mở về 0 ở khung khóa.
- **N = 1** (nháp): không lệch gì, như máy ảnh lỗ kim, có răng cưa.
- Mỗi mẫu vẽ vào đích RGBA16F có độ sâu; bóng đổ vẽ lại cho từng mẫu; rồi cộng vào RGBA32F bằng phép blend cộng.
- **Phải cộng dồn bằng 32F.** Probe lane T: cộng 0,001 hai lần vào 0,25 thì 16F ra 0,25195, 32F ra 0,25200.
- Cần extension `EXT_float_blend`; thiếu thì trang ném lỗi "thiếu EXT_float_blend".
- **Tăng mẫu theo đoạn** (`sppBoost` trong job `clip`): `[[f0, f1, spp], ...]`. Bản 1 của ca mẫu: vật bay rất nhanh làm vệt nhòe có vân sọc ở khung 298 và 446, nên khung 292–304 và 440–452 vẽ 48 mẫu; khung khác vẫn 16. Bản 2 đi đều nhịp, không còn cú bay nhanh như vậy, nên không cần.

## 3. Hoàn thiện trên GPU (resolve)

`Accumulator.resolve({expo, tone, frame, grain})`, khoảng 0,7 ms mỗi khung trên RTX:

1. Nhân 1/N rồi nhân EXPO (phơi sáng).
2. `tone: 0` = kẹp vào [0, 1] (ca mẫu dùng); `tone: 1` = Neutral. Không có ACES.
3. Lanczos-3 thu nhỏ 2:1, tách hai lượt (ngang rồi dọc), trong ánh sáng tuyến tính. Kẹp trước rồi mới thu, để không có viền tối quanh vùng sáng.
4. OETF sRGB: đường cong đổi ánh sáng tuyến tính sang mã màu của màn hình.
5. **Dither TPDF ±1 mức**: cộng nhiễu tam giác rất nhỏ, để dải chuyển màu không thành bậc. Grain có seed theo khung: có sẵn, ca mẫu để 0.
6. Lật dòng ngay trong shader, để `readPixels` ra ảnh từ trên xuống. Dữ liệu float không ra khỏi GPU.

`scale` của `Accumulator` chỉ nhận 1 hoặc 2 (render 1× hoặc 2× rồi thu về 1080p).

## 4. Màu

- #0068FF nằm sát mép gam màu sRGB (R = 0, B = 255). Tone map nào cũng kéo lệch: lane B tính ACES lệch ΔE2000 3,98, Neutral 1,31, kẹp 0. Vì vậy: không tone map, vật liệu không phản xạ bóng, phơi sáng tính chứ không đoán.
- Trên MP4, #0068FF giải mã ra (0, 103, 255) = #0067FF. Đây là số dự án từng đo trên V2, V3. `qa.py` lấy đích (0, 104, 255).
- **EXPO tính giải tích** (`world-desk.js`): EXPO = 0,995·π / (I_key·key_z + I_fill·fill_z + I_hemi·hemi_B). Tức là chọn sao cho mặt trắng hướng thẳng về máy, dưới đèn ban ngày, ra 0,995: sát trắng mà không cháy. Ca mẫu: EXPO = 0,8305.
- **Vật không chịu đèn** (màn hình, bong bóng, hạt thở, vùng tràn xanh) nhân màu với `INV_EXPO` = 1/EXPO. Sau bước ×EXPO, chúng ra đúng màu token.
- **Nền phẳng** (`style.bg = 'flat'`, mặc định từ bản 2):
  - bàn, tường, sàn là một vật liệu không chịu đèn (`fieldMat`), cùng màu với màu xóa khung, nhân `INV_EXPO`;
  - đèn của đồ vật luôn ở mức ban ngày; đêm hay ngày chỉ đổi màu nền (#003C99 → trắng), như V2;
  - đổi màu nền trộn mã sRGB (`getRGB(..., SRGBColorSpace)` rồi `setRGB(..., SRGBColorSpace)`). Trộn trong ánh sáng tuyến tính cho màu xám đục giữa chừng;
  - kiểu phòng có đèn của bản 1 vẫn còn (`style.bg = 'room'`).
- **Look C2** (shader `C2_FS` trong `mascot3d.js`; mascot không dùng đèn của cảnh):
  - mặt trước và mặt sau giữ đúng màu token, phẳng tuyệt đối;
  - trọng số cạnh vát f tính theo vị trí chiều sâu |z| của điểm (0 trên mặt, 1 ở thành bên), không theo pháp tuyến từng mặt nhỏ, nên ranh màu mượt, hết khấc;
  - thành bên đi từ token đậm (#003C99) tới token (#0068FF) theo độ sáng e = 0,30 + 0,55·max(n·key, 0) + 0,20·max(n·fill, 0), với đèn tính trong không gian vật (bám theo mascot);
  - vệt sáng mảnh dọc cạnh vát hướng về đèn chính (`uRim` 0,45);
  - `uFlat` = 1: tô phẳng hoàn toàn (khung khóa); `uWhite` và vùng tràn xanh đổi sang bảng màu trắng theo từng điểm ảnh (cầu sang end card);
  - cuối cùng nhân `uInvExpo`.
- Hình C2: dày t, cạnh vát 0,08t, 6 đoạn, pháp tuyến mượt tới 40°, `bevelOffset = −bevel` để viền ngoài nằm đúng vector. Kiểu A, B, C của G1 vẫn còn trong `createBo` để so.
- `tools/qa/palette.py` của dự án báo lỗi oan trên ảnh 3D (mảng chuyển sắc). Phim 3D đo màu theo mặt nạ bằng `qa.py`.

## 5. GPU và Chrome

Bộ cờ đủ nằm ở hằng `BASE_FLAGS`, `GPU_FLAGS` của `render.py`. Phần quan trọng:

```
chrome.exe --headless --use-angle=d3d11 --force_high_performance_gpu --enable-gpu --ignore-gpu-blocklist
           --force-color-profile=srgb --disable-background-timer-throttling --disable-renderer-backgrounding
           --user-data-dir=<thư mục tạm của job> <url>
```

| Cờ (đo bằng chuỗi GPU của WebGL, lane T) | GPU |
|---|---|
| Mặc định; `--use-angle=d3d11 --enable-gpu --ignore-gpu-blocklist`; cờ kiểu HyperFrames; `d3d11on12` | Intel UHD 770 |
| `--use-angle=d3d11 --force_high_performance_gpu` | **RTX 3070 Ti** (mặc định của skill) |
| `--use-angle=vulkan --enable-features=Vulkan --no-sandbox` | RTX, nhanh hơn ~40 %, nhưng phải tắt sandbox; chưa kiểm tất định trên đường này |
| `--use-angle=swiftshader` | CPU |
| **Linux (máy vmiz):** `--use-angle=d3d11` | Không có WebGL (d3d11 chỉ có trên Windows) |
| **Linux:** `--use-angle=gl --enable-gpu --ignore-gpu-blocklist` | **RTX 3070 Ti**, ANGLE OpenGL 4.5 (mặc định của `render.py` trên Linux, đã render thử 2026-10-29) |
| **Linux:** `--use-angle=vulkan --enable-features=Vulkan` | RTX, không cần `--no-sandbox`; chưa kiểm tất định |

- Tin đầu (`hello`) mang chuỗi GPU. Không có "NVIDIA" thì `render.py` dừng ngay.
- Bản Chrome (user agent) ghi ở tin đầu và tin `done`. Khác nhau (Chrome tự cập nhật giữa chừng) thì báo lỗi. Ca mẫu: `HeadlessChrome/156.0.0.0`.
- Mỗi job một thư mục profile tạm. Xong hoặc lỗi đều dọn cả cây tiến trình Chrome trong khối `finally` (Windows: `taskkill /PID <pid> /T /F`; Linux: `os.killpg`, Chrome chạy trong session riêng). Hết giờ sau 900 s.
- HTTP chỉ phục vụ file trong `film3d/`, ở 127.0.0.1 (cổng ngẫu nhiên khi chạy job, 8765 khi `serve`), không cache.

## 6. Gửi khung: WebSocket, không CDP

- **CDP** (Chrome DevTools Protocol) là đường Playwright, Puppeteer dùng để điều khiển Chrome. Chụp khung 1080p qua đó mất 190–1100 ms. Ngay cả WebSocket, khi Chrome đang nối Playwright, cũng tụt còn 260–380 ms mỗi tin từ tin thứ 3.
- Cách của skill: Chrome chạy như tiến trình thường, không nối CDP; trang tự render rồi đẩy khung qua WebSocket. 2,3 ms mỗi khung 1080p (4K: 7,7 ms).
- Mỗi tin: `[u32 little-endian độ dài header][header JSON UTF-8][dữ liệu]`. Python trả "ok" sau mỗi tin; trang chờ "ok" rồi mới gửi tin sau, để giữ nhịp và không dồn bộ nhớ.
- Chrome chia tin lớn thành nhiều mảnh. Bộ nhận Python ghép đủ mảnh rồi mới xử lý.
- Bộ nhận chỉ dùng thư viện chuẩn + numpy (gỡ mặt nạ XOR của WebSocket bằng numpy).

## 7. Mã hóa

Khung về Python được đẩy thẳng vào ffmpeg:

```
-f rawvideo -pix_fmt rgba -s 1920x1080 -r 60 -i - -c:v ffv1 -level 3 -pix_fmt bgr0 -slices 24 -g 1   → clip.mkv
```

FFV1 là codec không mất chất lượng; 960 khung khoảng 1,2 GB. Rồi ra H.264 (hằng `RGB2YUV`, `X264` của `render.py`):

```
-vf scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p,
    setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709
-c:v libx264 -preset slow -profile:v high -b:v 25M -maxrate 30M -bufsize 50M -pix_fmt yuv420p
-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv -movflags +faststart
```

- **bt709** là chuẩn màu của video HD. **Dải TV** dùng mã 16–235 thay vì 0–255, là chuẩn của video phát.
- Thiếu `setparams` thì nhãn primaries và trc bị ghi "unknown".
- v0: mỗi job `clip` ra một file FFV1. Chưa chia chunk 120 khung như phương án; job lỗi thì chạy lại cả job.
- **Mux âm** (G6, G7) không mã hóa lại hình: chép nguyên luồng H.264 của bản ghép, thêm AAC 320k, `-aac_pns 0`, master mono tách thành 2 kênh giống nhau, theo quy ước mux của dự án. Kiểm bằng md5 luồng hình (`ffmpeg -i <mp4> -map 0:v -c copy -f md5 -`): bản giao phải trùng bản ghép.
  - Ca mẫu bản 2: `score_thumon_thuvien.py --video <bản ghép> --out <bản −16> --out-14 <bản −14>`. Tách kênh bằng `pan`: mỗi kênh −3,0103 dB so với mono (bản −16, độ to bằng master như `-ac 2`), hoặc −1,0103 dB (bản −14: cộng +2 dB sau limiter, không ép limiter thêm).
  - Bản 1: `score_thumon_build.py --video <bản ghép> --out <file giao>` (`-ac 2`).

## 8. Ghép lớp phủ chữ + end card

- Lớp phủ render bằng Remotion: `--codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png --muted`. Ra `.mov` ProRes 4444 có kênh trong suốt, bt709 dải TV. Ca mẫu: 1260 khung, ~177 MB; ffprobe đọc ra `yuva444p12le`.
- `render.py compose <3D.mkv> <lớp phủ.mov> <ra.mp4> [--timecode]`:
  - cả hai nguồn đưa về `settb=1/60,setpts=N` trước tiên. `clip.mkv` (Matroska) ghi mốc giờ theo ms, không chia chẵn cho 60 fps; thiếu bước này thì `overlay` chọn lệch khung: chữ giật, cứ 3 khung lặp 1, end card lệch dần. Lỗi có từ bản 1, rà chéo bản 2 mới bắt được; sửa ngày 21/10;
  - phần 3D đổi sang RGB (`gbrp`); lớp phủ đổi về RGB có alpha theo đúng bt709 dải TV;
  - chồng bằng `overlay=format=gbrp:alpha=straight`. **Alpha thẳng** nghĩa là màu chưa nhân sẵn với độ trong suốt; Remotion xuất kiểu này;
  - phần 3D ngắn hơn lớp phủ thì giữ khung cuối (`tpad ... stop_mode=clone`); end card đục che đi;
  - mã hóa H.264 một lần như mục 7, `-r 60`;
  - `--timecode`: in giờ phim ở góc dưới phải cho bản duyệt, theo số khung (giờ:phút:giây:khung, `drawtext ... timecode ... rate=60`), nên khung 960 hiện đúng `00:00:16:00`. Bản đầu in theo giây làm tròn và ghi khung 960 là "15.999". Font cục bộ, đường dẫn tương đối, nên lệnh tự chạy từ gốc dự án.
- **Vì sao không đưa MP4 3D qua Remotion:** chuỗi 3D → H.264 → Remotion chụp JPEG → H.264 là ba lần nén chồng lên một màu xanh sát mép gam màu (lane Q). Ghép bằng ffmpeg chỉ nén H.264 một lần, từ nguồn không mất.

## 9. Tốc độ đo thật (RTX 3070 Ti, D3D11, không CDP)

| Việc | Số đo | Nguồn |
|---|---|---|
| Clip 960 khung, 16 mẫu, 2×, nền phẳng, không tăng mẫu (Thủ môn bản 2, bản giao) | trung vị 25 ms/khung trong trang; cả job 105 s; mã hóa H.264 thêm ~17 s | `out/v2-hq/render-meta.json` |
| Clip 960 khung, 16 mẫu, 2×, có 26 khung 48 mẫu (Thủ môn bản 1) | trung vị 36 ms/khung trong trang; cả job 84,5 s (bản trước, chưa tăng mẫu: 75,6 s); mã hóa H.264 thêm ~17 s | `out/animatic-hq/render-meta.json` |
| Cùng clip, 1 mẫu, 1× | trung vị 15 ms/khung; cả job 36,2 s | `out/animatic/render-meta.json` |
| Khung lẻ kèm mặt nạ (job `frames`, `stills`) | trung vị 44–97 ms | `render-meta.json` các job |
| Đoạn 4 s của G1 | 26 ms/khung; 240 khung ~12 s | `g1-thu-look.md` |
| Khung đầu (biên dịch shader) | 250–660 ms; khung 48 mẫu tới ~1 s | G1, ca mẫu |
| Cảnh vừa, 614 nghìn tam giác, 3 đèn (probe) | 100,6 ms/khung | lane T |
| Lỡ chạy trên Intel (probe) | ~500 ms/khung | lane T |

Hệ quả: bản nháp 1 mẫu chỉ nhanh gấp 2 mà đo sai (nhiễu răng cưa). Duyệt luôn bằng bản chất lượng cuối.

## 10. Chưa làm, để phim sau

- **Số mẫu tự động theo tốc độ**: N = clamp(⌈v·0,45/2⌉, 16, 64), v là tốc độ trên màn hình (px/khung). Lane T đề xuất. Ca mẫu mới làm tay bằng `sppBoost` cho hai đoạn đã thấy vân sọc.
- **Chia chunk 120 khung**, chunk lỗi thì render lại riêng chunk đó.
- **Kiểm xuyên vật tự động** bằng trường khoảng cách (SDF): mascot lấy từ đường viền logo, đạo cụ giải tích, thử ở 240 Hz. Lane T thiết kế, chưa dựng.
- **`dump=anchors`** (điểm neo cho chữ bám theo vật): ca mẫu chưa cần.
- **Vulkan**: chỉ khi cần nhanh hơn; chấp nhận tắt sandbox; phải kiểm lại tất định.
