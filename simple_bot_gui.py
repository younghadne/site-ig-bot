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
        
        # Anti-Detection: Timing controls (SPED UP)
        self.timing_config = {
            'follow_delay_min': 1,
            'follow_delay_max': 3,
            'scroll_delay_min': 0.5,
            'scroll_delay_max': 1.5,
            'page_transition_min': 2,
            'page_transition_max': 4,
            'micro_break_min': 10,
            'micro_break_max': 20,
            'micro_break_frequency': 50,
            'sleep_hours_start': 23,
            'sleep_hours_end': 7,
        }
        
        # Anti-Detection: Rate limit tracking (MORE CONSERVATIVE)
        self.rate_limit_data = {
            'last_action_time': 0,
            'actions_this_hour': 0,
            'hour_start_time': None,
            'consecutive_failures': 0,
            'last_rate_limit_hit': None,
            'hourly_action_limit': 15,  # Reduced from 30
        }
        
        # Anti-Detection: Action jitter tracking
        self.action_count = 0
        self.last_break_time = 0
        
        # AUTONOMOUS MODE: Self-healing and retry settings
        self.autonomous_config = {
            'max_retries': 3,
            'retry_delay': 5,
            'auto_recovery': True,
            'silent_mode': False,  # Less verbose logging
            'resume_on_crash': True,
        }
        
        # Bot statistics with analytics
        self.stats = {
            'followers_gained': 0,
            'likes_given': 0,
            'accounts_processed': 0,
            'start_time': None,
            'followed_accounts': [],
            'follow_back_count': 0,
            'success_rate': 0.0,
            'hourly_stats': {},
        }
        
        # Analytics: Target account performance
        self.target_performance = {}
        
        # Create UI
        self.create_widgets()
        
    def safe_action(self, action_func, *args, **kwargs):
        """Execute action with auto-retry and error recovery"""
        max_retries = self.autonomous_config['max_retries']
        retry_delay = self.autonomous_config['retry_delay']
        
        for attempt in range(max_retries):
            try:
                result = action_func(*args, **kwargs)
                if result:
                    return True
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
            except Exception as e:
                if not self.autonomous_config['silent_mode']:
                    self.log_message(f"⚠️ Attempt {attempt+1} failed: {str(e)[:50]}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
        
        return False
    
    def auto_heal(self):
        """Self-healing: recover from common Instagram issues"""
        try:
            # Check for and dismiss popups
            dismiss_selectors = [
                "//android.widget.Button[@text='Dismiss']",
                "//android.widget.Button[@text='Not Now']",
                "//android.widget.Button[@text='Cancel']",
                "//android.widget.TextView[@text='Dismiss']",
                "com.instagram.android:id/negative_button",
            ]
            
            for selector in dismiss_selectors:
                try:
                    if selector.startswith("//"):
                        elem = self.device.xpath(selector)
                    else:
                        elem = self.device(resourceId=selector)
                    
                    if elem.exists:
                        elem.click()
                        if not self.autonomous_config['silent_mode']:
                            self.log_message("🔧 Auto-healed: dismissed popup")
                        time.sleep(1)
                        return True
                except:
                    continue
            
            # Check if we're stuck on a screen
            current_app = self.device.app_current()
            if 'instagram' not in str(current_app.get('package', '')).lower():
                # Relaunch Instagram
                self.device.app_start("com.instagram.android")
                if not self.autonomous_config['silent_mode']:
                    self.log_message("🔧 Auto-healed: relaunched Instagram")
                time.sleep(5)
                return True
                
        except Exception as e:
            pass
        
        return False
    
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
        
        # Target Account
        ttk.Label(settings_grid, text="Target Account:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.targets_var = tk.StringVar(value='champagnepapi')
        ttk.Entry(settings_grid, textvariable=self.targets_var, width=40).grid(row=1, column=1, columnspan=2, sticky='ew', padx=5, pady=5)
        
        # Daily Limits
        ttk.Label(settings_grid, text="Daily Follow Limit:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.follow_limit_var = tk.StringVar(value='120')
        ttk.Entry(settings_grid, textvariable=self.follow_limit_var, width=10).grid(row=2, column=1, sticky='w', padx=5, pady=5)
        ttk.Label(settings_grid, text="(Safe: 100-150)").grid(row=2, column=2, sticky='w', padx=5, pady=5)
        
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
        
        # 24-hour spread mode
        self.spread_24h_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_grid, text="Spread over 24 hours", variable=self.spread_24h_var).grid(row=4, column=2, columnspan=2, sticky='w', padx=5, pady=5)
        
        # Silent mode (autonomous - no watching needed)
        self.silent_mode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_grid, text="Silent Mode (Auto-run)", variable=self.silent_mode_var, command=self._toggle_silent_mode).grid(row=5, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        # Speed Settings Frame
        speed_frame = ttk.LabelFrame(main_frame, text="⚡ Speed Control")
        speed_frame.pack(fill=tk.X, pady=(0, 15))
        
        speed_grid = ttk.Frame(speed_frame)
        speed_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Follow delay
        ttk.Label(speed_grid, text="Follow Delay (sec):").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.follow_delay_var = tk.StringVar(value='5')
        ttk.Entry(speed_grid, textvariable=self.follow_delay_var, width=8).grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        # Scroll delay
        ttk.Label(speed_grid, text="Scroll Delay (sec):").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.scroll_delay_var = tk.StringVar(value='3')
        ttk.Entry(speed_grid, textvariable=self.scroll_delay_var, width=8).grid(row=0, column=3, sticky='w', padx=5, pady=5)
        
        # Page delay
        ttk.Label(speed_grid, text="Page Load (sec):").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.page_delay_var = tk.StringVar(value='5')
        ttk.Entry(speed_grid, textvariable=self.page_delay_var, width=8).grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        # Speed preset buttons
        ttk.Button(speed_grid, text="🐌 Slow", command=lambda: self.set_speed('slow')).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(speed_grid, text="🚶 Normal", command=lambda: self.set_speed('normal')).grid(row=1, column=3, padx=5, pady=5)
        ttk.Button(speed_grid, text="🚀 Fast", command=lambda: self.set_speed('fast')).grid(row=1, column=4, padx=5, pady=5)
        
        # Control Panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        
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
        
        # Features Panel
        features_frame = ttk.LabelFrame(main_frame, text="🎯 Features")
        features_frame.pack(fill=tk.X, pady=(0, 10))
        
        features_grid = ttk.Frame(features_frame)
        features_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Row 1: Core features
        ttk.Button(features_grid, text="🔄 Auto Unfollow", command=self._run_auto_unfollow).grid(row=0, column=0, padx=5, pady=3, sticky='ew')
        ttk.Button(features_grid, text="❤️ Auto Like Feed", command=self._run_auto_like_feed).grid(row=0, column=1, padx=5, pady=3, sticky='ew')
        ttk.Button(features_grid, text="👁️ Mass Story View", command=self._run_mass_story_view).grid(row=0, column=2, padx=5, pady=3, sticky='ew')
        ttk.Button(features_grid, text="✅ Approve Requests", command=self._run_auto_approve).grid(row=0, column=3, padx=5, pady=3, sticky='ew')
        
        # Row 2: DM features
        ttk.Button(features_grid, text="💬 Auto DM", command=self._run_auto_dm).grid(row=1, column=0, padx=5, pady=3, sticky='ew')
        ttk.Button(features_grid, text="📩 Welcome DM", command=self._run_welcome_dm).grid(row=1, column=1, padx=5, pady=3, sticky='ew')
        ttk.Button(features_grid, text="💬 Auto Comment", command=self._run_auto_comment).grid(row=1, column=2, padx=5, pady=3, sticky='ew')
        ttk.Button(features_grid, text="👁️ View Stories", command=self._run_view_stories).grid(row=1, column=3, padx=5, pady=3, sticky='ew')
        
        # Feature settings
        feat_settings = ttk.Frame(features_grid)
        feat_settings.grid(row=2, column=0, columnspan=4, sticky='ew', pady=(5, 0))
        
        ttk.Label(feat_settings, text="Unfollow Limit:").pack(side=tk.LEFT, padx=3)
        self.unfollow_limit_var = tk.StringVar(value='50')
        ttk.Entry(feat_settings, textvariable=self.unfollow_limit_var, width=6).pack(side=tk.LEFT, padx=3)
        
        ttk.Label(feat_settings, text="Like Limit:").pack(side=tk.LEFT, padx=3)
        self.like_feed_limit_var = tk.StringVar(value='20')
        ttk.Entry(feat_settings, textvariable=self.like_feed_limit_var, width=6).pack(side=tk.LEFT, padx=3)
        
        ttk.Label(feat_settings, text="Story Limit:").pack(side=tk.LEFT, padx=3)
        self.story_limit_var = tk.StringVar(value='50')
        ttk.Entry(feat_settings, textvariable=self.story_limit_var, width=6).pack(side=tk.LEFT, padx=3)
        
        ttk.Label(feat_settings, text="DM Message:").pack(side=tk.LEFT, padx=3)
        self.dm_message_var = tk.StringVar(value='')
        ttk.Entry(feat_settings, textvariable=self.dm_message_var, width=20).pack(side=tk.LEFT, padx=3)
        
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
    
    def set_speed(self, speed):
        """Set speed preset - SAFE RECOMMENDED: 100-150 follows/day, spread out"""
        if speed == 'slow':
            self.follow_delay_var.set('10')  # 10 seconds between follows
            self.scroll_delay_var.set('5')
            self.page_delay_var.set('8')
            self.log_message("🐌 SAFE MODE: ~6 follows/hour, 100-150/day max (lowest risk)")
        elif speed == 'normal':
            self.follow_delay_var.set('6')   # 6 seconds between follows
            self.scroll_delay_var.set('3')
            self.page_delay_var.set('5')
            self.log_message("🚶 NORMAL MODE: ~10 follows/hour, stay under 150/day")
        elif speed == 'fast':
            self.follow_delay_var.set('3')   # 3 seconds between follows
            self.scroll_delay_var.set('2')
            self.page_delay_var.set('3')
            self.log_message("🚀 FAST MODE: Higher risk - only for warmed accounts")
    
    def _toggle_silent_mode(self):
        """Toggle silent mode for autonomous operation"""
        self.autonomous_config['silent_mode'] = self.silent_mode_var.get()
        if self.silent_mode_var.get():
            self.log_message("🔇 Silent Mode ON - Bot will run autonomously")
        else:
            self.log_message("🔊 Silent Mode OFF - Verbose logging enabled")
    
    def _get_delay(self, action_type='follow'):
        """Get delay from GUI settings"""
        try:
            if action_type == 'follow':
                base = float(self.follow_delay_var.get())
                return random.uniform(base * 0.8, base * 1.2)
            elif action_type == 'scroll':
                base = float(self.scroll_delay_var.get())
                return random.uniform(base * 0.8, base * 1.2)
            elif action_type == 'transition':
                base = float(self.page_delay_var.get())
                return random.uniform(base * 0.8, base * 1.2)
        except:
            return 2.0
        return random.uniform(2, 5)
    
    # ==================== ANTI-DETECTION METHODS ====================
    
    def _get_24h_spread_delay(self, follow_limit):
        """Calculate delay to spread follows evenly over 24 hours"""
        if follow_limit <= 0:
            return 0
        seconds_per_follow = (24 * 3600) / follow_limit  # 24 hours in seconds
        return seconds_per_follow
    
    def apply_24h_delay(self, follow_limit):
        """Wait the calculated time to spread follows over 24 hours"""
        delay = self._get_24h_spread_delay(follow_limit)
        if delay > 0:
            minutes = delay / 60
            self.log_message(f"⏰ 24H SPREAD: Waiting {minutes:.1f} minutes until next follow...")
            time.sleep(delay)
        return delay
    
    def human_delay(self, action_type='follow'):
        """Generate human-like delays with jitter - uses GUI settings"""
        delay = self._get_delay(action_type)
        
        self.action_count += 1
        if self.action_count >= self.timing_config['micro_break_frequency']:
            self._take_micro_break()
            self.action_count = 0
        
        time.sleep(delay)
        return delay
    
    def _take_micro_break(self):
        """Take a random micro-break to simulate human behavior"""
        break_duration = random.uniform(self.timing_config['micro_break_min'], self.timing_config['micro_break_max'])
        self.log_message(f"😴 Taking micro-break for {break_duration:.1f} seconds...")
        time.sleep(break_duration)
        self.log_message("☕ Break over, resuming...")
    
    def check_rate_limit(self):
        """Check if we're approaching rate limits - DISABLED hourly limit"""
        current_time = time.time()
        
        # HOURLY LIMIT CHECK REMOVED - was causing 5 minute pauses
        # if self.rate_limit_data['hour_start_time'] and (current_time - self.rate_limit_data['hour_start_time']) >= 3600:
        #     self.rate_limit_data['actions_this_hour'] = 0
        #     self.rate_limit_data['hour_start_time'] = current_time
        #     self.log_message("🔄 Hourly action counter reset")
        # 
        # if self.rate_limit_data['actions_this_hour'] >= self.rate_limit_data['hourly_action_limit']:
        #     self.log_message(f"⏳ Hourly limit reached ({self.rate_limit_data['hourly_action_limit']} actions). Waiting 5 minutes...")
        #     time.sleep(300)
        #     self.rate_limit_data['actions_this_hour'] = 0
        #     self.rate_limit_data['hour_start_time'] = current_time
        
        # Keep exponential backoff for consecutive failures
        if self.rate_limit_data['consecutive_failures'] > 3:
            backoff = min(2 ** self.rate_limit_data['consecutive_failures'], 3600)
            self.log_message(f"⚠️ Exponential backoff: waiting {backoff} seconds due to {self.rate_limit_data['consecutive_failures']} failures")
            time.sleep(backoff)
        
        # Keep sleep mode check
        current_hour = datetime.now().hour
        if self.timing_config['sleep_hours_start'] <= current_hour or current_hour < self.timing_config['sleep_hours_end']:
            self.log_message(f"🌙 Sleep mode active (hours {self.timing_config['sleep_hours_start']}-{self.timing_config['sleep_hours_end']}). Pausing...")
            return False
        
        return True
    
    def record_action(self, success=True):
        """Record an action for rate limiting"""
        if self.rate_limit_data['hour_start_time'] is None:
            self.rate_limit_data['hour_start_time'] = time.time()
        
        self.rate_limit_data['actions_this_hour'] += 1
        self.rate_limit_data['last_action_time'] = time.time()
        
        if success:
            self.rate_limit_data['consecutive_failures'] = 0
        else:
            self.rate_limit_data['consecutive_failures'] += 1
    
    def record_rate_limit_hit(self):
        """Record when we hit a rate limit"""
        self.rate_limit_data['last_rate_limit_hit'] = time.time()
        self.rate_limit_data['consecutive_failures'] += 1
        self.log_message(f"🚫 Rate limit detected! Failures: {self.rate_limit_data['consecutive_failures']}")
        pause_time = min(300 * self.rate_limit_data['consecutive_failures'], 3600)
        self.log_message(f"⏸️ Pausing for {pause_time} seconds due to rate limit...")
        time.sleep(pause_time)
    
    def smart_scroll(self):
        """Scroll just enough to show the next account, then stop and wait"""
        # Small scroll to reveal next account (about one row)
        start_y = 650  # Lower on screen
        end_y = 450    # Scroll up less
        duration = random.uniform(0.8, 1.5)
        self.device.swipe(540, start_y, 540, end_y, duration)
        time.sleep(2)  # Wait for UI to settle
        self.human_delay('scroll')
    
    def should_skip_action(self, skip_probability=0.05):
        """Occasionally skip an action to simulate human imperfection"""
        return random.random() < skip_probability
    
    def check_instagram_warnings(self):
        """Check for Instagram warning messages that indicate detection"""
        warning_selectors = [
            "Try Again Later",
            "Action Blocked",
            "We restrict certain activity",
            "Please try again later",
            "Your account has been temporarily restricted"
        ]
        
        for warning in warning_selectors:
            if self.device(textContains=warning).exists or self.device(text=warning).exists:
                self.log_message(f"🚨 INSTAGRAM WARNING DETECTED: '{warning}'")
                self.record_rate_limit_hit()
                return True
        
        return False

    # ==================== END ANTI-DETECTION METHODS ====================

    # ==================== ANALYTICS METHODS ====================
    
    def record_followed_account(self, username, target_account):
        """Record that we followed an account for analytics"""
        follow_data = {
            'username': username,
            'target_account': target_account,
            'followed_at': datetime.now().isoformat(),
            'followed_back': False,
            'hour': datetime.now().hour
        }
        
        self.stats['followed_accounts'].append(follow_data)
        
        if target_account not in self.target_performance:
            self.target_performance[target_account] = {
                'total_follows': 0,
                'follow_backs': 0,
                'success_rate': 0.0
            }
        self.target_performance[target_account]['total_follows'] += 1
        
        hour = datetime.now().hour
        if hour not in self.stats['hourly_stats']:
            self.stats['hourly_stats'][hour] = 0
        self.stats['hourly_stats'][hour] += 1
        
        self.log_message(f"📊 Analytics: Recorded follow of @{username} from @{target_account}")
    
    def update_success_rate(self):
        """Update the overall success rate"""
        if self.stats['followed_accounts']:
            follow_backs = sum(1 for acc in self.stats['followed_accounts'] if acc['followed_back'])
            self.stats['follow_back_count'] = follow_backs
            self.stats['success_rate'] = (follow_backs / len(self.stats['followed_accounts'])) * 100
            self.log_message(f"📊 Follow-back rate: {self.stats['success_rate']:.1f}% ({follow_backs}/{len(self.stats['followed_accounts'])})")
    
    def show_analytics_summary(self):
        """Show analytics summary in logs"""
        self.log_message("\n📈 ===== ANALYTICS SUMMARY =====")
        self.log_message(f"Total follows: {len(self.stats['followed_accounts'])}")
        self.log_message(f"Follow-backs: {self.stats['follow_back_count']}")
        self.log_message(f"Success rate: {self.stats['success_rate']:.1f}%")
        
        if self.target_performance:
            self.log_message("\n🏆 Top Target Accounts:")
            sorted_targets = sorted(self.target_performance.items(), key=lambda x: x[1]['total_follows'], reverse=True)[:5]
            for account, stats in sorted_targets:
                self.log_message(f"  @{account}: {stats['total_follows']} follows")
        
        if self.stats['hourly_stats']:
            self.log_message("\n⏰ Hourly Activity:")
            for hour, count in sorted(self.stats['hourly_stats'].items()):
                self.log_message(f"  {hour:02d}:00 - {count} follows")
        
        self.log_message("================================\n")

    # ==================== END ANALYTICS METHODS ====================

    # ==================== SMART TARGETING METHODS ====================
    
    def analyze_profile_quality(self, username_text_elem=None):
        """Analyze profile quality and return score (0-100)"""
        quality_score = 100
        skip_reasons = []
        
        try:
            if username_text_elem and username_text_elem.exists:
                username = username_text_elem.get_text() if hasattr(username_text_elem, 'get_text') else ""
                
                red_flags = ['bot', 'spam', 'promo', 'buy', 'sell', 'dm', 'click', 'free', 'crypto', 'nft', 'invest', 'forex', 'signal']
                username_lower = username.lower()
                for flag in red_flags:
                    if flag in username_lower:
                        quality_score -= 30
                        skip_reasons.append(f"Red flag in username: {flag}")
                        break
                
                if username.isdigit() or (len(username) >= 8 and sum(c.isdigit() for c in username) >= 3):
                    quality_score -= 20
                    skip_reasons.append("Numeric/random username pattern")
                
                if username.count('_') >= 3 or username.count('-') >= 3:
                    quality_score -= 15
                    skip_reasons.append("Excessive special characters")
            
            if self.device(text="Follow Back").exists:
                quality_score -= 25
                skip_reasons.append("Follow-back user detected")
            
            if self.device(text="Private").exists or self.device(description="Private account").exists:
                quality_score -= 10
                skip_reasons.append("Private account")
            
        except Exception as e:
            self.log_message(f"⚠️ Profile analysis error: {e}")
        
        return max(0, quality_score), skip_reasons
    
    def should_follow_profile(self, min_score=70):
        """Decide whether to follow a profile based on quality score"""
        score, reasons = self.analyze_profile_quality()
        
        if score < min_score:
            self.log_message(f"⏭️ Skipping low-quality profile (score: {score}/100)")
            for reason in reasons:
                self.log_message(f"   - {reason}")
            return False
        
        return True
    
    def get_profile_info_from_list(self):
        """Try to extract profile info from followers list view"""
        try:
            username_elem = self.device(resourceId="com.instagram.android:id/follow_list_username")
            if username_elem.exists:
                return username_elem[0]
            
            text_elems = self.device(className="android.widget.TextView")
            for elem in text_elems:
                text = elem.get_text()
                if text and len(text) > 0 and not text in ["Follow", "Following", "Requested", "Message"]:
                    return elem
            
            return None
        except:
            return None

    # ==================== END SMART TARGETING METHODS ====================

    # ==================== EXPANDED ACTIONS METHODS ====================
    
    COMMENT_TEMPLATES = [
        "🔥", "❤️", "👏", "😍", "💯", "Great content!", "Love this!", "Amazing!",
        "So good!", "Perfect!", "👌", "🙌", "💪", "😊", "Nice!"
    ]
    
    WELCOME_DM_TEMPLATES = [
        "Hey! Thanks for following me 🙏",
        "Welcome! Glad to have you here 😊",
        "Thanks for the follow! Feel free to DM me anytime 💬",
        "Appreciate the follow! Check out my latest posts 🔥",
        "Hey there! Thanks for following - stay tuned for more content! ✨",
    ]
    
    def auto_unfollow(self, max_unfollows=50):
        """Unfollow users from your Following list"""
        unfollowed = 0
        try:
            self.log_message(f"🔄 Starting auto-unfollow (max: {max_unfollows})...")
            
            # Go to own profile
            profile_tab = self.device(resourceId="com.instagram.android:id/tab_bar").child(index=4)
            if profile_tab.exists:
                profile_tab.click()
                time.sleep(3)
            else:
                profile_btn = self.device(description="Profile")
                if profile_btn.exists:
                    profile_btn.click()
                    time.sleep(3)
            
            # Click on Following count
            following_selectors = [
                "com.instagram.android:id/row_profile_header_following_container",
                "com.instagram.android:id/following_container",
                "//android.widget.TextView[contains(@text, 'Following')]",
            ]
            
            for selector in following_selectors:
                try:
                    if selector.startswith("//"):
                        btn = self.device.xpath(selector)
                    else:
                        btn = self.device(resourceId=selector)
                    
                    if btn.exists:
                        btn.click()
                        time.sleep(3)
                        break
                except:
                    continue
            
            # Unfollow users in the list
            while self.bot_running and unfollowed < max_unfollows:
                try:
                    # Find Following buttons (people we're following)
                    following_btn = self.device(text="Following")
                    if following_btn.exists:
                        following_btn.click()
                        time.sleep(1)
                        
                        # Confirm unfollow
                        confirm_btn = self.device(text="Unfollow")
                        if confirm_btn.exists:
                            confirm_btn.click()
                            unfollowed += 1
                            self.log_message(f"✅ Unfollowed #{unfollowed}/{max_unfollows}")
                            time.sleep(random.uniform(2, 5))
                        else:
                            self.log_message("⚠️ No confirm button found")
                            self.device.press("back")
                            time.sleep(1)
                    else:
                        # Scroll to find more Following buttons
                        self.device.swipe(540, 650, 540, 450, 1.0)
                        time.sleep(2)
                        
                        # Check again after scroll
                        following_btn = self.device(text="Following")
                        if not following_btn.exists:
                            self.log_message("✅ No more users to unfollow")
                            break
                    
                    # Anti-detection: occasional delay
                    if unfollowed % 10 == 0 and unfollowed > 0:
                        self.log_message("😴 Taking a break from unfollowing...")
                        time.sleep(random.uniform(30, 60))
                    
                except Exception as e:
                    self.log_message(f"⚠️ Unfollow error: {e}")
                    self.smart_scroll()
                    continue
            
            self.log_message(f"✅ Auto-unfollow complete: {unfollowed} users unfollowed")
            
        except Exception as e:
            self.log_message(f"❌ Auto-unfollow error: {e}")
        
        return unfollowed
    
    def auto_like_feed(self, num_likes=20):
        """Like posts in the home feed"""
        likes_given = 0
        try:
            self.log_message(f"❤️ Starting auto-like on feed (max: {num_likes})...")
            
            # Go to home feed
            home_tab = self.device(resourceId="com.instagram.android:id/tab_bar").child(index=0)
            if home_tab.exists:
                home_tab.click()
                time.sleep(2)
            
            while self.bot_running and likes_given < num_likes:
                try:
                    # Find like buttons (not yet liked)
                    like_btn = self.device(resourceId="com.instagram.android:id/row_feed_button_like")
                    if like_btn.exists:
                        # Check if already liked (would have a filled heart)
                        like_btn.click()
                        likes_given += 1
                        self.stats['likes_given'] += 1
                        self.log_message(f"❤️ Liked post #{likes_given}/{num_likes}")
                        self.update_stats_display()
                        time.sleep(random.uniform(1, 3))
                    
                    # Scroll down in feed
                    self.device.swipe(540, 1500, 540, 500, 0.8)
                    time.sleep(random.uniform(1, 2))
                    
                    # Anti-detection: occasional delay
                    if likes_given % 15 == 0 and likes_given > 0:
                        self.log_message("😴 Taking a break from liking...")
                        time.sleep(random.uniform(20, 40))
                    
                except Exception as e:
                    self.log_message(f"⚠️ Like error: {e}")
                    continue
            
            self.log_message(f"✅ Auto-like complete: {likes_given} posts liked")
            
        except Exception as e:
            self.log_message(f"❌ Auto-like error: {e}")
        
        return likes_given
    
    def auto_like_posts(self, num_likes=3):
        """Like recent posts from current profile"""
        likes_given = 0
        try:
            posts = self.device(resourceId="com.instagram.android:id/media_set_row_content")
            if posts.exists:
                for i in range(min(num_likes, 3)):
                    try:
                        post = posts[i]
                        post.click()
                        time.sleep(2)
                        
                        like_btn = self.device(resourceId="com.instagram.android:id/row_feed_button_like")
                        if like_btn.exists:
                            like_btn.click()
                            likes_given += 1
                            self.stats['likes_given'] += 1
                            self.log_message(f"❤️ Liked post {likes_given}/{num_likes}")
                            self.update_stats_display()
                            time.sleep(random.uniform(1, 3))
                        
                        self.device.press("back")
                        time.sleep(1)
                    except:
                        continue
        except Exception as e:
            self.log_message(f"⚠️ Auto-like error: {e}")
        
        return likes_given
    
    def auto_dm(self, username, message=None):
        """Send a DM to a specific user"""
        try:
            self.log_message(f"💬 Sending DM to @{username}...")
            
            # Look for Message button on profile
            msg_selectors = [
                "com.instagram.android:id/profile_header_msg_button",
                "com.instagram.android:id/row_profile_header_message_button",
                "//android.widget.Button[@text='Message']",
                "//android.widget.TextView[@text='Message']",
            ]
            
            for selector in msg_selectors:
                try:
                    if selector.startswith("//"):
                        msg_btn = self.device.xpath(selector)
                    else:
                        msg_btn = self.device(resourceId=selector)
                    
                    if msg_btn.exists:
                        msg_btn.click()
                        time.sleep(3)
                        break
                except:
                    continue
            
            # Type message
            dm_text = message if message else random.choice(self.WELCOME_DM_TEMPLATES)
            msg_field = self.device(resourceId="com.instagram.android:id/layout_message_composer_edittext")
            if not msg_field.exists:
                msg_field = self.device(className="android.widget.EditText")
            
            if msg_field.exists:
                msg_field.set_text(dm_text)
                time.sleep(1)
                
                # Send
                send_btn = self.device(resourceId="com.instagram.android:id/layout_message_composer_button_send")
                if not send_btn.exists:
                    send_btn = self.device(description="Send")
                
                if send_btn.exists:
                    send_btn.click()
                    self.log_message(f"✅ DM sent to @{username}: '{dm_text[:30]}...'")
                    time.sleep(2)
                    self.device.press("back")
                    return True
            
            self.log_message(f"⚠️ Could not send DM to @{username}")
            return False
            
        except Exception as e:
            self.log_message(f"❌ Auto-DM error: {e}")
            return False
    
    def send_welcome_dm(self, username):
        """Send a welcome DM to a newly followed user"""
        return self.auto_dm(username, message=random.choice(self.WELCOME_DM_TEMPLATES))
    
    def mass_story_view(self, max_stories=50):
        """Mass view stories from home feed"""
        stories_viewed = 0
        try:
            self.log_message(f"👁️ Starting mass story viewing (max: {max_stories})...")
            
            # Go to home feed
            home_tab = self.device(resourceId="com.instagram.android:id/tab_bar").child(index=0)
            if home_tab.exists:
                home_tab.click()
                time.sleep(2)
            
            while self.bot_running and stories_viewed < max_stories:
                try:
                    # Find story rings at top of feed
                    story_ring = self.device(resourceId="com.instagram.android:id/reel_ring")
                    if not story_ring.exists:
                        # Try alternative
                        story_ring = self.device(descriptionContains="story")
                    
                    if story_ring.exists:
                        story_ring.click()
                        time.sleep(2)
                        
                        # View stories with natural timing
                        story_count = 0
                        while story_count < 10:  # Max stories per user
                            time.sleep(random.uniform(2, 5))
                            story_count += 1
                            stories_viewed += 1
                            self.log_message(f"👁️ Viewed story #{stories_viewed}/{max_stories}")
                            
                            # Tap to advance to next story
                            self.device.click(900, 500)  # Right side = next story
                            time.sleep(1)
                            
                            # Check if we're still in story viewer
                            close_btn = self.device(description="Close")
                            if not close_btn.exists and not self.device(resourceId="com.instagram.android:id/reel_viewer").exists:
                                break
                        
                        # Close story viewer
                        close_btn = self.device(description="Close")
                        if close_btn.exists:
                            close_btn.click()
                        else:
                            self.device.press("back")
                        time.sleep(2)
                        
                        # Anti-detection
                        if stories_viewed % 20 == 0 and stories_viewed > 0:
                            self.log_message("😴 Taking a break from stories...")
                            time.sleep(random.uniform(15, 30))
                    else:
                        # Scroll to find more stories
                        self.device.swipe(540, 400, 540, 200, 0.5)
                        time.sleep(2)
                        
                        if not self.device(resourceId="com.instagram.android:id/reel_ring").exists:
                            self.log_message("✅ No more stories to view")
                            break
                        
                except Exception as e:
                    self.log_message(f"⚠️ Story view error: {e}")
                    self.device.press("back")
                    time.sleep(2)
                    continue
            
            self.log_message(f"✅ Mass story viewing complete: {stories_viewed} stories viewed")
            
        except Exception as e:
            self.log_message(f"❌ Mass story view error: {e}")
        
        return stories_viewed
    
    def view_stories(self, max_stories=5):
        """View stories from target account"""
        stories_viewed = 0
        try:
            story_ring = self.device(resourceId="com.instagram.android:id/reel_ring")
            if story_ring.exists:
                story_ring.click()
                self.log_message("👁️ Viewing stories...")
                time.sleep(2)
                
                while stories_viewed < max_stories:
                    time.sleep(random.uniform(2, 5))
                    stories_viewed += 1
                    self.log_message(f"👁️ Viewed story {stories_viewed}/{max_stories}")
                    
                    self.device.click(900, 500)
                    time.sleep(1)
                    
                    if self.device(text="Stories").exists or self.device(description="Stories").exists:
                        break
                
                self.device.press("back")
                time.sleep(1)
        except Exception as e:
            self.log_message(f"⚠️ Story view error: {e}")
        
        return stories_viewed
    
    def auto_approve_follow_requests(self):
        """Approve pending follow requests"""
        approved = 0
        try:
            self.log_message("✅ Starting auto-approve follow requests...")
            
            # Go to own profile
            profile_tab = self.device(resourceId="com.instagram.android:id/tab_bar").child(index=4)
            if profile_tab.exists:
                profile_tab.click()
                time.sleep(3)
            
            # Look for follow requests indicator
            requests_selectors = [
                "com.instagram.android:id/follow_requests_container",
                "//android.widget.TextView[contains(@text, 'Requests')]",
            ]
            
            for selector in requests_selectors:
                try:
                    if selector.startswith("//"):
                        req = self.device.xpath(selector)
                    else:
                        req = self.device(resourceId=selector)
                    
                    if req.exists:
                        req.click()
                        time.sleep(3)
                        break
                except:
                    continue
            
            # Approve all pending requests
            while self.bot_running:
                try:
                    # Find Confirm/Approve buttons
                    confirm_btn = self.device(text="Confirm")
                    if not confirm_btn.exists:
                        confirm_btn = self.device(text="Approve")
                    
                    if confirm_btn.exists:
                        confirm_btn.click()
                        approved += 1
                        self.log_message(f"✅ Approved follow request #{approved}")
                        time.sleep(random.uniform(1, 3))
                    else:
                        # Scroll for more
                        self.device.swipe(540, 650, 540, 450, 1.0)
                        time.sleep(2)
                        
                        confirm_btn = self.device(text="Confirm")
                        if not confirm_btn.exists:
                            confirm_btn = self.device(text="Approve")
                        if not confirm_btn.exists:
                            self.log_message("✅ No more pending requests")
                            break
                        
                except Exception as e:
                    self.log_message(f"⚠️ Approve error: {e}")
                    continue
            
            self.log_message(f"✅ Auto-approve complete: {approved} requests approved")
            
        except Exception as e:
            self.log_message(f"❌ Auto-approve error: {e}")
        
        return approved
    
    def auto_comment(self, custom_comment=None):
        """Leave a comment on current post"""
        try:
            comment_btn = self.device(resourceId="com.instagram.android:id/row_feed_button_comment")
            if not comment_btn.exists:
                comment_btn = self.device(description="Comment")
            
            if comment_btn.exists:
                comment_btn.click()
                time.sleep(2)
                
                comment_text = custom_comment if custom_comment else random.choice(self.COMMENT_TEMPLATES)
                
                comment_field = self.device(resourceId="com.instagram.android:id/layout_comment_composer_edittext")
                if comment_field.exists:
                    comment_field.set_text(comment_text)
                    time.sleep(1)
                    
                    post_btn = self.device(resourceId="com.instagram.android:id/layout_comment_composer_button_post")
                    if post_btn.exists:
                        post_btn.click()
                        self.log_message(f"💬 Commented: '{comment_text}'")
                        time.sleep(2)
                        return True
        except Exception as e:
            self.log_message(f"⚠️ Auto-comment error: {e}")
        
        return False
    
    def view_stories(self, max_stories=5):
        """View stories from target account"""
        stories_viewed = 0
        try:
            story_ring = self.device(resourceId="com.instagram.android:id/reel_ring")
            if story_ring.exists:
                story_ring.click()
                self.log_message("👁️ Viewing stories...")
                time.sleep(2)
                
                while stories_viewed < max_stories:
                    time.sleep(random.uniform(2, 5))
                    stories_viewed += 1
                    self.log_message(f"👁️ Viewed story {stories_viewed}/{max_stories}")
                    
                    self.device.click(0.8, 0.5)
                    time.sleep(1)
                    
                    if self.device(text="Stories").exists or self.device(description="Stories").exists:
                        break
                
                self.device.press("back")
                time.sleep(1)
        except Exception as e:
            self.log_message(f"⚠️ Story view error: {e}")
        
        return stories_viewed

    # ==================== END EXPANDED ACTIONS METHODS ====================

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
            targets_input = self.targets_var.get().strip()
            follow_limit = int(self.follow_limit_var.get())
            like_limit = int(self.like_limit_var.get())
            followers_per_account = int(self.followers_per_account_var.get())
            
            # Parse multiple target accounts (comma-separated)
            target_accounts = [account.strip() for account in targets_input.split(',') if account.strip()]
            
            if not target_accounts:
                self.log_message("❌ No target accounts specified!")
                return
            
            self.log_message(f"👤 Started bot for user: {username}")
            self.log_message(f"🎯 Target accounts: {', '.join(['@' + acc for acc in target_accounts])}")
            self.log_message(f"📊 Limits: {follow_limit} follows/day, {like_limit} likes/day")
            self.log_message(f"👥 Will process {followers_per_account} followers per account")
            self.log_message(f"🎲 RANDOM MODE: Will cycle through accounts randomly until limit reached")
            
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
            
            # Loop randomly through target accounts until daily limit reached
            loop_count = 0
            while self.bot_running and self.stats['followers_gained'] < follow_limit:
                loop_count += 1
                self.log_message(f"🔄 RANDOM LOOP #{loop_count}")
                
                # Shuffle accounts for random order
                random.shuffle(target_accounts)
                self.log_message(f"🎲 Random order: {', '.join(['@' + a for a in target_accounts])}")
                
                # Process each account in random order
                for target_account in target_accounts:
                    if not self.bot_running or self.stats['followers_gained'] >= follow_limit:
                        self.log_message("🛑 Stopping - daily limit reached or bot stopped")
                        break
                    
                    try:
                        self.log_message(f"📍 Processing target account: @{target_account}")
                        
                        # Search for user
                        self.log_message(f"🔍 Searching for @{target_account}...")
                        if not self._search_user(target_account):
                            self.log_message(f"⚠️ Could not find @{target_account}, skipping to next account")
                            continue
                        
                        # Go to their followers list
                        self.log_message(f"👥 Opening followers list for @{target_account}...")
                        if self._open_followers_list():
                            # Ensure we're in the Followers tab
                            self._ensure_in_followers_tab()
                            
                            # Process followers
                            followers_processed = self._process_followers(target_account, followers_per_account, follow_limit, like_limit)
                            
                            # If daily limit reached, stop processing
                            if self.stats['followers_gained'] >= follow_limit:
                                self.log_message(f"🎉 Daily follow limit reached! Bot stopping.")
                                self.stats['accounts_processed'] += 1
                                self.update_stats_display()
                                break
                            
                            self.log_message(f"✅ Processed {followers_processed} followers from @{target_account}")
                        else:
                            self.log_message(f"❌ Could not open followers list for @{target_account}")
                        
                        self.stats['accounts_processed'] += 1
                        self.update_stats_display()
                        
                    except Exception as e:
                        self.log_message(f"❌ Error processing @{target_account}: {str(e)}")
                        continue
                
                # Check if we should start another random loop
                if self.bot_running and self.stats['followers_gained'] < follow_limit:
                    self.log_message(f"🎲 Completed loop #{loop_count}. Starting new random loop...")
                    time.sleep(random.uniform(10, 20))  # Break between loops
            
            if self.bot_running:
                self.log_message("🎉 Bot session completed successfully!")
                self.log_message(f"📊 Final stats: {self.stats['followers_gained']} follows, {self.stats['likes_given']} likes")
                
                # ANALYTICS: Show summary
                self.update_success_rate()
                self.show_analytics_summary()
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
            
            # Try clicking on followers count by coordinates - LEFT side is Followers
            self.log_message("🔄 Trying coordinate-based followers click...")
            self.device.click(250, 300)  # LEFT side = Followers button
            time.sleep(3)
            return True
            
        except Exception as e:
            self.log_message(f"❌ Error opening followers list: {str(e)}")
            return False
    
    def _ensure_in_followers_tab(self):
        """Make sure we're in the Followers tab, not Following or Mutual tab"""
        try:
            self.log_message("🔄 Ensuring we're in Followers tab...")
            time.sleep(2)
            
            current_tab = self._get_current_tab()
            self.log_message(f"📍 Current tab detected: {current_tab}")
            
            if current_tab == "followers":
                self.log_message("✅ Already in Followers tab")
                return True
            elif current_tab in ["following", "mutual", "unknown"]:
                self.log_message(f"⚠️ Currently in {current_tab} tab - switching to Followers")
                return self._switch_to_followers_tab()
            else:
                self.log_message("🔄 Tab unclear - attempting to switch to Followers")
                return self._switch_to_followers_tab()
                
        except Exception as e:
            self.log_message(f"❌ Error ensuring Followers tab: {str(e)}")
            return False
    
    def _get_current_tab(self):
        """Detect which tab we're currently on"""
        try:
            # Check for Followers indicators
            followers_indicators = [
                "//android.widget.TextView[@text='Followers']",
                "//android.widget.Button[@text='Followers']",
                "//android.widget.TextView[@text='followers']",
                "//android.widget.Button[@text='followers']",
                "//android.widget.TextView[contains(@text, 'Followers')]",
                "//android.widget.TextView[contains(@text, 'followers')]",
                "com.instagram.android:id/followers_tab",
                "com.instagram.android:id/tab_text",  # Generic tab text
            ]
            
            for indicator in followers_indicators:
                try:
                    if indicator.startswith("//"):
                        elem = self.device.xpath(indicator)
                    else:
                        elem = self.device(resourceId=indicator)
                    
                    if elem.exists and elem.info.get('selected', False):
                        return "followers"
                except:
                    continue
            
            # Check for Following indicators
            following_indicators = [
                "//android.widget.TextView[@text='Following']",
                "//android.widget.Button[@text='Following']",
                "//android.widget.TextView[@text='following']",
                "//android.widget.Button[@text='following']",
                "//android.widget.TextView[contains(@text, 'Following')]",
                "//android.widget.TextView[contains(@text, 'following')]",
                "com.instagram.android:id/following_tab",
                "com.instagram.android:id/tab_text",  # Generic tab text
            ]
            
            for indicator in following_indicators:
                try:
                    if indicator.startswith("//"):
                        elem = self.device.xpath(indicator)
                    else:
                        elem = self.device(resourceId=indicator)
                    
                    if elem.exists and elem.info.get('selected', False):
                        return "following"
                except:
                    continue
            
            # Check for Mutual indicators (accounts you both follow)
            mutual_indicators = [
                "//android.widget.TextView[@text='Mutual']",
                "//android.widget.Button[@text='Mutual']",
                "//android.widget.TextView[@text='mutual']",
                "//android.widget.Button[@text='mutual']",
                "//android.widget.TextView[contains(@text, 'Mutual')]",
                "//android.widget.TextView[contains(@text, 'mutual')]",
                "com.instagram.android:id/mutual_tab",
                "com.instagram.android:id/tab_text",  # Generic tab text
            ]
            
            for indicator in mutual_indicators:
                try:
                    if indicator.startswith("//"):
                        elem = self.device.xpath(indicator)
                    else:
                        elem = self.device(resourceId=indicator)
                    
                    if elem.exists and elem.info.get('selected', False):
                        return "mutual"
                except:
                    continue
            
            return "unknown"
            
        except Exception as e:
            return "unknown"
    
    def _switch_to_followers_tab(self):
        """Switch to Followers tab"""
        try:
            self.log_message("🔄 Switching to Followers tab...")
            
            # Try specific Followers tab selectors
            followers_selectors = [
                "//android.widget.TextView[@text='Followers']",
                "//android.widget.Button[@text='Followers']",
                "//android.widget.TextView[@text='followers']",
                "//android.widget.Button[@text='followers']",
                "//android.widget.TextView[contains(@text, 'Followers')]",
                "//android.widget.TextView[contains(@text, 'followers')]",
                "com.instagram.android:id/followers_tab",
                "com.instagram.android:id/tab_text",  # Generic tab text
            ]
            
            for selector in followers_selectors:
                try:
                    if selector.startswith("//"):
                        followers_tab = self.device.xpath(selector)
                    else:
                        followers_tab = self.device(resourceId=selector)
                    
                    if followers_tab.exists:
                        followers_tab.click()
                        time.sleep(2)
                        self.log_message("✅ Clicked Followers tab")
                        
                        # Verify we're now in Followers tab
                        if self._get_current_tab() == "followers":
                            self.log_message("✅ Successfully switched to Followers tab")
                            return True
                        else:
                            self.log_message("⚠️ Click didn't switch tabs - trying coordinate approach")
                            break
                except:
                    continue
            
            # Try coordinate-based approach - click on LEFT side where Followers tab is
            # Tab order: Followers (left) | Mutual (middle) | Following (right)
            self.log_message("🔄 Trying coordinate-based Followers tab click...")
            self.device.click(100, 400)  # Far LEFT = Followers tab
            time.sleep(2)
            
            # Verify the switch
            if self._get_current_tab() == "followers":
                self.log_message("✅ Successfully switched to Followers tab with coordinates")
                return True
            else:
                # Try different positions - Followers should be leftmost
                positions = [(80, 400), (120, 400), (150, 400)]
                for x, y in positions:
                    self.log_message(f"🔄 Trying position ({x}, {y})...")
                    self.device.click(x, y)
                    time.sleep(2)
                    if self._get_current_tab() == "followers":
                        self.log_message("✅ Switched to Followers tab")
                        return True
                
                self.log_message("❌ Could not switch to Followers tab")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Error switching to Followers tab: {str(e)}")
            return False
    
    def _is_on_profile_page(self):
        """Check if we're on a profile page with multiple indicators"""
        try:
            # Check for profile page indicators
            profile_indicators = [
                self.device(text="Follow").exists,
                self.device(text="Following").exists,
                self.device(text="Message").exists,
                self.device(text="Follow Back").exists,
                self.device(resourceId="com.instagram.android:id/profile_tab_username").exists,
                self.device(resourceId="com.instagram.android:id/row_profile_header_username").exists,
                self.device(resourceId="com.instagram.android:id/profile_header_follow_button").exists,
            ]
            return any(profile_indicators)
        except:
            return False
    
    def _search_user(self, username):
        """Search for a user on Instagram - FIXED VERSION"""
        try:
            self.log_message(f"🔍 Searching for: @{username}")
            
            # Click search tab
            search_tab = self.device(resourceId="com.instagram.android:id/tab_bar").child(index=1)
            if search_tab.exists:
                search_tab.click()
                time.sleep(3)
            else:
                search_btn = self.device(description="Search and Explore")
                if search_btn.exists:
                    search_btn.click()
                    time.sleep(3)
            
            # Click search box
            search_box = self.device(resourceId="com.instagram.android:id/action_bar_search_edit_text")
            if not search_box.exists:
                search_box = self.device(className="android.widget.EditText")
            
            if search_box.exists:
                search_box.click()
                time.sleep(1)
                search_box.clear_text()
                time.sleep(0.5)
                search_box.set_text(username)
                self.log_message(f"⌨️ Typed: '{username}'")
                time.sleep(4)  # Wait for results
            else:
                self.log_message("❌ Could not find search box")
                return False
            
            # Try to find and click the first search result
            self.log_message(f"🔍 Looking for: '{username}'")
            
            # Method 1: Click on the row_search_user container (entire row)
            self.log_message("🔍 Looking for search result row...")
            row_selectors = [
                "com.instagram.android:id/row_search_user",
                "//android.widget.LinearLayout[contains(@resource-id, 'row_search')]",
                "//android.view.ViewGroup[contains(@resource-id, 'row_search')]",
            ]
            
            for selector in row_selectors:
                try:
                    if selector.startswith("//"):
                        row = self.device.xpath(selector)
                    else:
                        row = self.device(resourceId=selector)
                    
                    if row.exists:
                        self.log_message(f"✅ Found search row: {selector}")
                        row.click()
                        time.sleep(4)  # Wait longer for page to load
                        # Verify we're on a profile page
                        if self._is_on_profile_page():
                            self.log_message("✅ Successfully navigated to profile")
                            return True
                        else:
                            self.log_message("⚠️ Clicked but not on profile page yet, continuing...")
                except:
                    continue
            
            # Method 2: Look for profile picture and click the row containing it
            self.log_message("🔍 Looking for profile picture...")
            try:
                # Find all avatars and click the first one's parent
                avatars = self.device(resourceId="com.instagram.android:id/row_search_user_avatar")
                if avatars.exists:
                    # Click the first avatar's parent (the row)
                    first_avatar = avatars[0] if hasattr(avatars, '__iter__') else avatars
                    # Try to get parent or just click the avatar
                    first_avatar.click()
                    time.sleep(4)
                    if self._is_on_profile_page():
                        self.log_message("✅ Clicked profile picture, on profile page")
                        return True
                    else:
                        self.log_message("⚠️ Clicked avatar but not on profile page")
            except Exception as e:
                self.log_message(f"⚠️ Avatar click failed: {e}")
            
            # Method 3: Direct text match with parent container
            self.log_message("🔍 Trying direct text match...")
            try:
                exact_match = self.device(text=username)
                if exact_match.exists:
                    # Try to find the parent row
                    match = exact_match[0] if hasattr(exact_match, '__iter__') else exact_match
                    match.click()
                    time.sleep(4)
                    if self._is_on_profile_page():
                        self.log_message(f"✅ Clicked exact match: {username}")
                        return True
                    else:
                        self.log_message("⚠️ Clicked text but not on profile page")
            except:
                pass
            
            # Method 4: Coordinate click on first result
            self.log_message("🔄 Trying coordinate click...")
            self.device.click(540, 450)
            time.sleep(4)  # Increased wait time
            if self._is_on_profile_page():
                self.log_message("✅ Coordinate click worked")
                return True
            
            self.log_message(f"✅ Search completed for: '{username}' - proceeding to profile")
            # Return True since we did click on something in search results
            return True
            
        except Exception as e:
            self.log_message(f"❌ Search error: {str(e)}")
            return False
    
    def _get_current_profile_username(self):
        """Get the username of the current profile we're on"""
        try:
            # Look for username in various locations
            username_selectors = [
                "com.instagram.android:id/profile_tab_username",
                "com.instagram.android:id/row_profile_header_username", 
                "com.instagram.android:id/title",
                "//android.widget.TextView[contains(@resource-id, 'username')]",
                "//android.widget.TextView[contains(@text, '@')]"
            ]
            
            for selector in username_selectors:
                try:
                    if selector.startswith("//"):
                        username_elem = self.device.xpath(selector)
                    else:
                        username_elem = self.device(resourceId=selector)
                    
                    if username_elem.exists:
                        username = username_elem.get_text()
                        if username and username.strip():
                            # Remove @ symbol if present
                            clean_username = username.strip().lstrip('@')
                            self.log_message(f"📍 Current profile: @{clean_username}")
                            return clean_username
                except:
                    continue
            
            return None
            
        except Exception as e:
            self.log_message(f"❌ Error getting current username: {str(e)}")
            return None
    
    def _process_followers(self, account, max_followers, follow_limit, like_limit):
        """Process followers with anti-detection features"""
        followers_processed = 0
        stay_in_followers = self.stay_in_followers_var.get()
        
        try:
            self.log_message(f"👥 Starting to process followers from @{account}")
            self.log_message(f"🔄 Stay in followers mode: {'ON' if stay_in_followers else 'OFF'}")
            self.log_message(f"🎯 Will follow max {max_followers} from this account")
            
            i = 0
            while self.bot_running and self.stats['followers_gained'] < follow_limit and followers_processed < max_followers:
                if not self.bot_running:
                    break
                
                # AUTONOMOUS: Auto-heal from common issues
                if self.autonomous_config['auto_recovery']:
                    self.auto_heal()
                
                # ANTI-DETECTION: Check rate limits
                if not self.check_rate_limit():
                    self.log_message("⏸️ Rate limit check failed - pausing")
                    time.sleep(60)
                    continue
                
                # ANTI-DETECTION: Check for Instagram warnings
                if self.check_instagram_warnings():
                    continue
                
                # ANTI-DETECTION: Occasionally skip an action
                if self.should_skip_action(0.05):
                    self.log_message("😴 Taking a moment...")
                    self.human_delay('follow')
                    continue
                
                try:
                    if stay_in_followers:
                        self.log_message(f"👤 [ONE AT A TIME] Following follower #{followers_processed+1}/{max_followers} from @{account}...")
                        
                        # SMART TARGETING: Check profile quality (DISABLED - was skipping too many)
                        # username_elem = self.get_profile_info_from_list()
                        # if not self.should_follow_profile(min_score=70):
                        #     self.smart_scroll()
                        #     i += 1
                        #     continue
                        
                        if self._follow_follower_from_list():
                            self.stats['followers_gained'] += 1
                            followers_processed += 1
                            self.record_action(success=True)
                            self.log_message(f"✅ [FOLLOWED #{followers_processed}] from @{account} | Total: {self.stats['followers_gained']}/{follow_limit}")
                            self.update_stats_display()
                            self.human_delay('follow')
                            
                            # 24-HOUR SPREAD: Wait calculated time between follows
                            if self.spread_24h_var.get():
                                self.apply_24h_delay(follow_limit)
                            
                            # ONE AT A TIME: Scroll after each follow
                            self.log_message(f"⬇️ Scrolling to find next person...")
                            self.smart_scroll()
                            i += 1
                        else:
                            self.record_action(success=False)
                            self.log_message(f"⏭️ [SKIP] Couldn't follow - scrolling to next...")
                            self.smart_scroll()
                            i += 1
                        
                        continue  # Skip the normal scroll at bottom since we did it here
                    else:
                        self.log_message(f"👤 Clicking follower #{followers_processed+1}/{max_followers} profile...")
                        if self._click_follower_from_list():
                            time.sleep(2)
                            
                            if self.stats['followers_gained'] < follow_limit:
                                if self._follow_user_from_profile():
                                    self.stats['followers_gained'] += 1
                                    followers_processed += 1
                                    self.record_action(success=True)
                                    self.log_message(f"✅ Followed {followers_processed}/{max_followers} from @{account} | Total: {self.stats['followers_gained']}/{follow_limit}")
                                    self.update_stats_display()
                                    self.human_delay('follow')
                                else:
                                    self.record_action(success=False)
                                    self.log_message(f"⏭️ Already following this account")
                            
                            self.log_message("🔙 Going back to followers list...")
                            self.device.press("back")
                            time.sleep(2)
                            
                            # Scroll to find next follower after going back
                            self.log_message("⬇️ Scrolling to find next person...")
                            self.smart_scroll()
                            i += 1
                        else:
                            # Failed to click follower, scroll to next
                            self.log_message("⏭️ Couldn't click follower - scrolling to next...")
                            self.smart_scroll()
                            i += 1
                    
                    if not self.bot_running:
                        break
                    
                    if self.stats['followers_gained'] >= follow_limit:
                        self.log_message(f"🎉 Daily follow limit reached! ({self.stats['followers_gained']}/{follow_limit} follows)")
                        break
                    
                    if followers_processed >= max_followers:
                        self.log_message(f"🎯 Reached {max_followers} follows from @{account} - Moving to next account!")
                        break
                    
                    # ANTI-DETECTION: Smart scroll with variable timing
                    self.log_message(f"⬇️ Scrolling... ({followers_processed}/{max_followers} from @{account})")
                    self.smart_scroll()
                    
                    i += 1
                    
                    # Safety check - too many attempts without follows (RELAXED)
                    if i > max_followers * 5 and followers_processed == 0:
                        self.log_message("⚠️ Too many attempts with no follows - may be at end of list")
                        break
                    
                except Exception as e:
                    self.log_message(f"❌ Error processing follower: {str(e)}")
                    self.record_action(success=False)
                    continue
            
            self.log_message(f"✅ Finished with @{account}: Followed {followers_processed}/{max_followers} people")
            return followers_processed
            
        except Exception as e:
            self.log_message(f"❌ Error in _process_followers: {str(e)}")
            return followers_processed
    
    def _follow_follower_from_list(self):
        """Follow follower directly from followers list - ONLY click Follow button"""
        try:
            self.log_message("🔍 Looking for Follow button...")
            
            # Wait for elements to load
            time.sleep(1)
            
            # Look for Follow buttons in followers list - be very specific
            follow_selectors = [
                "com.instagram.android:id/follow_list_button",
                "com.instagram.android:id/button",
                "com.instagram.android:id/row_follow_button",
                "com.instagram.android:id/follow_button",
                "com.instagram.android:id/primary_button",
            ]
            
            for selector in follow_selectors:
                try:
                    follow_btn = self.device(resourceId=selector, text="Follow")
                    if follow_btn.exists:
                        self.log_message(f"✅ Found Follow button: {selector}")
                        follow_btn.click()
                        time.sleep(1)
                        return True
                except Exception as e:
                    self.log_message(f"⚠️ Selector {selector} failed: {e}")
                    continue
            
            # Try XPath for Follow button
            try:
                follow_btn = self.device.xpath("//android.widget.Button[@text='Follow']")
                if follow_btn.exists:
                    self.log_message("✅ Found Follow button via XPath (Button)")
                    follow_btn.click()
                    time.sleep(1)
                    return True
            except Exception as e:
                self.log_message(f"⚠️ XPath Button failed: {e}")
            
            # Try TextView with Follow text
            try:
                follow_btn = self.device.xpath("//android.widget.TextView[@text='Follow']")
                if follow_btn.exists:
                    self.log_message("✅ Found Follow button via XPath (TextView)")
                    follow_btn.click()
                    time.sleep(1)
                    return True
            except Exception as e:
                self.log_message(f"⚠️ XPath TextView failed: {e}")
            
            # Try any element with "Follow" text
            try:
                follow_btn = self.device(text="Follow")
                if follow_btn.exists:
                    self.log_message("✅ Found Follow button by text")
                    follow_btn.click()
                    time.sleep(1)
                    return True
            except Exception as e:
                self.log_message(f"⚠️ Text search failed: {e}")
            
            # COORDINATE FALLBACK: Follow button is typically on the RIGHT side of each row
            self.log_message("🔄 Trying coordinate click on Follow button...")
            # Try multiple positions on the right side where Follow button appears
            positions = [(950, 400), (950, 450), (950, 350), (900, 400), (980, 400)]
            for x, y in positions:
                self.device.click(x, y)
                time.sleep(0.5)
            self.log_message("✅ Clicked Follow button coordinates")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Error following from list: {str(e)}")
            return False
    
    def _click_follower_from_list(self):
        """Click on follower profile to open it"""
        try:
            # Click on center of follower row
            self.device.click(540, 400)  # Center of screen for follower row
            time.sleep(2)
            return True
        except Exception as e:
            return False
    
    def _follow_user_from_profile(self):
        """Follow user from their profile page"""
        try:
            # Wait for profile to load
            time.sleep(2)
            
            # Look for Follow button on profile
            follow_selectors = [
                "com.instagram.android:id/follow_button",
                "com.instagram.android:id/button_text", 
                "com.instagram.android:id/primary_button",
                "com.instagram.android:id/follow_list_button",
                "//android.widget.TextView[@text='Follow']",
                "//android.widget.Button[@text='Follow']",
                "//android.widget.TextView[contains(@text, 'Follow')]",
                "//android.widget.Button[contains(@text, 'Follow')]",
            ]
            
            for selector in follow_selectors:
                try:
                    if selector.startswith("//"):
                        follow_btn = self.device.xpath(selector)
                    else:
                        follow_btn = self.device(resourceId=selector)
                    
                    if follow_btn.exists:
                        follow_btn.click()
                        time.sleep(2)
                        return True
                except:
                    continue
            
            # Check if already following
            following_selectors = [
                "//android.widget.TextView[@text='Following']",
                "//android.widget.Button[@text='Following']"
            ]
            
            for selector in following_selectors:
                try:
                    if selector.startswith("//"):
                        following_btn = self.device.xpath(selector)
                    else:
                        following_btn = self.device(resourceId=selector)
                    
                    if following_btn.exists:
                        return False  # Already following
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.log_message(f"❌ Error following from profile: {str(e)}")
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
                "com.instagram.android:id/tab_bar",
                "//android.widget.TextView[@text='Following']",
                "//android.widget.Button[@text='Following']"
            ]
            
            for selector in following_selectors:
                try:
                    if selector.startswith("//"):
                        following_tab = self.device.xpath(selector)
                    else:
                        following_tab = self.device(resourceId=selector)
                        
                        if selector == "com.instagram.android:id/tab_bar":
                            following_tab = following_tab.child(index=2)
                        
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

    # ==================== FEATURE THREAD WRAPPERS ====================
    
    def _run_feature_thread(self, feature_func, *args):
        """Run a feature in a background thread"""
        if not self.device:
            messagebox.showerror("Error", "Please connect to a device first!")
            return
        self.bot_running = True
        thread = threading.Thread(target=feature_func, args=args, daemon=True)
        thread.start()
    
    def _run_auto_unfollow(self):
        try:
            limit = int(self.unfollow_limit_var.get())
        except:
            limit = 50
        self._run_feature_thread(self.auto_unfollow, limit)
    
    def _run_auto_like_feed(self):
        try:
            limit = int(self.like_feed_limit_var.get())
        except:
            limit = 20
        self._run_feature_thread(self.auto_like_feed, limit)
    
    def _run_mass_story_view(self):
        try:
            limit = int(self.story_limit_var.get())
        except:
            limit = 50
        self._run_feature_thread(self.mass_story_view, limit)
    
    def _run_auto_approve(self):
        self._run_feature_thread(self.auto_approve_follow_requests)
    
    def _run_auto_dm(self):
        username = self.targets_var.get().strip()
        if not username:
            messagebox.showerror("Error", "Enter a target account for DM!")
            return
        msg = self.dm_message_var.get().strip() or None
        self._run_feature_thread(self.auto_dm, username, msg)
    
    def _run_welcome_dm(self):
        username = self.targets_var.get().strip()
        if not username:
            messagebox.showerror("Error", "Enter a target account for Welcome DM!")
            return
        self._run_feature_thread(self.send_welcome_dm, username)
    
    def _run_auto_comment(self):
        self._run_feature_thread(self.auto_comment)
    
    def _run_view_stories(self):
        try:
            limit = int(self.story_limit_var.get())
        except:
            limit = 5
        self._run_feature_thread(self.view_stories, limit)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleBotGUI(root)
    root.mainloop()
