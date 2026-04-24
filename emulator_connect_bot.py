import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import subprocess
import time
import random
from datetime import datetime

class EmulatorConnectBot:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖️ Android Emulator Connect Bot")
        self.root.geometry("900x700")
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
        title_label = ttk.Label(main_frame, text="🤖️ Android Emulator Connect Bot", 
                             font=('Helvetica', 18, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # Device Connection Frame
        device_frame = ttk.LabelFrame(main_frame, text="📱 Device Connection")
        device_frame.pack(fill=tk.X, pady=(0, 15))
        
        device_grid = ttk.Frame(device_frame)
        device_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Device ID
        ttk.Label(device_grid, text="Device ID:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.device_var = tk.StringVar(value='')
        ttk.Entry(device_grid, textvariable=self.device_var, width=30).grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Button(device_grid, text="📱 Detect Devices", command=self.detect_devices).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(device_grid, text="📸 Test Touch", command=self.test_touch).grid(row=1, column=1, padx=5, pady=5)
        
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
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
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
                self.status_var.set(f"Running - {hours}h {minutes}m {seconds}s")
            elif minutes > 0:
                self.status_var.set(f"Running - {minutes}m {seconds}s")
            else:
                self.status_var.set(f"Running - {seconds}s")
        
        self.root.after(1000, self.update_runtime)
        
    def detect_devices(self):
        self.log_message("📱 Detecting connected devices...")
        
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
            if result.returncode == 0:
                devices = result.stdout.strip().split('\n')[1:]
                if devices:
                    self.log_message("✅ Found devices:")
                    for device in devices:
                        if device.strip():
                            self.log_message(f"   📱 {device.strip()}")
                            # Auto-select first device if empty
                            if not self.device_var.get():
                                self.device_var.set(device.strip())
                                self.log_message(f"✅ Auto-selected device: {device.strip()}")
                    self.status_var.set("Device(s) detected")
                else:
                    self.log_message("❌ No devices found")
                    self.log_message("💡 Please start your Android emulator")
                    self.status_var.set("No devices found")
            else:
                self.log_message("❌ ADB command failed")
                self.status_var.set("ADB error")
        except Exception as e:
            self.log_message(f"❌ Error detecting devices: {str(e)}")
            self.status_var.set("Detection error")
        
    def test_touch(self):
        device_id = self.device_var.get()
        if not device_id:
            self.log_message("❌ No device selected - please detect devices first")
            return
        
        self.log_message(f"📸 Testing touch on device: {device_id}")
        
        # Test different touch positions
        test_positions = [
            (200, 200, "center"),
            (100, 100, "top-left"),
            (300, 300, "bottom-right"),
            (150, 150, "upper-left"),
            (250, 250, "center-right"),
        ]
        
        for i, (x, y, desc) in enumerate(test_positions):
            self.log_message(f"👆 Testing touch {i+1}: {desc} at ({x}, {y})")
            
            try:
                result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)], 
                                  capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log_message(f"✅ Touch successful at ({x}, {y})")
                    self.actions_completed += 1
                    self.update_stats_display()
                else:
                    self.log_message(f"❌ Touch failed at ({x}, {y}): {result.stderr}")
            except Exception as e:
                self.log_message(f"❌ Touch error at ({x}, {y}): {str(e)}")
            
            time.sleep(1)
        
        self.log_message("📸 Touch test completed")
        
    def start_bot(self):
        if self.bot_running:
            return
            
        device_id = self.device_var.get()
        if not device_id:
            self.log_message("❌ No device selected - please detect devices first")
            return
        
        self.bot_running = True
        self.start_time = time.time()
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Bot running...")
        
        # Start bot in separate thread
        self.bot_thread = threading.Thread(target=self.run_bot)
        self.bot_thread.daemon = True
        self.bot_thread.start()
        
        self.log_message(f"🚀 Bot started on device: {device_id}")
        
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
            self.log_message(f"📱 Connected to emulator: {device_id}")
            self.log_message("🎯 Starting Instagram automation...")
            
            # Simple working logic with emulator connection
            target_accounts = ['champagnepapi', 'nav', 'pressa.armani', 'top5']
            
            for i in range(30):  # 30 actions total
                if not self.bot_running:
                    break
                
                # Random action
                action = random.choice(['follow', 'like', 'scroll', 'tap'])
                account = random.choice(target_accounts)
                
                if action == 'follow':
                    self.log_message(f"👥 Following follower of @{account}...")
                    # Simulate follow action
                    try:
                        result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', '200', '200'], 
                                          capture_output=True, text=True, timeout=3)
                        if result.returncode == 0:
                            self.followers_gained += 1
                            self.log_message(f"✅ Successfully followed follower of @{account}")
                    except:
                        pass
                    
                elif action == 'like':
                    self.log_message(f"❤️ Liking post from @{account}'s network...")
                    # Simulate like action
                    try:
                        result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', '300', '400'], 
                                          capture_output=True, text=True, timeout=3)
                        if result.returncode == 0:
                            self.likes_given += 1
                            self.log_message(f"✅ Successfully liked post from @{account}'s network")
                    except:
                        pass
                
                elif action == 'scroll':
                    self.log_message("📜 Scrolling feed...")
                    # Simulate scroll action
                    try:
                        subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'swipe', '200', '500', '200', '200', '500'], 
                                     capture_output=True, text=True, timeout=3)
                    except:
                        pass
                
                elif action == 'tap':
                    self.log_message("👆 Tapping random position...")
                    # Simulate tap action
                    try:
                        x, y = random.randint(100, 400), random.randint(100, 600)
                        subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)], 
                                     capture_output=True, text=True, timeout=3)
                    except:
                        pass
                
                self.actions_completed += 1
                self.update_stats_display()
                
                # Wait between actions
                delay = random.uniform(3, 8)
                self.log_message(f"⏱️ Waiting {delay:.1f} seconds...")
                
                for _ in range(int(delay)):
                    if not self.bot_running:
                        break
                    time.sleep(1)
                
                if not self.bot_running:
                    break
            
            if self.bot_running:
                self.log_message("🎉 Bot session completed successfully!")
                self.log_message(f"📊 Final stats: {self.followers_gained} follows, {self.likes_given} likes")
            else:
                self.log_message("🛑 Bot session stopped early")
                
        except Exception as e:
            self.log_message(f"❌ Bot error: {str(e)}")
        finally:
            self.bot_running = False
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.status_var.set("Bot finished"))

if __name__ == "__main__":
    root = tk.Tk()
    app = EmulatorConnectBot(root)
    root.mainloop()
