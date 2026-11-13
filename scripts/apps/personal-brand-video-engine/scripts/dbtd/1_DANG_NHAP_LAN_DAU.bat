@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ====================================================================
echo BƯỚC 1: CÀI ĐẶT THƯ VIỆN (CHỈ CHẠY LẦN ĐẦU) VÀ MỞ CỬA SỔ ĐĂNG NHẬP
echo ====================================================================
if not exist "node_modules\playwright" (
    echo Đang cài đặt bộ điều khiển trình duyệt Playwright...
    call npm install
)
echo.
echo Đang mở trình duyệt Chrome riêng của Bot...
echo Hãy đăng nhập tài khoản TikTok và Facebook của bạn trên cửa sổ vừa bật.
echo Sau khi đăng nhập xong, hãy ĐÓNG cửa sổ trình duyệt đó lại để lưu phiên!
echo.
node bot_autopost.mjs --login
echo.
echo Hoàn tất lưu phiên đăng nhập! Từ giờ các lần đăng bài sẽ chạy ngầm 100%%.
pause
