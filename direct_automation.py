# direct_automation.py - Direct browser automation for job application
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
    # Visible browser for CAPTCHA solving
    
    try:
        service = ChromeService()  # Use system ChromeDriver
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.maximize_window()
        return driver
    except Exception as e:
        print(f"❌ Browser setup failed: {e}")
        return None

def apply_to_job():
    """Apply to the Aqueity job directly"""
    
    print("🎯 Direct Job Application Automation")
    print("=" * 50)
    
    # Load profile
    profile = load_profile()
    if not profile:
        return False
    
    personal_info = profile.get('personal_info', {})
    eligibility = profile.get('eligibility', {})
    experience = profile.get('experience', {})
    
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
        # Check for CAPTCHA
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
            print("Press Enter after solving the CAPTCHA to continue form filling.")
            input("[Press Enter when CAPTCHA is solved] ")
        
        print("3. Filling form fields...")
        
        # Form field mappings
        field_mappings = {
            # Name fields
            'input[name*="firstName"], input[name*="first_name"], input[placeholder*="First"]': personal_info.get('legal_first_name'),
            'input[name*="lastName"], input[name*="last_name"], input[placeholder*="Last"]': personal_info.get('legal_last_name'),
            'input[name*="fullName"], input[name*="full_name"], input[placeholder*="Full"]': f"{personal_info.get('legal_first_name', '')} {personal_info.get('legal_last_name', '')}".strip(),
            
            # Contact fields
            'input[type="email"], input[name*="email"], input[placeholder*="Email"]': personal_info.get('email'),
            'input[type="tel"], input[name*="phone"], input[placeholder*="Phone"]': personal_info.get('phone'),
            
            # Address fields
            'input[name*="address"], input[placeholder*="Address"]': personal_info.get('address_line_1'),
            'input[name*="city"], input[placeholder*="City"]': personal_info.get('city'),
            'input[name*="state"], input[placeholder*="State"]': personal_info.get('state_province'),
            'input[name*="zip"], input[name*="postal"], input[placeholder*="Zip"]': personal_info.get('zip_postal_code'),
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
                            print(f"   ✅ Filled: {selector[:30]}... = {value}")
                            filled_count += 1
                            time.sleep(0.5)
                            break
                except Exception as e:
                    print(f"   ⚠️ Error with {selector}: {e}")
        
        # Handle file upload (resume)
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
        
        # Handle common yes/no questions
        yes_no_mappings = {
            'work authorization': eligibility.get('are_you_legally_authorized_to_work', 'Yes'),
            'sponsorship': eligibility.get('will_you_require_sponsorship', 'No'),
            'visa': eligibility.get('will_you_require_sponsorship', 'No'),
        }
        
        # Find radio buttons and checkboxes
        choice_elements = driver.find_elements(By.CSS_SELECTOR, 'input[type="radio"], input[type="checkbox"]')
        
        for element in choice_elements:
            try:
                # Get the question context
                parent = element.find_element(By.XPATH, './ancestor::div[contains(@class, "form") or contains(@class, "field") or contains(@class, "question")][1]')
                question_text = parent.text.lower()
                
                for keyword, answer in yes_no_mappings.items():
                    if keyword in question_text:
                        # Find the right option
                        value = element.get_attribute('value')
                        if (answer.lower() == 'yes' and value and 'yes' in value.lower()) or \
                           (answer.lower() == 'no' and value and 'no' in value.lower()):
                            if not element.is_selected():
                                driver.execute_script("arguments[0].click();", element)
                                print(f"   ✅ Selected: {keyword} = {answer}")
                                filled_count += 1
                                time.sleep(0.5)
                        break
            except:
                continue
        
        print(f"\n4. Form filling completed: {filled_count} fields filled")
        
        # Look for submit button
        print("5. Looking for submit button...")
        submit_button = None
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:contains('Submit')",
            "button:contains('Apply')"
        ]
        
        for selector in submit_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        text = element.text.lower()
                        if any(word in text for word in ['submit', 'apply', 'send']):
                            submit_button = element
                            print(f"   ✅ Found: {element.text}")
                            break
                if submit_button:
                    break
            except:
                continue
        
        if submit_button:
            print("\n6. Ready to submit!")
            print("   ⚠️ This will submit a REAL job application to Aqueity!")
            
            submit_choice = input("   Submit application now? (y/n): ").lower().strip()
            
            if submit_choice in ['y', 'yes']:
                try:
                    # Scroll to and click submit
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_button)
                    time.sleep(2)
                    submit_button.click()
                    
                    print("   📤 Application submitted!")
                    time.sleep(5)
                    
                    # Check for success
                    page_source = driver.page_source.lower()
                    success_keywords = ['thank you', 'thanks', 'submitted', 'received', 'success']
                    
                    if any(keyword in page_source for keyword in success_keywords):
                        print("   🎉 SUCCESS: Application appears to have been submitted!")
                        return True
                    else:
                        print("   ⚠️ Submission status unclear - check manually")
                        return False
                        
                except Exception as e:
                    print(f"   ❌ Submission error: {e}")
                    return False
            else:
                print("   👍 Submission cancelled by user")
                return False
        else:
            print("   ❌ No submit button found")
            return False
        
        # Keep browser open for review
        print("\n7. Keeping browser open for 30 seconds for review...")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ Application process failed: {e}")
        return False
    
    finally:
        driver.quit()
        print("✅ Browser closed")

if __name__ == "__main__":
    print("🎯 IntelliApply Direct Job Application")
    print("=" * 60)
    print("This will:")
    print("1. Open visible browser")
    print("2. Navigate to Aqueity job") 
    print("3. Detect and handle CAPTCHA")
    print("4. Fill form with your profile data")
    print("5. Submit real application (with your permission)")
    print("")
    print("⚠️ This bypasses the bot system completely")
    print("⚠️ This submits a REAL job application")
    print("")
    
    proceed = input("❓ Proceed with direct application? (y/n): ").lower().strip()
    
    if proceed in ['y', 'yes']:
        success = apply_to_job()
        
        if success:
            print("\n🎉 Job application submitted successfully!")
            print("Check your email for confirmation from Aqueity.")
        else:
            print("\n⚠️ Application submission incomplete")
    else:
        print("👍 Application cancelled")
