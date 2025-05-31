from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import os
from datetime import datetime

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "healthy", "service": "BTC Monitor", "timestamp": datetime.now().isoformat()}

@app.get("/")
def root():
    return {"message": "BTC Monitor API", "endpoints": ["/health", "/restream", "/display"]}

@app.get("/restream")
def restream_data():
    """為Restream Studio提供JSON數據"""
    try:
        from max_api import MaxAPI
        max_api = MaxAPI()
        ticker = max_api.get_ticker('btcusdt')
        
        if ticker:
            price = float(ticker['price'])
            return {
                "btc_price": f"${price:,.2f}",
                "btc_price_raw": price,
                "currency": "USD",
                "symbol": "BTC/USDT",
                "status": "🟢 LIVE",
                "last_update": datetime.now().strftime("%H:%M:%S"),
                "date": datetime.now().strftime("%Y-%m-%d")
            }
        else:
            return {"btc_price": "載入中...", "status": "🟡 連接中"}
    except Exception as e:
        return {"btc_price": "ERROR", "status": f"🔴 {str(e)}"}

@app.get("/display", response_class=HTMLResponse)
def display_page():
    """為直播顯示提供HTML頁面"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
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
                min-height: 180px;
                font-weight: bold;
            }
            .btc-container {
                text-align: center;
                background: rgba(0,0,0,0.4);
                padding: 30px;
                border-radius: 20px;
                border: 3px solid #f7931a;
                box-shadow: 0 8px 25px rgba(0,0,0,0.5);
                min-width: 350px;
            }
            .btc-price {
                font-size: 36px;
                color: #f7931a;
                margin: 15px 0;
                text-shadow: 3px 3px 6px rgba(0,0,0,0.7);
                font-weight: 900;
            }
            .btc-symbol {
                font-size: 22px;
                color: #ffffff;
                margin-bottom: 10px;
                text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
            }
            .update-time {
                font-size: 14px;
                color: #cccccc;
                margin-top: 15px;
            }
            .status {
                font-size: 16px;
                margin-top: 10px;
                font-weight: bold;
            }
            .live-indicator {
                background: #ff0000;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 14px;
                margin-top: 10px;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
        </style>
    </head>
    <body>
        <div class="btc-container">
            <div class="btc-symbol">₿ BTC/USDT</div>
            <div class="btc-price" id="price">載入中...</div>
            <div class="status" id="status">🟡 連接中...</div>
            <div class="live-indicator">🔴 LIVE</div>
            <div class="update-time" id="time">--:--:--</div>
        </div>

        <script>
            async function updatePrice() {
                try {
                    const response = await fetch('/restream');
                    const data = await response.json();
                    
                    document.getElementById('price').textContent = data.btc_price;
                    document.getElementById('status').textContent = data.status;
                    document.getElementById('time').textContent = '更新: ' + data.last_update;
                } catch (error) {
                    document.getElementById('price').textContent = '連線錯誤';
                    document.getElementById('status').textContent = '🔴 API錯誤';
                    document.getElementById('time').textContent = new Date().toLocaleTimeString();
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
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True) 