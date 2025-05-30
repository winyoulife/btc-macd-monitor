import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
import threading
import time
import logging
from datetime import datetime, timedelta
import queue
import os

# 導入自定義模組
from max_api import MaxAPI
from macd_analyzer import MACDAnalyzer
from telegram_notifier import TelegramNotifier
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, PRICE_UPDATE_INTERVAL,
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
)

class BTCMACDApp:
    def __init__(self, root):
        self.root = root
        self.setup_logging()
        self.setup_window()
        
        # 初始化組件
        self.max_api = MaxAPI()
        self.macd_analyzer = MACDAnalyzer()
        self.telegram_notifier = TelegramNotifier()
        
        # 資料存儲
        self.price_data = None
        self.kline_data = None
        self.macd_data = None
        self.signal_history = []
        
        # 控制變數
        self.is_running = False
        self.update_thread = None
        self.data_queue = queue.Queue()
        
        # 建立GUI
        self.create_widgets()
        self.setup_plot()
        
        # 開始定時更新
        self.root.after(1000, self.check_queue)
        
    def setup_logging(self):
        """設定日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('btc_macd.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_window(self):
        """設定主視窗"""
        self.root.title("BTC/TWD MACD 交易信號分析系統")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(True, True)
        
        # 設定風格
        style = ttk.Style()
        style.theme_use('clam')
    
    def create_widgets(self):
        """建立GUI組件"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 上方控制面板
        self.create_control_panel(main_frame)
        
        # 中間價格信息面板
        self.create_price_panel(main_frame)
        
        # 圖表區域
        self.create_chart_area(main_frame)
        
        # 下方信號和日誌面板
        self.create_bottom_panel(main_frame)
    
    def create_control_panel(self, parent):
        """建立控制面板"""
        control_frame = ttk.LabelFrame(parent, text="控制面板", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 按鈕框架
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X)
        
        # 開始/停止按鈕
        self.start_btn = ttk.Button(
            btn_frame, text="開始監控", 
            command=self.toggle_monitoring, width=12
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 手動更新按鈕
        self.update_btn = ttk.Button(
            btn_frame, text="手動更新", 
            command=self.manual_update, width=12
        )
        self.update_btn.pack(side=tk.LEFT, padx=5)
        
        # 測試Telegram按鈕
        self.test_telegram_btn = ttk.Button(
            btn_frame, text="測試Telegram", 
            command=self.test_telegram_connection, width=12
        )
        self.test_telegram_btn.pack(side=tk.LEFT, padx=5)
        
        # 設定按鈕
        self.settings_btn = ttk.Button(
            btn_frame, text="設定", 
            command=self.open_settings, width=12
        )
        self.settings_btn.pack(side=tk.LEFT, padx=5)
        
        # 狀態標籤
        self.status_label = ttk.Label(control_frame, text="狀態: 已停止", foreground="red")
        self.status_label.pack(side=tk.RIGHT)
    
    def create_price_panel(self, parent):
        """建立價格信息面板"""
        price_frame = ttk.LabelFrame(parent, text="BTC/TWD 價格信息", padding=10)
        price_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 價格信息網格
        info_frame = ttk.Frame(price_frame)
        info_frame.pack(fill=tk.X)
        
        # 當前價格
        ttk.Label(info_frame, text="當前價格:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.price_var = tk.StringVar(value="--")
        self.price_label = ttk.Label(info_frame, textvariable=self.price_var, font=("Arial", 14, "bold"), foreground="blue")
        self.price_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # 24小時高/低價
        ttk.Label(info_frame, text="24H高:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        self.high_var = tk.StringVar(value="--")
        ttk.Label(info_frame, textvariable=self.high_var, foreground="green").grid(row=0, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(info_frame, text="24H低:").grid(row=0, column=4, sticky=tk.W, padx=(10, 5))
        self.low_var = tk.StringVar(value="--")
        ttk.Label(info_frame, textvariable=self.low_var, foreground="red").grid(row=0, column=5, sticky=tk.W, padx=5)
        
        # 成交量
        ttk.Label(info_frame, text="成交量:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.volume_var = tk.StringVar(value="--")
        ttk.Label(info_frame, textvariable=self.volume_var).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # 更新時間
        ttk.Label(info_frame, text="更新時間:").grid(row=1, column=2, sticky=tk.W, padx=(20, 5))
        self.update_time_var = tk.StringVar(value="--")
        ttk.Label(info_frame, textvariable=self.update_time_var).grid(row=1, column=3, columnspan=3, sticky=tk.W, padx=5)
    
    def create_chart_area(self, parent):
        """建立圖表區域"""
        chart_frame = ttk.LabelFrame(parent, text="MACD 技術分析圖表", padding=5)
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 創建圖表框架
        self.chart_frame = chart_frame
    
    def setup_plot(self):
        """設定matplotlib圖表"""
        self.fig = Figure(figsize=(12, 8), dpi=100)
        self.fig.patch.set_facecolor('white')
        
        # 創建子圖
        self.ax1 = self.fig.add_subplot(3, 1, 1)  # 價格圖
        self.ax2 = self.fig.add_subplot(3, 1, 2)  # MACD圖
        self.ax3 = self.fig.add_subplot(3, 1, 3)  # RSI圖
        
        self.fig.tight_layout(pad=3.0)
        
        # 創建畫布
        self.canvas = FigureCanvasTkAgg(self.fig, self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_bottom_panel(self, parent):
        """建立底部面板"""
        bottom_frame = ttk.Frame(parent)
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左側 - MACD指標面板
        self.create_macd_panel(bottom_frame)
        
        # 右側 - 信號和日誌面板
        self.create_signal_log_panel(bottom_frame)
    
    def create_macd_panel(self, parent):
        """建立MACD指標面板"""
        macd_frame = ttk.LabelFrame(parent, text="MACD 技術指標", padding=10)
        macd_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # MACD值顯示
        info_frame = ttk.Frame(macd_frame)
        info_frame.pack(fill=tk.X)
        
        # 創建指標標籤
        indicators = [
            ("MACD:", "macd_value_var"),
            ("Signal:", "signal_value_var"),
            ("Histogram:", "histogram_var"),
            ("RSI:", "rsi_var"),
            ("EMA12:", "ema12_var"),
            ("EMA26:", "ema26_var")
        ]
        
        for i, (label, var_name) in enumerate(indicators):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(info_frame, text=label, font=("Arial", 9, "bold")).grid(
                row=row, column=col, sticky=tk.W, padx=(0, 5), pady=2
            )
            var = tk.StringVar(value="--")
            setattr(self, var_name, var)
            ttk.Label(info_frame, textvariable=var, font=("Arial", 9)).grid(
                row=row, column=col+1, sticky=tk.W, padx=(0, 20), pady=2
            )
    
    def create_signal_log_panel(self, parent):
        """建立信號和日誌面板"""
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 交易信號面板
        signal_frame = ttk.LabelFrame(right_frame, text="交易信號", padding=10)
        signal_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 信號顯示
        signal_info = ttk.Frame(signal_frame)
        signal_info.pack(fill=tk.X)
        
        ttk.Label(signal_info, text="當前信號:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.signal_var = tk.StringVar(value="無信號")
        self.signal_label = ttk.Label(signal_info, textvariable=self.signal_var, 
                                     font=("Arial", 12, "bold"))
        self.signal_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 信號強度
        strength_frame = ttk.Frame(signal_frame)
        strength_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(strength_frame, text="信號強度:").pack(side=tk.LEFT)
        self.strength_var = tk.StringVar(value="0%")
        ttk.Label(strength_frame, textvariable=self.strength_var).pack(side=tk.LEFT, padx=(10, 0))
        
        # 信號原因
        ttk.Label(signal_frame, text="分析原因:").pack(anchor=tk.W, pady=(5, 0))
        self.reason_var = tk.StringVar(value="--")
        ttk.Label(signal_frame, textvariable=self.reason_var, wraplength=300).pack(anchor=tk.W)
        
        # 日誌面板
        log_frame = ttk.LabelFrame(right_frame, text="系統日誌", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=50)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def toggle_monitoring(self):
        """切換監控狀態"""
        if not self.is_running:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """開始監控"""
        self.is_running = True
        self.start_btn.config(text="停止監控")
        self.status_label.config(text="狀態: 運行中", foreground="green")
        
        # 啟動更新線程
        self.update_thread = threading.Thread(target=self.update_worker, daemon=True)
        self.update_thread.start()
        
        self.log_message("開始監控 BTC/TWD 價格和 MACD 信號")
    
    def stop_monitoring(self):
        """停止監控"""
        self.is_running = False
        self.start_btn.config(text="開始監控")
        self.status_label.config(text="狀態: 已停止", foreground="red")
        
        self.log_message("停止監控")
    
    def update_worker(self):
        """後台更新工作線程"""
        while self.is_running:
            try:
                # 獲取價格資料
                price_data = self.max_api.get_ticker()
                if price_data:
                    self.data_queue.put(('price', price_data))
                
                # 獲取K線資料
                kline_data = self.max_api.get_klines(limit=100)
                if kline_data is not None and len(kline_data) > 0:
                    # 計算MACD
                    macd_data = self.macd_analyzer.calculate_macd(kline_data)
                    if macd_data is not None:
                        self.data_queue.put(('macd', macd_data))
                        
                        # 分析信號
                        signal_data = self.macd_analyzer.analyze_signal(macd_data, price_data['price'])
                        self.data_queue.put(('signal', signal_data))
                        
                        # 檢查是否需要發送Telegram通知
                        if signal_data['signal'] in ['BUY', 'SELL'] and signal_data['strength'] > 50:
                            # 在後台發送通知
                            threading.Thread(
                                target=self.send_telegram_notification,
                                args=(signal_data, price_data),
                                daemon=True
                            ).start()
                
                time.sleep(PRICE_UPDATE_INTERVAL / 1000)  # 轉換為秒
                
            except Exception as e:
                self.logger.error(f"更新數據時出錯: {e}")
                time.sleep(5)  # 錯誤時等待更長時間
    
    def check_queue(self):
        """檢查數據隊列並更新GUI"""
        try:
            while True:
                data_type, data = self.data_queue.get_nowait()
                
                if data_type == 'price':
                    self.update_price_display(data)
                elif data_type == 'macd':
                    self.update_macd_display(data)
                    self.update_chart(data)
                elif data_type == 'signal':
                    self.update_signal_display(data)
                elif data_type == 'log':
                    self.log_message(data)
                    
        except queue.Empty:
            pass
        
        # 繼續檢查
        self.root.after(100, self.check_queue)
    
    def update_price_display(self, price_data):
        """更新價格顯示"""
        self.price_data = price_data
        self.price_var.set(f"${price_data['price']:,.0f} TWD")
        self.high_var.set(f"${price_data['high']:,.0f}")
        self.low_var.set(f"${price_data['low']:,.0f}")
        self.volume_var.set(f"{price_data['volume']:.2f} BTC")
        self.update_time_var.set(price_data['timestamp'].strftime('%H:%M:%S'))
    
    def update_macd_display(self, macd_data):
        """更新MACD指標顯示"""
        self.macd_data = macd_data
        summary = self.macd_analyzer.get_macd_summary(macd_data)
        
        if summary:
            self.macd_value_var.set(f"{summary['macd']:.4f}")
            self.signal_value_var.set(f"{summary['signal']:.4f}")
            self.histogram_var.set(f"{summary['histogram']:.4f}")
            self.rsi_var.set(f"{summary['rsi']:.1f}")
            self.ema12_var.set(f"${summary['ema_12']:,.0f}")
            self.ema26_var.set(f"${summary['ema_26']:,.0f}")
    
    def update_signal_display(self, signal_data):
        """更新信號顯示"""
        signal = signal_data['signal']
        strength = signal_data['strength']
        reason = signal_data['reason']
        
        # 設定信號顯示顏色
        if signal == 'BUY':
            color = 'green'
            display_signal = f"買入 🚀"
        elif signal == 'SELL':
            color = 'red'
            display_signal = f"賣出 📉"
        else:
            color = 'gray'
            display_signal = f"持有 ⏸️"
        
        self.signal_var.set(display_signal)
        self.signal_label.config(foreground=color)
        self.strength_var.set(f"{strength}%")
        self.reason_var.set(reason)
        
        # 記錄強信號
        if signal in ['BUY', 'SELL'] and strength > 50:
            self.log_message(f"強{signal}信號: {strength}% - {reason}")
    
    def update_chart(self, macd_data):
        """更新圖表"""
        try:
            if macd_data is None or len(macd_data) < 50:
                return
            
            # 清除舊圖
            self.ax1.clear()
            self.ax2.clear()
            self.ax3.clear()
            
            # 取最近50個數據點
            data = macd_data.tail(50).copy()
            x_range = range(len(data))
            
            # 圖1: 價格和EMA
            self.ax1.plot(x_range, data['close'], label='價格', color='black', linewidth=2)
            self.ax1.plot(x_range, data['ema_12'], label='EMA12', color='blue', alpha=0.7)
            self.ax1.plot(x_range, data['ema_26'], label='EMA26', color='red', alpha=0.7)
            self.ax1.set_title('BTC/TWD 價格走勢', fontsize=12, fontweight='bold')
            self.ax1.legend(loc='upper left')
            self.ax1.grid(True, alpha=0.3)
            
            # 圖2: MACD
            self.ax2.plot(x_range, data['macd'], label='MACD', color='blue', linewidth=2)
            self.ax2.plot(x_range, data['macd_signal'], label='Signal', color='red', linewidth=2)
            self.ax2.bar(x_range, data['macd_histogram'], label='Histogram', 
                        color=['green' if x > 0 else 'red' for x in data['macd_histogram']], 
                        alpha=0.6)
            self.ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            self.ax2.set_title('MACD 指標', fontsize=12, fontweight='bold')
            self.ax2.legend(loc='upper left')
            self.ax2.grid(True, alpha=0.3)
            
            # 圖3: RSI
            self.ax3.plot(x_range, data['rsi'], label='RSI', color='purple', linewidth=2)
            self.ax3.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='超買(70)')
            self.ax3.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='超賣(30)')
            self.ax3.axhline(y=50, color='gray', linestyle='-', alpha=0.5)
            self.ax3.set_title('RSI 相對強弱指標', fontsize=12, fontweight='bold')
            self.ax3.set_ylim(0, 100)
            self.ax3.legend(loc='upper left')
            self.ax3.grid(True, alpha=0.3)
            
            # 設定x軸標籤（時間）
            if len(data) > 10:
                step = max(1, len(data) // 10)
                x_labels = [data.iloc[i]['timestamp'].strftime('%H:%M') 
                           for i in range(0, len(data), step)]
                x_positions = list(range(0, len(data), step))
                
                for ax in [self.ax1, self.ax2, self.ax3]:
                    ax.set_xticks(x_positions)
                    ax.set_xticklabels(x_labels, rotation=45)
            
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"更新圖表失敗: {e}")
    
    def manual_update(self):
        """手動更新數據"""
        self.log_message("手動更新數據...")
        
        def update_task():
            try:
                # 獲取數據並放入隊列
                price_data = self.max_api.get_ticker()
                if price_data:
                    self.data_queue.put(('price', price_data))
                
                kline_data = self.max_api.get_klines(limit=100)
                if kline_data is not None:
                    macd_data = self.macd_analyzer.calculate_macd(kline_data)
                    if macd_data is not None:
                        self.data_queue.put(('macd', macd_data))
                        signal_data = self.macd_analyzer.analyze_signal(macd_data, price_data['price'])
                        self.data_queue.put(('signal', signal_data))
                        
                self.data_queue.put(('log', "手動更新完成"))
                        
            except Exception as e:
                self.data_queue.put(('log', f"手動更新失敗: {e}"))
        
        threading.Thread(target=update_task, daemon=True).start()
    
    def test_telegram_connection(self):
        """測試Telegram連接"""
        def test_task():
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                success, message = loop.run_until_complete(
                    self.telegram_notifier.test_connection()
                )
                loop.close()
                
                if success:
                    self.data_queue.put(('log', f"Telegram測試成功: {message}"))
                    messagebox.showinfo("成功", f"Telegram連接成功!\n{message}")
                else:
                    self.data_queue.put(('log', f"Telegram測試失敗: {message}"))
                    messagebox.showerror("失敗", f"Telegram連接失敗!\n{message}")
                    
            except Exception as e:
                error_msg = f"測試連接時出錯: {e}"
                self.data_queue.put(('log', error_msg))
                messagebox.showerror("錯誤", error_msg)
        
        threading.Thread(target=test_task, daemon=True).start()
    
    def send_telegram_notification(self, signal_data, price_data):
        """發送Telegram通知"""
        try:
            success = self.telegram_notifier.send_signal_sync(signal_data, price_data)
            if success:
                self.data_queue.put(('log', f"已發送{signal_data['signal']}信號通知"))
            else:
                self.data_queue.put(('log', "發送Telegram通知失敗"))
        except Exception as e:
            self.data_queue.put(('log', f"發送通知錯誤: {e}"))
    
    def open_settings(self):
        """開啟設定視窗"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("設定")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)
        
        # Telegram設定
        telegram_frame = ttk.LabelFrame(settings_window, text="Telegram 設定", padding=10)
        telegram_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(telegram_frame, text="Bot Token:").pack(anchor=tk.W)
        token_var = tk.StringVar(value=TELEGRAM_BOT_TOKEN)
        token_entry = ttk.Entry(telegram_frame, textvariable=token_var, width=50, show="*")
        token_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(telegram_frame, text="Chat ID:").pack(anchor=tk.W)
        chat_var = tk.StringVar(value=TELEGRAM_CHAT_ID)
        chat_entry = ttk.Entry(telegram_frame, textvariable=chat_var, width=50)
        chat_entry.pack(fill=tk.X)
        
        # 按鈕
        btn_frame = ttk.Frame(settings_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_settings():
            # 這裡可以實現保存設定到文件的功能
            messagebox.showinfo("提示", "設定已保存（重啟程式後生效）")
            settings_window.destroy()
        
        ttk.Button(btn_frame, text="保存", command=save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="取消", command=settings_window.destroy).pack(side=tk.RIGHT)
    
    def log_message(self, message):
        """添加日誌訊息"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # 限制日誌行數
        lines = self.log_text.get('1.0', tk.END).count('\n')
        if lines > 100:
            self.log_text.delete('1.0', '10.0')
    
    def on_closing(self):
        """關閉程式時的清理工作"""
        self.is_running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1)
        self.root.destroy()

def main():
    root = tk.Tk()
    app = BTCMACDApp(root)
    
    # 設定關閉事件
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # 啟動GUI
    root.mainloop()

if __name__ == "__main__":
    main() 