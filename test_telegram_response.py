#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
測試Telegram回應格式的腳本
"""

import asyncio
import os
from datetime import datetime, timezone, timedelta
from webhook_telegram_handler import WebhookTelegramHandler
from cloud_monitor import CloudMonitor

# 台灣時區 (UTC+8)
TAIWAN_TZ = timezone(timedelta(hours=8))

async def test_response_format():
    """測試回應格式"""
    print("🧪 開始測試Telegram回應格式...")
    
    # 模擬市場數據
    market_data = {
        'technical': {
            'macd': 1234.56,
            'macd_signal': 1200.00,
            'macd_histogram': 34.56,
            'rsi': 58.2
        },
        'price': {
            'current': 3142000,
            'high_24h': 3200000,
            'low_24h': 3100000,
            'volume_24h': 156.78
        }
    }
    
    # 模擬新聞數據
    news_list = [
        {
            'title': 'Bitcoin Bulls Rack up $600M Liquidations',
            'summary': 'A cascade of liquidations might suggest a market turning point',
            'source': 'CoinDesk'
        },
        {
            'title': 'Where Will Bitcoin Be in 10 Years?',
            'summary': 'Long-term outlook analysis',
            'source': 'Yahoo Finance'
        },
        {
            'title': 'Bitcoin stumbles as Trump accuses China',
            'summary': 'Geopolitical tensions affect crypto markets',
            'source': 'Yahoo Finance'
        }
    ]
    
    # 創建模擬的CloudMonitor
    monitor = CloudMonitor()
    
    # 創建WebhookTelegramHandler
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', 'dummy_token')
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '123456789')
    
    handler = WebhookTelegramHandler(bot_token, chat_id, monitor)
    
    # 執行AI分析
    tech_analysis = handler.perform_ai_analysis(
        market_data['technical'], 
        market_data['price'], 
        True  # is_buy_query
    )
    
    # 分析新聞情緒
    sentiment_analysis = handler.sentiment_analyzer.analyze_news_sentiment(news_list)
    
    # 獲取交易建議
    trading_recommendation = handler.sentiment_analyzer.get_trading_recommendation(
        sentiment_analysis, tech_analysis
    )
    
    # 格式化回應
    response = handler.format_comprehensive_response(
        tech_analysis, 
        sentiment_analysis, 
        trading_recommendation, 
        market_data['technical'], 
        market_data['price'], 
        True,  # is_buy_query
        news_list
    )
    
    print("=" * 80)
    print("📱 模擬Telegram回應內容：")
    print("=" * 80)
    print(response)
    print("=" * 80)
    
    # 檢查關鍵變更
    checks = [
        ("移除新聞標題", "相關新聞資訊:" not in response),
        ("包含新聞統計", "24小時新聞統計:" in response),
        ("包含利多消息", "利多消息:" in response),
        ("包含利空消息", "利空消息:" in response),
        ("市場展望中文化", "樂觀看漲" in response or "謹慎看跌" in response or "中性觀望" in response),
        ("包含機率預測", "機率預測:" in response),
        ("包含上漲機率", "上漲機率:" in response),
        ("包含下跌機率", "下跌機率:" in response)
    ]
    
    print("\n✅ 功能驗證結果：")
    print("-" * 40)
    all_passed = True
    for check_name, passed in checks:
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"{check_name}: {status}")
        if not passed:
            all_passed = False
    
    print("-" * 40)
    if all_passed:
        print("🎉 所有修改都已生效！")
    else:
        print("⚠️ 部分修改可能未生效，請檢查代碼")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(test_response_format()) 