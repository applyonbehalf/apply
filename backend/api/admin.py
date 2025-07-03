# backend/api/admin.py - Admin interface for URL management
from fastapi import APIRouter, Depends, HTTPException, status
from auth.auth_middleware import get_current_active_user
from database.models import UserResponse, APIResponse
from database.connection import db
from pydantic import BaseModel, validator
from typing import List, Optional
import uuid

router = APIRouter()

# Models for admin operations
class JobCategoryCreate(BaseModel):
    category_name: str
    description: Optional[str] = None

class JobCategoryResponse(BaseModel):
    id: str
    category_name: str
    description: Optional[str]
    is_active: bool
    created_at: str

class JobUrlCreate(BaseModel):
    category_id: str
    urls: List[str]
    
    @validator('urls')
    def validate_urls(cls, v):
        for url in v:
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f'Invalid URL: {url}')
        return v

class JobUrlResponse(BaseModel):
    id: str
    category_id: str
    category_name: str
    job_url: str
    job_title: Optional[str]
    company_name: Optional[str]
    status: str
    created_at: str

class BulkApplicationRequest(BaseModel):
    category_id: str
    urls: List[str]

# Admin permission check (you can modify this logic)
def require_admin_access():
    async def admin_check(current_user: UserResponse = Depends(get_current_active_user)):
        # For now, you can be the admin. Later add proper admin role
        admin_emails = ["shubhammane56@gmail.com", "admin@applyonbehalf.com"]
        
        if current_user.email not in admin_emails:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return current_user
    return admin_check

# Job Categories Management
@router.get("/categories", response_model=List[JobCategoryResponse])
async def get_job_categories(admin_user: UserResponse = Depends(require_admin_access())):
    """Get all job categories"""
    try:
        categories = await db.get_job_categories()
        return [JobCategoryResponse(**cat) for cat in categories]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")

@router.post("/categories", response_model=JobCategoryResponse)
async def create_job_category(
    category_data: JobCategoryCreate,
    admin_user: UserResponse = Depends(require_admin_access())
):
    """Create a new job category"""
    try:
        new_category = {
            "id": str(uuid.uuid4()),
            "category_name": category_data.category_name,
            "description": category_data.description,
            "is_active": True
        }
        
        created_category = await db.create_job_category(new_category)
        if not created_category:
            raise HTTPException(status_code=500, detail="Failed to create category")
        
        return JobCategoryResponse(**created_category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create category: {str(e)}")

# Job URLs Management  
@router.get("/job-urls", response_model=List[JobUrlResponse])
async def get_job_urls(
    category_id: Optional[str] = None,
    status: Optional[str] = None,
    admin_user: UserResponse = Depends(require_admin_access())
):
    """Get job URLs, optionally filtered by category or status"""
    try:
        job_urls = await db.get_job_urls(category_id=category_id, status=status)
        return [JobUrlResponse(**url) for url in job_urls]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job URLs: {str(e)}")

@router.post("/job-urls")
async def add_job_urls(
    url_data: JobUrlCreate,
    admin_user: UserResponse = Depends(require_admin_access())
):
    """Add job URLs to a category"""
    try:
        # Verify category exists
        category = await db.get_job_category_by_id(url_data.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Job category not found")
        
        created_urls = []
        for url in url_data.urls:
            new_url = {
                "id": str(uuid.uuid4()),
                "category_id": url_data.category_id,
                "job_url": url,
                "status": "active",
                "uploaded_by": admin_user.email
            }
            
            created_url = await db.create_job_url(new_url)
            if created_url:
                created_urls.append(created_url)
        
        # Trigger automatic application creation
        applications_created = await trigger_auto_applications(url_data.category_id, url_data.urls)
        
        return APIResponse(
            success=True,
            message=f"Added {len(created_urls)} URLs and created {applications_created} applications",
            data={
                "urls_added": len(created_urls),
                "applications_created": applications_created,
                "category": category["category_name"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add URLs: {str(e)}")

# Auto-create applications for users
async def trigger_auto_applications(category_id: str, job_urls: List[str]) -> int:
    """Automatically create applications for users interested in this job category"""
    try:
        # Find users who want jobs in this category
        interested_users = await db.get_users_by_job_category(category_id)
        
        applications_created = 0
        
        for user in interested_users:
            # Get user's default profile
            default_profile = await db.get_user_default_profile(user['user_id'])
            
            if not default_profile:
                print(f"⚠️ User {user['user_id']} has no default profile, skipping")
                continue
            
            # Create applications for each URL
            for job_url in job_urls:
                app_data = {
                    "id": str(uuid.uuid4()),
                    "user_id": user['user_id'],
                    "profile_id": default_profile['id'],
                    "job_url": job_url,
                    "status": "queued",
                    "priority": 1,  # Higher priority for admin-added jobs
                    "created_by": "admin_auto"
                }
                
                created_app = await db.create_application(app_data)
                if created_app:
                    applications_created += 1
                    print(f"✅ Created application for user {user['user_id'][:8]}... → {job_url}")
        
        print(f"🎯 Auto-created {applications_created} applications for {len(interested_users)} users")
        return applications_created
        
    except Exception as e:
        print(f"❌ Error in auto-application creation: {e}")
        return 0

# Bulk operations
@router.post("/bulk-applications")
async def create_bulk_applications(
    request: BulkApplicationRequest,
    admin_user: UserResponse = Depends(require_admin_access())
):
    """Create applications for all users interested in a job category"""
    try:
        applications_created = await trigger_auto_applications(request.category_id, request.urls)
        
        return APIResponse(
            success=True,
            message=f"Created {applications_created} applications",
            data={"applications_created": applications_created}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk application creation failed: {str(e)}")

# Statistics for admin dashboard
@router.get("/stats")
async def get_admin_stats(admin_user: UserResponse = Depends(require_admin_access())):
    """Get admin dashboard statistics"""
    try:
        stats = await db.get_admin_stats()
        return APIResponse(success=True, data=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get admin stats: {str(e)}")

# User management
@router.get("/users")
async def get_all_users(
    category_id: Optional[str] = None,
    admin_user: UserResponse = Depends(require_admin_access())
):
    """Get all users, optionally filtered by job category preference"""
    try:
        users = await db.get_all_users(category_id=category_id)
        return APIResponse(success=True, data=users)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")

# Test endpoint
@router.get("/test")
async def test_admin():
    """Test admin API"""
    return {
        "message": "Admin API is working",
        "features": [
            "Job category management",
            "Job URL management", 
            "Auto-application creation",
            "User management",
            "Admin statistics"
        ]
    }