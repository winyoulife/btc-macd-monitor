#!/usr/bin/env python3

from max_api import MaxAPI
from enhanced_macd_analyzer import EnhancedMACDAnalyzer

def quick_test():
    print("📊 快速MACD測試 (30分鐘週期)")
    
    max_api = MaxAPI()
    analyzer = EnhancedMACDAnalyzer()
    
    # 獲取30分鐘K線
    kline_data = max_api.get_klines('btctwd', period=30, limit=500)
    
    if kline_data is None:
        print("❌ 無法獲取資料")
        return
    
    print(f"✅ 獲取到 {len(kline_data)} 根30分鐘K線")
    print(f"📈 最新價格: {kline_data['close'].iloc[-1]:,.0f}")
    
    # 計算MACD
    df_with_macd = analyzer.calculate_macd(kline_data)
    
    if df_with_macd is None:
        print("❌ MACD計算失敗")
        return
    
    latest = df_with_macd.iloc[-1]
    macd = latest['macd']
    signal = latest['macd_signal']
    histogram = latest['macd_histogram']
    
    print(f"\n🎯 我們的計算結果 (30分鐘):")
    print(f"   MACD: {macd:.1f}")
    print(f"   Signal: {signal:.1f}")
    print(f"   Histogram: {histogram:.1f}")
    
    print(f"\n💡 MAX顯示的參考值:")
    print(f"   MACD: -4020.3")
    print(f"   Signal: -14199.1")
    print(f"   Histogram: -10178.8")
    
    print(f"\n📊 差異分析:")
    print(f"   MACD差異: {abs(macd - (-4020.3)):,.1f}")
    print(f"   Signal差異: {abs(signal - (-14199.1)):,.1f}")
    print(f"   Histogram差異: {abs(histogram - (-10178.8)):,.1f}")

if __name__ == "__main__":
    quick_test() 