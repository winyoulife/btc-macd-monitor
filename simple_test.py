#!/usr/bin/env python3

import os
import http.server
import socketserver

PORT = int(os.environ.get('PORT', 8000))

class TestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/display':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """<!DOCTYPE html>
<html>
<head>
    <title>雲端測試</title>
</head>
<body>
    <h1>🚨 雲端測試成功！</h1>
    <p>如果你看到這個頁面，代表雲端平台可以運行！</p>
    <p>這是最簡單的測試版本</p>
</body>
</html>"""
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'404: Not Found')

print(f"🚀 測試服務器運行在端口: {PORT}")
with socketserver.TCPServer(("", PORT), TestHandler) as httpd:
    httpd.serve_forever() 