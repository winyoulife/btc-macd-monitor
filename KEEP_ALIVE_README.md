# 🚀 保活功能說明 (優化版)

## 問題背景
Render.com免費方案會在15-30分鐘無活動後讓服務進入休眠狀態。當有新請求時需要約1分鐘重新啟動，這導致：
- 首次查詢需要等待系統重新啟動
- 影響Telegram互動查詢的即時性

## 解決方案
系統新增**強化型自動保活功能**，高頻率發送內部健康檢查請求，確保服務始終運行。

## 功能特點
- ✅ **高頻保活**: 每5分鐘自動ping健康檢查端點（比原來的30分鐘更頻繁）
- ✅ **多端點ping**: 同時ping /health 和 /status 端點，確保全面覆蓋
- ✅ **立即啟動**: 系統啟動後立即執行第一次ping，無需等待
- ✅ **智能調度**: 與主監控循環並行運行，不影響效能
- ✅ **錯誤恢復**: ping失敗時自動重試，詳細日誌記錄
- ✅ **狀態監控**: 可通過 `/status` 端點查看保活狀態
- ✅ **環境配置**: 支持環境變數自定義設定

## 環境變數配置

### Render.com平台設定
在Render.com控制台添加以下環境變數：

| 變數名稱 | 默認值 | 說明 |
|---------|--------|------|
| `KEEP_ALIVE_ENABLED` | `true` | 是否啟用保活功能 |
| `KEEP_ALIVE_INTERVAL` | `300` | Ping間隔（秒），默認5分鐘 |
| `RENDER_EXTERNAL_HOSTNAME` | 自動偵測 | Render服務域名，通常自動設定 |

### 建議設定
```bash
KEEP_ALIVE_ENABLED=true
KEEP_ALIVE_INTERVAL=300  # 5分鐘，可根據需要調整
```

## 工作原理
1. **系統啟動時**: 立即執行第一次ping，然後創建保活任務
2. **高頻Ping**: 每5分鐘向多個端點發送GET請求
   - `https://your-app.onrender.com/health`
   - `https://your-app.onrender.com/status` (如果可用)
3. **狀態記錄**: 記錄最後成功ping時間和ping次數
4. **錯誤處理**: ping失敗時記錄詳細日誌，1分鐘後重試

## 狀態監控
訪問 `/status` 端點查看保活狀態：
```json
{
  "keep_alive": {
    "enabled": true,
    "interval_seconds": 300,
    "health_url": "https://your-app.onrender.com/health",
    "last_ping": "2024-01-15T10:30:00+08:00"
  }
}
```

## 效果對比
| 項目 | 優化前 | 優化後 |
|------|--------|--------|
| Ping間隔 | 30分鐘 | **5分鐘** |
| 首次ping | 等待30分鐘 | **立即執行** |
| Ping端點 | 單一端點 | **多端點** |
| 日誌詳細度 | 基本 | **詳細** |
| 休眠風險 | 高 | **極低** |

## 實際效果
- 🎯 **即時回應**: Telegram查詢無需等待系統重啟
- 🔄 **24小時活躍**: 服務始終保持響應狀態  
- 📊 **穩定監控**: MACD監控不受服務休眠影響
- 💬 **流暢交互**: AI分析查詢立即響應
- ⚡ **零冷啟動**: 完全消除1分鐘等待時間

## 日誌範例
```
💓 保活功能已啟動 - 間隔: 300秒 (5分鐘)
   目標URL: https://btc-macd-monitor.onrender.com/health
🚀 執行初始保活ping...
💓 保活ping成功: https://btc-macd-monitor.onrender.com/health (狀態: 200)
💓 保活ping成功: https://btc-macd-monitor.onrender.com/status (狀態: 200)
✅ 保活完成 - 2/2 個端點成功
🔄 執行第 2 次保活ping...
```

## 自定義間隔
如需更積極的保活（不建議低於5分鐘）：
```bash
KEEP_ALIVE_INTERVAL=180  # 3分鐘（極積極）
```

如需較溫和的保活：
```bash
KEEP_ALIVE_INTERVAL=600  # 10分鐘
```

## 禁用保活功能
如需禁用（強烈不建議）：
```bash
KEEP_ALIVE_ENABLED=false
```

> **注意**: 
> - 5分鐘間隔是經過測試的最佳平衡點
> - 間隔太短可能消耗過多資源
> - 間隔太長無法有效防止休眠
> - 建議保持默認的5分鐘設定 