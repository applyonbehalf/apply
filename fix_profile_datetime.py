# fix_profile_datetime.py - Fix datetime serialization issue
import json
from datetime import datetime

def fix_profile_data():
    """Fix datetime serialization in profile data"""
    
    profile_path = "/Users/shubhammane/Desktop/IntelliApply_Bot/data/profile.json"
    
    print("🔧 Fixing Profile DateTime Issues")
    print("=" * 40)
    
    try:
        # Load profile data
        with open(profile_path, 'r') as f:
            profile_data = json.load(f)
        
        print("✅ Profile data loaded successfully")
        
        # Function to convert datetime objects to strings
        def convert_datetime_to_string(obj):
            if isinstance(obj, dict):
                return {key: convert_datetime_to_string(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime_to_string(item) for item in obj]
            elif isinstance(obj, datetime):
                return obj.isoformat()
            else:
                return obj
        
        # Convert any datetime objects
        cleaned_profile = convert_datetime_to_string(profile_data)
        
        # Validate that it's JSON serializable
        test_json = json.dumps(cleaned_profile)
        print("✅ Profile data is now JSON serializable")
        
        # Create backup
        backup_path = profile_path + ".backup"
        with open(backup_path, 'w') as f:
            json.dump(profile_data, f, indent=2)
        print(f"📁 Backup created: {backup_path}")
        
        # Save cleaned version
        with open(profile_path, 'w') as f:
            json.dump(cleaned_profile, f, indent=2)
        
        print(f"✅ Profile updated: {profile_path}")
        return True
        
    except FileNotFoundError:
        print(f"❌ Profile file not found: {profile_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in profile: {e}")
        return False
    except Exception as e:
        print(f"❌ Error fixing profile: {e}")
        return False

# Also create a simpler test to verify the API endpoint
def test_profile_creation_simple():
    """Test profile creation with minimal data"""
    import requests
    
    API_BASE = "http://localhost:8003"
    
    # Login first
    login_data = {
        "email": "shubhmmane56@gmail.com",
        "password": "secure_password_123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/auth/login", json=login_data, timeout=10)
        if response.status_code != 200:
            print("❌ Login failed")
            return False
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test with minimal profile data
        minimal_profile = {
            "profile_name": "Test Profile - Minimal",
            "profile_data": {
                "personal_info": {
                    "legal_first_name": "Shubham",
                    "legal_last_name": "Mane",
                    "email": "shubhammane56@gmail.com",
                    "phone": "312-539-9755"
                }
            },
            "is_default": False  # Don't make it default to avoid conflicts
        }
        
        response = requests.post(f"{API_BASE}/api/profiles", json=minimal_profile, headers=headers, timeout=10)
        
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Minimal profile created successfully: {profile['id']}")
            return True
        else:
            print(f"❌ Minimal profile creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing profile creation: {e}")
        return False

def main():
    """Main function"""
    print("🔧 IntelliApply Profile DateTime Fix")
    print("=" * 50)
    
    # Fix the profile data first
    if fix_profile_data():
        print("\n✅ Profile data fixed!")
        
        # Test with minimal profile
        print("\n🧪 Testing profile creation...")
        if test_profile_creation_simple():
            print("\n🎯 Profile creation is working!")
            print("\nNext steps:")
            print("1. Run: python quick_fix_and_test.py")
            print("2. The profile creation should now work")
        else:
            print("\n⚠️ Profile creation still has issues")
            print("Check the server logs for more details")
    else:
        print("\n❌ Failed to fix profile data")

if __name__ == "__main__":
    main()