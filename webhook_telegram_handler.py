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
from advanced_crypto_analyzer import AdvancedCryptoAnalyzer
from news_fetcher import NewsFetcher
from news_sentiment_analyzer import NewsSentimentAnalyzer

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
        self.advanced_analyzer = AdvancedCryptoAnalyzer()
        self.news_fetcher = NewsFetcher()
        self.sentiment_analyzer = NewsSentimentAnalyzer()
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
        
        # 支持各種問號符號：半角?、全角？、手機問號等
        question_marks = ['?', '？', '︖', '﹖']
        
        for keyword in all_keywords:
            if keyword in text:
                # 檢查是否包含任何類型的問號
                for qmark in question_marks:
                    if qmark in text:
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
            
            # 獲取新聞數據 - 增加獲取數量
            self.logger.info("📰 正在從15個全球新聞源獲取最新資訊...")
            news_list = []
            try:
                news_list = self.news_fetcher.get_crypto_news(limit=8)  # 增加到8條
                self.logger.info(f"✅ 獲取到 {len(news_list)} 條新聞")
                # 顯示新聞來源統計
                sources = [news.get('source', 'Unknown') for news in news_list]
                source_count = {}
                for source in sources:
                    source_count[source] = source_count.get(source, 0) + 1
                self.logger.info(f"📊 新聞來源分布: {source_count}")
            except Exception as e:
                self.logger.warning(f"⚠️  新聞獲取失敗: {e}")
            
            # 分析新聞情緒 - 使用增強分析器
            self.logger.info("🔍 正在使用AI增強情緒分析器分析新聞...")
            sentiment_analysis = self.sentiment_analyzer.analyze_news_sentiment(news_list)
            self.logger.info(f"📈 新聞情緒: {sentiment_analysis['overall_sentiment']}")
            self.logger.info(f"📊 詳細統計: 利多{sentiment_analysis.get('bullish_count', 0)}筆, 利空{sentiment_analysis.get('bearish_count', 0)}筆, 中性{sentiment_analysis.get('neutral_count', 0)}筆")
            
            # 提取技術指標
            technical = market_data['technical']
            price = market_data['price']
            
            # 判斷用戶詢問類型
            is_buy_query = any(keyword in query for keyword in ['买进', '买入', '買進', '購入', 'buy', 'BUY', '进场', '進場'])
            
            # AI技術分析
            self.logger.info("🔍 正在執行綜合多重技術指標分析...")
            tech_analysis = self.advanced_analyzer.comprehensive_analysis(
                market_data['df'], price['current']
            )
            
            # 綜合分析 - 結合技術面和新聞面
            self.logger.info("🎯 正在生成綜合交易建議...")
            trading_recommendation = self.sentiment_analyzer.get_trading_recommendation(
                sentiment_analysis, tech_analysis
            )
            
            # 格式化回覆，包含所有分析
            self.logger.info("📝 正在格式化分析回覆...")
            response = self.format_comprehensive_response(
                tech_analysis, sentiment_analysis, trading_recommendation, 
                technical, price, is_buy_query, news_list
            )
            
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
    
    def format_comprehensive_response(self, tech_analysis: Dict, sentiment_analysis: Dict, 
                                    trading_recommendation: Dict, technical: Dict, price: Dict, 
                                    is_buy_query: bool, news_list: List[Dict]) -> str:
        """格式化綜合分析回覆"""
        query_type = "買進" if is_buy_query else "賣出"
        
        # 技術分析建議
        recommendation = tech_analysis.get('recommendation', 'HOLD')
        if recommendation in ['STRONG_BUY', 'BUY']:
            tech_emoji = '🚀'
            tech_text = '建議買進' if recommendation == 'BUY' else '強烈建議買進'
            tech_color = '🟢'
        elif recommendation in ['STRONG_SELL', 'SELL']:
            tech_emoji = '📉'
            tech_text = '建議賣出' if recommendation == 'SELL' else '強烈建議賣出'
            tech_color = '🔴'
        else:
            tech_emoji = '⚖️'
            tech_text = '建議持有'
            tech_color = '🟡'
        
        # 新聞情緒
        news_sentiment = sentiment_analysis['overall_sentiment']
        if news_sentiment == 'bullish':
            news_emoji = '📈'
            news_text = '看漲'
            news_color = '🟢'
        elif news_sentiment == 'bearish':
            news_emoji = '📉'
            news_text = '看跌'
            news_color = '🔴'
        else:
            news_emoji = '➡️'
            news_text = '中性'
            news_color = '🟡'
        
        # 綜合建議
        action = trading_recommendation['action']
        risk_level = trading_recommendation['risk_level']
        probability = trading_recommendation['probability_analysis']
        
        # 風險等級emoji
        risk_emojis = {'低': '🟢', '中低': '🟡', '中等': '🟠', '較高': '🔴', '高': '🔴'}
        risk_emoji = risk_emojis.get(risk_level, '🟡')
        
        # 置信度條
        tech_confidence = tech_analysis.get('confidence', 50)
        news_confidence = sentiment_analysis['confidence']
        tech_confidence_bar = '█' * (int(tech_confidence) // 10) + '░' * (10 - int(tech_confidence) // 10)
        news_confidence_bar = '█' * (int(news_confidence) // 10) + '░' * (10 - int(news_confidence) // 10)
        
        # 獲取技術指標數值
        tech_values = tech_analysis.get('technical_values', {})
        
        response = f"""
🤖 <b>AI綜合交易分析</b> (多重技術指標版)

❓ <b>您的詢問:</b> {query_type}？

🎯 <b>綜合建議:</b> {action}
📊 <b>概率分析:</b> {probability}
⚠️ <b>風險等級:</b> {risk_emoji} {risk_level}

💰 <b>目前市場數據:</b>
• 價格: ${price['current']:,.0f} TWD
• 24H最高: ${price['high_24h']:,.0f} TWD
• 24H最低: ${price['low_24h']:,.0f} TWD

🔬 <b>多重技術指標分析:</b>
{tech_color} <b>技術建議:</b> {tech_emoji} {tech_text}
📊 <b>技術置信度:</b> {tech_confidence:.1f}% [{tech_confidence_bar}]

📊 <b>關鍵指標數值:</b>
• MA7: {tech_values.get('ma7', 0):,.1f} TWD
• MA25: {tech_values.get('ma25', 0):,.1f} TWD
• MA99: {tech_values.get('ma99', 0):,.1f} TWD
• MACD: {tech_values.get('macd', 0):.2f}
• RSI: {tech_values.get('rsi', 0):.1f}
• 布林帶位置: {tech_values.get('bb_position', 0):.2f}

📈 <b>多重指標權重分析:</b>
• 🟢 看漲分數: {tech_analysis.get('bullish_score', 0):.1f}
• 🔴 看跌分數: {tech_analysis.get('bearish_score', 0):.1f}
• ⚖️ 淨分數: {tech_analysis.get('net_score', 0):.1f}

📰 <b>新聞情緒分析:</b>
{news_color} <b>市場情緒:</b> {news_emoji} {news_text}
📊 <b>情緒置信度:</b> {int(news_confidence)}% [{news_confidence_bar}]
🎲 <b>漲跌概率:</b> 上漲{sentiment_analysis['bullish_probability']}% vs 下跌{sentiment_analysis['bearish_probability']}%

📊 <b>24小時新聞統計:</b>
• 📈 利多消息: {sentiment_analysis.get('bullish_count', 0)} 筆
• 📉 利空消息: {sentiment_analysis.get('bearish_count', 0)} 筆
• ➡️ 中性消息: {sentiment_analysis.get('neutral_count', 0)} 筆
• 🌐 來源多樣性: {sentiment_analysis.get('source_diversity', 0)}/15個權威新聞源

🔍 <b>技術指標詳細分析:</b>
"""
        
        # 添加各項技術指標的詳細分析
        detailed_analysis = tech_analysis.get('detailed_analysis', {})
        
        if 'ma_cross' in detailed_analysis:
            ma = detailed_analysis['ma_cross']
            response += f"• 📏 均線系統: {ma['signal']} ({ma['strength']:.0f}%)\n"
        
        if 'macd' in detailed_analysis:
            macd = detailed_analysis['macd']
            response += f"• 📊 MACD: {macd['signal']} ({macd['strength']:.0f}%)\n"
            
        if 'rsi' in detailed_analysis:
            rsi = detailed_analysis['rsi']
            response += f"• 📈 RSI: {rsi['signal']} ({rsi['strength']:.0f}%)\n"
            
        if 'bollinger' in detailed_analysis:
            bb = detailed_analysis['bollinger']
            response += f"• 📊 布林帶: {bb['signal']} ({bb['strength']:.0f}%)\n"
            
        if 'volume' in detailed_analysis:
            vol = detailed_analysis['volume']
            response += f"• 📊 成交量: {vol['signal']} ({vol['strength']:.0f}%)\n"

        response += f"""

💡 <b>操作建議:</b> {trading_recommendation['reason']}

📈 <b>機率預測:</b>
• 🚀 上漲機率: {sentiment_analysis['bullish_probability']}%
• 📉 下跌機率: {sentiment_analysis['bearish_probability']}%

⏰ <b>分析時間:</b> {datetime.now(TAIWAN_TZ).strftime('%Y-%m-%d %H:%M:%S')} (台灣時間)

<i>⚠️ 此為AI多重技術指標+新聞綜合分析，整合MA、MACD、RSI、布林帶、成交量等專業指標，僅供參考，請結合其他資訊並謹慎決策</i>
        """
        
        return response.strip()
    
    def _translate_outlook(self, outlook: str) -> str:
        """將英文市場展望翻譯成中文說明"""
        outlook_translations = {
            'BULLISH': '樂觀看漲 - 技術指標顯示上漲趨勢，建議關注買進機會',
            'BEARISH': '謹慎看跌 - 技術指標顯示下跌趨勢，建議謹慎操作或等待',
            'NEUTRAL': '中性觀望 - 技術指標方向不明，建議持有觀察市場變化',
            'WAIT': '等待時機 - 當前不是進出場的最佳時機，建議耐心等待',
            'STRONG_BULLISH': '強烈看漲 - 多項指標強烈看漲，可考慮適度加碼',
            'STRONG_BEARISH': '強烈看跌 - 多項指標強烈看跌，建議減倉或止損'
        }
        return outlook_translations.get(outlook, '中性觀望 - 技術指標方向不明，建議持有觀察市場變化')
    
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