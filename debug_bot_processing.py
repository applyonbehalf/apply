# debug_bot_processing.py - Debug exactly what's happening in bot processing
import requests
import time
import json

API_BASE = "http://localhost:8003"

def debug_bot_processing():
    """Debug the bot processing step by step"""
    
    print("🔍 Debugging Bot Processing Step by Step")
    print("=" * 60)
    
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
        
        print(f"✅ Using profile: {profile_id}")
        
        # Check what's in the profile data
        profile_data = profiles[0]['profile_data']
        personal_info = profile_data.get('personal_info', {})
        print(f"📋 Profile data preview:")
        print(f"   Name: {personal_info.get('legal_first_name')} {personal_info.get('legal_last_name')}")
        print(f"   Email: {personal_info.get('email')}")
        print(f"   Phone: {personal_info.get('phone')}")
        
        # Stop any existing bot
        print(f"\n1. Stopping existing bot...")
        stop_response = requests.post(f"{API_BASE}/api/bot/stop", headers=headers, timeout=10)
        time.sleep(2)
        
        # Start bot with debugging
        print(f"2. Starting bot with visible browser...")
        bot_config = {
            "headless": False,
            "max_concurrent": 1
        }
        
        start_response = requests.post(f"{API_BASE}/api/bot/start", json=bot_config, headers=headers, timeout=15)
        
        if start_response.status_code != 200:
            print(f"❌ Bot start failed: {start_response.text}")
            return
        
        print("✅ Bot started")
        
        # Get bot status to see what's actually running
        print(f"3. Checking bot status...")
        status_response = requests.get(f"{API_BASE}/api/bot/status", headers=headers, timeout=10)
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"   Bot running: {status['data']['running']}")
            if 'stats' in status['data']:
                print(f"   Stats: {status['data']['stats']}")
        
        time.sleep(3)
        
        # Instead of using process-single, let's add to queue and monitor
        print(f"4. Adding job to queue...")
        queue_request = {
            "profile_id": profile_id,
            "urls": ["https://aqueity.applytojob.com/apply/Appyvb1yAu/Jr-SOC-Engineer?source=LinkedIn"],
            "batch_name": "Debug Test Batch"
        }
        
        queue_response = requests.post(f"{API_BASE}/api/bot/add-urls", json=queue_request, headers=headers, timeout=10)
        
        if queue_response.status_code == 200:
            result = queue_response.json()
            print(f"✅ Added to queue: {result}")
            
            # Monitor the queue for 2 minutes
            print(f"5. Monitoring queue processing...")
            for i in range(24):  # 24 * 5 seconds = 2 minutes
                time.sleep(5)
                
                # Check queue status
                queue_status = requests.get(f"{API_BASE}/api/bot/my-queue", headers=headers, timeout=10)
                if queue_status.status_code == 200:
                    queue_info = queue_status.json()['data']
                    print(f"   Queue: {queue_info['queued']} queued, {queue_info['processing']} processing, " +
                          f"{queue_info['completed']} completed, {queue_info['failed']} failed, " +
                          f"{queue_info['captcha_required']} captcha")
                    
                    # Check applications
                    apps_response = requests.get(f"{API_BASE}/api/applications", headers=headers, timeout=10)
                    if apps_response.status_code == 200:
                        applications = apps_response.json()
                        if applications:
                            latest = applications[0]
                            print(f"   Latest app status: {latest['status']}")
                            if latest.get('error_message'):
                                print(f"   Error: {latest['error_message']}")
                    
                    # If completed or failed, break
                    if queue_info['completed'] > 0 or queue_info['failed'] > 0:
                        print(f"   Processing completed!")
                        break
                    
                    # If captcha required, inform user
                    if queue_info['captcha_required'] > 0:
                        print(f"   🚨 CAPTCHA required! Check browser window.")
                        
                        # Get CAPTCHA sessions
                        captcha_response = requests.get(f"{API_BASE}/api/bot/captcha/pending", timeout=10)
                        if captcha_response.status_code == 200:
                            captchas = captcha_response.json()['data']
                            for captcha in captchas:
                                print(f"   📝 CAPTCHA session: {captcha['id'][:8]}...")
                                print(f"      Screenshot: {captcha.get('screenshot_url', 'N/A')}")
                
                print(f"   ⏰ Monitoring... ({(i+1)*5} seconds elapsed)")
        else:
            print(f"❌ Failed to add to queue: {queue_response.text}")
            return
        
        # Final status check
        print(f"\n6. Final status check...")
        
        # User applications count
        user_response = requests.get(f"{API_BASE}/api/auth/me", headers=headers, timeout=10)
        if user_response.status_code == 200:
            user = user_response.json()
            print(f"   Applications used: {user['applications_used']}/{user['applications_limit']}")
        
        # Applications in database
        apps_response = requests.get(f"{API_BASE}/api/applications", headers=headers, timeout=10)
        if apps_response.status_code == 200:
            applications = apps_response.json()
            print(f"   Applications in DB: {len(applications)}")
            
            if applications:
                for app in applications:
                    print(f"      {app['status']}: {app['job_url']}")
                    if app.get('error_message'):
                        print(f"         Error: {app['error_message']}")
        
        # User stats
        stats_response = requests.get(f"{API_BASE}/api/users/stats", headers=headers, timeout=10)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"   User stats: {stats}")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

def check_browser_handler_file():
    """Check if the browser handler file was actually updated"""
    
    print(f"\n🔍 Checking Browser Handler File")
    print("=" * 40)
    
    handler_file = "backend/bot/enhanced_browser_handler.py"
    
    try:
        with open(handler_file, 'r') as f:
            content = f.read()
        
        # Check for our updated signatures
        if 'working ChromeDriver' in content:
            print("✅ Browser handler has been updated")
        else:
            print("❌ Browser handler NOT updated")
            
        if 'Enhanced CAPTCHA detection' in content:
            print("✅ CAPTCHA detection code present")
        else:
            print("❌ CAPTCHA detection code missing")
            
        if 'ChromeDriver loaded from' in content:
            print("✅ ChromeDriver path detection present")
        else:
            print("❌ ChromeDriver path detection missing")
            
    except FileNotFoundError:
        print(f"❌ File not found: {handler_file}")

def main():
    """Main function"""
    print("🔍 IntelliApply Bot Processing Debugger")
    print("=" * 60)
    
    # Check if our updates were applied
    check_browser_handler_file()
    
    print("\nThis will:")
    print("1. Add job to queue (instead of direct processing)")
    print("2. Monitor queue in real-time")
    print("3. Show CAPTCHA detection")
    print("4. Track actual database changes")
    print("")
    
    proceed = input("❓ Proceed with detailed debugging? (y/n): ").lower().strip()
    
    if proceed in ['y', 'yes']:
        debug_bot_processing()
    else:
        print("👍 Debug cancelled")

if __name__ == "__main__":
    main()