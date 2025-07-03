# api/users.py
from fastapi import APIRouter, Depends
from auth.auth_middleware import get_current_active_user
from database.models import UserResponse, UserStats
from database.connection import db

router = APIRouter()

@router.get("/stats", response_model=UserStats)
async def get_user_stats(current_user: UserResponse = Depends(get_current_active_user)):
    """Get user application statistics"""
    stats = await db.get_user_stats(current_user.id)
    return UserStats(**stats)