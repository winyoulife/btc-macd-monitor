import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime
import threading
import pandas as pd
import numpy as np
from font_config import DISPLAY_TEXT

class MACDDetailWindow:
    def __init__(self, parent=None):
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("MACD 詳細數值視窗")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        self.current_data = None
        self.setup_ui()
        
    def setup_ui(self):
        """設定使用者界面"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 標題
        title_label = ttk.Label(main_frame, text="MACD 技術指標詳細數值", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 數值顯示區域
        self.create_value_section(main_frame)
        
        # 圖表區域
        self.create_chart_section(main_frame)
        
        # 狀態區域
        self.create_status_section(main_frame)
    
    def create_value_section(self, parent):
        """建立數值顯示區域"""
        value_frame = ttk.LabelFrame(parent, text="當前 MACD 數值", padding=15)
        value_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 使用網格布局
        grid_frame = ttk.Frame(value_frame)
        grid_frame.pack(fill=tk.X)
        
        # MACD 值
        ttk.Label(grid_frame, text="MACD 線:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.macd_var = tk.StringVar(value="--")
        self.macd_label = ttk.Label(grid_frame, textvariable=self.macd_var, 
                                   font=("Arial", 14), foreground="blue")
        self.macd_label.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Signal 值
        ttk.Label(grid_frame, text="Signal 線:", font=("Arial", 12, "bold")).grid(
            row=0, column=2, sticky=tk.W, padx=(20, 10), pady=5)
        self.signal_var = tk.StringVar(value="--")
        self.signal_label = ttk.Label(grid_frame, textvariable=self.signal_var, 
                                     font=("Arial", 14), foreground="red")
        self.signal_label.grid(row=0, column=3, sticky=tk.W, padx=10, pady=5)
        
        # Histogram 值
        ttk.Label(grid_frame, text="Histogram:", font=("Arial", 12, "bold")).grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.histogram_var = tk.StringVar(value="--")
        self.histogram_label = ttk.Label(grid_frame, textvariable=self.histogram_var, 
                                        font=("Arial", 14))
        self.histogram_label.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        # 差值
        ttk.Label(grid_frame, text="MACD-Signal:", font=("Arial", 12, "bold")).grid(
            row=1, column=2, sticky=tk.W, padx=(20, 10), pady=5)
        self.diff_var = tk.StringVar(value="--")
        self.diff_label = ttk.Label(grid_frame, textvariable=self.diff_var, 
                                   font=("Arial", 14))
        self.diff_label.grid(row=1, column=3, sticky=tk.W, padx=10, pady=5)
        
        # 更新時間
        ttk.Label(grid_frame, text="更新時間:", font=("Arial", 10)).grid(
            row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.update_time_var = tk.StringVar(value="--")
        ttk.Label(grid_frame, textvariable=self.update_time_var, font=("Arial", 10)).grid(
            row=2, column=1, columnspan=3, sticky=tk.W, padx=10, pady=(10, 0))
    
    def create_chart_section(self, parent):
        """建立圖表區域"""
        chart_frame = ttk.LabelFrame(parent, text="MACD 走勢圖", padding=10)
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 創建matplotlib圖表
        self.fig = Figure(figsize=(10, 4), dpi=100)
        self.fig.patch.set_facecolor('white')
        
        self.ax = self.fig.add_subplot(111)
        self.fig.tight_layout(pad=2.0)
        
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 初始化空圖表
        self.update_empty_chart()
    
    def create_status_section(self, parent):
        """建立狀態區域"""
        status_frame = ttk.LabelFrame(parent, text="交易信號狀態", padding=10)
        status_frame.pack(fill=tk.X)
        
        status_grid = ttk.Frame(status_frame)
        status_grid.pack(fill=tk.X)
        
        # 信號狀態
        ttk.Label(status_grid, text="當前信號:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.signal_status_var = tk.StringVar(value="持有")
        self.signal_status_label = ttk.Label(status_grid, textvariable=self.signal_status_var, 
                                            font=("Arial", 12, "bold"))
        self.signal_status_label.grid(row=0, column=1, sticky=tk.W, padx=10)
        
        # 信號強度
        ttk.Label(status_grid, text="信號強度:", font=("Arial", 10, "bold")).grid(
            row=0, column=2, sticky=tk.W, padx=(20, 10))
        self.strength_var = tk.StringVar(value="0%")
        ttk.Label(status_grid, textvariable=self.strength_var, font=("Arial", 12)).grid(
            row=0, column=3, sticky=tk.W, padx=10)
        
        # 信心度
        ttk.Label(status_grid, text="信心度:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.confidence_var = tk.StringVar(value="0%")
        ttk.Label(status_grid, textvariable=self.confidence_var, font=("Arial", 12)).grid(
            row=1, column=1, sticky=tk.W, padx=10, pady=(5, 0))
    
    def update_empty_chart(self):
        """更新空圖表"""
        self.ax.clear()
        self.ax.text(0.5, 0.5, '等待數據...', ha='center', va='center', 
                    transform=self.ax.transAxes, fontsize=14)
        self.ax.set_title(DISPLAY_TEXT['macd_indicator'], fontsize=12, fontweight='bold')
        self.canvas.draw()
    
    def update_data(self, macd_data, signal_data=None):
        """更新數據顯示"""
        try:
            if macd_data is None:
                return
            
            self.current_data = macd_data
            
            # 獲取最新數值
            latest = macd_data.iloc[-1]
            macd_val = latest['macd'] if not pd.isna(latest['macd']) else 0
            signal_val = latest['macd_signal'] if not pd.isna(latest['macd_signal']) else 0
            histogram_val = latest['macd_histogram'] if not pd.isna(latest['macd_histogram']) else 0
            diff_val = macd_val - signal_val
            
            # 更新數值顯示
            self.macd_var.set(f"{macd_val:.6f}")
            self.signal_var.set(f"{signal_val:.6f}")
            self.histogram_var.set(f"{histogram_val:.6f}")
            self.diff_var.set(f"{diff_val:.6f}")
            self.update_time_var.set(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # 更新顏色
            self.histogram_label.config(foreground="green" if histogram_val > 0 else "red")
            self.diff_label.config(foreground="green" if diff_val > 0 else "red")
            
            # 更新信號狀態
            if signal_data:
                signal_type = signal_data.get('signal', 'HOLD')
                strength = signal_data.get('strength', 0)
                confidence = signal_data.get('confidence', 0)
                
                # 設定信號顯示
                if signal_type == 'BUY':
                    self.signal_status_var.set("買入 🚀")
                    self.signal_status_label.config(foreground="green")
                elif signal_type == 'SELL':
                    self.signal_status_var.set("賣出 📉")
                    self.signal_status_label.config(foreground="red")
                else:
                    self.signal_status_var.set("持有 ⏸️")
                    self.signal_status_label.config(foreground="gray")
                
                self.strength_var.set(f"{strength}%")
                self.confidence_var.set(f"{confidence}%")
            
            # 更新圖表
            self.update_chart(macd_data)
            
        except Exception as e:
            print(f"更新數據失敗: {e}")
    
    def update_chart(self, macd_data):
        """更新MACD圖表"""
        try:
            self.ax.clear()
            
            # 取最近50個點或全部數據
            data_to_plot = macd_data.tail(50) if len(macd_data) > 50 else macd_data
            x_range = range(len(data_to_plot))
            
            # 繪製MACD線和Signal線
            self.ax.plot(x_range, data_to_plot['macd'], 
                        label=DISPLAY_TEXT['macd'], color='blue', linewidth=2)
            self.ax.plot(x_range, data_to_plot['macd_signal'], 
                        label=DISPLAY_TEXT['signal'], color='red', linewidth=2)
            
            # 繪製Histogram柱狀圖
            colors = ['green' if x > 0 else 'red' for x in data_to_plot['macd_histogram']]
            self.ax.bar(x_range, data_to_plot['macd_histogram'], 
                       label=DISPLAY_TEXT['histogram'], color=colors, alpha=0.6, width=0.8)
            
            # 添加零線
            self.ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            # 設定標題和標籤
            self.ax.set_title(DISPLAY_TEXT['macd_indicator'], fontsize=12, fontweight='bold')
            self.ax.legend(loc='upper left')
            self.ax.grid(True, alpha=0.3)
            
            # 設定x軸標籤
            if len(data_to_plot) > 10:
                step = max(1, len(data_to_plot) // 10)
                x_labels = [data_to_plot.iloc[i]['timestamp'].strftime('%H:%M') 
                           for i in range(0, len(data_to_plot), step)]
                x_positions = list(range(0, len(data_to_plot), step))
                self.ax.set_xticks(x_positions)
                self.ax.set_xticklabels(x_labels, rotation=45)
            
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"更新圖表失敗: {e}")
    
    def show(self):
        """顯示視窗"""
        self.window.deiconify()
        self.window.lift()
    
    def hide(self):
        """隱藏視窗"""
        self.window.withdraw()
    
    def destroy(self):
        """銷毀視窗"""
        self.window.destroy()

def main():
    """測試用主函數"""
    # 創建測試數據
    dates = pd.date_range(start='2025-01-01', periods=100, freq='H')
    test_data = pd.DataFrame({
        'timestamp': dates,
        'close': 100 + np.cumsum(np.random.randn(100) * 0.5),
        'macd': np.random.randn(100) * 2,
        'macd_signal': np.random.randn(100) * 1.5,
        'macd_histogram': np.random.randn(100) * 0.5
    })
    
    # 測試視窗
    root = tk.Tk()
    root.withdraw()  # 隱藏主視窗
    
    detail_window = MACDDetailWindow()
    detail_window.update_data(test_data)
    
    root.mainloop()

if __name__ == "__main__":
    main() 