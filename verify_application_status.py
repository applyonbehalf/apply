# verify_application_status.py - Check what actually happened
import requests
import json

API_BASE = "http://localhost:8003"

def check_application_status():
    """Check the actual application status in our database"""
    
    print("🔍 Checking Application Status")
    print("=" * 40)
    
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
        
        # Get user info
        print("1. Checking user info...")
        user_response = requests.get(f"{API_BASE}/api/auth/me", headers=headers, timeout=10)
        if user_response.status_code == 200:
            user = user_response.json()
            print(f"✅ User: {user['name']}")
            print(f"   Applications Used: {user['applications_used']}/{user['applications_limit']}")
        
        # Get applications
        print("\n2. Checking job applications...")
        apps_response = requests.get(f"{API_BASE}/api/applications", headers=headers, timeout=10)
        if apps_response.status_code == 200:
            applications = apps_response.json()
            print(f"✅ Found {len(applications)} applications:")
            
            for i, app in enumerate(applications, 1):
                print(f"\n   {i}. Application ID: {app['id'][:8]}...")
                print(f"      Job URL: {app['job_url']}")
                print(f"      Status: {app['status']}")
                print(f"      Company: {app.get('company_name', 'Unknown')}")
                print(f"      Title: {app.get('job_title', 'Unknown')}")
                print(f"      Created: {app['created_at']}")
                if app.get('error_message'):
                    print(f"      Error: {app['error_message']}")
                if app.get('submitted_at'):
                    print(f"      Submitted: {app['submitted_at']}")
        else:
            print(f"❌ Failed to get applications: {apps_response.status_code}")
        
        # Get user stats
        print("\n3. Checking user statistics...")
        stats_response = requests.get(f"{API_BASE}/api/users/stats", headers=headers, timeout=10)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"✅ Application Statistics:")
            print(f"   Total: {stats['total_applications']}")
            print(f"   Completed: {stats['completed']}")
            print(f"   Failed: {stats['failed']}")
            print(f"   Processing: {stats['processing']}")
            print(f"   Queued: {stats['queued']}")
            print(f"   CAPTCHA Required: {stats['captcha_required']}")
            print(f"   Success Rate: {stats['success_rate']:.1f}%")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_captcha_detection():
    """Test CAPTCHA detection with visible browser"""
    
    print("\n🧪 Testing CAPTCHA Detection")
    print("=" * 40)
    
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
        
        # Get profile ID
        profiles_response = requests.get(f"{API_BASE}/api/profiles", headers=headers, timeout=10)
        if profiles_response.status_code != 200:
            print("❌ Failed to get profiles")
            return
        
        profiles = profiles_response.json()
        if not profiles:
            print("❌ No profiles found")
            return
        
        profile_id = profiles[0]['id']
        
        print(f"🎯 Testing with visible browser (you'll see the CAPTCHA)")
        print(f"   Profile ID: {profile_id}")
        print(f"   This will open a browser window - DO NOT close it!")
        print(f"   You should see the CAPTCHA that needs to be solved")
        
        # Start bot with visible browser
        bot_config = {"headless": False, "max_concurrent": 1}  # headless=False!
        start_response = requests.post(f"{API_BASE}/api/bot/start", json=bot_config, headers=headers, timeout=15)
        
        if start_response.status_code == 200:
            print("✅ Bot started with visible browser")
            
            # Process the same URL with visible browser
            test_request = {
                "profile_id": profile_id,
                "job_url": "https://aqueity.applytojob.com/apply/Appyvb1yAu/Jr-SOC-Engineer?source=LinkedIn"
            }
            
            print("\n🔍 Processing application with visible browser...")
            print("   Watch the browser - you should see the CAPTCHA!")
            
            response = requests.post(
                f"{API_BASE}/api/bot/process-single",
                json=test_request,
                headers=headers,
                timeout=300  # 5 minute timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Response: {result}")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Response: {response.text}")
        else:
            print(f"❌ Failed to start bot: {start_response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🔍 IntelliApply Application Verification")
    print("=" * 60)
    
    # Check what's in the database
    check_application_status()
    
    print("\n" + "=" * 60)
    print("📋 CAPTCHA Detection Analysis:")
    print("   If applications_used is still 0 and no 'completed' applications,")
    print("   then the CAPTCHA blocked the submission.")
    print("")
    print("   To test CAPTCHA detection with visible browser:")
    
    test_captcha = input("❓ Test CAPTCHA detection with visible browser? (y/n): ").lower().strip()
    if test_captcha in ['y', 'yes']:
        test_captcha_detection()

if __name__ == "__main__":
    main()