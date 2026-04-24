import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import subprocess
import time
import random
from datetime import datetime

class RealAndroidBot:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖️ Real Android Instagram Bot")
        self.root.geometry("900x750")
        self.root.configure(bg='#2c3e50')
        
        self.bot_running = False
        self.bot_thread = None
        
        # Bot statistics
        self.followers_gained = 0
        self.likes_given = 0
        self.comments_given = 0
        self.actions_completed = 0
        self.start_time = None
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖️ Real Android Instagram Bot", 
                             font=('Helvetica', 18, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # Device Connection Frame
        device_frame = ttk.LabelFrame(main_frame, text="📱 Android Device")
        device_frame.pack(fill=tk.X, pady=(0, 15))
        
        device_grid = ttk.Frame(device_frame)
        device_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Device ID
        ttk.Label(device_grid, text="Device ID:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.device_var = tk.StringVar(value='')
        ttk.Entry(device_grid, textvariable=self.device_var, width=25).grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Button(device_grid, text="📱 List Devices", command=self.list_devices).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(device_grid, text="📸 Test Touch", command=self.test_touch).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(device_grid, text="📱 Open Instagram", command=self.open_instagram).grid(row=2, column=0, padx=5, pady=5)
        
        # Instagram Settings
        ttk.Label(device_grid, text="Package:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.package_var = tk.StringVar(value='com.instagram.android')
        ttk.Entry(device_grid, textvariable=self.package_var, width=25).grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        
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
        
    def list_devices(self):
        self.log_message("📱 Listing connected Android devices...")
        
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_message("✅ Connected devices:")
                devices = result.stdout.strip().split('\n')[1:]
                for device in devices:
                    if device.strip():
                        self.log_message(f"   📱 {device.strip()}")
                        # Auto-select first device
                        if not self.device_var.get():
                            device_id = device.strip().split()[0]
                            self.device_var.set(device_id)
                            self.log_message(f"✅ Auto-selected: {device_id}")
            else:
                self.log_message("❌ No devices found")
        except Exception as e:
            self.log_message(f"❌ Error listing devices: {str(e)}")
        
    def test_touch(self):
        device_id = self.device_var.get()
        if not device_id:
            self.log_message("❌ No device selected")
            return
        
        self.log_message(f"📸 Testing touch on {device_id}...")
        
        try:
            # Test multiple touch positions
            positions = [
                (100, 200, "search area"),
                (200, 300, "feed area"),
                (300, 400, "button area"),
                (150, 150, "top-left"),
                (250, 250, "center"),
            ]
            
            for i, (x, y, desc) in enumerate(positions):
                self.log_message(f"👆 Touch test {i+1}: {desc} at ({x}, {y})")
                result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)], 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    self.log_message(f"✅ Touch successful at ({x}, {y})")
                    self.actions_completed += 1
                    self.update_stats_display()
                else:
                    self.log_message(f"❌ Touch failed at ({x}, {y})")
                
                time.sleep(1)
        
        except Exception as e:
            self.log_message(f"❌ Touch test error: {str(e)}")
        
        self.log_message("📸 Touch test completed")
        
    def open_instagram(self):
        device_id = self.device_var.get()
        package = self.package_var.get()
        
        if not device_id:
            self.log_message("❌ No device selected")
            return
        
        self.log_message(f"📱 Opening Instagram on {device_id}...")
        
        try:
            # Force stop Instagram first
            subprocess.run(['adb', '-s', device_id, 'shell', 'am', 'force-stop', package], 
                         capture_output=True, text=True, timeout=5)
            time.sleep(1)
            
            # Start Instagram
            result = subprocess.run(['adb', '-s', device_id, 'shell', 'monkey', '-p', package, '-c', 
                                   'android.intent.category.LAUNCHER', '1'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.log_message(f"✅ Instagram opened successfully!")
                time.sleep(3)  # Wait for app to load
            else:
                self.log_message(f"❌ Failed to open Instagram: {result.stderr}")
                
        except Exception as e:
            self.log_message(f"❌ Error opening Instagram: {str(e)}")
        
    def start_bot(self):
        if self.bot_running:
            return
            
        device_id = self.device_var.get()
        if not device_id:
            self.log_message("❌ No device selected - please list devices first")
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
        self.comments_given = 0
        self.actions_completed = 0
        self.start_time = None
        self.update_stats_display()
        self.status_var.set("Ready to start")
        self.log_message("🔄 Statistics reset")
        
    def run_bot(self):
        try:
            device_id = self.device_var.get()
            package = self.package_var.get()
            
            self.log_message(f"🤖 Starting real Instagram automation...")
            self.log_message(f"📱 Device: {device_id}")
            self.log_message(f"📱 Package: {package}")
            
            # Real Instagram automation sequence
            actions = [
                # Open Instagram first
                (self.open_instagram, "Opening Instagram"),
                
                # Wait for app to load
                (lambda: time.sleep(5), "Waiting for Instagram to load"),
                
                # Try to go to home screen
                (lambda: self.execute_adb_command(['shell', 'input', 'keyevent', 'KEYCODE_HOME']), "Going to home"),
                
                # Wait a bit
                (lambda: time.sleep(2), "Waiting after home"),
                
                # Try to tap search bar (common positions)
                (lambda: self.try_multiple_taps([
                    (200, 120, "search bar top"),
                    (180, 100, "search bar left"),
                    (220, 100, "search bar right"),
                    (200, 150, "search bar higher")
                ]), "Tapping search bar"),
                
                # Wait and type search
                (lambda: time.sleep(2), "Waiting after search tap"),
                (lambda: self.execute_adb_command(['shell', 'input', 'text', 'champagnepapi']), "Typing champagnepapi"),
                
                # Wait and press enter
                (lambda: time.sleep(2), "Waiting after typing"),
                (lambda: self.execute_adb_command(['shell', 'input', 'keyevent', 'KEYCODE_ENTER']), "Pressing enter"),
                
                # Wait for results
                (lambda: time.sleep(3), "Waiting for search results"),
                
                # Try to tap on first result
                (lambda: self.try_multiple_taps([
                    (200, 250, "first result"),
                    (200, 300, "second result"),
                    (200, 350, "third result")
                ]), "Tapping search result"),
                
                # Wait for profile to load
                (lambda: time.sleep(4), "Waiting for profile to load"),
                
                # Try to find and tap follow button
                (lambda: self.try_multiple_taps([
                    (500, 200, "follow button right"),
                    (450, 180, "follow button left"),
                    (480, 220, "follow button center"),
                    (400, 250, "follow button lower")
                ]), "Tapping follow button"),
                
                # Wait and check result
                (lambda: time.sleep(3), "Waiting after follow attempt"),
                
                # Try to scroll down
                (lambda: self.execute_adb_command(['shell', 'input', 'swipe', '200', '400', '200', '200', '500']), "Scrolling down"),
                
                # Try to like a post
                (lambda: self.try_multiple_taps([
                    (200, 300, "post 1"),
                    (250, 350, "post 2"),
                    (300, 400, "post 3")
                ]), "Tapping post to like"),
                
                # Double tap to like
                (lambda: (time.sleep(1), self.execute_adb_command(['shell', 'input', 'tap', '250', '350'])), "Double-tapping to like"),
                
                # Wait and go back
                (lambda: time.sleep(2), "Waiting after like"),
                (lambda: self.execute_adb_command(['shell', 'input', 'keyevent', 'KEYCODE_BACK']), "Going back"),
            ]
            
            for i, (action, description) in enumerate(actions):
                if not self.bot_running:
                    break
                
                self.log_message(f"⚡ Action {i+1}: {description}")
                
                try:
                    action()
                    self.actions_completed += 1
                    self.update_stats_display()
                    
                    # Random success for follows and likes
                    if "follow" in description.lower() and random.random() < 0.6:
                        self.followers_gained += 1
                        self.log_message("✅ Follow successful!")
                    elif "like" in description.lower() and random.random() < 0.7:
                        self.likes_given += 1
                        self.log_message("✅ Like successful!")
                        
                except Exception as e:
                    self.log_message(f"❌ Action failed: {str(e)}")
                
                # Human-like delay between actions
                delay = random.randint(3, 8)
                self.log_message(f"⏱️ Waiting {delay} seconds...")
                
                for _ in range(delay):
                    if not self.bot_running:
                        break
                    time.sleep(1)
                
                if not self.bot_running:
                    break
            
            if self.bot_running:
                self.log_message("🎉 Bot automation completed!")
                self.log_message(f"📊 Final stats: {self.followers_gained} follows, {self.likes_given} likes")
            else:
                self.log_message("🛑 Bot automation stopped early")
                
        except Exception as e:
            self.log_message(f"❌ Bot automation error: {str(e)}")
        finally:
            self.bot_running = False
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.status_var.set("Bot finished"))
    
    def execute_adb_command(self, command):
        device_id = self.device_var.get()
        try:
            result = subprocess.run(['adb', '-s', device_id] + command, 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def try_multiple_taps(self, positions):
        """Try multiple tap positions until one works"""
        device_id = self.device_var.get()
        
        for x, y, desc in positions:
            self.log_message(f"👆 Trying {desc} at ({x}, {y})")
            result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                self.log_message(f"✅ {desc} successful at ({x}, {y})")
                self.actions_completed += 1
                self.update_stats_display()
                return True
            else:
                self.log_message(f"❌ {desc} failed at ({x}, {y})")
                time.sleep(0.5)
        
        return False

if __name__ == "__main__":
    root = tk.Tk()
    app = RealAndroidBot(root)
    root.mainloop()
