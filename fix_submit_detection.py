# fix_submit_detection.py - Enhanced submit button detection
import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def load_profile():
    """Load profile data"""
    try:
        with open('/Users/shubhammane/Desktop/IntelliApply_Bot/data/profile.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Could not load profile: {e}")
        return None

def setup_browser():
    """Setup browser with working configuration"""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        service = ChromeService()
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.maximize_window()
        return driver
    except Exception as e:
        print(f"❌ Browser setup failed: {e}")
        return None

def enhanced_submit_detection(driver):
    """Enhanced submit button detection"""
    
    print("🔍 Enhanced Submit Button Detection")
    print("=" * 40)
    
    # Method 1: Standard submit button selectors
    standard_selectors = [
        "button[type='submit']",
        "input[type='submit']",
        "button[id*='submit']",
        "button[class*='submit']"
    ]
    
    print("1. Checking standard submit selectors...")
    for selector in standard_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    print(f"   ✅ Found: {selector} - Text: '{element.text}'")
                    return element
        except Exception as e:
            print(f"   ⚠️ Error with {selector}: {e}")
    
    # Method 2: Text-based button detection
    print("2. Checking text-based buttons...")
    button_keywords = ['submit', 'apply', 'send application', 'continue', 'next', 'finish']
    
    all_buttons = driver.find_elements(By.TAG_NAME, "button")
    all_buttons.extend(driver.find_elements(By.CSS_SELECTOR, "a[role='button']"))
    all_buttons.extend(driver.find_elements(By.CSS_SELECTOR, "div[role='button']"))
    all_buttons.extend(driver.find_elements(By.CSS_SELECTOR, "*[onclick]"))
    
    for button in all_buttons:
        try:
            if button.is_displayed() and button.is_enabled():
                button_text = button.text.lower().strip()
                if button_text:
                    for keyword in button_keywords:
                        if keyword in button_text:
                            print(f"   ✅ Found text button: '{button.text}' (matches '{keyword}')")
                            return button
        except:
            continue
    
    # Method 3: Check for links that might be submit buttons
    print("3. Checking submit links...")
    links = driver.find_elements(By.TAG_NAME, "a")
    for link in links:
        try:
            if link.is_displayed():
                link_text = link.text.lower().strip()
                href = link.get_attribute('href') or ''
                if any(keyword in link_text for keyword in button_keywords):
                    if 'javascript:' in href or href == '#' or 'submit' in href:
                        print(f"   ✅ Found submit link: '{link.text}'")
                        return link
        except:
            continue
    
    # Method 4: Find any clickable element with submit-related attributes
    print("4. Checking elements with submit attributes...")
    submit_xpath_patterns = [
        "//*[contains(@id, 'submit')]",
        "//*[contains(@class, 'submit')]", 
        "//*[contains(@name, 'submit')]",
        "//*[contains(@value, 'submit')]",
        "//*[contains(@aria-label, 'submit')]",
        "//*[contains(text(), 'Submit Application')]",
        "//*[contains(text(), 'Apply Now')]",
        "//*[contains(text(), 'Send Application')]"
    ]
    
    for xpath in submit_xpath_patterns:
        try:
            elements = driver.find_elements(By.XPATH, xpath)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    print(f"   ✅ Found via XPath: '{element.text}' (tag: {element.tag_name})")
                    return element
        except:
            continue
    
    # Method 5: Look for form and find its submit mechanism
    print("5. Checking form submit mechanisms...")
    forms = driver.find_elements(By.TAG_NAME, "form")
    for form in forms:
        try:
            # Look for submit buttons within the form
            form_submits = form.find_elements(By.CSS_SELECTOR, "button, input[type='submit'], *[type='submit']")
            for submit_elem in form_submits:
                if submit_elem.is_displayed() and submit_elem.is_enabled():
                    print(f"   ✅ Found form submit: '{submit_elem.text}' in form")
                    return submit_elem
        except:
            continue
    
    print("❌ No submit button found with enhanced detection")
    return None

def apply_to_job_enhanced():
    """Enhanced job application with better submit detection"""
    
    print("🎯 Enhanced Job Application Automation")
    print("=" * 50)
    
    # Load profile
    profile = load_profile()
    if not profile:
        return False
    
    personal_info = profile.get('personal_info', {})
    eligibility = profile.get('eligibility', {})
    
    # Setup browser
    driver = setup_browser()
    if not driver:
        return False
    
    try:
        # Navigate to job
        job_url = "https://aqueity.applytojob.com/apply/Appyvb1yAu/Jr-SOC-Engineer?source=LinkedIn"
        print(f"1. Navigating to: {job_url}")
        driver.get(job_url)
        time.sleep(3)
        
        print("2. Checking for CAPTCHA...")
        # CAPTCHA detection
        captcha_present = False
        captcha_selectors = [
            'iframe[src*="recaptcha"]',
            '.g-recaptcha',
            '[class*="captcha"]'
        ]
        
        for selector in captcha_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].is_displayed():
                    print(f"🚨 CAPTCHA detected: {selector}")
                    captcha_present = True
                    break
            except:
                continue
        
        if captcha_present:
            print("⏳ Please solve the CAPTCHA in the browser window...")
            input("[Press Enter when CAPTCHA is solved] ")
        
        # Enhanced form filling
        print("3. Enhanced form filling...")
        
        # More comprehensive field mappings
        field_mappings = {
            # Name fields (more variations)
            'input[name*="firstName"], input[name*="first_name"], input[name*="fname"], input[placeholder*="First"], input[id*="first"]': personal_info.get('legal_first_name'),
            'input[name*="lastName"], input[name*="last_name"], input[name*="lname"], input[placeholder*="Last"], input[id*="last"]': personal_info.get('legal_last_name'),
            'input[name*="fullName"], input[name*="full_name"], input[name*="name"], input[placeholder*="Full"], input[placeholder*="Name"]': f"{personal_info.get('legal_first_name', '')} {personal_info.get('legal_last_name', '')}".strip(),
            
            # Contact fields
            'input[type="email"], input[name*="email"], input[placeholder*="Email"], input[id*="email"]': personal_info.get('email'),
            'input[type="tel"], input[name*="phone"], input[placeholder*="Phone"], input[id*="phone"]': personal_info.get('phone'),
            
            # Address fields
            'input[name*="address"], input[placeholder*="Address"], input[id*="address"]': personal_info.get('address_line_1'),
            'input[name*="city"], input[placeholder*="City"], input[id*="city"]': personal_info.get('city'),
            'input[name*="state"], input[placeholder*="State"], input[id*="state"]': personal_info.get('state_province'),
            'input[name*="zip"], input[name*="postal"], input[placeholder*="Zip"], input[id*="zip"]': personal_info.get('zip_postal_code'),
        }
        
        filled_count = 0
        
        # Fill text fields
        for selector, value in field_mappings.items():
            if value:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element.clear()
                            element.send_keys(str(value))
                            print(f"   ✅ Filled: {element.get_attribute('name') or element.get_attribute('placeholder') or 'field'} = {value}")
                            filled_count += 1
                            time.sleep(0.5)
                            break
                except Exception as e:
                    print(f"   ⚠️ Error with field: {e}")
        
        # Handle file upload
        resume_path = profile.get('document_paths', {}).get('resume')
        if resume_path and os.path.exists(resume_path):
            try:
                file_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="file"]')
                for file_input in file_inputs:
                    if file_input.is_displayed():
                        file_input.send_keys(resume_path)
                        print(f"   ✅ Uploaded resume: {os.path.basename(resume_path)}")
                        filled_count += 1
                        break
            except Exception as e:
                print(f"   ⚠️ Resume upload error: {e}")
        
        # Enhanced yes/no question handling
        yes_no_mappings = {
            'authorization': eligibility.get('are_you_legally_authorized_to_work', 'Yes'),
            'authorized': eligibility.get('are_you_legally_authorized_to_work', 'Yes'), 
            'sponsorship': eligibility.get('will_you_require_sponsorship', 'No'),
            'sponsor': eligibility.get('will_you_require_sponsorship', 'No'),
            'visa': eligibility.get('will_you_require_sponsorship', 'No'),
        }
        
        # Find and handle choice elements
        choice_elements = driver.find_elements(By.CSS_SELECTOR, 'input[type="radio"], input[type="checkbox"]')
        
        for element in choice_elements:
            try:
                # Get broader context
                for ancestor_level in range(1, 4):
                    try:
                        parent = element.find_element(By.XPATH, f'./ancestor::*[{ancestor_level}]')
                        question_text = parent.text.lower()
                        
                        for keyword, answer in yes_no_mappings.items():
                            if keyword in question_text:
                                value = element.get_attribute('value') or ''
                                label_text = ''
                                
                                # Try to find associated label
                                try:
                                    label = element.find_element(By.XPATH, './following-sibling::label[1] | ./preceding-sibling::label[1]')
                                    label_text = label.text.lower()
                                except:
                                    pass
                                
                                # Check if this element matches our answer
                                should_select = False
                                if answer.lower() == 'yes':
                                    should_select = ('yes' in value.lower() or 'yes' in label_text or 'true' in value.lower())
                                elif answer.lower() == 'no':
                                    should_select = ('no' in value.lower() or 'no' in label_text or 'false' in value.lower())
                                
                                if should_select and not element.is_selected():
                                    driver.execute_script("arguments[0].click();", element)
                                    print(f"   ✅ Selected: {keyword} = {answer}")
                                    filled_count += 1
                                    time.sleep(0.5)
                                break
                        break
                    except:
                        continue
            except:
                continue
        
        print(f"\\n4. Enhanced form filling completed: {filled_count} fields filled")
        
        # Enhanced submit button detection
        submit_button = enhanced_submit_detection(driver)
        
        if submit_button:
            print(f"\\n6. Submit button found: '{submit_button.text}'")
            print("   ⚠️ Ready to submit REAL job application!")
            
            submit_choice = input("   Submit application now? (y/n): ").lower().strip()
            
            if submit_choice in ['y', 'yes']:
                try:
                    # Scroll to submit button
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_button)
                    time.sleep(2)
                    
                    # Try multiple click methods
                    try:
                        submit_button.click()
                        print("   📤 Standard click successful")
                    except:
                        try:
                            driver.execute_script("arguments[0].click();", submit_button)
                            print("   📤 JavaScript click successful")
                        except:
                            print("   ❌ Both click methods failed")
                            return False
                    
                    print("   ⏳ Waiting for submission...")
                    time.sleep(5)
                    
                    # Enhanced success detection
                    current_url = driver.current_url
                    page_source = driver.page_source.lower()
                    
                    success_indicators = [
                        'thank you', 'thanks', 'submitted', 'received', 'success',
                        'application received', 'thank you for applying', 'confirmation'
                    ]
                    
                    url_changed = current_url != job_url
                    success_text_found = any(indicator in page_source for indicator in success_indicators)
                    
                    if url_changed and ('thank' in current_url or 'success' in current_url):
                        print("   🎉 SUCCESS: URL changed to success page!")
                        return True
                    elif success_text_found:
                        print("   🎉 SUCCESS: Success confirmation found on page!")
                        return True
                    elif url_changed:
                        print("   ✅ LIKELY SUCCESS: URL changed after submission")
                        print(f"      New URL: {current_url}")
                        return True
                    else:
                        print("   ⚠️ Submission status unclear")
                        print("   Check the browser window manually")
                        return False
                        
                except Exception as e:
                    print(f"   ❌ Submission error: {e}")
                    return False
            else:
                print("   👍 Submission cancelled by user")
                return False
        else:
            print("\\n❌ Could not find submit button")
            print("   Please submit manually in the browser window")
            print("   Look for Submit, Apply, Continue, or Next button")
            
            manual_submit = input("   Continue manually? (y/n): ").lower().strip()
            if manual_submit in ['y', 'yes']:
                print("   ⏳ Please submit manually and press Enter when done...")
                input("   [Press Enter after manual submission] ")
                return True
            return False
        
        # Keep browser open for review
        print("\\n7. Keeping browser open for 30 seconds...")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ Application process failed: {e}")
        return False
    
    finally:
        try:
            driver.quit()
            print("✅ Browser closed")
        except:
            pass

if __name__ == "__main__":
    print("🎯 Enhanced IntelliApply Job Application")
    print("=" * 60)
    print("Improvements:")
    print("✅ Enhanced submit button detection")
    print("✅ Better form field mapping")
    print("✅ Comprehensive choice handling")
    print("✅ Multiple click methods")
    print("✅ Manual submission fallback")
    print("")
    
    proceed = input("❓ Proceed with enhanced application? (y/n): ").lower().strip()
    
    if proceed in ['y', 'yes']:
        success = apply_to_job_enhanced()
        
        if success:
            print("\\n🎉 Job application completed!")
            print("Check your email for confirmation from Aqueity.")
            print("Check the job website to see if you can apply again (it should block repeat applications)")
        else:
            print("\\n⚠️ Application incomplete - may need manual intervention")
    else:
        print("👍 Application cancelled")