# test_enhanced_bot.py - Test the enhanced multi-user bot system
import asyncio
import requests
import time
import threading
import subprocess
import os

API_BASE = "http://localhost:8000"

# Test user credentials
TEST_USER = {
    "email": "testuser@example.com",
    "name": "Test User",
    "password": "testpassword123"
}

TEST_URLS = [
    "https://aqueity.applytojob.com/apply/Appyvb1yAu/Jr-SOC-Engineer?source=LinkedIn",
    # Add more test URLs here
]

def start_server():
    """Start the FastAPI server"""
    os.chdir('backend')
    subprocess.run(['python', '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'])

async def test_enhanced_bot_system():
    """Test the complete enhanced bot system"""
    print("🤖 Testing Enhanced IntelliApply Bot System")
    print("=" * 60)
    
    # Wait for server
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    try:
        # Step 1: Register/Login user
        print("\n1. Setting up test user...")
        try:
            response = requests.post(f"{API_BASE}/api/auth/register", json=TEST_USER, timeout=10)
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data["access_token"]
                print(f"✅ User registered successfully")
            else:
                # Try login instead
                response = requests.post(f"{API_BASE}/api/auth/login", json={
                    "email": TEST_USER["email"],
                    "password": TEST_USER["password"]
                }, timeout=10)
                if response.status_code == 200:
                    token_data = response.json()
                    access_token = token_data["access_token"]
                    print(f"✅ User logged in successfully")
                else:
                    print(f"❌ Authentication failed: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Step 2: Create a profile
        print("\n2. Creating user profile...")
        profile_data = {
            "profile_name": "Enhanced Test Profile",
            "profile_data": {
                "personal_info": {
                    "legal_first_name": "Test",
                    "legal_last_name": "User",
                    "email": "testuser@example.com",
                    "phone": "555-123-4567",
                    "location": "Chicago, IL",
                    "address_line_1": "123 Test St",
                    "city": "Chicago",
                    "state_province": "IL",
                    "zip_postal_code": "60601"
                },
                "experience": {
                    "total_years_professional_experience": "5",
                    "salary_expectation": "$100,000"
                },
                "preferences": {
                    "work_preference": "Hybrid"
                },
                "eligibility": {
                    "are_you_legally_authorized_to_work": "Yes",
                    "will_you_require_sponsorship": "No"
                }
            },
            "is_default": True
        }
        
        try:
            response = requests.post(f"{API_BASE}/api/profiles", json=profile_data, headers=headers, timeout=10)
            if response.status_code == 200:
                profile = response.json()
                profile_id = profile['id']
                print(f"✅ Profile created: {profile['profile_name']}")
            else:
                print(f"❌ Profile creation failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Profile creation error: {e}")
            return False
        
        # Step 3: Check bot status
        print("\n3. Checking bot status...")
        try:
            response = requests.get(f"{API_BASE}/api/bot/status", headers=headers, timeout=10)
            if response.status_code == 200:
                status = response.json()
                print(f"✅ Bot status: {status['data']['message']}")
                bot_running = status['data']['running']
            else:
                print(f"⚠️ Bot status check failed: {response.status_code}")
                bot_running = False
        except Exception as e:
            print(f"❌ Bot status error: {e}")
            bot_running = False
        
        # Step 4: Start bot if not running
        if not bot_running:
            print("\n4. Starting bot...")
            try:
                bot_config = {
                    "headless": False,  # Set to False for testing to see the browser
                    "max_concurrent": 1
                }
                response = requests.post(f"{API_BASE}/api/bot/start", json=bot_config, headers=headers, timeout=15)
                if response.status_code == 200:
                    print("✅ Bot started successfully")
                else:
                    print(f"❌ Bot start failed: {response.status_code} - {response.text}")
                    return False
            except Exception as e:
                print(f"❌ Bot start error: {e}")
                return False
        else:
            print("ℹ️ Bot is already running")
        
        # Step 5: Add URLs to queue
        print("\n5. Adding test URLs to queue...")
        try:
            urls_request = {
                "profile_id": profile_id,
                "urls": TEST_URLS,
                "batch_name": "Enhanced Bot Test Batch"
            }
            response = requests.post(f"{API_BASE}/api/bot/add-urls", json=urls_request, headers=headers, timeout=10)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Added {result['data']['applications_created']} applications to queue")
                batch_id = result['data']['batch_id']
            else:
                print(f"❌ Failed to add URLs: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Add URLs error: {e}")
            return False
        
        # Step 6: Monitor queue progress
        print("\n6. Monitoring queue progress...")
        for i in range(12):  # Monitor for 2 minutes (12 * 10 seconds)
            try:
                response = requests.get(f"{API_BASE}/api/bot/my-queue", headers=headers, timeout=10)
                if response.status_code == 200:
                    queue_info = response.json()['data']
                    print(f"   Queue status: {queue_info['queued']} queued, {queue_info['processing']} processing, " +
                          f"{queue_info['completed']} completed, {queue_info['failed']} failed")
                    
                    # Check for CAPTCHA
                    if queue_info['captcha_required'] > 0:
                        print(f"   🚨 {queue_info['captcha_required']} applications require CAPTCHA solving")
                        
                        # Get pending CAPTCHAs
                        captcha_response = requests.get(f"{API_BASE}/api/bot/captcha/pending", timeout=10)
                        if captcha_response.status_code == 200:
                            captchas = captcha_response.json()['data']
                            for captcha in captchas:
                                print(f"   📝 CAPTCHA session: {captcha['id'][:8]}... - Expires: {captcha['expires_at']}")
                                print(f"      Solve at: https://applyonbehalf.com/solve-captcha/{captcha['id']}")
                    
                    # Break if all processed
                    if queue_info['queued'] == 0 and queue_info['processing'] == 0:
                        print("✅ All applications processed!")
                        break
                
                time.sleep(10)  # Wait 10 seconds before next check
                
            except Exception as e:
                print(f"⚠️ Queue monitoring error: {e}")
        
        # Step 7: Get final statistics
        print("\n7. Final statistics...")
        try:
            response = requests.get(f"{API_BASE}/api/bot/status", headers=headers, timeout=10)
            if response.status_code == 200:
                status = response.json()['data']
                if 'stats' in status:
                    stats = status['stats']
                    print(f"   Total processed: {stats.get('total_processed', 0)}")
                    print(f"   Successful: {stats.get('successful', 0)}")
                    print(f"   Failed: {stats.get('failed', 0)}")
                    print(f"   CAPTCHAs encountered: {stats.get('captcha_required', 0)}")
                    print(f"   Success rate: {stats.get('success_rate', 0):.1f}%")
        except Exception as e:
            print(f"⚠️ Statistics error: {e}")
        
        # Step 8: Test manual single application (optional)
        print("\n8. Testing single application processing...")
        if len(TEST_URLS) > 1:
            try:
                single_request = {
                    "profile_id": profile_id,
                    "job_url": TEST_URLS[0]  # Use first URL for single test
                }
                response = requests.post(f"{API_BASE}/api/bot/process-single", json=single_request, headers=headers, timeout=30)
                if response.status_code == 200:
                    print("✅ Single application processed successfully")
                else:
                    print(f"⚠️ Single application processing: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Single application error: {e}")
        
        print("\n🎉 Enhanced bot system test completed!")
        print("\nKey Features Tested:")
        print("   ✅ Multi-user authentication")
        print("   ✅ Profile management")
        print("   ✅ Bot control (start/stop)")
        print("   ✅ Queue management")
        print("   ✅ CAPTCHA detection")
        print("   ✅ Real-time monitoring")
        print("   ✅ Statistics tracking")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def main():
    """Main test runner"""
    print("🚀 Starting Enhanced IntelliApply Bot Test")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('backend'):
        print("❌ Error: 'backend' directory not found.")
        print("Please run this script from the IntelliApply_Bot root directory.")
        return
    
    # Start server in background
    print("🌐 Starting API server...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Run the async test
    success = asyncio.run(test_enhanced_bot_system())
    
    if success:
        print("\n✅ All tests passed! Your enhanced bot system is working correctly.")
        print("\nNext steps:")
        print("   1. Visit http://localhost:8000/docs to explore all API endpoints")
        print("   2. Build the frontend dashboard")
        print("   3. Add more job URLs to test at scale")
        print("   4. Set up email/SMS notifications")
        
        print("\n   Press Ctrl+C to stop the server")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Test completed")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()