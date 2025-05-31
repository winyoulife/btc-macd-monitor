#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速價格變化警報系統
專門檢測快速價格變化，不依賴複雜技術指標
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from max_api import MaxAPI
import requests

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QuickPriceAlert:
    def __init__(self):
        self.max_api = MaxAPI()
        self.previous_price = None
        self.price_history = []
        self.alert_thresholds = {
            'minute_change': 0.5,  # 1分鐘變化0.5%觸發警報
            'five_minute_change': 1.0,  # 5分鐘變化1.0%觸發警報
            'volume_spike': 1.5,  # 成交量放大1.5倍觸發警報
        }
        
    async def send_telegram_alert(self, message):
        """發送Telegram警報"""
        try:
            bot_token = "7323086952:AAE5fkQp8n98TOYnPpj2KPyrCI6hX5R2n2I"
            chat_id = "6839863072"
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Telegram警報發送成功")
            else:
                logger.error(f"❌ Telegram警報發送失敗: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Telegram警報發送錯誤: {e}")
    
    def check_price_alerts(self, current_data, previous_data=None):
        """檢查價格警報"""
        alerts = []
        current_price = current_data['price']
        current_time = current_data['timestamp']
        
        # 檢查瞬時價格變化
        if previous_data:
            prev_price = previous_data['price']
            price_change_pct = ((current_price - prev_price) / prev_price) * 100
            
            if abs(price_change_pct) >= self.alert_thresholds['minute_change']:
                direction = "📈 急漲" if price_change_pct > 0 else "📉 急跌"
                alerts.append({
                    'type': 'PRICE_SPIKE',
                    'message': f"{direction} {abs(price_change_pct):.2f}%",
                    'severity': 'HIGH' if abs(price_change_pct) >= 1.0 else 'MEDIUM'
                })
        
        # 檢查5分鐘內的累積變化
        if len(self.price_history) >= 5:
            five_min_ago_price = self.price_history[-5]['price']
            five_min_change = ((current_price - five_min_ago_price) / five_min_ago_price) * 100
            
            if abs(five_min_change) >= self.alert_thresholds['five_minute_change']:
                direction = "📈 持續上漲" if five_min_change > 0 else "📉 持續下跌"
                alerts.append({
                    'type': 'TREND_ALERT',
                    'message': f"{direction} 5分鐘累積 {abs(five_min_change):.2f}%",
                    'severity': 'HIGH' if abs(five_min_change) >= 1.5 else 'MEDIUM'
                })
        
        # 檢查成交量異常
        if 'volume' in current_data and len(self.price_history) >= 3:
            avg_volume = sum([d['volume'] for d in self.price_history[-3:]]) / 3
            if avg_volume > 0:
                volume_ratio = current_data['volume'] / avg_volume
                if volume_ratio >= self.alert_thresholds['volume_spike']:
                    alerts.append({
                        'type': 'VOLUME_SPIKE',
                        'message': f"💥 成交量爆發 {volume_ratio:.1f}倍",
                        'severity': 'HIGH' if volume_ratio >= 2.0 else 'MEDIUM'
                    })
        
        return alerts
    
    async def monitor_price_changes(self):
        """持續監控價格變化"""
        logger.info("🚀 開始快速價格監控...")
        
        while True:
            try:
                # 獲取當前市場數據
                ticker = self.max_api.get_ticker('btcusdt')
                if not ticker:
                    logger.warning("❌ 無法獲取價格數據")
                    await asyncio.sleep(30)
                    continue
                
                current_data = {
                    'price': ticker['price'],
                    'volume': ticker['volume'],
                    'timestamp': datetime.now()
                }
                
                # 檢查警報
                previous_data = self.price_history[-1] if self.price_history else None
                alerts = self.check_price_alerts(current_data, previous_data)
                
                # 發送警報
                for alert in alerts:
                    message = f"""
🚨 <b>BTC快速變化警報</b>

💰 當前價格: {current_data['price']:,.0f} TWD
⚡ 變化: {alert['message']}
⏰ 時間: {current_data['timestamp'].strftime('%H:%M:%S')}
🔥 級別: {alert['severity']}

#BTC #快速警報 #{alert['type']}
"""
                    await self.send_telegram_alert(message.strip())
                    logger.info(f"🚨 發送警報: {alert['message']}")
                
                # 更新歷史記錄
                self.price_history.append(current_data)
                
                # 只保留最近10分鐘的數據
                cutoff_time = datetime.now() - timedelta(minutes=10)
                self.price_history = [
                    d for d in self.price_history 
                    if d['timestamp'] > cutoff_time
                ]
                
                # 每次都輸出當前狀態（方便調試）
                if len(self.price_history) >= 2:
                    last_change = ((current_data['price'] - self.price_history[-2]['price']) / 
                                 self.price_history[-2]['price']) * 100
                    logger.info(f"💰 BTC: {current_data['price']:,.0f} TWD ({last_change:+.2f}%)")
                else:
                    logger.info(f"💰 BTC: {current_data['price']:,.0f} TWD")
                
                # 等待下次檢查（30秒間隔以捕獲快速變化）
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ 監控錯誤: {e}")
                await asyncio.sleep(60)  # 錯誤時等待更長時間

async def main():
    """主函數"""
    alert_system = QuickPriceAlert()
    
    # 發送啟動通知
    startup_message = f"""
🚀 <b>快速價格警報系統啟動</b>

📊 監控設置:
• 1分鐘變化 ≥ 0.5% 觸發警報
• 5分鐘變化 ≥ 1.0% 觸發警報  
• 成交量放大 ≥ 1.5倍 觸發警報

⏰ 啟動時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#系統啟動 #快速警報
"""
    await alert_system.send_telegram_alert(startup_message.strip())
    
    # 開始監控
    await alert_system.monitor_price_changes()

if __name__ == "__main__":
    asyncio.run(main()) 