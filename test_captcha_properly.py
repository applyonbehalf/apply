# test_captcha_properly.py - Proper CAPTCHA testing with visible browser
import requests
import time
import subprocess
import os

API_BASE = "http://localhost:8003"

def stop_existing_bot():
    """Stop any existing bot"""
    login_data = {
        "email": "shubhmmane56@gmail.com",
        "password": "secure_password_123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Try to stop bot
            requests.post(f"{API_BASE}/api/bot/stop", headers=headers, timeout=10)
            print("🛑 Stopped existing bot")
            time.sleep(2)
    except:
        pass

def test_with_visible_browser():
    """Test CAPTCHA detection with visible browser"""
    
    print("🔍 Testing CAPTCHA Detection with Visible Browser")
    print("=" * 60)
    
    # Stop any existing bot first
    stop_existing_bot()
    
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
        if profiles_response.status_code != 200:
            print("❌ Failed to get profiles")
            return
        
        profiles = profiles_response.json()
        if not profiles:
            print("❌ No profiles found")
            return
        
        profile_id = profiles[0]['id']
        print(f"✅ Using profile: {profile_id}")
        
        # Start bot with visible browser
        print("\n1. Starting bot with visible browser...")
        bot_config = {
            "headless": False,  # THIS IS KEY - you'll see the browser!
            "max_concurrent": 1
        }
        
        start_response = requests.post(f"{API_BASE}/api/bot/start", json=bot_config, headers=headers, timeout=15)
        
        if start_response.status_code != 200:
            print(f"❌ Failed to start bot: {start_response.status_code}")
            print(f"Response: {start_response.text}")
            return
        
        print("✅ Bot started with visible browser")
        
        # Wait for bot to initialize
        print("2. Waiting for bot to initialize...")
        time.sleep(3)
        
        # Process the Aqueity job with visible browser
        print("3. Processing Aqueity job application...")
        print("   🚨 WATCH THE BROWSER WINDOW - you should see:")
        print("      - Job page loading")
        print("      - Form being filled")
        print("      - CAPTCHA appearing")
        print("      - Bot pausing at CAPTCHA")
        
        test_request = {
            "profile_id": profile_id,
            "job_url": "https://aqueity.applytojob.com/apply/Appyvb1yAu/Jr-SOC-Engineer?source=LinkedIn"
        }
        
        print("\n🎯 Starting application process...")
        print("   ⚠️  Browser window will open - don't close it!")
        print("   📱 When CAPTCHA appears, solve it manually")
        
        response = requests.post(
            f"{API_BASE}/api/bot/process-single",
            json=test_request,
            headers=headers,
            timeout=300  # 5 minutes to handle CAPTCHA
        )
        
        print(f"\n📊 Process completed!")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Result: {result}")
            
            if result.get('success'):
                print("🎉 Application processed successfully!")
                print("   Check the browser to see final status")
            else:
                print(f"❌ Application failed: {result.get('message', 'Unknown error')}")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
        
        # Check updated status
        print("\n4. Checking updated application status...")
        time.sleep(2)
        
        user_response = requests.get(f"{API_BASE}/api/auth/me", headers=headers, timeout=10)
        if user_response.status_code == 200:
            user = user_response.json()
            print(f"   Applications Used: {user['applications_used']}/{user['applications_limit']}")
        
        apps_response = requests.get(f"{API_BASE}/api/applications", headers=headers, timeout=10)
        if apps_response.status_code == 200:
            applications = apps_response.json()
            print(f"   Total Applications: {len(applications)}")
            
            if applications:
                latest_app = applications[0]
                print(f"   Latest Status: {latest_app['status']}")
                if latest_app.get('error_message'):
                    print(f"   Error: {latest_app['error_message']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("🧪 IntelliApply CAPTCHA Detection Test")
    print("=" * 60)
    print("This will:")
    print("1. Stop any existing bot")
    print("2. Start bot with VISIBLE browser")
    print("3. Navigate to Aqueity job")
    print("4. Show you the CAPTCHA that needs solving")
    print("5. Test our CAPTCHA detection")
    print("")
    
    proceed = input("❓ Proceed with visible browser test? (y/n): ").lower().strip()
    
    if proceed in ['y', 'yes']:
        test_with_visible_browser()
        
        print("\n📋 Expected Outcomes:")
        print("   ✅ Browser window opens and you can see it")
        print("   ✅ Job form gets filled automatically")
        print("   ✅ CAPTCHA appears and bot should detect it")
        print("   ✅ You can solve CAPTCHA manually")
        print("   ✅ Application submits after CAPTCHA solved")
    else:
        print("👍 Test cancelled")

if __name__ == "__main__":
    main()