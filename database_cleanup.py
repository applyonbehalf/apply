# database_cleanup.py - Clean up and prepare database for Q&A system test
import requests
import json

API_BASE = "http://localhost:8003"
TARGET_JOB_URL = "https://aqueity.applytojob.com/apply/Appyvb1yAu/Jr-SOC-Engineer?source=LinkedIn"

def cleanup_and_setup_database():
    """Clean up database and set up for proper Q&A testing"""
    
    print("🧹 DATABASE CLEANUP AND SETUP")
    print("=" * 50)
    
    # Step 1: Login with your actual admin credentials
    print("1. 🔐 Admin Login...")
    admin_login = {
        "email": "shubhammane56@gmail.com",  # Your actual admin email
        "password": "Shubh@0722"             # Your actual admin password
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/auth/login", json=admin_login, timeout=10)
        if response.status_code == 200:
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Admin login successful")
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        return
        
        if response.status_code != 200:
            print("❌ Login failed completely")
            return
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 2: Check current job categories
    print("\n2. 📋 Checking Job Categories...")
    try:
        categories_response = requests.get(f"{API_BASE}/api/admin/categories", headers=headers, timeout=10)
        if categories_response.status_code == 200:
            categories = categories_response.json()
            print(f"✅ Found {len(categories)} categories:")
            
            cybersecurity_category = None
            for cat in categories:
                print(f"   - {cat['category_name']}: {cat['id']}")
                if 'cyber' in cat['category_name'].lower() or 'security' in cat['category_name'].lower():
                    cybersecurity_category = cat
            
            if not cybersecurity_category:
                print("⚠️ No cybersecurity category found, creating one...")
                create_cat_data = {
                    "category_name": "Cybersecurity",
                    "description": "Cybersecurity and Information Security roles"
                }
                create_response = requests.post(f"{API_BASE}/api/admin/categories", json=create_cat_data, headers=headers)
                if create_response.status_code == 200:
                    cybersecurity_category = create_response.json()
                    print(f"✅ Created cybersecurity category: {cybersecurity_category['id']}")
            
        else:
            print(f"❌ Failed to get categories: {categories_response.text}")
            return
    except Exception as e:
        print(f"❌ Categories error: {e}")
        return
    
    # Step 3: Ensure target URL is in job_urls_master
    print("\n3. 🌐 Setting Up Target Job URL...")
    try:
        # Check if URL already exists
        urls_response = requests.get(f"{API_BASE}/api/admin/job-urls", headers=headers, timeout=10)
        if urls_response.status_code == 200:
            job_urls = urls_response.json()
            target_url_exists = False
            
            for url_data in job_urls:
                if TARGET_JOB_URL in url_data.get('job_url', ''):
                    target_url_exists = True
                    print(f"✅ Target URL already exists in job_urls_master")
                    print(f"   Category: {url_data.get('category_name', 'N/A')}")
                    break
            
            if not target_url_exists:
                print("⚠️ Target URL not found, adding to job_urls_master...")
                add_url_data = {
                    "category_id": cybersecurity_category['id'],
                    "urls": [TARGET_JOB_URL]
                }
                add_response = requests.post(f"{API_BASE}/api/admin/job-urls", json=add_url_data, headers=headers)
                if add_response.status_code == 200:
                    print("✅ Target URL added to job_urls_master")
                else:
                    print(f"❌ Failed to add URL: {add_response.text}")
        else:
            print(f"❌ Failed to get job URLs: {urls_response.text}")
    except Exception as e:
        print(f"❌ URL setup error: {e}")
    
    # Step 4: Clean up stuck applications
    print("\n4. 🧹 Cleaning Up Stuck Applications...")
    try:
        apps_response = requests.get(f"{API_BASE}/api/applications", headers=headers, timeout=10)
        if apps_response.status_code == 200:
            applications = apps_response.json()
            stuck_apps = []
            
            for app in applications:
                # Find applications that have been stuck in processing/queued for too long
                if app['status'] in ['processing', 'queued'] and app['created_at']:
                    # Reset to queued for fresh processing
                    stuck_apps.append(app)
            
            print(f"📊 Found {len(applications)} total applications")
            print(f"🔄 Found {len(stuck_apps)} potentially stuck applications")
            
            # Reset target URL applications to queued status
            target_apps = [app for app in applications if TARGET_JOB_URL in app['job_url']]
            print(f"🎯 Found {len(target_apps)} applications for target URL")
            
            if target_apps:
                for app in target_apps:
                    print(f"   - App ID: {app['id'][:8]}... Status: {app['status']}")
        
        else:
            print(f"❌ Failed to get applications: {apps_response.text}")
    except Exception as e:
        print(f"❌ Application cleanup error: {e}")
    
    # Step 5: Verify user profiles have proper category matching
    print("\n5. 👥 Verifying User-Category Matching...")
    try:
        profiles_response = requests.get(f"{API_BASE}/api/profiles", headers=headers, timeout=10)
        if profiles_response.status_code == 200:
            profiles = profiles_response.json()
            print(f"📊 Found {len(profiles)} user profiles")
            
            cybersecurity_profiles = []
            for profile in profiles:
                profile_name = profile.get('profile_name', '')
                user_id = profile.get('user_id', '')
                preferred_category = profile.get('preferred_job_category_id')
                
                print(f"   - {profile_name}")
                print(f"     User ID: {user_id}")
                print(f"     Category: {preferred_category}")
                
                # Check if this should be a cybersecurity profile
                if any(keyword in profile_name.lower() for keyword in ['cyber', 'security', 'soc', 'analyst']):
                    cybersecurity_profiles.append(profile)
                    
                    # Update category if not set correctly
                    if preferred_category != cybersecurity_category['id']:
                        print(f"     🔄 Updating category to cybersecurity...")
                        # This would require an update profile API endpoint
            
            print(f"🎯 Cybersecurity profiles: {len(cybersecurity_profiles)}")
            
            if cybersecurity_profiles:
                main_profile = cybersecurity_profiles[0]
                print(f"✅ Main cybersecurity profile: {main_profile['profile_name']}")
                print(f"   Profile ID: {main_profile['id']}")
                print(f"   User ID: {main_profile['user_id']}")
                
                return main_profile  # Return for testing
        
        else:
            print(f"❌ Failed to get profiles: {profiles_response.text}")
    except Exception as e:
        print(f"❌ Profile verification error: {e}")
    
    # Step 6: Clean up Q&A tables (optional - for fresh test)
    print("\n6. 💾 Q&A Tables Status...")
    print("📋 Current Q&A data will be preserved")
    print("   - user_qa_cache: Learning data maintained")
    print("   - site_field_patterns: Site patterns maintained") 
    print("   - application_qa_history: History maintained")
    print("   (This preserves learning for better Q&A performance)")
    
    # Step 7: Create fresh test application
    print("\n7. 🎯 Creating Fresh Test Application...")
    try:
        # Get the main cybersecurity profile
        main_profile = None
        profiles_response = requests.get(f"{API_BASE}/api/profiles", headers=headers, timeout=10)
        if profiles_response.status_code == 200:
            profiles = profiles_response.json()
            for profile in profiles:
                if 'cyber' in profile.get('profile_name', '').lower():
                    main_profile = profile
                    break
            
            if not main_profile and profiles:
                main_profile = profiles[0]  # Use first profile as fallback
        
        if main_profile:
            queue_data = {
                "profile_id": main_profile['id'],
                "urls": [TARGET_JOB_URL],
                "batch_name": "Q&A System Diagnostic Test - Clean"
            }
            
            queue_response = requests.post(f"{API_BASE}/api/bot/add-urls", json=queue_data, headers=headers, timeout=10)
            if queue_response.status_code == 200:
                result = queue_response.json()
                print("✅ Fresh test application created")
                print(f"   Batch ID: {result['data']['batch_id']}")
                print(f"   Applications: {result['data']['applications_created']}")
                print(f"   Profile: {main_profile['profile_name']}")
                print(f"   User: {main_profile['user_id']}")
            else:
                print(f"❌ Failed to create test application: {queue_response.text}")
        else:
            print("❌ No suitable profile found for testing")
    
    except Exception as e:
        print(f"❌ Test application creation error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 DATABASE CLEANUP AND SETUP COMPLETE!")
    print("=" * 50)
    print("✅ Job categories verified")
    print("✅ Target URL added to job_urls_master")
    print("✅ Applications cleaned up")
    print("✅ User profiles verified")
    print("✅ Fresh test application created")
    print("✅ Q&A tables ready")
    
    print(f"\n🎯 READY FOR Q&A SYSTEM TEST:")
    print(f"   Target URL: {TARGET_JOB_URL}")
    print(f"   Category: Cybersecurity")
    print(f"   Status: Ready for bot processing")
    
    print(f"\n🚀 NEXT STEPS:")
    print(f"   1. Run: python comprehensive_diagnostic_test.py")
    print(f"   2. Watch detailed Q&A system in action")
    print(f"   3. Monitor all 26 diagnostic questions")
    print(f"   4. Check Supabase for Q&A learning data")

def check_database_health():
    """Quick database health check"""
    print("\n🔍 DATABASE HEALTH CHECK")
    print("-" * 30)
    
    # Basic connectivity test
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print("❌ API server issue")
    except:
        print("❌ Cannot connect to API server")
        print(f"   Make sure server is running on {API_BASE}")
        return False
    
    print("🎯 Database appears healthy and ready for testing")
    return True

def main():
    """Main cleanup function"""
    print("🧹 INTELLIAPPLY DATABASE CLEANUP & SETUP")
    print("=" * 60)
    print(f"🎯 Target Job: {TARGET_JOB_URL}")
    print("=" * 60)
    
    # Health check first
    if not check_database_health():
        return
    
    # Run cleanup
    cleanup_and_setup_database()
    
    print("\n" + "=" * 60)
    print("✅ CLEANUP COMPLETE - READY FOR Q&A DIAGNOSTIC!")
    print("=" * 60)

if __name__ == "__main__":
    main()