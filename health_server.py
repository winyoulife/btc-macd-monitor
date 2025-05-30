#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
健康檢查服務器
用於雲端部署時的健康監控和狀態檢查
"""

import json
import threading
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class HealthCheckHandler(BaseHTTPRequestHandler):
    """健康檢查請求處理器"""
    
    def __init__(self, monitor, *args, **kwargs):
        self.monitor = monitor
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """處理GET請求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/health':
            self.handle_health_check()
        elif path == '/status':
            self.handle_status_check()
        elif path == '/metrics':
            self.handle_metrics()
        elif path == '/config':
            self.handle_config()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def handle_health_check(self):
        """健康檢查端點"""
        try:
            health_status = {
                'status': 'healthy' if self.monitor.is_running else 'stopped',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            }
            
            self.send_json_response(health_status, 200)
            
        except Exception as e:
            error_response = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.send_json_response(error_response, 500)
    
    def handle_status_check(self):
        """詳細狀態檢查"""
        try:
            status = self.monitor.get_status()
            
            # 修復 datetime 序列化問題
            if 'stats' in status and 'start_time' in status['stats']:
                if status['stats']['start_time']:
                    status['stats']['start_time'] = status['stats']['start_time'].isoformat()
            
            # 修復監控數據中的 timestamp
            if 'last_monitoring_data' in status:
                for symbol, data in status['last_monitoring_data'].items():
                    if 'timestamp' in data and data['timestamp']:
                        data['timestamp'] = data['timestamp'].isoformat()
            
            response = json.dumps(status, indent=2, ensure_ascii=False)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
            
        except Exception as e:
            error_response = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
            response = json.dumps(error_response, indent=2)
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
    
    def handle_metrics(self):
        """指標端點（Prometheus格式）"""
        try:
            stats = self.monitor.stats
            
            metrics = f"""# HELP macd_monitor_alerts_total Total alerts sent
# TYPE macd_monitor_alerts_total counter
macd_monitor_alerts_total {stats['alerts_sent']}

# HELP macd_monitor_checks_total Total checks performed
# TYPE macd_monitor_checks_total counter
macd_monitor_checks_total {stats['checks_performed']}

# HELP macd_monitor_errors_total Total errors occurred
# TYPE macd_monitor_errors_total counter
macd_monitor_errors_total {stats['errors_count']}

# HELP macd_monitor_running Monitor running status
# TYPE macd_monitor_running gauge
macd_monitor_running {1 if self.monitor.is_running else 0}
"""
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(metrics.encode())
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f'Error: {str(e)}'.encode())
    
    def handle_config(self):
        """配置檢查端點"""
        try:
            # 隱藏敏感信息
            config = self.monitor.config.copy()
            config['notifications'] = {
                'telegram_enabled': config['notifications']['telegram_enabled'],
                'email_enabled': config['notifications']['email_enabled'],
                'slack_enabled': config['notifications']['slack_enabled'],
                'discord_enabled': config['notifications']['discord_enabled']
            }
            
            self.send_json_response(config, 200)
            
        except Exception as e:
            error_response = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.send_json_response(error_response, 500)
    
    def send_json_response(self, data, status_code=200):
        """發送JSON響應"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        self.wfile.write(json_data.encode('utf-8'))
    
    def log_message(self, format, *args):
        """禁用默認日誌輸出"""
        pass

class HealthServer:
    """健康檢查服務器"""
    
    def __init__(self, monitor, port=8080):
        self.monitor = monitor
        self.port = port
        self.server = None
        self.server_thread = None
    
    def start(self):
        """啟動健康檢查服務器"""
        try:
            # 創建處理器工廠
            def handler_factory(*args, **kwargs):
                return HealthCheckHandler(self.monitor, *args, **kwargs)
            
            # 創建服務器
            self.server = HTTPServer(('0.0.0.0', self.port), handler_factory)
            
            # 在新線程中運行服務器
            self.server_thread = threading.Thread(
                target=self.server.serve_forever,
                daemon=True
            )
            self.server_thread.start()
            
            print(f"✅ 健康檢查服務器啟動於端口 {self.port}")
            print(f"🔗 端點:")
            print(f"   • Health: http://localhost:{self.port}/health")
            print(f"   • Status: http://localhost:{self.port}/status")
            print(f"   • Metrics: http://localhost:{self.port}/metrics")
            print(f"   • Config: http://localhost:{self.port}/config")
            
        except Exception as e:
            print(f"❌ 啟動健康檢查服務器失敗: {e}")
    
    def stop(self):
        """停止健康檢查服務器"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print(f"🔴 健康檢查服務器已停止")

if __name__ == "__main__":
    # 測試服務器
    from cloud_monitor import CloudMonitor
    
    monitor = CloudMonitor()
    health_server = HealthServer(monitor)
    
    try:
        health_server.start()
        print("按 Ctrl+C 停止測試服務器")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        health_server.stop()
        print("\n測試服務器已停止") 