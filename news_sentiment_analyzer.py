#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
新聞情緒分析器 - 分析BTC相關新聞的市場情緒
計算漲跌概率並提供交易建議
"""

import re
from typing import List, Dict, Tuple

class NewsSentimentAnalyzer:
    """新聞情緒分析器"""
    
    def __init__(self):
        # 新聞來源權重系統
        self.source_weights = {
            'CoinDesk': 1.0,
            'Cointelegraph': 0.95,
            'Bloomberg': 1.1,     # 主流金融媒體權重較高
            'Reuters': 1.1,
            'Decrypt': 0.9,
            'Bitcoin Magazine': 0.85,
            'CNBC': 1.0,
            'TradingView': 0.8,   # 技術分析類
            'CoinGlass': 0.9,
            'CoinPost': 0.7,
            'Twitter情緒': 0.6,   # 社交媒體權重較低
            'SEC': 1.2,           # 監管新聞權重最高
            '金色財經': 0.8,
            'Google新聞': 0.7,
            'Yahoo Finance': 0.75
        }
        
        # 擴展的看漲關鍵詞及權重
        self.bullish_keywords = {
            # 強烈看漲 (3分)
            'surge': 3, 'soar': 3, 'rally': 3, 'boom': 3, 'explode': 3,
            'skyrocket': 3, 'moonshot': 3, 'breakthrough': 3, 'adoption': 3,
            'institutional': 3, 'etf approved': 3, 'mass adoption': 3,
            'all-time high': 3, 'record high': 3, 'new high': 3,
            '飆漲': 3, '暴漲': 3, '突破': 3, '大漲': 3, '採用': 3, '看漲': 3,
            '機構': 3, 'ETF通過': 3, '歷史新高': 3, '創新高': 3, '牛市': 3,
            
            # 中等看漲 (2分)
            'rise': 2, 'climb': 2, 'gain': 2, 'up': 2, 'bull': 2, 'bullish': 2,
            'positive': 2, 'optimistic': 2, 'confidence': 2, 'approval': 2,
            'upgrade': 2, 'investment': 2, 'fund': 2, 'accumulation': 2,
            'buy the dip': 2, 'oversold': 2, 'reversal': 2,
            '上漲': 2, '攀升': 2, '樂觀': 2, '利好': 2, '看好': 2, '投資': 2,
            '資金流入': 2, '超賣反彈': 2, '反轉': 2, '買進': 2, '增持': 2,
            
            # 輕微看漲 (1分)
            'recover': 1, 'stable': 1, 'steady': 1, 'support': 1, 'hold': 1,
            'resilient': 1, 'rebound': 1, 'consolidation': 1,
            '回升': 1, '穩定': 1, '支撐': 1, '企穩': 1, '持穩': 1, '反彈': 1,
            '整固': 1, '抗跌': 1, '築底': 1
        }
        
        # 擴展的看跌關鍵詞及權重
        self.bearish_keywords = {
            # 強烈看跌 (-3分)
            'crash': -3, 'plunge': -3, 'collapse': -3, 'dump': -3, 'panic': -3,
            'bloodbath': -3, 'massacre': -3, 'catastrophe': -3, 'ban': -3,
            'crackdown': -3, 'prohibition': -3, 'selloff': -3, 'liquidation': -3,
            '崩盤': -3, '暴跌': -3, '大跌': -3, '禁止': -3, '恐慌': -3, '血洗': -3,
            '清算': -3, '拋售': -3, '打壓': -3, '嚴厲監管': -3,
            
            # 中等看跌 (-2分)
            'fall': -2, 'drop': -2, 'decline': -2, 'bear': -2, 'bearish': -2,
            'negative': -2, 'concern': -2, 'worry': -2, 'regulation': -2,
            'uncertainty': -2, 'skeptical': -2, 'warning': -2, 'risk': -2,
            'overbought': -2, 'bubble': -2,
            '下跌': -2, '下滑': -2, '看跌': -2, '擔憂': -2, '監管': -2, '風險': -2,
            '超買': -2, '泡沫': -2, '警告': -2, '不確定': -2, '懷疑': -2,
            
            # 輕微看跌 (-1分)
            'dip': -1, 'correction': -1, 'pressure': -1, 'resistance': -1,
            'profit-taking': -1, 'caution': -1, 'hesitation': -1,
            '回調': -1, '修正': -1, '壓力': -1, '阻力': -1, '調整': -1,
            '獲利了結': -1, '謹慎': -1, '猶豫': -1
        }
        
        # 市場動向關鍵詞
        self.market_trend_keywords = {
            # 強勢趨勢
            'trend reversal': 2, 'breakout': 2, 'momentum': 2, 'volume spike': 2,
            'whale activity': 1, 'institutional flow': 2, 'retail fomo': 1,
            '趨勢反轉': 2, '突破': 2, '動能': 2, '成交量暴增': 2, '機構資金': 2,
            '散戶FOMO': 1, '鯨魚活動': 1,
            
            # 弱勢趨勢  
            'trend breakdown': -2, 'support broken': -2, 'volume decline': -1,
            'whale selling': -2, 'institutional exit': -2, 'retail panic': -2,
            '趨勢破壞': -2, '支撐破裂': -2, '成交量萎縮': -1, '機構撤離': -2,
            '散戶恐慌': -2, '鯨魚拋售': -2
        }
        
        # 合併所有關鍵詞
        self.all_keywords = {**self.bullish_keywords, **self.bearish_keywords, **self.market_trend_keywords}
        
        # 中性關鍵詞
        self.neutral_keywords = {
            'trade': 0, 'trading': 0, 'market': 0, 'price': 0, 'volume': 0,
            'analysis': 0, 'update': 0, 'report': 0, 'data': 0,
            '交易': 0, '市場': 0, '價格': 0, '成交量': 0, '分析': 0, '報告': 0
        }
    
    def analyze_news_sentiment(self, news_list: List[Dict[str, str]]) -> Dict:
        """分析新聞列表的整體情緒 - 增強版本支持來源權重"""
        if not news_list:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0,
                'bullish_probability': 50,
                'bearish_probability': 50,
                'confidence': 0,
                'analysis': '無新聞數據可分析',
                'source_breakdown': {}
            }
        
        total_weighted_score = 0
        total_weight = 0
        news_count = len(news_list)
        detailed_analysis = []
        source_breakdown = {}
        
        for news in news_list:
            title = news.get('title', '')
            summary = news.get('summary', '')
            source = news.get('source', 'Unknown')
            text = (title + ' ' + summary).lower()
            
            # 計算基礎情緒分數
            base_score = self._calculate_sentiment_score(text)
            
            # 獲取來源權重
            source_weight = self.source_weights.get(source, 0.5)
            
            # 加權分數
            weighted_score = base_score * source_weight
            total_weighted_score += weighted_score
            total_weight += source_weight
            
            # 情緒標籤
            sentiment = self._score_to_sentiment(base_score)
            
            # 詳細分析
            detailed_analysis.append({
                'title': title[:50] + '...' if len(title) > 50 else title,
                'source': source,
                'base_score': round(base_score, 2),
                'weight': source_weight,
                'weighted_score': round(weighted_score, 2),
                'sentiment': sentiment
            })
            
            # 來源統計
            if source not in source_breakdown:
                source_breakdown[source] = {
                    'count': 0,
                    'total_score': 0,
                    'avg_score': 0,
                    'sentiment': 'neutral'
                }
            
            source_breakdown[source]['count'] += 1
            source_breakdown[source]['total_score'] += base_score
            source_breakdown[source]['avg_score'] = round(
                source_breakdown[source]['total_score'] / source_breakdown[source]['count'], 2
            )
            source_breakdown[source]['sentiment'] = self._score_to_sentiment(
                source_breakdown[source]['avg_score']
            )
        
        # 計算加權平均情緒分數
        avg_weighted_score = total_weighted_score / total_weight if total_weight > 0 else 0
        
        # 轉換為概率
        bullish_prob, bearish_prob = self._score_to_probability(avg_weighted_score)
        
        # 計算置信度（考慮來源多樣性和權重）
        source_diversity = len(source_breakdown)
        weight_factor = min(1.0, total_weight / news_count)  # 權重因子
        confidence = min(95, abs(avg_weighted_score) * 15 + source_diversity * 5 + weight_factor * 10 + 25)
        
        # 整體情緒
        overall_sentiment = self._score_to_sentiment(avg_weighted_score)
        
        # 統計各類情緒的新聞數量
        bullish_count = sum(1 for item in detailed_analysis if item['sentiment'] == 'bullish')
        bearish_count = sum(1 for item in detailed_analysis if item['sentiment'] == 'bearish')
        neutral_count = news_count - bullish_count - bearish_count
        
        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_score': round(avg_weighted_score, 2),
            'bullish_probability': bullish_prob,
            'bearish_probability': bearish_prob,
            'confidence': round(confidence, 1),
            'news_count': news_count,
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'neutral_count': neutral_count,
            'source_diversity': source_diversity,
            'detailed_analysis': detailed_analysis,
            'source_breakdown': source_breakdown,
            'analysis': self._generate_enhanced_analysis_text(
                avg_weighted_score, bullish_prob, bearish_prob, 
                bullish_count, bearish_count, neutral_count, source_diversity
            )
        }
    
    def _calculate_sentiment_score(self, text: str) -> float:
        """計算單條新聞的情緒分數 - 使用擴展關鍵詞庫"""
        score = 0
        matched_keywords = []
        
        # 檢查所有情緒關鍵詞
        for keyword, weight in self.all_keywords.items():
            # 使用更精確的匹配模式
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text.lower()) or keyword.lower() in text.lower():
                score += weight
                matched_keywords.append((keyword, weight))
        
        # 特殊加權規則
        # 1. 如果同時出現強烈正面和負面詞，減少絕對值
        strong_positive = any(weight >= 2 for _, weight in matched_keywords)
        strong_negative = any(weight <= -2 for _, weight in matched_keywords)
        
        if strong_positive and strong_negative:
            score *= 0.7  # 混合情緒，降低強度
        
        # 2. 多個同類詞彙的遞減效應
        positive_count = sum(1 for _, weight in matched_keywords if weight > 0)
        negative_count = sum(1 for _, weight in matched_keywords if weight < 0)
        
        if positive_count > 3:
            score *= 0.85  # 避免過度正面
        if negative_count > 3:
            score *= 0.85  # 避免過度負面
        
        # 3. 數字相關的特殊處理
        if self._contains_price_movement(text):
            price_sentiment = self._analyze_price_movement(text)
            score += price_sentiment * 0.5  # 價格變動的影響
        
        # 限制分數範圍
        return max(-5, min(5, round(score, 2)))
    
    def _contains_price_movement(self, text: str) -> bool:
        """檢查是否包含價格變動信息"""
        price_patterns = [
            r'\d+%', r'\$\d+', r'up \d+', r'down \d+', r'漲\d+', r'跌\d+',
            r'上漲\d+', r'下跌\d+', r'升\d+', r'降\d+'
        ]
        return any(re.search(pattern, text) for pattern in price_patterns)
    
    def _analyze_price_movement(self, text: str) -> float:
        """分析價格變動的情緒影響"""
        score = 0
        
        # 上漲相關
        up_patterns = [
            (r'up (\d+)%', 1), (r'漲(\d+)%', 1), (r'上漲(\d+)%', 1),
            (r'升(\d+)%', 1), (r'增(\d+)%', 1)
        ]
        
        # 下跌相關
        down_patterns = [
            (r'down (\d+)%', -1), (r'跌(\d+)%', -1), (r'下跌(\d+)%', -1),
            (r'降(\d+)%', -1), (r'減(\d+)%', -1)
        ]
        
        for pattern, multiplier in up_patterns + down_patterns:
            match = re.search(pattern, text)
            if match:
                percentage = float(match.group(1))
                # 根據漲跌幅度調整情緒強度
                if percentage > 10:
                    score += multiplier * 2
                elif percentage > 5:
                    score += multiplier * 1.5
                else:
                    score += multiplier * 1
                break
        
        return score
    
    def _score_to_sentiment(self, score: float) -> str:
        """將分數轉換為情緒標籤"""
        if score > 1:
            return 'bullish'
        elif score < -1:
            return 'bearish'
        else:
            return 'neutral'
    
    def _score_to_probability(self, score: float) -> Tuple[int, int]:
        """將情緒分數轉換為漲跌概率"""
        # 基準概率50%，根據情緒分數調整
        base_prob = 50
        adjustment = score * 8  # 每分調整8%
        
        bullish_prob = max(10, min(90, base_prob + adjustment))
        bearish_prob = 100 - bullish_prob
        
        return int(bullish_prob), int(bearish_prob)
    
    def _generate_analysis_text(self, score: float, bull_prob: int, bear_prob: int) -> str:
        """生成分析文字"""
        if score > 1.5:
            return f"新聞整體偏向樂觀，市場情緒看漲，上漲概率{bull_prob}%"
        elif score > 0.5:
            return f"新聞略顏正面，市場謹慎樂觀，輕微看漲{bull_prob}%"
        elif score < -1.5:
            return f"新聞普遍負面，市場情緒看跌，下跌概率{bear_prob}%"
        elif score < -0.5:
            return f"新聞略顯負面，市場謹慎悲觀，輕微看跌{bear_prob}%"
        else:
            return f"新聞情緒中性，市場方向不明，觀望為主"
    
    def _generate_enhanced_analysis_text(self, score: float, bull_prob: int, bear_prob: int, 
                                         bullish_count: int, bearish_count: int, neutral_count: int, source_diversity: int) -> str:
        """生成增強版分析文字"""
        if score > 1.5:
            return f"新聞整體偏向樂觀，市場情緒看漲，上漲概率{bull_prob}%，來源多樣性{source_diversity}"
        elif score > 0.5:
            return f"新聞略顏正面，市場謹慎樂觀，輕微看漲{bull_prob}%，來源多樣性{source_diversity}"
        elif score < -1.5:
            return f"新聞普遍負面，市場情緒看跌，下跌概率{bear_prob}%，來源多樣性{source_diversity}"
        elif score < -0.5:
            return f"新聞略顯負面，市場謹慎悲觀，輕微看跌{bear_prob}%，來源多樣性{source_diversity}"
        else:
            return f"新聞情緒中性，市場方向不明，觀望為主，來源多樣性{source_diversity}"
    
    def get_trading_recommendation(self, sentiment_analysis: Dict, technical_analysis: Dict) -> Dict:
        """結合新聞情緒和技術分析給出交易建議"""
        news_sentiment = sentiment_analysis['overall_sentiment']
        news_confidence = sentiment_analysis['confidence']
        bull_prob = sentiment_analysis['bullish_probability']
        bear_prob = sentiment_analysis['bearish_probability']
        
        # 技術分析建議
        tech_recommendation = technical_analysis.get('recommendation', 'HOLD')
        tech_confidence = technical_analysis.get('confidence', 50)
        
        # 綜合評分
        combined_score = 0
        
        # 新聞情緒權重
        if news_sentiment == 'bullish':
            combined_score += 2
        elif news_sentiment == 'bearish':
            combined_score -= 2
        
        # 技術指標權重
        if tech_recommendation == 'BUY':
            combined_score += 1
        elif tech_recommendation == 'SELL':
            combined_score -= 1
        
        # 置信度權重
        if news_confidence > 70 and tech_confidence > 70:
            combined_score *= 1.5
        
        # 生成建議
        if combined_score >= 2:
            action = "建議進場買進"
            reason = "新聞情緒強烈看漲，技術面配合"
            risk_level = "中等"
        elif combined_score >= 1:
            action = "謹慎進場"
            reason = "新聞略偏正面，可小量建倉"
            risk_level = "中低"
        elif combined_score <= -2:
            action = "建議獲利了結/停損"
            reason = "新聞情緒悲觀，技術面走弱"
            risk_level = "較高"
        elif combined_score <= -1:
            action = "謹慎觀望"
            reason = "新聞略偏負面，暫緩進場"
            risk_level = "中等"
        else:
            action = "持有觀望"
            reason = "新聞技術面信號不明確"
            risk_level = "低"
        
        return {
            'action': action,
            'reason': reason,
            'risk_level': risk_level,
            'combined_score': combined_score,
            'probability_analysis': f"上漲{bull_prob}% vs 下跌{bear_prob}%"
        } 