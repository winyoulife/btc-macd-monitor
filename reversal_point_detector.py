#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
技術轉折點檢測系統
專門檢測低點反彈和高點回測的關鍵時機
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from max_api import MaxAPI
from advanced_crypto_analyzer import AdvancedCryptoAnalyzer
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ReversalPointDetector:
    def __init__(self):
        self.max_api = MaxAPI()
        self.analyzer = AdvancedCryptoAnalyzer()
        self.price_history = []
        self.last_alert_time = {}
        
        # 轉折點檢測參數
        self.config = {
            'support_resistance_period': 20,  # 支撐阻力計算週期
            'reversal_confirmation_period': 3,  # 反轉確認週期
            'min_bounce_strength': 0.3,  # 最小反彈強度 (%)
            'min_pullback_strength': 0.3,  # 最小回測強度 (%)
            'alert_cooldown': 1800,  # 警報冷卻時間 (30分鐘)
        }
    
    async def send_telegram_alert(self, message):
        """發送Telegram警報"""
        try:
            bot_token = "7323086952:AAE5fkQp8n98TOYnPpj2KPyrCI6hX5R2n2I"
            chat_id = "6839863072"
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info("✅ 轉折點警報發送成功")
            else:
                logger.error(f"❌ 轉折點警報發送失敗: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ 轉折點警報發送錯誤: {e}")
    
    def calculate_support_resistance(self, df):
        """計算支撐阻力位"""
        try:
            period = self.config['support_resistance_period']
            
            # 計算局部高點和低點
            highs = df['high'].rolling(window=period, center=True).max()
            lows = df['low'].rolling(window=period, center=True).min()
            
            # 找出明顯的支撐和阻力位
            current_price = df['close'].iloc[-1]
            recent_highs = highs.dropna().tail(10)
            recent_lows = lows.dropna().tail(10)
            
            # 阻力位：比當前價格高的局部高點
            resistance_levels = recent_highs[recent_highs > current_price].unique()
            # 支撐位：比當前價格低的局部低點  
            support_levels = recent_lows[recent_lows < current_price].unique()
            
            # 取最近的支撐阻力位
            nearest_resistance = resistance_levels.min() if len(resistance_levels) > 0 else None
            nearest_support = support_levels.max() if len(support_levels) > 0 else None
            
            return {
                'support': nearest_support,
                'resistance': nearest_resistance,
                'current_price': current_price
            }
            
        except Exception as e:
            logger.error(f"計算支撐阻力位錯誤: {e}")
            return None
    
    def detect_low_point_bounce(self, df, support_resistance):
        """檢測低點反彈信號"""
        try:
            if not support_resistance or support_resistance['support'] is None:
                return None
            
            current_price = df['close'].iloc[-1]
            support_level = support_resistance['support']
            
            # 檢查是否接近支撐位
            distance_to_support = (current_price - support_level) / support_level * 100
            
            # 近期是否觸及過支撐位
            recent_period = self.config['reversal_confirmation_period']
            recent_lows = df['low'].tail(recent_period)
            touched_support = any(low <= support_level * 1.005 for low in recent_lows)  # 0.5%容錯
            
            if not touched_support:
                return None
            
            # 檢查反彈力度
            recent_closes = df['close'].tail(recent_period)
            if len(recent_closes) < 2:
                return None
                
            lowest_recent = recent_closes.min()
            bounce_strength = (current_price - lowest_recent) / lowest_recent * 100
            
            # 檢查技術指標確認
            rsi = df['rsi'].iloc[-1] if 'rsi' in df.columns else None
            macd = df['macd'].iloc[-1] if 'macd' in df.columns else None
            
            # 反彈確認條件
            conditions = {
                'near_support': distance_to_support <= 2.0,  # 距離支撐位2%內
                'touched_support': touched_support,
                'bounce_strength': bounce_strength >= self.config['min_bounce_strength'],
                'rsi_oversold': rsi is not None and rsi < 40,  # RSI超賣
                'price_rising': recent_closes.iloc[-1] > recent_closes.iloc[-2],  # 價格上升
            }
            
            # 至少滿足3個條件才發出警報
            confirmed_conditions = sum(conditions.values())
            
            if confirmed_conditions >= 3:
                return {
                    'type': 'LOW_POINT_BOUNCE',
                    'support_level': support_level,
                    'current_price': current_price,
                    'bounce_strength': bounce_strength,
                    'distance_to_support': distance_to_support,
                    'conditions_met': confirmed_conditions,
                    'rsi': rsi,
                    'confidence': min(95, confirmed_conditions * 20)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"檢測低點反彈錯誤: {e}")
            return None
    
    def detect_high_point_pullback(self, df, support_resistance):
        """檢測高點回測信號"""
        try:
            if not support_resistance or support_resistance['resistance'] is None:
                return None
            
            current_price = df['close'].iloc[-1]
            resistance_level = support_resistance['resistance']
            
            # 檢查是否接近阻力位
            distance_to_resistance = (resistance_level - current_price) / current_price * 100
            
            # 近期是否觸及過阻力位
            recent_period = self.config['reversal_confirmation_period']
            recent_highs = df['high'].tail(recent_period)
            touched_resistance = any(high >= resistance_level * 0.995 for high in recent_highs)  # 0.5%容錯
            
            if not touched_resistance:
                return None
            
            # 檢查回測力度
            recent_closes = df['close'].tail(recent_period)
            if len(recent_closes) < 2:
                return None
                
            highest_recent = recent_closes.max()
            pullback_strength = (highest_recent - current_price) / highest_recent * 100
            
            # 檢查技術指標確認
            rsi = df['rsi'].iloc[-1] if 'rsi' in df.columns else None
            macd = df['macd'].iloc[-1] if 'macd' in df.columns else None
            
            # 回測確認條件
            conditions = {
                'near_resistance': distance_to_resistance <= 2.0,  # 距離阻力位2%內
                'touched_resistance': touched_resistance,
                'pullback_strength': pullback_strength >= self.config['min_pullback_strength'],
                'rsi_overbought': rsi is not None and rsi > 60,  # RSI超買
                'price_falling': recent_closes.iloc[-1] < recent_closes.iloc[-2],  # 價格下降
            }
            
            # 至少滿足3個條件才發出警報
            confirmed_conditions = sum(conditions.values())
            
            if confirmed_conditions >= 3:
                return {
                    'type': 'HIGH_POINT_PULLBACK',
                    'resistance_level': resistance_level,
                    'current_price': current_price,
                    'pullback_strength': pullback_strength,
                    'distance_to_resistance': distance_to_resistance,
                    'conditions_met': confirmed_conditions,
                    'rsi': rsi,
                    'confidence': min(95, confirmed_conditions * 20)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"檢測高點回測錯誤: {e}")
            return None
    
    def should_send_alert(self, alert_type):
        """檢查是否應該發送警報（避免重複）"""
        now = datetime.now()
        last_time = self.last_alert_time.get(alert_type)
        
        if last_time is None:
            return True
        
        time_diff = (now - last_time).total_seconds()
        return time_diff >= self.config['alert_cooldown']
    
    async def monitor_reversal_points(self):
        """持續監控技術轉折點"""
        logger.info("🚀 開始技術轉折點監控...")
        
        while True:
            try:
                # 獲取K線數據（需要足夠的歷史數據）
                klines_df = self.max_api.get_klines('btctwd', period=60, limit=100)
                
                if klines_df is None or klines_df.empty:
                    logger.warning("❌ 無法獲取K線數據")
                    await asyncio.sleep(60)
                    continue
                
                # 計算技術指標
                klines_with_indicators = self.analyzer.calculate_all_indicators(klines_df)
                if klines_with_indicators is None:
                    logger.warning("❌ 無法計算技術指標")
                    await asyncio.sleep(60)
                    continue
                
                # 計算支撐阻力位
                support_resistance = self.calculate_support_resistance(klines_with_indicators)
                
                current_price = klines_with_indicators['close'].iloc[-1]
                
                # 檢測低點反彈
                bounce_signal = self.detect_low_point_bounce(klines_with_indicators, support_resistance)
                if bounce_signal and self.should_send_alert('LOW_POINT_BOUNCE'):
                    message = f"""
🚀 <b>低點反彈信號！買進機會</b>

💰 當前價格: {bounce_signal['current_price']:,.0f} TWD
📊 支撐位: {bounce_signal['support_level']:,.0f} TWD
📈 反彈強度: {bounce_signal['bounce_strength']:.2f}%
📍 距離支撐: {bounce_signal['distance_to_support']:.2f}%
📊 RSI: {bounce_signal['rsi']:.1f}
🔥 置信度: {bounce_signal['confidence']:.0f}%
✅ 滿足條件: {bounce_signal['conditions_met']}/5

⏰ 時間: {datetime.now().strftime('%H:%M:%S')}

#低點反彈 #買進機會 #支撐位反彈
"""
                    await self.send_telegram_alert(message.strip())
                    self.last_alert_time['LOW_POINT_BOUNCE'] = datetime.now()
                    logger.info(f"🚨 發送低點反彈警報")
                
                # 檢測高點回測
                pullback_signal = self.detect_high_point_pullback(klines_with_indicators, support_resistance)
                if pullback_signal and self.should_send_alert('HIGH_POINT_PULLBACK'):
                    message = f"""
📉 <b>高點回測信號！賣出機會</b>

💰 當前價格: {pullback_signal['current_price']:,.0f} TWD
📊 阻力位: {pullback_signal['resistance_level']:,.0f} TWD
📉 回測強度: {pullback_signal['pullback_strength']:.2f}%
📍 距離阻力: {pullback_signal['distance_to_resistance']:.2f}%
📊 RSI: {pullback_signal['rsi']:.1f}
🔥 置信度: {pullback_signal['confidence']:.0f}%
✅ 滿足條件: {pullback_signal['conditions_met']}/5

⏰ 時間: {datetime.now().strftime('%H:%M:%S')}

#高點回測 #賣出機會 #阻力位回測
"""
                    await self.send_telegram_alert(message.strip())
                    self.last_alert_time['HIGH_POINT_PULLBACK'] = datetime.now()
                    logger.info(f"🚨 發送高點回測警報")
                
                # 輸出當前監控狀態
                if support_resistance:
                    support = support_resistance['support']
                    resistance = support_resistance['resistance']
                    logger.info(f"💰 BTC: {current_price:,.0f} | 支撐: {support:,.0f if support else 'N/A'} | 阻力: {resistance:,.0f if resistance else 'N/A'}")
                else:
                    logger.info(f"💰 BTC: {current_price:,.0f} | 計算支撐阻力位中...")
                
                # 等待下次檢查（2分鐘間隔）
                await asyncio.sleep(120)
                
            except Exception as e:
                logger.error(f"❌ 轉折點監控錯誤: {e}")
                await asyncio.sleep(120)

async def main():
    """主函數"""
    detector = ReversalPointDetector()
    
    # 發送啟動通知
    startup_message = f"""
🎯 <b>技術轉折點檢測系統啟動</b>

📊 監控目標:
📈 低點反彈信號 - 買進機會
📉 高點回測信號 - 賣出機會

⚙️ 檢測設置:
• 支撐阻力計算週期: 20根K線
• 反轉確認週期: 3根K線  
• 最小反彈/回測強度: 0.3%
• 警報冷卻時間: 30分鐘

⏰ 啟動時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#轉折點檢測 #技術分析
"""
    await detector.send_telegram_alert(startup_message.strip())
    
    # 開始監控
    await detector.monitor_reversal_points()

if __name__ == "__main__":
    asyncio.run(main()) 