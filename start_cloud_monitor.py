#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
雲端MACD監控系統啟動器
整合監控功能和健康檢查服務
"""

import asyncio
import os
import signal
import sys
from cloud_monitor import CloudMonitor
from health_server import HealthServer

class CloudMonitorService:
    """雲端監控服務管理器"""
    
    def __init__(self, config_file='monitor_config.json'):
        self.monitor = CloudMonitor(config_file)
        self.health_server = None
        self.is_stopping = False
        
        # 設置信號處理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """處理停止信號"""
        if not self.is_stopping:
            self.is_stopping = True
            print(f"\n📡 收到停止信號 ({signum})")
            asyncio.create_task(self.stop())
    
    async def start(self):
        """啟動完整的雲端監控服務"""
        print("🚀 啟動雲端MACD監控系統")
        print("="*50)
        
        try:
            # 啟動健康檢查服務器
            health_port = self.monitor.config['cloud']['health_check_port']
            self.health_server = HealthServer(self.monitor, health_port)
            self.health_server.start()
            
            print("\n📊 監控配置:")
            config = self.monitor.config
            print(f"   • 交易對: {', '.join(config['monitoring']['symbols'])}")
            print(f"   • 主要週期: {config['monitoring']['primary_period']}分鐘")
            print(f"   • 檢查間隔: {config['monitoring']['check_interval']}秒")
            print(f"   • 平台: {config['cloud']['platform']}")
            
            print("\n🔔 通知設定:")
            notifications = config['notifications']
            for service, enabled in notifications.items():
                status = "✅" if enabled else "❌"
                print(f"   • {service.replace('_', ' ').title()}: {status}")
            
            print(f"\n⚙️  高級設定:")
            advanced = config['advanced']
            print(f"   • 冷卻期: {advanced['cooldown_period']}秒")
            print(f"   • 每小時最大警報: {advanced['max_alerts_per_hour']}次")
            
            print("\n" + "="*50)
            
            # 啟動監控
            await self.monitor.run_forever()
            
        except Exception as e:
            print(f"❌ 啟動失敗: {e}")
            await self.stop()
    
    async def stop(self):
        """停止所有服務"""
        if self.is_stopping:
            return
            
        self.is_stopping = True
        print("\n🔄 正在停止服務...")
        
        # 停止監控
        if self.monitor:
            await self.monitor.stop()
        
        # 停止健康檢查服務器
        if self.health_server:
            self.health_server.stop()
        
        print("✅ 所有服務已停止")

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='雲端MACD監控系統',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例子:
  python start_cloud_monitor.py                    # 使用默認配置
  python start_cloud_monitor.py --config my.json  # 使用自定義配置
  python start_cloud_monitor.py --test            # 測試模式
        """
    )
    
    parser.add_argument(
        '--config', 
        default='monitor_config.json',
        help='配置文件路徑 (默認: monitor_config.json)'
    )
    
    parser.add_argument(
        '--test', 
        action='store_true',
        help='測試模式 - 僅檢查配置和連接'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='健康檢查服務器端口 (默認: 8080)'
    )
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 測試模式")
        test_system(args.config)
        return
    
    # 創建並啟動服務
    service = CloudMonitorService(args.config)
    
    # 更新端口配置
    service.monitor.config['cloud']['health_check_port'] = args.port
    
    try:
        asyncio.run(service.start())
    except KeyboardInterrupt:
        print("\n👋 用戶中斷")
    except Exception as e:
        print(f"\n❌ 系統錯誤: {e}")
        sys.exit(1)

def test_system(config_file):
    """測試系統配置和連接"""
    print("🔍 檢查系統配置...")
    
    try:
        # 測試配置載入
        monitor = CloudMonitor(config_file)
        print("✅ 配置文件載入成功")
        
        # 測試API連接
        print("\n🔗 測試API連接...")
        ticker = monitor.max_api.get_ticker('btctwd')
        if ticker:
            print(f"✅ MAX API連接成功 - BTC價格: ${ticker['price']:,.0f}")
        else:
            print("❌ MAX API連接失敗")
        
        # 測試Telegram連接
        if monitor.config['notifications']['telegram_enabled']:
            print("\n📱 測試Telegram連接...")
            
            async def test_telegram():
                try:
                    success, message = await monitor.telegram_notifier.test_connection()
                    if success:
                        print(f"✅ Telegram連接成功: {message}")
                    else:
                        print(f"❌ Telegram連接失敗: {message}")
                except Exception as e:
                    print(f"❌ Telegram測試錯誤: {e}")
            
            try:
                # 使用新的event loop來避免衝突
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(test_telegram())
                loop.close()
            except Exception as e:
                print(f"❌ Telegram測試失敗: {e}")
        
        print("\n✅ 系統測試完成")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 