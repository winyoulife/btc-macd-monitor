@echo off
chcp 65001 >nul
echo ====================================================
echo BTC MACD 雲端監控系統 - 專案備份腳本
echo ====================================================
echo.

:: 設定變數
set BACKUP_BASE=C:\BTC_MACD_BACKUP
set BACKUP_DATE=%date:~0,4%-%date:~5,2%-%date:~8,2%
set BACKUP_DIR=%BACKUP_BASE%\%BACKUP_DATE%
set SOURCE_DIR=%cd%

echo 📁 來源目錄: %SOURCE_DIR%
echo 💾 備份目錄: %BACKUP_DIR%
echo.

:: 創建備份資料夾
echo ⚡ 創建備份資料夾...
if not exist "%BACKUP_BASE%" mkdir "%BACKUP_BASE%"
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

:: 複製所有檔案
echo 📋 開始複製檔案...
echo    - 複製核心程式檔案...
xcopy "*.py" "%BACKUP_DIR%\" /Y >nul
echo    - 複製配置檔案...
xcopy "*.json" "%BACKUP_DIR%\" /Y >nul
xcopy "*.txt" "%BACKUP_DIR%\" /Y >nul
echo    - 複製文檔檔案...
xcopy "*.md" "%BACKUP_DIR%\" /Y >nul
echo    - 複製批次腳本...
xcopy "*.bat" "%BACKUP_DIR%\" /Y >nul
echo    - 複製部署檔案...
xcopy "Dockerfile" "%BACKUP_DIR%\" /Y >nul 2>nul
xcopy "docker-compose.yml" "%BACKUP_DIR%\" /Y >nul 2>nul
xcopy "render.yaml" "%BACKUP_DIR%\" /Y >nul 2>nul
xcopy "heroku.yml" "%BACKUP_DIR%\" /Y >nul 2>nul
echo    - 複製 Git 記錄...
if exist ".git" xcopy ".git" "%BACKUP_DIR%\.git\" /E /I /Y >nul 2>nul

:: 檢查重要檔案
echo.
echo ✅ 檢查重要檔案是否已備份:
call :check_file "cloud_monitor.py"
call :check_file "health_server.py"
call :check_file "start_cloud_monitor.py"
call :check_file "telegram_notifier.py"
call :check_file "requirements.txt"
call :check_file "monitor_config.json"
call :check_file "PROJECT_BACKUP_README.md"
call :check_file "CONVERSATION_HISTORY.md"
call :check_file "HOW_TO_BACKUP_AND_RESTORE.md"

:: 創建備份資訊檔案
echo.
echo 📝 創建備份資訊檔案...
echo 備份資訊 > "%BACKUP_DIR%\BACKUP_INFO.txt"
echo ======== >> "%BACKUP_DIR%\BACKUP_INFO.txt"
echo 備份日期: %date% %time% >> "%BACKUP_DIR%\BACKUP_INFO.txt"
echo 來源目錄: %SOURCE_DIR% >> "%BACKUP_DIR%\BACKUP_INFO.txt"
echo 備份目錄: %BACKUP_DIR% >> "%BACKUP_DIR%\BACKUP_INFO.txt"
echo 作業系統: %OS% >> "%BACKUP_DIR%\BACKUP_INFO.txt"
echo 電腦名稱: %COMPUTERNAME% >> "%BACKUP_DIR%\BACKUP_INFO.txt"
echo 使用者名稱: %USERNAME% >> "%BACKUP_DIR%\BACKUP_INFO.txt"
echo. >> "%BACKUP_DIR%\BACKUP_INFO.txt"
echo 重要檔案清單: >> "%BACKUP_DIR%\BACKUP_INFO.txt"
dir "%BACKUP_DIR%\*.py" /B >> "%BACKUP_DIR%\BACKUP_INFO.txt" 2>nul
dir "%BACKUP_DIR%\*.md" /B >> "%BACKUP_DIR%\BACKUP_INFO.txt" 2>nul
dir "%BACKUP_DIR%\*.json" /B >> "%BACKUP_DIR%\BACKUP_INFO.txt" 2>nul

:: 顯示統計資訊
echo.
echo 📊 備份統計:
for /f %%i in ('dir "%BACKUP_DIR%\*.py" /b 2^>nul ^| find /c /v ""') do echo    Python 檔案: %%i 個
for /f %%i in ('dir "%BACKUP_DIR%\*.md" /b 2^>nul ^| find /c /v ""') do echo    文檔檔案: %%i 個
for /f %%i in ('dir "%BACKUP_DIR%\*.json" /b 2^>nul ^| find /c /v ""') do echo    配置檔案: %%i 個
for /f %%i in ('dir "%BACKUP_DIR%\*.bat" /b 2^>nul ^| find /c /v ""') do echo    批次腳本: %%i 個

echo.
echo ✨ 備份完成！
echo.
echo 📍 備份位置: %BACKUP_DIR%
echo 📚 重要文檔:
echo    - PROJECT_BACKUP_README.md     (專案總覽)
echo    - CONVERSATION_HISTORY.md      (對話記錄)
echo    - HOW_TO_BACKUP_AND_RESTORE.md (備份指南)
echo.
echo 💡 下次要恢復專案時:
echo    1. 複製 %BACKUP_DIR% 到新位置
echo    2. 閱讀 HOW_TO_BACKUP_AND_RESTORE.md
echo    3. 執行 pip install -r requirements.txt
echo    4. 運行 python quick_macd_test.py 測試
echo.
echo 🔍 要檢視備份檔案嗎? (Y/N)
set /p choice=請選擇: 
if /i "%choice%"=="Y" explorer "%BACKUP_DIR%"

echo.
echo ✅ 備份作業完成！按任意鍵結束...
pause >nul
exit /b 0

:: 檢查檔案是否存在的函數
:check_file
if exist "%BACKUP_DIR%\%~1" (
    echo    ✓ %~1
) else (
    echo    ✗ %~1 [缺失]
)
goto :eof 