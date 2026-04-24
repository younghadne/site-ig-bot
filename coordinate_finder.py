import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import re
import time
from datetime import datetime

class CoordinateFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("📍 Instagram Coordinate Finder")
        self.root.geometry("900x700")
        
        self.device_id = ""
        self.detected_coords = {}
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="📍 Instagram Coordinate Finder", 
                         font=('Helvetica', 18, 'bold'))
        title.pack(pady=(0, 15))
        
        # Instructions
        instructions = """
🔍 HOW TO FIND CORRECT COORDINATES:

1. Open Instagram on your emulator
2. Click "Capture Screen" to get view data
3. Click "Find Coordinates" to extract positions
4. Test coordinates by clicking "Test Tap"
5. Save working coordinates

💡 TIPS:
- Make sure Instagram is open and visible
- Try multiple positions for each element
- Save coordinates that actually work
- Different screens need different coordinates
        """
        
        instr_label = tk.Text(main_frame, height=8, wrap=tk.WORD, font=('Courier', 9))
        instr_label.pack(fill=tk.X, pady=(0, 10))
        instr_label.insert('1.0', instructions)
        instr_label.config(state=tk.DISABLED)
        
        # Device Frame
        device_frame = ttk.LabelFrame(main_frame, text="📱 Device")
        device_frame.pack(fill=tk.X, pady=(0, 10))
        
        device_grid = ttk.Frame(device_frame)
        device_grid.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(device_grid, text="Device ID:").grid(row=0, column=0, sticky='w')
        self.device_var = tk.StringVar(value='')
        ttk.Entry(device_grid, textvariable=self.device_var, width=30).grid(row=0, column=1, sticky='ew', padx=5)
        
        ttk.Button(device_grid, text="📱 List Devices", command=self.list_devices).grid(row=1, column=0, pady=5)
        ttk.Button(device_grid, text="📸 Capture Screen", command=self.capture_screen).grid(row=1, column=1, pady=5)
        
        # Coordinates Display
        coords_frame = ttk.LabelFrame(main_frame, text="📍 Found Coordinates")
        coords_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.coords_text = tk.Text(coords_frame, height=15, font=('Courier', 10))
        self.coords_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.coords_text.insert('1.0', "Click 'Capture Screen' to find Instagram button positions...")
        
        # Test Controls
        test_frame = ttk.LabelFrame(main_frame, text="🧪 Test Coordinates")
        test_frame.pack(fill=tk.X, pady=(0, 10))
        
        test_grid = ttk.Frame(test_frame)
        test_grid.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(test_grid, text="X:").grid(row=0, column=0)
        self.test_x = tk.StringVar(value='200')
        ttk.Entry(test_grid, textvariable=self.test_x, width=8).grid(row=0, column=1, padx=5)
        
        ttk.Label(test_grid, text="Y:").grid(row=0, column=2)
        self.test_y = tk.StringVar(value='200')
        ttk.Entry(test_grid, textvariable=self.test_y, width=8).grid(row=0, column=3, padx=5)
        
        ttk.Button(test_grid, text="👆 Test Tap", command=self.test_tap).grid(row=0, column=4, padx=10)
        ttk.Button(test_grid, text="💾 Save Coordinates", command=self.save_coordinates).grid(row=0, column=5, padx=10)
        
        # Log
        log_frame = ttk.LabelFrame(main_frame, text="📝 Log")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def list_devices(self):
        self.log("📱 Listing devices...")
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                devices = result.stdout.strip().split('\n')[1:]
                for device in devices:
                    if device.strip():
                        self.log(f"📱 {device.strip()}")
                        if not self.device_var.get():
                            self.device_var.set(device.strip().split()[0])
                            self.log(f"✅ Auto-selected: {device.strip().split()[0]}")
            else:
                self.log("❌ No devices found")
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
    
    def capture_screen(self):
        device_id = self.device_var.get()
        if not device_id:
            self.log("❌ No device selected")
            return
            
        self.log("📸 Capturing screen data...")
        
        try:
            # Get window hierarchy
            result = subprocess.run(['adb', '-s', device_id, 'shell', 'dumpsys', 'window', 'windows'], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                self.log("✅ Got window data")
                self.parse_window_data(result.stdout)
            else:
                self.log("❌ Failed to get window data")
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
    
    def parse_window_data(self, data):
        """Parse window data to find Instagram UI elements"""
        self.log("🔍 Parsing window data...")
        
        # Look for Instagram package
        if 'com.instagram.android' not in data:
            self.log("⚠️ Instagram not detected - make sure it's open")
            return
        
        # Extract bounds for UI elements
        # Look for patterns like bounds=[0,0][1080,1920]
        bounds_pattern = r'bounds=\[(\d+),(\d+)\]\[(\d+),(\d+)\]'
        bounds_matches = re.findall(bounds_pattern, data)
        
        # Get screen size
        screen_match = re.search(r'cur=(\d+)x(\d+)', data)
        if screen_match:
            screen_width = int(screen_match.group(1))
            screen_height = int(screen_match.group(2))
            self.log(f"📱 Screen size: {screen_width}x{screen_height}")
        else:
            screen_width = 1080
            screen_height = 1920
            self.log("📱 Using default screen size: 1080x1920")
        
        # Calculate relative coordinates based on common Instagram layouts
        # These are percentages of screen size
        coords = {
            "SEARCH_BAR": (int(screen_width * 0.5), int(screen_height * 0.08)),
            "SEARCH_ICON": (int(screen_width * 0.15), int(screen_height * 0.08)),
            "HOME_TAB": (int(screen_width * 0.1), int(screen_height * 0.9)),
            "SEARCH_TAB": (int(screen_width * 0.3), int(screen_height * 0.9)),
            "REELS_TAB": (int(screen_width * 0.5), int(screen_height * 0.9)),
            "SHOP_TAB": (int(screen_width * 0.7), int(screen_height * 0.9)),
            "PROFILE_TAB": (int(screen_width * 0.9), int(screen_height * 0.9)),
            "FIRST_RESULT": (int(screen_width * 0.5), int(screen_height * 0.25)),
            "SECOND_RESULT": (int(screen_width * 0.5), int(screen_height * 0.35)),
            "THIRD_RESULT": (int(screen_width * 0.5), int(screen_height * 0.45)),
            "FOLLOW_BUTTON": (int(screen_width * 0.85), int(screen_height * 0.18)),
            "LIKE_BUTTON_1": (int(screen_width * 0.5), int(screen_height * 0.55)),
            "LIKE_BUTTON_2": (int(screen_width * 0.5), int(screen_height * 0.75)),
            "BACK_BUTTON": (int(screen_width * 0.05), int(screen_height * 0.05)),
        }
        
        self.detected_coords = coords
        
        # Display coordinates
        display_text = f"📍 DETECTED COORDINATES (Screen: {screen_width}x{screen_height})\n\n"
        for name, (x, y) in coords.items():
            display_text += f"{name}: ({x}, {y})\n"
        
        display_text += "\n💡 Test these coordinates using the Test Controls above"
        display_text += "\n💡 Adjust X/Y values if needed for your screen"
        
        self.coords_text.delete('1.0', tk.END)
        self.coords_text.insert('1.0', display_text)
        
        self.log(f"✅ Found {len(coords)} coordinates")
        self.log("👆 Test each coordinate to verify it works")
        
    def test_tap(self):
        device_id = self.device_var.get()
        if not device_id:
            self.log("❌ No device selected")
            return
        
        try:
            x = int(self.test_x.get())
            y = int(self.test_y.get())
        except:
            self.log("❌ Invalid X/Y values")
            return
        
        self.log(f"👆 Testing tap at ({x}, {y})...")
        
        try:
            result = subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                self.log(f"✅ Tap successful at ({x}, {y})")
            else:
                self.log(f"❌ Tap failed: {result.stderr}")
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
    
    def save_coordinates(self):
        """Save coordinates to a file"""
        if not self.detected_coords:
            self.log("❌ No coordinates to save - capture screen first")
            return
        
        try:
            with open('instagram_coordinates.txt', 'w') as f:
                f.write("# Instagram UI Coordinates\n")
                f.write(f"# Generated: {datetime.now()}\n\n")
                for name, (x, y) in self.detected_coords.items():
                    f.write(f"{name} = ({x}, {y})\n")
            
            self.log("💾 Coordinates saved to instagram_coordinates.txt")
            self.log("✅ Use these in your bot script")
        except Exception as e:
            self.log(f"❌ Error saving: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CoordinateFinder(root)
    root.mainloop()
