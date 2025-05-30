# Render.com 部署指南

## 🚀 快速部署到 Render.com

Render.com 是一個完全免費的雲端平台，不需要信用卡即可部署應用。

### 第一步：準備 GitHub 倉庫

1. 前往 [GitHub](https://github.com) 創建新倉庫
2. 將本地代碼推送到 GitHub：

```bash
# 如果還沒有設置遠程倉庫
git remote add origin https://github.com/YOUR_USERNAME/btc-macd-monitor.git
git branch -M main
git push -u origin main
```

### 第二步：在 Render.com 創建服務

1. 前往 [Render.com](https://render.com) 註冊免費帳號
2. 連接你的 GitHub 帳號
3. 點擊 "New Web Service"
4. 選擇你的 GitHub 倉庫
5. 使用以下設置：

   - **Name**: `btc-macd-monitor`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start_cloud_monitor.py`

### 第三步：設置環境變數

在 Render.com 的 Environment 部分添加以下變數：

**必需變數：**
- `TELEGRAM_BOT_TOKEN`: 你的 Telegram Bot Token
- `TELEGRAM_CHAT_ID`: 你的 Telegram Chat ID

**可選變數：**
- `MONITORING_SYMBOLS`: `btctwd`
- `PRIMARY_PERIOD`: `15`
- `CHECK_INTERVAL`: `60`
- `PLATFORM`: `render`
- `MACD_FAST`: `12`
- `MACD_SLOW`: `26`
- `MACD_SIGNAL`: `9`
- `RSI_PERIOD`: `14`
- `RSI_OVERBOUGHT`: `80`
- `RSI_OVERSOLD`: `20`
- `COOLDOWN_PERIOD`: `300`
- `MAX_ALERTS_PER_HOUR`: `10`

### 第四步：部署

1. 點擊 "Create Web Service"
2. Render 將自動構建和部署你的應用
3. 部署完成後，你將獲得一個 URL，例如：`https://btc-macd-monitor.onrender.com`

### 監控和管理

- **健康檢查**: `https://your-app.onrender.com/health`
- **狀態查看**: `https://your-app.onrender.com/status`
- **指標查看**: `https://your-app.onrender.com/metrics`
- **配置查看**: `https://your-app.onrender.com/config`

### 注意事項

1. **免費方案限制**：
   - 750 小時/月免費運行時間
   - 15 分鐘無活動後會休眠
   - 冷啟動時間約 1-2 分鐘

2. **保持活躍**：
   - 系統會自動發送心跳請求保持活躍
   - 也可以使用外部監控服務定期訪問你的健康檢查端點

3. **日誌查看**：
   - 在 Render.com 控制台可以查看應用日誌
   - 支持實時日誌流

### 故障排除

如果部署失敗，檢查以下項目：

1. **依賴安裝失敗**：檢查 `requirements.txt` 是否正確
2. **環境變數錯誤**：確保 Telegram 配置正確
3. **啟動失敗**：查看 Render 日誌獲取詳細錯誤信息

### 手動部署腳本

```bash
# 1. 提交更改
git add .
git commit -m "Deploy to Render.com"
git push origin main

# 2. Render 會自動重新部署
```

### 成功指標

部署成功後，你應該會收到 Telegram 消息：
```
🤖 雲端監控系統啟動

📊 監控設定:
• 交易對: btctwd
• 週期: 15分鐘
• 檢查間隔: 60秒

⏰ 啟動時間: 2025-05-30 10:00:00

🔔 系統將開始監控市場並發送警報通知
```

這表示你的雲端監控系統已經成功運行！ 