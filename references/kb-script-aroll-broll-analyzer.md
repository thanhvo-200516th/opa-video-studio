# kb-script-aroll-broll-analyzer — toàn văn tài liệu của nguồn `script-aroll-broll-analyzer`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/script-aroll-broll-analyzer/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: script-aroll-broll-analyzer/SKILL.md ===== -->

---
name: script-aroll-broll-analyzer
description: >-
  Nhận Brief và Kịch bản video (đơn lẻ, hàng loạt, hoặc từ Spec/URL), phân tích tách cảnh A-Roll và B-Roll linh hoạt theo 3 chế độ (aroll_heavy, balanced_credit_saver, broll_heavy), chuẩn hóa lời thoại tiếng Việt cho TTS, đóng gói Thư mục con đánh số thứ tự kép (01_a-roll-1.mp4, 02_b-roll-1.mp4 + 02_voice-b-roll-1.mp3...), gọi trực tiếp API HeyGen tạo video A-Roll và gọi trực tiếp API Muse (muse2api) tạo video B-Roll thuần hình ảnh (KHÔNG VOICE, KHÔNG TEXT/PHỤ ĐỀ), sẵn sàng nối thẳng vào skill master-video-edit. Kích hoạt khi người dùng gửi kịch bản/brief cần phân tích A-Roll & B-Roll, gọi API HeyGen làm A-Roll, gọi API Muse làm B-roll, hoặc chuẩn bị thư mục kịch bản cho quy trình dựng video 10 bước.
---

# Script A-Roll & B-Roll Analyzer + HeyGen A-Roll & Muse B-Roll API Pipeline

Skill này đóng gói trọn vẹn quy trình **Nhận Kịch Bản ➔ Phân Tích Cảnh `A-Roll` & `B-Roll` ➔ Gọi API HeyGen Tạo `A-Roll` ➔ Gọi API Muse Tạo `B-Roll` ➔ Đóng Gói Thư Mục Con Đánh Số Cho `master-video-edit`**:

1. **Nhận Brief & Kịch bản** (1 kịch bản lẻ, file `.md` Spec như `SPEC-50-KICH-BAN-V8.md`, file `.json`, hoặc trang web kịch bản).
2. **Phân tích kịch bản & quyết định linh hoạt tỷ lệ `A-Roll` / `B-Roll`** theo 3 chế độ (`aroll_heavy`, `balanced_credit_saver`, `broll_heavy`).
3. **Đánh số thứ tự kép tường minh (`01_a-roll-1.mp4`, `02_b-roll-1.mp4` + `02_voice-b-roll-1.mp3`, `03_a-roll-2.mp4`...)** để AI hiểu tuyệt đối mạch ghép trên Timeline.
4. **Gọi trực tiếp API HeyGen (`scripts/render_heygen_aroll.py`)** tạo video nhân vật nói `A-Roll` (`<STT>_a-roll-<N>.mp4` có sẵn Hình + Tiếng khớp khẩu hình; tự động bỏ qua các shot đánh dấu `🎥 QUAY THẬT`).
5. **Gọi trực tiếp API Muse (`scripts/render_muse_broll.py`)** tạo video trám cảnh `B-Roll` (`<STT>_b-roll-<M>.mp4` dọc `9:16`, H.264 30fps BT.709, **TUYỆT ĐỐI KHÔNG VOICE `-an`, KHÔNG TEXT / PHỤ ĐỀ / WATERMARK**).
6. **Kiểm định tự động (`validate --check-media`) & bàn giao sang [`master-video-edit`](../master-video-edit/SKILL.md)** để lắp ráp Timeline đa rãnh.

---

## 1. Quy Tắc Cốt Lõi Khi Phân Tích & Tạo `A-Roll` / `B-Roll`

### 1.1. Ba Chế Độ Phân Bổ `A-Roll` / `B-Roll` Linh Hoạt
Tuyệt đối **không áp đặt cứng nhắc một tỷ lệ cố định** cho mọi kịch bản. Phân loại từng kịch bản vào 1 trong 3 chế độ:

| Chế độ (`ratio_mode`) | Khi nào áp dụng | Tỷ lệ gợi ý | Cách phân bổ `A-Roll` & `B-Roll` |
| :--- | :--- | :---: | :--- |
| **`aroll_heavy`** *(Nhiều A-Roll, Ít B-Roll)* | Kịch bản tâm sự người làm chủ, chia sẻ góc nhìn cá nhân, triết lý quản trị, kể chuyện trực diện | `48%–70% A-Roll`<br>`30%–52% B-Roll` | Giữ `A-Roll` xuyên suốt các câu thể hiện cảm xúc, quan điểm và nhấn giọng (`~6 Shots A-Roll`); chỉ chèn `B-Roll` ở các câu nêu ví dụ hoặc minh họa. |
| **`balanced_credit_saver`** *(Cân bằng – Tối ưu Credit HeyGen)* | Kịch bản giải pháp AI doanh nghiệp, phân tích sai lầm & quy trình (mặc định) | `30%–38% A-Roll`<br>`62%–70% B-Roll` | Dùng `A-Roll` ở các nhịp chốt uy tín (`Hook`, `Story lead`, `Proof lead`, `CTA` — `~4 Shots A-Roll`), toàn bộ phần giải thích/chứng minh dùng `B-Roll` để tiết kiệm 62%–70% credit HeyGen. |
| **`broll_heavy`** *(Ít A-Roll, Nhiều B-Roll)* | Kịch bản thị phạm thao tác, 1 ảnh ra bộ video, review F&B, bất động sản Google Maps, giao diện kéo-thả | `15%–31% A-Roll`<br>`69%–85% B-Roll` | Chỉ dùng `A-Roll` ở câu Hook mở đầu, 1 nhịp chuyển ngắn và câu CTA kết bài (`~3 Shots A-Roll`); phần thân là chuỗi `B-Roll` liên tiếp (`b-roll-1` ➔ `b-roll-9`). |

---

### 1.2. Quy Tắc Đánh Số Thứ Tự Kép Trong Thư Mục Con Để AI Hiểu Tuyệt Đối

Mỗi phân đoạn trong kịch bản được đánh **2 lớp số thứ tự**:
1. **Số thứ tự xuất hiện trên Timeline (`01`, `02`, `03`...):** Vị trí đứng của phân đoạn đó từ đầu đến cuối video.
2. **Loại cảnh + Số thứ tự trong nhóm (`a-roll-1`, `b-roll-1`, `a-roll-2`, `b-roll-2`...):** Cho biết đó là cảnh A-Roll thứ mấy hay cảnh B-Roll thứ mấy.

| Loại phân đoạn | Nguồn API tạo | Tên file trong Thư mục con của Kịch bản | Giải thích cho AI / Skill Edit |
| :--- | :--- | :--- | :--- |
| **Phân đoạn `A-Roll`** | **API HeyGen** (`render_heygen_aroll.py`) hoặc `🎥 QUAY THẬT` | `<STT>_a-roll-<N>.mp4`<br>*(VD: `01_a-roll-1.mp4`, `06_a-roll-2.mp4`)* | File video người nói đã có sẵn **cả Hình lẫn Tiếng**. Đặt thẳng lên `V1` + `A1`. |
| **Phân đoạn `B-Roll` (Phần Hình)** | **API Muse (`muse2api`)** (`render_muse_broll.py`) | `<STT>_b-roll-<M>.mp4`<br>*(VD: `02_b-roll-1.mp4`, `03_b-roll-2.mp4`)* | File video minh họa **thuần hình ảnh, KHÔNG VOICE (`-an`), KHÔNG TEXT**. Đặt lên `V1`/`V2` tại đúng vị trí `<STT>`. |
| **Phân đoạn `B-Roll` (Phần Tiếng)** | **API ElevenLabs** | `<STT>_voice-b-roll-<M>.mp3`<br>*(VD: `02_voice-b-roll-1.mp3`, `03_voice-b-roll-2.mp3`)* | File âm thanh `voice-off` đi cặp 1-1 với `<STT>_b-roll-<M>.mp4` (cùng số đầu `<STT>`). Đặt xuống `A1` khớp khít với hình B-Roll đó. |

---

### 1.3. Quy Tắc Chuẩn Hóa Lời Thoại Tiếng Việt (`tts_text`) & Khóa Rule `B-Roll`
- **Chuẩn hóa `tts_text` cho HeyGen & ElevenLabs:** Mọi con số (`1`, `15`, `50.000`), phần trăm (`%`), tiền tệ (`k`, `tr`, `đ`), tốc độ khung hình (`30fps`, `24/7`) được tự động đổi sang **chữ tiếng Việt đầy đủ** (`normalize_vi_tts`).
- **Rule khóa cứng cho `B-Roll` trên Muse (`broll_prompt`):**
  - Tự động nối hậu tố tiếng Anh: `"Pure visual footage/motion only, vertical 9:16 (1080x1920), photorealistic, NO text, NO subtitles, NO captions, NO UI text, NO watermark, muted / NO voice."`
  - Khi tải về từ Muse API, script tự động chạy `ffmpeg` chuẩn hóa `1080x1920 @ 30fps BT.709`, **gỡ bỏ hoàn toàn rãnh âm thanh (`-an`)** và **xoá sạch metadata (`-map_metadata -1`)**.

---

## 2. Cấu Hình API Keys (HeyGen & Muse)

Không bao giờ ghi cứng API Key vào code hay file Markdown. Các script tự động đọc cấu hình từ biến môi trường hoặc file cấu hình trong `~/.config/`:

1. **Cấu hình API Muse (`~/.config/muse/env` hoặc biến môi trường):**
   ```ini
   MUSE_BASE_URL=http://127.0.0.1:18181/v1
   MUSE_API_KEY=sk-...
   ```
2. **Cấu hình API HeyGen (`~/.config/heygen/env` hoặc biến môi trường):**
   ```ini
   HEYGEN_API_KEY=...
   # Tùy chọn ghi đè Avatar / Voice mặc định của kênh Anh Huy:
   HEYGEN_AVATAR_ID=761364fad106369de1c3ada3994aee9c
   HEYGEN_VOICE_ID=09bed03ed2984542836268ac73ffc18c
   ```

---

## 3. Bộ Lệnh Thực Thi Toàn Quy Trình (4 Bước)

### Bước 1: Nhận Kịch Bản & Phân Tích `A-Roll` / `B-Roll` Ra Thư Mục Con

#### Trường hợp A — Từ File Spec Markdown (`SPEC-50-KICH-BAN-V8.md` hoặc `SPEC-10-KICH-BAN-V4.md`):
```bash
python3 /home/vmiz/.gemini/config/skills/script-aroll-broll-analyzer/scripts/analyze_and_scaffold.py \
  from-spec "/duong/dan/SPEC-50-KICH-BAN-V8.md" \
  --out-dir "/duong/dan/Danh_Sach_50_Kich_Ban"
```
*(Có thể thêm `--filter-id XM01` nếu chỉ muốn trích xuất 1 kịch bản cụ thể).*

#### Trường hợp B — Từ Kịch Bản Mới (File JSON bóc tách từ Brief/Text):
```bash
python3 /home/vmiz/.gemini/config/skills/script-aroll-broll-analyzer/scripts/analyze_and_scaffold.py \
  from-json "/duong/dan/input_scripts.json" \
  --out-dir "/duong/dan/Danh_Sach_Kich_Ban"
```

---

### Bước 2: Gọi API HeyGen Tạo Video `A-Roll` (`<STT>_a-roll-<N>.mp4`)

Sử dụng [scripts/render_heygen_aroll.py](./scripts/render_heygen_aroll.py) (hoặc lệnh con `render-aroll` trong `analyze_and_scaffold.py`).
- **Mặc định chạy ở chế độ `DRY-RUN`** (kiểm tra câu thoại `tts_text`, bỏ qua các shot `🎥 QUAY THẬT` và các file đã tồn tại, **không tốn Credit HeyGen**):
```bash
python3 /home/vmiz/.gemini/config/skills/script-aroll-broll-analyzer/scripts/render_heygen_aroll.py \
  "/duong/dan/Danh_Sach_50_Kich_Ban/01_XM01_..."
```
- **Khi đã kiểm tra xong, thêm cờ `--yes` để gọi API HeyGen thật và tải `.mp4` về Thư mục con:**
```bash
python3 /home/vmiz/.gemini/config/skills/script-aroll-broll-analyzer/scripts/render_heygen_aroll.py \
  "/duong/dan/Danh_Sach_50_Kich_Ban/01_XM01_..." --yes
```
*(Hỗ trợ lọc theo kịch bản `--filter-id XM01`, lọc 1 shot lẻ `--shot a-roll-2`, hoặc đổi độ phân giải `--resolution 720p|1080p`).*

---

### Bước 3: Gọi API Muse Tạo Video `B-Roll` Thuần Hình Ảnh (`<STT>_b-roll-<M>.mp4`)

Sử dụng [scripts/render_muse_broll.py](./scripts/render_muse_broll.py) (hoặc lệnh con `render-broll` trong `analyze_and_scaffold.py`):
- **Xem trước danh sách Prompt B-Roll (`--dry-run`):**
```bash
python3 /home/vmiz/.gemini/config/skills/script-aroll-broll-analyzer/scripts/render_muse_broll.py \
  "/duong/dan/Danh_Sach_50_Kich_Ban/01_XM01_..." --dry-run
```
- **Chạy gọi API Muse tạo toàn bộ B-Roll cho 1 kịch bản (chế độ mặc định `image-to-video`: tạo ảnh khung đầu 9:16 qua `muse-image` rồi chuyển động qua `muse-video`, chuẩn hóa H.264 30fps BT.709, xoá tiếng `-an`):**
```bash
python3 /home/vmiz/.gemini/config/skills/script-aroll-broll-analyzer/scripts/render_muse_broll.py \
  "/duong/dan/Danh_Sach_50_Kich_Ban/01_XM01_..." --mode image-to-video
```
- **Hoặc tạo nhanh 1 clip B-Roll lẻ từ câu Prompt bất kỳ:**
```bash
python3 /home/vmiz/.gemini/config/skills/script-aroll-broll-analyzer/scripts/render_muse_broll.py \
  --prompt "Cận cảnh bàn tay doanh nhân ký sổ tay bên cạnh màn hình..." \
  --seconds 4 --aspect-ratio 9:16 -o "/duong/dan/02_b-roll-1.mp4"
```

---

### Bước 4: Chạy Đồng Bộ Cả `A-Roll` + `B-Roll` (`render-all`) & Kiểm Định (`validate`)

```bash
# 1. Xem trước toàn bộ A-Roll (HeyGen) + B-Roll (Muse) của kịch bản XM01 (Dry-run):
python3 /home/vmiz/.gemini/config/skills/script-aroll-broll-analyzer/scripts/analyze_and_scaffold.py \
  render-all "/duong/dan/Danh_Sach_50_Kich_Ban" --filter-id XM01

# 2. Thực thi gọi cả API HeyGen + API Muse cho kịch bản XM01:
python3 /home/vmiz/.gemini/config/skills/script-aroll-broll-analyzer/scripts/analyze_and_scaffold.py \
  render-all "/duong/dan/Danh_Sach_50_Kich_Ban" --filter-id XM01 --yes

# 3. Kiểm tra toàn bộ file media đã đủ trong Thư mục con trước khi đưa vào master-video-edit:
python3 /home/vmiz/.gemini/config/skills/script-aroll-broll-analyzer/scripts/analyze_and_scaffold.py \
  validate "/duong/dan/Danh_Sach_50_Kich_Ban" --check-media
```

---

## 4. Cấu Trúc Thư Mục Con Sau Khi Chạy Đủ Pipeline

```text
📁 <Thu_Muc_Tong>/
 └── 📁 01_XM01_<Ten_Kich_Ban>/
      ├── 📄 00_BANG_PHAN_CANH.md              # Bảng phân cảnh chi tiết (Markdown)
      ├── 📄 00_storyboard_manifest.json       # Bản đồ tổng thể (Thứ tự cảnh, lời thoại, prompt, tên file đích)
      ├── 📄 prompts_heygen_aroll.json         # Payload các cảnh A-Roll gửi API HeyGen
      ├── 📄 prompts_elevenlabs_voice.json     # Payload lời thoại B-Roll gửi API ElevenLabs
      ├── 📄 prompts_muse_veo_broll.json       # Payload Prompt hình B-Roll (không text, không voice) gửi API Muse
      ├── 🎬 01_a-roll-1.mp4                   # Cảnh 01: A-Roll #1 (Quay thật hoặc HeyGen: Hình + Tiếng)
      ├── 🎬 02_b-roll-1.mp4                   # Cảnh 02: B-Roll #1 (Muse API: H.264 9:16 30fps, câm -an, không text)
      ├── 🔊 02_voice-b-roll-1.mp3             # Cảnh 02: Voice-off B-Roll #1 (ElevenLabs)
      ├── 🎬 03_b-roll-2.mp4                   # Cảnh 03: B-Roll #2 (Muse API)
      ├── 🔊 03_voice-b-roll-2.mp3             # Cảnh 03: Voice-off B-Roll #2 (ElevenLabs)
      ├── ...
      └── 🎬 06_a-roll-2.mp4                   # Cảnh 06: A-Roll #2 (HeyGen API: Hình + Tiếng)
```

---

## 5. Tài Liệu & Script Trong Skill
- [scripts/analyze_and_scaffold.py](./scripts/analyze_and_scaffold.py): CLI trung tâm phân tích kịch bản (`from-spec`, `from-json`), chuẩn hóa TTS tiếng Việt (`normalize-tts`), điều phối gọi API (`render-aroll`, `render-broll`, `render-all`), kiểm định (`validate`) và xuất báo cáo (`report`).
- [scripts/render_heygen_aroll.py](./scripts/render_heygen_aroll.py): Script kết nối trực tiếp API HeyGen (`POST /v3/videos` & `/v2/video/generate`), kiểm tra lỗi phát âm số tiếng Việt, hỗ trợ `DRY-RUN` bảo vệ Credit và tải file `<STT>_a-roll-<N>.mp4`.
- [scripts/render_muse_broll.py](./scripts/render_muse_broll.py): Script kết nối trực tiếp API Muse (`muse2api` qua `muse-image` + `muse-video`), tạo B-Roll dọc `9:16` và chuẩn hóa `ffmpeg` (`H.264 30fps BT.709, -an` câm tuyệt đối, `-map_metadata -1`).
- [references/schema-and-rules.md](./references/schema-and-rules.md): Định dạng JSON chuẩn của `00_storyboard_manifest.json` và quy tắc phân tích 3 chế độ tỷ lệ `A-Roll` / `B-Roll`.

<!-- ===== /file: script-aroll-broll-analyzer/SKILL.md ===== -->

<!-- ===== file: script-aroll-broll-analyzer/references/schema-and-rules.md ===== -->

# Schema & Quy Tắc Phân Tích Kịch Bản (`00_storyboard_manifest.json`)

## 1. Cấu Trúc File JSON Đầu Vào (`from-json`) & `00_storyboard_manifest.json`

Khi AI phân tích một hoặc nhiều kịch bản mới từ Brief/Text của người dùng, AI tạo file JSON theo cấu trúc dưới đây rồi truyền vào `scripts/analyze_and_scaffold.py from-json`:

```json
{
  "project_name": "Du_An_Video_AI_Doanh_Nghiep",
  "aspect_ratio": "9:16",
  "resolution": "1080x1920",
  "fps": 30,
  "scripts": [
    {
      "script_id": "KB10",
      "slug": "KB10_Giao_Viec_Di_Ca_Phe_4_Phan_Tram_Token",
      "title": "Giao Việc Trên Máy Tính Rồi Cầm Điện Thoại Đi Cà Phê: Làm 1 Video Tốn Đúng 4% Token",
      "ratio_mode": "balanced_credit_saver",
      "target_duration_sec": 46.0,
      "segments": [
        {
          "type": "a-roll",
          "time_range": "00s – 02.5s",
          "duration_sec": 2.5,
          "beat_name": "1. Hook",
          "display_text": "Ai bảo dùng AI dựng video tự động là tốn tiền mua Token?",
          "tts_text": "Ai bảo dùng AI dựng video tự động là tốn tiền mua Token?",
          "visual_direction": "Avatar người nói nhìn thẳng ống kính đặt câu hỏi phản biện ấn tượng.",
          "keywords": ["AI BẢO TỐN TOKEN?"],
          "post_fx_note": "Gắn chữ Hook AI BẢO DỰNG VIDEO TỰ ĐỘNG TỐN TOKEN?"
        },
        {
          "type": "b-roll",
          "time_range": "02.5s – 05.0s",
          "duration_sec": 2.5,
          "beat_name": "1. Hook (Cảnh trám)",
          "display_text": "Một clip 5 phút mình làm chỉ hết đúng 4% hạn mức tuần thôi anh em ạ!",
          "tts_text": "Một clip năm phút mình làm chỉ hết đúng bốn phần trăm hạn mức tuần thôi anh em ạ!",
          "broll_prompt": "Cảnh một doanh nhân ngồi thư thái ở quán cà phê ngập nắng, một tay nâng tách espresso, một tay lướt nhẹ điện thoại.",
          "keywords": ["4% HẠN MỨC TUẦN"],
          "post_fx_note": "Đè thanh tiến trình USAGE: 4% màu xanh lá"
        },
        {
          "type": "a-roll",
          "time_range": "05.0s – 08.5s",
          "duration_sec": 3.5,
          "beat_name": "2. Story (Dẫn nỗi đau)",
          "display_text": "Sở dĩ nhiều người dùng AI 2 ngày đã báo hết sạch dung lượng là vì:",
          "tts_text": "Sở dĩ nhiều người dùng AI hai ngày đã báo hết sạch dung lượng là vì:",
          "visual_direction": "Avatar người nói giải thích nguyên nhân cốt lõi khiến người dùng tốn Token.",
          "keywords": ["2 NGÀY HẾT DUNG LƯỢNG"],
          "post_fx_note": "Phụ đề nhấn 2 NGÀY HẾT SẠCH DUNG LƯỢNG"
        }
      ]
    }
  ]
}
```

---

## 2. Tự Động Đánh Số Kép Khi Chạy `analyze_and_scaffold.py`

Khi chạy qua `scripts/analyze_and_scaffold.py`, mỗi phần tử trong `segments` sẽ được tự động tính toán và bổ sung các trường định danh chuẩn cho AI:

- **`seq_index`**: Số nguyên `1, 2, 3, 4...` (Thứ tự xuất hiện trên Timeline).
- **`seq_prefix`**: Chuỗi 2 chữ số `"01"`, `"02"`, `"03"`, `"04"`...
- **`role_index`**: Số thứ tự riêng trong nhóm `a-roll` (`1, 2, 3...`) hoặc trong nhóm `b-roll` (`1, 2, 3...`).
- **`role_id`**: `"a-roll-1"`, `"b-roll-1"`, `"a-roll-2"`, `"b-roll-2"`...
- **`files`**:
  - Nếu `type == "a-roll"`:
    - `video_file`: `"01_a-roll-1.mp4"` *(Nguồn: API HeyGen — đã có cả hình người nói lẫn tiếng)*
    - `voice_file`: `null` *(Không gọi ElevenLabs vì đã dùng tiếng trong clip HeyGen)*
  - Nếu `type == "b-roll"`:
    - `video_file`: `"02_b-roll-1.mp4"` *(Nguồn: API MUSE / MCP Veo 3 — chỉ hình minh họa, KHÔNG VOICE, KHÔNG TEXT)*
    - `voice_file`: `"02_voice-b-roll-1.mp3"` *(Nguồn: API ElevenLabs — đi cặp 1-1 với `02_b-roll-1.mp4`)*

---

## 3. Ba Chế Độ Phân Bổ `A-Roll` và `B-Roll` Linh Hoạt

1. **Chế độ Nhiều A-Roll – Ít B-Roll (`aroll_heavy`):**
   - Dùng khi người dùng yêu cầu kịch bản chia sẻ cá nhân, tâm sự, kể chuyện trực diện.
   - Ví dụ chuỗi cảnh: `01_a-roll-1` ➔ `02_a-roll-2` ➔ `03_b-roll-1` ➔ `04_a-roll-3` ➔ `05_b-roll-2` ➔ `06_a-roll-4`.
2. **Chế độ Cân Bằng & Tối Ưu Credit HeyGen (`balanced_credit_saver`):**
   - Dùng cho các kịch bản giải pháp doanh nghiệp, chia sẻ kiến thức thực chiến.
   - Ví dụ chuỗi cảnh: `01_a-roll-1` ➔ `02_b-roll-1` ➔ `03_a-roll-2` ➔ `04_b-roll-2` ➔ `05_b-roll-3` ➔ `06_a-roll-3` ➔ `07_b-roll-4` ... ➔ `12_a-roll-4`.
3. **Chế độ Ít A-Roll – Nhiều B-Roll (`broll_heavy`):**
   - Dùng cho kịch bản review món ăn F&B, bất động sản, demo phần mềm/sản phẩm.
   - Ví dụ chuỗi cảnh: `01_b-roll-1` ➔ `02_a-roll-1` ➔ `03_b-roll-2` ➔ `04_b-roll-3` ➔ `05_b-roll-4` ➔ `06_b-roll-5` ➔ `07_a-roll-2`.

<!-- ===== /file: script-aroll-broll-analyzer/references/schema-and-rules.md ===== -->
