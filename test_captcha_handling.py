# test_captcha_handling.py - Test CAPTCHA detection and handling
import requests
import time

API_BASE = "http://localhost:8003"

def test_captcha_workflow():
    """Test the complete CAPTCHA workflow"""
    
    print("🧪 Testing CAPTCHA Detection and Handling")
    print("=" * 50)
    
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
        profiles = profiles_response.json()
        profile_id = profiles[0]['id']
        
        # Stop any existing bot
        requests.post(f"{API_BASE}/api/bot/stop", headers=headers, timeout=10)
        time.sleep(2)
        
        # Start bot with visible browser for CAPTCHA solving
        print("1. Starting bot with VISIBLE browser...")
        bot_config = {
            "headless": False,  # VISIBLE for CAPTCHA solving
            "max_concurrent": 1
        }
        
        start_response = requests.post(f"{API_BASE}/api/bot/start", json=bot_config, headers=headers, timeout=15)
        if start_response.status_code != 200:
            print(f"❌ Failed to start bot: {start_response.text}")
            return
        
        print("✅ Bot started with visible browser")
        time.sleep(3)
        
        # Process Aqueity job (we know it has CAPTCHA)
        print("2. Processing job with CAPTCHA...")
        print("   🖥️ Browser window should open")
        print("   📝 Form should start filling")
        print("   🚨 When CAPTCHA appears, solve it manually!")
        
        test_request = {
            "profile_id": profile_id,
            "job_url": "https://aqueity.applytojob.com/apply/Appyvb1yAu/Jr-SOC-Engineer?source=LinkedIn"
        }
        
        print("\n⏰ Processing (up to 5 minutes for CAPTCHA solving)...")
        
        response = requests.post(
            f"{API_BASE}/api/bot/process-single",
            json=test_request,
            headers=headers,
            timeout=300  # 5 minutes for CAPTCHA
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n📊 Result: {result}")
            
            # Check if application was actually created
            apps_response = requests.get(f"{API_BASE}/api/applications", headers=headers)
            if apps_response.status_code == 200:
                applications = apps_response.json()
                print(f"\n📋 Applications in database: {len(applications)}")
                
                if applications:
                    latest = applications[0]
                    print(f"   Status: {latest['status']}")
                    print(f"   URL: {latest['job_url']}")
                    if latest.get('error_message'):
                        print(f"   Error: {latest['error_message']}")
            
            # Check user application count
            user_response = requests.get(f"{API_BASE}/api/auth/me", headers=headers)
            if user_response.status_code == 200:
                user = user_response.json()
                print(f"\n👤 Applications used: {user['applications_used']}/{user['applications_limit']}")
                
                if user['applications_used'] > 0:
                    print("🎉 SUCCESS: Application was actually submitted!")
                else:
                    print("⚠️ Application count unchanged - likely blocked by CAPTCHA")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_captcha_workflow()
