# auth/auth_middleware.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.jwt_handler import JWTHandler
from database.connection import db
from database.models import UserResponse
from typing import Optional

# Security scheme
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """Get the current authenticated user"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify the token
        user_id = JWTHandler.verify_token(credentials.credentials)
        
        if user_id is None:
            raise credentials_exception
        
        # Get user from database
        user_data = await db.get_user_by_id(user_id)
        
        if user_data is None:
            raise credentials_exception
        
        # Check if user is active
        if not user_data.get('is_active', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        return UserResponse(**user_data)
        
    except Exception as e:
        print(f"Authentication error: {e}")
        raise credentials_exception

async def get_current_active_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Get current active user (additional check for active status)"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return current_user

async def get_optional_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[UserResponse]:
    """Get current user if authenticated, None otherwise (for optional auth endpoints)"""
    if not credentials:
        return None
    
    try:
        user_id = JWTHandler.verify_token(credentials.credentials)
        if user_id:
            user_data = await db.get_user_by_id(user_id)
            if user_data and user_data.get('is_active', False):
                return UserResponse(**user_data)
    except Exception:
        pass
    
    return None

def require_subscription(min_plan: str = "free"):
    """Dependency to check user subscription level"""
    async def check_subscription(current_user: UserResponse = Depends(get_current_active_user)) -> UserResponse:
        plan_hierarchy = {"free": 0, "pro": 1, "enterprise": 2}
        
        user_level = plan_hierarchy.get(current_user.subscription_plan, 0)
        required_level = plan_hierarchy.get(min_plan, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires {min_plan} subscription or higher"
            )
        
        return current_user
    
    return check_subscription

def check_application_quota():
    """Dependency to check if user has remaining application quota"""
    async def quota_check(current_user: UserResponse = Depends(get_current_active_user)) -> UserResponse:
        if current_user.applications_used >= current_user.applications_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Monthly application limit reached. Please upgrade your plan or wait for reset."
            )
        
        return current_user
    
    return quota_check