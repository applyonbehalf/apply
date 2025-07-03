# api/bot.py - Bot control API endpoints
from fastapi import APIRouter, Depends, HTTPException, status
from auth.auth_middleware import get_current_active_user
from database.models import UserResponse, APIResponse
from services.bot_service import bot_service
from typing import List
from pydantic import BaseModel

router = APIRouter()

# Request models
class BotStartRequest(BaseModel):
    headless: bool = True
    max_concurrent: int = 1

class AddUrlsRequest(BaseModel):
    profile_id: str
    urls: List[str]
    batch_name: str = None

class ProcessSingleRequest(BaseModel):
    profile_id: str
    job_url: str

# Bot control endpoints (admin only for now)
@router.post("/start")
async def start_bot(
    request: BotStartRequest,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Start the application processing bot"""
    # TODO: Add admin permission check
    # if current_user.subscription_plan != 'enterprise':
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await bot_service.start_bot(
        headless=request.headless,
        max_concurrent=request.max_concurrent
    )
    
    if result['success']:
        return APIResponse(success=True, message=result['message'], data=result.get('config'))
    else:
        raise HTTPException(status_code=400, detail=result['message'])

@router.post("/stop")
async def stop_bot(current_user: UserResponse = Depends(get_current_active_user)):
    """Stop the application processing bot"""
    # TODO: Add admin permission check
    
    result = await bot_service.stop_bot()
    
    if result['success']:
        return APIResponse(success=True, message=result['message'])
    else:
        raise HTTPException(status_code=400, detail=result['message'])

@router.get("/status")
async def get_bot_status(current_user: UserResponse = Depends(get_current_active_user)):
    """Get current bot status and statistics"""
    status_info = await bot_service.get_bot_status()
    return APIResponse(success=True, data=status_info)

@router.get("/queue")
async def get_queue_status(current_user: UserResponse = Depends(get_current_active_user)):
    """Get current queue status"""
    queue_info = await bot_service.get_queue_status()
    return APIResponse(success=True, data=queue_info)

# User-specific endpoints
@router.post("/add-urls")
async def add_urls_to_queue(
    request: AddUrlsRequest,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Add job URLs to the processing queue"""
    result = await bot_service.add_urls_to_queue(
        user_id=current_user.id,
        profile_id=request.profile_id,
        urls=request.urls,
        batch_name=request.batch_name
    )
    
    if result['success']:
        return APIResponse(
            success=True, 
            message=result['message'],
            data={
                'batch_id': result['batch_id'],
                'applications_created': result['applications_created']
            }
        )
    else:
        raise HTTPException(status_code=400, detail=result['message'])

@router.post("/process-single")
async def process_single_application(
    request: ProcessSingleRequest,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Process a single application immediately (for testing)"""
    result = await bot_service.process_single_application(
        user_id=current_user.id,
        profile_id=request.profile_id,
        job_url=request.job_url
    )
    
    if result['success']:
        return APIResponse(success=True, message=result['message'])
    else:
        raise HTTPException(status_code=400, detail=result['message'])

@router.get("/my-queue")
async def get_my_queue_status(current_user: UserResponse = Depends(get_current_active_user)):
    """Get queue status for current user"""
    queue_info = await bot_service.get_user_queue_status(current_user.id)
    return APIResponse(success=True, data=queue_info)

@router.post("/pause-my-applications")
async def pause_my_applications(current_user: UserResponse = Depends(get_current_active_user)):
    """Pause all applications for current user"""
    result = await bot_service.pause_user_applications(current_user.id)
    
    if result['success']:
        return APIResponse(success=True, message=result['message'])
    else:
        raise HTTPException(status_code=400, detail=result['message'])

@router.post("/resume-my-applications")
async def resume_my_applications(current_user: UserResponse = Depends(get_current_active_user)):
    """Resume all paused applications for current user"""
    result = await bot_service.resume_user_applications(current_user.id)
    
    if result['success']:
        return APIResponse(success=True, message=result['message'])
    else:
        raise HTTPException(status_code=400, detail=result['message'])

# CAPTCHA solving endpoints
@router.get("/captcha/pending")
async def get_pending_captchas():
    """Get all pending CAPTCHA sessions (admin endpoint)"""
    try:
        from database.connection import db
        sessions = await db.get_pending_captchas()
        return APIResponse(success=True, data=sessions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/captcha/{session_id}/solve")
async def solve_captcha(session_id: str):
    """Mark CAPTCHA as solved"""
    try:
        from database.connection import db
        success = await db.update_captcha_status(session_id, 'solved', 'admin')
        
        if success:
            return APIResponse(success=True, message="CAPTCHA marked as solved")
        else:
            raise HTTPException(status_code=400, detail="Failed to update CAPTCHA status")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/captcha/{session_id}/skip")
async def skip_captcha(session_id: str):
    """Skip CAPTCHA (mark as skipped)"""
    try:
        from database.connection import db
        success = await db.update_captcha_status(session_id, 'skipped', 'admin')
        
        if success:
            return APIResponse(success=True, message="CAPTCHA skipped")
        else:
            raise HTTPException(status_code=400, detail="Failed to skip CAPTCHA")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))