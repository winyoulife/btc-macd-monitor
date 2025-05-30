#!/usr/bin/env python3
"""
優化版程式測試腳本
"""

import sys
import traceback

def test_font_config():
    """測試字體配置"""
    try:
        from font_config import setup_chinese_font, DISPLAY_TEXT
        print("✅ 字體配置模組載入成功")
        setup_chinese_font()
        print("✅ 字體設定完成")
        return True
    except Exception as e:
        print(f"❌ 字體配置失敗: {e}")
        return False

def test_enhanced_analyzer():
    """測試增強版分析器"""
    try:
        from enhanced_macd_analyzer import EnhancedMACDAnalyzer
        analyzer = EnhancedMACDAnalyzer()
        print("✅ 增強版MACD分析器載入成功")
        return True
    except Exception as e:
        print(f"❌ 增強版分析器失敗: {e}")
        return False

def test_macd_window():
    """測試MACD詳細視窗"""
    try:
        import tkinter as tk
        from macd_detail_window import MACDDetailWindow
        print("✅ MACD詳細視窗模組載入成功")
        return True
    except Exception as e:
        print(f"❌ MACD詳細視窗測試失敗: {e}")
        return False

def test_main_gui():
    """測試主GUI（不實際運行）"""
    try:
        from optimized_main_gui import OptimizedBTCMACDGUI
        print("✅ 優化版主GUI模組載入成功")
        return True
    except Exception as e:
        print(f"❌ 主GUI測試失敗: {e}")
        traceback.print_exc()
        return False

def run_simple_gui():
    """運行簡化版GUI"""
    try:
        print("\n🚀 啟動簡化版GUI測試...")
        from optimized_main_gui import OptimizedBTCMACDGUI
        
        # 創建應用但不立即顯示MACD詳細視窗
        app = OptimizedBTCMACDGUI()
        print("✅ GUI創建成功，啟動主循環...")
        app.run()
        
    except Exception as e:
        print(f"❌ GUI運行失敗: {e}")
        traceback.print_exc()

def main():
    print("="*50)
    print("🧪 優化版程式模組測試")
    print("="*50)
    
    tests = [
        ("字體配置", test_font_config),
        ("增強版分析器", test_enhanced_analyzer),
        ("MACD詳細視窗", test_macd_window),
        ("主GUI模組", test_main_gui)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n🔍 測試 {name}...")
        result = test_func()
        results.append((name, result))
    
    print("\n" + "="*50)
    print("📊 測試結果摘要:")
    print("="*50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"{name:15} : {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有測試通過！")
        response = input("\n是否要啟動完整GUI？ (y/N): ")
        if response.lower() in ['y', 'yes']:
            run_simple_gui()
    else:
        print("\n⚠️  部分測試失敗，請檢查錯誤訊息")

if __name__ == "__main__":
    main() 