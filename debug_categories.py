# debug_categories.py - Check what's in the database
import requests
import json

API_BASE = "http://localhost:8002"

def debug_categories():
    """Debug what categories exist"""
    print("🔍 Debugging Job Categories")
    print("=" * 40)
    
    # Get your token (use the one from your curl command)
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4ZjYxYmYyOS1hYzZmLTRmNzktODdlNi0yYzNlZDA3ZDBlNTciLCJleHAiOjE3NTIxNzk5NTd9.XYC1qcEdbqy8j-gm-L6BtgCAWzjR2gkyq0KOnbepyXc"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Check if admin API works
    print("1. Testing admin API...")
    try:
        response = requests.get(f"{API_BASE}/api/admin/test", headers=headers)
        if response.status_code == 200:
            print("✅ Admin API working")
        else:
            print(f"❌ Admin API failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Admin API error: {e}")
        return
    
    # Test 2: Check categories
    print("\n2. Checking job categories...")
    try:
        response = requests.get(f"{API_BASE}/api/admin/categories", headers=headers)
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Found {len(categories)} categories:")
            
            if categories:
                for i, cat in enumerate(categories, 1):
                    print(f"   {i}. ID: {cat['id']}")
                    print(f"      Name: {cat['category_name']}")
                    print(f"      Description: {cat['description']}")
                    print()
                
                # Show how to use the first category
                first_cat = categories[0]
                print("🎯 Example curl command with correct category ID:")
                print(f'curl -X POST "http://localhost:8002/api/admin/job-urls" \\')
                print(f'     -H "Authorization: Bearer {token}" \\')
                print(f'     -H "Content-Type: application/json" \\')
                print(f'     -d \'{{')
                print(f'       "category_id": "{first_cat["id"]}",')
                print(f'       "urls": [')
                print(f'         "https://example.com/job-1",')
                print(f'         "https://example.com/job-2"')
                print(f'       ]')
                print(f'     }}\'')
                
            else:
                print("❌ No categories found!")
                print("\n🔧 This means the database setup didn't work.")
                print("   Please run the Supabase SQL script first.")
                
        elif response.status_code == 403:
            print("❌ Access denied - you're not recognized as admin")
            print("   Make sure you're using shubhammane56@gmail.com")
        else:
            print(f"❌ Categories request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Categories error: {e}")
    
    # Test 3: Check current user
    print("\n3. Checking current user...")
    try:
        response = requests.get(f"{API_BASE}/api/auth/me", headers=headers)
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Current user: {user['name']} ({user['email']})")
            if user['email'] == "shubhammane56@gmail.com":
                print("✅ You have admin privileges")
            else:
                print("⚠️ You might not have admin privileges")
        else:
            print(f"❌ User check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User check error: {e}")

if __name__ == "__main__":
    debug_categories()