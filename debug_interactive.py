#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
調試交互式Telegram功能
檢查為什麼在雲端平台無法正常工作
"""

import os
import asyncio
import logging
from telegram import Bot
import json

async def debug_telegram_bot():
    """調試Telegram機器人設置"""
    print("🔍 調試交互式Telegram功能")
    
    # 檢查環境變數
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    print(f"📱 Bot Token: {'已設置' if bot_token else '❌ 未設置'}")
    print(f"💬 Chat ID: {'已設置' if chat_id else '❌ 未設置'}")
    
    if not bot_token or not chat_id:
        print("❌ 環境變數未正確設置")
        return False
    
    try:
        # 測試Bot連接
        bot = Bot(token=bot_token)
        print("🤖 正在測試Bot連接...")
        
        # 獲取Bot資訊
        me = await bot.get_me()
        print(f"✅ Bot連接成功: {me.username}")
        
        # 測試發送訊息
        test_message = """
🧪 <b>交互式功能測試</b>

如果您看到這條訊息，說明Bot可以正常發送訊息。

現在請嘗試發送：
• "買進?" 
• "賣出?"

系統應該會回覆AI分析。
        """
        
        await bot.send_message(
            chat_id=int(chat_id),
            text=test_message.strip(),
            parse_mode='HTML'
        )
        print("✅ 測試訊息已發送")
        
        # 檢查webhook設置
        webhook_info = await bot.get_webhook_info()
        print(f"🔗 Webhook URL: {webhook_info.url if webhook_info.url else '未設置'}")
        
        if webhook_info.url:
            print("⚠️  檢測到Webhook設置，這可能與長輪詢衝突")
            print("   建議刪除Webhook以啟用長輪詢模式")
            
            # 可選：刪除webhook
            await bot.delete_webhook()
            print("🗑️  Webhook已刪除")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot測試失敗: {e}")
        return False

async def test_message_handling():
    """測試訊息處理"""
    print("\n📨 測試訊息處理邏輯")
    
    try:
        from interactive_telegram_handler import InteractiveTelegramHandler
        from cloud_monitor import CloudMonitor
        
        # 初始化監控器
        monitor = CloudMonitor()
        
        # 檢查交互式處理器
        if monitor.interactive_handler:
            print("✅ 交互式處理器已初始化")
            
            # 測試訊息識別
            test_queries = ["買進?", "賣出?", "买进?", "sell?"]
            for query in test_queries:
                is_trading = monitor.interactive_handler.is_trading_query(query)
                print(f"   '{query}' -> {'✅ 識別為交易詢問' if is_trading else '❌ 未識別'}")
        else:
            print("❌ 交互式處理器未初始化")
            
    except Exception as e:
        print(f"❌ 訊息處理測試失敗: {e}")

def check_deployment_config():
    """檢查部署配置"""
    print("\n⚙️  檢查部署配置")
    
    # 檢查必要文件
    required_files = [
        'interactive_telegram_handler.py',
        'cloud_monitor.py',
        'requirements.txt'
    ]
    
    for file in required_files:
        exists = os.path.exists(file)
        print(f"   {file}: {'✅ 存在' if exists else '❌ 缺失'}")
    
    # 檢查requirements.txt
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
            has_telegram = 'python-telegram-bot' in requirements
            print(f"   Telegram依賴: {'✅ 已包含' if has_telegram else '❌ 缺失'}")
    except:
        print("   ❌ 無法讀取requirements.txt")

async def main():
    """主函數"""
    print("🚀 開始調試交互式Telegram功能\n")
    
    # 1. 檢查部署配置
    check_deployment_config()
    
    # 2. 測試Bot連接
    bot_ok = await debug_telegram_bot()
    
    # 3. 測試訊息處理
    if bot_ok:
        await test_message_handling()
    
    print("\n📋 調試完成")
    print("如果Bot連接正常但仍無回應，可能需要：")
    print("1. 重新部署到Render.com")
    print("2. 檢查雲端日誌")
    print("3. 確認應用程式正在運行交互式功能")

if __name__ == "__main__":
    asyncio.run(main()) 