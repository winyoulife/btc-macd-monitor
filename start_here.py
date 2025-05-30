"""
BTC/TWD MACD 交易信號分析系統 - 主啟動器
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys

class MainLauncher:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
    def setup_window(self):
        """設定主視窗"""
        self.root.title("BTC/TWD MACD 交易信號分析系統")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 標題
        title_label = ttk.Label(main_frame, text="🚀 BTC/TWD MACD 交易信號分析系統", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 30))
        
        # 副標題
        subtitle = ttk.Label(main_frame, text="專業的虛擬貨幣技術分析工具", 
                            font=("Arial", 12))
        subtitle.pack(pady=(0, 20))
        
        # 按鈕區域
        self.create_buttons(main_frame)
        
        # 狀態區域
        self.create_status_section(main_frame)
        
        # 檢查環境
        self.check_environment()
    
    def create_buttons(self, parent):
        """建立按鈕區域"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=20)
        
        # 主要按鈕
        ttk.Button(button_frame, text="🔧 Telegram設定助手", 
                  command=self.open_telegram_setup,
                  width=25, style="Accent.TButton").pack(pady=10)
        
        ttk.Button(button_frame, text="📊 啟動主程式", 
                  command=self.launch_main_app,
                  width=25, style="Accent.TButton").pack(pady=10)
        
        # 輔助按鈕
        aux_frame = ttk.Frame(button_frame)
        aux_frame.pack(pady=(20, 0))
        
        ttk.Button(aux_frame, text="檢查環境", 
                  command=self.check_environment,
                  width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(aux_frame, text="安裝依賴", 
                  command=self.install_dependencies,
                  width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(aux_frame, text="說明文件", 
                  command=self.open_readme,
                  width=12).pack(side=tk.LEFT, padx=5)
    
    def create_status_section(self, parent):
        """建立狀態顯示區域"""
        status_frame = ttk.LabelFrame(parent, text="系統狀態", padding=15)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.status_text = tk.Text(status_frame, height=8, width=60, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def add_status(self, message, level="INFO"):
        """添加狀態訊息"""
        import datetime
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        
        if level == "ERROR":
            prefix = "❌"
        elif level == "SUCCESS":
            prefix = "✅"
        elif level == "WARNING":
            prefix = "⚠️"
        else:
            prefix = "ℹ️"
        
        self.status_text.insert(tk.END, f"[{timestamp}] {prefix} {message}\n")
        self.status_text.see(tk.END)
        self.root.update()
    
    def check_environment(self):
        """檢查環境設定"""
        self.add_status("正在檢查系統環境...")
        
        # 檢查Python版本
        python_version = sys.version_info
        if python_version >= (3, 8):
            self.add_status(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}", "SUCCESS")
        else:
            self.add_status(f"Python版本過舊: {python_version.major}.{python_version.minor}, 需要3.8+", "ERROR")
        
        # 檢查依賴套件
        required_packages = ['requests', 'pandas', 'numpy', 'matplotlib', 'telegram', 'ta']
        
        for package in required_packages:
            try:
                __import__(package)
                self.add_status(f"套件 {package}: 已安裝", "SUCCESS")
            except ImportError:
                self.add_status(f"套件 {package}: 未安裝", "WARNING")
        
        # 檢查配置文件
        try:
            from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
            if TELEGRAM_BOT_TOKEN != '請設定您的Telegram Bot Token':
                self.add_status("Telegram Bot Token: 已設定", "SUCCESS")
            else:
                self.add_status("Telegram Bot Token: 未設定", "WARNING")
                
            if TELEGRAM_CHAT_ID != '請設定您的Telegram Chat ID':
                self.add_status("Telegram Chat ID: 已設定", "SUCCESS")
            else:
                self.add_status("Telegram Chat ID: 未設定", "WARNING")
        except Exception as e:
            self.add_status(f"配置檢查失敗: {e}", "ERROR")
        
        self.add_status("環境檢查完成")
    
    def install_dependencies(self):
        """安裝依賴套件"""
        self.add_status("正在安裝依賴套件...")
        
        try:
            # 在Windows上執行安裝
            if os.name == 'nt':
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                                      capture_output=True, text=True)
            else:
                result = subprocess.run(['pip', 'install', '-r', 'requirements.txt'], 
                                      capture_output=True, text=True)
            
            if result.returncode == 0:
                self.add_status("依賴套件安裝成功", "SUCCESS")
            else:
                self.add_status(f"安裝失敗: {result.stderr}", "ERROR")
                
        except Exception as e:
            self.add_status(f"安裝錯誤: {e}", "ERROR")
    
    def open_telegram_setup(self):
        """開啟Telegram設定助手"""
        try:
            self.add_status("正在啟動Telegram設定助手...")
            subprocess.Popen([sys.executable, 'telegram_setup_helper.py'])
            self.add_status("Telegram設定助手已啟動", "SUCCESS")
        except Exception as e:
            self.add_status(f"啟動失敗: {e}", "ERROR")
            messagebox.showerror("錯誤", f"無法啟動Telegram設定助手:\n{e}")
    
    def launch_main_app(self):
        """啟動主程式"""
        try:
            # 先檢查基本設定
            from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
            
            if (TELEGRAM_BOT_TOKEN == '請設定您的Telegram Bot Token' or 
                TELEGRAM_CHAT_ID == '請設定您的Telegram Chat ID'):
                
                result = messagebox.askyesno(
                    "Telegram未設定", 
                    "檢測到Telegram尚未設定，是否繼續啟動？\n\n"
                    "• 點擊「是」: 啟動主程式（無Telegram功能）\n"
                    "• 點擊「否」: 先設定Telegram"
                )
                
                if not result:
                    self.open_telegram_setup()
                    return
            
            self.add_status("正在啟動主程式...")
            subprocess.Popen([sys.executable, 'main_gui.py'])
            self.add_status("主程式已啟動", "SUCCESS")
            
        except Exception as e:
            self.add_status(f"啟動失敗: {e}", "ERROR")
            messagebox.showerror("錯誤", f"無法啟動主程式:\n{e}")
    
    def open_readme(self):
        """開啟說明文件"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile('README.md')
            else:  # Linux/Mac
                subprocess.run(['open', 'README.md'])
            self.add_status("說明文件已開啟", "SUCCESS")
        except Exception as e:
            self.add_status(f"無法開啟說明文件: {e}", "ERROR")

def main():
    root = tk.Tk()
    
    # 設定主題樣式
    style = ttk.Style()
    style.theme_use('clam')
    
    app = MainLauncher(root)
    root.mainloop()

if __name__ == "__main__":
    main() 