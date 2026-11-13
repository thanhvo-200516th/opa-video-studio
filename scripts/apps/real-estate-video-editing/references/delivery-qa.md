# Kiểm tra trước khi giao video

1. **Lời và chữ:** Nghe lại âm đầu của từng từ được nhấn và so với frame đầu tiên có chữ. Xem frame ngay trước âm, lúc âm bắt đầu, 0,2 giây sau và lúc fade out. Không hiện chữ sớm, không đợi người dẫn nói xong cụm mới hiện. Từ trước phải còn trên màn hình khi từ sau vào; toàn cụm ở lại đủ đọc và fade mềm, không nhấp nháy. Kiểm tra dấu, số tiền và địa danh.
2. **Ảnh và safe area:** Xem từng lần đổi ảnh ở kích thước điện thoại. Có ảnh khác nhau phù hợp các ý thoại; ảnh đủ rõ giữa, mép mờ mềm, chuyển không giật, không che người/mặt/chữ. Không có chữ “Hình ảnh minh hoạ”. Không có chữ/ảnh chạm vùng crop phía trên hoặc hai mép.
3. **Tiếng:** Xác nhận video gốc có audio stream và file cuối vẫn có AAC stream. Giải mã file cuối, đo âm lượng/RMS; nghe những đoạn đầu, giữa và cuối hoặc so dạng sóng tiếng gốc với đầu ra để chắc giọng gốc được giữ. SFX chỉ là lớp phụ, không nuốt chữ, không clipping.
4. **Hình:** `ffprobe` phải cho thấy 1440×2560, H.264, thời lượng đúng với source và frame rate hợp lý. Xem frame đại diện để kiểm tra lõi chữ gradient xanh dương/xanh lá rõ trên background, chữ phụ vàng, glow nhẹ thực sự có nhưng không lóa, không viền đen thô, motion fade/nhích mượt. Không dựa chỉ vào tên file “2K”.
5. **Giao:** Cung cấp MP4 cuối cùng; khi chỉnh vòng sau, thay đúng video trước để người dùng không phải phân biệt nhiều bản. Nêu ngắn gọn những thay đổi và kết quả kiểm tra tiếng.

## Ví dụ nhịp đã duyệt (chỉ dùng cho footage này)

| Tiếng nói | Chữ màn hình | Bắt đầu |
| --- | --- | ---: |
| 5 phút di chuyển từ dự án | 5 PHÚT / di chuyển từ dự án | 1.52 / 1.90 s |
| không khí biển Hạ Long mỗi ngày | KHÔNG KHÍ BIỂN / Hạ Long mỗi ngày | 4.54 / 5.06 s |
| một căn hộ không chỉ để ở | MỘT CĂN HỘ / không chỉ để ở | 6.96 / 7.42 s |
| tận hưởng cuộc sống | TẬN HƯỞNG / cuộc sống | 8.86 / 9.28 s |

Lấy mốc từng từ từ nguồn mới khi dựng footage khác. Các con số trên không phải timing mặc định cho mọi clip.
