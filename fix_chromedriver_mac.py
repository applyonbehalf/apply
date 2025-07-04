# fix_chromedriver_mac.py - Fix ChromeDriver issues on Mac
import os
import subprocess
import platform
import shutil

def check_system():
    """Check Mac system architecture"""
    print("🔍 Checking Mac System")
    print("=" * 30)
    
    system = platform.system()
    machine = platform.machine()
    processor = platform.processor()
    
    print(f"System: {system}")
    print(f"Machine: {machine}")
    print(f"Processor: {processor}")
    
    if machine == 'arm64':
        print("✅ Detected: Apple Silicon Mac (M1/M2/M3)")
        return 'arm64'
    else:
        print("✅ Detected: Intel Mac")
        return 'x64'

def clean_webdriver_cache():
    """Clean webdriver-manager cache"""
    print("\n🧹 Cleaning WebDriver Cache")
    print("=" * 30)
    
    cache_paths = [
        os.path.expanduser('~/.wdm'),
        os.path.expanduser('~/.cache/selenium')
    ]
    
    for path in cache_paths:
        if os.path.exists(path):
            print(f"Removing: {path}")
            try:
                shutil.rmtree(path)
                print(f"✅ Removed: {path}")
            except Exception as e:
                print(f"❌ Error removing {path}: {e}")
        else:
            print(f"Not found: {path}")

def install_chromedriver_manually():
    """Install ChromeDriver manually for Mac"""
    print("\n🔧 Installing ChromeDriver Manually")
    print("=" * 40)
    
    # Check if brew is available
    try:
        subprocess.run(['brew', '--version'], capture_output=True, check=True)
        print("✅ Homebrew detected")
        
        print("Installing ChromeDriver via Homebrew...")
        try:
            # Uninstall any existing version
            subprocess.run(['brew', 'uninstall', 'chromedriver'], capture_output=True)
            # Install fresh
            result = subprocess.run(['brew', 'install', 'chromedriver'], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ ChromeDriver installed via Homebrew")
                return True
            else:
                print(f"❌ Homebrew install failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Homebrew error: {e}")
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Homebrew not found")
    
    # Alternative: Download directly
    print("\n🔗 Alternative: Manual download instructions")
    print("1. Visit: https://chromedriver.chromium.org/downloads")
    print("2. Download ChromeDriver for Mac")
    print("3. Move to /usr/local/bin/chromedriver")
    print("4. Run: chmod +x /usr/local/bin/chromedriver")
    
    return False

def test_fixed_chromedriver():
    """Test the fixed ChromeDriver"""
    print("\n🧪 Testing Fixed ChromeDriver")
    print("=" * 30)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        
        # Try different ChromeDriver paths
        driver_paths = [
            '/usr/local/bin/chromedriver',  # Homebrew default
            '/opt/homebrew/bin/chromedriver',  # M1 Homebrew
            'chromedriver'  # System PATH
        ]
        
        for driver_path in driver_paths:
            try:
                print(f"Trying ChromeDriver at: {driver_path}")
                
                # Test if file exists and is executable
                if driver_path != 'chromedriver':
                    if not os.path.exists(driver_path):
                        print(f"  ❌ File not found: {driver_path}")
                        continue
                    if not os.access(driver_path, os.X_OK):
                        print(f"  ❌ Not executable: {driver_path}")
                        continue
                
                # Create Chrome options
                options = webdriver.ChromeOptions()
                options.add_argument("--headless")  # Test in headless first
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                
                # Create service
                if driver_path == 'chromedriver':
                    service = Service()  # Let it find in PATH
                else:
                    service = Service(executable_path=driver_path)
                
                # Test driver
                driver = webdriver.Chrome(service=service, options=options)
                driver.get("https://www.google.com")
                title = driver.title
                driver.quit()
                
                print(f"  ✅ SUCCESS: ChromeDriver works at {driver_path}")
                print(f"  📄 Test page title: {title}")
                return driver_path
                
            except Exception as e:
                print(f"  ❌ Failed with {driver_path}: {e}")
                continue
        
        print("❌ No working ChromeDriver found")
        return None
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None

def create_fixed_browser_test():
    """Create a test with the fixed ChromeDriver"""
    working_driver_path = test_fixed_chromedriver()
    
    if not working_driver_path:
        print("\n❌ No working ChromeDriver found")
        return False
    
    print(f"\n🔧 Creating Fixed Browser Test")
    print("=" * 30)
    
    # Create a test script with the working driver path
    test_script = f'''# test_fixed_browser.py - Test with working ChromeDriver
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
        {"service = Service()" if working_driver_path == "chromedriver" else f'service = Service(executable_path="{working_driver_path}")'}
        
        print("1. Starting visible Chrome browser...")
        driver = webdriver.Chrome(service=service, options=options)
        
        # Anti-detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}})")
        driver.maximize_window()
        
        print("✅ Browser started - you should see Chrome window!")
        
        # Navigate to Aqueity job
        job_url = "https://aqueity.applytojob.com/apply/Appyvb1yAu/Jr-SOC-Engineer?source=LinkedIn"
        print(f"2. Navigating to: {{job_url}}")
        driver.get(job_url)
        
        print("✅ Page loaded - you should see the job application!")
        print("   🔍 Look for the reCAPTCHA checkbox")
        
        # Wait for user to see
        print("\\n⏳ Keeping browser open for 30 seconds...")
        print("   👀 Observe the page and look for CAPTCHA")
        time.sleep(30)
        
        # Check for CAPTCHA
        print("\\n3. Checking for CAPTCHA...")
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
                    print(f"   ✅ CAPTCHA found: {{selector}}")
                    captcha_found = True
            except:
                pass
        
        if not captcha_found:
            print("   ❌ No CAPTCHA detected with selectors")
            
            # Check page source
            if 'recaptcha' in driver.page_source.lower():
                print("   ⚠️ But 'recaptcha' found in page source")
                captcha_found = True
        
        print("\\n4. Closing browser...")
        driver.quit()
        
        return captcha_found
        
    except Exception as e:
        print(f"❌ Test failed: {{e}}")
        return False

if __name__ == "__main__":
    success = test_visible_browser()
    if success:
        print("\\n🎉 SUCCESS: Browser test worked!")
        print("Now we can fix the bot to use this ChromeDriver")
    else:
        print("\\n❌ Browser test failed")
'''
    
    with open('test_fixed_browser.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Created: test_fixed_browser.py")
    return True

def main():
    """Main function"""
    print("🔧 IntelliApply ChromeDriver Fix for Mac")
    print("=" * 50)
    
    # Check system
    arch = check_system()
    
    # Clean cache
    clean_webdriver_cache()
    
    # Install ChromeDriver
    if install_chromedriver_manually():
        print("✅ ChromeDriver installation completed")
    
    # Test and create fixed version
    if create_fixed_browser_test():
        print("\n🎯 Next steps:")
        print("1. Run: python test_fixed_browser.py")
        print("2. You should see a Chrome browser window open")
        print("3. Look for the CAPTCHA on the Aqueity page")
        print("4. If successful, we'll update the bot to use this ChromeDriver")
    
    print("\n📋 Troubleshooting:")
    print("If test_fixed_browser.py still fails:")
    print("1. Install Chrome browser if not installed")
    print("2. Try: brew install chromedriver")
    print("3. Manually download ChromeDriver for your Mac architecture")

if __name__ == "__main__":
    main()