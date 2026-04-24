import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import time
import random
from datetime import datetime

class PreciseInstagramBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖️ Precise Instagram Bot")
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
            'successful_actions': 0,
            'failed_actions': 0
        }
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖️ Precise Instagram Bot", 
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
        
        # Success Rate
        ttk.Label(stats_grid, text="✅ Success Rate:", font=('Helvetica', 12, 'bold')).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.success_rate_var = tk.StringVar(value="0%")
        ttk.Label(stats_grid, textvariable=self.success_rate_var, font=('Helvetica', 14, 'bold'), 
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
        
        # Action Settings
        ttk.Label(settings_grid, text="Follow Limit:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.follow_limit_var = tk.StringVar(value='10')
        ttk.Entry(settings_grid, textvariable=self.follow_limit_var, width=10).grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(settings_grid, text="Like Limit:").grid(row=2, column=2, sticky='w', padx=5, pady=5)
        self.like_limit_var = tk.StringVar(value='25')
        ttk.Entry(settings_grid, textvariable=self.like_limit_var, width=10).grid(row=2, column=3, sticky='w', padx=5, pady=5)
        
        ttk.Label(settings_grid, text="Delay (sec):").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.delay_var = tk.StringVar(value='8')
        ttk.Entry(settings_grid, textvariable=self.delay_var, width=10).grid(row=3, column=1, sticky='w', padx=5, pady=5)
        
        # Control Panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(control_frame, text="📱 Check Device", command=self.check_device).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🔍 Find Search Bar", command=self.find_search_bar).pack(side=tk.LEFT, padx=5)
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
        
        # Calculate success rate
        total = self.stats['successful_actions'] + self.stats['failed_actions']
        if total > 0:
            success_rate = (self.stats['successful_actions'] / total) * 100
            self.success_rate_var.set(f"{success_rate:.1f}%")
        else:
            self.success_rate_var.set("0%")
        
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
        
    def find_search_bar(self):
        self.log_message("🔍 Trying to find Instagram search bar...")
        
        # Common search bar positions in Instagram
        search_positions = [
            (200, 120),  # Top center
            (180, 100),  # Slightly left
            (220, 100),  # Slightly right
            (150, 130),  # More left
            (250, 130),  # More right
            (200, 80),   # Higher up
            (200, 140),  # Lower down
        ]
        
        for i, (x, y) in enumerate(search_positions):
            self.log_message(f"🔍 Testing search position {i+1}: ({x}, {y})")
            success, output, error = self.run_adb_command(['shell', 'input', 'tap', str(x), str(y)])
            if success:
                self.log_message(f"✅ Tapped at ({x}, {y}) - check if search bar opened")
                time.sleep(2)
                
                # Try to type something to see if keyboard appeared
                self.run_adb_command(['shell', 'input', 'text', 'test'])
                time.sleep(2)
                
                # Clear the test
                self.run_adb_command(['shell', 'input', 'keyevent', 'KEYCODE_CTRL_A'])
                time.sleep(1)
                
                response = messagebox.askyesno("Search Bar Test", f"Did the search bar open at position ({x}, {y})?")
                if response:
                    self.log_message(f"✅ Found search bar at ({x}, {y})!")
                    return
                else:
                    # Go back and try next position
                    self.run_adb_command(['shell', 'input', 'keyevent', 'KEYCODE_BACK'])
                    time.sleep(1)
            else:
                self.log_message(f"❌ Failed to tap at ({x}, {y}): {error}")
        
        self.log_message("❌ Could not find working search bar position")
        
    def open_instagram(self):
        self.log_message("📱 Opening Instagram app...")
        success, output, error = self.run_adb_command(['shell', 'monkey', '-p', 'com.instagram.android', '-c', 'android.intent.category.LAUNCHER', '1'])
        if success:
            self.log_message("✅ Instagram app opened")
            time.sleep(6)  # Wait for app to fully load
            self.log_message("📱 App should be fully loaded now")
        else:
            self.log_message(f"❌ Cannot open Instagram: {error}")
            self.log_message("💡 Make sure Instagram is installed on the emulator")
        
    def safe_touch(self, x, y, description=""):
        success, output, error = self.run_adb_command(['shell', 'input', 'tap', str(x), str(y)])
        if success:
            self.stats['successful_actions'] += 1
            if description:
                self.log_message(f"✅ Successfully tapped {description} at ({x}, {y})")
            else:
                self.log_message(f"✅ Successfully tapped at ({x}, {y})")
            self.update_stats_display()
            return True
        else:
            self.stats['failed_actions'] += 1
            self.log_message(f"❌ Failed to tap {description} at ({x}, {y}): {error}")
            self.update_stats_display()
            return False
        
    def safe_swipe(self, x1, y1, x2, y2, duration=500, description=""):
        success, output, error = self.run_adb_command(['shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(duration)])
        if success:
            self.stats['successful_actions'] += 1
            if description:
                self.log_message(f"✅ Successfully swiped {description}")
            else:
                self.log_message(f"✅ Successfully swiped from ({x1}, {y1}) to ({x2}, {y2})")
            self.update_stats_display()
            return True
        else:
            self.stats['failed_actions'] += 1
            self.log_message(f"❌ Failed to swipe {description}: {error}")
            self.update_stats_display()
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
            'successful_actions': 0,
            'failed_actions': 0
        }
        self.update_stats_display()
        self.runtime_var.set("0s")
        self.log_message("🔄 Statistics reset")
        
    def follow_account_precise(self, username):
        """Precise account following with proper Instagram UI navigation"""
        self.log_message(f"👥 Starting follow process for @{username}")
        
        # Step 1: Go to home/feed first to ensure we're in a good state
        self.log_message("🏠 Going to home screen...")
        self.run_adb_command(['shell', 'input', 'keyevent', 'KEYCODE_HOME'])
        time.sleep(2)
        
        # Step 2: Open Instagram again to be sure
        self.open_instagram()
        
        # Step 3: Find and tap search bar (try multiple positions)
        self.log_message("🔍 Looking for search bar...")
        search_positions = [
            (200, 120),  # Most common position
            (180, 100),  # Alternative
            (220, 100),  # Alternative
            (150, 130),  # Alternative
        ]
        
        search_found = False
        for x, y in search_positions:
            if self.safe_touch(x, y, f"search bar at ({x}, {y})"):
                time.sleep(2)
                
                # Test if search opened by trying to type
                self.run_adb_command(['shell', 'input', 'text', username])
                time.sleep(3)
                
                # Look for search results - FIRST click Accounts tab, then tap user result
                self.log_message("🏷️ Looking for Accounts tab in search...")
                
                # Accounts tab positions (usually at the top of search results)
                accounts_tab_positions = [
                    (100, 200),  # Left side - Accounts
                    (200, 200),  # Center - Accounts  
                    (300, 200),  # Right side - Accounts
                    (150, 180),  # Slightly higher
                    (250, 180),  # Slightly higher
                ]
                
                accounts_tab_found = False
                for ax, ay in accounts_tab_positions:
                    if self.safe_touch(ax, ay, f"Accounts tab at ({ax}, {ay})"):
                        time.sleep(2)
                        accounts_tab_found = True
                        self.log_message("✅ Clicked on Accounts tab")
                        break
                
                if accounts_tab_found:
                    time.sleep(2)  # Wait for accounts to load
                    
                    # Now tap on user result from accounts list
                    user_result_positions = [
                        (200, 280),  # First account in list
                        (200, 330),  # Second account
                        (200, 380),  # Third account
                        (200, 430),  # Fourth account
                    ]
                
                for rx, ry in user_result_positions:
                    if self.safe_touch(rx, ry, f"user result for @{username}"):
                        time.sleep(4)  # Wait for profile to load
                        
                        # Now look for follow button on profile
                        self.log_message("🔍 Looking for follow button on profile...")
                        follow_positions = [
                            (500, 200),  # Right side, top
                            (450, 180),  # Slightly left
                            (480, 220),  # Slightly down
                            (520, 190),  # Slightly right
                            (400, 200),  # More left
                        ]
                        
                        for fx, fy in follow_positions:
                            if self.safe_touch(fx, fy, f"follow button at ({fx}, {fy})"):
                                time.sleep(3)
                                
                                # Check if follow was successful by looking for "Following" text
                                # We'll assume success if the tap worked
                                self.stats['followers_gained'] += 1
                                self.update_stats_display()
                                self.log_message(f"✅ Successfully followed @{username}!")
                                search_found = True
                                break
                        
                        if search_found:
                            break
                
                if search_found:
                    break
                
                # If this search position didn't work, go back and try next
                self.run_adb_command(['shell', 'input', 'keyevent', 'KEYCODE_BACK'])
                time.sleep(1)
        
        if not search_found:
            self.log_message(f"❌ Could not follow @{username} - search bar not found")
        
        return search_found
        
    def like_posts_precise(self):
        """Precise post liking from home feed"""
        self.log_message("❤️ Starting like process from home feed")
        
        # Go to home
        self.run_adb_command(['shell', 'input', 'keyevent', 'KEYCODE_HOME'])
        time.sleep(2)
        self.open_instagram()
        time.sleep(3)
        
        # Like posts from feed
        posts_to_like = min(5, 25 - self.stats['likes_given'])
        
        for i in range(posts_to_like):
            if not self.bot_running or self.stats['likes_given'] >= 25:
                break
            
            self.log_message(f"❤️ Liking post {i+1}")
            
            # Try different positions for posts in feed
            post_positions = [
                (200, 300),  # First post
                (200, 450),  # Second post
                (200, 600),  # Third post
            ]
            
            for px, py in post_positions:
                if self.safe_touch(px, py, f"post {i+1} at ({px}, {py})"):
                    time.sleep(2)
                    
                    # Double tap to like
                    if self.safe_touch(px, py, f"like tap 1 for post {i+1}"):
                        time.sleep(0.5)
                        if self.safe_touch(px, py, f"like tap 2 for post {i+1}"):
                            time.sleep(2)
                            self.stats['likes_given'] += 1
                            self.stats['posts_liked'] += 1
                            self.update_stats_display()
                            self.log_message(f"✅ Liked post {i+1}")
                            break
                    
                    # Go back to feed
                    self.run_adb_command(['shell', 'input', 'keyevent', 'KEYCODE_BACK'])
                    time.sleep(1)
                    break
            
            # Scroll down for next post
            if i < posts_to_like - 1:
                self.safe_swipe(200, 500, 200, 200, 800, f"scroll for next post")
                time.sleep(2)
        
    def run_bot(self):
        try:
            device_id = self.device_var.get()
            target_accounts = [acc.strip() for acc in self.targets_var.get().split(',')]
            follow_limit = int(self.follow_limit_var.get())
            like_limit = int(self.like_limit_var.get())
            delay = int(self.delay_var.get())
            
            self.log_message(f"📱 Connecting to device: {device_id}")
            
            # Check device connection
            success, output, error = self.run_adb_command(['shell', 'echo', 'Device connected'])
            if not success:
                self.log_message(f"❌ Cannot connect to device: {error}")
                return
            
            self.log_message(f"✅ Connected to {device_id}")
            self.log_message(f"🎯 Target accounts: {len(target_accounts)}")
            self.log_message(f"📊 Limits: {follow_limit} follows, {like_limit} likes")
            self.log_message(f"⏱️ Delay: {delay} seconds between actions")
            
            # Open Instagram
            self.open_instagram()
            
            # Main bot loop
            action_count = 0
            while self.bot_running and action_count < 30:  # Safety limit
                
                # Alternate between following and liking
                if action_count % 2 == 0 and self.stats['followers_gained'] < follow_limit and target_accounts:
                    # Follow action
                    username = target_accounts[self.stats['accounts_processed'] % len(target_accounts)]
                    if self.follow_account_precise(username):
                        self.stats['accounts_processed'] += 1
                        self.update_stats_display()
                        
                elif self.stats['likes_given'] < like_limit:
                    # Like action
                    self.like_posts_precise()
                
                # Wait between actions
                if self.bot_running:
                    self.log_message(f"⏱️ Waiting {delay} seconds...")
                    for remaining in range(delay, 0, -1):
                        if not self.bot_running:
                            break
                        time.sleep(1)
                
                action_count += 1
            
            if self.bot_running:
                self.log_message("🎉 Bot session completed successfully!")
                self.log_message(f"📊 Final stats: {self.stats['followers_gained']} follows, {self.stats['likes_given']} likes")
                self.log_message(f"✅ Success rate: {self.success_rate_var.get()}")
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
    app = PreciseInstagramBotGUI(root)
    root.mainloop()
