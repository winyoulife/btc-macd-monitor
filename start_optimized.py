#!/usr/bin/env python3
"""
BTC MACD 專業交易信號分析系統 - 優化版啟動腳本
"""

import sys
import os
import subprocess
import importlib
from datetime import datetime

def check_python_version():
    """檢查Python版本"""
    if sys.version_info < (3, 7):
        print("❌ 錯誤: 需要 Python 3.7 或以上版本")
        print(f"當前版本: {sys.version}")
        return False
    print(f"✅ Python 版本檢查通過: {sys.version}")
    return True

def check_dependencies():
    """檢查依賴套件"""
    required_packages = [
        'tkinter',
        'matplotlib',
        'pandas',
        'numpy',
        'requests',
        'ta',
        'schedule'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            else:
                importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (缺失)")
            missing_packages.append(package)
    
    if missing_packages:
        print("\n⚠️  發現缺失的套件，正在安裝...")
        install_missing_packages(missing_packages)
        return False
    
    return True

def install_missing_packages(packages):
    """安裝缺失的套件"""
    try:
        print("執行: pip install -r requirements.txt")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 套件安裝完成")
            return True
        else:
            print("❌ 套件安裝失敗")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ 安裝過程中發生錯誤: {e}")
        return False

def check_config_file():
    """檢查配置文件"""
    if not os.path.exists('config.py'):
        print("❌ 配置文件 config.py 不存在")
        return False
    
    try:
        import config
        print("✅ 配置文件檢查通過")
        return True
    except Exception as e:
        print(f"❌ 配置文件錯誤: {e}")
        return False

def main():
    """主函數"""
    print("="*60)
    print("🚀 BTC MACD 專業交易信號分析系統 - 優化版")
    print("="*60)
    print(f"啟動時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 環境檢查
    print("🔍 環境檢查中...")
    if not check_python_version():
        input("按任意鍵退出...")
        return
    
    if not check_dependencies():
        print("\n請重新運行此腳本以完成套件安裝")
        input("按任意鍵退出...")
        return
    
    if not check_config_file():
        input("按任意鍵退出...")
        return
    
    print("\n✅ 所有檢查通過！")
    print("\n" + "="*60)
    print("請選擇啟動方式:")
    print("1. 🚀 啟動優化版主程式 (推薦)")
    print("2. 📊 僅啟動 MACD 詳細視窗 (測試)")
    print("3. ⚙️  Telegram 設定助手")
    print("4. 🔧 啟動原版程式")
    print("5. ❌ 退出")
    print("="*60)
    
    while True:
        try:
            choice = input("\n請輸入選項 (1-5): ").strip()
            
            if choice == '1':
                print("\n🚀 啟動優化版主程式...")
                try:
                    from optimized_main_gui import main as optimized_main
                    optimized_main()
                except Exception as e:
                    print(f"❌ 啟動失敗: {e}")
                    input("按任意鍵退出...")
                break
                
            elif choice == '2':
                print("\n📊 啟動 MACD 詳細視窗...")
                try:
                    from macd_detail_window import main as detail_main
                    detail_main()
                except Exception as e:
                    print(f"❌ 啟動失敗: {e}")
                    input("按任意鍵退出...")
                break
                
            elif choice == '3':
                print("\n⚙️  啟動 Telegram 設定助手...")
                try:
                    import telegram_setup_helper
                    telegram_setup_helper.main()
                except Exception as e:
                    print(f"❌ 啟動失敗: {e}")
                    input("按任意鍵退出...")
                break
                
            elif choice == '4':
                print("\n🔧 啟動原版程式...")
                try:
                    from main_gui import main as original_main
                    original_main()
                except Exception as e:
                    print(f"❌ 啟動失敗: {e}")
                    input("按任意鍵退出...")
                break
                
            elif choice == '5':
                print("\n👋 再見！")
                break
                
            else:
                print("❌ 無效選項，請輸入 1-5")
                
        except KeyboardInterrupt:
            print("\n\n👋 使用者中斷，再見！")
            break
        except Exception as e:
            print(f"❌ 發生錯誤: {e}")
            break

if __name__ == "__main__":
    main() 