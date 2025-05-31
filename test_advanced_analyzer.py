#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
測試高級加密貨幣技術分析器
驗證多重技術指標分析功能
"""

import asyncio
import logging
import pandas as pd
from datetime import datetime
from advanced_crypto_analyzer import AdvancedCryptoAnalyzer
from max_api import MaxAPI

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('AdvancedAnalyzerTest')

async def test_advanced_analyzer():
    """測試高級技術分析器"""
    print("🚀 開始測試高級加密貨幣技術分析器")
    print("=" * 60)
    
    try:
        # 初始化組件
        analyzer = AdvancedCryptoAnalyzer()
        max_api = MaxAPI()
        
        # 獲取BTC/TWD市場數據
        print("📊 正在獲取BTC/TWD市場數據...")
        kline_data = max_api.get_klines('btctwd', period=60, limit=200)
        
        if kline_data is None or kline_data.empty:
            print("❌ 無法獲取K線數據")
            return
            
        print(f"✅ 成功獲取 {len(kline_data)} 條K線數據")
        
        # 獲取當前價格
        ticker = max_api.get_ticker('btctwd')
        current_price = float(ticker['price']) if ticker else 3140000.0
        
        print(f"💰 當前BTC價格: ${current_price:,.0f} TWD")
        print()
        
        # 執行綜合技術分析
        print("🤖 開始執行多重技術指標分析...")
        analysis_result = analyzer.comprehensive_analysis(kline_data, current_price)
        
        # 顯示分析結果
        print("\n📈 === 多重技術指標分析結果 ===")
        print(f"🎯 綜合建議: {analysis_result['recommendation']}")
        print(f"📊 建議說明: {analysis_result['advice']}")
        print(f"🎪 置信度: {analysis_result['confidence']:.1f}%")
        print(f"🟢 看漲分數: {analysis_result['bullish_score']:.1f}")
        print(f"🔴 看跌分數: {analysis_result['bearish_score']:.1f}")
        print(f"⚖️ 淨分數: {analysis_result['net_score']:.1f}")
        print()
        
        # 顯示各項技術指標詳細分析
        print("🔍 === 各項技術指標詳細分析 ===")
        detailed_analysis = analysis_result.get('detailed_analysis', {})
        
        # 移動平均線分析
        if 'ma_cross' in detailed_analysis:
            ma = detailed_analysis['ma_cross']
            print(f"📏 均線系統: {ma['signal']} (強度: {ma['strength']:.0f}%)")
            print(f"   └ {ma['details']}")
            ma_values = ma.get('ma_values', {})
            if ma_values:
                print(f"   └ MA7: {ma_values.get('ma7', 0):,.1f}, MA25: {ma_values.get('ma25', 0):,.1f}, MA99: {ma_values.get('ma99', 0):,.1f}")
        
        # MACD分析
        if 'macd' in detailed_analysis:
            macd = detailed_analysis['macd']
            print(f"📊 MACD: {macd['signal']} (強度: {macd['strength']:.0f}%)")
            print(f"   └ {macd['details']}")
            macd_values = macd.get('macd_values', {})
            if macd_values:
                print(f"   └ MACD: {macd_values.get('macd', 0):.2f}, Signal: {macd_values.get('signal', 0):.2f}, Histogram: {macd_values.get('histogram', 0):.2f}")
        
        # RSI分析
        if 'rsi' in detailed_analysis:
            rsi = detailed_analysis['rsi']
            print(f"📈 RSI: {rsi['signal']} (強度: {rsi['strength']:.0f}%)")
            print(f"   └ {rsi['details']}")
            print(f"   └ RSI值: {rsi.get('rsi_value', 0):.1f}")
        
        # 布林帶分析
        if 'bollinger' in detailed_analysis:
            bb = detailed_analysis['bollinger']
            print(f"📊 布林帶: {bb['signal']} (強度: {bb['strength']:.0f}%)")
            print(f"   └ {bb['details']}")
            print(f"   └ 布林帶位置: {bb.get('bb_position', 0):.2f}")
        
        # 成交量分析
        if 'volume' in detailed_analysis:
            vol = detailed_analysis['volume']
            print(f"📊 成交量: {vol['signal']} (強度: {vol['strength']:.0f}%)")
            print(f"   └ {vol['details']}")
            print(f"   └ 成交量比率: {vol.get('volume_ratio', 1):.1f}")
        
        print()
        
        # 顯示關鍵技術指標數值
        print("📊 === 關鍵技術指標數值 ===")
        tech_values = analysis_result.get('technical_values', {})
        if tech_values:
            print(f"• MA7: {tech_values.get('ma7', 0):,.1f} TWD")
            print(f"• MA25: {tech_values.get('ma25', 0):,.1f} TWD")
            print(f"• MA99: {tech_values.get('ma99', 0):,.1f} TWD")
            print(f"• MACD: {tech_values.get('macd', 0):.2f}")
            print(f"• MACD Signal: {tech_values.get('macd_signal', 0):.2f}")
            print(f"• MACD Histogram: {tech_values.get('macd_histogram', 0):.2f}")
            print(f"• RSI: {tech_values.get('rsi', 0):.1f}")
            print(f"• 布林帶位置: {tech_values.get('bb_position', 0):.2f}")
            print(f"• 成交量比率: {tech_values.get('volume_ratio', 1):.1f}")
        
        print()
        
        # 測試格式化報告
        print("📝 === 格式化分析報告 ===")
        formatted_report = analyzer.format_analysis_report(analysis_result)
        print(formatted_report)
        
        # 評估分析系統效能
        print("\n🎯 === 分析系統評估 ===")
        
        # 指標覆蓋率
        indicator_count = len(detailed_analysis)
        expected_indicators = 5  # ma_cross, macd, rsi, bollinger, volume
        coverage = (indicator_count / expected_indicators) * 100
        
        print(f"📈 指標覆蓋率: {indicator_count}/{expected_indicators} ({coverage:.0f}%)")
        
        # 信號強度評估
        if analysis_result['confidence'] >= 70:
            confidence_level = "🟢 高"
        elif analysis_result['confidence'] >= 50:
            confidence_level = "🟡 中等"
        else:
            confidence_level = "🔴 低"
            
        print(f"🎪 置信度評級: {confidence_level}")
        
        # 多重指標一致性
        bullish_indicators = sum(1 for analysis in detailed_analysis.values() if analysis['signal'] == 'BULLISH')
        bearish_indicators = sum(1 for analysis in detailed_analysis.values() if analysis['signal'] == 'BEARISH')
        neutral_indicators = sum(1 for analysis in detailed_analysis.values() if analysis['signal'] == 'NEUTRAL')
        
        print(f"📊 指標方向分布: 看漲{bullish_indicators}個, 看跌{bearish_indicators}個, 中性{neutral_indicators}個")
        
        if bullish_indicators > bearish_indicators:
            consensus = "🟢 偏多頭"
        elif bearish_indicators > bullish_indicators:
            consensus = "🔴 偏空頭"
        else:
            consensus = "🟡 分歧"
            
        print(f"🎯 指標共識: {consensus}")
        
        print("\n✅ 高級技術分析器測試完成！")
        print("=" * 60)
        
        return analysis_result
        
    except Exception as e:
        print(f"❌ 測試過程中出現錯誤: {e}")
        import traceback
        print(f"詳細錯誤: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    asyncio.run(test_advanced_analyzer()) 