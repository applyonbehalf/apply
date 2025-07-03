# simple_test.py
# Let's test each component step by step

def test_imports():
    """Test if all imports work"""
    print("🧪 Testing imports...")
    
    try:
        print("1. Testing basic imports...")
        import os
        from dotenv import load_dotenv
        load_dotenv()
        print("   ✅ Basic imports OK")
        
        print("2. Testing FastAPI...")
        from fastapi import FastAPI
        print("   ✅ FastAPI import OK")
        
        print("3. Testing Supabase...")
        from supabase import create_client
        print("   ✅ Supabase import OK")
        
        print("4. Testing config...")
        try:
            from config import settings
            print(f"   ✅ Config OK - Supabase URL: {settings.supabase_url[:30]}...")
        except Exception as e:
            print(f"   ❌ Config error: {e}")
            return False
        
        print("5. Testing database connection...")
        try:
            from database.connection import db
            print("   ✅ Database connection OK")
        except Exception as e:
            print(f"   ❌ Database connection error: {e}")
            return False
        
        print("6. Testing models...")
        try:
            from database.models import UserCreate, UserResponse
            print("   ✅ Models OK")
        except Exception as e:
            print(f"   ❌ Models error: {e}")
            return False
        
        print("7. Testing auth...")
        try:
            from auth.jwt_handler import JWTHandler
            from auth.auth_middleware import get_current_user
            print("   ✅ Auth OK")
        except Exception as e:
            print(f"   ❌ Auth error: {e}")
            return False
            
        print("8. Testing API modules...")
        try:
            from api import auth
            print("   ✅ Auth API OK")
        except Exception as e:
            print(f"   ❌ Auth API error: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_simple_fastapi():
    """Test a simple FastAPI app"""
    print("\n🚀 Testing simple FastAPI app...")
    
    try:
        from fastapi import FastAPI
        import uvicorn
        import threading
        import time
        import requests
        
        # Create simple app
        app = FastAPI()
        
        @app.get("/test")
        def test_endpoint():
            return {"message": "test working"}
        
        # Start server in thread
        def run_server():
            uvicorn.run(app, host="localhost", port=8001, log_level="critical")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait and test
        time.sleep(2)
        response = requests.get("http://localhost:8001/test")
        
        if response.status_code == 200:
            print("   ✅ Simple FastAPI app works")
            return True
        else:
            print(f"   ❌ Simple app failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Simple FastAPI test failed: {e}")
        return False

def test_database_direct():
    """Test database connection directly"""
    print("\n🗄️ Testing database connection...")
    
    try:
        import os
        from supabase import create_client
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not supabase_url or not supabase_key:
            print("   ❌ Missing Supabase credentials in .env")
            return False
        
        client = create_client(supabase_url, supabase_key)
        
        # Test query
        response = client.table('users').select('count').execute()
        print("   ✅ Database connection works")
        return True
        
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 IntelliApply Backend Diagnostic Test")
    print("=" * 50)
    
    # Test each component
    imports_ok = test_imports()
    
    if imports_ok:
        print("\n✅ All imports successful!")
        
        fastapi_ok = test_simple_fastapi()
        db_ok = test_database_direct()
        
        if fastapi_ok and db_ok:
            print("\n🎉 All tests passed! Your backend should work.")
            print("Try running: python -m uvicorn main:app --reload")
        else:
            print("\n⚠️ Some tests failed, but imports work.")
    else:
        print("\n❌ Import issues found. Let's fix them first.")