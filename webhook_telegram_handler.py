#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Webhook模式Telegram處理器
專為雲端環境設計，解決長輪詢被阻擋的問題
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Any, List
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from aiohttp import web
import os

from max_api import MaxAPI
from enhanced_macd_analyzer import EnhancedMACDAnalyzer
from news_fetcher import NewsFetcher

# 台灣時區 (UTC+8)
TAIWAN_TZ = timezone(timedelta(hours=8))

class WebhookTelegramHandler:
    """Webhook模式Telegram處理器"""
    
    def __init__(self, bot_token: str, chat_id: str, cloud_monitor):
        self.bot_token = bot_token
        self.chat_id = int(chat_id)
        self.cloud_monitor = cloud_monitor
        self.max_api = MaxAPI()
        self.macd_analyzer = EnhancedMACDAnalyzer()
        self.news_fetcher = NewsFetcher()
        self.logger = logging.getLogger('WebhookTelegram')
        
        # 創建Application
        self.application = Application.builder().token(bot_token).build()
        
        # 添加消息處理器
        self.application.add_handler(
            MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message)
        )
        
        # Webhook設置
        self.webhook_path = f"/webhook/{bot_token}"
        self.webhook_url = None
        self.app = None
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """處理接收到的訊息"""
        self.logger.info(f"🔔 Webhook收到Telegram更新: {type(update).__name__}")
        
        if not update.message:
            self.logger.debug("收到非訊息更新，忽略")
            return
            
        # 記錄訊息詳情
        incoming_chat_id = update.message.chat.id
        message_text = update.message.text.strip() if update.message.text else "非文字訊息"
        
        self.logger.info(f"📨 Webhook收到訊息:")
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
                try:
                    await update.message.reply_text("❌ 抱歉，處理您的詢問時出現錯誤，請稍後再試。")
                except:
                    pass
        else:
            self.logger.debug(f"非交易詢問訊息: '{text}'，忽略")
    
    def is_trading_query(self, text: str) -> bool:
        """判斷是否為交易詢問"""
        buy_keywords = ['买进', '买入', '買進', '買入', 'buy', 'BUY', '进场', '進場']
        sell_keywords = ['卖出', '卖掉', '賣出', '賣掉', 'sell', 'SELL', '出场', '出場']
        test_keywords = ['test', 'TEST', '測試', '测试']
        
        all_keywords = buy_keywords + sell_keywords + test_keywords
        
        for keyword in all_keywords:
            if keyword in text and '?' in text:
                return True
        return False
    
    async def analyze_trading_decision(self, query: str) -> str:
        """分析交易決策並返回AI建議"""
        try:
            self.logger.info("🤖 開始AI分析流程...")
            
            # 獲取當前市場數據
            self.logger.info("📊 正在獲取市場數據...")
            market_data = await self.cloud_monitor.check_market_conditions('btctwd')
            if not market_data:
                return "❌ 抱歉，目前無法獲取市場數據，請稍後再試。"
            
            # 獲取即時新聞
            self.logger.info("📰 正在獲取BTC相關新聞...")
            news_list = []
            try:
                news_list = self.news_fetcher.get_crypto_news(limit=3)
                self.logger.info(f"✅ 獲取到 {len(news_list)} 條新聞")
            except Exception as e:
                self.logger.warning(f"⚠️  新聞獲取失敗: {e}")
            
            # 提取技術指標
            technical = market_data['technical']
            price = market_data['price']
            
            # 判斷用戶詢問類型
            is_buy_query = any(keyword in query for keyword in ['买进', '买入', '買進', '買入', 'buy', 'BUY', '进场', '進場'])
            
            # AI分析邏輯
            self.logger.info("🔍 正在執行技術分析...")
            analysis = self.perform_ai_analysis(technical, price, is_buy_query)
            
            # 格式化回覆，包含新聞
            self.logger.info("📝 正在格式化分析回覆...")
            response = self.format_analysis_response(analysis, technical, price, is_buy_query, news_list)
            
            self.logger.info("✅ AI分析完成")
            return response
            
        except Exception as e:
            self.logger.error(f"分析交易決策時出錯: {e}")
            import traceback
            self.logger.error(f"詳細錯誤: {traceback.format_exc()}")
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
    
    def format_analysis_response(self, analysis: Dict, technical: Dict, price: Dict, is_buy_query: bool, news_list: List[Dict]) -> str:
        """格式化分析回覆"""
        query_type = "買進" if is_buy_query else "賣出"
        
        # 建議emoji和文字
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
🤖 <b>AI交易分析回覆</b> (Webhook模式)

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

⏰ <b>分析時間:</b> {datetime.now(TAIWAN_TZ).strftime('%Y-%m-%d %H:%M:%S')} (台灣時間)

<i>⚠️ 此為AI技術分析，僅供參考，請結合其他資訊並謹慎決策</i>
        """
        
        # 添加新聞
        if news_list:
            response += f"""
📰 <b>相關新聞資訊:</b>
"""
            for i, news in enumerate(news_list, 1):
                title = news['title']
                source = news.get('source', '未知來源')
                time_str = news.get('time', '剛剛')
                
                # 限制標題長度避免過長
                if len(title) > 45:
                    title = title[:42] + "..."
                
                response += f"   {i}. {title}\n"
                response += f"      <i>📍 來源: {source} • {time_str}</i>\n"
                
                # 如果有摘要，也加上
                if news.get('summary'):
                    summary = news['summary']
                    if len(summary) > 60:
                        summary = summary[:57] + "..."
                    response += f"      💬 {summary}\n"
                response += "\n"
        else:
            response += f"""
📰 <b>相關新聞資訊:</b> 暫時無法獲取最新新聞
"""
        
        return response.strip()
    
    async def webhook_handler(self, request):
        """處理Webhook請求"""
        try:
            # 驗證請求路徑
            if request.path != self.webhook_path:
                self.logger.warning(f"無效的webhook路徑: {request.path}")
                return web.Response(status=404)
            
            # 獲取請求數據
            data = await request.json()
            self.logger.info(f"🌐 收到Webhook請求: {len(str(data))} 字節")
            
            # 創建Update對象
            update = Update.de_json(data, self.application.bot)
            
            if update:
                # 處理更新
                await self.application.process_update(update)
                self.logger.info("✅ Webhook更新處理完成")
            else:
                self.logger.warning("⚠️ 無效的Update數據")
            
            return web.Response(text="OK")
            
        except Exception as e:
            self.logger.error(f"❌ Webhook處理失敗: {e}")
            import traceback
            self.logger.error(f"詳細錯誤: {traceback.format_exc()}")
            return web.Response(status=500)
    
    async def setup_webhook(self):
        """設置Webhook"""
        try:
            # 設置Webhook URL
            port = int(os.getenv('PORT', 8080))
            
            # Render.com 提供的公開 URL
            service_name = os.getenv('RENDER_SERVICE_NAME', 'btc-macd-monitor')
            self.webhook_url = f"https://{service_name}.onrender.com{self.webhook_path}"
            
            self.logger.info(f"🌐 設置Webhook URL: {self.webhook_url}")
            
            # 初始化Application
            await self.application.initialize()
            
            # 設置Webhook
            await self.application.bot.set_webhook(
                url=self.webhook_url,
                drop_pending_updates=True
            )
            
            self.logger.info("✅ Webhook設置成功")
            
            # 發送成功通知
            try:
                await self.application.bot.send_message(
                    chat_id=self.chat_id,
                    text="🎉 <b>交互式AI分析 (Webhook模式) 已啟動！</b>\n\n💬 發送 '買進?' 或 '賣出?' 即可獲得即時AI分析\n\n🌐 使用Webhook模式，更穩定可靠",
                    parse_mode='HTML'
                )
                self.logger.info("✅ Webhook啟動通知已發送")
            except Exception as e:
                self.logger.warning(f"發送啟動通知失敗: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Webhook設置失敗: {e}")
            import traceback
            self.logger.error(f"詳細錯誤: {traceback.format_exc()}")
            return False
    
    async def start_webhook_server(self):
        """啟動Webhook服務器"""
        try:
            # 創建web應用
            self.app = web.Application()
            self.app.router.add_post(self.webhook_path, self.webhook_handler)
            
            # 添加健康檢查端點
            self.app.router.add_get('/health', self.health_check)
            
            port = int(os.getenv('PORT', 8080))
            
            self.logger.info(f"🚀 啟動Webhook服務器於端口 {port}")
            
            # 啟動服務器
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', port)
            await site.start()
            
            self.logger.info("✅ Webhook服務器已啟動")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Webhook服務器啟動失敗: {e}")
            return False
    
    async def health_check(self, request):
        """健康檢查端點"""
        return web.json_response({
            'status': 'healthy',
            'webhook_mode': True,
            'timestamp': datetime.now(TAIWAN_TZ).isoformat()
        })
    
    async def stop_webhook(self):
        """停止Webhook"""
        try:
            if self.application:
                await self.application.bot.delete_webhook()
                await self.application.stop()
                await self.application.shutdown()
            self.logger.info("✅ Webhook已停止")
        except Exception as e:
            self.logger.error(f"❌ 停止Webhook失敗: {e}") 