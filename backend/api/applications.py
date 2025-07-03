# api/applications.py
from fastapi import APIRouter, Depends, HTTPException
from auth.auth_middleware import get_current_active_user, check_application_quota
from database.models import UserResponse, ApplicationCreate, ApplicationResponse
from database.connection import db
from typing import List
import uuid

router = APIRouter()

@router.get("/", response_model=List[ApplicationResponse])
async def get_user_applications(
    limit: int = 50,
    offset: int = 0,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get user's job applications"""
    applications = await db.get_user_applications(current_user.id, limit, offset)
    return [ApplicationResponse(**app) for app in applications]

@router.post("/", response_model=ApplicationResponse)
async def create_application(
    app_data: ApplicationCreate,
    current_user: UserResponse = Depends(check_application_quota())
):
    """Create a new job application"""
    new_app = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.id,
        **app_data.dict()
    }
    
    created_app = await db.create_application(new_app)
    if not created_app:
        raise HTTPException(status_code=500, detail="Failed to create application")
    
    return ApplicationResponse(**created_app)