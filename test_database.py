# test_database.py
# Run this to test your Supabase connection

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def test_database_connection():
    """Test the database connection and basic operations"""
    
    try:
        # Create Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("✅ Supabase client created successfully")
        
        # Test 1: Read users
        users_response = supabase.table('users').select('*').execute()
        print(f"✅ Found {len(users_response.data)} users in database")
        
        for user in users_response.data:
            print(f"   - {user['name']} ({user['email']}) - {user['subscription_plan']}")
        
        # Test 2: Read user profiles
        profiles_response = supabase.table('user_profiles').select('*').execute()
        print(f"✅ Found {len(profiles_response.data)} user profiles")
        
        for profile in profiles_response.data:
            print(f"   - {profile['profile_name']} for user {profile['user_id']}")
        
        # Test 3: Create a test job application
        test_application = {
            'user_id': users_response.data[0]['id'],
            'profile_id': profiles_response.data[0]['id'],
            'job_url': 'https://example.com/test-job',
            'job_title': 'Test Software Engineer',
            'company_name': 'Test Company',
            'status': 'queued'
        }
        
        app_response = supabase.table('job_applications').insert(test_application).execute()
        print(f"✅ Created test job application: {app_response.data[0]['id']}")
        
        # Test 4: Query the queued applications
        queued_apps = supabase.table('job_applications').select('*').eq('status', 'queued').execute()
        print(f"✅ Found {len(queued_apps.data)} queued applications")
        
        # Test 5: Test the custom function
        next_app = supabase.rpc('get_next_queued_application').execute()
        if next_app.data:
            print(f"✅ Next queued application: {next_app.data[0]['job_url']}")
        else:
            print("ℹ️ No queued applications found")
        
        # Clean up: Delete the test application
        supabase.table('job_applications').delete().eq('job_url', 'https://example.com/test-job').execute()
        print("✅ Cleaned up test data")
        
        print("\n🎉 All database tests passed! Your setup is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # First, install required packages
    print("Installing required packages...")
    os.system("pip install supabase python-dotenv")
    
    print("\n" + "="*50)
    print("Testing IntelliApply Database Connection")
    print("="*50)
    
    # Check environment variables
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("❌ Missing environment variables!")
        print("Please create a .env file with:")
        print("SUPABASE_URL=your_supabase_url")
        print("SUPABASE_SERVICE_KEY=your_service_key")
        exit(1)
    
    # Run the test
    success = test_database_connection()
    
    if success:
        print("\n✅ Ready to proceed to Day 2!")
    else:
        print("\n❌ Please fix the issues above before continuing.")