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

# 導入自定義模組
from max_api import MaxAPI
from enhanced_macd_analyzer import EnhancedMACDAnalyzer
from telegram_notifier import TelegramNotifier
from config import *
from font_config import setup_chinese_font, DISPLAY_TEXT
from macd_detail_window import MACDDetailWindow

class OptimizedBTCMACDGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 BTC MACD 專業交易信號分析系統")
        self.root.geometry(f"{GUI_WIDTH}x{GUI_HEIGHT}")
        self.root.resizable(True, True)
        
        # 設定中文字體
        setup_chinese_font()
        
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
        
        # 建立GUI
        self.setup_gui()
        
        # 設定定時任務
        self.setup_schedule()
        
        # 啟動數據處理
        self.process_queue()
    
    def setup_logging(self):
        """設定日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_gui(self):
        """建立主界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 控制面板
        self.create_control_panel(main_frame)
        
        # 價格資訊面板
        self.create_price_panel(main_frame)
        
        # MACD圖表區域
        self.create_chart_panel(main_frame)
        
        # 信號與日誌面板
        self.create_signal_log_panel(main_frame)
    
    def create_control_panel(self, parent):
        """建立控制面板"""
        control_frame = ttk.LabelFrame(parent, text="🎛️ 控制面板", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)
        
        # 啟動/停止按鈕
        self.start_button = ttk.Button(button_frame, text="🚀 啟動監控", 
                                      command=self.start_monitoring, style='Success.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ 停止監控", 
                                     command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 手動更新按鈕
        ttk.Button(button_frame, text="🔄 手動更新", 
                  command=self.manual_update).pack(side=tk.LEFT, padx=(0, 10))
        
        # MACD詳細視窗按鈕
        ttk.Button(button_frame, text="📊 MACD詳細", 
                  command=self.show_macd_detail).pack(side=tk.LEFT, padx=(0, 10))
        
        # 設置按鈕
        ttk.Button(button_frame, text="⚙️ 設置", 
                  command=self.show_settings).pack(side=tk.LEFT, padx=(0, 10))
        
        # 狀態顯示
        self.status_var = tk.StringVar(value="🟡 等待啟動")
        status_label = ttk.Label(button_frame, textvariable=self.status_var, 
                                font=("Arial", 12, "bold"))
        status_label.pack(side=tk.RIGHT)
    
    def create_price_panel(self, parent):
        """建立價格資訊面板"""
        price_frame = ttk.LabelFrame(parent, text="💰 BTC/TWD 即時行情", padding=15)
        price_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 價格網格
        price_grid = ttk.Frame(price_frame)
        price_grid.pack(fill=tk.X)
        
        # 當前價格
        ttk.Label(price_grid, text="當前價格:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.current_price_var = tk.StringVar(value="載入中...")
        price_label = ttk.Label(price_grid, textvariable=self.current_price_var, 
                               font=("Arial", 18, "bold"), foreground="blue")
        price_label.grid(row=0, column=1, sticky=tk.W, padx=10)
        
        # 24小時變化
        ttk.Label(price_grid, text="24H變化:", font=("Arial", 12, "bold")).grid(
            row=0, column=2, sticky=tk.W, padx=(20, 10))
        self.price_change_var = tk.StringVar(value="--")
        self.price_change_label = ttk.Label(price_grid, textvariable=self.price_change_var, 
                                           font=("Arial", 14, "bold"))
        self.price_change_label.grid(row=0, column=3, sticky=tk.W, padx=10)
        
        # 最後更新時間
        ttk.Label(price_grid, text="更新時間:", font=("Arial", 10)).grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.last_update_var = tk.StringVar(value="--")
        ttk.Label(price_grid, textvariable=self.last_update_var, 
                 font=("Arial", 10)).grid(row=1, column=1, columnspan=3, 
                                         sticky=tk.W, padx=10, pady=(10, 0))
    
    def create_chart_panel(self, parent):
        """建立MACD圖表面板"""
        chart_frame = ttk.LabelFrame(parent, text="📈 MACD 技術分析圖表", padding=10)
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 創建matplotlib圖表
        self.fig = Figure(figsize=(12, 8), dpi=100)
        self.fig.patch.set_facecolor('white')
        
        # 創建子圖：價格圖和MACD圖
        self.ax1 = self.fig.add_subplot(211)  # 價格圖
        self.ax2 = self.fig.add_subplot(212)  # MACD圖
        
        self.fig.tight_layout(pad=3.0)
        
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 初始化空圖表
        self.update_empty_chart()
    
    def create_signal_log_panel(self, parent):
        """建立信號與日誌面板"""
        # 使用notebook來分頁顯示
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        # 信號頁面
        signal_frame = ttk.Frame(notebook, padding=10)
        notebook.add(signal_frame, text="🎯 交易信號")
        
        # 當前信號顯示
        signal_info_frame = ttk.LabelFrame(signal_frame, text="當前信號狀態", padding=10)
        signal_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        signal_grid = ttk.Frame(signal_info_frame)
        signal_grid.pack(fill=tk.X)
        
        # 信號類型
        ttk.Label(signal_grid, text="信號:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.signal_var = tk.StringVar(value="HOLD")
        self.signal_label = ttk.Label(signal_grid, textvariable=self.signal_var, 
                                     font=("Arial", 14, "bold"))
        self.signal_label.grid(row=0, column=1, sticky=tk.W, padx=10)
        
        # 信號強度
        ttk.Label(signal_grid, text="強度:", font=("Arial", 12, "bold")).grid(
            row=0, column=2, sticky=tk.W, padx=(20, 10))
        self.strength_var = tk.StringVar(value="0%")
        ttk.Label(signal_grid, textvariable=self.strength_var, 
                 font=("Arial", 12)).grid(row=0, column=3, sticky=tk.W, padx=10)
        
        # 信號原因
        ttk.Label(signal_grid, text="原因:", font=("Arial", 10)).grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.reason_var = tk.StringVar(value="--")
        ttk.Label(signal_grid, textvariable=self.reason_var, 
                 font=("Arial", 10)).grid(row=1, column=1, columnspan=3, 
                                         sticky=tk.W, padx=10, pady=(5, 0))
        
        # 日誌頁面
        log_frame = ttk.Frame(notebook, padding=10)
        notebook.add(log_frame, text="📝 系統日誌")
        
        # 日誌文本框
        log_text_frame = ttk.Frame(log_frame)
        log_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_text_frame, height=8, wrap=tk.WORD, 
                               font=("Consolas", 9))
        log_scrollbar = ttk.Scrollbar(log_text_frame, orient=tk.VERTICAL, 
                                     command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_schedule(self):
        """設定定時任務"""
        # 每整點記錄MACD數據
        schedule.every().hour.at(":00").do(self.hourly_record)
        
    def update_empty_chart(self):
        """更新空圖表"""
        self.ax1.clear()
        self.ax2.clear()
        
        self.ax1.text(0.5, 0.5, '等待數據載入...', ha='center', va='center', 
                     transform=self.ax1.transAxes, fontsize=14)
        self.ax1.set_title('BTC/TWD 價格走勢', fontsize=12, fontweight='bold')
        
        self.ax2.text(0.5, 0.5, '等待MACD數據...', ha='center', va='center', 
                     transform=self.ax2.transAxes, fontsize=14)
        self.ax2.set_title('MACD 指標', fontsize=12, fontweight='bold')
        
        self.canvas.draw()
    
    def start_monitoring(self):
        """啟動監控"""
        if not self.running:
            self.running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_var.set("🟢 監控中")
            
            # 啟動更新線程
            self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
            self.update_thread.start()
            
            self.log_message("系統啟動，開始監控 BTC/TWD MACD 信號...")
    
    def stop_monitoring(self):
        """停止監控"""
        if self.running:
            self.running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_var.set("🟡 已停止")
            
            self.log_message("監控已停止")
    
    def manual_update(self):
        """手動更新"""
        if not self.running:
            self.log_message("執行手動更新...")
            threading.Thread(target=self.fetch_and_analyze, daemon=True).start()
    
    def show_macd_detail(self):
        """顯示MACD詳細視窗"""
        try:
            # 檢查視窗是否存在且有效
            if (self.macd_detail_window is None or 
                not hasattr(self.macd_detail_window, 'window') or
                not self.macd_detail_window.window.winfo_exists()):
                
                # 創建新的詳細視窗
                self.macd_detail_window = MACDDetailWindow(self.root)
            
            if self.data_df is not None:
                # 獲取最新的信號數據
                current_price = self.get_current_price()
                signal_data = self.macd_analyzer.analyze_enhanced_signal(self.data_df, current_price)
                self.macd_detail_window.update_data(self.data_df, signal_data)
            
            # 安全地顯示視窗
            try:
                self.macd_detail_window.show()
            except tk.TclError:
                # 如果視窗已經銷毀，重新創建
                self.macd_detail_window = MACDDetailWindow(self.root)
                if self.data_df is not None:
                    current_price = self.get_current_price()
                    signal_data = self.macd_analyzer.analyze_enhanced_signal(self.data_df, current_price)
                    self.macd_detail_window.update_data(self.data_df, signal_data)
                self.macd_detail_window.show()
                
        except Exception as e:
            self.logger.error(f"顯示MACD詳細視窗失敗: {e}")
            self.log_message(f"無法開啟MACD詳細視窗: {str(e)}")
            # 重置視窗引用
            self.macd_detail_window = None
    
    def show_settings(self):
        """顯示設置視窗"""
        messagebox.showinfo("設置", "設置功能開發中...")
    
    def update_loop(self):
        """數據更新循環"""
        while self.running:
            try:
                # 執行數據獲取和分析
                self.fetch_and_analyze()
                
                # 執行定時任務
                schedule.run_pending()
                
                # 等待下一次更新
                time.sleep(UPDATE_INTERVAL)
                
            except Exception as e:
                self.logger.error(f"更新循環錯誤: {e}")
                time.sleep(5)  # 錯誤時短暫等待
    
    def fetch_and_analyze(self):
        """獲取數據並分析"""
        try:
            # 獲取K線數據（5天）
            kline_data = self.max_api.get_klines('btctwd', period=1, limit=7200)  # 5分鐘K線，5天數據
            
            if kline_data is None or len(kline_data) == 0:
                self.log_message("無法獲取K線數據")
                return
            
            # 計算MACD
            df_with_macd = self.macd_analyzer.calculate_macd(kline_data)
            
            if df_with_macd is None:
                self.log_message("MACD計算失敗")
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
            
            # 檢查是否需要發送通知
            self.check_and_send_notification(signal_data)
            
        except Exception as e:
            self.logger.error(f"數據獲取分析錯誤: {e}")
            self.log_message(f"數據更新失敗: {str(e)}")
    
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
            
            # 只有高強度信號才發送通知
            if signal_type in ['BUY', 'SELL'] and strength >= 70:
                current_time = datetime.now()
                
                # 避免重複發送（10分鐘內不重複）
                if (self.last_signal_time is None or 
                    (current_time - self.last_signal_time).seconds > 600):
                    
                    self.telegram_notifier.send_signal_notification(signal_data)
                    self.last_signal_time = current_time
                    
                    self.log_message(f"已發送{signal_type}信號通知，強度: {strength}%")
                    
        except Exception as e:
            self.logger.error(f"通知發送錯誤: {e}")
    
    def hourly_record(self):
        """整點記錄"""
        try:
            if self.data_df is not None:
                success = self.macd_analyzer.record_hourly_data(self.data_df, 10)
                if success:
                    self.log_message("已完成整點MACD數據記錄")
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
                        self.update_chart(data)
                    elif data_type == 'signal_data':
                        self.update_signal_display(data)
                        
                except queue.Empty:
                    break
                    
        except Exception as e:
            self.logger.error(f"隊列處理錯誤: {e}")
        
        # 每100ms檢查一次隊列
        self.root.after(100, self.process_queue)
    
    def update_price_display(self, current_price):
        """更新價格顯示"""
        try:
            self.current_price_var.set(f"${current_price:,.0f} TWD")
            self.last_update_var.set(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # 這裡可以添加24小時變化計算
            # 暫時先設置為空
            self.price_change_var.set("--")
            
        except Exception as e:
            self.logger.error(f"價格顯示更新錯誤: {e}")
    
    def update_chart(self, df):
        """更新圖表"""
        try:
            self.ax1.clear()
            self.ax2.clear()
            
            # 只顯示近5天的數據
            days_5_ago = datetime.now() - timedelta(days=5)
            recent_data = df[df['timestamp'] >= days_5_ago]
            
            if len(recent_data) == 0:
                self.update_empty_chart()
                return
            
            # 價格圖 (上方)
            self.ax1.plot(recent_data['timestamp'], recent_data['close'], 
                         color='black', linewidth=2, label='BTC/TWD')
            self.ax1.plot(recent_data['timestamp'], recent_data['ema_12'], 
                         color='blue', linewidth=1, alpha=0.7, label='EMA12')
            self.ax1.plot(recent_data['timestamp'], recent_data['ema_26'], 
                         color='red', linewidth=1, alpha=0.7, label='EMA26')
            
            self.ax1.set_title('BTC/TWD 價格走勢 (近5天)', fontsize=12, fontweight='bold')
            self.ax1.legend(loc='upper left')
            self.ax1.grid(True, alpha=0.3)
            
            # MACD圖 (下方)
            self.ax2.plot(recent_data['timestamp'], recent_data['macd'], 
                         color='blue', linewidth=2, label='MACD')
            self.ax2.plot(recent_data['timestamp'], recent_data['macd_signal'], 
                         color='red', linewidth=2, label='Signal')
            
            # Histogram柱狀圖
            colors = ['green' if x > 0 else 'red' for x in recent_data['macd_histogram']]
            self.ax2.bar(recent_data['timestamp'], recent_data['macd_histogram'], 
                        color=colors, alpha=0.6, width=timedelta(minutes=5), label='Histogram')
            
            self.ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            self.ax2.set_title('MACD 指標', fontsize=12, fontweight='bold')
            self.ax2.legend(loc='upper left')
            self.ax2.grid(True, alpha=0.3)
            
            # 設定時間軸格式
            self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            self.ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            
            plt.setp(self.ax1.xaxis.get_majorticklabels(), rotation=45)
            plt.setp(self.ax2.xaxis.get_majorticklabels(), rotation=45)
            
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"圖表更新錯誤: {e}")
    
    def update_signal_display(self, signal_data):
        """更新信號顯示"""
        try:
            signal_type = signal_data.get('signal', 'HOLD')
            strength = signal_data.get('strength', 0)
            reason = signal_data.get('reason', '--')
            
            # 更新信號顯示
            if signal_type == 'BUY':
                self.signal_var.set("🚀 BUY")
                self.signal_label.config(foreground="green")
            elif signal_type == 'SELL':
                self.signal_var.set("📉 SELL")
                self.signal_label.config(foreground="red")
            else:
                self.signal_var.set("⏸️ HOLD")
                self.signal_label.config(foreground="gray")
            
            self.strength_var.set(f"{strength}%")
            self.reason_var.set(reason)
            
            # 更新MACD詳細視窗（如果已開啟且有效）
            try:
                if (self.macd_detail_window and 
                    hasattr(self.macd_detail_window, 'window') and
                    self.macd_detail_window.window.winfo_exists()):
                    self.macd_detail_window.update_data(self.data_df, signal_data)
            except (tk.TclError, AttributeError):
                # 視窗已關閉或無效，清除引用
                self.macd_detail_window = None
                    
        except Exception as e:
            self.logger.error(f"信號顯示更新錯誤: {e}")
    
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
                    pass  # 視窗可能已經關閉
                finally:
                    self.macd_detail_window = None
            
            # 關閉主視窗
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"應用程式關閉錯誤: {e}")
            # 強制退出
            try:
                self.root.destroy()
            except:
                pass

def main():
    """主函數"""
    try:
        app = OptimizedBTCMACDGUI()
        app.run()
    except Exception as e:
        print(f"應用程式啟動失敗: {e}")

if __name__ == "__main__":
    main() 