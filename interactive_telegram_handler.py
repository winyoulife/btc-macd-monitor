#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
交互式Telegram消息处理器
处理用户的买进/卖出询问，提供AI分析建议
"""

import asyncio
import logging
import os
import re
from datetime import datetime
from typing import Dict, Optional, Any
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, filters, ContextTypes

from max_api import MaxAPI
from enhanced_macd_analyzer import EnhancedMACDAnalyzer

class InteractiveTelegramHandler:
    """交互式Telegram处理器"""
    
    def __init__(self, bot_token: str, chat_id: str, cloud_monitor):
        self.bot_token = bot_token
        self.chat_id = int(chat_id)
        self.cloud_monitor = cloud_monitor
        self.max_api = MaxAPI()
        self.macd_analyzer = EnhancedMACDAnalyzer()
        self.logger = logging.getLogger('InteractiveTelegram')
        
        # 创建Application
        self.application = Application.builder().token(bot_token).build()
        
        # 添加消息处理器
        self.application.add_handler(
            MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message)
        )
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理接收到的消息"""
        if not update.message or update.message.chat.id != self.chat_id:
            return
            
        text = update.message.text.strip()
        self.logger.info(f"收到消息: {text}")
        
        # 检查是否是询问买进/卖出
        if self.is_trading_query(text):
            response = await self.analyze_trading_decision(text)
            await update.message.reply_text(response, parse_mode='HTML')
    
    def is_trading_query(self, text: str) -> bool:
        """判断是否为交易询问"""
        # 买进相关关键词
        buy_keywords = ['买进', '买入', '買進', '買入', 'buy', 'BUY', '进场', '進場']
        # 卖出相关关键词  
        sell_keywords = ['卖出', '卖掉', '賣出', '賣掉', 'sell', 'SELL', '出场', '出場']
        
        for keyword in buy_keywords + sell_keywords:
            if keyword in text and '?' in text:
                return True
        return False
    
    async def analyze_trading_decision(self, query: str) -> str:
        """分析交易决策并返回AI建议"""
        try:
            # 获取当前市场数据
            market_data = await self.cloud_monitor.check_market_conditions('btctwd')
            if not market_data:
                return "❌ 抱歉，目前无法获取市场数据，请稍后再试。"
            
            # 提取技术指标
            technical = market_data['technical']
            price = market_data['price']
            
            # 判断用户询问类型
            is_buy_query = any(keyword in query for keyword in ['买进', '买入', '買進', '買入', 'buy', 'BUY', '进场', '進場'])
            
            # AI分析逻辑
            analysis = self.perform_ai_analysis(technical, price, is_buy_query)
            
            # 格式化回复
            response = self.format_analysis_response(analysis, technical, price, is_buy_query)
            
            return response
            
        except Exception as e:
            self.logger.error(f"分析交易决策时出错: {e}")
            return "❌ 分析过程中出现错误，请稍后再试。"
    
    def perform_ai_analysis(self, technical: Dict, price: Dict, is_buy_query: bool) -> Dict[str, Any]:
        """执行AI分析"""
        macd = technical['macd']
        signal = technical['macd_signal']
        histogram = technical['macd_histogram']
        rsi = technical['rsi']
        
        analysis = {
            'recommendation': 'HOLD',
            'confidence': 50,
            'reasons': [],
            'risk_level': 'MEDIUM',
            'short_term_outlook': 'NEUTRAL',
            'long_term_outlook': 'NEUTRAL'
        }
        
        # MACD分析
        if macd > signal:
            if histogram > 0:
                analysis['reasons'].append("MACD位于信号线上方，柱状图为正值，显示上涨动能")
                analysis['short_term_outlook'] = 'BULLISH'
                if is_buy_query:
                    analysis['confidence'] += 20
            else:
                analysis['reasons'].append("MACD位于信号线上方但柱状图收窄，上涨动能减弱")
                if not is_buy_query:
                    analysis['confidence'] += 10
        else:
            if histogram < 0:
                analysis['reasons'].append("MACD位于信号线下方，柱状图为负值，显示下跌动能")
                analysis['short_term_outlook'] = 'BEARISH'
                if not is_buy_query:
                    analysis['confidence'] += 20
            else:
                analysis['reasons'].append("MACD位于信号线下方但柱状图收窄，下跌动能减弱")
                if is_buy_query:
                    analysis['confidence'] += 10
        
        # RSI分析
        if rsi > 70:
            analysis['reasons'].append(f"RSI={rsi:.1f}，市场处于超买状态，回调风险较高")
            analysis['risk_level'] = 'HIGH'
            if not is_buy_query:
                analysis['confidence'] += 15
        elif rsi < 30:
            analysis['reasons'].append(f"RSI={rsi:.1f}，市场处于超卖状态，反弹概率较高")
            analysis['risk_level'] = 'LOW'
            if is_buy_query:
                analysis['confidence'] += 15
        else:
            analysis['reasons'].append(f"RSI={rsi:.1f}，市场处于中性区域")
        
        # 综合判断
        if analysis['confidence'] >= 70:
            if is_buy_query and analysis['short_term_outlook'] == 'BULLISH':
                analysis['recommendation'] = 'BUY'
            elif not is_buy_query and analysis['short_term_outlook'] == 'BEARISH':
                analysis['recommendation'] = 'SELL'
        elif analysis['confidence'] <= 40:
            analysis['recommendation'] = 'WAIT'
        
        # 调整置信度范围
        analysis['confidence'] = min(85, max(15, analysis['confidence']))
        
        return analysis
    
    def format_analysis_response(self, analysis: Dict, technical: Dict, price: Dict, is_buy_query: bool) -> str:
        """格式化分析回复"""
        query_type = "买进" if is_buy_query else "卖出"
        
        # 建议emoji
        if analysis['recommendation'] == 'BUY':
            rec_emoji = '🚀'
            rec_text = '建议买进'
            rec_color = '🟢'
        elif analysis['recommendation'] == 'SELL':
            rec_emoji = '📉'
            rec_text = '建议卖出'
            rec_color = '🔴'
        elif analysis['recommendation'] == 'WAIT':
            rec_emoji = '⏳'
            rec_text = '建议等待'
            rec_color = '🟡'
        else:
            rec_emoji = '⚖️'
            rec_text = '建议持有'
            rec_color = '🟡'
        
        # 风险等级emoji
        risk_emojis = {'LOW': '🟢', 'MEDIUM': '🟡', 'HIGH': '🔴'}
        risk_emoji = risk_emojis.get(analysis['risk_level'], '🟡')
        
        # 置信度条
        confidence = analysis['confidence']
        confidence_bar = '█' * (confidence // 10) + '░' * (10 - confidence // 10)
        
        response = f"""
🤖 <b>AI交易分析回复</b>

❓ <b>您的询问:</b> {query_type}?

{rec_color} <b>AI建议:</b> {rec_emoji} {rec_text}
📊 <b>置信度:</b> {confidence}% [{confidence_bar}]
⚠️ <b>风险等级:</b> {risk_emoji} {analysis['risk_level']}

💰 <b>当前市场数据:</b>
• 价格: ${price['current']:,.0f} TWD
• 24H高: ${price['high_24h']:,.0f} TWD
• 24H低: ${price['low_24h']:,.0f} TWD

📈 <b>技术指标:</b>
• MACD: {technical['macd']:.2f}
• Signal: {technical['macd_signal']:.2f}
• Histogram: {technical['macd_histogram']:.2f}
• RSI: {technical['rsi']:.1f}

🔍 <b>分析依据:</b>
"""
        
        for i, reason in enumerate(analysis['reasons'], 1):
            response += f"   {i}. {reason}\n"
        
        # 添加市场展望
        outlook_emojis = {'BULLISH': '📈', 'BEARISH': '📉', 'NEUTRAL': '➡️'}
        short_emoji = outlook_emojis.get(analysis['short_term_outlook'], '➡️')
        long_emoji = outlook_emojis.get(analysis['long_term_outlook'], '➡️')
        
        response += f"""
🔮 <b>市场展望:</b>
• 短期: {short_emoji} {analysis['short_term_outlook']}
• 长期: {long_emoji} {analysis['long_term_outlook']}

⏰ <b>分析时间:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<i>⚠️ 此为AI技术分析，仅供参考，请结合其他信息并谨慎决策</i>
        """
        
        return response.strip()
    
    async def start_polling(self):
        """启动消息轮询"""
        self.logger.info("启动Telegram消息处理器...")
        try:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            self.logger.info("Telegram消息处理器已启动")
        except Exception as e:
            self.logger.error(f"启动消息处理器失败: {e}")
    
    async def stop_polling(self):
        """停止消息轮询"""
        try:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            self.logger.info("Telegram消息处理器已停止")
        except Exception as e:
            self.logger.error(f"停止消息处理器失败: {e}") 