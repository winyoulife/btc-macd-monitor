@echo off
chcp 65001 >nul

REM Heroku 部署腳本 (Windows版本)
echo 🚀 開始部署到 Heroku...

REM 檢查是否已登錄 Heroku
heroku whoami >nul 2>&1
if errorlevel 1 (
    echo ❌ 請先登錄 Heroku: heroku login
    pause
    exit /b 1
)

REM 應用名稱
set APP_NAME=%1
if "%APP_NAME%"=="" set APP_NAME=btc-macd-monitor

echo 📝 應用名稱: %APP_NAME%

REM 創建 Heroku 應用（如果不存在）
heroku apps:info %APP_NAME% >nul 2>&1
if errorlevel 1 (
    echo 🆕 創建新的 Heroku 應用...
    heroku create %APP_NAME% --region us
)

REM 設置 Heroku stack 為 container
echo 🐳 設置容器部署...
heroku stack:set container -a %APP_NAME%

REM 設置環境變量
echo ⚙️  設置環境變量...
echo 請在 Heroku Dashboard 或使用以下命令設置環境變量：
echo.
echo heroku config:set TELEGRAM_BOT_TOKEN=your_bot_token -a %APP_NAME%
echo heroku config:set TELEGRAM_CHAT_ID=your_chat_id -a %APP_NAME%
echo.

REM 部署
echo 🚢 開始部署...
git add -A
git commit -m "Deploy cloud monitor to Heroku"
git push heroku main

REM 啟動應用
echo ⚡ 啟動應用...
heroku ps:scale web=1 -a %APP_NAME%

REM 顯示應用信息
echo ✅ 部署完成！
echo.
echo 🔗 應用URL: https://%APP_NAME%.herokuapp.com
echo 📊 健康檢查: https://%APP_NAME%.herokuapp.com/health
echo 📈 狀態檢查: https://%APP_NAME%.herokuapp.com/status
echo.
echo 📝 查看日誌: heroku logs --tail -a %APP_NAME%
echo 🔧 管理應用: heroku open -a %APP_NAME%

pause 