"""
專業版字體配置模組
解決matplotlib中文顯示問題，提供專業界面字體支援
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib
import platform
import os
import tkinter as tk
from tkinter import font

class ProfessionalFontManager:
    def __init__(self):
        self.system = platform.system()
        self.chinese_font_available = False
        self.current_font = None
        self.setup_fonts()
    
    def get_available_fonts(self):
        """獲取系統可用字體"""
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        return available_fonts
    
    def setup_fonts(self):
        """設定專業字體配置"""
        try:
            # 定義各系統的專業字體優先順序
            if self.system == "Windows":
                chinese_fonts = [
                    'Microsoft YaHei UI',  # 微軟雅黑UI (最佳)
                    'Microsoft YaHei',     # 微軟雅黑
                    'Microsoft JhengHei UI',  # 微軟正黑體UI
                    'Microsoft JhengHei',     # 微軟正黑體
                    'SimHei',              # 黑體
                    'SimSun',              # 宋體
                    'KaiTi'                # 楷體
                ]
                english_fonts = [
                    'Segoe UI',
                    'Calibri',
                    'Arial',
                    'Tahoma'
                ]
            elif self.system == "Darwin":  # macOS
                chinese_fonts = [
                    'PingFang SC',         # 蘋方-簡
                    'Heiti SC',            # 黑體-簡
                    'STHeiti',             # 華文黑體
                    'Arial Unicode MS'
                ]
                english_fonts = [
                    'SF Pro Display',
                    'Helvetica Neue',
                    'Arial',
                    'System Font'
                ]
            else:  # Linux
                chinese_fonts = [
                    'Noto Sans CJK SC',
                    'WenQuanYi Micro Hei',
                    'DejaVu Sans',
                    'Ubuntu'
                ]
                english_fonts = [
                    'Ubuntu',
                    'DejaVu Sans',
                    'Liberation Sans',
                    'Arial'
                ]
            
            available_fonts = self.get_available_fonts()
            
            # 嘗試設定中文字體
            for font_name in chinese_fonts:
                if font_name in available_fonts:
                    try:
                        plt.rcParams['font.sans-serif'] = [font_name] + english_fonts
                        plt.rcParams['axes.unicode_minus'] = False
                        
                        # 測試中文顯示
                        fig, ax = plt.subplots(figsize=(2, 1))
                        ax.text(0.5, 0.5, '測試中文顯示', ha='center', va='center')
                        plt.close(fig)
                        
                        self.current_font = font_name
                        self.chinese_font_available = True
                        print(f"✅ 成功設定專業中文字體: {font_name}")
                        break
                    except Exception as e:
                        continue
            
            if not self.chinese_font_available:
                # 設定英文字體
                for font_name in english_fonts:
                    if font_name in available_fonts:
                        plt.rcParams['font.sans-serif'] = [font_name]
                        plt.rcParams['axes.unicode_minus'] = False
                        self.current_font = font_name
                        print(f"⚠️ 使用英文字體: {font_name}")
                        break
            
            # 設定其他matplotlib參數
            self.setup_matplotlib_style()
            
        except Exception as e:
            print(f"❌ 字體設定失敗: {e}")
            self.fallback_font_setup()
    
    def setup_matplotlib_style(self):
        """設定專業matplotlib樣式"""
        # 設定專業樣式
        plt.style.use('default')
        
        # 確保使用Unicode字體
        if self.chinese_font_available and self.current_font:
            # 設定matplotlib使用支援Unicode的字體
            plt.rcParams['font.sans-serif'] = [self.current_font, 'Arial Unicode MS', 'DejaVu Sans']
            plt.rcParams['font.family'] = 'sans-serif'
        else:
            # 備用設定
            plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans', 'Arial', 'sans-serif']
            plt.rcParams['font.family'] = 'sans-serif'
        
        plt.rcParams['axes.unicode_minus'] = False
        
        # 字體設定
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['axes.labelsize'] = 10
        plt.rcParams['xtick.labelsize'] = 9
        plt.rcParams['ytick.labelsize'] = 9
        plt.rcParams['legend.fontsize'] = 9
        plt.rcParams['figure.titlesize'] = 14
        
        # 顏色和樣式
        plt.rcParams['axes.facecolor'] = '#fafafa'
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['axes.edgecolor'] = '#cccccc'
        plt.rcParams['axes.linewidth'] = 0.8
        plt.rcParams['grid.color'] = '#e0e0e0'
        plt.rcParams['grid.linewidth'] = 0.5
        plt.rcParams['grid.alpha'] = 0.7
        
        # 線條樣式
        plt.rcParams['lines.linewidth'] = 1.5
        plt.rcParams['lines.markersize'] = 4
        
        # 圖例樣式
        plt.rcParams['legend.frameon'] = True
        plt.rcParams['legend.fancybox'] = True
        plt.rcParams['legend.shadow'] = True
        plt.rcParams['legend.framealpha'] = 0.9
        
        # 確保文字渲染設定
        plt.rcParams['text.usetex'] = False  # 不使用LaTeX
        plt.rcParams['mathtext.fontset'] = 'dejavusans'  # 數學文字字體
    
    def fallback_font_setup(self):
        """備用字體設定"""
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False
        self.current_font = 'Arial'
        print("🔄 使用備用字體設定")
    
    def get_tkinter_font(self, size=10, weight='normal'):
        """獲取Tkinter字體"""
        if self.chinese_font_available and self.current_font:
            return (self.current_font, size, weight)
        else:
            # 使用系統默認字體
            if self.system == "Windows":
                return ('Segoe UI', size, weight)
            elif self.system == "Darwin":
                return ('SF Pro Display', size, weight)
            else:
                return ('Ubuntu', size, weight)

# 創建全局字體管理器
font_manager = ProfessionalFontManager()

def get_professional_text():
    """根據字體支援返回專業顯示文字"""
    # 強制使用英文以避免字體問題
    return {
        'app_title': '🚀 BTC MACD Professional Trading Signal Analysis',
        'price_trend': 'BTC/TWD Price Trend (Last 5 Days)',
        'macd_indicator': 'MACD Technical Indicator',
        'control_panel': '🎛️ Control Panel',
        'price_info': '💰 BTC/TWD Real-time Quote',
        'chart_panel': '📈 MACD Technical Analysis Chart',
        'signal_panel': '🎯 Trading Signals',
        'system_log': '📝 System Log',
        'current_price': 'Current Price',
        '24h_change': '24H Change',
        'update_time': 'Update Time',
        'signal': 'Signal',
        'strength': 'Strength',
        'reason': 'Reason',
        'start_monitor': '🚀 Start Monitor',
        'stop_monitor': '⏹️ Stop Monitor',
        'manual_update': '🔄 Manual Update',
        'macd_detail': '📊 MACD Detail',
        'settings': '⚙️ Settings',
        'status_waiting': '🟡 Waiting',
        'status_running': '🟢 Running',
        'status_stopped': '🟡 Stopped',
        'loading': 'Loading...',
        'macd': 'MACD',
        'signal_line': 'Signal',
        'histogram': 'Histogram',
        'ema12': 'EMA12',
        'ema26': 'EMA26'
    }

# 專業配色方案
PROFESSIONAL_COLORS = {
    'primary': '#2E86AB',      # 專業藍
    'secondary': '#A23B72',    # 專業紫紅
    'success': '#06D6A0',      # 成功綠
    'warning': '#F18F01',      # 警告橙
    'danger': '#C73E1D',       # 危險紅
    'info': '#6C63FF',         # 資訊藍
    'light': '#F8F9FA',        # 淺色背景
    'dark': '#212529',         # 深色文字
    'muted': '#6C757D',        # 輔助文字
    'border': '#DEE2E6',       # 邊框色
    'background': '#FFFFFF',   # 主背景
    'surface': '#F8F9FA',      # 表面色
    'chart_bg': '#FAFBFC',     # 圖表背景
    'grid': '#E9ECEF',         # 網格線
    'buy_color': '#06D6A0',    # 買入信號色
    'sell_color': '#C73E1D',   # 賣出信號色
    'hold_color': '#6C757D',   # 持有信號色
    'macd_line': '#2E86AB',    # MACD線色
    'signal_line': '#C73E1D',  # 信號線色
    'histogram_pos': '#06D6A0', # 正直方圖
    'histogram_neg': '#C73E1D'  # 負直方圖
}

# 獲取專業文字
PROFESSIONAL_TEXT = get_professional_text()

def setup_professional_style():
    """設定專業樣式"""
    return font_manager.setup_fonts()

def get_font_config():
    """獲取字體配置"""
    return {
        'current_font': font_manager.current_font,
        'chinese_available': font_manager.chinese_font_available,
        'system': font_manager.system
    } 