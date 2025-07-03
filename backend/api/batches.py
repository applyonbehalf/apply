# api/batches.py
from fastapi import APIRouter, Depends, HTTPException
from auth.auth_middleware import get_current_active_user
from database.models import UserResponse, BatchCreate, BatchResponse
from database.connection import db
from typing import List
import uuid

router = APIRouter()

@router.get("/", response_model=List[BatchResponse])
async def get_user_batches(current_user: UserResponse = Depends(get_current_active_user)):
    """Get user's application batches"""
    batches = await db.get_user_batches(current_user.id)
    return [BatchResponse(**batch) for batch in batches]

@router.post("/", response_model=BatchResponse)
async def create_batch(
    batch_data: BatchCreate,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Create a new application batch"""
    new_batch = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.id,
        "total_count": len(batch_data.urls),
        **batch_data.dict()
    }
    
    created_batch = await db.create_batch(new_batch)
    if not created_batch:
        raise HTTPException(status_code=500, detail="Failed to create batch")
    
    return BatchResponse(**created_batch)