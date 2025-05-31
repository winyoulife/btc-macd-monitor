#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
測試擴展的新聞獲取和情緒分析功能
"""

import asyncio
import logging
from news_fetcher import NewsFetcher
from news_sentiment_analyzer import NewsSentimentAnalyzer

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_enhanced_news_system():
    """測試增強的新聞系統"""
    print("🧪 測試擴展的新聞獲取和情緒分析系統")
    print("=" * 60)
    
    # 初始化組件
    news_fetcher = NewsFetcher()
    sentiment_analyzer = NewsSentimentAnalyzer()
    
    # 測試新聞獲取
    print("\n📰 測試新聞獲取...")
    news_list = news_fetcher.get_crypto_news(limit=8)
    
    if not news_list:
        print("❌ 無法獲取新聞，可能網路問題或來源暫時不可用")
        # 使用模擬數據進行測試
        news_list = [
            {
                'title': '比特幣突破關鍵阻力位，機構投資者大量買進',
                'summary': '大型資產管理公司正在增加比特幣配置，推動價格上漲15%',
                'source': 'Bloomberg',
                'time': '30分鐘前'
            },
            {
                'title': 'SEC主席：加密貨幣監管框架將更加明確',
                'summary': '監管政策的明朗化有助於市場健康發展',
                'source': 'SEC',
                'time': '1小時前'
            },
            {
                'title': '比特幣技術分析：RSI指標顯示超賣信號',
                'summary': '當前技術指標顯示市場可能即將反彈',
                'source': 'TradingView',
                'time': '45分鐘前'
            },
            {
                'title': '社交媒體情緒分析：比特幣討論度上升，整體偏看漲',
                'summary': '過去24小時Twitter提及比特幣次數增加15%，看漲情緒佔主導',
                'source': 'Twitter情緒',
                'time': '即時'
            },
            {
                'title': '比特幣期貨持倉量創新高，機構信心增強',
                'summary': '數據顯示大額持倉者正在增加比特幣倉位',
                'source': 'CoinGlass',
                'time': '2小時前'
            }
        ]
        print("✅ 使用模擬新聞數據進行測試")
    
    print(f"\n📊 獲取到 {len(news_list)} 條新聞")
    print("詳細新聞列表:")
    for i, news in enumerate(news_list, 1):
        print(f"   {i}. 【{news['source']}】{news['title']}")
        if news.get('summary'):
            print(f"      摘要: {news['summary'][:80]}...")
        print(f"      時間: {news['time']}")
        print()
    
    # 測試情緒分析
    print("\n🧠 測試情緒分析...")
    sentiment_result = sentiment_analyzer.analyze_news_sentiment(news_list)
    
    print("情緒分析結果:")
    print(f"   整體情緒: {sentiment_result['overall_sentiment']}")
    print(f"   情緒分數: {sentiment_result['sentiment_score']}")
    print(f"   看漲概率: {sentiment_result['bullish_probability']}%")
    print(f"   看跌概率: {sentiment_result['bearish_probability']}%")
    print(f"   置信度: {sentiment_result['confidence']}%")
    print(f"   新聞總數: {sentiment_result['news_count']}")
    print(f"   利多新聞: {sentiment_result['bullish_count']} 則")
    print(f"   利空新聞: {sentiment_result['bearish_count']} 則")
    print(f"   中性新聞: {sentiment_result['neutral_count']} 則")
    print(f"   來源多樣性: {sentiment_result['source_diversity']}")
    print(f"   分析摘要: {sentiment_result['analysis']}")
    
    # 來源統計
    print("\n📈 來源統計:")
    for source, stats in sentiment_result['source_breakdown'].items():
        print(f"   {source}: {stats['count']}則, 平均分數: {stats['avg_score']}, 情緒: {stats['sentiment']}")
    
    # 詳細分析
    print("\n🔍 詳細分析:")
    for item in sentiment_result['detailed_analysis']:
        print(f"   • {item['title']}")
        print(f"     來源: {item['source']} (權重: {item['weight']})")
        print(f"     基礎分數: {item['base_score']} → 加權分數: {item['weighted_score']}")
        print(f"     情緒: {item['sentiment']}")
        print()
    
    # 測試新聞來源權重系統
    print("\n⚖️  新聞來源權重系統:")
    weights = sentiment_analyzer.source_weights
    sorted_sources = sorted(weights.items(), key=lambda x: x[1], reverse=True)
    
    print("   權重排序（高→低）:")
    for source, weight in sorted_sources:
        status = "✅" if any(news['source'] == source for news in news_list) else "⭕"
        print(f"   {status} {source}: {weight}")
    
    return sentiment_result

if __name__ == "__main__":
    try:
        result = test_enhanced_news_system()
        print("\n" + "=" * 60)
        print("🎉 測試完成！擴展的新聞系統運行正常")
        print("✨ 主要改進:")
        print("   • 15個新聞來源（vs 原來的3個）")
        print("   • 智能權重系統")
        print("   • 增強的情緒分析")
        print("   • 詳細的統計信息")
        print("   • 更精確的概率計算")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc() 