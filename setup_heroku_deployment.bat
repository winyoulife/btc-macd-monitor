@echo off
chcp 65001 >nul

echo 🚀 Heroku 部署完整設置
echo ====================================================

REM 檢查Heroku CLI
heroku --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Heroku CLI未安裝
    echo 請先安裝 Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
    pause
    exit /b 1
)

echo ✅ Heroku CLI已安裝

REM 檢查是否登錄
heroku whoami >nul 2>&1
if errorlevel 1 (
    echo ❌ 請先登錄 Heroku
    echo 執行: heroku login
    pause
    exit /b 1
)

echo ✅ Heroku已登錄

REM 檢查Git
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git未安裝
    echo.
    echo 請安裝Git：
    echo https://git-scm.com/download/win
    echo.
    echo 或者我們可以手動創建部署包...
    set /p choice="是否要手動創建部署包？(y/n): "
    if /i "%choice%"=="y" (
        goto :manual_deploy
    ) else (
        pause
        exit /b 1
    )
)

echo ✅ Git已安裝

:git_deploy
REM 初始化Git（如果需要）
if not exist .git (
    echo 📝 初始化Git倉庫...
    git init
    git add .
    git commit -m "Initial commit"
)

REM 設置應用名稱
set /p APP_NAME="請輸入Heroku應用名稱（或按Enter使用默認名稱）: "
if "%APP_NAME%"=="" set APP_NAME=btc-macd-monitor-%RANDOM%

echo 📝 應用名稱: %APP_NAME%

REM 創建Heroku應用
echo 🆕 創建Heroku應用...
heroku create %APP_NAME% --region us

REM 設置容器部署
echo 🐳 設置容器部署...
heroku stack:set container -a %APP_NAME%

REM 設置環境變量
echo ⚙️  設置環境變數...
echo.
echo 重要：請設置您的Telegram Bot資訊
echo.
set /p BOT_TOKEN="請輸入您的Telegram Bot Token: "
set /p CHAT_ID="請輸入您的Telegram Chat ID: "

if not "%BOT_TOKEN%"=="" (
    heroku config:set TELEGRAM_BOT_TOKEN=%BOT_TOKEN% -a %APP_NAME%
)

if not "%CHAT_ID%"=="" (
    heroku config:set TELEGRAM_CHAT_ID=%CHAT_ID% -a %APP_NAME%
)

REM 部署
echo 🚢 開始部署...
git add .
git commit -m "Deploy to Heroku" --allow-empty
heroku git:remote -a %APP_NAME%
git push heroku main

goto :deploy_complete

:manual_deploy
echo 📦 手動部署模式
echo.
echo 請按照以下步驟操作：
echo.
echo 1. 訪問 Heroku Dashboard: https://dashboard.heroku.com
echo 2. 點擊 "New" -> "Create new app"
echo 3. 輸入應用名稱
echo 4. 選擇 "Container Registry" 部署方式
echo 5. 按照網頁上的指示進行部署
echo.
goto :end

:deploy_complete
echo.
echo ✅ 部署完成！
echo.
echo 🔗 應用資訊：
echo    應用名稱: %APP_NAME%
echo    應用URL: https://%APP_NAME%.herokuapp.com
echo    健康檢查: https://%APP_NAME%.herokuapp.com/health
echo    系統狀態: https://%APP_NAME%.herokuapp.com/status
echo.
echo 📋 常用命令：
echo    查看日誌: heroku logs --tail -a %APP_NAME%
echo    重啟應用: heroku restart -a %APP_NAME%
echo    打開應用: heroku open -a %APP_NAME%
echo.
echo 🎉 您的MACD監控系統現在已經在雲端24/7運行！

:end
pause 