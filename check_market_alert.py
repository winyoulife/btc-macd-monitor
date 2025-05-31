#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
緊急市場檢查 - 診斷警報系統
"""

import asyncio
import logging
from datetime import datetime
from max_api import MaxAPI
from advanced_crypto_analyzer import AdvancedCryptoAnalyzer

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def emergency_market_check():
    """緊急市場檢查"""
    try:
        print("🚨 緊急市場檢查開始...")
        print("=" * 50)
        
        # 初始化API
        max_api = MaxAPI()
        analyzer = AdvancedCryptoAnalyzer()
        
        # 1. 檢查當前價格
        print("📊 檢查當前市場狀態...")
        ticker = max_api.get_ticker('btctwd')
        
        if ticker:
            current_price = ticker['price']
            print(f"💰 當前BTC價格: {current_price:,.0f} TWD")
            print(f"📈 24h最高: {ticker['high']:,.0f} TWD")
            print(f"📉 24h最低: {ticker['low']:,.0f} TWD")
            print(f"📊 24h成交量: {ticker['volume']:,.0f}")
        else:
            print("❌ 無法獲取價格數據")
            return
        
        print("\n" + "=" * 50)
        
        # 2. 獲取最新K線數據
        print("📈 獲取最新K線數據...")
        klines_df = max_api.get_klines('btctwd', period=60, limit=50)
        
        if klines_df is not None and not klines_df.empty:
            latest_close = klines_df['close'].iloc[-1]
            prev_close = klines_df['close'].iloc[-2]
            price_change = ((latest_close - prev_close) / prev_close) * 100
            
            print(f"📊 最新K線收盤價: {latest_close:,.0f} TWD")
            print(f"📊 前一根K線收盤價: {prev_close:,.0f} TWD")
            print(f"📈 價格變化: {price_change:+.2f}%")
            
            # 檢查最近幾根K線的趨勢
            if len(klines_df) >= 5:
                recent_closes = klines_df['close'].iloc[-5:].tolist()
                print(f"📊 最近5根K線收盤價: {[f'{x:,.0f}' for x in recent_closes]}")
                
                # 計算5分鐘內的總變化
                total_change = ((recent_closes[-1] - recent_closes[0]) / recent_closes[0]) * 100
                print(f"📈 5根K線總變化: {total_change:+.2f}%")
        else:
            print("❌ 無法獲取K線數據")
            return
        
        print("\n" + "=" * 50)
        
        # 3. 執行AI技術分析
        print("🤖 執行AI技術分析...")
        
        # 直接使用DataFrame進行分析
        analysis_result = await asyncio.get_event_loop().run_in_executor(
            None, analyzer.comprehensive_analysis, klines_df, current_price
        )
        
        print(f"🎯 AI建議: {analysis_result['recommendation']}")
        print(f"🔥 置信度: {analysis_result['confidence']:.1f}%")
        print(f"📊 MACD: {analysis_result['indicators']['macd']:.2f}")
        print(f"📊 RSI: {analysis_result['indicators']['rsi']:.1f}")
        print(f"📊 活躍指標: {analysis_result['active_indicators']}/5")
        
        print("\n" + "=" * 50)
        
        # 4. 檢查警報觸發條件
        print("🚨 檢查警報觸發條件...")
        
        confidence = analysis_result['confidence']
        recommendation = analysis_result['recommendation']
        
        print(f"當前置信度: {confidence:.1f}%")
        print(f"警報閾值: 65%")
        print(f"是否觸發警報: {'✅ 是' if confidence >= 65 else '❌ 否'}")
        
        if confidence < 65:
            print(f"⚠️  警報未觸發原因: 置信度 {confidence:.1f}% < 65%")
            print(f"💡 需要至少2個指標達到50%以上強度才能獲得高置信度")
        
        # 5. 檢查價格變化警報
        if abs(price_change) > 1.0:  # 如果價格變化超過1%
            print(f"🔥 檢測到重大價格變化: {price_change:+.2f}%")
            if price_change > 1.0:
                print("📈 建議: 可能有看漲機會，建議關注")
            else:
                print("📉 建議: 可能有看跌風險，建議注意")
        
        print("\n" + "=" * 50)
        print("✅ 緊急市場檢查完成")
        
    except Exception as e:
        logger.error(f"緊急檢查失敗: {e}")
        print(f"❌ 檢查失敗: {e}")

if __name__ == "__main__":
    asyncio.run(emergency_market_check()) 