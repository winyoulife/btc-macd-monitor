"""
Telegram Bot 設定助手
幫助用戶設定Telegram Bot Token 和 Chat ID
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import webbrowser
import asyncio
from telegram import Bot
import threading

class TelegramSetupHelper:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
    def setup_window(self):
        """設定視窗"""
        self.root.title("Telegram Bot 設定助手")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 標題
        title_label = ttk.Label(main_frame, text="Telegram Bot 設定助手", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 步驟說明
        self.create_instructions(main_frame)
        
        # 輸入框
        self.create_input_section(main_frame)
        
        # 按鈕
        self.create_buttons(main_frame)
        
        # 測試結果
        self.create_result_section(main_frame)
    
    def create_instructions(self, parent):
        """建立說明文字"""
        instructions_frame = ttk.LabelFrame(parent, text="設定步驟", padding=10)
        instructions_frame.pack(fill=tk.X, pady=(0, 20))
        
        instructions = """
1. 建立Telegram Bot:
   • 在Telegram中搜尋 @BotFather
   • 發送 /newbot 命令
   • 按照指示設定Bot名稱和用戶名
   • 複製獲得的Bot Token

2. 獲取Chat ID:
   • 與你建立的Bot開始對話
   • 發送任意訊息給Bot
   • 點擊下方"獲取Chat ID"按鈕
   • 從結果中找到你的Chat ID

3. 測試連接:
   • 在下方輸入Bot Token和Chat ID
   • 點擊"測試連接"確認設定正確
        """
        
        text_widget = tk.Text(instructions_frame, height=12, width=70, wrap=tk.WORD)
        text_widget.insert('1.0', instructions)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack()
    
    def create_input_section(self, parent):
        """建立輸入區域"""
        input_frame = ttk.LabelFrame(parent, text="Bot 設定", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Bot Token
        ttk.Label(input_frame, text="Bot Token:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.token_var = tk.StringVar()
        self.token_entry = ttk.Entry(input_frame, textvariable=self.token_var, 
                                    width=50, show="*")
        self.token_entry.grid(row=0, column=1, padx=(10, 0), pady=5)
        
        # Chat ID
        ttk.Label(input_frame, text="Chat ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.chat_id_var = tk.StringVar()
        self.chat_id_entry = ttk.Entry(input_frame, textvariable=self.chat_id_var, width=20)
        self.chat_id_entry.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 獲取Chat ID按鈕
        ttk.Button(input_frame, text="獲取Chat ID", 
                  command=self.get_chat_id).grid(row=1, column=2, padx=(10, 0))
    
    def create_buttons(self, parent):
        """建立按鈕區域"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Button(button_frame, text="開啟BotFather", 
                  command=self.open_botfather).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="測試連接", 
                  command=self.test_connection).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="保存設定", 
                  command=self.save_config).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="關閉", 
                  command=self.root.destroy).pack(side=tk.RIGHT)
    
    def create_result_section(self, parent):
        """建立結果顯示區域"""
        result_frame = ttk.LabelFrame(parent, text="測試結果", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=8, width=70)
        self.result_text.pack(fill=tk.BOTH, expand=True)
    
    def open_botfather(self):
        """開啟BotFather"""
        webbrowser.open("https://t.me/botfather")
        self.add_result("已開啟BotFather，請按照說明建立Bot")
    
    def get_chat_id(self):
        """獲取Chat ID"""
        token = self.token_var.get().strip()
        if not token:
            messagebox.showerror("錯誤", "請先輸入Bot Token")
            return
        
        def get_updates():
            try:
                url = f"https://api.telegram.org/bot{token}/getUpdates"
                webbrowser.open(url)
                self.add_result("已開啟瀏覽器顯示更新資訊")
                self.add_result("請在JSON回應中找到 'chat' -> 'id' 的數值")
                self.add_result("範例: \"chat\":{\"id\":123456789,...}")
            except Exception as e:
                self.add_result(f"開啟失敗: {e}")
        
        threading.Thread(target=get_updates, daemon=True).start()
    
    def test_connection(self):
        """測試Telegram連接"""
        token = self.token_var.get().strip()
        chat_id = self.chat_id_var.get().strip()
        
        if not token or not chat_id:
            messagebox.showerror("錯誤", "請輸入Bot Token和Chat ID")
            return
        
        def test_task():
            try:
                self.add_result("正在測試連接...")
                
                # 建立Bot並測試
                bot = Bot(token=token)
                
                # 異步測試
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def test_bot():
                    # 獲取Bot資訊
                    bot_info = await bot.get_me()
                    self.add_result(f"✓ Bot連接成功: {bot_info.username}")
                    
                    # 發送測試訊息
                    test_message = f"🤖 測試訊息\nBot: {bot_info.username}\n時間: {asyncio.get_event_loop().time()}"
                    await bot.send_message(chat_id=chat_id, text=test_message)
                    self.add_result("✓ 測試訊息發送成功!")
                    
                    return True
                
                success = loop.run_until_complete(test_bot())
                loop.close()
                
                if success:
                    self.add_result("🎉 Telegram設定完成!")
                    messagebox.showinfo("成功", "Telegram連接測試成功!\n請檢查是否收到測試訊息。")
                
            except Exception as e:
                self.add_result(f"❌ 測試失敗: {e}")
                messagebox.showerror("失敗", f"連接測試失敗:\n{e}")
        
        threading.Thread(target=test_task, daemon=True).start()
    
    def save_config(self):
        """保存設定到config.py"""
        token = self.token_var.get().strip()
        chat_id = self.chat_id_var.get().strip()
        
        if not token or not chat_id:
            messagebox.showerror("錯誤", "請輸入Bot Token和Chat ID")
            return
        
        try:
            # 讀取現有config.py
            with open('config.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替換Token和Chat ID
            import re
            content = re.sub(
                r"TELEGRAM_BOT_TOKEN = .*",
                f"TELEGRAM_BOT_TOKEN = '{token}'",
                content
            )
            content = re.sub(
                r"TELEGRAM_CHAT_ID = .*",
                f"TELEGRAM_CHAT_ID = '{chat_id}'",
                content
            )
            
            # 寫入文件
            with open('config.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.add_result("✓ 設定已保存到config.py")
            messagebox.showinfo("成功", "設定已保存!\n現在可以啟動主程式了。")
            
        except Exception as e:
            self.add_result(f"❌ 保存失敗: {e}")
            messagebox.showerror("錯誤", f"保存設定失敗:\n{e}")
    
    def add_result(self, message):
        """添加結果訊息"""
        import datetime
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        self.result_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.result_text.see(tk.END)
        self.root.update()

def main():
    root = tk.Tk()
    app = TelegramSetupHelper(root)
    root.mainloop()

if __name__ == "__main__":
    main() 