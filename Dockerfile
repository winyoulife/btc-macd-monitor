# 使用Python官方镜像
FROM python:3.9-slim

# 設置工作目錄
WORKDIR /app

# 設置環境變量
ENV PYTHONUNBUFFERED=1

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 複製文件
COPY simple_web_stream.py .

# 暴露端口
EXPOSE 8080

# 啟動命令
CMD ["python", "simple_web_stream.py"]