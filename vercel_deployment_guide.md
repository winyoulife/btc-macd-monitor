# 🌊 Vercel YouTube 直播部署指南

## 🎯 概念說明
由於 Vercel 是 serverless 平台，不適合長時間運行的進程。
我們創建了一個**創新的解決方案**：
- 🎬 **按需觸發**: 點擊按鈕啟動 4 分鐘串流
- 🔄 **手動續期**: 重複觸發維持連續直播
- 💻 **Web 控制台**: 美觀的操作界面

## 📋 部署步驟

### 1. 📂 項目結構
```
.
├── vercel.json           # Vercel 配置
├── package.json         # 項目配置
├── index.html          # 控制台界面
├── api/
│   ├── health.js       # 健康檢查
│   └── stream.js       # 串流啟動
└── vercel_deployment_guide.md
```

### 2. 🚀 部署到 Vercel

#### 方法一：GitHub 自動部署
1. 前往 [vercel.com](https://vercel.com)
2. 使用 GitHub 登入
3. 點擊 "New Project"
4. 選擇 `winyoulife/btc-macd-monitor` 倉庫
5. 部署設置：
   - Framework Preset: `Other`
   - Build Command: `echo 'No build needed'`
   - Output Directory: `.`

#### 方法二：CLI 部署
```bash
npm install -g vercel
vercel login
vercel --prod
```

### 3. ⚙️ 環境變數設置
在 Vercel Dashboard 中設置：
- `YOUTUBE_STREAM_KEY`: f8bd-vduf-ycuf-s1ke-atbb

### 4. 🎮 使用方法
部署後前往: `https://[項目名稱].vercel.app`

1. 點擊 "開始 4 分鐘串流"
2. 等待串流啟動
3. 在 YouTube Studio 查看直播狀態
4. 4 分鐘後重複點擊以續期

## ⚠️ 限制與注意事項

### Vercel 限制
- ⏰ **執行時間**: 最多 5 分鐘（我們設為 4 分鐘安全值）
- 💾 **內存限制**: 1GB
- 🔄 **冷啟動**: 可能有 1-2 秒延遲
- 📊 **併發限制**: 免費版有限制

### 串流特性
- 📹 **解析度**: 720p (1280x720)
- 🎵 **音訊**: AAC 128k
- 📡 **位元率**: 1500k (適中設置)
- ⏱️ **持續時間**: 4 分鐘/次

## 🎭 優缺點分析

### ✅ 優點
- 🆓 **完全免費**: 無資源限制顧慮
- 🌍 **全球 CDN**: 快速響應
- 🎨 **美觀界面**: 專業控制台
- 🔧 **易於維護**: serverless 架構

### ❌ 缺點
- ⏰ **需要手動續期**: 每 4 分鐘點一次
- 🔄 **間歇性中斷**: 切換時會有短暫斷流
- 📱 **需要人工操作**: 無法完全自動化

## 🎯 適用場景
- 🧪 **測試直播**: 驗證串流設置
- 📊 **展示用途**: 短時間演示
- 🎮 **互動式控制**: 需要人工干預的場合

## 🔄 自動化改進建議
可以考慮添加：
- ⏰ **定時器提醒**: 接近 4 分鐘時提醒續期
- 🤖 **自動重啟**: 使用 GitHub Actions 定時觸發
- �� **狀態監控**: 串流狀態實時顯示 