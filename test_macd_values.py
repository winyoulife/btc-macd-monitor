#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MACD數值測試程式
用於檢查我們的計算結果與MAX交易所的差異
"""

import pandas as pd
from max_api import MaxAPI
from enhanced_macd_analyzer import EnhancedMACDAnalyzer

def test_macd_calculation():
    """測試MACD計算"""
    print("🔍 測試MACD計算值...")
    
    # 初始化
    max_api = MaxAPI()
    macd_analyzer = EnhancedMACDAnalyzer()
    
    # 測試不同週期
    periods = [1, 5, 10, 15, 30, 60, 240, 1440]  # 增加10分鐘和30分鐘測試
    
    for period in periods:
        print(f"\n📊 測試 {period} 分鐘週期:")
        
        try:
            # 獲取K線數據
            if period == 1:
                limit = 1000  # 1分鐘線需要更多資料
            elif period <= 60:
                limit = 500
            else:
                limit = 200
                
            kline_data = max_api.get_klines('btctwd', period=period, limit=limit)
            
            if kline_data is None or len(kline_data) == 0:
                print(f"❌ 無法獲取 {period} 分鐘K線數據")
                continue
            
            print(f"✅ 獲取到 {len(kline_data)} 根K線")
            print(f"📈 最新收盤價: {kline_data['close'].iloc[-1]:,.2f}")
            
            # 計算MACD
            df_with_macd = macd_analyzer.calculate_macd(kline_data)
            
            if df_with_macd is None or len(df_with_macd) == 0:
                print(f"❌ MACD計算失敗")
                continue
            
            # 顯示最新MACD值
            latest = df_with_macd.iloc[-1]
            macd = latest['macd']
            signal = latest['macd_signal'] 
            histogram = latest['macd_histogram']
            
            print(f"🎯 MACD: {macd:.1f}")
            print(f"🎯 Signal: {signal:.1f}")  
            print(f"🎯 Histogram: {histogram:.1f}")
            
            # 如果是1分鐘線，也打印前幾個值
            if period == 1:
                print("\n📋 最近5個MACD值:")
                for i in range(-5, 0):
                    row = df_with_macd.iloc[i]
                    print(f"  {i}: MACD={row['macd']:.1f}, Signal={row['macd_signal']:.1f}, Hist={row['macd_histogram']:.1f}")
            
        except Exception as e:
            print(f"❌ 錯誤: {e}")
    
    print(f"\n💡 MAX顯示的參考值: MACD=-4020.3, Signal=-14199.1, Histogram=-10178.8")
    print("🔍 請比較上述計算結果，找出最接近的週期")

if __name__ == "__main__":
    test_macd_calculation() 