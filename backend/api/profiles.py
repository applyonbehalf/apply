# api/profiles.py - Complete fixed version with job category support
from fastapi import APIRouter, Depends, HTTPException, status
from auth.auth_middleware import get_current_active_user
from database.connection import db
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import json
from pydantic import BaseModel, Field

router = APIRouter()

# Updated models with preferred_job_category_id support
class ProfileData(BaseModel):
    personal_info: Dict[str, Any] = Field(..., description="Personal information")
    experience: Optional[Dict[str, Any]] = Field(None, description="Experience information")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Work preferences")
    eligibility: Optional[Dict[str, Any]] = Field(None, description="Work eligibility")
    document_paths: Optional[Dict[str, Any]] = Field(None, description="Document file paths")
    skills: Optional[Dict[str, Any]] = Field(None, description="Skills and certifications")
    education: Optional[List[Dict[str, Any]]] = Field(None, description="Education history")
    employment_history: Optional[List[Dict[str, Any]]] = Field(None, description="Employment history")

class ProfileCreate(BaseModel):
    profile_name: str = Field(..., min_length=1, max_length=100)
    profile_data: ProfileData
    resume_url: Optional[str] = None
    cover_letter_template: Optional[str] = None
    preferred_job_category_id: Optional[str] = None  # Added for job category preference
    is_default: bool = False

class ProfileUpdate(BaseModel):
    profile_name: Optional[str] = None
    profile_data: Optional[ProfileData] = None
    resume_url: Optional[str] = None
    cover_letter_template: Optional[str] = None
    preferred_job_category_id: Optional[str] = None  # Added for job category preference
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None

class ProfileResponse(BaseModel):
    id: str
    user_id: str
    profile_name: str
    profile_data: ProfileData
    resume_url: Optional[str]
    cover_letter_template: Optional[str]
    preferred_job_category_id: Optional[str] = None  # Added for job category preference
    is_default: bool
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class UserResponse(BaseModel):
    id: str
    email: str
    name: str

def serialize_datetime(obj):
    """Custom JSON serializer for datetime objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: serialize_datetime(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetime(item) for item in obj]
    else:
        return obj

@router.get("/", response_model=List[ProfileResponse])
async def get_user_profiles(current_user: UserResponse = Depends(get_current_active_user)):
    """Get all profiles for current user"""
    try:
        profiles = await db.get_user_profiles(current_user.id)
        
        # Serialize datetime objects
        serialized_profiles = []
        for profile in profiles:
            serialized_profile = serialize_datetime(profile)
            serialized_profiles.append(ProfileResponse(**serialized_profile))
        
        return serialized_profiles
    except Exception as e:
        print(f"Error getting user profiles: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get profiles: {str(e)}")

@router.post("/", response_model=ProfileResponse)
async def create_profile(
    profile_data: ProfileCreate,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Create a new profile with job category preference support"""
    try:
        # Convert profile data to dict and handle datetime serialization
        profile_dict = profile_data.dict()
        
        # Serialize any datetime objects in profile_data
        profile_dict['profile_data'] = serialize_datetime(profile_dict['profile_data'])
        
        new_profile = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "profile_name": profile_dict['profile_name'],
            "profile_data": profile_dict['profile_data'],
            "resume_url": profile_dict.get('resume_url'),
            "cover_letter_template": profile_dict.get('cover_letter_template'),
            "preferred_job_category_id": profile_dict.get('preferred_job_category_id'),  # This is the key field!
            "is_default": profile_dict.get('is_default', False),
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        print(f"Creating profile with job category: {new_profile.get('preferred_job_category_id')}")
        
        created_profile = await db.create_profile(new_profile)
        if not created_profile:
            raise HTTPException(status_code=500, detail="Failed to create profile")
        
        print(f"Profile created successfully with ID: {created_profile.get('id')}")
        
        # Serialize the response
        serialized_profile = serialize_datetime(created_profile)
        return ProfileResponse(**serialized_profile)
        
    except Exception as e:
        print(f"Error creating profile: {e}")
        raise HTTPException(status_code=500, detail=f"Profile creation failed: {str(e)}")

@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: str,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get a specific profile"""
    try:
        profile = await db.get_profile_by_id(profile_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Check if user owns this profile
        if profile['user_id'] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        serialized_profile = serialize_datetime(profile)
        return ProfileResponse(**serialized_profile)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")

@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: str,
    profile_update: ProfileUpdate,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Update a profile with job category preference support"""
    try:
        # Check if profile exists and user owns it
        existing_profile = await db.get_profile_by_id(profile_id)
        if not existing_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        if existing_profile['user_id'] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Prepare update data
        update_data = profile_update.dict(exclude_unset=True)
        if 'profile_data' in update_data:
            update_data['profile_data'] = serialize_datetime(update_data['profile_data'])
        
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        print(f"Updating profile {profile_id} with job category: {update_data.get('preferred_job_category_id')}")
        
        updated_profile = await db.update_profile(profile_id, update_data)
        if not updated_profile:
            raise HTTPException(status_code=500, detail="Failed to update profile")
        
        print(f"Profile updated successfully")
        
        serialized_profile = serialize_datetime(updated_profile)
        return ProfileResponse(**serialized_profile)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@router.delete("/{profile_id}")
async def delete_profile(
    profile_id: str,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Delete a profile"""
    try:
        # Check if profile exists and user owns it
        existing_profile = await db.get_profile_by_id(profile_id)
        if not existing_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        if existing_profile['user_id'] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = await db.delete_profile(profile_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete profile")
        
        return {"message": "Profile deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete profile: {str(e)}")

@router.get("/test/job-categories")
async def test_profile_job_categories(current_user: UserResponse = Depends(get_current_active_user)):
    """Test endpoint to check job category preferences"""
    try:
        profiles = await db.get_user_profiles(current_user.id)
        
        result = []
        for profile in profiles:
            result.append({
                "profile_id": profile.get('id'),
                "profile_name": profile.get('profile_name'),
                "preferred_job_category_id": profile.get('preferred_job_category_id'),
                "is_active": profile.get('is_active'),
                "is_default": profile.get('is_default')
            })
        
        return {
            "user_id": current_user.id,
            "user_email": current_user.email,
            "profiles": result
        }
        
    except Exception as e:
        print(f"Error in test endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")