# test_fixed_browser.py - Test with working ChromeDriver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

def test_visible_browser():
    """Test with visible browser using fixed ChromeDriver"""
    
    print("🧪 Testing Fixed ChromeDriver with Visible Browser")
    print("=" * 50)
    
    # Chrome options for visible browser
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # NO --headless flag = visible browser!
    
    try:
        # Use the working ChromeDriver path
        service = Service()
        
        print("1. Starting visible Chrome browser...")
        driver = webdriver.Chrome(service=service, options=options)
        
        # Anti-detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.maximize_window()
        
        print("✅ Browser started - you should see Chrome window!")
        
        # Navigate to Aqueity job
        job_url = "https://aqueity.applytojob.com/apply/Appyvb1yAu/Jr-SOC-Engineer?source=LinkedIn"
        print(f"2. Navigating to: {job_url}")
        driver.get(job_url)
        
        print("✅ Page loaded - you should see the job application!")
        print("   🔍 Look for the reCAPTCHA checkbox")
        
        # Wait for user to see
        print("\n⏳ Keeping browser open for 30 seconds...")
        print("   👀 Observe the page and look for CAPTCHA")
        time.sleep(30)
        
        # Check for CAPTCHA
        print("\n3. Checking for CAPTCHA...")
        captcha_selectors = [
            'iframe[src*="recaptcha"]',
            '.g-recaptcha', 
            '#recaptcha',
            '.captcha',
            '[class*="captcha"]'
        ]
        
        captcha_found = False
        for selector in captcha_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"   ✅ CAPTCHA found: {selector}")
                    captcha_found = True
            except:
                pass
        
        if not captcha_found:
            print("   ❌ No CAPTCHA detected with selectors")
            
            # Check page source
            if 'recaptcha' in driver.page_source.lower():
                print("   ⚠️ But 'recaptcha' found in page source")
                captcha_found = True
        
        print("\n4. Closing browser...")
        driver.quit()
        
        return captcha_found
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_visible_browser()
    if success:
        print("\n🎉 SUCCESS: Browser test worked!")
        print("Now we can fix the bot to use this ChromeDriver")
    else:
        print("\n❌ Browser test failed")
