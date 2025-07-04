# fix_backend_datetime.py - Fix backend datetime serialization
import os
import json
from datetime import datetime

def fix_backend_datetime_issues():
    """Fix datetime serialization issues in backend"""
    
    print("🔧 Fixing Backend DateTime Issues")
    print("=" * 40)
    
    # Fix the profile API endpoint
    profiles_api_path = "backend/api/profiles.py"
    
    if os.path.exists(profiles_api_path):
        print(f"📁 Fixing {profiles_api_path}")
        
        # Read current content
        with open(profiles_api_path, 'r') as f:
            content = f.read()
        
        # Create backup
        with open(f"{profiles_api_path}.backup", 'w') as f:
            f.write(content)
        
        # Updated profiles.py with proper datetime handling
        new_content = '''# api/profiles.py - Fixed version with datetime handling
from fastapi import APIRouter, Depends, HTTPException, status
from auth.auth_middleware import get_current_active_user
from database.models import UserResponse, ProfileCreate, ProfileResponse, ProfileUpdate
from database.connection import db
from typing import List
import uuid
from datetime import datetime
import json

router = APIRouter()

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
    """Create a new profile"""
    try:
        # Convert profile data to dict and handle datetime serialization
        profile_dict = profile_data.dict()
        
        # Serialize any datetime objects in profile_data
        profile_dict['profile_data'] = serialize_datetime(profile_dict['profile_data'])
        
        new_profile = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "is_active": True,
            **profile_dict
        }
        
        created_profile = await db.create_profile(new_profile)
        if not created_profile:
            raise HTTPException(status_code=500, detail="Failed to create profile")
        
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
    """Update a profile"""
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
        
        updated_profile = await db.update_profile(profile_id, update_data)
        if not updated_profile:
            raise HTTPException(status_code=500, detail="Failed to update profile")
        
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
'''
        
        # Write the fixed content
        with open(profiles_api_path, 'w') as f:
            f.write(new_content)
        
        print(f"✅ Fixed {profiles_api_path}")
    else:
        print(f"❌ File not found: {profiles_api_path}")
        return False
    
    return True

def test_server_restart():
    """Test if we need to restart the server"""
    import requests
    
    try:
        response = requests.get("http://localhost:8003/health", timeout=5)
        if response.status_code == 200:
            print("ℹ️ Server is running. You'll need to restart it for changes to take effect.")
            return True
    except:
        print("ℹ️ Server appears to be stopped.")
        return False

def main():
    """Main function"""
    print("🔧 IntelliApply Backend DateTime Fix")
    print("=" * 50)
    
    if fix_backend_datetime_issues():
        print("\n✅ Backend datetime issues fixed!")
        
        if test_server_restart():
            print("\n⚠️ IMPORTANT: You need to restart the server!")
            print("\nSteps:")
            print("1. Press Ctrl+C to stop the current server")
            print("2. Run: python quick_fix_and_test.py")
            print("3. The profile creation should now work")
        else:
            print("\n🎯 Ready to test!")
            print("Run: python quick_fix_and_test.py")
    else:
        print("\n❌ Failed to fix backend issues")

if __name__ == "__main__":
    main()