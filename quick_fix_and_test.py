# quick_fix_and_test.py - Fixed version with proper paths and selenium check
import requests
import json
import time
import threading
import subprocess
import os
import sys

API_BASE = "http://localhost:8003"  # Changed port to avoid conflict
JOB_URL = "https://aqueity.applytojob.com/apply/Appyvb1yAu/Jr-SOC-Engineer?source=LinkedIn"

# Your user data
USER_DATA = {
    "email": "shubhmmane56@gmail.com",  # Fixed email
    "name": "Shubham Mane",
    "password": "secure_password_123"
}

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check if backend exists
    if not os.path.exists('backend'):
        print("❌ Error: 'backend' directory not found.")
        return False
    
    # Check if profile.json exists
    absolute_profile_path = "/Users/shubhammane/Desktop/IntelliApply_Bot/data/profile.json"
    profile_paths = [absolute_profile_path, 'data/profile.json', 'profile.json']
    profile_found = False
    
    for path in profile_paths:
        if os.path.exists(path):
            print(f"✅ Found profile.json at: {path}")
            profile_found = True
            break
    
    if not profile_found:
        print("❌ Error: profile.json not found")
        print("Searched in:", profile_paths)
        return False
    
    # Check if required packages are installed
    try:
        import selenium
        print("✅ Selenium is available")
    except ImportError:
        print("❌ Selenium not installed. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium", "webdriver-manager"])
            print("✅ Selenium installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install selenium")
            return False
    
    # Check for Google AI
    try:
        import google.generativeai
        print("✅ Google AI is available")
    except ImportError:
        print("❌ Google AI not installed. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
            print("✅ Google AI installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Google AI")
            return False
    
    return True

def start_server():
    """Start the FastAPI server"""
    os.chdir('backend')
    subprocess.run(['python', '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8003'])

def load_profile_data():
    """Load profile data from multiple possible locations"""
    # Use absolute path first
    absolute_path = "/Users/shubhammane/Desktop/IntelliApply_Bot/data/profile.json"
    possible_paths = [
        absolute_path,
        'data/profile.json', 
        'profile.json', 
        './data/profile.json',
        './profile.json',
        os.path.expanduser('~/Desktop/IntelliApply_Bot/data/profile.json')
    ]
    
    print(f"🔍 Looking for profile.json in:")
    for path in possible_paths:
        print(f"   - {path}")
        try:
            with open(path, 'r') as f:
                print(f"✅ Loaded profile data from: {path}")
                return json.load(f)
        except FileNotFoundError:
            print(f"   ❌ Not found: {path}")
            continue
        except Exception as e:
            print(f"   ❌ Error reading {path}: {e}")
            continue
    
    print("❌ Could not find profile.json in any location")
    return None

def setup_user_and_profile():
    """Complete user setup process"""
    print("🔐 Setting up user account and profile...")
    
    # Load your profile data
    profile_data = load_profile_data()
    if not profile_data:
        return None, None
    
    # Step 1: Try to register user (or login if already exists)
    print("1. Registering/logging in user...")
    try:
        response = requests.post(f"{API_BASE}/api/auth/register", json=USER_DATA, timeout=10)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print("✅ User registered successfully")
        else:
            # Try login instead
            login_data = {"email": USER_DATA["email"], "password": USER_DATA["password"]}
            response = requests.post(f"{API_BASE}/api/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data["access_token"]
                print("✅ User logged in successfully")
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None, None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the backend is running.")
        return None, None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None, None
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Step 2: Create profile with your data
    print("2. Creating profile with your data...")
    try:
        # Clean the profile data to ensure JSON serialization
        def clean_for_json(obj):
            if isinstance(obj, dict):
                return {key: clean_for_json(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            elif hasattr(obj, 'isoformat'):  # datetime objects
                return obj.isoformat()
            else:
                return obj
        
        cleaned_profile_data = clean_for_json(profile_data)
        
        profile_request = {
            "profile_name": f"Cybersecurity Professional - {int(time.time())}",  # Unique name
            "profile_data": cleaned_profile_data,
            "is_default": False  # Always false to avoid constraint issues
        }
        
        response = requests.post(f"{API_BASE}/api/profiles", json=profile_request, headers=headers, timeout=15)
        if response.status_code == 200:
            profile = response.json()
            profile_id = profile['id']
            print(f"✅ Profile created: {profile['profile_name']}")
            return access_token, profile_id
        else:
            print(f"❌ Profile creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Try to get existing profile instead
            print("🔄 Trying to use existing profile...")
            profiles_response = requests.get(f"{API_BASE}/api/profiles", headers=headers, timeout=10)
            if profiles_response.status_code == 200:
                profiles = profiles_response.json()
                if profiles:
                    profile_id = profiles[0]['id']
                    print(f"✅ Using existing profile: {profiles[0]['profile_name']}")
                    return access_token, profile_id
            
            return access_token, None
            
    except Exception as e:
        print(f"❌ Profile creation error: {e}")
        return access_token, None

def test_single_application_simple(access_token, profile_id):
    """Test single application using the simple method"""
    print("🎯 Testing single application processing...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # First, start the bot if it's not running
    print("1. Checking and starting bot...")
    try:
        # Check bot status
        response = requests.get(f"{API_BASE}/api/bot/status", headers=headers, timeout=10)
        if response.status_code == 200:
            status = response.json()['data']
            if not status.get('running', False):
                print("   Bot is not running. Starting bot...")
                
                # Start the bot
                bot_config = {"headless": False, "max_concurrent": 1}
                start_response = requests.post(f"{API_BASE}/api/bot/start", json=bot_config, headers=headers, timeout=15)
                if start_response.status_code == 200:
                    print("   ✅ Bot started successfully")
                else:
                    print(f"   ❌ Failed to start bot: {start_response.status_code}")
                    print(f"   Response: {start_response.text}")
                    return False
            else:
                print("   ✅ Bot is already running")
        else:
            print(f"   ⚠️ Could not check bot status: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️ Bot status check error: {e}")
    
    # Give bot a moment to initialize
    print("2. Waiting for bot to initialize...")
    time.sleep(3)
    
    try:
        # Use the simple single application endpoint
        single_app_request = {
            "profile_id": profile_id,
            "job_url": JOB_URL
        }
        
        print(f"3. Processing job application...")
        print(f"   URL: {JOB_URL}")
        print("   ⚠️  This will open a browser window - do NOT close it!")
        print("   🚨 If you see a CAPTCHA, solve it manually")
        
        response = requests.post(
            f"{API_BASE}/api/bot/process-single", 
            json=single_app_request, 
            headers=headers, 
            timeout=180  # 3 minutes timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("🎉 Application processed successfully!")
                return True
            else:
                print(f"❌ Application failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
            # If bot not running, try alternative approach
            if "Bot is not running" in response.text:
                print("\n🔄 Bot not running, trying alternative approach...")
                return test_with_queue_method(access_token, profile_id, headers)
            
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - this is normal for long processing")
        print("The application may still be processing in the background")
        print("Check the browser window to see if it completed")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_with_queue_method(access_token, profile_id, headers):
    """Alternative method using the queue system"""
    print("📋 Trying queue-based processing...")
    
    try:
        # Add to queue
        urls_request = {
            "profile_id": profile_id,
            "urls": [JOB_URL],
            "batch_name": "Test Application - Aqueity SOC"
        }
        
        response = requests.post(f"{API_BASE}/api/bot/add-urls", json=urls_request, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Added to queue: {result['data']['applications_created']} applications")
            
            # Monitor for a short time
            print("   📊 Monitoring queue (30 seconds)...")
            for i in range(6):  # 6 * 5 = 30 seconds
                time.sleep(5)
                queue_response = requests.get(f"{API_BASE}/api/bot/my-queue", headers=headers, timeout=10)
                if queue_response.status_code == 200:
                    queue_info = queue_response.json()['data']
                    print(f"   Queue: {queue_info['processing']} processing, {queue_info['completed']} completed")
                    
                    if queue_info['completed'] > 0:
                        print("   🎉 Application completed via queue!")
                        return True
                    elif queue_info['failed'] > 0:
                        print("   ❌ Application failed in queue")
                        return False
            
            print("   ⏰ Queue monitoring timeout - check manually")
            return False
        else:
            print(f"   ❌ Failed to add to queue: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Queue method error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 IntelliApply Quick Fix and Test")
    print("=" * 50)
    
    # Check requirements first
    if not check_requirements():
        print("❌ Requirements check failed. Please fix the issues above.")
        return
    
    print("✅ All requirements met!")
    
    # Start server
    print("\n🌐 Starting backend server...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(8)
    
    # Test server connectivity
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    try:
        # Setup user and profile
        access_token, profile_id = setup_user_and_profile()
        
        if not access_token or not profile_id:
            print("❌ Failed to set up user and profile")
            return
        
        print(f"\n✅ Setup complete!")
        print(f"   🔑 Token: {access_token[:30]}...")
        print(f"   👤 Profile ID: {profile_id}")
        
        # Ask user if they want to proceed
        print(f"\n📋 Ready to apply to:")
        print(f"   {JOB_URL}")
        print("\n⚠️  This will:")
        print("   1. Open a browser window")
        print("   2. Navigate to the job page")
        print("   3. Fill out the application form automatically")
        print("   4. Submit the application")
        print("\n🚨 IMPORTANT: If you see a CAPTCHA, solve it manually!")
        
        proceed = input("\n❓ Proceed with application? (y/n): ").lower().strip()
        
        if proceed == 'y' or proceed == 'yes':
            success = test_single_application_simple(access_token, profile_id)
            
            if success:
                print("\n🎉 SUCCESS! Check the job website to confirm your application.")
            else:
                print("\n⚠️ Application may have encountered issues.")
                print("Check the browser window for details.")
        else:
            print("👍 Test cancelled. Your account and profile are set up and ready!")
        
        print(f"\n📊 API Documentation: http://localhost:8003/docs")
        print("Press Ctrl+C to stop")
        
        # Keep server running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()