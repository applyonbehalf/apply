# bot/enhanced_browser_handler.py - Multi-user enhanced browser handler
import time
import random
import os
import uuid
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from typing import Dict, List, Optional, Any
from datetime import datetime

class EnhancedBrowserHandler:
    """Enhanced browser handler for multi-user job applications"""
    
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
        """Setup browser with anti-detection measures"""
        options = webdriver.ChromeOptions()
        
        # Headless mode for production
        if self.headless:
            options.add_argument("--headless")
        
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
            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            
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
            
            # Close generic popups
            popup_selectors = [
                "button[aria-label*='close']",
                "button[class*='close']",
                ".modal button[class*='close']",
                "[role='dialog'] button"
            ]
            
            for selector in popup_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements[:2]:  # Only try first 2
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            await asyncio.sleep(1)
                            break
                except:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Popup handling error: {e}")
    
    async def scan_form_elements(self) -> List[Dict[str, Any]]:
        """Scan and analyze form elements on the page"""
        try:
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
        try:
            # Method 1: Look in parent containers
            current = element
            for _ in range(5):
                try:
                    current = current.find_element(By.XPATH, "./..")
                    text_elements = current.find_elements(By.XPATH, ".//*[contains(text(), '?') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sponsorship') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'visa')]")
                    
                    for text_elem in text_elements:
                        text = text_elem.text.strip()
                        if text and len(text) > 10:
                            return text
                except:
                    break
            
            # Method 2: Look for fieldset legend
            try:
                fieldset = element.find_element(By.XPATH, "./ancestor::fieldset[1]")
                legend = fieldset.find_element(By.TAG_NAME, "legend")
                return legend.text.strip()
            except:
                pass
            
            return None
            
        except Exception:
            return None
    
    async def _analyze_field(self, element) -> Optional[Dict[str, Any]]:
        """Analyze a single form field"""
        try:
            label = await self._get_field_label(element)
            if not label:
                return None
            
            field_type = element.get_attribute('type') or element.tag_name
            is_required = element.get_attribute('required') is not None or '*' in label
            
            field_data = {
                'label': label.replace('*', '').strip(),
                'element': element,
                'type': field_type,
                'required': is_required,
                'name': element.get_attribute('name'),
                'id': element.get_attribute('id')
            }
            
            # Additional data for select elements
            if element.tag_name == 'select':
                field_data['type'] = 'dropdown'
                try:
                    select = Select(element)
                    field_data['options'] = [opt.text for opt in select.options if opt.text and '--' not in opt.text]
                except:
                    field_data['options'] = []
            
            return field_data
            
        except Exception:
            return None
    
    async def _get_field_label(self, element) -> Optional[str]:
        """Get the label for a form field"""
        try:
            # Method 1: Associated label
            element_id = element.get_attribute('id')
            if element_id:
                try:
                    label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{element_id}']")
                    return label.text.strip()
                except:
                    pass
            
            # Method 2: Parent label
            try:
                parent_label = element.find_element(By.XPATH, "./ancestor::label[1]")
                return parent_label.text.strip()
            except:
                pass
            
            # Method 3: Nearby text
            try:
                parent = element.find_element(By.XPATH, "./..")
                labels = parent.find_elements(By.TAG_NAME, "label")
                if labels:
                    return labels[0].text.strip()
            except:
                pass
            
            # Method 4: Placeholder or name
            placeholder = element.get_attribute('placeholder')
            if placeholder:
                return placeholder
            
            name = element.get_attribute('name')
            if name:
                return name.replace('_', ' ').title()
            
            return None
            
        except Exception:
            return None
    
    async def fill_field(self, field: Dict[str, Any], value: str) -> bool:
        """Fill a form field with the given value"""
        try:
            element = field['element']
            field_type = field['type']
            
            # Scroll to element
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            await asyncio.sleep(random.uniform(0.5, 1.0))
            
            if field_type == 'file':
                if value and os.path.exists(str(value)):
                    element.send_keys(str(value))
                    print(f"📎 Uploaded file: {os.path.basename(value)}")
                    return True
                else:
                    print(f"⚠️ File not found: {value}")
                    return False
            
            elif field_type == 'dropdown':
                try:
                    select = Select(element)
                    select.select_by_visible_text(value)
                    print(f"📋 Selected dropdown: {value}")
                    return True
                except Exception as e:
                    print(f"❌ Dropdown selection failed: {e}")
                    return False
            
            elif field_type in ['radio', 'checkbox']:
                # This is handled separately in fill_choice_field
                return False
            
            else:
                # Text input
                element.clear()
                
                # Human-like typing
                for char in str(value):
                    element.send_keys(char)
                    await asyncio.sleep(random.uniform(0.05, 0.15))
                
                print(f"✍️ Filled field: {field['label'][:30]}...")
                return True
                
        except Exception as e:
            print(f"❌ Field filling error: {e}")
            return False
    
    async def fill_choice_field(self, field: Dict[str, Any], choice: str) -> bool:
        """Fill a choice field (radio/checkbox)"""
        try:
            elements = field['elements']
            field_type = field['type']
            
            # For radio buttons, uncheck all first
            if field_type == 'radio':
                for elem in elements:
                    if elem.is_selected():
                        elem.click()
                        await asyncio.sleep(0.5)
            
            # Find and click the right choice
            for element in elements:
                label_text = await self._get_field_label(element)
                value_text = element.get_attribute('value')
                
                if (label_text and choice.lower() in label_text.lower()) or \
                   (value_text and choice.lower() == value_text.lower()):
                    
                    if not element.is_selected():
                        self.driver.execute_script("arguments[0].click();", element)
                        print(f"☑️ Selected choice: {choice}")
                        await asyncio.sleep(random.uniform(0.5, 1.0))
                        return True
                    else:
                        print(f"ℹ️ Choice already selected: {choice}")
                        return True
            
            print(f"❌ Choice not found: {choice}")
            return False
            
        except Exception as e:
            print(f"❌ Choice selection error: {e}")
            return False
    
    async def check_for_captcha(self) -> Optional[Dict[str, Any]]:
        """Check if there's a CAPTCHA on the page"""
        try:
            captcha_selectors = [
                'iframe[src*="recaptcha"]',
                '.g-recaptcha',
                '#recaptcha',
                '.captcha',
                '[class*="captcha"]',
                '.cf-challenge-form',  # Cloudflare
                '[data-sitekey]'  # reCAPTCHA
            ]
            
            for selector in captcha_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            print(f"🚨 CAPTCHA detected: {selector}")
                            
                            # Take screenshot
                            screenshot_url = await self._take_captcha_screenshot()
                            
                            return {
                                'type': 'recaptcha' if 'recaptcha' in selector else 'unknown',
                                'element': element,
                                'screenshot_url': screenshot_url,
                                'page_url': self.driver.current_url,
                                'selector': selector
                            }
                except:
                    continue
            
            return None
            
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
            
            # TODO: Upload to Supabase Storage (implement later)
            # For now, return local path
            return filepath
            
        except Exception as e:
            print(f"❌ Screenshot error: {e}")
            return None
    
    async def submit_application(self) -> Dict[str, Any]:
        """Submit the application form"""
        try:
            # Find submit button
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button[class*='submit']",
                "button[id*='submit']",
                "*[role='button'][class*='submit']",
                "a[class*='submit'][href='#']"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            text = element.text.lower()
                            if any(keyword in text for keyword in ['submit', 'apply', 'send', 'finish']):
                                submit_button = element
                                break
                    if submit_button:
                        break
                except:
                    continue
            
            if not submit_button:
                return {'success': False, 'error': 'Submit button not found'}
            
            print(f"🎯 Found submit button: {submit_button.text}")
            
            # Scroll to submit button
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_button)
            await asyncio.sleep(2)
            
            # Record current URL for comparison
            current_url = self.driver.current_url
            
            # Click submit
            try:
                submit_button.click()
            except:
                # Try JavaScript click if regular click fails
                self.driver.execute_script("arguments[0].click();", submit_button)
            
            print("📤 Clicked submit button")
            
            # Wait for submission
            await asyncio.sleep(3)
            
            # Check for success indicators
            new_url = self.driver.current_url
            success_indicators = await self._check_success_indicators()
            
            if new_url != current_url:
                print("✅ URL changed - likely successful submission")
                self.session_stats['applications_successful'] += 1
                return {'success': True, 'message': 'Application submitted successfully'}
            
            elif success_indicators:
                print(f"✅ Success indicators found: {success_indicators}")
                self.session_stats['applications_successful'] += 1
                return {'success': True, 'message': 'Application submitted successfully'}
            
            else:
                # Check for error messages
                error_messages = await self._check_error_messages()
                if error_messages:
                    print(f"❌ Error messages found: {error_messages}")
                    return {'success': False, 'error': f"Submission errors: {', '.join(error_messages)}"}
                else:
                    print("⚠️ Submission status unclear")
                    return {'success': False, 'error': 'Submission status unclear'}
            
        except Exception as e:
            print(f"❌ Submission error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _check_success_indicators(self) -> List[str]:
        """Check for success indicators on the page"""
        try:
            success_keywords = ['thank you', 'thanks', 'success', 'submitted', 'complete', 'confirmation', 'received']
            success_indicators = []
            
            for keyword in success_keywords:
                try:
                    xpath = f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword}')]"
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        if element.is_displayed() and len(element.text.strip()) > 0:
                            success_indicators.append(element.text.strip())
                            break
                except:
                    continue
            
            return success_indicators
            
        except Exception:
            return []
    
    async def _check_error_messages(self) -> List[str]:
        """Check for error messages on the page"""
        try:
            error_selectors = [
                ".error",
                ".alert-danger",
                ".alert-error", 
                "[class*='error']",
                "[role='alert']",
                ".validation-error"
            ]
            
            error_messages = []
            for selector in error_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.text.strip():
                            error_messages.append(element.text.strip())
                except:
                    continue
            
            return error_messages
            
        except Exception:
            return []
    
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