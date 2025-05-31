from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import os
from datetime import datetime

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "healthy", "service": "YouTube BTC Stream", "timestamp": datetime.now().isoformat()}

@app.get("/")
def root():
    return {"message": "YouTube BTC Stream API", "endpoints": ["/health", "/stream", "/display"]}

@app.get("/stream")
def stream_data():
    """為YouTube直播提供JSON數據"""
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
                "status": "🟢 正常運行",
                "last_update": datetime.now().strftime("%H:%M:%S"),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "formatted_display": f"💰 BTC: ${price:,.2f} USD"
            }
        else:
            return {
                "btc_price": "載入中...",
                "status": "🟡 獲取數據中",
                "last_update": datetime.now().strftime("%H:%M:%S")
            }
    except Exception as e:
        return {
            "btc_price": "連線錯誤",
            "status": f"🔴 錯誤: {str(e)}",
            "last_update": datetime.now().strftime("%H:%M:%S")
        }

@app.get("/display", response_class=HTMLResponse)
def display_page():
    """為OBS Browser Source提供HTML顯示頁面"""
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
                background: rgba(0,0,0,0.3);
                padding: 20px;
                border-radius: 15px;
                border: 2px solid #f7931a;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            }
            .btc-price {
                font-size: 28px;
                color: #f7931a;
                margin: 10px 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }
            .btc-symbol {
                font-size: 18px;
                color: #ffffff;
                margin-bottom: 5px;
            }
            .update-time {
                font-size: 12px;
                color: #cccccc;
                margin-top: 10px;
            }
            .status {
                font-size: 14px;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <div class="btc-container">
            <div class="btc-symbol">₿ BTC/USDT</div>
            <div class="btc-price" id="price">載入中...</div>
            <div class="status" id="status">🟡 連接中...</div>
            <div class="update-time" id="time">--:--:--</div>
        </div>

        <script>
            async function updatePrice() {
                try {
                    const response = await fetch('/stream');
                    const data = await response.json();
                    
                    document.getElementById('price').textContent = data.btc_price;
                    document.getElementById('status').textContent = data.status;
                    document.getElementById('time').textContent = '更新: ' + data.last_update;
                } catch (error) {
                    document.getElementById('price').textContent = '連線錯誤';
                    document.getElementById('status').textContent = '🔴 無法連接';
                    document.getElementById('time').textContent = new Date().toLocaleTimeString();
                }
            }

            // 立即更新一次
            updatePrice();
            
            // 每30秒更新一次
            setInterval(updatePrice, 30000);
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("youtube_stream_api:app", host="0.0.0.0", port=port, reload=True) 