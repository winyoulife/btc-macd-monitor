"""
字體配置模組
解決matplotlib中文顯示問題
"""

import matplotlib.pyplot as plt
import matplotlib
import platform
import os

def setup_chinese_font():
    """設定中文字體支援"""
    try:
        # 根據不同系統設定字體
        system = platform.system()
        
        if system == "Windows":
            # Windows系統常見中文字體
            fonts = ['Microsoft YaHei', 'SimHei', 'Microsoft JhengHei', 'DFKai-SB']
        elif system == "Darwin":  # macOS
            fonts = ['Ping Fang TC', 'Heiti TC', 'Arial Unicode MS']
        else:  # Linux
            fonts = ['DejaVu Sans', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC']
        
        # 嘗試設定字體
        font_set = False
        for font in fonts:
            try:
                plt.rcParams['font.sans-serif'] = [font]
                plt.rcParams['axes.unicode_minus'] = False
                
                # 測試字體是否可用
                fig, ax = plt.subplots(figsize=(1, 1))
                ax.text(0.5, 0.5, '測試', fontsize=12)
                plt.close(fig)
                
                print(f"成功設定字體: {font}")
                font_set = True
                break
            except Exception as e:
                continue
        
        if not font_set:
            # 如果都失敗，使用英文顯示
            print("警告: 無法設定中文字體，將使用英文顯示")
            return False
            
        return True
        
    except Exception as e:
        print(f"字體設定失敗: {e}")
        return False

def get_display_text():
    """根據字體支援情況返回顯示文字"""
    if setup_chinese_font():
        return {
            'price_trend': 'BTC/TWD 價格走勢',
            'macd_indicator': 'MACD 指標',
            'price': '價格',
            'macd': 'MACD',
            'signal': 'Signal',
            'histogram': 'Histogram',
            'overbought': '超買(70)',
            'oversold': '超賣(30)'
        }
    else:
        return {
            'price_trend': 'BTC/TWD Price Trend',
            'macd_indicator': 'MACD Indicator',
            'price': 'Price',
            'macd': 'MACD',
            'signal': 'Signal',
            'histogram': 'Histogram',
            'overbought': 'Overbought(70)',
            'oversold': 'Oversold(30)'
        }

# 初始化字體設定
DISPLAY_TEXT = get_display_text() 