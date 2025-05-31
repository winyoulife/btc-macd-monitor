from fastapi import FastAPI
from cloud_monitor import CloudMonitor
import uvicorn
import os

app = FastAPI()
monitor = CloudMonitor()

@app.get("/health")
def health():
    return {"status": "healthy", "webhook_mode": True, "timestamp": "2025-06-01T00:01:09.162064+08:00"}

@app.get("/status")
def status():
    return monitor.get_status()

@app.get("/")
def root():
    return {"message": "BTC MACD Monitor API", "endpoints": ["/health", "/status"]}

# 若要本地測試可加：
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True) 