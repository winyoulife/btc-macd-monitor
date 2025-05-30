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
        # 看漲關鍵詞及權重
        self.bullish_keywords = {
            # 強烈看漲
            'surge': 3, 'soar': 3, 'rally': 3, 'boom': 3, 'explode': 3,
            'skyrocket': 3, 'moonshot': 3, 'breakthrough': 3, 'adoption': 3,
            '飆漲': 3, '暴漲': 3, '突破': 3, '大漲': 3, '採用': 3, '看漲': 3,
            
            # 中等看漲  
            'rise': 2, 'climb': 2, 'gain': 2, 'up': 2, 'bull': 2, 'bullish': 2,
            'positive': 2, 'optimistic': 2, 'confidence': 2, 'approval': 2,
            '上漲': 2, '攀升': 2, '牛市': 2, '樂觀': 2, '利好': 2, '看好': 2,
            
            # 輕微看漲
            'recover': 1, 'stable': 1, 'steady': 1, 'support': 1, 'hold': 1,
            '回升': 1, '穩定': 1, '支撐': 1, '企穩': 1, '持穩': 1
        }
        
        # 看跌關鍵詞及權重
        self.bearish_keywords = {
            # 強烈看跌
            'crash': -3, 'plunge': -3, 'collapse': -3, 'dump': -3, 'panic': -3,
            'bloodbath': -3, 'massacre': -3, 'catastrophe': -3, 'ban': -3,
            '崩盤': -3, '暴跌': -3, '大跌': -3, '禁止': -3, '恐慌': -3, '血洗': -3,
            
            # 中等看跌
            'fall': -2, 'drop': -2, 'decline': -2, 'bear': -2, 'bearish': -2,
            'negative': -2, 'concern': -2, 'worry': -2, 'regulation': -2,
            '下跌': -2, '下滑': -2, '熊市': -2, '看跌': -2, '擔憂': -2, '監管': -2,
            
            # 輕微看跌
            'dip': -1, 'correction': -1, 'pressure': -1, 'resistance': -1,
            '回調': -1, '修正': -1, '壓力': -1, '阻力': -1, '調整': -1
        }
        
        # 中性關鍵詞
        self.neutral_keywords = {
            'trade': 0, 'trading': 0, 'market': 0, 'price': 0, 'volume': 0,
            '交易': 0, '市場': 0, '價格': 0, '成交量': 0
        }
    
    def analyze_news_sentiment(self, news_list: List[Dict[str, str]]) -> Dict:
        """分析新聞列表的整體情緒"""
        if not news_list:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0,
                'bullish_probability': 50,
                'bearish_probability': 50,
                'confidence': 0,
                'analysis': '無新聞數據可分析'
            }
        
        total_score = 0
        news_count = len(news_list)
        detailed_analysis = []
        
        for news in news_list:
            title = news.get('title', '')
            summary = news.get('summary', '')
            text = (title + ' ' + summary).lower()
            
            news_score = self._calculate_sentiment_score(text)
            total_score += news_score
            
            sentiment = self._score_to_sentiment(news_score)
            detailed_analysis.append({
                'title': title[:40] + '...' if len(title) > 40 else title,
                'score': news_score,
                'sentiment': sentiment
            })
        
        # 計算平均情緒分數
        avg_score = total_score / news_count
        
        # 轉換為概率
        bullish_prob, bearish_prob = self._score_to_probability(avg_score)
        
        # 計算置信度
        confidence = min(90, abs(avg_score) * 20 + 30)
        
        # 整體情緒
        overall_sentiment = self._score_to_sentiment(avg_score)
        
        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_score': avg_score,
            'bullish_probability': bullish_prob,
            'bearish_probability': bearish_prob,
            'confidence': confidence,
            'news_count': news_count,
            'detailed_analysis': detailed_analysis,
            'analysis': self._generate_analysis_text(avg_score, bullish_prob, bearish_prob)
        }
    
    def _calculate_sentiment_score(self, text: str) -> float:
        """計算單條新聞的情緒分數"""
        score = 0
        
        # 檢查看漲關鍵詞
        for keyword, weight in self.bullish_keywords.items():
            if keyword.lower() in text:
                score += weight
        
        # 檢查看跌關鍵詞
        for keyword, weight in self.bearish_keywords.items():
            if keyword.lower() in text:
                score += weight  # weight已經是負數
        
        # 限制分數範圍
        return max(-5, min(5, score))
    
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