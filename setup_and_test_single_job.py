# setup_and_test_single_job.py - Complete setup and test for single job application
import requests
import json
import time
import threading
import subprocess
import os

API_BASE = "http://localhost:8002"
JOB_URL = "https://aqueity.applytojob.com/apply/Appyvb1yAu/Jr-SOC-Engineer?source=LinkedIn"

# Your user data
USER_DATA = {
    "email": "shubhammane56@gmail.com",
    "name": "Shubham Mane",
    "password": "secure_password_123"  # Change this to something secure
}

def start_server():
    """Start the FastAPI server"""
    os.chdir('backend')
    subprocess.run(['python', '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8002'])

def load_profile_data():
    """Load your existing profile.json data"""
    # Try multiple possible locations
    possible_paths = [
        'profile.json',           # Root directory
        'data/profile.json',      # Data directory
        './profile.json',         # Current directory
        '../profile.json'         # Parent directory
    ]
    
    for path in possible_paths:
        try:
            with open(path, 'r') as f:
                print(f"✅ Found profile data at: {path}")
                return json.load(f)
        except FileNotFoundError:
            continue
    
    print("❌ profile.json not found. Searched in:")
    for path in possible_paths:
        print(f"   - {path}")
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
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None, None
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Step 2: Create profile with your data
    print("2. Creating profile with your data...")
    try:
        profile_request = {
            "profile_name": "Cybersecurity Professional - Main Profile",
            "profile_data": profile_data,  # Your entire profile.json content
            "is_default": True
        }
        
        response = requests.post(f"{API_BASE}/api/profiles", json=profile_request, headers=headers, timeout=15)
        if response.status_code == 200:
            profile = response.json()
            profile_id = profile['id']
            print(f"✅ Profile created: {profile['profile_name']}")
            print(f"   Profile ID: {profile_id}")
            return access_token, profile_id
        else:
            print(f"❌ Profile creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return access_token, None
            
    except Exception as e:
        print(f"❌ Profile creation error: {e}")
        return access_token, None

def add_job_url_and_process(access_token, profile_id):
    """Add the job URL and start processing"""
    print("🎯 Adding job URL and starting processing...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Step 1: Add the job URL to queue
    print("1. Adding job URL to processing queue...")
    try:
        urls_request = {
            "profile_id": profile_id,
            "urls": [JOB_URL],
            "batch_name": "Test Application - Aqueity SOC Engineer"
        }
        
        response = requests.post(f"{API_BASE}/api/bot/add-urls", json=urls_request, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Added job to queue")
            print(f"   Batch ID: {result['data']['batch_id']}")
            print(f"   Applications created: {result['data']['applications_created']}")
        else:
            print(f"❌ Failed to add job URL: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Add URL error: {e}")
        return False
    
    # Step 2: Check if bot is running
    print("2. Checking bot status...")
    try:
        response = requests.get(f"{API_BASE}/api/bot/status", headers=headers, timeout=10)
        if response.status_code == 200:
            status = response.json()['data']
            if not status.get('running', False):
                print("Bot is not running. Starting bot...")
                # Start the bot
                bot_config = {"headless": False, "max_concurrent": 1}  # headless=False so you can see the browser
                start_response = requests.post(f"{API_BASE}/api/bot/start", json=bot_config, headers=headers, timeout=15)
                if start_response.status_code == 200:
                    print("✅ Bot started successfully")
                else:
                    print(f"❌ Failed to start bot: {start_response.status_code}")
                    return False
            else:
                print("✅ Bot is already running")
    except Exception as e:
        print(f"⚠️ Bot status check error: {e}")
    
    # Step 3: Monitor processing
    print("3. Monitoring application processing...")
    print("   📝 You should see a browser window open shortly...")
    print("   🚨 If a CAPTCHA appears, solve it manually in the browser")
    print("   ⏱️ Monitoring for 5 minutes...")
    
    for i in range(30):  # Monitor for 5 minutes (30 * 10 seconds)
        try:
            response = requests.get(f"{API_BASE}/api/bot/my-queue", headers=headers, timeout=10)
            if response.status_code == 200:
                queue_info = response.json()['data']
                print(f"   📊 Queue: {queue_info['queued']} queued, {queue_info['processing']} processing, " +
                      f"{queue_info['completed']} completed, {queue_info['failed']} failed")
                
                # Check for CAPTCHA
                if queue_info.get('captcha_required', 0) > 0:
                    print(f"   🚨 CAPTCHA detected! Please solve it in the browser window")
                
                # Check if processing is complete
                if queue_info['queued'] == 0 and queue_info['processing'] == 0:
                    if queue_info['completed'] > 0:
                        print("🎉 Application completed successfully!")
                        return True
                    elif queue_info['failed'] > 0:
                        print("❌ Application failed")
                        return False
            
            time.sleep(10)  # Wait 10 seconds before next check
            
        except Exception as e:
            print(f"⚠️ Monitoring error: {e}")
    
    print("⏰ Monitoring timeout reached")
    return False

def main():
    """Main test function"""
    print("🚀 IntelliApply Single Job Application Test")
    print("=" * 60)
    print(f"📋 Job URL: {JOB_URL}")
    print("=" * 60)
    
    # Check if backend directory exists
    if not os.path.exists('backend'):
        print("❌ Error: 'backend' directory not found.")
        print("Please run this script from the IntelliApply_Bot root directory.")
        return
    
    # Check if profile.json exists
    profile_locations = ['profile.json', 'data/profile.json', './profile.json']
    profile_found = any(os.path.exists(path) for path in profile_locations)
    
    if not profile_found:
        print("❌ Error: profile.json not found.")
        print("Searched in:")
        for path in profile_locations:
            print(f"   - {path}")
        print("Please ensure your profile data exists in one of these locations")
        return
    
    # Start server in background
    print("🌐 Starting backend server...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(5)  # Wait for server to start
    
    try:
        # Setup user and profile
        access_token, profile_id = setup_user_and_profile()
        
        if not access_token or not profile_id:
            print("❌ Failed to set up user and profile")
            return
        
        print(f"✅ Setup complete!")
        print(f"   Access Token: {access_token[:30]}...")
        print(f"   Profile ID: {profile_id}")
        
        # Process the job application
        success = add_job_url_and_process(access_token, profile_id)
        
        if success:
            print("\n🎉 SUCCESS! Your job application was processed successfully!")
            print("\nNext steps:")
            print("1. Check the job website to confirm your application was submitted")
            print("2. Add more job URLs to process multiple applications")
            print("3. Build a web dashboard for easier management")
        else:
            print("\n⚠️ Application processing encountered issues")
            print("Check the browser window and server logs for details")
        
        print(f"\n📊 API Documentation: http://localhost:8002/docs")
        print("Press Ctrl+C to stop the server")
        
        # Keep server running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Server stopped")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()