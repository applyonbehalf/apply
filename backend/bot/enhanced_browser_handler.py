# bot/enhanced_browser_handler.py - SIMPLIFIED WORKING VERSION
import time
import random
import os
import uuid
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from typing import Dict, List, Optional, Any
from datetime import datetime

class EnhancedBrowserHandler:
    """Simplified enhanced browser handler that actually works"""
    
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
        
        print(f"🤖 Initializing browser handler for session {self.session_id[:8]}")
        self._setup_browser()
    
    def _setup_browser(self):
        """Setup browser with simplified, working configuration"""
        options = webdriver.ChromeOptions()
        
        # Headless mode setting
        if self.headless:
            options.add_argument("--headless")
            print(f"🔇 Browser running in headless mode")
        else:
            print(f"👁️ Browser running in visible mode")
        
        # Essential options only
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # Use the path that worked in our tests
            driver_path = '/opt/homebrew/bin/chromedriver'
            
            if os.path.exists(driver_path):
                service = ChromeService(executable_path=driver_path)
                print(f"✅ Using ChromeDriver at: {driver_path}")
            else:
                service = ChromeService()  # Let it find automatically
                print("✅ Using system ChromeDriver")
            
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Anti-detection script
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set window size
            if not self.headless:
                self.driver.maximize_window()
            else:
                self.driver.set_window_size(1920, 1080)
            
            self.wait = WebDriverWait(self.driver, 15)
            print(f"✅ Browser initialized successfully for session {self.session_id[:8]}")
            
        except Exception as e:
            print(f"❌ Error initializing browser: {e}")
            raise Exception(f"Browser initialization failed: {e}")
    
    async def navigate_to_job(self, job_url: str, application_id: str) -> bool:
        """Navigate to a job application page"""
        try:
            self.current_application_id = application_id
            self.current_url = job_url
            
            print(f"🌐 Navigating to: {job_url}")
            self.driver.get(job_url)
            
            # Wait for page load
            await asyncio.sleep(3)
            
            print(f"✅ Successfully navigated to job page")
            return True
            
        except Exception as e:
            print(f"❌ Navigation error: {e}")
            return False
    
    async def check_for_captcha(self) -> Optional[Dict[str, Any]]:
        """Simple CAPTCHA detection"""
        try:
            print("🔍 Checking for CAPTCHA...")
            
            # Check for reCAPTCHA response token (indicates solved)
            try:
                response_element = self.driver.find_element(By.CSS_SELECTOR, '[name="g-recaptcha-response"]')
                response_value = response_element.get_attribute('value')
                if response_value and len(response_value) > 10:
                    print(f"✅ CAPTCHA already solved (token length: {len(response_value)})")
                    return None  # CAPTCHA is solved
            except:
                pass
            
            # Check for CAPTCHA iframe
            try:
                iframe = self.driver.find_element(By.CSS_SELECTOR, 'iframe[src*="recaptcha"]')
                if iframe.is_displayed():
                    # Take screenshot
                    screenshot_path = await self._take_captcha_screenshot()
                    
                    print(f"🚨 CAPTCHA detected - manual solving required")
                    return {
                        'type': 'recaptcha',
                        'screenshot_url': screenshot_path,
                        'page_url': self.driver.current_url,
                        'detected_at': datetime.utcnow().isoformat()
                    }
            except:
                pass
            
            print("✅ No CAPTCHA detected")
            return None
            
        except Exception as e:
            print(f"❌ CAPTCHA check error: {e}")
            return None
    
    async def _take_captcha_screenshot(self) -> str:
        """Take a screenshot for CAPTCHA solving"""
        try:
            # Create screenshots directory
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
    
    async def wait_for_captcha_solution(self, captcha_info: Dict[str, Any], timeout: int = 300) -> bool:
        """Wait for manual CAPTCHA solution with user interaction"""
        try:
            print(f"⏳ CAPTCHA DETECTED - Manual solving required")
            print(f"📸 Screenshot: {captcha_info.get('screenshot_url', 'N/A')}")
            print(f"")
            print(f"🔔 PLEASE SOLVE THE CAPTCHA IN THE BROWSER WINDOW")
            print(f"   1. Look at the browser window")
            print(f"   2. Click the 'I'm not a robot' checkbox")
            print(f"   3. Complete any image challenges if they appear")
            print(f"   4. Wait for the green checkmark")
            print(f"")
            print(f"⏰ Bot will check every 10 seconds for up to {timeout//60} minutes...")
            
            start_time = time.time()
            check_interval = 10  # Check every 10 seconds
            
            while time.time() - start_time < timeout:
                await asyncio.sleep(check_interval)
                
                # Check if CAPTCHA is solved
                current_captcha = await self.check_for_captcha()
                
                if not current_captcha:
                    print("✅ CAPTCHA solved! Continuing with application...")
                    return True
                
                elapsed = int(time.time() - start_time)
                print(f"⏳ Still waiting for CAPTCHA solution... ({elapsed}s elapsed)")
            
            print("⏰ Timeout waiting for CAPTCHA solution")
            return False
            
        except Exception as e:
            print(f"❌ Error waiting for CAPTCHA solution: {e}")
            return False
    
    async def scan_form_elements(self, skip_captcha_check: bool = False) -> List[Dict[str, Any]]:
        """Scan form elements (simplified version)"""
        try:
            # Check for CAPTCHA first unless skipped
            if not skip_captcha_check:
                captcha_info = await self.check_for_captcha()
                if captcha_info:
                    print("🚨 CAPTCHA detected - returning CAPTCHA info")
                    return [{'__captcha_detected__': True, 'captcha_info': captcha_info}]
            
            print("📋 Scanning form elements...")
            
            # Simple form scanning
            inputs = self.driver.find_elements(By.CSS_SELECTOR, "input, textarea, select")
            form_fields = []
            
            for element in inputs:
                if not element.is_displayed():
                    continue
                
                field_type = element.get_attribute('type') or 'text'
                
                # Skip certain types
                if field_type in ['hidden', 'submit', 'button']:
                    continue
                
                field_data = {
                    'element': element,
                    'type': field_type,
                    'name': element.get_attribute('name') or element.get_attribute('id') or '',
                    'label': element.get_attribute('placeholder') or 'Unknown field',
                    'required': element.get_attribute('required') is not None
                }
                
                form_fields.append(field_data)
            
            print(f"📋 Found {len(form_fields)} form fields")
            return form_fields
            
        except Exception as e:
            print(f"❌ Form scanning error: {e}")
            return []
    
    async def submit_application(self) -> Dict[str, Any]:
        """Submit the application using enhanced button detection"""
        try:
            print("🚀 Attempting to submit application...")
            
            # Use the enhanced submit button finder
            submit_success = await self.find_submit_button()
            
            if submit_success:
                # Check for success indicators after submission
                await asyncio.sleep(3)
                
                # Look for success messages
                page_source = self.driver.page_source.lower()
                success_indicators = [
                    'thank you',
                    'success',
                    'submitted',
                    'received',
                    'confirmation',
                    'complete'
                ]
                
                for indicator in success_indicators:
                    if indicator in page_source:
                        return {
                            'success': True,
                            'message': f'Application submitted successfully (detected: {indicator})',
                            'final_url': self.driver.current_url
                        }
                
                # If no explicit success indicator, assume success if no error
                return {
                    'success': True,
                    'message': 'Application submitted (submit button clicked successfully)',
                    'final_url': self.driver.current_url
                }
            else:
                return {
                    'success': False,
                    'error': 'Could not find or click submit button'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Submission error: {str(e)}'
            }
    
    
    async def fill_field(self, field_data: Dict[str, Any], value: Any) -> bool:
        """Fill a form field with the given value"""
        try:
            element = field_data['element']
            field_type = field_data.get('type', 'text')
            field_label = field_data.get('label', 'Unknown')
            
            print(f"📝 Filling field '{field_label}' with: {value}")
            
            # Scroll to element
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            await asyncio.sleep(0.5)
            
            if field_type in ['text', 'email', 'tel', 'url', 'search']:
                # Text input
                element.clear()
                element.send_keys(str(value))
                
            elif field_type == 'textarea':
                # Textarea
                element.clear()
                element.send_keys(str(value))
                
            elif field_type == 'select-one':
                # Dropdown
                from selenium.webdriver.support.ui import Select
                select = Select(element)
                
                # Try to select by visible text first
                try:
                    select.select_by_visible_text(str(value))
                except:
                    # If that fails, try by value
                    try:
                        select.select_by_value(str(value))
                    except:
                        # If both fail, select first non-empty option
                        options = [opt for opt in select.options if opt.text.strip() and opt.text.strip() != '--']
                        if options:
                            select.select_by_visible_text(options[0].text)
                            
            elif field_type == 'checkbox':
                # Checkbox - check if value is truthy
                if value and str(value).lower() not in ['false', 'no', '0', '']:
                    if not element.is_selected():
                        element.click()
                else:
                    if element.is_selected():
                        element.click()
                        
            elif field_type == 'radio':
                # Radio button - click if this is the selected value
                if str(value).lower() in field_label.lower():
                    element.click()
                    
            elif field_type == 'file':
                # File upload
                if value and os.path.exists(str(value)):
                    element.send_keys(str(value))
                    
            print(f"✅ Successfully filled field '{field_label}'")
            return True
            
        except Exception as e:
            print(f"❌ Error filling field '{field_label}': {e}")
            return False
    
    
    async def find_submit_button(self) -> bool:
        """Enhanced submit button detection with click interception handling"""
        try:
            print("🔍 Looking for submit button...")
            
            submit_button = None
            
            # Method 1: Direct CSS selectors (avoiding :contains which doesn't work)
            direct_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                '.resumator-external-apply-button',
                '*[class*="submit"]',
                '*[class*="apply"]',
                '*[id*="submit"]',
                '*[id*="apply"]'
            ]
            
            for selector in direct_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            button_text = button.text.strip()
                            button_class = button.get_attribute('class') or ''
                            print(f"✅ Found submit button: '{button_text}' (class: {button_class})")
                            submit_button = button
                            break
                    if submit_button:
                        break
                except Exception as e:
                    print(f"⚠️ Error with selector {selector}: {e}")
                    continue
            
            # Method 2: XPath text-based search if CSS failed
            if not submit_button:
                print("🔍 Trying XPath text-based search...")
                
                xpath_patterns = [
                    "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]",
                    "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply')]",
                    "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply')]",
                    "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]",
                    "//*[contains(@class, 'resumator-external-apply-button')]",
                    "//*[contains(@class, 'indeed-apply')]"
                ]
                
                for xpath in xpath_patterns:
                    try:
                        elements = self.driver.find_elements(By.XPATH, xpath)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                element_text = element.text.strip() or element.get_attribute('value') or 'No text'
                                print(f"✅ Found submit element via XPath: '{element_text}' (tag: {element.tag_name})")
                                submit_button = element
                                break
                        if submit_button:
                            break
                    except Exception as e:
                        print(f"⚠️ Error with XPath {xpath}: {e}")
                        continue
            
            # Method 3: Try clicking the submit button with multiple strategies
            if submit_button:
                return await self._click_submit_button_with_fallbacks(submit_button)
            else:
                print("❌ No submit button found")
                await self._debug_available_buttons()
                return False
                
        except Exception as e:
            print(f"❌ Error in submit button detection: {e}")
            return False
    
    async def _click_submit_button_with_fallbacks(self, submit_button) -> bool:
        """Try multiple strategies to click the submit button"""
        try:
            print(f"🎯 Attempting to click submit button: '{submit_button.text}'")
            
            # Strategy 1: Remove overlaying elements first
            print("🧹 Removing potential overlay elements...")
            self.driver.execute_script("""
                // Remove Indeed widget overlay that's blocking clicks
                var indeedWidget = document.getElementById('resumator-indeed-apply-widget');
                if (indeedWidget) {
                    indeedWidget.style.display = 'none';
                    console.log('Removed Indeed widget overlay');
                }
                
                // Remove other potential overlays
                var overlays = document.querySelectorAll('[style*="position: fixed"], [style*="z-index"]');
                overlays.forEach(function(overlay) {
                    if (overlay.style.zIndex > 1000) {
                        overlay.style.display = 'none';
                    }
                });
                
                // Remove any modal backdrops
                var modals = document.querySelectorAll('.modal-backdrop, .overlay, [class*="overlay"]');
                modals.forEach(function(modal) {
                    modal.style.display = 'none';
                });
            """)
            
            await asyncio.sleep(1)
            
            # Strategy 2: Scroll to submit button and ensure it's in view
            print("📍 Scrolling to submit button...")
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_button)
            await asyncio.sleep(2)
            
            # Strategy 3: Try normal click first
            try:
                print("🖱️ Attempting normal click...")
                submit_button.click()
                print("✅ Normal click successful!")
                await asyncio.sleep(3)
                return True
                
            except Exception as click_error:
                print(f"⚠️ Normal click failed: {click_error}")
                
                # Strategy 4: JavaScript click
                try:
                    print("🖱️ Attempting JavaScript click...")
                    self.driver.execute_script("arguments[0].click();", submit_button)
                    print("✅ JavaScript click successful!")
                    await asyncio.sleep(3)
                    return True
                    
                except Exception as js_error:
                    print(f"⚠️ JavaScript click failed: {js_error}")
                    
                    # Strategy 5: Force click with coordinates
                    try:
                        print("🖱️ Attempting ActionChains click...")
                        from selenium.webdriver.common.action_chains import ActionChains
                        actions = ActionChains(self.driver)
                        actions.move_to_element(submit_button).click().perform()
                        print("✅ ActionChains click successful!")
                        await asyncio.sleep(3)
                        return True
                        
                    except Exception as action_error:
                        print(f"⚠️ ActionChains click failed: {action_error}")
                        
                        # Strategy 6: Submit form directly if button is in a form
                        try:
                            print("📋 Attempting form submission...")
                            form = submit_button.find_element(By.XPATH, "./ancestor::form[1]")
                            self.driver.execute_script("arguments[0].submit();", form)
                            print("✅ Form submission successful!")
                            await asyncio.sleep(3)
                            return True
                            
                        except Exception as form_error:
                            print(f"⚠️ Form submission failed: {form_error}")
                            
                            # Strategy 7: Try clicking parent elements
                            try:
                                print("🖱️ Attempting to click parent element...")
                                parent = submit_button.find_element(By.XPATH, "./..")
                                self.driver.execute_script("arguments[0].click();", parent)
                                print("✅ Parent element click successful!")
                                await asyncio.sleep(3)
                                return True
                                
                            except Exception as parent_error:
                                print(f"❌ All click strategies failed: {parent_error}")
                                return False
                    
        except Exception as e:
            print(f"❌ Error in click strategies: {e}")
            return False
    
    async def _debug_available_buttons(self):
        """Debug helper to show all available buttons on the page"""
        try:
            print("🔍 DEBUG: Available buttons on page:")
            all_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button, input[type="button"], input[type="submit"], a[role="button"], div[role="button"], *[onclick]')
            
            visible_buttons = []
            for btn in all_buttons:
                try:
                    if btn.is_displayed():
                        text = btn.text.strip() or btn.get_attribute('value') or btn.get_attribute('aria-label') or 'No text'
                        btn_class = btn.get_attribute('class') or 'No class'
                        btn_id = btn.get_attribute('id') or 'No ID'
                        tag = btn.tag_name
                        visible_buttons.append(f"   {tag}: '{text[:50]}' (class: {btn_class[:50]}, id: {btn_id[:30]})")
                except:
                    continue
            
            print(f"   Found {len(visible_buttons)} visible clickable elements:")
            for i, btn_info in enumerate(visible_buttons[:20]):  # Show first 20
                print(f"   {i+1}. {btn_info}")
                
        except Exception as e:
            print(f"   ❌ Debug error: {e}")

    
    async def get_user_profile_data(self, user_id: str, profile_id: str = None) -> Dict[str, Any]:
        """Fetch user profile data from database instead of file"""
        try:
            from database.connection import db
            
            print(f"📋 Fetching profile data for user: {user_id}")
            
            if profile_id:
                # Get specific profile
                profile = await db.get_profile_by_id(profile_id)
            else:
                # Get user's default profile
                profile = await db.get_user_default_profile(user_id)
            
            if profile and profile.get('profile_data'):
                profile_data = profile['profile_data']
                print(f"✅ Loaded profile: {profile.get('profile_name', 'Default')}")
                print(f"   User name: {profile_data.get('personal_info', {}).get('full_name', 'Unknown')}")
                print(f"   Email: {profile_data.get('personal_info', {}).get('email', 'Unknown')}")
                return profile_data
            else:
                print(f"⚠️ No profile found for user {user_id}, using default data")
                return self._get_default_profile_data()
                
        except Exception as e:
            print(f"❌ Error fetching profile data: {e}")
            return self._get_default_profile_data()
    
    def _get_default_profile_data(self) -> Dict[str, Any]:
        """Fallback default profile data"""
        return {
            "personal_info": {
                "legal_first_name": "Job",
                "legal_last_name": "Applicant",
                "full_name": "Job Applicant",
                "email": "applicant@example.com",
                "phone": "+1-555-000-0000",
                "address_line_1": "123 Main Street",
                "city": "Any City",
                "state_province": "CA",
                "zip_postal_code": "90210"
            },
            "experience": {
                "total_years_professional_experience": "3-5 years",
                "salary_expectation": "$70,000 - $90,000"
            },
            "preferences": {
                "work_preference": "Hybrid"
            },
            "eligibility": {
                "work_authorization": "authorized",
                "visa_sponsorship_required": False,
                "visa_sponsorship": "No"
            }
        }

    def close(self):
        """Close the browser"""
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
