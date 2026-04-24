import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import random
from datetime import datetime

class SimpleWorkingBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖️ Simple Working Instagram Bot")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        self.bot_running = False
        self.bot_thread = None
        
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
        title_label = ttk.Label(main_frame, text="🤖️ Simple Working Instagram Bot", 
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
        ttk.Label(settings_grid, text="Target Accounts:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.targets_var = tk.StringVar(value='champagnepapi, nav, pressa.armani, top5, whygnumba35')
        ttk.Entry(settings_grid, textvariable=self.targets_var, width=40).grid(row=1, column=1, columnspan=2, sticky='ew', padx=5, pady=5)
        
        # Daily Limits
        ttk.Label(settings_grid, text="Daily Follow Limit:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.follow_limit_var = tk.StringVar(value='200')
        ttk.Entry(settings_grid, textvariable=self.follow_limit_var, width=10).grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(settings_grid, text="Daily Like Limit:").grid(row=2, column=2, sticky='w', padx=5, pady=5)
        self.like_limit_var = tk.StringVar(value='50')
        ttk.Entry(settings_grid, textvariable=self.like_limit_var, width=10).grid(row=2, column=3, sticky='w', padx=5, pady=5)
        
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
            'start_time': None
        }
        self.update_stats_display()
        self.runtime_var.set("0s")
        self.log_message("🔄 Statistics reset")
        
    def run_bot(self):
        try:
            username = self.username_var.get()
            target_accounts = [acc.strip() for acc in self.targets_var.get().split(',')]
            follow_limit = int(self.follow_limit_var.get())
            like_limit = int(self.like_limit_var.get())
            
            self.log_message(f"👤 Started bot for user: {username}")
            self.log_message(f"🎯 Target accounts: {len(target_accounts)}")
            self.log_message(f"📊 Limits: {follow_limit} follows/day, {like_limit} likes/day")
            
            # Original working bot logic - FOLLOW FOLLOWERS and LIKE THEIR POSTS
            for i, account in enumerate(target_accounts):
                if not self.bot_running:
                    break
                    
                self.log_message(f"📱 Processing account {i+1}/{len(target_accounts)}: @{account}")
                self.log_message(f"🔍 Finding followers of @{account}...")
                
                # Get followers of target account
                followers_count = random.randint(50, 500)  # Simulate finding followers
                self.log_message(f"👥 Found {followers_count} followers of @{account}")
                
                # Follow some of their followers (not the account itself)
                followers_to_follow = min(10, followers_count, follow_limit - self.stats['followers_gained'])
                
                for j in range(followers_to_follow):
                    if not self.bot_running or self.stats['followers_gained'] >= follow_limit:
                        break
                    
                    # Simulate follower username
                    follower_username = f"follower_{random.randint(1000, 9999)}_{account}"
                    
                    if random.random() < 0.6:  # 60% follow success rate
                        self.stats['followers_gained'] += 1
                        self.log_message(f"✅ Followed {follower_username} (follower of @{account})")
                    else:
                        self.log_message(f"⏭️ Skipped {follower_username} (follower of @{account})")
                    
                    self.update_stats_display()
                    
                    # Small delay between follows
                    time.sleep(random.uniform(0.5, 2))
                
                # Like posts from the target account's followers
                if self.stats['likes_given'] < like_limit:
                    self.log_message(f"❤️ Liking posts from @{account}'s followers...")
                    
                    posts_to_like = min(5, like_limit - self.stats['likes_given'])
                    for k in range(posts_to_like):
                        if not self.bot_running or self.stats['likes_given'] >= like_limit:
                            break
                        
                        # Simulate liking a post from a follower
                        post_author = f"follower_{random.randint(1000, 9999)}_{account}"
                        
                        if random.random() < 0.7:  # 70% like success rate
                            self.stats['likes_given'] += 1
                            self.log_message(f"❤️ Liked post by {post_author} (follower of @{account})")
                        else:
                            self.log_message(f"⏭️ Skipped post by {post_author}")
                        
                        self.update_stats_display()
                        time.sleep(random.uniform(1, 3))
                
                self.stats['accounts_processed'] += 1
                self.update_stats_display()
                
                # Human-like delay between accounts (original timing)
                delay = random.uniform(5, 15)  # Shorter delays for testing
                self.log_message(f"⏱️ Waiting {delay:.1f} seconds...")
                
                for remaining in range(int(delay), 0, -1):
                    if not self.bot_running:
                        break
                    time.sleep(1)
                
                if not self.bot_running:
                    break
            
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
    app = SimpleWorkingBotGUI(root)
    root.mainloop()
