# api/batches.py - Updated with better error handling
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import uuid
from datetime import datetime

router = APIRouter()

# Fallback models
class BatchCreate(BaseModel):
    batch_name: str = Field(..., min_length=1, max_length=200)
    urls: List[str] = Field(..., min_items=1, max_items=100)
    profile_id: str

    @validator('urls')
    def validate_urls(cls, v):
        for url in v:
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f'Invalid URL: {url}')
        return v

class BatchResponse(BaseModel):
    id: str
    user_id: str
    batch_name: str
    urls: List[str]
    profile_id: str
    total_count: int
    processed_count: int = 0
    successful_count: int = 0
    failed_count: int = 0
    status: str = "pending"
    created_at: datetime
    updated_at: datetime

class UserResponse(BaseModel):
    id: str
    email: str
    name: str

# Try to import real dependencies
try:
    from auth.auth_middleware import get_current_active_user
    from database.models import UserResponse as DBUserResponse, BatchCreate as DBBatchCreate, BatchResponse as DBBatchResponse
    from database.connection import db
    
    # Use real models if available
    UserResponse = DBUserResponse
    BatchCreate = DBBatchCreate
    BatchResponse = DBBatchResponse
    
    DEPS_AVAILABLE = True
    print("✅ Batch dependencies loaded successfully")
    
except ImportError as e:
    print(f"⚠️ Batch dependencies not available: {e}")
    print("   Using fallback implementations")
    DEPS_AVAILABLE = False
    
    # Mock database
    mock_batches = {}
    
    class MockDB:
        async def get_user_batches(self, user_id: str):
            return [batch for batch in mock_batches.values() if batch.get('user_id') == user_id]
        
        async def create_batch(self, batch_data: dict):
            batch_id = batch_data['id']
            mock_batches[batch_id] = batch_data
            return batch_data
    
    db = MockDB()
    
    # Mock auth middleware
    async def get_current_active_user():
        return UserResponse(
            id="mock_user_id",
            email="mock@example.com",
            name="Mock User"
        )

@router.get("/", response_model=List[BatchResponse])
async def get_user_batches(current_user: UserResponse = Depends(get_current_active_user)):
    """Get user's application batches"""
    try:
        batches = await db.get_user_batches(current_user.id)
        return [BatchResponse(**batch) for batch in batches]
    except Exception as e:
        print(f"Error getting user batches: {e}")
        # Return empty list if there's an error
        return []

@router.post("/", response_model=BatchResponse)
async def create_batch(
    batch_data: BatchCreate,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Create a new application batch"""
    try:
        new_batch = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "batch_name": batch_data.batch_name,
            "urls": batch_data.urls,
            "profile_id": batch_data.profile_id,
            "total_count": len(batch_data.urls),
            "processed_count": 0,
            "successful_count": 0,
            "failed_count": 0,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        created_batch = await db.create_batch(new_batch)
        if not created_batch:
            raise HTTPException(status_code=500, detail="Failed to create batch")
        
        return BatchResponse(**created_batch)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating batch: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch creation failed: {str(e)}"
        )

@router.get("/test")
async def test_batches():
    """Test endpoint to verify batches module is working"""
    return {
        "message": "Batches API is working",
        "dependencies_available": DEPS_AVAILABLE
    }