#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
測試交互式Telegram功能
"""

import asyncio
import os
from cloud_monitor import CloudMonitor

async def test_interactive():
    """測試交互式功能"""
    print("🧪 測試交互式Telegram功能")
    
    # 設定環境變數（如果需要）
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        print("❌ 請設定 TELEGRAM_BOT_TOKEN 環境變數")
        return
    
    if not os.getenv('TELEGRAM_CHAT_ID'):
        print("❌ 請設定 TELEGRAM_CHAT_ID 環境變數")
        return
    
    # 建立監控實例
    monitor = CloudMonitor()
    
    # 測試市場數據獲取
    market_data = await monitor.check_market_conditions('btctwd')
    if market_data:
        print("✅ 市場數據獲取成功")
        print(f"   價格: ${market_data['price']['current']:,.0f} TWD")
        print(f"   MACD: {market_data['technical']['macd']:.2f}")
        print(f"   RSI: {market_data['technical']['rsi']:.1f}")
    else:
        print("❌ 市場數據獲取失敗")
        return
    
    # 測試AI分析
    if monitor.interactive_handler:
        print("✅ 交互式處理器已初始化")
        
        # 模擬買進詢問
        analysis = monitor.interactive_handler.perform_ai_analysis(
            market_data['technical'], 
            market_data['price'], 
            is_buy_query=True
        )
        
        print(f"✅ AI分析完成:")
        print(f"   建議: {analysis['recommendation']}")
        print(f"   置信度: {analysis['confidence']}%")
        print(f"   原因: {analysis['reasons']}")
        
        # 測試格式化回覆
        response = monitor.interactive_handler.format_analysis_response(
            analysis, 
            market_data['technical'], 
            market_data['price'], 
            is_buy_query=True
        )
        print("✅ 格式化回覆:")
        print(response[:200] + "..." if len(response) > 200 else response)
    else:
        print("❌ 交互式處理器未初始化")
    
    print("\n💡 測試完成！您現在可以:")
    print("   1. 在Telegram中發送 '買進?' 或 '賣出?'")
    print("   2. 系統會自動回覆AI分析建議")
    print("   3. 使用雲端部署來24/7響應您的詢問")

if __name__ == "__main__":
    asyncio.run(test_interactive()) 