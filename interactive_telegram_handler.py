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
        """啟動訊息輪詢 - 雲端優化版本"""
        self.logger.info("啟動Telegram訊息處理器...")
        
        # 創建Bot實例
        bot = Bot(token=self.bot_token)
        
        # 超強力清理 - 雲端環境特殊處理
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                self.logger.info(f"🔧 第 {attempt + 1} 次清理嘗試...")
                
                # 檢查當前狀態
                webhook_info = await bot.get_webhook_info()
                self.logger.info(f"   當前Webhook: {webhook_info.url or '未設置'}")
                self.logger.info(f"   待處理更新: {webhook_info.pending_update_count}")
                
                # 強制刪除任何webhook
                if webhook_info.url:
                    self.logger.info("   🧹 刪除現有webhook...")
                    await bot.delete_webhook(drop_pending_updates=True)
                    await asyncio.sleep(2)
                
                # 超級清理：設置假webhook再刪除
                self.logger.info("   🧹 執行深度清理...")
                fake_url = "https://example.com/fake"
                await bot.set_webhook(url=fake_url, drop_pending_updates=True)
                await asyncio.sleep(1)
                await bot.delete_webhook(drop_pending_updates=True)
                await asyncio.sleep(2)
                
                # 測試連接
                self.logger.info("   🧪 測試Bot連接...")
                try:
                    # 使用短超時測試
                    updates = await bot.get_updates(limit=1, timeout=3)
                    self.logger.info(f"   ✅ 連接測試成功，獲得 {len(updates)} 個更新")
                    break  # 成功，跳出清理循環
                except Exception as test_e:
                    if "Conflict" in str(test_e):
                        self.logger.warning(f"   ⚠️  第 {attempt + 1} 次測試仍有衝突: {test_e}")
                        if attempt < max_attempts - 1:
                            wait_time = (attempt + 1) * 5
                            self.logger.info(f"   ⏰ 等待 {wait_time} 秒後重試...")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            self.logger.error("   ❌ 所有清理嘗試都失敗了")
                            raise test_e
                    else:
                        self.logger.error(f"   ❌ 其他錯誤: {test_e}")
                        break
                        
            except Exception as e:
                self.logger.error(f"   ❌ 清理過程失敗: {e}")
                if attempt == max_attempts - 1:
                    raise e
        
        # 現在嘗試啟動Application
        self.logger.info("🚀 開始啟動Application...")
        
        try:
            await self.application.initialize()
            await self.application.start()
            
            # 使用更保守的輪詢設置
            self.logger.info("🔄 啟動輪詢（雲端優化設置）...")
            await self.application.updater.start_polling(
                drop_pending_updates=True,
                timeout=30,           # 較長的超時
                read_timeout=30,
                write_timeout=30,
                connect_timeout=20,
                pool_timeout=20,
                error_callback=self._enhanced_error_callback,
                allowed_updates=None,  # 接收所有類型的更新
                bootstrap_retries=-1   # 無限重試
            )
            
            self.logger.info("✅ Telegram長輪詢已啟動")
            
            # 發送成功通知
            try:
                await bot.send_message(
                    chat_id=self.chat_id,
                    text="🎉 <b>交互式AI分析功能現已完全啟動！</b>\n\n💬 發送 '買進?' 或 '賣出?' 即可獲得即時AI分析",
                    parse_mode='HTML'
                )
                self.logger.info("✅ 啟動成功通知已發送")
            except Exception as msg_e:
                self.logger.warning(f"發送成功通知失敗: {msg_e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Application啟動失敗: {e}")
            
            # 如果是衝突錯誤，發送特殊通知
            if "Conflict" in str(e):
                try:
                    await bot.send_message(
                        chat_id=self.chat_id,
                        text="⚠️ <b>交互式功能啟動遇到衝突</b>\n\n🔧 系統正在自動修復，請稍等1-2分鐘後重新部署",
                        parse_mode='HTML'
                    )
                except:
                    pass
            
            raise e
    
    def _enhanced_error_callback(self, update, context):
        """增強的錯誤回調函數"""
        error = context.error
        self.logger.error(f"Telegram更新處理錯誤: {error}")
        
        if "Conflict" in str(error):
            self.logger.error("🚨 檢測到嚴重衝突 - 可能需要重新部署")
            # 嘗試發送緊急通知
            asyncio.create_task(self._send_emergency_notification())
        elif "Timeout" in str(error):
            self.logger.warning("⏰ 超時錯誤 - 這在雲端環境是正常的")
        else:
            self.logger.error(f"未知錯誤: {error}")
    
    async def _send_emergency_notification(self):
        """發送緊急通知"""
        try:
            emergency_bot = Bot(token=self.bot_token)
            await emergency_bot.send_message(
                chat_id=self.chat_id,
                text="🚨 <b>檢測到Bot衝突</b>\n\n請重新部署系統以完全解決衝突問題",
                parse_mode='HTML'
            )
        except:
            pass
    
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