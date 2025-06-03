#!/usr/bin/env python3
"""
YouTube Live Stream Web Service for Render.com
"""
import os
import subprocess
import time
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = b"""
            <html>
            <head><title>YouTube Live Stream</title></head>
            <body>
                <h1>YouTube Live Stream Active</h1>
                <p>Streaming to YouTube with HIGH QUALITY test pattern.</p>
                <p>Stream Key: f8bd-vduf-ycuf-s1ke-atbb</p>
                <p>Bitrate: 2500k (HD Quality)</p>
            </body>
            </html>
            """
            self.wfile.write(html)
        else:
            self.send_response(404)
            self.end_headers()

def start_web_server():
    """啟動健康檢查 Web 服務器"""
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    logger.info(f"Web server starting on port {port}")
    server.serve_forever()

def start_stream():
    """啟動 YouTube 直播"""
    # YouTube 串流金鑰
    stream_key = os.environ.get('YOUTUBE_STREAM_KEY', 'f8bd-vduf-ycuf-s1ke-atbb')
    rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
    
    # 優化的 FFmpeg 命令 - 高品質設置
    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'testsrc=size=1920x1080:rate=30,format=yuv420p',  # 提升到 1080p 30fps
        '-f', 'lavfi', 
        '-i', 'sine=frequency=1000:sample_rate=48000',  # 提升音頻取樣率
        '-c:v', 'libx264',
        '-preset', 'fast',  # 改為 fast 提升品質
        '-b:v', '2500k',    # 提升到建議位元率
        '-maxrate', '3000k', # 提升最大位元率
        '-bufsize', '6000k', # 提升緩衝區
        '-pix_fmt', 'yuv420p',
        '-g', '60',         # 提升 GOP 大小
        '-keyint_min', '30', # 關鍵幀間隔
        '-c:a', 'aac',
        '-b:a', '160k',     # 提升音頻位元率
        '-ar', '48000',     # 音頻取樣率
        '-f', 'flv',
        '-reconnect', '1',   # 自動重連
        '-reconnect_streamed', '1',
        '-reconnect_delay_max', '2',
        rtmp_url
    ]
    
    logger.info(f"Starting HIGH QUALITY stream to: {rtmp_url}")
    logger.info("Stream settings: 1080p@30fps, 2500k video, 160k audio")
    
    while True:
        try:
            # 啟動串流
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"FFmpeg error: {stderr}")
                logger.info("Restarting in 30 seconds...")
                time.sleep(30)
            else:
                logger.info("Stream ended normally")
                break
                
        except Exception as e:
            logger.error(f"Error: {e}")
            logger.info("Restarting in 30 seconds...")
            time.sleep(30)

if __name__ == "__main__":
    logger.info("YouTube Live Stream Web Service Starting...")
    
    # 檢查 FFmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        logger.info("FFmpeg is available")
    except:
        logger.error("FFmpeg not found")
        exit(1)
    
    # 啟動 Web 服務器（在背景執行）
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    
    # 啟動直播（主線程）
    start_stream() 