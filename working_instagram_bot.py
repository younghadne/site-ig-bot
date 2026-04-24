import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import time
import random
from datetime import datetime

class WorkingInstagramBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖️ Working Instagram Bot")
        self.root.geometry("900x700")
        self.root.configure(bg='#2c3e50')
        
        self.bot_running = False
        self.bot_thread = None
        
        # Bot statistics
        self.stats = {
            'followers_gained': 0,
            'likes_given': 0,
            'accounts_processed': 0,
            'posts_liked': 0,
            'start_time': None,
            'actions_completed': 0
        }
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖️ Working Instagram Bot", 
                             font=('Helvetica', 18, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # Statistics Frame
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Statistics")
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Followers Gained
        ttk.Label(stats_grid, text="👥 Followers Gained:", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.followers_var = tk.StringVar(value="0")
        ttk.Label(stats_grid, textvariable=self.followers_var, font=('Helvetica', 14, 'bold'), 
                 foreground='#27ae60').grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # Likes Given
        ttk.Label(stats_grid, text="❤️ Likes Given:", font=('Helvetica', 12, 'bold')).grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.likes_var = tk.StringVar(value="0")
        ttk.Label(stats_grid, textvariable=self.likes_var, font=('Helvetica', 14, 'bold'), 
                 foreground='#e67e22').grid(row=0, column=3, sticky='w', padx=5, pady=2)
        
        # Actions Completed
        ttk.Label(stats_grid, text="⚡ Actions Completed:", font=('Helvetica', 12, 'bold')).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.actions_var = tk.StringVar(value="0")
        ttk.Label(stats_grid, textvariable=self.actions_var, font=('Helvetica', 14, 'bold'), 
                 foreground='#3498db').grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # Runtime
        ttk.Label(stats_grid, text="⏱️ Runtime:", font=('Helvetica', 12, 'bold')).grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.runtime_var = tk.StringVar(value="0s")
        ttk.Label(stats_grid, textvariable=self.runtime_var, font=('Helvetica', 14, 'bold'), 
                 foreground='#9b59b6').grid(row=1, column=3, sticky='w', padx=5, pady=2)
        
        # Settings Frame
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Settings")
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        settings_grid = ttk.Frame(settings_frame)
        settings_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Device ID
        ttk.Label(settings_grid, text="Device ID:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.device_var = tk.StringVar(value='emulator-5554')
        ttk.Entry(settings_grid, textvariable=self.device_var, width=20).grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        # Target Accounts
        ttk.Label(settings_grid, text="Target Accounts:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.targets_var = tk.StringVar(value='champagnepapi, nav, pressa.armani')
        targets_entry = ttk.Entry(settings_grid, textvariable=self.targets_var, width=50)
        targets_entry.grid(row=1, column=1, columnspan=3, sticky='ew', padx=5, pady=5)
        
        # Hashtags
        ttk.Label(settings_grid, text="Hashtags:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.hashtags_var = tk.StringVar(value='tech, fashion, art')
        ttk.Entry(settings_grid, textvariable=self.hashtags_var, width=30).grid(row=2, column=1, columnspan=2, sticky='ew', padx=5, pady=5)
        
        # Action Settings
        ttk.Label(settings_grid, text="Follow Limit:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.follow_limit_var = tk.StringVar(value='10')
        ttk.Entry(settings_grid, textvariable=self.follow_limit_var, width=10).grid(row=3, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(settings_grid, text="Like Limit:").grid(row=3, column=2, sticky='w', padx=5, pady=5)
        self.like_limit_var = tk.StringVar(value='25')
        ttk.Entry(settings_grid, textvariable=self.like_limit_var, width=10).grid(row=3, column=3, sticky='w', padx=5, pady=5)
        
        ttk.Label(settings_grid, text="Delay (sec):").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.delay_var = tk.StringVar(value='5')
        ttk.Entry(settings_grid, textvariable=self.delay_var, width=10).grid(row=4, column=1, sticky='w', padx=5, pady=5)
        
        # Control Panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(control_frame, text="📱 Check Device", command=self.check_device).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="📸 Test Touch", command=self.test_touch).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="📱 Open Instagram", command=self.open_instagram).pack(side=tk.LEFT, padx=5)
        
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
        self.followers_var.set(str(self.stats['followers_gained']))
        self.likes_var.set(str(self.stats['likes_given']))
        self.actions_var.set(str(self.stats['actions_completed']))
        
    def update_runtime(self):
        if self.stats['start_time']:
            runtime = int(time.time() - self.stats['start_time'])
            hours = runtime // 3600
            minutes = (runtime % 3600) // 60
            seconds = runtime % 60
            
            if hours > 0:
                self.runtime_var.set(f"{hours}h {minutes}m {seconds}s")
            elif minutes > 0:
                self.runtime_var.set(f"{minutes}m {seconds}s")
            else:
                self.runtime_var.set(f"{seconds}s")
        
        self.root.after(1000, self.update_runtime)
        
    def run_adb_command(self, command, timeout=10):
        try:
            device_id = self.device_var.get()
            full_command = ['adb', '-s', device_id] + command
            result = subprocess.run(full_command, capture_output=True, text=True, timeout=timeout)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timeout"
        except Exception as e:
            return False, "", str(e)
    
    def check_device(self):
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
            if result.returncode == 0:
                devices = result.stdout.strip().split('\n')[1:]
                if devices:
                    self.log_message("📱 Connected devices:")
                    for device in devices:
                        if device.strip():
                            self.log_message(f"   {device.strip()}")
                    self.status_var.set("Device(s) found")
                else:
                    self.log_message("❌ No devices found - please start emulator")
                    self.status_var.set("No devices found")
            else:
                self.log_message("❌ ADB error - check Android SDK")
                self.status_var.set("ADB error")
        except Exception as e:
            self.log_message(f"❌ Error checking devices: {str(e)}")
            self.status_var.set("Error checking devices")
        
    def test_touch(self):
        self.log_message("👆 Testing touch coordinates...")
        
        # Test various touch points to see what works
        test_points = [
            (200, 200, "center"),
            (100, 100, "top-left"),
            (500, 500, "bottom-right"),
            (300, 300, "middle"),
            (400, 100, "top-center"),
            (100, 400, "left-center")
        ]
        
        for x, y, desc in test_points:
            success, output, error = self.run_adb_command(['shell', 'input', 'tap', str(x), str(y)])
            if success:
                self.log_message(f"✅ Touch test successful at ({x}, {y}) - {desc}")
            else:
                self.log_message(f"❌ Touch test failed at ({x}, {y}) - {desc}: {error}")
            time.sleep(1)
        
    def open_instagram(self):
        self.log_message("📱 Opening Instagram app...")
        success, output, error = self.run_adb_command(['shell', 'monkey', '-p', 'com.instagram.android', '-c', 'android.intent.category.LAUNCHER', '1'])
        if success:
            self.log_message("✅ Instagram app opened")
            time.sleep(5)  # Wait for app to fully load
            self.log_message("📱 App should be loaded now")
        else:
            self.log_message(f"❌ Cannot open Instagram: {error}")
            self.log_message("💡 Make sure Instagram is installed on the emulator")
        
    def perform_touch(self, x, y, description=""):
        success, output, error = self.run_adb_command(['shell', 'input', 'tap', str(x), str(y)])
        if success:
            self.stats['actions_completed'] += 1
            if description:
                self.log_message(f"👆 Tapped {description} at ({x}, {y})")
            else:
                self.log_message(f"👆 Tapped at ({x}, {y})")
            self.update_stats_display()
            return True
        else:
            self.log_message(f"❌ Error tapping at ({x}, {y}): {error}")
            return False
        
    def perform_swipe(self, x1, y1, x2, y2, duration=500, description=""):
        success, output, error = self.run_adb_command(['shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(duration)])
        if success:
            self.stats['actions_completed'] += 1
            if description:
                self.log_message(f"👆 Swiped {description}")
            else:
                self.log_message(f"👆 Swiped from ({x1}, {y1}) to ({x2}, {y2})")
            self.update_stats_display()
            return True
        else:
            self.log_message(f"❌ Error swiping: {error}")
            return False
        
    def start_bot(self):
        if self.bot_running:
            return
            
        self.bot_running = True
        self.stats['start_time'] = time.time()
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Bot running...")
        
        # Start bot in separate thread
        self.bot_thread = threading.Thread(target=self.run_bot)
        self.bot_thread.daemon = True
        self.bot_thread.start()
        
        self.log_message("🚀 Bot started successfully!")
        
    def stop_bot(self):
        if not self.bot_running:
            return
            
        self.bot_running = False
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Bot stopped")
        
        self.log_message("🛑 Bot stopped by user")
        
    def reset_stats(self):
        self.stats = {
            'followers_gained': 0,
            'likes_given': 0,
            'accounts_processed': 0,
            'posts_liked': 0,
            'start_time': None,
            'actions_completed': 0
        }
        self.update_stats_display()
        self.runtime_var.set("0s")
        self.log_message("🔄 Statistics reset")
        
    def run_bot(self):
        try:
            device_id = self.device_var.get()
            target_accounts = [acc.strip() for acc in self.targets_var.get().split(',')]
            hashtags = [tag.strip() for tag in self.hashtags_var.get().split(',')]
            follow_limit = int(self.follow_limit_var.get())
            like_limit = int(self.like_limit_var.get())
            delay = int(self.delay_var.get())
            
            self.log_message(f"📱 Connecting to device: {device_id}")
            
            # Check if device is connected
            success, output, error = self.run_adb_command(['shell', 'echo', 'Device connected'])
            if not success:
                self.log_message(f"❌ Cannot connect to device: {error}")
                return
            
            self.log_message(f"✅ Connected to {device_id}")
            self.log_message(f"🎯 Target accounts: {len(target_accounts)}")
            self.log_message(f"🏷️ Hashtags: {len(hashtags)}")
            self.log_message(f"📊 Limits: {follow_limit} follows, {like_limit} likes")
            self.log_message(f"⏱️ Delay: {delay} seconds between actions")
            
            # Open Instagram
            self.open_instagram()
            
            # Wait for app to be ready
            self.log_message("⏱️ Waiting for Instagram to load...")
            time.sleep(5)
            
            action_count = 0
            
            # Perform actions - simple and reliable
            while self.bot_running and (self.stats['followers_gained'] < follow_limit or self.stats['likes_given'] < like_limit):
                
                # Random action: either follow attempt or like attempt
                if random.random() < 0.5 and self.stats['followers_gained'] < follow_limit:
                    # Simulate follow action
                    self.log_message("👥 Attempting follow action...")
                    
                    # Tap search area
                    if self.perform_touch(200, 150, "search area"):
                        time.sleep(2)
                        
                        # Type a random username from targets
                        if target_accounts:
                            username = random.choice(target_accounts)
                            self.run_adb_command(['shell', 'input', 'text', username])
                            time.sleep(3)
                            
                            # Tap first result
                            if self.perform_touch(200, 250, f"search result for {username}"):
                                time.sleep(3)
                                
                                # Look for follow button (try multiple positions)
                                follow_positions = [(500, 200), (450, 180), (480, 220), (520, 190)]
                                for x, y in follow_positions:
                                    if self.perform_touch(x, y, f"follow button attempt at ({x}, {y})"):
                                        time.sleep(2)
                                        self.stats['followers_gained'] += 1
                                        self.update_stats_display()
                                        break
                
                elif self.stats['likes_given'] < like_limit:
                    # Simulate like action
                    self.log_message("❤️ Attempting like action...")
                    
                    # Scroll a bit
                    if self.perform_swipe(300, 500, 300, 200, 800, "scroll down"):
                        time.sleep(2)
                        
                        # Try to like (double tap)
                        like_positions = [(250, 350), (300, 400), (350, 350), (200, 400)]
                        for x, y in like_positions:
                            if self.perform_touch(x, y, f"like attempt 1 at ({x}, {y})"):
                                time.sleep(0.5)
                                if self.perform_touch(x, y, f"like attempt 2 at ({x}, {y})"):
                                    time.sleep(2)
                                    self.stats['likes_given'] += 1
                                    self.stats['posts_liked'] += 1
                                    self.update_stats_display()
                                    break
                
                # Wait between actions
                self.log_message(f"⏱️ Waiting {delay} seconds...")
                for remaining in range(delay, 0, -1):
                    if not self.bot_running:
                        break
                    time.sleep(1)
                
                action_count += 1
                if action_count >= 50:  # Safety limit
                    self.log_message("🛑 Reached action limit (50 actions)")
                    break
            
            if self.bot_running:
                self.log_message("🎉 Bot session completed successfully!")
                self.log_message(f"📊 Final stats: {self.stats['followers_gained']} follows, {self.stats['likes_given']} likes")
                self.log_message(f"⚡ Total actions performed: {self.stats['actions_completed']}")
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
    app = WorkingInstagramBotGUI(root)
    root.mainloop()
