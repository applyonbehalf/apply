# api/profiles.py  
from fastapi import APIRouter, Depends, HTTPException, status
from auth.auth_middleware import get_current_active_user
from database.models import UserResponse, ProfileCreate, ProfileResponse, ProfileUpdate
from database.connection import db
from typing import List
import uuid

router = APIRouter()

@router.get("/", response_model=List[ProfileResponse])
async def get_user_profiles(current_user: UserResponse = Depends(get_current_active_user)):
    """Get all profiles for current user"""
    profiles = await db.get_user_profiles(current_user.id)
    return [ProfileResponse(**profile) for profile in profiles]

@router.post("/", response_model=ProfileResponse)
async def create_profile(
    profile_data: ProfileCreate,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Create a new profile"""
    new_profile = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.id,
        **profile_data.dict()
    }
    
    created_profile = await db.create_profile(new_profile)
    if not created_profile:
        raise HTTPException(status_code=500, detail="Failed to create profile")
    
    return ProfileResponse(**created_profile)