import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import os
import json
import time
from datetime import datetime

class InstagramBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖️ Instagram Bot - Working Edition")
        self.root.geometry("900x700")
        self.root.configure(bg='#2c3e50')
        
        self.bot_process = None
        self.config_file = 'working_bot_config.json'
        self.log_file = 'working_bot_logs.txt'
        
        # Bot statistics
        self.stats = {
            'followers_gained': 0,
            'followers_lost': 0,
            'likes_given': 0,
            'sessions_completed': 0,
            'total_runtime': 0,
            'last_session': None
        }
        
        # Create UI
        self.create_widgets()
        self.load_settings()
        self.load_stats()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖️ Instagram Bot - Working Edition", 
                             font=('Helvetica', 18, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # Statistics Dashboard
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Statistics Dashboard")
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Followers Gained
        ttk.Label(stats_grid, text="👥 Followers Gained:", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.followers_gained_var = tk.StringVar(value="0")
        ttk.Label(stats_grid, textvariable=self.followers_gained_var, font=('Helvetica', 14, 'bold'), 
                 foreground='#27ae60').grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # Followers Lost
        ttk.Label(stats_grid, text="💔 Followers Lost:", font=('Helvetica', 12, 'bold')).grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.followers_lost_var = tk.StringVar(value="0")
        ttk.Label(stats_grid, textvariable=self.followers_lost_var, font=('Helvetica', 14, 'bold'), 
                 foreground='#e74c3c').grid(row=0, column=3, sticky='w', padx=5, pady=2)
        
        # Likes Given
        ttk.Label(stats_grid, text="❤️ Likes Given:", font=('Helvetica', 12, 'bold')).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.likes_given_var = tk.StringVar(value="0")
        ttk.Label(stats_grid, textvariable=self.likes_given_var, font=('Helvetica', 14, 'bold'), 
                 foreground='#e67e22').grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # Sessions Completed
        ttk.Label(stats_grid, text="✅ Sessions:", font=('Helvetica', 12, 'bold')).grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.sessions_var = tk.StringVar(value="0")
        ttk.Label(stats_grid, textvariable=self.sessions_var, font=('Helvetica', 14, 'bold'), 
                 foreground='#3498db').grid(row=1, column=3, sticky='w', padx=5, pady=2)
        
        # Runtime
        ttk.Label(stats_grid, text="⏱️ Runtime:", font=('Helvetica', 12, 'bold')).grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.runtime_var = tk.StringVar(value="0h 0m")
        ttk.Label(stats_grid, textvariable=self.runtime_var, font=('Helvetica', 14, 'bold'), 
                 foreground='#9b59b6').grid(row=2, column=1, sticky='w', padx=5, pady=2)
        
        # Reset Stats Button
        ttk.Button(stats_grid, text="🔄 Reset Stats", command=self.reset_stats).grid(row=2, column=2, columnspan=2, pady=10)
        
        # Settings Notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Account Settings Tab
        account_frame = ttk.Frame(notebook)
        notebook.add(account_frame, text="👤 Account")
        
        ttk.Label(account_frame, text="Instagram Username:").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.username_var = tk.StringVar(value='younghadene')
        ttk.Entry(account_frame, textvariable=self.username_var, width=30).grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        
        ttk.Label(account_frame, text="Password:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.password_var = tk.StringVar(value='inin')
        ttk.Entry(account_frame, textvariable=self.password_var, show="*", width=30).grid(row=1, column=1, sticky='ew', padx=10, pady=5)
        
        # Target Settings Tab
        target_frame = ttk.Frame(notebook)
        notebook.add(target_frame, text="🎯 Target Settings")
        
        ttk.Label(target_frame, text="Target Accounts (comma-separated):").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.target_accounts_var = tk.StringVar(value='champagnepapi, nav, pressa.armani, top5, whygnumba35, robinbanks_, killy, dahoudini, northsidebenji, smiley61st, yungtory, safe, jimmyprime, caspertng, kmoney, bvlly305, pengzgang, talluptwinz, burnabandz, 3mfrenchofficial')
        target_accounts_entry = ttk.Entry(target_frame, textvariable=self.target_accounts_var, width=50)
        target_accounts_entry.grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        
        ttk.Label(target_frame, text="Hashtags (comma-separated):").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.hashtags_var = tk.StringVar(value='tech, fashion, art')
        ttk.Entry(target_frame, textvariable=self.hashtags_var, width=50).grid(row=1, column=1, sticky='ew', padx=10, pady=5)
        
        # Activity Settings Tab
        activity_frame = ttk.Frame(notebook)
        notebook.add(activity_frame, text="⚡ Activity Settings")
        
        ttk.Label(activity_frame, text="Daily Follow Limit:").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.daily_follow_limit_var = tk.StringVar(value='200')
        ttk.Entry(activity_frame, textvariable=self.daily_follow_limit_var, width=20).grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        
        ttk.Label(activity_frame, text="Daily Like Limit:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.daily_like_limit_var = tk.StringVar(value='50')
        ttk.Entry(activity_frame, textvariable=self.daily_like_limit_var, width=20).grid(row=1, column=1, sticky='ew', padx=10, pady=5)
        
        ttk.Label(activity_frame, text="Follow Percentage (0-100):").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.follow_percentage_var = tk.StringVar(value='40')
        ttk.Entry(activity_frame, textvariable=self.follow_percentage_var, width=20).grid(row=2, column=1, sticky='ew', padx=10, pady=5)
        
        # Advanced Settings Tab
        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text="🔧 Advanced Settings")
        
        self.stealth_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_frame, text="🕵️ Stealth Mode", variable=self.stealth_mode_var).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        self.human_behavior_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_frame, text="👤 Human Behavior Simulation", variable=self.human_behavior_var).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        
        self.auto_block_detection_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_frame, text="🚫 Auto Block Detection", variable=self.auto_block_detection_var).grid(row=2, column=0, sticky='w', padx=10, pady=5)
        
        self.session_persistence_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_frame, text="💾 Session Persistence", variable=self.session_persistence_var).grid(row=3, column=0, sticky='w', padx=10, pady=5)
        
        # Control Panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="🚀 Start Bot", command=self.start_bot)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="🛑 Stop Bot", command=self.stop_bot, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="💾 Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="📂 Load Settings", command=self.load_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🗑️ Clear Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        
        # Status Bar
        self.status_var = tk.StringVar(value="Ready to start")
        status_label = ttk.Label(control_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_label.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        
        # Log Area
        log_frame = ttk.LabelFrame(main_frame, text="📝 Bot Logs")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def start_bot(self):
        try:
            self.status_var.set("Starting bot...")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # Save current settings
            self.save_settings()
            
            # Generate bot script
            bot_script = self.generate_bot_script()
            
            # Write bot script to file
            with open('temp_bot.py', 'w') as f:
                f.write(bot_script)
            
            # Start bot in separate thread
            self.bot_thread = threading.Thread(target=self.run_bot)
            self.bot_thread.daemon = True
            self.bot_thread.start()
            
            self.log_message("🚀 Bot started successfully!")
            self.status_var.set("Bot running...")
            
        except Exception as e:
            self.log_message(f"❌ Error starting bot: {str(e)}")
            self.status_var.set("Error starting bot")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def stop_bot(self):
        try:
            if self.bot_process:
                self.bot_process.terminate()
                self.bot_process = None
            
            self.status_var.set("Bot stopped")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.log_message("🛑 Bot stopped by user")
            
        except Exception as e:
            self.log_message(f"❌ Error stopping bot: {str(e)}")
    
    def run_bot(self):
        try:
            # Run the bot script
            self.bot_process = subprocess.Popen(['python3', 'temp_bot.py'], 
                                                stdout=subprocess.PIPE, 
                                                stderr=subprocess.STDOUT, 
                                                universal_newlines=True,
                                                cwd=os.getcwd())
            
            # Read output in real-time
            for line in self.bot_process.stdout:
                self.root.after(0, self.log_message, line.strip())
                self.root.after(0, self.update_stats_from_log, line.strip())
            
            # Process finished
            self.bot_process.wait()
            self.root.after(0, self.on_bot_finished)
            
        except Exception as e:
            self.root.after(0, self.log_message, f"❌ Bot error: {str(e)}")
            self.root.after(0, self.on_bot_finished)
    
    def on_bot_finished(self):
        self.status_var.set("Bot has stopped")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.stats['sessions_completed'] += 1
        self.update_stats_display()
        self.save_stats()
    
    def generate_bot_script(self):
        username = self.username_var.get()
        password = self.password_var.get()
        target_accounts = [acc.strip() for acc in self.target_accounts_var.get().split(',')]
        hashtags = [tag.strip() for tag in self.hashtags_var.get().split(',')]
        daily_follow_limit = int(self.daily_follow_limit_var.get())
        daily_like_limit = int(self.daily_like_limit_var.get())
        follow_percentage = int(self.follow_percentage_var.get()) / 100
        
        script = f'''import time
import random
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException

class RealInstagramBot:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.target_accounts = {target_accounts}
        self.hashtags = {hashtags}
        self.daily_follow_limit = {daily_follow_limit}
        self.daily_like_limit = {daily_like_limit}
        self.follow_percentage = {follow_percentage}
        self.followers_gained = 0
        self.likes_given = 0
        self.running = True
        self.driver = None
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{{timestamp}}] {{message}}")
        
    def human_delay(self, min_seconds=2, max_seconds=8):
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        
    def setup_driver(self):
        try:
            options = webdriver.ChromeOptions()
            
            # Android Studio emulator connection settings
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Connect to Android Studio emulator
            options.add_argument('--remote-debugging-port=9222')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            
            # Android Studio device settings
            mobile_emulation = {{
                "deviceMetrics": {{
                    "width": 411,
                    "height": 869,
                    "pixelRatio": 2.625
                }},
                "userAgent": "Mozilla/5.0 (Linux; Android 11; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36 Instagram 219.0.0.12.117 Android (30; 11; 2280x1080; google; Pixel 4; flame; qcom; en_US; 123123123)"
            }}
            options.add_experimental_option("mobileEmulation", mobile_emulation)
            
            # Try to connect to Android Studio emulator
            try:
                import subprocess
                result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
                if result.returncode == 0 and 'emulator-' in result.stdout:
                    self.log("✅ Android Studio emulator detected")
                    devices = result.stdout.strip().split('\\n')[1:]
                    for device in devices:
                        if device.strip():
                            self.log(f"📱 Found device: {{device.strip()}}")
                else:
                    self.log("⚠️ No Android Studio emulator found - please start emulator")
            except Exception as e:
                self.log(f"⚠️ ADB error: {{str(e)}}")
            
            # Initialize Chrome driver
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}})")
            
            # Set Android Studio mobile viewport
            self.driver.set_window_size(411, 869)
            
            self.log("✅ Android Studio emulator Chrome driver initialized")
            return True
        except Exception as e:
            self.log(f"❌ Error setting up Android Studio emulator driver: {{str(e)}}")
            return False
            
    def login(self):
        try:
            self.log("🔐 Logging into Instagram...")
            self.driver.get("https://www.instagram.com/accounts/login/")
            self.human_delay(3, 6)
            
            # Find and fill username
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.clear()
            username_input.send_keys(self.username)
            self.human_delay(1, 3)
            
            # Find and fill password
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.clear()
            password_input.send_keys(self.password)
            self.human_delay(1, 3)
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            self.human_delay(5, 8)
            
            # Check if login successful
            if "instagram.com" in self.driver.current_url and "login" not in self.driver.current_url:
                self.log("✅ Successfully logged in!")
                return True
            else:
                self.log("❌ Login failed - check credentials")
                return False
                
        except Exception as e:
            self.log(f"❌ Login error: {{str(e)}}")
            return False
            
    def follow_user(self, username):
        try:
            if self.followers_gained >= self.daily_follow_limit:
                return False
                
            self.log(f"👥 Attempting to follow @{{username}}...")
            self.driver.get(f"https://www.instagram.com/{{username}}/")
            self.human_delay(3, 6)
            
            # Look for follow button
            follow_button = None
            follow_selectors = [
                "//button[contains(text(), 'Follow')]",
                "//button[contains(@class, '_acan')]",
                "//div[contains(text(), 'Follow')]/parent::button"
            ]
            
            for selector in follow_selectors:
                try:
                    follow_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue
                    
            if follow_button:
                # Scroll to button
                self.driver.execute_script("arguments[0].scrollIntoView(true);", follow_button)
                self.human_delay(1, 2)
                
                # Click follow button
                follow_button.click()
                self.followers_gained += 1
                self.log(f"✅ Successfully followed @{{username}}!")
                self.human_delay(5, 10)
                return True
            else:
                self.log(f"⚠️ Could not find follow button for @{{username}}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error following @{{username}}: {{str(e)}}")
            return False
            
    def like_hashtag_posts(self, hashtag):
        try:
            if self.likes_given >= self.daily_like_limit:
                return False
                
            self.log(f"❤️ Liking posts with hashtag #{{hashtag}}...")
            self.driver.get(f"https://www.instagram.com/explore/tags/{{hashtag}}/")
            self.human_delay(3, 6)
            
            # Find first few posts
            posts = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
            posts_to_like = min(3, len(posts), self.daily_like_limit - self.likes_given)
            
            for i in range(posts_to_like):
                if not self.running or self.likes_given >= self.daily_like_limit:
                    break
                    
                try:
                    post = posts[i]
                    post.click()
                    self.human_delay(2, 4)
                    
                    # Like the post
                    like_button = None
                    like_selectors = [
                        "//span[contains(@class, 'coreSpriteHeartOpen')]",
                        "//button/span[contains(@class, 'coreSpriteHeartOpen')]",
                        "//svg[@aria-label='Like']"
                    ]
                    
                    for selector in like_selectors:
                        try:
                            like_button = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                            break
                        except:
                            continue
                            
                    if like_button:
                        like_button.click()
                        self.likes_given += 1
                        self.log(f"✅ Liked post #{{i+1}} with #{{hashtag}}")
                        self.human_delay(3, 6)
                    
                    # Close post
                    close_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Close')]")
                    close_button.click()
                    self.human_delay(2, 4)
                    
                except Exception as e:
                    self.log(f"⚠️ Error liking post #{{i+1}}: {{str(e)}}")
                    continue
                    
            return True
            
        except Exception as e:
            self.log(f"❌ Error liking hashtag posts: {{str(e)}}")
            return False
            
    def run_session(self):
        self.log("🚀 Starting real Instagram bot session...")
        self.log(f"📊 Daily limits: {{self.daily_follow_limit}} follows, {{self.daily_like_limit}} likes")
        
        if not self.setup_driver():
            return 0, 0
            
        if not self.login():
            return 0, 0
            
        try:
            # Follow target accounts
            for account in self.target_accounts:
                if not self.running:
                    break
                if random.random() < self.follow_percentage:
                    if self.follow_user(account):
                        self.human_delay(10, 20)
                        
            # Like hashtag posts
            for hashtag in self.hashtags:
                if not self.running:
                    break
                if self.like_hashtag_posts(hashtag):
                    self.human_delay(10, 20)
                    
        except Exception as e:
            self.log(f"❌ Session error: {{str(e)}}")
            
        finally:
            if self.driver:
                self.driver.quit()
                
        self.log(f"📊 Session complete: {{self.followers_gained}} follows, {{self.likes_given}} likes")
        return self.followers_gained, self.likes_given

# Run the bot
if __name__ == "__main__":
    bot = RealInstagramBot("{username}", "{password}")
    try:
        followers, likes = bot.run_session()
        print(f"🎉 Bot completed successfully!")
        print(f"📊 Final stats: {{followers}} follows, {{likes}} likes")
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user")
        bot.running = False
        if bot.driver:
            bot.driver.quit()
    except Exception as e:
        print(f"❌ Bot error: {{str(e)}}")
        if bot.driver:
            bot.driver.quit()
'''
        return script
    
    def update_stats_from_log(self, log_line):
        try:
            if "Successfully followed" in log_line:
                self.stats['followers_gained'] += 1
                self.update_stats_display()
            elif "Successfully liked" in log_line:
                self.stats['likes_given'] += 1
                self.update_stats_display()
        except:
            pass
    
    def update_stats_display(self):
        self.followers_gained_var.set(str(self.stats['followers_gained']))
        self.followers_lost_var.set(str(self.stats['followers_lost']))
        self.likes_given_var.set(str(self.stats['likes_given']))
        self.sessions_var.set(str(self.stats['sessions_completed']))
        
        # Update runtime
        if self.stats['last_session']:
            runtime = datetime.now() - self.stats['last_session']
            hours = int(runtime.total_seconds() // 3600)
            minutes = int((runtime.total_seconds() % 3600) // 60)
            self.runtime_var.set(f"{hours}h {minutes}m")
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
        # Also save to log file
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def save_settings(self):
        settings = {
            'username': self.username_var.get(),
            'password': self.password_var.get(),
            'target_accounts': self.target_accounts_var.get(),
            'hashtags': self.hashtags_var.get(),
            'daily_follow_limit': self.daily_follow_limit_var.get(),
            'daily_like_limit': self.daily_like_limit_var.get(),
            'follow_percentage': self.follow_percentage_var.get(),
            'stealth_mode': self.stealth_mode_var.get(),
            'human_behavior': self.human_behavior_var.get(),
            'auto_block_detection': self.auto_block_detection_var.get(),
            'session_persistence': self.session_persistence_var.get()
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        self.log_message("💾 Settings saved")
    
    def load_settings(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                
                self.username_var.set(settings.get('username', 'younghadene'))
                self.password_var.set(settings.get('password', 'inin'))
                self.target_accounts_var.set(settings.get('target_accounts', 'champagnepapi, nav, pressa.armani, top5'))
                self.hashtags_var.set(settings.get('hashtags', 'tech, fashion, art'))
                self.daily_follow_limit_var.set(settings.get('daily_follow_limit', '200'))
                self.daily_like_limit_var.set(settings.get('daily_like_limit', '50'))
                self.follow_percentage_var.set(settings.get('follow_percentage', '40'))
                self.stealth_mode_var.set(settings.get('stealth_mode', True))
                self.human_behavior_var.set(settings.get('human_behavior', True))
                self.auto_block_detection_var.set(settings.get('auto_block_detection', True))
                self.session_persistence_var.set(settings.get('session_persistence', True))
                
                self.log_message("📂 Settings loaded")
        except Exception as e:
            self.log_message(f"❌ Error loading settings: {str(e)}")
    
    def save_stats(self):
        with open('bot_stats.json', 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def load_stats(self):
        try:
            if os.path.exists('bot_stats.json'):
                with open('bot_stats.json', 'r') as f:
                    self.stats = json.load(f)
                self.update_stats_display()
        except:
            pass
    
    def reset_stats(self):
        self.stats = {
            'followers_gained': 0,
            'followers_lost': 0,
            'likes_given': 0,
            'sessions_completed': 0,
            'total_runtime': 0,
            'last_session': None
        }
        self.update_stats_display()
        self.save_stats()
        self.log_message("🔄 Statistics reset")
    
    def clear_logs(self):
        self.log_text.delete(1.0, tk.END)
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        self.log_message("🗑️ Logs cleared")

if __name__ == "__main__":
    root = tk.Tk()
    app = InstagramBotGUI(root)
    root.mainloop()
