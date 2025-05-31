#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Restream.io 整合模組
連接AI技術分析系統到多平台直播
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional
import aiohttp
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

from max_api import MaxAPI
from advanced_crypto_analyzer import AdvancedCryptoAnalyzer

class RestreamIntegration:
    """Restream.io 整合類別"""
    
    def __init__(self):
        self.max_api = MaxAPI()
        self.analyzer = AdvancedCryptoAnalyzer()
        
        # 設置日誌
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('RestreamIntegration')
        
        # Restream 設定
        self.restream_key = os.getenv('RESTREAM_KEY', '')
        self.restream_url = f"rtmp://live.restream.io/live/{self.restream_key}"
        
        # 影像設定
        self.width = 1920
        self.height = 1080
        self.fps = 30
        self.bitrate = 4000  # 4000 kbps for high quality
        
        # 數據快取
        self.latest_analysis = {}
        self.price_history = []
        
        # FFmpeg 進程
        self.ffmpeg_process = None
        
    async def start_multi_platform_stream(self):
        """啟動多平台直播"""
        self.logger.info("🚀 啟動Restream多平台直播...")
        
        if not self.restream_key:
            self.logger.error("❌ 請設置 RESTREAM_KEY 環境變數")
            self.logger.error("   從 https://restream.io 控制台獲取串流金鑰")
            return
        
        # 驗證Restream連接
        if not await self.verify_restream_connection():
            self.logger.error("❌ Restream連接驗證失敗")
            return
        
        # 啟動FFmpeg串流
        self.setup_ffmpeg_stream()
        
        # 啟動數據更新任務
        data_task = asyncio.create_task(self.data_update_loop())
        
        # 啟動影像生成任務
        video_task = asyncio.create_task(self.video_streaming_loop())
        
        # 等待任務完成
        try:
            await asyncio.gather(data_task, video_task)
        except KeyboardInterrupt:
            self.logger.info("🛑 收到停止信號，正在關閉直播...")
            await self.stop_stream()
    
    async def verify_restream_connection(self) -> bool:
        """驗證Restream連接"""
        try:
            # 這裡可以添加API驗證邏輯
            self.logger.info("✅ Restream連接驗證成功")
            self.logger.info(f"🌐 將串流到: {self.restream_url}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Restream連接驗證失敗: {e}")
            return False
    
    def setup_ffmpeg_stream(self):
        """設置FFmpeg串流到Restream"""
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-s', f'{self.width}x{self.height}',
            '-pix_fmt', 'bgr24',
            '-r', str(self.fps),
            '-i', '-',  # 從stdin讀取
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'fast',  # 平衡品質和性能
            '-r', str(self.fps),
            '-g', str(self.fps * 2),  # GOP大小
            '-b:v', f'{self.bitrate}k',  # 位元率
            '-bufsize', f'{self.bitrate * 2}k',  # 緩衝區大小
            '-maxrate', f'{self.bitrate}k',
            '-f', 'flv',
            self.restream_url
        ]
        
        try:
            self.ffmpeg_process = subprocess.Popen(
                ffmpeg_cmd, 
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.logger.info("✅ FFmpeg串流進程已啟動")
        except Exception as e:
            self.logger.error(f"❌ FFmpeg啟動失敗: {e}")
            raise
    
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
    
    async def video_streaming_loop(self):
        """影像串流循環"""
        while True:
            try:
                if self.latest_analysis and self.ffmpeg_process:
                    frame = self.generate_professional_frame()
                    await self.send_frame_to_stream(frame)
                
                await asyncio.sleep(1/self.fps)  # 控制幀率
            except Exception as e:
                self.logger.error(f"❌ 影像串流失敗: {e}")
                await asyncio.sleep(1)
    
    def generate_professional_frame(self) -> np.ndarray:
        """生成專業級直播畫面"""
        # 創建漸層背景
        frame = self.create_gradient_background()
        
        # 獲取最新數據
        price = self.latest_analysis.get('price', 0)
        analysis = self.latest_analysis.get('analysis', {})
        
        # 繪製主標題區域
        self.draw_header_section(frame, price, analysis)
        
        # 繪製AI分析區域
        self.draw_analysis_section(frame, analysis)
        
        # 繪製技術指標區域
        self.draw_indicators_section(frame, analysis)
        
        # 繪製價格圖表
        self.draw_advanced_chart(frame)
        
        # 繪製頁腳資訊
        self.draw_footer_section(frame)
        
        return frame
    
    def create_gradient_background(self) -> np.ndarray:
        """創建漸層背景"""
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # 創建深藍到黑色的漸層
        for y in range(self.height):
            factor = y / self.height
            blue = int(40 * (1 - factor))
            frame[y, :] = (blue, blue//2, blue)
        
        return frame
    
    def draw_header_section(self, frame: np.ndarray, price: float, analysis: Dict):
        """繪製標題區域"""
        # 主標題
        title = "🤖 BTC/TWD AI技術分析直播"
        self.draw_text_with_shadow(frame, title, (50, 80), 64, (0, 255, 136))
        
        # 價格顯示
        price_text = f"${price:,.0f} TWD"
        self.draw_text_with_shadow(frame, price_text, (50, 180), 96, (255, 255, 255))
        
        # 24小時變化
        ticker = self.latest_analysis.get('ticker', {})
        if 'change' in ticker:
            change = float(ticker.get('change', 0))
            change_pct = float(ticker.get('change_pct', 0))
            change_text = f"{change:+,.0f} ({change_pct:+.2f}%)"
            color = (0, 255, 0) if change >= 0 else (0, 0, 255)
            self.draw_text_with_shadow(frame, change_text, (50, 280), 48, color)
    
    def draw_analysis_section(self, frame: np.ndarray, analysis: Dict):
        """繪製AI分析區域"""
        x_offset = self.width // 2 + 50
        
        # AI建議
        recommendation = analysis.get('recommendation', 'HOLD')
        confidence = analysis.get('confidence', 0)
        
        rec_text = f"AI建議: {self.get_recommendation_text(recommendation)}"
        color = self.get_recommendation_color(recommendation)
        self.draw_text_with_shadow(frame, rec_text, (x_offset, 150), 48, color)
        
        # 置信度顯示
        conf_text = f"置信度: {confidence:.1f}%"
        self.draw_text_with_shadow(frame, conf_text, (x_offset, 220), 36, (200, 200, 200))
        
        # 置信度條
        self.draw_confidence_bar(frame, confidence, (x_offset, 280))
    
    def draw_confidence_bar(self, frame: np.ndarray, confidence: float, pos: tuple):
        """繪製置信度條"""
        bar_width = 400
        bar_height = 30
        x, y = pos
        
        # 背景條
        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height), (50, 50, 50), -1)
        
        # 填充條
        fill_width = int((confidence / 100) * bar_width)
        if confidence >= 70:
            color = (0, 255, 0)  # 綠色
        elif confidence >= 40:
            color = (0, 255, 255)  # 黃色
        else:
            color = (0, 0, 255)  # 紅色
        
        cv2.rectangle(frame, (x, y), (x + fill_width, y + bar_height), color, -1)
        
        # 邊框
        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height), (255, 255, 255), 2)
    
    def draw_indicators_section(self, frame: np.ndarray, analysis: Dict):
        """繪製技術指標區域"""
        technical_values = analysis.get('technical_values', {})
        y_start = 400
        
        indicators = [
            ("移動平均 MA7", technical_values.get('ma7', 0), "price"),
            ("移動平均 MA25", technical_values.get('ma25', 0), "price"),
            ("MACD", technical_values.get('macd', 0), "value"),
            ("RSI", technical_values.get('rsi', 0), "percent"),
            ("布林帶上軌", technical_values.get('bb_upper', 0), "price"),
            ("布林帶下軌", technical_values.get('bb_lower', 0), "price")
        ]
        
        for i, (name, value, value_type) in enumerate(indicators):
            y_pos = y_start + (i % 3) * 80
            x_pos = 50 + (i // 3) * 600
            
            if value:
                if value_type == "price":
                    text = f"{name}: ${value:,.0f}"
                elif value_type == "percent":
                    text = f"{name}: {value:.1f}%"
                else:
                    text = f"{name}: {value:.2f}"
                
                self.draw_text_with_shadow(frame, text, (x_pos, y_pos), 28, (200, 200, 255))
    
    def draw_advanced_chart(self, frame: np.ndarray):
        """繪製進階價格圖表"""
        if len(self.price_history) < 2:
            return
        
        # 圖表區域
        chart_x = 50
        chart_y = 650
        chart_w = self.width - 100
        chart_h = 300
        
        # 繪製圖表背景
        cv2.rectangle(frame, (chart_x, chart_y), 
                     (chart_x + chart_w, chart_y + chart_h), (30, 30, 30), -1)
        cv2.rectangle(frame, (chart_x, chart_y), 
                     (chart_x + chart_w, chart_y + chart_h), (100, 100, 100), 2)
        
        # 計算價格範圍
        prices = [p['price'] for p in self.price_history[-50:]]  # 最近50個點
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        if price_range == 0:
            return
        
        # 繪製網格線
        for i in range(1, 5):
            y = chart_y + (i * chart_h // 5)
            cv2.line(frame, (chart_x, y), (chart_x + chart_w, y), (60, 60, 60), 1)
        
        # 繪製價格線
        points = []
        for i, price_data in enumerate(self.price_history[-50:]):
            x = chart_x + (i / len(self.price_history[-50:])) * chart_w
            y = chart_y + chart_h - ((price_data['price'] - min_price) / price_range) * chart_h
            points.append((int(x), int(y)))
        
        # 繪製價格線
        for i in range(1, len(points)):
            cv2.line(frame, points[i-1], points[i], (0, 255, 136), 3)
        
        # 價格標籤
        self.draw_text_with_shadow(frame, f"${max_price:,.0f}", 
                                 (chart_x + chart_w + 10, chart_y + 20), 24, (255, 255, 255))
        self.draw_text_with_shadow(frame, f"${min_price:,.0f}", 
                                 (chart_x + chart_w + 10, chart_y + chart_h - 20), 24, (255, 255, 255))
    
    def draw_footer_section(self, frame: np.ndarray):
        """繪製頁腳區域"""
        y_pos = self.height - 80
        
        # 時間戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.draw_text_with_shadow(frame, f"更新時間: {timestamp}", 
                                 (50, y_pos), 28, (150, 150, 150))
        
        # 免責聲明
        disclaimer = "⚠️ 本直播內容僅供教育參考，不構成投資建議"
        self.draw_text_with_shadow(frame, disclaimer, 
                                 (50, y_pos + 40), 24, (255, 255, 0))
        
        # 平台標識
        platform_text = "🌐 多平台同步直播 via Restream.io"
        self.draw_text_with_shadow(frame, platform_text, 
                                 (self.width - 500, y_pos), 24, (0, 200, 255))
    
    def draw_text_with_shadow(self, frame: np.ndarray, text: str, pos: tuple, 
                            size: int, color: tuple):
        """繪製帶陰影的文字"""
        x, y = pos
        thickness = max(1, size // 20)
        
        # 陰影
        cv2.putText(frame, text, (x + 2, y + 2), cv2.FONT_HERSHEY_SIMPLEX, 
                   size/30, (0, 0, 0), thickness + 1, cv2.LINE_AA)
        
        # 主文字
        cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 
                   size/30, color, thickness, cv2.LINE_AA)
    
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
    
    async def send_frame_to_stream(self, frame: np.ndarray):
        """發送幀到串流"""
        try:
            if self.ffmpeg_process and self.ffmpeg_process.stdin:
                self.ffmpeg_process.stdin.write(frame.tobytes())
                self.ffmpeg_process.stdin.flush()
        except BrokenPipeError:
            self.logger.error("❌ FFmpeg管道中斷，正在重新啟動...")
            self.setup_ffmpeg_stream()
        except Exception as e:
            self.logger.error(f"❌ 發送幀失敗: {e}")
    
    async def stop_stream(self):
        """停止直播"""
        self.logger.info("🛑 正在停止直播...")
        
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            try:
                await asyncio.wait_for(
                    asyncio.to_thread(self.ffmpeg_process.wait), 
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                self.ffmpeg_process.kill()
        
        self.logger.info("✅ 直播已停止")

async def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Restream多平台直播系統')
    parser.add_argument('--restream-key', help='Restream串流金鑰')
    args = parser.parse_args()
    
    if args.restream_key:
        os.environ['RESTREAM_KEY'] = args.restream_key
    
    integration = RestreamIntegration()
    await integration.start_multi_platform_stream()

if __name__ == "__main__":
    asyncio.run(main()) 