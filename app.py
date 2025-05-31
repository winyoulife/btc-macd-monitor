from fastapi import FastAPI
from cloud_monitor import CloudMonitor
import uvicorn

app = FastAPI()
monitor = CloudMonitor()

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/status")
def status():
    return monitor.get_status()

# 若要本地測試可加：
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=10000, reload=True) 