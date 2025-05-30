# BTC/TWD MACD 交易信號分析系統

## 📊 功能特點

這是一個專為台灣虛擬貨幣交易所MAX設計的BTC/TWD交易信號分析系統，具備以下功能：

### 🎯 核心功能
- **即時價格監控**: 即時獲取MAX交易所BTC/TWD價格資料
- **MACD技術分析**: 自動計算MACD、Signal、Histogram等技術指標
- **RSI指標**: 提供相對強弱指標分析
- **AI智能信號**: 基於多重技術指標的智能買賣信號判斷
- **Telegram通知**: 自動發送交易信號到Telegram

### 🖥️ 界面特點
- **現代化GUI**: 使用tkinter建立的美觀視窗界面
- **即時圖表**: matplotlib繪製的專業技術分析圖表
- **多面板顯示**: 價格資訊、技術指標、交易信號一目了然
- **系統日誌**: 完整的操作記錄和錯誤追蹤

## 🚀 快速開始

### 1. 環境需求
- Python 3.8 或更高版本
- Windows 10/11 (已針對Windows最佳化)

### 2. 安裝依賴
```bash
pip install -r requirements.txt
```

### 3. Telegram Bot 設定

#### 建立Telegram Bot
1. 在Telegram中搜尋 `@BotFather`
2. 發送 `/newbot` 命令
3. 依照指示設定Bot名稱和用戶名
4. 獲得Bot Token (格式: 123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ)

#### 獲取Chat ID
1. 將Bot加入到你想接收通知的群組或私人聊天
2. 發送一條訊息給Bot
3. 瀏覽: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. 在回應中找到你的Chat ID

#### 設定環境變數
建立 `.env` 文件或設定系統環境變數：
```bash
TELEGRAM_BOT_TOKEN=你的Bot Token
TELEGRAM_CHAT_ID=你的Chat ID
```

或者直接在 `config.py` 中修改：
```python
TELEGRAM_BOT_TOKEN = '你的Bot Token'
TELEGRAM_CHAT_ID = '你的Chat ID'
```

### 4. 啟動程式
```bash
python main_gui.py
```

## 📱 使用說明

### 主界面操作

#### 控制面板
- **開始監控**: 開始即時監控和分析
- **手動更新**: 立即更新價格和指標
- **測試Telegram**: 測試Telegram連接是否正常
- **設定**: 開啟設定視窗

#### 價格資訊面板
顯示BTC/TWD的即時價格資訊：
- 當前價格
- 24小時最高/最低價
- 成交量
- 最後更新時間

#### MACD技術指標面板
顯示關鍵技術指標：
- MACD線
- Signal線  
- Histogram
- RSI
- EMA12/EMA26

#### 交易信號面板
顯示AI分析結果：
- 當前信號（買入/賣出/持有）
- 信號強度（0-100%）
- 分析原因

#### 圖表區域
三個專業技術分析圖表：
1. **價格走勢圖**: BTC價格、EMA12、EMA26
2. **MACD圖**: MACD線、Signal線、Histogram
3. **RSI圖**: RSI指標及超買超賣線

#### 系統日誌
記錄所有操作和信號，便於追蹤分析。

### Telegram通知

當系統檢測到強烈的買入或賣出信號時，會自動發送包含以下資訊的通知：
- 信號類型和強度
- 當前價格
- 技術指標數值
- 分析原因
- 時間戳記

## ⚙️ 設定參數

可在 `config.py` 中調整的參數：

### MACD參數
```python
MACD_FAST_PERIOD = 12    # 快線週期
MACD_SLOW_PERIOD = 26    # 慢線週期
MACD_SIGNAL_PERIOD = 9   # 信號線週期
```

### 交易信號參數
```python
BUY_THRESHOLD = 0.0001      # 買入閾值
SELL_THRESHOLD = -0.0001    # 賣出閾值
MIN_SIGNAL_INTERVAL = 300   # 最小信號間隔（秒）
```

### 更新頻率
```python
PRICE_UPDATE_INTERVAL = 5000  # 價格更新間隔（毫秒）
```

## 🛡️ 風險聲明

⚠️ **重要提醒**:
- 本系統僅提供技術分析建議，不構成投資建議
- 虛擬貨幣投資具有高風險，可能導致本金損失
- 請在充分了解風險的前提下進行投資決策
- 建議結合多種分析方法和資訊來源

## 🔧 故障排除

### 常見問題

#### 1. Telegram通知不工作
- 檢查Bot Token和Chat ID是否正確
- 確認Bot已加入到目標群組/聊天
- 使用"測試Telegram"功能驗證連接

#### 2. 價格資料無法獲取
- 檢查網路連接
- 確認MAX交易所API服務正常
- 查看系統日誌了解詳細錯誤

#### 3. 圖表顯示問題
- 確認matplotlib正確安裝
- 重啟程式
- 檢查Python版本兼容性

#### 4. 程式無法啟動
- 確認所有依賴已正確安裝
- 檢查Python版本（需要3.8+）
- 查看終端錯誤訊息

### 日誌文件
程式會自動生成 `btc_macd.log` 日誌文件，記錄詳細的運行資訊和錯誤，有助於問題診斷。

## 📄 授權條款

本專案僅供學習和研究使用。使用者需自行承擔使用風險。

## 🤝 貢獻

歡迎提出問題、建議或貢獻代碼！

---

**開發資訊**:
- 開發語言: Python 3.8+
- GUI框架: tkinter
- 圖表庫: matplotlib
- 技術分析: ta (Technical Analysis)
- 通訊: python-telegram-bot
- 交易所API: MAX Exchange 