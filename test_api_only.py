# test_api_only.py - Test just the API endpoints first
import requests
import time
import threading
import subprocess
import os

API_BASE = "http://localhost:8000"

TEST_USER = {
    "email": "testuser@example.com",
    "name": "Test User",
    "password": "testpassword123"
}

def start_server():
    """Start the FastAPI server"""
    os.chdir('backend')
    subprocess.run(['python', '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'])

def test_api_endpoints():
    """Test just the API endpoints"""
    print("🧪 Testing IntelliApply API Endpoints")
    print("=" * 50)
    
    # Wait for server
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    try:
        # Test 1: Health check
        print("\n1. Testing health check...")
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Health check: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Test 2: Root endpoint
        print("\n2. Testing root endpoint...")
        response = requests.get(f"{API_BASE}/", timeout=5)
        if response.status_code == 200:
            print(f"✅ Root endpoint: {response.json()['message']}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
        
        # Test 3: Authentication
        print("\n3. Testing authentication...")
        response = requests.post(f"{API_BASE}/api/auth/register", json=TEST_USER, timeout=10)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"✅ User registered: {TEST_USER['email']}")
        else:
            # Try login
            response = requests.post(f"{API_BASE}/api/auth/login", json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }, timeout=10)
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data["access_token"]
                print(f"✅ User logged in: {TEST_USER['email']}")
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test 4: Get current user
        print("\n4. Testing get current user...")
        response = requests.get(f"{API_BASE}/api/auth/me", headers=headers, timeout=5)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Current user: {user_data['name']} ({user_data['subscription_plan']})")
        else:
            print(f"❌ Get user failed: {response.status_code}")
            return False
        
        # Test 5: Create profile
        print("\n5. Testing profile creation...")
        profile_data = {
            "profile_name": "Test Profile",
            "profile_data": {
                "personal_info": {
                    "legal_first_name": "Test",
                    "legal_last_name": "User",
                    "email": "test@example.com",
                    "phone": "555-123-4567"
                },
                "experience": {
                    "total_years_professional_experience": "5",
                    "salary_expectation": "$100,000"
                }
            },
            "is_default": True
        }
        
        response = requests.post(f"{API_BASE}/api/profiles", json=profile_data, headers=headers, timeout=10)
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Profile created: {profile['profile_name']}")
            profile_id = profile['id']
        else:
            print(f"❌ Profile creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Test 6: Bot status (should work even if bot isn't running)
        print("\n6. Testing bot status...")
        response = requests.get(f"{API_BASE}/api/bot/status", headers=headers, timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Bot status endpoint working: {status['success']}")
        else:
            print(f"❌ Bot status failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        print("\n🎉 All API endpoints are working!")
        print("\nNext steps:")
        print("1. Fix any remaining import issues")
        print("2. Add missing database functions")
        print("3. Test the full bot system")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main test runner"""
    print("🚀 Testing IntelliApply API Only")
    print("=" * 50)
    
    # Check directory
    if not os.path.exists('backend'):
        print("❌ Error: 'backend' directory not found.")
        return
    
    # Start server
    print("🌐 Starting API server...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Test
    success = test_api_endpoints()
    
    if success:
        print("\n✅ API is working! Now you can:")
        print("   1. Add the missing database functions")
        print("   2. Replace the notification service")
        print("   3. Test the full enhanced bot")
        
        print("\n   Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Test completed")
    else:
        print("\n❌ API test failed")

if __name__ == "__main__":
    main()