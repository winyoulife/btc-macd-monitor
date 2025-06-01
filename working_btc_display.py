#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import http.server
import socketserver
import json
import urllib.request
import threading
import time
import os

# 全局變數存儲BTC價格
btc_price_data = {"price": "載入中...", "timestamp": ""}

def get_btc_price():
    """獲取BTC價格的背景線程"""
    global btc_price_data
    while True:
        try:
            # 使用最簡單的API
            response = urllib.request.urlopen("https://api.coinbase.com/v2/exchange-rates?currency=BTC", timeout=10)
            data = json.loads(response.read().decode())
            usd_rate = float(data['data']['rates']['USD'])
            
            btc_price_data = {
                "price": f"${usd_rate:,.2f}",
                "timestamp": time.strftime("%H:%M:%S")
            }
            print(f"✅ BTC價格更新: {btc_price_data['price']}")
        except Exception as e:
            print(f"❌ 價格獲取失敗: {e}")
            btc_price_data = {
                "price": "無法獲取",
                "timestamp": time.strftime("%H:%M:%S")
            }
        
        time.sleep(30)  # 30秒更新一次

class BTCHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/display':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>BTC 直播監控</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body {{
            background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
            color: #00ff88;
            font-family: 'Courier New', monospace;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }}
        .container {{
            text-align: center;
            background: rgba(0,0,0,0.7);
            padding: 40px;
            border-radius: 20px;
            border: 2px solid #00ff88;
            box-shadow: 0 0 30px rgba(0,255,136,0.3);
        }}
        h1 {{
            font-size: 3em;
            margin: 0 0 20px 0;
            text-shadow: 0 0 20px #00ff88;
        }}
        .price {{
            font-size: 6em;
            font-weight: bold;
            margin: 20px 0;
            text-shadow: 0 0 30px #00ff88;
            animation: pulse 2s infinite;
        }}
        .time {{
            font-size: 1.5em;
            opacity: 0.8;
            margin-top: 20px;
        }}
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 BTC 即時價格 🚀</h1>
        <div class="price">{btc_price_data['price']}</div>
        <div class="time">更新時間: {btc_price_data['timestamp']}</div>
        <div class="time">每30秒自動更新</div>
    </div>
</body>
</html>
"""
            self.wfile.write(html.encode('utf-8'))
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "price": btc_price_data['price']}
            self.wfile.write(json.dumps(response).encode())
        else:
            super().do_GET()

if __name__ == "__main__":
    PORT = int(os.environ.get('PORT', 9999))  # 雲端使用環境變數，本地使用9999
    
    # 啟動價格獲取線程
    price_thread = threading.Thread(target=get_btc_price, daemon=True)
    price_thread.start()
    
    # 啟動HTTP服務器
    with socketserver.TCPServer(("", PORT), BTCHandler) as httpd:
        print(f"🚀 BTC直播服務器運行在: http://localhost:{PORT}/display")
        print(f"🔗 Restream Studio使用: http://localhost:{PORT}/display")
        print("按 Ctrl+C 停止服務器")
        httpd.serve_forever() 