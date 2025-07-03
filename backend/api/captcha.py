# api/captcha.py
from fastapi import APIRouter, Depends, HTTPException
from auth.auth_middleware import get_current_active_user
from database.models import UserResponse, CaptchaSessionResponse, CaptchaSessionUpdate
from database.connection import db
from typing import List

router = APIRouter()

@router.get("/pending", response_model=List[CaptchaSessionResponse])
async def get_pending_captchas():
    """Get all pending CAPTCHA sessions (admin endpoint)"""
    sessions = await db.get_pending_captchas()
    return [CaptchaSessionResponse(**session) for session in sessions]

@router.post("/{session_id}/solve")
async def solve_captcha(session_id: str, update_data: CaptchaSessionUpdate):
    """Mark CAPTCHA as solved"""
    success = await db.update_captcha_status(
        session_id, 
        update_data.status, 
        update_data.solved_by
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update CAPTCHA status")
    
    return {"success": True, "message": "CAPTCHA status updated"}