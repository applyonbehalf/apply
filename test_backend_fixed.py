# test_backend_fixed.py - Fixed to work from parent directory
import uvicorn
import requests
import time
import threading
import json
import os
import sys
from datetime import datetime

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

# Test configuration
API_BASE = "http://localhost:8000"
TEST_USER = {
    "email": "test@example.com",
    "name": "Test User", 
    "password": "testpassword123"
}

def start_server():
    """Start the FastAPI server in a separate thread"""
    # Change to backend directory
    os.chdir('backend')
    
    # Import and run the app
    try:
        from main import app
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="critical")
    except Exception as e:
        print(f"Server start error: {e}")

def test_api_endpoints():
    """Test all API endpoints"""
    print("🧪 Testing IntelliApply Backend API")
    print("=" * 50)
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: User registration
    print("\n2. Testing user registration...")
    try:
        response = requests.post(f"{API_BASE}/api/auth/register", json=TEST_USER)
        if response.status_code == 200:
            print("✅ User registration passed")
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"   Token received: {access_token[:20]}...")
        else:
            print(f"❌ User registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ User registration failed: {e}")
        return False
    
    # Test 3: Get current user
    print("\n3. Testing get current user...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{API_BASE}/api/auth/me", headers=headers)
        if response.status_code == 200:
            print("✅ Get current user passed")
            user_data = response.json()
            print(f"   User: {user_data['name']} ({user_data['email']})")
            user_id = user_data['id']
        else:
            print(f"❌ Get current user failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get current user failed: {e}")
        return False
    
    # Test 4: Create a profile
    print("\n4. Testing profile creation...")
    try:
        profile_data = {
            "profile_name": "Software Engineer Profile",
            "profile_data": {
                "personal_info": {
                    "legal_first_name": "Test",
                    "legal_last_name": "User",
                    "email": "test@example.com",
                    "phone": "555-123-4567"
                },
                "experience": {
                    "total_years": "5",
                    "salary_expectation": "$100,000"
                }
            },
            "is_default": True
        }
        
        response = requests.post(f"{API_BASE}/api/profiles", json=profile_data, headers=headers)
        if response.status_code == 200:
            print("✅ Profile creation passed")
            profile = response.json()
            print(f"   Profile: {profile['profile_name']}")
            profile_id = profile['id']
        else:
            print(f"❌ Profile creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Profile creation failed: {e}")
        return False
    
    # Test 5: Get user profiles
    print("\n5. Testing get user profiles...")
    try:
        response = requests.get(f"{API_BASE}/api/profiles", headers=headers)
        if response.status_code == 200:
            print("✅ Get user profiles passed")
            profiles = response.json()
            print(f"   Found {len(profiles)} profiles")
        else:
            print(f"❌ Get user profiles failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get user profiles failed: {e}")
        return False
    
    # Test 6: Create application batch
    print("\n6. Testing batch creation...")
    try:
        batch_data = {
            "batch_name": "Test Job Applications",
            "urls": [
                "https://example.com/job1",
                "https://example.com/job2",
                "https://example.com/job3"
            ],
            "profile_id": profile_id
        }
        
        response = requests.post(f"{API_BASE}/api/batches", json=batch_data, headers=headers)
        if response.status_code == 200:
            print("✅ Batch creation passed")
            batch = response.json()
            print(f"   Batch: {batch['batch_name']} ({batch['total_count']} jobs)")
        else:
            print(f"❌ Batch creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Batch creation failed: {e}")
        return False
    
    # Test 7: Get user stats
    print("\n7. Testing user stats...")
    try:
        response = requests.get(f"{API_BASE}/api/users/stats", headers=headers)
        if response.status_code == 200:
            print("✅ User stats passed")
            stats = response.json()
            print(f"   Total applications: {stats['total_applications']}")
            print(f"   Success rate: {stats['success_rate']}%")
        else:
            print(f"❌ User stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ User stats failed: {e}")
        return False
    
    # Test 8: Get pending CAPTCHAs
    print("\n8. Testing pending CAPTCHAs...")
    try:
        response = requests.get(f"{API_BASE}/api/captcha/pending")
        if response.status_code == 200:
            print("✅ Pending CAPTCHAs passed")
            captchas = response.json()
            print(f"   Found {len(captchas)} pending CAPTCHAs")
        else:
            print(f"❌ Pending CAPTCHAs failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Pending CAPTCHAs failed: {e}")
        return False
    
    print("\n🎉 All API tests passed!")
    print("\n📋 API Summary:")
    print(f"   - Base URL: {API_BASE}")
    print(f"   - Documentation: {API_BASE}/docs")
    print(f"   - Test user created: {TEST_USER['email']}")
    print(f"   - Access token: {access_token[:30]}...")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting IntelliApply Backend Test")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('backend'):
        print("❌ Error: 'backend' directory not found.")
        print("Please run this script from the IntelliApply_Bot root directory.")
        exit(1)
    
    # Start server in background
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Run tests
    success = test_api_endpoints()
    
    if success:
        print("\n✅ Backend is ready! You can now:")
        print("   1. Visit http://localhost:8000/docs for API documentation")
        print("   2. Test endpoints manually")
        print("   3. Move to Day 3 tasks")
        print("\n   Press Ctrl+C to stop the server")
        
        # Keep server running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Server stopped")
    else:
        print("\n❌ Backend tests failed. Please check the errors above.")