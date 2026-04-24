import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import time
import random
from datetime import datetime

class VisualInstagramBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖️ Visual Instagram Bot")
        self.root.geometry("1000x750")
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
        title_label = ttk.Label(main_frame, text="🤖️ Visual Instagram Bot - Test Coordinates First", 
                             font=('Helvetica', 18, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # Create two columns
        columns_frame = ttk.Frame(main_frame)
        columns_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Controls
        left_frame = ttk.Frame(columns_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Statistics Frame
        stats_frame = ttk.LabelFrame(left_frame, text="📊 Statistics")
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
        
        # Settings Frame
        settings_frame = ttk.LabelFrame(left_frame, text="⚙️ Settings")
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
        targets_entry = ttk.Entry(settings_grid, textvariable=self.targets_var, width=40)
        targets_entry.grid(row=1, column=1, columnspan=2, sticky='ew', padx=5, pady=5)
        
        # Action Settings
        ttk.Label(settings_grid, text="Follow Limit:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.follow_limit_var = tk.StringVar(value='5')
        ttk.Entry(settings_grid, textvariable=self.follow_limit_var, width=10).grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(settings_grid, text="Like Limit:").grid(row=2, column=2, sticky='w', padx=5, pady=5)
        self.like_limit_var = tk.StringVar(value='10')
        ttk.Entry(settings_grid, textvariable=self.like_limit_var, width=10).grid(row=2, column=2, sticky='w', padx=5, pady=5)
        
        # Control Panel
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(control_frame, text="📱 Check Device", command=self.check_device).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🎯 Test Search Bar", command=self.test_search_bar).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🏷️ Test Accounts Tab", command=self.test_accounts_tab).pack(side=tk.LEFT, padx=5)
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
        
        # Right column - Visual Guide
        right_frame = ttk.Frame(columns_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Visual Guide Frame
        visual_frame = ttk.LabelFrame(right_frame, text="👁️ Visual Coordinate Guide")
        visual_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create coordinate display
        coord_text = """
🎯 IMPORTANT: Test coordinates before running bot!

📱 SCREEN LAYOUT (Approximate):
┌─────────────────────────────────┐
│  (50,50)   (200,50)   (350,50) │
│    🏠          🔍           ⚙️    │
│                                 │
│  (100,200)  (200,200)  (300,200) │
│    📝          📱           👤    │
│                                 │
│  (150,350)  (200,350)  (250,350) │
│    🏷️         👥           ❤️    │
│                                 │
│  (100,500)  (200,500)  (300,500) │
│    📸          📊           ⏱️    │
└─────────────────────────────────┘

🔍 SEARCH FLOW:
1. Tap search bar at (200,120)
2. Type username
3. Tap Accounts tab at (100,200) ← IMPORTANT!
4. Tap user from list at (200,280)
5. Tap follow button at (500,200)

❤️ LIKE FLOW:
1. Go to home
2. Scroll down
3. Double-tap post to like

💡 TIPS:
- Use "Test Search Bar" button first
- Use "Test Accounts Tab" button second
- Watch where the bot actually taps
- Adjust coordinates if needed
        """
        
        coord_display = tk.Text(visual_frame, height=25, width=40, wrap=tk.WORD, font=('Courier', 9))
        coord_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        coord_display.insert('1.0', coord_text)
        coord_display.config(state=tk.DISABLED)
        
        # Log Area (bottom)
        log_frame = ttk.LabelFrame(main_frame, text="📝 Bot Logs")
        log_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD)
        self.log_text.pack(fill=tk.X, padx=5, pady=5)
        
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
                self.runtime_var = tk.StringVar(value=f"{hours}h {minutes}m {seconds}s")
            elif minutes > 0:
                self.runtime_var = tk.StringVar(value=f"{minutes}m {seconds}s")
            else:
                self.runtime_var = tk.StringVar(value=f"{seconds}s")
        
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
        
    def test_search_bar(self):
        self.log_message("🎯 Testing search bar coordinates...")
        
        # Show visual indicator
        self.log_message("👁️ Watch the emulator screen - I will tap search bar area")
        time.sleep(2)
        
        # Test search bar positions
        search_positions = [
            (200, 120),  # Most common
            (180, 100),  # Alternative
            (220, 100),  # Alternative
            (150, 130),  # Alternative
        ]
        
        for i, (x, y) in enumerate(search_positions):
            self.log_message(f"👆 Tapping search position {i+1} at ({x}, {y})")
            success, output, error = self.run_adb_command(['shell', 'input', 'tap', str(x), str(y)])
            if success:
                self.log_message(f"✅ Tap successful at ({x}, {y})")
            else:
                self.log_message(f"❌ Tap failed at ({x}, {y}): {error}")
            
            # Ask user if this was correct
            response = messagebox.askyesno("Test Search Bar", f"Did I tap the search bar at ({x}, {y})?\n\nClick YES if correct, NO to try next position.")
            if response:
                self.log_message(f"✅ Found search bar at ({x}, {y})!")
                return
            else:
                time.sleep(1)
        
        self.log_message("❌ Could not find working search bar position")
        
    def test_accounts_tab(self):
        self.log_message("🏷️ Testing Accounts tab coordinates...")
        
        # Show visual indicator
        self.log_message("👁️ Watch the emulator screen - I will tap Accounts tab area")
        time.sleep(2)
        
        # Test Accounts tab positions
        accounts_positions = [
            (100, 200),  # Left side
            (200, 200),  # Center
            (300, 200),  # Right side
            (150, 180),  # Slightly higher
            (250, 180),  # Slightly higher
        ]
        
        for i, (x, y) in enumerate(accounts_positions):
            self.log_message(f"👆 Tapping Accounts tab position {i+1} at ({x}, {y})")
            success, output, error = self.run_adb_command(['shell', 'input', 'tap', str(x), str(y)])
            if success:
                self.log_message(f"✅ Tap successful at ({x}, {y})")
            else:
                self.log_message(f"❌ Tap failed at ({x}, {y}): {error}")
            
            # Ask user if this was correct
            response = messagebox.askyesno("Test Accounts Tab", f"Did I tap the Accounts tab at ({x}, {y})?\n\nClick YES if correct, NO to try next position.")
            if response:
                self.log_message(f"✅ Found Accounts tab at ({x}, {y})!")
                return
            else:
                time.sleep(1)
        
        self.log_message("❌ Could not find working Accounts tab position")
        
    def open_instagram(self):
        self.log_message("📱 Opening Instagram app...")
        success, output, error = self.run_adb_command(['shell', 'monkey', '-p', 'com.instagram.android', '-c', 'android.intent.category.LAUNCHER', '1'])
        if success:
            self.log_message("✅ Instagram app opened")
            time.sleep(6)
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
        self.runtime_var = tk.StringVar(value="0s")
        self.log_message("🔄 Statistics reset")
        
    def run_bot(self):
        try:
            device_id = self.device_var.get()
            target_accounts = [acc.strip() for acc in self.targets_var.get().split(',')]
            follow_limit = int(self.follow_limit_var.get())
            like_limit = int(self.like_limit_var.get())
            
            self.log_message(f"📱 Connecting to device: {device_id}")
            
            # Check device connection
            success, output, error = self.run_adb_command(['shell', 'echo', 'Device connected'])
            if not success:
                self.log_message(f"❌ Cannot connect to device: {error}")
                return
            
            self.log_message(f"✅ Connected to {device_id}")
            self.log_message(f"🎯 Target accounts: {len(target_accounts)}")
            self.log_message(f"📊 Limits: {follow_limit} follows, {like_limit} likes")
            
            # Open Instagram
            self.open_instagram()
            
            # Main bot loop - very careful and slow
            for i, username in enumerate(target_accounts):
                if not self.bot_running or self.stats['followers_gained'] >= follow_limit:
                    break
                
                self.log_message(f"👥 Processing account {i+1}/{len(target_accounts)}: @{username}")
                
                # Step 1: Tap search bar
                self.log_message("🔍 Tapping search bar...")
                if not self.safe_touch(200, 120, "search bar"):
                    continue
                
                time.sleep(2)
                
                # Step 2: Type the EXACT username from target accounts
                self.log_message(f"⌨️ Typing EXACT username: '{username}'")
                self.run_adb_command(['shell', 'input', 'text', username])
                time.sleep(3)
                self.log_message(f"✅ Typed: '{username}' - check if it appears correctly")
                
                # Step 3: Tap Accounts tab (CRITICAL!)
                self.log_message("🏷️ Tapping Accounts tab...")
                if not self.safe_touch(100, 200, "Accounts tab"):
                    continue
                
                time.sleep(3)
                
                # Step 4: Tap user from accounts list
                self.log_message(f"👥 Tapping user result for @{username}...")
                if not self.safe_touch(200, 280, f"user {username}"):
                    continue
                
                time.sleep(4)
                
                # Step 5: Try to follow
                self.log_message("👥 Looking for follow button...")
                follow_positions = [(500, 200), (450, 180), (480, 220)]
                
                for fx, fy in follow_positions:
                    if self.safe_touch(fx, fy, f"follow button at ({fx}, {fy})"):
                        time.sleep(3)
                        self.stats['followers_gained'] += 1
                        self.stats['accounts_processed'] += 1
                        self.update_stats_display()
                        self.log_message(f"✅ Successfully followed @{username}!")
                        break
                
                # Wait between accounts
                if self.bot_running:
                    delay = random.randint(15, 30)
                    self.log_message(f"⏱️ Waiting {delay} seconds...")
                    for remaining in range(delay, 0, -1):
                        if not self.bot_running:
                            break
                        time.sleep(1)
            
            if self.bot_running:
                self.log_message("🎉 Bot session completed successfully!")
                self.log_message(f"📊 Final stats: {self.stats['followers_gained']} follows")
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
    app = VisualInstagramBotGUI(root)
    root.mainloop()
