@echo off
chcp 65001 >nul

echo 🚀 啟動本地MACD監控系統（無需Docker）
echo ====================================================

REM 檢查Python是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安裝，請先安裝Python 3.9+
    pause
    exit /b 1
)

REM 安裝依賴
echo 📦 檢查並安裝依賴...
pip install -r requirements.txt >nul 2>&1

REM 創建配置文件（如果不存在）
if not exist monitor_config.json (
    echo 📝 創建默認配置文件...
    copy monitor_config.example.json monitor_config.json >nul 2>&1
)

REM 測試系統
echo 🧪 測試系統配置...
python start_cloud_monitor.py --test

echo.
echo ✅ 測試完成！
echo.

REM 詢問是否要啟動監控
set /p choice="是否要啟動監控系統？(y/n): "
if /i "%choice%"=="y" (
    echo 🚀 啟動監控系統...
    echo 按 Ctrl+C 停止監控
    echo.
    python start_cloud_monitor.py
) else (
    echo �� 未啟動監控系統
)

pause 