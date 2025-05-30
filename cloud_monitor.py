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
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import schedule
import pandas as pd

from max_api import MaxAPI
from enhanced_macd_analyzer import EnhancedMACDAnalyzer
from telegram_notifier import TelegramNotifier

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
        """設置日誌系統"""
        log_level = logging.INFO
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # 創建logger
        self.logger = logging.getLogger('CloudMonitor')
        self.logger.setLevel(log_level)
        
        # 移除現有的handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 控制台handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(log_format)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 文件handler
        file_handler = logging.FileHandler('cloud_monitor.log')
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
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
                }
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
        self.stats['start_time'] = datetime.now()
        
        self.logger.info("雲端監控系統啟動")
        
        # 發送啟動通知
        if self.config['notifications']['telegram_enabled']:
            start_message = f"""
🤖 <b>雲端監控系統啟動</b>

📊 <b>監控設定:</b>
• 交易對: {', '.join(self.config['monitoring']['symbols'])}
• 週期: {self.config['monitoring']['primary_period']}分鐘
• 檢查間隔: {self.config['monitoring']['check_interval']}秒

⏰ <b>啟動時間:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔔 系統將開始監控市場並發送警報通知
            """
            
            try:
                await self.telegram_notifier.bot.send_message(
                    chat_id=self.telegram_notifier.chat_id,
                    text=start_message.strip(),
                    parse_mode='HTML'
                )
            except Exception as e:
                self.logger.error(f"發送啟動通知失敗: {e}")
        
        # 主監控循環
        interval = self.config['monitoring']['check_interval']
        
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
            await self.stop()
    
    async def stop(self):
        """停止監控"""
        self.is_running = False
        
        # 發送停止通知
        if self.config['notifications']['telegram_enabled']:
            runtime = datetime.now() - self.stats['start_time'] if self.stats['start_time'] else timedelta(0)
            
            stop_message = f"""
🛑 <b>雲端監控系統停止</b>

📊 <b>運行統計:</b>
• 運行時間: {str(runtime).split('.')[0]}
• 檢查次數: {self.stats['checks_performed']}
• 警報發送: {self.stats['alerts_sent']}
• 錯誤次數: {self.stats['errors_count']}

⏰ <b>停止時間:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
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