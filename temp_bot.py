import time
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
        self.target_accounts = ['champagnepapi', 'nav', 'pressa.armani', 'top5', 'whygnumba35', 'robinbanks_', 'killy', 'dahoudini', 'northsidebenji', 'smiley61st', 'yungtory', 'safe', 'jimmyprime', 'caspertng', 'kmoney', 'bvlly305', 'pengzgang', 'talluptwinz', 'burnabandz', '3mfrenchofficial']
        self.hashtags = ['tech', 'fashion', 'art']
        self.daily_follow_limit = 200
        self.daily_like_limit = 50
        self.follow_percentage = 0.4
        self.followers_gained = 0
        self.likes_given = 0
        self.running = True
        self.driver = None
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
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
            mobile_emulation = {
                "deviceMetrics": {
                    "width": 411,
                    "height": 869,
                    "pixelRatio": 2.625
                },
                "userAgent": "Mozilla/5.0 (Linux; Android 11; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36 Instagram 219.0.0.12.117 Android (30; 11; 2280x1080; google; Pixel 4; flame; qcom; en_US; 123123123)"
            }
            options.add_experimental_option("mobileEmulation", mobile_emulation)
            
            # Try to connect to Android Studio emulator
            try:
                import subprocess
                result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
                if result.returncode == 0 and 'emulator-' in result.stdout:
                    self.log("✅ Android Studio emulator detected")
                    devices = result.stdout.strip().split('\n')[1:]
                    for device in devices:
                        if device.strip():
                            self.log(f"📱 Found device: {device.strip()}")
                else:
                    self.log("⚠️ No Android Studio emulator found - please start emulator")
            except Exception as e:
                self.log(f"⚠️ ADB error: {str(e)}")
            
            # Initialize Chrome driver
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set Android Studio mobile viewport
            self.driver.set_window_size(411, 869)
            
            self.log("✅ Android Studio emulator Chrome driver initialized")
            return True
        except Exception as e:
            self.log(f"❌ Error setting up Android Studio emulator driver: {str(e)}")
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
            self.log(f"❌ Login error: {str(e)}")
            return False
            
    def follow_user(self, username):
        try:
            if self.followers_gained >= self.daily_follow_limit:
                return False
                
            self.log(f"👥 Attempting to follow @{username}...")
            self.driver.get(f"https://www.instagram.com/{username}/")
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
                self.log(f"✅ Successfully followed @{username}!")
                self.human_delay(5, 10)
                return True
            else:
                self.log(f"⚠️ Could not find follow button for @{username}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error following @{username}: {str(e)}")
            return False
            
    def like_hashtag_posts(self, hashtag):
        try:
            if self.likes_given >= self.daily_like_limit:
                return False
                
            self.log(f"❤️ Liking posts with hashtag #{hashtag}...")
            self.driver.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
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
                        self.log(f"✅ Liked post #{i+1} with #{hashtag}")
                        self.human_delay(3, 6)
                    
                    # Close post
                    close_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Close')]")
                    close_button.click()
                    self.human_delay(2, 4)
                    
                except Exception as e:
                    self.log(f"⚠️ Error liking post #{i+1}: {str(e)}")
                    continue
                    
            return True
            
        except Exception as e:
            self.log(f"❌ Error liking hashtag posts: {str(e)}")
            return False
            
    def run_session(self):
        self.log("🚀 Starting real Instagram bot session...")
        self.log(f"📊 Daily limits: {self.daily_follow_limit} follows, {self.daily_like_limit} likes")
        
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
            self.log(f"❌ Session error: {str(e)}")
            
        finally:
            if self.driver:
                self.driver.quit()
                
        self.log(f"📊 Session complete: {self.followers_gained} follows, {self.likes_given} likes")
        return self.followers_gained, self.likes_given

# Run the bot
if __name__ == "__main__":
    bot = RealInstagramBot("younghadene", "inin")
    try:
        followers, likes = bot.run_session()
        print(f"🎉 Bot completed successfully!")
        print(f"📊 Final stats: {followers} follows, {likes} likes")
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user")
        bot.running = False
        if bot.driver:
            bot.driver.quit()
    except Exception as e:
        print(f"❌ Bot error: {str(e)}")
        if bot.driver:
            bot.driver.quit()
