import pandas as pd
import numpy as np
import ta
from datetime import datetime, timedelta
import logging
from config import MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD

class MACDAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.fast_period = MACD_FAST_PERIOD
        self.slow_period = MACD_SLOW_PERIOD
        self.signal_period = MACD_SIGNAL_PERIOD
        
    def calculate_macd(self, df):
        """計算MACD指標"""
        try:
            if df is None or len(df) < self.slow_period + self.signal_period:
                self.logger.warning("資料不足，無法計算MACD")
                return None
            
            # 計算MACD
            df = df.copy()
            df['macd'] = ta.trend.MACD(
                close=df['close'],
                window_fast=self.fast_period,
                window_slow=self.slow_period
            ).macd()
            
            df['macd_signal'] = ta.trend.MACD(
                close=df['close'],
                window_fast=self.fast_period,
                window_slow=self.slow_period
            ).macd_signal()
            
            df['macd_histogram'] = ta.trend.MACD(
                close=df['close'],
                window_fast=self.fast_period,
                window_slow=self.slow_period
            ).macd_diff()
            
            # 計算EMA
            df['ema_12'] = ta.trend.EMAIndicator(close=df['close'], window=12).ema_indicator()
            df['ema_26'] = ta.trend.EMAIndicator(close=df['close'], window=26).ema_indicator()
            
            # 計算RSI
            df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
            
            return df
            
        except Exception as e:
            self.logger.error(f"計算MACD失敗: {e}")
            return None
    
    def analyze_signal(self, df, current_price):
        """分析交易信號"""
        try:
            if df is None or len(df) < 3:
                return {
                    'signal': 'HOLD',
                    'strength': 0,
                    'reason': '資料不足',
                    'macd_current': 0,
                    'macd_signal_current': 0,
                    'histogram_current': 0,
                    'rsi_current': 50
                }
            
            # 獲取最新資料
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            macd_current = latest['macd'] if not pd.isna(latest['macd']) else 0
            macd_signal_current = latest['macd_signal'] if not pd.isna(latest['macd_signal']) else 0
            histogram_current = latest['macd_histogram'] if not pd.isna(latest['macd_histogram']) else 0
            rsi_current = latest['rsi'] if not pd.isna(latest['rsi']) else 50
            
            # 基本MACD信號
            signal = 'HOLD'
            strength = 0
            reasons = []
            
            # MACD線穿越信號線
            if macd_current > macd_signal_current and prev['macd'] <= prev['macd_signal']:
                signal = 'BUY'
                strength += 30
                reasons.append('MACD黃金交叉')
            elif macd_current < macd_signal_current and prev['macd'] >= prev['macd_signal']:
                signal = 'SELL'
                strength += 30
                reasons.append('MACD死亡交叉')
            
            # 直方圖變化
            if histogram_current > 0 and prev['macd_histogram'] <= 0:
                if signal != 'SELL':
                    signal = 'BUY'
                strength += 20
                reasons.append('直方圖轉正')
            elif histogram_current < 0 and prev['macd_histogram'] >= 0:
                if signal != 'BUY':
                    signal = 'SELL'
                strength += 20
                reasons.append('直方圖轉負')
            
            # RSI輔助判斷
            if rsi_current < 30:
                if signal == 'BUY':
                    strength += 15
                    reasons.append('RSI超賣')
                elif signal == 'SELL':
                    strength -= 10  # 減少賣出強度
            elif rsi_current > 70:
                if signal == 'SELL':
                    strength += 15
                    reasons.append('RSI超買')
                elif signal == 'BUY':
                    strength -= 10  # 減少買入強度
            
            # 價格動量
            price_change = (current_price - df.iloc[-5]['close']) / df.iloc[-5]['close'] * 100
            if abs(price_change) > 2:  # 價格變動超過2%
                if price_change > 0 and signal == 'BUY':
                    strength += 10
                    reasons.append('價格上漲動量')
                elif price_change < 0 and signal == 'SELL':
                    strength += 10
                    reasons.append('價格下跌動量')
            
            # 確保強度在合理範圍
            strength = min(100, max(0, strength))
            
            return {
                'signal': signal,
                'strength': strength,
                'reason': '; '.join(reasons) if reasons else '無明確信號',
                'macd_current': macd_current,
                'macd_signal_current': macd_signal_current,
                'histogram_current': histogram_current,
                'rsi_current': rsi_current,
                'price_change_5m': price_change
            }
            
        except Exception as e:
            self.logger.error(f"分析信號失敗: {e}")
            return {
                'signal': 'HOLD',
                'strength': 0,
                'reason': f'分析錯誤: {str(e)}',
                'macd_current': 0,
                'macd_signal_current': 0,
                'histogram_current': 0,
                'rsi_current': 50
            }
    
    def get_macd_summary(self, df):
        """獲取MACD摘要資訊"""
        if df is None or len(df) == 0:
            return None
            
        latest = df.iloc[-1]
        return {
            'macd': latest['macd'] if not pd.isna(latest['macd']) else 0,
            'signal': latest['macd_signal'] if not pd.isna(latest['macd_signal']) else 0,
            'histogram': latest['macd_histogram'] if not pd.isna(latest['macd_histogram']) else 0,
            'rsi': latest['rsi'] if not pd.isna(latest['rsi']) else 50,
            'ema_12': latest['ema_12'] if not pd.isna(latest['ema_12']) else 0,
            'ema_26': latest['ema_26'] if not pd.isna(latest['ema_26']) else 0
        } 