# 使用Python官方镜像
FROM python:3.9-slim

# 設置工作目錄
WORKDIR /app

# 設置環境變量
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 複製requirements文件
COPY requirements.txt .
COPY render_stream.py .

# 安裝Python依賴
RUN pip install -r requirements.txt

# 複製應用程序代碼
COPY . .

# 創建日誌目錄
RUN mkdir -p /app/logs

# 設置權限
RUN chmod +x start_cloud_monitor.py

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 暴露端口
EXPOSE 8080

# 啟動命令
CMD ["python", "render_stream.py"] 