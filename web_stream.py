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
                <p>Streaming to YouTube with test pattern.</p>
                <p>Stream Key: f8bd-vduf-ycuf-s1ke-atbb</p>
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
    
    # FFmpeg 命令 - 生成測試圖案
    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'testsrc=size=1280x720:rate=25,format=yuv420p',
        '-f', 'lavfi', 
        '-i', 'sine=frequency=1000:sample_rate=44100',
        '-c:v', 'libx264',
        '-preset', 'veryfast',
        '-b:v', '2000k',
        '-maxrate', '2500k',
        '-bufsize', '4000k',
        '-pix_fmt', 'yuv420p',
        '-g', '50',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-f', 'flv',
        rtmp_url
    ]
    
    logger.info(f"Starting stream to: {rtmp_url}")
    
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