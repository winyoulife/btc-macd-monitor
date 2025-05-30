#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
新聞獲取器 - 獲取BTC相關的即時新聞
支持多個新聞源和中文翻譯
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re

class NewsFetcher:
    """新聞獲取器類"""
    
    def __init__(self):
        self.logger = logging.getLogger('NewsFetcher')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_crypto_news(self, limit: int = 3) -> List[Dict[str, str]]:
        """獲取加密貨幣新聞"""
        news_list = []
        
        try:
            # 嘗試多個新聞源
            sources = [
                self._get_coindesk_news,
                self._get_google_news,
                self._get_yahoo_finance_news
            ]
            
            for source_func in sources:
                try:
                    source_news = source_func(limit)
                    if source_news:
                        news_list.extend(source_news)
                        if len(news_list) >= limit:
                            break
                except Exception as e:
                    self.logger.warning(f"新聞源獲取失敗: {e}")
                    continue
            
            # 去重並限制數量
            seen_titles = set()
            unique_news = []
            for news in news_list:
                if news['title'] not in seen_titles:
                    seen_titles.add(news['title'])
                    unique_news.append(news)
                    if len(unique_news) >= limit:
                        break
            
            return unique_news
            
        except Exception as e:
            self.logger.error(f"獲取新聞失敗: {e}")
            return []
    
    def _get_coindesk_news(self, limit: int = 3) -> List[Dict[str, str]]:
        """從CoinDesk獲取新聞"""
        try:
            # CoinDesk RSS feed
            url = "https://www.coindesk.com/arc/outboundfeeds/rss/"
            
            # 簡化的RSS解析
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            news_list = []
            content = response.text
            
            # 簡單的RSS item提取
            items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
            
            for item in items[:limit]:
                title_match = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
                link_match = re.search(r'<link>(.*?)</link>', item)
                desc_match = re.search(r'<description><!\[CDATA\[(.*?)\]\]></description>', item)
                
                if title_match and link_match:
                    title = title_match.group(1).strip()
                    # 過濾BTC相關新聞
                    if any(keyword.lower() in title.lower() for keyword in ['bitcoin', 'btc', '比特幣']):
                        news_list.append({
                            'title': self._translate_to_chinese(title),
                            'summary': self._translate_to_chinese(desc_match.group(1).strip()[:100] + "...") if desc_match else "",
                            'source': 'CoinDesk',
                            'time': '剛剛'
                        })
            
            return news_list
            
        except Exception as e:
            self.logger.warning(f"CoinDesk新聞獲取失敗: {e}")
            return []
    
    def _get_google_news(self, limit: int = 3) -> List[Dict[str, str]]:
        """從Google新聞獲取BTC相關新聞"""
        try:
            # Google新聞RSS (中文)
            search_terms = "比特幣 OR Bitcoin OR BTC"
            url = f"https://news.google.com/rss/search?q={search_terms}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            news_list = []
            content = response.text
            
            # 簡單的RSS item提取
            items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
            
            for item in items[:limit]:
                title_match = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
                link_match = re.search(r'<link>(.*?)</link>', item)
                pub_date_match = re.search(r'<pubDate>(.*?)</pubDate>', item)
                
                if title_match:
                    title = title_match.group(1).strip()
                    # 移除新聞源信息
                    title = re.sub(r' - .*$', '', title)
                    
                    time_str = "剛剛"
                    if pub_date_match:
                        try:
                            pub_date = pub_date_match.group(1)
                            # 簡化時間顯示
                            if "hour" in pub_date or "小時" in pub_date:
                                time_str = "幾小時前"
                            elif "min" in pub_date or "分鐘" in pub_date:
                                time_str = "幾分鐘前"
                        except:
                            pass
                    
                    news_list.append({
                        'title': title,
                        'summary': '',
                        'source': 'Google新聞',
                        'time': time_str
                    })
            
            return news_list
            
        except Exception as e:
            self.logger.warning(f"Google新聞獲取失敗: {e}")
            return []
    
    def _get_yahoo_finance_news(self, limit: int = 3) -> List[Dict[str, str]]:
        """獲取Yahoo Finance BTC新聞"""
        try:
            # 使用Yahoo Finance API
            url = "https://query1.finance.yahoo.com/v1/finance/search"
            params = {
                'q': 'bitcoin',
                'quotesCount': 0,
                'newsCount': limit,
                'enableFuzzyQuery': False,
                'quotesQueryId': 'tss_match_phrase_query',
                'multiQuoteQueryId': 'multi_quote_single_token_query',
                'newsQueryId': 'news_cie_vespa',
                'enableCb': True,
                'enableNavLinks': True,
                'enableEnhancedTrivialQuery': True
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            news_list = []
            if 'news' in data:
                for item in data['news'][:limit]:
                    title = item.get('title', '')
                    summary = item.get('summary', '')
                    
                    # 翻譯標題和摘要
                    title_zh = self._translate_to_chinese(title)
                    summary_zh = self._translate_to_chinese(summary[:100] + "..." if len(summary) > 100 else summary)
                    
                    news_list.append({
                        'title': title_zh,
                        'summary': summary_zh,
                        'source': 'Yahoo Finance',
                        'time': '剛剛'
                    })
            
            return news_list
            
        except Exception as e:
            self.logger.warning(f"Yahoo Finance新聞獲取失敗: {e}")
            return []
    
    def _translate_to_chinese(self, text: str) -> str:
        """簡單的英文到中文翻譯"""
        if not text:
            return text
            
        # 檢查是否已經是中文
        if re.search(r'[\u4e00-\u9fff]', text):
            return text
        
        # 簡單的關鍵詞翻譯映射
        translations = {
            'Bitcoin': '比特幣',
            'BTC': 'BTC',
            'cryptocurrency': '加密貨幣',
            'crypto': '加密貨幣',
            'blockchain': '區塊鏈',
            'mining': '挖礦',
            'wallet': '錢包',
            'exchange': '交易所',
            'trading': '交易',
            'price': '價格',
            'market': '市場',
            'bull': '牛市',
            'bear': '熊市',
            'rally': '上漲',
            'crash': '崩盤',
            'dip': '下跌',
            'surge': '飆漲',
            'falls': '下跌',
            'rises': '上漲',
            'drops': '下跌',
            'climbs': '攀升',
            'hits': '達到',
            'reaches': '到達',
            'breaks': '突破',
            'support': '支撐',
            'resistance': '阻力',
            'bullish': '看漲',
            'bearish': '看跌',
            'volatile': '波動',
            'volatility': '波動性',
            'institutional': '機構',
            'adoption': '採用',
            'regulation': '監管',
            'regulatory': '監管',
            'SEC': '美國證交會',
            'ETF': 'ETF基金',
            'futures': '期貨',
            'options': '選擇權'
        }
        
        # 進行關鍵詞替換
        translated_text = text
        for en, zh in translations.items():
            translated_text = re.sub(r'\b' + re.escape(en) + r'\b', zh, translated_text, flags=re.IGNORECASE)
        
        return translated_text
    
    def format_news_summary(self, news_list: List[Dict[str, str]]) -> str:
        """格式化新聞摘要"""
        if not news_list:
            return "📰 <b>相關新聞:</b> 暫無最新新聞"
        
        formatted = "📰 <b>相關新聞:</b>\n"
        
        for i, news in enumerate(news_list, 1):
            title = news['title']
            source = news['source']
            time_str = news['time']
            
            # 限制標題長度
            if len(title) > 50:
                title = title[:47] + "..."
            
            formatted += f"   {i}. {title}\n"
            formatted += f"      <i>📍 {source} • {time_str}</i>\n"
            
            if news['summary']:
                summary = news['summary']
                if len(summary) > 80:
                    summary = summary[:77] + "..."
                formatted += f"      💬 {summary}\n"
            
            formatted += "\n"
        
        return formatted.strip()

# 測試函數
def test_news_fetcher():
    """測試新聞獲取功能"""
    fetcher = NewsFetcher()
    news = fetcher.get_crypto_news(3)
    print("獲取到的新聞:")
    for i, item in enumerate(news, 1):
        print(f"{i}. {item['title']}")
        print(f"   來源: {item['source']}")
        print(f"   時間: {item['time']}")
        if item['summary']:
            print(f"   摘要: {item['summary']}")
        print()

if __name__ == "__main__":
    test_news_fetcher() 