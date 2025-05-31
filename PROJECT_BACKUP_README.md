# BTC MACD 雲端監控系統 - 完整專案備份

## 專案概述

這是一個完整的 BTC/TWD MACD 技術指標監控系統，具備以下功能：
- 24/7 雲端監控 BTC 價格和 MACD 指標
- Telegram 即時通知（黃金交叉、死亡交叉、RSI 警告）
- 多平台部署支援（Render.com、Fly.io、Heroku 等）
- 本地 GUI 介面和雲端健康檢查
- 智能冷卻期和速率限制

## 專案結構

### 核心監控系統
- `cloud_monitor.py` - 主要監控程式（856行）
- `health_server.py` - 健康檢查伺服器（225行）
- `start_cloud_monitor.py` - 統一啟動器（202行）
- `macd_analyzer.py` - MACD 分析器（183行）
- `telegram_notifier.py` - Telegram 通知模組（215行）

### GUI 介面系統
- `ultimate_professional_gui.py` - 專業版GUI（1346行）
- `professional_main_gui.py` - 主GUI介面（796行）
- `optimized_main_gui.py` - 優化版GUI（602行）
- `main_gui.py` - 基礎GUI（596行）
- `macd_detail_window.py` - MACD詳細視窗（277行）

### 啟動腳本
- `start_professional.py` - 專業版啟動器（240行）
- `start_optimized.py` - 優化版啟動器（177行）
- `start_here.py` - 基礎啟動器（224行）

### Telegram 相關
- `webhook_telegram_handler.py` - Webhook處理器（489行）
- `interactive_telegram_handler.py` - 互動式處理器（418行）
- `telegram_setup_helper.py` - 設定助手（241行）

### 配置和工具
- `config.py` - 基礎配置（35行）
- `professional_font_config.py` - 字體配置（255行）
- `font_config.py` - 基礎字體配置（80行）
- `max_api.py` - MAX交易所API（77行）
- `custom_macd_calculator.py` - 自定義MACD計算器（106行）

### 部署和測試
- `Dockerfile` - Docker容器配置
- `docker-compose.yml` - Docker Compose配置
- `heroku.yml` - Heroku部署配置
- `render.yaml` - Render.com部署配置
- `requirements.txt` - Python依賴包清單

### 文檔系統
- `README.md` - 主要說明文檔
- `QUICK_START.md` - 快速開始指南
- `CLOUD_DEPLOYMENT.md` - 雲端部署指南
- `CLOUD_MONITOR_USAGE.md` - 監控系統使用說明
- `PROFESSIONAL_GUIDE.md` - 專業版使用指南
- `OPTIMIZATION_GUIDE.md` - 優化指南
- `INTERACTIVE_TELEGRAM_GUIDE.md` - Telegram互動指南
- `RENDER_DEPLOYMENT.md` - Render部署指南

### 批次腳本（Windows）
- `run_local.bat` - 本地運行
- `deploy_to_render.bat` - 部署到Render
- `setup_heroku_deployment.bat` - Heroku部署設定
- `docker_local_setup.bat` - Docker本地設定
- `check_and_deploy.bat` - 檢查並部署

## 快速使用指南

### 1. 本地運行
```bash
# 安裝依賴
pip install -r requirements.txt

# 運行GUI版本
python start_professional.py

# 運行雲端監控版本
python start_cloud_monitor.py
```

### 2. 雲端部署
- **Render.com**: 使用 `deploy_to_render.bat` 或參考 `RENDER_DEPLOYMENT.md`
- **Fly.io**: 參考 `CLOUD_DEPLOYMENT.md`
- **Docker**: 使用 `docker-compose up -d`

### 3. 設定 Telegram 通知
1. 運行 `python telegram_setup_helper.py`
2. 設定環境變數或修改 `monitor_config.json`
3. 測試通知功能

## 環境變數設定

```bash
# Telegram 設定
TELEGRAM_BOT_TOKEN=你的機器人Token
TELEGRAM_CHAT_ID=你的聊天室ID

# API 設定  
MAX_API_KEY=MAX交易所API密鑰
MAX_API_SECRET=MAX交易所API密鑰

# 監控設定
ALERT_COOLDOWN=300  # 警告冷卻期（秒）
MAX_ALERTS_PER_HOUR=10  # 每小時最大警告數
```

## 備份還原步驟

### 備份專案
1. 複製整個專案資料夾到安全位置
2. 備份 `.env` 檔案（如果有的話）
3. 備份 `monitor_config.json` 設定檔
4. 保存這份對話記錄文檔

### 還原專案
1. 將備份的專案資料夾復製到新位置
2. 安裝 Python 依賴：`pip install -r requirements.txt`
3. 恢復環境變數設定
4. 運行測試：`python quick_macd_test.py`

## 故障排除

### 常見問題
1. **Telegram 通知失效**：檢查 Token 和 Chat ID
2. **API 連接失敗**：檢查網路連接和 API 金鑰
3. **Docker 部署失敗**：確認 Docker Desktop 已安裝
4. **編碼錯誤**：確認系統支援 UTF-8 編碼

### 調試工具
- `quick_macd_test.py` - 快速功能測試
- `simple_debug.py` - 簡單調試工具
- `check_telegram_settings.py` - Telegram 設定檢查

## 專案特色

1. **智能監控**：自動檢測 MACD 黃金交叉和死亡交叉
2. **多重警告**：RSI 超買超賣警告
3. **速率控制**：防止通知轟炸
4. **多平台支援**：可部署到多個雲端平台
5. **健康檢查**：內建 API 端點監控系統狀態
6. **專業GUI**：多種介面選擇，支援即時圖表

## 技術規格

- **語言**：Python 3.9+
- **主要依賴**：pandas, numpy, matplotlib, tkinter, requests
- **部署平台**：Render.com, Fly.io, Heroku, Docker
- **通知系統**：Telegram Bot API
- **數據來源**：MAX 交易所 API

## 版本歷史

- v1.0：基礎 MACD 監控功能
- v2.0：加入 GUI 介面和 Telegram 通知
- v3.0：雲端部署支援和健康檢查
- v4.0：專業版GUI和多平台部署
- v5.0：智能監控和速率控制

---

**建立日期**：2025年5月30日  
**最後更新**：2025年5月30日  
**狀態**：已測試並可正常運行  
**備份完整性**：✅ 所有核心文件已包含 