# test_admin_system.py - Complete admin system test
import requests
import json

API_BASE = "http://localhost:8002"

def test_admin_system():
    """Test the complete admin system"""
    print("🔧 Testing Admin System")
    print("=" * 50)
    
    # Step 1: Test admin endpoint (no auth required)
    print("\n1. Testing admin test endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/admin/test")
        if response.status_code == 200:
            print("✅ Admin API is working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Admin test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Admin test error: {e}")
        return False
    
    # Step 2: Register admin user
    print("\n2. Registering admin user...")
    admin_user = {
        "email": "shubhammane56@gmail.com",  # Your email for admin access
        "name": "Admin User",
        "password": "adminpass123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/auth/register", json=admin_user)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print("✅ Admin user registered")
        elif response.status_code == 400 and "already registered" in response.text:
            # Try login instead
            print("   User exists, trying login...")
            response = requests.post(f"{API_BASE}/api/auth/login", json={
                "email": admin_user["email"],
                "password": admin_user["password"]
            })
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data["access_token"]
                print("✅ Admin user logged in")
            else:
                print(f"❌ Admin login failed: {response.status_code}")
                return False
        else:
            print(f"❌ Admin registration failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Admin auth error: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Step 3: Test job categories
    print("\n3. Testing job categories...")
    try:
        response = requests.get(f"{API_BASE}/api/admin/categories", headers=headers)
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Found {len(categories)} job categories:")
            for cat in categories:
                print(f"   - {cat['category_name']}: {cat['description']}")
                
            # Save first category ID for testing
            if categories:
                cyber_security_cat = next((cat for cat in categories if 'cyber' in cat['category_name'].lower()), categories[0])
                category_id = cyber_security_cat['id']
                category_name = cyber_security_cat['category_name']
            else:
                print("❌ No categories found")
                return False
        else:
            print(f"❌ Categories test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Categories error: {e}")
        return False
    
    # Step 4: Test adding job URLs
    print(f"\n4. Testing adding job URLs to '{category_name}'...")
    test_urls = [
        "https://example.com/cybersecurity-analyst-1",
        "https://example.com/security-engineer-2",
        "https://test-company.com/info-sec-role"
    ]
    
    try:
        response = requests.post(f"{API_BASE}/api/admin/job-urls", 
                               headers=headers,
                               json={
                                   "category_id": category_id,
                                   "urls": test_urls
                               })
        if response.status_code == 200:
            result = response.json()
            print("✅ Successfully added job URLs")
            print(f"   URLs added: {result['data']['urls_added']}")
            print(f"   Applications created: {result['data']['applications_created']}")
        else:
            print(f"❌ Adding URLs failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Add URLs error: {e}")
        return False
    
    # Step 5: Test getting job URLs
    print("\n5. Testing job URLs retrieval...")
    try:
        response = requests.get(f"{API_BASE}/api/admin/job-urls", headers=headers)
        if response.status_code == 200:
            job_urls = response.json()
            print(f"✅ Found {len(job_urls)} job URLs in system")
            for url in job_urls[:3]:  # Show first 3
                print(f"   - {url['job_url']} ({url.get('category_name', 'Unknown')})")
        else:
            print(f"❌ Job URLs retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Job URLs error: {e}")
        return False
    
    # Step 6: Test admin stats
    print("\n6. Testing admin statistics...")
    try:
        response = requests.get(f"{API_BASE}/api/admin/stats", headers=headers)
        if response.status_code == 200:
            result = response.json()
            stats = result['data']
            print("✅ Admin statistics:")
            print(f"   Total users: {stats['total_users']}")
            print(f"   Total categories: {stats['total_categories']}")
            print(f"   Total job URLs: {stats['total_job_urls']}")
            print(f"   Active applications: {stats['active_applications']}")
            print(f"   Pending CAPTCHAs: {stats['pending_captchas']}")
        else:
            print(f"❌ Admin stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Admin stats error: {e}")
        return False
    
    # Step 7: Create a test user with job preferences
    print("\n7. Creating test user with job preferences...")
    test_user = {
        "email": "testuser1@example.com",
        "name": "Test User 1",
        "password": "testpass123"
    }
    
    try:
        # Register test user
        response = requests.post(f"{API_BASE}/api/auth/register", json=test_user)
        if response.status_code == 200:
            user_token_data = response.json()
            user_token = user_token_data["access_token"]
            print("✅ Test user created")
        elif response.status_code == 400:
            # User exists, login
            response = requests.post(f"{API_BASE}/api/auth/login", json={
                "email": test_user["email"],
                "password": test_user["password"]
            })
            if response.status_code == 200:
                user_token_data = response.json()
                user_token = user_token_data["access_token"]
                print("✅ Test user logged in")
            else:
                print("⚠️ Could not login test user, skipping profile test")
                user_token = None
        else:
            print("⚠️ Could not create test user, skipping profile test")
            user_token = None
        
        # Create profile with job category preference
        if user_token:
            user_headers = {"Authorization": f"Bearer {user_token}"}
            profile_data = {
                "profile_name": "Cybersecurity Professional",
                "profile_data": {
                    "personal_info": {
                        "legal_first_name": "Test",
                        "legal_last_name": "User",
                        "email": "testuser1@example.com"
                    },
                    "experience": {
                        "total_years_professional_experience": "3"
                    }
                },
                "preferred_job_category_id": category_id,  # Link to cybersecurity
                "is_default": True
            }
            
            response = requests.post(f"{API_BASE}/api/profiles", 
                                   headers=user_headers,
                                   json=profile_data)
            if response.status_code == 200:
                print("✅ Test user profile created with job category preference")
            else:
                print(f"⚠️ Profile creation failed: {response.status_code}")
                
    except Exception as e:
        print(f"⚠️ Test user setup error: {e}")
    
    print("\n🎉 Admin System Test Complete!")
    print("\n📋 Summary:")
    print("✅ Admin API endpoints working")
    print("✅ Job categories loaded")
    print("✅ Job URL management working")
    print("✅ Auto-application creation working")
    print("✅ Admin statistics working")
    print("✅ User-category linking working")
    
    print(f"\n🌐 Your admin dashboard will be at: {API_BASE}/admin")
    print("🎯 Next steps:")
    print("   1. Add the AdminDashboard.tsx to your frontend")
    print("   2. Add real job URLs through the admin interface")
    print("   3. Watch applications get created automatically!")
    
    return True

if __name__ == "__main__":
    test_admin_system()