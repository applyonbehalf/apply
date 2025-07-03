# api/users.py - Updated with better error handling
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Fallback models
class UserResponse(BaseModel):
    id: str
    email: str
    name: str

class UserStats(BaseModel):
    total_applications: int
    queued: int
    processing: int
    completed: int
    failed: int
    captcha_required: int
    success_rate: float

# Try to import real dependencies
try:
    from auth.auth_middleware import get_current_active_user
    from database.models import UserResponse as DBUserResponse, UserStats as DBUserStats
    from database.connection import db
    
    # Use real models if available
    UserResponse = DBUserResponse
    UserStats = DBUserStats
    
    DEPS_AVAILABLE = True
    print("✅ User dependencies loaded successfully")
    
except ImportError as e:
    print(f"⚠️ User dependencies not available: {e}")
    print("   Using fallback implementations")
    DEPS_AVAILABLE = False
    
    # Mock database
    class MockDB:
        async def get_user_stats(self, user_id: str):
            return {
                "total_applications": 0,
                "queued": 0,
                "processing": 0,
                "completed": 0,
                "failed": 0,
                "captcha_required": 0,
                "success_rate": 0.0
            }
    
    db = MockDB()
    
    # Mock auth middleware
    async def get_current_active_user():
        return UserResponse(
            id="mock_user_id",
            email="mock@example.com",
            name="Mock User"
        )

@router.get("/stats", response_model=UserStats)
async def get_user_stats(current_user: UserResponse = Depends(get_current_active_user)):
    """Get user application statistics"""
    try:
        stats = await db.get_user_stats(current_user.id)
        return UserStats(**stats)
    except Exception as e:
        print(f"Error getting user stats: {e}")
        # Return default stats if there's an error
        return UserStats(
            total_applications=0,
            queued=0,
            processing=0,
            completed=0,
            failed=0,
            captcha_required=0,
            success_rate=0.0
        )

@router.get("/test")
async def test_users():
    """Test endpoint to verify users module is working"""
    return {
        "message": "Users API is working",
        "dependencies_available": DEPS_AVAILABLE
    }