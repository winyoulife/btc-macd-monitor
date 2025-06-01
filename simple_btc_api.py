from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn
import requests
import os
from datetime import datetime

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "healthy", "service": "BTC Monitor", "timestamp": datetime.now().isoformat()}

@app.get("/")
def root():
    return {"message": "BTC Monitor API", "endpoints": ["/health", "/restream", "/display"]}

def get_btc_price():
    """直接從API獲取BTC價格"""
    try:
        # 使用CoinGecko API (無需API key)
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data['bitcoin']['usd']
        
        # 備用：使用Binance API
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return float(data['price'])
            
        return None
    except:
        return None

@app.get("/restream")
def restream_data():
    """為Restream Studio提供JSON數據"""
    price = get_btc_price()
    
    if price:
        return {
            "btc_price": f"${price:,.2f}",
            "btc_price_raw": price,
            "currency": "USD",
            "symbol": "BTC/USD",
            "status": "🟢 LIVE",
            "last_update": datetime.now().strftime("%H:%M:%S"),
            "date": datetime.now().strftime("%Y-%m-%d")
        }
    else:
        return {
            "btc_price": "載入中...", 
            "status": "🟡 連接中",
            "last_update": datetime.now().strftime("%H:%M:%S")
        }

@app.get("/display", response_class=HTMLResponse)
def display_page():
    """為直播顯示提供HTML頁面"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BTC Price Monitor</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                margin: 0;
                padding: 20px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                font-weight: bold;
            }
            .btc-container {
                text-align: center;
                background: rgba(0,0,0,0.4);
                padding: 40px;
                border-radius: 25px;
                border: 4px solid #f7931a;
                box-shadow: 0 10px 30px rgba(0,0,0,0.6);
                min-width: 400px;
                backdrop-filter: blur(10px);
            }
            .btc-price {
                font-size: 48px;
                color: #f7931a;
                margin: 20px 0;
                text-shadow: 4px 4px 8px rgba(0,0,0,0.8);
                font-weight: 900;
            }
            .btc-symbol {
                font-size: 28px;
                color: #ffffff;
                margin-bottom: 15px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.6);
            }
            .update-time {
                font-size: 16px;
                color: #cccccc;
                margin-top: 20px;
            }
            .status {
                font-size: 18px;
                margin-top: 15px;
                font-weight: bold;
            }
            .live-indicator {
                background: #ff0000;
                color: white;
                padding: 8px 20px;
                border-radius: 25px;
                font-size: 16px;
                margin-top: 15px;
                animation: pulse 2s infinite;
                display: inline-block;
            }
            @keyframes pulse {
                0% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.7; transform: scale(1.05); }
                100% { opacity: 1; transform: scale(1); }
            }
            .loading {
                animation: blink 1.5s infinite;
            }
            @keyframes blink {
                0%, 50% { opacity: 1; }
                51%, 100% { opacity: 0.3; }
            }
        </style>
    </head>
    <body>
        <div class="btc-container">
            <div class="btc-symbol">₿ BITCOIN</div>
            <div class="btc-price loading" id="price">載入中...</div>
            <div class="status" id="status">🟡 連接中...</div>
            <div class="live-indicator">🔴 LIVE</div>
            <div class="update-time" id="time">正在獲取數據...</div>
        </div>

        <script>
            async function updatePrice() {
                try {
                    const response = await fetch('/restream');
                    const data = await response.json();
                    
                    const priceElement = document.getElementById('price');
                    const statusElement = document.getElementById('status');
                    const timeElement = document.getElementById('time');
                    
                    priceElement.textContent = data.btc_price;
                    statusElement.textContent = data.status;
                    timeElement.textContent = '更新時間: ' + data.last_update;
                    
                    // 移除loading動畫
                    priceElement.classList.remove('loading');
                    
                } catch (error) {
                    document.getElementById('price').textContent = '連線錯誤';
                    document.getElementById('status').textContent = '🔴 API錯誤';
                    document.getElementById('time').textContent = '錯誤時間: ' + new Date().toLocaleTimeString();
                }
            }

            // 立即更新
            updatePrice();
            
            // 每30秒更新
            setInterval(updatePrice, 30000);
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("simple_btc_api:app", host="0.0.0.0", port=port, reload=False) 