# 專案備份與還原操作指南

## 立即備份操作（現在就做！）

### 1. 創建備份資料夾
```bash
# 在你的電腦上創建備份資料夾
mkdir C:\BTC_MACD_BACKUP
mkdir C:\BTC_MACD_BACKUP\2025-05-30
```

### 2. 複製整個專案
```bash
# 複製目前工作目錄的所有文件
# 從： C:\2025-05-29btcmacd2
# 到： C:\BTC_MACD_BACKUP\2025-05-30\
```

### 3. 備份檢查清單
確認以下文件都已複製：

#### ✅ 核心程式檔案
- [ ] `cloud_monitor.py` (35KB)
- [ ] `health_server.py` (7.9KB)  
- [ ] `start_cloud_monitor.py` (6.6KB)
- [ ] `telegram_notifier.py` (7.5KB)
- [ ] `macd_analyzer.py` (6.6KB)

#### ✅ GUI 系統檔案
- [ ] `ultimate_professional_gui.py` (58KB)
- [ ] `professional_main_gui.py` (34KB)
- [ ] `start_professional.py` (8.8KB)
- [ ] `main_gui.py` (24KB)

#### ✅ 配置檔案
- [ ] `monitor_config.json` (965B)
- [ ] `requirements.txt` (236B)
- [ ] `config.py` (892B)

#### ✅ 部署檔案
- [ ] `Dockerfile`
- [ ] `docker-compose.yml`
- [ ] `render.yaml`
- [ ] `heroku.yml`

#### ✅ 批次腳本
- [ ] `run_local.bat`
- [ ] `deploy_to_render.bat`
- [ ] 所有 `.bat` 檔案

#### ✅ 文檔檔案
- [ ] `README.md`
- [ ] `PROJECT_BACKUP_README.md`
- [ ] `CONVERSATION_HISTORY.md`
- [ ] `HOW_TO_BACKUP_AND_RESTORE.md`
- [ ] 所有 `.md` 檔案

#### ✅ 重要設定檔案
- [ ] `.env` (如果存在)
- [ ] `monitor_config.json`
- [ ] Git 資料夾 `.git/` (包含版本歷史)

---

## 下次還原操作步驟

### 步驟 1：環境準備
```bash
# 1. 確認 Python 已安裝
python --version

# 2. 確認 pip 可用
pip --version

# 3. 確認 Git 已安裝（如果要部署）
git --version
```

### 步驟 2：還原專案檔案
```bash
# 1. 創建新的工作目錄
mkdir C:\BTC_MACD_PROJECT_RESTORED
cd C:\BTC_MACD_PROJECT_RESTORED

# 2. 複製備份檔案到新目錄
# 從 C:\BTC_MACD_BACKUP\2025-05-30\ 複製所有檔案
```

### 步驟 3：安裝依賴
```bash
# 安裝 Python 套件
pip install -r requirements.txt

# 確認主要套件已安裝
pip list | findstr pandas
pip list | findstr requests
pip list | findstr matplotlib
```

### 步驟 4：配置設定
```bash
# 1. 檢查 monitor_config.json
type monitor_config.json

# 2. 設定環境變數（如果需要）
# 方法一：創建 .env 檔案
# 方法二：在系統中設定環境變數
```

### 步驟 5：功能測試
```bash
# 1. 快速功能測試
python quick_macd_test.py

# 2. 測試 Telegram 連接
python check_telegram_settings.py

# 3. 測試 GUI（可選）
python start_professional.py
```

### 步驟 6：啟動系統
```bash
# 本地運行
python start_cloud_monitor.py

# 或使用批次腳本
run_local.bat
```

---

## 重要的環境變數設定

### 必要設定
```bash
# Telegram 機器人設定
TELEGRAM_BOT_TOKEN=你的機器人Token
TELEGRAM_CHAT_ID=你的聊天室ID

# 可選：MAX API 設定
MAX_API_KEY=你的API密鑰
MAX_API_SECRET=你的API密鑰
```

### 設定方法

#### 方法一：使用 .env 檔案
創建 `.env` 檔案：
```
TELEGRAM_BOT_TOKEN=7123456789:ABCDEF...
TELEGRAM_CHAT_ID=1234567890
```

#### 方法二：Windows 環境變數
```cmd
# 在 CMD 中設定
setx TELEGRAM_BOT_TOKEN "你的Token"
setx TELEGRAM_CHAT_ID "你的ChatID"

# 在 PowerShell 中設定
$env:TELEGRAM_BOT_TOKEN="你的Token"
$env:TELEGRAM_CHAT_ID="你的ChatID"
```

---

## 對話記錄的使用方法

### 1. 重要文檔位置
- **完整對話記錄**：`CONVERSATION_HISTORY.md`
- **專案總覽**：`PROJECT_BACKUP_README.md`
- **這份操作指南**：`HOW_TO_BACKUP_AND_RESTORE.md`

### 2. 下次與 AI 對話時的提示
將以下文字提供給 AI：

```
我有一個完整的 BTC MACD 雲端監控系統專案，包含：

1. 專案概覽文檔：PROJECT_BACKUP_README.md
2. 完整對話記錄：CONVERSATION_HISTORY.md  
3. 備份操作指南：HOW_TO_BACKUP_AND_RESTORE.md

專案包含以下主要功能：
- 24/7 BTC/TWD MACD 監控
- Telegram 通知系統
- 多種 GUI 介面
- 雲端部署支援 (Render.com, Fly.io, Docker)
- 完整的健康檢查系統

請閱讀這些文檔後幫我進行 [你的具體需求]。
```

### 3. 快速重新熟悉專案
1. 先讀 `PROJECT_BACKUP_README.md` - 了解整體架構
2. 再讀 `CONVERSATION_HISTORY.md` - 了解開發過程和技術細節
3. 查看 `QUICK_START.md` - 快速啟動指南

---

## 故障排除

### 常見問題及解決方案

#### 1. Python 套件安裝失敗
```bash
# 升級 pip
python -m pip install --upgrade pip

# 使用特定來源安裝
pip install -r requirements.txt -i https://pypi.org/simple/
```

#### 2. Telegram 連接失敗
```bash
# 檢查設定
python check_telegram_settings.py

# 重新設定機器人
python telegram_setup_helper.py
```

#### 3. API 連接問題
```bash
# 測試網路連接
python quick_macd_test.py

# 檢查防火牆設定
```

#### 4. 編碼錯誤
- 確認系統支援 UTF-8
- 在 Windows 上可能需要設定 `PYTHONIOENCODING=utf-8`

---

## 安全提醒

### 🔒 不要備份的敏感資料
- 實際的 Telegram Bot Token
- API 密鑰和秘鑰
- 個人聊天室 ID

### ✅ 安全備份建議
1. 將敏感資料記錄在安全的地方（如密碼管理器）
2. 備份時排除 `.env` 檔案
3. 使用 `monitor_config.example.json` 作為範本

---

## 備份驗證清單

### 🔍 復原後確認事項
- [ ] 所有 `.py` 檔案都存在且可讀取
- [ ] `requirements.txt` 存在且內容正確
- [ ] 部署檔案 (Dockerfile, render.yaml 等) 完整
- [ ] 文檔檔案 (.md) 可正常開啟
- [ ] `quick_macd_test.py` 可正常運行
- [ ] Telegram 設定可正常使用

### 🎯 功能測試確認
- [ ] BTC 價格獲取正常
- [ ] MACD 計算正確
- [ ] Telegram 通知發送成功
- [ ] GUI 介面可正常啟動
- [ ] 健康檢查端點回應正常

---

**備份完成日期**：_____年___月___日  
**驗證人員**：_________________  
**備份位置**：C:\BTC_MACD_BACKUP\2025-05-30\  
**狀態**：□ 已完成 □ 已驗證 □ 可正常還原 