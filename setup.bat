@echo off
chcp 65001
echo ========================================
echo  BTC/TWD MACD 交易信號分析系統
echo  環境設定腳本
echo ========================================
echo.

echo [1/4] 檢查Python版本...
python --version
if %errorlevel% neq 0 (
    echo 錯誤: 未找到Python，請先安裝Python 3.8或更高版本
    echo 下載地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo [2/4] 升級pip...
python -m pip install --upgrade pip

echo.
echo [3/4] 安裝依賴套件...
pip install -r requirements.txt

echo.
echo [4/4] 檢查安裝結果...
python -c "import requests, pandas, numpy, matplotlib, telegram; print('所有依賴套件安裝成功！')"

echo.
echo ========================================
echo  設定完成！
echo ========================================
echo.
echo 下一步設定Telegram Bot:
echo 1. 在Telegram中搜尋 @BotFather
echo 2. 發送 /newbot 建立新的Bot
echo 3. 獲得Bot Token
echo 4. 獲取你的Chat ID
echo 5. 編輯config.py文件，填入Token和Chat ID
echo.
echo 設定完成後，執行: python main_gui.py
echo.
pause 