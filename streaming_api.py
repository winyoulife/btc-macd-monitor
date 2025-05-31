#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YouTube直播用AI技術分析API服務器
提供即時技術分析數據給直播疊加系統
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any
from aiohttp import web, web_request
from aiohttp.web import middleware
import aiohttp_cors

from max_api import MaxAPI
from advanced_crypto_analyzer import AdvancedCryptoAnalyzer

class StreamingAnalysisAPI:
    """直播分析API服務器"""
    
    def __init__(self, port: int = 8888):
        self.port = port
        self.max_api = MaxAPI()
        self.analyzer = AdvancedCryptoAnalyzer()
        
        # 設置日誌
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('StreamingAPI')
        
        # 快取最新分析結果
        self.latest_analysis = {}
        self.last_update = None
        
        # 創建web應用
        self.app = web.Application(middlewares=[self.cors_middleware])
        self.setup_routes()
        
    @middleware
    async def cors_middleware(self, request: web_request.Request, handler):
        """CORS中間件"""
        try:
            response = await handler(request)
        except Exception as e:
            response = web.json_response(
                {'error': str(e)}, 
                status=500
            )
        
        # 添加CORS頭
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return response
        
    def setup_routes(self):
        """設置路由"""
        # API路由
        self.app.router.add_get('/api/analysis', self.get_analysis)
        self.app.router.add_get('/api/price', self.get_price_only)
        self.app.router.add_get('/api/health', self.health_check)
        
        # 靜態文件路由 - 提供直播疊加頁面
        self.app.router.add_get('/', self.serve_overlay)
        self.app.router.add_get('/overlay', self.serve_overlay)
        
        # OPTIONS請求處理
        self.app.router.add_options('/{path:.*}', self.handle_options)
    
    async def handle_options(self, request: web_request.Request):
        """處理OPTIONS請求"""
        return web.Response(
            status=200,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )
    
    async def serve_overlay(self, request: web_request.Request):
        """提供直播疊加頁面"""
        try:
            with open('live_stream_overlay.html', 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        except FileNotFoundError:
            return web.Response(text='Overlay file not found', status=404)
    
    async def get_analysis(self, request: web_request.Request):
        """獲取完整AI技術分析"""
        try:
            self.logger.info("🔍 收到完整分析請求")
            
            # 檢查是否需要更新數據（每30秒更新一次）
            now = datetime.now()
            if (self.last_update is None or 
                (now - self.last_update).total_seconds() > 30):
                
                self.logger.info("📊 更新分析數據...")
                await self.update_analysis()
            
            # 返回快取的分析結果
            return web.json_response(self.latest_analysis)
            
        except Exception as e:
            self.logger.error(f"❌ 獲取分析失敗: {e}")
            return web.json_response({
                'error': '分析服務暫時不可用',
                'timestamp': datetime.now().isoformat()
            }, status=500)
    
    async def get_price_only(self, request: web_request.Request):
        """只獲取價格數據（更頻繁更新）"""
        try:
            self.logger.info("💰 收到價格查詢請求")
            
            # 獲取最新價格
            ticker = self.max_api.get_ticker('btcusdt')
            if not ticker:
                raise Exception("無法獲取價格數據")
            
            price_data = {
                'price': {
                    'current': float(ticker['price']),
                    'high_24h': float(ticker['high']),
                    'low_24h': float(ticker['low']),
                    'volume_24h': float(ticker['volume'])
                },
                'timestamp': datetime.now().isoformat()
            }
            
            return web.json_response(price_data)
            
        except Exception as e:
            self.logger.error(f"❌ 獲取價格失敗: {e}")
            return web.json_response({
                'error': '價格服務暫時不可用',
                'timestamp': datetime.now().isoformat()
            }, status=500)
    
    async def update_analysis(self):
        """更新AI分析數據"""
        try:
            # 獲取市場數據
            ticker = self.max_api.get_ticker('btcusdt')
            if not ticker:
                raise Exception("無法獲取市場數據")
            
            # 獲取K線數據
            kline_data = self.max_api.get_klines('btcusdt', period=60, limit=200)
            if kline_data is None or kline_data.empty:
                raise Exception("無法獲取K線數據")
            
            current_price = float(ticker['price'])
            
            # 執行AI分析
            self.logger.info("🤖 執行AI技術分析...")
            ai_analysis = self.analyzer.comprehensive_analysis(kline_data, current_price)
            
            # 組織數據
            self.latest_analysis = {
                'price': {
                    'current': current_price,
                    'high_24h': float(ticker['high']),
                    'low_24h': float(ticker['low']),
                    'volume_24h': float(ticker['volume'])
                },
                'ai_analysis': {
                    'recommendation': ai_analysis.get('recommendation', 'HOLD'),
                    'confidence': ai_analysis.get('confidence', 0),
                    'advice': ai_analysis.get('advice', '分析中...'),
                    'bullish_score': ai_analysis.get('bullish_score', 0),
                    'bearish_score': ai_analysis.get('bearish_score', 0),
                    'net_score': ai_analysis.get('net_score', 0),
                    'technical_values': ai_analysis.get('technical_values', {}),
                    'detailed_analysis': ai_analysis.get('detailed_analysis', {})
                },
                'timestamp': datetime.now().isoformat(),
                'update_interval': 30
            }
            
            self.last_update = datetime.now()
            self.logger.info(f"✅ 分析更新完成 - 建議: {ai_analysis.get('recommendation')}, 置信度: {ai_analysis.get('confidence', 0):.1f}%")
            
        except Exception as e:
            self.logger.error(f"❌ 更新分析數據失敗: {e}")
            # 如果更新失敗，至少提供基本錯誤信息
            self.latest_analysis = {
                'error': '分析更新失敗',
                'timestamp': datetime.now().isoformat()
            }
    
    async def health_check(self, request: web_request.Request):
        """健康檢查"""
        return web.json_response({
            'status': 'healthy',
            'service': 'Streaming Analysis API',
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'timestamp': datetime.now().isoformat()
        })
    
    async def start_server(self):
        """啟動服務器"""
        self.logger.info(f"🚀 啟動直播分析API服務器 - 端口: {self.port}")
        
        # 立即執行第一次分析
        self.logger.info("📊 執行初始分析...")
        await self.update_analysis()
        
        # 啟動定期更新任務
        asyncio.create_task(self.periodic_update())
        
        # 啟動web服務器
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        self.logger.info(f"✅ 直播分析API服務器已啟動")
        self.logger.info(f"   - API端點: http://localhost:{self.port}/api/analysis")
        self.logger.info(f"   - 直播疊加: http://localhost:{self.port}/overlay")
        self.logger.info(f"   - 健康檢查: http://localhost:{self.port}/api/health")
        
        return site
    
    async def periodic_update(self):
        """定期更新分析數據"""
        while True:
            try:
                await asyncio.sleep(30)  # 每30秒更新
                self.logger.info("🔄 定期更新分析數據...")
                await self.update_analysis()
            except Exception as e:
                self.logger.error(f"❌ 定期更新失敗: {e}")
                await asyncio.sleep(60)  # 失敗後等待1分鐘再試

async def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='YouTube直播AI技術分析API')
    parser.add_argument('--port', type=int, default=8888, help='API服務器端口')
    args = parser.parse_args()
    
    # 創建並啟動API服務器
    api_server = StreamingAnalysisAPI(port=args.port)
    await api_server.start_server()
    
    try:
        # 保持服務器運行
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 服務器停止")

if __name__ == "__main__":
    asyncio.run(main()) 