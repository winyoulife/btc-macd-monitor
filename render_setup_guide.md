# 🚀 Render.com YouTube 直播設置指南

## 步驟一：註冊 Render.com

1. 前往 [render.com](https://render.com)
2. 點擊 "Get Started for Free"
3. 使用 GitHub 帳戶登入（推薦）

## 步驟二：創建 GitHub Repository

1. 前往 [github.com](https://github.com)
2. 創建新的 repository，命名為 `youtube-livestream`
3. 上傳以下文件：
   - `render_stream.py`
   - `requirements.txt`
   - `Dockerfile`
   - `render.yaml`

## 步驟三：連接到 Render.com

1. 在 Render.com Dashboard 點擊 "New +"
2. 選擇 "Background Worker"
3. 連接您的 GitHub repository
4. 選擇 `youtube-livestream` repository

## 步驟四：配置設定

1. **服務名稱**: `youtube-livestream`
2. **Environment**: `Docker`
3. **Plan**: `Free` (750小時/月)
4. **Dockerfile路徑**: `./Dockerfile`

## 步驟五：設置環境變數

在 Environment Variables 部分添加：
- **Key**: `YOUTUBE_STREAM_KEY`
- **Value**: `f8bd-vduf-ycuf-s1ke-atbb`

## 步驟六：部署

1. 點擊 "Create Web Service"
2. 等待部署完成（約5-10分鐘）
3. 檢查 Logs 確認串流開始

## 📊 使用監控

- **每月限制**: 750 小時（約25天）
- **重新啟動**: 在 Render Dashboard 手動重啟
- **日誌查看**: Dashboard → Service → Logs

## 🔧 管理指令

### 停止直播
在 Render Dashboard 點擊 "Suspend"

### 重新啟動
點擊 "Resume" 或 "Manual Deploy"

### 更新串流金鑰
1. 編輯 Environment Variables
2. 更新 `YOUTUBE_STREAM_KEY`
3. Manual Deploy

## 💡 優化建議

1. **定期重啟**: 每天重啟一次避免記憶體洩漏
2. **監控使用時數**: 接近750小時時暫停
3. **備用方案**: 準備其他平台帳戶 