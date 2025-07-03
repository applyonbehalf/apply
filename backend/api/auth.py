# api/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from auth.jwt_handler import JWTHandler
from auth.auth_middleware import get_current_active_user
from database.connection import db
from database.models import (
    UserCreate, UserLogin, UserResponse, Token, APIResponse
)
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/register", response_model=Token)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = await db.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = JWTHandler.hash_password(user_data.password)
    
    # Create user data
    new_user_data = {
        "id": str(uuid.uuid4()),
        "email": user_data.email,
        "name": user_data.name,
        "password_hash": hashed_password,
        "subscription_plan": "free",
        "applications_limit": 5,
        "applications_used": 0,
        "is_active": True,
        "email_verified": False
    }
    
    try:
        # Create user in database
        created_user = await db.create_user(new_user_data)
        
        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Create access token
        access_token = JWTHandler.create_access_token(
            data={"sub": created_user["id"]}
        )
        
        return Token(access_token=access_token, token_type="bearer")
        
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login_user(login_data: UserLogin):
    """Login a user"""
    
    # Get user by email
    user = await db.get_user_by_email(login_data.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not JWTHandler.verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create access token
    access_token = JWTHandler.create_access_token(
        data={"sub": user["id"]}
    )
    
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: UserResponse = Depends(get_current_active_user)):
    """Refresh access token"""
    
    # Create new access token
    access_token = JWTHandler.create_access_token(
        data={"sub": current_user.id}
    )
    
    return Token(access_token=access_token, token_type="bearer")

@router.post("/logout", response_model=APIResponse)
async def logout(current_user: UserResponse = Depends(get_current_active_user)):
    """Logout user (client should delete token)"""
    
    # Note: In a production app, you might want to maintain a blacklist of tokens
    # For now, we just return success and rely on client to delete token
    
    return APIResponse(
        success=True,
        message="Successfully logged out"
    )