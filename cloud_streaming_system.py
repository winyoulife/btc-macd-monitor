#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
雲端自動直播系統
無需本地電腦24小時開機的YouTube直播解決方案
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import aiohttp
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

from max_api import MaxAPI
from advanced_crypto_analyzer import AdvancedCryptoAnalyzer

class CloudStreamingSystem:
    """雲端自動直播系統"""
    
    def __init__(self):
        self.max_api = MaxAPI()
        self.analyzer = AdvancedCryptoAnalyzer()
        
        # 設置日誌
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('CloudStreaming')
        
        # 直播設定
        self.youtube_stream_key = os.getenv('YOUTUBE_STREAM_KEY', '')
        self.stream_url = "rtmp://a.rtmp.youtube.com/live2/"
        
        # 影像設定
        self.width = 1920
        self.height = 1080
        self.fps = 30
        
        # 數據快取
        self.latest_analysis = {}
        self.price_history = []
        
    async def start_streaming(self):
        """啟動雲端直播"""
        self.logger.info("🚀 啟動雲端自動直播系統...")
        
        if not self.youtube_stream_key:
            self.logger.error("❌ 請設置 YOUTUBE_STREAM_KEY 環境變數")
            return
        
        # 啟動數據更新任務
        data_task = asyncio.create_task(self.data_update_loop())
        
        # 啟動影像生成任務
        video_task = asyncio.create_task(self.video_generation_loop())
        
        # 等待任務完成
        await asyncio.gather(data_task, video_task)
    
    async def data_update_loop(self):
        """數據更新循環"""
        while True:
            try:
                await self.update_market_data()
                await asyncio.sleep(30)  # 每30秒更新一次
            except Exception as e:
                self.logger.error(f"❌ 數據更新失敗: {e}")
                await asyncio.sleep(60)
    
    async def update_market_data(self):
        """更新市場數據和AI分析"""
        try:
            # 獲取價格數據
            ticker = self.max_api.get_ticker('btctwd')
            if not ticker:
                raise Exception("無法獲取價格數據")
            
            current_price = float(ticker['price'])
            
            # 更新價格歷史
            self.price_history.append({
                'price': current_price,
                'timestamp': datetime.now()
            })
            
            # 保持最近100個價格點
            if len(self.price_history) > 100:
                self.price_history = self.price_history[-100:]
            
            # 獲取K線數據並執行AI分析
            kline_data = self.max_api.get_klines('btctwd', period=60, limit=200)
            if kline_data is not None and not kline_data.empty:
                analysis = self.analyzer.comprehensive_analysis(kline_data, current_price)
                
                self.latest_analysis = {
                    'price': current_price,
                    'analysis': analysis,
                    'ticker': ticker,
                    'timestamp': datetime.now()
                }
                
                self.logger.info(f"✅ 數據更新完成 - 價格: ${current_price:,.0f}, 建議: {analysis.get('recommendation', 'N/A')}")
            
        except Exception as e:
            self.logger.error(f"❌ 更新市場數據失敗: {e}")
    
    async def video_generation_loop(self):
        """影像生成循環"""
        while True:
            try:
                if self.latest_analysis:
                    frame = self.generate_frame()
                    await self.stream_frame(frame)
                
                await asyncio.sleep(1/self.fps)  # 控制幀率
            except Exception as e:
                self.logger.error(f"❌ 影像生成失敗: {e}")
                await asyncio.sleep(1)
    
    def generate_frame(self) -> np.ndarray:
        """生成單幀影像"""
        # 創建背景
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        frame[:] = (20, 20, 40)  # 深藍色背景
        
        # 獲取最新數據
        price = self.latest_analysis.get('price', 0)
        analysis = self.latest_analysis.get('analysis', {})
        
        # 繪製標題
        title = "🤖 BTC/TWD AI技術分析直播"
        self.draw_text(frame, title, (50, 50), 48, (0, 255, 136))
        
        # 繪製價格
        price_text = f"${price:,.0f} TWD"
        self.draw_text(frame, price_text, (50, 150), 72, (255, 255, 255))
        
        # 繪製AI建議
        recommendation = analysis.get('recommendation', 'HOLD')
        confidence = analysis.get('confidence', 0)
        
        rec_text = f"AI建議: {self.get_recommendation_text(recommendation)}"
        color = self.get_recommendation_color(recommendation)
        self.draw_text(frame, rec_text, (50, 250), 36, color)
        
        conf_text = f"置信度: {confidence:.1f}%"
        self.draw_text(frame, conf_text, (50, 300), 28, (200, 200, 200))
        
        # 繪製技術指標
        self.draw_indicators(frame, analysis)
        
        # 繪製價格圖表
        self.draw_price_chart(frame)
        
        # 繪製時間戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.draw_text(frame, f"更新時間: {timestamp}", (50, self.height - 100), 24, (150, 150, 150))
        
        # 繪製免責聲明
        disclaimer = "⚠️ 本直播內容僅供教育參考，不構成投資建議"
        self.draw_text(frame, disclaimer, (50, self.height - 50), 20, (255, 255, 0))
        
        return frame
    
    def draw_text(self, frame: np.ndarray, text: str, pos: tuple, size: int, color: tuple):
        """在畫面上繪製文字"""
        cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 
                   size/30, color, 2, cv2.LINE_AA)
    
    def draw_indicators(self, frame: np.ndarray, analysis: Dict):
        """繪製技術指標"""
        technical_values = analysis.get('technical_values', {})
        y_offset = 400
        
        indicators = [
            ("MA7", technical_values.get('ma7', 0)),
            ("MA25", technical_values.get('ma25', 0)),
            ("MACD", technical_values.get('macd', 0)),
            ("RSI", technical_values.get('rsi', 0))
        ]
        
        for i, (name, value) in enumerate(indicators):
            if value:
                if name in ['MA7', 'MA25']:
                    text = f"{name}: ${value:,.0f}"
                else:
                    text = f"{name}: {value:.2f}"
                
                self.draw_text(frame, text, (50, y_offset + i * 40), 24, (200, 200, 255))
    
    def draw_price_chart(self, frame: np.ndarray):
        """繪製簡單的價格圖表"""
        if len(self.price_history) < 2:
            return
        
        # 圖表區域
        chart_x = self.width - 600
        chart_y = 150
        chart_w = 500
        chart_h = 300
        
        # 繪製圖表邊框
        cv2.rectangle(frame, (chart_x, chart_y), (chart_x + chart_w, chart_y + chart_h), (100, 100, 100), 2)
        
        # 計算價格範圍
        prices = [p['price'] for p in self.price_history]
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        if price_range == 0:
            return
        
        # 繪製價格線
        points = []
        for i, price_data in enumerate(self.price_history):
            x = chart_x + (i / len(self.price_history)) * chart_w
            y = chart_y + chart_h - ((price_data['price'] - min_price) / price_range) * chart_h
            points.append((int(x), int(y)))
        
        for i in range(1, len(points)):
            cv2.line(frame, points[i-1], points[i], (0, 255, 136), 2)
    
    def get_recommendation_text(self, rec: str) -> str:
        """獲取建議文字"""
        texts = {
            'STRONG_BUY': '🚀 強烈買進',
            'BUY': '📈 建議買進',
            'HOLD': '⚖️ 持有觀望',
            'SELL': '📉 建議賣出',
            'STRONG_SELL': '💥 強烈賣出'
        }
        return texts.get(rec, '分析中...')
    
    def get_recommendation_color(self, rec: str) -> tuple:
        """獲取建議顏色"""
        if 'BUY' in rec:
            return (0, 255, 136)  # 綠色
        elif 'SELL' in rec:
            return (255, 68, 68)  # 紅色
        else:
            return (255, 170, 0)  # 橙色
    
    async def stream_frame(self, frame: np.ndarray):
        """推送幀到YouTube"""
        # 這裡需要使用FFmpeg將幀推送到YouTube
        # 實際實現需要建立FFmpeg進程
        pass
    
    def setup_ffmpeg_stream(self):
        """設置FFmpeg串流"""
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-s', f'{self.width}x{self.height}',
            '-pix_fmt', 'bgr24',
            '-r', str(self.fps),
            '-i', '-',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'ultrafast',
            '-r', str(self.fps),
            '-g', str(self.fps * 2),
            '-b:v', '4000k',
            '-bufsize', '8000k',
            '-f', 'flv',
            f'{self.stream_url}{self.youtube_stream_key}'
        ]
        
        return subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

# 簡化的啟動器
class SimpleCloudStreaming:
    """簡化的雲端直播方案"""
    
    def __init__(self):
        self.logger = logging.getLogger('SimpleStreaming')
    
    async def start_image_stream(self):
        """啟動靜態圖片流直播"""
        self.logger.info("🎬 啟動簡化雲端直播...")
        
        # 這個方案使用靜態圖片 + 定期更新
        # 適合服務器資源有限的情況
        
        while True:
            try:
                # 生成當前分析圖片
                image_path = await self.generate_analysis_image()
                
                # 使用FFmpeg推送靜態圖片
                await self.stream_static_image(image_path)
                
                await asyncio.sleep(30)  # 每30秒更新一次
                
            except Exception as e:
                self.logger.error(f"❌ 簡化直播失敗: {e}")
                await asyncio.sleep(60)
    
    async def generate_analysis_image(self) -> str:
        """生成分析圖片"""
        # 創建圖片
        img = Image.new('RGB', (1920, 1080), color=(20, 20, 40))
        draw = ImageDraw.Draw(img)
        
        # 繪製內容...
        # (這裡可以添加更詳細的圖片生成邏輯)
        
        # 保存圖片
        temp_path = f"/tmp/analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        img.save(temp_path)
        
        return temp_path
    
    async def stream_static_image(self, image_path: str):
        """推送靜態圖片到YouTube"""
        # 使用FFmpeg推送靜態圖片
        pass

async def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='雲端自動直播系統')
    parser.add_argument('--mode', choices=['full', 'simple'], default='simple', 
                       help='直播模式: full=完整視頻流, simple=靜態圖片流')
    args = parser.parse_args()
    
    if args.mode == 'full':
        streaming_system = CloudStreamingSystem()
        await streaming_system.start_streaming()
    else:
        simple_system = SimpleCloudStreaming()
        await simple_system.start_image_stream()

if __name__ == "__main__":
    asyncio.run(main()) 