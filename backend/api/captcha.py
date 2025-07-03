# api/captcha.py - Updated with better error handling
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

# Fallback models
class CaptchaSessionResponse(BaseModel):
    id: str
    application_id: str
    screenshot_url: Optional[str]
    page_url: Optional[str]
    status: str = "pending"
    admin_notes: Optional[str]
    solved_at: Optional[datetime]
    solved_by: Optional[str]
    expires_at: datetime
    created_at: datetime
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    user_name: Optional[str] = None

class CaptchaSessionUpdate(BaseModel):
    status: str
    admin_notes: Optional[str] = None
    solved_by: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: str

# Try to import real dependencies
try:
    from auth.auth_middleware import get_current_active_user
    from database.models import UserResponse as DBUserResponse, CaptchaSessionResponse as DBCaptchaSessionResponse, CaptchaSessionUpdate as DBCaptchaSessionUpdate
    from database.connection import db
    
    # Use real models if available
    UserResponse = DBUserResponse
    CaptchaSessionResponse = DBCaptchaSessionResponse
    CaptchaSessionUpdate = DBCaptchaSessionUpdate
    
    DEPS_AVAILABLE = True
    print("✅ CAPTCHA dependencies loaded successfully")
    
except ImportError as e:
    print(f"⚠️ CAPTCHA dependencies not available: {e}")
    print("   Using fallback implementations")
    DEPS_AVAILABLE = False
    
    # Mock database
    mock_captcha_sessions = {}
    
    class MockDB:
        async def get_pending_captchas(self):
            return [session for session in mock_captcha_sessions.values() if session.get('status') == 'pending']
        
        async def update_captcha_status(self, session_id: str, status: str, solved_by: str = None):
            if session_id in mock_captcha_sessions:
                mock_captcha_sessions[session_id]['status'] = status
                if solved_by:
                    mock_captcha_sessions[session_id]['solved_by'] = solved_by
                    mock_captcha_sessions[session_id]['solved_at'] = datetime.utcnow()
                return True
            return False
    
    db = MockDB()
    
    # Mock auth middleware
    async def get_current_active_user():
        return UserResponse(
            id="mock_user_id",
            email="mock@example.com",
            name="Mock User"
        )

@router.get("/pending", response_model=List[CaptchaSessionResponse])
async def get_pending_captchas():
    """Get all pending CAPTCHA sessions (admin endpoint)"""
    try:
        sessions = await db.get_pending_captchas()
        return [CaptchaSessionResponse(**session) for session in sessions]
    except Exception as e:
        print(f"Error getting pending CAPTCHAs: {e}")
        # Return empty list if there's an error
        return []

@router.post("/{session_id}/solve")
async def solve_captcha(session_id: str, update_data: CaptchaSessionUpdate):
    """Mark CAPTCHA as solved"""
    try:
        success = await db.update_captcha_status(
            session_id, 
            update_data.status, 
            update_data.solved_by
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update CAPTCHA status")
        
        return {"success": True, "message": "CAPTCHA status updated"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error solving CAPTCHA: {e}")
        raise HTTPException(status_code=500, detail=f"CAPTCHA update failed: {str(e)}")

@router.post("/{session_id}/skip")
async def skip_captcha(session_id: str):
    """Skip CAPTCHA (mark as skipped)"""
    try:
        success = await db.update_captcha_status(session_id, 'skipped', 'admin')
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to skip CAPTCHA")
        
        return {"success": True, "message": "CAPTCHA skipped"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error skipping CAPTCHA: {e}")
        raise HTTPException(status_code=500, detail=f"CAPTCHA skip failed: {str(e)}")

@router.get("/test")
async def test_captcha():
    """Test endpoint to verify CAPTCHA module is working"""
    return {
        "message": "CAPTCHA API is working",
        "dependencies_available": DEPS_AVAILABLE
    }