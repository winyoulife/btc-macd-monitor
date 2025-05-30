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

# 導入專業模組
from max_api import MaxAPI
from enhanced_macd_analyzer import EnhancedMACDAnalyzer
from telegram_notifier import TelegramNotifier
from config import *
from professional_font_config import (
    font_manager, PROFESSIONAL_TEXT, PROFESSIONAL_COLORS,
    setup_professional_style
)
from macd_detail_window import MACDDetailWindow

class ProfessionalBTCMACDGUI:
    def __init__(self):
        # 初始化專業字體
        setup_professional_style()
        
        # 創建主窗口
        self.root = tk.Tk()
        self.root.title(PROFESSIONAL_TEXT['app_title'])
        self.root.geometry(f"{GUI_WIDTH}x{GUI_HEIGHT}")
        self.root.resizable(True, True)
        self.root.configure(bg=PROFESSIONAL_COLORS['background'])
        
        # 設定窗口圖標和樣式
        self.setup_window_style()
        
        # 初始化組件
        self.max_api = MaxAPI()
        self.macd_analyzer = EnhancedMACDAnalyzer()
        self.telegram_notifier = TelegramNotifier()
        
        # 數據更新隊列
        self.update_queue = queue.Queue()
        
        # 控制變量
        self.running = False
        self.update_thread = None
        self.last_signal_time = None
        self.data_df = None
        self.macd_detail_window = None
        
        # 設定日誌
        self.setup_logging()
        
        # 創建專業樣式
        self.setup_professional_ttk_style()
        
        # 建立專業GUI
        self.setup_professional_gui()
        
        # 設定定時任務
        self.setup_schedule()
        
        # 啟動數據處理
        self.process_queue()
    
    def setup_window_style(self):
        """設定窗口樣式"""
        try:
            # 設定窗口最小尺寸
            self.root.minsize(1000, 700)
            
            # Windows特定設定
            if font_manager.system == "Windows":
                try:
                    # 設定Windows風格
                    self.root.wm_attributes('-transparentcolor', '')
                except:
                    pass
        except Exception as e:
            print(f"窗口樣式設定失敗: {e}")
    
    def setup_professional_ttk_style(self):
        """設定專業TTK樣式"""
        self.style = ttk.Style()
        
        # 使用現代主題
        available_themes = self.style.theme_names()
        if 'vista' in available_themes:
            self.style.theme_use('vista')
        elif 'clam' in available_themes:
            self.style.theme_use('clam')
        
        # 自定義專業樣式
        self.style.configure('Professional.TLabel',
                           background=PROFESSIONAL_COLORS['background'],
                           foreground=PROFESSIONAL_COLORS['dark'],
                           font=font_manager.get_tkinter_font(10))
        
        self.style.configure('Title.TLabel',
                           background=PROFESSIONAL_COLORS['background'],
                           foreground=PROFESSIONAL_COLORS['primary'],
                           font=font_manager.get_tkinter_font(14, 'bold'))
        
        self.style.configure('Price.TLabel',
                           background=PROFESSIONAL_COLORS['background'],
                           foreground=PROFESSIONAL_COLORS['primary'],
                           font=font_manager.get_tkinter_font(18, 'bold'))
        
        self.style.configure('Status.TLabel',
                           background=PROFESSIONAL_COLORS['background'],
                           foreground=PROFESSIONAL_COLORS['success'],
                           font=font_manager.get_tkinter_font(12, 'bold'))
        
        # 按鈕樣式
        self.style.configure('Professional.TButton',
                           font=font_manager.get_tkinter_font(10),
                           padding=(10, 5))
        
        self.style.configure('Success.TButton',
                           font=font_manager.get_tkinter_font(10, 'bold'),
                           padding=(15, 8))
        
        self.style.configure('Warning.TButton',
                           font=font_manager.get_tkinter_font(10, 'bold'),
                           padding=(15, 8))
        
        # LabelFrame樣式
        self.style.configure('Professional.TLabelframe',
                           background=PROFESSIONAL_COLORS['background'],
                           borderwidth=1,
                           relief='solid')
        
        self.style.configure('Professional.TLabelframe.Label',
                           background=PROFESSIONAL_COLORS['background'],
                           foreground=PROFESSIONAL_COLORS['primary'],
                           font=font_manager.get_tkinter_font(11, 'bold'))
        
        # Notebook樣式
        self.style.configure('Professional.TNotebook',
                           background=PROFESSIONAL_COLORS['background'],
                           borderwidth=0)
        
        self.style.configure('Professional.TNotebook.Tab',
                           background=PROFESSIONAL_COLORS['surface'],
                           foreground=PROFESSIONAL_COLORS['dark'],
                           font=font_manager.get_tkinter_font(10),
                           padding=(15, 8))
    
    def setup_logging(self):
        """設定日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_professional_gui(self):
        """建立專業界面"""
        # 主容器
        main_container = tk.Frame(self.root, bg=PROFESSIONAL_COLORS['background'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 標題區域
        self.create_header_section(main_container)
        
        # 控制面板
        self.create_control_panel(main_container)
        
        # 價格資訊面板
        self.create_price_panel(main_container)
        
        # 圖表區域
        self.create_chart_panel(main_container)
        
        # 底部信息面板
        self.create_bottom_panel(main_container)
    
    def create_header_section(self, parent):
        """創建標題區域"""
        header_frame = tk.Frame(parent, bg=PROFESSIONAL_COLORS['background'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 主標題
        title_label = ttk.Label(header_frame, text=PROFESSIONAL_TEXT['app_title'],
                               style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # 狀態指示器
        status_frame = tk.Frame(header_frame, bg=PROFESSIONAL_COLORS['background'])
        status_frame.pack(side=tk.RIGHT)
        
        ttk.Label(status_frame, text="系統狀態:",
                 style='Professional.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_var = tk.StringVar(value=PROFESSIONAL_TEXT['status_waiting'])
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var,
                                     style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT)
    
    def create_control_panel(self, parent):
        """建立專業控制面板"""
        control_frame = ttk.LabelFrame(parent, text=PROFESSIONAL_TEXT['control_panel'],
                                      style='Professional.TLabelframe')
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 內部容器
        control_inner = tk.Frame(control_frame, bg=PROFESSIONAL_COLORS['background'])
        control_inner.pack(fill=tk.X, padx=15, pady=15)
        
        # 左側按鈕組
        left_buttons = tk.Frame(control_inner, bg=PROFESSIONAL_COLORS['background'])
        left_buttons.pack(side=tk.LEFT)
        
        # 主要控制按鈕
        self.start_button = ttk.Button(left_buttons, text=PROFESSIONAL_TEXT['start_monitor'],
                                      command=self.start_monitoring, style='Success.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(left_buttons, text=PROFESSIONAL_TEXT['stop_monitor'],
                                     command=self.stop_monitoring, state=tk.DISABLED,
                                     style='Warning.TButton')
        self.stop_button.pack(side=tk.LEFT, padx=(0, 20))
        
        # 功能按鈕
        ttk.Button(left_buttons, text=PROFESSIONAL_TEXT['manual_update'],
                  command=self.manual_update, style='Professional.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(left_buttons, text=PROFESSIONAL_TEXT['macd_detail'],
                  command=self.show_macd_detail, style='Professional.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(left_buttons, text=PROFESSIONAL_TEXT['settings'],
                  command=self.show_settings, style='Professional.TButton').pack(side=tk.LEFT)
        
        # 右側實時信息
        right_info = tk.Frame(control_inner, bg=PROFESSIONAL_COLORS['background'])
        right_info.pack(side=tk.RIGHT)
        
        # 最後更新時間
        ttk.Label(right_info, text=PROFESSIONAL_TEXT['update_time'] + ":",
                 style='Professional.TLabel').pack(anchor=tk.E)
        self.last_update_var = tk.StringVar(value="--")
        ttk.Label(right_info, textvariable=self.last_update_var,
                 style='Professional.TLabel').pack(anchor=tk.E)
    
    def create_price_panel(self, parent):
        """建立專業價格面板"""
        price_frame = ttk.LabelFrame(parent, text=PROFESSIONAL_TEXT['price_info'],
                                    style='Professional.TLabelframe')
        price_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 內部網格
        price_grid = tk.Frame(price_frame, bg=PROFESSIONAL_COLORS['background'])
        price_grid.pack(fill=tk.X, padx=20, pady=15)
        
        # 當前價格區域
        price_section = tk.Frame(price_grid, bg=PROFESSIONAL_COLORS['background'])
        price_section.pack(side=tk.LEFT)
        
        ttk.Label(price_section, text=PROFESSIONAL_TEXT['current_price'] + ":",
                 style='Professional.TLabel').pack(anchor=tk.W)
        
        self.current_price_var = tk.StringVar(value=PROFESSIONAL_TEXT['loading'])
        price_label = ttk.Label(price_section, textvariable=self.current_price_var,
                               style='Price.TLabel')
        price_label.pack(anchor=tk.W)
        
        # 變化幅度區域
        change_section = tk.Frame(price_grid, bg=PROFESSIONAL_COLORS['background'])
        change_section.pack(side=tk.LEFT, padx=(50, 0))
        
        ttk.Label(change_section, text=PROFESSIONAL_TEXT['24h_change'] + ":",
                 style='Professional.TLabel').pack(anchor=tk.W)
        
        self.price_change_var = tk.StringVar(value="--")
        self.price_change_label = ttk.Label(change_section, textvariable=self.price_change_var,
                                           style='Professional.TLabel')
        self.price_change_label.pack(anchor=tk.W)
        
        # 信號狀態區域
        signal_section = tk.Frame(price_grid, bg=PROFESSIONAL_COLORS['background'])
        signal_section.pack(side=tk.RIGHT)
        
        ttk.Label(signal_section, text=PROFESSIONAL_TEXT['signal'] + ":",
                 style='Professional.TLabel').pack(anchor=tk.E)
        
        # 當前信號顯示
        signal_display = tk.Frame(signal_section, bg=PROFESSIONAL_COLORS['background'])
        signal_display.pack(anchor=tk.E)
        
        self.signal_var = tk.StringVar(value="HOLD")
        self.signal_label = ttk.Label(signal_display, textvariable=self.signal_var,
                                     style='Status.TLabel')
        self.signal_label.pack(side=tk.LEFT)
        
        self.strength_var = tk.StringVar(value="0%")
        ttk.Label(signal_display, textvariable=self.strength_var,
                 style='Professional.TLabel').pack(side=tk.LEFT, padx=(10, 0))
    
    def create_chart_panel(self, parent):
        """建立專業圖表面板"""
        chart_frame = ttk.LabelFrame(parent, text=PROFESSIONAL_TEXT['chart_panel'],
                                    style='Professional.TLabelframe')
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 圖表容器
        chart_container = tk.Frame(chart_frame, bg=PROFESSIONAL_COLORS['chart_bg'])
        chart_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 創建專業matplotlib圖表
        self.fig = Figure(figsize=(14, 10), dpi=100)
        self.fig.patch.set_facecolor(PROFESSIONAL_COLORS['chart_bg'])
        
        # 創建子圖：價格圖和MACD圖
        self.ax1 = self.fig.add_subplot(211)  # 價格圖
        self.ax2 = self.fig.add_subplot(212)  # MACD圖
        
        # 設定子圖樣式
        self.setup_subplot_style()
        
        self.fig.tight_layout(pad=4.0)
        
        self.canvas = FigureCanvasTkAgg(self.fig, chart_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 初始化空圖表
        self.update_empty_chart()
    
    def setup_subplot_style(self):
        """設定子圖樣式"""
        # 價格圖樣式
        self.ax1.set_facecolor(PROFESSIONAL_COLORS['background'])
        self.ax1.grid(True, color=PROFESSIONAL_COLORS['grid'], alpha=0.6, linewidth=0.5)
        self.ax1.spines['top'].set_visible(False)
        self.ax1.spines['right'].set_visible(False)
        self.ax1.spines['left'].set_color(PROFESSIONAL_COLORS['border'])
        self.ax1.spines['bottom'].set_color(PROFESSIONAL_COLORS['border'])
        
        # MACD圖樣式
        self.ax2.set_facecolor(PROFESSIONAL_COLORS['background'])
        self.ax2.grid(True, color=PROFESSIONAL_COLORS['grid'], alpha=0.6, linewidth=0.5)
        self.ax2.spines['top'].set_visible(False)
        self.ax2.spines['right'].set_visible(False)
        self.ax2.spines['left'].set_color(PROFESSIONAL_COLORS['border'])
        self.ax2.spines['bottom'].set_color(PROFESSIONAL_COLORS['border'])
    
    def create_bottom_panel(self, parent):
        """建立底部面板"""
        # 使用notebook來分頁顯示
        notebook = ttk.Notebook(parent, style='Professional.TNotebook')
        notebook.pack(fill=tk.X, pady=(0, 10))
        
        # 交易信號頁面
        signal_frame = tk.Frame(notebook, bg=PROFESSIONAL_COLORS['background'])
        notebook.add(signal_frame, text=PROFESSIONAL_TEXT['signal_panel'])
        
        self.create_signal_panel(signal_frame)
        
        # 系統日誌頁面
        log_frame = tk.Frame(notebook, bg=PROFESSIONAL_COLORS['background'])
        notebook.add(log_frame, text=PROFESSIONAL_TEXT['system_log'])
        
        self.create_log_panel(log_frame)
    
    def create_signal_panel(self, parent):
        """創建信號面板"""
        signal_container = tk.Frame(parent, bg=PROFESSIONAL_COLORS['background'])
        signal_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 信號詳情網格
        signal_grid = tk.Frame(signal_container, bg=PROFESSIONAL_COLORS['background'])
        signal_grid.pack(fill=tk.X)
        
        # 信號類型
        ttk.Label(signal_grid, text=PROFESSIONAL_TEXT['signal'] + ":",
                 style='Professional.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 15))
        
        self.signal_display_var = tk.StringVar(value="⏸️ HOLD")
        self.signal_display_label = ttk.Label(signal_grid, textvariable=self.signal_display_var,
                                             style='Status.TLabel')
        self.signal_display_label.grid(row=0, column=1, sticky=tk.W, padx=15)
        
        # 信號強度
        ttk.Label(signal_grid, text=PROFESSIONAL_TEXT['strength'] + ":",
                 style='Professional.TLabel').grid(row=0, column=2, sticky=tk.W, padx=(30, 15))
        
        self.strength_display_var = tk.StringVar(value="0%")
        ttk.Label(signal_grid, textvariable=self.strength_display_var,
                 style='Professional.TLabel').grid(row=0, column=3, sticky=tk.W, padx=15)
        
        # 信號原因
        ttk.Label(signal_grid, text=PROFESSIONAL_TEXT['reason'] + ":",
                 style='Professional.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        self.reason_var = tk.StringVar(value="--")
        ttk.Label(signal_grid, textvariable=self.reason_var,
                 style='Professional.TLabel').grid(row=1, column=1, columnspan=3,
                                                  sticky=tk.W, padx=15, pady=(10, 0))
    
    def create_log_panel(self, parent):
        """創建日誌面板"""
        log_container = tk.Frame(parent, bg=PROFESSIONAL_COLORS['background'])
        log_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 日誌文本框
        log_text_frame = tk.Frame(log_container, bg=PROFESSIONAL_COLORS['background'])
        log_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_text_frame, height=6, wrap=tk.WORD,
                               font=font_manager.get_tkinter_font(9),
                               bg=PROFESSIONAL_COLORS['surface'],
                               fg=PROFESSIONAL_COLORS['dark'],
                               selectbackground=PROFESSIONAL_COLORS['primary'],
                               selectforeground='white',
                               borderwidth=1,
                               relief='solid')
        
        log_scrollbar = ttk.Scrollbar(log_text_frame, orient=tk.VERTICAL,
                                     command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_schedule(self):
        """設定定時任務"""
        schedule.every().hour.at(":00").do(self.hourly_record)
    
    def update_empty_chart(self):
        """更新空圖表"""
        self.ax1.clear()
        self.ax2.clear()
        self.setup_subplot_style()
        
        self.ax1.text(0.5, 0.5, PROFESSIONAL_TEXT['loading'],
                     ha='center', va='center', transform=self.ax1.transAxes,
                     fontsize=14, color=PROFESSIONAL_COLORS['muted'])
        self.ax1.set_title(PROFESSIONAL_TEXT['price_trend'], fontsize=14, fontweight='bold',
                          color=PROFESSIONAL_COLORS['primary'], pad=20)
        
        self.ax2.text(0.5, 0.5, PROFESSIONAL_TEXT['loading'],
                     ha='center', va='center', transform=self.ax2.transAxes,
                     fontsize=14, color=PROFESSIONAL_COLORS['muted'])
        self.ax2.set_title(PROFESSIONAL_TEXT['macd_indicator'], fontsize=14, fontweight='bold',
                          color=PROFESSIONAL_COLORS['primary'], pad=20)
        
        self.canvas.draw()
    
    def start_monitoring(self):
        """啟動監控"""
        if not self.running:
            self.running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_var.set(PROFESSIONAL_TEXT['status_running'])
            
            # 更新狀態標籤顏色
            self.style.configure('Status.TLabel', foreground=PROFESSIONAL_COLORS['success'])
            
            # 啟動更新線程
            self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
            self.update_thread.start()
            
            self.log_message("🚀 系統啟動，開始專業監控 BTC/TWD MACD 信號...")
    
    def stop_monitoring(self):
        """停止監控"""
        if self.running:
            self.running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_var.set(PROFESSIONAL_TEXT['status_stopped'])
            
            # 更新狀態標籤顏色
            self.style.configure('Status.TLabel', foreground=PROFESSIONAL_COLORS['warning'])
            
            self.log_message("⏹️ 監控已停止")
    
    def manual_update(self):
        """手動更新"""
        if not self.running:
            self.log_message("🔄 執行手動更新...")
            threading.Thread(target=self.fetch_and_analyze, daemon=True).start()
    
    def show_macd_detail(self):
        """顯示MACD詳細視窗"""
        try:
            if (self.macd_detail_window is None or 
                not hasattr(self.macd_detail_window, 'window') or
                not self.macd_detail_window.window.winfo_exists()):
                
                self.macd_detail_window = MACDDetailWindow(self.root)
            
            if self.data_df is not None:
                current_price = self.get_current_price()
                signal_data = self.macd_analyzer.analyze_enhanced_signal(self.data_df, current_price)
                self.macd_detail_window.update_data(self.data_df, signal_data)
            
            try:
                self.macd_detail_window.show()
            except tk.TclError:
                self.macd_detail_window = MACDDetailWindow(self.root)
                if self.data_df is not None:
                    current_price = self.get_current_price()
                    signal_data = self.macd_analyzer.analyze_enhanced_signal(self.data_df, current_price)
                    self.macd_detail_window.update_data(self.data_df, signal_data)
                self.macd_detail_window.show()
                
        except Exception as e:
            self.logger.error(f"顯示MACD詳細視窗失敗: {e}")
            self.log_message(f"❌ 無法開啟MACD詳細視窗: {str(e)}")
            self.macd_detail_window = None
    
    def show_settings(self):
        """顯示設置視窗"""
        messagebox.showinfo("設置", "⚙️ 專業設置功能開發中...")
    
    def update_loop(self):
        """數據更新循環"""
        while self.running:
            try:
                self.fetch_and_analyze()
                schedule.run_pending()
                time.sleep(UPDATE_INTERVAL)
            except Exception as e:
                self.logger.error(f"更新循環錯誤: {e}")
                time.sleep(5)
    
    def fetch_and_analyze(self):
        """獲取數據並分析"""
        try:
            # 獲取K線數據（5天）
            kline_data = self.max_api.get_klines('btctwd', period=1, limit=7200)
            
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
            self.update_queue.put(('chart_data', df_with_macd))
            self.update_queue.put(('signal_data', signal_data))
            
            # 檢查通知
            self.check_and_send_notification(signal_data)
            
        except Exception as e:
            self.logger.error(f"數據獲取分析錯誤: {e}")
            self.log_message(f"❌ 數據更新失敗: {str(e)}")
    
    def get_current_price(self):
        """獲取當前價格"""
        try:
            ticker = self.max_api.get_ticker('btctwd')
            if ticker:
                return ticker['price']
        except Exception as e:
            self.logger.error(f"獲取價格失敗: {e}")
        return 0
    
    def check_and_send_notification(self, signal_data):
        """檢查並發送通知"""
        try:
            signal_type = signal_data.get('signal', 'HOLD')
            strength = signal_data.get('strength', 0)
            
            if signal_type in ['BUY', 'SELL'] and strength >= 70:
                current_time = datetime.now()
                
                if (self.last_signal_time is None or 
                    (current_time - self.last_signal_time).seconds > 600):
                    
                    self.telegram_notifier.send_signal_notification(signal_data)
                    self.last_signal_time = current_time
                    
                    self.log_message(f"📤 已發送{signal_type}信號通知，強度: {strength}%")
                    
        except Exception as e:
            self.logger.error(f"通知發送錯誤: {e}")
    
    def hourly_record(self):
        """整點記錄"""
        try:
            if self.data_df is not None:
                success = self.macd_analyzer.record_hourly_data(self.data_df, 10)
                if success:
                    self.log_message("✅ 已完成整點MACD數據記錄")
        except Exception as e:
            self.logger.error(f"整點記錄錯誤: {e}")
    
    def process_queue(self):
        """處理更新隊列"""
        try:
            while True:
                try:
                    item = self.update_queue.get_nowait()
                    data_type, data = item
                    
                    if data_type == 'price_data':
                        self.update_price_display(data)
                    elif data_type == 'chart_data':
                        self.update_professional_chart(data)
                    elif data_type == 'signal_data':
                        self.update_signal_display(data)
                        
                except queue.Empty:
                    break
                    
        except Exception as e:
            self.logger.error(f"隊列處理錯誤: {e}")
        
        self.root.after(100, self.process_queue)
    
    def update_price_display(self, current_price):
        """更新價格顯示"""
        try:
            self.current_price_var.set(f"${current_price:,.0f} TWD")
            self.last_update_var.set(datetime.now().strftime('%H:%M:%S'))
            
            # 這裡可以添加24小時變化計算
            self.price_change_var.set("--")
            
        except Exception as e:
            self.logger.error(f"價格顯示更新錯誤: {e}")
    
    def update_professional_chart(self, df):
        """更新專業圖表"""
        try:
            self.ax1.clear()
            self.ax2.clear()
            self.setup_subplot_style()
            
            # 只顯示近5天的數據
            days_5_ago = datetime.now() - timedelta(days=5)
            recent_data = df[df['timestamp'] >= days_5_ago]
            
            if len(recent_data) == 0:
                self.update_empty_chart()
                return
            
            # 專業價格圖 (上方)
            self.ax1.plot(recent_data['timestamp'], recent_data['close'], 
                         color=PROFESSIONAL_COLORS['primary'], linewidth=2.5, label='BTC/TWD', alpha=0.9)
            self.ax1.plot(recent_data['timestamp'], recent_data['ema_12'], 
                         color=PROFESSIONAL_COLORS['success'], linewidth=1.5, alpha=0.8, label=PROFESSIONAL_TEXT['ema12'])
            self.ax1.plot(recent_data['timestamp'], recent_data['ema_26'], 
                         color=PROFESSIONAL_COLORS['danger'], linewidth=1.5, alpha=0.8, label=PROFESSIONAL_TEXT['ema26'])
            
            self.ax1.set_title(PROFESSIONAL_TEXT['price_trend'], fontsize=14, fontweight='bold',
                              color=PROFESSIONAL_COLORS['primary'], pad=20)
            self.ax1.legend(loc='upper left', framealpha=0.9)
            
            # 專業MACD圖 (下方)
            self.ax2.plot(recent_data['timestamp'], recent_data['macd'], 
                         color=PROFESSIONAL_COLORS['macd_line'], linewidth=2.5, label=PROFESSIONAL_TEXT['macd'])
            self.ax2.plot(recent_data['timestamp'], recent_data['macd_signal'], 
                         color=PROFESSIONAL_COLORS['signal_line'], linewidth=2.5, label=PROFESSIONAL_TEXT['signal_line'])
            
            # 專業Histogram柱狀圖
            colors = [PROFESSIONAL_COLORS['histogram_pos'] if x > 0 else PROFESSIONAL_COLORS['histogram_neg'] 
                     for x in recent_data['macd_histogram']]
            self.ax2.bar(recent_data['timestamp'], recent_data['macd_histogram'], 
                        color=colors, alpha=0.7, width=timedelta(minutes=5), label=PROFESSIONAL_TEXT['histogram'])
            
            self.ax2.axhline(y=0, color=PROFESSIONAL_COLORS['dark'], linestyle='-', alpha=0.4, linewidth=1)
            self.ax2.set_title(PROFESSIONAL_TEXT['macd_indicator'], fontsize=14, fontweight='bold',
                              color=PROFESSIONAL_COLORS['primary'], pad=20)
            self.ax2.legend(loc='upper left', framealpha=0.9)
            
            # 設定專業時間軸格式
            self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            self.ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            
            plt.setp(self.ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
            plt.setp(self.ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            self.fig.tight_layout(pad=4.0)
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"圖表更新錯誤: {e}")
    
    def update_signal_display(self, signal_data):
        """更新信號顯示"""
        try:
            signal_type = signal_data.get('signal', 'HOLD')
            strength = signal_data.get('strength', 0)
            reason = signal_data.get('reason', '--')
            
            # 更新主界面信號顯示
            if signal_type == 'BUY':
                self.signal_var.set("🚀 BUY")
                self.signal_display_var.set("🚀 BUY")
                self.style.configure('Status.TLabel', foreground=PROFESSIONAL_COLORS['buy_color'])
            elif signal_type == 'SELL':
                self.signal_var.set("📉 SELL")
                self.signal_display_var.set("📉 SELL")
                self.style.configure('Status.TLabel', foreground=PROFESSIONAL_COLORS['sell_color'])
            else:
                self.signal_var.set("⏸️ HOLD")
                self.signal_display_var.set("⏸️ HOLD")
                self.style.configure('Status.TLabel', foreground=PROFESSIONAL_COLORS['hold_color'])
            
            self.strength_var.set(f"{strength}%")
            self.strength_display_var.set(f"{strength}%")
            self.reason_var.set(reason)
            
            # 更新MACD詳細視窗
            try:
                if (self.macd_detail_window and 
                    hasattr(self.macd_detail_window, 'window') and
                    self.macd_detail_window.window.winfo_exists()):
                    self.macd_detail_window.update_data(self.data_df, signal_data)
            except (tk.TclError, AttributeError):
                self.macd_detail_window = None
                    
        except Exception as e:
            self.logger.error(f"信號顯示更新錯誤: {e}")
    
    def log_message(self, message):
        """記錄專業日誌消息"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # 限制日誌長度
        if int(self.log_text.index('end-1c').split('.')[0]) > 1000:
            self.log_text.delete('1.0', '500.0')
    
    def run(self):
        """運行專業應用程式"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"應用程式運行錯誤: {e}")
    
    def on_closing(self):
        """應用程式關閉處理"""
        try:
            self.running = False
            
            # 安全關閉MACD詳細視窗
            if self.macd_detail_window:
                try:
                    if (hasattr(self.macd_detail_window, 'window') and
                        self.macd_detail_window.window.winfo_exists()):
                        self.macd_detail_window.destroy()
                except (tk.TclError, AttributeError):
                    pass
                finally:
                    self.macd_detail_window = None
            
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"應用程式關閉錯誤: {e}")
            try:
                self.root.destroy()
            except:
                pass

def main():
    """主函數"""
    try:
        app = ProfessionalBTCMACDGUI()
        app.run()
    except Exception as e:
        print(f"❌ 專業應用程式啟動失敗: {e}")

if __name__ == "__main__":
    main() 