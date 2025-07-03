# test_api_diagnostic.py - Complete diagnostic testing script
import requests
import time
import threading
import subprocess
import os
import sys
import socket
import signal
from datetime import datetime

def find_free_port(start_port=8001):
    """Find a free port starting from start_port"""
    for port in range(start_port, start_port + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free ports found")

class ServerManager:
    def __init__(self):
        self.process = None
        self.port = None
        self.api_base = None
    
    def start_server(self):
        """Start the FastAPI server with better process management"""
        try:
            # Find free port
            self.port = find_free_port()
            self.api_base = f"http://localhost:{self.port}"
            
            print(f"🌐 Starting server on port {self.port}")
            
            # Change to backend directory
            os.chdir('backend')
            
            # Start server process
            self.process = subprocess.Popen([
                sys.executable, '-m', 'uvicorn', 
                'main:app', 
                '--host', '0.0.0.0', 
                '--port', str(self.port),
                '--log-level', 'info'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            print(f"✅ Server process started with PID: {self.process.pid}")
            return True
            
        except Exception as e:
            print(f"❌ Server start error: {e}")
            return False
    
    def check_server_status(self):
        """Check if server process is running"""
        if self.process:
            return self.process.poll() is None
        return False
    
    def get_server_output(self):
        """Get server output for debugging"""
        if self.process:
            try:
                stdout, stderr = self.process.communicate(timeout=1)
                return stdout, stderr
            except subprocess.TimeoutExpired:
                return "Process still running", "Process still running"
        return "No process", "No process"
    
    def stop_server(self):
        """Stop the server process"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                print(f"✅ Server stopped")
            except subprocess.TimeoutExpired:
                self.process.kill()
                print(f"⚠️ Server force killed")
            except Exception as e:
                print(f"⚠️ Error stopping server: {e}")

def check_server_ready(api_base, max_attempts=60, verbose=True):
    """Check if server is ready with detailed logging"""
    print(f"🔍 Checking server readiness at {api_base}")
    
    for attempt in range(max_attempts):
        try:
            if verbose and attempt % 5 == 0:
                print(f"   Attempt {attempt + 1}/{max_attempts}...")
            
            response = requests.get(f"{api_base}/health", timeout=3)
            
            if response.status_code == 200:
                print(f"✅ Server is ready! (attempt {attempt + 1})")
                return True
            else:
                if verbose:
                    print(f"   Got status {response.status_code}, retrying...")
                    
        except requests.exceptions.ConnectionError:
            if verbose and attempt % 10 == 0:
                print(f"   Connection refused, server may still be starting...")
        except requests.exceptions.Timeout:
            if verbose:
                print(f"   Request timeout, server may be overloaded...")
        except Exception as e:
            if verbose and attempt % 10 == 0:
                print(f"   Unexpected error: {e}")
        
        time.sleep(1)
    
    print(f"❌ Server failed to respond after {max_attempts} seconds")
    return False

def test_basic_connectivity():
    """Test basic server connectivity with detailed diagnostics"""
    print("🔧 Starting Diagnostic Test")
    print("=" * 50)
    
    # Check pre-requisites
    if not os.path.exists('backend'):
        print("❌ Error: 'backend' directory not found.")
        return False
    
    if not os.path.exists('backend/main.py'):
        print("❌ Error: 'backend/main.py' not found.")
        return False
    
    original_dir = os.getcwd()
    server_manager = ServerManager()
    
    try:
        # Start server
        if not server_manager.start_server():
            return False
        
        # Wait a bit for server to initialize
        print("⏳ Waiting for server initialization...")
        time.sleep(5)
        
        # Check if process is still running
        if not server_manager.check_server_status():
            print("❌ Server process died unexpectedly")
            stdout, stderr = server_manager.get_server_output()
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
        
        print("✅ Server process is running")
        
        # Test connectivity with longer timeout
        if not check_server_ready(server_manager.api_base, max_attempts=60, verbose=True):
            print("❌ Server failed health check")
            
            # Try to get server logs
            print("\n🔍 Server diagnostics:")
            if server_manager.check_server_status():
                print("   - Process is still running")
            else:
                print("   - Process has died")
                stdout, stderr = server_manager.get_server_output()
                print(f"   - STDOUT: {stdout[:500]}")
                print(f"   - STDERR: {stderr[:500]}")
            
            # Try manual connection test
            print(f"\n🔧 Manual connection test to {server_manager.api_base}")
            try:
                response = requests.get(f"{server_manager.api_base}/health", timeout=10)
                print(f"   - Status: {response.status_code}")
                print(f"   - Response: {response.text[:200]}")
            except Exception as e:
                print(f"   - Connection error: {e}")
            
            return False
        
        # Server is ready, run basic tests
        print("\n🧪 Running basic API tests...")
        
        test_results = {}
        
        # Test 1: Health check
        try:
            response = requests.get(f"{server_manager.api_base}/health", timeout=5)
            test_results['health'] = response.status_code == 200
            if test_results['health']:
                print("✅ Health check: PASSED")
            else:
                print(f"❌ Health check: FAILED ({response.status_code})")
        except Exception as e:
            test_results['health'] = False
            print(f"❌ Health check: ERROR ({e})")
        
        # Test 2: Root endpoint
        try:
            response = requests.get(f"{server_manager.api_base}/", timeout=5)
            test_results['root'] = response.status_code == 200
            if test_results['root']:
                print("✅ Root endpoint: PASSED")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Root endpoint: FAILED ({response.status_code})")
        except Exception as e:
            test_results['root'] = False
            print(f"❌ Root endpoint: ERROR ({e})")
        
        # Test 3: API docs
        try:
            response = requests.get(f"{server_manager.api_base}/docs", timeout=5)
            test_results['docs'] = response.status_code == 200
            if test_results['docs']:
                print("✅ API docs: PASSED")
            else:
                print(f"❌ API docs: FAILED ({response.status_code})")
        except Exception as e:
            test_results['docs'] = False
            print(f"❌ API docs: ERROR ({e})")
        
        # Test 4: Test endpoints
        test_endpoints = [
            'auth', 'users', 'profiles', 'applications', 'batches', 'captcha', 'bot'
        ]
        
        for endpoint in test_endpoints:
            try:
                response = requests.get(f"{server_manager.api_base}/api/{endpoint}/test", timeout=5)
                test_results[endpoint] = response.status_code == 200
                if test_results[endpoint]:
                    print(f"✅ {endpoint.capitalize()} API: PASSED")
                else:
                    print(f"❌ {endpoint.capitalize()} API: FAILED ({response.status_code})")
            except Exception as e:
                test_results[endpoint] = False
                print(f"❌ {endpoint.capitalize()} API: ERROR ({e})")
        
        # Summary
        passed = sum(test_results.values())
        total = len(test_results)
        success_rate = (passed / total) * 100
        
        print(f"\n📊 Test Results: {passed}/{total} passed ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 API is working well!")
            
            # Interactive mode
            print(f"\n🌐 Server is running at: {server_manager.api_base}")
            print(f"📖 API Documentation: {server_manager.api_base}/docs")
            print("\n⚡ You can now:")
            print("   1. Visit the API docs in your browser")
            print("   2. Test endpoints manually")
            print("   3. Run the authentication test: python test_auth.py")
            print("   4. Run the full test suite")
            print("\nPress Ctrl+C to stop the server")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Stopping server...")
                return True
        else:
            print("⚠️ API has issues that need to be resolved")
            return False
    
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
        return True
    except Exception as e:
        print(f"❌ Diagnostic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        os.chdir(original_dir)
        server_manager.stop_server()

def run_comprehensive_test():
    """Run comprehensive API test"""
    print("🧪 Running Comprehensive API Test")
    print("=" * 50)
    
    # Find free port for testing
    port = find_free_port()
    api_base = f"http://localhost:{port}"
    
    print(f"🌐 Testing API at: {api_base}")
    
    try:
        # Wait for server to be ready
        if not check_server_ready(api_base, max_attempts=30, verbose=False):
            print("❌ Server not ready for comprehensive test")
            return False
        
        print("✅ Server is ready for comprehensive testing")
        
        # Test authentication flow
        print("\n🔐 Testing Authentication...")
        
        test_user = {
            "email": "comprehensive@test.com",
            "name": "Comprehensive Test User",
            "password": "testpassword123"
        }
        
        # Register user
        response = requests.post(f"{api_base}/api/auth/register", json=test_user, timeout=10)
        
        if response.status_code == 200:
            print("✅ User registration: PASSED")
            token_data = response.json()
            access_token = token_data.get("access_token")
        elif response.status_code == 400:
            # Try login
            response = requests.post(f"{api_base}/api/auth/login", json={
                "email": test_user["email"],
                "password": test_user["password"]
            }, timeout=10)
            
            if response.status_code == 200:
                print("✅ User login: PASSED")
                token_data = response.json()
                access_token = token_data.get("access_token")
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        if not access_token:
            print("❌ No access token received")
            return False
        
        print(f"🎟️ Access token received: {access_token[:20]}...")
        
        # Test protected endpoints
        headers = {"Authorization": f"Bearer {access_token}"}
        
        protected_endpoints = [
            ("auth/me", "Current User"),
            ("users/stats", "User Statistics"),
            ("profiles/", "User Profiles"),
            ("applications/", "Applications"),
            ("batches/", "Batches"),
            ("bot/status", "Bot Status")
        ]
        
        passed_protected = 0
        for endpoint, name in protected_endpoints:
            try:
                response = requests.get(f"{api_base}/api/{endpoint}", headers=headers, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {name}: PASSED")
                    passed_protected += 1
                else:
                    print(f"❌ {name}: FAILED ({response.status_code})")
            except Exception as e:
                print(f"❌ {name}: ERROR ({e})")
        
        # Final results
        total_protected = len(protected_endpoints)
        protected_success_rate = (passed_protected / total_protected) * 100
        
        print(f"\n📊 Protected Endpoints: {passed_protected}/{total_protected} passed ({protected_success_rate:.1f}%)")
        
        if protected_success_rate >= 80:
            print("🎉 Comprehensive test PASSED!")
            return True
        else:
            print("⚠️ Comprehensive test had issues")
            return False
        
    except Exception as e:
        print(f"❌ Comprehensive test failed: {e}")
        return False

def main():
    """Main diagnostic test"""
    print("🔍 IntelliApply API Diagnostic Test")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_basic_connectivity()
    
    if success:
        print("\n✅ Diagnostic test completed successfully!")
    else:
        print("\n❌ Diagnostic test found issues")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Check if all required dependencies are installed")
        print("   2. Verify your .env file has correct database credentials")
        print("   3. Make sure no other services are using the ports")
        print("   4. Check the server logs above for specific errors")
        print("   5. Try running: cd backend && python -m uvicorn main:app --reload")

if __name__ == "__main__":
    main()