# simple_profile_test.py - Test if we can find and load your profile
import json
import os

def test_profile_loading():
    """Test loading profile from various locations"""
    print("🔍 Testing Profile Loading")
    print("=" * 40)
    
    # Absolute path
    absolute_path = "/Users/shubhammane/Desktop/IntelliApply_Bot/data/profile.json"
    
    # Relative paths
    relative_paths = [
        'data/profile.json',
        'profile.json', 
        './data/profile.json',
        './profile.json'
    ]
    
    all_paths = [absolute_path] + relative_paths
    
    print("Current working directory:", os.getcwd())
    print("\nTesting paths:")
    
    for i, path in enumerate(all_paths, 1):
        print(f"\n{i}. Testing: {path}")
        
        # Check if file exists
        if os.path.exists(path):
            print(f"   ✅ File exists")
            
            # Try to read it
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                print(f"   ✅ Successfully loaded JSON")
                print(f"   📊 Keys found: {list(data.keys())}")
                
                # Check for required fields
                if 'personal_info' in data:
                    personal = data['personal_info']
                    name = f"{personal.get('legal_first_name', '')} {personal.get('legal_last_name', '')}"
                    email = personal.get('email', '')
                    print(f"   👤 Name: {name}")
                    print(f"   📧 Email: {email}")
                
                print(f"   🎉 SUCCESS! Profile loaded from: {path}")
                return path, data
                
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON decode error: {e}")
            except Exception as e:
                print(f"   ❌ Error reading file: {e}")
        else:
            print(f"   ❌ File not found")
    
    print("\n❌ Could not load profile from any location")
    return None, None

def main():
    """Main test"""
    path, data = test_profile_loading()
    
    if path and data:
        print(f"\n🎯 Profile successfully loaded!")
        print(f"📁 Location: {path}")
        print(f"📊 Data size: {len(json.dumps(data))} characters")
        
        # Show some key info
        personal = data.get('personal_info', {})
        print(f"\n📋 Profile Summary:")
        print(f"   Name: {personal.get('legal_first_name')} {personal.get('legal_last_name')}")
        print(f"   Email: {personal.get('email')}")
        print(f"   Phone: {personal.get('phone')}")
        print(f"   Location: {personal.get('location')}")
        
        eligibility = data.get('eligibility', {})
        print(f"\n🔍 Work Eligibility:")
        print(f"   Work authorized: {eligibility.get('are_you_legally_authorized_to_work')}")
        print(f"   Sponsorship needed: {eligibility.get('will_you_require_sponsorship')}")
        
        print(f"\n✅ Your profile is ready for the application system!")
        
    else:
        print(f"\n❌ Profile loading failed")
        print(f"Please check:")
        print(f"   1. File exists at: /Users/shubhammane/Desktop/IntelliApply_Bot/data/profile.json")
        print(f"   2. File contains valid JSON")
        print(f"   3. You're running this from: IntelliApply_Bot directory")

if __name__ == "__main__":
    main()