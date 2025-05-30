import asyncio
import logging
from datetime import datetime, timedelta
from telegram import Bot
from telegram.error import TelegramError

class TelegramNotifier:
    def __init__(self, bot_token=None, chat_id=None):
        # 如果有提供參數就使用，否則從config讀取
        if bot_token and chat_id:
            self.bot_token = bot_token
            self.chat_id = chat_id
        else:
            try:
                from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
                self.bot_token = TELEGRAM_BOT_TOKEN
                self.chat_id = TELEGRAM_CHAT_ID
            except ImportError:
                self.bot_token = None
                self.chat_id = None
        
        self.bot = None
        self.logger = logging.getLogger(__name__)
        self.last_signal_time = {}
        
        try:
            from config import MIN_SIGNAL_INTERVAL
            self.min_interval = MIN_SIGNAL_INTERVAL
        except ImportError:
            self.min_interval = 300  # 預設5分鐘
        
        # 初始化Bot
        if self.bot_token and self.bot_token != '請設定您的Telegram Bot Token':
            try:
                self.bot = Bot(token=self.bot_token)
            except Exception as e:
                self.logger.error(f"初始化Telegram Bot失敗: {e}")
    
    def can_send_signal(self, signal_type):
        """檢查是否可以發送信號（避免過於頻繁）"""
        now = datetime.now()
        if signal_type in self.last_signal_time:
            time_diff = (now - self.last_signal_time[signal_type]).total_seconds()
            if time_diff < self.min_interval:
                return False
        return True
    
    async def send_signal_notification(self, signal_data, price_data):
        """發送交易信號通知"""
        if not self.bot or not self.chat_id or self.chat_id == '請設定您的Telegram Chat ID':
            self.logger.warning("Telegram Bot未正確設定")
            return False
        
        try:
            signal_type = signal_data['signal']
            
            # 檢查是否可以發送
            if not self.can_send_signal(signal_type):
                return False
            
            # 準備訊息
            message = self._format_signal_message(signal_data, price_data)
            
            # 發送訊息
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            # 記錄發送時間
            self.last_signal_time[signal_type] = datetime.now()
            self.logger.info(f"已發送{signal_type}信號通知")
            return True
            
        except TelegramError as e:
            self.logger.error(f"發送Telegram訊息失敗: {e}")
            return False
        except Exception as e:
            self.logger.error(f"發送通知時出現錯誤: {e}")
            return False
    
    def _format_signal_message(self, signal_data, price_data):
        """格式化信號訊息"""
        signal = signal_data['signal']
        strength = signal_data['strength']
        reason = signal_data['reason']
        current_price = price_data['price']
        
        # 設定emoji
        if signal == 'BUY':
            emoji = '🚀'
            action = '買入'
        elif signal == 'SELL':
            emoji = '📉'
            action = '賣出'
        else:
            emoji = '⏸️'
            action = '持有'
        
        # 強度條
        strength_bar = '█' * (strength // 10) + '░' * (10 - strength // 10)
        
        message = f"""
<b>{emoji} BTC/TWD 交易信號 {emoji}</b>

🎯 <b>信號類型:</b> {action}
💪 <b>信號強度:</b> {strength}% [{strength_bar}]
📝 <b>分析原因:</b> {reason}

💰 <b>當前價格:</b> ${current_price:,.0f} TWD
📊 <b>技術指標:</b>
   • MACD: {signal_data['macd_current']:.4f}
   • Signal: {signal_data['macd_signal_current']:.4f}
   • Histogram: {signal_data['histogram_current']:.4f}
   • RSI: {signal_data['rsi_current']:.1f}

⏰ <b>時間:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<i>⚠️ 此為技術分析建議，請謹慎評估風險後再做投資決策</i>
        """
        
        return message.strip()
    
    async def send_status_update(self, price_data, macd_summary):
        """發送狀態更新（非信號）"""
        if not self.bot or not self.chat_id:
            return False
            
        try:
            message = f"""
<b>📊 BTC/TWD 市場狀態</b>

💰 <b>當前價格:</b> ${price_data['price']:,.0f} TWD
📈 <b>24H最高:</b> ${price_data['high']:,.0f} TWD  
📉 <b>24H最低:</b> ${price_data['low']:,.0f} TWD
💹 <b>24H成交量:</b> {price_data['volume']:.2f} BTC

📊 <b>技術指標:</b>
   • MACD: {macd_summary['macd']:.4f}
   • Signal: {macd_summary['signal']:.4f}
   • Histogram: {macd_summary['histogram']:.4f}
   • RSI: {macd_summary['rsi']:.1f}
   • EMA12: ${macd_summary['ema_12']:,.0f}
   • EMA26: ${macd_summary['ema_26']:,.0f}

⏰ <b>更新時間:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message.strip(),
                parse_mode='HTML'
            )
            return True
            
        except Exception as e:
            self.logger.error(f"發送狀態更新失敗: {e}")
            return False
    
    async def test_connection(self):
        """測試Telegram連接"""
        if not self.bot:
            return False, "Bot未初始化"
            
        try:
            bot_info = await self.bot.get_me()
            test_message = f"🤖 連接測試成功！\nBot名稱: {bot_info.username}\n時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=test_message
            )
            return True, f"連接成功，Bot: {bot_info.username}"
            
        except Exception as e:
            return False, f"連接失敗: {str(e)}"
    
    def send_signal_sync(self, signal_data, price_data):
        """同步版本的發送信號（用於GUI調用）"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.send_signal_notification(signal_data, price_data)
            )
            loop.close()
            return result
        except Exception as e:
            self.logger.error(f"同步發送失敗: {e}")
            return False
    
    def send_message(self, message):
        """發送簡單訊息（用於測試）"""
        if not self.bot or not self.chat_id:
            self.logger.warning("Telegram Bot未正確設定")
            return False
            
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def send_async():
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message
                )
            
            loop.run_until_complete(send_async())
            loop.close()
            return True
            
        except Exception as e:
            self.logger.error(f"發送訊息失敗: {e}")
            return False 