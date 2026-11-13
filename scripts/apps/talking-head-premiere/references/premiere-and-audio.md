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
