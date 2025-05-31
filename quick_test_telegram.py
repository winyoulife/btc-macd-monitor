#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速測試Telegram功能的腳本
"""

import asyncio
import os
from telegram import Bot

async def test_telegram_response():
    """直接測試Telegram回應"""
    
    # 從環境變數或config.py獲取設置
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token:
        try:
            from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
            bot_token = TELEGRAM_BOT_TOKEN
            chat_id = TELEGRAM_CHAT_ID
        except ImportError:
            print("❌ 找不到Telegram配置")
            return
    
    print(f"📱 測試Telegram連接...")
    print(f"   Bot Token: {bot_token[:10]}...")
    print(f"   Chat ID: {chat_id}")
    
    try:
        bot = Bot(token=bot_token)
        
        # 測試訊息
        test_message = """
🧪 <b>測試新的回應格式</b>

這是測試訊息，確認修改是否生效：

📊 <b>24小時新聞統計:</b>
• 📈 利多消息: 2 筆
• 📉 利空消息: 0 筆
• ➡️ 中性消息: 1 筆

🔮 <b>市場展望:</b>
• 短期: 樂觀看漲 - 技術指標顯示上漲趨勢，建議關注買進機會
• 長期: 中性觀望 - 技術指標方向不明，建議持有觀察市場變化

📈 <b>機率預測:</b>
• 🚀 上漲機率: 65%
• 📉 下跌機率: 35%

✅ 如果您看到這個格式，表示修改已生效！
        """
        
        await bot.send_message(
            chat_id=int(chat_id),
            text=test_message.strip(),
            parse_mode='HTML'
        )
        
        print("✅ 測試訊息已發送到Telegram！")
        print("📱 請檢查您的Telegram，看看新格式是否顯示正確")
        
    except Exception as e:
        print(f"❌ 發送測試訊息失敗: {e}")

if __name__ == "__main__":
    asyncio.run(test_telegram_response()) 