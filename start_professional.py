#!/usr/bin/env python3
"""
🚀 BTC MACD 專業交易信號分析系統 - 專業版啟動器
Professional BTC MACD Trading Signal Analysis System - Professional Launcher
"""

import sys
import os
import traceback
import platform
from datetime import datetime

def print_banner():
    """顯示專業啟動橫幅"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🚀 BTC MACD 專業交易信號分析系統 v2.0 Professional Edition                    ║
║                                                                              ║
║    ✨ 專業版特色:                                                             ║
║    • 🎨 現代化專業界面設計                                                     ║
║    • 🔧 增強版字體配置                                                        ║
║    • 📊 專業級圖表視覺效果                                                     ║
║    • 🎯 智能信號分析系統                                                       ║
║    • 📱 實時通知推送                                                          ║
║    • 💾 自動數據記錄                                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)
    print(f"🖥️  系統: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"⏰ 啟動時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

def check_environment():
    """檢查運行環境"""
    print("🔍 正在檢查運行環境...")
    
    # 檢查Python版本
    if sys.version_info < (3, 7):
        print("❌ 錯誤: 需要 Python 3.7 或更高版本")
        return False
    
    # 檢查必要模組
    required_modules = {
        'tkinter': 'GUI框架',
        'matplotlib': '圖表繪製',
        'pandas': '數據處理',
        'numpy': '數值計算',
        'requests': 'HTTP請求',
        'schedule': '定時任務'
    }
    
    missing_modules = []
    for module, description in required_modules.items():
        try:
            __import__(module)
            print(f"✅ {module:12} - {description}")
        except ImportError:
            print(f"❌ {module:12} - {description} (缺失)")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️  缺少必要模組: {', '.join(missing_modules)}")
        print("請運行: pip install matplotlib pandas numpy requests schedule")
        return False
    
    # 檢查自定義模組
    custom_modules = {
        'max_api': 'MAX交易所API',
        'enhanced_macd_analyzer': '增強版MACD分析器',
        'telegram_notifier': 'Telegram通知器',
        'professional_font_config': '專業字體配置',
        'config': '配置文件'
    }
    
    for module, description in custom_modules.items():
        try:
            __import__(module)
            print(f"✅ {module:25} - {description}")
        except ImportError as e:
            print(f"❌ {module:25} - {description} (缺失)")
            print(f"   錯誤詳情: {e}")
            return False
    
    print("✅ 環境檢查完成，所有依賴項就緒！")
    return True

def test_font_system():
    """測試字體系統"""
    try:
        print("🔤 測試專業字體系統...")
        from professional_font_config import font_manager, setup_professional_style
        
        # 初始化字體
        setup_professional_style()
        
        print(f"✅ 字體系統初始化成功")
        print(f"   當前字體: {font_manager.current_font}")
        print(f"   中文支援: {'是' if font_manager.chinese_font_available else '否'}")
        print(f"   系統平台: {font_manager.system}")
        
        return True
    except Exception as e:
        print(f"❌ 字體系統測試失敗: {e}")
        return False

def run_professional_gui():
    """運行專業版GUI"""
    try:
        print("🚀 啟動專業版GUI...")
        from professional_main_gui import ProfessionalBTCMACDGUI
        
        # 創建並運行應用
        app = ProfessionalBTCMACDGUI()
        print("✅ 專業版GUI創建成功，啟動主循環...")
        app.run()
        
    except Exception as e:
        print(f"❌ 專業版GUI啟動失敗: {e}")
        traceback.print_exc()

def run_compatibility_mode():
    """運行兼容模式（舊版GUI）"""
    try:
        print("🔄 啟動兼容模式...")
        from optimized_main_gui import OptimizedBTCMACDGUI
        
        # 創建並運行應用
        app = OptimizedBTCMACDGUI()
        print("✅ 兼容模式GUI創建成功，啟動主循環...")
        app.run()
        
    except Exception as e:
        print(f"❌ 兼容模式啟動失敗: {e}")
        traceback.print_exc()

def run_test_mode():
    """運行測試模式"""
    try:
        print("🧪 運行系統測試...")
        from test_optimized import main as test_main
        test_main()
    except Exception as e:
        print(f"❌ 測試模式運行失敗: {e}")
        traceback.print_exc()

def run_ultimate_professional_gui():
    """運行終極專業版GUI"""
    try:
        print("🚀 啟動終極專業版GUI...")
        from ultimate_professional_gui import UltimateProfessionalBTCMACDGUI
        
        # 創建並運行應用
        app = UltimateProfessionalBTCMACDGUI()
        print("✅ 終極專業版GUI創建成功，啟動主循環...")
        app.run()
        
    except Exception as e:
        print(f"❌ 終極專業版GUI啟動失敗: {e}")
        traceback.print_exc()

def show_menu():
    """顯示啟動菜單"""
    print("\n📋 請選擇啟動模式:")
    print("1. 🚀 終極專業版GUI (推薦)")
    print("2. 🚀 專業版GUI")
    print("3. 🔄 兼容模式GUI")
    print("4. 🧪 系統測試模式")
    print("5. 🔤 字體系統測試")
    print("6. ❌ 退出")
    print("-" * 40)
    
    while True:
        try:
            choice = input("請輸入選項 (1-6): ").strip()
            
            if choice == '1':
                print("\n🚀 正在啟動終極專業版GUI...")
                return run_ultimate_professional_gui
            elif choice == '2':
                print("\n🚀 正在啟動專業版GUI...")
                return run_professional_gui
            elif choice == '3':
                print("\n🔄 正在啟動兼容模式...")
                return run_compatibility_mode
            elif choice == '4':
                print("\n🧪 正在運行系統測試...")
                return run_test_mode
            elif choice == '5':
                print("\n🔤 正在測試字體系統...")
                test_font_system()
                print("\n回到主菜單...")
                show_menu()
                return None
            elif choice == '6':
                print("👋 再見！")
                return None
            else:
                print("⚠️  無效選項，請輸入 1-6")
                
        except KeyboardInterrupt:
            print("\n\n👋 用戶取消，再見！")
            return None
        except Exception as e:
            print(f"⚠️  輸入錯誤: {e}")

def main():
    """主啟動函數"""
    try:
        # 顯示啟動橫幅
        print_banner()
        
        # 檢查環境
        if not check_environment():
            print("\n❌ 環境檢查失敗，無法啟動系統")
            input("按 Enter 鍵退出...")
            return
        
        # 測試字體系統
        if not test_font_system():
            print("⚠️  字體系統測試失敗，但程序仍可繼續運行")
        
        print("\n🎉 系統就緒！")
        
        # 顯示菜單並執行選擇
        action = show_menu()
        if action:
            action()
            
    except KeyboardInterrupt:
        print("\n\n👋 用戶中斷，程序退出")
    except Exception as e:
        print(f"\n❌ 啟動器發生未預期錯誤: {e}")
        traceback.print_exc()
        input("按 Enter 鍵退出...")

if __name__ == "__main__":
    main() 