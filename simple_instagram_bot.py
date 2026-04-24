import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import time
import random
import subprocess
import uiautomator2 as u2

class InstagramBot:
    """Core Instagram automation using uiautomator2"""
    
    def __init__(self):
        self.device = None
        self.device_id = None
        self.is_running = False
        self.stats = {
            'follows': 0,
            'accounts_processed': 0,
            'start_time': None
        }
    
    def connect_device(self, device_id):
        """Connect to Android device via uiautomator2"""
        try:
            # Check if device is available
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
            if device_id not in result.stdout:
                return False, f"Device {device_id} not found"
            
            # Connect to device
            self.device = u2.connect(device_id)
            self.device_id = device_id
            
            # Test connection
            device_info = self.device.info
            return True, f"Connected to {device_info.get('brand', 'Unknown')} {device_info.get('model', 'Device')}"
            
        except Exception as e:
            return False, str(e)
    
    def open_instagram(self):
        """Open Instagram app"""
        try:
            self.device.app_start("com.instagram.android")
            time.sleep(5)
            return True
        except Exception as e:
            return False
    
    def search_user(self, username):
        """Search for a user on Instagram"""
        try:
            # Click search tab
            search_tab = self.device(resourceId="com.instagram.android:id/tab_bar").child(index=1)
            if search_tab.exists:
                search_tab.click()
                time.sleep(2)
            
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
                time.sleep(3)
            
            # Try to find and click the user
            selectors = [
                ("resourceId", "com.instagram.android:id/row_search_user"),
                ("resourceId", "com.instagram.android:id/row_search_user_username"),
                ("description", f"{username}"),
            ]
            
            for selector_type, selector_value in selectors:
                try:
                    if selector_type == "resourceId":
                        elem = self.device(resourceId=selector_value, text=username)
                    elif selector_type == "description":
                        elem = self.device(description=selector_value)
                    
                    if elem.exists:
                        elem.click()
                        time.sleep(3)
                        return True
                except:
                    continue
            
            # Fallback: coordinate click
            self.device.click(540, 450)
            time.sleep(3)
            return True
            
        except Exception as e:
            return False
    
    def open_followers_list(self):
        """Open followers list of current profile"""
        try:
            followers_selectors = [
                "com.instagram.android:id/row_profile_header_followers_container",
                "com.instagram.android:id/followers_container",
                "//android.widget.TextView[@text='followers']"
            ]
            
            for selector in followers_selectors:
                try:
                    if selector.startswith("//"):
                        btn = self.device.xpath(selector)
                    else:
                        btn = self.device(resourceId=selector)
                    
                    if btn.exists:
                        btn.click()
                        time.sleep(3)
                        return True
                except:
                    continue
            
            # Fallback coordinate
            self.device.click(250, 300)
            time.sleep(3)
            return True
            
        except:
            return False
    
    def follow_from_list(self):
        """Follow user directly from followers list"""
        try:
            time.sleep(1)
            
            # Try multiple selectors
            selectors = [
                "com.instagram.android:id/follow_list_button",
                "com.instagram.android:id/button",
                "com.instagram.android:id/row_follow_button",
                "com.instagram.android:id/follow_button",
            ]
            
            for selector in selectors:
                try:
                    btn = self.device(resourceId=selector, text="Follow")
                    if btn.exists:
                        btn.click()
                        time.sleep(1)
                        self.stats['follows'] += 1
                        return True
                except:
                    continue
            
            # Try XPath
            try:
                btn = self.device.xpath("//android.widget.Button[@text='Follow']")
                if btn.exists:
                    btn.click()
                    time.sleep(1)
                    self.stats['follows'] += 1
                    return True
            except:
                pass
            
            # Fallback: coordinate click on right side
            self.device.click(950, 400)
            time.sleep(0.5)
            return True
            
        except:
            return False
    
    def scroll_list(self):
        """Scroll down in followers list"""
        try:
            self.device.swipe(540, 650, 540, 450, 1.0)
            time.sleep(2)
            return True
        except:
            return False
    
    def process_followers(self, target_account, max_followers, log_callback=None):
        """Process followers from target account"""
        followers_processed = 0
        
        try:
            # Search for target
            if log_callback:
                log_callback(f"🔍 Searching for @{target_account}...")
            
            if not self.search_user(target_account):
                if log_callback:
                    log_callback(f"❌ Could not find @{target_account}")
                return 0
            
            if log_callback:
                log_callback(f"✅ Found @{target_account}")
            
            # Open followers list
            if log_callback:
                log_callback(f"👥 Opening followers list...")
            
            if not self.open_followers_list():
                if log_callback:
                    log_callback(f"❌ Could not open followers list")
                return 0
            
            if log_callback:
                log_callback(f"✅ Opened followers list")
            
            # Process followers
            while self.is_running and followers_processed < max_followers:
                if log_callback:
                    log_callback(f"👤 Following follower #{followers_processed + 1}...")
                
                if self.follow_from_list():
                    followers_processed += 1
                    if log_callback:
                        log_callback(f"✅ Followed! Total: {self.stats['follows']}")
                else:
                    if log_callback:
                        log_callback(f"⏭️ Could not follow, scrolling...")
                
                # Scroll to next
                self.scroll_list()
                
                # Small delay between actions
                time.sleep(random.uniform(2, 4))
            
            self.stats['accounts_processed'] += 1
            return followers_processed
            
        except Exception as e:
            if log_callback:
                log_callback(f"❌ Error: {str(e)}")
            return followers_processed
    
    def start(self):
        self.is_running = True
        self.stats['start_time'] = time.time()
    
    def stop(self):
        self.is_running = False


class SimpleBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Bot - Simple")
        self.bot = InstagramBot()
        
        # Variables
        self.device_id_var = tk.StringVar(value="emulator-5554")
        self.target_account_var = tk.StringVar()
        self.max_followers_var = tk.StringVar(value="10")
        self.status_var = tk.StringVar(value="Ready")
        self.follows_var = tk.StringVar(value="0")
        self.accounts_var = tk.StringVar(value="0")
        
        self.bot_thread = None
        
        # Create notebook (tab control)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Connection tab
        conn_frame = ttk.Frame(notebook, padding="10")
        notebook.add(conn_frame, text="Connection")
        self.create_connection_tab(conn_frame)
        
        # Bot tab
        bot_frame = ttk.Frame(notebook, padding="10")
        notebook.add(bot_frame, text="Bot Control")
        self.create_bot_tab(bot_frame)
        
        # Log tab
        log_frame = ttk.Frame(notebook, padding="10")
        notebook.add(log_frame, text="Logs")
        self.create_log_tab(log_frame)
    
    def create_connection_tab(self, frame):
        """Create device connection tab"""
        ttk.Label(frame, text="Device ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.device_id_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(frame, text="Connect", command=self.connect_device).grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Label(frame, text="Status:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, textvariable=self.status_var).grid(row=2, column=1, sticky=tk.W, pady=5)
    
    def create_bot_tab(self, frame):
        """Create bot control tab"""
        ttk.Label(frame, text="Target Account:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.target_account_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Max Followers:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.max_followers_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="▶ Start", command=self.start_bot).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="⏹ Stop", command=self.stop_bot).pack(side=tk.LEFT, padx=5)
        
        # Stats
        stats_frame = ttk.LabelFrame(frame, text="Stats", padding="10")
        stats_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        ttk.Label(stats_frame, text="Follows:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(stats_frame, textvariable=self.follows_var).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(stats_frame, text="Accounts:").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(stats_frame, textvariable=self.accounts_var).grid(row=1, column=1, sticky=tk.W, padx=5)
    
    def create_log_tab(self, frame):
        """Create log display tab"""
        self.log_text = scrolledtext.ScrolledText(frame, width=60, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(frame, text="Clear", command=self.clear_logs).pack(pady=5)
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_logs(self):
        """Clear log display"""
        self.log_text.delete(1.0, tk.END)
    
    def connect_device(self):
        """Connect to Android device"""
        device_id = self.device_id_var.get()
        self.log_message(f"🔌 Connecting to {device_id}...")
        
        success, message = self.bot.connect_device(device_id)
        
        if success:
            self.status_var.set("Connected")
            self.log_message(f"✅ {message}")
        else:
            self.status_var.set("Failed")
            self.log_message(f"❌ {message}")
    
    def start_bot(self):
        """Start bot automation"""
        if not self.bot.device:
            messagebox.showerror("Error", "Please connect to device first!")
            return
        
        target = self.target_account_var.get().strip()
        if not target:
            messagebox.showerror("Error", "Please enter a target account!")
            return
        
        try:
            max_followers = int(self.max_followers_var.get())
        except:
            max_followers = 10
        
        self.bot.start()
        self.log_message("🚀 Bot started!")
        
        # Run bot in separate thread
        self.bot_thread = threading.Thread(
            target=self.run_bot,
            args=(target, max_followers),
            daemon=True
        )
        self.bot_thread.start()
    
    def run_bot(self, target_account, max_followers):
        """Main bot execution"""
        # Open Instagram
        self.log_message("📱 Opening Instagram...")
        if not self.bot.open_instagram():
            self.log_message("❌ Failed to open Instagram")
            return
        
        self.log_message("✅ Instagram opened")
        
        # Process followers
        count = self.bot.process_followers(
            target_account, 
            max_followers,
            log_callback=self.log_message
        )
        
        self.log_message(f"🎉 Completed! Followed {count} users")
        self.update_stats()
        self.bot.stop()
    
    def stop_bot(self):
        """Stop bot automation"""
        self.bot.stop()
        self.log_message("🛑 Bot stopped")
    
    def update_stats(self):
        """Update stats display"""
        self.follows_var.set(str(self.bot.stats['follows']))
        self.accounts_var.set(str(self.bot.stats['accounts_processed']))


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x500")
    app = SimpleBotGUI(root)
    root.mainloop()
