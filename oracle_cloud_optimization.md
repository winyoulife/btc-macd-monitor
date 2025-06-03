# Oracle Cloud Always Free 優化指南

## 🎯 **避免停機的策略**

### 1. **降低資源使用**
```bash
# 使用更低的設定
ffmpeg -f lavfi -i testsrc=size=1280x720:rate=15 \
  -c:v libx264 -preset veryfast -crf 28 \
  -maxrate 1500k -bufsize 3000k \
  -f flv rtmp://a.rtmp.youtube.com/live2/YOUR_KEY
```

### 2. **間歇性使用**
- 不要24/7運行直播
- 每次直播1-2小時，然後停止
- 讓伺服器"休息"

### 3. **多地區策略**
- 註冊多個Oracle帳戶（不同email）
- 選擇不同地區的資料中心
- 韓國首爾、日本東京、美國Phoenix輪流使用

### 4. **監控使用量**
```bash
# 檢查CPU使用率
top
# 檢查網路使用量
vnstat
```

## ⚠️ **觸發停機的行為**
- CPU 100% 使用超過8小時
- 連續大量出站流量
- 挖礦或其他高負載活動
- 同時運行多個實例做相同工作

## 🔄 **恢復策略**
1. 等待24-48小時自動恢復
2. 重新啟動實例
3. 必要時重新創建實例 