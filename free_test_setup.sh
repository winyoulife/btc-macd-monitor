#!/bin/bash
# 🚀 免費 24/7 雲端直播測試腳本
# 適用於 AWS EC2 t2.micro 免費實例

echo "🚀 開始設置免費 24/7 Bitcoin 雲端直播..."

# 更新系統
sudo apt update -y
sudo apt upgrade -y

# 安裝必要軟體
echo "📦 安裝必要軟體..."
sudo apt install -y ffmpeg xvfb chromium-browser pulseaudio

# 創建虛擬顯示
echo "🖥️ 設置虛擬顯示..."
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &

# 啟動音頻服務
echo "🎵 啟動音頻服務..."
pulseaudio --start --exit-idle-time=-1

# 創建直播腳本
echo "📺 創建直播腳本..."
cat > ~/stream_btc.sh << 'EOF'
#!/bin/bash

# 設置顯示
export DISPLAY=:99

# 啟動 Bitcoin 儀表板
chromium-browser --no-sandbox --kiosk --disable-dev-shm-usage \
    --disable-gpu --no-first-run --disable-extensions \
    --disable-default-apps --disable-translate \
    https://winyoulife.github.io/btc-macd-monitor/ &

# 等待頁面載入
sleep 10

# 開始直播到 YouTube
# 請替換 YOUR_STREAM_KEY 為你的 YouTube 直播金鑰
ffmpeg -f x11grab -r 30 -s 1920x1080 -i :99.0 \
       -f pulse -ac 2 -i default \
       -vcodec libx264 -preset veryfast -b:v 3000k \
       -acodec aac -ab 128k -ar 44100 \
       -f flv rtmp://a.rtmp.youtube.com/live2/YOUR_STREAM_KEY

EOF

# 給腳本執行權限
chmod +x ~/stream_btc.sh

# 創建開機自動啟動
echo "⚡ 設置開機自動啟動..."
cat > /tmp/btc-stream.service << EOF
[Unit]
Description=Bitcoin 24/7 Cloud Streaming
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu
ExecStartPre=/bin/bash -c 'Xvfb :99 -screen 0 1920x1080x24 &'
ExecStart=/home/ubuntu/stream_btc.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/btc-stream.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable btc-stream.service

echo "✅ 設置完成！"
echo ""
echo "🎯 接下來請："
echo "1. 前往 YouTube Studio 獲取直播金鑰"
echo "2. 編輯 ~/stream_btc.sh，替換 YOUR_STREAM_KEY"
echo "3. 執行: sudo systemctl start btc-stream.service"
echo "4. 關閉你的電腦，測試雲端直播是否持續！"
echo ""
echo "📊 檢查直播狀態: systemctl status btc-stream.service"
echo "📝 查看直播日誌: journalctl -u btc-stream.service -f" 