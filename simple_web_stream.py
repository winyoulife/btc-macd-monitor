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
            self.wfile.write(b'<h1>YouTube Stream Running</h1>')

def start_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    logger.info(f"Server starting on port {port}")
    server.serve_forever()

def start_stream():
    stream_key = 'f8bd-vduf-ycuf-s1ke-atbb'
    rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
    
    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'testsrc=size=1280x720:rate=25',
        '-c:v', 'libx264',
        '-preset', 'veryfast',
        '-b:v', '1500k',
        '-f', 'flv',
        rtmp_url
    ]
    
    logger.info("Starting simple stream...")
    subprocess.run(cmd)

if __name__ == "__main__":
    # 啟動 Web 服務器
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # 啟動串流
    start_stream() 