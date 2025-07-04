# simple_profile_test_api.py - Simple test for profile creation
import requests
import json
import time

def test_profile_creation():
    """Test profile creation with the fixed backend"""
    
    print("🧪 Testing Profile Creation API")
    print("=" * 40)
    
    API_BASE = "http://localhost:8003"
    
    # Login first
    login_data = {
        "email": "shubhmmane56@gmail.com",
        "password": "secure_password_123"
    }
    
    try:
        print("1. Logging in...")
        response = requests.post(f"{API_BASE}/api/auth/login", json=login_data, timeout=10)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return False
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
        
        # Test with very simple profile data
        print("2. Testing simple profile creation...")
        simple_profile = {
            "profile_name": f"Test Profile {int(time.time())}",  # Unique name
            "profile_data": {
                "personal_info": {
                    "legal_first_name": "Shubham",
                    "legal_last_name": "Mane",
                    "email": "shubhmmane56@gmail.com"
                }
            },
            "is_default": False
        }
        
        response = requests.post(f"{API_BASE}/api/profiles", json=simple_profile, headers=headers, timeout=10)
        
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Profile created successfully!")
            print(f"   ID: {profile['id']}")
            print(f"   Name: {profile['profile_name']}")
            return profile['id']
        else:
            print(f"❌ Profile creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_with_full_profile():
    """Test with the full profile data"""
    
    print("\n3. Testing with full profile data...")
    
    API_BASE = "http://localhost:8003"
    
    # Login
    login_data = {
        "email": "shubhmmane56@gmail.com",
        "password": "secure_password_123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/auth/login", json=login_data, timeout=10)
        if response.status_code != 200:
            return False
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Load the full profile data
        profile_path = "/Users/shubhammane/Desktop/IntelliApply_Bot/data/profile.json"
        with open(profile_path, 'r') as f:
            full_profile_data = json.load(f)
        
        full_profile = {
            "profile_name": f"Full Profile {int(time.time())}",
            "profile_data": full_profile_data,
            "is_default": False
        }
        
        response = requests.post(f"{API_BASE}/api/profiles", json=full_profile, headers=headers, timeout=15)
        
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Full profile created successfully!")
            print(f"   ID: {profile['id']}")
            print(f"   Name: {profile['profile_name']}")
            return profile['id']
        else:
            print(f"❌ Full profile creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error with full profile: {e}")
        return False

def main():
    """Main test"""
    print("🧪 IntelliApply Profile API Test")
    print("=" * 50)
    
    # Test simple profile first
    simple_profile_id = test_profile_creation()
    
    if simple_profile_id:
        # Test full profile
        full_profile_id = test_with_full_profile()
        
        if full_profile_id:
            print(f"\n🎉 SUCCESS! Both profiles created!")
            print(f"   Simple Profile ID: {simple_profile_id}")
            print(f"   Full Profile ID: {full_profile_id}")
            print(f"\n🎯 Ready for application testing!")
            print(f"Run: python quick_fix_and_test.py")
        else:
            print(f"\n⚠️ Simple profile works, but full profile has issues")
            print(f"You can still test with the simple profile: {simple_profile_id}")
    else:
        print(f"\n❌ Profile creation still not working")
        print(f"Check if the server was restarted after the backend fix")

if __name__ == "__main__":
    main()