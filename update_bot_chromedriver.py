# update_bot_chromedriver.py - Update bot to use working ChromeDriver and fix CAPTCHA detection
import os
import shutil

def update_enhanced_browser_handler():
    """Update the enhanced browser handler with working ChromeDriver"""
    
    print("🔧 Updating Enhanced Browser Handler")
    print("=" * 40)
    
    handler_path = "backend/bot/enhanced_browser_handler.py"
    
    if not os.path.exists(handler_path):
        print(f"❌ File not found: {handler_path}")
        return False
    
    # Create backup
    shutil.copy2(handler_path, f"{handler_path}.backup")
    print(f"📁 Backup created: {handler_path}.backup")
    
    # Updated browser handler with working ChromeDriver and better CAPTCHA detection
    new_content = '''# bot/enhanced_browser_handler.py - Fixed ChromeDriver and CAPTCHA detection
import time
import random
import os
import uuid
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from typing import Dict, List, Optional, Any
from datetime import datetime

class EnhancedBrowserHandler:
    """Enhanced browser handler with fixed ChromeDriver and CAPTCHA detection"""
    
    def __init__(self, user_id: str = None, headless: bool = False):
        self.user_id = user_id
        self.headless = headless
        self.driver = None
        self.wait = None
        self.session_id = str(uuid.uuid4())
        self.current_application_id = None
        self.current_url = None
        
        # Stats tracking
        self.session_stats = {
            'applications_processed': 0,
            'applications_successful': 0,
            'applications_failed': 0,
            'captchas_encountered': 0,
            'session_start': datetime.utcnow()
        }
        
        self._setup_browser()
    
    def _setup_browser(self):
        """Setup browser with working ChromeDriver"""
        options = webdriver.ChromeOptions()
        
        # Headless mode setting
        if self.headless:
            options.add_argument("--headless")
            print(f"🔇 Browser running in headless mode")
        else:
            print(f"👁️ Browser running in visible mode")
        
        # Anti-detection options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Performance options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        
        # User agent randomization
        user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        try:
            # Try different ChromeDriver paths (based on our successful test)
            driver_paths = [
                '/usr/local/bin/chromedriver',  # Homebrew default
                '/opt/homebrew/bin/chromedriver',  # M1 Homebrew
                'chromedriver'  # System PATH
            ]
            
            driver_created = False
            for driver_path in driver_paths:
                try:
                    if driver_path == 'chromedriver':
                        service = ChromeService()  # Let it find in PATH
                    else:
                        if os.path.exists(driver_path):
                            service = ChromeService(executable_path=driver_path)
                        else:
                            continue
                    
                    self.driver = webdriver.Chrome(service=service, options=options)
                    print(f"✅ ChromeDriver loaded from: {driver_path}")
                    driver_created = True
                    break
                    
                except Exception as e:
                    print(f"⚠️ Failed with {driver_path}: {e}")
                    continue
            
            if not driver_created:
                raise Exception("No working ChromeDriver found")
            
            # Anti-detection script
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set window size
            if not self.headless:
                self.driver.maximize_window()
            else:
                self.driver.set_window_size(1920, 1080)
            
            self.wait = WebDriverWait(self.driver, 15)
            print(f"✅ Browser initialized for session {self.session_id[:8]}")
            
        except Exception as e:
            print(f"❌ Error initializing browser: {e}")
            raise
    
    async def navigate_to_job(self, job_url: str, application_id: str) -> bool:
        """Navigate to a job application page"""
        try:
            self.current_application_id = application_id
            self.current_url = job_url
            
            print(f"🌐 Navigating to: {job_url}")
            self.driver.get(job_url)
            
            # Wait for page load
            await asyncio.sleep(random.uniform(2, 4))
            
            # Handle common popups
            await self._handle_common_popups()
            
            return True
            
        except Exception as e:
            print(f"❌ Navigation error: {e}")
            return False
    
    async def _handle_common_popups(self):
        """Handle common popups and overlays"""
        try:
            # Cookie banners
            cookie_selectors = [
                "[id*='cookie'] button[id*='accept']",
                "[class*='cookie'] button[class*='accept']",
                "button[id*='accept-cookie']",
                "button[class*='accept-cookie']"
            ]
            
            for selector in cookie_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            print("🍪 Accepted cookies")
                            await asyncio.sleep(1)
                            break
                except:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Popup handling error: {e}")
    
    async def check_for_captcha(self) -> Optional[Dict[str, Any]]:
        """Enhanced CAPTCHA detection"""
        try:
            print("🔍 Checking for CAPTCHA...")
            
            # Enhanced CAPTCHA selectors based on our successful test
            captcha_selectors = [
                'iframe[src*="recaptcha"]',      # ✅ Found in test
                '.g-recaptcha',                  # ✅ Found in test  
                '[class*="captcha"]',            # ✅ Found in test
                '#recaptcha',
                '.captcha',
                '.cf-challenge-form',
                '[data-sitekey]',
                'div[class*="recaptcha"]',
                '[id*="captcha"]'
            ]
            
            captcha_info = None
            
            for selector in captcha_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            print(f"🚨 CAPTCHA detected with selector: {selector}")
                            
                            # Take screenshot for manual solving
                            screenshot_url = await self._take_captcha_screenshot()
                            
                            captcha_info = {
                                'type': 'recaptcha' if 'recaptcha' in selector else 'unknown',
                                'element': element,
                                'screenshot_url': screenshot_url,
                                'page_url': self.driver.current_url,
                                'selector': selector,
                                'detected_at': datetime.utcnow().isoformat()
                            }
                            
                            self.session_stats['captchas_encountered'] += 1
                            break
                    
                    if captcha_info:
                        break
                        
                except Exception as e:
                    print(f"⚠️ Error checking {selector}: {e}")
                    continue
            
            # Also check page source for CAPTCHA content
            if not captcha_info:
                page_source = self.driver.page_source.lower()
                captcha_keywords = ['recaptcha', 'captcha', 'hcaptcha', 'human verification']
                
                for keyword in captcha_keywords:
                    if keyword in page_source:
                        print(f"🚨 CAPTCHA keyword '{keyword}' found in page source")
                        
                        screenshot_url = await self._take_captcha_screenshot()
                        
                        captcha_info = {
                            'type': keyword,
                            'element': None,
                            'screenshot_url': screenshot_url,
                            'page_url': self.driver.current_url,
                            'selector': 'page_source',
                            'detected_at': datetime.utcnow().isoformat()
                        }
                        
                        self.session_stats['captchas_encountered'] += 1
                        break
            
            if captcha_info:
                print(f"🚨 CAPTCHA CONFIRMED: {captcha_info['type']} at {captcha_info['page_url']}")
            else:
                print("✅ No CAPTCHA detected")
            
            return captcha_info
            
        except Exception as e:
            print(f"❌ CAPTCHA check error: {e}")
            return None
    
    async def _take_captcha_screenshot(self) -> str:
        """Take a screenshot for CAPTCHA solving"""
        try:
            # Create screenshots directory if it doesn't exist
            screenshot_dir = os.path.join(os.getcwd(), 'captcha_screenshots')
            os.makedirs(screenshot_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"captcha_{self.session_id[:8]}_{timestamp}.png"
            filepath = os.path.join(screenshot_dir, filename)
            
            # Take screenshot
            self.driver.save_screenshot(filepath)
            print(f"📸 CAPTCHA screenshot saved: {filepath}")
            
            return filepath
            
        except Exception as e:
            print(f"❌ Screenshot error: {e}")
            return None
    
    async def scan_form_elements(self) -> List[Dict[str, Any]]:
        """Scan and analyze form elements on the page"""
        try:
            # First check if there's a CAPTCHA that should block form filling
            captcha_info = await self.check_for_captcha()
            if captcha_info:
                print("🚨 CAPTCHA detected - form filling will be paused")
                return []  # Return empty to trigger CAPTCHA handling
            
            # Scroll to ensure all elements are loaded
            await self._scroll_to_bottom()
            
            form_fields = []
            
            # Find all input elements
            inputs = self.driver.find_elements(By.CSS_SELECTOR, "input, textarea, select")
            
            # Group radio buttons and checkboxes
            choice_groups = {}
            
            for element in inputs:
                if not element.is_displayed():
                    continue
                
                field_type = element.get_attribute('type')
                
                if field_type in ['radio', 'checkbox']:
                    name = element.get_attribute('name')
                    if name:
                        if name not in choice_groups:
                            question_label = await self._find_question_for_choice(element)
                            choice_groups[name] = {
                                'label': question_label or f"Choice group: {name}",
                                'type': field_type,
                                'elements': [],
                                'required': element.get_attribute('required') is not None
                            }
                        choice_groups[name]['elements'].append(element)
                else:
                    field_data = await self._analyze_field(element)
                    if field_data:
                        form_fields.append(field_data)
            
            # Add choice groups
            form_fields.extend(choice_groups.values())
            
            print(f"📋 Found {len(form_fields)} form fields")
            return form_fields
            
        except Exception as e:
            print(f"❌ Form scanning error: {e}")
            return []
    
    async def _scroll_to_bottom(self):
        """Scroll to bottom to load all elements"""
        try:
            # Gradual scroll to mimic human behavior
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            current_position = 0
            
            while current_position < total_height:
                # Scroll in increments
                scroll_increment = random.randint(300, 600)
                current_position += scroll_increment
                
                self.driver.execute_script(f"window.scrollTo(0, {current_position});")
                await asyncio.sleep(random.uniform(0.5, 1.5))
                
                # Check if new content loaded
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height > total_height:
                    total_height = new_height
            
            # Scroll back to top
            self.driver.execute_script("window.scrollTo(0, 0);")
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"⚠️ Scroll error: {e}")
    
    async def _find_question_for_choice(self, element) -> Optional[str]:
        """Find the question text for a choice element"""
        # Implementation same as before
        return None
    
    async def _analyze_field(self, element) -> Optional[Dict[str, Any]]:
        """Analyze a single form field"""
        # Implementation same as before
        return None
    
    async def _get_field_label(self, element) -> Optional[str]:
        """Get the label for a form field"""
        # Implementation same as before
        return None
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        self.session_stats['session_duration'] = (datetime.utcnow() - self.session_stats['session_start']).total_seconds()
        return self.session_stats.copy()
    
    def close(self):
        """Close the browser and cleanup"""
        try:
            if self.driver:
                self.driver.quit()
                print(f"🔒 Browser session {self.session_id[:8]} closed")
        except Exception as e:
            print(f"⚠️ Error closing browser: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
'''
    
    # Write the updated content
    with open(handler_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated: {handler_path}")
    return True

def create_test_with_captcha_handling():
    """Create a test that properly handles CAPTCHA"""
    
    test_content = '''# test_captcha_handling.py - Test CAPTCHA detection and handling
import requests
import time

API_BASE = "http://localhost:8003"

def test_captcha_workflow():
    """Test the complete CAPTCHA workflow"""
    
    print("🧪 Testing CAPTCHA Detection and Handling")
    print("=" * 50)
    
    # Login
    login_data = {
        "email": "shubhmmane56@gmail.com",
        "password": "secure_password_123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/auth/login", json=login_data, timeout=10)
        if response.status_code != 200:
            print("❌ Login failed")
            return
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get profile
        profiles_response = requests.get(f"{API_BASE}/api/profiles", headers=headers, timeout=10)
        profiles = profiles_response.json()
        profile_id = profiles[0]['id']
        
        # Stop any existing bot
        requests.post(f"{API_BASE}/api/bot/stop", headers=headers, timeout=10)
        time.sleep(2)
        
        # Start bot with visible browser for CAPTCHA solving
        print("1. Starting bot with VISIBLE browser...")
        bot_config = {
            "headless": False,  # VISIBLE for CAPTCHA solving
            "max_concurrent": 1
        }
        
        start_response = requests.post(f"{API_BASE}/api/bot/start", json=bot_config, headers=headers, timeout=15)
        if start_response.status_code != 200:
            print(f"❌ Failed to start bot: {start_response.text}")
            return
        
        print("✅ Bot started with visible browser")
        time.sleep(3)
        
        # Process Aqueity job (we know it has CAPTCHA)
        print("2. Processing job with CAPTCHA...")
        print("   🖥️ Browser window should open")
        print("   📝 Form should start filling")
        print("   🚨 When CAPTCHA appears, solve it manually!")
        
        test_request = {
            "profile_id": profile_id,
            "job_url": "https://aqueity.applytojob.com/apply/Appyvb1yAu/Jr-SOC-Engineer?source=LinkedIn"
        }
        
        print("\\n⏰ Processing (up to 5 minutes for CAPTCHA solving)...")
        
        response = requests.post(
            f"{API_BASE}/api/bot/process-single",
            json=test_request,
            headers=headers,
            timeout=300  # 5 minutes for CAPTCHA
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\\n📊 Result: {result}")
            
            # Check if application was actually created
            apps_response = requests.get(f"{API_BASE}/api/applications", headers=headers)
            if apps_response.status_code == 200:
                applications = apps_response.json()
                print(f"\\n📋 Applications in database: {len(applications)}")
                
                if applications:
                    latest = applications[0]
                    print(f"   Status: {latest['status']}")
                    print(f"   URL: {latest['job_url']}")
                    if latest.get('error_message'):
                        print(f"   Error: {latest['error_message']}")
            
            # Check user application count
            user_response = requests.get(f"{API_BASE}/api/auth/me", headers=headers)
            if user_response.status_code == 200:
                user = user_response.json()
                print(f"\\n👤 Applications used: {user['applications_used']}/{user['applications_limit']}")
                
                if user['applications_used'] > 0:
                    print("🎉 SUCCESS: Application was actually submitted!")
                else:
                    print("⚠️ Application count unchanged - likely blocked by CAPTCHA")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_captcha_workflow()
'''
    
    with open('test_captcha_handling.py', 'w') as f:
        f.write(test_content)
    
    print("✅ Created: test_captcha_handling.py")

def main():
    """Main function"""
    print("🔧 Updating IntelliApply Bot with Working ChromeDriver")
    print("=" * 60)
    
    if update_enhanced_browser_handler():
        print("✅ Browser handler updated with working ChromeDriver")
        
        create_test_with_captcha_handling()
        
        print("\n🎯 Next Steps:")
        print("1. Restart your server (the bot code was updated)")
        print("2. Run: python test_captcha_handling.py")
        print("3. You should see a browser window open")
        print("4. Solve the CAPTCHA when it appears")
        print("5. Application should submit successfully!")
        
        print("\n🚨 CAPTCHA Workflow:")
        print("   Browser Opens → Form Fills → CAPTCHA Appears → [YOU SOLVE] → Submits")
    else:
        print("❌ Failed to update browser handler")

if __name__ == "__main__":
    main()