#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试交互式Telegram功能
"""

import asyncio
import os
from cloud_monitor import CloudMonitor

async def test_interactive():
    """测试交互式功能"""
    print("🧪 测试交互式Telegram功能")
    
    # 设置环境变量（如果需要）
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        print("❌ 请设置 TELEGRAM_BOT_TOKEN 环境变量")
        return
    
    if not os.getenv('TELEGRAM_CHAT_ID'):
        print("❌ 请设置 TELEGRAM_CHAT_ID 环境变量")
        return
    
    # 创建监控实例
    monitor = CloudMonitor()
    
    # 测试市场数据获取
    market_data = await monitor.check_market_conditions('btctwd')
    if market_data:
        print("✅ 市场数据获取成功")
        print(f"   价格: ${market_data['price']['current']:,.0f} TWD")
        print(f"   MACD: {market_data['technical']['macd']:.2f}")
        print(f"   RSI: {market_data['technical']['rsi']:.1f}")
    else:
        print("❌ 市场数据获取失败")
        return
    
    # 测试AI分析
    if monitor.interactive_handler:
        print("✅ 交互式处理器已初始化")
        
        # 模拟买进询问
        analysis = monitor.interactive_handler.perform_ai_analysis(
            market_data['technical'], 
            market_data['price'], 
            is_buy_query=True
        )
        
        print(f"✅ AI分析完成:")
        print(f"   建议: {analysis['recommendation']}")
        print(f"   置信度: {analysis['confidence']}%")
        print(f"   原因: {analysis['reasons']}")
        
        # 测试格式化回复
        response = monitor.interactive_handler.format_analysis_response(
            analysis, 
            market_data['technical'], 
            market_data['price'], 
            is_buy_query=True
        )
        print("✅ 格式化回复:")
        print(response[:200] + "..." if len(response) > 200 else response)
    else:
        print("❌ 交互式处理器未初始化")
    
    print("\n💡 测试完成！您现在可以:")
    print("   1. 在Telegram中发送 '买进?' 或 '卖出?'")
    print("   2. 系统会自动回复AI分析建议")
    print("   3. 使用云端部署来24/7响应您的询问")

if __name__ == "__main__":
    asyncio.run(test_interactive()) 