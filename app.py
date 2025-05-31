from fastapi import FastAPI
from cloud_monitor import CloudMonitor
import uvicorn
import os
from datetime import datetime

app = FastAPI()
monitor = CloudMonitor()

@app.get("/health")
def health():
    return {"status": "healthy", "webhook_mode": True, "timestamp": datetime.now().isoformat()}

@app.get("/status")
def status():
    return monitor.get_status()

@app.get("/")
def root():
    return {"message": "BTC MACD Monitor API", "endpoints": ["/health", "/status", "/restream"]}

@app.get("/restream")
def restream_data():
    """專為Restream Studio設計的API端點"""
    try:
        # 獲取BTC價格（使用CloudMonitor中的數據或直接調用API）
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
                "status": "正常運行",
                "last_update": datetime.now().strftime("%H:%M:%S"),
                "date": datetime.now().strftime("%Y-%m-%d")
            }
        else:
            return {
                "btc_price": "載入中...",
                "status": "獲取數據中",
                "last_update": datetime.now().strftime("%H:%M:%S")
            }
    except Exception as e:
        return {
            "btc_price": "連線錯誤",
            "status": f"錯誤: {str(e)}",
            "last_update": datetime.now().strftime("%H:%M:%S")
        }

# 若要本地測試可加：
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True) 