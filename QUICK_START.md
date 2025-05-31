# 🚀 快速開始指南

選擇最適合您的方式來運行MACD監控系統：

## 📊 運行方式對比

| 方式 | 難度 | 推薦度 | 特點 |
|------|------|---------|------|
| **本地Python** | ⭐ | ⭐⭐⭐⭐⭐ | 最簡單，無需額外安裝 |
| **Docker** | ⭐⭐ | ⭐⭐⭐⭐ | 容器化，易於管理 |
| **雲端部署** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 24/7運行，自動化 |

## 🏃‍♂️ 方式一：本地Python運行（推薦新手）

### 1. 一鍵啟動
```bash
# Windows
./run_local.bat

# 手動運行
python start_cloud_monitor.py --test  # 測試
python start_cloud_monitor.py        # 正式運行
```

### 2. 優點
- ✅ 無需安裝Docker
- ✅ 簡單易用
- ✅ 適合測試和開發

### 3. 缺點
- ❌ 需要保持電腦開啟
- ❌ 不適合24/7運行

## 🐳 方式二：Docker運行

### 1. 安裝Docker Desktop

**Windows 10/11：**
1. 下載：https://www.docker.com/products/docker-desktop/
2. 安裝並重啟電腦
3. 啟動Docker Desktop

**驗證安裝：**
```bash
docker --version
docker compose version
```

### 2. 運行容器

```bash
# 使用Docker Compose（推薦）
docker compose up -d

# 或直接使用Docker
docker build -t macd-monitor .
docker run -d -p 8080:8080 macd-monitor
```

### 3. 檢查狀態

```bash
# 查看容器狀態
docker compose ps

# 查看日誌
docker compose logs -f

# 健康檢查
curl http://localhost:8080/health
```

### 4. 停止容器

```bash
docker compose down
```

## ☁️ 方式三：雲端部署（推薦生產環境）

### 1. Heroku部署（最簡單）

```bash
# Windows
./deploy.bat winyoulife

# 設置環境變量
heroku config:set TELEGRAM_BOT_TOKEN=your_token -a your-app-name
heroku config:set TELEGRAM_CHAT_ID=your_chat_id -a your-app-name
```

### 2. 其他雲端平台
- **Railway**: 現代化部署
- **DigitalOcean**: 性價比高
- **AWS/GCP**: 企業級

詳細步驟請參考：`CLOUD_DEPLOYMENT.md`

## 🛠️ 故障排除

### Docker問題

**問題：docker-compose 命令不存在**
```bash
# 新版Docker使用 docker compose（無連字符）
docker compose up -d

# 如果還是不行，安裝Docker Desktop
```

**問題：Docker Desktop未啟動**
```bash
# 手動啟動Docker Desktop應用程式
# 或在服務中啟動Docker服務
```

### Python問題

**問題：模組導入錯誤**
```bash
# 安裝依賴
pip install -r requirements.txt

# 檢查Python版本（需要3.9+）
python --version
```

**問題：API連接失敗**
```bash
# 檢查網絡連接
ping max-api.maicoin.com

# 測試API
curl https://max-api.maicoin.com/api/v2/tickers/btctwd
```

## 🎯 選擇建議

### 新手用戶
1. 先用 `run_local.bat` 測試
2. 確認功能正常後考慮Docker或雲端

### 開發測試
1. 本地Python運行
2. 使用Docker進行環境隔離

### 生產使用
1. 雲端部署（Heroku/Railway）
2. 配置監控和警報

## 📱 監控面板

無論使用哪種方式，您都可以通過以下端點監控系統：

- **健康檢查**: `http://localhost:8080/health`
- **系統狀態**: `http://localhost:8080/status`
- **配置檢查**: `http://localhost:8080/config`
- **指標數據**: `http://localhost:8080/metrics`

## 🆘 需要幫助？

如果遇到問題：

1. 查看相關日誌文件
2. 檢查 `CLOUD_MONITOR_USAGE.md` 使用指南
3. 參考 `CLOUD_DEPLOYMENT.md` 部署指南
4. 確保Telegram Bot配置正確

祝您使用愉快！🚀 