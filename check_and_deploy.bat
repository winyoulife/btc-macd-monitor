@echo off
echo.
echo 🔍 檢查系統環境...
echo ====================================================

REM 檢查Heroku CLI
echo 檢查 Heroku CLI...
heroku --version 2>nul
if errorlevel 1 (
    echo ❌ Heroku CLI 未安裝或未正確配置
    goto :error
) else (
    echo ✅ Heroku CLI 正常
)

REM 檢查Heroku登錄
echo 檢查 Heroku 登錄狀態...
heroku whoami 2>nul
if errorlevel 1 (
    echo ❌ 未登錄 Heroku
    echo 請執行: heroku login
    goto :error
) else (
    echo ✅ Heroku 已登錄
)

REM 檢查Git
echo 檢查 Git...
git --version 2>nul
if errorlevel 1 (
    echo ❌ Git 未安裝
    echo.
    echo 🎯 您有兩個選擇：
    echo.
    echo 選擇1：安裝Git（推薦）
    echo   1. 下載：https://git-scm.com/download/win
    echo   2. 安裝後重啟命令提示字元
    echo   3. 再次執行此腳本
    echo.
    echo 選擇2：手動部署
    echo   1. 訪問：https://dashboard.heroku.com
    echo   2. 點擊 "New" -> "Create new app"
    echo   3. 輸入應用名稱
    echo   4. 選擇 "Deploy" 頁籤
    echo   5. 連接GitHub或使用Container Registry
    echo.
    goto :error
) else (
    echo ✅ Git 已安裝
    echo.
    echo 🚀 一切就緒！可以開始自動部署...
    echo.
    pause
    goto :auto_deploy
)

:auto_deploy
echo 🚀 開始自動部署...
REM 這裡可以添加自動部署邏輯
echo 請告訴我您想要的應用名稱，然後我們開始部署！
goto :end

:error
echo.
echo ⚠️  請解決上述問題後再次嘗試
goto :end

:end
pause 