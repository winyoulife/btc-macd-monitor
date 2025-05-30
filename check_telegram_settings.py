#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
檢查並修復Telegram設置
"""

import os

def check_current_settings():
    """檢查當前設置"""
    print("🔍 檢查當前Telegram設置")
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    print(f"📱 Bot Token: {bot_token[:10] + '...' if bot_token else '❌ 未設置'}")
    print(f"💬 Chat ID: {chat_id if chat_id else '❌ 未設置'}")
    
    return bot_token, chat_id

def provide_fix_instructions():
    """提供修復指導"""
    print("\n🔧 修復指導:")
    print("1. 確認您的Bot Token是否正確")
    print("   - 去 @BotFather 確認您的bot")
    print("   - Token格式: 1234567890:ABCdef123...")
    print()
    print("2. 在Render.com設置環境變數:")
    print("   - 登入 https://dashboard.render.com")
    print("   - 點擊您的 btc-macd-monitor 服務")
    print("   - 進入 Environment 頁面")
    print("   - 添加/更新環境變數：")
    print("     TELEGRAM_BOT_TOKEN = 您的bot token")
    print("     TELEGRAM_CHAT_ID = 您的chat id")
    print()
    print("3. 重新部署:")
    print("   - 在Render.com點擊 Manual Deploy")
    print("   - 或推送代碼到GitHub觸發自動部署")
    print()
    print("4. 測試步驟:")
    print("   - 等待部署完成")
    print("   - 在Telegram發送: 買進?")
    print("   - 應該收到AI分析回覆")

def main():
    print("🚀 Telegram設置檢查工具\n")
    
    bot_token, chat_id = check_current_settings()
    
    if not bot_token or not chat_id:
        print("\n❌ 環境變數設置不完整")
    else:
        print("\n✅ 本地環境變數已設置")
        print("   但雲端可能不一致，請檢查Render.com設置")
    
    provide_fix_instructions()
    
    print("\n💡 重要:")
    print("交互式功能需要在雲端正確運行，本地測試可能有限制")

if __name__ == "__main__":
    main() 