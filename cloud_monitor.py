#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
雲端MACD監控系統
支持多種雲端平台部署和通知方式
"""

import asyncio
import json
import logging
import time
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
import schedule
import pandas as pd
import aiohttp  # 添加http客戶端

from max_api import MaxAPI
from enhanced_macd_analyzer import EnhancedMACDAnalyzer
from telegram_notifier import TelegramNotifier

# 添加交互式处理器导入
try:
    from webhook_telegram_handler import WebhookTelegramHandler
    WEBHOOK_AVAILABLE = True
except ImportError:
    WEBHOOK_AVAILABLE = False
    WebhookTelegramHandler = None

# 保留原有的長輪詢處理器作為備用
try:
    from interactive_telegram_handler import InteractiveTelegramHandler
    INTERACTIVE_AVAILABLE = True
except ImportError:
    INTERACTIVE_AVAILABLE = False
    InteractiveTelegramHandler = None

# 台灣時區 (UTC+8)
TAIWAN_TZ = timezone(timedelta(hours=8))

class CloudMonitor:
    """雲端監控系統主類"""
    
    def __init__(self, config_file: str = 'monitor_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        
        # 使用環境變量覆蓋配置
        self.apply_env_overrides()
        
        # 初始化組件
        self.max_api = MaxAPI()
        self.macd_analyzer = EnhancedMACDAnalyzer()
        self.telegram_notifier = TelegramNotifier()
        
        # 設置日誌
        self.setup_logging()
        
        # 監控狀態
        self.is_running = False
        self.last_alerts = {}
        self.monitoring_data = {}
        
        # 統計數據
        self.stats = {
            'alerts_sent': 0,
            'checks_performed': 0,
            'errors_count': 0,
            'start_time': None
        }
        
        # 保活功能設置
        self.keep_alive_enabled = os.getenv('KEEP_ALIVE_ENABLED', 'true').lower() == 'true'
        self.keep_alive_interval = int(os.getenv('KEEP_ALIVE_INTERVAL', '300'))  # 5分鐘，確保服務始終活躍
        self.health_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost:8080')}/health"
        self.last_keep_alive = None
        
        # 初始化交互式Telegram处理器 - 添加詳細日誌
        self.interactive_handler = None
        self.webhook_handler = None
        self.logger.info("=" * 60)
        self.logger.info("🔧 開始初始化Webhook式Telegram處理器...")
        self.logger.info("=" * 60)
        
        # 檢查是否啟用Webhook功能
        if not WEBHOOK_AVAILABLE:
            self.logger.error("❌ Webhook模組不可用 - 未找到 webhook_telegram_handler")
            self.logger.error(f"   WEBHOOK_AVAILABLE = {WEBHOOK_AVAILABLE}")
            self.logger.error(f"   WebhookTelegramHandler = {WebhookTelegramHandler}")
            # 嘗試使用長輪詢作為備用
            if INTERACTIVE_AVAILABLE:
                self.logger.info("🔄 嘗試使用長輪詢模式作為備用...")
                self._init_polling_handler()
            return
            
        self.logger.info(f"✅ Webhook模組可用: WEBHOOK_AVAILABLE = {WEBHOOK_AVAILABLE}")
            
        if not self.config['notifications']['telegram_enabled']:
            self.logger.warning("⚠️  Telegram通知未啟用，跳過Webhook功能")
            self.logger.warning(f"   telegram_enabled = {self.config['notifications']['telegram_enabled']}")
            return
            
        self.logger.info(f"✅ Telegram通知已啟用: {self.config['notifications']['telegram_enabled']}")
        
        # 檢查環境變數
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        self.logger.info(f"📱 環境變數檢查:")
        self.logger.info(f"   Bot Token檢查: {'✅ 已設置' if bot_token else '❌ 未設置'}")
        if bot_token:
            self.logger.info(f"   Bot Token (前10字元): {bot_token[:10]}...")
        self.logger.info(f"   Chat ID檢查: {'✅ 已設置' if chat_id else '❌ 未設置'}")
        if chat_id:
            self.logger.info(f"   Chat ID: {chat_id}")
        
        if not bot_token:
            self.logger.error("❌ TELEGRAM_BOT_TOKEN 環境變數未設置，無法啟動Webhook功能")
            self.logger.error("   請在Render.com控制台確認環境變數設置")
            return
            
        if not chat_id:
            self.logger.error("❌ TELEGRAM_CHAT_ID 環境變數未設置，無法啟動Webhook功能")
            self.logger.error("   請在Render.com控制台確認環境變數設置")
            return
        
        try:
            self.logger.info("🚀 正在創建Webhook處理器實例...")
            self.logger.info(f"   使用Bot Token: {bot_token[:10]}...")
            self.logger.info(f"   使用Chat ID: {chat_id}")
            self.logger.info(f"   傳入CloudMonitor實例: {type(self).__name__}")
            
            self.webhook_handler = WebhookTelegramHandler(bot_token, chat_id, self)
            self.logger.info("✅ Webhook處理器實例創建成功")
            self.logger.info(f"   處理器類型: {type(self.webhook_handler).__name__}")
            self.logger.info(f"   處理器Chat ID: {self.webhook_handler.chat_id}")
            
        except Exception as e:
            self.logger.error("=" * 60)
            self.logger.error("❌ Webhook處理器初始化失敗")
            self.logger.error("=" * 60)
            self.logger.error(f"錯誤類型: {type(e).__name__}")
            self.logger.error(f"錯誤訊息: {e}")
            import traceback
            self.logger.error(f"詳細錯誤追蹤:")
            for line in traceback.format_exc().split('\n'):
                if line.strip():
                    self.logger.error(f"   {line}")
            self.logger.error("=" * 60)
            self.webhook_handler = None
        
        self.logger.info("=" * 60)
        self.logger.info(f"🏁 Webhook處理器初始化完成")
        self.logger.info(f"   最終狀態: {'✅ 成功' if self.webhook_handler else '❌ 失敗'}")
        self.logger.info("=" * 60)
    
    def _init_polling_handler(self):
        """初始化長輪詢處理器作為備用"""
        try:
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            chat_id = os.getenv('TELEGRAM_CHAT_ID')
            
            if bot_token and chat_id:
                self.interactive_handler = InteractiveTelegramHandler(bot_token, chat_id, self)
                self.logger.info("✅ 長輪詢處理器初始化成功（備用模式）")
            else:
                self.logger.error("❌ 長輪詢處理器初始化失敗：環境變數不足")
        except Exception as e:
            self.logger.error(f"❌ 長輪詢處理器初始化失敗: {e}")
        
    def apply_env_overrides(self):
        """使用環境變量覆蓋配置"""
        # Telegram設置
        if os.getenv('TELEGRAM_BOT_TOKEN'):
            # 確保telegram_notifier有正確的token
            os.environ.setdefault('TELEGRAM_BOT_TOKEN', os.getenv('TELEGRAM_BOT_TOKEN'))
        
        if os.getenv('TELEGRAM_CHAT_ID'):
            os.environ.setdefault('TELEGRAM_CHAT_ID', os.getenv('TELEGRAM_CHAT_ID'))
        
        # 監控設置
        if os.getenv('MONITOR_INTERVAL'):
            self.config['monitoring']['check_interval'] = int(os.getenv('MONITOR_INTERVAL'))
        
        if os.getenv('PRIMARY_PERIOD'):
            self.config['monitoring']['primary_period'] = int(os.getenv('PRIMARY_PERIOD'))
        
        if os.getenv('CHECK_SYMBOLS'):
            symbols = os.getenv('CHECK_SYMBOLS').split(',')
            self.config['monitoring']['symbols'] = [s.strip() for s in symbols]
        
        # 通知設置
        if os.getenv('COOLDOWN_PERIOD'):
            self.config['advanced']['cooldown_period'] = int(os.getenv('COOLDOWN_PERIOD'))
        
        if os.getenv('MAX_ALERTS_PER_HOUR'):
            self.config['advanced']['max_alerts_per_hour'] = int(os.getenv('MAX_ALERTS_PER_HOUR'))
        
        # 服務設置
        if os.getenv('PORT'):
            self.config['cloud']['health_check_port'] = int(os.getenv('PORT'))
        
        if os.getenv('LOG_LEVEL'):
            self.config['logging'] = {'level': os.getenv('LOG_LEVEL').upper()}
        
        if os.getenv('TIMEZONE'):
            self.config['cloud']['timezone'] = os.getenv('TIMEZONE')
    
    def load_config(self) -> Dict[str, Any]:
        """載入配置文件"""
        default_config = {
            "monitoring": {
                "symbols": ["btctwd"],
                "periods": [1, 5, 15, 30, 60],
                "check_interval": 60,
                "primary_period": 60
            },
            "alerts": {
                "macd_crossover": True,
                "signal_strength_threshold": 70,
                "price_change_threshold": 2.0,
                "volume_spike_threshold": 1.5,
                "rsi_overbought": 80,
                "rsi_oversold": 20
            },
            "notifications": {
                "telegram_enabled": True,
                "email_enabled": False,
                "slack_enabled": False,
                "discord_enabled": False
            },
            "cloud": {
                "platform": "local",  # local, heroku, aws, gcp, azure
                "health_check_port": 8080,
                "timezone": "Asia/Taipei"
            },
            "advanced": {
                "cooldown_period": 300,
                "max_alerts_per_hour": 10,
                "enable_backtesting": False,
                "data_retention_days": 30
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # 合併配置
                default_config.update(loaded_config)
            else:
                # 創建默認配置文件
                self.save_config(default_config)
                
        except Exception as e:
            print(f"⚠️  配置文件載入錯誤，使用默認配置: {e}")
            
        return default_config
    
    def save_config(self, config: Dict[str, Any] = None):
        """保存配置文件"""
        if config is None:
            config = self.config
            
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存配置文件失敗: {e}")
    
    def setup_logging(self):
        """設置日誌"""
        # 創建logs目錄
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # 設置日誌格式（移除emoji避免編碼問題）
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler('logs/cloud_monitor.log', encoding='utf-8'),
                logging.StreamHandler()  # 移除編碼設置，讓系統自動處理
            ]
        )
        
        self.logger = logging.getLogger('CloudMonitor')
        self.logger.info("雲端監控系統日誌已啟動")
        
    async def check_market_conditions(self, symbol: str) -> Optional[Dict[str, Any]]:
        """檢查市場條件"""
        try:
            self.logger.info(f"開始檢查 {symbol} 市場條件")
            
            # 獲取價格數據
            self.logger.info("正在獲取價格數據...")
            ticker = self.max_api.get_ticker(symbol)
            if not ticker:
                self.logger.error(f"無法獲取 {symbol} 價格數據")
                return None
            
            self.logger.info(f"價格數據獲取成功: {ticker.get('price', 'N/A')}")
            
            # 獲取主要週期的K線數據
            primary_period = self.config['monitoring']['primary_period']
            self.logger.info(f"正在獲取 {primary_period} 分鐘K線數據...")
            kline_data = self.max_api.get_klines(symbol, period=primary_period, limit=200)
            
            if kline_data is None or kline_data.empty:
                self.logger.error(f"無法獲取 {symbol} K線數據")
                return None
            
            self.logger.info(f"K線數據獲取成功，共 {len(kline_data)} 條記錄")
            
            # 計算技術指標
            self.logger.info("正在計算技術指標...")
            df_with_macd = self.macd_analyzer.calculate_macd(kline_data)
            if df_with_macd is None or df_with_macd.empty:
                self.logger.error(f"MACD計算失敗")
                return None
            
            if len(df_with_macd) < 2:
                self.logger.error(f"技術指標數據不足，只有 {len(df_with_macd)} 條記錄")
                return None
            
            self.logger.info("技術指標計算成功")
            
            latest = df_with_macd.iloc[-1]
            previous = df_with_macd.iloc[-2]
            
            # 安全獲取技術指標數據，使用默認值處理缺失項
            def safe_get(series, key, default=0.0):
                try:
                    value = series.get(key, default)
                    return float(value) if pd.notna(value) else default
                except:
                    return default
            
            # 構建市場條件數據
            market_data = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'price': {
                    'current': float(ticker['price']),
                    'high_24h': float(ticker['high']),
                    'low_24h': float(ticker['low']),
                    'volume_24h': float(ticker['volume'])
                },
                'technical': {
                    'macd': safe_get(latest, 'macd'),
                    'macd_signal': safe_get(latest, 'macd_signal'),
                    'macd_histogram': safe_get(latest, 'macd_histogram'),
                    'rsi': safe_get(latest, 'rsi', 50.0),  # RSI 默認值 50
                    'ema_12': safe_get(latest, 'ema_12'),
                    'ema_26': safe_get(latest, 'ema_26')
                },
                'previous': {
                    'macd': safe_get(previous, 'macd'),
                    'macd_signal': safe_get(previous, 'macd_signal'),
                    'macd_histogram': safe_get(previous, 'macd_histogram')
                },
                'df': df_with_macd  # 添加完整的K線數據供高級分析使用
            }
            
            self.logger.info(f"市場條件檢查完成: MACD={market_data['technical']['macd']:.2f}, RSI={market_data['technical']['rsi']:.1f}")
            return market_data
            
        except Exception as e:
            self.logger.error(f"檢查市場條件時出錯: {e}")
            import traceback
            self.logger.error(f"詳細錯誤: {traceback.format_exc()}")
            self.stats['errors_count'] += 1
            return None
    
    def analyze_alerts(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析並生成警報"""
        alerts = []
        
        try:
            current = market_data['technical']
            previous = market_data['previous']
            price = market_data['price']
            config = self.config['alerts']
            
            # MACD金叉死叉
            if config['macd_crossover']:
                macd_current = current['macd']
                signal_current = current['macd_signal']
                macd_prev = previous['macd']
                signal_prev = previous['macd_signal']
                
                # 金叉
                if macd_prev <= signal_prev and macd_current > signal_current:
                    alerts.append({
                        'type': 'MACD_GOLDEN_CROSS',
                        'priority': 'HIGH',
                        'message': f'MACD金叉信號！MACD({macd_current:.4f}) > Signal({signal_current:.4f})',
                        'action': 'BUY',
                        'strength': 85
                    })
                
                # 死叉
                elif macd_prev >= signal_prev and macd_current < signal_current:
                    alerts.append({
                        'type': 'MACD_DEATH_CROSS',
                        'priority': 'HIGH',
                        'message': f'MACD死叉信號！MACD({macd_current:.4f}) < Signal({signal_current:.4f})',
                        'action': 'SELL',
                        'strength': 85
                    })
            
            # RSI超買超賣
            rsi = current['rsi']
            if rsi >= config['rsi_overbought']:
                alerts.append({
                    'type': 'RSI_OVERBOUGHT',
                    'priority': 'MEDIUM',
                    'message': f'RSI超買警告！當前RSI: {rsi:.1f}',
                    'action': 'SELL',
                    'strength': 60
                })
            elif rsi <= config['rsi_oversold']:
                alerts.append({
                    'type': 'RSI_OVERSOLD',
                    'priority': 'MEDIUM',
                    'message': f'RSI超賣警告！當前RSI: {rsi:.1f}',
                    'action': 'BUY',
                    'strength': 60
                })
            
            # 價格變化警報
            # 這裡需要歷史價格數據來計算變化百分比
            # 暫時跳過，可以在後續版本中加入
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"分析警報時出錯: {e}")
            return []
    
    def should_send_alert(self, alert: Dict[str, Any]) -> bool:
        """檢查是否應該發送警報"""
        alert_type = alert['type']
        now = datetime.now()
        
        # 檢查冷卻期
        cooldown = self.config['advanced']['cooldown_period']
        if alert_type in self.last_alerts:
            time_diff = (now - self.last_alerts[alert_type]).total_seconds()
            if time_diff < cooldown:
                return False
        
        # 檢查每小時警報限制
        max_per_hour = self.config['advanced']['max_alerts_per_hour']
        hour_ago = now - timedelta(hours=1)
        recent_alerts = sum(1 for time in self.last_alerts.values() if time > hour_ago)
        
        if recent_alerts >= max_per_hour:
            return False
        
        return True
    
    async def send_notifications(self, alerts: List[Dict[str, Any]], market_data: Dict[str, Any]):
        """發送通知"""
        notifications = self.config['notifications']
        
        for alert in alerts:
            if not self.should_send_alert(alert):
                continue
            
            try:
                # Telegram通知
                if notifications['telegram_enabled']:
                    signal_data = {
                        'signal': alert['action'],
                        'strength': alert['strength'],
                        'reason': alert['message'],
                        'macd_current': market_data['technical']['macd'],
                        'macd_signal_current': market_data['technical']['macd_signal'],
                        'histogram_current': market_data['technical']['macd_histogram'],
                        'rsi_current': market_data['technical']['rsi']
                    }
                    
                    price_data = {
                        'price': market_data['price']['current'],
                        'high': market_data['price']['high_24h'],
                        'low': market_data['price']['low_24h'],
                        'volume': market_data['price']['volume_24h']
                    }
                    
                    success = await self.telegram_notifier.send_signal_notification(signal_data, price_data)
                    if success:
                        self.last_alerts[alert['type']] = datetime.now()
                        self.stats['alerts_sent'] += 1
                        self.logger.info(f"已發送Telegram警報: {alert['type']}")
                
                # 其他通知方式可以在這裡添加
                # Email, Slack, Discord等
                
            except Exception as e:
                self.logger.error(f"發送通知失敗: {e}")
    
    async def monitoring_cycle(self):
        """監控循環"""
        self.logger.info("開始監控循環")
        
        for symbol in self.config['monitoring']['symbols']:
            try:
                # 檢查市場條件
                market_data = await self.check_market_conditions(symbol)
                if not market_data:
                    continue
                
                # 分析警報
                alerts = self.analyze_alerts(market_data)
                
                # 發送通知
                if alerts:
                    await self.send_notifications(alerts, market_data)
                
                # 更新統計
                self.stats['checks_performed'] += 1
                self.monitoring_data[symbol] = market_data
                
                self.logger.info(f"{symbol} 監控完成 - 發現 {len(alerts)} 個警報")
                
            except Exception as e:
                self.logger.error(f"監控 {symbol} 時出錯: {e}")
                self.stats['errors_count'] += 1
    
    async def run_forever(self):
        """持續運行監控"""
        self.is_running = True
        self.stats['start_time'] = datetime.now(TAIWAN_TZ)
        
        self.logger.info("雲端監控系統啟動")
        
        # 啟動Webhook式Telegram處理器
        self.logger.info("=" * 60)
        self.logger.info("🚀 準備啟動Webhook式Telegram處理器...")
        self.logger.info("=" * 60)
        
        if self.webhook_handler:
            self.logger.info("✅ Webhook處理器實例存在，開始啟動...")
            self.logger.info(f"   處理器類型: {type(self.webhook_handler).__name__}")
            self.logger.info(f"   處理器Chat ID: {self.webhook_handler.chat_id}")
            try:
                self.logger.info("🔄 正在設置Webhook...")
                await self.webhook_handler.setup_webhook()
                
                self.logger.info("🔄 正在啟動Webhook服務器...")
                await self.webhook_handler.start_webhook_server()
                
                self.logger.info("✅ Webhook式Telegram訊息處理已啟動")
            except Exception as e:
                self.logger.error("=" * 50)
                self.logger.error("❌ 啟動Webhook處理器失敗")
                self.logger.error("=" * 50)
                self.logger.error(f"錯誤類型: {type(e).__name__}")
                self.logger.error(f"錯誤訊息: {e}")
                import traceback
                self.logger.error("詳細錯誤追蹤:")
                for line in traceback.format_exc().split('\n'):
                    if line.strip():
                        self.logger.error(f"   {line}")
                self.logger.error("=" * 50)
        elif self.interactive_handler:
            self.logger.info("🔄 使用長輪詢處理器作為備用...")
            try:
                await self.interactive_handler.start_polling()
                self.logger.info("✅ 長輪詢處理器已啟動（備用模式）")
            except Exception as e:
                self.logger.error(f"❌ 長輪詢處理器啟動失敗: {e}")
        else:
            self.logger.error("❌ 沒有可用的Telegram處理器")
            self.logger.error("⚠️  所有Telegram處理器都未初始化 - 檢查環境變數和配置")
            # 再次檢查原因
            self.logger.error("🔍 診斷原因:")
            if not WEBHOOK_AVAILABLE and not INTERACTIVE_AVAILABLE:
                self.logger.error("   原因: 所有處理器模組都不可用")
            elif not self.config['notifications']['telegram_enabled']:
                self.logger.error("   原因: Telegram通知未啟用")
            elif not os.getenv('TELEGRAM_BOT_TOKEN'):
                self.logger.error("   原因: TELEGRAM_BOT_TOKEN 環境變數未設置")
            elif not os.getenv('TELEGRAM_CHAT_ID'):
                self.logger.error("   原因: TELEGRAM_CHAT_ID 環境變數未設置")
            else:
                self.logger.error("   原因: 未知初始化錯誤")
        
        self.logger.info("=" * 60)
        self.logger.info(f"🏁 Telegram處理器啟動流程完成")
        self.logger.info(f"   Webhook狀態: {'✅ 運行中' if self.webhook_handler else '❌ 未運行'}")
        self.logger.info(f"   長輪詢狀態: {'✅ 運行中' if self.interactive_handler else '❌ 未運行'}")
        self.logger.info("=" * 60)
        
        # 發送啟動通知
        if self.config['notifications']['telegram_enabled']:
            # 檢查AI分析功能狀態 - 支持Webhook和長輪詢兩種模式
            ai_enabled = bool(self.webhook_handler or self.interactive_handler)
            ai_mode = ""
            if self.webhook_handler:
                ai_mode = " (Webhook模式)"
            elif self.interactive_handler:
                ai_mode = " (長輪詢模式)"
            
            start_message = f"""
🤖 <b>雲端監控系統啟動</b>

📊 <b>監控設定:</b>
• 交易對: {', '.join(self.config['monitoring']['symbols'])}
• 週期: {self.config['monitoring']['primary_period']}分鐘
• 檢查間隔: {self.config['monitoring']['check_interval']}秒

💬 <b>交互式功能:</b>
• AI分析: {'✅ 已啟用' if ai_enabled else '❌ 未啟用'}{ai_mode}

💓 <b>保活功能:</b>
• 自動保活: {'✅ 已啟用' if self.keep_alive_enabled else '❌ 已禁用'}
{f'• Ping間隔: {self.keep_alive_interval//60}分鐘 ({self.keep_alive_interval}秒)' if self.keep_alive_enabled else ''}

⏰ <b>啟動時間:</b> {datetime.now(TAIWAN_TZ).strftime('%Y-%m-%d %H:%M:%S')} (台灣時間)

🔔 系統將開始監控市場並發送警報通知

💡 <b>使用方法:</b>
發送 "買進?" 或 "賣出?" 可獲得AI分析建議
            """
            
            try:
                await self.telegram_notifier.bot.send_message(
                    chat_id=self.telegram_notifier.chat_id,
                    text=start_message.strip(),
                    parse_mode='HTML'
                )
                self.logger.info("✅ 啟動通知已發送")
            except Exception as e:
                self.logger.error(f"❌ 發送啟動通知失敗: {e}")
        
        # 主監控循環
        interval = self.config['monitoring']['check_interval']
        
        # 創建保活任務
        keep_alive_task = None
        if self.keep_alive_enabled:
            keep_alive_task = asyncio.create_task(self.keep_alive_task())
            self.logger.info("💓 保活任務已啟動")
        
        try:
            while self.is_running:
                start_time = time.time()
                
                await self.monitoring_cycle()
                
                # 計算等待時間
                elapsed = time.time() - start_time
                wait_time = max(0, interval - elapsed)
                
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                
        except KeyboardInterrupt:
            self.logger.info("收到停止信號")
        except Exception as e:
            self.logger.error(f"監控循環出錯: {e}")
        finally:
            # 取消保活任務
            if keep_alive_task:
                keep_alive_task.cancel()
                try:
                    await keep_alive_task
                except asyncio.CancelledError:
                    pass
                self.logger.info("💓 保活任務已停止")
            
            await self.stop()
    
    async def stop(self):
        """停止監控"""
        self.is_running = False
        
        # 停止交互式Telegram处理器
        if self.interactive_handler:
            try:
                await self.interactive_handler.stop_polling()
                self.logger.info("交互式Telegram訊息處理已停止")
            except Exception as e:
                self.logger.error(f"停止交互式處理器失敗: {e}")
        
        # 發送停止通知
        if self.config['notifications']['telegram_enabled']:
            runtime = datetime.now(TAIWAN_TZ) - self.stats['start_time'] if self.stats['start_time'] else timedelta(0)
            
            stop_message = f"""
🛑 <b>雲端監控系統停止</b>

📊 <b>運行統計:</b>
• 運行時間: {str(runtime).split('.')[0]}
• 檢查次數: {self.stats['checks_performed']}
• 警報發送: {self.stats['alerts_sent']}
• 錯誤次數: {self.stats['errors_count']}

⏰ <b>停止時間:</b> {datetime.now(TAIWAN_TZ).strftime('%Y-%m-%d %H:%M:%S')} (台灣時間)
            """
            
            try:
                await self.telegram_notifier.bot.send_message(
                    chat_id=self.telegram_notifier.chat_id,
                    text=stop_message.strip(),
                    parse_mode='HTML'
                )
            except Exception as e:
                self.logger.error(f"發送停止通知失敗: {e}")
        
        self.logger.info("雲端監控系統已停止")
    
    async def keep_alive_ping(self):
        """發送保活ping請求"""
        if not self.keep_alive_enabled:
            return
            
        try:
            # 添加多個端點ping，確保服務活躍
            endpoints = [
                f"{self.health_url}",
                f"{self.health_url.replace('/health', '/status')}" if '/health' in self.health_url else None
            ]
            
            success_count = 0
            for endpoint in endpoints:
                if endpoint is None:
                    continue
                    
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(endpoint, timeout=10) as response:
                            if response.status == 200:
                                success_count += 1
                                self.last_keep_alive = datetime.now(TAIWAN_TZ)
                                self.logger.info(f"保活ping成功: {endpoint} (狀態: {response.status})")
                            else:
                                self.logger.warning(f"保活ping回應異常: {endpoint} (狀態: {response.status})")
                except Exception as e:
                    self.logger.warning(f"單個端點ping失敗: {endpoint} - {e}")
            
            if success_count == 0:
                self.logger.error("所有保活ping都失敗了")
            else:
                self.logger.info(f"保活完成 - {success_count}/{len([e for e in endpoints if e])} 個端點成功")
                
        except Exception as e:
            self.logger.warning(f"保活ping失敗: {e}")
    
    async def keep_alive_task(self):
        """保活任務（背景運行）"""
        if not self.keep_alive_enabled:
            self.logger.info("保活功能已禁用")
            return
            
        self.logger.info(f"保活功能已啟動 - 間隔: {self.keep_alive_interval}秒 ({self.keep_alive_interval//60}分鐘)")
        self.logger.info(f"   目標URL: {self.health_url}")
        
        # 立即執行第一次ping
        self.logger.info("執行初始保活ping...")
        await self.keep_alive_ping()
        
        ping_count = 1
        while self.is_running:
            try:
                await asyncio.sleep(self.keep_alive_interval)
                if self.is_running:  # 再次檢查，避免停止時執行
                    ping_count += 1
                    self.logger.info(f"執行第 {ping_count} 次保活ping...")
                    await self.keep_alive_ping()
            except asyncio.CancelledError:
                self.logger.info(f"保活任務已取消 (共執行了 {ping_count} 次ping)")
                break
            except Exception as e:
                self.logger.error(f"保活任務出錯: {e}")
                await asyncio.sleep(60)  # 錯誤時等待1分鐘再試

    def get_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        try:
            if self.stats['start_time'] and isinstance(self.stats['start_time'], datetime):
                runtime = datetime.now() - self.stats['start_time']
                runtime_seconds = int(runtime.total_seconds())
                runtime_formatted = str(runtime).split('.')[0]
            else:
                runtime_seconds = 0
                runtime_formatted = "0:00:00"
            
            # 簡化狀態響應，避免序列化問題
            return {
                'is_running': self.is_running,
                'runtime_seconds': runtime_seconds,
                'runtime_formatted': runtime_formatted,
                'stats': {
                    'alerts_sent': self.stats['alerts_sent'],
                    'checks_performed': self.stats['checks_performed'],
                    'errors_count': self.stats['errors_count'],
                    'start_time': self.stats['start_time'].isoformat() if self.stats['start_time'] and isinstance(self.stats['start_time'], datetime) else None
                },
                'monitoring_symbols': self.config['monitoring']['symbols'],
                'monitoring_active': len(self.monitoring_data) > 0,
                'keep_alive': {
                    'enabled': self.keep_alive_enabled,
                    'interval_seconds': self.keep_alive_interval,
                    'health_url': self.health_url,
                    'last_ping': self.last_keep_alive.isoformat() if self.last_keep_alive else None
                },
                'telegram_handlers': {
                    'webhook_active': bool(self.webhook_handler),
                    'polling_active': bool(self.interactive_handler)
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'is_running': self.is_running,
                'timestamp': datetime.now().isoformat()
            }

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='雲端MACD監控系統')
    parser.add_argument('--config', default='monitor_config.json', help='配置文件路徑')
    parser.add_argument('--test', action='store_true', help='測試模式')
    args = parser.parse_args()
    
    monitor = CloudMonitor(args.config)
    
    if args.test:
        print("🧪 測試模式")
        # 可以添加測試邏輯
        return
    
    try:
        asyncio.run(monitor.run_forever())
    except KeyboardInterrupt:
        print("\n👋 監控系統已停止")

if __name__ == "__main__":
    main() 