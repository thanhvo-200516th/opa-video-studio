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
