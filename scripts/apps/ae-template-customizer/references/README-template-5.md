# Ca mẫu nhánh B: sửa template mua về "template 5.aep"

Bốn script do một phiên agent khác viết (23–26/10/2026) khi sửa template thương mại 13 cảnh `template 5.aep` thành video quảng cáo OPA Agent. Kết quả là `OPA_Agent_Promo_2026.aep`.
- Gói giữ **nguyên nội dung** bốn script để tham khảo.
- Script chưa được chạy lại để kiểm khi đóng gói.
- Chưa có ghi nhận Minh đã duyệt video của ca này.

| Script | Việc | Đầu vào cứng trong code |
|---|---|---|
| `parse_aep_timings.py` | đọc báo cáo cấu trúc template, tính giây và khung toàn cục của mọi cảnh, comp con | `C:\Users\Public\OPA-AE-20261021\T5-REPORT-DECODED.txt` |
| `customize_template_assets.jsx` | nạp chân dung, logo, thẻ UI, nhạc; đổi bảng màu; thay chữ tiếng Việt; sửa Range Selector | `/media/vmiz/Over Powers/video AE/template intro/video edit teamplate/template 5.aep`, thư mục `OPA_T5_Assets`, file nhạc trên ổ F |
| `prepare_sfx_pro.py` | chọn 78 cue SFX bộ uisfx-themes, đổi WAV 48 kHz 24-bit, `volume=-4.5dB,lowpass=11000`, tính startTime căn đỉnh | danh sách cue và mốc cảnh của template 5, kho SFX ổ D, thư mục ra ổ F |
| `generate_ae_sfx_jsx.py` | sinh JSX đưa SFX vào comp `00_OPA_SFX_Master` và từng cảnh, gain −6 … −9,5 dB | JSON cue của bước trên, đường dẫn template 5 |

## Phải sửa trước khi dùng cho dự án khác

1. **Đường dẫn cứng** ở đầu mỗi script: đổi sang dự án mới.
2. **Chạy trên bản sao, trong phiên AE riêng** (sổ tay mục 3). Hai file JSX được viết để chạy trong phiên AE đang mở:
   - lưu đè lên chính `template 5.aep`;
   - JSX sinh ra gọi `openInViewer()` trước bước lưu. Hàm này cần giao diện, nên xóa nó khi chạy headless.
3. **`customize_template_assets.jsx` bỏ qua lỗi im lặng** (`catch (err) {}`). Thêm dòng ghi lỗi ra file báo cáo trước khi dùng.
4. **Báo cáo cấu trúc** mà `parse_aep_timings.py` đọc do hai file không có trong gói tạo ra: `inspect_t5_aepx.jsx` và `decode_aepx.py`, cùng ở `C:\Users\Public\OPA-AE-20261021`.
   - Hai file này giấu báo cáo vào comment của file .aepx, vì phiên chạy của họ không ghi file được.
   - Trong phiên riêng thì ghi thẳng ra file JSON, như `references/template-audit/scripts/export-projects.jsx`.
5. **Mức âm** (−4,5 dB trước, gain −6 … −9,5 dB, nhạc −8 dB) là số đặt cho riêng bộ âm của ca này, chưa đo trên bản xuất. Dùng làm điểm xuất phát, rồi đo và master theo sổ tay mục 9.
6. **Không dùng `run_ae_script.py` của ca này.** File đó đẩy script vào phiên AE đang mở bằng cách đổi tiến trình cha (parent PID), trái với luật không chạy vào phiên AE của Minh.
7. **Lưu:** đổi `app.project.save(projFile)` thành `app.project.save()` trên bản sao đã mở.
8. **Viết lại phần riêng của template 5:** tên comp, vòng lặp 13 cảnh, `SCENE_STARTS`, danh sách 78 cue, thông số 3840×2160 / 30 fps / 55,5 s.

## Chỗ làm trái luật của skill (sửa trước khi dùng lại)

| Chỗ | Trái luật nào | Sửa |
|---|---|---|
| `customize_template_assets.jsx` nhập thẳng file MP3 nhạc ngoài (`atlasaudio-upbeat-corporate-617614.mp3`) | sổ tay 9.3, 9.6: nhạc phải là WAV 48 kHz; video OPA tự tổng hợp nhạc | đổi sang WAV; video OPA dùng nhạc tự tổng hợp hoặc hỏi Minh |
| Font `BeVietnamPro-Black` | ngoài bộ font duyệt của OPA | dùng ExtraBold, hoặc hỏi Minh thêm font vào bộ |
| Vài dòng chữ mở đầu bằng chữ thường | luật viết hoa chữ cái đầu mọi dòng (URL được miễn) | viết hoa chữ cái đầu |
| Màu #00E0FF, #05122E và giữ `Buttons_Glow_Color` | 5 màu OPA, không glow | đổi về 5 màu OPA, tắt glow, trừ khi Minh duyệt giữ |
| `prepare_sfx_pro.py` đổi WAV bằng `-ac 2` | sổ tay 9.2: `-ac 2` hạ mỗi kênh 3 dB | giữ số kênh gốc, hoặc nhân đôi kênh nguyên mức |
| `prepare_sfx_pro.py` lấy M từ CSV thay vì đo lại file WAV đã xử lý | gain phải tính trên file thật đưa vào AE (sổ tay 9.2) | đo lại sau khi đổi WAV và lọc |
| Nhiều khối `catch` rỗng, cả trong JSX được sinh ra | mọi lỗi phải ghi vào báo cáo (sổ tay 3.4) | ghi lỗi ra file |
