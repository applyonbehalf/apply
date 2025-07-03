# src/browser_handler.py (FIXED VERSION - Better Checkbox Handling)

import time
import random
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BrowserHandler:
    """Manages all Selenium WebDriver interactions."""
    VERSION = "18.1" # Fixed checkbox grouping version

    def __init__(self):
        options = webdriver.ChromeOptions()
        try:
            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, 10)
            print(f"BrowserHandler Version: {self.VERSION} initialized successfully.")
        except Exception as e: 
            print(f"Error initializing WebDriver: {e}")

    def find_required_empty_fields(self):
        return []

    def handle_cookie_banner(self):
        time.sleep(1)
        try:
            allow_keywords = ['allow', 'accept', 'ok', 'agree']
            xpath = " | ".join([f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{key}')]" for key in allow_keywords])
            buttons = self.driver.find_elements(By.XPATH, xpath)
            for button in buttons:
                if button.is_displayed() and button.is_enabled():
                    print("Found and clicked cookie consent button.")
                    button.click()
                    time.sleep(1)
                    return True
        except Exception:
            return False

    def navigate_to_url(self, url):
        if self.driver:
            print(f"Navigating to: {url}")
            self.driver.get(url)

    def find_navigation_button(self, keywords):
        """Enhanced button finding that handles various button types and formats."""
        if not self.driver: return None
        
        for keyword in keywords:
            # Method 1: Look for buttons with text containing the keyword
            xpath_patterns = [
                # Standard button elements
                f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}')]",
                # Input buttons
                f"//input[@type='button' and contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}')]",
                f"//input[@type='submit' and contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}')]",
                # Div or span elements that act as buttons
                f"//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}') and (contains(@class, 'btn') or contains(@class, 'button') or contains(@onclick, 'submit') or contains(@role, 'button'))]",
                # Links that act as buttons (but not href="#")
                f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}') and not(@href='#')]",
                # Any element with role="button"
                f"//*[@role='button' and contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}')]",
                # Look for elements with specific classes that might be buttons
                f"//*[contains(@class, 'submit') and contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}')]"
            ]
            
            for xpath in xpath_patterns:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            print(f"Found {keyword} button: {element.tag_name} with text: '{element.text}' and class: '{element.get_attribute('class')}'")
                            return element
                except Exception as e:
                    print(f"Error in xpath pattern {xpath}: {e}")
                    continue
        
        # If no button found with keywords, try a broader search for submit-type elements
        print(f"No button found with keywords {keywords}. Trying broader search...")
        try:
            # Look for any submit inputs or buttons
            submit_elements = self.driver.find_elements(By.XPATH, 
                "//input[@type='submit'] | //button[@type='submit'] | //*[contains(@class, 'submit')] | //*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit application')]")
            
            for element in submit_elements:
                if element.is_displayed() and element.is_enabled():
                    print(f"Found submit element via broader search: {element.tag_name} with text: '{element.text}'")
                    return element
        except Exception as e:
            print(f"Error in broader search: {e}")
        
        return None

    def find_next_button(self): 
        return self.find_navigation_button(['next', 'continue'])
    
    def find_submit_button(self): 
        return self.find_navigation_button(['submit', 'apply', 'finish', 'send'])

    def find_success_indicators(self):
        """Looks for keywords on the page that indicate a successful submission."""
        success_indicators = []
        success_keywords = ['thank you', 'thanks', 'success', 'submitted', 'complete', 'confirmation']
        xpath = "//*[" + " or ".join([f"contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{key}')" for key in success_keywords]) + "]"
        try:
            success_elements = self.driver.find_elements(By.XPATH, xpath)
            for el in success_elements:
                if el.is_displayed():
                    print(f"Found success indicator text: {el.text}")
                    success_indicators.append(el.text)
        except Exception: pass
        return success_indicators

    def get_form_elements_fully(self):
        if not self.driver: return []
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        return self._extract_form_elements()

    def _extract_form_elements(self):
        """Improved parser that properly groups checkboxes and radio buttons by their question."""
        form_fields = []
        all_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input, textarea, select")
        choice_groups = {}
        processed_elements = set()
        
        for element in all_inputs:
            if not element.is_displayed() or element in processed_elements: 
                continue
            
            field_type = element.get_attribute('type')
            
            if field_type in ['radio', 'checkbox']:
                # Find the question label for this choice group
                question_label = self._find_question_for_choice(element)
                
                if question_label:
                    # Group by question instead of name attribute
                    group_key = question_label
                    
                    if group_key not in choice_groups:
                        choice_groups[group_key] = {
                            'label': question_label, 
                            'elements': [], 
                            'type': field_type, 
                            'required': self._is_choice_group_required(element)
                        }
                    
                    choice_groups[group_key]['elements'].append(element)
                    processed_elements.add(element)
                else:
                    # Fallback: treat as individual field if no question found
                    field = self._parse_element_details(element)
                    if field: form_fields.append(field)
                    processed_elements.add(element)
            else:
                field = self._parse_element_details(element)
                if field: form_fields.append(field)
                processed_elements.add(element)
        
        # Add grouped choices to form fields
        form_fields.extend(choice_groups.values())
        return form_fields

    def _find_question_for_choice(self, element):
        """
        Find the actual question text for a checkbox/radio button.
        This looks for nearby text that looks like a question.
        """
        try:
            # Method 1: Look for question text in parent containers
            current = element
            for _ in range(5):  # Go up to 5 levels
                current = current.find_element(By.XPATH, "./..")
                # Look for text that ends with '?' or contains 'sponsorship', 'visa', etc.
                text_elements = current.find_elements(By.XPATH, ".//*[contains(text(), '?') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sponsorship') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'visa') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'require')]")
                
                for text_elem in text_elements:
                    text = text_elem.text.strip()
                    if text and len(text) > 10:  # Reasonable question length
                        return text
                        
        except Exception:
            pass
            
        try:
            # Method 2: Look for preceding text elements
            preceding_elements = self.driver.find_elements(By.XPATH, f"//input[@type='{element.get_attribute('type')}' and @value='{element.get_attribute('value')}']/preceding::*[contains(text(), '?')][1]")
            if preceding_elements:
                return preceding_elements[0].text.strip()
        except Exception:
            pass
            
        return None

    def _is_choice_group_required(self, element):
        """Check if the choice group is required by looking for required indicators."""
        try:
            # Look for asterisk (*) or 'required' in nearby elements
            parent = element.find_element(By.XPATH, "./ancestor::div[1]")
            return '*' in parent.text or 'required' in parent.get_attribute('class').lower()
        except:
            return element.get_attribute('required') is not None

    def _parse_element_details(self, element):
        label = self._get_label_for_element(element)
        if not label: return None
        is_required = element.get_attribute('required') is not None
        if '*' in label: is_required = True
        
        tag = element.tag_name
        field_type = element.get_attribute('type')
        field_data = {'label': label.replace('*', '').strip(), 'element': element, 'required': is_required}

        if tag == 'select':
            field_data['type'] = 'dropdown'
            field_data['options'] = [opt.text for opt in Select(element).options if opt.text and '--' not in opt.text]
        elif tag == 'textarea': 
            field_data['type'] = 'textarea'
        else: 
            field_data['type'] = field_type
        
        return field_data

    def _get_label_for_element(self, element, is_group=False):
        # Try to find an associated <label> tag first
        try:
            element_id = element.get_attribute('id')
            if element_id:
                label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{element_id}']")
                return label.text.strip()
        except: pass
        
        # For grouped elements, find the question label in the parent container
        if is_group:
            try:
                container = element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'form-group') or contains(@class, 'form-field') or contains(@class, 'question')]")
                label = container.find_element(By.CSS_SELECTOR, "label, .control-label")
                return label.text.strip()
            except: pass
        
        # Fallback for labels that wrap the input
        try:
            parent_label = element.find_element(By.XPATH, "./ancestor::label[1]")
            return parent_label.text.strip()
        except: pass
        
        # Final fallback
        return element.get_attribute('placeholder') or element.get_attribute('name') or element.get_attribute('value') or ""
    
    def fill_text_input_slowly(self, element, text):
        if not element: return
        try:
            field_type = element.get_attribute('type')
            if field_type == 'file':
                if text and os.path.exists(str(text)):
                    element.send_keys(str(text))
                    print(f"✅ Uploaded file: {text}")
                else: 
                    print(f"⚠️ Warning: File path not found or invalid: {text}")
            else:
                element.clear()
                for char in str(text):
                    element.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.1))
                print(f"✅ Filled text field with: {text}")
        except Exception as e: 
            print(f"❌ Error filling input: {e}")

    def select_dropdown_option_by_text(self, element, text):
        if element:
            try: 
                Select(element).select_by_visible_text(text)
            except Exception as e: 
                print(f"❌ Error selecting dropdown option: {e}")

    def click_choice_button(self, elements, choice_to_make):
        """
        Improved choice clicking that handles mutual exclusivity for radio buttons
        and proper selection for checkboxes.
        """
        if not elements: return False
        
        try:
            # For radio buttons and single checkboxes, ensure only one is selected
            element_type = elements[0].get_attribute('type')
            
            # First, uncheck all elements if this is a radio group or exclusive checkbox group
            if element_type == 'radio' or (element_type == 'checkbox' and len(elements) > 1):
                for elem in elements:
                    if elem.is_selected():
                        self.driver.execute_script("arguments[0].click();", elem)
                        print(f"🔄 Unchecked: {self._get_label_for_element(elem)}")
            
            # Now find and click the correct choice
            for element in elements:
                label_text = self._get_label_for_element(element)
                value_text = element.get_attribute('value')
                
                # Check if this element matches our choice
                if (label_text and choice_to_make.lower() in label_text.lower()) or \
                   (value_text and choice_to_make.lower() == value_text.lower()):
                    
                    if not element.is_selected():
                        self.driver.execute_script("arguments[0].click();", element)
                        print(f"✅ Selected: {choice_to_make}")
                        return True
                    else:
                        print(f"ℹ️ Already selected: {choice_to_make}")
                        return True
            
            print(f"❌ Could not find choice '{choice_to_make}' among options")
            return False
            
        except Exception as e:
            print(f"❌ Error clicking choice button: {e}")
            return False

    def close_browser(self):
        if self.driver: 
            self.driver.quit()