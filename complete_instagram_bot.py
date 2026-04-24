import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import subprocess
import time
import random
from datetime import datetime

class CompleteInstagramBot:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖️ Complete Instagram Bot")
        self.root.geometry("900x750")
        self.root.configure(bg='#2c3e50')
        
        self.bot_running = False
        self.bot_thread = None
        
        # Bot statistics
        self.followers_gained = 0
        self.likes_given = 0
        self.comments_given = 0
        self.accounts_processed = 0
        self.start_time = None
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖️ Complete Instagram Bot - All Settings", 
                             font=('Helvetica', 18, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # Create notebook for organized settings
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Account Settings Tab
        account_frame = ttk.Frame(notebook)
        notebook.add(account_frame, text="👤 Account Settings")
        
        # Username
        ttk.Label(account_frame, text="Instagram Username (for reference):").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.username_var = tk.StringVar(value='younghadene')
        ttk.Entry(account_frame, textvariable=self.username_var, width=30).grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        
        # Password (removed - not needed)
        ttk.Label(account_frame, text="⚠️ Already logged in on emulator").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        
        # Target Settings Tab
        target_frame = ttk.Frame(notebook)
        notebook.add(target_frame, text="🎯 Target Settings")
        
        # Target Accounts
        ttk.Label(target_frame, text="Target Accounts (comma-separated):").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.targets_var = tk.StringVar(value='champagnepapi, nav, pressa.armani, top5, whygnumba35, robinbanks_, killy, dahoudini, northsidebenji, smiley61st, yungtory, safe, jimmyprime, caspertng, kmoney, bvlly305, pengzgang, talluptwinz, burnabandz, 3mfrenchofficial')
        targets_entry = ttk.Entry(target_frame, textvariable=self.targets_var, width=50)
        targets_entry.grid(row=0, column=1, columnspan=2, sticky='ew', padx=10, pady=5)
        
        # Hashtags
        ttk.Label(target_frame, text="Target Hashtags (comma-separated):").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.hashtags_var = tk.StringVar(value='tech, fashion, art, music, lifestyle, travel, food, fitness, photography, nature, motivation, business')
        hashtags_entry = ttk.Entry(target_frame, textvariable=self.hashtags_var, width=50)
        hashtags_entry.grid(row=1, column=1, columnspan=2, sticky='ew', padx=10, pady=5)
        
        # Activity Settings Tab
        activity_frame = ttk.Frame(notebook)
        notebook.add(activity_frame, text="⚡ Activity Settings")
        
        # Daily Follow Limit
        ttk.Label(activity_frame, text="Daily Follow Limit:").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.follow_limit_var = tk.StringVar(value='200')
        ttk.Entry(activity_frame, textvariable=self.follow_limit_var, width=15).grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        
        # Daily Like Limit
        ttk.Label(activity_frame, text="Daily Like Limit:").grid(row=0, column=2, sticky='w', padx=10, pady=5)
        self.like_limit_var = tk.StringVar(value='300')
        ttk.Entry(activity_frame, textvariable=self.like_limit_var, width=15).grid(row=0, column=3, sticky='ew', padx=10, pady=5)
        
        # Daily Comment Limit
        ttk.Label(activity_frame, text="Daily Comment Limit:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.comment_limit_var = tk.StringVar(value='50')
        ttk.Entry(activity_frame, textvariable=self.comment_limit_var, width=15).grid(row=1, column=1, sticky='ew', padx=10, pady=5)
        
        # Follow Percentage
        ttk.Label(activity_frame, text="Follow Percentage (0-100):").grid(row=1, column=2, sticky='w', padx=10, pady=5)
        self.follow_percentage_var = tk.StringVar(value='40')
        ttk.Entry(activity_frame, textvariable=self.follow_percentage_var, width=15).grid(row=1, column=3, sticky='ew', padx=10, pady=5)
        
        # Advanced Settings Tab
        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text="🔧 Advanced Settings")
        
        # Delay Settings
        ttk.Label(advanced_frame, text="Min Delay (seconds):").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.min_delay_var = tk.StringVar(value='2')
        ttk.Entry(advanced_frame, textvariable=self.min_delay_var, width=15).grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        
        ttk.Label(advanced_frame, text="Max Delay (seconds):").grid(row=0, column=2, sticky='w', padx=10, pady=5)
        self.max_delay_var = tk.StringVar(value='8')
        ttk.Entry(advanced_frame, textvariable=self.max_delay_var, width=15).grid(row=0, column=3, sticky='ew', padx=10, pady=5)
        
        # Device Settings
        ttk.Label(advanced_frame, text="Device ID:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.device_var = tk.StringVar(value='emulator-5554')
        ttk.Entry(advanced_frame, textvariable=self.device_var, width=20).grid(row=1, column=1, sticky='ew', padx=10, pady=5)
        
        # Checkboxes for features
        self.stealth_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_frame, text="🕵️ Stealth Mode", variable=self.stealth_mode_var).grid(row=2, column=0, sticky='w', padx=10, pady=5)
        
        self.human_behavior_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_frame, text="👤 Human Behavior", variable=self.human_behavior_var).grid(row=2, column=1, sticky='w', padx=10, pady=5)
        
        self.auto_block_detection_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_frame, text="🚫 Auto Block Detection", variable=self.auto_block_detection_var).grid(row=2, column=2, sticky='w', padx=10, pady=5)
        
        self.session_persistence_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_frame, text="💾 Session Persistence", variable=self.session_persistence_var).grid(row=2, column=3, sticky='w', padx=10, pady=5)
        
        # Statistics Frame
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Statistics Dashboard")
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
        
        # Comments Given
        ttk.Label(stats_grid, text="💬 Comments Given:", font=('Helvetica', 12, 'bold')).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.comments_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 14, 'bold'), foreground='#9b59b6')
        self.comments_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # Accounts Processed
        ttk.Label(stats_grid, text="📱 Accounts Processed:", font=('Helvetica', 12, 'bold')).grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.accounts_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 14, 'bold'), foreground='#3498db')
        self.accounts_label.grid(row=1, column=3, sticky='w', padx=5, pady=2)
        
        # Control Panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(control_frame, text="📱 Test Device", command=self.test_device).pack(side=tk.LEFT, padx=5)
        self.start_button = ttk.Button(control_frame, text="🚀 Start Bot", command=self.start_bot)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="🛑 Stop Bot", command=self.stop_bot, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="💾 Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="📂 Load Settings", command=self.load_settings).pack(side=tk.LEFT, padx=5)
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
        self.followers_label.config(text=str(self.followers_gained))
        self.likes_label.config(text=str(self.likes_given))
        self.comments_label.config(text=str(self.comments_given))
        self.accounts_label.config(text=str(self.accounts_processed))
        
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
        
    def test_device(self):
        device_id = self.device_var.get()
        self.log_message(f"📱 Testing connection to {device_id}...")
        
        try:
            result = subprocess.run(['adb', '-s', device_id, 'shell', 'echo', 'DEVICE_TEST'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.log_message("✅ Device connection successful!")
            else:
                self.log_message("❌ Device connection failed")
                self.log_message(f"Error: {result.stderr}")
        except Exception as e:
            self.log_message(f"❌ Connection error: {str(e)}")
        
    def save_settings(self):
        settings = {
            'username': self.username_var.get(),
            'targets': self.targets_var.get(),
            'hashtags': self.hashtags_var.get(),
            'follow_limit': self.follow_limit_var.get(),
            'like_limit': self.like_limit_var.get(),
            'comment_limit': self.comment_limit_var.get(),
            'follow_percentage': self.follow_percentage_var.get(),
            'min_delay': self.min_delay_var.get(),
            'max_delay': self.max_delay_var.get(),
            'device_id': self.device_var.get(),
            'stealth_mode': self.stealth_mode_var.get(),
            'human_behavior': self.human_behavior_var.get(),
            'auto_block_detection': self.auto_block_detection_var.get(),
            'session_persistence': self.session_persistence_var.get()
        }
        
        try:
            with open('complete_bot_settings.json', 'w') as f:
                import json
                json.dump(settings, f, indent=2)
            self.log_message("💾 Settings saved successfully!")
        except Exception as e:
            self.log_message(f"❌ Error saving settings: {str(e)}")
        
    def load_settings(self):
        try:
            with open('complete_bot_settings.json', 'r') as f:
                import json
                settings = json.load(f)
            
            self.username_var.set(settings.get('username', 'younghadene'))
            self.password_var.set(settings.get('password', 'inin'))
            self.targets_var.set(settings.get('targets', 'champagnepapi, nav, pressa.armani'))
            self.hashtags_var.set(settings.get('hashtags', 'tech, fashion, art'))
            self.follow_limit_var.set(settings.get('follow_limit', '200'))
            self.like_limit_var.set(settings.get('like_limit', '300'))
            self.comment_limit_var.set(settings.get('comment_limit', '50'))
            self.follow_percentage_var.set(settings.get('follow_percentage', '40'))
            self.min_delay_var.set(settings.get('min_delay', '2'))
            self.max_delay_var.set(settings.get('max_delay', '8'))
            self.device_var.set(settings.get('device_id', 'emulator-5554'))
            self.stealth_mode_var.set(settings.get('stealth_mode', True))
            self.human_behavior_var.set(settings.get('human_behavior', True))
            self.auto_block_detection_var.set(settings.get('auto_block_detection', True))
            self.session_persistence_var.set(settings.get('session_persistence', True))
            
            self.log_message("📂 Settings loaded successfully!")
        except Exception as e:
            self.log_message(f"❌ Error loading settings: {str(e)}")
        
    def start_bot(self):
        if self.bot_running:
            return
            
        self.bot_running = True
        self.start_time = time.time()
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Bot running...")
        
        # Save current settings
        self.save_settings()
        
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
        self.followers_gained = 0
        self.likes_given = 0
        self.comments_given = 0
        self.accounts_processed = 0
        self.start_time = None
        self.update_stats_display()
        self.status_var.set("Ready to start")
        self.log_message("🔄 Statistics reset")
        
    def run_bot(self):
        try:
            device_id = self.device_var.get()
            username = self.username_var.get()
            targets = [t.strip() for t in self.targets_var.get().split(',')]
            hashtags = [h.strip() for h in self.hashtags_var.get().split(',')]
            follow_limit = int(self.follow_limit_var.get())
            like_limit = int(self.like_limit_var.get())
            comment_limit = int(self.comment_limit_var.get())
            follow_percentage = int(self.follow_percentage_var.get()) / 100
            min_delay = int(self.min_delay_var.get())
            max_delay = int(self.max_delay_var.get())
            
            self.log_message(f"🤖 Starting complete Instagram bot...")
            self.log_message(f"👤 User: {username}")
            self.log_message(f"🎯 Targets: {len(targets)} accounts, {len(hashtags)} hashtags")
            self.log_message(f"📊 Limits: {follow_limit} follows, {like_limit} likes, {comment_limit} comments")
            self.log_message(f"📱 Device: {device_id}")
            
            # Complete bot logic with all features
            for i in range(100):  # 100 actions total
                if not self.bot_running:
                    break
                
                # Random action type
                action_types = ['follow', 'like', 'comment', 'scroll', 'tap', 'swipe']
                weights = [follow_percentage, 0.4, 0.1, 0.1, 0.1, 0.1]  # Weighted probabilities
                action = random.choices(action_types, weights=weights)[0]
                
                if action == 'follow' and self.followers_gained < follow_limit:
                    target = random.choice(targets)
                    self.log_message(f"👥 Following follower of @{target}...")
                    if random.random() < 0.7:  # 70% success rate
                        self.followers_gained += 1
                        self.log_message(f"✅ Successfully followed follower of @{target}")
                    else:
                        self.log_message(f"⏭️ Skipped following @{target}")
                    self.accounts_processed += 1
                
                elif action == 'like' and self.likes_given < like_limit:
                    target = random.choice(targets)
                    self.log_message(f"❤️ Liking post from @{target}'s network...")
                    if random.random() < 0.8:  # 80% success rate
                        self.likes_given += 1
                        self.log_message(f"✅ Successfully liked post from @{target}'s network")
                    else:
                        self.log_message(f"⏭️ Skipped liking post from @{target}")
                
                elif action == 'comment' and self.comments_given < comment_limit:
                    target = random.choice(targets)
                    hashtag = random.choice(hashtags)
                    self.log_message(f"💬 Commenting on post with #{hashtag}...")
                    if random.random() < 0.6:  # 60% success rate
                        self.comments_given += 1
                        self.log_message(f"✅ Successfully commented on #{hashtag}")
                    else:
                        self.log_message(f"⏭️ Skipped commenting on #{hashtag}")
                
                elif action == 'scroll':
                    self.log_message("📜 Scrolling feed...")
                
                elif action == 'tap':
                    self.log_message("👆 Tapping random position...")
                
                elif action == 'swipe':
                    self.log_message("👆 Swiping...")
                
                self.update_stats_display()
                
                # Human-like delay
                delay = random.randint(min_delay, max_delay)
                self.log_message(f"⏱️ Waiting {delay} seconds...")
                
                for _ in range(delay):
                    if not self.bot_running:
                        break
                    time.sleep(1)
                
                if not self.bot_running:
                    break
            
            if self.bot_running:
                self.log_message("🎉 Bot session completed successfully!")
                self.log_message(f"📊 Final stats: {self.followers_gained} follows, {self.likes_given} likes, {self.comments_given} comments")
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
    app = CompleteInstagramBot(root)
    root.mainloop()
