#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
強力修復Telegram Bot衝突問題
徹底清除所有衝突實例和webhooks
"""

import asyncio
import os
import sys
import time
from telegram import Bot
from telegram.error import TelegramError

async def force_clear_bot_conflicts():
    """強力清除Bot衝突"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ 未設置 TELEGRAM_BOT_TOKEN 環境變數")
        return False
    
    print("🔧 強力修復Telegram Bot衝突")
    print("=" * 50)
    
    bot = Bot(token=bot_token)
    
    try:
        print("🔍 1. 檢查Bot信息...")
        me = await bot.get_me()
        print(f"   Bot名稱: {me.first_name} (@{me.username})")
        print(f"   Bot ID: {me.id}")
        
        print("\n🔍 2. 檢查當前webhook狀態...")
        webhook_info = await bot.get_webhook_info()
        print(f"   Webhook URL: {webhook_info.url or '未設置'}")
        print(f"   待處理更新: {webhook_info.pending_update_count}")
        print(f"   最後錯誤: {webhook_info.last_error_message or '無'}")
        
        if webhook_info.url:
            print("\n🧹 3. 刪除現有webhook...")
            await bot.delete_webhook(drop_pending_updates=True)
            print("   ✅ Webhook已刪除")
            await asyncio.sleep(3)  # 等待確保刪除完成
        else:
            print("\n✅ 3. 無需刪除webhook")
        
        print("\n🧹 4. 清除所有待處理更新...")
        # 通過設置一個臨時webhook然後立即刪除來清除所有更新
        temp_url = "https://httpbin.org/post"  # 臨時測試URL
        await bot.set_webhook(url=temp_url, drop_pending_updates=True)
        await asyncio.sleep(2)
        await bot.delete_webhook(drop_pending_updates=True)
        print("   ✅ 待處理更新已清除")
        
        print("\n🔄 5. 測試Bot連接...")
        # 嘗試獲取更新以測試連接
        try:
            updates = await bot.get_updates(limit=1, timeout=5)
            print(f"   ✅ Bot連接正常，獲得 {len(updates)} 個更新")
        except Exception as e:
            if "Conflict" in str(e):
                print(f"   ⚠️  仍有衝突: {e}")
                print("   🔄 進行額外清理...")
                
                # 更激進的清理方法
                for i in range(3):
                    try:
                        await asyncio.sleep(5)  # 等待更長時間
                        await bot.delete_webhook(drop_pending_updates=True)
                        updates = await bot.get_updates(limit=1, timeout=3)
                        print(f"   ✅ 第 {i+1} 次嘗試成功")
                        break
                    except Exception as retry_e:
                        print(f"   ❌ 第 {i+1} 次嘗試失敗: {retry_e}")
                        if i == 2:  # 最後一次嘗試
                            print("   ⚠️  可能需要等待更長時間讓其他實例自動停止")
            else:
                print(f"   ❌ 其他錯誤: {e}")
        
        print("\n✅ Bot衝突清理完成!")
        print("\n💡 建議:")
        print("   1. 等待 30-60 秒讓所有實例完全停止")
        print("   2. 確保沒有本地測試腳本在運行")
        print("   3. 重新部署 Render.com 應用")
        print("   4. 部署完成後測試 '買進?' 功能")
        
        return True
        
    except Exception as e:
        print(f"❌ 修復過程中出錯: {e}")
        import traceback
        print(f"詳細錯誤: {traceback.format_exc()}")
        return False

async def main():
    """主函數"""
    print("🚀 開始強力修復Bot衝突...")
    
    success = await force_clear_bot_conflicts()
    
    if success:
        print("\n🎉 修復完成！")
        print("\n下一步：")
        print("1. 推送此修復到GitHub")
        print("2. 等待Render.com自動重新部署")
        print("3. 部署完成後在Telegram測試")
    else:
        print("\n❌ 修復失敗，請檢查Bot Token")

if __name__ == "__main__":
    # 設置環境變數（如果在本地運行）
    if len(sys.argv) > 1 and len(sys.argv) > 2:
        os.environ['TELEGRAM_BOT_TOKEN'] = sys.argv[1]
        print(f"使用命令行提供的Bot Token: {sys.argv[1][:10]}...")
    
    asyncio.run(main()) 