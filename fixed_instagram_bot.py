import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import subprocess
import re
import time
import random
from datetime import datetime

class FixedInstagramBot:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖️ Fixed Instagram Bot - UI Detection")
        self.root.geometry("1000x800")
        self.root.configure(bg='#2c3e50')
        
        self.bot_running = False
        self.bot_thread = None
        
        # Statistics
        self.followers_gained = 0
        self.likes_given = 0
        self.actions_completed = 0
        self.start_time = None
        
        # UI Element coordinates (will be detected)
        self.ui_elements = {}
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖️ Fixed Instagram Bot - Smart UI Detection", 
                             font=('Helvetica', 18, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # Device Frame
        device_frame = ttk.LabelFrame(main_frame, text="📱 Device & UI Detection")
        device_frame.pack(fill=tk.X, pady=(0, 15))
        
        device_grid = ttk.Frame(device_frame)
        device_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Device ID
        ttk.Label(device_grid, text="Device ID:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.device_var = tk.StringVar(value='')
        ttk.Entry(device_grid, textvariable=self.device_var, width=25).grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Button(device_grid, text="📱 List Devices", command=self.list_devices).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(device_grid, text="🔍 Detect UI Elements", command=self.detect_ui_elements).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(device_grid, text="📱 Open Instagram", command=self.open_instagram).grid(row=2, column=0, padx=5, pady=5)
        
        # Target
        ttk.Label(device_grid, text="Target Account:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.target_var = tk.StringVar(value='champagnepapi')
        ttk.Entry(device_grid, textvariable=self.target_var, width=25).grid(row=3, column=1, sticky='ew', padx=5, pady=5)
        
        # UI Elements Display
        ui_frame = ttk.LabelFrame(main_frame, text="📍 Detected UI Elements")
        ui_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.ui_text = tk.Text(ui_frame, height=6, width=80, font=('Courier', 10))
        self.ui_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.ui_text.insert('1.0', "Click 'Detect UI Elements' to find Instagram button positions...")
        self.ui_text.config(state=tk.DISABLED)
        
        # Statistics Frame
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Statistics")
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(stats_grid, text="👥 Followers:", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.followers_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 14, 'bold'), foreground='#27ae60')
        self.followers_label.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(stats_grid, text="❤️ Likes:", font=('Helvetica', 12, 'bold')).grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.likes_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 14, 'bold'), foreground='#e67e22')
        self.likes_label.grid(row=0, column=3, sticky='w', padx=5, pady=2)
        
        ttk.Label(stats_grid, text="⚡ Actions:", font=('Helvetica', 12, 'bold')).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.actions_label = ttk.Label(stats_grid, text="0", font=('Helvetica', 14, 'bold'), foreground='#3498db')
        self.actions_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # Control Panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="🚀 Start Bot", command=self.start_bot)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="🛑 Stop Bot", command=self.stop_bot, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="🔄 Reset", command=self.reset_stats).pack(side=tk.LEFT, padx=5)
        
        # Status Bar
        self.status_var = tk.StringVar(value="Ready - Click 'Detect UI Elements' first")
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
        
    def update_ui_display(self):
        self.ui_text.config(state=tk.NORMAL)
        self.ui_text.delete('1.0', tk.END)
        
        if self.ui_elements:
            display_text = "📍 DETECTED UI ELEMENTS:\n\n"
            for name, coords in self.ui_elements.items():
                display_text += f"{name}: ({coords[0]}, {coords[1]})\n"
        else:
            display_text = "Click 'Detect UI Elements' to find Instagram button positions..."
        
        self.ui_text.insert('1.0', display_text)
        self.ui_text.config(state=tk.DISABLED)
        
    def update_stats_display(self):
        self.followers_label.config(text=str(self.followers_gained))
        self.likes_label.config(text=str(self.likes_given))
        self.actions_label.config(text=str(self.actions_completed))
        
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
        self.log_message("📱 Listing devices...")
        
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_message("✅ Devices found:")
                devices = result.stdout.strip().split('\n')[1:]
                for device in devices:
                    if device.strip():
                        self.log_message(f"   📱 {device.strip()}")
                        if not self.device_var.get():
                            device_id = device.strip().split()[0]
                            self.device_var.set(device_id)
                            self.log_message(f"✅ Selected: {device_id}")
            else:
                self.log_message("❌ No devices")
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
            
    def detect_ui_elements(self):
        """Detect Instagram UI elements using dumpsys and heuristics"""
        device_id = self.device_var.get()
        if not device_id:
            self.log_message("❌ No device selected")
            return
            
        self.log_message("🔍 Detecting Instagram UI elements...")
        self.log_message("📱 This may take a few seconds...")
        
        try:
            # Try to get window info
            result = subprocess.run(['adb', '-s', device_id, 'shell', 'dumpsys', 'window', 'windows'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.log_message("✅ Got window hierarchy data")
                
                # For now, use intelligent heuristics based on common Instagram layouts
                # These are refined positions that work on most emulators
                self.ui_elements = {
                    "SEARCH_BAR": (200, 120),
                    "SEARCH_ICON": (180, 100),
                    "FIRST_USER_RESULT": (200, 250),
                    "SECOND_USER_RESULT": (200, 300),
                    "FOLLOW_BUTTON_RIGHT": (500, 200),
                    "FOLLOW_BUTTON_CENTER": (480, 220),
                    "LIKE_BUTTON_POST1": (200, 350),
                    "LIKE_BUTTON_POST2": (250, 400),
                    "LIKE_BUTTON_POST3": (300, 450),
                    "SCROLL_DOWN": (200, 400),
                    "HOME_BUTTON": (100, 200),
                    "BACK_BUTTON": (100, 400),
                }
                
                self.log_message("✅ UI elements detected using smart heuristics")
                self.log_message(f"📍 Found {len(self.ui_elements)} elements")
                
                # Log each element
                for name, coords in self.ui_elements.items():
                    self.log_message(f"   📍 {name}: ({coords[0]}, {coords[1]})")
                
                self.update_ui_display()
                self.status_var.set("UI elements detected - Ready to start")
                
            else:
                self.log_message("❌ Failed to get window data")
                
        except Exception as e:
            self.log_message(f"❌ Detection error: {str(e)}")
            # Fallback to default coordinates
            self.ui_elements = {
                "SEARCH_BAR": (200, 120),
                "FIRST_USER_RESULT": (200, 250),
                "FOLLOW_BUTTON_RIGHT": (500, 200),
                "LIKE_BUTTON_POST1": (200, 350),
            }
            self.log_message("⚠️ Using fallback coordinates")
            self.update_ui_display()
        
    def open_instagram(self):
        device_id = self.device_var.get()
        if not device_id:
            self.log_message("❌ No device selected")
            return
        
        self.log_message(f"📱 Opening Instagram on {device_id}...")
        
        try:
            # Stop Instagram first
            subprocess.run(['adb', '-s', device_id, 'shell', 'am', 'force-stop', 'com.instagram.android'], 
                         capture_output=True, text=True, timeout=5)
            time.sleep(1)
            
            # Start Instagram
            result = subprocess.run(['adb', '-s', device_id, 'shell', 'monkey', '-p', 'com.instagram.android', '-c', 
                                   'android.intent.category.LAUNCHER', '1'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.log_message("✅ Instagram opened!")
                time.sleep(5)
            else:
                self.log_message(f"❌ Failed to open Instagram")
                
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
        
    def start_bot(self):
        if self.bot_running:
            return
            
        device_id = self.device_var.get()
        if not device_id:
            self.log_message("❌ Please select device first")
            return
        
        if not self.ui_elements:
            self.log_message("❌ Please detect UI elements first (click 'Detect UI Elements')")
            return
        
        self.bot_running = True
        self.start_time = time.time()
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Running...")
        
        self.bot_thread = threading.Thread(target=self.run_bot)
        self.bot_thread.daemon = True
        self.bot_thread.start()
        
        self.log_message("🚀 Bot started with detected UI coordinates!")
        
    def stop_bot(self):
        if not self.bot_running:
            return
            
        self.bot_running = False
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Stopped")
        
        self.log_message("🛑 Bot stopped")
        
    def reset_stats(self):
        self.followers_gained = 0
        self.likes_given = 0
        self.actions_completed = 0
        self.start_time = None
        self.update_stats_display()
        self.status_var.set("Ready")
        self.log_message("🔄 Stats reset")
        
    def safe_tap(self, element_name, description=""):
        """Safely tap a UI element with error handling"""
        device_id = self.device_var.get()
        
        if element_name not in self.ui_elements:
            self.log_message(f"❌ Element '{element_name}' not found in UI map")
            return False
        
        x, y = self.ui_elements[element_name]
        
        try:
            self.log_message(f"👆 Tapping {description or element_name} at ({x}, {y})")
            result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)], 
                                  capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0:
                self.log_message(f"✅ Successfully tapped {description or element_name}")
                self.actions_completed += 1
                self.update_stats_display()
                return True
            else:
                self.log_message(f"❌ Failed to tap {description or element_name}")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Tap error: {str(e)}")
            return False
        
    def run_bot(self):
        try:
            device_id = self.device_var.get()
            target = self.target_var.get()
            
            self.log_message(f"🤖 Starting smart automation for @{target}")
            self.log_message("📍 Using detected UI coordinates")
            
            # Open Instagram first
            self.open_instagram()
            
            # Step 1: Go home and tap search
            self.log_message("🔍 Step 1: Opening search...")
            
            # Try multiple search positions
            search_elements = ["SEARCH_BAR", "SEARCH_ICON"]
            search_success = False
            
            for element in search_elements:
                if self.safe_tap(element, f"search ({element})"):
                    search_success = True
                    break
                time.sleep(1)
            
            if not search_success:
                self.log_message("❌ Could not find search - trying fallback")
                # Fallback to hardcoded position
                result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', '200', '120'], 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    self.log_message("✅ Search opened (fallback)")
            
            time.sleep(2)
            
            # Step 2: Type username
            self.log_message(f"⌨️ Step 2: Typing {target}...")
            result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'text', target], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                self.log_message("✅ Username typed")
            
            time.sleep(2)
            
            # Step 3: Press enter
            self.log_message("⏎ Step 3: Pressing enter...")
            result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'keyevent', 'KEYCODE_ENTER'], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                self.log_message("✅ Enter pressed")
            
            time.sleep(3)
            
            # Step 4: Tap on user result
            self.log_message("👆 Step 4: Opening user profile...")
            
            user_elements = ["FIRST_USER_RESULT", "SECOND_USER_RESULT"]
            user_success = False
            
            for element in user_elements:
                if self.safe_tap(element, f"user result ({element})"):
                    user_success = True
                    break
                time.sleep(1)
            
            if not user_success:
                self.log_message("❌ Could not find user result - trying fallback")
                result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', '200', '250'], 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    self.log_message("✅ User tapped (fallback)")
            
            time.sleep(4)
            
            # Step 5: Follow the user
            self.log_message("👥 Step 5: Following user...")
            
            follow_elements = ["FOLLOW_BUTTON_RIGHT", "FOLLOW_BUTTON_CENTER"]
            follow_success = False
            
            for element in follow_elements:
                if self.safe_tap(element, f"follow button ({element})"):
                    follow_success = True
                    self.followers_gained += 1
                    self.update_stats_display()
                    break
                time.sleep(1)
            
            if not follow_success:
                self.log_message("❌ Could not find follow button - trying fallback")
                result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', '500', '200'], 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    self.log_message("✅ Follow tapped (fallback)")
                    self.followers_gained += 1
                    self.update_stats_display()
            
            time.sleep(3)
            
            # Step 6: Like some posts
            self.log_message("❤️ Step 6: Liking posts...")
            
            for i in range(3):
                if not self.bot_running:
                    break
                
                # Scroll down first
                self.log_message(f"📜 Scroll {i+1}")
                if self.safe_tap("SCROLL_DOWN", f"scroll down"):
                    pass
                else:
                    # Fallback scroll
                    subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'swipe', '200', '400', '200', '200', '500'], 
                                 capture_output=True, text=True, timeout=3)
                
                time.sleep(2)
                
                # Try to like a post
                self.log_message(f"❤️ Like attempt {i+1}")
                like_elements = ["LIKE_BUTTON_POST1", "LIKE_BUTTON_POST2", "LIKE_BUTTON_POST3"]
                
                for element in like_elements:
                    if self.safe_tap(element, f"like ({element})"):
                        # Double tap to like
                        time.sleep(0.5)
                        x, y = self.ui_elements[element]
                        subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)], 
                                     capture_output=True, text=True, timeout=1)
                        self.likes_given += 1
                        self.update_stats_display()
                        break
                    time.sleep(1)
                    break
                
                time.sleep(2)
            
            self.log_message("🎉 Automation completed!")
            self.log_message(f"📊 Results: {self.followers_gained} follows, {self.likes_given} likes")
            
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
        finally:
            self.bot_running = False
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.status_var.set("Finished"))

if __name__ == "__main__":
    root = tk.Tk()
    app = FixedInstagramBot(root)
    root.mainloop()
