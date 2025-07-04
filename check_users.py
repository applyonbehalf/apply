# check_users.py - Tool to check users and database
import requests
import json
import sys
import os

API_BASE = "http://localhost:8003"

def check_server():
    """Check if server is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def login_user(email, password):
    """Login and get token"""
    try:
        login_data = {"email": email, "password": password}
        response = requests.post(f"{API_BASE}/api/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def get_current_user(token):
    """Get current user info"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/api/auth/me", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Get user failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Get user error: {e}")
        return None

def get_user_profiles(token):
    """Get user profiles"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/api/profiles", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Get profiles failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Get profiles error: {e}")
        return None

def get_user_applications(token):
    """Get user applications"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/api/applications", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Get applications failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Get applications error: {e}")
        return None

def main():
    """Main function"""
    print("🔍 IntelliApply User & Database Checker")
    print("=" * 50)
    
    # Check if server is running
    if not check_server():
        print("❌ Server is not running. Start it first:")
        print("   cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8003")
        return
    
    print("✅ Server is running")
    
    # Login with your credentials
    email = "shubhmmane56@gmail.com"  # Fixed email
    password = "secure_password_123"
    
    print(f"\n🔐 Logging in as: {email}")
    token = login_user(email, password)
    
    if not token:
        print("❌ Could not login. Maybe user doesn't exist or wrong password?")
        return
    
    print(f"✅ Login successful! Token: {token[:30]}...")
    
    # Get user info
    print(f"\n👤 Getting user information...")
    user_info = get_current_user(token)
    
    if user_info:
        print(f"✅ User Details:")
        print(f"   ID: {user_info['id']}")
        print(f"   Name: {user_info['name']}")
        print(f"   Email: {user_info['email']}")
        print(f"   Subscription: {user_info['subscription_plan']}")
        print(f"   Applications Used: {user_info['applications_used']}/{user_info['applications_limit']}")
        print(f"   Account Active: {user_info['is_active']}")
        print(f"   Email Verified: {user_info.get('email_verified', 'N/A')}")
        if 'created_at' in user_info:
            print(f"   Created: {user_info['created_at']}")
        if 'reset_date' in user_info:
            print(f"   Reset Date: {user_info.get('reset_date', 'N/A')}")
    
    # Get profiles
    print(f"\n📋 Getting user profiles...")
    profiles = get_user_profiles(token)
    
    if profiles:
        print(f"✅ Found {len(profiles)} profiles:")
        for i, profile in enumerate(profiles, 1):
            print(f"   {i}. {profile['profile_name']}")
            print(f"      ID: {profile['id']}")
            print(f"      Default: {profile['is_default']}")
            print(f"      Active: {profile['is_active']}")
            print(f"      Created: {profile['created_at']}")
    
    # Get applications
    print(f"\n📝 Getting user applications...")
    applications = get_user_applications(token)
    
    if applications:
        print(f"✅ Found {len(applications)} applications:")
        for i, app in enumerate(applications, 1):
            print(f"   {i}. {app.get('job_title', 'Unknown Job')}")
            print(f"      Company: {app.get('company_name', 'Unknown Company')}")
            print(f"      Status: {app['status']}")
            print(f"      URL: {app['job_url']}")
            print(f"      Created: {app['created_at']}")
    else:
        print("ℹ️ No applications found")
    
    print(f"\n📊 Summary:")
    print(f"   User: {user_info['name'] if user_info else 'Unknown'}")
    print(f"   Profiles: {len(profiles) if profiles else 0}")
    print(f"   Applications: {len(applications) if applications else 0}")
    print(f"   API Docs: http://localhost:8003/docs")

if __name__ == "__main__":
    main()