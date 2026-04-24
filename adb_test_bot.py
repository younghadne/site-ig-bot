import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import subprocess
import time
import random
from datetime import datetime

class ADBTestBot:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖️ ADB Test Bot")
        self.root.geometry("900x750")
        self.root.configure(bg='#2c3e50')
        
        self.bot_running = False
        self.bot_thread = None
        
        # Bot statistics
        self.touches_successful = 0
        self.touches_failed = 0
        self.commands_successful = 0
        self.start_time = None
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖️ ADB Test & Fix Bot", 
                             font=('Helvetica', 18, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # ADB Test Frame
        test_frame = ttk.LabelFrame(main_frame, text="🧪 ADB Connection Test")
        test_frame.pack(fill=tk.X, pady=(0, 15))
        
        test_grid = ttk.Frame(test_frame)
        test_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Device ID
        ttk.Label(test_grid, text="Device ID:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.device_var = tk.StringVar(value='')
        ttk.Entry(test_grid, textvariable=self.device_var, width=30).grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        # Test buttons
        ttk.Button(test_grid, text="📱 List Devices", command=self.list_devices).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(test_grid, text="🧪 Test ADB Basic", command=self.test_adb_basic).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(test_grid, text="👆 Test Input Commands", command=self.test_input_commands).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(test_grid, text="📸 Test Different Touch", command=self.test_different_touch).grid(row=2, column=1, padx=5, pady=5)
        
        # Statistics Frame
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Test Results")
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Touch Success
        ttk.Label(stats_grid, text="✅ Touch Success:", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.touch_success_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 14, 'bold'), foreground='#27ae60')
        self.touch_success_label.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # Touch Failed
        ttk.Label(stats_grid, text="❌ Touch Failed:", font=('Helvetica', 12, 'bold')).grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.touch_fail_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 14, 'bold'), foreground='#e74c3c')
        self.touch_fail_label.grid(row=0, column=3, sticky='w', padx=5, pady=2)
        
        # Commands Success
        ttk.Label(stats_grid, text="🔧 Commands Success:", font=('Helvetica', 12, 'bold')).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.command_success_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 14, 'bold'), foreground='#3498db')
        self.command_success_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # Control Panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="🚀 Start Bot", command=self.start_bot)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="🛑 Stop Bot", command=self.stop_bot, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="🔄 Reset Stats", command=self.reset_stats).pack(side=tk.LEFT, padx=5)
        
        # Status Bar
        self.status_var = tk.StringVar(value="Ready to test ADB")
        status_label = ttk.Label(control_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_label.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        
        # Log Area
        log_frame = ttk.LabelFrame(main_frame, text="📝 Test Logs")
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
        self.touch_success_label.config(text=str(self.touches_successful))
        self.touch_fail_label.config(text=str(self.touches_failed))
        self.command_success_label.config(text=str(self.commands_successful))
        
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
        
    def list_devices(self):
        self.log_message("📱 Listing all connected devices...")
        
        try:
            result = subprocess.run(['adb', 'devices', '-l'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_message("✅ Device list:")
                devices = result.stdout.strip().split('\n')
                for device in devices:
                    if device.strip():
                        self.log_message(f"   📱 {device.strip()}")
                        # Extract device ID properly
                        device_parts = device.strip().split()
                        if device_parts and not self.device_var.get():
                            actual_device_id = device_parts[0]  # Take first part before any whitespace
                            self.device_var.set(actual_device_id)
                            self.log_message(f"✅ Auto-selected device: {actual_device_id}")
            else:
                self.log_message("❌ Failed to list devices")
        except Exception as e:
            self.log_message(f"❌ Error listing devices: {str(e)}")
        
    def test_adb_basic(self):
        device_id = self.device_var.get()
        if not device_id:
            self.log_message("❌ No device selected")
            return
        
        self.log_message(f"🧪 Testing basic ADB connection to {device_id}...")
        
        # Test basic ADB commands
        tests = [
            (['shell', 'echo', 'ADB_TEST'], "echo command"),
            (['shell', 'getprop', 'ro.product.model'], "get device model"),
            (['shell', 'wm', 'size'], "get screen size"),
            (['shell', 'dumpsys', 'window', 'windows'], "get window info"),
        ]
        
        for cmd, desc in tests:
            try:
                self.log_message(f"🔧 Testing: {desc}")
                result = subprocess.run(['adb', '-s', device_id] + cmd, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log_message(f"✅ {desc} SUCCESS")
                    self.commands_successful += 1
                else:
                    self.log_message(f"❌ {desc} FAILED: {result.stderr}")
            except Exception as e:
                self.log_message(f"❌ {desc} ERROR: {str(e)}")
            
            time.sleep(1)
        
        self.update_stats_display()
        
    def test_input_commands(self):
        device_id = self.device_var.get()
        if not device_id:
            self.log_message("❌ No device selected")
            return
        
        self.log_message(f"👆 Testing different input methods on {device_id}...")
        
        # Test different input methods
        input_tests = [
            (['shell', 'input', 'keyevent', 'KEYCODE_HOME'], "HOME button"),
            (['shell', 'input', 'keyevent', 'KEYCODE_BACK'], "BACK button"),
            (['shell', 'input', 'keyevent', 'KEYCODE_MENU'], "MENU button"),
            (['shell', 'input', 'text', 'TEST_TEXT'], "TEXT input"),
            (['shell', 'input', 'tap', '200', '200'], "TAP at center"),
        ]
        
        for cmd, desc in input_tests:
            try:
                self.log_message(f"👆 Testing: {desc}")
                result = subprocess.run(['adb', '-s', device_id] + cmd, capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    self.log_message(f"✅ {desc} SUCCESS")
                    self.commands_successful += 1
                else:
                    self.log_message(f"❌ {desc} FAILED: {result.stderr}")
            except Exception as e:
                self.log_message(f"❌ {desc} ERROR: {str(e)}")
            
            time.sleep(2)
        
        self.update_stats_display()
        
    def test_different_touch(self):
        device_id = self.device_var.get()
        if not device_id:
            self.log_message("❌ No device selected")
            return
        
        self.log_message(f"📸 Testing different touch methods on {device_id}...")
        
        # Test different touch methods and positions
        touch_tests = [
            (['shell', 'input', 'tap', '100', '100'], "TOP-LEFT"),
            (['shell', 'input', 'tap', '300', '100'], "TOP-RIGHT"),
            (['shell', 'input', 'tap', '100', '400'], "BOTTOM-LEFT"),
            (['shell', 'input', 'tap', '300', '400'], "BOTTOM-RIGHT"),
            (['shell', 'input', 'tap', '200', '250'], "CENTER"),
            (['shell', 'input', 'swipe', '200', '400', '200', '200', '500'], "SCROLL-DOWN"),
            (['shell', 'input', 'swipe', '200', '200', '200', '400', '500'], "SCROLL-UP"),
        ]
        
        for cmd, desc in touch_tests:
            try:
                self.log_message(f"📸 Testing: {desc}")
                result = subprocess.run(['adb', '-s', device_id] + cmd, capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    self.log_message(f"✅ {desc} SUCCESS")
                    self.touches_successful += 1
                else:
                    self.log_message(f"❌ {desc} FAILED: {result.stderr}")
                    self.touches_failed += 1
            except Exception as e:
                self.log_message(f"❌ {desc} ERROR: {str(e)}")
                self.touches_failed += 1
            
            time.sleep(1)
        
        self.update_stats_display()
        
    def start_bot(self):
        if self.bot_running:
            return
            
        device_id = self.device_var.get()
        if not device_id:
            self.log_message("❌ No device selected - please test ADB first")
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
        self.touches_successful = 0
        self.touches_failed = 0
        self.commands_successful = 0
        self.start_time = None
        self.update_stats_display()
        self.status_var.set("Ready to test ADB")
        self.log_message("🔄 Statistics reset")
        
    def run_bot(self):
        try:
            device_id = self.device_var.get()
            self.log_message(f"🤖 Starting simple bot on {device_id}...")
            
            # Very simple bot - just test basic commands
            actions = [
                (['shell', 'input', 'tap', '200', '200'], "TAP CENTER"),
                (['shell', 'input', 'swipe', '200', '400', '200', '200', '500'], "SCROLL DOWN"),
                (['shell', 'input', 'text', 'instagram'], "TYPE INSTAGRAM"),
                (['shell', 'input', 'keyevent', 'KEYCODE_ENTER'], "PRESS ENTER"),
                (['shell', 'input', 'tap', '300', '300'], "TAP RIGHT"),
                (['shell', 'input', 'keyevent', 'KEYCODE_BACK'], "GO BACK"),
            ]
            
            for i, (cmd, desc) in enumerate(actions):
                if not self.bot_running:
                    break
                
                self.log_message(f"⚡ Action {i+1}: {desc}")
                
                try:
                    result = subprocess.run(['adb', '-s', device_id] + cmd, capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        self.log_message(f"✅ {desc} SUCCESS")
                        self.commands_successful += 1
                    else:
                        self.log_message(f"❌ {desc} FAILED")
                except Exception as e:
                    self.log_message(f"❌ {desc} ERROR: {str(e)}")
                
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
                self.log_message("🎉 Bot test completed!")
                self.log_message(f"📊 Results: {self.commands_successful} commands successful")
            else:
                self.log_message("🛑 Bot test stopped early")
                
        except Exception as e:
            self.log_message(f"❌ Bot error: {str(e)}")
        finally:
            self.bot_running = False
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.status_var.set("Test finished"))

if __name__ == "__main__":
    root = tk.Tk()
    app = ADBTestBot(root)
    root.mainloop()
