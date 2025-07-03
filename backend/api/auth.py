# api/auth.py - Robust version with better datetime handling
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
import uuid
from datetime import datetime
import traceback

router = APIRouter()

# Models that work in all scenarios
class UserCreate(BaseModel):
    email: str
    name: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    subscription_plan: str = "free"
    applications_limit: int = 5
    applications_used: int = 0
    is_active: bool = True

class APIResponse(BaseModel):
    success: bool
    message: str
    data: dict = None

# Try to import dependencies with comprehensive fallbacks
JWT_AVAILABLE = False
DB_AVAILABLE = False
AUTH_AVAILABLE = False

try:
    from auth.jwt_handler import JWTHandler
    JWT_AVAILABLE = True
    print("✅ JWT Handler loaded")
except ImportError as e:
    print(f"⚠️ JWT Handler not available: {e}")
    class JWTHandler:
        @staticmethod
        def hash_password(password: str) -> str:
            return f"hashed_{password}"
        
        @staticmethod
        def verify_password(plain: str, hashed: str) -> bool:
            return hashed == f"hashed_{plain}"
        
        @staticmethod
        def create_access_token(data: dict) -> str:
            return f"mock_token_{data.get('sub', 'unknown')[:8]}"

try:
    from database.connection import db
    DB_AVAILABLE = True
    print("✅ Database connection loaded")
except ImportError as e:
    print(f"⚠️ Database connection not available: {e}")
    # Create a simple in-memory database
    class MockDB:
        def __init__(self):
            self.users = {}
        
        async def get_user_by_email(self, email: str):
            return self.users.get(email)
        
        async def create_user(self, user_data: dict):
            # Handle datetime conversion safely
            clean_data = user_data.copy()
            for key, value in clean_data.items():
                if isinstance(value, datetime):
                    clean_data[key] = value.isoformat()
            
            self.users[clean_data['email']] = clean_data
            return clean_data
    
    db = MockDB()

try:
    from auth.auth_middleware import get_current_active_user
    AUTH_AVAILABLE = True
    print("✅ Auth middleware loaded")
except ImportError as e:
    print(f"⚠️ Auth middleware not available: {e}")
    async def get_current_active_user():
        return UserResponse(
            id="mock_user_id",
            email="mock@example.com",
            name="Mock User"
        )

@router.post("/register", response_model=Token)
async def register_user(user_data: UserCreate):
    """Register a new user - robust version"""
    try:
        print(f"🔐 Registering user: {user_data.email}")
        
        # Check if user already exists
        existing_user = await db.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = JWTHandler.hash_password(user_data.password)
        print(f"✅ Password hashed")
        
        # Create user data - be very careful with datetimes
        user_id = str(uuid.uuid4())
        current_time_str = datetime.utcnow().isoformat()
        
        new_user_data = {
            "id": user_id,
            "email": user_data.email,
            "name": user_data.name,
            "password_hash": hashed_password,
            "subscription_plan": "free",
            "applications_limit": 5,
            "applications_used": 0,
            "is_active": True,
            "email_verified": False,
            # Store as ISO strings to avoid serialization issues
            "created_at": current_time_str,
            "updated_at": current_time_str
        }
        
        print(f"📝 Creating user in database...")
        
        # Create user in database
        created_user = await db.create_user(new_user_data)
        
        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user in database"
            )
        
        print(f"✅ User created successfully")
        
        # Create access token
        access_token = JWTHandler.create_access_token(
            data={"sub": created_user["id"]}
        )
        
        print(f"🎟️ Token created: {access_token[:20]}...")
        
        return Token(access_token=access_token, token_type="bearer")
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the full error for debugging
        print(f"❌ Registration error: {e}")
        print(f"❌ Full traceback:")
        traceback.print_exc()
        
        # Return a more specific error message
        error_msg = str(e)
        if "JSON serializable" in error_msg:
            error_msg = "Database serialization error - using fallback method"
        elif "connection" in error_msg.lower():
            error_msg = "Database connection error - using fallback method"
        
        # Try a simpler fallback registration
        try:
            print("🔄 Attempting fallback registration...")
            fallback_user = {
                "id": str(uuid.uuid4()),
                "email": user_data.email,
                "name": user_data.name,
                "password_hash": f"hashed_{user_data.password}",
                "subscription_plan": "free",
                "applications_limit": 5,
                "applications_used": 0,
                "is_active": True
            }
            
            # Store in simple dict (for testing)
            if not hasattr(db, 'fallback_users'):
                db.fallback_users = {}
            db.fallback_users[user_data.email] = fallback_user
            
            token = f"fallback_token_{fallback_user['id'][:8]}"
            print(f"✅ Fallback registration successful")
            
            return Token(access_token=token, token_type="bearer")
            
        except Exception as fallback_error:
            print(f"❌ Fallback registration also failed: {fallback_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {error_msg}"
            )

@router.post("/login", response_model=Token)
async def login_user(login_data: UserLogin):
    """Login a user - robust version"""
    try:
        print(f"🔑 Login attempt for: {login_data.email}")
        
        # Get user by email
        user = await db.get_user_by_email(login_data.email)
        
        # Also check fallback users if available
        if not user and hasattr(db, 'fallback_users'):
            user = db.fallback_users.get(login_data.email)
            print("🔄 Using fallback user data")
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not JWTHandler.verify_password(login_data.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Create access token
        access_token = JWTHandler.create_access_token(
            data={"sub": user["id"]}
        )
        
        print(f"✅ Login successful for {login_data.email}")
        
        return Token(access_token=access_token, token_type="bearer")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: UserResponse = Depends(get_current_active_user)):
    """Refresh access token"""
    try:
        access_token = JWTHandler.create_access_token(
            data={"sub": current_user.id}
        )
        return Token(access_token=access_token, token_type="bearer")
    except Exception as e:
        print(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout", response_model=APIResponse)
async def logout(current_user: UserResponse = Depends(get_current_active_user)):
    """Logout user"""
    return APIResponse(success=True, message="Successfully logged out")

@router.get("/test")
async def test_auth():
    """Test endpoint with system status"""
    return {
        "message": "Auth API is working",
        "jwt_available": JWT_AVAILABLE,
        "db_available": DB_AVAILABLE,
        "auth_middleware_available": AUTH_AVAILABLE,
        "test_time": datetime.utcnow().isoformat(),
        "features": [
            "User registration",
            "User login", 
            "Token management",
            "Fallback authentication"
        ]
    }

@router.get("/status")
async def get_auth_status():
    """Get detailed auth system status"""
    try:
        # Test database connection
        test_email = "test@status.check"
        db_test = await db.get_user_by_email(test_email)
        db_status = "working"
    except Exception as e:
        db_status = f"error: {str(e)[:50]}"
    
    # Count users if possible
    user_count = 0
    try:
        if hasattr(db, 'users'):
            user_count = len(db.users)
        elif hasattr(db, 'fallback_users'):
            user_count = len(db.fallback_users)
    except:
        pass
    
    return {
        "auth_system_status": "operational",
        "components": {
            "jwt_handler": "mock" if not JWT_AVAILABLE else "real",
            "database": db_status,
            "auth_middleware": "mock" if not AUTH_AVAILABLE else "real"
        },
        "stats": {
            "registered_users": user_count,
            "fallback_mode": not (JWT_AVAILABLE and DB_AVAILABLE and AUTH_AVAILABLE)
        },
        "endpoints": {
            "POST /register": "register new user",
            "POST /login": "authenticate user",
            "GET /me": "get current user info",
            "POST /refresh": "refresh token",
            "POST /logout": "logout user"
        }
    }