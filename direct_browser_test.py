# direct_browser_test.py - Direct test with visible browser to see what's happening
import sys
import os
import time
import json

# Add the src directory to path so we can import our modules
sys.path.append('src')
sys.path.append('backend')

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_direct_browser():
    """Test direct browser automation with visible window"""
    
    print("🧪 Direct Browser Test - Visible Mode")
    print("=" * 50)
    
    # Setup Chrome with visible browser
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # DO NOT add --headless - we want to see the browser!
    print("1. Starting visible Chrome browser...")
    
    try:
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), 
            options=options
        )
        
        # Anti-detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.maximize_window()
        
        print("✅ Browser started - you should see Chrome window!")
        
        # Navigate to the job page
        job_url = "https://aqueity.applytojob.com/apply/Appyvb1yAu/Jr-SOC-Engineer?source=LinkedIn"
        print(f"2. Navigating to: {job_url}")
        driver.get(job_url)
        
        print("✅ Page loaded - you should see the job application form")
        print("   🔍 Look for the reCAPTCHA - it should be visible")
        
        # Wait and let user observe
        print("\n⏳ Waiting 10 seconds for you to see the page...")
        time.sleep(10)
        
        # Check for CAPTCHA
        print("3. Checking for CAPTCHA elements...")
        captcha_selectors = [
            'iframe[src*="recaptcha"]',
            '.g-recaptcha',
            '#recaptcha',
            '.captcha',
            '[class*="captcha"]',
            '.cf-challenge-form',
            '[data-sitekey]'
        ]
        
        captcha_found = False
        for selector in captcha_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"   ✅ Found CAPTCHA with selector: {selector}")
                    for i, element in enumerate(elements):
                        print(f"      Element {i+1}: visible={element.is_displayed()}, enabled={element.is_enabled()}")
                    captcha_found = True
            except Exception as e:
                print(f"   ⚠️ Error checking {selector}: {e}")
        
        if not captcha_found:
            print("   ❌ No CAPTCHA elements found with standard selectors")
            
            # Check page source for CAPTCHA-related content
            page_source = driver.page_source.lower()
            captcha_keywords = ['recaptcha', 'captcha', 'human', 'robot', 'verification']
            
            print("   🔍 Checking page source for CAPTCHA keywords...")
            for keyword in captcha_keywords:
                if keyword in page_source:
                    print(f"      ✅ Found '{keyword}' in page source")
                    captcha_found = True
        
        # Look for form elements
        print("\n4. Checking for form elements...")
        try:
            forms = driver.find_elements(By.TAG_NAME, "form")
            print(f"   Found {len(forms)} form(s)")
            
            inputs = driver.find_elements(By.TAG_NAME, "input")
            print(f"   Found {len(inputs)} input fields")
            
            for i, input_elem in enumerate(inputs[:5]):  # Show first 5
                input_type = input_elem.get_attribute('type')
                input_name = input_elem.get_attribute('name')
                input_placeholder = input_elem.get_attribute('placeholder')
                print(f"      Input {i+1}: type={input_type}, name={input_name}, placeholder={input_placeholder}")
        
        except Exception as e:
            print(f"   ❌ Error checking forms: {e}")
        
        # Test form filling
        print("\n5. Testing basic form interaction...")
        try:
            # Look for name field
            name_selectors = [
                'input[name*="name"]',
                'input[placeholder*="name"]',
                'input[placeholder*="Name"]'
            ]
            
            for selector in name_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        element = elements[0]
                        if element.is_displayed() and element.is_enabled():
                            print(f"   ✅ Found name field: {selector}")
                            element.clear()
                            element.send_keys("Shubham Mane")
                            print(f"   ✅ Filled name field with test data")
                            break
                except Exception as e:
                    print(f"   ⚠️ Error with {selector}: {e}")
        
        except Exception as e:
            print(f"   ❌ Form filling error: {e}")
        
        # Keep browser open for manual inspection
        print(f"\n6. Browser will stay open for 60 seconds...")
        print(f"   🔍 Manually inspect the page:")
        print(f"      - Can you see the CAPTCHA?")
        print(f"      - Are there form fields visible?")
        print(f"      - What does the page look like?")
        
        for i in range(60, 0, -10):
            print(f"   ⏰ {i} seconds remaining...")
            time.sleep(10)
        
        print("7. Closing browser...")
        driver.quit()
        print("✅ Browser closed")
        
        return captcha_found
        
    except Exception as e:
        print(f"❌ Browser test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_our_browser_handler():
    """Test our enhanced browser handler"""
    
    print("\n🔧 Testing Our Enhanced Browser Handler")
    print("=" * 50)
    
    try:
        # Import our browser handler
        from bot.enhanced_browser_handler import EnhancedBrowserHandler
        
        print("1. Creating browser handler with headless=False...")
        browser = EnhancedBrowserHandler(user_id="test_user", headless=False)
        
        print("✅ Browser handler created")
        
        # Navigate to job
        job_url = "https://aqueity.applytojob.com/apply/Appyvb1yAu/Jr-SOC-Engineer?source=LinkedIn"
        print(f"2. Navigating to job page...")
        
        # Use asyncio for async method
        import asyncio
        
        async def test_navigation():
            success = await browser.navigate_to_job(job_url, "test_app_id")
            return success
        
        # Run the async function
        success = asyncio.run(test_navigation())
        
        if success:
            print("✅ Navigation successful")
            
            print("3. Browser should be visible now...")
            time.sleep(10)
            
            # Check for CAPTCHA
            async def test_captcha():
                captcha_info = await browser.check_for_captcha()
                return captcha_info
            
            captcha_info = asyncio.run(test_captcha())
            
            if captcha_info:
                print(f"✅ CAPTCHA detected: {captcha_info}")
            else:
                print("❌ No CAPTCHA detected")
            
            print("4. Keeping browser open for inspection...")
            time.sleep(30)
            
        browser.close()
        print("✅ Browser closed")
        
    except ImportError as e:
        print(f"❌ Could not import browser handler: {e}")
    except Exception as e:
        print(f"❌ Browser handler test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("🔍 IntelliApply Browser Debugging")
    print("=" * 60)
    print("This will:")
    print("1. Test direct Selenium browser (visible)")
    print("2. Navigate to Aqueity job page")
    print("3. Show CAPTCHA detection")
    print("4. Test our browser handler")
    print("")
    
    proceed = input("❓ Proceed with browser debugging? (y/n): ").lower().strip()
    
    if proceed in ['y', 'yes']:
        # Test direct browser first
        captcha_found = test_direct_browser()
        
        print(f"\n📊 Direct Browser Test Results:")
        print(f"   CAPTCHA Found: {'✅ Yes' if captcha_found else '❌ No'}")
        
        # Test our browser handler
        test_browser_handler = input("\n❓ Test our enhanced browser handler? (y/n): ").lower().strip()
        if test_browser_handler in ['y', 'yes']:
            test_our_browser_handler()
        
        print(f"\n📋 Summary:")
        print(f"   If you saw the browser and CAPTCHA, the issue is in our bot logic")
        print(f"   If you didn't see anything, there's a display/headless issue")
    else:
        print("👍 Test cancelled")

if __name__ == "__main__":
    main()