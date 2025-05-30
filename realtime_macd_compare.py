#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
即時MACD比較工具
用於找出最接近MAX交易所顯示的MACD計算方式
"""

import time
from max_api import MaxAPI
from enhanced_macd_analyzer import EnhancedMACDAnalyzer

def realtime_compare():
    """即時比較不同週期的MACD值"""
    print("🔄 即時MACD比較工具")
    print("按 Ctrl+C 停止")
    
    max_api = MaxAPI()
    analyzer = EnhancedMACDAnalyzer()
    
    # 要測試的週期
    periods_to_test = [1, 5, 15, 30, 60]
    
    try:
        while True:
            print("\n" + "="*80)
            print(f"⏰ {time.strftime('%H:%M:%S')}")
            
            # 獲取當前價格
            ticker = max_api.get_ticker('btctwd')
            if ticker:
                print(f"💰 當前價格: ${ticker['price']:,.0f} TWD")
            
            print("\n📊 不同週期MACD值:")
            
            for period in periods_to_test:
                try:
                    # 獲取K線
                    limit = 1000 if period == 1 else 500
                    kline_data = max_api.get_klines('btctwd', period=period, limit=limit)
                    
                    if kline_data is None:
                        print(f"❌ {period}分鐘: 無法獲取資料")
                        continue
                    
                    # 計算MACD
                    df_with_macd = analyzer.calculate_macd(kline_data)
                    
                    if df_with_macd is None:
                        print(f"❌ {period}分鐘: MACD計算失敗")
                        continue
                    
                    latest = df_with_macd.iloc[-1]
                    macd = latest['macd']
                    signal = latest['macd_signal']
                    histogram = latest['macd_histogram']
                    
                    print(f"🔹 {period:2d}分鐘: MACD={macd:8.1f}, Signal={signal:8.1f}, Hist={histogram:8.1f}")
                    
                except Exception as e:
                    print(f"❌ {period}分鐘: 錯誤 - {e}")
            
            print(f"\n💡 請在MAX上查看當前MACD值，找出最接近的週期")
            print(f"📋 然後告訴我哪個週期最接近")
            
            # 等待5秒
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n👋 比較工具已停止")

if __name__ == "__main__":
    realtime_compare() 