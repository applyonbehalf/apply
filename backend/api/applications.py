# api/applications.py - Updated with better error handling
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

router = APIRouter()

# Fallback models
class ApplicationCreate(BaseModel):
    profile_id: str
    job_url: str = Field(..., min_length=1)
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    job_location: Optional[str] = None
    priority: int = Field(0, ge=0, le=10)

class ApplicationResponse(BaseModel):
    id: str
    user_id: str
    profile_id: str
    batch_id: Optional[str]
    job_url: str
    job_title: Optional[str]
    company_name: Optional[str]
    job_location: Optional[str]
    status: str = "queued"
    priority: int
    application_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    submitted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    applications_limit: int = 5
    applications_used: int = 0

# Try to import real dependencies
try:
    from auth.auth_middleware import get_current_active_user, check_application_quota
    from database.models import UserResponse as DBUserResponse, ApplicationCreate as DBApplicationCreate, ApplicationResponse as DBApplicationResponse
    from database.connection import db
    
    # Use real models if available
    UserResponse = DBUserResponse
    ApplicationCreate = DBApplicationCreate
    ApplicationResponse = DBApplicationResponse
    
    DEPS_AVAILABLE = True
    print("✅ Application dependencies loaded successfully")
    
except ImportError as e:
    print(f"⚠️ Application dependencies not available: {e}")
    print("   Using fallback implementations")
    DEPS_AVAILABLE = False
    
    # Mock database
    mock_applications = {}
    
    class MockDB:
        async def get_user_applications(self, user_id: str, limit: int = 50, offset: int = 0):
            user_apps = [app for app in mock_applications.values() if app.get('user_id') == user_id]
            return user_apps[offset:offset + limit]
        
        async def create_application(self, app_data: dict):
            app_id = app_data['id']
            mock_applications[app_id] = app_data
            return app_data
    
    db = MockDB()
    
    # Mock auth middleware
    async def get_current_active_user():
        return UserResponse(
            id="mock_user_id",
            email="mock@example.com",
            name="Mock User",
            applications_limit=5,
            applications_used=0
        )
    
    def check_application_quota():
        async def quota_check():
            return await get_current_active_user()
        return quota_check

@router.get("/", response_model=List[ApplicationResponse])
async def get_user_applications(
    limit: int = 50,
    offset: int = 0,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get user's job applications"""
    try:
        applications = await db.get_user_applications(current_user.id, limit, offset)
        return [ApplicationResponse(**app) for app in applications]
    except Exception as e:
        print(f"Error getting user applications: {e}")
        # Return empty list if there's an error
        return []

@router.post("/", response_model=ApplicationResponse)
async def create_application(
    app_data: ApplicationCreate,
    current_user: UserResponse = Depends(check_application_quota())
):
    """Create a new job application"""
    try:
        new_app = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "profile_id": app_data.profile_id,
            "job_url": app_data.job_url,
            "job_title": app_data.job_title,
            "company_name": app_data.company_name,
            "job_location": app_data.job_location,
            "status": "queued",
            "priority": app_data.priority,
            "application_data": None,
            "error_message": None,
            "submitted_at": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        created_app = await db.create_application(new_app)
        if not created_app:
            raise HTTPException(status_code=500, detail="Failed to create application")
        
        return ApplicationResponse(**created_app)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Application creation failed: {str(e)}"
        )

@router.get("/test")
async def test_applications():
    """Test endpoint to verify applications module is working"""
    return {
        "message": "Applications API is working",
        "dependencies_available": DEPS_AVAILABLE
    }