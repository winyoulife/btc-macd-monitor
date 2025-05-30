import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import threading
import queue
import time
import schedule
from datetime import datetime, timedelta
import logging

# 導入必要模組
from max_api import MaxAPI
from enhanced_macd_analyzer import EnhancedMACDAnalyzer
from telegram_notifier import TelegramNotifier

# 定義缺少的常量
GUI_WIDTH = 1000
GUI_HEIGHT = 500
UPDATE_INTERVAL = 1

# Telegram 設定
TELEGRAM_BOT_TOKEN = "7323086952:AAE5fkQp8n98TOYnPpj2KPyrCI6hX5R2n2I"
TELEGRAM_CHAT_ID = "8164385222"

# 其他配置常量
MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26  
MACD_SIGNAL_PERIOD = 9
BUY_THRESHOLD = 0.0001
SELL_THRESHOLD = -0.0001
SIGNAL_THRESHOLD = 50
MIN_SIGNAL_INTERVAL = 300

# 設定matplotlib避免字體問題
plt.style.use('default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['text.usetex'] = False

# 專業配色方案
ULTIMATE_COLORS = {
    'primary': '#2E86AB',        # 專業藍
    'secondary': '#A23B72',      # 專業紫紅
    'success': '#06D6A0',        # 成功綠
    'warning': '#F18F01',        # 警告橙
    'danger': '#C73E1D',         # 危險紅
    'info': '#6C63FF',           # 資訊藍
    'light': '#F8F9FA',          # 淺色背景
    'dark': '#212529',           # 深色文字
    'muted': '#6C757D',          # 輔助文字
    'border': '#DEE2E6',         # 邊框色
    'background': '#FFFFFF',     # 主背景
    'surface': '#F8F9FA',        # 表面色
    'chart_bg': '#FAFBFC',       # 圖表背景
    'grid': '#E9ECEF',           # 網格線
    'buy_color': '#06D6A0',      # 買入信號色
    'sell_color': '#C73E1D',     # 賣出信號色
    'hold_color': '#6C757D',     # 持有信號色
    'macd_line': '#2E86AB',      # MACD線色
    'signal_line': '#C73E1D',    # 信號線色
    'histogram_pos': '#06D6A0',  # 正直方圖
    'histogram_neg': '#C73E1D'   # 負直方圖
}

class UltimateProfessionalBTCMACDGUI:
    def __init__(self):
        # 創建主窗口
        self.root = tk.Tk()
        self.root.title("🚀 BTC MACD Professional Trading Signal Analysis System")
        self.root.geometry(f"{GUI_WIDTH}x{GUI_HEIGHT}")
        self.root.resizable(True, True)
        self.root.configure(bg=ULTIMATE_COLORS['background'])
        
        # 設定窗口樣式
        self.setup_window_style()
        
        # 初始化組件
        self.max_api = MaxAPI()
        self.macd_analyzer = EnhancedMACDAnalyzer()
        self.telegram_notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        
        # 數據更新隊列
        self.update_queue = queue.Queue()
        
        # 控制變量
        self.running = False
        self.update_thread = None
        self.last_signal_time = None
        self.data_df = None
        self.macd_detail_window = None
        
        # 交易信號狀態追蹤
        self.trading_state = "INITIAL"  # INITIAL, WAIT_BUY, WAIT_SELL, BUY_SIGNAL, SELL_SIGNAL
        self.previous_macd = None
        self.previous_signal = None
        self.macd_trend = "UNKNOWN"  # UP, DOWN, FLAT
        self.signal_trend = "UNKNOWN"  # UP, DOWN, FLAT
        self.trend_history = []  # 儲存最近的趨勢資料
        
        # 即時更新列表
        self.history_data = []
        self.max_history_items = 10  # 只保留最近10筆資料
        
        # 設定日誌
        self.setup_logging()
        
        # 創建專業樣式
        self.setup_professional_ttk_style()
        
        # 建立GUI
        self.setup_gui()
        
        # 設定定時任務
        self.setup_schedule()
        
        # 啟動數據處理
        self.process_queue()
    
    def setup_window_style(self):
        """設定窗口樣式"""
        try:
            self.root.minsize(1000, 700)
            # Windows特定優化
            try:
                self.root.wm_attributes('-topmost', False)
            except:
                pass
        except Exception as e:
            print(f"Window style setup failed: {e}")
    
    def setup_professional_ttk_style(self):
        """設定專業TTK樣式"""
        self.style = ttk.Style()
        
        # 使用現代主題
        available_themes = self.style.theme_names()
        if 'vista' in available_themes:
            self.style.theme_use('vista')
        elif 'clam' in available_themes:
            self.style.theme_use('clam')
        
        # 自定義樣式
        self.style.configure('Professional.TLabel',
                           background=ULTIMATE_COLORS['background'],
                           foreground=ULTIMATE_COLORS['dark'],
                           font=('Segoe UI', 10))
        
        self.style.configure('Title.TLabel',
                           background=ULTIMATE_COLORS['background'],
                           foreground=ULTIMATE_COLORS['primary'],
                           font=('Segoe UI', 14, 'bold'))
        
        self.style.configure('Price.TLabel',
                           background=ULTIMATE_COLORS['background'],
                           foreground=ULTIMATE_COLORS['primary'],
                           font=('Segoe UI', 18, 'bold'))
        
        self.style.configure('Status.TLabel',
                           background=ULTIMATE_COLORS['background'],
                           foreground=ULTIMATE_COLORS['success'],
                           font=('Segoe UI', 12, 'bold'))
        
        # 按鈕樣式
        self.style.configure('Professional.TButton',
                           font=('Segoe UI', 10),
                           padding=(10, 5))
        
        self.style.configure('Success.TButton',
                           font=('Segoe UI', 10, 'bold'),
                           padding=(15, 8))
        
        self.style.configure('Warning.TButton',
                           font=('Segoe UI', 10, 'bold'),
                           padding=(15, 8))
        
        # LabelFrame樣式
        self.style.configure('Professional.TLabelframe',
                           background=ULTIMATE_COLORS['background'],
                           borderwidth=1,
                           relief='solid')
        
        self.style.configure('Professional.TLabelframe.Label',
                           background=ULTIMATE_COLORS['background'],
                           foreground=ULTIMATE_COLORS['primary'],
                           font=('Segoe UI', 11, 'bold'))
        
        # Notebook樣式
        self.style.configure('Professional.TNotebook',
                           background=ULTIMATE_COLORS['background'],
                           borderwidth=0)
        
        self.style.configure('Professional.TNotebook.Tab',
                           background=ULTIMATE_COLORS['surface'],
                           foreground=ULTIMATE_COLORS['dark'],
                           font=('Segoe UI', 10),
                           padding=(15, 8))
    
    def setup_logging(self):
        """設定日誌"""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def setup_gui(self):
        """建立專業界面"""
        # 創建主滾動框架
        main_canvas = tk.Canvas(self.root, bg=ULTIMATE_COLORS['background'])
        main_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg=ULTIMATE_COLORS['background'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        # 修正滾動條和畫布布局 - 滾動條靠右，畫布填滿剩餘空間
        main_scrollbar.pack(side="right", fill="y")
        main_canvas.pack(side="left", fill="both", expand=True)
        
        # 主容器（現在在滾動框架內）
        main_container = tk.Frame(scrollable_frame, bg=ULTIMATE_COLORS['background'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 綁定滾輪事件
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 確保畫布內容寬度與畫布匹配
        def configure_scroll_region(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
            # 設置scrollable_frame的寬度與canvas一致
            canvas_width = event.width
            main_canvas.itemconfig(main_canvas.find_all()[0], width=canvas_width)
        
        main_canvas.bind('<Configure>', configure_scroll_region)
        
        # 標題區域
        self.create_header_section(main_container)
        
        # 控制面板
        self.create_control_panel(main_container)
        
        # 價格資訊面板
        self.create_price_panel(main_container)
        
        # MACD數值面板
        self.create_macd_values_panel(main_container)
        
        # 交易信號監控面板
        self.create_signal_monitoring_panel(main_container)
        
        # AI BTC新聞分析面板
        self.create_ai_news_panel(main_container)
        
        # 底部信息面板
        self.create_bottom_panel(main_container)
    
    def create_header_section(self, parent):
        """創建標題區域"""
        header_frame = tk.Frame(parent, bg=ULTIMATE_COLORS['background'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 主標題
        title_label = ttk.Label(header_frame, 
                               text="🚀 BTC MACD 專業交易信號分析系統",
                               style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # 狀態指示器
        status_frame = tk.Frame(header_frame, bg=ULTIMATE_COLORS['background'])
        status_frame.pack(side=tk.RIGHT)
        
        ttk.Label(status_frame, text="系統狀態:", style='Professional.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_var = tk.StringVar(value="🟡 等待中")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT)
    
    def create_control_panel(self, parent):
        """建立控制面板"""
        control_frame = ttk.LabelFrame(parent, text="🎛️ 控制面板", style='Professional.TLabelframe')
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 內部容器
        control_inner = tk.Frame(control_frame, bg=ULTIMATE_COLORS['background'])
        control_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # 左側按鈕組
        left_buttons = tk.Frame(control_inner, bg=ULTIMATE_COLORS['background'])
        left_buttons.pack(side=tk.LEFT)
        
        # 主要控制按鈕
        self.start_button = ttk.Button(left_buttons, text="🚀 開始監控",
                                      command=self.start_monitoring, style='Success.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(left_buttons, text="⏹️ 停止監控",
                                     command=self.stop_monitoring, state=tk.DISABLED, style='Warning.TButton')
        self.stop_button.pack(side=tk.LEFT, padx=(0, 20))
        
        # 功能按鈕
        ttk.Button(left_buttons, text="🔄 手動更新",
                  command=self.manual_update, style='Professional.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(left_buttons, text="📱 測試通知",
                  command=self.test_notification, style='Professional.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(left_buttons, text="⚙️ 設定",
                  command=self.show_settings, style='Professional.TButton').pack(side=tk.LEFT)
        
        # 右側實時信息
        right_info = tk.Frame(control_inner, bg=ULTIMATE_COLORS['background'])
        right_info.pack(side=tk.RIGHT)
        
        # 最後更新時間
        ttk.Label(right_info, text="更新時間:", style='Professional.TLabel').pack(anchor=tk.E)
        self.last_update_var = tk.StringVar(value="--")
        ttk.Label(right_info, textvariable=self.last_update_var, style='Professional.TLabel').pack(anchor=tk.E)
    
    def create_price_panel(self, parent):
        """建立價格面板"""
        price_frame = ttk.LabelFrame(parent, text="💰 BTC/TWD 即時報價", style='Professional.TLabelframe')
        price_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 內部網格
        price_grid = tk.Frame(price_frame, bg=ULTIMATE_COLORS['background'])
        price_grid.pack(fill=tk.X, padx=15, pady=10)
        
        # 當前價格區域
        price_section = tk.Frame(price_grid, bg=ULTIMATE_COLORS['background'])
        price_section.pack(side=tk.LEFT)
        
        ttk.Label(price_section, text="當前價格:", style='Professional.TLabel').pack(anchor=tk.W)
        
        self.current_price_var = tk.StringVar(value="載入中...")
        price_label = ttk.Label(price_section, textvariable=self.current_price_var, style='Price.TLabel')
        price_label.pack(anchor=tk.W)
        
        # 變化幅度區域
        change_section = tk.Frame(price_grid, bg=ULTIMATE_COLORS['background'])
        change_section.pack(side=tk.LEFT, padx=(50, 0))
        
        ttk.Label(change_section, text="24H變化:", style='Professional.TLabel').pack(anchor=tk.W)
        
        self.price_change_var = tk.StringVar(value="--")
        self.price_change_label = ttk.Label(change_section, textvariable=self.price_change_var,
                                           style='Professional.TLabel')
        self.price_change_label.pack(anchor=tk.W)
        
        # 信號狀態區域
        signal_section = tk.Frame(price_grid, bg=ULTIMATE_COLORS['background'])
        signal_section.pack(side=tk.RIGHT)
        
        ttk.Label(signal_section, text="信號:", style='Professional.TLabel').pack(anchor=tk.E)
        
        # 當前信號顯示
        signal_display = tk.Frame(signal_section, bg=ULTIMATE_COLORS['background'])
        signal_display.pack(anchor=tk.E)
        
        self.signal_var = tk.StringVar(value="HOLD")
        self.signal_label = ttk.Label(signal_display, textvariable=self.signal_var, style='Status.TLabel')
        self.signal_label.pack(side=tk.LEFT)
        
        self.strength_var = tk.StringVar(value="0%")
        ttk.Label(signal_display, textvariable=self.strength_var,
                 style='Professional.TLabel').pack(side=tk.LEFT, padx=(10, 0))
    
    def create_macd_values_panel(self, parent):
        """建立MACD數值面板"""
        macd_values_frame = ttk.LabelFrame(parent, text="📊 MACD 即時數值", style='Professional.TLabelframe')
        macd_values_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 內部網格
        macd_values_grid = tk.Frame(macd_values_frame, bg=ULTIMATE_COLORS['background'])
        macd_values_grid.pack(fill=tk.X, padx=15, pady=10)
        
        # MACD值
        macd_section = tk.Frame(macd_values_grid, bg=ULTIMATE_COLORS['background'])
        macd_section.pack(side=tk.LEFT)
        
        ttk.Label(macd_section, text="MACD值:", style='Professional.TLabel').pack(anchor=tk.W)
        self.current_macd_var = tk.StringVar(value="載入中...")
        ttk.Label(macd_section, textvariable=self.current_macd_var, 
                 style='Professional.TLabel', font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W)
        
        # 信號線值
        signal_section = tk.Frame(macd_values_grid, bg=ULTIMATE_COLORS['background'])
        signal_section.pack(side=tk.LEFT, padx=(40, 0))
        
        ttk.Label(signal_section, text="信號線:", style='Professional.TLabel').pack(anchor=tk.W)
        self.current_signal_var = tk.StringVar(value="--")
        ttk.Label(signal_section, textvariable=self.current_signal_var,
                 style='Professional.TLabel', font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W)
        
        # 柱狀體值
        histogram_section = tk.Frame(macd_values_grid, bg=ULTIMATE_COLORS['background'])
        histogram_section.pack(side=tk.LEFT, padx=(40, 0))
        
        ttk.Label(histogram_section, text="柱狀體:", style='Professional.TLabel').pack(anchor=tk.W)
        self.current_histogram_var = tk.StringVar(value="--")
        ttk.Label(histogram_section, textvariable=self.current_histogram_var,
                 style='Professional.TLabel', font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W)
        
        # 最後更新時間
        update_time_section = tk.Frame(macd_values_grid, bg=ULTIMATE_COLORS['background'])
        update_time_section.pack(side=tk.RIGHT)
        
        ttk.Label(update_time_section, text="最後更新:", style='Professional.TLabel').pack(anchor=tk.E)
        self.macd_update_time_var = tk.StringVar(value="--")
        ttk.Label(update_time_section, textvariable=self.macd_update_time_var,
                 style='Professional.TLabel', font=('Segoe UI', 9)).pack(anchor=tk.E)
    
    def create_signal_monitoring_panel(self, parent):
        """建立交易信號監控面板"""
        signal_monitor_frame = ttk.LabelFrame(parent, text="🎯 智能交易信號監控", style='Professional.TLabelframe')
        signal_monitor_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 內部網格
        signal_monitor_grid = tk.Frame(signal_monitor_frame, bg=ULTIMATE_COLORS['background'])
        signal_monitor_grid.pack(fill=tk.X, padx=15, pady=10)
        
        # 當前交易狀態
        status_section = tk.Frame(signal_monitor_grid, bg=ULTIMATE_COLORS['background'])
        status_section.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(status_section, text="📊 當前交易狀態:", style='Professional.TLabel', 
                 font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT)
        
        # 信號燈
        self.signal_light = tk.Label(status_section, text="●", font=('Segoe UI', 20), 
                                   fg="#FFA500", bg=ULTIMATE_COLORS['background'])  # 預設黃色
        self.signal_light.pack(side=tk.LEFT, padx=(10, 5))
        
        self.trading_status_var = tk.StringVar(value="🔄 系統初始化中...")
        self.trading_status_label = ttk.Label(status_section, textvariable=self.trading_status_var,
                                            style='Professional.TLabel', font=('Segoe UI', 11, 'bold'))
        self.trading_status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # 分隔線
        separator = tk.Frame(signal_monitor_grid, height=1, bg=ULTIMATE_COLORS['border'])
        separator.pack(fill=tk.X, pady=10)
        
        # 買進監控區域
        buy_section = tk.Frame(signal_monitor_grid, bg=ULTIMATE_COLORS['background'])
        buy_section.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(buy_section, text="🚀 買進條件分析:", style='Professional.TLabel', 
                 font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
        
        self.buy_condition_var = tk.StringVar(value="分析中...")
        self.buy_condition_label = ttk.Label(buy_section, textvariable=self.buy_condition_var,
                                           style='Professional.TLabel', wraplength=350)
        self.buy_condition_label.pack(anchor=tk.W, pady=(5, 0))
        
        # 賣出監控區域
        sell_section = tk.Frame(signal_monitor_grid, bg=ULTIMATE_COLORS['background'])
        sell_section.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        ttk.Label(sell_section, text="📉 賣出條件分析:", style='Professional.TLabel',
                 font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
        
        self.sell_condition_var = tk.StringVar(value="分析中...")
        self.sell_condition_label = ttk.Label(sell_section, textvariable=self.sell_condition_var,
                                            style='Professional.TLabel', wraplength=350)
        self.sell_condition_label.pack(anchor=tk.W, pady=(5, 0))
        
        # 啟動信號燈閃爍效果
        self.start_signal_light_animation()
    
    def start_signal_light_animation(self):
        """啟動信號燈閃爍動畫"""
        def animate():
            if self.trading_state in ["WAIT_BUY", "WAIT_SELL"]:
                # 黃燈閃爍
                current_color = self.signal_light.cget("fg")
                new_color = "#FFA500" if current_color == "#FFD700" else "#FFD700"
                self.signal_light.config(fg=new_color)
            
            # 每500毫秒更新一次
            self.root.after(500, animate)
        
        animate()
    
    def analyze_trend(self, current_macd, current_signal):
        """分析MACD和信號線的趨勢"""
        if self.previous_macd is not None and self.previous_signal is not None:
            # 計算趨勢
            macd_diff = current_macd - self.previous_macd
            signal_diff = current_signal - self.previous_signal
            
            # 更新趨勢
            if abs(macd_diff) > 50:  # 設定一個閾值避免小幅波動
                self.macd_trend = "UP" if macd_diff > 0 else "DOWN"
            
            if abs(signal_diff) > 50:
                self.signal_trend = "UP" if signal_diff > 0 else "DOWN"
            
            # 記錄歷史
            trend_data = {
                'timestamp': datetime.now(),
                'macd': current_macd,
                'signal': current_signal,
                'macd_trend': self.macd_trend,
                'signal_trend': self.signal_trend,
                'cross_state': "MACD_ABOVE" if current_macd > current_signal else "SIGNAL_ABOVE"
            }
            
            self.trend_history.append(trend_data)
            
            # 保留最近20個資料點
            if len(self.trend_history) > 20:
                self.trend_history = self.trend_history[-20:]
        
        # 更新前一個值
        self.previous_macd = current_macd
        self.previous_signal = current_signal
    
    def determine_trading_state(self, current_macd, current_signal):
        """判斷交易狀態"""
        if len(self.trend_history) < 3:
            return "INITIAL"
        
        recent_trends = self.trend_history[-3:]
        
        # 檢查交叉情況
        macd_above_signal = current_macd > current_signal
        previous_cross_state = recent_trends[-2]['cross_state'] if len(recent_trends) >= 2 else None
        current_cross_state = "MACD_ABOVE" if macd_above_signal else "SIGNAL_ABOVE"
        
        # 檢測金叉（MACD突破信號線向上）
        if (previous_cross_state == "SIGNAL_ABOVE" and current_cross_state == "MACD_ABOVE" and 
            self.macd_trend == "DOWN" and self.signal_trend == "DOWN"):
            return "BUY_SIGNAL"
        
        # 檢測死叉（MACD跌破信號線向下）
        if (previous_cross_state == "MACD_ABOVE" and current_cross_state == "SIGNAL_ABOVE" and 
            self.macd_trend == "UP" and self.signal_trend == "UP"):
            return "SELL_SIGNAL"
        
        # 等待買進條件：雙線下降且MACD < 信號線
        if (self.macd_trend == "DOWN" and self.signal_trend == "DOWN" and 
            current_macd < current_signal):
            return "WAIT_BUY"
        
        # 等待賣出條件：雙線上升且MACD > 信號線
        if (self.macd_trend == "UP" and self.signal_trend == "UP" and 
            current_macd > current_signal):
            return "WAIT_SELL"
        
        return "HOLD"
    
    def update_signal_monitoring(self, macd_val, signal_val, signal_data):
        """更新交易信號監控"""
        try:
            # 分析趨勢
            self.analyze_trend(macd_val, signal_val)
            
            # 判斷交易狀態
            new_state = self.determine_trading_state(macd_val, signal_val)
            
            # 更新狀態
            if new_state != self.trading_state:
                self.trading_state = new_state
                self.log_message(f"🔄 交易狀態變更: {new_state}")
            
            # 更新視覺顯示
            self.update_signal_display_advanced(macd_val, signal_val)
            
        except Exception as e:
            self.logger.error(f"Signal monitoring update error: {e}")
    
    def update_signal_display_advanced(self, macd_val, signal_val):
        """更新進階信號顯示"""
        try:
            # 根據交易狀態更新信號燈和文字
            if self.trading_state == "BUY_SIGNAL":
                self.signal_light.config(fg="#06D6A0")  # 綠燈
                self.trading_status_var.set("🚀 強烈買進訊號！")
                self.trading_status_label.configure(foreground=ULTIMATE_COLORS['buy_color'])
                
            elif self.trading_state == "SELL_SIGNAL":
                self.signal_light.config(fg="#C73E1D")  # 紅燈
                self.trading_status_var.set("📉 強烈賣出訊號！")
                self.trading_status_label.configure(foreground=ULTIMATE_COLORS['sell_color'])
                
            elif self.trading_state == "WAIT_BUY":
                # 黃燈閃爍在動畫函數中處理
                self.trading_status_var.set("⏳ 等待買進時機...")
                self.trading_status_label.configure(foreground="#FFA500")
                
            elif self.trading_state == "WAIT_SELL":
                # 黃燈閃爍在動畫函數中處理
                self.trading_status_var.set("⏳ 等待賣出時機...")
                self.trading_status_label.configure(foreground="#FFA500")
                
            else:
                self.signal_light.config(fg="#6C757D")  # 灰燈
                self.trading_status_var.set("⚪ 觀察中...")
                self.trading_status_label.configure(foreground=ULTIMATE_COLORS['muted'])
            
            # 更新買進條件分析
            buy_analysis = self.get_buy_condition_analysis(macd_val, signal_val)
            self.buy_condition_var.set(buy_analysis)
            
            # 更新賣出條件分析
            sell_analysis = self.get_sell_condition_analysis(macd_val, signal_val)
            self.sell_condition_var.set(sell_analysis)
            
        except Exception as e:
            self.logger.error(f"Advanced signal display update error: {e}")
    
    def get_buy_condition_analysis(self, macd_val, signal_val):
        """獲取買進條件分析"""
        analysis = []
        
        # MACD位置分析
        if macd_val < signal_val:
            analysis.append("✅ MACD低於信號線")
        else:
            analysis.append("❌ MACD高於信號線")
        
        # 趨勢分析 - 根據實際趨勢顯示
        if self.macd_trend == "DOWN" and self.signal_trend == "DOWN":
            analysis.append("✅ 雙線往下趨勢")
        elif self.macd_trend == "UP" and self.signal_trend == "UP":
            analysis.append("⚠️ 雙線往上趨勢")
        elif self.macd_trend == "UNKNOWN" or self.signal_trend == "UNKNOWN":
            analysis.append("🔄 趨勢分析中...")
        else:
            analysis.append(f"📊 混合趨勢: MACD{self.macd_trend}, 信號線{self.signal_trend}")
        
        # 交叉潛力
        if len(self.trend_history) >= 2:
            macd_change = self.trend_history[-1]['macd'] - self.trend_history[-2]['macd']
            if macd_change > 0 and macd_val < signal_val:
                analysis.append("🔄 MACD開始反彈")
            elif macd_change < 0:
                analysis.append("📉 MACD持續下跌")
        
        return " | ".join(analysis)
    
    def get_sell_condition_analysis(self, macd_val, signal_val):
        """獲取賣出條件分析"""
        analysis = []
        
        # MACD位置分析 - 修正邏輯
        if macd_val > signal_val:
            analysis.append("✅ MACD高於信號線")
        else:
            analysis.append("❌ MACD低於信號線")
        
        # 趨勢分析 - 根據實際趨勢顯示
        if self.macd_trend == "UP" and self.signal_trend == "UP":
            analysis.append("✅ 雙線往上趨勢")
        elif self.macd_trend == "DOWN" and self.signal_trend == "DOWN":
            analysis.append("⚠️ 雙線往下趨勢")
        elif self.macd_trend == "UNKNOWN" or self.signal_trend == "UNKNOWN":
            analysis.append("🔄 趨勢分析中...")
        else:
            analysis.append(f"📊 混合趨勢: MACD{self.macd_trend}, 信號線{self.signal_trend}")
        
        # 交叉潛力
        if len(self.trend_history) >= 2:
            macd_change = self.trend_history[-1]['macd'] - self.trend_history[-2]['macd']
            if macd_change < 0 and macd_val > signal_val:
                analysis.append("🔄 MACD開始回調")
            elif macd_change > 0:
                analysis.append("📈 MACD持續上漲")
        
        return " | ".join(analysis)
    
    def create_ai_news_panel(self, parent):
        """建立AI BTC新聞分析面板"""
        ai_news_frame = ttk.LabelFrame(parent, text="🤖 AI BTC 近24小時重大漲跌分析", style='Professional.TLabelframe')
        ai_news_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 內部容器（移除按鈕區域）
        ai_news_container = tk.Frame(ai_news_frame, bg=ULTIMATE_COLORS['background'])
        ai_news_container.pack(fill=tk.X, padx=15, pady=10)
        
        # AI分析文本區域
        self.ai_analysis_text = tk.Text(ai_news_container, height=4, wrap=tk.WORD,
                                       font=('Microsoft YaHei', 9),
                                       bg=ULTIMATE_COLORS['surface'],
                                       fg=ULTIMATE_COLORS['dark'],
                                       selectbackground=ULTIMATE_COLORS['primary'],
                                       selectforeground='white',
                                       borderwidth=1,
                                       relief='solid')
        
        ai_scrollbar = ttk.Scrollbar(ai_news_container, orient=tk.VERTICAL, command=self.ai_analysis_text.yview)
        self.ai_analysis_text.configure(yscrollcommand=ai_scrollbar.set)
        
        self.ai_analysis_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ai_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 初始化AI分析
        self.ai_analysis_text.insert(tk.END, "🔄 正在獲取BTC最新新聞並進行AI分析...")
        
        # 啟動新聞分析線程
        threading.Thread(target=self.update_ai_analysis, daemon=True).start()
    
    def create_bottom_panel(self, parent):
        """建立底部面板"""
        notebook = ttk.Notebook(parent, style='Professional.TNotebook')
        notebook.pack(fill=tk.X, pady=(0, 10))
        
        # 交易信號頁面
        signal_frame = tk.Frame(notebook, bg=ULTIMATE_COLORS['background'])
        notebook.add(signal_frame, text="🎯 交易信號")
        
        self.create_signal_panel(signal_frame)
        
        # 系統日誌頁面
        log_frame = tk.Frame(notebook, bg=ULTIMATE_COLORS['background'])
        notebook.add(log_frame, text="📝 系統日誌")
        
        self.create_log_panel(log_frame)
    
    def create_signal_panel(self, parent):
        """創建信號面板"""
        signal_container = tk.Frame(parent, bg=ULTIMATE_COLORS['background'])
        signal_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 信號詳情網格
        signal_grid = tk.Frame(signal_container, bg=ULTIMATE_COLORS['background'])
        signal_grid.pack(fill=tk.X)
        
        # 信號類型
        ttk.Label(signal_grid, text="信號:", style='Professional.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 15))
        
        self.signal_display_var = tk.StringVar(value="⏸️ HOLD")
        self.signal_display_label = ttk.Label(signal_grid, textvariable=self.signal_display_var, style='Status.TLabel')
        self.signal_display_label.grid(row=0, column=1, sticky=tk.W, padx=15)
        
        # 信號強度
        ttk.Label(signal_grid, text="強度:", style='Professional.TLabel').grid(row=0, column=2, sticky=tk.W, padx=(30, 15))
        
        self.strength_display_var = tk.StringVar(value="0%")
        ttk.Label(signal_grid, textvariable=self.strength_display_var,
                 style='Professional.TLabel').grid(row=0, column=3, sticky=tk.W, padx=15)
        
        # 信號原因
        ttk.Label(signal_grid, text="原因:", style='Professional.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        self.reason_var = tk.StringVar(value="--")
        ttk.Label(signal_grid, textvariable=self.reason_var,
                 style='Professional.TLabel').grid(row=1, column=1, columnspan=3,
                                                  sticky=tk.W, padx=15, pady=(10, 0))
    
    def create_log_panel(self, parent):
        """創建日誌面板"""
        log_container = tk.Frame(parent, bg=ULTIMATE_COLORS['background'])
        log_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 日誌文本框
        log_text_frame = tk.Frame(log_container, bg=ULTIMATE_COLORS['background'])
        log_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_text_frame, height=6, wrap=tk.WORD,
                               font=('Consolas', 9),
                               bg=ULTIMATE_COLORS['surface'],
                               fg=ULTIMATE_COLORS['dark'],
                               selectbackground=ULTIMATE_COLORS['primary'],
                               selectforeground='white',
                               borderwidth=1,
                               relief='solid')
        
        log_scrollbar = ttk.Scrollbar(log_text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_schedule(self):
        """設定定時任務"""
        schedule.every().hour.at(":00").do(self.hourly_record)
    
    def start_monitoring(self):
        """啟動監控"""
        if not self.running:
            self.running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_var.set("🟢 監控中")
            
            # 更新狀態標籤顏色
            self.style.configure('Status.TLabel', foreground=ULTIMATE_COLORS['success'])
            
            # 啟動更新線程
            self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
            self.update_thread.start()
            
            self.log_message("🚀 系統啟動，開始監控 BTC/TWD MACD 信號...")
    
    def stop_monitoring(self):
        """停止監控"""
        if self.running:
            self.running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_var.set("🟡 已停止")
            
            # 更新狀態標籤顏色
            self.style.configure('Status.TLabel', foreground=ULTIMATE_COLORS['warning'])
            
            self.log_message("⏹️ 監控已停止")
    
    def manual_update(self):
        """手動更新"""
        if not self.running:
            self.log_message("🔄 執行手動更新...")
            threading.Thread(target=self.fetch_and_analyze, daemon=True).start()
    
    def test_notification(self):
        """測試通知"""
        try:
            test_message = f"""🧪 BTC MACD 系統測試通知

📅 時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🤖 系統: BTC MACD 專業交易信號分析系統
✅ 通知功能正常運作

這是一則測試通知，確認Telegram通知功能正常。"""
            
            # 使用簡單的發送方法
            success = self.telegram_notifier.send_message(test_message)
            if success:
                self.log_message("📱 測試通知發送成功！")
                messagebox.showinfo("通知測試", "✅ Telegram測試通知發送成功！")
            else:
                self.log_message("❌ 測試通知發送失敗")
                messagebox.showerror("通知測試", "❌ Telegram測試通知發送失敗，請檢查設定")
        except Exception as e:
            self.logger.error(f"Test notification error: {e}")
            self.log_message(f"❌ 測試通知錯誤: {str(e)}")
            messagebox.showerror("通知測試", f"❌ 測試通知失敗: {str(e)}")
    
    def show_settings(self):
        """顯示設置視窗"""
        messagebox.showinfo("設定", "⚙️ 專業設定功能開發中...")
    
    def update_loop(self):
        """數據更新循環"""
        while self.running:
            try:
                self.fetch_and_analyze()
                schedule.run_pending()
                time.sleep(UPDATE_INTERVAL)
            except Exception as e:
                self.logger.error(f"Update loop error: {e}")
                time.sleep(5)
    
    def fetch_and_analyze(self):
        """獲取數據並分析"""
        try:
            # 使用60分鐘線數據（1小時週期）
            kline_data = self.max_api.get_klines('btctwd', period=60, limit=500)
            
            if kline_data is None or len(kline_data) == 0:
                self.log_message("⚠️ 無法獲取K線數據")
                return
            
            # 計算MACD
            df_with_macd = self.macd_analyzer.calculate_macd(kline_data)
            
            if df_with_macd is None:
                self.log_message("⚠️ MACD計算失敗")
                return
            
            self.data_df = df_with_macd
            
            # 獲取當前價格
            current_price = self.get_current_price()
            
            # 分析交易信號
            signal_data = self.macd_analyzer.analyze_enhanced_signal(df_with_macd, current_price)
            
            # 更新GUI
            self.update_queue.put(('price_data', current_price))
            self.update_queue.put(('signal_data', signal_data))
            
            # 檢查通知
            self.check_and_send_notification(signal_data)
            
        except Exception as e:
            self.logger.error(f"Data fetch and analysis error: {e}")
            self.log_message(f"❌ 數據更新失敗: {str(e)}")
    
    def get_current_price(self):
        """獲取當前價格"""
        try:
            ticker = self.max_api.get_ticker('btctwd')
            if ticker:
                return ticker['price']
        except Exception as e:
            self.logger.error(f"Failed to get price: {e}")
        return 0
    
    def check_and_send_notification(self, signal_data):
        """檢查並發送通知"""
        try:
            # 基於新的交易狀態發送通知
            if self.trading_state in ['BUY_SIGNAL', 'SELL_SIGNAL']:
                current_time = datetime.now()
                
                # 檢查通知間隔（防止頻繁通知）
                if (self.last_signal_time is None or 
                    (current_time - self.last_signal_time).seconds > 300):  # 5分鐘間隔
                    
                    # 準備通知消息
                    if self.trading_state == 'BUY_SIGNAL':
                        message = self.prepare_buy_notification_message()
                    elif self.trading_state == 'SELL_SIGNAL':
                        message = self.prepare_sell_notification_message()
                    
                    # 發送通知
                    success = self.telegram_notifier.send_message(message)
                    
                    if success:
                        self.last_signal_time = current_time
                        self.log_message(f"📤 已發送 {self.trading_state} 通知")
                    else:
                        self.log_message(f"❌ {self.trading_state} 通知發送失敗")
                    
        except Exception as e:
            self.logger.error(f"Notification error: {e}")
    
    def prepare_buy_notification_message(self):
        """準備買進通知消息"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        current_price = self.current_price_var.get()
        macd_val = self.current_macd_var.get()
        signal_val = self.current_signal_var.get()
        
        message = f"""🚀 【BTC強烈買進訊號】
        
📅 時間: {current_time}
💰 當前價格: {current_price}
📊 MACD狀況:
   • MACD值: {macd_val}
   • 信號線: {signal_val}
   • 狀態: MACD突破信號線向上
   
🎯 信號分析:
   • 雙線下降後出現金叉
   • MACD從低位反彈突破信號線
   • 建議考慮買進時機
   
⚠️ 風險提醒: 請結合其他指標綜合判斷"""
        
        return message
    
    def prepare_sell_notification_message(self):
        """準備賣出通知消息"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        current_price = self.current_price_var.get()
        macd_val = self.current_macd_var.get()
        signal_val = self.current_signal_var.get()
        
        message = f"""📉 【BTC強烈賣出訊號】
        
📅 時間: {current_time}
💰 當前價格: {current_price}
📊 MACD狀況:
   • MACD值: {macd_val}
   • 信號線: {signal_val}
   • 狀態: MACD跌破信號線向下
   
🎯 信號分析:
   • 雙線上升後出現死叉
   • MACD從高位回調跌破信號線
   • 建議考慮賣出時機
   
⚠️ 風險提醒: 請結合其他指標綜合判斷"""
        
        return message
    
    def hourly_record(self):
        """整點記錄"""
        try:
            if self.data_df is not None:
                success = self.macd_analyzer.record_hourly_data(self.data_df, 10)
                if success:
                    self.log_message("✅ 已完成整點MACD數據記錄")
        except Exception as e:
            self.logger.error(f"Hourly record error: {e}")
    
    def process_queue(self):
        """處理更新隊列"""
        try:
            while True:
                try:
                    item = self.update_queue.get_nowait()
                    data_type, data = item
                    
                    if data_type == 'price_data':
                        self.update_price_display(data)
                    elif data_type == 'signal_data':
                        self.update_signal_display(data)
                        
                except queue.Empty:
                    break
                    
        except Exception as e:
            self.logger.error(f"Queue processing error: {e}")
        
        self.root.after(100, self.process_queue)
    
    def update_price_display(self, current_price):
        """更新價格顯示"""
        try:
            self.current_price_var.set(f"${current_price:,.0f} TWD")
            self.last_update_var.set(datetime.now().strftime('%H:%M:%S'))
            self.price_change_var.set("--")
        except Exception as e:
            self.logger.error(f"Price display update error: {e}")
    
    def update_signal_display(self, signal_data):
        """更新信號顯示"""
        try:
            signal_type = signal_data.get('signal', 'HOLD')
            strength = signal_data.get('strength', 0)
            reason = signal_data.get('reason', '--')
            
            # 更新信號顯示
            if signal_type == 'BUY':
                self.signal_var.set("🚀 BUY")
                self.signal_display_var.set("🚀 BUY")
                self.style.configure('Status.TLabel', foreground=ULTIMATE_COLORS['buy_color'])
            elif signal_type == 'SELL':
                self.signal_var.set("📉 SELL")
                self.signal_display_var.set("📉 SELL")
                self.style.configure('Status.TLabel', foreground=ULTIMATE_COLORS['sell_color'])
            else:
                self.signal_var.set("⏸️ HOLD")
                self.signal_display_var.set("⏸️ HOLD")
                self.style.configure('Status.TLabel', foreground=ULTIMATE_COLORS['hold_color'])
            
            self.strength_var.set(f"{strength}%")
            self.strength_display_var.set(f"{strength}%")
            self.reason_var.set(reason)
            
            # 更新MACD數值顯示
            if self.data_df is not None and len(self.data_df) > 0:
                latest_data = self.data_df.iloc[-1]
                macd_val = latest_data.get('macd', 0)
                signal_val = latest_data.get('macd_signal', 0)
                histogram_val = latest_data.get('macd_histogram', 0)
                
                # 更新顯示值
                self.current_macd_var.set(f"{macd_val:.1f}")
                self.current_signal_var.set(f"{signal_val:.1f}")
                self.current_histogram_var.set(f"{histogram_val:.1f}")
                
                # 更新時間
                current_time = datetime.now()
                self.macd_update_time_var.set(current_time.strftime('%H:%M:%S'))
                
                # 更新交易信號監控
                self.update_signal_monitoring(macd_val, signal_val, signal_data)
                    
        except Exception as e:
            self.logger.error(f"Signal display update error: {e}")
    
    def update_ai_analysis(self):
        """更新AI新聞分析 - 定期執行"""
        import time
        
        while True:
            try:
                # 獲取BTC相關新聞
                self.root.after(0, lambda: self.update_ai_text("🔄 正在獲取最新BTC新聞資料..."))
                
                news_data = self.fetch_btc_news()
                
                if news_data:
                    # 使用AI分析新聞
                    analysis = self.analyze_news_with_ai(news_data)
                    
                    # 添加下次更新時間
                    next_update = datetime.now() + timedelta(minutes=30)
                    analysis += f"\n\n⏰ 下次分析更新：{next_update.strftime('%H:%M')}"
                    
                    # 更新GUI
                    self.root.after(0, lambda: self.update_ai_text(analysis))
                    self.log_message("✅ AI新聞分析已更新")
                else:
                    fallback_analysis = "📰 目前無法獲取即時新聞，請稍後再試。"
                    next_update = datetime.now() + timedelta(minutes=30)
                    fallback_analysis += f"\n\n⏰ 下次分析更新：{next_update.strftime('%H:%M')}"
                    self.root.after(0, lambda: self.update_ai_text(fallback_analysis))
                
                # 等待30分鐘再次更新
                time.sleep(30 * 60)  # 30分鐘 = 1800秒
                
            except Exception as e:
                self.logger.error(f"AI analysis update error: {e}")
                error_msg = f"❌ AI分析錯誤: {str(e)}"
                next_update = datetime.now() + timedelta(minutes=30)
                error_msg += f"\n\n⏰ 下次分析更新：{next_update.strftime('%H:%M')}"
                self.root.after(0, lambda: self.update_ai_text(error_msg))
                
                # 出錯時等待5分鐘再試
                time.sleep(5 * 60)
    
    def fetch_btc_news(self):
        """獲取BTC新聞"""
        try:
            import requests
            from datetime import datetime, timedelta
            
            # 嘗試多個新聞源
            news_sources = [
                {
                    'name': 'CryptoPanic',
                    'url': 'https://cryptopanic.com/api/v1/posts/',
                    'params': {'auth_token': 'free', 'currencies': 'BTC', 'filter': 'hot'}
                },
                {
                    'name': 'CoinDesk RSS',
                    'url': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
                    'type': 'rss'
                }
            ]
            
            for source in news_sources:
                try:
                    if source.get('type') == 'rss':
                        # 處理RSS源
                        news_data = self.fetch_rss_news(source['url'])
                        if news_data:
                            return news_data
                    else:
                        # 處理API源
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                        response = requests.get(source['url'], 
                                              params=source.get('params', {}), 
                                              headers=headers, 
                                              timeout=10)
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            if source['name'] == 'CryptoPanic':
                                news_data = self.parse_cryptopanic_data(data)
                                if news_data:
                                    return news_data
                
                except Exception as e:
                    self.logger.warning(f"Failed to fetch from {source['name']}: {e}")
                    continue
            
            # 如果所有源都失敗，返回模擬數據
            return self.get_fallback_analysis()
            
        except Exception as e:
            self.logger.error(f"Fetch news error: {e}")
            return self.get_fallback_analysis()
    
    def fetch_rss_news(self, url):
        """獲取RSS新聞"""
        try:
            import requests
            import xml.etree.ElementTree as ET
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                news_items = []
                for item in root.findall('.//item')[:10]:
                    title_elem = item.find('title')
                    desc_elem = item.find('description')
                    link_elem = item.find('link')
                    
                    if title_elem is not None:
                        title = title_elem.text or ''
                        if any(keyword in title.lower() for keyword in ['bitcoin', 'btc', '比特幣']):
                            news_items.append({
                                'title': title,
                                'description': desc_elem.text[:200] if desc_elem is not None else '',
                                'url': link_elem.text if link_elem is not None else '',
                                'published_at': datetime.now().isoformat()
                            })
                
                return news_items[:5]
                
        except Exception as e:
            self.logger.warning(f"RSS fetch error: {e}")
            return None
    
    def parse_cryptopanic_data(self, data):
        """解析CryptoPanic數據"""
        try:
            news_items = []
            
            for item in data.get('results', [])[:10]:
                title = item.get('title', '')
                if any(keyword in title.lower() for keyword in ['bitcoin', 'btc', '比特幣']):
                    news_items.append({
                        'title': title,
                        'description': item.get('title', '')[:200],  # 使用標題作為描述
                        'url': item.get('url', ''),
                        'published_at': item.get('published_at', '')
                    })
            
            return news_items[:5]
            
        except Exception as e:
            self.logger.warning(f"CryptoPanic parse error: {e}")
            return None
    
    def get_fallback_analysis(self):
        """當無法獲取新聞時的備用分析"""
        return [
            {
                'title': '當前BTC市場相對穩定',
                'description': '由於網絡連接或API限制，無法獲取實時新聞。建議關注主要加密貨幣新聞網站。',
                'url': 'https://www.coindesk.com',
                'published_at': datetime.now().isoformat()
            }
        ]
    
    def analyze_news_with_ai(self, news_data):
        """使用AI分析新聞"""
        try:
            if not news_data:
                return "📰 目前無法獲取即時新聞，請稍後再試。"
            
            # 組合新聞標題和描述
            news_text = ""
            for i, news in enumerate(news_data, 1):
                news_text += f"{i}. {news['title']}\n{news.get('description', '')}\n\n"
            
            # 簡單的情感分析和趨勢判斷
            positive_keywords = [
                '上漲', '突破', '新高', '買入', '看多', '利好', '牛市', '反彈',
                'bullish', 'rise', 'surge', 'pump', 'moon', 'rally', 'gains',
                'adoption', 'institutional', 'etf', 'breakthrough'
            ]
            
            negative_keywords = [
                '下跌', '跌破', '賣出', '看空', '利空', '熊市', '回調', '暴跌',
                'bearish', 'fall', 'drop', 'dump', 'crash', 'decline',
                'correction', 'selloff', 'regulatory', 'ban'
            ]
            
            positive_count = sum(1 for keyword in positive_keywords if keyword.lower() in news_text.lower())
            negative_count = sum(1 for keyword in negative_keywords if keyword.lower() in news_text.lower())
            
            # 生成分析結果
            current_time = datetime.now().strftime('%H:%M:%S')
            analysis = f"🤖 AI BTC市場分析 ({current_time})：\n\n"
            
            if positive_count > negative_count:
                sentiment = "📈 偏向樂觀"
                analysis += f"{sentiment}：發現 {positive_count} 個正面信號，{negative_count} 個負面信號\n"
                analysis += "💡 市場情緒相對積極，可能有利於BTC價格表現。\n\n"
            elif negative_count > positive_count:
                sentiment = "📉 偏向謹慎"
                analysis += f"{sentiment}：發現 {negative_count} 個負面信號，{positive_count} 個正面信號\n"
                analysis += "⚠️ 市場存在謹慎情緒，建議密切關注技術指標。\n\n"
            else:
                sentiment = "⚖️ 相對平衡"
                analysis += f"{sentiment}：正負面信號基本均衡（正面{positive_count}個，負面{negative_count}個）\n"
                analysis += "💭 市場情緒較為中性，短期可能延續震蕩格局。\n\n"
            
            # 添加主要新聞標題
            analysis += "📰 主要關注事項：\n"
            for i, news in enumerate(news_data[:3], 1):
                title = news['title'][:60]
                analysis += f"{i}. {title}{'...' if len(news['title']) > 60 else ''}\n"
            
            analysis += f"\n🔄 分析更新時間：{current_time}"
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"AI analysis error: {e}")
            return f"🤖 AI分析系統：\n\n📊 當前BTC市場處於觀察階段\n💡 建議結合MACD技術指標進行判斷\n⏰ {datetime.now().strftime('%H:%M:%S')}"
    
    def update_ai_text(self, analysis):
        """更新AI分析文本"""
        try:
            self.ai_analysis_text.delete(1.0, tk.END)
            self.ai_analysis_text.insert(tk.END, analysis)
        except Exception as e:
            self.logger.error(f"Update AI text error: {e}")
    
    def log_message(self, message):
        """記錄日誌消息"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # 限制日誌長度
        if int(self.log_text.index('end-1c').split('.')[0]) > 1000:
            self.log_text.delete('1.0', '500.0')
    
    def run(self):
        """運行應用程式"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Application runtime error: {e}")
    
    def on_closing(self):
        """應用程式關閉處理"""
        try:
            self.running = False
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Application closing error: {e}")
            try:
                self.root.destroy()
            except:
                pass

def main():
    """主函數"""
    try:
        app = UltimateProfessionalBTCMACDGUI()
        app.run()
    except Exception as e:
        print(f"❌ Ultimate Professional application startup failed: {e}")

if __name__ == "__main__":
    main() 