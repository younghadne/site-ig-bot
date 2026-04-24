import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import subprocess
import time
import random
from datetime import datetime

class PreciseInstagramBotFixed:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖️ Precise Instagram Bot - Fixed")
        self.root.geometry("1000x800")
        self.root.configure(bg='#2c3e50')
        
        self.bot_running = False
        self.bot_thread = None
        
        # Bot statistics
        self.followers_gained = 0
        self.likes_given = 0
        self.posts_liked = 0
        self.clicks_successful = 0
        self.clicks_failed = 0
        self.start_time = None
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖️ Precise Instagram Bot - Fixed Coordinates", 
                             font=('Helvetica', 18, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # Instructions Panel
        instructions_frame = ttk.LabelFrame(main_frame, text="📋 Instructions")
        instructions_frame.pack(fill=tk.X, pady=(0, 15))
        
        instructions_text = """
🎯 HOW TO USE THIS BOT:

1. 📱 Click "List Devices" to find your emulator
2. 📸 Click "Test Touch" to find working coordinates
3. 📱 Click "Open Instagram" to launch IG
4. 🚀 Click "Start Bot" to begin automation

📍 COMMON SCREEN COORDINATES:
┌─────────────────────────────────────────┐
│ (200,120)  SEARCH BAR           │
│ (100,200)  HOME BUTTON           │
│ (300,200)  FOLLOW BUTTON         │
│ (200,300)  POST LIKE            │
│ (200,400)  SCROLL DOWN           │
│ (100,400)  BACK BUTTON            │
└─────────────────────────────────────────┘

💡 TIPS:
- Test coordinates first before running bot
- If wrong position, adjust in code below
- Watch your emulator screen to see actual taps
- Different emulators may have different coordinates
        """
        
        instructions_label = tk.Text(instructions_frame, height=12, width=80, wrap=tk.WORD, font=('Courier', 9))
        instructions_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        instructions_label.insert('1.0', instructions_text)
        instructions_label.config(state=tk.DISABLED)
        
        # Device Connection Frame
        device_frame = ttk.LabelFrame(main_frame, text="📱 Device Connection")
        device_frame.pack(fill=tk.X, pady=(0, 15))
        
        device_grid = ttk.Frame(device_frame)
        device_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Device ID
        ttk.Label(device_grid, text="Device ID:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.device_var = tk.StringVar(value='')
        ttk.Entry(device_grid, textvariable=self.device_var, width=25).grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Button(device_grid, text="📱 List Devices", command=self.list_devices).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(device_grid, text="📸 Test Touch", command=self.test_all_coordinates).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(device_grid, text="📱 Open Instagram", command=self.open_instagram).grid(row=2, column=0, padx=5, pady=5)
        
        # Target Accounts
        ttk.Label(device_grid, text="Target Accounts:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.targets_var = tk.StringVar(value='champagnepapi')
        ttk.Entry(device_grid, textvariable=self.targets_var, width=30).grid(row=3, column=1, columnspan=2, sticky='ew', padx=5, pady=5)
        
        # Statistics Frame
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Statistics")
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Clicks Success
        ttk.Label(stats_grid, text="✅ Clicks Success:", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.click_success_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 14, 'bold'), foreground='#27ae60')
        self.click_success_label.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # Clicks Failed
        ttk.Label(stats_grid, text="❌ Clicks Failed:", font=('Helvetica', 12, 'bold')).grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.click_fail_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 14, 'bold'), foreground='#e74c3c')
        self.click_fail_label.grid(row=0, column=3, sticky='w', padx=5, pady=2)
        
        # Followers Gained
        ttk.Label(stats_grid, text="👥 Followers Gained:", font=('Helvetica', 12, 'bold')).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.followers_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 14, 'bold'), foreground='#e67e22')
        self.followers_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # Likes Given
        ttk.Label(stats_grid, text="❤️ Likes Given:", font=('Helvetica', 12, 'bold')).grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.likes_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 14, 'bold'), foreground='#9b59b6')
        self.likes_label.grid(row=1, column=2, sticky='w', padx=5, pady=2)
        
        # Posts Liked
        ttk.Label(stats_grid, text="📸 Posts Liked:", font=('Helvetica', 12, 'bold')).grid(row=1, column=3, sticky='w', padx=5, pady=2)
        self.posts_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 14, 'bold'), foreground='#3498db')
        self.posts_label.grid(row=1, column=3, sticky='w', padx=5, pady=2)
        
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
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
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
        self.click_success_label.config(text=str(self.clicks_successful))
        self.click_fail_label.config(text=str(self.clicks_failed))
        self.followers_label.config(text=str(self.followers_gained))
        self.likes_label.config(text=str(self.likes_given))
        self.posts_label.config(text=str(self.posts_liked))
        
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
        
    def test_all_coordinates(self):
        device_id = self.device_var.get()
        if not device_id:
            self.log_message("❌ No device selected")
            return
        
        self.log_message(f"📸 Testing all common coordinates on {device_id}...")
        
        try:
            # Test all common Instagram coordinate positions
            test_coordinates = [
                (200, 120, "SEARCH BAR"),
                (100, 200, "HOME BUTTON"),
                (300, 200, "FOLLOW BUTTON"),
                (200, 300, "POST LIKE"),
                (200, 400, "SCROLL DOWN"),
                (100, 400, "BACK BUTTON"),
                (150, 250, "MENU BUTTON"),
                (250, 350, "PROFILE PICTURE"),
                (200, 500, "STORIES"),
            ]
            
            for i, (x, y, desc) in enumerate(test_coordinates):
                self.log_message(f"👆 Test {i+1}: {desc} at ({x}, {y})")
                
                try:
                    result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)], 
                                          capture_output=True, text=True, timeout=3)
                    if result.returncode == 0:
                        self.log_message(f"✅ SUCCESS: {desc} at ({x}, {y})")
                        self.clicks_successful += 1
                    else:
                        self.log_message(f"❌ FAILED: {desc} at ({x}, {y})")
                        self.clicks_failed += 1
                    
                    self.update_stats_display()
                    time.sleep(1)
                except Exception as e:
                    self.log_message(f"❌ Touch error at ({x}, {y}): {str(e)}")
                    self.clicks_failed += 1
                    self.update_stats_display()
                    time.sleep(1)
        
        except Exception as e:
            self.log_message(f"❌ Touch test error: {str(e)}")
        
        self.log_message(f"📸 Coordinate test completed - Success: {self.clicks_successful}, Failed: {self.clicks_failed}")
        
    def open_instagram(self):
        device_id = self.device_var.get()
        if not device_id:
            self.log_message("❌ No device selected")
            return
        
        self.log_message(f"📱 Opening Instagram on {device_id}...")
        
        try:
            # Force stop Instagram first
            subprocess.run(['adb', '-s', device_id, 'shell', 'am', 'force-stop', 'com.instagram.android'], 
                         capture_output=True, text=True, timeout=5)
            time.sleep(1)
            
            # Start Instagram
            result = subprocess.run(['adb', '-s', device_id, 'shell', 'monkey', '-p', 'com.instagram.android', '-c', 
                                   'android.intent.category.LAUNCHER', '1'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.log_message("✅ Instagram opened successfully!")
                time.sleep(5)  # Wait for app to fully load
            else:
                self.log_message(f"❌ Failed to open Instagram: {result.stderr}")
                
        except Exception as e:
            self.log_message(f"❌ Error opening Instagram: {str(e)}")
        
    def start_bot(self):
        if self.bot_running:
            return
            
        device_id = self.device_var.get()
        target_account = self.targets_var.get()
        
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
        
        self.log_message(f"🚀 Instagram bot started on {device_id}")
        self.log_message(f"🎯 Target: @{target_account}")
        
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
        self.posts_liked = 0
        self.clicks_successful = 0
        self.clicks_failed = 0
        self.start_time = None
        self.update_stats_display()
        self.status_var.set("Ready to start")
        self.log_message("🔄 Statistics reset")
        
    def run_bot(self):
        try:
            device_id = self.device_var.get()
            target_account = self.targets_var.get()
            
            self.log_message("🤖 Starting precise Instagram automation...")
            self.log_message("📊 Strategy: Follow target account directly")
            
            # Open Instagram first
            self.open_instagram()
            
            # Wait for Instagram to load
            time.sleep(3)
            
            # Step 1: Go to home screen first
            self.log_message("🏠 Going to home screen...")
            result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'keyevent', 'KEYCODE_HOME'], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                self.log_message("✅ Home screen reached")
            time.sleep(2)
            
            # Step 2: Tap search bar (try multiple positions)
            self.log_message("🔍 Tapping search bar...")
            search_positions = [
                (200, 120, "center search"),
                (180, 100, "left search"),
                (220, 100, "right search"),
                (200, 150, "high search"),
                (200, 90, "very high search")
            ]
            
            search_found = False
            for x, y in search_positions:
                self.log_message(f"👆 Trying search at ({x}, {y})")
                result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)], 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    self.log_message(f"✅ Search bar found at ({x}, {y})")
                    search_found = True
                    self.clicks_successful += 1
                    break
                else:
                    self.log_message(f"❌ Search failed at ({x}, {y})")
                    self.clicks_failed += 1
                
                time.sleep(1)
            
            if not search_found:
                self.log_message("❌ Could not find search bar")
                return
            
            self.update_stats_display()
            time.sleep(2)
            
            # Step 3: Type target username
            self.log_message(f"⌨️ Typing @{target_account}...")
            result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'text', target_account], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                self.log_message(f"✅ Username typed: @{target_account}")
            time.sleep(2)
            
            # Step 4: Press enter
            self.log_message("⏎ Pressing enter...")
            result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'keyevent', 'KEYCODE_ENTER'], 
                                  capture_output=True, text=True, timeout=3)
            time.sleep(3)
            
            # Step 5: Look for user result and tap
            self.log_message("👆 Looking for user result...")
            result_positions = [
                (200, 250, "first result"),
                (200, 300, "second result"),
                (200, 350, "third result"),
                (200, 400, "fourth result")
            ]
            
            user_found = False
            for x, y in result_positions:
                self.log_message(f"👆 Trying user result at ({x}, {y})")
                result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)], 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    self.log_message(f"✅ User result found at ({x}, {y})")
                    user_found = True
                    self.clicks_successful += 1
                    break
                else:
                    self.log_message(f"❌ User result failed at ({x}, {y})")
                    self.clicks_failed += 1
                
                time.sleep(1)
            
            if not user_found:
                self.log_message("❌ Could not find user result")
                return
            
            self.update_stats_display()
            time.sleep(4)
            
            # Step 6: Wait for profile to load
            self.log_message("⏱️ Waiting for profile to load...")
            time.sleep(4)
            
            # Step 7: Look for follow button (try multiple positions)
            self.log_message("👥 Looking for follow button...")
            follow_positions = [
                (500, 200, "right follow"),
                (450, 180, "left follow"),
                (480, 220, "center follow"),
                (400, 250, "lower follow"),
                (350, 200, "upper follow"),
                (300, 300, "middle follow")
            ]
            
            follow_found = False
            for x, y in follow_positions:
                self.log_message(f"👆 Trying follow button at ({x}, {y})")
                result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)], 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    self.log_message(f"✅ Follow button found at ({x}, {y})")
                    follow_found = True
                    self.clicks_successful += 1
                    break
                else:
                    self.log_message(f"❌ Follow button failed at ({x}, {y})")
                    self.clicks_failed += 1
                
                time.sleep(1)
            
            if follow_found:
                self.log_message("✅ Successfully followed @{target_account}!")
                self.followers_gained += 1
                self.update_stats_display()
            else:
                self.log_message(f"❌ Could not find follow button for @{target_account}")
            
            # Step 8: Test liking posts
            if self.likes_given < 10:  # Like max 10 posts
                self.log_message("❤️ Testing post likes...")
                
                # Scroll down to find posts
                for scroll_attempt in range(2):
                    self.log_message(f"📜 Scroll {scroll_attempt + 1}")
                    result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'swipe', '200', '400', '200', '200', '500'], 
                                          capture_output=True, text=True, timeout=3)
                    time.sleep(2)
                
                # Try to like posts
                for like_attempt in range(3):
                    if self.likes_given >= 10:
                        break
                            
                    self.log_message(f"❤️ Like attempt {like_attempt + 1}")
                    like_positions = [(200, 300), (250, 350), (300, 400)]
                    
                    for x, y in like_positions:
                        self.log_message(f"👆 Trying post like at ({x}, {y})")
                        result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)], 
                                                  capture_output=True, text=True, timeout=3)
                        if result.returncode == 0:
                            # Double tap to like
                            time.sleep(0.5)
                            result2 = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)], 
                                                         capture_output=True, text=True, timeout=3)
                            if result2.returncode == 0:
                                self.likes_given += 1
                                self.posts_liked += 1
                                self.update_stats_display()
                                self.log_message(f"✅ Post liked! (Total: {self.likes_given})")
                                break
                        time.sleep(1)
                    time.sleep(1)
                
            self.log_message(f"📊 Session completed: {self.followers_gained} follows, {self.likes_given} likes")
            
            if self.bot_running:
                self.log_message("🎉 Instagram automation completed!")
            else:
                self.log_message("🛑 Instagram automation stopped early")
                
        except Exception as e:
            self.log_message(f"❌ Instagram automation error: {str(e)}")
        finally:
            self.bot_running = False
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.status_var.set("Bot finished"))

if __name__ == "__main__":
    root = tk.Tk()
    app = PreciseInstagramBotFixed(root)
    root.mainloop()
