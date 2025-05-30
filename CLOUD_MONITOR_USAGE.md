# 🌟 雲端MACD監控系統 - 使用指南

恭喜！您現在有了一個專業的雲端監控系統，可以24/7自動監控BTC MACD指標並發送通知。

## 🚀 快速啟動

### 1. 本地測試
```bash
# 測試所有組件
python start_cloud_monitor.py --test

# 本地運行監控
python start_cloud_monitor.py
```

### 2. Docker 本地運行
```bash
# 構建並運行
docker-compose up -d

# 查看日誌
docker-compose logs -f
```

### 3. 雲端部署（推薦：Heroku）
```bash
# Windows用戶
./deploy.bat

# 或手動部署
heroku create your-app-name
heroku stack:set container -a your-app-name
git push heroku main
```

## 📊 監控功能

### 自動警報類型

1. **🔥 MACD金叉** - 買入信號
   - MACD線向上穿越信號線
   - 強度：85%

2. **📉 MACD死叉** - 賣出信號
   - MACD線向下穿越信號線
   - 強度：85%

3. **⚠️ RSI超買** - 賣出警告
   - RSI > 80
   - 強度：60%

4. **💡 RSI超賣** - 買入機會
   - RSI < 20
   - 強度：60%

### 通知樣式

```
🚀 BTC/TWD 交易信號 🚀

🎯 信號類型: 買入
💪 信號強度: 85% [████████░░]
📝 分析原因: MACD金叉信號！MACD(0.0156) > Signal(0.0134)

💰 當前價格: $3,177,845 TWD
📊 技術指標:
   • MACD: 0.0156
   • Signal: 0.0134
   • Histogram: 0.0022
   • RSI: 45.2

⏰ 時間: 2024-01-15 14:30:25
```

## ⚙️ 配置調整

### 配置文件：`monitor_config.json`

```json
{
  "monitoring": {
    "symbols": ["btctwd"],
    "check_interval": 60,
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

### 環境變量配置

```bash
# 必需
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# 可選調整
MONITOR_INTERVAL=30      # 檢查間隔（秒）
PRIMARY_PERIOD=15        # 主要週期（分鐘）
COOLDOWN_PERIOD=300      # 冷卻期（秒）
MAX_ALERTS_PER_HOUR=10   # 每小時最大警報數
```

## 🔍 監控和維護

### 健康檢查

訪問以下端點監控系統狀態：

- **健康檢查**: `https://your-app.herokuapp.com/health`
- **詳細狀態**: `https://your-app.herokuapp.com/status`
- **系統指標**: `https://your-app.herokuapp.com/metrics`

### 日誌查看

```bash
# Heroku
heroku logs --tail -a your-app-name

# Docker
docker-compose logs -f macd-monitor

# 本地
tail -f cloud_monitor.log
```

### 狀態檢查範例

```json
{
  "is_running": true,
  "runtime": "2:30:45",
  "stats": {
    "alerts_sent": 12,
    "checks_performed": 150,
    "errors_count": 0,
    "start_time": "2024-01-15T12:00:00"
  }
}
```

## 📈 使用建議

### 1. 設置策略

**保守策略**
- `check_interval`: 60秒
- `signal_strength_threshold`: 80
- `cooldown_period`: 600秒

**積極策略**
- `check_interval`: 30秒
- `signal_strength_threshold`: 60
- `cooldown_period`: 180秒

**高頻策略**
- `check_interval`: 15秒
- `primary_period`: 5分鐘
- `max_alerts_per_hour`: 20

### 2. 風險管理

- ⚠️ **永遠不要只依賴單一指標**
- 📊 **結合其他技術分析工具**
- 💰 **設置止損止盈點**
- 📚 **持續學習市場動態**

### 3. 通知管理

- 🔕 **設置合理的冷卻期**，避免過多通知
- 📱 **調整時間段**，避免夜間打擾
- 📊 **定期檢查準確率**，調整參數

## 🛠️ 故障排除

### 常見問題

**Q: 收不到Telegram通知**
```bash
# 檢查配置
curl https://your-app.com/config

# 測試Bot
python -c "
from telegram_notifier import TelegramNotifier
import asyncio
notifier = TelegramNotifier()
print(asyncio.run(notifier.test_connection()))
"
```

**Q: API連接失敗**
```bash
# 檢查網絡
curl https://max-api.maicoin.com/api/v2/tickers/btctwd

# 重啟服務
heroku restart -a your-app-name
```

**Q: 記憶體不足**
```bash
# 升級Heroku dyno
heroku ps:scale web=1:standard-1x -a your-app-name
```

### 調試模式

```bash
# 啟用詳細日誌
export LOG_LEVEL=DEBUG
python start_cloud_monitor.py

# 單次檢查
python -c "
from cloud_monitor import CloudMonitor
import asyncio
monitor = CloudMonitor()
asyncio.run(monitor.monitoring_cycle())
"
```

## 📱 Telegram指令

在Telegram中，您可以直接與Bot互動：

- `/start` - 開始接收通知
- `/status` - 查看系統狀態
- `/config` - 查看當前配置
- `/test` - 測試連接

## 🎯 最佳實踐

### 1. 部署檢查清單
- [ ] 測試本地運行
- [ ] 驗證Telegram連接
- [ ] 設置環境變量
- [ ] 部署到雲端
- [ ] 驗證健康檢查
- [ ] 監控日誌輸出

### 2. 運行監控
- [ ] 每日檢查系統狀態
- [ ] 每週檢查警報準確率
- [ ] 每月調整參數
- [ ] 定期備份配置

### 3. 投資安全
- [ ] 永遠不要全倉操作
- [ ] 設置合理的投資比例
- [ ] 保持理性判斷
- [ ] 定期學習提升

## 🚨 重要提醒

⚠️ **投資風險警告**
- 此系統僅提供技術分析建議
- 不構成投資建議
- 投資有風險，請謹慎決策
- 建議結合其他分析工具

🔒 **安全提醒**
- 保護好您的API密鑰
- 定期更新密碼
- 不要分享敏感信息
- 注意釣魚攻擊

## 🎉 享受您的智能監控系統！

現在您擁有了一個：
- ✅ 24/7 自動監控
- ✅ 即時 Telegram 通知
- ✅ 多重技術指標分析
- ✅ 雲端高可用部署
- ✅ 完整的監控面板

祝您投資順利！ 🚀📈 