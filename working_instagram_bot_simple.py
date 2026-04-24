import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import subprocess
import time
from datetime import datetime

class WorkingInstagramBotSimple:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖️ Working Instagram Bot - Simple")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        self.bot_running = False
        self.bot_thread = None
        
        # Statistics
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
        title_label = ttk.Label(main_frame, text="🤖️ Working Instagram Bot - Simple", 
                             font=('Helvetica', 18, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # Device Frame
        device_frame = ttk.LabelFrame(main_frame, text="📱 Device Settings")
        device_frame.pack(fill=tk.X, pady=(0, 15))
        
        device_grid = ttk.Frame(device_frame)
        device_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Device ID
        ttk.Label(device_grid, text="Device ID:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.device_var = tk.StringVar(value='')
        ttk.Entry(device_grid, textvariable=self.device_var, width=25).grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Button(device_grid, text="📱 List Devices", command=self.list_devices).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(device_grid, text="📱 Open Instagram", command=self.open_instagram).grid(row=1, column=1, padx=5, pady=5)
        
        # Target
        ttk.Label(device_grid, text="Target:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.target_var = tk.StringVar(value='champagnepapi')
        ttk.Entry(device_grid, textvariable=self.target_var, width=25).grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        
        # Statistics Frame
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Statistics")
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(stats_grid, text="👥 Followers:", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.followers_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 14, 'bold'), foreground='#27ae60')
        self.followers_label.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(stats_grid, text="❤️ Likes:", font=('Helvetica', 12, 'bold')).grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.likes_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 14, 'bold'), foreground='#e67e22')
        self.likes_label.grid(row=0, column=3, sticky='w', padx=5, pady=2)
        
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
        
        ttk.Button(control_frame, text="🔄 Reset", command=self.reset_stats).pack(side=tk.LEFT, padx=5)
        
        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(control_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_label.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        
        # Log Area
        log_frame = ttk.LabelFrame(main_frame, text="📝 Logs")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
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
                status_text = f"Running - {hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                status_text = f"Running - {minutes}m {seconds}s"
            else:
                status_text = f"Running - {seconds}s"
            
            self.status_var.set(status_text)
        
        self.root.after(1000, self.update_runtime)
        
    def list_devices(self):
        self.log_message("📱 Listing devices...")
        
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_message("✅ Devices found:")
                devices = result.stdout.strip().split('\n')[1:]
                for device in devices:
                    if device.strip():
                        self.log_message(f"   📱 {device.strip()}")
                        if not self.device_var.get():
                            device_id = device.strip().split()[0]
                            self.device_var.set(device_id)
                            self.log_message(f"✅ Selected: {device_id}")
            else:
                self.log_message("❌ No devices")
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
        
    def open_instagram(self):
        device_id = self.device_var.get()
        if not device_id:
            self.log_message("❌ No device selected")
            return
        
        self.log_message(f"📱 Opening Instagram on {device_id}...")
        
        try:
            # Stop Instagram first
            subprocess.run(['adb', '-s', device_id, 'shell', 'am', 'force-stop', 'com.instagram.android'], 
                         capture_output=True, text=True, timeout=5)
            time.sleep(1)
            
            # Start Instagram
            result = subprocess.run(['adb', '-s', device_id, 'shell', 'monkey', '-p', 'com.instagram.android', '-c', 
                                   'android.intent.category.LAUNCHER', '1'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.log_message("✅ Instagram opened!")
                time.sleep(5)
            else:
                self.log_message(f"❌ Failed to open Instagram")
                
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
        
    def start_bot(self):
        if self.bot_running:
            return
            
        device_id = self.device_var.get()
        if not device_id:
            self.log_message("❌ Please select device first")
            return
        
        self.bot_running = True
        self.start_time = time.time()
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Running...")
        
        self.bot_thread = threading.Thread(target=self.run_bot)
        self.bot_thread.daemon = True
        self.bot_thread.start()
        
        self.log_message("🚀 Bot started!")
        
    def stop_bot(self):
        if not self.bot_running:
            return
            
        self.bot_running = False
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Stopped")
        
        self.log_message("🛑 Bot stopped")
        
    def reset_stats(self):
        self.followers_gained = 0
        self.likes_given = 0
        self.actions_completed = 0
        self.start_time = None
        self.update_stats_display()
        self.status_var.set("Ready")
        self.log_message("🔄 Stats reset")
        
    def run_bot(self):
        try:
            device_id = self.device_var.get()
            target = self.target_var.get()
            
            self.log_message(f"🤖 Starting automation for @{target}")
            
            # Open Instagram first
            self.open_instagram()
            
            # Simple automation sequence
            self.log_message("🔍 Searching for user...")
            
            # Try to tap search bar
            search_positions = [(200, 120), (180, 100), (220, 100)]
            for x, y in search_positions:
                self.log_message(f"👆 Tapping search at ({x}, {y})")
                result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)], 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    self.log_message("✅ Search bar tapped")
                    self.actions_completed += 1
                    break
                time.sleep(1)
            
            time.sleep(2)
            
            # Type username
            self.log_message(f"⌨️ Typing {target}...")
            result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'text', target], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                self.log_message("✅ Username typed")
                self.actions_completed += 1
            
            time.sleep(2)
            
            # Press enter
            self.log_message("⏎ Pressing enter...")
            result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'keyevent', 'KEYCODE_ENTER'], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                self.log_message("✅ Enter pressed")
                self.actions_completed += 1
            
            time.sleep(3)
            
            # Tap on user result
            self.log_message("👆 Tapping user result...")
            result_positions = [(200, 250), (200, 300), (200, 350)]
            for x, y in result_positions:
                self.log_message(f"👆 Trying result at ({x}, {y})")
                result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)], 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    self.log_message("✅ User result tapped")
                    self.actions_completed += 1
                    break
                time.sleep(1)
            
            time.sleep(4)
            
            # Try to follow
            self.log_message("👥 Looking for follow button...")
            follow_positions = [(500, 200), (450, 180), (480, 220)]
            for x, y in follow_positions:
                self.log_message(f"👆 Trying follow at ({x}, {y})")
                result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)], 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    self.log_message("✅ Follow button tapped!")
                    self.followers_gained += 1
                    self.actions_completed += 1
                    break
                time.sleep(1)
            
            time.sleep(3)
            
            # Try to like some posts
            self.log_message("❤️ Looking for posts to like...")
            for i in range(3):
                if not self.bot_running:
                    break
                
                # Scroll down
                self.log_message(f"📜 Scroll {i+1}")
                result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'swipe', '200', '400', '200', '200', '500'], 
                                      capture_output=True, text=True, timeout=3)
                time.sleep(2)
                
                # Try to like a post
                self.log_message(f"❤️ Like attempt {i+1}")
                like_positions = [(200, 300), (250, 350), (300, 400)]
                for x, y in like_positions:
                    result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)], 
                                          capture_output=True, text=True, timeout=3)
                    if result.returncode == 0:
                        # Double tap to like
                        time.sleep(0.5)
                        result2 = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)], 
                                              capture_output=True, text=True, timeout=3)
                        if result2.returncode == 0:
                            self.log_message("✅ Post liked!")
                            self.likes_given += 1
                            self.actions_completed += 1
                            break
                    time.sleep(1)
                    break
                
                time.sleep(2)
            
            self.update_stats_display()
            self.log_message("🎉 Automation completed!")
            
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
        finally:
            self.bot_running = False
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.status_var.set("Finished"))

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkingInstagramBotSimple(root)
    root.mainloop()
