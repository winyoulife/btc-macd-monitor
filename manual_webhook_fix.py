#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
手動Webhook清理腳本
使用正確的Token徹底清除所有衝突
"""

import asyncio
import sys
from telegram import Bot
from telegram.error import TelegramError

async def manual_webhook_fix():
    """手動修復webhook衝突"""
    # 使用正確的Token
    bot_token = "7323086952:AAE5fkQp8n98TOYnPpj2KPyrCI6hX5R2n2I"
    chat_id = "8164385222"
    
    print("🔧 手動Webhook修復工具")
    print("=" * 50)
    
    bot = Bot(token=bot_token)
    
    try:
        print("🔍 1. 檢查Bot狀態...")
        me = await bot.get_me()
        print(f"   Bot: {me.first_name} (@{me.username})")
        print(f"   ID: {me.id}")
        
        print("\n🔍 2. 檢查當前Webhook...")
        webhook_info = await bot.get_webhook_info()
        print(f"   URL: {webhook_info.url or '未設置'}")
        print(f"   待處理: {webhook_info.pending_update_count}")
        print(f"   錯誤: {webhook_info.last_error_message or '無'}")
        
        print("\n🧹 3. 強制清除所有Webhook...")
        await bot.delete_webhook(drop_pending_updates=True)
        print("   ✅ 第一次清除完成")
        
        await asyncio.sleep(3)
        
        print("\n🧹 4. 深度清除...")
        # 設置假webhook再刪除
        await bot.set_webhook(url="https://example.com/clear", drop_pending_updates=True)
        await asyncio.sleep(2)
        await bot.delete_webhook(drop_pending_updates=True)
        print("   ✅ 深度清除完成")
        
        await asyncio.sleep(3)
        
        print("\n🧪 5. 驗證清除結果...")
        webhook_info = await bot.get_webhook_info()
        print(f"   最終URL: {webhook_info.url or '✅ 已清除'}")
        print(f"   最終待處理: {webhook_info.pending_update_count}")
        
        print("\n🧪 6. 測試長輪詢...")
        try:
            updates = await bot.get_updates(limit=1, timeout=5)
            print(f"   ✅ 長輪詢測試成功，獲得 {len(updates)} 個更新")
        except Exception as e:
            if "Conflict" in str(e):
                print(f"   ❌ 仍有衝突: {e}")
                print("   🔄 進行最終清理...")
                
                for i in range(3):
                    await asyncio.sleep(5)
                    await bot.delete_webhook(drop_pending_updates=True)
                    try:
                        updates = await bot.get_updates(limit=1, timeout=3)
                        print(f"   ✅ 第 {i+1} 次最終測試成功")
                        break
                    except:
                        print(f"   ⏳ 第 {i+1} 次最終測試失敗，繼續...")
            else:
                print(f"   ❌ 其他錯誤: {e}")
        
        print("\n🎉 7. 發送測試通知...")
        try:
            await bot.send_message(
                chat_id=chat_id,
                text="🔧 <b>手動Webhook修復完成</b>\n\n✅ 現在嘗試發送 '買進?' 測試功能",
                parse_mode='HTML'
            )
            print("   ✅ 測試通知已發送")
        except Exception as e:
            print(f"   ❌ 發送通知失敗: {e}")
        
        print("\n✅ 手動修復完成！")
        print("\n💡 下一步:")
        print("1. 等待 30 秒")
        print("2. 重新部署 Render.com 服務")
        print("3. 測試 '買進?' 功能")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 修復失敗: {e}")
        import traceback
        print(f"詳細錯誤: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 開始手動修復...")
    success = asyncio.run(manual_webhook_fix())
    
    if success:
        print("\n🎯 修復成功！請重新部署服務")
    else:
        print("\n💥 修復失敗，請檢查網路連接") 