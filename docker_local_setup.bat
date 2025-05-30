@echo off
chcp 65001 >nul

echo 🐳 Docker 本地部署設置
echo ====================================================

REM 檢查Docker是否安裝
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker未安裝
    echo.
    echo 請安裝Docker Desktop：
    echo https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

echo ✅ Docker已安裝

REM 檢查Docker是否運行
docker ps >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker未啟動
    echo 請啟動Docker Desktop應用程式
    pause
    exit /b 1
)

echo ✅ Docker正在運行

REM 創建配置文件（如果不存在）
if not exist monitor_config.json (
    echo 📝 創建默認配置文件...
    if exist monitor_config.example.json (
        copy monitor_config.example.json monitor_config.json >nul 2>&1
    ) else (
        echo {> monitor_config.json
        echo   "monitoring": {>> monitor_config.json
        echo     "symbols": ["btctwd"],>> monitor_config.json
        echo     "check_interval": 60,>> monitor_config.json
        echo     "primary_period": 15>> monitor_config.json
        echo   }>> monitor_config.json
        echo }>> monitor_config.json
    )
)

echo 📦 構建Docker鏡像...
docker build -t macd-monitor .

if errorlevel 1 (
    echo ❌ 構建失敗
    pause
    exit /b 1
)

echo ✅ 鏡像構建成功

echo 🚀 啟動容器...
docker run -d -p 8080:8080 --name macd-monitor macd-monitor

if errorlevel 1 (
    echo ❌ 容器啟動失敗
    echo 可能是容器已存在，嘗試刪除舊容器...
    docker rm -f macd-monitor >nul 2>&1
    docker run -d -p 8080:8080 --name macd-monitor macd-monitor
)

echo.
echo ✅ 容器啟動成功！
echo.
echo 🔗 監控面板：
echo    健康檢查: http://localhost:8080/health
echo    系統狀態: http://localhost:8080/status
echo    配置檢查: http://localhost:8080/config
echo.
echo 📋 常用命令：
echo    查看日誌: docker logs -f macd-monitor
echo    停止容器: docker stop macd-monitor
echo    刪除容器: docker rm -f macd-monitor
echo.

pause 