# ☁️ Oracle Cloud 永久免費 24/7 直播設置

## 🎯 為什麼選擇 Oracle Cloud？

### **🆓 永久免費配置**
- **CPU：** 2 x AMD EPYC 處理器
- **RAM：** 12GB 記憶體
- **儲存：** 100GB 硬碟空間
- **網路：** 每月 10TB 流量
- **重點：** 🔥 **永久免費，不是試用！**

### **💪 性能比較**
```
Oracle Cloud Free:  12GB RAM + 2 CPU = 🚀 超強
AWS t2.micro:       1GB RAM + 1 CPU  = 😐 普通
Google Cloud:       0.6GB RAM + 1 CPU = 😕 較弱
```

## 📋 **設置步驟**

### **步驟 1: 註冊 Oracle Cloud 帳戶**
1. **前往：** https://www.oracle.com/cloud/free/
2. **點擊 "Start for free"**
3. **填寫註冊資訊**
   - 選擇國家/地區
   - 提供信用卡（不會收費，只是驗證）
   - 完成驗證

### **步驟 2: 創建免費 VM 實例**
1. **登入 Oracle Cloud 控制台**
2. **導航：** Compute → Instances
3. **點擊 "Create Instance"**
4. **配置設定：**
   ```
   名稱: btc-streaming-server
   映像: Ubuntu 20.04 LTS
   形狀: VM.Standard.E2.1.Micro (永久免費)
   CPU: 2 AMD EPYC
   記憶體: 12GB
   ```

### **步驟 3: 網路設置**
1. **創建 VCN（虛擬雲端網路）**
2. **開放端口：**
   ```
   SSH: 22
   HTTP: 80
   HTTPS: 443
   RTMP: 1935
   ```
3. **設置安全規則允許流量**

### **步驟 4: 連接到服務器**
```bash
# 使用 SSH 連接
ssh -i ~/.ssh/oracle_cloud_key ubuntu@YOUR_ORACLE_IP

# 或使用 Oracle 網頁控制台的雲端終端
```

### **步驟 5: 安裝直播軟體**
```bash
# 下載並執行自動化安裝腳本
curl -s https://raw.githubusercontent.com/your-repo/oracle_stream_setup.sh | bash
```

## 🛠️ **Oracle 專用安裝腳本**

```bash
#!/bin/bash
# Oracle Cloud 永久免費 24/7 直播腳本

echo "🚀 Oracle Cloud 永久免費直播設置開始..."

# 更新系統
sudo apt update -y && sudo apt upgrade -y

# 安裝直播軟體
sudo apt install -y ffmpeg xvfb chromium-browser pulseaudio wget curl

# 設置虛擬顯示器
echo "🖥️ 設置虛擬顯示器..."
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &

# 創建直播腳本
cat > ~/oracle_stream.sh << 'EOF'
#!/bin/bash

# 設置環境
export DISPLAY=:99

# 啟動虛擬顯示
Xvfb :99 -screen 0 1920x1080x24 &
sleep 5

# 啟動 Bitcoin 儀表板
chromium-browser --no-sandbox --kiosk --disable-dev-shm-usage \
    --disable-gpu --no-first-run --disable-extensions \
    --disable-default-apps --disable-translate \
    --window-size=1920,1080 \
    https://winyoulife.github.io/btc-macd-monitor/ &

# 等待頁面完全載入
sleep 15

# 開始 24/7 直播到 YouTube
ffmpeg -f x11grab -r 30 -s 1920x1080 -i :99.0 \
       -c:v libx264 -preset veryfast -b:v 4000k \
       -maxrate 4000k -bufsize 8000k \
       -g 60 -c:a aac -b:a 128k -ar 44100 \
       -f flv rtmp://a.rtmp.youtube.com/live2/YOUR_STREAM_KEY

EOF

chmod +x ~/oracle_stream.sh

# 創建系統服務
sudo tee /etc/systemd/system/oracle-btc-stream.service > /dev/null <<EOF
[Unit]
Description=Oracle BTC 24/7 Cloud Streaming
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu
ExecStart=/home/ubuntu/oracle_stream.sh
Restart=always
RestartSec=10
Environment=DISPLAY=:99

[Install]
WantedBy=multi-user.target
EOF

# 啟用服務
sudo systemctl daemon-reload
sudo systemctl enable oracle-btc-stream.service

echo "✅ Oracle Cloud 永久免費直播設置完成！"
echo ""
echo "🎯 下一步："
echo "1. 獲取 YouTube 直播金鑰"
echo "2. 編輯 ~/oracle_stream.sh 替換 YOUR_STREAM_KEY"
echo "3. 啟動服務: sudo systemctl start oracle-btc-stream.service"
echo "4. 關閉電腦測試！"
echo ""
echo "📊 檢查狀態: sudo systemctl status oracle-btc-stream.service"
echo "📝 查看日誌: sudo journalctl -u oracle-btc-stream.service -f"
```

## 💰 **成本分析**

### **Oracle Cloud 永久免費**
- **月費：** $0 💚
- **年費：** $0 💚  
- **總費用：** $0 💚
- **性能：** 12GB RAM + 2 CPU 🚀

### **其他方案比較**
- AWS: 12個月後每月 $10-15 💸
- Google Cloud: 90天後每月 $8-12 💸
- 付費服務: 每月 $12-25 💸

## 🎯 **Oracle 的隱藏優勢**

### **1. 永久免費保證**
```
Oracle 官方承諾：Always Free 資源永遠不會過期
不像 AWS 只有 12 個月試用
```

### **2. 強悍性能**
```
12GB RAM 可以同時：
- 運行多個直播
- 處理更複雜的技術分析
- 支援更高的直播品質
```

### **3. 企業級穩定性**
```
Oracle 是企業級雲端服務
99.9% 正常運行時間
全球多個數據中心
```

## 🚀 **立即行動計劃**

### **今天：** 註冊 Oracle Cloud
1. 前往 oracle.com/cloud/free
2. 完成免費註冊
3. 驗證帳戶

### **明天：** 設置虛擬機器
1. 創建免費 VM 實例
2. 配置網路安全規則
3. 運行自動化安裝腳本

### **後天：** 測試直播
1. 設置 YouTube 直播金鑰
2. 啟動 24/7 雲端直播
3. 關閉電腦測試效果

## ⚡ **為什麼我之前沒推薦 Oracle？**

**坦白說：**
- Oracle 註冊稍微複雜一點
- 但配置和性能遠超其他免費方案
- 永久免費是真正的遊戲改變者

**現在我強烈推薦 Oracle Cloud！** 🔥

## 🎁 **額外福利**

**用 Oracle 的 12GB RAM，你還可以：**
- 同時直播多個加密貨幣
- 運行更複雜的 AI 分析
- 支援更多觀眾同時觀看
- 未來擴展更多功能

**真的是最佳選擇！** 🏆 