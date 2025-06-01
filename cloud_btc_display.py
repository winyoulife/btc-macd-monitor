#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import urllib.request
import threading
import time
from datetime import datetime

# 全局變數存儲BTC價格
btc_price_data = {"price": "載入中...", "timestamp": "", "last_update": 0}

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
                "timestamp": time.strftime("%H:%M:%S"),
                "last_update": time.time()
            }
            print(f"✅ BTC價格更新: {btc_price_data['price']}")
        except Exception as e:
            print(f"❌ 價格獲取失敗: {e}")
            btc_price_data.update({
                "price": "無法獲取",
                "timestamp": time.strftime("%H:%M:%S")
            })
        
        time.sleep(30)  # 30秒更新一次

def generate_html():
    """生成HTML頁面"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>BTC 雲端直播監控</title>
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
        .cloud {{
            font-size: 1em;
            color: #ffaa00;
            margin-top: 10px;
        }}
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 BTC 雲端即時價格 🚀</h1>
        <div class="price">{btc_price_data['price']}</div>
        <div class="time">更新時間: {btc_price_data['timestamp']}</div>
        <div class="time">每30秒自動更新</div>
        <div class="cloud">☁️ 雲端直播服務 ☁️</div>
    </div>
</body>
</html>"""

def application(environ, start_response):
    """WSGI應用程式 - 雲端相容"""
    path = environ.get('PATH_INFO', '/')
    
    if path == '/health':
        response = json.dumps({
            "status": "healthy", 
            "price": btc_price_data['price'],
            "timestamp": datetime.now().isoformat(),
            "service": "Cloud BTC Monitor"
        }).encode('utf-8')
        start_response('200 OK', [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response)))
        ])
        return [response]
    
    elif path == '/display' or path == '/':
        html = generate_html().encode('utf-8')
        start_response('200 OK', [
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Content-Length', str(len(html)))
        ])
        return [html]
    
    else:
        error = b'404: Not Found'
        start_response('404 Not Found', [
            ('Content-Type', 'text/plain'),
            ('Content-Length', str(len(error)))
        ])
        return [error]

# Flask相容性 (如果需要)
try:
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        return {
            "status": "healthy", 
            "price": btc_price_data['price'],
            "timestamp": datetime.now().isoformat(),
            "service": "Cloud BTC Monitor Flask"
        }
    
    @app.route('/display')
    @app.route('/')
    def display():
        return generate_html()
        
except ImportError:
    app = None

if __name__ == "__main__":
    # 啟動價格獲取線程
    price_thread = threading.Thread(target=get_btc_price, daemon=True)
    price_thread.start()
    
    PORT = int(os.environ.get('PORT', 8000))
    
    # 使用內建HTTP伺服器作為備用
    import http.server
    import socketserver
    from urllib.parse import urlparse, parse_qs
    
    class CloudHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "status": "healthy", 
                    "price": btc_price_data['price'],
                    "timestamp": datetime.now().isoformat(),
                    "service": "Cloud BTC Monitor"
                }
                self.wfile.write(json.dumps(response).encode())
            elif self.path == '/display' or self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(generate_html().encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'404: Not Found')
    
    print(f"🚀 雲端BTC直播服務器運行在: http://0.0.0.0:{PORT}")
    print(f"🔗 直播URL: http://0.0.0.0:{PORT}/display")
    
    with socketserver.TCPServer(("0.0.0.0", PORT), CloudHandler) as httpd:
        httpd.serve_forever() 