#!/usr/bin/env python3
import os
import subprocess
import time
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>YouTube Stream Running - 2500k Bitrate</h1>')

def start_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    logger.info(f"Server starting on port {port}")
    server.serve_forever()

def start_stream():
    stream_key = 'f8bd-vduf-ycuf-s1ke-atbb'
    rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
    
    # 優化的 FFmpeg 命令 - 符合 YouTube 要求
    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'testsrc=size=1920x1080:rate=30',  # 1080p 30fps
        '-f', 'lavfi',
        '-i', 'sine=frequency=1000:sample_rate=48000',  # 添加音頻
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-b:v', '2500k',      # 提升到 YouTube 建議位元率
        '-maxrate', '2500k',
        '-bufsize', '5000k',
        '-pix_fmt', 'yuv420p',
        '-g', '60',
        '-keyint_min', '30',
        '-c:a', 'aac',
        '-b:a', '128k',       # 音頻位元率
        '-ar', '48000',
        '-f', 'flv',
        '-flvflags', 'no_duration_filesize',
        rtmp_url
    ]
    
    logger.info("Starting HIGH QUALITY stream - 2500k bitrate...")
    logger.info("Stream: 1080p@30fps + Audio")
    
    while True:
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Stream error: {stderr}")
                logger.info("Restarting in 10 seconds...")
                time.sleep(10)
            else:
                logger.info("Stream ended normally")
                break
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    # 啟動 Web 服務器
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # 啟動串流
    start_stream() 