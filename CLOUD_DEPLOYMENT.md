# 🚀 雲端MACD監控系統部署指南

這個指南將教您如何將MACD監控系統部署到各種雲端平台，實現24/7自動監控和通知。

## 📋 目錄

- [快速開始](#快速開始)
- [部署選項](#部署選項)
- [環境變量配置](#環境變量配置)
- [平台特定部署](#平台特定部署)
- [監控和維護](#監控和維護)
- [故障排除](#故障排除)

## 🏃‍♂️ 快速開始

### 1. 準備工作

確保您已經：
- ✅ 設置好Telegram Bot（參考原本的設置指南）
- ✅ 有Git版本控制
- ✅ 安裝了Docker（推薦）

### 2. 測試本地運行

```bash
# 測試系統配置
python start_cloud_monitor.py --test

# 本地運行
python start_cloud_monitor.py
```

### 3. 使用Docker本地測試

```bash
# 構建鏡像
docker build -t macd-monitor .

# 運行容器
docker run -d -p 8080:8080 \
  -v $(pwd)/monitor_config.json:/app/monitor_config.json \
  macd-monitor
```

## 🌐 部署選項

### 選項對比

| 平台 | 成本 | 難度 | 推薦度 | 特點 |
|------|------|------|---------|------|
| **Heroku** | 免費/付費 | ⭐⭐ | ⭐⭐⭐⭐⭐ | 最簡單，自動SSL |
| **Railway** | 免費/付費 | ⭐⭐ | ⭐⭐⭐⭐ | 現代化，易用 |
| **DigitalOcean** | 付費 | ⭐⭐⭐ | ⭐⭐⭐⭐ | 性價比高 |
| **AWS** | 付費 | ⭐⭐⭐⭐ | ⭐⭐⭐ | 功能最全 |
| **本地Docker** | 免費 | ⭐⭐ | ⭐⭐⭐ | 完全控制 |

## ⚙️ 環境變量配置

### 必需變量

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### 可選變量

```bash
# 監控設置
MONITOR_INTERVAL=60
PRIMARY_PERIOD=15
CHECK_SYMBOLS=btctwd

# 通知設置
COOLDOWN_PERIOD=300
MAX_ALERTS_PER_HOUR=10

# 服務設置
PORT=8080
LOG_LEVEL=INFO
TIMEZONE=Asia/Taipei
```

## 🚀 平台特定部署

### 1. Heroku 部署（推薦）

**為什麼選擇Heroku？**
- ✅ 有免費方案
- ✅ 自動SSL證書
- ✅ 簡單的CI/CD
- ✅ 內建監控

**部署步驟：**

```bash
# 1. 安裝Heroku CLI
# 下載：https://devcenter.heroku.com/articles/heroku-cli

# 2. 登錄
heroku login

# 3. 使用自動部署腳本
./deploy.bat  # Windows
./deploy      # Linux/Mac

# 或手動部署
heroku create your-app-name
heroku stack:set container -a your-app-name
git push heroku main
```

**設置環境變量：**

```bash
heroku config:set TELEGRAM_BOT_TOKEN=your_token -a your-app-name
heroku config:set TELEGRAM_CHAT_ID=your_chat_id -a your-app-name
```

### 2. Railway 部署

```bash
# 1. 安裝Railway CLI
npm install -g @railway/cli

# 2. 登錄和部署
railway login
railway deploy
```

### 3. DigitalOcean App Platform

1. 登錄DigitalOcean控制台
2. 創建新App
3. 連接GitHub倉庫
4. 選擇Dockerfile構建
5. 設置環境變量
6. 部署

### 4. AWS ECS/Fargate

```yaml
# aws-task-definition.json
{
  "family": "macd-monitor",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "macd-monitor",
      "image": "your-ecr-repo/macd-monitor:latest",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "TELEGRAM_BOT_TOKEN",
          "value": "your_token"
        }
      ]
    }
  ]
}
```

### 5. Google Cloud Run

```bash
# 構建並推送
gcloud builds submit --tag gcr.io/PROJECT_ID/macd-monitor

# 部署
gcloud run deploy --image gcr.io/PROJECT_ID/macd-monitor \
  --platform managed \
  --set-env-vars TELEGRAM_BOT_TOKEN=your_token
```

## 📊 監控和維護

### 健康檢查端點

部署後，您可以通過以下端點監控系統：

```bash
# 基本健康檢查
curl https://your-app.herokuapp.com/health

# 詳細狀態
curl https://your-app.herokuapp.com/status

# Prometheus指標
curl https://your-app.herokuapp.com/metrics

# 配置檢查
curl https://your-app.herokuapp.com/config
```

### 日誌監控

```bash
# Heroku
heroku logs --tail -a your-app-name

# Docker
docker logs -f container_name

# 查看特定時間範圍
heroku logs --since="2024-01-01 00:00" -a your-app-name
```

### 性能監控

使用Prometheus + Grafana組合：

```bash
# 啟動監控堆棧
docker-compose --profile monitoring up -d

# 訪問Grafana
open http://localhost:3000
# 用戶名：admin，密碼：admin
```

## 🔧 配置調優

### 監控配置範例

```json
{
  "monitoring": {
    "symbols": ["btctwd", "ethtwd"],
    "periods": [5, 15, 30, 60],
    "check_interval": 30,
    "primary_period": 15
  },
  "alerts": {
    "macd_crossover": true,
    "signal_strength_threshold": 70,
    "rsi_overbought": 80,
    "rsi_oversold": 20
  },
  "advanced": {
    "cooldown_period": 300,
    "max_alerts_per_hour": 10
  }
}
```

### 高頻交易配置

```json
{
  "monitoring": {
    "check_interval": 15,
    "primary_period": 5
  },
  "alerts": {
    "signal_strength_threshold": 60
  },
  "advanced": {
    "cooldown_period": 60,
    "max_alerts_per_hour": 20
  }
}
```

## 🐛 故障排除

### 常見問題

**1. Telegram通知不工作**
```bash
# 檢查配置
curl https://your-app.com/config

# 測試連接
python -c "
from telegram_notifier import TelegramNotifier
import asyncio
notifier = TelegramNotifier()
print(asyncio.run(notifier.test_connection()))
"
```

**2. API連接失敗**
```bash
# 檢查網絡
curl https://max-api.maicoin.com/api/v2/tickers/btctwd

# 檢查應用日誌
heroku logs --tail -a your-app-name | grep "ERROR"
```

**3. 記憶體不足**
```bash
# Heroku升級dyno
heroku ps:scale web=1:standard-1x -a your-app-name

# 檢查記憶體使用
heroku logs --dyno=web.1 -a your-app-name | grep "memory"
```

**4. 部署失敗**
```bash
# 檢查Docker構建
docker build . --no-cache

# 檢查依賴
pip install -r requirements.txt
```

### 調試模式

```bash
# 啟用詳細日誌
export LOG_LEVEL=DEBUG
python start_cloud_monitor.py

# 測試模式
python start_cloud_monitor.py --test
```

## 💰 成本估算

### 免費方案
- **Heroku**: 550小時/月免費
- **Railway**: $5免費額度
- **Vercel**: 免費（需調整為無服務器）

### 付費方案
- **Heroku Hobby**: $7/月
- **DigitalOcean**: $5/月起
- **AWS**: ~$10/月
- **Google Cloud**: ~$8/月

## 🔒 安全考慮

1. **環境變量**: 永遠不要將密鑰提交到代碼庫
2. **HTTPS**: 確保所有通信都使用HTTPS
3. **訪問控制**: 考慮添加API密鑰認證
4. **監控**: 設置異常活動警報

## 📈 擴展功能

### 多通知渠道

```python
# 添加Email通知
from email_notifier import EmailNotifier

# 添加Discord通知
from discord_notifier import DiscordNotifier

# 添加Slack通知
from slack_notifier import SlackNotifier
```

### 多交易所支持

```python
# 添加其他交易所
from binance_api import BinanceAPI
from coinbase_api import CoinbaseAPI
```

### 高級分析

```python
# 添加機器學習預測
from ml_predictor import MLPredictor

# 添加技術分析指標
from advanced_indicators import BollingerBands, MACD, RSI
```

## 🎯 生產環境檢查清單

### 部署前
- [ ] 測試本地運行
- [ ] 驗證Telegram連接
- [ ] 檢查API限制
- [ ] 設置監控警報
- [ ] 準備回滾計劃

### 部署後
- [ ] 驗證健康檢查
- [ ] 測試通知功能
- [ ] 監控日誌輸出
- [ ] 設置性能監控
- [ ] 文檔化配置

## 🆘 支持

如果遇到問題：

1. 查看[故障排除](#故障排除)部分
2. 檢查應用日誌
3. 測試各個組件
4. 查看平台特定文檔

---

🎉 **恭喜！** 您現在有了一個全天候運行的BTC MACD監控系統！ 