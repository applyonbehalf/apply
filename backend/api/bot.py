# api/bot.py - Updated with better error handling
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

router = APIRouter()

# Request models
class BotStartRequest(BaseModel):
    headless: bool = True
    max_concurrent: int = 1

class AddUrlsRequest(BaseModel):
    profile_id: str
    urls: List[str]
    batch_name: Optional[str] = None

class ProcessSingleRequest(BaseModel):
    profile_id: str
    job_url: str

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: str

# Try to import real dependencies
try:
    from auth.auth_middleware import get_current_active_user
    from database.models import UserResponse as DBUserResponse, APIResponse as DBAPIResponse
    from services.bot_service import bot_service
    
    # Use real models if available
    UserResponse = DBUserResponse
    APIResponse = DBAPIResponse
    
    BOT_SERVICE_AVAILABLE = True
    print("✅ Bot service dependencies loaded successfully")
    
except ImportError as e:
    print(f"⚠️ Bot service dependencies not available: {e}")
    print("   Using fallback implementations")
    BOT_SERVICE_AVAILABLE = False
    
    # Mock bot service
    class MockBotService:
        async def start_bot(self, headless: bool = True, max_concurrent: int = 1):
            return {
                'success': True,
                'message': 'Mock bot started successfully',
                'config': {'headless': headless, 'max_concurrent': max_concurrent}
            }
        
        async def stop_bot(self):
            return {'success': True, 'message': 'Mock bot stopped successfully'}
        
        async def get_bot_status(self):
            return {
                'running': False,
                'message': 'Mock bot service - not actually running',
                'stats': {
                    'total_processed': 0,
                    'successful': 0,
                    'failed': 0,
                    'success_rate': 0
                }
            }
        
        async def get_queue_status(self):
            return {
                'queued': 0,
                'processing': 0,
                'completed': 0,
                'failed': 0
            }
        
        async def add_urls_to_queue(self, user_id: str, profile_id: str, urls: List[str], batch_name: str = None):
            return {
                'success': True,
                'message': f'Mock: Added {len(urls)} URLs to queue',
                'batch_id': 'mock_batch_id',
                'applications_created': len(urls)
            }
        
        async def process_single_application(self, user_id: str, profile_id: str, job_url: str):
            return {'success': True, 'message': 'Mock: Single application processed'}
        
        async def get_user_queue_status(self, user_id: str):
            return {
                'queued': 0,
                'processing': 0,
                'completed': 0,
                'failed': 0,
                'success_rate': 0
            }
        
        async def pause_user_applications(self, user_id: str):
            return {'success': True, 'message': 'Mock: User applications paused'}
        
        async def resume_user_applications(self, user_id: str):
            return {'success': True, 'message': 'Mock: User applications resumed'}
    
    bot_service = MockBotService()
    
    # Mock auth middleware
    async def get_current_active_user():
        return UserResponse(
            id="mock_user_id",
            email="mock@example.com",
            name="Mock User"
        )

# Bot control endpoints
@router.post("/start")
async def start_bot(
    request: BotStartRequest,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Start the application processing bot"""
    try:
        result = await bot_service.start_bot(
            headless=request.headless,
            max_concurrent=request.max_concurrent
        )
        
        if result['success']:
            return APIResponse(success=True, message=result['message'], data=result.get('config'))
        else:
            raise HTTPException(status_code=400, detail=result['message'])
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error starting bot: {e}")
        raise HTTPException(status_code=500, detail=f"Bot start failed: {str(e)}")

@router.post("/stop")
async def stop_bot(current_user: UserResponse = Depends(get_current_active_user)):
    """Stop the application processing bot"""
    try:
        result = await bot_service.stop_bot()
        
        if result['success']:
            return APIResponse(success=True, message=result['message'])
        else:
            raise HTTPException(status_code=400, detail=result['message'])
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error stopping bot: {e}")
        raise HTTPException(status_code=500, detail=f"Bot stop failed: {str(e)}")

@router.get("/status")
async def get_bot_status(current_user: UserResponse = Depends(get_current_active_user)):
    """Get current bot status and statistics"""
    try:
        status_info = await bot_service.get_bot_status()
        return APIResponse(success=True, data=status_info)
    except Exception as e:
        print(f"Error getting bot status: {e}")
        return APIResponse(
            success=False, 
            message=f"Status check failed: {str(e)}",
            data={'running': False, 'error': str(e)}
        )

@router.get("/queue")
async def get_queue_status(current_user: UserResponse = Depends(get_current_active_user)):
    """Get current queue status"""
    try:
        queue_info = await bot_service.get_queue_status()
        return APIResponse(success=True, data=queue_info)
    except Exception as e:
        print(f"Error getting queue status: {e}")
        return APIResponse(
            success=False,
            message=f"Queue status failed: {str(e)}",
            data={'error': str(e)}
        )

# User-specific endpoints
@router.post("/add-urls")
async def add_urls_to_queue(
    request: AddUrlsRequest,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Add job URLs to the processing queue"""
    try:
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
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error adding URLs to queue: {e}")
        raise HTTPException(status_code=500, detail=f"URL addition failed: {str(e)}")

@router.post("/process-single")
async def process_single_application(
    request: ProcessSingleRequest,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Process a single application immediately (for testing)"""
    try:
        result = await bot_service.process_single_application(
            user_id=current_user.id,
            profile_id=request.profile_id,
            job_url=request.job_url
        )
        
        if result['success']:
            return APIResponse(success=True, message=result['message'])
        else:
            raise HTTPException(status_code=400, detail=result['message'])
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing single application: {e}")
        raise HTTPException(status_code=500, detail=f"Single application processing failed: {str(e)}")

@router.get("/my-queue")
async def get_my_queue_status(current_user: UserResponse = Depends(get_current_active_user)):
    """Get queue status for current user"""
    try:
        queue_info = await bot_service.get_user_queue_status(current_user.id)
        return APIResponse(success=True, data=queue_info)
    except Exception as e:
        print(f"Error getting user queue status: {e}")
        return APIResponse(
            success=False,
            message=f"User queue status failed: {str(e)}",
            data={'error': str(e)}
        )

@router.post("/pause-my-applications")
async def pause_my_applications(current_user: UserResponse = Depends(get_current_active_user)):
    """Pause all applications for current user"""
    try:
        result = await bot_service.pause_user_applications(current_user.id)
        
        if result['success']:
            return APIResponse(success=True, message=result['message'])
        else:
            raise HTTPException(status_code=400, detail=result['message'])
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error pausing applications: {e}")
        raise HTTPException(status_code=500, detail=f"Application pause failed: {str(e)}")

@router.post("/resume-my-applications")
async def resume_my_applications(current_user: UserResponse = Depends(get_current_active_user)):
    """Resume all paused applications for current user"""
    try:
        result = await bot_service.resume_user_applications(current_user.id)
        
        if result['success']:
            return APIResponse(success=True, message=result['message'])
        else:
            raise HTTPException(status_code=400, detail=result['message'])
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error resuming applications: {e}")
        raise HTTPException(status_code=500, detail=f"Application resume failed: {str(e)}")

# CAPTCHA solving endpoints
@router.get("/captcha/pending")
async def get_pending_captchas():
    """Get all pending CAPTCHA sessions (admin endpoint)"""
    try:
        from database.connection import db
        sessions = await db.get_pending_captchas()
        return APIResponse(success=True, data=sessions)
    except Exception as e:
        print(f"Error getting pending CAPTCHAs: {e}")
        return APIResponse(success=True, data=[])  # Return empty list on error

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
        print(f"Error solving CAPTCHA: {e}")
        raise HTTPException(status_code=500, detail=f"CAPTCHA solve failed: {str(e)}")

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
        print(f"Error skipping CAPTCHA: {e}")
        raise HTTPException(status_code=500, detail=f"CAPTCHA skip failed: {str(e)}")

@router.get("/test")
async def test_bot():
    """Test endpoint to verify bot module is working"""
    return {
        "message": "Bot API is working",
        "bot_service_available": BOT_SERVICE_AVAILABLE
    }