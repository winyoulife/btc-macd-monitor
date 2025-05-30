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
        """處理接收到的訊息"""
        # 記錄所有接收到的更新
        self.logger.info(f"🔔 收到Telegram更新: {type(update).__name__}")
        
        if not update.message:
            self.logger.debug("收到非訊息更新，忽略")
            return
            
        # 記錄所有收到的訊息，包括Chat ID
        incoming_chat_id = update.message.chat.id
        message_text = update.message.text.strip() if update.message.text else "非文字訊息"
        
        self.logger.info(f"📨 收到訊息:")
        self.logger.info(f"   來源Chat ID: {incoming_chat_id}")
        self.logger.info(f"   目標Chat ID: {self.chat_id}")
        self.logger.info(f"   訊息內容: '{message_text}'")
        self.logger.info(f"   ID匹配: {'✅ 是' if incoming_chat_id == self.chat_id else '❌ 否'}")
        
        if incoming_chat_id != self.chat_id:
            self.logger.warning(f"❌ Chat ID不匹配，忽略來自 {incoming_chat_id} 的訊息")
            return
            
        text = message_text
        self.logger.info(f"✅ 收到來自目標群組的訊息: '{text}'")
        
        # 檢查是否是詢問買進/賣出
        if self.is_trading_query(text):
            self.logger.info(f"✅ 識別為交易詢問: '{text}'")
            try:
                self.logger.info("🤖 開始執行AI分析...")
                response = await self.analyze_trading_decision(text)
                self.logger.info("📤 正在發送AI分析回覆...")
                await update.message.reply_text(response, parse_mode='HTML')
                self.logger.info("✅ AI分析回覆已發送")
            except Exception as e:
                self.logger.error(f"❌ 處理交易詢問時出錯: {e}")
                import traceback
                self.logger.error(f"詳細錯誤: {traceback.format_exc()}")
                # 發送錯誤訊息給用戶
                try:
                    await update.message.reply_text("❌ 抱歉，處理您的詢問時出現錯誤，請稍後再試。")
                except:
                    pass
        else:
            self.logger.debug(f"非交易詢問訊息: '{text}'，忽略")
    
    def is_trading_query(self, text: str) -> bool:
        """判斷是否為交易詢問"""
        # 買進相關關鍵詞
        buy_keywords = ['买进', '买入', '買進', '買入', 'buy', 'BUY', '进场', '進場']
        # 賣出相關關鍵詞  
        sell_keywords = ['卖出', '卖掉', '賣出', '賣掉', 'sell', 'SELL', '出场', '出場']
        # 測試關鍵詞
        test_keywords = ['test', 'TEST', '測試', '测试']
        
        all_keywords = buy_keywords + sell_keywords + test_keywords
        
        for keyword in all_keywords:
            if keyword in text and '?' in text:
                return True
        return False
    
    async def analyze_trading_decision(self, query: str) -> str:
        """分析交易決策並返回AI建議"""
        try:
            # 獲取當前市場數據
            market_data = await self.cloud_monitor.check_market_conditions('btctwd')
            if not market_data:
                return "❌ 抱歉，目前無法獲取市場數據，請稍後再試。"
            
            # 提取技術指標
            technical = market_data['technical']
            price = market_data['price']
            
            # 判斷用戶詢問類型
            is_buy_query = any(keyword in query for keyword in ['买进', '买入', '買進', '買入', 'buy', 'BUY', '进场', '進場'])
            
            # AI分析邏輯
            analysis = self.perform_ai_analysis(technical, price, is_buy_query)
            
            # 格式化回覆
            response = self.format_analysis_response(analysis, technical, price, is_buy_query)
            
            return response
            
        except Exception as e:
            self.logger.error(f"分析交易決策時出錯: {e}")
            return "❌ 分析過程中出現錯誤，請稍後再試。"
    
    def perform_ai_analysis(self, technical: Dict, price: Dict, is_buy_query: bool) -> Dict[str, Any]:
        """執行AI分析"""
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
                analysis['reasons'].append("MACD位於信號線上方，柱狀圖為正值，顯示上漲動能")
                analysis['short_term_outlook'] = 'BULLISH'
                if is_buy_query:
                    analysis['confidence'] += 20
            else:
                analysis['reasons'].append("MACD位於信號線上方但柱狀圖收窄，上漲動能減弱")
                if not is_buy_query:
                    analysis['confidence'] += 10
        else:
            if histogram < 0:
                analysis['reasons'].append("MACD位於信號線下方，柱狀圖為負值，顯示下跌動能")
                analysis['short_term_outlook'] = 'BEARISH'
                if not is_buy_query:
                    analysis['confidence'] += 20
            else:
                analysis['reasons'].append("MACD位於信號線下方但柱狀圖收窄，下跌動能減弱")
                if is_buy_query:
                    analysis['confidence'] += 10
        
        # RSI分析
        if rsi > 70:
            analysis['reasons'].append(f"RSI={rsi:.1f}，市場處於超買狀態，回調風險較高")
            analysis['risk_level'] = 'HIGH'
            if not is_buy_query:
                analysis['confidence'] += 15
        elif rsi < 30:
            analysis['reasons'].append(f"RSI={rsi:.1f}，市場處於超賣狀態，反彈機率較高")
            analysis['risk_level'] = 'LOW'
            if is_buy_query:
                analysis['confidence'] += 15
        else:
            analysis['reasons'].append(f"RSI={rsi:.1f}，市場處於中性區域")
        
        # 綜合判斷
        if analysis['confidence'] >= 70:
            if is_buy_query and analysis['short_term_outlook'] == 'BULLISH':
                analysis['recommendation'] = 'BUY'
            elif not is_buy_query and analysis['short_term_outlook'] == 'BEARISH':
                analysis['recommendation'] = 'SELL'
        elif analysis['confidence'] <= 40:
            analysis['recommendation'] = 'WAIT'
        
        # 調整置信度範圍
        analysis['confidence'] = min(85, max(15, analysis['confidence']))
        
        return analysis
    
    def format_analysis_response(self, analysis: Dict, technical: Dict, price: Dict, is_buy_query: bool) -> str:
        """格式化分析回覆"""
        query_type = "買進" if is_buy_query else "賣出"
        
        # 建議emoji
        if analysis['recommendation'] == 'BUY':
            rec_emoji = '🚀'
            rec_text = '建議買進'
            rec_color = '🟢'
        elif analysis['recommendation'] == 'SELL':
            rec_emoji = '📉'
            rec_text = '建議賣出'
            rec_color = '🔴'
        elif analysis['recommendation'] == 'WAIT':
            rec_emoji = '⏳'
            rec_text = '建議等待'
            rec_color = '🟡'
        else:
            rec_emoji = '⚖️'
            rec_text = '建議持有'
            rec_color = '🟡'
        
        # 風險等級emoji
        risk_emojis = {'LOW': '🟢', 'MEDIUM': '🟡', 'HIGH': '🔴'}
        risk_emoji = risk_emojis.get(analysis['risk_level'], '🟡')
        
        # 置信度條
        confidence = analysis['confidence']
        confidence_bar = '█' * (confidence // 10) + '░' * (10 - confidence // 10)
        
        response = f"""
🤖 <b>AI交易分析回覆</b>

❓ <b>您的詢問:</b> {query_type}?

{rec_color} <b>AI建議:</b> {rec_emoji} {rec_text}
📊 <b>置信度:</b> {confidence}% [{confidence_bar}]
⚠️ <b>風險等級:</b> {risk_emoji} {analysis['risk_level']}

💰 <b>目前市場數據:</b>
• 價格: ${price['current']:,.0f} TWD
• 24H最高: ${price['high_24h']:,.0f} TWD
• 24H最低: ${price['low_24h']:,.0f} TWD

📈 <b>技術指標:</b>
• MACD: {technical['macd']:.2f}
• Signal: {technical['macd_signal']:.2f}
• Histogram: {technical['macd_histogram']:.2f}
• RSI: {technical['rsi']:.1f}

🔍 <b>分析依據:</b>
"""
        
        for i, reason in enumerate(analysis['reasons'], 1):
            response += f"   {i}. {reason}\n"
        
        # 添加市場展望
        outlook_emojis = {'BULLISH': '📈', 'BEARISH': '📉', 'NEUTRAL': '➡️'}
        short_emoji = outlook_emojis.get(analysis['short_term_outlook'], '➡️')
        long_emoji = outlook_emojis.get(analysis['long_term_outlook'], '➡️')
        
        response += f"""
🔮 <b>市場展望:</b>
• 短期: {short_emoji} {analysis['short_term_outlook']}
• 長期: {long_emoji} {analysis['long_term_outlook']}

⏰ <b>分析時間:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<i>⚠️ 此為AI技術分析，僅供參考，請結合其他資訊並謹慎決策</i>
        """
        
        return response.strip()
    
    async def start_polling(self):
        """啟動訊息輪詢"""
        self.logger.info("啟動Telegram訊息處理器...")
        try:
            # 先清除任何現有的webhook，避免衝突
            self.logger.info("正在清除可能的webhook衝突...")
            bot = Bot(token=self.bot_token)
            
            try:
                webhook_info = await bot.get_webhook_info()
                if webhook_info.url:
                    self.logger.warning(f"發現現有webhook: {webhook_info.url}，正在清除...")
                    await bot.delete_webhook(drop_pending_updates=True)
                    self.logger.info("✅ Webhook已清除")
                    
                # 等待一下確保清除完成
                await asyncio.sleep(2)
            except Exception as e:
                self.logger.warning(f"清除webhook時出現問題: {e}")
            
            self.logger.info("正在初始化Application...")
            await self.application.initialize()
            self.logger.info("正在啟動Application...")
            await self.application.start()
            self.logger.info("正在啟動訊息輪詢...")
            await self.application.updater.start_polling(
                drop_pending_updates=True,  # 丟棄待處理更新
                timeout=10,                 # 設置超時
                error_callback=self._error_callback
            )
            self.logger.info("✅ Telegram訊息處理器已啟動，等待訊息...")
        except Exception as e:
            self.logger.error(f"❌ 啟動訊息處理器失敗: {e}")
            import traceback
            self.logger.error(f"詳細錯誤: {traceback.format_exc()}")
            
            # 如果是衝突錯誤，提供解決建議
            if "Conflict" in str(e):
                self.logger.error("🔧 檢測到bot衝突！請確保沒有其他實例在運行同一個bot")
                self.logger.error("   解決方案：運行 fix_bot_conflict.py 腳本")
    
    def _error_callback(self, update, context):
        """錯誤回調函數"""
        error = context.error
        self.logger.error(f"Telegram更新處理錯誤: {error}")
        
        if "Conflict" in str(error):
            self.logger.error("🔧 檢測到bot衝突，建議重啟服務")
    
    async def stop_polling(self):
        """停止訊息輪詢"""
        try:
            self.logger.info("正在停止訊息輪詢...")
            if hasattr(self.application, 'updater') and self.application.updater:
                await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            self.logger.info("✅ Telegram訊息處理器已停止")
        except Exception as e:
            self.logger.error(f"❌ 停止訊息處理器失敗: {e}")
            import traceback
            self.logger.error(f"詳細錯誤: {traceback.format_exc()}") 