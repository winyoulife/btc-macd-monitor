#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自訂MACD計算器
嘗試不同算法來匹配MAX交易所的MACD值
"""

import pandas as pd
import numpy as np
from max_api import MaxAPI

class CustomMACDCalculator:
    def __init__(self, fast=12, slow=26, signal=9):
        self.fast = fast
        self.slow = slow
        self.signal = signal
    
    def calculate_ema(self, data, period):
        """計算指數移動平均"""
        return data.ewm(span=period, adjust=False).mean()
    
    def calculate_sma(self, data, period):
        """計算簡單移動平均"""
        return data.rolling(window=period).mean()
    
    def calculate_macd_standard(self, close_prices):
        """標準MACD計算（EMA方法）"""
        ema_fast = self.calculate_ema(close_prices, self.fast)
        ema_slow = self.calculate_ema(close_prices, self.slow)
        
        macd = ema_fast - ema_slow
        signal = self.calculate_ema(macd, self.signal)
        histogram = macd - signal
        
        return macd, signal, histogram
    
    def calculate_macd_sma_signal(self, close_prices):
        """MACD計算（信號線用SMA）"""
        ema_fast = self.calculate_ema(close_prices, self.fast)
        ema_slow = self.calculate_ema(close_prices, self.slow)
        
        macd = ema_fast - ema_slow
        signal = self.calculate_sma(macd, self.signal)  # 用SMA代替EMA
        histogram = macd - signal
        
        return macd, signal, histogram
    
    def calculate_macd_percentage(self, close_prices):
        """MACD百分比版本"""
        ema_fast = self.calculate_ema(close_prices, self.fast)
        ema_slow = self.calculate_ema(close_prices, self.slow)
        
        # 計算百分比差異
        macd = ((ema_fast - ema_slow) / ema_slow) * 100
        signal = self.calculate_ema(macd, self.signal)
        histogram = macd - signal
        
        return macd, signal, histogram

def test_custom_macd():
    """測試自訂MACD計算"""
    print("🧪 測試自訂MACD計算方法...")
    
    max_api = MaxAPI()
    calculator = CustomMACDCalculator()
    
    # 測試不同週期
    periods = [15, 30, 60]
    
    for period in periods:
        print(f"\n📊 測試 {period} 分鐘週期:")
        
        try:
            # 獲取K線數據
            limit = 500 if period <= 60 else 200
            kline_data = max_api.get_klines('btctwd', period=period, limit=limit)
            
            if kline_data is None or len(kline_data) == 0:
                print(f"❌ 無法獲取 {period} 分鐘K線數據")
                continue
            
            print(f"✅ 獲取到 {len(kline_data)} 根K線")
            close_prices = kline_data['close']
            
            # 測試不同計算方法
            print("\n🔹 標準EMA方法:")
            macd1, signal1, hist1 = calculator.calculate_macd_standard(close_prices)
            print(f"   MACD: {macd1.iloc[-1]:.1f}, Signal: {signal1.iloc[-1]:.1f}, Hist: {hist1.iloc[-1]:.1f}")
            
            print("🔹 SMA信號線方法:")
            macd2, signal2, hist2 = calculator.calculate_macd_sma_signal(close_prices)
            print(f"   MACD: {macd2.iloc[-1]:.1f}, Signal: {signal2.iloc[-1]:.1f}, Hist: {hist2.iloc[-1]:.1f}")
            
            print("🔹 百分比方法:")
            macd3, signal3, hist3 = calculator.calculate_macd_percentage(close_prices)
            print(f"   MACD: {macd3.iloc[-1]:.1f}, Signal: {signal3.iloc[-1]:.1f}, Hist: {hist3.iloc[-1]:.1f}")
            
        except Exception as e:
            print(f"❌ 錯誤: {e}")
    
    print(f"\n💡 MAX顯示的參考值: MACD=-4020.3, Signal=-14199.1, Histogram=-10178.8")
    print("🔍 請檢查哪種方法最接近")

if __name__ == "__main__":
    test_custom_macd() 