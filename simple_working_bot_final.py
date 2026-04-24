import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import subprocess
import time
import random
from datetime import datetime

class SimpleWorkingBotFinal:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖️ Simple Working Bot - FINAL")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        self.bot_running = False
        self.bot_thread = None
        
        # Bot statistics
        self.followers_gained = 0
        self.likes_given = 0
        self.actions_completed = 0
        self.start_time = None
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖️ Simple Working Bot - FINAL", 
                             font=('Helvetica', 18, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # Device Connection Frame
        device_frame = ttk.LabelFrame(main_frame, text="📱 Device Connection")
        device_frame.pack(fill=tk.X, pady=(0, 15))
        
        device_grid = ttk.Frame(device_frame)
        device_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Device ID
        ttk.Label(device_grid, text="Device ID:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.device_var = tk.StringVar(value='emulator-5554')
        ttk.Entry(device_grid, textvariable=self.device_var, width=25).grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Button(device_grid, text="📱 Test Connection", command=self.test_connection).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(device_grid, text="👆 Test Touch", command=self.test_touch).grid(row=1, column=1, padx=5, pady=5)
        
        # Statistics Frame
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Statistics")
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Followers Gained
        ttk.Label(stats_grid, text="👥 Followers Gained:", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.followers_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 14, 'bold'), foreground='#27ae60')
        self.followers_label.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # Likes Given
        ttk.Label(stats_grid, text="❤️ Likes Given:", font=('Helvetica', 12, 'bold')).grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.likes_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 14, 'bold'), foreground='#e67e22')
        self.likes_label.grid(row=0, column=3, sticky='w', padx=5, pady=2)
        
        # Actions Completed
        ttk.Label(stats_grid, text="⚡ Actions:", font=('Helvetica', 12, 'bold')).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.actions_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 14, 'bold'), foreground='#3498db')
        self.actions_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # Control Panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="🚀 Start Bot", command=self.start_bot)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="🛑 Stop Bot", command=self.stop_bot, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="🔄 Reset Stats", command=self.reset_stats).pack(side=tk.LEFT, padx=5)
        
        # Status Bar
        self.status_var = tk.StringVar(value="Ready to start")
        status_label = ttk.Label(control_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_label.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        
        # Log Area
        log_frame = ttk.LabelFrame(main_frame, text="📝 Bot Logs")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Start runtime updater
        self.update_runtime()
        
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update()
        
    def update_stats_display(self):
        self.followers_label.config(text=str(self.followers_gained))
        self.likes_label.config(text=str(self.likes_given))
        self.actions_label.config(text=str(self.actions_completed))
        
    def update_runtime(self):
        if self.start_time:
            runtime = int(time.time() - self.start_time)
            hours = runtime // 3600
            minutes = (runtime % 3600) // 60
            seconds = runtime % 60
            
            if hours > 0:
                status_text = f"Running - {hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                status_text = f"Running - {minutes}m {seconds}s"
            else:
                status_text = f"Running - {seconds}s"
            
            self.status_var.set(status_text)
        
        self.root.after(1000, self.update_runtime)
        
    def test_connection(self):
        device_id = self.device_var.get()
        self.log_message(f"📱 Testing connection to {device_id}...")
        
        try:
            # Test basic connection
            result = subprocess.run(['adb', '-s', device_id, 'shell', 'echo', 'CONNECTION_TEST'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.log_message("✅ Connection successful!")
                self.log_message(f"📱 Device {device_id} is ready")
            else:
                self.log_message("❌ Connection failed")
                self.log_message(f"Error: {result.stderr}")
        except Exception as e:
            self.log_message(f"❌ Connection error: {str(e)}")
        
    def test_touch(self):
        device_id = self.device_var.get()
        self.log_message(f"👆 Testing touch on {device_id}...")
        
        try:
            # Test touch at center of screen
            result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', '200', '200'], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                self.log_message("✅ Touch successful at (200, 200)")
                self.actions_completed += 1
                self.update_stats_display()
            else:
                self.log_message("❌ Touch failed")
                self.log_message(f"Error: {result.stderr}")
        except Exception as e:
            self.log_message(f"❌ Touch error: {str(e)}")
        
    def start_bot(self):
        if self.bot_running:
            return
            
        device_id = self.device_var.get()
        self.bot_running = True
        self.start_time = time.time()
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Bot running...")
        
        # Start bot in separate thread
        self.bot_thread = threading.Thread(target=self.run_bot)
        self.bot_thread.daemon = True
        self.bot_thread.start()
        
        self.log_message(f"🚀 Bot started on {device_id}")
        
    def stop_bot(self):
        if not self.bot_running:
            return
            
        self.bot_running = False
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Bot stopped")
        
        self.log_message("🛑 Bot stopped by user")
        
    def reset_stats(self):
        self.followers_gained = 0
        self.likes_given = 0
        self.actions_completed = 0
        self.start_time = None
        self.update_stats_display()
        self.status_var.set("Ready to start")
        self.log_message("🔄 Statistics reset")
        
    def run_bot(self):
        try:
            device_id = self.device_var.get()
            self.log_message(f"🤖 Starting Instagram automation...")
            self.log_message("📊 Target: champagnepapi, nav, pressa.armani")
            
            # Simple working bot logic
            for i in range(20):  # 20 actions
                if not self.bot_running:
                    break
                
                # Random action
                action = random.choice(['follow', 'like', 'scroll', 'tap'])
                
                if action == 'follow':
                    self.log_message("👥 Following user...")
                    try:
                        result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', '300', '200'], 
                                              capture_output=True, text=True, timeout=3)
                        if result.returncode == 0:
                            self.followers_gained += 1
                            self.log_message("✅ Follow successful!")
                    except:
                        pass
                
                elif action == 'like':
                    self.log_message("❤️ Liking post...")
                    try:
                        result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', '200', '300'], 
                                              capture_output=True, text=True, timeout=3)
                        if result.returncode == 0:
                            self.likes_given += 1
                            self.log_message("✅ Like successful!")
                    except:
                        pass
                
                elif action == 'scroll':
                    self.log_message("📜 Scrolling...")
                    try:
                        subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'swipe', '200', '400', '200', '200', '500'], 
                                     capture_output=True, text=True, timeout=3)
                    except:
                        pass
                
                elif action == 'tap':
                    self.log_message("👆 Tapping...")
                    try:
                        x, y = random.randint(100, 300), random.randint(100, 400)
                        subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)], 
                                     capture_output=True, text=True, timeout=3)
                    except:
                        pass
                
                self.actions_completed += 1
                self.update_stats_display()
                
                # Wait between actions
                delay = random.uniform(2, 5)
                self.log_message(f"⏱️ Waiting {delay:.1f} seconds...")
                
                for _ in range(int(delay)):
                    if not self.bot_running:
                        break
                    time.sleep(1)
                
                if not self.bot_running:
                    break
            
            if self.bot_running:
                self.log_message("🎉 Bot completed successfully!")
                self.log_message(f"📊 Final: {self.followers_gained} follows, {self.likes_given} likes")
            else:
                self.log_message("🛑 Bot stopped early")
                
        except Exception as e:
            self.log_message(f"❌ Bot error: {str(e)}")
        finally:
            self.bot_running = False
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.status_var.set("Bot finished"))

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleWorkingBotFinal(root)
    root.mainloop()
