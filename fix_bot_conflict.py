#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修復Telegram Bot衝突問題
清除webhook和重置bot狀態
"""

import os
import asyncio
from telegram import Bot

async def fix_bot_conflict():
    """修復bot衝突"""
    print("🔧 修復Telegram Bot衝突問題")
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN 環境變數未設置")
        return
    
    try:
        bot = Bot(token=bot_token)
        
        print("🔍 檢查當前webhook狀態...")
        webhook_info = await bot.get_webhook_info()
        
        if webhook_info.url:
            print(f"🗑️  發現webhook: {webhook_info.url}")
            print("正在刪除webhook...")
            success = await bot.delete_webhook(drop_pending_updates=True)
            if success:
                print("✅ Webhook已刪除，待處理更新已清除")
            else:
                print("❌ 刪除webhook失敗")
        else:
            print("✅ 沒有設置webhook")
        
        print("🧹 清除待處理更新...")
        # 獲取並丟棄所有待處理更新
        try:
            updates = await bot.get_updates(timeout=1, limit=100)
            if updates:
                print(f"🗑️  清除了 {len(updates)} 個待處理更新")
                # 確認收到最後一個更新，以清除所有待處理更新
                last_update_id = updates[-1].update_id
                await bot.get_updates(offset=last_update_id + 1, timeout=1)
                print("✅ 所有待處理更新已清除")
            else:
                print("✅ 沒有待處理更新")
        except Exception as e:
            print(f"⚠️  清除更新時出現輕微錯誤: {e}")
        
        print("📋 Bot資訊:")
        me = await bot.get_me()
        print(f"  Bot名稱: {me.first_name}")
        print(f"  用戶名: @{me.username}")
        print(f"  Bot ID: {me.id}")
        
        print("\n✅ Bot衝突修復完成！")
        print("💡 現在可以重新啟動監控系統")
        
    except Exception as e:
        print(f"❌ 修復過程中出錯: {e}")

if __name__ == "__main__":
    asyncio.run(fix_bot_conflict()) 