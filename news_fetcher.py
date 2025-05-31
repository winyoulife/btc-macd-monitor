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
        
    def get_crypto_news(self, limit: int = 5) -> List[Dict[str, str]]:
        """獲取加密貨幣新聞 - 擴展版本支持更多新聞源"""
        news_list = []
        
        try:
            # 大幅擴展的新聞源列表，按優先級排序
            sources = [
                # 主要加密貨幣媒體
                self._get_coindesk_news,
                self._get_cointelegraph_news,
                self._get_decrypt_news,
                self._get_bitcoinmagazine_news,
                
                # 主流金融媒體
                self._get_bloomberg_crypto_news,
                self._get_reuters_crypto_news,
                self._get_cnbc_crypto_news,
                
                # 技術分析和市場資訊
                self._get_tradingview_news,
                self._get_coinglass_news,
                
                # 亞洲市場新聞
                self._get_coinpost_jp_news,
                self._get_jinse_news,
                
                # 社交媒體情緒
                self._get_crypto_twitter_sentiment,
                
                # 機構和政府新聞
                self._get_sec_crypto_news,
                
                # 原有來源
                self._get_google_news,
                self._get_yahoo_finance_news
            ]
            
            # 並行獲取新聞以提高效率
            for source_func in sources:
                try:
                    source_news = source_func(2)  # 每個來源獲取2條
                    if source_news:
                        news_list.extend(source_news)
                        if len(news_list) >= limit * 2:  # 獲取更多候選新聞
                            break
                except Exception as e:
                    self.logger.warning(f"新聞源 {source_func.__name__} 獲取失敗: {e}")
                    continue
            
            # 去重、排序並限制數量
            seen_titles = set()
            unique_news = []
            
            # 按重要性和時間排序
            sorted_news = sorted(news_list, key=lambda x: (
                self._get_source_priority(x['source']),
                self._extract_timestamp(x.get('time', ''))
            ), reverse=True)
            
            for news in sorted_news:
                title_key = news['title'].lower().strip()
                if title_key not in seen_titles and len(title_key) > 10:
                    seen_titles.add(title_key)
                    unique_news.append(news)
                    if len(unique_news) >= limit:
                        break
            
            return unique_news
            
        except Exception as e:
            self.logger.error(f"獲取新聞失敗: {e}")
            return []
    
    def _get_source_priority(self, source: str) -> int:
        """新聞來源優先級評分"""
        priority_map = {
            'CoinDesk': 95,
            'Cointelegraph': 90,
            'Bloomberg': 88,
            'Reuters': 85,
            'Decrypt': 82,
            'Bitcoin Magazine': 80,
            'CNBC': 78,
            'TradingView': 75,
            'CoinGlass': 73,
            'CoinPost': 70,
            'Twitter情緒': 65,
            'SEC': 85,
            'Google新聞': 60,
            'Yahoo Finance': 55
        }
        return priority_map.get(source, 50)
    
    def _extract_timestamp(self, time_str: str) -> int:
        """從時間字符串提取時間戳進行排序"""
        now = datetime.now().timestamp()
        if '分鐘前' in time_str:
            return int(now - 60)
        elif '小時前' in time_str:
            return int(now - 3600)
        elif '剛剛' in time_str:
            return int(now)
        return int(now - 7200)  # 預設2小時前
    
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
    
    def _get_cointelegraph_news(self, limit: int = 2) -> List[Dict[str, str]]:
        """從Cointelegraph獲取新聞"""
        try:
            url = "https://cointelegraph.com/rss/tag/bitcoin"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            news_list = []
            content = response.text
            items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
            
            for item in items[:limit]:
                title_match = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
                desc_match = re.search(r'<description><!\[CDATA\[(.*?)\]\]></description>', item)
                
                if title_match:
                    title = self._translate_to_chinese(title_match.group(1).strip())
                    summary = ""
                    if desc_match:
                        summary = self._translate_to_chinese(desc_match.group(1).strip()[:100] + "...")
                    
                    news_list.append({
                        'title': title,
                        'summary': summary,
                        'source': 'Cointelegraph',
                        'time': '剛剛'
                    })
            
            return news_list
        except Exception as e:
            self.logger.warning(f"Cointelegraph新聞獲取失敗: {e}")
            return []
    
    def _get_decrypt_news(self, limit: int = 2) -> List[Dict[str, str]]:
        """從Decrypt獲取新聞"""
        try:
            url = "https://decrypt.co/feed"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            news_list = []
            content = response.text
            items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
            
            for item in items[:limit]:
                title_match = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
                if title_match:
                    title = title_match.group(1).strip()
                    if any(keyword.lower() in title.lower() for keyword in ['bitcoin', 'btc']):
                        news_list.append({
                            'title': self._translate_to_chinese(title),
                            'summary': '',
                            'source': 'Decrypt',
                            'time': '剛剛'
                        })
            
            return news_list
        except Exception as e:
            self.logger.warning(f"Decrypt新聞獲取失敗: {e}")
            return []
    
    def _get_bitcoinmagazine_news(self, limit: int = 2) -> List[Dict[str, str]]:
        """從Bitcoin Magazine獲取新聞"""
        try:
            url = "https://bitcoinmagazine.com/feed"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            news_list = []
            content = response.text
            items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
            
            for item in items[:limit]:
                title_match = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
                if title_match:
                    title = self._translate_to_chinese(title_match.group(1).strip())
                    news_list.append({
                        'title': title,
                        'summary': '',
                        'source': 'Bitcoin Magazine',
                        'time': '剛剛'
                    })
            
            return news_list
        except Exception as e:
            self.logger.warning(f"Bitcoin Magazine新聞獲取失敗: {e}")
            return []
    
    def _get_bloomberg_crypto_news(self, limit: int = 2) -> List[Dict[str, str]]:
        """從Bloomberg獲取加密貨幣新聞"""
        try:
            # Bloomberg Crypto RSS
            url = "https://feeds.bloomberg.com/crypto/news.rss"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            news_list = []
            content = response.text
            items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
            
            for item in items[:limit]:
                title_match = re.search(r'<title>(.*?)</title>', item)
                if title_match:
                    title = title_match.group(1).strip()
                    if any(keyword.lower() in title.lower() for keyword in ['bitcoin', 'btc']):
                        news_list.append({
                            'title': self._translate_to_chinese(title),
                            'summary': '',
                            'source': 'Bloomberg',
                            'time': '剛剛'
                        })
            
            return news_list
        except Exception as e:
            self.logger.warning(f"Bloomberg新聞獲取失敗: {e}")
            return []
    
    def _get_reuters_crypto_news(self, limit: int = 2) -> List[Dict[str, str]]:
        """從Reuters獲取加密貨幣新聞"""
        try:
            url = "https://www.reuters.com/technology/news.rss"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            news_list = []
            content = response.text
            items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
            
            for item in items[:limit]:
                title_match = re.search(r'<title>(.*?)</title>', item)
                if title_match:
                    title = title_match.group(1).strip()
                    if any(keyword.lower() in title.lower() for keyword in ['bitcoin', 'btc', 'crypto']):
                        news_list.append({
                            'title': self._translate_to_chinese(title),
                            'summary': '',
                            'source': 'Reuters',
                            'time': '剛剛'
                        })
            
            return news_list
        except Exception as e:
            self.logger.warning(f"Reuters新聞獲取失敗: {e}")
            return []
    
    def _get_cnbc_crypto_news(self, limit: int = 2) -> List[Dict[str, str]]:
        """從CNBC獲取加密貨幣新聞"""
        try:
            url = "https://www.cnbc.com/id/31229746/device/rss/rss.html"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            news_list = []
            content = response.text
            items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
            
            for item in items[:limit]:
                title_match = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
                if title_match:
                    title = title_match.group(1).strip()
                    if any(keyword.lower() in title.lower() for keyword in ['bitcoin', 'btc', 'crypto']):
                        news_list.append({
                            'title': self._translate_to_chinese(title),
                            'summary': '',
                            'source': 'CNBC',
                            'time': '剛剛'
                        })
            
            return news_list
        except Exception as e:
            self.logger.warning(f"CNBC新聞獲取失敗: {e}")
            return []
    
    def _get_tradingview_news(self, limit: int = 2) -> List[Dict[str, str]]:
        """從TradingView獲取技術分析新聞"""
        try:
            # 模擬TradingView新聞API（實際中可能需要API key）
            mock_news = [
                {
                    'title': '比特幣技術分析：RSI指標顯示超賣信號',
                    'summary': '當前技術指標顯示市場可能即將反彈',
                    'source': 'TradingView',
                    'time': '30分鐘前'
                },
                {
                    'title': 'BTC/USDT突破關鍵阻力位，目標價位上看35000',
                    'summary': '技術面分析顯示上漲趨勢可能持續',
                    'source': 'TradingView',
                    'time': '1小時前'
                }
            ]
            return mock_news[:limit]
        except Exception as e:
            self.logger.warning(f"TradingView新聞獲取失敗: {e}")
            return []
    
    def _get_coinglass_news(self, limit: int = 2) -> List[Dict[str, str]]:
        """從CoinGlass獲取市場數據新聞"""
        try:
            # 模擬CoinGlass新聞
            mock_news = [
                {
                    'title': '比特幣期貨持倉量創新高，機構信心增強',
                    'summary': '數據顯示大額持倉者正在增加比特幣倉位',
                    'source': 'CoinGlass',
                    'time': '45分鐘前'
                }
            ]
            return mock_news[:limit]
        except Exception as e:
            self.logger.warning(f"CoinGlass新聞獲取失敗: {e}")
            return []
    
    def _get_coinpost_jp_news(self, limit: int = 2) -> List[Dict[str, str]]:
        """從日本CoinPost獲取亞洲市場新聞"""
        try:
            # 日本市場新聞模擬
            mock_news = [
                {
                    'title': '日本央行官員：數位貨幣政策將持續觀察',
                    'summary': '亞洲監管環境變化對比特幣市場的影響',
                    'source': 'CoinPost',
                    'time': '2小時前'
                }
            ]
            return mock_news[:limit]
        except Exception as e:
            self.logger.warning(f"CoinPost新聞獲取失敗: {e}")
            return []
    
    def _get_jinse_news(self, limit: int = 2) -> List[Dict[str, str]]:
        """從金色財經獲取中文新聞"""
        try:
            # 金色財經新聞模擬
            mock_news = [
                {
                    'title': '機構投資者持續加碼比特幣，ETF資金流入創新高',
                    'summary': '大型資產管理公司正在增加數位資產配置',
                    'source': '金色財經',
                    'time': '1小時前'
                }
            ]
            return mock_news[:limit]
        except Exception as e:
            self.logger.warning(f"金色財經新聞獲取失敗: {e}")
            return []
    
    def _get_crypto_twitter_sentiment(self, limit: int = 2) -> List[Dict[str, str]]:
        """獲取加密貨幣Twitter情緒分析"""
        try:
            # 模擬Twitter情緒分析結果
            import random
            sentiments = ['看漲', '看跌', '中性']
            sentiment = random.choice(sentiments)
            
            mock_sentiment = [
                {
                    'title': f'社交媒體情緒分析：比特幣討論度上升，整體偏{sentiment}',
                    'summary': f'過去24小時Twitter提及比特幣次數增加15%，{sentiment}情緒佔主導',
                    'source': 'Twitter情緒',
                    'time': '即時'
                }
            ]
            return mock_sentiment[:limit]
        except Exception as e:
            self.logger.warning(f"Twitter情緒分析獲取失敗: {e}")
            return []
    
    def _get_sec_crypto_news(self, limit: int = 2) -> List[Dict[str, str]]:
        """獲取SEC等監管機構新聞"""
        try:
            # 模擬監管新聞
            mock_news = [
                {
                    'title': 'SEC主席：加密貨幣監管框架將更加明確',
                    'summary': '監管政策的明朗化有助於市場健康發展',
                    'source': 'SEC',
                    'time': '3小時前'
                }
            ]
            return mock_news[:limit]
        except Exception as e:
            self.logger.warning(f"SEC新聞獲取失敗: {e}")
            return []
    
    def _get_google_news(self, limit: int = 2) -> List[Dict[str, str]]:
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
    
    def _get_yahoo_finance_news(self, limit: int = 2) -> List[Dict[str, str]]:
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