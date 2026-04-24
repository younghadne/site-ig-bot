import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import time
import random
from datetime import datetime

class RealEmulatorBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖️ Real Instagram Emulator Bot")
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
            'start_time': None
        }
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖️ Real Instagram Emulator Bot", 
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
        
        # Accounts Processed
        ttk.Label(stats_grid, text="📱 Accounts Processed:", font=('Helvetica', 12, 'bold')).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.accounts_var = tk.StringVar(value="0")
        ttk.Label(stats_grid, textvariable=self.accounts_var, font=('Helvetica', 14, 'bold'), 
                 foreground='#3498db').grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # Posts Liked
        ttk.Label(stats_grid, text="📸 Posts Liked:", font=('Helvetica', 12, 'bold')).grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.posts_var = tk.StringVar(value="0")
        ttk.Label(stats_grid, textvariable=self.posts_var, font=('Helvetica', 14, 'bold'), 
                 foreground='#9b59b6').grid(row=1, column=3, sticky='w', padx=5, pady=2)
        
        # Runtime
        ttk.Label(stats_grid, text="⏱️ Runtime:", font=('Helvetica', 12, 'bold')).grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.runtime_var = tk.StringVar(value="0s")
        ttk.Label(stats_grid, textvariable=self.runtime_var, font=('Helvetica', 14, 'bold'), 
                 foreground='#e74c3c').grid(row=2, column=1, sticky='w', padx=5, pady=2)
        
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
        self.targets_var = tk.StringVar(value='champagnepapi, nav, pressa.armani, top5, whygnumba35')
        targets_entry = ttk.Entry(settings_grid, textvariable=self.targets_var, width=50)
        targets_entry.grid(row=1, column=1, columnspan=3, sticky='ew', padx=5, pady=5)
        
        # Hashtags
        ttk.Label(settings_grid, text="Hashtags:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.hashtags_var = tk.StringVar(value='tech, fashion, art')
        ttk.Entry(settings_grid, textvariable=self.hashtags_var, width=30).grid(row=2, column=1, columnspan=2, sticky='ew', padx=5, pady=5)
        
        # Daily Limits
        ttk.Label(settings_grid, text="Follow Limit:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.follow_limit_var = tk.StringVar(value='20')
        ttk.Entry(settings_grid, textvariable=self.follow_limit_var, width=10).grid(row=3, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(settings_grid, text="Like Limit:").grid(row=3, column=2, sticky='w', padx=5, pady=5)
        self.like_limit_var = tk.StringVar(value='50')
        ttk.Entry(settings_grid, textvariable=self.like_limit_var, width=10).grid(row=3, column=3, sticky='w', padx=5, pady=5)
        
        # Control Panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(control_frame, text="📱 Check Device", command=self.check_device).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🏠 Home Screen", command=self.go_home).pack(side=tk.LEFT, padx=5)
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
        self.accounts_var.set(str(self.stats['accounts_processed']))
        self.posts_var.set(str(self.stats['posts_liked']))
        
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
        
    def go_home(self):
        success, output, error = self.run_adb_command(['shell', 'input', 'keyevent', 'KEYCODE_HOME'])
        if success:
            self.log_message("🏠 Returned to home screen")
        else:
            self.log_message(f"❌ Error going home: {error}")
    
    def open_instagram(self):
        self.log_message("📱 Opening Instagram app...")
        success, output, error = self.run_adb_command(['shell', 'monkey', '-p', 'com.instagram.android', '-c', 'android.intent.category.LAUNCHER', '1'])
        if success:
            self.log_message("✅ Instagram app opened")
            time.sleep(3)
        else:
            self.log_message(f"❌ Cannot open Instagram: {error}")
            self.log_message("💡 Make sure Instagram is installed on the emulator")
        
    def tap_screen(self, x, y, description=""):
        success, output, error = self.run_adb_command(['shell', 'input', 'tap', str(x), str(y)])
        if success:
            if description:
                self.log_message(f"👆 Tapped {description} at ({x}, {y})")
        else:
            self.log_message(f"❌ Error tapping at ({x}, {y}): {error}")
        time.sleep(random.uniform(1, 3))
        
    def swipe_screen(self, x1, y1, x2, y2, duration=500, description=""):
        success, output, error = self.run_adb_command(['shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(duration)])
        if success:
            if description:
                self.log_message(f"👆 Swiped {description}")
        else:
            self.log_message(f"❌ Error swiping: {error}")
        time.sleep(random.uniform(2, 4))
        
    def input_text(self, text, description=""):
        success, output, error = self.run_adb_command(['shell', 'input', 'text', text])
        if success:
            if description:
                self.log_message(f"⌨️ Typed {description}: {text}")
        else:
            self.log_message(f"❌ Error typing text: {error}")
        time.sleep(random.uniform(1, 2))
        
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
            'start_time': None
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
            
            # Open Instagram
            self.open_instagram()
            
            # Process target accounts - follow users
            for i, account in enumerate(target_accounts):
                if not self.bot_running or self.stats['followers_gained'] >= follow_limit:
                    break
                    
                self.log_message(f"📱 Processing account {i+1}/{len(target_accounts)}: @{account}")
                
                # Go to home first
                self.tap_screen(50, 50, "home button")
                time.sleep(2)
                
                # Tap search bar
                self.tap_screen(200, 100, "search bar")
                time.sleep(2)
                
                # Clear search and type username
                self.run_adb_command(['shell', 'input', 'keyevent', 'KEYCODE_CTRL_A'])
                time.sleep(1)
                self.input_text(account, f"username @{account}")
                time.sleep(3)
                
                # Tap on the first result (user profile)
                self.tap_screen(200, 200, f"search result for @{account}")
                time.sleep(3)
                
                # Try to follow
                if self.stats['followers_gained'] < follow_limit:
                    # Look for follow button (usually at top right)
                    self.tap_screen(500, 200, "follow button")
                    time.sleep(2)
                    
                    # Check if followed successfully by looking for "Following" button
                    self.tap_screen(500, 200, "check follow status")
                    time.sleep(2)
                    
                    self.stats['followers_gained'] += 1
                    self.log_message(f"✅ Attempted to follow @{account}")
                    self.update_stats_display()
                
                self.stats['accounts_processed'] += 1
                self.update_stats_display()
                
                # Human-like delay
                delay = random.uniform(20, 40)
                self.log_message(f"⏱️ Waiting {delay:.1f} seconds...")
                
                for remaining in range(int(delay), 0, -1):
                    if not self.bot_running:
                        break
                    time.sleep(1)
            
            # Process hashtags - like posts
            for i, hashtag in enumerate(hashtags):
                if not self.bot_running or self.stats['likes_given'] >= like_limit:
                    break
                    
                self.log_message(f"🏷️ Processing hashtag {i+1}/{len(hashtags)}: #{hashtag}")
                
                # Go to home
                self.tap_screen(50, 50, "home button")
                time.sleep(2)
                
                # Tap search bar
                self.tap_screen(200, 100, "search bar")
                time.sleep(2)
                
                # Clear search and type hashtag
                self.run_adb_command(['shell', 'input', 'keyevent', 'KEYCODE_CTRL_A'])
                time.sleep(1)
                self.input_text(f"#{hashtag}", f"hashtag #{hashtag}")
                time.sleep(3)
                
                # Tap on hashtag result
                self.tap_screen(200, 250, f"hashtag result for #{hashtag}")
                time.sleep(3)
                
                # Like posts from hashtag feed
                posts_to_like = min(5, like_limit - self.stats['likes_given'])
                for post_num in range(posts_to_like):
                    if not self.bot_running or self.stats['likes_given'] >= like_limit:
                        break
                    
                    self.log_message(f"📸 Liking post {post_num+1} from #{hashtag}")
                    
                    # Double tap to like
                    self.tap_screen(300, 400, f"post {post_num+1} - first tap")
                    time.sleep(0.5)
                    self.tap_screen(300, 400, f"post {post_num+1} - second tap (like)")
                    time.sleep(2)
                    
                    self.stats['likes_given'] += 1
                    self.stats['posts_liked'] += 1
                    self.update_stats_display()
                    
                    # Scroll to next post
                    self.swipe_screen(300, 500, 300, 200, 800, f"scroll to next post")
                
                # Human-like delay between hashtags
                delay = random.uniform(15, 30)
                self.log_message(f"⏱️ Waiting {delay:.1f} seconds...")
                
                for remaining in range(int(delay), 0, -1):
                    if not self.bot_running:
                        break
                    time.sleep(1)
            
            if self.bot_running:
                self.log_message("🎉 Bot session completed successfully!")
                self.log_message(f"📊 Final stats: {self.stats['followers_gained']} follows, {self.stats['likes_given']} likes")
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
    app = RealEmulatorBotGUI(root)
    root.mainloop()
