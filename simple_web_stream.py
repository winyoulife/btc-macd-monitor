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
            self.wfile.write(b'<h1>YouTube Stream - CBR 2500k</h1>')

def start_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    logger.info(f"Server starting on port {port}")
    server.serve_forever()

def start_stream():
    stream_key = 'f8bd-vduf-ycuf-s1ke-atbb'
    rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
    
    # 強制 CBR 2500k 位元率設置
    cmd = [
        'ffmpeg', '-re',  # 即時播放
        '-f', 'lavfi',
        '-i', 'testsrc=size=1280x720:rate=30',  # 降到720p但保持高位元率
        '-f', 'lavfi',
        '-i', 'sine=frequency=1000:sample_rate=48000',
        '-c:v', 'libx264',
        '-preset', 'ultrafast',  # 最快編碼
        '-tune', 'zerolatency',
        '-b:v', '2500k',        # 目標位元率
        '-minrate', '2500k',    # 最小位元率 
        '-maxrate', '2500k',    # 最大位元率
        '-bufsize', '2500k',    # CBR 設置
        '-pix_fmt', 'yuv420p',
        '-g', '30',
        '-keyint_min', '30',
        '-x264opts', 'nal-hrd=cbr',  # 強制CBR
        '-c:a', 'aac',
        '-b:a', '128k',
        '-ar', '48000',
        '-f', 'flv',
        '-flvflags', 'no_duration_filesize',
        rtmp_url
    ]
    
    logger.info("Starting CBR 2500k stream...")
    logger.info("Settings: 720p@30fps + CBR 2500k + Audio")
    
    attempt = 0
    while True:
        try:
            attempt += 1
            logger.info(f"Stream attempt #{attempt}")
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Stream failed: {stderr}")
                logger.info("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                logger.info("Stream ended normally")
                break
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # 啟動 Web 服務器
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # 啟動串流
    start_stream() 