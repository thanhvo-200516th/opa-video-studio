# HƯỚNG DẪN VẬN HÀNH HỆ THỐNG ĐĂNG BÀI TỰ ĐỘNG CHẠY NGẦM (`DBTD`)

> **Thư mục gốc:** `/media/vmiz/Over Powers/THÀNH V/THCN thành/THUONG_HIEU_CA_NHAN_THANH_90_NGAY/DBTD`

---

## 1. CẤU TRÚC THƯ MỤC ĐÃ ĐƯỢC KHỞI TẠO SẴN TRONG `DBTD`

Toàn bộ **48 bài lịch chính thức (12 tuần)**, **3 bài ghim** và **12 bài dự phòng/case study** đã được tạo sẵn thư mục theo đúng ngày và mã bài:

- `00_PINNED_VIDEOS/` (`20261025_PIN01`, `20261025_PIN02`, `20261025_PIN03`)
- `01_TUAN_01_2610_3110/`
  - `20261026_C001/` (Thứ Hai 26/10/2026)
  - `20261027_C022/` (Thứ Ba 27/10/2026)
  - `20261029_C040/` (Thứ Năm 29/10/2026)
  - `20261031_C055/` (Thứ Bảy 31/10/2026)
- `02_TUAN_02_0211_0711/` ... đến `12_TUAN_12_1101_1601/`
- `13_DU_PHONG_VA_CASE_STUDY/` (`DUPHONG_C018` ... `DUPHONG_C060`)
- `_he_thong_bot/` (Chứa bộ điều khiển trình duyệt chạy ngầm 100%)

> 💡 **Mẹo:** Trong mỗi thư mục bài đăng (ví dụ `20261026_C001`), đã có sẵn file **`THONG_TIN_BAI_DANG.txt`** ghi rõ tên file cần đặt và toàn bộ Caption TikTok + Bài đăng Facebook của đúng ngày hôm đó.

---

## 2. QUY TẮC ĐẶT TÊN FILE CỐ ĐỊNH ĐỂ BOT TỰ NHẬN DIỆN

Khi xuất video hoặc ảnh xong cho ngày nào, bạn chỉ cần bỏ vào thư mục của ngày đó theo công thức:

- **Video chính (TikTok / FB Reels / Fanpage):** `[Mã_Thư_Mục]_VIDEO.mp4`
  - Ví dụ ngày 26/10 (`C001`): `20261026_C001_VIDEO.mp4`
- **Ảnh bìa Video (Thumbnail):** `[Mã_Thư_Mục]_THUMB.png` (hoặc `.jpg`)
  - Ví dụ: `20261026_C001_THUMB.png`
- **Ảnh bài viết Facebook / Fanpage (1 ảnh hoặc nhiều ảnh):** `[Mã_Thư_Mục]_IMG_01.png`, `[Mã_Thư_Mục]_IMG_02.png`...
  - Ví dụ: `20261026_C001_IMG_01.png`, `20261026_C001_IMG_02.png`

---

## 3. CÁCH CHẠY NGẦM 100% KHÔNG BẬT CỬA SỔ TRÌNH DUYỆT

Hệ thống sử dụng **2 lớp ẩn cửa sổ**:
1. **Lớp trình duyệt (`--headless=new`):** Chrome tự mở trang, gắn file và bấm nút Đăng hoàn toàn trong bộ nhớ RAM mà không vẽ giao diện ra màn hình.
2. **Lớp hệ điều hành (`2_CHAY_NGAM_KHONG_CUA_SO.vbs` với cờ `vbHide = 0`):** Ẩn luôn cả cửa sổ đen Command Prompt (CMD). Bạn đang dựng Premiere/After Effects sẽ không bao giờ bị một cửa sổ nào nhảy lên làm phiền.

### 3 Bước kích hoạt:
1. **Bước 1 (Chỉ làm 1 lần duy nhất):** Mở thư mục `_he_thong_bot`, nhấp đúp vào **`1_DANG_NHAP_LAN_DAU.bat`**.
   - Một cửa sổ Chrome riêng sẽ hiện lên để bạn đăng nhập sẵn **TikTok** và **Facebook**.
   - Đăng nhập xong, bạn tắt cửa sổ Chrome đó đi. Toàn bộ phiên đăng nhập đã được lưu cứng vào `_he_thong_bot/browser_profile`.
2. **Bước 2:** Mở file `_he_thong_bot/config.json`, điền đường dẫn URL Fanpage của bạn vào dòng `"fanpageUrl"`.
3. **Bước 3 (Bật tự động chạy ngầm):** Nhấp đúp vào **`3_CAI_LICH_TU_DONG_WINDOWS.bat`**.
   - Windows sẽ tự động kiểm tra lịch ngầm mỗi 15 phút và tự đăng bài khi tới đúng Ngày + Giờ mà không hiện bất kỳ cửa sổ nào.
   - Mọi kết quả đều được ghi lại trong `_he_thong_bot/logs/autopost.log`.

---

## 4. CẬP NHẬT LÊN GOOGLE SHEET CỦA BẠN

Trong thư mục `DBTD` đã có sẵn 2 file bảng tính đã điền đủ 60 kịch bản & caption:
1. **`He-thong-content-ca-nhan-Thanh-AutoPost.xlsx`**: File Excel đầy đủ 9 tab (đã sửa lại tab `Lịch sản xuất` chuẩn 4 Pillar và thêm tab mới **`Lịch Đăng Tự Động`**).
2. **`Lich_Dang_Tu_Dong_Import_GGSheet.csv`**: Bạn có thể mở Google Sheet hiện tại của bạn $\rightarrow$ Bấm **Tệp (File) > Nhập (Import) > Tải lên (Upload)** $\rightarrow$ Chọn file CSV này và chọn *"Chèn trang tính mới (Insert new sheet)"* là có ngay tab `Lịch Đăng Tự Động` trên Google Sheet!
