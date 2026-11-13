@echo off
chcp 65001 >nul
set "VBS_PATH=%~dp02_CHAY_NGAM_KHONG_CUA_SO.vbs"
echo ====================================================================
echo ĐĂNG KÝ TÁC VỤ CHẠY NGẦM TỰ ĐỘNG TRÊN WINDOWS (TASK SCHEDULER)
echo ====================================================================
schtasks /Create /SC MINUTE /MO 15 /TN "Thanh_DBTD_AutoPost" /TR "wscript.exe \"%VBS_PATH%\"" /F
echo.
echo ✅ Đã cài đặt lịch chạy ngầm tự động mỗi 15 phút (Task: Thanh_DBTD_AutoPost).
echo Khi tới đúng Ngày + Giờ đăng bài, Bot sẽ tự động chạy ngầm 100%% mà KHÔNG bật bất kỳ cửa sổ nào lên màn hình!
pause
