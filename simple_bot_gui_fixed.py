import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import random
from datetime import datetime
import uiautomator2 as u2
import subprocess
import re

class SimpleBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖️ Simple Instagram Bot")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        self.bot_running = False
        self.bot_thread = None
        self.device = None
        self.device_id = None
        
        # Bot statistics
        self.stats = {
            'followers_gained': 0,
            'likes_given': 0,
            'accounts_processed': 0,
            'start_time': None
        }
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖️ Simple Instagram Bot", 
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
        
        # Runtime
        ttk.Label(stats_grid, text="⏱️ Runtime:", font=('Helvetica', 12, 'bold')).grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.runtime_var = tk.StringVar(value="0s")
        ttk.Label(stats_grid, textvariable=self.runtime_var, font=('Helvetica', 14, 'bold'), 
                 foreground='#9b59b6').grid(row=1, column=3, sticky='w', padx=5, pady=2)
        
        # Device Connection Frame
        device_frame = ttk.LabelFrame(main_frame, text="📱 Device Connection")
        device_frame.pack(fill=tk.X, pady=(0, 15))
        
        device_grid = ttk.Frame(device_frame)
        device_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Device ID
        ttk.Label(device_grid, text="Device ID:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.device_id_var = tk.StringVar(value='emulator-5554')
        ttk.Entry(device_grid, textvariable=self.device_id_var, width=20).grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Button(device_grid, text="🔍 Connect", command=self.connect_device).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(device_grid, text="🧪 Test", command=self.test_connection).grid(row=0, column=3, padx=5, pady=5)
        self.device_status_var = tk.StringVar(value="Not connected")
        ttk.Label(device_grid, textvariable=self.device_status_var, foreground='#e74c3c').grid(row=0, column=4, sticky='w', padx=5, pady=5)
        
        # Settings Frame
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Settings")
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        settings_grid = ttk.Frame(settings_frame)
        settings_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Username
        ttk.Label(settings_grid, text="Username:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.username_var = tk.StringVar(value='younghadene')
        ttk.Entry(settings_grid, textvariable=self.username_var, width=20).grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        # Target Accounts
        ttk.Label(settings_grid, text="Target Account:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.targets_var = tk.StringVar(value='champagnepapi')
        ttk.Entry(settings_grid, textvariable=self.targets_var, width=40).grid(row=1, column=1, columnspan=2, sticky='ew', padx=5, pady=5)
        
        # Daily Limits
        ttk.Label(settings_grid, text="Daily Follow Limit:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.follow_limit_var = tk.StringVar(value='200')
        ttk.Entry(settings_grid, textvariable=self.follow_limit_var, width=10).grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(settings_grid, text="Daily Like Limit:").grid(row=2, column=2, sticky='w', padx=5, pady=5)
        self.like_limit_var = tk.StringVar(value='50')
        ttk.Entry(settings_grid, textvariable=self.like_limit_var, width=10).grid(row=2, column=3, sticky='w', padx=5, pady=5)
        
        # Followers to process per account
        ttk.Label(settings_grid, text="Followers per Account:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.followers_per_account_var = tk.StringVar(value='10')
        ttk.Entry(settings_grid, textvariable=self.followers_per_account_var, width=10).grid(row=3, column=1, sticky='w', padx=5, pady=5)
        
        # Stay in followers list option
        self.stay_in_followers_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_grid, text="Stay in Followers List", variable=self.stay_in_followers_var).grid(row=4, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        # Control Panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="🚀 Start Bot", command=self.start_bot)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="🛑 Stop Bot", command=self.stop_bot, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="🔄 Reset Stats", command=self.reset_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="👥 Go to Following", command=self.go_to_following_tab).pack(side=tk.LEFT, padx=5)
        
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
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def update_stats_display(self):
        self.followers_var.set(str(self.stats['followers_gained']))
        self.likes_var.set(str(self.stats['likes_given']))
        self.accounts_var.set(str(self.stats['accounts_processed']))
        
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
        
    def test_connection(self):
        """Test device connection without blocking UI"""
        if not self.device:
            messagebox.showerror("Error", "Please connect to a device first!")
            return
            
        def test_thread():
            try:
                self.log_message("🧪 Testing device connection...")
                
                # Test device wake up
                self.device.screen_on()
                time.sleep(1)
                
                # Test screenshot
                screenshot = self.device.screenshot()
                if screenshot:
                    self.log_message("✅ Screenshot test passed")
                
                # Test app launch
                self.log_message("📱 Testing Instagram launch...")
                self.device.app_start("com.instagram.android")
                time.sleep(3)
                
                # Check if Instagram is running
                current_app = self.device.app_current()
                if 'instagram' in str(current_app.get('package', '')).lower():
                    self.log_message("✅ Instagram launch test passed")
                    self.device.app_stop("com.instagram.android")
                else:
                    self.log_message("⚠️ Instagram may not be installed")
                
                self.log_message("🎉 Connection test completed successfully!")
                
            except Exception as e:
                self.log_message(f"❌ Test failed: {str(e)}")
        
        # Run test in background thread
        test_thread = threading.Thread(target=test_thread)
        test_thread.daemon = True
        test_thread.start()
    
    def connect_device(self):
        """Connect to Android emulator"""
        try:
            device_id = self.device_id_var.get()
            self.log_message(f"🔌 Connecting to device: {device_id}")
            self.device_status_var.set("Connecting...")
            self.root.update()
            
            # Check if device is available
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
            if device_id not in result.stdout:
                self.log_message(f"❌ Device {device_id} not found. Available devices:")
                for line in result.stdout.split('\n')[1:]:
                    if line.strip():
                        self.log_message(f"   {line}")
                self.device_status_var.set("Device not found")
                return
            
            # Connect to device using uiautomator2
            self.device = u2.connect(device_id)
            self.device_id = device_id
            
            # Test connection
            device_info = self.device.info
            self.log_message(f"✅ Connected to {device_info.get('brand', 'Unknown')} {device_info.get('model', 'Device')}")
            self.log_message(f"📱 Android version: {device_info.get('version', 'Unknown')}")
            
            self.device_status_var.set("Connected")
            self.log_message("🎯 Device ready for Instagram automation")
            
        except Exception as e:
            self.log_message(f"❌ Connection failed: {str(e)}")
            self.device_status_var.set("Connection failed")
    
    def start_bot(self):
        if self.bot_running:
            return
            
        if not self.device:
            messagebox.showerror("Error", "Please connect to a device first!")
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
        
        # Wait a moment for the bot thread to recognize the stop
        time.sleep(0.5)
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Bot stopped")
        
        self.log_message("🛑 Bot stopped by user")
        
    def reset_stats(self):
        self.stats = {
            'followers_gained': 0,
            'likes_given': 0,
            'accounts_processed': 0,
            'start_time': None
        }
        self.update_stats_display()
        self.runtime_var.set("0s")
        self.log_message("🔄 Statistics reset")
        
    def run_bot(self):
        try:
            username = self.username_var.get()
            target_account = self.targets_var.get().strip()
            follow_limit = int(self.follow_limit_var.get())
            like_limit = int(self.like_limit_var.get())
            followers_per_account = int(self.followers_per_account_var.get())
            
            self.log_message(f"👤 Started bot for user: {username}")
            self.log_message(f"🎯 Target account: @{target_account}")
            self.log_message(f"📊 Limits: {follow_limit} follows/day, {like_limit} likes/day")
            self.log_message(f"👥 Will process {followers_per_account} followers per account")
            
            # Wake up device and unlock if needed
            self.device.screen_on()
            time.sleep(2)
            
            if not self.device.info.get('screenOn', True):
                self.device.press("power")
                time.sleep(2)
            
            # Open Instagram
            self.log_message("📱 Opening Instagram app...")
            self.device.app_start("com.instagram.android")
            time.sleep(5)
            
            # Process the single target account
            try:
                # Search for user
                self.log_message(f"🔍 Searching for @{target_account}...")
                if not self._search_user(target_account):
                    return
                
                # Go to their followers list
                self.log_message(f"👥 Opening followers list for @{target_account}...")
                if self._open_followers_list():
                    # Ensure we're in the Followers tab, not Following tab
                    self._ensure_in_followers_tab()
                    
                    # Process followers
                    followers_processed = self._process_followers(target_account, followers_per_account, follow_limit, like_limit)
                    self.log_message(f"✅ Processed {followers_processed} followers from @{target_account}")
                else:
                    self.log_message(f"❌ Could not open followers list for @{target_account}")
                
                self.stats['accounts_processed'] += 1
                self.update_stats_display()
                
            except Exception as e:
                self.log_message(f"❌ Error processing @{target_account}: {str(e)}")
                pass
            
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
    
    def _open_followers_list(self):
        """Open followers list of current profile"""
        try:
            # Look for followers button
            followers_selectors = [
                "com.instagram.android:id/row_profile_header_followers_container",
                "com.instagram.android:id/followers_container",
                "//android.widget.TextView[@text='followers']"
            ]
            
            for selector in followers_selectors:
                try:
                    if selector.startswith("//"):
                        followers_btn = self.device.xpath(selector)
                    else:
                        followers_btn = self.device(resourceId=selector)
                    
                    if followers_btn.exists:
                        followers_btn.click()
                        time.sleep(3)
                        return True
                except:
                    continue
            
            # Try clicking on followers count by coordinates
            self.log_message("🔄 Trying coordinate-based followers click...")
            self.device.click(400, 300)  # Approximate followers button location
            time.sleep(3)
            return True
            
        except Exception as e:
            self.log_message(f"❌ Error opening followers list: {str(e)}")
            return False
    
    def _click_follower_profile(self):
        """Click on follower profile to open it"""
        try:
            # Click on center of follower row
            self.device.click(540, 400)  # Center of screen for follower row
            time.sleep(2)
            return True
        except Exception as e:
            return False
    
    def go_to_following_tab(self):
        """Navigate to Following tab on Instagram"""
        try:
            self.log_message("🔄 Navigating to Following tab...")
            
            # Click on profile tab to go to your profile
            profile_tab = self.device(resourceId="com.instagram.android:id/tab_bar").child(index=4)
            if profile_tab.exists:
                profile_tab.click()
                time.sleep(2)
            else:
                # Try alternative profile button
                profile_btn = self.device(description="Profile")
                if profile_btn.exists:
                    profile_btn.click()
                    time.sleep(2)
            
            # Look for Following tab/button
            following_selectors = [
                "com.instagram.android:id/following_tab",
                ("com.instagram.android:id/tab_bar").child(index=2),
                "//android.widget.TextView[@text='Following']",
                "//android.widget.Button[@text='Following']"
            ]
            
            for selector in following_selectors:
                try:
                    if selector.startswith("//"):
                        following_tab = self.device.xpath(selector)
                    else:
                        following_tab = self.device(resourceId=selector)
                    
                    if following_tab.exists:
                        following_tab.click()
                        time.sleep(2)
                        self.log_message("✅ Successfully navigated to Following tab")
                        return True
                except:
                    continue
            
            # Try coordinate-based approach
            self.log_message("🔄 Trying coordinate-based Following tab click...")
            self.device.click(200, 300)  # Approximate Following tab location
            time.sleep(2)
            self.log_message("✅ Attempted to navigate to Following tab")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Error navigating to Following tab: {str(e)}")
            return False
    
    def _search_user(self, username):
        """Search for a user on Instagram"""
        try:
            # Click search tab
            search_tab = self.device(resourceId="com.instagram.android:id/tab_bar").child(index=1)
            if search_tab.exists:
                search_tab.click()
                time.sleep(2)
            else:
                # Try alternative search button
                search_btn = self.device(description="Search and Explore")
                if search_btn.exists:
                    search_btn.click()
                    time.sleep(2)
            
            # Click search box
            search_box = self.device(resourceId="com.instagram.android:id/action_bar_search_edit_text")
            if search_box.exists:
                search_box.click()
                time.sleep(1)
                search_box.set_text(username)
                time.sleep(3)
            else:
                # Try alternative search box
                alt_search = self.device(className="android.widget.EditText")
                if alt_search.exists:
                    alt_search.click()
                    time.sleep(1)
                    alt_search.set_text(username)
                    time.sleep(3)
            
            # Click on user in search results
            user_result = self.device(text=username)
            if user_result.exists:
                user_result.click()
                time.sleep(3)
                return True
            else:
                self.log_message(f"❌ Could not find @{username} in search results")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Search error: {str(e)}")
            return False
    
    def _ensure_in_followers_tab(self):
        """Make sure we're in the Followers tab, not Following tab"""
        try:
            self.log_message("🔄 Ensuring we're in Followers tab...")
            
            # Look for Followers tab indicator
            followers_indicators = [
                "//android.widget.TextView[@text='Followers']",
                "//android.widget.Button[@text='Followers']",
                "com.instagram.android:id/followers_tab"
            ]
            
            for indicator in followers_indicators:
                try:
                    if indicator.startswith("//"):
                        followers_elem = self.device.xpath(indicator)
                    else:
                        followers_elem = self.device(resourceId=indicator)
                    
                    if followers_elem.exists:
                        # Check if it's selected/active
                        if followers_elem.info.get('selected', False):
                            self.log_message("✅ Already in Followers tab")
                            return True
                        else:
                            # Click on Followers tab
                            followers_elem.click()
                            time.sleep(2)
                            self.log_message("✅ Switched to Followers tab")
                            return True
                except:
                    continue
            
            # Try coordinate-based approach - click on left side of profile
            self.log_message("🔄 Trying coordinate-based Followers tab click...")
            self.device.click(300, 300)  # Approximate Followers tab location
            time.sleep(2)
            self.log_message("✅ Attempted to switch to Followers tab")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Error ensuring Followers tab: {str(e)}")
            return False

    def _process_followers(self, account, max_followers, follow_limit, like_limit):
        """Process followers from followers list - with option to stay in list"""
        followers_processed = 0
        stay_in_followers = self.stay_in_followers_var.get()
        
        try:
            self.log_message(f"👥 Starting to process {max_followers} followers from @{account}")
            self.log_message(f"🔄 Stay in followers mode: {'ON' if stay_in_followers else 'OFF'}")
            
            # Scroll through followers list
            for i in range(max_followers):
                if not self.bot_running or self.stats['followers_gained'] >= follow_limit:
                    self.log_message("🛑 Stopping follower processing - limit reached or bot stopped")
                    break
                
                # Check if bot was stopped during processing
                if not self.bot_running:
                    self.log_message("🛑 Bot stop detected during follower processing")
                    break
                
                try:
                    if stay_in_followers:
                        # Stay in followers list - just follow directly
                        self.log_message(f"👤 Following follower {i+1} directly from list...")
                        if self._follow_follower_from_list():
                            self.stats['followers_gained'] += 1
                            followers_processed += 1
                            self.log_message(f"✅ Followed follower #{i+1}")
                            self.update_stats_display()
                        else:
                            self.log_message(f"⏭️ Already following or couldn't find follow button for follower #{i+1}")
                    else:
                        # Original behavior - click profile, follow, go back
                        self.log_message(f"👤 Clicking follower {i+1} profile...")
                        if self._click_follower_from_list():
                            time.sleep(2)
                            
                            if self.stats['followers_gained'] < follow_limit:
                                if self._follow_user_from_profile():
                                    self.stats['followers_gained'] += 1
                                    followers_processed += 1
                                    self.log_message(f"✅ Followed follower #{i+1}")
                                    self.update_stats_display()
                                else:
                                    self.log_message(f"⏭️ Already following follower #{i+1}")
                            
                            # Go back to followers list
                            self.log_message("🔙 Going back to followers list...")
                            self.device.press("back")
                            time.sleep(2)
                    
                    # Check if bot was stopped after each action
                    if not self.bot_running:
                        self.log_message("🛑 Bot stop detected - stopping processing")
                        break
                    
                    # Scroll down slowly to next followers - smaller scroll distance
                    self.log_message(f"⬇️ Scrolling down slowly to see more followers...")
                    self.device.swipe(540, 650, 540, 450, 0.3)  # Slower, smaller scroll
                    time.sleep(random.uniform(3, 5))  # Longer pause between scrolls
                    
                    # Every 3 followers, do a bigger scroll to load new content
                    if (i + 1) % 3 == 0:
                        self.log_message("🔄 Doing bigger scroll to load new followers...")
                        self.device.swipe(540, 600, 540, 300, 0.4)
                        time.sleep(random.uniform(2, 3))
                    
                except Exception as e:
                    self.log_message(f"❌ Error processing follower {i+1}: {str(e)}")
                    continue
            
            self.log_message(f"🎉 Finished processing followers from @{account}. Total followed: {followers_processed}")
            return followers_processed
            
        except Exception as e:
            self.log_message(f"❌ Error in process_followers: {str(e)}")
            return followers_processed
    
    def _follow_follower_from_list(self):
        """Follow follower directly from followers list"""
        try:
            # Look for Follow buttons in followers list
            follow_selectors = [
                "com.instagram.android:id/follow_list_button",
                "com.instagram.android:id/button_text",
                "//android.widget.TextView[@text='Follow']",
                "//android.widget.Button[@text='Follow']"
            ]
            
            for selector in follow_selectors:
                try:
                    if selector.startswith("//"):
                        follow_btns = self.device.xpath(selector)
                    else:
                        follow_btns = self.device(resourceId=selector)
                    
                    if follow_btns.exists:
                        # Click first visible follow button
                        buttons = follow_btns if hasattr(follow_btns, '__iter__') else [follow_btns]
                        for button in buttons:
                            try:
                                button.click()
                                time.sleep(2)
                                return True
                            except:
                                continue
                except:
                    continue
            
            # Try coordinate-based follow button click
            self.log_message("🔄 Trying coordinate-based follow click...")
            self.device.click(800, 350)  # Follow button is usually on the right side
            time.sleep(2)
            return True
            
        except Exception as e:
            self.log_message(f"❌ Error following from list: {str(e)}")
            return False
    
    def _search_user(self, username):
        """Search for a user on Instagram"""
        try:
            # Click search tab
            search_tab = self.device(resourceId="com.instagram.android:id/tab_bar").child(index=1)
            if search_tab.exists:
                search_tab.click()
                time.sleep(2)
            else:
                # Try alternative search button
                search_btn = self.device(description="Search and Explore")
                if search_btn.exists:
                    search_btn.click()
                    time.sleep(2)
            
            # Click search box
            search_box = self.device(resourceId="com.instagram.android:id/action_bar_search_edit_text")
            if search_box.exists:
                search_box.click()
                time.sleep(1)
                search_box.set_text(username)
                time.sleep(3)
            else:
                # Try alternative search box
                alt_search = self.device(className="android.widget.EditText")
                if alt_search.exists:
                    alt_search.click()
                    time.sleep(1)
                    alt_search.set_text(username)
                    time.sleep(3)
            
            # Click on user in search results
            user_result = self.device(text=username)
            if user_result.exists:
                user_result.click()
                time.sleep(3)
                return True
            else:
                self.log_message(f"❌ Could not find @{username} in search results")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Search error: {str(e)}")
            return False

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleBotGUI(root)
    root.mainloop()
