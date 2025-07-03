# test_auth.py - Test authentication endpoints
import requests
import json
import time

API_BASE = "http://localhost:8002"  # Adjust port if needed

def test_auth_flow():
    """Test the complete authentication flow"""
    print("🔐 Testing Authentication Flow")
    print("=" * 50)
    
    # Test data
    test_user = {
        "email": "testuser@intelliapply.com",
        "name": "Test User",
        "password": "securepassword123"
    }
    
    try:
        # Test 1: Register user
        print("\n1. Testing user registration...")
        response = requests.post(
            f"{API_BASE}/api/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"   Token: {access_token[:30]}...")
        elif response.status_code == 400 and "already registered" in response.text:
            print("ℹ️ User already exists, proceeding to login...")
            access_token = None
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        # Test 2: Login user (if registration failed due to existing user)
        if not access_token:
            print("\n2. Testing user login...")
            response = requests.post(
                f"{API_BASE}/api/auth/login",
                json={
                    "email": test_user["email"],
                    "password": test_user["password"]
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Login successful!")
                token_data = response.json()
                access_token = token_data.get("access_token")
                print(f"   Token: {access_token[:30]}...")
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        
        # Test 3: Get current user info
        if access_token:
            print("\n3. Testing protected endpoint...")
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{API_BASE}/api/auth/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Protected endpoint access successful!")
                user_info = response.json()
                print(f"   User: {user_info.get('name')} ({user_info.get('email')})")
                print(f"   Plan: {user_info.get('subscription_plan')}")
                print(f"   Applications: {user_info.get('applications_used')}/{user_info.get('applications_limit')}")
            else:
                print(f"❌ Protected endpoint failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        
        # Test 4: Test other endpoints with token
        if access_token:
            print("\n4. Testing other API endpoints...")
            
            endpoints_to_test = [
                ("users/stats", "User Stats"),
                ("profiles/", "User Profiles"),
                ("applications/", "Applications"),
                ("batches/", "Batches"),
                ("bot/status", "Bot Status")
            ]
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            for endpoint, name in endpoints_to_test:
                try:
                    response = requests.get(
                        f"{API_BASE}/api/{endpoint}",
                        headers=headers,
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        print(f"   ✅ {name}: Working")
                    else:
                        print(f"   ⚠️ {name}: Status {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ {name}: Error ({e})")
        
        # Test 5: Check all registered users (testing endpoint)
        print("\n5. Checking registered users...")
        try:
            response = requests.get(f"{API_BASE}/api/auth/users", timeout=5)
            if response.status_code == 200:
                users_info = response.json()
                print(f"✅ Users endpoint working: {users_info}")
            else:
                print(f"⚠️ Users endpoint: {response.status_code}")
        except Exception as e:
            print(f"❌ Users endpoint error: {e}")
        
        print("\n🎉 Authentication flow test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_scenarios():
    """Test error scenarios"""
    print("\n🔧 Testing Error Scenarios")
    print("=" * 30)
    
    # Test invalid login
    print("\n1. Testing invalid login...")
    response = requests.post(
        f"{API_BASE}/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        },
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 401:
        print("✅ Invalid login correctly rejected")
    else:
        print(f"⚠️ Unexpected response for invalid login: {response.status_code}")
    
    # Test invalid token
    print("\n2. Testing invalid token...")
    headers = {
        "Authorization": "Bearer invalid_token_12345",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{API_BASE}/api/auth/me", headers=headers)
    
    if response.status_code == 401:
        print("✅ Invalid token correctly rejected")
    else:
        print(f"⚠️ Unexpected response for invalid token: {response.status_code}")

def main():
    """Main test function"""
    print("🧪 IntelliApply Authentication Test")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server not responding correctly: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server at {API_BASE}")
        print(f"   Make sure the server is running with: python test_api_diagnostic.py")
        return
    
    print(f"✅ Server is running at {API_BASE}")
    
    # Run tests
    auth_success = test_auth_flow()
    
    if auth_success:
        test_error_scenarios()
        print("\n✅ All authentication tests completed!")
        print(f"\n📖 API Documentation: {API_BASE}/docs")
        print(f"🌐 Test the API interactively at the docs URL")
    else:
        print("\n❌ Authentication tests failed")

if __name__ == "__main__":
    main()