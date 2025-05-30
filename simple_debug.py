#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
簡化的調試腳本
"""

import os
import requests

def check_telegram_bot():
    """檢查Telegram Bot設置"""
    print("🔍 檢查Telegram Bot設置")
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    print(f"📱 Bot Token: {'已設置' if bot_token else '❌ 未設置'}")
    print(f"💬 Chat ID: {'已設置' if chat_id else '❌ 未設置'}")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN 環境變數未設置")
        return False
    
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID 環境變數未設置")
        return False
    
    try:
        # 測試Bot API
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                print(f"✅ Bot連接成功: {data['result']['username']}")
                return True
            else:
                print(f"❌ Bot API錯誤: {data}")
        else:
            print(f"❌ HTTP錯誤: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 連接錯誤: {e}")
    
    return False

def check_interactive_import():
    """檢查交互式模組導入"""
    print("\n📦 檢查模組導入")
    
    try:
        from interactive_telegram_handler import InteractiveTelegramHandler
        print("✅ interactive_telegram_handler 導入成功")
        
        from cloud_monitor import CloudMonitor
        print("✅ cloud_monitor 導入成功")
        
        # 測試初始化
        monitor = CloudMonitor()
        if hasattr(monitor, 'interactive_handler') and monitor.interactive_handler:
            print("✅ interactive_handler 已初始化")
        else:
            print("❌ interactive_handler 未初始化")
            
    except Exception as e:
        print(f"❌ 模組導入失敗: {e}")

def main():
    print("🚀 簡化調試開始\n")
    
    # 檢查Bot設置
    bot_ok = check_telegram_bot()
    
    # 檢查模組導入
    check_interactive_import()
    
    print("\n💡 重要提醒:")
    print("1. 確保您的Render.com應用程式包含所有檔案")
    print("2. 環境變數必須在Render.com控制台設置")
    print("3. 可能需要重新部署後生效")
    
    if bot_ok:
        print("\n🧪 請在Telegram發送測試訊息：")
        print("   發送：買進?")
        print("   發送：賣出?")
        print("   如果仍無回應，問題可能在雲端部署")

if __name__ == "__main__":
    main() 