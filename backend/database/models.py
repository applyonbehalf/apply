# database/models_simple.py - Simplified models without EmailStr requirement
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums for status fields
class SubscriptionPlan(str, Enum):
    FREE = "free"
    PRO = "pro" 
    ENTERPRISE = "enterprise"

class ApplicationStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    CAPTCHA_REQUIRED = "captcha_required"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class CaptchaStatus(str, Enum):
    PENDING = "pending"
    SOLVED = "solved"
    EXPIRED = "expired"
    SKIPPED = "skipped"

class BatchStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class NotificationType(str, Enum):
    CAPTCHA_REQUIRED = "captcha_required"
    APPLICATION_COMPLETED = "application_completed"
    APPLICATION_FAILED = "application_failed"
    QUOTA_EXCEEDED = "quota_exceeded"
    BATCH_COMPLETED = "batch_completed"
    SYSTEM_ALERT = "system_alert"

# User models - using str instead of EmailStr
class UserCreate(BaseModel):
    email: str  # Changed from EmailStr to str
    name: str
    password: str

class UserLogin(BaseModel):
    email: str  # Changed from EmailStr to str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    subscription_plan: SubscriptionPlan
    applications_limit: int
    applications_used: int
    reset_date: datetime
    is_active: bool
    email_verified: bool
    created_at: datetime

class UserUpdate(BaseModel):
    name: Optional[str] = None
    subscription_plan: Optional[SubscriptionPlan] = None
    applications_limit: Optional[int] = None

# Profile models
class ProfileData(BaseModel):
    personal_info: Dict[str, Any] = Field(..., description="Personal information (name, email, phone, etc.)")
    experience: Optional[Dict[str, Any]] = Field(None, description="Experience information")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Work preferences")
    eligibility: Optional[Dict[str, Any]] = Field(None, description="Work eligibility information")
    skills: Optional[Dict[str, Any]] = Field(None, description="Skills and certifications")
    education: Optional[List[Dict[str, Any]]] = Field(None, description="Education history")
    employment_history: Optional[List[Dict[str, Any]]] = Field(None, description="Employment history")

class ProfileCreate(BaseModel):
    profile_name: str = Field(..., min_length=1, max_length=100)
    profile_data: ProfileData
    resume_url: Optional[str] = None
    cover_letter_template: Optional[str] = None
    is_default: bool = False

class ProfileUpdate(BaseModel):
    profile_name: Optional[str] = None
    profile_data: Optional[ProfileData] = None
    resume_url: Optional[str] = None
    cover_letter_template: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None

class ProfileResponse(BaseModel):
    id: str
    user_id: str
    profile_name: str
    profile_data: ProfileData
    resume_url: Optional[str]
    cover_letter_template: Optional[str]
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

# Job Application models
class ApplicationCreate(BaseModel):
    profile_id: str
    job_url: str = Field(..., min_length=1)  # Simplified URL validation
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    job_location: Optional[str] = None
    priority: int = Field(0, ge=0, le=10)

class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    job_location: Optional[str] = None
    error_message: Optional[str] = None
    application_data: Optional[Dict[str, Any]] = None

class ApplicationResponse(BaseModel):
    id: str
    user_id: str
    profile_id: str
    batch_id: Optional[str]
    job_url: str
    job_title: Optional[str]
    company_name: Optional[str]
    job_location: Optional[str]
    status: ApplicationStatus
    priority: int
    application_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    captcha_session_id: Optional[str]
    processing_started_at: Optional[datetime]
    submitted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

# Batch models
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
    processed_count: int
    successful_count: int
    failed_count: int
    status: BatchStatus
    created_at: datetime
    updated_at: datetime

# CAPTCHA models
class CaptchaSessionCreate(BaseModel):
    application_id: str
    screenshot_url: Optional[str] = None
    page_url: Optional[str] = None

class CaptchaSessionUpdate(BaseModel):
    status: CaptchaStatus
    admin_notes: Optional[str] = None
    solved_by: Optional[str] = None

class CaptchaSessionResponse(BaseModel):
    id: str
    application_id: str
    screenshot_url: Optional[str]
    page_url: Optional[str]
    status: CaptchaStatus
    admin_notes: Optional[str]
    solved_at: Optional[datetime]
    solved_by: Optional[str]
    expires_at: datetime
    created_at: datetime
    
    # Include application details for admin interface
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    user_name: Optional[str] = None

# Notification models
class NotificationCreate(BaseModel):
    user_id: Optional[str] = None
    type: NotificationType
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    is_admin_notification: bool = False

class NotificationResponse(BaseModel):
    id: str
    user_id: Optional[str]
    type: NotificationType
    title: str
    message: str
    data: Optional[Dict[str, Any]]
    is_read: bool
    is_admin_notification: bool
    created_at: datetime

# Analytics models
class UserStats(BaseModel):
    total_applications: int
    queued: int
    processing: int
    completed: int
    failed: int
    captcha_required: int
    success_rate: float

# Authentication models
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None

# API Response models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None