# 🚀 保活功能說明

## 問題背景
Render.com免費方案會在30分鐘無活動後讓服務進入休眠狀態。當有新請求時需要約1分鐘重新啟動，這導致：
- 首次查詢需要等待系統重新啟動
- 影響Telegram互動查詢的即時性

## 解決方案
系統新增自動保活功能，定時發送內部健康檢查請求，保持服務始終運行。

## 功能特點
- ✅ **自動保活**: 每30分鐘自動ping健康檢查端點
- ✅ **智能調度**: 與主監控循環並行運行，不影響效能
- ✅ **錯誤恢復**: ping失敗時自動重試
- ✅ **狀態監控**: 可通過 `/status` 端點查看保活狀態
- ✅ **環境配置**: 支持環境變數自定義設定

## 環境變數配置

### Render.com平台設定
在Render.com控制台添加以下環境變數：

| 變數名稱 | 默認值 | 說明 |
|---------|--------|------|
| `KEEP_ALIVE_ENABLED` | `true` | 是否啟用保活功能 |
| `KEEP_ALIVE_INTERVAL` | `1800` | Ping間隔（秒），建議30分鐘 |
| `RENDER_EXTERNAL_HOSTNAME` | 自動偵測 | Render服務域名，通常自動設定 |

### 建議設定
```bash
KEEP_ALIVE_ENABLED=true
KEEP_ALIVE_INTERVAL=1800  # 30分鐘
```

## 工作原理
1. **系統啟動時**: 創建保活任務，與主監控循環並行運行
2. **定時Ping**: 每30分鐘向 `https://your-app.onrender.com/health` 發送GET請求
3. **狀態記錄**: 記錄最後成功ping時間，可通過狀態端點查詢
4. **錯誤處理**: Ping失敗時記錄警告，1分鐘後重試

## 狀態監控
訪問 `/status` 端點查看保活狀態：
```json
{
  "keep_alive": {
    "enabled": true,
    "interval_seconds": 1800,
    "health_url": "https://your-app.onrender.com/health",
    "last_ping": "2024-01-15T10:30:00+08:00"
  }
}
```

## 效果
- 🎯 **即時回應**: Telegram查詢無需等待系統重啟
- 🔄 **持續運行**: 24小時保持服務活躍狀態
- 📊 **穩定監控**: MACD監控不受服務休眠影響
- 💬 **流暢交互**: AI分析查詢立即響應

## 日誌範例
```
💓 保活功能已啟動 - 間隔: 1800秒
   目標URL: https://btc-macd-monitor.onrender.com/health
💓 保活ping成功: https://btc-macd-monitor.onrender.com/health
```

## 禁用保活功能
如需禁用（不建議）：
```bash
KEEP_ALIVE_ENABLED=false
```

> **注意**: 禁用保活功能後，系統將恢復到原始狀態，可能出現冷啟動延遲問題。 